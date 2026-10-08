# -*- coding: utf-8 -*-
"""
plot_underlap.py — the cross-section of the cell with the stretch of body that no gate covers (under the BL-side spacer) marked, and under it
the electron quasi-Fermi potential along the channel during the write: where the BL-to-node voltage falls (round 37, NOTES (ca)).

  python tools/plot_underlap.py <dopmap.csv> <load-line run folder> <out.png> [--fig2 <Fig.2 image>] [--set Blc=bot Blx=200 ...]

<dopmap.csv> = tools/export_doping.sh <struct> 0.200 (net doping of the real mesh); the run folder holds LL_*.plt of a deck "load" with ProbeE.
With --fig2 the single-cell drawing of the paper's Fig.2 is put next to the section (then the picture is not for the repository).
"""
import sys, os, re, glob, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import sde_dryrun as D
import plot_gt as G
from gt_tran import load
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dopmap"); ap.add_argument("run"); ap.add_argument("out"); ap.add_argument("--fig2"); ap.add_argument("--set", nargs="*", default=[])
    a = ap.parse_args(); prm = dict(D.DEFAULTS)
    for kv in a.set:
        k, v = kv.split("=", 1); prm[k] = v if isinstance(D.DEFAULTS.get(k), str) else float(v) if re.search(r"[.eE]", v) else int(v)
    img, xmax, ymax, rec, ymin = G.raster(a.dopmap, prm)
    x0 = prm["Wbl"] / 2; x1 = x0 + prm["Lsp1"]; x2 = x1 + prm["Lg"]; x3 = x2 + prm["Lsp2"]            # pillar face, gate edges, source end [nm]
    y3 = prm["Dvox"] / 2 + prm["Tgm"] + prm["Tox"]; y4 = y3 + prm["Tbody"]                             # body, bottom and top [nm]
    s = load(glob.glob(os.path.join(a.run, "LL_*.plt"))[0]); vn = s["sn_v OuterVoltage"]; cur = [abs(v) * 0.1e6 for v in s["sn_v TotalCurrent"]]
    qf = {}
    for k in s:
        m = re.match(r"Pos\(([-\d.eE]+),([-\d.eE]+)\) eQuasiFermiPotential", k)
        if m and abs(float(m.group(2)) * 1e3 - (y3 + y4) / 2) < 0.6: qf[float(m.group(1)) * 1e3] = s[k]
    xs = sorted(qf)
    def at(col, v):          # value of a column at node voltage v
        for i in range(1, len(vn)):
            if (vn[i - 1] - v) * (vn[i] - v) <= 0 and vn[i] != vn[i - 1]: return col[i - 1] + (col[i] - col[i - 1]) * (v - vn[i - 1]) / (vn[i] - vn[i - 1])
    vbl = max(s["bl OuterVoltage"])
    n = 2 if a.fig2 else 1
    fig = plt.figure(figsize=(7.4 * n, 9.0)); gs = fig.add_gridspec(2, n, height_ratios=[1, 1.05], hspace=0.36, wspace=0.24)
    ax = fig.add_subplot(gs[0, n - 1]); bx = fig.add_subplot(gs[1, n - 1], sharex=ax)
    if a.fig2:
        l, t, r, b = G.INSET; pa = fig.add_subplot(gs[0, 0]); pa.imshow(plt.imread(a.fig2)[t:b, l:r], interpolation="nearest"); pa.set_xticks([]); pa.set_yticks([])
        pa.set_title("논문 Fig. 2의 단일 셀 그림: BL과 게이트 사이(노란 스페이서 아래)에도\n파란 몸체(Floating Body)가 이어져 있어요", fontsize=10)
        l, t, r, b = G.XSECC; pb = fig.add_subplot(gs[1, 0]); pb.imshow(plt.imread(a.fig2)[t:b, l:r], interpolation="nearest"); pb.set_xticks([]); pb.set_yticks([])
        pb.set_title("논문 Fig. 2의 어레이 단면 (BL 오른쪽 셀):\n빨강 = N+, 파랑 = p형 몸체, 노랑 = 스페이서", fontsize=10)
    # ---- the section of the cell layer
    ax.imshow(img, origin="lower", extent=(0, xmax, ymin, ymax), aspect="auto", interpolation="nearest")
    ax.set(xlim=(0, xmax), ylim=(0, ymax + 46), ylabel="높이 (논문의 Z) [nm]")
    ax.add_patch(Rectangle((x0, y3), prm["Lsp1"], prm["Tbody"], fill=False, ec="white", lw=2.6, ls="--", zorder=5))
    ax.annotate("게이트가 덮지 않는 몸체\n(p형 10¹⁸ cm⁻³, 길이 25 nm)", ((x0 + x1) / 2, y4), ((x0 + x1) / 2 + 30, ymax + 31), ha="center", va="center", fontsize=10.5, weight="bold",
                arrowprops=dict(arrowstyle="->", lw=1.6), bbox=dict(boxstyle="round", fc="white", ec="k"), zorder=6, annotation_clip=False)
    lab = dict(ha="center", va="center", fontsize=9, weight="bold")
    ax.text(x0 / 2, (y3 + y4) / 2, "BL 기둥\nN+ 10²⁰", color="white", **lab); ax.text((x1 + x2) / 2, (y3 + y4) / 2, "p형 몸체 (게이트 아래 100 nm)", color="white", **lab)
    ax.text((x1 + x2) / 2, y4 + prm["Tox"] + prm["Tgm"] / 2, "게이트 (WL)", **lab); ax.text((x1 + x2) / 2, y3 - prm["Tox"] - prm["Tgm"] / 2, "게이트 (WL)", **lab)
    ax.text((x0 + x1) / 2, y4 + prm["Tox"] + prm["Tgm"] / 2, "스페\n이서", fontsize=7.5, ha="center", va="center"); ax.text((x2 + x3) / 2, y4 + prm["Tox"] + prm["Tgm"] / 2, "스페\n이서", fontsize=7.5, ha="center", va="center")
    ax.text((x2 + x3) / 2, (y3 + y4) / 2, "N+\n소스", color="white", fontsize=7.5, ha="center", va="center", weight="bold")
    ax.annotate("저장 노드\n접촉", (x3, (y3 + y4) / 2), (x3 - 14, 8), fontsize=8, ha="center", arrowprops=dict(arrowstyle="->", lw=1))
    for xa, xb, t in ((0, x0, f"BL/2 {x0:g}"), (x0, x1, f"{prm['Lsp1']:g}"), (x1, x2, f"게이트 길이 {prm['Lg']:g} nm"), (x2, x3, f"{prm['Lsp2']:g}")):
        ax.annotate("", (xa, ymax + 2.5), (xb, ymax + 2.5), arrowprops=dict(arrowstyle="<->", lw=0.8), annotation_clip=False); ax.text((xa + xb) / 2, ymax + 4.5, t, ha="center", va="bottom", fontsize=8)
    ax.set_title(f"만든 구조의 단면 (Case 2, 몸체 {prm['Tbody']:g} nm; 색은 메시의 도핑: 빨강 N+, 파랑 p)\nBL 기둥은 아래로 {prm['Blx']:g} nm 더 이어지고 그 끝에 BL 접촉이 있어요", fontsize=10)
    ax.legend(handles=[Patch(fc=G.COL["n"], label="N+ Si"), Patch(fc=G.COL["p"], label="p Si (몸체)"), Patch(fc=G.COL["gd"], label=f"게이트 절연막 ({prm['Gdi']} 5 nm)"),
                       Patch(fc=G.COL["gate"], label="게이트"), Patch(fc=G.COL["sp"], label=f"스페이서 ({prm['Spm']})"), Patch(fc=G.COL["ox"], label="층간 절연 (SiO2)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=3, fontsize=7.5, frameon=False)
    plt.setp(ax.get_xticklabels(), visible=False)
    # ---- the electron quasi-Fermi potential along the channel at three node voltages of the write
    bx.axvspan(x0, x1, color="#ffd54f", alpha=0.55, zorder=0); bx.axvspan(x1, x2, color="#b3e5fc", alpha=0.35, zorder=0)
    for v, c in ((0.36, "#1b5e20"), (0.82, "#d81b60"), (1.095, "#283593")):
        prof = [at(qf[x], v) for x in xs]; ia = min(xs, key=lambda q: abs(q - (x0 - 3))); ib = min(xs, key=lambda q: abs(q - (x1 + 2)))
        drop = at(qf[ia], v) - at(qf[ib], v)
        bx.plot(xs, prof, "-o", ms=3, color=c, lw=1.6, label=f"노드 {v:g} V (전류 {at(cur, v):.0f} µA): 전체 {1e3 * (vbl - v):.0f} mV 중 {1e3 * drop:.0f} mV = {100 * drop / (vbl - v):.0f} %가 노란 구간에")
    bx.set(xlabel="채널 방향 위치 (논문의 Y) [nm]", ylabel="전자 quasi-Fermi 전위 [V]", ylim=(0.25, 1.25))
    bx.text((x0 + x1) / 2, 0.29, "게이트가\n없는 몸체", ha="center", fontsize=8.5, weight="bold"); bx.text((x1 + x2) / 2, 0.29, "게이트 아래 채널", ha="center", fontsize=8.5)
    bx.text(x0 / 2, 0.29, "BL 기둥", ha="center", fontsize=8.5); bx.text((x2 + x3) / 2, 0.29, "소스", ha="center", fontsize=8.5)
    bx.grid(alpha=0.3); bx.legend(fontsize=8, loc="center right", bbox_to_anchor=(1.0, 0.36))
    bx.set_title(f"쓰기 조건의 DC 계산 (게이트 1.8 V, BL {vbl:g} V): 전압이 어디서 떨어지나\n선의 기울기가 큰 곳이 전류를 막는 곳이에요", fontsize=10)
    fig.savefig(a.out, dpi=150, bbox_inches="tight"); plt.close(fig); print("wrote", a.out)


if __name__ == "__main__":
    main()
