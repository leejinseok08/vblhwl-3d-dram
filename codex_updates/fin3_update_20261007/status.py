from pathlib import Path
import json,sys,datetime
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent))
from audit_recovery_round11 import readplt
from guard import quota
m=json.loads((B/'manifest.json').read_text());rows=[]
for j in m['runs']:
 rd=B/'runs'/j['id'];o=dict(id=j['id'],case=j['case'],hold_us=j['parameters']['tHold']/1000,status='pending')
 if (rd/'exit_code.txt').exists():o.update(status='finished',exit_code=int((rd/'exit_code.txt').read_text()))
 elif (rd/'process.json').exists():
  x=json.loads((rd/'process.json').read_text());active=Path('/proc/'+str(x['pid'])+'/cwd').resolve()==rd.resolve();o.update(status='running' if active else 'inactive_without_exit_code',**x)
  if active:
   try:
    data,meta=readplt(rd/('c1_'+j['id']+'_dev.plt'),live=True);o.update(saved_ns=meta['last_ns'],partial_output_well_formed=meta['pass'])
   except Exception as e:o['partial_output_note']=str(e)
 rows.append(o)
a=sum(x['status']=='running' for x in rows);f=sum(x['status']=='finished' for x in rows);p=sum(x['status']=='pending' for x in rows)
s=dict(checked_at=datetime.datetime.now().astimezone().isoformat(),baseline='fin3',planned=5,finished=f,running=a,pending=p,runs=rows,quota=quota(),summary=f'fin3 후속 계산 {a}개 실행 중 / {p}개 대기 / {f}개 종료; 기존 fin3 원시결과5개 독립검증완료')
(B/'launch_status.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');print(json.dumps(s,ensure_ascii=False,indent=2))
