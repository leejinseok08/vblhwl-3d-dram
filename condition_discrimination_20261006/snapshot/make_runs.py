# -*- coding: utf-8 -*-
"""
make_runs.py — structures and sdevice decks of the Cho-cell TCAD (Cho et al., IRPS 2026; VBL / HWL 1T1C 3D DRAM cell).

  python make_runs.py --only YE_ --sh run_iv.sh    # runs whose id starts with YE_, batch script runs/run_iv.sh
  python make_runs.py --list                       # the run table

Output (all numbers resolved):
  runs/_struct/<struct>_dvs.cmd        SDE input (sde -e -l <file>)
  runs/<id>/<id>_des.cmd               sdevice input
  runs/<id>/run.json                   parameters + schedule
  runs/manifest.csv, runs/<batch>.sh, sdevice*.par
Before any run: check the structure and the run conditions against the paper's text and figures (CLAUDE.md).
"""
import os, sys, json, csv, math, argparse, re, copy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import P as PDEF

# ------------------------------------------------------------------ structures
# Geometry and doping defaults in params.py are Case 2 of Fig.5(b) with the HfO2 gate dielectric. Doping is set per region.
# gr_c<n> = Fig.5(b) Cases 1-4 with 5 nm SiO2 (does not reproduce Fig.5(c)); gr_c<n>h = with HfO2 (the device in use; Case 5 =
# gr_c4h with work function 5.0 eV). gr_yy / gr_zz = Case 2 device, two cells across the BL / two layers (row hammer Cases 1 /
# 2 of the paper); gr_zzg = zz with the victim body contacted. g3_c2h = 3D unit cell, transistor only, 50 nm pillar.
# gm_spox / gm_sphk = SiO2 / HfO2 spacers (material diagnostics).
STRUCTS = dict(
    gr_c1=dict(Tbody=30, Gdi="SiO2"), gr_c2=dict(Gdi="SiO2"), gr_c3=dict(Tbody=10, Gdi="SiO2"), gr_c4=dict(Tbody=10, Nch=1e16, Gdi="SiO2"),
    gr_c1h=dict(Tbody=30), gr_c2h=dict(), gr_c3h=dict(Tbody=10), gr_c4h=dict(Tbody=10, Nch=1e16),
    gr_yy=dict(Pair="yy"), gr_zz=dict(Pair="zz"), gr_zzg=dict(Pair="zz", Bgc=1),
    g3_c2h=dict(Tpl="sde_gt3_dvs.cmd", Wbl=50, Dim=3),
    # 3D, Case 2 device, row hammer Case 3 (X-X'): half victim row + wall + half aggressor row, WL cut by 20 nm (and 40 nm: does the gap matter?)
    g3x_c2h=dict(Tpl="sde_gt3_dvs.cmd", Wbl=50, Dim=3, Pair="xx"), g3x40_c2h=dict(Tpl="sde_gt3_dvs.cmd", Wbl=50, Dim=3, Pair="xx", Wcut=40),
    # candidates for the WL cut (user 2026-10-06: "pick the candidates"): 10 nm (closest to an uncut WL the mesh carries), 20 nm
    # (= gate thickness), 40 nm, 100 nm (= the whole wall: each WL only over its own row)
    g3x10_c2h=dict(Tpl="sde_gt3_dvs.cmd", Wbl=50, Dim=3, Pair="xx", Wcut=10), g3x100_c2h=dict(Tpl="sde_gt3_dvs.cmd", Wbl=50, Dim=3, Pair="xx", Wcut=100),
    gm_spox=dict(Spm="SiO2"), gm_sphk=dict(Spm="HfO2"),
    # mesh variants of Case 2 / Case 1 (the same structure): junction mesh 0.25 / 2 nm; q5 = 5 nm everywhere along the channel,
    # 2 nm across, 0.5 nm at the dielectric (what a 3D array mesh can afford)
    gq025_c2h=dict(Mj=0.25, Mg=0.25), gq2_c2h=dict(Mj=2, Mg=2), gq5_c2h=dict(Mc=5, Mj=5, Mv=2, Mi=0.5, Mg=5),
    gq2_c1h=dict(Tbody=30, Mj=2, Mg=2), gq5_c1h=dict(Tbody=30, Mc=5, Mj=5, Mv=2, Mi=0.5, Mg=5),
)
SDE_KEYS = ["Lg", "Tbody", "Tox", "Tgm", "Dvox", "Nsd", "Nch", "Gdi", "Spm", "Pair", "Bgc", "Lsp1", "Lsp2", "Wbl", "Wact", "Dhox", "Mc", "Mj", "Mv", "Mi", "Mg", "Wcut"]

def fill_sde(name, prm):
    src = open(os.path.join(HERE, prm["Tpl"]), encoding="utf-8").read()
    src = src.replace('"n@node@', '"@node@')   # SWB writes n<node>_msh.tdr; decks here read <struct>_msh.tdr
    vals = {k: prm[k] for k in SDE_KEYS}; vals["node"] = name
    def sub(m):
        k = m.group(1)
        if k not in vals: raise KeyError(f"no value for @{k}@")
        return str(vals[k])
    return re.sub(r"@([A-Za-z_]\w*)@", sub, src)


# ------------------------------------------------------------------ shared deck text
def physics(p, indent="  "):
    rec = []
    if p["GR"]:
        dd = "DopingDependence " if p["SRHdd"] else ""
        srh = (f"SRH( {dd}TempDependence ElectricField( Lifetime=Hurkx DensityCorrection=None ) )"
               if p["TAT"] else f"SRH( {dd}TempDependence )")
        if p["SRHon"]: rec.append(srh + "")
        if p["BTBT"] == 2: rec.append("Band2Band( Model=NonlocalPath )   # diagnostic only: tunnelling along the path, default Si parameters")
        elif p["BTBT"] == 3: rec.append("Band2Band( Model=Hurkx DensityCorrection=Local )   # Hurkx, densities in its D factor corrected by the quasi-Fermi gradient (manual eq.495)")
        elif p["BTBT"]: rec.append("Band2Band( Model=Hurkx )")
        if p["II"]:   rec.append(f"Avalanche( vanOverstraeten{' ' + p['IIdf'] if p['IIdf'] else ''} )")
    rtxt = ""
    if rec:
        rtxt = f"{indent}  Recombination(\n" + "".join(f"{indent}    {r}\n" for r in rec) + f"{indent}  )\n"
    else:
        rtxt = f"{indent}  # GR=0: all generation/recombination off (coupling-only reference)\n"
    t = (f"{indent}Physics {{\n"
         f"{indent}  Temperature = {p['Temp']}\n"
         f"{indent}  EffectiveIntrinsicDensity( {p['Bgn']} )\n"
         + (f"{indent}  eQuantumPotential\n" if p["QC"] else "") +
         f"{indent}  Mobility( DopingDependence{('', ' HighFieldSaturation Enormal(Lombardi)', ' HighFieldSaturation', ' eHighFieldSaturation')[p['Mob']]}{' ThinLayer' if p['ThinL'] else ''} )\n"
         + rtxt + f"{indent}}}\n")
    if p["Dit"] and p["GR"]:
        t += (f"{indent}Physics( MaterialInterface=\"Silicon/SiO2\" ) {{\n"
              f"{indent}  Traps( ( Donor Uniform fromMidBandGap EnergyMid=0 EnergySig=0.5 Conc={p['Dit']:g} eXsection=1e-15 hXsection=1e-15 ) )\n"
              f"{indent}}}\n")
    return t

def plotblk(indent="  "):
    return (f"{indent}Plot {{\n"
            f"{indent}  eDensity hDensity ElectrostaticPotential SpaceCharge DopingConcentration\n"
            f"{indent}  ElectricField/Vector eCurrent/Vector hCurrent/Vector\n"
            f"{indent}  eQuasiFermiPotential hQuasiFermiPotential ConductionBandEnergy ValenceBandEnergy\n"
            f"{indent}  AvalancheGeneration Band2BandGeneration SRHRecombination eQuantumPotential\n"
            f"{indent}}}\n")

