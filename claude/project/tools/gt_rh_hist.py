# gt_rh_hist.py [tag ...] : round 15, the row hammer of Fig.6(e) / Fig.7 with a history that charges the victim's body (runs
# D<tag>Ry_yy, Ryi_yy, Rz_zz, Rzi_zz: Y-Y' and Z-Z', impact ionization off / on). Default tags: fin (no history) x1 x2 x3 x4 x7 and
# the idle controls x5 (of x2) and x6 (of x7), in which the aggressor WL stays at 0 V.
# Per run, from the start of the hammer (run.json: sched.tS) to its end: holes in the victim's body and rise of its body-centre
# potential at the start, storage node at the start, loss of the node per cycle over all cycles and over the last five (a
# first-cycle shift is not a loss per cycle), the node after every cycle, the jump of the victim gate node if a resistor sits
# in the WL, and the change of the body over the hammer. Loss counted positive when the node falls. Works on running jobs.
# Paper (per cycle, from the thresholds of Fig.6(e) / Fig.7 and the margin 0.605 V): Y-Y' 0.0535 mV with and without impact
# ionization; Z-Z' 0.0100 mV without, with it the node falls from 1.1 to 0.58 V inside the ten cycles.
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
TAGS = [a for a in sys.argv[1:] if not a.startswith("-")] or ["fin", "x1", "x2", "x3", "x4", "x7", "x5", "x6"]
WHAT = {"fin": "no history", "x1": "16.2 us at Vdd", "x2": "16.2 us at Vdd/2", "x3": "16.2 us at Vdd, R 200k", "x4": "16.2 us at Vdd/2, R 200k",
        "x7": "100 us at Vdd/2", "x5": "idle: 16.2 us at Vdd/2", "x6": "idle: 100 us at Vdd/2"}
PAPER = {"Ry_yy": "0.0535", "Ryi_yy": "0.0535", "Rz_zz": "0.0100", "Rzi_zz": "node 1.1 -> 0.58 V", "Rzbi_zz": "node 1.1 -> 0.58 V", "Rzg_zz": "0.036", "Rzbg_zz": "0.036"}

def run(rid):
    d = os.path.join(RUNS, rid)
    try:
        s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0]); j = json.load(open(os.path.join(d, "run.json"), encoding="utf-8"))
    except Exception: return None
    t = s["time"]; k = lambda n: next((x for x in s if n in x), None); sn = s[k("nSN)")]; T = dv["time"]
    tS, tE = j["sched"]["tS"], j["sched"]["tEnd"]; p = j["params"]; per = (p["tON"] + p["tOFF"]) * 1e-9; n = int(p["Ncyc"])
    if t[-1] < tS: return dict(state=f"before the hammer: t = {t[-1] * 1e9:.4g} ns of {tS * 1e9:.6g}")
    kc = next(q for q in dv if q.startswith("Pos") and "ElectrostaticPotential" in q); kh = next(q for q in dv if "hDensity" in q and "Ch_a" not in q); end = min(t[-1], T[-1], tE)
    done = int((end - tS) / per + 1e-6); L = lambda x: (at(t, sn, tS) - at(t, sn, x)) * 1e3
    cyc = [L(tS + i * per) for i in range(1, done + 1)]
    o = dict(state="complete" if done >= n else f"{done} of {n} cycles", holes=at(T, dv[kh], tS) * 1e-13, rise=(at(T, dv[kc], tS) - dv[kc][0]) * 1e3, sn0=at(t, sn, tS), cyc=cyc, n=done,
             allc=cyc[-1] / done if done else float("nan"), last5=(cyc[-1] - cyc[-6]) / 5 if done >= 6 else float("nan"),
             drise=(at(T, dv[kc], end) - at(T, dv[kc], tS)) * 1e3, dholes=(at(T, dv[kh], end) - at(T, dv[kh], tS)) * 1e-13)
    if k("nGv"):
        g = s[k("nGv")]; o["gate"] = max(v for x, v in zip(t, g) if tS <= x <= end) * 1e3
    return o

for nm, lab in (("Ry_yy", "Y-Y', impact ionization off"), ("Ryi_yy", "Y-Y', impact ionization on"), ("Rz_zz", "Z-Z', impact ionization off"), ("Rzi_zz", "Z-Z', impact ionization on"),
                ("Rzbi_zz", "Z-Z', BL contact at the bottom end of the pillar, impact ionization on"), ("Rzg_zz", "Z-Z', grounded body, impact ionization on"),
                ("Rzbg_zz", "Z-Z', BL contact at the bottom end, grounded body, impact ionization on")):
    print(f"== {lab}   (paper per cycle: {PAPER[nm]})")
    print("   config  history                    | holes  body rise  node at start | loss per cycle [mV]: all, last five | total [mV] | body over the hammer: rise, holes | gate jump | state")
    R = {tag: run(f"D{tag}{nm}") for tag in TAGS}
    if not any(R.values()): print("   (no run of the named configurations)"); continue
    for tag in TAGS:
        o = R[tag]
        if o is None: print(f"   {tag:6s}  {WHAT.get(tag, ''):26s} | no data"); continue
        if "holes" not in o: print(f"   {tag:6s}  {WHAT.get(tag, ''):26s} | {o['state']}"); continue
        print(f"   {tag:6s}  {WHAT.get(tag, ''):26s} | {o['holes']:5.0f}  {o['rise']:+7.0f} mV  {o['sn0']:.4f} V     | {o['allc']:+9.5f}  {o['last5']:+9.5f}             | {o['cyc'][-1] if o['cyc'] else float('nan'):+9.4f}  | "
              f"{o['drise']:+7.1f} mV {o['dholes']:+6.0f}          | " + (f"{o['gate']:+6.0f} mV" if "gate" in o else "    -    ") + f" | {o['state']}")
    for a, b in (("x2", "x5"), ("x7", "x6")):
        if R.get(a) and R.get(b) and "cyc" in R[a] and "cyc" in R[b] and R[a]["n"] and R[b]["n"]:
            m = min(R[a]["n"], R[b]["n"]); print(f"   {a} minus its idle control {b}: {(R[a]['cyc'][m - 1] - R[b]['cyc'][m - 1]) / m:+.5f} mV per cycle over {m} cycles (what the aggressor adds)")
    if "-c" in sys.argv:
        for tag in TAGS:
            o = R[tag]
            if o and o.get("cyc"): print(f"   {tag}: node below its start after cycle 1 .. {o['n']} [mV]: " + " ".join(f"{x:+.4f}" for x in o["cyc"]))
