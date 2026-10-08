# gt_cs_formula.py : which simple area formulas give the storage capacitances of the paper's text, 3.6 / 4.2 / 5.1 fF for bodies of
# 10 / 20 / 30 nm (Z pitch 90 / 100 / 110 nm), with EOT 3.8 A? The paper says C_S is "calculated using the dimensions defined in Fig. 5(a)"
# and "determined by layer thickness (Z-pitch), lateral capacitance length (L_CAP) and the EOT", and gives no formula.
# Area = a L X + b X Y + c L W + d W X with X, Y lengths that change with the body (Z pitch; node height h = Z - dVOX; g = 2 Tox + Tbody;
# t = Tbody), L = L_CAP = 100 nm, W = row width 100 nm, and a, b, c, d from a list of counts and of multiples of pi. A formula passes if all
# three capacitances round to the text's values. Prints the passing formulas, the plainest first. A search, not a proof: NOTES (by).
import itertools, math
K = 3.9 * 8.854e-18 / 3.8e-4 * 1e-6 * 1e15            # fF per nm2 at EOT 3.8 A: 9.087e-5
TEXT = (3.6, 4.2, 5.1); L = W = 100.0
XS = {"Z": (90, 100, 110), "h": (60, 70, 80), "g": (20, 30, 40), "t": (10, 20, 30)}
CO = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "8": 8, "pi/4": math.pi / 4, "pi/2": math.pi / 2, "pi": math.pi, "2pi": 2 * math.pi, "4pi": 4 * math.pi}
out = []; tried = 0
for (xn, xs), (yn, ys) in itertools.product(XS.items(), repeat=2):
    for (an, a), (bn, b), (cn, c), (dn, d) in itertools.product(CO.items(), repeat=4):
        if a == 0 and b == 0 and d == 0: continue                                          # no dependence on the body at all
        tried += 1
        cs = [K * (a * L * x + b * x * y + c * L * W + d * W * x) for x, y in zip(xs, ys)]
        if all(abs(v - t) < 0.05 for v, t in zip(cs, TEXT)):
            terms = ([f"{an} L {xn}"] if a else []) + ([f"{bn} {xn} {yn}"] if b else []) + ([f"{cn} L W"] if c else []) + ([f"{dn} W {xn}"] if d else [])
            out.append((len(terms), " + ".join(terms), cs))
print(f"{K * 1e4:.4f} fF per face of 100 nm x 100 nm; formulas tried: {tried}; passing: {len(set(f for _, f, _ in out))}")
for n, f, cs in sorted(set((n, f, tuple(round(v, 2) for v in cs)) for n, f, cs in out))[:30]: print(f"  A = {f:44s} -> {cs[0]:.2f} / {cs[1]:.2f} / {cs[2]:.2f} fF")
# the drawn structure of round 32 for comparison (plate sum of tools/gt_cap.py): four faces L x W that do not change, only the inside of the wall grows
print("drawn node (round 32), plate sum: " + " / ".join(f"{K * (2 * L * W + 2 * 10 * W + 2 * (L - 10) * W + (h - 20) * W):.2f}" for h in (60, 70, 80)) + " fF; by AC 4.05 / 4.15 / 4.25")
# the authors' own use of the three values, Fig.5(d): sense margin = (Vdd / 2) C_S / (C_S + C_BL) with no leakage term; C_BL at 64 layers from the 144.14 mV
# the paper prints for the 20 nm body; then what 3.6 and 5.1 fF give at 64 and at 16 layers (to hold against the points of the right graph)
cbl = 4.2 * (0.55 / 0.14414 - 1)
print(f"C_BL at 64 layers from 144.14 mV: {cbl:.2f} fF ({cbl / 64:.3f} fF per layer). Sense margin 10 / 20 / 30 nm at 64 layers: "
      + " / ".join(f"{550 * c / (c + cbl):.1f}" for c in TEXT) + " mV; at 16 layers: " + " / ".join(f"{550 * c / (c + cbl / 4):.1f}" for c in TEXT) + " mV")
print("C_BL / C_S lines of the left graph if C_BL per layer goes with the Z pitch: 10 nm / 20 nm = " + f"{(90 / 3.6) / (100 / 4.2):.3f}, 20 nm / 30 nm = {(100 / 4.2) / (110 / 5.1):.3f}")
assert abs(K * 2 * L * W - 1.817) < 0.005              # two faces of 100 nm x 100 nm are 1.82 fF
