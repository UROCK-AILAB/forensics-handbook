---
title: "로그인 항목"
parent: "아티팩트 · 자동 실행·지속성"
nav_order: 600
---

# 로그인 항목 (Login Items)

로그인 항목 (Login Items)은 사용자가 로그인할 때 자동으로 열리는 앱과 항목이고, 목록은 사용자 홈의 plist·`backgrounditems.btm`·시스템 BTM 저장소에 남아서 사용자 몫의 자동 실행을 찾을 때 실행 에이전트·데몬과 함께 봅니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 로그인 때 열고 싶은 앱을 등록하거나 앱이 스스로 로그인 항목으로 자리를 잡으면, macOS는 그 목록을 파일에 적어 두고, 목록에 든 항목은 사용자가 로그인할 때마다 다시 열리며 악성 코드가 자리를 잡는 방법으로도 쓰입니다. 로그인 항목을 저장하는 파일로는 `backgrounditems.btm` 이 있습니다 [1].

공개 아티팩트 정의 모음인 ForensicArtifacts에서는 로그인 항목 파일과 로그인 창 설정 파일 여러 개가 `MacOSUserLoginItemsPlistFile` 한 항목으로 묶여 있습니다 [2]. 이 묶음에 든 로그인 창 plist에는 로그인 훅 (LoginHook)·로그아웃 훅 (LogoutHook)도 저장되고 `sudo defaults read com.apple.loginwindow` 로 확인합니다 [1]. 훅은 로그인 항목과 동작이 달라서 [그 밖의 지속성 위치 (Login Hook·Authorization Plugin·Emond)](other-persistence.md)에서 따로 다루고, 로그인 창의 다른 설정은 [로그인 창 설정 (loginwindow)](../system-account/loginwindow.md)에 있습니다.

macOS 13 이후에는 백그라운드 작업 관리 (Background Task Management, BTM)가 로그인 항목을 실행 에이전트·데몬과 함께 관리하고, 등록 기록의 구조와 `sfltool dumpbtm`, 시스템 설정의 로그인 항목 화면, MDM 규칙은 [실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)](launchd/index.md) 아래의 백그라운드 작업 관리 페이지에서 다룹니다. 이 페이지는 그 밖의 파일 위치와 해석을 다룹니다.

## 위치와 버전별 차이

| 경로 | 설명 | 출처 |
|---|---|---|
| `~/Library/Preferences/com.apple.loginitems.plist` | 사용자 로그인 항목 plist (예전 방식) | [2] |
| `~/Library/Application Support/com.apple.backgroundtaskmanagementagent/backgrounditems.btm` | 사용자 로그인 항목 | [1][2] |
| `/private/var/db/com.apple.backgroundtaskmanagement/BackgroundItems-v*.btm` | 시스템 BTM 저장소 (`/var/db/...` 형태로도 적힘) | [2] |
| `/Library/Preferences/com.apple.loginwindow.plist` | 로그인 창 plist | [2] |
| `~/Library/Preferences/loginwindow.plist` | 로그인 창 plist | [2] |
| `~/Library/Preferences/ByHost/com.apple.loginwindow.plist` | 로그인 창 plist (기기별) | [2] |
| `~/Library/Preferences/ByHost/com.apple.loginwindow.*.plist` | 로그인 창 plist (기기별) | [2] |
| `/var/root/Library/Preferences/com.apple.loginwindow.plist` | root 계정의 로그인 창 plist (`/private/var/root/...` 형태로도 적힘) | [2] |

`~` 로 시작하는 경로는 사용자마다 하나씩 있어서, 이미지에서는 모든 사용자 홈을 돌며 같은 경로를 찾습니다. 사용자 목록은 [사용자 계정 (Local Accounts)](../system-account/user-accounts/index.md)에서 먼저 뽑아 둡니다.

경로마다 쓰이는 macOS 버전과, 예전 plist에서 `backgrounditems.btm` 으로, 다시 시스템 BTM 저장소로 넘어간 시점은 실제 데이터로 확인해야 합니다.

