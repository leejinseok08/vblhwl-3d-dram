from pathlib import Path
import sys,json,datetime
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'snapshot'))
from gt_tran import load,at
M=json.loads((R/'manifest.json').read_text())
CONTROL=R.parent/'numeric_A1'

def integral(t,y,a,b):
    xs=[a]+[x for x in t if a<x<b]+[b];ys=[at(t,y,x) for x in xs]
    return sum((x1-x0)*(y0+y1)/2 for x0,x1,y0,y1 in zip(xs,xs[1:],ys,ys[1:]))

def metrics(rd,rid,p,sched):
    d=load(str(next(rd.glob('*_dev.plt'))));s=load(str(rd/(rid+'_sys.plt')))
    T=d['time'];t=s['time'];last=min(t[-1],T[-1]);release=.14e-9;a=sched['tS']-1e-12;b=sched['tS']+10.5e-9-1e-12
    row={'last_ns':last*1e9,'first_low_complete':last>=b}
    if last<a:return row
    psi=next(k for k in d if 'ElectrostaticPotential' in k);h=next(k for k in d if 'hDensity' in k)
    scale=p['Wact']/1000*1e-12
    snkey=next(k for k in s if 'nSN)' in k);sn=lambda x:at(t,s[snkey],x)
    row.update(SN_after_initialisation_V=sn(release),SN_prefall_V=sn(a),
        hold_droop_mV=(sn(release)-sn(a))*1000,
        psi_prefall_V=at(T,d[psi],a),
        psi_rise_equilibrium_mV=(at(T,d[psi],a)-at(T,d[psi],0))*1000,
        psi_rise_after_initialisation_mV=(at(T,d[psi],a)-at(T,d[psi],release))*1000,
        Nholes_prefall=at(T,d[h],a)*scale,
        SN_current_hold_fC=integral(T,d['sn_v TotalCurrent'],release,a)*1e15,
        Cs_hold_deltaV_fC=p['Cs']*(sn(release)-sn(a))*1e15)
    e=next((k for k in d if 'eDensity' in k),None)
    if e:row['Nelectrons_prefall']=at(T,d[e],a)*scale
    if last>=b:
        qI=integral(T,d['sn_v TotalCurrent'],a,b)*1e15;qC=p['Cs']*(sn(a)-sn(b))*1e15
        row.update(first_low_loss_from_prefall_mV=(sn(a)-sn(b))*1000,
            total_loss_from_initialisation_mV=(sn(release)-sn(b))*1000,
            SN_current_first_low_fC=qI,Cs_first_low_deltaV_fC=qC,
            charge_mismatch_first_low_fC=qI-qC)
    return row

out={'checked_at':datetime.datetime.now().astimezone().isoformat(),'runs':[]}
for j in M['runs']:
    rid=j['id'];rd=R/'runs'/rid;f=rd/'exit_code.txt'
    row={'id':rid,'exit_code':f.read_text().strip() if f.exists() else None}
    try:new=metrics(rd,rid,j['parameters'],j['schedule'])
    except (StopIteration,FileNotFoundError,AttributeError):out['runs'].append(row);continue
    row['free_SN']=new
    if 'SN_prefall_V' in new:
        control=metrics(CONTROL/'runs'/j['control_id'],j['control_id'],j['parameters'],j['schedule'])
        row['long_clamp_control']=control
        row['difference']={'SN_prefall_mV':(new['SN_prefall_V']-control['SN_prefall_V'])*1000,
          'psi_prefall_mV':(new['psi_prefall_V']-control['psi_prefall_V'])*1000,
          'Nholes':new['Nholes_prefall']-control['Nholes_prefall']}
    out['runs'].append(row)
out['all_finished']=all(x.get('exit_code')=='0' for x in out['runs'])
(R/'analysis.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
for x in out['runs']:print(json.dumps(x))
print('ALL_FINISHED',out['all_finished'],'Diagnostic: no automatic adoption or paper-reproduction claim')
