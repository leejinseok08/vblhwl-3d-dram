from pathlib import Path
import json,collections,subprocess,datetime,os
B=Path(__file__).resolve().parent
active=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  cmd=(p/'cmdline').read_bytes().split(b'\0');cwd=(p/'cwd').resolve()
 except (OSError,RuntimeError):continue
 if cmd and cmd[0].split(b'/')[-1]==b'sdevice' and B/'runs' in cwd.parents:active.append(dict(pid=int(p.name),id=cwd.name))
counts=collections.Counter(p['id'] for p in active);assert max(counts.values(),default=0)==1,'Duplicate simulation'
results=[json.loads(p.read_text()) for p in (B/'results').glob('*.json')]
out=dict(checked_at=datetime.datetime.now().astimezone().isoformat(),active_count=len(active),active=active,duplicates=False,results=len(results),invalid=[r for r in results if not r.get('success')],booster_log=(B/'boost.log').read_text()[-1500:] if (B/'boost.log').exists() else '',load=Path('/proc/loadavg').read_text().strip())
(B/'parallel_status.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
