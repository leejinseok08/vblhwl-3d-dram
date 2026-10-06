# gt_fig5c.py <run dir> ... [--png out.png] : Id-Vg of the Cho-device runs against Fig.5(c) of Cho et al., IRPS 2026.
# Works on finished and on running / stopped runs (current file without its closing brace), swept up or down.
# The paper prints "Drain Current [A]". W = factor applied to the 2D current (A/um): default 1 (per um);
# set GT_W=0.1 for a 100 nm wide device (BL pitch 200 nm - isolation wall 100 nm).
#   usage:  GT_W=0.1 python3 tools/gt_fig5c.py runs/XW_c1 runs/XW_c2 ...
# --png (PC, needs matplotlib): the same runs drawn over the paper's curves, which are the pixels of each curve colour in
# the embedded figure image (preview/cho_fig5c_pixels.json; Vg = -1 + (x - 990.0) / 81.83, log10 I = -4 - (y - 420.5) / 15.25).
import sys, os, re, glob, math, json

# Fig.5(c) read from the embedded image (15.25 px per decade, 81.8 px per volt; about +-0.1 decade, +-0.02 V):
# gate voltage where the rising branch crosses 1e-10 / 1e-8 / 1e-6 A, minimum (Vg, log10 I), log10 I at Vg -1 V and +1 V
PAPER = {1: dict(v10=0.34, v8=0.47, v6=0.60, vmin=-0.11, lmin=-16.9, lm1=-13.5, l1=-4.07),
         2: dict(v10=0.33, v8=0.44, v6=0.57, vmin=-0.07, lmin=-16.4, lm1=-13.2, l1=None),
         3: dict(v10=0.30, v8=0.42, v6=0.55, vmin=-0.15, lmin=-16.4, lm1=-13.1, l1=None),
         4: dict(v10=0.26, v8=0.39, v6=0.51, vmin=-0.13, lmin=-16.4, lm1=-13.2, l1=-3.89),
         5: dict(v10=0.53, v8=0.65, v6=0.78, vmin=0.09, lmin=-16.5, lm1=-12.85, l1=-4.52)}   # the legend covers part of this curve: +-0.04 V
W = float(os.environ.get("GT_W", "1"))
HERE = os.path.dirname(os.path.abspath(__file__))


