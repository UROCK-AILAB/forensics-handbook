# 양식 기록 (formhistory.sqlite)

## 한 줄 요약

파이어폭스는 웹 양식의 입력란에 친 값을 `formhistory.sqlite` 에 SQLite 형식으로 저장하고 다음에 입력할 때 이 값을 자동완성 후보로 보여 주며, 입력란 이름과 값, 쓴 횟수, 처음과 마지막으로 쓴 시각이 남습니다. 지운 항목의 식별자와 지운 시각을 따로 담는 표도 있지만, 소스는 안드로이드판에서만 이 표에 씁니다.

## 무엇을 기록하나 · 왜 생기나

양식 기록 (Form History) 은 사용자가 입력란에 친 값을 입력란 이름과 함께 모아 둔 기록이며, 같은 이름의 입력란을 다시 만나면 파이어폭스가 저장해 둔 값을 후보로 보여 줍니다. 한 행에는 쓴 횟수와 처음·마지막으로 쓴 시각이 함께 있습니다.

- 안드로이드판은 항목을 지울 때 `moz_deleted_formhistory` 표에 그 항목의 `guid` 와 지운 시각을 씁니다. 소스의 `supportsDeletedTable` 이 안드로이드에서만 참이므로, Windows 판에서는 이 표에 행을 쓰지 않습니다.
- 오래된 항목은 파이어폭스가 스스로 지웁니다. 소스의 `expireOldEntries()` 는 `browser.formfill.expire_days` 로 기준 시각을 계산하고, `lastUsed` 가 그보다 이른 항목을 지웁니다.

## 위치와 버전별 차이

- 파일 이름은 `formhistory.sqlite` 입니다. 프로필 폴더에서 찾습니다. 프로필 폴더를 찾는 법은 [프로필 구조 (profiles.ini·prefs.js)](profiles-ini-prefs-js.md) 에서 다룹니다.
- 이번에 연 소스에서는 파일 이름만 확인했습니다. 본 폴더와 로컬 폴더 중 어느 쪽에 있는지는 검체에서 확인합니다.
- 아래 표와 칸은 파이어폭스 소스의 개발 중인 최신 코드(main 가지, 2026-09-23)에서 확인한 것입니다. 이때 DB 스키마 버전 상수(`DB_SCHEMA_VERSION`)는 5 입니다.
- 예전 스키마 버전에 어느 표와 칸이 있었는지, 각 버전이 어느 출시판에 들어갔는지는 확인하지 못했습니다.

## 구조

저장 형식은 SQLite 입니다. 페이지와 레코드를 읽는 법은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

### 표

| 표 | 담는 것 |
|---|---|
| `moz_formhistory` | 입력란 이름과 값 한 쌍마다 한 행입니다 |
| `moz_deleted_formhistory` | 지운 항목의 `guid` 와 지운 시각입니다. 안드로이드판만 씁니다 |
| `moz_sources` | 출처 문자열입니다. 값의 뜻은 확인하지 못했습니다 |
| `moz_history_to_sources` | `moz_formhistory` 행과 `moz_sources` 행을 잇습니다 |

### `moz_formhistory` 의 칸

| 칸 | 뜻 |
|---|---|
| `id` | 행 번호입니다 |
| `fieldname` | 입력란 이름입니다. 비워 둘 수 없습니다 (TEXT NOT NULL) |
| `value` | 입력란에 친 값입니다. 비워 둘 수 없습니다 (TEXT NOT NULL) |
| `timesUsed` | 그 값을 쓴 횟수입니다 |
| `firstUsed` | 처음 쓴 시각입니다 |
| `lastUsed` | 마지막으로 쓴 시각입니다 |
| `guid` | 항목 식별자입니다. 지운 항목 표와 이 값으로 이어집니다 |

- 이 표에는 사이트 주소 칸이 없습니다. 어느 사이트에서 친 값인지는 이 표만으로 알 수 없습니다.
- `value` 는 텍스트 칸입니다. 친 값을 글자 그대로 읽을 수 있습니다.

### `moz_deleted_formhistory` 의 칸

- `id`, `timeDeleted`, `guid` 입니다.
- 입력란 이름과 값은 이 표에 없고 지운 항목은 `guid` 로만 가리킵니다.
- Windows 판은 이 표에 행을 쓰지 않으므로 Windows 검체에서 이 표가 비어 있어도 지운 항목이 없다는 뜻이 아닙니다.

### 색인

- `moz_formhistory_index` 는 `fieldname` 을 색인합니다.
- `moz_formhistory_lastused_index` 는 `lastUsed` 를 색인합니다.
- `moz_formhistory_guid_index` 는 `guid` 를 색인합니다.

### 관련 설정

