# -*- coding: utf-8 -*-
"""
plot_gt.py — the built Cho cell next to the drawings of Cho et al. (IRPS 2026) Fig.2, in the colours of that figure.

  python tools/plot_gt.py <dopmap.csv> <out.png> --fig2 <Fig.2 image> --set Lg=100 Tbody=20 Tox=5.0 Nsd=1e20 Gdi=HfO2

<dopmap.csv> = tools/export_doping.sh <struct> 0.200 on the server (x_um, y_um, net doping of the real mesh): silicon is
coloured by its sign there, red n / blue p as in the figure. Materials and contacts come from sde_gt_dvs.cmd through the
dry-run interpreter (same script as the mesh). --fig2 = the embedded Fig.2 image of the paper (2017 x 1173 px).
"""
import sys, os, re, csv, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import sde_dryrun as D
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
plt.rcParams["font.family"] = ["DejaVu Sans", "Malgun Gothic"]

# colours of the paper's drawing (sampled there): isolation oxide, spacer, gate dielectric line, gate metal, n and p silicon
COL = {"ox": (0.0, 0.86, 1.0), "sp": (0.86, 0.86, 0.47), "gd": (0.80, 0.09, 0.22), "gate": (0.0, 0.69, 0.94), "n": (1.0, 0.0, 0.0), "p": (0.0, 0.0, 0.80)}
INSET = (1285, 668, 1890, 950)      # single-cell view in the Fig.2 image (left, top, right, bottom)
XSEC = (419, 728, 549, 806)         # one cell right of the bit line, top layer, in the array cross-section
PAIRX = (349, 726, 546, 850)        # both cells at the bit line, top two layers (for the yy and zz sections)


def raster(dop_csv, params, res=0.25):
    """RGB image (y up) of the built cell and its size in nm."""
    rec, _ = D.run(os.path.join(HERE, "..", "sde_gt_dvs.cmd"), params)
    xmax = max(b["x2"] for b in rec.boxes) * 1e3; ymax = max(b["y2"] for b in rec.boxes) * 1e3
    cols = {}
    for x, y, n in csv.reader(open(dop_csv)):
        if float(n): cols.setdefault(float(x) * 1e3, []).append((float(y) * 1e3, float(n)))
    xs = sorted(cols)
    nx, ny = int(round(xmax / res)), int(round(ymax / res))
    img = [[(1, 1, 1)] * nx for _ in range(ny)]; key = [[None] * nx for _ in range(ny)]
    for i in range(nx):
        x = (i + 0.5) * res; col = cols[min(xs, key=lambda v: abs(v - x))]
        for j in range(ny):
            y = (j + 0.5) * res
            b = next((b for b in reversed(rec.boxes) if b["x1"] * 1e3 <= x <= b["x2"] * 1e3 and b["y1"] * 1e3 <= y <= b["y2"] * 1e3), None)
            if b is None: continue
            if b["mat"] == "Silicon":
                n = min(col, key=lambda c: abs(c[0] - y))[1]; k = "n" if n > 0 else "p"
            else:
                k = "gd" if b["name"].startswith("R.Gox") else "gate" if b["deleted"] else "sp" if b["name"].startswith("R.Sp") else "ox"
            key[j][i] = k if b["mat"] == "Silicon" else b["name"]; img[j][i] = COL[k]
    for j in range(ny):                                   # outlines between regions
        for i in range(nx):
            if (i + 1 < nx and key[j][i] != key[j][i + 1]) or (j + 1 < ny and key[j][i] != key[j + 1][i]): img[j][i] = (0.1, 0.1, 0.1)
    return img, xmax, ymax, rec


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dopmap"); ap.add_argument("out"); ap.add_argument("--fig2"); ap.add_argument("--set", nargs="*", default=[])
    a = ap.parse_args(); prm = dict(D.DEFAULTS)
    for kv in a.set:
        k, v = kv.split("=", 1)
        prm[k] = v if isinstance(D.DEFAULTS.get(k), str) else float(v) if re.search(r"[.eE]", v) else int(v)
    img, xmax, ymax, rec = raster(a.dopmap, prm)
    pair = prm["Pair"] != "one"; n = (2 if pair else 3) if a.fig2 else 1
    fig, axs = plt.subplots(1, n, figsize=(6.2 * n, 4.8), gridspec_kw=dict(width_ratios=[1, 1.35] if pair and a.fig2 else [1.25, 1, 1.35][3 - n:]))
    axs = [axs] if n == 1 else list(axs)
    if a.fig2:
        f2 = plt.imread(a.fig2)
        for ax, (l, t, r, b), ttl in (((axs[0], PAIRX, "논문 Fig. 2: 어레이 단면 (BL 양쪽 셀, 위 두 층)"),) if pair else
                                      ((axs[0], INSET, "논문 Fig. 2: 단일 셀 그림"), (axs[1], XSEC, "논문 Fig. 2: 어레이 단면 (BL 오른쪽 셀, 맨 위층)"))):
            ax.imshow(f2[t:b, l:r], interpolation="nearest"); ax.set_title(ttl, fontsize=10); ax.set_xticks([]); ax.set_yticks([])
    ax = axs[-1]
    ax.imshow(img, origin="lower", extent=(0, xmax, 0, ymax), aspect="equal", interpolation="nearest")
    x1 = prm["Wbl"] / 2; x2 = x1 + prm["Lsp1"]; x3 = x2 + prm["Lg"]
    for xa, xb, lab in () if pair else ((0, x1, f"BL/2\n{x1:g}"), (x1, x2, f"{prm['Lsp1']:g}"), (x2, x3, f"Lg {prm['Lg']:g}"), (x3, xmax, f"{prm['Lsp2']:g}")):
        ax.annotate("", (xa, ymax + 4), (xb, ymax + 4), arrowprops=dict(arrowstyle="<->", lw=0.8), annotation_clip=False)
        ax.text((xa + xb) / 2, ymax + 6, lab, ha="center", va="bottom", fontsize=8)
    for name, lst in rec.contacts.items():
        for c in lst:
            if c[0] == "edge": ax.text(c[1][0] * 1e3 + (4 if c[1][0] == 0 else -4), c[1][1] * 1e3, name, color="white", fontsize=9, weight="bold", ha="left" if c[1][0] == 0 else "right", va="center")
            else: ax.text((c[2]["x1"] + c[2]["x2"]) * 500, (c[2]["y1"] + c[2]["y2"]) * 500, name, color="k", fontsize=9, weight="bold", ha="center", va="center")
    ax.set(xlabel="x = 논문의 Y [nm]", ylabel="y = 논문의 Z [nm]", xlim=(0, xmax), ylim=(0, ymax + 22))
    ax.set_title(f"만든 구조 ({prm['Pair']}; 메시의 도핑, 몸체 {prm['Tbody']:g} nm, {prm['Nch']:.0e} cm⁻³)", fontsize=10)
    ax.legend(handles=[Patch(fc=COL["n"], label="N+ Si (BL, 소스)"), Patch(fc=COL["p"], label="p Si (몸체)"), Patch(fc=COL["gd"], label=f"게이트 절연막 ({prm['Gdi']})"),
                       Patch(fc=COL["gate"], label="게이트"), Patch(fc=COL["sp"], label=f"스페이서 ({prm['Spm']})"), Patch(fc=COL["ox"], label="층간 절연 (SiO2)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, fontsize=8, frameon=False)
    fig.tight_layout(); fig.savefig(a.out, dpi=150, bbox_inches="tight"); plt.close(fig); print("wrote", a.out)


if __name__ == "__main__":
    main()