def probe_xyz(p):
    """Body centre under the gate (um): the probe of CurrentPlot. 0.3 Lg from the BL-side gate edge if the contact slot sits at the centre."""
    u = p["Lsp1"] + p["Lg"] * (0.3 if p["Bgc"] else 0.5); Lc = p["Lsp1"] + p["Lg"] + p["Lsp2"]
    y = p["Dvox"] / 2 + p["Tgm"] + p["Tox"] + p["Tbody"] / 2
    if p["Tpl"] == "sde_gt3_dvs.cmd": return f"({(p['Wbl'] / 2 + p['Lsp1'] + p['Lg'] / 2) / 1000:.5f} {y / 1000:.5f} {p['Wact'] / 4000:.5f})"
    return f"({(Lc - u if p['Pair'] == 'yy' else p['Wbl'] / 2 + u) / 1000:.5f} {y / 1000:.5f})"

def currentplot(p, indent="  "):
    pos = probe_xyz(p); extra = ""
    if p["Tpl"] == "sde_gt_dvs.cmd" and p["Pair"] == "one":
        # the paper does not say where it reads "the body potential": also under the BL-side spacer and at both ends of the gate
        yb = (p["Dvox"] / 2 + p["Tgm"] + p["Tox"] + p["Tbody"] / 2) / 1000
        for u in (p["Lsp1"] / 2, p["Lsp1"] + 0.1 * p["Lg"], p["Lsp1"] + 0.9 * p["Lg"]):
            q = f"({(p['Wbl'] / 2 + u) / 1000:.5f} {yb:.5f})"
            extra += f"{indent}  ElectrostaticPotential( {q} )\n{indent}  hQuasiFermiPotential( {q} )\n"
    return (f"{indent}CurrentPlot {{\n"
            f"{indent}  ElectrostaticPotential( {pos} )   # V_B probe: victim channel centre at body level\n"
            f"{indent}  hQuasiFermiPotential( {pos} )\n"
            f"{indent}  eQuasiFermiPotential( {pos} )\n" + extra
            + (f"{indent}  hDensity( Integrate( Region=\"R.Body_v\" ) )\n" if p["BodyMode"] == "BC" else "") +
            f"{indent}  hDensity( Integrate( Region=\"R.Ch_v\" ) )   # vertical channel sheet\n"
            f"{indent}  AvalancheGeneration( Integrate( Semiconductor ) )\n"
            f"{indent}  Band2BandGeneration( Integrate( Semiconductor ) )\n"
            f"{indent}}}\n")

# sogangic1 has 128 cores: "maximum" segfaults in Pardiso at the first solve; 8 was as fast as 16 or 32 (2D, 8k nodes)
NTHREADS = 8

def mathblk(p):
    if p["Dim"] == 3 and p["Lin3"] == "Pardiso":
        meth = "  Method    = ParDiSo\n"
    elif p["Dim"] == 3:
        meth = ('  Method    = ILS\n'
                '  ILSrc     = "set(1){ iterative(gmres(100), tolrel=1e-10, tolunprec=1e-4, tolabs=0, maxit=200); '
                'preconditioning(ilut(0.0005,-1), left); ordering(symmetric=nd, nonsymmetric=mpsilst); '
                'options(compact=yes, linscale=0, refineresidual=10, verbose=0); };"\n')
    else:
        meth = "  Method    = Blocked\n  SubMethod = Pardiso\n"
    return ("Math {\n" + ("  Extrapolate\n" if p["Extrap"] else "") + f"  Derivatives\n  RelErrControl\n  Digits = {p['Dig']}\n"
            + ("  ExtendedPrecision\n" if p["XP"] else "") + f"  ErrRef(Electron) = {p['ErrE']:g}\n  ErrRef(Hole)     = {p['ErrH']:g}\n  Iterations ={p['NewtIter']}\n  NotDamped  = {p['NotDamped']}\n"
            + (f"  RefDens_eGradQuasiFermi_ElectricField = {p['RefD']:g}\n  RefDens_hGradQuasiFermi_ElectricField = {p['RefD']:g}\n" if p["RefD"] else "")
            + meth + "  ACMethod    = Blocked\n  ACSubMethod = Pardiso\n  Transient = BE\n"
            f"  NumberOfThreads = {NTHREADS}\n  ExitOnFailure\n  CNormPrint\n}}\n")

def electrodes_single(p, dc=False):
    g = 0.0 if dc else p["Vnwl"]; b = 0.0 if dc else p["Vb"]
    e = ['{ Name="bl"     Voltage=0.0 }', '{ Name="sn_v"   Voltage=0.0 }',
         f'{{ Name="gs_v"   Voltage={g} WorkFunction={p["WFs"]} }}',
         f'{{ Name="gd_v"   Voltage={g} WorkFunction={p["WFd"]} }}']
    if p["BodyMode"] == "BC": e.append(f'{{ Name="body_v" Voltage={b} }}')
    return e

# ------------------------------------------------------------------ waveform schedule
class Sched:
    """Builds PWL breakpoints and transient segments (fine steps on edges, coarse on plateaus)."""
    def __init__(self, p):
        self.te = p["tEdge"] * 1e-9; self.seg = []
    def add(self, t1, t2, dt):
        if t2 > t1 + 1e-18: self.seg.append((t1, t2, dt))
    def edge(self, t1):
        self.add(t1, t1 + self.te, self.te / 5); return t1 + self.te
    def plat(self, t1, t2):
        L = t2 - t1
        if L <= 0: return t2
        self.add(t1, t2, L / 50 if L > 1e-6 else L / 10); return t2

def pwl(pts):
    return " ".join(f"{t:.6e} {v:.6g}" for t, v in pts)

def solve_transient(S):
    lines = ["Solve {",
             "  Coupled( Iterations=200 LineSearchDamping=1e-4 ){ Poisson eQuantumPotential }",
             "  Coupled{ Poisson Electron Hole eQuantumPotential Contact Circuit }"]
    for (t1, t2, dt) in S.seg:
        lines.append(f"  Transient( InitialTime={t1:.6e} FinalTime={t2:.6e} InitialStep={dt/10:.3e} "
                     f"MaxStep={dt:.3e} MinStep=1e-18 Increment=1.5 Decrement=2 )")
        lines.append("    { Coupled{ Poisson Electron Hole eQuantumPotential Contact Circuit }")
        nint = max(4, min(50, round((t2 - t1) / dt)))       # the system and current files get a point per maximum step (4 was too coarse for the write curve)
        lines.append(f"      CurrentPlot( Time=( Range=({t1:.6e} {t2:.6e}) Intervals={nint} ) ) }}")
    lines.append('  Plot( FilePrefix="end" )')
    lines.append("}")
    return "\n".join(lines) + "\n"

def header(rid, title, p, struct):
    keys = ["Temp", "GR", "TAT", "BTBT", "II", "Dit", "Rb", "Vb", "Vdd", "Vpp", "Vnwl", "Cs", "WFd", "WFs"]
    return (f"# ===================================================================\n"
            f"# {rid}: {title}\n"
            f"# structure: {struct}   |  " + "  ".join(f"{k}={p[k]:g}" if isinstance(p[k], float) else f"{k}={p[k]}" for k in keys) + "\n"
            f"# generated by make_runs.py — Cho et al. (IRPS 2026) cell. Sentaurus U-2022.12.\n"
            f"# ===================================================================\n")

def dev_file(rid, struct, p, indent="  "):
    return (f"{indent}File {{\n{indent}  Grid      = \"../_struct/{struct}_msh.tdr\"\n"
            f"{indent}  Plot      = \"{rid}_dev.tdr\"\n{indent}  Current   = \"{rid}_dev.plt\"\n"
            f"{indent}  Parameter = \"../../{p['Par']}\"\n{indent}}}\n")

