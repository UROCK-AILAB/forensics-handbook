---
title: "앱 스토어 기록"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 420
---

# 앱 스토어 기록 (App Store)

## 한 줄 요약

앱 스토어 (App Store) 기록은 앱 번들 폴더의 `iTunesMetadata.plist`·`BundleMetadata.plist` 와 App Store 서비스가 쓰는 SQLite DB·설정 plist 에 흩어져 있고, 앱이 App Store 에서 왔는지, 어떤 번들 ID 와 상품 식별자가 스토어 서비스 기록에 올라 있는지를 보여 줍니다.

## 무엇을 기록하나 · 왜 생기나

앱 번들 폴더에는 `iTunesMetadata.plist` 와 `BundleMetadata.plist` 가 있습니다[1]. MVT 는 `iTunesMetadata.plist` 로 앱의 설치 출처를 보고 App Store 가 아닌 곳에서 온 앱을 따로 표시합니다[2]. 이 파일에 내려받은 시각, 버전, 내려받은 Apple ID 가 들어 있다는 설명도 있지만 원문과 키 이름을 확인하지 못해서 이 페이지에서는 다루지 않습니다.

앱이 충돌하면 충돌 보고서 본문의 `storeInfo` 에 `itemID` 가 들어가고, 이 값은 스토어에서 앱을 가리키는 Apple 식별자입니다[3]. 그래서 충돌 보고서 한 건으로도 번들 ID 와 스토어 식별자를 이을 수 있고, 보고서 구조는 [충돌·진단 기록](diagnostics.md) 에서 다룹니다.

구매 기록 DB 인 `DAAP.sqlitedb`(iOS 12 에서 추가, 구매한 앱을 Apple ID·가족 구매까지 포함해 기록)[4]와 여러 기기에 걸친 구매를 담는 `storeUser.db`[5]는 지운 앱을 찾는 절차에서 주로 쓰여서, 경로와 해석은 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) 에서 다룹니다.

## 위치와 버전별 차이

### 확인한 범위

| 근거 | 범위 |
|---|---|
| 번들 폴더의 `iTunesMetadata.plist`·`BundleMetadata.plist` | iOS 15 이미지로 도구를 비교한 글[1] |
| MVT 의 설치 출처 판단 | 일반 백업과 전체 덤프[2] |
| 충돌 보고서의 `storeInfo.itemID` | iOS 15 부터 쓰는 JSON 형식 충돌 보고서[3] |
| App Store 서비스 DB·plist 의 이름과 칸 | 로컬 백업, 암호화 안 함 |

MVT 는 백업에서는 `Info.plist`, 파일 시스템 덤프에서는 `iTunesMetadata.plist` 를 쓴다고 나눠 적었고[2], 관찰한 로컬 백업의 메모에도 `iTunesMetadata.plist`·`BundleMetadata.plist` 는 나오지 않았습니다. 그래서 번들 폴더의 메타데이터 plist 는 파일 시스템 추출에서 찾습니다. 수집 방식 차이는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

### 로컬 백업에 보이는 DB

관찰한 로컬 백업의 `HomeDomain :: Library/com.apple.itunesstored/` 아래에는 DB 가 네 개 있었습니다. 첫 DB 이름의 `#` 은 관찰 메모에서 숫자를 가린 자리입니다.

