#!/bin/bash
# _q.sh - scratch query script (overwritten for each one-off question that needs quotes; see CLAUDE.md, server section)
# usage: bash tools/_q.sh <mode> [seconds to wait first] [arguments]
#   r3d = rebuild the two 3D structures from today's structure files (old meshes moved aside) and run the 3D checks + top views
#   st = state of every run of rounds 4-6 (tools/run_state.py) | sa = one line per run that is not complete | live | du = disk | cx = Codex's plot files
#   rh <runs> = row-hammer table | s <tags> = scorecard | t <tags> = loss after every BL-low phase | wo <tags> = write and WL switch-off
#   ii = the impact-ionization factor runs | w <runs> = write curves | steps <runs> = their last time steps
cd ~/vblhwl_3d_dram
if [ "$1" = mat ]; then    # mat <pattern>: material names of the installed release (datexcodes.txt)
  f=$(find $(dirname $(dirname $(dirname $(readlink -f $(which sdevice))))) -path '*/lib/datexcodes.txt' 2>/dev/null | head -1); echo "$f"
  grep -B2 -E "group *= *$2" "$f" | grep '{' | tr -d ' {' | paste -sd' ' | fold -s -w 180; exit 0     # all materials of that group (Insulator, Conductor, Semiconductor)
fi
if [ "$1" = m1s ]; then    # round 32: meshes of the cells with the drawn storage capacitor (structure only, no device run), check, doping maps, contacts
  S="gs_c1hb gs_c2hb gs_c3hb gs18_c2hb gs0_c2hb"
  ( cd runs/_struct; for s in $S; do [ -f ${s}_msh.tdr ] || sde -e -l ${s}_dvs.cmd > ${s}_sde.log 2>&1; ls -la --time-style=+%H:%M ${s}_msh.tdr | awk '{print $7, $5, $6}'
      grep -i -E 'error|warn|fail' ${s}_sde.log | head -3; grep -h -i -E 'contact|vertices|elements' ${s}_msh.log 2>/dev/null | head -12 | cut -c1-150; done
    for s in gs_c2hb gs18_c2hb gs0_c2hb; do bash ../../tools/export_doping.sh $s 0.200 | tail -1; done )
  bash tools/gt_precheck.sh gs_c1hb:30 gs_c2hb:20 gs_c3hb:10 gs18_c2hb:20 gs0_c2hb:20
  exit 0
fi
if [ "$1" = ga ]; then    # ga <struct>: build a mini-array structure (sde_gt3a_dvs.cmd; structure only, no device run): mesh size, errors, regions, contacts
  cd runs/_struct; s=$2; rm -f ${s}_msh.tdr ${s}_bnd.tdr; t0=$(date +%s); sde -e -l ${s}_dvs.cmd > ${s}_sde.log 2>&1; echo "$s: sde took $(( $(date +%s) - t0 )) s"
  grep -i -E 'error|fail|cannot|unbound|invalid' ${s}_sde.log | sort | uniq -c | head -12; grep -E 'points\.|elements\.' ${s}_sde.log | tr -s ' \n' ' '; echo
  ls -la --time-style=+%H:%M ${s}_msh.tdr ${s}_bnd.tdr 2>&1 | awk '{print $7, $5, $6}'; tail -4 ${s}_sde.log | cut -c1-200
  exit 0
fi
if [ "$1" = gab ]; then    # gab <struct>: the same build detached (structure only); gas <struct>: how far it is
  cd runs/_struct; rm -f $2_msh.tdr $2_bnd.tdr; nohup sde -e -l $2_dvs.cmd > $2_sde.log 2>&1 < /dev/null & echo "sde of $2 started $(date +%H:%M:%S)"; exit 0
fi
if [ "$1" = gas ]; then
  cd runs/_struct; s=$2; n=0; while [ $n -lt ${3:-0} ] && pgrep -u "$USER" -f "sde -e -l ${s}_dvs" > /dev/null; do sleep 10; n=$((n + 10)); done; date +%H:%M:%S; pgrep -u "$USER" -a -f "sde|snmesh" | cut -c1-80; grep -i -E 'error|fail|cannot|unbound|invalid' ${s}_sde.log | sort | uniq -c | head -8
  grep -E 'points\.|elements\.' ${s}_sde.log | tr -s ' \n' ' '; echo; ls -la --time-style=+%H:%M ${s}_msh.tdr ${s}_bnd.tdr 2>&1 | awk '{print $7, $5, $6}'; tail -3 ${s}_sde.log | cut -c1-160; exit 0
