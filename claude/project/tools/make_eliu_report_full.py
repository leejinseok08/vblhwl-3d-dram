# make_eliu_report_full.py - the complete report asked for on 2026-10-07 night ("everything, in eliU, once all of it - Codex's experiment
# included - has finished; with the remaining problems, the improvement measures and their explanation"). Reader: an EE junior; simple
# structure and short sentences, the real terms, every new idea tied to coursework, every number with unit and source. The page builder,
# the text checks and the style are those of tools/make_eliu_report.py; the text is in tools/eliu_full_text.py. New pictures
# gt2d_full_01 .. 07 go into Desktop\서강대\반엘프\pic_vbl_hwl_1t1c_3ddram, pictures of earlier rounds are reused from there; one HTML
# file with the pictures embedded goes into ...\results_vbl_hwl_1t1c_3ddram. Run on the PC: python tools/make_eliu_report_full.py
# Data: the run files of the shared working copy (claude/data/runs); Codex's results are read from origin/main of that repository
# (codex_updates/fin3_factorial_20261007/ranking.json; read, not edited). The numbers typed into the text are checked against the run
# files (check()). No picture of the paper is used: its values are numbers read off its figures.
import sys, os, glob, json, math, subprocess
os.environ["GT_RUNS"] = r"C:\Users\LEEJINSEOK\vblhwl-3d-dram\claude\data\runs"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import make_eliu_report as M
import make_eliu_report_1007 as R7
import eliu_full_text as T
import paper_targets as P
import gt_fig5c as G
import score2d as S
import gt_rh_ripple as RP
import gt_fbe_leak as LK
import gt_fbe_pairs as FP
import gt_hsu_fig2c as H                   # sets GT_W = 1 for later imports only: gt_fig5c is loaded already, its currents stay in amperes of the 0.1 um device
from gt_tran import PAPER_FBE
load, at, edges, key, save, clean, INK, RUNS, E = M.load, M.at, M.edges, M.key, M.save, M.clean, M.INK, M.RUNS, M.E
assert G.W == 0.1
REPO = r"C:\Users\LEEJINSEOK\vblhwl-3d-dram"; PIC = M.PIC; CDX = "codex_updates/fin3_factorial_20261007"
OUT = os.path.join(M.BASE, "results_vbl_hwl_1t1c_3ddram", "GT_IRPS2026_전체보고_eliU_2026-10-08.html")
PAP = "#c62828"; COL = M.COL
OLD = dict(cell="gt2d_eliu_01_cell.png", hsu="gt2d_hsu_fig2c_si_reference_round29.png", holes="gt2d_eliu1007_08_holes.png", pair="gt2d_eliu1007_01_pair.png",
           body="gt2d_eliu1007_04_body.png", ef="gt2d_electricfield_contact_avalanche_rounds21_28.png", hurkx="gt2d_hurkx_ab_rounds30_31.png", d3="gt2d_eliu1007_09_3d.png")
X3 = dict(swing=0.116, loss=0.00066)        # 3D X-X' pair of 2026-10-06 (X3p, text Cs 4.2 fF; NOTES (aw)): its raw files are not in the shared copy
F6E = dict(xx=0.70, yy=0.0, row=0.128)      # Fig.6(e) read on 2026-10-08 (tools/gt_rh_ripple.py): reversible swing of the node [mV], one pixel row [mV]

# ------------------------------------------------------------------ data
def scores(tag):          # the seven group scores of a configuration with the present scorer
    iv = S.iv(tag)[0]; w = S.write(tag)[0]; (br, l1, l2), _ = S.fbe(tag); (rh, ri), _ = S.rh(tag)
    return dict(IV=iv, W=w, BR=br, L1=l1, L2=l2, RH=rh, RI=ri)

def fbe_case(tag, c):     # one FBE run with the scorer's definitions: holes at t_A, bar, losses from the node when it is charged
    rid = f"D{tag}F_c{c}"; d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
    t = s["time"]; sn = s[key(s, "nSN)")]; T_ = dv["time"]; t0 = edges(t, s[key(s, "nWL)")], 0, 1.8, False)[0] + 4e-11
    f = edges(t, s[key(s, "nBL")], 0, 1.1, False); r = [x for x in edges(t, s[key(s, "nBL")], 0, 1.1, True) if x > f[0]]; v0 = at(t, sn, t0)
    ka = next(q for q in dv if q.startswith("AveWindow((0.075") and "ElectrostaticPotential" in q); L = lambda x: (v0 - at(t, sn, x)) * 1e3
    return dict(holes=at(T_, dv[next(q for q in dv if "hDensity" in q)], f[0] - 3e-10) * 1e-13, bar=(at(T_, dv[ka], f[0] + 5e-10) - dv[ka][0]) * 1e3,
                first=L(r[0] - 3e-10), two=L(r[1] - 3e-10), l200=L(t0 + 2e-7))

def numbers():            # everything the text types, from the run files
    D = dict(n=len([d for d in os.listdir(RUNS) if os.path.isdir(os.path.join(RUNS, d)) and not d.startswith("_")]), sc={t: scores(t) for t in ("b0", "fin3", "fin5")})
    D["iv"] = {}
    for c in range(1, 6):
        pts = G.curve(os.path.join(RUNS, f"DdyI_c{c}")); v = [G.cross(pts, i) for i in (1e-10, 1e-8, 1e-6)]
        D["iv"][c] = dict(v=v, dev=[v[0] - G.PAPER[c]["v10"], v[1] - G.PAPER[c]["v8"], v[2] - G.PAPER[c]["v6"]], ss=(v[1] - v[0]) / 2 * 1e3, lm1=G.at(pts, -1.0))
    D["w"] = {r: [at(*R7.write(r), x) for x in (12, 24, 39, 60)] for r in ("DdyW_c2", "DfinW_c2", "Db0W_c2", "Dd7W_c2")}
    D["f"] = {c: fbe_case("dy", c) for c in range(1, 6)}; D["leak"] = {c: LK.leak(f"DdyF_c{c}") for c in range(1, 6)}
    D["rp"] = {r: RP.ripple(r) for r in ("DdyRy_yy", "DdyRzb_zz", "DdyRzbg_zz", "QSid_zz", "Dr2Ry_yy", "Dr2Rz_zz", "Dx2Ry_yy", "Dx7Ry_yy", "Dx2Rz_zz", "Dx7Rz_zz")}
    D["h"] = {r: R7.hammer(r) for r in ("DdyRzb_zz", "DdyRzbi_zz", "Dg9Rzbi_zz", "Dg8Rzi_zz", "Dg0Rzbi_zz", "Dg6Rzi_zz", "Dg7Rzbg_zz", "Dg3Rzg_zz", "Dg4Rzg_zz", "Dg1Ryi_yy")}
    pts = G.curve(os.path.join(RUNS, "DhyI_c3")); D["hsu"] = [G.at(pts, v) + 1.0 - H.HSU[v] for v in (-0.7, -0.8, -0.9, -1.0, -1.25, -1.5, -1.75)]      # A/um = A of the 0.1 um device x 10
    D["d3"] = R7.fbe("E3S2_c2"); D["l5"] = lambda r: sum(D["rp"][r]["loss"][-5:]) / 5
    D["fc"] = {t: {c: fbe_case(t, c) for c in range(1, 5)} for t in ("dl", "dm")}; D["sc"].update({t: scores(t) for t in ("fin3n", "fin4")})      # the two configurations without an avalanche model: axis / end contact
    def wpairs(rid):      # pairs made by impact ionization from the start of the transient to the WL switch-off (the write)
        d = os.path.join(RUNS, rid); s = load(os.path.join(d, rid + "_sys.plt")); dv = load(glob.glob(os.path.join(d, "*_dev.plt"))[0])
        return at(dv["time"], FP.cum(dv["time"], dv[next(x for x in dv if "ImpactIonization" in x)]), edges(s["time"], s[key(s, "nWL)")], 0, 1.8, False)[0] + 4e-11) * FP.W
    D["wp"] = {t: [wpairs(f"D{t}F_c{c}") for c in range(1, 6)] for t in ("b0", "fin")}
    return D

