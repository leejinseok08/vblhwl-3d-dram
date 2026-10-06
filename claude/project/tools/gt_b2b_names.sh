#!/bin/bash
# gt_b2b_names.sh [all] - print the band-to-band tunnelling section of the default silicon parameter file of this Sentaurus
# release (names, defaults, the formulas in its comments). Run before changing a coefficient by name.
# Without argument: the Hurkx lines only; with "all": the whole Band2BandTunneling section.
t=$(mktemp -d); cd $t || exit 1
sdevice -P:Silicon > /dev/null 2>&1 < /dev/null
if [ "$1" = all ]; then awk '/^Band2BandTunneling/{f=1} f{print NR": "$0} f&&/^}/{exit}' models.par | cut -c1-230
else grep -n -E 'Agen|Bgen|Pgen|Arec|Brec|Prec|^Band2BandTunneling|Hurkx|D = ' models.par | head -16; fi
cd /; rm -rf $t
