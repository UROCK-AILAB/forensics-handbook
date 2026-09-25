---
title: "메시지·사진 지우기"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 1530
---

# 메시지·사진 지우기 (Content Deletion)

앱은 그대로 두고 메시지나 사진만 지웠는지, 언제 지웠는지를 따지는 시나리오입니다. 지운 내용을 되살리는 방법은 [지운 대화와 사진 찾기 (Deleted Content)](../deleted-content.md) 에서 다루고, 이 페이지는 지우는 행위가 어디에 어떻게 남는지를 봅니다.

## 조사 질문

사용자가 특정 대화나 사진을 지웠는지, 지웠다면 언제였는지, 그 항목이 아직 "최근 삭제된 항목" 에 남아 있는지를 묻습니다. 지운 사람이 이 기기의 사용자인지, 같은 계정의 다른 기기에서 지운 것이 동기화된 것인지도 함께 가립니다.

## 먼저 확인할 것

iOS 버전과 지운 뒤 지난 기간이 가장 먼저입니다. Apple 문서가 밝힌 조건은 아래와 같습니다.

| 항목 | 메시지 | 사진·동영상 |
|---|---|---|
| "최근 삭제된 항목" 에 머무는 기간 | 지운 지 30~40일 안의 메시지·대화만 되살릴 수 있습니다 [1] | 30일 동안 머문 뒤 영구 삭제됩니다 [2] |
| 필요한 버전 | iOS 16, iPadOS 16.1 이후이고, iOS 16 으로 올리기 전에 지운 메시지는 되살릴 수 없습니다 [1] | 문서에 버전 조건이 없습니다 |
| 영구 삭제 | 문서에 따로 적혀 있지 않습니다 | "최근 삭제된 항목" 앨범에서 지우면 되살릴 수 없습니다 [2] |
| 다른 기기 반영 | Messages in iCloud 를 켰을 때 다른 기기에 반영되는지는 이번에 연 문서에 없었습니다 | iCloud 사진을 쓰면 한 기기에서 지운 사진이 같은 Apple 계정의 다른 모든 기기에서도 지워집니다 [2] |
| 화면에서 들어가는 곳 | 대화 목록의 필터 버튼, iOS 18 에서는 대화 목록의 "편집" [1] | iOS 16, iPadOS 16.1 이후 "가려진 항목" 과 "최근 삭제된 항목" 앨범은 기본으로 Face ID 또는 Touch ID 가 있어야 열리고, 설정에서 끄면 가려진 항목 앨범도 함께 풀립니다 [2] |

수집 범위와 동기화 설정도 확인합니다. iCloud 사진을 쓰는 계정이라면 이 기기의 삭제 흔적이 다른 기기에서 지운 결과일 수 있어서, [애플 계정](../../../02-artifacts/system-account/apple-account.md) 과 연결된 기기를 먼저 살펴봅니다.

## 볼 아티팩트와 순서

아래 표·칸·키는 관찰한 백업에서 이름만 확인한 것이고, 각 칸 값의 뜻과 시각 기준은 이 핸드북에서 확인하지 못했습니다. 이름이 삭제·복구를 가리키는 것처럼 보여도, 검체에서 쓰기 전에 공개 도구의 해석과 대조하거나 시험 기기로 값이 바뀌는 모습을 확인합니다.