def check(D):             # the numbers typed into tools/eliu_full_text.py against the run files
    near = lambda a, b, tol: abs(a - b) <= tol; f = D["f"]; s5 = D["sc"]["fin5"]; l5 = D["l5"]
    c = [D["n"] == 507, [round(s5[k], 2) for k in ("IV", "W", "BR", "L1", "L2", "RH", "RI")] == [0.72, 1.12, 0.10, 0.42, 1.46, 4.42, 11.88],
         [round(D["sc"]["fin3"][k], 2) for k in ("IV", "W", "BR", "L1", "L2")] == [0.73, 0.93, 0.02, 0.48, 1.48],
         sum(1 for q in D["iv"].values() for x in q["dev"] if abs(x) <= 0.0205) == 12, all(0.03 <= x <= 0.04 for x in D["iv"][5]["dev"]),
         all(60.15 <= q["ss"] <= 60.35 for q in D["iv"].values()), all(abs(D["iv"][k]["lm1"] - G.PAPER[k]["lm1"]) < 0.2 for k in D["iv"]),
         [round(D["iv"][k]["v"][1], 2) for k in range(1, 6)] == [0.48, 0.45, 0.43, 0.39, 0.69], [round(D["iv"][k]["lm1"], 2) for k in range(1, 6)] == [-13.42, -13.21, -13.16, -13.39, -12.86],
         [round(x, 3) for x in D["w"]["DdyW_c2"]] == [0.736, 0.912, 1.015, 1.083], [round((x - y) * 1e3) for x, y in zip(D["w"]["DdyW_c2"][2:], (1.06, 1.13))] == [-45, -47],
         [round(f[k]["holes"]) for k in range(1, 6)] == [1601, 1371, 1307, 1130, 1349], [round(f[k]["bar"]) for k in range(1, 6)] == [557, 448, 367, 323, 372],
         [round(f[k]["first"], 2) for k in range(1, 6)] == [82.76, 22.20, 4.92, 3.82, 0.14], [round(f[k]["l200"], 1) for k in (1, 2, 3, 5)] == [165.1, 63.9, 15.5, 1.6],
         near(f[4]["two"], 5.81, 0.006), near(f[5]["l200"], 1.58, 0.006), 1.49 < f[1]["first"] / 55 < 1.52, 1.64 < f[1]["l200"] / 100 < 1.66,
         [round(D["leak"][k]["hi"] * D["leak"][k]["C"] * 1e12, 1) for k in range(1, 6)] == [7.0, 9.7, 9.5, 8.7, 13.5], near(D["leak"][5]["L"] * 1e-3 * D["leak"][5]["C"] / 1.602e-19, 15.2, 0.1),
         near(l5("DdyRy_yy"), 0.00138, 2e-5), near(l5("DdyRzb_zz"), 0.00138, 2e-5), near(D["rp"]["DdyRzb_zz"]["sw"][5], 0.472, 0.002), abs(D["rp"]["DdyRy_yy"]["sw"][5]) < 0.001,
         near(D["rp"]["QSid_zz"]["sw"][5], 0.201, 0.002), near(l5("Dx2Ry_yy"), 0.00115, 2e-5), near(l5("Dx7Ry_yy"), 0.00019, 2e-5), near(l5("Dx2Rz_zz"), 0.00115, 2e-5),
         near(l5("Dx7Rz_zz"), 0.00020, 2e-5), near(l5("Dr2Ry_yy"), 0.0006, 1e-4), near(D["rp"]["Dr2Rz_zz"]["loss"][0], 0.093, 0.001), near(l5("Dr2Rz_zz"), 0.0003, 1e-4),
         near(D["h"]["DdyRzb_zz"]["pulse"], 0.0, 0.05), near(D["h"]["DdyRzbi_zz"]["body"][-1], 39.9, 0.2), round(D["h"]["DdyRzbi_zz"]["hend"][-1] - D["h"]["DdyRzbi_zz"]["hend"][0]) == 46,
         [round(D["h"][r]["pulse"]) for r in ("Dg9Rzbi_zz", "Dg8Rzi_zz", "Dg0Rzbi_zz", "Dg6Rzi_zz")] == [157, 174, 280, 320], near(D["h"]["Dg1Ryi_yy"]["cyc"][2], 0.17, 0.01),
         near(D["h"]["Dg1Ryi_yy"]["cyc"][-1], 3.75, 0.01), 3.0 <= min(D["h"]["Dg0Rzbi_zz"]["cyc"][1:]) and max(D["h"]["Dg8Rzi_zz"]["cyc"]) <= 11.3,
         [round(sum(D["h"][r]["cyc"][-5:]) / 5, 3) for r in ("Dg7Rzbg_zz", "Dg3Rzg_zz", "Dg4Rzg_zz")] == [0.008, 0.010, 0.013], 0.045 <= min(D["hsu"]) and max(D["hsu"]) <= 0.125,
         near(D["d3"]["avg"], 458, 1), near(D["d3"]["first"], 27.55, 0.03), near(D["d3"]["l200"], 59.4, 0.1),
         [(round(D["fc"]["dl"][k]["first"], 1), round(D["fc"]["dl"][k]["l200"], 1)) for k in (1, 2, 3)] == [(60.9, 112.9), (18.6, 49.1), (4.4, 12.9)],
         [(round(D["fc"]["dm"][k]["first"], 1), round(D["fc"]["dm"][k]["l200"], 1)) for k in (1, 2, 3)] == [(81.6, 163.8), (21.5, 62.8), (4.7, 14.9)],
         (round(D["fc"]["dl"][4]["first"], 1), round(D["fc"]["dl"][4]["two"], 2), round(D["fc"]["dm"][4]["first"], 1), round(D["fc"]["dm"][4]["two"], 2)) == (3.4, 5.01, 3.7, 5.58),
         [round(D["sc"][t][k], 2) for t in ("fin3n", "fin4") for k in ("L1", "L2")] == [0.45, 1.42, 0.43, 1.46],
         all(abs(D["fc"]["dl"][k]["l200"] / P.FBE_200[k] - 1) <= 0.13 for k in (1, 2, 3)), near(D["fc"]["dm"][1]["l200"] / 100, 1.64, 0.005),
         all(abs(D["f"][k][m] / D["fc"]["dm"][k][m] - 1) <= 0.05 for k in range(1, 5) for m in ("first", "l200", "two")),
         (round(min(D["wp"]["b0"])), round(max(D["wp"]["b0"])), round(min(D["wp"]["fin"])), round(max(D["wp"]["fin"]))) == (620, 902, 132, 224)]
    # arithmetic of the text
    q = 1.602e-19; e0 = 8.854e-12
    c += [near(4.2e-15 * 0.72 / 12e-12 * 1e6, 252, 0.5), near(1.8e-15 * 1.38e-6 / 0.188e-9 * 1e12, 13.2, 0.1), near(3.9 * e0 / 3.8e-10 * 1e3, 90.9, 0.1), near(2 * 0.01 * 90.9, 1.82, 0.01),
          near(4.2 / 90.9, 0.046, 0.0005), near(1371 * q * 1e15, 0.22, 0.005), near(1371 * q / 1.8e-15 * 1e3, 122, 0.5), near(F6E["xx"] * 1e-3 / 1.8 * 1.8e-15 * 1e18, 0.70, 0.005),
          near(F6E["xx"] * 1e-3 / 1.8 * 4.2e-15 * 1e18, 1.63, 0.01), near(X3["swing"] * 1e-3 / 1.8 * 4.2e-15 * 1e18, 0.27, 0.005), near(1.8e-15 * 0.0535e-3 / 0.188e-9 * 1e9, 0.51, 0.01),
          near(1.58 * 1.54 / 0.5, 4.87, 0.01), near(0.605 / 11.3e3 * 1e3, 0.0535, 1e-4), near(1e-9 * 10e-9 / 1.8e-15 * 1e3, 5.6, 0.05), near(13.5e-12 * 179e-9 / q, 15.1, 0.1)]
    n15 = sum(1 for k in range(1, 6) if abs(f[k]["bar"] - P.FBE_RISE[k]) <= 30) + sum(1 for k in range(1, 5) if abs(math.log10(f[k]["first"] / P.FBE_FIRST[k])) <= 0.3) + (f[5]["first"] <= 0.5) \
        + sum(1 for k in (1, 2, 3) if abs(math.log10(f[k]["l200"] / P.FBE_200[k])) <= 0.3) + (abs(math.log10(f[4]["two"] / 5.0)) <= 0.3) + (f[5]["l200"] <= 0.5)
    c.append(n15 == 14)
    assert all(c), [i for i, x in enumerate(c) if not x]
    return len(c)

