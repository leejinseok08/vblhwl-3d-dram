from pathlib import Path
import sys,json,gzip,tempfile,re,csv,math,datetime,os
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent))
from audit_recovery_round11 import readplt,at,integ,expected_times,missing_times
Q=1.602176634e-19
def read(path):
 if path.exists():return readplt(path)
 if Path(str(path)+'.gz').exists():
  with gzip.open(str(path)+'.gz','rb') as g,tempfile.NamedTemporaryFile(delete=False) as f:f.write(g.read());name=f.name
  try:return readplt(Path(name))
  finally:os.unlink(name)
 raise FileNotFoundError(str(path))
def analyse(j,rd=None,rid=None,reused=False):
 rid=rid or j['id'];rd=rd or B/'runs'/rid
 out=dict(id=j['id'],group=j['group'],case=j['case'],preparation=j['preparation'],source_factor=j['source_factor'],source_window=j['source_window'],hold_ns=j['hold_ns'],SN_protocol=j['SN_protocol'],II=j['II'],Cs_basis=j['Cs_basis'],reused=reused,checked_at=datetime.datetime.now().astimezone().isoformat(),source_directory=str(rd),source_run=rid)
 try:
  s,sc=read(rd/(rid+'_sys.plt'));d,dc=read(rd/('c1_'+rid+'_dev.plt'))
  assert sc['pass'] and dc['pass'],'file integrity'
  end=j['schedule']['tEnd'];ts=j['schedule']['tS'];release=.14e-9
  assert min(s['time'][-1],d['time'][-1])>=end-1e-17,'time coverage'
  cmd=rd/(rid+'_des.cmd')
  if cmd.exists():assert not missing_times(d['time'],expected_times(cmd.read_text()),min(d['time'][-1],end)),'requested samples missing'
  psi=next(k for k in d if k.startswith('Pos(0.125,') and k.endswith('ElectrostaticPotential'));h='IntegrR.Ch_v hDensity';scale=j['parameters']['Wact']/1000*1e-12
  cap=j['parameters']['Cs'];cap=float(f'{cap:g}') # actual resolved deck precision
  def snap(t):return dict(time_ns=t*1e9,SN_V=at(s,'v(nSN)',t),holes=at(d,h,t)*scale,psi_V=at(d,psi,t),body_rise_eq_mV=(at(d,psi,t)-at(d,psi,0))*1000,body_rise_after_initial_reset_mV=(at(d,psi,t)-at(d,psi,release))*1000)
  def phase(a,b):
   v=(at(s,'v(nSN)',a)-at(s,'v(nSN)',b))*1000;cur=integ(d,'sn_v TotalCurrent',a,b)*1e15;dv=cap*v*1e12
   o=dict(SN_loss_mV=v,SN_total_fC=cur,Cs_deltaV_fC=dv,SN_e_fC=integ(d,'sn_v eCurrent',a,b)*1e15,SN_h_fC=integ(d,'sn_v hCurrent',a,b)*1e15,SN_displacement_fC=integ(d,'sn_v DisplacementCurrent',a,b)*1e15,
    BL_e_fC=integ(d,'bl eCurrent',a,b)*1e15,BL_h_fC=integ(d,'bl hCurrent',a,b)*1e15,charge_mismatch_fC=cur-dv,charge_mismatch_relative=abs(cur-dv)/max(abs(dv),1e-5),holes_change=(at(d,h,b)-at(d,h,a))*scale)
   for label,suffix in [('BTBT','band2bandgeneration'),('II','impactionization'),('SRH','srhrecombination'),('proxy','opticalgeneration')]:
    for region,prefix in [('body','IntegrR.Ch_v '),('all_Si','IntegrSemiconductor ')]:
     k=next((k for k in d if k.startswith(prefix) and k.lower().endswith(suffix)),None)
     o[f'{label}_{region}_pairs']=integ(d,k,a,b)*scale if k else (0 if label=='proxy' and j['preparation']=='natural' else None)
   if all(o[k] is not None for k in ['BTBT_body_pairs','II_body_pairs','SRH_body_pairs','proxy_body_pairs']):
    o['outward_body_flux_plus_discretization_residual']=o['BTBT_body_pairs']+o['II_body_pairs']+o['proxy_body_pairs']-o['SRH_body_pairs']-o['holes_change']
   return o
  out.update(prefall=snap(ts),hold=phase(release,ts),first_low=phase(ts,end),fall_edge=phase(ts,ts+.5e-9),low_plateau=phase(ts+.5e-9,end),system=sc,device=dc)
  hs=[v for t,v in zip(s['time'],s['v(nSN)']) if release<=t<=ts]
  out['hold_max_SN_deviation_mV']=max(abs(v-1.1) for v in hs)*1000
  out['external_clamp_SN_current_fC']=sum(integ(d,'sn_v TotalCurrent',max(release,a),b)*1e15 for a,b in j['clamps_s'] if b>release)
  out['definitions']={k:dict(eq_rise_mV=(at(d,k,ts)-at(d,k,0))*1000,after_reset_rise_mV=(at(d,k,ts)-at(d,k,release))*1000,absolute_prefall_V=at(d,k,ts)) for k in d if k.startswith('Pos(') and (k.endswith('ElectrostaticPotential') or k.endswith('hQuasiFermiPotential'))}
  c=j['case'];body={1:555,2:445,3:365,4:320,5:368}[c];loss={1:55,2:29,3:7.1,4:3.5,5:0}[c];actual=out['first_low']['SN_loss_mV']
  score_loss=abs(math.log10(max(actual,1e-3)/loss))/.3 if loss else max(0,actual)/1
  scores=dict(body=abs(out['prefall']['body_rise_eq_mV']-body)/30,loss=score_loss,SN_initial=abs(out['prefall']['SN_V']-1.1)/.005,hold_flatness=out['hold_max_SN_deviation_mV']/5)
  out['scores']=scores;out['joint_FBE_max_score']=max(scores.values());out['FBE_all_targets_within_tolerance']=all(v<=1 for v in scores.values())
  out['first_low_charge_budget_ok']=abs(out['first_low']['charge_mismatch_fC'])<=max(.01*abs(out['first_low']['Cs_deltaV_fC']),1e-4)
  if c==2:
   targets={12:.72,24:.92,39:1.06,60:1.13};errors={str(t):(at(s,'v(nSN)',15e-12+t*1e-12)-v)*1000 for t,v in targets.items()}
   out['write_error_mV']=errors;out['write_max_error_mV']=max(abs(v) for v in errors.values());out['write_strict_pass']=out['write_max_error_mV']<=30
  out['classification']='natural_history' if j['preparation']=='natural' and j['SN_protocol']=='early' else 'externally_prepared_state'
  out['success']=True
 except Exception as e:out.update(success=False,error=str(e))
 return out
