---
title: "소프트웨어 업데이트 기록"
parent: "아티팩트 · 시스템·계정"
nav_order: 550
---

# 소프트웨어 업데이트 기록 (Software Update)

`com.apple.SoftwareUpdate.plist` 에는 마지막으로 업데이트에 성공한 시각과 그때의 운영체제 버전, 그리고 권장 업데이트 목록이 남고, 설치 이력 파일과 자동 업데이트 설정을 함께 보면 이 맥이 언제 어떤 상태로 업데이트를 받았는지 추정할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

맥은 소프트웨어 업데이트(Software Update)를 확인하고 받고 설치하는 과정의 결과를 설정 파일 `com.apple.SoftwareUpdate.plist` 에 적습니다. 공개 타임라인 도구 plaso 에는 이 파일만 읽는 plist 플러그인 `macos_software_update` 가 있고, 플러그인 주석은 `LastFullSuccessfulDate` 를 "전체 업데이트 시각", `LastSuccessfulDate` 를 "부분 업데이트 시각" 으로 설명합니다. [2] 다만 이 두 날짜가 업데이트 확인(검사)에 성공한 시각인지, 실제로 설치한 시각인지는 Apple 이 공식으로 설명하지 않습니다. 그래서 두 키의 뜻은 plaso 의 해석으로만 읽습니다.

조사에서 이 기록이 쓸모 있는 곳은 두 가지입니다. 하나는 사고 당시 시스템이 얼마나 최신이었는지 보는 일이고, 알려진 취약점이 고쳐지기 전 버전이었는지 판단할 때 근거가 됩니다. 다른 하나는 자동 업데이트 설정으로, 자동 확인이나 보안 데이터 설치가 꺼져 있으면 보안 업데이트가 늦게 들어간 이유를 설명할 수 있습니다. 그 값을 관리 서버가 강제했는지 사용자가 바꿨는지는 [구성 프로파일](../persistence/configuration-profiles.md) 기록과 함께 봐야 구분할 수 있습니다.

설치한 패키지의 이력은 `/Library/Receipts/InstallHistory.plist` 에 따로 쌓이고, 이 파일은 [OS 버전과 설치 기록](os-version-install-history.md) 페이지가 본문으로 다룹니다. 여기서는 업데이트와 이어지는 부분만 짧게 씁니다.

## 위치와 버전별 차이

| 기록 | 위치 | 비고 |
|---|---|---|
| 마지막 업데이트 상태 | 파일 이름 `com.apple.SoftwareUpdate.plist` | plaso 는 경로가 아니라 파일 이름(대소문자 무시)으로 이 파일을 알아봅니다 [2] |
| 설치 이력 | `/Library/Receipts/InstallHistory.plist` | 본문은 [OS 버전과 설치 기록](os-version-install-history.md) [1] |
| 자동 업데이트 관리 설정 | MDM 페이로드 `com.apple.SoftwareUpdate` | 관리 서버가 내려보내는 구성 프로파일 [4] |

plaso 는 파일 이름만 보고 이 파일을 알아보므로, 전체 경로는 이미지에서 파일 이름으로 검색해 실제로 놓인 자리를 찾고, 보고서에도 찾은 경로를 그대로 적습니다. 이 파일의 키가 macOS 버전마다 어떻게 달라지는지(예: Big Sur 이후 키 변화)는 실제 데이터로 확인해야 합니다. 아래 버전 표는 MDM 페이로드의 버전별 변화입니다. [4]

| macOS 버전 | 바뀐 점 |
|---|---|
| 10.7 | MDM 페이로드 `com.apple.SoftwareUpdate` 와 `CatalogURL` 키 도입 |
| 10.9 | `AllowPreReleaseInstallation` 키 도입 |
| 10.14 | `restrict-software-update-require-admin-to-install` 키 도입 |
| 10.15 | 자동 업데이트 키 6개(`AutomaticallyInstallMacOSUpdates` 등) 도입 |
| 11 | `CatalogURL`(사내 업데이트 카탈로그 지정) 사용 중단, 지원 안 함 |
| 26 | 페이로드 `com.apple.SoftwareUpdate` 사용 중단 표시, 선언형 관리(declarative management) 구성 `com.apple.configuration.softwareupdate.settings` 로 대체 |
| 27 | 페이로드 제거 예정 표시 |

