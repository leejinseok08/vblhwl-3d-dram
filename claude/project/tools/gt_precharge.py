# gt_precharge.py [-n] [--dc <load-line run>] <run id> ... : the pre-charge (write -> WL off -> hold) of the Cho transient runs (deck_cho), plan P2
# of 2026-10-09 ("natural pre-charge"). Works on the reset runs (SNset: the node is set to 1.1 V at 130 - 140 ps; before that the run IS the
# natural write) and on the natural runs (SNfree / DnwR*). Per run:
#   1. state at the instants of the pre-charge: WL edge, the four points of Fig.4(a) (12 / 24 / 39 / 60 ps after it: 0.72 / 0.92 / 1.06 / 1.13 V),
#      WL off (1 ps before / 5 ps after its falling edge), the end of the BL step, before / after the reset window, the BL step to Vdd/2, the
#      start of the hammer or of the BL pulses: storage node, BL, WL, potential and hole quasi-Fermi potential at the body probe, node minus
#      that quasi-Fermi potential (source-body bias of the victim), holes in the victim body, pairs made so far by impact ionization and BTBT;
#   2. charge balance per interval: Cs dV of the node against the time integral of the storage-node contact current (electron, hole and
#      displacement parts; the reset window is outside every interval: the circuit sets the node there), the mean charging current Cs dV / dt
#      next to the paper's (Fig.4(a) with the text's 4.2 fF: 252 / 70 / 39 / 14 uA), the BL contact current, and the charge the reset adds;
#   3. --dc <run>: the DC load-line current (deck "load": gates at Vpp, BL at the write level, node swept) at the node voltages the transient
#      passes, next to the transient's own contact current there (same terminal voltages, but the body and the displacement currents differ);
#   4. with ProbeE in the deck: where the BL-to-node voltage falls (electron quasi-Fermi potential along the victim channel at mid-depth):
#      pillar and contact | body under the BL-side spacer | gated channel | source, at the four points of Fig.4(a).
# Units: contact currents of the device file are cell currents (AreaFactor = cell width / 1 um); body integrals x 1e-13 = carriers in a 100 nm
# wide cell (as tools/gt_rh_pairs.py). -n prints the column names.
import sys, os, re, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
W = 1e-13                          # body integral -> carriers in the 100 nm wide cell
Q = 1.602e-19
TE = 5e-12                         # edge time of deck_cho
PAPER_I = (252, 70, 39, 14)        # uA: Fig.4(a) with 4.2 fF between its points (make_runs.py, round 37)


def cum(T, y, be=False):           # running time integral; be: right end point (the quadrature of Transient = BE), else trapezoid
    o = [0.0]
    for i in range(1, len(T)): o.append(o[-1] + (y[i] if be else (y[i] + y[i - 1]) / 2) * (T[i] - T[i - 1]))
    return o


def first_at(t, v, x):
    """Value at time x; at a time that the file holds twice (a reset), the FIRST copy = the state before the circuit changed it."""
    for i, ti in enumerate(t):
        if ti >= x - 1e-18: return v[i] if ti <= x + 1e-18 or i == 0 else v[i - 1] + (v[i] - v[i - 1]) * (x - t[i - 1]) / ((ti - t[i - 1]) or 1)
    return v[-1]


def schedule(p, sched, test):
    """Times of deck_cho's pre-charge (s): WL edge, WL off, end of the BL step, reset window (FBE / RH decks only), start of the test phase."""
    t1 = 3 * TE + p["tWr"] * 1e-9; t2 = t1 + TE; vw = p["Vwr"] or p["Vdd"]
    if vw != p["Vdd"]: t2 += TE
    tset = (t2, t2 + 2 * TE) if p["SNset"] and test in ("FBE", "RH") else None
    return dict(wl_on=3 * TE, wl_off=t1, bl_done=t2, tset=tset, reset=bool(tset) and not p.get("SNfree", 0),
                hold_end=(tset[1] if tset else t2) + p["tHold"] * 1e-9, test=sched.get("tS"))


