# plot_held.py [out.png] - round 12 in one picture: the body charged by the model's own generation with the storage node held at
# 1.1 V (hold 15.2 / 18 / 20 / 22 us), then the BL waveform of Fig.8(b). Over the hold: body rise at t_A (left), loss of the first
# BL-low phase (middle), loss at 200 ns (right); the paper's values dashed, the one hold that fits the first-phase losses best
# as a vertical line. Data: runs Dn1F .. Dn4F_c1..5. Run on the PC: python tools/plot_held.py
import sys, os, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or r"C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs"
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram\gt2d_held_node_round12.png"
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
COL = {1: "#d32f2f", 2: "#c2185b", 3: "#1976d2", 4: "#f57c00", 5: "#388e3c"}; INK = "#263238"
NAME = {1: "Case 1 (30 nm)", 2: "Case 2 (20 nm)", 3: "Case 3 (10 nm, 1e18)", 4: "Case 4 (10 nm, 1e16)", 5: "Case 5 (1e16, WF 5.0)"}
HOLD = (("Dn1F", 15.2), ("Dn2F", 18.0), ("Dn3F", 20.0), ("Dn4F", 22.0))

def run(rid):
    d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; T = dv["time"]
    q = next(x for x in dv if "ElectrostaticPotential" in x)                     # the first probe of the deck = body centre
    f = edges(t, s[k("nBL")], 0, 1.1, False); r = [x for x in edges(t, s[k("nBL")], 0, 1.1, True) if x > f[0]]; tA = f[0] - 3e-10
    return dict(rise=(at(T, dv[q], tA) - dv[q][0]) * 1e3, first=(at(t, sn, tA) - at(t, sn, r[0] - 3e-10)) * 1e3, l200=(at(t, sn, tA) - at(t, sn, f[0] + 179e-9)) * 1e3)

D = {c: [run(f"{tag}_c{c}") for tag, _ in HOLD] for c in range(1, 6)}; H = [h for _, h in HOLD]
def interp(c, key, h):
    i = max(0, min(2, next((k for k in range(3) if h <= H[k + 1]), 2))); w = (h - H[i]) / (H[i + 1] - H[i])
    return math.exp(math.log(D[c][i][key]) * (1 - w) + math.log(D[c][i + 1][key]) * w)
grid = [15.2 + i * 0.05 for i in range(137)]
hb = min(grid, key=lambda h: max(abs(math.log10(interp(c, "first", h) / P.FBE_FIRST[c])) for c in range(1, 5)))
fig, ax = plt.subplots(1, 3, figsize=(19, 6.2))
for c in range(1, 6):
    ax[0].plot(H, [o["rise"] for o in D[c]], "-o", color=COL[c], lw=2.3, ms=7, label=f"2D 모델, {NAME[c]}"); ax[0].axhline(P.FBE_RISE[c], color=COL[c], ls="--", lw=1.2)
    ax[1].plot(H, [o["first"] for o in D[c]], "-o", color=COL[c], lw=2.3, ms=7, label=f"2D 모델, {NAME[c]}")
    ax[2].plot(H, [o["l200"] for o in D[c]], "-o", color=COL[c], lw=2.3, ms=7, label=f"2D 모델, {NAME[c]}")
    if P.FBE_FIRST[c] > 0: ax[1].axhline(P.FBE_FIRST[c], color=COL[c], ls="--", lw=1.2)
    ax[2].axhline(P.FBE_200[c], color=COL[c], ls="--", lw=1.2)
for a in ax:
    a.axvline(hb, color=INK, ls=":", lw=1.8); a.set_xlim(14.6, 22.6); a.set_xticks(H); a.set_xticklabels(["15.2", "18", "20", "22"], fontsize=11)
    a.set_xlabel("첫 BL 하강 전 유지 시간 [µs] (저장 노드는 1.1 V로 고정)", fontsize=12); a.grid(alpha=0.25, which="both")
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
ax[0].set_ylabel("t_A의 몸체 중심 전위 상승 [mV]", fontsize=12.5); ax[0].set_ylim(280, 720)
ax[0].set_title("막대는 이미 넘어섰어요 (19.1 µs에서 +42 ~ +141 mV)", fontsize=14, fontweight="bold", color=INK); ax[0].legend(fontsize=9.3, loc="upper left", ncol=2)
ax[0].text(hb + 0.08, 288, f"공통 유지 {hb:.1f} µs", fontsize=10.5, color=INK); ax[0].text(14.7, 695, "", fontsize=10)
ax[1].set_yscale("log"); ax[1].set_ylim(0.08, 200); ax[1].set_yticks([0.1, 1, 10, 100]); ax[1].set_yticklabels(["0.1", "1", "10", "100"], fontsize=11); ax[1].minorticks_off()
ax[1].set_ylabel("첫 BL 저전위 구간(10.5 ns)의 손실 [mV]", fontsize=12.5)
ax[1].set_title("첫 구간 손실은 한 유지 시간에서 허용 안이에요 (0.28 decade)", fontsize=14, fontweight="bold", color=INK)
ax[1].text(14.7, 185, "점선(가로) = 논문 55 / 29 / 7.1 / 3.5 mV, Case 5는 0\n허용 = 0.3 decade (약 2배)", fontsize=10.5, color=INK, va="top")
ax[2].set_yscale("log"); ax[2].set_ylim(0.8, 300); ax[2].set_yticks([1, 10, 100]); ax[2].set_yticklabels(["1", "10", "100"], fontsize=11); ax[2].minorticks_off()
ax[2].set_ylabel("200 ns의 손실 [mV]", fontsize=12.5)
ax[2].set_title("200 ns 손실은 두꺼운 몸체에서 커요 (Case 2: 2.2배)", fontsize=14, fontweight="bold", color=INK)
ax[2].text(14.7, 180, "점선(가로) = 논문 100 / 50 / 14.6 / 약 7 / 1 mV", fontsize=10.5, color=INK, va="top")
fig.suptitle("라운드 12: 모델의 자체 생성으로 충전(저장 노드 1.1 V 고정)한 뒤 논문 BL 파형 전체. 점선(가로) = 논문, 세로 점선 = 첫 구간 손실이 가장 잘 맞는 공통 유지 시간",
             fontsize=14.5, fontweight="bold", color=INK)
fig.tight_layout(); fig.savefig(OUT, dpi=125, bbox_inches="tight", facecolor="white"); print(OUT, f"common hold {hb:.1f} us")
