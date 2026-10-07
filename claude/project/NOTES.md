# NOTES — Cho cell (VBL / HWL 1T1C 3D DRAM): decisions, checks, results

Newest first. Entries (ai) .. (as) were written while this work still lived in `bcvfet_tcad`; file and run names in them are
the ones of that time (structures `gx_*` / `gp_*` are the meshes before the doping went per region, `gr_*` the current ones).

## 2026-10-08 (bs) user: "all of it as an eliU report once everything, Codex's experiment included, has finished; with the remaining problems, the improvement measures and their explanation" - the complete report; found while writing it: Fig.6(e) read for the first time (reversible swing), the contact position decides Case 1's losses, Codex's late-reset scores are counted from the node before the reset, one common hold time does not give the five cases
- Report: `Desktop\서강대\반엘프\results_vbl_hwl_1t1c_3ddram\GT_IRPS2026_전체보고_eliU_2026-10-08.html`, built by `tools/make_eliu_report_full.py` (text in
  `tools/eliu_full_text.py`; page builder and text checks of `tools/make_eliu_report.py`): 557 sentences, 6.6 units per sentence, no analogy word,
  69 numbers of the text asserted against the run files of the shared copy or by arithmetic; pictures `gt2d_full_01 .. 07` new (scoreboard, Id-Vg,
  write, FBE, Codex, Fig.6(e) swing and loss, common hold time), eight earlier ones reused; no crop of the paper. Sections: where the work stands |
  concepts | goal and rules | structure with the kind of every value | Fig.5(c) and 5(d) | the Hsu check | Fig.4(a) | Fig.8 | origin of the holes |
  Fig.6(e) | Fig.7 candidate (two sections) | ElectricField everywhere | decisions A - D with the contact table | 3D | Codex | my ten errors |
  remaining problems P1 - P8 | measures M1 - M7, each with its explanation | six decisions for the user. No new simulation: the server was Codex's.
- Held against the sources while writing (my summary / first draft was wrong or loose here):
  * the 3D X-X' row hammer HAS run (2026-10-06, (aw): X3p, 0.00066 mV per cycle, swing +0.116 mV, text Cs 4.2 fF); what has not run is the rebuilt pair
    with today's device (E3X decks).
  * the paper's own words (text re-read): the storage node is "geometrically defined" (captions of Fig.2 and Fig.4); the text's Cs (3.6 / 4.2 / 5.1 fF)
    is "calculated using the dimensions" of Fig.5(a) (EOT 3.8 A, L_CAP 100 nm) for the sense margin, the capacitance of the TCAD structure is not
    given; S/D 1e20 stands in Sec.III; row hammer 0.05 / 0.01 / 0.006 mV per cycle with thresholds 11.3k / 60.5k / 100.8k.
  * grounded body with the candidate mechanism of Fig.7: 0.008 (g7) / 0.010 (g3) / 0.013 (g4) mV per cycle over the last five cycles (0.010 - 0.013 was written).
  * what the write leaves: default driving force 103 / 35 / 9 / 2 / 1 holes (ohmic contacts), 213 / 151 / 114 / 161 / 205 with both contacts closed (o3);
    pairs made during the write 620 - 902 with the text's capacitors (b0) and 132 - 224 with the fitted ones (fin): about the same in all five cases, as
    the charge the bars need is (1130 - 1601 holes), and 1.3 - 2.2 times short with the text's capacitors.
- Fig.6(e) read from the embedded image for the first time (`tools/gt_rh_ripple.py`; scratch scripts fig6e_px*.py; the crop stays in the scratch folder).
  Frame rows 771.5 .. 1084.5 = 1.120 .. 1.080 V (the two lower axis labels are misprinted "1.109", "1.108"): 0.128 mV per pixel row, 1.100 V = row 928.
  Blue = Case 3, X-X', drawn on top: a square wave on rows 928 - 929 while the aggressor WL is HIGH and on row 934 while it is low (the waveform of
  Fig.6(c) starts high at the left frame; the twenty transitions of the node sit on its edges within 2 px): a reversible swing of +0.70 mV (+-0.13),
  no drift within a row over the ten cycles (text: 0.006 mV per cycle = half a row). Magenta = Case 1, Y-Y': no swing in the first two pulses (it stays
  on 928 - 929 while blue is down), then rows 929 - 932: a drift of 0.3 - 0.4 mV by the seventh pulse (text: 0.05 mV per cycle). Red = Case 2, Z-Z':
  hidden under the other two. (My first reading had the sign wrong: I took the waveform of (c) to start low.)
  The model: swing Y-Y' 0.000 mV (as the paper), Z-Z' +0.47 mV (fin5, 1.8 fF; +0.20 at 4.2 fF), 3D X-X' +0.116 mV (4.2 fF); with the WL resistor it
  grows (+0.66 mV at 2e5 Ohm, +3.3 mV at 1e7, victim gate +35 .. +239 mV). As a capacitive divider (swing = 1.8 V x C_c / C_s) the paper's X-X' has
  C_c = 0.70 aF (1.8 fF) .. 1.6 aF (4.2 fF), our transistor-only 3D pair 0.27 aF: 2.6 - 6 times less. And the paper's Y-Y' loses most with no swing at
  all: its loss is not coupling to the node. Both go into the measures (M1: storage node as a structure; M4: 3D pairs with it, swing first).
- Contact position and Case 1 ((bn) gave the group scores only). No avalanche model, same stand-in rates:
    first-phase / later loss [mV]   paper        axis contact (fin3n = dl)   end contact (fin4 = dm; fin5 within 5 %)
    Case 1                          55 / 100     60.9 / 112.9                81.6 / 163.8
    Case 2                          29 / 50      18.6 / 49.1                 21.5 / 62.8
    Case 3                          7.1 / 14.6   4.4 / 12.9                  4.7 / 14.9
    Case 4 (after two low phases)   3.5 / 5.0    3.4 / 5.01                  3.7 / 5.58
  Group scores the same (0.45 / 1.42 against 0.43 / 1.46: Case 5 rules L2), but per case the axis contact has every later loss within 13 % and the end
  contact has Case 1 64 % high; the first-phase losses of Cases 2, 3 are a little closer with the end contact. P6 ("Case 1 loses 1.5 - 1.65 times the
  paper's") moves with decision B. Not changed: fin5 stays (the candidate of Fig.7 needs the end contact); where the contact sits is to be settled on a
  pillar of several layers (M4). Put to the user as a decision.
- Other things looked up for the measures, existing runs only: spacer material against the hold leak (Case 2: Si3N4 11.6, SiO2 11.2, HfO2 13.1 pA): no
  lever for Case 5. Avalanche models of the installed release (manual): vanOverstraeten (default), Okuto, Lackner, UniBo, UniBo2; only the default has
  been used; driving forces: three tried. No Auger recombination in the decks (noted, not changed). Fig.5(d) (sense margin, (al)) is in the report as
  reproduced by the formula.
- Codex's factorial (fin3 base: 720 runs = 5 cases x 12 preparations x 3 storage-node protocols x avalanche on / off x 2 capacitors) ended on 2026-10-08
  04:49 (its logs: QUEUE COMPLETE, NIGHT CONTROLLER EXIT complete=True; 720 valid results). Its result files were copied from the server (read only)
  and ranked with the rule of its own rank.py: `tools/codex_rank_snapshot.py` -> `claude/data/tables/codex_fin3_ranking_as_read.json` (origin/main
  still held its state of 21:42). By Codex's scoring 10 of the 144 groups pass all five cases (groups 13, 15, 29, 31, 49, 53, 63, 67, 85, 89).
  * A point about that scoring, to be told to Codex (its files are untouched): the losses are counted from the node just before the first BL fall
    (`SN_prefall_V`, read before the late reset, which acts in the last 10 ps). In the late-reset groups with natural generation the node has drooped
    36 - 146 mV by then, so their losses come out negative and their scores are 45 - 146. Counted from the reset node (loss + droop) the group natural
    x 1.2, late reset, avalanche off passes: bars 548 / 444 / 378 / 334 / 395 mV, first-phase loss 52.0 / 17.4 / 6.0 / 4.6 mV, 200 ns 102.5 / 47.1 / 15.2 mV.
  * Re-scored my way (`rescore` / `mine` in the builder: targets of tools/paper_targets.py, late reset counted from the reset node, the later loss of
    Case 5 left out because it is the 1.6 mV hold leak in every group, a pass only with the node at 1.1 V at t_A): 10 groups pass (13, 15, 35, 49, 57,
    63, 71, 85, 89, 93). Natural generation 3 of 36, pairs put into the whole body 4, into the BL-side 25 nm 3, into the storage-node-side 25 nm 0;
    factor 0.8: 0 of 48, 1.0: 7, 1.2: 3; node clamped 5 of 48, late reset 4, released early 1; avalanche off 4 of 72, on 6; text capacitors 0 of 72,
    write-fit capacitors 10. So: the same body state gives the same Fig.8 whatever made it (stand-in pairs or the model's own GIDL over 14.6 -
    24.7 us); 20 % of charge is the whole tolerance; the text's capacitors never pass; pairs put in at the storage-node side never pass.
  * Best group (worst item 0.58): pairs in the whole body x 1.2, avalanche model off (g63 clamped, g71 late reset): Case 1 loses 54.3 / 105.0 mV
    (paper 55 / 100), Case 2 19.3 / 49.8, Case 3 6.3 / 15.6, on the fin3 structure, i.e. with the AXIS contact: the direction of the contact table above.
- Measure M2 (one common hold time for the five cases) carried out on Codex's natural-generation runs, no new run (`common_time` in the builder;
  picture gt2d_full_07): the bar and the losses of each case interpolated in log t between its three hold times (0.8 / 1.0 / 1.2 of its own time);
  all five cases are covered from 16.5 to 17.5 us only. Best common time 17.5 us (node clamped, avalanche on): worst item 1.94 (Case 3 first-phase
  loss 1.86 against 7.1 mV; bars Case 5 +55 mV, Case 1 -36 mV); the other three combinations 2.13 / 2.95 / 3.18. Bars grow with the hold time, so
  no common time mends Case 1 and Case 5 together. The model's GIDL charges the five cases at different speeds (own times 20.6 / 16.2 / 19.6 / 18.7 /
  14.6 us, ratio 1.41) while the bars ask for about one hole charge: a GIDL history with ONE hold time is not the origin of the charge of Fig.8.
  M2 is closed. (What does scale alike in the five cases is the charge through the channel during the write: that is why M3 looks at what the write
  leaves once the avalanche model is chosen by Fig.7.)
- Remaining problems as the report lists them: P1 origin of the hole charge | P2 Fig.6(e) (loss per cycle 0.0014 / 0.0014 / 0.00066 against 0.0535 /
  0.0100 / 0.0060; swing X-X' 0.12 against 0.70 mV) | P3 Fig.7 (size, Y-Y') | P4 storage capacitor of the transient (1.8 fF fitted, 4.2 fF calculated
  in the text; two faces of the drawn storage-node block at EOT 3.8 A are 1.82 fF) | P5 Case 5 at 200 ns | P6 Case 1 and the tail of the write |
  P7 3D pairs with today's device, ElectricField numerics | P8 what the figures do not let one read. Measures: M1 storage node as a structure (AC
  capacitance, write curve, swing) | M2 one common hold time (done, see above) | M3 kind and driving force of the avalanche model against Fig.7(e), and
  what the same setting leaves after the write | M4 3D pairs with the structural node | M5 position of the storage-node junction inside the reading
  error of Fig.2 | M6 numerics | M7 way of working (kind and source curve of every read value, reading scripts kept, old runs to the PC).
- Shared: branch `claude` (tools, report, pictures gt2d_full_*, tables `fig6e_reversible_swing.txt`, `contact_position_case_losses.txt`,
  `codex_fin3_ranking_as_read.json`, status / analysis 11 / register note). Nothing of mine ran on the server.

## 2026-10-07 (br) user: "A, B, C as they are; start D" - the device is now `fin5`: BL contact of the single cells at the pillar end, no avalanche model in Fig.4(a) / 5(c) / 8, Hurkx A 1.2e20 and B 2.0e7 back-calculated from the GIDL branch of Hsu's silicon transistor. Case 5 does not move with A and B: its hold leak is not set by the tunnelling rate
- Decisions (user, 21:40): A = no avalanche model in Fig.4(a) / Fig.8 (it stays for Fig.7, where the paper names it); B = BL contact of the
  single cells at the pillar end (gr_c1hb .. gr_c4hb; the pairs gr_yy, gr_zzb, gr_zzbg have it there already); C = the blue stretch of the
  1.1 V line of Fig.8(c) is curve 5 (Case 5 scored as loss / 0.5 mV); D = back-calculate the Hurkx field coefficient B. With A and B alone
  the device is `fin4` (the runs of fin3bn: Dd0I, DdoW, DdmF): IV 0.73, W 1.12, BR 0.07, L1 0.43, L2 1.46.
- Round 30 (`run_d30.sh`, 21:27 - 21:41, 22 runs, gr_c1hb .. gr_c4hb; Codex's state fetched, registered and pushed, decks and parameter
  files md5-equal PC / server, gate ALL PASS with the four lines read; conditions re-read: Cho Fig.5(c), Fig.8(b),(c), Hsu Fig.2(c)): B =
  2.25e7 / 2.1e7 / 2.0e7 / 1.9e7 V/cm with A = 1.7e21 / 3.3e20 / 1.1e20 / 3.6e19 (A scaled so that the rate at the 0.91 MV/cm of the Id-Vg
  branch stays; the branch goes with A, so one run per B fixes A afterwards). Tool `gt_hurkx_scan.py`.
    B [V/cm]  A run  | Cho Fig.5(c) at -1 V, model - paper, Cases 1 - 5 (mean) | A fitted | Hsu Fig.2(c) branch as run, -0.7 .. -1.75 V | tilt  | Case 5 at 200 ns, leak
    2.25e7    1.7e21 | +0.01 -0.04 -0.07 -0.23 +0.02 (-0.06)                   | 1.96e21  | -0.30 -0.24 -0.20 -0.17 -0.01 +0.09 +0.09  | +0.39 | 1.577 mV, 13.54 pA
    2.1e7     3.3e20 | +0.03 -0.04 -0.09 -0.22 -0.01 (-0.07)                   | 3.84e20  | -0.10 -0.06 -0.06 -0.06 +0.03 +0.09 +0.06  | +0.15 | 1.576 mV, 13.54 pA
    2.0e7     1.1e20 | +0.05 -0.04 -0.10 -0.22 -0.04 (-0.07)                   | 1.30e20  | +0.05 +0.06 +0.03 +0.01 +0.06 +0.08 +0.03  | -0.01 | 1.575 mV, 13.53 pA
    1.9e7     3.6e19 | +0.05 -0.05 -0.12 -0.23 -0.07 (-0.08)                   | 4.37e19  | +0.19 +0.18 +0.12 +0.08 +0.08 +0.07 +0.00  | -0.18 | 1.573 mV, 13.52 pA
  (Hsu's conditions with the work function 4.27 eV on the end-contact Case 3 cell: thresholds +0.003 / +0.003 / -0.006 V, 60.2 mV/dec,
  on-current within 0.01 decade.)
  * B: the shape of Hsu's GIDL branch (tilt = residual at -1.75 V minus at -0.7 V) is the model's at B = 2.0e7 V/cm. The tilt moves 0.17
    decade per 0.1e7 and the branch is read to about 0.1 decade: B = 2.0 (+-0.1) e7. At 2.0e7 the seven residuals are +0.01 .. +0.08.
  * A: Cho's five points at -1 V ask for 1.3e20, the level of Hsu's branch for about 1.0e20: A = 1.2e20, both within 0.1 decade.
  * Case 5: the loss at 200 ns does NOT move (1.577 -> 1.573 mV) while A changes 47-fold and B by 16 %; leak 13.5 pA, 15.7 tunnelling
    pairs throughout. My forecast in (bo) and in the report before it ("B 2.1e7 cuts the hold leak by about 3") was WRONG. It took the
    leak of the storage-node corner to go with A exp(-B / F) like the Id-Vg branch. At that corner (3.4 MV/cm, the gate edge on the
    junction) the rate of the formula is microamperes, and what the model lets through is fixed by its density factor, i.e. by how fast
    the carriers leave the spot, not by A or B. ((as) of 2026-10-05 had seen it: "the default Hurkx setting damps exactly that"; I did
    not connect it with Case 5.)
- Round 31 (`run_d31.sh`, 21:45, 17 runs, 12 at a time because Codex had gone to 16 workers; gr_c1hb .. gr_c4hb, gr_yy, gr_zzb, gr_zzbg,
  gate ALL PASS with the seven lines read): the device with A 1.2e20, B 2.0e7 = `fin5` (tag dy; Hsu's conditions hy).
    Fig.5(c): thresholds as before; GIDL at -1 V -13.42 / -13.21 / -13.16 / -13.39 / -12.86 (paper -13.5 / -13.2 / -13.1 / -13.2 / -12.85);
              minimum -16.9 .. -17.0 (was -17.1 .. -17.3; paper -16.4 .. -16.9). IV 0.72.
    Hsu Fig.2(c): branch +0.08 +0.10 +0.07 +0.05 +0.10 +0.12 +0.07, tilt -0.01 (old coefficients: -0.30 .. +0.09, tilt +0.39).
    Fig.4(a): 0.736 / 0.912 / 1.015 / 1.083 V. W 1.12 (as fin4: the write has no avalanche model now).
    Fig.8: holes 1601 / 1371 / 1307 / 1130 / 1349; bars 557 / 448 / 367 / 323 / 372; first low phase 82.8 / 22.2 / 4.92 / 3.82 / 0.13 mV;
           200 ns 165.1 / 63.9 / 15.5 mV (Cases 1 - 3), Case 4 after two low phases 5.81 (paper 5.0), Case 5 1.58. BR 0.10, L1 0.42, L2 1.46
           (Case 5 alone carries L2 above 1).
    Row hammer on the end-contact pairs (Fig.6(e): model off; Fig.7: on, default driving force): Y-Y' 0.00138 mV per cycle (paper
           0.0535), Z-Z' 0.0014 in the last five cycles (0.0100); with the model Y-Y' 0.0002, Z-Z' node 0.035 mV HIGHER after ten cycles
           with the body +40 mV / +46 holes; grounded body 0.0014 (0.036). RH 4.42, RI 11.88: as with the axis contact, the steady leak only.
  `fin5` = 0.72 / 1.12 / 0.10 / 0.42 / 1.46 / 4.42 / 11.88 (`fin3`: 0.73 / 0.93 / 0.02 / 0.48 / 1.48 / 4.39 / 11.88).
- Open after D: Case 5 at 200 ns (1.58 mV against "on the 1.1 V line") is not a matter of A and B. Left: the storage capacitor of the
  transient (the same 15 electrons are 0.68 mV on the text's 3.6 fF) or the way the tunnelling model treats the carrier densities at the
  storage-node corner (the paper says "Hurkx" and no more).
- Codex meanwhile (commits a93cfc6 21:34, 28a07b3 21:42): superseded outputs taken off the server (account 8100 -> 6956 MB), its fin3
  factorial (720 runs, at condition 50 of 144 at 21:40) at 16 workers, more between 00:00 and 07:00 through a queue that counts my runs.
- User, 23:2x: a complete eliU report once everything, Codex's experiment included, has finished; with the remaining problems, the
  improvement measures and their explanation.
- Picture `pic_vbl_hwl_1t1c_3ddram\gt2d_hurkx_ab_rounds30_31.png` (`tools/plot_hurkx_scan.py`); table `hurkx_ab_and_fin5_rounds30_31.txt`.

## 2026-10-07 (bq) user: "isn't the device of the authors' oxide-channel papers ours?" (Hsu .. Cho .. Yu, IMW 2025 = A02; TED 73(9) 2026 = A08) - the papers' own device is not (IWO channel, L 25 nm), but the cell frame is the same and the SILICON reference transistor of their Fig.2(c) IS our cell: round 29 reproduces its Id-Vg with nothing changed but the gate work function
- Read: both PDFs whole (A02 four pages, A08 seven; the user's copies in 저자의 논문). They propose an oxide-semiconductor (W-doped In2O3,
  IWO) access transistor in the horizontal 1T1C / vertical-BL cell; A08 adds dual-deck stacking and a multilevel cell. No floating-body
  effect, no row hammer in them: an n-type oxide channel has no p body, and the papers say its wide band gap suppresses band-to-band
  tunnelling and GIDL.
- Same frame as Cho's cell: A02 Fig.6(c),(d) = A08 Table I: channel thickness 10 nm, two gate oxides of 5 nm, two gates of 20 nm, isolation
  oxide 30 nm (Z pitch 90 nm), BL pitch 200 nm, BL / capacitor radius 50 nm (A08), average WL pitch 275 nm, capacitor dielectric 4 nm (EOT
  3 A), TiN / W 6 nm, 2WLtBL 175 nm, 2WLtC 375 nm; channel length 25 nm. Cho's Fig.5(a): the same numbers with Lg 100 nm and bodies of
  30 / 20 / 10 nm. Bank tables of both papers: memory-cell pitch 625 nm for the Si-based array, 550 nm for the IWO one (the 75 nm of
  channel length); V_DD 1.1 V, V_PP 1.8 V. Legend of Fig.1: the Si-based cell has "HKMG"; capacitor ZrOx with TiN. Cs = 4 fF, calculated
  for EOT 3 A (both). A02 text: the hold voltage of the silicon transistor is designed to be -0.5 V; Si needs L = 100 nm for its leakage.
- Fig.2(c), the same figure in both: measured IWO transistor against TCAD curves of a silicon dual-gate transistor "as shown in the
  inset"; the inset is the cell drawing of Cho's Fig.2 ((ai) noted that and took the width from it). L_Si 100 / 25 nm, W_Si 100 nm, t_Si
  10 nm, W_eff 200 nm, V_DS = 1 V (printed in the TED version), drain current in A/um, Vg -2 .. 2.5 V.
  Blue curve (L = 100 nm) read off the embedded image of A08 (`tools/gt_hsu_fig2c.py`, dict HSU; frame x 146 .. 917, y 420 .. 806 of the
  970 x 920 image: 0.036 decade and 0.006 V per pixel): Vg at 1e-9 / 1e-7 / 1e-5 A/um = -0.127 / -0.007 / +0.135 V, 60.2 mV/dec, minimum
  below 1e-16 A/um near -0.6 V, GIDL branch log10 I = -15.84 / -15.18 / -14.56 / -14.04 / -13.17 / -12.56 / -12.05 at -0.7 / -0.8 / -0.9 /
  -1.0 / -1.25 / -1.5 / -1.75 V, on-current -2.83 / -2.71 / -2.65 / -2.60 at 1.0 / 1.5 / 2.0 / 2.4 V.
- Round 29 (`run_d29.sh`, 21:03, 5 runs, gr_c3h / gr_c4h; Codex's state fetched (73e8c4c, its factorial at F3C045), registered and
  pushed, decks md5-equal PC / server, gate ALL PASS with both lines read; the structures were held against Cho's Fig.5(a)/(b) and the
  conditions against Fig.2(c) of the two papers). Decks = fin's Id-Vg decks with V_DS 1.0 V, Vg 2.5 -> -2.0 V and the gate work function
  4.3 eV [back-calculated from the thresholds above: Cho's Case 3 curve lies 0.43 V higher; Cho's cases have 4.7 / 5.0 eV].
    run      cell, Hurkx A          | Vg at 1e-9 / 1e-7 / 1e-5 minus the paper | slope | GIDL branch minus the paper, -0.7 .. -1.75 V | on-current minus the paper, 1.0 .. 2.4 V | minimum
    DdrI_c3  N_A 1e18, 1.7e21       | +0.033 / +0.033 / +0.024 V              | 60.2  | -0.09 -0.03 -0.02 -0.02 +0.09 +0.16 +0.14   | -0.02 -0.01 +0.01 +0.01                 | -16.62 at -0.56 V
    DdsI_c3  N_A 1e18, default      | the same                                | 60.2  | +0.21 +0.28 +0.29 +0.29 +0.40 +0.45 +0.42   | the same                                | -16.48 at -0.56 V
    DdrI_c4  N_A 1e16, 1.7e21       | -0.006 / -0.006 / -0.022 V              | 60.3  | (kink) -0.50 -0.44 -0.39 -0.21 -0.10 -0.10  | +0.13 +0.11 +0.11 +0.10                 | -16.18 at -0.73 V
    DdsI_c4  N_A 1e16, default      | the same                                | 60.3  | -0.31 -0.19 -0.12 -0.08 +0.10 +0.19 +0.17   | the same                                | -16.32 at -0.68 V
    DdtI_c4  1e16, 1.7e21, V_DS 1.1 | the same                                | 60.3  | +0.17 +0.22 +0.22 +0.23 +0.33 +0.36 +0.30   | +0.15 +0.13 +0.13 +0.12                 | -16.31 at -0.60 V
  The Case 3 cell (10 nm body, N_A 1e18, HfO2 5 nm) with the fitted Hurkx A is their silicon transistor: slope equal to 0.1 mV/dec,
  on-current within 0.02 decade from 1.0 to 2.4 V, GIDL branch within 0.16 decade over 1.05 V of gate voltage, minimum at -0.56 V
  (theirs near -0.6 V). Its thresholds sit 0.03 V high: their work function is about 4.27 eV. The 1e16 cell has the thresholds at 4.3 eV
  but not the on-current (+0.10 .. +0.13 decade) and not the branch.
- What this confirms, none of it fitted to this curve: (1) gate dielectric and transport of our cell (HfO2 5 nm was a fit to Cho's
  thresholds; here the slope and the on-current of an independent curve); (2) Hurkx A 1.7e21 (a fit to Cho's GIDL at -1 V with V_DS
  1.1 V): the default A lies 0.21 - 0.45 decade above their branch; (3) the width: Cho's amperes are the 2D current x 0.1 um; (4) V_DS
  of Cho's Fig.5(c) = 1.1 V and not 1.0 V, if both papers use one tunnelling model: 0.1 V of drain bias moves the branch by 0.4 - 0.7
  decade (dt against dr), so a Fig.5(c) taken at 1.0 V would have asked for an A 2.5 - 5 times larger, which would miss this curve.
- What it leaves open: the model's branch is a little steeper than theirs (residual -0.09 at -0.7 V, +0.14 at -1.75 V): a hint at a
  smaller Hurkx B, the direction Case 5 asks for ((bo)); at this reading accuracy no more than a hint. The papers say nothing on the
  body's hole charge, on impact ionization or on the storage node of a transient (their Cs = 4 fF is a calculated value for the sense
  margin). Not ours: L 25 nm, IWO, the hold voltage of -0.5 V (belongs to their work function).
