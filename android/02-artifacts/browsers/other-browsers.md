---
title: "그 밖의 브라우저"
parent: "아티팩트 · 인터넷·브라우저"
nav_order: 890
---

# 그 밖의 브라우저 (웨일·파이어폭스)

네이버 웨일(com.naver.whale)은 공개 도구에 전용 파서가 없고 파일 배치를 다룬 공개 자료도 없는 브라우저이고, 파이어폭스(org.mozilla.firefox)는 Chromium 계열과 다른 배치로 `files/places.sqlite` 에 방문 기록·북마크·검색어를 남기면서 시각을 유닉스 밀리초로 적습니다 [1][3][4].

## 무엇을 기록하나 · 왜 생기나

**웨일.** Google Play 에 올라간 앱 이름은 "Whale - 네이버 웨일 브라우저" 이고 개발자는 NAVER Corp. 입니다 [5]. 웨일에는 퀵서치, 툴바 북마크, 원하는 콘텐츠를 담는 스크랩북, 악성 광고를 막는 클린 웹, 웨일온 화상회의가 있고, 네이버 아이디로 로그인하면 PC와 스마트폰에서 같은 북마크와 방문 기록을 씁니다 [5]. 파일 및 미디어 권한은 다운로드한 파일을 저장하거나 기기의 파일을 열 때 쓰고, Android 13 미만에서만 씁니다 [5]. 웨일이 Chromium 기반인지는 실제 기기의 파일 구조로 확인해야 합니다.

**파이어폭스.** Firefox for Android 는 방문할 때마다 `places.sqlite` 에 주소와 방문을 쌓고, 같은 파일에 북마크와 검색어도 둡니다 [3][4]. 쿠키, 입력 양식 기록, 사이트 권한은 프로필 폴더의 SQLite 파일에, 다운로드와 최근 닫은 탭, 자주 가는 사이트는 `databases` 폴더의 DB 에 남고, 페이지 캐시는 `cache2/entries` 에 쌓입니다 [3]. ALEAPP 에는 Firefox 전용 모듈이 여러 개 있어서(firefox.py, firefoxCookies.py, firefoxDownloads.py, firefoxFormHistory.py, firefoxPermissions.py, firefoxRecentlyClosedTabs.py, firefoxTopSites.py, browserCachefirefox.py) 이 파일들을 따로 읽습니다 [1].

같은 Gecko 계열 앱인 Fennec F-Droid(org.mozilla.fennec_fdroid)와 Tor Browser(org.torproject.torbrowser)도 같은 파일 배치를 씁니다 [3]. ALEAPP 의 방문 기록 모듈은 패키지 이름이 아니라 `files/places.sqlite` 라는 배치로 파일을 찾고, 브라우저 열에는 경로 속 패키지 이름을 적습니다 [3].

## 위치와 버전별 차이

**웨일.** 알려진 것이 적어서 상태만 표로 정리합니다.

| 항목 | 상태 |
|---|---|
| 패키지 이름 | com.naver.whale (Play 상세 페이지 주소의 id) [5] |
| 공개 도구 전용 파서 | ALEAPP 에 없음 [1] |
| 프로필 폴더 이름(`app_chrome` 인지 다른 이름인지) | 공개 자료 없음 |
| History·Cookies 같은 파일 이름 | 공개 자료 없음 |
| 동기화로 들어온 PC 방문 기록이 폰 파일에 섞이는지 | 공개 자료 없음 |

웨일이 `app_chrome/Default/History` 에 쓴다면 ALEAPP 는 그 파일을 Chromium 파서로 읽고 브라우저 이름 열에 com.naver.whale 을 적습니다. ALEAPP 는 `app_chrome` 을 쓰는 Chromium 파생 브라우저를 경로 안의 패키지 폴더 이름으로 구분하기 때문입니다 [2]. 실제로 웨일이 `app_chrome` 을 쓰는지는 실제 기기로 확인합니다.

