;; =====================================================================
;; sde_gt3a_dvs.cmd - the 3 x 2 x 5 mini array of Cho et al. (Georgia Tech), IRPS 2026, Fig.2: Nrow rows along the word line,
;; two cells per row and layer that share the bit-line pillar, Nlay layers, with the access transistors and the storage
;; capacitors as geometry ("geometrically defined access transistors and capacitors", Fig.2 caption).
;;
;; Axes as in sde_gt3_dvs.cmd: x = the paper's Y (along the channel; BL centre at x = 0, cells at +x and -x), y = the paper's Z
;; (stacking; layer k from k Zp to (k+1) Zp), z = the paper's X (along the word line; rows Wact wide, walls Dhox).
;; From Fig.5(a): Lg, BL pitch = Wact + Dhox, WL pitch WLp = BL centre to capacitor pillar centre (the period along the
;; channel is 2 WLp: both are mirror planes), Dhox, L_CAP, Z pitch = 2 Tox + Tbody + 2 Tg + dVOX. Read off Fig.2 (top view and
;; cross-section, scaled with 2 WLp = 550 nm): the source ends 174 nm from the BL centre; the storage-node box is 200 nm long and
;; centred on the capacitor pillar (L_CAP on either side; the far half belongs to the mirrored neighbour, which has no gates
;; and no BL in the model: unpatterned stack); the node box spans the layer from gate bottom to gate top, ground fins lie in the
;; dVOX levels, a ground finger lies inside the node (U-shaped section); the pillar circle is wider than the row (ratio 1.16),
;; so it parts the two halves of the box; word lines run on across the walls; BL pillars are square and fill the row.
;; Not in the paper (assumed, each a parameter): capacitor pillar radius Rcp, node wall Tcw, dielectric thickness Tcd,
;; outer stack length Xout, margins Zmar, bottom layer Tsub (nitride) and top oxide Ttop.
;; Contacts: bl_<r> (top end of each pillar), wl_<k><s> (both gate plates of layer k on side s = p / m), sn_<r><k><s>
;; (storage node of the cell), gp (capacitor ground: pillars, fins, fingers), snx (the far half boxes of the neighbours).
;; =====================================================================
(sde:clear)
(sdegeo:set-default-boolean "ABA")
(define nm 1e-3)
(define Lg   (* @Lg@ nm))     (define Tb  (* @Tbody@ nm)) (define Tox (* @Tox@ nm)) (define Tg (* @Tgm@ nm)) (define Dv (* @Dvox@ nm))
(define S1   (* @Lsp1@ nm))   (define S2  (* @Lsp2@ nm))  (define Hb  (* 0.5 @Wbl@ nm))
(define Wa   (* @Wact@ nm))   (define Dh  (* @Dhox@ nm))
(define WLp  (* @WLp@ nm))    (define Lcap (* @Lcap@ nm)) (define Tcd (* @Tcd@ nm)) (define Tcw (* @Tcw@ nm)) (define Rcp (* @Rcp@ nm))
(define Xout (* @Xout@ nm))   (define Zmar (* @Zmar@ nm)) (define Tsub (* @Tsub@ nm)) (define Ttop (* @Ttop@ nm))
(define Nrow @Nrow@) (define Nlay @Nlay@)
(define Nsd  @Nsd@) (define Nch @Nch@) (define Gdi "@Gdi@") (define Spm "@Spm@")
(define Zp (+ Dv (* 2 Tg) (* 2 Tox) Tb)) (define H (* Nlay Zp))
(define x1 Hb) (define x2 (+ x1 S1)) (define x3 (+ x2 Lg)) (define x4 (+ x3 S2))
(define xc WLp) (define x5 (+ xc Lcap)) (define Xt (+ x5 Xout))      ; capacitor pillar centre, far end of the node box, end of the model
(define y1 (* 0.5 Dv)) (define y2 (+ y1 Tg)) (define y3 (+ y2 Tox)) (define y4 (+ y3 Tb)) (define y5 (+ y4 Tox)) (define y6 (+ y5 Tg))
(define Zt (+ (* 2 Zmar) (* Nrow Wa) (* (+ Nrow 1) Dh)))
(define (zrow r) (+ Zmar Dh (* r (+ Wa Dh))))
(define (num i) (number->string i))
(define (cub xa ya za xb yb zb mat name) (sdegeo:create-cuboid (position xa ya za) (position xb yb zb) mat name))
(define (cset name r g b) (sdegeo:define-contact-set name 4.0 (color:rgb r g b) "##"))
(define (metal-contact name p)
  (sdegeo:set-current-contact-set name)
  (sdegeo:set-contact-boundary-faces (find-body-id p))
  (sdegeo:delete-region (find-body-id p)))
(define (loop i n f) (if (< i n) (begin (f i) (loop (+ i 1) n f))))

