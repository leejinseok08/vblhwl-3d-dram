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
    gr_yy=dict(Pair="yy"), gr_zz=dict(Pair="zz"), gr_zzg=dict(Pair="zz", Bgc=1), gr_zzb=dict(Pair="zz", Blc="bot"), gr_zzbg=dict(Pair="zz", Blc="bot", Bgc=1),
    g3_c2h=dict(Tpl="sde_gt3_dvs.cmd", Wbl=50, Dim=3),
    # 3D, Case 2 device, row hammer Case 3 (X-X'): half victim row + wall + half aggressor row, WL cut by 20 nm (and 40 nm: does the gap matter?)
    g3x_c2h=dict(Tpl="sde_gt3_dvs.cmd", Wbl=50, Dim=3, Pair="xx"), g3x40_c2h=dict(Tpl="sde_gt3_dvs.cmd", Wbl=50, Dim=3, Pair="xx", Wcut=40),
    # candidates for the WL cut (user 2026-10-06: "pick the candidates"): 10 nm (closest to an uncut WL the mesh carries), 20 nm
    # (= gate thickness), 40 nm, 100 nm (= the whole wall: each WL only over its own row)
    g3x10_c2h=dict(Tpl="sde_gt3_dvs.cmd", Wbl=50, Dim=3, Pair="xx", Wcut=10), g3x100_c2h=dict(Tpl="sde_gt3_dvs.cmd", Wbl=50, Dim=3, Pair="xx", Wcut=100),
    gm_spox=dict(Spm="SiO2"), gm_sphk=dict(Spm="HfO2"),
    gw_c2h=dict(Wbl=50),      # Case 2 with the 50 nm pillar that the WL pitch of 275 nm in Fig.5(a) implies (the drawing shows 100)
    # mesh variants of Case 2 / Case 1 (the same structure): junction mesh 0.25 / 2 nm; q5 = 5 nm everywhere along the channel,
    # 2 nm across, 0.5 nm at the dielectric (what a 3D array mesh can afford)
    gq025_c2h=dict(Mj=0.25, Mg=0.25), gq2_c2h=dict(Mj=2, Mg=2), gq5_c2h=dict(Mc=5, Mj=5, Mv=2, Mi=0.5, Mg=5),
    gq2_c1h=dict(Tbody=30, Mj=2, Mg=2), gq5_c1h=dict(Tbody=30, Mc=5, Mj=5, Mv=2, Mi=0.5, Mg=5),
)
SDE_KEYS = ["Lg", "Tbody", "Tox", "Tgm", "Dvox", "Nsd", "Nch", "Gdi", "Spm", "Pair", "Bgc", "Blc", "Lsp1", "Lsp2", "Wbl", "Wact", "Dhox", "Mc", "Mj", "Mv", "Mi", "Mg", "Wcut"]

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
        if p["ProbeT"]:      # across the body thickness at the centre probe's x: 1 nm inside both gate-oxide interfaces, 1/4 and 3/4
            y0 = p["Dvox"] / 2 + p["Tgm"] + p["Tox"]; xq = pos.strip("()").split()[0]
            for d in (1.0, p["Tbody"] / 4, 3 * p["Tbody"] / 4, p["Tbody"] - 1.0):
                q = f"({xq} {(y0 + d) / 1000:.5f})"
                extra += f"{indent}  ElectrostaticPotential( {q} )\n{indent}  hQuasiFermiPotential( {q} )\n"
        if p["ProbeX"]:      # the whole channel every 5 nm at mid-depth and 1 nm under one gate oxide; statistics over the body region and its two parts
            y0 = p["Dvox"] / 2 + p["Tgm"] + p["Tox"]; x0 = p["Wbl"] / 2; L = p["Lsp1"] + p["Lg"] + p["Lsp2"]
            for yy in (y0 + p["Tbody"] / 2, y0 + 1.0):
                for i in range(int(L / 5)):
                    extra += f"{indent}  ElectrostaticPotential( ({(x0 + 2.5 + 5 * i) / 1000:.5f} {yy / 1000:.5f}) )\n"
            win = lambda a, b: f"Window[({a / 1000:.5f} {y0 / 1000:.5f}) ({b / 1000:.5f} {(y0 + p['Tbody']) / 1000:.5f})]"
            gated, under = win(x0 + p["Lsp1"], x0 + p["Lsp1"] + p["Lg"]), win(x0, x0 + p["Lsp1"])
            extra += (f'{indent}  ElectrostaticPotential( Average(Region="R.Ch_v") Minimum(Region="R.Ch_v") Maximum(Region="R.Ch_v") Average({gated}) Average({under}) )\n'
                      f'{indent}  hQuasiFermiPotential( Average(Region="R.Ch_v") Average({gated}) )\n')
    if p["ProbeX"] and p["Tpl"] == "sde_gt_dvs.cmd" and p["Pair"] != "one":       # 2D pair: average over the victim's body under its gate, holes in the aggressor's body
        y0 = p["Dvox"] / 2 + p["Tgm"] + p["Tox"]; xa = p["Lsp2"] if p["Pair"] == "yy" else p["Wbl"] / 2 + p["Lsp1"]
        extra += (f"{indent}  ElectrostaticPotential( Average(Window[({xa / 1000:.5f} {y0 / 1000:.5f}) ({(xa + p['Lg']) / 1000:.5f} {(y0 + p['Tbody']) / 1000:.5f})]) )\n"
                  f'{indent}  hDensity( Integrate( Region="R.Ch_a" ) )\n')
    if p["ProbeX"] and p["Tpl"] == "sde_gt3_dvs.cmd" and p["Pair"] == "one":      # 3D unit cell: the average over the body under the gate (the half row of the model)
        y0 = p["Dvox"] / 2 + p["Tgm"] + p["Tox"]; x0 = p["Wbl"] / 2 + p["Lsp1"]
        extra += (f"{indent}  ElectrostaticPotential( Average(Window[({x0 / 1000:.5f} {y0 / 1000:.5f} 0) "
                  f"({(x0 + p['Lg']) / 1000:.5f} {(y0 + p['Tbody']) / 1000:.5f} {p['Wact'] / 2000:.5f})]) )\n")
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
            f"  NumberOfThreads = {p['Nthr']}\n  ExitOnFailure\n  CNormPrint\n}}\n")

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
    def log(self, t1, t2, first=1e-9, n=20):
        """A long stretch after a fast event (microseconds to milliseconds): pieces that grow by a decade, n steps each, so that
        the solver and the plot files resolve the nanoseconds after the event and still reach the end (one piece of L / 20 would
        start with a step of L / 200)."""
        a, b = t1, min(t1 + first, t2); self.add(a, b, (b - a) / n)
        while b < t2 - 1e-18:
            a, b = b, min(t1 + (b - t1) * 10, t2); self.add(a, b, (b - a) / n)

def ft(t):
    """A time in the deck: 7 digits as always; 13 only where 7 cannot hold it (a 0.5 ns BL edge at 21 ms would print as zero length)."""
    s = f"{t:.6e}"
    return s if abs(float(s) - t) <= 1e-12 * abs(t) else f"{t:.12e}"

def pwl(pts):
    return " ".join(f"{ft(t)} {v:.6g}" for t, v in pts)