# ------------------------------------------------------------------ Codex's factorial experiment (read from origin/main, not edited)
SNAP = os.path.join(REPO, "claude", "data", "tables", "codex_fin3_ranking_as_read.json")      # made by tools/codex_rank_snapshot.py from a copy of Codex's result files
def codex():              # the ranking of Codex's experiment: the copy of its result files read from the server when there is one, else origin/main
    g = lambda *a: subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, timeout=180)
    if os.path.exists(SNAP):
        j = json.load(open(SNAP, encoding="utf-8")); return dict(j=j, n=j["result_files"], commit="server copy read at " + j["read_at"])
    g("fetch", "-q", "origin")
    r = g("show", f"origin/main:{CDX}/ranking.json")
    if r.returncode: print("Codex's ranking could not be read:", r.stderr.decode("utf-8", "replace")[:200]); return None
    j = json.loads(r.stdout.decode("utf-8")); n = len([x for x in g("ls-tree", "-r", "--name-only", "origin/main", f"{CDX}/results/").stdout.decode().split() if x.endswith(".json")])
    return dict(j=j, n=n, commit=g("log", "-1", "--format=%h %cd", "--date=format:%m-%d %H:%M", "origin/main").stdout.decode().strip())

PREP = lambda g: "모델의 GIDL로 채움" if g["preparation"] == "natural" else {"uniform": "쌍을 몸체 전체에 넣음", "bl": "쌍을 BL 쪽 25 nm에 넣음", "sn": "쌍을 SN 쪽 25 nm에 넣음"}[g["window"]]
LEV = [("준비 방법", PREP), ("양 또는 시간의 배율", lambda g: f"{float(g['factor']):g}배"), ("준비하는 동안의 SN", lambda g: {"clamped": "1.1 V에 고정", "early": "일찍 풂", "late_reset": "BL 하강 직전에 다시 1.1 V"}[g["SN"]]),
       ("avalanche 모델", lambda g: "켬" if int(g["II"]) else "끔"), ("저장 노드 용량", lambda g: {"write_fit": "쓰기 곡선에 맞춘 값", "text": "본문의 값"}[g["Cs"]])]

def my_scores(c, v):      # my scorer's three numbers for one case from (bar, first-phase loss, losses after each low phase, loss at 200 ns)
    bar, first, low, l200 = v; fl = P.FBE_FLAT.get(c); last = P.FBE_LAST.get(c); el = lambda a, b: abs(math.log10(max(a, P.FLOOR) / max(b, P.FLOOR))) / P.DEC_TOL
    return (abs(bar - P.FBE_RISE[c]) / P.FBE_RISE_TOL, first / fl if fl else el(first, P.FBE_FIRST[c]), l200 / fl if fl else el(low[last[0] - 1], last[1]) if last else el(l200, P.FBE_200[c]))

def rescore(g):           # my scorer on one of Codex's groups. Codex counts the losses from the node just before the first BL fall; with the late reset the node is set to
    # 1.1 V after that reading, so the droop of the hold is added back (loss from the reset node). Returns per case the four quantities and the three scores, and the
    # worst score without the later loss of Case 5 (the hold leak of problem P5: about 1.6 mV in every group, whatever the preparation).
    v = {}
    for c in g["cases"]:
        d = -c["SN_prefall_error_mV"] if g["SN"] == "late_reset" else 0.0; low = [x + d for x in c["low_phase_loss_mV"]]
        v[c["case"]] = (c["body_avg_fin3_mV"], low[0], low, c["loss200_paper_axis_mV"] + d)
    sc = {k: my_scores(k, x) for k, x in v.items()}
    return v, sc, max(x for k, t in sc.items() for i, x in enumerate(t) if (k, i) != (5, 2))

def mine(g):              # pass by my scoring: every item inside its tolerance and the node at 1.1 V at t_A (kept there, or set there just before the fall)
    return rescore(g)[2] <= 1 and (g["SN"] == "late_reset" or bool(g["SN_precondition_all_pass"]))

