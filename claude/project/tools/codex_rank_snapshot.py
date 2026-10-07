# codex_rank_snapshot.py <folder with Codex's result files F3C*_c*.json> <out.json> : Codex's fin3 factorial (720 runs), ranked from a copy
# of its result files with the rule of its own rank.py (codex_updates/fin3_factorial_20261007/rank.py on origin/main): a group = the five
# cases of one condition; only successful results count; max_score = the largest of the three scores (body, first, loss200) over the five
# cases; all_cases_pass = every case has all of its Fig.8 metrics inside Codex's tolerances. The result files are Codex's: they are read,
# not changed; the output says where and when they were read. Used by tools/make_eliu_report_full.py when origin/main is behind the server.
import sys, os, json, glob, collections, datetime
src, out = sys.argv[1], sys.argv[2]; groups = collections.defaultdict(list); n = bad = 0
for f in sorted(glob.glob(os.path.join(src, "*.json"))):
    try: o = json.load(open(f, encoding="utf-8"))
    except Exception: bad += 1; continue
    n += 1
    if o.get("success"): groups[o["group"]].append(o)
rank = [dict(group=g, preparation=rs[0]["preparation"], factor=rs[0]["preparation_factor"], window=rs[0]["source_window"], SN=rs[0]["SN_protocol"], II=rs[0]["II"], Cs=rs[0]["Cs_basis"],
             max_score=max(max(r["scores"].values()) for r in rs), all_cases_pass=all(r["all_five_figure8_metrics_for_this_case"] for r in rs),
             SN_precondition_all_pass=all(r["SN_prefall_within_5mV"] for r in rs), cases=sorted(rs, key=lambda x: x["case"])) for g, rs in groups.items() if len(rs) == 5]
rank.sort(key=lambda r: r["max_score"])
json.dump(dict(read_at=datetime.datetime.now().astimezone().isoformat(timespec="seconds"), source="sogangic1:~/vblhwl_3d_dram/codex_validation/fin3_factorial_20261007/results (Codex's files, read only)",
               result_files=n, unreadable=bad, successful=sum(len(v) for v in groups.values()), complete_groups=len(rank), baseline="fin3", ranking=rank), open(out, "w", encoding="utf-8"), indent=1)
print(f"result files {n} (unreadable {bad}), successful {sum(len(v) for v in groups.values())}, complete groups {len(rank)}, passing all five cases {sum(1 for r in rank if r['all_cases_pass'])} -> {out}")
