# gt_write_cause.py [out.png] - why the write curve of Fig.4(a) does not come out with the text's 4.2 fF (user question,
# 2026-10-06). Case 2. Run on the PC (needs runs/Db0W_c2, DcsW_c2 *_sys.plt and runs/DfinI_c2/IdVg_*.plt from the server).
# Three things are put side by side:
#   1. the paper's write curve: storage node 0.72 / 0.92 / 1.06 / 1.13 V at 12 / 24 / 39 / 60 ps after the WL edge;
#   2. the model's write curve with 4.2 fF and with 1.8 fF, and the charging current C dV/dt against the node voltage
#      (if it is the same for both capacitors, the transistor alone sets the speed and time simply scales with C);
#   3. a bound that does not use the model at all: the paper's own Id-Vg of Fig.5(c) (digitized pixels) as the charging
#      current, I <= Id(Vg = Vpp - V_SN) (source follower: the real current is lower, Vds shrinks as the node rises),
#      taken from the highest of the four WF 4.7 curves at each Vg. t >= C * integral dV / I.
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paper_targets as P                      # sets the width for gt_fig5c
import gt_fig5c as G
from gt_tran import load, at, edges
HERE = os.path.dirname(os.path.abspath(__file__)); RUNS = os.path.join(HERE, "..", "runs")
PAPER = [(12, 0.72), (24, 0.92), (39, 1.06), (60, 1.13)]; VPP = 1.8

