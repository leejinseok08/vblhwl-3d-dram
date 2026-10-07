# make_eliu_report_1007.py - report of the afternoon of 2026-10-07 written with the user's skill eliU (reader: an EE junior; simple
# structure and short sentences, the real terms, every new idea tied to something from the coursework, every number with unit
# and source). Content: rounds 15 - 20 and the 3D confirmation (NOTES (bl), (bm)). The page builder, the text checks and the
# style are those of tools/make_eliu_report.py. Draws gt2d_eliu1007_01 .. 09 into Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram and
# writes one HTML file with the pictures embedded into ...\results_vbl_hwl_1t1c_3ddram. Run on the PC: python tools/make_eliu_report_1007.py
# Data: the run files of the shared working copy (C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs). The numbers typed into the
# text are checked against those files (CHECK at the end). No picture of the paper is used: its values are numbers read off its figures.
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import make_eliu_report as M
import paper_targets as P
load, at, edges, key, save, clean, INK, RUNS = M.load, M.at, M.edges, M.key, M.save, M.clean, M.INK, M.RUNS
OUT = os.path.join(M.BASE, "results_vbl_hwl_1t1c_3ddram", "GT_IRPS2026_현황보고_eliU_2026-10-07_오후.html")
PAP, HOLE, BAND = "#c62828", "#1565c0", "#fff3e0"
CB = dict(fin="#78909c", axis="#8d6e63", end="#1565c0", none="#2e7d32", end42="#6a1b9a", yy="#ef6c00")

# ------------------------------------------------------------------ data
def run(rid):             # system file, device file and description of one run of the shared copy
    d = os.path.join(RUNS, rid)
    return load(os.path.join(d, rid + "_sys.plt")), load(glob.glob(os.path.join(d, "*_dev.plt"))[0]), json.load(open(os.path.join(d, "run.json"), encoding="utf-8"))

def hammer(rid, n=8):     # a row-hammer pair run inside the aggressor cycles, n points per cycle from the start of the hammer
    s, dv, j = run(rid); t, T = s["time"], dv["time"]; p = j["params"]; tS = j["sched"]["tS"]; per = (p["tON"] + p["tOFF"]) * 1e-9; end = min(t[-1], T[-1])
    sn = s[key(s, "nSN)")]; hv = dv[next(q for q in dv if "hDensity" in q and "Ch_a" not in q)]
    kb = next((q for q in dv if q.startswith("AveWindow") and "ElectrostaticPotential" in q), None) or next(q for q in dv if q.startswith("Pos") and "ElectrostaticPotential" in q)
    xs = [tS + i * per / n for i in range(10 * n + 1) if tS + i * per / n <= end + 1e-15]; c = (len(xs) - 1) // n
    v = [at(t, sn, x) for x in xs]; b = [(at(T, dv[kb], x) - dv[kb][0]) * 1e3 for x in xs]; h = [at(T, hv, x) * 1e-13 for x in xs]
    return dict(t=[(x - tS) * 1e9 for x in xs], sn=v, holes=h, body=[y - b[0] for y in b], body0=b[0], cyc=[(v[(i - 1) * n] - v[i * n]) * 1e3 for i in range(1, c + 1)],
                hend=[h[i * n] for i in range(c + 1)], pulse=b[n // 2] - b[0], hpulse=h[n // 2] - h[0])

def last5(rid):           # loss of the node per cycle over the last five of the ten cycles [mV]
    return sum(hammer(rid, 1)["cyc"][-5:]) / 5

def write(rid):           # write curve: time after the WL edge [ps], storage node [V]
    s = load(os.path.join(RUNS, rid, rid + "_sys.plt")); t = s["time"]; t0 = edges(t, s[key(s, "nWL)")], 0, 1.8, True)[0]
    return [(x - t0) * 1e12 for x in t], s[key(s, "nSN)")]

def fbe(rid):             # an FBE run (2D or 3D): holes at t_A, gated-body average 0.25 ns after the fall, losses; a stalled run: holes at its end
    s, dv, j = run(rid); t, T = s["time"], dv["time"]; sn = s[key(s, "nSN)")]; bl = s[key(s, "nBL")]
    hf = 2e-12 if next(q for q in dv if "ElectrostaticPotential" in q).count(",") == 2 else 1e-13; kh = next(q for q in dv if "hDensity" in q)
    ka = next((q for q in dv if q.startswith("AveWindow((0.075") or q.startswith("AveWindow((0.05,0.04,0)")), None); f = edges(t, bl, 0, 1.1, False); end = min(t[-1], T[-1])
    if not f or end < f[0] + 1.8e-7: return dict(holes=at(T, dv[kh], end) * hf, done=False)
    r = [x for x in edges(t, bl, 0, 1.1, True) if x > f[0]]; tA = f[0] - 3e-10; L = lambda x: (at(t, sn, tA) - at(t, sn, x)) * 1e3
    return dict(holes=at(T, dv[kh], tA) * hf, avg=(at(T, dv[ka], f[0] + 5e-10) - dv[ka][0]) * 1e3, l5=L(f[0] + 5e-9), first=L(r[0] - 3e-10), l200=L(f[0] + 179e-9), done=True)

# ------------------------------------------------------------------ pictures (one message each; paper = open markers or hatched bars)
def bands(a):
    for i in range(10): a.axvspan(0.188 * i, 0.188 * i + 0.094, color=BAND, zorder=0)

def fig_pair():
    NP, PB, GT, OX, SP = "#e57373", "#90caf9", "#a5d6a7", "#f5f5f5", "#bdbdbd"
    fig, a = plt.subplots(figsize=(12.5, 8.6)); a.set_xlim(-40, 262); a.set_ylim(-50, 246); a.set_aspect("equal"); a.axis("off")
    def box(x, y, w, h, c, t="", fs=11):
        a.add_patch(Rectangle((x, y), w, h, fc=c, ec=INK, lw=1.0))
        if t: a.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=INK)
    box(0, 0, 50, 200, NP); a.text(25, 186, "BL 기둥 (N+)\n0.55 V", ha="center", va="center", fontsize=10.5, color=INK)
    for yb, who in ((0, "피해 셀"), (100, "공격 셀")):
        y1 = yb + 15
        box(50, y1 + 25, 25, 20, PB); box(75, y1 + 25, 100, 20, PB); box(175, y1 + 25, 25, 20, NP, "N+", fs=9)
        a.text(126, y1 + 35, f"{who} 몸체 (p)", ha="center", va="center", fontsize=10.5, color=INK)
        for y in (y1 + 20, y1 + 45): box(50, y, 150, 5, OX)
        for y in (y1, y1 + 50):
            box(75, y, 100, 20, GT, "WL 0 ↔ 1.8 V" if yb else "WL 0 V", fs=10.5); box(50, y, 25, 20, SP); box(175, y, 25, 20, SP)
    a.text(206, 146, "저장 노드", fontsize=10, va="center", color=INK); a.text(206, 50, "저장 노드\n1.1 V", fontsize=10, va="center", color=INK)
    a.text(128, 107, "위: 공격 셀 (aggressor), WL 0 ↔ 1.8 V 반복", fontsize=10, ha="center", va="center", color=INK)
    a.text(128, 93, "아래: 피해 셀 (victim), WL 0 V", fontsize=10, ha="center", va="center", color=INK)
    arr = lambda p, q: a.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=18, lw=2.6, color=HOLE, connectionstyle="arc3,rad=0.25"))
    a.plot([165], [150], "*", color="#f9a825", ms=22, mec=INK, zorder=6); a.text(206, 176, "① 충돌 이온화로\n전자–정공 쌍 생성", fontsize=10.5, ha="left", va="center", color=INK, fontweight="bold")
    a.annotate("", xy=(169, 153), xytext=(204, 171), arrowprops=dict(arrowstyle="-", color=INK, lw=1.0))
    arr((98, 155), (58, 155)); arr((40, 146), (40, 60)); arr((52, 46), (94, 46))
    a.text(82, 145, "② 정공", fontsize=10.5, color=HOLE, fontweight="bold", ha="center"); a.text(20, 104, "③ N+\n기둥을\n지나감", fontsize=10, color=HOLE, fontweight="bold", ha="center", va="center")
    a.text(125, 7, "④ 피해 셀 몸체에 쌓임 → 몸체 전위 상승", fontsize=10.5, color=HOLE, fontweight="bold", ha="center", va="center")
    a.plot([0, 0], [0, 200], color="#8d6e63", lw=5, solid_capstyle="butt")
    a.text(-7, 100, "BL 접촉을 기둥 축에 둔 경우\n(지금까지의 2D 단면): 정공이 여기서 사라짐", fontsize=9.8, color="#8d6e63", rotation=90, ha="right", va="center")
    a.plot([0, 50], [0, 0], color="#0d47a1", lw=6, solid_capstyle="butt"); a.text(25, -9, "BL 접촉을 기둥 끝에 둔 경우\n(새 구조 gr_zzb)", fontsize=10, color="#0d47a1", ha="center", va="top")
    a.text(110, 232, "p (공격 셀 몸체) – N+ (BL 기둥) – p (피해 셀 몸체): pnp BJT와 같은 배치", fontsize=12, color=INK, ha="center", fontweight="bold")
    a.set_title("Z–Z' 쌍(위아래 층 이웃)의 2D 단면과, 정공이 넘어가는 길", fontsize=16, fontweight="bold", color=INK)
    return save(fig, "gt2d_eliu1007_01_pair.png")

