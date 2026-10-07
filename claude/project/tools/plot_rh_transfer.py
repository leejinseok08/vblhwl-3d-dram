# plot_rh_transfer.py <table> [out.png] [stalled runs, comma separated] - rounds 16 - 19 in one picture: the holes that impact
# ionization makes in the aggressor reach the victim's body through the shared N+ BL pillar.
# <table> = the text of tools/_rh_tab.sh (its last part, tools/gt_rh_wave.py: node and body inside the aggressor cycles).
# Left: the Z-Z' pair of the 2D section with the path of the holes and the two places of the BL contact. Middle: change of the
# victim's body potential (average under the gate) since the start of the hammer, model runs against the one number of Fig.7(e)
# (665.1 mV after the first aggressor pulse). Right: loss of the victim's storage node, log scale, against Fig.7(a) (read off the
# figure, typed in). A run that ends early is marked (stalled numerically, or not further computed). Run on the PC.
import sys, re
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
TAB = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram\gt2d_rh_hole_transfer_rounds16_19.png"
STALLED = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else {"Dg3Rzi_zz", "Dg3Ryi_yy", "Dg4Rzi_zz", "Dg5Rzi_zz", "Dg5Ryi_yy"}     # stopped by hand at 1e-16 s time steps
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
INK = "#263238"; PAP = "#c62828"; NP = "#e57373"; PB = "#90caf9"; GT = "#a5d6a7"; OX = "#f5f5f5"; SP = "#bdbdbd"; HOLE = "#1565c0"

W = {}; cur = None                                   # run -> rows (t [ns], aggressor WL, node [V], holes, centre [mV], average [mV] or None)
for ln in open(TAB, encoding="utf-8", errors="replace"):
    m = re.match(r"== (\S+): hammer from", ln)
    if m: cur = W.setdefault(m.group(1), []); cur.clear(); continue
    if ln.startswith("== "): cur = None; continue
    if cur is None: continue
    try: v = [float(x) for x in ln.split()]
    except ValueError: continue
    if len(v) < 5: continue
    if abs(v[0]) < 1e-9: v.insert(3, 0.0)            # the first row has no step
    cur.append((v[0], v[1], v[2], v[4], v[5], v[6] if len(v) > 6 else None))

RUNS = [("DfinRzi_zz", "기본 구동력, 접촉은 기둥 축 (지금까지의 모델)", "#78909c", "-"),
        ("Dg1Rzi_zz", "ElectricField, 접촉은 기둥 축", "#8d6e63", "-"),
        ("Dg9Rzbi_zz", "ElectricField, 접촉은 기둥 아래 끝", "#1565c0", "-"),
        ("Dg8Rzi_zz", "ElectricField, 접촉이 정공을 받지 않음", "#2e7d32", "-"),
        ("Dg0Rzbi_zz", "ElectricField, 접촉은 기둥 아래 끝, 커패시터 4.2 fF", "#6a1b9a", "-"),
        ("Dg1Ryi_yy", "Y–Y': ElectricField, 접촉은 기둥 위 끝", "#ef6c00", "--")]
EXTRA = [("Dg6Rzi_zz", "#2e7d32")]       # contact takes no holes, 4.2 fF (two cycles): thin dotted

fig, ax = plt.subplots(1, 3, figsize=(21, 7.2), gridspec_kw=dict(width_ratios=[1.0, 1.0, 1.0]))
a = ax[0]; a.set_xlim(-30, 240); a.set_ylim(-42, 236); a.set_aspect("equal"); a.axis("off")
def box(x, y, w, h, c, t="", fs=9.5):
    a.add_patch(Rectangle((x, y), w, h, fc=c, ec=INK, lw=1.0))
    if t: a.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=INK)
box(0, 0, 50, 200, NP); a.text(25, 186, "BL 기둥 (N+)\n0.55 V", ha="center", va="center", fontsize=9, color=INK)
for yb, who in ((0, "피해 셀"), (100, "공격 셀")):
    y1 = yb + 15
    box(50, y1 + 25, 25, 20, PB); box(75, y1 + 25, 100, 20, PB); box(175, y1 + 25, 25, 20, NP, "N+", fs=8)
    a.text(138, y1 + 35, f"{who} 몸체 (p, 부유)", ha="center", va="center", fontsize=9.3, color=INK)
    for y in (y1 + 20, y1 + 45): box(50, y, 150, 5, OX)
    for y in (y1, y1 + 50):
        box(75, y, 100, 20, GT, "WL 0 ↔ 1.8 V" if yb else "WL 0 V", fs=9); box(50, y, 25, 20, SP); box(175, y, 25, 20, SP)
