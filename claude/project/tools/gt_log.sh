#!/bin/bash
# gt_log.sh <run> ... - where each run stands: last time step lines and the last error / failure lines of its sdevice output.
# usage (anywhere): bash tools/gt_log.sh TF_c5 TF_c1
cd "$(dirname "$0")/../runs" || exit 1
for r in "$@"; do
  echo "== $r"
  grep -E 'Computing step|done \(|Transient finished' $r/$r.out | tail -3
  grep -n -i -E 'error|fail|not converge|aborted|singular' $r/$r.out | tail -4
  tail -4 $r/$r.out
done
