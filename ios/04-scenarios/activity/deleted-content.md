---
title: "지운 대화와 사진 찾기"
parent: "시나리오 · 행위 재구성"
nav_order: 1490
---

# 지운 대화와 사진 찾기 (Deleted Content)

사용자가 지운 메시지·대화·사진의 내용을 기기 기록에서 다시 찾는 시나리오입니다. 보내기 취소하거나 편집한 메시지의 원래 내용도 함께 다룹니다. 지우는 행위가 언제 어떻게 남는지, 지운 사람이 누구인지는 [증거를 없애려 했나 (Anti-Forensics)](anti-forensics/index.md) 에서 다루고, 이 페이지는 "무엇이 남아 있고 어디서 꺼내는가" 에 집중합니다.

## 조사 질문

대화 상대가 받았다고 주장하는 메시지가 기기에 없을 때 지운 것인지 처음부터 없던 것인지, 지웠다면 내용을 되찾을 수 있는지를 묻습니다. 보내기 취소한 메시지나 편집한 메시지의 원래 문구, 사용자가 지운 사진이 아직 기기에 남아 있는지도 같은 질문에 들어갑니다.

## 먼저 확인할 것

**iOS 버전과 지운 뒤 지난 기간**이 가장 먼저입니다. 메시지는 "최근 삭제된 항목" 에 머무는 동안 본 DB 안에 남아서 [2], 이 기간 안인지에 따라 찾는 방법이 크게 달라집니다.

| 항목 | 메시지 | 사진·동영상 |
|---|---|---|
| "최근 삭제된 항목" 이 있는 버전 | iOS 16, iPadOS 16.1 이후입니다 [1] | 문서에 버전 조건이 없습니다 |
| 되살릴 수 있는 기간 | 지운 지 30~40일 안의 것만 되살릴 수 있습니다 [1] | 30일 동안 남은 뒤 영구 삭제되어 되살릴 수 없습니다 [4] |
| 본 DB 에 남는 조건 | 두 번째로 지우거나 30일이 차기 전까지 본 DB 안에 남습니다 [2] | 공개 자료 없음 |
| 화면에서 여는 조건 | 해당 없음 | 아이폰·아이패드에서는 Face ID 나 Touch ID 로 열어야 합니다 [4]. 이 잠금이 생긴 버전은 문서에 없습니다 |

**수집 범위**도 확인합니다. iOS 는 SQLite 를 WAL 모드로 돌려서 백업에도 보통 `sms.db-wal` 이 함께 있고, WAL 없이 DB 를 열면 가장 최근 메시지가 빠지는데도 아무 경고가 나오지 않습니다 [3]. 수집한 자료에 `-wal` 파일이 함께 있는지 확인하고, 없다면 그 사실을 기록해 둡니다. WAL 의 동작은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

**시각 단위**를 미리 알아 둡니다. `sms.db` 의 시각은 Apple 절대 시각 (2001-01-01) 기준이고, 옛 백업은 초 단위지만 대략 iOS 11 부터는 같은 열이 나노초 단위입니다 [3]. 값이 1e12 보다 크면 나노초로 봅니다 [3]. 요즘 날짜를 나노초로 적으면 7e17 안팎이 되니 이 크기로 단위를 판별합니다. `delete_date` 열의 단위는 공개 자료에 없어서 값의 크기를 보고 같은 방식으로 판단하고, 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을 따릅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | 메시지 DB `sms.db` 의 `chat_recoverable_message_join` 표 — 백업의 HomeDomain `Library/SMS/sms.db` | 이 표가 있으면 "최근 삭제된 항목" 저장소를 뜻하고, iOS 16 이후에 있습니다 [3]. 열은 `chat_id`, `message_id`, `delete_date`, `ck_sync_state` 이고, `delete_date` 는 늘 채워지지는 않으니 열이 있는지와 값이 들어 있는지를 따로 확인합니다 [3] | [메시지](../../02-artifacts/communications/messages/index.md) |
| 2 | `message` 표의 본문 열 | 최근 삭제된 메시지는 본 DB 안에 남아서 [2] 본문 열에서 내용을 찾습니다. `message` 표의 본문 열은 `text`, `attributedBody`, `message_summary_info` 입니다 | [메시지](../../02-artifacts/communications/messages/index.md) |
| 3 | `recoverable_message_part` 표 | 열은 `chat_id`, `message_id`, `part_index`, `delete_date`, `part_text`, `ck_sync_state` 입니다. 이 표의 쓰임을 설명한 공개 자료가 없어서 `part_text` 에 본문이 남는지는 열 이름만으로 단정하지 않습니다 | [메시지](../../02-artifacts/communications/messages/index.md) |
| 4 | 보내기 취소·편집 흔적 — `message` 표의 `date_edited`, `date_retracted`, `message_summary_info` | `date_edited` 가 0 이나 NULL 이면 편집한 적이 없고, `date_retracted` 가 0 이 아니면 보낸 사람이 보내기 취소한 메시지입니다 (둘 다 iOS 16 이후) [3]. `message_summary_info` 는 편집 기록과 취소 정보를 담은 blob 입니다 [3] | [메시지](../../02-artifacts/communications/messages/index.md) |
| 5 | `sms.db-wal` | 본 DB 에 아직 반영되지 않은 최근 변경 [3] | [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) |
| 6 | 사진 DB — 백업의 CameraRollDomain `Media/PhotoData/Photos.sqlite` | `ZASSET` 표에 `ZTRASHEDSTATE`, `ZTRASHEDREASON`, `ZCLOUDDELETESTATE`, `ZHIDDEN` 열이 있습니다. 값별 뜻은 실제 데이터로 확인해야 합니다 | [사진 보관함](../../02-artifacts/media/photos/index.md) |
| 7 | 다른 Apple 앱의 삭제 관련 표 | 아래 문단 참고 | 각 앱 페이지 |

