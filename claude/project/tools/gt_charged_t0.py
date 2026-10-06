# gt_charged_t0.py : the hypothesis "at t = 0 of Fig.8 the body is already charged and the storage node stands at 1.1 V" held
# against the paper's numbers with the runs that have exactly that state: Dh1F .. Dh4F (hole charge 1.0 / 1.25 / 1.5 / 2.0 times
# the charge of the bars, set by the stand-in generation while the node is held; then the paper's BL waveform, 9 low phases).
#   table A: per case and charge, body rise at t_A (body centre, against the start of the transient), holes, loss 5 ns and
#            3 ns after the BL fall, after low phases 1 .. 4, and at 200 ns of the paper's axis;
#   table B: per case the state (interpolated in the body rise, losses on a log scale) that gives the paper's loss of the
#            first low phase: how far it is from the bar, what charge it needs, and what the rest of the curve is there;
#   table C: every recorded reading of a "body potential" (four positions, electrostatic and hole quasi-Fermi potential, against
#            the start of the transient and against t = 0) at those states, against the bars: is there one that fits?
# Paper values: tools/paper_targets.py and the pixel readings of NOTES (au). GT_RUNS: another runs folder.
import sys, os, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
TAGS = (("Dh1F", 1.0), ("Dh2F", 1.25), ("Dh3F", 1.5), ("Dh4F", 2.0))
PAPER_EARLY = {1: (5, 43), 2: (5, 23), 3: (3, 3.3), 4: (3, 1.4)}      # (ns after the BL fall, loss mV): Fig.8(b), (c) read from the pixels
PAPER_PH = {1: (55, 67, 76, 83)}                                       # loss after low phases 1 .. 4 (Case 1 only could be read)

def run(rid):
    d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; T = dv["time"]
    t0 = edges(t, s[k("nWL)")], 0, 1.8, False)[0] + 4e-11; f = edges(t, s[k("nBL")], 0, 1.1, False); r = [x for x in edges(t, s[k("nBL")], 0, 1.1, True) if x > f[0]]
    tA = f[0] - 3e-10; L = lambda x: (at(t, sn, tA) - at(t, sn, x)) * 1e3
    o = dict(holes=at(T, dv[next(x for x in dv if "hDensity" in x)], tA) * 1e-13, sn=at(t, sn, tA), L5=L(f[0] + 5e-9), L3=L(f[0] + 3e-9),
             ph=[L(x - 3e-10) for x in r[:9]], L200=L(f[0] + 179e-9), probe={})
    for q in dv:
        if q.startswith("Pos(") and ("ElectrostaticPotential" in q or "hQuasiFermi" in q):
            n = "x = " + q[4:q.index(",")] + " um " + q.split()[-1]          # the height of the probe follows the body thickness: name by x
            o["probe"][n + " | since the start"] = (at(T, dv[q], tA) - dv[q][0]) * 1e3; o["probe"][n + " | since t = 0"] = (at(T, dv[q], tA) - at(T, dv[q], t0)) * 1e3
    o["rise"] = o["probe"]["x = 0.125 um ElectrostaticPotential | since the start"]
    return o

D = {c: [run(f"{tag}_c{c}") for tag, _ in TAGS] for c in range(1, 6)}
print("A. charged at t = 0, node at 1.1 V at t_A (stand-in charge x 1.0 / 1.25 / 1.5 / 2.0 of the bars). Losses in mV; paper in brackets")
print("case charge  holes  rise[mV]   node[V] | +5 ns   +3 ns | after low phase 1 .. 4              |  200 ns | first / 200 ns")
for c in range(1, 6):
    for (tag, fac), o in zip(TAGS, D[c]):
        print(f"{c:3d}  x{fac:<5} {o['holes']:6.0f} {o['rise']:6.0f}    {o['sn']:.4f} | {o['L5']:6.2f} {o['L3']:7.2f} | " + " ".join(f"{x:7.2f}" for x in o["ph"][:4])
              + f"   | {o['L200']:7.2f} | {o['ph'][0] / o['L200']:5.2f}")
    e = PAPER_EARLY.get(c); ph = PAPER_PH.get(c, (P.FBE_FIRST[c],))
    print(f"     paper        {P.FBE_RISE[c]:6d}    1.1000 | " + (f"{e[1]:6.1f} at +{e[0]} ns " if e else "               ") + "| " + " ".join(f"{x:7.1f}" for x in ph) + " " * (8 * (4 - len(ph)))
          + f"   | {P.FBE_200[c]:7.1f} | " + (f"{P.FBE_FIRST[c] / P.FBE_200[c]:5.2f}" if P.FBE_FIRST[c] else "    -"))

def match(c, key, target):
    """weight w and index i so that log(loss) at (1 - w) * state i + w * state i+1 equals the target; None outside the grid"""
    v = [key(o) for o in D[c]]
    for i in range(len(v) - 1):
        if v[i] <= target <= v[i + 1]: return i, (math.log(target) - math.log(v[i])) / (math.log(v[i + 1]) - math.log(v[i]))
lin = lambda c, i, w, key: key(D[c][i]) * (1 - w) + key(D[c][i + 1]) * w
logi = lambda c, i, w, key: math.exp(math.log(key(D[c][i])) * (1 - w) + math.log(key(D[c][i + 1])) * w)

