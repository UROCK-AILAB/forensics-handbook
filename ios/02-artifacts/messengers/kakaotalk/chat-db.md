---
title: "대화 DB 구조와 암호화"
parent: "카카오톡"
grand_parent: "아티팩트 · 메신저"
nav_order: 810
---

# 대화 DB 구조와 암호화 (Chat DB)

## 한 줄 요약

카카오톡 메시지는 `Message.sqlite` 의 `Message` 표에 한 행씩 쌓이고 채팅방은 `Talk.sqlite` 의 `ZCHAT` 표에 있으며, 보낸 사람·채팅방·종류·시각은 평문이지만 본문과 첨부 정보는 열마다 따로 암호화되어 base64 문자열로 저장됩니다.

## 무엇을 기록하나 · 왜 생기나

메시지를 주고받을 때마다 `Message` 표에 행이 생기고, 행에는 어느 채팅방(`chatId`)에서 누가(`userId`) 언제(`sentAt`) 보냈는지와 함께 본문(`message`)과 첨부 정보(`attachment`)가 들어갑니다[2][3]. 채팅방 목록과 마지막 메시지, 안 읽은 수는 `Talk.sqlite` 의 `ZCHAT` 표에 따로 있습니다[2]. 파일이 어디 있는지는 [저장 위치와 파일 (Paths·Files)](paths-files.md)에서 다룹니다.

## 위치와 버전별 차이

두 DB 모두 앱 데이터 컨테이너의 `Library/PrivateDocuments/` 아래에 있습니다[2][3]. 공개 도구에는 시험한 iOS 버전과 앱 버전이 적혀 있지 않아서[2][3], 버전에 따른 표 구조 차이는 실제 데이터로 확인합니다.

## 구조

### `Message` 표 (`Message.sqlite`)

주요 열은 아래와 같습니다[2][3].

| 열 | 읽는 법 |
|---|---|
| `id` | 메시지 행 번호입니다 |
| `chatId` | 채팅방 ID 이고, `ZCHAT.ZID` 와 받은 미디어 폴더 이름에 같은 값이 쓰입니다[2] |
| `userId` | 보낸 사용자 ID 이고, `Talk.sqlite` 의 `ZUSER.ZID` 와 이어 이름을 찾습니다[2][3] |
| `type` | 메시지 종류를 나타내는 정수이고 공식 설명은 없습니다[2]. 한 공개 도구는 2 를 사진 한 장, 27 을 여러 장 사진으로 다룹니다[3] |
| `message` | 본문이고 암호문(base64)입니다[2] |
| `attachment` | 첨부 정보이고 암호문(base64)입니다[2] |
| `sentAt`, `readAt` | Mac 절대 시각(초)입니다[1][2] |
| `updateAt` | UNIX 시각(초)입니다[1][2] |
| `serverLogId`, `clientMsgId`, `prevId` | 값의 뜻을 설명한 공개 자료가 없습니다 |

보낸 사람 이름은 `Message.userId` 를 `ZUSER.ZID` 와 이어 찾고, 짝이 없으면 ID 만 남습니다[2][3]. 공개 도구 하나는 `userId` 가 내 ID 와 같으면 보낸 메시지로 봅니다[3]. 그 도구가 내 ID 를 정하는 방법과 그 한계는 [계정과 친구 목록 (Account·Friends)](account-friends.md)에 있습니다.

### `ZCHAT`·`ZCHATFOLDER` 표 (`Talk.sqlite`)

`Talk.sqlite` 는 Core Data 저장소라서 표 이름이 Z 로 시작합니다[2]. `ZCHAT` 에는 아래 열이 있습니다[2].

```
ZID, ZROOMNAME, ZTYPE, ZVIEWTYPE, ZACTIVEMEMBERCOUNT, ZUNREADCOUNT,
ZLASTMESSAGEID, ZLASTMESSAGETYPE, ZUPDATEDAT
```

`ZROOMNAME` 은 대부분 비어 있는데, 1:1 채팅에는 방 이름이 없고 앱 화면에 보이는 이름은 멤버로 만들기 때문입니다[2]. 그래서 빈 방 이름을 누락으로 보지 않습니다. 마지막 메시지 본문 열도 본문과 같은 방식으로 암호화되어 있고[2], `ZUNREADCOUNT` 는 시험 기기의 모든 행에서 0 이었습니다[2]. 사용자가 만든 채팅방 폴더는 `ZCHATFOLDER` 표에 있고, `ZNAME` 에 폴더 이름이, `ZCHATIDS` 에 채팅방 ID 목록이 들어 있습니다[2].

