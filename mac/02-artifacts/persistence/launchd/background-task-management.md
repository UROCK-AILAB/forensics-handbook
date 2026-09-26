---
title: "백그라운드 작업 관리"
parent: "실행 에이전트·데몬"
grand_parent: "아티팩트 · 자동 실행·지속성"
nav_order: 590
---

# 백그라운드 작업 관리 (BTM·Background Items)

백그라운드 작업 관리 (Background Task Management, BTM)는 macOS 13부터 로그인 항목·실행 에이전트·실행 데몬의 등록을 추적하는 기능이고, 등록 목록과 사용자 승인 상태는 `/private/var/db/com.apple.backgroundtaskmanagement/` 의 `.btm` 파일에 남습니다.

## 무엇을 기록하나 · 왜 생기나

macOS 13부터 BTM이 로그인 항목과 실행 에이전트·데몬을 관리하고, 사용자는 그 목록을 시스템 설정의 일반 → 로그인 항목 화면에서 봅니다 [1]. 이런 항목이 설치되면 사용자에게 알림이 하나 뜨고, 사용자는 알림을 일주일이나 하루 미루거나 닫을 수 있으며 닫으면 다음 설치 때 다시 뜹니다 [1].

앱이 스스로 도우미를 등록하는 길도 BTM과 이어집니다. SMAppService(macOS 13.0 이상)는 앱 번들 안의 로그인 항목·에이전트·데몬 도우미를 등록하고, 등록한 뒤 실제로 실행되는지는 사용자 승인에 달려 있습니다 [2]. 이 API에는 `mainApp`, `agent(plistName:)`, `daemon(plistName:)`, `loginItem(identifier:)`, `register()`, `unregister()`, `statusForLegacyPlist(at:)`, `openSystemSettingsLoginItems()` 가 있습니다 [2].

그래서 macOS 13 이후 기기에서는 폴더에 놓인 plist와 별도로, 시스템이 "이런 항목이 등록돼 있고 사용자가 이렇게 처리했다" 고 적어 둔 목록을 하나 더 얻을 수 있습니다. 폴더 쪽 위치는 [위치와 적용 범위 (Locations)](locations.md)에 있습니다.

## 위치와 버전별 차이

```
/private/var/db/com.apple.backgroundtaskmanagement/BackgroundItems-v*.btm
```

이 파일을 읽으려면 전체 디스크 접근 권한(Full Disk Access)이 필요합니다 [3]. 파일 이름의 버전 번호는 macOS 버전에 따라 다릅니다.

| macOS | 파일 이름 [3] |
|---|---|
| 13.0 | `BackgroundItems-v*.btm` (번호는 실제 기기에서 확인) |
| 13.1 | `BackgroundItems-v7.btm` |

`BackgroundItems-v4.btm` 이라는 이름도 쓰였고 [3], macOS 13.2 이후의 번호는 실제 기기에서 확인합니다. DumpBTM은 그 폴더에서 `.btm` 으로 끝나는 파일 목록의 마지막 것을 골라 읽으므로 [4], 수집할 때는 폴더 안의 `.btm` 파일을 모두 가져오고 어느 파일을 분석했는지 기록합니다.

## 구조

파일은 NSKeyedArchiver로 직렬화한 바이너리 plist이고, 최상위 키 `store` 에 `Storage` 객체가 들어 있습니다 [3][4]. 아래 구조는 공개 도구 DumpBTM의 소스를 기준으로 합니다(2023-01-20 판) [4]. NSKeyedArchiver plist를 푸는 일반 원리는 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에 있습니다.

`Storage` 에는 두 묶음이 있습니다 [4].

| 속성 | 내용 [4] |
|---|---|
| `itemsByUserIdentifier` | 키는 사용자 UUID, 값은 `ItemRecord` 배열 |
| `mdmPayloadsByIdentifier` | MDM 페이로드 |

사용자 UUID는 UID가 아니라서 따로 풀어야 하고, Open Directory에서 GUID 속성(kODAttributeTypeGUID)으로 사용자를 찾아 UniqueID를 읽으면 풀립니다 [4]. 디스크 이미지에서는 [사용자 계정 (Local Accounts)](../../system-account/user-accounts/index.md)의 계정 기록과 맞춰 풀고, UUID와 UID의 차이는 [식별자 읽기 (UUID·UID·GUID)](../../../01-foundations/value-decoding/uuid-uid.md)에 있습니다.

`ItemRecord` 하나가 등록 항목 하나이고, 속성은 아래와 같습니다 [4].

