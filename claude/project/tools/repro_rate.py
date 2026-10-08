# repro_rate.py <config tag> ... : share of the paper's scored numbers (tools/paper_targets.py) that a configuration has inside
# its tolerance (|simulated - paper| / tolerance <= 1), per figure group and in all. Reads the item lists score2d.py makes its
# rms from; prints them so that every count can be checked by eye.
import sys
import score2d as S
NAMES = ["IV Fig.5(c)", "W  Fig.4(a)", "BR Fig.8(a)", "L1 Fig.8(b)", "L2 Fig.8(c)", "RH Fig.6(e)", "RI Fig.7"]
got = []
_rms = S.rms
S.rms = lambda e: (got.append(list(e)), _rms(e))[1]
for tag in sys.argv[1:]:
    got.clear()
    S.iv(tag); S.write(tag); S.fbe(tag); S.rh(tag)
    assert len(got) == len(NAMES), f"{tag}: {len(got)} groups scored, {len(NAMES)} expected (a run is missing)"
    print(tag)
    tot = ok = 0; shares = []
    for n, e in zip(NAMES, got):
        k = sum(abs(x) <= 1 for x in e); tot += len(e); ok += k; shares.append(k / len(e))
        print(f"  {n}  {k:2d} / {len(e):2d} = {100 * k / len(e):5.1f} %   " + " ".join(f"{x:+.2f}" for x in e))
    print(f"  all items   {ok} / {tot} = {100 * ok / tot:.1f} %   mean of the seven figure groups {100 * sum(shares) / len(shares):.1f} %")
