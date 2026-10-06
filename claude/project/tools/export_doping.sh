#!/bin/bash
# export_doping.sh <struct> [x1_um] [columns] — net doping of runs/_struct/<struct>_msh.tdr as one CSV (x_um,y_um,N).
# Run in runs/_struct with the Sentaurus environment loaded. Output: <struct>_dopmap.csv
s=$1; x1=${2:-0.0746}; nx=${3:-150}; tmp=$PWD/_dop_$s
rm -rf $tmp; mkdir $tmp
EXP_TDR=$PWD/${s}_msh.tdr EXP_OUT=$tmp EXP_X0=0 EXP_X1=$x1 EXP_NX=$nx \
  svisual -b "$(cd "$(dirname "$0")" && pwd)/export_doping.tcl" < /dev/null 2>&1 | grep -E '^(DONE|SKIP)|rror' | tail -5
python3 - "$tmp" "${s}_dopmap.csv" <<'EOF'
import sys, glob, csv, os
out = open(sys.argv[2], "w"); n = 0
for f in sorted(glob.glob(os.path.join(sys.argv[1], "cut_*.csv"))):
    x = float(os.path.basename(f)[:-4].split("_")[2])
    for r in list(csv.reader(open(f)))[2:]:
        if len(r) == 2: out.write(f"{x:.6f},{float(r[0]):.6f},{float(r[1]):.4e}\n"); n += 1
print("rows", n)
EOF
rm -rf $tmp; ls -la ${s}_dopmap.csv