| 속성 | 내용 |
|---|---|
| `type` | 항목 종류 비트 (아래 표) |
| `generation` | 세대 값 |
| `disposition` | 사용자 처리 상태 비트 (아래 표) |
| `url` | 항목 위치. agent·daemon은 plist 경로 |
| `uuid`·`identifier` | 항목 식별자 |
| `name`·`developerName` | 이름과 개발자 이름 |
| `bookmark` | NSData. 파일 참조 데이터 |
| `container` | 부모 항목의 identifier |
| `embeddedItems` | 이 항목에 딸린 항목 |
| `executablePath` | 실행 파일 경로 |
| `teamIdentifier`·`bundleIdentifier` | 팀 ID와 번들 ID |
| `lightweightRequirement` | NSData |
| `associatedBundleIdentifiers` | 연결된 번들 ID |

`url` 로 항목을 찾는 방법은 종류마다 다릅니다. agent·daemon 항목은 `url` 이 곧 plist 경로이고, login item 항목은 부모(`container`) 항목의 url 경로 뒤에 자기 url을 붙여 번들을 찾습니다 [4]. `bookmark` 를 푸는 법은 [파일 참조 데이터 (Alias·Bookmark)](../../../01-foundations/value-decoding/alias-bookmark.md)에, 팀 ID와 번들 ID를 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다. `associatedBundleIdentifiers` 는 plist의 `AssociatedBundleIdentifiers` 키와 이름이 같습니다([plist 키 해석](plist-keys.md)).

### type 비트

| 비트 | 이름 [4] |
|---|---|
| 0x2 | app |
| 0x4 | login item |
| 0x8 | agent |
| 0x10 | daemon |
| 0x20 | developer |
| 0x10000 | legacy |
| 0x80000 | curated |

표에 없는 비트(0x1 등)는 뜻이 공개되지 않았으므로, 켜져 있으면 값을 그대로 적고 뜻을 짐작하지 않습니다.

### disposition 비트

| 비트 | 켜짐 | 꺼짐 [4] |
|---|---|---|
| 0x1 | enabled | disabled |
| 0x2 | allowed | disallowed |
| 0x4 | hidden | visible |
| 0x8 | notified | not notified |

아래 값은 위 두 표로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다.

```
type        0x10008 = 0x10000 (legacy) + 0x8 (agent)
disposition 0x3     = 0x1 (enabled) + 0x2 (allowed), 0x4 꺼짐 (visible), 0x8 꺼짐 (not notified)
```

이 예시는 "legacy 로 표시된 에이전트 항목이고, 켜져 있고 허용됐으며, visible 이고, notified 비트는 꺼져 있다" 로 읽습니다.

## MDM 규칙

MDM의 `com.apple.servicemanagement` 페이로드에 들어가는 규칙은 아래와 같고, 규칙마다 종류(`RuleType`)와 값(`RuleValue`), 선택 항목 `Comment` 가 있습니다 [1].

| RuleType | 맞추는 대상 [1] |
|---|---|
| `BundleIdentifier` | 번들 ID |
| `BundleIdentifierPrefix` | 번들 ID 앞부분 |
| `TeamIdentifier` | 개발자 팀 ID |
| `Label` | plist `Label` 과 정확히 일치 |
| `LabelPrefix` | plist `Label` 앞부분 |

BTM 파일의 `mdmPayloadsByIdentifier` 에 페이로드가 들어 있으면 관리 규칙이 걸린 맥이라서, 항목의 상태를 사용자가 한 일로 읽기 전에 규칙과 먼저 맞춰 봅니다. 프로파일 자체는 [구성 프로파일 (Configuration Profiles·MDM)](../configuration-profiles.md)에서 확인합니다.

## 증거로서 의미

**증명하는 것.** 기록에 항목이 있으면 BTM이 그 로그인 항목·에이전트·데몬을 등록 항목으로 알고 있었다는 뜻이고, 항목이 어느 사용자 UUID 아래에 있는지, 어떤 종류인지, 켜짐·허용·숨김·알림 상태가 어땠는지, 개발자 이름과 팀 ID·번들 ID가 무엇으로 적혀 있었는지를 말할 수 있습니다. 폴더에서 plist가 지워졌더라도 기록에 plist 경로가 남아 있으면 그 경로에 항목이 등록된 적이 있다는 단서가 됩니다.

**증명하지 못하는 것.** 등록됐다는 사실은 실행됐다는 뜻이 아닙니다. allowed 비트만으로는 누가 허용했는지 알 수 없고, 누가 항목을 설치했는지도 기록에는 없습니다.