def solve_transient(S):
    lines = ["Solve {",
             "  Coupled( Iterations=200 LineSearchDamping=1e-4 ){ Poisson eQuantumPotential }",
             "  Coupled{ Poisson Electron Hole eQuantumPotential Contact Circuit }"]
    for (t1, t2, dt) in S.seg:
        lines.append(f"  Transient( InitialTime={ft(t1)} FinalTime={ft(t2)} InitialStep={dt/10:.3e} "
                     f"MaxStep={dt:.3e} MinStep=1e-18 Increment=1.5 Decrement=2 )")
        lines.append("    { Coupled{ Poisson Electron Hole eQuantumPotential Contact Circuit }")
        nint = max(4, min(50, round((t2 - t1) / dt)))       # the system and current files get a point per maximum step (4 was too coarse for the write curve)
        lines.append(f"      CurrentPlot( Time=( Range=({ft(t1)} {ft(t2)}) Intervals={nint} ) ) }}")
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
    t1 = 3 * te + p["tWr"] * 1e-9; S.add(tf, t1, 10e-12); twf = min(p["tWf"] * 1e-12, te)
    WL += [(t1, Vpp), (t1 + twf, 0.0)]; S.add(t1, t1 + twf, twf / 5); S.add(t1 + twf, t1 + te, te / 10)       # (second piece only if the WL falls faster than 5 ps)
    if p["SNa0"] and pair: WA = list(WL)                  # aggressor cell written to '1' together with the victim (a DC start with its node at 1.1 V did not converge)
    t2 = t1 + te
    if Vw != Vdd: BL += [(t2, Vw), (t2 + te, Vdd)]; S.add(t2, t2 + te, te / 5); t2 += te
    tset = None
    if p["SNset"] and test in ("FBE", "RH"):          # the paper's initial state: storage node at '1' when the FBE / RH phase begins
        tset = (t2, t2 + 2 * te); S.add(t2, t2 + 2 * te, te / 5); t2 += 2 * te       # t2 = "t = 0" of Fig.8(b)
    hold = p["tHold"] * 1e-9; tS = t2 + hold; tgen = None
    if p["Gb"] and tset and test in ("FBE", "RH"):
        if hold < 1.5e-9: raise ValueError(f"{rid}: the hole supply needs a hold of 1.5 ns or more")
        # Fig.8(a) as a condition: electron-hole pairs made uniformly in the floating body from 0.2 ns after the storage node is
        # set to 1 ns before the first BL fall, the storage node held at SNset meanwhile (in Fig.8(b), (c) it is still at 1.1 V
        # at t_A) and released 0.5 ns before the fall. Where the holes of the paper come from is not decided by this.
        # Row hammer: the same during the hold with the BL still at Vdd, before it goes to Vdd/2 (the pre-charge is common to both).
        tgen = (t2 + 2e-10, tS - 1e-9); tset = (tset[0], tS - 5e-10)
        S.add(t2, tset[1], hold / 40); S.add(tset[1], tS, 5e-11)
    elif p["SNhold"] and tset and test in ("FBE", "RH"):  # own generation, the node held through the hold and released 0.5 ns before the fall (RH: before the BL step)
        if hold < 1.5e-9: raise ValueError(f"{rid}: a held node needs a hold of 1.5 ns or more")
        tset = (tset[0], tS - 5e-10)
        S.log(t2, tset[1]) if hold > 1e-6 else S.add(t2, tset[1], hold / 40)
        S.add(tset[1], tS, 5e-11)
    elif hold > 1e-6: S.log(t2, tS)                       # long hold (time scale of the cited FBE tests): steps even in log time
    else: S.add(t2, tS, hold / 20)
    t = tS
    if test == "H":      # hold only, no write: BL and storage node driven to Vdd together with the WL at 0 V (what the junctions generate)
        S = Sched(p); BL = [(0, 0.0), (te, 0.0), (3 * te, Vdd)]; WL = [(0, 0.0)]; tS = 3 * te; t = tS + hold
        S.add(0, te, te); S.add(te, tS, te / 5)
        if hold > 2.1e-9: S.add(tS, tS + 1e-10, 5e-12); S.add(tS + 1e-10, tS + 1e-9, 5e-11); S.add(tS + 1e-9, t, hold / 40)     # long hold: the first nanosecond finely
        else: S.add(tS, t, hold / 40)
    if test == "FBE":
        e = p["tEdge"] * 1e-9; h = p["Tper"] * 1e-9 / 2; BL.append((tS, Vdd))
        for k in range(int(p["Npulse"])):                  # low half first, then high
            BL += [(t + e, 0.0), (t + h, 0.0), (t + h + e, Vdd), (t + 2 * h, Vdd)]
            plat = (lambda a, b: S.log(a, b, n=10)) if h > 1e-6 else (lambda a, b: S.add(a, b, h / 20))      # long phases: log steps after each edge
            S.add(t, t + e, e / 5); plat(t + e, t + h); S.add(t + h, t + h + e, e / 5); plat(t + h + e, t + 2 * h); t += 2 * h
    elif test == "RH":
        h2 = (p["tHold2"] or p["tHold"]) * 1e-9          # hold at Vdd/2 before the hammer
        BL += [(tS, Vdd), (tS + te, Vdd / 2)]; S.add(tS, tS + te, te / 5); t = tS + te + h2
        if p["SNhold"] == 2 and tset:                    # the history at Vdd/2: the node stays held, released 0.5 ns before the hammer
            tset = (tset[0], t - 5e-10)
            S.log(tS + te, tset[1]) if h2 > 1e-6 else S.add(tS + te, tset[1], h2 / 20)
            S.add(tset[1], t, 5e-11)
        elif h2 > 1e-6: S.log(tS + te, t)
        else: S.add(tS + te, t, h2 / 20)
        tS = t; WA.append((t, 0.0)); ton, toff = p["tON"] * 1e-9, p["tOFF"] * 1e-9; va = 0.0 if p["Idle"] else Vpp
        for k in range(int(p["Ncyc"])):
            WA += [(t + te, va), (t + ton, va), (t + ton + te, 0.0), (t + ton + toff, 0.0)]
            S.add(t, t + te, te / 5); S.add(t + te, t + ton, ton / 10); S.add(t + ton, t + ton + te, te / 5); S.add(t + ton + te, t + ton + toff, toff / 10)
            t += ton + toff
    tEnd = t
    for w in (BL, WL, WA):
        if w[-1][0] < tEnd: w.append((tEnd, w[-1][1]))
    el = ['{ Name="bl" Voltage=0.0 }' if p["BLhv"] < 0 else f'{{ Name="bl" Voltage=0.0 eRecVelocity=1e7 hRecVelocity={p["BLhv"]:g} }}']
    snv = "" if p["SNhv"] < 0 else f' eRecVelocity=1e7 hRecVelocity={p["SNhv"]:g}'
    for c in ("va" if pair else "v"):
        el += [f'{{ Name="sn_{c}" Voltage=0.0{snv} }}', f'{{ Name="gs_{c}" Voltage=0.0 WorkFunction={p["WFs"]} }}', f'{{ Name="gd_{c}" Voltage=0.0 WorkFunction={p["WFd"]} }}']
    if p["Bgc"]: el.append('{ Name="body_v" Voltage=0.0 }')          # grounded body: held at 0 V
    ph = physics(p).replace("Physics {\n", f"Physics {{\n    AreaFactor = {2 if p['Dim'] == 3 else p['Wact'] / 1000:g}\n", 1); cp = currentplot(p)
    if tgen:      # constant generation in the body region, on between tgen[0] and tgen[1] with 0.1 ns ramps (manual: "Constant Optical Generation", eq. 699)
        # (the device-wide section must name a source: zero everywhere, the body region sets its own value; Scaling=0 = none in the DC start)
        ph = ph.replace("Physics {\n", "Physics {\n    Optics( OpticalGeneration( Scaling=0 SetConstant( Value=0 ) TimeDependence( WaveTime=(%.6e, %.6e) WaveTLin=1e-10 ) ) )\n" % tgen, 1)
        ph += f'  Physics( Region="R.Ch_v" ) {{ Optics( OpticalGeneration( SetConstant( Value={p["Gb"]:g} ) ) ) }}\n'
        cp = cp.replace("  AvalancheGeneration(", '  OpticalGeneration( Integrate( Region="R.Ch_v" ) )\n    AvalancheGeneration(', 1)
    dev = ("Device CELL {\n  Electrode {\n" + "".join(f"    {e}\n" for e in el) + "  }\n" + dev_file(rid, struct, p) + ph + plotblk() + cp + "}\n")
    gv = "nGv" if p["Rwl"] else "nWL"
    bn = "nBd" if p["Rbl"] else "nBL"
    inst = f'CELL c1 ( "bl"={bn} "sn_v"=nSN "gs_v"={gv} "gd_v"={gv}' + (' "sn_a"=nSNa "gs_a"=nWLa "gd_a"=nWLa' if pair else "") + " )"
    sysl = [inst, f"Vsource_pset vsn ( nSN 0 ) {{ pwl = ( {pwl(BL)} ) }}" if test == "H" else f"Capacitor_pset Cs ( nSN 0 ) {{ capacitance = {p['Cs']:g} }}",
            f"Vsource_pset vbl ( nBL 0 ) {{ pwl = ( {pwl(BL)} ) }}", f"Vsource_pset vwl ( nWL 0 ) {{ pwl = ( {pwl(WL)} ) }}"]
    plotn = "v(nSN) v(nBL) v(nWL)"
    if p["Rwl"]: sysl.append(f"Resistor_pset rwl ( nGv nWL ) {{ resistance = {p['Rwl']:g} }}"); plotn += " v(nGv)"
    if p["Rbl"]: sysl.append(f"Resistor_pset rbl ( nBd nBL ) {{ resistance = {p['Rbl']:g} }}"); plotn += " v(nBd)"
    if pair:
        sysl += [f"Capacitor_pset Csa ( nSNa 0 ) {{ capacitance = {p['Cs']:g} }}", f"Vsource_pset vwla ( nWLa 0 ) {{ pwl = ( {pwl(WA)} ) }}"]; plotn += " v(nSNa) v(nWLa)"
    sns = [] if test == "H" else ["nSN", "nSNa"] if pair else ["nSN"]; sysl += [f"Set( {n} = 0 )" for n in sns]      # DC start: a node that sees only its capacitor and a 1e-21 A contact is singular
    solve = solve_transient(S).replace("Contact Circuit }\n", "Contact Circuit }\n" + "".join(f"  Unset( {n} )\n" for n in sns), 1)
    if tset:
        a, b = (f"  Transient( InitialTime={ft(x)} " for x in tset)
        if solve.count(a) != 1 or solve.count(b) != 1: raise ValueError(f"{rid}: cannot place Set / Unset of the storage node")
        sa, ua = (f"  Set( nSNa = {p['SNa0']:g} )\n", "  Unset( nSNa )\n") if p["SNa0"] and pair else ("", "")       # the aggressor's node with the victim's
        solve = solve.replace(a, f"  Set( nSN = {p['SNset']:g} )\n" + sa + a).replace(b, "  Unset( nSN )\n" + ua + b)
    txt = (header(rid, f"Cho cell, mixed mode, test={test}, section={p['Pair']}", p, struct) + f'File {{ Output = "{rid}_log" }}\n\n' + dev +
           "\nSystem {\n" + "".join(f"  {l}\n" for l in sysl) + f'  Plot "{rid}_sys.plt" ( time() {plotn} )\n}}\n\n' + mathblk(p) + solve)
    return txt, dict(kind="cho", test=test, tS=tS, tEnd=tEnd), (BL, WL, WA), S

