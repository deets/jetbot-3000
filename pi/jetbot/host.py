#
import time
import argparse

from .base import (
    setup_logging,
    ServerHub,
    )

from .protocol import (
    TimeSync,
    )

def protocol_test():
    parser = argparse.ArgumentParser()
    ServerHub.setup_argparser(parser)
    opts = parser.parse_args()
    setup_logging(opts)
    hub = ServerHub.setup(opts)
    hub += TimeSync()

    while True:
        time.sleep(.5)
        hub.process_once()
