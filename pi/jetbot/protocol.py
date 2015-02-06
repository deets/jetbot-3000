#
import sys
import argparse
import logging
import time
import uuid
import json
from functools import partial
import threading
import Queue

import zmq

PORT = 12345
HOST = 'jetbot-vhost'

logger = logging.getLogger(__name__)


class Message(object):

    TYPE = None

    def __init__(self):
        self.uid = str(uuid.uuid4())


    def __json__(self):
        assert self.TYPE is not None, \
          "You must subclass Message and define TYPE: %s" % \
          self.__class__.__name__
        return {
            'timestamp': time.time(),
            'type': self.TYPE,
            'uid': self.uid,
            }

class SyncMessage(Message):

    TYPE = "TIME_SYNC"

    def __init__(self):
        super(SyncMessage, self).__init__()


    @classmethod
    def ack(cls, ack_msg):
        # as found on wikipedia
        # http://en.wikipedia.org/wiki/Network_Time_Protocol#Clock_synchronization_algorithm
        t0 = ack_msg["sender_timestamp"]
        t1 = ack_msg["receiver_timestamp"]
        t2 = ack_msg["timestamp"]
        t3 = ack_msg["received"]

        total_roundtrip = t3 - t0
        processing_time = t2 - t1
        delay = total_roundtrip - processing_time
        offset = ((t1 - t0) + (t2 - t3)) / 2.0

        logger.info("DELAY: %f", delay)
        logger.info("OFFSET: %f", offset)


class SyncAck(Message):

    TYPE = "SYNC_ACK"

    def __init__(self, sync):
        super(SyncAck, self).__init__()
        self._sender_timestamp = sync["timestamp"]
        self._receiver_timestamp = sync["received"]
        self._sender_uid = sync["uid"]

    def __json__(self):
        res = super(SyncAck, self).__json__()
        res.update(
            dict(
                sender_timestamp=self._sender_timestamp,
                receiver_timestamp=self._receiver_timestamp,
                sender_uid=self._sender_uid,
                )
        )
        return res


class TimeSync(object):

    SYNC_INTERVAL = 2.0

    def __init__(self):
        self._last_active = time.time() - self.SYNC_INTERVAL
        self._sync_messages = {}


    def _active(self):
        now = time.time()
        if now - self._last_active >= self.SYNC_INTERVAL:
            self._last_active = now
            return True
        return False


    def activate(self, send):
        if self._active():
            msg = SyncMessage()
            self._sync_messages[msg.uid] = msg
            send(msg)

    def process(self, msg, send):
        type_ = msg["type"]
        if type_ == SyncMessage.TYPE:
            send(SyncAck(msg))
        elif type_ == SyncAck.TYPE:
            self.sync_ack(msg)


    def sync_ack(self, msg):
        original_uid = msg["sender_uid"]
        sync_msg = self._sync_messages.pop(original_uid, None)
        if sync_msg is None:
            logger.warn("Message already discarded for SYNC_ACK %r", msg)
            return
        sync_msg.ack(msg)


def setup_logging(_opts):
    logging.basicConfig(
        level=logging.DEBUG,
        stream=sys.stderr,
    )

def send_message(socket, message):
    payload = message.__json__()
    socket.send(json.dumps(payload))



def receive_message(socket, processors, send):
    while True:
        packet = socket.recv()
        now = time.time()
        message = json.loads(packet)
        message["received"] = now
        logger.debug(json.dumps(message))
        for processor in processors:
            processor.process(message, send)


def pi_protocol_test():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    opts = parser.parse_args()

    setup_logging(opts)

    uri = "tcp://{host}:{port}".format(host=opts.host, port=opts.port)

    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect(uri)
    time_sync = TimeSync()

    logger.info("Connecting to '%s'", uri)

    send = partial(send_message, socket)

    while True:
        packet = socket.recv()
        now = time.time()
        message = json.loads(packet)
        message["received"] = now
        logger.debug(json.dumps(message))
        time_sync.process(message, send)


def protocol_test():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=PORT)
    opts = parser.parse_args()
    setup_logging(opts)
    uri = "tcp://*:{port}".format(port=opts.port)

    context = zmq.Context()
    socket = context.socket(zmq.PAIR)

    socket.bind(uri)
    logger.info("Binding to '%s'", uri)

    time_sync = TimeSync()

    send_queue = Queue.Queue()
    receiver_thread = threading.Thread(
        target=partial(
            receive_message,
            socket,
            [time_sync],
            send_queue.put,
            ),
        )
    receiver_thread.setDaemon(True)
    receiver_thread.start()

    send = partial(send_message, socket)
    while True:
        time.sleep(.5)
        for _ in xrange(send_queue.qsize()):
            send(send_queue.get())
        time_sync.activate(send)