# ------------------------------------------------------------------ parameter files
def par_text(eps=22.0, tau=1.0, agen=None, bgen=None, pgen=None, alpha=None, dpot=None, dcr=None, ii=None):
    """sdevice parameter file. Everything not listed is the Sentaurus U-2022.12 default (Hurkx: Agen 3.5e21, Bgen 2.25e7 V/cm, P 2,
    alpha 0, dPot 0). Hurkx (manual eq. 496, 497): G = Agen D (F / 1 V/cm)^Pgen exp(-Bgen (Eg/Eg300)^1.5 / F) with
    D = (np - ni^2) / ((n + ni)(p + ni)) (1 - |alpha|) + alpha; alpha = -1 is "only generation" (D = -1: no density factor).
    dPot [V]: no tunnelling where the potential changes by less than dPot/2 over the length dPot/F along the field (manual,
    "Tunneling Near Interfaces and Equilibrium Regions"); 2.24 = a potential change of at least the band gap (1.12 V).
    dcr = DenCorRef [cm^-3], electrons and holes: with DensityCorrection=Local the correction of a carrier density n is weighted
    by n / (n + DenCorRef) (manual eq. 495, 423: "improving numeric robustness"); default 0 = full weight at any density.
    ii = factor on the ionization coefficients a of van Overstraeten - de Man (manual Table 89: electrons 7.03e5, holes 1.582e6
    below / 6.71e5 above 4e5 V/cm), a diagnosis only: no source gives such a factor."""
    av = (f"\n  vanOverstraetendeMan\n  {{\n    a(low)  = {7.03e5 * ii:g} , {1.582e6 * ii:g}\n    a(high) = {7.03e5 * ii:g} , {6.71e5 * ii:g}\n  }}\n" if ii else "")
    b2b = ""
    if agen or bgen or pgen or alpha is not None or dpot or dcr:      # the same values for the recombination branch
        b2b = ("\n  Band2BandTunneling\n  {\n" + (f"    Agen = {agen:g}\n    Arec = {agen:g}\n" if agen else "") + (f"    Bgen = {bgen:g}\n    Brec = {bgen:g}\n" if bgen else "")
               + (f"    Pgen = {pgen:g}\n    Prec = {pgen:g}\n" if pgen else "") + (f"    alpha = {alpha:g}\n" if alpha is not None else "") + (f"    dPot = {dpot:g}\n" if dpot else "") + (f"    DenCorRef = {dcr:g} , {dcr:g}\n" if dcr else "") + "  }\n")
    return ("* written by make_runs.py (par_text): parameter file of the Cho-cell decks\n\n"
            f'Material = "HfO2" {{\n  Epsilon\n  {{\n    epsilon = {eps:g}                * 5 nm gate dielectric; 22 = Sentaurus default\n  }}\n}}\n\n'
            'Material = "Si3N4" {\n  Epsilon\n  {\n    epsilon = 7.0                 * spacers: Lee .. Yu, IMW 2026 (Sentaurus default 7.5)\n  }\n}\n\n'
            'Material = "SiO2" {\n  Epsilon\n  {\n    epsilon = 3.9\n  }\n}\n\n'
            'Material = "Silicon" {\n  Scharfetter\n  {\n'
            f"    taumax  = {1e-5 * tau:.4e} ,   {3e-6 * tau:.4e}     # [s] electrons , holes (default x {tau:g})\n  }}\n" + b2b + av + "}\n")

