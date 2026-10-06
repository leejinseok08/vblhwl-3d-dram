#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
exec 9>queue.lock
flock -n 9 || { echo 'Queue already active'; exit 1; }
while IFS= read -r rid; do
 [ -n "$rid" ] || continue
 [ ! -f "runs/$rid/exit_code.txt" ] || continue
 python3 guard.py "$rid" || exit 2
 date -Is
 echo "START $rid (one sdevice, four threads)"
 printf '%s\n' "$rid" > current_run.txt
 cd "runs/$rid"
 set +e
 sdevice "${rid}_des.cmd" > "${rid}.out" 2>&1
 rc=$?
 set -e
 printf '%s\n' "$rc" > exit_code.txt
 cd ../..
 echo "END $rid rc=$rc"
 [ "$rc" -eq 0 ] || exit "$rc"
 python3 analyze.py > analysis.log 2>&1 || exit 3
done < queue.txt
echo COMPLETE > current_run.txt
