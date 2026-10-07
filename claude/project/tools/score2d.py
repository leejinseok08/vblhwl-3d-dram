# score2d.py [-v] <config tag> ... : scorecard of 2D device configurations against the paper (tools/paper_targets.py).
# A configuration <tag> is the set of runs D<tag>I_c1..5 (Id-Vg), D<tag>W_c2 (write), D<tag>F_c1..5 (FBE), D<tag>Ry_yy /
# D<tag>Ryi_yy / D<tag>Rz_zz / D<tag>Rzi_zz / D<tag>Rzg_zz (row hammer Y-Y' and Z-Z' without / with impact ionization,
# grounded body). What a configuration does not run itself is taken from the baseline b0 (Id-Vg: the confirmed YE runs).
# Score of a group = root mean square of (simulated - paper) / tolerance; 1 = at the edge of the reading error, the
# smaller the better. Groups: IV Fig.5(c) | W Fig.4(a) | BR Fig.8(a) body rise | L1 loss in the first low phase | L2 loss
# at 200 ns | RH Fig.6(e) | RI Fig.7. Total = root mean square of the groups present.
# Definitions: losses from the storage node voltage when it is charged and the WL is back at 0 V (1.1 V, the start of every
# curve of Fig.8(b), (c)); t_A = just before the first BL fall; body potential = electrostatic potential at the body centre
# under the gate, its rise counted from the start of the transient (everything at 0 V): round 1 showed that the bars of
# Fig.8(a) are "one end potential minus the potential of the depleted body" (NOTES (ax)), which is this difference.
# -v prints the numbers behind each score.
import sys, os, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paper_targets as P
import gt_fig5c as G
from gt_tran import load, at, edges
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
rd = lambda rid: os.path.join(RUNS, rid)
rms = lambda e: math.sqrt(sum(x * x for x in e) / len(e)) if e else float("nan")
elog = lambda s, r: math.log10(max(s, P.FLOOR) / max(r, P.FLOOR)) / P.DEC_TOL

# A configuration whose decks are, line by line, those of runs already made is scored from those runs (checked 2026-10-06:
# fin2 = storage node 1.8 fF, Hurkx Agen 1.7e21, hole charge of Fig.8(a), ideal WL = DfinI / DfinW / Dh1F / DfinR).
COMPOSE = {"fin2": dict(I="fin", W="fin", F="h1", R="fin"), "fin3": dict(I="fin", W="fin", F="s2", R="fin"),
           # 2026-10-07 evening (NOTES (bn)): fin3 on the cells with the BL contact at the pillar end (b), fin3 with the avalanche model off
           # in the FBE and the stand-in rate raised so that the charge is back on the bars (n), both (bn). Their row hammer is fin's (axis contact), not redone.
           "fin3b": dict(I="d0", W="dc", F="dc", R="fin"), "fin3n": dict(I="fin", W="dn", F="dl", R="fin"), "fin3bn": dict(I="d0", W="do", F="dm", R="fin")}
# Reading of Fig.8(a), back-calculated on 2026-10-07 (NOTES (bk); the paper does not say where it reads the body potential): for the FBE
# runs named here the body rise is the AVERAGE electrostatic potential of the body under the gate (column AveWindow, runs with
# ProbeX=1), counted from the start of the transient and read at this offset from the middle of the first BL fall [s]:
# +0.5 ns = 0.25 ns after the fall is complete, -0.3 ns = just before it. Other runs: the body-centre point just before the fall.
AVGREAD = {"s2": 5e-10, "p1": 5e-10, "p2": 5e-10, "s1": -3e-10, "dc": 5e-10, "dd": 5e-10, "de": 5e-10, "dj": 5e-10, "dk": 5e-10, "dl": 5e-10, "dm": 5e-10}
part = lambda tag, k: COMPOSE.get(tag, {}).get(k, tag)
FB = []                                               # filled by first(): True where a baseline run stands in for the configuration's own
def first(*ids):
    if os.path.isdir(rd(ids[0])) and not glob.glob(os.path.join(rd(ids[0]), "*.plt")): return None      # own run planned, nothing written yet: no stand-in
    for i in ids:
        if glob.glob(os.path.join(rd(i), "*.plt")): FB.append(i != ids[0]); return i
    return None