fi
if [ "$1" = gad ]; then    # gad <struct>: the mesh as DF-ISE text (tdx), its head and section sizes
  cd runs/_struct; s=$2; python3 -c 'import numpy; print("numpy", numpy.__version__)'; rm -f ${s}_msh.grd ${s}_msh.dat; tdx -dd ${s}_msh.tdr > ${s}_tdx.log 2>&1; tail -2 ${s}_tdx.log; ls -la ${s}_msh.grd* | awk '{print $5, $9}'
  zcat -f ${s}_msh.grd* | head -40 | cut -c1-200; zcat -f ${s}_msh.grd* | grep -n -E '^ *(Vertices|Edges|Faces|Locations|Elements|Region)' | head -20 | cut -c1-120; exit 0
fi
if [ "$1" = gac ]; then    # gac <struct>: cuts of a mini-array mesh for the pictures next to Fig.2 (tools/grd_cut.py -> runs/_struct/<struct>_cut_*.json, packed into /tmp/<struct>_cuts.tgz)
  cd runs/_struct; s=$2; [ -f ${s}_msh.grd ] || tdx -dd ${s}_msh.tdr > ${s}_tdx.log 2>&1
  python3 ../../tools/grd_cut.py ${s}_msh.grd --info z $3 ${s}_cut_xsec.json y $4 ${s}_cut_body.json y $5 ${s}_cut_gate.json y $6 ${s}_cut_fin.json x $7 ${s}_cut_cap.json x $8 ${s}_cut_wl.json
  tar czf /tmp/${s}_cuts.tgz ${s}_cut_*.json; ls -la /tmp/${s}_cuts.tgz | awk '{print $5, $9}'; rm -f ${s}_msh.grd ${s}_msh.dat; exit 0
fi
if [ "$1" = gat ]; then    # gat <struct>: what the running build logs within 60 s (which contact step, how many per minute)
  cd runs/_struct; f=$2_sde.log; for i in 1 2; do date +%H:%M:%S; wc -l < $f; grep -c 'sdegeo:set-contact' $f; grep -c 'delete-region' $f; tail -c 300 $f | tr -s '
' ' ' | cut -c1-200; echo; [ $i = 1 ] && sleep 60; done
  grep -o 'sdegeo:set-contact (list.*' $f | tail -1 | grep -o 'find-face-id' | wc -l; exit 0
fi
if [ "$1" = gak ]; then    # gak <struct>: stop the structure build of <struct>
  pkill -u "$USER" -f "sde -e -l $2_dvs"; sleep 1; pgrep -u "$USER" -a -f "sde -e -l" | cut -c1-60; nproc; exit 0
fi
if [ "$1" = m9 ]; then # the paper's sentences on Fig.7 / Fig.8(c) against fin7: body of the victim at t_A (Fig.7(e): 2.4 / 665.1 / 1.8 mV), pairs and holes per cycle, on-current of Cases 3 - 5 (text: +3.9 % from Case 3 to 5)
  python3 tools/gt_rh_body.py DptRzb_zz DptRzbi_zz DptRzbg_zz DptRyi_yy 2>&1 | cut -c1-210
  python3 tools/gt_rh_pairs.py DptRzbi_zz DptiRzbi_zz 2>&1 | cut -c1-210
  env GT_W=0.1 python3 tools/gt_fig5c.py runs/Dpb2I_c3 runs/Dpb2I_c4 runs/Dpb2I_c5 | cut -c1-200
  exit 0
fi
if [ "$1" = m8 ]; then   # round 38: m8 <seconds to wait>: state, the write table (fin7 without a model first) and the node before / after the WL goes off
  sleep $2; date +%H:%M:%S; python3 tools/run_state.py run_d38.sh | cut -c1-300
  R="DptW_c2 DwnvW_c2 DwnlW_c2 DwnuW_c2 DwovW_c2 DwolW_c2 DwouW_c2"; python3 tools/gt_write_tab.py $R; python3 tools/gt_wl_off.py $R | cut -c1-120
  exit 0
