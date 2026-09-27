---
title: "메신저로"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 2490
---

# 메신저로 (Messenger)

이 맥의 메신저로 자료를 첨부해 다른 사람에게 보냈는지 묻는 조사를 다룹니다. 어떤 메신저를 썼는지 먼저 좁히고, 메시지 앱이라면 `chat.db` 의 `message` 표에서 보낸 메시지(`is_from_me = 1`) 가운데 첨부가 붙은 행을 `attachment`·`handle`·`chat` 표와 이어 뽑습니다. 그다음 `~/Library/Messages/Attachments/` 아래 사본을 원본 파일과 비교하고, 원본 파일의 최근 항목과 FSEvents 기록을 보낸 시각과 함께 타임라인에 올립니다.

## 조사 질문

이 맥의 메신저로 자료를 첨부해 다른 사람에게 보냈는지 묻습니다. 이 페이지는 맥에 기본으로 들어 있는 메시지 앱 (iMessage·SMS)을 중심으로, 보낸 메시지에 붙은 첨부를 데이터베이스에서 골라내는 순서를 다룹니다. 메시지 데이터베이스 전체 구조는 [메시지 (iMessage·SMS)](../../../02-artifacts/messengers/imessage/index.md) 페이지에 있고, 경로마다 공통으로 쓰는 판단 원칙은 [자료를 밖으로 빼돌렸나](index.md) 허브에 있습니다.

## 먼저 확인할 것

먼저 어떤 메신저를 썼는지 확인합니다. [설치한 앱과 영수증](../../../02-artifacts/system-account/installed-apps-receipts.md)과 [어떤 앱을 언제 썼나](../../activity/app-usage.md)로 사용한 앱을 좁히고, 메시지 앱이 아닌 메신저는 저장 위치와 구조가 앱마다 달라서 각 페이지를 따릅니다. [카카오톡](../../../02-artifacts/messengers/kakaotalk.md), [텔레그램](../../../02-artifacts/messengers/telegram.md), [슬랙](../../../02-artifacts/messengers/slack.md), [팀즈](../../../02-artifacts/messengers/teams.md), [디스코드](../../../02-artifacts/messengers/discord.md), [위챗](../../../02-artifacts/messengers/wechat.md), [라인](../../../02-artifacts/messengers/line.md), [왓츠앱](../../../02-artifacts/messengers/whatsapp.md), [시그널](../../../02-artifacts/messengers/signal.md) 페이지가 있습니다.

메시지 앱의 데이터베이스는 `~/Library/Messages/chat.db`(SQLite)이고, 첨부 파일은 `~/Library/Messages/Attachments/` 아래에 있습니다 [1][2]. 둘 다 사용자 홈 아래에 있어서 사용자마다 따로 보고, 데이터베이스와 첨부 폴더를 함께 수집해야 첨부 기록과 실제 파일을 맞춰 볼 수 있습니다.

시각 기준도 먼저 정해 둡니다. `message` 표의 `date`·`date_read`·`date_delivered`는 맥 절대 시각(2001-01-01 기준)입니다 [2]. 값의 절댓값이 32비트 범위(0xFFFFFFFF)를 넘으면 나노초 단위이므로 10억으로 나눈 뒤 바꾸고, 이 나노초 형식은 하이 시에라 (High Sierra)에서 나타납니다 [2]. 어느 버전부터 나노초로 바뀌었는지는 알려져 있지 않아서, 분석 대상마다 값의 자릿수를 보고 단위를 정합니다([맥의 시각 값](../../../01-foundations/value-decoding/mac-time-values.md)). 맥의 시간대는 [시간대와 시계 설정](../../../02-artifacts/system-account/time-zone.md)에서 확인합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `chat.db`의 `message` 표 | 보낸 쪽인지 받은 쪽인지(`is_from_me`), 서비스, 시각 | [메시지](../../../02-artifacts/messengers/imessage/index.md) |
| 2 | `message_attachment_join`과 `attachment` 표 | 메시지에 붙은 첨부의 이름·경로·크기 | [메시지](../../../02-artifacts/messengers/imessage/index.md) |
| 3 | `handle`과 `chat` 표 | 상대 연락처와 대화 식별자 | [메시지](../../../02-artifacts/messengers/imessage/index.md), [연락처](../../../02-artifacts/cloud-apps/contacts.md) |
| 4 | `~/Library/Messages/Attachments/` | 첨부 파일 사본 | [메시지](../../../02-artifacts/messengers/imessage/index.md) |
| 5 | 원본 파일의 최근 항목과 FSEvents | 첨부하기 전에 원본 파일을 다룬 흔적 | [최근 항목](../../../02-artifacts/file-folder-usage/recent-items/index.md), [파일 시스템 이벤트](../../../02-artifacts/filesystem/fsevents/index.md) |

표 사이 연결은 아래와 같습니다 [2].

| 연결 | 이어 주는 열 |
|---|---|
| `message` ↔ `attachment` | `message_attachment_join`(message_id, attachment_id) |
| `message` ↔ `chat` | `chat_message_join`(message_id, chat_id) |
| `message` → `handle` | `message.handle_id` → `handle.ROWID` |

