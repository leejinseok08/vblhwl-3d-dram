# gt_fbe_leak.py <run id> ... : FBE runs, what the storage-node loss is made of. Per run, from t_A (just before the first BL fall) to
# 200 ns of the paper's axis: the loss in mV and as electrons (loss x Cs / q), the electron-hole pairs made in that span by band-to-band
# tunnelling and by impact ionization (100 nm wide device = integral x 1e-13), the holes in the body at both ends, and the rate of the
# loss inside the BL-low phases and inside the BL-high phases (0.6 ns away from the edges). A floating-body loss sits in the BL-low
# phases and takes holes out of the body; a leak that tunnelling at the storage-node junction makes (GIDL) has the same rate in both
# phases, one electron per pair, and leaves its holes in the body. The last column is the rate in the last 10 ns of the hold.
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at, edges
from gt_fbe_pairs import cum, W
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs"); q = 1.602e-19
print("run        Cs[fF] | loss t_A -> 200 ns [mV] = electrons | pairs: tunnelling, impact ion. | holes at t_A -> 200 ns | loss rate [uV/ns]: BL low, BL high | = current [pA]: low, high | last 10 ns of the hold")
for rid in sys.argv[1:]:
    d = os.path.join(RUNS, rid)
    try:
        s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0]); p = json.load(open(os.path.join(d, "run.json"), encoding="utf-8"))["params"]
    except Exception as e: print(rid, "no data", e); continue
    t = s["time"]; T = dv["time"]; k = lambda n: next(x for x in s if n in x); sn = s[k("nSN)")]; bl = s[k("nBL")]
    f = edges(t, bl, 0, 1.1, False); r = [x for x in edges(t, bl, 0, 1.1, True) if f and x > f[0]]
    if not f or min(t[-1], T[-1]) < f[0] + 179e-9: print(rid, "does not reach 200 ns"); continue
    tA = f[0] - 3e-10; tE = f[0] + 179e-9; C = p["Cs"]
    bb = cum(T, dv[next(x for x in dv if "Band2BandGeneration" in x)]); ii = cum(T, dv[next(x for x in dv if "ImpactIonization" in x)]); hd = dv[next(x for x in dv if "hDensity" in x)]
    L = (at(t, sn, tA) - at(t, sn, tE)) * 1e3
    lo = sum(at(t, sn, a + 6e-10) - at(t, sn, b - 6e-10) for a, b in zip(f, r)) / sum((b - 6e-10) - (a + 6e-10) for a, b in zip(f, r))                  # V/s inside the low phases
    hi = sum(at(t, sn, b + 6e-10) - at(t, sn, a - 6e-10) for b, a in zip(r, f[1:])) / sum((a - 6e-10) - (b + 6e-10) for b, a in zip(r, f[1:]))        # V/s inside the high phases
    pre = (at(t, sn, tA - 1e-8) - at(t, sn, tA)) / 1e-8
    print(f"{rid:10s} {C * 1e15:5.2f}  | {L:8.3f} = {L * 1e-3 * C / q:7.1f}            | {(at(T, bb, tE) - at(T, bb, tA)) * W:9.1f} {(at(T, ii, tE) - at(T, ii, tA)) * W:9.1f}       | "
          f"{at(T, hd, tA) * W:6.0f} -> {at(T, hd, tE) * W:6.0f}      | {lo * 1e-3:8.2f} {hi * 1e-3:7.2f}                 | {lo * C * 1e12:8.1f} {hi * C * 1e12:6.1f}        | {pre * 1e-3:6.2f} uV/ns")
