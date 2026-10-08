# grd_cut.py <mesh.grd> [--info] [<axis> <at_nm> <out.json>] ... : planar cuts through a 3D Sentaurus mesh, by material.
# The mesh is the DF-ISE text that `tdx -dd <struct>_msh.tdr` writes (the TDR file of this release is not HDF5). Read: vertices,
# edges, faces, the tetrahedra of every region with its material, the triangles of every contact. The cut of a tetrahedron is
# a triangle or a quadrilateral of its material. Metals are contacts here (their bodies are deleted in the structure file),
# i.e. holes in the mesh: the cut of a contact's faces gives closed loops. Each cut goes to a JSON file
# {"axis", "at_nm", "polys": {material: [[[u, v], ..], ..]}, "loops": [[contact, [[u, v], ..]], ..]} in nm, (u, v) = the two
# other axes in the order x, y, z. Drawn on the PC by tools/plot_ga.py. So the picture shows the structure as built.
# Axes of the project's 3D structures: x = the paper's Y (along the channel), y = the paper's Z (stacking), z = the paper's X.
#   --info : vertices, bounding box, regions and tetrahedra by material, contacts with their number of faces.
import sys, re, json, gzip, collections
import numpy as np

def read(path):
    txt = (gzip.open(path, "rt") if path.endswith(".gz") else open(path)).read()
    def sec(name, start=0):
        m = re.compile(r"\b%s \((\d+)\) \{" % name).search(txt, start); e = txt.index("}", m.end())
        return int(m.group(1)), txt[m.end():e], e
    nv, s, p = sec("Vertices"); V = np.array(s.split(), float).reshape(nv, 3)
    ne, s, p = sec("Edges", p); E = np.array(s.split(), np.int64).reshape(ne, 2)
    nf, s, p = sec("Faces", p); F = np.array(s.split(), np.int64).reshape(nf, 4); assert (F[:, 0] == 3).all(), "faces other than triangles"
    nl, s, p = sec("Locations", p)
    nel, s, p = sec("Elements", p); lines = s.strip().split("\n"); assert len(lines) == nel
    code = np.array([int(l.split(None, 1)[0]) for l in lines]); other = collections.Counter(code[(code != 5) & (code != 2)].tolist())
    it = np.flatnonzero(code == 5); ic = np.flatnonzero(code == 2)
    T = np.array(" ".join(lines[i] for i in it).split(), np.int64).reshape(-1, 5)[:, 1:] if len(it) else np.zeros((0, 4), np.int64)
    C = np.array(" ".join(lines[i] for i in ic).split(), np.int64).reshape(-1, 4)[:, 1:] if len(ic) else np.zeros((0, 3), np.int64)
    ix = lambda a: np.where(a < 0, -a - 1, a)
    def tri(e3):                                         # vertices of triangles given by three edges each
        s4 = np.sort(np.concatenate([E[ix(e3[:, 0])], E[ix(e3[:, 1])]], axis=1), axis=1)
        return np.column_stack([s4[:, 0], np.where(s4[:, 1] != s4[:, 0], s4[:, 1], s4[:, 2]), s4[:, 3]])
    FV = tri(F[:, 1:])
    a = FV[ix(T[:, 0])]; b = FV[ix(T[:, 1])]
    inn = lambda q: (q[:, None] == a).any(1)
    TV = np.column_stack([a, np.where(~inn(b[:, 0]), b[:, 0], np.where(~inn(b[:, 1]), b[:, 1], b[:, 2]))])
    CV = tri(C); pos_t = np.full(nel, -1); pos_t[it] = np.arange(len(it)); pos_c = np.full(nel, -1); pos_c[ic] = np.arange(len(ic))
    bulk, cont = [], []
    for m in re.finditer(r'Region \("([^"]+)"\) \{\s*material = (\S+)\s*Elements \((\d+)\) \{([^}]*)\}', txt[p:]):
        ids = np.array(m.group(4).split(), np.int64)
        if m.group(2) == "Contact": cont.append((m.group(1), CV[pos_c[ids][pos_c[ids] >= 0]]))
        else: bulk.append((m.group(1), m.group(2), TV[pos_t[ids][pos_t[ids] >= 0]]))
    return V, bulk, cont, other

