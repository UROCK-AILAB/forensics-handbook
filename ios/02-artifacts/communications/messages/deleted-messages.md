---
title: "지운 메시지의 흔적"
parent: "메시지"
grand_parent: "아티팩트 · 통화·메시지·연락처"
nav_order: 490
---

# 지운 메시지의 흔적 (Deleted Messages)

iOS 16 부터 메시지 앱에 최근 삭제된 항목 복구와 보낸 메시지 취소·편집이 생기면서 sms.db 에 삭제·복구용 표가 늘었고, 취소하거나 편집한 메시지는 `message.text` 가 비는 대신 다른 열과 바이옴·알림 기록에 흔적이 남을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 메시지나 대화를 지우면 iOS 16 이후에는 바로 사라지지 않고 "최근 삭제된 항목" 에 머물며, 30~40일 안에 지운 메시지·대화만 복구할 수 있습니다[2]. 이 복구 기능은 iOS 16, iPadOS 16.1 이후에 있습니다[2]. sms.db 에서는 `chat_recoverable_message_join` 이 최근 삭제된 항목을 담고, 이 표는 iOS 16 이후에 있습니다[5].

보낸 메시지 취소는 보낸 뒤 2분 안에 할 수 있고 iOS 16, iPadOS 16.1, macOS Ventura 이후에 쓸 수 있습니다[3]. 이 기능은 iMessage 기준으로 안내되어 있고 SMS·RCS 에서 되는지는 안내에 없습니다. 상대가 예전 OS 를 쓰면 취소해도 상대 화면에 메시지가 남을 수 있습니다[3]. 편집은 보낸 뒤 15분 안에 할 수 있습니다[1][4].

sms.db 의 기본 구조는 [대화 DB 구조 (sms.db)](sms-db.md)에서, 첨부 파일은 [첨부 파일 (Attachments)](attachments.md)에서 다룹니다.

## 위치와 버전별 차이

| iOS 버전 | 삭제·취소·편집 | 출처 |
|---|---|---|
| iOS 15 까지 | 최근 삭제된 항목 복구, 보낸 메시지 취소·편집 기능이 없습니다 | [2][3] |
| iOS 16 이후 | 최근 삭제된 항목(30~40일 안 복구), 취소(2분 안), 편집(15분 안)이 생겼고 `chat_recoverable_message_join` 이 쓰입니다 | [1][2][3][4][5] |

sms.db 에서 삭제와 이어진 표와 열은 아래와 같습니다.

| 표 | 열 |
|---|---|
| `chat_recoverable_message_join` | `chat_id`, `message_id`, `delete_date`, `ck_sync_state` |
| `recoverable_message_part` | `chat_id`, `message_id`, `part_index`, `delete_date`, `part_text`, `ck_sync_state` |
| `unsynced_removed_recoverable_messages` | `ROWID`, `chat_guid`, `message_guid`, `part_index` |
| `deleted_messages` | `ROWID`, `guid` |
| `sync_deleted_messages` | `ROWID`, `guid`, `recordID` |
| `sync_deleted_chats` | `ROWID`, `guid`, `recordID`, `timestamp` |
| `sync_deleted_attachments` | `ROWID`, `guid`, `recordID` |
| `scheduled_messages_pending_cloudkit_delete` | `ROWID`, `guid`, `recordID` |
| `chat` | `is_recovered`, `is_deleting_incoming_messages` |

## 구조

`chat_recoverable_message_join` 은 최근 삭제된 항목에 들어간 메시지를 대화방과 이어 두는 표이지만, `delete_date` 는 늘 채워지지는 않아서 열이 있는지와 값이 있는지를 먼저 확인합니다[5]. `recoverable_message_part`, `deleted_messages`, `sync_deleted_*` 표가 정확히 무엇을 담는지는 공개된 설명이 없어 실제 데이터로 확인해야 합니다. 특히 `recoverable_message_part.part_text` 는 이름만 보면 지운 본문이 남을 것 같지만, 실제 데이터에서 값을 보고 판단합니다.