## 구조

### com.apple.SoftwareUpdate.plist

plaso 가 이 파일에서 찾는 키는 여섯 개이고, 여섯 키가 최상위에 모두 있어야 이 플러그인이 파일을 처리합니다. 날짜 키는 plist 의 `date` 형식으로 읽습니다. [2] plist 의 형식과 날짜 값 저장 방식은 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지에 있습니다.

| 키 | plaso 가 하는 일 | plaso 출력 |
|---|---|---|
| `LastFullSuccessfulDate` | 날짜로 읽음. 주석은 "전체 업데이트 시각" | `full_update_time` |
| `LastSuccessfulDate` | 날짜로 읽음. 주석은 "부분 업데이트 시각" | `update_time` (위 값과 다를 때만) |
| `LastAttemptSystemVersion` | 문자열로 읽음 | `system_version` |
| `LastUpdatesAvailable` | 참(0이 아님)인지 봄 | 참일 때만 아래 배열을 읽음 |
| `RecommendedUpdates` | 원소마다 `Identifier` 와 `Product Key` 를 꺼냄 | "Identifier (Product Key)" 형식의 문자열 목록 |
| `LastRecommendedUpdatesAvailable` | 있어야 하는 키로만 확인하고 값은 쓰지 않음 | 없음 |

`LastSuccessfulDate` 가 `LastFullSuccessfulDate` 와 같으면 plaso 는 `full_update_time` 하나만 내고 `update_time` 은 따로 내지 않습니다. [2] 그래서 plaso 결과에 `update_time` 이 없다고 해서 원본 파일에 `LastSuccessfulDate` 키가 없는 것은 아니고, 필요하면 원본 plist 를 직접 열어 확인합니다. `LastAttemptSystemVersion` 은 키 이름대로 마지막으로 업데이트를 시도할 때의 운영체제 버전 문자열로 나옵니다. [2]

### 자동 업데이트 설정 키 (MDM 페이로드)

MDM 페이로드 `com.apple.SoftwareUpdate` 의 키는 다음과 같습니다. 이 페이로드는 기기 채널에서만 쓰고 한 기기에 하나만 설치하며, 사용자 등록(User Enrollment) 기기에서는 쓸 수 없습니다. [4]

| 키 | 형식·기본값 | 도입 | 값에 따른 동작 |
|---|---|---|---|
| `CatalogURL` | 문자열 | 10.7 | 업데이트 카탈로그 URL. 11 부터 지원 안 함 |
| `AllowPreReleaseInstallation` | 불리언, true | 10.9 | true 면 베타(프리릴리스) 설치 가능 |
| `restrict-software-update-require-admin-to-install` | 불리언, false | 10.14 | true 면 앱 설치를 관리자로 제한 |
| `AutomaticallyInstallMacOSUpdates` | 불리언, true | 10.15 | false 면 "Install macOS Updates" 선택을 막고 사용자가 못 바꿈 |
| `AutomaticallyInstallAppUpdates` | 불리언, true | 10.15 | false 면 "Install app updates from the App Store" 해제, 변경 금지 |
| `AutomaticCheckEnabled` | 불리언, true | 10.15 | false 면 "Check for updates" 해제, 변경 금지 |
| `AutomaticDownload` | 불리언, true | 10.15 | false 면 "Download new updates when available from the App Store" 해제, 변경 금지 |
| `CriticalUpdateInstall` | 불리언, true | 10.15 | false 면 중요 업데이트 자동 설치를 끄고 "Install system data files and security updates" 변경 금지 |
| `ConfigDataInstall` | 불리언, true | 10.15 | false 면 구성 데이터(configuration data) 자동 설치 제한 |