SNK = {"clamped": "1.1 V에 고정", "late_reset": "풀어 뒀다가 BL 하강 직전에 다시 1.1 V"}
SNV = {"clamped": "SN을 1.1 V에 고정하고", "late_reset": "SN을 풀어 뒀다가 다시 1.1 V로 올리고"}; IIV = {1: "avalanche 모델을 켠", 0: "avalanche 모델을 끈"}
def common_time(C):       # measure M2: one hold time for all five cases, interpolated from Codex's natural-generation runs (0.8 / 1.0 / 1.2 of each case's own time)
    out = []
    for sn in ("clamped", "late_reset"):
        for ii in (1, 0):
            gs = {float(g["factor"]): g for g in C["j"]["ranking"] if g["preparation"] == "natural" and g["SN"] == sn and g["Cs"] == "write_fit" and int(g["II"]) == ii}
            if sorted(gs) != [0.8, 1.0, 1.2]: continue
            V = {f: rescore(g)[0] for f, g in gs.items()}; Tm = {f: {c["case"]: c["hold_ns"] for c in g["cases"]} for f, g in gs.items()}
            def val(c, tc, V=V, Tm=Tm):     # the four quantities of case c at the hold time tc [ns]: linear in log t between the three runs (losses in log)
                f = sorted(V); t = [Tm[x][c] for x in f]; i = 0 if tc <= t[1] else 1; w = math.log(tc / t[i]) / math.log(t[i + 1] / t[i]); a, b = V[f[i]][c], V[f[i + 1]][c]
                lin = lambda x, y: x + (y - x) * w; lg = lambda x, y: math.exp(lin(math.log(max(x, 1e-4)), math.log(max(y, 1e-4))))
                return (lin(a[0], b[0]), lg(a[1], b[1]), [lg(x, y) for x, y in zip(a[2], b[2])], lg(a[3], b[3]))
            item = lambda c, tc: max(x for i, x in enumerate(my_scores(c, val(c, tc))) if (c, i) != (5, 2))
            lo = max(Tm[0.8].values()); hi = min(Tm[1.2].values()); ts = [lo + (hi - lo) * i / 200 for i in range(201)]
            per = {c: [item(c, tc) for tc in ts] for c in range(1, 6)}; worst = [max(per[c][i] for c in per) for i in range(len(ts))]; k = min(range(len(ts)), key=lambda i: worst[i])
            out.append(dict(sn=sn, ii=ii, lo=lo, hi=hi, ts=ts, per=per, worst=worst, best=worst[k], tbest=ts[k], at={c: val(c, ts[k]) for c in per}, at_sc={c: my_scores(c, val(c, ts[k])) for c in per},
                            ok={f: mine(g) for f, g in gs.items()}, times={f: [Tm[f][c] for c in range(1, 6)] for f in Tm}, own={f: rescore(g)[2] for f, g in gs.items()}))
    return dict(cfg=out, **min(out, key=lambda o: o["best"])) if out else None

def codex_text(C, K):     # the sentences and the table of the section on Codex, and the sentences of the first section
    base = ["Codex는 같은 저장소에서 제 결과를 따로 검증하는 도구예요.", "10월 5일부터 제 결과를 독립적으로 다시 계산했어요.", "WL 저항의 손실이 쌓이지 않는다는 것을 Codex가 확인했어요.",
            "SN을 일찍 풀면 31~38 mV 내려간다는 것도 Codex가 찾았어요.",
            "10월 7일에는 fin3를 기준으로 조건 조합 실험을 시작했어요.", "실행은 720개예요.", "Case 5개에 준비 방법 12가지, SN 처리 3가지, avalanche 2가지, 용량 2가지를 곱한 수예요.",
            "준비 방법은 몸체에 정공을 채우는 방법이에요.", "하나는 모델 자체의 GIDL로 14.6~20.6 µs 동안 채우는 것이에요.", "다른 하나는 전자–정공 쌍을 넣어 주는 것이에요.",
            "넣는 자리는 몸체 전체, BL 쪽 25 nm, SN 쪽 25 nm 세 가지예요.", "양과 시간은 0.8배, 1.0배, 1.2배예요.", "SN 처리는 세 가지예요.",
            "준비하는 동안 1.1 V에 고정하기, 처음에만 맞추고 풀어 두기, 풀어 뒀다가 BL 하강 직전에 다시 맞추기예요.", "판정의 허용치는 막대 30 mV, 손실 0.3 decade예요."]
    if not C: return dict(one=["Codex의 조건 조합 실험은 결과를 읽지 못했어요."], body=base + ["이 보고서를 만들 때 Codex의 결과 파일을 읽지 못했어요."], pic=None, cap=None, table=None)
    R = C["j"]["ranking"]; n = len(R); ok = [g for g in R if g["all_cases_pass"]]; my = [g for g in R if mine(g)]; done = C["n"] >= 720 and n >= 144; ln = [g for g in R if g["SN"] == "late_reset" and g["preparation"] == "natural"]; dr = [-c["SN_prefall_error_mV"] for g in ln for c in g["cases"]]
    body = base + [f"결과 파일은 {C['n']}개, 다섯 Case가 다 끝난 조합은 {n}개예요.", f"Codex의 채점으로는 그중 {len(ok)}개가 다섯 Case를 모두 통과했어요."]
    if not done: body.append("이 숫자는 실험이 끝나기 전의 중간 값이에요.")
    body += ["Codex의 채점에서 한 가지를 짚어 둬요.", "Codex는 손실을 BL 하강 직전의 SN 전압에서부터 세요.", "SN을 하강 직전에 다시 맞춘 조합에서는 그 전압이 다시 맞추기 전의 값이에요.",
             f"모델의 GIDL로 채운 조합은 그동안 SN이 {min(dr):.0f}~{max(dr):.0f} mV 내려가 있어요." if dr else "모델의 GIDL로 채운 조합은 아직 결과가 없어요.",
             f"그래서 그 조합 {len(ln)}개는 손실이 음수로 나오고 점수가 {int(min(g['max_score'] for g in ln))}점을 넘어요." if ln else "그 조합의 점수는 아직 없어요.",
             "다시 맞춘 1.1 V에서부터 세면 결과가 달라져요.", "그래서 Codex의 결과 파일을 제 채점 방식으로 다시 셌어요.", "Codex의 파일은 읽기만 했어요.",
             "Case 5의 200 ns 손실은 이 셈에서 뺐어요.", "어느 조합에서나 약 1.6 mV라서 준비 방법을 가리지 못하기 때문이에요.", "t_A에 SN이 1.1 V인 조합만 통과로 쳤어요.",
             f"그렇게 세면 {len(my)}개가 통과해요.", "아래 표는 조건별로 통과한 조합의 수예요.", "분모는 그 조건을 쓴 조합의 수예요."]
    rows = []
    for name, fn in LEV:
        lev = sorted({fn(g) for g in R})
        cnt = lambda S_: "<br>".join(f"{sum(1 for g in S_ if fn(g) == l)} / {sum(1 for g in R if fn(g) == l)}" for l in lev)
        rows.append((name, "<br>".join(lev), cnt(ok), cnt(my)))
    nat = [g for g in my if g["preparation"] == "natural"]; prx = [g for g in my if g["preparation"] == "proxy"]; txt = [g for g in my if g["Cs"] == "text"]; sn = [g for g in my if g.get("window") == "sn"]
    body += [f"통과한 {len(my)}개 중 모델의 GIDL로 채운 조합이 {len(nat)}개, 쌍을 넣어 준 조합이 {len(prx)}개예요.", "두 방법이 같은 결과를 줘요.", "그러니 Fig. 8을 정하는 것은 t_A의 몸체 상태예요.",
             "그 상태를 무엇이 만들었는지는 이 실험으로 가릴 수 없어요.", f"본문의 용량을 쓴 조합은 {len(txt)}개가 통과했어요.", f"쌍을 SN 쪽 25 nm에 넣은 조합은 {len(sn)}개가 통과했어요.",
             "배율을 20 % 바꾸면 대부분 허용치를 벗어나요.", "정공 전하에 그만큼 민감하다는 뜻이에요."]
    b = min(my, key=lambda g: rescore(g)[2]) if my else None
    if b:
        v, _, w = rescore(b)
        body += [f"제 채점으로 가장 좋은 조합은 가장 나쁜 점수가 {w:.2f}예요.", f"{PREP(b)}, 배율 {float(b['factor']):.1f}, avalanche 모델 {LEV[3][1](b)}인 조합이에요.",
                 f"거기서 Case 1의 손실은 {v[1][1]:.1f} mV와 {v[1][3]:.1f} mV예요.", "논문은 55 mV와 100 mV예요.", "이 실험의 구조는 BL 접촉이 기둥 축인 fin3예요.",
                 "12절의 접촉 위치 표와 같은 방향의 결과예요."]
    if K: body += ["이 자료로 방안 M2를 바로 계산해 봤어요.", "결과는 19절에 있어요."]
    one = ["Codex의 조건 조합 실험 720개가 끝났어요." if done else f"Codex의 조건 조합 실험은 720개 중 {C['n']}개가 끝났어요.", f"조합 {n}개 중 {len(my)}개가 제 채점으로 다섯 Case를 모두 통과했어요.",
           "정공을 채우는 방법이 달라도 t_A의 몸체 상태가 같으면 결과가 같아요."]
    return dict(one=one, body=body, pic="codex", cap="왼쪽은 조합별 점수(다섯 Case 중 가장 나쁜 값), 오른쪽은 조건별로 통과한 조합의 비율이에요. 실행과 결과 파일은 Codex의 것이고, 채점은 본문에 적은 제 방식이에요.",
                table=(["조건", "수준", "Codex의 채점: 통과 / 조합", "제 채점: 통과 / 조합"], rows))