- Picture: `pic_vbl_hwl_1t1c_3ddram\gt2d_hsu_fig2c_si_reference_round29.png` (`tools/plot_hsu_fig2c.py`, our curves and the read points,
  no crop of the paper). Table `hsu_fig2c_si_reference_round29.txt`. Report 9.20, shared analysis section 9.

## 2026-10-07 (bp) user: "you are confusing Fig.8(c) with the index of the chart" - Fig.8(c) taken apart element by element: nothing was read from the inset or the legend, but two of my "paper values" are not on the figure as values (Case 4 at 200 ns, Case 5), and the zoom's scale was 4 % off in (bo)
- The user's description, which is right: left graph = storage node of all three 10 nm cases on the full scale (0 .. 1.1 V), all at 1.1 V
  and a little lower with time; right graph = the on-current bars as an inset, and outside the inset the fall of the storage node with
  the BL pulses for N_A 1e16 and 1e18. No new runs.
- What every element is (embedded image img08, 1029 x 737):
  * left graph: 0 V = rows 672 - 673, 5.6 mV per row. A blue line on rows 478 - 479 over the whole time (no slope at this resolution;
    1.1 V = row 477.8), red (and magenta) two rows under it from 30 ns on; red box rows 468 .. 493 = the range of the zoom. The legend
    (thick samples: black dashed "BL Pulse", red = N_A 1e18 WF 4.7 = case 3, magenta = N_A 1e16 WF 4.7 = case 4, blue = N_A 1e16 WF 5.0 =
    case 5) sits inside this graph. The three cases cannot be told apart in millivolts here.
  * right graph (zoom): plot area rows 441 .. 674 (1.1101 .. 1.0 V), a 2-row line on the 1.1 V level (rows 462 - 463), 0.4726 mV per
    row ((bo) had taken row 683, the row of the tick labels, as 1.0 V: 0.452). Red curve complete: 6 / 16 / 20.5 / 22.5 / 24.5 .. 30.6
    rows = 7.6 mV after the first low phase, 14.5 mV at 200 ns (target 7.1 / 14.6: stays). Magenta curve: 8.0 rows = 3.8 mV after the
    first low phase, 10.6 rows = 5.0 mV after the second, and it ENDS at x = 571 = 67 ns; nothing magenta after that, although the
    annotation text over that area is transparent (the dashed BL lines show through it). The line on the 1.1 V level is BLACK from
    19 ns to 120 ns and BLUE from 121 ns to 200 ns, on the same two rows; why it is black first cannot be told from the picture (it is
    not the frame: the plot goes on above it; not the zoom arrow: that ends outside the graph; not the BL pulse: it is unbroken through
    the BL-low phases).
  * inset: on-current of cases 3 / 4 / 5 in arbitrary units (1.0 / 1.2 / 1.04, "3.9 %"). Legend of the right graph: three coloured
    squares. NOT used for any storage-node number. The "0 -> 1.0" of my tables was a loss in mV, not the inset's axis and not a voltage.
- So, of the numbers I had called "paper, Fig.8(c)":
    case 3: 7.1 mV / 14.6 mV          read off the red curve                                          a reading
    case 4: 3.5 mV, 5.0 mV at 63 ns   read off the magenta curve (it is drawn up to 67 ns)            a reading
    case 4: 7.0 mV at 200 ns          NOT on the figure: my extrapolation ((au): "then hidden; about 7")   not a reading
    case 5: 0 / 0.5 mV or less        the blue stretch of the 1.1 V line (121 - 200 ns) read as curve 5; left graph: blue at 1.1 V
                                      within one row = 5.6 mV                                         a reading that rests on that identification
  If the blue stretch is not curve 5, the paper shows case 5 only on the left graph, "1.1 V within 5.6 mV", and the model's 1.58 mV at
  200 ns could not be called a mismatch. Grounds for reading it as curve 5: blue is used for case 5 alone in the figure's data, the
  left graph has the blue curve on that level over the whole time, and the note on cases 4 and 5 (V_th0 larger with WF 5.0 eV) only
  says something if curve 5 is in the graph and does not fall. Asked the user to check on the PDF.
- Scoring: `paper_targets.FBE_LAST = {4: (2, 5.0)}`: Case 4 is scored at its last readable plateau (after the second BL-low phase,
  5.0 mV) in place of 200 ns (`score2d.py`, `gt_avg_tab.py`). L1 / L2 now: fin2 2.97 / 2.09, fin 0.85 / 1.44, `fin3` 0.48 / 1.48, fin3b
  0.69 / 1.66, fin3n 0.45 / 1.42, fin3bn 0.43 / 1.46 ((bo): 1.50 / 1.69 / 1.43 / 1.48). Case 4 after two low phases: `fin3` 5.24 mV,
  fin3n 5.01, fin3bn 5.58 (paper 5.0). The model's 200 ns values of Case 4 (10.1 / 9.5 / 11.0 mV) have nothing on the figure to be held
  against.
- Lesson: a target is a number that can be pointed at on the figure. Bounds and extrapolations get their own names in `paper_targets`
  (FBE_FLAT, FBE_LAST) and are said as such in every table.

## 2026-10-07 (bo) user: "why is the paper's Case 5 at 0 at the start, what differs from ours?" - in the model, too, Case 5 loses nothing to the floating body; its 0.13 -> 1.58 mV is tunnelling at the storage-node junction (13.6 pA). The paper's curve stays on the 1.1 V line: the 1.58 mV at 200 ns are NOT inside. Score target corrected
- No new runs. Tool: `gt_fbe_leak.py` (loss as electrons, pairs by tunnelling / impact ionization, holes in the body, rate of the loss inside
  the BL-low and inside the BL-high phases).
- Model, `fin3` (Ds2F), from t_A to 200 ns:
    case | loss [mV] = electrons | pairs: tunnelling / impact ion. | holes t_A -> 200 ns | rate BL low / BL high [uV/ns] = [pA]
    1    | 182.9  = 2496         |    7.1 / 310.3                  | 1579 -> 1139        | 1932 / 3.17 = 4222 / 6.9
    2    |  67.8  =  761         |    0.4 / 119.1                  | 1354 -> 1070        |  732 / 5.62 = 1317 / 10.1
    3    |  13.8  =  133         |  -12.8 /  23.9                  | 1294 -> 1011        |  145 / 6.23 =  224 / 9.6
    4    |  10.1  =   97         |   -7.7 /  17.6                  | 1118 ->  832        |  105 / 5.71 =  162 / 8.8
    5    |   1.577 =  15.2       |   14.0 /   1.8                  | 1335 -> 1351        | 8.82 / 8.78 = 13.6 / 13.6
  Case 5: the same rate with the BL low and with the BL high, the holes stay in the body (they grow by the 16 pairs), electrons lost =
  pairs made (15.2 against 15.8). That is the leak of the storage-node junction under the gate edge (band-to-band tunnelling with the
  WL at 0 V and the node at 1.1 V; (au): 3.44 MV/cm at that corner), not a floating-body loss. The same with the avalanche model off
  (DdlF_c5: 15.7 pairs, 1.577 mV), with 1134 / 1413 holes in the body (Dh1F_c5, DfinF_c5: 14.0 / 13.9 pairs), and in every case while the
  BL is high (6.9 - 10.1 pA in Cases 1 - 4; Case 5 has the most, as its GIDL branch in Fig.5(c) is the highest).
  The floating-body part of Case 5 is zero because its threshold is 0.30 V higher (Fig.5(c): 0.57 / 0.69 / 0.81 V against 0.27 / 0.39 /
  0.51 V of Case 4; paper 0.53 / 0.65 / 0.78 against 0.26 / 0.39 / 0.51). The paper's own label in Fig.8(c) says the same (V_th0 larger
  with WF 5.0 eV).
- Paper, zoom of Fig.8(c) read again from the embedded image (1.1 V = rows 462 - 463, 1.0 V = row 674: 0.47 mV per row; corrected in (bp), first written with
  0.452; check of the scale: Case 3 ends 14.5 mV down, Case 4 reaches 5.0 mV where its curve ends): the blue-tinted pixels of Case 5 sit ON the top frame
  row from 124 ns to 196 ns (their centre -0.12 .. +0.17 mV from that row in six bands of 20 columns; before 124 ns the tint cannot be
  told from the frame). So the paper's Case 5 is "on the 1.1 V line within one pixel row (0.47 mV)" over the whole 200 ns, not "0 -> 1.0
  mV": the 1.0 of `paper_targets.FBE_200[5]` was the upper bound of the first reading ((au): "within 1 mV").
- What follows: the 0.13 mV of the first low phase are below a pixel, there is no difference to explain. At 200 ns the model's 1.58 mV
  would lie 3.3 rows under that line: NOT what the paper shows. With the text's 3.6 fF the same 15 - 17 electrons are 0.68 - 0.74 mV
  (Db0F_c5: 0.738 mV), 1.6 rows. Bound from the figure: I <= C x 0.47 mV / 179 ns = 4.1 pA (1.54 fF) or 9.5 pA (3.6 fF); the model has
  13.6 pA. Two things the paper leaves open decide it: the storage capacitor of the transient (1.54 fF for the 10 nm bodies from the fit
  of the write curve, 3.6 fF in the text) and the size of the tunnelling leak in the hold state. The Hurkx A was fitted at Vg = -1 V of
  Fig.5(c), where the field is 0.91 MV/cm ((au)); the hold corner has 3.44 MV/cm, so the hold leak is an extrapolation and goes as
  exp(B x 8.1e-7 cm/V) against the fitted point. Estimate from those two fields, NOT run: B 2.25e7 -> 2.1e7 V/cm with A re-fitted (about
  3.5e20) would cut the hold leak by about 3. The same change makes the GIDL branch less steep, and the model's minimum current is 0.2 -
  0.9 decade under the paper's in all five cases (-17.1 .. -17.3 against -16.4 .. -16.9).
- Scoring corrected (my reading, not a new condition): `paper_targets.FBE_FLAT = {5: 0.5}`: a case whose curve stays on the 1.1 V line is
  scored linearly, loss / 0.5 mV, at both instants (`score2d.py`, `gt_avg_tab.py`; FBE_200[5] = 1.0 stays for the log plots). Scores L1 /
  L2 now: fin2 2.97 / 2.01 (was 2.97 / 1.44), fin 0.85 / 1.47 (0.84 / 0.51), `fin3` 0.48 / 1.50 (0.47 / 0.58), fin3b 0.69 / 1.69 (0.68 /
  0.98), fin3n 0.45 / 1.43 (0.44 / 0.37), fin3bn 0.43 / 1.48 (0.42 / 0.55). Cases 1 - 4 are unchanged; the whole rise of L2 is Case 5 at
  200 ns (1.58 / 0.5 = 3.2). "Every number of Fig.8 inside its tolerance" ((bk)) holds for 14 of the 15 numbers, not for this one.

## 2026-10-07 (bn) user: "run (가)" - the device set up with the driving force ElectricField and the BL contact at the pillar end (rounds 21 - 28): it does not carry Fig.5(c) and Fig.8. By-products: the contact position sets the gain of the parasitic BJT; without any avalanche model Fig.8 fits better
- Why: (bm) left the driving force coupled to the write curve (with ElectricField the text's 4.2 fF nearly fits Fig.4(a)) and the Fig.7
  candidate needing a BL contact at the pillar end, while `fin3` has the default driving force and the contact on the pillar axis. The user
  chose option (가) of the afternoon report: set the device up anew with both and see whether Fig.5(c), Fig.4(a) and Fig.8 come out.
- Code: structures gr_c1hb .. gr_c4hb (single cells with `Blc="bot"`; gr_c2hb drawn next to Fig.2 before use, scratch folder, has a crop
  of the paper figure), `CASEB`, cfg2d `wcase=` (write on another case), the write's `II=1` moved into the overridable dict. Older decks
  byte-identical (checked before each of the eight batches). Tools: `gt_write_tab.py` (write runs against Fig.4(a)), `gt_fbe_pairs.py`
  (pairs and body holes per BL period), `plot_ef_refit.py`, `score2d.py` (`COMPOSE` fin3b / fin3n / fin3bn, `AVGREAD` for the d-tags,
  run folder from GT_RUNS), `_q.sh why / cb`, share_pack.sh (table `electricfield_contact_avalanche_rounds21_28.txt`).
- Batches (each: Codex's state fetched first (its last commit 73e8c4c of 13:29; live: its fin3 factorial, nothing with ElectricField or the
  contact), registered and pushed, decks md5-equal PC / server, gate ALL PASS with every line read): run_d21.sh 16:45 (14 runs) |
  run_d22.sh 16:52 (15) | run_d23.sh 17:21 (16) | run_d24.sh 18:12 (4) | run_d25.sh 18:15 (10) | run_d26.sh 18:25 (10) | run_d27.sh
  18:35 (1) | run_d28.sh 18:45 (3): 73 runs. Paper re-read for them: Fig.2 (the BL is a pillar through the whole stack, no core drawn),
  Sec.III / Fig.4(a), Fig.5, Sec.VI / Fig.8.
- Fig.4(a) with ElectricField (Case 2 cell, end contact; node at 12 / 24 / 39 / 60 ps, paper 0.72 / 0.92 / 1.06 / 1.13 V): 4.2 fF 0.781 / 1.017 /
  1.103 / 1.138 (score 2.04), 5.04 fF 1.03, 5.67 fF 0.701 / 0.951 / 1.055 / 1.106 (0.72), 5.88 fF 0.79, 6.72 fF 1.58; Case 1 cell with its
  5.1 fF 1.28, Case 3 cell with 3.6 fF 2.39. Default driving force, 1.8 fF: 0.93 (axis), 0.94 (end). With ElectricField the write asks for
  1.35 x the text's capacitor (`fin3`: 0.43 x).
- Fig.5(c): with the ionization off the end contact changes nothing (d0: thresholds, 60.2 - 60.3 mV/dec, GIDL branch as fin, score 0.73).
  With ElectricField on there is no DC curve: the five gate ramps stop at Vg = 1.108 / 1.062 / 1.083 / 1.085 / 1.387 V (Case 5 higher by its
  work function), all with the BL still at 0 V (d1). As a sweep in time
  (Case 2, BL 1.1 V, 0 -> 1.8 V): 100 us 0.29 / 0.38 / 0.53 V at 1e-10 / 1e-8 / 1e-6 A, 44.2 mV/dec; 10 ms 0.24 / 0.38 / 0.53, 73.1 mV/dec; the
  current x 2.8 at 1 V, x 5.1 at 1.8 V (paper 0.33 / 0.44 / 0.57). Control with the ionization off: the DC curve at both sweep times (0.33 /
  0.45 / 0.58, 60.5 / 60.4 mV/dec). So the shift is the ionization's, and the curve then depends on the sweep time (the on-current charges
  the floating body). Case 1 with the model on does not reach its drain bias at all.
- Fig.8 with ElectricField (end contact; stand-in rate re-sized to the bars, x 0.75 / 0.816 / 0.908 / 0.936 / 0.919 of `fin3`'s: 1539 / 1339 /
  1290 / 1105 / 1321 holes, bars 558 / 446 / 366 / 320 / 368 against 555 / 445 / 365 / 320 / 368):
  * capacitors x 1.35 (de): Case 1 loses 404 mV in the first low phase (paper 55), then the run stalls; Case 2 12.0 - 12.7 mV in EVERY low
    phase, 113.5 mV at 200 ns (paper 29 -> 50); Case 3 2.07 -> 9.93 (7.1 -> 14.6); Case 4 1.49 -> 6.56 (3.5 -> 7.0); Case 5 0.18 -> 3.95 (0 -> 1.0).
  * capacitors of `fin3` (dd): Case 1 339 mV 5 ns after the fall; Case 2 44.2 -> 311.6; Case 3 6.2 -> 30.2; Case 4 4.65 -> 20.3; Case 5 0.56 -> 12.5.
  * why (`gt_fbe_pairs.py`, Case 2): default driving force: a BL-low phase makes 42, 21, 14 .. 5 pairs, the body goes 1355 -> 1070 holes over
    the nine phases, the loss per phase 23.0 -> 2.75 mV. ElectricField: every low phase makes 155 - 143 pairs (and 19 in each high phase), the body
    stays at 1347 -> 1341 holes and every phase costs the same. Case 1: 3557 pairs in the first low phase, body 1551 -> 1762 holes. The
    leakage current makes its own body charge again; a capacitor only scales the millivolts.
  VERDICT on (가): ElectricField cannot be the avalanche model of Fig.5(c) and Fig.8; it fits Fig.4(a) alone. It stays what (bm) left it:
  a candidate for Fig.7, the one figure for which the paper names an avalanche model.
- By-product 1, the contact position with `fin3`'s own models (dc = `fin3` on gr_c*hb, Id-Vg d0; `fin3b`): scores IV 0.73, W 0.94, BR 0.03,
  L1 0.68, L2 0.98 (`fin3`: 0.73 / 0.93 / 0.02 / 0.47 / 0.58). Case 1 91 -> 147 mV in the first low phase and 183 -> 326 mV at 200 ns, Case 2
  23.2 -> 27.7 and 67.8 -> 95.7; same charge (1578 against 1579 holes), same bars. My reading (no run isolates it): while the BL is low it
  is the emitter of the parasitic n-p-n; a contact 50 nm from the junction over the whole height takes the injected holes (short
  emitter), one at the pillar end does not, so the gain and with it the loss for the same body charge are larger. What the runs show:
  Case 1 loses about 1240 electrons from the node in the first low phase with the axis contact (91.1 mV x 2.19 fF) and about 2000 with
  the end contact (146.5 mV), for 382 / 381 holes that leave the body (net loss of the body + pairs made in the phase).
- By-product 2, the avalanche model itself (default driving force) in the FBE. With it off and the same stand-in rate the charge at t_A
  is 1298 / 1142 / 1142 / 992 / 1139 holes (with it 1579 / 1354 / 1294 / 1118 / 1335): the model had multiplied the stand-in's pairs during
  the hold by 1.13 - 1.22, and it makes 169 (Case 1) / 42 (Case 2) pairs in the first low phase. With it off and the rate raised x 1.23 /
  1.195 / 1.14 / 1.135 / 1.18 (1597 / 1366 / 1302 / 1126 / 1344 holes, bars 554 / 447 / 366 / 322 / 371):
  * axis contact (dl, `fin3n`): first low phase 60.9 / 18.6 / 4.36 / 3.37 / 0.13 mV, 200 ns 112.9 / 49.1 / 12.9 / 9.49 / 1.58 (paper 55 / 29 / 7.1 /
    3.5 / 0 and 100 / 50 / 14.6 / 7 / 1), Case 1 after phases 2 - 4 77 / 86 / 93 (paper 67 / 76 / 83): BR 0.06, L1 0.44, L2 0.37.
  * end contact (dm, `fin3bn`): 81.6 / 21.5 / 4.72 / 3.66 / 0.13 and 163.8 / 62.8 / 14.9 / 11.0 / 1.58: BR 0.07, L1 0.42, L2 0.55.
  * write with the model off: 1.8 fF 0.737 / 0.913 / 1.016 / 1.084 V, score 1.11 (end contact 1.12); 1.7 fF 1.05; 1.6 fF 1.12 (with the model 0.93).
  A device WITHOUT an avalanche model in Fig.4(a), 5(c), 8 therefore scores 0.73 / 1.11 / 0.06 / 0.44 / 0.37 (axis) or 0.73 / 1.12 / 0.07 / 0.42 /
  0.55 (pillar end) against `fin3`'s 0.73 / 0.93 / 0.02 / 0.47 / 0.58, and the driving force chosen for Fig.7 then touches no other figure:
  that is the paper's wording (avalanche model named for Fig.7 only). NOT adopted: "impact ionization on in the FBE" is a condition the
  user set on 2026-10-06. Both by-products go to the user as decisions; `fin3` is unchanged.
- Numerics: Dd8F_c1, Dd9F_c1, DdeF_c1, DddF_c1 stopped by hand (`gt_kill.sh -`, files kept) after the node had collapsed and the steps
  had gone to 1e-14 .. 1e-16 s; Dd1I_c1 .. c5 and Dd6I_c1 ended by themselves (exit 2). `run_state.py` calls the transient Id-Vg runs
  "stopped early (exit=0)" although they reach 1.8 V.
- Picture: `pic_vbl_hwl_1t1c_3ddram\gt2d_electricfield_contact_avalanche_rounds21_28.png` (six panels, `tools/plot_ef_refit.py`). Report:
  results folder, section 9.17. Shared repository: ANALYSIS 4.10, table above, 73 run folders.

## 2026-10-07 (bm) back-calculation of Fig.7, rounds 16 - 19: the holes of the victim come from the AGGRESSOR through the BL pillar (driving force ElectricField, BL contact at the end of the pillar); round 17: Fig.8 without stand-in
- Why: (bl) left one candidate for the 665.1 mV that Fig.7(e) shows after ONE aggressor pulse with the node still at 1.1 V: holes made by
  impact ionization in the aggressor that reach the victim. With the default driving force the aggressor makes 60 - 71 pairs per cycle and the
  BL contact of the section (pillar axis, 50 nm from the junctions, whole height) takes most of what enters the pillar. Two things the paper
  does not fix were varied (model choices and contact placement, no numbers from outside): the driving force of the avalanche model
  (`IIdf="ElectricField"`, a Sentaurus keyword; default GradQuasiFermi) and where / whether the BL contact takes holes.
- Code: `SNhv` (hole recombination velocity of the storage-node contacts, like `BLhv`), `Blc` ("axis" = as before, "bot" = BL contact at the
  bottom end of the pillar; template sde_gt_dvs.cmd), structures gr_zzb / gr_zzbg (zz with that contact, floating / grounded victim body),
  run names Rzbi_zz / Rzbg_zz in cfg2d (only when named in rhsel). Older decks byte-identical (checked four times); older structure files
  differ by the two Blc lines only (their meshes are not rebuilt). gr_zzb drawn next to Fig.2 before use (scratch folder, has a crop of the
  paper figure: not for the repository): regions and doping as gr_zz, "bl" at the bottom end.
  Tools: `gt_rh_pairs.py` (pairs per cycle, holes in both bodies, holes through each contact), `gt_rh_body.py`, `gt_rh_wave.py` (inside the
  cycles), `gt_rh_hist.py` (now also the grounded and bottom-contact runs), `_q.sh steps` (time steps of named runs), `_q.sh zb`.
- Batches (each: Codex's state read first, registered and pushed, decks md5-equal PC / server, gate ALL PASS with every line read):
  round 16 `run_d16.sh` 12:27, 12 runs, gr_yy / gr_zz / gr_zzg | round 17 `run_d17.sh` 12:48, 15 runs, gr_c1h .. gr_c4h |
  round 18 `run_d18.sh` 13:34, 5 runs, gr_yy / gr_zz / gr_zzb / gr_zzbg | round 19 `run_d19.sh` 14:19, 3 runs, gr_zz / gr_zzb.
  Paper re-read for them: Sec.V, Fig.6(b),(c), Fig.7(a) - (e) (round 16, 18, 19); Sec.VI, Fig.8, Fig.4(a) (round 17).
- Round 16 (Case 2 pair, B1, paper timing, no history, no stand-in; Z-Z' unless said; "holes" = into the victim's body):
  * g2, default driving force, BL contact takes no holes: 60 - 71 pairs per cycle as before; holes +52 (Z-Z') / +74 (Y-Y') in ten cycles;
    node as fin. Ionization off: unchanged to the digit (0.00144 mV per cycle). The contact alone does nothing: too few pairs.
  * g1, ElectricField, contacts as they were: 9500 - 10000 pairs in cycle 1, 3800 - 4100 per cycle after (x 60 - 150). Z-Z' (axis contact):
    holes +77, then +31 per cycle; node rises 0.021 mV per cycle, no loss in ten cycles. Y-Y' (contact at the top end, 40 nm from both
    junctions): holes +441, then +200 - 250 per cycle; node falls from cycle 3 on: 0.17 / 0.47 / 0.85 / 1.33 / 1.84 / 2.43 mV per cycle.
  * g3, both: holes +874 in cycle 1 (+664 within the first pulse), then +648 / +628 (Z-Z'); +1236, +830 (Y-Y'). Victim's gated-body average
    +208 -> +378 mV in the first pulse (+170 mV; centre +205; paper 665.1), +426 / +566 / +694 / +817 mV after cycles 1 - 4. Node: -0.49 /
    -4.0 / -7.0 mV per cycle (Z-Z'), -1.96 / -7.8 (Y-Y'); it falls mostly while the aggressor is HIGH (70 - 80 % of the loss: g8 cycle 4 -7.2 mV in the high phase,
    -2.9 in the low one; g9 cycle 7 -6.7 / -1.5), where Fig.7(a) draws flat low phases. Both stall in cycle 4 / 3 (below).
  * g4, both + R = 2e5: the same hole gain (+852 / +584 / +580 / +644), node -1.1 (rise) / +1.9 / +4.6 / +8.1 mV per cycle; gate jump +264 mV.
  * grounded victim body (paper 0.036 mV per cycle, node flat): g3 0.0101 mV per cycle (last five, a steady loss), g4 (R) 0.0133,
    g1 (axis contact) 0.0019, default driving force 0.00145. 4 holes in the body throughout. The grounded body is immune, as in Fig.7(c).
