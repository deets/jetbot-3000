import zmq
import random
import time
import argparse
import os
import Queue
import threading
from functools import partial
from math import sqrt, atan2, pi

PORT = 12345
HOST = '192.168.178.39'
SPEED_THRESHOLD = 0.2
TIMEOUT = .25

from bottle import route, run, template, static_file, request

QUEUE = Queue.Queue()

@route('/')
def index():
    return template('index')


@route('/static/<filename:path>')
def send_static(filename):
    return static_file(
        filename,
        root=os.path.join(
            os.path.dirname(__file__),
            "static",
            )
        )


@route('/track', method="POST")
def track():
    data = request.json
    command = data.get("command")
    if command is not None:
        command = dict(up="forward 100",
                 left="spin_left 100",
                 right="spin_right 100",
                 down="reverse 100").get(command, command)
        print "command:", command
        QUEUE.put(
            command
            )


def sender(socket):
    while True:
        try:
            command = QUEUE.get(True, TIMEOUT)
        except Queue.Empty:
            command = "stop"
        print command
        socket.send(command)


def main():
    global SOCKET
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    opts = parser.parse_args()

    uri = "tcp://{host}:{port}".format(host=opts.host, port=opts.port)
    print uri

    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind(uri)

    t = threading.Thread(target=partial(sender, socket=socket))
    t.setDaemon(True)
    t.start()
    run(host='', port=8080)


    # while True:
    #     for message in ("forward 100", "spin_left 50", "quit"):
    #         socket.send(message)
    #         time.sleep(1)


if __name__ == "__main__":
    main()
