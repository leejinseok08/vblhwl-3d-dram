# 조합 스캔 실행 전 점검 — 2026-10-06

사용자가 가능한 조건 조합을 시뮬레이션하고 적절한 값 후보를 추리라고 지시했다. 이는 미확인 초기 상태/바이어스 이력을 진단하는 허가이며, 그 조건들을 논문 명시값으로 바꾸어 부르는 허가는 아니다.

Cho 원문 III/IV/VI와 Fig2/4/5/8 및 grounded control Fig7을 이번 배치 전에 다시 읽었다. 원문 렌더 p2/p3/p4/p5 전체와 p3/p4 본문을 대조했다. 치수/도핑/WF는 Fig5 Case1~5 고정, BL=1.1→0V/WL=0V, edge0.5ns 및 low10.5ns는 기존 Fig8 판독 기준을 유지한다. 자연 유지15.2/21µs는 논문 ns 이력과 다른 진단이다. 모델은 기존 보정 Hurkx A1.7e21/B2.25e7 파일 그대로, vanOverstraeten 계수 그대로이다. II on/off는 Fig8 사용 여부가 미명시이므로 분리하는 진단이며 기본 비교는 on이다. HfO2/Si3N4, abrupt,300K,수명은 현재 가정이다. 저자 Fig8 body 측정 위치/기준, 정공 초기화, SN reset 상세는 미확인이다.

유한 후보 공간: 5Case × 12preparations × 3SN × 2II × 2Cs =720. 연속 공간의 모든 값을 조사했다는 뜻은 아니다.

| 축 | 후보 | 근거/범위 |
|---|---|---|
| 자연 준비 | hold21ns/15.2µs/21µs, Gb0 | 논문 시간축/Claude round11의 막대 근접시간/NG 구간. 모든 조건에서 이후 BL 주기는21ns |
| 대리 준비 | uniform/BL쪽25nm/SN쪽25nm × GBQ×1/1.125/1.25 | 기존 막대/손실 진단과 그 중간. 대리 생성의 실제 정공 수는 결과에서 측정, 이름만으로1050/1300이라 부르지 않음 |
| SN | 초기10ps 설정후자유/hold끝0.5ns전까지고정/초기자유후하강직전10ps재설정 | 자유이력/기존몸체조건/전하와SN상태분리. 외부 공급 전하 및 hold평탄도도 별도 기록 |
| II | 기존계수 on/off | 미확인 사용여부 진단. 계수배수 변경 없음 |
| Cs | Case별본문5.1/4.2/3.6fF 및×1.8/4.2 | 본문/현재쓰기보정. Cs본문 후보는 쓰기 실패 여부 함께 평가 |

Grid는 원래 gr_c1h~gr_c4h TDR로 고정한다. 별도 OpticalGenerationInput은 초기 대리 source만 바꾸며 도핑/재료/Grid를 바꾸지 않는다. 25nm window에 rate×5를 적용해 명목 pair dose를 맞추며 실제 광생성 적분을 측정한다. source ramp와 mesh interpolation 때문에 같다고 가정하여 Nh를 고정하지 않는다.

실제 svisual 검사: 각 mesh의 body lo/mid/hi에서 접합50/175nm, Nsd1e20, Nch Case1~3 1e18/Case4~5 1e16, body40..70/60/50nm을 확인했다. 총12 horizontal +4 vertical 검사가 모두 통과했다. 4mesh×3source의 optical cutline12개도 지지구간과 외부0을 확인했다. stdout의24 PASS 줄을 전부 읽었다. 실제 mesh/source CSV 및 해시를 보존한다.

측정: Nh=body hDensity적분×2D폭. body electrostatic/quasiFermi 및 BL스페이서/게이트/중앙/SN쪽 모든 저장 probe를 재분석한다. 전위 기준은 평형과초기SNreset종료를 모두 기록하며 가장잘맞는정의를저자정의라고채택하지않는다. body BTBT/II/signedSRH/대리source 및전류e/h/displacement를 적분한다. SRH는순재결합; 연속식잔차는경계이동+수치오차다. 고정구간에서∫I=CsΔV를강요하지않고 외부노드보충전하를기록한다.

후보 점수: body±30mV, 첫low log오차±0.3decade(Case5 1mV), SN초기±5mV와hold평탄도±5mV, 첫low전하수지오차≤max(1%,1e-4fC). 판독오차/진단허용치이며모두논문명시허용치가아니다. Case2쓰기는12/24/39/60ps 개별±30mV로확인. 평균만맞는값을성공이라하지않는다. Case5target0/음수누설은명시한다. 5Case공통조합과Case별best를따로정렬하며자연이력과외부준비상태를구분한다. 최종 채택에는200ns곡선/IdVg/쓰기및필요한groundedcontrol재검증이필요하다.

Lee etal TED survey SecII-B/Fig3의 GIDL정공축적→기생npnBJT→BL전이전류스파이크 설명을 따르되, 그 설명은특정계수를정하지않는다. 이번배치는초기조건이설명을만족시킬수있는지찾는스캔이다.

자원: 이전Codex복구/NG큐모두완료,Claude새실행없음을등록부/서버로확인했다. 서버128CPU,available약240GB,load약3. 8workers×4threads로유한동시실행, 계정soft9GiB/hard10GiB/최소512MiB여유를매실행검사한다. 자체완료로그/PLT/TDR만무손실gzip+해시검증후원본대체. 압축결과는분석기가직접읽는다. 신규screen만6h walltime한도로부적합/수렴실패를기록한다. 다른프로세스중단없음. 입력잠금으로중복실행방지. 원문그림/PDF/설치매뉴얼은GitHub에올리지않는다.
