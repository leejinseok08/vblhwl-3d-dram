# gt_precharge.py [-n] [--dc <load-line run>] <run id> ... : the pre-charge (write -> WL off -> hold) of the Cho transient runs (deck_cho), plan P2
# of 2026-10-09 ("natural pre-charge"). Works on the reset runs (SNset: the node is set to 1.1 V at 130 - 140 ps; before that the run IS the
# natural write), on the natural runs (SNfree / DnwR*) and on Codex's CxN* runs (GT_RUNS=<its runs folder>; read only). Per run:
#   0. how the file was recorded: bare CurrentPlot in every Transient (every accepted step written, so the right-end rule of Transient = BE
#      closes the charge balance) or timed CurrentPlot (steps between the plotted points are missing); every time the file holds twice, with
#      what differs between the copies (a reset changes the node, a segment boundary does not). Rule: the first copy is the state before the
#      circuit changed it, the last copy the state after; nothing is dropped.
#   1. state at the instants of the pre-charge: t = 0 (DC start), WL crossing 0.9 V (MEASURE.md 4.3, interpolated), the four points of Fig.4(a)
#      (12 / 24 / 39 / 60 ps after it), the write peak, WL off (1 ps before / the crossing / 5 ps after), the end of the BL step, before / after
#      the reset window, the BL at Vdd/2, the start of the hammer: SN, BL, WL; body potential at the centre probe and averaged under the gate
#      (ProbeX), hole quasi-Fermi potential, holes in the victim body; the INSTANTANEOUS storage-node current (electron / hole / displacement /
#      total, + = charging the node);
#   2. the write against Fig.4(a) (read: 0.72 / 0.92 / 1.06 / 1.13 V, tolerance +-30 mV) with every error and the worst;
#   3. charge balance per interval: Cs dV of the node against the time integral of the storage-node contact current; the reset window is a
#      clamp (the circuit sets the node) and is listed apart. Next to it the INTERVAL MEAN Cs dV / dt of the model and of the paper (both
#      interval means; never compared with an instantaneous or a DC current);
#   4. --dc <run>: the DC load-line current (deck "load": gates at Vpp, BL at the write level, node swept) next to the transient's
#      INSTANTANEOUS contact current at the same node voltage (both instantaneous; the body and the displacement currents differ, so the DC value
#      is no bound on the transient current);
#   5. with ProbeE in the deck: where the BL-to-node voltage V(nBL) - V(nSN) falls, from the electron quasi-Fermi potential along the victim
#      channel at mid-depth: BL terminal to the pillar axis at the cell (x 2 nm) | pillar to x0 - 3 nm | junction + body under the BL-side spacer | gated
#      channel | source and storage-node contact.
# Units: contact currents of a mixed-mode device are cell currents (AreaFactor = cell width / 1 um in the deck); a DC deck without AreaFactor
# gives A/um and is scaled by its own Wact; body integrals x 1e-13 = carriers in a 100 nm wide cell (as tools/gt_rh_pairs.py). -n prints the
# column names.
import sys, os, re, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
W = 1e-13                          # body integral -> carriers in the 100 nm wide cell
Q = 1.602e-19
TE = 5e-12                         # edge time of deck_cho
PAPER_I = (252, 70, 39, 14)        # uA: interval means Cs dV / dt of Fig.4(a) with 4.2 fF between its points (make_runs.py, round 37)


def cum(T, y, be=False):           # running time integral; be: right end point (the quadrature of Transient = BE), else trapezoid
    o = [0.0]
    for i in range(1, len(T)): o.append(o[-1] + (y[i] if be else (y[i] + y[i - 1]) / 2) * (T[i] - T[i - 1]))
    return o


def first_at(t, v, x):
    """Value at time x; at a time that the file holds twice (a reset), the FIRST copy = the state before the circuit changed it."""
    for i, ti in enumerate(t):
        if ti >= x - 1e-18: return v[i] if ti <= x + 1e-18 or i == 0 else v[i - 1] + (v[i] - v[i - 1]) * (x - t[i - 1]) / ((ti - t[i - 1]) or 1)
    return v[-1]


