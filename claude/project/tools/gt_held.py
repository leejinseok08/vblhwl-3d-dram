# gt_held.py : round 12 (runs Dn1F .. Dn4F_c1..5): the body charged by the model's own generation while the storage node is held
# at 1.1 V (hold 15.2 / 18 / 20 / 22 us, node released 0.5 ns before the first BL fall), then the whole BL waveform of Fig.8(b).
# The question: does ONE such state give the bars of Fig.8(a) and the curves of Fig.8(b), (c) together?
#   A  every run: state at t_A (node, holes, body rise), rise in the last 21 ns of the hold, losses 3 / 5 ns after the fall,
#      after low phases 1 .. 4 and 9, at 200 ns of the paper's axis;
#   B  Q1: the hold at which the first-phase loss is the paper's, case by case, and the one common hold that fits the cases best;
#   C  Q2: the curve at that common hold against the points read from Fig.8(b), (c);
#   D  Q3: every reading of a "body potential" at that hold (along the channel and across the thickness, electrostatic and hole
#      quasi-Fermi potential, from the start of the transient and from t = 0) against the bars;
#   E  Q4: the same body rise reached by the stand-in supply (Dh1F .. Dh4F): are the losses the same, also after the first phase?
#   (Q5, the rise in the last 21 ns of the hold, is a column of A.)
# Runs that have not come as far as a reading are left out of it. GT_RUNS: another runs folder.
import sys, os, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
HOLD = (("Dn1F", 15.2), ("Dn2F", 18.0), ("Dn3F", 20.0), ("Dn4F", 22.0)); STAND = ("Dh1F", "Dh2F", "Dh3F", "Dh4F")
EARLY = {1: (5, 43), 2: (5, 23), 3: (3, 3.3), 4: (3, 1.4)}; PH = {1: (55, 67, 76, 83)}; Y0 = 0.040      # body starts 40 nm above the layer's mid-plane (Dvox / 2 + Tgm + Tox)

def run(rid):
    d = os.path.join(RUNS, rid)
    try: s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    except Exception: return None
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; T = dv["time"]
    w = edges(t, s[k("nWL)")], 0, 1.8, False); f = edges(t, s[k("nBL")], 0, 1.1, False)
    if not w or not f or t[-1] < f[0] + 1e-9: return None
    r = [x for x in edges(t, s[k("nBL")], 0, 1.1, True) if x > f[0]]; t0 = w[0] + 4e-11; tA = f[0] - 3e-10; end = min(t[-1], T[-1])
    L = lambda x: (at(t, sn, tA) - at(t, sn, x)) * 1e3 if x <= end else float("nan")
    hol = lambda x: at(T, dv[next(q for q in dv if "hDensity" in q)], x) * 1e-13
    o = dict(sn=at(t, sn, tA), holes=hol(tA), L3=L(f[0] + 3e-9), L5=L(f[0] + 5e-9), ph=[L(x - 3e-10) for x in r[:9]] + [float("nan")] * (9 - len(r[:9])),
             L200=L(f[0] + 179e-9), hph=[hol(x - 3e-10) if x <= end else float("nan") for x in r[:9]], probe={})
    pos = sorted({q.split()[0] for q in dv if q.startswith("Pos(")}); yc = float(next(q for q in dv if q.startswith("Pos(0.125")).split(",")[1].rstrip(") ElectrostaticPotential").split(")")[0])
    tb = 2 * (yc - Y0)
    for q in dv:
        if not (q.startswith("Pos(") and ("ElectrostaticPotential" in q or "hQuasiFermi" in q)): continue
        x_, y_ = (float(v) for v in q[4:q.index(")")].split(",")[:2]); qty = "psi" if "Electrostatic" in q else "phi_p"
        dep = (y_ - Y0) / tb; where = "mid-depth" if abs(dep - 0.5) < 1e-3 else f"{(y_ - Y0) * 1e3:.1f} nm from one gate oxide" if dep < 0.5 else f"{(Y0 + tb - y_) * 1e3:.1f} nm from the other gate oxide"
        for ref, base in (("from the start", dv[q][0]), ("from t = 0", at(T, dv[q], t0))):
            o["probe"][f"x = {x_ * 1e3:5.1f} nm, {where}, {qty}, {ref}"] = (at(T, dv[q], tA) - base) * 1e3
    kc = next(q for q in dv if q.startswith("Pos(0.125") and "Electrostatic" in q and abs(float(q[4:q.index(")")].split(",")[1]) - yc) < 1e-9)
    o["rise"] = (at(T, dv[kc], tA) - dv[kc][0]) * 1e3; o["last21"] = (at(T, dv[kc], tA) - at(T, dv[kc], tA - 21e-9)) * 1e3
    return o

