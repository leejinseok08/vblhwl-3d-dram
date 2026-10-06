# plot_3d_fbe.py [out.png] - the FBE of Case 2 in the 3D unit cell next to the 2D section, at the same two charged states
# (hole charge of the bar of Fig.8(a) and 1.25 times it, set by the stand-in supply with the storage node held), against the
# points read from Fig.8(b). Left: storage-node loss over time. Right: loss of the first BL-low phase over the body rise at t_A
# (2D line through the four stand-in states, the two 3D runs as diamonds, the paper's pair as a star).
# Data: runs E3F_c2, E3F125_c2 (3D), Dh1F_c2 .. Dh4F_c2 (2D). Run on the PC: python tools/plot_3d_fbe.py
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or r"C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs"
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram\gt3_fbe_case2_vs_2d.png"
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
INK = "#263238"; C3 = "#6a1b9a"; C2 = "#c2185b"

def run(rid):
    d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; T = dv["time"]; q = next(x for x in dv if "ElectrostaticPotential" in x)
    f = edges(t, s[k("nBL")], 0, 1.1, False); r = [x for x in edges(t, s[k("nBL")], 0, 1.1, True) if x > f[0]]; tA = f[0] - 3e-10
    pts = [((x - f[0] + 0.25e-9) * 1e9 + 21.0, (at(t, sn, tA) - y) * 1e3) for x, y in zip(t, sn) if x >= tA - 2e-8]
    return dict(rise=(at(T, dv[q], tA) - dv[q][0]) * 1e3, first=(at(t, sn, tA) - at(t, sn, r[0] - 3e-10)) * 1e3, l200=(at(t, sn, tA) - at(t, sn, f[0] + 179e-9)) * 1e3,
                tau=[p[0] for p in pts], loss=[p[1] for p in pts])

a3, b3 = run("E3F_c2"), run("E3F125_c2"); D2 = [run(f"Dh{i}F_c2") for i in (1, 2, 3, 4)]
fig, ax = plt.subplots(1, 2, figsize=(17, 6.3), gridspec_kw=dict(width_ratios=[1.2, 1]))
a = ax[0]
a.plot(D2[0]["tau"], D2[0]["loss"], color=C2, lw=1.8, ls="--", label=f"2D 단면, 막대 전하 (몸체 +{D2[0]['rise']:.0f} mV)")
a.plot(a3["tau"], a3["loss"], color=C3, lw=2.4, label=f"3D 단위 셀, 막대 전하 (몸체 +{a3['rise']:.0f} mV)")
a.plot(D2[1]["tau"], D2[1]["loss"], color="#f06292", lw=1.8, ls="--", label=f"2D 단면, 전하 1.25배 (몸체 +{D2[1]['rise']:.0f} mV)")
a.plot(b3["tau"], b3["loss"], color="#ab47bc", lw=2.4, label=f"3D 단위 셀, 전하 1.25배 (몸체 +{b3['rise']:.0f} mV)")
a.plot([26, 31.5, 200], [23, 29, 50], "*", color="#fbc02d", ms=20, mec=INK, mew=1.0, zorder=5, label="논문 Fig. 8(b) Case 2 (그림 판독값)")
a.set_xlim(0, 205); a.set_ylim(-3, 62); a.set_xlabel("시간 [ns] (논문 축: 첫 BL 하강 21.0 ns, 주기 21 ns)", fontsize=12.5); a.set_ylabel("Case 2 저장 노드 손실 [mV] (t_A 기준)", fontsize=12.5)
a.grid(alpha=0.25); a.legend(fontsize=10, loc="upper left"); a.set_title("3D로 바꿔도 손실 곡선은 2D와 같은 크기예요", fontsize=14.5, fontweight="bold", color=INK)
b = ax[1]
b.plot([o["rise"] for o in D2], [o["first"] for o in D2], "-o", color=C2, lw=2.2, ms=7, label="2D 단면: 정공을 넣어 둔 상태 (×1 / 1.25 / 1.5 / 2)")
b.plot([a3["rise"], b3["rise"]], [a3["first"], b3["first"]], "D", color=C3, ms=11, mec=INK, mew=1.0, zorder=4, label="3D 단위 셀 (×1 / 1.25)")
b.plot([P.FBE_RISE[2]], [P.FBE_FIRST[2]], "*", color="#fbc02d", ms=22, mec=INK, mew=1.0, zorder=5, label="논문: (막대 445 mV, 첫 구간 손실 29 mV)")
b.set_yscale("log"); b.set_xlim(400, 700); b.set_ylim(0.8, 250); b.set_yticks([1, 3, 10, 30, 100]); b.set_yticklabels(["1", "3", "10", "30", "100"], fontsize=11); b.minorticks_off()
b.set_xlabel("t_A의 몸체 중심 전위 상승 [mV]", fontsize=12.5); b.set_ylabel("첫 BL 저전위 구간(10.5 ns)의 손실 [mV]", fontsize=12.5); b.grid(alpha=0.25, which="both"); b.legend(fontsize=10, loc="lower right")
b.set_title("같은 몸체 전위에서 3D 점이 2D 곡선 위에 있어요", fontsize=14.5, fontweight="bold", color=INK)
for s_ in ax:
    for sp in ("top", "right"): s_.spines[sp].set_visible(False)
fig.suptitle("3D 점검 (Case 2): 막대와 손실의 차이는 2D 단면 때문이 아니에요", fontsize=16, fontweight="bold", color=INK)
fig.tight_layout(); fig.savefig(OUT, dpi=125, bbox_inches="tight", facecolor="white"); print(OUT)
print(f"3D bar state: rise {a3['rise']:.0f} mV, first {a3['first']:.2f} mV, 200 ns {a3['l200']:.2f} mV | x 1.25: rise {b3['rise']:.0f}, first {b3['first']:.2f}, 200 ns {b3['l200']:.2f}")