def _sect(P, d):                                         # where the plane d = 0 crosses one simplex (points P, signed distances d)
    out = []; n = len(P)
    for i in range(n):
        for j in range(i + 1, n):
            if (d[i] > 0) != (d[j] > 0): out.append(P[i] + (P[j] - P[i]) * (d[i] / (d[i] - d[j])))
    return out

def cut(V, bulk, cont, axis, at):
    ax = "xyz".index(axis); keep = [i for i in range(3) if i != ax]; D = V[:, ax] - at
    polys = collections.defaultdict(list)
    for name, mat, T in bulk:
        if not len(T): continue
        dt = D[T]; m = (dt.max(1) > 0) & (dt.min(1) <= 0)
        for t in T[m]:
            p = np.array(_sect(V[t], D[t]))[:, keep]
            if len(p) == 4:                              # order the four points around their centre
                c = p.mean(0); p = p[np.argsort(np.arctan2(p[:, 1] - c[1], p[:, 0] - c[0]))]
            polys[mat + ("|n" if name.startswith(("R.BL", "R.Src")) else "")].append(np.round(p * 1e3, 2).tolist())      # N+ silicon apart: BL pillar, source
    loops = []
    for name, F in cont:
        if not len(F): continue
        df = D[F]; m = (df.max(1) > 0) & (df.min(1) <= 0); nb = collections.defaultdict(list)
        for f in F[m]:
            s = _sect(V[f], D[f])
            if len(s) == 2:
                a, b = (tuple(np.round(q[keep] * 1e3, 3)) for q in s)
                if a != b: nb[a].append(b); nb[b].append(a)
        seen = set(); chains = []
        def walk(start):
            loop = [start]; seen.add(start); cur = start
            while True:
                nx = [q for q in nb[cur] if q not in seen]
                if not nx: break
                cur = nx[0]; seen.add(cur); loop.append(cur)
            return loop
        for start in [q for q in nb if len(set(nb[q])) == 1]:      # open chains first: the contact reaches the edge of the model, where it has no faces
            if start not in seen: chains.append(walk(start))
        while chains:                                               # join open chains end to nearest end into one outline
            c = chains.pop(0)
            while chains:
                d2 = lambda p, q: (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
                j, rev, dj = min(((j, r, d2(c[-1], ch[-1] if r else ch[0])) for j, ch in enumerate(chains) for r in (0, 1)), key=lambda t: t[2])
                if dj >= d2(c[-1], c[0]): break                     # its own start is nearer: the outline is complete
                ch = chains.pop(j); c += ch[::-1] if rev else ch
            if len(c) >= 3: loops.append([name, [list(q) for q in c]])
        for start in list(nb):
            if start not in seen:
                c = walk(start)
                if len(c) >= 3: loops.append([name, [list(q) for q in c]])
    return polys, loops

if __name__ == "__main__":
    V, bulk, cont, other = read(sys.argv[1]); a = sys.argv[2:]
    if "--info" in a:
        a.remove("--info"); mats = collections.Counter(); tets = collections.Counter()
        for name, mat, T in bulk: mats[mat] += 1; tets[mat] += len(T)
        print("vertices", len(V), "box [nm]", np.round(V.min(0) * 1e3, 2).tolist(), np.round(V.max(0) * 1e3, 2).tolist())
        print("regions by material:", dict(mats)); print("tetrahedra by material:", dict(tets), "| other element codes:", dict(other))
        cc = collections.Counter(re.sub(r"\d", "#", n) for n, F in cont)
        print(len(cont), "contacts:", " ".join(f"{k} x {v}" for k, v in sorted(cc.items())), "| without faces:", [n for n, F in cont if not len(F)])
    for axis, at, out in zip(a[0::3], a[1::3], a[2::3]):
        polys, loops = cut(V, bulk, cont, axis, float(at) * 1e-3)
        json.dump(dict(axis=axis, at_nm=float(at), polys=polys, loops=loops), open(out, "w"))
        print("wrote", out, sum(len(v) for v in polys.values()), "polygons", len(loops), "contact loops")