- Round 18:
  * g7, ElectricField, BL contact at the bottom end of the pillar (below the victim), OHMIC: holes +682 in cycle 1, then +448 / +423 / +439;
    only 118 - 235 holes per cycle leave through the BL contact. Gated-body average +159 -> +316 mV in the first pulse (+158 mV). Node +0.31
    (rise) / -1.05 / -2.6 / -4.2 mV per cycle. So the transfer does not need a contact that refuses holes: a contact where a pillar has it
    is enough. Grounded (g7 Rzbg): node 1.10001 / 1.10000 / 1.09999 after cycles 1 - 3.
  * g6 = g3 with the text's 4.2 fF on both cells: 18 070 pairs in cycle 1, holes +1319 within the first pulse, +1815 in cycle 1; gated-body
    average +190 -> +509 mV in the first pulse (+320 mV; centre +375; paper 665.1). Node -3.0 mV in cycle 1.
  * g5 = g3 with ErrRef(Electron) 1e12: identical to g3 to the digit and stalls at the same instant.
- The stall (g3, g4, g5 at about 3000 - 3300 holes in the victim; o2 right after the write): time steps of 1e-16 .. 1e-18 s. The Newton
  iteration oscillates on the electron density (3e12 .. 4.5e12 cm^-3) at the gate-oxide interface 10 nm inside the gate from the storage-node
  side, inside a hole accumulation layer of 1.5e20 cm^-3; the node moves 2 mV per 23 ps there, nothing runs away. A numerical matter of the
  ElectricField driving force in an accumulation layer. Stopped by hand (`gt_kill.sh -`), files kept: Dg3Rzi_zz, Dg3Ryi_yy, Dg4Rzi_zz,
  Dg5Rzi_zz, Dg5Ryi_yy, Do2F_c1 .. c4 (Do2F_c5 ended by itself, exit 2).
