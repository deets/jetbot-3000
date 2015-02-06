#!/bin/bash
rm -rf dist/* build/*
python2.7 setup.py sdist
scp dist/* pi@192.168.2.2:/tmp

ssh pi@192.168.2.2 "cd /tmp; /home/pi/.virtualenvs/jetbot/bin/pip install -U JetBot*"

