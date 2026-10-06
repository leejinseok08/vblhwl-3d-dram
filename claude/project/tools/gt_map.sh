#!/bin/bash
# gt_map.sh <file.tdr> <x0_um> <x1_um> <nx> <y0_um> <y1_um> "<var> <var> ..." - fields of a 2D device plot inside a window, from
# vertical cuts every (x1-x0)/nx: per variable the maximum and where, and for Band2BandGeneration also the integral over the
# window as a current per 100 nm wide cell. Without variables: list the fields of the file.
# The field magnitude is "Abs(ElectricField-V)". Run with the Sentaurus environment loaded.
# usage: bash tools/gt_map.sh runs/CHn0_c1/end_c1_CHn0_c1_dev.tdr 0.150 0.200 100 0.035 0.075 "Abs(ElectricField-V) Band2BandGeneration"
f=$(readlink -f "$1"); here="$(cd "$(dirname "$0")" && pwd)"; tmp=$(mktemp -d)
MAP_TDR=$f MAP_OUT=$tmp MAP_X0=${2:-0} MAP_X1=${3:-0.25} MAP_NX=${4:-50} MAP_VARS="$7" svisual -b $here/export_map.tcl < /dev/null 2>&1 | grep -E '^(FIELDS|SKIP)|rror' | cut -c1-1500 | head -5
[ -z "$7" ] && { rm -rf $tmp; exit 0; }
python3 - "$tmp" "$5" "$6" "$2" "$3" "$4" <<'EOF'
import sys, glob, csv, os
d, y0, y1, x0, x1, nx = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
dx = (x1 - x0) / nx; best = {}; integ = {}; names = None
for f in sorted(glob.glob(os.path.join(d, "cut_*.csv"))):
    x = float(os.path.basename(f)[:-4].split("_")[2]); rows = list(csv.reader(open(f)))
    names = [c.strip() for c in rows[0]][1:]
    pts = []
    for r in rows[2:]:
        try: v = [float(c) for c in r]
        except ValueError: continue
        if len(v) == len(names) + 1 and y0 <= v[0] <= y1: pts.append(v)
    pts.sort()
    for j, n in enumerate(names):
        for v in pts:
            if n not in best or abs(v[j + 1]) > abs(best[n][0]): best[n] = (v[j + 1], x, v[0])
        integ[n] = integ.get(n, 0.0) + sum((a[j + 1] + b[j + 1]) / 2 * (b[0] - a[0]) for a, b in zip(pts, pts[1:])) * dx      # [unit] um^2
for n in names or []:
    extra = f" | integral over the window = {integ[n] * 0.1 * 1e-12 * 1.602e-19 * 1e9:.4g} nA per cell" if "Generation" in n or "Recombination" in n else ""
    print(f"   {n:28s} max {best[n][0]:.4e} at x = {best[n][1] * 1000:.2f} nm, y = {best[n][2] * 1000:.2f} nm{extra}")
EOF
rm -rf $tmp
