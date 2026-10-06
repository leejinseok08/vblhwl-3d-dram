# plot_charged_t0.py [out.png] - the hypothesis "the body is already charged at t = 0 of Fig.8, storage node at 1.1 V" in one picture.
# Left: loss of the first BL-low phase over the body rise at t_A, Cases 1 - 4: the stand-in states Dh1F .. Dh4F (line), the states
# charged by the model's own generation (Codex's runs, open squares; GT_CODEX = folder with its results/*.json), and the paper's
# pair (bar of Fig.8(a), first-phase loss of Fig.8(b), (c)) as a star. The star lies left of the line: the arrow is the body rise
# that is missing. Right: storage-node loss over time for Case 1, charge x 1.0 / 1.25 / 1.5 and the state interpolated to the
# paper's first-phase loss, against the points read from Fig.8(b). Run on the PC: python tools/plot_charged_t0.py
import sys, os, glob, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or r"C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs"
CX = os.environ.get("GT_CODEX", "")
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram\gt2d_charged_t0_check.png"
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
COL = {1: "#d32f2f", 2: "#c2185b", 3: "#1976d2", 4: "#f57c00"}; INK = "#263238"
NAME = {1: "Case 1 (30 nm)", 2: "Case 2 (20 nm)", 3: "Case 3 (10 nm, 1e18)", 4: "Case 4 (10 nm, 1e16)"}
TAGS = (("Dh1F", 1.0), ("Dh2F", 1.25), ("Dh3F", 1.5), ("Dh4F", 2.0))

def run(rid):
    d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; T = dv["time"]
    q = next(x for x in dv if x.startswith("Pos(0.125") and "ElectrostaticPotential" in x)
    f = edges(t, s[k("nBL")], 0, 1.1, False); r = [x for x in edges(t, s[k("nBL")], 0, 1.1, True) if x > f[0]]; tA = f[0] - 3e-10
    tau = [(x - f[0] + 0.25e-9) * 1e9 + 21.0 for x in t]                       # the paper's axis: the first BL fall starts at 21.0 ns
    return dict(rise=(at(T, dv[q], tA) - dv[q][0]) * 1e3, first=(at(t, sn, tA) - at(t, sn, r[0] - 3e-10)) * 1e3, tau=tau, loss=[(at(t, sn, tA) - x) * 1e3 for x in sn])

D = {c: [run(f"{tag}_c{c}") for tag, _ in TAGS] for c in range(1, 5)}
fig, ax = plt.subplots(1, 2, figsize=(17.5, 6.6), gridspec_kw=dict(width_ratios=[1.15, 1]))
a = ax[0]
for c in range(1, 5):
    x = [o["rise"] for o in D[c]]; y = [o["first"] for o in D[c]]
    a.plot(x, y, "-o", color=COL[c], lw=2.3, ms=7, label=f"2D 모델, {NAME[c]}: 정공을 넣어 둔 상태 (×1 / 1.25 / 1.5 / 2)")
    i = next(k for k in range(3) if y[k] <= P.FBE_FIRST[c] <= y[k + 1]); w = (math.log(P.FBE_FIRST[c]) - math.log(y[i])) / (math.log(y[i + 1]) - math.log(y[i]))
    xm = x[i] * (1 - w) + x[i + 1] * w
    a.plot([P.FBE_RISE[c]], [P.FBE_FIRST[c]], "*", color=COL[c], ms=21, mec=INK, mew=1.0, zorder=5)
    a.annotate("", xy=(xm - 3, P.FBE_FIRST[c]), xytext=(P.FBE_RISE[c] + 9, P.FBE_FIRST[c]), arrowprops=dict(arrowstyle="->", color=COL[c], lw=1.8, ls="--"))
    a.text((P.FBE_RISE[c] + xm) / 2, P.FBE_FIRST[c] * 1.16, f"+{xm - P.FBE_RISE[c]:.0f} mV", color=COL[c], fontsize=12, ha="center", fontweight="bold")
if os.path.isdir(CX):
    for f_ in glob.glob(os.path.join(CX, "*.json")):
        d = json.load(open(f_, encoding="utf-8"))
        if d["preparation"] == "natural" and d["II"] == 1 and d["Cs_basis"] == "write_fit" and d["hold_ns"] > 1000 and d["case"] in COL:
            a.plot([d["prefall"]["body_rise_eq_mV"]], [d["first_low"]["SN_loss_mV"]], "s", mfc="white", mec=COL[d["case"]], mew=2.0, ms=9, zorder=4)
    a.plot([], [], "s", mfc="white", mec=INK, mew=2.0, ms=9, label="모델의 자체 생성으로 충전한 상태 (Codex 실행: 유지 15.2 µs / 21 µs)")
