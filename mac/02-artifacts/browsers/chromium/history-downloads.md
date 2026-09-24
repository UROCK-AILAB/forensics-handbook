---
title: "방문·다운로드 기록"
parent: "크롬·엣지·웨일"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1240
---

# 방문·다운로드 기록 (History)

Chromium 계열 브라우저는 프로필 폴더의 `History` SQLite 파일에 방문한 URL과 방문 한 건 한 건, 받은 파일과 그 파일까지 거친 URL을 남기고, 시각은 1601-01-01 UTC 기준 마이크로초로 적어서 기준만 맞추면 웹 사용과 다운로드를 한 시간축에 놓을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

브라우저는 `History` 파일에 방문을 쌓고, 같은 파일에 다운로드 목록도 함께 둡니다 [1][3]. 방문 기록은 URL 하나당 한 행인 `urls` 표와 방문 한 번당 한 행인 `visits` 표로 나뉘고, `visits.url` 이 `urls.id` 를 가리킵니다 [1]. 다운로드는 `downloads` 표에 한 건씩 남고, 그 파일을 받기까지 거친 URL은 `downloads_url_chains` 표에 순서대로 남습니다 [3].

프로필 폴더에는 `History` 말고도 오래된 방문을 담는 `Archived History` 와 방문한 URL의 지문만 모아 둔 `Visited Links` 가 있습니다 [1][5]. `Archived History` 는 오래된 버전을 설명한 자료에 나오는 파일이라서, 최신 브라우저 버전에서도 만들어지는지는 확인하지 못했습니다. 프로필 폴더를 찾는 법은 [맥에서의 위치와 프로필 (Profiles)](profiles.md)에서 다룹니다.

## 위치와 버전별 차이

```
<사용자 데이터 폴더>/<프로필>/History
<사용자 데이터 폴더>/<프로필>/Archived History
<사용자 데이터 폴더>/<프로필>/Visited Links
```

macOS 10.15 Catalina 이후 버전에 따라 이 파일이 달라진다는 자료는 찾지 못했고, 출처에 나오는 변화는 모두 브라우저 버전에 따른 것입니다.

| 브라우저 쪽 변화 | 내용 |
|---|---|
| 다운로드 시각 기준 | 예전 `downloads.start_time` 은 1970 기준 초(time_t)였고, 이후 1601 기준 마이크로초로 옮겨졌습니다 [1][3] |
| 다운로드 URL 칸 | 예전 `downloads` 표에는 `url`·`full_path` 칸이 있었고, 버전 26부터 `target_path` 칸과 `downloads_url_chains` 표로 나뉘었습니다 [1] |
| 다운로드 상태 값 | 옛 상태 값 3(BUG_140687)은 새 버전에서 INTERRUPTED로 옮겨집니다 [3] |

아래 표 구성은 Chromium 소스의 현재 버전(2026-09 시점) 기준입니다. 오래된 브라우저가 만든 DB에는 일부 칸이 없을 수 있어서, 먼저 검체 DB의 `.schema` 로 칸을 확인합니다.

## 구조

### urls 와 visits

`urls` 표에서 확인한 칸은 `id`, `url`, `title` 이고 [1], 방문 횟수나 마지막 방문 시각을 담는 칸은 연 자료로 확인하지 못했습니다. `visits` 표의 칸은 아래와 같습니다 [4].

```
id, url, visit_time, from_visit, external_referrer_url, transition,
segment_id, visit_duration, incremented_omnibox_typed_score, opener_visit,
originator_cache_guid, originator_visit_id, originator_from_visit,
originator_opener_visit, is_known_to_sync, consider_for_ntp_most_visited,
visited_link_id, app_id
```

