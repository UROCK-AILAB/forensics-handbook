---
title: "메시지 첨부 파일"
parent: "메시지"
grand_parent: "아티팩트 · 메시지·메신저"
nav_order: 1360
---

# 첨부 파일 (Attachments)

메시지로 주고받은 파일은 `~/Library/Messages/Attachments/` 아래 하위 폴더에 저장되고, `chat.db` 의 `attachment` 표가 파일마다 디스크 경로·원래 이름·형식·크기를 적어 두어서, 표의 행과 디스크의 파일을 짝지어 읽습니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

메시지 앱은 첨부 하나마다 `attachment` 표에 한 행을 만들고, 그 행을 `message_attachment_join` 표로 메시지 행과 잇습니다 [2]. 첨부 행의 `guid` 는 본문 속 첨부 자리에 들어 있는 `__kIMFileTransferGUIDAttributeName` 값과 짝이 맞아서 [1], 대화 화면의 어느 자리에 어떤 파일이 붙었는지까지 되살릴 수 있습니다. 본문과 메시지 표의 열은 [대화 DB (chat.db)](chat-db.md)에서 다룹니다.

사용자는 대화 위쪽의 연락처·그룹 아이콘을 누르고 Photos, Links 같은 분류를 골라 그 대화에서 공유한 사진과 링크를 모아 볼 수 있고 [3], 같은 자리에서 첨부만 따로 지우거나 같은 종류의 첨부를 한꺼번에 지울 수도 있습니다 [4].

## 위치와 버전별 차이

경로는 아래와 같은 모양입니다 [1].

```
~/Library/Messages/Attachments/3d/...
~/Library/Messages/StickerCache/ab/...
```

주고받은 파일은 `Attachments` 아래에, 스티커는 `StickerCache` 아래에 있습니다 [1]. 두 글자 폴더 아래로 몇 단계의 폴더가 어떤 규칙으로 이어지는지는 공개된 설명이 없으니, 폴더 이름에서 뜻을 짐작하지 않고 `attachment` 표의 `filename` 열이 가리키는 경로를 따라갑니다.

macOS 버전에 따라 위치나 열이 달라지는지는 실제 데이터로 확인해야 합니다. Genmoji를 만들 때 쓴 문구는 `emoji_description` 열에 담깁니다 [1].

## 구조

`attachment` 표의 주요 열은 아래와 같습니다 [1].

| 열 | 뜻 |
|---|---|
| `rowid` | 행 번호 |
| `guid` | 첨부 GUID. 본문 속 `__kIMFileTransferGUIDAttributeName` 값과 짝이 맞습니다 |
| `filename` | DB에 적힌 디스크 경로. `~/Library/Messages/Attachments/...` 처럼 `~` 로 시작합니다 |
| `uti` | 형식 식별자 (Uniform Type Identifier) |
| `mime_type` | MIME 형식 |
| `transfer_name` | 전송될 때의 원래 파일 이름 |
| `total_bytes` | 메시지 앱이 기록한 크기 |
| `is_sticker` | 스티커 여부 |
| `hide_attachment` | 메시지 화면에서 숨기는 표시 |
| `emoji_description` | Genmoji를 만들 때 쓴 문구 |

첨부 출처 정보를 plist로 인코딩한 `attribution_info` 열도 있습니다 [2]. 이 열이 `attachment` 표에 속하는지, 생성 시각이나 전송 상태를 담는 열이 있는지는 분석 대상의 표 정의에서 확인합니다.

## 증거로서 의미

**증명하는 것.** `attachment` 행이 있으면, 이 DB에 그 이름·형식·크기의 첨부가 기록되어 있다는 사실을 보여 줍니다. 연결 표로 이어진 메시지 행을 따라가면 어느 대화에서 어느 쪽이 보낸 메시지에 붙었는지, 그 메시지의 시각은 언제인지를 함께 읽을 수 있습니다. `filename` 이 가리키는 자리에 파일이 있으면 첨부의 내용까지 볼 수 있고, 파일 크기를 `total_bytes` 와 맞춰 보면 기록된 파일과 같은 파일인지 추정할 수 있습니다.

**증명하지 못하는 것.** 받은 첨부를 사용자가 열어 보았는지를 보여 주는 기록은 알려진 것이 없습니다. `transfer_name` 은 전송될 때의 이름일 뿐이라서, 그 파일을 누가 만들었는지나 어디서 처음 왔는지는 파일 안의 메타데이터와 다른 자료로 따로 봅니다.

행은 있는데 디스크에 파일이 없을 때 그 이유를 표만 보고 정하지 않습니다. 사용자가 첨부만 따로 지웠을 수도 있고 [4], "Keep messages" 설정으로 기간이 지난 대화가 첨부와 함께 자동으로 지워졌을 수도 있습니다 [4]. 파일이 iCloud에만 남아 있는 경우가 있는지, Messages in iCloud를 켰을 때 오래된 첨부를 로컬에서 내리는지는 분석 대상의 설정과 함께 확인합니다. 자동 삭제 설정과 최근 삭제 폴더는 [지운 메시지의 흔적 (Deleted Messages)](deleted-messages.md)에서 다룹니다.

