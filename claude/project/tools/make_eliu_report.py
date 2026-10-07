# make_eliu_report.py - status report of the evening of 2026-10-06 written with the user's skill eliU (reader: an EE junior;
# simple structure and short sentences, the real terms, every new idea tied to something from the coursework, every number
# with unit and source). Sections: 한 줄로 -> 기본부터 -> 조금 더 -> 그래서?, then the numbers in one table and a glossary.
# Draws gt2d_eliu_01 .. 06 into Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram and writes one HTML file with the pictures embedded
# into ...\results_vbl_hwl_1t1c_3ddram. Run on the PC: python tools/make_eliu_report.py
# Data: the run files of the shared working copy (C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs); numbers NOTES (bb), (bc).
# No picture of the paper is used: the paper's values are numbers read off its figures (tools/paper_targets.py).
import sys, os, glob, base64, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gt_tran import load, at, edges, PAPER_FBE
import paper_targets as P
import make_eli5_report as E                      # the cell drawing and the colours of the earlier report
RUNS = r"C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs"
BASE = r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프"
PIC = os.path.join(BASE, "pic_vbl_hwl_1t1c_3ddram"); OUT = os.path.join(BASE, "results_vbl_hwl_1t1c_3ddram", "GT_IRPS2026_현황보고_eliU_2026-10-06_저녁.html")
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
GREEN, YELLOW, RED, GREY, ORANGE, INK = E.GREEN, E.YELLOW, E.RED, E.GREY, E.ORANGE, E.INK
COL = E.COL

def save(fig, name):
    f = os.path.join(PIC, name); fig.savefig(f, dpi=130, bbox_inches="tight", facecolor="white"); plt.close(fig); return f

def sysf(rid): return load(os.path.join(RUNS, rid, rid + "_sys.plt"))
def key(s, n): return next(x for x in s if n in x)
def clean(ax):
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)

def fbe(tag, c):          # one FBE run: time [ns] from the charged node, storage node [V], BL-low phases
    rid = f"D{tag}F_c{c}"; s = sysf(rid); t = s["time"]; sn, bl, wl = s[key(s, "nSN)")], s[key(s, "nBL")], s[key(s, "nWL)")]
    t0 = edges(t, wl, 0, 1.8, False)[0] + 4e-11; f = edges(t, bl, 0, 1.1, False); r = [x for x in edges(t, bl, 0, 1.1, True) if x > f[0]]
    i = [j for j, x in enumerate(t) if x >= t0]
    return dict(t=[(t[j] - t0) * 1e9 for j in i], sn=[sn[j] for j in i], lo=[((a - t0) * 1e9, (b - t0) * 1e9) for a, b in zip(f, r)])

def fig_cell():
    fig, ax = plt.subplots(1, 2, figsize=(15, 5.4)); E.cell(ax[0], False); E.cell(ax[1], True); fig.tight_layout()
    return save(fig, "gt2d_eliu_01_cell.png")

SCORE = [("Id–Vg (Fig. 5(c))", 0.79, 0.73, None), ("쓰기 (Fig. 4(a))", 6.49, 0.93, None), ("몸체 전위 상승 (Fig. 8(a))", 11.97, 0.12, 2.03),
         ("FBE: 첫 BL 저전위 구간 손실 (Fig. 8(b), (c))", 6.62, 2.97, 0.84), ("FBE: 200 ns 손실 (Fig. 8(b), (c))", 5.14, 1.44, 0.51),
         ("로우 해머 (Fig. 6(e))", 4.71, 4.39, None), ("로우 해머 + 충돌 이온화 (Fig. 7)", 11.88, 11.88, None)]
def fig_score():
    fig, ax = plt.subplots(figsize=(14, 6.4)); n = len(SCORE); box = dict(fc="white", ec="none", pad=1.5)
    for i, (name, a, b, c) in enumerate(SCORE):
        y = n - 1 - i; col = GREEN if b < 1 else YELLOW if b < 3 else RED
        ax.barh(y + 0.19, a, 0.34, color=GREY, zorder=3); ax.barh(y - 0.19, b, 0.34, color=col, zorder=3)
        ax.text(a * 1.07, y + 0.19, f"{a:g}", va="center", fontsize=11, color="#546e7a", bbox=box, zorder=5)
        ax.text(b * 1.07, y - 0.19, f"{b:g}", va="center", fontsize=12.5, fontweight="bold", color=INK, bbox=box, zorder=5)
        if c: ax.plot([c], [y - 0.19], marker="D", ms=10, mfc="white", mec="#6a1b9a", mew=2, zorder=6)
    ax.set_xscale("log"); ax.set_xlim(0.08, 60); ax.set_yticks(range(n)); ax.set_yticklabels([s[0] for s in SCORE][::-1], fontsize=12.5)
    ax.axvline(1.0, color="#2e7d32", ls="--", lw=2, zorder=4)
    ax.text(0.93, n - 0.35, "점수 1 = 그림 판독 오차의 한계\n(이 선보다 왼쪽이면 재현)", ha="right", va="bottom", fontsize=11.5, color="#2e7d32")
    ax.set_xticks([0.1, 0.5, 1, 2, 5, 10, 20]); ax.set_xticklabels(["0.1", "0.5", "1", "2", "5", "10", "20"], fontsize=11); ax.minorticks_off()
    ax.set_xlabel("점수 = (시뮬레이션 − 논문) ÷ 허용오차의 제곱평균제곱근 (작을수록 좋음)", fontsize=12.5); ax.set_ylim(-0.7, n + 0.35); ax.grid(axis="x", alpha=0.25, zorder=0)
    ax.barh([-5], [1], color=GREY, label="오늘 아침 기준선 (b0)"); ax.barh([-5], [1], color=GREEN, label="최종 구성 fin2: 1 미만")
    ax.barh([-5], [1], color=YELLOW, label="최종 구성 fin2: 1~3"); ax.barh([-5], [1], color=RED, label="최종 구성 fin2: 3 이상")
    ax.plot([], [], marker="D", ms=9, mfc="white", mec="#6a1b9a", mew=2, ls="none", label="참고: 정공 전하 1.25배 (fin)")
    ax.legend(loc="upper right", fontsize=11, frameon=True); ax.set_title("점수판: 논문 그림별로 얼마나 가까운가 (최종 2D 구성 fin2)", fontsize=17, fontweight="bold", color=INK, pad=12); clean(ax)
    return save(fig, "gt2d_eliu_02_score.png")

