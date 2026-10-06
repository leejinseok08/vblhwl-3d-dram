# gt_fig4a.py <out.png> <run dir> ... : write curves (storage node against time) over the curve of Fig.4(a) of Cho et al.
# The paper's curve is read from the embedded image (frame 0 .. 3 V = rows 276 .. 79, 2.0 px per ps from column 1204.5;
# about +-0.02 V, +-1 ps). Prints, for each run, the rms difference with the best common time shift (edge times are not given).
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at

PAPER = [(15.25, 0.213), (18.25, 0.442), (21.25, 0.548), (24.25, 0.647), (27.25, 0.716), (33.25, 0.845), (36.25, 0.891), (39.25, 0.921),
         (42.25, 0.952), (48.25, 1.013), (51.25, 1.035), (54.25, 1.058), (60.25, 1.089), (63.25, 1.096), (66.25, 1.104), (69.25, 1.119), (75.25, 1.127)]
PBL = 1.168          # bit-line level of the paper's write, same reading

if __name__ == "__main__":
    out = sys.argv[1]; curves = []
    for rd in sys.argv[2:]:
        rid = os.path.basename(rd.rstrip("/")); s = load(os.path.join(rd, rid + "_sys.plt"))
        t = [x * 1e12 for x in s["time"]]; v = s[next(k for k in s if "nSN)" in k)]
        cs = re.search(r"capacitance = ([\d.e+-]+)", open(os.path.join(rd, rid + "_des.cmd"), encoding="utf-8").read()).group(1)
        best = min(((sum((at(t, v, tp - d) - vp) ** 2 for tp, vp in PAPER) / len(PAPER)) ** 0.5, d) for d in [x * 0.25 for x in range(-24, 25)])
        rms0 = (sum((at(t, v, tp) - vp) ** 2 for tp, vp in PAPER) / len(PAPER)) ** 0.5
        print(f"{rid:10s} Cs {float(cs) * 1e15:.1f} fF: rms {rms0 * 1e3:5.1f} mV as run; {best[0] * 1e3:5.1f} mV with our curve moved by {best[1]:+.2f} ps; "
              f"SN at 24.25 / 39.25 / 54.25 / 75.25 ps: " + " / ".join(f"{at(t, v, x):.3f}" for x in (24.25, 39.25, 54.25, 75.25)) + f"; end {v[-1]:.3f} V")
        curves.append((float(cs) * 1e15, t, v, best[1]))
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = ["DejaVu Sans", "Malgun Gothic"]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot([p[0] for p in PAPER], [p[1] for p in PAPER], "ko", ms=5, label="논문 Fig. 4(a) (baseline, 그림 판독)")
    ax.axhline(PBL, color="r", ls=":", lw=1); ax.text(100, PBL + 0.015, f"논문의 BL {PBL} V", color="r", fontsize=8)
    for (cs, t, v, d), c in zip(curves, ("#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b")):
        ax.plot(t, v, "-", color=c, lw=1.4, label=f"TCAD, Cs {cs:.1f} fF")
    ax.set(xlim=(0, 125), ylim=(0, 1.3), xlabel="시간 [ps]", ylabel="저장 노드 전압 [V]", title="쓰기: 저장 노드 충전 (BL 1.168 V, WL 1.8 V)")
    ax.grid(alpha=0.3); ax.legend(fontsize=8, loc="lower right"); fig.tight_layout(); fig.savefig(out, dpi=150); print("wrote", out)
