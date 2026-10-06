# gt_long_split.py [<short tag> <control tag>] : the first BL-low phase of a long-hold FBE run (default Dz3F, hold 21 us) split in two:
# what the storage node loses in the same time span when the BL stays high (the run of the control tag, default Dz6F, has the
# same history and holds on: an idle control), and what the BL-low phase adds to that. Also the holes in the body at the
# start and the end of the span, in both runs. Cases 1 - 5.
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
A, B = (sys.argv[1:3] + ["Dz3F", "Dz6F"])[:2] if len(sys.argv) > 2 else ("Dz3F", "Dz6F")

def run(rid):
    d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; k = lambda n: next(x for x in s if n in x); kh = next(x for x in dv if "hDensity" in x)
    t0 = edges(t, s[k("nWL)")], 0, 1.8, False)[0] + 4e-11; f = edges(t, s[k("nBL")], 0, 1.1, False); r = [x for x in edges(t, s[k("nBL")], 0, 1.1, True) if x > f[0]]
    kc = next(x for x in dv if "ElectrostaticPotential" in x)
    return dict(t0=t0, tA=f[0] - 3e-10, tB=r[0] - 3e-10, tP=f[0] + 10.5e-9 - 3e-10, sn=lambda x: at(t, s[k("nSN)")], x),
                hol=lambda x: at(dv["time"], dv[kh], x) * 1e-13, rise=lambda x: (at(dv["time"], dv[kc], x) - dv[kc][0]) * 1e3)

print(f"first BL-low phase of {A} against the same span of {B} (BL stays high). Node in mV, holes in the body as a count.")
print("Case  span after t = 0 [us]   loss, BL low   loss, BL high   added by BL low   holes: start -> end BL low / BL high   node at start [V]")
for c in range(1, 6):
    a, b = run(f"{A}_c{c}"), run(f"{B}_c{c}"); x1, x2 = a["tA"] - a["t0"], a["tB"] - a["t0"]
    assert x2 < b["tA"] - b["t0"], "the control has left its hold inside the span"
    la = (a["sn"](a["tA"]) - a["sn"](a["tB"])) * 1e3; lb = (b["sn"](b["t0"] + x1) - b["sn"](b["t0"] + x2)) * 1e3
    print(f"{c:4d}  {x1 * 1e6:8.2f} .. {x2 * 1e6:6.2f}  {la:12.2f}  {lb:14.2f}  {la - lb:16.2f}     {a['hol'](a['tA']):6.0f} -> {a['hol'](a['tB']):6.0f} / {b['hol'](b['t0'] + x2):6.0f}"
          f"  {a['sn'](a['tA']):16.4f}")

# The same length as the paper's BL-low phase: the loss in the first 10.5 ns after the first BL fall (read 0.3 ns before the
# instant at which the paper's BL would rise again, against t_A; a reading Codex made first, docs/CODEX_ROUND11_CAUSE_AND_RECOVERY).
import paper_targets as P
print()
print("loss in the first 10.5 ns after the first BL fall [mV] (the paper's BL-low phase is 10.5 ns long), with the state at t_A")
print("hold before t_A     " + "".join(f"   Case {c}" for c in range(1, 6)) + "   | body rise at t_A [mV]          | node change in the hold [mV]")
for tag, lab in (("DcsF", "21 ns (paper axis)"), ("Dz3F", "21 us"), ("Dz4F", "210 us"), ("Dz5F", "2.1 ms"), ("Dz6F", "21 ms")):
    z = [run(f"{tag}_c{c}") for c in range(1, 6)]
    print(f"{lab:20s}" + "".join(f"{(a['sn'](a['tA']) - a['sn'](a['tP'])) * 1e3:9.2f}" for a in z) + "   | "
          + " ".join(f"{a['rise'](a['tA']):5.0f}" for a in z) + "  | " + " ".join(f"{(a['sn'](a['tA']) - a['sn'](a['t0'])) * 1e3:7.1f}" for a in z))
print(f"{'paper Fig.8':20s}" + "".join(f"{P.FBE_FIRST[c]:9.2f}" for c in range(1, 6)) + "   | " + " ".join(f"{P.FBE_RISE[c]:5.0f}" for c in range(1, 6)) + "  |     0 (flat)")
