from pathlib import Path
import json,tarfile,shutil,datetime,hashlib
B=Path(__file__).resolve().parent;CV=B.parent;REPO=CV/'github_repository/vblhwl-3d-dram';OUT=REPO/'codex_updates/fin3_factorial_20261007';OUT.mkdir(parents=True,exist_ok=True)
unpacked=B/'share_snapshot';unpacked.mkdir(exist_ok=True)
with tarfile.open(B/'share_inputs.tar.gz') as tar:
 for m in tar.getmembers():
  dest=(unpacked/m.name).resolve();assert dest.is_relative_to(unpacked.resolve()) and m.isfile();dest.parent.mkdir(parents=True,exist_ok=True)
  with tar.extractfile(m) as f,dest.open('wb') as g:shutil.copyfileobj(f,g)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.py','.ps1']:shutil.copy2(p,OUT/p.name)
for name in ['manifest.json','design_matrix.csv','PRE_RUN_CHECK.md','status.json','old720_discarded.json','ranking.json']:
 if (unpacked/name).exists():shutil.copy2(unpacked/name,OUT/name)
for name in ['checks','results']:
 shutil.copytree(unpacked/name,OUT/name,dirs_exist_ok=True)
if (B/'latest_status.json').exists():shutil.copy2(B/'latest_status.json',OUT/'status.json')
shutil.copy2(B/'share_inputs.tar.gz',OUT/'input_snapshot.tar.gz')
s=json.loads((OUT/'status.json').read_text(encoding='utf-8'));old=json.loads((OUT/'old720_discarded.json').read_text(encoding='utf-8'))
nat=json.loads((OUT/'results/F3C013_c2.json').read_text(encoding='utf-8')) if (OUT/'results/F3C013_c2.json').exists() else None
report=f'''# fin3로 교체한 720개 개선 실험

{s['checked_at']} 확인 기준이에요. 새 fin3 탐색을 시작했고 기존720개 큐는 중단했어요. 기존 결과는 후보 선정에서 폐기했어요. 원시 데이터와 Git 이력은 이전 판단의 근거를 추적하기 위해 남겼어요.

720개는 Case5개×준비조건12개×SN초기화3개×II2개×Cs2개예요. fin3완료baseline5개와 같은조건의 자체생성F3N5개를 재사용해요. 실제 새 solver계산은710개예요. 기존720개의 결과는 하나도 재사용하지 않아요. 재사용한 실행은 source_id와 실제 원본 CMD/PLT로 추적할 수 있어요. 새 입력과 원본의 수치 출력 간격은 별도로 남겨요.

준비조건은 fin3 Case별 자연 생성 유지시간20.6/16.2/19.6/18.7/14.6µs의0.8·1.0·1.2배와 외부 pair source의 uniform/BL25nm/SN25nm×fin3생성률0.8·1.0·1.2배예요. SN은 준비 중 고정/일찍 해제/하강 직전 재설정, II는 켬/끔, Cs는 쓰기곡선 보정값/본문값을 비교해요. 재료·접합·Hurkx계수는 바꾸지 않아요.

fin3에 맞춰 몸체 전위를 gate아래 평균 ElectrostaticPotential로 읽어요. 초기 평형을 기준으로 BL하강 완료0.25ns뒤 값을 비교해요. 이 측정 정의와 Case별 준비조건은 역산한 후보이며 저자의 명시 조건이 아니에요. 외부 source로 맞은 결과를 자연 GIDL로 설명하지 않아요.

새 입력은 모두 첫low와9주기,200ns전체를 계산해요. 몸체 전위, 첫low손실,200ns손실을 동시에 비교해요. 정공 수, BTBT·II·SRH의 생성·재결합 적분, SN전류와CsΔV를 따로 기록해요. 준비 중 SNclamp가 공급하는 전하 때문에 그 구간의 전류와CsΔV 차이는 곧바로 수치 오류로 판단하지 않아요. body잔차에는 경계 유입·유출과 이산화 오차가 함께 들어 있어요.

논문 III/VI와 Fig.2/4/5/8을 재검토했어요. 새 메시·source24개와 입력720개, 총744개 점검을 통과하고 각PASS를 읽은 뒤 실행했어요. 실제메시의 접합50/175nm·body두께·도핑을 확인했어요. 매 실행 입력SHA와quota512MiB여유를 확인해요.

현재 새 탐색 결과{s['results']}개를 읽었고 모두 출력 형식·시간 범위 검증을 통과했어요. 이 수는 재사용 기준 결과를 포함해요. 새solver는{s['active'].__len__()}개, 별도 자연생성F3N은{s['natural_active'].__len__()}개가 실행 중이에요. 기존720개 실행은0개예요. 기존큐에서 실행중이던8개만중단했으며 Claude RH·3D와 F3N은 유지했어요. 큐 상한은8workers×4threads예요. 재사용F3N의 완료를 기다리는 작업이 있어서 현재solver수는8보다 작을 수 있어요.

완료 원시출력은 로컬로 복사해 파일별SHA를 검증한 뒤 서버에서 정리해요. 전송이 멈추면 quota보호가 새 작업 시작을 대기시켜요. 원시출력의 자동 GitHub 업로드는 하지 않으며 이번커밋에는 현재확보한 결과와 재사용 원시출력 스냅샷을 담았어요.

후보는5개Case가 모두 끝난 조합끼리 비교해요. 각Case의 몸체±30mV, first/200ns±0.3decade(Case5first±1mV)를 진단 기준으로 사용해요. 약2배허용범위의 통과는 논문값의 정확한 재현 완료를 뜻하지 않아요. SN초기전압과쓰기곡선, 전하수지 결과도 함께 확인해요. 과거720개용 종료예상시간은 폐기하며 새실행속도가 확보된 뒤 다시 산정해요.
'''
if nat:
 report+=f'''\n자연 생성 Case2가 먼저 완료됐어요.16.2µs동안SN을고정한 조건에서 첫하강 전정공{nat['Nh_prefall']:.0f}개, fin3몸체상승{nat['body_avg_fin3_mV']:.2f}mV,첫low손실{nat['low_phase_loss_mV'][0]:.2f}mV,200ns손실{nat['loss200_claude_avg_tool_mV']:.2f}mV예요. 논문은445/29/50mV예요. 이Case는진단범위를통과했지만 긴준비시간과SN고정이논문과같은이력인지는미확인이에요. firstlow전류와CsΔV차이는{nat['first_low']['mismatch_relative']*100:.3f}%,200ns구간은{nat['all_after_first_fall']['mismatch_relative']*100:.3f}%예요. 쓰기곡선최대오차는{nat['write_from_WL_midpoint']['max_error_mV']:.2f}mV여서개별점±30mV기준은남아있어요.\n'''
