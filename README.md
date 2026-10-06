# VBL/HWL 1T1C DRAM 재현 실험 공유

Cho et al., **Row Hammer Effect and Floating Body Effect of Monolithic 3D Stackable 1T1C DRAM**, IRPS2026, DOI [10.1109/IRPS61424.2026.11499232](https://doi.org/10.1109/IRPS61424.2026.11499232)의 재현 과정에서 수행한 Codex 독립 진단 실험과 Claude 대조 데이터다.

**스냅샷: 2026-10-06 17:54 KST. 논문 전위·손실의 동시 재현은 미완료다.**

먼저 [Claude 인계 문서](docs/CLAUDE_HANDOFF.md)와 [실험 요약](docs/RESULTS_SNAPSHOT.md)을 읽는다. 완료된 원시 파형과 진행 중에 동결한 파형을 함께 보존했으며, 정확한 상태는 [snapshot_status.json](snapshot_status.json)에 있다. 실행 중이던 서버 작업은 계속 진행되므로 저장소의 상태가 이후 서버 상태와 같다고 가정하지 않는다.

| 배치 | 완료 / 전체 | 내용 |
|---|---:|---|
| A1 | 4 / 4 | BL 전환 이후 시간 간격 및 출력 간격 검증 |
| A3 | 2 / 4 | SN 장기고정과 10ps 초기화 후 해제 비교 |
| A2 입력 방법 | 2 / 2 | 같은 균일 생성의 region 상수 방식과 파일 입력 방식 비교 |
| 기존 조건 판별 | 5 / 9 | long hold·II·WL저항·aggressor/idle 판별 |

별도로 [reference_2d](reference_2d)에 Dh1/Dfin Case1~5의 200ns 대조 원시 파형·입력 10개와 감사 분석을 보존했다. 신규19개 가운데 완료13개, 미완료6개다. A2 BL/SN 집중생성의 동일전위 sizing과 pulse 본실험은 아직 시작하지 않았다.

현재 확인한 주요 결과:

- A1의 시간 간격 변경 후 첫 손실 차이는 최대0.059mV. 해당 수치 설정만으로 전위·손실 불일치를 설명하기 어렵다.
- A3 Case1에서 SN 고정을 풀어도 body 정공수는 거의 같지만 BL토글 전에 SN이30.92/38.42mV 낮아졌다. 그 뒤 첫BL-low 추가손실은2.51/17.85mV다. 토글 전 손실을 논문의 첫 토글 손실에 합쳐서 맞췄다고 보고하지 않는다.
- A2 균일source의 파일 입력은 Case1/2 모두 내부 동등성 기준을 통과했다. 중심전위차이0.107/0.096mV, 정공수차이0.038/0.035%다.
- 기존 R≈2e5Ω·IIoff의 aggressor 추가효과는 약0.105mV에서 포화했다. 지속적인 RH 손실 증가로 판정하지 않는다.

## 파일 구성

- `device_meshes/`: 실제 실행에 사용한 gr_c1h/gr_c2h/gr_zz 메쉬, 원본 해시 보존.
- `fbe_joint_20261006/{numeric_A1,free_sn_A3,spatial_A2}/`: 실제 실행CMD, run metadata, PLT/TDR, 원본 파라미터·SDE·분석 스크립트, 구조 및 source 점검 기록.
- `condition_discrimination_20261006/`: 기존 판별 실험9개의 입력과 완료/부분 결과.
- `reference_2d/`: Dh1/Dfin 10개 원시 데이터와200ns 감사 분석.
- `docs/`: 최신 스냅샷 분석과 인계, 과거시점별 보고서.
- `figures/`: 재분석 수치에서 작성한 비교 그림.
- `FILES_SHA256.json`: 공유파일 전체의 바이트 무결성 기록.

## 검증과 재분석

Python3 표준 라이브러리로 원시 데이터의 무결성과 분석 재생성을 검증할 수 있다. TCAD 라이선스는 아래 검증에 필요하지 않다.

```bash
python scripts/verify_package.py
```

실제 실행덱의 경로는 원래 서버 경로를 보존했다. 재실행 준비는 별도 `_replay`에 경로만 바꾼 덱을 만들며 시뮬레이션을 시작하지 않는다.

```bash
python scripts/prepare_run.py fbe_joint_20261006/free_sn_A3 FS_c1_q1050
```

재실행 환경은 Sentaurus U-2022.12다. 원문·그림 및 실제 메쉬 점검을 완료한 뒤 준비된 디렉터리에서 sdevice를 실행한다. 원래 manifest 해시는 실행 당시 원본 CMD를 가리키므로 경로를 변경한 재실행덱의 해시는 별도로 기록한다.

## 재현 범위

원문은3D array와기하커패시터를사용한다. 이번 신규FBE는2D 진단이며, 과도Cs는본문5.1/4.2fF 대신기존보정2.185714/1.8fF를사용했다. HfO2/Si3N4·abrupt profile·300K·Hurkx계수·인위적전자-정공쌍생성·SN고정은현재가정이다. FBE IIon은사용자기준이며Fig.8의저자선택은미확인이다. 이패키지는저자덱을복구했다는주장이아니다.