fi
if [ "$1" = m7 ]; then    # round 37, second part: meshes of the two spacer variants (structure only), check, start of the four DC runs
  ( cd runs/_struct; for s in gbh_c2hb gbo_c2hb; do [ -f ${s}_msh.tdr ] || sde -e -l ${s}_dvs.cmd > ${s}_sde.log 2>&1; grep -i -E 'error|fail' ${s}_sde.log | head -3; done )
  bash tools/gt_start.sh run_d37b.sh 4 gb2_c4hb:10 gbh_c2hb:20 gbo_c2hb:20
  exit 0
fi
if [ "$1" = m6 ]; then    # round 36: m6 <seconds to wait>: state, then fin6 and fin6t (text capacitors) side by side, and the write table
  sleep $2; date +%H:%M:%S; python3 tools/run_state.py run_d35.sh run_d36.sh | cut -c1-400
  python3 tools/score2d.py -v fin6 fin6t | grep -v -E 'IV:|RH:' | cut -c1-520; python3 tools/gt_write_tab.py Dpb2W_c2 DptW_c2; python3 tools/repro_rate.py fin6t | cut -c1-200
  exit 0
fi
if [ "$1" = m5s ]; then    # round 35: meshes of the pairs with the BL pillar continued by two pitches (structure only, no device run), check, doping maps
  ( cd runs/_struct; for s in gb2_yy gb2_zz gb2_zzg; do [ -f ${s}_msh.tdr ] || sde -e -l ${s}_dvs.cmd > ${s}_sde.log 2>&1; ls -la --time-style=+%H:%M ${s}_msh.tdr | awk '{print $7, $5, $6}'
      grep -i -E 'error|fail' ${s}_sde.log | head -3; grep -h -E 'Optimizing elements' ${s}_msh.log 2>/dev/null | head -1; done
    bash ../../tools/export_doping.sh gb2_zz 0.200 | tail -1; bash ../../tools/export_doping.sh gb2_yy 0.400 300 | tail -1 )
  bash tools/gt_precheck.sh gb2_c1hb:30 gb2_c3hb:10 gb2_c4hb:10 gb2_yy:20:1:yy gb2_zz:20:2 gb2_zzg:20:2
  exit 0
fi
if [ "$1" = m5 ]; then    # round 35: m5 <seconds to wait>: state, then the scorecard of fin5 and fin6 and the share of items inside the tolerance
  sleep $2; date +%H:%M:%S; python3 tools/run_state.py run_d35.sh | cut -c1-500
  python3 tools/score2d.py -v fin5 fin6 | cut -c1-520; python3 tools/repro_rate.py fin5 fin6 | cut -c1-330
  exit 0
fi
if [ "$1" = m4s ]; then    # round 34: meshes of the cells with the BL pillar continued to its contact (structure only, no device run), check, doping map
  S="gb1_c1hb gb2_c1hb gb4_c1hb gb1_c2hb gb2_c2hb gb4_c2hb"
  ( cd runs/_struct; for s in $S; do [ -f ${s}_msh.tdr ] || sde -e -l ${s}_dvs.cmd > ${s}_sde.log 2>&1; ls -la --time-style=+%H:%M ${s}_msh.tdr | awk '{print $7, $5, $6}'
      grep -i -E 'error|fail' ${s}_sde.log | head -3; grep -h -E 'Optimizing elements' ${s}_msh.log 2>/dev/null | head -1; done
    bash ../../tools/export_doping.sh gb2_c2hb 0.200 | tail -1 )
  bash tools/gt_precheck.sh gb1_c1hb:30 gb2_c1hb:30 gb4_c1hb:30 gb1_c2hb:20 gb2_c2hb:20 gb4_c2hb:20 gr_c1hb:30 gr_c2hb:20
  exit 0
