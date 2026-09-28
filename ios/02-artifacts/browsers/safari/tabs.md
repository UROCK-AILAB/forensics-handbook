---
title: "탭과 세션"
parent: "사파리"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 740
---

# 탭과 세션 (Tabs)

사파리의 탭 흔적은 지금 열린 탭을 담는 SafariTabs.db, iOS 16 부터 닫은 탭을 담는 BrowserState.db, iCloud 로 연결된 다른 기기의 탭을 담는 CloudTabs.db 세 곳에 나뉘어 남고, 버전에 따라 각 DB 가 맡는 역할과 시각 기준이 달라집니다.

## 무엇을 기록하나 · 왜 생기나

사파리는 탭 목록을 DB 에 저장하고, 탭마다 제목·URL·마지막으로 본 시각 같은 값이 함께 남습니다[1]. SafariTabs.db 는 지금 열려 있는 탭을 보는 곳이고 표 이름이 `bookmarks` 입니다[1][2]. 이 표의 `parent` 열로 고정 탭, 최근 닫은 탭, 이 기기의 탭, 개인 정보 보호 탭이 나뉘고, `order_index` 는 탭을 연 순서입니다[2].

BrowserState.db 의 `tabs` 표는 iOS 16 부터 닫은 뒤의 탭만 담습니다[2]. CloudTabs.db 는 같은 계정으로 iCloud 에 연결된 다른 기기의 탭을 담아서[1], 이 기기에서 열지 않은 탭이 들어 있을 수 있습니다. 개인 정보 보호 탭을 가려내는 법은 [개인 정보 보호 브라우징 (Private Browsing)](private-browsing.md)에서 다룹니다.

## 위치와 버전별 차이

세 DB 모두 기기의 `/private/var/mobile/Library/Safari/` 아래에 있습니다[1][3]. 암호화하지 않은 백업에는 세 DB 가 모두 들어가지 않습니다. 방문 기록이 암호화한 백업에만 들어가는 규칙은 [방문 기록 (History.db)](history.md)에서 다룹니다.

| iOS 버전 | 달라지는 점 | 출처 |
|---|---|---|
| iOS 15 | SafariTabs.db, BrowserState.db, CloudTabs.db 세 DB 가 모두 있고, CloudTabs.db 를 읽는 도구는 드뭅니다 | [3] |
| iOS 16 | BrowserState.db 는 닫은 뒤의 탭만 담고, iOS 15 에서 복원된 탭이 iOS 16 으로 옮겨집니다 | [2] |
| iOS 18 이하 | `last_viewed_time` 이 Apple 절대 시각입니다 | [1] |
| iOS 26 이상 | `last_viewed_time` 이 UNIX 시각입니다 | [1] |

iLEAPP 의 탭 모듈은 iOS 12.4, 13.3.1, 14.3, 15.0.2, 16.1.1~16.5, 17.1~17.6.1, 18.0~18.7.8 에서 시험되어[1], iOS 26·27 기기에서는 결과를 직접 대조합니다. 탭 그룹이 SafariTabs.db 안에 어떻게 저장되는지, 예전 파일 이름으로 나오는 `LastSession.plist`·`RecentlyClosedTabs.plist`[4] 가 어느 버전까지 쓰였는지는 실제 데이터로 확인해야 합니다.

## 구조

| DB · 표 | 열 | 출처 |
|---|---|---|
| SafariTabs.db `bookmarks` | `id`, `parent`, `title`, `url`, `last_modified`, `date_closed`, `extra_attributes`, `local_attributes`, `external_uuid`, `deleted`, `order_index` | [1] |
| BrowserState.db `tabs` | `last_viewed_time`, `title`, `url`, `user_visible_url`, `opened_from_link`, `private_browsing` | [1] |
| CloudTabs.db `cloud_tabs` | `system_fields`, `title`, `url`, `device_uuid`, `tab_uuid` | [1] |
| CloudTabs.db `cloud_tab_devices` | `device_uuid`, `device_name` | [1] |

CloudTabs.db 의 두 표는 `device_uuid` 로 이어지고, iLEAPP 는 이 열로 탭에 기기 이름을 붙입니다[1]. 위 열은 iLEAPP 가 읽는 것만 적은 것이라 실제 DB 에서 두 표의 열 목록을 한 번 더 봅니다. SafariTabs.db 의 `bookmarks` 표는 [북마크와 읽기 목록 (Bookmarks·Reading List)](bookmarks-reading-list.md)의 Bookmarks.db `bookmarks` 표와 열 이름이 여럿 겹치지만, 같은 구조인지는 실제 데이터로 비교합니다.

