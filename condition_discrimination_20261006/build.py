from pathlib import Path
import sys, copy, json, hashlib, re

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'snapshot'))
import make_runs as mr
REMOTE='/home/e20241515/vblhwl_3d_dram/codex_validation/condition_discrimination_20261006'
MESHROOT='/home/e20241515/vblhwl_3d_dram/runs/_struct'
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
meshes={'gr_c1h':'c9c50820ee739fd5653b541bdd2a91ceea11e775605f5a784ece72268826a070',
        'gr_c2h':'e44c0359c930d640d42ee9f1fffcf61ddb960c40da99432776fe1420d0b7b8c5',
        'gr_zz':'43768c65a04290b5ece53ea0b811a37fc0a94b0e2a5eb5dfce562a982ea7ae9a'}
jobs=[]
# Initial-history sensitivities. Baselines CFk/CFi already exist; keep their
# write, capacitor, model, and BL amplitude. Longer hold is NOT a paper fact.
for case,ii in [(1,1),(1,0),(2,1)]:
    old=f'CF{"i" if ii else "k"}_c{case}'
    r=copy.deepcopy(next(r for r in mr.RUNS if r['id']==old))
    r['id']=f'CDH_c{case}_i{ii}'
    r['ov'].update(tHold=2100.0,Npulse=3,SNset=0.0,tWr=0.3)
    jobs.append((r,False,old,'history: 2.1 us natural hold, three BL cycles'))
# Matched initial timing for all resistor/attack controls. OFF reproduces the
# Fig.6 model choice; ON tests Fig.7. 50 cycles distinguishes offset from slope.
for ii,res,tag in [(0,1e-4,'id'),(0,2e5,'r2e5'),(1,2e5,'r2e5')]:
    for attack in (True,False):
        old='QS2e5_zz'
        r=copy.deepcopy(next(r for r in mr.RUNS if r['id']==old))
        r['id']=f'CDR_{tag}_i{ii}_{"on" if attack else "idle"}'
        r['ov'].update(II=ii,Rwl=res,tWr=1.0,tHold=1.0,Ncyc=50,SNset=0.0)
        jobs.append((r,not attack,old,'matched timing, aggressor toggle versus idle'))

rows=[]
for r,idle,old,purpose in jobs:
    p,txt,info=mr.build(r); rid=r['id']; st=r['struct']
    if r['deck']=='cho:FBE':
        _,_,_,sched=mr.deck_cho(rid,p,st,'FBE')
        start=info['tS']-p['tHold']*1e-9
        i=next(i for i,(a,b,dt) in enumerate(sched.seg) if abs(a-start)<1e-15 and abs(b-info['tS'])<1e-15)
        bounds=[0,1e-9,10e-9,100e-9,1000e-9,2100e-9]
        sched.seg[i:i+1]=[(start+a,start+b,min((b-a)/20,20e-9)) for a,b in zip(bounds,bounds[1:])]
        mr.check_segs(sched,info['tEnd'])
        solve=mr.solve_transient(sched).replace('Contact Circuit }\n','Contact Circuit }\n  Unset( nSN )\n',1)
        txt=(txt[:txt.rfind('Solve {')]+solve).replace(' eQuantumPotential','')
        info['nseg']=len(sched.seg)
        info['min_steps']=mr.check_segs(sched,info['tEnd'])
    if idle:
        pat=r'(Vsource_pset vwla \( nWLa 0 \) \{ pwl = \()(.*?)(\) \})'
        match=re.search(pat,txt); assert match
        vals=[float(v) for v in match.group(2).split()]
        pts=[(vals[i],0.0) for i in range(0,len(vals),2)]
        mr.check_pwl(rid+' idle',pts)
        txt=txt[:match.start(2)]+mr.pwl(pts)+txt[match.end(2):]
    # Retain all charge evolution; no manual body charge or post-write SN clamp.
    assert txt.count('Unset( nSN )')==1 and 'Set( nSN = 1.1' not in txt
    assert txt.index('Unset( nSN )')<txt.index('Transient(')
    assert 'eQuantumPotential' not in txt and p['QC']==0
    assert p['BTBT']==1 and p['SNset']==0 and p['Bgc']==0
    assert p['Lg']==100 and p['Tox']==5 and p['Tgm']==20 and p['Dvox']==30
    assert p['Nsd']==1e20 and p['Nch']==1e18
    assert p['Cs']==mr.CSB[p['Tbody']]
    txt=txt.replace(f'Grid      = "../_struct/{st}_msh.tdr"',f'Grid      = "{MESHROOT}/{st}_msh.tdr"')
    txt=txt.replace(f'Parameter = "../../{p["Par"]}"',f'Parameter = "{REMOTE}/snapshot/{p["Par"]}"')
    out=ROOT/'runs'/rid; out.mkdir(parents=True,exist_ok=True)
    deck=out/f'{rid}_des.cmd'; deck.write_text(txt,encoding='utf-8',newline='\n')
    meta=dict(id=rid,structure=st,source_template=old,purpose=purpose,parameters=p,
              schedule=info,aggressor_idle=idle,deck_sha256=sha(deck),
              mesh_sha256=meshes[st],status='diagnostic; undisclosed author settings not established',
              explicit_differences_from_paper=['2D transistor + lumped Cs, not full 3D capacitor',
              'history hold 2100 ns / three pulses OR 50 RH cycles are diagnostic choices',
              'HfO2/Si3N4, abrupt profiles, 300 K and undisclosed model values are assumptions'])
    (out/'run.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    rows.append(meta)
# Interleave to get one result for each question early; one process at a time.
order=['CDH_c1_i1','CDR_r2e5_i0_on','CDR_r2e5_i0_idle','CDH_c1_i0',
       'CDR_id_i0_on','CDR_id_i0_idle','CDR_r2e5_i1_on','CDR_r2e5_i1_idle','CDH_c2_i1']
rows.sort(key=lambda r:order.index(r['id']))
manifest=dict(runs=rows,meshes=meshes,snapshot_sha256={p.name:sha(p) for p in (ROOT/'snapshot').iterdir() if p.is_file()})
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'queue.txt').write_text('\n'.join(order)+'\n',encoding='ascii')
for r in rows: print(r['id'],r['structure'],r['parameters']['II'],r['schedule'])
