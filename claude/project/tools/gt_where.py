# gt_where.py [-a] : round 13 (runs Dp1F / Dp2F_c1..5): back-calculation of WHERE and WHEN Fig.8(a) reads the body potential.
# The hole charge of Cases 1 - 4 is bracketed around the value that gives the paper's loss of the first BL-low phase; the state
# with exactly that loss is interpolated between the two runs of a case (log of the loss). At that state every recorded reading
# of a potential is held against the bars:
#   places   : along the channel every 5 nm at mid-depth and 1 nm under one gate oxide, the older probes, across the thickness;
#              average / minimum / maximum over the body region, average over its gated part and over the part under the
#              BL-side spacer; "saddle" = the lowest mid-depth potential between the two junctions (the top of the barrier
#              the electrons have to cross), computed here from the line of probes;
#   quantity : electrostatic potential (hole quasi-Fermi potential where it was recorded);
#   instants : just before the first BL fall, and 0.25 / 1 / 3 / 5 / 10 ns after the fall is complete (BL low);
#   counted  : from the start of the transient (body without holes) or from t = 0 (after the write).
# Printed: the readings with the smallest largest deviation over Cases 1 - 4, and what each of them says for Case 5 (whose
# state the loss does not fix: the charge at which that reading shows 368 mV). -a: all readings instead of the best 25.
import sys, os, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
PLO = {1: 1.40, 2: 1.32, 3: 1.23, 4: 1.14, 5: 1.00}; PHI = {1: 1.50, 2: 1.42, 3: 1.33, 4: 1.24, 5: 1.15}
AFTER = (0.25, 1.0, 3.0, 5.0, 10.0); INST = ["before the fall"] + [f"BL low +{a:g} ns" for a in AFTER]; Y0 = 0.040

def run(rid):
    d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; T = dv["time"]
    w = edges(t, s[k("nWL)")], 0, 1.8, False); f = edges(t, s[k("nBL")], 0, 1.1, False); r = [x for x in edges(t, s[k("nBL")], 0, 1.1, True) if x > f[0]]
    t0 = w[0] + 4e-11; tA = f[0] - 3e-10; times = [tA] + [f[0] + 2.5e-10 + a * 1e-9 for a in AFTER]
    o = dict(first=(at(t, sn, tA) - at(t, sn, r[0] - 3e-10)) * 1e3, l200=(at(t, sn, tA) - at(t, sn, f[0] + 179e-9)) * 1e3, l5=(at(t, sn, tA) - at(t, sn, f[0] + 5e-9)) * 1e3,
             l3=(at(t, sn, tA) - at(t, sn, f[0] + 3e-9)) * 1e3, ph=[(at(t, sn, tA) - at(t, sn, x - 3e-10)) * 1e3 for x in r[:9]],
             holes=at(T, dv[next(q for q in dv if "hDensity" in q)], tA) * 1e-13, rd={})
    yc = None; line = {}
    for q in dv:
        if not ("ElectrostaticPotential" in q or "hQuasiFermi" in q) or q == "time": continue
        qty = "psi" if "Electrostatic" in q else "phi_p"
        if q.startswith("Pos("):
            x_, y_ = (float(v) for v in q[4:q.index(")")].split(",")[:2])
            if yc is None: yc = y_                                           # the first probe of the deck = body centre
            tb = 2 * (yc - Y0); dep = (y_ - Y0) / tb
            where = "mid-depth" if abs(dep - 0.5) < 1e-3 else f"{(y_ - Y0) * 1e3:.1f} nm under one gate oxide" if dep < 0.5 else f"{(Y0 + tb - y_) * 1e3:.1f} nm under the other gate oxide"
            name = f"x = {x_ * 1e3:5.1f} nm, {where}, {qty}"
            if qty == "psi" and where == "mid-depth": line[x_] = q
        else:
            name = q.replace("ElectrostaticPotential", "psi").replace("hQuasiFermiPotential", "phi_p")
            if name.startswith("AveWindow((0.075"): name = "average over the gated body, " + name.split()[-1]          # the window follows the body thickness: name it by what it is
            elif name.startswith("AveWindow((0.05"): name = "average under the BL-side spacer, " + name.split()[-1]
            elif name.startswith("AveR.Ch_v"): name = "average over the body region, " + name.split()[-1]
            elif name.startswith("MinR.Ch_v"): name = "minimum in the body region, " + name.split()[-1]
            elif name.startswith("MaxR.Ch_v"): name = "maximum in the body region, " + name.split()[-1]
        for ref, base in (("from the start", dv[q][0]), ("from t = 0", at(T, dv[q], t0))):
            o["rd"][f"{name} | {ref}"] = [(at(T, dv[q], x) - base) * 1e3 for x in times]
    xs = sorted(x for x in line if 0.0505 <= x <= 0.1745)                    # between the two junctions (50 and 175 nm)
    if len(xs) > 5:
        sad = lambda x: min(at(T, dv[line[u]], x) for u in xs); loc = lambda x: min(xs, key=lambda u: at(T, dv[line[u]], x)) * 1e3
        s0 = min(dv[line[u]][0] for u in xs)
        o["rd"]["saddle (lowest mid-depth potential between the junctions), psi | from the start"] = [(sad(x) - s0) * 1e3 for x in times]
        o["rd"]["saddle (lowest mid-depth potential between the junctions), psi | from t = 0"] = [(sad(x) - sad(t0)) * 1e3 for x in times]
        o["saddle_x"] = [loc(x) for x in times]
    return o