- Round 17, FBE of the five cases with the paper's waveform and NO stand-in (does the write's own ionization leave the charge of Fig.8?):
  * o1, ElectricField + BL contact takes no holes (storage-node contact ohmic, as the drawing has a metal electrode at the end of the N+
    source): holes at t_A 704 / 519 / 345 / 213 / 18 (needed for the bars 1579 / 1354 / 1294 / 1118 / 1335), gated-body average 0.25 ns after
    the fall +366 / +252 / +142 / +104 / +43 mV (bars 555 / 445 / 365 / 320 / 368), first-phase loss 0.24 / 0.12 / 0.08 / 0.07 / 0.10 mV.
  * o3, default driving force, both contacts closed for holes: 213 / 151 / 114 / 161 / 205 holes, +220 / +140 / +77 / +90 / +99 mV.
  * o2, ElectricField, both closed: 5349 / 4971 / 4109 / 3282 / 2293 holes right after the write (3 - 4 x the bars' charge), then the stall.
  VERDICT: the write's own ionization does leave hundreds of holes once the BL contact does not take them, but not the charge of Fig.8
  and not its pattern over the cases (Case 5: 18). Fig.8's charge lies between "the storage-node contact takes holes" and "it takes none";
  nothing fixes a value in between. The origin of the charge of Fig.8 stays open; `fin3` keeps it as a condition.
- What rounds 16, 18 say about Fig.7 (a back-calculated candidate, not the paper's statement): with the driving force ElectricField the
  aggressor makes 4000 - 18 000 pairs per cycle; its holes enter the N+ BL pillar (the aggressor's body is forward biased while its WL is
  high) and the victim's body - BL junction collects them: p (aggressor body) - N+ (pillar) - p (victim body). That gives, for the first
  time in this model, (1) a body rise of hundreds of mV within the first aggressor pulse with the node still at 1.1 V (158 - 320 mV; paper
  665), (2) nothing with ionization off, (3) a node that falls only while the aggressor is high and faster from pulse to pulse,
  (4) a grounded body that keeps 1.1 V with 0.010 - 0.013 mV per cycle (paper 0.036). Not matched: the size (first-pulse rise 1/2 - 1/4 of
  the paper's; node loss 4 - 8 mV per pulse where the paper has 30 - 120), the collapse itself (the runs stall first), and the directions:
  in this model Y-Y' is hit as well (with an end contact 1/2 - 1/3 as much as Z-Z'), in the paper Y-Y' does not change at all.
- Round 19 (numerics only: ErrRef(Electron) 1e17, which takes the oscillating density out of the convergence test): before the hammer and
  in cycles 1 - 4 the runs repeat their twins (g9 against g7: holes 857 / 1312 / 1723 / 2164 against 857 / 1305 / 1728 / 2167, node equal to
  0.05 mV; g8 against g3: holes 1220 / 1868 / 2493 against 1202 / 1850 / 2478, pairs in cycle 1 3 % lower) and they get past the instant where
  g3 / g5 stalled. g8 (BL contact takes no holes): node -0.55 / -4.1 / -7.0 / -10.1 mV per cycle, 3187 holes after cycle 4.
  g0 (BL contact at the bottom end, ohmic, 4.2 fF): 18 274 pairs in cycle 1, holes 1551 / 2292 / 2823 / 3320, node -0.94 / -3.05 / -3.11 / -3.26 mV
  per cycle: it levels off near 3.3 mV per cycle = 0.605 V / 180 cycles (the paper's node is at 0.58 V after seven pulses; with the model
  off the paper has 60.5k cycles, this model 0.00144 mV per cycle). They slow down again from cycle 5 on (steps of 1e-14 .. 1e-13 s);
  how far each got and which were stopped at the end of the session: see the last lines of this entry.
- Round 20 = `run_d20.sh`, 14:41, 7 runs (gate ALL PASS on gr_c1h .. gr_c4h, four lines read). Seen in the pair runs: with ElectricField
  the write of the cell is much faster, because its body fills with holes while the WL is high (the body effect lowers the threshold).
  Storage node at 12 / 24 / 39 / 60 ps after the WL edge (paper Fig.4(a): 0.72 / 0.92 / 1.06 / 1.13 V):
    default driving force, 1.8 fF (`fin3`, the fit)   0.743 / 0.921 / 1.025 / 1.093   (deviation +23 / +1 / -35 / -37 mV)
    default driving force, 4.2 fF (the text's value)   0.512 / 0.716 / 0.859 / 0.968   (-208 / -204 / -201 / -162 mV)
    ElectricField, 4.2 fF (Do4W_c2, Do5W_c2)           0.785 / 1.019 / 1.104 / 1.140   (+65 / +99 / +44 / +10 mV)
    ElectricField, 1.8 fF (pair runs g1, g7)           0.96 - 0.98 / 1.13 / 1.16 / 1.17
  So the 1.8 fF of `fin3` and the driving force are coupled: the text's 4.2 fF was 160 - 208 mV too slow with the default driving force
  and is 10 - 99 mV too fast with ElectricField. Neither is inside the 30 mV; which pair the paper has cannot be told from Fig.4(a) alone.
  FBE with ElectricField, the text's capacitors (5.1 / 4.2 / 3.6 fF), BL contact that takes no holes, no stand-in (o4): 479 / 354 / 216 /
  149 / 5 holes, gated-body average +307 / +206 / +107 / +86 / +39 mV, losses 0.05 mV: no Fig.8 either.
- End of the session, 15:50: the three runs of round 19 needed more than ten minutes per cycle and were stopped by hand after 5 - 7 cycles
  (files kept): g9 (bottom-end contact, 1.8 fF) node -0.31 (rise) / 1.08 / 2.52 / 4.25 / 6.15 / 7.61 / 8.18 mV per cycle, 3712 holes; g8 0.55 /
  4.14 / 7.04 / 10.07 / 11.22 mV per cycle, 3915 holes; g0 (4.2 fF) 0.94 / 3.05 / 3.11 / 3.26 / 3.14 mV per cycle, 3810 holes. The loss per cycle
  levels off (g0 at 3.1 - 3.3 mV, g9 near 8 - 9 mV, g8 near 11 - 12 mV): no collapse within the cycles computed. Also stopped earlier:
  Dg6Rzi_zz (cycle 2), Dg7Rzbi_zz (cycle 6, stalled). Nothing of mine runs on the server; quota 7.8 of 9.2 GB.
- Shared: register, status, analysis 4.9 / 5.4 - 5.7 / 7.2, tables (`row_hammer_history_round15.txt`, `row_hammer_pairs_and_body_round15.txt`,
  `row_hammer_aggressor_holes_rounds16_18.txt`, `fbe_and_write_no_standin_rounds17_20.txt`, `fbe_3d_new_reading_case2.txt`), 72 new run
  folders, pictures `gt2d_rh_history_round15.png`, `gt2d_rh_hole_transfer_rounds16_19.png` (`tools/_rh_tab.sh` on the server, then
  `tools/plot_rh_transfer.py <table>` on the PC). Report sections 9.13 - 9.16. Not updated: the comparison workbook.
- User (after the chat report): "report through eliu". eliU report file `results_vbl_hwl_1t1c_3ddram\GT_IRPS2026_현황보고_eliU_2026-10-07_오후.html`,
  built by `tools/make_eliu_report_1007.py` (page builder and text checks of `tools/make_eliu_report.py`, whose fixed texts are now in `TXT`;
  yesterday's report is still reproduced byte for byte): 260 sentences, 5.9 units per sentence, nine pictures `gt2d_eliu1007_01 .. 09`
  drawn from the run files of the shared copy, 25 numbers of the text asserted against those files. Found while checking and corrected in
  the analysis / status / register / report: the node falls MOSTLY in the aggressor-high phase (70 - 80 % of the loss), not only there;
  first-pulse body rise of g1 27 mV (Z-Z'), 120 mV (Y-Y'), g3 Y-Y' 252 mV.
- Not changed: `fin3` and its scores. ElectricField is not adopted for the device: with it the write is faster (round 20) and Fig.5(c) /
  Fig.8 / the scores have not been redone with it.

## 2026-10-07 (bl) round 15 (user: go on with option 3): row hammer with the history that charges the body; 3D confirmation of the new reading; Fig.7(c) read again; round 16 started
- User, 2026-10-07 ~09:50: "go on like this" on my recommendation of option 3 = put the history that gives Fig.8 its hole charge into the row
  hammer and see whether Fig.6(e) and Fig.7 come out with it (the only test of the origin hypothesis on a figure independent of Fig.8).
- Code: `tHold2` (hold at Vdd/2 before the hammer), `Idle` (aggressor WL stays at 0 V), `SNhold` also in the row-hammer deck (1: node held
  through the hold at Vdd; 2: also through the hold at Vdd/2, released 0.5 ns before the hammer); `ProbeX=1` on 2D pair structures records the
  average potential of the victim's body under its gate and the holes in the aggressor's body. Older decks byte-identical (11 checked, twice).
- Round 15 = `run_d15.sh`, 28 runs Dx1..Dx7 x (Ry_yy, Ryi_yy, Rz_zz, Rzi_zz), B1, no stand-in: x1 16.2 us at Vdd then Vdd/2 for 1 ns | x2 16.2 us
  at Vdd/2 | x3, x4 the same with R = 2e5 Ohm | x7 100 us at Vdd/2 | x5, x6 idle controls of x2, x7. Codex's state read before (commit 56023b0:
  its fin3 follow-up, FBE only). Paper re-read: Sec.V, Fig.6(b),(c): BL Vdd/2, victim WL 0 V, aggressor 0 <-> Vpp, ten pulses in 2 ns.
  Gate 09:58, ALL PASS on gr_yy and gr_zz (both lines read; `runs/run_d15.check`), 20 jobs, 09:58:56 - 11:55, all 28 complete.
- Result (`tools/gt_rh_hist.py -c`; loss of the node per cycle in mV, + = falls; paper Y-Y' 0.0535 off and on, Z-Z' 0.0100 off, 1.1 -> 0.58 V on):
  * state before the hammer: 1319 - 1360 holes, body centre +503 .. +513 mV (16.2 us); 2758 - 2763 holes, +826 mV (100 us);
  * Y-Y' off: fin 0.00144 | x1 .. x4 0.00115 = idle x5 0.00115 (attack - idle 0.0000) | x7: one upward shift of 0.0025 mV, then 0.00019 = idle x6;
  * Y-Y' on: fin 0.00034 | x1 .. x4 the node RISES 0.0026 per cycle (body +6.7 mV, +27 holes in ten cycles) | x7 rises 0.0064;
  * Z-Z' off: fin -0.029 at cycle 1, then +0.00144 | x1, x2 -0.029, then +0.00115 | x3, x4 (R) +0.098 at cycle 1 (gate jump +207 mV), then +0.0011
    (ten-cycle mean 0.0102, which happens to be the paper's number: one shift, no accumulation) | x7 -0.030, then +0.0002;
  * Z-Z' on: the same shifts, then +0.0005 (x1, x2), +0.0007 (x3, x4), -0.0009 (x7). No collapse (victim body +1 mV, +4 holes in ten cycles).
  The loss that is left is the tunnelling leak of the node junction (0.00115 mV per cycle = 11 pA at 1.8 fF); it FALLS as the body fills
  (0.00019 = 1.8 pA after 100 us). With the BL at Vdd/2 a charged body does nothing: the BL-side barrier is 0.55 V higher than in Fig.8.
  VERDICT: the history does not give Fig.6(e) or Fig.7. The origin hypothesis (charging over 16 us before t = 0) gets no support from a
  figure that is independent of Fig.8; it is not refuted by them either (a body charged like Fig.8's is inert under the hammer bias).
- From the device files (`tools/gt_rh_pairs.py`, `tools/gt_rh_body.py`): impact ionization makes 53 - 71 pairs per aggressor cycle, every cycle
  (the aggressor node is pulled to 0.34 V at each WL fall and recharged to 0.55 V: about 2400 electrons pass its channel per cycle). Of the
  holes 0.4 per cycle (Z-Z') / 3.3 (Y-Y') reach the victim's body, 10 - 12 leave through the BL contact, 18 - 23 through the aggressor's node
  contact. With R = 2e5 the victim body is lifted +32 mV at mid-pulse, +4.3 mV at the end of the first pulse (paper, model off: 2.4 mV).
- CORRECTION of (bc), from the figure image at 4 x: in Fig.7(c) the arrows "t = 0" and "t = t_A" end on the FIRST aggressor pulse (its start
  and its end, 0.09 ns), not at 0.45 ns. So the 665.1 mV of Fig.7(e) build up within the first aggressor pulse. The node stays at 1.1 V through
  pulses 1 and 2 and then falls only while the aggressor is HIGH (0.12 / 0.11 / 0.08 / 0.07 / 0.06 / 0.03 V per pulse), flat while it is low,
  and stops at 0.58 V. 1000 - 2000 holes in 94 ps with the node flat cannot come from the victim's own channel current or from its
  storage-node junction (either would cost the node 40 - 700 mV). What is left: holes made in the aggressor that reach the victim.
- 3D confirmation of the reading of (bk), Case 2 (`tools/gt3_fbe.py`, now with the gated-body average): E3S1_c2 (x 1.31, 1347 holes) average
  +456 / +433 mV (before the fall / 0.25 ns after), +5 ns 8.58, first phase 14.26, 200 ns 41.89 mV; E3S2_c2 (x 1.45, 1486 holes) +486 / +458,
  18.90, 27.55, 59.40 mV; 2D Ds2F_c2 +470 / +445, 13.89, 23.18, 67.76; paper 445, 23, 29, 50. E3S2_c2 alone is inside every tolerance (bar +13 mV,
  -0.09 / -0.02 / +0.07 decades); interpolated to the bar: 19.6 and 49.5 mV. The 3D cell needs about 10 % more holes for the same potential.
  The reading of (bk) holds in 3D; "before the fall" fails there too (11 mV in the first phase at the bar).
- Round 16 = `run_d16.sh`, 12 runs, started 12:27:12 (gate ALL PASS on gr_yy, gr_zz, gr_zzg, three lines read; `runs/run_d16.check`; Codex's
  state read at 6116f98: its fin3 factorial is FBE only; registered 0d298b4): can the aggressor's holes reach the victim? g1 avalanche driving
  force ElectricField (the write made 17 000 pairs with it instead of 600 - 900) | g2 BL contact that takes no holes (`BLhv=0`: the section
  puts the contact on the pillar axis, the array has it at the end of the pillar) | g3 both | g4 both with R = 2e5 Ohm. Z-Z', Y-Y', grounded.

## 2026-10-07 (bk) back-calculation, step 1: where and when Fig.8(a) reads the body potential (rounds 13, 14); fin3; bcvfet_tcad moved
- User (08:30): move bcvfet_tcad off the server; the authors cannot be asked, the open values have to be back-calculated; go on.
- bcvfet_tcad: my part (runs 4354 files, tools, preview, files at the top: 4484 files, 1919 MB) packed (`tools/arch_manifest.sh`, tar in /tmp),
  downloaded (C:\Users\LEEJINSEOK\bcvfet_tcad_server_archive\bcvfet_tcad_claude_part_2026-10-07.tgz, 1668285425 bytes, sha256 a59d0bb5..0f23),
  held against the server's md5 list file by file (4484 of 4484 equal, the archive's sha256 equal on both machines), then taken off the
  server with `tools/arch_remove.sh` (only the files of the list). Codex's two folders in it (codex_validation 1009 MB,
  codex_hurkx_fig1_20261004_014926 77 MB) were left; a note MOVED_2026-10-07.txt lies in the folder; a second copy of the archive is in /tmp
  on the server. Account 8719 -> 6880 MB. Codex's screen had been deferring runs for lack of quota (queue.log: DEFER quota); it went on by
  itself at 08:36.
- What the paper's own numbers say (no run): the current that the first-phase losses mean, I = Cs dV/dt over the first 5 ns (Cases 1, 2) or
  3 ns (Cases 3, 4), is 18.8 / 8.3 / 1.7 / 0.72 nA with the capacitors of the write curve (43.9 / 19.3 / 4.0 / 1.7 nA with the text's). The gate
  voltage at which Fig.5(c) carries that current: 0.488 / 0.436 / 0.374 / 0.316 V (0.512 / 0.459 / 0.396 / 0.340 V). The bars: 0.555 / 0.445 / 0.365 /
  0.320 V. For Cases 2 - 4 the two agree within 10 mV (write-curve capacitors): in the paper's data the body rise acts on the leak like the
  same rise of the gate voltage. Case 5: Fig.5(c) at 0.368 V carries 2e-13 A, no loss, as in Fig.8(c). In my runs the bar state of Case 2
  leaks 0.40 nA, the current of Fig.5(c) at 0.366 V: 76 mV short. The gap of (bg) again, now from the paper's figures alone.
- Fig.8(b) looked at again: the dot "t = t_A" sits on the first BL edge (centre at about 19 ns, radius 5 ns): before or after the fall
  cannot be told from the picture.
- `tools/gt_ta_scan.py` (existing runs Dh1F .. Dh4F): at the states with the paper's first-phase loss the potential under the gate read WITH
  THE BL LOW comes close to the bars (x = 85 nm, 5 ns after the fall: 536 / 449 / 378 / 313 mV); the centre point before the fall is 98 / 90 / 70 /
  43 mV high.
- Round 13 (`run_d13.sh`, 10 runs Dp1F / Dp2F_c1..5, gate 08:41 ALL PASS, complete 08:57): charge around the value that gives the first-phase
  loss (x 1.40, 1.50 / 1.32, 1.42 / 1.23, 1.33 / 1.14, 1.24 of the old bar charge; Case 5 x 1.00, 1.15); new probes `ProbeX` (the channel
  every 5 nm at mid-depth and 1 nm under a gate oxide; average, minimum, maximum of the potential over the body region; average over the
  body under the gate and under the BL-side spacer; manual p.176: Average(Region=..), Average(Window[..])). `tools/gt_where.py`: 912
  readings (place x quantity x instant x reference) held against the bars at the states with the paper's loss (x 1.44 / 1.35 / 1.27 / 1.17,
  1463 / 1398 / 1382 / 1121 holes). 22 are within 30 mV in Cases 1 - 4, all of them potentials under the gate read with the BL low. Of the
  readings one would write down as a definition [mV, deviation from the bars in brackets]:
    body-centre point, before the fall             650 / 531 / 435 / 360   (+95 / +86 / +70 / +40)      the reading used until now
    body-centre point, BL low + 5 ns               600 / 487 / 392 / 329   (+45 / +42 / +27 / +9)
    top of the barrier (lowest mid-depth potential between the junctions; at x = 97.5 nm with the BL low), + 5 ns   603 / 487 / 392 / 329
    average over the whole body region, before     607 / 528 / 455 / 399   (+52 / +83 / +90 / +79);   BL low + 5 ns   (-100 / -59 / -47 / -53)
    minimum in the body region, before             526 / 412 / 336 / 262   (-29 / -33 / -29 / -58)
    AVERAGE OVER THE BODY UNDER THE GATE, before   567 / 479 / 401 / 337   (+12 / +34 / +36 / +17)
                                  1 ns after       530 / 450 / 377 / 318   (-25 / +5 / +12 / -2)
    hole quasi-Fermi potential, any place          200 - 460 mV off
  One definition fits: the average electrostatic potential of the body under the gate, counted from the start of the transient (the
  body without holes), read at the first BL edge. Between "just before" and "just after" the fall it passes through the bars.
- Round 14 (`run_d14.sh`, 10 runs Ds1F / Ds2F_c1..5, gate 09:00 ALL PASS, complete 09:17): the charge sized to the bars with that reading,
  the losses left as predictions (`tools/gt_avg_tab.py`):
    s2 = read 0.25 ns after the fall: charge x 1.56 / 1.31 / 1.19 / 1.17 / 1.18 (1579 / 1354 / 1294 / 1118 / 1335 holes); bars -1 / 0 / -1 / +1 / +1 mV;
         first low phase 91.3 / 23.2 / 4.53 / 3.49 / 0.13 mV (+0.22 / -0.10 / -0.20 / 0.00 decades); 200 ns 182.9 / 67.8 / 13.8 / 10.1 / 1.58 mV (+0.26 / +0.13 /
         -0.02 / +0.16 / +0.20); 5 or 3 ns after the fall 63.9 / 13.9 / 2.71 / 2.12 mV (+0.17 / -0.22 / -0.27 / 0.00); Case 1 after phases 2 - 4 120 / 137 /
         149 (67 / 76 / 83); Case 4 after two phases 5.2 (5.2). Every number inside its tolerance (30 mV, 0.3 decades).
    s1 = read just before the fall: x 1.37 / 1.20 / 1.12 / 1.10 / 1.13 (1403 / 1245 / 1219 / 1051 / 1279 holes); first low phase 40.1 / 11.3 / 2.80 / 2.26 /
         0.13 mV (-0.14 / -0.41 / -0.40 / -0.19: Cases 2, 3 outside); 200 ns 121.7 / 45.9 / 10.8 / 8.05 / 1.58 mV (+0.09 / -0.04 / -0.13 / +0.06 / +0.20); Case 1
         after phases 2 - 4 62 / 77 / 88 (67 / 76 / 83).
  The first phase wants the later instant, the tail of Case 1 the earlier one: the reading belongs on the edge itself.
- `fin3` (tools/score2d.py: COMPOSE and AVGREAD) = DfinI, DfinW, Ds2F, DfinR*: Id-Vg 0.73, write 0.93, body rise 0.02, first-phase loss 0.47,
  loss at 200 ns 0.58, row hammer 4.39, row hammer with impact ionization 11.88 (fin2: 0.12 / 2.97 / 1.44; fin: 2.03 / 0.84 / 0.51).
  Fig.4(a), 5(c) and all of Fig.8 inside the reading error together for the first time. What it rests on: the definition of the body
  potential is back-calculated (about ten definitions tried, the paper names none), and the hole charge is still a condition (1100 - 1600
  holes, 0.18 - 0.25 fC, put in by the stand-in supply with the node held), now sized to Fig.8(a) with that definition. Picture
  `tools/plot_body_reading.py` -> `gt2d_body_reading_fin3.png`.
- Open after this step: where the charge comes from (own generation with the node held would need 20.6 / 16.2 / 19.6 / 18.7 / 14.6 us for
  these charges: no common time, Case 5 too fast); the row hammer (Fig.6(e), 7). 3D: E3S1_c2 / E3S2_c2 (x 1.31 / x 1.45, the average over
  the gated body recorded) started 09:19 after gt3_check (the same lines as at 01:29; mesh unchanged since 2026-10-06 17:28).

- User (09:40): Codex's two folders in ~/bcvfet_tcad stay where they are. Asked for a detailed explanation of the open question
  "where does the hole charge come from": given in the chat with a schematic (`tools/plot_hole_source.py` ->
  `gt2d_hole_source_problem.png`). Numbers put side by side for it: holes needed (fin3) 1579 / 1354 / 1294 / 1118 / 1335 = 8.5 - 12 nA
  if made in 21 ns; the model's generation in the hold 9 - 14 pA (about 1 / 900), its electrons 96 - 97 % into the storage node
  (Q / C for these charges: 111 - 133 mV). Share of the needed charge that each known process gives: own generation for 18 us with
  the node held 0.89 / 1.09 / 0.92 / 0.96 / 1.22; impact ionization x 7 at the WL switch-off 0.93 / 0.99 / 1.01 / 1.18 / 1.47 (rejected:
  Fig.7(c)); pairs made by impact ionization during the write 0.57 / 0.52 / 0.47 / 0.76 / 0.60, of which 0 - 123 holes stay.

## 2026-10-07 (bj) the check in 3D (unit cell g3_c2h, Case 2): the gap between the bars and the losses is not a matter of the 2D section
- Six runs, started 01:30 after the structure check of (bi), all exit 0: E3I_c2 21 min, E3K_c2 59 min, E3F_c2 / E3F125_c2 2 h 20 min each
  (a BL period of 21 ns in about 10 min; the 5 - 6 h told before were too many), E3W_c2, E3H_c2. 16 - 26 MB a run folder.
  Tools: `tools/gt3_fbe.py` (3D and 2D runs read the same way; holes of a 3D run = integral x 2e-12), `tools/gt_probes.py -k` now
  counts the holes of a 3D run rightly (it used the 2D factor: 20 times too few), picture `tools/plot_3d_fbe.py` ->
  `gt3_fbe_case2_vs_2d.png`, table `fbe_3d_unit_cell_case2.txt` in the share pack.
- The 3D device with the final values is the 2D device:
    Id-Vg (E3I_c2, GT_W=2): 0.33 / 0.45 / 0.58 V at 1e-10 / 1e-8 / 1e-6 A, 60.4 mV/dec, 10^-13.01 A at -1 V, 10^-3.63 A at 1.8 V
                            (2D DfinI_c2: 0.33 / 0.45 / 0.59, 60.3, -13.24, -3.67; paper 0.33 / 0.44 / 0.57)
    write (E3W_c2, 1.8 fF): 0.744 / 0.957 / 1.046 / 1.106 V at 24 / 39 / 54 / 75 ps, 1.074 V after the WL is off (2D 0.725 / 0.942 / 1.035 / 1.098, 1.076)
    hold without supply (E3H_c2): 32 holes at t_A, body +45 mV from the start, +2 mV within the 21 ns (2D DcsF_c2: 37 holes, +49 mV):
                            the 3D body does not fill by itself in 21 ns either.
    sizing (E3K_c2): the bar of 445 mV is passed with 1094 holes (2D 1056), body centre at +0.256 V (2D +0.255 V); the rate that
                            ends there is 1.886e26 (2D 1.808e26, 4 % less).
- FBE with the charge put in and the node held, then the waveform of Fig.8(b) [mV]:
                           holes  rise   +3 ns  +5 ns | low phase 1 .. 9                                              | 200 ns
    3D bar charge  E3F_c2     1038  +431   0.50   0.78 |  1.48  2.83  4.11  5.31  6.44  7.52  8.55  9.54 10.49 | 10.41
    2D bar charge  Dh1F_c2    1045  +442   0.71   1.12 |  2.16  4.16  6.05  7.83  9.51 11.12 12.66 14.13 15.54 | 15.46
    3D x 1.25      E3F125_c2  1287  +493   3.65   5.67 |  9.94 15.96 20.31 23.73 26.56 28.98 31.10 33.00 34.71 | 34.62
    2D x 1.25      Dh2F_c2    1295  +506   5.79   9.06 | 15.97 25.69 32.70 38.20 42.74 46.61 50.00 53.01 55.73 | 55.64
    paper Case 2                    445          23    | 29                                                    | 50
  The same charge lifts the 3D body 11 - 13 mV less, and the 3D losses are 0.68 (bar) and 0.62 (x 1.25) times the 2D ones in
  every phase. At the same body rise the 3D points lie on the 2D curve: 1.48 mV at 431 mV (2D curve 1.53), 9.94 mV at 493 mV
  (2D curve 10.6). E3F_c2 ran at the 2D rate; its rise is 14 mV under the bar, inside the 30 mV, so it was not run again at
  the sized rate.
- So in 3D too the bar state loses 1.5 mV in the first low phase where the paper shows 29 mV (a factor 20), and 10 mV at 200 ns
  where the paper shows 50. The 2D section is a faithful stand-in for the unit cell in this test; what separates Fig.8(a) from
  Fig.8(b), (c) is not the dimension of the model. Left as candidates: what the authors call the body potential and where they
  read it, their initial state, their capacitor in this test, the models of their deck. Questions for the authors.
- Disk: account 8360 of 9216 MB at 03:55, growing about 3 MB per minute with Codex's screen (its own guard stops new runs with
  less than 512 MiB free: about 05:50 at this pace). Said to the user; nothing of mine is running.

## 2026-10-07 (bi) round 12 (user: run it yourself, and 3D too): own generation with the node held, whole waveform; 3D check started
- User (01:35): the 20 runs written for Codex are run here; 3D now as well. The prompt for Codex is withdrawn (note at its head, both
  copies; register pushed before the start, commit 7df9f66).
- Code: `SNhold` (FBE, with SNset, no Gb: the node stays held at SNset through the hold and is released 0.5 ns before the first BL
  fall; long holds in log steps) and `ProbeT` (probes across the body thickness at the centre x: 1 nm inside both gate-oxide
  interfaces, 1/4 and 3/4) in params.py / make_runs.py; 11 older decks byte-identical, 2D and 3D. Configurations n1 .. n4 = hold
  15.2 / 18 / 20 / 22 us, B1, impact ionization at the default coefficients, then the waveform of Fig.8(b) (period 21 ns, 9 low
  phases). Decks read (Dn3F_c1: Cs 2.19 fF, node set at 0.13 ns and released at 19999.64 ns, first fall at 20000.14 ns, probes).
  Conditions held against the paper: structure and write as always; off the paper: the hold of 15 - 22 us and the held node (a
  preparation). Gate 01:28, ALL PASS on gr_c1h .. gr_c4h, every line read. `run_d12.sh`, 16 jobs, 20 runs complete at 02:00 (exit 0).
  Tools: `tools/gt_held.py` (tables A - E), `tools/plot_held.py` -> `gt2d_held_node_round12.png`.
- Result, Cases 1 / 2 / 3 / 4 / 5 (node 1.1000 V at t_A in every run):
    hold      holes                           body rise [mV]             first low phase [mV]               200 ns [mV]
    15.2 us   1227 / 1282 / 1020 / 916 / 1383     592 / 503 / 345 / 308 / 429    11.34 / 14.64 / 0.59 / 0.77 / 0.13     60.8 / 53.1 / 4.27 / 4.43 / 1.57
    18 us     1413 / 1478 / 1196 / 1076 / 1627    638 / 550 / 389 / 349 / 486    42.58 / 42.61 / 2.38 / 2.68 / 0.14     125.4 / 93.4 / 9.87 / 8.80 / 1.55
    20 us     1542 / 1610 / 1320 / 1188 / 1798    669 / 582 / 420 / 377 / 526    79.48 / 67.66 / 5.26 / 5.15 / 0.15     170.5 / 120.8 / 14.94 / 12.38 / 1.55
    22 us     1666 / 1737 / 1442 / 1299 / 1968    699 / 612 / 449 / 404 / 565    119.79 / 92.54 / 9.38 / 8.24 / 0.17    211.1 / 146.0 / 20.26 / 16.03 / 1.57
    paper                                     555 / 445 / 365 / 320 / 368    55 / 29 / 7.1 / 3.5 / 0               100 / 50 / 14.6 / 7 / 1
  The 15.2 us row repeats Codex's group 17 (11.49 / 14.95 / 0.59 / 0.77 / 0.13 mV, same holes and rises): two independent runs agree.
- Q1 (one hold for all cases?): the paper's first-phase loss needs a hold of 18.9 / 17.0 / 21.1 / 18.9 us (Cases 1 - 4). At ONE
  hold, 19.1 us, the four losses are 61.0 / 55.6 / 3.8 / 3.9 mV = 1.11 / 1.92 / 0.53 / 1.11 times the paper's, Case 5 0.15 mV: the
  largest deviation is 0.28 decades, inside the reading tolerance of 0.3. So the first-phase losses of all five cases do
  come out of one prepared state, barely.
- Q2 (the rest of the curve at 19.1 us): 200 ns 149.7 / 108.3 / 12.5 / 10.7 / 1.5 mV against 100 / 50 / 14.6 / 7 / 1 (1.5 / 2.2 / 0.86 / 1.5
  times; Case 2 outside the tolerance); Case 1 after phases 2 - 4 87 / 103 / 115 (67 / 76 / 83); 5 ns after the fall 38.9 / 40.1 (43 / 23),
  3 ns after it 1.4 / 1.6 (3.3 / 1.4); Case 4 after two phases 5.7 (5.2).
- Q3 (the bars at 19.1 us): body-centre rise 656 / 569 / 407 / 365 / 509 mV = 101 / 124 / 42 / 45 / 141 mV above the bars. None of the 24
  readings (four places along the channel, four more across the thickness, electrostatic and hole quasi-Fermi potential,
  from the start of the transient and from t = 0) is within 30 mV in all five cases. Nearest: the potential 1 nm from a gate
  oxide, from the start: 443 / 442 / 353 / 320 / 461 (-112 / -3 / -12 / 0 / +93): right for Cases 2 - 4, wrong for 1 and 5.
- Q4 (does it matter how the charge was made?): no. At the same body rise the stand-in states (Dh1F .. Dh4F) lose the same
  within 2 - 15 % through the whole curve (Case 1 at 638 mV: 42.6 / 39.0 mV in the first phase, 125.4 / 118.7 mV at 200 ns).
- Q5: in the last 21 ns of the hold the body rises 0.28 - 0.45 mV. A body charged at t = 0 has no rise to show in Fig.8(a).
- Reading: "charged at t = 0", made by the model's own generation with the node held, gives the five first-phase losses at
  one hold inside the tolerance - and at that state the bars are 42 - 141 mV too high, the 200 ns losses of the thick bodies
  1.5 - 2.2 times too large, and no place or reference of the body potential mends the bars. Fig.8(a) and Fig.8(b), (c) do not
  come out of one state in the 2D model. Not a reproduction.
- 3D check started 01:30 (user: now). g3_c2h unchanged since 2026-10-06 17:28; `gt3_check.sh` read line by line (53280 vertices,
  no errors; junctions 25.00 / 150.00 nm at z = 25 nm; silicon 0 .. 50 nm across the rows, model ends at 100 nm; word line not
  interrupted), top view drawn next to Fig.2 (`gt3_unit_top_vs_cho_fig2_check_2026-10-07.png`, pic folder, not for the repository).
  Four batches side by side, 8 threads each: `run_3d_k.sh` E3K_c2 (sizing of the supply), `run_3d_f1.sh` E3F_c2 (FBE at the 2D rate
  of the bar, 1.808e26), `run_3d_f2.sh` E3F125_c2 (x 1.25, new run), `run_3d_s.sh` E3I_c2, E3W_c2, E3H_c2 one after the other.
  The FBE runs start at the 2D rate without waiting for the sizing: their own body rise at t_A shows whether the bar is met;
  if it is off by more than 30 mV they are stopped and started again at the sized rate.
  E3I_c2 done (21 min): thresholds 0.33 / 0.45 / 0.58 V at 1e-10 / 1e-8 / 1e-6 A, 60.4 mV/dec, 10^-13.01 A at -1 V, 10^-3.63 A at 1.8 V
  (2D DfinI_c2 0.33 / 0.45 / 0.59, 60.3, -13.24, -3.67; paper 0.33 / 0.44 / 0.57). Read with `GT_W=2` (the 3D current is that of
  the half cell; with the 2D setting 0.1 it comes out 20 times too low: a reading matter, noticed and checked).
  Disk: a 3D unit-cell run folder is 16 MB; account 8011 of 9216 MB at 02:01.

## 2026-10-07 (bh) user decisions: Codex's 20 runs before its screen; 3D check after the screen
- User (01:10): (1) the 20 runs of the prompt go in front of Codex's queue (written into the prompt, both copies); (2) the 3D check
  is on: start it after Codex's screen of 720 has ended and the disk has been looked at. 3D is no longer paused for this check.
  Plan: gt3_check on g3_c2h and the top view first (rule 1), pull / register / push (rule 6); stage 1 E3K_c2 (sizing of the
  supply in 3D), E3H_c2 (write + 21 ns hold), E3W_c2, E3I_c2; stage 2 FBE of Case 2 at the sized rate x 1.0 and x 1.25, held
  against Dh1F_c2 / Dh2F_c2 and the paper's 29 mV. The pair runs E3X_xx / E3Xi_xx are not part of it.
- Measured for the time and disk estimate (server, 01:20): 2D FBE with 9 pulses 13 - 20 min (Dh1F_c3 / c1); 3D unit cell write
  30 min (V3Wp_c2), Id-Vg 21 min (V3I_c2); 3D pair row hammer 7 h 20 min (X3p_xx). A 3D unit-cell run folder is 16 MB (two
  field files of 7.7 MB), a pair run 32 - 33 MB: the '7 GB' of (aw) is not disk. Account 7829 of 9216 MB; this project 3137 MB
  (runs 2236, Codex 901), the dropped bcvfet_tcad 2923 MB. Codex's screen: 91 runs ended in 110 min (started 23:30).
  So the disk was no reason to wait with 3D (said so to the user; the order stays the user's).

## 2026-10-07 (bg) "the body is already charged at t = 0 of Fig.8" held against the paper's numbers; Codex's screen; prompt for the missing runs
- User: check whether the paper's numbers come out if t = 0 is a charged state; write the prompt for the missing runs, the user hands
  it to Codex. No run of mine was started (the user gives this line to Codex).
- Codex meanwhile (its commits ce037a9 .. 32f5e2a on main, server read at 00:35): a screen of 720 conditions
  (`codex_validation/factorial_conditions_20261006`, 8 at a time, 50 of 720 done at 00:33): Cases 1 - 5 x preparation (own
  generation, hold 21 ns / 15.2 us / 21 us; stand-in in the whole body / 25 nm at the BL side / 25 nm at the SN side, x 1 / 1.125 / 1.25)
  x node (free / held at 1.1 V up to 0.5 ns before the fall / put back to 1.1 V 10 ps before the fall) x impact ionization on / off
  x Cs (text / x 1.8 / 4.2). The BL period is the paper's 21 ns; every run ends at the end of the first BL-low phase. The run I
  named as missing (BL fall at 15.2 us) is its group 13 and is done:
    hold 15.2 us, node free:      rise 569 / 469 / 325 / 289 / 404 mV, node 1.027 / 1.004 / 1.006 / 1.015 / 0.971 V, first low 5.19 / 5.27 / 0.32 / 0.40 / 0.12 mV
    the same, node put back:      rise 571 / 471 / 326 / 290 / 405 mV, node 1.1 V,                                 first low 5.59 / 5.59 / 0.33 / 0.41 / 0.13 mV
    the same, node held at 1.1 V: rise 592 / 503 / 345 / 308 / 429 mV (holes 1228 / 1284 / 1020 / 916 / 1384),         first low 11.49 / 14.95 / 0.59 / 0.77 / 0.13 mV
  (its result files, not recomputed by me from the raw data). Paper: 555 / 445 / 365 / 320 / 368 mV and 55 / 29 / 7.1 / 3.5 / 0 mV.
- The check, with the runs that have the state "charged, node at 1.1 V" and the whole waveform: Dh1F .. Dh4F (stand-in charge
  x 1.0 / 1.25 / 1.5 / 2.0 of the bar charge). `tools/gt_charged_t0.py` (tables A - D; GT_CODEX = Codex's results folder for D),
  picture `tools/plot_charged_t0.py` -> `gt2d_charged_t0_check.png`.
  * The loss of the first low phase is one function of the body rise at t_A, whatever made the charge: Codex's states charged
    by the model's own generation lie on the curve of the stand-in states at the same rise (11.49 against 11.22, 14.95 / 14.73,
    5.19 / 5.21, 48.28 / 47.37 mV; thin bodies 0.59 / 0.64, 0.32 / 0.38, extrapolated), node at 1.1 V or at 0.93 - 1.03 V.
  * At the bars (x 1.0): first low phase 2.62 / 2.16 / 1.06 / 1.09 / 0.13 mV, 200 ns 20.3 / 15.5 / 6.2 / 5.4 / 1.6 (paper 55 / 29 / 7.1 / 3.5 / 0
    and 100 / 50 / 14.6 / 7 / 1): Case 5 fits, Cases 1 - 4 lose 21 / 13 / 6.7 / 3.2 times too little.
  * The state that gives the paper's first-phase loss (interpolated, Cases 1 - 4): body rise 653 / 535 / 435 / 363 mV = 98 / 90 / 70 /
    43 mV above the bar, charge x 1.45 / 1.37 / 1.28 / 1.19 (1473 / 1415 / 1385 / 1132 holes). There: loss 5 ns (Cases 3, 4: 3 ns) after
    the fall 34.8 / 18.4 / 3.2 / 1.5 mV (paper 43 / 23 / 3.3 / 1.4), Case 1 after low phases 2 - 4 79 / 95 / 107 (67 / 76 / 83), Case 4 after two
    phases 5.2 (5.2 at 63 ns), 200 ns 142 / 76 / 17.5 / 10.1 (100 / 50 / 14.6 / about 7). The other way round, the state with the paper's
    200 ns loss (rise 624 / 500 / 420 / 337 mV) has a first-phase loss of 27.9 / 13.5 / 5.1 / 1.8 mV.
  * No recorded reading of a body potential gives the bars at those states (four positions along the channel at mid-thickness,
    electrostatic and hole quasi-Fermi potential, counted from the start of the transient or from t = 0): best rms 48 mV
    (x = 85 nm, electrostatic, from the start: +43 / +57 / +57 / +27). Positions across the thickness were never recorded.
  * In the low phases the holes leave (x 1.5, Case 1: 1523 -> 1356 -> 1291 -> 1251 ..), the body falls (-42, -59, -69 mV) and the
    steps shrink (73.6, 27.5, 16.9, 12.2 mV); nothing is refilled in the 10.5 ns high phases. The paper's steps shrink faster
    (55, 12, 9, 7): at an equal first step the model's later steps are about twice the paper's.
  * Fig.8(a) by the paper's own words is the rise between two time stamps, t = 0 and t_A (Sec.VI), and its numbers are counted
    from the body without hole charge ((ax): bars + depleted potentials of this model = one end potential). A body that is
    charged already rises 0.25 - 0.36 mV in 21 ns (12 - 17 mV per us between 15.2 and 21 us). So "charged at t = 0", taken
    literally, leaves no rise for Fig.8(a); it needs the t = 0 of Fig.8(a) to be another, uncharged state than the t = 0 of the
    curves, which the paper does not say.
  * A body left alone until it saturates (100 us and more, node free) loses 221 / 126 / 28 / 23 / 4.6 mV in the first 10.5 ns: four
    times the paper's Case 1, Case 5 no longer immune. The paper's losses are near a state "about 20 us after the write" (own
    generation, node held: 19.9 / 17.7 / 22.1 / 19.8 us by my estimate at 13 mV per us from Codex's group 17; not run), a time nothing
    in the paper gives.
- Verdict: with a charged state at t = 0 the flat node, the order of the cases, Case 5, the early part of Cases 3, 4 and a
  staircase that saturates come out. Bars and losses do not come out of one state (43 - 98 mV apart), the later steps of the
  thick bodies are too large, and Fig.8(a) as the paper describes it is left without a rise. Not a reproduction.
- Missing for this check and asked of Codex (prompt `PROMPT_FOR_CODEX_charged_t0_2026-10-07.md` in the shared folder `claude/`
  and in the results folder; the user hands it over): own generation with the node held at 1.1 V for 15.2 / 18 / 20 / 22 us, then
  the whole waveform of Fig.8(b) (9 low phases), Cases 1 - 5, probes across the body thickness: 20 runs. Codex's screen stops
  after the first low phase. Mine to offer, the user's to decide: the same check in 3D (decks E3* wait).

## 2026-10-06 (bf) round 11: the FBE with the hold and the BL period stretched (21 us .. 21 ms), no stand-in generation (user: Codex does not run this)
- `run_d11.sh`, 20 runs Dz3F .. Dz6F_c1..5: hold before the first BL fall and BL period 21 us / 210 us / 2.1 ms / 21 ms, BL edges 0.5 ns,
  baseline B1, impact ionization at the default coefficients, node set to 1.1 V for 10 ps after the write and then free. Code:
  `Sched.log` (decade pieces, steps even in log time) for holds and BL phases longer than 1 us; `ft()` prints deck times with 13
  digits where 7 cannot hold them (a 0.5 ns edge at 21 ms); older decks byte-identical (8 checked). Conditions held against the
  paper (only the time scale leaves the printed axis of Fig.8(b)); gate 21:11, ALL PASS on gr_c1h .. gr_c4h, every line read;
  register entry pushed first. All 20 complete at 21:43 (32 min). Tools: `tools/gt_long_hold.py [-q] [-b] <runs>` (charging,
  bar crossing, loss per phase), `tools/gt_long_split.py` (first phase against the idle control; first 10.5 ns), picture
  `tools/plot_long_hold.py` -> `gt2d_long_hold_round11.png` (pic folder).
- Storage capacitor of the FBE decks, said exactly: `CSB[tbody] * k_cs` = the paper's 5.1 / 4.2 / 3.6 fF times 1.8 / 4.2 = 2.19 fF
  (Case 1), 1.80 fF (Case 2), 1.54 fF (Cases 3 - 5). "1.8 fF" in other entries is the 20 nm value. The charge sums below use these.
- How the body fills by itself (one curve, the same in all four scales up to their hold), Cases 1 / 2 / 3 / 4 / 5:
    after t = 0     holes in the body                  body rise [mV]               node change [mV]
    10 ns           103 / 36 / 9 / 3 / 1               174 / 48 / 6 / 2 / 0         -0.06 .. -0.09
    1 us            182 / 123 / 77 / 63 / 93           235 / 119 / 44 / 35 / 49     -5.6 / -7.6 / -6.8 / -6.2 / -9.4
    10 us           821 / 824 / 648 / 577 / 873        482 / 381 / 244 / 215 / 299  -50 / -68 / -64 / -58 / -88
    15.2 us         1136 / 1146 / 944 / 843 / 1280     567 / 467 / 324 / 288 / 402  -73 / -95 / -94 / -84 / -128
    21 us           1452 / 1454 / 1248 / 1117 / 1695   645 / 543 / 401 / 358 / 501  -94 / -121 / -124 / -112 / -170
    100 us on       2151 / 2000 / 1882 / 1745 / 2655   804 / 668 / 549 / 507 / 714  -143 / -167 / -187 / -174 / -265   (saturated)
    Fig.8(a), 21 ns                                    555 / 445 / 365 / 320 / 368  0 (flat up to t_A)
  The bar of Fig.8(a) is passed after 14.3 / 13.7 / 18.2 / 17.7 / 13.3 us with 1087 / 1055 / 1099 / 960 / 1130 holes in the body and
  the node 69 / 87 / 109 / 96 / 113 mV down. At one common hold, 15.2 us, the five rises lie closest to the bars: rms 30 mV, the
  order of the cases as in the paper (1 > 2 > 5 > 3 > 4). No stand-in; the one thing fitted is that time.
- The node pays: C dV of the node at the bar crossing = 943 / 979 / 1052 / 925 / 1093 electrons against 984 / 1019 / 1090 / 957 / 1129
  holes gained in the hold: 96 - 97 % in every case. Codex's integrals for Case 1 at 21 us say the same (holes +1349, node 0.2075 fC
  = 1295 electrons; pairs in all silicon: tunnelling 1229, impact ionization 126, so about 9 % of it is not GIDL). Mean rate
  to the bar 9 - 14 pA (8 nA would fill the body in 21 ns); I = C dV/dt between 10 and 21 us 8.7 / 8.8 / 8.4 / 7.6 / 11.5 pA = 4.0 / 4.9 /
  5.5 / 4.9 / 7.5 mV per us. A node of 1.5 - 2.2 fF cannot stay flat for microseconds at this current; over 21 ns it moves
  0.1 - 0.2 mV. The paper's node is flat. (An earlier draft of this entry used 1.8 fF for all cases and got 79 - 113 %: wrong.)
- First BL-low phase of the 21 us runs (10.5 us long) against the same span of the 21 ms runs, where the BL stays high (the
  same history: an idle control), [mV]:
    loss with the BL low    334.5 / 239.6 / 76.6 / 62.3 / 66.5
    loss with the BL high    28.5 /  30.4 / 39.8 / 37.2 / 57.6     (the generation going on)
    added by the BL low     305.9 / 209.2 / 36.8 / 25.1 /  8.9
    holes, start -> end     1452 -> 745, 1454 -> 716, 1248 -> 684, 1117 -> 524, 1695 -> 1709   (BL high: 1848 / 1795 / 1635 / 1479 / 2258)
  In Case 5 87 % of the loss in the stretched phase is the hold loss and the holes do not leave; in Cases 1, 2 the BL-low
  phase itself takes 0.2 - 0.3 V. What the BL adds keeps the paper's order (1 > 2 > 3 > 4 > 5).
- The length of the paper's phase (a reading Codex made first, docs/CODEX_ROUND11_CAUSE_AND_RECOVERY_2026-10-06.md at f26b62d; my
  tool gives the same numbers): loss in the first 10.5 ns after the first BL fall [mV]
    hold 21 ns (DcsF)     0.08 / 0.09 / 0.07 / 0.07 / 0.10     body 174 / 49 / 7 / 2 / 1 mV, node flat
    hold 21 us            46.5 / 35.0 / 3.3 / 3.4 / 0.13       body 645 / 543 / 401 / 358 / 501 mV (36 - 133 mV above the bars), node -94 .. -170 mV
    hold 210 us .. 21 ms  221 / 126 / 28 / 23 / 4.6            body 804 / 668 / 549 / 507 / 714 mV (saturated), node -143 .. -265 mV
    paper                 55 / 29 / 7.1 / 3.5 / 0              body 555 / 445 / 365 / 320 / 368 mV, node flat
  At 21 us the loss is 0.85 / 1.2 / 0.46 / 0.97 times the paper's (Case 5: 0.13 mV against 0). It is the trade-off of round 3
  again, now with the model's own generation: the bars fit at 15.2 us (the state of `fin2`, whose loss in 10.5 ns is 3 - 20
  times too small), the losses fit near 21 us (the state of `fin`: bars 53 - 68 mV high there, 36 - 133 mV here).
  Not run: the BL falling at 15.2 us (the loss at the hold where the bars fit). Codex is on this line now (below).
- Whole stretched phases, loss against the node at t_A, first phase -> after nine [mV]:
    21 us:  334 / 240 / 77 / 62 / 67  ->  489 / 447 / 403 / 389 / 362      (node at the end 0.52 - 0.60 V)
    210 us: 460 / 406 / 318 / 286 / 262  ->  518 / 481 / 437 / 443 / 350
    2.1 ms: 522 / 483 / 438 / 443 / 352  ->  590 / 555 / 512 / 521 / 414
    21 ms:  592 / 557 / 513 / 523 / 415  ->  662 / 633 / 604 / 705 / 474   (node at the end 0.22 - 0.36 V)
  Not to be held against the paper's 55 / 29 / 7.1 / 3.5 / 0 (10.5 ns phases); the cited papers show losses of this size in
  their ms phases ([4] Fig.5(b): 20 nm body about 1.0 -> 0.6 V after the first low phase, (be)). Case 4 at 21 ms goes on losing
  21 mV per period after the others have settled: 1.5 fA, read as the off-current of the lowest threshold (0.387 V), not
  looked into further. With the paper's 21 ns timing and no stand-in the same model loses 0.07 - 0.10 mV in the first phase,
  1.1 - 1.7 mV after nine.
- Reading: the frame of the cited papers (holes of the GIDL collect in the body while the BL is high) works in this model
  without any stand-in and gives the pattern of the five bars at one hold time. What does not fit Fig.8: the time (15 us
  against 21 ns), the node (down 73 - 128 mV at that time, flat in the paper), and bars and losses at one instant. The
  paper's body is charged without the node paying: a state that was set, a generation on the BL side, or a time axis that
  does not show the charging. Not decidable from the paper. `fin2` stays a condition.
- Codex (read 21:55, its commit f26b62d on main; read-only for me): analysed the 20 runs at 21:33 (11 complete then), same
  conclusion ("natural generation fills the body but the node discharges meanwhile"); runs `NG_c1_21us`, `NG_c2_21us` = my
  Dz3F Cases 1, 2 again with the body's electron density, tunnelling, impact ionization and SRH written out and four times
  finer steps, to the end of the first low phase; reran its two runs the quota broke (`RR_FS_c2_q1300` done and whole,
  `RR_CDR_id_i0_idle` running). I start nothing on this line while it runs.

## 2026-10-06 (be) reference [4] obtained and read; the time scale of the cited FBE tests; the conclusions of Sec.VI held against our runs
- User: get [4] and read it. Deng .. Liu, "Balancing Charge Loss and Carrier Mobility ...", IEEE TED 72(1) 2025, DOI
  10.1109/TED.2024.3493066, IEEE document 10752092; PDF 14.1 MB through the user's Chrome session (access by Sogang library),
  kept as `Desktop\서강대\반엘프\관련논문\R03_deng_ted2025.pdf`, entered in that folder's source list (md + json, SHA256). Read: text of
  Sec.I - VI, Table II and Fig.5 on the publisher's page.
  * Holes: "mostly generated from gate-induced drain leakage", they gather in the thicker, partially depleted body, which with the
    n-doped source / drain forms a parasitic n-p-n transistor; with the BL low the transistor of a cell holding "1" amplifies:
    loss current = (beta + 1) x I_GIDL (Fig.5(a)). A fully depleted thin body cannot take the holes up.
  * How the loss is computed: transient of a 1T1C cell, BL at 50 % duty, node evaluated at 64 ms (one refresh cycle), plate
    at 0.5 V. Fig.5(b): time axis 0 .. 0.12 s, BL period 20 ms, the node falls in steps in the BL-low phases (20 nm body: 1.0 ->
    0.6 V after the first low phase). Reference [3], Fig.6 (looked at again): the same test, 0 .. 120 ms, BL period 20 ms, node flat
    for the first 10 ms (BL high), then steps.
  * Models: density gradient (fitted to their Schroedinger-Poisson solver), band-to-band tunnelling, Auger, SRH, band-gap
    narrowing, interface traps 5e10 cm-2 eV-1; no impact ionization. Device (Table II): gate length 80 nm, gate oxide 5 nm SiO2,
    width 40 nm, S/D 1e20, LDD 1e17; off-current taken at V_G = -0.3 V; channel 5 - 20 nm. An LDD-like junction lowers the
    gate-to-drain field, the GIDL and with it the loss.
- What follows for Fig.8 of the IRPS paper: its two references run the BL-toggling test over 120 ms with a BL period of 20 ms,
  where GIDL has the time to fill the body; Fig.8(b) shows the same staircase with "Time [ns]" on the axis (first fall 21,
  period 21, window 200). Our model, as built, generates 14.7 pA at the storage-node junction right after the write (hold test of
  2026-10-05) and Codex's 2.1 us hold gains 180 holes (13.7 pA): at that rate the charge of the bars (1050 holes) takes about 12 us
  and 21 ns give 2 holes. A question for the authors (unit of the time axis of Fig.8, or how the body is charged in 21 ns), and a
  test that would follow the cited frame: the FBE without stand-in generation with hold and BL period stretched (21 us .. 21 ms).
  That is Codex's family (long holds): proposed to the user, not started.
- Correction to (bd): the comparison with the DC curve of Fig.5(c) does not bound the transient. Right after the WL switch-off
  the floating body is in deep depletion and the generation is far above the steady-state leakage (model: 14.7 pA against
  1e-17 A in the DC sweep). What stands is the transient number: 8 nA are needed for 1050 holes in 21 ns, the model gives 14.7 pA.
- User: do our runs also show the on-current rising a little when the doping is lowered or the gate work function raised, and
  the other conclusions of Sec.VI? On-current from the Id-Vg runs DfinI (Vd 1.1 V, width 0.1 um), relative to Case 3:
    Vg 1.79 V: Case 3 195.3 uA, Case 4 253.5 (x 1.298), Case 5 221.4 (x 1.134; x 0.873 against Case 4)
    Vg 1.5 V: x 1.359 / x 1.089;  1.2 V: x 1.510 / x 0.773;  1.0 V: x 1.748 / x 0.379.   Paper, inset of Fig.8(c) (bar heights 106 /
    128 / 111 px): x 1.21 / x 1.04 ("3.9 %"); Case 5 against Case 4 x 0.87.
  So: lower doping raises the on-current (ours +30 %, paper +21 %), the higher work function lowers it (ours -13 %, paper -13 %),
  both together leave a small gain (ours +13 % at Vpp, paper +3.9 %; in ours the sign depends on the gate voltage: below about
  1.4 V Case 5 is under Case 3). Thresholds at 1e-8 A: 0.426 / 0.387 / 0.687 V. Case 5 does not reach 1.1 V in the write
  (0.97 V at 60 ps, 0.995 V before the WL falls; Cases 3 / 4: 1.12 / 1.17 V): the on-current at Vpp hides that.
  Sec.VI, statement by statement (paper | ours): thicker body, larger body rise (555 / 445 / 365 mV | with the same 1050 holes in
  every case 545 / 440 / 351; with no charge put in 193 / 55 / 9: same direction; in fin2 the rise is a condition); larger rise,
  larger loss (200 ns: 100 / 50 / 14.6 | 20.3 / 15.5 / 6.2 mV: same direction, 2.4 - 5 times smaller); lower doping, Case 3 -> 4, less loss
  (14.6 -> 7, first phase 7.1 -> 3.5 | 6.2 -> 5.4, first phase 1.06 -> 1.09: weak, and at equal holes Case 4 loses more: 0.88 against
  0.30 mV); higher work function, Case 4 -> 5, a little more rise but the loss suppressed (320 -> 368 mV, 7 -> 1 | at equal holes 340
  -> 344 mV; loss 5.4 -> 1.6, first phase 1.09 -> 0.13: same). Not the same: the size of the doping effect.

## 2026-10-06 (bd) user: was the caption of Fig.8 looked at when the source of the holes of Fig.8(a) was sought? Read, not weighed - done now
- The caption of Fig.8 was among the text read this evening but was not used in the question. Looked at now:
  * Its item (a) speaks of model parameters and the design space and of the floating body effect "explored at different body
    thickness, doping concentration and gate work function" - nearly the sentence of the caption of Fig.5 - and does not say
    what the bars are, where the potential is read, or how the body gets its charge. Items (b), (c): sensitivity to thickness,
    doping and work function, and the on-current. Nothing on a generation model.
  * Fig.6(e) carries "Impact ionization model Off" and Fig.7(a), (c) "Impact ionization model On" in the panels and Fig.7's
    caption names the model; Fig.8 has no such word in caption or panels. The paper does not say that Fig.8 has it on.
  * A second reading of item (a) cannot be excluded from the caption alone: that the panel's content is counted among the
    "model parameters", i.e. a state that was set. The text of Sec.VI speaks against it ("rise in body potential over time ...
    at each time stamp", as in Fig.7(e), whose three values are results).
- Where the paper does speak of the origin of the holes (not seen before; Sec.I): holes "generated under a strong electric field"
  accumulate in the body, with its references [3], [4]; and the work "applies the classical body effect as framework" (hence the
  V_th(V_SB) formula under Fig.8(a)). Reference [3] (Khan .. Pakala, TED 71(12) 2024; `Desktop\서강대\반엘프\관련논문\R01`): with the storage
  node and the BL high and the WL off, holes generated by GIDL move into the body and raise its potential; the BL going low
  then lowers the barrier. Its models: density gradient, high-field saturation, thin-layer mobility, Hurkx band-to-band
  tunnelling; no impact ionization. Reference [4] (Deng .. Liu, TED 72(1) 2025) is not on the PC. The SISPAD 2025 paper in the
  same folder (R02, not one of the nine references): holes from band-to-band and trap-assisted tunnelling in the retention
  phase with the BL high. The authors' survey says the same (rule 5).
- Correction of my own wording: "the paper says impact ionization" for the holes was true of Fig.7 only. For Fig.8 the
  paper's frame is GIDL (Hurkx) in the hold, t = 0 -> t_A. The factor diagnosis of this evening therefore tested a mechanism the
  paper names for Fig.7, not for Fig.8 (its result stands: rejected, by the grounded body).
- The GIDL frame against the paper's own Fig.5(c): 1050 holes (0.17 fC) in 21 ns are 8 nA on average. The curves of Fig.5(c) have
  their minimum at 10^-16.4 .. 10^-17 A near Vg = -0.1 V, so the GIDL part at Vg = 0 V, Vd = 1.1 V is below 4e-17 A: eight orders
  short; even the GIDL branch at Vg = -1 V (10^-13.2 A) is five orders short. The model agrees with that (2 holes in 21 ns,
  NOTES (ax); raising the storage-node-side generation by 100 droops the node 36 - 60 mV, NOTES 2026-10-05). So neither caption nor text tells how the body rises 320 - 555 mV in 21 ns at WL = 0 V,
  and Fig.5(c) says GIDL cannot do it at that bias: a question for the authors (what happens between the end of Fig.4(a), WL at
  1.8 V, and t = 0 of Fig.8, WL at 0 V; what the state at t = 0 is; which model produces the rise).

## 2026-10-06 (bc) rounds 6 - 10: steps 2 - 5 finished; impact-ionization factor diagnosis; the paper's Fig.7 and Fig.8 read again
- Round 6 (reruns, clean). Step 2, Case 2, baseline B1 + bar charge: SiO2 spacer write 0.72 / 0.90 / 1.01 / 1.08 V, GIDL -13.37,
  FBE rise 444 mV, first loss 2.32, 200 ns 16.3 mV; HfO2 spacer 0.79 / 0.96 / 1.05 / 1.11 V, -12.81, 438, 1.84, 13.7; 50 nm pillar: write and
  thresholds the same, 442, 2.15, 13.8 (baseline 0.74 / 0.92 / 1.02 / 1.09 V, -13.24, 442, 2.16, 15.5). No score improves: Si3N4 and the
  100 nm pillar stay (and the 50 nm pillar of the 3D model is no difference). Lombardi mobility (Mob=1): thresholds the same, on-
  current 0.07 - 0.09 decade lower; the transients do not get past the WL rise (56 min at 15 ps), stopped.
  Step 4, row hammer with the body charged (ideal WL, impact ionization on): 1056 holes: Y-Y' node rises 0.0026 mV per cycle,
  Z-Z' loss 0.00065; 1970 holes: rises 0.0049, loss 0.00005. No collapse.
  Step 5, Y-Y': BL series resistor 10 kOhm 0.00144, with the aggressor node at 1.1 V 0.00144, WL resistor 2e5 0.00137 mV per cycle.
  R = 2e5 at 1.8 fF, settled gate: grounded body -0.4449 mV at cycle 1, -0.4542 after ten (4.2 fF: -0.1904 / -0.1962): the same
  charge, 0.80 aC; floating 0.37 - 0.39 aC (-0.2033 mV at 1.8 fF, -0.0929 at 4.2 fF). One shift in cycle 1 in every deck.
  DtcRz_zz (and DtcRzi_zz, DycRy_yy) ran through the full-quota window: whole rows are missing (DtcRz_zz: the first aggressor
  pulse), the files look whole to `run_state.py`. Not rerun (Codex's R = 2e5 pairs cover the question); left out of the share.
  Step 3: x5 leaves 207 / 119 / 114 / 14 / 7 holes after the WL switch-off, x7 1462 / 1334 / 1302 / 1320 / 1969 (node -151 / -177 / -203 / -207 /
  -60 mV at the switch-off, body rise 651 / 516 / 416 / 409 / 566 mV, hold droop 0.10 - 0.18 mV); coarse mesh at x1: 100 / 36 (103 / 35).
- Round 7, FBE without the stand-in generation. x7: Case 3 first loss 9.53 mV, 200 ns 29.9 mV (paper 7.1 / 14.6); Case 5 0.17 / 1.60
  (0 / 1); Cases 1 and 2 latch when the BL reaches 0 V (node -576 / -635 mV within a nanosecond, solver crawling); Case 4 still
  at the switch-off. x6: Case 2 753 holes, rise 362 mV, 0.38 / 3.83 mV; Case 4 no avalanche (18 holes); Case 5 1086 holes, 355 mV,
  0.12 / 1.60 mV; Cases 1, 3 crawl at the switch-off. So the factor at which the switch-off avalanches differs from case to case
  (5 already at x6, 2 partly, 4 not), the charge it leaves is not that of the bars, and above it the thick bodies latch.
- Round 9, final configuration with the coefficients x4 / x5: the stand-in generation is itself multiplied (holes at t_A 1630 /
  1736 / 1630 / 1405 / 1970 at x4, 1861 / 2062 / 1890 / 1603 / 2372 at x5, against 1058 / 1045 / 1091 / 957 / 1134), so these are no runs at the
  bar charge. At equal hole number against the charge series h1 .. h4: Case 3 x 1.6 (x4), x 3.0 (x5), x 2.1 (x7); Case 4 x 1.5, x 2.2;
  Cases 1 and 2 latch (x4, 1630 / 1736 holes: -565 / -517 mV in the first low phase). The first-phase loss depends strongly on the
  coefficients; to bring the bar charge to the paper's 55 / 29 / 7.1 / 3.5 mV the loop gain would have to sit at 0.95 / 0.92 / 0.85 / 0.69
  in the four cases at once: not a robust way to Fig.8.
- The paper read again for the models and for Fig.7 / Fig.8 (text by pdftotext, figure images carved from the PDF into the
  scratch folder, looked at, not kept):
  * Models named: "BTBT Hurkx model ... to evaluate the gate induced drain leakage"; "an avalanche model for impact ionization"
    is "incorporated" for Fig.7. No model name, no coefficients, no driving force. Whether Fig.8 has it on is not said.
  * Fig.7(b): in both configurations (grounded, floating) a resistor R sits between the victim gate node V_gate2 and the
    victim WL source (0 V); a capacitor between the aggressor gate V_gate1 and V_gate2, another between V_gate2 and V_body
    (grounded or left open). So R on the victim WL is the paper's, without a value; my reading of earlier days was right.
  * Fig.7(a) / (c): with the model on the node of Case 2 falls in steps, one per aggressor pulse, from about 0.45 ns (= t_A) on,
    and ends at 0.58 V; Fig.7(e): body rise between t = 0 and t_A: 2.4 mV (off, floating), 665.1 mV (on, floating), 1.8 mV (on,
    grounded). The body is charged during the first two aggressor cycles, not before the hammer.
  * Fig.8: t = 0 at the start of the plot, t_A at the first BL fall. The paper explains the loss by the threshold shift of the
    body effect (formula under Fig.8(a); gamma ~ sqrt(NA) / Cox in Fig.8(c)), not by a bipolar transistor.
  * Consequence for R: with R in the WL path the write of Fig.4(a) needs R x C_gate of a few ps (R below about 1e4 Ohm), and
    then the victim gate does not jump. One R cannot serve Fig.4(a) and Fig.7 in this lumped 2D model.
- Rounds 8 and 10: row hammer with the coefficients x7 / x9 (ideal WL) and x5 / x7 with R = 2e5 Ohm (the configuration Fig.7(b)
  draws), floating and grounded. The grounded-body cell cannot be written and cannot hold: node during the write 0.08 V (x5),
  -0.19 V (x7), -0.15 V (x7, ideal WL), -0.28 V (x9); set to 1.1 V it is back at 0.096 V / -0.27 V before the hammer (x5 / x7) and
  at 0.40 V after 10 ps (x9); the same deck with the default coefficients: 0.83 V in the write (body effect of the grounded
  body), 1.055 V before the hammer. With the body tied to 0 V nothing stops the avalanche: the N+ / p junction breaks down at
  1.1 V. The paper's grounded body keeps 1.1 V with the model on (Fig.7(c), 0.036 mV per cycle). So a factor of 5 or more is
  not the paper's model: the factor diagnosis is closed, nothing adopted. Floating with R: the WL falls slowly, no avalanche at
  the switch-off even at x7 (body -0.187 V before the hammer), cycle 1 at x5 -0.1996 mV (the usual shift); stopped after 1 - 2
  cycles. Floating with the ideal WL (u7, u9): 30 min at the switch-off avalanche without progress, stopped. All runs of mine
  stopped at 20:21 (`gt_kill.sh -`); only Codex's CDR_r2e5_i1_on is left on the server. Disk 7.3 GB after `gz_logs.sh`.
- The scorecard line of k7 (first loss 0.40) counts only the cases that finished (3 and 5); m1's write score is from a run
  that was stopped. Neither is a score of a configuration.
- Shared: branch `claude` of the GitHub repository, commits 81cf3ef (first share), b65b511, a0a2b89, 57cca0a (register entries
  before rounds 8 - 10), and the final one of today; `tools/share_pack.sh` packs tables, the 221 complete runs, the resistor scan,
  the YE Id-Vg runs and 12 stopped runs kept as evidence (33 MB). Report section 9 and the workbook are updated (the workbook
  is built with the virtual environment in the session scratch folder: the PC's Python has no openpyxl).
- State: 2D configuration fin2 as the user decided; what is left open in 2D has no open parameter of mine any more: the hole
  source, bars and first-phase loss together, row hammer. Next steps are the user's: 3D (E3 decks), merging the branch,
  Codex's reruns of the two runs the quota broke.

## 2026-10-06 (bb) shared GitHub repository with Codex; what Codex tested; the disk quota ran full; rounds 4 / 5 as far as they survived; rerun round 6
- User (18:1x): `https://github.com/leejinseok08/vblhwl-3d-dram` (private) holds what Codex checked. Share status, experiment
  data and analysis there and do not run conditions or experiments that are already tested or under test. My working copy:
  `C:\Users\LEEJINSEOK\vblhwl-3d-dram`, branch `claude`, everything of mine under `claude/` (Codex's files are not touched).
  `claude/EXPERIMENTS.md` is the register both sides read before a new run. Rule 6 in CLAUDE.md.
- Codex's experiments (its docs at commit 34ed948, snapshot 17:54; all 2D, Cs 1.8 / 2.19 fF, my decks as the base):
  * A1, 4 runs (Cases 1, 2 x 1050 / 1300 holes): time step after the BL edge 5 ps, plateau 50 ps. First loss changes by at
    most 0.059 mV, holes by 0.012 %. The numerics after the BL edge are not the cause of the small first loss.
  * A3, 4 runs (2 done at the snapshot): storage node set for 10 ps only, then free, same pair generation. Case 1: before
    the first BL fall the node is 30.9 mV (1050 holes) / 38.4 mV (1300 holes) lower, holes and body-centre potential the same
    (0.12 %, -0.9 mV); loss added by the first BL-low phase 2.51 / 17.85 mV (clamped: 2.61 / 18.92). So the stand-in generation
    takes charge from the storage node and the long clamp puts it back: the hole-charge condition is "body state + node reset",
    not a history. The 56 mV total at 1300 holes must not be read as the paper's 55 mV.
  * A2: the same uniform source read from a file equals the region constant (0.107 mV, 0.038 %); sources confined to 25 nm
    at the BL side / the storage-node side are prepared, their sizing and pulse runs not started.
  * Condition discrimination, 9 runs (5 done): R = 2e5 Ohm, impact ionization off, 50 cycles, write 1 ns and hold 1 ns each
    (gate node settled), 4.2 fF, with an idle control (aggressor off): attack - idle = 0.1001 mV after cycle 1, 0.1052 after
    10, 0.1050 after 50; slope of the last ten cycles -4.7e-6 mV per cycle. A one-time offset, no accumulation (my 4.2 fF
    runs: 0.0930 / 0.0987 mV over ten cycles). Long hold of 2.1 us, Case 1: holes 73 -> 253 with impact ionization, 174
    without; node -5.5 mV in the hold. Under way or waiting there: ideal-R idle control, R = 2e5 with impact ionization
    (attack / idle), Case 2 long hold, A3 Case 2, the A2 confined sources.
- Not run by me from now on (Codex has or is running them): free storage node during the generation, confined sources,
  microsecond holds, time-step checks, R = 2e5 attack / idle pairs over many cycles.
  Stopped as duplicates or as invalid by design (18:26 - 18:38, `gt_kill.sh -`, single runs, batches left alive): Drf / Dtf
  (30 cycles at 2e5: Codex's 50-cycle pair answers it), Drc / Drd / Dre and Dta / Dtb / Dtd (R scan: only needed for a refit, and R
  is not adopted), the row-hammer runs of ra (paper timing: the gate node behind 200 kOhm has not settled when the hammer starts).
- Disk quota. The account has 10 GB (soft 9216 MB). 18:14 - 18:27 it was full: 43 runs side by side, and every run writes
  its log twice (`<id>_log_des.log` and `<id>.out`, the same text: 3.0 of the 4.4 GB under runs/). What it did: 17 runs
  never started (stdout could not be opened), 5 died with exit 5, more than 20 lost 4 kB blocks in the middle of their
  plot files (the columns shift from there on: "last time" reads 0.55 or 1.1), three wrote no plot file at all and ended
  with exit 0, and the batch logs lost lines. Two processes had also been writing into DydRy_yy (rerun batch started while
  the first batch still had the run queued). Codex's runs on the same account were hit too: CDR_id_i0_idle lost a block
  from row 1088 on (last good time 8.35 ns of 12.4), FS_c2_q1300 ran without plot files (told to the user; not touched).
  Repair, nothing deleted: `tools/gz_logs.sh` gzips the logs and stdout captures of runs that are not running (2761 -> 371 MB
  here, 970 -> 156 MB in ~/bcvfet_tcad/runs; quota 10240 -> 7300 MB; `zcat -f` reads them). Against a repeat: the runner
  written by make_runs.py gzips both files when a run ends and takes a lock on the run folder (`flock`: a second process is
  refused with exit=99); `gt_start.sh` refuses a batch when less than 40 MB per run is free below the soft limit;
  `tools/run_state.py <batch>.sh ...` reads the state from the run folders (live process, last time against the deck's
  FinalTime, plot files whole) instead of the batch log; `gt_kill.sh - <run> ...` stops single runs.
- Rounds 4 / 5, what is whole (table `tools/gt_wl_off.py`, scorecard):
  * ra (R = 2e5 everywhere): write 0.07 / 0.22 / 0.51 / 0.88 V at 12 / 24 / 39 / 60 ps (score 18.85; the gate node needs 60 ps to
    reach 1.7 V); FBE at the bar charge: body rise 0.24, first-phase loss 2.10 / 1.87 / 0.99 / 1.07 / 0.13 mV, 200 ns 16.3 / 13.4 /
    5.6 / 5.0 / 1.3 mV (without R 2.62 / 2.16 / 1.06 / 1.09 / 0.13 and 20.3 / 15.5 / 6.2 / 5.4 / 1.6): a little less, no extra drop.
  * tc (R = 2e5, 1.8 fF, write 1 ns, hold 1 ns), Z-Z' with impact ionization after 7 cycles: -0.220 mV in all, 0.0039 mV
    per cycle over the last five (ideal WL 0.0013). The one-time shift is 2.2 times that of 4.2 fF (0.098 mV), as 4.2 / 1.8.
    At the Cs of the transient the ten-cycle mean would be 0.022, not the paper's 0.0100: the 2e5 was a fit at 4.2 fF.
  * Impact-ionization coefficients x k, write + WL off + 21 ns hold, no supply. Holes left after the WL switch-off, Cases
    1 - 5: x1 103 / 35 / 9 / 2 / 1; x2 140 / 56 / 21 / 4 / 1; x3 165 / 75 / 36 / 10 / 2; x4 185 / 91 / 50 / 8 / 4; x5 207 / . / 114 / . / .;
    x10 . / 2349 / 2199 / 2185 / . with the node falling 262 - 293 mV at the switch-off (71 - 76 mV by coupling alone) and the body
    rise 750 / 623 / 608 mV (paper 445 / 365 / 320). Pairs made during the WL fall: x5 105 (Case 3), x10 2364: between x5 and x10
    the ionization integral passes 1 at the storage-node-side gate edge and the body charges until the field is gone.
    x10 Cases 1 and 5 and x100 do not get past that instant (Newton fails for 35 - 60 min at 0.124 ns, x100 Case 2 at 9 ps
    into the write): stopped. No droop in the hold in any of them (0.07 - 0.20 mV in 21 ns).
  * Y-Y': aggressor node at 1.1 V (yc) 0.00144 mV per cycle over the last five of 8 cycles; BL series resistor 1 / 10 kOhm
    (ya, yb, 3 cycles before the files broke) 0.00144. The same as without (0.00144; paper 0.0535).
  * `rh_tab.py` now leaves out the aggressor pulse that belongs to the write (decks with SNa0).
- Correction to (az) and to the report: the landing of the node after the WL switch-off (1.168 V in, 1.10 V at the start of
  Fig.8) is no second, independent sign for 1.8 fF. What happens at the switch-off is itself open (coupling alone, or pairs
  made there), and the paper does not show the node between Fig.4(a) and the start of Fig.8. The 1.8 fF rests on the charge
  balance of the write curve alone.
- Round 6 = `run_d6.sh`, 31 runs: everything of steps 2 - 5 that never ran or broke (sx / sh / bw / m1 I, W, F; j5 Cases 2, 4, 5;
  j7 all five; q5; ha, hc; yb, yd; tc Ry, Ryi, Rzg). Deck conditions held against the paper once more (Fig.5(a)/(b) device
  values, write 1.168 V / 105 ps, FBE 21.0 / 21.0 ns / 0.5 ns / 9 phases, hammer 0.094 ns x 10; tc with write and hold of 1 ns on
  purpose). Gate 18:39, ALL PASS on gm_sphk, gm_spox, gq5_c1h, gq5_c2h, gr_c1h .. gr_c4h, gr_yy, gr_zz, gr_zzg, gw_c2h (every
  line read; `runs/run_d6.check`); 24 jobs.

## 2026-10-06 (ba) user decisions; round 4 (steps 2 - 5 and the 200 kOhm question); 3D rebuilt and held against the paper's pictures
- User: (1) the hole charge stays a condition and is sized to Fig.8(a) (not to the loss curves): GBQ, about 1050 holes;
  the row-hammer WL resistor 200 kOhm: find out what trouble it makes, use it if none; rebuild 3D from the improvements and
  do the picture check against the paper. (2) Go on with steps 2 - 6 of the remaining 2D work. Asked for the total time:
  told 4 - 5 hours.
- Code: `Gb` now also in the row-hammer deck (supply during the hold with the BL at Vdd, 3 ns hold); `Rbl` (BL series
  resistor), `SNa0` (aggressor node at the start), impact-ionization factor in the parameter file (`cal_par(.., ii=)`),
  `cfg2d(cases=, wst=, rhsel=, iv=)`; structure gw_c2h (50 nm pillar); `gt_precheck.sh` takes the junction positions from the
  pillar width in the structure file (50 nm pillar: 25.00 / 150.00 nm). Earlier decks unchanged (checked).
- Round 4 = `run_d4.sh`, 49 runs, gate passed 17:25 (ALL PASS on gr_c1h .. gr_c4h, gr_yy, gr_zz, gr_zzg and the three variant
  meshes rebuilt today: gm_spox, gm_sphk, gw_c2h; check in `runs/run_d4.check`). Baseline B2 = 1.8 fF + Agen 1.7e21 + GBQ.
  ra: 200 kOhm in write, FBE and row hammer | rc / rd / re: R 100 / 150 / 300 kOhm, Z-Z' at 1.8 fF | rf: 200 kOhm, 30 cycles |
  ha .. hd: row hammer with the body charged (1056 holes = 445 mV of Fig.8(a), 1970 holes = 665 mV of Fig.7(e); R 0 / 200 kOhm) |
  ya .. yd: Y-Y' with a BL series resistor 1 / 10 kOhm and the aggressor node at 1.1 V | i1 / i2: impact-ionization
  coefficients x 10 / x 100, write + 21 ns hold | sx / sh / bw / m1: SiO2 spacer, HfO2 spacer, 50 nm pillar, Lombardi mobility (Case 2).
  Left out of step 2: a graded junction. The paper gives one doping value per region, the template sets doping per region,
  and the gate checks abrupt junctions at fixed positions; a graded profile would be a departure from the paper, not an
  open assumption.
- 3D rebuilt (old meshes moved to `runs/_unused/struct3d_before_rebuild`, structure files regenerated, same template):
  `gt3_check.sh`, every line read. g3_c2h: 53280 vertices, no errors, junctions 25.00 / 150.00 nm at z = 25 nm (1e20 ->
  -1e18 -> 1e20), silicon row z = 0 .. 50 nm, model ends at 100 nm, WL not interrupted. g3x_c2h: 107404 vertices, no errors,
  junctions 25.00 / 150.00 nm at z = 25 and 175 nm, rows 0 .. 50 and 150 .. 200 nm, wall 100 nm, WL interrupted 90 .. 110 nm.
  Pictures next to Fig.2 (pic folder): `gt3_unit_top_vs_cho_fig2_rebuilt.png`, `gt3_rh_xx_top_vs_cho_fig2_rebuilt.png` (rows and
  walls 100 nm each, BL pillar only inside the row, WL running on over the wall, cut only in the X-X' model as the paper
  says), `gt3_row_section_xsec_vs_cho_fig2_rebuilt.png` (the row's section: BL | spacer with p body under it | gate | spacer
  with N+ under it, as in the single-cell drawing). One difference between our own models noted for the user: the 3D rows
  carry a 50 nm pillar (25 + 25 + 100 + 25 + L_CAP 100 = the WL pitch 275 of Fig.5(a)), the 2D section a 100 nm one (the
  proportions of the cross-section drawing); `bw` in round 4 shows whether that matters.
- 3D decks with the 2D values are generated and not started: E3I_c2, E3W_c2, E3H_c2 (write + 21 ns hold, no supply), E3K_c2
  (sizing), E3F_c2 (FBE, 2D rate), E3X_xx, E3Xi_xx (`run_3d_E3.sh`).

## 2026-10-06 (az) two questions of the user: why 4.2 fF does not give the write curve; does the loss curve belong in the 2D stage
- (1) Fig.4(a) against the text's 4.2 fF, Case 2 (`python tools/gt_write_cause.py <png>`; picture `gt2d_write_cs_cause.png`).
  * Charge balance, no model needed: 4.2 fF x 0.72 V in 12 ps = 252 uA on average. The largest current of Case 2 anywhere in
    Fig.5(c) is 229 uA (Vg 1.6 .. 1.75 V, Vd 1.1 V); held for the whole 12 ps it gives 0.66 V, and it cannot be held: the node
    is the source, Vgs = 1.8 V - V_SN falls as it charges.
  * Upper bounds with the full saturation current Id(Vg = 1.8 - V_SN) at every instant: with the highest paper curve
    (Cases 1 - 4) 15.0 / 22.5 / 33.2 / 44.6 ps for 0.72 / 0.92 / 1.06 / 1.13 V at 4.2 fF (paper 12 / 24 / 39 / 60): C <= 3.4 fF from the
    first point; with Case 2's own curve (the model's, which follows the paper's where that is visible) 19.4 / 32.9 / 57.3 /
    89.6 ps: C <= 2.6 - 3.1 fF.
  * The model (Vds shrinks from 1.17 V to 0, so the current is about half the saturation value: 53 / 22 / 12 uA at 0.72 / 0.92 /
    1.0 V against 146 / 78 / 56 in Id-Vg): 24.3 / 49.1 / 97.7 ps at 4.2 fF, 11.0 / 23.9 / 47.8 / 84.4 ps at 1.8 fF. Time scales with
    C (ratio 2.0 - 2.4 for 2.33), the current at a given V_SN is the same for both capacitors within 20 %: the transistor
    alone sets the speed. Over the first two points the model at 4.2 fF is a factor 2.0 - 2.1 slow.
  * What Fig.4(a) fixes is therefore Cs per device width, 18 - 20 fF/um. The same ratio follows from the WL switch-off (BL
    1.168 V in, 1.10 V at the start of Fig.8: 68 mV through the 0.07 fF gate-to-node coupling). Width 100 nm comes from
    BL pitch 200 - wall 100 nm (Fig.5(a)) and from the absolute current of Fig.5(c) (model on-current 192 - 211 uA against
    229 uA): Cs = 1.8 - 2.0 fF. The other ways out fail: Vpp would have to be about 3 V, the time axis off by a factor 2;
    the coupling kick of the WL edge is 30 mV.
  * So the text's 4.2 fF is the value calculated from the dimensions of Fig.5(a) for the sense margin (EOT 3.8 A = 90.9
    fF/um2, i.e. 0.046 um2), and the node of the paper's transient model carries about 1.8 fF (0.020 um2; two faces of
    L_CAP 100 nm x 100 nm give 1.82 fF - noted as a number, not as a proof of how the node was built).
  * Left over: the model's tail is slow even at 1.8 fF (1.02 / 1.09 V at 39 / 60 ps, paper 1.06 / 1.13). At low Vds the model
    conducts less than the paper's device. Candidate: the 25 nm ungated p region on the BL side (length read off the
    drawing of Fig.2); in the BL-low phase of the FBE that region is the source-side barrier, so it also enters the loss.
  * Checked afterwards on the Dh1F runs (body at the bar): that region is NOT the barrier in the BL-low phase. Potential under
    the BL-side spacer +0.272 / +0.277 / +0.288 / +0.314 / +0.170 V against +0.224 / +0.228 / +0.228 / +0.223 / -0.018 V at the
    body centre under the gate (Cases 1 - 5): the gated body is the barrier, 20 - 28 mV lower than at t_A because the BL
    went down. So the underlap can only matter for the write tail (BL as drain at low Vds), and that tail is inside the
    reading error (score 0.93); it is not a lever for the loss curve.
- (2) Is the 2D stage the place for the loss curve of Fig.8? What exists on the 3D unit cell g3_c2h (half row + half wall,
  55154 vertices): Id-Vg (0.33 / 0.45 / 0.58 V, 60.4 mV/dec, on-current log -4.13 / -3.63, with the half-cell factor 2; 2D
  0.33 / 0.45 / 0.59, 60.3, -4.15 / -3.67), write curve at 4.2 fF (0.511 / 0.713 / 0.858 / 0.968 V; 2D 0.512 / 0.716 / 0.859 /
  0.968), body-centre potential at the start (-0.1891 V; 2D -0.1905). No FBE run has ever been made in 3D.
  Assessment given to the user: as a check of the mechanism the 2D section is the right tool (one cell, the same section
  physics, 40 - 60 min a run against hours in 3D), and what was learned there stands (Fig.8(a) = one hole charge; order
  of the cases; saturating shape; Case 5). But the hole charge fitted to the loss curves (KQ 1.25) is not a 2D parameter
  to call fixed: the paper's curves are 3D results with an unknown hole source and a geometric capacitor; the 2D = 3D
  equality is shown for Id-Vg and the write only; the fit is exponentially sensitive (60 mV = a factor 10) and already
  cannot meet Fig.8(a) and Fig.8(b), (c) together. Reclassified as provisional (CLAUDE.md State). Proposed, waiting for the
  user's word because 3D is paused: on g3_c2h, Case 2, one sizing run (hold with the hole supply, about 40 min) and FBE runs
  at KQ 1.0 and 1.25 (about 5 - 6 h each), compared with DfinF_c2 / Dh1F_c2.

## 2026-10-06 (ay) 2D completion, rounds 2 and 3: the body's hole charge at t_A is the one open quantity of Fig.8; final 2D set started
- Gate before each batch (`runs/run_d2.check`, `run_d2f.check`, `run_d3.check`, `run_dfin.check`): ALL PASS on gr_c1h .. gr_c4h
  (and gr_yy, gr_zz, gr_zzg for the final set): Lg 100, Tox 5, Tg 20, dVOX 30, Tbody 30 / 20 / 10, 1e20, 1e18 / 1e16, spacers 25 nm,
  junctions 50.00 / 175.00 nm (yy: 25.00 / 150.00 / 250.00 / 375.00).
- How the body is charged in the decks (`Gb`): constant electron-hole pair generation in the body region between the write and
  1 ns before the first BL fall, storage node held at 1.1 V meanwhile and released 0.5 ns before the fall (Sentaurus: Optics(
  OpticalGeneration( Scaling=0 SetConstant( Value=0 ) TimeDependence( WaveTime=(..) WaveTLin=1e-10 ) ) ) device-wide, SetConstant(
  Value=G ) in Physics( Region="R.Ch_v" ); without Scaling=0 the DC start diverges, without a device-wide source sdevice stops).
  It is a stand-in: it sets the state at t_A, it says nothing about where the paper's holes come from.
- Round 2 (20 runs, body at the bar of Fig.8(a)): rises 553 / 441 / 363 / 318 / 366 mV (paper 555 / 445 / 365 / 320 / 368).
  Losses first BL-low phase / 200 ns [mV], paper 55 / 29 / 7.1 / 3.5 / 0 and 100 / 50 / 14.6 / 7 / 1:
  q0 (text Cs) 1.3 / 0.9 / 0.44 / 0.45 / 0.06 and 10.2 / 6.6 / 2.6 / - / 0.70; q1 (Cs 1.8 fF) 2.6 / 2.0 / 0.98 / 1.02 / 0.13 and
  19.8 / 14.4 / 5.8 / 5.1 / 1.6; qn (1050 holes in every case: bars 545 / 440 / 351 / 340 / 344, score 0.54) 1.0 / 0.9 / 0.3 / 0.9 / 0.06
  and 8.1 / 6.3 / 2.0 / 3.2 / 0.7; q3 (SRH lifetimes x 0.01): slightly less, no gain. Against b0 (0.5 - 0.8 mV in 200 ns, bars
  193 / 55 / 9 / 3 / 0): scores BR 12.0 -> 0.1, L1 6.6 -> 3.0, L2 5.1 -> 1.5 (q1). The order of the cases is the paper's, Case 5 is
  right, the later BL-low phases lose about what the paper's do (Case 2: 1.3 - 1.9 against 1 - 5 mV per phase, Case 3: 0.4 - 0.9
  against 0.9, Case 4: 0.3 - 0.8 against 0.4); the first phase is 3 - 20 times too small and the curve does not flatten.
  At the bar the body holds phi_p = 0.71 - 0.74 V (WF 4.7) and 0.49 V (WF 5.0) under the gate.
- WL fall time (f1 / f2 / f3, 15 runs): holes left in the body after the write 123 / 41 / 13 / 3 / 0 at 5 ps, 177 / 87 / 55 / 25 / 5 at
  1 ps, 200 / 141 / 98 / 63 / 11 at 0.1 ps, 258 / 159 / 122 / 78 / 28 at 0.01 ps (pairs made at the edge up to 600 - 800, most leave).
  About 1050 are needed in each case: a fast switch-off is not the source. Dropped.
- Round 3 (20 runs, baseline B1 = Cs 1.8 fF + Hurkx Agen 1.7e21, hole charge 1 / 1.25 / 1.5 / 2 x that of the bars):
  scores BR / L1 / L2: h1 0.12 / 2.97 / 1.44, h2 2.03 / 0.84 / 0.51, h3 4.05 / 1.09 / 1.05, h4 7.86 / 2.25 / 1.86.
  h2 (about 1300 holes, 0.21 fC), loss after each BL-low phase [mV] | at 200 ns, paper in brackets:
    Case 1: 18.9 32.6 43.4 52.3 59.9 66.5 72.3 77.5 82.3 | 82.1   (55 67 76 83 87 93 98 101 | 100)
    Case 2: 16.0 25.7 32.7 38.2 42.7 46.6 50.0 53.0 55.7 | 55.7   (29 34 38 40 43 45 46 49 | 50)
    Case 3: 6.4 9.2 11.1 12.4 13.5 14.5 15.3 16.0 16.6 | 16.6     (7.1 .. | 14.6)
    Case 4: 5.3 7.4 8.7 9.6 10.4 11.1 11.6 12.1 12.6 | 12.5       (3.5 .. | 7)
    Case 5: 0.14 .. 1.61 | 1.58                                   (0 .. | 1 or less)
  The curve now flattens as the paper's does: at this potential the body loses holes to the BL in each low phase (Case 3:
  1360 -> 1220 holes in the first one). Bars at this charge: 608 / 506 / 429 / 378 / 436 mV, 53 - 68 mV (10 - 18 %) above the paper's.
  The charge that fits the first-phase loss case by case is 1.45 / 1.37 / 1.28 / 1.19 x; one factor for all: 1.25 (L2) .. 1.3 (L1).
  ADOPTED: KQ = 1.25. Fig.8(a) and Fig.8(b), (c) cannot both be met by the hole charge: 60 mV of body potential are a factor 10
  in current. The loss curve is the unambiguous quantity (node voltage against time); where and how the paper reads "body
  potential" is not stated - only that the differences between its bars are those of the body centre of this model.