def iv(tag):
    tag = part(tag, "I"); e, txt = [], []
    for c in range(1, 6):
        rid = first(f"D{tag}I_c{c}", f"YE_c{c}")
        try: pts = G.curve(rd(rid))
        except Exception: return None, "no Id-Vg"
        v = {k: G.cross(pts, i) for k, i in (("v10", 1e-10), ("v8", 1e-8), ("v6", 1e-6))}
        v["lm1"] = G.at(pts, -1.0); v["l1"] = G.at(pts, 1.0); v["ss"] = (v["v8"] - v["v10"]) / 2 * 1e3 if None not in (v["v8"], v["v10"]) else None
        for k, tol in P.IV_TOL.items():
            ref = P.IV_SS if k == "ss" else P.IV[c].get(k)
            if ref is None or v[k] is None: continue
            e.append((v[k] - ref) / tol)
        txt.append(f"c{c} {v['v10']:.2f}/{v['v8']:.2f}/{v['v6']:.2f} gidl {v['lm1']:.2f}" if None not in (v["v10"], v["v8"], v["v6"], v["lm1"]) else f"c{c} incomplete")
    return rms(e), "; ".join(txt)

def write(tag):
    tag = part(tag, "W")
    rid = first(f"D{tag}W_c2", "Db0W_c2")
    if not rid: return None, "no write run"
    s = load(os.path.join(rd(rid), rid + "_sys.plt")); t = s["time"]; sn = s[[k for k in s if "nSN)" in k][0]]; wl = s[[k for k in s if "nWL)" in k][0]]
    tw = edges(t, wl, 0, 1.8, True)[0]; v = {ps: at(t, sn, tw + ps * 1e-12) for ps in P.WRITE}
    return rms([(v[ps] - P.WRITE[ps]) / P.WRITE_TOL for ps in P.WRITE]), " / ".join(f"{v[ps]:.2f}" for ps in P.WRITE) + f" V ({rid})"

def fbe(tag):
    tag = part(tag, "F"); er, e1, e2, txt = [], [], [], []
    for c in range(1, 6):
        rid = first(f"D{tag}F_c{c}", f"Db0F_c{c}")
        if not rid: return (None, None, None), "no FBE run"
        s = load(os.path.join(rd(rid), rid + "_sys.plt")); dv = load(glob.glob(os.path.join(rd(rid), "*_dev.plt"))[0])
        t = s["time"]; key = lambda n: next(k for k in s if n in k); sn, bl, wl = s[key("nSN)")], s[key("nBL")], s[key("nWL)")]
        tw0 = edges(t, wl, 0, 1.8, False); f = edges(t, bl, 0, 1.1, False); r = [x for x in edges(t, bl, 0, 1.1, True) if f and x > f[0]]
        if not (tw0 and f and r): txt.append(f"c{c} not far enough"); continue
        t0 = tw0[0] + 4e-11; tA = f[0] - 3e-10; T = dv["time"]; kv = [k for k in dv if "ElectrostaticPotential" in k][0]
        ka = [k for k in dv if k.startswith("AveWindow((0.075") and "ElectrostaticPotential" in k] if tag in AVGREAD else []
        rise = (at(T, dv[ka[0]], f[0] + AVGREAD[tag]) - dv[ka[0]][0]) * 1e3 if ka else (at(T, dv[kv], tA) - dv[kv][0]) * 1e3; v0 = at(t, sn, t0)
        l1 = (v0 - at(t, sn, r[0] - 3e-10)) * 1e3; l2 = (v0 - at(t, sn, min(t[-1], t0 + 2e-7))) * 1e3 if t[-1] >= t0 + 1.9e-7 else None
        er.append((rise - P.FBE_RISE[c]) / P.FBE_RISE_TOL)
        flat = P.FBE_FLAT.get(c)                      # curve on the 1.1 V line in the paper: linear, loss / reading error
        e1.append(l1 / flat if flat else elog(l1, P.FBE_FIRST[c]))
        last = P.FBE_LAST.get(c)                      # curve that ends before 200 ns in the paper: its last readable plateau instead
        if last: l2 = (v0 - at(t, sn, r[last[0] - 1] - 3e-10)) * 1e3 if len(r) >= last[0] else None
        if l2 is not None: e2.append(l2 / flat if flat else elog(l2, last[1] if last else P.FBE_200[c]))
        txt.append(f"c{c} rise {rise:+.0f} first {l1:.2f} {f'after {last[0]} low phases' if last else '200ns'} {'-' if l2 is None else format(l2, '.2f')} (SN0 {v0:.3f})")
    return (rms(er), rms(e1), rms(e2)), "; ".join(txt)

