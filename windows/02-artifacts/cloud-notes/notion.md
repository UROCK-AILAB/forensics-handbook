# 노션 (Notion)

## 한 줄 요약

노션 데스크톱 앱은 `AppData\Roaming\Notion\notion.db` 라는 SQLite 파일에 페이지·데이터베이스·사용자 정보를 둡니다. 중심 표는 `block` 이고, 이 표의 행마다 만든·고친 시각과 만든·고친 사람이 들어 있습니다. 같은 폴더의 맞춤법 사전 파일에는 사용자가 사전에 넣은 단어가 남습니다.

> 이 글은 공개 수집 규칙(KAPE 대상 파일)과 공개 SQL 맵(SQLECmd) 두 가지로 확인한 내용만 씁니다. 노션을 다룬 공개 분석 글은 이번에 열어 보지 못했습니다. "확인하지 못했습니다" 라고 적은 곳은 검체에서 직접 확인합니다.

## 무엇을 기록하나 · 왜 생기나

- 노션은 문서·데이터베이스를 서버에 두는 협업 노트 서비스이고, 데스크톱 앱은 그 내용을 로컬 DB 에 담아 둡니다.
KAPE 대상 파일 설명은 `notion.db` 를 모든 페이지, 데이터베이스, 사용자 등을 담은 SQLite DB 이고 모든 항목의 만든·고친 시각이 들어 있다고 적습니다. 다만 "모든 페이지" 라는 설명의 근거는 적혀 있지 않습니다(아래 "증명하지 못하는 것"). 맞춤법 사전 파일 `Custom Dictionary.txt` 에는 사용자가 맞춤법 사전에 넣은 단어가 남습니다.

## 위치와 버전별 차이

| 파일 | 위치 | 내용 |
|---|---|---|
| `notion.db` | `C:\Users\<USER>\AppData\Roaming\Notion\notion.db` | 로컬 DB (SQLite) |
| `Custom Dictionary.txt` | `C:\Users\<USER>\AppData\Roaming\Notion\Partitions\notion\Custom Dictionary.txt` | 사용자가 사전에 넣은 단어 |

- `Partitions\notion` 폴더와 `Custom Dictionary.txt` 는 Electron(Chromium) 앱의 세션 폴더와 맞춤법 사전 이름 규칙과 같습니다(KAPE 경로에서 추론). 규칙은 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에 있습니다.
- 이 폴더에 `Cache`·`Local Storage`·`IndexedDB` 같은 다른 Chromium 폴더도 있는지는 확인하지 못했습니다.
- 앱 판에 따라 DB 구조가 다른지, 스토어 판이 따로 있는지는 확인하지 못했습니다.
- 노션에 오프라인 모드가 들어온 때와, 그 뒤 로컬에 담아 두는 범위가 바뀌었는지도 확인하지 못했습니다.

## 구조

### notion.db 판정

- SQLECmd 맵은 파일에 `block` 표가 있으면 노션 DB 로 판정합니다.
- SQLite 파일 구조는 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.

### block 표

SQLECmd 맵은 `block` 표에서 아래 칸을 읽습니다.

| 묶음 | 칸 |
|---|---|
| 식별 | `id`, `version`, `type` |
| 위치 | `space_id`, `collection_id`, `parent_id` |
| 내용 | `properties` |
| 만든 때와 사람 | `created_time`, `created_by` |
| 고친 때와 사람 | `last_edited_time`, `last_edited_by` |

- 맵은 이 칸들을 값 그대로 냅니다. 시각 칸도 변환하지 않습니다.
- 칸 이름으로 보면 `parent_id` 는 부모 항목, `space_id` 는 속한 작업 공간, `collection_id` 는 속한 데이터베이스를 가리키는 것으로 보입니다. 칸 이름에서 짐작한 뜻이며 확인하지 못했습니다.
- `properties` 에 제목·본문 텍스트가 어떤 형식으로 들어가는지 확인하지 못했습니다.

### 만든 사람 이름 붙이기

- 맵은 `block.created_by_id` 를 `notion_user.id` 와 `INNER JOIN` 으로 이어 `notion_user.name` 을 "만든 사람 이름" 으로 붙이므로, `notion_user` 에 짝이 없는 `block` 행은 맵 결과에서 빠집니다.
- 맵 쿼리는 `created_by` 와 `created_by_id` 를 둘 다 씁니다. 두 칸이 한 파일에 모두 있는지, 앱 판마다 다른지는 확인하지 못했습니다.
- `block`·`notion_user` 말고 다른 표의 이름은 확인하지 못했습니다.

