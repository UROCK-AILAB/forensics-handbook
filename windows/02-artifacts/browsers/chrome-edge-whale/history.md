---
title: "방문·다운로드 기록"
parent: "크롬 계열 브라우저"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1600
---

# 방문·다운로드 기록 (History)

## 한 줄 요약

크롬 계열 브라우저는 프로필 폴더의 `History` 파일에 방문 기록과 다운로드 기록을 남깁니다. 이 파일은 SQLite 데이터베이스이고, 방문은 주소마다 한 행(`urls`)과 방문마다 한 행(`visits`)으로 나눠 적으며, 다운로드는 `downloads` 표와 주소 사슬 표(`downloads_url_chains`)에 적습니다. 시각 칸은 1601-01-01 0시(UTC)부터 센 마이크로초입니다.

## 무엇을 기록하나 · 왜 생기나

브라우저는 방문 기록 화면, 주소창 추천, 새 탭의 자주 가는 사이트를 보여 주려고 이 기록을 쓰며, 다운로드 목록 화면도 이 파일을 읽습니다. 기록은 사용자가 지우거나 보관 기한이 지나야 사라집니다.

| 표 | 한 행이 뜻하는 것 | 주요 내용 |
|---|---|---|
| `urls` | 주소 하나 | 주소, 제목, 방문 횟수, 주소창 입력 횟수, 마지막 방문 시각 |
| `visits` | 방문 한 번 | 방문 시각, 어떻게 왔는지(전환 유형), 앞 방문, 머문 길이 |
| `visit_source` | 직접 방문이 아닌 방문 하나 | 동기화·확장 프로그램·가져오기로 들어온 방문 표시 |
| `keyword_search_terms` | 검색 한 번 | 주소창에서 검색 엔진으로 보낸 검색어 |
| `downloads` | 다운로드 하나 | 저장 경로, 시작·끝 시각, 받은 크기, 상태, 위험 판정, 해시 |
| `downloads_url_chains` | 다운로드 주소 사슬의 한 칸 | 처음 요청한 주소부터 실제로 받은 주소까지 |

이 밖에도 `meta`, `segments`, `segment_usage` 같은 표가 있고 브라우저 판이 올라가면서 표가 늘어납니다. 이 페이지는 위 여섯 표를 다룹니다.

시크릿 창에서 연 페이지는 이 파일에 남지 않습니다. 이 점과 기록의 한계는 [크롬 계열 브라우저](index.md) 허브에서 다룹니다.

## 위치와 버전별 차이

### 위치

`History` 는 프로필 폴더(`Default`, `Profile 1` 등) 바로 아래 있습니다. 브라우저별 `User Data` 폴더 위치는 [크롬 계열 브라우저](index.md) 허브에 정리했습니다. 프로필 이름과 폴더를 잇는 법은 [프로필 폴더와 계열 브라우저 구분](../../../01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md)에서 다룹니다.

같은 폴더에 `History-journal` 이 함께 있습니다. 이 파일은 SQLite 롤백 저널이라서 두 파일을 함께 수집합니다. 저널을 어떻게 읽는지는 [WAL과 롤백 저널](../../../01-foundations/database-log-formats/sqlite/wal-journal-shm.md)에서 다룹니다.

### 버전별 차이

위치와 구조는 Windows 버전과 상관이 없습니다. 브라우저 판에 따라 달라집니다.

| 판 | 달라진 점 | 근거 |
|---|---|---|
| Chrome 37 이전 | 3개월이 지난 방문 기록을 `Archived History` 파일로 옮겨 두었습니다 | Benson (2014) |
| Chrome 37 부터 | 브라우저가 시작할 때 `Archived History` 를 지웁니다 | Benson (2014) |
| 현재 소스 | 90일이 지난 기록을 오래된 기록으로 보고 지웁니다(`kExpireDaysThreshold = 90`) | Chromium `history_backend.h` |
| 판이 올라갈 때마다 | `visits`·`downloads` 에 열이 늘어납니다. 동기화 방문을 가리는 `originator_cache_guid` 가 그런 예입니다 | Chromium 소스 |
| 옛 판의 다운로드 상태 | 상태 값 3 은 옛 버그 때 쓰던 값입니다. 지금 코드는 이 값을 4(중단)로 바꿉니다 | Chromium `download_database.cc` |