def fig_hist():
    G = [("Y–Y' (BL 기둥 건너편 이웃)", P.RH["yy"], [("이력 없음", "DfinRy_yy", HOLE), ("16.2 µs 이력", "Dx2Ry_yy", HOLE), ("16.2 µs\n대조군", "Dx5Ry_yy", "#90a4ae"), ("100 µs 이력", "Dx7Ry_yy", HOLE), ("100 µs\n대조군", "Dx6Ry_yy", "#90a4ae")]),
         ("Z–Z' (위아래 층 이웃)", P.RH["zz"], [("이력 없음", "DfinRz_zz", HOLE), ("16.2 µs 이력", "Dx2Rz_zz", HOLE), ("16.2 µs\n대조군", "Dx5Rz_zz", "#90a4ae"), ("100 µs 이력", "Dx7Rz_zz", HOLE), ("100 µs\n대조군", "Dx6Rz_zz", "#90a4ae")])]
    fig, ax = plt.subplots(figsize=(14.5, 6.4)); x = 0; ticks = []; labs = []
    for name, pap, rows in G:
        x0 = x; ax.bar(x, pap, 0.7, fc="white", ec=PAP, hatch="//", lw=1.6, zorder=3); ax.text(x, pap * 1.2, f"{pap:.4f}", ha="center", fontsize=11, color=PAP); ticks.append(x); labs.append("논문"); x += 1
        for lab, rid, col in rows:
            v = last5(rid); ax.bar(x, v, 0.7, color=col, zorder=3); ax.text(x, v * 1.2, f"{v:.5f}", ha="center", fontsize=10.5, color=INK); ticks.append(x); labs.append(lab); x += 1
        ax.text((x0 + x - 1) / 2, 0.42, name, ha="center", fontsize=13, fontweight="bold", color=INK); x += 0.8
    ax.set_yscale("log"); ax.set_ylim(1e-4, 0.7); ax.set_yticks([1e-4, 1e-3, 1e-2, 1e-1]); ax.set_yticklabels(["0.0001", "0.001", "0.01", "0.1"], fontsize=11); ax.minorticks_off()
    ax.set_xticks(ticks); ax.set_xticklabels(labs, fontsize=10.5); ax.set_ylabel("저장 노드 손실 [mV / 사이클] (마지막 5사이클)", fontsize=12.5); ax.grid(axis="y", alpha=0.25, zorder=0)
    ax.bar([-9], [1], fc="white", ec=PAP, hatch="//", label="논문 (본문의 임계 사이클 수에서 계산)"); ax.bar([-9], [1], color=HOLE, label="2D 모델: 공격 WL 0 ↔ 1.8 V"); ax.bar([-9], [1], color="#90a4ae", label="2D 모델, 대조군: 공격 WL 0 V")
    ax.set_xlim(-0.8, x - 1); ax.legend(fontsize=11, loc="upper right", bbox_to_anchor=(1.0, 0.86)); clean(ax)
    ax.set_title("라운드 15: 몸체를 미리 채워도(이력) 손실은 대조군과 같아요 (충돌 이온화 끔)", fontsize=16, fontweight="bold", color=INK, pad=10)
    return save(fig, "gt2d_eliu1007_02_history.png")

