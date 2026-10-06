#!/bin/bash
# gt3_top.sh <struct> [zmax_nm] [step_nm] - a 3D Cho-cell mesh seen from above, for the picture next to the top view of the
# paper's Fig.2 (tools/plot_gt3.py on the PC). Along the channel (x) in planes z = step/2, 3 step/2, .. : net doping at body
# mid-height (y = 50 nm: which silicon is n, which is p, where the wall is) and the points that exist at main-gate level
# (y = 75 nm: gate metal is a contact and has no mesh points, so points there are oxide or spacer).
# Writes runs/_struct/<struct>_top.csv with lines  level,z_nm,x_nm,doping  (level = body / gate).
cd "$(dirname "$0")/../runs/_struct" || exit 1
s=$1; zmax=${2:-200}; st=${3:-5}; tmp=$(mktemp -d)
cat > $tmp/top.tcl <<EOF
set d [load_file $PWD/${s}_msh.tdr]
set p [create_plot -dataset \$d]
for {set z [expr {$st / 2.0}]} {\$z < $zmax} {set z [expr {\$z + $st}]} {
  if {[catch {
    set c [create_cutplane -plot \$p -type z -at [expr {\$z / 1000.0}]]
    set q [create_plot -dataset \$c]
    foreach {y name} {0.05 body 0.075 gate} {
      if {[catch {
        set l [create_cutline -plot \$q -type y -at \$y]
        export_variables {X DopingConcentration} -dataset \$l -filename [format "$tmp/%s_%07.2f.csv" \$name \$z] -overwrite
      } e2]} { }
    }
  } e1]} { puts "SKIP \$z: \$e1" }
}
exit
EOF
svisual -b $tmp/top.tcl < /dev/null 2>&1 | grep SKIP | head -3
python3 - $tmp ${s}_top.csv <<'EOF'
import sys, glob, os, csv
out = open(sys.argv[2], "w"); n = 0
for f in sorted(glob.glob(os.path.join(sys.argv[1], "*.csv"))):
    lev, z = os.path.basename(f)[:-4].split("_")
    for r in list(csv.reader(open(f)))[2:]:
        try: out.write(f"{lev},{float(z):.2f},{float(r[0]) * 1000:.3f},{float(r[1]):.4e}\n"); n += 1
        except (ValueError, IndexError): pass
print("rows", n)
EOF
rm -rf $tmp; ls -la ${s}_top.csv