취소하거나 편집한 메시지는 `message.text` 열이 비워집니다[1][4]. 두 경우 모두 `date_edited` 열에 바뀐 시각이 남는다는 설명이 있지만[4], `date_edited` 열이 없는 `message` 표도 있어서 열이 있는지 먼저 확인합니다. 편집 기록과 취소 정보는 `message_summary_info` 에 들어가고[5], D20 의 시험에서는 `attributedBody` 와 `message_summary_info` 에서 편집 기록을 찾았으며 편집할 때마다 따로 기록되었습니다[1].

설정 파일에도 삭제와 이어진 이름의 키가 있습니다. 값과 뜻은 공개된 설명이 없어 실제 데이터로 확인합니다.

| 파일(HomeDomain, `Library/Preferences/`) | 키 |
|---|---|
| `com.apple.MobileSMS.plist` | `KeepMessageForDays`, `SSKeepMessages`, `KeepMessagesVersionID`, `DeleteVerificationCodes` |
| `com.apple.madrid.plist` | `LocalDBStats` 아래 `deletedMessages`, `deletedRecoverableMessages`, `deletedAttachments`, `deletedChats`, 그리고 `Server.TotalRecords.recoverableMessageDeleteZone` |
| `com.apple.imdsmsrecordstore.plist` | `DeleteSequenceNumber` |

`KeepMessageForDays` 와 `SSKeepMessages` 는 이름으로 보면 메시지 보관 기간 설정과 이어져 보이지만, 설정할 수 있는 값과 자동 삭제가 일어나는 방식은 공개된 설명이 없습니다. `DeleteVerificationCodes` 도 이름으로는 인증 코드 자동 삭제 설정으로 보일 뿐입니다. 설정 plist 를 읽는 법은 [설정 값 (Preferences)](../../system-account/preferences.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** `chat_recoverable_message_join` 에 행이 있으면 그 메시지가 수집 시점에 최근 삭제된 항목에 들어 있었다는 사실을 보여 줍니다[5]. `message.text` 가 비고 `message_summary_info` 에 취소·편집 정보가 있으면 그 메시지가 취소되거나 편집된 기록이 있다는 사실까지 말할 수 있습니다.

**증명하지 못하는 것.** `delete_date` 가 비어 있을 수 있어서[5] 언제 지웠는지를 이 표만으로 늘 알 수는 없습니다. 복구 표에 없다고 지운 메시지가 없었다는 뜻도 아니고, 30~40일이 지난 항목은 복구할 수 없게 됩니다[2]. 취소한 메시지가 상대 기기에서 정말 사라졌는지도 상대 OS 버전에 따라 달라서[3] 이 기기의 기록만으로는 알 수 없습니다. 누가 지웠는지도 이 DB 로는 알 수 없습니다.

보고서에는 "이 대화방의 메시지 몇 건이 수집 시점에 최근 삭제된 항목으로 기록되어 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`delete_date` 의 기준과 단위(Mac 절대 시각 나노초인지)는 공개된 설명이 없습니다. `message.date` 를 바꾸는 방법([대화 DB 구조 (sms.db)](sms-db.md)의 시각 해석 절)을 그대로 적용해 본 뒤, 결과가 그 메시지의 `date` 보다 뒤이고 수집 시각보다 앞인지 확인하고 나서 씁니다. `sync_deleted_chats.timestamp` 도 같은 이유로 단위를 확인하고 씁니다.

## 함정과 한계

WAL 파일을 빼고 열면 최근 메시지가 경고 없이 빠져서[5] WAL 을 반드시 함께 수집합니다. SQLite 의 WAL 과 빈 페이지에서 지운 행을 되살리는 방법은 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)와 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

한 기기에서 복구하면 Messages in iCloud 로 다른 기기에도 반영된다는 설명과 편집을 "최대 5번" 할 수 있다는 설명도 있지만, 공식 자료로 뒷받침되지 않으니 실제 기기로 확인하고 씁니다.

