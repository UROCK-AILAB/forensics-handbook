---
title: "설치된 앱"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 410
---

# 설치된 앱 (Installed Apps·applicationState.db)

## 한 줄 요약

설치된 앱 목록은 주로 `applicationState.db` 에서 만들고, 앱 번들 폴더의 메타데이터 plist, 홈 화면 배치 파일, 백업의 `Info.plist`·`Manifest.plist` 로 보강하며, 이 기록들은 "수집 시점에 이 번들 ID 의 앱이 기기에 있었다" 는 상태를 보여 줍니다.

## 무엇을 기록하나 · 왜 생기나

`applicationState.db` 는 앱의 설치 컨테이너와 데이터 위치를 보여 줍니다[4]. 이 DB 에서는 `application_identifier_tab` 이 번들 ID 를 번호에 잇고, `kvs` 가 앱과 데이터 경로를 잇고, `key_tab` 이 key 번호를 이름에 잇습니다[3]. 앱 컨테이너 구조 자체는 [iOS의 파일 시스템](../../01-foundations/storage/filesystem/index.md), 번들 ID 읽는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에서 다룹니다.

iOS 15 이미지로 여러 도구를 비교한 글에 따르면 대부분의 도구가 `applicationstate.db` 로 설치 앱 목록을 만들고, 일부 도구는 각 번들 폴더의 `iTunesMetadata.plist`·`BundleMetadata.plist` 를 함께 씁니다[1]. 같은 글은 홈 화면 항목을 담은 `IconState.plist` 와 각 앱 컨테이너 최상위의 `.com.apple.mobile_container_manager.metadata.plist` 를 보조 자료로 들고, 설치·제거 활동과 앱별 사용 기간은 Mobile Installation 로그로 잡는다고 적었습니다[1]. `iTunesMetadata.plist` 로 앱을 어디서 받았는지 보는 방법은 [앱 스토어 기록](app-store.md) 에서 다룹니다.

## 위치와 버전별 차이

### 기기 안 경로

```
/private/var/mobile/Library/FrontBoard/applicationState.db
/private/var/mobile/Library/SpringBoard/IconState.plist
```

`applicationState.db` 경로는 [3][4] 에, `IconState.plist` 경로는 [1] 에 나옵니다. [1] 은 DB 이름을 `applicationstate.db` 로 소문자로 적었고, 관찰한 백업에서는 `applicationState.db` 였습니다 (확인 범위: iOS 27.0). 대소문자가 다른 이름으로 검색해 놓치지 않도록 대소문자를 가리지 않고 찾습니다.

### 근거별 확인 범위

| 근거 | 시험 환경 |
|---|---|
| `applicationState.db` 세 표의 관계, key 이름으로 조인 | 2018년 글, iOS 11.2.1[3] |
| 앱을 정리하면 `applicationState.db` 항목이 지워짐, `IconState.plist` 로 정리한 앱을 가름 | 2019년 글[4] |
| 도구마다 다른 설치 로그 해석 | iOS 15 이미지[1] |
| 백업의 파일·표·키 이름 | 로컬 백업, 암호화 안 함 (확인 범위: iOS 27.0) |

### 로컬 백업에 보이는 것

관찰한 로컬 백업에서는 아래 파일들이 보였습니다. 값은 읽지 않았습니다 (확인 범위: iOS 27.0).

