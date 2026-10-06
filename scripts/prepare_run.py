"""Prepare a portable replay deck; never launch a solver or contact a server."""
from pathlib import Path
import sys,json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
batch=(ROOT/sys.argv[1]).resolve();assert batch.is_relative_to(ROOT)
rid=sys.argv[2];m=json.loads((batch/'manifest.json').read_text(encoding='utf-8'));j=next(x for x in m['runs'] if x['id']==rid)
deck=batch/'runs'/rid/(rid+'_des.cmd')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(deck)==j['deck_sha256']
mesh=ROOT/'device_meshes'/(j['structure']+'_msh.tdr');assert sha(mesh)==j['mesh_sha256']
dest=ROOT/'_replay'/batch.name/rid;dest.mkdir(parents=True,exist_ok=False)
text=deck.read_text(encoding='utf-8')
def path_replace(match):
    key,name=match.group(1),Path(match.group(2)).name
    target=mesh if key=='Grid' else batch/'snapshot'/name if key=='Parameter' else batch/'profiles'/name
    assert target.is_file(),target
    return key+' = "'+target.as_posix()+'"'
text,n=re.subn(r'(Grid|Parameter|OpticalGenerationInput)\s*=\s*"([^"]+)"',path_replace,text)
assert n>=2
out=dest/deck.name;out.write_text(text,encoding='utf-8',newline='\n')
(dest/'replay_provenance.json').write_text(json.dumps({'source_deck_sha256':sha(deck),'prepared_deck_sha256':sha(out),
 'only_change':'file paths Grid/Parameter/OpticalGenerationInput; paper and actual mesh review still required before execution'},indent=2)+'\n')
print('Prepared',out,'; simulation NOT started')