### 열 단위 암호화

`message` 와 `attachment` 는 저장된 상태에서 base64 로 적은 암호문이고, iLEAPP 가 시험한 두 기기에서는 비어 있지 않은 값이 모두 암호문이었습니다[2]. 열마다 따로 AES-CBC 로 암호화하고, 키는 그 행의 사용자 ID(`Message.userId`)와 앱에 들어 있는 고정 값으로 PBKDF2-HMAC-SHA1 을 거쳐 만듭니다[1][2][4]. 다른 사용자 ID 로 만든 키나 키를 만드는 조건을 조금 바꾼 키로는 값이 하나도 풀리지 않습니다[2]. 고정 값은 공개된 안드로이드판 방식과 같고 키를 만드는 방법만 다릅니다[2].

사용자 ID 마다 키가 달라서, 한 사람이 보낸 행이 풀려도 다른 사람이 보낸 행은 따로 풀어야 합니다. iLEAPP 는 풀리지 않은 값을 버리지 않고 저장된 base64 그대로 보고서에 남깁니다[2].

## 증거로서 의미

**증명하는 것.** `Message` 행은 이 기기의 카카오톡 DB 에 어느 채팅방에서 어떤 사용자 ID 로 기록된 메시지가 이 시각 값과 함께 남아 있다는 사실을 보여 줍니다. 본문이 풀리면 그 내용도 확인할 수 있고, 보낸 사람·채팅방·종류·시각은 평문이라[1][2] 본문을 풀지 못해도 누구와 언제 오갔는지의 틀은 잡을 수 있습니다.

**증명하지 못하는 것.** 행이 있다고 사용자가 그 메시지를 읽었다고 단정할 수 없고, `readAt` 이 무엇이 바뀔 때 바뀌는지는 실제 데이터로 확인해야 합니다. `type` 값의 뜻은 공식 설명이 없고 한 도구의 가정[3]만 있어서, 사진·음성 같은 메시지 종류를 숫자만으로 단정하지 않습니다. 기기에 없는 메시지가 서버나 상대 기기에는 있을 수 있어서, 행이 없다고 대화가 없었다고 볼 수도 없습니다.

## 시각 해석

한 표 안에서 시각 기준이 섞여 있습니다. `sentAt`·`readAt` 은 2001-01-01 을 기준으로 한 Mac 절대 시각(초)이고, `updateAt` 은 1970-01-01 을 기준으로 한 UNIX 시각(초)입니다[1][2]. `ZCHAT.ZUPDATEDAT` 도 Mac 절대 시각(초)입니다[2]. 두 기준은 모두 UTC 라서, 현지 시각은 바꾼 뒤에 시간대를 따로 적용합니다.

두 기준의 차이는 2001-01-01 과 1970-01-01 사이의 초 수[3]이고 계산하면 978307200 초입니다. 기준은 가장 최근 행을 두 방식으로 모두 바꿔 보고 수집 기간 안에 드는 쪽을 골라 확인할 수 있습니다[2]. 새 데이터에서도 열마다 이 방법으로 한 번 더 확인합니다. 시각 값 전반은 [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

아래는 기준을 잘못 고르면 어떻게 되는지 보여 주려고 만든 예시 값이고 실제 기기에서 나온 값이 아닙니다.

| 열 | 예시 값 | Mac 절대 시각으로 읽으면(UTC) | UNIX 시각으로 읽으면(UTC) |
|---|---|---|---|
| `sentAt` | 800000000 | 2026-05-09 06:13:20 | 1995-05-09 06:13:20 |
| `updateAt` | 1780000000 | 2057-05-28 20:26:40 | 2026-05-28 20:26:40 |

## 함정과 한계

`Message.sqlite` 는 행 내용 대부분이 `-wal` 파일에 있을 수 있습니다[2]. WAL 을 빼고 열면 메시지가 거의 없어 보일 수 있어서, 수집할 때 세 파일을 함께 가져옵니다. 지운 메시지를 SQLite 빈 공간이나 WAL 에서 찾는 방법은 카카오톡만 다룬 공개 자료가 없어서 일반적인 방법을 따르고, 그 방법은 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)와 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

