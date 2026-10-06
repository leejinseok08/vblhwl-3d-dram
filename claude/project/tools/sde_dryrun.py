# -*- coding: utf-8 -*-
"""
sde_dryrun.py — Sentaurus 없이 sde_dvs.cmd를 '건식 실행'하는 검증 도구

- SWB @param@ 를 값으로 바꾼 뒤, 작은 Scheme 해석기로 스크립트를 실제로 실행한다.
- sdegeo/sdedr 함수는 기록만 하는 스텁이다 (ABA 덮어쓰기 순서, 접점, 도핑 창 기록).
- 확인하는 것: 문법·괄호, 정의 안 된 변수, 인자 개수, 접점 위치에 원하는 영역이 있는지,
  금속 영역을 올바로 집었는지, 영역 이름 중복, 도핑 창이 소자 안에 있는지.
- 결과 그림: 단면(재료·접점)과 채널 중심선 도핑 프로파일(의도한 해석 기준).

사용:  python sde_dryrun.py ../sde_dvs.cmd  [--set Ncell=2 Arr=FaceStack ...]  --png out.png
Sentaurus 실제 동작(메시, 프로파일 방향 'Positive/Negative')까지 보장하지는 않는다.
"""
import re, sys, os, math, argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from params import P            # params.py is the single source of values
DEFAULTS = dict(P)
DEFAULTS["node"] = 1

# ---------------- tiny Scheme ----------------
class Sym(str): pass
def tokenize(s):
    s = re.sub(r";[^\n]*", "", s)
    toks = re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|\'|[^\s()\']+', s)
    return toks
def parse(toks):
    out = []
    def read(i):
        t = toks[i]
        if t == "(":
            lst = []; i += 1
            while toks[i] != ")":
                v, i = read(i); lst.append(v)
            return lst, i + 1
        if t == ")": raise SyntaxError("unexpected )")
        if t == "'":
            v, i = read(i + 1); return ["quote", v], i
        if t.startswith('"'): return ("str", t[1:-1]), i + 1
        try: return float(t) if re.search(r"[.eE]", t) else int(t), i + 1
        except ValueError: return Sym(t), i + 1
    i = 0
    while i < len(toks):
        v, i = read(i); out.append(v)
    return out

class Env(dict):
    def __init__(self, params=(), args=(), outer=None):
        super().__init__(zip(params, args)); self.outer = outer
    def find(self, k):
        if k in self: return self
        if self.outer is None: raise NameError(f"undefined: {k}")
        return self.outer.find(k)

class Proc:
    def __init__(self, params, body, env, name="lambda"):
        self.params, self.body, self.env, self.name = params, body, env, name
    def __call__(self, *a):
        if len(a) != len(self.params):
            raise TypeError(f"{self.name}: expected {len(self.params)} args, got {len(a)}")
        e = Env(self.params, a, self.env); r = None
        for b in self.body: r = ev(b, e)
        return r

def ev(x, env):
    if isinstance(x, Sym): return env.find(x)[x]
    if isinstance(x, tuple): return x[1]
    if not isinstance(x, list): return x
    if not x: return []
    op = x[0]
    if op == "quote": return x[1]
    if op == "if":
        c = ev(x[1], env)
        if c is not False: return ev(x[2], env)
        return ev(x[3], env) if len(x) > 3 else None
    if op == "cond":
        for cl in x[1:]:
            if cl[0] == "else" or ev(cl[0], env) is not False:
                r = None
                for b in cl[1:]: r = ev(b, env)
                return r
        return None
    if op == "define":
        if isinstance(x[1], list):
            name = x[1][0]; env[name] = Proc(x[1][1:], x[2:], env, name)
        else: env[x[1]] = ev(x[2], env)
        return None
    if op == "set!":
        env.find(x[1])[x[1]] = ev(x[2], env); return None
    if op == "lambda": return Proc(x[1], x[2:], env)
    if op == "begin":
        r = None
        for b in x[1:]: r = ev(b, env)
        return r
    if op == "let*":
        e = Env(outer=env)
        for (k, v) in x[1]: e[k] = ev(v, e)
        r = None
        for b in x[2:]: r = ev(b, e)
        return r
    f = ev(op, env); args = [ev(a, env) for a in x[1:]]
    try:
        return f(*args)
    except TypeError as err:
        raise TypeError(f"in ({op} ...): {err}")

