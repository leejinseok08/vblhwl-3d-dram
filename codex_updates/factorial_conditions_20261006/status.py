from pathlib import Path
import json,datetime,subprocess
from analyze import ranking,readplt
from guard import quota
B=Path(__file__).resolve().parent;m=json.loads((B/'manifest.json').read_text());running=[]
for j in m['runs']:
 rd=B/'runs'/j['id'];p=rd/'process.json'
 if p.exists() and not (rd/'exit_code.txt').exists():
  x=json.loads(p.read_text())
  try:active=Path(f"/proc/{x['pid']}/cwd").resolve()==rd.resolve()
  except OSError:active=False
  item=dict(id=j['id'],pid=x['pid'],active=active,started_at=x['started_at'])
  try:
   data,meta=readplt(rd/('c1_'+j['id']+'_dev.plt'),live=True)
   item.update(saved_ns=meta['last_ns'],partial_output_well_formed=meta['pass'])
  except Exception as e:item['partial_output_note']=str(e)
  running.append(item)
r=ranking()
d=dict(checked_at=datetime.datetime.now().astimezone().isoformat(),planned=720,reused=len(json.loads((B/'reuse.json').read_text())),new_completed=sum((B/'runs'/j['id']/'exit_code.txt').exists() for j in m['runs']),running=running,analysed=r['analysed'],valid=r['valid'],complete_groups=len(r['ranked_common_configurations']),quota=quota())
(B/'status.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