- R of Fig.7(b), morning scan read (Z-Z', text Cs, impact ionization off; total over 10 cycles, mean per cycle, last five,
  victim gate jump): 1e-4 Ohm +0.011 mV, -0.0011, +0.0007, 0 | 2e5: -0.099, +0.0099, +0.0024, +211 mV | 5e5: -0.61, +0.061,
  +0.0003, +229 | 2e6: -1.31, +0.131, +0.0026, +240 | 5e6: -1.44, +0.144, +0.037, +242. Paper 0.0100 mV per cycle: R = 2e5 Ohm
  if "per cycle" is the mean over the ten cycles (it is one shift in the first cycles, not a loss that repeats). Paper
  conditions (r2): floating 0.0093 (impact ionization on: 0.0098; paper: storage node falls to 0.58 V), grounded body with
  impact ionization 0.0196 (paper 0.036). Y-Y': 0.0007 at every R (the pillar screens the victim gate; paper 0.0535).
- Final 2D set `fin` started 12:59 (16 runs: Id-Vg x 5, write, FBE x 5 with KQ, row hammer x 5; all with B1). Result, scores
  IV 0.73 / W 0.93 / BR 2.03 / L1 0.84 / L2 0.51 / RH 4.4 / RI 11.9 (b0: 0.79 / 6.49 / 12.0 / 6.62 / 5.14 / 4.71 / 11.9):
  Id-Vg thresholds as before, GIDL -13.49 / -13.24 / -13.17 / -13.43 / -12.83; write 0.74 / 0.92 / 1.02 / 1.09 V; FBE = h2 to the digit;
  row hammer (ideal WL, 1.8 fF): Y-Y' +0.0014, Z-Z' +0.0014 mV per cycle over the last five (one upward shift of 0.02 mV at
  the start), with impact ionization Y-Y' +0.0003, Z-Z' +0.0013 (no collapse), grounded body +0.0015.
