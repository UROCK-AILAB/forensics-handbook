---
title: "대화 DB 구조"
parent: "메시지"
grand_parent: "아티팩트 · 통화·메시지·연락처"
nav_order: 470
---

# 대화 DB 구조 (sms.db)

## 한 줄 요약

sms.db 는 메시지 앱이 iMessage·SMS 대화를 저장하는 SQLite 데이터베이스이고, 메시지 한 건은 `message` 표의 한 행으로 들어가며 상대·대화방·첨부는 연결 표를 거쳐 이어 붙여야 한 줄의 대화로 읽힙니다.

## 무엇을 기록하나 · 왜 생기나

메시지 앱(번들 ID `com.apple.MobileSMS`)으로 주고받은 메시지마다 본문, 보낸 방향, 상대 주소, 쓴 서비스, 보낸·읽은·전달된 시각이 한 행에 남습니다. 상대 전화번호나 이메일 주소는 `handle` 표에 따로 모아 두고 그 주소로 쓴 서비스도 함께 적으며[4], 대화방은 `chat` 표에 한 행씩 둡니다. 그래서 "누가 언제 무엇을 보냈나" 를 보려면 `message` 를 중심으로 `handle`·`chat`·연결 표를 이어 붙여야 합니다.

첨부 파일은 [첨부 파일 (Attachments)](attachments.md)에서, 지운 메시지와 취소·편집의 흔적은 [지운 메시지의 흔적 (Deleted Messages)](deleted-messages.md)에서 다룹니다. SQLite 파일 형식 자체는 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)를 봅니다.

## 위치와 버전별 차이

기기 안에서는 `/private/var/mobile/Library/SMS/sms.db` 에 있습니다[4]. 로컬 백업에서는 HomeDomain 의 `Library/SMS/sms.db` 로 보이고, 백업 안에서 파일을 찾는 방법은 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)에 있습니다.

| iOS 버전 | 달라진 점 | 출처 |
|---|---|---|
| iOS 11 전후 | 날짜 칸이 초 단위에서 나노초 단위로 바뀝니다(대략 iOS 11 부터) | [5] |
| iOS 15 까지 | `associated_message_guid` 로 반응(탭백)을 원래 메시지에 잇고 `attributedBody` 칸도 이미 있지만, 본문은 대개 `text` 에 들어 있습니다 | [5] |
| iOS 16 이후 | 보낸 메시지 취소·편집과 최근 삭제된 항목 복구가 생겼고, `text` 가 NULL 인 행이 잦아져 `attributedBody` 를 꼭 읽어야 합니다 | [2][3][4][5] |

`date_edited`, `date_retracted`, `thread_originator_guid`, `destination_caller_id`, `associated_message_emoji` 는 iOS 16 이후의 `message` 칸으로 알려져 있고[4][5], iLEAPP 도 `destination_caller_id` 를 읽습니다[1]. 그런데 이 다섯 칸이 없는 `message` 표도 있어서, 이 칸 이름을 박아 둔 질의문은 새 버전에서 오류를 낼 수 있습니다. 먼저 `PRAGMA table_info(message);` 로 칸 목록을 확인합니다.

## 구조

sms.db 에는 아래와 같은 표가 있습니다.

```
_SqliteDatabaseProperties  attachment            chat
chat_handle_join           chat_lookup           chat_message_join
chat_recoverable_message_join                    chat_service
deleted_messages           handle                index_state_metrics
kvtable                    message               message_attachment_join
message_processing_task    persistent_tasks      recoverable_message_part
scheduled_messages_pending_cloudkit_delete       sqlite_sequence
sync_chat_slice            sync_deleted_attachments
sync_deleted_chats         sync_deleted_messages
unsynced_removed_recoverable_messages
```

대화를 읽는 데 쓰는 표와 칸은 아래와 같습니다.