스키마 판 번호는 `meta` 표에 있으므로 검체마다 먼저 확인합니다. 열 목록은 `sqlite_master` 의 `CREATE TABLE` 문으로 확인하는데, 아래 표는 2026년 9월 Chromium 소스 기준이라 옛 판에는 없는 열이 있습니다. Edge·Whale 도 같은 Chromium 코드로 이 파일을 만들지만 제조사가 표를 더할 수 있으니 표 목록부터 봅니다.

## 구조

SQLite 페이지와 레코드를 읽는 법은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md)와 [파일·페이지 구조](../../../01-foundations/database-log-formats/sqlite/b-tree-record-format.md)에서 다룹니다. 여기서는 표와 열의 뜻만 다룹니다.

### urls — 주소마다 한 행

| 열 | 뜻 |
|---|---|
| `id` | 주소 번호입니다. `visits.url` 과 `keyword_search_terms.url_id` 가 이 번호를 가리킵니다 |
| `url` | 주소 |
| `title` | 페이지 제목 |
| `visit_count` | 방문 횟수 |
| `typed_count` | 주소창에 직접 입력해서 온 횟수 |
| `last_visit_time` | 마지막 방문 시각 |
| `hidden` | 1 이면 주소창 자동 완성에 쓰지 않는 주소입니다 |

소스 주석은 `visit_count` 가 `visits` 의 행 수와 "자주 같지만 늘 같지는 않다" 고 적습니다. `id` 는 AUTOINCREMENT 로 만드는데, 소스 주석에 따르면 동기화 때문에 번호를 다시 쓰지 않으려는 것입니다.

### visits — 방문마다 한 행

| 열 | 뜻 |
|---|---|
| `id` | 방문 번호. AUTOINCREMENT 라서 새 행일수록 커집니다 |
| `url` | `urls.id` |
| `visit_time` | 방문 시각 |
| `from_visit` | 이 방문으로 이어진 앞 방문의 번호 |
| `transition` | 전환 유형(아래 절) |
| `visit_duration` | 머문 길이. 마이크로초 단위이고 기본값은 0 입니다 |
| `opener_visit` | 이 페이지를 연 방문의 번호 |
| `originator_cache_guid` | 동기화로 들어온 방문이면, 처음 방문한 기기의 식별자 |
| `is_known_to_sync` | 동기화가 아는 방문이면 1. 다른 기기에서 받은 방문과 이 기기에서 동기화로 보낸 방문이 모두 해당합니다 |

소스 주석에 따르면 만료 작업 뒤에는 `from_visit`·`opener_visit` 가 없는 방문 번호를 가리킬 수 있습니다.

### transition — 전환 유형

`transition` 은 32비트 값입니다. 아래 8비트(`& 0xFF`)가 기본 유형입니다. 위 24비트(`& 0xFFFFFF00`)는 덧붙은 표시이며, 값과 뜻은 Chromium `page_transition_types.h` 에서 옮겼습니다.

| 기본 유형 | 이름 | 뜻 |
|---|---|---|
| 0 | LINK | 다른 페이지의 링크를 눌러 왔습니다 |
| 1 | TYPED | 주소창에 주소를 입력해서 왔습니다 |
| 2 | AUTO_BOOKMARK | 브라우저 화면의 추천을 눌러 왔습니다 |
| 3 | AUTO_SUBFRAME | 최상위가 아닌 프레임이 자동으로 읽었습니다 |
| 4 | MANUAL_SUBFRAME | 사용자가 프레임 안에서 이동했고, 뒤로 가기 목록에 들어갔습니다 |
| 5 | GENERATED | 주소창에 입력한 뒤 주소처럼 보이지 않는 항목(검색 등)을 골랐습니다 |
| 6 | AUTO_TOPLEVEL | 최상위 창에 자동으로 읽은 내용입니다 |
| 7 | FORM_SUBMIT | 폼에 값을 넣어 보냈습니다 |
| 8 | RELOAD | 새로 고침을 눌렀거나, 주소창에서 같은 주소로 Enter 를 눌렀습니다 |
| 9 | KEYWORD | 기본이 아닌 검색 엔진의 키워드로 만든 주소입니다 |
| 10 | KEYWORD_GENERATED | 키워드 검색에 딸려 생긴 방문입니다 |

