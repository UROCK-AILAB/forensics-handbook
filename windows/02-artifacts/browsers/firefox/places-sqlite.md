---
title: "방문·다운로드·즐겨찾기"
parent: "파이어폭스"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1710
---

# 방문·다운로드·즐겨찾기 (places.sqlite)

파이어폭스는 방문한 페이지, 즐겨찾기, 다운로드 기록을 프로필 본 폴더의 `places.sqlite` 파일 하나에 SQLite 형식으로 모아 둡니다. 한 번의 방문마다 언제, 어떤 방식으로 그 페이지에 닿았는지가 행으로 남습니다.

## 무엇을 기록하나 · 왜 생기나

파이어폭스는 방문한 주소를 `moz_places` 표에 한 번씩 적어 두고, 같은 주소를 여러 번 방문하면 방문마다 `moz_historyvisits` 표에 행을 하나씩 늘립니다. 즐겨찾기와 폴더는 `moz_bookmarks` 표에, 주소창에 친 글자와 그때 고른 페이지는 `moz_inputhistory` 표에 남습니다. Firefox 21 부터는 다운로드 기록도 `places.sqlite` 에 들어가며, 그 전에는 `downloads.sqlite` 라는 파일을 따로 썼습니다.

방문 하나에는 그 페이지에 어떻게 닿았는지를 나타내는 방문 유형 (visit type) 이 붙습니다. 링크를 눌렀는지, 주소창에 쳤는지, 리다이렉트로 넘어갔는지가 이 값으로 갈립니다.

## 위치와 버전별 차이

- 위치는 프로필 본 폴더의 `places.sqlite` 입니다. 프로필 폴더를 찾는 법은 [프로필 구조 (profiles.ini·prefs.js)](profiles-ini-prefs-js.md) 에서 다룹니다.
- Vista·7 의 실제 경로 예는 `C:\Users\%USERNAME%\AppData\Roaming\Mozilla\Firefox\Profiles\%PROFILE%.default\places.sqlite` 입니다.
- Firefox 21 전에는 다운로드 기록이 `downloads.sqlite` 의 `moz_downloads` 표에 있었습니다. 이 표에는 `startTime`, `endTime`, `source`, `currBytes`, `maxBytes` 열이 있었습니다. 오래된 데이터를 분석할 때는 이 파일도 찾습니다.
- 아래 표와 열 이름은 파이어폭스 개발 중인 최신 코드(main 가지) 기준입니다[1]. 예전 출시판에는 없는 열이 있을 수 있으므로, 오래된 데이터에서는 표와 열을 먼저 확인합니다.

## 구조

저장 형식은 SQLite 입니다. 페이지와 레코드를 읽는 법은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

### 주요 표

| 표 | 담는 것 |
|---|---|
| `moz_places` | 방문한 주소 하나마다 한 행입니다. 방문 횟수와 마지막 방문 시각을 담습니다 |
| `moz_historyvisits` | 방문 하나마다 한 행입니다. 언제, 어떤 유형으로 방문했는지 담습니다 |
| `moz_bookmarks` | 즐겨찾기와 폴더입니다 |
| `moz_bookmarks_deleted` | 지운 즐겨찾기의 `guid` 와 지운 시각입니다 |
| `moz_inputhistory` | 주소창에 친 글자와 그때 고른 페이지입니다 |
| `moz_keywords` | 즐겨찾기에 붙인 키워드입니다 |
| `moz_annos`·`moz_anno_attributes` | 페이지에 붙인 주석입니다. 다운로드 기록도 여기에 들어갑니다 |
| `moz_origins` | 주소의 출처(스킴·호스트)와 빈도 점수입니다 |
| `moz_places_metadata` | 페이지를 본 시간, 스크롤, 키 입력 같은 상호작용 기록입니다 |
| `moz_places_metadata_search_queries` | 검색어(`terms`)입니다. `moz_places_metadata.search_query_id` 가 이 표를 가리킵니다 |

