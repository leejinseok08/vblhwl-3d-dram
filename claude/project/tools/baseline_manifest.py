# baseline_manifest.py <config> [out.json] : the frozen inputs of a configuration of tools/score2d.py (plan P0 of 2026-10-09: "fin7 input
# table"), read on the server from the run folders themselves. Per run: deck, parameter file and mesh with SHA-256, the hash of the deck's
# Physics sections and of its parameter file (the model set: MEASURE.md principle 7, one configuration = one set of physics models, except
# where the paper itself divides: Fig.6(e) off / Fig.7 on), the structure and the main parameters from run.json, and whether the run is
# complete (last time of the system plot = the deck's end; Id-Vg: the current file closed). The runs are COMPOSE[config] of score2d.py plus
# the idle controls (score2d.IDLE). Nothing is changed.
import sys, os, re, json, glob, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score2d as S

KEYS = ("Tbody", "Nch", "WFs", "WFd", "Cs", "II", "IImod", "IIdf", "Par", "Pair", "Blc", "Blx", "Bgc", "SNset", "SNfree", "Gb", "Ncyc", "Idle", "Temp", "Vdd", "Vpp", "Vwr", "tWr")
sha = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest() if f and os.path.isfile(f) else None


def physics(txt):
    """The Physics sections of a deck (brace-matched), whitespace-normalised. Lines that are conditions, not models, are left out:
    AreaFactor (the cell width) and the stand-in generation of the FBE decks (Optics, rate per case = params Gb)."""
    txt = "\n".join(l for l in txt.splitlines() if "AreaFactor" not in l and "Optics(" not in l)
    out = []
    for m in re.finditer(r"\bPhysics\b[^{\n]*\{", txt):
        i, d = m.end(), 1
        while d and i < len(txt): d += {"{": 1, "}": -1}.get(txt[i], 0); i += 1
        out.append(" ".join(txt[m.start():i].split()))
    return "\n".join(out)


def runs(cfg):
    c = S.COMPOSE.get(cfg, dict(I=cfg, W=cfg, F=cfg, R=cfg)); ids = []
    ids += [f"D{c['I']}I_c{k}" for k in range(1, 6)] + [f"D{c['W']}W_c2"] + [f"D{c['F']}F_c{k}" for k in range(1, 6)]
    for t in (c["R"], S.IDLE.get(c["R"])):
        if t: ids += [os.path.basename(d) for d in sorted(glob.glob(S.rd(f"D{t}R*")))]
    return ids


def complete(d, rid, j):
    sp = os.path.join(d, rid + "_sys.plt")
    if os.path.isfile(sp):
        t = S.load(sp)["time"]; te = j["sched"].get("tEnd")
        return bool(te) and abs(t[-1] - te) <= 1e-3 * te
    iv = glob.glob(os.path.join(d, "IdVg_*.plt"))
    return bool(iv) and open(iv[0], errors="replace").read().rstrip().endswith("}")


def entry(rid):
    d = S.rd(rid); deck = os.path.join(d, rid + "_des.cmd")
    if not os.path.isfile(deck): return dict(id=rid, state="no run folder / deck")
    txt = open(deck, errors="replace").read(); j = json.load(open(os.path.join(d, "run.json")))
    grid = re.search(r'Grid\s*=\s*"([^"]+)"', txt); par = re.search(r'Parameter\s*=\s*"([^"]+)"', txt)
    gpath = os.path.normpath(os.path.join(d, grid.group(1))) if grid else None
    ppath = os.path.normpath(os.path.join(d, par.group(1))) if par else None
    p = j["params"]
    return dict(id=rid, struct=j["struct"], deck_kind=j["deck"], complete=complete(d, rid, j),
                deck_sha256=sha(deck), mesh=os.path.basename(gpath) if gpath else None, mesh_sha256=sha(gpath),
                par=os.path.basename(ppath) if ppath else None, par_sha256=sha(ppath),
                physics_sha256=hashlib.sha256(physics(txt).encode()).hexdigest()[:16],
                params={k: p[k] for k in KEYS if k in p})


def main(cfg, out):
    rows = [entry(r) for r in runs(cfg)]
    fam = {}
    for r in rows:
        if "physics_sha256" in r: fam.setdefault((r["physics_sha256"], r["par_sha256"][:16] if r["par_sha256"] else None), []).append(r["id"])
    for r in rows:
        print(f"{r['id']:14s} {'ok  ' if r.get('complete') else 'OPEN'} {r.get('struct', ''):10s} mesh {str(r.get('mesh_sha256'))[:12]} "
              f"par {r.get('par', '')} {str(r.get('par_sha256'))[:12]} phys {r.get('physics_sha256', '-')} | "
              + " ".join(f"{k}={v}" for k, v in r.get("params", {}).items() if k in ("Tbody", "Nch", "WFs", "Cs", "II", "Bgc", "Idle", "SNset")))
    print(f"\nmodel sets (Physics sections + parameter file): {len(fam)}")
    for (ph, pa), ids in fam.items(): print(f"  phys {ph} par {pa}: {' '.join(ids)}")
    json.dump(dict(config=cfg, runs=rows, model_sets=[dict(physics=ph, par=pa, runs=ids) for (ph, pa), ids in fam.items()]),
              open(out, "w"), indent=1)
    print(f"-> {out}")


if __name__ == "__main__":
    t = "Physics { A } x Physics( Region=\"r\" ) { B { C } } y"
    assert physics(t) == 'Physics { A }\nPhysics( Region="r" ) { B { C } }'
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else f"baseline_{sys.argv[1]}.json")