def fig_loss(R1):
    name = {1: "Case 1 (30 nm)", 2: "Case 2 (20 nm)", 3: "Case 3 (10 nm, 1e18)", 4: "Case 4 (10 nm, 1e16)", 5: "Case 5 (1e16, WF 5.0)"}
    fig, ax = plt.subplots(1, 2, figsize=(15.5, 5.9))
    for a, cs, ylim, ttl in ((ax[0], (1, 2, 3), (0.985, 1.106), "Fig. 8(b): 몸체 두께 30 / 20 / 10 nm"), (ax[1], (3, 4, 5), (1.080, 1.1012), "Fig. 8(c) 확대: 도핑과 일함수")):
        for lo, hi in R1[1]["lo"]: a.axvspan(lo, hi, color="#e1f5fe", zorder=0)
        for c in cs:
            r = R1[c]; a.plot(r["t"], r["sn"], color=COL[c], lw=2.2, label=f"2D 모델 fin2, {name[c]}", zorder=3)
            ends = [hi for _, hi in r["lo"]]
            pts = list(zip(ends, PAPER_FBE[c][0])) if c in PAPER_FBE and PAPER_FBE[c][0] else [(ends[0], P.FBE_FIRST[c])]
            pts.append((200.0, P.FBE_200[c]))
            a.plot([p for p, _ in pts], [1.1 - v * 1e-3 for _, v in pts], "o", mfc="white", color=COL[c], ms=8, mew=2, zorder=4, label=f"논문, Case {c} (그림에서 읽음)")
        a.set_xlim(0, 206); a.set_ylim(*ylim); a.set_xlabel("시간 [ns] (0 = 저장 노드 충전 직후)", fontsize=13); a.set_ylabel("저장 노드 전압 [V]", fontsize=13)
        a.set_title(ttl, fontsize=15, fontweight="bold", color=INK); a.grid(alpha=0.25); a.legend(fontsize=10, loc="lower left"); clean(a)
    ax[0].text(165, 1.0695, "하늘색 띠 = BL이 0 V인 구간\n(21 ns 주기, 9회)", ha="center", fontsize=11.5, color="#0277bd", bbox=dict(fc="white", ec="#b3e5fc", pad=4))
    fig.suptitle("FBE: 저장 노드 전압 (선 = 2D 모델, 정공 약 1050개 조건 / 동그라미 = 논문)", fontsize=17, fontweight="bold", color=INK); fig.tight_layout()
    return save(fig, "gt2d_eliu_03_fbe_loss.png")

def cycles(rid):          # storage-node change [mV] 20 ps before every aggressor rise, counted from before the first pulse
    s = sysf(rid); t = s["time"]; sn = s[key(s, "nSN)")]; wa = s[key(s, "nWLa")]; wf = edges(t, s[key(s, "nWL)")], 0, 1.8, False)
    r = [x for x in edges(t, wa, 0, 1.8, True) if not wf or x > wf[-1]]; per = r[1] - r[0]
    v = [at(t, sn, x - 2e-11) for x in r] + [at(t, sn, r[-1] + per - 2e-11)]
    return [(y - v[0]) * 1e3 for y in v]

def fig_r():
    fig, ax = plt.subplots(1, 2, figsize=(15.5, 5.9))
    for rid, lab, col, node in (("DfinW_c2", "2D 모델, 이상적 WL: 저장 노드", "#1976d2", "nSN)"), ("DraW_c2", "2D 모델, WL 저항 200 kΩ: 저장 노드", "#d32f2f", "nSN)"),
                                ("DraW_c2", "WL 저항 200 kΩ: victim 게이트 노드", "#78909c", "nGv")):
        s = sysf(rid); t = s["time"]; t0 = edges(t, s[key(s, "nWL)")], 0, 1.8, True)[0]
        ax[0].plot([(x - t0) * 1e12 for x in t], s[key(s, node)], color=col, lw=2.4, ls="--" if node == "nGv" else "-", label=lab, zorder=3)
    ax[0].plot(list(P.WRITE), list(P.WRITE.values()), "o", mfc="white", color=INK, ms=9, mew=2, zorder=5, label="논문 Fig. 4(a) 저장 노드 (그림에서 읽음)")
    ax[0].set_xlim(-5, 105); ax[0].set_ylim(0, 1.95); ax[0].set_xlabel("WL 상승 뒤 시간 [ps]", fontsize=13); ax[0].set_ylabel("전압 [V]", fontsize=13)
    ax[0].set_title("쓰기: R이 있으면 게이트가 늦게 올라가요 (τ = RC)", fontsize=14.5, fontweight="bold", color=INK); ax[0].legend(fontsize=10.5, loc="lower right"); ax[0].grid(alpha=0.25); clean(ax[0])
    n = list(range(11))
    ax[1].plot(n, [-0.0100 * i for i in n], "--", color=INK, lw=2, label="논문 Fig. 6(e): 사이클마다 0.0100 mV씩 쌓이는 경우")
    for rid, lab, col in (("DfinRz_zz", "2D 모델, 이상적 WL (1.8 fF)", "#1976d2"), ("Dr2Rz_zz", "2D 모델, WL 저항 200 kΩ (4.2 fF)", "#d32f2f"), ("DtcRzg_zz", "2D 모델, 200 kΩ + 몸체 접지 (1.8 fF)", "#f57c00")):
        v = cycles(rid); ax[1].plot(range(len(v)), v, "-o", color=col, lw=2.2, ms=6, label=lab, zorder=3)
    ax[1].set_xlim(-0.3, 10.3); ax[1].set_ylim(-0.50, 0.08); ax[1].set_xlabel("aggressor 사이클 수", fontsize=13); ax[1].set_ylabel("저장 노드 전압 변화 [mV]", fontsize=13)
    ax[1].set_title("로우 해머 Z–Z': 첫 사이클에 한 번 내려가고 더 쌓이지 않아요", fontsize=14.5, fontweight="bold", color=INK); ax[1].legend(fontsize=10.5, loc="center right"); ax[1].grid(alpha=0.25); clean(ax[1])
    fig.tight_layout(); return save(fig, "gt2d_eliu_04_wl_resistor.png")

