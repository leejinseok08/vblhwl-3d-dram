# gt_rh_count.py <tag> [idle tag] : the row-hammer threshold counts of Fig.7(d) of Cho et al. from the pair runs of a configuration.
# RH-Case 1 / 2 / 3 of Fig.7(d) are the DIRECTIONS Y-Y' / Z-Z' / X-X' (all on device design Case 2), not the device Cases 1 - 3 of Fig.5(b).
# The paper's count = voltage margin / loss of the victim's storage node per aggressor cycle (Sec.IV). Two margins, kept apart (plan P0):
#   605 mV  back-calculated from the paper's own counts (60.5k x 0.0100 mV = 100.8k x 0.0060 mV = 605 mV): a reading, not a stated value;
#   550 mV  the text's formula 0.5 VDD - I_leak t / Cs, which cannot exceed 0.5 x 1.1 V for a non-negative leak. Why the two differ is open.
# Per bar: the loss per cycle of the attack run as the paper takes it (the cell's own leak included), over all cycles and over the last
# five (a first-cycle shift is not a loss per cycle), the same minus the idle control, and the counts. A finite count only where the slope
# is positive both over all cycles and over the last five; otherwise "no fall" (the node does not fall) or "unsteady" (the two slopes
# differ in sign). "no fall" is NOT the paper's "N/A", which is the opposite: the node collapses within the ten cycles (Fig.7(a)).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score2d as S
MARGINS = (605.0, 550.0)   # mV: back-calculated from the counts / upper bound of the text's formula
BARS = (("RH-Case 1 Y off", "Ry_yy", "11.3k"), ("RH-Case 1 Y on", "Ryi_yy", "11.3k"), ("RH-Case 2 Z off", "Rzb_zz", "60.5k"),
        ("RH-Case 2 Z on", "Rzbi_zz", "N/A (collapse)"), ("RH-Case 2 Z gnd on", "Rzbg_zz", "16.8k"))
NOT_2D = (("RH-Case 3 X off", "100.8k", "X-X' is a 3D quantity (next row): not in the 2D section"),
          ("RH-Case 3 X on", "86.4k", "X-X' is a 3D quantity (next row): not in the 2D section"),
          ("6F2 reference", "1.12k", "the planar 6F2 cell of the paper: outside this reproduction"))


def cnt(per, last, margin):
    """Count from the two slopes [mV per cycle], or why there is none."""
    if per is None or last is None: return "-"
    if per > 0 and last > 0:
        n = margin / last
        return f"{n / 1e3:.1f}k" if n >= 1e3 else f"{n:.0f}"
    return "no fall" if per <= 0 and last <= 0 else "unsteady"


def main(tag, idle):
    f = lambda x: "   -    " if x is None else f"{x:+8.5f}"
    print(f"{'bar of Fig.7(d)':20s} | loss per cycle [mV]: all, last five | count 605 / 550 mV | minus idle: all, last five | count 605 / 550 mV | paper")
    for lab, nm, pap in BARS:
        rid = f"D{tag}{nm}"
        if not os.path.isdir(S.rd(rid)): rid = rid.replace("Rzb", "Rz", 1)
        if not os.path.isdir(S.rd(rid)): print(f"{lab:20s} | no run | paper {pap}"); continue
        m = S.rh_run(rid)
        if not m: print(f"{lab:20s} | {rid}: no cycle yet | paper {pap}"); continue
        iid = rid.replace("D" + tag, "D" + idle, 1) if idle else None
        i = S.rh_run(iid, m["r"]) if iid and os.path.isdir(S.rd(iid)) else None
        d = (m["per"] - i["per"], m["last"] - i["last"] if m["last"] is not None and i["last"] is not None else None) if i else (None, None)
        c = lambda a, b: " / ".join(cnt(a, b, g) for g in MARGINS)
        print(f"{lab:20s} | {f(m['per'])} {f(m['last'])} ({m['n']} cycles) | {c(m['per'], m['last']):>17s} | {f(d[0])} {f(d[1])} | {c(*d):>17s} | {pap}")
    for lab, pap, why in NOT_2D: print(f"{lab:20s} | not run: {why} | paper {pap}")


def selfcheck():
    assert cnt(0.0100, 0.0100, 605.0) == "60.5k" and cnt(-0.001, -0.002, 605.0) == "no fall" and cnt(0.001, -0.001, 605.0) == "unsteady"
    assert cnt(0.006, 0.006, 550.0) == "91.7k" and cnt(None, None, 605.0) == "-"


if __name__ == "__main__":
    selfcheck()
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
