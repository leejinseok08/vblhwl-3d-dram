from pathlib import Path
import sys,json,datetime
r=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'snapshot'));from gt_tran import load,at
m=json.loads((r/'manifest.json').read_text());out={'checked_at':datetime.datetime.now().astimezone().isoformat(),'runs':[]}
controls=json.loads((r.parent/'numeric_A1'/'analysis.json').read_text())
for j in m['runs']:
    rd=r/'runs'/j['id'];f=rd/'exit_code.txt'
    row={'id':j['id'],'exit_code':f.read_text().strip() if f.exists() else None}
    try:d=load(str(next(rd.glob('*_dev.plt'))));s=load(str(rd/(j['id']+'_sys.plt')))
    except (StopIteration,FileNotFoundError,AttributeError):out['runs'].append(row);continue
    t=j['schedule']['tS']-1e-12;p=j['parameters'];T=d['time'];scale=p['Wact']/1000*1e-12
    if min(T[-1],s['time'][-1])<t:row['last_ns']=T[-1]*1e9;out['runs'].append(row);continue
    psi=next(k for k in d if 'ElectrostaticPotential' in k);h=next(k for k in d if 'hDensity' in k)
    row.update(psi_prefall_V=at(T,d[psi],t),Nholes_prefall=at(T,d[h],t)*scale,
      psi_rise_equilibrium_mV=(at(T,d[psi],t)-at(T,d[psi],0))*1000,
      SN_prefall_V=at(s['time'],s[next(k for k in s if 'nSN)' in k)],t),
      nominal_Fig8_rise_mV=j['target_rise_mV'])
    ctl=next(x['new'] for x in controls['runs'] if x['id']==j['control_id'])
    row['delta_psi_from_constant_mV']=(row['psi_prefall_V']-ctl['psi_prefall_V'])*1000
    row['relative_Nholes_change']=row['Nholes_prefall']/ctl['Nholes_prefall']-1
    row['uniform_import_equivalent']=abs(row['delta_psi_from_constant_mV'])<=5 and abs(row['relative_Nholes_change'])<=.01
    out['runs'].append(row)
out['all_finished']=all(x.get('exit_code')=='0' for x in out['runs'])
out['uniform_import_pass']=out['all_finished'] and all(x.get('uniform_import_equivalent',False) for x in out['runs'])
(r/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
for x in out['runs']:print(json.dumps(x))
print('UNIFORM_IMPORT_PASS',out['uniform_import_pass'],'No localised sizing or pulse run automatically launched')
