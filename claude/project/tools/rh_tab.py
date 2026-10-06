# rh_tab.py <run id> ... : row-hammer runs in one table, counted the way the paper's Fig.6(e) can be read (a 2 ns window of
# ten aggressor cycles): storage-node change over the whole pulse train, that divided by the number of cycles, the mean
# change per cycle over the last five cycles (what keeps accumulating), the reversible swing with the aggressor WL high, and
# the first jump of the victim gate node if the deck has the resistor of Fig.7(b).
# Paper: 0.0535 / 0.0100 / 0.0060 mV per cycle for Y-Y' / Z-Z' / X-X' (impact ionization off); thresholds = 0.605 V / loss.
# Sampling 20 ps before each aggressor rise. Works on running jobs.
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
runs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
print("run            R [Ohm]  cycles  total change [mV]  per cycle (all)  per cycle (last 5)  swing [mV]  gate jump [mV]")
for rid in sys.argv[1:]:
    try: s = load(os.path.join(runs, rid, rid + "_sys.plt"))
    except Exception: print(f"{rid:14s} no data"); continue
    t = s["time"]; sn = s[[k for k in s if "nSN)" in k][0]]; wa = s[[k for k in s if "nWLa" in k][0]]; gv = [k for k in s if "nGv" in k]
    m = re.search(r"resistance = ([-+0-9.eE]+)", open(os.path.join(runs, rid, rid + "_des.cmd")).read()); R = m.group(1) if m else "0"
    wf = edges(t, s[[k for k in s if "nWL)" in k][0]], 0, 1.8, False)       # the aggressor pulse of the write (SNa0 decks) is not a hammer pulse
    r = [x for x in edges(t, wa, 0, 1.8, True) if not wf or x > wf[-1]]
    if len(r) < 2: print(f"{rid:14s} {R:>7s}  pulses not reached (t = {t[-1] * 1e9:.3f} ns)"); continue
    per = r[1] - r[0]; v = [at(t, sn, x - 2e-11) for x in r] + ([at(t, sn, r[-1] + per - 2e-11)] if t[-1] >= r[-1] + per - 2e-11 else [])
    n = len(v) - 1; hi = [at(t, sn, x + 5e-11) - at(t, sn, x - 2e-11) for x in r if t[-1] > x + 5e-11]
    last5 = f"{(v[-6] - v[-1]) / 5 * 1e3:+9.5f}" if n >= 6 else "     -   "
    gb = f"{max(at(t, s[gv[0]], r[0] + d * 1e-12) for d in (2, 5, 8, 12, 20)) * 1e3:+7.1f}" if gv else "      -"
    print(f"{rid:14s} {R:>7s}  {n:4d}   {(v[-1] - v[0]) * 1e3:+10.4f}      {(v[0] - v[-1]) / max(n, 1) * 1e3:+9.5f}        {last5}        {sum(hi) / len(hi) * 1e3:+8.4f}   {gb}")
