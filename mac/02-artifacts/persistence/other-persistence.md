---
title: "그 밖의 지속성 위치"
parent: "아티팩트 · 자동 실행·지속성"
nav_order: 650
---

# 그 밖의 지속성 위치 (Login Hook·Authorization Plugin·Emond)

로그인 훅 (Login Hook)·권한 부여 플러그인 (Authorization Plugin)·이벤트 감시 데몬 (Emond)은 흔히 쓰이지 않는 자동 실행 위치이고, 셋 다 root 권한으로 코드를 돌릴 수 있어서 실행 에이전트·데몬만 보고 끝내면 놓치기 쉬운 지속성 흔적입니다.

## 무엇을 기록하나 · 왜 생기나

세 가지 모두 원래는 관리자가 쓰라고 만든 기능입니다. 로그인 훅과 로그아웃 훅 (Logout Hook)은 사용자가 로그인하거나 로그아웃할 때 스크립트 하나를 root 권한으로 실행하게 하는 설정이고, 설정 도메인 `com.apple.loginwindow` 의 `LoginHook`·`LogoutHook` 키에 스크립트 경로를 적는 방식입니다. [1][2] 이 기능은 폐기됐고, 같은 일은 launchd 에이전트·데몬으로 하면 됩니다. [1]

권한 부여 플러그인은 권한 부여 서비스 (Authorization Services)를 넓혀서 새로운 인증 방식이나 정책 DB만으로는 나타내기 어려운 정책을 구현하는 번들입니다. [3] 로그인 과정도 권한 부여 규칙 하나로 돌아가서, 이 규칙에 플러그인의 메커니즘을 끼워 넣으면 로그인할 때마다 그 코드가 실행됩니다. [4]

이벤트 감시 데몬은 여러 서비스에서 이벤트를 받아 간단한 규칙 엔진에 넣고, 규칙에 맞으면 동작을 실행하는 launch daemon입니다. 규칙은 plist 형식이고, 시스템 시작·사용자 인증 같은 이벤트 종류와 시스템 명령 실행·메일 전송 같은 동작을 정의합니다. [5] emond도 root 권한으로 실행됩니다. [5]

MITRE ATT&CK는 로그인 훅을 T1037.002 (Boot or Logon Initialization Scripts: Login Hook)로, emond를 T1546.014 (Event Triggered Execution: Emond)로 분류하고, 로그인 훅은 지속성 (TA0003)과 권한 상승 (TA0004) 두 전술에 걸쳐 있습니다. [2][5]

셋 모두 디스크에는 "무엇을 언제 실행하라" 는 설정 파일과 실제로 실행될 스크립트·번들이 남고, 실행 자체의 기록은 이 설정 파일에 남지 않습니다. 이 페이지는 설정이 남는 자리와 그 읽는 법을 다루고, launchd 기반의 흔한 자동 실행은 [실행 에이전트·데몬](launchd/index.md), 로그인 창의 다른 설정은 [로그인 창 설정](../system-account/loginwindow.md)에서 다룹니다.

## 위치와 버전별 차이

### 경로

| 항목 | 경로 | 출처 |
|---|---|---|
| 로그인·로그아웃 훅 설정 (Apple 문서) | `/var/root/Library/Preferences/com.apple.loginwindow.plist` | [1] |
| 로그인·로그아웃 훅 설정 (MITRE) | `/Library/Preferences/com.apple.loginwindow.plist` | [2] |
| 권한 부여 플러그인 번들 (10.5 이후) | `/Library/Security/SecurityAgentPlugins` | [4] |
| 권한 부여 플러그인 번들 (10.5 이전) | `/System/Library/CoreServices/SecurityAgentPlugins` | [4] |
| 권한 정책 DB (TN2228, 2008년 기준) | `/etc/authorization` | [4] |
| emond 실행 파일 | `/sbin/emond` | [5] |
| emond 규칙 디렉터리 | `/etc/emond.d/rules/` | [5] |
| emond 큐 디렉터리 | `/private/var/db/emondClients` | [5] |
| emond launchd 설정 | `/System/Library/LaunchDaemons/com.apple.emond.plist` | [5] |

로그인 훅 plist 경로는 Apple 문서와 MITRE가 서로 다르게 적었고 [1][2], 현재 macOS에서 어느 쪽이 실제 저장 위치인지는 기기에서 직접 확인합니다. 조사할 때는 두 파일 모두에서 `LoginHook`·`LogoutHook` 키를 찾아봅니다.

### 버전별 차이