`Talk.sqlite` 의 빈 방 이름과 모두 0 인 안 읽은 수는 시험 기기 기준의 관찰이라서[2], 다른 기기에서도 같다고 보지 않습니다. 도구마다 복호에 실패한 값을 처리하는 방식이 다를 수 있어서, 본문이 빈 행이 원래 비어 있던 행인지 풀리지 않은 행인지 원래 값과 맞춰 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

AES 는 16바이트 단위로 암호화해서, CBC 로 만든 암호문은 길이가 16의 배수입니다. base64 를 풀어 바이트 길이를 보면 값이 암호문인지 짐작할 수 있습니다. 아래는 설명하려고 만든 값이고 실제 기기에서 나온 값이 아닙니다.

```
message (저장된 값) : q1VvJ0x9cP8uYHkQm2fA4w3tZs7LbR1oNe5iKd9wXjU=
base64 을 푼 바이트 : AB 55 6F 27 4C 7D 70 FF 2E 60 79 10 9B 67 C0 E3
                      0D ED 66 CE CB 6D 1D 68 35 EE 62 29 DF 70 5E 35
길이               : 32 바이트 (16 의 배수)
```

평문 UTF-8 이라면 한글이 `EA`~`ED` 로 시작하는 세 바이트씩 규칙 있게 이어지지만, 암호문에는 그런 규칙이 보이지 않습니다.

### 질의로 한 번

```sql
-- Message.sqlite 에서 실행한다
SELECT id, chatId, userId, type,
       datetime(sentAt + 978307200, 'unixepoch') AS sent_utc,
       datetime(updateAt, 'unixepoch')           AS update_utc,
       length(message) AS msg_b64_len
FROM Message
ORDER BY sentAt DESC
LIMIT 20;
```

보낸 사람 이름을 붙이려면 `Talk.sqlite` 를 `ATTACH` 로 붙이고 `userId = ZUSER.ZID` 로 잇습니다.

### 공개 도구로 한 번

iLEAPP 의 카카오톡 분석기는 본문과 첨부 정보를 풀어 Messages·Chats 보고서를 만들고, 풀리지 않은 값은 base64 그대로 둡니다[1][2]. 위 질의로 센 행 수와 보고서의 행 수, 그리고 base64 가 그대로 남은 행 수를 맞춰 봅니다. 복호 방식은 논문[4]과 도구 소스[2]에서 확인할 수 있습니다.

## 교차 검증

같은 시각대에 카카오톡 알림이 왔는지는 [알림 기록 (Notifications)](../../app-usage/notifications.md)에서, 앱을 그 시각에 쓰고 있었는지는 [KnowledgeC (knowledgeC.db)](../../app-usage/knowledgec/index.md)와 [바이옴 (Biome)](../../app-usage/biome/index.md)에서 확인합니다. 다른 연락 수단과 시간순으로 합치는 방법은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)과 [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md)에 있습니다.

## 실습

공개된 iOS 시험 이미지 가운데 카카오톡이 설치된 것으로 아래를 풀어 봅니다.

1. `Message` 의 가장 최근 행 `sentAt`·`updateAt` 을 두 기준으로 모두 바꿔 보고, 수집 시각과 맞는 기준을 골라 봅니다.
2. `message` 가 비어 있지 않은 행 가운데 base64 를 풀었을 때 길이가 16의 배수가 아닌 행이 있는지 찾아봅니다.
3. `ZROOMNAME` 이 빈 채팅방마다 `Message` 에 나오는 `userId` 가 몇 개인지 세어 1:1 채팅인지 짐작해 봅니다.

## 참고 문헌

1. abrignoni/iLEAPP, Pull Request #2249 "Add KakaoTalk support for iOS" (2026-09-22 병합) — https://github.com/abrignoni/iLEAPP/pull/2249
2. abrignoni/iLEAPP, `scripts/artifacts/kakaoTalk.py` — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kakaoTalk.py
3. kim-do-hyeon/iOS-Forensic, `artifact_analyzer/messenger/kakaotalk/kakaotalk_analyzer.py` — https://github.com/kim-do-hyeon/iOS-Forensic/blob/main/artifact_analyzer/messenger/kakaotalk/kakaotalk_analyzer.py
4. 김도현·김병욱·양영욱·장홍준, 「iOS 환경에서 카카오톡 데이터 복호화 및 아티팩트 분석 연구」, 디지털콘텐츠학회논문지 26권 5호 1363-1373쪽, 2025, DOI 10.9728/dcs.2025.26.5.1363 — https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003204555
