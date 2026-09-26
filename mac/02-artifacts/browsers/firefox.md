---
title: "파이어폭스"
parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1270
---

# 파이어폭스 (Firefox)

파이어폭스는 사용자 프로필 폴더의 SQLite 파일에 방문·북마크·쿠키 기록을 남기고 캐시는 `~/Library/Caches` 쪽에 따로 두며, 시각은 대부분 1970-01-01 UTC 기준 마이크로초로 적습니다.

## 무엇을 기록하나 · 왜 생기나

파이어폭스는 Firefox 3부터 방문 기록을 `places.sqlite` 에 저장합니다 [1]. 이 DB 하나에 방문한 URL, URL마다 쌓이는 방문 한 건 한 건, 북마크가 함께 들어 있어서 [2], 웹 사용 행위를 재구성할 때 가장 먼저 여는 파일입니다. 사용자가 페이지를 열 때마다 방문이 한 행씩 늘고, 그 행에는 링크를 눌렀는지, 주소를 직접 입력했는지, 서버가 리디렉션했는지를 나타내는 방문 종류 (Transition Type)가 붙습니다 [3].

다운로드 기록은 옛 버전에서 `downloads.sqlite` 에 따로 쌓였고, 이후 버전에서는 `places.sqlite` 로 옮겨졌습니다 [1][4]. 지금 버전에서는 파일을 받으면 방문 기록에 다운로드 종류(값 7)의 방문이 한 행 남습니다 [3]. 쿠키는 `cookies.sqlite` 에, 부가 기능과 확장 목록은 `addons.json`·`extensions.json` 에 들어 있습니다 [4].

이 밖에도 양식 자동 완성(`formhistory.sqlite`), 파비콘(`favicons.sqlite`), 열린 탭과 창을 되살리는 세션 파일(`sessionstore.jsonlz4`), 저장된 비밀번호(`logins.json`)와 그 키(`key4.db`) 같은 파일도 프로필 폴더에 있다고 알려져 있고, 이 파일들의 구조는 이 페이지에서 다루지 않습니다. 저장된 비밀번호를 사고 대응에서 어떻게 다루는지는 [저장된 암호 (Passwords·iCloud Keychain)](../credentials/saved-passwords.md)에서 다룹니다.

## 위치와 버전별 차이

프로필 파일은 사용자 홈의 `Library/Application Support/Firefox/Profiles` 아래 프로필 폴더마다 따로 있고 [1][4], 캐시는 같은 이름의 프로필 폴더를 `Library/Caches` 아래에 따로 만들어 둡니다 [1][4]. 수집할 때는 프로필 폴더 이름을 와일드카드로 잡아 모든 프로필을 빠짐없이 모읍니다 [4].

| 기록 | 위치 | 알려 주는 것 |
|---|---|---|
| 방문·북마크·다운로드 | `~/Library/Application Support/Firefox/Profiles/*/places.sqlite`, `places.sqlite-wal` [1][4] | 방문한 URL, 방문 시각과 종류, 북마크, 다운로드 방문 |
| 쿠키 | `~/Library/Application Support/Firefox/Profiles/*/cookies.sqlite`, `cookies.sqlite-wal` [4] | 어떤 사이트의 쿠키가 남아 있는지 |
| 옛 다운로드 기록 | `~/Library/Application Support/Firefox/Profiles/*/downloads.sqlite`, `downloads.sqlite-wal` [4] | 옛 버전에서 받은 파일 |
| 부가 기능·확장 | `~/Library/Application Support/Firefox/Profiles/*/addons.json`, `extensions.json`, `webapps/webapps.json` [4] | 설치된 부가 기능과 확장 |
| 캐시 (Firefox 32 이후) | `~/Library/Caches/Firefox/Profiles/*/cache2/` 와 그 아래 `entries/`, `doomed/` [1][4] | 내려받아 둔 웹 콘텐츠 |
| 캐시 (옛 형식) | `~/Library/Caches/Firefox/Profiles/*/Cache/` [1] | 옛 버전의 캐시 |

프로필 폴더 이름에는 `*.default` 와 `*.default-*` 두 패턴이 있어서 [4], 이름 끝에 `.default` 만 붙은 폴더와 `.default-` 뒤에 글자가 더 붙은 폴더를 모두 찾아야 합니다. 한 계정 안에 프로필 폴더가 여러 개 있으면 기록 묶음도 그만큼 여러 개입니다.

알려진 경로 변화는 macOS 버전이 아니라 모두 파이어폭스 버전에 따른 것입니다.

