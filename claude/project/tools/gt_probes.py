# gt_probes.py [-w] <run id> ... : the potential probes of FBE runs along the body mid-line at four instants, to see which
# quantity / place / pair of instants Fig.8(a) ("body potential rise, t = 0 -> t_A": 555 / 445 / 365 / 320 / 368 mV) can be.
# Instants: eq = start of the transient (everything at 0 V) | t0 = storage node charged, WL back at 0 V | tA = just before
# the first BL fall | lo = end of the first BL-low phase. Probes as written by make_runs.py (x along the channel, um):
# 0.0625 = p body under the BL-side spacer, 0.085 / 0.125 / 0.165 = under the gate (BL side / centre / storage-node side).
# Holes = integral of the hole density over the channel region x 1e-13 (um^2 -> cm^2, width 0.1 um) = number of holes.
# 3D runs (probe with three coordinates): x 2e-12 (um^3 -> cm^3, the half cell of the model times 2).
# -w : the write phase instead, step by step (holes in the body, pairs made by impact ionization so far, node voltages).
# -k : sizing runs of the hole supply (params.py Gb): when does the body centre stand above its start value by what Fig.8(a)
#      shows, which share of the supply had been delivered by then, and the rate that ends exactly there.
import sys, os, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
PAPER = {"1": 555, "2": 445, "3": 365, "4": 320, "5": 368}
args = [a for a in sys.argv[1:] if a not in ("-w", "-k", "-q")]       # -q with -w: the summary line only
for rid in args:
    d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; key = lambda n: next(k for k in s if n in k); sn, bl, wl = s[key("nSN)")], s[key("nBL")], s[key("nWL)")]
    T = dv["time"]; kh = next(k for k in dv if "hDensity" in k); kc = next(k for k in dv if "ElectrostaticPotential" in k)
    HF = 2e-12 if kc.count(",") == 2 else 1e-13      # 3D unit cell: um^3 -> cm^3, half cell x 2
    w = edges(t, wl, 0, 1.8, False)
    if "-k" in sys.argv:
        deck = open(os.path.join(d, rid + "_des.cmd")).read(); g0 = float(re.findall(r"SetConstant\( Value=([-+.0-9eE]+)", deck)[-1])     # the body region's (the device-wide one is 0)
        g1, g2 = (float(x) for x in re.search(r"WaveTime=\(([^,]+), ([^)]+)\)", deck).groups()); tl = 1e-10
        F = lambda x: min(max(x - (g1 - tl), 0), tl) ** 2 / (2 * tl) + min(max(x - g1, 0), g2 - g1) + (tl / 2 - (tl - min(max(x - g2, 0), tl)) ** 2 / (2 * tl))     # integral of the time function up to x
        tgt = PAPER[rid[-1]] * 1e-3; rise = [v - dv[kc][0] for v in dv[kc]]
        i = next((i for i in range(1, len(T)) if T[i - 1] >= g1 - tl and rise[i] >= tgt > rise[i - 1]), None)       # only while the supply runs (the write lifts the body too)
        if i is None: print(f"{rid}: rise at the end {rise[-1] * 1e3:+.1f} mV, target {tgt * 1e3:.0f} not crossed (rate {g0:g})"); continue
        tc = T[i - 1] + (T[i] - T[i - 1]) * (tgt - rise[i - 1]) / (rise[i] - rise[i - 1]); fr = F(tc) / F(g2 + tl)
        qf = " ".join(f"{at(T, dv[k], tc):+.3f}" for k in dv if "hQuasiFermiPotential" in k)       # hole quasi-Fermi potential at the probes, in the order of the deck
        print(f"{rid}: target {tgt * 1e3:.0f} mV crossed at {tc * 1e9:.2f} ns with {at(T, dv[kh], tc) * HF:.0f} holes in the body (psi {at(T, dv[kc], tc):+.3f} V, phi_p {qf} V), {fr * 100:.1f} % of the supply delivered"
              f" -> rate {g0 * fr:.4g} (sizing rate {g0:g}); at the end: rise {rise[-1] * 1e3:+.1f} mV, {dv[kh][-1] * HF:.0f} holes, storage node {sn[-1]:.4f} V")
        continue
    if "-w" in sys.argv:
        ka = next(k for k in dv if "Avalanche" in k or "ImpactIonization" in k); made = 0.0; rows = []
        for i in range(1, len(T)):
            made += 0.5 * (dv[ka][i] + dv[ka][i - 1]) * (T[i] - T[i - 1]) * HF       # integral of the rate [1/s per cm3 x um2] over time -> pairs
            rows.append((T[i], at(t, wl, T[i]), at(t, bl, T[i]), at(t, sn, T[i]), dv[kh][i] * HF, made, dv[kc][i]))
        end = (w[0] if w else T[-1]) + 3e-11
        print(f"{rid}: time [ps]  WL  BL  SN [V] | holes in the body | pairs made by impact ionization so far | psi at the body centre [V]")
        if "-q" not in sys.argv:
            for r in [r for r in rows if r[0] <= end][::4]: print(f"   {r[0] * 1e12:7.1f}  {r[1]:5.2f} {r[2]:5.2f} {r[3]:6.3f} | {r[4]:9.1f} | {r[5]:9.1f} | {r[6]:+.3f}")
        b = [r for r in rows if w and r[0] <= w[0] - 1e-12][-1]; a = [r for r in rows if w and r[0] <= w[0] + 8e-12][-1]      # before the WL falls / after it, before the node is set
        print(f"{rid}: before the WL falls: SN {b[3]:.3f} V, {b[4]:.0f} holes, {b[5]:.0f} pairs made | after: SN {a[3]:.3f} V, {a[4]:.0f} holes, {a[5]:.0f} pairs"
              f" | at the end ({T[-1] * 1e9:.2f} ns): {dv[kh][-1] * HF:.0f} holes, body centre {(dv[kc][-1] - dv[kc][0]) * 1e3:+.0f} mV above its start (paper {PAPER.get(rid[-1], '?')}),"
              f" storage node {sn[-1]:.4f} V ({(sn[-1] - at(t, sn, (w[0] if w else t[-1]) + 4e-11)) * 1e3:+.2f} mV since it was set)")
        continue
    f = edges(t, bl, 0, 1.1, False); r = [x for x in edges(t, bl, 0, 1.1, True) if f and x > f[0]]
    if not (f and w): print(rid, "not far enough"); continue
    inst = [("eq", T[0]), ("t0", w[0] + 4e-11), ("tA", f[0] - 3e-10)] + ([("lo", r[0] - 3e-10)] if r else [])
    print(f"{rid}  (paper Fig.8(a): {PAPER.get(rid[-1], '?')} mV)   holes in the body: " + "  ".join(f"{n} {at(T, dv[kh], x) * HF:.3g}" for n, x in inst))
    for k in [k for k in dv if "Potential" in k and "Pos(" in k]:
        v = [at(T, dv[k], x) for n, x in inst]
        print(f"   {k[:44]:44s} " + "  ".join(f"{n} {x:+.4f}" for (n, _), x in zip(inst, v)) + f"   | eq->tA {(v[2] - v[0]) * 1e3:+7.1f}  t0->tA {(v[2] - v[1]) * 1e3:+7.1f} mV")