| DB | 표(주요 칸) |
|---|---|
| `itunesstored#.sqlitedb` | `ZINAPPREVIEWREQUEST`(`ZRATED`, `ZDATE`, `ZBUNDLEIDENTIFIER`, `ZBUNDLEVERSION`), `ZMICROPAYMENTBASE`(`ZPRODUCTIDENTIFIER`, `ZTRANSACTIONIDENTIFIER`, `ZORIGINALTRANSACTIONIDENTIFIER`, `ZPURCHASEDATE`, `ZORIGINALPURCHASEDATE`, `ZINSERTDATE`, `ZQUANTITY`, `ZSTATE`, `ZUSERDSID`, `ZAPPLICATIONUSERNAME`, `ZASKPERMISSIONREQUESTIDENTIFIER`, `ZRECEIPTDATA` 등), `ZMICROPAYMENTCLIENT`(`ZIDENTIFIER`, `ZBUNDLEVERSION`, `ZSTOREIDENTIFIER`, `ZVENDORIDENTIFIER`, `ZLASTQUEUECHECKDATE`, `ZSANDBOXED` 등), `ZMICROPAYMENTDOWNLOAD`(`ZDOWNLOADID`, `ZLOCALURL`, `ZREMOTEURL`, `ZSTATE`, `ZPAYMENT` 등), `Z_METADATA`, `Z_MODELCACHE`, `Z_PRIMARYKEY` |
| `itunesstored_private.sqlitedb` | `ZCANCELEDDOWNLOAD`(`ZACCOUNTIDENTIFIER`, `ZQUEUEIDENTIFIER`, `ZCANCELURL`), `ZPUSHNOTIFICATION`(`ZCLIENT`, `ZUSERINFO`), `ZPUSHNOTIFICATIONCLIENT`(`ZCLIENTIDENTIFIER`), `ZPUSHNOTIFICATIONENVIRONMENT`(`ZLASTACCOUNTIDENTIFIER`, `ZENVIRONMENTNAME`, `ZTOKENDATA`), `ZRINGTONEPURCHASE`(`ZADAMID`, `ZTRANSACTIONID` 등) |
| `kvs.sqlitedb` | `kvs_value`(`pid`, `domain`, `key`, `value`) |
| `purchase_intents.sqlitedb` | `purchase_intents_table`(`product_identifier`, `app_bundle_id`, `timestamp`, `pid`, `product_name`, `app_name`), `install_attribution_params_table`(`app_adam_id`, `ad_network_id`, `campaign_id`, `impression_id`, `timestamp`, `attribution_signature`, `local_timestamp`), `install_attribution_pingback_table`(`app_adam_id`, `ad_network_id`, `campaign_id`, `transaction_id`, `attribution_signature`, `pingback_url`, `pending`, `retry_count`, `local_timestamp`) |

`ZMICROPAYMENT…` 표가 앱 내 구입 (in-app purchase) 기록인지, `ZINAPPREVIEWREQUEST` 가 앱 평가 요청 기록인지는 이름에서 짐작할 뿐 확인하지 못했습니다. `Z` 로 시작하는 표·칸과 `Z_METADATA`·`Z_PRIMARYKEY` 는 Core Data 가 만드는 저장소와 이름 모양이 같지만, 이것도 문서로 확인한 사실은 아닙니다.

### 로컬 백업에 보이는 설정 plist

값은 읽지 않고 키 이름과 형만 보았습니다.

| 도메인 :: 경로 | 관찰한 키 |
|---|---|
| `HomeDomain :: Library/Preferences/com.apple.appstored.plist` | `LastUpdatesCheck`, `LastUpdatesPerform`, `LastAutoUpdateCompletion`, `LastOSInstallDate`, `UpdateCleanupTime`, `OffloadingGracePeriodStartDate`, `AppUsageLaunchesIntervalStartDate`, `AppUsageBiomeStartDate`, `AppUsageNextPostTargetDate`, `AppUsageFlushTargetDate`, `LastWeeklyAnalyticsPostDate` (모두 datetime), `LastOSBuildVersion`·`osVersionStringKey` (str), `ArcadeSubscriptionState` (str), `ArcadeDeviceID`·`ODPDeviceID` (str), `RestoreInstallsFailedWithCodeSigError`(사전), `PerformedPostRestoreUpdate` (bool), `ManageSubsOnDeleteBlacklist` (list) 등 |
| `HomeDomain :: Library/Preferences/com.apple.AppStore.plist` | `lastBootstrapDate` (float), `lastBootstrapTimeZone` (str), `mostRecentTabIdentifier` (str), `inAppMessagesLastArcadeTabVisitDate` (datetime), `AutoPlayVideoSetting` (str) 등 |
| `AppDomain-com.apple.AppStore :: Library/Preferences/com.apple.ap.AppStore.plist` | `AppStoreSLPContentSnapshot` (bytes) |
| `SysContainerDomain-com.apple.appstored :: Library/katana-subscription-cache.plist` | `allInfo` |

`AppDomain-com.apple.AppStore` 도메인에는 항목이 18개, `SysContainerDomain-com.apple.appstored` 에는 4개 있었고, `AppDomainPlugin-com.apple.AppStoreDaemon.ASDAskPermissionExtension`, `…ASDUserNotificationExtension`, `…AppStoreEventServiceExtension`, `AppDomain-com.apple.AskPermissionUI` 같은 관련 도메인도 보였습니다. `com.apple.appstored.plist` 키 이름은 업데이트 확인, OS 설치, 앱 정리 유예 같은 사건을 떠올리게 하지만 어느 키의 뜻도 확인하지 못했습니다. 백업 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md), plist 는 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

## 구조