def m2_text(K):           # section 19 once the common-time calculation exists (measure M2 carried out with Codex's data)
    if not K: return None
    c = K["at"]; s = K["at_sc"]; ok = K["best"] <= 1; t = K["tbest"] / 1e3; us = lambda v: " / ".join(f"{x / 1e3:.1f}" for x in v)
    rows = [(f"Case {k}", f"{c[k][0]:.0f} / {P.FBE_RISE[k]}", f"{c[k][1]:.3g} / {P.FBE_FIRST[k]:g}",
             (f"{c[k][2][1]:.2f} / 5.0 (BL-low 2회 뒤)" if k == 4 else f"{c[k][3]:.1f} / {'0.5 이하 (P5, 셈에서 뺌)' if k == 5 else format(P.FBE_200[k], 'g')}"),
             f"{max(x for i, x in enumerate(s[k]) if (k, i) != (5, 2)):.2f}") for k in range(1, 6)]
    won = [(o, f) for o in K["cfg"] for f in sorted(o["ok"]) if o["ok"][f]]
    dev = {k: c[k][0] - P.FBE_RISE[k] for k in c}; hi_, lo_ = max(dev, key=dev.get), min(dev, key=dev.get)      # bars rise with the hold time: one too high and one too low cannot both be mended
    mono = [f"하지만 방향은 알 수 있어요.", f"그 시간에서 Case {hi_}의 막대는 {dev[hi_]:.0f} mV 높고 Case {lo_}의 막대는 {-dev[lo_]:.0f} mV 낮아요.", "막대는 시간이 길수록 커져요.",
            "그래서 시간을 늘려도 줄여도 두 Case가 함께 맞지 않아요."] if dev[hi_] > 30 and dev[lo_] < -30 else []
    sent = ["P1을 전하 보존으로 따져 볼게요.", "쌍이 생기면 전자와 정공이 하나씩이에요.", "정공이 몸체에 남으면 전자는 SN이나 BL로 가요.",
            "전자가 SN으로 가면 SN 전압이 내려가요.", "정공 1371개는 0.22 fC예요.", "1.8 fF에서 ΔV = Q/C = 122 mV예요.", "논문의 SN은 1.1 V에서 시작해요.",
            "그러니 두 가지 길만 남아요.", "하나는 전자가 BL로 빠지는 길이에요.", "다른 하나는 SN을 다시 1.1 V로 올리는 길이에요.",
            "두 번째 길은 실제 DRAM의 refresh와 같아요.", "refresh는 셀의 전하를 주기적으로 다시 쓰는 동작이에요.", "유지하는 동안 GIDL이 몸체를 채워요.", "refresh가 SN만 1.1 V로 되돌려요.",
            "Codex의 실험에 바로 이 길이 들어 있어요.", "GIDL로 채우는 동안 SN을 1.1 V에 고정한 경우가 하나예요.", "풀어 뒀다가 BL 하강 직전에 다시 1.1 V로 올린 경우가 다른 하나예요."]
    for o, f in won:
        sent.append(f"{SNV[o['sn']]} {IIV[o['ii']]} 조합은 배율 {f:.1f}에서 통과해요.")
    if won:
        o, f = won[0]; sent += ["Case마다 시간을 따로 주면 Fig. 8의 숫자가 나온다는 뜻이에요.", f"예를 들어 첫 조합의 시간은 Case 1~5에서 {us(o['times'][f])} µs예요.",
                                f"가장 긴 Case 1은 가장 짧은 Case 5의 {o['times'][f][0] / o['times'][f][4]:.2f}배예요."]
    else: sent.append("제 채점으로는 어느 조합도 통과하지 못했어요.")
    sent += ["실제 이력이라면 시간이 하나여야 해요.", "그래서 0.8배, 1.0배, 1.2배의 세 점 사이를 이어서 공통 시간 하나에서의 값을 계산했어요.", "새 실행은 하지 않았어요.",
             f"다섯 Case가 모두 계산된 범위는 {K['lo'] / 1e3:.1f}~{K['hi'] / 1e3:.1f} µs예요.", f"계산한 조합 {len(K['cfg'])}개 중 가장 좋은 것은 {SNV[K['sn']]} {IIV[K['ii']]} 경우예요.",
             f"가장 좋은 공통 시간은 {t:.1f} µs이고, 그때 가장 나쁜 점수가 {K['best']:.2f}예요."]
    sent += (["1 이하이니 다섯 Case가 함께 허용치 안이에요.", "즉 유지 시간 하나로 Fig. 8의 숫자가 나와요.", "GIDL로 채우고 SN을 다시 올리는 이력이 출처의 후보가 됐어요.",
              "다만 세 점을 이은 값이라 그 시간으로 직접 돌려 확인해야 해요.", "그리고 논문이 그런 이력을 썼는지는 논문에 적혀 있지 않아요."] if ok else
             ["1보다 크니 시간 하나로는 다섯 Case가 함께 나오지 않아요.", "같은 시간 동안 GIDL이 넣는 전하가 Case마다 다르기 때문이에요.", "일함수가 큰 Case 5가 가장 빨리 차요.",
              "논문의 막대는 다섯 Case에 거의 같은 전하를 요구해요.", "그러니 GIDL로 채우는 이력만으로는 출처를 설명하지 못해요.", "정공 전하는 계속 조건으로 남아요.",
              "이 범위 밖의 공통 시간은 Codex의 자료로는 계산할 수 없어요."] + mono)
    sent += ["아래 표가 그 공통 시간에서의 값이에요.", "값은 모델 / 논문 순서예요."]
    return dict(sent=sent, table=(["Case", "막대 [mV]", "첫 BL-low 구간 손실 [mV]", "나중 손실 [mV]", "가장 나쁜 점수"], rows), ok=ok, t=t, best=K["best"])

