#!/bin/bash
# share_pack.sh : pack what goes into the shared GitHub repository (github.com/leejinseok08/vblhwl-3d-dram, folder claude/)
# from the server: the tables my tools print for the 2D completion rounds, and for every run of those rounds that is complete
# and whole (tools/run_state.py -c) its deck, run description and plot files. No meshes, no saved fields, no logs.
# Result: /tmp/share_vblhwl.tgz (outside the disk quota). Runs of the morning's WL-resistor scan (QS*, QR*, QY*) go along.
cd ~/vblhwl_3d_dram || exit 1
O=/tmp/share_vblhwl_$(date +%H%M%S); mkdir -p $O/tables; T=$O/tables
B=$(cd runs; ls run_d*.sh)
python3 tools/run_state.py -a $B | grep '^[A-Z]' | sort -u > $T/run_state.txt
# DtcRz_zz ran through the full-quota window of 2026-10-06 and lost whole rows (the first aggressor pulse): its files look whole
ids=$(for r in $(python3 tools/run_state.py -c $B); do [ $r = DtcRz_zz ] || echo -n "$r "; done)
q=$(cd runs; ls -d QS*_zz QR*_zz QY*_yy QSid_zz YE_c[1-5] 2>/dev/null | sort -u)    # the WL-resistor scan of the morning and the confirmed Id-Vg runs
# stopped by hand on 2026-10-06 once their question was settled; kept as evidence (whole up to the stop, the last row may be cut)
part=$(cd runs; ls -d Dw5Rzg_zz Dw7Rzg_zz Du7Rzg_zz Du9Rzg_zz Dw5Rzi_zz Dw7Rzi_zz Dk7F_c1 Dk7F_c2 Dv4F_c1 Dv4F_c2 Dv5F_c1 Dv5F_c2 2>/dev/null)
have() { for r in "$@"; do echo " $ids $q " | grep -q " $r " && echo $r; done; }    # only complete runs
python3 tools/score2d.py -v b0 cs ep e1 e2 w3 a5 ab r2 q0 q1 qn q3 f1 f2 f3 h1 h2 h3 h4 fin fin2 ra sx sh bw m1 k6 k7 > $T/scorecard.txt 2>&1
python3 tools/gt_fbe_tab.py Db0F Dq0F Dq1F DqnF Dq3F Df1F Df2F Df3F Dh1F Dh2F Dh3F Dh4F DfinF DraF DsxF DshF DbwF Dk6F Dk7F > $T/fbe_fig8_tables.txt 2>&1
for t in h1 fin ra k6 k7; do for c in 1 2 3 4 5; do [ -n "$(have D${t}F_c$c)" ] || continue; echo "D${t}F_c$c"; python3 tools/gt_tran.py runs/D${t}F_c$c 2>&1 | grep -E "FBE|paper Fig.8" | cut -c1-220; done; done > $T/fbe_loss_per_phase.txt
python3 tools/rh_tab.py $(have $(cd runs; ls -d Db0R* DcsR* DepR* Dr2R* DfinR* DtcR* DhaR* DhcR* DybR* DydR* Q[SRY]*_[yz][yz] 2>/dev/null)) > $T/row_hammer_table.txt 2>&1
for r in $(have $(cd runs; ls -d Dr2R* DfinR* DtcR* DhaR* DhcR* DybR* DydR* 2>/dev/null)); do python3 tools/gt_tran.py runs/$r 2>&1 | grep -E "^== |RH" | cut -c1-260; done > $T/row_hammer_cycle_by_cycle.txt
python3 tools/gt_wl_off.py $(for t in h1 j2 j3 j4 j5 j7 i1 q5 k6 k7; do for c in 1 2 3 4 5; do echo "$ids" | tr ' ' '\n' | grep -x "D${t}F_c$c"; done; done) > $T/write_and_wl_off_ii_factor.txt 2>&1
for r in $(have Db0W_c2 DcsW_c2 DfinW_c2 DraW_c2 Dw3W_c2 DsxW_c2 DshW_c2 DbwW_c2 Dm1W_c2); do python3 tools/gt_tran.py runs/$r 2>&1 | grep -E "^$r|W:|SN" | head -4 | cut -c1-220; done > $T/write_curves.txt
env GT_W=0.1 python3 tools/gt_fig5c.py $(for c in 1 2 3 4 5; do echo runs/DfinI_c$c; done) > $T/idvg_fig5c_fin.txt 2>&1
env GT_W=0.1 python3 tools/gt_fig5c.py $(for c in 1 2 3 4 5; do echo runs/YE_c$c; done) > $T/idvg_fig5c_b0_YE.txt 2>&1
env GT_W=0.1 python3 tools/gt_fig5c.py $(for r in $(have DsxI_c2 DshI_c2 DbwI_c2 Dm1I_c2); do echo runs/$r; done) > $T/idvg_fig5c_sensitivity_case2.txt 2>&1
cat runs/run_d*.check > $T/structure_checks_before_each_batch.txt 2>/dev/null
{ echo "Grounded body with the impact-ionization coefficients x5 / x7 / x9: the storage node from the write to the start of the hammer"
  echo "(DtcRzg_zz = the same deck with the default coefficients). Columns: time, node, BL, victim gate node or WL."
  for r in DtcRzg_zz Dw5Rzg_zz Dw7Rzg_zz; do python3 tools/plt_at.py $r 0.0 3.0 15 'nSN)' nBL nGv; done
  for r in Du7Rzg_zz Du9Rzg_zz; do python3 tools/plt_at.py $r 0.10 0.19 9 'nSN)' nBL 'nWL)'; done; } > $T/strong_ii_grounded_body_cannot_hold.txt 2>&1
python3 tools/gt_fbe_tab.py Dk6F Dk7F Dv4F Dv5F > $T/fbe_ii_factor_rounds_7_9.txt 2>&1
{ for z in z3 z4 z5 z6; do python3 tools/gt_long_hold.py $([ $z = z6 ] && echo -b) $(have D${z}F_c1 D${z}F_c2 D${z}F_c3 D${z}F_c4 D${z}F_c5); done; } > $T/fbe_long_hold_round11.txt 2>&1
python3 tools/gt_long_split.py > $T/fbe_long_hold_split_round11.txt 2>&1
python3 tools/gt_charged_t0.py > $T/charged_t0_check.txt 2>&1
python3 tools/gt_held.py > $T/held_node_round12.txt 2>&1
( cd runs; for r in $ids $q $part; do ls $r/${r}_des.cmd $r/run.json $r/*.plt 2>/dev/null; done; ls _struct/*_dvs.cmd ) > $O/files.txt
tar czf /tmp/share_vblhwl.tgz -C $O tables -C ~/vblhwl_3d_dram/runs -T $O/files.txt
echo "complete runs packed: $(echo $ids | wc -w) + scan and Id-Vg runs $(echo $q | wc -w) + partial runs kept as evidence $(echo $part | wc -w); files $(wc -l < $O/files.txt); $(ls -la /tmp/share_vblhwl.tgz | awk '{printf "%.1f MB", $5 / 1e6}')"
wc -c $T/* | tail -12