def save(j,rd=None,rid=None,reused=False):
 o=analyse(j,rd,rid,reused);tmp=B/'results'/(j['id']+'.tmp');tmp.write_text(json.dumps(o,indent=2)+'\n');tmp.replace(B/'results'/(j['id']+'.json'));return o
def ranking():
 rows=[]
 for p in (B/'results').glob('*.json'):
  try:rows.append(json.loads(p.read_text()))
  except (ValueError,OSError):pass
 good=[r for r in rows if r.get('success')];good.sort(key=lambda r:r['joint_FBE_max_score'])
 groups={}
 for r in good:groups.setdefault(r['group'],[]).append(r)
 complete=[]
 for g,rs in groups.items():
  if len(rs)!=5:continue
  complete.append(dict(group=g,common_max_score=max(r['joint_FBE_max_score'] for r in rs),all_five_FBE_pass=all(r['FBE_all_targets_within_tolerance'] for r in rs),write_pass=next(r.get('write_strict_pass',False) for r in rs if r['case']==2),charge_budget_pass=all(r['first_low_charge_budget_ok'] for r in rs),configuration={k:rs[0][k] for k in ['preparation','hold_ns','source_factor','source_window','SN_protocol','II','Cs_basis']},cases=[r['id'] for r in sorted(rs,key=lambda r:r['case'])]))
 complete.sort(key=lambda r:r['common_max_score'])
 data=dict(checked_at=datetime.datetime.now().astimezone().isoformat(),planned=720,analysed=len(rows),valid=len(good),failed=len(rows)-len(good),ranked_cases=good,ranked_common_configurations=complete,
  note='Rank is a shortlist, not reproduction success. Actual initial charge is measured; proxy multiplier is not author value. Body reference remains unresolved. Strict per-point tolerances; complete200ns/IdVg/grounded control required for final adoption.')
 tmp=B/'ranking.tmp';tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(B/'ranking.json')
 keys=['id','group','case','classification','preparation','hold_ns','source_window','source_factor','SN_protocol','II','Cs_basis','joint_FBE_max_score','FBE_all_targets_within_tolerance','first_low_charge_budget_ok','write_max_error_mV']
 with (B/'candidate_ranking.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows({k:r.get(k) for k in keys} for r in good)
 return data
if __name__=='__main__':
 m=json.loads((B/'manifest.json').read_text())
 if len(sys.argv)>1:
  j=next(j for j in m['runs'] if j['id']==sys.argv[1]);o=save(j);print(json.dumps(o))
 else:
  d=ranking();print('Ranking:',d['analysed'],d['valid'],'common groups',len(d['ranked_common_configurations']))
