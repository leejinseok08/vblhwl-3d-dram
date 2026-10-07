# plot_hsu_fig2c.py [out.png] - round 29: our 10 nm silicon cells at the conditions of the SILICON reference transistor of Hsu, Cho,
# Sharda, Park, Datta, Yu (IMW 2025 Fig.2(c); the same figure in TED 73(9), 2026): L 100 nm, t_Si 10 nm, W 100 nm, V_DS = 1 V, A/um.
# Points = the paper's blue curve as read off the embedded image (tools/gt_hsu_fig2c.py, HSU); lines = our runs. Left: the whole
# curve; right: the GIDL branch. Run on the PC; run files from GT_RUNS (default: the shared repository's claude/data/runs).
import sys, os, math
os.environ.setdefault("GT_RUNS", r"C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import gt_hsu_fig2c as H                 # sets GT_W = 1 (A/um)
G = H.G; RUNS = os.environ["GT_RUNS"]
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram\gt2d_hsu_fig2c_si_reference_round29.png"
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
INK = "#263238"; PAP = "#c62828"
SETS = (("DdrI_c3", "#1565c0", "-", 2.4, "우리 셀: 몸체 10 nm, N_A 1e18 (Case 3의 구조), 일함수 4.3 eV, Hurkx A 1.7e21 (맞춘 값)"),
        ("DdsI_c3", "#1565c0", ":", 1.8, "같은 셀, Hurkx A 기본값 3.5e21"),
        ("DdrI_c4", "#2e7d32", "-", 1.8, "우리 셀: N_A 1e16 (Case 4의 구조), 일함수 4.3 eV, A 1.7e21"),
        ("DdtI_c4", "#2e7d32", "--", 1.4, "같은 셀, V_DS 1.1 V (0.1 V의 영향)"))
fig, ax = plt.subplots(1, 2, figsize=(19, 8.2))
for a, (x0, x1, y0, y1) in zip(ax, ((-2.05, 2.55, 1e-17, 1e-2), (-1.9, -0.45, 1e-17, 3e-12))):
    for rid, col, ls, lw, lab in SETS:
        p = [q for q in G.curve(os.path.join(RUNS, rid)) if q[1] > 0]
        a.plot([v for v, i in p], [i for v, i in p], color=col, ls=ls, lw=lw, label=lab)
    a.plot(list(H.HSU), [10.0 ** l for l in H.HSU.values()], "D", color=PAP, ms=8, mec=INK, zorder=6, label="논문의 실리콘 비교 트랜지스터 (Hsu 외, Fig. 2(c), L = 100 nm: 그림에서 읽음)")
    a.set_yscale("log"); a.set(xlim=(x0, x1), ylim=(y0, y1)); a.grid(alpha=0.25)
    k = range(int(round(math.log10(y0))), int(math.floor(math.log10(y1))) + 1, 2 if a is ax[0] else 1)
    a.set_yticks([10.0 ** q for q in k]); a.set_yticklabels([f"1e{q}" for q in k]); a.minorticks_off()
    a.set_xlabel("게이트 전압 [V]  (V_DS = 1 V)", fontsize=12); a.set_ylabel("드레인 전류 [A/µm]", fontsize=12)
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
ax[0].legend(fontsize=9.5, loc="upper left"); ax[0].set_title("① Id–Vg 전체", fontsize=13.5, fontweight="bold", color=INK)
ax[1].set_title("② GIDL 가지 확대", fontsize=13.5, fontweight="bold", color=INK)
fig.suptitle("라운드 29: 같은 저자의 산화물 채널 논문에 실린 실리콘 비교 트랜지스터와 우리 셀 (2D, 새 맞춤 없음. 바꾼 것은 게이트 일함수뿐)", fontsize=15, fontweight="bold", color=INK)
fig.tight_layout(); fig.savefig(OUT, dpi=110, bbox_inches="tight", facecolor="white"); print(OUT)