def rh_run(rid):
    s = load(os.path.join(rd(rid), rid + "_sys.plt")); t = s["time"]; sn = s[[k for k in s if "nSN)" in k][0]]; wa = s[[k for k in s if "nWLa" in k][0]]
    r = edges(t, wa, 0, 1.8, True)
    if len(r) < 2: return None
    per = r[1] - r[0]; v = [at(t, sn, x - 2e-11) for x in r] + ([at(t, sn, r[-1] + per - 2e-11)] if t[-1] >= r[-1] + per - 2e-11 else [])
    n = len(v) - 1
    return dict(n=n, tot=(v[0] - v[-1]) * 1e3, per=(v[0] - v[-1]) / n * 1e3, last=(v[-6] - v[-1]) / 5 * 1e3 if n >= 6 else None)

def rh(tag):
    tag = part(tag, "R"); e, ei, txt = [], [], []
    for k, rid, ref in (("yy", f"D{tag}Ry_yy", P.RH["yy"]), ("zz", f"D{tag}Rz_zz", P.RH["zz"])):
        rid = first(rid, rid.replace(f"D{tag}", "Db0"))
        m = rh_run(rid) if rid else None
        if not m or m["n"] < 10: txt.append(f"{k} off: not complete"); continue
        e.append(elog(m["per"], ref)); txt.append(f"{k} off {m['per']:+.4f} (last 5: {m['last']:+.4f})")
    for k, rid, ref, kind in (("yy", f"D{tag}Ryi_yy", P.RH_II["yy"], "per"), ("zz", f"D{tag}Rzi_zz", P.RH_II["zz_drop"], "tot"), ("zz gnd", f"D{tag}Rzg_zz", P.RH_II["zz_gnd"], "per")):
        rid = first(rid, rid.replace(f"D{tag}", "Db0"))
        m = rh_run(rid) if rid else None
        if not m or m["n"] < 10: txt.append(f"{k} on: not complete"); continue
        ei.append(elog(m[kind], ref)); txt.append(f"{k} on {m[kind]:+.4f}{' mV total' if kind == 'tot' else ''}")
    return (rms(e), rms(ei)), "; ".join(txt)

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "-v"]; verbose = "-v" in sys.argv
    print("config      IV      W       BR      L1      L2      RH      RI    | total   (rms of deviation / tolerance, < 1 = within reading error; * = taken from the baseline, - = not there yet)")
    for tag in args:
        g, star, notes = {}, {}, []
        for keys, fn in ((("IV",), iv), (("W",), write), (("BR", "L1", "L2"), fbe), (("RH", "RI"), rh)):
            FB.clear()
            try: v, n = fn(tag)
            except Exception as x: v, n = None, f"{type(x).__name__}: {x}"
            for k, x in zip(keys, v if isinstance(v, tuple) else (v,) * len(keys)): g[k] = x; star[k] = "*" if any(FB) else " "
            notes.append(f"{keys[0]}: {n}")
        ok = [v for v in g.values() if v is not None and v == v]
        f = lambda k: "   -   " if g.get(k) is None or g[k] != g[k] else f"{g[k]:6.2f}{star[k]}"
        print(f"{tag:8s} " + " ".join(f(k) for k in ("IV", "W", "BR", "L1", "L2", "RH", "RI")) + f" | {rms(ok):6.2f}")
        if verbose:
            for n in notes: print("      " + n[:600])
