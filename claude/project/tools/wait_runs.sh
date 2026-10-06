#!/bin/bash
# wait_runs.sh <max seconds> <run id> ... - wait until every named run has ended (its .out says "Good Bye" or sdevice of that
# folder is gone), at most <max seconds>; a progress line every 10 minutes keeps the ssh session alive. Then print the
# transient summary of each run (tools/gt_tran.py, node voltages and row-hammer / FBE numbers only).
cd "$(dirname "$0")/.." || exit 1
max=$1; shift; t0=$(date +%s); last=0
while :; do
  left=0
  for r in "$@"; do grep -q "Good Bye" runs/$r/$r.out 2>/dev/null || left=$((left + 1)); done
  now=$(( $(date +%s) - t0 ))
  [ $left -eq 0 ] && { echo "all ended after $now s"; break; }
  [ $now -ge $max ] && { echo "still running after $now s: $left of $# runs"; break; }
  if [ $((now - last)) -ge 600 ]; then last=$now; echo "$(date +%H:%M) waiting, $left running: $(for r in "$@"; do echo -n "$r $(grep -c 'Computing BE-step' runs/$r/$r.out 2>/dev/null) steps; "; done)"; fi
  sleep 30
done
for r in "$@"; do python3 tools/gt_tran.py runs/$r | grep "==\|RH:\|FBE:\|write:\|aggressor" | cut -c1-240; echo "   $(grep -h 'wallclock' runs/$r/$r.out | tail -1)"; done
