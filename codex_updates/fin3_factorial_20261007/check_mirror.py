from pathlib import Path
import tempfile,tarfile,io,json,hashlib,subprocess,sys
B=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(dir=B) as t:
 d=Path(t);data=b'fin3 raw preservation check\n';rel='runs/F3C999_c1/proof.plt.gz';pack=d/'test.tar'
 with tarfile.open(pack,'w') as tar:
  m=tarfile.TarInfo(rel);m.size=len(data);tar.addfile(m,io.BytesIO(data))
 inv=dict(batch='test',pack_sha256=hashlib.sha256(pack.read_bytes()).hexdigest(),files=[dict(relative=rel,size=len(data),sha256=hashlib.sha256(data).hexdigest())]);meta=d/'test.json';meta.write_text(json.dumps(inv),encoding='utf-8')
 subprocess.check_call([sys.executable,str(B/'mirror_local.py'),str(meta),str(d/'verified')]);assert (d/'verified'/rel).read_bytes()==data and json.loads((d/'test.receipt.json').read_text(encoding='utf-8'))['verified_files']==1
print('PASS local raw mirror: tar inventory, safe path, file size/SHA, receipt, original bytes preserved')
