# repro_rate.py <config tag> ... : share of the paper's scored numbers (tools/paper_targets.py) that a configuration has inside
# its tolerance (|simulated - paper| / tolerance <= 1), per figure group and in all. Reads the item lists score2d.py makes its
# rms from; prints them so that every count can be checked by eye, and the worst item of each group (MEASURE.md: no average
# without the largest deviation). Each group carries its kind (MEASURE.md, section 2):
#   cal  = a model value was fixed with these numbers (gate dielectric, Hurkx A / B, temperature, mobility model; storage capacitor)
#   cond = put in as a condition (the hole charge sized to the bars of Fig.8(a))
#   pred = nothing was fitted to them: what the model predicts once the values above are set
import sys
import score2d as S
NAMES = [("IV Fig.5(c)", "cal"), ("W  Fig.4(a)", "cal"), ("BR Fig.8(a)", "cond"), ("L1 Fig.8(b)", "pred"), ("L2 Fig.8(c)", "pred"), ("RH Fig.6(e)", "pred"), ("RI Fig.7   ", "pred")]
got = []
_rms = S.rms
S.rms = lambda e: (got.append(list(e)), _rms(e))[1]
for tag in sys.argv[1:]:
    got.clear()
    S.iv(tag); S.write(tag); S.fbe(tag); S.rh(tag)
    assert len(got) == len(NAMES), f"{tag}: {len(got)} groups scored, {len(NAMES)} expected (a run is missing)"
    print(tag)
    n = {}; shares = []
    for (name, kind), e in zip(NAMES, got):
        k = sum(abs(x) <= 1 for x in e); a, b = n.get(kind, (0, 0)); n[kind] = (a + k, b + len(e)); shares.append(k / len(e))
        print(f"  {name} {kind:4s} {k:2d} / {len(e):2d} = {100 * k / len(e):5.1f} %  worst {max(e, key=abs):+6.2f} | " + " ".join(f"{x:+.2f}" for x in e))
    ok, tot = sum(a for a, b in n.values()), sum(b for a, b in n.values())
    print(f"  all items   {ok} / {tot} = {100 * ok / tot:.1f} %   mean of the seven figure groups {100 * sum(shares) / len(shares):.1f} %   |   "
          + "   ".join(f"{kind} {a} / {b} = {100 * a / b:.1f} %" for kind, (a, b) in n.items()))