def curve(rd):
    f = glob.glob(os.path.join(rd, "IdVg_*.plt"))[0]; txt = open(f, errors="replace").read()
    names = re.findall(r'"([^"]*)"', re.search(r"datasets\s*=\s*\[(.*?)\]", txt, re.S).group(1))
    nums = [float(x) for x in re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", txt[txt.index("Data"):])]
    n = len(names); rows = [nums[i:i + n] for i in range(0, len(nums) - len(nums) % n, n)]
    kv = names.index("gs_v OuterVoltage"); ki = names.index("sn_v TotalCurrent")
    return sorted((r[kv], abs(r[ki]) * W) for r in rows)


def cross(pts, level):          # gate voltage where the rising branch crosses `level`
    k = min(range(len(pts)), key=lambda j: pts[j][1])
    for (v1, i1), (v2, i2) in zip(pts[k:], pts[k + 1:]):
        if i1 < level <= i2: return v1 + (v2 - v1) * math.log10(level / i1) / math.log10(i2 / i1)
    return None


def at(pts, v):
    for (v1, i1), (v2, i2) in zip(pts, pts[1:]):
        if v1 <= v <= v2 and i1 > 0 and i2 > 0:
            return math.log10(i1) + (math.log10(i2) - math.log10(i1)) * (v - v1) / (v2 - v1 or 1)
    return None


def picture(curves, png):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = ["DejaVu Sans", "Malgun Gothic"]
    pix = json.load(open(os.path.join(HERE, "..", "preview", "cho_fig5c_pixels.json")))
    col = {1: "#0000ff", 2: "#ff0000", 3: "#00c000", 4: "#ffa000", 5: "#ff00ff"}
    lab = {1: "Case 1: 30 nm, 1e18, 4.7 eV", 2: "Case 2: 20 nm, 1e18, 4.7 eV", 3: "Case 3: 10 nm, 1e18, 4.7 eV",
           4: "Case 4: 10 nm, 1e16, 4.7 eV", 5: "Case 5: 10 nm, 1e16, 5.0 eV"}
    def base(k):                # baseline curve: median of the paper's pixels in 0.03 V bins
        bins = {}
        for x, y in pix[k]: bins.setdefault(round((-1 + (x - 990.0) / 81.83) / 0.03), []).append(-4 - (y - 420.5) / 15.25)
        b = [(i * 0.03, sorted(v)[len(v) // 2]) for i, v in sorted(bins.items())]
        # stray pixels (legend, other curves): drop a point more than 0.7 decade off the line through its neighbours
        b = [q for j, q in enumerate(b) if j in (0, len(b) - 1) or abs(q[1] - (b[j - 1][1] + (b[j + 1][1] - b[j - 1][1]) * (q[0] - b[j - 1][0]) / (b[j + 1][0] - b[j - 1][0]))) < 0.7]
        out = []                # no line across parts hidden under other curves
        for j, q in enumerate(b):
            if j and q[0] - b[j - 1][0] > 0.1: out.append((float("nan"), float("nan")))
            out.append(q)
        return out
    fig = plt.figure(figsize=(12.5, 7.6)); gs = fig.add_gridspec(2, 2, height_ratios=[3.2, 1])
    axs = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    for ax, (xl, yl) in zip(axs, (((-1, 2), (-17.5, -3)), ((0.2, 1.9), (-8, -3.3)))):
        for k in sorted(pix):
            c = int(k[1]); bl = base(k)
            ax.plot([-1 + (x - 990.0) / 81.83 for x, y in pix[k]], [-4 - (y - 420.5) / 15.25 for x, y in pix[k]], ".", color=col[c], ms=3, alpha=0.3)
            ax.plot([v for v, l in bl], [l for v, l in bl], "--", color=col[c], lw=1.6, alpha=0.9)
        for c, pts in curves:
            ax.plot([v for v, i in pts], [math.log10(i) for v, i in pts], "-", color=col[c], lw=1.2, label=lab[c])
        ax.set(xlim=xl, ylim=yl, xlabel="게이트 전압 [V]", ylabel="log10 드레인 전류 [A]"); ax.grid(alpha=0.3)
    axs[0].set_title("점선: 논문 Fig. 5(c) (baseline, 그림 판독),  실선: TCAD (폭 0.1 um)", fontsize=10); axs[1].set_title("켜진 영역 확대", fontsize=10)
    from matplotlib.lines import Line2D
    h, l = axs[0].get_legend_handles_labels()
    axs[0].legend(h + [Line2D([], [], color="k", ls="--", lw=1.6), Line2D([], [], color="k", lw=1.2)], l + ["논문 (baseline)", "TCAD"], fontsize=8, loc="lower right")
    f2 = lambda x: "-" if x is None else f"{x:.2f}"
    rows = []
    for c, pts in curves:
        p = PAPER[c]; k = min(range(len(pts)), key=lambda j: pts[j][1])
        rows.append([f"Case {c}"] + [f"{f2(p[a])} / {f2(t)}" for a, t in (("v10", cross(pts, 1e-10)), ("v8", cross(pts, 1e-8)), ("v6", cross(pts, 1e-6)),
                                                                        ("lmin", math.log10(pts[k][1])), ("lm1", at(pts, -1.0)), ("l1", at(pts, 1.0)))])
    ta = fig.add_subplot(gs[1, :]); ta.axis("off")
    t = ta.table(cellText=rows, colLabels=["논문 (baseline) / TCAD", "Vg @1e-10 A [V]", "Vg @1e-8 A [V]", "Vg @1e-6 A [V]", "최소 전류 log10 [A]", "Vg -1 V 전류 log10 [A]", "Vg +1 V 전류 log10 [A]"],
                 loc="center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1, 1.35)
    fig.tight_layout(); fig.savefig(png, dpi=150); print("wrote", png)


if __name__ == "__main__":
    args = sys.argv[1:]; png = None
    if "--png" in args: k = args.index("--png"); png = args[k + 1]; del args[k:k + 2]
    f2 = lambda x, n=2: "  -  " if x is None else f"{x:+.{n}f}"
    print(f"W = {W} um.  columns: Vg at 1e-10 / 1e-8 / 1e-6 A | SS (1e-10..1e-8) mV/dec | minimum Vg, log10 I | log10 I at Vg -1, +1, +1.8 V")
    curves = []
    for rd in args:
        name = os.path.basename(rd.rstrip("/")); m = re.search(r"_c(\d)", name); c = int(m.group(1)) if m else None
        try: pts = curve(rd)
        except Exception as e:
            print(f"{name:14s} no curve ({e})"); continue
        curves.append((c, pts))
        v10, v8, v6 = cross(pts, 1e-10), cross(pts, 1e-8), cross(pts, 1e-6)
        ss = (v8 - v10) / 2 * 1e3 if v10 is not None and v8 is not None else None
        k = min(range(len(pts)), key=lambda j: pts[j][1])
        print(f"{name:14s} {f2(v10)} {f2(v8)} {f2(v6)} | {f2(ss, 1)} | {pts[k][0]:+.2f} {math.log10(pts[k][1]):+.2f} | "
              f"{f2(at(pts, -1.0))} {f2(at(pts, 1.0))} {f2(at(pts, 1.79))}   Vg {pts[0][0]:+.2f}..{pts[-1][0]:+.2f} ({len(pts)} pts)")
        if c in PAPER:
            p = PAPER[c]
            print(f"  paper Case {c}  {f2(p['v10'])} {f2(p['v8'])} {f2(p['v6'])} | {f2((p['v8'] - p['v10']) / 2 * 1e3, 1)} | {p['vmin']:+.2f} {p['lmin']:+.2f} | {f2(p['lm1'])} {f2(p['l1'])}   -")
    if png: picture(curves, png)
