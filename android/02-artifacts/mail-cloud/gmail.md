---
title: "지메일"
parent: "아티팩트 · 메일·클라우드"
nav_order: 1080
---

# 지메일 (Gmail)

지메일 앱(`com.google.android.gm`)은 로그인한 계정마다 `bigTopDataDB` 라는 SQLite DB 를 하나씩 만들어 메일 머리와 본문을 압축한 프로토콜 버퍼로 담아 두고 [2], 설정 파일 `Gmail.xml` 에는 현재 쓰는 계정과 로그인한 계정 주소가 남아서 [1][2] "이 폰에서 어떤 메일 계정으로 무엇을 주고받았나" 를 따질 때 먼저 찾아볼 곳입니다.

## 무엇을 기록하나 · 왜 생기나

지메일 앱은 서버의 메일을 기기에 받아 두고 보여 주는 앱이라서, 받은 메일과 보낸 메일의 사본과 라벨별 개수, 내려받은 첨부 파일이 앱 데이터 폴더에 쌓입니다 [2]. 구글 계정 말고도 IMAP 같은 다른 메일 계정을 지메일 앱에 넣을 수 있고, 이런 계정의 메일은 구글 계정 메일과 따로 `EmailProvider` DB 에 저장됩니다 [3].

필드 번호를 적은 공식 문서는 없고, 아래 필드 번호는 공개 도구 ALEAPP 가 시험 이미지에서 맞춰 정한 값입니다 [2].

## 위치와 버전별 차이

앱 데이터는 `/data/data/` 또는 `/data/user/` 아래 사용자 번호 폴더에 있고, `data_mirror` 경로로도 찾을 수 있습니다 [2]. 폴더 짜임은 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md), 이 폴더를 다른 앱이나 셸이 읽을 수 있는지는 [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md) 페이지에서 다룹니다. 경로 패턴은 아래와 같습니다.

```
*/com.google.android.gm/shared_prefs/Gmail.xml                 계정 정보 [1][2]
*/com.google.android.gm/databases/bigTopDataDB.*                계정별 메일 DB(뒤는 숫자 id) [2]
*/com.google.android.gm/databases/downloader.db*               다운로드 요청 [2]
*/com.google.android.gm/files/downloads/*/attachments/*/*.*    내려받은 첨부 [2]
*/com.google.android.gm/databases/EmailProvider.*              IMAP 등 다른 계정 [3]
*/com.google.android.gm/files/body/0/*/*.*                     IMAP 메일 본문(.txt·.html) [3]
*/com.google.android.gm/databases/*.db_att/*                   IMAP 받은 첨부 [3]
*/com.google.android.gm/cache/*.attachment                     IMAP 보낸 첨부 [3]
```

IMAP 본문 파일은 메시지 `_id` 를 이름으로 씁니다 [3]. DB 옆에는 `-wal`·`-shm`·`-journal` 파일이 함께 있을 수 있습니다 [2]. 복사할 때 이 파일들을 빠뜨리면 안 되는 이유는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에 있습니다.

한 기기에 Android 사용자가 여럿이면 사용자마다 `Gmail.xml` 과 `bigTopDataDB` 가 따로 생깁니다 [1][2]. 사용자 번호를 읽는 법은 [사용자와 프로필](../system-account/users-profiles.md) 페이지에 있습니다.

ALEAPP 시험 이미지로 확인된 범위는 아래와 같습니다 [1][2]. One UI 버전에 따라 경로나 표가 달라지는지는 실제 기기에서 확인합니다.

| 항목 | 내용 |
|---|---|
| 가장 낮은 판 | Android 10, 지메일 버전 코드 62632206 (이미지 이름 galaxys10) |
| 가장 높은 판 | Android 17, 지메일 버전 코드 65854395 (이미지 이름 hc_pixel8pro) |
| 삼성 기기 이미지 | galaxys10_a10, s20fe_a13, samsunga53_a14, samsungs20_a13 |
| 계정 DB 가 둘인 이미지 | samsunga53_a14 |
| 모듈 최종 갱신일 | 2026-08-24 [1][2][3] |

## 구조

### Gmail.xml