**파이어폭스.** 경로는 ALEAPP 가 찾는 패턴 기준이고, 방문 기록은 앱 데이터 폴더 아래를, 나머지는 패키지 폴더 이름부터 적었습니다 [3].

| 위치 | 알려 주는 것 |
|---|---|
| `앱 데이터/files/places.sqlite` | 방문 기록, 방문, 북마크, 검색어 |
| `org.mozilla.firefox/files/mozilla/*.default/cookies.sqlite` | 쿠키 |
| `org.mozilla.firefox/files/mozilla/*.default/formhistory.sqlite` | 입력 양식에 넣은 값 |
| `org.mozilla.firefox/files/mozilla/*.default/permissions.sqlite` | 사이트별 권한 |
| `org.mozilla.firefox/databases/mozac_downloads_database` | 다운로드 (Tor Browser 는 `org.torproject.torbrowser/databases/mozac_downloads_database`) |
| `org.mozilla.firefox/databases/recently_closed_tabs` | 최근 닫은 탭 |
| `org.mozilla.firefox/databases/top_sites` | 자주 가는 사이트 |
| `data/org.mozilla.firefox/cache/*/cache2/entries/` | 페이지 캐시 |

지금 열려 있는 탭 목록이 남는 파일은 실제 기기로 확인합니다. 버전에 따른 차이 가운데 알려진 것은 아래와 같습니다.

| 버전 | 차이 |
|---|---|
| ALEAPP 표본: Android 14(Pixel 7a) versionCode 2016030615, Android 15 에뮬레이터 Firefox 154.0.1 versionCode 2016180578 | 같은 경로 패턴으로 읽음 [3] |
| 쿠키 스키마 16(Firefox 142)부터 | cookies.sqlite 의 expiry 단위가 초에서 밀리초로 바뀜 [3] |
| 옛 Firefox DB | `moz_places_metadata_search_queries` 표가 없어 ALEAPP 가 검색어 추출을 건너뜀 [3] |

