#!/bin/bash
rm -rf dist/* build/*
python2.7 setup.py sdist
scp dist/* pi@$JETBOT_PI:/tmp

ssh pi@$JETBOT_PI "cd /tmp; $JETBOT_PI_PIP install -U JetBot*"

