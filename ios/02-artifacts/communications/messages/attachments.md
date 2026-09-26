---
title: "첨부 파일"
parent: "메시지"
grand_parent: "아티팩트 · 통화·메시지·연락처"
nav_order: 480
---

# 첨부 파일 (Attachments)

메시지로 주고받은 사진·영상·파일은 sms.db 밖의 첨부 폴더에 파일로 저장되고, sms.db 의 `attachment` 표가 그 파일의 경로·형식·크기·전송 방향을 기록하며 `message_attachment_join` 이 첨부를 메시지에 잇습니다.

## 무엇을 기록하나 · 왜 생기나

MMS 와 iMessage 로 오간 파일은 기기의 `/private/var/mobile/Library/SMS/Attachments` 폴더에 모입니다[3]. 파일 하나마다 `attachment` 표에 한 행이 생기고, `message_attachment_join` 의 `message_id`·`attachment_id` 가 그 행을 메시지에 잇습니다[1]. `message` 표에도 첨부가 있는 메시지를 표시하는 캐시 열 `cache_has_attachments` 가 있습니다.

메시지 본문에서는 첨부 자리에 U+FFFC(OBJECT REPLACEMENT CHARACTER) 한 글자가 들어가서, 사진만 보낸 메시지는 본문이 이 글자 하나뿐일 수 있습니다[2]. 사진은 사용자가 설정을 바꾸지 않았다면 HEIC 로 저장됩니다[2].

`message`·`handle`·`chat` 을 이어 붙이는 방법은 [대화 DB 구조 (sms.db)](sms-db.md)에 있습니다.

## 위치와 버전별 차이

`attachment.filename` 열에는 아래처럼 `~/` 로 시작하는 경로가 들어가고, 16진 두 글자 폴더가 두 단계 이어진 다음 첨부마다 GUID 폴더가 하나씩 있습니다[2].

```
~/Library/SMS/Attachments/ab/11/<첨부 GUID>/IMG_4471.HEIC
```

로컬 백업에서는 sms.db 가 HomeDomain 에 있는 것과 달리 첨부 파일은 MediaDomain 에 있습니다[2]. 백업 파일 ID 는 `SHA1("도메인-상대경로")` 로 구하고[2], 첨부는 `filename` 앞의 `~/` 를 떼고 `MediaDomain-Library/SMS/Attachments/...` 를 넣어 계산합니다[2]. 도메인을 HomeDomain 으로 잘못 넣으면 오류 없이 모든 첨부를 못 찾습니다[2]. 백업 구조 자체는 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)에서 다룹니다.

iOS 버전에 따라 첨부 폴더 구조가 달라진다는 공개 자료는 없습니다.

## 구조

`attachment` 표에는 열이 26개 있습니다.

```
ROWID, guid, created_date, start_date, filename, uti, mime_type,
transfer_state, is_outgoing, user_info, transfer_name, total_bytes,
is_sticker, sticker_user_info, attribution_info, hide_attachment,
ck_sync_state, ck_server_change_token_blob, ck_record_id, original_guid,
is_commsafety_sensitive, emoji_image_content_identifier,
emoji_image_short_description, preview_generation_state, preflight_info,
sensitivity_analysis
```

| 열 | 읽는 법 |
|---|---|
| `filename` | 첨부 파일 경로입니다. `~/` 로 시작하는 형식은 위와 같습니다[2] |
| `transfer_name` | 전송할 때의 파일 이름입니다. `filename` 과 `transfer_name` 둘 중 하나가 빌 수 있습니다[2] |
| `created_date` | iLEAPP 가 첨부 시각으로 쓰는 열입니다[1] |
| `uti`, `mime_type`, `total_bytes`, `is_outgoing` | 값 설명을 담은 공개 자료가 없습니다 |
| `is_sticker`, `sticker_user_info`, `is_commsafety_sensitive`, `sensitivity_analysis` | 값의 뜻을 밝힌 공개 자료가 없습니다 |

첨부 관련 설정 키는 아래 plist 에 있습니다. 값의 뜻을 밝힌 공개 자료는 없습니다. `DidMakeAllAttachmentsClassC` 의 "ClassC" 는 데이터 보호 등급 C 를 뜻할 가능성이 있고, 데이터 보호 등급 자체는 [데이터 보호 (Data Protection)](../../../01-foundations/storage/data-protection/index.md)에서 다룹니다.

| 파일(HomeDomain, `Library/Preferences/`) | 키 |
|---|---|
| `com.apple.MobileSMS.plist` | `SSKeepAttachments`, `DidMakeAllAttachmentsClassC`, `DidMarkGroupPhotosAsUnpurgeable` |
| `com.apple.MobileSMSPreview.plist` | `IMPreviewGenerationMaxPxWidth`, `IMPreviewGenerationMinHeight`, `IMPreviewGenerationMinWidth`, `IMPreviewGenerationScreenScale` |
| `com.apple.imagent.plist` | `AttachmentDownloadEarliestDate`, `attachmentZoneChangeToken-syncStoreVersion`, `com.apple.messages-cache-delete.purge_markers` |
| `com.apple.madrid.plist` | `AttachmentDownloadHistoryFinished`, `AttachmentFileSizeUpdateWatermark` |

`MobileSMSPreview` 키 이름으로 짐작하면 미리보기를 만드는 설정으로 보입니다. 미리보기 파일이 어디에 저장되는지는 실제 데이터로 확인합니다.

## 증거로서 의미

**증명하는 것.** `attachment` 행과 `message_attachment_join` 은 이 기기의 메시지 DB 에 그 메시지와 이어진 첨부가 이 이름·경로로 기록되어 있다는 사실을 보여 줍니다. 첨부 폴더에 파일이 남아 있으면 그 파일의 내용을 직접 확인할 수 있고, 이어진 메시지의 `is_from_me` 로 보낸 쪽인지 받은 쪽인지도 구분할 수 있습니다.

