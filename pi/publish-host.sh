#!/bin/bash
rm -rf dist/* build/*
python2.7 setup.py sdist
scp dist/* $JETBOT_VHOST:/tmp

ssh $JETBOT_VHOST "cd /tmp; /home/deets/.virtualenvs/jetbot/bin/pip install -U JetBot*"