| 표시 값 | 이름 | 뜻 |
|---|---|---|
| 0x00800000 | BLOCKED | 관리 대상 사용자가 막힌 주소에 가려 했습니다 |
| 0x01000000 | FORWARD_BACK | 앞으로·뒤로 버튼을 썼습니다 |
| 0x02000000 | FROM_ADDRESS_BAR | 주소창에서 시작한 이동입니다 |
| 0x04000000 | HOME_PAGE | 홈 페이지로 가는 이동입니다 |
| 0x08000000 | FROM_API | 외부 앱이 시작한 이동입니다. 정확한 뜻은 브라우저마다 다릅니다 |
| 0x10000000 | CHAIN_START | 리다이렉트 사슬의 시작입니다 |
| 0x20000000 | CHAIN_END | 리다이렉트 사슬의 끝입니다 |
| 0x40000000 | CLIENT_REDIRECT | 자바스크립트나 meta refresh 로 넘어갔습니다 |
| 0x80000000 | SERVER_REDIRECT | 서버의 HTTP 헤더로 넘어갔습니다 |

예를 들어 805306369 는 0x30000001 입니다. 기본 유형은 1(TYPED)이고 표시는 CHAIN_START 와 CHAIN_END 이므로, 리다이렉트 없이 주소를 입력해 온 방문이라는 뜻입니다.

### visit_source — 방문의 출처

소스 주석에 따르면 사용자가 직접 방문한 행은 공간을 아끼려고 이 표에 적지 않습니다. 그래서 `visits.id` 가 이 표에 없으면 이 브라우저에서 직접 방문한 것입니다.

| `source` | 뜻 |
|---|---|
| 0 | 다른 곳에서 동기화로 들어왔습니다 |
| 1 | 사용자가 방문했습니다 |
| 2 | 확장 프로그램이 넣었습니다 |
| 3·4·5 | Firefox·IE·Safari 에서 가져왔습니다 |
| 6 | 소스 이름은 `SOURCE_ACTOR` 입니다. 주석은 "GLIC actor" 가 넣었다고만 적습니다 |
| 7 | 소스 이름은 `SOURCE_OS_MIGRATION_IMPORTED` 입니다. 설명 주석은 없습니다 |

### keyword_search_terms — 검색어

| 열 | 뜻 |
|---|---|
| `keyword_id` | 검색 엔진 번호. 검색 엔진 목록은 [자동완성·폼 기록 (Web Data)](web-data-autofill.md) 쪽 파일에 있습니다 |
| `url_id` | 검색 결과 주소의 `urls.id` |
| `term` | 입력한 검색어 |
| `normalized_term` | 소문자로 바꾸고 공백을 합친 검색어 |

검색 시각은 이 표에 없습니다. `url_id` 로 `urls`·`visits` 와 이어서 얻습니다.

### downloads · downloads_url_chains — 다운로드

