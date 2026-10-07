from pathlib import Path
import json,datetime,collections
B=Path(__file__).resolve().parent;groups=collections.defaultdict(list)
for f in (B/'results').glob('*.json'):
 o=json.loads(f.read_text())
 if o.get('success'):groups[o['group']].append(o)
rank=[]
for g,rs in groups.items():
 if len(rs)!=5:continue
 rank.append(dict(group=g,preparation=rs[0]['preparation'],factor=rs[0]['preparation_factor'],window=rs[0]['source_window'],SN=rs[0]['SN_protocol'],II=rs[0]['II'],Cs=rs[0]['Cs_basis'],max_score=max(max(r['scores'].values()) for r in rs),all_cases_pass=all(r['all_five_figure8_metrics_for_this_case'] for r in rs),SN_precondition_all_pass=all(r['SN_prefall_within_5mV'] for r in rs),cases=sorted(rs,key=lambda x:x['case'])))
rank.sort(key=lambda r:r['max_score'])
(B/'ranking.json').write_text(json.dumps(dict(updated_at=datetime.datetime.now().astimezone().isoformat(),baseline='fin3',old720_excluded=True,complete_groups=len(rank),ranking=rank),indent=2)+'\n');print('COMPLETE GROUPS',len(rank))
