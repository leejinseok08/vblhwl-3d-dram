#!/bin/bash
# gt_kill.sh <batch script name> <run-folder prefix> ... - stop one batch of ours: the batch script with its own job
# dispatcher (xargs) and the sdevice processes whose working directory is runs/<prefix>*. Other batches keep running
# (until 2026-10-06 this killed every dispatcher sitting in runs/, which stopped the queue of other batches).
# usage: bash tools/gt_kill.sh run_gt_tr.sh TW_ TF TR
#        bash tools/gt_kill.sh - DtfRz_zz DrcRz_zz   ("-" = no batch: only these runs stop, their batch goes on with its next run)
R="$(cd "$(dirname "$0")/../runs" && pwd)"; b=$1; shift
[ "$b" = - ] || for q in $(pgrep -u "$USER" -f "bash $b"); do pkill -P $q 2>/dev/null; kill $q 2>/dev/null; done
sleep 1
for p in $(pgrep -u "$USER" -f 'sdevice|sdevice_'); do
  d=$(readlink /proc/$p/cwd 2>/dev/null)
  case "$d" in "$R"/*) for pre in "$@"; do case "$(basename "$d")" in "$pre"*) kill $p 2>/dev/null && echo "killed $p $d";; esac; done;; esac
done