fi
if [ "$1" = m4 ]; then    # round 34: m4 <seconds to wait>: state, then bars and losses of fin5 (dy) and of the pillar variants, Cases 1 and 2
  sleep $2; date +%H:%M:%S; python3 tools/run_state.py run_d34.sh run_d34b.sh | cut -c1-500
  python3 tools/score2d.py -v dy pb1 pb2 pb4 pbn | awk '/^[a-z]/ {t=$1; print} /BR:/ {n=split($0, a, ";"); for (i = 1; i <= (t == "pb2" || t == "dy" ? n : 2); i++) print t, "|", a[i]} /IV:/ && t == "pb2" {split($0, a, ";"); print t, "|", a[2]} /W:/ && t == "pb2" {print t, "|", $0}' | cut -c1-200
  exit 0
fi
if [ "$1" = m4b ]; then    # round 34b: meshes of the 10 nm cells with the pillar continued by 2 pitches (structure only), check, start
  ( cd runs/_struct; for s in gb2_c3hb gb2_c4hb; do [ -f ${s}_msh.tdr ] || sde -e -l ${s}_dvs.cmd > ${s}_sde.log 2>&1; grep -i -E 'error|fail' ${s}_sde.log | head -3; done )
  bash tools/gt_start.sh run_d34b.sh 3 gb2_c3hb:10 gb2_c4hb:10
  exit 0