a.text(206, 140, "저장\n노드", fontsize=8.5, va="center", color=INK); a.text(206, 50, "저장 노드\n1.1 V", fontsize=8.5, va="center", color=INK)
arr = lambda p, q: a.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16, lw=2.4, color=HOLE, connectionstyle="arc3,rad=0.25"))
a.plot([184], [159], "*", color="#f9a825", ms=22, mec=INK, zorder=6); a.text(206, 178, "① 충돌\n이온화", fontsize=9.5, ha="left", va="center", color=INK, fontweight="bold")
arr((98, 155), (58, 155)); arr((40, 146), (40, 60)); arr((52, 46), (96, 46))
a.text(84, 146, "② 정공", fontsize=9.5, color=HOLE, fontweight="bold", ha="center"); a.text(20, 104, "③ N+\n기둥을\n지나감", fontsize=9, color=HOLE, fontweight="bold", ha="center", va="center")
a.text(125, 7, "④ 피해 셀 몸체에 쌓임 → 몸체 전위 상승", fontsize=9.5, color=HOLE, fontweight="bold", ha="center", va="center")
a.plot([0, 0], [0, 200], color="#8d6e63", lw=5, solid_capstyle="butt")
a.text(-6, 100, "접촉을 기둥 축에 둔 경우\n(지금까지의 2D 단면): 정공을 흡수", fontsize=8.8, color="#8d6e63", rotation=90, ha="right", va="center")
a.plot([0, 50], [0, 0], color="#0d47a1", lw=6, solid_capstyle="butt"); a.text(25, -9, "접촉을 기둥 끝에 둔 경우\n(실제 기둥의 접촉 위치)", fontsize=8.8, color="#0d47a1", ha="center", va="top")
a.text(105, 227, "p(공격 셀 몸체) – N+(BL 기둥) – p(피해 셀 몸체): pnp 배치", fontsize=10.5, color=INK, ha="center", fontweight="bold")
a.set_title("Z–Z' 쌍의 단면과 정공이 넘어가는 길", fontsize=13.5, fontweight="bold", color=INK)

b = ax[1]; c = ax[2]
for i in range(10):
    b.axvspan(0.188 * i, 0.188 * i + 0.094, color="#fff3e0", zorder=0); c.axvspan(0.188 * i, 0.188 * i + 0.094, color="#fff3e0", zorder=0)
for rid, lab, col, ls in RUNS:
    r = W.get(rid)
    if not r: continue
    t = [x[0] for x in r]; av = [x[5] if x[5] is not None else x[4] for x in r]; nd = [x[2] for x in r]
    full = t[-1] > 1.8; note = "" if full else f"  ({t[-1]:.2f} ns에서 계산이 멈춤)" if rid in STALLED else f"  ({t[-1]:.2f} ns까지 계산)"
    b.plot(t, [v - av[0] for v in av], color=col, lw=2.0, ls=ls, label=lab + note)
    loss = [max((nd[0] - v) * 1e3, 1e-3) for v in nd]
    c.plot(t[1:], loss[1:], color=col, lw=2.0, ls=ls)
    if not full: b.plot(t[-1], av[-1] - av[0], "x", color=col, ms=10, mew=2.5); c.plot(t[-1], loss[-1], "x", color=col, ms=10, mew=2.5)
for rid, col in EXTRA:
    r = W.get(rid)
    if not r or len(r) < 9: continue
    t = [x[0] for x in r]; av = [x[5] if x[5] is not None else x[4] for x in r]; nd = [x[2] for x in r]
    b.plot(t, [v - av[0] for v in av], color=col, lw=1.1, ls=":"); c.plot(t[1:], [max((nd[0] - v) * 1e3, 1e-3) for v in nd][1:], color=col, lw=1.1, ls=":")
b.plot([0.094], [665.1], "D", color=PAP, ms=11, mec=INK, zorder=7, label="논문 Fig. 7(e): 첫 펄스 뒤 665.1 mV")
b.set_xlim(0, 2.0); b.set_ylim(-30, 1350); b.set_xlabel("해머 시작부터의 시간 [ns]  (연한 띠: 공격 WL이 1.8 V)", fontsize=11)
b.set_ylabel("피해 셀 몸체 전위의 변화 [mV]\n(게이트 아래 평균, 해머 시작 기준)", fontsize=11); b.legend(fontsize=8.8, loc="upper right"); b.grid(alpha=0.25)
b.set_title("피해 셀의 몸체 전위 (충돌 이온화 켬)", fontsize=13.5, fontweight="bold", color=INK)
tp = [0.285, 0.30, 0.40, 0.50, 0.60, 0.71, 0.80, 0.91, 1.00, 1.10, 1.20, 1.30, 1.40, 1.50, 2.0]
vp = [1.099, 1.07, 1.07, 0.95, 0.94, 0.83, 0.82, 0.74, 0.74, 0.67, 0.67, 0.61, 0.61, 0.585, 0.585]
c.plot(tp, [(1.1 - v) * 1e3 for v in vp], color=PAP, lw=2.4, marker="o", ms=4, label="논문 Fig. 7(a) (그림에서 읽음)")
c.axhline(605, color=PAP, lw=0.8, ls=":"); c.text(1.98, 640, "허용 손실 0.605 V", fontsize=8.8, color=PAP, ha="right")
c.set_yscale("log"); c.set_ylim(0.02, 1500); c.set_xlim(0, 2.0); c.set_yticks([0.1, 1, 10, 100, 1000]); c.set_yticklabels(["0.1", "1", "10", "100", "1000"]); c.minorticks_off()
c.set_xlabel("해머 시작부터의 시간 [ns]", fontsize=11); c.set_ylabel("피해 셀 저장 노드의 손실 [mV] (로그)", fontsize=11); c.legend(fontsize=9.5, loc="lower right"); c.grid(alpha=0.25)
c.set_title("피해 셀의 저장 노드 (선 색은 가운데 그림과 같음)", fontsize=13.5, fontweight="bold", color=INK)
for q in (b, c):
    for sp in ("top", "right"): q.spines[sp].set_visible(False)
fig.suptitle("라운드 16~19: 공격 셀에서 충돌 이온화로 생긴 정공이 BL 기둥을 지나 피해 셀 몸체로 넘어가는가 (Case 2, 2D, 역산 후보)", fontsize=15, fontweight="bold", color=INK)
fig.tight_layout(); fig.savefig(OUT, dpi=120, bbox_inches="tight", facecolor="white"); print(OUT, {k: (len(v), round(v[-1][0], 3)) for k, v in W.items() if v and k[2] in "0689"})
