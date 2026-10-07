# gt_hsu_fig2c.py <run dir> ... : Id-Vg runs against the SILICON reference transistor of Hsu, Cho, Sharda, Park, Datta, Yu (IMW 2025
# Fig.2(c); the same figure in TED 73(9), 2026): "simulated silicon channel (L = 100 nm)", L 100 nm, t_Si 10 nm, W 100 nm, V_DS = 1 V,
# drain current in A/um. The inset of that figure is the cell drawing of Cho et al. (IRPS 2026): same authors' group, same TCAD cell.
# HSU = the blue curve read off the embedded image of the TED paper (970 x 920; frame x 146 .. 917 = Vg -2 .. 2.5 V, y 420 .. 806 =
# 1e-2 .. 1e-16 A/um: 0.036 decade and 0.006 V per pixel; the line is 5 - 16 pixels thick, so about +-0.1 decade on the steep part).
# Per run: log10 I [A/um] at the same gate voltages and the difference, the gate voltage at 1e-9 / 1e-7 / 1e-5 A/um, the slope and
# the minimum. The 2D current of the runs is per um of width already (GT_W = 1).
import sys, os, math
os.environ["GT_W"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gt_fig5c as G
HSU = {-1.75: -12.05, -1.50: -12.56, -1.25: -13.17, -1.00: -14.04, -0.90: -14.56, -0.80: -15.18, -0.70: -15.84, -0.50: -15.20, -0.40: -13.56,
       -0.30: -11.93, -0.20: -10.19, -0.10: -8.56, 0.00: -6.89, 0.10: -5.36, 0.20: -4.34, 0.30: -3.80, 0.50: -3.26, 1.00: -2.83, 1.50: -2.71,
       2.00: -2.65, 2.40: -2.60}
def cross(pts, lev):                          # Vg where the curve of {Vg: log10 I} crosses lev on the rising branch
    v = sorted(pts); k = min(range(len(v)), key=lambda j: pts[v[j]])
    for a, b in zip(v[k:], v[k + 1:]):
        if pts[a] < lev <= pts[b]: return a + (b - a) * (lev - pts[a]) / (pts[b] - pts[a])
hv = [cross(HSU, l) for l in (-9, -7, -5)]
print("Vg [V]          " + " ".join(f"{v:+6.2f}" for v in HSU))
print("Hsu Fig.2(c)    " + " ".join(f"{l:6.2f}" for l in HSU.values()) + f"   | Vg at 1e-9 / 1e-7 / 1e-5 A/um: {hv[0]:+.3f} / {hv[1]:+.3f} / {hv[2]:+.3f} V, {(hv[1] - hv[0]) / 2 * 1e3:.1f} mV/dec; minimum under 1e-16 near -0.6 V")
for rd in sys.argv[1:]:
    name = os.path.basename(rd.rstrip("/\\"))
    try: pts = G.curve(rd)
    except Exception as e: print(f"{name:15s} no curve ({e})"); continue
    m = [G.at(pts, v) for v in HSU]; k = min(range(len(pts)), key=lambda j: pts[j][1])
    c = [G.cross(pts, 10.0 ** l) for l in (-9, -7, -5)]
    print(f"{name:15s} " + " ".join("     -" if x is None else f"{x:6.2f}" for x in m) + "   | " + " / ".join("  -  " if x is None else f"{x:+.3f}" for x in c)
          + (f" V, {(c[1] - c[0]) / 2 * 1e3:.1f} mV/dec" if None not in c[:2] else "") + f"; minimum {math.log10(pts[k][1]):.2f} at {pts[k][0]:+.2f} V; Vg {pts[0][0]:+.2f} .. {pts[-1][0]:+.2f}")
    print(f"{'  minus Hsu':15s} " + " ".join("     -" if x is None else f"{x - l:+6.2f}" for x, l in zip(m, HSU.values()))
          + ("   | " + " / ".join(f"{a - b:+.3f}" for a, b in zip(c, hv)) + " V" if None not in c else ""))
