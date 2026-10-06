from pathlib import Path
import sys,json,datetime,re
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent))
from audit_recovery_round11 import readplt,at,integ,expected_times,missing_times,Q,ROOT
m=json.loads((R/'manifest.json').read_text())
def analyse(j):
    rid=j['id'];rd=R/'runs'/rid
    row={'id':rid,'kind':j['kind'],'checked_at':datetime.datetime.now().astimezone().isoformat()}
    rc=(rd/'exit_code.txt').read_text().strip() if (rd/'exit_code.txt').exists() else None
    row['exit_code']=rc
    try:s,sc=readplt(rd/(rid+'_sys.plt'),live=rc is None);d,dc=readplt(rd/('c1_'+rid+'_dev.plt'),live=rc is None)
    except Exception as e:row['read_error']=str(e);return row
    row.update(system=sc,device=dc)
    if j['kind']=='body_balance_observation':
        row['body_observation_keys']=[k for k in d if k.startswith('IntegrR.Ch_v ') and any(w in k for w in ['Density','Generation','Ionization','Recombination'])]
    cmd=(rd/(rid+'_des.cmd')).read_text();last=min(s['time'][-1],d['time'][-1]);end=j['schedule']['tEnd']
    miss=missing_times(d['time'],expected_times(cmd),last)
    row['missing_requested_samples']=len(miss)
    row['valid_complete']=rc=='0' and sc['pass'] and dc['pass'] and not miss and abs(last-end)<max(1e-20,end*1e-7)
    if not sc['pass'] or not dc['pass'] or miss:return row
    p=j['parameters'];ts=j['schedule']['tS'];scale=p['Wact']/1000*1e-12
    if rid.startswith('RR_CDR'):
        period=(p['tON']+p['tOFF'])*1e-9;marks=[ts+n*period-20e-12 for n in range(51)]
        marks=[x for x in marks if x<=last]
        losses=[(at(s,'v(nSN)',marks[0])-at(s,'v(nSN)',x))*1000 for x in marks]
        row['idle_loss_same_phase_mV']=losses
        if len(losses)==51:
            attack,_=readplt(ROOT/'codex_validation/condition_discrimination_20261006/runs/CDR_id_i0_on/CDR_id_i0_on_sys.plt')
            a=[(at(attack,'v(nSN)',marks[0])-at(attack,'v(nSN)',x))*1000 for x in marks]
            net=[x-y for x,y in zip(a,losses)]
            row['attack_minus_idle_loss_mV']=net;row['net_last10_mV_per_cycle']=(net[50]-net[40])/10
        return row
    release=.14e-9;psi=next(k for k in d if k.startswith('Pos(0.125,') and k.endswith('ElectrostaticPotential'))
    h='IntegrR.Ch_v hDensity';sn='v(nSN)';cap=float(re.search(r'capacitance\s*=\s*([\deE.+-]+)',cmd)[1])
    if last<release:return row
    def snap(x):
        return {'time_ns':x*1e9,'SN_V':at(s,sn,x),'body_holes':at(d,h,x)*scale,
             'psi_V':at(d,psi,x),'psi_rise_equilibrium_mV':(at(d,psi,x)-at(d,psi,0))*1000,
             'psi_rise_after_reset_mV':(at(d,psi,x)-at(d,psi,release))*1000}
    row['snapshots']=[snap(x) for x in [release,min(ts,last)] if x<=last]
    def phase(a,b,body=False):
        drop=at(s,sn,a)-at(s,sn,b);cur=integ(d,'sn_v TotalCurrent',a,b);qcap=cap*drop
        r={'start_ns':a*1e9,'end_ns':b*1e9,'SN_loss_mV':drop*1000,'SN_total_fC':cur*1e15,
           'SN_electron_fC':integ(d,'sn_v eCurrent',a,b)*1e15,'SN_hole_fC':integ(d,'sn_v hCurrent',a,b)*1e15,
           'SN_displacement_fC':integ(d,'sn_v DisplacementCurrent',a,b)*1e15,'Cs_deltaV_fC':qcap*1e15,
           'BL_electron_fC':integ(d,'bl eCurrent',a,b)*1e15,'BL_hole_fC':integ(d,'bl hCurrent',a,b)*1e15,
           'charge_mismatch_fC':(cur-qcap)*1e15,'charge_mismatch_relative':abs(cur-qcap)/max(abs(qcap),1e-22),
           'body_holes_start':at(d,h,a)*scale,'body_holes_end':at(d,h,b)*scale}
        if body:
            gb=next(k for k in d if k.startswith('IntegrR.Ch_v ') and k.endswith('Band2BandGeneration'))
            gi=next(k for k in d if k.startswith('IntegrR.Ch_v ') and ('ImpactIonization' in k or 'Avalanche' in k))
            sr=next(k for k in d if k.startswith('IntegrR.Ch_v ') and k.lower().endswith('srhrecombination'))
            gbt=integ(d,gb,a,b)*scale;gii=integ(d,gi,a,b)*scale;rs=integ(d,sr,a,b)*scale
            delta=r['body_holes_end']-r['body_holes_start']
            r.update(BTBT_body_pairs=gbt,II_body_pairs=gii,SRH_body_signed_net_recombination_pairs=rs,
                body_hole_delta=delta,net_outward_body_hole_flux_plus_discretization_residual=gbt+gii-rs-delta)
            for label,words in [('BTBT_all_Si_pairs','band2bandgeneration'),('II_all_Si_pairs','impactionization'),('SRH_all_Si_signed_net_recombination_pairs','srhrecombination')]:
                key=next((k for k in d if k.startswith('IntegrSemiconductor ') and k.lower().endswith(words)),None)
                if key:r[label]=integ(d,key,a,b)*scale
        return r
    if last<ts:
        if j['kind']=='body_balance_observation':row['hold_partial']=phase(release,last,True)
        return row
    row['prefall']=snap(ts);row['hold']=phase(release,ts,j['kind']=='body_balance_observation')
    if last>=ts+10.5e-9:
        row['first_10p5ns_after_fall']=phase(ts,ts+10.5e-9,j['kind']=='body_balance_observation')
    lowend=ts+(p['Tper']*.5e-9)
    if last>=lowend:
        row['first_low']=phase(ts,lowend,j['kind']=='body_balance_observation')
        row['lowend']=snap(lowend)
        row['charge_budget_within_1percent']=all(row[k]['charge_mismatch_relative']<.01 for k in ['hold','first_low'])
    if j['kind']=='body_balance_observation':
        edge=ts+p['tEdge']*1e-9
        if last>=edge:row['fall_edge']=phase(ts,edge,True)
        if last>=lowend:row['low_plateau']=phase(edge,lowend,True)
        row['interpretation']='SRH signed NET recombination. Body flux is inferred by continuity residual, not a measured boundary current. No stand-in generation; II remains on.'
    return row

out={'checked_at':datetime.datetime.now().astimezone().isoformat(),'runs':[analyse(j) for j in m['runs']]}
(R/'recovery_analysis.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
for row in out['runs']:print(json.dumps(row))
