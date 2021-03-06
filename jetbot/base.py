#

import sys
import logging
import time
import json
import Queue
import threading
import nanomsg

logger = logging.getLogger(__name__)

PORT = 12345
HOST = 'jetbot-vhost'


def setup_logging(_opts):
    logging.basicConfig(
        level=logging.DEBUG,
        stream=sys.stderr,
    )
    logging.getLogger("geventwebsocket.handler").setLevel(logging.ERROR)


class Hub(object):

    def __init__(self, socket):
        self._socket = socket
        self._receiver_thread_send_queue = Queue.Queue()
        self._processors = []
        self._running = True
        self._receiver_thread = threading.Thread(
            target=self._receive_message,
        )
        self._receiver_thread.setDaemon(True)


    def start(self):
        self._receiver_thread.start()


    def __iadd__(self, processor):
        self._processors.append(processor)
        return self


    def _send(self, message):
        payload = message.__json__()
        self._socket.send(json.dumps(payload))


    def _receive_message(self):
        while self._running:
            packet = self._socket.recv()
            now = time.time()
            message = json.loads(packet)
            message["received"] = now
            for processor in self._processors:
                processor.process(
                    message,
                    self._receiver_thread_send_queue.put,
                )


    @classmethod
    def setup_argparser(cls, parser):
        pass


    def process_once(self):
        for processor in self._processors:
            processor.activate(self._send)
        for _ in xrange(self._receiver_thread_send_queue.qsize()):
            self._send(self._receiver_thread_send_queue.get())


class ServerHub(Hub):


    @classmethod
    def setup_argparser(cls, parser):
        super(ServerHub, cls).setup_argparser(parser)
        parser.add_argument("--port", type=int, default=PORT)


    @classmethod
    def setup(cls, opts):
        uri = "tcp://*:{port}".format(port=opts.port)

        socket = nanomsg.Socket(nanomsg.PAIR)

        socket.bind(uri)
        logger.info("Binding to '%s'", uri)
        return cls(socket)


class PiHub(Hub):

    @classmethod
    def setup_argparser(cls, parser):
        super(PiHub, cls).setup_argparser(parser)
        parser.add_argument("--port", type=int, default=PORT)
        parser.add_argument("--host", default=HOST)


    @classmethod
    def setup(cls, opts):
        uri = "tcp://{host}:{port}".format(host=opts.host, port=opts.port)
        socket = nanomsg.Socket(nanomsg.PAIR)

        logger.info("Connecting to '%s'", uri)
        socket.connect(uri)
        return cls(socket)


def message_valid(threshold, received, remote_timestamp, remote_offset):
    diff = received - (remote_timestamp - remote_offset)
    return threshold >= abs(diff)