def voltage_split(dv, p, ts):
    """With ProbeE: shares of the BL-to-node drop of the electron quasi-Fermi potential along the victim channel, at the times ts."""
    qf = {}
    for k in dv:
        m = re.search(r"\(\s*(-?[\d.eE+-]+)\s*[ ,]\s*(-?[\d.eE+-]+)\s*\)", k) if "eQuasiFermiPotential" in k else None
        if m: qf[(round(float(m.group(1)) * 1e3, 1), round(float(m.group(2)) * 1e3, 1))] = dv[k]
    ym = p["Dvox"] / 2 + p["Tgm"] + p["Tox"] + p["Tbody"] / 2; row = sorted(x for (x, y) in qf if abs(y - ym) < 0.6)
    if len(row) < 4: return None
    near = lambda x: min(row, key=lambda a: abs(a - x)); col = lambda x: qf[(near(x), min((y for (a, y) in qf if a == near(x)), key=lambda y: abs(y - ym)))]
    x0 = p["Wbl"] / 2; xg1 = x0 + p["Lsp1"]; xg2 = xg1 + p["Lg"]; T = dv["time"]; out = []
    for t in ts:
        a, b, c, d = (at(T, col(x), t) for x in (row[0], x0 + 3, xg1 + 2, xg2 - 3)); e = at(T, col(row[-1]), t)
        tot = a - e; out.append((t, tot, [(a - b) / tot, (b - c) / tot, (c - d) / tot, (d - e) / tot] if abs(tot) > 1e-6 else None))
    return out


