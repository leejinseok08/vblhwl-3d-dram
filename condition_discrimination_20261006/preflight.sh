#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p checks
python3 - <<'PY'
import json,hashlib,pathlib
r=pathlib.Path.cwd(); m=json.loads((r/'manifest.json').read_text())
for st,h in m['meshes'].items():
 p=pathlib.Path('/home/e20241515/vblhwl_3d_dram/runs/_struct')/(st+'_msh.tdr')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h,st+' mesh changed'
 print('PASS mesh SHA256',st,h)
for n,h in m['snapshot_sha256'].items():
 assert hashlib.sha256((r/'snapshot'/n).read_bytes()).hexdigest()==h,n
print('PASS frozen input snapshots')
PY
for spec in gr_c1h:30:1 gr_c2h:20:1 gr_zz:20:2; do
 IFS=: read -r st tb nl <<< "$spec"
 for ((layer=0;layer<nl;layer++)); do
  for pos in lo mid hi; do
   y=$(python3 -c "print(($layer*(80+$tb)+40+{'lo':0.5,'mid':$tb/2,'hi':$tb-0.5}['$pos'])/1000)")
   tag=${st}_L${layer}_${pos}
   CHK_TDR=/home/e20241515/vblhwl_3d_dram/runs/_struct/${st}_msh.tdr CHK_X=0.125 CHK_Y=$y \
   CHK_OUT=$PWD/checks/${tag}_vertical.csv CHK_OUTH=$PWD/checks/${tag}_horizontal.csv \
   svisual -b snapshot/chk_struct.tcl < /dev/null > checks/${tag}.log 2>&1
  done
 done
done
python3 verify_mesh.py | tee checks/mesh_verdict.txt