PARS = {"sdevice.par": {}, "sdevice_gt_b10.par": dict(agen=3.5e22), "sdevice_gt_b100.par": dict(agen=3.5e23), "sdevice_gt_tau.par": dict(tau=0.01),
        "sdevice_gt_k10.par": dict(eps=10), "sdevice_gt_k50.par": dict(eps=50), "sdevice_gt_m3.par": dict(agen=3.5e18), "sdevice_gt_m2.par": dict(agen=3.5e19)}

def cal_par(a, b=2.25e7, p=None, alpha=None, dpot=None, dcr=None, ii=None):
    """Parameter file with Hurkx rate a, field coefficient b, exponent p, alpha and dPot (registered in PARS); returns its name."""
    name = (f"sdevice_cal_a{a:.2g}_b{b:.3g}" + (f"_p{p:g}" if p else "") + (f"_al{alpha:g}" if alpha is not None else "") + (f"_dp{dpot:g}" if dpot else "") + (f"_dc{dcr:.0e}" if dcr else "") + (f"_ii{ii:g}" if ii else "") + ".par").replace("+", "")
    PARS[name] = dict(agen=a, bgen=b, pgen=p, alpha=alpha, dpot=dpot, dcr=dcr, ii=ii); return name

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
PC = dict(TR, tWr=0.105, SNset=1.1, Vwr=1.168, Nthr=4)
# ---- 2D device completion (user 2026-10-06): fix the open parameters by experiment, round by round.
# Process (CLAUDE.md, "2D completion"): 1. structure match against the paper (tools/gt_start.sh gate, kept in runs/<batch>.check)
# 2. run the configurations of the round  3. score every configuration against the paper (tools/score2d.py, targets in
# tools/paper_targets.py)  4. adopt a change only if it lowers the score of the group it is meant for and leaves Fig.5(c)
# inside its tolerance  5. next round from the new baseline. A configuration <tag> = runs D<tag>I_c<n> (Id-Vg), D<tag>W_c2
# (write), D<tag>F_c<n> (FBE, impact ionization on), D<tag>Ry_yy / Ryi_yy / Rz_zz / Rzi_zz / Rzg_zz (row hammer).
def cfg2d(tag, what, k_cs=1.0, par=None, rh=None, gb=None, cases=None, wst="gr_c2h", rhsel=None, iv=None, **ov):
    """cases / wst: other structures for the cases and for the write run; rhsel: only these row-hammer runs; iv: overrides of the Id-Vg runs."""
    pv = dict(Par=par) if par else {}; GB = gb or {}; CS = cases or CASES
    if "I" in what:
        for c, st, wf, tb in CS: RUNS.append(R(f"D{tag}I_c{c}", "GT", st, "idvg", WFs=wf, WFd=wf, **dict(IV, Nthr=4, **pv, **(iv or {}))))
    if "W" in what:
        RUNS.append(R(f"D{tag}W_c2", "GT", wst, "cho:W", WFs=4.7, WFd=4.7, II=1, Cs=CSB[20] * k_cs, **dict(dict(PC, ErrH=1e14), **pv, **ov)))
    if "F" in what:
        for c, st, wf, tb in CS:
            RUNS.append(R(f"D{tag}F_c{c}", "GT", st, "cho:FBE", WFs=wf, WFd=wf, Cs=CSB[tb] * k_cs,
                          **dict(dict(PC, II=1, Tper=21, Npulse=9, tEdge=0.5, tHold=21.0, ErrH=1e14 if c <= 3 else 1e10, Gb=GB.get(c, 0.0)), **pv, **ov)))
    if "R" in what:
        for nm_, st, ii in (("Ry_yy", "gr_yy", 0), ("Ryi_yy", "gr_yy", 1), ("Rz_zz", "gr_zz", 0), ("Rzi_zz", "gr_zz", 1), ("Rzg_zz", "gr_zzg", 1),
                            ("Rzbi_zz", "gr_zzb", 1), ("Rzbg_zz", "gr_zzbg", 1)):      # the last two (BL contact at the bottom end of the pillar) only when named in rhsel
            if (rhsel and nm_ not in rhsel) or (not rhsel and "zb" in nm_): continue
            RUNS.append(R(f"D{tag}{nm_}", "GT", st, "cho:RH", WFs=4.7, WFd=4.7, II=ii, Cs=CSB[20] * k_cs,
                          **dict(dict(PC, ErrH=1e14, tON=0.094, tOFF=0.094, Ncyc=10), **pv, **ov, **(rh or {}))))
