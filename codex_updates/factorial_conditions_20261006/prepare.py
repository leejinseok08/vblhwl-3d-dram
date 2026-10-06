from pathlib import Path
import shutil,json,hashlib,re,sys,itertools,csv
B=Path(__file__).resolve().parent;ROOT=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['snapshot','profiles','checks','runs','results']:(B/n).mkdir(exist_ok=True)
if sys.argv[1:] == ['bootstrap']:
 for n in ['make_runs.py','params.py','sde_gt_dvs.cmd','sdevice_cal_a1.7e21_b2.25e07.par']:shutil.copy2(ROOT/n,B/'snapshot'/n)
 shutil.copy2(ROOT/'codex_validation/condition_discrimination_20261006/snapshot/chk_struct.tcl',B/'snapshot/chk_struct.tcl')
 # Profiles carry only an optical source; their geometry never replaces the Grid.
 text=(ROOT/'codex_validation/fbe_joint_20261006/spatial_A2/create_profiles.tcl').read_text()
 text=text.replace('foreach case {1 2}', 'foreach case {1 2 3 4}')
 text=text.replace('$root/../numeric_A1/runs/JN_c${case}_q1050/end_c1_des.tdr','$root/snapshot/c${case}_profile_source.tdr')
 (B/'create_profiles.tcl').write_text(text)
 for c in [1,2,3,4]:
  source=ROOT/'runs'/f'Dh1F_c{c}'/'end_c1_des.tdr'
  spec=json.loads((source.parent/'run.json').read_text())
  assert spec['struct']==f'gr_c{c}h'
  shutil.copy2(source,B/'snapshot'/f'c{c}_profile_source.tdr')
 text=(ROOT/'codex_validation/fbe_joint_20261006/spatial_A2/verify_profiles.tcl').read_text().replace('foreach case {1 2}', 'foreach case {1 2 3 4}').replace('$case == 1 ? .055 : .050','$case == 1 ? .055 : ($case == 2 ? .050 : .045)')
 (B/'verify_profiles.tcl').write_text(text)
 print('BOOTSTRAP: frozen generator/parameters and source-only TDR preparation');sys.exit()

sys.path.insert(0,str(B/'snapshot'));import make_runs as mk
from params import P as DEF
PAR=B/'snapshot/sdevice_cal_a1.7e21_b2.25e07.par'
base=json.loads((ROOT/'runs/Dh1F_c2/run.json').read_text())['params']
cases=[(c,st,w,t) for c,st,w,t in mk.CASES];meshes={};inputs={}
for c,st,w,t in cases:
 grid=ROOT/'runs/_struct'/f'{st}_msh.tdr';meshes[st]=sha(grid)
 old=ROOT/'runs'/f'Dh1F_c{c}'/f'Dh1F_c{c}_des.cmd'
 inputs[str(old)]=sha(old)
