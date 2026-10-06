# gt_iv_at.py <run dir> ... : the GIDL branch of an Id-Vg run in numbers: log10 of the drain current (W from GT_W, default
# 0.1 um here) at Vg = -1.0, -0.8, -0.5, -0.3, 0 V, next to the paper's readings of Fig.5(c) at -1 and -0.5 V for that case.
# Works on runs that stop before -1 V and on sweeps that start at 0.3 V.
import sys, os, re
os.environ.setdefault("GT_W", "0.1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gt_fig5c as G
P05 = {1: -14.74, 2: None, 3: -14.47, 4: -14.49, 5: -13.41}      # paper at -0.5 V (Case 2 is hidden under the other curves there)
f = lambda x: "   -  " if x is None else f"{x:6.2f}"
print("run             log10 I [A] at Vg -1.0   -0.8   -0.5   -0.3    0.0 | paper -1.0   -0.5 | minimum (Vg, log I) | sweep")
for rd in sys.argv[1:]:
    rid = os.path.basename(rd.rstrip("/")); m = re.search(r"_c(\d)", rid); c = int(m.group(1)) if m else 0
    try: pts = G.curve(rd)
    except Exception:
        print(f"{rid:14s} no curve"); continue
    k = min(range(len(pts)), key=lambda j: pts[j][1]); import math
    print(f"{rid:14s}                      " + " ".join(f(G.at(pts, v)) for v in (-1.0, -0.8, -0.5, -0.3, 0.0)) +
          f" | {f(G.PAPER[c]['lm1']) if c in G.PAPER else '   -  '} {f(P05.get(c))} | {pts[k][0]:+.2f} {math.log10(pts[k][1]):6.2f} | {pts[0][0]:+.2f} .. {pts[-1][0]:+.2f} V ({len(pts)} pts)")