## 증거로서 의미

### 증명하는 것

- `notion.db` 가 있으면 그 프로필에서 노션 데스크톱 앱이 돈 적이 있습니다.
- `block` 행이 있으면 그 항목이 로컬 DB 에 담긴 적이 있습니다.
- 행마다 만든·고친 시각과 만든·고친 사람 ID 를 알 수 있습니다.
- `notion_user` 와 이으면 만든 사람의 노션 계정 이름을 알 수 있습니다.
- `Custom Dictionary.txt` 의 단어는 이 프로필에서 누군가 사전에 넣은 말입니다. 사람 이름, 회사 용어, 사건 관련 단어가 들어 있으면 단서가 됩니다.

### 증명하지 못하는 것

- `notion.db` 에 계정의 모든 페이지가 들어 있는지, 사용자가 연 페이지만 들어 있는지 확인하지 못했습니다.
- 그래서 DB 에 어떤 페이지가 없다고 그 페이지가 없었거나 지워졌다고 말하지 못합니다.
- 만든 사람은 노션 계정입니다. 이 PC 에서 만들었다는 뜻도, PC 사용자가 그 사람이라는 뜻도 아닙니다. 공유 작업 공간이면 다른 사람이 다른 기기에서 만든 항목일 수 있습니다(추론).
- 지운 항목을 따로 표시하는 칸이 있는지 확인하지 못했습니다.
- 시각 칸의 단위를 확인하지 못했으므로, 변환한 시각은 검증한 뒤에 씁니다.

보고서에는 "사용자가 X 페이지를 만들었다" 대신 이렇게 씁니다. "`notion.db` 의 `block` 표에 `properties` 에 X 가 들어 있는 행이 있다. 이 행의 `created_by` 는 노션 사용자 Y 를 가리키고, `created_time` 값을 Unix 밀리초로 보고 바꾸면 Z(UTC)이다. 단위는 검체의 다른 시각과 맞춰 확인했다."

## 시각 해석

- 맵은 `created_time`·`last_edited_time` 을 바꾸지 않고 그대로 냅니다.
- 단위와 기준은 확인하지 못했습니다.
- 값의 자릿수로 먼저 짐작합니다. 아래는 계산 예시이며 검체 값이 아닙니다.

| 값 예시 | 자릿수 | 짐작 | 변환 결과 |
|---|---|---|---|
| 1704067200 | 10자리 | Unix 초 | 2024-01-01 00:00:00 UTC |
| 1704067200000 | 13자리 | Unix 밀리초 | 2024-01-01 00:00:00 UTC |

- 짐작이 맞는지는 답을 아는 시각으로 확인합니다. 예를 들어 시험용 PC 에서 페이지를 하나 만들고 그 시각과 행의 값을 비교합니다.
- Unix 시각은 UTC 기준입니다. 형식별 변환은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

## 함정과 한계

- **칸 이름이 판마다 다를 수 있습니다.** 맵 쿼리부터 `created_by` 와 `created_by_id` 를 섞어 씁니다. 쿼리 전에 `.schema block` 으로 칸을 확인합니다.
- **담긴 범위를 모릅니다.** "모든 페이지" 라는 설명만 믿고 없는 페이지를 지운 것으로 보지 않습니다.
- **`properties` 형식을 모릅니다.** 원문 그대로 보존하고, 뽑은 텍스트를 보고서에 옮길 때는 원문 값과 함께 적습니다.
- **곁 파일을 함께 모읍니다.** `notion.db` 와 이름이 같은 `-wal`·`-journal`·`-shm` 파일이 있으면 같이 둡니다. 뜻은 [WAL과 롤백 저널](../../01-foundations/database-log-formats/sqlite/wal-journal-shm.md) 에 있습니다.
- **지운 행은 파일 안 빈 공간에 남을 수 있습니다.** 찾는 법은 [파일 안에 남은 지운 레코드](../../01-foundations/database-log-formats/sqlite/freelist-freeblock.md) 에 있습니다.
- **공개 자료가 적습니다.** 이 글은 수집 규칙과 SQL 맵 두 가지에 기댑니다. 표 구조는 검체로 넓혀 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