HOLES = {1: [103, 140, 165, 185, 207, 1462, None], 2: [35, 56, 75, 91, 119, 1334, 2349], 3: [9, 21, 36, 50, 114, 1302, 2199], 4: [2, 4, 10, 8, 14, 1320, 2185], 5: [1, 1, 2, 4, 7, 1969, None]}
def fig_ii():
    k = [1, 2, 3, 4, 5, 7, 10]; fig, ax = plt.subplots(figsize=(12.5, 6.0))
    ax.axhspan(962, 1138, color="#ffe0b2", alpha=0.8, zorder=1); ax.text(1.05, 1230, "Fig. 8(a) 막대에 해당하는 정공 수 (962~1138개)", fontsize=11.5, color="#e65100", va="bottom")
    for c in range(1, 6):
        xs = [a for a, b in zip(k, HOLES[c]) if b]; ys = [b for b in HOLES[c] if b]
        ax.plot(xs, ys, "-o", color=COL[c], lw=2.2, ms=7, label=E.CASE[c - 1].replace("\n", ", "), zorder=3)
    ax.axvspan(5, 7, color="#eceff1", zorder=0); ax.text(5.9, 2.2, "문턱\n(5배와 7배 사이)", ha="center", fontsize=12, color="#455a64")
    ax.set_yscale("log"); ax.set_ylim(0.7, 4000); ax.set_xlim(0.7, 10.6); ax.set_xticks(k); ax.set_xticklabels([f"{x}배" for x in k], fontsize=12)
    ax.set_xlabel("충돌 이온화 계수에 곱한 배수 (1배 = Sentaurus 기본값)", fontsize=13); ax.set_ylabel("WL이 꺼진 뒤 몸체에 남는 정공 수 [개]", fontsize=13)
    ax.set_title("충돌 이온화 계수를 키우면: 5배까지는 변화가 작고 7배에서 애벌랜치", fontsize=16, fontweight="bold", color=INK, pad=10)
    ax.legend(fontsize=10.5, loc="lower right"); ax.grid(alpha=0.25, which="both"); clean(ax)
    return save(fig, "gt2d_eliu_05_ii_factor.png")

