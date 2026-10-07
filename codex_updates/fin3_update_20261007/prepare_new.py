from pathlib import Path
import sys,json,shutil,hashlib
B=Path(__file__).resolve().parent;ROOT=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['snapshot','checks','runs','results']:(B/n).mkdir(exist_ok=True)
if sys.argv[1:]==['bootstrap']:
 for n in ['make_runs.py','params.py','sdevice_cal_a1.7e21_b2.25e07.par']:shutil.copy2(ROOT/n,B/'snapshot'/n)
 shutil.copy2(ROOT/'codex_validation/condition_discrimination_20261006/snapshot/chk_struct.tcl',B/'snapshot/chk_struct.tcl')
 print('Frozen generator/parameter file; root files untouched');sys.exit()
sys.path.insert(0,str(B/'snapshot'));import make_runs as mk
from params import P as DEF
jobs=[];holds={1:20600,2:16200,3:19600,4:18700,5:14600}
for c,st,w,tb in mk.CASES:
 rid=f'F3N_c{c}';base=json.loads((B/'baseline'/f'Ds2F_c{c}'/'run.json').read_text())
 p=dict(DEF);p.update(base['params']);p.update(Gb=0,SNhold=1,tHold=holds[c],Npulse=9,Tper=21,tEdge=.5,ProbeX=1,ProbeT=1,Nthr=4)
 par=B/'snapshot'/p['Par'];assert par.exists()
 raw,sched,waves,S=mk.deck_cho(rid,p,st,'FBE')
 head=raw.split('Solve {',1)[0]
 grid=ROOT/'runs/_struct'/f'{st}_msh.tdr'
 head=head.replace(f'"../_struct/{st}_msh.tdr"',f'"{grid}"').replace(f'"../../{par.name}"',f'"{par}"')
 marker='hDensity( Integrate( Region="R.Ch_v" ) )';assert head.count(marker)==1
 head=head.replace(marker,marker+'\n    eDensity( Integrate( Region="R.Ch_v" ) )\n    Band2BandGeneration( Integrate( Region="R.Ch_v" ) )\n    AvalancheGeneration( Integrate( Region="R.Ch_v" ) )\n    SRHRecombination( Integrate( Region="R.Ch_v" ) )\n    SRHRecombination( Integrate( Semiconductor ) )')
 assert 'Ave' not in head or 'Average(Window' in head
 ts=sched['tS'];end=sched['tEnd'];clamps=[(.13e-9,ts-.5e-9)]
 # Preserve the existing waveform and models; refine first edge and low interval and explicitly save the fin3 reading.
 bounds={0,end,.13e-9,.14e-9,ts-.5e-9,ts,ts+.5e-9,ts+.75e-9,ts+3.25e-9,ts+5.25e-9,ts+10.45e-9,ts+10.5e-9,ts+179e-9,ts+179.25e-9}
 for a,b,dt in S.seg:bounds.update([a,b])
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
 solve+=['  Plot( FilePrefix="end" )','}'];deck=head+'\n'.join(solve)+'\n'
 rd=B/'runs'/rid;rd.mkdir(exist_ok=True);cmd=rd/(rid+'_des.cmd');assert not (rd/'process.json').exists();cmd.write_text(deck)
 j=dict(id=rid,case=c,structure=st,parameters=p,schedule=sched,clamps_s=clamps,deck_sha256=sha(cmd),mesh_path=str(grid),mesh_sha256=sha(grid),parameter_path=str(par),parameter_sha256=sha(par),baseline='fin3',comparison='Ds2F_c'+str(c),diagnostic='natural generation with externally held SN; case-specific hold estimated by Claude ANALYSIS4.8; not paper ns history',reading=dict(quantity='gated-body average electrostatic potential',reference='transient initial equilibrium',time_s=ts+.75e-9,offset_after_fall_complete_ns=.25),paper_axis_origin_s=ts-21e-9)
 (rd/'run.json').write_text(json.dumps(j,indent=2)+'\n');jobs.append(j)
(B/'manifest.json').write_text(json.dumps(dict(baseline='fin3',runs=jobs,claude_commit='5e6deb4',frozen_inputs={p.name:sha(p) for p in (B/'snapshot').iterdir() if p.is_file()},old_screen='fin2 legacy diagnostic, unchanged'),indent=2)+'\n')
print('Prepared five non-duplicate own-generation full-waveform tests:',[(j['id'],j['parameters']['tHold']) for j in jobs])