SharedPreferences 형식의 XML 이고, 읽는 법은 [설정 XML과 SharedPreferences](../../01-foundations/data-formats/shared-preferences.md) 페이지에서 다룹니다. `active-account` 항목에 지금 쓰는 계정 주소가 적히고 [1], 로그인한 계정 주소는 `<주소>-account-alias` 모양의 키 이름으로 남습니다 [2]. 키 이름 자체에 주소가 들어가 있어서 값보다 키 목록을 먼저 살펴봅니다.

### bigTopDataDB

파일 이름 뒤의 숫자 id 는 계정 주소를 Java `String.hashCode` 로 계산한 값과 같습니다 [2]. 구글이 문서로 밝힌 규칙은 아니고, ALEAPP 시험 이미지에서 맞춰 본 결과입니다 [2]. ALEAPP 는 이 관계로 DB 파일과 `Gmail.xml` 의 주소를 짝짓고, 짝이 맞지 않는 DB 는 계정 열을 비워 둡니다 [2].

| 표 | 열 | 담긴 것 |
|---|---|---|
| `item_messages` | `row_id`, `zipped_message_proto` 등 | 메일 한 통이 한 행 [2] |
| `item_message_attachments` | `item_messages_row_id` 등 | 첨부 이름·해시. `item_messages.row_id` 로 이어짐 [2] |
| `label_counts` | `label_server_perm_id`, `unread_count`, `total_count`, `unseen_count` | 라벨(받은편지함 등)별 개수 [2] |

첨부 표의 이름·해시 값은 열 이름이 알려져 있지 않아 열 순서로 읽습니다 [2].

`zipped_message_proto` 열은 첫 1바이트 뒤가 zlib 으로 압축한 프로토콜 버퍼이고, 풀면 번호 붙은 필드로 나뉩니다 [2]. 프로토콜 버퍼를 읽는 일반 방법은 [프로토콜 버퍼 (Protocol Buffers)](../../01-foundations/data-formats/protobuf.md) 페이지에 있습니다. 필드 번호는 아래와 같습니다 [2].

| 필드 | 뜻 |
|---|---|
| 17 | 시각(유닉스 밀리초) |
| 1.2 | 받는 주소 |
| 1.3 | 받는 사람 이름 |
| 5 | 제목 |
| 6.2.3.2 | HTML 본문 |
| 11.17 | 회신 주소 |
| 11.15 | 회신 이름 |
| 11.8 | Mailed By |
| 11.9 | Signed by |

본문이 들어 있는 필드 자리는 앱 버전마다 달라서 본문을 못 읽는 경우가 있습니다 [2].

### downloader.db

표 `download_requests` 에는 `request_time_ms`(유닉스 밀리초), `account_name`, `type`, `caller_id`, `url`, `target_file_path`, `target_file_size`, `priority` 열이 있습니다 [2]. 다만 ALEAPP 시험 이미지 8개 중 7개가 0행이었습니다 [2].

### EmailProvider (다른 메일 계정)

표 `Message`, `Account`, `Mailbox` 를 `Message.AccountKey = Account._id`, `Message.mailboxKey = Mailbox._id` 로 잇습니다 [3]. `Message` 에서는 `timeStamp`, `_id`, `snippet`, `toList`, `replyToList`, `subject`, `fromList`, `displayName`, `flagRead`, `flagAttachment` 를 읽고, 폴더 이름은 `Mailbox.displayName`, 계정 주소는 `Account.emailAddress` 에서 가져옵니다 [3]. 첨부는 `Attachment` 표의 `accountKey`, `_id`, `fileName`, `mimeType`, `cachedFile` 열에 있습니다 [3].

`HostAuth` 표에는 `login`, `password`, `address`, `port` 열이 있고 `Account.hostAuthKeyRecv`·`hostAuthKeySend` 로 이어집니다 [3]. 메일 서버 비밀번호가 들어 있을 수 있는 열이라서, 보고서와 사본을 다룰 때 따로 가려서 취급합니다.

열 이름이 AOSP 이메일 앱과 같아서 열의 뜻은 [삼성 이메일 (Samsung Email)](samsung-email.md) 페이지의 AOSP 비교 절을 참고할 수 있습니다. 다만 지메일 앱 쪽 DB 가 AOSP 와 같은 구조라는 것은 열 이름이 같다는 점에서 나온 짐작입니다.

