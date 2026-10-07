# gt_rh_wave.py <run id> [first cycle] [last cycle] [points per cycle] : a row-hammer pair run inside the aggressor cycles.
# Prints, at equal steps through the chosen cycles (default: all the run has reached, 8 points per cycle): time from the start of
# the hammer, aggressor WL, victim storage node and its change since the previous point, holes in the victim's body, the
# victim's body-centre potential and gated-body average (if recorded) against the start of the transient, the victim gate
# node if a resistor sits in the WL. Shows in which phase of the aggressor the node falls (Fig.7(a): only while it is high).
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
rid = sys.argv[1]; d = os.path.join(RUNS, rid)
s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0]); j = json.load(open(os.path.join(d, "run.json"), encoding="utf-8"))
t = s["time"]; T = dv["time"]; p = j["params"]; tS = j["sched"]["tS"]; per = (p["tON"] + p["tOFF"]) * 1e-9; end = min(t[-1], T[-1])
k = lambda n: next((x for x in s if n in x), None); sn = s[k("nSN)")]; wa = s[k("nWLa")]; gv = s[k("nGv")] if k("nGv") else None
hv = dv[next(q for q in dv if "hDensity" in q and "Ch_a" not in q)]; pc = dv[next(q for q in dv if q.startswith("Pos") and "ElectrostaticPotential" in q)]
ka = next((q for q in dv if q.startswith("AveWindow") and "ElectrostaticPotential" in q), None)
c0 = int(sys.argv[2]) if len(sys.argv) > 2 else 1; c1 = int(sys.argv[3]) if len(sys.argv) > 3 else int((end - tS) / per + 1); n = int(sys.argv[4]) if len(sys.argv) > 4 else 8
print(f"== {rid}: hammer from {tS * 1e9:.4f} ns, now at {end * 1e9:.4f} ns; cycles {c0} .. {c1}")
print("   t - t0 [ns]  aggressor WL [V]  victim node [V]   step [mV]  holes  body centre [mV]" + ("  gated-body average [mV]" if ka else "") + ("  victim gate [mV]" if gv else ""))
prev = None
for i in range((c0 - 1) * n, c1 * n + 1):
    x = tS + i * per / n
    if x > end + 1e-15: break
    v = at(t, sn, x)
    print(f"   {(x - tS) * 1e9:9.4f}   {at(t, wa, x):8.3f}        {v:.5f}     {'' if prev is None else f'{(v - prev) * 1e3:+8.3f}':>8s}  {at(T, hv, x) * 1e-13:5.0f}   {(at(T, pc, x) - pc[0]) * 1e3:+8.1f}"
          + (f"          {(at(T, dv[ka], x) - dv[ka][0]) * 1e3:+8.1f}" if ka else "") + (f"          {at(t, gv, x) * 1e3:+8.1f}" if gv else ""))
    prev = v
