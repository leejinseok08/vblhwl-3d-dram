#!/bin/bash
# gt3_check.sh <struct> [z_nm ...] - build a 3D Cho-cell structure (no device run) and print what is held against the paper:
# mesh size, regions, junction positions along the channel at body mid-height in the plane(s) z (default 25 nm = middle of
# the half victim row; give 175 as well for the aggressor row of the X-X' pair), where the silicon lies across the rows
# (x = gate centre, body mid-height) and where the word line is interrupted (main-gate level, x = gate centre).
# Geometry assumed: 20 nm body (mid-height y = 50 nm, main gate 65 .. 85 nm), 50 nm pillar (gate centre x = 100 nm).
# Expected from the paper (Fig.2 top view, Fig.5(a)): junctions at 25.00 nm (pillar face) and 150.00 nm (source-side gate
# edge); silicon rows 100 nm wide (half row 0 .. 50 nm; X-X' pair: also 150 .. 200 nm), isolation wall 100 nm between them.
# usage (Sentaurus environment loaded):  bash tools/gt3_check.sh g3_c2h        bash tools/gt3_check.sh g3x_c2h 25 175
cd "$(dirname "$0")/../runs/_struct" || exit 1
s=$1; shift; zs=${@:-25}
[ -f ${s}_msh.tdr ] || sde -e -l ${s}_dvs.cmd > ${s}_sde.log 2>&1
echo "== $s  $(grep -E 'points\.|elements\.' ${s}_sde.log | tr -s ' \n' ' ')  errors: $(grep -c -i -E '^error|\*\*\* error' ${s}_sde.log)"
[ -f ${s}_msh.tdr ] || { echo "   NO MESH"; tail -5 ${s}_sde.log; exit 1; }
first=1
for z in $zs; do
  rm -f ${s}_cutx.csv ${s}_cutz.csv ${s}_cutg.csv
  CHK_TDR=$PWD/${s}_msh.tdr CHK_Y=0.05 CHK_Z=$(echo "$z / 1000" | bc -l) CHK_X=0.1 CHK_YG=0.075 CHK_OUTH=$PWD/${s}_cutx.csv CHK_OUTW=$PWD/${s}_cutz.csv CHK_OUTG=$PWD/${s}_cutg.csv \
    svisual -b ../../tools/chk3d.tcl < /dev/null 2>&1 | grep -E '^REGIONS|FAILED' | cut -c1-600 | { [ $first = 1 ] && cat || grep FAILED; }
  awk -F, -v z=$z 'NR > 3 && ($2 + 0) * (p + 0) < 0 { printf "   z = %s nm, junction along the channel: %.2f..%.2f nm (%.3g -> %.3g)\n", z, px * 1000, $1 * 1000, p, $2 }
           NR > 2 { px = $1; p = $2 } END { printf "   z = %s nm, last point x = %.2f nm, %d points\n", z, px * 1000, NR - 2 }' ${s}_cutx.csv
  if [ $first = 1 ]; then
    [ -f ${s}_cutz.csv ] && sort -t, -k1,1g ${s}_cutz.csv | awk -F, '$1 + 0 == $1 { d = ($2 + 0 != 0); if (d && !on) { a = $1; on = 1 } if (!d && on) { printf "   silicon across the rows: z = %.2f .. %.2f nm\n", a * 1000, pz * 1000; on = 0 } pz = $1; e = $1 }
         END { if (on) printf "   silicon across the rows: z = %.2f .. %.2f nm\n", a * 1000, pz * 1000; printf "   the model ends at z = %.2f nm\n", e * 1000 }'
    if [ -s ${s}_cutg.csv ]; then sort -t, -k1,1g ${s}_cutg.csv | awk -F, '$1 + 0 == $1 { if (!n) a = $1; b = $1; n++ } END { if (n) printf "   main-gate level: word line interrupted from z = %.2f to %.2f nm (%d points)\n", a * 1000, b * 1000, n; else print "   main-gate level: word line not interrupted" }'
    else echo "   main-gate level: word line not interrupted"; fi
  fi
  first=0
done
