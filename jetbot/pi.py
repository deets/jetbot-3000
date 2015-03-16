#
import time
import argparse

from .base import (
    PiHub,
    setup_logging,
    )

from .protocol import TimeSync, DriveController, wait_loop
from .motorcontrol import MotorControl


def pi_protocol_test():
    parser = argparse.ArgumentParser()
    PiHub.setup_argparser(parser)
    opts = parser.parse_args()

    setup_logging(opts)
    hub = PiHub.setup(opts)

    hub += TimeSync()

    scheduler(hub)


def jetbot_driver(motor_control_class=MotorControl, scheduler=wait_loop):
    parser = argparse.ArgumentParser()
    PiHub.setup_argparser(parser)
    opts = parser.parse_args()

    setup_logging(opts)
    hub = PiHub.setup(opts)

    mc = motor_control_class()

    timesync = TimeSync()
    hub += timesync
    hub += DriveController(timesync, mc)

    mc.start()
    scheduler(hub)


def motor_test():
    mc = MotorControl(command_timeout=10.0)
    mc.start()

    for command in ["forward", "reverse", "spin_left", "stop"]:
        mc.control(command)
        time.sleep(2.0)

    mc.stop()


def gui_simulator():
    from .gui import GuiMotorControl
    gmc = GuiMotorControl()
    jetbot_driver(
        motor_control_class=gmc,
        scheduler=gmc.scheduler,
        )