# Output names carry their extension: run ids contain "." (Vb+0.0), and sdevice takes ".0_dev" as the
# extension otherwise (plot and current file then get the same name and overwrite each other).
# ------------------------------------------------------------------ deck builders
def deck_idvg(rid, p, struct):
    el = "\n".join("  " + e for e in electrodes_single(p, dc=True))
    body_ramp = ""
    if p["BodyMode"] == "BC":
        body_ramp = (f'  Quasistationary( InitialStep=0.05 MaxStep=0.2 MinStep=1e-6 Goal{{ Name="body_v" Voltage={p["Vb"]} }} )\n'
                     "    { Coupled{ Poisson Electron Hole eQuantumPotential } }\n")
    v1, v2 = (p["VgMax"], p["VgMin"]) if p["SwDown"] else (p["VgMin"], p["VgMax"])     # gate bias before / after the sweep
    if p["SwT"]:      # the sweep in time: the gate electrodes carry v1 -> v2 over SwT seconds, the DC start is already at v1
        T = p["SwT"]; el = el.replace('Voltage=0.0 WorkFunction', f'Voltage=( {v1} at 0, {v2} at {T:g} ) WorkFunction')
        return (header(rid, f"Id-Vg (Fig.5(c)) as a transient gate sweep, {abs(v2 - v1) / T:g} V/s", p, struct) +
                f'File {{\n  Grid      = "../_struct/{struct}_msh.tdr"\n  Plot      = "{rid}_dev.tdr"\n  Current   = "{rid}_dev.plt"\n'
                f'  Output    = "{rid}_log"\n  Parameter = "../../{p["Par"]}"\n}}\n'
                f"Electrode {{\n{el}\n}}\n" + physics(p, "") + plotblk("") + currentplot(p, "") + mathblk(p) +
                "Solve {\n  Coupled( Iterations=200 LineSearchDamping=1e-4 ){ Poisson }\n  Coupled{ Poisson Electron Hole }\n"
                f'  Quasistationary( InitialStep=0.02 MaxStep=0.1 MinStep=1e-6 Goal{{ Name="{p["Dterm"]}" Voltage={p["Vds"]} }} )\n'
                "    { Coupled{ Poisson Electron Hole } }\n"
                f'  NewCurrentFile="IdVg_"\n'
                f"  Transient( InitialTime=0 FinalTime={T:g} InitialStep={T * 1e-4:g} MaxStep={T / 104:g} MinStep={T * 1e-13:g} Increment=1.5 Decrement=2 )\n"
                "    { Coupled{ Poisson Electron Hole } }\n}\n"), dict(kind="idvg")
    txt = (header(rid, "DC Id-Vg (Fig.5(c))", p, struct) +
           f'File {{\n  Grid      = "../_struct/{struct}_msh.tdr"\n  Plot      = "{rid}_dev.tdr"\n  Current   = "{rid}_dev.plt"\n'
           f'  Output    = "{rid}_log"\n  Parameter = "../../{p["Par"]}"\n}}\n'
           f"Electrode {{\n{el}\n}}\n" + physics(p, "") + plotblk("") + currentplot(p, "") + mathblk(p) +
           "Solve {\n  Coupled( Iterations=200 LineSearchDamping=1e-4 ){ Poisson eQuantumPotential }\n"
           "  Coupled{ Poisson Electron Hole eQuantumPotential }\n" + body_ramp +
           f'  Quasistationary( InitialStep=0.02 MaxStep=0.1 MinStep=1e-6 Goal{{ Name="gs_v" Voltage={v1} }} Goal{{ Name="gd_v" Voltage={v1} }} )\n'
           "    { Coupled{ Poisson Electron Hole eQuantumPotential } }\n"
           f'  Quasistationary( InitialStep=0.02 MaxStep=0.1 MinStep=1e-6 Goal{{ Name="{p["Dterm"]}" Voltage={p["Vds"]} }} )\n'
           "    { Coupled{ Poisson Electron Hole eQuantumPotential } }\n"
           f'  NewCurrentFile="IdVg_"\n'
           f'  Quasistationary( InitialStep=2e-3 MaxStep=0.0125 MinStep=1e-7 Goal{{ Name="gs_v" Voltage={v2} }} Goal{{ Name="gd_v" Voltage={v2} }} )\n'
           "    { Coupled{ Poisson Electron Hole eQuantumPotential } }\n}\n")
    return txt, dict(kind="idvg")

