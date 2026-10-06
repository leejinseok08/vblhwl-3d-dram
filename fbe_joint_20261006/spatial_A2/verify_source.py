from pathlib import Path
import csv,json
r=Path(__file__).resolve().parent;results=[]
for case in [1,2]:
 for window in ['uniform','bl','sn']:
    rows=[]
    for row in csv.reader((r/'checks'/f'c{case}_{window}_generation.csv').open()):
        try:
            if len(row)==2:rows.append(tuple(map(float,row)))
        except ValueError:pass
    a,b={'uniform':(.05,.175),'bl':(.05,.075),'sn':(.15,.175)}[window]
    assert rows
    inside=[v for x,v in rows if a+.001<x<b-.001]
    outside=[v for x,v in rows if x<a-.001 or x>b+.001]
    assert inside and all(abs(v/1e26-1)<1e-5 for v in inside),(case,window,inside)
    leakage=max(abs(v) for v in outside)/1e26
    assert outside and leakage<1e-5,(case,window,leakage)
    msg=f'PASS source c{case} {window}: inside ({a*1000:g},{b*1000:g})nm=1e26 cm^-3 s^-1, outside/peak<1e-5 (actual {leakage:.3g}); exclude 1nm interface interpolation band'
    print(msg);results.append(msg)
(r/'checks'/'source_pass.json').write_text(json.dumps({'pass':True,'checks':results},indent=2)+'\n')
