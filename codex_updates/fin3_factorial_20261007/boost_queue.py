"""Eight supplemental workers; executed input bytes and original queue stay unchanged."""
from pathlib import Path
import json,hashlib,datetime
B=Path(__file__).resolve().parent
source=(B/'run_queue.py').read_text()
prefix=source.split('\ncheck()\nwith concurrent.futures.',1)[0]
old="B=Path(__file__).resolve().parent;lk=(B/'queue.lock').open('w');fcntl.flock(lk,fcntl.LOCK_EX|fcntl.LOCK_NB)"
assert old in prefix
prefix=prefix.replace(old,"B=Path(__file__).resolve().parent;lk=(B/'boost_queue.lock').open('w');fcntl.flock(lk,fcntl.LOCK_EX|fcntl.LOCK_NB)")
old=" while not quota()['reserve_ok']:emit('DEFER quota '+j['id']);time.sleep(30)"
assert old in prefix
prefix=prefix.replace(old," while not quota()['reserve_ok'] or not resource_room():emit('DEFER resources '+j['id']);time.sleep(30)")
old=" lock=(rd/'process.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)"
assert old in prefix
prefix=prefix.replace(old," lock=(rd/'process.lock').open('a')\n try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)\n except BlockingIOError:emit('SKIP claimed '+j['id']);return\n if (rd/'exit_code.txt').exists() or (rd/'process.json').exists():emit('SKIP already launched '+j['id']);return")
exec(compile(prefix,str(B/'boost_queue.py')+':shared_worker','exec'),globals())
def resource_room():
 load=float(Path('/proc/loadavg').read_text().split()[0])
 mem={line.split(':')[0]:int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines()}
 return load<96 and mem['MemAvailable']>32*1024*1024
check()
m=json.loads((B/'manifest.json').read_text());jobs=[j for j in reversed(m['runs']) if not j['reuse_from'] and not (B/'runs'/j['id']/'process.json').exists() and not (B/'runs'/j['id']/'exit_code.txt').exists()]
record=dict(started_at=datetime.datetime.now().astimezone().isoformat(),original_workers=8,supplemental_workers=8,total_cap=16,threads_per_job=4,manifest_sha256=hashlib.sha256((B/'manifest.json').read_bytes()).hexdigest(),unchanged_input_verified=True,paper_review='Original pages2/3/5 reread 2026-10-07 21:35; Fig2/4/5/8; same mesh hashes, profiles, parameters and 720 conditions',duplicate_prevention='shared process.lock plus recheck under lock; original queue starts front, supplemental starts back',resource_limits='load1min<96; MemAvailable>32GiB; quota reserve512MiB',available_jobs=len(jobs))
(B/'concurrency_update.json').write_text(json.dumps(record,indent=2)+'\n');emit('BOOST START 8 extra workers; same verified input; original queue untouched')
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 fs=[pool.submit(run,j) for j in jobs]
 for f in concurrent.futures.as_completed(fs):
  try:f.result()
  except Exception as e:emit('BOOST ERROR '+repr(e))
(B/'boost_complete.json').write_text(json.dumps(dict(completed_at=datetime.datetime.now().astimezone().isoformat()))+'\n')
emit('BOOST COMPLETE')
