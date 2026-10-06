#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3 guard.py FC013_c1
nohup python3 -u run_queue.py > queue.log 2>&1 < /dev/null &
echo "$!" > queue.pid
echo "LAUNCHED candidate screening queue PID $(cat queue.pid), 8 workers, 720 conditions (20 reused)"