### `moz_places` 의 열

- `id`, `url`, `title`, `rev_host`, `visit_count`, `hidden`, `typed`, `frecency`, `last_visit_date`, `guid`, `foreign_count`, `url_hash`, `description`, `preview_image_url`, `site_name`, `origin_id`, `recalc_frecency`, `alt_frecency`, `recalc_alt_frecency` 입니다.
- `rev_host` 는 호스트 이름을 거꾸로 뒤집은 문자열입니다. 같은 도메인의 주소를 빨리 모으려는 색인용입니다.
- `visit_count` 는 방문 횟수입니다. `typed` 는 주소창에 직접 친 적이 있는지 표시합니다.
- `frecency` 는 자주·최근 방문을 함께 셈한 점수입니다. 주소창 자동완성 순서를 정하는 값입니다.

### `moz_historyvisits` 의 열

- `id`, `from_visit`, `place_id`, `visit_date`, `visit_type`, `session`, `source`, `triggeringPlaceId` 입니다.
- `place_id` 는 `moz_places.id` 를 가리키며, 어느 주소를 방문했는지 잇는 열쇠입니다.
- `from_visit` 은 이 방문의 바로 앞 방문을 가리키므로 링크를 눌러 넘어온 경로를 거슬러 올라가 찾을 수 있습니다.
- `visit_date` 는 방문 시각입니다.

### `visit_type` 값

방문 유형은 아래와 같습니다[2].

| 값 | 이름 | 뜻 |
|---|---|---|
| 1 | TRANSITION_LINK | 링크를 눌러 새 페이지를 열었습니다 |
| 2 | TRANSITION_TYPED | 주소창에 직접 쳤거나 자동완성 결과를 골랐습니다 |
| 3 | TRANSITION_BOOKMARK | 즐겨찾기로 들어갔습니다 |
| 4 | TRANSITION_EMBED | 페이지 안의 이미지·프레임 내용이 불러와졌습니다 |
| 5 | TRANSITION_REDIRECT_PERMANENT | 영구 리다이렉트로 넘어갔습니다 |
| 6 | TRANSITION_REDIRECT_TEMPORARY | 임시 리다이렉트로 넘어갔습니다 |
| 7 | TRANSITION_DOWNLOAD | 다운로드입니다 |
| 8 | TRANSITION_FRAMED_LINK | 프레임 안의 링크를 눌러 방문했습니다 |
| 9 | TRANSITION_RELOAD | 새로 고침입니다 |

- 값 2(TYPED) 는 사용자가 손으로 그 주소를 불러왔다는 뜻에 가깝습니다. 값 4(EMBED) 는 사용자가 그 주소를 열려고 한 것이 아닙니다.

### `moz_historyvisits.source` 값

| 값 | 이름 |
|---|---|
| 0 | VISIT_SOURCE_ORGANIC |
| 1 | VISIT_SOURCE_SPONSORED |
| 2 | VISIT_SOURCE_BOOKMARKED |
| 3 | VISIT_SOURCE_SEARCHED |

## 증거로서 의미

### 증명하는 것

- `moz_historyvisits` 의 한 행은 그 시각에 브라우저가 그 주소를 불러왔다는 기록입니다.
- `visit_type` 이 2(TYPED) 면 사용자가 주소창에 직접 쳤거나 자동완성을 골랐습니다.
- `from_visit` 을 따라가면 어느 페이지에서 링크를 눌러 이 페이지로 왔는지 거슬러 올라가 찾을 수 있습니다.
- `moz_bookmarks` 에 즐겨찾기가 있으면 이 프로필에 그 주소가 저장돼 있었습니다. 사용자가 직접 저장했는지, 설치 때 들어간 기본 즐겨찾기인지, 다른 브라우저에서 가져왔는지는 따로 확인합니다.
- 다운로드 주석이 있으면 이 브라우저로 그 파일을 내려받은 기록이 있습니다. `downloads/destinationFileURI` 에 저장 위치가, `downloads/metaData` 에 상태·끝난 시각·파일 크기 같은 값이 JSON 으로 남습니다.
- 사생활 보호 창에서 내려받은 파일은 다운로드 기록에 넣지 않습니다. `download.source.isPrivate` 가 참이면 기록하지 않습니다[4].

