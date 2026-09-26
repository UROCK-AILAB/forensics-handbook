---
title: "통합 로그에서 찾을 것"
parent: "아티팩트 · 로그"
nav_order: 1710
has_children: true
has_toc: false
---

# 통합 로그에서 찾을 것 (Unified Log Events)

통합 로그 (Unified Log)는 macOS 가 시스템 전체의 로그 메시지를 한곳에 모아 두는 기록이고, 로그인·잠금·관리자 권한 사용·원격 접속처럼 사람이 맥에서 한 일을 프로세스와 서브시스템, 메시지 문구로 골라내 사고 대응과 탐지에 씁니다.

## 왜 중요한가

통합 로그는 macOS 10.12 Sierra 에서 들어왔고 [1][2], 그 뒤로 로그인 창·보안 데몬·sshd 같은 여러 프로세스가 같은 저장소에 메시지를 남깁니다. 그래서 언제 로그인했는지, sudo 로 무엇을 실행했는지, SSH 나 화면 공유 접속이 있었는지를 한 저장소에서 시간순으로 찾아볼 수 있습니다 [2][5]. 기록은 프로세스·서브시스템·카테고리·메시지 문구 같은 조건으로 골라내는데 [4], 어느 조건을 걸어야 원하는 기록이 나오는지는 이 허브 아래 페이지들이 주제별로 정리합니다.

기록이 늘 남아 있지는 않습니다. 디스크 저장소가 정해진 크기를 넘으면 오래된 메시지부터 지워지니 [3], 오래된 기록은 기간이 아니라 크기 기준으로 밀려납니다. 보관 기간은 대략 28~30일, 기록은 3천만~5천만 건 정도라는 관찰이 있지만 [2], Apple 이 정한 값은 아닙니다.

메시지 수준에 따라서도 남는 범위가 다릅니다. Debug 수준은 메모리에만 있고, Info 수준은 `log` 도구로 수집할 때만 남으며, Default·Error·Fault 수준은 저장 한도까지 디스크에 남습니다 [3]. 그래서 디스크 이미지에서 기본으로 찾을 수 있는 기록은 Default·Error·Fault 수준이고, Info·Debug 로 찍힌 메시지는 사후 분석에서 없을 수 있습니다.

사용자 이름 같은 값이 가려져 있을 수도 있습니다. 기본값으로 정수·실수·불린은 그대로 두고 동적 문자열과 복잡한 객체는 가리며 [3], 출력에는 `<private>` 로 나옵니다 [4][5]. 가린 값을 보이게 하는 구성 프로파일을 설치할 수 있지만 설치한 뒤의 기록부터만 적용되고, 그 전에 남은 기록은 풀리지 않습니다 [5].

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 위치 | 로그 본문(`.tracev3`)은 `/private/var/db/diagnostics/` 아래 `Persist`, `Special`, `Signpost`, `HighVolume`, `timesync` 폴더, 보조 파일(문자열·메타데이터)은 `/private/var/db/uuidtext/` 아래 [1][5]. `/var` 는 `/private/var` 의 심볼릭 링크라 `/var/db/...` 로도 보입니다 |
| macOS 버전 | 10.12 Sierra 부터. 버전별 차이는 아래 표 |
| 알려 주는 것 | 로그인·세션, 로그인 키체인 잠금 해제, sudo 실행, SSH·화면 공유 접속, TCC 권한 위반 등(메시지를 남긴 프로세스·서브시스템·시각과 함께) [2][5] |
| 알려 주지 않는 것 | 디스크에 남지 않은 Debug·Info 메시지, 가려진(`<private>`) 값, 크기 한도로 밀려난 오래된 기록 [3][5] |
| 시각 | 항목마다 mach continuous time 을 쓰고, `timesync` 파일의 부팅 정보와 시스템 시계(wall clock) 값으로 실제 시각을 계산합니다. 헤더의 시스템 시계 값은 유닉스 시각(UTC)입니다 [1][5] |
| 보는 법 | `log show`(아카이브는 `--archive`), 실시간은 `log stream`, 아카이브 만들기는 `log collect` [4]. 공개 파서 예로 Mandiant `macos-unifiedlogs` 가 있습니다 [5] |

