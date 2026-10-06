#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3 guard.py "$(head -n 1 queue.txt)"
if [ -f queue.pid ] && kill -0 "$(cat queue.pid)" 2>/dev/null; then
 echo 'Existing queue process is alive'; exit 1
fi
nohup bash run_queue.sh > queue.log 2>&1 < /dev/null &
echo $! > queue.pid
echo "Launched sequential queue PID=$(cat queue.pid)"