| 순서 | 아티팩트 | 위치(백업) | 표·칸·키 이름 | 자세히 |
|---|---|---|---|---|
| 1 | 메시지 DB 의 복구 관련 표 | HomeDomain `Library/SMS/sms.db` | `chat_recoverable_message_join`(`chat_id`, `message_id`, `delete_date`, `ck_sync_state`), `recoverable_message_part`(`chat_id`, `message_id`, `part_index`, `delete_date`, `part_text`, `ck_sync_state`), `unsynced_removed_recoverable_messages`(`chat_guid`, `message_guid`, `part_index`) | [메시지](../../../02-artifacts/communications/messages/index.md) |
| 2 | 메시지 DB 의 삭제·동기화 표 | 같은 파일 | `deleted_messages`(`guid`), `sync_deleted_messages`(`guid`, `recordID`), `sync_deleted_chats`(`guid`, `recordID`, `timestamp`), `sync_deleted_attachments`(`guid`, `recordID`), `scheduled_messages_pending_cloudkit_delete`, `chat` 표의 `is_recovered`, `is_deleting_incoming_messages` | [메시지](../../../02-artifacts/communications/messages/index.md) |
| 3 | 메시지 설정 | HomeDomain `Library/Preferences/com.apple.MobileSMS.plist` | `KeepMessageForDays`, `SSKeepMessages`, `KeepMessagesVersionID`, `DeleteVerificationCodes` | [설정 값](../../../02-artifacts/system-account/preferences.md) |
| 4 | 메시지 동기화 통계 | HomeDomain `Library/Preferences/com.apple.madrid.plist` | `Server.TotalRecords.recoverableMessageDeleteZone`, `LocalDBStats`(`deletedMessages`, `deletedChats`, `deletedAttachments`, `deletedRecoverableMessages`, `totalRecoverableMessages` 등) | [메시지](../../../02-artifacts/communications/messages/index.md) |
| 5 | 사진 DB 의 휴지통 상태 | CameraRollDomain `Media/PhotoData/Photos.sqlite` | `ZASSET` 의 `ZTRASHEDSTATE`, `ZTRASHEDREASON`, `ZHIDDEN`, `ZCLOUDDELETESTATE`, `ZVISIBILITYSTATE` | [사진 보관함](../../../02-artifacts/media/photos/index.md) |
| 6 | 사진 DB 의 휴지통 시각 | 같은 파일 | `ZTRASHEDDATE` 가 `ZINTERNALRESOURCE`, `ZTRANSIENTINTERNALRESOURCE`, `ZGENERICALBUM`, `ZSHARE` 표에 있습니다 | [사진 보관함](../../../02-artifacts/media/photos/index.md) |
| 7 | 사진 DB 의 변경 이력 | 같은 파일 | `ACHANGE`(`ZCHANGETYPE`, `ZENTITY`, `ZENTITYPK`, `ZTRANSACTIONID`, `ZCOLUMNS`), `ATRANSACTION`(`ZTIMESTAMP`, `ZAUTHOR`, `ZBUNDLEID`, `ZCONTEXTNAME`, `ZPROCESSID` 등) | [사진 보관함](../../../02-artifacts/media/photos/index.md) |
| 8 | iCloud 사진 설정 | CameraRollDomain `Media/PhotoData/CPL/cloudphotos-#.#.plist` | `configuration` 안의 `max.days.inRecentlyDeleted`(값은 읽지 않았습니다) | [사진 보관함](../../../02-artifacts/media/photos/index.md) |

관찰한 `ZASSET` 칸 목록에서는 `ZTRASHEDDATE` 가 보이지 않았지만, 칸 목록이 앞쪽만 적혀 있었을 수 있어서 검체에서 직접 확인합니다. 사진 DB 에는 이 밖에 `ZADDITIONALASSETATTRIBUTES` 의 `ZPTPTRASHEDSTATE`, `ZGENERICALBUM`·`ZMOMENT`·`ZSHARE`·`ZINTERNALRESOURCE` 의 `ZTRASHEDSTATE`, `ZDETECTEDFACE` 의 `ZISINTRASH` 칸도 있습니다.

메시지·사진 말고 다른 Apple 기본 앱에도 비슷한 이름의 칸이 있습니다. 메모 앱 `NoteStore.sqlite`(AppDomainGroup-group.com.apple.notes)의 `ZICCLOUDSYNCINGOBJECT` 표에 `ZMARKEDFORDELETION`, `ZISRECOVERINGFROMTRASH` 가 있고, 프리폼 `Boards/boards.db`(AppDomainGroup-group.com.apple.freeform)의 `boards` 표에 `tombstoned`, `tombstone_date`, `hide_from_recently_deleted` 가 있으며, 미리 알림 `Data-*.sqlite` 의 `ZREMCDREMINDER` 표에 `ZMARKEDFORDELETION` 이 있습니다. 메모 앱의 "최근 삭제된 항목" 보관 기간은 확인하지 못했고, 앱별 설명은 [메모](../../../02-artifacts/mail-cloud/notes.md) 와 [미리 알림과 캘린더](../../../02-artifacts/mail-cloud/reminders-calendar.md) 에서 다룹니다.

## 분석 흐름

