from pathlib import Path
import re,json,math,bisect,datetime,hashlib,csv,os

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent/'recovery_round11_20261006'
OUT.mkdir(exist_ok=True)
NUM=r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'
Q=1.602176634e-19
SNAP=None

def readplt(path, live=False):
    raw=path.read_bytes(); txt=raw.decode('utf-8',errors='strict')
    if SNAP is not None and path.parent.name.startswith('Dz'):
        dest=SNAP/path.parent.name/path.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    names=re.findall(r'"([^"]+)"',re.search(r'datasets\s*=\s*\[(.*?)\]',txt,re.S)[1])
    data=re.search(r'\bData\s*\{(.*?)(?:\}|$)',txt,re.S)[1]
    tokens=data.split();v=[float(x) for x in tokens]
    rem=len(v)%len(names);rows=[v[i:i+len(names)] for i in range(0,len(v)-rem,len(names))]
    d={k:[r[i] for r in rows] for i,k in enumerate(names)}
    t=d['time'];assert t
    backwards=sum(b<a-1e-22 for a,b in zip(t,t[1:]))
    finite=all(math.isfinite(x) for x in v)
    check={'filename':path.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
           'rows':len(rows),'columns':len(names),'trailing_values':rem,'closed':txt.rstrip().endswith('}'),
           'backwards':backwards,'finite':finite,'first_ns':t[0]*1e9,'last_ns':t[-1]*1e9,
           'max_time_gap_ns':max([b-a for a,b in zip(t,t[1:])]+[0])*1e9}
    check['pass']=backwards==0 and finite and (live or rem==0) and (live or check['closed'])
    return d,check

def at(d,k,x):
    t=d['time'];v=d[k]
    if x<t[0]-1e-20 or x>t[-1]+1e-20:raise ValueError('outside saved time')
    i=bisect.bisect_left(t,x)
    if i==0:return v[0]
    if i>=len(t):return v[-1]
    return v[i-1]+(v[i]-v[i-1])*(x-t[i-1])/(t[i]-t[i-1])
def integ(d,k,a,b):
    t=d['time'];i=bisect.bisect_right(t,a);j=bisect.bisect_left(t,b)
    xs=[a]+t[i:j]+[b];ys=[at(d,k,x) for x in xs]
    return sum((y+x)/2*(r-l) for l,r,x,y in zip(xs,xs[1:],ys,ys[1:]))
def expected_times(cmd):
    pat=r'CurrentPlot\s*\(\s*Time\s*=\s*\(\s*Range\s*=\s*\(\s*('+NUM+r')\s+('+NUM+r')\s*\)\s*Intervals\s*=\s*(\d+)'
    ts=[]
    for a,b,n in re.findall(pat,cmd):
        a,b,n=float(a),float(b),int(n);ts.extend(a+(b-a)*i/n for i in range(n+1))
    return sorted(set(ts))
def missing_times(t,expected,limit):
    missing=[]
    for x in expected:
        if x>limit+max(1e-20,abs(limit)*1e-10):continue
        i=bisect.bisect_left(t,x);near=t[max(0,i-1):i+1]
        if not near or min(abs(x-y) for y in near)>max(1e-20,abs(x)*2e-10):missing.append(x)
    return missing