| 칸 | 뜻 |
|---|---|
| `url` | `urls.id` 를 가리킵니다 [1] |
| `visit_time` | 방문 시각, 1601-01-01 UTC 기준 마이크로초 [1] |
| `from_visit` | 이 방문을 부른 이전 방문의 id이고, 리디렉션 연쇄를 따라갈 때 씁니다. DB에 없는 id를 가리키기도 합니다 [4] |
| `opener_visit` | 새 탭이나 새 창으로 이 방문을 연 방문의 id [4] |
| `transition` | 어떻게 이 페이지에 왔는지를 적은 값(아래 표) [2] |
| `visit_duration` | 방문을 연 때부터 닫거나 끝낸 때까지의 길이이고, 탭이 떠 있기만 한 시간도 들어갑니다 [6]. 소스는 이 값을 시간 간격 형식(`BindTimeDelta`)으로 적는데 [4], 저장 단위는 소스에서 따로 확인하지 못해서 검체 값의 크기로 한 번 확인합니다 |
| `originator_*`, `is_known_to_sync` | 칸 이름으로 보아 다른 기기에서 동기화된 방문과 관련된 칸이고, 어떻게 채워지는지는 확인하지 못했습니다 [4] |

`visit_source` 표에는 `id` 와 `source` 두 칸이 있고, `source` 는 방문이 어디서 왔는지를 나타냅니다 [4]. 값은 0 SOURCE_SYNCED(다른 곳에서 동기화), 1 SOURCE_BROWSED(사용자가 탐색), 2 SOURCE_EXTENSION(확장이 추가), 3 SOURCE_FIREFOX_IMPORTED, 4 SOURCE_IE_IMPORTED, 5 SOURCE_SAFARI_IMPORTED, 6 SOURCE_ACTOR, 7 SOURCE_OS_MIGRATION_IMPORTED 이고, 소스는 이미 있는 번호를 바꾸지 말라고 적어 둡니다 [6]. 방문을 넣을 때 출처가 SOURCE_BROWSED가 아닌 경우에만 이 표에 행을 만들어서 [4], `visit_source` 에 행이 없는 방문은 이 브라우저에서 탐색한 방문으로 읽습니다.

### transition 값

`transition` 은 PageTransition 값이고, 하위 8비트(마스크 `0xFF`)가 핵심 종류, 그 위의 비트가 한정자입니다 [2].

| 핵심 종류 | 값 | | 한정자 | 값 |
|---|---|---|---|---|
| LINK | 0 | | BLOCKED | `0x00800000` |
| TYPED | 1 | | FORWARD_BACK | `0x01000000` |
| AUTO_BOOKMARK | 2 | | FROM_ADDRESS_BAR | `0x02000000` |
| AUTO_SUBFRAME | 3 | | HOME_PAGE | `0x04000000` |
| MANUAL_SUBFRAME | 4 | | FROM_API | `0x08000000` |
| GENERATED | 5 | | CHAIN_START | `0x10000000` |
| AUTO_TOPLEVEL | 6 | | CHAIN_END | `0x20000000` |
| FORM_SUBMIT | 7 | | CLIENT_REDIRECT | `0x40000000` |
| RELOAD | 8 | | SERVER_REDIRECT | `0x80000000` |
| KEYWORD | 9 | | | |
| KEYWORD_GENERATED | 10 | | | |

리디렉션 마스크는 CLIENT_REDIRECT와 SERVER_REDIRECT를 합친 값이고, 한정자 마스크는 `0xFFFFFF00` 입니다 [2].

### downloads 와 딸린 표

`downloads` 표의 칸은 아래와 같습니다 [3].

```
id, guid, current_path, target_path, start_time, received_bytes, total_bytes,
state, danger_type, interrupt_reason, hash, end_time, opened, last_access_time,
transient, referrer, site_url, embedder_download_data, tab_url, tab_referrer_url,
http_method, by_ext_id, by_ext_name, by_web_app_id, etag, last_modified,
mime_type, original_mime_type
```

