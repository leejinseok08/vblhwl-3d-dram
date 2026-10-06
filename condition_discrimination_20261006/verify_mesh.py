from pathlib import Path
import csv,json,re
root=Path(__file__).resolve().parent
checks=[]
for st,tb,nl in [('gr_c1h',30,1),('gr_c2h',20,1),('gr_zz',20,2)]:
 for layer in range(nl):
  for pos in ['lo','mid','hi']:
   tag=f'{st}_L{layer}_{pos}'; path=root/'checks'/(tag+'_horizontal.csv')
   data=[]
   for row in csv.reader(path.open()):
    try: data.append((float(row[0]),float(row[1])))
    except (ValueError,IndexError): pass
   assert data,tag+' no cutline data'
   changes=[(a,b) for a,b in zip(data,data[1:]) if a[1]*b[1]<0]
   assert len(changes)==2,(tag,changes)
   for (a,b),expected in zip(changes,[50,175]):
    assert abs(a[0]*1000-expected)<0.05 and abs(b[0]*1000-expected)<0.05,(tag,a,b)
   for x,d in data:
    if 1<x*1000<49 or 176<x*1000<199: assert abs(d/1e20-1)<1e-5,(tag,x,d)
    if 51<x*1000<174: assert abs(d/(-1e18)-1)<1e-5,(tag,x,d)
   msg=f'PASS {tag}: junctions 50 / 175 nm; donor 1e20, acceptor 1e18 cm^-3'
   print(msg);checks.append(msg)
assert len(checks)==12
(root/'checks'/'mesh_pass.json').write_text(json.dumps({'pass':True,'checks':checks},indent=2))
print('ALL 12 CUTLINES PASS; human paper/geometry review still required before launch')
