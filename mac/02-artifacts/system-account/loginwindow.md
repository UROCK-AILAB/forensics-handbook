---
title: "로그인 창 설정"
parent: "아티팩트 · 시스템·계정"
nav_order: 530
---

# 로그인 창 설정 (loginwindow)

`/Library/Preferences/com.apple.loginwindow.plist` 에서 마지막으로 로그인한 사용자와 자동 로그인 계정, 손님 계정 사용 여부를 읽고, 관리 서버가 내려보낸 로그인 창 설정과 함께 보면 이 맥에 누가 어떤 방식으로 들어올 수 있었는지 추정할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

로그인 창의 동작과 마지막 로그인 결과는 설정 파일 `com.apple.loginwindow.plist` 에 남습니다. 이 파일에는 마지막으로 로그인한 사용자가 담기고 [3], 시스템 쪽 파일에는 자동 로그인 계정, 손님 계정 사용 여부, 마지막 로그인 사용자 이름 같은 키가 있습니다. [1] 시스템 파일과 같은 이름의 파일이 사용자 홈 폴더 아래에도 있습니다. [2]

기관이 맥을 관리할 때는 관리 서버 (MDM) 가 `com.apple.loginwindow` 유형의 설정 페이로드를 내려보내 로그인 창에 무엇을 보여 줄지, 누구의 로그인을 허용할지, 자동 로그인을 어떻게 할지 정합니다. [4] 조사에서 이 두 기록은 [그 시각에 맥을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 를 따질 때 쓰는데, 자동 로그인이 켜져 있거나 손님 계정이 열려 있으면 로그인 기록만으로 사람을 가려내기 어려워지기 때문입니다.

계정 자체의 정보는 [사용자 계정](user-accounts/index.md) 페이지가 본문으로 다루고, 자동 로그인 암호를 가려 저장하는 `/private/etc/kcpassword` 도 그 페이지에 정리되어 있습니다.

## 위치와 버전별 차이

| 기록 | 위치 | 알려 주는 것 |
|---|---|---|
| 시스템 로그인 창 설정 | `/Library/Preferences/com.apple.loginwindow.plist` | 마지막 로그인 사용자, 자동 로그인 계정, 손님 계정 사용 여부 [1][2][3] |
| 사용자별 로그인 창 설정 | `<홈 폴더>/Library/Preferences/com.apple.loginwindow.plist` | 사용자 쪽 파일. 담기는 키는 공개 자료 없음 [2] |
| 관리 설정 페이로드 | 구성 프로파일 안의 `com.apple.loginwindow` 유형 | 관리 서버가 정한 로그인 창 동작 [4] |

관리 서버가 내려보낸 값이 디스크의 어느 파일에 풀려 남는지는 실제 데이터로 확인해야 합니다. 프로파일 자체를 찾는 법은 [구성 프로파일](../persistence/configuration-profiles.md) 페이지에 있습니다. 페이로드 키는 macOS 버전마다 도입 시기가 달라서 아래 구조 절의 표에 버전을 함께 적었습니다. [4]

## 구조

### 시스템 파일의 키

mac_apt 가 시스템 쪽 `com.apple.loginwindow.plist` 에서 읽는 키는 다음과 같습니다. [1] plist 를 여는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지에 있습니다.

| 키 | 뜻 |
|---|---|
| `autoLoginUser` | 자동 로그인 계정 |
| `GuestEnabled` | 손님 계정 사용 여부 |
| `lastUserName` | 마지막으로 로그인한 사용자 이름 |
| `lastUser` | 뜻은 공개 자료 없음 |
| `lastLoginPanic` | 뜻과 값 형식은 공개 자료 없음 |
| `AccountInfo` | 사전. mac_apt 는 그 안의 `FirstLogins`, `MaximumUsers`, `OnConsole` 을 읽음. 각 값의 뜻은 공개 자료 없음 |

키마다 어떤 형식의 값이 들어가는지는 공개 자료가 없습니다. `lastUser`, `lastLoginPanic`, `AccountInfo` 안의 값은 키 이름만으로 뜻을 짐작하지 않고, 실제 데이터에서 나온 값을 그대로 적은 뒤 다른 기록과 맞춰 봅니다.

### 관리 설정 페이로드의 키

`com.apple.loginwindow` 페이로드의 주요 키는 다음과 같습니다. [4]

| 키 | 형 | macOS | 뜻 |
|---|---|---|---|
| `SHOWFULLNAME` | boolean | 10.7+ | true 면 사용자 목록 대신 이름·암호 입력 창을 보여 줌 |
| `HideLocalUsers` | boolean | 10.7+ | 네트워크·시스템 사용자만 표시 |
| `HideAdminUsers` | boolean | 10.7+ | 관리자 사용자 숨김 |
| `HideMobileAccounts` | boolean | 10.7+ | 모바일 계정 숨김 |
| `IncludeNetworkUser` | boolean | 10.7+ | 네트워크 사용자 표시 |
| `SHOWOTHERUSERS_MANAGED` | boolean | 10.7+ | 목록에 "기타…" 표시 |
| `AdminHostInfo` | string | 10.7+ | 컴퓨터 정보 표시(HostName, SystemVersion, IPAddress) |
| `AdminMayDisableMCX` | boolean | 10.7+ | 로컬 관리자가 로그인 때 관리 설정을 우회하도록 허용 |
| `AllowList` / `DenyList` | array | 10.7+ | 로그인을 허용·거부할 사용자·그룹 GUID. `DenyList` 가 우선 |
| `LoginwindowText` | string | 10.7+ | 로그인 창에 보이는 문구 |
| `RetriesUntilHint` | integer | 10.7+ | 암호 힌트가 나오기까지 재시도 횟수 |
| `DisableConsoleAccess` | boolean | 10.7+ | `>console` 특수 사용자 이름 무시 |
| `ShutDownDisabled` / `RestartDisabled` / `SleepDisabled` | boolean | 10.7+ | 로그인 창의 해당 버튼 비활성 |
| `ShutDownDisabledWhileLoggedIn` / `RestartDisabledWhileLoggedIn` / `PowerOffDisabledWhileLoggedIn` | boolean | 10.7+ | 로그인한 동안 해당 메뉴 항목 비활성 |
| `LogOutDisabledWhileLoggedIn` | boolean | 10.13+ | 로그인한 동안 로그아웃 메뉴 비활성 |
| `DisableScreenLockImmediate` | boolean | 10.13+ | 즉시 화면 잠금 기능 비활성 |
| `showInputMenu` | boolean | 10.8+ | 로그인 창에 입력 메뉴 표시 |
| `DisableFDEAutoLogin` | boolean | 10.9+ | 파일볼트를 켠 상태의 자동 로그인 비활성 |
| `AutologinUsername` | string | 14.0+ | 자동 로그인 사용자의 짧은 이름 |
| `AutologinPassword` | string | 14.0+ | 위 사용자의 암호 |
| `ForceWifiConfigurationOnLockScreen` | boolean | 27.0+ | 로그인·잠금 화면에서 Wi-Fi 선택 허용 |
| `ForceCaptivePortalConnectionFromLockScreen` | boolean | 27.0+ | 로그인·잠금 화면에서 캡티브 포털 연결 |

이 페이로드 정의에는 `LoginHook`·`LogoutHook`·`GuestEnabled`·`DisableGuestAccount` 키가 없습니다. [4] 그래서 시스템 파일에서 `GuestEnabled` 를 봤다면 그 값은 이 페이로드에서 온 값이 아니라고 보고, 손님 계정을 관리 서버가 막았는지는 다른 페이로드나 설정을 따로 찾아봅니다. 로그인 때 스크립트를 돌리던 옛 방식인 로그인 훅이 이 파일에 남는지는 실제 데이터로 확인해야 하고, 지속성 관점의 설명은 [그 밖의 지속성 위치](../persistence/other-persistence.md) 페이지를 봅니다.

## 증거로서 의미

**증명하는 것.** `lastUserName` 은 파일을 마지막으로 쓴 시점의 마지막 로그인 사용자 이름을 알려 주고 [1][3], `autoLoginUser` 에 값이 있으면 그 계정으로 자동 로그인하도록 설정되어 있었다는 기록입니다. [1] `GuestEnabled` 는 손님 계정을 쓸 수 있게 되어 있었는지 보여 줍니다. [1] 구성 프로파일에 `com.apple.loginwindow` 페이로드가 있으면, 로그인 창에 사용자 목록이 보였는지, 누구의 로그인을 막았는지, 로그인 중 로그아웃·종료 메뉴를 막았는지를 관리 서버가 정했다는 근거가 됩니다. [4]

**증명하지 못하는 것.** `lastUserName` 은 마지막 한 명만 남기고 로그인 시각이나 이전 사용자를 남기지 않아서, 사건 시각에 누가 로그인해 있었는지는 이 값으로 정할 수 없습니다. 자동 로그인이 켜져 있으면 맥을 켠 사람이 암호를 입력하지 않고도 그 계정으로 들어갈 수 있어서, 그 계정의 활동을 계정 주인의 행동으로 곧바로 잇지 않습니다. 페이로드는 관리 서버가 정한 설정이고, 그 설정이 사건 당시에 이미 설치되어 있었는지는 프로파일 설치 기록에서 따로 확인합니다.

보고서에는 "`com.apple.loginwindow.plist` 의 `lastUserName` 은 무엇이고, `autoLoginUser` 에 이 계정이 설정되어 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

위 시스템 파일의 키 가운데 시각 값으로 알려진 것은 없고, `lastLoginPanic` 이 날짜인지도 알려져 있지 않습니다. 파일의 수정 시각은 로그인 말고도 설정이 바뀔 때 다시 쓰일 수 있어서, "마지막 로그인 시각" 으로 보고서에 적지 않습니다. 로그인과 로그아웃의 시각은 [맥 사용 시간 재구성](../../04-scenarios/activity/usage-time.md) 과 [통합 로그에서 찾을 것](../logs/unified-log-events/index.md) 에서 찾고, 이 파일의 `lastUserName` 은 그 결과의 마지막 사용자와 맞는지 확인하는 데 씁니다.

## 함정과 한계

시스템 파일의 키와 페이로드의 키는 이름이 비슷해도 다른 키입니다. 시스템 파일의 `autoLoginUser` 와 페이로드의 `AutologinUsername` 은 둘 다 자동 로그인 계정에 관한 값이지만 출처가 다르고, 보고서에는 어느 파일의 어느 키에서 읽었는지 밝혀 적습니다.

페이로드 정의에는 `AutologinPassword` 키가 문자열로 들어 있습니다. [4] 구성 프로파일 사본에 이 키가 있으면 계정 암호가 들어 있을 수 있으니, 보고서와 작업 기록에 값을 옮겨 적지 않고 키가 있다는 사실만 적습니다.

사용자 홈 폴더 쪽 `com.apple.loginwindow.plist` 는 위치만 알려져 있고 담기는 키는 공개 자료가 없습니다. [2] 시스템 파일과 같은 키가 있다고 가정하지 말고, 실제 파일에서 열어 본 키를 그대로 적습니다.

파일이 없거나 `lastUserName` 이 계정 목록에 없는 이름이면, 계정을 지웠거나 파일에 손댄 흔적일 수도 있지만 이 파일 하나로 결론 내리지 않습니다. 지운 계정은 [사용자 계정](user-accounts/index.md) 페이지의 안내를 따라 찾고, 전체 판단은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 시나리오를 따릅니다.

## 직접 분석해 보기

### 헥스로 한 번

바이너리 plist 는 키 이름을 문자열 객체로 저장해서, 헥스 편집기에서 `lastUserName` 이나 `autoLoginUser` 를 검색하면 파일 안에 그 키가 있는지부터 확인할 수 있습니다. 키와 값을 잇는 오프셋 표를 따라가 값을 읽는 절차는 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지에 있습니다. 키가 없는 것과 값이 빈 문자열인 것은 뜻이 다를 수 있으니, 헥스에서 둘을 나눠 적습니다.

> 그림 자리: 헥스 편집기에서 `lastUserName` 키 문자열과 이어지는 사용자 이름 값을 표시한 화면(명세로 만든 예시 파일 기준)

### 공개 도구로 한 번

mac_apt 의 `BASICINFO` 플러그인은 시스템 쪽 `com.apple.loginwindow.plist` 의 위 키를 기본 정보로 냅니다. [1] 구성 프로파일 안의 페이로드는 프로파일을 열어 유형이 `com.apple.loginwindow` 인 페이로드를 찾아 읽고, 프로파일을 찾는 자리와 여는 법은 [구성 프로파일](../persistence/configuration-profiles.md) 페이지를 따릅니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 내용 |
|---|---|
| [사용자 계정](user-accounts/index.md) | `lastUserName`·`autoLoginUser` 가 실제 계정인지, 자동 로그인 암호 파일이 있는지 |
| [구성 프로파일](../persistence/configuration-profiles.md) | 로그인 창 페이로드가 언제 설치되었는지 |
| [파일볼트](../../01-foundations/protection/filevault/index.md) | 파일볼트가 켜져 있었는지와 자동 로그인 설정이 서로 맞는지 |
| [통합 로그에서 찾을 것](../logs/unified-log-events/index.md) | 로그인·로그아웃 이벤트와 마지막 사용자 |
| [그 밖의 지속성 위치](../persistence/other-persistence.md) | 로그인 훅 같은 로그인 때 실행되는 항목 |

## 실습

공개된 시험용 맥 이미지(NIST CFReDS 등)로 다음 질문을 풀어 봅니다.

1. 시스템 쪽 `com.apple.loginwindow.plist` 를 열어 mac_apt 가 읽는 여섯 키 가운데 어떤 키가 있는지, 값은 무엇인지 적어 봅니다.
2. `lastUserName` 이 계정 목록의 어느 계정과 맞는지 확인하고, 통합 로그에서 찾은 마지막 로그인 사용자와 비교합니다.
3. `autoLoginUser` 에 값이 있다면, 그 설정이 사건 시각의 사용자 판단에 어떤 영향을 주는지 적어 봅니다.
4. 사용자 홈 폴더마다 `com.apple.loginwindow.plist` 가 있는지 찾고, 어떤 키가 들어 있는지 시스템 파일과 비교합니다.
5. 구성 프로파일이 있다면 `com.apple.loginwindow` 페이로드를 찾아 `SHOWFULLNAME`, `DenyList`, `DisableFDEAutoLogin` 값을 읽어 봅니다.

## 참고 문헌

1. mac_apt `BASICINFO` 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/basicinfo.py
2. ForensicArtifacts `macos.yaml` (MacOSLoginWindowPlistFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
3. Forensics Wiki, Mac OS X 10.9 artifacts location — https://forensics.wiki/mac_os_x_10.9_artifacts_location/
4. Apple device-management 저장소, `com.apple.loginwindow` 페이로드 정의 — https://raw.githubusercontent.com/apple/device-management/release/mdm/profiles/com.apple.loginwindow.yaml