## 증거로서 의미

**증명하는 것**

`Gmail.xml` 의 계정 주소와 계정별 `bigTopDataDB` 파일은 그 주소로 이 기기의 지메일 앱에 로그인한 적이 있다는 기록입니다 [1][2]. `item_messages` 의 한 행은 그 계정의 메일 한 통이 기기에 받아져 있었다는 뜻이고, 필드 17 의 시각과 제목·받는 주소를 읽을 수 있습니다 [2]. 첨부 폴더에 파일이 있으면 그 첨부를 기기로 내려받은 적이 있다는 정황이 됩니다.

**증명하지 못하는 것**

Mailed By·Signed by 는 저장된 머리 값을 그대로 보인 것이고 인증 결과 (Authentication-Results) 로 검증한 값이 아니라서 [2], 이 값만으로 발신자가 진짜라고 말할 수 없습니다. 메일이 DB 에 있다는 것만으로 사용자가 그 메일을 열어 읽었다고 할 수 없고, 보낸 메일이 있어도 이 기기에서 썼는지 다른 기기나 웹에서 쓰고 동기화만 되었는지는 따로 따져야 합니다. DB 에 없는 메일은 기기에 받지 않았을 수도 있어서, 계정 전체의 메일 목록으로 보면 안 됩니다.

## 시각 해석

`zipped_message_proto` 필드 17 과 `download_requests.request_time_ms` 는 유닉스 밀리초이고 [2], 유닉스 시각은 UTC 기준이라 현지 시각으로 옮길 때 기기 시간대를 따로 확인합니다. 필드 17 이 받은 시각인지 보낸 시각인지는 알려져 있지 않아 "메일 시각" 으로만 적습니다. EmailProvider 의 `timeStamp` 가 어떤 시각인지 적은 자료도 없습니다. 같은 이름 열의 AOSP 쪽 뜻은 [삼성 이메일 (Samsung Email)](samsung-email.md) 페이지에 있지만, 지메일 앱 쪽도 같은지는 실제 데이터로 확인합니다. 값을 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md), 시간대 확인은 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 페이지에 있습니다.

## 함정과 한계

첫째, 필드 번호에 공식 문서가 없어서 앱이 업데이트되면 자리가 바뀔 수 있습니다 [2]. 도구가 제목이나 본문을 비워 두었다면 필드 자리가 바뀌었을 가능성을 먼저 의심하고, 덩어리를 직접 풀어 확인합니다.

둘째, EmailProvider 쪽은 ALEAPP 시험 이미지 17개 모두 `Account`·`Message` 표가 비어 있었고, 모듈은 만든 자료로만 검증했습니다 [3]. 실제 데이터에서 결과가 나오면 도구 출력과 원본 행을 맞춰 보는 과정을 거칩니다.

셋째, 숫자 id 와 `String.hashCode` 가 맞는다는 것은 문서로 밝힌 규칙이 아니라서 [2], 맞지 않는 파일이 나오면 규칙이 바뀐 것인지 다른 계정인지 구분해 두고 보고서에 단정하지 않습니다.

넷째, 삭제한 메일이 DB 나 WAL 에 얼마나 남는지는 실제 데이터로 확인합니다. SQLite 에서 지운 행이 남을 수 있는 자리는 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) 페이지에서 다룹니다. 계정을 기기에서 빼면 앱 데이터가 어떻게 되는지도 알려져 있지 않으니, 계정을 넣고 뺀 흔적은 아래 교차 검증의 계정 기록에서 찾습니다.

## 직접 분석해 보기

### 값으로 한 번

아래는 Java `String.hashCode` 계산 방식과 프로토콜 버퍼 인코딩 규칙으로 만든 예시이고, 실제 데이터에서 나온 값이 아닙니다. 주소 `user@example.com` 을 `String.hashCode` 로 계산하면 1084137992 가 나오고, 위 규칙대로라면 이 계정의 DB 파일 이름은 `bigTopDataDB.1084137992` 가 됩니다. 해시가 음수로 나오는 주소에서 파일 이름이 어떻게 적히는지는 알려져 있지 않아 실제 데이터로 확인합니다.

