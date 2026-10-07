from pathlib import Path
import json,shutil
B=Path(__file__).resolve().parent;R=B.parent/'github_repository/vblhwl-3d-dram';O=R/'codex_updates/fin3_factorial_20261007'
s=json.loads((B/'latest_status.json').read_text(encoding='utf-8'));r=json.loads((B/'latest_ranking.json').read_text(encoding='utf-8'));nat=next(g for g in r['ranking'] if g['group']==13)
qualified=[g for g in r['ranking'] if g['all_cases_pass'] and g['SN_precondition_all_pass']]
report=f'''# fin3 개선 실험 현황

{s['checked_at']} 확인 기준이에요. 전체720개 중74개 결과를 검증했어요. 이 중64개는 신규계산,10개는 fin3기준·자연생성 재사용 결과예요. 새실행8개가 진행 중이고638개가 대기 중이에요. 완료율은10.3%예요. 현재 완료분의 실행·출력검증 실패는0개예요. 기존720개큐와실행은 중단 상태예요.

Case5개가 모두 끝난 조합은144개 중14개예요. 몸체전위·첫low·200ns손실의 진단범위와SN초기전압1.1V±5mV를 함께 통과한 조합은 기준조합을 포함해{len(qualified)}개예요. 허용범위는 몸체±30mV, 손실±0.3decade(약2배),Case5첫low±1mV예요. 저자의 측정 오차가 아니라 탐색용 판정 기준이에요.

uniform source를 넣고SN을 일찍 해제한 조합53은 곡선오차 점수만 보면 가장 작아요. 하지만 BL하강 전SN이1.048~1.055V로 낮아져 있어 초기전압 조건을 통과하지 못했어요. 이 조합을 최종1위로 고르지 않아요. 통과조합은85(BL국소source·SN고정),89(BL국소source·SN조기해제),49(fin3uniform기준),13(자연생성·SN고정)이에요. 모두II켬과쓰기곡선보정Cs조건이에요. 이후II끔·본문Cs와0.8/1.2배준비조건이 추가되면 순위가 달라질 수 있어요.

자연생성Case1~5가 모두 완료됐어요. 외부pair source없이 BTBT와II로 전하를 쌓았어요. 준비시간은20.6/16.2/19.6/18.7/14.6µs이고 준비 중SN을1.1V로 고정했어요. 따라서 GIDL만의 생성이나 논문의 초기이력을 확정한 결과는 아니에요. fin3읽기도 역산한 측정정의라는 제한이 남아 있어요.

|Case|몸체상승:논문/계산[mV]|첫low손실:논문/계산[mV]|200ns손실:논문/계산[mV]|
|---|---:|---:|---:|
'''
for o,pb,p1,p2 in zip(nat['cases'],[555,445,365,320,368],[55,29,7.1,3.5,0],[100,50,14.6,7,1]):
 report+=f"|{o['case']}|{pb}/{o['body_avg_fin3_mV']:.2f}|{p1}/{o['low_phase_loss_mV'][0]:.2f}|{p2}/{o['loss200_claude_avg_tool_mV']:.2f}|\n"
report+='''
몸체전위는 모두 약1.2mV이내로 맞았어요. 하지만Case1의 첫low손실은약1.70배,200ns손실은약1.84배예요. 현재 남은 핵심은 몸체전위가 비슷한데도 SN에서 빠져나가는 전하가 다른 이유를 구분하는 것이에요. 자연생성으로 정공을 채우는 경로는 확보했지만 모든결과의 정확한 재현을 완료한 상태는 아니에요. 200ns는Claude평균판독도구와같은시각을쓴값이며paper-axis값도원시분석에별도로남겼어요.

원시데이터 수집기에서Windows PowerShell의UTF-8무BOM스크립트가 한글경로를잘못읽는오류가 있었어요. 로컬검증이 실패했으므로 서버원본은 삭제하지 않았어요. 스크립트를UTF-8BOM으로저장한뒤 해당수집기만재시작했어요. 실제완료파일의로컬SHA검증과서버정리성공로그를확인했어요. 시뮬레이션입력과Claude실행은바꾸지않았어요. 서버quota보호는유지해요.

나머지646개(실행8+대기638개)를 계속 계산해요. 각조합5개Case가모이면 몸체전위·SN초기상태·첫low·200ns·전하수지를같이평가해요. 외부source후보와자연생성후보를따로구분해요. 기존720개결과는이판정에사용하지않아요.
'''
P=Path('C:/Users/LEEJINSEOK/Desktop/서강대/반엘프/results_vbl_hwl_1t1c_3ddram/Codex_독립검증_2026-10-07/fin3_720_개선실험')
for f in [P/'fin3_720_개선실험_현황_1327.md',R/'docs/CODEX_FIN3_PROGRESS_2026-10-07_1327.md']:
 f.write_text(report,encoding='utf-8',newline='\n')
for src,dst in [('latest_status.json','status.json'),('latest_ranking.json','ranking.json')]:
 for d in [P,O]:shutil.copy2(B/src,d/dst)
for name in ['collect.ps1','report_status.py']:shutil.copy2(B/name,O/name)
for o in r['ranking']:
 for c in o['cases']:(O/'results'/(c['id']+'.json')).write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8',newline='\n')
print('REPORT UPDATED; ranked snapshots include70 of74results, remaining4 are in incomplete groups')
