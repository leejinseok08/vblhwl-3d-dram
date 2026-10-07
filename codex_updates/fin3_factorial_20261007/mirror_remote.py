from pathlib import Path
import json,sys,tarfile,hashlib,os,fcntl,subprocess
B=Path(__file__).resolve().parent;M=B/'mirror';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lock=(M/'export.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX)
manifest=json.loads((B/'manifest.json').read_text());ids={j['id'] for j in manifest['runs'] if not j['reuse_from']}
if sys.argv[1]=='export':
 subprocess.check_call(['python3',str(B/'rank.py')],stdout=subprocess.DEVNULL)
 pending=M/'pending.json'
 if pending.exists():print(pending.read_text());sys.exit()
 files=[];jobs=[]
 for rid in sorted(ids):
  rd=B/'runs'/rid
  if not (rd/'finished.json').exists() or (M/(rid+'.receipt.json')).exists():continue
  if not (B/'results'/(rid+'.json')).exists():continue
  jobs.append(rid)
  for p in rd.iterdir():
   if p.is_file() and (p.name.endswith(('.plt.gz','.tdr.gz','.log.gz','.stdout.gz'))):files.append(dict(relative=str(p.relative_to(B)),size=p.stat().st_size,sha256=sha(p)))
  if len(jobs)==4:break
 if not jobs:print(json.dumps(dict(empty=True,queue_complete=(B/'queue_complete.json').exists())));sys.exit()
 batch='batch_'+jobs[0]+'_'+jobs[-1];pack=M/(batch+'.tar');tmp=pack.with_suffix('.tmp')
 with tarfile.open(tmp,'w') as tar:
  for f in files:tar.add(str(B/f['relative']),arcname=f['relative'],recursive=False)
 tmp.replace(pack)
 inventory=dict(batch=batch,jobs=jobs,files=files,pack_path=str(pack),pack_sha256=sha(pack))
 (M/(batch+'.json')).write_text(json.dumps(inventory,indent=2)+'\n');pending.write_text(json.dumps(inventory)+'\n');print(json.dumps(inventory))
elif sys.argv[1]=='retire':
 p=M/'pending.json';inv=json.loads(p.read_text());receipt=json.loads((M/'receipt.json').read_text());assert receipt['batch']==inv['batch'] and receipt['pack_sha256']==inv['pack_sha256'] and receipt['verified_files']==len(inv['files'])
 for f in inv['files']:
  q=B/f['relative'];assert q.resolve().parent.parent==B/'runs' and q.parent.name in ids
  assert (q.parent/'finished.json').exists() and q.stat().st_size==f['size'] and sha(q)==f['sha256']
 for rid in inv['jobs']:(M/(rid+'.receipt.json')).write_text(json.dumps(receipt)+'\n')
 for f in inv['files']:(B/f['relative']).unlink()
 Path(inv['pack_path']).unlink();p.unlink();print('RETIRED verified local mirror '+inv['batch'])
