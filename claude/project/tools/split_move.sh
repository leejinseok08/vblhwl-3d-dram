#!/bin/bash
# split_move.sh - one-off (2026-10-05), server side of the Chen / Cho split: move the Cho-cell run folders, structures, batch
# files, previews, templates, parameter files and tools from ~/bcvfet_tcad to ~/vblhwl_3d_dram. Nothing is deleted; the names
# moved are listed in ~/vblhwl_3d_dram/moved_from_bcvfet_server.txt. codex_validation is not touched.
set -u; O=~/bcvfet_tcad; N=~/vblhwl_3d_dram; L=$N/moved_from_bcvfet_server.txt
pgrep -u "$USER" -x sdevice > /dev/null && { echo "sdevice is running: nothing moved"; exit 1; }
mkdir -p $N/runs/_struct $N/tools $N/preview
cd $O/runs || exit 1
for d in */; do r=${d%/}; [ "$r" = "_struct" ] && continue
  grep -q -E '_struct/g[txrp3m][0-9a-z]*_' $r/${r}_des.cmd 2>/dev/null && mv $r $N/runs/ && echo "run $r" >> $L
done
for f in _struct/*; do b=$(basename $f); case "$b" in g[txrp3m][0-9a-z]*_*) mv $f $N/runs/_struct/ && echo "struct $b" >> $L;; esac; done
for f in run_gt* run_gx* run_gr_* run_g3.* run_hm.* run_cal.*; do [ -f "$f" ] && mv $f $N/runs/ && echo "batch $f" >> $L; done
cd $O
for f in sdevice_gt_*.par sde_gt_dvs.cmd sde_gt3_dvs.cmd; do [ -e $f ] && mv $f $N/ && echo "file $f" >> $L; done
for f in tools/gt_* tools/gt3_* tools/plot_gt.py tools/chk3d.tcl tools/export_gt_pkg.py tools/build_gt_results.py; do [ -e $f ] && mv $f $N/tools/ && echo "tool $f" >> $L; done
for f in preview/cho_* preview/g[xrpm]*; do [ -e $f ] && mv $f $N/preview/ && echo "preview $f" >> $L; done
echo "moved $(grep -c . $L) entries; cho runs $(ls $N/runs | wc -l), left in bcvfet $(ls $O/runs | wc -l); cho structures $(ls $N/runs/_struct | grep -c _dvs.cmd)"