- Written for the user: report `Desktop\\서강대\\반엘프\\results_vbl_hwl_1t1c_3ddram\\GT_IRPS2026_2D_소자완성_보고_2026-10-06.md`, picture
  `pic_vbl_hwl_1t1c_3ddram\\gt2d_fbe_fig8_vs_cho.png` (`tools/plot_fbe2d.py fin h1 <png>`), workbook rebuilt (125 rows, new sheet
  "2D 완성 라운드"). Open for the user: keep the hole charge as a condition? fitted to the loss curves (1.25 x, now) or to the
  bars (1.0 x)? R = 2e5 Ohm for row hammer or the ideal WL? resume 3D with these values?
- Found at 13:55 and stopped at 13:57 (`gt_kill.sh`): X3Q_xx and X3Qi_xx (3D X-X', paper conditions, 8 threads each) had been
  running since 10:32. The upload / start call that the user interrupted in the morning had already started them on the
  server (its 2D batch `run_pc2d.sh` did not start: gr_zzg was missing and the gate refused); the stop of 10:35 named only the
  seven X3c / X3r runs. They ran without their check lines having been read and with the values from before the 2D rounds
  (4.2 fF, default Hurkx); 1 - 2 of 10 cycles done (+0.0009 / +0.0015 mV so far). Decks and partial files kept.
  Lesson: after an interrupted start call, list what runs on the server (`whats_running.sh`, not only `-s`) before going on.
- User (after the report): "where do we stand, as a report explained with /eli5 and pictures". First version: the eli5 skill's
  default (age 5, an analogy world without any technical word, the real terms only in a table at the end). User: "it is all
  analogy, I cannot tell what it means - keep the way of explaining, use the real terms." Second version, the one to use:
  `results_vbl_hwl_1t1c_3ddram\GT_IRPS2026_현황보고_쉬운설명_실제용어_2026-10-06.html` (one line -> basics -> a little more ->
  so what; short sentences; real terms, each with a one-line meaning; six pictures embedded = `pic_vbl_hwl_1t1c_3ddram\
  gt2d_status_01 .. 06_*.png`; a table of the numbers and a glossary at the end). Regenerate on the PC: `python
  tools/make_eli5_report.py` (asserts: no word of the analogy version, 10 space-separated units per sentence or fewer).
  The analogy version (`GT_IRPS2026_쉬운설명_현황보고_2026-10-06.html`, `gt2d_eli5_*.png`) is still in the folders, not removed.
  For next time: easy explanations of the user's own work keep the real terms (saved as a feedback memory).
- Ideas not run (each would need a value that no allowed source gives, so the user's word first): impact-ionization
  coefficients scaled up (the paper's body charges within one aggressor pulse in Fig.7(e)); a shorter BL-side underlap (the
  25 nm are read off the drawing of Fig.2; in the BL-low phase that region is the source-side barrier).

## 2026-10-06 (ax) 2D completion, round 1 and what Fig.8(a) is (user: finish the device in 2D first; design experiments, run, improve)
- User, 2026-10-06: "1. as the paper. 3. impact ionization on, initial state and body potential as the paper's conditions", then:
  complete the device at the 2D level from what is confirmed in 2D - experiments that fix the open parameters, simulations, an
  improvement process; and again: the structure match against the paper before every simulation. 3D is paused: the seven 3D
  runs of (aw) were stopped at 10:35 (`gt_kill.sh`, which now stops only the named batch); decks kept.
- Process (CLAUDE.md "2D completion process"): gate `gt_start.sh` (now also compares the dimensions written into the structure
  file with Fig.5(a)/(b) and keeps the check in `runs/<batch>.check`) -> configurations `cfg2d()` (one change each) -> scorecard
  `tools/score2d.py` against `tools/paper_targets.py` (rms of deviation / tolerance per figure) -> adopt / reject -> next round.
- Paper conditions in the decks (`PC`): write as Fig.4(a) (BL 1.168 V, WL high 15 .. 120 ps), then the storage node set to
  1.1 V for 10 ps and released (`SNset`: every curve of Fig.8(b), (c), 6(e), 7 starts at 1.1 V), FBE timing of Fig.8(b), impact
  ionization on in the FBE runs, row hammer with BL at Vdd/2 both without and with impact ionization.
- Round 1 (78 runs, `run_d1.sh`, gate passed 10:41 on gr_c1h .. gr_c4h, gr_yy, gr_zz, gr_zzg). Scores (IV / W / BR / L1 / L2 / RH / RI):
  b0 baseline 0.79 / 6.49 / 12.0 / 6.6 / 5.1 / 4.7 / 11.9. One change each:
  * cs (storage node 1.8 fF instead of the text's 4.2): W 6.49 -> 0.93 (0.74 / 0.92 / 1.02 / 1.09 V at 12 / 24 / 39 / 60 ps; paper
    0.72 / 0.92 / 1.06 / 1.13). ADOPTED for the transient node. Second, independent sign: with BL at 1.168 V the node ends at
    1.16 V and the WL switch-off takes 76 mV off (1.54 fF) -> 1.08 V, the paper's start value 1.1 V; with 3.6 fF it ends at 1.065.
  * a5 (Hurkx Agen 1.7e21, default 3.5e21): GIDL at -1 V -13.49 / -13.24 / -13.17 / -13.43 / -12.83 (paper -13.5 / -13.2 / -13.1 /
    -13.2 / -12.85; default -13.18 / -12.94 / -12.88 / -13.14 / -12.59). IV 0.79 -> 0.73. ADOPTED (both inside the reading error).
    ab (Agen 2.7e19, Bgen 1.875e7): 0.74, no gain over a5. The hold loss does not follow Agen (0.49 - 0.82 mV in 200 ns either way).
  * ep (impact ionization driven by Eparallel), e1 / e2 (BL edges 0.1 / 1 ns), w3 (WL high 300 ps): BR, L1, L2 unchanged. Kept as they are.
  * r2 (WL resistor 2e5 Ohm in the FBE runs): one drop of 7 - 11 mV at the first BL edge in every case, Case 5 included
    (paper: 55 / 29 / 7.1 / 3.5 / none). Not what Fig.8 shows; R stays a row-hammer parameter.
  * Row hammer b0: Y-Y' +0.0006, Z-Z' +0.0006 mV per cycle (last five), with impact ionization the same; nothing moves it.
- What Fig.8(a) is (probes of the b0 runs, `tools/gt_probes.py`): the body centre of this model stands at -0.2955 / -0.1905 /
  -0.1141 / -0.0746 / -0.3734 V at the start of the transient (depleted body, set by the gates). Paper's bars + these:
  +0.260 / +0.255 / +0.251 / +0.245 V for Cases 1 - 4 and -0.005 V for Case 5. The differences between the bars (110, 80, 45 mV)
  are the differences between the start potentials of this model (105, 76, 40 mV): the bars are "one end potential (0.25 V for
  WF 4.7, 0.0 V for WF 5.0) minus the potential of the depleted body". Consequences: (1) the paper's start potentials are those
  of this structure - a check of thickness, doping, gate dielectric and work function that was not asked for; (2) at t_A the
  paper's body holds hole charge (a depleted body cannot sit at one potential for 10 / 20 / 30 nm and 1e16 / 1e18); (3) the
  rise is counted from the depleted start (scorecard changed to that). No other probe or pair of instants gives the five
  numbers (potential under the BL-side spacer +673 / 623 / 586 / 586 / 584, hole quasi-Fermi potential 342 / 297 / 307 / 322 / 9).
- Sizing (`DqkF`, constant pair generation in the body with the storage node held, `Gb`): the bars are reached with 1084 / 1056 /
  1099 / 962 / 1138 holes in the body: ONE hole charge, about 1050 holes = 0.17 fC, within 8 % for all five cases.
  For comparison: impact ionization makes 894 / 709 / 609 / 851 / 802 pairs during the write in this model (text Cs), of
  which 123 / 41 / 13 / 3 / 0 holes are left when the WL is off (they leave to the storage-node side while the WL is high).
- Running (started 12:06 / 12:09, gate passed): round 2 = q0 (body charged to the bar, text Cs), q1 (Cs 1.8 fF), qn (1050 holes
  in every case), q3 (SRH lifetimes x 0.01): do the losses of Fig.8(b), (c) follow? And f1 / f2 / f3 (WL falls in 1 / 0.1 / 0.01 ps
  instead of 5): does a fast switch-off with impact ionization leave the hole charge behind?

## 2026-10-06 (aw) 3D X-X' row hammer: result; user decisions on R, the WL cut and impact ionization; next runs started
- X3p / X3pi / X3pg (3D pair, row hammer Case 3, impact ionization off / on, cut 40 nm; 6 h 15 - 26 min each, 7 GB):
  mean change per cycle over the last five cycles 0.00066 / 0.00067 / 0.00066 mV (paper 0.0060, with impact ionization
  0.0070), reversible swing with the aggressor WL high +0.116 / +0.116 / +0.126 mV. Counted the same way (`tools/rh_tab.py`),
  with the text Cs: Y-Y' 0.0006, Z-Z' 0.0007, X-X' 0.00066 mV per cycle against the paper's 0.0535 / 0.0100 / 0.0060: the
  same static leak (13 - 15 pA at the storage-node junction) in all three directions, no path that accumulates.
  Report for the user: `Desktop\서강대\반엘프\results_vbl_hwl_1t1c_3ddram\GT_IRPS2026_3D_결과보고_2026-10-06.md` (the user
  asked for the 3D results as a report file in the 반엘프 folder); workbook rebuilt (113 rows).
- The PC ran short of memory while a background ssh waiter sat idle and Claude Code stopped it: no background waiters on this
  PC; the batches run under nohup on the server and are read on request.
- User decisions (2026-10-06): (1) go on with R of Fig.7(b) as a fit parameter and take the ideal value 1e-4 Ohm too;
  (2) I pick the candidates for the WL cut; (3) compare impact ionization on / off for Fig.8 and choose.
  * (2) candidates: 10 nm (closest to the uncut WL of the top view that the mesh carries), 20 nm (= gate thickness, baseline),
    40 nm, 100 nm (= the whole wall: each WL over its own row only). Meshes g3x10_c2h / g3x100_c2h checked with gt3_check.sh
    (junctions 25.00 / 150.00 nm in both rows, rows 0 .. 50 and 150 .. 200 nm, WL interrupted 95 .. 105 and 50 .. 150 nm);
    pictures `gt3_rh_xx_cut10nm_top_vs_cho_fig2.png`, `gt3_rh_xx_cut100nm_top_vs_cho_fig2.png`.
  * (3) comparison (2D, default Hurkx, FB2; table in the report, section 7): hole quasi-Fermi potential at t_A minus the
    start potential: on 584 / 435 / 405 / 389 / 375 (mean deviation 31 mV, the paper's order 1 > 2 > 3 > 4), off 390 / 371 / 356 /
    368 / 374 (60 mV, no order); losses the same. Proposal to the user: impact ionization on for Fig.8, off for Fig.6(e),
    on for Fig.7 (the paper's own split). Waiting for the user's word.
- Started 09:38 / 09:43 (checks: gt_start.sh gate with gr_zz and gr_yy [25.00 / 150.00 / 250.00 / 375.00 nm], gt3_check lines read):
  2D QS (Z-Z', R 1e-4 / 2e5 / 5e5 / 2e6 / 5e6) and QY (Y-Y', R 1e-4 / 1e6 / 1e7); 3D X3c10 / X3c100 (ideal WL, cut 10 / 100 nm),
  X3rid (R 1e-4), X3r1e6 with the four cuts. First cycle so far: R 2e5 -0.088 mV, 5e5 -0.58 mV (victim gate jumps +211 / +229 mV);
  Y-Y': the victim gate does not move at any R (-0.2 mV): the pillar screens it, so R cannot give the paper's 0.0535 there.
  Read with `python3 tools/rh_tab.py <runs>` (or `bash tools/_q.sh`).

## 2026-10-06 (av) what the results suggested, run; 3D unit cell verified, X-X' pair built and started (user: improvements, then 3D)
- Checks before the runs: `gt_start.sh` gate on gr_c1h .. gr_c4h and gr_zz (junctions 50.00 / 175.00 nm, six heights in the pair).
  3D: `gt3_check.sh` on g3_c2h, g3x_c2h, g3x40_c2h, every line read: junctions 25.00 / 150.00 nm in the victim row (z = 25 nm)
  and in the aggressor row (z = 175 nm), silicon rows z = 0 .. 50 and 150 .. 200 nm, wall between, model ends at 200 nm = BL
  pitch (Fig.5(a): 200 = row 100 + wall 100), WL interrupted z = 90 .. 110 nm (40 nm variant 80 .. 120). Top view next to
  Fig.2: `pic_vbl_hwl_1t1c_3ddram\gt3_rh_xx_top_vs_cho_fig2.png`. Not in the paper: the width of the WL cut (the text only
  says the WL is "hypothetically decoupled"): 20 nm [ASM], a 40 nm variant runs beside it.
- 2D, default Hurkx model, FB2 timing (`gt_fbe_tab.py`), loss at 200 ns, Cases 1 - 5, paper 100 / 50 / 14.6 / 7 / 1 mV:
  * FW (WL high 105 ps only, impact ionization on): 0.37 / 0.55 / 0.51 / 0.51 / 0.60 mV; holes left by the write 123 / 41 / 13 /
    2.6 / 0.3 (300 ps write: 73 / 12 / 7 / 1.6 / 0.08).
  * FB_ / FBi_ (band-gap narrowing BennettWilson = Sentaurus default, Cases 1, 2): 0.15 / 0.20 mV with and without impact
    ionization (the generation falls with n_i,eff); Id-Vg YB: thresholds 0.38 / 0.50 / 0.63 and 0.35 / 0.47 / 0.61 V, i.e.
    +0.02 V away from Fig.5(c). OldSlotboom stays.
  * FR (resistor of Fig.7(b) between the gates and the WL source, 1e6 Ohm, Case 2): 0.64 mV; the gate node dips 54 mV during
    a BL fall, rises 28 mV during a BL rise, back within 1 ns.
- Row hammer Z-Z' in 2D with that resistor (QR / QRi, text Cs 4.2 fF, 10 cycles; paper 0.0100 mV per cycle):
    R 1e5: victim gate +150 mV for 20 ps at each aggressor rise; loss 0.0007 / 0.0006 mV per cycle (impact ionization off / on)
    R 1e6: +230 mV, gone in 100 ps; storage node shifts -1.04 mV in the first two cycles, then 0.0005 - 0.0007 mV per cycle
    R 1e7: storage node -0.23 / -0.23 / -0.19 / -0.16 / -0.13 / -0.10 / -0.08 mV per cycle, shrinking: the gate node settles
           with R C of about 1 ns; a coupling shift, not an accumulating loss. In a 2 ns window it looks like 0.1 - 0.2 mV per
           cycle. The paper's 0.01 lies between R 1e6 and 1e7. No R is given; it would be a fit parameter (user to decide).
- 3D unit cell g3_c2h against the 2D section and Fig.5(c) (Case 2): Id-Vg V3I: Vg at 1e-10 / 1e-8 / 1e-6 A 0.33 / 0.45 / 0.58 V
  (2D 0.33 / 0.45 / 0.59, paper 0.33 / 0.44 / 0.57), 60.4 mV/dec, log I at -1 / +1 / +1.8 V -12.72 / -4.13 / -3.63 (2D -12.94 /
  -4.15 / -3.67). Write V3Wp: 0.511 / 0.713 / 0.858 / 0.968 / 1.064 V at 12 / 24 / 39 / 60 / 100 ps (2D 0.492 / 0.690 / 0.837 /
  0.951 / 1.052). The 3D cell is the 2D cell.
- 3D numerics: with the iterative solver the transients crawl as soon as the WL is on (200 inner iterations in every Newton
  step, 40 - 60 Newton steps, 10 min per time step); with ParDiSo (`Lin3="Pardiso"`) 4 Newton steps, 11 s per time step on
  53k vertices and 25 s on 107k. X3p / X3pi / X3pg (row hammer X-X', impact ionization off / on, cut 40 nm) started
  02:21, about 420 steps each. Read with `python3 tools/gt_tran.py runs/X3p_xx runs/X3pi_xx runs/X3pg_xx`.
- Comparison workbook rebuilt: `results_vbl_hwl_1t1c_3ddram\GT_IRPS2026_논문대비_비교표_2026-10-06.xlsx`.

## 2026-10-06 (au) tunnelling calibration: carried out, and why it cannot be what Fig.8 needs (user: check first, then calibrate)
- Check before the runs (now a gate: `tools/gt_start.sh` builds missing meshes, runs `tools/gt_precheck.sh`, starts the batch only
  on ALL PASS): gr_c1h .. gr_c4h junctions at 50.00 / 175.00 nm at three heights, N+ 1e20, body 1e18 / 1e16. Conditions re-read:
  * Fig.8(b) from the pixels (frame 0 .. 200 ns = columns 658 .. 948, 18 BL edges at 688.5 .. 947.5): first BL fall at 21.0 ns,
    period 21.0 ns, 9 low phases in 200 ns. The 16 ns / 20 ns / 10 pulses used so far were read by eye. New timing = `FB2`
    (hold 20.7 ns after the write, period 21, 9 pulses, edges 0.5 ns [ASM, not resolvable]). Codex read the same independently.
  * Fig.8(b), (c) storage node, loss in mV (Cases 1 / 2 from 5.75 mV per pixel row, 3 / 4 from the zoom, 0.47 mV per row):
    Case 1: 43 at 26 ns, 55 after the first low phase, 67 / 76 / 83 after the next three, 100 at 200 ns;  Case 2: 23, 29, 50;
    Case 3: 3.3 at 24 ns, 7.1 at 31 ns, 14.6 at 197 ns;  Case 4: 1.4 at 24 ns, 3.5 at 30 ns, 5.2 at 63 ns (then hidden; about 7);
    Case 5: within 1 mV. So: no droop that can be read before the first BL fall, the largest step in the first low phase.
- Models tried for "generation that goes on while holes pile up" (Lee et al. survey, TED 2026, Fig.3: holes generated by GIDL
  during BL precharge accumulate in the isolated body and can bias a parasitic n-p-n BJT; BL 1/2 VDD -> VSS triggers the spike):
  * BTBT 3 = Hurkx with DensityCorrection=Local. Correction of my wording (Codex, manual p.534/537): this does not remove the
    density factor D, it puts densities corrected by the quasi-Fermi gradient into it. Hold test, A 3.5e19: 12.7 nA at the
    storage-node corner, constant in time. Three Math settings give the same numbers but the steps collapse to 1e-15 s again
    and again (13 - 84 min for 20 ns); no Id-Vg gets below -0.83 V, also not as a sweep in time. DenCorRef 1e3 / 1e10: no help.
  * alpha = -1 ("only generation") with dPot: with dPot 2.24 V no generation at the corner at all, with 1.12 V 0.05 nA, Id-Vg
    branches ragged and not ordered in A (dPot switches per mesh node). Dropped.
  * Id-Vg as a transient gate sweep (0.3 -> -1 V in 130 s, `SwT`): equals the DC sweep of the default model within 0.02 decade.
- Where the two branches are made (default model, saved plots, `tools/gt_map.sh`): Id-Vg at -1 V: generation at the BL junction
  5.8 nm inside the body, 0.91 MV/cm, 6.5e-14 A = the drain current, and the same amount recombines at the source corner
  (3.2 MV/cm): no gain. Hold: storage-node corner 3.44 MV/cm, 14.6 pA; with BTBT 3 the same field and 0.48 of the undamped rate.
- CFd (BTBT 3, A 2.8e19, FB2, five cases): 9.2 - 10.7 nA. Body centre, after the write -> first BL fall: +556 / +496 / +432 /
  +415 mV (paper 555 / 445 / 365 / 320). But the storage node drops 36 / 48 / 60 / 59 mV in the 21 ns hold, and in the first
  low phase of Case 3 by 30 mV = the generation alone (parasitic BJT gain about 0.3; the body stays clamped at 0.79 V above
  the BL). CHe (A 8e18, B 1.9e7): 10.3 - 10.6 nA, as predicted from the two fields (B 1.9e7 would lift the BL branch 14 times).
- **Charge bookkeeping, the decisive point.** Every pair made at the storage-node junction takes one electron from the node.
  The paper's Cases 3 / 4 / 5 lose 53 / 25 / 3.6 aC in 200 ns and at most 12 / 5 aC before 24 ns. A body-centre potential up
  by 0.32 - 0.56 V under 5 nm HfO2 needs 0.2 - 0.3 fC of holes (measured: 1300 - 1400 holes for +0.42 V). So the paper's
  holes do not come out of the storage-node junction at nA level, and no rate or field coefficient can repair that: with A
  small enough for Case 5 (1 mV: at most 18 pA; the default model gives 13 pA = 0.64 mV, which fits) the body does not rise.
  The order Case 4 (7 mV) >> Case 5 (1 mV) is also against generation (WF 5.0 gives more of it: ours 0.51 / 0.64 mV).
- What the paper's numbers do fit: our equilibrium potentials at the body centre are -0.296 / -0.190 / -0.114 / -0.075 /
  -0.373 V; adding the paper's rises gives +0.260 / +0.255 / +0.251 / +0.245 / -0.005 V. Cases 1 - 4 end at one level.
  Two readings: (i) electrostatic potential: +0.25 V is where the BL (0 V) -> SN barrier is 0.3 eV, i.e. nA conduction, which is
  what the first-step losses are (27 / 11 / 2.4 / 1.2 nA); it needs the 0.2 - 0.3 fC of holes from somewhere that costs the
  storage node nothing. (ii) hole quasi-Fermi potential at t_A minus the potential at t = 0: needs only 1 - 100 holes, and the
  default model with impact ionization on gives 584 / 435 / 405 / 389 / 375 mV (off: 390 / 371 / 356 / 368 / 374) against
  555 / 445 / 365 / 320 / 368; Fig.7(e) (665 mV with impact ionization, 2.4 without, 1.8 grounded) reads the same way. The
  paper does not say which quantity it plots, where, or between which instants beyond the two dots of Fig.8(b).
- X series, default Hurkx, FB2, five cases (`tools/gt_fbe_tab.py`): as it is (CFk) loss at 200 ns 0.46 / 0.64 / 0.56 / 0.51 /
  0.64 mV; impact ionization with the default driving force (CFi), Eparallel (CFp), ElectricField (CFf), BL contact that takes
  no holes (CFh, CFg): the same losses to 0.02 mV. Holes left by the write with impact ionization: 73 / 12 / 7 / 1.6 / 0.08
  (ElectricField 124 / 35 / 10 / 4 / 1.7). The write makes 600 - 900 pairs (17 000 with ElectricField) in the first 40 ps but
  they leave the body while the WL is high (Case 1: 411 at 30 ps, 127 at 100 ps, 70 at 315 ps; 10 nm bodies: none after 150 ps).
- Mesh (gq025 / gq2 / gq5: junction mesh 0.25 / 2 / 5 nm, 13.9k / 7.7k / 3.2k vertices): corner generation 14.6 / 14.7 / 14.1 pA,
  FBE loss 0.61 - 0.64 mV, thresholds the same, GIDL branch at -1 V -12.94 / -12.86 / -12.79. Not a mesh matter.
- State: Fig.8(a) is within 0 - 22 % under reading (ii) with the stated models; the storage-node losses of Cases 1 - 4 (first
  step 55 / 29 / 7 / 3.5 mV) are not produced by any variant; Case 5 is. What the paper's simulation has that ours has not is
  not in the paper. Seen on re-reading Fig.7(b): its row-hammer circuit has a resistor R between the victim gate and its WL
  source (no value given); `Rwl` exists in the deck and was never used. The survey also names WL-WL coupling as its own
  loss path. Next (user, 2026-10-06): run what these results suggest, then the 3D structure and the next stage.

## 2026-10-05 (at) project split; intent of the tunnelling calibration; why the Case order is reversed (user)
- Split out of bcvfet_tcad into this folder (PC and server). make_runs.py / params.py rewritten for the Cho cell only; the 54
  decks and 11 structure files they generate are identical to the ones that were run (comments aside). Prompt for Codex:
  `Desktop\서강대\반엘프\Codex_전달_프롬프트_2026-10-05.md`.
- Intent (user: say so in every report): turning the density damping of the tunnelling model off follows the authors' own
  description (Lee et al. survey, TED 2026, Fig.3): GIDL holes accumulate in the isolated body and bias the parasitic BJT.
- Case order (paper: loss 30 nm > 20 nm > 10 nm, about 100 / 50 / 14 mV, most of it at the first BL fall; trial RAm3: 20 nm >
  30 nm, growing from period to period). Likely related, most likely first:
  (1) where the generation happens. Ours sits at the gate edge of the storage-node junction (surface), so it does not grow with
      body thickness; a weaker field dependence (Hurkx B) lets the whole junction cross-section and the BL side contribute,
      which scales with thickness and is also what the GIDL branch of Fig.5(c) needs.
  (2) the regime. The paper's body is already up by 445 - 555 mV before the first BL edge and the loss comes as a first dump:
      limited by the hole reservoir (grows with thickness; the survey: loss saturates with BL-hold time). Ours reaches only
      +130 .. +180 mV in the 16 ns hold and the loss follows the generation rate, the same in both cases.
  (3) Cs per case: the text's 5.1 fF for 30 nm against 4.2 fF for 20 nm lowers the thick body's loss by 20 % at equal charge.
  (4) gain of the parasitic BJT, larger for the thicker, less gate-controlled body (acts only once the body is charged).
- Codex's workbook of material candidates per part read (313 evidence rows): gate dielectric HfO2, ZrO2, HfO2/ZrO2/HfO2, "oxide
  5 nm" (the paper); spacer / interlayer SiO2, Si3N4, SiON, SiN, air spacer. To be used when a material has to be varied.
- Next: calibrate rate and field coefficient with the damping off against Fig.5(c) (GIDL branch) and Fig.8 (loss, order, shape).

## 2026-10-05 (as) can the density treatment of the tunnelling model be calibrated from the folder "저자의 논문"? (user)
- Folder read (13 files: Lee survey TED 2026, Hsu IMW 2025, Lee routing 2026, Jeong FE-NAND, Hsu TED 2026, Lee IMW 2026,
  Wu TED 2025, the IRPS paper, four patents, a source list). None names a tunnelling coefficient or a density option; the
  only model statement is the IRPS paper's "BTBT Hurkx model". What they do give: the mechanism (survey, Fig.3 text: holes
  generated by GIDL accumulate in the isolated body and bias the parasitic n-p-n BJT; a BL swing then gives a BJT current
  spike) and curves to aim at (IRPS Fig.5(c) GIDL branch, IRPS Fig.8 loss and body potential; Hsu IMW 2025 Fig.2(c) and
  Lee IMW 2026 Fig.3 for other Si cells). So: no direct calibration, an indirect one against the authors' curves.
- The mechanism of the survey needs generation that goes on while holes pile up; the default Hurkx setting damps exactly that.
- Feasibility (meshes re-checked first; BTBT 3 = DensityCorrection=Local, Hurkx rate x 1e-3, runs RAm3 / YAm3):
    FBE Case 2: loss 81.2 mV in 200 ns (7 -> 11.5 mV per period, growing), body centre -0.19 -> +0.32 V (+510 mV);
                paper about 50 mV and 445 mV.   Generation 1.0e23 = 1.6 nA.
    FBE Case 1: 54.6 mV after nine periods, body +0.58 V; paper about 100 mV and 555 mV.
    Id-Vg Case 1 (stops at -0.85 V): thresholds unchanged; log10 I at -0.8 / -0.5 V: -16.06 / -15.64 against -13.65 / -14.65 with
                the default model and about -14.0 / -14.74 in the paper. The other three Id-Vg did not converge.
  With rate x 1e-2 the FBE runs crawl (13 ns in 13 min) and were stopped.
- Reading: Fig.8 wants the storage-node-side generation about 100 times the default-model value, Fig.5(c) wants the BL-side
  branch where the default model has it. One rate factor cannot give both (x 1e-3 with the damping off: SN side right
  order, BL side 1 - 2.4 decades low). A second knob is needed that weighs high field against low field: the Hurkx field
  coefficient B, or the storage-node junction itself (position under the gate edge, grading). Not done.

## 2026-10-05 (ar) are the materials the paper does not name behind the missing loss? (user) No: factor 0.1 - 1.7
- Hold test (H, 2 ns, Case 2, 2D), one material changed at a time; generation at the storage-node junction per cell:
    as built (HfO2 5 nm k 22, Si3N4 spacers)   14.7 pA
    spacers SiO2 / HfO2                         14.2 / 16.1 pA
    gate dielectric SiO2 5 nm                   1.8 pA
    gate dielectric permittivity 10 / 50        7.7 / 25.0 pA
  The paper's loss needs 0.1 - 2.5 nA. The unnamed materials move the loss by less than a factor of two upward.
- Mesh check before the run done for gm_spox; for gm_sphk the check file was missing when the batch started and was read
  afterwards (junctions 50.00 / 175.00 nm). Start the batch only after every check line is there.

## 2026-10-05 (aq) 3D unit cell (transistor only, BL 50 nm): same generation as the 2D section
- User: BL 50 nm (back to 100 if it makes trouble), transistor only in 3D; never start a run without the check against the
  paper's text and figures.
- sde_gt3_dvs.cmd, structure g3_c2h: half cell (mirror plane through the row centre, AreaFactor 2): silicon 0 .. 50 nm across the
  row, wall 50 .. 100 nm (oxide), both gate layers continuous over the wall, pillar inside the row only; along the channel
  pillar half 25 | spacer 25 | gate 100 | spacer 25. 53k points. Check before the run (tools/gt3_check.sh, chk3d.tcl): junctions
  at 25.00 and 150.00 nm (1e20 / -1e18), doped silicon up to z = 50.00 nm, cell to z = 100.00 nm, contacts bl / sn_v / gs_v /
  gd_v. Against the paper: Fig.5(a) BL pitch 200 = 100 + 100; top view of Fig.2 (pillar fills the row, word lines run over
  the walls); cross-section of Fig.2 (parts along the channel); Z stack of the table; WL pitch 275 with the 50 nm pillar.
  Not the paper's: the capacitor (lumped), neighbours.
- Hold test (deck_cho test H: BL and storage node to 1.1 V together, WL 0, 2 ns; a diagnostic of the FBE hold state, not a
  run of the paper), Case 2: generation integral 2D 9.162e20 x 0.1 um = 14.7 pA per cell; 3D 4.540e19 x 2 = 14.5 pA.
  Ratio 0.99. Body holes after 2 ns the same too (1.84e11 in both, same units). The third dimension of the transistor
  does not raise the loss. Both runs took under 7 minutes.

## 2026-10-05 (ap) 3D unit cell: what the paper fixes (user: base the 3D unit cell on the paper too)
- Top view of Fig.2 measured (raw image, 2.08 nm/px across the rows from BL pitch 200 nm = 96 px; 1.98 nm/px along the
  channel from BL centre -> plate centre 139 px = WL pitch 275 nm). Across the rows: cell row 39 px + lines (about 90 nm),
  isolation wall 50 px + lines (about 110 nm): the table's 100 / 100 within the line width. The BL fills the whole row
  width and is 39 px long; the WL bars run over the walls, 40 px; BL-to-WL gap 14 px edge to edge (7-8 px of spacer colour);
  WL-to-capacitor gap 18 px; capacitor box 98 px for two storage nodes with the plate circle in the middle.
- So the top view is drawn to the table's pitches, and in it the gate is about 80 nm, the BL about 83 nm, not 100 / 100 as the
  cross-section view and the single-cell view show (there BL centre -> plate centre is 333 - 350 nm). With Lg 100 and L_CAP 100
  from the table, WL pitch 275 leaves BL / 2 + both spacers = 75 nm. Spacers 25 / 25 (Id-Vg checked) -> BL 50 nm.
  Not decided: user.
- Capacitor drawing (Fig.2, cut view + legend): ground pillar with dielectric shell through all layers, horizontal ground
  plates from it, storage-node block (L_CAP long, row wide) between two plates. Top + bottom faces alone, 100 x 100 nm at
  EOT 3.8 A, are 1.8 fF; with the pillar-side face about 2.3 - 2.5 fF. The text's 3.6 / 4.2 / 5.1 fF needs more area than
  that; the write curve (am) asks for 1.5 - 2.1 fF. Plate and node thicknesses are not given.
- Unit cell proposed: X = BL pitch 200 nm (Si 100 + half a wall each side), Y = BL centre to plate centre, Z = one Z pitch;
  first 3D cell = transistor in 3D with the lumped Cs, capacitor geometry as a second step.

## 2026-10-05 (ao) gr_ meshes: write, FBE, RH again; what the charge loss answers to (user: list the variables)
- Pre-run check: gr_c1h .. c4h, gr_c1 / gr_c2 (SiO2), gr_yy, gr_zz junctions and levels read from the meshes before any run.
- Same numbers as on the old meshes. Write (BL 1.168 V): SN after WL off 1.124 V (4.2 fF), 1.099 V (1.8 fF). FBE loss in
  200 ns, Cases 1-5: 0.52 / 0.71 / 0.63 / 0.57 / 0.72 mV (RF), avalanche on 0.53 / 0.72 / 0.63 / 0.57 / 0.72 (RFi), Cs x 0.43
  1.19 / 1.57 / 1.36 / 1.23 / 1.64 (RG). RH with 1.8 fF, ten periods: 0.00148 mV per cycle in yy and in zz, 0.00135 with
  avalanche; SN +0.47 mV while the aggressor WL is high in zz, none in yy. Paper: FBE 100 / 50 / 14 / 7 / 1, RH 0.0535 / 0.0100.
- What the loss is: band-to-band generation at the storage-node junction. Integral of Band2BandGeneration 8.4e20 after
  the WL is off = 13.5 pA at 0.1 um width = the SN loss; the holes stay in the body (integral of hDensity in R.Ch_v
  5.7e11 -> 1.8e14 in 200 ns, Case 1; body centre +39 mV).
- One change at a time, Cases 1 / 2, text Cs, loss in 200 ns (base 0.52 / 0.71 mV):
    Hurkx rate x 10 / x 100     0.61 / 0.74,  0.70 / 0.75      generation integral only x 1.36 at x 100
    SRH lifetimes x 0.01        0.52 / 0.71                    field-enhanced SRH: 0.52 / 0.71
    BL edges 5 ps (0.1 ns)      0.52 / 0.71                    avalanche on: 0.53 / 0.72
    358 K                       16.4 / 22.9                    generation x 32; body centre +412 / +339 mV in 200 ns
    SiO2 5 nm gate dielectric   0.00 / 0.01                    writes only to 0.79 / 0.91 V in 0.3 ns
  So the generation does not follow the Hurkx prefactor but n_i (activation about Eg / 2): the factor
  D = (np - ni^2) / ((n + ni)(p + ni)) of Sentaurus' Hurkx model throttles it where the generated holes pile up.
- Band2Band( Model=Hurkx DensityCorrection=Local ) (BTBT 3; runs RL, YL): at the WL falling edge the generation integral
  goes to 6e25 (1e5 times), the body centre jumps by +0.36 V (Case 4) to +0.73 V (Case 1) within picoseconds, and the
  step size collapses there; the Id-Vg with it stalls in the first gate ramp. Runs stopped, no loss number. It shows the
  lever (the density treatment of the tunnelling model at the storage-node junction), not a usable setting yet.
- Not tried: non-local tunnelling for this device, the junction a few nm under or away from the gate edge, a graded
  junction, a spacer / dielectric change next to the storage-node junction, negative WL level, 3D.

## 2026-10-05 (an) doping per region: junctions exactly on the part boundaries (user saw it in the yy picture)
- User: in gt_rh_yy_xsec_vs_cho_fig2 the N+ under the SN-side spacer reaches past the spacer edge into the p silicon, and the
  p silicon looks recessed at the N+ pillar, while the paper's parts are divided exactly; check the other parts too.
- Two causes. (1) Real: the constant profiles were placed by coordinate windows, so every vertex on a silicon / silicon
  boundary took the N+ value and the junction lay inside the body, between the boundary and the next vertex (gx_c2h: 50.00 ..
  50.39 nm and 174.61 .. 175.00 nm; up to 0.4 nm), and the boron background made the N+ 9.9e19 instead of 1e20.
  (2) Picture: 150 doping columns over 400 nm (2.7 nm) painted that as about 1.7 nm.
- Fix: sdedr:define-constant-profile-region for R.BL, R.Ch_*, R.Src_* (no material-wide boron, no windows). Structures
  gr_c1h .. gr_c4h, gr_yy, gr_zz (the gx_ / gp_ meshes are the old ones). tools/gt_mesh_check.sh reads the junctions at
  three heights per layer: 50.00 / 175.00 nm (single, zz both layers), 25.00 / 150.00 / 250.00 / 375.00 nm (yy), levels
  1e20 and -1e18 (-1e16 in gr_c4h), same at 0.5 nm from either face and at mid-height. Pictures redrawn from 0.5 nm columns
  (export_doping.sh <struct> <x1> <columns>): gt_cell_ / gt_rh_yy_ / gt_rh_zz_xsec_vs_cho_fig2.png.
- Other parts held against the array cross-section of Fig.2: spacer / gate / spacer split at gate level, gate dielectric
  line from the pillar face to the end of the SN-side spacer, pillar through all layers, 15 + 15 nm of oxide between two
  layers: as drawn. Not the paper's: the storage node (a contact and a lumped Cs here), the pillar contact (top end in
  yy, axis otherwise). Vertical proportions of the drawing (body : gate : isolation = 10 : 12 : 14 px) are not the
  table's 20 : 20 : 30 nm; the table is used.
- Id-Vg on the gr_ meshes (YE, pre-run check done): 0.36 / 0.48 / 0.61, 0.33 / 0.45 / 0.59, 0.31 / 0.43 / 0.56, 0.27 / 0.39 /
  0.51, 0.57 / 0.69 / 0.81 V: equal to XE within 0.01 V and 0.02 decade. Fig.5(c) agreement unchanged. Shared package and
  workbook now carry gr_ + YE. RH on gr_yy / gr_zz (RQ, Cs 1.8 fF) started 20:14; TS on the old meshes stopped.

## 2026-10-05 (am) Fig.4(a) with a smaller Cs; FBE / RH repeated with it; pre-run check made a rule (user)
- User rule: before every batch, check structure and conditions against the paper's text and figures; run only if they
  agree (CLAUDE.md). The two-cell sections had been run after gt_check only. Now drawn next to the array cross-section of
  Fig.2 (pics gt_rh_yy_xsec_vs_cho_fig2.png, gt_rh_zz_...): BL between two mirrored cells / two layers on one side with
  15 + 15 nm of oxide between them; silicon under the BL-side spacer has the body colour ((6, 11, 250) against (3, 11, 251)
  under the gate, three layers, both cells), under the SN-side spacer the BL colour. They agree. Victim below / aggressor
  above as in Fig.6(b) and 7(b); BL at Vdd/2, victim WL 0, aggressor WL 0 <-> Vpp as in the text.
- The system file had a point only every 25 ps of the charging curve (CurrentPlot Intervals 4): the "+12 / 24 / 39 / 60 ps"
  values of (aj) and (ak) were straight-line interpolations and too low. solve_transient now writes a point per maximum step.
- Fig.4(a), dense, BL 1.168 V (tools/gt_fig4a.py, 17 points of the paper's curve). SN at 24.25 / 39.25 / 54.25 / 75.25 ps,
  paper 0.647 / 0.921 / 1.058 / 1.127:   Cs 4.2 fF 0.475 / 0.717 / 0.853 / 0.959 (rms 182 mV);  2.5 fF rms 70;
  2.1 fF 0.677 / 0.901 / 1.002 / 1.071 (57);  1.8 fF 0.720 / 0.933 / 1.026 / 1.088 (66; 34 if moved 1.75 ps);
  1.5 fF 0.768 / 0.968 / 1.051 / 1.106 (90; 44 if moved 2.5 ps).  SN after the WL is off: 1.108 / 1.099 / 1.086 V
  (2.1 / 1.8 / 1.5 fF), paper 1.10.  Close for 1.5 - 2.1 fF, not the same: the paper's curve is slower at the start and
  faster at the end than any single Cs gives.
- FBE with the text's Cs x 1.8 / 4.2 and BL 1.168 V (TH): SN after the write 1.102 / 1.099 / 1.094 / 1.093 / 0.973 V; loss in
  200 ns 1.19 / 1.58 / 1.37 / 1.23 / 1.64 mV (paper 100 / 50 / 14 / 7 / 1): 2.4 times the earlier loss, i.e. only 1 / Cs.
  RH with 1.8 fF (TS): 0.0015 (yy) and 0.0014 (zz) mV per cycle after one or two periods, runs not finished when read.
- Fig.8: its caption (a) repeats the caption of Fig.5 ("Model parameters and different design space ..."), but the panel
  is the body-potential bar chart and the text of section VI cites Fig.8(a), (b), (c) as results. It stays a target.

## 2026-10-05 (al) Fig.5(d) checked point by point: the sense-margin set of (aj) was wrong (user asked)
- All 24 markers of the right panel digitised (labels 350 .. 50 at rows 419.3 .. 618.7, 37.36 px per 16 layers; shifted by
  1.8 mV to put the labelled point on 144.14). Straight line through 1 / SM against layers: signal term 0.555 V (20 nm),
  0.544 V (30 nm), C_BL 0.187 / 0.182 fF per layer with the text's Cs.
- Set A = formula as printed: 0.55 V, Cs 3.6 / 4.2 / 5.1 fF, C_BL 0.1848 fF per layer (11.83 fF at 64): every 20 and 30 nm
  point within 1.5 mV, 10 nm within 1.2 mV up to 64 layers (beyond that the squares are hidden under the circles).
  Set B of (aj) (0.605 V, 0.1997 fF per layer, Cs 4.0) hits only 20 nm / 64 layers: 336 instead of 322 at 16 layers, and
  the 30 nm series is off by 20 mV. B withdrawn; README of the shared package, workbook and this file now say A.
- C_BL 0.185 fF per layer is back-calculated: 7 % below ref. 9 (0.1997) and 8 % below the left panel of the same figure
  (0.64 / 0.61 / 0.55 at 128 layers = C_BL/Cs 3.2 / 3.05 / 2.75 at 64, i.e. C_BL proportional to the Z pitch).
- The 0.605 V of the RH counts (60.5k x 0.01 mV) stays an observation without explanation.

## 2026-10-05 (ak) Cho cell: three follow-up checks on the transient mismatch (user)
- Runs TG / TGi (FBE Cases 1-5, avalanche off / on, 16 ns hold, probes under the BL-side spacer and at both gate ends),
  TGw (BL 1.155 V during a 1 ns write, avalanche on), TWv_cs42 / 30 / 21 / 15 (write, BL 1.155 V, Cs 4.2 .. 1.5 fF).
- (1) Where the body potential is read. Electrostatic potential, before the write -> before the first BL edge [mV]:
      Case            1     2     3     4     5      paper 555 / 445 / 365 / 320 / 368
      gate centre     21     5     1     1     0     (avalanche on: 138 / 22 / 9)
      BL-side spacer  465   436   411   411   409
      SN end of gate  496   342   138   140
  Under the spacer it also swings 586 - 663 mV with every BL edge. So the paper's few hundred mV are what the body that the
  gate does not cover does when BL and SN go from 0 to 1.1 V: geometry, not stored holes. Magnitude right, the paper's
  spread over thickness (555 .. 365) is wider than ours (465 .. 411) and its Case 4 < Case 5 is not there.
- (2) Write level and length: SN after the write 1.12 - 1.13 V, loss in 200 ns 0.55 / 0.72 / 0.62 / 0.56 / 0.7 mV: unchanged
  (the same 13 - 15 pA). Body centre +89 / +11 / +7 mV. Not the cause.
- (3) Write curve, SN at 24.5 / 36.5 / 51.5 / 72.5 ps (paper 0.65 / 0.89 / 1.04 / 1.12 V, BL about 1.16 V):
      Cs 4.2 fF 0.40 / 0.65 / 0.81 / 0.94;  3.0 fF 0.47 / 0.74 / 0.89 / 1.00;  2.1 fF 0.55 / 0.82 / 0.96 / 1.05;
      1.5 fF 0.63 / 0.89 / 1.02 / 1.09.  SN after the WL is off: 1.094 V (2.1 fF), 1.072 V (1.5 fF); paper 1.10 V.
  The paper's cell charges like 1.5 - 2.1 fF on our transistor, 35 - 50 % of the 4.2 fF of its text ("calculated using the
  dimensions"). A stronger transistor would look the same: not separable in the 2D section.
- Still open: the size of the paper's SN loss (0.1 - 2.5 nA equivalent). With Cs 1.5 - 2.1 fF ours would be 2 - 3 times
  larger, still 30 - 50 times short. 3D is not needed for (1) and (2); it is for (3) (the capacitor as drawn) and for RH Case 3.

## 2026-10-05 (aj) Cho cell: write, FBE and RH transients on the Id-Vg device. Not reproduced.
- User: go through figure reading, write, RH Cases 1 / 2 (+ impact ionization, grounded body) and FBE Cases 1-5; no 6F2
  device; share the fixed device; fix C_BL and Cs so that the paper's sense margin comes out and say so separately.
- Shared package: `Desktop\서강대\반엘프\GT_IRPS2026_확정소자_공유_2026-10-05` (+ .zip), built by tools/export_gt_pkg.py.
- Sense margin. The text gives Cs only (3.6 / 4.2 / 5.1 fF); C_BL and C_BL/Cs only as Fig.5(d). The paper's RH counts are
  margin / loss with margin 0.605 V (60.5k x 0.01 mV = 100.8k x 0.006 mV), and 144.14 mV x (1 + C_BL/Cs) = 0.605 V needs
  C_BL/Cs = 3.197 = 12.78 fF / 4.0 fF, the values of its ref. 9 (0.0247 + 0.175 fF per layer x 64, Cs 4 fF). Fixed for the
  sense-margin formula: C_BL 12.78 fF, Cs 4.0 fF, signal term 0.605 V (not Vdd/2 = 0.55 V) -> 143.7 mV with our I_L 1.3e-16 A.
  With 0.55 V as printed: 135.9 mV. Fig.4(a) reads BL = 1.16 V (frame 0 .. 3 V = rows 276 .. 79), i.e. 1.155 - 0.55 = 0.605.
  The transient decks carry the text's Cs (3.6 / 4.2 / 5.1 fF).
- Read from the figures: Fig.4(a) SN 0.72 / 0.92 / 1.06 / 1.13 V at 12 / 24 / 39 / 60 ps after the WL edge; Fig.6(c) 10
  pulses, 0.094 ns high / 0.094 ns low, vertical edges; Fig.8(b) BL 0 <-> 1.1 V, 20 ns period, 50 %, 10 pulses, SN after
  200 ns about 1.00 / 1.05 / 1.087 V (30 / 20 / 10 nm), Fig.8(c) Case 4 about 1.093, Case 5 1.099; Fig.8(a) body rise 555 /
  445 / 365 / 320 / 368 mV; Fig.7 Case 2 with avalanche 1.1 -> 0.58 V in 2 ns, body +665 mV (2.4 off, 1.8 grounded);
  thresholds 11.3k / 60.5k / 100.8k, with avalanche 11.3k / N/A / 86.4k, grounded Case 2 16.8k.
- New: sde_gt_dvs.cmd with a cell function, `Pair` one / yy (two cells across the BL) / zz (two layers), `Bgc` (body
  contact slot); structures gp_yy, gp_zz, gp_zzg; `deck_cho` (write, then FBE or RH; AreaFactor 0.1; storage nodes Set to
  0 V for the DC start and Unset, else the 1e16 / 5.0 eV cell is singular); tools gt_tran.py, gt_log.sh, gt_kill.sh.
- Numerics: with high-field saturation on holes the step size collapses to 1e-16 s at the WL edge of the write (30 nm body,
  both pairs, runs with avalanche). Not Digits, not ErrRef(Hole), not damping, not RefDens: electrons-only saturation
  (`Mob` 3) cures it (trials TTa / TTb / TTc). Id-Vg with it (XE) = XW within 0.01 V / 0.02 decade (GIDL of Case 5 +0.17).
- Id-Vg cross-checks with avalanche on: HfO2 (XI) puts Cases 1-3 all at 0.28 / 0.41 / 0.55 V (paper 0.34 / 0.33 / 0.30 at
  1e-10): the paper's Fig.5(c) is without avalanche. SiO2 + avalanche (XS) brings the 1e-10 crossings to 0.37 / 0.35 / 0.32
  but leaves the on-current 0.5 - 0.9 decade low: SiO2 stays ruled out.
- Results (Case 2 device unless said; SN after the write 1.063 V, the WL edge takes 37 mV):
    write     SN 0.39 / 0.63 / 0.79 / 0.91 V at 12 / 24 / 39 / 60 ps: half the paper's speed (first slope equal, 0.03 V/ps)
    FBE       SN loss in 200 ns 0.4 / 0.65 / 0.6 / 0.5 / 0.7 mV (Cases 1-5), same with avalanche; paper 100 / 50 / 14 / 7 / 1.
              Body rise (centre under the gate, before the write -> before the first BL edge) 18 / 3 / 0 / 0 / -1 mV, with
              avalanche 137 / 21 / 9 / 2 / -1; paper 555 / 445 / 365 / 320 / 368.
    RH yy     0.00061 mV per cycle (paper 0.0535); zz 0.00061 (paper 0.0100);
              zz with avalanche 0.00054, body +6 mV (paper: 0.52 V in 2 ns, +665 mV); yy with avalanche 0.0001;
              zzg 0.0002 but it writes only to 0.72 V (the slot cuts the body). All ten periods, Digits 7 = Digits 5.
              In zz the SN sits 0.20 mV higher while the aggressor WL is high (reversible coupling); yy shows none.
              gt_tran.py samples 20 ps before each rising edge (2 ps fell on the edge and faked 0.0105 mV per cycle).
  Every loss of ours is the same 13 pA: static GIDL at the storage-node junction (N+ at the gate edge under HfO2), not the
  aggressor and not the body. The paper's losses correspond to 0.1 - 2.5 nA.
- Open, not decided: what makes the paper's body rise by 0.3 - 0.55 V within about 20 ns. Charge of that size cannot come
  from leakage in our device (13 pA x 20 ns = 2 holes; the body needs about 2000 behind HfO2). Candidates to look at: where
  and between which instants the paper reads "body potential" (ungated body under the BL-side spacer follows the BL); the
  state the write leaves (their BL 1.16 V, their write length); a junction / spacer / dielectric detail of the 3D model
  that the 2D section does not carry. The write being twice as fast with the same on-current points the same way: the
  cell of the paper is not fully described by Fig.5(c).

## 2026-10-05 (ai) Cho et al. (Georgia Tech, IRPS 2026) cell: section checked against Fig.2, three errors fixed, Fig.5(c) reproduced
- Direction (user): Chen dropped. Build the cell of Cho et al. as it is, no modification, and check the paper's numbers.
  Values only from the paper, the Shimeng Yu group's papers, the nine references of the IRPS paper and their references.
- The first structure (gt_*; runs GT_ / GTS_ / GTH_ / GH_ / GM_ / GV_ / GL_, results still on the server) was run before
  its section was compared with the drawing. User: is the section the paper's (the Chen problem again)? It was not.
  Pixel reading of the embedded Fig.2 image (array cross-section: gate 43.5 px; single-cell view: gate 200 px):
    part                              paper                                    first structure
    silicon under the SN-side spacer  N+ (red); source contact right behind    p body + an extra 25 nm N+ block   WRONG
    spacers                           own colour, not the isolation cyan       SiO2                               WRONG
    drain terminal of the Id-Vg       BL ("source and drain (BL)")             storage-node side                  WRONG
    BL pillar, BL-side spacer         N+, as long as the gate; 0.25 Lg, p under it    same
    gate dielectric                   along the silicon under both spacers     same
  The same drawing is the inset of Fig.2(c) of Hsu .. Yu, IMW 2025 ("TCAD for Si access transistor": DRAIN block, body
  under the drain-side spacer and the gate, N+ under the source-side spacer, SOURCE metal block).
  Cause of the first error: "gate to source block 23-28 nm" and "source block about 24 nm" were the same 11 pixels.
- Lengths that Fig.5(a) does not list: IMW 2025 Fig.6 gives 2WLtBL 175 nm and 2WLtC 375 nm at L 25 nm, i.e. BL + 2
  spacers = 150 nm and 2 spacers + 2 L_CAP + plate = 350 nm; with the drawn proportions (BL = plate = 4 spacers) BL 100,
  spacer 25, plate 100, L_CAP 100. The IRPS table still says WL pitch 275 nm although its Lg is 100 (its drawing: 333-350).
- Spacer material: the captions call the cyan layers oxide; the yellow is another insulator. The group's models hold
  SiO2 (k 3.9) and Si3N4 (k 7.0) (Lee .. Yu, IMW 2026) and the gate-level layer of the VBL flow is Si3N4 (Wu .. Yu, Wong,
  TED 2025): `Spm` = Si3N4, epsilon 7.0 in sdevice.par (Sentaurus default 7.5). Inferred, not stated in the paper.
- Now: sde_gt_dvs.cmd redrawn, structures gx_c1 .. c4 (+ "h" = HfO2), parameters `Spm`, `Dterm` (drain electrode of the
  Id-Vg deck), `RefD`; `Lsrc` gone. Mesh junctions at 50.0 and 175.0 nm. Picture of the mesh next to Fig.2
  (tools/plot_gt.py): pic_vbl_hwl_1t1c_3ddram\gt_cell_xsec_vs_cho_fig2.png.
- Fig.5(c) on the corrected cell: W 0.1 um (BL pitch 200 - wall 100; IMW 2025 Fig.2(c): W_Si,DG 100 nm), Vd 1.1 V on the BL
  (assumed), gate swept down, Hurkx and SRH defaults, no quantum correction, no impact ionization. tools/gt_fig5c.py;
  paper read from the image at about +-0.02 V and +-0.1 decade. Vg at 1e-10 / 1e-8 / 1e-6 A | minimum | log10 I at -1 / +1 / 1.8 V
    Case 1 paper  0.34 0.47 0.60 | -0.11 V -16.9 | -13.5  -4.07  (-3.64 at 1.7 V, Case 2)
    XW_c1         0.36 0.48 0.61 | -0.07   -17.0 | -13.20 -4.18 -3.65
    Case 2 paper  0.33 0.44 0.57 | -0.07   -16.4 | -13.2
    XW_c2         0.33 0.45 0.59 | -0.10   -17.0 | -12.98 -4.15 -3.67
    Case 3 paper  0.30 0.42 0.55 | -0.15   -16.4 | -13.1
    XW_c3         0.31 0.43 0.56 | -0.12   -17.0 | -12.94 -4.14 -3.71
    Case 4 paper  0.26 0.39 0.51 | -0.13   -16.4 | -13.2  -3.89
    XW_c4         0.27 0.39 0.51 | -0.20   -17.1 | -13.21 -3.90 -3.60
    Case 5 paper  0.53 0.65 0.78 | +0.09   -16.5 | -12.85 -4.52     (the legend box covers part of this curve: +-0.04 V)
    XW_c5         0.57 0.69 0.81 | +0.12   -17.1 | -12.76 -4.56 -3.65
  XW = HfO2 5 nm (epsilon 22 = Sentaurus default; no allowed paper gives a number), mobility = doping dependence +
  high-field saturation. Picture: pic_vbl_hwl_1t1c_3ddram\gt_fig5c_tcad_vs_cho.png (the paper's curve pixels under our lines).
  Before the correction the minimum was 20-30 times too high and the knee too soft (GM_: -15.2 .. -14.6, -4.45 at +1 V).
- What the same runs say about the unstated choices:
  gate dielectric: SiO2 5 nm (XO) spreads Vt of Cases 1-4 over 0.35 V (0.59 / 0.49 / 0.38 / 0.24; paper 0.08 V).
    The paper's 0.04 V between 30 and 10 nm body at 1e18 is q N dT / 2 Cox for an EOT of about 0.9 nm.
  mobility: doping dependence only (XH) is 0.14-0.48 decade high at +1 V and 0.45-0.8 at 1.8 V; with the normal-field
    term added (XG) 0.1 decade low. Ref. 7 of the paper (Chen .. , IEDM 2024) names "field-dependent mobility",
    the group's SISPAD 2024 "doping dependence mobility model".
- Numerics: XV / XF (no RefD) stop in the subthreshold range of the 1e16 body (hole equation, 1e5 holes cm^-3 at the
  body centre); `RefD` 1e12 (Math RefDens_[e|h]GradQuasiFermi_ElectricField) lets all five finish. Curves agree with and
  without it where both exist.
- Open: the paper's model is 3D. This section carries the transistor, RH Case 1 (across the BL) and Case 2 (vertical);
  Case 3 (across the isolation wall) and the wrapped capacitor need 3D. Not separated: how much each of the three
  corrections contributes. `dev_file()` in make_runs.py uses an undefined `p` (old FBE / RH decks; `--list` fails there).

