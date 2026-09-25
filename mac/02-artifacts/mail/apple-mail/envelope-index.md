---
title: "메일 색인 DB"
parent: "애플 메일"
grand_parent: "아티팩트 · 메일"
nav_order: 1300
---

# 메일 색인 DB (Envelope Index)

`Envelope Index` 는 애플 메일 저장소의 `MailData` 폴더에 있는 확장자 없는 SQLite 파일이고, 메시지마다 제목·발신자·받는 사람·메일함·날짜·상태 값을 여러 표에 나눠 담아 두지만 본문 텍스트는 담지 않습니다 [2][4].

## 무엇을 기록하나

메시지 한 건은 `messages` 표의 한 행이 되고, 제목·주소·메일함은 따로 떨어진 표에 한 번씩만 적은 뒤 번호로 가리키는 정규화 구조입니다 [4]. 이 행의 ROWID 가 곧 본문 파일 `<ROWID>.emlx` 의 이름 숫자라서, 색인에서 찾은 메시지를 [저장 구조 (emlx·V10)](storage.md)의 규칙으로 본문 파일까지 따라갈 수 있습니다 [3][4]. 본문 텍스트는 이 DB 에 없어서 내용을 보려면 `.emlx` 를 읽어야 합니다 [2].

메일 분류 점수와 발신 업체 분류 값이 이 DB 에 들어 있는 스키마도 있습니다 [1].

## 위치와 버전별 차이

```
~/Library/Mail/V<n>/MailData/Envelope Index
```

파일 이름에 공백이 있고 확장자가 없습니다 [2][4]. `V<n>` 폴더를 고르는 법과 라이브 시스템에서 읽을 때 필요한 권한은 [저장 구조](storage.md)에 있습니다.

V10 스키마에는 아래 표와 칸이 모두 있습니다 [4]. 분류 관련 표가 어느 macOS 버전부터 생겼는지는 공개 자료가 없어서, 검체에서 표 목록을 먼저 뽑아 보고 어떤 표가 있는지 적어 둡니다.

## 구조

### 기본 표

| 표 | 칸 (V10 에 반드시 있는 것) |
|---|---|
| `messages` | ROWID, message_id, subject, sender, mailbox, date_received, date_sent, read, flagged, deleted, size, conversation_id |
| `subjects` | ROWID, subject |
| `addresses` | ROWID, address |
| `mailboxes` | ROWID, url, total_count, unread_count |
| `recipients` | message, address |
| `attachments` | message, name |
| `message_global_data` | message_id, message_id_header |

칸 이름으로 보면 `messages.subject` 는 `subjects.ROWID` 를, `messages.sender` 는 `addresses.ROWID` 를, `messages.mailbox` 는 `mailboxes.ROWID` 를 가리키고, `recipients.message` 와 `attachments.message` 는 `messages.ROWID` 를 가리킵니다 [4]. 이 가운데 공개 도구 코드에 조인으로 나오는 것은 `messages` 와 `mailboxes` 를 이어 메일함 URL 을 붙이는 것뿐이고, 나머지 대응은 칸 이름에서 짐작한 것이라 검체에서 몇 건을 `.emlx` 헤더와 맞춰 확인합니다 [4].

`mailboxes.url` 은 `imap://<계정 UUID>/<경로>` 같은 메일함 URL 이고, 이 값과 ROWID 를 합치면 본문 파일 경로가 정해집니다 [3][4]. `message_global_data.message_id_header` 에는 RFC 822 `Message-ID` 헤더 값이 들어 있어서, 서버나 다른 기기에서 나온 같은 메일과 맞춰 볼 수 있습니다 [4].

### 분류 표

`message_global_data` 에는 `model_category`, `model_subcategory`, `model_analytics` 칸이 있고, `model_analytics` 는 score, senderScore, reasonCodes 가 든 JSON 입니다 [1]. 발신자·업체 분류는 아래 표에 있습니다 [1].

| 표 | 칸 |
|---|---|
| `business_addresses` | category |
| `business_categories` | category |
| `businesses` | address_comment, domain |

category 값에는 아래와 같은 해석이 있습니다 [1].

| 값 | 뜻 |
|---|---|
| 0 | primary |
| 1 | transactions |
| 2 | updates |
| 3 | promotions |

## 증거로서 의미

**증명하는 것.** 수집 시점에 색인에 이 메시지 행이 있었고, 그 행에 어떤 제목·발신자·메일함·크기·상태 값이 적혀 있었는지를 보여 줍니다 [4]. `.emlx` 파일이 없어진 뒤에도 색인 행이 남아 있으면 그런 메일이 저장소에 있었다는 흔적이 되지만, Exchange 계정은 처음부터 본문 파일이 없는 경우가 흔해서 [3] 파일이 없다는 것만으로 지워졌다고 보지는 않습니다. `mailboxes` 의 `total_count`·`unread_count` 로는 메일함별 규모를 볼 수 있습니다 [4].

**증명하지 못하는 것.** 본문은 이 DB 에 없습니다 [2]. `read`·`flagged`·`deleted` 칸 값이 0 과 1 로만 나뉘는지, 언제 바뀌는지는 공개 자료가 없고, 바뀐 시각이나 바꾼 사람도 이 칸에는 없습니다. `recipients` 표에서 받는 사람이 To·Cc·Bcc 가운데 어디에 있었는지 가르는 칸은 알려져 있지 않아서, 받는 사람 종류는 `.emlx` 헤더에서 확인합니다. 분류 값을 누가 어떤 기준으로 매기는지도 공개 자료가 없고, 이 값으로 사용자가 메일을 어떻게 다뤘는지를 말할 수는 없습니다 [1].