`start_time`, `end_time`, `last_access_time` 은 1601 기준 마이크로초입니다 [3]. `state` 는 0이 진행 중(IN_PROGRESS), 1이 완료(COMPLETE), 2가 취소(CANCELLED), 3이 옛 값 BUG_140687, 4가 중단(INTERRUPTED)이고, 소스는 이 번호가 DB에 저장되니 바꾸지 말라고 적어 둡니다 [7]. `danger_type` 도 같은 파일에 번호가 정해져 있어서 0 NOT_DANGEROUS, 1 DANGEROUS_FILE, 2 DANGEROUS_URL, 3 DANGEROUS_CONTENT, 4 MAYBE_DANGEROUS_CONTENT, 5 UNCOMMON_CONTENT, 6 USER_VALIDATED, 7 DANGEROUS_HOST, 8 POTENTIALLY_UNWANTED 처럼 이어지고, 그 뒤 값은 브라우저 버전에 따라 늘어나서 검체 버전의 소스로 확인합니다 [7]. `interrupt_reason` 의 숫자 뜻은 확인하지 못했습니다. `by_ext_id`·`by_ext_name` 은 칸 이름으로 보아 확장이 시작한 다운로드일 때 그 확장을 적는 칸이고 [3], 확장 쪽 흔적은 [확장 (Extensions)](extensions.md)에서 다룹니다.

`downloads_url_chains` 표는 `id`, `chain_index`, `url` 세 칸이고, `(id, chain_index)` 가 기본 키, `id` 가 `downloads.id` 입니다 [3]. 한 다운로드에 여러 행이 붙을 수 있고, `chain_index` 순서대로 읽으면 리디렉션을 포함해 파일에 닿기까지 거친 URL이 나옵니다 [3]. `downloads_slices` 표(`download_id`, `offset`, `received_bytes`, `finished`)는 파일을 여러 조각으로 나눠 받거나 이어 받을 때 조각 정보를 적습니다 [3].

### Visited Links

`Visited Links` 는 머리의 매직 `VLnk` 다음에 URL 지문 목록이 이어지는 파일이고, 시각 정보는 없습니다 [1]. 방문 시점은 이 파일로 알 수 없어서 `History` 의 시각과 함께 봅니다.

## 증거로서 의미

**증명하는 것.** 이 프로필의 `History` 에 이 URL을 이 시각에 연 방문 기록이 있고, `transition` 으로 그 방문이 주소창 입력(TYPED)인지 링크(LINK)인지 리디렉션인지를 가릴 수 있다는 점입니다 [2]. `downloads` 와 `downloads_url_chains` 는 어떤 경로에 어떤 파일을 저장하려 했는지, 그 파일이 어느 URL들을 거쳐 왔는지, 다운로드가 완료됐는지 중단됐는지를 알려 줍니다 [3].

**증명하지 못하는 것.** 방문 기록이 있다고 사람이 그 화면을 봤다고 단정할 수는 없고, 리디렉션이나 하위 프레임(AUTO_SUBFRAME)처럼 사용자가 직접 고르지 않은 방문도 행으로 남습니다 [2]. `visit_source` 가 0(SOURCE_SYNCED)인 방문은 소스 주석대로 다른 곳에서 동기화된 방문이라서 이 맥에서 직접 연 것이 아닐 수 있습니다 [6]. 다운로드 행은 받은 파일이 지금 디스크에 있는지, 사용자가 그 파일을 열었는지까지는 알려 주지 않습니다.

보고서에는 "이 프로필의 방문 기록에 이 시각(UTC)에 이 URL을 주소창 입력으로 연 기록이 있다", "이 시각에 이 URL에서 받은 파일을 이 경로로 저장한 다운로드 기록이 있고 상태 값은 완료다" 처럼 씁니다.

## 시각 해석

`visit_time` 과 다운로드 시각 칸은 1601-01-01 00:00:00 UTC를 기준으로 센 마이크로초이고 [1][3], 흔히 WebKit 시각 또는 Chrome 시각이라고 부릅니다. 맥 절대 시각(2001 기준)이나 유닉스 시각(1970 기준)과 기준이 달라서, 1,000,000으로 나눠 초로 바꾼 뒤 1601과 1970 사이의 초 `11644473600` 을 빼면 유닉스 시각이 됩니다. 기준끼리의 관계는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 모아 두었습니다.

