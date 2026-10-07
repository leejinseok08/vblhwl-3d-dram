# gt_rh_ripple.py [run id ...] : the reversible swing of the victim's storage node inside the aggressor cycles of a row-hammer pair run,
# against Fig.6(e) of the paper. Read there on 2026-10-08 (embedded image, 0.128 mV per pixel row, 1.100 V = row 928; the X-X' curve is
# drawn on top; its ten transitions line up with the edges of the aggressor waveform of Fig.6(c), which starts HIGH at the left frame):
# the node sits about 0.70 mV HIGHER while the aggressor WL is high and is back between the pulses, ten times; that level stays inside
# one row (0.13 mV) over the ten cycles; the Y-Y' curve shows no swing in the first two pulses and lies 2 - 3 rows (0.3 - 0.4 mV) lower
# from the third pulse on; the Z-Z' curve is hidden under the other two. The axis labels under 1.100 are misprinted (1.109, 1.108).
# (The paper's text: 0.05 / 0.01 / 0.006 mV per cycle for Y-Y' / Z-Z' / X-X'.)
# Per run: swing = node in the middle of the aggressor's high phase minus the mean of the node just before the rise and just before
# the next rise [mV], cycles 1, 2, 5, 10; the same for the victim gate node where the deck has one (WL resistor); loss per cycle.
#   usage (PC): GT_RUNS=<shared runs> python tools/gt_rh_ripple.py [ids]      default: the scan of the WL resistor and the pairs of fin5
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
PAPER = dict(swing=+0.70, row=0.128)          # mV: X-X' curve of Fig.6(e), and the size of one pixel row
DEF = ["DdyRy_yy", "DdyRzb_zz", "DdyRzbg_zz", "DfinRy_yy", "DfinRz_zz", "QYid_yy", "QY1e6_yy", "QY1e7_yy", "QSid_zz", "QR1e5_zz", "QS2e5_zz", "QS5e5_zz", "QR1e6_zz", "QS2e6_zz",
       "QS5e6_zz", "QR1e7_zz", "Dr2Ry_yy", "Dr2Rz_zz", "Dr2Rzg_zz"]

def ripple(rid):
    d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); t = s["time"]; key = lambda n: next((k for k in s if n in k), None)
    sn = s[key("nSN)")]; wa = s[key("nWLa")]; r = edges(t, wa, 0, 1.8, True); f = edges(t, wa, 0, 1.8, False)
    if len(r) < 2: return None
    per = r[1] - r[0]; hi = (f[0] - r[0]) if f and f[0] > r[0] else per / 2; gk = key("nGv"); g = s[gk] if gk else None
    j = json.load(open(os.path.join(d, "run.json"), encoding="utf-8")) if os.path.exists(os.path.join(d, "run.json")) else {}
    out = dict(per=per * 1e9, cs=j.get("params", {}).get("Cs"), R=j.get("params", {}).get("Rwl"), sw={}, gw={}, n=0)
    for i, x in enumerate(r):
        if t[-1] < x + per - 2e-11: break
        a, b, m = at(t, sn, x - 2e-11), at(t, sn, x + per - 2e-11), at(t, sn, x + hi / 2)
        out["sw"][i + 1] = (m - (a + b) / 2) * 1e3; out["n"] = i + 1; out.setdefault("loss", []).append((a - b) * 1e3)
        if g: out["gw"][i + 1] = (at(t, g, x + hi / 2) - at(t, g, x - 2e-11)) * 1e3
    return out

if __name__ == "__main__":
    ids = sys.argv[1:] or DEF
    print(f"paper Fig.6(e), X-X' curve: swing {PAPER['swing']:+.2f} mV while the aggressor WL is high (one pixel row = {PAPER['row']} mV); text: 0.05 / 0.01 / 0.006 mV per cycle")
    print("run            Cs[fF] R_WL[Ohm] | swing of the node, cycle 1 / 2 / 5 / 10 [mV] | victim gate, cycle 1 / 10 [mV] | loss cycle 1, mean of the last five [mV]")
    for rid in ids:
        try: m = ripple(rid)
        except Exception as e: print(f"{rid:14s} {type(e).__name__}: {e}"); continue
        if not m or not m["n"]: print(f"{rid:14s} no complete cycle"); continue
        q = lambda d, k: "   -   " if k not in d else f"{d[k]:+7.3f}"; cs = "  -  " if m["cs"] is None else f"{m['cs'] * 1e15:5.2f}"; R = "    -   " if m["R"] is None else f"{m['R']:8.1e}"
        l5 = sum(m["loss"][-5:]) / 5 if m["n"] >= 6 else float("nan")
        print(f"{rid:14s} {cs} {R} | {q(m['sw'], 1)} {q(m['sw'], 2)} {q(m['sw'], 5)} {q(m['sw'], 10)} | {q(m['gw'], 1)} {q(m['gw'], 10)} | {m['loss'][0]:+8.4f} {l5:+8.4f}   ({m['n']} cycles)")
