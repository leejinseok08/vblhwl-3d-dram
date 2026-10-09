# gt_cap_array.py [run id]: capacitance matrix of the mini array (deck "ac" on ga_* / gax_*, make_runs.deck_aca) in fF / aF, against the paper:
# C_S per node (text 4.2 fF for Case 2), C_BL per layer (Cho's [9] = Hsu .. Yu, IMW 2025: 0.0247 + 0.175 = 0.1997 fF per layer; its extension
# TED 2026, Table II: 0.2016 fF at BL radius 50 nm; 0.185 back-calculated from Fig.5(d): three different numbers), and the direct
# capacitance from a victim node to the aggressor's WL / node in the three row-hammer directions (Fig.3: Y-Y' across the BL = other side,
# same row and layer; Z-Z' = layer above / below, same side; X-X' = next row, same layer and side). The swing a floating victim node sees
# when the aggressor WL goes 0 -> Vpp is C(victim, WL) / C(victim) x 1.8 V to first order (Fig.6(e): X-X' +0.70 mV, Y-Y' none); a small-signal
# estimate at 0 V, not the transient. Contacts held at 0 V, so -c(n,m) is the direct (partial) capacitance; c(n,n) the whole capacitance of n.
# Word lines: ga_* has one WL contact per layer and side shared by the rows (wl_<k><s>, 45 contacts); gax_* one per row (wl_<r><k><s>, 65).
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


def split_wl(c):
    """True for a mesh with one WL per row (wl_<r><k><s>), False for the WL shared by the rows (wl_<k><s>)."""
    return "nwl_00p,nwl_00p" in c


def wl(c, r, k, s):
    return f"wl_{r}{k}{s}" if split_wl(c) else f"wl_{k}{s}"


def table(c, nr=3, nk=5):
    rows = []; sp = split_wl(c)
    for s in "pm":
        for r in range(nr):
            for k in range(nk):
                v = f"sn_{r}{k}{s}"; tot = cc(c, v, v)
                d = dict(node=v, total=tot, gp=cc(c, v, "gp"), snx=cc(c, v, "snx"), own_wl=cc(c, v, wl(c, r, k, s)), bl=cc(c, v, f"bl_{r}"))
                for dirn, rr, kk, ss in neighbours(r, k, s, nr, nk):
                    a = f"sn_{rr}{kk}{ss}"
                    # X-X' on a shared WL: the aggressor's WL is the victim's own (the paper decouples it for X-X'), so only node-to-node is meaningful
                    d.setdefault(dirn, []).append(dict(agg=a, sn=cc(c, v, a), wl=None if dirn == "X" and not sp else cc(c, v, wl(c, rr, kk, ss))))
                rows.append(d)
    return rows