(sdedr:define-constant-profile "CP.Ch" "BoronActiveConcentration" Nch)
(sdedr:define-constant-profile "CP.Nsd" "PhosphorusActiveConcentration" Nsd)
(define (dope prof reg) (sdedr:define-constant-profile-region (string-append "PL." reg) prof reg))
(cset "gp" 0.2 0.8 0.9) (cset "snx" 0.6 0.4 0)

;; ---------------- isolation, bottom layer ----------------
(cub (- Xt) (- Tsub) 0 Xt (+ H Ttop) Zt "SiO2" "R.Ox")
(cub (- Xt) (- Tsub) 0 Xt 0 Zt "Si3N4" "R.Sub")

;; ---------------- one cell: side sg (+1 / -1, tag s), row r (silicon from za to zb), layer k ----------------
(define (cell sg s r k za zb)
  (define yo (* k Zp)) (define id (string-append (num r) (num k) s)) (define zc (* 0.5 (+ za zb)))
  (define (X v) (* sg v)) (define (Y v) (+ yo v))
  (define (bx xa ya xb yb mat name) (cub (X xa) (Y ya) za (X xb) (Y yb) zb mat (string-append name id)))
  (define (bz xa ya xb yb in mat name) (cub (X xa) (Y ya) (+ za in) (X xb) (Y yb) (- zb in) mat (string-append name id)))
  ;; access transistor (the section of sde_gt_dvs.cmd)
  (bx x1 y3 x3 y4 "Silicon" "R.Ch_") (bx x3 y3 x4 y4 "Silicon" "R.Src_")
  (bx x1 y2 x4 y3 Gdi "R.GoxB_") (bx x1 y4 x4 y5 Gdi "R.GoxT_")
  (bx x1 y1 x2 y2 Spm "R.SpB1_") (bx x3 y1 x4 y2 Spm "R.SpB2_") (bx x1 y5 x2 y6 Spm "R.SpT1_") (bx x3 y5 x4 y6 Spm "R.SpT2_")
  (dope "CP.Ch" (string-append "R.Ch_" id)) (dope "CP.Nsd" (string-append "R.Src_" id))
  ;; the unpatterned stack beyond the far half of the node box: silicon layer between gate-dielectric skins and spacer material
  (bx x5 y1 Xt y6 Spm "R.DuS_") (bx x5 y2 Xt y5 Gdi "R.DuG_") (bx x5 y3 Xt y4 "Silicon" "R.Dum_")
  (dope "CP.Ch" (string-append "R.Dum_" id))
  ;; storage capacitor: dielectric around the node, the node box in two halves (cell / mirrored neighbour), inside it dielectric and
  ;; the ground finger; each in two halves, so that the pillar leaves every body in one piece
  (bx x4 (- y1 Tcd) xc (+ y6 Tcd) "Insulator1" "R.CdA_") (bx xc (- y1 Tcd) x5 (+ y6 Tcd) "Insulator1" "R.CdB_")
  (bx x4 y1 xc y6 "TiN" "M.SnA_") (bx xc y1 x5 y6 "TiN" "M.SnB_")
  (bz (+ x4 Tcw) (+ y1 Tcw) xc (- y6 Tcw) Tcw "Insulator1" "R.CiA_") (bz xc (+ y1 Tcw) (- x5 Tcw) (- y6 Tcw) Tcw "Insulator1" "R.CiB_")
  (bz (+ x4 Tcw Tcd) (+ y1 Tcw Tcd) xc (- y6 Tcw Tcd) (+ Tcw Tcd) "TiN" "M.GfA_")
  (bz xc (+ y1 Tcw Tcd) (- x5 Tcw Tcd) (- y6 Tcw Tcd) (+ Tcw Tcd) "TiN" "M.GfB_"))

;; ground fins of one row and side in the dVOX levels: level j lies under layer j (j = Nlay: above the top layer)
(define (fin sg s r j za zb)
  (define ya (if (= j 0) 0 (+ (* (- j 1) Zp) y6 Tcd))) (define yb (if (= j Nlay) H (+ (* j Zp) y1 (- Tcd))))
  (define id (string-append (num r) (num j) s))
  (cub (* sg x4) ya za (* sg xc) yb zb "TiN" (string-append "M.GpA_" id)) (cub (* sg xc) ya za (* sg x5) yb zb "TiN" (string-append "M.GpB_" id)))

