---
title: "구글 Keep"
parent: "아티팩트 · 구글 입력·음성 비서"
nav_order: 1200
---

# 구글 Keep (Google Keep)

구글 Keep 은 메모와 체크리스트를 앱 데이터 폴더의 `keep.db` 한 파일에 모읍니다. 노트 한 건의 제목과 시각, 마지막으로 고친 사람의 이메일은 `tree_entity` 표에, 본문과 체크리스트 항목은 `list_item` 표에, 공유한 상대는 `sharing` 표에 남고, 시각은 모두 유닉스 밀리초입니다[1][2][3]. 노트와 항목마다 삭제 표시 열이 따로 있어서, 지운 노트도 행이 남아 있으면 내용을 읽을 수 있습니다[2][3].

## 무엇을 기록하나 · 왜 생기나

구글 Keep 의 패키지 이름은 `com.google.android.keep` 이고, 노트는 구글 계정과 동기화됩니다[3]. 사용자가 노트를 만들거나 고치면 `keep.db` 의 행이 생기거나 바뀌고, 노트에 넣은 이미지는 앱 데이터 폴더의 `files/` 아래에 파일로 저장됩니다[3].

한 기기에 구글 계정이 둘 이상 있으면 `account` 표에 계정마다 행이 생기고, 다른 표는 `account_id` 로 이 표를 가리킵니다[3]. 그래서 노트마다 어느 계정의 노트인지 알 수 있습니다. 다른 사람과 공유한 노트는 공유 상대의 이메일이 `sharing` 표에 남고, 마지막으로 고친 사람의 이메일은 `tree_entity.last_modifier_email` 에 남습니다[1][2].

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 패키지 | `com.google.android.keep` |
| 노트 데이터베이스 | `/data/data/com.google.android.keep/databases/keep.db` (딸린 `-wal`·`-shm`·`-journal` 파일 포함) |
| 노트에 넣은 이미지 | `/data/data/com.google.android.keep/files/1/image/original/` |

데이터베이스 경로는 [1][2][3], 이미지 폴더는 [3] 이 근거입니다. Android 14 를 쓴 Pixel 7a 에서도 `keep.db` 는 같은 `databases` 폴더에 있습니다[4]. 앱 데이터 폴더의 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 를 봅니다.

`keep.db` 의 짜임은 앱 판에 따라 다릅니다. 새 판에는 노트 본문을 검색용으로 한 번 더 담는 표 `text_search_note_content_content` 가 있고, 예전 판에는 이 표가 없어 본문이 `list_item` 표에만 있습니다[1]. ALEAPP 모듈 두 개의 시험 자료는 아래와 같습니다.

| ALEAPP 모듈 | Android | Keep 버전 코드 | 결과 행 수 |
|---|---|---|---|
| `keepNotes`[1] | 13 | 220522207, 220589177 | 0 |
| `keepNotes`[1] | 14 | 220548335 | 2 |
| `keepNotes`[1] | 15 | 220627544 | 0 |
| `keepNotes`[1] | 16 | 220663535 | 1 |
| `googleKeepNotes`[2] | 13·14·15·16 | 위와 같은 다섯 자료 | 모두 0 |

같은 자료에서 한 모듈은 행을 내고 다른 모듈은 0행을 내므로, 도구 하나의 0행을 "노트 없음" 으로 적지 않습니다.

## 구조

저장 형식 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 를 봅니다.

### tree_entity 표 — 노트 한 건

| 열 | 뜻 | 근거 |
|---|---|---|
| `_id` | 노트 번호. 다른 표가 이 값으로 노트를 가리킴 | [1][2] |
| `account_id` | `account._id` 를 가리킴 | [3] |
| `title` | 제목 | [1][2][3] |
| `time_created` | 만든 시각 | [1] |
| `time_last_updated` | 마지막으로 바뀐 시각 | [1] |
| `user_edited_timestamp` | 사용자가 고친 시각 | [1] |
| `shared_timestamp` | 공유한 시각 | [2] |
| `last_modifier_email` | 마지막으로 고친 사람의 이메일 | [1][2][3] |
| `is_owner` | 이 계정이 노트 주인인지 | [3] |
| `is_pinned` | 위에 고정했는지 | [3] |
| `is_deleted` | 삭제 표시 | [3] |

### list_item 표 — 본문과 체크리스트 항목

| 열 | 뜻 | 근거 |
|---|---|---|
| `_id` | 항목 번호 | [1][2] |
| `account_id` | `account._id` 를 가리킴 | [2] |
| `list_parent_id` | 항목이 속한 노트의 ID | [2][3] |
| `text` | 노트에 넣은 글 | [1][2][3] |
| `synced_text` | 구글 계정과 동기화된 글 | [2][3] |
| `time_created` | 만든 시각 | [2][3] |
| `time_last_updated` | 마지막으로 바뀐 시각 | [2][3] |
| `is_deleted` | 삭제 표시. ALEAPP 은 1 을 삭제로 표시 | [2][3] |

### 그 밖의 표

