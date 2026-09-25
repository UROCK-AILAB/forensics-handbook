---
title: "방문 기록"
parent: "사파리"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 730
---

# 방문 기록 (History.db)

## 한 줄 요약

사파리는 방문 기록을 History.db 에 남기고 URL 한 개를 `history_items` 의 한 행으로, 방문 한 번을 `history_visits` 의 한 행으로 적으며, `origin` 칸으로 이 기기의 방문과 iCloud 로 넘어온 다른 기기의 방문을 가를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 사파리로 페이지를 열 때마다 방문 한 번이 `history_visits` 에 한 행으로 쌓이고, 같은 URL 은 `history_items` 의 한 행에 모여 방문 횟수(`visit_count`)가 늘어납니다[1]. 방문 행에는 방문 시각, 페이지 제목, 넘겨주기(redirect) 앞뒤의 방문이 함께 남고, 공개 자료들도 이 DB 에서 URL, 방문 시각, 방문 횟수, 페이지 제목, 넘어온 출처를 뽑습니다[1][3].

iCloud 로 방문 기록을 맞추는 설정이면 다른 기기에서 본 페이지도 이 DB 에 들어옵니다. `origin` 칸이 0 이면 이 기기에서 방문한 것이고 1 이면 iCloud 로 동기화된 다른 기기의 방문입니다[1]. 개인 정보 보호 모드에서 방문한 사이트는 History.db 에 저장되지 않는데[2], 그 모드의 흔적은 [개인 정보 보호 브라우징 (Private Browsing)](private-browsing.md)에서 따로 다룹니다.

## 위치와 버전별 차이

기기 경로는 `/private/var/mobile/Library/Safari/History.db` 이고[2][3], iLEAPP 는 iOS 17 이후를 위해 프로필별 DB `Safari/Profiles/*/History.db` 도 찾습니다[1]. 이때 기본 DB 는 "Default" 로, 프로필 DB 는 프로필 폴더 이름으로 표시합니다[1]. 프로필 기능이 정확히 iOS 17 에 생겼는지는 이번에 연 자료로 확인하지 못했습니다.

| 구분 | 위치 | 비고 |
|---|---|---|
| 기본 방문 기록 | `/private/var/mobile/Library/Safari/History.db` | iOS 15 이미지에서 확인한 경로입니다[2] |
| 프로필별 방문 기록 | `Safari/Profiles/*/History.db` | iLEAPP 가 iOS 17 이후용으로 찾는 경로입니다[1] |
| 로컬 백업 | 관찰한 백업(암호화 안 함)에는 없음 | Apple 은 웹 사이트 기록이 암호화한 백업에만 들어간다고 안내합니다[4] |

관찰한 백업은 암호화하지 않은 백업이었고 History.db 가 목록에 없었습니다(확인 범위: iPhone 13 mini, iOS 27.0). Apple 지원 문서는 저장된 암호, Wi-Fi 설정, 건강 데이터, 통화 기록과 함께 "웹 사이트 기록(Website history)" 을 암호화한 백업에만 들어가는 항목으로 듭니다[4]. 그래서 백업으로 방문 기록을 보려면 백업 암호를 건 백업이 필요하고, 백업 형식은 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)에서 다룹니다.

## 구조

| 표 | 한 행의 뜻 | 주요 칸(iLEAPP 가 읽는 것)[1] |
|---|---|---|
| `history_visits` | 방문 한 번 | `id`, `visit_time`, `title`, `redirect_source`, `redirect_destination`, `origin`, `history_item` |
| `history_items` | URL 한 개 | `url`, `visit_count` |

`history_visits.history_item` 은 `history_items.id` 를 가리키고, iLEAPP 도 이 조건으로 두 표를 잇습니다[1]. `redirect_source` 와 `redirect_destination` 은 URL 이 아니라 다른 방문의 `id` 를 가리키고, iLEAPP 는 이 id 를 URL 로 바꿔 보여 줍니다[1]. visit id 는 DB 하나 안에서만 유일해서[1], 기본 DB 와 프로필 DB 를 합칠 때 id 가 겹쳐도 같은 방문이 아닙니다. 삭제 흔적을 담는 표나 iCloud 동기화용 표가 따로 있는지는 이번에 연 자료로 확인하지 못했습니다.

방문 기록과 이어진 이름의 설정 파일도 백업에 남습니다(확인 범위: iPhone 13 mini, iOS 27.0).

| 위치 | 키 |
|---|---|
| AppDomain-com.apple.mobilesafari `Library/Preferences/com.apple.Safari.History.plist` | `CloudKitAccountInfoCache`(dict), `CKPerBootTasks`(list), `CKStartupTime`(int) |
| AppDomain-com.apple.mobilesafari `Library/Preferences/com.apple.mobilesafari.plist` | `didMigrateHistoryToCoreSpotlightAfterUpgrade`(bool), `numberOfHistoryDonationAttempts`(int), `LastCloudHistoryConfigurationUpdateTime`(float), `RecentWebSearches`(list), `LastActiveProfile`(str) |
| HomeDomain `Library/Preferences/com.apple.SafariCloudHistoryPushAgent.plist` | `AcknowledgedPushNotifications`(bool) |
| HomeDomain `Library/Application Support/CloudDocs/session/containers/` | `com.apple.SafariShared.History.plist`, `iCloud.com.apple.mobilesafari.plist`(둘 다 `com.apple.mobilesafari` 아래 `BRContainer*` 키) |