prep=[('natural',21,None,0),('natural',15200,None,0),('natural',21000,None,0)]
prep += [('proxy',21,where,f) for where in ['uniform','bl','sn'] for f in [1,1.125,1.25]]
jobs=[]
for g,(pr,mode,ii,capmode) in enumerate(itertools.product(prep,['early','clamped','late_reset'],[1,0],['write_fit','text']),1):
 kind,hold,where,f=pr
 for c,st,w,tb in cases:
  rid=f'FC{g:03d}_c{c}'
  p=dict(DEF);p.update(base);p.update(mk.STRUCTS[st]);p.update(WFs=w,WFd=w,Tbody=tb,II=ii,Cs=mk.CSB[tb]*(1.8/4.2 if capmode=='write_fit' else 1),tHold=hold,Tper=21,Npulse=1,Nthr=4,ErrH=1e14 if c<=3 else 1e10,Par=PAR.name,Gb=mk.GBQ[c]*f if kind=='proxy' else 0)
  raw,sched,waves,S=mk.deck_cho(rid,p,st,'FBE')
  ts=sched['tS'];end=ts+10.5e-9;release=.14e-9
  if mode=='early':clamps=[(.13e-9,release)]
  elif mode=='clamped':clamps=[(.13e-9,ts-.5e-9)]
  else:clamps=[(.13e-9,release),(ts-10e-12,ts)]
  # Keep original physical waveform/device blocks. Explicitly reconstruct solver segments to place clamp boundaries.
  head=raw.split('Solve {',1)[0]
  head=head.replace(f'"../_struct/{st}_msh.tdr"',f'"{ROOT}/runs/_struct/{st}_msh.tdr"').replace(f'"../../{PAR.name}"',f'"{PAR}"')
  profile=None
  if kind=='proxy' and where!='uniform':
   profile=B/'profiles'/f'c{min(c,4)}_{where}.tdr'
   mark=re.search(r'Optics\( OpticalGeneration\( Scaling=0 SetConstant\( Value=0 \) TimeDependence\( WaveTime=\((.*?)\) WaveTLin=1e-10 \) \) \)',head)
   assert mark
   scale=p['Gb']/1e26*5 # equal nominal pair dose: 25nm window versus 125nm body; actual integral is measured.
   head=head.replace(mark[0],f'Optics( OpticalGeneration( Scaling=0 ReadFromFile( DatasetName=OpticalGeneration ) TimeDependence( Scaling={scale:.12g} WaveTime=({mark[1]}) WaveTLin=1e-10 ) ) )')
   head=re.sub(r'  Physics\( Region="R.Ch_v" \) \{ Optics.*?\}\n','',head)
   head=head.replace('    Grid      =',f'    OpticalGenerationInput = "{profile}"\n    Grid      =',1)
  cp='    hDensity( Integrate( Region="R.Ch_v" ) )'
  assert head.count(cp)==1
  head=head.replace(cp,cp+'\n    eDensity( Integrate( Region="R.Ch_v" ) )\n    Band2BandGeneration( Integrate( Region="R.Ch_v" ) )\n    AvalancheGeneration( Integrate( Region="R.Ch_v" ) )\n    SRHRecombination( Integrate( Region="R.Ch_v" ) )\n    SRHRecombination( Integrate( Semiconductor ) )')
  # Build a union of original segments and clamp times; no overlap and no missed voltage boundaries.
  bounds={0,end,release,ts,ts+.5e-9,ts+1.5e-9,ts+10.5e-9}
  for a,b,dt in S.seg:
   if a<end:bounds.update([a,min(b,end)])
  for a,b in clamps:bounds.update([a,b])
  bounds=sorted(x for x in bounds if 0<=x<=end)
  seg=[]
  for a,b in zip(bounds,bounds[1:]):
   if b-a<1e-18:continue
   orig=[dt for x,y,dt in S.seg if x-1e-17<=a and b<=y+1e-17];assert orig,(rid,a,b)
   dt=min(orig)
   if a>=release:
    if a>=ts:dt=min(dt,10e-12 if a<ts+.5e-9 else 25e-12)
    else:dt*=.25
   dt=min(dt,(b-a)/8)
   seg.append((a,b,dt))
  solve=['Solve {','  Coupled( Iterations=200 LineSearchDamping=1e-4 ){ Poisson }','  Coupled{ Poisson Electron Hole Contact Circuit }','  Unset( nSN )']
  for a,b,dt in seg:
   for x,y in clamps:
    if abs(a-x)<1e-18:solve.append('  Set( nSN = 1.1 )')
    if abs(a-y)<1e-18:solve.append('  Unset( nSN )')
   n=max(8,min(100,int(round((b-a)/dt))))
   solve += [f'  Transient( InitialTime={a:.12e} FinalTime={b:.12e} InitialStep={dt/10:.12e} MaxStep={dt:.12e} MinStep=1e-18 Increment=1.5 Decrement=2 )',
    '    { Coupled{ Poisson Electron Hole Contact Circuit }',f'      CurrentPlot( Time=( Range=({a:.12e} {b:.12e}) Intervals={n} ) ) }}']
  solve+=['  Plot( FilePrefix="end" )','}']
  deck=head+'\n'.join(solve)+'\n';rd=B/'runs'/rid;rd.mkdir(exist_ok=True);fn=rd/(rid+'_des.cmd');fn.write_text(deck)
  j=dict(id=rid,group=g,case=c,preparation=kind,hold_ns=hold,source_window=where,source_factor=f,SN_protocol=mode,II=ii,Cs_basis=capmode,structure=st,parameters=p,schedule=dict(sched,tEnd=end),
   clamps_s=clamps,deck_sha256=sha(fn),mesh_path=str(ROOT/'runs/_struct'/f'{st}_msh.tdr'),mesh_sha256=meshes[st],parameter_path=str(PAR),parameter_sha256=sha(PAR),
   profile_path=str(profile) if profile else None,profile_sha256=sha(profile) if profile else None,
   fixed_geometry_source='Cho Fig2/Fig5; same gr meshes; no junction/material/physical coefficient changes')
  (rd/'run.json').write_text(json.dumps(j,indent=2)+'\n');jobs.append(j)
assert len(jobs)==720 and len({j['id'].lower() for j in jobs})==720
# Prioritize missing natural histories, spatial profiles and intermediate charge; severe cases first.
def priority(j):
 pr=0 if j['preparation']=='natural' and j['hold_ns']==15200 else 1 if j['source_window'] in ('bl','sn') else 2
 return (pr,0 if j['case'] in (1,2) else 1,0 if j['II']==1 and j['Cs_basis']=='write_fit' else 1,j['group'],j['case'])
jobs.sort(key=priority)
m=dict(runs=jobs,meshes=meshes,input_source_sha256=inputs,snapshot_sha256={p.name:sha(p) for p in (B/'snapshot').iterdir() if p.is_file()},
 factors=dict(case=[1,2,3,4,5],II=[0,1],Cs=['write_fit','text'],SN=['early','clamped','late_reset'],preparation=prep),
 count=720,screen='same first 10.5ns BL low; full 200ns and write/IdVg validation for shortlisted common configurations',
 resource_policy='8 workers x4 threads, gzip only own completed artifacts, quota reserve512MiB, max walltime6h per screening run')
(B/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
(B/'queue.txt').write_text('\n'.join(j['id'] for j in jobs)+'\n')
with (B/'design_matrix.csv').open('w',newline='',encoding='utf-8-sig') as f:
 keys=['id','group','case','preparation','hold_ns','source_window','source_factor','SN_protocol','II','Cs_basis'];w=csv.DictWriter(f,keys);w.writeheader();w.writerows({k:j[k] for k in keys} for j in jobs)
print('PREPARED',len(jobs),'finite factorial screen conditions; grids',meshes)
