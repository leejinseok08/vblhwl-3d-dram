#!/bin/bash
# gt_precheck.sh <struct>:<tbody_nm>[:<layers>[:yy]] ... - the structure match that comes before every batch (user rule:
# no simulation before the structure is held against the paper). For each structure
#   (1) the dimensions and materials written into its structure file are compared with the paper: Fig.5(a) gate length 100,
#       gate oxide 5, gate 20, vertical isolation 30 nm, body thickness of the case (Fig.5(b): 30 / 20 / 10), source / drain
#       1e20, channel 1e18 or 1e16; from the drawing of Fig.2: both spacers 25 nm (0.25 Lg), the p body under the BL-side
#       spacer and the N+ source under the storage-node-side spacer (that is what puts the junctions where (2) expects them);
#   (2) the mesh must exist, and its junction positions and doping levels (three heights per layer) are read back:
#       single cell and zz pair: pillar face at 50.00 nm, source-side gate edge at 175.00 nm;
#       ":yy" (two cells across the 100 nm pillar, Fig.3(a)): 25.00 / 150.00 / 250.00 / 375.00 nm.
# Prints PASS / FAIL per structure and "ALL PASS" only if every line passed. Start a batch only after reading ALL PASS.
# Not from the paper (kept as they are, listed for the record): gate dielectric material, spacer material, pillar width.
# usage (Sentaurus environment loaded):  bash tools/gt_precheck.sh gr_c1h:30 gr_c2h:20 gr_c3h:10 gr_c4h:10 gr_zz:20:2 gr_yy:20:1:yy
cd "$(dirname "$0")/.." || exit 1
ok=1
val() { grep -m1 -E "^\(define $2 " runs/_struct/${1}_dvs.cmd | sed -E 's/^\(define [A-Za-z0-9]+ +//; s/\).*//; s/^\(\* *//; s/ nm$//; s/"//g; s/ +$//; s/\.0$//'; }
for a in "$@"; do
  s=${a%%:*}; r=${a#*:}; tb=${r%%:*}; nl=1; yy=0
  case "$r" in *:yy) yy=1; r=${r%:yy};; esac
  [ "$r" != "$tb" ] && nl=${r##*:}
  f=runs/_struct/${s}_dvs.cmd
  [ -f $f ] || { echo "FAIL $s: no structure file"; ok=0; continue; }
  card="Lg=$(val $s Lg) Tbody=$(val $s Tb) Tox=$(val $s Tox) Tg=$(val $s Tg) dVOX=$(val $s Dv) S1=$(val $s S1) S2=$(val $s S2) Nsd=$(val $s Nsd) Nch=$(val $s Nch)"
  want="Lg=100 Tbody=$tb Tox=5 Tg=20 dVOX=30 S1=25 S2=25 Nsd=1e+20"
  case "$card" in "$want Nch=1e+18"|"$want Nch=1e+16") c1=1;; *) c1=0;; esac
  mat="gate dielectric $(val $s Gdi), spacer $(val $s Spm), half pillar $(val $s Hb)"
  blx=$(val $s Blx); [ -n "$blx" ] && [ "$blx" != 0 ] && mat="$mat, BL pillar continued by $blx nm to its contact (Fig.2: the pillar runs through all layers)"
  # storage node drawn as a structure (2026-10-08): Fig.5(a) gives L_CAP 100 nm and EOT 3.8 A; shape and thicknesses are read off Fig.2
  cap=$(val $s Cap)
  if [ -n "$cap" ] && [ "$cap" != lump ]; then
    cc="Lcap=$(val $s Lcap) EOT=$(val $s Ceot)A"; [ "$cc" = "Lcap=100 EOT=3.8A" ] || c1=0
    card="$card $cc"; want="$want Lcap=100 EOT=3.8A"
    mat="$mat, storage capacitor '$cap' (shape from the Fig.2 cross-section): dielectric $(val $s Tcd) nm, node wall $(val $s Tcw) nm"
  fi
  [ -f runs/_struct/${s}_msh.tdr ] || { echo "FAIL $s: no mesh"; ok=0; continue; }
  out=$(bash tools/gt_mesh_check.sh $s $nl $tb)
  n=$(echo "$out" | grep -c .)
  # where the junctions have to be: pillar face and source-side gate edge, from the pillar width of the file (100 nm: 50.00 /
  # 175.00; "yy", two cells across the pillar: 25.00 / 150.00 / 250.00 / 375.00)
  hb=$(val $s Hb | awk '{print $1 * $2}'); P() { awk -v x="$1" 'BEGIN{printf "%.2f", x}'; }; E() { echo "$1" | sed 's/\./\\./g'; }
  NP='\(1e\+20 -> -1e\+1[68]\)'; PN='\(-1e\+1[68] -> 1e\+20\)'
  if [ $yy = 1 ]; then j1=$(P 25); j2=$(P 150); j3=$(P $(awk -v h=$hb 'BEGIN{print 150 + 2 * h}')); j4=$(P $(awk -v h=$hb 'BEGIN{print 275 + 2 * h}'))
    good=$(echo "$out" | grep -c -E "\| $(E $j1)\.\.$(E $j1) nm $NP \| $(E $j2)\.\.$(E $j2) nm $PN \| $(E $j3)\.\.$(E $j3) nm $NP \| $(E $j4)\.\.$(E $j4) nm $PN\$"); pos="$j1 / $j2 / $j3 / $j4"
  else j1=$(P $hb); j2=$(P $(awk -v h=$hb 'BEGIN{print h + 125}'))
    good=$(echo "$out" | grep -c -E "\| $(E $j1)\.\.$(E $j1) nm $NP \| $(E $j2)\.\.$(E $j2) nm $PN\$"); pos="$j1 / $j2"; fi
  lev=$(echo "$out" | grep -o -E -- '-1e\+1[68]' | sort -u | tr '\n' ' ')
  if [ $c1 = 1 ] && [ "$n" -eq $((3 * nl)) ] && [ "$good" -eq "$n" ]; then
    echo "PASS $s: Fig.5(a)/(b) $card | junctions at $pos nm at $n heights, N+ 1e+20, body $lev| not from the paper: $mat"
  else
    echo "FAIL $s: dimensions [$card] (paper: $want, Nch 1e+18 or 1e+16); junction lines as drawn: $good of $n"; echo "$out"; ok=0
  fi
done
[ $ok -eq 1 ] && echo "ALL PASS" || echo "NOT ALL PASS: do not start the batch"