`date_edited`, `date_retracted` 열이 있는지는 실제 데이터에서 직접 확인합니다. `sms.db` 에는 이 밖에 `deleted_messages`(`ROWID`, `guid`), `sync_deleted_messages`, `sync_deleted_chats`, `sync_deleted_attachments`, `unsynced_removed_recoverable_messages` 표와 `chat` 표의 `is_recovered`, `is_deleting_incoming_messages` 열도 있습니다. `deleted_messages` 와 `sync_deleted_*` 표의 쓰임을 설명한 공개 자료가 없고, 열도 `guid` 같은 식별값뿐이라서 이 페이지에서는 내용을 찾는 곳으로 다루지 않습니다. 지운 흔적으로 보는 분석은 [증거를 없애려 했나](anti-forensics/index.md) 에서 다룹니다.

메시지·사진 말고도 삭제와 관련된 이름의 표·열이 있습니다. 음성 사서함 HomeDomain `Library/Voicemail/voicemail.db` 에는 `voicemail` 표와 같은 열로 된 `deleted` 표가 있고 그 안에 `trashed_date` 열이 있습니다. 캘린더 HomeDomain `Library/Calendar/Calendar.sqlitedb` 의 `ResourceChange` 표에는 `delete_count`, `deleted_summary`, `deleted_start_date` 열이 있습니다. 이 열들의 동작을 설명한 공개 자료는 없고, 앱별 설명은 [음성 사서함과 통화 녹음](../../02-artifacts/communications/voicemail-recording.md), [미리 알림과 캘린더](../../02-artifacts/mail-cloud/reminders-calendar.md), [메모](../../02-artifacts/mail-cloud/notes.md) 에서 다룹니다.

## 분석 흐름

1. 기기의 iOS 버전과 조사 대상 기간을 적고, 위 조건표로 "최근 삭제된 항목" 기간 안인지 판단합니다.
2. `sms.db` 와 `sms.db-wal` 을 함께 복사해 같은 폴더에 두고, 그 사본으로 엽니다. 여는 법과 WAL 을 다루는 주의점은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 를 따릅니다.
3. `chat_recoverable_message_join` 에 행이 있는지 봅니다. 행이 있으면 `chat_id` 로 어느 대화인지, `message_id` 로 어느 메시지인지를 찾아 `message` 표의 본문 열을 확인합니다. `message_id` 는 이름으로 보면 `message` 표의 `ROWID` 와 이어지는 것 같지만, 공개 도구의 해석이나 시험 기기 결과와 대조합니다.

   ```sql
   SELECT j.chat_id, j.message_id, j.delete_date, m.text, m.attributedBody
   FROM chat_recoverable_message_join AS j
   LEFT JOIN message AS m ON m.ROWID = j.message_id;
   ```