a.plot([], [], "*", color="#9e9e9e", ms=18, mec=INK, label="논문: (Fig. 8(a) 막대, Fig. 8(b), (c) 첫 구간 손실)")
a.set_yscale("log"); a.set_xlim(270, 800); a.set_ylim(0.25, 400); a.set_yticks([0.3, 1, 3, 10, 30, 100, 300]); a.set_yticklabels(["0.3", "1", "3", "10", "30", "100", "300"], fontsize=11)
a.set_xlabel("t_A의 몸체 중심 전위 상승 [mV] (과도 해석 시작 대비)", fontsize=12.5); a.set_ylabel("첫 BL 저전위 구간(10.5 ns)의 저장 노드 손실 [mV]", fontsize=12.5)
a.grid(alpha=0.25, which="both"); a.minorticks_off(); a.legend(fontsize=9.3, loc="lower right")
a.set_title("논문의 손실이 나오려면 몸체가 막대보다 43~98 mV 높아야 해요", fontsize=14.5, fontweight="bold", color=INK)
a.text(278, 250, "Case 5 (WF 5.0)는 그리지 않았어요:\n모델 0.13 mV, 논문 0 mV로 맞아요", fontsize=10.5, color=INK, va="top")
b = ax[1]
o1, o2, o3 = D[1][0], D[1][1], D[1][2]; w = (math.log(P.FBE_FIRST[1]) - math.log(o2["first"])) / (math.log(o3["first"]) - math.log(o2["first"]))
for o in (o1, o2, o3): o["tau"], o["loss"] = zip(*[(x, y) for x, y in zip(o["tau"], o["loss"]) if x >= 1.0])      # without the write
b.plot(o1["tau"], o1["loss"], color="#ef9a9a", lw=2.0, label=f"모델, 막대 전하 ×1.0 (몸체 +{o1['rise']:.0f} mV)")
b.plot(o2["tau"], o2["loss"], color="#e57373", lw=2.0, label=f"모델, ×1.25 (몸체 +{o2['rise']:.0f} mV)")
b.plot(o3["tau"], o3["loss"], color="#b71c1c", lw=2.0, label=f"모델, ×1.5 (몸체 +{o3['rise']:.0f} mV)")
ti = [x for x in o2["tau"] if 1.0 <= x <= 205]; yi = lambda o, x: max(at(o["tau"], o["loss"], x), 1e-3)
b.plot(ti, [math.exp(math.log(yi(o2, x)) * (1 - w) + math.log(yi(o3, x)) * w) for x in ti], color=INK, lw=2.6, ls="--",
       label=f"모델, 첫 구간 손실을 논문에 맞춘 상태 (보간, 몸체 +{o2['rise'] * (1 - w) + o3['rise'] * w:.0f} mV)")
b.plot([26, 31.5, 52.5, 73.5, 94.5, 200], [43, 55, 67, 76, 83, 100], "*", color="#fbc02d", ms=19, mec=INK, mew=1.0, zorder=5, label="논문 Fig. 8(b) Case 1 (그림 판독값)")
b.set_xlim(0, 205); b.set_ylim(-5, 175); b.set_xlabel("시간 [ns] (논문 축: 첫 BL 하강 21.0 ns, 주기 21 ns)", fontsize=12.5); b.set_ylabel("Case 1 저장 노드 손실 [mV] (t_A 기준)", fontsize=12.5)
b.grid(alpha=0.25); b.legend(fontsize=9.6, loc="upper left")
b.set_title("Case 1: 첫 계단을 맞추면 뒤 계단이 논문의 약 2배예요", fontsize=14.5, fontweight="bold", color=INK)
for s_ in (a, b):
    for sp in ("top", "right"): s_.spines[sp].set_visible(False)
fig.suptitle("가설 점검: Fig. 8의 t = 0에 몸체가 이미 충전돼 있고 저장 노드가 1.1 V라면", fontsize=16.5, fontweight="bold", color=INK)
fig.tight_layout(); fig.savefig(OUT, dpi=125, bbox_inches="tight", facecolor="white"); print(OUT)
