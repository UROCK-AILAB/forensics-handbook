---
title: "웹 사용 행위 재구성"
parent: "시나리오 · 행위 재구성"
nav_order: 1460
---

# 웹 사용 행위 재구성 (Web Activity)

아이폰에서 언제 어떤 웹 페이지를 열었는지, 무엇을 검색했는지를 브라우저와 시스템 기록으로 되짚는 시나리오입니다. Safari·크롬 DB 하나하나의 구조는 브라우저 페이지에서 다루고, 이 페이지는 수집 범위에 따라 볼 수 있는 기록을 고르고, 브라우저 기록과 바이옴 (Biome) 을 겹쳐 지운 방문까지 찾는 순서에 집중합니다.

## 조사 질문

"사건 전에 특정 사이트를 방문했나", "이 검색어를 언제 입력했나", "방문 기록을 지웠나", "개인 정보 보호 모드로 무엇을 봤나" 같은 질문입니다. 답은 방문한 URL 과 시각, 방문한 기기(이 기기인지 iCloud 로 동기화된 다른 기기인지), 방문을 연 앱, 기록을 지운 흔적으로 나뉩니다. Safari 방문 기록 하나로는 동기화된 방문과 지운 방문을 가리기 어려워서 바이옴의 웹 사용 스트림과 탭 기록을 함께 봅니다.

## 먼저 확인할 것

**수집 범위**를 먼저 봅니다. 웹사이트 방문 기록은 암호를 건 로컬 백업에만 들어갑니다 [5][12]. 그래서 암호를 걸지 않은 로컬 백업에는 `History.db`·`SafariTabs.db`·`BrowserState.db`·`CloudTabs.db` 가 없고 HomeDomain `Library/Safari/Bookmarks.db` 만 있습니다. 바이옴은 전체 파일 시스템 추출에서 다룬 자료만 있습니다 [11].

**iOS 버전**에 따라 파일 위치와 시각 형식이 달라집니다.

| iOS 버전 | 달라지는 점 |
|---|---|
| iOS 15 | Safari 기록 파일은 `/private/var/mobile/Library/Safari/` 아래 `History.db`, `SafariTabs.db`, `BrowserState.db`, `CloudTabs.db`, `Bookmarks.db` 입니다 [1] |
| iOS 16 | `_DKEvent.Safari.History` 스트림이 `History.db` 보다 몇 초 늦게 찍히고, 기록을 지울 때 바이옴에 남는 모양도 알려져 있습니다 [4] |
| iOS 17 이후 | 프로필별 기록 `Safari/Profiles/*/History.db` 가 따로 있습니다 [2]. iLEAPP 의 바이옴 `App.WebUsage` 파서는 iOS 17.1~18.7.8 자료로 시험됐습니다 [7] |
| iOS 18 이하 / 26 이상 | Safari 탭 시각 형식이 iOS 18 이하는 Cocoa, iOS 26 이상은 Unix 입니다 [3] |
| iOS 27 | `Bookmarks.db` 와 아래 "로컬 백업에서 보이는 것" 의 파일이 암호 없는 백업에 있습니다 |

**시각 기준**이 브라우저마다 다릅니다. Safari 방문 시각은 값이 978307200 보다 크면 Unix 시각, 작으면 Mac 절대 시각으로 읽고 [2], 크롬은 1601-01-01 부터 센 마이크로초라서 [8] 기준점이 다릅니다. 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을 따릅니다.

