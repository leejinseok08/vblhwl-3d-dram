# plt_cols.py <run id> [substring] : the column names of a run's device plot file (those containing the substring, if given).
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs", sys.argv[1])
dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0]); sub = sys.argv[2] if len(sys.argv) > 2 else ""
names = [k for k in dv if sub in k]; print(len(dv), "columns,", len(dv["time"]), "rows;", len(names), "shown")
for k in names: print("  ", k, "| first", dv[k][0], "| last", dv[k][-1])
