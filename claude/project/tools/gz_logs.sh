#!/bin/bash
# gz_logs.sh [-n] : gzip the sdevice logs and stdout captures (*.log, *.out) in the folders of runs that are not running.
# Nothing is deleted: every file is compressed outside the quota first, tested, and only then put in the original's place
# as <name>.gz (gunzip brings it back). Why: the account's disk quota is 10 GB and the .log / .out pair of a run (the same
# text twice) made 3.0 of the 4.4 GB under runs/ on 2026-10-06, when runs died with "Disk quota exceeded".
# -n = only say what would be done; -bg = under nohup, report in /tmp/gz_logs_vblhwl.out. Folders with a live process and files touched in the last 10 minutes are left alone;
# codex_validation is never entered (it lies outside runs/).
if [ "$1" = -bg ]; then nohup bash $0 > /tmp/gz_logs_vblhwl.out 2>&1 & exit 0; fi    # survives a dropped ssh session
cd ${GZ_RUNS:-$HOME/vblhwl_3d_dram/runs} || exit 1    # GZ_RUNS = another runs folder of ours (e.g. ~/bcvfet_tcad/runs)
dry=$1; mkdir -p /tmp/gzlog_$USER
live=$(for p in /proc/[0-9]*; do [ -O $p ] && readlink $p/cwd; done 2>/dev/null | grep "$PWD/" | sed "s|$PWD/||; s|/.*||" | sort -u)
echo "live run folders left alone: $(echo $live | wc -w)"
before=$(quota -s 2>/dev/null | awk 'NR>2 && $1 ~ /M|G/ {print $1; exit}')
n=0; b0=0; b1=0
for f in $(find . -mindepth 2 -maxdepth 2 -type f \( -name '*.log' -o -name '*.out' \) -size +50k -mmin +10 | sed 's|^\./||' | sort); do
  d=${f%%/*}
  echo "$live" | grep -qx "$d" && continue
  s=$(stat -c %s "$f"); n=$((n + 1)); b0=$((b0 + s))
  [ "$dry" = -n ] && continue
  t=/tmp/gzlog_$USER/${f//\//__}.gz    # named after the file: a copy left behind can be put back by hand
  if gzip -c "$f" > $t && gzip -t $t; then
    rm "$f"
    if ! cp $t "$f.gz"; then sleep 3; cp $t "$f.gz" || { echo "STOP: the compressed copy of $f is kept in $t"; exit 1; }; fi
    cmp -s $t "$f.gz" || { echo "STOP: $f.gz differs from $t (kept)"; exit 1; }
    b1=$((b1 + $(stat -c %s "$f.gz"))); rm $t
  else
    echo "not compressed (left as it is): $f"; rm -f $t
  fi
done
echo "files: $n, before ${b0} bytes = $((b0 / 1000000)) MB, after $((b1 / 1000000)) MB"
echo "quota used: $before -> $(quota -s 2>/dev/null | awk 'NR>2 && $1 ~ /M|G/ {print $1; exit}')"