def paper_iv():                               # per case: sorted (Vg, log10 I), median of the pixels in 0.03 V bins
    pix = json.load(open(os.path.join(HERE, "..", "preview", "cho_fig5c_pixels.json"))); out = {}
    for k, pts in pix.items():
        bins = {}
        for x, y in pts: bins.setdefault(round((-1 + (x - 990.0) / 81.83) / 0.03), []).append(-4 - (y - 420.5) / 15.25)
        b = [(i * 0.03, sorted(v)[len(v) // 2]) for i, v in sorted(bins.items())]
        out[int(k[1])] = [q for j, q in enumerate(b) if j in (0, len(b) - 1) or abs(q[1] - (b[j - 1][1] + (b[j + 1][1] - b[j - 1][1]) * (q[0] - b[j - 1][0]) / (b[j + 1][0] - b[j - 1][0]))) < 0.7]
    return out

def interp(curve, v):                         # log-linear in between, flat beyond the ends
    if v <= curve[0][0]: return curve[0][1]
    if v >= curve[-1][0]: return curve[-1][1]
    for (a, la), (b, lb) in zip(curve, curve[1:]):
        if a <= v <= b: return la + (lb - la) * (v - a) / ((b - a) or 1)

def write_run(rid, cs):
    s = load(os.path.join(RUNS, rid, rid + "_sys.plt")); t = s["time"]; k = lambda n: next(x for x in s if n in x); sn, wl = s[k("nSN)")], s[k("nWL)")]
    te = edges(t, wl, 0, VPP, True)[0]; tf = edges(t, wl, 0, VPP, False)[0]; i = [j for j, x in enumerate(t) if te - 4e-12 <= x <= tf - 2e-12]
    tt = [(t[j] - te) * 1e12 for j in i]; vv = [sn[j] for j in i]
    q = [j for j in range(1, len(tt) - 3) if tt[j - 1] >= 3.0]          # from 3 ps after the edge: the WL is at Vpp, no coupling kick in dV/dt
    return dict(t=tt, v=vv, vi=[vv[j] for j in q], i=[cs * (vv[j + 1] - vv[j - 1]) / ((tt[j + 1] - tt[j - 1]) * 1e-12) for j in q], cs=cs)

def t_at(r, v):                               # time [ps after the WL edge] at which the node passes v
    for j in range(1, len(r["t"])):
        if r["v"][j - 1] < v <= r["v"][j]: return r["t"][j - 1] + (r["t"][j] - r["t"][j - 1]) * (v - r["v"][j - 1]) / (r["v"][j] - r["v"][j - 1])

def i_at(r, v):
    for j in range(1, len(r["vi"])):
        if r["vi"][j - 1] < v <= r["vi"][j]: return r["i"][j - 1] + (r["i"][j] - r["i"][j - 1]) * (v - r["vi"][j - 1]) / (r["vi"][j] - r["vi"][j - 1])

if __name__ == "__main__":
    iv = paper_iv(); env = lambda vg: max(interp(iv[c], vg) for c in (1, 2, 3, 4))            # highest of the WF 4.7 curves
    mod = G.curve(os.path.join(RUNS, "DfinI_c2")); m_at = lambda vg: G.at(mod, min(vg, mod[-1][0] - 1e-6))      # flat beyond the last point (1.79 V)
    print("on-current at Vd = 1.1 V [uA]:   Vg     paper Case 2   paper, highest of Cases 1-4   model Case 2 (width 0.1 um)")
    for vg in (1.0, 1.2, 1.4, 1.6, 1.75):
        print(f"                                 {vg:4.2f}   {10 ** interp(iv[2], vg) * 1e6:8.0f}       {10 ** env(vg) * 1e6:8.0f}                      {10 ** m_at(vg) * 1e6:8.0f}")
    print(f"  (paper Case 2 pixels end at Vg = {iv[2][-1][0]:.2f} V; between {[q[0] for q in iv[2] if q[0] > 0.6][0]:.2f} and 1.6 V the curve lies under others and is interpolated)")
    a, b = write_run("Db0W_c2", 4.2e-15), write_run("DcsW_c2", 1.8e-15)
    print("\nmodel write curve, Case 2: time after the WL edge [ps] and charging current C dV/dt [uA] at a node voltage")
    print("   V_SN [V]   t (4.2 fF)   t (1.8 fF)   ratio   | I (4.2 fF)   I (1.8 fF)   | paper Id(Vg = 1.8 - V_SN), highest curve")
    for v in (0.5, 0.6, 0.72, 0.8, 0.92, 1.0):
        ta, tb, ia, ib = t_at(a, v), t_at(b, v), i_at(a, v), i_at(b, v)
        ua = lambda x: "       -" if x is None else f"{x * 1e6:8.0f}"       # no current value inside the first 3 ps
        print(f"   {v:5.2f}     {ta:8.1f}     {tb:8.1f}    {ta / tb:5.2f}   | {ua(ia)}     {ua(ib)}     | {10 ** env(VPP - v) * 1e6:8.0f}")
    print(f"   capacitor ratio 4.2 / 1.8 = {4.2 / 1.8:.2f}")
    def bound(cs, v, cur=None, n=400):        # shortest time to v if an Id-Vg curve (log10 A against Vg) were the charging current
        cur = cur or env; return cs * sum((v / n) / 10 ** cur(VPP - (k + 0.5) * v / n) for k in range(n)) * 1e12
    imax = 10 ** interp(iv[2], 1.75)
    print(f"\nsimplest check: the largest current of Case 2 in Fig.5(c) is {imax * 1e6:.0f} uA (Vg 1.6 .. 1.75 V). Held for 12 ps it moves a 4.2 fF node by"
          f" {imax * 12e-12 / 4.2e-15:.2f} V; Fig.4(a) shows 0.72 V. A 4.2 fF node needs {4.2e-15 * 0.72 / 12e-12 * 1e6:.0f} uA on average over those 12 ps, a 1.8 fF node {1.8e-15 * 0.72 / 12e-12 * 1e6:.0f} uA.")
    print("\npaper's write curve against the two capacitors (time after the WL edge [ps] to reach the voltage)")
    print("   V_SN [V]   paper | model 4.2 fF   model 1.8 fF | shortest possible at 4.2 fF if the current were Id(Vg = 1.8 - V_SN) of Fig.5(c):")
    print("                                                   highest paper curve   Case 2 (model curve)   | largest C these two allow [fF]")
    for tp, v in PAPER:
        print(f"   {v:5.2f}     {tp:5.0f} | {t_at(a, v) or float('nan'):8.1f}       {t_at(b, v) or float('nan'):8.1f}     | {bound(4.2e-15, v):12.1f}          {bound(4.2e-15, v, m_at):12.1f}          | {tp / bound(1e-15, v):6.2f}   {tp / bound(1e-15, v, m_at):6.2f}")
    print("   (these bounds take the full saturation current at Vgs = Vpp - V_SN and a WL that is at Vpp at once; the real")
    print("    source-follower current is lower because Vds shrinks as the node rises: see the current columns above)")
    eps = 3.9 * 8.854e-12 / 3.8e-10            # F/m^2 at EOT 3.8 A (Fig.5(a))
    print(f"\ncapacitor of Fig.5(a): EOT 3.8 A -> {eps * 1e3:.1f} fF/um^2. 4.2 fF = {4.2e-15 / eps * 1e12:.4f} um^2; 1.8 fF = {1.8e-15 / eps * 1e12:.4f} um^2;"
          f" two faces of L_CAP 100 nm x 100 nm = 0.0200 um^2 = {eps * 0.02e-12 * 1e15:.2f} fF")
    if len(sys.argv) > 1:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
        fig, ax = plt.subplots(1, 2, figsize=(15, 5.6))
        ax[0].plot(a["t"], a["v"], color="#d32f2f", lw=2.2, label="2D 모델, 저장 노드 4.2 fF (본문 값)"); ax[0].plot(b["t"], b["v"], color="#1976d2", lw=2.2, label="2D 모델, 저장 노드 1.8 fF")
        vs = [0.02 * k for k in range(1, 58)]; ax[0].plot([bound(4.2e-15, v) for v in vs], vs, "--", color="#d32f2f", lw=1.6, label="4.2 fF일 때 가능한 가장 빠른 충전\n(논문 Fig. 5(c)의 Id–Vg를 충전 전류로 쓴 상한)")
        ax[0].plot([p[0] for p in PAPER], [p[1] for p in PAPER], "o", mfc="white", color="#263238", ms=9, mew=2.2, label="논문 Fig. 4(a) (그림 판독)")
        ax[0].set_xlim(-3, 100); ax[0].set_ylim(0, 1.25); ax[0].set_xlabel("WL 상승 뒤 시간 [ps]", fontsize=13); ax[0].set_ylabel("저장 노드 전압 [V]", fontsize=13)
        ax[0].set_title("쓰기 곡선: 4.2 fF로는 논문의 속도가 나오지 않음", fontsize=14, fontweight="bold"); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=10.5, loc="lower right")
        ax[1].plot(a["vi"], [x * 1e6 for x in a["i"]], color="#d32f2f", lw=2.2, label="2D 모델의 충전 전류, 4.2 fF"); ax[1].plot(b["vi"], [x * 1e6 for x in b["i"]], color="#1976d2", lw=2.2, label="2D 모델의 충전 전류, 1.8 fF")
        ax[1].plot(vs, [10 ** env(VPP - v) * 1e6 for v in vs], "--", color="#546e7a", lw=1.8, label="논문 Fig. 5(c): Id(Vg = 1.8 V − V_SN), Vd 1.1 V (상한)")
        seg = [(0.0, 0.0)] + [(t_, v_) for t_, v_ in PAPER]
        for (t1, v1), (t2, v2) in zip(seg, seg[1:]):
            for cs, col in ((4.2e-15, "#d32f2f"), (1.8e-15, "#1976d2")):
                ax[1].plot([v1, v2], [cs * (v2 - v1) / ((t2 - t1) * 1e-12) * 1e6] * 2, color=col, lw=5, alpha=0.3, solid_capstyle="butt")
        ax[1].plot([], [], color="#d32f2f", lw=5, alpha=0.3, label="논문 곡선에 필요한 평균 전류, 4.2 fF라면"); ax[1].plot([], [], color="#1976d2", lw=5, alpha=0.3, label="논문 곡선에 필요한 평균 전류, 1.8 fF라면")
        ax[1].set_xlim(0, 1.15); ax[1].set_ylim(0, 280); ax[1].set_xlabel("저장 노드 전압 V_SN [V]", fontsize=13); ax[1].set_ylabel("충전 전류 I = C·dV/dt [µA]", fontsize=13)
        ax[1].set_title("충전 전류: 트랜지스터가 낼 수 있는 값과 필요한 값", fontsize=14, fontweight="bold"); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=10, loc="upper right")
        fig.suptitle("Fig. 4(a) 쓰기 곡선과 저장 노드 용량 (Case 2, WL 1.8 V, BL 1.168 V)", fontsize=15, fontweight="bold"); fig.tight_layout(); fig.savefig(sys.argv[1], dpi=130); print("saved", sys.argv[1])
