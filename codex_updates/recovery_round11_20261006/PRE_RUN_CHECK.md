# 실행 전 원문·실제 메시 대조 — 2026-10-06

사용자 지시: 손상 출력 범위를 확정하고 원문·figure·구조 재검토 후 필요한 실행만 복구. Claude 라운드11의 몸체 정공, 전위, SN 유지/low 손실, 전류 적분, 생성·재결합 분리.

재검토한 원문은 Cho IRPS2026 III, IV, V, VI, VIII 및 Figs2/4/5/6/7/8이다. 사용자 보유 원본 렌더 p2/p3/p4/p5와 본문 p3/p4를 다시 읽었다. Fig2는 BL→25nm spacer 아래 body→100nm gated body→SN 접합이며 3D mini-array와 geometric Cs를 사용한다. Fig5는 Lg100/Tox5/Tgm20/dVOX30nm, Case1/2 Tbody30/20nm, Nsd1e20/Nch1e18 cm^-3, WF4.7eV. RH의 Fig6(e)는 II off, Fig7은 II on. FBE Fig8은 II 사용 여부·전위 위치·초기화 상세를 공개하지 않았다.

현재 모델은 2D 단면 및 집중 Cs 진단이다. HfO2/Si3N4, abrupt junction, 300K, SRH/Hurkx/II 미공개 계수는 현행 가정이다. Fig8의 막대 정공 조건, SN 재설정, 보정 Cs를 저자 명시값으로 쓰지 않는다. Lee 외 survey SecII-B/Fig3는 GIDL 정공 축적→기생 n-p-n BJT 바이어스→BL 변화 스파이크를 설명하지만 특정 Sentaurus 계수를 확정하지 않는다.

| 실행 | 유지하는 원래 조건 | 이번 변경 |
|---|---|---|
| RR_CDR_id_i0_idle | 2층 gr_zz, Cs4.2fF, Rwl1e-4Ω, IIoff, aggressor idle, 50cycles, end12.43ns | 출력 이름만 변경. 원본 손상 덱의 정확한 복구이며 physics/timing/solver 원문과 동일 |
| RR_FS_c2_q1300 | gr_c2h, Cs1.8fF, IIon, 기존 대리 생성, SN0.13..0.14ns 설정 후 자유 상태, end63.14ns | 출력 이름만 변경. 자연 GIDL 실험이 아니며 초기 상태 진단 복구 |
| NG_c1_21us / NG_c2_21us | Claude Dz3F Case1/2의 mesh/material/physics/coefficient/PWL/initial state 모두 유지. Gb0, IIon 기본계수, hold21µs, BLperiod21µs, edge0.5ns | 몸체 eDensity/BTBT/II/signed SRH 관측 추가. reset 뒤 plateau MaxStep1/4, 첫 하강과 직후5ps, 다음 구간20ps. 각 segment 출력100intervals. 첫 low끝31.50014µs에 종료 |

손상 범위: Codex 현행19실행의 sys/dev 파일과 CMD의 요청 출력 시점을 대조했다.17개는 검사 통과. CDR_id_i0_idle은 잘린 숫자·dev열 정렬/시간축 이상, FS_c2_q1300은 sys/devPLT 둘 다 없음. 기존 손상 데이터는 보존한다. TDR은 필요 분석량을 복원하지 못하므로 임의 PLT 보간으로 복구하지 않는다.

구조 검사: 동일 mesh SHA를 확인하고 svisual로 12개 수평 cutline을 새로 추출했다. 모든 층·lo/mid/hi에서 junction50/175nm, N+1e20/p1e18을 확인했다. 추가 수직검사: gr_c1h40..70nm, gr_c2h40..60nm, gr_zz40..60/140..160nm. 기존 저장 CSV만 재사용하지 않는다. source geometry/model/PWL 비교와 snapshot SHA는 manifest/guard로 잠근다.

현재 라운드11의 부족 출력: 전체 반도체 BTBT/II를 body hDensity 변화와 빼서 남는 양을 재결합으로 부를 수 없다. domain mismatch와 boundary flux가 섞인다. 추가 관측은 같은 body에서 ΔNh = ∫G_BTBT+∫G_II−∫R_SRH−net outward carrier flux로 읽는다. R_SRH는 부호 있는 순재결합이며 음수일 때 생성이다. 잔차는 경계 순유출과 수치 오차이지 재결합이 아니다. 단자 e/h/변위/총전류를 따로 적분하고 CsΔV와 확인한다. II가 켜져 있으므로 자연 생성 모두를 GIDL로 단정하지 않는다.

quota: 사용자별 soft9GiB/hard10GiB를 확인한다. 최소512MiB 여유를 남기며 Codex 최대2개만 동시 실행한다. stdout은 시작부터 gzip, 완료한 Codex canonical log도 hash검증 후 압축 보관한다. 다른 작업을 중단·수정하지 않는다. 완료 판정은 exit0 + sys/dev 행열·time coverage·requested samples이며 수치 전하 수지 오차는 별도 판정한다.