def main():
    global SNAP
    SNAP=OUT/'round11_snapshots'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    audits=[]
    for rel in ['condition_discrimination_20261006','fbe_joint_20261006/numeric_A1',
                'fbe_joint_20261006/free_sn_A3','fbe_joint_20261006/spatial_A2']:
        base=ROOT/'codex_validation'/rel;m=json.loads((base/'manifest.json').read_text())
        for j in m['runs']:
            rid=j['id'];rd=base/'runs'/rid;cmd=(rd/(rid+'_des.cmd')).read_text()
            row={'batch':rel,'id':rid,'target_ns':j['schedule']['tEnd']*1e9,
                 'exit_code':(rd/'exit_code.txt').read_text().strip() if (rd/'exit_code.txt').exists() else None,
                 'files':[],'problems':[]}
            for f in [rd/(rid+'_sys.plt'),rd/('c1_'+rid+'_dev.plt')]:
                if not f.exists():row['problems'].append(f.name+' missing');continue
                try:
                    d,c=readplt(f);row['files'].append(c)
                    if not c['pass']:row['problems'].append(f.name+' malformed')
                    if abs(c['last_ns']-row['target_ns'])>max(1e-5,row['target_ns']*1e-7):row['problems'].append(f.name+' wrong end time')
                    if '_dev.plt' in f.name and c['backwards']==0:
                        miss=missing_times(d['time'],expected_times(cmd),j['schedule']['tEnd'])
                        c['missing_requested_samples']=len(miss);c['missing_times_ns_first20']=[x*1e9 for x in miss[:20]]
                        if miss:row['problems'].append(f.name+' missing requested output samples')
                except Exception as e:row['problems'].append(f.name+' parse error: '+str(e))
            row['valid']=row['exit_code']=='0' and not row['problems'];audits.append(row)
    
    rounds=[]
    for z in range(3,7):
        for c in range(1,6):
            rid=f'Dz{z}F_c{c}';rd=ROOT/'runs'/rid
            row={'id':rid,'case':c,'complete':False,'issues':[]}
            try:
                spec=json.loads((rd/'run.json').read_text());p=spec['params'];sched=spec['sched'];cmd=(rd/(rid+'_des.cmd')).read_text()
                sd=SNAP/rid;sd.mkdir(parents=True,exist_ok=True)
                (sd/'run.json').write_bytes((rd/'run.json').read_bytes())
                (sd/(rid+'_des.cmd')).write_bytes((rd/(rid+'_des.cmd')).read_bytes())
                rc=(rd/'exit_code.txt').read_text().strip() if (rd/'exit_code.txt').exists() else None
                # Claude runner may use a different exit marker; scientific completion uses files/time.
                s,sc=readplt(rd/(rid+'_sys.plt'),live=rc is None);d,dc=readplt(rd/('c1_'+rid+'_dev.plt'),live=rc is None)
                row.update(exit_code=rc,system=sc,device=dc,hold_us=p['tHold']/1000,period_us=p['Tper']/1000,
                    target_us=sched['tEnd']*1e6,saved_us=min(s['time'][-1],d['time'][-1])*1e6,
                    Gb=p.get('Gb'),II=p['II'],Cs_fF=p['Cs']*1e15)
                row['complete']=sc['closed'] and dc['closed'] and abs(s['time'][-1]-sched['tEnd'])<1e-7*sched['tEnd'] and abs(d['time'][-1]-sched['tEnd'])<1e-7*sched['tEnd']
                if not sc['pass'] or not dc['pass']:row['issues'].append('malformed output');rounds.append(row);continue
                expected=expected_times(cmd);limit=min(s['time'][-1],d['time'][-1]);miss=missing_times(d['time'],expected,limit)
                row['missing_requested_samples_to_saved_time']=len(miss)
                if miss:row['issues'].append('missing requested output samples');rounds.append(row);continue
                ts=sched['tS'];te=p['tEdge']*1e-9;per=p['Tper']*1e-9;release=.14e-9
                psi=next(k for k in d if k.startswith('Pos(0.125,') and k.endswith('ElectrostaticPotential'))
                h=next(k for k in d if k=='IntegrR.Ch_v hDensity');scale=p['Wact']/1000*1e-12
                gn=next(k for k in d if k.startswith('IntegrSemiconductor ') and k.endswith('Band2BandGeneration'))
                ii=next(k for k in d if k.startswith('IntegrSemiconductor ') and ('ImpactIonization' in k or 'Avalanche' in k))
                sn='v(nSN)';cap=float(re.search(r'capacitance\s*=\s*('+NUM+')',cmd)[1]);row['actual_deck_Cs_fF']=cap*1e15
                def snap(x):
                    return {'time_us':x*1e6,'SN_V':at(s,sn,x),'holes':at(d,h,x)*scale,
                            'psi_V':at(d,psi,x),'psi_rise_equilibrium_mV':(at(d,psi,x)-at(d,psi,0))*1000,
                            'psi_rise_after_reset_mV':(at(d,psi,x)-at(d,psi,release))*1000,
                            'BTBT_all_Si_pA':at(d,gn,x)*scale*Q*1e12,'II_all_Si_pA':at(d,ii,x)*scale*Q*1e12}
                row['snapshots']=[snap(x) for x in [release,min(ts,limit)] if x<=limit]
                def phase(a,b):
                    drop=at(s,sn,a)-at(s,sn,b);cur=integ(d,'sn_v TotalCurrent',a,b);qcap=cap*drop
                    return {'start_us':a*1e6,'end_us':b*1e6,'SN_loss_mV':drop*1000,
                        'SN_total_fC':cur*1e15,'SN_electron_fC':integ(d,'sn_v eCurrent',a,b)*1e15,
                        'SN_hole_fC':integ(d,'sn_v hCurrent',a,b)*1e15,
                        'SN_displacement_fC':integ(d,'sn_v DisplacementCurrent',a,b)*1e15,
                        'BL_electron_fC':integ(d,'bl eCurrent',a,b)*1e15,
                        'BL_hole_fC':integ(d,'bl hCurrent',a,b)*1e15,
                        'Cs_deltaV_fC':qcap*1e15,'charge_mismatch_fC':(cur-qcap)*1e15,
                        'holes_start':at(d,h,a)*scale,'holes_end':at(d,h,b)*scale,
                        'BTBT_all_Si_pairs_integral':integ(d,gn,a,b)*scale,
                        'II_all_Si_pairs_integral':integ(d,ii,a,b)*scale}
                if limit>=ts:
                    row['prefall']=snap(ts);row['hold']=phase(release,ts)
                    target={1:555,2:445,3:365,4:320,5:368}[c]/1000
                    row['first_reach_paper_bar']=None
                    for i in range(1,len(d['time'])):
                        a,b=d['time'][i-1],d['time'][i]
                        if a<release or b>ts:continue
                        va,vb=d[psi][i-1]-d[psi][0],d[psi][i]-d[psi][0]
                        if va<target<=vb:
                            x=a+(b-a)*(target-va)/(vb-va)
                            row['first_reach_paper_bar']=snap(x)
                            row['first_reach_paper_bar']['SN_loss_after_reset_mV']=(at(s,sn,release)-at(s,sn,x))*1000
                            break
                lowend=ts+per/2
                if limit>=ts+te:row['first_fall_edge']=phase(ts,ts+te)
                if limit>=lowend:
                    row['first_low']=phase(ts,lowend);row['first_low_plateau']=phase(ts+te,lowend)
                    row['lowend']=snap(lowend)
                if limit>=ts+10.5e-9:
                    row['first_10p5ns_after_fall']=phase(ts,ts+10.5e-9)
                row['available_body_recombination']=any('SRH' in k and k.startswith('IntegrR.Ch_v ') for k in d)
                row['available_body_BTBT']=any('Band2BandGeneration' in k and k.startswith('IntegrR.Ch_v ') for k in d)
                row['available_body_II']=any(('ImpactIonization' in k or 'Avalanche' in k) and k.startswith('IntegrR.Ch_v ') for k in d)
                row['interpretation_limit']='Whole-Si generation minus body stored holes is not recombination: region mismatch and carrier flux. II enabled; cannot attribute all charge to GIDL.'
            except Exception as e:row['issues'].append(str(e))
            rounds.append(row)
    
    data={'checked_at':datetime.datetime.now().astimezone().isoformat(),'raw_snapshot_path':str(SNAP),'codex_audit':audits,'round11':rounds}
    (OUT/'audit_round11.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    (SNAP/'analysis.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    with (OUT/'audit_summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=['batch','id','exit_code','valid','problems']);w.writeheader()
        for r in audits:w.writerow({k:('; '.join(r[k]) if k=='problems' else r[k]) for k in w.fieldnames})
    for r in audits:print('AUDIT',r['id'],'PASS' if r['valid'] else 'FAIL','; '.join(r['problems']))
    for r in rounds:
        print('ROUND11',r['id'],'complete' if r['complete'] else 'partial',r.get('saved_us'),
              'holes',r.get('prefall',{}).get('holes'),'rise',r.get('prefall',{}).get('psi_rise_equilibrium_mV'),
              'holdloss',r.get('hold',{}).get('SN_loss_mV'),'low',r.get('first_low',{}).get('SN_loss_mV'),r['issues'])

if __name__ == '__main__':
    main()
