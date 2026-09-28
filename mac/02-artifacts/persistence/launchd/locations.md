---
title: "위치와 적용 범위"
parent: "실행 에이전트·데몬"
grand_parent: "아티팩트 · 자동 실행·지속성"
nav_order: 570
---

# 위치와 적용 범위 (Locations)

실행 에이전트·데몬의 설정 파일(plist)은 정해진 폴더 다섯 곳과 앱 번들 안에 놓이고, 어느 폴더에 있느냐에 따라 누가 넣는 자리인지와 어느 도메인(domain)에서 도는지가 갈립니다.

## 무엇을 기록하나 · 왜 생기나

에이전트와 데몬은 사실상 같은 것이고, 에이전트는 로그인한 특정 사용자에 속해서 그 사용자가 로그인해 있을 때만 돕니다 [2]. launchd는 부팅할 때 `/System/Library/LaunchDaemons/` 와 `/Library/LaunchDaemons/` 의 plist를 읽어 데몬을 등록하고, 항상 돌아야 한다고 적힌 데몬을 띄웁니다 [2]. 사용자가 로그인하면 `/System/Library/LaunchAgents`, `/Library/LaunchAgents`, 그 사용자의 `Library/LaunchAgents` 에서 에이전트를 읽어 등록하고, 마찬가지로 항상 돌아야 한다고 적힌 에이전트를 띄웁니다 [2].

그래서 이 폴더들에 놓인 plist 하나하나가 부팅이나 로그인 때 launchd가 읽는 자동 실행 설정이고, 파일이 어느 폴더에 있는지를 보면 그 작업이 시스템 전체에 걸리는지 사용자 세션마다 걸리는지를 알 수 있습니다. plist 안의 키가 무엇을 언제 실행하는지는 [plist 키 해석 (ProgramArguments·RunAtLoad·KeepAlive)](plist-keys.md)에서 다룹니다.

## 위치

launchd가 plist를 읽는 폴더는 아래 다섯 곳입니다 [1]. "누가 넣나" 칸의 괄호 안 영어는 man 페이지 문구입니다.

| 경로 | 종류 | 누가 넣나 (man 페이지 [1]) | 언제 읽나 [2] |
|---|---|---|---|
| `~/Library/LaunchAgents` | 사용자별 에이전트 | 사용자 (provided by the user) | 그 사용자가 로그인할 때 |
| `/Library/LaunchAgents` | 사용자별 에이전트 | 관리자 (provided by the administrator) | 사용자가 로그인할 때마다 |
| `/Library/LaunchDaemons` | 시스템 전역 데몬 | 관리자 (provided by the administrator) | 부팅할 때 |
| `/System/Library/LaunchAgents` | 사용자별 에이전트 | 운영체제 (provided by OS X) | 사용자가 로그인할 때마다 |
| `/System/Library/LaunchDaemons` | 시스템 전역 데몬 | 운영체제 (provided by OS X) | 부팅할 때 |

`/Library/LaunchAgents` 는 관리자가 넣는 폴더지만 여기 있는 에이전트도 사용자별(per-user)이라서, 로그인하는 사용자마다 그 사용자의 세션에 올라갑니다 [1][2]. 직접 만든 데몬의 plist는 `/Library/LaunchDaemons` 에, 에이전트의 plist는 `/Library/LaunchAgents` 나 사용자의 `Library/LaunchAgents` 에 설치합니다 [2]. 사용자 폴더는 계정마다 따로 있어서 이미지에서 찾을 때는 사용자 홈을 모두 돌아봐야 하고, 계정 목록은 [사용자 계정 (Local Accounts)](../../system-account/user-accounts/index.md)에서 얻습니다.

## 버전별 차이

macOS 13부터는 위 다섯 폴더 말고도 앱 번들 안에 도우미를 두고 등록하는 길이 생겼습니다. SMAppService(macOS 13.0 이상)는 앱 번들 안에 든 로그인 항목·에이전트·데몬 도우미를 등록하고 [4], 이렇게 설치한 plist에서만 `BundleProgram` 키를 쓸 수 있는데 이 키의 값은 앱 번들 기준 상대 경로입니다 [1].

| 항목 | macOS 10.15 ~ 12 | macOS 13 이후 |
|---|---|---|
| 앱 번들 안 도우미 (SMAppService) | 없음 | 앱 번들 안에 두고 등록 [4] |
| 등록 추적과 사용자 승인 | 없음 | 백그라운드 작업 관리가 추적 ([백그라운드 작업 관리 (BTM·Background Items)](background-task-management.md)) |

앱 번들 안 도우미는 다섯 폴더를 살펴봐서는 나오지 않으니, macOS 13 이후 기기에서는 백그라운드 작업 관리 기록의 `url` 을 따라가 찾습니다.

## 소유자와 권한

전역으로 설치한 데몬·에이전트 plist는 root 소유여야 하고, 사용자용 에이전트 plist는 그 사용자 소유여야 합니다 [2]. 어느 쪽이든 그룹과 다른 사용자에게 쓰기 권한이 없어야 하며, 파일 모드로는 `600` 이나 `400` 입니다 [2].

이 조건에서 벗어난 소유자나 권한은 문서 절차와 다른 방식으로 파일을 놓았다는 단서라서 기록해 둘 만합니다. 다만 현재 macOS가 조건에 맞지 않는 plist를 거부하는지, 거부할 때 어떤 로그를 남기는지는 시험 기기에서 재현해 확인하고, 그런 파일이 실제로 적재됐는지는 다른 기록으로 따로 판단합니다.

## 도메인 (적용 범위)