| 파이어폭스 버전 | 바뀐 점 |
|---|---|
| Firefox 3부터 | 방문 기록을 `places.sqlite` 에 저장 [1] |
| Firefox 21 이하 | 다운로드 기록이 `downloads.sqlite` 에 있고, 그 뒤로는 `places.sqlite` 로 옮겨짐 [1]. 정확한 전환 버전은 공개 자료 없음 |
| Firefox 32부터 | 캐시 폴더가 `Cache/` 에서 `cache2/` 로 바뀜 [1] |
| 최근 버전 | `moz_places`·`moz_origins` 뒤쪽 열(`alt_frecency`, `recalc_alt_frecency` 등)은 2026-09 무렵 소스 기준이라 오래된 DB에는 없을 수 있음 [2] |

## 구조

`places.sqlite` 의 중심은 URL 한 개당 한 행인 `moz_places` 와 방문 한 번당 한 행인 `moz_historyvisits` 이고, 방문 행의 `place_id` 가 `moz_places.id` 를 가리켜 한 URL에 방문 여러 행이 붙습니다 [2]. 북마크(`moz_bookmarks.fk`), `moz_inputhistory.place_id`, 페이지 주석(`moz_annos.place_id`)도 같은 식으로 `moz_places.id` 를 가리키고, `moz_places.origin_id` 는 `moz_origins` 를 가리킵니다 [2].

> 그림 자리: `moz_places` 를 가운데 두고 `moz_historyvisits`·`moz_bookmarks`·`moz_inputhistory`·`moz_annos`·`moz_places_metadata` 가 `place_id`(북마크는 `fk`)로 붙고, `origin_id` 로 `moz_origins` 에 이어지는 관계도

| 표 | 주요 열 | 담는 것 |
|---|---|---|
| `moz_places` | `id`, `url`, `title`, `rev_host`, `visit_count`, `hidden`, `typed`, `frecency`, `last_visit_date`, `guid`, `origin_id` | URL 한 개당 한 행. 제목과 방문 횟수, 마지막 방문 시각 [2] |
| `moz_historyvisits` | `id`, `from_visit`, `place_id`, `visit_date`, `visit_type`, `session`, `source`, `triggeringPlaceId` | 방문 한 번당 한 행 [2] |
| `moz_bookmarks` | `id`, `type`, `fk`, `parent`, `position`, `title`, `dateAdded`, `lastModified`, `guid` | 북마크와 폴더 [2] |
| `moz_origins` | `id`, `prefix`, `host`, `frecency`, `block_until_ms`, `block_pages_until_ms` | `prefix` 와 `host` 로 나눈 출처 단위 행 [2] |
| `moz_annos`, `moz_anno_attributes` | `place_id`, `anno_attribute_id`, `content`, `dateAdded`, `lastModified` / `id`, `name` | 페이지에 붙은 주석과 주석 이름 [2] |
| `moz_items_annos` | `moz_annos` 와 같고 `place_id` 대신 `item_id` | `item_id` 가 가리키는 항목에 붙은 주석 [2] |
| `moz_inputhistory` | `place_id`, `input`, `use_count` | 입력 글자(`input`)와 사용 횟수. 주소창 입력과 고른 결과로 알려져 있음 [2] |
| `moz_keywords` | `id`, `keyword`, `place_id`, `post_data` | 키워드 [2] |
| `moz_bookmarks_deleted` | `guid`, `dateRemoved` | 열 이름으로 보면 지운 북마크의 `guid` 와 지운 시각. 시각 단위는 실제 데이터로 확인 [2] |
| `moz_places_metadata` | `place_id`, `referrer_place_id`, `created_at`, `updated_at`, `total_view_time`, `typing_time`, `key_presses`, `scrolling_time`, `scrolling_distance`, `document_type`, `search_query_id` | 열 이름으로 보면 페이지를 본 시간과 입력·스크롤 양 [2] |

`moz_places_metadata` 의 시간 열 단위와 이 표가 들어온 버전은 공개 자료가 없어서, 보고서에 옮길 때는 실물 값의 크기를 보고 단위를 따로 확인합니다. `from_visit` 는 열 이름대로 바로 앞 방문의 `id` 로 보고 방문 흐름을 이어 붙이는 데 흔히 쓰지만, 열 이름에서 나온 풀이입니다 [2]. 다운로드한 파일의 저장 경로가 `moz_annos` 에 `downloads/destinationFileURI` 같은 이름으로 남는다고 알려져 있어서, 분석 대상의 `moz_annos` 에서 확인합니다.