# ------------------------------------------------------------------ new pictures (paper = open markers or hatched bars)
def fig_score(SC):
    G_ = [("Id–Vg (Fig. 5(c))", "IV"), ("쓰기 (Fig. 4(a))", "W"), ("몸체 전위 막대 (Fig. 8(a))", "BR"), ("FBE: 첫 BL-low 구간 손실 (Fig. 8(b), (c))", "L1"), ("FBE: 나중 손실 (Fig. 8(b), (c))", "L2"),
          ("로우 해머 (Fig. 6(e))", "RH"), ("로우 해머 + 충돌 이온화 (Fig. 7)", "RI")]
    fig, ax = plt.subplots(figsize=(14, 6.8)); n = len(G_); box = dict(fc="white", ec="none", pad=1.2)
    for i, (name, k) in enumerate(G_):
        y = n - 1 - i
        for dy, tag, colr, fs in ((0.27, "b0", M.GREY, 10.5), (0.0, "fin3", "#90caf9", 10.5), (-0.27, "fin5", None, 12.5)):
            v = SC[tag][k]; c = colr or (M.GREEN if v < 1 else M.YELLOW if v < 3 else M.RED)
            ax.barh(y + dy, v, 0.24, color=c, zorder=3); ax.text(v * 1.07, y + dy, f"{v:.2f}", va="center", fontsize=fs, color=INK, fontweight="bold" if tag == "fin5" else "normal", bbox=box, zorder=5)
    ax.set_xscale("log"); ax.set_xlim(0.012, 60); ax.set_yticks(range(n)); ax.set_yticklabels([g[0] for g in G_][::-1], fontsize=12.5)
    ax.axvline(1.0, color="#2e7d32", ls="--", lw=2, zorder=4); ax.text(0.93, n - 0.36, "점수 1 = 그림을 읽는 오차의 한계\n(이 선보다 왼쪽이면 재현)", ha="right", va="bottom", fontsize=11.5, color="#2e7d32")
    ax.set_xticks([0.02, 0.1, 0.5, 1, 2, 5, 10, 20]); ax.set_xticklabels(["0.02", "0.1", "0.5", "1", "2", "5", "10", "20"], fontsize=11); ax.minorticks_off()
    ax.set_xlabel("점수 = (모델 - 논문) ÷ 허용 오차의 제곱평균제곱근 (작을수록 좋음)", fontsize=12.5); ax.set_ylim(-0.7, n + 1.15); ax.grid(axis="x", alpha=0.25, zorder=0)
    ax.barh([-5], [1], color=M.GREY, label="처음 (b0: 본문의 값 그대로, 10월 6일 아침)"); ax.barh([-5], [1], color="#90caf9", label="fin3 (10월 7일 아침)")
    ax.barh([-5], [1], color=M.GREEN, label="fin5 (지금): 1 미만"); ax.barh([-5], [1], color=M.YELLOW, label="fin5: 1~3"); ax.barh([-5], [1], color=M.RED, label="fin5: 3 이상")
    ax.legend(loc="upper right", fontsize=10.5, frameon=True, ncol=2); ax.set_title("점수판: 논문 그림별로 얼마나 가까운가", fontsize=17, fontweight="bold", color=INK, pad=12); clean(ax)
    return save(fig, "gt2d_full_01_score.png")

def fig_idvg():
    fig, ax = plt.subplots(figsize=(13, 6.6)); nm = ["Case 1: 30 nm, 1e18, WF 4.7", "Case 2: 20 nm, 1e18, WF 4.7", "Case 3: 10 nm, 1e18, WF 4.7", "Case 4: 10 nm, 1e16, WF 4.7", "Case 5: 10 nm, 1e16, WF 5.0"]
    for c in range(1, 6):
        p = [q for q in G.curve(os.path.join(RUNS, f"DdyI_c{c}")) if q[1] > 0]; ax.plot([v for v, i in p], [i for v, i in p], color=COL[c], lw=2.2, label=nm[c - 1], zorder=3)
        q = G.PAPER[c]; ax.plot([q["v10"], q["v8"], q["v6"], -1.0, q["vmin"]], [1e-10, 1e-8, 1e-6, 10.0 ** q["lm1"], 10.0 ** q["lmin"]], "o", mfc="white", color=COL[c], ms=8, mew=2, zorder=4)
    ax.plot([], [], "o", mfc="white", color=INK, ms=8, mew=2, label="논문 Fig. 5(c) (그림에서 읽은 값)")
    ax.set_yscale("log"); ax.set_xlim(-1.05, 1.85); ax.set_ylim(1e-18, 1e-3); k = range(-18, -2, 2); ax.set_yticks([10.0 ** q for q in k]); ax.set_yticklabels([f"1e{q}" for q in k], fontsize=11); ax.minorticks_off()
    ax.set_xlabel("게이트 전압 [V]  (BL 1.1 V)", fontsize=12.5); ax.set_ylabel("드레인 전류 [A]  (폭 0.1 µm)", fontsize=12.5); ax.legend(fontsize=10.5, loc="lower right"); ax.grid(alpha=0.25); clean(ax)
    ax.set_title("Fig. 5(c): Id–Vg 다섯 Case (선 = 모델 fin5, 동그라미 = 논문)", fontsize=16, fontweight="bold", color=INK, pad=10)
    return save(fig, "gt2d_full_02_idvg.png")

def fig_write():
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    for rid, lab, col, ls in (("DdyW_c2", "fin5: avalanche 모델 없음, 1.8 fF (맞춘 값)", "#1565c0", "-"), ("DfinW_c2", "fin3: 기본 구동력의 avalanche 모델, 1.8 fF", "#90a4ae", "-"),
                              ("Db0W_c2", "본문의 4.2 fF (avalanche 모델, 기본 구동력)", "#455a64", ":"), ("Dd7W_c2", "ElectricField 구동력, 5.67 fF (기각한 구성)", "#6a1b9a", "--")):
        t, v = R7.write(rid); ax.plot(t, v, color=col, lw=2.4, ls=ls, zorder=3, label="2D 모델: " + lab)
    ax.errorbar(list(P.WRITE), list(P.WRITE.values()), yerr=P.WRITE_TOL, fmt="o", mfc="white", color=PAP, ms=10, mew=2.2, capsize=4, zorder=5, label="논문 Fig. 4(a) (그림에서 읽은 값, 허용 30 mV)")
    ax.set_xlim(-3, 100); ax.set_ylim(0, 1.25); ax.set_xlabel("WL이 올라간 뒤의 시간 [ps]", fontsize=12.5); ax.set_ylabel("저장 노드 전압 [V]", fontsize=12.5); ax.legend(fontsize=11, loc="lower right"); ax.grid(alpha=0.25); clean(ax)
    ax.set_title("Fig. 4(a): 쓰기 곡선 (Case 2)", fontsize=16, fontweight="bold", color=INK, pad=10)
    return save(fig, "gt2d_full_03_write.png")

