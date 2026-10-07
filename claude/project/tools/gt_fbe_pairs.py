# gt_fbe_pairs.py <run id> ... : FBE runs, does the body charge decay or is it made again? Per run and per BL period after the first
# BL fall: electron-hole pairs made by impact ionization and by band-to-band tunnelling in the low phase and in the high phase that
# follows (time integral of the generation integrals of the device file; 100 nm wide device = integral x 1e-13), holes in the body at
# the fall and at the end of the low phase, and what the storage node loses in the low phase. Works on running jobs.
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
W = 1e-13

def cum(T, y):                             # running time integral (trapezoid), as in gt_rh_pairs.py (that file runs on import)
    o = [0.0]
    for i in range(1, len(T)): o.append(o[-1] + (y[i] + y[i - 1]) / 2 * (T[i] - T[i - 1]))
    return o

def phases(rid):
    """rows (period, pairs II low, pairs II high, pairs BTBT low, holes at the fall, holes at the end of the low phase, node loss in the low phase [mV])"""
    d = os.path.join(RUNS, rid)
    s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; T = dv["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; bl = s[k("nBL")]; end = min(t[-1], T[-1])
    av = cum(T, dv[next(q for q in dv if "ImpactIonization" in q)]); bb = cum(T, dv[next(q for q in dv if "Band2BandGeneration" in q)])
    hv = dv[next(q for q in dv if "hDensity" in q)]; f = edges(t, bl, 0, 1.1, False); r = [x for x in edges(t, bl, 0, 1.1, True) if f and x > f[0]]
    out = []
    for i, (a, b) in enumerate(zip(f, r)):
        if b > end: break
        c = f[i + 1] if i + 1 < len(f) and f[i + 1] <= end else None       # end of the high phase that follows
        out.append((i + 1, (at(T, av, b) - at(T, av, a)) * W, (at(T, av, c) - at(T, av, b)) * W if c else float("nan"), (at(T, bb, b) - at(T, bb, a)) * W,
                    at(T, hv, a) * W, at(T, hv, b) * W, (at(t, sn, a) - at(t, sn, b)) * 1e3))
    return out

if __name__ == "__main__":
    for rid in sys.argv[1:]:
        try: rows = phases(rid); p = json.load(open(os.path.join(RUNS, rid, "run.json"), encoding="utf-8"))["params"]
        except Exception as e: print(f"{rid}: no data ({e})"); continue
        print(f"== {rid}: driving force {p.get('IIdf') or 'default'}, Cs {p['Cs'] * 1e15:.2f} fF")
        print("   BL period | pairs by impact ionization: low phase, high phase | by tunnelling, low phase | holes in the body: at the fall, end of the low phase | node loss in the low phase [mV]")
        for n, a, b, c, h0, h1, dl in rows: print(f"   {n:9d} | {a:26.0f} {b:11.0f}        | {c:12.1f}             | {h0:18.0f} {h1:10.0f}                     | {dl:8.2f}")