def last_at(t, v, x):
    """Value at time x; at a time held twice, the LAST copy = the state after the circuit changed it."""
    for i in range(len(t) - 1, -1, -1):
        if t[i] <= x + 1e-18: return v[i] if t[i] >= x - 1e-18 or i == len(t) - 1 else v[i] + (v[i + 1] - v[i]) * (x - t[i]) / ((t[i + 1] - t[i]) or 1)
    return v[0]


def dupes(t, cols):
    """Times held more than once: (time, {column: (first copy, last copy)})."""
    out, i = [], 1
    while i < len(t):
        if t[i] - t[i - 1] <= 1e-21:
            j = i
            while j + 1 < len(t) and t[j + 1] == t[i]: j += 1
            out.append((t[i], {k: (c[i - 1], c[j]) for k, c in cols.items()})); i = j + 1
        else: i += 1
    return out


def schedule(p, sched, test):
    """Times of deck_cho's pre-charge (s): WL edge, WL off, end of the BL step, reset window (FBE / RH decks only), start of the test phase."""
    t1 = 3 * TE + p["tWr"] * 1e-9; t2 = t1 + TE; vw = p["Vwr"] or p["Vdd"]
    if vw != p["Vdd"]: t2 += TE
    tset = (t2, t2 + 2 * TE) if p["SNset"] and test in ("FBE", "RH") else None
    return dict(wl_on=3 * TE, wl_off=t1, bl_done=t2, tset=tset, reset=bool(tset) and not p.get("SNfree", 0),
                hold_end=(tset[1] if tset else t2) + p["tHold"] * 1e-9, test=sched.get("tS"))


def voltage_split(dv, p, ts, vbl, vsn):
    """With ProbeE: shares of V(nBL) - V(nSN) along the victim channel (electron quasi-Fermi potential at mid-depth), at the times ts."""
    qf = {}
    for k in dv:
        m = re.search(r"\(\s*(-?[\d.eE+-]+)\s*[ ,]\s*(-?[\d.eE+-]+)\s*\)", k) if "eQuasiFermiPotential" in k else None
        if m: qf[(round(float(m.group(1)) * 1e3, 1), round(float(m.group(2)) * 1e3, 1))] = dv[k]
    ym = p["Dvox"] / 2 + p["Tgm"] + p["Tox"] + p["Tbody"] / 2; row = sorted(x for (x, y) in qf if abs(y - ym) < 0.6)
    if len(row) < 4: return None
    near = lambda x: min(row, key=lambda a: abs(a - x)); col = lambda x: qf[(near(x), min((y for (a, y) in qf if a == near(x)), key=lambda y: abs(y - ym)))]
    x0 = p["Wbl"] / 2; xg1 = x0 + p["Lsp1"]; xg2 = xg1 + p["Lg"]; T = dv["time"]; out = []
    for t, b0, s0 in zip(ts, vbl, vsn):
        q = [at(T, col(x), t) for x in (row[0], x0 - 3, xg1 + 2, xg2 - 3)]          # x0 - 3, xg1 + 2, xg2 - 3: the points of gt_loadline.py
        tot = b0 - s0; pts = [b0] + q + [s0]
        out.append((t, tot, [(pts[i] - pts[i + 1]) / tot for i in range(5)] if abs(tot) > 1e-6 else None, [near(x) for x in (row[0], x0 - 3, xg1 + 2, xg2 - 3)]))
    return out