N = {c: [(h, run(f"{tag}_c{c}")) for tag, h in HOLD] for c in range(1, 6)}
S = {c: [o for o in (run(f"{tag}_c{c}") for tag in STAND) if o] for c in range(1, 6)}
f2 = lambda x, w=7: f"{x:{w}.2f}" if x == x else " " * (w - 1) + "-"
print("A. own generation, node held at 1.1 V through the hold, then the waveform of Fig.8(b). Losses in mV against the node at t_A")
print("case hold[us] node[V]  holes  rise[mV]  last 21 ns | +3 ns   +5 ns | after low phase 1 .. 4            phase 9 | 200 ns")
for c in range(1, 6):
    for h, o in N[c]:
        if not o: print(f"{c:3d}  {h:5.1f}   (no reading yet)"); continue
        print(f"{c:3d}  {h:5.1f}   {o['sn']:.4f} {o['holes']:6.0f} {o['rise']:8.0f}  {o['last21']:+7.2f} mV | {f2(o['L3'])} {f2(o['L5'])} | " + " ".join(f2(x) for x in o["ph"][:4]) + f"  {f2(o['ph'][8])} | {f2(o['L200'])}")
    e = EARLY.get(c); ph = PH.get(c, (P.FBE_FIRST[c],))
    print(f"     paper   1.1000        {P.FBE_RISE[c]:8d}               | " + (f"{e[1]:5.1f} at +{e[0]} ns  " if e else " " * 16) + "| " + " ".join(f"{x:7.1f}" for x in ph) + " " * (8 * (4 - len(ph))) + f"          | {P.FBE_200[c]:7.1f}")

def interp(c, key, h, log=True):
    """value at hold h between the two nearest runs that have it (log-linear for losses, linear else); None if fewer than two"""
    pts = [(hh, key(o)) for hh, o in N[c] if o and key(o) == key(o) and (not log or key(o) > 0)]
    if len(pts) < 2: return None
    i = max(0, min(len(pts) - 2, next((k for k in range(len(pts) - 1) if h <= pts[k + 1][0]), len(pts) - 2)))
    (h1, v1), (h2, v2) = pts[i], pts[i + 1]; w = (h - h1) / (h2 - h1)
    return math.exp(math.log(v1) * (1 - w) + math.log(v2) * w) if log else v1 * (1 - w) + v2 * w

first = lambda o: o["ph"][0]
print()
print("B. Q1: which hold gives the paper's loss of the first low phase (interpolated between the runs; '>' / '<' = outside 15.2 .. 22 us)")
grid = [15.2 + i * 0.05 for i in range(137)]; need = {}
for c in range(1, 5):
    v = [interp(c, first, h) for h in grid]
    if v[0] is None: print(f"   Case {c}: not enough runs yet"); continue
    j = next((i for i in range(len(grid)) if v[i] >= P.FBE_FIRST[c]), None)
    need[c] = "> 22" if j is None else "< 15.2" if j == 0 else f"{grid[j]:.1f}"
    print(f"   Case {c}: paper {P.FBE_FIRST[c]:5.1f} mV; model {v[0]:6.2f} mV at 15.2 us .. {v[-1]:7.2f} mV at 22 us; the paper's value at a hold of {need[c]} us")
