;; =====================================================================
;; sde_gt3_dvs.cmd — 3D unit cell of the 3D stackable 1T1C DRAM model of Cho et al. (Georgia Tech), IRPS 2026: the access
;; transistor in 3D, the storage capacitor lumped in the deck (user 2026-10-05: unit cell from the paper, transistor only).
;;
;; Axes: x = the paper's Y (along the channel), y = the paper's Z (stacking), z = the paper's X (along the word line).
;; Unit cell of the paper: BL pitch 200 nm along the word line = silicon row 100 nm + isolation wall 100 nm (Fig.5a); BL
;; centre to plate centre 275 nm along the channel (WL pitch); one Z pitch. Along the channel the transistor only (BL centre
;; to the end of the N+ source = 25 + 25 + 100 + 25 nm with the 50 nm pillar the WL pitch asks for).
;; In the row the section is that of sde_gt_dvs.cmd. In the wall: oxide, and the two gate layers running on across it
;; (the top view of Fig.2 shows the word lines continuous over the walls and the pillar only inside the row).
;; Pair = "one": the half with z >= 0 of one cell (mirror plane through the middle of the row; AreaFactor 2 in the deck).
;;   Electrodes: bl, sn_v, gs_v (main gate), gd_v (back gate).
;; Pair = "xx": row hammer Case 3 of the paper (X-X', Fig.3(c)): half of the victim row (z = 0 .. 50 nm), the whole wall
;;   (50 .. 150 nm), half of the aggressor row (150 .. 200 nm, mirror plane at 200 nm). The paper: "the WL in this model
;;   is hypothetically decoupled" - here the two gate layers are cut in the middle of the wall by a gap Wcut (not in the
;;   paper; oxide). Both pillars carry the contact bl. Further electrodes: sn_a, gs_a, gd_a.
;; =====================================================================
(sde:clear)
(sdegeo:set-default-boolean "ABA")
(define nm 1e-3)
(define Lg   (* 100 nm))        ; gate length: 100 (Fig.5a)
(define Tb   (* 20 nm))     ; body thickness (Fig.5a)
(define Tox  (* 5.0 nm))       ; gate oxide: 5 (Fig.5a)
(define Tg   (* 20 nm))       ; gate thickness: 20 (Fig.5a)
(define Dv   (* 30 nm))      ; vertical isolation: 30 (Fig.5a)
(define S1   (* 25 nm))      ; BL-side spacer, p body under it
(define S2   (* 25 nm))      ; storage-node-side spacer, N+ source under it
(define Hb   (* 0.5 50 nm))   ; half of the bit-line pillar along the channel
(define Ws   (* 0.5 100 nm))  ; half of the silicon row along the word line: BL pitch - wall = 100 (Fig.5a)
(define Dh   (* 0.5 100 nm))  ; half of the isolation wall: 100 (Fig.5a)
(define Gc   (* 0.5 20 nm))  ; half of the gap that cuts the word line in the wall (xx only; not in the paper)
(define Nsd  1e+20) (define Nch 1e+18) (define Gdi "HfO2") (define Spm "Si3N4")
(define xx? (string=? "xx" "xx"))
(define x1 Hb) (define x2 (+ x1 S1)) (define x3 (+ x2 Lg)) (define x4 (+ x3 S2))
(define y1 (* 0.5 Dv)) (define y2 (+ y1 Tg)) (define y3 (+ y2 Tox)) (define y4 (+ y3 Tb))
(define y5 (+ y4 Tox)) (define y6 (+ y5 Tg)) (define y7 (+ y6 (* 0.5 Dv)))
(define z1 Ws) (define z2 (+ Ws Dh))                 ; row edge, middle of the wall
(define z3 (+ z2 Dh)) (define z4 (+ z3 Ws))          ; xx: aggressor row from z3 to its mirror plane z4
(define zt (if xx? z4 z2))                           ; end of the model along the word line
(define ym (/ (+ y3 y4) 2.0)) (define xg (/ (+ x2 x3) 2.0)) (define zm (/ z1 2.0)) (define zma (/ (+ z3 z4) 2.0))
(define (cub xa ya za xb yb zb mat name) (sdegeo:create-cuboid (position xa ya za) (position xb yb zb) mat name))
(define (win name xa ya za xb yb zb) (sdedr:define-refeval-window name "Cuboid" (position xa ya za) (position xb yb zb)))
(define (cset name r g b) (sdegeo:define-contact-set name 4.0 (color:rgb r g b) "##"))
(define (face-contact name p) (sdegeo:define-3d-contact (find-face-id p) name))
(define (metal-contact name p)
  (sdegeo:set-current-contact-set name)
  (sdegeo:set-contact-boundary-faces (find-body-id p))
  (sdegeo:delete-region (find-body-id p)))