보고서에는 "색인 DB 의 이 행에 이 발신 주소와 받은 시각 값이 기록되어 있고, 읽음 칸 값은 1 이다" 처럼 칸 이름과 값을 그대로 적고, 칸의 뜻은 어느 도구의 해석인지 함께 밝힙니다.

## 시각 해석

`date_received` 와 `date_sent` 가 유닉스 시각인지 맥 절대 시각 (Mac Absolute Time)인지는 공개 자료가 없습니다. 검체에서 정할 때는 한 메시지의 두 칸 값을 두 기준으로 모두 풀어 보고, 같은 메시지 `.emlx` 의 `Date` 헤더와 가까운 쪽을 고릅니다. 두 기준의 차이와 변환식은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

## 함정과 한계

이 스키마는 공개 도구가 역분석한 것이고 Apple 이 문서로 밝힌 구조가 아닙니다 [2]. 칸 뜻은 도구마다 다르게 읽을 수 있어서, 보고서에 쓰는 해석은 실물에서 메일 앱 화면과 맞춰 본 것으로 한정합니다.

쓰기 앞 기록 (WAL)의 변경은 본 파일에 늦게 반영됩니다 [2]. 최근 변경이 `Envelope Index-wal` 에만 있고 본 파일에는 아직 없을 수 있어서, 수집할 때 같은 폴더에서 `Envelope Index` 로 시작하는 파일을 모두 함께 복사합니다. WAL 을 다루는 순서와 지운 행을 찾는 방법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)와 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)에 있습니다.

삭제한 메일의 행이 색인에 얼마나 오래 남는지는 공개 자료가 없습니다. `deleted` 칸이 켜진 행이 있다고 해서 사용자가 지운 시각을 알 수는 없습니다.

## 직접 분석해 보기

### 헥스로 확인하기

파일에 확장자가 없어서 먼저 헥스로 앞부분을 열어 SQLite 파일인지 확인하고, 페이지 크기와 WAL 모드 여부를 읽습니다. 머리글 필드의 위치와 뜻은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

### 공개 도구로 읽기

증거 사본을 `sqlite3` 명령 줄 도구로 읽기 전용으로 엽니다. 표 목록을 먼저 뽑고, 아래처럼 메시지와 제목·발신자·메일함을 이어 봅니다. 조인 가운데 `mailboxes` 를 뺀 나머지는 칸 이름에서 짐작한 것이라, 결과 몇 건을 `.emlx` 헤더와 맞춰 봅니다.

```sql
.tables

SELECT m.ROWID, s.subject, a.address AS sender, mb.url AS mailbox,
       m.date_received, m.date_sent, m.read, m.flagged, m.deleted, m.size
FROM messages m
LEFT JOIN subjects  s  ON s.ROWID  = m.subject
LEFT JOIN addresses a  ON a.ROWID  = m.sender
LEFT JOIN mailboxes mb ON mb.ROWID = m.mailbox
ORDER BY m.ROWID;
```

받는 사람은 `recipients` 에서 메시지 번호로 모읍니다. `recipients.address` 가 `addresses.ROWID` 를 가리키는지는 칸 이름에서 짐작한 것이라, 결과가 헤더의 받는 사람과 맞는지 꼭 봅니다.

```sql
SELECT r.message, a.address
FROM recipients r
LEFT JOIN addresses a ON a.ROWID = r.address
WHERE r.message = 159566;
```

## 교차 검증

ROWID 로 [저장 구조](storage.md)의 `.emlx` 를 찾아 제목·발신자·Message-ID 를 헤더와 맞춰 보고, `.emlx` 의 `flags` 상태 비트와 이 DB 의 `read`·`flagged`·`deleted` 칸도 서로 맞춰 봅니다. 첨부 목록은 [첨부 파일 (Attachments)](attachments.md)에서 다룹니다. 발신 주소는 [연락처 (Contacts)](../../cloud-apps/contacts.md)와 맞춰 사람을 짚고, 다른 메신저 기록과 함께 [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md) 흐름으로 묶습니다.

## 실습

애플 메일 데이터가 들어 있는 공개 검체나 직접 만든 시험 계정으로 아래 질문을 풀어 봅니다.

1. `Envelope Index` 의 표 목록에 이 페이지의 기본 표가 모두 있는가? 분류 표는 있는가?
2. 메시지 하나의 `date_received` 와 `date_sent` 를 두 시각 기준으로 풀어 보고, `.emlx` 의 `Date` 헤더와 맞는 기준을 고른다.
3. `mailboxes` 에서 `unread_count` 가 가장 큰 메일함의 URL 을 찾고, 그 URL 이 가리키는 `.mbox` 폴더를 디스크에서 찾는다.
4. `.emlx` 파일이 없는 `messages` 행이 있는가? 있다면 그 행의 메일함 URL 이 어떤 계정 종류인지와 `deleted` 칸 값은 무엇인지 확인한다.

## 참고 문헌

1. maxgribov/apple-mail-parser (Envelope Index 분류 파서 README) — https://github.com/maxgribov/apple-mail-parser
2. Inkvi/apple-mail-mcp (Envelope Index + .emlx 읽기 도구 README) — https://github.com/Inkvi/apple-mail-mcp
3. Inkvi/apple-mail-mcp — src/store/paths.ts (저장소 루트·.emlx 경로 계산 코드) — https://raw.githubusercontent.com/Inkvi/apple-mail-mcp/main/src/store/paths.ts
4. Inkvi/apple-mail-mcp — src/store/probe.ts (필수 표·칸 목록) — https://raw.githubusercontent.com/Inkvi/apple-mail-mcp/main/src/store/probe.ts
