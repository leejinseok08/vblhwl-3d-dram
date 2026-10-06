#!/bin/bash
# build_check.sh - build structures with sde, then report nodes, contacts and doping extremes.
# usage (in runs/_struct, Sentaurus environment loaded):  bash ../../tools/build_check.sh <struct>[:x_um] ...
#   x_um = x of the vertical doping cut (default 0.103 = channel centre)
HERE="$(cd "$(dirname "$0")" && pwd)"
for arg in "$@"; do
  s=${arg%%:*}; x=0.103; [ "$arg" != "$s" ] && x=${arg##*:}
  rm -f ${s}_msh.tdr ${s}_bnd*
  sde -e -l ${s}_dvs.cmd > ${s}_sde.log 2>&1; rc=$?
  echo "== $s  sde exit=$rc  $(grep -E 'points\.|elements\.' ${s}_sde.log | tr -s ' \n' ' ')"
  grep -i -E 'error|unbound|obsolete' ${s}_sde.log | sort | uniq -c | head -5
  [ -f ${s}_msh.tdr ] || { echo "   NO MESH"; continue; }
  CHK_TDR=$PWD/${s}_msh.tdr CHK_X=$x CHK_OUT=$PWD/${s}_doping.csv CHK_Y=0.119 CHK_OUTH=$PWD/${s}_doping_ybody.csv svisual -b "$HERE/chk_struct.tcl" < /dev/null 2>&1 \
    | grep '^REGIONS' | tr ' ' '\n' | grep -v -E '^R\.|\+|^REGIONS|JunctionLine|^$' | sort | tr '\n' ' ' | sed 's/^/   contacts: /'
  echo
  # net doping: max = N+ peak, min = P+ peak (must be Nsd and -Nbody, not 2x)
  [ -f ${s}_doping.csv ] || { echo "   (no doping cut: 3D mesh)"; continue; }
  awk -F, 'NR>2 { if ($2+0 > mx) mx = $2+0; if ($2+0 < mn) mn = $2+0 } END { printf "   doping at x=%s um: max %.3e  min %.3e\n", X, mx, mn }' X=$x ${s}_doping.csv
done