ok = [c for c in range(1, 5) if interp(c, first, 18.0) is not None]
if ok:
    dev = lambda h: max(abs(math.log10(interp(c, first, h) / P.FBE_FIRST[c])) for c in ok)
    hb = min(grid, key=dev)
    print(f"   one common hold, Cases {' '.join(map(str, ok))}: best at {hb:.1f} us, largest deviation {dev(hb):.2f} decades (tolerance {P.DEC_TOL}): "
          + ", ".join(f"Case {c} {interp(c, first, hb):.1f} mV ({interp(c, first, hb) / P.FBE_FIRST[c]:.2f} x)" for c in ok)
          + (f"; Case 5 {interp(5, first, hb):.2f} mV (paper 0)" if interp(5, first, hb) is not None else ""))
    print()
    print(f"C. Q2: the curve at the common hold of {hb:.1f} us [mV] (paper in brackets)")
    for c in range(1, 6):
        if interp(c, first, hb) is None: continue
        e = EARLY.get(c); ke = (lambda o: o["L5"]) if e and e[0] == 5 else (lambda o: o["L3"])
        g = lambda key, log=True: interp(c, key, hb, log)
        row = f"   Case {c}: body rise {g(lambda o: o['rise'], False):4.0f} ({P.FBE_RISE[c]}), holes {g(lambda o: o['holes'], False):5.0f}"
        if e and g(ke) is not None: row += f", +{e[0]} ns {g(ke):5.1f} ({e[1]})"
        row += f", first phase {g(first):6.2f} ({P.FBE_FIRST[c]})"
        if c in PH and g(lambda o: o["ph"][3]) is not None: row += ", phases 2 - 4 " + " / ".join(f"{g(lambda o, j=j: o['ph'][j]):.0f}" for j in (1, 2, 3)) + " (" + " / ".join(map(str, PH[c][1:])) + ")"
        if c == 4 and g(lambda o: o["ph"][1]) is not None: row += f", after two phases {g(lambda o: o['ph'][1]):.1f} (5.2 at 63 ns)"
        if g(lambda o: o["L200"]) is not None: row += f", 200 ns {g(lambda o: o['L200']):6.1f} ({P.FBE_200[c]})"
        print(row)
    print()
    print(f"D. Q3: every reading of a body potential at the common hold of {hb:.1f} us [mV] against the bars 555 / 445 / 365 / 320 / 368 (tolerance {P.FBE_RISE_TOL:.0f} mV)")
    names = [n for n in next(o for _, o in N[1] if o)["probe"]]; rows = []
    for n in names:
        v = [interp(c, lambda o, n=n: o["probe"].get(n, float("nan")), hb, False) for c in range(1, 6)]
        if any(x is None for x in v): continue
        d_ = [v[c - 1] - P.FBE_RISE[c] for c in range(1, 6)]; rows.append((max(abs(x) for x in d_), n, v, d_))
    for worst, n, v, d_ in sorted(rows)[:12]:
        print(f"   largest deviation {worst:4.0f} mV  " + " ".join(f"{x:5.0f}" for x in v) + "   (" + " ".join(f"{x:+4.0f}" for x in d_) + f")   {n}")
    print(f"   readings within {P.FBE_RISE_TOL:.0f} mV in all five cases: " + (", ".join(n for w_, n, _, _ in rows if w_ <= P.FBE_RISE_TOL) or "none") + f"   ({len(rows)} readings held against the bars)")

def stand(c, rise, key):
    """the stand-in states of this case at this body rise (log-linear in the rise between the two nearest; '*' = outside the grid)"""
    r_ = [o["rise"] for o in S[c]]
    if len(r_) < 2: return float("nan"), ""
    i = max(0, min(len(r_) - 2, next((k for k in range(len(r_) - 1) if rise <= r_[k + 1]), len(r_) - 2))); w = (rise - r_[i]) / (r_[i + 1] - r_[i])
    return math.exp(math.log(key(S[c][i])) * (1 - w) + math.log(key(S[c][i + 1])) * w), ("" if r_[0] <= rise <= r_[-1] else "*")
print()
print("E. Q4: own generation (this round) / stand-in supply (Dh runs) at the same body rise: loss after phase 1, after phase 4, at 200 ns [mV]")
for c in range(1, 6):
    for h, o in N[c]:
        if not o: continue
        print(f"   Case {c}, hold {h:4.1f} us, rise {o['rise']:4.0f} mV: " + "   ".join(
            f"{lab} {f2(key(o), 6)} / {'%6.2f%s' % stand(c, o['rise'], key)}" for lab, key in (("phase 1", first), ("phase 4", lambda o: o["ph"][3]), ("200 ns", lambda o: o["L200"]))))