| macOS | 내용 |
|---|---|
| 버전 구분 없음 | 위 표의 경로 전부가 로그인 항목 관련 파일로 적힘 [2] |
| 13 이후 | BTM이 로그인 항목을 관리함 (자세한 내용은 [실행 에이전트·데몬](launchd/index.md) 아래 백그라운드 작업 관리 페이지) |

어느 파일이 조사 대상 버전에서 실제로 쓰이는지는 버전마다 다를 수 있어서, 수집할 때는 위 경로를 구분하지 않고 모두 가져오고 파일마다 있고 없음과 시각을 적어 둡니다.

## 구조

위 파일은 모두 plist 파일입니다 [2]. plist를 읽는 일반 원리(XML과 바이너리 형식, 바이너리 plist의 오브젝트 테이블, NSKeyedArchiver로 묶은 데이터)는 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에 있습니다.

각 파일 안에서 어떤 키에 항목이 들어가는지(`com.apple.loginitems.plist` 안의 키 이름, `com.apple.loginwindow` plist에서 로그인 때 다시 여는 앱 목록이 들어가는 키)는 공개된 분석 자료가 없어서, 키 이름을 짐작해 찾지 말고 파일 전체를 풀어 경로·번들 ID·앱 이름이 보이는 값을 모두 적습니다. 값 안에 파일 참조 데이터가 들어 있으면 [파일 참조 데이터 (Alias·Bookmark)](../../01-foundations/value-decoding/alias-bookmark.md)의 방법으로 풀고, 번들 ID와 팀 ID는 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)를 참고합니다.

## 증거로서 의미

**증명하는 것.** 목록에 항목이 있으면 수집한 시점에 그 사용자 계정의 로그인 항목으로 그 앱이나 파일이 등록돼 있었다는 뜻이고, 어느 사용자 홈의 파일인지로 어느 계정에 걸린 자동 실행인지를 말할 수 있습니다. 항목이 가리키는 파일이 지워졌더라도 목록에 경로가 남아 있으면 그 경로에 무언가가 있었다는 단서가 됩니다.

**증명하지 못하는 것.** 등록돼 있다는 사실은 실제로 실행됐다는 뜻이 아니고, 누가 등록했는지(사용자가 직접 넣었는지, 앱이 스스로 넣었는지)도 이 파일로는 판별할 수 없습니다. 언제 등록됐는지도 이 파일의 내용만으로는 알 수 없습니다(아래 시각 해석).

보고서에는 "이 계정의 로그인 항목 목록에 이 앱 경로가 들어 있었다" 처럼 기록으로 확인되는 만큼만 쓰고, 실행 여부는 실행 흔적과 맞춘 뒤에 따로 씁니다.

## 시각 해석

로그인 항목 파일 안에 등록 시각이 들어 있는지, 들어 있다면 어떤 기준의 시각인지는 실제 데이터로 확인하고, 등록 시기는 파일 밖의 기록으로 좁힙니다. 목록 파일 자체의 파일 시스템 시각은 목록이 마지막으로 바뀐 때를 알려 줄 뿐 어느 항목이 그때 들어갔는지까지는 알려 주지 않고, 항목이 가리키는 앱의 설치 시각과 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)의 변경 기록을 함께 놓으면 범위가 좁아집니다. 여러 시각 값의 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에서 확인합니다.

## 함정과 한계

로그인 항목은 한 파일에만 있지 않습니다. 사용자 홈의 예전 plist와 `backgrounditems.btm`, 시스템 BTM 저장소, 여러 개의 로그인 창 plist가 한꺼번에 남아 있을 수 있고, 어느 파일이 현재 쓰이는지 모르고 한 곳만 보면 항목을 놓치거나 쓰이지 않는 옛 목록을 현재 설정으로 잘못 읽을 수 있습니다.

로그인 창 plist에는 로그인 항목 말고도 로그인 훅 같은 다른 설정이 함께 들어 있어서 [1], 이 plist에서 찾은 스크립트 경로를 로그인 항목으로 적으면 실행 방식과 실행 계정을 잘못 설명하게 됩니다. 훅인지 로그인 항목인지는 키 이름으로 먼저 구분합니다.