| 항목 | 버전 정보 | 출처 |
|---|---|---|
| 로그인·로그아웃 훅 | 폐기됨. MITRE는 macOS 10.11에서 폐기됐다고 적었고, Apple은 버전을 밝히지 않음 | [1][2] |
| 권한 부여 플러그인 설치 경로 | Mac OS X 10.5 이후 `/Library/Security/SecurityAgentPlugins` | [4] |
| 권한 정책 DB | 2008년 기준 `/etc/authorization` 이고 바뀔 수 있음. 현재 위치는 실제 기기에서 확인 | [4] |
| emond | 버전별로 들어 있는지 실제 기기에서 확인 | — |

로그인 훅을 설명한 문서 [1][4]는 갱신이 멈춘 보관 문서라서, 폐기 뒤 macOS 10.15 이후에서 훅이 실제로 실행되는지는 기기에서 직접 확인해야 합니다. emond도 버전에 따라 빠져 있을 수 있어서, 먼저 `/sbin/emond` 와 launchd 설정 plist가 있는지부터 확인합니다.

## 구조

### 로그인 훅

`com.apple.loginwindow` plist 안에서 `LoginHook` 과 `LogoutHook` 은 각각 실행할 스크립트의 경로 문자열 하나를 값으로 두고, 그래서 로그인 훅과 로그아웃 훅은 한 번에 하나씩만 설치할 수 있습니다. [1][2] 스크립트 파일에는 실행 권한이 있어야 하고, 실행될 때 첫 인자(`$1`)로 로그인하는 사용자의 짧은 이름 (short name)이 넘어옵니다. [1] 로그인 훅은 로그인 중 홈 디렉터리가 마운트된 뒤 한 시점에 돌고 [4], 훅이 끝날 때까지 나머지 로그인 동작이 기다립니다. [1]

새로 설치한 시스템에서는 사용자가 빠른 사용자 전환 같은 로그인 창 설정을 바꾸기 전까지 `/var/root/Library/Preferences/com.apple.loginwindow.plist` 가 없고, plist가 없으면 이 방법이 동작하지 않습니다. [1] plist 자체의 형식은 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md)을 참고합니다.

### 권한 부여 플러그인

로그인에 쓰는 권한 (right) 이름은 `system.login.console` 이고 클래스는 `evaluate-mechanisms` 이며, `loginwindow` 프로세스가 이 권한을 요청해서 로그인 메커니즘들을 돌립니다. [4] 권한 정의 안의 `mechanisms` 배열에 메커니즘이 순서대로 적혀 있고, 그 순서대로 실행됩니다. [4]

메커니즘 문자열은 아래 형식이고, 뒤에 `,privileged` 가 붙는지에 따라 실행 주체가 달라집니다. [4]

```
플러그인이름:메커니즘이름[,privileged]
```

| 구분 | 실행 프로세스 | 실행 계정 | UI |
|---|---|---|---|
| `,privileged` 붙음 | `authorizationhost` | EUID/RUID 0 (root) | 띄울 수 없음 |
| 붙지 않음 | `SecurityAgent` | UID 92 (`_securityagent`) | 띄울 수 있음 |

Mac OS X 10.5 기본값은 아래 순서입니다. [4]

```
builtin:smartcard-sniffer,privileged
loginwindow:login
builtin:reset-password,privileged
builtin:auto-login,privileged
builtin:authenticate,privileged
HomeDirMechanism:login,privileged
HomeDirMechanism:status
MCXMechanism:login
loginwindow:success
loginwindow:done
```

플러그인 번들 파일은 소유자가 `root`, 그룹이 `wheel` 이어야 하고 root 말고는 쓰기 권한이 없어야 합니다. [4] 그래서 번들의 소유자나 권한이 이 조건과 다르면 설치 과정부터 의심해 볼 만합니다.

### emond

emond는 launchd 설정 `/System/Library/LaunchDaemons/com.apple.emond.plist` 에 따라 뜨고, 이 설정의 `QueueDirectories` 경로인 `/private/var/db/emondClients` 에 파일이 있어야 서비스가 시작됩니다. [5] 규칙은 `/etc/emond.d/rules/` 아래의 plist 파일이고, 파일 하나에 이벤트 종류와 실행할 동작이 함께 적힙니다. [5] `QueueDirectories` 가 무엇인지는 [실행 에이전트·데몬](launchd/index.md)을 참고합니다.

## 증거로서 의미

**증명하는 것**

- `LoginHook`·`LogoutHook` 키에 경로가 있으면, 그 설정이 남아 있던 시점에 해당 스크립트를 로그인·로그아웃 때 root 권한으로 실행하도록 지정돼 있었다는 사실을 보여 줍니다.
- `mechanisms` 배열에 기본값에 없는 플러그인 이름이 있고 같은 이름의 번들이 `/Library/Security/SecurityAgentPlugins` 에 있으면, 로그인할 때 그 코드가 불리도록 구성돼 있었다고 볼 수 있습니다.
- `/etc/emond.d/rules/` 에 규칙 파일이 있고 큐 디렉터리에 파일이 있으면, emond가 그 규칙에 따라 명령을 실행할 수 있는 상태였다는 사실을 보여 줍니다.