# Round 1: baseline b0 = the paper's conditions as decided (pre-charge of Fig.4(a): BL 1.168 V, WL high 15 .. 120 ps; t = 0:
# storage node 1.1 V, WL 0, BL Vdd; FBE timing of Fig.8(b); impact ionization on in FBE, row hammer both ways; text Cs; default
# Hurkx), then one change each:
cfg2d("b0", "WFR")
cfg2d("cs", "WFR", k_cs=1.8 / 4.2)                           # storage capacitor that gives the write speed of Fig.4(a) (NOTES (am))
cfg2d("ep", "FR", IIdf="Eparallel")                          # driving force of the impact ionization
cfg2d("e1", "F", tEdge=0.1); cfg2d("e2", "F", tEdge=1.0)     # BL edge of the FBE pulses (not resolvable in Fig.8(b))
cfg2d("w3", "WF", tWr=0.3)                                   # WL high for 300 ps instead of the 105 ps window of Fig.4(a)
cfg2d("a5", "IF", par=cal_par(1.7e21, 2.25e7))               # Hurkx rate x 0.48: the GIDL branch of Fig.5(c) at -1 V
cfg2d("ab", "IF", par=cal_par(2.7e19, 1.875e7))              # rate and field coefficient from the two points -1 V and -0.5 V of Fig.5(c), Case 1
cfg2d("r2", "FR", Rwl=2e5, tWr=1.0, rh=dict(tHold=1.0))      # resistor of Fig.7(b) at the value the Z-Z' scan points to
# Round 2: Fig.8(a) as a condition. Found in round 1 (NOTES (ax)): the paper's rises are "one common end potential minus the
# potential of the depleted body at the start": 555 / 445 / 365 / 320 mV + the start values of this model (-0.2955 / -0.1905 /
# -0.1141 / -0.0746 V at the body centre) = +0.260 / +0.255 / +0.251 / +0.245 V; Case 5 (WF 5.0): -0.005 V. No variant of round 1
# brings holes into the body (rise 0.5 - 193 mV, of which nothing is hole charge except in Case 1). So the body is charged to
# the paper's potential (Gb) and the question becomes whether the device then loses charge as Fig.8(b), (c) show.
GB0 = {1: 4e26, 2: 5e26, 3: 1e27, 4: 1e27, 5: 1e27}          # qk = sizing runs: no BL pulses, generation on purpose too high;
cfg2d("qk", "F", gb=GB0, Npulse=0)                           # tools/gt_probes.py -k reads off the rate that ends at Fig.8(a)
# Sizing result: Fig.8(a) is reached with 1084 / 1056 / 1099 / 962 / 1138 holes in the body - one hole charge (about 1050 holes,
# 0.17 fC) for all five cases within 8 %.
GBQ = {1: 1.137e26, 2: 1.808e26, 3: 3.991e26, 4: 3.527e26, 5: 4.037e26}      # ends at the bar of Fig.8(a), case by case
GBN = {1: 1.101e26, 2: 1.798e26, 3: 3.813e26, 4: 3.850e26, 5: 3.725e26}      # 1050 holes in every case (one number instead of five)
cfg2d("q0", "F", gb=GBQ)                                     # body at the potential of Fig.8(a), text Cs
cfg2d("q1", "F", gb=GBQ, k_cs=1.8 / 4.2)                     # the same with the storage capacitance of the write curve
cfg2d("qn", "F", gb=GBN)                                     # the same hole charge in every case
cfg2d("q3", "F", gb=GBQ, par="sdevice_gt_tau.par")           # SRH lifetimes x 0.01: how fast the body loses its holes in the BL-low phases
# Where can one hole charge for all cases come from? Candidate: the channel electrons (about 0.2 fC at Vpp) leave through the
# junctions when the WL goes off; with impact ionization on they leave holes behind if the WL falls faster than they can go.
for k_, f_ in (("f1", 1.0), ("f2", 0.1), ("f3", 0.01)): cfg2d(k_, "F", tWf=f_, Npulse=0, tHold=1.0)       # WL fall 1 / 0.1 / 0.01 ps, 1 ns hold, no BL pulses
# Round 3, on the baseline adopted after round 1 (B1: storage node 1.8 fF, Hurkx Agen 1.7e21): the hole charge at t_A as the
# open quantity. Round 2 (body at the bar of Fig.8(a)): losses in the paper's order but 3 - 20 times too small in the first
# BL-low phase. How do the body rise (Fig.8(a)) and the losses (Fig.8(b), (c)) move against each other when the charge grows?
B1 = dict(k_cs=1.8 / 4.2, par=cal_par(1.7e21, 2.25e7))
for k_, f_ in (("h1", 1.0), ("h2", 1.25), ("h3", 1.5), ("h4", 2.0)): cfg2d(k_, "F", gb={c: g * f_ for c, g in GBQ.items()}, **B1)
# Result of round 3: 1.25 x the charge of the bars (about 1300 holes, 0.21 fC) gives the losses of Fig.8(b), (c) with their
# saturating shape (200 ns: 82 / 56 / 16.6 / 12.5 / 1.6 mV against 100 / 50 / 14.6 / 7 / 1), the bars then stand 53 - 68 mV high.
# fin = the 2D device as fixed on 2026-10-06, every test with the same parameters (the numbers of the report come from here).
KQ = 1.25
cfg2d("fin", "IWFR", gb={c: g * KQ for c, g in GBQ.items()}, **B1)
# ---- User decisions of 2026-10-06 (afternoon): the hole charge stays a condition and is sized to Fig.8(a) (GBQ, not x 1.25);
# R of Fig.7(b) = 200 kOhm for the row hammer if it makes no trouble; steps 2 - 6 of the remaining 2D work. Round 4.
B2 = dict(B1, gb=GBQ)                                                          # baseline from here on
cfg2d("ra", "WFR", Rwl=2e5, **B2)                                              # 200 kOhm in every test, nothing else changed
for k_, r_ in (("rc", 1e5), ("rd", 1.5e5), ("re", 3e5)): cfg2d(k_, "R", Rwl=r_, rhsel=("Rz_zz",), **B1)       # R scan at 1.8 fF (the morning scan had 4.2 fF)
cfg2d("rf", "R", Rwl=2e5, rhsel=("Rz_zz",), rh=dict(Ncyc=30), **B1)           # 30 cycles: one shift or a loss in every cycle?
# step 4: row hammer with the body charged (the paper pre-charges with impact ionization for FBE and row hammer alike).
# 1056 holes = the bar of Fig.8(a) for Case 2 (445 mV), 1970 holes = the 665 mV of Fig.7(e); through a 1.9 ns window (3 ns hold).
GRH = lambda g: g * 19.9 / 1.9
for k_, r_, g_ in (("ha", 0, 1.808e26), ("hb", 2e5, 1.808e26), ("hc", 0, 3.492e26), ("hd", 2e5, 3.492e26)):
    cfg2d(k_, "R", rhsel=("Ryi_yy", "Rzi_zz"), rh=dict(Gb=GRH(g_), tHold=3.0), **dict(B1, **({"Rwl": r_} if r_ else {})))