| 도메인 :: 경로 | 관찰한 표·키 |
|---|---|
| `HomeDomain :: Library/FrontBoard/applicationState.db` | `application_identifier_tab(id, application_identifier)`, `key_tab(id, key)`, `kvs(id, application_identifier, key, value)`, `schema(version)` |
| 백업 최상위 `Info.plist` | `Installed Applications`, `Applications` 키 |
| 백업 최상위 `Manifest.plist` | `Applications` 키 |
| `HomeDomain :: Library/SpringBoard/IconState.plist` | `iconLists`, `buttonBar`, `ignored`, `today`, `listUniqueIdentifiers` (list), `displayName`, `defaultDisplayName`, `uniqueIdentifier` (str) |
| `HomeDomain :: Library/SpringBoard/DesiredIconState.plist` | `iconLists`, `dockUtilities`, `buttonBar`, `ignored`, `today`, `listUniqueIdentifiers` (list), `metadata` 아래 `creationDate` |
| `InstallDomain :: Library/MobileInstallation/BackedUpState/SystemAppInstallState.plist`, `BackupSystemAppInstallState.plist` | Apple 기본 앱 번들 ID(`com.apple.mobilesafari`, `com.apple.weather`, `com.apple.AppStore` 등)가 키이고 값은 int |
| `HomeDomain :: Library/Preferences/com.apple.mobile.installation.plist` | `ExtensionDataContainerParentIDUpdateVersion` (int) 하나 |
| `HomeDomain :: Library/Preferences/com.apple.mt.lastLaunch.plist` | `launches` 아래에 번들 ID 가 키로 들어 있음 |
| `HomeDomain :: Library/Preferences/com.apple.siri.sirisuggestions.plist` | `lastAppInstallDate` (datetime), `numAppInstallsToday` (int) 등 |
| `SysContainerDomain-com.apple.lsd :: com.apple.launchservices.appmarketplaces.plist` | `version` (int), `preferredMarketplaces` (list) |
| `SysContainerDomain-com.apple.managedappdistributiond :: distributor-preferences-store.plist` | `doNotShowSheetList` (list) |

`InstallDomain` 의 두 plist 값, `lastLaunch` 의 값, `sirisuggestions` 의 두 키, `appmarketplaces` 가 대체 앱 마켓과 관련된 파일인지는 모두 뜻을 확인하지 못했습니다. `SysSharedContainerDomain-systemgroup.com.apple.mobile.installationhelperlogs` 도메인(항목 5개)도 있었지만 안의 파일 이름은 관찰 메모에 없습니다 (확인 범위: iOS 27.0).

백업 전체 도메인 1,428개 가운데 Apple 기본 영역이 아닌 161개는 관찰 메모에서 이름을 가렸습니다 (확인 범위: iOS 27.0). 백업의 앱 도메인은 `AppDomain-com.apple.AppStore` 처럼 이름에 번들 ID 가 들어가서 설치 앱 후보를 모을 때 쓸 수 있지만, 이 목록이 설치 앱과 정확히 같은지는 확인하지 못했습니다. 백업 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

## 구조

`applicationState.db` 의 네 표는 다음과 같이 이어집니다[3].

| 표 | 칸 | 하는 일 |
|---|---|---|
| `application_identifier_tab` | `id`, `application_identifier` | 번들 ID 를 번호에 연결 |
| `key_tab` | `id`, `key` | key 번호를 key 이름에 연결 |
| `kvs` | `id`, `application_identifier`, `key`, `value` | 앱 번호와 key 번호마다 값을 둠. 앱과 데이터 경로를 이음 |
| `schema` | `version` | 칸 하나만 관찰했고 값의 뜻은 확인하지 못함 (확인 범위: iOS 27.0) |

iOS 11.2.1 기기로 시험한 글은 `kvs` 에 `compatibilityInfo` key 가 있으면 앱 폴더가 있는 설치 앱으로, 없으면 지운 앱으로 보았고, 지운 앱 가운데 일부는 `_UninstallDate` key 에 삭제 시각을 담은 이진 plist 를 남겼지만 모든 앱이 그렇지는 않았다고 적었습니다[3]. `key_tab` 의 번호가 기기나 버전마다 같은지는 원 저자도 확신하지 않았습니다[3]. 그래서 번호를 외워 쓰지 말고 `key_tab` 과 조인해 key 이름으로 거릅니다. `value` 칸에는 이진 plist 가 들어가는 경우가 있어서[3], 값을 풀 때는 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 의 방법을 씁니다.

## 증거로서 의미

