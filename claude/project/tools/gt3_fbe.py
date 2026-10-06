# gt3_fbe.py <run id> ... : FBE runs of the 3D unit cell (E3F_c2, E3F125_c2, ..) and 2D runs (Dh1F_c2, ..) read the same way, side
# by side: state at t_A (node, holes in the body, body-centre rise from the start of the transient and from t = 0) and the loss
# of the storage node 3 / 5 ns after the first BL fall, after every BL-low phase the run has reached, and at 200 ns of the
# paper's axis. Works on running jobs (what is not reached yet is "-").
# Holes: integral of the hole density over the body region; 2D: x 1e-13 (um^2 -> cm^2, width 0.1 um); 3D: x 2e-12 (um^3 -> cm^3,
# half cell x 2). The body probe is the first ElectrostaticPotential of the deck (body centre) in both.
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
f2 = lambda x, w=7: f"{x:{w}.2f}" if x == x else " " * (w - 1) + "-"
print("run          dim | node at t_A  holes  rise from start / from t = 0 [mV] | +3 ns   +5 ns | after low phase 1 .. 9 [mV]" + " " * 44 + "| 200 ns")
for rid in sys.argv[1:]:
    d = os.path.join(RUNS, rid)
    try: s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    except Exception: print(f"{rid:12s} no data"); continue
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; T = dv["time"]
    kc = next(x for x in dv if "ElectrostaticPotential" in x); kh = next(x for x in dv if "hDensity" in x); three = kc.count(",") == 2
    w = edges(t, s[k("nWL)")], 0, 1.8, False); f = edges(t, s[k("nBL")], 0, 1.1, False)
    if not w: print(f"{rid:12s} {'3D' if three else '2D'}  | still writing: t = {t[-1] * 1e12:.0f} ps, node {sn[-1]:.4f} V"); continue
    t0 = w[0] + 4e-11; hf = 2e-12 if three else 1e-13; end = min(t[-1], T[-1])
    if not f or end < f[0]:
        print(f"{rid:12s} {'3D' if three else '2D'}  | in the hold: t = {end * 1e9:.2f} ns, node {at(t, sn, end):.4f} V, holes {at(T, dv[kh], end) * hf:.0f}, "
              f"rise {(at(T, dv[kc], end) - dv[kc][0]) * 1e3:+.0f} / {(at(T, dv[kc], end) - at(T, dv[kc], t0)) * 1e3:+.0f} mV"); continue
    r = [x for x in edges(t, s[k("nBL")], 0, 1.1, True) if x > f[0]]; tA = f[0] - 3e-10
    L = lambda x: (at(t, sn, tA) - at(t, sn, x)) * 1e3 if x <= end else float("nan")
    ph = [L(x - 3e-10) for x in r[:9]] + [float("nan")] * (9 - len(r[:9]))
    print(f"{rid:12s} {'3D' if three else '2D'}  | {at(t, sn, tA):.4f} V {at(T, dv[kh], tA) * hf:6.0f}  {(at(T, dv[kc], tA) - dv[kc][0]) * 1e3:+6.0f} / {(at(T, dv[kc], tA) - at(T, dv[kc], t0)) * 1e3:+6.0f}"
          + " " * 14 + f"| {f2(L(f[0] + 3e-9))} {f2(L(f[0] + 5e-9))} | " + " ".join(f2(x) for x in ph) + f" | {f2(L(f[0] + 179e-9))}   (now at {end * 1e9:.1f} ns)")
c = 2
print(f"paper Case {c}:      rise {P.FBE_RISE[c]} mV | +5 ns 23 mV | first low phase {P.FBE_FIRST[c]} mV | 200 ns {P.FBE_200[c]} mV")
