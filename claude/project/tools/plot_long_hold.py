# plot_long_hold.py [out.png] - round 11 in one picture: the FBE test of Fig.8 on the time scale of the papers the IRPS paper
# cites for it, with no stand-in generation. Left: rise of the body-centre potential against the hold time (log axis), the bars
# of Fig.8(a) as dashed lines; middle: what the storage node gives for it; right: loss in the first BL-low phase against the
# hold time, read over the first 10.5 ns after the first BL fall (the length of the paper's BL-low phase), the paper's losses dashed. Data: runs Dz6F_c1..5 (the whole charging curve),
# Dz3F .. Dz6F (losses), Dcs (the 21 ns point, default Hurkx A). Run on the PC: python tools/plot_long_hold.py
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gt_tran import load, at, edges
import paper_targets as P
RUNS = r"C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs"
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram\gt2d_long_hold_round11.png"
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
COL = {1: "#d32f2f", 2: "#c2185b", 3: "#1976d2", 4: "#f57c00", 5: "#388e3c"}; INK = "#263238"
NAME = {1: "Case 1 (30 nm)", 2: "Case 2 (20 nm)", 3: "Case 3 (10 nm, 1e18)", 4: "Case 4 (10 nm, 1e16)", 5: "Case 5 (1e16, WF 5.0)"}

def run(rid):
    d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn, bl, wl = s[k("nSN)")], s[k("nBL")], s[k("nWL)")]
    T = dv["time"]; kc = next(x for x in dv if "ElectrostaticPotential" in x)
    t0 = edges(t, wl, 0, 1.8, False)[0] + 4e-11; f = edges(t, bl, 0, 1.1, False); r = [x for x in edges(t, bl, 0, 1.1, True) if x > f[0]]
    tA = f[0] - 3e-10
    return dict(t0=t0, tA=tA, T=T, psi=dv[kc], t=t, sn=sn, p10=(at(t, sn, tA) - at(t, sn, f[0] + 10.5e-9 - 3e-10)) * 1e3)

fig, ax = plt.subplots(1, 3, figsize=(19, 6.0))
for c in range(1, 6):
    z = run(f"Dz6F_c{c}"); xs = [x for x in z["T"] if z["t0"] + 2e-9 < x <= z["tA"]]
    ax[0].plot([(x - z["t0"]) * 1e6 for x in xs], [(at(z["T"], z["psi"], x) - z["psi"][0]) * 1e3 for x in xs], color=COL[c], lw=2.3, label=f"2D 모델, {NAME[c]}")
    ax[0].axhline(P.FBE_RISE[c], color=COL[c], ls="--", lw=1.2)
    xt = [x for x in z["t"] if z["t0"] + 2e-9 < x <= z["tA"]]
    ax[1].plot([(x - z["t0"]) * 1e6 for x in xt], [(at(z["t"], z["sn"], x) - at(z["t"], z["sn"], z["t0"])) * 1e3 for x in xt], color=COL[c], lw=2.3, label=NAME[c])
    sc = [21e-3, 21, 210, 2100, 21000]; lo = [run(f"DcsF_c{c}")["p10"]] + [run(f"Dz{k}F_c{c}")["p10"] for k in (3, 4, 5, 6)]
    ax[2].plot(sc[:2], lo[:2], ":", color=COL[c], lw=1.6); ax[2].plot(sc[:1], lo[:1], "o", color=COL[c], ms=6)   # dotted: no run between
    ax[2].plot(sc[1:], lo[1:], "-o", color=COL[c], lw=2.2, ms=6, label=f"2D 모델, {NAME[c]}")
    if P.FBE_FIRST[c] > 0: ax[2].axhline(P.FBE_FIRST[c], color=COL[c], ls="--", lw=1.2)