**증명하는 것.** `applicationState.db` 에 번들 ID 항목과 컨테이너 경로가 있으면 수집 시점에 그 앱이 기기에 설치되어 있었다는 근거가 됩니다[4]. 다만 지운 앱의 번들 ID 가 `_UninstallDate` 같은 key 와 함께 남은 사례가 있어서[3], 번들 ID 가 있다는 것만으로 설치 상태라고 쓰지 않고 그 앱에 어떤 key 가 달렸는지까지 확인합니다. `IconState.plist` 는 홈 화면에 어떤 항목이 어디 놓였는지를, 백업의 `Info.plist`·`Manifest.plist` 는 백업을 만든 시점의 앱 목록 키를 보여 줍니다(키 이름은 관찰, 확인 범위: iOS 27.0).

**증명하지 못하는 것.** 설치되어 있다는 사실은 앱을 쓴 적이 있다는 뜻이 아니고, 누가 언제 설치했는지도 알려 주지 않습니다. 앱을 정리 (offload) 하면 `applicationState.db` 항목이 지워져서[4], 항목이 없다는 사실만으로는 한 번도 설치한 적이 없다고도, 지웠다고도 말할 수 없습니다. 정리한 앱과 지운 앱을 가르는 절차는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) 에서 다룹니다.

보고서에는 "이 앱을 쓰고 있었다" 대신 "수집 시점의 `applicationState.db` 에 번들 ID `com.example.app` 항목과 데이터 컨테이너 경로가 있다" 처럼 씁니다.

## 시각 해석

이 페이지의 기록은 대부분 시각이 아니라 상태를 담습니다. `applicationState.db` 에서 설치 시각을 읽는 방법은 확인한 자료에 없고, 관찰한 백업에서 시각 형으로 보인 키는 `sirisuggestions` 의 `lastAppInstallDate` (datetime) 와 `DesiredIconState.plist` 의 `metadata`·`creationDate` 정도였습니다 (확인 범위: iOS 27.0). 두 키 모두 이름은 설치 시각이나 파일을 만든 시각을 떠올리게 하지만 뜻을 확인하지 못해서, 다른 기록과 맞기 전에는 설치 시각으로 쓰지 않습니다.

설치와 제거 시각은 Mobile Installation 로그[1]와 [바이옴](biome/index.md) 의 설치 기록에서 찾고, 시각 기준은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 확인합니다.

## 함정과 한계

**도구마다 목록이 다릅니다.** iOS 15 이미지 비교에서 Mobile Installation 로그를 읽을 때 어떤 도구는 설치에 성공한 항목만, 어떤 도구는 설치와 제거 항목을 모두, iLEAPP 는 재부팅과 관련된 항목까지 보았습니다[1]. 도구 둘이 다른 앱 목록을 내면 어느 파일의 어느 항목에서 나온 결과인지부터 확인합니다.

**로그 경로와 형식은 따로 확인합니다.** Mobile Installation 로그의 파일 경로와 줄 형식, 보관 기간은 이 페이지의 자료로 확인하지 못했습니다. 로그를 인용할 때는 검체에서 찾은 실제 경로를 함께 적습니다.

**정리한 앱은 목록에서 빠질 수 있습니다.** 정리한 앱은 `applicationState.db` 에서 항목이 지워지고[4], `IconState.plist` 로 정리한 앱과 완전히 설치된 앱을 가릅니다[4]. `applicationState.db` 한 곳만 보고 설치 앱 수를 보고하지 않습니다.

**이름만 보고 해석하지 않습니다.** `SystemAppInstallState.plist` 처럼 이름에 설치 상태가 들어간 파일도 값의 뜻은 확인하지 못했습니다 (확인 범위: iOS 27.0). Apple 기본 앱의 설치 여부로 옮겨 적기 전에 다른 기록과 맞춰 봅니다.

**지우기와 조작.** 앱을 지우거나 정리하면 이 페이지의 기록에서는 흔적이 줄어들지만, 번들 ID 는 사용 기록과 구매 기록에 남을 수 있습니다. 그 흐름은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에서 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시이고 특정 검체에서 나온 값이 아닙니다. `kvs.value` 칸의 값을 헥스로 뽑았을 때 이진 plist 라면 첫 8바이트가 `bplist00` 입니다.

