from pathlib import Path
import subprocess,json,hashlib
B=Path(__file__).resolve().parent
R=B.parent/'github_repository/vblhwl-3d-dram'
git=['git','-c','safe.directory='+R.as_posix()]
paths=subprocess.check_output(git+['ls-tree','-r','--name-only','-z','origin/claude','claude/data/runs'],cwd=R).decode().split('\0')
items=[]
for c in range(1,6):
 for p in paths:
  if '/Ds2F_c'+str(c)+'/' not in p:continue
  raw=subprocess.check_output(git+['show','origin/claude:'+p],cwd=R)
  q=B/'baseline'/Path(p).parent.name/Path(p).name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
  items.append(dict(source=p,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
assert len(items)==20
(B/'baseline_inventory.json').write_text(json.dumps(dict(claude_commit='5e6deb4',baseline='fin3',FBE='Ds2F_c1..5',files=items),indent=2)+'\n',encoding='utf-8')
print('Imported fin3 baseline without rerunning:',len(items),'files')
