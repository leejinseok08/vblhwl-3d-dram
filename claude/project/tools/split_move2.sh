#!/bin/bash
# split_move2.sh - one-off: the structure files of the Cho cell (g?_*) that split_move.sh left behind (its shell pattern was wrong).
set -u; O=~/bcvfet_tcad; N=~/vblhwl_3d_dram; L=$N/moved_from_bcvfet_server.txt
pgrep -u "$USER" -x sdevice > /dev/null && { echo "sdevice is running: nothing moved"; exit 1; }
cd $O/runs/_struct || exit 1
for f in g[txrp3m]_*; do [ -e "$f" ] && mv "$f" $N/runs/_struct/ && echo "struct $f" >> $L; done
echo "cho structures now: $(ls $N/runs/_struct | grep -c _dvs.cmd) decks, $(ls $N/runs/_struct | grep -c _msh.tdr) meshes; g?_ left in bcvfet: $(ls | grep -c -E '^g[txrp3m]_')"
