from pathlib import Path
import json,sys,tarfile,hashlib
B=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
meta=Path(sys.argv[1]);dest=Path(sys.argv[2]);inv=json.loads(meta.read_text(encoding='utf-8'));pack=meta.with_suffix('.tar');assert sha(pack)==inv['pack_sha256'];dest.mkdir(parents=True,exist_ok=True)
with tarfile.open(pack) as tar:
 members=tar.getmembers();assert {m.name for m in members}=={f['relative'] for f in inv['files']}
 for m in members:
  target=(dest/m.name).resolve();assert target.is_relative_to(dest.resolve()) and m.isfile();target.parent.mkdir(parents=True,exist_ok=True)
  with tar.extractfile(m) as src,target.open('wb') as out:
   while True:
    block=src.read(1048576)
    if not block:break
    out.write(block)
for f in inv['files']:
 p=dest/f['relative'];assert p.stat().st_size==f['size'] and sha(p)==f['sha256']
receipt=dict(batch=inv['batch'],pack_sha256=inv['pack_sha256'],verified_files=len(inv['files']),local_directory=str(dest))
meta.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n');pack.unlink();print('VERIFIED',inv['batch'],len(inv['files']))
