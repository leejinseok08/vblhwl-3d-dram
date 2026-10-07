from pathlib import Path
import json,subprocess,fcntl,concurrent.futures,gzip,hashlib,time,os,signal,datetime
from guard import check,quota,verify
from analyze_fin3 import save
B=Path(__file__).resolve().parent;lk=(B/'queue.lock').open('w');fcntl.flock(lk,fcntl.LOCK_EX|fcntl.LOCK_NB)
def emit(t):print(datetime.datetime.now().astimezone().isoformat(),t,flush=True)
def run(j):
 rd=B/'runs'/j['id']
 if j.get('reuse_from'):
  ref=j['reuse_from'];src=Path(ref['directory']);f=src/(ref['id']+'_sys.plt')
  while not (f.exists() or Path(str(f)+'.gz').exists()) or (ref['kind']=='fin3_own_generation_live' and not (src/'exit_code.txt').exists()):time.sleep(30)
  o=save(j);emit('REFERENCE '+j['id']+' valid='+str(o['success']));return
 if (rd/'exit_code.txt').exists():return
 while not quota()['reserve_ok']:emit('DEFER quota '+j['id']);time.sleep(30)
 subprocess.check_call(['python3',str(B/'guard.py')],stdout=subprocess.DEVNULL);verify(j)
 lock=(rd/'process.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 p=subprocess.Popen(['sdevice',j['id']+'_des.cmd'],cwd=rd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
 (rd/'process.json').write_text(json.dumps(dict(pid=p.pid,started_at=datetime.datetime.now().astimezone().isoformat()))+'\n');emit('START '+j['id'])
 def consume():
  with gzip.open(rd/(j['id']+'.stdout.gz'),'wb') as g:
   while True:
    v=p.stdout.read(65536)
    if not v:break
    g.write(v)
 with concurrent.futures.ThreadPoolExecutor(max_workers=1) as reader:
  f=reader.submit(consume)
  try:rc=p.wait(timeout=6*3600)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   rc=124
  f.result()
 o={}
 (rd/'exit_code.txt').write_text(str(rc)+'\n')
 if rc==0:o=save(j)
 else:
  o=dict(id=j['id'],success=False,exit_code=rc);(B/'results'/(j['id']+'.json')).write_text(json.dumps(o)+'\n')
 for q in rd.iterdir():
  if q.suffix not in ('.tdr','.plt','.log'):continue
  h=hashlib.sha256(q.read_bytes()).digest()
  with q.open('rb') as f,gzip.open(str(q)+'.gz','wb') as g:
   while True:
    v=f.read(65536)
    if not v:break
    g.write(v)
  with gzip.open(str(q)+'.gz','rb') as g:assert hashlib.sha256(g.read()).digest()==h
  assert q.parent==rd;q.unlink()
 (rd/'finished.json').write_text(json.dumps(dict(exit_code=rc,finished_at=datetime.datetime.now().astimezone().isoformat()))+'\n')
 emit('END '+j['id']+' rc='+str(rc)+' valid='+str(o.get('success')))
check()
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 fs=[pool.submit(run,j) for j in json.loads((B/'manifest.json').read_text())['runs']]
 for f in concurrent.futures.as_completed(fs):
  try:f.result()
  except Exception as e:emit('ERROR '+repr(e))
(B/'queue_complete.json').write_text(json.dumps(dict(completed_at=datetime.datetime.now().astimezone().isoformat()))+'\n')
emit('QUEUE COMPLETE; fin3 initial history remains a diagnostic')
