# gt_avg_tab.py <tag> ... : FBE configurations whose runs record the average potential of the body under the gate (ProbeX=1; rounds
# 13, 14: Dp1F, Dp2F, Ds1F, Ds2F), held against Fig.8 with the back-calculated reading of Fig.8(a):
#   body potential = average electrostatic potential of the body under the gate, counted from the start of the transient,
#   read at the first BL edge (printed: just before the fall, and 0.25 ns after it is complete).
# Per case: holes at t_A, that reading (and the old one: the body-centre point just before the fall), storage node at t_A, loss
# 3 / 5 ns after the fall, after low phases 1 .. 4 and 9, at 200 ns of the paper's axis; then the deviations from the paper
# (bar in mV with the reading named in the header line of the tag; losses in decades) and how many lie inside the tolerances.
import sys, os, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
EARLY = {1: (5, 43), 2: (5, 23), 3: (3, 3.3), 4: (3, 1.4)}; PH = {1: (55, 67, 76, 83)}

def run(rid):
    d = os.path.join(RUNS, rid)
    try: s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    except Exception: return None
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; T = dv["time"]
    f = edges(t, s[k("nBL")], 0, 1.1, False)
    if not f or t[-1] < f[0] + 1.8e-7: return None          # the reading at 200 ns of the paper's axis needs the first fall + 179 ns
    r = [x for x in edges(t, s[k("nBL")], 0, 1.1, True) if x > f[0]]; tA = f[0] - 3e-10
    ka = next(q for q in dv if q.startswith("AveWindow((0.075") and "ElectrostaticPotential" in q); kc = next(q for q in dv if "ElectrostaticPotential" in q)
    L = lambda x: (at(t, sn, tA) - at(t, sn, x)) * 1e3; R = lambda q, x: (at(T, dv[q], x) - dv[q][0]) * 1e3
    return dict(holes=at(T, dv[next(q for q in dv if "hDensity" in q)], tA) * 1e-13, sn=at(t, sn, tA), avg0=R(ka, tA), avg1=R(ka, f[0] + 5e-10), cen=R(kc, tA),
                l3=L(f[0] + 3e-9), l5=L(f[0] + 5e-9), ph=[L(x - 3e-10) for x in r[:9]], l200=L(f[0] + 179e-9))

for tag in sys.argv[1:]:
    D = {c: run(f"{tag}_c{c}") for c in range(1, 6)}
    if not all(D.values()): print(f"== {tag}: not all five runs are complete"); continue
    print(f"== {tag}   (paper in brackets)")
    print("   case holes | body under the gate, average [mV]: before the fall, 0.25 ns after | centre point before | node [V] | +3 ns  +5 ns | low phase 1 .. 4                 phase 9 | 200 ns")
    for c in range(1, 6):
        o = D[c]; e = EARLY.get(c)
        print(f"   {c}    {o['holes']:5.0f} | {o['avg0']:5.0f} {o['avg1']:5.0f} [{P.FBE_RISE[c]}]" + " " * 34 + f"| {o['cen']:5.0f}" + " " * 15 + f"| {o['sn']:.4f}   | {o['l3']:6.2f} {o['l5']:6.2f}"
              + (f" [{e[1]} at +{e[0]}]" if e else "") + " | " + " ".join(f"{x:7.2f}" for x in o["ph"][:4]) + f"  {o['ph'][8]:7.2f}"
              + (" [" + " ".join(map(str, PH[c])) + "]" if c in PH else f" [{P.FBE_FIRST[c]}]") + f" | {o['l200']:7.2f} [{'on the 1.1 V line' if c in P.FBE_FLAT else P.FBE_200[c]}]")
    for lab, key in (("read just before the fall", "avg0"), ("read 0.25 ns after the fall", "avg1")):
        db = [D[c][key] - P.FBE_RISE[c] for c in range(1, 6)]
        print(f"   bars, {lab}: deviation " + " / ".join(f"{x:+.0f}" for x in db) + f" mV (tolerance {P.FBE_RISE_TOL:.0f}): {sum(abs(x) <= P.FBE_RISE_TOL for x in db)} of 5 inside")
    dec = lambda m, p_: math.log10(max(m, P.FLOOR) / p_)
    d1 = [dec(D[c]["ph"][0], P.FBE_FIRST[c]) for c in range(1, 5)]; d2 = [dec(D[c]["l200"], P.FBE_200[c]) for c in range(1, 5)]; fl = P.FBE_FLAT[5]
    de = [dec(D[c]["l5"] if EARLY[c][0] == 5 else D[c]["l3"], EARLY[c][1]) for c in range(1, 5)]
    print(f"   first low phase: deviation " + " / ".join(f"{x:+.2f}" for x in d1) + f" decades (tolerance {P.DEC_TOL}), Case 5 {D[5]['ph'][0]:.2f} mV (paper: on the 1.1 V line, tolerance {fl} mV): "
          f"{sum(abs(x) <= P.DEC_TOL for x in d1) + (D[5]['ph'][0] <= fl)} of 5 inside")
    print(f"   200 ns: deviation " + " / ".join(f"{x:+.2f}" for x in d2) + f" decades, Case 5 {D[5]['l200']:.2f} mV (paper: on the 1.1 V line, tolerance {fl} mV): {sum(abs(x) <= P.DEC_TOL for x in d2) + (D[5]['l200'] <= fl)} of 5 inside;   3 or 5 ns after the fall: " + " / ".join(f"{x:+.2f}" for x in de)
          + f" decades: {sum(abs(x) <= P.DEC_TOL for x in de)} of 4 inside")
    if all(x == x for x in D[1]["ph"][:4]): print("   Case 1 after low phases 2 - 4: " + " / ".join(f"{x:.0f}" for x in D[1]["ph"][1:4]) + " mV (paper 67 / 76 / 83); Case 4 after two phases: " + f"{D[4]['ph'][1]:.1f} mV (paper 5.2 at 63 ns)")
