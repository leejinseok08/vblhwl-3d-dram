from pathlib import Path
import tarfile,json
B=Path(__file__).resolve().parent
with tarfile.open(B/'share_inputs.tar.gz','w:gz') as tar:
 for folder in ['checks','snapshot','profiles','results']:
  for p in (B/folder).iterdir():
   if p.is_file():tar.add(str(p),arcname=str(p.relative_to(B)),recursive=False)
 for rd in (B/'runs').iterdir():
  for p in [rd/(rd.name+'_des.cmd'),rd/'run.json']:
   if p.exists():tar.add(str(p),arcname=str(p.relative_to(B)),recursive=False)
 for n in ['manifest.json','design_matrix.csv','PRE_RUN_CHECK.md','status.json','old720_discarded.json','ranking.json']:
  p=B/n
  if p.exists():tar.add(str(p),arcname=n,recursive=False)
 for j in json.loads((B/'manifest.json').read_text())['runs']:
  ref=j.get('reuse_from')
  if not ref:continue
  rd=Path(ref['directory'])
  if ref['kind']=='fin3_own_generation_live' and not (rd/'exit_code.txt').exists():continue
  for p in rd.iterdir():
   if p.is_file() and (p.name in ['run.json','exit_code.txt'] or p.name.endswith(('_des.cmd','_sys.plt','_sys.plt.gz','_dev.plt','_dev.plt.gz'))):tar.add(str(p),arcname='reference_raw/'+ref['id']+'/'+p.name,recursive=False)
print('EXPORTED', (B/'share_inputs.tar.gz').stat().st_size)
