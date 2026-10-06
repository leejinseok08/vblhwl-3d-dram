# make_eli5_report.py - where the 2D reproduction stands, as an easy picture report (user, 2026-10-06, /eli5).
# The first version told it in an analogy world (water bucket, marbles ...); the user: "it is all analogy, I cannot tell what
# it means - keep the way of explaining, use the real terms". So: one-line summary -> basics -> a little more -> so what,
# short sentences, six pictures, and every word the real term (BL, WL, storage node, floating body, holes, mV, ns).
# Draws gt2d_status_01 .. 06 into Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram and writes one HTML report with the pictures
# embedded into ...\results_vbl_hwl_1t1c_3ddram. Run on the PC: python tools/make_eli5_report.py
# Numbers: NOTES (ax), (ay). Curves from runs/DfinF_c*, bars from runs/Dh1F_c* (result files copied from the server).
# Checked at the end: no word of the analogy version left, sentences short (10 space-separated units or fewer on average).
import sys, os, glob, base64, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch
from gt_tran import load, at, edges, PAPER_FBE
import paper_targets as P
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
BASE = r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프"
PIC = os.path.join(BASE, "pic_vbl_hwl_1t1c_3ddram"); OUT = os.path.join(BASE, "results_vbl_hwl_1t1c_3ddram", "GT_IRPS2026_현황보고_쉬운설명_실제용어_2026-10-06.html")
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
GREEN, YELLOW, RED, GREY, ORANGE, INK = "#66bb6a", "#ffb300", "#ef5350", "#b0bec5", "#fb8c00", "#263238"
CASE = ["Case 1\n30 nm · 1e18\nWF 4.7 eV", "Case 2\n20 nm · 1e18\nWF 4.7 eV", "Case 3\n10 nm · 1e18\nWF 4.7 eV", "Case 4\n10 nm · 1e16\nWF 4.7 eV", "Case 5\n10 nm · 1e16\nWF 5.0 eV"]
COL = {1: "#d32f2f", 2: "#c2185b", 3: "#1976d2", 4: "#f57c00", 5: "#388e3c"}

def save(fig, name):
    f = os.path.join(PIC, name); fig.savefig(f, dpi=130, bbox_inches="tight", facecolor="white"); plt.close(fig); return f

def run(tag, c):          # one FBE run: time [ns] from the charged node, storage node [V], BL-low phases, body rise [mV]
    d = os.path.join(RUNS, f"D{tag}F_c{c}"); s = load(os.path.join(d, f"D{tag}F_c{c}_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn, bl, wl = s[k("nSN)")], s[k("nBL")], s[k("nWL)")]
    t0 = edges(t, wl, 0, 1.8, False)[0] + 4e-11; f = edges(t, bl, 0, 1.1, False); r = [x for x in edges(t, bl, 0, 1.1, True) if x > f[0]]
    kv = next(x for x in dv if "ElectrostaticPotential" in x); i = [j for j, x in enumerate(t) if x >= t0]
    return dict(t=[(t[j] - t0) * 1e9 for j in i], sn=[sn[j] for j in i], lo=[((a - t0) * 1e9, (b - t0) * 1e9) for a, b in zip(f, r)],
                rise=(at(dv["time"], dv[kv], f[0] - 3e-10) - dv[kv][0]) * 1e3)

def fig_map():
    fig, ax = plt.subplots(figsize=(15, 6.6)); ax.set_xlim(0, 12.4); ax.set_ylim(-2.5, 3.0); ax.axis("off"); ax.set_aspect("equal")
    ax.plot([0.7, 11.7], [0, 0], color="#cfd8dc", lw=26, solid_capstyle="round", zorder=1)
    ax.plot([0.7, 7.2], [0, 0], color="#a5d6a7", lw=26, solid_capstyle="round", zorder=2)
    stops = [("구조", "○", "Fig. 2, Fig. 5(a)와\n치수·접합 일치", GREEN), ("Id–Vg", "○", "Fig. 5(c)와 일치\n(점수 0.73)", GREEN),
             ("쓰기", "○", "Fig. 4(a)와 일치\n(점수 0.93)", GREEN), ("FBE", "△", "몸체 정공 전하를\n조건으로 넣으면\nFig. 8(b), (c)와 일치", YELLOW),
             ("로우 해머", "×", "Fig. 6(e), Fig. 7과\n아직 불일치", RED), ("3D 모델", "…", "구조 점검까지 끝내고\n중지 상태", GREY)]
    for i, (name, mark, note, col) in enumerate(stops):
        x = 1.2 + 2.0 * i
        ax.add_patch(Circle((x, 0), 0.62, fc=col, ec="white", lw=4, zorder=3))
        ax.text(x, -0.03, mark, ha="center", va="center", fontsize=30, fontweight="bold", color="white", zorder=4)
        ax.text(x, 1.75, f"{i + 1}. {name}", ha="center", fontsize=15, fontweight="bold", color=INK)
        ax.text(x, -1.05, note, ha="center", va="top", fontsize=12, color="#37474f", linespacing=1.4)
    ax.text(7.2, 0.7, "지금 여기\n▼", ha="center", va="bottom", fontsize=15, fontweight="bold", color="#d84315", linespacing=0.95)
    ax.text(0.2, 2.6, "재현 진행 지도 (2D 단면 모델)", fontsize=19, fontweight="bold", color=INK)
    return save(fig, "gt2d_status_01_map.png")

