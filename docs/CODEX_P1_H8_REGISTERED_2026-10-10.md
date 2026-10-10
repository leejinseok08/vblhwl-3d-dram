# Codex P1 h/8 실행 전 등록 — 2026-10-10

상태: 실행 전 등록. 사용자 지시: “다음 검증 실행해”, “어제 작성한 계획서대로 진행해”.
기준 계획: docs/CODEX_2D_FIRST_REPRODUCTION_PLAN_2026-10-09.md의 P1.

## 범위

- Codex가 CxN8Atk / CxN8Idle 두 건을 병렬 실행한다. 각 4 threads.
- 검증 완료된 h/4 덱의 50개 Transient 구간 MaxStep만 절반으로 줄인다. hammer plateau 최대 간격은 1.175 ps이다.
- InitialStep, MinStep, Newton 허용오차, 물리 모델, bare CurrentPlot, 펄스, Cs=4.2 fF, AreaFactor=0.1, 300 K와 SN 초기 reset을 보존한다.
- fin7 C2, 2D Z 방향 pair, II ON 진단이다. 자연 precharge나 3D mini-array 재현으로 판정하지 않는다.
- gb2_zz mesh SHA-256: aa0f32997e339c589882542dee7ead8919a2003459f94da75d86bc6d5606d0b2.
- 앞선 6건은 10월 10일 01:27 종료했다. h/2→h/4 body 전위 차이 7.282 mV가 6 mV 기준을 넘었으므로 h/8을 추가한다.

## 실행 전 검토

Cho 원문의 Sec.III/V 및 Fig.2/4/5/6/7 본문과 그림을 다시 읽는다. 실제 배포한 메시에서 모든 contact, 양쪽 채널의 접합 50/175 nm와 N+=1e20 / p=1e18 cm^-3, Lg=100 / Tbody=20 / Tox=5 / Tgate=20 / isolation=30 / spacer=25 nm를 새 preflight로 검사한다.
preflight 모든 줄을 읽고 review_gate.json에 해시와 검토 근거를 기록한 뒤 실행한다. 기존 ALL PASS를 실행 승인으로 재사용하지 않는다. 직전 프로세스 및 quota도 확인한다.
HfO2/Si3N4, 300 K, 수명 및 Hurkx/II 기본 계수는 현행 가정이며 저자 명시값으로 승격하지 않는다. 새 물리 입력값을 추가하지 않는다.

## 추출과 판정

등록 위상 245–2125 ps에서 SN 손실, attack−idle, 마지막 5주기 기울기, body 중심 전위 상승과 BE 전하 잔차를 추출한다. accepted step 전체를 원시 PLT 저장 시점과 대조한다. MEASURE.md의 별도 20 ps 위상 정의도 구분하여 검토한다.
최신 refinement의 body 차이 ≤6 mV, 기울기 차이 ≤0.0012 mV/cycle를 확인한다. 앞선 h/2→h/4가 body 기준을 넘었으므로 h/8 한 번의 통과만으로 연속 수렴이나 G1 완료를 선언하지 않는다. 시간 및 필요 시 Newton 검증 뒤 gb2j_zz/gb2a_zz 메시 후보를 검증한다. 물성 보정이나 P2/P6를 자동 시작하지 않는다.

## 역할 분담

Claude의 10월 10일 12:30 업데이트를 확인했다. 메시 후보 두 종, P2 분석 도구 및 Hk4/CPbare1의 DnwRzb_zz / DnwRzbi_zz / DnwRzbg_zz는 이미 준비됐고 미실행이다. Codex는 P1을 담당한다. Claude는 현재 자료 분석과 P2 준비를 이어가되, G1 통과 및 최종 수치 설정 전달 후 P2 덱을 재생성하고 실행한다.

서버 경로: ~/vblhwl_3d_dram/codex_validation/numerics_h8_20261010_01.
실제 실행 상태와 결과는 live_status.json, completed_analysis.json 및 runs/CxN8*에 기록한다.


## 2026-10-10 후속 사용자 범위 변경

Fig.7 grounded body case를 재현 조건에서 제외했다. 위의 최초 등록/실행 기록은 당시의 이력이다. 최신 계획과 Claude 프롬프트에서는 P2 floating OFF/ON 2건, P5 floating 4조건의 attack/idle 8건, P6 ON Y/Z floating 4건으로 변경했다. Grounded 파형·threshold·body rise·억제 설명은 현재 재현율과 통과 조건에서 제외한다. 현재 h/8 두 실행은 floating이므로 이 범위 변경에 해당하지 않는다.