- 소스는 `browser.formfill` 아래 설정을 읽습니다. `enable`, `expire_days`, `agedWeight`, `boundaryWeight`, `bucketSize`, `debug`, `maxTimeGroupings`, `prefixWeight`, `timeGroupingSize` 입니다.
- 분석에서 먼저 볼 설정은 `enable` 과 `expire_days` 입니다. `expire_days` 는 항목을 며칠 뒤에 지울지 정합니다.
- `expire_days` 의 기본값은 확인하지 못했습니다. 설정 파일의 형식도 확인하지 못했습니다. [프로필 구조 (profiles.ini·prefs.js)](profiles-ini-prefs-js.md) 를 참고합니다.

### 확인하지 못한 것

- `moz_sources.source` 에 들어가는 값의 뜻입니다.
- 비밀번호 칸이나 카드 번호 칸의 값을 저장하지 않는지입니다.
- 브라우저 검색창에 친 검색어가 이 파일에 어떤 입력란 이름으로 들어가는지입니다.
- 사생활 보호 창 (Private Browsing) 에서 친 값을 저장하는지입니다. 참고한 소스 파일(`FormHistory.sys.mjs`)에는 사생활 보호 창을 다루는 코드가 없었습니다. 다른 곳에서 처리할 수 있으므로 어느 쪽으로도 단정하지 않습니다.

## 증거로서 의미

### 증명하는 것

- 이 프로필에서 `fieldname` 이름의 입력란에 `value` 값을 친 기록이 있습니다.
- `timesUsed` 는 그 값을 쓴 횟수입니다.
- `firstUsed` 는 처음 쓴 시각이고, `lastUsed` 는 마지막으로 쓴 시각입니다.
- (안드로이드판) `moz_deleted_formhistory` 의 한 행은 그 시각에 양식 기록 항목 하나를 지운 기록입니다. 지운 시각이 한곳에 몰려 있으면 한꺼번에 지운 흔적일 수 있습니다.

### 증명하지 못하는 것

- 어느 사이트에서 친 값인지는 `moz_formhistory` 에 없습니다. 같은 이름의 입력란은 여러 사이트에 있을 수 있습니다.
- 친 값을 서버로 보냈는지는 알 수 없습니다.
- 처음과 마지막 사이의 각 사용 시각은 남지 않습니다.
- 키보드 앞의 사람이 누구인지는 알 수 없습니다.
- 행이 없다고 입력하지 않은 것은 아닙니다. 기록 기능이 꺼져 있었거나, 만료로 지웠거나, 사용자가 지웠을 수 있습니다.
- 지운 항목 표에는 값이 없습니다. 무엇을 지웠는지는 이 표만으로 알 수 없습니다. Windows 판에서는 지운 사실 자체도 이 표에 남지 않습니다.

보고서에는 "그 사이트에 그 값을 입력했다" 대신 "이 프로필의 양식 기록에 입력란 이름 X, 값 Y 인 항목이 있다. 쓴 횟수는 N 이고, 처음 쓴 시각은 A(UTC), 마지막으로 쓴 시각은 B(UTC) 이다" 처럼 씁니다.

## 시각 해석

- `firstUsed`, `lastUsed`, `timeDeleted` 는 1970년 1월 1일 00:00 UTC 부터 센 마이크로초입니다. 파이어폭스 소스는 이 단위를 PRTime 이라고 부릅니다.
- 현지 시각이 아닙니다. 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.
- 처음 저장할 때 `firstUsed`·`lastUsed` 를 그때 시각으로, `timesUsed` 를 1 로 씁니다.
- 같은 값을 다시 쓰면 `timesUsed` 를 1 올리고 `lastUsed` 만 그때 시각으로 바꿉니다. `firstUsed` 는 그대로입니다.
- 만료 판정에는 `lastUsed` 를 씁니다. 오래 쓰지 않은 값이 먼저 사라집니다.
- 여러 기록을 한 시간 축에 놓을 때는 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 을 따릅니다.

## 함정과 한계

