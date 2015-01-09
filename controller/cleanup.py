#!/usr/bin/env python
import sys
import logging
import RPi.GPIO as GPIO


logger = logging.getLogger(__name__)

def main():
    GPIO.cleanup()


if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        )
    main()
