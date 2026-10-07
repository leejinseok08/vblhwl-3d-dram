from pathlib import Path
import sys,shutil,json,hashlib,itertools,re,csv
B=Path(__file__).resolve().parent;ROOT=B.parents[1];REF=B.parent/'fin3_update_20261007';OLD=B.parent/'factorial_conditions_20261006'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['snapshot','profiles','checks','runs','results','mirror']:(B/n).mkdir(exist_ok=True)
if sys.argv[1:]==['bootstrap']:
 for n in ['make_runs.py','params.py','sdevice_cal_a1.7e21_b2.25e07.par','chk_struct.tcl']:shutil.copy2(REF/'snapshot'/n,B/'snapshot'/n)
 shutil.copytree(REF/'baseline',B/'baseline',dirs_exist_ok=True)
 shutil.copytree(OLD/'profiles',B/'profiles',dirs_exist_ok=True)
 shutil.copy2(OLD/'verify_profiles.tcl',B/'verify_profiles.tcl')
 print('Frozen fin3 sources and source-only optical profiles; no legacy results imported');sys.exit()
sys.path.insert(0,str(B/'snapshot'));import make_runs as mk
from params import P as DEF
assert mk.GBB=={1:1.56,2:1.31,3:1.19,4:1.17,5:1.18}
PAR=B/'snapshot/sdevice_cal_a1.7e21_b2.25e07.par';H={1:20600,2:16200,3:19600,4:18700,5:14600}
preps=[('natural',None,q) for q in [.8,1,1.2]]+ [('proxy',w,q) for w in ['uniform','bl','sn'] for q in [.8,1,1.2]]
jobs=[];references=[]
for group,(pr,mode,ii,cm) in enumerate(itertools.product(preps,['clamped','early','late_reset'],[1,0],['write_fit','text']),1):
 kind,where,q=pr
 for c,st,w,tb in mk.CASES:
  rid=f'F3C{group:03d}_c{c}';base=json.loads((B/'baseline'/f'Ds2F_c{c}'/'run.json').read_text())['params']
  p=dict(DEF);p.update(base);p.update(Gb=mk.GBQ[c]*mk.GBB[c]*q if kind=='proxy' else 0,SNhold=int(mode=='clamped'),tHold=H[c]*q if kind=='natural' else 21,II=ii,Cs=mk.CSB[tb]*(1.8/4.2 if cm=='write_fit' else 1),ProbeX=1,ProbeT=1,Nthr=4,Npulse=9,Tper=21,tEdge=.5,Par=PAR.name)
  raw,sched,waves,S=mk.deck_cho(rid,p,st,'FBE');ts=sched['tS'];end=sched['tEnd'];head=raw.split('Solve {',1)[0]
  grid=ROOT/'runs/_struct'/f'{st}_msh.tdr';head=head.replace(f'"../_struct/{st}_msh.tdr"',f'"{grid}"').replace(f'"../../{PAR.name}"',f'"{PAR}"')
  profile=None
  if kind=='proxy' and where!='uniform':
   profile=B/'profiles'/f'c{min(c,4)}_{where}.tdr'
   pat=r'Optics\( OpticalGeneration\( Scaling=0 SetConstant\( Value=0 \) TimeDependence\( WaveTime=\((.*?)\) WaveTLin=1e-10 \) \) \)'
   mark=re.search(pat,head);assert mark
   scale=p['Gb']/1e26*5
   head=head.replace(mark[0],f'Optics( OpticalGeneration( Scaling=0 ReadFromFile( DatasetName=OpticalGeneration ) TimeDependence( Scaling={scale:.12g} WaveTime=({mark[1]}) WaveTLin=1e-10 ) ) )')
   head=re.sub(r'  Physics\( Region="R.Ch_v" \) \{ Optics.*?\}\n','',head)
   head=head.replace('    Grid      =',f'    OpticalGenerationInput = "{profile}"\n    Grid      =',1)
  marker='hDensity( Integrate( Region="R.Ch_v" ) )';assert head.count(marker)==1
  head=head.replace(marker,marker+'\n    eDensity( Integrate( Region="R.Ch_v" ) )\n    Band2BandGeneration( Integrate( Region="R.Ch_v" ) )\n    AvalancheGeneration( Integrate( Region="R.Ch_v" ) )\n    SRHRecombination( Integrate( Region="R.Ch_v" ) )\n    SRHRecombination( Integrate( Semiconductor ) )')
  if mode=='clamped':clamps=[(.13e-9,ts-.5e-9)]
  elif mode=='early':clamps=[(.13e-9,.14e-9)]
  else:clamps=[(.13e-9,.14e-9),(ts-10e-12,ts)]
  bounds={0,end,.13e-9,.14e-9,ts-.5e-9,ts,ts+.5e-9,ts+.75e-9,ts+3.25e-9,ts+5.25e-9,ts+10.45e-9,ts+10.5e-9,ts+179e-9,ts+179.25e-9}
  for k in range(9):bounds.add(ts+k*21e-9+10.45e-9)
  for a,b,dt in S.seg:bounds.update([a,b])
  for a,b in clamps:bounds.update([a,b])
  bounds=sorted(x for x in bounds if 0<=x<=end)
  solve=['Solve {','  Coupled( Iterations=200 LineSearchDamping=1e-4 ){ Poisson }','  Coupled{ Poisson Electron Hole Contact Circuit }','  Unset( nSN )']
  for a,b in zip(bounds,bounds[1:]):
   if b-a<1e-18:continue
   ds=[dt for x,y,dt in S.seg if x-1e-17<=a and b<=y+1e-17];assert ds,(rid,a,b)
   dt=min(ds)
   if a>=.14e-9 and a<ts:dt*=.25
   if ts<=a<ts+10.5e-9:dt=min(dt,10e-12 if a<ts+.5e-9 else 25e-12)
   dt=min(dt,(b-a)/8)
   for x,y in clamps:
    if abs(a-x)<1e-18:solve.append('  Set( nSN = 1.1 )')
    if abs(a-y)<1e-18:solve.append('  Unset( nSN )')
   n=max(8,min(100,int(round((b-a)/dt))))
   solve += [f'  Transient( InitialTime={a:.12e} FinalTime={b:.12e} InitialStep={dt/10:.12e} MaxStep={dt:.12e} MinStep=1e-18 Increment=1.5 Decrement=2 )','    { Coupled{ Poisson Electron Hole Contact Circuit }',f'      CurrentPlot( Time=( Range=({a:.12e} {b:.12e}) Intervals={n} ) ) }}']
  solve+=['  Plot( FilePrefix="end" )','}'];deck=head+'\n'.join(solve)+'\n';rd=B/'runs'/rid;rd.mkdir(exist_ok=True);cmd=rd/(rid+'_des.cmd');assert not (rd/'process.json').exists();cmd.write_text(deck)
  ref=None
  if q==1 and mode=='clamped' and ii==1 and cm=='write_fit' and where in (None,'uniform'):
   source=REF/'runs'/f'F3N_c{c}' if kind=='natural' else B/'baseline'/f'Ds2F_c{c}'
   ref=dict(directory=str(source),id=source.name,kind='fin3_own_generation_live' if kind=='natural' else 'fin3_completed_baseline')
   references.append(dict(target_id=rid,**ref))
  j=dict(id=rid,group=group,case=c,baseline='fin3',preparation=kind,preparation_factor=q,source_window=where,source_factor=q if kind=='proxy' else 0,absolute_GBQ_factor=mk.GBB[c]*q if kind=='proxy' else 0,hold_ns=p['tHold'],SN_protocol=mode,II=ii,Cs_basis=cm,structure=st,parameters=p,schedule=sched,clamps_s=clamps,deck_sha256=sha(cmd),mesh_path=str(grid),mesh_sha256=sha(grid),parameter_path=str(PAR),parameter_sha256=sha(PAR),profile_path=str(profile) if profile else None,profile_sha256=sha(profile) if profile else None,reuse_from=ref,reading=dict(quantity='gated-body average electrostatic potential',reference='transient initial equilibrium',time_s=ts+.75e-9),diagnostic='case-specific fin3 preparation; not a paper-disclosed initial history')
  (rd/'run.json').write_text(json.dumps(j,indent=2)+'\n');jobs.append(j)
assert len(jobs)==720 and len(references)==10
def priority(j):return (0 if j['reuse_from'] and j['preparation']=='proxy' else 1 if j['preparation_factor']==1 and j['II']==1 and j['Cs_basis']=='write_fit' else 2,j['group'],j['case'])
jobs.sort(key=priority)
manifest=dict(baseline='fin3',claude_baseline_commit='5e6deb4',claude_latest_checked='986aae4',runs=jobs,references=references,full_waveform=True,old_720_reused=False,frozen_inputs={p.name:sha(p) for p in (B/'snapshot').iterdir() if p.is_file()},preparation_factors=[.8,1,1.2],resource_policy='8 workers x4threads; local verified raw-data mirror then server retirement; quota reserve512MiB;6h per job')
(B/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with (B/'design_matrix.csv').open('w',newline='',encoding='utf-8-sig') as f:
 keys=['id','group','case','preparation','preparation_factor','source_window','absolute_GBQ_factor','hold_ns','SN_protocol','II','Cs_basis'];w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader();w.writerows({k:j[k] for k in keys} for j in jobs)
print('PREPARED720 fin3 full-waveform conditions; reuse10 fin3 references, NEW710; no old720 result reused')