def scm_bool(v): return v
def mk_global(rec):
    g = Env()
    num = lambda *a: a
    g.update({
        "+": lambda *a: sum(a), "*": lambda *a: math.prod(a),
        "-": lambda a, *b: -a if not b else a - sum(b),
        "/": lambda a, *b: 1.0 / a if not b else a / math.prod(b),
        "=": lambda a, b: a == b, "<": lambda a, b: a < b, ">": lambda a, b: a > b,
        "min": min, "max": max, "list": lambda *a: list(a), "append": lambda *a: [v for l in a for v in l],
        "list-ref": lambda l, k: l[k], "string-append": lambda *a: "".join(a),
        "string=?": lambda a, b: a == b,
        "abs": abs, "exp": math.exp, "log": math.log, "sqrt": math.sqrt, "number->string": lambda v: str(v),
        "for-each": lambda f, l: [f(v) for v in l] and None, "car": lambda l: l[0] if isinstance(l, list) else l,
        "position": lambda x, y, z: (x, y, z), "color:rgb": lambda r, g_, b: (r, g_, b),
    })
    for name in ["sde:clear", "sdegeo:set-default-boolean", "sde:save-model", "sde:build-mesh"]:
        g[name] = (lambda n: (lambda *a: rec.call(n, a)))(name)
    g["sdegeo:create-rectangle"] = lambda p1, p2, m, n: rec.box(p1, p2, m, n)
    g["sdegeo:create-cuboid"] = lambda p1, p2, m, n: rec.box(p1, p2, m, n)
    g["sdegeo:define-contact-set"] = lambda n, w, c, s: rec.cset(n)
    g["sdegeo:set-current-contact-set"] = lambda n: rec.setcur(n)
    g["find-edge-id"] = lambda p: ("edge", p)
    g["find-face-id"] = lambda p: ("edge", p)
    g["find-body-id"] = lambda p: rec.body_at(p)
    g["sdegeo:define-2d-contact"] = lambda e, n: rec.edge_contact(e, n)
    g["sdegeo:define-3d-contact"] = lambda e, n: rec.edge_contact(e, n)
    g["sdegeo:set-contact-boundary-edges"] = lambda b: rec.body_contact(b)
    g["sdegeo:set-contact-boundary-faces"] = lambda b: rec.body_contact(b)
    g["sdegeo:delete-region"] = lambda b: rec.delete(b)
    g["sdedr:define-refeval-window"] = lambda n, t, p1, p2: rec.window(n, t, p1, p2)
    g["sdedr:define-constant-profile"] = lambda n, sp, v: rec.prof(n, ("const", sp, v))
    g["sdedr:define-constant-profile-material"] = lambda n, p, m: rec.place(n, p, ("material", m))
    g["sdedr:define-constant-profile-placement"] = lambda n, p, w: rec.place(n, p, w)
    g["sdedr:define-constant-profile-region"] = lambda n, p, r: rec.place(n, p, ("region", r))
    # (... "PeakPos" p "PeakVal" v "StdDev" s | "ValueAtDepth" v "Depth" d  "Erf"|"Gauss" "Factor" f): keyword + number pairs
    g["sdedr:define-gaussian-profile"] = lambda n, sp, *kv: rec.prof(n, ("gauss", sp, dict(
        (kv[i], kv[i + 1]) for i in range(len(kv) - 1) if isinstance(kv[i], str) and not isinstance(kv[i + 1], str))))
    # (... "SymPos" s "MaxVal" m "Length" l "Erf" "Factor" f)
    g["sdedr:define-erf-profile"] = lambda n, sp, *kv: rec.prof(n, ("erf", sp, dict(SymPos=kv[1], MaxVal=kv[3], Length=kv[5], Factor=kv[8])))
    g["sdedr:define-analytical-profile-placement"] = lambda n, p, w, d, r, e: rec.place(n, p, w, d)
    g["sdedr:define-refinement-size"] = lambda n, *a: rec.call("rsize", (n,) + a)
    g["sdedr:define-refinement-placement"] = lambda n, s, w: rec.call("rplace", (n, s, w))
    g["sdedr:define-refinement-function"] = lambda n, *a: rec.call("rfunc", (n,) + a)
    return g

