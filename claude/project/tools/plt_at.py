# plt_at.py <run id> <t1 ns> <t2 ns> <steps> <name part> ... : values of the system plot file of a run at evenly spaced
# instants (linear interpolation), one column per dataset whose name holds one of the name parts (e.g. nSN) nGv nWLa).
# The first named dataset is also printed as the change since t1 in mV. For looking at one edge or one cycle.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load, at
rid, t1, t2, n = sys.argv[1], float(sys.argv[2]) * 1e-9, float(sys.argv[3]) * 1e-9, int(sys.argv[4])
s = load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs", rid, rid + "_sys.plt")); t = s["time"]
ks = [next(k for k in s if p in k) for p in sys.argv[5:]]
print(f"{rid}: t [ns]   " + "   ".join(f"{k:>10s}" for k in ks) + f"   d {ks[0]} [mV]")
v0 = at(t, s[ks[0]], t1)
for i in range(n + 1):
    x = t1 + (t2 - t1) * i / n
    print(f"   {x * 1e9:8.4f}   " + "   ".join(f"{at(t, s[k], x):10.6f}" for k in ks) + f"   {(at(t, s[ks[0]], x) - v0) * 1e3:+9.4f}")
