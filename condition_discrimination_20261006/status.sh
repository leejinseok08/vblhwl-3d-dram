#!/bin/bash
set -eu
cd "$(dirname "$0")"
date -Is
cat queue.pid
cat queue.log
rid=$(cat current_run.txt)
if [ "$rid" != COMPLETE ]; then
 echo "CURRENT $rid"
 ps -u "$(id -un)" -o pid,ppid,etime,args | grep -E 'CDH_|CDR_|run_queue.sh' | grep -v grep || true
 tail -n 16 "runs/$rid/$rid.out"
fi