def cell(ax, charged):
    ax.set_xlim(0, 10.2); ax.set_ylim(0, 6.9); ax.axis("off"); ax.set_aspect("equal")
    ax.add_patch(FancyBboxPatch((0.5, 0.6), 1.0, 5.2, boxstyle="round,pad=0.02,rounding_size=0.3", fc="#64b5f6", ec="#1565c0", lw=2))
    ax.text(1.0, 3.2, "BL\n(N+)\n" + ("0 V" if charged else "1.1 V"), ha="center", va="center", fontsize=12.5, fontweight="bold", color="white")
    ax.add_patch(Rectangle((1.5, 2.75), 3.9, 0.9, fc="#fff9c4", ec="#f9a825", lw=2))                     # the floating body
    for y in (3.8, 2.1): ax.add_patch(FancyBboxPatch((2.3, y), 3.1, 0.5, boxstyle="round,pad=0.01,rounding_size=0.12", fc="#90a4ae", ec="#455a64", lw=1.5))
    ax.text(3.85, 4.05, "WL (게이트) 0 V", ha="center", va="center", fontsize=11.5, color="white", fontweight="bold")
    ax.text(3.85, 2.35, "WL (게이트) 0 V", ha="center", va="center", fontsize=11.5, color="white", fontweight="bold")
    ax.add_patch(Rectangle((5.4, 2.75), 0.9, 0.9, fc="#bbdefb", ec="#1565c0", lw=2)); ax.text(5.85, 3.78, "N+", ha="center", va="bottom", fontsize=11, color="#0d47a1", fontweight="bold")
    lvl = 3.9 if charged else 5.0
    ax.add_patch(Rectangle((6.3, 1.0), 3.0, lvl - 1.0, fc="#81d4fa", ec="none")); ax.add_patch(Rectangle((6.3, 1.0), 3.0, 4.4, fc="none", ec=INK, lw=2.5))
    ax.text(7.8, 2.3, "저장 노드 (SN)\n커패시터", ha="center", va="center", fontsize=13.5, fontweight="bold", color="#01579b", linespacing=1.4)
    ax.annotate("부유 몸체 (p형)", xy=(2.0, 3.2), xytext=(3.1, 5.6), fontsize=13, fontweight="bold", color="#e65100", ha="center",
                arrowprops=dict(arrowstyle="-|>", color="#e65100", lw=1.8))
    ax.plot([1.6, 1.6, 5.3, 5.3], [1.95, 1.8, 1.8, 1.95], color=INK, lw=1.6); ax.text(2.9, 1.3, "액세스 트랜지스터", ha="center", fontsize=12.5, fontweight="bold", color=INK)
    if charged:
        for x, y in ((2.6, 3.0), (2.95, 3.35), (3.3, 3.0), (3.65, 3.35), (4.0, 3.0), (4.35, 3.35), (4.7, 3.0), (5.05, 3.35), (2.25, 3.35)):
            ax.add_patch(Circle((x, y), 0.14, fc=ORANGE, ec="#e65100", lw=1)); ax.text(x, y - 0.01, "+", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        ax.annotate("정공", xy=(4.7, 3.05), xytext=(5.2, 1.1), fontsize=13, fontweight="bold", color="#e65100", ha="center",
                    arrowprops=dict(arrowstyle="-|>", color="#e65100", lw=1.8))
        ax.add_patch(FancyArrowPatch((1.7, 3.2), (6.2, 3.2), arrowstyle="-|>", mutation_scale=18, color="#0277bd", lw=2.2, ls=(0, (4, 3))))
        ax.text(5.85, 2.62, "전자 →", ha="center", va="top", fontsize=11.5, color="#0277bd", fontweight="bold")
        ax.text(7.8, 4.25, "SN 전압 ↓ (전자 누설)", ha="center", fontsize=12, color="#01579b"); ax.text(7.8, 5.6, "1.1 V보다 낮아짐", ha="center", fontsize=12, color="#01579b")
        ax.text(5.1, 6.35, "FBE: 몸체에 정공이 쌓이고 BL이 0 V가 되면 전자가 BL → SN으로 새요", ha="center", fontsize=14, fontweight="bold", color=INK)
    else:
        ax.text(7.8, 5.6, "SN 전압 1.1 V = '1'", ha="center", fontsize=12, color="#01579b")
        ax.text(5.1, 6.35, "유지 상태: WL 0 V, 채널 닫힘, SN 전압 유지", ha="center", fontsize=14, fontweight="bold", color=INK)

def fig_cell():
    fig, ax = plt.subplots(1, 2, figsize=(15, 5.4)); cell(ax[0], False); cell(ax[1], True); fig.tight_layout()
    return save(fig, "gt2d_status_02_cell.png")

SCORE = [("Id–Vg (Fig. 5(c))", 0.79, 0.73), ("쓰기 (Fig. 4(a))", 6.49, 0.93), ("FBE: 첫 BL 저전위 구간 손실 (Fig. 8(b), (c))", 6.62, 0.84), ("FBE: 200 ns 손실 (Fig. 8(b), (c))", 5.14, 0.51),
         ("몸체 전위 상승 (Fig. 8(a))", 12.0, 2.0), ("로우 해머 (Fig. 6(e))", 4.7, 4.4), ("로우 해머 + 충돌 이온화 (Fig. 7)", 11.9, 11.9)]
def fig_score():
    fig, ax = plt.subplots(figsize=(14, 6.2)); n = len(SCORE); box = dict(fc="white", ec="none", pad=1.5)
    for i, (name, a, b) in enumerate(SCORE):
        y = n - 1 - i; col = GREEN if b < 1 else YELLOW if b < 3 else RED
        ax.barh(y + 0.19, a, 0.34, color=GREY, zorder=3); ax.barh(y - 0.19, b, 0.34, color=col, zorder=3)
        ax.text(a * 1.07, y + 0.19, f"{a:g}", va="center", fontsize=11, color="#546e7a", bbox=box, zorder=5); ax.text(b * 1.07, y - 0.19, f"{b:g}", va="center", fontsize=12.5, fontweight="bold", color=INK, bbox=box, zorder=5)
    ax.set_xscale("log"); ax.set_xlim(0.08, 60); ax.set_yticks(range(n)); ax.set_yticklabels([s[0] for s in SCORE][::-1], fontsize=12.5)
    ax.axvline(1.0, color="#2e7d32", ls="--", lw=2, zorder=4)
    ax.text(0.93, n - 0.35, "점수 1 = 그림 판독 오차의 한계\n(이 선보다 왼쪽이면 재현)", ha="right", va="bottom", fontsize=11.5, color="#2e7d32")
    ax.set_xticks([0.1, 0.5, 1, 2, 5, 10, 20]); ax.set_xticklabels(["0.1", "0.5", "1", "2", "5", "10", "20"], fontsize=11); ax.minorticks_off()
    ax.set_xlabel("점수 = (시뮬레이션 - 논문) ÷ 허용오차의 제곱평균제곱근 (작을수록 좋음)", fontsize=12.5); ax.set_ylim(-0.7, n + 0.35); ax.grid(axis="x", alpha=0.25, zorder=0)
    ax.barh([-5], [1], color=GREY, label="오늘 시작 (기준선)"); ax.barh([-5], [1], color=GREEN, label="최종 2D 구성: 재현 (1 미만)"); ax.barh([-5], [1], color=YELLOW, label="최종 2D 구성: 부분 재현"); ax.barh([-5], [1], color=RED, label="최종 2D 구성: 재현 안 됨")
    ax.legend(loc="upper right", fontsize=11.5, frameon=True); ax.set_title("점수판: 논문 그림별로 얼마나 가까워졌나", fontsize=17, fontweight="bold", color=INK, pad=12)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    return save(fig, "gt2d_status_03_score.png")

def fig_holes(R1, RF):
    need = [1084, 1056, 1099, 962, 1138]; x = list(range(1, 6))
    fig, ax = plt.subplots(1, 2, figsize=(15.5, 5.9))
    ax[0].axhspan(960, 1140, color="#ffe0b2", alpha=0.7, zorder=1); ax[0].bar(x, need, 0.55, color=ORANGE, ec="#e65100", zorder=3)
    for i, v in zip(x, need): ax[0].text(i, v + 22, f"{v}개", ha="center", fontsize=12.5, fontweight="bold", color=INK)
    ax[0].text(3, 1265, "다섯 Case 모두 약 1050개 (0.17 fC)", ha="center", fontsize=15, fontweight="bold", color="#e65100")
    ax[0].set_ylim(0, 1400); ax[0].set_ylabel("t_A 시점의 몸체 정공 수 [개]", fontsize=13); ax[0].set_title("Fig. 8(a)의 몸체 전위가 되는 데\n필요한 정공 수 (2D 모델)", fontsize=15, fontweight="bold", color=INK)
    w = 0.27; book = [P.FBE_RISE[c] for c in x]
    for dx, v, col, lab in ((-w, book, "#546e7a", "논문 Fig. 8(a)"), (0, [R1[c]["rise"] for c in x], "#ffcc80", "2D, 정공 약 1050개 (막대에 맞춤)"), (w, [RF[c]["rise"] for c in x], ORANGE, "2D, 정공 약 1300개 (손실 곡선에 맞춤, 최종)")):
        ax[1].bar([i + dx for i in x], v, w, color=col, label=lab, zorder=3)
        for i, y in zip(x, v): ax[1].text(i + dx, y + 8, f"{y:.0f}", ha="center", fontsize=9, color=INK)
    ax[1].set_ylim(0, 740); ax[1].set_ylabel("몸체 중심 전위 상승 [mV] (해석 시작 → t_A)", fontsize=13); ax[1].legend(fontsize=11, loc="upper right")
    ax[1].set_title("몸체 전위 상승: 논문과 2D 모델", fontsize=15, fontweight="bold", color=INK)
    for a in ax:
        a.set_xticks(x); a.set_xticklabels(CASE, fontsize=10.5); a.grid(axis="y", alpha=0.25, zorder=0)
        for s in ("top", "right"): a.spines[s].set_visible(False)
    fig.tight_layout(); return save(fig, "gt2d_status_04_holes.png")

def fig_loss(RF):
    name = {1: "Case 1 (30 nm)", 2: "Case 2 (20 nm)", 3: "Case 3 (10 nm, 1e18)", 4: "Case 4 (10 nm, 1e16)", 5: "Case 5 (1e16, WF 5.0)"}
    fig, ax = plt.subplots(1, 2, figsize=(15.5, 5.9))
    for a, cs, ylim, ttl in ((ax[0], (1, 2, 3), (0.975, 1.106), "Fig. 8(b): 몸체 두께 30 / 20 / 10 nm"), (ax[1], (3, 4, 5), (1.080, 1.1012), "Fig. 8(c) 확대: 도핑과 일함수")):
        for lo, hi in RF[1]["lo"]: a.axvspan(lo, hi, color="#e1f5fe", zorder=0)
        for c in cs:
            r = RF[c]; a.plot(r["t"], r["sn"], color=COL[c], lw=2.2, label=f"2D 모델, {name[c]}", zorder=3)
            ends = [hi for _, hi in r["lo"]]
            pts = list(zip(ends, PAPER_FBE[c][0])) if c in PAPER_FBE and PAPER_FBE[c][0] else [(ends[0], P.FBE_FIRST[c])]
            pts.append((200.0, P.FBE_200[c]))
            a.plot([p for p, _ in pts], [1.1 - v * 1e-3 for _, v in pts], "o", mfc="white", color=COL[c], ms=8, mew=2, zorder=4, label=f"논문, Case {c} (그림 판독)")
        a.set_xlim(0, 206); a.set_ylim(*ylim); a.set_xlabel("시간 [ns] (0 = 저장 노드 충전 직후)", fontsize=13); a.set_ylabel("저장 노드 전압 [V]", fontsize=13)
        a.set_title(ttl, fontsize=15, fontweight="bold", color=INK); a.grid(alpha=0.25); a.legend(fontsize=10, loc="lower left")
        for s in ("top", "right"): a.spines[s].set_visible(False)
    ax[0].text(160, 0.986, "하늘색 띠 = BL이 0 V인 구간\n(21 ns 주기, 9회)", ha="center", fontsize=11.5, color="#0277bd", bbox=dict(fc="white", ec="#b3e5fc", pad=4))
    fig.suptitle("FBE: 저장 노드 전압 손실 (선 = 2D 모델, 동그라미 = 논문)", fontsize=17, fontweight="bold", color=INK); fig.tight_layout()
    return save(fig, "gt2d_status_05_fbe_loss.png")

def fig_rh():
    fig, ax = plt.subplots(figsize=(12.5, 5.8)); w = 0.25; g = [0, 1]
    data = (("논문 Fig. 6(e)", "#546e7a", [0.0535, 0.0100]), ("2D 모델, 이상적인 WL", RED, [0.0007, 0.0007]), ("2D 모델, WL 저항 R = 200 kΩ", YELLOW, [0.0006, 0.0093]))
    for k, (lab, col, v) in enumerate(data):
        xs = [i + (k - 1) * w for i in g]; ax.bar(xs, v, w, color=col, label=lab, zorder=3)
        for x, y in zip(xs, v): ax.text(x, y * 1.12, f"{y:.4f}", ha="center", fontsize=12, fontweight="bold", color=INK)
    ax.set_yscale("log"); ax.set_ylim(0.0003, 0.3); ax.set_yticks([0.001, 0.01, 0.1]); ax.set_yticklabels(["0.001", "0.01", "0.1"], fontsize=11); ax.minorticks_off()
    ax.set_xticks(g); ax.set_xticklabels(["Y–Y' (BL 건너편 이웃 셀)", "Z–Z' (위아래 층 이웃 셀)"], fontsize=14)
    ax.set_ylabel("사이클당 저장 노드 손실 [mV]", fontsize=13); ax.legend(fontsize=12, loc="upper right"); ax.grid(axis="y", alpha=0.25, zorder=0)
    ax.text(-0.44, 0.24, "Case 2, 충돌 이온화 끔, 저장 노드 4.2 fF 기준.\nR을 넣은 Z–Z' 값은 10사이클 평균 (한 번의 결합 이동)", fontsize=10.5, color="#546e7a", va="top", linespacing=1.5)
    ax.set_title("로우 해머: 2D 단면에서는 논문만큼 손실이 나오지 않음", fontsize=17, fontweight="bold", color=INK, pad=12)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    return save(fig, "gt2d_status_06_rh.png")

# ------------------------------------------------------------------ the text: easy sentences, real terms
SEC = [   # (label, heading, picture key, caption, sentences, numbered questions)
 ("한 줄로", "무엇을 하고 있나요?", None, None,
  ["Cho 외 IRPS 2026 논문의 1T1C 3D DRAM 셀을 Sentaurus TCAD로 똑같이 만들고 있어요.", "2D 단면 모델로는 거의 끝났어요.", "Id–Vg, 쓰기, FBE 손실 곡선이 논문 그림과 맞아요.",
   "로우 해머와 몸체 정공의 출처는 아직 재현하지 못했어요."], None),
 ("기본부터", "셀 구조와 두 가지 현상", "cell", "셀의 2D 단면을 단순하게 그린 것. 왼쪽은 유지 상태, 오른쪽은 몸체에 정공이 쌓인 뒤 BL이 0 V가 된 상태예요.",
  ["셀은 액세스 트랜지스터 1개와 커패시터 1개예요.", "저장 노드(SN)는 커패시터 쪽 전극이에요.", "SN 전압이 1.1 V면 '1'을 저장한 상태예요.", "비트라인(BL)은 전하를 넣고 빼는 수직 기둥이에요.",
   "워드라인(WL)은 게이트예요.", "몸체 위아래에 하나씩 있어요.", "WL을 1.8 V로 올리면 채널이 열려요.", "WL이 0 V면 채널이 닫혀요.",
   "몸체는 채널이 생기는 p형 실리콘이에요.", "이 몸체는 어디에도 접지되어 있지 않아요.", "그래서 부유 몸체(floating body)라고 불러요.",
   "몸체에 정공이 쌓이면 몸체 전위가 올라가요.", "그러면 문턱 전압이 낮아져요.", "WL이 0 V여도 전자가 BL에서 SN으로 새요.", "SN 전압이 내려가요.", "이것이 부유 몸체 효과(FBE)예요.",
   "로우 해머는 이웃 셀 때문에 생기는 손실이에요.", "이웃 셀의 WL을 계속 켰다 끄면 내 SN 전압이 조금씩 내려가요.", "논문은 두 현상을 숫자로 보여 줘요.", "2D 모델에서 같은 숫자가 나오면 재현 성공이에요."], None),
 ("조금 더", "1. 진행 지도", "map", "여섯 단계. 초록은 재현된 단계, 노랑은 조건을 넣어 재현된 단계, 빨강은 재현 안 된 단계예요.",
  ["단계는 모두 여섯 개예요.", "구조, Id–Vg, 쓰기는 논문과 맞아요.", "FBE는 몸체 정공 전하를 조건으로 넣어서 맞췄어요.", "로우 해머는 아직 논문과 달라요.", "3D 모델은 중지 상태예요."], None),
 ("조금 더", "2. 시뮬레이션 전 구조 일치 검사", None, None,
  ["배치를 시작하기 전마다 구조를 논문과 대조해요.", "게이트 길이 100 nm, 게이트 산화막 5 nm를 확인해요.", "게이트 두께 20 nm, 수직 격리 30 nm도 확인해요.", "몸체 두께와 도핑은 Case별로 확인해요.",
   "메시에서 접합 위치도 읽어요.", "50.00 nm와 175.00 nm여야 해요.", "모두 맞을 때만 실행을 시작해요.", "오늘 배치는 여섯 개였어요.", "여섯 개 모두 통과한 뒤에 시작했어요.",
   "첫 배치는 한 번 거부됐어요.", "구조 파일 하나가 서버에 없었기 때문이에요.", "파일을 올리고 다시 검사해서 통과했어요."], None),
 ("조금 더", "3. 점수판: 무엇이 좋아졌나요?", "score", "논문 그림별 점수. 회색은 오늘 시작할 때, 색 막대는 최종 2D 구성이에요.",
  ["점수는 시뮬레이션과 논문의 차이를 허용오차로 나눈 값이에요.", "1보다 작으면 그림 판독 오차 안이에요.", "Id–Vg는 0.79에서 0.73이 됐어요.", "Hurkx 터널링 계수 A를 1.7×10<sup>21</sup>로 낮췄어요.", "그래서 GIDL 가지가 논문과 맞아요.",
   "쓰기는 6.49에서 0.93이 됐어요.", "저장 노드 용량을 1.8 fF로 바꿨기 때문이에요.", "본문에는 4.2 fF라고 적혀 있어요.", "그런데 Fig. 4(a)의 충전 속도는 1.8 fF일 때 맞아요.",
   "FBE 손실은 6.62에서 0.84가 됐어요.", "200 ns 손실은 5.14에서 0.51이 됐어요.", "둘 다 몸체에 정공 전하를 넣은 결과예요."], None),
 ("조금 더", "4. 몸체 정공: 오늘 찾은 것", "holes", "왼쪽: Fig. 8(a)의 몸체 전위에 필요한 정공 수. 오른쪽: 정공을 넣었을 때의 몸체 전위 상승.",
  ["Fig. 8(a)는 몸체 전위 상승을 보여 줘요.", "다섯 Case의 값은 555 / 445 / 365 / 320 / 368 mV예요.", "그런데 필요한 정공 수는 거의 같았어요.", "1084 / 1056 / 1099 / 962 / 1138개예요.", "약 1050개, 전하로 0.17 fC예요.",
   "이유도 찾았어요.", "막대는 '공통 최종 전위 − 공핍된 몸체의 처음 전위'예요.", "처음 전위가 Case마다 달라서 막대가 달라 보여요.",
   "정공 1050개를 넣으면 몸체 전위 상승이 논문과 같아요.", "그런데 그때는 SN 손실이 3~20배 작아요.", "정공 1300개(0.21 fC)를 넣으면 손실 곡선이 논문과 같아요.", "그때는 몸체 전위가 53~68 mV 더 높아요.",
   "둘을 동시에 맞추지는 못했어요.", "몸체 전위 60 mV가 전류 10배에 해당하기 때문이에요.", "지금은 손실 곡선에 맞춰 두었어요."], None),
 ("조금 더", "5. FBE 손실 곡선: 논문과 나란히 보기", "loss", "SN 전압 대 시간. 선은 2D 모델, 동그라미는 논문 그림에서 읽은 값이에요.",
  ["BL을 1.1 V와 0 V 사이에서 아홉 번 오르내렸어요.", "BL이 0 V인 구간마다 SN 전압이 내려가요.", "몸체가 두꺼울수록 손실이 커요.", "Case 순서가 논문과 같아요.",
   "첫 구간에서 많이 내려가요.", "뒤로 갈수록 덜 내려가요.", "이 꺾이는 모양도 논문과 같아요.", "200 ns 손실은 82 / 56 / 16.6 / 12.5 / 1.6 mV예요.", "논문은 100 / 50 / 14.6 / 7 / 1 mV예요.",
   "첫 구간 손실은 18.9 / 16.0 / 6.4 / 5.3 / 0.14 mV예요.", "논문은 55 / 29 / 7.1 / 3.5 / 0 mV예요.", "Case 1과 2의 첫 구간은 논문보다 작아요.", "Case 5는 손실이 거의 없어요.", "논문도 그래요."], None),
 ("조금 더", "6. 아직 재현하지 못한 것 세 가지", "rh", "로우 해머의 사이클당 SN 손실. 논문 막대가 2D 모델보다 훨씬 커요.",
  ["첫째, 몸체 정공의 출처를 몰라요.", "쓰기 중 충돌 이온화는 정공을 0~123개만 남겨요.", "WL을 0.01 ps 만에 꺼도 28~258개예요.", "유지 구간의 터널링은 정공을 충분히 만들어요.", "대신 SN이 36~60 mV 처져요.",
   "논문 곡선에는 그런 처짐이 없어요.", "그래서 지금은 몸체에 일정한 생성을 넣었어요.", "첫 BL 하강 직전(t_A)의 상태만 맞춘 조건이에요.",
   "둘째, 로우 해머가 논문과 달라요.", "Y–Y'는 사이클당 0.0007 mV예요.", "논문은 0.0535 mV예요.", "2D 단면에서는 BL 기둥이 이웃 WL을 가려요.",
   "Z–Z'는 WL 저항 200 kΩ을 넣으면 0.0093 mV예요.", "논문은 0.0100 mV예요.", "다만 이 값은 한 번 생기는 결합 이동이에요.", "쌓이는 손실이 아니에요.", "충돌 이온화를 켠 Z–Z'의 급락(Fig. 7(a))은 나오지 않아요.",
   "셋째, 3D 모델은 중지 상태예요.", "켜져 있던 3D 실행 두 개도 중단했어요."], None),
 ("그래서?", "이제 무엇을 정하면 될까요?", None, None,
  ["2D 소자는 거의 완성이에요.", "여기서 확정한 값을 3D 모델에 그대로 넣게 돼요.", "그 뒤에 로우 해머와 패스 게이트 효과를 볼 수 있어요.", "이제 네 가지를 정해 주세요."],
  ["몸체 정공 전하를 '조건'으로 넣는 방식을 계속 쓸까요?", "정공 전하를 손실 곡선(약 1300개)에 맞출까요, Fig. 8(a) 막대(약 1050개)에 맞출까요?",
   "로우 해머에 WL 저항 200 kΩ을 쓸까요, 이상적인 WL로 둘까요?", "3D를 다시 시작할까요?"]),
]
RESULT = [   # figure, what is compared, paper, final 2D configuration, score
 ("Fig. 5(c) Id–Vg", "1×10<sup>-8</sup> A가 되는 Vg, Case 1~5", "0.47 / 0.44 / 0.42 / 0.39 / 0.65 V", "0.48 / 0.45 / 0.43 / 0.39 / 0.69 V", "0.73"),
 ("Fig. 5(c) GIDL", "log<sub>10</sub> I @ Vg −1 V", "−13.5 / −13.2 / −13.1 / −13.2 / −12.85", "−13.49 / −13.24 / −13.17 / −13.43 / −12.83", "(위에 포함)"),
 ("Fig. 4(a) 쓰기", "WL 상승 뒤 12 / 24 / 39 / 60 ps의 SN 전압 (Case 2)", "0.72 / 0.92 / 1.06 / 1.13 V", "0.74 / 0.92 / 1.02 / 1.09 V", "0.93"),
 ("Fig. 8(b), (c) FBE", "첫 BL 저전위 구간의 SN 손실", "55 / 29 / 7.1 / 3.5 / 0 mV", "18.9 / 16.0 / 6.4 / 5.3 / 0.14 mV", "0.84"),
 ("Fig. 8(b), (c) FBE", "200 ns의 SN 손실", "100 / 50 / 14.6 / 7 / 1 mV", "82 / 56 / 16.6 / 12.5 / 1.6 mV", "0.51"),
 ("Fig. 8(a)", "몸체 중심 전위 상승", "555 / 445 / 365 / 320 / 368 mV", "608 / 506 / 429 / 378 / 436 mV (정공 약 1050개일 때 548 / 442 / 363 / 319 / 367)", "2.0 (0.12)"),
 ("Fig. 6(e) 로우 해머", "사이클당 SN 손실, Y–Y' / Z–Z'", "0.0535 / 0.0100 mV", "0.0014 / 0.0014 mV (이상적 WL, 1.8 fF)", "4.4"),
 ("Fig. 7 로우 해머 + 충돌 이온화", "Z–Z' SN 전압 / 몸체 접지 시 사이클당 손실", "1.1 → 0.58 V / 0.036 mV", "급락 없음 / 0.0015 mV", "11.9"),
]
TERM = [   # term, plain meaning, value and source in this work
 ("1T1C DRAM 셀", "트랜지스터 1개와 커패시터 1개로 1비트를 저장하는 셀", "수직 BL, 수평 WL 구조. 논문 Fig. 2"),
 ("저장 노드 (SN)", "커패시터의 셀 쪽 전극. 여기 전압이 데이터", "'1' = 1.1 V. 용량은 본문 3.6 / 4.2 / 5.1 fF, 과도 해석에서는 1.8 fF로 확정 (Fig. 4(a))"),
 ("비트라인 (BL)", "셀에 전하를 넣고 빼는 선. 이 구조에서는 수직 N+ 기둥", "Vdd 1.1 V, 쓰기 때 1.168 V"),
 ("워드라인 (WL)", "액세스 트랜지스터의 게이트. 몸체 위아래 이중 게이트", "Vpp 1.8 V. 길이 100 nm, 두께 20 nm, HfO2 5 nm"),
 ("부유 몸체 (floating body)", "접지 경로가 없는 p형 몸체. 정공이 들어오면 빠져나갈 길이 없음", "두께 30 / 20 / 10 nm, 도핑 1×10<sup>18</sup> / 1×10<sup>16</sup>"),
 ("Case 1~5", "논문 Fig. 5(b)의 다섯 가지 소자 조건", "몸체 30 / 20 / 10 / 10 / 10 nm, 도핑 1e18 / 1e18 / 1e18 / 1e16 / 1e16, 일함수 4.7 / 4.7 / 4.7 / 4.7 / 5.0 eV"),
 ("정공", "몸체에 쌓이는 양전하 캐리어", "약 1050개 = 0.17 fC (Fig. 8(a) 막대에 해당), 약 1300개 = 0.21 fC (손실 곡선에 맞춤, 현재 채택)"),
 ("몸체 전위 상승", "몸체 중심 정전위가 해석 시작(모두 0 V)에서 t_A까지 오른 양", "Fig. 8(a). t_A = 첫 BL 하강 직전 (21 ns)"),
 ("부유 몸체 효과 (FBE)", "몸체에 쌓인 정공이 문턱 전압을 낮춰 SN 전하가 새는 현상", "Fig. 8. BL을 1.1 V ↔ 0 V로 토글, WL 0 V. 첫 하강 21 ns, 주기 21 ns, 9회"),
 ("로우 해머", "이웃 셀의 WL을 반복해서 켰다 끌 때 내 SN 전하가 줄어드는 현상", "Fig. 6(e), 7. aggressor WL 0 ↔ 1.8 V, BL 0.55 V. Y–Y' = BL 건너 이웃, Z–Z' = 위아래 층 이웃"),
 ("Id–Vg", "게이트 전압에 따른 드레인 전류 곡선", "Fig. 5(c). 문턱, 기울기, GIDL, 켜진 전류를 비교"),
 ("GIDL, Hurkx A", "게이트가 음일 때 접합에서 생기는 터널링 누설과 그 모델 계수", "A 1.7×10<sup>21</sup> (기본 3.5×10<sup>21</sup>), Fig. 5(c)의 Vg −1 V에 맞춤"),
 ("충돌 이온화", "빠른 캐리어가 전자–정공 쌍을 새로 만드는 현상", "논문은 이 모델을 켜면 몸체가 뜬다고 함 (Fig. 7(e): 2.4 → 665 mV). 2D에서는 쓰기 중 쌍 600~900개, 남는 정공 0~123개"),
 ("WL 저항 R", "논문 Fig. 7(b) 회로의 victim 게이트와 WL 전원 사이 저항 (값 없음)", "맞춤 후보 200 kΩ: Z–Z' 0.0093 mV (10사이클 평균)"),
 ("몸체 정공 전하 조건", "몸체 영역에 일정한 전자–정공 생성을 넣어 t_A의 상태를 맞추는 방법", "그동안 SN은 1.1 V로 고정. 대리 수단이며 논문의 정공 출처를 설명하지 않음"),
 ("구조 일치 검사", "실행 전 구조를 논문과 대조하는 단계 (tools/gt_start.sh)", "오늘 배치 6개 모두 통과 후 시작. 치수, 스페이서 25 nm, 접합 50.00 / 175.00 nm"),
 ("점수", "(시뮬레이션 − 논문) ÷ 허용오차의 제곱평균제곱근", "허용오차: 문턱 0.02 V, 쓰기 0.03 V, 몸체 상승 30 mV, 손실 0.3 decade. 1 미만 = 판독 오차 안"),
 ("2D / 3D", "단면 모델 / 입체 모델", "3D는 구조 점검까지 끝내고 중지. 실행 중인 3D 없음 (7건 10:35, 2건 13:57 중단)"),
]
ANALOGY = ["물통", "손잡이", "구슬", "수도관", "그림책", "방바닥", "딸깍", "눈금", "납작한", "입체 집", "작은 집"]

def check_text():
    body = [s for sec in SEC for s in sec[4]]; every = body + [q for sec in SEC if sec[5] for q in sec[5]] + [x for sec in SEC for x in (sec[1], sec[3]) if x] + [x for row in RESULT + TERM for x in row]
    left = [(w, s) for s in every for w in ANALOGY if w in s]; avg = sum(len(re.sub(r"<[^>]+>", "", s).split()) for s in body) / len(body)
    assert not left, left
    assert avg <= 10, avg
    return len(body), avg

def html(img):
    b64 = lambda f: "data:image/png;base64," + base64.b64encode(open(f, "rb").read()).decode()
    chip = {"한 줄로": "#1e88e5", "기본부터": "#8e24aa", "조금 더": "#43a047", "그래서?": "#f4511e"}; out = []
    for lab, head, key, cap, sents, qs in SEC:
        out.append(f'<section><h2><span class="chip" style="background:{chip[lab]}">{lab}</span>{head}</h2>')
        if key: out.append(f'<figure><img src="{b64(img[key])}" alt="{cap}"><figcaption>{cap}</figcaption></figure>')
        out.append('<p class="easy">' + "<br>".join(sents) + "</p>")
        if qs: out.append('<ol class="easy">' + "".join(f"<li>{q}</li>" for q in qs) + "</ol>")
        out.append("</section>")
    tab = lambda rows: "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cho 외 (IRPS 2026) 소자 재현 현황</title>
<style>
 body {{ font-family: "Malgun Gothic", "맑은 고딕", "Apple SD Gothic Neo", sans-serif; background: #fffdf7; color: #263238; margin: 0; }}
 main {{ max-width: 960px; margin: 0 auto; padding: 24px 16px 60px; }}
 h1 {{ font-size: 28px; margin: 8px 0 4px; }} .meta {{ color: #78909c; font-size: 14px; margin-bottom: 18px; }}
 section {{ background: #fff; border: 1px solid #eceff1; border-radius: 16px; padding: 18px 22px; margin: 18px 0; box-shadow: 0 1px 3px rgba(0,0,0,.05); }}
 h2 {{ font-size: 21px; margin: 2px 0 12px; }} .chip {{ color: #fff; font-size: 14px; border-radius: 999px; padding: 4px 12px; margin-right: 10px; vertical-align: 3px; }}
 p.easy, ol.easy {{ font-size: 18px; line-height: 1.85; margin: 10px 0 2px; }} ol.easy {{ padding-left: 28px; }}
 figure {{ margin: 6px 0 10px; }} img {{ max-width: 100%; height: auto; border-radius: 10px; }} figcaption {{ color: #607d8b; font-size: 14px; margin-top: 4px; }}
 .ref {{ background: #f5f7f8; }} .ref h2 {{ font-size: 19px; }} .ref p {{ font-size: 14.5px; line-height: 1.7; color: #455a64; }}
 .wrap {{ overflow-x: auto; }} table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; }}
 th, td {{ border: 1px solid #cfd8dc; padding: 6px 9px; vertical-align: top; text-align: left; }} th {{ background: #37474f; color: #fff; }}
 td:first-child {{ font-weight: bold; white-space: nowrap; }}
</style></head><body><main>
<h1>Cho 외 (IRPS 2026) 소자 재현, 어디까지 왔을까요?</h1>
<div class="meta">2026년 10월 6일 · 2D 단면 모델 기준 · 쉬운 문장으로 쓰되 용어는 실제 용어 그대로 · 대상 논문: "Row Hammer Effect and Floating Body Effect of Monolithic 3D Stackable 1T1C DRAM"</div>
{"".join(out)}
<section class="ref"><h2>숫자 한눈에: 논문과 최종 2D 구성</h2>
<p>Case 1~5 순서예요. 논문 값은 그림에서 읽은 수치예요. 점수가 1보다 작으면 그림 판독 오차 안이에요.</p>
<div class="wrap"><table><tr><th>논문 그림</th><th>비교한 값</th><th>논문</th><th>최종 2D 구성</th><th>점수</th></tr>{tab(RESULT)}</table></div></section>
<section class="ref"><h2>용어 풀이</h2>
<p>본문에 나온 용어의 뜻과, 이 작업에서 쓴 값·근거예요. 라운드별 실험과 채택·기각 내용은 같은 폴더의
<b>GT_IRPS2026_2D_소자완성_보고_2026-10-06.md</b>와 <b>GT_IRPS2026_논문대비_비교표_2026-10-06.xlsx</b>에 있어요.</p>
<div class="wrap"><table><tr><th>용어</th><th>쉬운 뜻</th><th>이 작업에서의 값·근거</th></tr>{tab(TERM)}</table></div></section>
</main></body></html>
"""

if __name__ == "__main__":
    n, avg = check_text()
    RF = {c: run("fin", c) for c in range(1, 6)}; R1 = {c: run("h1", c) for c in range(1, 6)}
    img = dict(map=fig_map(), cell=fig_cell(), score=fig_score(), holes=fig_holes(R1, RF), loss=fig_loss(RF), rh=fig_rh())
    open(OUT, "w", encoding="utf-8", newline="\n").write(html(img))
    print(f"text: {n} sentences, {avg:.1f} units per sentence, no analogy word"); print("\n".join(img.values())); print(OUT, os.path.getsize(OUT) // 1024, "kB")
