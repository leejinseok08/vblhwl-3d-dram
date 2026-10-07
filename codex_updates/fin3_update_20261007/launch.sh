#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 guard.py
nohup python3 -u run_queue.py > queue.log 2>&1 < /dev/null &
echo $! > queue.pid
echo "Started fin3 own-generation follow-up queue PID $(cat queue.pid)"
