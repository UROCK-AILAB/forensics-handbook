---
title: "방문 기록"
parent: "사파리"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1150
---

# 방문 기록 (History.db)

사파리는 방문 기록(History)을 SQLite 데이터베이스 `History.db` 에 저장하고, 주소 하나는 `history_items` 표에 한 행, 방문 한 번은 `history_visits` 표에 한 행으로 남아서 두 표를 이어 읽으면 어느 주소를 언제 열었는지 시간순으로 다시 짤 수 있습니다.

## 무엇을 기록하나

같은 주소를 몇 번 열든 `history_items` 에는 그 주소의 행이 하나만 있고(`url` 칸이 UNIQUE), 방문할 때마다 `history_visits` 에 행이 하나씩 늘어납니다 [1][2]. 방문 행에는 방문 시각과 그때의 페이지 제목이 들어가고, 페이지를 제대로 불러왔는지, GET 이 아닌 요청이었는지, 어느 방문에서 리디렉트돼 왔는지도 칸으로 남습니다 [2]. 사파리 폴더 전체의 파일 목록과 설정 파일은 허브 [사파리 (Safari)](index.md)에서 정리합니다.

## 위치와 버전별 차이

공개 도구 mac_apt 의 코드 주석과 ForensicArtifacts 정의 파일을 따르면 버전마다 파일이 이렇게 달라집니다 [1][4].

| 시기 | 파일 | 형식 | 출처 |
|---|---|---|---|
| OS X Mavericks 까지 | `~/Library/Safari/History.plist` | plist | [1][4] |
| OS X Yosemite 부터 | `~/Library/Safari/History.db` 와 `History.db-wal` | SQLite | [1][4] |
| Safari 15 부터 | 컨테이너 `~/Library/Containers/com.apple.Safari/Data/Library/Safari` 아래도 찾음 | SQLite | [1] |
| Safari 17 부터 | 프로필마다 컨테이너 쪽 사파리 폴더 아래 `Profiles/{UUID}/History.db` 가 따로 있음 | SQLite | [1] |

이 핸드북이 주로 다루는 macOS 10.15 Catalina 이후에는 `History.db` 가 기준입니다. 다만 ForensicArtifacts 정의는 `History.db` 를 `~/Library/Safari/` 에만 적고 있어서 [4], Safari 15 부터 모든 파일이 컨테이너로 옮겨 갔다고 보지 않고 두 위치를 다 확인합니다. Safari 17 에서 프로필을 여러 개 쓰면 프로필마다 방문 기록 파일이 따로 생기니 [1], 한 파일만 열고 "방문 기록이 없다" 고 쓰면 안 됩니다. 프로필 목록을 `SafariTabs.db` 에서 찾는 방법은 [탭과 세션 (Tabs·Sessions)](tabs-sessions.md)에 있습니다.

Mavericks 이하의 `History.plist` 에는 `WebHistoryFileVersion`, 방문 항목 배열 `WebHistoryDates`(항목 안에 `redirectURLs`, `title`, `lastVisitedDate`), 도메인별 묶음 `WebHistoryDomains.v2`(안에 `itemCount`)가 있습니다 [1]. ForensicArtifacts 정의는 이 파일의 위치만 적습니다 [4].

## 구조

`History.db` 에 있는 표는 `history_client_versions`, `history_event_listeners`, `history_events`, `history_items`, `history_tombstones`, `history_visits`, `metadata` 입니다 [2]. 분석의 중심은 `history_items` 와 `history_visits` 이고, 두 표는 `history_visits.history_item = history_items.id` 로 잇습니다 [1][2]. SQLite 파일 자체를 읽는 법과 WAL 은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

### history_items — 주소

| 칸 | 내용 [2] |
|---|---|
| `id` | 행 번호. 방문 행이 이 값을 가리킴 |
| `url` | 주소. UNIQUE |
| `domain_expansion` | 도메인 관련 값 |
| `visit_count` | 방문 수 |
| `daily_visit_counts`, `weekly_visit_counts` | BLOB. 이름으로 보면 일별·주별 방문 수 |
| `autocomplete_triggers` | BLOB |
| `should_recompute_derived_visit_counts` | 방문 수를 다시 셀지 나타내는 값(이름 기준) |
| `visit_count_score` | 방문 점수 |

BLOB 칸 세 개의 내부 형식은 확인한 자료에 없어서 이 페이지에서는 풀지 않습니다.

### history_visits — 방문

