# G1 중단 및 복구 등록 — 2026-10-10

19:31 확인: 최초 병렬6건과 runner는 모두 없고, 정상 종료0건이다. 서버 boot 시각은16:50으로 표시되며 마지막 로그mtime은17:06이다. 서버 재시작과 작업 중단을 확인했지만, 이 두 시각의 차이 때문에 재시작 순간/중단 원인을 단정하지 않는다. 기존 live_status.json은0byte이고 완료 코드·Good Bye가 없다. 덱·mesh·parameter 등32개 잠금 입력의 해시는 모두 일치한다.

| 최초 run | 마지막 로그 accepted 시각 [ns] | 목표2.125ns 대비 위치 |
|---|---:|---:|
| CxN16Atk | 1.00010 | 47.1% |
| CxN16Idle | 1.84020 | 86.6% |
| CxMJ8Atk | 0.53038 | 25.0% |
| CxMJ8Idle | 1.25670 | 59.1% |
| CxMA8Atk | 0.34222 | 16.1% |
| CxMA8Idle | 0.44834 | 21.1% |

이는 로그상 시간 위치이며 완료율이나 남은 wall time 추정이 아니다. 정상 완료/원시PLT 온전성을 인정하지 않는다. 기존 덱에는 restart Save가 없고 PLT만 남아 있어 상태를 이어 실행할 수 없다. 기존 파일을 그대로 보존하고 새 복구 폴더에서 처음부터 다시 계산한다.

복구 배치 g1_recovery_20261010_01: CxR16Atk/Idle, CxRJ8Atk/Idle, CxRA8Atk/Idle 총6건. Run ID만 변경하고 원래 시간/메시/Physics/Newton/10주기/2.125ns/Cs/reset은 그대로다. 각4threads, 총24threads. 원문과 실제 세 mesh를 새로 점검하고 review_gate를 기록한 뒤 시작한다. Grounded 제외 유지, G1 미통과, P2 대기 유지.

예상 저장500MB와 RAM12GiB는 현재 여유 범위다. 현재 server load는197이고 CPU busy70%로 이전보다 높아 기존21:40~01:40 완료 예상은 철회한다. 복구 시작 후 실제 속도로 새 예측을 계산한다. 상태 JSON은 fsync 뒤 atomic replace하고 boot ID를 기록해 상태 파일의 내구성과 재시작 추적을 개선한다. 이는 소자 계산 설정 변경이 아니다.

기존 중단 증거: docs/CODEX_G1_INTERRUPTION_AUDIT_2026-10-10.json.
복구 manifest: experiments/g1_recovery_20261010_01_manifest.json.
서버: ~/vblhwl_3d_dram/codex_validation/g1_recovery_20261010_01.