취소·편집 흔적은 sms.db 밖에도 남습니다. D20 의 iOS 16 시험에서는 취소한 메시지의 날짜·시각·내용·상대가 바이옴의 AppIntent 스트림(`/private/var/mobile/Library/Biome/streams/public/AppIntent/local`)에 남을 수 있었고, 알림 기록(`/private/var/mobile/Library/DuetExpertCenter/streams/UserNotificationEvents/local/`)에도 내용이 남았지만 알림 시각이 원래 메시지 시각과 늘 맞지는 않았습니다[1]. 편집한 메시지도 같은 곳에 남았습니다[1]. KnowledgeC.db 에서는 보통의 파싱으로는 나오지 않았고 카빙으로 찾을 수 있었습니다[1]. 이 결과는 iOS 16 에서 시험한 것이고 세부 버전은 밝혀져 있지 않아서, 다른 버전에서는 실제 기기로 다시 확인합니다.

## 직접 분석해 보기

sqlite3 로 WAL 을 함께 둔 사본을 열고, 먼저 최근 삭제된 항목을 대화방과 함께 뽑아 봅니다.

```sql
SELECT r.chat_id, c.chat_identifier, r.message_id, r.delete_date,
       m.guid, m.date, m.is_from_me, m.text IS NULL AS text_is_null
FROM chat_recoverable_message_join r
LEFT JOIN chat c    ON c.ROWID = r.chat_id
LEFT JOIN message m ON m.ROWID = r.message_id
ORDER BY r.chat_id, r.message_id;
```

그다음 `text` 가 비고 `message_summary_info` 가 채워진 행을 골라 취소·편집 후보로 봅니다. `message_summary_info` 는 이진 plist 라서 [속성 목록 파일 (plist·NSKeyedArchiver)](../../../01-foundations/data-formats/plist.md)의 방법으로 풉니다.

```sql
SELECT ROWID, guid, date, is_from_me, length(message_summary_info) AS msi_len
FROM message
WHERE text IS NULL AND message_summary_info IS NOT NULL
ORDER BY date;
```

이 목록에는 `attributedBody` 에 본문이 남은 행도 섞일 수 있어, 본문을 꺼낸 뒤에도 비어 있는지 한 번 더 확인합니다.

## 교차 검증

취소·편집한 메시지의 내용은 [바이옴 (Biome)](../../app-usage/biome/index.md), [알림 기록 (Notifications)](../../app-usage/notifications.md), [KnowledgeC (knowledgeC.db)](../../app-usage/knowledgec/index.md)에서 같은 시간대를 찾아 맞춰 봅니다[1]. 검색용으로 색인에 들어간 메시지 본문은 sms.db 에서 지운 뒤에도 [스포트라이트 검색 색인](../../input-assistant/spotlight.md)에 남을 수 있습니다. 조사 흐름은 [지운 대화와 사진 찾기 (Deleted Content)](../../../04-scenarios/activity/deleted-content.md)와 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)를 따릅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 16 이후 시험 데이터로 아래를 풀어 봅니다.

1. `chat_recoverable_message_join` 의 행 가운데 `delete_date` 가 빈 행이 몇 개인지 세어 봅니다.
2. `recoverable_message_part.part_text` 에 무엇이 들어 있는지 보고, 같은 `message_id` 의 `message` 행과 비교해 봅니다.
3. `text` 가 비고 `message_summary_info` 가 채워진 행을 골라 plist 를 풀어 편집 기록이 몇 번 들어 있는지 세어 봅니다.
4. 3번에서 찾은 메시지의 시각에 알림 기록이나 바이옴에 같은 내용이 있는지 찾아봅니다.

## 참고 문헌

1. D20 Forensics, "iOS 16 - "Paul unsent a message." ... OR DID HE?!" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-paul-unsent-message-or-did-he.html
2. Apple 지원, "Recover deleted text messages on your iPhone or iPad" — https://support.apple.com/en-us/102615
3. Apple 지원, "How to unsend messages on your iPhone" — https://support.apple.com/en-us/105085
4. Magnet Forensics, "The Meaning of Messages" (2023-03-09) — https://www.magnetforensics.com/blog/the-meaning-of-messages/
5. ChatExport, ChatExportKnowledge README — https://github.com/ChatExport/ChatExportKnowledge
