# repro_rate.py <config tag> ... : share of the paper's scored numbers (tools/paper_targets.py) that a configuration has inside
# its tolerance (|simulated - paper| / tolerance <= 1), per figure group and in all. Reads the item lists score2d.py makes its
# rms from; prints them so that every count can be checked by eye, and the worst item of each group (MEASURE.md: no average
# without the largest deviation). Each group carries its kind (MEASURE.md, section 2):
#   cal  = a model value was fixed with these numbers (gate dielectric, Hurkx A / B, temperature, mobility model; storage capacitor)
#   cond = put in as a condition (the hole charge sized to the bars of Fig.8(a))
#   pred = nothing was fitted to them: what the model predicts once the values above are set
# Denominators (Codex review 2026-10-09; plan P0): the list is fixed as `legacy52` (LEGACY below, 52 items). An item is
#   pass / fail      = scored from the configuration's own run;
#   missing          = its run is not there or not complete (never dropped from the denominator);
#   stand-in         = score2d took a baseline run in place of the configuration's own (score2d.first): not counted as a pass.
# The rate is passes / 52; passes / (own items scored) is printed next to it. Items added since (Fig.7(e), X-X', the natural initial state,
# Ion C3 -> C5, sentence checks) are a separate list with its own denominator (results folder: target registry), not mixed into legacy52.
import sys
import score2d as S
NAMES = [("IV Fig.5(c)", "cal"), ("W  Fig.4(a)", "cal"), ("BR Fig.8(a)", "cond"), ("L1 Fig.8(b)", "pred"), ("L2 Fig.8(c)", "pred"), ("RH Fig.6(e)", "pred"), ("RI Fig.7   ", "pred")]
LEGACY = [28, 4, 5, 5, 5, 2, 3]       # items per group when everything is there: IV 5 cases x (v10 v8 v6 lm1 ss) + l1 of Cases 1, 4, 5
W_PRED = ("fin7", "fin6t", "pt")       # configurations whose capacitor is the paper's text value: nothing is fitted to Fig.4(a), the write is a prediction
assert sum(LEGACY) == 52


def groups(tag):
    """[(items, stand_in)] per group of NAMES, in order."""
    got, out = [], []
    _rms = S.rms
    S.rms = lambda e: (got.append(list(e)), _rms(e))[1]
    try:
        for fn in (S.iv, S.write, S.fbe, S.rh):
            S.FB.clear(); n0 = len(got); fn(tag); sub = any(S.FB)
            out += [(e, sub) for e in got[n0:]]
    finally:
        S.rms = _rms
    assert len(out) == len(NAMES), f"{tag}: {len(out)} groups scored, {len(NAMES)} expected"
    return out


def count(tag, gs):
    """Per group: (name, kind, pass, fail, missing, stand_in, worst, items); fixed denominator LEGACY."""
    rows = []
    for (name, kind), (e, sub), n in zip(NAMES, gs, LEGACY):
        if name.startswith("W ") and tag in W_PRED: kind = "pred"
        k = 0 if sub else sum(abs(x) <= 1 for x in e)
        rows.append((name, kind, k, 0 if sub else len(e) - k, n - len(e), len(e) if sub else 0, max(e, key=abs) if e else None, e))
    return rows


def main(tags):
    for tag in tags:
        rows = count(tag, groups(tag)); print(tag)
        for name, kind, ok, bad, mis, sub, worst, e in rows:
            st = f"{ok:2d} pass {bad:2d} fail" + (f" {mis:2d} missing" if mis else "") + (f" {sub:2d} stand-in" if sub else "")
            w = "" if worst is None else f"  worst {worst:+6.2f} | " + " ".join(f"{x:+.2f}" for x in e)
            print(f"  {name} {kind:4s} {ok:2d} / {ok + bad + mis + sub:2d}  ({st}){w}")
        ok = sum(r[2] for r in rows); own = sum(r[2] + r[3] for r in rows); mis = sum(r[4] for r in rows); sub = sum(r[5] for r in rows)
        kinds = {}
        for r in rows: a, b = kinds.get(r[1], (0, 0)); kinds[r[1]] = (a + r[2], b + r[2] + r[3] + r[4] + r[5])
        print(f"  legacy52: {ok} / 52 = {100 * ok / 52:.1f} %   (own items scored {own}: {ok} / {own} = {100 * ok / own:.1f} %; missing {mis}, stand-in {sub})   |   "
              + "   ".join(f"{k} {a} / {b}" for k, (a, b) in kinds.items()))


def selfcheck():
    """A missing group stays in the denominator, a stand-in group is not a pass."""
    gs = [([0.5] * 28, False), ([2.0] * 4, False), ([0.1] * 5, True), ([0.5] * 5, False), ([], False), ([0.5, 3.0], False), ([0.5] * 3, False)]
    rows = count("x", gs); ok = sum(r[2] for r in rows)
    assert ok == 28 + 5 + 1 + 3 and rows[2][5] == 5 and rows[4][4] == 5 and sum(r[2] + r[3] + r[4] + r[5] for r in rows) == 52


if __name__ == "__main__":
    selfcheck()
    main(sys.argv[1:])