두 앱의 데이터 폴더를 확보하는 방법은 [모바일 증거 확보 (Acquisition)](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 봅니다.

## 구조

웨일은 파일 구조가 알려지지 않았고, Chromium 계열 파일이 나오면 [크롬 (Chrome for Android)](chrome/index.md) 페이지의 방법으로 읽습니다. 아래는 Firefox 의 `places.sqlite` 이고, 표와 열은 Mozilla application-services 의 main 가지 스키마 파일 기준입니다(특정 Firefox 버전 태그가 아닙니다) [4].

| 표 | 주요 열 | 알려 주는 것 |
|---|---|---|
| moz_places | id, url, title, visit_count_local, visit_count_remote, hidden, typed, frecency, last_visit_date_local, last_visit_date_remote, guid, foreign_count, url_hash, description, preview_image_url, origin_id, sync_status, sync_change_counter, unknown_fields | 주소 한 개당 한 행 |
| moz_historyvisits | id, is_local, from_visit, place_id, visit_date, visit_type, unknown_fields | 방문 한 건당 한 행 |
| moz_bookmarks | id, fk(place_id), type, parent, position, title, dateAdded, lastModified, guid, syncStatus, syncChangeCounter | 북마크와 폴더 |
| moz_places_metadata | id, created_at, updated_at, place_id, total_view_time, search_query_id, referrer_place_id, document_type, typing_time, key_presses | 페이지를 본 시간과 입력 |
| moz_places_metadata_search_queries | id, term | 검색어 |
| moz_places_tombstones, moz_historyvisit_tombstones(place_id, visit_date), moz_bookmarks_deleted | — | 삭제 흔적 |
| moz_inputhistory | place_id, input 등 | 열 전체와 뜻은 공개 자료 없음 |

moz_places 에서는 방문 횟수와 마지막 방문 시각이 로컬(local)과 원격(remote)으로 나뉘어 있어서, 동기화로 들어온 값과 이 기기에서 생긴 값이 따로 적힙니다 [4]. moz_historyvisits 의 is_local 은 로컬에서 추가한 방문이면 항상 참, 동기화로 추가된 방문이면 항상 거짓이라서 방문 한 건 단위로 둘을 가를 수 있습니다 [4]. typed 열은 참·거짓이 아니라 횟수를 뜻하지만, ALEAPP 는 0/1 을 No/Yes 로 표시합니다 [3][4]. moz_places_metadata 의 document_type 은 0 이 일반 문서, 1 이 미디어입니다 [4].

ALEAPP 가 읽는 값의 뜻은 다음과 같습니다 [3].

| 열 | 값 |
|---|---|
| moz_historyvisits.visit_type | 1 LINK, 2 TYPED, 3 BOOKMARK, 4 EMBED, 5 REDIRECT_PERMANENT, 6 REDIRECT_TEMPORARY, 7 DOWNLOAD, 8 FRAMED_LINK, 9 RELOAD |
| moz_bookmarks.type | 1 URL, 2 Folder, 3 Separator |
| downloads.status | 3 Paused, 4 Canceled, 5 Failed, 6 Finished |

다른 파일에서 ALEAPP 가 읽는 열은 이렇습니다 [3]. formhistory.sqlite 의 moz_formhistory 표에서는 fieldname, value, timesUsed, id 와 firstUsed, lastUsed 를 읽고, mozac_downloads_database 의 downloads 표에서는 file_name, url, content_type, content_length, status 와 저장 폴더 열을 읽는데 이 열의 이름은 스키마에 따라 destination_directory 이거나 directory_path 입니다. recently_closed_tabs 표와 top_sites 표에서는 title, url, created_at 을 읽고, top_sites 에는 기본 사이트인지 나타내는 열도 있습니다.

> 그림 자리: moz_places 한 행에 moz_historyvisits 여러 행이 place_id 로 이어지고, moz_bookmarks 와 moz_places_metadata 도 place_id 로 붙는 관계도. is_local 참·거짓으로 로컬 방문과 동기화 방문을 색으로 나눈다

## 증거로서 의미

**증명하는 것.** Firefox 의 moz_historyvisits 에 is_local 이 참인 행이 있으면 이 기기의 Firefox 에서 그 주소를 그 시각에 방문했다는 기록이 남아 있다는 뜻이고, 거짓인 행은 동기화로 들어온 방문입니다 [4]. visit_type 으로 링크를 눌러 들어갔는지(LINK), 주소를 쳐서 들어갔는지(TYPED), 북마크로 들어갔는지(BOOKMARK) 같은 들어간 경로를 가를 수 있습니다 [3]. 다운로드 표의 status 가 6(Finished)이면 Firefox 가 그 파일을 끝까지 받았다고 기록한 것입니다 [3].

**증명하지 못하는 것.** 기록만으로는 기기를 누가 들고 있었는지 알 수 없습니다. 같은 배치를 Tor Browser 와 Fennec F-Droid 도 쓰기 때문에, 파일 이름만 보고 Firefox 기록이라고 쓰지 말고 경로의 패키지 이름을 함께 적습니다 [3]. 삭제 흔적 표(moz_places_tombstones 등)에 남은 행은 지운 항목을 가리킬 수 있지만, 이 표들이 언제 채워지고 언제 비워지는지 알려지지 않아서 행이 없다는 사실만으로 지운 적이 없다고 말할 수 없습니다 [4]. 웨일은 파일 구조도, 동기화된 PC 방문 기록이 섞이는지도 알려지지 않았기 때문에, 웨일 파일에서 주소를 찾더라도 이 폰에서 직접 연 것이라고 단정하지 않습니다.

## 시각 해석

Firefox 는 파일마다 시각 단위가 다릅니다. places.sqlite 의 시각은 유닉스 밀리초이고 ALEAPP 는 1000 으로 나눠 UTC 로 바꾸며, 다른 파일까지 ALEAPP 가 읽는 단위를 정리하면 다음과 같습니다 [3].

| 파일·열 | 단위 |
|---|---|
| places.sqlite: moz_historyvisits.visit_date, moz_places.last_visit_date_local, moz_bookmarks.dateAdded·lastModified | 밀리초 |
| cookies.sqlite: lastAccessed, creationTime | 마이크로초 |
| cookies.sqlite: expiry | 스키마 16 미만은 초, 16 이상은 밀리초 |
| formhistory.sqlite: firstUsed, lastUsed | 마이크로초 |
| permissions.sqlite: modificationTime, expireTime | 밀리초 |
| mozac_downloads_database, recently_closed_tabs, top_sites: created_at | 밀리초 |

Android 의 places 시각은 밀리초이고, moz_bookmarks_synced.dateAdded 와 moz_places_stale_frecencies.stale_at 도 밀리초입니다 [3][4]. 데스크톱 Firefox 의 PRTime 은 마이크로초라서 Android 값을 데스크톱 기준으로 읽으면 어긋납니다 [3]. cookies.sqlite 의 expiry 는 ALEAPP 가 `PRAGMA user_version` 이 16 이상이면 1000 으로 나누고, 버전을 읽지 못하면 값이 100000000000 보다 클 때 밀리초로 봅니다 [3].

last_visit_date_local 은 이 기기의 마지막 방문, last_visit_date_remote 는 동기화로 들어온 마지막 방문이라서 [4], 타임라인에는 local 쪽을 쓰고 remote 쪽은 따로 표시합니다. 시각 형식 전반은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

## 함정과 한계

ALEAPP 의 "Firefox - Web History" 쿼리는 `moz_places.origin_id = moz_historyvisits.id` 로 두 표를 잇는데, 스키마에서 origin_id 는 moz_origins 표의 id 를 가리킵니다 [3][4]. 이 연결 때문에 결과가 빠지거나 틀어질 수 있으니, 방문 한 건 한 건은 스키마와 맞게 `moz_historyvisits.place_id = moz_places.id` 로 잇는 "Firefox - Web Visits" 결과를 기준으로 봅니다 [3][4].

typed 열을 ALEAPP 가 Yes/No 로 보여 주지만 스키마상 횟수라서, 2 이상의 값은 원본 파일에서 직접 확인합니다 [3][4]. 옛 Firefox DB 에는 검색어 표가 없어 ALEAPP 검색어 결과가 비어 나올 수 있고, 이때 검색을 안 했다는 뜻으로 읽지 않습니다 [3].

도구 결과에 Tor Browser 나 Fennec F-Droid 행이 Firefox 모듈 이름 아래 섞여 나올 수 있어서 브라우저 열의 패키지 이름을 확인합니다 [3]. 반대로 쿠키·입력 양식·사이트 권한 모듈은 `org.mozilla.firefox` 경로만 찾기 때문에, Fennec F-Droid 나 Tor Browser 의 cookies.sqlite 같은 파일은 도구 결과에 나오지 않아도 직접 열어 봅니다 [3]. 웨일은 전용 모듈이 없어서 도구 결과에 아무것도 없어도 파일이 없다는 뜻이 아닙니다 [1].

## 직접 분석해 보기

**헥스로 한 번.** 아래는 명세로 만든 예시이고 실제 기기의 값이 아닙니다. moz_historyvisits.visit_date 에 정수 1700000000000 이 들어 있다면 16진수로 `0x18BCFE56800` 이고, 밀리초라서 1000 으로 나누면 유닉스 초 1700000000 이 되어 2023-11-14 22:13:20 UTC 로 읽힙니다. 같은 값을 데스크톱 Firefox 처럼 마이크로초로 잘못 읽으면 1,700,000 초가 되어 1970-01-20 16:13:20 UTC 가 나오는데, 방문 시각이 1970년 1월로 나오면 단위를 잘못 고른 것입니다. SQLite 레코드 안에서 정수가 저장되는 방식은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md) 페이지를 봅니다.

