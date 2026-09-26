---
title: "대화 DB"
parent: "메시지"
grand_parent: "아티팩트 · 메시지·메신저"
nav_order: 1350
---

# 대화 DB (chat.db)

`chat.db` 는 맥 메시지 앱이 메시지·대화방·상대 주소·첨부 목록을 표로 나눠 담는 SQLite 데이터베이스이고, 사용자 홈의 `~/Library/Messages/chat.db` 에 있습니다 [2].

## 무엇을 기록하나 · 왜 생기나

메시지 앱은 주고받은 메시지를 `message` 표에 한 행씩 쌓고, 대화방과 상대 주소, 첨부 파일은 따로 표를 두어 연결 표로 잇습니다 [2]. 한 DB에 iMessage·RCS·SMS·MMS 메시지가 섞여 들어 있고 [5], 메시지 행마다 서비스 이름 칸(`service`)이 있습니다 [1]. `service` 칸 값의 정확한 철자는 검체에서 값 목록부터 뽑아 보고 해석합니다.

이 페이지는 표 구조와 시각, 편집·보내기 취소 기록을 다룹니다. 첨부 표와 디스크의 첨부 파일은 [첨부 파일 (Attachments)](attachments.md)에서, 지운 메시지와 SQLite 빈 공간은 [지운 메시지의 흔적 (Deleted Messages)](deleted-messages.md)에서 다룹니다.

## 위치와 버전별 차이

| 파일 | 설명 |
|---|---|
| `~/Library/Messages/chat.db` | 대화 DB 본체의 기본 경로입니다 [2] |
| `~/Library/Messages/chat.db-wal` | DB가 WAL 모드일 때 같은 폴더에 생기는 파일. SQLite는 DB 이름 뒤에 `-wal` 을 붙여 이 파일을 만듭니다 [4] |
| iOS 백업 안 `3d/3d0d7e5fb2ce288813306e4d4636395e047a3d28` | iOS 백업에 들어 있는 같은 형식의 메시지 DB. 백업은 파일을 해시 이름으로 저장합니다 [2] |

chat.db가 WAL 모드로 동작하는지, `chat.db-shm` 이 함께 생기는지는 검체에서 확인합니다. WAL 모드라면 최근 변경은 체크포인트 때 비로소 DB 파일로 옮겨지는 구조라서 [4], 수집할 때는 `chat.db` 와 같은 폴더의 `-wal` 파일, 있으면 `-shm` 파일까지 함께 떠야 최근 메시지가 빠지지 않습니다. 수집 방법은 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)에 있습니다.

macOS 버전에 따라 알려진 차이는 아래 편집·보내기 취소 기능입니다. 그 밖의 표·칸 차이는 검체의 표 정의로 확인합니다.

## 구조

SQLite 파일 자체의 구조는 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다루고, 여기서는 메시지 앱이 쓰는 표와 칸만 봅니다. 표는 아래와 같습니다 [2].

| 표 | 담는 것 |
|---|---|
| `message` | 메시지. 한 건이 한 행입니다 |
| `chat` | 대화(대화방) |
| `handle` | 상대 주소. 메시지 행의 `handle_id` 가 이 표의 행 번호를 가리킵니다 [1] |
| `attachment` | 첨부 파일 ([첨부 파일](attachments.md)) |
| `chat_message_join` | 대화와 메시지를 잇는 연결 표 |
| `message_attachment_join` | 메시지와 첨부를 잇는 연결 표 |
| `chat_handle_join` | 대화와 상대를 잇는 연결 표 |
| `chat_recoverable_message_join` | 최근 삭제된 메시지(Recently Deleted) ([지운 메시지의 흔적](deleted-messages.md)) |

연결 표의 칸 이름은 조인하기 전에 사본에서 표 정의로 먼저 확인합니다.

### message 표의 주요 칸

`message` 표의 주요 칸은 아래와 같습니다 [1].

