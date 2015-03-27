#
import sys
import argparse
import logging
import time
import uuid
from random import random
import json
from functools import partial
import threading
import Queue
from itertools import cycle
from abc import ABCMeta, abstractmethod

from .base import message_valid

logger = logging.getLogger(__name__)


class Message(object):

    TYPE = None

    TIMESTAMP = "timestamp" # When this message was send
    RECEIVED = "received" # When this message was received at the sender

    def __init__(self, clock=time.time):
        self.uid = str(uuid.uuid4())
        self._clock = clock


    def __json__(self):
        assert self.TYPE is not None, \
          "You must subclass Message and define TYPE: %s" % \
          self.__class__.__name__
        return {
            'type': self.TYPE,
            'uid': self.uid,
            self.TIMESTAMP: self._clock()
            }

class SyncMessage(Message):

    TYPE = "TIME_SYNC"

    def __init__(self, *a, **k):
        super(SyncMessage, self).__init__(*a, **k)


    @classmethod
    def ack(cls, ack_msg):
        # as found on wikipedia
        # http://en.wikipedia.org/wiki/Network_Time_Protocol#Clock_synchronization_algorithm
        t0 = ack_msg["sender_timestamp"]
        t1 = ack_msg["receiver_timestamp"]
        t2 = ack_msg[Message.TIMESTAMP]
        t3 = ack_msg[Message.RECEIVED]

        total_roundtrip = t3 - t0
        processing_time = t2 - t1
        delay = total_roundtrip - processing_time
        offset = ((t1 - t0) + (t2 - t3)) / 2.0

        logger.debug("DELAY: %f", delay)
        logger.debug("OFFSET: %f", offset)
        return offset, delay


class SyncAck(Message):

    TYPE = "SYNC_ACK"

    def __init__(self, sync, *a, **k):
        super(SyncAck, self).__init__(*a, **k)
        self._sender_timestamp = sync[Message.TIMESTAMP]
        self._receiver_timestamp = sync[Message.RECEIVED]
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



class Protocol(object):

    __metaclass__ = ABCMeta


    @abstractmethod
    def activate(self, send):
        """
        Called in an intervall
        by the HUB to perform whatever
        work necessary, and possibly send
        messages.
        """
        pass


    @abstractmethod
    def process(self, msg, send):
        """
        Invoked by the receiving background-thread
        when a message comes in. It's possible to send
        messages.
        """
        pass



class IntervalActivationMixin(object):

    def __init__(self, activation_interval, clock=time.time):
        self._activation_interval = activation_interval
        self._last_active = clock() - self._activation_interval
        self._clock = clock


    def _active(self):
        now = self._clock()
        if now - self._last_active >= self._activation_interval:
            self._last_active = now
            return True
        return False


class TimeSync(Protocol, IntervalActivationMixin):

    SYNC_INTERVAL = 2.0

    def __init__(self, clock=time.time):
        super(TimeSync, self).__init__(
            activation_interval=self.SYNC_INTERVAL,
            clock=clock,
            )
        self._sync_messages = {}
        self._clock = clock
        self._offset, self._delay = None, None
        self._updated = clock() - self.SYNC_INTERVAL * 2


    def _active(self):
        now = self._clock()
        if now - self._last_active >= self.SYNC_INTERVAL:
            self._last_active = now
            return True
        return False


    def activate(self, send):
        if self._active():
            msg = SyncMessage(clock=self._clock)
            self._sync_messages[msg.uid] = msg
            send(msg)


    def process(self, msg, send):
        type_ = msg["type"]
        if type_ == SyncMessage.TYPE:
            send(SyncAck(msg, clock=self._clock))
        elif type_ == SyncAck.TYPE:
            self.sync_ack(msg)


    def sync_ack(self, msg):
        original_uid = msg["sender_uid"]
        sync_msg = self._sync_messages.pop(original_uid, None)
        if sync_msg is None:
            logger.warn("Message already discarded for SYNC_ACK %r", msg)
            return
        self._offset, self._delay = sync_msg.ack(msg)
        self._updated = self._clock()


    @property
    def offset(self):
        if self._clock() <= self._updated + self.SYNC_INTERVAL * 2.0:
            return self._offset


    @property
    def delay(self):
        if self._clock() <= self._updated + self.SYNC_INTERVAL * 2.0:
            return self._delay


class Drive(Message):

    def __init__(self, command, *a, **k):
        super(Drive, self).__init__(*a, **k)
        self.TYPE = command



class DriveTest(Protocol, IntervalActivationMixin):

    INTERVAL = 0.1


    def __init__(self, commands, *a, **k):
        super(DriveTest, self).__init__(
            activation_interval=self.INTERVAL,
            *a,
            **k
        )
        self._commands = cycle(commands)


    def activate(self, send):
        if not self._active():
            return
        command = self._commands.next()
        logger.info("Sending %s", command)
        send(Drive(command, self._randomized_clock))


    def _randomized_clock(self):
        now = self._clock()
        now -= random()
        return now


    def process(self, _msg, _send):
        pass


class DriveController(Protocol):

    def __init__(self, timesync, motorcontrol, threshold=0.5, *a, **k):
        super(DriveController, self).__init__(
            *a,
            **k
        )
        self._timesync = timesync
        self._threshold = threshold
        self._motorcontrol = motorcontrol


    def activate(self, send):
        pass


    def process(self, msg, _send):
        if msg["type"] in  ("forward", "spin_left", "spin_right", "stop", "reverse"):
            if self._message_valid(msg):
                logger.info("Driving: %s", msg["type"])
                self._motorcontrol.control(msg["type"])
            else:
                logger.warn("Discarding invalid message %r", msg)
                self._motorcontrol.control("stop")


    def _message_valid(self, msg):
        # align timestamp to our own clock
        offset = self._timesync.offset
        if offset is None:
            logger.info("Not yet enough time-sync info")
            return False
        return message_valid(
            self._threshold,
            msg[Message.RECEIVED],
            msg[Message.TIMESTAMP],
            offset
            )


class StatusReporter(Protocol):

    DISCONNECTION_TIMEOUT = 2.0

    def __init__(self):
        self._last_message_retrieved = time.time() - self.DISCONNECTION_TIMEOUT


    @property
    def status(self):
        if time.time() - self._last_message_retrieved > \
          self.DISCONNECTION_TIMEOUT:
            return "disconnected"
        return "connected"


    def process(self, _msg, _send):
        self._last_message_retrieved = time.time()


    def activate(self, _send):
        pass


def wait_loop(hub):
    hub.start()
    while True:
        time.sleep(.1)
        hub.process_once()
