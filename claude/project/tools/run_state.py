# run_state.py [-a] <batch script> ... : the state of every run of the named batch scripts, read from the run folders themselves
# (the batch logs lost lines while the disk quota was full on 2026-10-06): a live sdevice process or not, the last time in the
# system plot file against the last FinalTime of the deck, and whether the plot files are whole (rows complete, time never
# running backwards: a write that failed in the middle of a file shifts its columns). Default: one line per state with the run ids; -a: one line per run;
# -c: only the ids of the complete runs; -f <system plot file> ...: test only these files.
import sys, os, re, glob, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")


def shape(f):                             # datasets per row, numbers in the file, the time column (as gt_tran.load reads it)
    txt = open(f, errors="replace").read()
    n = len(re.findall(r'"([^"]*)"', re.search(r"datasets\s*=\s*\[(.*?)\]", txt, re.S).group(1)))
    nums = re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", txt[txt.index("Data"):])
    return n, len(nums), [float(x) for x in nums[0:len(nums) - len(nums) % n:n]]


if "-f" in sys.argv:                      # -f <system plot file> ... : only test the named files (read-only, e.g. runs of another agent)
    for f in sys.argv[2:]:
        n, k, t = shape(f); bad = next((i for i in range(1, len(t)) if t[i] < t[i - 1] or t[i] > 0.5), None)     # no transient here is longer than 0.21 s; a shifted column reads 0.55 or 1.1
        print(f"{'time ok ' if bad is None else 'TIME BROKEN at row %d (last good %.4g ns)' % (bad, t[bad - 1] * 1e9)} | {'rows whole' if k % n == 0 else 'LAST ROW CUT (%d of %d numbers)' % (k % n, n)} | {k // n} rows, last time {t[-1] * 1e9:.4g} ns  {f}")
    sys.exit()
every = "-a" in sys.argv; only = "-c" in sys.argv; batches = [b for b in sys.argv[1:] if b not in ("-a", "-c")]
live = {}
for p in subprocess.run(["pgrep", "-u", os.environ["USER"], "-x", "sdevice"], capture_output=True, text=True).stdout.split():
    try: d = os.readlink(f"/proc/{p}/cwd")
    except OSError: continue
    if os.path.dirname(d) == os.path.realpath(R): live[os.path.basename(d)] = live.get(os.path.basename(d), 0) + 1
groups = {}
for b in batches:
    log = os.path.join(R, b[:-3] + ".log"); txt = open(log, errors="replace").read() if os.path.exists(log) else ""
    code = dict(re.findall(r"^(\S+) exit=(\d+)", txt, re.M))
    for rid in " ".join(re.findall(r"printf '%s\\n' (.*?) \|", open(os.path.join(R, b)).read())).split():
        d = os.path.join(R, rid); deck = os.path.join(d, rid + "_des.cmd")
        ft = [float(x) for x in re.findall(r"FinalTime\s*=\s*([-+0-9.eE]+)", open(deck).read())] if os.path.exists(deck) else []
        last, mono = None, True
        for f in glob.glob(os.path.join(d, "*.plt")):
            try: n, k, t = shape(f)
            except Exception: mono = False; continue
            if rid not in live and k % n: mono = False              # a finished file holds whole rows only
            if f.endswith("_sys.plt") and t: last = t[-1]; mono = mono and all(b2 >= a2 for a2, b2 in zip(t, t[1:])) and t[-1] <= (max(ft) * 1.001 if ft else 1e-3)      # a shifted column reads 0.55 or 1.1 as a time
        e = code.get(rid)
        if rid in live: st = "running" + (" (%d processes in one folder!)" % live[rid] if live[rid] > 1 else "") + ("" if glob.glob(os.path.join(d, "*.plt")) else ", no plot file yet")
        elif not glob.glob(os.path.join(d, "*.plt")): st = "no output" + (f" (exit={e})" if e else "")
        elif ft and last is not None and last >= max(ft) * (1 - 1e-6): st = "complete"
        elif not ft: st = "complete" if e == "0" else f"ended, exit={e}"
        else: st = f"stopped early (exit={e})"
        if not mono: st += ", PLOT FILE DAMAGED"
        groups.setdefault(st, []).append(rid)
        if every: print(f"{rid:12s} {st:28s} {'' if last is None else '%.4g' % (last * 1e9) + ' ns'}{' of %.4g ns' % (max(ft) * 1e9) if ft else ''}")
if only: print(" ".join(sorted(set(groups.get("complete", [])))))    # -c: only the ids of the runs that are complete and whole
else:
    for st in sorted(groups): print(f"{st} [{len(groups[st])}]: {' '.join(groups[st])}")