**어느 앱이 웹을 열었는지**도 염두에 둡니다. iOS 에서 웹을 탐색하는 앱은 WebKit 을 써야 하고(App Review 지침 2.5.6), EU·일본에는 예외 권한이 있습니다 [10]. 앱 안에서 연 페이지는 Safari 기록 말고 그 앱의 데이터와 바이옴에서도 찾아봅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | Safari `History.db` — `/private/var/mobile/Library/Safari/History.db` [1] | `history_visits` 는 방문 한 번마다 한 행으로 `visit_time`, `title`, `redirect_source`, `redirect_destination`, `origin` 칸이 있고, `history_items` 는 URL 하나마다 한 행으로 `url`, `visit_count` 칸이 있습니다. `origin` 이 0 이면 이 기기, 1 이면 iCloud 로 동기화된 다른 기기의 방문입니다 [2] | [사파리](../../02-artifacts/browsers/safari/index.md) |
| 2 | Safari 탭 — `SafariTabs.db` [1] | 열려 있던 탭. 개인 정보 보호 모드 방문은 `History.db` 에 저장되지 않지만 개인 정보 보호 탭은 이 파일에 남습니다 [1][4] | [사파리](../../02-artifacts/browsers/safari/index.md) |
| 3 | 바이옴 `App.WebUsage` — `/private/var/mobile/Library/Biome/streams/restricted/` [6] | 시각, 제목, URL, 도메인, 번들 ID, GUID, 보관 28일 [6]. 비슷한 스트림으로 `Safari.Navigations`, `_DKEvent.Safari.History` 가 있습니다 [6] | [바이옴](../../02-artifacts/app-usage/biome/index.md) |
| 4 | 크롬 — 백업 `AppDomain-com.google.chrome.ios` 의 `Library/Application Support/Google/Chrome/Default/History` [9] | 크롬 방문 기록. 시각은 1601 기준 마이크로초 [8] | [크롬](../../02-artifacts/browsers/chrome.md) |
| 5 | 다른 앱 안의 웹 기록 | 네이버 앱 같은 앱의 자체 기록 | [네이버 앱](../../02-artifacts/browsers/naver.md) |
| 6 | 암호 없는 백업의 Safari 곁 기록 | 아래 "로컬 백업에서 보이는 것" | 이 페이지 |

바이옴 `App.WebUsage` 는 자료마다 필드가 조금씩 다릅니다. iLEAPP 는 경로 패턴 `*/Biome/streams/restricted/App.WebUsage/local/*` 에서 필드 1 을 GUID, 2 를 시각, 4 를 전체 URL, 5 를 도메인, 6 을 번들 ID(예: `com.apple.mobilesafari`)로 읽고, 필드 3·8 은 뜻을 모르는 정수로 남겨 둡니다 [7]. 제목 필드는 한 자료에 있지만 [6] iLEAPP 필드 목록에는 없습니다 [7]. 번들 ID 칸이 있어서 Safari 말고 다른 앱의 웹 사용도 담길 수 있지만, 다른 회사 앱 값이 실제로 들어가는지는 검체에서 확인합니다.

### 로컬 백업에서 보이는 것

암호를 걸지 않은 로컬 백업에는 방문 기록 DB 가 없는 대신 아래 파일이 있습니다. 칸의 시각 기준과, 이 기록이 방문 기록을 얼마나 대신할 수 있는지는 알려져 있지 않아서 "`History.db` 가 없어도 방문한 도메인의 흔적이 남는 곳" 으로만 씁니다.

| 파일 | 표·칸·키 이름 |
|---|---|
| HomeDomain `Library/Safari/Bookmarks.db` | `bookmarks` 표(칸 37개). 읽기 목록이 이 표에 드는지는 검체에서 확인합니다 |
| `AppDomain-com.apple.mobilesafari` 의 `Library/WebKit/WebsiteData/ResourceLoadStatistics/observations.db` | `ObservedDomains` 표의 `registrableDomain`, `lastSeen`, `hadUserInteraction`, `mostRecentUserInteractionTime` 등 |
| `AppDomain-com.apple.mobilesafari` 의 `Library/Metadata Cache/LPLinkMetadata.db` | `page_url` 표의 `url`, `uuid`, `last_fetch_date` 등 |
| `AppDomain-com.apple.mobilesafari` 의 `Library/Safari/IgnoredSiriSuggestedSites.db` | `ignored_siri_suggested_sites` 표의 `siriSuggestedSiteURL`, `query`, `timestamp`, `visitedURL` 등 |
| `AppDomainGroup-group.com.apple.safari` 의 `Library/Safari/PerSitePreferences.db` | `preference_values` 표의 `domain`, `preference`, `timestamp` 등 |
| `AppDomain-com.apple.mobilesafari` 의 `Library/Preferences/com.apple.mobilesafari.plist` | `RecentWebSearches`(목록), `LastActiveProfile`(문자열) 키 |

