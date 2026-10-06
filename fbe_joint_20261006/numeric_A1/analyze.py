from pathlib import Path
import sys,json,math,datetime
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'snapshot'))
from gt_tran import load,at
M=json.loads((R/'manifest.json').read_text())
def integral(t,y,a,b):
 xs=[a]+[x for x in t if a<x<b]+[b];ys=[at(t,y,x) for x in xs]
 return sum((x1-x0)*(y0+y1)/2 for x0,x1,y0,y1 in zip(xs,xs[1:],ys,ys[1:]))
def metrics(rd,rid,p,sched):
 df=next(rd.glob('*_dev.plt'));d=load(str(df));s=load(str(rd/(rid+'_sys.plt')))
 T=d['time'];t=s['time'];last=min(t[-1],T[-1]);a=sched['tS']-1e-12;b=sched['tS']+p['Tper']*1e-9/2-1e-12
 if last<b:return {'last_ns':last*1e9,'first_low_complete':False}
 psi=next(k for k in d if 'ElectrostaticPotential' in k);h=next(k for k in d if 'hDensity' in k);scale=p['Wact']/1000*1e-12
 snkey=next(k for k in s if 'nSN)' in k);sn=lambda x:at(t,s[snkey],x)
 origin=sched['tS']-p['tHold']*1e-9
 qI=integral(T,d['sn_v TotalCurrent'],a,b)*1e15;qC=p['Cs']*(sn(a)-sn(b))*1e15
 return {'last_ns':last*1e9,'first_low_complete':True,
  'psi_prefall_V':at(T,d[psi],a),'Nholes_prefall':at(T,d[h],a)*scale,
  'first_loss_origin_mV':(sn(origin)-sn(b))*1000,'first_loss_prefall_mV':(sn(a)-sn(b))*1000,
  'SN_current_integral_fC':qI,'Cs_deltaV_fC':qC,'charge_mismatch_fC':qI-qC,
  'charge_relative_mismatch':abs(qI-qC)/max(abs(qC),1e-15)}
out={'checked_at':datetime.datetime.now().astimezone().isoformat(),'runs':[]}
for j in M['runs']:
 rid=j['id'];rd=R/'runs'/rid;exitfile=rd/'exit_code.txt'
 row={'id':rid,'exit_code':exitfile.read_text().strip() if exitfile.exists() else None}
 try: new=metrics(rd,rid,j['parameters'],j['schedule'])
 except (StopIteration,FileNotFoundError,AttributeError):out['runs'].append(row);continue
 row['new']=new
 if new['first_low_complete']:
  old=j['source_template'];bd=R/'baseline'/old;meta=json.loads((bd/'run.json').read_text())
  orig=metrics(bd,old,meta['params'],meta['sched']);row['baseline']=orig
  dp=(new['psi_prefall_V']-orig['psi_prefall_V'])*1000
  dn=(new['Nholes_prefall']-orig['Nholes_prefall'])/orig['Nholes_prefall']
  dl=new['first_loss_origin_mV']-orig['first_loss_origin_mV']
  chargeok=abs(new['charge_mismatch_fC'])<=max(.001,.01*abs(new['Cs_deltaV_fC']))
  row['comparison']={'delta_psi_mV':dp,'relative_Nholes_change':dn,'delta_first_loss_mV':dl,
     'potential_pass':abs(dp)<=5,'holes_pass':abs(dn)<=.01,
     'loss_pass':abs(dl)<=max(.1,.02*abs(orig['first_loss_origin_mV'])),'charge_balance_pass':chargeok}
  row['pass']=all(row['comparison'][k] for k in ['potential_pass','holes_pass','loss_pass','charge_balance_pass'])
 out['runs'].append(row)
out['all_finished']=all(x.get('exit_code')=='0' for x in out['runs'])
out['A1_pass']=out['all_finished'] and all(x.get('pass',False) for x in out['runs'])
(R/'analysis.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
for x in out['runs']:print(json.dumps(x))
print('ALL_FINISHED',out['all_finished'],'A1_PASS',out['A1_pass'])