| 열 | 뜻 (Chromium `download_row.h` 주석) |
|---|---|
| `id` · `guid` | 다운로드 번호와 GUID |
| `current_path` | 지금 파일이 있는 경로. 받는 중이거나 중단됐으면 `target_path` 와 다를 수 있습니다 |
| `target_path` | 다 받았을 때 파일이 놓일 경로 |
| `start_time` · `end_time` | 받기 시작한 시각, 끝난 시각 |
| `received_bytes` · `total_bytes` | 지금까지 받은 바이트, 전체 바이트 |
| `state` | 상태(아래 표) |
| `danger_type` | 위험 판정(아래 표) |
| `interrupt_reason` | 중단 이유. 상태가 중단일 때 씁니다 |
| `hash` | 받은 내용의 SHA-256 원시 바이트. 16진 문자열이 아닙니다. 일부만 받았으면 일부의 해시입니다 |
| `opened` | 브라우저에서 이 파일을 연 적이 있으면 1 |
| `last_access_time` | 마지막으로 접근한 시각 |
| `transient` | 1 이면 화면에 보이지 않고 끝나면 정리되는 다운로드 |
| `referrer` | 참조 주소 |
| `site_url` | 다운로드를 시작한 사이트 |
| `tab_url` · `tab_referrer_url` | 다운로드를 시작한 탭의 주소와 그 탭의 참조 주소 |
| `by_ext_id` · `by_ext_name` | 다운로드를 만든 확장 프로그램 |
| `mime_type` · `original_mime_type` | 내용 형식. 앞의 것은 추정일 수 있습니다 |

`downloads_url_chains` 는 `id`·`chain_index`·`url` 세 열이고, `id` 는 `downloads.id` 입니다. `chain_index` 가 0 인 주소가 처음 요청한 주소이고, 번호가 가장 큰 주소가 실제로 데이터를 받은 주소입니다.

| `state` | 뜻 |
|---|---|
| 0 | 받는 중 |
| 1 | 완료 |
| 2 | 취소 |
| 3 | 옛 버그 값. 지금 코드는 4 로 바꿉니다 |
| 4 | 중단 |

| `danger_type` | 뜻 (일부) |
|---|---|
| 0 | 안전 |
| 1 | 시스템에 위험한 파일 형식 |
| 2 | Safe Browsing 이 악성 파일로 이어지는 주소로 판정 |
| 3 | Safe Browsing 이 악성 내용으로 판정 |
| 4 | 악성일 수 있음(검사가 끝나기 전 등) |
| 5 | 검사했지만 판단할 자료가 모자람 |
| 6 | 다른 위험 판정이 났지만 사용자가 그래도 받기로 함 |
| 7 | 주로 악성 파일을 퍼뜨리는 호스트에서 받음 |
| 8 | 브라우저·PC 설정을 바꾸는 앱·확장 |

값 9 이후는 관리 정책·기업 검사와 관련된 값입니다. 전체 목록은 Chromium `download_constants.h` 에 있습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 프로필에 이 주소의 방문 기록이 있습니다 | 이 PC 에서 방문했는지. 동기화된 방문일 수 있습니다 |
| 기록된 시각 무렵에 그 페이지를 불러왔습니다 (시계가 맞다면) | 사람이 화면을 보고 있었는지. 누가 키보드 앞에 있었는지 |
| 어떻게 왔는지: 주소 입력, 링크, 폼 전송, 리다이렉트 | 페이지에서 무엇을 읽고 썼는지 |
| 어떤 검색어로 검색했는지 | 90일보다 오래된 방문 |
| 어떤 주소에서 어떤 경로로 파일을 받았는지, 얼마나 받았는지 | 그 파일이 지금도 디스크에 있는지 |
| 브라우저 안에서 그 파일을 연 적이 있는지(`opened`) | 탐색기 등 브라우저 밖에서 그 파일을 열었는지 |

- 프로필은 Windows 계정 안의 브라우저 단위입니다. 한 프로필을 여러 사람이 쓸 수 있습니다([그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md)).
- 기록이 없다는 것은 방문하지 않았다는 뜻이 아닙니다. 시크릿 창, 기록 지우기, 90일 만료, 다른 프로필·다른 브라우저가 모두 이유가 됩니다.
- 리다이렉트 한 번에도 `visits` 행이 여러 개 생깁니다. 사용자가 누른 횟수로 세지 않습니다.
- `visit_duration` 은 창을 보고 있던 시간과 같다고 볼 수 없습니다.