# step 5: Y-Y' candidates (BL series resistor 1 / 10 kOhm; aggressor node at '1')
for k_, ov_ in (("ya", dict(Rbl=1e3)), ("yb", dict(Rbl=1e4)), ("yc", dict(SNa0=1.1)), ("yd", dict(Rbl=1e4, SNa0=1.1))): cfg2d(k_, "R", rhsel=("Ry_yy",), **dict(B1, **ov_))
# step 3: impact-ionization coefficients x 10 / x 100, write + 21 ns hold, no hole supply: do holes stay, does the node droop?
for k_, f_ in (("i1", 10), ("i2", 100)): cfg2d(k_, "F", k_cs=1.8 / 4.2, par=cal_par(1.7e21, 2.25e7, ii=f_), Npulse=0)
# step 2: what the results owe to assumptions the paper does not fix, Case 2: spacer material, BL pillar width, mobility model
C2 = lambda st: ((2, st, 4.7, 20),)
cfg2d("sx", "IWF", cases=C2("gm_spox"), wst="gm_spox", **B2); cfg2d("sh", "IWF", cases=C2("gm_sphk"), wst="gm_sphk", **B2)
cfg2d("bw", "IWF", cases=C2("gw_c2h"), wst="gw_c2h", **B2)
cfg2d("m1", "IWF", cases=C2("gr_c2h"), iv=dict(Mob=1), Mob=1, **B2)
# The resistor again, with time for the gate node to settle (ra / rc .. rf above keep the paper's timing - WL high 105 ps,
# 50 ps to the first aggressor edge - and with 200 kOhm the victim's gate is still coming down when the hammering starts,
# which is itself one of the troubles the resistor makes): WL high 1 ns, 1 ns hold, as in the morning scan, now at 1.8 fF.
for k_, r_ in (("ta", 1e5), ("tb", 1.5e5), ("td", 3e5)): cfg2d(k_, "R", Rwl=r_, tWr=1.0, rhsel=("Rz_zz",), rh=dict(tHold=1.0), **B1)
cfg2d("tc", "R", Rwl=2e5, tWr=1.0, rh=dict(tHold=1.0), **B1)                    # 200 kOhm: all five row-hammer runs
cfg2d("tf", "R", Rwl=2e5, tWr=1.0, rhsel=("Rz_zz",), rh=dict(tHold=1.0, Ncyc=30), **B1)       # 30 cycles
# Round 5 (from i1: with the coefficients x 10 the WL switch-off leaves 2200 holes in the Case 3 body - avalanche at the
# storage-node-side gate edge while the gate goes low, the node paying for it before the curves of Fig.8 start).
# Where is the threshold, and is the hole charge then the same for the five cases? Write + WL off + 21 ns hold, no hole supply.
for f_ in (2, 3, 4, 5, 7): cfg2d(f"j{f_}", "F", k_cs=1.8 / 4.2, par=cal_par(1.7e21, 2.25e7, ii=f_), Npulse=0)
# The same with the default coefficients on the coarse mesh a 3D array can afford (5 nm along the channel): a mesh effect?
cfg2d("q5", "F", k_cs=1.8 / 4.2, par=cal_par(1.7e21, 2.25e7), cases=((1, "gq5_c1h", 4.7, 30), (2, "gq5_c2h", 4.7, 20)), Npulse=0)
# Round 7 (step 3, diagnosis): the FBE of Fig.8 as the paper runs it - no stand-in generation - with the impact-ionization
# coefficients x 6 and x 7. Rounds 5 / 6: with x 7 the avalanche at the WL switch-off leaves 1462 / 1334 / 1302 / 1320 holes in
# Cases 1 - 4 (the charge the loss curves ask for, `fin`: about 1300) and no droop in the hold; with x 5 it does not start
# (207 / 119 / 114 / 14). Does that state lose charge as Fig.8(b), (c) show, and where does x 6 land against the bars of
# Fig.8(a)? The factor has no source: a diagnosis, nothing to adopt without the user's word.
for f_ in (6, 7): cfg2d(f"k{f_}", "F", k_cs=1.8 / 4.2, par=cal_par(1.7e21, 2.25e7, ii=f_))
# Round 8 (diagnosis): the row hammer of Fig.7 with the impact-ionization coefficients x 7 and x 9, ideal WL, no stand-in
# generation. Round 7: with x 7 the node of Case 2 falls by 0.27 V within the first 0.5 ns of BL = 0 V in the FBE (paper: 29 mV
# in 10 ns): the parasitic bipolar transistor latches. Fig.7(a) shows such a fall for Z-Z' at BL = 0.55 V (1.1 -> 0.58 V in
# 2 ns, body 665 mV: x 7 gives 516 mV at the WL switch-off, x 10 750 mV) and none with the body grounded (0.036 mV per cycle).
for f_ in (7, 9): cfg2d(f"u{f_}", "R", rhsel=("Ryi_yy", "Rzi_zz", "Rzg_zz"), k_cs=1.8 / 4.2, par=cal_par(1.7e21, 2.25e7, ii=f_))
# Round 9 (step 2: how the FBE of the final configuration reacts to the impact-ionization coefficients, below the avalanche at
# the WL switch-off): fin2 (bar charge GBQ as a condition, node held meanwhile) with the coefficients x 4 and x 5. Round 7: with
# x 7 and about 1300 holes the first-phase loss of Case 3 is 9.5 mV (6.4 mV at that charge with the default coefficients) and
# Case 2 latches: multiplication raises the loss per hole, the more the thicker the body - the direction the paper's
# 55 / 29 / 7.1 mV ask for (model at the bar charge: 2.6 / 2.2 / 1.1).
for f_ in (4, 5): cfg2d(f"v{f_}", "F", gb=GBQ, k_cs=1.8 / 4.2, par=cal_par(1.7e21, 2.25e7, ii=f_))
# Round 10 (diagnosis of Fig.7 as the paper draws it). Fig.7(b), looked at again on 2026-10-06: a resistor R sits between the
# victim gate node and its WL source (0 V) in the floating and in the grounded configuration, a capacitor between the
# aggressor gate and the victim gate; Fig.7(a): the node falls in steps, one per aggressor pulse, from 0.45 ns on; Fig.7(e): the
# body rises 665 mV between t = 0 and t_A (0.45 ns of hammering) with the impact-ionization model on, 2.4 mV with it off. So
# the body is charged during the hammer, by the jumps of the victim gate. R = 2e5 Ohm (jump 0.21 V) with the coefficients x 5
# (no avalanche at the WL switch-off) and x 7; write and hold 1 ns each (gate node settled).
for f_ in (5, 7): cfg2d(f"w{f_}", "R", Rwl=2e5, tWr=1.0, rhsel=("Rzi_zz", "Rzg_zz"), rh=dict(tHold=1.0), k_cs=1.8 / 4.2, par=cal_par(1.7e21, 2.25e7, ii=f_))
# Round 11 (user, 2026-10-06 night: Codex does not run this): the FBE test on the time scale of the papers the IRPS paper cites
# for it. Its references [3] (Khan, TED 2024, Fig.6) and [4] (Deng, TED 2025, Fig.5(b)) toggle the BL with a period of 20 ms over
# 120 ms and let GIDL fill the floating body in the BL-high phases; Fig.8(b) of the IRPS paper shows the same staircase on an
# axis marked in ns (first fall 21, period 21). Here: no stand-in generation, nothing changed but the time scale - hold before
# the first BL fall and BL period x 1e3 .. 1e6 (21 us .. 21 ms), BL edges kept at 0.5 ns, storage node set to 1.1 V for 10 ps after
# the write and then free. Asks: does the model's own tunnelling generation bring the body to the bars of Fig.8(a), after how
# long, what does the node do meanwhile, and what is lost in the BL-low phases. A diagnosis off the paper's printed time axis.
for k_, f_ in (("z3", 1e3), ("z4", 1e4), ("z5", 1e5), ("z6", 1e6)): cfg2d(k_, "F", tHold=21.0 * f_, Tper=21 * f_, **B1)
# Round 12 (user 2026-10-07: check "the body is already charged at t = 0"; run it here, not at Codex): the state made by the
# model's own generation with the storage node held at 1.1 V through the hold (released 0.5 ns before the first BL fall), then
# the paper's waveform whole (period 21 ns, 9 low phases). Hold 15.2 / 18 / 20 / 22 us: the bars fit near 15 us, the first-phase
# losses near 20 us (NOTES (bg)). Probes across the body thickness. Codex's screen has 15.2 and 21 us with the node held, up
# to the end of the first low phase only. A diagnosis off the paper's printed time axis; the held node is a preparation.
for k_, h_ in (("n1", 15.2), ("n2", 18.0), ("n3", 20.0), ("n4", 22.0)): cfg2d(k_, "F", tHold=h_ * 1e3, SNhold=1, ProbeT=1, **B1)
# Round 13 (user 2026-10-07: the authors cannot be asked, back-calculate): WHERE and WHEN does Fig.8(a) read the body potential?
# The hole charge of each case is set by the paper's loss of the first low phase instead of by the bar (x 1.45 / 1.37 / 1.28 / 1.19 of
# the bar charge, NOTES (bg); two runs per case around that value, Case 5 at x 1.0 / 1.15), the potential is written along the whole
# channel and as region statistics. With the existing probes the reading "under the gate, BL side, BL low" gives the four bars
# within 20 mV at those states (tools/gt_ta_scan.py); this round holds every simple reading against the bars.
PLO = {1: 1.40, 2: 1.32, 3: 1.23, 4: 1.14, 5: 1.00}; PHI = {1: 1.50, 2: 1.42, 3: 1.33, 4: 1.24, 5: 1.15}
for k_, f_ in (("p1", PLO), ("p2", PHI)): cfg2d(k_, "F", gb={c: GBQ[c] * f_[c] for c in GBQ}, ProbeX=1, ProbeT=1, **B1)
# Round 14: the reading that round 13 singles out among the definitions one would write down: the AVERAGE potential of the body under
# the gate, counted from the start of the transient, at the first BL edge (the dot t_A of Fig.8(b) sits on that edge). The hole charge
# is sized to the bars of Fig.8(a) with that reading, case by case (interpolated from round 13): s1 = read just before the BL fall,
# s2 = read 0.25 ns after it. A fit to Fig.8(a) through a back-calculated definition; the losses of Fig.8(b), (c) are then predictions.
GBA = {1: 1.37, 2: 1.20, 3: 1.12, 4: 1.10, 5: 1.13}; GBB = {1: 1.56, 2: 1.31, 3: 1.19, 4: 1.17, 5: 1.18}
for k_, f_ in (("s1", GBA), ("s2", GBB)): cfg2d(k_, "F", gb={c: GBQ[c] * f_[c] for c in GBQ}, ProbeX=1, ProbeT=1, **B1)
# Round 15 (user 2026-10-07: test the origin of the body charge on a figure that is independent of Fig.8): the row hammer of Fig.6(e) /
# Fig.7 with the history that gives Fig.8 its charge. The victim's body charges by the model's own generation while its storage node
# is held at 1.1 V; then the hammer of the paper (BL Vdd/2, aggressor WL 0 <-> Vpp, 10 cycles). x1: 16.2 us with the BL at Vdd (the
# state of fin3, Case 2), then Vdd/2 for 1 ns | x2: 16.2 us with the BL at Vdd/2 (the idle bias of the hammer test) | x3, x4: the same
# with the resistor of Fig.7(b) on the victim WL (200 kOhm, a fit of 2026-10-06) | x7: 100 us at Vdd/2 (towards saturation) |
# x5, x6: x2 and x7 with the aggressor WL kept at 0 V (what the cell loses anyway). Y-Y' and Z-Z', impact ionization off / on.
HIS = 16.2e3; RHS = ("Ry_yy", "Ryi_yy", "Rz_zz", "Rzi_zz")
cfg2d("x1", "R", rhsel=RHS, rh=dict(SNhold=1, tHold=HIS, tHold2=1.0), **B1)
cfg2d("x2", "R", rhsel=RHS, rh=dict(SNhold=2, tHold=2.0, tHold2=HIS), **B1)
cfg2d("x3", "R", rhsel=RHS, Rwl=2e5, tWr=1.0, rh=dict(SNhold=1, tHold=HIS, tHold2=1.0), **B1)
cfg2d("x4", "R", rhsel=RHS, Rwl=2e5, tWr=1.0, rh=dict(SNhold=2, tHold=2.0, tHold2=HIS), **B1)
cfg2d("x5", "R", rhsel=RHS, rh=dict(SNhold=2, tHold=2.0, tHold2=HIS, Idle=1), **B1)
cfg2d("x6", "R", rhsel=RHS, rh=dict(SNhold=2, tHold=2.0, tHold2=1e5, Idle=1), **B1)
cfg2d("x7", "R", rhsel=RHS, rh=dict(SNhold=2, tHold=2.0, tHold2=1e5), **B1)
# Round 16 (2026-10-07, back-calculation of Fig.7): can the holes that impact ionization makes in the AGGRESSOR reach the victim's body?
# Fig.7(c) marks t = 0 and t_A on the first aggressor pulse and Fig.7(e) gives 665.1 mV of body rise between them with the model on (2.4 mV
# off, 1.8 mV grounded) while the node is still at 1.1 V: 1000 - 2000 holes in 94 ps that the victim's own node does not pay for. In the runs
# so far the aggressor makes 60 - 71 pairs per cycle and 0.4 (Z-Z') / 3.3 (Y-Y') holes per cycle reach the victim; 10 - 12 leave through
# the BL contact, which the 2D section puts on the pillar axis (in the array it is at the end of the pillar). Two choices the paper
# leaves open: g1 the avalanche driving force ElectricField (the write made 17 000 pairs with it instead of 600 - 900) | g2 a BL contact
# that takes no holes | g3 both | g4 both with the resistor of Fig.7(b) (2e5 Ohm, a fit). Paper timing, no stand-in, no history.
cfg2d("g1", "R", rhsel=("Ryi_yy", "Rzi_zz", "Rzg_zz"), IIdf="ElectricField", ProbeX=1, **B1)
cfg2d("g2", "R", rhsel=("Ry_yy", "Ryi_yy", "Rz_zz", "Rzi_zz"), BLhv=0.0, ProbeX=1, **B1)
cfg2d("g3", "R", rhsel=("Ryi_yy", "Rzi_zz", "Rzg_zz"), IIdf="ElectricField", BLhv=0.0, ProbeX=1, **B1)
cfg2d("g4", "R", rhsel=("Rzi_zz", "Rzg_zz"), IIdf="ElectricField", BLhv=0.0, ProbeX=1, Rwl=2e5, tWr=1.0, rh=dict(tHold=1.0), **B1)
# Round 18 (2026-10-07, after round 16): with ElectricField and a BL contact that takes no holes the victim's body gains 600 - 1200 holes per
# aggressor cycle and its node starts to fall while the aggressor is high, in Z-Z' and in Y-Y' alike; the runs stall after 2 - 4 cycles
# (time steps of 1e-16 s at the storage-node-side gate edge). g5 = g3 with ErrRef(Electron) 1e12 (numerics only: does the node go on to
# fall?) | g6 = g5 with the text's capacitors (4.2 fF on both cells: the first aggressor pulse moves 2.3 times the charge) | g7 = ElectricField
# with the BL contact where a pillar has it, at its end: bottom end, below the victim, ohmic (structures gr_zzb / gr_zzbg): is Z-Z' then
# hit and Y-Y' (g1: contact at the top end, 40 nm from both junctions) not, as in the paper?
cfg2d("g5", "R", rhsel=("Ryi_yy", "Rzi_zz"), IIdf="ElectricField", BLhv=0.0, ProbeX=1, ErrE=1e12, **B1)
cfg2d("g6", "R", rhsel=("Rzi_zz",), IIdf="ElectricField", BLhv=0.0, ProbeX=1, ErrE=1e12, k_cs=1.0, par=B1["par"])
cfg2d("g7", "R", rhsel=("Rzbi_zz", "Rzbg_zz"), IIdf="ElectricField", ProbeX=1, ErrE=1e12, **B1)
# Round 19 (2026-10-07): g5 stalls where g3 did (victim body about 3000 holes; Newton oscillates on the electron density, 3e12 cm^-3, in
# the hole accumulation layer at the gate oxide, 1.5e20 cm^-3, 10 nm inside the gate from the storage-node side). Numerics only:
# ErrRef(Electron) 1e17 takes that density out of the convergence test (the electrons that carry the node's loss are far denser).
# g8 = g3 | g9 = g7 (BL contact at the bottom end, ohmic) | g0 = g9 with the text's capacitors (4.2 fF).
cfg2d("g8", "R", rhsel=("Rzi_zz",), IIdf="ElectricField", BLhv=0.0, ProbeX=1, ErrE=1e17, **B1)
cfg2d("g9", "R", rhsel=("Rzbi_zz",), IIdf="ElectricField", ProbeX=1, ErrE=1e17, **B1)
cfg2d("g0", "R", rhsel=("Rzbi_zz",), IIdf="ElectricField", ProbeX=1, ErrE=1e17, k_cs=1.0, par=B1["par"])
# Round 20 (2026-10-07): seen in rounds 16 - 19: with ElectricField the write is much faster (the body fills with holes while the WL is
# high), 0.96 / 1.13 / 1.16 / 1.17 V at 12 / 24 / 39 / 60 ps with 1.8 fF, and 0.78 / 1.02 / 1.10 / 1.14 V with the TEXT's 4.2 fF (paper Fig.4(a)
# 0.72 / 0.92 / 1.06 / 1.13 V; default driving force with 4.2 fF: 0.51 / 0.72 / 0.86 / 0.97 V, which is why 1.8 fF was fitted). So: the write and
# the FBE of the five cases with ElectricField and the text's capacitors (5.1 / 4.2 / 3.6 fF), no stand-in. o4 BL contact takes no holes |
# o5 contacts as they are (write only).
cfg2d("o4", "WF", IIdf="ElectricField", BLhv=0.0, ProbeX=1, ProbeT=1, par=B1["par"])
cfg2d("o5", "W", IIdf="ElectricField", par=B1["par"])
# Round 17 (2026-10-07, back-calculation of the hole charge of Fig.8 after the first look at round 16): with the driving force ElectricField the
# write of the cell itself makes about 6300 pairs (default 150), and what the contacts do not take stays in a floating body. FBE of the five
# cases with the paper's waveform, NO stand-in generation: o1 ElectricField + BL contact that takes no holes | o2 the same + storage-node
# contact that takes no holes | o3 both contacts closed for holes, default driving force (which of the two does it).
cfg2d("o1", "F", IIdf="ElectricField", BLhv=0.0, ProbeX=1, ProbeT=1, **B1)
cfg2d("o2", "F", IIdf="ElectricField", BLhv=0.0, SNhv=0.0, ProbeX=1, ProbeT=1, **B1)
cfg2d("o3", "F", BLhv=0.0, SNhv=0.0, ProbeX=1, ProbeT=1, **B1)
# ---- 3D with what the 2D rounds fixed (user 2026-10-06: rebuild 3D from the improvements, then the picture check against the
# paper). The structures are the checked ones (g3_c2h unit cell, g3x_c2h X-X' pair); what changes is in the decks: storage node
# 1.8 fF, Hurkx Agen 1.7e21, the paper conditions (PC), the hole charge of Fig.8(a) as a condition. Not started without the
# user's word (each transient takes hours); E3H is the short one that answers "does 3D fill the body by itself".
P3 = dict(PC, Par=cal_par(1.7e21, 2.25e7), Lin3="Pardiso", Nthr=8)
RUNS.append(R("E3I_c2", "GT", "g3_c2h", "idvg", WFs=4.7, WFd=4.7, **dict(IV, Par=P3["Par"])))
RUNS.append(R("E3W_c2", "GT", "g3_c2h", "cho:W", WFs=4.7, WFd=4.7, II=1, Cs=1.8e-15, **dict(P3, ErrH=1e14)))
F3 = dict(P3, II=1, Tper=21, tEdge=0.5, tHold=21.0, ErrH=1e14)
RUNS.append(R("E3H_c2", "GT", "g3_c2h", "cho:FBE", WFs=4.7, WFd=4.7, Cs=1.8e-15, **dict(F3, Npulse=0)))                 # write + 21 ns hold, no supply
RUNS.append(R("E3K_c2", "GT", "g3_c2h", "cho:FBE", WFs=4.7, WFd=4.7, Cs=1.8e-15, **dict(F3, Npulse=0, Gb=GB0[2])))      # sizing of the supply in 3D
RUNS.append(R("E3F_c2", "GT", "g3_c2h", "cho:FBE", WFs=4.7, WFd=4.7, Cs=1.8e-15, **dict(F3, Npulse=9, Gb=GBQ[2])))      # FBE at the 2D rate (to be replaced by the 3D sizing)
RUNS.append(R("E3F125_c2", "GT", "g3_c2h", "cho:FBE", WFs=4.7, WFd=4.7, Cs=1.8e-15, **dict(F3, Npulse=9, Gb=GBQ[2] * 1.25)))     # 1.25 x that charge (2D: where the losses fit); user 2026-10-07: the check in 3D
# 2026-10-07, after round 14: the back-calculated reading of Fig.8(a) (average potential of the body under the gate at the first BL
# edge) in 3D. Two charges around the one that puts that reading on the bar in 2D (x 1.31 of the old bar charge for Case 2).
for nm_, f_ in (("E3S1_c2", 1.31), ("E3S2_c2", 1.45)):
    RUNS.append(R(nm_, "GT", "g3_c2h", "cho:FBE", WFs=4.7, WFd=4.7, Cs=1.8e-15, **dict(F3, Npulse=9, Gb=GBQ[2] * f_, ProbeX=1)))
