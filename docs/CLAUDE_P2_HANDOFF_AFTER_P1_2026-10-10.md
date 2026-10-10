# Claude 전달용 프롬프트 — 어제 공동 계획 이행

아래 블록을 Claude에 전달한다. `/goal`이 해당 환경에 등록돼 있지 않으면 같은 내용을 지속 작업 목표로 사용한다. 이 파일 작성은 Claude에 실제 전달하거나 Claude 작업을 실행한 뜻은 아니다.

```text
/goal Cho IRPS2026 VBL/HWL 1T1C DRAM의 2026-10-09 공동 계획에서 Claude 담당 P2 준비와 자연 precharge 원인 분리를 완료하고, 원시 근거·미해결 항목·다음 최소 대조를 한국어로 보고한다. P2 시뮬레이션은 Codex의 G1 통과 및 최종 수치 설정 전달 후 실행한다.

1. 기준과 현재 상태
사용자의 최신 지시는 “다음 검증 실행해”와 “어제 작성한 계획서대로 진행해”이다. GitHub leejinseok08/vblhwl-3d-dram의 docs/CODEX_2D_FIRST_REPRODUCTION_PLAN_2026-10-09.md를 기준으로 한다. 프로젝트 CLAUDE.md, MEASURE.md와 본인 최신 NOTES/claude/EXPERIMENTS.md를 읽는다. 오래된 main snapshot을 현재 서버 상태로 간주하지 않는다.
Codex는 P1 시간·메시·전하 수지 검증을 담당한다. 기존 CxN1/2/4 attack+idle 6건은 2026-10-10 01:27 정상 종료했고, accepted step 저장 시점 및 원시 해시 검증을 마쳤다. h/2→h/4 body 순상승 차이 7.282 mV가 6 mV 예산을 넘었다. h/4 순 body 상승 27.458 mV, SN 순손실 −0.023033 mV, 마지막 5주기 순기울기 −0.000686784 mV/cycle이다. 이 작은 음의 손실은 물리적 이득의 증거가 아니다.
Codex 후속 numerics_h8_20261010_01의 CxN8Atk / CxN8Idle는 2026-10-10 12:50:44 KST 시작했다. 서버 ~/vblhwl_3d_dram/codex_validation/numerics_h8_20261010_01, runner PID84122, device PID84130/84131이다. 각 4 threads이며 50개 MaxStep만 h/4의 절반, hammer plateau 1.175 ps이다. Physics·Newton·InitialStep·펄스·Cs·메시·SN reset은 동일하다. 등록 commit23811f60d67f1c713ee3e9961e1e7e4a804563b1. 아직 결과와 G1 판정은 없다.
Codex 배치를 중복 실행하거나 수정하지 않는다. h/8 한 번 통과만으로 G1을 선언하지 않는다. 연속 refinement 안정성과 메시 검증이 남아 있다.

2. 이미 완료한 본인 작업은 재사용한다
10월 10일 12:30 기록의 P0 채점 수정, tools/gt_precharge.py, gb2j_zz/gb2a_zz 메시 후보, Hk4/CPbare1의 DnwRzb_zz / DnwRzbi_zz / DnwRzbg_zz 및 runs/run_p2nw.sh는 준비된 상태다. 이를 처음부터 다시 만들거나 지금 큐를 실행하지 않는다.
G1 대기 중에는 기존 raw와 본인 분석 도구로 write 부족이 처음 발생하는 구간, 중복 시각과 reset 전후 상태의 처리, 전류 단위·폭·AreaFactor·Cs 및 준페르미 전압 분배를 점검하고 P2 표와 덱 diff를 준비한다. 기존 전류값과 구간 평균을 다른 정의로 섞지 않는다. 초기 DC 전류 한 점이 과도 충전 전류의 상한이라는 결론을 내리지 않는다.

3. G1 통과 후 P2 최소 3건
Codex가 통과한 시간·메시·출력·Newton 설정을 명시하면 공식 생성기에 반영하고 덱을 재생성한다. 현재 Hk4는 잠정 설정이다. h/8을 최종 통과값으로 미리 확정하지 않는다.
각 해당 원본과 동일한 Z pair의 floating/II OFF, floating/기본 II ON, grounded/기본 II ON을 write→WL off→hold(공격 직전 245 ps)까지 실행한다. 초기 평형용 nSN=0 설정과 해제는 보존하고, 130–140 ps의 SN=1.1 V 강제 reset만 제거한다. SN 강제 상태를 자연 충전으로 보고하지 않는다.
Case2 Tbody20 nm / Nch1e18 cm^-3 / WF4.7 eV, 해당 원본의 BL/WL 펄스, Cs4.2 fF, 접촉·도핑·구조·재료와 물리 모델을 고정한다. II 구성은 write부터 끝까지 유지한다. underlap·Cs·이동도·Hurkx·접지 저항을 동시에 바꾸지 않는다. Fig7b의 R은 맞춤 변수가 아니다.
매 배치 실행 전에 원문 본문·캡션·그림과 실제 mesh의 접합·도핑·치수·접촉을 새로 확인하고 모든 검사 줄을 읽는다. 입력 해시, 소유자, 변경/고정 변수, 예상 작업 수·자원, 성공/중단 기준을 등록하고 live process/quota를 확인한다. 상대 큐는 보존한다.
기존 reset raw는 조건이 일치하는 대조군으로 재사용한다. 비교 가능한 mesh/시간/물리 입력과 초기 이력을 먼저 명시한다. 서로 다른 설정의 raw를 같은 통과 비교표에 섞지 않는다.

4. 추출과 해석
초기 평형, WL 상승 중간점(0.9 V) 후 12/24/39/60 ps, write peak, WL-off 전후, BL 전환, 공격 직전의 SN·body 중심/평균·정공 수와 SN의 전자/정공/변위/total current를 표로 낸다. 쓰기 판독값 0.72/0.92/1.06/1.13 V를 각각 ±30 mV로 비교하고 최악 오차도 공개한다.
SN–BL 전압 및 전자 준페르미 분포에서 채널/underlap/접촉 전압 분배를 계산한다. 기존 54–80% underlap 해석이 새 자연 이력에서도 성립하는지 확인한다. CsΔV+∫I(total)dt는 accepted BE endpoint 전체로 계산하고 clamp 구간과 분리한다. 중복 시각은 reset 전후 상태에 따라 구분하며 일률적으로 한 상태를 버리지 않는다.
grounded의 충전 부족은 접촉·도핑·회로 오류와 body 경계조건 차이를 분리해 판단한다. 모델 가정과 미공개 저자 조건은 별도 표시한다. 충전 부족을 설명했다고 쓰기 재현 성공으로 선언하지 않는다.

5. 산출물과 다음 단계
본인 소유 NOTES.md, claude/EXPERIMENTS.md 및 보고서에 기존 완료/현재 준비/실제 실행/미실행을 구분한다. 덱 diff, mesh/deck/parameter 해시, 실행/종료 시각, 원시 자료 위치, 세 구성 비교표와 가장 큰 불일치를 보고한다. G1 대기 중 끝낼 수 있는 준비는 진행하고, 실행 의존 작업은 G1 판정까지 보류한다.
P2 뒤에는 공동 계획 P3의 IV·load-line·자연 write 동시 검증으로 넘어간다. P4/P5 및 P6의 3D AC/pair/mini-array 순서를 건너뛰지 않는다. 출처 없는 새 물리값이 필요한 경우에만 근거와 후보 범위를 사용자에게 제시한다. 이미 승인된 준비나 조건이 충족된 계획 실행에 대해 중복 승인을 요청하지 않는다.
```