def report(rid, dc=None):
    d = os.path.join(RUNS, rid)
    try:
        s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0]); j = json.load(open(os.path.join(d, "run.json"), encoding="utf-8"))
    except Exception as e:
        print(f"{rid}: no data ({e})"); return
    p = j["params"]; S = schedule(p, j["sched"], j["deck"].split(":")[-1]); t, T = s["time"], dv["time"]; cs = p["Cs"]
    be = bool(re.search(r"Transient\s*=\s*BE\b", open(os.path.join(d, rid + "_des.cmd"), errors="replace").read()))
    k = lambda n: next(x for x in s if n in x); sn, bl, wl = s[k("nSN)")], s[k("nBL")], s[k("nWL)")]
    kb = next((x for x in dv if "ElectrostaticPotential" in x and x.startswith("Pos(")), None); kh = kb.replace("ElectrostaticPotential", "hQuasiFermiPotential") if kb else None
    hv = dv[next(x for x in dv if "hDensity" in x and "Ch_a" not in x)]
    isn = dv["sn_v TotalCurrent"]; cq = {n: cum(T, dv[f"sn_v {n}"], be) for n in ("TotalCurrent", "eCurrent", "hCurrent", "DisplacementCurrent")}; cbl = cum(T, dv["bl TotalCurrent"], be)
    trap = cum(T, isn)                 # the same with the trapezoid rule, to show what the quadrature does
    av = cum(T, dv[next(x for x in dv if "ImpactIonization" in x or "AvalancheGeneration" in x)], be); bb = cum(T, dv[next(x for x in dv if "Band2BandGeneration" in x)], be)
    up = edges(t, wl, 0, p["Vpp"], True); dn = edges(t, wl, 0, p["Vpp"], False)
    if not up or not dn: print(f"{rid}: write not complete in the file (last time {t[-1] * 1e12:.0f} ps)"); return
    tw, toff = up[0], dn[0]
    # sign of the device file's contact current: + = into the device or out of it (fixed by the write, where the node charges)
    sg = 1.0 if (at(T, cq["TotalCurrent"], toff) - at(T, cq["TotalCurrent"], tw)) * (at(t, sn, toff) - at(t, sn, tw)) > 0 else -1.0
    kind = f"{p['Pair']} pair" if p["Pair"] != "one" else "single cell"
    print(f"== {rid}: {kind}, body {'grounded' if p['Bgc'] else 'floating'}, avalanche {'on (' + str(p.get('IImod') or 'default') + (', ' + p['IIdf'] if p.get('IIdf') else '') + ')' if p['II'] else 'off'}, "
          f"Cs {cs * 1e15:.2f} fF, BL write {p['Vwr'] or p['Vdd']} V, " + (f"node SET to {p['SNset']} V at {S['tset'][0] * 1e12:.0f}-{S['tset'][1] * 1e12:.0f} ps" if S["reset"] else "node NOT set (natural)")
          + f"; file to {t[-1] * 1e12:.0f} ps; contact current sign: + = {'out of' if sg > 0 else 'into'} the device at sn_v; time integration "
          + ("BE (charge = step x current at its end: integrals below use that rule on the plotted points)" if be else "not BE (integrals: trapezoid)"))
    marks = [("WL edge", tw)] + [(f"+{ps} ps (paper {v:.2f})", tw + ps * 1e-12) for ps, v in P.WRITE.items()] + [("WL off - 1 ps", toff - 1e-12), ("WL off + 5 ps", toff + 5e-12), ("BL step done", S["bl_done"])]
    if S["tset"]: marks += [("before reset window" if S["reset"] else "start of the reset window (not set)", S["tset"][0]), ("after reset window", S["tset"][1])]
    marks += [("end of hold at Vdd", S["hold_end"])]
    if S["test"] and S["test"] > S["hold_end"] + 1e-15: marks += [("start of hammer / test", S["test"])]
    marks = [(a, b) for a, b in marks if b <= min(t[-1], T[-1]) + 1e-15]
    print("   instant                    t [ps] |  SN [V]   BL [V]   WL [V] | body: potential  h-QF [V] | SN - h-QF [V] | holes in body | pairs II   BTBT (so far)")
    for lab, x in marks:
        g = lambda v, tt=t: first_at(tt, v, x)
        b = f"{g(dv[kb], T):+8.4f}  {g(dv[kh], T):+8.4f}" if kb else "      -         -   "
        print(f"   {lab:24s} {x * 1e12:8.1f} | {g(sn):.4f}  {g(bl):.4f}  {g(wl):.4f} | {b} | {g(sn) - (g(dv[kh], T) if kh else 0):+8.4f}     | {g(hv, T) * W:10.0f}    | {g(av, T) * W:9.1f} {g(bb, T) * W:7.1f}")
    raw = sorted([tw] + [tw + ps * 1e-12 for ps in P.WRITE] + [toff, S["bl_done"], S["hold_end"]] + (list(S["tset"]) if S["tset"] else []) + ([S["test"]] if S["test"] else []))
    pts = []
    for x in raw:
        if x <= min(t[-1], T[-1]) + 1e-15 and (not pts or x > pts[-1] + 1e-15): pts.append(x)
    print("   interval [ps]        | Cs dV [fC]  integral I_sn [fC] (e / h / displacement)    residual | trapezoid instead: residual | mean Cs dV/dt [uA]  paper [uA] | BL contact charge [fC]")
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        if S["reset"] and a < S["tset"][1] - 1e-15 and b > S["tset"][0] + 1e-15: continue
        # after a reset the node value at a is the one after the Set (last copy): at() interpolates on the later copy only at a > the duplicate
        v_a = at(t, sn, a) if not (S["reset"] and abs(a - S["tset"][1]) < 1e-15) else at(t, sn, a + 1e-16)
        dq = cs * (first_at(t, sn, b) - v_a); ii = {n: sg * (first_at(T, c, b) - at(T, c, a)) for n, c in cq.items()}
        r = dq - ii["TotalCurrent"]; rt = dq - sg * (first_at(T, trap, b) - at(T, trap, a)); pi = f"{PAPER_I[i]:5d}" if i < 4 else "    -"
        pc = lambda x: f"{100 * x / dq:+6.1f} %" if abs(dq) > 1e-19 else "     - "
        print(f"   {a * 1e12:6.1f} - {b * 1e12:6.1f}   | {dq * 1e15:+8.4f}   {ii['TotalCurrent'] * 1e15:+8.4f} ({ii['eCurrent'] * 1e15:+.4f} / {ii['hCurrent'] * 1e15:+.4f} / {ii['DisplacementCurrent'] * 1e15:+.4f})"
              f"  {r * 1e15:+8.4f} ({pc(r)}) | {rt * 1e15:+8.4f} ({pc(rt)}) | {dq / (b - a) * 1e6:10.1f}       {pi}     | {sg * (first_at(T, cbl, b) - at(T, cbl, a)) * 1e15:+8.4f}")
    if S["reset"]:
        vb = first_at(t, sn, S["tset"][0])
        print(f"   reset window: node {vb:.4f} -> {p['SNset']} V, charge added by the circuit Cs x {p['SNset'] - vb:+.4f} V = {cs * (p['SNset'] - vb) * 1e15:+.4f} fC ({cs * (p['SNset'] - vb) / Q:.0f} electrons' worth)")
    if dc:
        ll = glob.glob(os.path.join(RUNS, dc, "LL_*.plt"))
        if ll:
            L = load(ll[0]); lv = L["sn_v OuterVoltage"]; li = [abs(x) * 0.1 for x in L["sn_v TotalCurrent"]]
            near = lambda xs, ys, x: min(zip(xs, ys), key=lambda q: abs(q[0] - x))[1]
            print(f"   DC load line {dc} (gates {p['Vpp']} V, BL {p['Vwr'] or p['Vdd']} V) against the transient's contact current at the same node voltage [uA]:")
            for lab, x in [(f"+{ps} ps", tw + ps * 1e-12) for ps in P.WRITE]:
                v = at(t, sn, x); print(f"      {lab:8s} node {v:.3f} V: transient {sg * at(T, isn, x) * 1e6:7.1f}   DC {near(lv, li, v) * 1e6:7.1f}")
    vs = voltage_split(dv, p, [tw + ps * 1e-12 for ps in P.WRITE])
    if vs:
        print("   BL-to-node drop of the electron quasi-Fermi potential: pillar and contact | body under the BL-side spacer | gated channel | source")
        for x, tot, sh in vs: print(f"      {(x - tw) * 1e12:4.0f} ps: {tot * 1e3:6.0f} mV = " + (" | ".join(f"{100 * q:4.0f} %" for q in sh) if sh else "-"))