방문 종류는 `moz_historyvisits.visit_type` 에 숫자로 들어갑니다 [3].

| 값 | 이름 | 뜻 |
|---|---|---|
| 1 | `TRANSITION_LINK` | 링크를 따라가 새 최상위 페이지를 엶 |
| 2 | `TRANSITION_TYPED` | 주소창에 URL을 입력했거나 주소창 자동 완성 결과를 고름. 방문 기록 사이드바·방문 기록 메뉴 같은 기록 목록에서 눌러 연 경우도 이 값 |
| 3 | `TRANSITION_BOOKMARK` | 북마크를 눌러 이동 |
| 4 | `TRANSITION_EMBED` | 페이지 안쪽 콘텐츠(이미지, iframe 내용, 링크를 누르지 않고 채워진 프레임 내용)를 불러옴 |
| 5 | `TRANSITION_REDIRECT_PERMANENT` | 영구 리디렉션 |
| 6 | `TRANSITION_REDIRECT_TEMPORARY` | 임시 리디렉션 |
| 7 | `TRANSITION_DOWNLOAD` | 다운로드 |
| 8 | `TRANSITION_FRAMED_LINK` | 링크를 따라가 프레임 안에서 방문 |
| 9 | `TRANSITION_RELOAD` | 새로 고침 |

2026-09 무렵 소스에는 1부터 9까지만 정의돼 있고 [3], 표에 없는 값이 나오면 그 DB를 만든 파이어폭스 버전의 소스를 따로 봅니다. 값 4 방문은 DB에 쓰지 않고 메모리에만 둔다는 이야기가 있어서, 실물 DB에 값 4 행이 있는지 직접 세어 봅니다.

## 증거로서 의미

**증명하는 것.** `moz_historyvisits` 한 행은 그 프로필의 파이어폭스가 그 시각에 그 URL을 방문 기록으로 남겼다는 뜻이고, 방문 종류로 그 방문이 어떻게 일어났는지를 가릅니다. 값 2(`TYPED`)는 주소창에 직접 입력했거나 자동 완성 결과를 고른 방문이고 값 1(`LINK`)은 링크를 따라간 방문이라서 [3], 사용자가 그 주소를 알고 찾아갔는지를 따질 때 근거가 됩니다. 다만 값 2에는 방문 기록 사이드바나 방문 기록 메뉴에서 눌러 연 방문도 들어가므로 [3], 값 2만으로 주소를 손으로 쳤다고 단정하지는 않습니다. 값 7(`DOWNLOAD`)은 그 URL에서 다운로드가 일어났다는 기록이고 [3], 북마크 행은 그 URL을 북마크에 넣은 기록입니다.

**증명하지 못하는 것.** 값 5·6은 서버가 보낸 리디렉션이라 사용자 행위가 아니고 [3], 값 4는 페이지 안의 이미지나 iframe 을 불러온 기록이라서 사용자가 그 URL을 직접 열었다는 근거가 되지 못합니다. 방문 기록으로는 누가 키보드 앞에 있었는지, 사용자가 화면을 실제로 읽었는지 알 수 없으므로, 사람을 특정하려면 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md)의 방법으로 다른 기록과 맞춰 봅니다. 다운로드 방문도 파일이 지금 디스크에 있다거나 실행됐다는 뜻은 아닙니다. 기록이 없다고 해서 방문하지 않았다고 말할 수도 없는데, 기록을 지웠거나 다른 프로필·다른 브라우저를 썼을 수 있고, 비공개 창 (Private Browsing) 방문이 이 DB에 남는지는 실제 데이터로 따로 확인합니다. 비공개 창 쪽은 [개인 정보 보호 브라우징으로 무엇을 했나 (Private Browsing)](../../04-scenarios/activity/private-browsing.md)에서 다룹니다.

보고서에는 "피조사자가 이 사이트에 접속했다" 보다 "이 계정의 파이어폭스 프로필에 이 URL을 방문 종류 2(주소창 입력·자동 완성·기록 목록 선택)로 연 방문 기록이 이 시각(UTC)에 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

파이어폭스의 PRTime 은 1970-01-01 기준 **마이크로초**입니다 [3]. 유닉스 시각과 기준점은 같지만 단위가 초가 아니라 마이크로초이고, 같은 기준으로 밀리초를 쓰는 자바스크립트 Date 와도 단위가 다릅니다 [3]. `moz_historyvisits.visit_date` 는 1970-01-01 UTC 기준 마이크로초라서 [1], 현지 시각으로 옮길 때는 먼저 UTC 로 바꾼 뒤 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)에서 확인한 시간대를 적용합니다.