1. `AppData\Roaming\Notion` 폴더를 하위 폴더째 사본으로 뜹니다. 분석은 사본에서만 합니다.
2. `notion.db` 를 헥스 편집기로 열어 맨 앞이 SQLite 머리 문자열인지 봅니다.
3. 조사 대상 페이지 제목 하나를 검색합니다. 찾은 자리 앞뒤를 보고 `properties` 값이 어떤 모양인지 적어 둡니다.
4. 같은 제목을 `-wal` 파일에서도 찾아봅니다. 본 DB 와 다른 내용이 나오면 아직 반영되지 않은 변경일 수 있습니다.
5. 시각 칸 값을 하나 골라 위 표처럼 자릿수로 단위를 짐작합니다.

### 공개 도구로 한 번

- KAPE 대상 `Notion` 은 `notion.db` 와 `Custom Dictionary.txt` 를 모읍니다.
- SQLECmd 는 맵 `Windows_Notion_Entries` 로 `notion.db` 에서 `block` 행과 만든 사람 이름을 뽑습니다.
- SQLite 명령줄 도구(sqlite3) 같은 공개 도구로 직접 확인할 때는 아래처럼 뽑아 봅니다. 칸 이름은 먼저 `.schema` 로 확인합니다.

```sql
SELECT b.id, b.type, b.parent_id, b.space_id,
       b.created_time, b.last_edited_time,
       u.name AS created_by_name, b.properties
FROM block AS b
LEFT JOIN notion_user AS u ON b.created_by_id = u.id;
```

- SQLECmd 결과와 직접 뽑은 결과의 행 수가 같은지 비교합니다. 위 쿼리는 `LEFT JOIN` 이라 만든 사람을 찾지 못한 행도 남깁니다. 직접 뽑은 쪽이 더 많으면, 그 차이가 맵의 `INNER JOIN` 에서 빠진 행입니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 크롬 계열 앱 공통 구조 | `Partitions\notion` 아래 다른 Chromium 폴더를 읽는 법을 봅니다 | [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) |
| 설치 프로그램 | 노션 앱이 설치된 적이 있는지 봅니다 | [설치 프로그램](../system-account/uninstall.md) |
| 프리페치 | 노션 실행 시각을 `last_edited_time` 과 맞춰 봅니다 | [프리페치](../execution/prefetch/index.md) |
| SRUM | 그 시간대에 노션 앱이 네트워크로 얼마나 주고받았는지 봅니다 | [SRUM](../execution/system-resource-usage-monitor/index.md) |
| 섀도 복사본 활용 | 예전 시점의 `notion.db` 와 비교해 사라진 행을 찾습니다 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 자료 유출 시나리오 | 노션에 옮겨 적은 자료를 다른 흔적과 묶어 봅니다 | [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) |

## 실습

노션 데스크톱 앱이 깔린 공개 검체(NIST CFReDS 등)를 구하거나, 시험용 PC 에 앱을 깔고 시험용 계정으로 페이지를 몇 개 만든 뒤 아래 질문을 풀어 봅니다.

1. `notion.db` 의 표 목록을 뽑습니다. `block` 과 `notion_user` 말고 어떤 표가 있습니까?
2. `block` 표에 `created_by` 와 `created_by_id` 가 둘 다 있습니까?
3. 직접 만든 페이지의 `created_time` 값은 몇 자리입니까? 만든 시각과 맞추면 단위는 무엇입니까?
4. 그 페이지의 `properties` 값은 어떤 모양입니까? 제목이 평문으로 보입니까?
5. 한 번도 열지 않은 페이지도 `block` 표에 있습니까?
6. `Custom Dictionary.txt` 에 단어를 하나 넣고, 파일이 언제 어떻게 바뀌는지 봅니다.

## 참고 문헌

1. Eric Zimmerman 외, KapeFiles GitHub 저장소 (커밋 ed0f9c7), `Targets/Apps/Notion.tkape` — https://github.com/EricZimmerman/KapeFiles
2. Eric Zimmerman 외, SQLECmd GitHub 저장소 (커밋 7f89270), `SQLMap/Maps/Windows_Notion_Entries.smap` — https://github.com/EricZimmerman/SQLECmd
