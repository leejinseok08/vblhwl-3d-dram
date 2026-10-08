# gt_rh_count.py <tag> [idle tag] : the row-hammer threshold counts of Fig.7(d) of Cho et al. from the pair runs of a configuration.
# The paper's count = voltage margin / loss of the victim's storage node per aggressor cycle (Sec.IV); its counts are 0.605 V divided by
# the loss per cycle (60.5k x 0.0100 mV = 100.8k x 0.0060 mV). Per bar of Fig.7(d): the loss per cycle of the attack run as the paper
# takes it (the cell's own leak included), over all cycles and over the last five (a first-cycle shift is not a loss per cycle), the
# same minus the idle control, and the counts 0.605 V / loss. A loss <= 0 (the node does not fall) has no count: "none".
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score2d as S
MARGIN = 605.0   # mV
BARS = (("Case 1 Y-Y' off", "Ry_yy", "11.3k"), ("Case 1 Y-Y' on", "Ryi_yy", "11.3k"), ("Case 2 Z-Z' off", "Rzb_zz", "60.5k"),
        ("Case 2 Z-Z' on", "Rzbi_zz", "N/A"), ("Case 2 grounded on", "Rzbg_zz", "16.8k"))
cnt = lambda x: "none" if x is None or x <= 0 else (f"{MARGIN / x / 1e3:.0f}k" if MARGIN / x >= 1e3 else f"{MARGIN / x:.0f}")
f = lambda x: "   -    " if x is None else f"{x:+8.5f}"
tag = sys.argv[1]; idle = sys.argv[2] if len(sys.argv) > 2 else None
print(f"{'bar of Fig.7(d)':20s} | loss per cycle [mV]: all cycles, last five | count | minus idle: all, last five | count | paper")
for lab, nm, pap in BARS:
    rid = f"D{tag}{nm}"
    if not os.path.isdir(S.rd(rid)): rid = rid.replace("Rzb", "Rz", 1)
    if not os.path.isdir(S.rd(rid)): print(f"{lab:20s} | no run"); continue
    m = S.rh_run(rid)
    if not m: print(f"{lab:20s} | {rid}: no cycle yet"); continue
    i = S.rh_run(rid.replace("D" + tag, "D" + idle, 1), m["r"]) if idle and os.path.isdir(S.rd(rid.replace("D" + tag, "D" + idle, 1))) else None
    d = (m["per"] - i["per"], m["last"] - i["last"] if m["last"] is not None and i["last"] is not None else None) if i else (None, None)
    print(f"{lab:20s} | {f(m['per'])} {f(m['last'])} ({m['n']} cycles) | {cnt(m['last']):>6s} | {f(d[0])} {f(d[1])} | {cnt(d[1]):>6s} | {pap}")