fi
if [ "$1" = pk ]; then    # rounds 32 / 33 for the shared repository: tables -> /tmp/tables_r3233.txt; deck, run description and plot files of the complete runs -> /tmp/share_r3233.tgz
  { echo "Rounds 32, 33 (2026-10-08): the storage node drawn as a structure after the Fig.2 cross-section; an avalanche model in the write on it. NOTES (bu), (bv)."
    echo; echo "== capacitance at 0 V, AC 1 MHz (tools/gt_cap.py)"; python3 tools/gt_cap.py DsaC_c1 DsaC_c2 DsaC_c3 DsbC_c2 DscC_c2
    echo; echo "== write of Fig.4(a) (tools/gt_write_tab.py; Cs = lumped capacitor of the deck: 0.00 = drawn node). sa / sb / sc = as drawn / walls 18 nm / solid node;"
    echo "   m<model><force>: v o l u = vanOverstraeten Okuto Lackner UniBo, 0 1 2 = default Eparallel ElectricField; DdyW_c2 = fin5"
    python3 tools/gt_write_tab.py DdyW_c2 DsaW_c2 DsbW_c2 DscW_c2 $(cd runs; ls -d Dm[volu][012]W_c2)
    echo; echo "== write + 21 ns hold, no stand-in, no BL pulses (tools/gt_wl_off.py); Fig.8(a) asks for 1371 holes and +445 mV in Case 2"
    python3 tools/gt_wl_off.py DmnF_c2 $(cd runs; ls -d Dm[volu][012]F_c2)
    echo; echo "== round 34: where the BL is measured. dy = fin5 (contact on the end face of a pillar one layer long); pb1 / pb2 / pb4 = pillar continued by 1 / 2 / 4 Z pitches"
    echo "   to its contact; pbn = contact that takes no holes. BR line: per case the bar (rise), the first-phase loss and the later loss [mV]. NOTES (bw), MEASURE.md 4.6"
    python3 tools/score2d.py -v dy pb1 pb2 pb4 pbn | grep -v -E 'RH:|IV: c1' | cut -c1-420; python3 tools/gt_write_tab.py DdyW_c2 Dpb2W_c2
    env GT_W=0.1 python3 tools/gt_fig5c.py runs/DdyI_c2 runs/Dpb2I_c2
    echo; echo "== rounds 35, 36: fin6 = fin5 measured at the BL pillar end two Z pitches away (tag pb2); fin6t = fin6 with the capacitors of the paper's text,"
    echo "   5.1 / 4.2 / 3.6 fF (tag pt). NOTES (bx), (bz). Row hammer of fin6: attack minus idle where both runs are complete."
    python3 tools/score2d.py -v fin5 fin6 fin6t | cut -c1-520; python3 tools/gt_write_tab.py DdyW_c2 Dpb2W_c2 DptW_c2; python3 tools/repro_rate.py fin5 fin6 fin6t | cut -c1-330
    echo; echo "== round 37: fin7 = fin6 with the text's capacitors (the device since 17:30), and why the current is low: DC charging current along the write"
    echo "   (gates 1.8 V, BL 1.168 V, node swept) and where the BL-to-node voltage falls. DpL_c<n> = Case n; DpLh / DpLo = Case 2 with HfO2 / SiO2 spacers. NOTES (ca)"
    python3 tools/gt_loadline.py DpL_c1 DpL_c2 DpL_c3 DpL_c4 DpL_c5 DpLh_c2 DpLo_c2
    echo "-- the write of each case with its own text capacitor (first 105 ps of the FBE runs of round 36)"; python3 tools/gt_wl_off.py DptF_c1 DptF_c2 DptF_c3 DptF_c4 DptF_c5 | cut -c1-80
    python3 tools/score2d.py -v fin6 fin7 | cut -c1-640; python3 tools/repro_rate.py fin6 fin7 | cut -c1-330
    echo; echo "== round 38 (a trial): the write of fin7's Case 2 cell (4.2 fF) with an avalanche model driven by ElectricField. wn* = Si3N4 spacers (the device), wo* = SiO2;"
    echo "   v / l / u = vanOverstraeten / Lackner / UniBo; DptW_c2 = fin7, no model. NOTES (cd)"
    R38="DptW_c2 DwnvW_c2 DwnlW_c2 DwnuW_c2 DwovW_c2 DwolW_c2 DwouW_c2"; python3 tools/gt_write_tab.py $R38; python3 tools/gt_wl_off.py $R38 | cut -c1-120
    echo; echo "== state of the runs at $(date '+%H:%M')"; python3 tools/run_state.py run_d32.sh run_d33.sh run_d34.sh run_d34b.sh run_d35.sh run_d36.sh run_d37.sh run_d37b.sh run_d37r.sh run_d38.sh
    echo; echo "== structure checks before the batches"; cat runs/run_d32.check runs/run_d33.check runs/run_d34.check runs/run_d34b.check runs/run_d35.check runs/run_d36.check runs/run_d37.check runs/run_d37b.check runs/run_d37r.check runs/run_d38.check; } > /tmp/tables_r3233.txt 2>&1
  ids=$(python3 tools/run_state.py -c run_d32.sh run_d33.sh run_d34.sh run_d34b.sh run_d35.sh run_d36.sh run_d37.sh run_d37b.sh run_d37r.sh run_d38.sh)
  ( cd runs; for r in $ids; do ls $r/${r}_des.cmd $r/run.json $r/*.plt 2>/dev/null; done; ls _struct/gs*_dvs.cmd _struct/gb*_dvs.cmd ) > /tmp/share_r3233.lst
  tar czf /tmp/share_r3233.tgz -C runs -T /tmp/share_r3233.lst; echo "$(echo $ids | wc -w) complete runs packed, $(ls -la /tmp/share_r3233.tgz | awk '{printf "%.1f MB", $5 / 1e6}'); tables $(wc -l < /tmp/tables_r3233.txt) lines"
  exit 0
fi
if [ "$1" = m3 ]; then    # rounds 32 / 33: m3 <seconds to wait> <tags>: state of the two batches, then score and the four points of the write of each tag
  sleep $2; shift; shift; date +%H:%M:%S; python3 tools/run_state.py run_d32.sh run_d33.sh | cut -c1-700
  python3 tools/score2d.py -v "$@" | awk '/^[a-z]/ {t=$1; w=$3} /W:/ {print t, "| W score", w, "|", $2, $3, $4, $5, $6, $7, $8, $9, $10}'
  python3 tools/gt_wl_off.py $(for t in "$@"; do [ -d runs/D${t}F_c2 ] && echo D${t}F_c2; done) | cut -c1-230      # write + hold runs: pairs, holes left, state at t_A
  exit 0
fi
m=$1; [ -n "$2" ] && sleep $2; shift; shift
if [ "$m" = r3d ]; then
  mkdir -p runs/_unused/struct3d_before_rebuild
  for s in g3_c2h g3x_c2h; do for e in msh.tdr bnd.tdr sde.log top.csv cutx.csv cutz.csv cutg.csv; do f=runs/_struct/${s}_$e; [ -f $f ] && mv $f runs/_unused/struct3d_before_rebuild/; done; done
  bash tools/gt3_check.sh g3_c2h 25
  bash tools/gt3_check.sh g3x_c2h 25 175
  bash tools/gt3_top.sh g3_c2h 100 5 | tail -2
  bash tools/gt3_top.sh g3x_c2h 200 5 | tail -2
  ls -la --time-style=+%H:%M runs/_struct/g3_c2h_msh.tdr runs/_struct/g3x_c2h_msh.tdr runs/_struct/g3_c2h_top.csv runs/_struct/g3x_c2h_top.csv | awk '{print $6, $5, $7}'
  exit 0
fi
if [ "$m" = du ]; then
  quota -s 2>/dev/null | tail -4; df -h ~ | tail -1
  echo "--- home [MB]"; du -sm ~/* 2>/dev/null | sort -n -r | head -8
  echo "--- this project [MB]"; du -sm * 2>/dev/null | sort -n -r | head -8
  echo "--- runs by kind"; find runs -type f -printf '%s %f\n' | awk '{n=split($2,a,"."); e=a[n]; if ($2 ~ /_des\.tdr$/) e="des.tdr"; s[e]+=$1; c[e]++} END{for(k in s) printf "%9.0f MB %6d files  %s\n", s[k]/1e6, c[k], k}' | sort -n -r | head -12
  echo "--- biggest run folders [MB]"; du -sm runs/* | sort -n -r | head -30
  exit 0
fi
if [ "$m" = sz ]; then    # what a share of the 2D completion rounds (runs D*) would weigh: decks, run descriptions, plot files
  for k in '*.plt' '*_des.cmd' 'run.json' '*.tdr'; do echo "$k: $(find runs -maxdepth 2 -path 'runs/D*' -name "$k" | wc -l) files, $(find runs -maxdepth 2 -path 'runs/D*' -name "$k" -printf '%s\n' | awk '{s+=$1} END{printf "%.1f MB", s/1e6}')"; done
  echo "run folders D*: $(ls -d runs/D*/ | wc -l); by round tag:"; ls -d runs/D*/ | sed 's|runs/D||; s|[IWFR].*||' | sort | uniq -c | awk '{printf "%s:%s ", $2, $1}'; echo
  echo "biggest plot files:"; find runs -maxdepth 2 -path 'runs/D*' -name '*.plt' -printf '%s %p\n' | sort -n -r | head -5
  exit 0
