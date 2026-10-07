from pathlib import Path
import json,sys,os,hashlib,shutil,datetime
B=Path(__file__).resolve().parent;CV=B.parent;OLD=CV/'factorial_conditions_20261006'
assert str(OLD)=='/home/e20241515/vblhwl_3d_dram/codex_validation/factorial_conditions_20261006'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (OLD/'OBSOLETE.json').exists()
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:cwd=(p/'cwd').resolve();cmd=(p/'cmdline').read_bytes()
 except OSError:continue
 if cwd==OLD or OLD in cwd.parents:assert b'run_queue.py' not in cmd and b'sdevice' not in cmd,'Old job still active'
for folder in ['fin3_update_20261007','fin3_factorial_20261007']:
 m=json.loads((CV/folder/'manifest.json').read_text());serialized=json.dumps(m)
 assert str(OLD)+'/' not in serialized,'Live manifest depends on old files'
 for j in m['runs']:
  for key in ['mesh','parameter','profile']:
   if j.get(key+'_path'):assert sha(Path(j[key+'_path']))==j[key+'_sha256']
targets=[OLD/'runs',OLD/'results']
inventory=[]
for d in targets:
 if not d.exists():continue
 assert d.resolve().parent==OLD and not d.is_symlink()
 for root,dirs,files in os.walk(str(d),followlinks=False):
  for n in dirs:assert not (Path(root)/n).is_symlink()
  for n in files:
   p=Path(root)/n;assert not p.is_symlink();inventory.append(dict(relative=str(p.relative_to(OLD)),bytes=p.stat().st_size))
record=dict(checked_at=datetime.datetime.now().astimezone().isoformat(),authorization='User: existing720 may be deleted if no longer needed',targets=[str(p) for p in targets],files=len(inventory),bytes=sum(p['bytes'] for p in inventory),live_manifests_independent=True,live_input_hashes_pass=True,old_processes_absent=True,kept='code/manifest/checks/snapshot/profiles/OBSOLETE and Git history',inventory=inventory)
if sys.argv[1]=='apply':
 for d in targets:
  if d.exists():shutil.rmtree(str(d))
 record['deleted']=True
(B/('old720_cleanup_applied.json' if sys.argv[1]=='apply' else 'old720_cleanup_plan.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='inventory'},indent=2))
