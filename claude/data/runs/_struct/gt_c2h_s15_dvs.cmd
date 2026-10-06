;; =====================================================================
;; sde_gt_dvs.cmd — one cell of the 3D stackable 1T1C DRAM model of Cho et al. (Georgia Tech),
;; "Row Hammer Effect and Floating Body Effect of Monolithic 3D Stackable 1T1C DRAM", IRPS 2026.
;;
;; 2D section along the channel (the paper's Y-Z plane; here x = Y, y = Z). The paper's model is 3D; the access
;; transistor is a double-gate device (main gate above, back gate below the body) that does not change along the
;; word line, so this section carries its Id-Vg. Left to right: half of the N+ bit-line pillar (drain), the p body
;; under spacer / gate / spacer, the N+ source block that leads to the storage node. Oxide everywhere else.
;;
;; From the paper (Fig.5a, text): Lg, body thickness, gate oxide, gate thickness, vertical isolation, S/D 1e20,
;; channel 1e16 .. 1e18, same work function on both gates. Read from the drawing Fig.2 (not stated): spacer
;; lengths, source block length, bit-line pillar width. Assumed: abrupt junctions at the pillar face and at the
;; source block (the paper gives no profile), SiO2 spacers.
;; Not in this section: storage capacitor (lumped in the decks), neighbouring cells, the third dimension.
;; Electrodes as in sde_dvs.cmd, so the same decks run: bl, sn_v, gs_v (main gate), gd_v (back gate).
;; =====================================================================
(sde:clear)
(sdegeo:set-default-boolean "ABA")
(define nm 1e-3)
(define Lg   (* 100 nm))        ; gate length: 100 (Fig.5a)
(define Tb   (* 20 nm))     ; body thickness: 30 / 20 / 10 (Fig.5a)
(define Tox  (* 5.0 nm))       ; gate oxide: 5 (Fig.5a)
(define Tg   (* 20 nm))       ; gate thickness: 20 (Fig.5a)
(define Dv   (* 30 nm))      ; vertical isolation: 30 (Fig.5a); half of it above and below the cell
(define S1   (* 15 nm))      ; gate to bit-line pillar (Fig.2)
(define S2   (* 15 nm))      ; gate to source block (Fig.2)
(define Ls   (* 25 nm))      ; source block (Fig.2)
(define Hb   (* 0.5 100 nm))   ; half of the bit-line pillar (Fig.2)
(define Nsd  1e+20)              ; source and drain (BL): 1e20
(define Nch  1e+18)              ; channel: 1e18 / 1e16
(define Gdi  "HfO2")            ; gate dielectric material ("gate oxide" in Fig.5a): SiO2 or HfO2
(define x1 Hb) (define x2 (+ x1 S1)) (define x3 (+ x2 Lg)) (define x4 (+ x3 S2)) (define x5 (+ x4 Ls))
(define y1 (* 0.5 Dv)) (define y2 (+ y1 Tg)) (define y3 (+ y2 Tox)) (define y4 (+ y3 Tb))
(define y5 (+ y4 Tox)) (define y6 (+ y5 Tg)) (define y7 (+ y6 (* 0.5 Dv)))     ; y7 = Z pitch = 2 Tox + Tbody + 2 Tg + Dvox
(define (box xa ya xb yb mat name) (sdegeo:create-rectangle (position xa ya 0) (position xb yb 0) mat name))

;; ---------------- regions ----------------
(box 0  0  x5 y7 "SiO2"    "R.Ox")
(box 0  0  x1 y7 "Silicon" "R.BL")       ; bit-line pillar (half), runs through all layers
(box x1 y3 x4 y4 "Silicon" "R.Ch_v")     ; floating body
(box x4 y3 x5 y4 "Silicon" "R.Src_v")    ; source block
(box x1 y2 x4 y3 Gdi       "R.GoxB")     ; gate dielectric, along the whole body as drawn in Fig.2 (single-cell view)
(box x1 y4 x4 y5 Gdi       "R.GoxT")
(box x2 y1 x3 y2 "TiN"     "M.GB_v")     ; back gate
(box x2 y5 x3 y6 "TiN"     "M.GT_v")     ; main gate

;; ---------------- doping: constant levels, abrupt junctions ----------------
(sdedr:define-constant-profile "CP.Ch" "BoronActiveConcentration" Nch)
(sdedr:define-constant-profile-material "CPM.Ch" "CP.Ch" "Silicon")
(sdedr:define-constant-profile "CP.Nsd" "PhosphorusActiveConcentration" Nsd)
(sdedr:define-refeval-window "W.BL"  "Rectangle" (position 0 0 0)   (position x1 y7 0))
(sdedr:define-refeval-window "W.Src" "Rectangle" (position x4 y3 0) (position x5 y4 0))
(sdedr:define-constant-profile-placement "PL.BL"  "CP.Nsd" "W.BL")
(sdedr:define-constant-profile-placement "PL.Src" "CP.Nsd" "W.Src")

;; ---------------- contacts ----------------
(define (cset name r g b) (sdegeo:define-contact-set name 4.0 (color:rgb r g b) "##"))
(define (edge-contact name p) (sdegeo:define-2d-contact (find-edge-id p) name))
(define (metal-contact name p)
  (sdegeo:set-current-contact-set name)
  (sdegeo:set-contact-boundary-edges (find-body-id p))
  (sdegeo:delete-region (find-body-id p)))
(define xg (/ (+ x2 x3) 2.0))
(cset "bl" 0 0 1)       (edge-contact "bl"   (position 0  (/ (+ y3 y4) 2.0) 0))     ; pillar axis
(cset "sn_v" 1 0 0)     (edge-contact "sn_v" (position x5 (/ (+ y3 y4) 2.0) 0))     ; storage-node end of the source block
(cset "gs_v" 0 0.6 0)   (metal-contact "gs_v" (position xg (/ (+ y5 y6) 2.0) 0))    ; main gate
(cset "gd_v" 0 0.9 0.3) (metal-contact "gd_v" (position xg (/ (+ y1 y2) 2.0) 0))    ; back gate

;; ---------------- mesh ----------------
(define (win name xa ya xb yb) (sdedr:define-refeval-window name "Rectangle" (position xa ya 0) (position xb yb 0)))
(win "RW.Glob" 0 0 x5 y7)
(sdedr:define-refinement-size "RS.Glob" (* 10 nm) (* 5 nm) (* 1 nm) (* 0.5 nm))
(sdedr:define-refinement-placement "RP.Glob" "RS.Glob" "RW.Glob")
(sdedr:define-refinement-function "RS.Glob" "DopingConcentration" "MaxTransDiff" 1)
;; body, source block and the pillar face: 2 nm along the channel, 1 nm across, 0.2 nm at Si/SiO2
(win "RW.Ch" (- x1 (* 10 nm)) (- y3 Tox) x5 (+ y4 Tox))
(sdedr:define-refinement-size "RS.Ch" (* 2 nm) (* 1 nm) (* 0.2 nm) (* 0.2 nm))
(sdedr:define-refinement-placement "RP.Ch" "RS.Ch" "RW.Ch")
(sdedr:define-refinement-function "RS.Ch" "MaxLenInt" "Silicon" "SiO2" (* 0.2 nm) 1.4 "DoubleSide")
(if (string=? Gdi "SiO2") 0 (sdedr:define-refinement-function "RS.Ch" "MaxLenInt" "Silicon" Gdi (* 0.2 nm) 1.4 "DoubleSide"))
;; the two abrupt junctions: 0.5 nm along the channel
(win "RW.Jd" (- x1 (* 6 nm)) y3 (+ x1 (* 10 nm)) y4)
(win "RW.Js" (- x4 (* 10 nm)) y3 (+ x4 (* 6 nm)) y4)
(sdedr:define-refinement-size "RS.J" (* 0.5 nm) (* 1 nm) (* 0.2 nm) (* 0.2 nm))
(sdedr:define-refinement-placement "RP.Jd" "RS.J" "RW.Jd")
(sdedr:define-refinement-placement "RP.Js" "RS.J" "RW.Js")

(sde:save-model "gt_c2h_s15_bnd")
(sde:build-mesh "gt_c2h_s15")
