# gt_cap_array.py [run id]: capacitance matrix of the mini array (deck "ac" on ga_*, make_runs.deck_aca) in fF / aF, against the paper:
# C_S per node (text 4.2 fF for Case 2), C_BL per layer ([9] = Hsu .. Yu TED 2026, Table II: 0.2016 fF at BL radius 50 nm), and the direct
# capacitance from a victim node to the aggressor's WL / node in the three row-hammer directions (Fig.3: Y-Y' across the BL = other side,
# same row and layer; Z-Z' = layer above / below, same side; X-X' = next row, same layer and side). The swing a floating victim node sees
# when the aggressor WL goes 0 -> Vpp is C(victim, WL) / C(victim) x 1.8 V (Fig.6(e): X-X' +0.70 mV, Y-Y' none). Contacts held at 0 V,
# so -c(n,m) is the direct (partial) capacitance; c(n,n) the whole capacitance of node n.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_cap import matrix, RUNS

VPP = 1.8


def cc(c, a, b):
    """Direct capacitance between contacts a and b [fF] (c(a,a) for a == b)."""
    a, b = "n" + a, "n" + b
    v = next((c[k] for k in (f"{a},{b}", f"{b},{a}") if k in c), None)
    if v is None: raise KeyError(f"{a},{b}")
    return v if a == b else -v


def neighbours(r, k, s, nr, nk):
    """Aggressor cells of victim sn_<r><k><s> per direction: [(direction, row, layer, side)] inside the array."""
    o = "m" if s == "p" else "p"; out = [("Y", r, k, o)]
    out += [("Z", r, kk, s) for kk in (k - 1, k + 1) if 0 <= kk < nk]
    out += [("X", rr, k, s) for rr in (r - 1, r + 1) if 0 <= rr < nr]
    return out


def table(c, nr=3, nk=5):
    rows = []
    for s in "pm":
        for r in range(nr):
            for k in range(nk):
                v = f"sn_{r}{k}{s}"; tot = cc(c, v, v)
                d = dict(node=v, total=tot, gp=cc(c, v, "gp"), snx=cc(c, v, "snx"), own_wl=cc(c, v, f"wl_{k}{s}"), bl=cc(c, v, f"bl_{r}"))
                for dirn, rr, kk, ss in neighbours(r, k, s, nr, nk):
                    a = f"sn_{rr}{kk}{ss}"; wl = f"wl_{kk}{ss}"
                    # X-X': the mesh's WL is shared by the three rows (the paper cuts it for X-X'), so only node-to-node is meaningful
                    d.setdefault(dirn, []).append(dict(agg=a, sn=cc(c, v, a), wl=None if dirn == "X" else cc(c, v, wl)))
                rows.append(d)
    return rows


def report(rid):
    c = matrix(rid)
    if c is None: print(f"{rid}: no extraction file"); return
    p = json.load(open(os.path.join(RUNS, rid, "run.json")))["params"]; nr, nk = p["Nrow"], p["Nlay"]
    rows = table(c, nr, nk)
    print(f"{rid}: {len(c)} matrix entries, rows {nr}, layers {nk}, BL pillar {p['Wbl']} nm, Lcap {p['Lcap']} nm, EOT {p['Ceot']} A   [fF unless aF]")
    print("node    | C(SN) total | SN-gp  SN-snx  SN-ownWL  SN-BL [aF] | Y: SN-WL SN-SN [aF] | Z: SN-WL SN-SN [aF] (each neighbour) | X: SN-SN [aF]")
    for d in rows:
        z = " ".join(f"{e['wl'] * 1e3:5.2f}/{e['sn'] * 1e3:5.2f}" for e in d["Z"]); x = " ".join(f"{e['sn'] * 1e3:5.2f}" for e in d.get("X", []))
        y = d["Y"][0]
        print(f"{d['node']} | {d['total']:8.3f}    | {d['gp']:6.3f} {d['snx']:6.3f} {d['own_wl']:7.3f} {d['bl'] * 1e3:7.2f}     | {y['wl'] * 1e3:6.2f} {y['sn'] * 1e3:6.2f}     | {z:28s} | {x}")
    inner = [d for d in rows if d["node"][3] == "1" and d["node"][4] in "123"]      # middle row, layers 1 - 3: neighbours on every side
    m = lambda f: sum(f(d) for d in inner) / len(inner)
    tot = m(lambda d: d["total"])
    print(f"\ninner cells (row 1, layers 1-3, both sides; n = {len(inner)}): C(SN) {tot:.3f} fF (text 4.2), SN-gp {m(lambda d: d['gp']):.3f}, own WL {m(lambda d: d['own_wl']):.3f}")
    for dirn in "YZ":
        cw = m(lambda d: sum(e["wl"] for e in d[dirn]) / len(d[dirn])); cs = m(lambda d: sum(e["sn"] for e in d[dirn]) / len(d[dirn]))
        print(f"  {dirn}-{dirn}': SN-aggressor WL {cw * 1e3:.3f} aF -> swing {cw / tot * VPP * 1e3:.3f} mV at Vpp {VPP} V | SN-aggressor SN {cs * 1e3:.3f} aF")
    cs = m(lambda d: sum(e["sn"] for e in d["X"]) / len(d["X"]))
    print(f"  X-X': SN-aggressor SN {cs * 1e3:.3f} aF (WL shared in this mesh; Fig.6(e) +0.70 mV would need {0.70e-3 / VPP * tot * 1e3:.2f} aF to the aggressor WL)")
    print("\nBL pillars: whole capacitance, per layer ([9] Table II: 0.2016 fF per layer = BL-BL 0.0247 + BL-WL 0.1769, BL radius 50 nm)")
    for r in range(nr):
        b = f"bl_{r}"; t = cc(c, b, b); wl = sum(cc(c, b, f"wl_{k}{s}") for k in range(nk) for s in "pm")
        bb = sum(cc(c, b, f"bl_{q}") for q in range(nr) if q != r)
        print(f"  {b}: {t:.4f} fF = {t / nk:.4f} per layer | to all WL {wl:.4f} ({wl / nk:.4f} per layer) | to other BL {bb:.4f} ({bb / nk:.4f}) | rest {t - wl - bb:.4f}")
    big = sorted(((k.split(",")[0], v) for k, v in c.items() if k.split(",")[0] == k.split(",")[1]), key=lambda kv: -kv[1])[:4]
    print("\nlargest whole capacitances: " + ", ".join(f"{k} {v:.3f}" for k, v in big))


if __name__ == "__main__":
    # self-check of the direction rule: a corner cell has one Y, one Z and one X neighbour; an inner cell one Y, two Z, two X
    assert [d for d, *_ in neighbours(0, 0, "p", 3, 5)] == ["Y", "Z", "X"] and len(neighbours(1, 2, "m", 3, 5)) == 5
    for rid in sys.argv[1:] or ["DgaC_c2"]: report(rid)
