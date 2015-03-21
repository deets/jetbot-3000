#
import argparse
from .server import WebConnector

from .base import (
    setup_logging,
    ServerHub,
    )

from .protocol import (
    TimeSync,
    DriveTest,
    wait_loop,
    StatusReporter,
    )


def protocol_test():
    parser = argparse.ArgumentParser()
    ServerHub.setup_argparser(parser)
    opts = parser.parse_args()
    setup_logging(opts)
    hub = ServerHub.setup(opts)
    hub += TimeSync()
    wait_loop(hub)


def drive_test():
    parser = argparse.ArgumentParser()
    ServerHub.setup_argparser(parser)

    opts = parser.parse_args()
    setup_logging(opts)
    hub = ServerHub.setup(opts)
    hub += TimeSync()
    hub += DriveTest(["spin_left", "forward", "spin_right", "reverse", "stop"])
    wait_loop(hub)


def server():
    parser = argparse.ArgumentParser()
    ServerHub.setup_argparser(parser)

    opts = parser.parse_args()
    setup_logging(opts)
    status_reporter = StatusReporter()
    hub = ServerHub.setup(opts)
    hub += TimeSync()
    hub += status_reporter
    hub += WebConnector(status_reporter=status_reporter)
    wait_loop(hub)
