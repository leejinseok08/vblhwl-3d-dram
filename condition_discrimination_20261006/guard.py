from pathlib import Path
import json,hashlib,sys
r=Path(__file__).resolve().parent; m=json.loads((r/'manifest.json').read_text())
assert json.loads((r/'checks'/'mesh_pass.json').read_text())['pass']
assert (r/'checks'/'reviewed.json').is_file(),'paper/mesh review missing'
review=json.loads((r/'checks'/'reviewed.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert review['manifest_sha256']==sha(r/'manifest.json')
rid=sys.argv[1]; job=next(j for j in m['runs'] if j['id']==rid)
assert sha(r/'runs'/rid/(rid+'_des.cmd'))==job['deck_sha256']
assert sha(Path('/home/e20241515/vblhwl_3d_dram/runs/_struct')/(job['structure']+'_msh.tdr'))==job['mesh_sha256']
for n,h in m['snapshot_sha256'].items(): assert sha(r/'snapshot'/n)==h,n
print('PASS pre-run guard:',rid,'paper review + geometry cutlines + unchanged mesh/deck/parameter hashes')