### 증명하지 못하는 것

- 페이지에서 무엇을 보았고 얼마나 머물렀는지는 방문 행만으로 알 수 없습니다. `moz_places_metadata` 의 상호작용 값이 힌트를 줄 뿐입니다.
- `visit_type` 이 4(EMBED) 나 리다이렉트인 행은 사용자가 그 주소를 열려고 한 것이 아닙니다. 페이지 안에 끼워 넣은 내용이나 자동 전환일 수 있습니다.
- 키보드 앞의 사람이 누구인지는 알 수 없습니다.
- 방문 행이 없다고 방문하지 않은 것은 아닙니다. 사용자가 기록을 지웠거나, 만료됐거나, 사생활 보호 창이었을 수 있습니다.

보고서에는 "그 사이트에 들어갔다" 대신 "이 프로필의 방문 기록에 그 주소가 있고, `visit_type` 2, 방문 시각은 X(UTC) 이다" 처럼 씁니다.

## 시각 해석

- `moz_historyvisits.visit_date` 는 1970년 1월 1일 00:00 UTC 부터 센 마이크로초입니다. 파이어폭스에서는 이 단위를 PRTime 이라고 부릅니다[2].
- 현지 시각이 아닙니다. 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.
- `moz_places.last_visit_date`, `moz_bookmarks.dateAdded`·`lastModified`, `moz_annos.dateAdded`·`lastModified` 도 같은 단위로 알려져 있으므로, 실제 데이터에서 다른 시각과 맞춰 확인합니다.
- 여러 기록을 한 시간 축에 놓을 때는 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 을 따릅니다.

## 함정과 한계

- **원본을 브라우저로 열지 않습니다.** 파이어폭스로 프로필을 열면 방문 기록이 바뀝니다. 해시를 기록한 사본으로 분석합니다.
- **실행 중에는 WAL 을 함께 봅니다.** SQLite 는 아직 본 파일에 합치지 않은 변경을 `-wal` 파일에 둘 수 있습니다. 최근 방문이 `places.sqlite-wal` 에만 있을 수 있습니다. [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 를 참고합니다.
- **`moz_places` 에 방문 행이 없는 주소가 있습니다.** 즐겨찾기만 하고 방문한 적 없는 주소, 다른 페이지가 참조만 한 주소도 `moz_places` 에 남습니다. `moz_places` 행 수를 방문 횟수로 오해하지 않습니다.
- **기록을 지우면 행이 표에서 사라집니다.** 지운 행의 조각이 SQLite 빈 공간이나 WAL 에 남을 수 있습니다. 옛 방문을 찾으려면 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md), 섀도 복사본, 메모리도 봅니다.
- **사생활 보호 창은 방문 행을 남기지 않는 것으로 알려져 있습니다.** [시크릿 모드로 무엇을 했나](../../../04-scenarios/activity/private-browsing.md) 를 참고합니다.

## 직접 분석해 보기

### 헥스로 한 번

`visit_date` 는 마이크로초 정수입니다. SQLite 레코드는 정수를 빅엔디언으로 저장합니다. 아래는 2024-01-01 00:00:00 UTC 를 명세대로 만든 예시입니다. 특정 기기에서 나온 값이 아닙니다.

```
00 06 0D D7 10 21 20 00    = 1704067200000000 (마이크로초)
1704067200000000 ÷ 1,000,000 = 1704067200 초 (1970-01-01 부터)
→ 2024-01-01 00:00:00 UTC
```

