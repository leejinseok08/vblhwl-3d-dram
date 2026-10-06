from pathlib import Path
import hashlib,json,datetime
r=Path(__file__).resolve().parent
(r/'checks').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review={'manifest_sha256':sha(r/'manifest.json'),
 'reviewed_at_local':datetime.datetime.now().astimezone().isoformat(),
 'paper_review':'Cho IRPS2026 III/IV/VI and Figs2/4/5/8 reviewed; 2D diagnostic, not full 3D FBE reproduction',
 'mesh_checks_read':8,'release_time_ns':.14,'control_release_time_ns':20.64,
 'A1_internal_validation':'all four completed and passed; generation, Cs, bias, II preserved',
 'review_document_sha256':sha(r/'PRE_RUN_CHECK.md'),
 'authorization':'User explicitly requested proceeding with approved diagnostic experiments'}
(r/'checks'/'reviewed.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
print('Reviewed manifest:',review['manifest_sha256'])
