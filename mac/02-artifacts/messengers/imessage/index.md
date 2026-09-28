---
title: "메시지"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1340
has_children: true
has_toc: false
---

# 메시지 (iMessage·SMS)

맥의 메시지 앱은 iMessage와 SMS 같은 여러 서비스의 대화를 사용자 폴더의 SQLite 데이터베이스 `~/Library/Messages/chat.db` 한 곳에 모으고 첨부 파일은 옆 폴더에 따로 두어서, 누구와 언제 무엇을 주고받았는지 재구성할 때 먼저 보는 자료입니다 [2][3].

## 왜 중요한가

iMessage·RCS·SMS·MMS 메시지가 한 DB에 함께 들어 있어서 [1] 맥 한 대에서 여러 경로의 대화를 한꺼번에 볼 수 있습니다. 메시지마다 보낸 쪽 표시와 시각, 반응·답장·편집 기록이 따로 남고, 첨부 파일은 DB의 첨부 행과 디스크의 파일을 짝지어 원본까지 확인할 수 있습니다.

지운 메시지도 곧바로 사라지지 않습니다. 앱은 지운 메시지를 최근 삭제 폴더(Recently Deleted)에 최대 30일 남기고 [4], 그 뒤에도 SQLite의 빈 공간과 WAL 파일, 상대 기기와 백업에 흔적이 남을 수 있습니다. 반대로 Messages in iCloud를 켜면 다른 기기에서 지운 것이 이 맥에도 반영되고, "Keep messages" 설정은 기간 지난 대화를 사용자가 손대지 않아도 지우기 때문에 [4], 메시지가 없다는 사실을 해석할 때는 이런 동작을 함께 따져야 합니다.

## 한눈에 보기

| 자료 | 위치 | macOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 대화 DB | `~/Library/Messages/chat.db` [2] | 대상 맥에서 경로 확인 | 대화방, 상대 주소, 메시지 본문, 보낸 쪽, 시각, 서비스 이름 |
| 첨부 파일 | `~/Library/Messages/Attachments/` 아래 하위 폴더 [3] | 대상 맥에서 폴더 확인 | 주고받은 파일 원본과 DB의 첨부 행 |
| 스티커 | `~/Library/Messages/StickerCache/` 아래 하위 폴더 [3] | 대상 맥에서 폴더 확인 | 스티커 이미지 |
| 최근 삭제 표 | `chat.db` 안 `chat_recoverable_message_join` [2] | 대상 `chat.db` 에 표가 있는지 확인 | 지운 뒤 30일 안에 되살릴 수 있는 메시지 [4] |
| 편집·보내기 취소 | `chat.db` 안 plist 열 `message_summary_info` [2] | macOS 13 이후, iMessage만 [5] | 편집 전 내용과 보내기 취소 정보 |

iOS 백업에도 같은 형식의 메시지 DB가 들어 있고 [2], 백업 안 파일 이름은 [대화 DB (chat.db)](chat-db.md)에 있습니다.

## 읽는 순서

1. [대화 DB (chat.db)](chat-db.md) — 표 구성과 `message` 표의 열, 인코딩된 본문, 시각 값의 기준점과 단위 판단, 편집·보내기 취소 기록을 다룹니다.
2. [첨부 파일 (Attachments)](attachments.md) — `attachment` 표의 열과 디스크 파일을 짝짓는 법, 파일이 없는 첨부 행을 해석할 때의 주의점을 다룹니다.
3. [지운 메시지의 흔적 (Deleted Messages)](deleted-messages.md) — 최근 삭제 폴더와 자동 삭제 설정, SQLite 빈 페이지와 WAL에 남는 옛 내용, 상대 기기와 백업 같은 다른 증거원을 다룹니다.

## 함께 볼 페이지

- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) — `chat.db` 의 저장 형식
- [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md) — plist로 인코딩된 열을 풀 때
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) — 메시지 시각을 풀 때
- [연락처 (Contacts)](../../cloud-apps/contacts.md) — 상대 주소를 사람 이름과 맞춰 볼 때
- [페이스타임과 통화 기록 (FaceTime·CallHistory)](../facetime-callhistory.md) — 같은 상대와의 통화
- [알림 센터 DB (Notification Center)](../notification-center.md) — 메시지 알림으로 남은 제목과 본문
- [아이폰·아이패드 연결 (iOS Devices)](../../external-devices/ios-devices/index.md) — 맥에 남은 iOS 백업
- [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md)
- [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)

## 참고 문헌

1. ReagentX/imessage-exporter (GitHub) — https://github.com/ReagentX/imessage-exporter
2. imessage_database table.rs 소스 (docs.rs) — https://docs.rs/imessage-database/latest/src/imessage_database/tables/table.rs.html
3. imessage_database::tables::attachment::Attachment (docs.rs) — https://docs.rs/imessage-database/latest/imessage_database/tables/attachment/struct.Attachment.html
4. Apple 지원, "Delete messages and conversations" (Messages 사용 설명서, macOS Catalina 10.15 이후) — https://support.apple.com/guide/messages/delete-messages-and-conversations-icht1035/mac
5. Apple 지원, "Unsend or edit messages" (Messages 사용 설명서, macOS 13 Ventura 이후) — https://support.apple.com/guide/messages/unsend-or-edit-messages-ichtd68328c6/mac