for a in ax[:2]:
    a.set_xscale("log"); a.set_xlim(2e-3, 2.5e4); a.axvspan(13.3, 18.2, color="#ffe0b2", zorder=0); a.axvline(0.021, color=INK, ls=":", lw=1.6); a.axvline(21, color="#6a1b9a", ls=":", lw=1.4)
    a.set_xticks([1e-2, 1e-1, 1, 10, 100, 1e3, 1e4]); a.set_xticklabels(["10 ns", "100 ns", "1 µs", "10 µs", "100 µs", "1 ms", "10 ms"], fontsize=10.5); a.minorticks_off()
    a.set_xlabel("유지 시간 (t = 0: 저장 노드 충전 직후, WL 0 V, BL 1.1 V)", fontsize=12); a.grid(alpha=0.25)
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
ax[0].set_ylabel("몸체 중심 전위 상승 [mV]", fontsize=12.5); ax[0].set_ylim(0, 860)
ax[0].text(0.024, 830, "논문의 t_A\n(21 ns)", fontsize=10.5, color=INK, va="top"); ax[0].text(15.5, 848, "막대에 닿는 시간\n13~18 µs", fontsize=10.5, color="#e65100", ha="center", va="top")
ax[0].text(0.03, 690, "점선 = 논문 Fig. 8(a) 막대\n(555 / 445 / 365 / 320 / 368 mV)", fontsize=9.5, color=INK)
ax[0].set_title("몸체는 모델의 GIDL만으로 채워져요 (약 15 µs)", fontsize=14, fontweight="bold", color=INK); ax[0].legend(fontsize=9.5, loc="lower right")
ax[1].set_ylabel("저장 노드 전압 변화 [mV]", fontsize=12.5); ax[1].set_ylim(-280, 15); ax[1].axhline(0, color=INK, lw=1)
ax[1].text(0.03, -22, "논문 Fig. 8(b), (c): 변화 없음", fontsize=10.5, color=INK)
ax[1].set_title("그 전하는 저장 노드가 내줘요 (막대 시점에 −69 ~ −114 mV)", fontsize=14, fontweight="bold", color=INK); ax[1].legend(fontsize=9.5, loc="lower left")
ax[2].set_xscale("log"); ax[2].set_yscale("log"); ax[2].set_xlim(8e-3, 6e4); ax[2].set_ylim(0.03, 3000); ax[2].axvline(21, color="#6a1b9a", ls=":", lw=1.4)
ax[2].set_xticks([21e-3, 21, 210, 2100, 21000]); ax[2].set_xticklabels(["21 ns\n(논문 축)", "21 µs", "210 µs", "2.1 ms", "21 ms"], fontsize=10)
ax[2].set_xlabel("첫 BL 하강 전 유지 시간", fontsize=12); ax[2].set_ylabel("BL 하강 뒤 첫 10.5 ns의 저장 노드 손실 [mV]", fontsize=12.5); ax[2].grid(alpha=0.25); ax[2].minorticks_off()
ax[2].set_yticks([0.1, 1, 10, 100, 1000]); ax[2].set_yticklabels(["0.1", "1", "10", "100", "1000"], fontsize=10.5)
ax[2].text(9e-3, 2300, "가로 점선 = 논문 첫 구간(10.5 ns) 손실\n55 / 29 / 7.1 / 3.5 mV (Case 5는 0). 색은 왼쪽 그림과 같음\n기울어진 점선 = 사이에 실행 없음", fontsize=10.5, color=INK, va="top")
ax[2].text(26, 0.05, "유지 21 µs:\n손실이 논문의 0.5~1.2배,\n몸체는 막대보다 36~133 mV 높음", fontsize=10, color="#6a1b9a", va="bottom")
ax[2].set_title("첫 10.5 ns 손실은 유지 21 µs 근처에서 논문 크기예요", fontsize=14, fontweight="bold", color=INK)
for sp in ("top", "right"): ax[2].spines[sp].set_visible(False)
fig.suptitle("라운드 11: 유지 시간을 늘린 FBE (대리 생성 없음, 시간 척도만 변경). 세로 점선: 논문의 t_A 21 ns, 보라색 21 µs", fontsize=16, fontweight="bold", color=INK)
fig.tight_layout(); fig.savefig(OUT, dpi=125, bbox_inches="tight", facecolor="white"); print(OUT)
