from pathlib import Path
import subprocess,sys,os,signal,time
B=Path(__file__).resolve().parent
if (B/'night.pid').exists():
 pid=int((B/'night.pid').read_text())
 if Path('/proc',str(pid)).exists():
  assert sys.argv[1:]==['restart_waiting'],'Night controller already active'
  assert (Path('/proc',str(pid))/'cwd').resolve()==B
  assert b'night_queue.py' in (Path('/proc',str(pid))/'cmdline').read_bytes()
  children=subprocess.check_output(['ps','--ppid',str(pid),'-o','pid='],universal_newlines=True) if subprocess.call(['pgrep','-P',str(pid)],stdout=subprocess.DEVNULL)==0 else ''
  assert not children.strip(),'Refusing restart with active children'
  os.kill(pid,signal.SIGTERM);time.sleep(1)
log=(B/'night.log').open('a');p=subprocess.Popen(['python3','-u',str(B/'night_queue.py')],cwd=B,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(B/'night.pid').write_text(str(p.pid)+'\n');print('NIGHT CONTROLLER LAUNCHED',p.pid)