# ------------------------------------------------------------------ Cho cell: write '1', then FBE or RH
def deck_cho(rid, p, struct, test):
    """Mixed mode, times in s. Write as in Fig.4(a) of Cho et al.: BL to Vdd, victim WL to Vpp 5 ps later, WL down after tWr.
    Then W: nothing more. FBE: BL Vdd <-> 0, WL 0 (Fig.4(c), 8). RH: BL to Vdd/2, aggressor WL 0 <-> Vpp (Fig.4(b), 6(c)).
    The 2D section is scaled to the cell with AreaFactor = Wact; each storage node carries Cs to ground."""
    pair = p["Pair"] != "one"; te = 5e-12; S = Sched(p); Vdd, Vpp = p["Vdd"], p["Vpp"]
    Vw = p["Vwr"] or Vdd                                  # BL level of the write (Fig.4(a) reads 1.16 V); back to Vdd after the WL is off
    BL = [(0, 0.0), (te, 0.0), (2 * te, Vw)]; WL = [(0, 0.0), (2 * te, 0.0), (3 * te, Vpp)]; WA = [(0, 0.0)]
    S.add(0, te, te); S.add(te, 3 * te, te / 5); tf = 3 * te + 100e-12; S.add(3 * te, tf, 2e-12)       # charging curve: 2 ps steps
    t1 = 3 * te + p["tWr"] * 1e-9; S.add(tf, t1, 10e-12); WL += [(t1, Vpp), (t1 + te, 0.0)]; S.add(t1, t1 + te, te / 5)
    t2 = t1 + te
    if Vw != Vdd: BL += [(t2, Vw), (t2 + te, Vdd)]; S.add(t2, t2 + te, te / 5); t2 += te
    tset = None
    if p["SNset"] and test in ("FBE", "RH"):          # the paper's initial state: storage node at '1' when the FBE / RH phase begins
        tset = (t2, t2 + 2 * te); S.add(t2, t2 + 2 * te, te / 5); t2 += 2 * te       # t2 = "t = 0" of Fig.8(b)
    hold = p["tHold"] * 1e-9; tS = t2 + hold; S.add(t2, tS, hold / 20); t = tS
    if test == "H":      # hold only, no write: BL and storage node driven to Vdd together with the WL at 0 V (what the junctions generate)
        S = Sched(p); BL = [(0, 0.0), (te, 0.0), (3 * te, Vdd)]; WL = [(0, 0.0)]; tS = 3 * te; t = tS + hold
        S.add(0, te, te); S.add(te, tS, te / 5)
        if hold > 2.1e-9: S.add(tS, tS + 1e-10, 5e-12); S.add(tS + 1e-10, tS + 1e-9, 5e-11); S.add(tS + 1e-9, t, hold / 40)     # long hold: the first nanosecond finely
        else: S.add(tS, t, hold / 40)
    if test == "FBE":
        e = p["tEdge"] * 1e-9; h = p["Tper"] * 1e-9 / 2; BL.append((tS, Vdd))
        for k in range(int(p["Npulse"])):                  # low half first, then high
            BL += [(t + e, 0.0), (t + h, 0.0), (t + h + e, Vdd), (t + 2 * h, Vdd)]
            S.add(t, t + e, e / 5); S.add(t + e, t + h, h / 20); S.add(t + h, t + h + e, e / 5); S.add(t + h + e, t + 2 * h, h / 20); t += 2 * h
    elif test == "RH":
        BL += [(tS, Vdd), (tS + te, Vdd / 2)]; S.add(tS, tS + te, te / 5); t = tS + te + hold; S.add(tS + te, t, hold / 20)
        tS = t; WA.append((t, 0.0)); ton, toff = p["tON"] * 1e-9, p["tOFF"] * 1e-9
        for k in range(int(p["Ncyc"])):
            WA += [(t + te, Vpp), (t + ton, Vpp), (t + ton + te, 0.0), (t + ton + toff, 0.0)]
            S.add(t, t + te, te / 5); S.add(t + te, t + ton, ton / 10); S.add(t + ton, t + ton + te, te / 5); S.add(t + ton + te, t + ton + toff, toff / 10)
            t += ton + toff
    tEnd = t
    for w in (BL, WL, WA):
        if w[-1][0] < tEnd: w.append((tEnd, w[-1][1]))
    el = ['{ Name="bl" Voltage=0.0 }' if p["BLhv"] < 0 else f'{{ Name="bl" Voltage=0.0 eRecVelocity=1e7 hRecVelocity={p["BLhv"]:g} }}']
    for c in ("va" if pair else "v"):
        el += [f'{{ Name="sn_{c}" Voltage=0.0 }}', f'{{ Name="gs_{c}" Voltage=0.0 WorkFunction={p["WFs"]} }}', f'{{ Name="gd_{c}" Voltage=0.0 WorkFunction={p["WFd"]} }}']
    if p["Bgc"]: el.append('{ Name="body_v" Voltage=0.0 }')          # grounded body: held at 0 V
    dev = ("Device CELL {\n  Electrode {\n" + "".join(f"    {e}\n" for e in el) + "  }\n" + dev_file(rid, struct, p) +
           physics(p).replace("Physics {\n", f"Physics {{\n    AreaFactor = {2 if p['Dim'] == 3 else p['Wact'] / 1000:g}\n", 1) + plotblk() + currentplot(p) + "}\n")
    gv = "nGv" if p["Rwl"] else "nWL"
    inst = f'CELL c1 ( "bl"=nBL "sn_v"=nSN "gs_v"={gv} "gd_v"={gv}' + (' "sn_a"=nSNa "gs_a"=nWLa "gd_a"=nWLa' if pair else "") + " )"
    sysl = [inst, f"Vsource_pset vsn ( nSN 0 ) {{ pwl = ( {pwl(BL)} ) }}" if test == "H" else f"Capacitor_pset Cs ( nSN 0 ) {{ capacitance = {p['Cs']:g} }}",
            f"Vsource_pset vbl ( nBL 0 ) {{ pwl = ( {pwl(BL)} ) }}", f"Vsource_pset vwl ( nWL 0 ) {{ pwl = ( {pwl(WL)} ) }}"]
    plotn = "v(nSN) v(nBL) v(nWL)"
    if p["Rwl"]: sysl.append(f"Resistor_pset rwl ( nGv nWL ) {{ resistance = {p['Rwl']:g} }}"); plotn += " v(nGv)"
    if pair:
        sysl += [f"Capacitor_pset Csa ( nSNa 0 ) {{ capacitance = {p['Cs']:g} }}", f"Vsource_pset vwla ( nWLa 0 ) {{ pwl = ( {pwl(WA)} ) }}"]; plotn += " v(nSNa) v(nWLa)"
    sns = [] if test == "H" else ["nSN", "nSNa"] if pair else ["nSN"]; sysl += [f"Set( {n} = 0 )" for n in sns]      # DC start: a node that sees only its capacitor and a 1e-21 A contact is singular
    solve = solve_transient(S).replace("Contact Circuit }\n", "Contact Circuit }\n" + "".join(f"  Unset( {n} )\n" for n in sns), 1)
    if tset:
        a, b = (f"  Transient( InitialTime={x:.6e} " for x in tset)
        if solve.count(a) != 1 or solve.count(b) != 1: raise ValueError(f"{rid}: cannot place Set / Unset of the storage node")
        solve = solve.replace(a, f"  Set( nSN = {p['SNset']:g} )\n" + a).replace(b, "  Unset( nSN )\n" + b)
    txt = (header(rid, f"Cho cell, mixed mode, test={test}, section={p['Pair']}", p, struct) + f'File {{ Output = "{rid}_log" }}\n\n' + dev +
           "\nSystem {\n" + "".join(f"  {l}\n" for l in sysl) + f'  Plot "{rid}_sys.plt" ( time() {plotn} )\n}}\n\n' + mathblk(p) + solve)
    return txt, dict(kind="cho", test=test, tS=tS, tEnd=tEnd), (BL, WL, WA), S

# ------------------------------------------------------------------ parameter files
def par_text(eps=22.0, tau=1.0, agen=None, bgen=None, pgen=None, alpha=None, dpot=None, dcr=None):
    """sdevice parameter file. Everything not listed is the Sentaurus U-2022.12 default (Hurkx: Agen 3.5e21, Bgen 2.25e7 V/cm, P 2,
    alpha 0, dPot 0). Hurkx (manual eq. 496, 497): G = Agen D (F / 1 V/cm)^Pgen exp(-Bgen (Eg/Eg300)^1.5 / F) with
    D = (np - ni^2) / ((n + ni)(p + ni)) (1 - |alpha|) + alpha; alpha = -1 is "only generation" (D = -1: no density factor).
    dPot [V]: no tunnelling where the potential changes by less than dPot/2 over the length dPot/F along the field (manual,
    "Tunneling Near Interfaces and Equilibrium Regions"); 2.24 = a potential change of at least the band gap (1.12 V).
    dcr = DenCorRef [cm^-3], electrons and holes: with DensityCorrection=Local the correction of a carrier density n is weighted
    by n / (n + DenCorRef) (manual eq. 495, 423: "improving numeric robustness"); default 0 = full weight at any density."""
    b2b = ""
    if agen or bgen or pgen or alpha is not None or dpot or dcr:      # the same values for the recombination branch
        b2b = ("\n  Band2BandTunneling\n  {\n" + (f"    Agen = {agen:g}\n    Arec = {agen:g}\n" if agen else "") + (f"    Bgen = {bgen:g}\n    Brec = {bgen:g}\n" if bgen else "")
               + (f"    Pgen = {pgen:g}\n    Prec = {pgen:g}\n" if pgen else "") + (f"    alpha = {alpha:g}\n" if alpha is not None else "") + (f"    dPot = {dpot:g}\n" if dpot else "") + (f"    DenCorRef = {dcr:g} , {dcr:g}\n" if dcr else "") + "  }\n")
    return ("* written by make_runs.py (par_text): parameter file of the Cho-cell decks\n\n"
            f'Material = "HfO2" {{\n  Epsilon\n  {{\n    epsilon = {eps:g}                * 5 nm gate dielectric; 22 = Sentaurus default\n  }}\n}}\n\n'
            'Material = "Si3N4" {\n  Epsilon\n  {\n    epsilon = 7.0                 * spacers: Lee .. Yu, IMW 2026 (Sentaurus default 7.5)\n  }\n}\n\n'
            'Material = "SiO2" {\n  Epsilon\n  {\n    epsilon = 3.9\n  }\n}\n\n'
            'Material = "Silicon" {\n  Scharfetter\n  {\n'
            f"    taumax  = {1e-5 * tau:.4e} ,   {3e-6 * tau:.4e}     # [s] electrons , holes (default x {tau:g})\n  }}\n" + b2b + "}\n")

PARS = {"sdevice.par": {}, "sdevice_gt_b10.par": dict(agen=3.5e22), "sdevice_gt_b100.par": dict(agen=3.5e23), "sdevice_gt_tau.par": dict(tau=0.01),
        "sdevice_gt_k10.par": dict(eps=10), "sdevice_gt_k50.par": dict(eps=50), "sdevice_gt_m3.par": dict(agen=3.5e18), "sdevice_gt_m2.par": dict(agen=3.5e19)}

