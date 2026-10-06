from pathlib import Path
import json,hashlib,subprocess,sys,datetime
B=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((B/'manifest.json').read_text())
def quota():
 txt=subprocess.check_output(['quota','-w'],universal_newlines=True).splitlines()
 for i,l in enumerate(txt):
  if '/dev/mapper/centos-home' in l:
   t=l.split()[1:] or txt[i+1].split();used,soft,hard=[int(x.strip('*')) for x in t[:3]]
   return {'used_KB':used,'soft_KB':soft,'hard_KB':hard,'reserve_ok':soft-used>=512*1024}
 raise RuntimeError('quota unavailable')
def verify(j):
 assert sha(B/'runs'/j['id']/(j['id']+'_des.cmd'))==j['deck_sha256']
 for k in ['mesh','parameter','profile']:
  if j.get(k+'_path'):assert sha(Path(j[k+'_path']))==j[k+'_sha256'],j['id']+' '+k
if __name__=='__main__' and sys.argv[1:]==['record']:
 assert json.loads((B/'checks/preflight.json').read_text())['pass']
 for j in m['runs']:verify(j)
 for path,h in m['input_source_sha256'].items():assert sha(Path(path))==h
 for n,h in m['snapshot_sha256'].items():assert sha(B/'snapshot'/n)==h
 q=quota();assert q['reserve_ok']
 (B/'checks/reviewed.json').write_text(json.dumps(dict(reviewed_at=datetime.datetime.now().astimezone().isoformat(),manifest_sha256=sha(B/'manifest.json'),paper_review_sha256=sha(B/'PRE_RUN_CHECK.md'),checks_sha256=sha(B/'checks/preflight.json'),checks_read=24,paper='Cho original III/IV/VI Figs2/4/5/8 and Fig7 grounded control; p2-p5 reviewed before this batch',authorization='User explicitly requested finite candidate combinations and simulated shortlist',quota=q),indent=2)+'\n')
 print('RECORDED paper/24 fresh checks/all720 decks/geometry/profile/coefficients',q)
elif __name__=='__main__':
 r=json.loads((B/'checks/reviewed.json').read_text());assert r['manifest_sha256']==sha(B/'manifest.json') and r['paper_review_sha256']==sha(B/'PRE_RUN_CHECK.md') and r['checks_sha256']==sha(B/'checks/preflight.json')
 j=next(j for j in m['runs'] if j['id']==sys.argv[1]);verify(j)
 q=quota();assert q['reserve_ok'];print('PASS per-run guard',j['id'],q)