유출 조사에 쓰는 열은 `message`의 `is_from_me`·`service`·`date`·`text`·`attributedBody`, `attachment`의 `filename`(첨부 경로)·`transfer_name`(첨부 이름)·`total_bytes`(크기), `handle.id`(상대 전화번호·이메일), `chat.chat_identifier`(대화 식별자)입니다 [2]. `is_from_me`가 1이면 이 계정이 보낸 메시지이고 0이면 받은 메시지입니다 [2].

## 분석 흐름

1. `chat.db`를 사본으로 엽니다. SQLite를 여는 주의점은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 페이지를 따릅니다.
2. 보낸 메시지(`is_from_me = 1`) 가운데 첨부가 붙은 행을 뽑습니다.

   ```sql
   SELECT m.rowid              AS message_rowid,
          m.date,
          m.service,
          h.id                 AS contact,
          c.chat_identifier,
          a.transfer_name,
          a.filename,
          a.total_bytes
   FROM message m
   JOIN message_attachment_join maj ON maj.message_id = m.rowid
   JOIN attachment a               ON a.rowid = maj.attachment_id
   LEFT JOIN handle h              ON h.rowid = m.handle_id
   LEFT JOIN chat_message_join cmj ON cmj.message_id = m.rowid
   LEFT JOIN chat c                ON c.rowid = cmj.chat_id
   WHERE m.is_from_me = 1;
   ```

3. `date` 값을 사람이 읽는 시각(UTC)으로 바꿉니다. 값이 초 단위라면 `datetime('2001-01-01', '+' || m.date || ' seconds')`로 바꾸고, 32비트 범위를 넘는 나노초 값이라면 `datetime('2001-01-01', '+' || (m.date / 1000000000) || ' seconds')`처럼 먼저 10억으로 나눕니다.
4. `attachment.filename`이 가리키는 경로로 `~/Library/Messages/Attachments/` 아래 사본을 찾고, 조사 대상 원본 파일과 해시·내용을 비교합니다. 이 폴더 아래 하위 폴더 규칙은 공개된 분석 자료가 없어서, 경로는 `filename` 값을 그대로 따라갑니다.
5. 원본 파일을 맥 쪽 최근 항목과 FSEvents에서 찾고, 메시지를 보낸 시각 전후로 그 파일을 다룬 흔적이 있는지 [타임라인](../../../03-techniques/analysis/timeline/index.md)에 올려 봅니다.

## 흔한 오판

- **`text` 열만 보고 본문이 없다고 보는 경우.** `text`가 비어 있는(NULL) 경우가 많고, 이때 본문 문자열은 바이너리 열인 `attributedBody`에 들어 있습니다 [2]. 그래서 `text`가 비면 `attributedBody`를 함께 봅니다.
- **첨부 폴더에 있는 파일을 보낸 파일로 보는 경우.** 폴더만 보고 방향을 정하지 않고, `attachment.filename`을 따라 이어진 메시지의 `is_from_me`로 정합니다.
- **`service` 값을 짐작해 적는 경우.** 이 열로 아이메시지와 SMS를 가르지만 실제 값 문자열을 설명한 공개 자료가 없어서, 실제 데이터의 값을 그대로 옮겨 적습니다.
- **`date_delivered`·`date_read`로 상대가 파일을 받거나 열었다고 쓰는 경우.** 열 이름으로 뜻을 짐작할 수 있을 뿐이고, 값의 뜻은 테스트 기기에서 확인한 뒤에 씁니다([도구 검증](../../../03-techniques/reporting/tool-validation.md)).
- **받은 첨부의 격리 속성을 보낸 흔적으로 보는 경우.** 메시지 첨부로 받은 파일에 붙는 격리 속성은 받는 쪽 흔적이고, 설명은 [격리 속성과 다운로드 기록](../../../02-artifacts/filesystem/quarantine/index.md) 페이지에 있습니다.

## 보고서 문장 예

> 사용자 ○○의 메시지 데이터베이스(`chat.db`)에는 `is_from_me` 값이 1인 메시지 한 건에 `transfer_name`이 "○○.pdf", `total_bytes`가 ○○○인 첨부가 이어져 있고, 이 메시지의 상대 연락처(`handle.id`)는 ○○입니다. 이 기록은 이 계정에서 해당 첨부를 담은 메시지를 보낸 쪽으로 저장했다는 사실을 보여 주지만, 상대가 파일을 받아 열었는지는 이 기록만으로 알 수 없습니다.

## 함께 볼 페이지

- [메시지 (iMessage·SMS)](../../../02-artifacts/messengers/imessage/index.md) — 데이터베이스 전체 구조
- [누구와 연락을 주고받았나 (Communication)](../../activity/communication.md) — 상대를 연락 기록 전체와 맞춰 보는 방법
- [아이폰으로 (iPhone)](iphone.md) — 같은 계정의 아이폰과 메시지가 이어진 경우
- [메일로 (Email)](email.md) — 메일 첨부로 보낸 경우

## 참고 문헌

1. ForensicArtifacts, "artifacts/data/macos.yaml" — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. mac_apt, plugins/imessage.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/imessage.py
