# plot_hurkx_scan.py [out.png] - rounds 30, 31: back-calculation of the Hurkx coefficients (A, B) of the band-to-band tunnelling model.
# Left: GIDL branch of the silicon reference transistor of Hsu .. Yu (IMW 2025 / TED 2026, Fig.2(c); points read off the figure) with
# the model at four values of B. Middle: model minus paper along that branch (A corrected by Cho's points at Vg = -1 V, as
# tools/gt_hurkx_scan.py does). Right: the loss of Case 5 at 200 ns against B, with what the paper's figure allows.
# Run on the PC; run files from GT_RUNS (default: the shared repository's claude/data/runs).
import sys, os, re, json, math
os.environ.setdefault("GT_RUNS", r"C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import gt_hsu_fig2c as H                 # sets GT_W = 1 (A/um)
from gt_fbe_leak import leak
G = H.G; RUNS = os.environ["GT_RUNS"]
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram\gt2d_hurkx_ab_rounds30_31.png"
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
INK = "#263238"; PAP = "#c62828"
SETS = (("Dd0I", "DhuI_c3", "DdmF_c5", "#8d6e63"), ("DdvI", "DhvI_c3", "DdvF_c5", "#ef6c00"), ("DdwI", "DhwI_c3", "DdwF_c5", "#1565c0"), ("DdxI", "DhxI_c3", "DdxF_c5", "#6a1b9a"))
BR = (-0.7, -0.8, -0.9, -1.0, -1.25, -1.5, -1.75)
def ab(rid):
    m = re.search(r"_a([0-9.e+-]+)_b([0-9.e+-]+?)(?:_|\.par)", json.load(open(os.path.join(RUNS, rid, "run.json"), encoding="utf-8"))["params"]["Par"])
    return float(m.group(1)), float(m.group(2))
fig, ax = plt.subplots(1, 3, figsize=(22, 7.6)); a, b, c = ax
bs, ls = [], []
for iv, hs, fb, col in SETS:
    A, B = ab(hs); lab = f"B = {B / 1e7:.2f}×10⁷ V/cm, A = {A:.2g}"
    p = [q for q in G.curve(os.path.join(RUNS, hs)) if q[1] > 0 and -1.95 <= q[0] <= -0.45]
    a.plot([v for v, i in p], [i for v, i in p], color=col, lw=2.0, label=lab)
    r1 = [G.at(G.curve(os.path.join(RUNS, f"{iv}_c{k}")), -1.0) - 1.0 - G.PAPER[k]["lm1"] for k in range(1, 6)]; d = sum(r1) / 5       # how far A is off by Cho's five points
    pts = G.curve(os.path.join(RUNS, hs)); rr = [G.at(pts, v) - H.HSU[v] - d for v in BR]
    b.plot(BR, rr, "-o", color=col, lw=2.0, ms=6, label=lab + f": 기울기 차이 {rr[-1] - rr[0]:+.2f}")
    o = leak(fb); bs.append(B / 1e7); ls.append(o["L"]); c.plot([B / 1e7], [o["L"]], "o", color=col, ms=13, mec=INK, zorder=5)
    print(hs, A, B, [round(x, 2) for x in rr], round(o["L"], 3))
a.plot(BR, [10.0 ** H.HSU[v] for v in BR], "D", color=PAP, ms=9, mec=INK, zorder=6, label="논문의 실리콘 비교 트랜지스터 (Hsu 외 Fig. 2(c), 그림에서 읽음)")
a.set_yscale("log"); a.set(xlim=(-1.9, -0.5), ylim=(1e-17, 3e-12)); k = range(-17, -11); a.set_yticks([10.0 ** q for q in k]); a.set_yticklabels([f"1e{q}" for q in k]); a.minorticks_off()
a.set_xlabel("게이트 전압 [V]  (V_DS = 1 V, 일함수 4.27 eV)", fontsize=12); a.set_ylabel("드레인 전류 [A/µm]", fontsize=12); a.legend(fontsize=9.5, loc="lower left")
a.set_title("① GIDL 가지: 논문의 실리콘 곡선과 모델", fontsize=13.5, fontweight="bold", color=INK)
b.axhline(0, color=INK, lw=0.8); b.axhspan(-0.1, 0.1, color="#eceff1", zorder=0); b.text(-1.83, -0.095, "회색 띠: 그림을 읽는 오차 ±0.1 decade", fontsize=9.5, color=INK, va="bottom")
b.set(xlim=(-1.85, -0.6), ylim=(-0.45, 0.45)); b.set_xlabel("게이트 전압 [V]", fontsize=12); b.set_ylabel("모델 − 논문 [decade]  (A는 Cho Fig. 5(c)의 −1 V 값에 맞춘 뒤)", fontsize=11.5); b.legend(fontsize=9.5, loc="upper center")
b.set_title("② 그 가지에서의 차이: B = 2.0×10⁷에서 기울기가 같아짐", fontsize=13.5, fontweight="bold", color=INK)
c.plot(bs, ls, "-", color="#90a4ae", lw=1.5, zorder=3)
c.axhspan(0, 0.5, color="#ffcdd2", zorder=0); c.text(1.905, 0.25, "논문 Fig. 8(c): Case 5의 선이 1.1 V 높이에 있음\n(0.5 mV 이하. 파란 선을 ⑤로 읽은 판독)", fontsize=10, color=PAP, va="center")
c.set(xlim=(1.85, 2.3), ylim=(0, 2.0)); c.set_xlabel("Hurkx 계수 B [10⁷ V/cm]  (A는 47배 범위에서 함께 바꿈)", fontsize=12); c.set_ylabel("Case 5의 200 ns 손실 [mV]", fontsize=12)
c.text(2.075, 1.68, "A, B를 바꿔도 그대로예요 (1.57~1.58 mV)", fontsize=11, color=INK, ha="center")
c.set_title("③ Case 5의 손실은 A, B에 반응하지 않음", fontsize=13.5, fontweight="bold", color=INK)
for q in ax:
    q.grid(alpha=0.25)
    for sp in ("top", "right"): q.spines[sp].set_visible(False)
fig.suptitle("라운드 30: Hurkx 계수 B의 역산 (GIDL 가지의 기울기로는 정해지고, Case 5의 손실로는 정해지지 않음)", fontsize=15.5, fontweight="bold", color=INK)
fig.tight_layout(); fig.savefig(OUT, dpi=110, bbox_inches="tight", facecolor="white"); print(OUT)