통합 로그 형식의 버전별 차이는 아래와 같습니다.

| macOS | 차이 |
|---|---|
| 10.12 Sierra | 통합 로그 도입 [1][2] |
| 12 Monterey | `/private/var/db/uuidtext/dsc` 의 UUID 파일 형식이 바뀌고, tracev3 에 Simpledump 이벤트 유형이 더해짐 [5] |
| 13 Ventura | libyal 형식 문서가 시험한 마지막 버전 [1] |
| 14 Sonoma 이후 | 형식 변화에 대한 공개 자료 없음 |

파일 구조와 시각 계산은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md) 에서 다룹니다.

## 읽는 순서

1. [로그인·로그아웃 (Login·Logout)](login-logout.md) — loginwindow·logind·securityd 기록으로 로그인과 세션 생성·종료, 로그인 직후 자동 실행된 항목을 찾습니다.
2. [잠금·잠금 해제·잠자기 (Lock·Sleep)](lock-sleep.md) — 잠금 해제 실패와 Apple Watch 잠금 해제를 찾는 조건과, 잠자기·깨우기 기록을 함께 보는 법을 다룹니다.
3. [관리자 권한 사용 (sudo·Authorization)](sudo-authorization.md) — sudo 로 실행한 명령과 TCC 권한 위반, 계정 DB 쪽 기록을 찾습니다.
4. [원격 로그인 (Remote Login)](remote-login.md) — sshd 와 화면 공유 프로세스의 기록으로 원격 접속과 인증 성공·실패를 찾습니다.
5. [자주 쓰는 검색 조건 (Predicates)](predicates.md) — `log show --predicate` 에 쓰는 키와 연산자, 앞 페이지들에 나온 조건을 표 하나로 모읍니다.

## 함께 볼 페이지

- [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md) — `.tracev3`·uuidtext 구조와 시각 계산
- [예전 시스템 로그 (ASL·syslog)](../../../01-foundations/data-formats/asl-syslog.md) — 10.12 이전 맥을 조사할 때
- [통합 로그의 프로세스 실행 기록 (Process Events)](../../execution/unified-log-process.md) — 프로그램 실행 쪽 기록
- [전원·잠자기 기록 (pmset)](../power-events.md) — 잠자기·깨우기 이력을 따로 볼 때
- [감사 로그 (OpenBSM Audit)](../openbsm-audit.md) — 로그인·권한 사용을 다른 기록으로 맞춰 볼 때
- [로그인 창 설정 (loginwindow)](../../system-account/loginwindow.md)
- [원격 접속 (Remote Access)](../../network/remote-access/index.md)
- [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md) — 켜진 맥에서 `log collect` 로 아카이브를 뜰 때
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)
- [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../../../04-scenarios/activity/usage-time.md)
- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)
- [원격 접속 침입 확인 (Remote Intrusion)](../../../04-scenarios/incident/remote-intrusion.md)
- [권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)](../../../04-scenarios/incident/privilege-tcc-bypass.md)

## 참고 문헌

1. libyal dtformats — Apple Unified Logging and Activity Tracing formats — https://github.com/libyal/dtformats/blob/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
2. CrowdStrike — How to Leverage Apple Unified Log for Incident Response — https://www.crowdstrike.com/blog/how-to-leverage-apple-unified-log-for-incident-response/
3. Apple Developer — Generating Log Messages from Your Code — https://developer.apple.com/tutorials/data/documentation/os/generating-log-messages-from-your-code.json
4. log(1) man page (Xcode man pages 모음) — https://keith.github.io/xcode-man-pages/log.1.html
5. Mandiant(Google Cloud) — Reviewing macOS Unified Logs — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
