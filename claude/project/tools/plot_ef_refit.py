# plot_ef_refit.py [out.png] - rounds 21 - 26 in one picture: what the avalanche driving force ElectricField, the place of the BL contact
# and the avalanche model itself do to Fig.4(a), Fig.5(c) and Fig.8 of the paper (Cho et al., IRPS 2026). Six panels: write curve,
# Id-Vg of Case 2, loss and body holes of Case 2 in the FBE test, loss of Case 1, and the Fig.8 scores of four configurations.
# Run on the PC. Run files from GT_RUNS (default: the shared repository's claude/data/runs). The paper's values are the numbers of
# tools/paper_targets.py and gt_fig5c.PAPER (read off the figures); a run that stops early is marked with a cross.
import sys, os, glob, math
os.environ.setdefault("GT_RUNS", r"C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs"); os.environ.setdefault("GT_W", "0.1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gt_tran import load, at, edges
import gt_fig5c as G, paper_targets as P, score2d as S
RUNS = os.environ["GT_RUNS"]
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram\gt2d_electricfield_end_contact_rounds21_26.png"
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
INK = "#263238"; PAP = "#c62828"
FIN, END, EF1, EF2, OFF, OFE = "#455a64", "#8d6e63", "#1565c0", "#6a1b9a", "#2e7d32", "#9e9d24"     # one colour per configuration, the same in every panel
sysf = lambda rid: load(os.path.join(RUNS, rid, rid + "_sys.plt"))
col = lambda s, n: s[next(k for k in s if n in k)]

def wr(rid):                                # write: ps after the WL edge, storage node [V]
    s = sysf(rid); t = s["time"]; e = edges(t, col(s, "nWL)"), 0, 1.8, True)[0]
    return [(x - e) * 1e12 for x in t], col(s, "nSN)")

def fb(rid):                                # FBE: ns after the first BL fall | loss since t_A [mV] ; ns | holes in the body
    s = sysf(rid); dv = load(glob.glob(os.path.join(RUNS, rid, "*_dev.plt"))[0]); t = s["time"]; sn = col(s, "nSN)"); T = dv["time"]
    f = edges(t, col(s, "nBL"), 0, 1.1, False)[0]; v0 = at(t, sn, f - 3e-10); hd = dv[next(k for k in dv if "hDensity" in k)]
    a = [(x, (v0 - v) * 1e3) for x, v in zip(t, sn) if x >= f - 3e-10]; b = [(x, h * 1e-13) for x, h in zip(T, hd) if x >= f - 3e-10]
    return [(x - f) * 1e9 for x, _ in a], [y for _, y in a], [(x - f) * 1e9 for x, _ in b], [y for _, y in b]

def line(ax, x, y, c, lab, ls="-", end=179.0, lw=2.0):
    ax.plot(x, y, color=c, lw=lw, ls=ls, label=lab)
    if x[-1] < end - 1: ax.plot(x[-1], y[-1], "x", color=c, ms=10, mew=2.5)       # stopped early

fig, ax = plt.subplots(2, 3, figsize=(22, 12.5)); (a, b, c), (d, e, g) = ax
# (a) write curve, Fig.4(a)
for rid, cl, lab, ls in (("DfinW_c2", FIN, "기본 구동력, 1.8 fF (지금의 소자 fin3)", "-"), ("Db0W_c2", FIN, "기본 구동력, 4.2 fF (본문의 용량)", ":"),
                         ("Dd2W_c2", EF1, "ElectricField, 4.2 fF (본문의 용량)", ":"), ("Dd7W_c2", EF1, "ElectricField, 5.67 fF (맞춘 값)", "-")):
    x, y = wr(rid); k = [i for i, v in enumerate(x) if -5 <= v <= 75]; a.plot([x[i] for i in k], [y[i] for i in k], color=cl, lw=2.0, ls=ls, label=lab)
a.errorbar(list(P.WRITE), list(P.WRITE.values()), yerr=P.WRITE_TOL, fmt="D", color=PAP, ms=9, mec=INK, capsize=4, zorder=6, label="논문 Fig. 4(a) (허용 ±30 mV)")
a.set(xlim=(-5, 75), ylim=(0, 1.25), xlabel="WL이 올라간 뒤의 시간 [ps]", ylabel="저장 노드 전압 [V]"); a.legend(fontsize=9.5, loc="lower right")
a.set_title("① 쓰기 곡선 (Case 2)", fontsize=13.5, fontweight="bold", color=INK)
# (b) Id-Vg of Case 2, Fig.5(c)
for rid, cl, lab, ls, lw in (("Dd0I_c2", FIN, "충돌 이온화 끔, DC", "-", 3.2), ("DdgI_c2", "#ffb300", "충돌 이온화 끔, 100 µs 스윕 (대조)", "--", 1.6),
                             ("Dd6I_c2", EF1, "ElectricField, 100 µs 스윕", "-", 2.0), ("DdiI_c2", EF2, "ElectricField, 10 ms 스윕", "-", 2.0)):
    p = [q for q in G.curve(os.path.join(RUNS, rid)) if q[1] > 0 and q[0] >= 0]; b.plot([v for v, i in p], [i for v, i in p], color=cl, lw=lw, ls=ls, label=lab)
pp = G.PAPER[2]; b.errorbar([pp["v10"], pp["v8"], pp["v6"]], [1e-10, 1e-8, 1e-6], xerr=P.IV_TOL["v10"], fmt="D", color=PAP, ms=9, mec=INK, capsize=4, zorder=6, label="논문 Fig. 5(c) (허용 ±0.02 V)")
b.set_yscale("log"); b.set(xlim=(0, 1.0), ylim=(1e-13, 1e-3), xlabel="게이트 전압 [V]  (BL 1.1 V)", ylabel="드레인 전류 [A]  (폭 0.1 µm)"); b.legend(fontsize=9.5, loc="lower right")
b.set_title("② Id–Vg (Case 2)", fontsize=13.5, fontweight="bold", color=INK)
# (c), (d) FBE of Case 2: loss and holes; (e) loss of Case 1
SETS = (("Ds2F", FIN, "기본 구동력, 접촉은 기둥 축 (fin3)", "-"), ("DdcF", END, "기본 구동력, 접촉은 기둥 끝", "-"), ("DdlF", OFF, "avalanche 끔, 접촉은 기둥 축", "-"),
        ("DdmF", OFE, "avalanche 끔, 접촉은 기둥 끝", "-"), ("DdeF", EF1, "ElectricField, 접촉은 기둥 끝, 용량 × 1.35", "-"), ("DddF", EF2, "ElectricField, 접촉은 기둥 끝, 용량 그대로", "-"))
for cs, p1, p2 in ((2, c, d), (1, e, None)):
    for tag, cl, lab, ls in SETS:
        try: x, y, xh, yh = fb(f"{tag}_c{cs}")
        except Exception as ex: print("skipped", tag, cs, ex); continue
        line(p1, x, [max(v, 1e-2) for v in y], cl, lab, ls)
        if p2: line(p2, xh, yh, cl, lab, ls)
    for i in range(9): p1.axvspan(21.0 * i, 21.0 * i + 10.5, color="#eceff1", zorder=0)
    pts = [(10.2, P.FBE_FIRST[cs]), (179.0, P.FBE_200[cs])] + ([(5.0, 23.0)] if cs == 2 else [(5.0, 43.0), (31.2, 67.0), (52.2, 76.0), (73.2, 83.0)])
    p1.errorbar([q[0] for q in pts], [q[1] for q in pts], yerr=[[q[1] * (1 - 10 ** -P.DEC_TOL) for q in pts], [q[1] * (10 ** P.DEC_TOL - 1) for q in pts]], fmt="D", color=PAP, ms=9, mec=INK,
                capsize=4, zorder=6, label="논문 Fig. 8(b), (c) (허용 ±0.3 decade)")
    p1.set_yscale("log"); p1.set(xlim=(-2, 185), ylim=(1, 600), xlabel="첫 BL 하강부터의 시간 [ns]  (회색 띠: BL이 0 V)", ylabel="저장 노드 손실 [mV] (로그)"); p1.legend(fontsize=9, loc="lower right")
    p1.set_yticks([1, 10, 100]); p1.set_yticklabels(["1", "10", "100"])
c.set_title("③ FBE 시험, Case 2: 저장 노드 손실", fontsize=13.5, fontweight="bold", color=INK); e.set_title("⑤ FBE 시험, Case 1: 저장 노드 손실", fontsize=13.5, fontweight="bold", color=INK)
for i in range(9): d.axvspan(21.0 * i, 21.0 * i + 10.5, color="#eceff1", zorder=0)
d.set(xlim=(-2, 185), xlabel="첫 BL 하강부터의 시간 [ns]  (회색 띠: BL이 0 V)", ylabel="몸체 안의 정공 수 [개]  (폭 0.1 µm)"); d.legend(fontsize=9, loc="lower left")
d.set_title("④ FBE 시험, Case 2: 몸체의 정공", fontsize=13.5, fontweight="bold", color=INK)
# (f) Fig.8 scores of four configurations
CF = (("fin3", "fin3\n기본 구동력\n접촉: 기둥 축", FIN), ("fin3b", "기본 구동력\n접촉: 기둥 끝", END), ("fin3n", "avalanche 끔\n접촉: 기둥 축", OFF), ("fin3bn", "avalanche 끔\n접촉: 기둥 끝", OFE))
for i, (tag, lab, cl) in enumerate(CF):
    v, txt = S.fbe(tag); print(tag, [round(x, 2) for x in v], txt)
    for j, (x, al) in enumerate(zip(v, (0.45, 0.72, 1.0))):
        g.bar(i + (j - 1) * 0.26, x, 0.24, color=cl, alpha=al, ec=INK, lw=0.8); g.text(i + (j - 1) * 0.26, x + 0.02, f"{x:.2f}", ha="center", va="bottom", fontsize=9.5, color=INK)
g.axhline(1.0, color=PAP, lw=1.4, ls="--"); g.text(3.45, 1.02, "허용 한계 (1.0)", color=PAP, fontsize=9.5, ha="right", va="bottom")
g.set_xticks(range(len(CF))); g.set_xticklabels([q[1] for q in CF], fontsize=10); g.set_ylabel("점수 = (모델 − 논문) / 허용 오차의 rms", fontsize=11); g.set_ylim(0, 1.25)
g.text(0.02, 0.97, "막대 셋: 몸체 전위 막대 (Fig. 8(a)) · 첫 구간 손실 · 200 ns 손실\nElectricField는 Case 1이 무너져서 점수를 낼 수 없어요", transform=g.transAxes, fontsize=9.8, va="top", color=INK)
g.set_title("⑥ Fig. 8 점수 (작을수록 좋음)", fontsize=13.5, fontweight="bold", color=INK)
for q in (a, b, c, d, e, g):
    q.grid(alpha=0.25)
    for sp in ("top", "right"): q.spines[sp].set_visible(False)
    q.xaxis.label.set_size(11); q.yaxis.label.set_size(11)
fig.suptitle("라운드 21~26: avalanche 구동력 ElectricField와 BL 접촉 위치를 소자 전체에 넣으면 Fig. 4(a)·5(c)·8이 나오는가 (2D)", fontsize=16, fontweight="bold", color=INK)
fig.tight_layout(); fig.savefig(OUT, dpi=110, bbox_inches="tight", facecolor="white"); print(OUT)