class Recorder:
    def __init__(self):
        self.boxes = []; self.contacts = {}; self.cur = None; self.windows = {}
        self.profiles = {}; self.places = []; self.log = []; self.errors = []; self.csets = set()
    def call(self, n, a): self.log.append((n, a))
    def box(self, p1, p2, m, n):
        if any(b["name"] == n for b in self.boxes): self.errors.append(f"duplicate region name {n}")
        if not (p1[0] < p2[0] and p1[1] < p2[1]): self.errors.append(f"degenerate box {n}: {p1}->{p2}")
        self.boxes.append(dict(x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1], z1=p1[2], z2=p2[2], mat=m, name=n, deleted=False))
    def body_at(self, p):
        for b in reversed(self.boxes):
            if b["deleted"]: continue
            if b["x1"] < p[0] < b["x2"] and b["y1"] < p[1] < b["y2"] and (b["z1"] == b["z2"] or b["z1"] <= p[2] <= b["z2"]):
                return b
        self.errors.append(f"find-body-id: nothing at {p}"); return None
    def cset(self, n):
        if n in self.csets: self.errors.append(f"contact set defined twice: {n}")
        self.csets.add(n); self.contacts.setdefault(n, [])
    def setcur(self, n): self.cur = n
    def edge_contact(self, e, n):
        p = e[1]
        if n not in self.csets: self.errors.append(f"contact {n} used before define-contact-set")
        on = [b for b in self.boxes if not b["deleted"] and b["mat"] == "Silicon" and
              b["x1"] <= p[0] <= b["x2"] and b["y1"] <= p[1] <= b["y2"] and
              (abs(p[0] - b["x1"]) < 1e-12 or abs(p[0] - b["x2"]) < 1e-12 or abs(p[1] - b["y1"]) < 1e-12 or abs(p[1] - b["y2"]) < 1e-12)]
        if not on: self.errors.append(f"edge contact {n}: point {p} is not on a silicon boundary")
        self.contacts[n].append(("edge", p, [b["name"] for b in on]))
    def body_contact(self, b):
        if b is None: return
        if b["mat"] not in ("Metal", "TiN", "Tungsten"): self.errors.append(f"contact {self.cur}: picked non-metal body {b['name']}")
        self.contacts[self.cur].append(("body", b["name"], b))
    def delete(self, b):
        if b is not None: b["deleted"] = True
    def window(self, n, t, p1, p2): self.windows[n] = (t, p1, p2)
    def prof(self, n, d): self.profiles[n] = d
    def place(self, n, p, w, d=None):
        if p not in self.profiles: self.errors.append(f"placement {n}: unknown profile {p}")
        if isinstance(w, str) and w not in self.windows: self.errors.append(f"placement {n}: unknown window {w}")
        self.places.append((n, p, w, d))

def run(path, params):
    src = open(path, encoding="utf-8").read()
    def sub(m):
        k = m.group(1)
        if k not in params: raise KeyError(f"SWB parameter @{k}@ has no value")
        return str(params[k])
    src = re.sub(r"@([A-Za-z_]\w*)@", sub, src)
    rec = Recorder(); g = mk_global(rec)
    for form in parse(tokenize(src)): ev(form, g)
    return rec, g

# ---------------- doping along a vertical line (intended semantics) ----------------
def doping_line(rec, g, x, ys):
    up = g["DIRUP"]
    net = []
    for y in ys:
        nd = na = 0.0
        for (n, p, w, d) in rec.places:
            kind = rec.profiles[p]
            if isinstance(w, tuple):   # material placement (background)
                v = kind[2]; sp = kind[1]
                if any((not b["deleted"]) and b["mat"] == "Silicon" and b["x1"] <= x <= b["x2"] and b["y1"] <= y <= b["y2"] for b in rec.boxes):
                    na += v if "Boron" in sp else 0; nd += v if "Phosph" in sp else 0
                continue
            t, p1, p2 = rec.windows[w]
            if kind[0] == "const":
                if p1[0] <= x <= p2[0] and p1[1] <= y <= p2[1]:
                    if "Boron" in kind[1]: na += kind[2]
                    else: nd += kind[2]
            else:                                  # erf or gauss along the primary direction
                pk = kind[2]; lat = 1.0
                if kind[0] == "erf": L = pk["Length"]
                else:
                    sig = pk["StdDev"] if "StdDev" in pk else pk["Depth"] / math.sqrt(2 * math.log(pk["PeakVal"] / pk["ValueAtDepth"]))
                    L = sig * math.sqrt(2)
                if p1[0] == p2[0]:                 # vertical baseline drawn upward: "Positive" = left side = -x
                    dist = (p1[0] - x) if d == up else (x - p1[0])
                    ya, yb = sorted((p1[1], p2[1])); lw = pk.get("Factor", 0) * L; din = min(y - ya, yb - y)
                    # lateral erf as Sentaurus Mesh applies it: measured from the nearer end of the baseline only
                    lat = 0.5 * (1 + math.erf(din / lw)) if lw > 0 else float(din >= 0)
                else:                              # horizontal baseline: primary direction along y
                    if not (p1[0] <= x <= p2[0]): continue
                    dist = (y - p1[1]) if d == up else (p1[1] - y)
                if dist < 0: continue
                if kind[0] == "erf": v = pk["MaxVal"] / 2 * (1 - math.erf((dist - pk["SymPos"]) / L)) * lat
                else: v = pk["PeakVal"] * math.exp(-((dist - pk.get("PeakPos", 0)) / L) ** 2) * lat
                if "Boron" in kind[1]: na += v
                else: nd += v
        net.append(nd - na)
    return net

