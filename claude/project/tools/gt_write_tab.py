# gt_write_tab.py <run id> ... : write runs against Fig.4(a). Per run: storage capacitor, driving force of the avalanche model, storage
# node 12 / 24 / 39 / 60 ps after the WL edge, deviation from the paper's four points [mV] and its rms / tolerance (the score of
# tools/score2d.py for the write). Works on running jobs (what is not reached is "-").
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
print("run          Cs [fF]  driving force   | node at 12 / 24 / 39 / 60 ps [V]    | deviation [mV]              | rms / tolerance (30 mV)")
print("paper Fig.4(a)                        | " + " / ".join(f"{v:.3f}" for v in P.WRITE.values()))
for rid in sys.argv[1:]:
    d = os.path.join(RUNS, rid)
    try: s = load(os.path.join(d, rid + "_sys.plt")); p = json.load(open(os.path.join(d, "run.json"), encoding="utf-8"))["params"]
    except Exception: print(f"{rid:12s} no data"); continue
    t = s["time"]; k = lambda n: next(x for x in s if n in x); e = edges(t, s[k("nWL)")], 0, 1.8, True)
    if not e: print(f"{rid:12s} before the WL edge"); continue
    v = [at(t, s[k("nSN)")], e[0] + x * 1e-12) if t[-1] >= e[0] + x * 1e-12 else None for x in P.WRITE]
    dev = [(a - b) * 1e3 if a is not None else None for a, b in zip(v, P.WRITE.values())]
    rms = (sum(x * x for x in dev) / 4) ** 0.5 / (P.WRITE_TOL * 1e3) if None not in dev else float("nan")
    print(f"{rid:12s} {p['Cs'] * 1e15:6.2f}   {(p.get('IIdf') or 'default') if p.get('II') else 'ionization off':14s} | " + " / ".join(f"{x:.3f}" if x is not None else "  -  " for x in v)
          + "       | " + " / ".join(f"{x:+5.0f}" if x is not None else "    -" for x in dev) + f"   | {rms:.2f}")