TP = [0.0, 0.285, 0.30, 0.40, 0.50, 0.60, 0.71, 0.80, 0.91, 1.00, 1.10, 1.20, 1.30, 1.40, 1.50, 2.0]            # Fig.7(a), (c): read off the figure
VP = [1.10, 1.10, 1.07, 1.07, 0.95, 0.94, 0.83, 0.82, 0.74, 0.74, 0.67, 0.67, 0.61, 0.61, 0.585, 0.585]
def fig_paper7():
    fig, ax = plt.subplots(figsize=(13.5, 6.6)); bands(ax)
    ax.plot(TP, VP, "-o", color=PAP, mfc="white", lw=2.2, ms=7, mew=1.8, zorder=4, label="논문 Fig. 7(a), (c): Z–Z' 피해 셀의 저장 노드, 충돌 이온화 켬 (그림에서 읽은 값)")
    for x, lab in ((0.0, "t = 0"), (0.094, "t = t_A\n(0.09 ns)")):
        ax.axvline(x, color=INK, ls="--", lw=1.6, zorder=3); ax.text(x + 0.012, 1.215, lab, fontsize=11.5, color=INK, va="top")
    ax.axvline(0.45, color="#b0bec5", ls=":", lw=1.6, zorder=2); ax.text(0.46, 0.60, "전에 읽은 t_A (0.45 ns): 틀림", fontsize=10.5, color="#78909c")
    ax.annotate("이 94 ps 동안의 몸체 전위 변화 (Fig. 7(e)에 적힌 값)\n충돌 이온화 끔 2.4 mV  /  켬 665.1 mV  /  켬 + 몸체 접지 1.8 mV", xy=(0.047, 1.145), xytext=(0.62, 1.185), fontsize=11.5, color=INK,
                va="center", arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4), bbox=dict(fc="white", ec="#b0bec5", pad=5))
    ax.annotate("펄스 1, 2 동안: 1.1 V 그대로", xy=(0.2, 1.1), xytext=(0.02, 0.83), fontsize=11.5, color=INK, arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    ax.annotate("공격 WL이 1.8 V인 구간에서만 내려감\n(펄스당 0.12 / 0.11 / 0.08 / 0.07 / 0.06 / 0.03 V)", xy=(0.655, 0.885), xytext=(0.95, 0.96), fontsize=11.5, color=INK, arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    ax.annotate("0.58 V에서 멈춤 (BL은 0.55 V)", xy=(1.75, 0.585), xytext=(1.38, 0.50), fontsize=11.5, color=INK, arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    ax.set_xlim(-0.03, 2.0); ax.set_ylim(0.44, 1.23); ax.set_xlabel("해머 시작부터의 시간 [ns]  (연한 띠: 공격 WL이 1.8 V인 구간)", fontsize=12.5); ax.set_ylabel("저장 노드 전압 [V]", fontsize=12.5)
    ax.legend(fontsize=11, loc="lower left"); ax.grid(alpha=0.25); clean(ax)
    ax.set_title("논문 Fig. 7을 다시 읽은 것: t_A는 첫 번째 공격 펄스의 끝이에요", fontsize=16, fontweight="bold", color=INK, pad=10)
    return save(fig, "gt2d_eliu1007_03_paper_fig7.png")

SET = [("DfinRzi_zz", "기본 구동력, BL 접촉은 기둥 축 (지금까지의 모델)", CB["fin"], "-"), ("Dg1Rzi_zz", "ElectricField, BL 접촉은 기둥 축", CB["axis"], "-"),
       ("Dg9Rzbi_zz", "ElectricField, BL 접촉은 기둥 끝", CB["end"], "-"), ("Dg8Rzi_zz", "ElectricField, BL 접촉이 정공을 받지 않음", CB["none"], "-"),
       ("Dg0Rzbi_zz", "ElectricField, BL 접촉은 기둥 끝, 커패시터 4.2 fF", CB["end42"], "-")]
def fig_body(H):
    fig, ax = plt.subplots(figsize=(13.5, 6.6)); bands(ax)
    for rid, lab, col, ls in SET:
        h = H[rid]; full = h["t"][-1] > 1.8
        ax.plot(h["t"], h["body"], color=col, lw=2.3, ls=ls, zorder=3, label=lab + ("" if full else f"  ({len(h['cyc'])}사이클까지 계산)"))
        if not full: ax.plot(h["t"][-1], h["body"][-1], "x", color=col, ms=10, mew=2.6, zorder=4)
    ax.plot([0.094], [665.1], "D", mfc="white", color=PAP, ms=12, mew=2.2, zorder=6, label="논문 Fig. 7(e): 첫 펄스 뒤 665.1 mV (그림에 적힌 값)")
    ax.set_xlim(0, 2.0); ax.set_ylim(-30, 1250); ax.set_xlabel("해머 시작부터의 시간 [ns]  (연한 띠: 공격 WL이 1.8 V인 구간)", fontsize=12.5)
    ax.set_ylabel("피해 셀 몸체 전위의 변화 [mV]\n(게이트 아래 평균, 해머 시작 기준)", fontsize=12.5); ax.legend(fontsize=10.5, loc="upper right"); ax.grid(alpha=0.25); clean(ax)
    ax.set_title("ElectricField + 기둥 끝 접촉이면 첫 공격 펄스 안에 피해 셀 몸체가 충전돼요", fontsize=16, fontweight="bold", color=INK, pad=10)
    return save(fig, "gt2d_eliu1007_04_body.png")

def fig_steps(H):
    fig, ax = plt.subplots(figsize=(13.5, 6.2)); bands(ax)
    for rid, lab, col, ls in SET[2:]:
        h = H[rid]; ax.plot(h["t"], [(v - h["sn"][0]) * 1e3 for v in h["sn"]], color=col, lw=2.4, marker="o", ms=3.5, zorder=3, label=lab)
    ax.set_xlim(0, 1.36); ax.set_ylim(-36, 3); ax.set_xlabel("해머 시작부터의 시간 [ns]  (연한 띠: 공격 WL이 1.8 V인 구간)", fontsize=12.5); ax.set_ylabel("저장 노드 전압의 변화 [mV]", fontsize=12.5)
    ax.legend(fontsize=11, loc="lower left"); ax.grid(alpha=0.25); clean(ax)
    ax.set_title("2D 모델: 노드는 주로 공격 WL이 높은 구간에서 내려가요 (손실의 약 80 %)", fontsize=15.5, fontweight="bold", color=INK, pad=10)
    return save(fig, "gt2d_eliu1007_05_steps.png")

def fig_size(H):
    fig, ax = plt.subplots(figsize=(13.5, 6.6)); bands(ax)
    ax.plot(TP[1:], [max((1.1 - v) * 1e3, 1.0) for v in VP[1:]], "-o", color=PAP, mfc="white", lw=2.2, ms=7, mew=1.8, zorder=4, label="논문 Fig. 7(a): Z–Z', 충돌 이온화 켬 (그림에서 읽은 값)")
    for rid, lab, col, ls in SET[2:] + [("Dg1Ryi_yy", "Y–Y': ElectricField, BL 접촉은 기둥 위 끝", CB["yy"], "--")]:
        h = H[rid]; loss = [max((h["sn"][0] - v) * 1e3, 1e-3) for v in h["sn"]]
        ax.plot(h["t"][1:], loss[1:], color=col, lw=2.2, ls=ls, zorder=3, label=lab)
        if h["t"][-1] < 1.8: ax.plot(h["t"][-1], loss[-1], "x", color=col, ms=10, mew=2.6, zorder=4)
    ax.axhline(605, color=PAP, lw=1.0, ls=":"); ax.text(1.98, 680, "허용 손실 0.605 V (논문의 임계 사이클 수 계산에 쓰인 값)", fontsize=10.5, color=PAP, ha="right")
    ax.set_yscale("log"); ax.set_ylim(0.05, 2500); ax.set_xlim(0, 2.0); ax.set_yticks([0.1, 1, 10, 100, 1000]); ax.set_yticklabels(["0.1", "1", "10", "100", "1000"], fontsize=11); ax.minorticks_off()
    ax.set_xlabel("해머 시작부터의 시간 [ns]", fontsize=12.5); ax.set_ylabel("피해 셀 저장 노드의 손실 [mV] (로그 축)", fontsize=12.5); ax.legend(fontsize=10.2, loc="lower right"); ax.grid(alpha=0.25); clean(ax)
    ax.set_title("크기는 아직 안 맞아요: 논문은 1 ns에 수백 mV, 2D 모델은 수십 mV", fontsize=16, fontweight="bold", color=INK, pad=10)
    return save(fig, "gt2d_eliu1007_06_size.png")

def fig_write():
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    for rid, lab, col in (("DfinW_c2", "기본 구동력, 1.8 fF (구성 fin3: 쓰기 곡선에 맞춘 값)", "#1976d2"), ("Db0W_c2", "기본 구동력, 4.2 fF (본문의 값)", "#78909c"), ("Do4W_c2", "ElectricField, 4.2 fF (본문의 값)", "#2e7d32")):
        t, v = write(rid); ax.plot(t, v, color=col, lw=2.5, zorder=3, label="2D 모델: " + lab)
    ax.plot(list(P.WRITE), list(P.WRITE.values()), "o", mfc="white", color=PAP, ms=11, mew=2.2, zorder=5, label="논문 Fig. 4(a) (그림에서 읽은 값)")
    ax.set_xlim(-3, 100); ax.set_ylim(0, 1.25); ax.set_xlabel("WL 상승 뒤 시간 [ps]", fontsize=12.5); ax.set_ylabel("저장 노드 전압 [V]", fontsize=12.5); ax.legend(fontsize=11.5, loc="lower right"); ax.grid(alpha=0.25); clean(ax)
    ax.set_title("쓰기 곡선: ElectricField에서는 본문의 4.2 fF가 느리지 않고 조금 빨라요", fontsize=16, fontweight="bold", color=INK, pad=10)
    return save(fig, "gt2d_eliu1007_07_write.png")

def fig_holes(F):
    S = [("Ds2F", "필요한 정공 수 (구성 fin3: Fig. 8(a) 막대에 맞춘 조건)", dict(fc="white", ec=PAP, hatch="//", lw=1.6)), ("Do1F", "쓰기가 남긴 수: ElectricField, BL 접촉이 정공을 받지 않음", dict(color="#1565c0")),
         ("Do4F", "같은 설정, 본문 커패시터 (5.1 / 4.2 / 3.6 fF)", dict(color="#6a1b9a")), ("Do2F", "저장 노드 접촉도 정공을 받지 않음 (쓰기 직후, 그 뒤 계산이 멈춤)", dict(color="#ef6c00"))]
    fig, ax = plt.subplots(figsize=(13.5, 6.4)); w = 0.2
    for k, (tag, lab, kw) in enumerate(S):
        v = [F[tag][c]["holes"] for c in range(1, 6)]; x = [c + (k - 1.5) * w for c in range(1, 6)]; ax.bar(x, v, w * 0.92, zorder=3, label=lab, **kw)
        for a, b in zip(x, v): ax.text(a, b * 1.12, f"{b:.0f}", ha="center", fontsize=9.5, color=INK)
    ax.set_yscale("log"); ax.set_ylim(2, 600000); ax.set_yticks([10, 100, 1000, 10000]); ax.set_yticklabels(["10", "100", "1000", "10000"], fontsize=11); ax.minorticks_off()
    ax.set_xticks(range(1, 6)); ax.set_xticklabels(["Case 1\n30 nm", "Case 2\n20 nm", "Case 3\n10 nm", "Case 4\n10 nm, 1e16", "Case 5\n1e16, WF 5.0"], fontsize=11.5)
    ax.set_ylabel("몸체의 정공 수 [개] (로그 축)", fontsize=12.5); ax.legend(fontsize=10.5, loc="upper right", ncol=1); ax.grid(axis="y", alpha=0.25, zorder=0); clean(ax)
    ax.set_title("Fig. 8의 정공 전하: 쓰기의 충돌 이온화만으로는 모자라거나 넘쳐요 (대리 생성 없음)", fontsize=15.5, fontweight="bold", color=INK, pad=10)
    return save(fig, "gt2d_eliu1007_08_holes.png")

def fig_3d(D2, D3):
    Q = [("Fig. 8(a) 막대 [mV]", P.FBE_RISE[2], D2["avg"], D3["avg"], (P.FBE_RISE[2] - 30, P.FBE_RISE[2] + 30)), ("하강 5 ns 뒤 손실 [mV]", 23, D2["l5"], D3["l5"], (23 / 2, 23 * 2)),
         ("첫 BL 저전위 구간 손실 [mV]", P.FBE_FIRST[2], D2["first"], D3["first"], (P.FBE_FIRST[2] / 2, P.FBE_FIRST[2] * 2)), ("200 ns 손실 [mV]", P.FBE_200[2], D2["l200"], D3["l200"], (P.FBE_200[2] / 2, P.FBE_200[2] * 2))]
    fig, ax = plt.subplots(1, 4, figsize=(15.5, 5.6))
    for a, (name, pap, v2, v3, tol) in zip(ax, Q):
        a.axhspan(*tol, color="#e8f5e9", zorder=0)
        a.bar(0, pap, 0.62, fc="white", ec=PAP, hatch="//", lw=1.6, zorder=3); a.bar(1, v2, 0.62, color="#1976d2", zorder=3); a.bar(2, v3, 0.62, color="#2e7d32", zorder=3)
        for x, v in ((0, pap), (1, v2), (2, v3)): a.text(x, v * 1.02, f"{v:.0f}" if v > 100 else f"{v:.1f}", ha="center", va="bottom", fontsize=12, color=INK)
        a.set_xticks([0, 1, 2]); a.set_xticklabels(["논문", "2D\n(fin3)", "3D\n단위 셀"], fontsize=11.5); a.set_title(name, fontsize=13, fontweight="bold", color=INK); a.set_ylim(0, max(pap, v2, v3, tol[1]) * 1.18); a.grid(axis="y", alpha=0.25, zorder=0); clean(a)
    fig.suptitle("3D 확인 (Case 2): 3D 단위 셀에서도 네 값이 모두 허용치(초록 띠) 안이에요", fontsize=16, fontweight="bold", color=INK); fig.tight_layout()
    return save(fig, "gt2d_eliu1007_09_3d.png")

# ------------------------------------------------------------------ the text: short sentences, real terms, anchors to coursework
T1 = (["구성", "해머 직전의 정공 수 [개]", "Y–Y', 충돌 이온화 끔 [mV/사이클]", "Z–Z', 끔 [mV/사이클]", "Z–Z', 켬"], [
 ("논문 (본문의 임계 사이클 수에서 계산)", "–", "0.0535", "0.0100", "1.1 → 0.58 V (7펄스)"),
 ("이력 없음 (fin)", "0~37", "0.00144", "0.00144", "붕괴 없음"),
 ("16.2 µs 이력 (x1, x2)", "1319~1360", "0.00115", "0.00115", "붕괴 없음"),
 ("16.2 µs 이력 + 피해 WL 저항 200 kΩ (x3, x4)", "1319~1331", "0.00115", "첫 사이클에 0.098 mV, 그 뒤 0.0011", "붕괴 없음"),
 ("100 µs 이력 (x7)", "2758~2763", "0.00019", "0.00020", "붕괴 없음"),
 ("대조군: 공격 WL 0 V (x5, x6)", "위와 같음", "0.00115 / 0.00019", "0.00115 / 0.00020", "–"),
])
T2 = (["정공의 후보 출처", "저장 노드가 치르는 값", "논문 Fig. 7과 맞는지"], [
 ("피해 셀의 저장 노드 접합 (GIDL, 충돌 이온화)", "쌍의 전자가 노드로 들어감: 0.34 fC ÷ 1.8 fF = 190 mV", "아님: 논문의 노드는 펄스 1, 2 동안 평탄"),
 ("피해 셀 자신의 채널 전류에서 생긴 쌍", "채널 전류가 노드에서 나옴: 수백 mV", "아님: 같은 이유"),
 ("공격 셀에서 생겨 넘어온 정공", "0", "남는 후보"),
])
T3 = (["구성 (모두 Case 2, Z–Z', 충돌 이온화 켬)", "공격 사이클당 쌍 [개]", "피해 셀 몸체로 온 정공 [개/사이클]", "첫 펄스 동안 몸체 전위 변화 [mV]", "저장 노드 손실 [mV/사이클]"], [
 ("논문 Fig. 7", "–", "–", "665.1", "펄스당 30 → 120, 7펄스 뒤 0.58 V"),
 ("기본 구동력, BL 접촉은 기둥 축 (fin)", "60~71", "0.4", "0.0", "없음"),
 ("기본 구동력, BL 접촉이 정공을 받지 않음 (g2)", "60~71", "5", "0.1", "없음"),
 ("ElectricField, BL 접촉은 기둥 축 (g1)", "첫 사이클 10 004, 그 뒤 약 3900", "첫 사이클 77, 그 뒤 31", "27", "없음 (10사이클 완료)"),
 ("ElectricField, BL 접촉은 기둥 끝 (g9)", "9981, 그 뒤 약 3900", "680, 그 뒤 410~540", "157", "−0.3 / 1.1 / 2.5 / 4.2 / 6.2 / 7.6 / 8.2"),
 ("ElectricField, BL 접촉이 정공을 받지 않음 (g8)", "9507, 그 뒤 약 3800", "893, 그 뒤 625~730", "174", "0.5 / 4.1 / 7.0 / 10.1 / 11.2"),
 ("ElectricField, 기둥 끝, 커패시터 4.2 fF (g0)", "18 274, 그 뒤 약 4500", "1368, 그 뒤 490~740", "280", "0.9 / 3.0 / 3.1 / 3.3 / 3.1"),
])
T4 = (["비교", "논문", "2D 모델", "판정"], [
 ("충돌 이온화를 끄면 몸체가 충전되지 않음", "첫 펄스 2.4 mV", "0.0 mV (저항 200 kΩ을 넣으면 4.3 mV)", "같음"),
 ("켜면 첫 펄스 안에 충전됨, 노드는 그동안 그대로", "665.1 mV", "157~320 mV", "현상은 같음, 크기는 1/4~1/2"),
 ("노드는 공격 WL이 높은 구간에서 내려감", "그림에서 그렇게 보임 (낮은 구간은 평탄)", "기둥 끝 접촉, 사이클 7: 높은 구간 6.7 mV, 낮은 구간 1.5 mV", "경향이 같음"),
 ("몸체를 접지하면 노드가 지켜짐", "0.036 mV/사이클", "0.0080~0.0133 mV/사이클", "현상은 같음, 크기는 1/3~1/4"),
 ("Z–Z'의 노드가 7펄스 안에 0.58 V까지 내려감", "펄스당 30 → 120 mV", "사이클당 3~11 mV에서 느려짐", "안 맞음 (약 1/10)"),
 ("Y–Y'는 충돌 이온화에 반응하지 않음", "0.0535 mV/사이클 그대로", "사이클 3부터 0.17 → 3.75 mV/사이클", "안 맞음"),
])
T5 = (["충돌 이온화의 구동력, 저장 노드 용량", "12 ps [V]", "24 ps [V]", "39 ps [V]", "60 ps [V]", "논문과의 차이 [mV]"], [
 ("논문 Fig. 4(a) (그림에서 읽은 값)", "0.72", "0.92", "1.06", "1.13", "–"),
 ("기본값, 1.8 fF (fin3: 맞춘 값)", "0.743", "0.921", "1.025", "1.093", "+23 / +1 / −35 / −37"),
 ("기본값, 4.2 fF (본문의 값)", "0.512", "0.716", "0.859", "0.968", "−208 / −204 / −201 / −162"),
 ("ElectricField, 4.2 fF (본문의 값)", "0.785", "1.019", "1.104", "1.140", "+65 / +99 / +44 / +10"),
])
T6 = (["배치", "실행 수", "시작 전에 논문과 대조한 구조 (모두 PASS)", "다시 읽은 논문 부분", "끝난 상태"], [
 ("3D 확인", "2", "g3_c2h (3D 점검과 위에서 본 그림)", "VI절, Fig. 8", "완료"),
 ("라운드 15", "28", "gr_yy, gr_zz", "V절, Fig. 6(b), (c)", "완료"),
 ("라운드 16", "12", "gr_yy, gr_zz, gr_zzg", "V절, Fig. 6, Fig. 7", "9개 완료, 3개는 계산이 멈춰 중단"),
 ("라운드 17", "15", "gr_c1h ~ gr_c4h", "VI절, Fig. 8, Fig. 4(a)", "10개 완료, 5개는 계산이 멈춤"),
 ("라운드 18", "5", "gr_yy, gr_zz, gr_zzb, gr_zzbg (새 구조는 Fig. 2 옆에 그려서 대조)", "V절, Fig. 7", "1개 완료, 4개 중단"),
 ("라운드 19", "3", "gr_zz, gr_zzb", "V절, Fig. 7", "5~7사이클에서 중단 (사이클당 10분 이상)"),
 ("라운드 20", "7", "gr_c1h ~ gr_c4h", "III절, Fig. 4(a), Fig. 8", "완료"),
])
T7 = (["정할 것", "선택지", "권장"], [
 ("다음에 무엇을 역산할지", "(가) ElectricField와 기둥 끝 접촉으로 Fig. 5(c)·4(a)·8을 다시 맞추기 / (나) Y–Y'가 반응하지 않는 이유 / (다) 3D 쌍 구조에서 정공 이동 확인", "(가). 커패시터 값이 먼저 정해져야 나머지가 뜻을 가져요"),
 ("GitHub의 claude 브랜치를 main에 합칠지", "합침 / 그대로", "그대로. (가)가 끝난 뒤가 좋아요"),
])
SEC = [   # (label, heading, picture key, caption, sentences, table, numbered questions)
 ("한 줄로", "지금 어디까지 왔나요?", None, None,
  ["3번 실험을 끝냈어요.", "Fig. 8의 정공 전하를 만드는 이력을 로우 해머에 넣은 실험이에요.", "그 이력으로는 Fig. 6(e)도 Fig. 7도 나오지 않았어요.",
   "이어서 Fig. 7의 현상을 내는 후보 기구를 처음 찾았어요.", "공격 셀에서 생긴 정공이 BL 기둥을 지나 피해 셀 몸체로 넘어가는 것이에요.", "크기는 논문의 1/2~1/10이에요.", "Y–Y' 방향은 논문과 맞지 않아요.",
   "이 기구는 논문에 적힌 것이 아니에요.", "제가 역산한 후보예요.", "소자 구성 fin3와 그 점수는 그대로예요.", "fin3의 읽기는 3D 단위 셀에서도 확인됐어요."], None, None),
 ("기본부터", "이 보고서에 필요한 개념", "pair", "Z–Z' 쌍의 2D 단면. 위가 공격 셀, 아래가 피해 셀이에요. 파란 화살표가 정공이 가는 길이고, 굵은 선 두 개가 BL 접촉을 둘 수 있는 두 자리예요.",
  ["셀은 액세스 트랜지스터 1개와 커패시터 1개예요.", "이것을 1T1C라고 해요.", "저장 노드(SN)는 커패시터의 셀 쪽 전극이에요.", "SN 전압 1.1 V가 '1'이에요.",
   "비트라인(BL)은 수직 N+ 기둥이에요.", "위아래 층의 셀이 이 기둥을 같이 써요.", "워드라인(WL)은 게이트이고 몸체 위아래에 있어요.",
   "몸체는 채널이 생기는 p형 실리콘이에요.", "어디에도 접지되지 않아서 부유 몸체(floating body)라고 해요.", "정공이 들어오면 몸체 전위가 올라가요.", "body effect로 문턱 전압이 내려가요.", "그러면 SN의 전하가 새요.",
   "SN 전압이 변하는 속도는 I = C·dV/dt예요.", "회로이론의 커패시터 식 그대로예요.",
   "로우 해머는 이웃 셀의 WL을 반복해서 켤 때 생기는 손실이에요.", "켜는 셀이 공격 셀(aggressor)이에요.", "당하는 셀이 피해 셀(victim)이에요.",
   "Z–Z'는 위아래 층 이웃이에요.", "Y–Y'는 BL 기둥 건너편 이웃이에요.", "해머 동안 BL은 0.55 V이고 피해 셀의 WL은 0 V예요.",
   "충돌 이온화(impact ionization)는 전계에서 가속된 캐리어가 전자–정공 쌍을 만드는 현상이에요.", "pn 접합의 애벌랜치 항복과 같은 물리예요.",
   "TCAD는 이 현상을 계수 α로 계산해요.", "α에 넣는 전계의 종류가 구동력(driving force)이에요.", "Sentaurus의 기본값은 준페르미 전위의 기울기예요.",
   "선택지 ElectricField는 전계의 크기 전체를 써요.", "채널에서는 게이트의 수직 전계까지 들어가요.", "그래서 쌍이 훨씬 많이 생겨요.", "논문은 충돌 이온화 모델의 이름도 구동력도 적지 않았어요.",
   "그림의 두 몸체와 BL 기둥은 p – N+ – p 순서예요.", "전자회로에서 배운 pnp BJT와 같은 배치예요.", "한쪽 몸체의 정공이 N+를 건너 다른 몸체로 갈 수 있어요.",
   "역산은 논문이 비워 둔 것을 논문 그림에서 거꾸로 찾는 일이에요.", "역산한 것은 논문에 적힌 값과 무게가 달라요."], None, None),
 ("조금 더", "1. 3번 실험: 이력을 넣은 로우 해머 (라운드 15)", "hist", "사이클당 손실. 빗금 막대가 논문, 파랑이 공격 WL을 켠 실행, 회색이 공격 WL을 0 V로 둔 대조군이에요. 파랑과 회색의 높이가 같은지 보세요.",
  ["가설은 이랬어요.", "Fig. 8의 정공 약 1350개가 긴 유지 시간에 GIDL로 쌓였다는 것이에요.", "GIDL은 게이트와 드레인 사이 전계로 생기는 터널링 누설이에요.",
   "모델에서는 BL이 높은 채 16.2 µs를 두면 그만큼 쌓여요.", "이 이력이 사실이라면 Fig. 6(e)와 Fig. 7에도 흔적이 있어야 해요.", "같은 Case 2 셀을 쓰는 그림이기 때문이에요.",
   "그래서 몸체를 그렇게 채운 뒤 논문의 해머를 걸었어요.", "채우는 동안 저장 노드는 1.1 V에 잡아 뒀어요.", "유지 시간은 16.2 µs와 100 µs 두 가지예요.",
   "대조군도 같이 돌렸어요.", "대조군은 공격 WL을 0 V로 둔 실행이에요.", "가만히 있어도 잃는 양을 재요.", "실행 28개가 모두 끝났어요.",
   "결과: 이력이 있어도 손실은 대조군과 같아요.", "공격 − 대조는 0.0000 mV/사이클이에요.", "남는 0.00115 mV/사이클을 전류로 바꿔 볼게요.",
   "I = C·dV/dt = 1.8 fF × 0.00115 mV ÷ 0.188 ns = 11 pA예요.", "저장 노드 접합의 GIDL 누설이에요.", "공격 셀과 무관해요.", "몸체가 더 차면 이 누설도 줄어요.",
   "Z–Z'에서 충돌 이온화를 켜도 붕괴가 없어요.", "이유는 BL 전압이에요.", "Fig. 8의 손실은 BL이 0 V일 때 생겨요.", "해머에서는 BL이 0.55 V예요.", "BL 쪽 장벽이 0.55 V 더 높아요.",
   "subthreshold 전류는 60 mV마다 10배씩 줄어요.", "0.55 V면 9자리 작아져요.",
   "판정: 출처 가설은 Fig. 8과 독립인 그림의 뒷받침을 얻지 못했어요.", "반박된 것도 아니에요.", "그렇게 충전된 몸체는 해머에서 흔적을 남기지 않기 때문이에요."], T1, None),
 ("조금 더", "2. 논문 Fig. 7을 다시 읽었어요 (제 읽기를 고침)", "paper7", "논문 Fig. 7(a), (c)의 값을 다시 그린 것. 점선 두 개가 t = 0과 t_A예요. 노드가 어느 구간에서 내려가는지 보세요.",
  ["Fig. 7(c)에는 화살표 두 개가 있어요.", "t = 0과 t = t_A예요.", "전에는 t_A를 0.45 ns로 읽었어요.", "틀린 읽기였어요.",
   "그림을 4배로 키워 화살표 끝을 다시 봤어요.", "두 화살표는 첫 번째 공격 펄스의 시작과 끝을 가리켜요.", "t_A는 약 0.09 ns예요.",
   "Fig. 7(e)는 그 사이의 몸체 전위 변화예요.", "충돌 이온화를 끄면 2.4 mV예요.", "켜면 665.1 mV예요.", "몸체를 접지하면 1.8 mV예요.",
   "즉 665 mV는 펄스 하나, 94 ps 동안 생겨요.", "그동안 저장 노드는 1.1 V 그대로예요.", "노드는 약 0.3 ns부터 내려가요.", "공격 WL이 1.8 V인 구간에서만 내려가요.", "0.58 V에서 멈춰요.",
   "665 mV를 정공 수로 바꿔 볼게요.", "이 모델에서 정공 1개는 몸체 전위를 0.26~0.31 mV 올려요.", "그러면 약 2100~2600개예요.",
   "전하는 Q = 2100 × 1.6×10⁻¹⁹ C = 0.34 fC 이상이에요.", "94 ps에 들어오려면 I = Q/t = 3.6 µA가 필요해요.",
   "이 정공이 피해 셀의 저장 노드 접합에서 생겼다면 어떨까요?", "쌍의 전자가 저장 노드로 들어가요.", "ΔV = Q/C = 0.34 fC ÷ 1.8 fF = 190 mV가 빠져야 해요.", "논문의 노드는 평탄해요.",
   "그래서 정공은 피해 셀 밖에서 와야 해요.", "남는 후보는 공격 셀이에요.", "켜진 공격 셀만 µA 전류를 흘려요."], T2, None),
 ("조금 더", "3. 후보 기구: 공격 셀의 정공이 BL 기둥을 지나 넘어와요 (라운드 16, 18, 19)", "body", "피해 셀 몸체 전위의 변화. 마름모가 논문의 값(첫 펄스 뒤 665.1 mV)이에요. 첫 번째 띠(첫 펄스) 안에서 각 선이 얼마나 오르는지 보세요.",
  ["먼저 지금까지의 모델에서 세어 봤어요.", "공격 셀은 사이클마다 60~71쌍을 만들어요.", "피해 셀 몸체에 닿는 정공은 0.4개예요.", "논문에 필요한 양의 1/5000이에요.",
   "그래서 논문이 정하지 않은 두 가지를 바꿨어요.", "첫째는 충돌 이온화의 구동력이에요.", "ElectricField로 바꿨어요.", "계수는 Sentaurus 기본값 그대로예요.",
   "둘째는 BL 접촉의 위치예요.", "접촉은 전압을 거는 금속 단자예요.", "N+ 안의 정공은 소수 캐리어예요.", "접촉에 닿으면 사라져요.",
   "지금까지의 2D 단면은 접촉을 기둥 축 전체에 뒀어요.", "접합에서 50 nm 거리예요.", "실제 기둥의 접촉은 기둥 끝에 있어요.",
   "그래서 접촉을 기둥 아래 끝으로 옮긴 구조를 만들었어요.", "이름은 gr_zzb예요.", "논문 Fig. 2 옆에 그려서 대조한 뒤에 썼어요.",
   "결과를 볼게요.", "ElectricField에서는 쌍이 사이클당 약 3900개로 늘어요.", "첫 사이클은 약 10 000개예요.",
   "이유를 숫자로 볼게요.", "공격 셀의 저장 노드는 WL이 꺼질 때 0.32 V로 끌려 내려가요.", "켜지면 0.55 V로 다시 채워져요.",
   "Q = C·ΔV = 1.8 fF × 0.23 V = 0.41 fC예요.", "전자 약 2600개가 사이클마다 채널을 지나가요.", "전자 1개가 쌍 1.5개를 만드는 셈이에요.",
   "접촉이 기둥 축에 있으면 피해 셀에 31개가 와요.", "기둥 끝에 있으면 410~680개가 와요.", "접촉이 정공을 아예 받지 않으면 625~890개예요.",
   "접촉을 기둥 끝에 두기만 해도 그 2/3가 넘어가요.", "첫 펄스 동안 몸체 전위는 157 mV 올라요.", "커패시터를 본문의 4.2 fF로 하면 280 mV예요.", "논문은 665 mV예요.",
   "커패시터가 크면 첫 펄스에 공격 셀을 지나는 전하가 늘어요.", "그래서 첫 사이클의 쌍이 1.8배로 늘어요."], T3, None),
 ("조금 더", "4. 논문과 같은 점", "steps", "2D 모델의 저장 노드 전압 변화. 연한 띠가 공격 WL이 높은 구간이에요. 선이 띠 안에서 더 가파르게 내려가는지 보세요.",
  ["Fig. 7과 같은 점이 네 가지예요.", "첫째, 충돌 이온화를 끄면 몸체가 충전되지 않아요.", "둘째, 켜면 첫 공격 펄스 안에 충전돼요.", "그동안 노드는 1.1 V 근처예요.",
   "셋째, 노드는 주로 공격 WL이 높은 구간에서 내려가요.", "손실의 약 80 %가 그 구간에서 생겨요.", "낮은 구간에서는 처음에 조금 더 내려간 뒤 평평해져요.", "넷째, 몸체를 접지하면 노드가 지켜져요.",
   "접지한 몸체에는 정공이 4개뿐이에요.", "넘어온 정공이 몸체 접촉으로 빠져나가요.", "손실은 0.008~0.013 mV/사이클이에요.", "논문은 0.036 mV/사이클이에요.",
   "노드는 왜 주로 높은 구간에서 내려갈까요?", "그 구간에만 정공이 기둥으로 들어오기 때문이에요.", "정공이 오면 피해 셀의 몸체–BL 접합이 순방향이 돼요.",
   "BL에서 전자가 몸체로 주입돼요.", "그 전자가 저장 노드(1.1 V)로 끌려가요.", "BL – 몸체 – 저장 노드가 npn BJT로 동작하는 것이에요.",
   "저자들의 조사 논문도 이 기생 n-p-n BJT를 설명해요.", "Lee 외, IEEE TED 73(3), 2026의 Fig. 3과 II-B절이에요."], T4, None),
 ("조금 더", "5. 논문과 다른 점", "size", "저장 노드의 손실을 로그 축에 그린 것. 빨강(열린 동그라미)이 논문, 색 선이 2D 모델이에요. 같은 시각에 몇 배 차이인지 보세요. BL 접촉이 기둥 축인 실행은 손실이 없어서 그리지 않았어요.",
  ["다른 점은 세 가지예요.", "첫째는 크기예요.", "첫 펄스의 몸체 전위 변화가 논문의 1/4~1/2이에요.", "노드 손실은 사이클당 3~11 mV예요.", "논문은 펄스당 30~120 mV예요.", "약 1/10이에요.",
   "모델의 손실은 사이클이 갈수록 더디게 늘어요.", "4.2 fF에서는 약 3.2 mV/사이클에서 평평해져요.", "0.605 V ÷ 3.2 mV = 약 190사이클이에요.", "논문은 7펄스예요.",
   "그래도 충돌 이온화를 끈 경우보다는 2000배 나빠요.", "끈 경우는 0.00144 mV/사이클이에요.",
   "둘째는 Y–Y'예요.", "모델에서는 Y–Y'의 피해 셀에도 정공이 와요.", "사이클당 190~250개예요.", "사이클 3부터 노드가 내려가요.", "논문의 Y–Y'는 충돌 이온화를 켜도 그대로예요.",
   "두 셀이 같은 높이에서 기둥을 마주 보는데 왜 그런지는 아직 몰라요.",
   "셋째는 수치 문제예요.", "피해 셀 몸체에 정공이 약 3000개 쌓이면 계산이 멈춰요.", "시간 스텝이 10⁻¹⁶ s까지 줄어요.", "과도 해석은 시간을 작은 스텝으로 나눠 풀어요.",
   "스텝마다 Newton 반복으로 방정식을 맞춰요.", "반복이 수렴하지 않으면 스텝을 줄여요.", "여기서는 산화막 계면의 전자 밀도가 반복마다 진동했어요.",
   "수렴 기준을 풀면 지나가요.", "대신 사이클 하나에 10분 넘게 걸려요.", "그래서 마지막 세 실행은 5~7사이클에서 제가 멈췄어요.", "10사이클 전체는 아직 못 봤어요."], None, None),
 ("조금 더", "6. 쓰기 곡선이 같이 움직여요 (라운드 20)", "write", "쓰기 곡선. 열린 동그라미가 논문 Fig. 4(a), 선이 2D 모델이에요. 회색 선과 초록 선은 용량이 같고 구동력만 달라요.",
  ["ElectricField에서는 쓰기가 빨라져요.", "쓰는 동안 충돌 이온화의 정공이 몸체에 차요.", "body effect로 문턱 전압이 내려가요.", "그래서 전류가 늘어요.",
   "어제까지의 상황을 다시 볼게요.", "본문의 저장 노드 용량은 4.2 fF예요.", "기본 구동력에서는 4.2 fF가 너무 느렸어요.", "논문보다 160~208 mV 낮았어요.", "그래서 1.8 fF로 맞췄어요.",
   "ElectricField에서는 같은 4.2 fF가 조금 빨라요.", "논문보다 10~99 mV 높아요.", "허용치는 30 mV예요.", "두 경우 모두 허용치 밖이에요.",
   "뜻은 이래요.", "fin3의 1.8 fF와 구동력은 서로 묶여 있어요.", "하나를 바꾸면 다른 하나도 다시 정해야 해요.", "Fig. 4(a)만으로는 논문이 어느 쪽인지 가릴 수 없어요."], T5, None),
 ("조금 더", "7. Fig. 8의 정공 전하는 여전히 출처를 몰라요 (라운드 17, 20)", "holes", "몸체의 정공 수. 빗금 막대가 Fig. 8(a) 막대에 필요한 수예요. 색 막대가 빗금 막대와 같은 높이가 되는지 보세요.",
  ["같은 설정으로 Fig. 8도 돌려 봤어요.", "대리 생성은 쓰지 않았어요.", "쓰기의 충돌 이온화가 남기는 정공만 셌어요.",
   "ElectricField에서 쓰기는 약 6300쌍을 만들어요.", "기본 구동력에서는 150쌍이에요.", "대부분은 WL이 높은 동안 저장 노드 접촉으로 빠져요.",
   "남는 정공은 18~704개예요.", "필요한 양은 1118~1579개예요.", "Case 5는 18개뿐이에요.", "Case별 모양도 논문과 달라요.",
   "저장 노드 접촉도 정공을 받지 않게 해 봤어요.", "그러면 2300~5300개가 남아요.", "이번에는 너무 많아요.", "그 뒤에는 계산이 멈췄어요.",
   "논문 Fig. 2에서 저장 노드 전극은 N+ 소스 끝에 붙은 금속이에요.", "금속 접촉은 정공을 받아요.", "그래서 정공을 받는 쪽이 구조에 맞아요.",
   "판정: 쓰기의 충돌 이온화만으로는 Fig. 8의 전하가 나오지 않아요.", "정공 전하의 출처는 여전히 열려 있어요.", "fin3는 이 전하를 조건으로 둬요."], None, None),
 ("조금 더", "8. 3D 확인: fin3의 읽기는 3D에서도 성립해요", "d3", "Case 2의 네 값. 빗금이 논문, 파랑이 2D, 초록이 3D 단위 셀이에요. 초록 띠가 허용치예요.",
  ["어제 역산한 읽기를 다시 적을게요.", "Fig. 8(a)의 몸체 전위는 게이트 아래 몸체의 평균 전위예요.", "첫 BL 하강이 끝나고 0.25 ns 뒤에 읽어요.",
   "이 읽기가 2D 단면만의 것인지 3D에서 확인했어요.", "3D 단위 셀에 정공 1486개를 넣었어요.", "2D의 fin3는 1354개였어요.", "3D는 같은 전위에 정공이 약 10 % 더 들어요.",
   "결과: 막대 458 mV (논문 445 mV)예요.", "첫 구간 손실 27.5 mV (논문 29 mV)예요.", "200 ns 손실 59.4 mV (논문 50 mV)예요.", "모두 허용치 안이에요.",
   "허용치는 막대 30 mV, 손실 0.3 decade예요.", "0.3 decade는 2배 차이예요.", "3D로 본 것은 Case 2 하나예요."], None, None),
 ("조금 더", "9. 무엇을 확인하고 돌렸나", None, None,
  ["배치마다 시작 전에 구조를 논문과 대조했어요.", "치수, 도핑, 접합 위치를 메시에서 다시 읽는 검사예요.", "모든 줄이 PASS인 것을 읽고 시작했어요.",
   "새 구조 gr_zzb는 논문 Fig. 2 옆에 그려서 대조했어요.", "배치마다 Codex의 현황도 먼저 읽었어요.", "Codex는 Fig. 8의 FBE 조건 실험을 하고 있어요.", "겹치는 실행은 없었어요.",
   "배치는 시작 전에 실험 등록부에 적고 푸시했어요.", "멈춘 실행의 파일은 지우지 않았어요.", "지금 서버에 제 실행은 없어요.", "디스크는 9.2 GB 중 7.8 GB를 써요.",
   "ElectricField는 소자 구성에 넣지 않았어요.", "이 구동력으로 Fig. 5(c)와 Fig. 8을 다시 확인하지 않았기 때문이에요."], T6, None),
 ("그래서?", "이제 무엇을 정하면 될까요?", None, None,
  ["Fig. 7은 처음으로 현상이 나왔어요.", "크기와 Y–Y'는 아직 안 맞아요.", "Fig. 8의 정공 출처는 그대로 열려 있어요.", "새로 알게 된 것은 구동력이 여러 그림을 함께 움직인다는 점이에요.",
   "쓰기 곡선, 로우 해머, 정공 수가 모두 구동력에 묶여 있어요.", "그래서 다음은 (가)를 권해요.", "아래 표에서 정해 주세요.", "정해 주시면 바로 이어서 할게요."], T7,
  ["다음 역산은 (가), (나), (다) 중 무엇부터 할까요?", "GitHub의 claude 브랜치는 그대로 둘까요?"]),
]
RESULT = [   # figure, what is compared, paper, this model, configuration / run, kind of the model value
 ("Fig. 6(e) Y–Y'", "사이클당 저장 노드 손실, 충돌 이온화 끔", "0.0535 mV (본문의 11.3k 사이클에서 계산)", "0.00144 / 0.00115 / 0.00019 mV (이력 없음 / 16.2 µs / 100 µs)", "fin, x2, x7", "시뮬레이션"),
 ("Fig. 6(e) Z–Z'", "사이클당 저장 노드 손실, 충돌 이온화 끔", "0.0100 mV (60.5k 사이클에서 계산)", "0.00144 / 0.00115 / 0.00020 mV", "fin, x2, x7", "시뮬레이션"),
 ("Fig. 7(e)", "첫 공격 펄스 동안 몸체 전위 변화, 충돌 이온화 켬", "665.1 mV (그림에 적힌 값)", "0.0 / 27 / 157 / 174 / 280 / 320 mV", "fin, g1, g9, g8, g0, g6", "시뮬레이션 (g1 이후는 역산 후보)"),
 ("Fig. 7(e)", "같은 값, 충돌 이온화 끔 / 켬 + 몸체 접지", "2.4 / 1.8 mV", "0.0 / 0.8~1.1 mV", "fin, g7·g3의 접지 실행", "시뮬레이션"),
 ("Fig. 7(a) Z–Z'", "저장 노드, 충돌 이온화 켬", "펄스당 30 → 120 mV, 7펄스 뒤 0.58 V (그림에서 읽은 값)", "사이클당 8.2 / 11.2 / 3.1 mV에서 느려짐", "g9 (7사이클), g8 (5사이클), g0 (5사이클)", "시뮬레이션, 계산을 중간에 멈춤"),
 ("Fig. 7(d) 몸체 접지", "사이클당 손실, 충돌 이온화 켬", "0.036 mV (16.8k 사이클에서 계산)", "0.0080 / 0.0101 / 0.0133 mV (기본 구동력 0.00145)", "g7, g3, g4의 접지 실행", "시뮬레이션"),
 ("Fig. 7(d) Y–Y'", "사이클당 손실, 충돌 이온화 켬", "0.0535 mV (끈 경우와 같음)", "사이클 3부터 0.17 → 3.75 mV", "g1 (BL 접촉은 기둥 위 끝)", "시뮬레이션: 논문과 다름"),
 ("Fig. 4(a) 쓰기", "WL 상승 뒤 12 / 24 / 39 / 60 ps의 저장 노드 전압", "0.72 / 0.92 / 1.06 / 1.13 V (그림에서 읽은 값)", "0.743 / 0.921 / 1.025 / 1.093 V (기본, 1.8 fF), 0.785 / 1.019 / 1.104 / 1.140 V (ElectricField, 4.2 fF)", "fin3, o4", "시뮬레이션 (1.8 fF는 맞춘 값)"),
 ("Fig. 8(a)", "막대에 필요한 정공 수, Case 1~5", "막대 555 / 445 / 365 / 320 / 368 mV", "필요 1579 / 1354 / 1294 / 1118 / 1335개. 쓰기가 남긴 수 704 / 519 / 345 / 213 / 18개", "fin3, o1", "조건 / 시뮬레이션"),
 ("Fig. 8, Case 2, 3D", "막대 / 5 ns 뒤 / 첫 구간 / 200 ns 손실", "445 / 23 / 29 / 50 mV", "2D 445 / 13.9 / 23.2 / 67.8 mV, 3D 458 / 18.9 / 27.5 / 59.4 mV", "Ds2F_c2, E3S2_c2", "시뮬레이션 (정공 전하는 조건, 읽기는 역산)"),
]
TERM = [   # term, plain meaning (with the anchor), value and source in this work
 ("1T1C DRAM 셀", "트랜지스터 1개와 커패시터 1개로 1비트를 저장하는 셀", "수직 BL, 수평 WL 구조. 논문 Fig. 2"),
 ("저장 노드 (SN)", "커패시터의 셀 쪽 전극. 여기 전압이 데이터. Q = CV, I = C·dV/dt", "'1' = 1.1 V. 과도 해석 용량 1.8 fF (맞춘 값), 본문 4.2 fF"),
 ("비트라인 (BL), 워드라인 (WL)", "전하를 넣고 빼는 수직 N+ 기둥 / 액세스 트랜지스터의 게이트", "해머 동안 BL 0.55 V, 피해 셀 WL 0 V, 공격 셀 WL 0 ↔ 1.8 V"),
 ("부유 몸체 (floating body)", "접지 경로가 없는 p형 몸체. 정공이 들어오면 전위가 오르고 body effect로 V_th가 내려감", "Case 2: 두께 20 nm, 도핑 1×10<sup>18</sup> cm<sup>-3</sup>"),
 ("로우 해머, 공격 셀, 피해 셀", "이웃 셀(공격 셀)의 WL을 반복해서 켤 때 내 셀(피해 셀)의 SN 전하가 줄어드는 현상", "0.094 ns씩 켜고 끄기를 10사이클. 논문 Fig. 6(c)"),
 ("Y–Y', Z–Z'", "BL 기둥 건너편 이웃 / 위아래 층 이웃", "논문 0.0535 / 0.0100 mV per cycle (충돌 이온화 끔)"),
 ("이력, 대조군", "해머 전에 몸체를 채우는 유지 구간 / 공격 WL을 0 V로 둔 같은 실행", "16.2 µs, 100 µs. 라운드 15"),
 ("GIDL", "게이트와 드레인 사이 전계로 생기는 터널링 누설. 쌍의 전자는 저장 노드로, 정공은 몸체로 감", "유지 상태에서 11 pA (시뮬레이션). 계산 모델은 Hurkx (논문이 적은 이름)"),
 ("충돌 이온화", "전계에서 가속된 캐리어가 전자–정공 쌍을 만드는 현상. pn 접합의 애벌랜치 항복과 같은 물리", "논문은 Fig. 7에서 켰다고만 적음. 모델 이름과 계수는 없음"),
 ("구동력 (driving force), ElectricField", "충돌 이온화 계수 α에 넣는 전계의 종류. ElectricField는 전계의 크기 전체", "Sentaurus 기본값은 준페르미 전위의 기울기. ElectricField에서 쌍이 60배 이상"),
 ("pnp 배치", "공격 셀 몸체(p) – BL 기둥(N+) – 피해 셀 몸체(p). 정공이 N+를 소수 캐리어로 건너감", "역산한 후보 기구. 논문에 적힌 것이 아님"),
 ("기생 npn BJT", "BL(N+) – 몸체(p) – 저장 노드(N+). 몸체에 정공이 쌓이면 켜져서 SN이 BL 쪽으로 방전됨", "저자들의 조사 논문: Lee 외, IEEE TED 73(3), 2026, Fig. 3, II-B절"),
 ("BL 접촉", "BL에 전압을 거는 금속 단자. 소수 캐리어(정공)는 여기 닿으면 사라짐", "2D 단면은 기둥 축에 둠. 새 구조 gr_zzb는 기둥 아래 끝"),
 ("t_A (Fig. 7)", "논문이 몸체 전위 변화를 읽은 시각", "첫 번째 공격 펄스의 끝, 약 0.09 ns (그림에서 읽은 값. 전의 0.45 ns는 틀림)"),
 ("게이트 아래 몸체의 평균 전위", "어제 역산한 Fig. 8(a)의 읽기. 과도 해석 시작 기준", "첫 BL 하강이 끝나고 0.25 ns 뒤. 3D에서도 확인 (Case 2)"),
 ("fin3", "지금의 소자 구성 이름", "1.8 fF, Hurkx A 1.7×10<sup>21</sup>, 정공 1118~1579개 (조건), 기본 구동력"),
 ("역산", "논문이 비워 둔 것을 논문 그림에서 거꾸로 찾는 일", "저자에게 물을 수 없어서 쓰는 방법 (사용자 지시, 2026-10-07)"),
 ("과도 해석, 시간 스텝, Newton 반복, 수렴", "시간을 작은 스텝으로 나눠 풀고, 스텝마다 반복 계산으로 방정식을 맞추는 방법", "정공 약 3000개에서 스텝이 10<sup>-16</sup> s로 줄어 멈춤. 수렴 기준 ErrRef(Electron) 10<sup>17</sup>이면 지나감"),
 ("허용치", "논문 그림을 읽는 오차의 한계로 둔 값", "쓰기 30 mV, 몸체 전위 30 mV, 손실 0.3 decade (2배)"),
 ("fC, aC", "전하의 단위. 1 fC = 10<sup>-15</sup> C", "전자 1개 = 0.16 aC. 정공 2100개 = 0.34 fC"),
]

def check(H, F, D2, D3):      # the numbers typed into the text against the run files
    near = lambda a, b, tol: abs(a - b) <= tol
    c = [near(last5("Dx2Ry_yy"), 0.00115, 2e-5), near(last5("Dx5Ry_yy"), 0.00115, 2e-5), near(last5("Dx7Ry_yy"), 0.00019, 2e-5), near(last5("DfinRy_yy"), 0.00144, 2e-5),
         near(H["Dg9Rzbi_zz"]["pulse"], 157, 2), near(H["Dg8Rzi_zz"]["pulse"], 174, 2), near(H["Dg0Rzbi_zz"]["pulse"], 280, 2), near(H["Dg1Rzi_zz"]["pulse"], 27, 1),
         [round(x, 1) for x in H["Dg9Rzbi_zz"]["cyc"]] == [-0.3, 1.1, 2.5, 4.2, 6.2, 7.6, 8.2], [round(x, 1) for x in H["Dg0Rzbi_zz"]["cyc"]] == [0.9, 3.0, 3.1, 3.3, 3.1],
         [round(x, 1) for x in H["Dg8Rzi_zz"]["cyc"]] == [0.5, 4.1, 7.0, 10.1, 11.2], near(H["Dg1Ryi_yy"]["cyc"][-1], 3.75, 0.01), near((H["Dg9Rzbi_zz"]["sn"][48] - H["Dg9Rzbi_zz"]["sn"][52]) * 1e3, 6.7, 0.05), near((H["Dg9Rzbi_zz"]["sn"][52] - H["Dg9Rzbi_zz"]["sn"][56]) * 1e3, 1.5, 0.05), near(H["Dg1Ryi_yy"]["cyc"][2], 0.17, 0.01),
         [round(F["Do1F"][k]["holes"]) for k in range(1, 6)] == [704, 519, 345, 213, 18], [round(F["Ds2F"][k]["holes"]) for k in range(1, 6)] == [1579, 1354, 1294, 1118, 1335],
         near(D3["avg"], 458, 1), near(D3["first"], 27.55, 0.03), near(D3["l200"], 59.4, 0.1), near(D2["first"], 23.2, 0.1), round(D3["holes"]) == 1486]
    w = {r: [round(at(*write(r), x), 3) for x in (12, 24, 39, 60)] for r in ("DfinW_c2", "Db0W_c2", "Do4W_c2")}
    c += [w["DfinW_c2"] == [0.743, 0.921, 1.025, 1.093], w["Db0W_c2"] == [0.512, 0.716, 0.859, 0.968], w["Do4W_c2"] == [0.785, 1.019, 1.104, 1.140]]
    assert all(c), [i for i, x in enumerate(c) if not x]
    return len(c)

if __name__ == "__main__":
    M.SEC, M.RESULT, M.TERM = SEC, RESULT, TERM
    M.TXT = dict(title="Cho 외 (IRPS 2026) 소자 재현: 2026-10-07 오후 현황 (로우 해머 역산)", meta="2026년 10월 7일 16:30 · 2D 단면 모델과 3D 단위 셀 확인 · 라운드 15~20",
                 res_head="숫자 한눈에: 논문과 이 모델", res_note="마지막 두 열을 꼭 봐 주세요. 어느 구성의 값인지와, 값의 종류예요. 구성 이름은 본문의 표에 있어요.",
                 res_cols=["논문 그림", "비교한 값", "논문", "이 모델", "구성·실행", "모델 값의 종류"],
                 term_note="실험별 내용은 같은 폴더의 <b>GT_IRPS2026_2D_소자완성_보고_2026-10-06.md</b> 9.13~9.16절과 GitHub <b>claude</b> 브랜치의 <b>claude/ANALYSIS.md</b> 4.9절, 5.4~5.7절, 7.2절에 있어요.")
    n, avg = M.check_text()
    H = {r: hammer(r) for r in [x[0] for x in SET] + ["Dg1Ryi_yy"]}
    F = {tag: {c: fbe(f"{tag}_c{c}") for c in range(1, 6)} for tag in ("Ds2F", "Do1F", "Do4F", "Do2F")}; D2, D3 = fbe("Ds2F_c2"), fbe("E3S2_c2")
    k = check(H, F, D2, D3)
    img = dict(pair=fig_pair(), hist=fig_hist(), paper7=fig_paper7(), body=fig_body(H), steps=fig_steps(H), size=fig_size(H), write=fig_write(), holes=fig_holes(F), d3=fig_3d(D2, D3))
    open(OUT, "w", encoding="utf-8", newline="\n").write(M.html(img))
    print(f"text: {n} sentences, {avg:.1f} units per sentence, no analogy word; {k} numbers of the text checked against the run files"); print("\n".join(img.values())); print(OUT, os.path.getsize(OUT) // 1024, "kB")