| 칸 | 뜻 |
|---|---|
| `rowid`, `guid` | 행 번호, 메시지 GUID |
| `text`, `subject` | 평문 본문, 제목 |
| `service` | 서비스 이름 |
| `handle_id` | 보낸 쪽의 `handle` 행 번호 |
| `destination_caller_id` | 메시지를 받은 주소 |
| `is_from_me` | 참이면 DB 주인이 보낸 메시지 |
| `is_read` | 읽음 표시. 받는 쪽이 읽으면 참이 됩니다 |
| `date`, `date_read`, `date_delivered`, `date_edited` | DB에 기록된 시각, 읽은 시각, 전달된 시각, 마지막으로 편집한 시각 |
| `associated_message_guid`, `associated_message_type`, `associated_message_emoji` | 반응(tapback)이 가리키는 메시지와 반응 종류 |
| `thread_originator_guid`, `thread_originator_part` | 답장 스레드의 원래 메시지 |
| `item_type`, `group_action_type`, `group_title`, `other_handle` | 대화 이름 변경 같은 시스템 메시지. `group_title` 에는 바뀐 대화 이름이 들어갑니다 |
| `share_status`, `share_direction` | 위치 공유 |
| `balloon_bundle_id` | 앱 메시지를 만든 앱의 번들 ID |
| `expressive_send_style_id` | 효과와 함께 보내기 |
| `filter_action`, `filter_sub_action` | 메시지 필터 분류 코드 |

GUID를 읽는 법은 [식별자 읽기 (UUID·UID·GUID)](../../../01-foundations/value-decoding/uuid-uid.md)에, `balloon_bundle_id` 같은 번들 ID를 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다.

### 인코딩된 칸

몇몇 칸은 값을 그대로 담지 않고 typedstream이나 plist로 인코딩해 담습니다 [2]. plist를 푸는 법은 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에 있습니다.

| 칸 | 인코딩 | 담는 것 | 표 |
|---|---|---|---|
| `attributedBody` | typedstream | 본문. `text` 가 비어 있으면 본문이 여기에 들어 있습니다 [1] | `message` |
| `message_summary_info` | plist | 메시지 요약. 편집·보내기 취소 정보가 여기에 들어갑니다 [1] | `message` |
| `payload_data` | plist | 앱 메시지 데이터 | — |
| `sticker_user_info` | plist | 스티커 정보 | — |
| `attribution_info` | plist | 첨부 출처 정보 | — |
| `properties` | plist | 대화 속성 | — |

— 는 어느 표의 칸인지 공개 자료에 나오지 않아 검체의 표 정의로 확인할 칸입니다.

## 편집·보내기 취소 (macOS 13 이후)

보낸 메시지는 2분 안에 보내기를 취소할 수 있고, 15분 안에 다섯 번까지 편집할 수 있습니다 [3]. 두 기능은 iMessage에서 macOS 13, iOS 16, iPadOS 16.1, visionOS 1 이후에만 되고, SMS·MMS·RCS 메시지에는 쓸 수 없습니다 [3]. 받는 쪽 기기의 버전에 따라 남는 모습이 다릅니다.

| 받는 쪽 | 남는 모습 |
|---|---|
| macOS 12, iOS 15.6, iPadOS 15.6 이하 | 원래 메시지가 그대로 남습니다. 편집은 "Edited to" 뒤에 새 글을 따옴표로 붙인 후속 메시지로 도착합니다 [3] |
| 그보다 새 버전 | 보낸 쪽과 받는 쪽 모두 편집한 메시지에서 "Edited" 를 눌러 이전 판을 볼 수 있습니다 [3] |
| 그룹 대화 | 편집 내용은 iMessage 사용자에게만 보입니다 [3] |