def cal_par(a, b=2.25e7, p=None, alpha=None, dpot=None, dcr=None):
    """Parameter file with Hurkx rate a, field coefficient b, exponent p, alpha and dPot (registered in PARS); returns its name."""
    name = (f"sdevice_cal_a{a:.2g}_b{b:.3g}" + (f"_p{p:g}" if p else "") + (f"_al{alpha:g}" if alpha is not None else "") + (f"_dp{dpot:g}" if dpot else "") + (f"_dc{dcr:.0e}" if dcr else "") + ".par").replace("+", "")
    PARS[name] = dict(agen=a, bgen=b, pgen=p, alpha=alpha, dpot=dpot, dcr=dcr); return name

# ------------------------------------------------------------------ run table
def R(rid, exp, struct, deck, **ov): return dict(id=rid, exp=exp, struct=struct, deck=deck, ov=ov)
RUNS = []
CASES = ((1, "gr_c1h", 4.7, 30), (2, "gr_c2h", 4.7, 20), (3, "gr_c3h", 4.7, 10), (4, "gr_c4h", 4.7, 10), (5, "gr_c4h", 5.0, 10))    # case, structure, WF, body
CSB = {30: 5.1e-15, 20: 4.2e-15, 10: 3.6e-15}        # storage capacitor by body thickness (text of the paper)
IV = dict(Temp=300, II=0, TAT=0, QC=0, ThinL=0, Vb=0.0, Vds=1.1, Dterm="bl", VgMin=-1.0, VgMax=1.8, SwDown=1, ErrH=1e10, NewtIter=40, Mob=3, RefD=1e12)
TR = dict(Temp=300, TAT=0, QC=0, ThinL=0, Mob=3, RefD=1e12, ErrH=1e10, NewtIter=60, NotDamped=10, Extrap=0, Vdd=1.1, Vpp=1.8, Vnwl=0.0, Vb=0.0)
FB = dict(TR, Tper=20, Npulse=10, tEdge=0.1, tHold=16, Vwr=1.168)      # FBE: BL 1.168 V during the write, 16 ns hold (Fig.4(a), 8(b))
# YE = Id-Vg of Fig.5(c), Cases 1-5: agrees with the paper (NOTES).
for c, st, wf, tb in CASES: RUNS.append(R(f"YE_c{c}", "GT", st, "idvg", WFs=wf, WFd=wf, **IV))
# RW = write curve of Fig.4(a) with Cs 4.2 / 1.8 fF. RF / RFi = FBE of Fig.8 with the text's Cs, avalanche off / on; RG = Cs x 1.8 / 4.2.
for cs in (42, 18): RUNS.append(R(f"RW_cs{cs}", "GT", "gr_c2h", "cho:W", WFs=4.7, WFd=4.7, II=0, Cs=cs * 1e-16, **dict(TR, ErrH=1e14, Vwr=1.168)))
for c, st, wf, tb in CASES:
    F = dict(FB, ErrH=1e14 if c <= 3 else 1e10, WFs=wf, WFd=wf)
    RUNS.append(R(f"RF_c{c}", "GT", st, "cho:FBE", II=0, Cs=CSB[tb], **F))
    RUNS.append(R(f"RFi_c{c}", "GT", st, "cho:FBE", II=1, Cs=CSB[tb], **F))
    RUNS.append(R(f"RG_c{c}", "GT", st, "cho:FBE", II=0, Cs=CSB[tb] * 1.8 / 4.2, **F))
# RQ = row hammer of Fig.6 / 7 in the 2D sections (paper's Cases 1 and 2), Cs 1.8 fF.
for nm, st, ii in (("RQ_yy", "gr_yy", 0), ("RQ_zz", "gr_zz", 0), ("RQi_zz", "gr_zz", 1)):
    RUNS.append(R(nm, "GT", st, "cho:RH", WFs=4.7, WFd=4.7, II=ii, Cs=1.8e-15, tON=0.094, tOFF=0.094, Ncyc=10, **dict(TR, ErrH=1e14, Vwr=1.168)))
# RD = diagnostics of the FBE loss on Cases 1 / 2, one change each (NOT the paper's device): Hurkx rate x 10 / x 100, field-enhanced
# SRH, SRH lifetimes x 0.01, 358 K, 5 ps BL edges, SiO2 gate dielectric.
for c, tb in ((1, 30), (2, 20)):
    F = dict(FB, ErrH=1e14, WFs=4.7, WFd=4.7, II=0, Cs=CSB[tb]); st = f"gr_c{c}h"
    for tag, s_, ov in (("b10", st, dict(Par="sdevice_gt_b10.par")), ("b100", st, dict(Par="sdevice_gt_b100.par")), ("tat", st, dict(TAT=1)),
                        ("tau", st, dict(Par="sdevice_gt_tau.par")), ("T358", st, dict(Temp=358)), ("edge", st, dict(tEdge=0.005)), ("sio2", st[:-1], {})):
        RUNS.append(R(f"RD{tag}_c{c}", "GT", s_, "cho:FBE", **dict(F, **ov)))
# HH = hold test (BL and storage node to Vdd, WL 0, 2 ns) in 2D and in the 3D unit cell; HM = the same with one unnamed material changed.
H = dict(TR, ErrH=1e14, tHold=2.0)
for nm, st, ov in (("HH_2d", "gr_c2h", {}), ("HH_3d", "g3_c2h", {}), ("HM_spox", "gm_spox", {}), ("HM_sphk", "gm_sphk", {}), ("HM_gox", "gr_c2", {}),
                   ("HM_k10", "gr_c2h", dict(Par="sdevice_gt_k10.par")), ("HM_k50", "gr_c2h", dict(Par="sdevice_gt_k50.par"))):
    RUNS.append(R(nm, "GT", st, "cho:H", WFs=4.7, WFd=4.7, II=0, Cs=CSB[20], **dict(H, **ov)))
# YA / RA = tunnelling without the density damping (BTBT 3) at a Hurkx rate of 1e-3 (m3) / 1e-2 (m2): calibration trial, Cases 1 / 2.
for k in ("m3", "m2"):
    for c, tb in ((1, 30), (2, 20)):
        RUNS.append(R(f"YA{k}_c{c}", "GT", f"gr_c{c}h", "idvg", WFs=4.7, WFd=4.7, **dict(IV, BTBT=3, Par=f"sdevice_gt_{k}.par")))
        RUNS.append(R(f"RA{k}_c{c}", "GT", f"gr_c{c}h", "cho:FBE", II=0, BTBT=3, Cs=CSB[tb], Par=f"sdevice_gt_{k}.par", **dict(FB, ErrH=1e14, WFs=4.7, WFd=4.7)))

# ---- Calibration of the tunnelling model (user 2026-10-05): Hurkx with the density damping off (BTBT 3), rate A and field
# coefficient B against the GIDL branch of Fig.5(c) and the FBE of Fig.8. CH = hold state of Fig.8 (BL and storage node at Vdd,
# WL 0) for 20 ns: body potential rise against Fig.8(a). CI = Id-Vg of Fig.5(c) from +0.3 V down (with BTBT 3 the ramp to
# 1.8 V at zero drain bias does not converge; the tunnelling does not act above 0.3 V).
CASE = {c: (st, wf, tb) for c, st, wf, tb in CASES}
def cal_runs(tag, a, b, cases, **ov):
    par = cal_par(a, b)
    for c in cases:
        st, wf, tb = CASE[c]
        RUNS.append(R(f"CH{tag}_c{c}", "GT", st, "cho:H", WFs=wf, WFd=wf, II=0, BTBT=3, Par=par, Cs=CSB[tb], **dict(TR, ErrH=1e14 if c <= 3 else 1e10, tHold=20.0, **ov)))
        RUNS.append(R(f"CI{tag}_c{c}", "GT", st, "idvg", WFs=wf, WFd=wf, **dict(IV, VgMax=0.3, BTBT=3, Par=par, **ov)))