보고서에는 "`attachment` 표 rowid ○○ 행에 `transfer_name` ○○, `mime_type` ○○, `total_bytes` ○○인 첨부가 기록되어 있고, 이 행은 `is_from_me` 값 ○인 메시지 rowid ○○ 행과 이어져 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

첨부가 오간 시각은 연결된 메시지 행의 `date` 로 잡습니다. 이 값의 기준점과 단위를 판단하는 법은 [대화 DB (chat.db)](chat-db.md)의 시각 해석 절에 있습니다. 디스크 파일의 파일 시스템 시각은 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)에서 읽는 법을 보고, 메시지 시각과 섞지 않고 따로 적습니다.

## 함정과 한계

`filename` 이 `~` 로 시작하면 수집한 이미지 안에서 그 사용자의 홈 폴더로 바꿔 경로를 풀어야 하고, 절대 경로로 적힌 행이 없는지도 봅니다. `hide_attachment` 가 켜진 첨부는 메시지 화면에 보이지 않을 수 있어서 [1], 화면 캡처나 도구의 대화 보기만으로 첨부 수를 세면 표의 행 수와 어긋날 수 있습니다.

받은 첨부에 격리(quarantine) 확장 속성이 붙는지는 실제 데이터로 확인합니다. 속성이 붙어 있다면 [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md)의 방법으로 읽고, 없다고 해서 메시지로 받지 않았다고 말하지 않습니다.

## 직접 분석해 보기

1. `chat.db` 와 같은 폴더의 `-wal` 파일, `~/Library/Messages/Attachments/` 와 `StickerCache/` 폴더를 함께 수집하고 사본에서 작업합니다.
2. sqlite3로 사본을 열고 첨부 행을 뽑습니다.

   ```sql
   SELECT rowid, guid, filename, transfer_name, uti, mime_type,
          total_bytes, is_sticker, hide_attachment
   FROM attachment;
   ```

3. `filename` 을 이미지 안 경로로 풀어 파일이 있는지 보고, 있으면 실제 크기를 `total_bytes` 와, 파일 앞부분의 형식 서명을 `uti`·`mime_type` 과 맞춰 봅니다.
4. `.schema message_attachment_join` 으로 연결 표의 열 이름을 확인한 뒤, 첨부 행과 메시지 행을 조인해 메시지의 `date`, `is_from_me`, `service` 를 붙입니다.
5. 같은 사본을 imessage-exporter로 내보내 [5], 내보낸 대화에서 첨부가 붙은 자리와 개수가 SQL 결과와 같은지 확인합니다.

## 교차 검증

| 함께 볼 자료 | 확인할 것 |
|---|---|
| [대화 DB (chat.db)](chat-db.md) | 첨부가 붙은 메시지의 보낸 쪽과 시각 |
| [지운 메시지의 흔적 (Deleted Messages)](deleted-messages.md) | 파일이 없는 첨부 행의 이유 |
| [사진 메타데이터 (EXIF·HEIC)](../../embedded-metadata/exif-heic.md) | 첨부 사진 안의 촬영 정보 |
| [문서 메타데이터 (iWork·Office)](../../embedded-metadata/iwork-office.md) | 첨부 문서 안의 작성 정보 |
| [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md) | 받은 파일에 붙은 속성 |
| [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md) | 메시지로 파일을 내보냈는지 보는 조사 흐름 |

## 실습

공개 시험 이미지(NIST CFReDS 등) 가운데 맥 사용자 폴더와 메시지 기록이 들어 있는 이미지를 골라 아래 질문을 풀어 봅니다.

1. `attachment` 표의 행 수와 `Attachments` 폴더 안 파일 수는 같은가?
2. `filename` 이 가리키는 자리에 파일이 없는 행은 몇 개이고, 그 행들의 메시지 시각은 언제인가?
3. `total_bytes` 와 실제 파일 크기가 다른 첨부가 있는가?
4. `is_from_me` 가 참인 메시지에 붙은 첨부, 곧 이 맥의 계정 쪽에서 보낸 첨부는 어떤 형식이 몇 개인가?

## 참고 문헌

1. imessage_database::tables::attachment::Attachment (docs.rs) — https://docs.rs/imessage-database/latest/imessage_database/tables/attachment/struct.Attachment.html
2. imessage_database table.rs 소스 (docs.rs) — https://docs.rs/imessage-database/latest/src/imessage_database/tables/table.rs.html
3. Apple 지원, "View all shared images and links in Messages on Mac" — https://support.apple.com/guide/messages/delete-messages-and-conversations-ichtdc9ebc32/mac
4. Apple 지원, "Delete messages and conversations" (Messages 사용 설명서, macOS Catalina 10.15 이후) — https://support.apple.com/guide/messages/delete-messages-and-conversations-icht1035/mac
5. ReagentX/imessage-exporter (GitHub) — https://github.com/ReagentX/imessage-exporter
