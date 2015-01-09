#!/bin/bash

scp *.py $JETBOT_VHOST:jet-robot
scp -r static $JETBOT_VHOST:jet-robot
scp -r views $JETBOT_VHOST:jet-robot