명세로 만든 예시로 보면, `13348540800000000` 은 1,000,000으로 나눈 `13348540800` 에서 `11644473600` 을 뺀 유닉스 시각 `1704067200` 이고, 이 값은 2024-01-01 00:00:00 UTC입니다. 값이 모두 UTC 기준이라서 현지 시각은 [시간대와 시계 설정 (Time Zone·NTP)](../../system-account/time-zone.md)을 보고 따로 바꿉니다.

오래된 DB를 다룰 때는 `downloads.start_time` 이 1970 기준 초였던 시기가 있어서 [1][3], 값의 자릿수가 다른 행보다 훨씬 적으면 1601 기준 마이크로초가 아니라 유닉스 초인지 먼저 의심합니다.

## 함정과 한계

- **동기화된 방문.** `visit_source` 와 `originator_*` 칸이 동기화와 관련되어 있어서 [4], 이 칸을 보지 않고 모든 방문을 이 맥에서 일어난 일로 적으면 틀릴 수 있습니다.
- **transition 이 음수로 보일 때.** SERVER_REDIRECT가 32비트의 맨 위 비트라서 부호 있는 32비트로 읽으면 음수가 됩니다. 명세로 만든 예시로 `0xA0000000`(SERVER_REDIRECT와 CHAIN_END, 핵심 종류 LINK)은 부호 없이 `2684354560`, 부호 있게 읽으면 `-1610612736` 입니다. 현재 소스는 이 값을 64비트 정수로 적지만 [4], 오래된 버전이나 도구에 따라 음수로 보일 수 있어서 값이 음수여도 하위 8비트와 한정자 비트를 그대로 풀어 봅니다.
- **끊긴 from_visit.** `from_visit` 이 DB에 없는 id를 가리키는 경우가 있어서 [4], 연쇄가 끊겼다는 점만으로 기록을 지웠다고 보지 않습니다.
- **모르는 숫자.** `interrupt_reason` 의 숫자 뜻과 `danger_type` 의 새 값은 이 페이지에 적지 않았습니다. 도구가 이 숫자를 글자로 바꿔 보여 주면 어떤 버전의 표를 썼는지 확인합니다.
- **검색어 표.** 검색어를 담는 `keyword_search_terms` 표의 칸은 확인하지 못해서 이 페이지에 적지 않았습니다.
- **지운 기록.** 지운 행을 찾으려면 SQLite 파일의 빈 공간을 살펴야 하고, 그 방법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)와 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.
- **격리 기록과의 연결.** 브라우저로 받은 파일의 격리 속성·격리 이벤트 DB와 이 표를 잇는 방법은 이 페이지의 출처에 없어서 URL과 시각으로 맞춰 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

명세로 만든 예시로 `transition` 값 `805306369` 를 풀어 봅니다. 16진수로 `0x30000001` 이고, 하위 8비트 `0x01` 은 TYPED, 위쪽 `0x30000000` 은 CHAIN_START(`0x10000000`)와 CHAIN_END(`0x20000000`)를 합친 값입니다 [2]. 사용자가 주소창에 입력해 연 방문이고, 리디렉션 없이 연쇄가 이 한 건에서 시작하고 끝났다는 뜻입니다.

시각 값도 헥스로 찾아볼 수 있습니다. 위의 예시 시각 `13348540800000000` 은 16진수로 `0x002F6C6D58A76000` 이고, SQLite는 정수를 빅 엔디언으로 적어서 레코드 안에서는 `00 2F 6C 6D 58 A7 60 00` 으로 보입니다. 레코드를 헥스로 따라가는 방법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다. `Visited Links` 를 헥스로 열면 첫 네 바이트가 `56 4C 6E 6B`(`VLnk`)인지 확인합니다 [1].

