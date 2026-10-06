# paper_targets.py - the numbers of Cho et al. (IRPS 2026) that the 2D device has to reproduce, in one place, with the
# tolerance each is scored with (reading error of the figure, or 0.3 decade for quantities read on a log scale / per cycle).
# Used by tools/score2d.py. Sources: Fig.5(c) pixels (gt_fig5c.PAPER), Fig.4(a), Fig.8(a) bars, Fig.8(b), (c) pixels
# (NOTES (au)), text of Sec.V (row hammer), Fig.7.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("GT_W", "0.1")
import gt_fig5c
IV = gt_fig5c.PAPER                                   # per case: v10, v8, v6 [V], vmin, lmin, lm1, l1 (log10 A)
IV_TOL = dict(v10=0.02, v8=0.02, v6=0.02, lm1=0.3, l1=0.1, ss=3.0)
IV_SS = 60.0                                          # mV/dec, all cases
WRITE = {12: 0.72, 24: 0.92, 39: 1.06, 60: 1.13}      # Fig.4(a): storage node [V] at ps after the WL edge (Case 2)
WRITE_TOL = 0.03
SN_START = 1.10                                       # every FBE / RH curve starts here
FBE_RISE = {1: 555, 2: 445, 3: 365, 4: 320, 5: 368}   # Fig.8(a): body potential rise t = 0 -> t_A [mV]
FBE_RISE_TOL = 30.0
FBE_FIRST = {1: 55, 2: 29, 3: 7.1, 4: 3.5, 5: 0.0}    # Fig.8(b), (c): loss at the end of the first low phase [mV]
FBE_200 = {1: 100, 2: 50, 3: 14.6, 4: 7.0, 5: 1.0}    # loss at 200 ns [mV]
RH = {"yy": 0.0535, "zz": 0.0100}                     # Fig.6(e), impact ionization off: mV per cycle (Y-Y', Z-Z'); X-X' 0.0060 needs 3D
RH_II = {"yy": 0.0535, "zz_drop": 520.0, "zz_gnd": 0.036}    # Fig.7: Y-Y' unchanged; Z-Z' 1.1 -> 0.58 V in the window [mV]; grounded body 16.8k cycles
DEC_TOL = 0.3                                         # decades, for losses and per-cycle numbers
FLOOR = 1e-3                                          # mV: below this a loss counts as this (log scale)
