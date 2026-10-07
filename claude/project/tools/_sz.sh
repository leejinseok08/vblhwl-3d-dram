#!/bin/bash
# _sz.sh [n] : size of the plot files (MB) and the number of rows of the runs of rounds 15 - 20 and the 3D confirmation, largest
# first (what a share would weigh). The patterns are inside the script: the remote shell (tcsh) would expand them itself.
cd ~/vblhwl_3d_dram/runs || exit 1
for d in Dg?R* Do?F_c? Do?W_c2 Dx?R* E3S?_c2; do [ -d "$d" ] || continue; s=$(du -cm $d/*.plt 2>/dev/null | tail -1 | cut -f1); echo "$s MB  $d  rows $(grep -c '^ *[-0-9]' $d/${d}_sys.plt 2>/dev/null)"; done | sort -n -r | head -${1:-25}