def plot(rec, g, png, title):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    col = {"Silicon": "#f3e2c4", "SiO2": "#cfe3f5", "HfO2": "#f4d35e", "TiN": "#a89f77", "Tungsten": "#9aa5b1"}
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 6.2), gridspec_kw=dict(width_ratios=[2.2, 1]))
    for b in rec.boxes:
        fc = "#ffffff" if b["deleted"] else col.get(b["mat"], "#eee")
        hatch = "///" if b["deleted"] else None
        ax.add_patch(Rectangle((b["x1"] * 1e3, b["y1"] * 1e3), (b["x2"] - b["x1"]) * 1e3, (b["y2"] - b["y1"]) * 1e3,
                               fc=fc, ec="#555", lw=0.4, hatch=hatch))
    # body/silicon doping tint
    for n, lst in rec.contacts.items():
        for c in lst:
            if c[0] == "edge":
                p = c[1]; ax.plot(p[0] * 1e3, p[1] * 1e3, "o", color="crimson", ms=6)
                ax.annotate(n, (p[0] * 1e3, p[1] * 1e3), xytext=(3, 3), textcoords="offset points", fontsize=8, color="crimson")
            else:
                b = c[2]; xc = (b["x1"] + b["x2"]) / 2 * 1e3; yc = (b["y1"] + b["y2"]) / 2 * 1e3
                ax.annotate(n, (xc, yc), ha="center", va="center", fontsize=7.5, color="#b00020", weight="bold")
    xmax = max(b["x2"] for b in rec.boxes) * 1e3; ymax = max(b["y2"] for b in rec.boxes) * 1e3
    ax.set_xlim(-3, xmax + 3); ax.set_ylim(-3, ymax + 3); ax.set_aspect("equal")
    ax.set_xlabel("x [nm]"); ax.set_ylabel("y [nm]"); ax.set_title(title, fontsize=10)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=c, ec="#555", label=m) for m, c in col.items()] +
              [Patch(fc="white", ec="#555", hatch="///", label="removed metal = contact")],
              loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8)
    # doping along victim channel centre
    X0 = g["X0"][0]; S = g["SS"][0]; xc = X0 + S * g["Wch"] / 2
    ys = [i * g["ytop"] / 600 for i in range(601)]
    net = doping_line(rec, g, xc, ys)
    ax2.plot([abs(v) for v in net], [y * 1e3 for y in ys], color="k")
    for i in range(len(ys) - 1):
        ax2.axhspan(ys[i] * 1e3, ys[i + 1] * 1e3, color="#3b82c4" if net[i] > 0 else "#d1495b", alpha=0.08, lw=0)
    ax2.set_xscale("log"); ax2.set_xlim(1e14, 3e20); ax2.set_ylim(0, g["ytop"] * 1e3)
    ax2.set_xlabel("|N_D − N_A| [cm⁻³]  (blue n, red p)"); ax2.set_title("victim channel centre (intended)", fontsize=10)
    for yy, lab in [(g["Hsd"], "BL N+ top"), (g["y1"], "gate start"), (g["y2"], "body"), (g["y3"], "body top"), (g["y4"], "gate end"), (g["y5"], "SN N+")]:
        ax2.axhline(yy * 1e3, color="#888", lw=0.5, ls=":"); ax2.text(1.2e14, yy * 1e3 + 1, lab, fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(png, dpi=130); plt.close(fig)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd"); ap.add_argument("--set", nargs="*", default=[]); ap.add_argument("--png")
    a = ap.parse_args()
    params = dict(DEFAULTS)
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k in DEFAULTS and not isinstance(DEFAULTS[k], str):
            params[k] = float(v) if re.search(r"[.eE]", v) else int(v)
        else:
            params[k] = v
    rec, g = run(a.cmd, params)
    print(f"regions: {len(rec.boxes)}  contacts: {sorted(rec.contacts)}  placements: {len(rec.places)}")
    for n in sorted(rec.contacts):
        print(f"  {n:7s} <- " + "; ".join(c[1] if c[0] == 'body' else f"edge@({c[1][0]*1e3:.1f},{c[1][1]*1e3:.1f}) on {c[2]}" for c in rec.contacts[n]))
    print("ERRORS:" if rec.errors else "no errors", *rec.errors, sep="\n  ")
    if a.png: plot(rec, g, a.png, f"BodyMode={params['BodyMode']}")
