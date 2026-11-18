# v0.91 배포 검수

| 구분 | 이번 결과 |
|---|---|
| 실제 EXE | 원본 CHD·GDI 각각 적용 → 50트랙 해시 전부 일치. 한글 경로, 실패/중단 처리 9사례 통과. |
| 레트로아크 | 1.22.2 + Flycast, 실제 EXE 적용 GDI, BIOS 부팅, OpenGL Core, 6,000프레임 후 일반 시합 메뉴 확인. |
| 화면 | 단체 선택 헤더 18곳·교정 선수 7명의 전체 프로필·K-1 별명 확인. 해당 화면 겹침/잘림 발견 0건. |
| 느려짐 | 단체 이적 첫 1/반복 5~6프레임, 격투가 첫 2/반복 8~9프레임, 문자판 5종 첫 1/반복 4프레임. |
| 정적 검수 | 테스트 63개, UI 폭 2,237조건, 원본 대조 압축 스트림 243개 통과. |
| 변경 범위 | 0.901 대비 문구/선수 이름/굿 글리프만 변경. 경기·입력 코드, DLC 기술 동작, 기존 글리프/이미지/애니메이션 동일. |
| 원본 보존 | 일본판 CHD SHA-256 동일, 50트랙 배치·오디오 47개·IP.BIN 유지. |

[수정 전체 표·새 스크린샷·측정 범위](FEEDBACK_0_91.md) · [EXE](patcher-verification.json) · [레트로아크](retroarch-v091-verification.json) · [선수 선택](fighter-performance.json) · [단체 이적](transfer-performance-v091.json) · [문자 입력](input-performance.json)

모든 메뉴·임의 입력·드문 오류 화면·모든 기술의 개별 시전을 전수 검사한 결과는 아닙니다. 실물 드림캐스트와 VMU 저장 후 재부팅 검증은 미완료입니다. 기존 글리프/조합 검사는 [0.901 기록](https://github.com/OldManCraveGuitars-bit/DC-Fire-Pro-Wrestling-D-Kr/blob/v0.901/docs/VERIFICATION.md)에 있으며 관련 코드는 이번 버전에서 바이트 동일함을 확인했습니다.
