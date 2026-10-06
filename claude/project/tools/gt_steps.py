# gt_steps.py <run dir> ... [-n N] : how a transient / quasistationary run stepped. Per run: number of steps tried and
# failed, then the last N (default 12) tries: start, size, Newton iterations, last error, ok / FAIL, and for a failed step the
# equation and place of the largest error. Reads <run>/<run>.out (or the _log file).
import sys, os, re, glob
args = sys.argv[1:]; N = 12
if "-n" in args: i = args.index("-n"); N = int(args[i + 1]); del args[i:i + 2]
num = r"([-+0-9.eE]+)"
for rd in args:
    rid = os.path.basename(rd.rstrip("/")); f = os.path.join(rd, rid + ".out")
    if not os.path.isfile(f): f = (glob.glob(os.path.join(rd, "*_log*")) + [""])[0]
    if not f: print(rid, "no log"); continue
    steps = []; cur = None; worst = {}
    for l in open(f, errors="replace"):
        m = re.match(r"\s*Computing (?:BE-|TRBDF-)?step from (?:t=)?" + num + r"(?: s)? to (?:t=)?" + num + r"(?: s)? \(Stepsize: " + num, l)
        if m: cur = dict(t=float(m.group(1)), dt=float(m.group(3)), it=0, err=float("nan"), ok=None, worst=""); steps.append(cur); worst = {}; continue
        if cur is None: continue
        m = re.match(r"\s*(\d+)\s+" + num + r"\s+" + num + r"\s+" + num + r"\s+" + num + r"\s+\d+", l)
        if m: cur["it"] = int(m.group(1)); cur["err"] = float(m.group(5)); continue
        m = re.match(r"\s*(poisson|electron|hole|QuasiFermiPo\w*|circuit|contact):\s+" + num + r"\s+\d+\s+\(([^)]*)\)", l)
        if m: worst[m.group(1)] = (float(m.group(2)), m.group(3)); cur["worst"] = max(worst.items(), key=lambda kv: kv[1][0]); continue
        if "Finished" in l or " Done " in l or re.match(r"\s*done", l): cur["ok"] = True
    for a, b in zip(steps, steps[1:]):
        if a["ok"] is None: a["ok"] = b["t"] > a["t"] * (1 + 1e-12) or (b["t"] > a["t"])
    bad = sum(1 for s in steps if s["ok"] is False)
    print(f"== {rid}: {len(steps)} steps tried, {bad} failed")
    for s in steps[-N:]:
        w = f"  worst {s['worst'][0]} {s['worst'][1][0]:.2e} at ({s['worst'][1][1]})" if s["worst"] and not s["ok"] else ""
        print(f"   t {s['t']:.6e}  dt {s['dt']:.3e}  it {s['it']:3d}  err {s['err']:9.2e}  {'ok' if s['ok'] else 'FAIL' if s['ok'] is False else '..'}{w}")