SafariTabs.db 의 두 BLOB 열 안에는 이진 plist 가 들어 있습니다.

| 열 | 안의 키 | 출처 |
|---|---|---|
| `local_attributes` | `LastVisitTime`, `OpenedFromLink`, `TabIndex`, `IsMuted`, `ShowingReader`[1], `SessionState`[2] | [1][2] |
| `extra_attributes` | `DateLastViewed` | [1] |

`SessionState` 키 안에는 또 다른 이진 plist 가 들어 있고, 앞 4바이트를 떼어야 plist 로 읽힙니다[2].

사파리 설정 plist 에도 탭과 이어진 이름의 키가 있지만, 이름만으로 값의 뜻을 단정할 수는 없습니다.

| 위치 | 키 |
|---|---|
| AppDomain-com.apple.mobilesafari `Library/Preferences/com.apple.mobilesafari.plist` | `CloudTabsEnabled`(bool), `BrowserControllersSavedState`(dict, 아래 UUID 키), `NewTabBehaviorIsStartPage`(bool), `ShowTabGroupFavoritesPreferenceKey`(bool), `LastPeriodicTabGroupsReportTime`(float), `StartPageSections`(bytes), `WBSCloudKitStartPageSectionOrder`(list), `LastActiveProfile`(str) |
| HomeDomain `Library/Preferences/com.apple.SafariBookmarksSyncAgent.plist` | `TabGroupMigrationStateEncodedRecordData`(bytes), `MigrationStateEncodedRecordData`(bytes), `NewestLaunchedSafariSyncControllerOSVersion`(str), `NewestLaunchedSafariBookmarksSyncAgentVersion`(str), `CC_OncePerBootBackingData`, `CKPerBootTasks`, `CKStartupTime` |

## 증거로서 의미

**증명하는 것.** SafariTabs.db 에 탭 행이 있으면 수집 시점에 그 URL 의 탭이 사파리에 저장되어 있었다는 사실을 보여 주고, `local_attributes` 의 `LastVisitTime` 과 `extra_attributes` 의 `DateLastViewed` 로 탭을 마지막으로 본 때를 추정할 수 있습니다[1]. BrowserState.db 의 행은 iOS 16 이후라면 닫은 탭의 기록이고[2], `opened_from_link` 로 링크를 눌러 연 탭인지를 봅니다[1].

**증명하지 못하는 것.** 탭이 열려 있었다는 기록만으로 사용자가 그 페이지를 읽었다고 할 수 없습니다. CloudTabs.db 의 탭은 다른 기기의 탭이라서[1] 이 기기에서 연 것으로 쓰면 안 되고, 어느 기기의 탭인지는 `device_name` 과 `device_uuid` 를 함께 적어 밝힙니다. 탭 DB 에 없는 페이지는 이미 닫혀 지워졌을 수 있어서 방문하지 않았다는 근거가 되지 못합니다.

보고서에는 "수집 시점에 이 URL 의 탭이 이 기기 사파리에 저장되어 있었고, 마지막으로 본 시각이 이렇게 기록되어 있다" 처럼 씁니다.

## 시각 해석

BrowserState.db 의 `last_viewed_time` 은 iOS 18 이하에서 Apple 절대 시각, iOS 26 이상에서 UNIX 시각입니다[1]. iLEAPP 는 버전을 보지 않고 값이 978307200 보다 크면 UNIX 로, 아니면 978307200 을 더해 Apple 절대 시각으로 바꿉니다[1]. `last_modified`, `date_closed`, `LastVisitTime`, `DateLastViewed` 도 같은 방식으로 자릿수를 본 뒤 결과가 수집 시각보다 앞인지 확인하고 씁니다. 두 기준을 읽는 법은 [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md)에 있습니다.

## 함정과 한계

- 암호화하지 않은 백업에는 세 DB 가 없으므로, 탭을 보려면 다른 수집 방식이 필요한지 먼저 따집니다. 수집 방식은 [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md)에서 다룹니다.
- iOS 15 도구 비교에서 CloudTabs.db 를 읽는 도구가 거의 없었으므로[3], 도구 결과에 다른 기기 탭이 없다고 DB 가 비었다고 보지 않습니다.
- `SessionState` 는 앞 4바이트를 떼지 않으면 plist 로 열리지 않아서[2], 도구 결과에 이 값이 비어 있으면 직접 꺼내 확인합니다.

