#!/bin/bash
rm -rf dist/* build/*
python2.7 setup.py sdist
ssh $JETBOT_VHOST "cd /tmp; rm JetBot*"

scp scripts/* $JETBOT_VHOST:/tmp
scp dist/* $JETBOT_VHOST:/tmp

ssh $JETBOT_VHOST "cd /tmp; $JETBOT_VHOST_PIP install -U JetBot*; /tmp/kill-old-server.sh"


