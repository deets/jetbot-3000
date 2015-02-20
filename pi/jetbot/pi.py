#
import time
import argparse

from .base import (
    PiHub,
    setup_logging,
    )

from .protocol import TimeSync, DriveController


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

    timesync = TimeSync()
    hub += timesync
    hub += DriveController(timesync)

    while True:
        time.sleep(.1)
        hub.process_once()
