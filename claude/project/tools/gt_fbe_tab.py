# gt_fbe_tab.py <run prefix> ... : FBE runs of the five cases in one table per prefix (runs/<prefix>_c1 .. _c5), against Fig.8.
# Columns: time reached; holes in the body after the write and before the first BL fall (t_A); at the body centre under the
# gate, t = 0 (before the write) -> t_A: rise of the electrostatic potential psi, and the hole quasi-Fermi potential phi_p at
# t_A minus psi at t = 0 (the reading of Fig.8(a) that needs only a few holes, NOTES (au)); storage-node change in the hold
# (after the write -> t_A), loss in the first low phase, loss at 200 ns (* = at the end of a shorter run).
# Paper (Fig.8): body rise 555 / 445 / 365 / 320 / 368 mV; first low phase about 55 / 29 / 7 / 3.5 / 0 mV; at 200 ns 100 / 50 /
# 14.6 / 7 / 1 mV; no droop in the hold that could be read (Case 3: 3.3 mV at 24 ns, Case 4: 1.4 mV).
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
PAP = {1: (555, 55, 100), 2: (445, 29, 50), 3: (365, 7, 14.6), 4: (320, 3.5, 7), 5: (368, 0, 1)}
runs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
for pre in sys.argv[1:]:
    print(f"== {pre}   (paper in brackets)")
    print("   case  t[ns] | holes: written   t_A | t=0 -> t_A [mV]: psi rise, phi_p(t_A) - psi(0) | SN [mV]: hold, 1st low phase, at 200 ns")
    for c in (1, 2, 3, 4, 5):
        rid = f"{pre}_c{c}"; rd = os.path.join(runs, rid)
        try: s = load(os.path.join(rd, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(rd, "*_dev.plt"))[0])
        except Exception: print(f"   {c}     no data"); continue
        t = s["time"]; key = lambda n: next(k for k in s if n in k); sn, bl, wl = s[key("nSN)")], s[key("nBL")], s[key("nWL)")]
        tw0 = edges(t, wl, 0, 1.8, False); f = edges(t, bl, 0, 1.1, False); r = [x for x in edges(t, bl, 0, 1.1, True) if f and x > f[0]]
        if not tw0 or t[-1] < tw0[0] + 1e-10: print(f"   {c}   {t[-1] * 1e9:6.2f} | write not finished"); continue
        T = dv["time"]; kv = [k for k in dv if "ElectrostaticPotential" in k][0]; kp = [k for k in dv if "hQuasiFermi" in k][0]; kh = [k for k in dv if "hDensity" in k][0]
        t1 = tw0[0] + 4e-11; t2 = (f[0] - 3e-10) if f else t[-1]; nh = lambda x: at(T, dv[kh], x) * 0.1 * 1e-12
        t3 = (r[0] - 3e-10) if r else None; v2 = at(t, sn, t2)
        lo = f"{(v2 - at(t, sn, t3)) * 1e3:6.2f}" if t3 else "     -"; te = min(t[-1], 2e-7)
        print(f"   {c}   {t[-1] * 1e9:6.1f} | {nh(t1):8.2f} {nh(t2):8.1f} | {(at(T, dv[kv], t2) - at(T, dv[kv], 0)) * 1e3:+6.0f} {(at(T, dv[kp], t2) - at(T, dv[kv], 0)) * 1e3:+6.0f}  [{PAP[c][0]}] | "
              f"{(v2 - at(t, sn, t1)) * 1e3:+7.2f}  {lo} [{PAP[c][1]}]  {(v2 - at(t, sn, te)) * 1e3:7.2f}{'' if t[-1] >= 2e-7 else '*'} [{PAP[c][2]}]" + ("" if f else "   (hold not finished)"))
