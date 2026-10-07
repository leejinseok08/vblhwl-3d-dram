# gt_rh_body.py <run id> ... : row-hammer pair runs, the victim's body at the instants Fig.7(e) could mean.
# Fig.7(c) marks "t = 0" and "t = t_A" with two arrows that end on the first aggressor pulse; Fig.7(e) gives the change of the
# body potential between them: 2.4 mV (impact ionization off, floating), 665.1 mV (on, floating), 1.8 mV (on, grounded body).
# Per run, at the start of the transient, at the start of the hammer and after 1/2, 1, 2, 2.5, 5 and 10 aggressor cycles: the
# electrostatic potential, the hole and the electron quasi-Fermi potential at the body-centre probe, holes in the victim's
# body, the storage node; then the change of each against the start of the hammer. Works on running jobs.
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
for rid in sys.argv[1:]:
    d = os.path.join(RUNS, rid)
    try:
        s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0]); j = json.load(open(os.path.join(d, "run.json"), encoding="utf-8"))
    except Exception as e:
        print(f"{rid}: no data ({e})"); continue
    t = s["time"]; T = dv["time"]; p = j["params"]; tS = j["sched"]["tS"]; per = (p["tON"] + p["tOFF"]) * 1e-9; end = min(t[-1], T[-1])
    col = lambda n: dv[next(q for q in dv if n in q and q.startswith("Pos"))]
    ps, hq, eq = col("ElectrostaticPotential"), col("hQuasiFermiPotential"), col("eQuasiFermiPotential"); hd = dv[next(q for q in dv if "hDensity" in q and "Ch_a" not in q)]
    sn = s[next(x for x in s if "nSN)" in x)]
    print(f"== {rid}: II {p.get('II')}, R {p.get('Rwl', 0):g} Ohm, body {'grounded' if p.get('Bgc') or 'zzg' in j.get('struct', '') else 'floating'}; hammer starts at {tS * 1e9:.4f} ns")
    print("   instant                 | potential [V]  hole QF [V]  electron QF [V] | holes | node [V]  || against the hammer start [mV]: potential, hole QF")
    for lab, x in [("start of the transient", 0.0), ("hammer start", tS)] + [(f"+ {c:g} cycles", tS + c * per) for c in (0.25, 0.5, 1, 1.5, 2, 2.5, 5, 10)]:
        if x > end + 1e-15: break
        print(f"   {lab:23s} | {at(T, ps, x):+9.4f}     {at(T, hq, x):+9.4f}    {at(T, eq, x):+9.4f}      | {at(T, hd, x) * 1e-13:5.0f} | {at(t, sn, x):.5f}  || {(at(T, ps, x) - at(T, ps, tS)) * 1e3:+9.1f}  {(at(T, hq, x) - at(T, hq, tS)) * 1e3:+9.1f}")