fi
if [ "$m" = live ]; then
  for p in $(pgrep -u "$USER" -x sdevice); do echo "$(readlink /proc/$p/cwd | sed "s|$HOME/vblhwl_3d_dram/||; s|^runs/||") $(ps -o etime= -p $p | tr -d ' ')"; done | sort | paste -sd' ' | fold -s -w 190
  exit 0
fi
if [ "$m" = steps ]; then    # how the named runs step in time: their last three time steps (a stalled run shows steps of 1e-15 s and less)
  for r in "$@"; do f=runs/$r/$r.out; [ -f $f ] || f=$f.gz; echo "=== $r"; zcat -f $f | grep -E 'Computing .*step from' | tail -3 | cut -c1-120; done
  exit 0
fi
if [ "$m" = why ]; then    # why the named runs ended: the last steps and the last failure lines of their output
  for r in "$@"; do f=runs/$r/$r.out; [ -f $f ] || f=$f.gz; echo "=== $r"; zcat -f $f | grep -E 'Computing|Step size|not converge|failed|rror' | tail -7 | cut -c1-150; done
  exit 0
fi
if [ "$m" = cb ]; then    # the four single cells with the BL contact at the bottom end of the pillar: mesh (structure only), check, doping map of Case 2
  ( cd runs/_struct; for s in gr_c1hb gr_c2hb gr_c3hb gr_c4hb; do [ -f ${s}_msh.tdr ] || sde -e -l ${s}_dvs.cmd > ${s}_sde.log 2>&1; ls -la --time-style=+%H:%M ${s}_msh.tdr | awk '{print $7, $5, $6}'; done
    bash ../../tools/export_doping.sh gr_c2hb 0.200 | tail -2; wc -l gr_c2hb_dopmap.csv )
  bash tools/gt_precheck.sh gr_c1hb:30 gr_c2hb:20 gr_c3hb:10 gr_c4hb:10
  exit 0
