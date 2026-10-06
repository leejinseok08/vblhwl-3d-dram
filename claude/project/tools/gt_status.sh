#!/bin/bash
# gt_status.sh [run ...] - state of the Cho-device runs: mesh sizes of the gt_* structures, the batch logs, progress of the
# named runs (default: all GT* folders), and the Id-Vg summary line of those that have a curve.
# usage (anywhere, Sentaurus environment loaded):  bash tools/gt_status.sh [GTH_c2 ...]
cd "$(dirname "$0")/../runs" || exit 1
for f in _struct/gt_*_sde.log; do echo "$(basename $f _sde.log): $(grep -E 'points\.' $f | tr -s ' \n' ' ') $(grep -c -i 'error' $f) error lines"; done
for l in run_gt*.log; do echo "== $l: $(tr '\n' ' ' < $l)"; done
[ $# -gt 0 ] || set -- GT*
bash ../tools/progress.sh "$@" | grep -E '^GT'
for r in "$@"; do ls $r/IdVg_*.plt > /dev/null 2>&1 && python3 ../tools/peek.py $r | head -1; done