보낸 쪽과 받는 쪽 모두 이전 판을 볼 수 있으니 편집 전 내용이 양쪽 기기에 남는다고 볼 수 있고, 이 정보는 `message_summary_info` 에 들어가고 마지막 편집 시각은 `date_edited` 에 들어갑니다 [1][2]. `message_summary_info` 안에서 편집 이력이 들어가는 키, 보내기 취소한 메시지의 행이 남는지, 남는다면 본문 칸이 비는지, 취소 시각을 따로 적는 칸이 있는지는 공개된 분석 자료가 없으니, 검체에서 `message_summary_info` 를 열어 보고 무엇이 남았는지를 그대로 적습니다.

## 증거로서 의미

**증명하는 것.** `message` 표에 행이 있으면, 이 DB에 그 GUID의 메시지가 그 서비스 이름과 시각 값으로 기록되어 있다는 사실을 보여 줍니다. `is_from_me` 가 참이면 DB 주인 쪽에서 보낸 메시지이고 [1], `handle_id` 와 `destination_caller_id` 로 상대 주소와 받은 주소를 잇습니다. 반응·답장 스레드·효과·위치 공유·앱 메시지 같은 부가 정보도 칸마다 따로 남아서, 본문만 보는 것보다 대화의 흐름을 자세히 되살릴 수 있습니다.

**증명하지 못하는 것.** DB 주인 쪽에서 보냈다는 기록만으로는 이 맥 앞에 앉은 사람이 입력했다고 말할 수 없고, 같은 계정을 쓰는 다른 기기와 동기화했는지를 함께 따져야 합니다. 동기화 설정이 남는 파일과 키는 공개된 자료가 없어 검체에서 확인합니다. `is_read` 와 `date_read` 도 앱이 읽음으로 표시한 기록일 뿐, 사람이 내용을 읽고 이해했다는 뜻은 아닙니다. `handle` 표의 값만으로 상대를 단정하지 않고, 상대가 누구인지는 연락처 같은 다른 자료로 맞춰 봅니다.

보고서에는 "`chat.db` 의 `message` 표 rowid ○○ 행에 `is_from_me` 값 1, `service` 값 ○○, `date` 값 ○○(2001-01-01 기준으로 풀어 ○○)인 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

`message` 표의 시각 칸 네 개는 2001-01-01 00:00:00을 기준점으로 삼고 [1], 맥 절대 시각(Cocoa 기준점)과 기준점이 같습니다. 값을 날짜로 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

단위가 초인지 나노초인지는 버전에 따라 다를 수 있어 검체에서 판단합니다. 2020년대 시각이라면 초 단위 값은 아홉 자리쯤이고 나노초 단위 값은 열여덟 자리쯤이라서, 값의 자릿수를 보고 단위를 판단한 뒤 그 판단을 보고서에 적습니다. 공개 도구 문서에는 "local time zone" 이라는 말이 나오지만 [1], 흔히 UTC로 알려져 있습니다. 그래서 저장값이 UTC 기준인지 현지 시각 기준인지는 같은 사건을 기록한 다른 아티팩트의 UTC 시각과 맞춰 본 뒤 정합니다. `date_read` 나 `date_delivered` 가 0인 값은 "읽지 않았다", "전달되지 않았다" 로 바로 옮기지 않습니다.

## 함정과 한계

`text` 칸이 비어 있고 본문이 `attributedBody` 에만 들어 있는 행이 있어서 [1], `text` 만 뽑으면 본문이 없는 메시지처럼 보입니다. 본문이 빈 행은 `attributedBody` 가 채워져 있는지 늘 함께 봅니다.

imessage-database 문서에 나오는 `num_attachments`, `chat_id`, `num_replies`, `deleted_from`, `components`, `edited_parts` 는 도구가 다른 표를 조인하거나 계산해서 만든 값일 수 있습니다 [1]. 도구 결과에 이런 이름이 보여도 `message` 표의 칸 이름으로 보고서에 옮기지 않고, 사본의 표 정의에서 실제 칸을 확인합니다.

`-wal` 파일 없이 `chat.db` 만 수집하면 체크포인트 전의 최근 변경이 빠질 수 있습니다 [4]. 분석은 원본이 아니라 함께 뜬 사본에서 합니다.

