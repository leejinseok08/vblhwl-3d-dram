from pathlib import Path
import sys,json,copy,re,hashlib,shutil,math
R=Path(__file__).resolve().parent;PROJECT=R.parents[2]
sys.path.insert(0,str(R/'snapshot'))
import make_runs as mr
BASE='/home/e20241515/vblhwl_3d_dram/codex_validation/fbe_joint_20261006/numeric_A1'
MESH='/home/e20241515/vblhwl_3d_dram/runs/_struct'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meshes={'gr_c1h':'c9c50820ee739fd5653b541bdd2a91ceea11e775605f5a784ece72268826a070',
        'gr_c2h':'e44c0359c930d640d42ee9f1fffcf61ddb960c40da99432776fe1420d0b7b8c5'}
jobs=[]
for case,tag in [(1,'h1'),(1,'fin'),(2,'h1'),(2,'fin')]:
 old=f'D{tag}F_c{case}';rid=f'JN_c{case}_{"q1050" if tag=="h1" else "q1300"}'
 src=PROJECT/'runs'/old; bd=R/'baseline'/old;bd.mkdir(parents=True,exist_ok=True)
 for f in src.iterdir():
  if f.suffix in ['.plt','.cmd','.json']:shutil.copy2(f,bd/f.name)
 meta=json.loads((bd/'run.json').read_text(encoding='utf-8'));p=copy.deepcopy(meta['params'])
 original=mr.deck_cho(old,p,meta['struct'],'FBE')[0].replace(' eQuantumPotential','')
 assert original==(bd/(old+'_des.cmd')).read_text(encoding='utf-8'),old+' baseline cannot be reproduced byte-for-byte by frozen builder'
 p['Npulse']=2
 txt,info,waves,S=mr.deck_cho(rid,p,meta['struct'],'FBE')
 for i,w in enumerate(waves):mr.check_pwl(rid+str(i),w)
 mr.check_segs(S,info['tEnd'])
 txt=txt.replace(' eQuantumPotential','')
 # Only numerical time/output resolution changes, plus a shorter diagnostic horizon.
 pat=r'Transient\( InitialTime=([\deE.+-]+) FinalTime=([\deE.+-]+) InitialStep=([\deE.+-]+) MaxStep=([\deE.+-]+)(.*?)CurrentPlot\( Time=\( Range=\((.*?)\) Intervals=(\d+) \) \)'
 fine=[]
 def refine(m):
  a,b,initial,dt=map(float,m.group(1,2,3,4));newdt=dt
  if a>=info['tS']-1e-16:newdt=min(dt,5e-12 if b-a<=p['tEdge']*1e-9+1e-15 else 50e-12)
  n=max(4,math.ceil((b-a)/newdt-1e-8))
  fine.append({'start_ns':a*1e9,'end_ns':b*1e9,'max_step_ps':newdt*1e12,'output_intervals':n})
  return f'Transient( InitialTime={m[1]} FinalTime={m[2]} InitialStep={newdt/10:.3e} MaxStep={newdt:.3e}{m[5]}CurrentPlot( Time=( Range=({m[6]}) Intervals={n} ) )'
 txt,n=re.subn(pat,refine,txt,flags=re.S);assert n==len(S.seg),(rid,n,len(S.seg))
 assert txt.count('Unset( nSN )')==2 and txt.count('Set( nSN = 1.1 )')==1
 assert 'eQuantumPotential' not in txt and p['QC']==0
 assert p['II']==1 and p['Gb']>0 and p['SNset']==1.1
 assert p['Lg']==100 and p['Tox']==5 and p['Tgm']==20 and p['Dvox']==30 and p['Nch']==1e18 and p['Nsd']==1e20
 txt=txt.replace(f'Grid      = "../_struct/{meta["struct"]}_msh.tdr"',f'Grid      = "{MESH}/{meta["struct"]}_msh.tdr"')
 txt=txt.replace(f'Parameter = "../../{p["Par"]}"',f'Parameter = "{BASE}/snapshot/{p["Par"]}"')
 d=R/'runs'/rid;d.mkdir(parents=True,exist_ok=True);deck=d/(rid+'_des.cmd');deck.write_text(txt,encoding='utf-8',newline='\n')
 j=dict(id=rid,structure=meta['struct'],source_template=old,parameters=p,schedule=info,
        deck_sha256=sha(deck),mesh_sha256=meshes[meta['struct']],segments=fine,
        purpose='A1: numerical convergence only; same artificial body generation and SN clamp as baseline',
        baseline_sha256={f.name:sha(f) for f in bd.iterdir() if f.is_file()},
        differences=['two BL cycles instead of nine','BL edge max5ps, plateau max50ps, dense output; pre-BL maxima unchanged'])
 (d/'run.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8');jobs.append(j)
manifest={'runs':jobs,'meshes':meshes,'snapshot_sha256':{f.name:sha(f) for f in (R/'snapshot').iterdir() if f.is_file()}}
(R/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'queue.txt').write_text('\n'.join(j['id'] for j in jobs)+'\n',encoding='ascii',newline='\n')
for j in jobs:print(j['id'],j['source_template'],'II',j['parameters']['II'],'Cs fF',j['parameters']['Cs']*1e15,'end ns',j['schedule']['tEnd']*1e9,'segments',len(j['segments']))
