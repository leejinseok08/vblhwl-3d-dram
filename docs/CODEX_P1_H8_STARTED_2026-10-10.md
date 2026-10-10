# P1 후속 검증 실행 보고 — 2026-10-10

어제 공동 계획의 P1에 따라 h/8 attack+idle 두 건을 12:50:44 KST에 시작했다. 12:52:30 확인에서 두 프로세스가 살아 있고 과도 계산을 진행 중이다. 완료 결과와 G1 판정은 아직 없다.

| 항목 | 상태 |
|---|---|
| 실험 | numerics_h8_20261010_01, CxN8Atk / CxN8Idle |
| 프로세스 | runner 84122, device 84130 / 84131, 각 4 threads |
| 변경 | h/4 덱의 50개 MaxStep만 절반, plateau 최대 1.175 ps |
| 고정 | baseline mesh, Physics/Newton/InitialStep, 전압·Cs4.2 fF·SN reset |
| 사전 검토 | 원문 p.2–5 텍스트/그림, 실제 7 contact·6높이 접합·도핑·치수 전부 확인, 새 preflight ALL PASS |
| 자원 | 실행 전 quota7707/9216/10240 MB, h4 실측 저장량을 바탕으로 후속 100 MB 추정 |
| 메모리 | 12:52 device RSS 약0.72 GiB/건; peak 값은 아님 |
| 진행 관측 | 마지막 attempted endpoint attack10.125 ps / idle10.375 ps, accepted 종료 시각과 구분 |
| 실행 전 등록 | GitHub commit23811f60d67f1c713ee3e9961e1e7e4a804563b1 |

기존 h/2→h/4 body 차이7.282 mV가 계획 예산6 mV를 넘어서 추가 실행한다. h/8 한 번의 통과만으로 연속 두 refinement 안정성이나 G1 완료를 선언하지 않는다. 완료 시 원시 종료·accepted step 저장 시점·전하 수지와 h/4 차이를 확인하고, 시간/필요 Newton 및 메시 두 후보 검증을 이어 판단한다. 2D pair와 SN reset은 수치 진단 조건이다.

Claude의 P0 도구 수정, 메시 후보 두 종, gt_precharge.py 및 Hk4/CPbare1 P2 덱 준비는 확인했다. 전달용 프롬프트는 기존 완료 작업을 재사용하고 G1 대기 중 가능한 분석·준비를 진행하며, 최종 수치 설정 전달 후 자연 precharge 세 건을 실행하도록 작성했다. Claude에는 아직 실제 전달하거나 실행하지 않았다.

공동 계획: docs/CODEX_2D_FIRST_REPRODUCTION_PLAN_2026-10-09.md.
프롬프트: docs/CLAUDE_P2_HANDOFF_AFTER_P1_2026-10-10.md.
실행 증거: experiments/numerics_h8_20261010_01_launch.json 및 review_gate.json.
서버 raw/상태: ~/vblhwl_3d_dram/codex_validation/numerics_h8_20261010_01.


## 2026-10-10 후속 사용자 범위 변경

Fig.7 grounded body case를 재현 조건에서 제외했다. 위의 최초 등록/실행 기록은 당시의 이력이다. 최신 계획과 Claude 프롬프트에서는 P2 floating OFF/ON 2건, P5 floating 4조건의 attack/idle 8건, P6 ON Y/Z floating 4건으로 변경했다. Grounded 파형·threshold·body rise·억제 설명은 현재 재현율과 통과 조건에서 제외한다. 현재 h/8 두 실행은 floating이므로 이 범위 변경에 해당하지 않는다.
