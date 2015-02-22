import sys
import signal
import threading
import logging
import Queue

# for our beloved host
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = object()


R1 = 24
R2 = 26
L1 = 19
L2 = 21

logger = logging.getLogger(__name__)


class MotorControl(object):

    DEFAULT_SPEED = 100

    def __init__(self, command_timeout=0.5):
        self._command_queue = Queue.Queue()
        self._timeout = command_timeout
        self._p = self._q = self._a = self._b = None
        self._setup()
        self._t = threading.Thread(target=self._mainloop)
        self._running = True
        self._stopped = True
        self._t.setDaemon(True)


    def _mainloop(self):
        try:
            while self._running:
                try:
                    command = self._command_queue.get(timeout=self._timeout)
                except Queue.Empty:
                    command = "stop"

                action = dict(
                    forward=self._forward,
                    spin_left=self._spin_left,
                    spin_right=self._spin_right,
                    stop=self._stop,
                    reverse=self._reverse,
                    shutdown=self._shutdown,
                    ).get(command, self._stop)

                action()

        finally:
            self._shutdown()


    def _shutdown(self):
        self._stop()
        self._running = False
        GPIO.cleanup()


    def start(self):
        self._t.start()


    def stop(self):
        self._running = False
        self._command_queue.put("shutdown")
        self._t.join()


    def control(self, command):
        self._command_queue.put(command)


    def _setup(self):
        #GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(L1, GPIO.OUT)
        self._p = GPIO.PWM(L1, 20)
        self._p.start(0)

        GPIO.setup(L2, GPIO.OUT)
        self._q = GPIO.PWM(L2, 20)
        self._q.start(0)

        GPIO.setup(R1, GPIO.OUT)
        self._a = GPIO.PWM(R1, 20)
        self._a.start(0)

        GPIO.setup(R2, GPIO.OUT)
        self._b = GPIO.PWM(R2, 20)
        self._b.start(0)

        def sighandler(_num, _frame):
            self._shutdown()
            sys.exit()

        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, sighandler)


    def _forward(self, speed=DEFAULT_SPEED):
        self._p.ChangeDutyCycle(speed)
        self._q.ChangeDutyCycle(0)
        self._a.ChangeDutyCycle(speed)
        self._b.ChangeDutyCycle(0)
        self._p.ChangeFrequency(speed + 5)
        self._a.ChangeFrequency(speed + 5)
        self._stopped = False


    # reverse(speed): Sets both motors to reverse at speed. 0 <= speed <= 100
    def _reverse(self, speed=DEFAULT_SPEED):
        self._p.ChangeDutyCycle(0)
        self._q.ChangeDutyCycle(speed)
        self._a.ChangeDutyCycle(0)
        self._b.ChangeDutyCycle(speed)
        self._q.ChangeFrequency(speed + 5)
        self._b.ChangeFrequency(speed + 5)
        self._stopped = False


    def _stop(self):
        if not self._stopped:
            self._p.ChangeDutyCycle(0)
            self._q.ChangeDutyCycle(0)
            self._a.ChangeDutyCycle(0)
            self._b.ChangeDutyCycle(0)
            self._stopped = True


    def _spin_left(self, speed=DEFAULT_SPEED):
        self._p.ChangeDutyCycle(0)
        self._q.ChangeDutyCycle(speed)
        self._a.ChangeDutyCycle(speed)
        self._b.ChangeDutyCycle(0)
        self._q.ChangeFrequency(speed + 5)
        self._a.ChangeFrequency(speed + 5)
        self._stopped = False


    def _spin_right(self, speed=DEFAULT_SPEED):
        self._p.ChangeDutyCycle(speed)
        self._q.ChangeDutyCycle(0)
        self._a.ChangeDutyCycle(0)
        self._b.ChangeDutyCycle(speed)
        self._p.ChangeFrequency(speed + 5)
        self._b.ChangeFrequency(speed + 5)


    def _turn_forward(self, left_speed=DEFAULT_SPEED, right_speed=DEFAULT_SPEED):
        self._p.ChangeDutyCycle(left_speed)
        self._q.ChangeDutyCycle(0)
        self._a.ChangeDutyCycle(right_speed)
        self._b.ChangeDutyCycle(0)
        self._p.ChangeFrequency(left_speed + 5)
        self._a.ChangeFrequency(right_speed + 5)
        self._stopped = False


    def _turn_reverse(self, left_speed=DEFAULT_SPEED, right_speed=DEFAULT_SPEED):
        self._p.ChangeDutyCycle(0)
        self._q.ChangeDutyCycle(left_speed)
        self._a.ChangeDutyCycle(0)
        self._b.ChangeDutyCycle(right_speed)
        self._q.ChangeFrequency(left_speed + 5)
        self._b.ChangeFrequency(right_speed + 5)
        self._stopped = False
