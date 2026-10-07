# fin3 720개 개선 실험 실행 전 점검

2026-10-07 Cho IRPS2026 원문 III/VI, Fig.2/4/5/8의 p2/p3/p5 이미지와 p4 본문을 다시 확인했어요. Lg100/Tox5/Tgm20/dVOX30nm, body30/20/10nm, spacer25nm, Nsd1e20/Nch1e18 또는1e16, WF4.7/5.0V를 유지해요. 접합50/175nm, body40..70/60/50nm는 새 svisual cutline으로 확인해요. HfO2/Si3N4,300K,SRH 및 Hurkx A1.7e21/B2.25e7은 기존 가정/보정값으로 유지해요. 저자의 공개값으로 승격하지 않아요.

720=5Cases×12준비조건×3SN초기화×2II×2Cs예요. 준비조건은 자연 생성 유지시간(20.6/16.2/19.6/18.7/14.6us)의0.8/1/1.2배와, 외부 pair source의 uniform/BL25nm/SN25nm×fin3 Case별GBQ배수의0.8/1/1.2배예요. 국소 source는 부피보상5배를 사용하며 실제 생성 적분을 따로 읽어요. 자연 생성도 긴 유지와 SNclamp의 영향이 있으므로 논문에 명시된 초기 이력으로 단정하지 않아요.

fin3 읽기는 gate 아래x75..175nm,y40..(40+Tbody)nm의 평균 ElectrostaticPotential에서 과도 초기 평형값을 빼고 BL하강 완료0.25ns뒤(tS+0.75ns)에 측정해요. 저자의 미공개 정의를 역산한 후보예요. 전체9주기,200ns를 모두 계산해요. 몸체±30mV,first/200ns±0.3decade(Case5first±1mV)는 진단 허용오차예요. 모든Case를 각각 판정하며 첫low와200ns손실, 전하 수지를 동시에 보고해요. 쓰기 기준은 WL중간전압 통과시각으로 맞춰요. 200ns의 paper-axis 및 Claude-tool 시각 차이를 모두 기록해요.

fin3완료baseline5개와 자체생성F3N5개만 재사용해요. 신규 solver는710개예요. 기존720개 출력은 재사용하지 않아요. 원본논문 구조와 새mesh/source24개,720개 입력 조건을 확인하고 모든PASS를 읽은 뒤 시작해요. 실행마다SHA와quota512MiB여유를 재확인해요. 새큐는8workers×4threads,건당6h상한이에요. 원시출력은 로컬 복사SHA검증 뒤에만 서버에서 정리해요. 기존720큐는 새큐 시작 확인 뒤 중단하고 후보에서 폐기해요. Claude Round15 RH/3D작업과 F3N자체생성5개는 건드리지 않아요.
