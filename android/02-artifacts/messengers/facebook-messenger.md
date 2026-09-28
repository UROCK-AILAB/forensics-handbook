---
title: "페이스북 메신저"
parent: "아티팩트 · 메신저"
nav_order: 990
---

# 페이스북 메신저 (Messenger)

페이스북 메신저 Android 앱의 대화 DB 는 예전 구조 `threads_db2` 와 새 구조 `msys_database_` 두 가지가 있고, 어느 쪽이든 메시지·첨부·반응·연락처를 SQLite 표로 남기며 시각은 유닉스 밀리초로 적습니다.

## 무엇을 기록하나 · 왜 생기나

메신저 앱은 대화방별 메시지와 첨부, 반응, 연락처를 기기의 DB 에 저장하고, 새 구조에서는 통화 기록도 표로 따로 둡니다[1]. 앱 버전에 따라 예전 구조(`threads_db2`)와 새 구조(`msys_database_`) 가운데 어느 쪽이 남는지 다르므로, 실제 데이터에서 어느 구조가 있는지부터 봅니다.

## 위치와 버전별 차이

DB 파일은 다음 세 가지 이름 패턴으로 찾고, 패턴에 패키지 이름은 들어 있지 않습니다[1].

```
*/*threads_db2-uid
*/msys_database*
*/*threads_db2
```

앱 패키지 이름은 `com.facebook.orca` 로 알려져 있으니, 실제 기기에서는 [설치된 앱](../app-usage/packages/index.md) 기록과 실제 파일이 나온 폴더로 확인합니다. DB 는 패턴처럼 파일 이름으로 찾되, 찾은 파일이 어느 앱 폴더에서 나왔는지를 함께 적어야 다른 앱의 같은 이름 파일과 섞이지 않습니다. 앱 폴더를 읽는 법은 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md)를 봅니다.

| 구조 | 파일 | 통화 기록 | 실제 데이터로 확인할 것 |
|---|---|---|---|
| 예전 | `threads_db2`, 사용자 ID 가 든 텍스트 파일 `threads_db2-uid` | 따로 된 표 없음. 관리 메시지 안의 JSON 에 있음 | 바뀐 앱 버전 |
| 새 | `msys_database_` 뒤에 사용자 ID 로 보이는 값이 붙은 파일 | `call_log` 표 | 바뀐 앱 버전, 종단 간 암호화 대화가 기본이 된 뒤 로컬 DB 가 바뀌었는지 |

Android 버전과 삼성 One UI 에 따른 차이는 실제 기기에서 확인해야 합니다.

## 구조

### 새 구조 — msys_database_

| 표 | 열 |
|---|---|
| `messages` | `timestamp_ms`, `sender_id`, `thread_key`, `text`, `is_admin_message`, `message_id` |
| `attachments` | `message_id`, `title_text`, `subtitle_text`, `filename`, `playable_url_mime_type`, `playable_url` |
| `attachment_ctas` | `message_id`, `native_url` |
| `reactions` | `message_id`, `reaction`, `reaction_creation_timestamp_ms` |
| `call_log` | `call_timestamp_ms`, `call_duration`(초), `call_direction`, `call_media_type`, `has_been_seen`, `thread_key` |
| `contacts` | `id`, `name`, `normalized_name_for_search`, `username`, `profile_picture_large_url`, `email_address`, `phone_number`, `is_messenger_user`, `friendship_status`, `birthday_timestamp`(유닉스 초) |

첨부·반응 표는 `message_id` 로 메시지와 이어지고, 메시지와 통화는 `thread_key` 로 대화방을 가리킵니다. `sender_id` 를 `contacts.id` 와 이어 붙이면 보낸 사람 이름을 붙일 수 있습니다.

### 예전 구조 — threads_db2

| 표 | 열 |
|---|---|
| `messages` | `timestamp_ms`, `sender`(JSON), `thread_key`, `text`, `snippet`, `attachments`(JSON), `shares`(JSON), `msg_id`, `msg_type`, `generic_admin_message_extensible_data`(JSON) |
| `threads` | `thread_key` |
| `message_reactions` | `msg_id`, `reaction`, `reaction_timestamp`(세대마다 이름이 다를 수 있음) |
| `thread_users` | `user_key`, `first_name`, `last_name`, `username`, `profile_pic_square`(JSON), `is_messenger_user`, `is_friend`, `friendship_status`, `contact_relationship_status` |