같은 이름의 `observations.db` 가 음악 앱(`AppDomain-com.apple.Music`)과 메일 앱(`AppDomain-com.apple.mobilemail`) 컨테이너에도 있어서, 도메인 흔적을 찾을 때는 Safari 컨테이너만 보지 않습니다.

## 분석 흐름

1. iOS 버전, 시간대, 수집 방법을 적고, 쓰던 브라우저를 백업 `Info.plist` 의 `Installed Applications` 나 `AppDomain-` 도메인 이름으로 확인합니다.
2. `History.db` 가 있으면 `history_visits` 와 `history_items` 를 이어 방문을 시각 순으로 늘어놓고, `origin` 으로 이 기기의 방문만 가립니다 [2].

   ```sql
   SELECT hi.url, hv.title, hv.origin,
          datetime(CASE WHEN hv.visit_time > 978307200 THEN hv.visit_time
                        ELSE hv.visit_time + 978307200 END, 'unixepoch') AS visit_utc,
          hi.visit_count
   FROM history_visits hv
   JOIN history_items hi ON hv.history_item = hi.id
   ORDER BY hv.visit_time;
   ```

   시각 판별식과 `history_visits.history_item` 을 `history_items.id` 와 잇는 방식은 iLEAPP 쿼리를 따른 것입니다 [2]. 버전에 따라 칸이 다를 수 있어서 쿼리가 칸 이름 오류로 멈추면 `PRAGMA table_info(history_visits);` 로 칸을 먼저 확인합니다.
3. `SafariTabs.db` 에서 열린 탭과 개인 정보 보호 탭을 봅니다 [1][4]. 탭 시각 형식은 iOS 버전에 따라 달라서 [3], 푼 값이 앞뒤 기록과 맞는지 확인합니다.
4. 전체 파일 시스템 추출이 있으면 바이옴 `App.WebUsage` 와 `_DKEvent.Safari.History` 를 `History.db` 와 겹칩니다. 바이옴에만 있고 `History.db` 에 없는 방문은 지운 방문일 수 있습니다. iOS 16 에서는 사용자가 기록을 하나씩 지워도 바이옴 SEGB 의 해당 기록이 곧바로 지워지지 않고, "전체 삭제" 때는 SEGB 안의 protobuf 가 그 자리에서 0x00 으로 덮어 써집니다 [4]. 0x00 으로 채워진 레코드가 몰려 있다면 전체 삭제를 했을 가능성으로 적고 [증거를 없애려 했나](anti-forensics/index.md) 와 이어 봅니다. SEGB 를 직접 읽는 법은 [SEGB 형식](../../01-foundations/data-formats/segb.md) 을 따릅니다.
5. 바이옴 `remote` 폴더의 기록은 같은 Apple 계정의 다른 기기에서 온 것이라 [13][14] 빼고, iLEAPP 의 `App.WebUsage` 파서는 `local` 폴더만 읽고 `tombstone` 폴더는 건너뛰어서 [7], `tombstone` 폴더는 따로 열어 봅니다.
6. 크롬 같은 다른 브라우저의 기록을 같은 방식으로 뽑아 시각 기준을 맞춘 뒤 합칩니다 [8][9].
7. 로컬 백업만 있다면 위 "로컬 백업에서 보이는 것" 표에서 조사 대상 도메인을 찾고, 찾은 흔적을 방문 시각이 아니라 "이 도메인의 흔적이 있다" 로만 적습니다. `RecentWebSearches` 키가 있으면 검색어 목록을 확인합니다.
8. 확정한 방문을 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올리고, 같은 시각의 앱 사용·위치 기록과 맞춰 봅니다.

## 흔한 오판

`History.db` 의 방문을 모두 이 기기에서 한 방문으로 적는 실수가 가장 흔합니다. `origin` 이 1 인 행은 iCloud 로 동기화된 다른 기기의 방문이라서 [2], 이 기기의 행위로 적지 않습니다.