| 표 | 칸 | 뜻 |
|---|---|---|
| `message` | `ROWID`, `guid` | 행 번호와 메시지마다 고유한 값입니다. `guid` 는 기기 사이 동기화에 씁니다[4] |
| `message` | `text`, `attributedBody` | 본문입니다. `text` 가 비어 있으면 `attributedBody`(typedstream 형식으로 저장한 NSAttributedString)에서 본문을 꺼냅니다[1] |
| `message` | `handle_id` | 상대를 가리키는 `handle.ROWID` 이고, 0 이면 그룹 메시지입니다[4] |
| `message` | `is_from_me` | 0 이면 받은 메시지, 1 이면 보낸 메시지입니다[1] |
| `message` | `service` | 메시지를 보낸 서비스 이름입니다. 들어가는 값의 목록은 공개된 설명이 없습니다 |
| `message` | `date`, `date_read`, `date_delivered` | 보낸·읽은·전달된 시각입니다[1] |
| `message` | `associated_message_guid`, `associated_message_type` | 반응(탭백)이 가리키는 원래 메시지입니다[5]. `associated_message_type` 은 값 하나하나가 아니라 2000번대·3000번대 범위로 묶어 맞춥니다[5]. 각 값의 뜻은 공개된 설명이 없습니다 |
| `message` | `message_summary_info` | 이진 plist 이고, Siri 로 보낸 메시지면 `com.apple.Siri` 가 들어갑니다[4]. 편집·취소 정보도 여기에 남습니다[5] |
| `handle` | `ROWID`, `id`, `service`, `country`, `uncanonicalized_id`, `person_centric_id` | 상대 번호·이메일과 그 주소로 쓴 서비스입니다[4] |
| `chat` | `ROWID`, `guid`, `chat_identifier`, `service_name`, `display_name` | 대화방입니다. `display_name` 은 채팅 이름입니다[1] |
| `chat_handle_join` | `chat_id`, `handle_id` | 대화방과 참가자를 잇고, 그룹 참가자를 모을 때 씁니다[1] |
| `chat_message_join` | `chat_id`, `message_id`, `message_date` 등 | 대화방과 메시지를 잇습니다[1] |

`message` 표는 칸이 61개이고 `item_type`, `balloon_bundle_id`, `payload_data`, `expressive_send_style_id`, `share_status` 같은 칸도 있지만, 이런 칸의 값 목록은 공개된 설명이 없습니다. `message_processing_task`, `persistent_tasks`, `kvtable`, `sync_chat_slice` 표도 뜻이 알려져 있지 않아 검체에서 확인합니다.

> 그림 자리: message 를 가운데 두고 handle·chat·chat_message_join·chat_handle_join·message_attachment_join 이 이어지는 관계도

