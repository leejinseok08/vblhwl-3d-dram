# plot_gt3.py <struct>_top.csv <paper top-view crop.png> <out.png> : the 3D X-X' pair seen from above next to the top view of
# the paper's Fig.2 (PC, matplotlib). Left: the paper. Middle: body mid-height (N+ red, p body blue, oxide wall white).
# Right: main-gate level (points that exist there = oxide / spacer, grey; no points = word-line metal, green background).
# Input from tools/gt3_top.sh (lines level,z_nm,x_nm,doping). Axes: x = along the channel (paper Y), z = along the word line (paper X).
import sys, csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in ("Malgun Gothic", "NanumGothic"):
    if any(f in x.name for x in font_manager.fontManager.ttflist): plt.rcParams["font.family"] = f; break
plt.rcParams["axes.unicode_minus"] = False
src, paper, out = sys.argv[1:4]
rows = [(l, float(z), float(x), float(d)) for l, z, x, d in csv.reader(open(src))]
fig, ax = plt.subplots(1, 3, figsize=(15, 5.2), gridspec_kw=dict(width_ratios=[1.25, 1, 1]))
ax[0].imshow(plt.imread(paper)); ax[0].axis("off"); ax[0].set_title("논문 Fig. 2 평면도 (baseline)")
b = [r for r in rows if r[0] == "body"]
col = ["#d62728" if d > 1e19 else "#1f4fd8" if d < -1e15 else "#dddddd" for _, _, _, d in b]
ax[1].scatter([r[2] for r in b], [r[1] for r in b], c=col, s=5, marker="s")
ax[1].set_title("TCAD 3D, 몸체 높이 (빨강 N+, 파랑 p 몸체, 회색 산화막)")
g = [r for r in rows if r[0] == "gate"]
ax[2].set_facecolor("#9ad19a")
ax[2].scatter([r[2] for r in g], [r[1] for r in g], c="#666666", s=5, marker="s")
ax[2].set_title("TCAD 3D, 주 게이트 높이 (초록 = WL 금속, 회색 = 산화막·스페이서)")
zmax = max(r[1] for r in rows); unit = zmax <= 100          # unit cell: half a row and half the wall; X-X' pair: 200 nm
for a in ax[1:]:
    a.set_xlabel("채널 방향 x [nm] (논문의 Y)"); a.set_ylabel("WL 방향 z [nm] (논문의 X)"); a.set_xlim(0, 175); a.set_ylim(0, 100 if unit else 200)
    for z, t in (((25, "셀 행 (절반, 0~50 nm)"), (75, "격리벽 (절반, 50~100 nm)")) if unit else ((25, "victim 행 (절반)"), (100, "격리벽 100 nm"), (175, "aggressor 행 (절반)"))):
        a.text(172, z, t, ha="right", va="center", fontsize=8, bbox=dict(fc="white", ec="none", alpha=0.7, pad=1))
    for z in ((50,) if unit else (50, 150)): a.axhline(z, color="k", lw=0.5, ls=":")
fig.tight_layout(); fig.savefig(out, dpi=140); print("wrote", out)