`restrict-software-update-require-admin-to-install` 은 `com.apple.appstore` 페이로드의 `restrict-store-require-admin-to-install` 과 같은 기능입니다. [4] 이 표의 키 이름은 MDM 프로파일 안에서 쓰는 이름이고, 같은 이름의 키가 로컬 `com.apple.SoftwareUpdate.plist` 에 사용자 설정으로도 저장되는지, 관리 설정이 어느 폴더에 놓이는지는 실제 데이터로 확인해야 합니다. 프로파일 자체를 어디서 찾는지는 [구성 프로파일](../persistence/configuration-profiles.md) 페이지를 봅니다.

### InstallHistory.plist 의 업데이트 항목

설치 이력 항목에는 `date`, `displayName`, `displayVersion`, `packageIdentifiers`, `processName`, `contentType` 키가 있습니다. [1] `com.apple.SoftwareUpdate.plist` 의 날짜 가까이에 있는 항목을 찾아 맞춰 볼 수 있지만, 업데이트 설치가 어떤 `processName` 값으로 남는지와 `contentType` 값이 보안 데이터 업데이트를 뜻하는지는 실제 데이터로 확인해야 합니다. 파일 전체의 해석은 [OS 버전과 설치 기록](os-version-install-history.md) 페이지에 있습니다.

## 증거로서 의미

**증명하는 것.** `LastAttemptSystemVersion` 은 마지막으로 업데이트를 시도할 때 이 맥이 어느 운영체제 버전이었는지 알려 주고, 두 날짜 키는 plaso 해석에 따르면 전체 업데이트와 부분 업데이트에 마지막으로 성공한 시각입니다. `LastUpdatesAvailable` 이 참이면 `RecommendedUpdates` 에 그 시점에 권장된 업데이트의 식별자와 제품 키가 남아 있어서, 적어도 그 시점에는 그 업데이트들이 설치되지 않았다는 쪽으로 읽을 수 있습니다. MDM 설정 키는 자동 확인·자동 다운로드·보안 데이터 설치를 관리 서버가 어떻게 정해 두었는지 보여 줍니다.

**증명하지 못하는 것.** 날짜 키가 검사 시각인지 설치 시각인지 Apple 이 공식으로 밝히지 않았으니, 보고서에 "이 시각에 업데이트를 설치했다" 고 단정하지 않습니다. `RecommendedUpdates` 는 권장된 목록이지 설치된 목록이 아니고, 누가 업데이트를 눌렀는지, 자동 업데이트였는지 사람이 한 것인지도 이 파일로는 알 수 없습니다. plaso 는 키마다 값 하나만 읽고 이 파일에서 과거 값의 목록은 나오지 않아서, 지난 업데이트의 흐름은 설치 이력과 로그에서 찾습니다.

보고서에는 "`com.apple.SoftwareUpdate.plist` 의 `LastFullSuccessfulDate` 값은 이 시각이고, plaso 는 이 키를 전체 업데이트 시각으로 해석한다. 같은 시간대에 `InstallHistory.plist` 에 이러이러한 설치 항목이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

두 날짜 키는 plist `date` 형식으로 저장되고 plaso 는 이를 날짜 값으로 바꿔 읽습니다. [2] plist 날짜가 어떤 기준 시각에서 세는 값인지와 읽는 법은 [맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md) 과 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지에 있습니다. 이 파일의 값이 UTC 인지 현지 시각인지는 공개된 자료가 없으니, 같은 시간대의 `InstallHistory.plist` 항목 `date` 와 맞춰 보고, 기기의 시간대는 [시간대와 시계 설정](time-zone.md) 에서 따로 확인합니다.

값이 바뀌는 조건도 공식 설명이 없습니다. `softwareupdate --list` 나 `--background` 는 업데이트 검사를 일으키는 옵션이라 날짜 키를 바꿀 가능성이 있으므로 이미지 확보 전에는 돌리지 않습니다.

## 함정과 한계

plaso 는 여섯 키가 모두 있는 파일만 이 플러그인으로 처리하므로, 키가 하나라도 빠진 파일은 결과에 아예 나오지 않습니다. [2] 그러니 plaso 결과에 이 항목이 없다고 해서 파일이 없거나 비어 있다고 보지 않고, 원본 plist 를 직접 엽니다.

