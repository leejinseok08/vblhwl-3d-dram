from pathlib import Path
import subprocess,json,datetime
B=Path(__file__).resolve().parent
subprocess.check_call(['python3',str(B/'guard.py')])
if (B/'boost.pid').exists():
 pid=int((B/'boost.pid').read_text());assert not Path('/proc',str(pid)).exists(),'Booster already active'
log=(B/'boost.log').open('a');p=subprocess.Popen(['python3','-u',str(B/'boost_queue.py')],cwd=B,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(B/'boost.pid').write_text(str(p.pid)+'\n');print('BOOST LAUNCHED',p.pid)
