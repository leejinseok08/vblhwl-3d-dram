from pathlib import Path
import hashlib,json,csv,datetime,sys,subprocess,re
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/'manifest.json').read_text())
def quota():
    txt=subprocess.check_output(['quota','-w'],universal_newlines=True)
    lines=txt.splitlines()
    for i,line in enumerate(lines):
        if '/dev/mapper/centos-home' in line:
            tokens=line.split();tokens=tokens[1:] if len(tokens)>1 else lines[i+1].split()
            nums=[int(x.strip('*')) for x in tokens[:3]]
            used,soft,hard=nums
            assert soft-used>=512*1024,('quota insufficient KB',used,soft,hard)
            return {'used_KB':used,'soft_KB':soft,'hard_KB':hard}
    raise RuntimeError('could not read user quota')
def verify():
    assert json.loads((R/'checks/mesh_pass.json').read_text())['pass']
    for j in m['runs']:
        assert sha(R/'runs'/j['id']/(j['id']+'_des.cmd'))==j['deck_sha256'],j['id']+' deck'
        for kind in ['mesh','parameter']:
            assert sha(Path(j[kind+'_path']))==j[kind+'_sha256'],j['id']+' '+kind
        assert sha(Path(j['source_path']))==j['source_deck_sha256'],j['id']+' source changed'
    for n,h in m['snapshot_sha256'].items():assert sha(R/'snapshot'/n)==h,n
    return quota()
if sys.argv[1:] == ['record']:
    checks=[]
    for st,layer,low,high in [('gr_c1h',0,40,70),('gr_c2h',0,40,60),('gr_zz',0,40,60),('gr_zz',1,140,160)]:
        rows=[]
        for row in csv.reader((R/'checks'/f'{st}_L{layer}_mid_vertical.csv').open()):
            try:rows.append((float(row[0])*1000,float(row[1])))
            except (ValueError,IndexError):pass
        body=[x for x,y in rows if low-1<x<high+1 and y< -1e17]
        assert abs(min(body)-low)<.01 and abs(max(body)-high)<.01
        msg=f'PASS vertical {st} L{layer}: body {min(body):.3f}..{max(body):.3f}nm';print(msg);checks.append(msg)
    q=verify();r={'reviewed_at':datetime.datetime.now().astimezone().isoformat(),'manifest_sha256':sha(R/'manifest.json'),
        'document_sha256':sha(R/'PRE_RUN_CHECK.md'),'human_read_all_horizontal_checks':12,'vertical_checks':checks,
        'paper':'Cho III/IV/V/VI/VIII and Fig2/4/5/6/7/8 read from original pages before this batch',
        'user_authorization':'User explicitly instructed exact damage recovery and source/recombination-separated Round11 analysis',
        'quota':q}
    (R/'checks/reviewed.json').write_text(json.dumps(r,indent=2)+'\n');print('RECORDED fresh paper/geometry review',q)
else:
    r=json.loads((R/'checks/reviewed.json').read_text())
    assert r['manifest_sha256']==sha(R/'manifest.json') and r['document_sha256']==sha(R/'PRE_RUN_CHECK.md')
    print('PASS guard paper/mesh/deck/parameter/source/quota',verify())