| 표 | 열과 뜻 | 근거 |
|---|---|---|
| `account` | `_id`, `name`(구글 계정 이메일) | [2][3] |
| `sharing` | `tree_entity_id`(노트), `email`(공유 상대), `is_deleted`(공유 삭제 표시) | [2] |
| `text_search_note_content_content` | `docid`(= `tree_entity._id`), `c0text`(본문) | [1] |
| `blob` | `files/` 아래 이미지의 파일 크기·이름·MIME 형식, 이미지에서 뽑은 글 | [3] |
| `blob_node` | 노트에 넣은 이미지의 만든 시각과 고친 시각 | [3] |

`blob`·`blob_node`·`tree_entity` 를 이으면 이미지가 어느 노트에 들어 있는지 알 수 있습니다[3]. 이을 때 쓰는 열 이름은 `PRAGMA table_info(blob_node);` 로 확인합니다. `text_search_note_content_content` 는 SQLite 전문 검색(FTS) 표가 내용을 담아 두는 보조 표(shadow table)입니다[1].

ALEAPP 공유 모듈은 쿼리의 `sync_status` 열이 1 이면 "Synced", 아니면 "Not Synced" 로 보여 줍니다[2]. 이 값의 뜻은 공식 문서가 아니라 도구 한 곳의 해석이라서, 보고서에 쓸 때는 그 범위를 함께 적습니다.

## 증거로서 의미

### 증명하는 것

`tree_entity` 의 행 하나는 그 제목의 노트가 이 기기의 Keep 에, `account_id` 가 가리키는 구글 계정 아래 있었다는 기록입니다[3]. `list_item.text` 나 `c0text` 로 본문을 읽을 수 있고, `time_created`·`time_last_updated`·`user_edited_timestamp` 로 만든 때와 바뀐 때를 볼 수 있습니다[1][2].

`sharing` 에 행이 있으면 그 노트를 `email` 의 상대와 공유했다는 기록이고, `last_modifier_email` 이 기기 계정과 다르면 공유받은 사람이 마지막으로 고쳤다는 뜻입니다[1][2]. `is_deleted` 가 1 인 행은 지운 기록이면서 지운 내용을 함께 담고 있습니다[2][3]. `text` 와 `synced_text` 가 다르면 마지막으로 고친 글이 아직 동기화되지 않았을 가능성이 있습니다[3].

### 증명하지 못하는 것

Keep 은 계정과 동기화되므로, 노트를 이 기기에서 썼는지 같은 계정의 다른 기기나 웹에서 쓰고 받아 왔는지는 이 표만으로 구분할 수 없습니다. `last_modifier_email` 도 계정을 가리킬 뿐 기기를 쓴 사람을 가리키지 않습니다([그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)).

`time_last_updated` 는 마지막으로 바뀐 때만 남아서 그 전의 고친 내용은 알 수 없습니다. 이미지에서 뽑은 글은 앱이 이미지에서 읽어 낸 글이라서, 사용자가 직접 친 글로 적지 않습니다[3].

보고서에는 "피의자가 이 메모를 썼다" 가 아니라 "이 기기의 `keep.db` 에 계정 ○○ 아래 제목 ○○ 인 노트가 있고, 만든 시각은 UTC ○○, 마지막으로 바뀐 시각은 UTC ○○, 마지막으로 고친 사람의 이메일은 ○○ 입니다" 처럼 씁니다.

## 시각 해석

| 열 | 값 | 무엇이 바뀔 때 바뀌나 |
|---|---|---|
| `tree_entity.time_created` | 유닉스 밀리초, UTC | 노트를 만든 때 |
| `tree_entity.time_last_updated` | 유닉스 밀리초, UTC | 노트가 바뀐 때 |
| `tree_entity.user_edited_timestamp` | 유닉스 밀리초, UTC | 사용자가 노트를 고친 때 |
| `tree_entity.shared_timestamp` | 유닉스 밀리초, UTC | 노트를 공유한 때 |
| `list_item.time_created`, `list_item.time_last_updated` | 유닉스 밀리초, UTC | 본문·항목을 만들고 바꾼 때 |

ALEAPP 은 이 값들을 1000 으로 나눈 뒤 `unixepoch` 로 바꿔 UTC 로 보여 줍니다[1][2]. `time_last_updated` 와 `user_edited_timestamp` 는 이름으로 보면 동기화 같은 앱 동작으로 바뀐 때와 사용자가 직접 고친 때를 나눠 적는 것일 가능성이 있어서, 두 값이 다르면 둘 다 적습니다. 현지 시각 바꾸기는 [시간대와 시각 설정](../system-account/time-zone.md) 과 [시각 값](../../01-foundations/value-decoding/time-values.md) 을 봅니다.

## 함정과 한계

ALEAPP 의 두 모듈은 쿼리가 달라서 결과도 다릅니다. `keepNotes` 는 검색용 표가 있으면 그 표를, 없으면 `list_item` 을 읽고[1], `googleKeepNotes` 는 `tree_entity._id` 와 `list_item._id` 가 같은 행만 이어 읽습니다[2]. 위 표처럼 시험 자료에서도 결과 행 수가 다르므로, 원본 표를 직접 열어 `SELECT count(*) FROM tree_entity;` 와 비교합니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