report+='\n실행 입력·원시출력·검사·manifest는 input_snapshot.tar.gz에 있어요. design_matrix.csv는720개 조건표,results는완료분분석,ranking.json은5개Case가완료된조합순위예요. 검사시각과실행시각은checks/reviewed.json,status.json,old720_discarded.json에기록했어요.\n'
(OUT/'README.md').write_text(report,encoding='utf-8',newline='\n');(REPO/'docs/CODEX_FIN3_FACTORIAL_2026-10-07.md').write_text(report,encoding='utf-8',newline='\n')
desktop=Path('C:/Users/LEEJINSEOK/Desktop/서강대/반엘프/results_vbl_hwl_1t1c_3ddram/Codex_독립검증_2026-10-07/fin3_720_개선실험');desktop.mkdir(parents=True,exist_ok=True)
(desktop/'fin3_720_개선실험_현황.md').write_text(report,encoding='utf-8',newline='\n')
for n in ['manifest.json','design_matrix.csv','status.json','old720_discarded.json','ranking.json']:shutil.copy2(OUT/n,desktop/n)
for p in [CV/'CURRENT_BASELINE.json',REPO/'docs/CODEX_CURRENT_BASELINE.json']:
 j=json.loads(p.read_text(encoding='utf-8'));j.update(active_batch='fin3_factorial_20261007',legacy_720_screen='OBSOLETE; queue stopped; excluded from selection; raw audit retained',new_search_conditions=720,new_solver_runs=710,reused_fin3_references=10,full_waveform_200ns=True,updated_at=s['checked_at']);p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
for folder in [OUT/'checks',OUT/'results']:
 for p in folder.iterdir():
  if p.suffix in ['.json','.txt','.csv','.log']:
   # Preserve raw check bytes and hashes; Git attributes handles binary/text elsewhere.
   pass
print('SHARED',OUT,'DESKTOP',desktop)