### 공개 도구로 한 번

`places.sqlite` 와 함께 `places.sqlite-wal` 도 사본으로 뜬 뒤, SQLite 명령줄 도구를 읽기 전용으로 열어 아래처럼 조회합니다.

```sql
SELECT p.url, p.title, v.visit_type,
       datetime(v.visit_date / 1000000, 'unixepoch') AS visited_utc
FROM moz_historyvisits v
JOIN moz_places p ON p.id = v.place_id
ORDER BY v.visit_date;
```

- `visit_date` 를 1,000,000 으로 나누면 1970년 기준 초가 됩니다. `unixepoch` 로 UTC 시각을 얻습니다.
- 방문 유형별로 세어 보면 사용자가 직접 친 방문(값 2)과 끼워 넣은 방문(값 4)의 비율을 볼 수 있습니다.
- DB Browser for SQLite 같은 범용 뷰어로 같은 표를 볼 수 있습니다. 브라우저 기록 전용 공개 도구는 시각 변환과 방문 유형 이름을 대신 붙여 줍니다. 도구 결과는 위 조회 결과와 한 번 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 쿠키 | 같은 도메인의 쿠키가 방문 시각 무렵에 생겼는지 봅니다 | [쿠키 (cookies.sqlite)](cookies-sqlite.md) |
| 캐시 | 방문한 페이지의 응답을 실제로 받았는지 봅니다 | [캐시 (cache2)](cache2.md) |
| 세션 복원 | 방문 시각에 열려 있던 탭을 봅니다 | [세션 복원 (sessionstore.jsonlz4)](sessionstore-jsonlz4.md) |
| 양식 기록 | 같은 시간대에 어떤 양식에 무엇을 쳤는지 봅니다 | [양식 기록 (formhistory.sqlite)](formhistory-sqlite.md) |
| $MFT | 다운로드한 파일이 디스크에 실제로 있는지, 그 시각을 봅니다 | [$MFT](../../filesystem/mft.md) |
| 다른 브라우저 방문 기록 | 같은 사이트를 다른 브라우저로 썼는지 봅니다 | [크롬 계열 방문 기록](../chrome-edge-whale/history.md) |

웹 사용 전체를 재구성하는 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) 에 있습니다.

## 실습

파이어폭스를 쓴 공개 시험 데이터(NIST CFReDS 등)에서 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. `moz_historyvisits` 에서 `visit_type` 이 2(TYPED) 인 방문만 골라 시간순으로 늘어놓습니다. 사용자가 손으로 연 사이트는 무엇입니까?
2. 한 방문을 골라 `from_visit` 을 따라 앞 방문으로 거슬러 올라갑니다. 어느 페이지에서 링크를 눌러 왔습니까?
3. `moz_places` 의 `visit_count` 가 가장 큰 주소는 무엇입니까? 그 주소의 첫 방문과 마지막 방문 시각은 언제입니까?
4. 다운로드 주석(`moz_annos` 의 `downloads/destinationFileURI`)에서 내려받은 파일의 저장 위치를 모읍니다. 그 파일이 $MFT 에 있습니까?

## 참고 문헌

1. Mozilla, *nsPlacesTables.h* (파이어폭스 소스, main 가지 — 표와 열 정의). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/components/places/nsPlacesTables.h
2. Mozilla, *nsINavHistoryService.idl* (파이어폭스 소스, main 가지 — 방문 유형·출처 값, PRTime 정의). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/components/places/nsINavHistoryService.idl
3. *Mozilla Firefox — Forensics Wiki* (파일 위치, downloads.sqlite 이력, 시각 단위). https://forensics.wiki/mozilla_firefox/
4. Mozilla, *DownloadHistory.sys.mjs* (파이어폭스 소스, main 가지 — 다운로드 주석 이름과 내용, 사생활 보호 창 다운로드 제외). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/components/downloads/DownloadHistory.sys.mjs
