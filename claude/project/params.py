# -*- coding: utf-8 -*-
"""
params.py — single source of every value of the Cho-cell TCAD (VBL / HWL 1T1C 3D DRAM cell).
Paper: Cho, Hsu, Lee, Sharda, Datta, Yu, "Row Hammer Effect and Floating Body Effect of Monolithic 3D Stackable 1T1C
DRAM", IRPS 2026. Change values here (or per structure / run in make_runs.py), then run make_runs.py.

Source tags:  [Cho]   stated in the paper (Fig.5(a), Fig.5(b), text)
              [ChoF]  read from a drawing of the paper (not stated as a number)
              [Grp]   from another paper of the Shimeng Yu group or a paper the IRPS paper cites
              [Fit]   not given anywhere: fixed by a curve of the paper (which one is said)
              [ASM]   assumption / numerics
Lengths in nm, concentrations in cm^-3, voltages in V, times in ns unless said.
"""
P = dict(
    Dim=2,              # 2 = section along the channel (sde_gt_dvs.cmd); 3 = unit cell (sde_gt3_dvs.cmd)
    Tpl="sde_gt_dvs.cmd",
    BodyMode="NOBODY",  # no body electrode (the deck builders ask)

    # ---------------- structure (defaults = Case 2 of Fig.5(b))
    Lg=100,             # gate length                                                      [Cho]
    Tbody=20,           # body thickness: 30 / 20 / 10 (Cases 1 / 2 / 3-5)                 [Cho]
    Tox=5.0,            # gate dielectric thickness                                        [Cho]
    Tgm=20,             # gate (word line) thickness, main and back gate                   [Cho]
    Dvox=30,            # vertical isolation oxide between two layers                      [Cho]
    Nsd=1e20,           # source and drain (BL) donors                                     [Cho]
    Nch=1e18,           # body acceptors: 1e18, 1e16 in Cases 4 / 5                        [Cho]
    Gdi="HfO2",         # gate dielectric material. The paper says "gate oxide" only; 5 nm of SiO2 spreads the thresholds of
                        # Cases 1-4 over 0.35 V (paper 0.08 V). Permittivity 22 = Sentaurus default   [Fit: Fig.5(c)]
    Spm="Si3N4",        # spacer material: its own colour in Fig.2; the group's models hold SiO2 and Si3N4 (k 7.0, Lee .. Yu,
                        # IMW 2026) and the gate-level layer of its VBL flow is Si3N4 (Wu .. Yu, Wong, TED 2025)   [ChoF + Grp]
    Lsp1=25,            # BL-side spacer; p body under it (Fig.2: 0.25 Lg)                 [ChoF]
    Lsp2=25,            # storage-node-side spacer; the N+ source lies under it            [ChoF]
    Wbl=100,            # bit-line pillar along the channel. 100 = the cross-section drawing; 50 keeps the table's WL pitch of
                        # 275 nm and is used for the 3D cell (user 2026-10-05; back to 100 if it makes trouble)   [ChoF]
    Wact=100,           # silicon row along the word line = BL pitch 200 - wall 100: scales the 2D current       [Cho]
    Dhox=100,           # isolation wall between two rows (3D cell only)                    [Cho]
    Wcut=20,            # 3D X-X' pair only: gap that cuts the word line in the middle of the wall (the paper decouples
                        # the WL "hypothetically" and gives no geometry)                    [ASM]
    Pair="one",         # section: "one" cell, "yy" = two cells across the BL (RH Case 1), "zz" = two layers (RH Case 2);
                        # 3D template: "xx" = two rows across the isolation wall (RH Case 3)    [Cho]
    Bgc=0,              # 1 = contact "body_v" in the victim body: the hypothetical grounded body of Fig.7(b)    [Cho]
    Mc=2, Mj=0.5, Mv=1, Mi=0.2, Mg=1,   # mesh of the 2D section [nm]: along the channel, at the two junctions, across the body,
                        # at the gate dielectric; Mg = smallest step the doping-gradient refinement may take along the
                        # channel (not physics: the paper gives no mesh)                     [ASM]

    # ---------------- gates, cell, biases
    WFs=4.7, WFd=4.7,   # work function of main / back gate: 4.7, 5.0 in Case 5            [Cho]
    Vdd=1.1,            # BL high / storage node '1'                                        [Cho]
    Vpp=1.8,            # WL high                                                           [Cho]
    Vnwl=0.0,           # WL low                                                            [Cho]
    Vb=0.0,             # not used (no body electrode)
    Rb=1e-3,            # not used (no body electrode)
    Cs=4.2e-15,         # storage capacitor [F]: 3.6 / 4.2 / 5.1 fF for 10 / 20 / 30 nm body (text). The write curve of Fig.4(a)
                        # asks for 1.5 - 2.1 fF                                             [Cho]
    Rwl=0.0,            # resistance between the victim gates and their WL source [Ohm] ("R" in Fig.7(b), no value)   [ASM]

    # ---------------- Id-Vg deck (Fig.5(c))
    Vds=1.1,            # drain bias = Vdd (not stated)                                     [ASM]
    Dterm="bl",         # the bit line is the drain                                         [Cho]
    VgMin=-1.0, VgMax=1.8, SwDown=1,     # gate swept down from VgMax (the up-sweep of the 1e16 body stalls)
    SwT=0.0,            # > 0: the gate sweep as a transient of this many seconds instead of a quasistationary ramp
                        # (floating body with the density-corrected tunnelling model: the DC sweep does not converge)

    # ---------------- transient decks (deck_cho): write as in Fig.4(a), then FBE (Fig.8) or RH (Fig.6, 7)
    Vwr=0.0,            # BL level during the write; 0 = Vdd. Fig.4(a) reads 1.168 V       [ChoF]
    tWr=0.3,            # write: WL high time. Fig.4(a) shows the WL high from 15 ps to the end of its window at 120 ps:
                        # 0.105 in the paper-condition runs (P*)                              [ASM] / [ChoF]
    SNset=0.0,          # > 0: storage node set to this value for 10 ps when the write is over (WL at 0 V, BL at Vdd), then
                        # released: the initial state of Fig.8(b), (c) and Fig.6(e), where every curve starts at 1.1 V at
                        # t = 0 ("after storage node is charged to '1'")                     [ChoF]
    tWf=5.0,            # WL fall time at the end of the write [ps]. The paper shows the WL high to the end of Fig.4(a) and at 0 V from the
                        # start of Fig.4(b), (c); how it gets there is not shown.                [ASM]
    Rbl=0.0,            # > 0: resistor [Ohm] between the BL source and the pillar contact (the paper's pillar runs through 64
                        # layers to its contact; an N+ pillar 100 nm x 100 nm is about 100 Ohm per layer). Y-Y' candidate.  [ASM]
    SNa0=0.0,           # > 0: the aggressor cell is written together with the victim and its storage node set to this value [V]
                        # when the victim's is (0 = it stays at '0'; the paper does not say which)                 [ASM]
    Gb=0.0,             # > 0 (FBE and RH, with SNset): electron-hole pairs made uniformly in the floating body at this rate [cm^-3 s^-1]
                        # between the write and the first BL fall, storage node held at SNset meanwhile. Sized per case so that
                        # the body-centre potential at t_A stands above its value at the start of the transient by what Fig.8(a)
                        # shows (555 / 445 / 365 / 320 / 368 mV): Fig.8(a) used as a condition. The source of the paper's holes
                        # is not known; this is a stand-in for it, off after t_A.               [fit to ChoF Fig.8(a)]
    SNhold=0,           # 1 (FBE, with SNset, without Gb): the storage node stays held at SNset through the whole hold and is
                        # released 0.5 ns before the first BL fall: the body charges by the model's own generation while the
                        # node does not pay for it ("charged at t = 0" as a state that was prepared; a diagnosis)      [ASM]
    ProbeT=0,           # 1: CurrentPlot probes across the body thickness at the probe's x (1 nm inside both gate-oxide
                        # interfaces, 1/4 and 3/4 of the thickness): the paper does not say where it reads the body potential
    tHold=0.05,         # wait after the write / before the first edge. Fig.8(b) from the pixels (2026-10-06): first BL fall
                        # at 21.0 ns (FB2 in make_runs.py: 20.7 after the write); read by eye before: about 16 ns (FB)   [ChoF]
    tEdge=0.1,          # BL edge of the FBE pulses (not given; FB2: 0.5 ns, 10 + 0.5 + 10 + 0.5 = 21)   [ASM]
    Tper=20, Npulse=10, # FBE: BL 0 <-> Vdd, 50 %. Fig.8(b) from the pixels: period 21.0 ns, 9 low phases in 200 ns (FB2);
                        # 20 ns and 10 pulses were read by eye (FB, runs RF / RD / RA)        [ChoF]
    tON=0.094, tOFF=0.094, Ncyc=10,      # RH: aggressor WL 0 <-> Vpp, 10 pulses (Fig.6(c))   [ChoF]

    # ---------------- physics switches
    Temp=300,           # the 60 mV/dec of Fig.5(c) is 300 K                               [Fit: Fig.5(c)]
    Bgn="OldSlotboom",  # band-gap narrowing model (EffectiveIntrinsicDensity); the Sentaurus default is BennettWilson   [ASM]
    GR=1, SRHon=1, SRHdd=1,              # SRH with the default doping-dependent lifetimes  [ASM]
    TAT=0,              # field-enhanced SRH                                                [ASM]
    BTBT=1,             # 1 = Hurkx (the paper's model, default coefficients); 3 = the same with DensityCorrection=Local (the
                        # densities in its D factor corrected by the quasi-Fermi gradient: not "D off"; diagnostic only,
                        # NOTES (au)); 2 = non-local path model                              [Cho] / [ASM]
    II=0,               # impact ionization (the paper: off in Fig.5(c) / 6(e), on in Fig.7)   [Cho]
    IIdf="",            # its driving force: "" = Sentaurus default (GradQuasiFermi), "Eparallel", "ElectricField"   [ASM]
    BLhv=-1.0,          # hole recombination velocity at the BL contact [cm/s]; -1 = ohmic. The 2D section puts the contact
                        # on the symmetry plane of the pillar, 50 nm from the junction; in the 3D array it sits at the
                        # end of the pillar. 0 = the contact takes no holes (electrons: 1e7 cm/s)   [ASM]
    Dit=0, QC=0, ThinL=0,                # no interface traps, no quantum correction, no thin-layer mobility   [ASM]
    Mob=3,              # mobility: doping dependence + 3 = high-field saturation for electrons only (with it on holes the
                        # transient stalls at the WL edge; the Id-Vg is the same) / 2 = both carriers / 1 = + normal field /
                        # 0 = doping dependence only                                        [Fit: Fig.5(c)]

    # ---------------- Newton settings (sdevice Math)
    NewtIter=40, NotDamped=50, Extrap=1, # transients: 60 / 10 / 0
    ErrH=1e10,          # ErrRef(Hole); 1e14 for the transients of the 1e18 bodies
    ErrE=1e8,           # ErrRef(Electron)
    XP=0,               # 1 = Math ExtendedPrecision
    RefD=1e12,          # RefDens_[e|h]GradQuasiFermi_ElectricField
    Dig=5,              # Math Digits
    Nthr=8,             # sdevice threads per run (4 in the 2D experiment rounds: more runs side by side)
    Lin3="ILS",         # linear solver of the 3D decks: "ILS" (iterative) or "Pardiso" (direct; the ILS stalls at 200 inner
                        # iterations once the channel is on)

    Par="sdevice.par",  # parameter file (written by make_runs.py)
)