D = {c: (run(f"Dp1F_c{c}"), run(f"Dp2F_c{c}")) for c in range(1, 6)}
print("runs: charge (x bar charge), holes at t_A, loss +3 / +5 ns, first low phase, 200 ns [mV] (paper first phase / 200 ns in brackets)")
for c in range(1, 6):
    for f_, o in zip((PLO[c], PHI[c]), D[c]):
        print(f"   Case {c} x{f_:.2f}: {o['holes']:5.0f} holes | {o['l3']:6.2f} {o['l5']:6.2f} | {o['first']:7.2f} ({P.FBE_FIRST[c]}) | {o['l200']:7.2f} ({P.FBE_200[c]})"
              + (f" | saddle at x = {o['saddle_x'][0]:.1f} nm before the fall, {o['saddle_x'][4]:.1f} nm with the BL low" if "saddle_x" in o else ""))
W = {}
for c in range(1, 5):
    a, b = D[c]; W[c] = (math.log(P.FBE_FIRST[c]) - math.log(a["first"])) / (math.log(b["first"]) - math.log(a["first"]))
st = lambda c, key: D[c][0][key] * (1 - W[c]) + D[c][1][key] * W[c]
print("state with the paper's first-phase loss: charge x " + " / ".join(f"{PLO[c] * (1 - W[c]) + PHI[c] * W[c]:.2f}" for c in range(1, 5)) + ", holes " + " / ".join(f"{st(c, 'holes'):.0f}" for c in range(1, 5))
      + "; 200 ns loss there " + " / ".join(f"{math.exp(math.log(D[c][0]['l200']) * (1 - W[c]) + math.log(D[c][1]['l200']) * W[c]):.1f}" for c in range(1, 5)) + " (paper 100 / 50 / 14.6 / 7)")
rows = []
for n in D[1][0]["rd"]:
    if any(n not in D[c][k]["rd"] for c in range(1, 6) for k in (0, 1)): continue
    for j, lab in enumerate(INST):
        v = [D[c][0]["rd"][n][j] * (1 - W[c]) + D[c][1]["rd"][n][j] * W[c] for c in range(1, 5)]
        d_ = [v[c - 1] - P.FBE_RISE[c] for c in range(1, 5)]
        a5, b5 = D[5][0]["rd"][n][j], D[5][1]["rd"][n][j]; f5 = PLO[5] + (PHI[5] - PLO[5]) * (P.FBE_RISE[5] - a5) / (b5 - a5) if abs(b5 - a5) > 1e-9 else float("nan")
        rows.append((max(abs(x) for x in d_), n, lab, v, d_, a5, b5, f5))
rows.sort(key=lambda r_: r_[0])
print()
print(f"readings at that state [mV] against the bars 555 / 445 / 365 / 320 (tolerance {P.FBE_RISE_TOL:.0f} mV); Case 5: reading at x 1.00 / x 1.15, and the charge at which it shows 368")
for w_, n, lab, v, d_, a5, b5, f5 in (rows if "-a" in sys.argv else rows[:25]):
    print(f"   worst {w_:4.0f} | " + " ".join(f"{x:5.0f}" for x in v) + " (" + " ".join(f"{x:+4.0f}" for x in d_) + f") | Case 5: {a5:4.0f} / {b5:4.0f} -> x {f5:4.2f} | {n}, {lab}")
print(f"   {sum(1 for r_ in rows if r_[0] <= P.FBE_RISE_TOL)} of {len(rows)} readings are within {P.FBE_RISE_TOL:.0f} mV in Cases 1 - 4")
print()
print("named readings:")
for key in ("x = 125.0 nm, mid-depth, psi", "average over the gated body, psi", "average over the body region, psi", "average under the BL-side spacer, psi", "minimum in the body region", "average over the gated body, phi_p", "saddle"):      # body centre; averages over the body region, its gated part, the part under the BL-side spacer; extrema; hole quasi-Fermi potential; barrier top
    for w_, n, lab, v, d_, a5, b5, f5 in rows:
        if key in n and "from the start" in n and lab in ("before the fall", "BL low +1 ns", "BL low +5 ns", "BL low +10 ns"):
            print(f"   worst {w_:4.0f} | " + " ".join(f"{x:5.0f}" for x in v) + " (" + " ".join(f"{x:+4.0f}" for x in d_) + f") | Case 5: {a5:4.0f} / {b5:4.0f} -> x {f5:4.2f} | {n}, {lab}")

# The other way round, for the reading that is a definition one would write down (average potential of the body under the
# gate, counted from the start of the transient): the charge at which that reading shows the bar, case by case, and the losses
# that state would have (interpolated or extrapolated between the two runs of the case; '*' = outside them).
print()
print("charge sized to the bars with the reading 'average over the gated body': predicted losses [mV] (paper in brackets, deviation in decades)")
key = "average over the gated body, psi | from the start"
for j, lab in enumerate(INST):
    if lab not in ("before the fall", "BL low +0.25 ns", "BL low +1 ns"): continue
    out = []
    for c in range(1, 6):
        a, b = D[c]; ra, rb = a["rd"][key][j], b["rd"][key][j]; w = (P.FBE_RISE[c] - ra) / (rb - ra); f_ = PLO[c] + (PHI[c] - PLO[c]) * w
        lg = lambda k_: math.exp(math.log(a[k_]) * (1 - w) + math.log(b[k_]) * w)
        l1, l2 = lg("first"), lg("l200"); dev = lambda m, p_: f"{math.log10(m / p_):+.2f}" if p_ > 0 else "  -  "
        out.append(f"Case {c}: x{f_:.2f}{'' if 0 <= w <= 1 else '*'} {a['holes'] * (1 - w) + b['holes'] * w:5.0f} holes, first {l1:6.2f} ({P.FBE_FIRST[c]}, {dev(l1, P.FBE_FIRST[c])}), 200 ns {l2:6.1f} ({P.FBE_200[c]}, {dev(l2, P.FBE_200[c])})")
    print(f"   read {lab}:"); [print("      " + x) for x in out]
