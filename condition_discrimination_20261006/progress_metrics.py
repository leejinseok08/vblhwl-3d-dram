from pathlib import Path
import sys,json,datetime
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r/'snapshot'))
from gt_tran import load,at
Q=1.602176634e-19
m=json.loads((r/'manifest.json').read_text())
out={'checked_at':datetime.datetime.now().astimezone().isoformat(),'runs':[]}
rh={}
for j in m['runs']:
 rid=j['id']; rd=r/'runs'/rid; p=j['parameters']; sched=j['schedule']
 rc=(rd/'exit_code.txt').read_text().strip() if (rd/'exit_code.txt').exists() else None
 row={'id':rid,'exit_code':rc,'status':'complete' if rc=='0' else 'failed' if rc else 'not_completed'}
 fs=list(rd.glob('*_dev.plt'))
 if not fs: out['runs'].append(row);continue
 try: d=load(str(fs[0]));s=load(str(rd/(rid+'_sys.plt')))
 except Exception as e: row['read_error']=str(e);out['runs'].append(row);continue
 t=d['time']; ts=s['time']; last=min(t[-1],ts[-1]); row['last_saved_ns']=last*1e9
 row['target_ns']=sched['tEnd']*1e9
 if rc=='0': assert last>=sched['tEnd']-1e-15,(rid,last)
 if rc is None: row['status']='partial'
 first=sched['tS']; vk=next(k for k in s if 'nSN)' in k)
 sn=lambda x:at(ts,s[vk],x)
 if rid.startswith('CDR') and last>=first:
  period=(p['tON']+p['tOFF'])*1e-9
  times=[first+n*period-20e-12 for n in range(51)]
  times=[x for x in times if x<=last]
  losses=[(sn(times[0])-sn(x))*1000 for x in times]
  row['RH']={'initial_SN_V':sn(times[0]),'sample_offset_before_rise_ps':20,'cycles':len(times)-1,
             'same_phase_loss_mV':losses,
             'mean_50_mV_per_cycle':losses[50]/50 if len(losses)>50 else None,
             'last10_mV_per_cycle':(losses[50]-losses[40])/10 if len(losses)>50 else None}
  rh[rid]=row['RH']
 if rid.startswith('CDH') and last>=first:
  scale=p['Wact']/1000*1e-12
  hk=next(k for k in d if 'IntegrR.Ch_v hDensity' in k)
  bk=next(k for k in d if 'IntegrSemiconductor Band2BandGeneration' in k)
  ak=next((k for k in d if 'Avalanche' in k and 'Integr' in k),None)
  potentials=[k for k in d if k.startswith('Pos(0.125,') and k.endswith(('ElectrostaticPotential','hQuasiFermiPotential'))]
  def snap(x):
   return dict(time_ns=x*1e9,SN_V=sn(x),body_holes=at(t,d[hk],x)*scale,
     BTBT_pA=at(t,d[bk],x)*scale*Q*1e12,avalanche_pA=at(t,d[ak],x)*scale*Q*1e12 if ak else None,
     potentials_V={k:at(t,d[k],x) for k in potentials})
  snaps=[snap(x) for x in [0.325e-9,1e-9,21.024e-9,first] if x<=last]
  cycles=[]
  for n in range(1,4):
   x=first+n*p['Tper']*1e-9
   if x<=last+1e-15: cycles.append((sn(first)-sn(x))*1000)
  event=[]
  ix=[i for i,x in enumerate(t) if first<=x<=first+1e-9]
  if ix:
   ip=max(ix,key=lambda i:abs(d['bl eCurrent'][i]))
   keys=[k for k in d if k.startswith(('bl ','sn_v ','gs_v ','gd_v ')) and k.endswith(('eCurrent','hCurrent','TotalCurrent','DisplacementCurrent'))]
   event={'time_ns':t[ip]*1e9,'currents_at_BL_e_peak_pA':{k:d[k][ip]*1e12 for k in keys}}
  row['FBE']={'snapshots':snaps,'hold_loss_from_1ns_mV':(sn(1e-9)-sn(first))*1000,
              'same_phase_cycle_loss_mV':cycles,'first_event':event}
 out['runs'].append(row)
if all(k in rh and rh[k]['cycles']==50 for k in ['CDR_r2e5_i0_on','CDR_r2e5_i0_idle']):
 a=rh['CDR_r2e5_i0_on']['same_phase_loss_mV']; b=rh['CDR_r2e5_i0_idle']['same_phase_loss_mV']
 delta=[x-y for x,y in zip(a,b)]
 out['R2e5_IIoff_attack_minus_idle']={'net_loss_mV_at_cycles':{str(i):delta[i] for i in [1,2,10,20,40,50]},
     'last10_net_mV_per_cycle':(delta[50]-delta[40])/10,'all50_net_mV_per_cycle':delta[50]/50}
(r/'progress_metrics.json').write_text(json.dumps(out,indent=2))
for row in out['runs']:
 brief={k:v for k,v in row.items() if k not in ['RH','FBE']};print(json.dumps(brief))
 if 'RH' in row:
  z=row['RH']; print('RH',json.dumps({k:v for k,v in z.items() if k!='same_phase_loss_mV'})); print('loss1,10,20,50',[z['same_phase_loss_mV'][i] for i in [1,10,20,50] if i<=z['cycles']])
 if 'FBE' in row: print('FBE',json.dumps(row['FBE']))
if 'R2e5_IIoff_attack_minus_idle' in out:print('PAIRED',json.dumps(out['R2e5_IIoff_attack_minus_idle']))
