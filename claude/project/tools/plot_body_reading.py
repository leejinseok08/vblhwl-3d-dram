# plot_body_reading.py [out.png] - the back-calculated reading of Fig.8(a) in one picture (rounds 13, 14).
# Left: loss of the first BL-low phase over the body potential rise, Cases 1 - 4, the same runs read in two ways: the body-centre
# point just before the first BL fall (dashed, the reading used until 2026-10-06) and the average over the body under the gate
# 0.25 ns after the fall (solid). The paper's pair (bar of Fig.8(a), first-phase loss) as a star: it lies on the solid lines.
# Right: storage-node loss over time of the configuration fin3 (charge sized to the bars with the new reading, runs Ds2F) against
# the points read from Fig.8(b), (c), log scale. Run on the PC: python tools/plot_body_reading.py
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or r"C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs"
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram\gt2d_body_reading_fin3.png"
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
COL = {1: "#d32f2f", 2: "#c2185b", 3: "#1976d2", 4: "#f57c00", 5: "#388e3c"}; INK = "#263238"
NAME = {1: "Case 1 (30 nm)", 2: "Case 2 (20 nm)", 3: "Case 3 (10 nm, 1e18)", 4: "Case 4 (10 nm, 1e16)", 5: "Case 5 (1e16, WF 5.0)"}
PTS = {1: [(26, 43), (31.5, 55), (52.5, 67), (73.5, 76), (94.5, 83), (200, 100)], 2: [(26, 23), (31.5, 29), (200, 50)], 3: [(24, 3.3), (31, 7.1), (197, 14.6)], 4: [(24, 1.4), (30, 3.5), (63, 5.2), (200, 7.0)]}

def run(rid):
    d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; T = dv["time"]
    kc = next(q for q in dv if "ElectrostaticPotential" in q); ka = next(q for q in dv if q.startswith("AveWindow((0.075") and "ElectrostaticPotential" in q)
    f = edges(t, s[k("nBL")], 0, 1.1, False); r = [x for x in edges(t, s[k("nBL")], 0, 1.1, True) if x > f[0]]; tA = f[0] - 3e-10
    pts = [((x - f[0] + 0.25e-9) * 1e9 + 21.0, (at(t, sn, tA) - y) * 1e3) for x, y in zip(t, sn) if x >= tA - 2e-8]
    return dict(old=(at(T, dv[kc], tA) - dv[kc][0]) * 1e3, new=(at(T, dv[ka], f[0] + 5e-10) - dv[ka][0]) * 1e3, first=(at(t, sn, tA) - at(t, sn, r[0] - 3e-10)) * 1e3,
                tau=[p[0] for p in pts], loss=[p[1] for p in pts])

fig, ax = plt.subplots(1, 2, figsize=(17.5, 6.6), gridspec_kw=dict(width_ratios=[1.1, 1]))
a = ax[0]
for c in range(1, 5):
    D = sorted((run(f"{tag}_c{c}") for tag in ("Ds1F", "Dp1F", "Dp2F", "Ds2F")), key=lambda o: o["first"])
    a.plot([o["old"] for o in D], [o["first"] for o in D], "--o", color=COL[c], lw=1.6, ms=5, mfc="white")
    a.plot([o["new"] for o in D], [o["first"] for o in D], "-o", color=COL[c], lw=2.4, ms=7, label=NAME[c])
    a.plot([P.FBE_RISE[c]], [P.FBE_FIRST[c]], "*", color=COL[c], ms=22, mec=INK, mew=1.0, zorder=5)
a.plot([], [], "-o", color="#757575", lw=2.4, ms=7, label="새 읽기: 게이트 아래 몸체의 평균 전위, BL 하강 0.25 ns 뒤")
a.plot([], [], "--o", color="#757575", lw=1.6, ms=5, mfc="white", label="옛 읽기: 몸체 중심 한 점, BL 하강 직전")
a.plot([], [], "*", color="#9e9e9e", ms=18, mec=INK, label="논문: (Fig. 8(a) 막대, Fig. 8(b), (c) 첫 구간 손실)")
a.set_yscale("log"); a.set_xlim(290, 700); a.set_ylim(1.5, 130); a.set_yticks([2, 5, 10, 20, 50, 100]); a.set_yticklabels(["2", "5", "10", "20", "50", "100"], fontsize=11); a.minorticks_off()
a.set_xlabel("몸체 전위 상승 [mV] (과도 해석 시작 대비)", fontsize=12.5); a.set_ylabel("첫 BL 저전위 구간(10.5 ns)의 저장 노드 손실 [mV]", fontsize=12.5)
a.grid(alpha=0.25, which="both"); a.legend(fontsize=9.6, loc="lower right")
a.set_title("몸체 전위를 '게이트 아래 평균'으로 읽으면 논문의 점이 곡선 위에 와요", fontsize=14, fontweight="bold", color=INK)
b = ax[1]
for c in range(1, 5):
    o = run(f"Ds2F_c{c}"); xs = [(x, y) for x, y in zip(o["tau"], o["loss"]) if x >= 21.3 and y > 0.2]
    b.plot([x for x, _ in xs], [y for _, y in xs], color=COL[c], lw=2.3, label=f"2D 모델 fin3, {NAME[c]}")
    b.plot([x for x, _ in PTS[c]], [y for _, y in PTS[c]], "*", color=COL[c], ms=17, mec=INK, mew=1.0, zorder=5)
b.plot([], [], "*", color="#9e9e9e", ms=16, mec=INK, label="논문 Fig. 8(b), (c) (그림 판독값)")
b.set_yscale("log"); b.set_xlim(15, 207); b.set_ylim(0.5, 400); b.set_yticks([1, 3, 10, 30, 100, 300]); b.set_yticklabels(["1", "3", "10", "30", "100", "300"], fontsize=11); b.minorticks_off()
b.set_xlabel("시간 [ns] (논문 축: 첫 BL 하강 21.0 ns, 주기 21 ns)", fontsize=12.5); b.set_ylabel("저장 노드 손실 [mV] (t_A 기준)", fontsize=12.5)
b.grid(alpha=0.25, which="both"); b.legend(fontsize=9.6, loc="lower right")
b.set_title("그 읽기로 전하를 막대에 맞추면 손실 곡선이 허용치(약 2배) 안이에요", fontsize=14, fontweight="bold", color=INK)
b.text(17, 250, "Case 5: 모델 0.13 mV (첫 구간), 1.6 mV (200 ns). 논문 0, 1 mV", fontsize=10.5, color=COL[5], va="top")
for s_ in ax:
    for sp in ("top", "right"): s_.spines[sp].set_visible(False)
fig.suptitle("역산 결과: Fig. 8(a)의 '몸체 전위'는 게이트 아래 몸체의 평균 전위로 읽어야 Fig. 8(b), (c)와 맞아요 (구성 fin3)", fontsize=15.5, fontweight="bold", color=INK)
fig.tight_layout(); fig.savefig(OUT, dpi=125, bbox_inches="tight", facecolor="white"); print(OUT)
