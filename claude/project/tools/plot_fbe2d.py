# plot_fbe2d.py <tag for the loss curves> <tag for the bars at the paper's potential> <out.png>
# Fig.8 of Cho et al. against the 2D device (run on the PC; needs runs/D<tag>F_c<n>/ *_sys.plt and *_dev.plt copied from the server).
# Left: storage node against time, five cases, with the paper's values at the end of the BL-low phases (Cases 1, 2: all eight
# read from Fig.8(b); Cases 3 - 5: first phase and 200 ns, Fig.8(c)). Right: body potential rise at t_A, paper's bars against
# the two configurations.
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gt_tran import load, at, edges, PAPER_FBE
import paper_targets as P
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
tag, tag0, out = sys.argv[1:4]; col = {1: "#d62728", 2: "#c2185b", 3: "#1f77b4", 4: "#ff8c00", 5: "#2ca02c"}
lab = {1: "Case 1 (30 nm, 1e18, 4.7)", 2: "Case 2 (20 nm)", 3: "Case 3 (10 nm)", 4: "Case 4 (10 nm, 1e16)", 5: "Case 5 (1e16, WF 5.0)"}

def run(t_, c):
    d = os.path.join(RUNS, f"D{t_}F_c{c}"); s = load(os.path.join(d, f"D{t_}F_c{c}_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn, bl, wl = s[k("nSN)")], s[k("nBL")], s[k("nWL)")]
    t0 = edges(t, wl, 0, 1.8, False)[0] + 4e-11; f = edges(t, bl, 0, 1.1, False); r = [x for x in edges(t, bl, 0, 1.1, True) if x > f[0]]
    kv = next(x for x in dv if "ElectrostaticPotential" in x); rise = (at(dv["time"], dv[kv], f[0] - 3e-10) - dv[kv][0]) * 1e3
    return dict(t=[(x - t0) * 1e9 for x in t], sn=sn, t0=t0, lo=[(x - t0) * 1e9 for x in r], rise=rise)

fig, ax = plt.subplots(1, 3, figsize=(17, 5.2), gridspec_kw=dict(width_ratios=[1.25, 1.25, 1]))
R = {c: run(tag, c) for c in range(1, 6)}
for a, cs, ylim in ((ax[0], (1, 2, 3), (0.98, 1.105)), (ax[1], (3, 4, 5), (1.08, 1.101))):
    for c in cs:
        r = R[c]; i = [j for j, x in enumerate(r["t"]) if x >= 0]
        a.plot([r["t"][j] for j in i], [r["sn"][j] for j in i], color=col[c], lw=1.6, label=f"2D 소자, {lab[c]}")
        pts = list(zip(r["lo"], PAPER_FBE[c][0])) if c in PAPER_FBE and PAPER_FBE[c][0] else [(r["lo"][0], P.FBE_FIRST[c])]
        pts.append((200.0, P.FBE_200[c]))
        a.plot([x for x, _ in pts], [1.1 - v * 1e-3 for _, v in pts], "o", mfc="none", color=col[c], ms=7, mew=1.6, label=f"논문 Fig. 8, Case {c} (판독)")
    a.set_xlim(0, 205); a.set_ylim(*ylim); a.set_xlabel("시간 [ns] (0 = 저장 노드 충전 직후)"); a.set_ylabel("저장 노드 전압 [V]"); a.grid(alpha=0.3); a.legend(fontsize=8, loc="lower left")
ax[0].set_title("Fig. 8(b): 몸체 두께 30 / 20 / 10 nm"); ax[1].set_title("Fig. 8(c) 확대: 도핑, 일함수")
w = 0.27; x = range(1, 6); R0 = {c: run(tag0, c) for c in x}
ax[2].bar([i - w for i in x], [P.FBE_RISE[c] for c in x], w, color="#555555", label="논문 Fig. 8(a)")
ax[2].bar([i for i in x], [R0[c]["rise"] for c in x], w, color="#9ecae1", label="2D 소자, 막대에 맞춘 정공 전하 (약 1050개)")
ax[2].bar([i + w for i in x], [R[c]["rise"] for c in x], w, color="#3182bd", label="2D 소자, 손실 곡선에 맞춘 전하 (1.25배)")
for i in x:
    for dx, v in ((-w, P.FBE_RISE[i]), (0, R0[i]["rise"]), (w, R[i]["rise"])): ax[2].text(i + dx, v + 6, f"{v:.0f}", ha="center", fontsize=7)
ax[2].set_xticks(list(x)); ax[2].set_xticklabels([f"Case {c}" for c in x]); ax[2].set_ylabel("몸체 중심 전위 상승 (과도 해석 시작 → t_A) [mV]"); ax[2].set_ylim(0, 700)
ax[2].set_title("Fig. 8(a): 몸체 전위 상승"); ax[2].legend(fontsize=8, loc="upper right"); ax[2].grid(axis="y", alpha=0.3)
fig.suptitle("Cho et al. (IRPS 2026) Fig. 8 대비 2D 소자 (최종 구성, 충돌 이온화 켬, 저장 노드 1.8 fF 기준)", fontsize=12)
fig.tight_layout(); fig.savefig(out, dpi=140); print("saved", out)
