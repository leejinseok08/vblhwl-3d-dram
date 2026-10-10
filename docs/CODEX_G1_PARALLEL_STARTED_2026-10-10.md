# G1 병렬 검증 시작 — 2026-10-10

**15:40:46 KST에 6건을 동시에 시작했다.** h/16 시간 검증 2건과 h/8 메시 두 단계 검증 4건을 병렬 계산한다. 개별4 threads, 총24 threads이며 실행 전 메시/입력 검사와 원문 검토를 마쳤다.

| 검증 | 실제 run ID | PID |
|---|---|---|
| 시간 h/16, baseline22459 vertices | CxN16Atk / CxN16Idle | 32544 / 32545 |
| 메시1, h/8,42745 vertices | CxMJ8Atk / CxMJ8Idle | 32549 / 32552 |
| 메시2, h/8,61261 vertices | CxMA8Atk / CxMA8Idle | 32560 / 32569 |

runner PID32536. 입력 등록 commit42f7be2d5878919c947455780efcf6f8986f2e06. 서버 경로 ~/vblhwl_3d_dram/codex_validation/g1_parallel_20261010_01.

기존 h/4,h/8 쌍은 재사용한다. 물리 입력·Newton·10주기·2.125ns 최종 시각·body6mV/쓰기6mV/기울기0.0012mV/cycle 기준을 유지한다. h/16은 MaxStep뿐 아니라 InitialStep도 절반으로 줄여 초기/최대step 비율을 유지했다. 메시 SDE diff는 refinement 선언만 다르며 기하·도핑·접촉은 같다. 두 메시 후보의 global 최소 x크기도1→0.5nm이고 global 최대10×5nm는 동일하다.

최근 서버는128 logical CPU, CPU idle71%, 가용 RAM약227GiB였다. 예상 RAM12GiB와 저장500MB를 현재 여유로 감당할 수 있다. 실제 비용은 프로파일링해 갱신한다. 각 작업이 끝날 때 결과를 자동 추출하므로 짧은 작업은 긴 작업을 기다리지 않고 비교표에 반영된다.

첫 G1 판정 예상은 **시작 후6–10시간, 10월10일21:40~11일01:40 KST**다. 이는 h/8 실측과 메시 규모에 따른 추정이며 통과를 보장하지 않는다. h/8→h/16이 통과해야 h/8 메시 비교를 확정에 사용한다. 실패하면 메시 결과는 예비 자료로 보존하고 필요한 추가 수치 검증을 결정한다. 자동 G1_numerical_candidate와 최종 독립 G1 판정은 구분한다.

Fig.7 grounded body는 계속 재현 범위에서 제외한다. P2 floating OFF/ON 두 건은 최종 G1 통과까지 대기한다. Claude는 같은 수치 배치를 중복 실행하지 않고 준비된 공식 덱에 최종 통과 설정을 반영한다.

근거: experiments/g1_parallel_20261010_01_manifest.json 및 review_gate.json. 진행은 서버 live_status.json/completed_analysis.json에 기록한다.