각 키가 무엇을 뜻하는지는 확인하지 못했고, 이름이 방문 기록·iCloud 동기화·프로필과 닮았다는 정도만 말할 수 있습니다. plist 를 읽는 법은 [설정 값 (Preferences)](../../system-account/preferences.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** `history_visits` 에 행이 있으면 그 시각에 그 URL 을 연 방문 기록이 사파리에 있다는 사실을 보여 주고, `origin` 이 0 이면 이 기기에서 연 기록입니다[1]. `redirect_source` 와 `redirect_destination` 을 따라가면 넘겨주기 앞뒤의 방문을 이어 볼 수 있지만[1], 앞쪽 방문을 사용자가 직접 주소를 쳐서 열었는지까지는 알려 주지 않습니다.

**증명하지 못하는 것.** 방문 행은 페이지를 불러온 기록일 뿐, 사용자가 그 페이지를 읽었는지나 화면에 얼마나 오래 띄웠는지는 알려 주지 않습니다. `origin` 이 1 인 행은 같은 계정의 다른 기기에서 일어난 방문이라서[1] 이 기기를 쓴 사람의 행위로 옮겨 쓰면 안 됩니다. 기록이 없다고 방문하지 않았다고 말할 수도 없는데, 개인 정보 보호 모드 방문은 처음부터 저장되지 않고[2] 사용자가 기록을 지웠을 수도 있기 때문입니다.

보고서에는 "이 기기의 사파리 방문 기록에 이 시각 이 URL 을 연 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

`visit_time` 은 방문이 일어난 시각입니다. iLEAPP 는 값이 978307200 보다 크면 UNIX 시각으로, 작으면 Apple 절대 시각(2001-01-01 기준)으로 보고 978307200 을 더해 바꿉니다[1]. 978307200 초는 1970-01-01 과 2001-01-01 사이의 차이입니다[1]. 같은 도구의 탭 코드는 iOS 18 이하를 Apple 절대 시각, iOS 26 이상을 UNIX 시각으로 적지만[5], History.db 가 어느 버전부터 바뀌었는지는 확인하지 못했습니다. 그래서 값의 자릿수를 먼저 보고 기준을 고르며, 두 기준을 읽는 법은 [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

## 함정과 한계

- 암호화하지 않은 백업에는 History.db 가 들어가지 않습니다[4]. 이런 백업만 있으면 아래 교차 검증 절의 다른 DB 에서 도메인 흔적을 찾지만, 그 DB 들이 방문 기록을 대신한다고 볼 근거는 확인하지 못했습니다.
- 프로필을 쓰는 기기에서는 기본 DB 만 열면 프로필의 방문이 빠집니다[1].
- 사용자가 사파리에서 기록을 하나씩 지워도 바이옴 SEGB 파일의 같은 기록은 곧바로 지워지지 않았고, "전체 삭제" 를 하면 SEGB 파일 안의 각 protobuf 가 그 자리에서 0x00 으로 덮어 써졌습니다(iOS 16 시험)[6]. 기록을 지운 흔적을 찾을 때는 이 차이를 함께 봅니다.
- 바이옴 `_DKEvent.Safari.History` 의 시각은 History.db 기록보다 몇 초 늦게 찍혔습니다(iOS 16 시험)[6]. 두 기록을 맞출 때는 이 몇 초 차이를 감안하고, 다른 버전에서는 검체로 다시 확인합니다.

## 직접 분석해 보기

sqlite3 로 WAL 을 함께 둔 사본을 엽니다. 먼저 `PRAGMA table_info(history_visits);` 와 `PRAGMA table_info(history_items);` 로 검체의 칸 목록이 아래 질의와 맞는지 봅니다. 아래 질의는 iLEAPP 와 같은 조건으로 두 표를 잇고, 같은 규칙으로 시각을 바꿉니다[1].

```sql
SELECT v.id, v.title, i.url, i.visit_count, v.origin,
       v.redirect_source, v.redirect_destination,
       datetime(CASE WHEN v.visit_time > 978307200
                     THEN v.visit_time
                     ELSE v.visit_time + 978307200 END, 'unixepoch') AS visit_utc
FROM history_visits v
LEFT JOIN history_items i ON i.id = v.history_item
ORDER BY v.visit_time;
```

넘겨주기 사슬을 보려면 `redirect_source` 가 가리키는 `id` 의 행을 같은 표에서 다시 찾아 붙입니다. 공개 도구로는 iLEAPP 의 사파리 방문 기록 모듈이 기본 DB 와 프로필 DB 를 함께 찾아 한 표로 보여 주므로[1], 직접 뽑은 결과와 행 수·시각을 맞춰 봅니다. SQLite 파일을 여는 바탕은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

> 그림 자리: `history_visits` 한 행이 `history_items` 와 `redirect_source` 로 다른 방문 행을 가리키는 관계

## 교차 검증

지금 열려 있거나 닫은 탭은 [탭과 세션 (Tabs)](tabs.md)에서, 저장해 둔 주소는 [북마크와 읽기 목록 (Bookmarks·Reading List)](bookmarks-reading-list.md)에서 맞춰 봅니다. 바이옴의 사파리 스트림은 [바이옴 (Biome)](../../app-usage/biome/index.md)에서 다룹니다.

History.db 가 없는 암호화 안 한 백업에서도 아래 DB 는 보였습니다(확인 범위: iPhone 13 mini, iOS 27.0). 모두 AppDomain-com.apple.mobilesafari 아래이고 PerSitePreferences.db 만 AppDomainGroup-group.com.apple.safari 아래에 있으며, 각 칸의 시각 기준과 뜻은 확인하지 못했습니다.

| 파일 | 표(칸) |
|---|---|
| `Library/Safari/IgnoredSiriSuggestedSites.db` | `ignored_siri_suggested_sites`(`id`, `siriSuggestedSiteURL`, `query`, `profile`, `timestamp`, `visitedURL`, `ignoreCount`) |
| `Library/Metadata Cache/LPLinkMetadata.db` | `page_url`(`url`, `uuid`, `last_fetch_date`, `last_fetch_did_succeed`, `metadata_has_image`), `uuid_info`(`uuid`, `timestamp`) |
| `Library/Safari/FrequentlyVisitedSitesBannedURLStore.plist` | 키 `BannedURLStrings`(list) |
| `Library/WebKit/WebsiteData/ResourceLoadStatistics/observations.db` | `ObservedDomains`(`registrableDomain`, `lastSeen`, `hadUserInteraction`, `mostRecentUserInteractionTime` 등 13칸), `OperatingDates`(`year`, `month`, `monthDay`), 그 밖에 도메인 관계 표 10여 개 |
| `Library/Safari/ContentBlockerStatistics.db` | `BlockedResources`(`firstPartyDomainID`, `thirdPartyDomainID`, `lastSeen`), `FirstPartyDomains`(`firstPartyDomainID`, `domain`), `ThirdPartyDomains`(`thirdPartyDomainID`, `domain`) |
| `Library/WebKit/WebsiteData/EnhancedSecurity/EnhancedSecuritySites.db` | `sites`(`site`, `enhanced_security_state`, `last_modified`) |
| `Library/Safari/PerSitePreferences.db` | `preference_values`(`id`, `domain`, `preference`, `preference_value`, `timestamp`, `sync_data`, `record_name`), `default_preferences`, `deleted_cloudkit_records` |
| `Library/WebKit/WebsiteData/Default/.../LocalStorage/localstorage.sqlite` | `ItemTable`(`key`, `value`) |

이 DB 들에서 도메인 이름을 찾으면 그 도메인과 사파리가 어떤 식으로든 닿은 흔적이라고 말할 수 있지만, 방문 시각이나 방문한 URL 까지 알려 준다고 확인한 자료는 없습니다. 조사 흐름은 [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md)과 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)를 따릅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 15 이후 파일 시스템 검체로 아래를 풀어 봅니다.

1. `history_visits` 에서 `origin` 이 0 인 행과 1 인 행을 세고, 1 인 행의 URL 이 이 기기의 탭 DB 에도 있는지 찾아봅니다.
2. `visit_time` 값의 자릿수를 보고 UNIX 시각인지 Apple 절대 시각인지 판단한 뒤, 바꾼 시각이 검체의 수집 시각보다 앞인지 확인합니다.
3. `redirect_source` 가 채워진 방문을 골라 넘겨주기 전의 URL 을 찾아봅니다.
4. `Safari/Profiles/` 아래에 History.db 가 더 있는지 보고, 있으면 기본 DB 와 같은 URL 이 겹치는지 비교합니다.

## 참고 문헌

1. iLEAPP `scripts/artifacts/safariHistory.py` (abrignoni/iLEAPP, main) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/safariHistory.py
2. iOS 15 Image Forensics Analysis and Tools Comparison - Native Apps (blog.digital-forensics.it, 2023-10) — https://blog.digital-forensics.it/2023/10/ios-15-image-forensics-analysis-and.html
3. Forensafe, iOS Safari Browser — https://forensafe.com/blogs/iOSSafari.html
4. Apple 지원, "About encrypted backups on your iPhone, iPad, or iPod touch" — https://support.apple.com/en-us/108353
5. iLEAPP `scripts/artifacts/safariTabs.py` (abrignoni/iLEAPP, main) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/safariTabs.py
6. D20 Forensics, "iOS 16 - Breaking Down the Biomes (Part 4) - Surfin' with Safari" (2022-09-28) — https://blog.d204n6.com/2022/09/ios-16-breaking-down-biomes-part-4.html