def report(rid):
    c = matrix(rid)
    if c is None: print(f"{rid}: no extraction file"); return
    p = json.load(open(os.path.join(RUNS, rid, "run.json")))["params"]; nr, nk = p["Nrow"], p["Nlay"]
    rows = table(c, nr, nk); sp = split_wl(c)
    print(f"{rid}: {len(c)} matrix entries, rows {nr}, layers {nk}, WL {'one per row' if sp else 'shared by the rows'}, BL pillar {p['Wbl']} nm, "
          f"Lcap {p['Lcap']} nm, EOT {p['Ceot']} A   [fF unless aF]")
    print(f"node    | C(SN) total | SN-gp  SN-snx  SN-ownWL  SN-BL [aF] | Y: SN-WL SN-SN [aF] | Z: SN-WL SN-SN [aF] (each neighbour) | X: {'SN-WL/' if sp else ''}SN-SN [aF]")
    for d in rows:
        z = " ".join(f"{e['wl'] * 1e3:5.2f}/{e['sn'] * 1e3:5.2f}" for e in d["Z"])
        x = " ".join((f"{e['wl'] * 1e3:5.2f}/" if sp else "") + f"{e['sn'] * 1e3:5.2f}" for e in d.get("X", []))
        y = d["Y"][0]
        print(f"{d['node']} | {d['total']:8.3f}    | {d['gp']:6.3f} {d['snx']:6.3f} {d['own_wl']:7.3f} {d['bl'] * 1e3:7.2f}     | {y['wl'] * 1e3:6.2f} {y['sn'] * 1e3:6.2f}     | {z:28s} | {x}")
    inner = [d for d in rows if d["node"][3] == "1" and d["node"][4] in "123"]      # middle row, layers 1 - 3: neighbours on every side
    m = lambda f: sum(f(d) for d in inner) / len(inner)
    tot = m(lambda d: d["total"])
    print(f"\ninner cells (row 1, layers 1-3, both sides; n = {len(inner)}): C(SN) {tot:.3f} fF (text 4.2), SN-gp {m(lambda d: d['gp']):.3f}, own WL {m(lambda d: d['own_wl']):.3f}")
    for dirn in ("YZX" if sp else "YZ"):
        cw = m(lambda d: sum(e["wl"] for e in d[dirn]) / len(d[dirn])); cs = m(lambda d: sum(e["sn"] for e in d[dirn]) / len(d[dirn]))
        print(f"  {dirn}-{dirn}': SN-aggressor WL {cw * 1e3:.3f} aF -> swing {cw / tot * VPP * 1e3:.3f} mV at Vpp {VPP} V | SN-aggressor SN {cs * 1e3:.3f} aF")
    if not sp:
        cs = m(lambda d: sum(e["sn"] for e in d["X"]) / len(d["X"]))
        print(f"  X-X': SN-aggressor SN {cs * 1e3:.3f} aF (WL shared in this mesh)")
    print(f"  Fig.6(e) X-X' +0.70 mV corresponds to {0.70e-3 / VPP * tot * 1e3:.2f} aF to the aggressor WL at this C(SN): a first-order estimate, not a target to fit")
    print("\nBL pillars: whole capacitance, per layer ([9] IMW 2025: 0.1997 fF per layer = BL-BL 0.0247 + BL-WL 0.175; TED 2026 Table II: 0.2016, BL radius 50 nm)")
    wls = sorted({k.split(",")[0][1:] for k in c if k.startswith("nwl_")})
    for r in range(nr):
        b = f"bl_{r}"; t = cc(c, b, b); w = sum(cc(c, b, x) for x in wls)
        bb = sum(cc(c, b, f"bl_{q}") for q in range(nr) if q != r)
        print(f"  {b}: {t:.4f} fF = {t / nk:.4f} per layer | to all WL {w:.4f} ({w / nk:.4f} per layer) | to other BL {bb:.4f} ({bb / nk:.4f}) | rest {t - w - bb:.4f}")
    big = sorted(((k.split(",")[0], v) for k, v in c.items() if k.split(",")[0] == k.split(",")[1]), key=lambda kv: -kv[1])[:4]
    print("\nlargest whole capacitances: " + ", ".join(f"{k} {v:.3f}" for k, v in big))


def selfcheck():
    """Direction rule and contact names, on synthetic matrices of both meshes (every pair present)."""
    assert [d for d, *_ in neighbours(0, 0, "p", 3, 5)] == ["Y", "Z", "X"] and len(neighbours(1, 2, "m", 3, 5)) == 5
    for split in (False, True):
        cs = [f"bl_{r}" for r in range(3)] + [f"sn_{r}{k}{s}" for r in range(3) for k in range(5) for s in "pm"] + ["gp", "snx"]
        cs += [f"wl_{r}{k}{s}" for r in range(3) for k in range(5) for s in "pm"] if split else [f"wl_{k}{s}" for k in range(5) for s in "pm"]
        syn = {f"n{a},n{b}": (3.0 if a == b else -1e-4) for a in cs for b in cs}
        t = table(syn); assert len(cs) == (65 if split else 45) and len(t) == 30
        assert all((e["wl"] is not None) == split for d in t for e in d["X"]) and all(e["wl"] is not None for d in t for e in d["Y"] + d["Z"])


if __name__ == "__main__":
    selfcheck()
    for rid in sys.argv[1:] or ["DgaC_c2"]: report(rid)