**증명하지 못하는 것.** iCloud 저장 공간 최적화 같은 이유로 파일이 지워져도 `attachment` 행은 남아서[2], 행이 있다고 파일이 기기에 있었다고 단정할 수 없습니다. 반대로 파일이 없다고 사용자가 지웠다고 볼 수도 없습니다.

## 시각 해석

iLEAPP 는 `attachment.created_date` 를 첨부 시각으로 씁니다[1]. 이 열의 기준과 단위를 밝힌 공개 자료는 없으니, sms.db 의 다른 날짜 열과 같은 방식인지 `message.date` 와 나란히 놓고 비교해 봅니다. 날짜 열을 바꾸는 방법은 [대화 DB 구조 (sms.db)](sms-db.md)의 시각 해석 절에 있습니다.

## 함정과 한계

백업에서 첨부를 찾을 때 가장 흔한 실수는 도메인을 HomeDomain 으로 넣는 것이고, 오류가 나지 않아서 "첨부가 없다" 로 잘못 결론 내리기 쉽습니다[2]. iLEAPP 는 경로의 `~` 를 `*` 로 바꿔 `*/Library/SMS/Attachments/*` 아래에서 파일을 찾고, 폴더로 된 묶음 첨부는 건너뛰고 일반 파일만 보고서에 넣습니다[1]. 그래서 도구 결과에 없는 첨부가 폴더 안에 남아 있을 수 있습니다.

Apple 은 iMessage 의 메시지 내용과 첨부를 저장하지 않고, 종단 간 암호화로 보호합니다[4]. 서버 쪽 데이터는 [클라우드 데이터 (iCloud·계정 데이터 요청)](../../../03-techniques/acquisition/cloud-data.md)에서 다룹니다.

이름에 삭제가 들어간 `sync_deleted_attachments` 표는 [지운 메시지의 흔적 (Deleted Messages)](deleted-messages.md)에서 다룹니다.

## 직접 분석해 보기

### 본문의 첨부 자리를 헥스로 보기

아래는 명세로 만든 예시이고 실제 기기에서 나온 값이 아닙니다. U+FFFC 를 UTF-8 로 적으면 세 바이트 `EF BF BC` 이고, 사진만 보낸 메시지의 `text` 열을 헥스로 보면 이 세 바이트만 보일 수 있습니다.

```
text (hex) : EF BF BC
text       : U+FFFC  (OBJECT REPLACEMENT CHARACTER)
```

sqlite3 에서는 `SELECT ROWID, hex(text) FROM message WHERE hex(text) = 'EFBFBC';` 로 이런 행을 골라 볼 수 있습니다.

### 메시지와 첨부를 잇고 백업 파일 ID 구하기

```sql
SELECT m.ROWID, m.is_from_me, a.ROWID AS att_id,
       a.filename, a.transfer_name, a.mime_type, a.total_bytes, a.created_date
FROM message m
JOIN message_attachment_join maj ON maj.message_id = m.ROWID
JOIN attachment a                ON a.ROWID = maj.attachment_id
ORDER BY m.date;
```

`filename` 을 얻으면 앞의 `~/` 를 떼고 MediaDomain 을 붙여 백업 파일 ID 를 구합니다[2]. 아래 경로는 명세의 형식을 따른 예시입니다.

```python
import hashlib
rel = "Library/SMS/Attachments/ab/11/<첨부 GUID>/IMG_4471.HEIC"
print(hashlib.sha1(("MediaDomain-" + rel).encode("utf-8")).hexdigest())
```

### 공개 도구로 한 번

iLEAPP 의 `sms.py` 는 `*/Library/SMS/sms.db*` 와 `*/Library/SMS/Attachments/*` 를 함께 읽어 메시지 보고서에 첨부를 붙입니다[1]. 위 질의문으로 센 첨부 행 수와 iLEAPP 보고서의 첨부 수를 맞춰 보면, 묶음 첨부처럼 도구가 건너뛴 항목을 가릴 수 있습니다.

## 교차 검증

기기에서 찍은 사진인지 받은 사진인지는 [사진 보관함 (Photos Library)](../../media/photos/index.md)과 [카메라 사진과 메타데이터 (DCIM·EXIF·HEIC)](../../media/dcim-exif.md)에서 같은 파일이 있는지 찾아 비교합니다. 첨부를 밖으로 보낸 정황을 따질 때는 [자료를 밖으로 보냈나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)의 흐름을 따릅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 시험 데이터로 아래를 풀어 봅니다.

1. `attachment` 행 가운데 `filename` 이 빈 행과 `transfer_name` 이 빈 행을 각각 세어 봅니다.
2. `filename` 으로 백업 파일 ID 를 구해 실제로 파일이 있는 행과 없는 행을 나눠 봅니다.
3. 본문이 U+FFFC 한 글자뿐인 메시지를 찾아 이어진 첨부의 `mime_type` 을 확인해 봅니다.

## 참고 문헌

1. iLEAPP, `scripts/artifacts/sms.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/sms.py
2. ChatExport, ChatExportKnowledge `attachments.md` — https://raw.githubusercontent.com/ChatExport/ChatExportKnowledge/main/attachments.md
3. Magnet Forensics, "The Meaning of Messages" (2023-03-09) — https://www.magnetforensics.com/blog/the-meaning-of-messages/
4. Apple Platform Security, "How iMessage sends and receives messages securely" — https://support.apple.com/guide/security/how-imessage-sends-and-receives-messages-secd9764312f/web