| 열 | 기준·단위 | 비고 |
|---|---|---|
| `moz_historyvisits.visit_date` | 1970-01-01 UTC, 마이크로초 | [1] |
| `moz_places.last_visit_date` | PRTime(마이크로초)으로 알려짐 | 단위는 실제 데이터로 확인 [2] |
| `moz_bookmarks.dateAdded`, `lastModified` | PRTime(마이크로초)으로 알려짐 | 단위는 실제 데이터로 확인 [2] |
| `moz_annos.dateAdded`, `lastModified` | PRTime(마이크로초)으로 알려짐 | 단위는 실제 데이터로 확인 [2] |
| `moz_origins.block_until_ms`, `block_pages_until_ms` | 이름상 밀리초 | 뜻은 공개 자료 없음 [2] |

방문 한 번이 `moz_historyvisits` 한 행이라서 방문마다 `visit_date` 가 하나씩 있고 [2], `moz_places.last_visit_date` 는 URL 한 행에 하나뿐인 값이라 방문 흐름을 따질 때는 `visit_date` 를 씁니다. PRTime 은 2001 기준 맥 절대 시각과도, 크롬 계열의 1601 기준 시각과도 다르므로 [1][3], 사파리·크롬 기록과 한 타임라인에 놓을 때는 기준을 먼저 맞춥니다. 기준끼리의 관계는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에 정리돼 있습니다.

## 함정과 한계

- **WAL 파일을 빼먹는 경우.** `places.sqlite-wal`, `cookies.sqlite-wal` 도 수집 대상이라서 [4], 본 DB만 복사하면 최근 기록이 빠질 수 있습니다. WAL 이 어떻게 동작하는지는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.
- **캐시 위치를 놓치는 경우.** 캐시는 프로필 폴더가 아니라 `~/Library/Caches/Firefox/Profiles/` 아래에 있어서 [1][4], `Application Support` 쪽만 수집하면 캐시가 통째로 빠집니다.
- **프로필이 여러 개인 경우.** 폴더 이름 패턴이 두 가지라서 [4] 한 패턴만 찾으면 다른 프로필을 놓칩니다.
- **버전마다 다른 스키마.** 열 목록은 최근 소스 기준이라 오래된 DB에는 일부 열이 없고 [2], 옛 버전의 다운로드 기록은 `places.sqlite` 가 아닌 `downloads.sqlite` 에 있습니다 [1][4].
- **리디렉션과 안쪽 콘텐츠 방문.** 방문 종류 5·6 행, 그리고 DB에 남아 있다면 4 행까지 사용자 방문으로 세면 방문 수가 부풀려집니다 [3].
- **지우기와 조작.** 사용자가 기록을 지우거나 파이어폭스가 오래된 기록을 정리한 뒤에도 WAL 이나 DB의 빈 공간에 흔적이 남을 수 있다는 점은 SQLite 일반론이라서, 파이어폭스 DB에서 어디까지 남는지는 실제 데이터로 확인합니다. 지운 행을 찾는 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)를, 기록을 없애려 한 정황을 판단하는 방법은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)를 봅니다.

## 직접 분석해 보기

원본 DB를 바로 열지 말고 `places.sqlite` 와 `places.sqlite-wal` 을 같은 작업 폴더에 함께 복사한 뒤 사본을 엽니다.

### 헥스로 한 번

아래 값은 명세에 맞춰 만든 예시이고, 실제 기기에서 나온 값이 아닙니다. SQLite 레코드에서 정수 열을 꺼내는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)를 따르고, 여기서는 꺼낸 `visit_date` 정수를 시각으로 바꾸는 단계만 따라갑니다.

```
visit_date 를 8바이트 빅 엔디언으로 적은 모양 (예시)
00 06 0a 24 18 1e 40 00

16진수 0x00060A24181E4000 = 10진수 1700000000000000
1700000000000000 마이크로초 ÷ 1000000 = 1700000000 초
1970-01-01 00:00:00 UTC + 1700000000 초 = 2023-11-14 22:13:20 UTC
```

같은 수를 초로 읽으면 말이 안 되는 먼 미래가 나오고, 맥 절대 시각이나 1601 기준으로 읽어도 엉뚱한 날짜가 나옵니다. 자릿수가 16자리 안팎이면 마이크로초를 먼저 의심합니다. 파이썬으로는 `datetime(1970,1,1) + timedelta(microseconds=값)` 처럼 계산합니다 [1].

### 공개 도구로 한 번