def fig_fbe():
    name = {1: "Case 1 (30 nm)", 2: "Case 2 (20 nm)", 3: "Case 3 (10 nm, 1e18)", 4: "Case 4 (10 nm, 1e16)", 5: "Case 5 (1e16, WF 5.0)"}
    R1 = {c: M.fbe("dy", c) for c in range(1, 6)}; fig, ax = plt.subplots(1, 2, figsize=(15.5, 6.1))
    for a, cs, ylim, ttl in ((ax[0], (1, 2, 3), (0.915, 1.108), "Fig. 8(b): 몸체 두께 30 / 20 / 10 nm"), (ax[1], (3, 4, 5), (1.080, 1.1012), "Fig. 8(c)의 확대 그래프: 도핑과 일함수")):
        for lo, hi in R1[1]["lo"]: a.axvspan(lo, hi, color="#e1f5fe", zorder=0)
        for c in cs:
            r = R1[c]; a.plot(r["t"], r["sn"], color=COL[c], lw=2.2, label=f"2D 모델 fin5, {name[c]}", zorder=3); ends = [hi for _, hi in r["lo"]]
            if c in (1, 2): pts = list(zip(ends, PAPER_FBE[c][0])) + [(200.0, P.FBE_200[c])]
            elif c == 3: pts = [(ends[0], P.FBE_FIRST[3]), (200.0, P.FBE_200[3])]
            elif c == 4: pts = [(ends[0], P.FBE_FIRST[4]), (ends[1], P.FBE_LAST[4][1])]
            else: pts = []
            if pts: a.plot([p for p, _ in pts], [1.1 - v * 1e-3 for _, v in pts], "o", mfc="white", color=COL[c], ms=8, mew=2, zorder=4, label=f"논문, Case {c} (그림에서 읽음)")
        if 5 in cs: a.axhspan(1.1 - P.FBE_FLAT[5] * 1e-3, 1.1, color=COL[5], alpha=0.18, zorder=1, label="논문, Case 5: 1.1 V 높이의 선 (0.5 mV 이하)")
        a.set_xlim(0, 206); a.set_ylim(*ylim); a.set_xlabel("시간 [ns] (0 = 저장 노드 충전 직후)", fontsize=13); a.set_ylabel("저장 노드 전압 [V]", fontsize=13)
        a.set_title(ttl, fontsize=15, fontweight="bold", color=INK); a.grid(alpha=0.25); a.legend(fontsize=9.8, loc="lower left"); clean(a)
    ax[0].text(165, 1.068, "하늘색 띠 = BL이 0 V인 구간\n(21 ns 주기, 9회)", ha="center", fontsize=11.5, color="#0277bd", bbox=dict(fc="white", ec="#b3e5fc", pad=4))
    fig.suptitle("FBE: 저장 노드 전압 (선 = 2D 모델 fin5, 정공 전하는 조건 / 동그라미 = 논문)", fontsize=17, fontweight="bold", color=INK); fig.tight_layout()
    return save(fig, "gt2d_full_04_fbe.png")

def fig_ripple(D):
    fig, ax = plt.subplots(1, 2, figsize=(15.5, 6.0)); sw = lambda r: D["rp"][r]["sw"][5]; l5 = D["l5"]
    A = [("논문\nX–X'\n(그림에서 읽음)", F6E["xx"], None), ("3D 모델\nX–X'\n(10월 6일, 4.2 fF)", X3["swing"], "#2e7d32"), ("2D 모델\nZ–Z'\n(fin5, 1.8 fF)", sw("DdyRzb_zz"), "#1565c0"),
         ("2D 모델\nZ–Z'\n(4.2 fF)", sw("QSid_zz"), "#90caf9"), ("논문\nY–Y'\n(그림에서 읽음)", F6E["yy"], None), ("2D 모델\nY–Y'\n(fin5, 1.8 fF)", sw("DdyRy_yy"), "#ef6c00")]
    for i, (lab, v, col) in enumerate(A):
        ax[0].bar(i, v, 0.62, color=col or "white", edgecolor=PAP if col is None else col, hatch="//" if col is None else None, lw=2 if col is None else 0, zorder=3)
        ax[0].text(i + (0.36 if col is None else 0), v + (0 if col is None else 0.02), f"{v:+.2f}" if abs(v) > 0.005 else "0", ha="left" if col is None else "center", va="center" if col is None else "bottom",
                   fontsize=12, color=PAP if col is None else INK, fontweight="bold")
    ax[0].errorbar([0, 4], [F6E["xx"], F6E["yy"]], yerr=F6E["row"], fmt="none", ecolor=PAP, capsize=5, lw=1.6, zorder=4)
    ax[0].set_xticks(range(len(A))); ax[0].set_xticklabels([a[0] for a in A], fontsize=10); ax[0].set_ylim(-0.15, 0.95); ax[0].set_ylabel("공격 WL이 높은 동안의 SN 전압 변화 [mV]", fontsize=12.5)
    ax[0].set_title("가역 스윙 (WL이 내려가면 돌아옴)", fontsize=15, fontweight="bold", color=INK); ax[0].grid(axis="y", alpha=0.25, zorder=0); clean(ax[0])
    ax[0].text(3.2, 0.82, "논문 값의 오차 막대 = 픽셀 한 줄 (0.13 mV)\n논문의 Z–Z' 곡선은 가려서 읽을 수 없음", ha="center", fontsize=10.5, color="#607d8b")
    Bp = [("Y–Y'", P.RH["yy"], l5("DdyRy_yy"), "2D, fin5"), ("Z–Z'", P.RH["zz"], l5("DdyRzb_zz"), "2D, fin5"), ("X–X'", 0.0060, X3["loss"], "3D, 10월 6일")]
    for i, (lab, pv, mv, src) in enumerate(Bp):
        ax[1].bar(i - 0.2, pv, 0.36, color="white", edgecolor=PAP, hatch="//", lw=2, zorder=3); ax[1].bar(i + 0.2, mv, 0.36, color="#1565c0", zorder=3)
        ax[1].text(i - 0.2, pv * 1.15, f"{pv:.4f}", ha="center", fontsize=11.5, color=PAP, fontweight="bold"); ax[1].text(i + 0.2, mv * 1.15, f"{mv:.4f}\n({src})", ha="center", va="bottom", fontsize=10.5, color=INK)
    ax[1].bar([-9], [1], color="white", edgecolor=PAP, hatch="//", lw=2, label="논문 (본문의 임계 사이클 수에서 계산)"); ax[1].bar([-9], [1], color="#1565c0", label="모델 (마지막 다섯 사이클의 평균)")
    ax[1].axhline(l5("DdyRy_yy"), color="#607d8b", ls=":", lw=1.6, zorder=2, label="2D 모델의 정적 누설 13 pA (해머와 무관)")
    ax[1].set_yscale("log"); ax[1].set_ylim(3e-4, 0.2); ax[1].set_xlim(-0.6, 2.6); ax[1].set_xticks(range(3)); ax[1].set_xticklabels([b[0] for b in Bp], fontsize=13)
    ax[1].set_yticks([1e-3, 1e-2, 1e-1]); ax[1].set_yticklabels(["0.001", "0.01", "0.1"], fontsize=11); ax[1].minorticks_off()
    ax[1].set_ylabel("사이클당 누적 손실 [mV]", fontsize=12.5); ax[1].set_title("누적 손실 (돌아오지 않고 쌓임)", fontsize=15, fontweight="bold", color=INK); ax[1].legend(fontsize=10.5, loc="upper right"); ax[1].grid(axis="y", alpha=0.25, zorder=0); clean(ax[1])
    fig.suptitle("Fig. 6(e): 충돌 이온화 없는 로우 해머 (빗금 = 논문, 색 = 모델)", fontsize=17, fontweight="bold", color=INK); fig.tight_layout()
    return save(fig, "gt2d_full_06_ripple.png")