def report(rid, dc=None):
    d = os.path.join(RUNS, rid)
    try:
        s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0]); j = json.load(open(os.path.join(d, "run.json"), encoding="utf-8"))
    except Exception as e:
        print(f"{rid}: no data ({e})"); return
    p = j["params"]; S = schedule(p, j["sched"], j["deck"].split(":")[-1]); t, T = s["time"], dv["time"]; cs = p["Cs"]
    deck = open(os.path.join(d, rid + "_des.cmd"), errors="replace").read(); sol = deck[deck.find("Solve"):]
    be = bool(re.search(r"Transient\s*=\s*BE\b", deck)); n_tr = sol.count("Transient("); n_bare = len(re.findall(r"CurrentPlot\s*\}", sol))
    full = n_tr > 0 and n_bare == n_tr
    k = lambda n: next(x for x in s if n in x); sn, bl, wl = s[k("nSN)")], s[k("nBL")], s[k("nWL)")]
    kb = next((x for x in dv if "ElectrostaticPotential" in x and x.startswith("Pos(")), None); kh = kb.replace("ElectrostaticPotential", "hQuasiFermiPotential") if kb else None
    if kh not in dv: kh = None
    xg = (p["Wbl"] / 2 + p["Lsp1"]) / 1000
    ka = next((x for x in dv if "ElectrostaticPotential" in x and "Window" in x and re.search(r"\(\(\s*([\d.eE+-]+)", x) and abs(float(re.search(r"\(\(\s*([\d.eE+-]+)", x).group(1)) - xg) < 1e-4), None)
    hv = dv[next(x for x in dv if "hDensity" in x and "Ch_a" not in x)]
    sg = None
    ic = {n: dv[f"sn_v {n}"] for n in ("eCurrent", "hCurrent", "DisplacementCurrent", "TotalCurrent")}
    cq = {n: cum(T, c, be) for n, c in ic.items()}; cbl = cum(T, dv["bl TotalCurrent"], be); trap = cum(T, ic["TotalCurrent"])
    up = edges(t, wl, 0, p["Vpp"], True); dn = edges(t, wl, 0, p["Vpp"], False)
    if not up or not dn: print(f"{rid}: write not complete in the file (last time {t[-1] * 1e12:.0f} ps)"); return
    tw, toff = up[0], dn[0]
    # sign of the device file's contact current: + = into the device or out of it (fixed by the write, where the node charges)
    sg = 1.0 if (at(T, cq["TotalCurrent"], toff) - at(T, cq["TotalCurrent"], tw)) * (at(t, sn, toff) - at(t, sn, tw)) > 0 else -1.0
    kind = f"{p['Pair']} pair" if p["Pair"] != "one" else "single cell"
    print(f"== {rid}: {kind}, body {('grounded' if not p.get('Bgi') else 'floating, insulator slot') if p['Bgc'] else 'floating'}{', slot ' + str(p.get('Bgl', 20)) + ' nm' if p['Bgc'] else ''}, avalanche {'on (' + str(p.get('IImod') or 'default') + (', ' + p['IIdf'] if p.get('IIdf') else '') + ')' if p['II'] else 'off'}, "
          f"Cs {cs * 1e15:.2f} fF, BL write {p['Vwr'] or p['Vdd']} V, " + (f"node SET to {p['SNset']} V at {S['tset'][0] * 1e12:.0f}-{S['tset'][1] * 1e12:.0f} ps" if S["reset"] else "node NOT set (natural)")
          + f"; file to {t[-1] * 1e12:.0f} ps; contact current sign: + = {'out of' if sg > 0 else 'into'} the device at sn_v")
    print(f"   record: {'bare CurrentPlot in all ' + str(n_tr) + ' Transients = every accepted step written' if full else f'timed CurrentPlot ({n_bare} of {n_tr} Transients bare): steps between the plotted points are NOT in the file'}; "
          f"{len(t)} / {len(T)} points (system / device); time integration {'BE: charge = step x current at its end (right-end rule)' if be else 'not BE (trapezoid)'}")
    tend = max(S["test"] or 0.0, S["hold_end"]) + 1e-15
    for nm, tt, cols in (("system", t, {"SN": sn, "BL": bl, "WL": wl}), ("device", T, {"I_sn": ic["TotalCurrent"], "holes": hv})):
        dd = dupes(tt, cols); late = [c for x, c in dd if x > tend]
        if late: print(f"   {nm} file: {len(late)} more times held twice after the pre-charge, {sum(all(abs(b[1] - b[0]) < 1e-12 * max(1.0, abs(b[0])) for b in c.values()) for c in late)} of them the same state")
        for x, c in [q for q in dd if q[0] <= tend]:
            diff = {a: b[1] - b[0] for a, b in c.items()}; same = all(abs(v) < 1e-12 * max(1.0, abs(c[a][0])) for a, v in diff.items())
            why = "reset: Set of the node" if S["tset"] and abs(x - S["tset"][0]) < 1e-15 and not same else "end of the reset window" if S["tset"] and abs(x - S["tset"][1]) < 1e-15 else "segment boundary"
            print(f"   {nm} file holds {x * 1e12:8.3f} ps twice ({why}): " + ("same state" if same else ", ".join(f"{a} {b[0]:.6g} -> {b[1]:.6g}" for a, b in c.items())))
    isg = lambda n, x, f=first_at: sg * f(T, ic[n], x) * 1e6
    marks = [("t = 0 (DC start)", t[0]), ("WL crosses 0.9 V", tw)] + [(f"+{ps} ps (paper {v:.2f})", tw + ps * 1e-12) for ps, v in P.WRITE.items()]
    ipk = max((i for i in range(len(t)) if tw <= t[i] <= toff), key=lambda i: sn[i]); marks += [("write peak", t[ipk])]
    marks += [("WL off - 1 ps", toff - 1e-12), ("WL off (0.9 V)", toff), ("WL off + 5 ps", toff + 5e-12), ("BL step done", S["bl_done"])]
    if S["tset"]: marks += [("before reset window" if S["reset"] else "start of the reset window (not set)", S["tset"][0]), ("after reset window", S["tset"][1])]
    marks += [("end of hold at Vdd", S["hold_end"])]
    if S["test"] and j["deck"].endswith("RH"): marks += [("BL at Vdd/2", S["hold_end"] + TE)]
    if S["test"] and S["test"] > S["hold_end"] + 1e-15: marks += [("start of hammer / test", S["test"])]
    marks = sorted([(a, b) for a, b in marks if b <= min(t[-1], T[-1]) + 1e-15], key=lambda q: q[1])
    print("   instant                      t [ps] |  SN [V]   BL [V]   WL [V] | body: centre  under gate  h-QF [V] | holes |  I_sn [uA]: electron    hole  displ.   total")
    for lab, x in marks:
        g = (lambda v, tt=t: last_at(tt, v, x)) if lab == "after reset window" else (lambda v, tt=t: first_at(tt, v, x))
        b = " ".join(f"{g(dv[q], T):+8.4f}" if q else "    -   " for q in (kb, ka, kh))
        cur = " ".join(f"{sg * g(ic[n], T) * 1e6:8.2f}" for n in ("eCurrent", "hCurrent", "DisplacementCurrent", "TotalCurrent"))
        print(f"   {lab:26s} {x * 1e12:8.2f} | {g(sn):.4f}  {g(bl):.4f}  {g(wl):.4f} | {b}   | {g(hv, T) * W:5.0f} | {cur}")
    vw = [first_at(t, sn, tw + ps * 1e-12) for ps in P.WRITE]; er = [1e3 * (v - P.WRITE[ps]) for v, ps in zip(vw, P.WRITE)]
    print("   write vs Fig.4(a) (read, +-30 mV): " + " / ".join(f"{v:.3f} ({e:+.0f} mV {'in' if abs(e) <= 1e3 * P.WRITE_TOL else 'OUT'})" for v, e in zip(vw, er))
          + f"; worst {max(er, key=abs):+.0f} mV at +{list(P.WRITE)[max(range(4), key=lambda i: abs(er[i]))]} ps")
    raw = sorted([tw] + [tw + ps * 1e-12 for ps in P.WRITE] + [toff, S["bl_done"], S["hold_end"]] + (list(S["tset"]) if S["tset"] else []) + ([S["test"]] if S["test"] else []))
    pts = []
    for x in raw:
        if x <= min(t[-1], T[-1]) + 1e-15 and (not pts or x > pts[-1] + 1e-15): pts.append(x)
    print("   interval [ps]          | Cs dV [fC]  integral I_sn [fC] (e / h / displacement)   residual BE | trapezoid: residual | interval mean Cs dV/dt [uA]: model  paper | BL charge [fC]")
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        clamp = S["reset"] and a < S["tset"][1] - 1e-15 and b > S["tset"][0] + 1e-15
        v_a = (first_at if clamp else last_at)(t, sn, a); dq = cs * (first_at(t, sn, b) - v_a); ii = {n: sg * (first_at(T, c, b) - last_at(T, c, a)) for n, c in cq.items()}
        r = dq - ii["TotalCurrent"]; rt = dq - sg * (first_at(T, trap, b) - last_at(T, trap, a)); pi = f"{PAPER_I[i]:5d}" if i < 4 else "    -"
        pc = lambda x: f"{100 * x / dq:+6.1f} %" if abs(dq) > 1e-19 else "     - "
        print(f"   {a * 1e12:7.2f} - {b * 1e12:7.2f}{' clamp' if clamp else '      '}| {dq * 1e15:+8.4f}   {ii['TotalCurrent'] * 1e15:+8.4f} ({ii['eCurrent'] * 1e15:+.4f} / {ii['hCurrent'] * 1e15:+.4f} / {ii['DisplacementCurrent'] * 1e15:+.4f})"
              f"  {r * 1e15:+8.4f} ({pc(r)}) | {rt * 1e15:+8.4f} ({pc(rt)}) |                 {dq / (b - a) * 1e6:8.1f}  {pi} | {sg * (first_at(T, cbl, b) - last_at(T, cbl, a)) * 1e15:+8.4f}")
    if S["reset"]:
        vb, va = first_at(t, sn, S["tset"][0]), last_at(t, sn, S["tset"][0])
        print(f"   reset (clamp): node {vb:.4f} V (first copy at {S['tset'][0] * 1e12:.0f} ps) -> {va:.4f} V (last copy); the circuit adds Cs x {va - vb:+.4f} V = {cs * (va - vb) * 1e15:+.4f} fC ({cs * (va - vb) / Q:.0f} electrons' worth)")
    if dc:
        ll = glob.glob(os.path.join(RUNS, dc, "LL_*.plt"))
        if ll:
            jd = json.load(open(os.path.join(RUNS, dc, "run.json"), encoding="utf-8"))["params"]; dd = open(os.path.join(RUNS, dc, os.path.basename(dc) + "_des.cmd"), errors="replace").read()
            f = 1.0 if "AreaFactor" in dd else jd["Wact"] / 1000
            L = load(ll[0]); lv = L["sn_v OuterVoltage"]; li = [abs(x) * f for x in L["sn_v TotalCurrent"]]
            near = lambda xs, ys, x: min(zip(xs, ys), key=lambda q: abs(q[0] - x))[1]
            print(f"   DC load line {dc} (gates {p['Vpp']} V, BL {p['Vwr'] or p['Vdd']} V; {'AreaFactor in the deck' if f == 1.0 else f'A/um x {f:g} um'}): instantaneous current at the same node voltage [uA]:")
            for lab, x in [(f"+{ps} ps", tw + ps * 1e-12) for ps in P.WRITE]:
                v = at(t, sn, x); print(f"      {lab:8s} node {v:.3f} V: transient {isg('TotalCurrent', x):7.1f}   DC {near(lv, li, v) * 1e6:7.1f}")
    xs = [tw + ps * 1e-12 for ps in P.WRITE]
    vs = voltage_split(dv, p, xs, [at(t, bl, x) for x in xs], [at(t, sn, x) for x in xs])
    if vs:
        print(f"   V(nBL) - V(nSN) along the victim channel (electron QF at x = {' / '.join(f'{a:g}' for a in vs[0][3])} nm): BL terminal -> pillar axis at the cell | pillar to 3 nm before the junction | junction + body under the BL-side spacer | gated channel | source + SN contact")
        for x, tot, sh, _ in vs: print(f"      {(x - tw) * 1e12:4.0f} ps: {tot * 1e3:6.0f} mV = " + (" | ".join(f"{100 * q:4.0f} %" for q in sh) if sh else "-"))


def selfcheck():
    assert first_at([0, 1, 2, 2, 3], [0, 1, 2, 9, 9], 2) == 2 and first_at([0, 1, 2], [0, 1, 2], 1.5) == 1.5
    assert last_at([0, 1, 2, 2, 3], [0, 1, 2, 9, 9], 2) == 9 and last_at([0, 1, 2], [0, 1, 2], 1.5) == 1.5 and last_at([0, 1, 2], [0, 1, 2], 1) == 1
    assert dupes([0, 1, 1, 2], {"a": [5, 6, 7, 8]}) == [(1, {"a": (6, 7)})] and dupes([0, 1, 2], {"a": [1, 2, 3]}) == []
    assert abs(edges([10e-12, 13e-12], [0.0, 1.08], 0, 1.8, True)[0] - 12.5e-12) < 1e-18      # the WL crossing, not the later point (MEASURE.md 4.3)
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