## 시각 해석

DumpBTM이 읽는 `ItemRecord` 속성에는 시각 필드가 없습니다 [4]. 그래서 이 기록만으로는 항목이 언제 등록됐는지, 사용자가 언제 알림을 처리했는지를 말할 수 없습니다. 파일의 다른 곳에 시각 정보가 있는지는 공개 자료가 없으므로, 시기는 `.btm` 파일의 파일 시스템 시각, 항목이 가리키는 plist와 실행 파일의 시각, 통합 로그 같은 다른 기록으로 좁힙니다. 여러 기록을 한 시간축에 놓는 방법은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)에 있습니다.

## 함정과 한계

`sfltool resetbtm` 은 로그인·백그라운드 항목 데이터를 초기화하는 명령이라서 [1], 라이브 시스템에서 수집하기 전에 실행하면 기록을 스스로 지우게 됩니다. 반대로 조사 대상 맥에 이 명령을 실행한 흔적이 있으면 기록이 초기화됐을 가능성을 염두에 두고 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)를 함께 봅니다.

DumpBTM은 `/System/Library/PrivateFrameworks/BackgroundTaskManagement.framework/Resources/backgroundtaskmanagementd` 를 dlopen해 클래스 정의를 얻은 뒤 파일을 풀기 때문에 macOS 위에서 도는 도구입니다 [4]. macOS가 아닌 분석 환경에서 일반 plist 도구 같은 다른 도구로 푼 결과는 macOS 위의 DumpBTM이나 `sfltool dumpbtm` 결과와 맞춰 봅니다.

파일 버전이 macOS 업데이트에 따라 바뀌므로, 위 구조가 모든 버전에 그대로 맞는다고 가정하지 않습니다. 위 구조는 DumpBTM 소스(2023-01-20) 기준입니다.

## 직접 분석해 보기

**macOS 기본 명령.** `sfltool dumpbtm` 은 로그인·백그라운드 항목의 현재 상태를 출력합니다 [1]. 라이브 대응에서는 이 출력을 그대로 저장해 두고, `resetbtm` 은 실행하지 않습니다.

```
sfltool dumpbtm
```

**공개 도구.** DumpBTM은 `sfltool dumpbtm` 의 오픈소스판이고 [3], 파일을 읽으려면 전체 디스크 접근 권한이 필요합니다 [3]. 수집한 `.btm` 파일을 분석용 macOS에서 풀어 항목마다 `type`·`disposition` 을 위 표로 해석하고, agent·daemon 항목의 `url` 을 이미지 속 plist와 맞춰 봅니다.

**로그.** Console에서는 `subsystem:backgroundtaskmanagement` 와 `category:mcx` 로 거르고, 터미널에서는 서브시스템을 `com.apple.backgroundtaskmanagement`, 범주를 `mcx` 로 거르는 `log stream` 을 씁니다 [1]. 이 필터는 MDM 규칙이 적용되는지 확인하는 용도이고, 등록·승인 때 남는 로그 문구는 실제 기기에서 확인합니다. 로그 형식은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있습니다. 도우미가 어느 앱에 딸렸는지 적은 귀속 (attribution) 정보는 `/System/Library/PrivateFrameworks/BackgroundTaskManagement.framework/Versions/A/Resources/attributions.plist` 에 있습니다 [1].

## 교차 검증

- [위치와 적용 범위 (Locations)](locations.md) — `url` 이 가리키는 plist가 폴더에 아직 있는지
- [로그인 항목 (Login Items)](../login-items.md) — login item 항목과 함께 볼 때
- [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../../01-foundations/protection/codesign-notarization-sip.md) — 팀 ID와 실행 파일 서명을 맞춰 볼 때
- [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md)
- [악성 코드 지속성 찾기 (Persistence)](../../../04-scenarios/incident/persistence.md)

## 참고 문헌

1. Apple Platform Deployment — Manage login items and background tasks on Mac — https://support.apple.com/guide/deployment/manage-login-items-background-tasks-mac-depdca572563/web
2. Apple Developer, SMAppService (문서 JSON) — https://developer.apple.com/tutorials/data/documentation/servicemanagement/smappservice.json
3. Objective-See, DumpBTM README — https://github.com/objective-see/DumpBTM
4. Objective-See, DumpBTM 소스 `library/code/dumpBTM.m`, `library/code/dumpBT_Internal.h` (Patrick Wardle, 2023-01-20) — https://github.com/objective-see/DumpBTM/tree/main/library/code