def selfcheck():
    assert first_at([0, 1, 2, 2, 3], [0, 1, 2, 9, 9], 2) == 2 and first_at([0, 1, 2], [0, 1, 2], 1.5) == 1.5
    p = dict(tWr=0.105, Vwr=1.168, Vdd=1.1, SNset=1.1, tHold=0.05)
    s = schedule(p, {"tS": 2.45e-10}, "RH"); assert abs(s["wl_off"] - 120e-12) < 1e-18 and abs(s["tset"][0] - 130e-12) < 1e-18 and abs(s["hold_end"] - 190e-12) < 1e-18 and s["reset"]
    w = schedule(p, {"tS": 1.8e-10}, "W"); assert w["tset"] is None and not w["reset"] and abs(w["hold_end"] - 180e-12) < 1e-18
    assert cum([0, 1, 2], [0, 2, 4], be=True) == [0, 2, 6] and cum([0, 1, 2], [0, 2, 4]) == [0, 1, 4]


if __name__ == "__main__":
    selfcheck()
    a = sys.argv[1:]; dc = a[a.index("--dc") + 1] if "--dc" in a else None
    rids = [x for i, x in enumerate(a) if x not in ("-n", "--dc") and (i == 0 or a[i - 1] != "--dc")]
    for rid in rids:
        if "-n" in a:
            for f in sorted(glob.glob(os.path.join(RUNS, rid, "*.plt"))): print(f"== {os.path.basename(f)}"); print("\n".join(load(f)))
        else: report(rid, dc)