# numerics first (A 1e-2 of the default, B default; Cases 1, 2): n0 = settings as before, n1 = ErrRef(Electron) 1e13, n2 = n1 + extended precision
cal_runs("n0", 3.5e19, 2.25e7, (1, 2))
cal_runs("n1", 3.5e19, 2.25e7, (1, 2), ErrE=1e13)
cal_runs("n2", 3.5e19, 2.25e7, (1, 2), ErrE=1e13, XP=1)
# Result: the three settings give the same numbers (hold: body centre +663 / +561 mV at 20 ns, Cases 1 / 2; paper 555 / 445 at 21 ns)
# but the steps collapse to 1e-15 s again and again (hours for 20 ns) and no Id-Vg gets below -0.83 V: BTBT 3 is not usable.
#
# ---- Model U (2026-10-06): the density factor of the Hurkx model itself switched off, alpha = -1 ("only generation", manual
# eq. 497), with dPot = 2.24 V so that it acts only where the potential changes by at least the band gap. Same knobs A, B.
# Fig.8(b) re-read from the pixels (frame 0 .. 200 ns = columns 658 .. 948; 18 BL edges at 688.5 .. 947.5): first BL fall at
# 21.0 ns, period 21.0 ns (half 10.5 ns), 9 low phases within 200 ns. FB2 replaces the 16 ns / 20 ns / 10 pulses read by eye.
FB2 = dict(TR, Tper=21, Npulse=9, tEdge=0.5, tHold=20.7, Vwr=1.168)       # edges not resolvable (<= 1 ns): 0.5 ns (10 + 0.5 + 10 + 0.5 = 21)
def cal_u(tag, a, b, cases, dpot=2.24, p=None, tests="HIF", **ov):
    """CH = hold 21 ns, CI = Id-Vg from +0.3 V down, CF = FBE with the timing of FB2; Hurkx alpha = -1."""
    par = cal_par(a, b, p, -1, dpot)
    for c in cases:
        st, wf, tb = CASE[c]; eh = 1e14 if c <= 3 else 1e10
        if "H" in tests: RUNS.append(R(f"CH{tag}_c{c}", "GT", st, "cho:H", WFs=wf, WFd=wf, II=0, Par=par, Cs=CSB[tb], **dict(TR, ErrH=eh, tHold=21.0, **ov)))
        if "I" in tests: RUNS.append(R(f"CI{tag}_c{c}", "GT", st, "idvg", WFs=wf, WFd=wf, **dict(IV, VgMax=0.3, Par=par, **ov)))
        if "F" in tests: RUNS.append(R(f"CF{tag}_c{c}", "GT", st, "cho:FBE", WFs=wf, WFd=wf, II=0, Par=par, Cs=CSB[tb], **dict(FB2, ErrH=eh, **ov)))
cal_u("u1", 3.5e21, 2.25e7, (1, 2), tests="HI")          # default coefficients
cal_u("u2", 3.5e19, 2.25e7, (1, 2))                      # rate x 1e-2
cal_u("u3", 3.5e19, 1.9e7, (1, 2))                       # field coefficient of Hurkx's own set (manual p.537): sensitivity to B
cal_u("u4", 3.5e19, 2.25e7, (1, 2), dpot=1.12, tests="HI")   # the guard at half the value: does it matter?
# Result: with dPot 2.24 no generation at all at the storage-node corner (hold: 0.000 nA, FBE loss 0.00 mV); with 1.12 V
# 0.05 nA; the Id-Vg branches come out ragged and not ordered in A. The guard is a switch per mesh node: model U dropped.
#
# ---- Back to BTBT 3 (2026-10-06). Hold test at A 3.5e19: 12.7 nA at the storage-node corner, body centre +663 / +561 mV at
# 20 ns (Cases 1 / 2; paper 555 / 445 at 21 ns): the paper's rise needs about 0.8 of that, 9.5 - 10 nA, in every case (its
# Case 4, 1e16: 320 mV on the two gate capacitances = 0.19 - 0.25 fC in 21 ns).
# d = A 2.8e19, B default: FBE of Fig.8 for the five cases. e = A 8e18 with B 1.9e7 (the field coefficient of Hurkx's own
# set, manual p.537): the same storage-node rate expected, and a BL-side branch 1 - 1.5 decades higher (what Fig.5(c) needs).
# CT = Id-Vg as a transient gate sweep, 0.3 -> -1.0 V in 130 s (0.01 V/s: the body follows down to 1e-17 A).
def cal_d(tag, a, b, cases, tests="HTF", p=None, btbt=3, dcr=None, **ov):
    par = cal_par(a, b, p, dcr=dcr) if a else "sdevice.par"
    for c in cases:
        st, wf, tb = CASE[c]; eh = 1e14 if c <= 3 else 1e10
        if "H" in tests: RUNS.append(R(f"CH{tag}_c{c}", "GT", st, "cho:H", WFs=wf, WFd=wf, II=0, BTBT=btbt, Par=par, Cs=CSB[tb], **dict(TR, ErrH=eh, tHold=21.0, **ov)))
        if "T" in tests: RUNS.append(R(f"CT{tag}_c{c}", "GT", st, "idvg", WFs=wf, WFd=wf, **dict(IV, VgMax=0.3, SwT=130.0, BTBT=btbt, Par=par, **ov)))
        if "F" in tests: RUNS.append(R(f"CF{tag}_c{c}", "GT", st, "cho:FBE", WFs=wf, WFd=wf, II=0, BTBT=btbt, Par=par, Cs=CSB[tb], **dict(FB2, ErrH=eh, **ov)))
cal_d("d", 2.8e19, 2.25e7, (1, 2, 3, 4, 5), tests="F")
cal_d("d", 2.8e19, 2.25e7, (1, 2), tests="T")
cal_d("e", 8e18, 1.9e7, (1, 2), tests="HT")
cal_d("k", 0, 0, (1, 2), tests="T", btbt=1)          # the default model through the same transient sweep: must give the YE branch
# Result CTk = YE within 0.02 decade over the whole branch: the sweep in time is a valid way to the Id-Vg.
# Numerics of BTBT 3: the correction acts with full weight on densities far below ni, where the quasi-Fermi gradient is noise.
# r10 / r3 = DenCorRef 1e10 (= ni: nothing to correct below it) / 1e3 (the default of the trap-assisted model), A 3.5e19 as CHn.
cal_d("r10", 3.5e19, 2.25e7, (1, 2), tests="H", dcr=1e10)
cal_d("r3", 3.5e19, 2.25e7, (1, 2), tests="H", dcr=1e3)
# Results (NOTES (au)): CFd, 9 - 11 nA at the storage-node corner: body centre +556 / +496 / +432 / +415 mV before the first
# BL fall (paper 555 / 445 / 365 / 320) but the storage node itself drops 36 / 48 / 60 / 59 mV in the 21 ns hold, because every
# pair made at its junction takes one electron from it. The paper's Cases 3 - 5 lose 14 / 7 / 1 mV in 200 ns: its holes do
# not come from the storage-node junction at this rate. CHe (8e18, 1.9e7): 10.3 - 10.6 nA as predicted. CHr: no progress.
#
# ---- X series (2026-10-06): default Hurkx model (damping on), FBE with the timing of FB2, one thing changed at a time.
#   k = as it is;  i = impact ionization, default driving force;  p = the same with Eparallel;  f = with ElectricField;
#   h = i + BL contact that takes no holes (BLhv 0);  g = k + that contact.
# ---- What the results of (au) suggest, default Hurkx model (2026-10-06, user: run the improvements, then 3D):
# QR / QRi = row hammer Z-Z' (2D zz section, text Cs 4.2 fF) with the resistor of Fig.7(b) between the victim gates and their
#   WL source, 1e5 / 1e6 / 1e7 Ohm (no value in the paper), impact ionization off / on. The write and the two holds are
#   stretched so that the gate node reaches Vpp and is back at 0 V before the aggressor starts.
# FR = FBE Case 2 with the same resistor.  FW = FBE with the WL high for 105 ps only (the window Fig.4(a) shows) and impact
#   ionization on: more of the holes of the write are still in the body.  FB_ = FBE with the Sentaurus default band-gap narrowing
#   (BennettWilson; decides the gain of the parasitic BJT), impact ionization off / on; YB = its Id-Vg.
for r, tw, th in ((1e5, 0.5, 1.0), (1e6, 4.0, 5.0), (1e7, 40.0, 20.0)):
    for ii, tag in ((0, "QR"), (1, "QRi")):
        RUNS.append(R(f"{tag}{r:.0e}_zz".replace("+0", ""), "GT", "gr_zz", "cho:RH", WFs=4.7, WFd=4.7, II=ii, Cs=CSB[20], Rwl=r, tWr=tw, tHold=th,
                      tON=0.094, tOFF=0.094, Ncyc=10, **dict(TR, ErrH=1e14, Vwr=1.168)))
