# Claude 인계: FBE 초기화·공간분포 진단

2026-10-06 17:54 KST 스냅샷. 데이터와 해석은 RESULTS_SNAPSHOT.md 및 각 batch analysis.json에 있다.

## 먼저 확인할 결론

1. 약1050/1300개 중 하나를 저자의 초기전하로 확정하지 않았다. A1 수치 변경에도 Case1의 첫 손실 부족은 남았다.
2. A3 Case1 두 조건이63.14ns까지 정상 종료했다. 장기SN고정을 풀면정공수/중심전위는대조와거의같지만,첫BL하강전SN이약31/38mV낮아졌다. 현재 균일pair-generation 초기화는SN외부보충에의존해1.1V를유지했다.
3. 약1300조건의전체손실56.27mV를논문첫손실약55mV와같다고판정하지말것. 38.42mV는BL토글전손실이며첫BL-low추가손실은17.85mV다. body rise606.94mV도논문약555mV와다르다.
4. A2 SetConstant→ReadFromFile 균일source동등성이Case1/2에서검증됐다. BL/SN집중source6개가준비됐지만동일전위sizing및pulse실험은아직미실행이다.

## 덱과 측정 정의

A3는A1대조와같은생성률·시간함수·균일공간분포·Cs·II·BL/WL파형·수치간격을사용한다. SN고정해제만20.64ns→0.14ns로이동했다. 초기SN고정0.13..0.14ns의10ps는남겼다. 생성은0.34..20.14ns와0.1ns ramp다. tS=21.14ns,21ns주기,2주기끝63.14ns. BLedge MaxStep5ps/plateau50ps; BL전환전최대간격은기존설정이다.

정공수는2D body∫p에폭0.1µm를곱해환산한다. 순전하는전자/이온화도핑도포함하므로정공총수와같지않다. body potential은현재중심ElectrostaticPotential이며평형기준/초기화후기준을모두보존한다. 저자의정확한기준은미확인이다. SN손실은토글전hold,첫BL-low추가손실,초기화부터총손실을분리한다.

A2 DeviceUG p.668–669/673의ReadFromFile와TimeDependence Scaling을사용한다. 프로파일은단위cm^-3 s^-1이며장치메쉬는동일하다. source용TDR의전위/density를restart초기상태로읽지않는다. 전체body x50..175nm,BL측50..75nm,SN측150..175nm. vertex보간으로경계전이가있으므로총발생량을추가확인해야한다.

## 다음에 필요한 작업

- 서버A3 Case2완료결과를읽고동일분석으로갱신. 저장소partial파일로200ns나완료상태를추정하지않는다.
- 같은중심전위에서전체/BL측/SN측3분포를no-pulse sizing. NtA를1050으로강제하지않고결과로읽는다. 공간source는진단가설이지저자의실제GIDL분포가아니다.
- 동일전위pulse실험에서pre-edge/mid-edge/post-edge/first-low끝의p/n,ψ/준페르미/밴드장벽/전류를확인. 준비된파일이검증됐다는사실만으로새소자실행을자동시작하지않는다.
- 최종적으로자연BTBT/avalanche가해당초기상태를만들수있는지검증. 보정Cs와2D폭·본문기하Cs의대응및저자초기화를추가확인해야한다.

## 출처와 소유권

Cho et al. IRPS2026 DOI10.1109/IRPS61424.2026.11499232, III/IV/VI 및Fig.2/4/5/7/8. 논문구조의3Darray/기하커패시터와현재2D집중Cs를혼동하지않는다.

Lee et al., Monolithically Stackable 1T1C 3-D DRAM: A Technical Survey, IEEE TED73(3),2026,Sec.II-B/Fig.3: GIDL정공이floating body에쌓여기생n-p-n BJT를바이어스하고BL변화에서스파이크가난다는메커니즘. 이설명은특정Sentaurus계수,인위적pair-generation,SN장기고정의근거가아니다.

이패키지입력·결과는Codex전용실험의스냅샷과읽기전용으로복사한Claude의Dh1/Dfin대조다. 원본프로젝트의Claude덱·NOTES·공유비교표는수정하지않았다. 연구추가파일은새디렉터리/커밋으로작성하고원시데이터는보존한다.