launchctl(1)은 서비스가 속하는 범위를 도메인으로 나누고, 대상은 아래 형식으로 가리킵니다 [3].

| 도메인 | 뜻 [3] |
|---|---|
| `system/` | 시스템 도메인. 루트 Mach bootstrap을 관리하는 특권 실행 영역 |
| `user/<uid>/` | 지정한 UID의 사용자 도메인 |
| `login/<asid>/` | GUI 로그인 때 생기는 사용자 로그인 도메인 |
| `gui/<uid>/` | 위 로그인 도메인을 UID로 가리키는 형태 |
| `pid/<pid>/` | 프로세스마다 붙는 PID 도메인 |

폴더 구분과 맞춰 보면 데몬 폴더의 plist는 시스템 도메인에서 돌고, 에이전트 폴더의 plist는 로그인한 사용자의 도메인에서 도는 것으로 보입니다. plist 안에서 실행 계정을 정하는 `UserName`·`GroupName` 키는 시스템 도메인에서만 쓰이고 [1], `LimitLoadToSessionType` 키는 에이전트에만 해당하며 어떤 종류의 세션에 적재할지를 제한합니다 [1]. 그래서 에이전트 plist에 `UserName` 이 적혀 있어도 그 계정으로 돈다고 읽으면 안 되고, 에이전트는 그것을 적재한 사용자의 세션에서 돈다고 봅니다.

## 비활성 상태가 저장되는 곳

plist의 `Disabled` 키만 보고 작업이 꺼져 있는지 판단하면 틀릴 수 있습니다. `launchctl disable`·`enable` 로 바꾼 상태는 재부팅한 뒤에도 유지되고 [3], 예전 방식인 `load -w`·`unload -w` 는 plist의 `Disabled` 키를 덮어쓰는데, 그 상태는 plist가 아니라 launchd 말고는 직접 고칠 수 없는 디스크의 다른 곳에 저장됩니다 [3].

라이브 시스템에서는 `launchctl print-disabled` 에 도메인을 주면 그 도메인에서 비활성으로 표시된 서비스 목록이 나옵니다 [3].

```
launchctl print-disabled system
launchctl print-disabled gui/<uid>
```

`Disabled` 키 자체의 뜻은 [plist 키 해석](plist-keys.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 폴더에 plist가 있으면 launchd가 부팅이나 로그인 때 읽을 수 있는 자리에 자동 실행 설정이 놓여 있었다는 뜻이고, 폴더에 따라 시스템 전역 데몬인지 사용자별 에이전트인지, 그리고 man 페이지 기준으로 누가 넣는 자리인지(사용자·관리자·macOS)를 말할 수 있습니다. 파일 소유자와 권한은 위의 설치 조건에 맞는지를 보여 줍니다.

**증명하지 못하는 것.** plist가 있다고 해서 그 작업이 실행됐다는 뜻은 아니고, 지금 켜져 있다는 뜻도 아닙니다. 비활성 상태는 plist 밖에 저장될 수 있고, 실행 여부는 실행 흔적을 따로 확인해야 합니다. 관리자 폴더에 있다는 사실도 "관리자가 넣었다" 는 man 페이지의 분류일 뿐이고, 실제로 누가 파일을 놓았는지는 알 수 없습니다.

## 함정과 한계

`/Library/LaunchAgents` 를 "시스템 전역" 폴더로 읽는 실수가 흔합니다. 이 폴더의 에이전트는 사용자별이라서 로그인하는 모든 사용자의 세션에서 따로 돌고 [1][2], 어느 사용자 세션에서 돌았는지는 사용자별 기록으로 따져야 합니다.

macOS 13 이후에는 앱 번들 안 도우미가 다섯 폴더 밖에 있으므로 폴더만 살펴보면 빠뜨립니다. `/System/Library` 아래 두 폴더는 macOS가 넣는 자리라서, 여기서 낯선 항목을 가려낼 때는 [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../../01-foundations/protection/codesign-notarization-sip.md)를 함께 봅니다.

## 직접 분석해 보기

디스크 이미지에서는 다음 순서로 봅니다.

1. 다섯 폴더와 모든 사용자 홈의 `Library/LaunchAgents` 에서 plist 목록을 뽑습니다.
2. 파일마다 소유자와 모드를 적고, 위의 설치 조건과 맞는지 표시합니다.
3. plist를 열어 실행 대상과 실행 조건 키를 읽습니다. plist 형식을 읽는 법은 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에 있습니다.
4. macOS 13 이후 기기면 백그라운드 작업 관리 기록과 목록을 맞춰 봅니다.

라이브 시스템에서는 위 `launchctl print-disabled` 로 비활성 목록을 확인하고, 실행 중인 서비스를 보는 명령은 [plist 키 해석](plist-keys.md)의 "직접 분석해 보기" 에 있습니다. 라이브 수집 절차는 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)을 봅니다.

## 교차 검증

- [백그라운드 작업 관리 (BTM·Background Items)](background-task-management.md) — macOS 13 이후 등록 기록과 폴더 목록을 맞춰 볼 때
- [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) — 폴더에 plist가 만들어지거나 지워진 기록
- [로그인 항목 (Login Items)](../login-items.md)
- [악성 코드 지속성 찾기 (Persistence)](../../../04-scenarios/incident/persistence.md)

## 참고 문헌

1. launchd.plist(5) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/launchd.plist.5.html
2. Apple, Daemons and Services Programming Guide — Creating Launch Daemons and Agents (2016-09-13) — https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html
3. launchctl(1) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/launchctl.1.html
4. Apple Developer, SMAppService (문서 JSON) — https://developer.apple.com/tutorials/data/documentation/servicemanagement/smappservice.json