for r, tw in ((1e6, 4.0), (1e7, 40.0)):
    RUNS.append(R(f"FR{r:.0e}_c2".replace("+0", ""), "GT", "gr_c2h", "cho:FBE", WFs=4.7, WFd=4.7, II=0, Cs=CSB[20], Rwl=r, tWr=tw, **dict(FB2, ErrH=1e14)))
for c, st, wf, tb in CASES:
    RUNS.append(R(f"FW_c{c}", "GT", st, "cho:FBE", WFs=wf, WFd=wf, II=1, Cs=CSB[tb], tWr=0.105, **dict(FB2, ErrH=1e14 if c <= 3 else 1e10)))
for c, tb in ((1, 30), (2, 20)):
    for ii, tag in ((0, "FB_"), (1, "FBi_")):
        RUNS.append(R(f"{tag}c{c}", "GT", f"gr_c{c}h", "cho:FBE", WFs=4.7, WFd=4.7, II=ii, Bgn="BennettWilson", Cs=CSB[tb], **dict(FB2, ErrH=1e14)))
    RUNS.append(R(f"YB_c{c}", "GT", f"gr_c{c}h", "idvg", WFs=4.7, WFd=4.7, Bgn="BennettWilson", **IV))

# ---- 3D, next stage (user 2026-10-06): the unit cell against Fig.5(c) and the 2D section, then row hammer Case 3 (X-X').
#   V3I = Id-Vg of the 3D unit cell (Case 2);  V3W = its write;  X3 / X3i = row hammer X-X' on the pair, impact ionization
#   off / on;  X3g = the same with the WL cut by 40 nm instead of 20 (the gap is not in the paper: does it matter?).
RUNS.append(R("V3I_c2", "GT", "g3_c2h", "idvg", WFs=4.7, WFd=4.7, **IV))
RUNS.append(R("V3W_c2", "GT", "g3_c2h", "cho:W", WFs=4.7, WFd=4.7, II=0, Cs=CSB[20], **dict(TR, ErrH=1e14, Vwr=1.168)))
for nm_, st, ii in (("X3_xx", "g3x_c2h", 0), ("X3i_xx", "g3x_c2h", 1), ("X3g_xx", "g3x40_c2h", 0)):
    RUNS.append(R(nm_, "GT", st, "cho:RH", WFs=4.7, WFd=4.7, II=ii, Cs=CSB[20], tON=0.094, tOFF=0.094, Ncyc=10, **dict(TR, ErrH=1e14, Vwr=1.168)))
# With the iterative solver these transients crawl once the WL is on (200 inner iterations per Newton step, 10 min per time
# step): the same runs with the direct solver (suffix p).
RUNS.append(R("V3Wp_c2", "GT", "g3_c2h", "cho:W", WFs=4.7, WFd=4.7, II=0, Cs=CSB[20], Lin3="Pardiso", **dict(TR, ErrH=1e14, Vwr=1.168)))
for nm_, st, ii in (("X3p_xx", "g3x_c2h", 0), ("X3pi_xx", "g3x_c2h", 1), ("X3pg_xx", "g3x40_c2h", 0)):
    RUNS.append(R(nm_, "GT", st, "cho:RH", WFs=4.7, WFd=4.7, II=ii, Cs=CSB[20], tON=0.094, tOFF=0.094, Ncyc=10, Lin3="Pardiso", **dict(TR, ErrH=1e14, Vwr=1.168)))

# ---- R of Fig.7(b) as a fit parameter (user 2026-10-06: go on with it, and take the ideal value 1e-4 Ohm too); WL-cut candidates.
#   2D, impact ionization off (Fig.6(e)), text Cs: Z-Z' (QS) and Y-Y' (QY) over R; "id" = 1e-4 Ohm.
#   3D X-X' (direct solver): ideal WL with the cut at 10 / 100 nm (20 and 40 are X3p, X3pg); R 1e-4; R 1e6 with the four cuts.
RTAB = {1e-4: (0.5, 1.0), 2e5: (1.0, 1.0), 5e5: (2.0, 2.5), 1e6: (4.0, 5.0), 2e6: (8.0, 10.0), 5e6: (20.0, 20.0), 1e7: (40.0, 20.0)}      # R: (write, hold) in ns
def rtag(r): return "id" if r < 1 else f"{r:.0e}".replace("+0", "")
for r in (1e-4, 2e5, 5e5, 2e6, 5e6):
    RUNS.append(R(f"QS{rtag(r)}_zz", "GT", "gr_zz", "cho:RH", WFs=4.7, WFd=4.7, II=0, Cs=CSB[20], Rwl=r, tWr=RTAB[r][0], tHold=RTAB[r][1],
                  tON=0.094, tOFF=0.094, Ncyc=10, **dict(TR, ErrH=1e14, Vwr=1.168)))
for r in (1e-4, 1e6, 1e7):
    RUNS.append(R(f"QY{rtag(r)}_yy", "GT", "gr_yy", "cho:RH", WFs=4.7, WFd=4.7, II=0, Cs=CSB[20], Rwl=r, tWr=RTAB[r][0], tHold=RTAB[r][1],
                  tON=0.094, tOFF=0.094, Ncyc=10, **dict(TR, ErrH=1e14, Vwr=1.168)))
X3 = dict(TR, ErrH=1e14, Vwr=1.168, Lin3="Pardiso", tON=0.094, tOFF=0.094, Ncyc=10)
for nm_, st, r in (("X3c10_xx", "g3x10_c2h", 0), ("X3c100_xx", "g3x100_c2h", 0), ("X3rid_xx", "g3x_c2h", 1e-4), ("X3r1e6_xx", "g3x_c2h", 1e6),
                   ("X3r1e6c10_xx", "g3x10_c2h", 1e6), ("X3r1e6c40_xx", "g3x40_c2h", 1e6), ("X3r1e6c100_xx", "g3x100_c2h", 1e6)):
    ov = dict(Rwl=r, tWr=RTAB[r][0], tHold=RTAB[r][1]) if r else {}
    RUNS.append(R(nm_, "GT", st, "cho:RH", WFs=4.7, WFd=4.7, II=0, Cs=CSB[20], **dict(X3, **ov)))

# ---- Paper conditions as decided by the user on 2026-10-06 ("use impact ionization; initial state and body potential as the paper
# gives them"; row hammer "as the paper": Fig.6(e) without, Fig.7 with impact ionization):
#   pre-charge = the transient of Fig.4(a) (BL 1.168 V, WL 1.8 V from 15 ps to the end of its window at 120 ps); initial state of
#   the FBE / RH phase = WL 0 V, BL at Vdd, storage node at 1.1 V (every curve of Fig.8(b), (c), 6(e), 7 starts there): SNset;
#   t = 0 = that instant, t_A = the first BL fall 21.0 ns later; body potential = potential at the body centre, t = 0 -> t_A.
PC = dict(TR, tWr=0.105, SNset=1.1, Vwr=1.168)
for c, st, wf, tb in CASES:         # PF = FBE of Fig.8, impact ionization on
    RUNS.append(R(f"PF_c{c}", "GT", st, "cho:FBE", WFs=wf, WFd=wf, II=1, Cs=CSB[tb], **dict(PC, Tper=21, Npulse=9, tEdge=0.5, tHold=21.0, ErrH=1e14 if c <= 3 else 1e10)))
