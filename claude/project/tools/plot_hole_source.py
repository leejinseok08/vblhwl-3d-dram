# plot_hole_source.py [out.png] - the open question "where does the hole charge of the body come from" in one picture.
# Left: the section of the cell along the channel (Fig.2 / Fig.5(a) dimensions, 20 nm body) in the hold state of Fig.8 (WL 0 V, BL
# and storage node at 1.1 V), with the places where electron-hole pairs are made in the model and where each carrier goes.
# Right: what is needed against what the model gives (generation current, time to fill), log scale. Numbers: NOTES (bf) .. (bk).
# A drawing with numbers typed in, no run data are read. Run on the PC: python tools/plot_hole_source.py
import sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram\gt2d_hole_source_problem.png"
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
INK = "#263238"; NP = "#e57373"; PB = "#90caf9"; GT = "#a5d6a7"; OX = "#eeeeee"; SP = "#bdbdbd"
fig, ax = plt.subplots(1, 2, figsize=(18.5, 7.2), gridspec_kw=dict(width_ratios=[1.75, 1]))
a = ax[0]; a.set_xlim(-12, 268); a.set_ylim(-78, 112); a.set_aspect("equal"); a.axis("off")
def box(x, y, w, h, c, t="", fs=10.5, **kw):
    a.add_patch(Rectangle((x, y), w, h, fc=c, ec=INK, lw=1.1, **kw))
    if t: a.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=INK)
box(0, -50, 50, 120, NP, "BL\n(N+)\n1.1 V"); box(50, 0, 25, 20, PB); box(75, 0, 100, 20, PB, "부유 몸체 (p형, 어디에도 연결되지 않음)", fs=10)
box(175, 0, 25, 20, NP); box(200, -8, 30, 36, NP, "저장\n노드\n1.1 V", fs=9.5)
for y in (20, -5): box(50, y, 150, 5, OX)                                    # gate oxide (5 nm)
for y in (25, -25): box(75, y, 100, 20, GT, "WL (게이트) 0 V" if y > 0 else "WL (백게이트) 0 V"); box(50, y, 25, 20, SP, "스페이서", fs=8); box(175, y, 25, 20, SP, "스페이서", fs=8)
a.plot([230, 248], [10, 10], color=INK, lw=1.5); a.plot([248, 248], [-2, 22], color=INK, lw=2.5); a.plot([254, 254], [-2, 22], color=INK, lw=2.5); a.plot([254, 264], [10, 10], color=INK, lw=1.5)
a.text(251, 30, "Cs\n1.5~2.2 fF", ha="center", fontsize=9.5, color=INK)
arrow = lambda p, q, c: a.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16, lw=2.2, color=c))
# 1: GIDL at the storage-node-side gate edge
a.plot([175], [17], "*", color="#f9a825", ms=22, mec=INK, zorder=6); arrow((177, 15), (212, 12), "#c62828"); arrow((172, 14), (140, 6), "#1565c0")
a.text(204, 30, "전자", color="#c62828", fontsize=10.5, fontweight="bold", va="bottom", ha="left"); a.text(139, 2, "정공", color="#1565c0", fontsize=10.5, fontweight="bold", ha="right")
a.text(160, 72, "① GIDL (밴드 간 터널링)\n게이트 끝(0 V)이 N+(1.1 V) 접합 위에 있어\n전계가 가장 센 곳. 모델: 9~14 pA.\n전자가 저장 노드로 들어가 노드 전압을 깎아요\n(생성된 전자의 96~97 %).", fontsize=10.2, color=INK, va="center", ha="left",
       bbox=dict(fc="#fff8e1", ec="#f9a825", lw=1.2))
a.annotate("", xy=(175, 19), xytext=(180, 58), arrowprops=dict(arrowstyle="-", color="#f9a825", lw=1.3))
# 2: impact ionization during the write, BL-side
a.plot([62], [4], "*", color="#8e24aa", ms=20, mec=INK, zorder=6)
a.text(-10, -66, "② 충돌 이온화 (쓰기 중, WL 1.8 V일 때): 전자–정공 쌍 600~900개가 생기지만,\nWL이 높은 동안 정공이 저장 노드 쪽으로 빠져나가 0~123개만 남아요. 계수를 7배로 키우면 1300~1970개가 남지만\n몸체를 접지한 셀이 1.1 V를 유지하지 못해서(논문 Fig. 7(c)와 반대) 기각했어요.", fontsize=10.2, color=INK, va="center", ha="left", bbox=dict(fc="#f3e5f5", ec="#8e24aa", lw=1.2))
a.annotate("", xy=(62, 2), xytext=(40, -55), arrowprops=dict(arrowstyle="-", color="#8e24aa", lw=1.3))
a.text(125, 102, "필요한 것: 몸체에 정공 1118~1579개 (0.18~0.25 fC)를 21 ns 안에, 저장 노드 전압은 그대로", fontsize=12, color="#0d47a1", fontweight="bold", ha="center")
a.annotate("", xy=(125, 21), xytext=(125, 97), arrowprops=dict(arrowstyle="-|>", color="#0d47a1", lw=1.6))
a.text(62.5, -34, "게이트가 없는\np 영역 25 nm\n(논문 Fig. 2)", fontsize=8.5, color=INK, ha="center", va="top")
a.set_title("유지 상태(WL 0 V, BL·저장 노드 1.1 V)의 셀 단면과 전자–정공 쌍이 생기는 곳", fontsize=14, fontweight="bold", color=INK)
b = ax[1]
lab = ["필요한 생성 전류\n(정공 약 1300개 ÷ 21 ns)", "모델의 GIDL\n(유지 중, 실측)"]; val = [10e-9, 11e-12]
b.barh([1, 0], val, color=["#0d47a1", "#f9a825"], height=0.55); b.set_xscale("log"); b.set_xlim(1e-12, 1e-6)
b.set_yticks([1, 0]); b.set_yticklabels(lab, fontsize=11.5); b.set_xlabel("전류", fontsize=12)
b.set_xticks([1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6]); b.set_xticklabels(["1 pA", "10 pA", "100 pA", "1 nA", "10 nA", "100 nA", "1 µA"], fontsize=10.5); b.minorticks_off()
b.text(10e-9 * 1.3, 1, "약 10 nA", va="center", fontsize=12, color=INK); b.text(11e-12 * 1.3, 0, "9~14 pA  (약 1/900)", va="center", fontsize=12, color=INK)
b.grid(alpha=0.25, axis="x"); b.set_ylim(-1.75, 1.6)
for sp in ("top", "right"): b.spines[sp].set_visible(False)
b.text(1.3e-12, -0.75, "그래서 모델에서는:\n· 채우는 데 13~21 µs가 걸려요 (논문 축은 21 ns)\n· 그동안 저장 노드가 110~140 mV 내려가요 (논문은 평탄)\n· 3D로 바꿔도 같아요 (21 ns 뒤 정공 32개, 2D는 37개)", fontsize=11.2, color=INK, va="top")
b.set_title("필요한 양과 모델이 주는 양", fontsize=14, fontweight="bold", color=INK)
fig.suptitle("정공 전하의 출처 문제: Fig. 8(a)의 몸체 전위 상승을 만드는 정공이 어디서 오는가", fontsize=16, fontweight="bold", color=INK)
fig.tight_layout(); fig.savefig(OUT, dpi=125, bbox_inches="tight", facecolor="white"); print(OUT)