**증명하지 못하는 것**

- 설정이 있다고 해서 실제로 실행됐다는 뜻은 아닙니다. 폐기된 로그인 훅은 현재 macOS에서 실행되는지부터 실제 기기로 확인해야 하고, 실행 여부는 로그나 프로세스 기록 같은 다른 흔적으로 따로 확인해야 합니다.
- 누가 설정을 넣었는지는 이 파일들만으로 알 수 없습니다. 로그인 훅을 만들거나 고치려면 관리자 권한이 필요하다는 점 [2]은 그 권한을 얻은 누군가가 넣었다는 범위까지만 좁혀 줍니다.
- 스크립트나 번들이 악성인지도 경로만으로는 판단할 수 없고, 내용과 서명을 따로 봐야 합니다. 서명 확인은 [서명·공증·무결성 보호](../../01-foundations/protection/codesign-notarization-sip.md)를 참고합니다.

보고서에는 "로그인 훅으로 악성 코드를 실행했다" 가 아니라 "`com.apple.loginwindow` plist의 `LoginHook` 값에 이 경로가 적혀 있고, 그 파일의 내용은 이렇다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`LoginHook` 값은 경로 문자열이라 그 안에 시각이 들어 있지 않습니다. 그래서 언제 설정됐는지는 plist 파일, 훅 스크립트, 플러그인 번들, emond 규칙 파일의 파일 시스템 시각으로 추정하고, 파일을 고칠 때 바뀌는 시각이라 마지막으로 고친 때만 알려 준다는 점을 감안합니다. 파일 시스템 시각을 읽는 법은 [APFS 구조](../../01-foundations/disk-volume/apfs/index.md)와 [맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md)에 있고, 파일이 만들어지고 바뀐 순서는 [파일 시스템 이벤트](../filesystem/fsevents/index.md)로 따로 맞춰 봅니다.

훅이나 규칙이 실행될 때 [통합 로그](../../01-foundations/data-formats/unified-log/index.md)에 어떤 서브시스템·메시지로 남는지는 실제 통합 로그에서 확인합니다.

## 함정과 한계

로그인 훅의 plist 경로는 출처마다 달라서 한쪽만 보면 놓칠 수 있고, 두 곳을 다 봐야 합니다. 폐기된 기능이라 "현재 macOS에서는 안 돈다" 고 단정하기 쉽지만, 설정이 남아 있으면 조사 대상에 넣습니다.

권한 정책 DB의 위치는 2008년 기준 `/etc/authorization` 이고 바뀔 수 있어서 [4], 현재 macOS의 위치는 실제 기기에서 확인합니다. 오래된 경로에 파일이 없다고 해서 규칙이 바뀌지 않았다고 결론 내리지 않습니다. 기본값 목록도 10.5 기준이라, 현재 버전의 기본 메커니즘과 1:1로 맞춰 보면 정상 항목을 이상 항목으로 잘못 볼 수 있고, 같은 버전의 깨끗한 설치본과 비교하는 편이 낫습니다.

emond는 버전에 따라 아예 없을 수 있어서, 규칙 디렉터리가 없다는 사실만으로 "지워졌다" 고 보지 않습니다. 반대로 `/sbin/emond` 가 없는 버전에서 규칙 파일만 남아 있다면 실행될 수 없는 흔적일 수 있습니다.

지우기 쪽에서 보면, `LoginHook` 키는 `defaults` 명령으로 지울 수 있어서 [1][2] 키가 없다는 사실이 과거에도 없었다는 뜻은 아닙니다. 지난 상태는 [스냅숏과 백업 비교](../../03-techniques/analysis/snapshot-diff.md)로 확인하고, 명령을 친 흔적은 [터미널 명령 기록](../execution/shell-history.md)에서 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

`com.apple.loginwindow.plist` 가 바이너리 plist라도 키 문자열 `LoginHook` 은 ASCII 바이트 그대로 들어가기 때문에, 헥스 편집기에서 문자열 검색으로 키 위치를 찾을 수 있습니다. 이 설명은 plist 형식 명세를 바탕으로 한 것이고 특정 기기에서 나온 값이 아닙니다. 키와 값이 어떻게 이어지는지(오브젝트 테이블·오프셋 테이블)는 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md)의 순서대로 따라가면 값인 스크립트 경로 문자열까지 닿습니다. emond 규칙 plist도 같은 방법으로 읽습니다.

