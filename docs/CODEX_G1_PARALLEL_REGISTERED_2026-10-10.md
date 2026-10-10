# G1 병렬 검증 등록 — 2026-10-10

사용자 요청 “더 빠르게 끝내고 싶어”에 따라 실행 대기를 없애되 수치 기준을 유지한다. h/16 baseline attack/idle 2건과 h/8 메시 두 후보 attack/idle 4건을 동시에 실행한다. 총6건×4 threads=24 threads. 서버128 logical CPU, 최근 CPU idle71%, 가용 RAM약227GiB, quota7768/9216MB를 확인했다. 예상 RAM12GiB, 추가저장500MB이며 첫 판정6–10시간은 추정값이다.

공동 계획의 P1 순차 실행을 계산상 독립한 검증의 병렬 실행으로 변경한다. h/8→h/16이 통과해야 h/8 메시 비교를 확정에 사용할 수 있다. 실패하면 메시 결과는 예비 자료로 남긴다. 비교 기준이나 주기 수를 줄이지 않는다. 모두 end2.125ns, 10cycles다.

- CxN16Atk/Idle: baseline gb2_zz에서 h/8의 50개 MaxStep과 InitialStep을 절반으로 줄인다. 기존 초기/최대 step 비율을 유지해 InitialStep>MaxStep이 되는 것을 막는다. MinStep/Newton/Physics 그대로다.
- CxMJ8Atk/Idle: gb2j_zz 42745 vertices, h/8 시간 설정 유지. 접합·body refinement만 변경한다.
- CxMA8Atk/Idle: gb2a_zz 61261 vertices, h/8 시간 설정 유지. 위에 채널·interface refinement를 추가한다.
- 기존 h/4,h/8 완료 결과를 재사용한다. 6건 모두 floating/II ON, Cs4.2fF, SN diagnostic reset 유지. Grounded body 제외는 계속 적용한다.
- 메시 SDE diff에서 기하·도핑·접촉은 완전히 같고 refinement만 다름을 확인했다. 원문 p2–5 본문·그림을 새로 읽고 실제세메시 contact/접합/도핑/치수를 preflight로 점검한다. 모든 줄 검토와 review_gate 등록 후 실행한다.

종료 판정은 time4→8,time8→16, meshbase→j,meshj→a의 연속 비교를 사용한다. body6mV, write6mV, 기울기0.0012mV/cycle 기준을 유지하고 accepted endpoint/BE 전하 수지를 검사한다. 자동 결과의 G1_numerical_candidate는 최종 G1 승인과 구분하며 독립 raw/hash audit가 필요하다. P2/P6는 자동 실행하지 않는다.

서버: ~/vblhwl_3d_dram/codex_validation/g1_parallel_20261010_01. manifest.json에 전체 해시·변수·자원·기준을 등록했다. live_status.json/completed_analysis.json에서 진행을 확인한다. 같은 조건의 별도 Claude 실행은 하지 않는다.