지우기 쪽에서 보면, 목록은 수집한 시점의 상태만 보여 주기 때문에 목록에 없다는 사실이 과거에도 없었다는 뜻은 아닙니다. 지난 상태는 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md)로 확인합니다. 로그인 항목을 넣고 빼는 동작이 통합 로그에 어떤 서브시스템·문구로 남는지는 실제 통합 로그에서 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

목록 파일을 헥스 편집기로 열어 앞머리로 XML plist인지 바이너리 plist인지 구분한 뒤, [속성 목록 파일](../../01-foundations/data-formats/plist/index.md)의 순서대로 오브젝트를 따라갑니다. 키 이름을 모를 때는 먼저 `.app` 이나 `/Applications/` 처럼 앱 경로에 흔히 들어가는 문자열을 검색해 값의 위치를 잡고 그 값이 어느 키·어느 배열에 딸려 있는지 거슬러 올라가면 파일마다 목록이 들어 있는 자리를 찾을 수 있습니다. 이 방법은 plist 형식을 바탕으로 한 설명이고 특정 기기에서 나온 값이 아닙니다.

### 공개 도구로 한 번

ForensicArtifacts 정의 파일 [2]은 공개 아티팩트 정의 모음이라서, 수집 목록을 짤 때 `MacOSUserLoginItemsPlistFile` 항목의 경로를 그대로 옮겨 빠짐없이 챙길 수 있습니다. 실행 중인 시스템에서는 로그인 창 설정을 아래처럼 읽을 수 있고 [1], 같은 plist를 이미지에서 꺼내 푼 결과와 맞춰 봅니다.

```
sudo defaults read com.apple.loginwindow
```

macOS 13 이후 시스템의 BTM 기록은 `sfltool dumpbtm` 으로 보고, 명령의 주의점은 [실행 에이전트·데몬](launchd/index.md) 아래 백그라운드 작업 관리 페이지에 있습니다. 실행 중인 시스템에서 명령을 칠 때의 원칙은 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)을 따릅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 |
|---|---|
| [실행 에이전트·데몬](launchd/index.md) | macOS 13 이후 BTM 등록 기록과, 같은 시기에 심어진 다른 자동 실행 |
| [그 밖의 지속성 위치](other-persistence.md) | 같은 로그인 창 plist에 들어가는 로그인 훅 |
| [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | 항목이 가리키는 앱이 언제 설치됐는지 |
| [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../01-foundations/protection/codesign-notarization-sip.md) | 항목이 가리키는 앱의 서명과 팀 ID |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | 목록 파일과 앱이 바뀐 순서 |
| [통합 로그의 프로세스 실행 기록 (Process Events)](../execution/unified-log-process.md) | 로그인 무렵에 그 앱이 실제로 실행됐는지 |

지속성 위치를 한꺼번에 살펴보는 순서는 [악성 코드 지속성 찾기 (Persistence)](../../04-scenarios/incident/persistence.md)에 있습니다.

## 실습

NIST CFReDS 같은 공개 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 이미지의 macOS 버전을 먼저 확인하고([OS 버전과 설치 기록](../system-account/os-version-install-history.md)), 위치 표의 경로 가운데 어느 파일이 있는지 사용자마다 적습니다.
2. 있는 파일마다 풀어서 앱 경로·번들 ID·앱 이름이 들어 있는 값을 모두 적고, 두 파일 이상에 같은 항목이 있는지 봅니다.
3. 로그인 창 plist에서 찾은 값 가운데 로그인 항목이 아닌 설정(로그인 훅 등)을 따로 가려냅니다.
4. 항목이 가리키는 앱이 이미지에 아직 있는지, 있다면 설치 시각과 목록 파일의 수정 시각이 어떻게 놓이는지 봅니다.

## 참고 문헌

1. Phil Stokes, "How Malware Persists on macOS" (SentinelOne, 2022-10-27 갱신) — https://www.sentinelone.com/blog/how-malware-persists-on-macos/
2. ForensicArtifacts, artifacts/data/macos.yaml (main 브랜치) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