;; ---------------- regions ----------------
(cub 0 0 0 x4 y7 zt "SiO2" "R.Ox")                   ; isolation: between the layers and the wall beside the row
(sdedr:define-constant-profile "CP.Ch" "BoronActiveConcentration" Nch)
(sdedr:define-constant-profile "CP.Nsd" "PhosphorusActiveConcentration" Nsd)
;; one row between za and zb (s = "v" / "a"), its gate layers from ga to gb (they run on into the wall), doping per region
(define (row za zb ga gb s)
  (define (nam n) (string-append n s))
  (define (nav n) (if (string=? s "v") n (string-append n "_a")))      ; the victim keeps the names of the single cell
  (cub 0  0  za x1 y7 zb "Silicon" (nav "R.BL"))     ; bit-line pillar, inside the row only
  (cub x1 y3 za x3 y4 zb "Silicon" (nam "R.Ch_"))    ; floating body: under the BL-side spacer and the gate
  (cub x3 y3 za x4 y4 zb "Silicon" (nam "R.Src_"))   ; source: under the storage-node-side spacer
  (cub x1 y2 za x4 y3 zb Gdi (nam "R.GoxB_")) (cub x1 y4 za x4 y5 zb Gdi (nam "R.GoxT_"))
  (cub x1 y1 za x2 y2 zb Spm (nam "R.SpB1_")) (cub x3 y1 za x4 y2 zb Spm (nam "R.SpB2_"))
  (cub x1 y5 za x2 y6 zb Spm (nam "R.SpT1_")) (cub x3 y5 za x4 y6 zb Spm (nam "R.SpT2_"))
  (cub x2 y1 ga x3 y2 gb "TiN" (nam "M.GB_"))        ; back gate = word-line layer
  (cub x2 y5 ga x3 y6 gb "TiN" (nam "M.GT_"))        ; main gate
  (sdedr:define-constant-profile-region (nav "PL.BL") "CP.Nsd" (nav "R.BL"))
  (sdedr:define-constant-profile-region (nav "PL.Ch") "CP.Ch" (nam "R.Ch_"))
  (sdedr:define-constant-profile-region (nav "PL.Src") "CP.Nsd" (nam "R.Src_")))
(row 0 z1 0 (if xx? (- z2 Gc) z2) "v")
(if xx? (row z3 z4 (+ z2 Gc) z4 "a"))

;; ---------------- contacts ----------------
(cset "bl" 0 0 1)       (face-contact "bl"   (position 0  ym zm))                   ; pillar axis plane
(cset "sn_v" 1 0 0)     (face-contact "sn_v" (position x4 ym zm))                   ; end face of the source
(cset "gs_v" 0 0.6 0)   (metal-contact "gs_v" (position xg (/ (+ y5 y6) 2.0) zm))
(cset "gd_v" 0 0.9 0.3) (metal-contact "gd_v" (position xg (/ (+ y1 y2) 2.0) zm))
(if xx? (begin
  (sdegeo:set-current-contact-set "bl") (face-contact "bl" (position 0 ym zma))     ; the aggressor's pillar: same bias
  (cset "sn_a" 1 0.5 0)   (face-contact "sn_a" (position x4 ym zma))
  (cset "gs_a" 0 0.4 0.4) (metal-contact "gs_a" (position xg (/ (+ y5 y6) 2.0) zma))
  (cset "gd_a" 0.4 0.8 0) (metal-contact "gd_a" (position xg (/ (+ y1 y2) 2.0) zma))))

;; ---------------- mesh (coarser than the 2D section: 3D) ----------------
(win "RW.Glob" 0 0 0 x4 y7 zt)
(sdedr:define-refinement-size "RS.Glob" (* 25 nm) (* 10 nm) (* 25 nm) (* 4 nm) (* 2 nm) (* 5 nm))
(sdedr:define-refinement-placement "RP.Glob" "RS.Glob" "RW.Glob")
(sdedr:define-refinement-size "RS.Ch" (* 5 nm) (* 2.5 nm) (* 10 nm) (* 1 nm) (* 0.3 nm) (* 1 nm))
(sdedr:define-refinement-function "RS.Ch" "MaxLenInt" "Silicon" Gdi (* 0.3 nm) 1.6 "DoubleSide")
(sdedr:define-refinement-function "RS.Ch" "MaxLenInt" "Silicon" "SiO2" (* 1 nm) 1.6)
(sdedr:define-refinement-size "RS.J" (* 1 nm) (* 2.5 nm) (* 10 nm) (* 0.5 nm) (* 0.3 nm) (* 1 nm))
(define (rowmesh za zb wa wb s)                      ; za .. zb = the silicon of the row, wa .. wb = that with 5 nm of the wall
  (win (string-append "RW.Ch_" s) 0 (- y3 Tox) wa x4 (+ y4 Tox) wb)
  (sdedr:define-refinement-placement (string-append "RP.Ch_" s) "RS.Ch" (string-append "RW.Ch_" s))
  (win (string-append "RW.Jd_" s) (- x1 (* 4 nm)) y3 za (+ x1 (* 8 nm)) y4 zb)
  (win (string-append "RW.Js_" s) (- x3 (* 8 nm)) y3 za (+ x3 (* 4 nm)) y4 zb)
  (sdedr:define-refinement-placement (string-append "RP.Jd_" s) "RS.J" (string-append "RW.Jd_" s))
  (sdedr:define-refinement-placement (string-append "RP.Js_" s) "RS.J" (string-append "RW.Js_" s)))
(rowmesh 0 z1 0 (+ z1 (* 5 nm)) "v")
(if xx? (rowmesh z3 z4 (- z3 (* 5 nm)) z4 "a"))

(sde:save-model "g3x_c2h_bnd")
(sde:build-mesh "g3x_c2h")