**공개 도구로 한 번.** `places.sqlite` 사본을 sqlite3 로 열어 방문을 한 건씩 뽑고, ALEAPP 의 "Firefox - Web Visits" 결과와 행 수를 맞춰 봅니다.

```
SELECT p.url, datetime(v.visit_date/1000, 'unixepoch') AS visit_utc,
       v.visit_type, v.is_local
FROM moz_historyvisits v
JOIN moz_places p ON v.place_id = p.id
ORDER BY v.visit_date;
```

is_local 이 0 인 행은 동기화로 들어온 방문이라서 이 기기의 행위로 적지 않습니다 [4]. 도구 결과를 원본과 맞춰 보는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지를 봅니다.

웨일은 패키지 폴더를 직접 열어 `app_chrome` 같은 Chromium 계열 폴더가 있는지부터 보고, 있으면 Chrome 과 같은 방법으로 읽습니다.

## 교차 검증

- [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) — `dumpsys usagestats` 이벤트 줄에는 time=, type=, package=, class= 필드가 있고 ACTIVITY_RESUMED·ACTIVITY_PAUSED 같은 종류가 나옵니다. package= 가 org.mozilla.firefox 나 com.naver.whale 인 줄의 시각이 방문 시각과 겹치는지 봅니다.
- [공용 저장 공간 (Shared Storage·/sdcard)](../../01-foundations/storage/shared-storage.md) — mozac_downloads_database 의 저장 폴더 열과 파일 이름으로 받은 파일이 실제로 남아 있는지 봅니다.
- [설치된 앱 (packages.xml)](../app-usage/packages/index.md) — 설치 시각과 버전을 확인합니다. Tor Browser 가 깔려 있었는지도 여기서 봅니다.
- [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) — 삭제 흔적 표 말고도 SQLite 빈 공간에 지운 행이 남는지 봅니다.
- [크롬 (Chrome for Android)](chrome/index.md), [삼성 인터넷 (Samsung Internet)](samsung-internet.md), [네이버 앱 (NAVER)](naver.md) — 같은 시간대에 다른 브라우저를 쓴 기록과 함께 봅니다.
- [웹 사용 행위 재구성 (Web Activity)](../../04-scenarios/activity/web-activity.md), [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)