# PR = row hammer: Fig.6(e) (off) and Fig.7 (on) for Y-Y' and Z-Z' in 2D; PRg = Z-Z' with the grounded body of Fig.7(b)
for nm_, st, ii in (("PR_yy", "gr_yy", 0), ("PRi_yy", "gr_yy", 1), ("PR_zz", "gr_zz", 0), ("PRi_zz", "gr_zz", 1), ("PRgi_zz", "gr_zzg", 1)):
    RUNS.append(R(nm_, "GT", st, "cho:RH", WFs=4.7, WFd=4.7, II=ii, Cs=CSB[20], tON=0.094, tOFF=0.094, Ncyc=10, **dict(PC, ErrH=1e14)))
for nm_, ii in (("X3Q_xx", 0), ("X3Qi_xx", 1)):      # X-X' in 3D with the same initial state (not "X3P": the PC folder names are case-blind, X3p_xx exists)
    RUNS.append(R(nm_, "GT", "g3x_c2h", "cho:RH", WFs=4.7, WFd=4.7, II=ii, Cs=CSB[20], tON=0.094, tOFF=0.094, Ncyc=10, Lin3="Pardiso", **dict(PC, ErrH=1e14)))

# MQ = the same default model on the mesh variants: hold 21 ns (H), FBE (F), Id-Vg (I). Is the corner generation a mesh matter?
for st, c, tb in (("gq025_c2h", 2, 20), ("gq2_c2h", 2, 20), ("gq5_c2h", 2, 20), ("gq2_c1h", 1, 30), ("gq5_c1h", 1, 30)):
    q = st.split("_")[0][2:]
    RUNS.append(R(f"MQ{q}H_c{c}", "GT", st, "cho:H", WFs=4.7, WFd=4.7, II=0, Cs=CSB[tb], **dict(TR, ErrH=1e14, tHold=21.0)))
    RUNS.append(R(f"MQ{q}F_c{c}", "GT", st, "cho:FBE", WFs=4.7, WFd=4.7, II=0, Cs=CSB[tb], **dict(FB2, ErrH=1e14)))
    RUNS.append(R(f"MQ{q}I_c{c}", "GT", st, "idvg", WFs=4.7, WFd=4.7, **IV))
for tag, ov in (("k", {}), ("i", dict(II=1)), ("p", dict(II=1, IIdf="Eparallel")), ("f", dict(II=1, IIdf="ElectricField")),
                ("h", dict(II=1, BLhv=0.0)), ("g", dict(BLhv=0.0))):
    for c, st, wf, tb in CASES:
        RUNS.append(R(f"CF{tag}_c{c}", "GT", st, "cho:FBE", WFs=wf, WFd=wf, Cs=CSB[tb], **dict(dict(FB2, ErrH=1e14 if c <= 3 else 1e10, II=0), **ov)))

# ------------------------------------------------------------------ checks
def check_pwl(name, pts):
    ts = [t for t, _ in pts]
    bad = [i for i in range(1, len(ts)) if not ts[i] > ts[i - 1]]
    if bad: raise ValueError(f"{name}: PWL times not increasing at index {bad[:3]}")

def check_segs(S, tEnd):
    for (a, b) in zip(S.seg, S.seg[1:]):
        if abs(a[1] - b[0]) > 1e-15: raise ValueError(f"segment gap {a} -> {b}")
    if abs(S.seg[-1][1] - tEnd) > 1e-15: raise ValueError(f"last segment ends {S.seg[-1][1]} != tEnd {tEnd}")
    return sum(math.ceil((t2 - t1) / dt) for t1, t2, dt in S.seg)   # minimum number of time steps

# ------------------------------------------------------------------ main
def build(run):
    p = copy.deepcopy(PDEF); p.update(STRUCTS[run["struct"]]); p.update(run["ov"])
    rid = run["id"]; kind = run["deck"]; steps = None
    if kind == "idvg": txt, info = deck_idvg(rid, p, run["struct"])
    else:
        txt, info, waves, S = deck_cho(rid, p, run["struct"], kind[4:])
        for i, w in enumerate(waves): check_pwl(f"{rid} wave{i}", w)
        steps = check_segs(S, info["tEnd"]); info["nseg"] = len(S.seg)
    info["min_steps"] = steps
    if not p["QC"]: txt = txt.replace(" eQuantumPotential", "")     # no density-gradient equation in Solve / Plot
    return p, txt, info

def wtext(path, s):
    """Write with LF line ends and UTF-8 even on Windows (Sentaurus/bash on the Linux server)."""
    with open(path, "w", encoding="utf-8", newline="\n") as f: f.write(s)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", nargs="*"); ap.add_argument("--list", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "runs")); ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--sh", default="run_all.sh")     # name of the batch script (a second batch next to a running one)
    a = ap.parse_args()
    seen = {}
    for x in [r["id"] for r in RUNS] + list(STRUCTS):       # the PC's file system is case-blind: X3P_xx would land in the folder of X3p_xx
        if seen.setdefault(x.lower(), x) != x: raise SystemExit(f"names differ only by case: {seen[x.lower()]} / {x}")
    runs = [r for r in RUNS if not a.only or any(r["id"].startswith(o) for o in a.only)]
    os.makedirs(os.path.join(a.out, "_struct"), exist_ok=True)
    used = sorted({r["struct"] for r in runs})
    for st in used:
        p = copy.deepcopy(PDEF); p.update(STRUCTS[st])
        wtext(os.path.join(a.out, "_struct", f"{st}_dvs.cmd"), fill_sde(st, p))
    rows = []
    for r in runs:
        p, txt, info = build(r)
        if a.list:
            print(f"{r['id']:28s} {r['exp']:4s} {r['struct']:15s} {r['deck']:9s} min_steps={info['min_steps']}"); continue
        d = os.path.join(a.out, r["id"]); os.makedirs(d, exist_ok=True)
        wtext(os.path.join(d, f"{r['id']}_des.cmd"), txt)
        wtext(os.path.join(d, "run.json"), json.dumps(dict(id=r["id"], exp=r["exp"], struct=r["struct"], deck=r["deck"],
                                                           params=p, sched=info), indent=1))
        rows.append(dict(id=r["id"], exp=r["exp"], struct=r["struct"], deck=r["deck"], dim=p["Dim"],
                         min_steps=info["min_steps"], **{k: p[k] for k in ("Rb", "Vb", "II", "GR", "Temp", "tON", "Ncyc", "Npulse")}))
    if a.list: return
    for name, kw in PARS.items(): wtext(os.path.join(HERE, name), par_text(**kw))
    with open(os.path.join(a.out, "manifest.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    sh = ["#!/bin/bash", "# build structures, then run decks (2D in parallel, 3D one at a time). Check every structure against the paper before running.",
          "# usage: ./run_all.sh [jobs]   (requires sde and sdevice in PATH)", "set -u", f"JOBS=${{1:-{a.jobs}}}",
          'cd "$(dirname "$0")"', "cd _struct"]
    for st in used: sh.append(f'[ -f {st}_msh.tdr ] || sde -e -l {st}_dvs.cmd > {st}_sde.log 2>&1 || echo "SDE FAILED: {st}"')
    sh += ["cd ..", "run() { cd \"$1\" && sdevice \"$1_des.cmd\" > \"$1.out\" 2>&1; echo \"$1 exit=$?\"; cd ..; }", "export -f run"]
    two = [r["id"] for r in rows if r["dim"] == 2]; three = [r["id"] for r in rows if r["dim"] == 3]
    if two: sh.append("printf '%s\\n' " + " ".join(two) + " | xargs -P \"$JOBS\" -I{} bash -c 'run {}'")
    for t in three: sh.append(f"run {t}")
    wtext(os.path.join(a.out, a.sh), "\n".join(sh) + "\n"); os.chmod(os.path.join(a.out, a.sh), 0o755)
    print(f"wrote {len(rows)} runs, {len(used)} structures -> {a.out}")

if __name__ == "__main__":
    main()
