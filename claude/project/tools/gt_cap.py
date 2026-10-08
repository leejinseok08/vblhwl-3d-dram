# gt_cap.py <run id> ... : capacitance matrix of the AC runs (deck "ac" of make_runs.py: single cell at 0 V, 1 MHz) in fF, next to the
# parallel-plate value of the drawn capacitor (faces x 3.9 eps0 / EOT, 100 nm wide) and to the text of the paper (3.6 / 4.2 / 5.1 fF for
# bodies of 10 / 20 / 30 nm). c(n,n) of the extraction file is the whole capacitance of a node, -c(n,m) the capacitance between two.
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_tran import load
RUNS = os.environ.get("GT_RUNS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
TEXT = {10: 3.6, 20: 4.2, 30: 5.1}
EPS0 = 8.854e-18                                       # F/um


def plates(p):
    """Parallel-plate capacitance [fF] of the drawn capacitor, face by face, no fringe fields: (outer faces, pillar-side faces, inside of the U)."""
    k = 3.9 * EPS0 / (p["Ceot"] * 1e-4) * p["Wact"] * 1e-3 * 1e15 * 1e-3      # fF per nm of face length (EOT in um, width in um)
    h = 2 * p["Tgm"] + 2 * p["Tox"] + p["Tbody"]; w, d, L = p["Tcw"], p["Tcd"], p["Lcap"]
    if p["Cap"] == "blk": return k * 2 * L, k * h, 0.0
    return k * 2 * L, k * 2 * w, k * (2 * (L - w) + (h - 2 * w))            # inside: under both arms and along the wall (node side of the dielectric)


def matrix(rid):
    f = glob.glob(os.path.join(RUNS, rid, "*_ac_des.plt"))
    if not f: return None
    s = load(f[0]); c = {k[2:-1].replace(" ", ""): v[-1] * 1e15 for k, v in s.items() if k.startswith("c(")}
    return c


if __name__ == "__main__":
    print("run        struct      body | C(SN) total | SN-ground  SN-WL  SN-BL | plates: outer + pillar side + inside = sum | text of the paper   [fF]")
    for rid in sys.argv[1:]:
        c = matrix(rid); p = json.load(open(os.path.join(RUNS, rid, "run.json")))
        if c is None: print(f"{rid:10s} no extraction file"); continue
        g = lambda a, b: next((c[k] for k in (f"{a},{b}", f"{b},{a}") if k in c), float("nan"))
        est = plates(p["params"]) if p["params"]["Cap"] != "lump" else (0.0, 0.0, 0.0)
        print(f"{rid:10s} {p['struct']:11s} {p['params']['Tbody']:3g}  | {g('nSN', 'nSN'):8.3f}    | {-g('nSN', 'nGP'):8.3f} {-g('nSN', 'nWL'):6.3f} {-g('nSN', 'nBL'):6.3f} |"
              f" {est[0]:.2f} + {est[1]:.2f} + {est[2]:.2f} = {sum(est):.2f} | {TEXT.get(p['params']['Tbody'], float('nan')):.1f}")
    # self-check of the plate formula: two faces of 100 nm x 100 nm at EOT 3.8 A are 1.82 fF (NOTES (az))
    assert abs(plates(dict(Ceot=3.8, Wact=100, Tgm=20, Tox=5, Tbody=20, Tcw=10, Tcd=4, Lcap=100, Cap="blk"))[0] - 1.817) < 0.005
