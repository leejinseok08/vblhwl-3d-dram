#!/bin/bash
# _rh_tab.sh [out] : the table of rounds 16 - 19 (row hammer: the aggressor's impact-ionization holes reaching the victim) as one text
# file: per configuration the node per cycle, per run the pairs and holes per cycle, the body at the instants of Fig.7(e), and the
# node and body inside the cycles (8 points per cycle). The same text goes into the share pack; tools/plot_rh_transfer.py reads it.
cd ~/vblhwl_3d_dram || exit 1
o=${1:-/tmp/rh_rounds16_19.txt}
G=$(cd runs; echo $(ls -d Dg[0-9]R* 2>/dev/null))
{ python3 tools/gt_rh_hist.py -c fin g1 g2 g3 g4 g5 g6 g7 g8 g9 g0; python3 tools/gt_rh_pairs.py DfinRzi_zz DfinRyi_yy $G; python3 tools/gt_rh_body.py $G
  for r in DfinRzi_zz $G; do python3 tools/gt_rh_wave.py $r; done; } > $o 2>&1
wc -l $o
