# gt_hold.py <run dir> ... : hold-state runs (deck_cho test H: BL and storage node driven to Vdd in 15 ps, WL 0) in one line
# each: time reached, steps; the step of the body potential while BL and SN go up (coupling, no charge); its rise after that
# (t0 = 16 ps = cell charged, WL off = "t = 0" of Fig.8) to 1 / 5 / 10 / 16 / 21 ns; the tunnelling generation as a current
# per cell at 1 and 16 ns. Probe = body centre under the gate (first potential probe of the deck).
# Paper, Fig.8(a), body potential rise t = 0 -> t_A (first BL fall, 21.0 ns in Fig.8(b)), Cases 1-5: 555 / 445 / 365 / 320 / 368 mV.
# The 2D generation integral [cm^-3 s^-1 um^2] x width 0.1 um x 1e-12 cm^3/um^3 x q is the current of the 100 nm wide cell.
import sys, os, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at
PAPER = {1: 555, 2: 445, 3: 365, 4: 320, 5: 368}
T = (1e-9, 5e-9, 1e-8, 1.6e-8, 2.1e-8); T0 = 1.6e-11
print("run            t [ns] steps | coupling | body rise [mV] after t0, at 1 / 5 / 10 / 16 / 21 ns | paper | generation [nA] at 1, 16 ns")
for rd in sys.argv[1:]:
    rid = os.path.basename(rd.rstrip("/")); d = glob.glob(os.path.join(rd, "*_dev.plt"))
    try: dv = load(d[0])
    except Exception as e:
        print(f"{rid:14s} no data"); continue
    t = dv["time"]; kv = next(k for k in dv if "ElectrostaticPotential" in k); kg = next(k for k in dv if "Band2Band" in k)
    v00 = dv[kv][0]; v0 = at(t, dv[kv], T0); m = re.search(r"_c(\d)", rid); c = int(m.group(1)) if m else 0
    rise = " ".join(f"{(at(t, dv[kv], x) - v0) * 1e3:6.0f}" if t[-1] >= x - 1e-12 else "     -" for x in T)
    gen = " ".join(f"{at(t, dv[kg], x) * 0.1 * 1e-12 * 1.602e-19 * 1e9:8.3f}" if t[-1] >= x else "       -" for x in (1e-9, 1.6e-8))
    print(f"{rid:14s} {t[-1] * 1e9:6.2f} {len(t):5d} | {(v0 - v00) * 1e3:8.0f} | {rise} | {PAPER.get(c, 0):4d} | {gen}")
