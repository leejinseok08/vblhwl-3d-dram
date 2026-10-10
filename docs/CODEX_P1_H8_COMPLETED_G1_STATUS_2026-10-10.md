# P1 h/8 완료 및 G1 상태 — 2026-10-10 15:31 KST 확인

**G1 미통과.** h/8 attack+idle 두 건은 정상 종료했다. 최신 h/4→h/8 차이는 계획의 body·기울기 예산 안에 들지만, 연속 두 refinement의 안정성 및 메시 검증이 아직 충족되지 않았다. P2 floating OFF/ON 두 건은 계속 G1 판정을 기다린다.

| 항목 | h/8 결과 또는 판정 |
|---|---:|
| CxN8Idle 종료 | 13:43:17 KST, exit0 |
| CxN8Atk 종료 | 14:46:22 KST, exit0 |
| 최종 시각 | 둘 다2.125 ns, Good Bye 확인 |
| accepted endpoint 저장 누락 | 둘 다0 |
| body 순상승(attack−idle) | 23.708997 mV |
| SN 순손실(attack−idle) | −0.02209744 mV |
| 마지막5주기 순기울기 | −0.000565664 mV/cycle |
| h/4→h/8 body 차이 절댓값 | 3.748584 mV ≤6 mV |
| h/4→h/8 기울기 차이 절댓값 | 0.000121120 mV/cycle ≤0.0012 |
| 앞선 h/2→h/4 body 차이 | 7.282302 mV >6 mV |
| BE 단자 전하 잔차 절댓값 최대 | 1.80e−14 fC |
| 연속 두 refinement 안정성 | 미충족 |
| 메시 두 후보 device 검증 | 미실행 |

판정 근거는 서버의 완료 추출 결과와 전체 accepted endpoint 저장 대조이다. 이번 상태 갱신에서는 전체 raw를 새로 내려받아 독립 재계산하지 않았다. 작은 음의 SN 순효과를 물리적 이득이나 RH 재현 성공으로 해석하지 않는다. 현재 2D pair와 초기 SN reset은 수치 진단 조건이다.

다음 단계는 추가 시간 refinement로 연속 안정성을 확인하고, 필요 Newton 검토와 준비된 gb2j_zz/gb2a_zz에서 같은 attack/idle 쌍의 메시 민감도를 평가하는 것이다. 이 상태 확인 중 새 시뮬레이션은 시작하지 않았다.

사용자 지시대로 Fig.7 grounded body 파형·threshold·body rise·접지 억제 설명은 재현 범위에서 제외한다. scope51 및 확장 목록의 포함 항목만 판정한다.

근거: docs/CODEX_P1_H8_COMPLETED_ANALYSIS_2026-10-10.json.
계획: docs/CODEX_2D_FIRST_REPRODUCTION_PLAN_2026-10-09.md.
서버: ~/vblhwl_3d_dram/codex_validation/numerics_h8_20261010_01.