`.sqlitedb` 확장자를 쓰지만 네 DB 모두 표와 칸이 있는 SQLite DB 이고, 여는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 와 같습니다. 번들 ID 가 들어가는 칸은 `ZINAPPREVIEWREQUEST.ZBUNDLEIDENTIFIER`, `ZMICROPAYMENTCLIENT.ZIDENTIFIER`, `purchase_intents_table.app_bundle_id` 처럼 이름으로 드러나는 곳이 있어서, 번들 ID 하나를 두고 네 DB 를 가로질러 찾을 수 있습니다. 칸 이름이 뜻하는 바는 위에서 적은 대로 확인하지 못했으니, 번들 ID 가 나온 표와 칸을 그대로 기록해 둡니다.

## 증거로서 의미

**증명하는 것.** 파일 시스템 추출에서는 `iTunesMetadata.plist` 로 앱의 설치 출처를 볼 수 있고, MVT 는 App Store 가 아닌 곳에서 온 앱을 따로 표시합니다[2]. 충돌 보고서의 `itemID` 는 그 앱이 스토어의 어느 항목인지를 가리킵니다[3]. 백업의 App Store 서비스 DB 에 어떤 번들 ID 나 상품 식별자가 있다는 사실은, 그 번들 ID 가 이 기기의 App Store 서비스 기록에 올라 있다는 뜻입니다.

**증명하지 못하는 것.** 각 칸의 뜻을 확인하지 못해서, `itunesstored` DB 의 행 하나를 "이 사람이 이 시각에 결제했다" 로 옮길 수 없습니다. 구매 기록은 계정 단위로 여러 기기에 걸칠 수 있어서[5] 이 기기에 설치했다는 증명도 아닙니다. 설치 여부는 [설치된 앱](installed-apps.md) 에서 따로 확인합니다.

보고서에는 "이 앱을 샀다" 대신 "`purchase_intents.sqlitedb` 의 `purchase_intents_table` 에 `app_bundle_id` 가 `com.example.app` 인 행이 있고, `timestamp` 칸 원래 값은 이것이다" 처럼 표·칸·원래 값을 함께 씁니다.

## 시각 해석

DB 에는 `ZDATE`, `ZPURCHASEDATE`, `ZORIGINALPURCHASEDATE`, `ZINSERTDATE`, `ZLASTQUEUECHECKDATE`, `timestamp`, `local_timestamp` 같은 시각 칸이 있지만 기준점과 단위는 확인하지 못했습니다. `install_attribution_*` 표에는 `timestamp` 와 `local_timestamp` 가 나란히 있는데, 두 칸이 어떻게 다른지도 확인하지 못했습니다. 값을 풀 때는 유닉스 시각과 Mac 절대 시각(2001-01-01 기준)으로 각각 바꿔 보고, 수집일이나 다른 기록과 맞는 쪽을 근거와 함께 적습니다.

설정 plist 의 `datetime` 형은 plist 날짜 형식이라 도구가 날짜로 풀어 주지만, `AppStore.plist` 의 `lastBootstrapDate` 는 `float` 형이라 기준점을 따로 확인해야 합니다. 같은 파일의 `lastBootstrapTimeZone` (str) 은 시간대와 관련된 값으로 보이지만 뜻은 확인하지 못했습니다. 시각 기준 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md), 기기 시간대는 [시간대와 시각 설정](../system-account/time-zone.md) 에서 다룹니다.

## 함정과 한계

**이름으로 뜻을 정하지 않습니다.** `ZMICROPAYMENT…`, `ZINAPPREVIEWREQUEST`, `install_attribution_*` 처럼 이름이 뜻을 말해 주는 것 같은 표도 문서로 확인한 뜻이 없습니다. 보고서에는 표와 칸 이름을 그대로 쓰고, 해석을 붙이려면 같은 검체에서 알고 있는 사건(예: 조사 중 직접 한 구매)과 맞춰 본 결과를 근거로 씁니다.

**수집 방식에 따라 보이는 것이 다릅니다.** 번들 폴더의 `iTunesMetadata.plist` 는 파일 시스템 추출에서 보고, 백업에서는 `Info.plist` 와 `itunesstored` DB 를 봅니다[2]. 한 방식에서 없다고 다른 방식에도 없다고 쓰지 않습니다.

**계정과 기기를 나눕니다.** 스토어 기록은 Apple 계정에 묶여 있어서, 가족 구매나 같은 계정의 다른 기기에서 생긴 기록이 섞일 수 있습니다[4][5]. 계정 정보는 [애플 계정](../system-account/apple-account.md) 에서 확인합니다.