압축을 푼 덩어리에서 필드 17 을 찾을 때는 필드 번호 17 과 형식 0(varint)을 합친 머리 바이트 `88 01` 을 찾습니다. 그 뒤의 varint 를 풀어 유닉스 밀리초로 읽습니다.

```
88 01                 필드 17, 형식 0 → (17 << 3) | 0 = 136 = 0x88 0x01
80 D0 EA B6 B7 33     varint → 1767225600000
1767225600000 ms      → 2026-01-01 00:00:00 UTC (한국 시각 09:00)
```

DB 사본을 SQLite 도구로 열어 라벨별 개수와 첨부 연결부터 볼 수 있습니다. 아래 질의는 위 구조 표로 만든 예시입니다.

```sql
SELECT label_server_perm_id, total_count, unread_count, unseen_count
FROM label_counts;

SELECT m.row_id, COUNT(a.item_messages_row_id) AS attachments
FROM item_messages m
LEFT JOIN item_message_attachments a ON a.item_messages_row_id = m.row_id
GROUP BY m.row_id;
```

`zipped_message_proto` 는 첫 1바이트를 떼고 zlib 으로 푼 다음 프로토콜 버퍼 도구에 넣어 위 필드 번호를 찾습니다 [2].

### 공개 도구로 한 번

ALEAPP 의 GmailActive 모듈이 `Gmail.xml` 을 [1], Gmail - App Emails·Label Details·Download Requests 모듈이 `bigTopDataDB` 와 `downloader.db` 를 [2], Gmail - IMAP Mailbox Emails·IMAP Accounts 모듈이 EmailProvider 를 [3] 읽어 표로 만들어 줍니다. 도구가 낸 메일 몇 통을 골라 위 방식으로 시각과 제목을 직접 풀어 맞춰 보는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [계정 (Accounts)](../system-account/accounts/index.md) | 기기에 등록된 계정과 계정을 넣고 뺀 기록이 `Gmail.xml` 의 주소와 맞는지 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | 메일 시각 앞뒤로 지메일 앱을 앞에 띄운 기록이 있는지 |
| [알림 기록 (Notification History)](../app-usage/notification-history.md) | 새 메일 알림이 DB 의 메일과 맞는지 |
| [설치된 앱 (packages.xml)](../app-usage/packages/index.md) | 지메일 앱의 설치·업데이트 시점과 버전 |
| [공용 저장 공간 (Shared Storage·/sdcard)](../../01-foundations/storage/shared-storage.md) | 첨부 파일을 공용 폴더로 따로 저장한 흔적 |

`dumpsys account` 출력에는 계정마다 `Account {name=..., type=...}` 줄과 "Accounts History" 표가 있고, 이 표에 계정 추가·삭제 동작이 기록됩니다. 열의 뜻은 [계정 (Accounts)](../system-account/accounts/index.md) 페이지에서 다룹니다. 메일로 누구와 연락했는지 묶어 보는 흐름은 [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md), 첨부로 자료를 내보냈는지 따지는 흐름은 [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에 있습니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 시험 이미지에 `com.google.android.gm` 앱 데이터가 들어 있으면 아래 질문을 풀어 봅니다.

1. `Gmail.xml` 의 `active-account` 는 어떤 주소이고, `-account-alias` 로 끝나는 키는 몇 개입니까?
2. `bigTopDataDB` 파일은 몇 개이고, 각 숫자 id 가 어느 주소의 `String.hashCode` 와 맞습니까?
3. `label_counts` 의 `total_count` 합과 `item_messages` 행 수가 비슷합니까? 다르다면 어떤 이유를 생각할 수 있습니까?
4. 첨부가 있는 메일 하나를 골라, 첨부 폴더에 실제 파일이 있는지 찾아봅니다.

## 참고 문헌

1. ALEAPP — scripts/artifacts/gmail.py (GmailActive 모듈) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/gmail.py
2. ALEAPP — scripts/artifacts/gmailEmails.py (Gmail - App Emails, Label Details, Download Requests 모듈) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/gmailEmails.py
3. ALEAPP — scripts/artifacts/gmailIMAPEmails.py (Gmail - IMAP Mailbox Emails, IMAP Accounts 모듈) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/gmailIMAPEmails.py