### 공개 도구로 한 번

실행 중인 시스템에서는 macOS 기본 명령 `defaults read` 로 값을 읽고, 이미지에서 꺼낸 plist는 파일을 직접 열어 봅니다. [1][2]

```
sudo defaults read com.apple.loginwindow LoginHook
sudo defaults read com.apple.loginwindow LogoutHook
```

권한 부여 플러그인은 `/Library/Security/SecurityAgentPlugins` 의 번들 목록과 각 번들의 소유자·그룹·권한을 보고, emond는 아래 순서로 봅니다.

1. `/sbin/emond` 와 `/System/Library/LaunchDaemons/com.apple.emond.plist` 가 있는지 확인합니다.
2. `/private/var/db/emondClients` 에 파일이 있는지 봅니다. 파일이 없으면 서비스가 시작되지 않습니다. [5]
3. `/etc/emond.d/rules/` 의 규칙 plist를 열어 이벤트 종류와 실행 동작을 읽습니다.
4. 각 파일의 소유자와 시각을 적습니다. root가 아닌 사용자가 만든 규칙은 따로 표시합니다. [5]

실행 중인 시스템에서 값을 읽을 때의 주의점은 [라이브 대응](../../03-techniques/process-acquisition/live-response/index.md)을 참고합니다.

## 교차 검증

로그인 훅은 `defaults` 명령이나 plist 수정으로 훅을 설정한 흔적과, 로그인 때 예상하지 못한 부모-자식 프로세스 관계로 스크립트·바이너리가 실행되는 것을 봅니다. emond는 규칙·큐 디렉터리의 허가 없는 생성·수정을 `/sbin/emond` 프로세스 실행과 맞춰 보고, 부팅·로그인 때 예상 밖의 셸 명령 실행을 표시합니다. [2][5] 함께 볼 아티팩트는 아래와 같습니다.

| 아티팩트 | 알려 주는 것 |
|---|---|
| [파일 시스템 이벤트](../filesystem/fsevents/index.md) | 설정·스크립트·규칙 파일이 만들어지고 바뀐 순서 |
| [통합 로그의 프로세스 실행 기록](../execution/unified-log-process.md) | 로그인·부팅 무렵의 프로세스 실행과 부모-자식 관계 |
| [감사 로그](../logs/openbsm-audit.md) | 켜져 있었다면 파일 쓰기와 프로세스 실행 기록 |
| [터미널 명령 기록](../execution/shell-history.md) | `defaults write` 같은 설정 명령을 친 흔적 |
| [실행 에이전트·데몬](launchd/index.md) | 같은 시기에 함께 심어진 다른 자동 실행 |
| [예약 작업](cron-periodic.md) | cron·periodic 쪽 자동 실행 |
| [사용자 계정](../system-account/user-accounts/index.md) | 훅에 넘어간 짧은 이름이 어느 계정인지 |

지속성 위치를 한꺼번에 살펴보는 순서는 [악성 코드 지속성 찾기](../../04-scenarios/incident/persistence.md)에 있고, 찾은 흔적을 시간 순으로 엮는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)을 참고합니다.

## 실습

NIST CFReDS 같은 공개 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 두 경로의 `com.apple.loginwindow.plist` 가 각각 있는지, 있다면 `LoginHook`·`LogoutHook` 키가 있는지 확인합니다.
2. `/Library/Security/SecurityAgentPlugins` 에 번들이 있는지, 있다면 소유자·그룹·권한이 root·wheel 조건에 맞는지 봅니다.
3. 이미지의 macOS 버전에 `/sbin/emond` 가 들어 있는지, 규칙 디렉터리와 큐 디렉터리에 파일이 있는지 봅니다.
4. 찾은 파일마다 파일 시스템 시각을 적고, 같은 시각대에 다른 지속성 위치가 바뀐 흔적이 있는지 맞춰 봅니다.

## 참고 문헌

1. Apple, Daemons and Services Programming Guide — Customizing Login and Logout (2016-09-13 갱신, 보관 문서) — https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CustomLogin.html
2. MITRE ATT&CK, T1037.002 Boot or Logon Initialization Scripts: Login Hook — https://attack.mitre.org/techniques/T1037/002/
3. Apple Developer, Authorization Plug-ins — https://developer.apple.com/tutorials/data/documentation/security/authorization-plug-ins.json
4. Apple, Technical Note TN2228: Running At Login (2008-09-16, 갱신 중단) — https://developer.apple.com/library/archive/technotes/tn2228/_index.html
5. MITRE ATT&CK, T1546.014 Event Triggered Execution: Emond — https://attack.mitre.org/techniques/T1546/014/
