;; =====================================================================
;; sde_gt_dvs.cmd — one cell of the 3D stackable 1T1C DRAM model of Cho et al. (Georgia Tech),
;; "Row Hammer Effect and Floating Body Effect of Monolithic 3D Stackable 1T1C DRAM", IRPS 2026.
;;
;; 2D section along the channel (the paper's Y-Z plane; here x = Y, y = Z), drawn like the single-cell view of its
;; Fig.2 (the same drawing is the inset "TCAD for Si access transistor" of Fig.2(c) in Hsu .. Yu, IMW 2025).
;; The paper's model is 3D; the access transistor is a double-gate device (main gate above, back gate below the
;; body) that does not change along the word line, so this section carries its Id-Vg.
;; Left to right: half of the N+ bit-line pillar (drain) | p body under the BL-side spacer | p body under the gate |
;; N+ source under the storage-node-side spacer | source contact (the metal block "Source" of the drawing; the
;; storage node in the array). The gate dielectric runs along the silicon under both spacers.
;;
;; From the paper (Fig.5a, text): Lg, body thickness, gate oxide, gate thickness, vertical isolation, S/D 1e20,
;; channel 1e16 .. 1e18, same work function on both gates. Read from the drawing (not stated): spacer lengths,
;; bit-line pillar width, which silicon is n and which is p, a spacer material other than the isolation oxide.
;; Abrupt junctions (the paper gives no profile).
;; Pair = "one": this cell alone. "yy": two cells across the bit line (row hammer Case 1, Y-Y'), victim left, aggressor
;; right. "zz": two layers on one side of the bit line (Case 2, Z-Z'), victim below, aggressor above.
;; Bgc = 1: contact "body_v" in the middle of the victim body (the hypothetical grounded body of Fig.7(b)).
;; Storage capacitor: lumped in the decks (Cap = "lump") or drawn as in the cross-section of Fig.2 (Cap = "u" / "blk", single cells only).
;; Not in this section: the third dimension (Case 3, X-X').
;; Electrodes: bl, sn_v, gs_v (main gate), gd_v (back gate) of the victim; sn_a, gs_a, gd_a of the aggressor; gp_v = ground of the
;; drawn capacitor (plates, finger, pillar).
;; =====================================================================
(sde:clear)
(sdegeo:set-default-boolean "ABA")
(define nm 1e-3)
(define Lg   (* 100 nm))        ; gate length: 100 (Fig.5a)
(define Tb   (* 20 nm))     ; body thickness: 30 / 20 / 10 (Fig.5a)
(define Tox  (* 5.0 nm))       ; gate oxide: 5 (Fig.5a)
(define Tg   (* 20 nm))       ; gate thickness: 20 (Fig.5a)
(define Dv   (* 30 nm))      ; vertical isolation: 30 (Fig.5a); half of it above and below each cell
(define S1   (* 25 nm))      ; BL-side spacer: gate to bit-line pillar, p body under it (Fig.2)
(define S2   (* 25 nm))      ; storage-node-side spacer, N+ source under it (Fig.2)
(define Hb   (* 0.5 100 nm))   ; half of the bit-line pillar (Fig.2)
(define Nsd  1e+20)              ; source and drain (BL): 1e20
(define Nch  1e+18)              ; channel: 1e18 / 1e16
(define Gdi  "HfO2")            ; gate dielectric material ("gate oxide" in Fig.5a): SiO2 or HfO2
(define Spm  "Si3N4")            ; spacer material (its own colour in Fig.2)
(define Pair "one")           ; one / yy / zz (see the header)
(define Bgc  0)              ; 1 = body contact in the victim
(define Blc  "bot")            ; BL contact: "axis" = on the pillar axis ("yy": top end of the pillar), "bot" = bottom end of the pillar
(define Cap  "u")            ; storage node: lump (capacitor in the deck) / u / blk (a structure, see below)
(define Lcap (* 100 nm))      ; storage capacitance length L_CAP: 100 (Fig.5a)
(define Ceot 3.8)             ; EOT of the capacitor dielectric [A]: 3.8 (Fig.5a); the permittivity in the parameter file follows from it
(define Tcd  (* 4 nm))       ; capacitor dielectric thickness (Hsu .. Yu: 4)
(define Tcw  (* 10 nm))       ; wall and arms of the U-shaped storage node (Fig.2 drawing)
(define yy? (string=? Pair "yy")) (define zz? (string=? Pair "zz")) (define lump? (string=? Cap "lump"))
(define Lc (+ S1 Lg S2))                          ; cell length from the pillar face
(define Lx (+ Lc (if lump? 0 (+ Lcap Tcd (* 10 nm)))))      ; the same with the capacitor and a 10 nm strip of the ground pillar
(define Zp (+ (* 2 Tox) Tb (* 2 Tg) Dv))          ; Z pitch = 2 Tox + Tbody + 2 Tg + Dvox
(define xb0 (if yy? Lx 0))                        ; pillar: the whole of it between two cells, else its right half
(define xb1 (+ xb0 (if yy? (* 2 Hb) Hb)))
(define xmax (+ xb1 Lx)) (define ymax (if zz? (* 2 Zp) Zp))
(define (box xa ya xb yb mat name) (sdegeo:create-rectangle (position xa ya 0) (position xb yb 0) mat name))
(define (win name xa ya xb yb) (sdedr:define-refeval-window name "Rectangle" (position xa ya 0) (position xb yb 0)))
(define (cset name r g b) (sdegeo:define-contact-set name 4.0 (color:rgb r g b) "##"))
(define (edge-contact name p) (sdegeo:define-2d-contact (find-edge-id p) name))
(define (metal-contact name p)
  (sdegeo:set-current-contact-set name)
  (sdegeo:set-contact-boundary-edges (find-body-id p))
  (sdegeo:delete-region (find-body-id p)))

;; ---------------- background, pillar, doping levels, mesh sizes ----------------
(box 0   0 xmax ymax "SiO2"    "R.Ox")    ; isolation oxide between the layers
(box xb0 0 xb1  ymax "Silicon" "R.BL")    ; bit-line pillar, runs through all layers
;; doping per region: with coordinate windows the vertices on a region boundary all took the N+ value, which put each
;; junction up to 0.4 nm inside the body, and the boron background made the N+ level 9.9e19 instead of 1e20
(sdedr:define-constant-profile "CP.Ch" "BoronActiveConcentration" Nch)
(sdedr:define-constant-profile "CP.Nsd" "PhosphorusActiveConcentration" Nsd)
(sdedr:define-constant-profile-region "PL.BL" "CP.Nsd" "R.BL")
(win "RW.Glob" 0 0 xmax ymax)
(sdedr:define-refinement-size "RS.Glob" (* 10 nm) (* 5 nm) (* 1 nm) (* 0.5 nm))
(sdedr:define-refinement-placement "RP.Glob" "RS.Glob" "RW.Glob")
(sdedr:define-refinement-function "RS.Glob" "DopingConcentration" "MaxTransDiff" 1)
;; body and source: Mc (2) nm along the channel, Mv (1) nm across, Mi (0.2) nm at the gate dielectric; Mj (0.5) nm at the two
;; abrupt junctions (in brackets the mesh of all gr_ structures; the gq_ structures vary it)
(sdedr:define-refinement-size "RS.Ch" (* 2 nm) (* 1 nm) (* (min 2 0.2) nm) (* 0.2 nm))
(sdedr:define-refinement-function "RS.Ch" "MaxLenInt" "Silicon" "SiO2" (* 0.2 nm) 1.4 "DoubleSide")
(if (string=? Gdi "SiO2") 0 (sdedr:define-refinement-function "RS.Ch" "MaxLenInt" "Silicon" Gdi (* 0.2 nm) 1.4 "DoubleSide"))
(sdedr:define-refinement-size "RS.J" (* 0.5 nm) (* 1 nm) (* (min 0.5 0.2) nm) (* 0.2 nm))
(sdedr:define-refinement-size "RS.Cap" (* 2 nm) (* 2 nm) (* 1 nm) (* 1 nm))      ; capacitor dielectric: two cells across its thickness
(cset "bl" 0 0 1)

;; ---------------- one cell ----------------
;; xf = pillar face it starts from, d = +1 (cell to the right) or -1, yb = bottom of its layer, s = "v" victim / "a" aggressor.
;; u = distance from the pillar face: spacer 0..S1 (p body under it), gate S1..S1+Lg, spacer and N+ source up to Lc.
(define (cell xf d yb s)
  (define (X u) (+ xf (* d u)))
  (define y1 (+ yb (* 0.5 Dv))) (define y2 (+ y1 Tg)) (define y3 (+ y2 Tox)) (define y4 (+ y3 Tb))
  (define y5 (+ y4 Tox)) (define y6 (+ y5 Tg)) (define ym (/ (+ y3 y4) 2.0))
  (define ug (+ S1 Lg)) (define xg (X (+ S1 (/ Lg 2.0))))
  (define (bx ua ya ub yc mat name) (box (min (X ua) (X ub)) ya (max (X ua) (X ub)) yc mat (string-append name s)))
  (define (wn name ua ya ub yc) (win (string-append name s) (min (X ua) (X ub)) ya (max (X ua) (X ub)) yc))
  (bx 0  y3 ug y4 "Silicon" "R.Ch_")      ; floating body: under the BL-side spacer and the gate
  (bx ug y3 Lc y4 "Silicon" "R.Src_")     ; source: under the storage-node-side spacer
  (bx 0  y2 Lc y3 Gdi       "R.GoxB_")    ; gate dielectric, along the silicon under both spacers
  (bx 0  y4 Lc y5 Gdi       "R.GoxT_")
  (bx 0 y1 S1 y2 Spm "R.SpB1_") (bx ug y1 Lc y2 Spm "R.SpB2_")     ; spacers at the back-gate level
  (bx 0 y5 S1 y6 Spm "R.SpT1_") (bx ug y5 Lc y6 Spm "R.SpT2_")     ; and at the main-gate level
  (bx S1 y1 ug y2 "TiN" "M.GB_")          ; back gate
  (bx S1 y5 ug y6 "TiN" "M.GT_")          ; main gate
  (sdedr:define-constant-profile-region (string-append "PL.Ch_" s) "CP.Ch" (string-append "R.Ch_" s))
  (sdedr:define-constant-profile-region (string-append "PL.Src_" s) "CP.Nsd" (string-append "R.Src_" s))
  (cset (string-append "sn_" s) 1 0 0)
  ;; Storage node. "lump": contact on the end face of the source, the capacitor is a circuit element of the deck. Otherwise the capacitor of
  ;; the Fig.2 cross-section: node on the end face of the source, as high as the gate stack (y1 .. y6) and L_CAP long; ground = plates at
  ;; the isolation level above and below, the pillar (a 10 nm strip of it) and, in "u", a finger inside the node, which is then U-shaped
  ;; and open towards the pillar; dielectric Tcd between node and ground. Node and ground are contacts (their metal is removed).
  (if lump? (edge-contact (string-append "sn_" s) (position (X Lc) ym 0))
    (let* ((a3 (+ Lc Lcap)) (xr (+ a3 Tcd)))                                  ; end of the node, face of the ground pillar
      (cset (string-append "gp_" s) 0.3 0.3 0.3)
      (bx Lc yb Lx (+ yb Zp) "TiN" "M.Gp_")                                  ; ground: what the next boxes leave of it = two plates + pillar strip
      (bx Lc (- y1 Tcd) xr (+ y6 Tcd) "Insulator1" "R.Cd_")                   ; dielectric around the node
      (bx Lc y1 a3 y6 "TiN" "M.Sn_")                                          ; node
      (if (string=? Cap "u") (begin
        (bx (+ Lc Tcw) (+ y1 Tcw) xr (- y6 Tcw) "Insulator1" "R.Cdi_")        ; inside of the U, lined with dielectric
        (bx (+ Lc Tcw Tcd) (+ y1 Tcw Tcd) xr (- y6 Tcw Tcd) "TiN" "M.Gf_")    ; ground finger
        (metal-contact (string-append "gp_" s) (position (X (- xr nm)) ym 0))))
      (metal-contact (string-append "gp_" s) (position (X (- Lx nm)) (+ yb nm) 0))
      (metal-contact (string-append "sn_" s) (position (X (+ Lc nm)) ym 0))
      (wn "RW.Cap_" Lc yb Lx (+ yb Zp))
      (sdedr:define-refinement-placement (string-append "RP.Cap_" s) "RS.Cap" (string-append "RW.Cap_" s))))
  (cset (string-append "gs_" s) 0 0.6 0)   (metal-contact (string-append "gs_" s) (position xg (/ (+ y5 y6) 2.0) 0))
  (cset (string-append "gd_" s) 0 0.9 0.3) (metal-contact (string-append "gd_" s) (position xg (/ (+ y1 y2) 2.0) 0))
  (if (= Bgc 1) (if (string=? s "v") (begin                 ; 20 nm x 2 nm contact slot in the middle of the body, under the gate centre
    (bx (+ S1 (* 0.4 Lg)) (- ym nm) (+ S1 (* 0.6 Lg)) (+ ym nm) "TiN" "M.Bg_")
    (cset "body_v" 0.5 0 0.5) (metal-contact "body_v" (position xg ym 0)))))
  (wn "RW.Ch_" (* -10 nm) (- y3 Tox) Lc (+ y4 Tox))
  (sdedr:define-refinement-placement (string-append "RP.Ch_" s) "RS.Ch" (string-append "RW.Ch_" s))
  (wn "RW.Jd_" (* -6 nm) y3 (* 10 nm) y4) (wn "RW.Js_" (- ug (* 10 nm)) y3 (+ ug (* 6 nm)) y4)
  (sdedr:define-refinement-placement (string-append "RP.Jd_" s) "RS.J" (string-append "RW.Jd_" s))
  (sdedr:define-refinement-placement (string-append "RP.Js_" s) "RS.J" (string-append "RW.Js_" s)))

(cell xb1 1 0 (if yy? "a" "v"))           ; the cell right of the pillar: the victim, in "yy" the aggressor
(if yy? (cell xb0 -1 0 "v"))              ; victim left of the pillar
(if zz? (cell xb1 1 Zp "a"))              ; aggressor one layer up
(if (string=? Blc "bot") (edge-contact "bl" (position (* 0.5 (+ xb0 xb1)) 0 0))   ; bottom end of the pillar (below the victim in "zz")
    (if yy? (edge-contact "bl" (position (+ xb0 Hb) ymax 0))      ; top end of the pillar
            (edge-contact "bl" (position 0 (* 0.5 Zp) 0))))       ; pillar axis

(sde:save-model "gs_c2hb_bnd")
(sde:build-mesh "gs_c2hb")
