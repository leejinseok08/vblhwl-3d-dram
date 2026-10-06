#!/bin/bash
# _q.sh - scratch query script (overwritten for each one-off question that needs quotes; see CLAUDE.md, server section)
# usage: bash tools/_q.sh <mode> [seconds to wait first] [arguments]
#   r3d = rebuild the two 3D structures from today's structure files (old meshes moved aside) and run the 3D checks + top views
#   st = state of every run of rounds 4-6 (tools/run_state.py) | sa = one line per run that is not complete | live | du = disk | cx = Codex's plot files
#   rh <runs> = row-hammer table | s <tags> = scorecard | t <tags> = loss after every BL-low phase | wo <tags> = write and WL switch-off
#   ii = the impact-ionization factor runs | w <runs> = write curves
cd ~/vblhwl_3d_dram
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
B=$(cd runs; ls run_d4.sh run_d4y.sh run_d4r.sh run_d5.sh run_d6.sh 2>/dev/null)
if [ "$m" = start6 ]; then bash tools/gt_start.sh run_d6.sh "$@"; m=st; fi
if [ "$m" = sa ]; then python3 tools/run_state.py -a $B | grep -E 'running|DAMAGED|no output|stopped' | sort -u; exit 0; fi
date +%H:%M; python3 tools/run_state.py $B | cut -c1-900; bash tools/_q.sh live; echo "disk quota: $(quota -s | tail -1 | awk '{print $1, "of", $2}'), $(uptime | sed 's/.*load/load/')"
[ "$m" = st ] && exit 0
if [ "$m" = pf ]; then for r in "$@"; do python3 tools/run_state.py -f runs/$r/*.plt | sed 's|runs/[^/]*/||'; done; exit 0; fi    # every plot file of the named runs
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
