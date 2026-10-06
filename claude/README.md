# Claude 쪽 현황 · 실험 데이터 · 분석

Cho 외, "Row Hammer Effect and Floating Body Effect of Monolithic 3D Stackable 1T1C DRAM", IRPS 2026
(DOI [10.1109/IRPS61424.2026.11499232](https://doi.org/10.1109/IRPS61424.2026.11499232)) 소자의 2D 단면 재현 작업 중 Claude가 한 부분이에요.
Codex가 올린 파일(`docs/`, `fbe_joint_20261006/` 등)은 건드리지 않았고, Claude의 것은 모두 이 `claude/` 폴더 안에 있어요.

원본 프로젝트: PC `C:\Users\LEEJINSEOK\vblhwl_3d_dram`, 서버 `~/vblhwl_3d_dram` (Sentaurus U-2022.12).

## 읽는 순서

빨리 보려면 `reports/GT_IRPS2026_현황보고_eliU_2026-10-06_저녁.html`부터예요 (그림 6장, 쉬운 문장, 실제 용어).

1. [STATUS.md](STATUS.md) — 무엇이 재현됐고 무엇이 안 됐는지, 사용자가 정한 것, 지금 돌고 있는 것
2. [EXPERIMENTS.md](EXPERIMENTS.md) — **실험 등록부.** 끝난 것 / 돌고 있는 것 / 하지 않기로 한 것. 새 실행을 만들기 전에 양쪽이 먼저 보는 표
3. [ANALYSIS.md](ANALYSIS.md) — 그림별 분석, Codex 결과와 맞춰 본 것, 고친 판단
4. `data/tables/` — 도구가 낸 표 그대로 (점수표, FBE, 로우 해머, 쓰기와 WL 꺼짐, Id–Vg, 실행 상태, 실행 전 구조 검사 기록)
5. `data/runs/<실행 이름>/` — 원시 자료: 덱 `<이름>_des.cmd`, 실행 설명 `run.json`, 노드 전압 `<이름>_sys.plt`, 소자 탐침 `c1_<이름>_dev.plt`
6. `project/` — 덱 생성기와 도구의 스냅샷 (`make_runs.py`, `params.py`, 구조 템플릿, `tools/`, `NOTES.md`, `CLAUDE.md`)
7. `reports/` — eliU 형식 현황 보고서(저녁), 2D 완성 보고서(9절이 저녁 갱신), 논문 대비 비교표, 15시의 현황 보고서, 그림

## 자료를 다시 읽는 법

Python 3 표준 라이브러리만 있으면 돼요. `project/tools/gt_tran.py`의 `load()`가 `.plt`를 읽어요.

```bash
cd claude/project
ln -s ../data/runs runs            # 도구는 ./runs/<실행 이름>을 찾아요 (Windows에서는 폴더를 복사해도 돼요)
python3 tools/score2d.py -v fin2   # 최종 2D 구성의 점수표
python3 tools/rh_tab.py DfinRz_zz Dr2Rz_zz DtcRzg_zz
python3 tools/gt_wl_off.py Dj5F_c2 Dj7F_c2
```

실행 이름 규칙: `D<구성>I_c<n>` Id–Vg, `D<구성>W_c2` 쓰기, `D<구성>F_c<n>` FBE, `D<구성>Ry_yy / Ryi_yy / Rz_zz / Rzi_zz / Rzg_zz`
로우 해머(Y–Y' / Z–Z', `i` = 충돌 이온화 켬, `g` = 몸체 접지). 구성이 무엇을 바꾼 것인지는 EXPERIMENTS.md와 `project/make_runs.py`의 `cfg2d(...)` 줄에 있어요.

## 들어 있지 않은 것

- 논문 PDF, 논문 그림을 잘라 붙인 그림 (구조 대조 그림 `gt3_*_vs_cho_fig2*.png` 등). 논문에서 읽은 **수치**는 `project/tools/paper_targets.py`에 있어요.
- 메시와 저장된 필드(TDR), 로그. 메시는 `data/runs/_struct/*_dvs.cmd`로 다시 만들 수 있어요 (`sde -e -l <파일>`).
- 끝나지 않았거나 출력이 손상된 실행. 어떤 실행이 왜 빠졌는지는 `data/tables/run_state.txt`와 STATUS.md의 "서버 사고"에 있어요.
- 접속 정보, 계정 이름.
