# A2 공간 생성 방법 점검 — 2026-10-06

## 지금 실행하는 범위

몸체 전체에 균일한 프로파일을 파일로 읽는 조건이 기존 region SetConstant와 같은 상태를 만드는지 Case1/2에서 먼저 확인한다. **BL/SN 집중 생성의 본실험이나 전위 보정 실행은 아직 시작하지 않는다.** 두 실행은 BL pulse가 없는21.14ns 초기화 확인이다. 원문 Fig.8 파형을 재현하는 본실험으로 보고하지 않는다.

## 논문·구조 대조

이번 작업에서 Cho 원문 p.2 III절/Fig.2/4, p.3 Fig.5/IV, p.4 VI, p.5 Fig.8을 다시 읽었다. 원문은3D array/기하 커패시터이고 이번은2D 진단이다. Lg100/Tox5/Tgm20/dVOX30nm, body30/20nm, S/D1e20/channel1e18cm^-3, WF4.7eV에 해당하는 현행 gr_c1h/gr_c2h 메쉬를 유지한다. 접합50/175nm와 body수직경계40..70/40..60nm를 다시 점검한다. gate는75..175nm다.

HfO2/Si3N4,300K,abrupt profile,Hurkx계수와II on은 현재의 가정/사용자 기준이다. Cs는 본문5.1/4.2fF가 아니라 기존 보정값2.185714/1.8fF이므로 명시조건 재현으로 취급하지 않는다. SN 장기고정과 pair-generation은 저자가 공개한 초기화 조건이 아니다.

## 설치 버전의 공식 구현 근거

Sentaurus Device U-2022.12 UG p.668–669: `File OpticalGenerationInput`과 `OpticalGeneration ReadFromFile(DatasetName=OpticalGeneration)`로 공간 source를 읽는다. p.673: transient Scaling은 TimeDependence 내부에서 지정한다. 기존 method 바깥의Scaling=0은 DC/quasistationary의 source 억제를 유지한다.

TDX U-2022.12 UG의 TdrDatasetSetName/SetQuantity, TdrDataGetCoordinate/SetComponent, TdrFileSave로 기존 Band2BandGeneration 필드의 **동일 생성률 단위 cm^-3 s^-1** 데이터 공간에 진단 프로파일을 작성했다. 저장 파일은 별도OpticalGenerationInput으로만 쓰며 장치 Grid는 기존 공유 메쉬다. source 파일의 다른 전위·density는 초기 상태로 로드하지 않는다.

프로파일6개: Case1/2 × 전체body(x50..175nm)/BL측25nm(x50..75)/SN측25nm(x150..175). 파일상의 amplitude1e26은 규격화 수치이며 이번uniform검증은TimeDependence Scaling=기존Gb/1e26으로 동일 생성률을 사용한다. BL/SN25nm는 진단 window로서 저자의 실제 GIDL 위치로 확정하지 않는다. source는vertex보간되므로 단면 검증에서경계±1nm를 제외하고 plateau/외부0을 확인한다. 해당 보간과 실제 발생 총량은 sizing에서 추가 확인해야 한다.

## 검증 순서

1. source6개 단면 plateau 및 외부/peak<1e-5 확인(경계±1nm 제외); 실제 단위·body좌표 로그 검토. CSV에서 미세한 보간 잔여값이 있어 외부의 수학적 정확한0으로 판정하지 않는다.
2. 메쉬의 접합·도핑6개와body두께2개를 서버에서 재검증하고 전 항목을 읽는다.
3. manifest승인·source/hash·mesh/hash·덱/hash를guard에서 확인한 후 uniform2개만 실행.
4. A1의같은시점(tS−1ps)ψ·N과 비교. ψ차이≤5mV/N차이≤1%가 내부 방법 검증 기준이며 논문 오차가 아니다. 미통과시 spatial source 도입 문제를 먼저 해결한다.
5. 방법 검증을 확인한 뒤 각 분포를같은몸체전위로맞추는no-pulse sizing과6개pulse본실험을 준비한다. 이큐는 이를자동실행하지않는다.

Lee survey Sec.II-B/Fig.3의 GIDL 정공 축적→기생n-p-n BJT→BL전환스파이크는 자연메커니즘의근거다. 임의source나profilewindow를저자가썼다는근거가아니다.
