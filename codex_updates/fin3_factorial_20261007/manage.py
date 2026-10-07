from pathlib import Path
import json,sys,os,signal,time,datetime,collections,subprocess
B=Path(__file__).resolve().parent;OLD=B.parent/'factorial_conditions_20261006';NAT=B.parent/'fin3_update_20261007'
sys.path.insert(0,str(B.parent))
from audit_recovery_round11 import readplt
def processes(root):
 out=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   cwd=(p/'cwd').resolve();cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
  except (OSError,RuntimeError):continue
  if cwd==root or root in cwd.parents:
   row=dict(pid=int(p.name),cwd=str(cwd),cmd=cmd)
   if cmd and Path(cmd.split()[0]).name=='sdevice':
    try:
     _,reading=readplt(cwd/(cwd.name+'_sys.plt'),live=True);row['last_time_ns']=reading['last_ns']
    except Exception as e:row['reading_error']=str(e)
   out.append(row)
 return out
def status():
 m=json.loads((B/'manifest.json').read_text());rows=[]
 for j in m['runs']:
  f=B/'results'/(j['id']+'.json')
  if f.exists():rows.append(json.loads(f.read_text()))
 out=dict(checked_at=datetime.datetime.now().astimezone().isoformat(),total=720,new_solver_planned=710,references_planned=10,results=len(rows),valid=sum(r.get('success',False) for r in rows),invalid=[r for r in rows if not r.get('success')],active=[p for p in processes(B) if Path(p['cmd'].split()[0]).name=='sdevice'],natural_active=[p for p in processes(NAT) if Path(p['cmd'].split()[0]).name=='sdevice'],old_active=[p for p in processes(OLD) if Path(p['cmd'].split()[0]).name=='sdevice'],quota=subprocess.check_output(['quota','-w'],universal_newlines=True),queue_log=(B/'queue.log').read_text()[-5000:] if (B/'queue.log').exists() else '')
 (B/'status.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return out
if sys.argv[1]=='status':status()
elif sys.argv[1]=='launch':
 subprocess.check_call(['python3',str(B/'guard.py')]);log=(B/'queue.log').open('a')
 p=subprocess.Popen(['python3','-u',str(B/'run_queue.py')],cwd=B,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);(B/'queue.pid').write_text(str(p.pid)+'\n');print('LAUNCHED',p.pid)
elif sys.argv[1]=='stop_old':
 s=status();assert s['active'] and s['valid']>=5,'New batch not verified running'
 pid=int((OLD/'queue.pid').read_text());ps=processes(OLD);parent=next(p for p in ps if p['pid']==pid);assert 'run_queue.py' in parent['cmd'] and parent['cwd']==str(OLD)
 record=dict(stopped_at=datetime.datetime.now().astimezone().isoformat(),reason='User requested fin3 replacement; old720 excluded from ranking',superseded_by=str(B),old_queue=parent,before=ps,old_results_count=len(list((OLD/'results').glob('*.json'))),raw_data_retained=True)
 os.kill(pid,signal.SIGSTOP)
 targets=[p for p in processes(OLD) if Path(p['cmd'].split()[0]).name=='sdevice' and str(OLD/'runs')+'/' in p['cwd']]
 for p in targets:
  assert os.getpgid(p['pid'])==p['pid'];os.killpg(p['pid'],signal.SIGTERM)
 os.kill(pid,signal.SIGKILL);time.sleep(3)
 for p in processes(OLD):
  if Path(p['cmd'].split()[0]).name=='sdevice':
   assert os.getpgid(p['pid'])==p['pid'];os.killpg(p['pid'],signal.SIGKILL)
 record['after']=processes(OLD);assert not any(Path(p['cmd'].split()[0]).name=='sdevice' for p in record['after'])
 (OLD/'OBSOLETE.json').write_text(json.dumps(record,indent=2)+'\n');(B/'old720_discarded.json').write_text(json.dumps(record,indent=2)+'\n');print('OLD720 STOPPED AND EXCLUDED; raw audit retained');status()
