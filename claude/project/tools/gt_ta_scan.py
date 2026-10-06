# gt_ta_scan.py : back-calculation of WHEN Fig.8(a) reads the body potential. For the charged-body runs Dh1F .. Dh4F (stand-in
# charge x 1.0 / 1.25 / 1.5 / 2.0, node at 1.1 V, the paper's BL waveform) the rise of the body-centre potential above the start
# of the transient is printed at instants around the first BL fall: just before it (the reading used so far), and 0.25 / 1 / 3 /
# 5 / 10 ns after the fall is complete, i.e. with the BL low. Then, per case, the state that gives the paper's first-phase loss
# (interpolated in the charge, as tools/gt_charged_t0.py does): the rise at each of those instants against the bar. If the
# bars were read with the BL already low, one instant should give all bars at the states that give the losses.
import sys, os, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
TAGS = (("Dh1F", 1.0), ("Dh2F", 1.25), ("Dh3F", 1.5), ("Dh4F", 2.0)); AFTER = (0.25, 1.0, 3.0, 5.0, 10.0)

def run(rid):
    d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; T = dv["time"]
    f = edges(t, s[k("nBL")], 0, 1.1, False); r = [x for x in edges(t, s[k("nBL")], 0, 1.1, True) if x > f[0]]; tA = f[0] - 3e-10; lowT = f[0] + 2.5e-10   # the fall is complete
    o = dict(first=(at(t, sn, tA) - at(t, sn, r[0] - 3e-10)) * 1e3, pr={})
    for q in dv:
        if q.startswith("Pos(") and ("ElectrostaticPotential" in q or "hQuasiFermi" in q):
            n = "x = " + q[4:q.index(",")] + " um " + ("psi" if "Electrostatic" in q else "phi_p")
            o["pr"][n] = [(at(T, dv[q], tA) - dv[q][0]) * 1e3] + [(at(T, dv[q], lowT + a * 1e-9) - dv[q][0]) * 1e3 for a in AFTER]
    return o

D = {c: [run(f"{tag}_c{c}") for tag, _ in TAGS] for c in range(1, 6)}
kc = "x = 0.125 um psi"
print("rise of the body-centre potential above the start of the transient [mV]: before the first BL fall | with the BL low, after " + " / ".join(f"{a:g}" for a in AFTER) + " ns")
for c in range(1, 6):
    for (tag, fac), o in zip(TAGS, D[c]):
        v = o["pr"][kc]; print(f"  Case {c} x{fac:<5} first-phase loss {o['first']:7.2f} mV | {v[0]:5.0f} | " + " ".join(f"{x:5.0f}" for x in v[1:]) + f"   (drop at the fall {v[1] - v[0]:+.0f} mV)")
print()
print("at the state that gives the paper's first-phase loss (Cases 1 - 4): reading [mV] at each instant, deviation from the bars in brackets")
M = {}
for c in range(1, 5):
    y = [o["first"] for o in D[c]]; i = next(k for k in range(3) if y[k] <= P.FBE_FIRST[c] <= y[k + 1]); M[c] = (i, (math.log(P.FBE_FIRST[c]) - math.log(y[i])) / (math.log(y[i + 1]) - math.log(y[i])))
rows = []
for n in D[1][0]["pr"]:
    for j, lab in enumerate(["before the fall"] + [f"BL low, +{a:g} ns" for a in AFTER]):
        v = [D[c][M[c][0]]["pr"][n][j] * (1 - M[c][1]) + D[c][M[c][0] + 1]["pr"][n][j] * M[c][1] for c in range(1, 5)]
        d_ = [v[c - 1] - P.FBE_RISE[c] for c in range(1, 5)]; rows.append((max(abs(x) for x in d_), n, lab, v, d_))
for w, n, lab, v, d_ in sorted(rows)[:14]:
    print(f"   largest deviation {w:4.0f} mV   " + " ".join(f"{x:5.0f}" for x in v) + "   (" + " ".join(f"{x:+4.0f}" for x in d_) + f")   {n}, {lab}")
print("   bars:                        " + " ".join(f"{P.FBE_RISE[c]:5d}" for c in range(1, 5)) + f"   tolerance {P.FBE_RISE_TOL:.0f} mV")
