#
import time
import argparse

from .base import (
    PiHub,
    setup_logging,
    )

from .protocol import TimeSync, DriveController
from .motorcontrol import MotorControl


def pi_protocol_test():
    parser = argparse.ArgumentParser()
    PiHub.setup_argparser(parser)
    opts = parser.parse_args()

    setup_logging(opts)
    hub = PiHub.setup(opts)

    hub += TimeSync()

    while True:
        time.sleep(.1)
        hub.process_once()


def jetbot_driver():
    parser = argparse.ArgumentParser()
    PiHub.setup_argparser(parser)
    opts = parser.parse_args()

    setup_logging(opts)
    hub = PiHub.setup(opts)

    mc = MotorControl()

    timesync = TimeSync()
    hub += timesync
    hub += DriveController(timesync, mc)

    mc.start()

    while True:
        time.sleep(.1)
        hub.process_once()


def motor_test():
    mc = MotorControl(command_timeout=10.0)
    mc.start()

    for command in ["forward", "reverse", "spin_left", "stop"]:
        mc.control(command)
        time.sleep(2.0)

    mc.stop()
