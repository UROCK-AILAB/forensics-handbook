---
title: "악성 코드 지속성 찾기"
parent: "시나리오 · 침해 사고"
nav_order: 2550
---

# 악성 코드 지속성 찾기 (Persistence)

## 조사 질문

악성 코드가 재부팅이나 다시 로그인한 뒤에도 저절로 실행되도록 이 맥 어딘가에 자리를 잡았는지, 잡았다면 언제 어느 위치에 잡았는지 묻습니다. macOS 에서 자동 실행을 거는 자리는 실행 에이전트·데몬 (LaunchAgents·LaunchDaemons) 이 가장 흔하지만, 로그인 항목, 구성 프로파일, 예약 작업, 메일 규칙처럼 덜 알려진 자리도 여럿 있습니다 [1]. 이 페이지는 그 자리들을 어떤 순서로 훑는지를 다루고, 위치마다의 파일 구조는 아티팩트 사전의 자동 실행·지속성 갈래 페이지로 넘깁니다.

## 먼저 확인할 것

OS 버전에 따라 로그인·백그라운드 항목을 다루는 방식이 크게 다릅니다. macOS 13 이전에는 도우미 설치 스크립트가 plist 를 정해진 폴더에 직접 넣었고, macOS 13 부터는 백그라운드 작업 관리 (Background Task Management, BTM) 가 이 항목들을 관리합니다 [2].

| macOS 버전 | 달라지는 점 | 출처 |
|---|---|---|
| 10.9 Mavericks 이후 | StartupItems 가 없어졌습니다 | [1] |
| Mojave 까지 | LoginHook·LogoutHook 이 동작한다고 글쓴이가 적었습니다 | [1] |
| 10.15 Catalina 이후 | cron 을 쓰려면 사용자 허용이 필요합니다 | [1] |
| 12 이하 | 도우미 설치 스크립트가 plist 를 정해진 폴더에 직접 넣습니다 | [2] |
| 13 Ventura 이후 | BTM 이 로그인·백그라운드 항목을 관리합니다 | [2] |

`rc.common` 과 `launchd.conf` 는 더는 동작하지 않아서 [1], 요즘 맥에서 이 파일이 보여도 자동 실행 자리로 세지 않습니다. cron 허용이 어느 개인 정보 보호 권한 항목에 남는지는 확인하지 못했습니다.

수집 범위는 사용자 폴더와 시스템 폴더를 모두 챙깁니다. 실행 에이전트만 해도 사용자별 폴더와 모든 사용자용 폴더가 따로 있고 [1], 예약 작업과 emond 는 `/etc/`, `/var/`, `/private/var/db/` 아래에 있어서, 사용자 홈만 모은 수집본으로는 여러 자리를 놓칩니다. 라이브 대응이 가능하면 `sfltool dumpbtm` 출력을 먼저 저장해 둡니다. 이 명령은 로그인·백그라운드 항목의 현재 상태와 적재된 `servicemanagement` 페이로드 UUID 를 출력합니다 [2]. 같은 도구의 `sfltool resetbtm` 은 로그인·백그라운드 항목 데이터를 초기화해서 [2], 조사 중에는 실행하지 않습니다(필자 판단). 라이브 수집 절차는 [라이브 대응](../../03-techniques/process-acquisition/live-response/index.md) 에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 위치 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 실행 에이전트·데몬 폴더 다섯 곳(아래 표) | 로그인·부팅 때 실행되는 프로그램과 실행 조건 | [실행 에이전트·데몬](../../02-artifacts/persistence/launchd/index.md) |
| 2 | `sfltool dumpbtm` 출력, BTM 로그 | macOS 13 이후 로그인·백그라운드 항목의 현재 상태 | [로그인 항목](../../02-artifacts/persistence/login-items.md) |
| 3 | `~/Library/Application Support/com.apple.backgroundtaskmanagementagent/backgrounditems.btm` | 옛 방식 로그인 항목 | [로그인 항목](../../02-artifacts/persistence/login-items.md) |
| 4 | `/Library/Managed Preferences/` | 설치된 구성 프로파일이 내려준 설정 | [구성 프로파일](../../02-artifacts/persistence/configuration-profiles.md) |
| 5 | cron, `/etc/periodic/`, `/var/at/jobs/` | 정해진 때 실행되는 작업 | [예약 작업](../../02-artifacts/persistence/cron-periodic.md) |
| 6 | 셸 시작 파일 | 터미널을 열 때마다 실행되는 명령 | [셸 시작 파일](../../02-artifacts/persistence/shell-startup-files.md) |
| 7 | LoginHook·LogoutHook, `/private/var/db/emondClients` | 드물게 쓰이는 자동 실행 자리 | [그 밖의 지속성 위치](../../02-artifacts/persistence/other-persistence.md) |
| 8 | `~/Library/Mail/V6/MailData/SyncedRules.plist` | AppleScript 를 실행하는 메일 규칙 | [애플 메일](../../02-artifacts/mail/apple-mail/index.md) |
| 9 | 커널·시스템 확장 | 커널 수준 자동 실행 | [커널·시스템 확장](../../02-artifacts/persistence/kext-system-extension.md) |