본문이 `list_item` 과 검색용 표 두 곳에 들어 있을 수 있으므로, 한쪽에서 지워진 글이 다른 쪽에 남아 있는지 둘 다 봅니다. 휴지통에 넣은 노트를 어떤 열로 표시하는지는 판마다 다를 수 있어서 `PRAGMA table_info(tree_entity);` 로 열 목록을 보고 확인합니다. 행 자체가 사라진 노트는 `keep.db` 의 빈 페이지와 `-wal` 파일에서 찾습니다([삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)).

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 레코드 형식으로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다. SQLite 는 4바이트로는 모자라고 6바이트면 들어가는 정수를 형식 번호 5 로 적습니다. 요즘 시각의 유닉스 밀리초 값이 이 범위라서, `time_created` 는 레코드 안에서 6바이트 정수로 들어갑니다.

```
05                    레코드 머리의 형식 번호 5 = 6바이트 부호 있는 정수
01 92 19 38 B6 00     값 0x1921938B600 = 1727000000000
```

1727000000000 을 1000 으로 나누면 유닉스 초 1727000000 이고, UTC 로 2024-09-22 10:13:20 입니다(만든 예시). 레코드 머리와 본문을 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에 있고, 빈 페이지에서 지운 행을 찾을 때 이 6바이트 모양을 실마리로 씁니다.

### 공개 도구로 한 번

1. 파일 시스템 전체 추출본에서 `databases/keep.db` 를 딸린 파일까지, `files/` 폴더와 함께 복사합니다.
2. SQLite 도구로 열고 `.tables` 와 `PRAGMA table_info(tree_entity);` 로 표와 열을 확인한 뒤 아래처럼 읽습니다.

```sql
SELECT t._id, a.name AS account,
       datetime(t.time_created/1000,'unixepoch')          AS created_utc,
       datetime(t.time_last_updated/1000,'unixepoch')     AS updated_utc,
       datetime(t.user_edited_timestamp/1000,'unixepoch') AS edited_utc,
       t.title, t.last_modifier_email, t.is_deleted
FROM tree_entity t LEFT JOIN account a ON t.account_id = a._id
ORDER BY t.time_created;

SELECT list_parent_id, text, synced_text, is_deleted,
       datetime(time_last_updated/1000,'unixepoch') AS updated_utc
FROM list_item ORDER BY list_parent_id;
```

3. ALEAPP 으로 같은 폴더를 처리하면 `keepNotes` 는 Time Created, Time Last Updated, User Edited Timestamp, Title, Text, Last Modifier Email 열로[1], `googleKeepNotes` 는 노트 결과와 공유 결과 두 가지로 나옵니다[2].
4. 2단계에서 직접 읽은 행 수와 값을 ALEAPP 결과와 맞춰 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [계정](../system-account/accounts/index.md) | `account.name` 의 구글 계정이 기기에 등록되어 있었는지 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 만든 시각·고친 시각 앞뒤로 Keep 이 앞에 떠 있었는지 |
| [알림 기록](../app-usage/notification-history.md) | 공유받은 노트 알림 |
| [삼성 노트](../samsung/samsung-notes.md) | 같은 기기에서 다른 메모 앱에 비슷한 내용을 적었는지 |

계정에 남은 Keep 데이터를 받는 방법은 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 를, 여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 을, 지운 내용을 찾는 조사 흐름은 [지운 대화와 사진 찾기](../../04-scenarios/activity/deleted-content.md) 를 봅니다.

## 실습

ALEAPP 시험 자료처럼 Keep 이 깔린 공개 Android 이미지(Android 13~16)를 골라 아래 질문을 풀어 봅니다.

1. `keep.db` 에 `text_search_note_content_content` 표가 있습니까? 있다면 `c0text` 와 `list_item.text` 의 글이 같습니까?
2. `account` 표에 계정이 몇 개이고, 노트는 계정마다 몇 건입니까?
3. `is_deleted` 가 1 인 행은 어느 표에 몇 개 있고, 그 행의 제목이나 본문은 무엇입니까?
4. `text` 와 `synced_text` 가 다른 항목이 있습니까?
5. `keepNotes` 와 `googleKeepNotes` 결과의 행 수를 `tree_entity` 행 수와 비교합니다.

## 참고 문헌

1. ALEAPP, scripts/artifacts/keepNotes.py (GitHub main) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/keepNotes.py
2. ALEAPP, scripts/artifacts/googleKeepNotes.py (GitHub main) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/googleKeepNotes.py
3. g4rud4, "Google Keep - Notes and Lists: Mobile Artifacts", bi0s blog, 2021-06-18 — https://blog.bi0s.in/2021/06/18/Forensics/Google-Keep-Notes-and-Lists-Mobile-Artifacts/
4. Mattia Epifani, "A first look at Android 14 forensics", 2024-01-18 — https://blog.digital-forensics.it/2024/01/a-first-look-at-android-14-forensics.html
