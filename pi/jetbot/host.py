#
import time
import argparse

from .base import (
    setup_logging,
    ServerHub,
    )

from .protocol import (
    TimeSync,
    DriveTest,
    )

def protocol_test():
    parser = argparse.ArgumentParser()
    ServerHub.setup_argparser(parser)
    opts = parser.parse_args()
    setup_logging(opts)
    hub = ServerHub.setup(opts)
    hub += TimeSync()

    while True:
        hub.process_once()



def drive_test():
    parser = argparse.ArgumentParser()
    ServerHub.setup_argparser(parser)

    opts = parser.parse_args()
    setup_logging(opts)
    hub = ServerHub.setup(opts)
    hub += TimeSync()
    hub += DriveTest(["forward"])

    while True:
        hub.process_once()