### 보고서 문장

아래 주소와 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "이 사용자의 Chrome `Default` 프로필 `History` 에는 2025-03-14 01:23:45 UTC 에 `https://example.com/` 방문 기록이 있습니다. 전환 유형은 주소창 입력(TYPED)입니다. `visit_source` 에 행이 없어 이 브라우저에서 직접 방문한 기록으로 보입니다."
- 쓰면 안 되는 문장: "피의자가 01:23 에 이 사이트에 직접 접속해 45초 동안 내용을 읽었습니다."

## 시각 해석

### 형식

시각 칸은 모두 1601-01-01 0시(UTC)부터 센 마이크로초입니다. Chromium 의 `base::Time` 이 이렇게 셉니다. DB 에는 `sql::Statement` 가 이 값을 64비트 정수로 적습니다. 머문 길이(`visit_duration`)도 같은 방식으로 마이크로초를 적습니다.

- Unix 시각으로 바꾸려면 11,644,473,600,000,000 을 빼고 1,000,000 으로 나눕니다.
- 값이 0 이면 비어 있는 칸입니다. 그대로 바꾸면 1601-01-01 이 나옵니다. 끝나지 않은 다운로드의 `end_time` 이 그런 예입니다.
- 현지 시각으로 바꿀 때는 그 PC 의 시간대 설정을 씁니다([시간대 설정](../../system-account/time-zone.md), [시간대·시계 오차 보정](../../../03-techniques/analysis/timeline/time-normalization.md)).
- 계산 방법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다.

### 칸마다 뜻

| 칸 | 무엇이 일어날 때 적나 |
|---|---|
| `visits.visit_time` | 방문 한 번의 시각 |
| `urls.last_visit_time` | 그 주소의 가장 최근 방문 시각. 새 방문이 생기면 바뀝니다 |
| `downloads.start_time` | 받기 시작한 시각. 소스 주석은 나중에 바뀌지 않는다고 적습니다 |
| `downloads.end_time` | 받기를 마친 시각 |
| `downloads.last_access_time` | 마지막으로 접근한 시각 |

### 동기화와 시계 변경

`visits.id` 는 새 행일수록 커집니다. 그래서 `id` 순서와 `visit_time` 순서가 어긋나는 곳을 찾으면 쓸모가 있습니다. 그 행이 동기화나 가져오기로 나중에 들어온 방문이면 어긋나도 정상입니다. 그렇지 않은 행이 어긋나면 시스템 시계 변경을 의심해 봅니다([시스템 시각을 바꿨나](../../../04-scenarios/activity/anti-forensics/system-time-change.md)).

## 함정과 한계

1. **`urls` 만 봅니다.** `urls` 는 주소마다 한 행인 요약입니다. 방문 하나하나의 시각은 `visits` 에 있습니다.
2. **동기화된 방문을 이 PC 의 방문으로 씁니다.** `visit_source.source` 가 0 이거나 `originator_cache_guid` 가 차 있으면 다른 기기의 방문일 수 있습니다.
3. **리다이렉트와 프레임을 방문 횟수에 넣습니다.** 사용자가 한 번 이동해도 여러 행이 생깁니다. 사람이 한 이동을 셀 때는 CHAIN_END 가 켜진 최상위 방문(기본 유형 3·4 제외)을 따로 셉니다.
4. **`transition` 이 음수로 보입니다.** 소스의 전환 유형 선언은 부호 있는 32비트입니다. 그래서 0x80000000 이 켜진 값은 음수로 저장될 수 있습니다. 32비트로 잘라 16진으로 바꾼 뒤 나눕니다.
5. **`current_path` 를 최종 경로로 씁니다.** 받는 중이거나 중단된 다운로드는 두 경로가 다를 수 있습니다. 두 칸을 모두 적습니다.
6. **중단 상태를 사용자 행동으로 읽습니다.** 소스에 따르면 브라우저는 시작할 때 "받는 중" 으로 남은 행을 "중단" 으로 바꿉니다. 이전 실행이 비정상으로 끝났다는 뜻일 수 있습니다.
7. **`hash` 를 16진 문자열로 봅니다.** 원시 32바이트입니다. 디스크의 파일과 맞추려면 16진으로 바꿔 비교합니다.
8. **실행 중인 브라우저에서 파일을 복사합니다.** 브라우저가 파일을 열고 있으면 복사가 안 되거나, 저널에만 있는 변경을 놓칠 수 있습니다. 수집 방법은 [선별 수집](../../../03-techniques/process-acquisition/evidence-acquisition/triage-collection.md)을 따릅니다.
9. **다운로드 기록 보관 기한을 방문과 같다고 봅니다.** 2014년 Benson 의 글은 다운로드 기록이 설치 때부터 쌓인다고 적었습니다. 지금 판에서도 그런지는 검체의 가장 오래된 `start_time` 으로 확인합니다.

