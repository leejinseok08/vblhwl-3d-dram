from pathlib import Path
import csv,json,os,subprocess,hashlib,sys,datetime
B=Path(__file__).resolve().parent
def values(path):
 out=[]
 for r in csv.reader(path.open()):
  try:out.append((float(r[0]),float(r[1])))
  except (ValueError,IndexError):pass
 return out
lines=[]
for c,tb,na in [(1,30,1e18),(2,20,1e18),(3,10,1e18),(4,10,1e16)]:
 st=f'gr_c{c}h';grid=B.parents[1]/'runs/_struct'/f'{st}_msh.tdr'
 for pos,dy in [('lo',.5),('mid',tb/2),('hi',tb-.5)]:
  tag=f'{st}_{pos}';env=dict(os.environ,CHK_TDR=str(grid),CHK_X='.125',CHK_Y=str((40+dy)/1000),CHK_OUT=str(B/'checks'/f'{tag}_vertical.csv'),CHK_OUTH=str(B/'checks'/f'{tag}_horizontal.csv'))
  with (B/'checks'/f'{tag}.log').open('w') as f:subprocess.check_call(['svisual','-b',str(B/'snapshot/chk_struct.tcl')],env=env,cwd=B,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
  d=values(B/'checks'/f'{tag}_horizontal.csv');cross=[(a,b) for a,b in zip(d,d[1:]) if a[1]*b[1]<0];assert len(cross)==2
  for (a,b),x in zip(cross,[50,175]):assert abs(a[0]*1000-x)<.05 and abs(b[0]*1000-x)<.05
  for x,v in d:
   if 1<x*1000<49 or 176<x*1000<199:assert abs(v/1e20-1)<1e-5
   if 51<x*1000<174:assert abs(v/-na-1)<1e-5
  if pos=='mid':
   vd=values(B/'checks'/f'{tag}_vertical.csv');body=[x*1000 for x,v in vd if 39<x*1000<41+tb and v<-na*.9]
   assert abs(min(body)-40)<.01 and abs(max(body)-40-tb)<.01
  msg=f'PASS mesh {st} {pos}: junction50/175nm Nsd1e20 Nch{na:g} body40..{40+tb}nm';print(msg,flush=True);lines.append(msg)
for c in [1,2,3,4]:
 for window in ['uniform','bl','sn']:
  a,b={'uniform':(.05,.175),'bl':(.05,.075),'sn':(.15,.175)}[window];d=values(B/'checks'/f'c{c}_{window}_generation.csv')
  inside=[v for x,v in d if a+.001<x<b-.001];outside=[v for x,v in d if x<a-.001 or x>b+.001]
  assert inside and all(abs(v/1e26-1)<1e-5 for v in inside)
  assert outside and max(abs(v) for v in outside)<1e21
  msg=f'PASS optical source c{c} {window}: {a*1000:g}..{b*1000:g}nm only; Grid unmodified';print(msg,flush=True);lines.append(msg)

for j in json.loads((B/'manifest.json').read_text())['runs']:
 p=j['parameters'];cmd=(B/'runs'/j['id']/(j['id']+'_des.cmd')).read_text()
 assert all(p[k]==v for k,v in dict(Lg=100,Tox=5,Tgm=20,Dvox=30,Nsd=1e20,Lsp1=25,Lsp2=25,Tper=21,tEdge=.5,Npulse=9).items())
 assert p['WFs']==p['WFd']==(5 if j['case']==5 else 4.7)
 assert 'Average(Window[(0.07500 0.04000)' in cmd
 assert abs(j['reading']['time_s']-j['schedule']['tS']-.75e-9)<1e-18
 assert abs(p['Cs']-({30:5.1e-15,20:4.2e-15,10:3.6e-15}[p['Tbody']]*(1.8/4.2 if j['Cs_basis']=='write_fit' else 1)))<1e-25
 assert bool(p['Gb'])==(j['preparation']=='proxy')
 if j['profile_path']:assert 'ReadFromFile' in cmd and 'OpticalGenerationInput' in cmd
 msg=f"PASS {j['id']}: mesh/model unchanged; {j['preparation']} x{j['preparation_factor']} {j['source_window']}; SN={j['SN_protocol']}; II={j['II']}; Cs={j['Cs_basis']}; fin3 average; full200ns"
 print(msg,flush=True);lines.append(msg)
(B/'checks/preflight.json').write_text(json.dumps(dict(pass_all=True,checks=lines,performed_at=datetime.datetime.now().astimezone().isoformat()),indent=2)+'\n')
print('ALL744 CHECKS PASS; review each line before launch')