## 직접 분석해 보기

### 헥스로 한 번

SQLite 파일은 첫 16바이트가 `SQLite format 3\000` 입니다 [4]. 아래는 명세로 만든 예시이고, 수집한 `chat.db` 의 첫 줄이 이렇게 보이면 SQLite 파일입니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

헤더의 나머지 칸, 특히 페이지 크기와 빈 페이지 목록은 [지운 메시지의 흔적](deleted-messages.md)에서 헥스로 따라갑니다.

### 공개 도구로 한 번

sqlite3 명령행 도구로 수집한 사본을 열고, 먼저 서비스별 행 수를 봅니다.

```sql
SELECT service, count(*) FROM message GROUP BY service;
```

그다음 메시지를 시각 순으로 뽑고, 본문이 `text` 에 없는 행을 따로 셉니다.

```sql
SELECT rowid, guid, service, handle_id, is_from_me,
       date, date_read, date_delivered, date_edited, text
FROM message
ORDER BY date;

SELECT rowid, guid, length(attributedBody)
FROM message
WHERE text IS NULL OR text = '';
```

같은 사본을 imessage-exporter로 내보내 [5], SQL로 센 행 수와 도구가 내보낸 메시지 수, `attributedBody` 에서 꺼낸 본문을 맞춰 봅니다. 두 결과가 다르면 어느 쪽이 무엇을 빼거나 더했는지 적고, 도구를 검증하는 법은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 교차 검증

| 함께 볼 자료 | 확인할 것 |
|---|---|
| [첨부 파일 (Attachments)](attachments.md) | 메시지에 붙은 파일과 디스크 원본 |
| [지운 메시지의 흔적 (Deleted Messages)](deleted-messages.md) | 최근 삭제 표와 빈 페이지, WAL의 옛 판 |
| [연락처 (Contacts)](../../cloud-apps/contacts.md) | 상대 주소를 사람 이름과 맞춰 보기 |
| [페이스타임과 통화 기록 (FaceTime·CallHistory)](../facetime-callhistory.md) | 같은 상대와의 통화 시각 |
| [아이폰·아이패드 연결 (iOS Devices)](../../external-devices/ios-devices/index.md) | iOS 백업 안의 같은 형식 DB |
| [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) | 메시지 시각을 다른 사건과 한 줄로 놓기 |
| [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md) | 이 DB를 쓰는 조사 흐름 |

## 실습

공개 검체(NIST CFReDS 등) 가운데 맥 사용자 폴더와 메시지 기록이 들어 있는 이미지를 골라 아래 질문을 풀어 봅니다.

1. `~/Library/Messages/` 에 `chat.db` 말고 `-wal`, `-shm` 파일이 있는가, 있다면 크기는 얼마인가?
2. `service` 칸에는 어떤 값이 몇 행씩 있는가?
3. `text` 가 비어 있고 `attributedBody` 만 채워진 행은 몇 개인가?
4. `date` 값의 자릿수로 단위를 판단하고, 가장 이른 메시지와 가장 늦은 메시지의 시각을 UTC로 적을 수 있는가?
5. `date_edited` 가 채워진 행이 있다면, 그 행의 `message_summary_info` plist에 무엇이 남아 있는가?

## 참고 문헌

1. imessage_database::tables::messages::message::Message (docs.rs) — https://docs.rs/imessage-database/latest/imessage_database/tables/messages/message/struct.Message.html
2. imessage_database table.rs 소스 (docs.rs) — https://docs.rs/imessage-database/latest/src/imessage_database/tables/table.rs.html
3. Apple 지원, "Unsend or edit messages" (Messages 사용 설명서, macOS 13 Ventura 이후) — https://support.apple.com/guide/messages/unsend-or-edit-messages-ichtd68328c6/mac
4. SQLite Database File Format (sqlite.org) — https://www.sqlite.org/fileformat2.html
5. ReagentX/imessage-exporter (GitHub) — https://github.com/ReagentX/imessage-exporter
