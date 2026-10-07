"""KST midnight to 07:00 resource-aware supplemental workers, no new conditions."""
from pathlib import Path
import json,datetime,hashlib,os,time,fcntl,subprocess,concurrent.futures,threading,gzip,signal
from guard import check,quota,verify
from analyze_fin3 import save
B=Path(__file__).resolve().parent;KST=datetime.timezone(datetime.timedelta(hours=9))
allocation=threading.Lock();stop=threading.Event();m=json.loads((B/'manifest.json').read_text());jobs=[j for j in m['runs'] if not j['reuse_from']]
def emit(s):print(datetime.datetime.now(KST).isoformat(),s,flush=True)
def resources():
 current=datetime.datetime.now(KST);all_sd=[];own=[];night_active=0
 controller_pid=int((B/'night.pid').read_text()) if (B/'night.pid').exists() else os.getpid()
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   cmd=(p/'cmdline').read_bytes().split(b'\0')
   if not cmd or cmd[0].split(b'/')[-1]!=b'sdevice':continue
   cwd=(p/'cwd').resolve();all_sd.append(int(p.name))
   if B/'runs' in cwd.parents:
    own.append(int(p.name))
    parent=next(int(l.split()[1]) for l in (p/'status').read_text().splitlines() if l.startswith('PPid:'))
    if parent==controller_pid:night_active+=1
  except (OSError,RuntimeError):continue
 cores=len(os.sched_getaffinity(0));other=len(all_sd)-len(own);load=float(Path('/proc/loadavg').read_text().split()[0]);mem={l.split(':')[0]:int(l.split()[1]) for l in Path('/proc/meminfo').read_text().splitlines()}
 # Four requested threads per sdevice; reserve sixteen logical CPUs for other work.
 extra_non_device=max(0,load-4*len(all_sd));cap=max(0,min(28,int((cores-16-4*other-extra_non_device)//4)))
 q=quota();safe=load<cores*.875 and mem['MemAvailable']>32*1024*1024 and q['reserve_ok']
 return dict(checked_at=current.isoformat(),night=0<=current.hour<7,available_cpus=cores,other_sdevice=other,own_active=len(own),night_active=night_active,total_cap=cap,night_cap=max(0,cap-16),load1min=load,available_memory_KB=mem['MemAvailable'],quota=q,safe=safe,launch_allowed=0<=current.hour<7 and safe and len(own)<cap and night_active<max(0,cap-16))
def work(j,claim):
 rd=B/'runs'/j['id'];p=None
 try:
  with allocation:
   subprocess.check_call(['python3',str(B/'guard.py')],stdout=subprocess.DEVNULL);verify(j)
   state=resources()
   if not state['launch_allowed']:return
   if (rd/'process.json').exists() or (rd/'exit_code.txt').exists():return
   p=subprocess.Popen(['sdevice',j['id']+'_des.cmd'],cwd=rd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
   (rd/'process.json').write_text(json.dumps(dict(pid=p.pid,started_at=datetime.datetime.now(KST).isoformat(),launcher='night_queue'))+'\n');emit('START '+j['id']+' total_before='+str(state['own_active'])+' cap='+str(state['total_cap']))
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
  (rd/'exit_code.txt').write_text(str(rc)+'\n')
  if rc==0:o=save(j)
  else:
   o=dict(id=j['id'],case=j['case'],success=False,exit_code=rc,launcher='night_queue');(B/'results'/(j['id']+'.json')).write_text(json.dumps(o)+'\n');stop.set();emit('STOP further night starts after nonzero exit; existing jobs preserved')
  for q in rd.iterdir():
   if q.suffix not in ['.tdr','.plt','.log']:continue
   digest=hashlib.sha256(q.read_bytes()).digest()
   with q.open('rb') as src,gzip.open(str(q)+'.gz','wb') as dst:
    while True:
     v=src.read(65536)
     if not v:break
     dst.write(v)
   with gzip.open(str(q)+'.gz','rb') as g:assert hashlib.sha256(g.read()).digest()==digest
   assert q.parent==rd;q.unlink()
  (rd/'finished.json').write_text(json.dumps(dict(exit_code=rc,finished_at=datetime.datetime.now(KST).isoformat(),launcher='night_queue'))+'\n');emit('END '+j['id']+' rc='+str(rc)+' valid='+str(o.get('success')))
 except Exception as e:emit('ERROR '+j['id']+' '+repr(e));stop.set()
 finally:claim.close()
def all_finished():return all((B/'results'/(j['id']+'.json')).exists() and (j['reuse_from'] or (B/'runs'/j['id']/'finished.json').exists()) for j in m['runs'])
if __name__=='__main__':
 import sys
 if sys.argv[1:]==['check']:
  print(json.dumps(resources(),indent=2));raise SystemExit()
 lock=(B/'night_queue.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 check();emit('NIGHT CONTROLLER READY; KST00:00-07:00; max12 extra on top of16; total<=28 subject to other load')
 policy=dict(configured_at=datetime.datetime.now(KST).isoformat(),timezone='Asia/Seoul',window='00:00 inclusive to07:00 exclusive',daytime_workers=16,night_max_total=28,night_supplemental_max=12,reserve_logical_cpus=16,threads_per_job=4,mem_reserve_GiB=32,quota_reserve_MiB=512,input_sha256=hashlib.sha256((B/'manifest.json').read_bytes()).hexdigest(),unchanged_conditions=True,at_0700='Stop new night launches; let active simulations finish',on_nonzero_exit='Stop further night launches; keep active jobs',completion='All720 result files plus raw-output finished markers, then exit')
 (B/'night_policy.json').write_text(json.dumps(policy,indent=2)+'\n')
 with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
  running=[]
  while not all_finished() and not stop.is_set():
   running=[f for f in running if not f.done()];state=resources();state['night_workers_active_or_claimed']=len(running);(B/'night_status.json').write_text(json.dumps(state,indent=2)+'\n')
   if state['launch_allowed'] and len(running)<12:
    pending=[j for j in jobs if not (B/'runs'/j['id']/'process.json').exists() and not (B/'runs'/j['id']/'exit_code.txt').exists()]
    # Prefer the middle of the remaining input list to avoid the two other queues' ends.
    middle=len(pending)//2;ordered=pending[middle:]+list(reversed(pending[:middle]))
    for j in ordered:
     if len(running)>=12 or not resources()['launch_allowed']:break
     claim=(B/'runs'/j['id']/'process.lock').open('a')
     try:fcntl.flock(claim,fcntl.LOCK_EX|fcntl.LOCK_NB)
     except BlockingIOError:claim.close();continue
     running.append(pool.submit(work,j,claim));time.sleep(.5)
   time.sleep(30)
 emit('NIGHT CONTROLLER EXIT; complete='+str(all_finished())+' halted='+str(stop.is_set()))
