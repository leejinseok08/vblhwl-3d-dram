#!/bin/bash
# gt_mesh_check.sh <struct> <layers> [tbody_nm] - numbers from the built mesh of a Cho-cell structure, to hold against the
# paper's drawing before any run: junction positions along the body at three heights of each layer (0.5 nm inside the lower
# face, mid-height, 0.5 nm inside the upper face) and the doping levels on both sides of each junction.
# layers = 1 or 2 (zz section). Geometry assumed: Dvox 30, Tgm 20, Tox 5 (body from 40 nm above the layer bottom, Z pitch 80 + body).
# usage (anywhere, Sentaurus environment loaded):  bash tools/gt_mesh_check.sh gr_yy 1
cd "$(dirname "$0")/../runs/_struct" || exit 1
s=$1; nl=${2:-1}; tb=${3:-20}; zp=$((80 + tb))
for l in $(seq 0 $((nl - 1))); do
  for f in 0.5 $(echo "$tb / 2" | bc -l) $(echo "$tb - 0.5" | bc -l); do
    y=$(echo "($l * $zp + 40 + $f) / 1000" | bc -l)
    CHK_TDR=$PWD/${s}_msh.tdr CHK_X=0.125 CHK_OUT=$PWD/${s}_doping.csv CHK_Y=$y CHK_OUTH=$PWD/${s}_doping_ybody.csv \
      svisual -b ../../tools/chk_struct.tcl < /dev/null > /dev/null 2>&1
    awk -F, 'NR > 3 && ($2 + 0) * (p + 0) < 0 { printf " | %.2f..%.2f nm (%.3g -> %.3g)", px * 1000, $1 * 1000, p, $2 }
             NR > 2 { px = $1; p = $2 } END { print "" }' ${s}_doping_ybody.csv | sed "s/^/$s layer $((l + 1)) y=$(printf %.4f $y):/"
  done
done