```
00000000  62 70 6C 69 73 74 30 30                          bplist00
```

이 머리글이 보이면 값을 따로 파일로 저장해 plist 로 풉니다. `IconState.plist` 도 이진 plist 라면 같은 머리글로 시작합니다.

### SQL 로 앱과 key 이름 잇기

사본에서 실행합니다. 먼저 이 검체의 key 이름을 확인합니다.

```sql
SELECT id, key FROM key_tab ORDER BY id;
```

그다음 번호 대신 이름으로 조인해 앱마다 어떤 key 가 있는지 봅니다.

```sql
SELECT a.application_identifier, k.key, length(v.value) AS value_len
FROM kvs v
JOIN application_identifier_tab a ON a.id = v.application_identifier
JOIN key_tab k ON k.id = v.key
ORDER BY a.application_identifier, k.key;
```

### 공개 도구로 한 번

MVT 의 Applications 모듈은 백업에서는 `Info.plist`, 파일 시스템 덤프에서는 `iTunesMetadata.plist` 로 설치 앱과 설치 출처를 뽑고, App Store 가 아닌 곳에서 온 앱을 표시합니다[2]. 일반 백업과 전체 덤프 둘 다 됩니다[2]. iLEAPP 는 Mobile Installation 로그를 읽습니다[1]. 도구 목록은 위 SQL 결과와 백업 `Info.plist` 의 `Installed Applications` 목록과 맞춰 보고, 어긋나는 번들 ID 를 따로 적습니다. 도구 검증은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

설치 여부를 확인한 다음에는 쓴 기록을 찾습니다. 앱을 앞화면에 띄운 기록은 [KnowledgeC](knowledgec/index.md) 와 [바이옴](biome/index.md), 사용 시간 합계는 [화면 사용 시간](screen-time.md), 통신량은 [앱별 데이터 사용량](../network/data-usage.md) 에서 봅니다. 앱을 어디서 받았는지와 구매 기록은 [앱 스토어 기록](app-store.md), 앱 번들 안의 정보는 [앱 번들 정보](../embedded-metadata/app-bundle.md), 관리 기기라면 [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) 도 함께 봅니다. 처음 보는 앱이나 지운 앱을 다루는 절차는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md), 수상한 앱을 가리는 흐름은 [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md) 에 있습니다.

## 실습

공개 검체(NIST CFReDS 등의 iOS 이미지)로 다음 질문을 풀어 봅니다.

1. `applicationState.db` 의 `key_tab` 에 key 가 몇 개 있고, 이름은 무엇입니까?
2. `application_identifier_tab` 의 번들 ID 가운데 `com.apple.` 로 시작하지 않는 번들 ID 는 몇 개입니까?
3. 그 번들 ID 가운데 `IconState.plist` 에 나오지 않는 것이 있습니까? 있다면 정리한 앱인지, 홈 화면에 두지 않은 앱인지 어떻게 가르겠습니까?
4. 로컬 백업이 함께 있다면 `Info.plist` 의 `Installed Applications` 목록과 `applicationState.db` 목록은 같습니까?
5. 두 가지 공개 도구로 설치 앱 목록을 뽑았을 때 결과가 어긋나는 번들 ID 는 무엇이고, 각각 어느 파일에서 나왔습니까?

## 참고 문헌

- [1] iOS 15 Image Forensics Analysis and Tools Comparison - Processing details and general device information — blog.digital-forensics.it (2023-09) — https://blog.digital-forensics.it/2023/09/ios-15-image-forensics-analysis-and.html
- [2] Records extracted by mvt-ios — Mobile Verification Toolkit — https://docs.mvt.re/en/latest/ios/records/
- [3] Identifying installed and uninstalled apps in iOS — Alexis Brignoni (2018-12) — https://abrignoni.blogspot.com/2018/12/identifying-installed-and-uninstalled.html
- [4] iOS - Tracking Traces of Deleted Applications — D20 Forensics (2019-09) — https://blog.d204n6.com/2019/09/ios-tracking-traces-of-deleted.html