**지우기와 조작.** 앱을 지워도 구매 기록은 남는다는 보고가 있어서[5], 앱이 없는 기기에서도 App Store 기록으로 번들 ID 를 찾을 수 있습니다. 앱 삭제를 증거 인멸로 볼지는 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름으로 따집니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시이고 특정 검체에서 나온 값이 아닙니다. 확장자가 `.sqlitedb` 여도 첫 16바이트가 SQLite 머리글이면 SQLite 도구로 엽니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

백업 안에서는 파일이 해시 이름으로 저장되어 확장자가 없어서, 이 머리글로 SQLite 파일을 먼저 가려낸 뒤 `Manifest.db` 의 경로와 맞춥니다.

### SQL 로 번들 ID 찾기

사본에서 실행합니다. 시각 칸은 기준을 모르니 원래 값과, 두 가지 기준으로 바꾼 값을 나란히 뽑아 비교합니다.

```sql
-- purchase_intents.sqlitedb
SELECT app_bundle_id, product_identifier, timestamp,
       datetime(timestamp, 'unixepoch')             AS if_unix,
       datetime(timestamp + 978307200, 'unixepoch') AS if_mac_absolute
FROM purchase_intents_table
ORDER BY timestamp;

-- itunesstored#.sqlitedb
SELECT ZBUNDLEIDENTIFIER, ZBUNDLEVERSION, ZDATE
FROM ZINAPPREVIEWREQUEST
ORDER BY ZDATE;
```

`978307200` 은 1970-01-01 과 2001-01-01 사이의 초입니다. 두 결과 가운데 어느 쪽이 맞는지는 이 SQL 로 정해지지 않고, 다른 기록과 맞춰 봐야 합니다.

### 공개 도구로 한 번

MVT 의 Applications 모듈은 설치 앱과 설치 출처를 뽑아 App Store 가 아닌 곳에서 온 앱을 표시하고, 일반 백업과 전체 덤프 둘 다 됩니다[2]. 결과에 표시된 앱은 위 SQL 로 `itunesstored` DB 에 같은 번들 ID 가 있는지 확인하고, 도구 결과를 그대로 옮기지 않습니다. 도구 검증은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

지금 설치 상태는 [설치된 앱](installed-apps.md), 번들 안의 정보는 [앱 번들 정보](../embedded-metadata/app-bundle.md), 스토어 식별자가 들어간 충돌 보고서는 [충돌·진단 기록](diagnostics.md) 에서 봅니다. 계정은 [애플 계정](../system-account/apple-account.md), 앱을 쓴 기록은 [KnowledgeC](knowledgec/index.md) 와 [바이옴](biome/index.md) 과 맞춥니다. App Store 가 아닌 곳에서 온 앱을 점검하는 흐름은 [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md) 과 [악성 코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md) 에 있습니다.

## 실습

공개 검체(NIST CFReDS 등의 iOS 이미지)로 다음 질문을 풀어 봅니다.

1. `com.apple.itunesstored` 폴더에 DB 가 몇 개 있고, 각 DB 의 표 이름은 이 페이지의 표와 같습니까?
2. `purchase_intents_table` 과 `ZINAPPREVIEWREQUEST` 에 나오는 번들 ID 가운데 수집 시점에 설치되어 있지 않은 앱이 있습니까?
3. `timestamp` 칸을 유닉스 시각과 Mac 절대 시각으로 각각 바꾸면 어느 쪽이 검체의 사용 기간 안에 들어옵니까?
4. 파일 시스템 추출이라면 `iTunesMetadata.plist` 로 본 설치 출처가 App Store 가 아닌 앱이 있습니까? 있다면 그 번들 ID 는 무엇입니까?
5. 충돌 보고서가 있다면 `storeInfo.itemID` 가 있는 보고서의 번들 ID 는 무엇입니까?

## 참고 문헌

- [1] iOS 15 Image Forensics Analysis and Tools Comparison - Processing details and general device information — blog.digital-forensics.it (2023-09) — https://blog.digital-forensics.it/2023/09/ios-15-image-forensics-analysis-and.html
- [2] Records extracted by mvt-ios — Mobile Verification Toolkit — https://docs.mvt.re/en/latest/ios/records/
- [3] Interpreting the JSON format of a crash report — Apple Developer Documentation — https://developer.apple.com/tutorials/data/documentation/xcode/interpreting-the-json-format-of-a-crash-report.md
- [4] iOS - Tracking Traces of Deleted Applications — D20 Forensics (2019-09) — https://blog.d204n6.com/2019/09/ios-tracking-traces-of-deleted.html
- [5] Has the user ever used the XYZ application? aka traces of application execution on mobile devices — digital-forensics.it (2023-12) — https://blog.digital-forensics.it/2023/12/has-user-ever-used-xyz-application-aka.html