for nm_, ii in (("E3X_xx", 0), ("E3Xi_xx", 1)):
    RUNS.append(R(nm_, "GT", "g3x_c2h", "cho:RH", WFs=4.7, WFd=4.7, II=ii, Cs=1.8e-15, **dict(P3, ErrH=1e14, tON=0.094, tOFF=0.094, Ncyc=10)))

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
    # one run: refused if a process already works in the folder (two batches wrote into one folder on 2026-10-06); the log and the
    # stdout capture (the same text twice) are gzipped when the run ends: the account's disk quota is 10 GB (tools/gz_logs.sh)
    sh += ["cd ..", "run() { cd \"$1\" && ( flock -n 9 || { echo \"$1 exit=99 (a process is already running in this folder)\"; exit 0; }; "
           "sdevice \"$1_des.cmd\" > \"$1.out\" 2>&1; e=$?; gzip -f \"$1.out\" \"$1_log_des.log\" 2> /dev/null; echo \"$1 exit=$e\" ) 9> .lock; cd ..; }", "export -f run"]
    two = [r["id"] for r in rows if r["dim"] == 2]; three = [r["id"] for r in rows if r["dim"] == 3]
    if two: sh.append("printf '%s\\n' " + " ".join(two) + " | xargs -P \"$JOBS\" -I{} bash -c 'run {}'")
    for t in three: sh.append(f"run {t}")
    wtext(os.path.join(a.out, a.sh), "\n".join(sh) + "\n"); os.chmod(os.path.join(a.out, a.sh), 0o755)
    print(f"wrote {len(rows)} runs, {len(used)} structures -> {a.out}")

if __name__ == "__main__":
    main()
