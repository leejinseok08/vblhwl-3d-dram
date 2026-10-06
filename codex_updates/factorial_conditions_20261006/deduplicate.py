from pathlib import Path
import json,hashlib,sys
from analyze import read,save
B=Path(__file__).resolve().parent;ROOT=B.parents[1];m=json.loads((B/'manifest.json').read_text())
sys.path.insert(0,str(B/'snapshot'));from params import P as DEFAULT
keys=['WFs','WFd','Vdd','Vpp','Vwr','tWr','tWf','Temp','Bgn','GR','SRHon','SRHdd','TAT','BTBT','II','IIdf','BLhv','Dit','QC','ThinL','Mob','Rwl','Rbl','Pair','Nch','Tbody','Wact','Lg','Tox','Tgm','Dvox','Nsd','Gdi','Spm','Lsp1','Lsp2','Wbl','Dhox','Bgc']
old=[]
for path in (ROOT/'runs').glob('*/run.json'):
 try:
  x=json.loads(path.read_text());p=dict(DEFAULT);p.update(x['params']);s=x['sched'];rid=path.parent.name
  if x.get('deck')!='cho:FBE' and s.get('test')!='FBE':continue
  if p['Gb']>0:mode='clamped'
  else:mode='early'
  par=ROOT/p['Par'];h=hashlib.sha256(par.read_bytes()).hexdigest()
  old.append((path.parent,rid,x['struct'],p,s,mode,h))
 except (KeyError,OSError,ValueError):pass
# Latest NG runs have complete body source observations, preferred over old coarse data.
rec=ROOT/'codex_validation/recovery_round11_20261006'
for j in json.loads((rec/'manifest.json').read_text())['runs']:
 if j['id'].startswith('NG_'):old.insert(0,(rec/'runs'/j['id'],j['id'],j['structure'],j['parameters'],j['schedule'],'early',j['parameter_sha256']))
reuse=[]
for j in m['runs']:
 matched=False
 if j['source_window'] not in (None,'uniform'):continue
 p=j['parameters']
 for rd,rid,st,op,s,mode,ph in old:
  if st!=j['structure'] or mode!=j['SN_protocol'] or ph!=j['parameter_sha256']:continue
  if any(p.get(k)!=op.get(k) for k in keys):continue
  if abs(p['Cs']/op['Cs']-1)>1e-9 or abs(p['tHold']-op['tHold'])>1e-5:continue
  if abs(p['Gb']-op['Gb'])>max(1,p['Gb']*1e-9):continue
  if op['Tper']<21 or s['tEnd']<j['schedule']['tEnd']:continue
  o=save(j,rd,rid,reused=True)
  if o['success']:
   reuse.append({'id':j['id'],'source':str(rd),'source_run':rid,'reason':'Same device/coefficients/pulse prefix/SN clamp/history; reanalysed intact stored first10.5ns'});matched=True;break
 if not matched:
  result=B/'results'/(j['id']+'.json')
  if result.exists():result.unlink()
(B/'reuse.json').write_text(json.dumps(reuse,indent=2)+'\n')
print('EXISTING COMPLETE CONDITIONS REUSED',len(reuse),'new pending',720-len(reuse))