print()
print("B. the state that gives the paper's loss of the first low phase (Cases 1 - 4; Case 5 loses 0.13 - 0.15 mV up to x 1.5, paper 0)")
print("case  first loss | rise there  bar   above the bar | charge   holes | +5 or +3 ns (paper)  | phases 2 .. 4 (paper)                 | 200 ns (paper)")
M = {}
for c in range(1, 5):
    i, w = match(c, lambda o: o["ph"][0], P.FBE_FIRST[c]); M[c] = (i, w)
    r_ = lin(c, i, w, lambda o: o["rise"]); e = PAPER_EARLY[c]; k5 = (lambda o: o["L5"]) if e[0] == 5 else (lambda o: o["L3"])
    ph = [logi(c, i, w, lambda o, j=j: o["ph"][j]) for j in (1, 2, 3)]
    print(f"{c:3d}  {P.FBE_FIRST[c]:7.1f} mV | {r_:6.0f}     {P.FBE_RISE[c]:4d}   {r_ - P.FBE_RISE[c]:+6.0f} mV     | x{lin(c, i, w, lambda o: 0) + TAGS[i][1] * (1 - w) + TAGS[i + 1][1] * w:5.2f}  {lin(c, i, w, lambda o: o['holes']):6.0f} | "
          f"{logi(c, i, w, k5):6.1f} ({e[1]:4.1f})       | " + " ".join(f"{x:6.1f}" for x in ph) + (" (" + " ".join(f"{x:.0f}" for x in PAPER_PH[c][1:]) + ")" if c in PAPER_PH else "           ")
          + f"       | {logi(c, i, w, lambda o: o['L200']):6.1f} ({P.FBE_200[c]:.1f})")
print("     the other way round, the state that gives the paper's loss at 200 ns:")
for c in range(1, 5):
    i, w = match(c, lambda o: o["L200"], P.FBE_200[c]); r_ = lin(c, i, w, lambda o: o["rise"])
    print(f"{c:3d}  200 ns {P.FBE_200[c]:5.1f} mV: rise {r_:4.0f} mV ({r_ - P.FBE_RISE[c]:+.0f} against the bar), charge x{TAGS[i][1] * (1 - w) + TAGS[i + 1][1] * w:.2f}, "
          f"first loss there {logi(c, i, w, lambda o: o['ph'][0]):5.1f} mV (paper {P.FBE_FIRST[c]})")

print()
print("C. every recorded reading of a body potential at the states of B [mV], against the bars 555 / 445 / 365 / 320 (Cases 1 - 4)")
rows = []
for q in D[1][0]["probe"]:
    v = [lin(c, *M[c], lambda o, q=q: o["probe"][q]) for c in range(1, 5)]
    rows.append((math.sqrt(sum((v[c - 1] - P.FBE_RISE[c]) ** 2 for c in range(1, 5)) / 4), q, v))
for rms, q, v in sorted(rows):
    print(f"   rms {rms:5.0f} mV   " + " ".join(f"{x:6.0f}" for x in v) + "   deviation " + " ".join(f"{v[c - 1] - P.FBE_RISE[c]:+5.0f}" for c in range(1, 5)) + f"   {q}")

# D. does it matter how the body was charged? States charged by the model's own generation (Codex's screen, groups "natural":
# hold 15.2 us or 21 us, node free / put back to 1.1 V before the fall / held at 1.1 V; its result files, read only) against
# the curve "loss of the first low phase over the body rise" of the stand-in states above, at the same rise. GT_CODEX: folder
# with Codex's results/*.json (default: codex_validation/factorial_conditions_20261006/results next to runs/).
def curve(c, rise):
    """first-phase loss of the stand-in states at this body rise (log-linear between the two nearest states; '*' = outside the grid)"""
    r = [o["rise"] for o in D[c]]; i = max(0, min(len(r) - 2, next((k for k in range(len(r) - 1) if rise <= r[k + 1]), len(r) - 2)))
    w = (rise - r[i]) / (r[i + 1] - r[i])
    return math.exp(math.log(D[c][i]["ph"][0]) * (1 - w) + math.log(D[c][i + 1]["ph"][0]) * w), ("" if r[0] <= rise <= r[-1] else "*")
CX = os.environ.get("GT_CODEX") or os.path.join(RUNS, "..", "codex_validation", "factorial_conditions_20261006", "results")
if os.path.isdir(CX):
    import json
    G = {}
    for f_ in glob.glob(os.path.join(CX, "*.json")):
        d = json.load(open(f_, encoding="utf-8"))
        if d["preparation"] == "natural" and d["II"] == 1 and d["Cs_basis"] == "write_fit" and d["hold_ns"] > 1000: G.setdefault((d["hold_ns"], d["SN_protocol"]), {})[d["case"]] = d
    print()
    print("D. charged by the model's own generation (Codex's runs) against the stand-in curve at the same body rise; first low phase [mV]")
    for (hold, prot), g in sorted(G.items()):
        if len(g) < 5: continue
        print(f"   hold {hold / 1e3:g} us, node {prot:10s} | rise " + " ".join(f"{g[c]['prefall']['body_rise_eq_mV']:5.0f}" for c in range(1, 6)) + " | node before the fall " + " ".join(f"{g[c]['prefall']['SN_V']:.3f}" for c in range(1, 6)))
        print("        loss, Codex's run        | " + " ".join(f"{g[c]['first_low']['SN_loss_mV']:7.2f}" for c in range(1, 6)))
        print("        stand-in curve, same rise| " + " ".join("%7.2f%s" % curve(c, g[c]["prefall"]["body_rise_eq_mV"]) for c in range(1, 6)))
    print(f"   paper: rise " + " ".join(f"{P.FBE_RISE[c]:5d}" for c in range(1, 6)) + " | loss " + " ".join(f"{P.FBE_FIRST[c]:5.1f}" for c in range(1, 6)))
