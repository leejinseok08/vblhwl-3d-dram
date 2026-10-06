#!/bin/bash
# gt_check.sh <struct> [y_um] - net doping along the body of a sde_gt_dvs.cmd structure (horizontal cut at y, default
# 0.050 = body mid-height of the 20 nm cell): the first and last value and every sign change (= junction position).
# usage (anywhere, Sentaurus environment loaded):  bash tools/gt_check.sh gt_c2
cd "$(dirname "$0")/../runs/_struct" || exit 1
s=$1; y=${2:-0.050}
CHK_TDR=$PWD/${s}_msh.tdr CHK_X=0.125 CHK_OUT=$PWD/${s}_doping.csv CHK_Y=$y CHK_OUTH=$PWD/${s}_doping_ybody.csv \
  svisual -b ../../tools/chk_struct.tcl < /dev/null > /dev/null 2>&1
awk -F, 'NR == 3 { printf "%s at y=%s um: x=%s N=%s\n", S, Y, $1, $2 }
         NR > 3 && ($2 + 0) * (p + 0) < 0 { printf "  junction between x=%s and x=%s  (%s -> %s)\n", px, $1, p, $2 }
         NR > 2 { px = $1; p = $2 }
         END { printf "  last x=%s N=%s  (%d points)\n", px, p, NR - 2 }' S=$s Y=$y ${s}_doping_ybody.csv