plaso 의 이 플러그인이 내는 데이터 형식 이름은 `macos:software_updata:entry` 이고, 원본 코드의 철자 "updata" 가 그대로 남아 있습니다. [2] 결과를 걸러 볼 때 "update" 로 검색하면 이 항목을 놓칠 수 있습니다.

`update_time` 이 따로 나오지 않는 경우도 헷갈리기 쉽습니다. 앞에서 적었듯 두 날짜가 같으면 plaso 는 `full_update_time` 하나만 내므로, 이를 "부분 업데이트가 없었다" 로 읽으면 안 됩니다.

MDM 설정 키는 관리 서버가 강제한 값이고, 사용자가 시스템 설정에서 직접 바꾼 값과 같은 자리에 같은 이름으로 남는지는 공개된 자료가 없습니다. 설정값이 꺼져 있다는 사실만으로 사용자가 일부러 업데이트를 막았다고 보지 않고, 구성 프로파일 설치 기록과 함께 판단합니다.

파일이 아예 없거나 날짜가 설치 이력·운영체제 버전과 맞지 않으면 지워지거나 손댄 흔적일 수도 있지만, 이 파일 하나로 결론 내리지 않습니다. 이전 값은 [스냅숏과 백업 비교](../../03-techniques/analysis/snapshot-diff.md) 로 찾아보고, 전체 판단은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 시나리오를 따릅니다.

신속 보안 대응(Rapid Security Response)이나 백그라운드 보안 개선이 어떤 흔적으로 남는지는 실제 데이터로 확인해야 합니다.

## 직접 분석해 보기

### 헥스로 한 번

헥스 편집기에서 `LastFullSuccessfulDate` 같은 키 이름을 검색하면 파일 안에 그 키가 있는지부터 확인할 수 있습니다. 키와 값이 어떻게 이어지는지, 날짜 객체를 어떻게 읽는지는 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지의 절차를 그대로 따릅니다. 헥스로 읽은 날짜는 도구 결과와 맞춰 보고, 어긋나면 도구 쪽 해석을 다시 확인합니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

> 그림 자리: 헥스 편집기에서 `LastFullSuccessfulDate` 키 문자열과 이어지는 날짜 객체를 표시한 화면(명세로 만든 예시 파일 기준)

### 공개 도구로 한 번

plaso 의 `macos_software_update` 플러그인은 형식 이름 "MacOS software update plist file" 로 이 파일을 처리하고, 결과에는 `full_update_time`, `update_time`, `system_version`, 권장 업데이트 문자열이 한 항목으로 나옵니다. [2] 타임라인에서 이 항목을 고를 때는 앞에서 적은 형식 이름 `macos:software_updata:entry` 를 씁니다. 타임라인에 넣는 일반 절차는 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 페이지에 있습니다.

설치 이력은 mac_apt 의 `INSTALLHISTORY` 플러그인으로 읽을 수 있고, 출력 열은 ContentType, Date, DisplayName, DisplayVersion, PackageIdentifiers, ProcessName, Source 입니다. `PackageIdentifiers` 는 여러 값을 쉼표로 이어 한 열에 적습니다. 이미지 전체가 없고 `InstallHistory.plist` 파일 하나만 있을 때도 이 파일만 넣어 분석하는 모드로 읽을 수 있습니다. [1] plaso 에도 설치 이력용 plist 플러그인 `install_history.py` 가 있습니다. [3]

### 라이브 시스템에서

켜져 있는 맥을 조사할 때는 `softwareupdate` 명령으로 현재 상태를 볼 수 있지만, 어떤 옵션은 시스템을 바꿉니다. [5] 라이브 대응 전반의 순서는 [라이브 대응](../../03-techniques/process-acquisition/live-response/index.md) 페이지를 따르고, 명령 결과는 실행 시각과 함께 적어 둡니다.

