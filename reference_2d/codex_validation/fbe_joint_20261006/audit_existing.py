from pathlib import Path
import sys,json,hashlib,csv,math
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT/'tools'))
from gt_tran import load,at
Q=1.602176634e-19
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def integ(t,v,a,b):
 xs=[a]+[x for x in t if a<x<b]+[b]
 ys=[at(t,v,x) for x in xs]
 return sum((y0+y1)*(x1-x0)/2 for x0,x1,y0,y1 in zip(xs,xs[1:],ys,ys[1:]))
rows=[];details=[];sources={}
for tag in ['h1','fin']:
 for c in range(1,6):
  rid=f'D{tag}F_c{c}';rd=PROJECT/'runs'/rid
  jf=rd/'run.json';meta=json.loads(jf.read_text(encoding='utf-8'));p=meta['params'];tA=meta['sched']['tS'];origin=tA-p['tHold']*1e-9
  dev=next(rd.glob('*_dev.plt'));sysf=rd/(rid+'_sys.plt');deck=rd/(rid+'_des.cmd')
  d=load(str(dev));s=load(str(sysf));T=d['time'];t=s['time']
  assert min(t[-1],T[-1])>=origin+200e-9,(rid,'incomplete')
  for f in [dev,sysf,deck,jf]:sources[str(f.relative_to(PROJECT))]=sha(f)
  snk=next(k for k in s if 'nSN)' in k);sn=lambda x:at(t,s[snk],x)
  psi=next(k for k in d if 'ElectrostaticPotential' in k);phi=next(k for k in d if 'hQuasiFermiPotential' in k)
  hk=next(k for k in d if 'hDensity' in k);nk=next((k for k in d if 'IntegrR.Ch_v' in k and 'eDensity' in k),None)
  scale=p['Wact']/1000*1e-12
  pre=tA-1e-12;lowend=tA+p['Tper']*1e-9/2-1e-12;end200=origin+200e-9
  refs={'equilibrium':T[0],'post_write_SNset':origin,'pre_BL_fall':pre}
  snapshots={name:{'ns':x*1e9,'SN_V':sn(x),'psi_V':at(T,d[psi],x),'phi_p_V':at(T,d[phi],x),'N_holes':at(T,d[hk],x)*scale} for name,x in refs.items()}
  row={'run':rid,'case':c,'Cs_fF':p['Cs']*1e15,'target_first_mV':[55,29,7.1,3.5,0][c-1],
       'target_200_mV':[100,50,14.6,7,1][c-1],'target_rise_mV':[555,445,365,320,368][c-1],
       'Nholes_preBL':snapshots['pre_BL_fall']['N_holes'],
       'excess_holes_vs_equilibrium':snapshots['pre_BL_fall']['N_holes']-snapshots['equilibrium']['N_holes'],
       'rise_from_eq_mV':(snapshots['pre_BL_fall']['psi_V']-snapshots['equilibrium']['psi_V'])*1000,
       'rise_from_FBEorigin_mV':(snapshots['pre_BL_fall']['psi_V']-snapshots['post_write_SNset']['psi_V'])*1000,
       'first_loss_from_origin_mV':(sn(origin)-sn(lowend))*1000,
       'first_loss_from_prefall_mV':(sn(pre)-sn(lowend))*1000,
       'loss200_from_origin_mV':(sn(origin)-sn(end200))*1000,
       'first_SN_total_integral_fC':integ(T,d['sn_v TotalCurrent'],pre,lowend)*1e15,
       'first_Cs_deltaV_fC':p['Cs']*(sn(pre)-sn(lowend))*1e15,
       'clamped_SN_terminal_charge_fC':integ(T,d['sn_v TotalCurrent'],origin,tA-0.5e-9)*1e15,
       'exact_lowend_ns':lowend*1e9,'FBE_origin_ns':origin*1e9,'prefall_ns':pre*1e9,'last_ns':min(T[-1],t[-1])*1e9}
  row['body_rise_normalized_error']=(row['rise_from_eq_mV']-row['target_rise_mV'])/30
  row['first_normalized_error']=(math.log10(max(row['first_loss_from_origin_mV'],1e-3)/row['target_first_mV'])/.3 if row['target_first_mV']>0 else row['first_loss_from_origin_mV'])
  row['loss200_normalized_error']=math.log10(max(row['loss200_from_origin_mV'],1e-3)/row['target_200_mV'])/.3
  details.append({'run':rid,'snapshots':snapshots,'all_potential_probes_preBL':{k:at(T,d[k],pre) for k in d if 'Pos(' in k and 'Potential' in k},'electron_integral_available':nk is not None})
  rows.append(row)
ROOT.mkdir(parents=True,exist_ok=True)
with (ROOT/'audit_existing.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(ROOT/'audit_existing.json').write_text(json.dumps({'runs':rows,'detail':details,'source_sha256':sources},ensure_ascii=False,indent=2),encoding='utf-8')
for x in rows: print(x['run'],'N',round(x['Nholes_preBL'],1),'rise eq/origin',round(x['rise_from_eq_mV'],1),round(x['rise_from_FBEorigin_mV'],1),'loss1',round(x['first_loss_from_origin_mV'],2),'loss200',round(x['loss200_from_origin_mV'],2),'SNclamp charge fC',round(x['clamped_SN_terminal_charge_fC'],4),'I/C check fC',round(x['first_SN_total_integral_fC'],4),round(x['first_Cs_deltaV_fC'],4))
