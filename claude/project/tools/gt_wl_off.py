# gt_wl_off.py <run id> ... : the write and the WL switch-off of deck_cho runs in one line each - storage node at 12 / 24 / 39 /
# 60 ps after the WL rises (Fig.4(a): 0.72 / 0.92 / 1.06 / 1.13 V), its value before and after the WL falls, the pairs made by
# impact ionization during the write and during the fall, the holes left in the body, and where the body centre and the
# storage node stand at the end of the hold (first BL fall or end of the run). For the impact-ionization factor runs.
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
print("run          SN at 12/24/39/60 ps [V]      | SN before -> after WL off | pairs: write + fall | holes left | at t_A: holes, body rise [mV], SN change in the hold [mV]")
for rid in sys.argv[1:]:
    d = os.path.join(RUNS, rid)
    try: s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    except Exception: print(f"{rid:12s} no data"); continue
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn, wl, bl = s[k("nSN)")], s[k("nWL)")], s[k("nBL")]
    up = edges(t, wl, 0, 1.8, True); dn = edges(t, wl, 0, 1.8, False)
    if not up: print(f"{rid:12s} WL has not risen yet"); continue
    T = dv["time"]; kh = next(x for x in dv if "hDensity" in x); ka = next(x for x in dv if "Avalanche" in x or "ImpactIonization" in x); kc = next(x for x in dv if "ElectrostaticPotential" in x)
    made = [0.0]
    for i in range(1, len(T)): made.append(made[-1] + 0.5 * (dv[ka][i] + dv[ka][i - 1]) * (T[i] - T[i - 1]) * 1e-13)
    w = " / ".join(f"{at(t, sn, up[0] + p * 1e-12):.2f}" for p in (12, 24, 39, 60))
    if not dn: print(f"{rid:12s} {w}   | WL still high"); continue
    b, a = dn[0] - 3.5e-12, dn[0] + 6e-12; f = edges(t, bl, 0, 1.1, False); te = (f[0] - 3e-10) if f else T[-1]; t0 = dn[0] + 4e-11
    tail = (f"{at(T, dv[kh], te) * 1e-13:6.0f}, {(at(T, dv[kc], te) - dv[kc][0]) * 1e3:+5.0f}, {(at(t, sn, te) - at(t, sn, t0)) * 1e3:+.2f}" if T[-1] > t0 + 1e-9 else "hold not reached yet")
    print(f"{rid:12s} {w}   | {at(t, sn, b):.3f} -> {at(t, sn, a):.3f} ({(at(t, sn, a) - at(t, sn, b)) * 1e3:+5.0f} mV) | {at(T, made, b):6.0f} + {at(T, made, a) - at(T, made, b):5.0f} | {at(T, dv[kh], a) * 1e-13:6.0f} | {tail}")
