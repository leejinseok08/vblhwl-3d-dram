from pathlib import Path
B=Path(__file__).resolve().parent
R=B.parent/'fin3_update_20261007'
def put(n,s): (B/n).write_text(s,encoding='utf-8',newline='\n')
old=(B.parent/'factorial_conditions_20261006/preflight.py').read_text(encoding='utf-8')
old=old[:old.index("(B/'checks/preflight.json')")]
old+="""
for j in json.loads((B/'manifest.json').read_text())['runs']:
 p=j['parameters'];cmd=(B/'runs'/j['id']/(j['id']+'_des.cmd')).read_text()
 assert all(p[k]==v for k,v in dict(Lg=100,Tox=5,Tgm=20,Dvox=30,Nsd=1e20,Lsp1=25,Lsp2=25,Tper=21,tEdge=.5,Npulse=9).items())
 assert p['WFs']==p['WFd']==(5 if j['case']==5 else 4.7)
 assert 'Average(Window[(0.07500 0.04000)' in cmd
 assert abs(j['reading']['time_s']-j['schedule']['tS']-.75e-9)<1e-18
 assert abs(p['Cs']-({30:5.1e-15,20:4.2e-15,10:3.6e-15}[p['Tbody']]*(1.8/4.2 if j['Cs_basis']=='write_fit' else 1)))<1e-25
 assert bool(p['Gb'])==(j['preparation']=='proxy')
 if j['profile_path']:assert 'ReadFromFile' in cmd and 'OpticalGenerationInput' in cmd
 msg=f"PASS {j['id']}: mesh/model unchanged; {j['preparation']} x{j['preparation_factor']} {j['source_window']}; SN={j['SN_protocol']}; II={j['II']}; Cs={j['Cs_basis']}; fin3 average; full200ns"
 print(msg,flush=True);lines.append(msg)
(B/'checks/preflight.json').write_text(json.dumps(dict(pass_all=True,checks=lines,performed_at=datetime.datetime.now().astimezone().isoformat()),indent=2)+'\\n')
print('ALL744 CHECKS PASS; review each line before launch')
"""
put('preflight.py',old)
g=(R/'guard.py').read_text(encoding='utf-8').replace("for k in ['mesh','parameter']:","for k in ['mesh','parameter']:")
g=g.replace("def check():", "def check():")
g=g.replace(" for k in ['mesh','parameter']:assert sha(Path(j[k+'_path']))==j[k+'_sha256']", " for k in ['mesh','parameter']:assert sha(Path(j[k+'_path']))==j[k+'_sha256']\n if j.get('profile_path'):assert sha(Path(j['profile_path']))==j['profile_sha256']")
g=g.replace('checks_read=17','checks_read=744').replace('fin3/17checks','fin3/744checks')
put('guard.py',g)
a=(R/'analyze_fin3.py').read_text(encoding='utf-8')
a=a[:a.index('def save(j):')]+"""def save(j):
 ref=j.get('reuse_from');rid=ref['id'] if ref else j['id'];rd=Path(ref['directory']) if ref else B/'runs'/rid
 try:
  source=json.loads((rd/'run.json').read_text()) if ref else j
  o=analyse(rd,rid,j['case'],source)
  o.update(id=j['id'],source_id=rid,reused_reference=bool(ref),group=j['group'],preparation=j['preparation'],preparation_factor=j['preparation_factor'],source_window=j['source_window'],SN_protocol=j['SN_protocol'],Cs_basis=j['Cs_basis'])
  o['SN_prefall_error_mV']=(o['SN_prefall_V']-1.1)*1000
  o['SN_prefall_within_5mV']=abs(o['SN_prefall_error_mV'])<=5
 except Exception as e:o=dict(id=j['id'],case=j['case'],success=False,error=str(e))
 f=B/'results'/(j['id']+'.json');tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(o,indent=2)+'\\n');tmp.replace(f);return o
if __name__=='__main__':
 for j in json.loads((B/'manifest.json').read_text())['runs']:
  if (B/'runs'/j['id']/'exit_code.txt').exists() or (j.get('reuse_from') and (Path(j['reuse_from']['directory'])/(j['reuse_from']['id']+'_sys.plt')).exists()):print(json.dumps(save(j)))
"""
put('analyze_fin3.py',a)
q=(R/'run_queue.py').read_text(encoding='utf-8')
q=q.replace(" rd=B/'runs'/j['id']\n if", " rd=B/'runs'/j['id']\n if j.get('reuse_from'):\n  ref=j['reuse_from'];src=Path(ref['directory']);f=src/(ref['id']+'_sys.plt')\n  while not (f.exists() or Path(str(f)+'.gz').exists()) or (ref['kind']=='fin3_own_generation_live' and not (src/'exit_code.txt').exists()):time.sleep(30)\n  o=save(j);emit('REFERENCE '+j['id']+' valid='+str(o['success']));return\n if")
q=q.replace('max_workers=2','max_workers=8')
q=q.replace(" (rd/'exit_code.txt').write_text(str(rc)+'\\n')", " o={}\n (rd/'exit_code.txt').write_text(str(rc)+'\\n')")
q=q.replace(" emit('END '", " (rd/'finished.json').write_text(json.dumps(dict(exit_code=rc,finished_at=datetime.datetime.now().astimezone().isoformat()))+'\\n')\n emit('END '")
q=q.replace("emit('QUEUE COMPLETE; natural-generation preparation remains a diagnostic')","(B/'queue_complete.json').write_text(json.dumps(dict(completed_at=datetime.datetime.now().astimezone().isoformat()))+'\\n')\nemit('QUEUE COMPLETE; fin3 initial history remains a diagnostic')")
put('run_queue.py',q)
put('PRE_RUN_CHECK.md',"""# fin3 720개 개선 실험 실행 전 점검

2026-10-07 Cho IRPS2026 원문 III/VI, Fig.2/4/5/8의 p2/p3/p5 이미지와 p4 본문을 다시 확인했어요. Lg100/Tox5/Tgm20/dVOX30nm, body30/20/10nm, spacer25nm, Nsd1e20/Nch1e18 또는1e16, WF4.7/5.0V를 유지해요. 접합50/175nm, body40..70/60/50nm는 새 svisual cutline으로 확인해요. HfO2/Si3N4,300K,SRH 및 Hurkx A1.7e21/B2.25e7은 기존 가정/보정값으로 유지해요. 저자의 공개값으로 승격하지 않아요.

720=5Cases×12준비조건×3SN초기화×2II×2Cs예요. 준비조건은 자연 생성 유지시간(20.6/16.2/19.6/18.7/14.6us)의0.8/1/1.2배와, 외부 pair source의 uniform/BL25nm/SN25nm×fin3 Case별GBQ배수의0.8/1/1.2배예요. 국소 source는 부피보상5배를 사용하며 실제 생성 적분을 따로 읽어요. 자연 생성도 긴 유지와 SNclamp의 영향이 있으므로 논문에 명시된 초기 이력으로 단정하지 않아요.

fin3 읽기는 gate 아래x75..175nm,y40..(40+Tbody)nm의 평균 ElectrostaticPotential에서 과도 초기 평형값을 빼고 BL하강 완료0.25ns뒤(tS+0.75ns)에 측정해요. 저자의 미공개 정의를 역산한 후보예요. 전체9주기,200ns를 모두 계산해요. 몸체±30mV,first/200ns±0.3decade(Case5first±1mV)는 진단 허용오차예요. 모든Case를 각각 판정하며 첫low와200ns손실, 전하 수지를 동시에 보고해요. 쓰기 기준은 WL중간전압 통과시각으로 맞춰요. 200ns의 paper-axis 및 Claude-tool 시각 차이를 모두 기록해요.

fin3완료baseline5개와 자체생성F3N5개만 재사용해요. 신규 solver는710개예요. 기존720개 출력은 재사용하지 않아요. 원본논문 구조와 새mesh/source24개,720개 입력 조건을 확인하고 모든PASS를 읽은 뒤 시작해요. 실행마다SHA와quota512MiB여유를 재확인해요. 새큐는8workers×4threads,건당6h상한이에요. 원시출력은 로컬 복사SHA검증 뒤에만 서버에서 정리해요. 기존720큐는 새큐 시작 확인 뒤 중단하고 후보에서 폐기해요. Claude Round15 RH/3D작업과 F3N자체생성5개는 건드리지 않아요.
""")
print('SUPPORT READY')