### SQL로 한 번

원본을 건드리지 않도록 `History` 사본을 만들어 `sqlite3` 같은 공개 도구로 엽니다. 방문은 아래처럼 `urls` 와 이어 읽습니다.

```sql
SELECT v.id,
       datetime(v.visit_time / 1000000 - 11644473600, 'unixepoch') AS visit_utc,
       u.url, u.title,
       v.transition & 255 AS core_type,
       printf('0x%08X', v.transition & 0xFFFFFF00) AS qualifiers,
       v.from_visit, v.opener_visit
FROM visits v JOIN urls u ON v.url = u.id
ORDER BY v.visit_time;
```

다운로드는 `downloads_url_chains` 를 붙여 거친 URL을 순서대로 봅니다.

```sql
SELECT d.id,
       datetime(d.start_time / 1000000 - 11644473600, 'unixepoch') AS start_utc,
       datetime(d.end_time / 1000000 - 11644473600, 'unixepoch') AS end_utc,
       d.target_path, d.state, d.received_bytes, d.total_bytes,
       d.by_ext_id, c.chain_index, c.url
FROM downloads d LEFT JOIN downloads_url_chains c ON c.id = d.id
ORDER BY d.start_time, c.chain_index;
```

오래된 DB에서 칸이 없다는 오류가 나면 `.schema downloads` 로 칸을 확인하고 해당 칸을 뺍니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md) | `downloads` 의 URL·시각과 격리 이벤트 DB의 URL·시각을 맞춰 봅니다 |
| [다운로드 출처 속성 (kMDItemWhereFroms)](../../filesystem/where-froms.md) | `target_path` 에 있는 파일의 출처 속성과 `downloads_url_chains` 를 비교합니다 |
| [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) | 받은 파일이 만들어지고 옮겨지거나 지워진 흔적을 찾습니다 |
| [쿠키와 저장된 암호 (Cookies·Login Data)](cookies-login-data.md) | 방문한 사이트의 쿠키 생성·접근 시각을 방문 시각과 맞춰 봅니다 |
| [사파리 (Safari)](../safari/index.md), [파이어폭스 (Firefox)](../firefox.md) | 같은 사용자가 다른 브라우저로 한 웹 사용을 함께 봅니다 |
| [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) | 방문·다운로드 시각을 실행·파일 사용 기록과 한 시간축에 놓습니다 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 프로필마다 `History` 의 `visits` 행 수와 가장 이른·늦은 `visit_time` 을 UTC로 적어 보세요.
2. `transition` 의 핵심 종류가 TYPED인 방문만 골라 URL 목록을 만들어 보세요.
3. 다운로드 한 건을 골라 `downloads_url_chains` 로 거친 URL을 순서대로 적고, `target_path` 의 파일이 아직 있는지 확인해 보세요.
4. 같은 다운로드가 격리 이벤트 DB에도 있는지 URL과 시각으로 찾아보세요.

## 참고 문헌

1. Forensics Wiki, "Google Chrome" — https://forensics.wiki/google_chrome/
2. Chromium 소스, ui/base/page_transition_types.h — https://chromium.googlesource.com/chromium/src/+/HEAD/ui/base/page_transition_types.h
3. Chromium 소스, components/history/core/browser/download_database.cc — https://chromium.googlesource.com/chromium/src/+/HEAD/components/history/core/browser/download_database.cc
4. Chromium 소스, components/history/core/browser/visit_database.cc — https://chromium.googlesource.com/chromium/src/+/HEAD/components/history/core/browser/visit_database.cc
5. ForensicArtifacts, webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
6. Chromium 소스, components/history/core/browser/history_types.h — https://chromium.googlesource.com/chromium/src/+/HEAD/components/history/core/browser/history_types.h
7. Chromium 소스, components/history/core/browser/download_constants.h — https://chromium.googlesource.com/chromium/src/+/HEAD/components/history/core/browser/download_constants.h
