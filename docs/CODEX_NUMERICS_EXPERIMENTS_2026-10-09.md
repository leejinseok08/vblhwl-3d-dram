# Codex P1: 2D 시간 간격 수렴 검증 — 2026-10-09

사용자 실행 지시: “너가 할일 시작해”. 담당: Codex. 배치: `numerics_20261009_01`.
계획 근거: `docs/CODEX_2D_FIRST_REPRODUCTION_PLAN_2026-10-09.md` P0/P1.
상태: 준비·독립 추출 교차검증 완료. 이 등록 시점에는 새 sdevice를 시작하지 않았다.

## 이미 확인한 원인

기존 CxS4/CxS8은 기록점 수만 다른 후처리 비교가 아니었다. 실제 solver 로그를 대조하면:

| 기존 실행 | 해머 구간 실제 최대 계산 스텝 [ps] | accepted 해머 스텝 수 |
|---|---:|---:|
| DptRzbi_zz | 9.4 | 651 |
| CxS4Atk | 2.4722 | 1293 |
| CxS8Atk | 1.2361 | 2376 |

전 구간 MaxStep 값은 같았지만 지정 CurrentPlot 시각에 따라 실제 계산 스텝이 달라졌다. 첫 스텝도 0.5→0.3125→0.15625 ps로 바뀌었다. 저장 해상도 증가로 적분 잔차가 줄었다는 사실만으로 solver 수렴을 선언할 수 없다.
설치된 Sentaurus Device U-2022.12 User Guide pp.171–173에서 지정 CurrentPlot 시각의 출력 제어와 bare CurrentPlot의 전체 스텝 기록 방식을 확인했다. 매뉴얼 원문은 Git에 포함하지 않는다.

## 실행 설계

| 실행 | 구분 | 모든 구간 MaxStep 배율 | 해머 plateau 최대 스텝 [ps] |
|---|---|---:|---:|
| CxN1Atk / CxN1Idle | 기준 attack/idle | 1 | 9.4 |
| CxN2Atk / CxN2Idle | attack/idle | 1/2 | 4.7 |
| CxN4Atk / CxN4Idle | attack/idle | 1/4 | 2.35 |

6건, 같은 단계의 attack/idle 두 건 병렬, 각 4 threads. 단계가 실패하거나 출력이 불완전하면 다음 단계로 진행하지 않는다. 모든 구간의 InitialStep·MinStep·Newton 조건은 보존한다.

세 단계 모두 Solve의 50개 지정 CurrentPlot을 bare CurrentPlot으로 바꿔 실제 내부 시점 전체를 기록한다. 따라서 기존 기록 방식과 다른 N1 대조를 새로 실행해야 한다. 한 단계와 다음 단계 사이에는 MaxStep만 다르다. 기록된 시각이 실제 accepted step과 일치하는지 로그로 검사한다.

## 고정 입력과 재현 범위

- 기준: 현행 fin7, 소자 설계 C2, topology Z, 2D gb2_zz, II ON.
- Cs 4.2 fF, AreaFactor0.1, 300 K, Hurkx + vanOverstraeten 기본 구동력, 전체 구간 동일.
- BL 0.55 V, 피해 WL0 V, 공격 WL0↔1.8 V, 188 ps 주기×10회.
- SN reset 130–140 ps와 모든 기존 바이어스·초기 상태·접촉·물성을 그대로 둔다. 자연 precharge는 Claude P2에서 따로 검증한다.
- 메시 SHA-256: `aa0f32997e339c589882542dee7ead8919a2003459f94da75d86bc6d5606d0b2`.
- 기존 입력 대비 변경 whitelist(실행 이름, 저장 방식, MaxStep) 검사 통과. 기존 CxS4/8 4건의 SN 손실·body 상승을 독립 코드로 재추출하여 기존 추출기와 1e-9 mV 이내 일치 확인.
- 과거 gr/gx 메시가 아닌 현행 gb2_zz 실물 메시를 재검사한다. Lg100/Tbody20/Tox5/Tg20/isolation30/spacer25 nm, 접합50/175 nm, N+1e20/p1e18, 7개 접촉, 두 층×3개 높이를 확인한다.
- HfO2/Si3N4, 300 K, SRH·Hurkx 계수·II 구동력은 기존 가정이다. 새 물리값을 추가하지 않는다. R은 실험 변수에 포함하지 않는다.

Cho Sec.III/V, Fig.2/5/6/7과 캡션을 재검토했다. 사용자 소장 Fig.6의 BL/VWL/공격 펄스와 Fig.7의 II ON 비교를 확인했다. 본 배치는 기존 2D+강제 초기 상태에서 수치 오차를 가르는 진단이며 원문 자연 precharge 재현 실행으로 표시하지 않는다.

## 사전 조건과 판정

등록 후 실제 구조·해시·접촉 점검의 모든 줄을 읽고 통과 기록을 남긴 뒤 시작한다. 배치 직전 계정 live run과 quota를 다시 확인한다. 21:57의 읽기 전용 점검에서는 sdevice 없음, 사용량7646/9216 MB였다. 6건 최소240 MB 여유와 실제 디스크를 시작 전에 재확인한다.

추출 지표: SN endpoint 및 같은 위상 주기별 잔류 손실, attack−idle, body 중심 전위(첫 펄스/최대/종료), 정공 수, 전류 성분 합, CsΔV+∫I, 실제 스텝 수/간격/실패 횟수. 사다리꼴 적분과 우측 적분을 병기한다. BE 수지 해석은 저장시점과 실제 solver 스텝의 정렬을 확인한 후에만 적용한다.

수치 차이 목표는 body6 mV, 마지막5주기 순손실 기울기0.0012 mV/cycle 이하를 우선 사용한다. 극소 순손실의 부호를 물리 현상으로 주장하려면 더 작은 오차가 필요하다. 연속 refinement와 메시 검증을 마치기 전에는 P1 완료로 선언하지 않는다. h/8 또는 Newton 허용오차 검증 필요성은 이번 결과에서 결정한다.

자동 기록: 서버 `live_status.json`, `completed_analysis.json`, 실행별 `exit_code.txt`, PLT/TDR 및 압축 solver 로그. 이는 파일 기록이며 자동 메시지 알림이 아니다.

소유권: Codex 전용 폴더만 사용한다. Claude의 3D 배열·메시·덱·큐는 변경하지 않는다. 같은 조건의 중복 실행을 방지하기 위해 이 문서를 공유 Git의 `docs`에 등록한다.