예전 구조는 여러 열에 JSON 문자열을 넣습니다. `sender` 에는 `$.name` 과 `$.user_key` 가, `attachments` 에는 `$[0].filename` 이, `shares` 에는 `$[0].name`, `$[0].description`, `$[0].href` 가 들어 있습니다[1]. `thread_users.user_key` 는 앞 9글자 뒤가 사용자 ID 입니다.

예전 구조에는 통화 기록 표가 따로 없고, `generic_admin_message_extensible_data` 가 있는 관리 메시지 행의 JSON 에 통화 정보(`$.call_duration`, `$.caller_id`, `$.video`)가 들어 있습니다[1]. ALEAPP 는 대화 목록을 만들 때 `msg_type` 이 -1 인 행과 이런 관리 메시지 행을 뺍니다.

## 증거로서 의미

**증명하는 것.** `messages` 에 행이 있으면 그 `thread_key` 대화방에 그 시각으로 적힌 메시지 기록이 기기의 DB 에 있었다는 뜻이고, 첨부 파일 이름·공유 링크·반응도 메시지별로 이어 볼 수 있습니다. 새 구조의 `call_log` 는 통화 시각·길이·방향·음성 또는 영상 여부를, `contacts` 는 앱이 저장해 둔 상대의 이름·사용자 이름·전화번호·메일 주소를 보여 줍니다.

**증명하지 못하는 것.** 연락처 표의 이름과 번호는 어디서 온 값인지 정해져 있지 않아서, 그 사람이 실제로 그 번호를 쓰는지는 따로 확인해야 합니다. ALEAPP 는 `call_direction` 1 을 건 통화, 2 를 받은 통화로, `call_media_type` 2 를 영상 통화로 읽지만, 이 대응은 도구가 정한 것이라 앱 버전마다 맞는지 실제 데이터로 확인해야 합니다. `friendship_status` 같은 열은 값 뜻이 공개되지 않았으므로, 알려진 통화·연락처 몇 건으로 값을 먼저 맞춰 본 뒤 "걸었다", "영상 통화였다" 를 씁니다. 첨부 표의 `playable_url` 은 원격 주소일 수 있고, 주소가 있다고 파일이 기기에 저장됐다고 볼 수는 없습니다.

## 시각 해석

열 이름 끝이 `_ms` 인 시각은 유닉스 밀리초이고, `datetime(칸/1000,'unixepoch')` 로 바꿉니다[1]. 예전 구조의 `message_reactions.reaction_timestamp` 도 이름에 `_ms` 는 없지만 1000 으로 나눠 씁니다[1]. `threads_db2` 세대마다 이 열 이름이 `reaction_timestamp`, `reaction_timestamp_ms`, `reaction_creation_timestamp_ms`, `reaction_creation_time_ms` 네 가지로 달라서[1], 실제 DB 에서 열 이름을 먼저 확인합니다. 새 구조의 `contacts.birthday_timestamp` 만 유닉스 초입니다. 유닉스 시각은 UTC 기준이라서, 현지 시각이 필요하면 [시간대와 시각 설정](../system-account/time-zone.md)을 함께 봅니다.