fi
if [ "$m" = zb ]; then    # the two pair structures with the BL contact at the bottom end of the pillar: mesh (structure only), check, doping map
  ( cd runs/_struct; for s in gr_zzb gr_zzbg; do [ -f ${s}_msh.tdr ] || sde -e -l ${s}_dvs.cmd > ${s}_sde.log 2>&1; ls -la --time-style=+%H:%M ${s}_msh.tdr | awk '{print $7, $5, $6}'; done
    bash ../../tools/export_doping.sh gr_zzb 0.200 | tail -2; wc -l gr_zzb_dopmap.csv )
  bash tools/gt_precheck.sh gr_zz:20:2 gr_zzb:20:2 gr_zzbg:20:2
  exit 0
fi
if [ "$m" = dq ]; then    # what the full disk quota of 2026-10-06 did: runs whose log or stdout names a write failure
  echo "--- batch logs: lines other than exit=0"; grep -v 'exit=0$' runs/run_d4.log runs/run_d4y.log runs/run_d4r.log runs/run_d5.log | cut -c1-150
  echo "--- runs touched in the last 4 h whose log / stdout names a write failure (first hit, its line number, mtime of the file)"
  for f in $(find runs codex_validation -mindepth 2 -type f \( -name '*.log' -o -name '*.out' -o -name '*.log.gz' -o -name '*.out.gz' \) -mmin -240 | sort); do
    h=$(zgrep -n -i -m1 -E 'quota exceeded|no space left|write error|cannot write|could not write|error writing|i/o error' $f 2>/dev/null) && echo "$f [$(date -r $f +%H:%M)] $(echo "$h" | cut -c1-140)"
  done
  echo "--- first time the batch log shows the quota"; ls -la --time-style=+%H:%M runs/run_d5.log runs/run_d4.log | awk '{print $6, $7}'
  for r in Dj5F_c2 Dj5F_c4 Dj5F_c5 Dj7F_c2 Dq5F_c1 Dq5F_c2; do echo "=== $r: $(ls --time-style=+%H:%M -la runs/$r | awk 'NR>1 && $7 !~ /^\.+$/ {printf "%s(%s,%s) ", $7, $5, $6}' | cut -c1-400)"; for f in runs/$r/$r.out runs/$r/$r.out.gz; do [ -f $f ] && zcat -f $f | tail -4 | cut -c1-160; done; done
  exit 0
fi
if [ "$m" = cx ]; then    # read-only: are the system plot files that Codex's runs wrote in the last 3 h whole? (disk quota full 18:14-18:25)
  f=$(find codex_validation -name '*_sys.plt' -mmin -180 | sort); [ -z "$f" ] && { echo "no *_sys.plt; plot files there:"; find codex_validation -name '*.plt' -mmin -180 | head -5; exit 0; }
  python3 tools/run_state.py -f $f | grep -v github_share | sed 's|codex_validation/||' | grep -v '^ok' ; echo "(files tested: $(echo $f | wc -w); only the damaged ones are listed)"
  for d in $(for p in $(pgrep -u "$USER" -x sdevice); do readlink /proc/$p/cwd; done | grep codex_validation); do echo "live: ${d#*codex_validation/}: $(ls -la --time-style=+%H:%M $d | awk 'NR>1 && $7 ~ /plt|log|out/ {printf "%s(%s,%s) ", $7, $5, $6}')"; done
  exit 0
fi
if [ "$m" = lh ]; then    # round 11: state of the batch, then the long-hold table of the named tags (z3 z4 z5 z6), all cases
  python3 tools/run_state.py run_d11.sh | cut -c1-400; R=""; for t in "$@"; do for c in 1 2 3 4 5; do R="$R D${t}F_c$c"; done; done; python3 tools/gt_long_hold.py $R; exit 0