| 옵션 | 동작 | 조사 중 주의 |
|---|---|---|
| `--schedule` | 기기 전체의 자동(백그라운드) 확인 설정 상태를 돌려줌. on/off 로 바꿀 수도 있음 | 인자 없이 상태만 확인 |
| `-l`, `--list` | 사용 가능한 macOS 업데이트와 일부 소프트웨어 업데이트 표시. 보안 데이터 업데이트는 `--include-config-data` 를 붙여야 나옴 | 검사를 일으켜 기록을 바꿀 수 있음 |
| `--background` | 업데이트 검사를 백그라운드로 한 번 강제로 실행 | 위와 같음 |
| `--list-full-installers` | 받을 수 있는 macOS 설치 프로그램 목록 | 목록 확인만 하고 받지 않음 |
| `-d`, `--download` / `-i`, `--install` | 내려받기만 함 / 내려받아 설치(root 필요) | 증거를 바꾸므로 쓰지 않음 |
| `--fetch-full-installer`, `--install-rosetta` | 설치 프로그램 받기 / Rosetta 설치 | 증거를 바꾸므로 쓰지 않음 |

`--ignore` 와 `--reset-ignored` 는 더는 지원하지 않습니다. [5] 설치 이력을 보여 주는 옵션은 알려진 것이 없습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 내용 |
|---|---|
| [OS 버전과 설치 기록](os-version-install-history.md) | `LastAttemptSystemVersion` 과 현재 운영체제 버전, 날짜 키와 가까운 설치 이력 항목 |
| [설치 로그](../logs/install-log.md) | 같은 시간대의 업데이트 검사·다운로드·설치 기록 |
| [통합 로그에서 찾을 것](../logs/unified-log-events/index.md) | 같은 시간대의 업데이트 관련 이벤트 |
| [구성 프로파일](../persistence/configuration-profiles.md) | 자동 업데이트 키를 강제한 프로파일과 설치 시각 |
| [보안 도구 기록](../logs/xprotect.md) | `CriticalUpdateInstall`·`ConfigDataInstall` 이 꺼져 있을 때 보안 도구 쪽 기록 |
| [설치한 앱과 영수증](installed-apps-receipts.md) | 앱 업데이트와 영수증 |

## 실습

공개 시험 자료(NIST CFReDS 등)의 맥 이미지로 다음 질문을 풀어 봅니다.

1. 이미지에서 `com.apple.SoftwareUpdate.plist` 를 파일 이름으로 찾고, 놓인 경로와 키 목록을 적어 봅니다. plaso 가 찾는 여섯 키 가운데 빠진 키가 있는지, 그래서 plaso 결과에 이 항목이 나오지 않는지도 봅니다.
2. `LastFullSuccessfulDate` 와 `LastSuccessfulDate` 가 같은지 다른지 확인하고, plaso 결과에 `update_time` 이 나오는지 맞춰 봅니다.
3. `LastAttemptSystemVersion` 과 이미지의 현재 운영체제 버전이 같은지 봅니다. 다르다면 그 사이에 무엇이 있었는지 `InstallHistory.plist` 에서 찾아봅니다.
4. `RecommendedUpdates` 에 남은 업데이트가 설치 이력에 나중에 나타나는지 확인합니다.
5. 구성 프로파일이 있다면 자동 업데이트 키 가운데 false 인 것이 있는지 보고, 그 값이 사고 당시 보안 업데이트 상태를 설명하는지 따져 봅니다.

## 참고 문헌

1. mac_apt, `plugins/installhistory.py` (INSTALLHISTORY 플러그인 소스) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/installhistory.py
2. plaso, `plaso/parsers/plist_plugins/software_update.py` (macos_software_update 플러그인 소스) — https://github.com/log2timeline/plaso/blob/main/plaso/parsers/plist_plugins/software_update.py, 같은 폴더의 `interface.py`(키·파일 이름 판정) — https://github.com/log2timeline/plaso/blob/main/plaso/parsers/plist_plugins/interface.py
3. plaso, `plaso/parsers/plist_plugins` 폴더 목록 — https://github.com/log2timeline/plaso/tree/main/plaso/parsers/plist_plugins
4. Apple, device-management 스키마 `mdm/profiles/com.apple.SoftwareUpdate.yaml` — https://github.com/apple/device-management/blob/release/mdm/profiles/com.apple.SoftwareUpdate.yaml
5. SS64, "softwareupdate Man Page - macOS" — https://ss64.com/mac/softwareupdate.html
