import unittest

from jetbot.protocol import TimeSync, Message


class FakeTimeSource(object):

    def __init__(self, offset, drift=1.0):
        self._start = self._timestamp = 1000.0
        self._offset = offset
        self._drift = drift


    def advance(self, offset):
        self._timestamp += offset


    def t1(self):
        return self._timestamp


    def t2(self):
        return self._start + \
          (self._timestamp - self._start + self._offset)\
           * self._drift


class TimeSyncingTests(unittest.TestCase):


    def test_fake_source_offset(self):
        offset = 10.0
        ts = FakeTimeSource(offset)
        self.assertEqual(ts.t1() + offset, ts.t2())


    def test_fake_source_advance(self):
        offset = 10.0
        ts = FakeTimeSource(offset)
        ts.advance(100.0)
        self.assertEqual(1100.0, ts.t1())


    def test_fake_source_advance(self):
        offset = 10.0
        ts = FakeTimeSource(offset)
        ts.advance(100.0)
        self.assertEqual(1100.0 + offset, ts.t2())


    def test_fake_source_drift(self):
        ts = FakeTimeSource(0.0, drift=2.0)
        ts.advance(1.0)
        self.assertEqual(1001.0, ts.t1())
        self.assertEqual(1002.0, ts.t2())


    def test_offset_determined(self):
        ts = FakeTimeSource(5.0) # the other is 5.0 seconds in the future
        here = TimeSync(clock=ts.t1)
        there = TimeSync(clock=ts.t2)

        messages = []
        def send(msg):
            messages.append(msg)

        here.activate(send)
        self.assertEqual(1, len(messages))
        message_to_send = messages[0].__json__()
        messages[:] = []

        ts.advance(.1) # network lag

        message_to_send[Message.RECEIVED] = ts.t2()

        there.process(message_to_send, send)
        self.assertEqual(1, len(messages))

        message_received = messages[0].__json__()
        messages[:] = []

        ts.advance(.1) # network lag

        message_received[Message.RECEIVED] = ts.t1()

        here.process(message_received, send)

        self.assertEqual(5.0, here.offset)
        self.assertTrue(abs(0.2 - here.delay) < .0001)