fi
B=$(cd runs; ls run_d4.sh run_d4y.sh run_d4r.sh run_d5.sh run_d6.sh 2>/dev/null)
if [ "$m" = start6 ]; then bash tools/gt_start.sh run_d6.sh "$@"; m=st; fi
if [ "$m" = sa ]; then python3 tools/run_state.py -a $B | grep -E 'running|DAMAGED|no output|stopped' | sort -u; exit 0; fi
date +%H:%M; python3 tools/run_state.py $B | cut -c1-900; bash tools/_q.sh live; echo "disk quota: $(quota -s | tail -1 | awk '{print $1, "of", $2}'), $(uptime | sed 's/.*load/load/')"
[ "$m" = st ] && exit 0
if [ "$m" = pf ]; then for r in "$@"; do python3 tools/run_state.py -f runs/$r/*.plt | sed 's|runs/[^/]*/||'; done; exit 0; fi    # every plot file of the named runs
if [ "$m" = rp ]; then for r in "$@"; do python3 tools/gt_tran.py runs/$r 2>&1 | grep -E "^== |probe|Pos\(|hole|Hole|body" | cut -c1-200 | head -14; done; exit 0; fi    # row hammer: the body probes at the marked instants
if [ "$m" = rc ]; then for r in "$@"; do python3 tools/gt_tran.py runs/$r 2>&1 | grep -E "^== |RH" | cut -c1-260; done; exit 0; fi    # row hammer cycle by cycle
if [ "$m" = c1 ]; then    # the first hammer cycle of the named runs: node, victim gate node, aggressor WL every 15 ps
  for r in "$@"; do t0=$(python3 tools/gt_tran.py runs/$r 2>&1 | grep -o 'first aggressor rise at [0-9.]*' | grep -o '[0-9.]*$'); [ -z "$t0" ] && t0=3.04; python3 tools/plt_at.py $r $(echo "$t0 - 0.03" | bc -l) $(echo "$t0 + 0.39" | bc -l) 28 'nSN)' nGv nWLa 'nBL'; done; exit 0
fi
if [ "$m" = mt ]; then    # runs of rounds 4 / 5 whose plot files were last written in or after the quota window and not rewritten by round 6
  d6=" $(grep '^printf' runs/run_d6.sh) $(grep '^printf' runs/run_d7.sh 2>/dev/null) "
  for r in $(cat runs/run_d4.sh runs/run_d4y.sh runs/run_d4r.sh runs/run_d5.sh | grep '^printf' | tr ' ' '\n' | sort -u); do
    [ -d runs/$r ] || continue; case "$d6" in *" $r "*) continue;; esac
    f=$(ls -t runs/$r/*.plt 2>/dev/null | head -1); [ -z "$f" ] && continue
    echo "$(date -r $f +%H:%M) $r"
  done | sort | awk '$1 >= "18:08"' | paste -sd' ' | fold -s -w 180
  exit 0
fi
if [ "$m" = tl ]; then for r in "$@"; do echo "=== $r ($(date -r runs/$r/${r}_log_des.log +%H:%M:%S))"; tail -c 2500 runs/$r/${r}_log_des.log | grep -v '^ *$' | tail -14 | cut -c1-150; done; exit 0; fi
if [ "$m" = rh ]; then python3 tools/rh_tab.py "$@"; exit 0; fi
if [ "$m" = wo ]; then R=""; for t in "$@"; do for c in 1 2 3 4 5; do [ -d runs/D${t}F_c$c ] && R="$R D${t}F_c$c"; done; done; python3 tools/gt_wl_off.py $R; exit 0; fi
if [ "$m" = jj ]; then for t in "$@"; do for c in 1 2 3 4 5; do [ -d runs/D${t}F_c$c ] || continue; python3 tools/gt_probes.py -w -q D${t}F_c$c 2>&1 | tail -1; done; done; exit 0; fi
if [ "$m" = ii ]; then for t in i1 i2; do for c in 1 2 3 4 5; do python3 tools/gt_probes.py -w -q D${t}F_c$c 2>&1 | tail -1; done; done; exit 0; fi
if [ "$m" = w ]; then for r in "$@"; do python3 tools/gt_tran.py runs/$r 2>&1 | grep -E "^$r|W:|SN" | head -4 | cut -c1-200; done; exit 0; fi
if [ "$m" = t ]; then for t in "$@"; do for c in 1 2 3 4 5; do [ -d runs/D${t}F_c$c ] || continue; echo "D${t}F_c$c"; python3 tools/gt_tran.py runs/D${t}F_c$c 2>&1 | grep -E "FBE|paper Fig.8" | cut -c1-200; done; done; exit 0; fi
python3 tools/score2d.py -v "$@"
