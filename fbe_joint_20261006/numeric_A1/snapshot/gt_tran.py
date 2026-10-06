# gt_tran.py <run dir> ... : the Cho transient runs (deck_cho) in numbers, for the comparison with Figs.4, 6, 7, 8 of the paper.
# Reads <run>_sys.plt (node voltages) and c1_<run>_dev.plt (probes in the body). Works on running jobs (unfinished files).
#   W  : storage node at 12 / 24 / 39 / 60 ps after the WL edge (paper Fig.4(a): 0.72 / 0.92 / 1.06 / 1.13 V at a BL of 1.16 V)
#   FBE: storage node after the write and after each BL period
#   RH : storage node 20 ps before each aggressor edge, loss per cycle (straight line through the last periods)
#   probes: every potential probe of the device file at the instants that could be the paper's "t = 0" and "t = t_A"
import sys, os, re, glob, math


def load(f):
    txt = open(f, errors="replace").read()
    names = re.findall(r'"([^"]*)"', re.search(r"datasets\s*=\s*\[(.*?)\]", txt, re.S).group(1))
    nums = [float(x) for x in re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", txt[txt.index("Data"):])]
    n = len(names); rows = [nums[i:i + n] for i in range(0, len(nums) - len(nums) % n, n)]
    return {k: [r[j] for r in rows] for j, k in enumerate(names)}


def at(t, v, x):
    if x <= t[0]: return v[0]
    for i in range(1, len(t)):
        if t[i - 1] <= x <= t[i]: return v[i - 1] + (v[i] - v[i - 1]) * (x - t[i - 1]) / ((t[i] - t[i - 1]) or 1)
    return v[-1]


def edges(t, v, lo, hi, rising):          # times where v passes the middle of lo..hi
    m = (lo + hi) / 2; out = []
    for i in range(1, len(t)):
        if (v[i - 1] < m <= v[i]) if rising else (v[i - 1] > m >= v[i]): out.append(t[i])
    return out


# Paper, Fig.8: SN loss [mV] at the end of the low phases 1..8, at 200 ns, and the body potential rise of Fig.8(a).
# Cases 1, 2 from the pixels of Fig.8(b) (5.75 mV per pixel row, start level row 115.0: +-3 mV); Cases 3-5 from the zoom of Fig.8(c).
PAPER_FBE = {1: ([55, 67, 76, 83, 87, 93, 98, 101], 100, 555), 2: ([29, 34, 38, 40, 43, 45, 46, 49], 50, 445),
             3: ([], 14, 365), 4: ([], 7, 320), 5: ([], 1, 368)}


def probes(rd, marks):                    # marks = [(label, time)]
    d = glob.glob(os.path.join(rd, "*_dev.plt"))
    if not d: return
    try: dv = load(d[0])
    except Exception: return
    cols = [k for k in dv if "ElectrostaticPotential" in k or "hQuasiFermi" in k or "Integr" in k]      # + integrals: body holes, generation
    print("   probe [V]" + " " * 46 + " ".join(f"{l:>9s}" for l, _ in marks))
    for k in cols: print(f"   {k[:54]:54s} " + " ".join(f"{at(dv['time'], dv[k], x):+9.4f}" if "Integr" not in k else f"{at(dv['time'], dv[k], x):9.3e}" for _, x in marks))


for rd in (sys.argv[1:] if __name__ == "__main__" else []):       # importable (gt_fig4a.py uses load and at)
    rid = os.path.basename(rd.rstrip("/"))
    try: s = load(os.path.join(rd, rid + "_sys.plt"))
    except Exception as e:
        print(f"{rid}: no system file ({e})"); continue
    t = s["time"]; key = lambda n: next(k for k in s if n in k)
    sn, bl, wl = s[key("nSN)")], s[key("nBL")], s[key("nWL)")]
    print(f"== {rid}: t = {t[-1] * 1e9:.4f} ns, {len(t)} steps, SN now {sn[-1]:.6f} V")
    tw = edges(t, wl, 0, 1.8, True); tw0 = edges(t, wl, 0, 1.8, False); marks = [("start", 0.0)]
    if tw:
        print("   write: SN at +12 / 24 / 39 / 60 / 100 ps after the WL edge: " + " ".join(f"{at(t, sn, tw[0] + x * 1e-12):.3f}" for x in (12, 24, 39, 60, 100)) +
              (f" | after WL off {at(t, sn, tw0[0] + 4e-11):.5f} V" if tw0 and t[-1] > tw0[0] + 4e-11 else ""))
        marks.append(("WL on", tw[0] + 1e-10))
        if tw0: marks.append(("WL off", tw0[0] + 4e-11))
    wa = [k for k in s if "nWLa" in k]
    if wa and max(s[wa[0]]) > 1:                                    # RH: aggressor periods
        r = edges(t, s[wa[0]], 0, 1.8, True); v0 = at(t, sn, r[0] - 2e-11)       # 20 ps before each rising edge: inside the low plateau
        ends = [x - 2e-11 for x in r[1:]] + ([r[-1] + 1.68e-10] if t[-1] > r[-1] + 1.68e-10 else [])
        hi = [at(t, sn, x + 5e-11) - at(t, sn, x - 2e-11) for x in r if t[-1] > x + 5e-11]      # aggressor high minus low: the ripple
        vs = [at(t, sn, x) for x in ends]
        print("   RH: SN before the first pulse %.6f V; change after each period [mV]: " % v0 + " ".join(f"{(v - v0) * 1e3:+.4f}" for v in vs))
        if hi: print(f"   RH: SN with the aggressor WL high minus low: {sum(hi) / len(hi) * 1e3:+.4f} mV (mean of {len(hi)})")
        if len(vs) >= 6:
            ys = vs[-6:]; n = len(ys); sl = sum((i - (n - 1) / 2) * y for i, y in enumerate(ys)) / sum((i - (n - 1) / 2) ** 2 for i in range(n))
            print(f"   RH: loss per cycle, last {n} periods: {-sl * 1e3:.5f} mV   -> 0.605 V / loss = {0.605 / max(-sl, 1e-12):.3g} cycles" if sl < 0 else f"   RH: SN rises {sl * 1e3:.5f} mV per cycle")
        sa = [k for k in s if "nSNa" in k]
        if sa: print(f"   aggressor SN: {at(t, s[sa[0]], r[0] - 2e-11):.3f} -> {s[sa[0]][-1]:.3f} V")
        marks += [("pre RH", r[0] - 2e-11), ("1st high", r[0] + 5e-11), ("end", t[-1])]
    else:
        f = edges(t, bl, 0, 1.1, False)                             # FBE: BL falling edges (middle of each edge)
        if f:
            start = lambda x, up: max(t[i] for i in range(len(t)) if t[i] <= x and (bl[i] <= 1e-3 if up else bl[i] >= 1.1 - 1e-3))    # where that edge begins
            fs = [start(x, False) for x in f]; rs = [start(x, True) for x in edges(t, bl, 0, 1.1, True) if x > f[0]]
            v0 = at(t, sn, fs[0] - 2e-11); per = (fs[1] - fs[0]) if len(fs) > 1 else 2.1e-8
            lo = [v0 - at(t, sn, x - 2e-11) for x in rs]                            # loss at the end of each low phase
            print(f"   FBE: first BL fall at {fs[0] * 1e9:.2f} ns, period {per * 1e9:.2f} ns; SN before it {v0:.5f} V")
            print("   FBE: loss at the end of each low phase [mV]: " + " ".join(f"{x * 1e3:.2f}" for x in lo))
            if t[-1] >= 2e-7: print(f"   FBE: loss at 200 ns: {(v0 - at(t, sn, 2e-7)) * 1e3:.2f} mV")
            m = re.search(r"_c(\d)", rid); c = int(m.group(1)) if m else 0
            if c in PAPER_FBE: print("   paper Fig.8, same instants:                  " + " ".join(f"{x:.0f}" for x in PAPER_FBE[c][0]) + f" | at 200 ns {PAPER_FBE[c][1]:.0f} mV | body rise t=0 -> t_A {PAPER_FBE[c][2]} mV")
            d = glob.glob(os.path.join(rd, "*_dev.plt"))
            if d and tw0:                                                           # body centre under the gate: after the write -> before the first BL fall
                dv = load(d[0]); kv = next(k for k in dv if "ElectrostaticPotential" in k); kg = [k for k in dv if "Band2Band" in k]
                rise = at(dv["time"], dv[kv], fs[0] - 2e-11) - at(dv["time"], dv[kv], tw0[0] + 4e-11)
                gen = at(dv["time"], dv[kg[0]], fs[0] / 2) * 0.1 * 1e-12 * 1.602e-19 * 1e9 if kg else float("nan")
                print(f"   FBE: body centre, WL off -> first BL fall: {rise * 1e3:+.0f} mV; tunnelling generation in the hold {gen:.3g} nA per cell")
            marks += [("pre BL", fs[0] - 2e-11), ("BL low", fs[0] + per / 4), ("BL high", fs[0] + 3 * per / 4), ("end", t[-1])]
    if marks[-1][0] != "end": marks += [("0.1 ns", 1e-10), ("half", t[-1] / 2), ("end", t[-1])]      # hold test: no edges to mark
    probes(rd, marks)