예전 구조에서 통화를 관리 메시지로 읽을 때, ALEAPP 는 통화 시작 시각을 `timestamp_ms/1000` 에서 통화 길이를 빼서 구합니다. 그러니 메시지 행의 시각을 통화가 끝난 무렵의 시각으로 다루는 셈이고, 도구 결과의 통화 시작 시각은 이 계산을 거친 값입니다. `timestamp_ms` 가 0 인 행은 ALEAPP 가 시각을 비워 두므로, 도구 결과에서 시각이 빈 행은 원본 값이 0 인지 확인합니다. 단위 판별은 [시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

## 함정과 한계

- 한 기기에서 `threads_db2` 와 `msys_database_` 가 함께 나오면 각각 따로 뽑고, 같은 메시지가 두 번 세지지 않는지 시각과 본문으로 대조합니다.
- 파일 이름 패턴만으로 찾으면 다른 앱의 비슷한 이름 파일이 섞일 수 있어서, 파일이 나온 폴더를 확인합니다.
- ALEAPP 결과의 대화 목록에는 관리 메시지와 `msg_type` 이 -1 인 행이 빠져 있습니다. 원본 표의 행 수와 도구 결과의 행 수가 다른 이유가 이것인지 먼저 확인합니다.
- 종단 간 암호화 대화가 로컬 DB 에 어떻게 남는지는 시험 기기에서 암호화 대화를 주고받은 뒤 DB 를 열어 확인합니다. 이 핸드북은 암호를 푸는 절차를 다루지 않습니다.
- 지운 메시지가 DB 에 남는지는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

예전 구조의 `sender` 열은 JSON 텍스트라서, 레코드를 헥스로 보면 `{`(0x7B) 와 큰따옴표(0x22)로 시작하는 ASCII 글자열이 보입니다. 이 모양을 알면 헥스 편집기에서 `"user_key"` 같은 글자열(`22 75 73 65 72 5F 6B 65 79 22`)을 찾아 해당 레코드 위치로 바로 갈 수 있습니다. 바이트 값은 ASCII 표로 만든 예시이고, 실제 데이터에서 나온 값이 아닙니다.

통화 시작 시각 계산도 값 하나로 따라가 봅니다. 다음은 만든 값입니다.

```
timestamp_ms   = 1758800000000   → /1000 → 1758800000 (2025-09-25 11:33:20 UTC)
call_duration  = 200 (초)
통화 시작 시각 = 1758800000 - 200 = 1758799800 (2025-09-25 11:30:00 UTC)
```

### 공개 도구로 한 번

ALEAPP 의 `FacebookMessenger.py` 는 두 구조를 모두 읽습니다. 결과를 확인하려고 `sqlite3` 로 새 구조 사본을 열어 메시지에 보낸 사람 이름을 붙여 봅니다.

```sql
SELECT datetime(m.timestamp_ms/1000, 'unixepoch') AS time_utc,
       m.thread_key, m.sender_id, c.name AS sender_name,
       m.text, m.is_admin_message, a.filename
FROM messages m
LEFT JOIN contacts c    ON c.id = m.sender_id
LEFT JOIN attachments a ON a.message_id = m.message_id
ORDER BY m.timestamp_ms;
```

예전 구조에서는 SQLite 의 JSON 함수로 보낸 사람 이름을 꺼냅니다.

```sql
SELECT datetime(timestamp_ms/1000, 'unixepoch') AS time_utc, thread_key,
       json_extract(sender, '$.name') AS sender_name, text, msg_type
FROM messages
ORDER BY timestamp_ms;
```

도구 결과와 직접 뽑은 결과의 건수가 다르면 [도구 검증](../../03-techniques/reporting/tool-validation.md)의 방법대로 원인을 찾습니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [설치된 앱](../app-usage/packages/index.md) | 실제 패키지 이름과 앱 버전 |
| [계정](../system-account/accounts/index.md) | 기기에 페이스북 계정이 등록돼 있는지 |
| [통화 기록](../communications/call-log.md) | 기본 통화와 메신저 통화를 한 시간선에 놓기 |
| [연락처](../communications/contacts.md) | `contacts.phone_number` 가 기기 주소록의 누구와 맞는지 |
| [알림 기록](../app-usage/notification-history.md) | 받은 메시지 알림의 제목과 시각 |

여러 메신저를 한 시간선에 모으는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md)에서 다룹니다.

## 실습

공개 시험 이미지(NIST CFReDS 등) 가운데 페이스북 메신저가 설치된 Android 이미지를 골라 다음 질문을 풀어 봅니다.

1. 이미지에 있는 DB 는 `threads_db2` 와 `msys_database_` 중 어느 쪽인가요? 파일은 어느 폴더에서 나왔나요?
2. `threads_db2-uid` 가 있다면 안에 든 사용자 ID 가 `thread_users.user_key` 의 ID 부분과 맞나요?
3. 예전 구조라면 관리 메시지 행 가운데 통화로 보이는 것이 몇 건이고, 각 통화의 시작 시각은 언제인가요?
4. 원본 `messages` 표의 행 수와 ALEAPP 결과의 메시지 건수를 비교하고, 차이가 나는 이유를 설명해 보세요.

## 참고 문헌

1. ALEAPP — FacebookMessenger.py. https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/FacebookMessenger.py
2. ALEAPP — scripts/artifacts 폴더 목록(GitHub API). https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
