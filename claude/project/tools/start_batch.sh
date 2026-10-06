#!/bin/bash
# start_batch.sh <batch script in runs/> <jobs> [struct ...] - start that batch in the background (log: <script>.log),
# then export the doping maps of the named structures (for the structure pictures). Refuses a batch already running.
b=$1; j=$2; shift 2
cd "$(dirname "$0")/../runs" || exit 1
pgrep -u "$USER" -f "bash $b" > /dev/null && { echo "$b already running"; exit 0; }
nohup bash $b $j > ${b%.sh}.log 2>&1 < /dev/null &
cd _struct
for s in "$@"; do for i in $(seq 60); do [ -f ${s}_msh.tdr ] && break; sleep 2; done; bash ../../tools/export_doping.sh $s; done
