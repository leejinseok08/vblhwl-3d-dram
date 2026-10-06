# gt_long_hold.py [-q] <run id> ... : FBE runs with a long hold and long BL phases (round 11, D z<k> F_c<n>): how the floating body
# fills by its own generation and what the storage node loses.
#   charging: at 10 ns, 100 ns, 1 us, ... after the storage node is set (t = 0 of Fig.8) and at t_A (just before the first BL fall):
#             holes in the body, rise of the body-centre potential since the start of the transient (Fig.8(a): 555 / 445 / 365 / 320 /
#             368 mV), change of the storage node since t = 0;
#   bar:      the time at which the rise passes the bar of Fig.8(a), with the holes and the node change at that time;
#   loss:     storage node at the end of every BL-low phase against its value at t_A, and against 1.1 V.
# Works on running jobs. -q: only the summary line of each run. -b: also the one hold time at which the named cases lie closest to the bars.
import sys, os, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
import paper_targets as P
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
quiet = "-q" in sys.argv; best = "-b" in sys.argv; keep = {}

def tm(x):                                  # a time with its unit
    for u, k in (("ms", 1e-3), ("us", 1e-6), ("ns", 1e-9)):
        if x >= k * 0.9995: return f"{x / k:.3g} {u}"
    return f"{x * 1e12:.3g} ps"

for rid in [a for a in sys.argv[1:] if a not in ("-q", "-b")]:
    d = os.path.join(RUNS, rid)
    try: s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    except Exception: print(f"{rid}: no data"); continue
    t = s["time"]; k = lambda n: next(x for x in s if n in x); sn, bl, wl = s[k("nSN)")], s[k("nBL")], s[k("nWL)")]
    T = dv["time"]; kh = next(x for x in dv if "hDensity" in x); kc = next(x for x in dv if "ElectrostaticPotential" in x)
    c = int(rid.rsplit("_c", 1)[1]); bar = P.FBE_RISE[c]
    wf = edges(t, wl, 0, 1.8, False)
    if not wf: print(f"{rid}: the write is not over (t = {tm(t[-1])})"); continue
    t0 = wf[0] + 4e-11; f = edges(t, bl, 0, 1.1, False); r = [x for x in edges(t, bl, 0, 1.1, True) if f and x > f[0]]
    tA = (f[0] - 3e-10) if f else None; end = tA if tA else min(t[-1], T[-1])
    hol = lambda x: at(T, dv[kh], x) * 1e-13; rise = lambda x: (at(T, dv[kc], x) - dv[kc][0]) * 1e3; dsn = lambda x: (at(t, sn, x) - at(t, sn, t0)) * 1e3
    grid = [t0 + 10.0 ** e for e in range(-8, 0) if t0 + 10.0 ** e < end] + [end]
    cross = None                            # first time the rise passes the bar (log-time interpolation between plot points)
    pts = [x for x in T if t0 < x <= end]
    for a, b in zip(pts, pts[1:]):
        ra, rb = rise(a), rise(b)
        if ra < bar <= rb: cross = t0 + math.exp(math.log(a - t0) + (math.log(b - t0) - math.log(a - t0)) * (bar - ra) / (rb - ra)); break
    state = "t_A" if tA else "now"
    head = (f"{rid}: Case {c}, bar {bar} mV | hold {tm(end - t0)} ({state}): holes {hol(end):.0f}, rise {rise(end):+.0f} mV, node {dsn(end):+.2f} mV | "
            + (f"bar reached after {tm(cross - t0)} (holes {hol(cross):.0f}, node {dsn(cross):+.2f} mV)" if cross else "bar not reached in the hold"))
    low = [(a, b) for a, b in zip(f, r)] if f else []
    if low:
        snA = at(t, sn, tA); L = [(snA - at(t, sn, b - 3e-10)) * 1e3 for a, b in low if b - 3e-10 <= t[-1]]
        head += f" | loss after BL-low phase 1 .. {len(L)} [mV]: " + " ".join(f"{x:.2f}" for x in L) + (f" | node at the end {at(t, sn, t[-1]):.4f} V" if L else "")
    print(head); keep[c] = (bar, end - t0, t0, T, dv[kc], dv[kh], t, sn)      # the arrays themselves: the lambdas above see only the last run
    if quiet: continue
    print("   time after t = 0   " + "".join(f"{tm(x - t0):>10s}" for x in grid))
    print("   holes in the body  " + "".join(f"{hol(x):10.0f}" for x in grid))
    print("   body rise [mV]     " + "".join(f"{rise(x):+10.0f}" for x in grid))
    print("   node change [mV]   " + "".join(f"{dsn(x):+10.2f}" for x in grid))
if best and len(keep) > 1:                  # -b: the one hold time at which the rises of the named cases lie closest to the bars of Fig.8(a)
    R = lambda v, x: (at(v[3], v[4], v[2] + x) - v[4][0]) * 1e3; H = lambda v, x: at(v[3], v[5], v[2] + x) * 1e-13
    N = lambda v, x: (at(v[6], v[7], v[2] + x) - at(v[6], v[7], v[2])) * 1e3
    hi = min(v[1] for v in keep.values()); grid = [1e-7 * (hi / 1e-7) ** (i / 600) for i in range(601)]
    rms = lambda x: math.sqrt(sum((R(v, x) - v[0]) ** 2 for v in keep.values()) / len(keep))
    x = min(grid, key=rms); cs = sorted(keep)
    print(f"closest to the bars of Fig.8(a) at one common hold time: {tm(x)} (rms deviation {rms(x):.0f} mV over Cases {' '.join(map(str, cs))})")
    print("   bar [mV]           " + "".join(f"{keep[c][0]:10d}" for c in cs))
    print("   body rise [mV]     " + "".join(f"{R(keep[c], x):+10.0f}" for c in cs))
    print("   holes in the body  " + "".join(f"{H(keep[c], x):10.0f}" for c in cs))
    print("   node change [mV]   " + "".join(f"{N(keep[c], x):+10.2f}" for c in cs))