def fig_gnd():
    fig, ax = plt.subplots(figsize=(12.5, 6.0))
    ax.axvspan(0.015, 1.02, color="#e8f5e9", zorder=0); ax.text(0.52, 1.36, "쓰기\n(WL 1.8 V, BL 1.168 V)", ha="center", fontsize=11.5, color="#2e7d32")
    ax.text(1.55, 1.36, "유지 (WL 0 V, BL 1.1 V)", ha="center", fontsize=11.5, color="#455a64"); ax.text(2.6, 1.36, "BL 0.55 V", ha="center", fontsize=11.5, color="#455a64")
    ax.axhline(1.1, color=INK, ls="--", lw=1.8, zorder=2); ax.text(2.98, 1.12, "논문 Fig. 7(c): 몸체 접지 셀이 유지하는 1.1 V", ha="right", va="bottom", fontsize=11.5, color=INK)
    for rid, lab, col in (("DtcRzg_zz", "기본 계수 (1배)", "#1976d2"), ("Dw5Rzg_zz", "계수 5배", "#f57c00"), ("Dw7Rzg_zz", "계수 7배", "#d32f2f")):
        s = sysf(rid); ax.plot([x * 1e9 for x in s["time"]], s[key(s, "nSN)")], color=col, lw=2.6, label=f"2D 모델, 몸체 접지, {lab}", zorder=3)
    ax.annotate("저장 노드를 1.1 V로\n설정 (10 ps)", xy=(1.03, 1.1), xytext=(1.25, 0.62), fontsize=11.5, color=INK, ha="left", arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
    ax.set_xlim(0, 3.0); ax.set_ylim(-0.45, 1.5); ax.set_xlabel("시간 [ns]", fontsize=13); ax.set_ylabel("저장 노드 전압 [V]", fontsize=13)
    ax.set_title("계수 5배 이상이면 몸체 접지 셀이 '1'을 유지하지 못해요 (접합 항복)", fontsize=16, fontweight="bold", color=INK, pad=10)
    ax.legend(fontsize=11.5, loc="center right"); ax.grid(alpha=0.25); clean(ax)
    return save(fig, "gt2d_eliu_06_grounded_body.png")

# ------------------------------------------------------------------ the text: short sentences, real terms, anchors to coursework
T1 = (["항목", "값", "값의 종류", "근거"], [
 ("치수, 도핑, 일함수", "게이트 길이 100 nm, 게이트 산화막 5 nm, 게이트 두께 20 nm, 수직 격리 30 nm, 몸체 30 / 20 / 10 nm, 도핑 1×10<sup>18</sup> / 1×10<sup>16</sup>, 일함수 4.7 / 5.0 eV", "논문에 적힌 값", "Fig. 5(a), (b)"),
 ("전압", "Vdd 1.1 V, Vpp 1.8 V, 로우 해머 때 BL 0.55 V", "논문에 적힌 값", "본문, Fig. 4"),
 ("쓰기 BL 전압, FBE 타이밍", "1.168 V. 첫 BL 하강 21.0 ns, 주기 21.0 ns, 9회", "그림에서 읽은 값", "Fig. 4(a), Fig. 8(b)"),
 ("게이트 절연막", "HfO2 5 nm", "맞춘 값", "Fig. 5(c)의 문턱"),
 ("과도 해석의 저장 노드 용량", "1.8 fF (본문은 4.2 fF)", "맞춘 값", "Fig. 4(a)의 쓰기 속도. 4.2 fF × 0.72 V ÷ 12 ps = 252 µA가 필요한데 Fig. 5(c)의 최대 전류가 229 µA"),
 ("Hurkx 계수 A", "1.7×10<sup>21</sup> (기본 3.5×10<sup>21</sup>)", "맞춘 값", "Fig. 5(c)의 GIDL"),
 ("t_A의 몸체 정공 전하", "약 1050개 = 0.17 fC", "조건 (사용자 결정)", "Fig. 8(a) 막대. 1050 × 1.6×10<sup>-19</sup> C"),
 ("WL", "이상적 (저항 없음)", "결정", "아래 4번"),
 ("스페이서, 소자 폭", "Si3N4 25 nm, 폭 0.1 µm", "가정", "Fig. 2의 그림 비율, 같은 연구 그룹의 논문"),
])
T7 = (["시험 (Case 2, 이상적 WL)", "결과 (10사이클)", "논문"], [
 ("기준: 몸체에 정공을 넣지 않음 (충돌 이온화 켬)", "Y–Y' 손실 0.00006, Z–Z' 손실 0.0013 mV/사이클", "Y–Y' 0.0535, Z–Z' 급락 (1.1 → 0.58 V)"),
 ("몸체에 정공 1056개 (Fig. 8(a)의 445 mV 수준, 충돌 이온화 켬)", "Y–Y' 노드가 사이클당 0.0026 mV 오름. Z–Z' 손실 0.00065 mV/사이클", "같음"),
 ("몸체에 정공 1970개 (Fig. 7(e)의 665 mV 수준, 충돌 이온화 켬)", "Y–Y' 오름 0.0049 mV. Z–Z' 손실 0.00005 mV/사이클", "같음"),
 ("Y–Y'에 BL 직렬 저항 10 kΩ (충돌 이온화 끔)", "0.00144 mV/사이클 (없을 때 0.00144)", "0.0535"),
 ("Y–Y'에 aggressor 저장 노드 1.1 V (충돌 이온화 끔)", "0.00144 mV/사이클", "0.0535"),
 ("Y–Y'에 WL 저항 200 kΩ (충돌 이온화 끔)", "0.00137 mV/사이클", "0.0535"),
])
T8 = (["바꾼 것 (Case 2)", "쓰기 12 ps의 저장 노드 [V]", "GIDL, log<sub>10</sub> I @ Vg −1 V", "FBE 첫 구간 손실 [mV]"], [
 ("기준: Si3N4 스페이서, BL 기둥 100 nm", "0.74", "−13.24", "2.16"),
 ("스페이서 SiO2", "0.72", "−13.37", "2.32"),
 ("스페이서 HfO2", "0.79", "−12.81", "1.84"),
 ("BL 기둥 50 nm", "0.74", "−13.27", "2.15"),
 ("이동도에 수직 전계 의존 추가", "수렴하지 않음", "−13.26", "수렴하지 않음"),
 ("논문", "0.72", "−13.2", "29"),
])
SEC = [   # (label, heading, picture key, caption, sentences, table, numbered questions)
 ("한 줄로", "지금 어디까지 왔나요?", None, None,
  ["사용자가 정한 대로 2D 소자 구성을 하나로 확정했어요.", "Id–Vg, 쓰기 곡선, 몸체 전위는 논문과 맞아요.", "FBE의 첫 구간 손실은 논문보다 3~20배 작아요.", "로우 해머는 재현되지 않았어요.",
   "WL 저항 200 kΩ과 충돌 이온화 계수 배수는 쓰지 않기로 했어요.", "둘 다 조사해서 근거를 찾았어요.", "남은 2D 단계의 실험은 모두 끝났어요."], None, None),
 ("기본부터", "이 보고서에 필요한 개념", "cell", "셀의 2D 단면을 단순하게 그린 것. 왼쪽은 유지 상태, 오른쪽은 몸체에 정공이 쌓인 뒤 BL이 0 V가 된 상태예요.",
  ["셀은 액세스 트랜지스터 1개와 커패시터 1개예요.", "이것을 1T1C라고 해요.", "저장 노드(SN)는 커패시터의 셀 쪽 전극이에요.", "SN 전압 1.1 V가 '1'이에요.",
   "비트라인(BL)은 전하를 넣고 빼는 수직 N+ 기둥이에요.", "워드라인(WL)은 게이트이고 몸체 위아래에 있어요.",
   "SN 전압이 변하는 속도는 I = C·dV/dt예요.", "회로이론의 커패시터 식 그대로예요.", "용량 1.8 fF에 1 nA가 흐르면 10 ns에 5.6 mV가 내려가요.",
   "몸체는 채널이 생기는 p형 실리콘이에요.", "어디에도 접지되지 않아서 부유 몸체(floating body)라고 해요.", "정공이 들어오면 빠져나갈 길이 없어요.", "그래서 몸체 전위가 올라가요.",
   "몸체 전위가 오르면 body effect 식의 V_SB가 음수가 돼요.", "그러면 문턱 전압 V_th가 내려가요.", "WL이 0 V여도 subthreshold 전류가 흘러요.", "SN 전하가 줄어요.", "이 현상이 부유 몸체 효과(FBE)예요.",
   "subthreshold 전류는 전위에 지수로 변해요.", "300 K에서 60 mV마다 10배예요.", "그래서 몸체 전위 60 mV 차이가 손실 10배 차이가 돼요.",
   "로우 해머는 이웃 셀의 WL을 반복해서 켤 때 생기는 손실이에요.", "켜는 셀이 aggressor, 당하는 셀이 victim이에요.", "Y–Y'은 BL 건너 이웃, Z–Z'은 위아래 층 이웃이에요.",
   "충돌 이온화(impact ionization)는 강한 전계에서 캐리어가 전자–정공 쌍을 만드는 현상이에요.", "만들어진 쌍이 또 쌍을 만들면 애벌랜치 항복이에요.", "pn 접합의 역방향 항복과 같은 현상이에요.",
   "점수는 시뮬레이션과 논문의 차이를 허용오차로 나눈 값이에요.", "1보다 작으면 그림을 읽는 오차 안이에요."], None, None),
 ("조금 더", "1. 사용자가 정한 것과 최종 구성 fin2", None, None,
  ["오후에 세 가지를 정해 주셨어요.", "첫째, 몸체 정공 전하는 조건으로 두고 Fig. 8(a) 막대에 맞춰요.", "둘째, WL 저항 200 kΩ은 문제가 없을 때만 써요.", "셋째, 3D는 다시 만들어 논문 그림과 대조해요.",
   "이 결정을 넣은 2D 구성의 이름이 fin2예요.", "새로 돌린 실행은 없어요.", "이미 끝난 실행 16개를 묶은 것이에요.", "3D는 다시 만들었고 논문 Fig. 2와의 대조를 통과했어요.", "3D 실행은 시작하지 않았어요.",
   "아래 표에서 값의 종류를 꼭 봐 주세요.", "논문에 적힌 값과 맞춘 값은 무게가 달라요."], T1, None),
 ("조금 더", "2. 점수판", "score", "논문 그림별 점수. 회색은 오늘 아침, 색 막대는 최종 구성 fin2, 마름모는 정공 전하를 1.25배로 했을 때예요.",
  ["Id–Vg는 0.73이고 쓰기는 0.93이에요.", "둘 다 1보다 작아요.", "몸체 전위 상승은 0.12예요.", "조건으로 맞춘 값이라 맞는 것이 당연해요.", "FBE 첫 구간 손실은 2.97이에요.", "200 ns 손실은 1.44예요.",
   "로우 해머는 4.39와 11.88이에요.", "아침과 거의 같아요.", "마름모는 정공 전하를 1.25배로 한 경우예요.", "손실은 맞지만 몸체 전위가 53~68 mV 높아져요.",
   "점수는 다섯 Case의 평균이에요.", "평균이 Case별 차이를 가릴 수 있어요.", "그래서 아래에 Case별 값도 적었어요."], None, None),
 ("조금 더", "3. FBE: 몸체 전위는 맞고 손실은 작아요", "loss", "저장 노드 전압 대 시간. 선은 2D 모델(정공 약 1050개 조건), 동그라미는 논문 그림에서 읽은 값이에요.",
  ["BL을 1.1 V와 0 V 사이에서 아홉 번 오르내렸어요.", "BL이 0 V인 구간마다 SN 전압이 내려가요.", "Case 순서는 논문과 같아요.", "Case 5의 손실이 거의 0인 것도 같아요.",
   "그런데 첫 구간 손실의 크기가 달라요.", "모델은 2.6 / 2.2 / 1.1 / 1.1 / 0.13 mV예요.", "논문은 55 / 29 / 7.1 / 3.5 / 0 mV예요.",
   "I = C·dV/dt로 전류로 바꿔 볼게요.", "Case 2는 모델 0.4 nA, 논문 5 nA예요.", "전류로 13배 차이예요.", "60 mV마다 10배이니 전위로는 약 70 mV예요.", "모델의 장벽이 70 mV쯤 높은 셈이에요.",
   "정공 전하를 1.25배로 하면 손실이 맞아요.", "대신 몸체 전위가 논문 막대보다 높아져요.", "두 그림을 한 전하로 함께 맞추지는 못했어요.",
   "정공은 몸체에 전자–정공 쌍을 만들어서 넣어요.", "그동안 SN은 1.1 V에 붙잡아 둬요.", "붙잡지 않으면 SN이 31~38 mV 내려가요.", "이 값은 Codex의 실험에서 나왔어요.",
   "그래서 이 조건은 정공이 생긴 과정을 재현한 것이 아니에요.", "첫 BL 하강 직전의 상태만 맞춘 것이에요."], None, None),
 ("조금 더", "4. WL 저항 200 kΩ: 쓰지 않는 이유", "r", "왼쪽: 쓰기 곡선. 오른쪽: 로우 해머 Z–Z'에서 사이클마다의 저장 노드 변화. 점선과 동그라미가 논문이에요.",
  ["논문 Fig. 7(b)에는 저항 R이 그려져 있어요.", "victim 게이트와 WL 전원 사이예요.", "값은 적혀 있지 않아요.", "200 kΩ은 Fig. 6(e)의 Z–Z' 값에 맞춘 값이었어요.", "조사해 보니 문제가 네 가지예요.",
   "첫째, 쓰기가 느려져요.", "게이트 노드가 30 ps에 63 %까지 올라가요.", "RC 회로의 시상수 τ = RC가 약 30 ps라는 뜻이에요.", "논문의 쓰기는 12 ps에 0.72 V예요.", "R이 있으면 12 ps에 0.07 V예요.", "쓰기 점수가 0.93에서 18.85가 돼요.",
   "둘째, 손실이 쌓이지 않아요.", "첫 사이클에 0.093 mV 내려가고 끝이에요.", "10사이클 뒤에도 0.093 mV예요.", "Codex의 50사이클 실험도 같았어요.", "논문은 임계 사이클 수를 0.605 V ÷ 0.0100 mV로 계산해요.", "즉 논문 값은 매 사이클 쌓이는 손실이에요.",
   "셋째, 4.2 fF에서만 맞아요.", "첫 사이클에 움직이는 전하가 0.39 aC로 일정해요.", "Q = C·ΔV이니 1.8 fF에서는 0.2 mV가 돼요.", "10사이클 평균이 논문의 2.2배가 돼요.",
   "넷째, Y–Y'은 R에 반응하지 않아요.", "그래서 200 kΩ은 소자에 넣지 않아요.", "R이 쓰기에도 있다면 τ가 수 ps여야 해요.", "그러면 R은 10 kΩ보다 작아야 하고 게이트가 튀지 않아요."], None, None),
 ("조금 더", "5. 정공은 어디서 올까: 충돌 이온화 계수를 키워 봤어요", "ii", "WL이 꺼진 뒤 몸체에 남는 정공 수. 주황 띠는 Fig. 8(a) 막대에 해당하는 수예요.",
  ["막대에 해당하는 정공 약 1050개가 어디서 오는지는 아직 몰라요.", "기본 계수로는 Case 2에서 35개가 남아요.", "WL을 0.01 ps 만에 꺼도 159개예요.", "그래서 진단으로 충돌 이온화 계수에 배수를 곱해 봤어요.",
   "이 배수는 문헌에서 온 값이 아니에요.", "5배까지는 변화가 작아요.", "7배에서 갑자기 1300개 넘게 남아요.", "WL이 꺼지는 순간 애벌랜치가 일어나기 때문이에요.",
   "몸체가 충전되면 전계가 줄어 애벌랜치가 멈춰요.", "그래서 두께와 도핑이 달라도 수가 비슷해요.", "Case 2, 3, 4가 1334 / 1302 / 1320개예요.", "이 성질은 Fig. 8(a)와 닮았어요.", "여기까지는 좋은 단서로 보였어요."], None, None),
 ("조금 더", "6. 그런데 이 배수는 논문과 맞지 않아요", "gnd", "몸체를 접지한 셀의 저장 노드 전압. 파랑은 기본 계수, 주황과 빨강은 5배와 7배예요.",
  ["같은 배수를 몸체 접지 셀에 넣어 봤어요.", "논문 Fig. 7(c)가 그 경우를 보여 주기 때문이에요.", "논문의 접지 셀은 충돌 이온화를 켜도 1.1 V를 유지해요.", "손실은 사이클당 0.036 mV뿐이에요.",
   "모델은 5배에서 SN이 0.10 V에 머물러요.", "7배에서는 −0.27 V예요.", "'1'을 쓸 수도 유지할 수도 없어요.", "이유는 pn 접합의 항복이에요.",
   "부유 몸체는 정공이 쌓이면 전위가 올라 전계가 줄어요.", "그래서 애벌랜치가 스스로 멈춰요.", "접지 몸체는 0 V에 묶여 있어서 멈추지 않아요.", "N+/p 접합이 1.1 V에서 항복하는 셈이에요.",
   "그래서 5배 이상의 배수는 기각했어요.", "FBE에서도 결론이 같아요.", "7배에서 Case 1과 2는 1 ns 안에 0.6 V가 빠져요.", "논문은 첫 구간 10 ns에 55 mV와 29 mV예요.",
   "정공의 출처는 여전히 재현되지 않았어요."], None, None),
 ("조금 더", "7. 로우 해머: 더 시험한 것", None, None,
  ["논문의 사이클당 손실은 Y–Y' 0.0535 mV, Z–Z' 0.0100 mV예요.", "모델은 둘 다 0.0014 mV예요.", "이 값은 정적 누설 수준이에요.", "여섯 가지를 더 시험했어요.", "어느 것도 값을 움직이지 않았어요.",
   "몸체를 논문 수준으로 충전해도 급락이 없어요.", "논문 Fig. 7(a)는 2 ns 안에 1.1 V에서 0.58 V로 내려가요."], T7, None),
 ("조금 더", "8. 가정 민감도", None, None,
  ["논문에 없어서 가정한 값 세 가지를 바꿔 봤어요.", "Case 2에서 한 가지씩 바꿨어요.", "좋아지는 점수가 없었어요.", "그래서 기본값을 유지해요.", "BL 기둥 폭은 결과에 영향이 없어요.", "3D 모델의 50 nm 기둥과 2D의 100 nm가 같은 결과라는 뜻이에요."], T8, None),
 ("조금 더", "9. 논문을 다시 읽어 확인한 것", None, None,
  ["논문 본문과 그림 원본을 다시 읽었어요.", "터널링 모델은 Hurkx라고 적혀 있어요.", "충돌 이온화는 모델 이름과 계수가 없어요.", "Fig. 7에서 켰다고만 적혀 있어요.", "Fig. 8에서 켰는지는 적혀 있지 않아요.",
   "Fig. 7(e)의 몸체 상승 665 mV는 해머 시작 뒤 0.45 ns 동안의 값이에요.", "즉 몸체는 해머 도중에 충전돼요.", "Fig. 7(a)는 aggressor 펄스마다 계단처럼 내려가요.",
   "Fig. 8은 손실을 body effect 식으로 설명해요.", "전자회로에서 배운 그 식이에요.", "이 내용은 저자에게 물을 항목의 근거가 돼요."], None, None),
 ("조금 더", "10. 서버 사고와 GitHub 공유", None, None,
  ["18:14에 서버 계정의 디스크 할당량 10 GB가 가득 찼어요.", "원인은 제 쪽이에요.", "실행 43개를 동시에 돌렸어요.", "실행마다 같은 로그를 두 번 쓰고 있었어요.", "제 실행 40여 개의 출력이 손상됐어요.", "필요한 것만 다시 돌렸어요.",
   "Codex 실행 두 개도 영향을 받았어요.", "CDR_id_i0_idle과 FS_c2_q1300이에요.", "Codex가 다시 돌려야 해요.", "로그를 압축해 사용량을 7.3 GB로 내렸어요.", "지운 파일은 없어요.", "시작 전에 할당량을 확인하는 검사를 넣었어요.",
   "GitHub 저장소의 claude 브랜치에 자료를 올렸어요.", "현황, 실험 등록부, 분석, 원시 자료예요.", "새 배치는 등록부에 먼저 적고 시작했어요.", "Codex가 하는 실험과 겹치는 실행은 멈췄어요."], None, None),
 ("그래서?", "이제 무엇을 정하면 될까요?", None, None,
  ["2D에서 움직일 수 있는 값은 모두 시험했어요.", "남은 불일치는 두 가지예요.", "FBE 첫 구간 손실의 크기와 로우 해머예요.", "다음 길은 세 가지예요.", "Codex의 생성 위치 실험, 3D에서의 FBE, 저자 확인이에요.", "아래 네 가지를 정해 주세요."], None,
  ["3D 실행(준비된 덱 7개)을 시작할까요?", "GitHub의 claude 브랜치를 main에 합칠까요?", "손상된 Codex 실행 2개의 재실행을 Codex에 전달할까요?",
   "저자에게 물을 항목(저장 노드 용량, R의 값, 충돌 이온화 모델, t = 0의 상태)을 문서로 정리할까요?"]),
]
RESULT = [   # figure, what is compared, paper, final 2D configuration fin2, score, kind of the model value
 ("Fig. 5(c) Id–Vg", "1×10<sup>-8</sup> A가 되는 Vg, Case 1~5", "0.47 / 0.44 / 0.42 / 0.39 / 0.65 V", "0.48 / 0.45 / 0.43 / 0.39 / 0.69 V", "0.73", "시뮬레이션"),
 ("Fig. 5(c) GIDL", "log<sub>10</sub> I @ Vg −1 V", "−13.5 / −13.2 / −13.1 / −13.2 / −12.85", "−13.49 / −13.24 / −13.17 / −13.43 / −12.83", "(위에 포함)", "시뮬레이션 (A를 맞춤)"),
 ("Fig. 4(a) 쓰기", "WL 상승 뒤 12 / 24 / 39 / 60 ps의 SN 전압 (Case 2)", "0.72 / 0.92 / 1.06 / 1.13 V", "0.74 / 0.92 / 1.02 / 1.09 V", "0.93", "시뮬레이션 (용량을 맞춤)"),
 ("Fig. 8(a)", "몸체 중심 전위 상승", "555 / 445 / 365 / 320 / 368 mV", "548 / 442 / 363 / 319 / 367 mV", "0.12", "조건으로 맞춤"),
 ("Fig. 8(b), (c) FBE", "첫 BL 저전위 구간의 SN 손실", "55 / 29 / 7.1 / 3.5 / 0 mV", "2.62 / 2.16 / 1.06 / 1.09 / 0.13 mV", "2.97", "시뮬레이션"),
 ("Fig. 8(b), (c) FBE", "200 ns의 SN 손실", "100 / 50 / 14.6 / 7 / 1 mV", "20.3 / 15.5 / 6.2 / 5.4 / 1.6 mV", "1.44", "시뮬레이션"),
 ("Fig. 6(e) 로우 해머", "사이클당 SN 손실, Y–Y' / Z–Z'", "0.0535 / 0.0100 mV", "0.0014 / 0.0014 mV", "4.39", "시뮬레이션"),
 ("Fig. 7 로우 해머 + 충돌 이온화", "Z–Z'의 SN 전압 / 몸체 접지 시 사이클당 손실", "1.1 → 0.58 V / 0.036 mV", "급락 없음 / 0.0015 mV", "11.88", "시뮬레이션"),
 ("(참고) 정공 전하 1.25배", "몸체 상승 / 첫 구간 손실 / 200 ns 손실", "위와 같음", "608 / 506 / 429 / 378 / 436 mV, 18.9 / 16.0 / 6.4 / 5.3 / 0.14 mV, 82 / 56 / 16.6 / 12.5 / 1.6 mV", "2.03 / 0.84 / 0.51", "시뮬레이션 (전하를 손실에 맞춤)"),
]
TERM = [   # term, plain meaning (with the anchor), value and source in this work
 ("1T1C DRAM 셀", "트랜지스터 1개와 커패시터 1개로 1비트를 저장하는 셀", "수직 BL, 수평 WL 구조. 논문 Fig. 2"),
 ("저장 노드 (SN)", "커패시터의 셀 쪽 전극. 여기 전압이 데이터. Q = CV", "'1' = 1.1 V. 과도 해석 용량 1.8 fF (맞춘 값), 본문 4.2 fF"),
 ("비트라인 (BL), 워드라인 (WL)", "전하를 넣고 빼는 수직 N+ 기둥 / 액세스 트랜지스터의 게이트", "Vdd 1.1 V, Vpp 1.8 V. 게이트 길이 100 nm, HfO2 5 nm"),
 ("부유 몸체 (floating body)", "접지 경로가 없는 p형 몸체. 정공이 들어오면 빠져나갈 길이 없음", "두께 30 / 20 / 10 nm, 도핑 1×10<sup>18</sup> / 1×10<sup>16</sup>"),
 ("부유 몸체 효과 (FBE)", "몸체 전위 상승 → body effect로 V_th 하강 → subthreshold 전류로 SN 전하 손실", "Fig. 8. BL 1.1 V ↔ 0 V, WL 0 V"),
 ("subthreshold 기울기 60 mV/decade", "문턱 아래 전류가 전위 60 mV마다 10배 변하는 것 (300 K)", "몸체 전위 60 mV = 손실 10배. Fig. 5(c)의 기울기도 60 mV/decade"),
 ("t_A", "첫 BL 하강 직전의 시각", "FBE에서 21 ns. 로우 해머 Fig. 7에서는 해머 시작 뒤 약 0.45 ns"),
 ("몸체 정공 전하 조건", "몸체에 전자–정공 쌍을 만들어 t_A의 상태를 맞추는 방법. 그동안 SN은 1.1 V에 고정", "약 1050개 = 0.17 fC. 놓으면 SN이 31~38 mV 내려감 (Codex 실험)"),
 ("fin2", "사용자 결정을 반영한 최종 2D 구성의 이름", "1.8 fF, Hurkx A 1.7×10<sup>21</sup>, 정공 약 1050개, 이상적 WL"),
 ("로우 해머, aggressor, victim", "이웃 셀(aggressor)의 WL을 반복해서 켤 때 내 셀(victim)의 SN 전하가 줄어드는 현상", "aggressor WL 0 ↔ 1.8 V, 0.094 ns씩 10사이클, BL 0.55 V"),
 ("Y–Y', Z–Z'", "BL 건너 이웃 / 위아래 층 이웃", "논문 0.0535 / 0.0100 mV per cycle (Fig. 6(e))"),
 ("WL 저항 R, 시상수 τ = RC", "victim 게이트와 WL 전원 사이의 저항. 게이트 전압은 τ만큼 늦게 따라감", "Fig. 7(b)에 그려져 있고 값 없음. 200 kΩ이면 τ 약 30 ps. 쓰지 않음"),
 ("GIDL, Hurkx 모델", "게이트와 드레인 사이 전계로 생기는 터널링 누설과 그 계산 모델", "논문이 이름을 적은 유일한 모델. A 1.7×10<sup>21</sup>"),
 ("충돌 이온화, 계수 배수", "강한 전계에서 캐리어가 전자–정공 쌍을 만드는 현상. 계수에 곱한 수가 배수", "기본 1배. 5~7배에서 WL 꺼짐에 애벌랜치. 진단용이고 기각"),
 ("애벌랜치 항복", "만들어진 쌍이 또 쌍을 만들어 전류가 스스로 커지는 상태. pn 접합의 역방향 항복", "계수 5배 이상에서 몸체 접지 셀의 N+/p 접합이 1.1 V에서 항복"),
 ("래치", "기생 바이폴라 전류와 충돌 이온화가 서로를 키워 스스로 유지되는 방전", "계수 7배 FBE에서 Case 1, 2: 1 ns 안에 0.58 / 0.64 V 손실"),
 ("점수", "(시뮬레이션 − 논문) ÷ 허용오차의 제곱평균제곱근", "허용오차: 문턱 0.02 V, 쓰기 0.03 V, 몸체 상승 30 mV, 손실 0.3 decade"),
 ("aC, fC", "전하의 단위. 1 fC = 10<sup>-15</sup> C, 1 aC = 10<sup>-18</sup> C", "전자 1개 = 0.16 aC. 0.39 aC는 전자 약 2.4개 분량"),
 ("구조 일치 검사", "실행 전 구조를 논문과 대조하는 단계 (tools/gt_start.sh)", "오늘 저녁 배치 5개(라운드 6~10) 모두 통과 후 시작"),
 ("실험 등록부", "Claude와 Codex가 겹치는 실험을 피하려고 보는 표", "GitHub claude 브랜치의 claude/EXPERIMENTS.md"),
]
ANALOGY = E.ANALOGY

def check_text():
    body = [s for sec in SEC for s in sec[4]]
    every = body + [q for sec in SEC if sec[6] for q in sec[6]] + [x for sec in SEC for x in (sec[1], sec[3]) if x] + [x for row in RESULT + TERM for x in row] + [x for sec in SEC if sec[5] for row in sec[5][1] for x in row]
    left = [(w, s) for s in every for w in ANALOGY if w in s]; avg = sum(len(re.sub(r"<[^>]+>", "", s).split()) for s in body) / len(body)
    assert not left, left
    assert avg <= 10, avg
    return len(body), avg

TXT = dict(   # the fixed texts of the page; a later report sets its own (tools/make_eliu_report_1007.py)
    title="Cho 외 (IRPS 2026) 소자 2D 재현: 저녁 현황", meta="2026년 10월 6일 20:40 · 2D 단면 모델",
    res_head="숫자 한눈에: 논문과 최종 2D 구성 fin2",
    res_note="Case 1~5 순서예요. 점수가 1보다 작으면 그림을 읽는 오차 안이에요. 마지막 열은 모델 값이 어떤 종류인지예요.",
    res_cols=["논문 그림", "비교한 값", "논문", "최종 2D 구성 fin2", "점수", "모델 값의 종류"],
    term_note="실험별 내용은 같은 폴더의 <b>GT_IRPS2026_2D_소자완성_보고_2026-10-06.md</b> 9절과\n"
              "<b>GT_IRPS2026_논문대비_비교표_2026-10-06.xlsx</b>, GitHub <b>claude</b> 브랜치의 <b>claude/ANALYSIS.md</b>에 있어요.")

def html(img):
    b64 = lambda f: "data:image/png;base64," + base64.b64encode(open(f, "rb").read()).decode()
    chip = {"한 줄로": "#1e88e5", "기본부터": "#8e24aa", "조금 더": "#43a047", "그래서?": "#f4511e"}; out = []
    tab = lambda rows: "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    for lab, head, k, cap, sents, table, qs in SEC:
        out.append(f'<section><h2><span class="chip" style="background:{chip[lab]}">{lab}</span>{head}</h2>')
        if k: out.append(f'<figure><img src="{b64(img[k])}" alt="{cap}"><figcaption>{cap}</figcaption></figure>')
        out.append('<p class="easy">' + "<br>".join(sents) + "</p>")
        if table: out.append('<div class="wrap"><table><tr>' + "".join(f"<th>{h}</th>" for h in table[0]) + "</tr>" + tab(table[1]) + "</table></div>")
        if qs: out.append('<ol class="easy">' + "".join(f"<li>{q}</li>" for q in qs) + "</ol>")
        out.append("</section>")
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TXT['title']}</title>
<style>
 body {{ font-family: "Malgun Gothic", "맑은 고딕", "Apple SD Gothic Neo", sans-serif; background: #fffdf7; color: #263238; margin: 0; }}
 main {{ max-width: 980px; margin: 0 auto; padding: 24px 16px 60px; }}
 h1 {{ font-size: 27px; margin: 8px 0 4px; }} .meta {{ color: #78909c; font-size: 14px; margin-bottom: 18px; line-height: 1.6; }}
 section {{ background: #fff; border: 1px solid #eceff1; border-radius: 16px; padding: 18px 22px; margin: 18px 0; box-shadow: 0 1px 3px rgba(0,0,0,.05); }}
 h2 {{ font-size: 21px; margin: 2px 0 12px; }} .chip {{ color: #fff; font-size: 14px; border-radius: 999px; padding: 4px 12px; margin-right: 10px; vertical-align: 3px; }}
 p.easy, ol.easy {{ font-size: 18px; line-height: 1.85; margin: 10px 0 8px; }} ol.easy {{ padding-left: 28px; }}
 figure {{ margin: 6px 0 10px; }} img {{ max-width: 100%; height: auto; border-radius: 10px; }} figcaption {{ color: #607d8b; font-size: 14px; margin-top: 4px; }}
 .ref {{ background: #f5f7f8; }} .ref h2 {{ font-size: 19px; }} .ref p {{ font-size: 14.5px; line-height: 1.7; color: #455a64; }}
 .wrap {{ overflow-x: auto; margin-top: 10px; }} table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; }}
 th, td {{ border: 1px solid #cfd8dc; padding: 6px 9px; vertical-align: top; text-align: left; }} th {{ background: #37474f; color: #fff; }}
 td:first-child {{ font-weight: bold; }}
</style></head><body><main>
<h1>{TXT['title']}</h1>
<div class="meta">{TXT['meta']} · eliU 형식: 문장과 구조는 쉽게, 용어는 실제 용어 그대로, 새 개념은 전공 과목에 연결<br>
대상 논문: "Row Hammer Effect and Floating Body Effect of Monolithic 3D Stackable 1T1C DRAM" (IRPS 2026). 논문 값은 그림에서 읽은 수치예요.</div>
{"".join(out)}
<section class="ref"><h2>{TXT['res_head']}</h2>
<p>{TXT['res_note']}</p>
<div class="wrap"><table><tr>{"".join(f"<th>{h}</th>" for h in TXT['res_cols'])}</tr>{tab(RESULT)}</table></div></section>
<section class="ref"><h2>용어 풀이</h2>
<p>본문에 나온 용어의 뜻과 이 작업에서의 값·근거예요. {TXT['term_note']}</p>
<div class="wrap"><table><tr><th>용어</th><th>뜻</th><th>이 작업에서의 값·근거</th></tr>{tab(TERM)}</table></div></section>
</main></body></html>
"""

if __name__ == "__main__":
    n, avg = check_text()
    R1 = {c: fbe("h1", c) for c in range(1, 6)}
    s = sysf("DraW_c2"); t = s["time"]; t0 = edges(t, s[key(s, "nWL)")], 0, 1.8, True)[0]; g = s[key(s, "nGv")]      # check of the time constant quoted in the text
    print("victim gate node behind 200 kOhm reaches 63 % of 1.8 V after", round(next((x - t0) * 1e12 for x, y in zip(t, g) if x > t0 and y >= 0.632 * 1.8), 1), "ps")
    img = dict(cell=fig_cell(), score=fig_score(), loss=fig_loss(R1), r=fig_r(), ii=fig_ii(), gnd=fig_gnd())
    open(OUT, "w", encoding="utf-8", newline="\n").write(html(img))
    print(f"text: {n} sentences, {avg:.1f} units per sentence, no analogy word"); print("\n".join(img.values())); print(OUT, os.path.getsize(OUT) // 1024, "kB")
