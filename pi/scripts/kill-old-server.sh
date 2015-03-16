#!/bin/bash
ps aux | grep jetbot/bin/server | grep -v grep | awk '{ print $2 }' | xargs kill
echo "killed old server, supervisord restarts"