## 실습

공개 실습 자료나 직접 만든 시험 기기 가운데 Firefox 나 웨일이 깔린 이미지를 골라 아래 질문을 풀어 봅니다.

1. `files/places.sqlite` 가 있는 패키지 폴더를 모두 찾으면 몇 개이고, 각각 어느 앱입니까?
2. moz_historyvisits 에서 is_local 이 0 인 행은 몇 개이고, 그 행들의 가장 이른 방문 시각은 언제입니까?
3. ALEAPP 의 "Firefox - Web History" 와 "Firefox - Web Visits" 결과의 행 수는 같습니까? 다르다면 위 SQL 로 뽑은 결과와 어느 쪽이 맞습니까?
4. cookies.sqlite 의 `PRAGMA user_version` 값은 얼마이고, 그 값에 따라 expiry 를 어떤 단위로 읽어야 합니까?
5. 웨일 패키지 폴더 아래에 `app_chrome` 폴더가 있습니까? 있다면 ALEAPP 는 그 행들을 어떤 브라우저 이름으로 적습니까?

## 참고 문헌

1. ALEAPP `scripts/artifacts` 폴더 목록(GitHub API) — https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
2. ALEAPP `scripts/artifacts/chrome.py` (main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chrome.py
3. ALEAPP 저장소 `scripts/artifacts` (main, 커밋 c044fe5, 2026-09-24). firefox.py, firefoxCookies.py, firefoxDownloads.py, firefoxFormHistory.py, firefoxPermissions.py, firefoxRecentlyClosedTabs.py, firefoxTopSites.py, browserCachefirefox.py — https://github.com/abrignoni/ALEAPP
4. Mozilla application-services, `components/places/sql/create_shared_schema.sql` (main) — https://raw.githubusercontent.com/mozilla/application-services/main/components/places/sql/create_shared_schema.sql
5. Google Play, "Whale - 네이버 웨일 브라우저" 상세 페이지(한국어) — https://play.google.com/store/apps/details?id=com.naver.whale&hl=ko