(define (side sg s)
  (loop 0 Nrow (lambda (r)
    (define za (zrow r)) (define zb (+ za Wa)) (define zc (* 0.5 (+ za zb))) (define rs (string-append (num r) s))
    (loop 0 (+ Nlay 1) (lambda (j) (fin sg s r j za zb)))
    (loop 0 Nlay (lambda (k) (cell sg s r k za zb)))
    ;; capacitor pillar: dielectric shell and ground core through all layers and the top oxide
    (sdegeo:create-cylinder (position (* sg xc) 0 zc) (position (* sg xc) (+ H Ttop) zc) Rcp "Insulator1" (string-append "R.CpD_" rs))
    (sdegeo:create-cylinder (position (* sg xc) 0 zc) (position (* sg xc) (+ H Ttop) zc) (- Rcp Tcd) "TiN" (string-append "M.Gc_" rs))))
  ;; word lines: the two gate plates of every layer, across all rows and walls
  (loop 0 Nlay (lambda (k)
    (define yo (* k Zp)) (define ks (string-append (num k) s))
    (cub (* sg x2) (+ yo y1) 0 (* sg x3) (+ yo y2) Zt "TiN" (string-append "M.WlB_" ks))
    (cub (* sg x2) (+ yo y5) 0 (* sg x3) (+ yo y6) Zt "TiN" (string-append "M.WlT_" ks)))))
(side 1 "p") (side -1 "m")

;; bit-line pillars: square, the width of the row, from the bottom layer to the top surface
(loop 0 Nrow (lambda (r)
  (define za (zrow r))
  (cub (- Hb) 0 za Hb (+ H Ttop) (+ za Wa) "Silicon" (string-append "R.BL_" (num r)))
  (dope "CP.Nsd" (string-append "R.BL_" (num r)))))

;; ---------------- contacts ----------------
;; Every metal body becomes a contact: its faces are marked and the body is deleted. One call per contact name with all its bodies
;; (a call per body took 30 - 85 s each in the full array: 208 bodies).
(define (metal-contacts name pts)
  (define b (apply append (map find-body-id pts)))
  (sdegeo:set-current-contact-set name) (sdegeo:set-contact-boundary-faces b) (sdegeo:delete-region b))
(define gpP '()) (define snxP '())
(define (contacts sg s)
  (define xg (* sg 0.5 (+ x2 x3)))
  (loop 0 Nlay (lambda (k)
    (define yo (* k Zp)) (define wl (string-append "wl_" (num k) s))
    (cset wl 0 0.6 0.2)
    (metal-contacts wl (list (position xg (+ yo (* 0.5 (+ y1 y2))) (* 0.5 Zt)) (position xg (+ yo (* 0.5 (+ y5 y6))) (* 0.5 Zt))))))
  (loop 0 Nrow (lambda (r)
    (define zc (+ (zrow r) (* 0.5 Wa)))
    (loop 0 Nlay (lambda (k)
      (define ym (+ (* k Zp) (* 0.5 (+ y3 y4)))) (define sn (string-append "sn_" (num r) (num k) s))
      (cset sn 1 0.6 0)
      (metal-contacts sn (list (position (* sg (+ x4 (* 0.5 Tcw))) ym zc)))
      (set! snxP (cons (position (* sg (- x5 (* 0.5 Tcw))) ym zc) snxP))
      (set! gpP (cons (position (* sg (+ x4 Tcw Tcd (* 2 nm))) ym zc) (cons (position (* sg (- x5 Tcw Tcd (* 2 nm))) ym zc) gpP)))))
    (loop 0 (+ Nlay 1) (lambda (j)
      (define yf (if (= j 0) (* 0.5 (- y1 Tcd)) (if (= j Nlay) (- H (* 0.5 (- y1 Tcd))) (* j Zp))))
      (set! gpP (cons (position (* sg (+ x4 (* 2 nm))) yf zc) (cons (position (* sg (- x5 (* 2 nm))) yf zc) gpP)))))
    (set! gpP (cons (position (* sg xc) (* 0.5 H) zc) gpP)))))
(contacts 1 "p") (contacts -1 "m")
(metal-contacts "snx" snxP) (metal-contacts "gp" gpP)
(loop 0 Nrow (lambda (r)
  (define bl (string-append "bl_" (num r)))
  (cset bl 0 0 1)
  (sdegeo:define-3d-contact (find-face-id (position 0 (+ H Ttop) (+ (zrow r) (* 0.5 Wa)))) bl)))

;; ---------------- mesh: Mg = coarse everywhere (structure and capacitance), finer in the silicon ----------------
(sdedr:define-refeval-window "RW.Glob" "Cuboid" (position (- Xt) (- Tsub) 0) (position Xt (+ H Ttop) Zt))
(sdedr:define-refinement-size "RS.Glob" (* 50 nm) (* 25 nm) (* 50 nm) (* 10 nm) (* 4 nm) (* 10 nm))
(sdedr:define-refinement-placement "RP.Glob" "RS.Glob" "RW.Glob")
(sdedr:define-refinement-size "RS.Si" (* 12.5 nm) (* 5 nm) (* 25 nm) (* 5 nm) (* 2.5 nm) (* 10 nm))
(sdedr:define-refinement-material "RP.Si" "RS.Si" "Silicon")

(sde:save-model "n@node@_bnd")
(sde:build-mesh "n@node@")
