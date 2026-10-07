# gt_rh_pairs.py <run id> ... : row-hammer pair runs, what impact ionization makes per aggressor cycle and what arrives in the victim.
# Per run, for the write and for every aggressor cycle of the hammer: electron-hole pairs made by impact ionization and by
# band-to-band tunnelling in the whole section (time integral of the two generation integrals of the device file; a 100 nm wide
# device = integral x 1e-13), holes in the victim's body at the end of the cycle (and in the aggressor's, if the deck records it),
# storage node of the victim and of the aggressor, and the holes that leave through the BL contact and the two storage-node contacts
# (time integral of the contact hole currents / q; sign as the device file gives it). Works on running jobs.
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
W = 1e-13

def cum(T, y):                             # running time integral (trapezoid)
    o = [0.0]
    for i in range(1, len(T)): o.append(o[-1] + (y[i] + y[i - 1]) / 2 * (T[i] - T[i - 1]))
    return o

for rid in sys.argv[1:]:
    d = os.path.join(RUNS, rid)
    try:
        s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0]); j = json.load(open(os.path.join(d, "run.json"), encoding="utf-8"))
    except Exception as e:
        print(f"{rid}: no data ({e})"); continue
    t = s["time"]; T = dv["time"]; k = lambda n: next((x for x in s if n in x), None); p = j["params"]
    tS, tE = j["sched"]["tS"], j["sched"]["tEnd"]; per = (p["tON"] + p["tOFF"]) * 1e-9; end = min(t[-1], T[-1], tE)
    av = cum(T, dv[next(q for q in dv if "ImpactIonization" in q or "AvalancheGeneration" in q)]); bb = cum(T, dv[next(q for q in dv if "Band2BandGeneration" in q)])
    hv = dv[next(q for q in dv if "hDensity" in q and "Ch_a" not in q)]; ha = next((dv[q] for q in dv if "hDensity" in q and "Ch_a" in q), None)
    sn = s[k("nSN)")]; sa = s[k("nSNa")] if k("nSNa") else None
    hc = {c: cum(T, dv[c + " hCurrent"]) for c in ("bl", "sn_a", "sn_v") if c + " hCurrent" in dv}   # contact hole currents [A]: time integral / q = holes
    print(f"== {rid}: II {p.get('II')}, R {p.get('Rwl', 0):g} Ohm, BL contact hole velocity {p.get('BLhv', -1):g}, aggressor node at the start {p.get('SNa0', 0):g} V; hammer from {tS * 1e9:.4f} ns, now at {end * 1e9:.4f} ns")
    print("   interval            | pairs by impact ionization  by tunnelling | holes in the victim body" + ("  in the aggressor body" if ha else "") + " | victim node [V]" + ("  aggressor node [V]" if sa else "") + " | holes through the contacts (+ = out of the device): " + " ".join(hc))
    marks = [("write + hold", 0.0, tS)] + [(f"cycle {i + 1}", tS + i * per, tS + (i + 1) * per) for i in range(int(p["Ncyc"])) if tS + (i + 1) * per <= end + 1e-15]
    for lab, a, b in marks:
        print(f"   {lab:19s} | {(at(T, av, b) - at(T, av, a)) * W:12.1f} {(at(T, bb, b) - at(T, bb, a)) * W:20.1f}      | {at(T, hv, b) * W:10.0f}" + (f" {at(T, ha, b) * W:18.0f}" if ha else "")
              + f"      | {at(t, sn, b):.5f}" + (f"        {at(t, sa, b):.4f}" if sa else "")
              + "      | " + " ".join(f"{(at(T, v, b) - at(T, v, a)) / 1.602e-19:+9.1f}" for v in hc.values()))
