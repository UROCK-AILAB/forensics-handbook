---
title: "실행 에이전트·데몬"
parent: "아티팩트 · 자동 실행·지속성"
nav_order: 560
has_children: true
has_toc: false
---

# 실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)

실행 에이전트 (LaunchAgent)와 실행 데몬 (LaunchDaemon)은 launchd가 부팅이나 로그인 때 plist 설정을 읽어 띄우는 작업이고, macOS에서 프로그램을 자동으로 실행하게 만드는 자리라서 지속성을 조사할 때 먼저 봅니다.

## 왜 중요한가

에이전트와 데몬은 사실상 같은 것이고, 에이전트는 로그인한 특정 사용자에 속해서 그 사용자가 로그인해 있을 때만 돌고 데몬은 시스템 전체에서 돕니다 [1][2]. 둘 다 plist 파일 하나로 설정하고, 그 파일이 정해진 폴더에 놓이기만 하면 부팅이나 로그인 때마다 launchd가 읽습니다 [2]. 사고 대응에서 재부팅한 뒤에도 무언가가 계속 실행되게 만든 흔적은 이 폴더들에서 먼저 찾습니다.

해석은 조심해야 합니다. launchd는 기본으로 필요할 때 작업을 띄우는 방식(on-demand)이라서, 클라이언트 쪽에서는 서비스가 늘 있는 것처럼 보여도 실제 프로세스는 돌고 있을 수도 아닐 수도 있습니다 [2]. plist가 있다는 사실과 그 작업이 실행됐다는 사실은 따로 확인해야 하고, 켜져 있는지 꺼져 있는지도 plist 밖에 저장될 수 있습니다 [3]. macOS 13부터는 백그라운드 작업 관리(BTM)가 이런 등록을 따로 추적하고 시스템 설정의 일반 → 로그인 항목 화면에 보여 주므로 [4], 최근 검체에서는 폴더의 plist와 등록 기록을 함께 봅니다.

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 위치 | `~/Library/LaunchAgents`, `/Library/LaunchAgents`, `/Library/LaunchDaemons`, `/System/Library/LaunchAgents`, `/System/Library/LaunchDaemons` [1]. macOS 13 이후에는 앱 번들 안 도우미도 있음 |
| 등록 기록 | `/private/var/db/com.apple.backgroundtaskmanagement/BackgroundItems-v*.btm` (macOS 13 이후) |
| 형식 | plist(작업 설정), NSKeyedArchiver 바이너리 plist(BTM 기록) |
| macOS 버전 | 다섯 폴더는 man 페이지 [1] 기준, 앱 번들 안 도우미(SMAppService)와 BTM은 macOS 13부터 |
| 알려 주는 것 | 실행 파일과 인자, 실행 조건, 시스템 전역인지 사용자별인지, (BTM) 등록 항목과 켜짐·허용 상태, 팀 ID·번들 ID |
| 알려 주지 않는 것 | 실제로 실행됐는지와 몇 번 실행됐는지, 누가 설치했는지, 설치 시각(plist 키는 실행 일정만 적고, BTM 항목 속성에는 시각 칸이 없음) |
| 라이브 확인 | `launchctl print`·`blame`·`print-disabled`, `sfltool dumpbtm` |
| 공개 도구 | DumpBTM(BTM 기록) |

## 읽는 순서

1. [위치와 적용 범위 (Locations)](locations.md) — 다섯 폴더와 앱 번들 안 도우미, 파일 소유자·권한 조건, 시스템·사용자 도메인, launchctl로 바꾼 비활성 상태가 어디에 남는지를 정리합니다.
2. [plist 키 해석 (ProgramArguments·RunAtLoad·KeepAlive)](plist-keys.md) — 무엇을 실행하는지와 언제 실행하는지를 정하는 키를 표로 풀고, `Program` 과 `ProgramArguments` 를 헷갈리는 함정과 잠자기에 따른 일정 실행 차이를 다룹니다.
3. [백그라운드 작업 관리 (BTM·Background Items)](background-task-management.md) — macOS 13부터 생긴 `.btm` 등록 기록의 구조와 type·disposition 비트, MDM 규칙, `sfltool` 로 확인하는 법을 다룹니다.

## 함께 볼 페이지

- [로그인 항목 (Login Items)](../login-items.md) — BTM이 함께 관리하는 또 다른 자동 실행 자리
- [예약 작업 (cron·periodic)](../cron-periodic.md)
- [그 밖의 지속성 위치 (Login Hook·Authorization Plugin·Emond)](../other-persistence.md)
- [구성 프로파일 (Configuration Profiles·MDM)](../configuration-profiles.md) — BTM 관리 규칙이 들어오는 경로
- [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md) — plist와 NSKeyedArchiver 형식
- [통합 로그의 프로세스 실행 기록 (Process Events)](../../execution/unified-log-process.md) — 설정한 작업이 실제로 실행됐는지
- [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)
- [악성 코드 지속성 찾기 (Persistence)](../../../04-scenarios/incident/persistence.md)

## 참고 문헌

1. launchd.plist(5) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/launchd.plist.5.html
2. Apple, Daemons and Services Programming Guide — Creating Launch Daemons and Agents (2016-09-13) — https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html
3. launchctl(1) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/launchctl.1.html
4. Apple Platform Deployment — Manage login items and background tasks on Mac — https://support.apple.com/guide/deployment/manage-login-items-background-tasks-mac-depdca572563/web
