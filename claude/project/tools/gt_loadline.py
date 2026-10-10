# gt_loadline.py [-n] <load-line run id> ... : the DC charging current along the write of Fig.4(a) (deck "load" of make_runs.py: gates at Vpp, BL at
# the write level, the storage-node contact swept from 0 V to the BL level) against what the paper's write curve asks for, and where the
# BL-to-node voltage drops (electron quasi-Fermi potential along the channel at mid-depth and down the BL pillar, ProbeE).
#   1. current into the node at chosen node voltages [uA per cell of 0.1 um], next to the average current the paper's curve implies with the
#      text's capacitor: C dV / dt between its four points (0.72 / 0.92 / 1.06 / 1.13 V at 12 / 24 / 39 / 60 ps);
#   2. the write curve that this DC current gives on that capacitor (t = C integral dV / I), next to the paper's four points;
#   3. at three node voltages the share of the BL-to-node voltage that falls in each part: pillar (contact to pillar face), the body under the
#      BL-side spacer, the gated channel, the source under the storage-node-side spacer.
# -n prints the column names of the current file.
import sys, os, re, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
W = 0.1                                                # um: width of the cell
CS = {30: 5.1e-15, 20: 4.2e-15, 10: 3.6e-15}           # text of the paper
PTS = [(0.0, 0.0)] + [(ps * 1e-12, v) for ps, v in P.WRITE.items()]        # (time after the WL edge, node voltage) of Fig.4(a)

def interp(xs, ys, x):
    for i in range(1, len(xs)):
        if (xs[i - 1] - x) * (xs[i] - x) <= 0 and xs[i] != xs[i - 1]: return ys[i - 1] + (ys[i] - ys[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1])
    return float("nan")

if __name__ == "__main__":
    names = "-n" in sys.argv
    for rid in [a for a in sys.argv[1:] if a != "-n"]:
        f = glob.glob(os.path.join(RUNS, rid, "LL_*.plt")); p = json.load(open(os.path.join(RUNS, rid, "run.json")))["params"]
        if not f: print(f"{rid}: no load-line file"); continue
        s = load(f[0])
        if names: print("\n".join(s)); continue
        v = s["sn_v OuterVoltage"]; cur = [abs(x) * W for x in s["sn_v TotalCurrent"]]; c = CS[p["Tbody"]]; vbl = p["Vwr"] or p["Vdd"]
        print(f"== {rid}: body {p['Tbody']} nm, gates {p['Vpp']} V, BL {vbl} V, {len(v)} points up to node {v[-1]:.3f} V; capacitor of the text {c * 1e15:.1f} fF")
        print("   1. node voltage [V]:            " + "  ".join(f"{x:6.2f}" for x in (0.0, 0.2, 0.4, 0.6, 0.72, 0.82, 0.92, 0.99, 1.06, 1.095, 1.13)))
        print("      DC current into the node [uA]: " + "  ".join(f"{interp(v, cur, x) * 1e6:6.1f}" for x in (0.0, 0.2, 0.4, 0.6, 0.72, 0.82, 0.92, 0.99, 1.06, 1.095, 1.13)))
        t = [0.0]                                      # 2. quasi-static write: dt = C dV / I
        for i in range(1, len(v)): t.append(t[-1] + c * (v[i] - v[i - 1]) / (0.5 * (cur[i] + cur[i - 1]) or 1e-30))
        print("   2. write from the DC current, node at 12 / 24 / 39 / 60 ps: " + " / ".join(f"{interp(t, v, ps * 1e-12):.3f}" for ps in P.WRITE)
              + " V   (paper " + " / ".join(f"{x:.2f}" for x in P.WRITE.values()) + ")")
        # interval means C dV / dt on the same intervals, paper and quasi-static model (one definition for both; a DC current at one node voltage
        # is neither an interval mean nor a bound on the transient current, which can exceed it at the WL edge: 2026-10-10, Codex's review)
        qs = lambda x: interp(t, v, x) if x > 0 else 0.0
        print("      interval means C dV/dt [uA], paper | quasi-static DC write: " + "; ".join(
            f"{a[0] * 1e12:.0f} - {b[0] * 1e12:.0f} ps: {c * (b[1] - a[1]) / (b[0] - a[0]) * 1e6:.0f} | {c * (qs(b[0]) - qs(a[0])) / (b[0] - a[0]) * 1e6:.0f}" for a, b in zip(PTS, PTS[1:])))
        qf = {}                                        # 3. electron quasi-Fermi potential probes: (x nm, y nm) -> column
        for k in s:
            m = re.search(r"\(?\s*(-?[\d.eE+-]+)[ ,]+(-?[\d.eE+-]+)\s*\)?", k) if "eQuasiFermiPotential" in k else None
            if m: qf[(round(float(m.group(1)) * 1e3, 1), round(float(m.group(2)) * 1e3, 1))] = s[k]
        ym = p["Dvox"] / 2 + p["Tgm"] + p["Tox"] + p["Tbody"] / 2; x0 = p["Wbl"] / 2; xg1 = x0 + p["Lsp1"]; xg2 = xg1 + p["Lg"]
        row = sorted(x for (x, y) in qf if abs(y - ym) < 0.6)
        near = lambda x: min(row, key=lambda a: abs(a - x))
        if not row: print("   3. no quasi-Fermi probes in the file (column names: -n)"); continue
        print(f"   3. where the BL-to-node voltage falls (electron quasi-Fermi potential at mid-depth; read at x = {near(x0 - 3)}, {near(xg1 + 2)}, {near(xg2 - 3)} nm; pillar face {x0:g}, gate {xg1:g} .. {xg2:g}):")
        print("      node [V]   current [uA]   whole drop [mV] = pillar and its contact | body under the BL-side spacer (25 nm) | gated channel (100 nm) | source (25 nm)")
        for vn in (0.36, 0.60, 0.82, 0.99, 1.095):
            g = lambda x: interp(v, qf[(near(x), min((y for (a, y) in qf if a == near(x)), key=lambda y: abs(y - ym)))], vn)
            a, b, cc, d = g(x0 - 3), g(xg1 + 2), g(xg2 - 3), g(row[-1])
            tot = vbl - vn; parts = (vbl - a, a - b, b - cc, cc - vn)
            print(f"      {vn:6.3f}    {interp(v, cur, vn) * 1e6:8.1f}       {tot * 1e3:6.0f}         = " + " | ".join(f"{x * 1e3:5.0f} ({100 * x / tot:3.0f} %)" for x in parts))
