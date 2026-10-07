from pathlib import Path
import sys,json,math,gzip,tempfile,os,csv,datetime
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent))
from audit_recovery_round11 import readplt,at,integ,expected_times,missing_times
def read(p):
 if p.exists():return readplt(p)
 with gzip.open(str(p)+'.gz','rb') as g,tempfile.NamedTemporaryFile(delete=False) as f:f.write(g.read());n=f.name
 try:return readplt(Path(n))
 finally:os.unlink(n)
def analyse(rd,rid,c,j):
 s,sc=read(rd/(rid+'_sys.plt'));d,dc=read(rd/('c1_'+rid+'_dev.plt'))
 assert sc['pass'] and dc['pass'],'malformed output'
 sched=j.get('schedule',j.get('sched'));ts=sched['tS'];end=sched['tEnd']
 assert min(sc['last_ns'],dc['last_ns'])>=end*1e9-1e-5,'incomplete'
 cmd=rd/(rid+'_des.cmd');assert not missing_times(d['time'],expected_times(cmd.read_text(encoding='utf-8')),end),'requested output missing'
 p=j.get('parameters',j.get('params'));cap=float(f"{p['Cs']:g}");scale=p['Wact']/1000*1e-12
 avg=next(k for k in d if k.startswith('AveWindow((0.075') and k.endswith('ElectrostaticPotential'))
 cen=next(k for k in d if k.startswith('Pos(0.125,') and k.endswith('ElectrostaticPotential'))
 a=ts-.05e-9;v=at(s,'v(nSN)',a)
 def phase(a,b):
  dv=(at(s,'v(nSN)',a)-at(s,'v(nSN)',b))*1000;qi=integ(d,'sn_v TotalCurrent',a,b)*1e15;qc=cap*dv*1e12
  o=dict(SN_loss_mV=dv,current_fC=qi,Cs_deltaV_fC=qc,mismatch_fC=qi-qc,mismatch_relative=abs(qi-qc)/max(abs(qc),1e-5))
  for key in ['sn_v eCurrent','sn_v hCurrent','sn_v DisplacementCurrent','bl eCurrent','bl hCurrent']:o[key+'_fC']=integ(d,key,a,b)*1e15
  o['holes_change']=(at(d,'IntegrR.Ch_v hDensity',b)-at(d,'IntegrR.Ch_v hDensity',a))*scale
  for label,suffix in [('BTBT','band2bandgeneration'),('II','impactionization'),('SRH','srhrecombination'),('proxy','opticalgeneration')]:
   for region,prefix in [('body','IntegrR.Ch_v '),('all_Si','IntegrSemiconductor ')]:
    key=next((k for k in d if k.startswith(prefix) and k.lower().endswith(suffix)),None)
    o[label+'_'+region+'_pairs']=integ(d,key,a,b)*scale if key else (0 if label=='proxy' and p['Gb']==0 else None)
  ks=['BTBT_body_pairs','II_body_pairs','SRH_body_pairs','proxy_body_pairs']
  if all(o[k] is not None for k in ks):o['outward_body_flux_plus_discretization_residual']=o[ks[0]]+o[ks[1]]-o[ks[2]]+o[ks[3]]-o['holes_change']
  return o
 rise=(at(d,avg,ts+.75e-9)-at(d,avg,0))*1000
 losses=[(v-at(s,'v(nSN)',ts+k*21e-9+10.45e-9))*1000 for k in range(9)]
 paper200=(v-at(s,'v(nSN)',ts+179e-9))*1000;compat200=(v-at(s,'v(nSN)',ts+179.25e-9))*1000
 target={1:555,2:445,3:365,4:320,5:368}[c];l1={1:55,2:29,3:7.1,4:3.5,5:0}[c];l2={1:100,2:50,3:14.6,4:7,5:1}[c]
 scores=dict(body=abs(rise-target)/30,first=abs(math.log10(max(losses[0],.001)/l1))/.3 if l1 else abs(losses[0]),loss200=abs(math.log10(max(compat200,.001)/l2))/.3)
 result=dict(id=rid,case=c,success=True,baseline='fin3',diagnostic=j.get('diagnostic','external pair-generation and SN preparation; imported fin3 baseline'),hold_ns=p['tHold'],Gb=p['Gb'],II=p['II'],Cs_F=cap,Nh_prefall=at(d,'IntegrR.Ch_v hDensity',a)*scale,SN_prefall_V=v,
  body_avg_fin3_mV=rise,body_avg_prefall_mV=(at(d,avg,a)-at(d,avg,0))*1000,body_center_prefall_mV=(at(d,cen,a)-at(d,cen,0))*1000,
  low_phase_loss_mV=losses,loss200_paper_axis_mV=paper200,loss200_claude_avg_tool_mV=compat200,scores=scores,all_five_figure8_metrics_for_this_case=max(scores.values())<=1,
  reading_time_ns=(ts+.75e-9)*1e9,paper_axis_origin_ns=(ts-21e-9)*1e9,hold=phase(.14e-9,a),first_low=phase(a,ts+10.45e-9),first_exact10p5ns=phase(ts,ts+10.5e-9),all_after_first_fall=phase(a,ts+179.25e-9),system=sc,device=dc)
 if c==2:
  w=s['v(nWL)'];tw=next(a+(b-a)*(.9-va)/(vb-va) for a,b,va,vb in zip(s['time'],s['time'][1:],w,w[1:]) if va<.9<=vb)
  targets={12:.72,24:.92,39:1.06,60:1.13};errs={str(ps):(at(s,'v(nSN)',tw+ps*1e-12)-v)*1000 for ps,v in targets.items()}
  result['write_from_WL_midpoint']=dict(reference_time_ps=tw*1e12,errors_mV=errs,max_error_mV=max(abs(e) for e in errs.values()),RMS_score=math.sqrt(sum((e/30)**2 for e in errs.values())/4),all_points_pass=max(abs(e) for e in errs.values())<=30)
 return result
def baseline():
 rows=[]
 for c in range(1,6):
  rid=f'Ds2F_c{c}';rd=B/'baseline'/rid;j=json.loads((rd/'run.json').read_text());rows.append(analyse(rd,rid,c,j))
 (B/'baseline_analysis.json').write_text(json.dumps(dict(checked_at=datetime.datetime.now().astimezone().isoformat(),claude_commit='5e6deb4',baseline='fin3',runs=rows),indent=2)+'\n')
 for o in rows:print('VERIFIED',o['id'],'fin3_body',round(o['body_avg_fin3_mV'],2),'first',round(o['low_phase_loss_mV'][0],3),'200ns',round(o['loss200_claude_avg_tool_mV'],3),'all_case_metrics_pass',o['all_five_figure8_metrics_for_this_case'])
 return rows
def save(j):
 try:o=analyse(B/'runs'/j['id'],j['id'],j['case'],j)
 except Exception as e:o=dict(id=j['id'],case=j['case'],success=False,error=str(e))
 (B/'results'/(j['id']+'.json')).write_text(json.dumps(o,indent=2)+'\n');return o
if __name__=='__main__':
 if sys.argv[1:]==['baseline']:baseline()
 else:
  m=json.loads((B/'manifest.json').read_text())
  for j in m['runs']:
   if (B/'runs'/j['id']/'exit_code.txt').exists():print(json.dumps(save(j)))
