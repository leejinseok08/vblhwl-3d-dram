#!/bin/bash
# gt_start.sh <batch>.sh <jobs> <struct>:<tbody_nm>[:<layers>] ... - the way a batch is started (user rule: no run before the
# structure is checked against the paper). Builds any missing mesh of the named structures (structure only, no device run),
# runs gt_precheck.sh on them and starts the batch only if it prints ALL PASS. The named structures must be all the
# structures the batch uses (compared with the batch script). Single-cell sections only (gt_precheck.sh).
# usage (Sentaurus environment loaded):  bash tools/gt_start.sh run_cal1.sh 12 gr_c1h:30 gr_c2h:20
cd "$(dirname "$0")/.." || exit 1
b=$1; j=$2; shift 2
[ -f runs/$b ] || { echo "no batch runs/$b"; exit 1; }
# disk quota of the account (10 GB; full on 2026-10-06: runs died or lost parts of their plot files): about 40 MB per run must be free
nrun=0; for w in $(grep -E '^(printf|run) ' runs/$b); do [ -d "runs/$w" ] && nrun=$((nrun + 1)); done    # run ids = the words that are run folders
read used soft <<< "$(quota -w 2>/dev/null | awk 'NR>2 {u=$2; gsub(/\*/, "", u); print int(u / 1024), int($3 / 1024); exit}')"
echo "disk quota: ${used:-?} of ${soft:-?} MB used; $nrun runs"
[ -n "${soft:-}" ] && [ "$soft" -gt 0 ] && [ $((soft - used)) -lt $((nrun * 40)) ] && { echo "less than $((nrun * 40)) MB free: batch $b NOT started (bash tools/gz_logs.sh frees space)"; exit 1; }
need=$(grep -o -E '\[ -f [A-Za-z0-9_]+_msh.tdr \]' runs/$b | sed 's/\[ -f //;s/_msh.tdr \]//' | sort -u | tr '\n' ' ')
given=$(for a in "$@"; do echo ${a%%:*}; done | sort -u | tr '\n' ' ')
[ "$need" = "$given" ] || { echo "structures of the batch ($need) are not the ones named for the check ($given): not started"; exit 1; }
for a in "$@"; do s=${a%%:*}; [ -f runs/_struct/${s}_msh.tdr ] || ( cd runs/_struct && sde -e -l ${s}_dvs.cmd > ${s}_sde.log 2>&1 ); done
out=$(bash tools/gt_precheck.sh "$@"); echo "$out"
{ echo "structure match before $b, $(date '+%Y-%m-%d %H:%M:%S')"; echo "$out"; } > runs/${b%.sh}.check       # kept with the batch: what was checked
echo "$out" | tail -1 | grep -q '^ALL PASS$' || { echo "batch $b NOT started"; exit 1; }
bash tools/start_batch.sh $b $j && echo "batch $b started with $j jobs at $(date +%H:%M:%S)"