| 칸 | 내용 [2] |
|---|---|
| `id` | 방문 번호 |
| `history_item` | `history_items.id` 를 가리킴. ON DELETE CASCADE |
| `visit_time` | 방문 시각. REAL |
| `title` | 방문 때의 페이지 제목 |
| `load_successful` | 불러오기 성공 여부. 기본값 1 |
| `http_non_get` | GET 이 아닌 요청 여부. 기본값 0 |
| `synthesized` | 기본값 0 |
| `redirect_source` | 이 방문으로 리디렉트해 온 방문의 `id` |
| `redirect_destination` | 이 방문에서 리디렉트해 간 방문의 `id` |
| `origin` | 기본값 0 |
| `generation`, `attributes`, `score` | 그 밖의 값 |

`history_item` 이 ON DELETE CASCADE 로 정의돼 있어서 `history_items` 의 행을 지우면 그 주소에 딸린 방문 행도 함께 지워집니다 [2]. `redirect_source`·`redirect_destination` 은 방문 행끼리 서로를 가리키는 칸이라서 따라가면 리디렉트 사슬을 볼 수 있지만, 칸마다 어떤 값이 들어가는지와 `origin`·`synthesized` 값의 뜻(예를 들어 iCloud 로 동기화된 방문인지)은 확인한 자료에 없습니다.

### history_tombstones

`history_tombstones` 에는 `id`, `start_time`(REAL), `end_time`(REAL), `url`, `generation` 칸이 있습니다 [2]. 이름과 칸 구성만 보면 지운 기간이나 주소를 적어 두는 표처럼 보이지만, 확인한 자료 어디에도 그렇게 적혀 있지 않고 두 시각 칸의 기준도 밝혀지지 않았습니다. 이 표의 행을 "사용자가 기록을 지운 증거" 로 쓰려면 같은 macOS 버전에서 직접 지워 보고 확인한 뒤에 씁니다.

## 증거로서 의미

**증명하는 것.** 방문 행이 있으면 그 사용자 계정(Safari 17 이후라면 그 프로필)의 사파리 방문 기록에 이 주소가 이 시각으로 올라 있다는 뜻입니다. `title` 로 그때의 페이지 제목을, `load_successful` 로 페이지를 제대로 불러왔는지를, 리디렉트 칸으로 어느 주소를 거쳐 도착했는지를 함께 볼 수 있습니다 [2].

**증명하지 못하는 것.** 사람이 주소를 직접 쳤는지, 링크를 눌렀는지, 페이지를 얼마나 오래 보았는지는 이 표로 알 수 없습니다. Apple 은 사파리 방문 기록을 iCloud 표준 데이터 보호에서도 종단간 암호화한다고 밝히고 [5], 기록을 지우면 같은 iCloud 계정의 다른 기기 기록도 지워진다고 설명합니다 [3]. 그런데 다른 기기에서 온 방문이 이 파일에 섞이는지, 섞인다면 어느 칸으로 구분하는지는 확인한 자료에 없어서, 방문 행 하나를 "이 맥에서 일어난 방문" 으로 단정하지 않습니다. 그 시각에 누가 맥 앞에 있었는지는 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)에서 따로 따집니다.

보고서에는 "피의자가 이 사이트에 접속했다" 가 아니라 "이 계정의 사파리 방문 기록에 이 주소가 이 시각(UTC)으로 남아 있고, 불러오기 성공 값은 1이다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

`visit_time` 은 맥 절대 시각(Mac Absolute Time), 곧 2001-01-01 00:00:00 UTC 부터 흐른 초를 실수로 적은 값이고, plaso 와 mac_apt 모두 이렇게 읽습니다 [1][2]. 방문 한 번에 값 하나가 생기고, `history_items` 에는 시각 칸이 없어서 주소별 "마지막 방문 시각" 은 방문 행의 최댓값으로 구합니다. 유닉스 시각으로 바꾸려면 978307200(1970-01-01 부터 2001-01-01 까지의 초)을 더합니다. 시각 값 전반은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md), 현지 시각으로 옮길 때 쓸 시간대 설정은 [시간대와 시계 설정 (Time Zone·NTP)](../../system-account/time-zone.md)을 봅니다.

## 함정과 한계

**WAL 을 빼먹기 쉽습니다.** `History.db` 옆에는 `History.db-wal` 이 붙어 있어서 [4] 본 파일만 복사하면 최근 방문이 빠질 수 있습니다. 두 파일을 함께 수집하고, 원본이 아닌 사본에서 엽니다.

**기록 지우기가 여러 곳을 한꺼번에 지웁니다.** Apple 설명에 따르면 기록 지우기는 방문 기록뿐만 아니라 열린 페이지의 뒤로/앞으로 목록, 자주 방문한 사이트 목록, 최근 검색, 웹페이지 아이콘, 열린 페이지 스냅샷, 다운로드 목록, 빠른 웹사이트 검색, 위치·알림을 요청한 사이트 목록까지 지우고, 내려받은 파일은 남기며, iCloud 로 묶인 다른 기기의 기록도 지웁니다 [3]. 그래서 방문 기록이 비어 있는데 다운로드 폴더에 파일이 남아 있거나 다른 기기에도 기록이 없다면 기록 지우기를 의심해 볼 수 있습니다. 지운 행이 WAL 이나 빈 페이지에 남는지는 확인한 자료에 없고, 복구 방법은 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md), 지우기 흔적 전반은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다. 일정 기간이 지나면 기록을 자동으로 지우는 설정의 키와 기본값도 확인하지 못했습니다.

