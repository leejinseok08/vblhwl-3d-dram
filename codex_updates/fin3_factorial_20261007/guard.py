from pathlib import Path
import json,hashlib,subprocess,sys,datetime
B=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def quota():
 ls=subprocess.check_output(['quota','-w'],universal_newlines=True).splitlines()
 for i,l in enumerate(ls):
  if '/dev/mapper/centos-home' in l:
   t=l.split()[1:] or ls[i+1].split();used,soft,hard=[int(x.strip('*')) for x in t[:3]]
   return dict(used_KB=used,soft_KB=soft,hard_KB=hard,reserve_ok=soft-used>=512*1024)
 raise RuntimeError('Quota unreadable')
def verify(j):
 assert sha(B/'runs'/j['id']/(j['id']+'_des.cmd'))==j['deck_sha256']
 for k in ['mesh','parameter']:assert sha(Path(j[k+'_path']))==j[k+'_sha256']
 if j.get('profile_path'):assert sha(Path(j['profile_path']))==j['profile_sha256']
def check():
 m=json.loads((B/'manifest.json').read_text());q=quota();assert q['reserve_ok']
 for j in m['runs']:verify(j)
 for n,h in m['frozen_inputs'].items():assert sha(B/'snapshot'/n)==h
 return q
if __name__=='__main__':
 q=check()
 if sys.argv[1:]==['record']:
  assert json.loads((B/'checks/preflight.json').read_text())['pass_all']
  rec=dict(reviewed_at=datetime.datetime.now().astimezone().isoformat(),checks_read=744,paper_sections='III/VI, Fig2/4/5/8, originalp2/p3/p5 andp4text reviewed anew',manifest_sha256=sha(B/'manifest.json'),paper_sha256=sha(B/'PRE_RUN_CHECK.md'),preflight_sha256=sha(B/'checks/preflight.json'),quota=q)
  (B/'checks/reviewed.json').write_text(json.dumps(rec,indent=2)+'\n');print('RECORDED new paper/fin3/744checks',q)
 else:
  r=json.loads((B/'checks/reviewed.json').read_text())
  for file,key in [('manifest.json','manifest_sha256'),('PRE_RUN_CHECK.md','paper_sha256'),('checks/preflight.json','preflight_sha256')]:assert sha(B/file)==r[key]
  print('PASS fin3 run guard',q)