### 지우기와 조작

- **브라우저 메뉴로 기록을 지웁니다.** 행이 사라집니다. Chromium 은 SQLite 보안 삭제를 켜고 빌드하므로, 파일 안 빈 공간은 대부분 0 입니다([파일 안에 남은 지운 레코드](../../../01-foundations/database-log-formats/sqlite/freelist-freeblock.md)). 저널에 지우기 전 페이지가 남을 수 있습니다.
- **일부 항목만 지웁니다.** `visits.id` 가 비어 있는 구간이 생깁니다. 번호가 빈 곳은 지운 흔적의 단서입니다. 90일 만료로도 앞쪽 번호가 빠지므로, 빈 구간이 어디 있는지 봅니다.
- **다운로드 목록만 지웁니다.** 받은 파일은 디스크에 남을 수 있습니다. 파일 쪽 흔적은 [다운로드 출처 표시 (Zone.Identifier)](../../filesystem/zone-identifier.md)와 [$MFT](../../filesystem/mft.md)에서 찾습니다.
- **`History` 파일째 지웁니다.** 브라우저는 다음 실행 때 빈 파일을 새로 만듭니다. 옛 파일은 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)이나 [$UsnJrnl](../../filesystem/usnjrnl.md)에서 흔적을 찾습니다.
- **시크릿 창을 씁니다.** 이 파일에는 처음부터 남지 않습니다([시크릿 모드로 무엇을 했나](../../../04-scenarios/activity/private-browsing.md)).

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 명세와 Chromium 소스의 `visits` 정의를 보고 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. 테이블 B-트리 잎 페이지 안의 셀 하나입니다. 열이 18개인 요즘 판 스키마를 가정했습니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    24 89 52 13 00 01 06 08 00 04 08 04 09 08 00 08
0x10    08 08 08 09 08 00 2A 00 2F 8E D9 92 A9 0A 40 30
0x20    00 00 01 02 AE A5 40
```

1. `24` 는 레코드 길이 36바이트입니다. `89 52` 는 행 번호(rowid) 1234 입니다. 둘 다 varint 입니다.
2. `13` 은 레코드 머리 길이 19바이트입니다. 그 뒤 18바이트가 열마다 형식 번호입니다.
3. 첫 형식 번호 `00` 은 NULL 입니다. `id` 는 INTEGER PRIMARY KEY 라서 값을 행 번호로 대신합니다. 그래서 이 방문의 `id` 는 1234 입니다.
4. 두 번째 `01` 은 1바이트 정수입니다. 몸통의 `2A` 가 `url` = 42 입니다. `urls` 의 42번 행과 이어집니다.
5. 세 번째 `06` 은 8바이트 빅 엔디언 정수입니다. 몸통의 `00 2F 8E D9 92 A9 0A 40` 이 `visit_time` 입니다.
6. 이 값은 13,386,389,025,000,000 입니다. 11,644,473,600,000,000 을 빼면 1,741,915,425,000,000 이 남습니다. 1,000,000 으로 나눈 Unix 시각은 2025-03-14 01:23:45 UTC 입니다. 한국 시각으로는 같은 날 10:23:45 입니다.
7. 네 번째 `08` 은 값이 0 인 정수입니다. 몸통에 바이트가 없습니다. 그래서 `from_visit` 이 0 이고, 앞 방문이 없습니다. `09` 는 값이 1 인 정수이고, 역시 몸통에 바이트가 없습니다.
8. 여섯 번째 `04` 는 4바이트 정수입니다. 몸통의 `30 00 00 01` 이 `transition` 입니다. 앞 절의 예처럼 TYPED + CHAIN_START + CHAIN_END 입니다.
9. 여덟 번째 `04` 의 몸통 `02 AE A5 40` 이 `visit_duration` 입니다. 45,000,000 마이크로초, 곧 45초입니다.

열 순서는 검체의 `CREATE TABLE` 문을 따릅니다. 옛 판에서 올라온 DB 는 열이 뒤에 붙어 순서가 다를 수 있습니다.

> 그림 자리: 위 셀에서 레코드 길이·행 번호·머리·몸통을 색으로 나누고, 형식 번호와 몸통 값을 화살표로 잇는 그림

### 공개 도구로 한 번

sqlite3 명령줄 셸, DB Browser for SQLite 같은 SQLite 도구로 사본을 엽니다. Hindsight, BrowsingHistoryView 같은 공개 도구도 이 파일을 읽습니다. 원본을 열면 저널이 반영돼 파일이 바뀔 수 있으므로 사본에서만 작업합니다.

방문 기록은 아래처럼 읽습니다.

```sql
SELECT v.id, u.url, u.title,
       datetime(v.visit_time/1000000 - 11644473600, 'unixepoch') AS visit_utc,
       printf('0x%08X', v.transition & 0xFFFFFFFF)              AS transition_hex,
       v.transition & 0xFF                                       AS core_type,
       v.from_visit, v.visit_duration/1000000.0                  AS duration_sec,
       vs.source
