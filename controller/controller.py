#!/usr/bin/env python
import sys
import logging
import time, RPi.GPIO as GPIO
import zmq
import argparse
import signal
import threading
import Queue
from functools import partial

logger = logging.getLogger(__name__)

R1 = 24
R2 = 26
L1 = 19
L2 = 21


p = q = a = b = None

def setup():
    global p, q, a, b
    #GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(L1, GPIO.OUT)
    p = GPIO.PWM(L1, 20)
    p.start(0)

    GPIO.setup(L2, GPIO.OUT)
    q = GPIO.PWM(L2, 20)
    q.start(0)

    GPIO.setup(R1, GPIO.OUT)
    a = GPIO.PWM(R1, 20)
    a.start(0)

    GPIO.setup(R2, GPIO.OUT)
    b = GPIO.PWM(R2, 20)
    b.start(0)

def forward(speed):
    p.ChangeDutyCycle(speed)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(speed)
    b.ChangeDutyCycle(0)
    p.ChangeFrequency(speed + 5)
    a.ChangeFrequency(speed + 5)

# reverse(speed): Sets both motors to reverse at speed. 0 <= speed <= 100
def reverse(speed):
    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(speed)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(speed)
    q.ChangeFrequency(speed + 5)
    b.ChangeFrequency(speed + 5)

def stop():
    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(0)


def spin_left(speed):
    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(speed)
    a.ChangeDutyCycle(speed)
    b.ChangeDutyCycle(0)
    q.ChangeFrequency(speed + 5)
    a.ChangeFrequency(speed + 5)

def spin_right(speed):
    p.ChangeDutyCycle(speed)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(speed)
    p.ChangeFrequency(speed + 5)
    b.ChangeFrequency(speed + 5)


def turn_forward(left_speed, right_speed):
    p.ChangeDutyCycle(left_speed)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(right_speed)
    b.ChangeDutyCycle(0)
    p.ChangeFrequency(left_speed + 5)
    a.ChangeFrequency(right_speed + 5)

def turn_reverse(left_speed, right_speed):
    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(left_speed)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(right_speed)
    q.ChangeFrequency(left_speed + 5)
    b.ChangeFrequency(right_speed + 5)


def sighandler(_num, _frame):
    shutdown()
    sys.exit()


def shutdown():
    stop()
    GPIO.cleanup()


def network_loop(queue, socket):
    while True:
        queue.put(socket.recv())

PORT = 12345
HOST = '192.168.178.39'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    opts = parser.parse_args()
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    uri = "tcp://{host}:{port}".format(host=opts.host, port=opts.port)

    setup()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, sighandler)

    queue = Queue.Queue()
    socket.connect(uri)
    t = threading.Thread(target=partial(
        network_loop, queue=queue, socket=socket
        ),
    )
    t.setDaemon(True)
    t.start()

    def quit():
        running.remove(True)

    running = [True]
    try:
        while running:
            message = queue.get()

            action = dict(
                forward=forward,
                spin_left=spin_left,
                spin_right=spin_right,
                stop=stop,
                quit=quit,
                ).get(message.split()[0])
            if action:
                args = [int(v) for v in message.split()[1:]]
                print action, args
                action(*args)
            else:
                print "unknown message:", message
                break
    finally:
        shutdown()


if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        )
    main()