방문 기록이 없다는 사실을 "방문하지 않았다" 로 읽는 일도 조심합니다. 개인 정보 보호 모드 방문은 `History.db` 에 저장되지 않고 [1], iOS 16 에서는 개인 정보 보호 탭 기록이 SEGB 에 처음부터 쓰이지 않는 것으로 보입니다 [4]. 암호 없는 백업에는 방문 기록이 아예 들어가지 않습니다 [5].

바이옴과 `History.db` 의 시각 차이를 조작 흔적으로 보는 실수도 있습니다. iOS 16 에서 `_DKEvent.Safari.History` 는 `History.db` 보다 몇 초 늦게 찍혀서 [4], 몇 초 차이는 같은 방문으로 묶습니다.

URL 이 있다고 "사용자가 그 페이지를 읽었다" 로 적는 일도 있습니다. `history_visits` 에는 `redirect_source`·`redirect_destination` 칸이 있어서 [2], 리디렉션으로 이어진 방문인지 이 칸과 앞뒤 행으로 확인한 뒤 사용자가 머문 페이지를 가립니다.

## 보고서 문장 예

> Safari `History.db` 의 `history_visits` 표에 (URL) 방문이 (시각, UTC) 에 기록돼 있고, `origin` 값은 0 입니다. iLEAPP 의 풀이에 따르면 이 값은 이 기기에서 한 방문을 뜻합니다. 이 기록은 이 기기의 Safari 가 해당 주소를 열었다는 것까지 보여 주며, 누가 기기를 조작했는지와 페이지 내용을 읽었는지는 보여 주지 않습니다.

> 바이옴 `App.WebUsage` 스트림의 `local` 폴더에 (도메인) 기록이 (시각, UTC) 에 있으나 같은 시각의 `History.db` 에는 해당 방문이 없습니다. 이 차이는 방문 기록이 나중에 지워졌을 가능성을 보여 주며, 누가 언제 지웠는지는 이 기록만으로 말할 수 없습니다.

## 함께 볼 페이지

- [사파리 (Safari)](../../02-artifacts/browsers/safari/index.md)
- [크롬 (Chrome for iOS)](../../02-artifacts/browsers/chrome.md)
- [네이버 앱 (NAVER)](../../02-artifacts/browsers/naver.md)
- [바이옴 (Biome)](../../02-artifacts/app-usage/biome/index.md)
- [증거를 없애려 했나 (Anti-Forensics)](anti-forensics/index.md)
- [콘텐츠 검색 (Content Search)](../../03-techniques/analysis/content-search.md)
- [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. digital-forensics.it, "iOS 15 Image Forensics Analysis and Tools Comparison - Native Apps" (2023-10) — https://blog.digital-forensics.it/2023/10/ios-15-image-forensics-analysis-and.html
2. iLEAPP, `scripts/artifacts/safariHistory.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/safariHistory.py
3. iLEAPP, `scripts/artifacts/safariTabs.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/safariTabs.py
4. D20 Forensics, "iOS 16 - Breaking Down the Biomes (Part 4) - Surfin' with Safari" (2022-09-28) — https://blog.d204n6.com/2022/09/ios-16-breaking-down-biomes-part-4.html
5. Apple 지원, "About encrypted backups on your iPhone, iPad, or iPod touch" — https://support.apple.com/en-us/108353
6. digital-forensics.it, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
7. iLEAPP, `scripts/artifacts/biomeAppWebUsage.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/biomeAppWebUsage.py
8. iLEAPP, `scripts/artifacts/chrome.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/chrome.py
9. MVT, `src/mvt/ios/modules/mixed/chrome_history.py` — https://raw.githubusercontent.com/mvt-project/mvt/main/src/mvt/ios/modules/mixed/chrome_history.py
10. Apple Developer, "App Review Guidelines" (2.5.6) — https://developer.apple.com/app-store/review/guidelines/
11. digital-forensics.it, "84 Streams Later: Exploring the Evolution of Apple Biome in iOS" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-exploring-evolution-of.html
12. MVT 문서, "Records extracted by mvt-ios" — https://docs.mvt.re/en/latest/ios/records/
13. iLEAPP, `scripts/artifacts/biomeInfocus.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/biomeInfocus.py
14. Magnet Forensics, "Bringing it Back With Biome Data" — https://www.magnetforensics.com/blog/bringing-it-back-with-biome-data/
