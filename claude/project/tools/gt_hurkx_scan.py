# gt_hurkx_scan.py [tag=cho,hsu,fbe ...] : back-calculation of the Hurkx coefficients (A, B) of the band-to-band tunnelling model (round 30
# and after). Three things of the authors' papers hold them:
#   Cho Fig.5(c)   log10 I at Vg = -1 V of the five cases (V_DS 1.1 V; amperes of the 0.1 um wide device) and the minimum of each curve
#   Hsu Fig.2(c)   the GIDL branch of the silicon reference transistor from -0.7 to -1.75 V (V_DS 1.0 V; tools/gt_hsu_fig2c.py)
#   Cho Fig.8(c)   Case 5 stays on the 1.1 V line: the loss at 200 ns is the hold leak of the storage-node junction (NOTES (bo))
# Per set: A and B of the runs (read from the name of their parameter file), the residuals at -1 V and their mean (the GIDL current goes
# with A, so the mean says how far A is off: A fitted = A run x 10^-mean), the residuals of the Hsu branch after that correction with
# their rms and tilt (residual at -1.75 V minus at -0.7 V), and the loss and leak of Case 5 scaled by the same factor.
# A set is given as tag=<Id-Vg prefix of the five cases>,<Hsu-condition run>,<FBE run of Case 5>; without arguments: round 30.
import sys, os, re, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gt_hsu_fig2c as H                       # sets GT_W = 1: currents in A/um
from gt_fbe_leak import leak
G = H.G; RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
SETS = [a.split("=") for a in sys.argv[1:]] or [["u", "Dd0I,DhuI_c3,DdmF_c5"], ["v", "DdvI,DhvI_c3,DdvF_c5"], ["w", "DdwI,DhwI_c3,DdwF_c5"], ["x", "DdxI,DhxI_c3,DdxF_c5"]]
BR = (-0.7, -0.8, -0.9, -1.0, -1.25, -1.5, -1.75)
def ab(rid):
    m = re.search(r"_a([0-9.e+-]+)_b([0-9.e+-]+?)(?:_|\.par)", json.load(open(os.path.join(RUNS, rid, "run.json"), encoding="utf-8"))["params"]["Par"])
    return (float(m.group(1)), float(m.group(2))) if m else (3.5e21, 2.25e7)
print("paper: Cho Fig.5(c) log10 I [A] at -1 V " + " / ".join(f"{G.PAPER[c]['lm1']:.2f}" for c in range(1, 6)) + "; minimum " + " / ".join(f"{G.PAPER[c]['lmin']:.1f} at {G.PAPER[c]['vmin']:+.2f} V" for c in range(1, 6)))
print("       Hsu Fig.2(c) log10 I [A/um] at " + " / ".join(f"{v:+.2f}" for v in BR) + " V: " + " / ".join(f"{H.HSU[v]:.2f}" for v in BR) + "; Cho Fig.8(c) Case 5: on the 1.1 V line (0.5 mV)")
for tag, runs in SETS:
    iv, hs, fb = runs.split(","); a, b = ab(iv + "_c1")
    r1, mn = [], []
    for c in range(1, 6):
        try: pts = G.curve(os.path.join(RUNS, f"{iv}_c{c}"))
        except Exception: r1.append(None); mn.append(None); continue
        x = G.at(pts, -1.0); k = min(range(len(pts)), key=lambda j: pts[j][1])
        r1.append(None if x is None else x - 1.0 - G.PAPER[c]["lm1"]); mn.append((math.log10(pts[k][1]) - 1.0, pts[k][0]))
    ok = [x for x in r1 if x is not None]; d = sum(ok) / len(ok) if ok else float("nan")
    print(f"== {tag}: A {a:.3g}, B {b:.3g} V/cm")
    print("   Cho, -1 V, model minus paper [decades]: " + " / ".join("  -  " if x is None else f"{x:+.2f}" for x in r1) + f"   mean {d:+.3f} -> A fitted {a * 10 ** -d:.3g}"
          + ";   minimum: " + " / ".join("-" if m is None else f"{m[0]:.2f} at {m[1]:+.2f}" for m in mn))
    try:
        pts = G.curve(os.path.join(RUNS, hs)); rr = [G.at(pts, v) - H.HSU[v] - d for v in BR]; k = min(range(len(pts)), key=lambda j: pts[j][1])
        print("   Hsu branch, model minus paper after that correction: " + " / ".join(f"{x:+.2f}" for x in rr) + f"   rms {math.sqrt(sum(x * x for x in rr) / len(rr)):.3f}, tilt {rr[-1] - rr[0]:+.2f}"
              + f";   as run: " + " / ".join(f"{x + d:+.2f}" for x in rr) + f";   minimum {math.log10(pts[k][1]):.2f} at {pts[k][0]:+.2f} V")
    except Exception as e: print("   Hsu branch: no curve yet", e)
    try:
        o = leak(fb)
        if o: print(f"   Case 5: loss at 200 ns {o['L']:.3f} mV, leak {o['hi'] * o['C'] * 1e12:.2f} pA, tunnelling pairs {o['bb']:.1f}   -> with A fitted: {o['L'] * 10 ** -d:.3f} mV, {o['hi'] * o['C'] * 1e12 * 10 ** -d:.2f} pA   ({fb}, Cs {o['C'] * 1e15:.2f} fF)")
        else: print("   Case 5: the FBE run has not reached 200 ns")
    except Exception as e: print("   Case 5: no FBE run yet", e)