- **원본 프로필로 브라우저를 켜지 않습니다.** 파이어폭스는 만료된 항목을 스스로 지웁니다. 해시를 기록한 사본으로 분석합니다.
- **저널 파일을 함께 뜹니다.** 이 파일의 저널 방식은 확인하지 못했습니다. 같은 폴더에 `formhistory.sqlite-wal` 이나 `formhistory.sqlite-journal` 이 있으면 함께 사본으로 뜹니다. [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 를 참고합니다.
- **입력란 이름으로 사이트를 단정하지 않습니다.** `email`, `q` 같은 이름은 여러 사이트가 함께 씁니다. 사이트는 방문 기록의 시각과 맞춰 좁힙니다.
- **지운 항목은 옛 사본과 견줘 찾습니다.** Windows 판에는 지운 항목 표에 행이 없습니다. 섀도 복사본 속 옛 파일에만 있는 `guid` 를 찾고, SQLite 의 빈 공간과 메모리도 봅니다. [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 과 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 를 참고합니다.
- **민감한 값이 평문으로 나옵니다.** 이름·주소·전화번호 같은 개인정보가 들어 있을 수 있습니다. 보고서에 옮길 때는 필요한 만큼만 적습니다.

## 직접 분석해 보기

### 헥스로 한 번

`lastUsed` 는 마이크로초 정수입니다. SQLite 레코드는 정수를 빅엔디언으로 저장합니다. 아래는 2024-03-15 09:30:00 UTC 를 명세대로 만든 예시입니다. 특정 검체에서 나온 값이 아닙니다.

```
00 06 13 AF A6 DD 76 00    = 1710495000000000 (마이크로초)
1710495000000000 ÷ 1,000,000 = 1710495000 초 (1970-01-01 부터)
→ 2024-03-15 09:30:00 UTC
```

- `firstUsed`·`timeDeleted` 도 같은 방식으로 읽습니다.

### 공개 도구로 한 번

`formhistory.sqlite` 와 저널 파일을 함께 사본으로 뜬 뒤, SQLite 명령줄 도구를 읽기 전용으로 열어 아래처럼 조회합니다.

```sql
SELECT fieldname, value, timesUsed,
       datetime(firstUsed / 1000000, 'unixepoch') AS first_utc,
       datetime(lastUsed  / 1000000, 'unixepoch') AS last_utc,
       guid
FROM moz_formhistory
ORDER BY lastUsed;

SELECT guid,
       datetime(timeDeleted / 1000000, 'unixepoch') AS deleted_utc
FROM moz_deleted_formhistory
ORDER BY timeDeleted;
```

두 번째 조회는 안드로이드판에서만 행이 나옵니다.

지운 항목을 찾으려면 섀도 복사본에서 꺼낸 옛 파일을 붙여, 옛 파일에만 있는 `guid` 를 뽑습니다. 아래 `old_formhistory.sqlite` 는 옛 사본의 파일 이름을 대신한 이름입니다. 여기서 나온 행은 옛 사본 이후에 지웠거나 만료된 항목입니다.

```sql
ATTACH 'old_formhistory.sqlite' AS old;

SELECT o.guid, o.fieldname, o.value, o.timesUsed,
       datetime(o.lastUsed / 1000000, 'unixepoch') AS last_utc
FROM old.moz_formhistory o
WHERE o.guid NOT IN (SELECT guid FROM main.moz_formhistory);
```

- DB Browser for SQLite 같은 범용 뷰어로 같은 표를 볼 수 있습니다. 브라우저 기록 전용 공개 도구의 결과는 위 조회 결과와 한 번 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 방문·다운로드·즐겨찾기 | `lastUsed` 무렵에 연 페이지로 어느 사이트에서 쳤는지 좁힙니다 | [places.sqlite](places-sqlite.md) |
| 세션 복원 | 그 시각에 열려 있던 탭을 봅니다 | [세션 복원 (sessionstore.jsonlz4)](sessionstore-jsonlz4.md) |
| 저장 비밀번호 | 로그인 정보를 저장한 사이트 목록과 견줍니다 | [저장 비밀번호 (logins.json·key4.db)](logins-json-key4-db.md) |
| 섀도 복사본 | 지운 항목이 남은 옛 파일을 꺼냅니다 | [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 크롬 계열 자동완성 | 같은 값을 다른 브라우저에도 쳤는지 봅니다 | [크롬 계열 브라우저](../chrome-edge-whale/index.md) |

웹 사용 전체를 재구성하는 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) 에 있습니다.

## 실습

파이어폭스를 쓴 공개 검체(NIST CFReDS 등)에서 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. `moz_formhistory` 에서 `timesUsed` 가 가장 큰 항목은 무엇입니까? 처음과 마지막으로 쓴 시각은 언제입니까?
2. `moz_deleted_formhistory` 에 행이 있습니까? 검체가 Windows 판이라면 행이 없는 것이 맞는지 확인합니다.
3. 섀도 복사본 속 옛 파일에만 있는 `guid` 를 찾아봅니다. 그 항목의 `lastUsed` 로 보아 만료로 사라졌을 수 있습니까?
4. 한 항목의 `lastUsed` 전후 몇 분의 방문 기록을 봅니다. 그 값을 어느 사이트에서 쳤다고 좁힐 수 있습니까?

## 참고 문헌

1. Mozilla, *FormHistory.sys.mjs* (파이어폭스 소스, main 가지 — 파일 이름, 스키마 버전, 표·칸·색인, 시각 단위, `browser.formfill` 설정, 만료 처리, 칸 갱신, 안드로이드에서만 지운 항목 표에 쓰는 조건). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/components/satchel/FormHistory.sys.mjs
2. Mozilla, *nsINavHistoryService.idl* (파이어폭스 소스, main 가지 — PRTime 정의). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/components/places/nsINavHistoryService.idl
