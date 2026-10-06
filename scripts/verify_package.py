"""Validate recorded hashes and reproduce all shared analyses without TCAD."""
from pathlib import Path
import json,hashlib,subprocess,sys,os,re,math,csv,io
R=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
batch_paths=['fbe_joint_20261006/numeric_A1','fbe_joint_20261006/free_sn_A3','fbe_joint_20261006/spatial_A2','condition_discrimination_20261006']
verified=0
if (R/'FILES_SHA256.json').exists():
    for path,expected in json.loads((R/'FILES_SHA256.json').read_text(encoding='utf-8'))['files'].items():
        assert sha(R/path)==expected,'Shared file changed: '+path;verified+=1
for path in batch_paths:
    batch=R/path;m=json.loads((batch/'manifest.json').read_text(encoding='utf-8'))
    for name,h in m['snapshot_sha256'].items():assert sha(batch/'snapshot'/name)==h,(path,name)
    assert json.loads((batch/'checks'/'mesh_pass.json').read_text(encoding='utf-8'))['pass']
    review=json.loads((batch/'checks'/'reviewed.json').read_text(encoding='utf-8'))
    assert review['manifest_sha256']==sha(batch/'manifest.json'),path
    for j in m['runs']:
        rid=j['id'];assert sha(batch/'runs'/rid/(rid+'_des.cmd'))==j['deck_sha256'],rid
        assert sha(R/'device_meshes'/(j['structure']+'_msh.tdr'))==j['mesh_sha256'],rid
        if 'profile' in j:assert sha(batch/'profiles'/j['profile'])==j['profile_sha256'],rid
        for name,h in j.get('baseline_sha256',{}).items():
            baseline=batch/'baseline'/j['source_template']/name
            if not baseline.exists() and 'control_id' in j:
                baseline=batch.parent/'numeric_A1'/'baseline'/j['source_template']/name
            assert sha(baseline)==h,(rid,name)
ref=R/'reference_2d';audit=ref/'codex_validation'/'fbe_joint_20261006'
for name,h in json.loads((audit/'audit_existing.json').read_text(encoding='utf-8'))['source_sha256'].items():assert sha(ref/name)==h,name
secret=re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgithub_pat_[A-Za-z0-9_]+|\bgh[pousr]_[A-Za-z0-9]{20,}')
for p in R.rglob('*'):
    if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and '_replay' not in p.parts and p.suffix in ['.py','.cmd','.json','.md','.sh','.txt','.par']:
        assert not secret.search(p.read_text(encoding='utf-8',errors='replace')),'Credential-like content found; path only: '+str(p.relative_to(R))
def strip_time(obj):
    if isinstance(obj,dict):return {k:strip_time(v) for k,v in obj.items() if k!='checked_at'}
    if isinstance(obj,list):return [strip_time(v) for v in obj]
    return obj
def equivalent(a,b,path='root'):
    if isinstance(a,dict):
        assert isinstance(b,dict) and a.keys()==b.keys(),(path,'keys')
        for k in a:equivalent(a[k],b[k],path+'.'+k)
    elif isinstance(a,list):
        assert isinstance(b,list) and len(a)==len(b),(path,'length')
        for i,(x,y) in enumerate(zip(a,b)):equivalent(x,y,path+'.'+str(i))
    elif isinstance(a,float):
        assert isinstance(b,(float,int)) and math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(path,a,b)
    else:assert a==b,(path,a,b)
env=os.environ.copy();env['PYTHONIOENCODING']='utf-8';env['PYTHONUTF8']='1'
for relative,script,outputs in [
 (batch_paths[0],'analyze.py',['analysis.json']),
 (batch_paths[1],'analyze.py',['analysis.json']),
 (batch_paths[2],'analyze.py',['analysis.json']),
 (batch_paths[3],'progress_metrics.py',['progress_metrics.json']),
 ('reference_2d/codex_validation/fbe_joint_20261006','audit_existing.py',['audit_existing.json','audit_existing.csv'])]:
    folder=R/relative;backup={n:(folder/n).read_bytes() for n in outputs}
    try:
        proc=subprocess.run([sys.executable,script],cwd=folder,capture_output=True,text=True,encoding='utf-8',env=env,timeout=180)
        assert proc.returncode==0,'Analysis failed: '+relative+' '+proc.stderr[-600:]
        for n,original in backup.items():
            if n.endswith('.json'):equivalent(strip_time(json.loads(original)),strip_time(json.loads((folder/n).read_bytes())),relative)
            else:
                oldrows=list(csv.reader(io.StringIO(original.decode('utf-8-sig'))));newrows=list(csv.reader(io.StringIO((folder/n).read_bytes().decode('utf-8-sig'))))
                def numeric(rows):
                    result=[]
                    for row in rows:
                        converted=[]
                        for value in row:
                            try:converted.append(float(value))
                            except ValueError:converted.append(value)
                        result.append(converted)
                    return result
                equivalent(numeric(oldrows),numeric(newrows),relative+'.csv')
        print('PASS raw-data analysis reproduction:',relative)
    finally:
        for n,original in backup.items():(folder/n).write_bytes(original)
print('PASS hashes, completed/partial raw-data analyses and credential-pattern inspection;',verified,'inventory files verified')