4. `text` 가 비어 있으면 `attributedBody` 를 봅니다. blob 을 푸는 방법은 [메시지](../../02-artifacts/communications/messages/index.md) 와 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 을 따릅니다.
5. `recoverable_message_part` 의 `part_text` 에 값이 있는지 확인합니다. 값이 있어도 그것이 지운 메시지의 본문이라고 곧바로 쓰지 않고, 같은 `message_id` 의 다른 기록과 맞는지 먼저 봅니다.
6. 보내기 취소·편집 메시지를 찾습니다. 두 경우 모두 `message` 표의 `text` 열이 비워지고 [2], 편집한 메시지는 편집할 때마다 시각이 붙은 판 기록을 남기며 그 내용은 `attributedBody` 나 `message_summary_info` 에 있습니다 [2]. `date_edited`·`date_retracted` 로 대상 행을 고른 뒤 이 두 열을 풉니다 [3].
7. 사진은 `Photos.sqlite` 의 `ZASSET` 에서 `ZTRASHEDSTATE` 값 분포를 보고, 값이 다른 행의 파일이 백업에 남아 있는지 [사진 보관함](../../02-artifacts/media/photos/index.md) 의 경로 규칙으로 찾습니다. 값의 뜻은 공개 문서에 설명돼 있지 않으니 시험 기기에서 사진을 지웠다 되살리며 값이 바뀌는 모습을 먼저 확인합니다.
8. "최근 삭제된 항목" 기간이 지난 내용은 SQLite 의 빈 페이지나 WAL 에 조각이 남는지를 살펴야 하는데, 방법과 한계는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다. 그런 조각을 되살릴 수 있는지는 기기마다 확인합니다.
9. 찾은 내용과 시각을 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올리고, 대화 상대 쪽 기록과 맞춰 봅니다. 대화 흐름 분석은 [누구와 연락을 주고받았나](communication.md) 를 봅니다.

## 흔한 오판

WAL 을 빼고 DB 를 열어 "메시지가 없다" 고 판단하는 실수가 가장 흔합니다. WAL 없이 열면 가장 최근 메시지가 빠지는데도 경고가 없어서 [3], 수집 단계에서 `-wal` 파일을 함께 챙겼는지부터 확인합니다.

보내기 취소한 메시지는 내용이 남지 않는다고 단정하는 실수도 있습니다. 보내기 취소하면 `text` 열이 비워지는 것은 맞지만 [2], `message_summary_info` 에 취소 정보가 들어 있어서 [3] 이 열까지 풀어 본 뒤에 판단합니다. 취소한 메시지의 원래 본문이 어느 열에 남는지는 실제 데이터로 확인해야 합니다.

`delete_date` 가 비어 있으니 지운 적이 없다고 보는 실수도 있습니다. 이 열은 늘 채워지지는 않아서 [3] 빈 값만으로는 지우지 않았다고 말할 수 없습니다.

시각 단위를 섞는 실수도 있습니다. 같은 열이 버전에 따라 초와 나노초로 달라서 [3], 한 가지 단위로 모든 행을 풀면 날짜가 엉뚱하게 나옵니다.

열 이름을 뜻으로 옮겨 적는 일도 조심합니다. `part_text`, `ZTRASHEDSTATE`, `trashed_date` 는 이름만 보면 뜻이 분명해 보이지만, 값을 확인하지 않은 채 보고서에 쓰면 틀릴 수 있습니다. 도구가 내놓은 해석은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 으로 확인합니다.

## 보고서 문장 예

> `sms.db`(WAL 포함) 의 `chat_recoverable_message_join` 표에 (대화 식별값) 대화의 메시지 (개수) 건이 있고, 이 가운데 (개수) 건은 `message` 표에 본문이 남아 있습니다. 이 기록은 해당 메시지가 "최근 삭제된 항목" 저장소에 들어 있었다는 것을 보여 주며, 누가 왜 지웠는지는 보여 주지 않습니다.

> `message` 표의 (행 식별값) 행은 `date_edited` 값이 0 이 아니고, `message_summary_info` 를 푼 결과 (시각, UTC) 에 편집하기 전 문구 "(문구)" 가 있습니다.

## 함께 볼 페이지

- [증거를 없애려 했나 (Anti-Forensics)](anti-forensics/index.md) — 지우는 행위의 흔적
- [메시지 (iMessage·SMS)](../../02-artifacts/communications/messages/index.md)
- [사진 보관함 (Photos Library)](../../02-artifacts/media/photos/index.md)
- [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)
- [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)
- [시각 값 (Mac 절대 시각·Unix·기타)](../../01-foundations/value-decoding/time-values.md)

## 참고 문헌

1. Apple 지원, "Recover deleted text messages on your iPhone or iPad" — https://support.apple.com/en-us/102615
2. D20 Forensics, "iOS 16 - "Paul unsent a message." ... OR DID HE?!" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-paul-unsent-message-or-did-he.html
3. ChatExport/ChatExportKnowledge README (공개 GitHub 메모, sms.db) — https://github.com/ChatExport/ChatExportKnowledge
4. Apple 지원, "How to recover deleted photos on your iPhone, iPad, Mac, or Apple Vision Pro" — https://support.apple.com/en-us/124460