### 실행 에이전트·데몬 폴더

| 폴더 | 범위 |
|---|---|
| `~/Library/LaunchAgents/` | 사용자별 |
| `/Library/LaunchAgents/` | 모든 사용자 |
| `/System/Library/LaunchAgents/` | SIP 보호 |
| `/Library/LaunchDaemons/` | 쓰려면 관리자 권한이 필요 |
| `/System/Library/LaunchDaemons/` | SIP 보호 |

지속성을 가를 때 plist 에서 먼저 볼 키는 `RunAtLoad`, `KeepAlive`, `ProgramArguments` 입니다 [1]. `ProgramArguments` 가 가리키는 실행 파일 경로가 수상한지 보는 일이 탐지의 중심이고, 라이브 환경이면 LaunchAgents 폴더에 쓰는 동작을 감시하는 방법도 쓸 수 있습니다 [1].

### 그 밖의 자리에서 볼 것

예약 작업 가운데 periodic 은 `/etc/periodic/` 아래 daily·weekly·monthly 폴더에 있고, 설정을 덮어쓰는 파일로 `/etc/defaults/periodic.conf` 와 `/etc/periodic.conf` 가 있습니다 [1]. at 작업은 `/var/at/jobs/` 안에 이름이 'a' 로 시작하는 파일로 남습니다 [1].

LoginHook·LogoutHook 은 `com.apple.loginwindow` 환경 설정에 있어서 라이브 환경에서는 root 로 `sudo defaults read com.apple.loginwindow` 를 실행해 확인합니다 [1]. emond 는 정상 용도로 거의 쓰이지 않아서, `/private/var/db/emondClients` 에 항목이 있으면 수상하게 봅니다 [1]. emond 가 없어진 버전은 확인하지 못했습니다.

폴더 동작 (Folder Actions) 은 파일로 찾기보다 실행 중인 `osascript` 프로세스 가운데 명령줄 인수에 `ScriptMonitor` 가 들어간 것을 찾습니다 [1]. 메일 규칙은 `SyncedRules.plist` 에서 AppleScript 를 실행하는 규칙을 찾고, 아이클라우드로 동기화된 사본도 있어서 함께 봅니다 [1]. 경로의 `V6` 는 메일 버전마다 바뀌는데, 버전별 대응은 확인하지 못했습니다.

### macOS 13 이후 BTM 로그

Apple 문서는 BTM 활동 로그를 볼 때 통합 로그의 서브시스템 `com.apple.backgroundtaskmanagement`, 범주 `mcx` 로 거르라고 안내합니다 [2]. 문서의 예는 실시간으로 보는 `log stream` 이라서, 수집본의 로그 아카이브에서는 같은 조건으로 아래처럼 추립니다.

```
log show --archive system_logs.logarchive \
  --predicate 'subsystem == "com.apple.backgroundtaskmanagement" AND category == "mcx"'
```

기기 관리를 받는 맥이면 조직의 MDM `com.apple.servicemanagement` 규칙을 받아 둡니다. 규칙은 BundleIdentifier, BundleIdentifierPrefix, TeamIdentifier, Label(launchd plist 의 Label), LabelPrefix 로 항목을 가리켜서 [2], 조직이 허용한 항목과 새로 생긴 항목을 가를 때 기준이 됩니다.

## 분석 흐름