FROM visits v
JOIN urls u ON u.id = v.url
LEFT JOIN visit_source vs ON vs.id = v.id
ORDER BY v.visit_time;
```

다운로드는 아래처럼 읽습니다.

```sql
SELECT d.id,
       datetime(d.start_time/1000000 - 11644473600, 'unixepoch') AS start_utc,
       CASE d.end_time WHEN 0 THEN NULL
            ELSE datetime(d.end_time/1000000 - 11644473600, 'unixepoch') END AS end_utc,
       d.target_path, d.received_bytes, d.total_bytes, d.state, d.danger_type,
       d.opened, d.tab_url, d.referrer, hex(d.hash) AS sha256,
       c.chain_index, c.url
FROM downloads d
LEFT JOIN downloads_url_chains c ON c.id = d.id
ORDER BY d.start_time, c.chain_index;
```

도구를 쓸 때는 다음을 확인합니다.

- 시각을 UTC 로 보여 주는지, 분석 PC 의 현지 시각으로 바꿔 보여 주는지 확인합니다.
- 도구가 `visit_source` 를 보여 주는지 확인합니다. 보여 주지 않으면 동기화 방문과 직접 방문을 가릴 수 없습니다.
- 행 몇 개는 위 쿼리나 헥스로 읽은 값과 맞춰 봅니다([도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)).

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [다운로드 출처 표시 (Zone.Identifier)](../../filesystem/zone-identifier.md) | 받은 파일에 붙은 출처 주소와 `downloads_url_chains` 의 주소 |
| [$MFT](../../filesystem/mft.md) · [$UsnJrnl](../../filesystem/usnjrnl.md) | `target_path` 파일의 생성 시각과 `end_time`. 파일이 나중에 지워졌는지 |
| [캐시 (Cache)](cache.md) | 방문 기록을 지운 뒤에도 남은 페이지 조각 |
| [세션·탭 복원 (Sessions)](sessions.md) | 닫을 때 열려 있던 탭과 탭별 뒤로 가기 목록 |
| [쿠키 (Cookies)](cookies.md) | 방문 시각 무렵 그 사이트의 쿠키가 생기거나 쓰였는지 |
| [즐겨찾기 (Bookmarks)](bookmarks.md) | 즐겨찾기로 온 방문(AUTO_BOOKMARK)과 즐겨찾기 목록 |
| [확장 프로그램 (Extensions)](extensions.md) | 확장이 넣은 방문(`source` 2)이나 확장이 만든 다운로드 |
| [네트워크 사용량 (SRUM)](../../execution/system-resource-usage-monitor/network-data-usage.md) | 그 시간대에 브라우저가 실제로 주고받은 양 |
| [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 지우기 전이나 만료 전의 `History` |

여러 기록을 한 타임라인으로 묶는 순서는 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md)에서 다룹니다. 받은 파일의 출처를 좇는 순서는 [이 파일은 어디서 왔나](../../../04-scenarios/activity/file-origin.md)를, 브라우저로 올린 흔적은 [웹메일·웹하드로 올렸나](../../../04-scenarios/exfiltration/data-exfiltration/web-upload.md)를 봅니다.

## 실습

**공개 검체**에서 크롬 계열 브라우저 프로필이 든 이미지를 하나 고릅니다. NIST CFReDS 목록에서 찾을 수 있습니다.

1. 프로필 폴더가 몇 개입니까? 프로필마다 `History` 의 `meta` 표에서 스키마 판 번호를 읽어 보십시오.
2. `visits` 에서 가장 오래된 `visit_time` 과 가장 최근 `visit_time` 은 언제입니까? 둘 사이가 90일보다 짧다면 까닭을 적어 보십시오.
3. 기본 유형이 TYPED 인 방문만 뽑아 보십시오. `urls.typed_count` 와 수가 맞습니까?
4. 다운로드 하나를 골라 `downloads_url_chains` 의 첫 주소와 마지막 주소를 비교해 보십시오. 받은 파일의 Zone.Identifier 와도 맞춰 보십시오.
5. `visits.id` 가 빠진 구간이 있습니까? 그 구간 앞뒤의 시각은 언제입니까?

**직접 만든 Windows 10·11 가상 머신**에서도 해 봅니다.

1. 주소창 입력, 링크 클릭, http 주소에서 https 로 넘어가는 이동을 한 번씩 하고 시각을 적어 둡니다.
2. 파일 하나는 끝까지 받고, 하나는 받다가 취소합니다.
3. 브라우저를 닫고 `History` 와 `History-journal` 을 복사합니다. 이동마다 `visits` 가 몇 행 생겼는지, `transition` 이 어떻게 적혔는지 봅니다.
4. 방문 기록 화면에서 한 항목만 지운 뒤 다시 복사합니다. `visits.id` 에 빈 곳이 생겼는지, 저널에 지운 행이 남았는지 확인합니다.

## 참고 문헌

- Chromium 소스, History 표 정의 — `url_database.cc` · `visit_database.cc` · `url_row.h` · `history_types.h`
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/url_database.cc
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/visit_database.cc
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/url_row.h
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/history_types.h
- Chromium 소스, 전환 유형과 다운로드 값 — `page_transition_types.h` · `download_row.h` · `download_constants.h` · `download_database.cc` · `download_danger_type.h`
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/ui/base/page_transition_types.h
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/download_row.h
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/download_constants.h
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/download_database.cc
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/download/public/common/download_danger_type.h
- Chromium 소스, 시각 저장과 보관 기한 — `base/time/time.h` · `sql/statement.cc` · `history_backend.h`
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/base/time/time.h
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/sql/statement.cc
  - https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/history_backend.h
- Ryan Benson, "Chrome Transition Values" (2014) — https://hindsig.ht/blog/chrome-transition-values
- Ryan Benson, "Archived History files removed from Chrome v37" (2014) — https://hindsig.ht/blog/archived-history-files-removed-from-chrome-v37
- Foxton Forensics, "Chrome History Location" — https://www.foxtonforensics.com/browser-history-examiner/chrome-history-location