`sqlite3` 명령줄 도구나 DB Browser for SQLite 같은 공개 SQLite 도구로 사본을 열고 두 표를 이어 봅니다.

```sql
-- 방문 한 건마다 URL과 UTC 시각, 방문 종류를 붙여 시간순으로 본다
SELECT v.id,
       datetime(v.visit_date / 1000000, 'unixepoch') AS visit_utc,
       v.visit_type,
       v.from_visit,
       p.url,
       p.title
FROM moz_historyvisits AS v
JOIN moz_places AS p ON p.id = v.place_id
ORDER BY v.visit_date;

-- 방문 종류 2(주소창 입력 등)와 7(다운로드)만 추린다
SELECT datetime(v.visit_date / 1000000, 'unixepoch') AS visit_utc,
       v.visit_type, p.url
FROM moz_historyvisits AS v
JOIN moz_places AS p ON p.id = v.place_id
WHERE v.visit_type IN (2, 7)
ORDER BY v.visit_date;

-- 북마크와 가리키는 URL
SELECT b.title, p.url, b.dateAdded, b.lastModified
FROM moz_bookmarks AS b
JOIN moz_places AS p ON p.id = b.fk;
```

첫 번째 질의 결과에서 `from_visit` 가 다른 행의 `id` 와 이어지는지 따라가면, 어떤 페이지에서 어떤 링크를 눌러 다음 페이지로 갔는지 흐름을 이어 볼 수 있습니다. `dateAdded`·`lastModified` 는 단위를 실제 데이터로 확인해야 하는 열이라서 결과를 그대로 두고 값의 크기를 먼저 봅니다.

## 교차 검증

- [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) — 방문 종류 7로 남은 다운로드가 받은 파일 쪽에도 기록을 남겼는지 대조합니다. 파이어폭스로 받은 파일에 격리 기록이 어떻게 남는지는 그 페이지에서 확인합니다.
- [다운로드 출처 속성 (kMDItemWhereFroms)](../filesystem/where-froms.md) — 받은 파일에 붙은 출처 URL과 방문 기록의 URL을 맞춰 봅니다.
- [사파리 (Safari)](safari/index.md), [크롬·엣지·웨일 (Chromium 계열)](chromium/index.md) — 같은 사용자가 다른 브라우저도 썼는지 봅니다.
- [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md) — 시각 기준을 맞춰 다른 아티팩트와 한 시간축에 놓습니다.
- [웹 사용 행위 재구성 (Web Activity)](../../04-scenarios/activity/web-activity.md), [악성 코드는 어디서 들어왔나 (Initial Access)](../../04-scenarios/incident/initial-access.md) — 이 기록을 쓰는 조사 흐름입니다.

## 실습

NIST CFReDS 같은 공개 시험 자료 가운데 파이어폭스를 쓴 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. `~/Library/Application Support/Firefox/Profiles/` 아래 프로필 폴더는 몇 개이고, 각각 `*.default` 와 `*.default-*` 가운데 어느 패턴에 맞나요?
2. `places.sqlite` 만 연 결과와 `places.sqlite-wal` 을 함께 둔 사본을 연 결과에서 `moz_historyvisits` 행 수가 다른가요? 다르다면 늘어난 행은 언제 방문인가요?
3. 가장 이른 방문과 가장 늦은 방문의 `visit_date` 를 UTC 로 바꾸고, 분석 대상의 시간대 설정으로 현지 시각을 구해 보세요.
4. 방문 종류 2(주소창 입력 등)로 연 URL 목록과 방문 종류 1(링크)로 연 URL 목록을 나눠 보고, 5·6(리디렉션)을 뺐을 때 방문 수가 얼마나 줄어드나요?
5. 방문 종류 7(다운로드) 방문마다 같은 시각 무렵 격리 기록이나 다운로드 출처 속성이 있는지 대조해 보세요.
6. `~/Library/Caches/Firefox/Profiles/` 아래 `cache2/entries/` 가 있다면, 프로필 폴더 이름이 `Application Support` 쪽과 맞는지 확인해 보세요.

## 참고 문헌

1. Forensics Wiki, "Mozilla Firefox" — https://forensics.wiki/mozilla_firefox/
2. Mozilla 소스(mozilla-central), toolkit/components/places/nsPlacesTables.h — https://searchfox.org/mozilla-central/source/toolkit/components/places/nsPlacesTables.h
3. Mozilla 소스(mozilla-central), toolkit/components/places/nsINavHistoryService.idl — https://searchfox.org/mozilla-central/source/toolkit/components/places/nsINavHistoryService.idl
4. ForensicArtifacts, webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