## 직접 분석해 보기

먼저 SafariTabs.db 에서 탭과 폴더를 한꺼번에 뽑아 `parent` 로 묶어 봅니다.

```sql
SELECT id, parent, title, url, order_index, deleted,
       last_modified, date_closed,
       length(local_attributes) AS la_len, length(extra_attributes) AS ea_len
FROM bookmarks
ORDER BY parent, order_index;
```

헥스로는 한 행의 `local_attributes` 를 `SELECT hex(local_attributes) FROM bookmarks WHERE id = ?;` 로 꺼내, 맨 앞에 이진 plist 의 시작 표식(`bplist`)이 오는지 봅니다. 그다음 plist 를 풀어 `SessionState` 값을 따로 꺼내면, 이 값은 앞 4바이트를 떼어 낸 나머지를 다시 plist 로 엽니다[2]. 떼어 낸 뒤 맨 앞에 시작 표식이 오는지 헥스로 한 번 더 봅니다. 시작 표식과 이진 plist 구조는 [속성 목록 파일 (plist·NSKeyedArchiver)](../../../01-foundations/data-formats/plist.md)에서 다룹니다.

BrowserState.db 는 아래처럼 닫은 탭을 시각 순으로 봅니다.

```sql
SELECT title, url, user_visible_url, opened_from_link, private_browsing,
       datetime(CASE WHEN last_viewed_time > 978307200
                     THEN last_viewed_time
                     ELSE last_viewed_time + 978307200 END, 'unixepoch') AS last_viewed_utc
FROM tabs
ORDER BY last_viewed_time;
```

CloudTabs.db 는 `PRAGMA table_info(cloud_tabs);` 와 `PRAGMA table_info(cloud_tab_devices);` 로 열을 확인한 뒤 `device_uuid` 로 두 표를 이어 기기별 탭을 봅니다[1]. 공개 도구로는 iLEAPP 의 사파리 탭 모듈이 세 DB 를 함께 읽으므로[1], 직접 뽑은 결과와 탭 수를 맞춰 봅니다.

> 그림 자리: SafariTabs.db `bookmarks` 표에서 `parent` 로 묶인 폴더 행과 탭 행, 그리고 `local_attributes` 안의 plist 속 `SessionState` 가 한 겹 더 들어 있는 모양

## 교차 검증

탭의 URL 을 [방문 기록 (History.db)](history.md)의 방문 행과 맞추고, 다른 기기의 탭은 방문 기록의 `origin` 이 1 인 행과 비교합니다. 바이옴의 사파리 스트림은 [바이옴 (Biome)](../../app-usage/biome/index.md)에서 다루고, 조사 흐름은 [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md)을 따릅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 16 이후 파일 시스템 시험 데이터로 아래를 풀어 봅니다.

1. SafariTabs.db `bookmarks` 에서 `parent` 값별로 행을 세고, 폴더 행의 `title` 로 각 묶음이 어떤 탭 종류인지 짐작해 봅니다.
2. 탭 하나의 `local_attributes` 에서 `LastVisitTime` 과 `extra_attributes` 의 `DateLastViewed` 를 꺼내 두 값을 비교합니다.
3. BrowserState.db `tabs` 의 `last_viewed_time` 자릿수를 보고 기기의 iOS 버전과 기준이 맞는지 확인합니다.
4. CloudTabs.db 에 기기가 몇 대 있는지 세고, 각 기기의 탭이 이 기기 방문 기록에도 있는지 찾아봅니다.

## 참고 문헌

1. iLEAPP `scripts/artifacts/safariTabs.py` (abrignoni/iLEAPP, main) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/safariTabs.py
2. D20 Forensics, "iOS 16 - Breaking Down the Biomes (Part 4) - Surfin' with Safari" (2022-09-28) — https://blog.d204n6.com/2022/09/ios-16-breaking-down-biomes-part-4.html
3. iOS 15 Image Forensics Analysis and Tools Comparison - Native Apps (blog.digital-forensics.it, 2023-10) — https://blog.digital-forensics.it/2023/10/ios-15-image-forensics-analysis-and.html
4. Forensafe, iOS Safari Browser — https://forensafe.com/blogs/iOSSafari.html
