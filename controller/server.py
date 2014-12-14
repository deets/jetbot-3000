import zmq
import random
import time
import argparse

PORT = 12345
HOST = '192.168.178.39'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    opts = parser.parse_args()

    uri = "tcp://{host}:{port}".format(host=opts.host, port=opts.port)
    print uri

    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind(uri)

    while True:
        for message in ("forward 100", "spin_left 50", "quit"):
            socket.send(message)
            time.sleep(1)


if __name__ == "__main__":
    main()
