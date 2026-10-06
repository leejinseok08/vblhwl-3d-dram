# NOTES — Cho cell (VBL / HWL 1T1C 3D DRAM): decisions, checks, results

Newest first. Entries (ai) .. (as) were written while this work still lived in `bcvfet_tcad`; file and run names in them are
the ones of that time (structures `gx_*` / `gp_*` are the meshes before the doping went per region, `gr_*` the current ones).

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