`attributedBody` 와 `message_summary_info` 를 풀려면 이진 plist 와 NSKeyedArchiver 를 알아야 하고, 이 내용은 [속성 목록 파일 (plist·NSKeyedArchiver)](../../../01-foundations/data-formats/plist.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** `message` 행 하나는 이 기기의 메시지 DB 에 그 `guid` 의 메시지가 기록되어 있고, `is_from_me` 값에 따라 보낸 것으로 또는 받은 것으로 적혀 있다는 사실을 보여 줍니다. `handle` 을 이어 붙이면 기록된 상대 주소와 서비스를 알 수 있고, `date_read`·`date_delivered` 가 채워져 있으면 읽음·전달 상태를 기록한 시각도 알 수 있습니다.

**증명하지 못하는 것.** `handle.id` 는 전화번호나 이메일 주소일 뿐이라서 그 주소를 실제로 쓴 사람이 누구인지는 따로 밝혀야 합니다. 보낸 메시지로 적혀 있어도 누가 기기를 손에 들고 보냈는지는 이 DB 만으로 알 수 없고, `message_summary_info` 로 Siri 를 거쳐 보낸 메시지인지도 함께 봅니다. 한 행이 어느 기기에서 만들어졌는지 가르는 칸은 알려져 있지 않습니다.

보고서에는 "이 시각에 이 주소와 주고받은 것으로 기록된 메시지가 이만큼 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

날짜 칸은 예전 iOS 에서 UNIX 시각이었고 지금은 대부분 Mac 절대 시각(Cocoa, 2001-01-01 00:00:00 UTC 기준)이며[4], 기준이 UTC 라서 현지 시각으로 바꾸려면 기기의 시간대를 따로 확인합니다. 단위는 대략 iOS 11 부터 나노초이고 예전 백업은 초입니다[5]. 값이 1e12 보다 크면 나노초로 보고 1e9 로 나눈 다음, UNIX 시각으로 바꾸려면 978307200 을 더합니다[5].

| 칸 | 칸이 가리키는 시각 |
|---|---|
| `date` | 메시지를 보내거나 받은 시각 |
| `date_read` | 읽음으로 기록한 시각 |
| `date_delivered` | 전달됨으로 기록한 시각 |

시각 값 전반은 [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

## 함정과 한계

WAL 파일 없이 sms.db 만 열면 최근 메시지가 빠지고 아무 경고도 나오지 않습니다[5]. WAL 파일을 함께 수집하고, sms.db 와 같은 폴더에 둔 사본에서 엽니다.

iOS 16 이후에는 `text` 가 NULL 인 행이 흔해서[5], `text` 만 뽑는 질의문은 본문이 빈 대화를 내놓습니다. `handle_id` 가 0 인 행을 "상대 없음" 으로 읽으면 그룹 메시지를 놓칩니다. iLEAPP 는 보낸 사람 칸을 받은 메시지(`is_from_me` = 0)일 때만 `handle` 에서 채웁니다[1].

`com.apple.imdsmsrecordstore.plist` 의 `IMDSavedDeviceState` 아래에는 `IMDSavedDeviceStateDidRestoreFromBackupKey`, `IMDSavedDeviceStateDidRestoreFromCloudBackupKey`, `IMDSavedDeviceStateDidMigrateFromDifferentDeviceKey`, `IMDSavedDeviceStateDidUpgradeKey` 같은 키가 있습니다. 이름으로는 DB 가 백업 복원이나 기기 이전을 거쳐 들어왔는지와 이어져 보이지만 뜻은 공개된 설명이 없어서, 판단 근거로 쓰려면 [초기화와 복원 흔적 (Erase·Restore)](../../system-account/erase-restore.md)과 함께 봅니다.

## 직접 분석해 보기

### 시각 값을 손으로 한 번 바꾸기

아래 값은 명세로 만든 예시이고 실제 검체에서 나온 값이 아닙니다.

```
date = 700000000000000000        (1e12 보다 크다 → 나노초)
700000000000000000 / 1e9  = 700000000 초 (2001-01-01 UTC 기준)
700000000 + 978307200     = 1678307200 (UNIX 시각)
1678307200                = 2023-03-08 20:26:40 UTC
```

예전 백업처럼 같은 칸에 `700000000` 이 들어 있다면 1e12 보다 작아서 초로 보고 나누지 않은 채 978307200 만 더합니다.

### 대화 한 줄로 이어 붙이기

sqlite3 로 사본을 열어 아래처럼 이어 붙입니다. 칸 이름은 위 표에 적은 것만 썼습니다.

```sql
SELECT
  m.ROWID,
  datetime(CASE WHEN m.date > 1000000000000 THEN m.date / 1000000000 ELSE m.date END
           + 978307200, 'unixepoch')          AS sent_utc,
  m.is_from_me,
  h.id                                         AS handle,
  m.service,
  c.chat_identifier,
  c.display_name,
  m.text,
  length(m.attributedBody)                     AS attributed_len
FROM message m
LEFT JOIN handle h            ON h.ROWID = m.handle_id
LEFT JOIN chat_message_join j ON j.message_id = m.ROWID
LEFT JOIN chat c              ON c.ROWID = j.chat_id
ORDER BY m.date;
```

`text` 가 NULL 이고 `attributed_len` 이 채워진 행은 `attributedBody` 에서 본문을 꺼내야 하는 행입니다.

### 공개 도구로 한 번

iLEAPP 의 `sms.py` 는 `message`, `handle`, `message_attachment_join`, `attachment`, `chat_message_join`, `chat` 을 이어 붙이고, `message.date`·`date_read`·`date_delivered`·`attachment.created_date` 를 시각으로 씁니다[1]. `text` 가 비면 `attributedBody` 에서 본문을 꺼냅니다[1]. 위 질의문 결과와 iLEAPP 결과의 행 수·시각을 맞춰 보면 도구가 빠뜨린 행이 있는지 가릴 수 있고, 맞춰 보는 절차는 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 교차 검증

주소록 이름은 [연락처 (AddressBook)](../contacts.md)에서 `handle.id` 로 찾아 붙이고, 같은 상대와의 통화는 [통화 기록 (CallHistory)](../call-history.md)에서 확인합니다. 메시지 알림은 [알림 기록 (Notifications)](../../app-usage/notifications.md)에, 앱을 쓴 시간대는 [KnowledgeC (knowledgeC.db)](../../app-usage/knowledgec/index.md)와 [바이옴 (Biome)](../../app-usage/biome/index.md)에 남을 수 있어 `message.date` 와 시간대를 맞춰 봅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 검체의 sms.db 로 아래를 풀어 봅니다.

1. `PRAGMA table_info(message);` 로 칸 목록을 뽑고, 이 페이지의 표에 없는 칸과 표에 있는데 검체에 없는 칸을 가려 봅니다.
2. `text` 가 NULL 인 행이 몇 개인지 세고, 그중 `attributedBody` 가 채워진 행에서 본문을 꺼내 봅니다.
3. WAL 을 함께 둔 사본과 빼고 연 사본에서 `message` 행 수를 비교해 봅니다.
4. `handle_id` 가 0 인 행을 골라 `chat_handle_join` 으로 그룹 참가자를 모아 봅니다.

## 참고 문헌

1. iLEAPP, `scripts/artifacts/sms.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/sms.py
2. Apple 지원, "Recover deleted text messages on your iPhone or iPad" — https://support.apple.com/en-us/102615
3. Apple 지원, "How to unsend messages on your iPhone" — https://support.apple.com/en-us/105085
4. Magnet Forensics, "The Meaning of Messages" (2023-03-09) — https://www.magnetforensics.com/blog/the-meaning-of-messages/
5. ChatExport, ChatExportKnowledge README — https://github.com/ChatExport/ChatExportKnowledge