1. OS 버전을 확인해 BTM 이 있는 맥인지 정합니다. 라이브면 `sfltool dumpbtm` 출력을 먼저 저장합니다.
2. 실행 에이전트·데몬 폴더 다섯 곳의 plist 를 모두 목록으로 만들고, 사용자·관리자 쪽 세 폴더부터 `ProgramArguments`, `RunAtLoad`, `KeepAlive` 를 읽습니다. plist 를 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 에 있습니다.
3. 로그인 항목을 확인합니다. macOS 13 이후는 BTM 출력과 로그를, 그 전 버전은 `backgrounditems.btm` 을 봅니다.
4. 구성 프로파일, 예약 작업, 셸 시작 파일, LoginHook, emond, 메일 규칙을 차례로 확인합니다. 라이브면 `osascript` 프로세스의 명령줄에서 폴더 동작도 찾습니다.
5. 찾은 항목이 가리키는 실행 파일을 확보해 서명과 번들 정보를 봅니다. 절차는 [악성 코드 흔적 분석](../../03-techniques/analysis/malware-triage/index.md) 과 [앱 번들 정보](../../02-artifacts/embedded-metadata/app-bundle.md) 에 있습니다.
6. plist 와 실행 파일이 생긴 시각을 [파일 시스템 이벤트](../../02-artifacts/filesystem/fsevents/index.md) 에서 찾아, [악성 코드는 어디서 들어왔나](initial-access.md) 에서 정리한 유입 시각과 나란히 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다.
7. 등록된 항목이 실제로 실행되었는지는 [통합 로그의 프로세스 실행 기록](../../02-artifacts/execution/unified-log-process.md) 으로 따로 확인합니다.

## 흔한 오판

- **LaunchAgents 폴더에 수상한 plist 가 없으니 지속성이 없다고 보는 경우.** 자동 실행 자리는 이 밖에도 여럿 있고 [1], macOS 13 이후는 BTM 이 항목을 관리합니다 [2]. 지속성을 만들지 않고 한 번 훔치고 끝내는 악성 코드도 있어서, 그런 경우는 [정보 탈취 악성 코드](infostealer.md) 흐름으로 봅니다.
- **커널 확장부터 뒤지는 경우.** 커널 확장은 악성 코드가 즐겨 쓰는 방법이 아닙니다 [1]. 사용자·관리자 쪽 실행 에이전트·데몬 폴더를 먼저 봅니다.
- **`/System/Library/` 쪽 항목까지 똑같이 의심하는 경우.** 이 두 폴더는 SIP 보호 대상이라 [1], 일반 조사에서는 사용자·관리자 쪽 폴더부터 봅니다. SIP 가 꺼진 맥이면 이 전제가 흔들린다는 점은 필자 해석이고, SIP 는 [서명·공증·무결성 보호](../../01-foundations/protection/codesign-notarization-sip.md) 에서 다룹니다.
- **구성 프로파일을 모두 조직이 설치한 것으로 보는 경우.** 사용자를 속여 직접 설치하게 한 사례가 있습니다 [1]. 조직의 기기 관리 목록과 대조합니다.
- **메일 규칙이 이 맥에서 만들어졌다고 보는 경우.** 규칙은 아이클라우드로 동기화된 사본도 있어서 [1], 필자 해석으로는 같은 계정의 다른 기기에서 만든 규칙일 수 있습니다.
- **plist 가 있으니 실행되었다고 쓰는 경우.** 등록은 실행 조건을 적어 둔 것이고, 실행 여부는 로그와 프로세스 기록으로 따로 확인합니다.

## 보고서 문장 예

> `/Library/LaunchDaemons/` 에 `○○.plist` 가 있고, 이 파일의 `ProgramArguments` 는 `○○` 경로의 실행 파일을 가리키며 `RunAtLoad` 값은 참입니다. 파일 시스템 이벤트에서 이 plist 가 생긴 기록은 ○○○○-○○-○○ ○○:○○:○○(UTC)입니다. 이 기록은 해당 실행 파일이 부팅 때 실행되도록 등록되어 있었다는 사실을 보여 주지만, 실제로 실행되었는지는 통합 로그의 프로세스 실행 기록으로 따로 확인해 적습니다.

## 함께 볼 페이지

- [실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)](../../02-artifacts/persistence/launchd/index.md) — plist 구조와 키 전체
- [로그인 항목 (Login Items)](../../02-artifacts/persistence/login-items.md) — BTM 과 옛 방식 로그인 항목
- [그 밖의 지속성 위치 (Login Hook·Authorization Plugin·Emond)](../../02-artifacts/persistence/other-persistence.md) — 드문 자동 실행 자리
- [악성 코드는 어디서 들어왔나 (Initial Access)](initial-access.md) — 지속성보다 앞선 유입
- [원격 접속 침입 확인 (Remote Intrusion)](remote-intrusion.md) — SSH 로그인 때 실행되는 스크립트

## 참고 문헌

1. Phil Stokes, "How Malware Persists on macOS" (SentinelOne) — https://www.sentinelone.com/blog/how-malware-persists-on-macos/
2. Apple Platform Deployment, "Manage login items and background tasks on Mac" — https://support.apple.com/guide/deployment/manage-login-items-background-tasks-mac-depdca572563/web
