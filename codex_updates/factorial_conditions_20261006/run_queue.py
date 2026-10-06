from pathlib import Path
import subprocess,fcntl,concurrent.futures,json,gzip,time,os,signal,hashlib,datetime
from guard import quota,verify
from analyze import save,ranking
B=Path(__file__).resolve().parent;lock=(B/'queue.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
M=json.loads((B/'manifest.json').read_text());reused={x['id'] for x in json.loads((B/'reuse.json').read_text())}
def emit(s):print(datetime.datetime.now().astimezone().isoformat(),s,flush=True)
def compress(path):
 if not path.exists():return
 h=hashlib.sha256(path.read_bytes()).digest();dest=Path(str(path)+'.gz')
 with path.open('rb') as f,gzip.open(dest,'wb') as g:
  while True:
   t=f.read(65536)
   if not t:break
   g.write(t)
 with gzip.open(dest,'rb') as g:assert hashlib.sha256(g.read()).digest()==h
 assert str(path.resolve()).startswith(str((B/'runs').resolve())+'/');path.unlink()
def run(j):
 rid=j['id'];rd=B/'runs'/rid
 if rid in reused:return rid,'reused'
 if (rd/'exit_code.txt').exists():return rid,'already executed'
 while not quota()['reserve_ok']:
  emit('DEFER quota '+rid);time.sleep(30)
 subprocess.check_call(['python3',str(B/'guard.py'),rid],stdout=subprocess.DEVNULL)
 lk=(rd/'process.lock').open('w');fcntl.flock(lk,fcntl.LOCK_EX|fcntl.LOCK_NB)
 emit('START '+rid)
 # Use a pipe and gzip from the start; no uncompressed duplicate stdout file.
 p=subprocess.Popen(['sdevice',rid+'_des.cmd'],cwd=rd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
 (rd/'process.json').write_text(json.dumps(dict(pid=p.pid,started_at=datetime.datetime.now().astimezone().isoformat()))+'\n')
 # Reader runs separately so a wall-time timeout can terminate only this new process group.
 def consume():
  with gzip.open(rd/(rid+'.stdout.gz'),'wb') as g:
   while True:
    t=p.stdout.read(65536)
    if not t:break
    g.write(t)
 with concurrent.futures.ThreadPoolExecutor(max_workers=1) as reader:
  f=reader.submit(consume)
  try:rc=p.wait(timeout=6*3600)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   rc=124
  f.result()
 (rd/'exit_code.txt').write_text(str(rc)+'\n')
 o=save(j) if rc==0 else dict(id=rid,group=j['group'],case=j['case'],success=False,exit_code=rc,error='simulation failure or6h screening timeout')
 if rc:(B/'results'/(rid+'.json')).write_text(json.dumps(o,indent=2)+'\n')
 for path in rd.iterdir():
  if path.suffix in ('.plt','.tdr','.log'):compress(path)
 emit('END '+rid+' rc='+str(rc)+' valid='+str(o.get('success')))
 return rid,rc
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 fs=[pool.submit(run,j) for j in M['runs']]
 for i,f in enumerate(concurrent.futures.as_completed(fs),1):
  try:r=f.result()
  except Exception as e:emit('ERROR '+repr(e));r=('error',repr(e))
  if i%5==0:ranking();emit('PROGRESS '+str(i)+'/720')
ranking();emit('SCREEN COMPLETE; shortlist is not final reproduction')
(B/'queue_complete.json').write_text(json.dumps(dict(finished_at=datetime.datetime.now().astimezone().isoformat()))+'\n')