1. 기기의 iOS 버전과 조사 대상 기간을 적고, 위 조건표로 "최근 삭제된 항목" 에 아직 남아 있을 수 있는 기간인지 판단합니다.
2. `sms.db` 를 열어 1번·2번 표에 행이 있는지 봅니다. DB 를 여는 법과 날짜 값은 [메시지](../../../02-artifacts/communications/messages/index.md) 를 따르고, `delete_date` 의 기준과 단위는 확인하지 못해서 값 모양을 [시각 값](../../../01-foundations/value-decoding/time-values.md) 과 맞춰 판단합니다.
3. 복구 관련 표의 `chat_id` 를 `chat` 표와 이어 어느 대화에서 지웠는지 적습니다.
4. `com.apple.MobileSMS.plist` 의 `KeepMessageForDays` 같은 값을 확인합니다. 이름으로 보아 메시지 보관 기간 설정과 관련될 수 있어서, 사용자가 지운 것인지 설정에 따라 사라진 것인지 가르는 데 참고합니다. 이 관계는 확인하지 못한 짐작이라 단정하지 않습니다.
5. `Photos.sqlite` 의 `ZASSET` 에서 `ZTRASHEDSTATE` 값 분포를 보고, 같은 사진의 자원 표에 있는 `ZTRASHEDDATE` 를 찾습니다. 값의 뜻은 공개 도구의 해석과 시험 기기 결과로 대조합니다.
6. 누가 지웠는지가 쟁점이면 `ATRANSACTION` 의 `ZTIMESTAMP`, `ZAUTHOR`, `ZBUNDLEID` 를 후보로 봅니다. 이 표가 삭제 작업의 주체와 시각을 가리키는지는 확인하지 못해서, 다른 흔적과 맞을 때만 씁니다.
7. iCloud 사진·메시지 동기화가 켜져 있었다면 같은 계정의 다른 기기에서 지웠을 가능성을 따로 적습니다.
8. 확인한 삭제 시각을 [타임라인](../../../03-techniques/analysis/timeline/index.md) 에 올리고, 지운 내용을 되찾는 일은 [지운 대화와 사진 찾기](../deleted-content.md) 와 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 로 넘깁니다.

## 흔한 오판

"최근 삭제된 항목" 에 없다고 지운 적이 없다고 보는 실수가 있습니다. 사진은 30일이 지나면 영구 삭제되고, 사용자가 "최근 삭제된 항목" 앨범에서 다시 지우면 되살릴 수 없습니다 [2]. 메시지도 30~40일이 지나면 되살릴 수 없습니다 [1].

iCloud 사진을 쓰는 기기에서 지운 흔적을 곧바로 이 기기 사용자의 행위로 적는 실수도 있습니다. 한 기기에서 지운 사진은 같은 계정의 다른 모든 기기에서도 지워져서 [2], 어느 기기에서 지웠는지는 따로 밝혀야 합니다.

iOS 16 이전에 지운 메시지를 "최근 삭제된 항목" 에서 찾으려는 실수도 있습니다. iOS 16 으로 올리기 전에 지운 메시지는 되살릴 수 없습니다 [1].

칸 이름을 뜻으로 옮겨 적는 일도 조심합니다. `ZTRASHEDSTATE` 나 `delete_date` 는 이름만 보면 뜻이 분명해 보이지만, 값의 기준과 단위를 검체에서 확인하지 않으면 보고서에 쓰지 않습니다. 도구가 내놓은 해석을 검증하는 법은 [도구 검증](../../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 보고서 문장 예

> `sms.db` 의 `chat_recoverable_message_join` 표에 (대화 식별값) 대화에 속한 메시지 (개수) 건의 행이 있고, 각 행의 `delete_date` 값은 (시각, UTC) 로 풀립니다. (검증 방법) 으로 칸의 뜻을 확인한 결과, 이 값은 해당 메시지를 지운 시각에 해당합니다. 메시지를 지운 사람과 이유는 이 기록으로 알 수 없습니다.

## 함께 볼 페이지

- [증거를 없애려 했나 (Anti-Forensics)](index.md) — 이 시나리오 묶음의 허브
- [앱 지우기 (App Removal)](app-removal.md) — 내용 대신 앱째 지운 경우
- [지운 대화와 사진 찾기 (Deleted Content)](../deleted-content.md)
- [메시지 (iMessage·SMS)](../../../02-artifacts/communications/messages/index.md)
- [사진 보관함 (Photos Library)](../../../02-artifacts/media/photos/index.md)
- [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md)

## 참고 문헌

1. Apple Support, "Recover deleted text messages on your iPhone or iPad" — https://support.apple.com/en-us/102615
2. Apple Support, "Delete photos on your iPhone or iPad" — https://support.apple.com/en-us/104967