def fig_codex(C):         # Codex's runs, scored my way (rescore / mine): late reset counted from the reset node, Case 5's later loss left out
    R = sorted(C["j"]["ranking"], key=lambda g: rescore(g)[2]); fig, ax = plt.subplots(1, 2, figsize=(15.5, 6.6)); pl = sorted({PREP(g) for g in R}); pc = dict(zip(pl, ["#1565c0", "#ef6c00", "#2e7d32", "#6a1b9a"]))
    for i, g in enumerate(R):
        ax[0].plot(i + 1, rescore(g)[2], "o" if mine(g) else "x", color=pc[PREP(g)], ms=7, mew=1.8, zorder=3)
    ax[0].axhline(1.0, color="#2e7d32", ls="--", lw=1.8); ax[0].set_yscale("log"); ax[0].set_xlabel("조합의 순위 (점수가 작은 순서)", fontsize=12.5); ax[0].set_ylabel("다섯 Case 중 가장 나쁜 점수 (제 채점)", fontsize=12.5)
    for p_, c_ in pc.items(): ax[0].plot([], [], "o", color=c_, label=p_)
    ax[0].plot([], [], "x", color=INK, mew=1.8, label="x = 통과하지 못한 조합 (점수 1 초과, 또는 t_A에 SN이 1.1 V가 아님)"); ax[0].legend(fontsize=10, loc="lower right"); ax[0].grid(alpha=0.25, which="major"); clean(ax[0])
    ax[0].set_yticks([0.5, 1, 2, 5, 10]); ax[0].set_yticklabels(["0.5", "1", "2", "5", "10"], fontsize=11); ax[0].minorticks_off()
    ax[0].set_title(f"조합 {len(R)}개의 점수", fontsize=14.5, fontweight="bold", color=INK)
    x = 0; tk, tl = [], []; fc = ["#90caf9", "#ffcc80", "#a5d6a7", "#ce93d8", "#b0bec5"]
    for (name, fn), col in zip(LEV, fc):
        for l in sorted({fn(g) for g in R}):
            v = [g for g in R if fn(g) == l]; n = sum(1 for g in v if mine(g))
            ax[1].barh(x, n / len(v) * 100, 0.72, color=col, zorder=3); ax[1].text(n / len(v) * 100 + 1.2, x, f"{n}/{len(v)}", va="center", fontsize=10.5, color=INK); tk.append(x); tl.append(f"{name}: {l}"); x += 1
        x += 0.5
    ax[1].set_yticks(tk); ax[1].set_yticklabels(tl, fontsize=10.2); ax[1].invert_yaxis(); ax[1].set_xlabel("다섯 Case를 모두 통과한 조합의 비율 [%] (제 채점)", fontsize=12.5); ax[1].set_xlim(0, max(25, max(p.get_width() for p in ax[1].patches) * 1.5)); ax[1].grid(axis="x", alpha=0.25, zorder=0); clean(ax[1])
    ax[1].set_title("어떤 조건이 통과를 가르나", fontsize=14.5, fontweight="bold", color=INK)
    fig.suptitle("Codex의 조건 조합 실험 (fin3 기준): Fig. 8의 막대, 첫 구간 손실, 나중 손실을 함께 봄", fontsize=16, fontweight="bold", color=INK); fig.tight_layout()
    return save(fig, "gt2d_full_05_codex.png")

def fig_common(K):
    fig, ax = plt.subplots(figsize=(12.5, 6.2)); ts = [t / 1e3 for t in K["ts"]]
    for c in range(1, 6): ax.plot(ts, K["per"][c], color=COL[c], lw=2, label=f"Case {c}" + (" (200 ns 손실은 뺌)" if c == 5 else ""), zorder=3)
    ax.plot(ts, K["worst"], color=INK, lw=3.2, ls="--", label="다섯 Case 중 가장 나쁜 점수", zorder=4); ax.axhline(1.0, color="#2e7d32", ls="--", lw=1.8)
    ax.plot([K["tbest"] / 1e3], [K["best"]], "D", color=PAP, ms=11, zorder=5, label=f"가장 좋은 공통 시간 {K['tbest'] / 1e3:.1f} µs: 점수 {K['best']:.2f}")
    ax.set_yscale("log"); ax.set_xlabel("다섯 Case에 똑같이 준 유지 시간 [µs]", fontsize=12.5); ax.set_ylabel("점수 (막대, 첫 구간 손실, 나중 손실 중 가장 나쁜 값)", fontsize=12.5)
    ax.set_yticks([0.2, 0.5, 1, 2, 5]); ax.set_yticklabels(["0.2", "0.5", "1", "2", "5"], fontsize=11); ax.minorticks_off(); ax.legend(fontsize=10.5); ax.grid(alpha=0.25); clean(ax)
    ax.set_title(f"방안 M2: 유지 시간 하나로 다섯 Case가 나오는가\n(Codex의 실행을 이어서 계산. SN은 {SNK[K['sn']]}, avalanche {'켬' if K['ii'] else '끔'})", fontsize=14.5, fontweight="bold", color=INK, pad=10)
    return save(fig, "gt2d_full_07_common_time.png")

if __name__ == "__main__":
    C = codex(); K = common_time(C) if C else None; D = numbers(); k = check(D)
    cx = codex_text(C, K); m2 = m2_text(K); SEC = T.sections(cx, D["n"], m2)      # with m2: measure M2 was carried out, its section and its rows tell the result
    M.SEC, M.RESULT, M.TERM = SEC, T.RESULT, T.TERM
    M.TXT = dict(title="Cho 외 (IRPS 2026) 소자 재현: 전체 보고", meta="2026년 10월 8일 · 2D 단면 모델 fin5, 3D 단위 셀 확인, Codex의 조건 조합 실험 · 라운드 1~31",
                 res_head="숫자 한눈에: 논문과 지금의 구성 fin5", res_note="Case 1~5 순서예요. 점수가 1보다 작으면 그림을 읽는 오차 안이에요. 마지막 열은 모델 값이 어떤 종류인지예요.",
                 res_cols=["논문 그림", "비교한 값", "논문", "모델 (따로 적지 않으면 fin5)", "점수", "모델 값의 종류"],
                 term_note="실험별 내용은 같은 폴더의 <b>GT_IRPS2026_2D_소자완성_보고_2026-10-06.md</b> 9절과 GitHub <b>claude</b> 브랜치의 <b>claude/ANALYSIS.md</b>에 있어요.")
    n, avg = M.check_text()
    img = {a: os.path.join(PIC, b) for a, b in OLD.items()}; assert all(os.path.exists(v) for v in img.values()), [a for a, v in img.items() if not os.path.exists(v)]
    img.update(score=fig_score(D["sc"]), idvg=fig_idvg(), write=fig_write(), fbe=fig_fbe(), ripple=fig_ripple(D))
    if C: img["codex"] = fig_codex(C)
    if K: img["common"] = fig_common(K)
    open(OUT, "w", encoding="utf-8", newline="\n").write(M.html(img))
    print(f"text: {n} sentences, {avg:.1f} units per sentence, no analogy word; {k} numbers of the text checked against the run files and by arithmetic")
    print("Codex:", (C["commit"], C["n"], len(C["j"]["ranking"]), sum(1 for g in C["j"]["ranking"] if g["all_cases_pass"]), sum(1 for g in C["j"]["ranking"] if mine(g))) if C else None,
          "| common time:", (K["sn"], K["ii"], round(K["tbest"]), round(K["best"], 2)) if K else None)
    print("\n".join(v for a, v in img.items() if a not in OLD)); print(OUT, os.path.getsize(OUT) // 1024, "kB")