**개인 정보 보호 브라우징은 이 파일에 안 남습니다.** 무엇이 남지 않고 어디를 대신 봐야 하는지는 [개인 정보 보호 브라우징 (Private Browsing)](private-browsing.md)에서 다룹니다.

**`visit_count` 는 저장된 숫자입니다.** 남아 있는 방문 행 수와 같다는 보장이 확인한 자료에 없으니, 보고서에 방문 횟수를 쓸 때는 방문 행을 직접 센 값과 나란히 적습니다.

## 직접 분석해 보기

사본에서 두 표를 이어 읽는 질의는 아래와 같습니다. plaso 가 읽는 칸 구성을 따르고 [2], 시각은 UTC 로 바꿔 둡니다.

```sql
SELECT v.id,
       i.url,
       v.title,
       datetime(v.visit_time + 978307200, 'unixepoch') AS visit_utc,
       v.load_successful,
       v.http_non_get,
       v.redirect_source,
       v.redirect_destination,
       i.visit_count
FROM history_visits AS v
JOIN history_items  AS i ON v.history_item = i.id
ORDER BY v.visit_time;
```

리디렉트 사슬은 `redirect_destination` 이 있는 방문에서 시작해 그 값이 가리키는 방문을 차례로 따라가면 됩니다. 칸 값의 뜻이 확인되지 않은 만큼, 사슬로 이은 결과는 방문 시각과 주소가 자연스럽게 이어지는지 눈으로 한 번 더 봅니다.

공개 도구로는 plaso 의 사파리 History.db 플러그인이 `history_items` 와 `history_visits` 를 이어 `id`, `url`, `visit_count`, `visit_time`, `redirect_destination`, `title`, `http_non_get`, `redirect_source` 를 읽고 [2], mac_apt 는 `title`, `url`, `load_successful`, `visit_time` 을 읽습니다 [1]. 도구마다 읽는 칸이 달라서 도구 결과에 없는 칸은 위 질의로 채우고, 도구 결과와 질의 결과의 행 수를 맞춰 봅니다. 도구 결과를 검증하는 방법은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 교차 검증

| 함께 볼 것 | 이유 |
|---|---|
| [다운로드 (Downloads.plist)](downloads.md) | 방문 직후 받은 파일이 있는지 |
| [탭과 세션 (Tabs·Sessions)](tabs-sessions.md) | 열려 있던 탭과 탭별 뒤로/앞으로 목록, 프로필 목록 |
| [북마크와 읽기 목록 (Bookmarks·Reading List)](bookmarks.md) | 자주 방문한 사이트, 저장해 둔 주소 |
| [캐시와 웹 데이터 (Cache·WebKit)](cache-webkit.md) | 같은 도메인의 쿠키 생성 시각, 웹 아이콘 |
| [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md) | 받은 파일 쪽에서 본 출처 |
| [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md) | 브라우저 흔적을 묶어 읽는 순서 |
| [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) | 방문 시각을 다른 기록과 한 줄로 세우기 |

## 실습

NIST CFReDS 같은 공개 맥 검체에서 `History.db` 를 찾아 아래 질문을 풀어 봅니다.

1. `~/Library/Safari/` 와 컨테이너 쪽 가운데 어디에 `History.db` 가 있고, `-wal` 파일도 함께 있는가
2. 가장 이른 방문과 가장 늦은 방문의 시각은 UTC 와 검체의 현지 시각으로 각각 언제인가
3. `visit_count` 가 가장 큰 주소는 무엇이고, 방문 행을 직접 센 값과 같은가
4. `redirect_destination` 이 채워진 방문을 하나 골라 리디렉트 사슬을 끝까지 따라가 보라
5. `history_tombstones` 에 행이 있다면 그 시각 칸 값을 방문 시각과 같은 방법으로 바꿔 보고, 해석이 가능한지 따져 보라

## 참고 문헌

1. mac_apt Safari 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/safari.py
2. plaso Safari History.db SQLite 플러그인 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/sqlite_plugins/safari.py
3. Apple Support, Safari 사용 설명서(Mac) — Clear your browsing history in Safari on Mac — https://support.apple.com/guide/safari/clear-your-browsing-history-sfri47acf5d6/mac
4. ForensicArtifacts 정의 파일 webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
5. Apple Support, iCloud data security overview (2026-01-05) — https://support.apple.com/en-us/102651
