# plot_rh_history.py [out.png] - round 15 in one picture: the row hammer with the history that charges the victim's body.
# Left: loss of the storage node per aggressor cycle (log scale), paper against the model without history, with the history
# (16.2 us, 100 us) and the idle controls (aggressor WL at 0 V). Middle: Z-Z' with impact ionization, node against time: the
# paper's steps (read off Fig.7(a), typed in) against the model (flat). Right: the victim's body potential over the first
# aggressor pulse, Fig.7(e) against the model. Numbers typed in from tools/gt_rh_hist.py -c and tools/gt_rh_body.py (NOTES (bl)).
# Run on the PC: python tools/plot_rh_history.py
import sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\LEEJINSEOK\Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram\gt2d_rh_history_round15.png"
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
INK = "#263238"; PAP = "#c62828"; MOD = "#1565c0"; IDL = "#90a4ae"
fig, ax = plt.subplots(1, 3, figsize=(20, 6.6), gridspec_kw=dict(width_ratios=[1.35, 1, 0.85]))

a = ax[0]
rows = [("Y–Y'\n논문", 0.0535, PAP), ("Y–Y'\n이력 없음", 0.00144, MOD), ("Y–Y'\n16.2 µs 이력", 0.00115, MOD), ("Y–Y'\n대조군\n(공격 WL 0 V)", 0.00115, IDL),
        ("Y–Y'\n100 µs 이력", 0.00019, MOD), ("Y–Y'\n100 µs 대조군", 0.00019, IDL), ("Z–Z'\n논문", 0.0100, PAP), ("Z–Z'\n이력 없음\n(마지막 5사이클)", 0.00144, MOD),
        ("Z–Z'\n16.2 µs 이력", 0.00115, MOD), ("Z–Z'\n100 µs 이력", 0.00020, MOD)]
x = list(range(len(rows)))
a.bar(x, [r[1] for r in rows], color=[r[2] for r in rows], width=0.68)
for i, r in enumerate(rows): a.text(i, r[1] * 1.18, f"{r[1]:.5f}".rstrip("0"), ha="center", fontsize=9.5, color=INK)
a.set_yscale("log"); a.set_ylim(1e-4, 0.2); a.set_yticks([1e-4, 1e-3, 1e-2, 1e-1]); a.set_yticklabels(["0.0001", "0.001", "0.01", "0.1"]); a.minorticks_off(); a.set_xticks(x); a.set_xticklabels([r[0] for r in rows], fontsize=8.8)
a.set_ylabel("저장 노드 손실 [mV / 사이클]", fontsize=11.5); a.grid(alpha=0.25, axis="y"); a.axvline(5.5, color=INK, lw=0.8, ls=":")
a.set_title("① 충돌 이온화 끔 (Fig. 6(e)): 이력을 넣어도 손실은 대조군과 같아요", fontsize=12.5, fontweight="bold", color=INK)
a.text(0.40, 0.80, "남는 손실은 저장 노드 접합의 터널링 누설(11 pA)이에요.\n몸체가 더 차면 오히려 줄어요 (100 µs: 1.8 pA).", transform=a.transAxes, fontsize=10.2, color=INK,
       bbox=dict(fc="#eceff1", ec=IDL, lw=1))

b = ax[1]
tp = [0.0, 0.285, 0.30, 0.40, 0.50, 0.60, 0.71, 0.80, 0.91, 1.00, 1.10, 1.20, 1.30, 1.40, 1.50, 2.0]
vp = [1.10, 1.10, 1.07, 1.07, 0.95, 0.94, 0.83, 0.82, 0.74, 0.74, 0.67, 0.67, 0.61, 0.61, 0.585, 0.585]
b.plot(tp, vp, color=PAP, lw=2.2, marker="o", ms=4, label="논문 Fig. 7(a) (그림에서 읽은 값)")
tm = [0.188 * i for i in range(11)]
b.plot(tm, [1.1] * 11, color=MOD, lw=2.2, marker="s", ms=4, label="모델: 이력 없음 / 16.2 µs / 100 µs\n(10사이클 동안 변화 0.04 mV 이하)")
for i in range(10): b.axvspan(0.188 * i, 0.188 * i + 0.094, color="#fff3e0", zorder=0)
b.set_xlim(0, 2.0); b.set_ylim(0.4, 1.2); b.set_xlabel("시간 [ns]  (연한 띠: 공격 WL이 1.8 V인 구간)", fontsize=11); b.set_ylabel("저장 노드 전압 [V]", fontsize=11.5)
b.legend(fontsize=9.8, loc="lower left"); b.grid(alpha=0.25)
b.set_title("② Z–Z', 충돌 이온화 켬 (Fig. 7(a)): 붕괴가 없어요", fontsize=12.5, fontweight="bold", color=INK)

c = ax[2]
lab = ["끔 · 부유", "켬 · 부유", "켬 · 접지"]; pap = [2.4, 665.1, 1.8]; mod = [0.05, 0.05, 0.05]; modt = ["0.0", "0.0", "0.0"]
xx = [0, 1, 2]
c.bar([i - 0.2 for i in xx], pap, width=0.38, color=PAP, label="논문 Fig. 7(e)")
c.bar([i + 0.2 for i in xx], mod, width=0.38, color=MOD, label="모델 (이상적 WL)")
for i in xx:
    c.text(i - 0.2, pap[i] * 1.2, f"{pap[i]:g}", ha="center", fontsize=10.5, color=INK); c.text(i + 0.2, mod[i] * 1.2, modt[i], ha="center", fontsize=10.5, color=INK)
c.set_yscale("log"); c.set_ylim(0.03, 3000); c.set_yticks([0.1, 1, 10, 100, 1000]); c.set_yticklabels(["0.1", "1", "10", "100", "1000"]); c.minorticks_off(); c.set_xticks(xx); c.set_xticklabels(lab, fontsize=10.5); c.set_ylabel("첫 공격 펄스 동안 몸체 전위 변화 [mV]", fontsize=11)
c.legend(fontsize=9.8, loc="upper right"); c.grid(alpha=0.25, axis="y")
c.set_title("③ 첫 펄스(0.09 ns) 동안의 몸체 전위", fontsize=12.5, fontweight="bold", color=INK)
c.text(0.03, 0.70, "저항 200 kΩ를 넣으면 모델도\n끔 · 부유가 +4.3 mV예요.\n665 mV는 나오지 않아요.", transform=c.transAxes, fontsize=10, color=INK, bbox=dict(fc="#eceff1", ec=IDL, lw=1))
for q in ax:
    for sp in ("top", "right"): q.spines[sp].set_visible(False)
fig.suptitle("라운드 15: Fig. 8의 정공 전하를 만드는 이력(자체 생성 16.2 µs, 100 µs)을 로우 해머에 넣은 결과 (Case 2, 2D)", fontsize=15, fontweight="bold", color=INK)
fig.tight_layout(); fig.savefig(OUT, dpi=125, bbox_inches="tight", facecolor="white"); print(OUT)
