---
title: "왓츠앱"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1460
---

# 왓츠앱 (WhatsApp)

왓츠앱은 iOS 에서 메시지·통화·연락처를 `ChatStorage.sqlite`, `CallHistory.sqlite`, `ContactsV2.sqlite` 같은 코어 데이터 SQLite 파일에 나눠 적고 시각은 2001-01-01 UTC 기준 초로 적으며, 맥 앱도 같은 이름의 DB를 쓴다고 알려져 있습니다. 맥 경로와 스키마가 iOS 와 같은지는 실제 데이터로 확인합니다.

## 무엇을 기록하나 · 왜 생기나

이 페이지의 표·열 설명은 iOS 기준입니다. iOS 왓츠앱은 앱 그룹 컨테이너에 대화 DB(`ChatStorage.sqlite`), 연락처 DB(`ContactsV2.sqlite`), 통화 기록 DB(`CallHistory.sqlite`)와 첨부 미디어 폴더를 둡니다 [1]. 메시지 한 건마다 보낸 시각, 내가 보낸 것인지 여부, 본문, 상대 식별자, 첨부 파일 경로, 메시지 종류가 한 행에 남고, 통화 한 건마다 시각·길이·결과가 남습니다 [1].

맥 앱이 이 DB를 어디에 두는지, iOS 와 스키마가 같은지는 실제 기기에서 확인합니다. 맥에서 같은 이름의 DB를 찾으면 아래 표·열 목록을 그대로 믿지 말고, 표 목록부터 열어 iOS 쪽 설명과 맞는지 확인한 뒤에 씁니다. 왓츠앱 데스크톱이 예전에 일렉트론 (Electron) 앱이었다는 설명도 흔하지만, 실제 앱 번들로 확인합니다.

ForensicArtifacts 의 메신저 정의 파일(`instant_messaging.yaml`)에는 왓츠앱 항목이 없습니다 [2].

## 위치와 버전별 차이

iOS 에서 파일이 놓이는 경로 패턴은 아래와 같습니다 [1].

| 기록 | iOS 경로 패턴 [1] |
|---|---|
| 대화 | `*/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*` |
| 연락처 | `*/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*` |
| 통화 기록 | `*/mobile/Containers/Shared/AppGroup/*/CallHistory.sqlite*` |
| 첨부 미디어 | `*/mobile/Containers/Shared/AppGroup/*/Message/Media/*/*/*/*` |

패턴 끝의 `*` 는 `-wal`·`-shm` 같은 짝 파일까지 함께 잡으려는 것으로 보입니다 [1].

맥 쪽 경로는 두 가지 후보가 있고, 둘 다 실제 기기에서 확인해야 합니다.

| 맥 앱 | 후보 위치 | 확인 정도 |
|---|---|---|
| 새 앱(아이패드 앱을 맥으로 옮긴 카탈리스트판) | `~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite` | 실제 기기에서 확인 |
| 옛 데스크톱 앱(일렉트론판으로 알려짐) | `~/Library/Application Support/WhatsApp/` | 실제 기기에서 확인 |

한 맥에 두 앱을 차례로 썼다면 두 후보 폴더가 함께 남을 수 있으니 둘 다 찾아봅니다.

## 구조

아래 표·열은 iOS 의 `ChatStorage.sqlite`, `CallHistory.sqlite`, `ContactsV2.sqlite` 기준입니다 [1]. 맥에서는 같은 이름의 표가 있는지부터 봅니다.

| DB | 표 | 주요 열 | 담는 것 |
|---|---|---|---|
| `ChatStorage.sqlite` | `ZWAMESSAGE` | `ZMESSAGEDATE`, `ZISFROMME`, `ZTEXT`, `ZFROMJID`, `ZTOJID`, `ZMEDIALOCALPATH`, `ZMESSAGETYPE` | 메시지 한 건당 한 행. 시각, 보낸 쪽 여부, 본문, 상대 식별자, 첨부 파일 경로, 종류 [1] |
| `ChatStorage.sqlite` | `ZWAMEDIAITEM`, `ZWACHATSESSION` | (메시지와 이어 붙여 읽음) | 첨부 항목과 대화방. `ZWAMESSAGE` 와 이어 붙여 읽음 [1] |
| `CallHistory.sqlite` | `ZWACDCALLEVENT`, `ZWACDCALLEVENTPARTICIPANT` | `ZDATE`, `ZDURATION`, `ZOUTCOME` | 통화 한 건과 참여자 [1] |
| `ContactsV2.sqlite` | `ZWAADDRESSBOOKCONTACT` | `ZFULLNAME`, `ZPHONENUMBER`, `ZWHATSAPPID` | 연락처 이름·전화번호·왓츠앱 식별자 [1] |

표끼리 어떤 열로 이어지는지는 iLEAPP 의 `whatsApp.py` 분석기 질의에서 볼 수 있습니다 [1].

값의 뜻이 알려진 열은 두 가지입니다. `ZMESSAGETYPE` 이 5인 행에는 위치 좌표가 들어 있고 [1], 다른 값은 보고서에 값만 옮기고 뜻을 단정하지 않습니다. 통화 결과 `ZOUTCOME` 은 아래처럼 읽습니다 [1].

| `ZOUTCOME` 값 | 뜻 |
|---|---|
| 0 | Ended (끝난 통화) |
| 1 | Missed (받지 못한 통화) |
| 4 | Rejected (거절한 통화) |

> 그림 자리: `ZWAMESSAGE` 를 가운데 두고 `ZWACHATSESSION`·`ZWAMEDIAITEM` 이 이어지는 모양과, 별도 DB인 `CallHistory.sqlite`·`ContactsV2.sqlite` 를 상대 식별자(JID)로 맞춰 보는 흐름

## 증거로서 의미

**증명하는 것.** `ZWAMESSAGE` 한 행은 그 기기의 왓츠앱 DB에 그 시각·그 상대와 주고받은 메시지 기록이 남아 있다는 뜻이고, `ZISFROMME` 로 그 기기 쪽 계정이 보낸 것인지 받은 것인지를 가릅니다 [1]. `ZMEDIALOCALPATH` 가 있으면 첨부 파일이 어느 경로로 저장됐는지 알 수 있어서 실제 파일이 남아 있는지 찾아볼 수 있고, 통화 기록의 `ZOUTCOME` 으로 통화가 이어졌는지, 받지 못했는지, 거절했는지를 가릅니다 [1].

**증명하지 못하는 것.** 메시지 기록으로는 누가 키보드 앞에 있었는지, 받은 메시지를 사람이 읽었는지 알 수 없습니다. 맥 앱은 휴대폰 계정과 이어 쓰는 앱이라는 설명이 흔하지만, 맥 DB의 한 행만으로는 맥에서 쓴 것인지 휴대폰에서 쓴 것인지 가를 수 없습니다. 첨부 경로가 있어도 파일이 지금 디스크에 있다는 뜻은 아니고, 연락처 이름(`ZFULLNAME`)은 기기 주소록에서 온 이름일 수 있어서 상대의 실제 신원과 같다고 볼 수 없습니다. 보고서에는 "피조사자가 이 사람에게 메시지를 보냈다" 보다 "이 계정의 왓츠앱 DB에 이 상대 식별자로 보낸 쪽 표시(`ZISFROMME`)가 붙은 메시지 기록이 이 시각(UTC)에 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`ZMESSAGEDATE` 같은 시각 열은 코어 데이터 (Cocoa) 시각, 곧 맥 절대 시각이라 2001-01-01 00:00:00 UTC 기준 초입니다 [1]. 통화 기록의 `ZDATE` 도 기준이 같고, 통화가 끝난 시각은 `ZDATE` 에 `ZDURATION` 을 더해 구합니다 [1]. 유닉스 시각과 기준점이 31년 가까이 달라서, 유닉스 시각으로 잘못 읽으면 1990년대 날짜가 나옵니다. 기준끼리의 관계는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에 있고, 현지 시각으로 옮길 때는 먼저 UTC 로 바꾼 뒤 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)에서 확인한 시간대를 적용합니다.

| 열 | 기준·단위 | 적용 범위 |
|---|---|---|
| `ZWAMESSAGE.ZMESSAGEDATE` | 2001-01-01 UTC, 초 | iOS [1] |
| `ZWACDCALLEVENT.ZDATE` | 2001-01-01 UTC, 초 | iOS [1] |
| `ZWACDCALLEVENT.ZDURATION` | 통화 길이, 초. `ZDATE` 에 더하면 끝난 시각이 되고, `time(ZDURATION, 'unixepoch')` 로 시:분:초로 바꿔 볼 수 있습니다 | iOS [1] |

맥 DB에서 같은 열을 찾더라도 기준이 같은지는 실물 값의 크기로 한 번 더 확인합니다.

## 함정과 한계

- **iOS 설명을 맥에 그대로 옮기는 경우.** 이 페이지의 표·열은 iOS 기준이라서 [1], 맥 DB가 같은 스키마인지 확인하기 전에는 "iOS 와 같은 이름의 DB" 까지만 씁니다.
- **WAL 파일을 빼먹는 경우.** 위치 패턴이 짝 파일까지 잡는 것처럼 [1], `ChatStorage.sqlite` 만 복사하면 최근 메시지가 빠질 수 있습니다. WAL 동작은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.
- **DB를 하나만 보는 경우.** 메시지·통화·연락처가 서로 다른 DB에 있어서 [1], 대화 DB만 보면 통화 기록과 상대 이름을 놓칩니다.
- **두 맥 앱을 섞는 경우.** 새 앱과 옛 앱의 후보 폴더가 함께 남아 있을 수 있어서, 폴더마다 어느 앱의 기록인지 따로 적습니다.
- **수집 정의에 빠져 있는 경우.** ForensicArtifacts 메신저 정의에 왓츠앱이 없어서 [2], 정의만 믿고 수집하면 왓츠앱 폴더가 빠질 수 있습니다.
- **지우기와 조작.** 지운 메시지 행이 WAL 이나 DB의 빈 공간에 남을 수 있다는 점은 SQLite 일반론이라서, 왓츠앱 DB에서도 그런지는 시험 기기에서 메시지를 지워 보고 확인합니다. 지운 행을 찾는 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)를, 기록을 없애려 한 정황은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)를 봅니다.

## 직접 분석해 보기

원본 DB를 바로 열지 말고 `ChatStorage.sqlite` 와 짝 파일(`-wal`, `-shm`)을 같은 작업 폴더에 함께 복사한 뒤 사본을 엽니다.

### 헥스로 한 번

아래 값은 명세에 맞춰 만든 예시이고, 실제 데이터에서 나온 값이 아닙니다. SQLite 레코드에서 열 값을 꺼내는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)를 따르고, 여기서는 꺼낸 `ZMESSAGEDATE` 값을 시각으로 바꾸는 단계만 따라갑니다. 이 열이 정수로 저장되는지 실수로 저장되는지는 `typeof(ZMESSAGEDATE)` 로 확인하고, 여기서는 두 경우를 함께 적습니다.

```
정수로 적힌 경우 (4바이트 빅 엔디언, 예시)
29 b9 27 00
16진수 0x29B92700 = 10진수 700000000

실수로 적힌 경우 (8바이트 IEEE 754 배정도, 빅 엔디언, 예시)
41 c4 dc 93 80 00 00 00
= 700000000.0

2001-01-01 00:00:00 UTC + 700000000 초 = 2023-03-08 20:26:40 UTC
(유닉스 시각으로 바꾸면 700000000 + 978307200 = 1678307200)
```

같은 수를 유닉스 시각으로 읽으면 1992년이 나오니, 9자리 안팎의 초 값이 엉뚱하게 이른 날짜로 풀리면 2001 기준을 먼저 의심합니다.

### 공개 도구로 한 번

iOS 추출물이라면 공개 도구 iLEAPP 가 이 파일들을 찾아 보고서로 만들어 줍니다 [1]. 맥 이미지에서는 `sqlite3` 명령줄 도구나 DB Browser for SQLite 로 사본을 열고, 먼저 표 목록으로 iOS 와 같은 표가 있는지 확인한 뒤 아래처럼 읽습니다.

```sql
-- 같은 표가 있는지 먼저 본다
SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE 'ZWA%';

-- 메시지를 UTC 시각과 함께 시간순으로 본다 (2001 기준 초 → 유닉스 시각)
SELECT datetime(ZMESSAGEDATE + 978307200, 'unixepoch') AS msg_utc,
       ZISFROMME, ZFROMJID, ZTOJID, ZMESSAGETYPE, ZTEXT, ZMEDIALOCALPATH
FROM ZWAMESSAGE
ORDER BY ZMESSAGEDATE;
```

통화 기록은 `CallHistory.sqlite` 사본에서 같은 방식으로 `ZWACDCALLEVENT` 의 `ZDATE` 를 바꾸고 `ZOUTCOME` 을 위 표로 읽습니다. `ZDURATION` 은 초 단위라서 `time(ZDURATION, 'unixepoch')` 로 시:분:초로 바꿔 봅니다 [1].

## 교차 검증

- [연락처 (Contacts)](../cloud-apps/contacts.md) — `ContactsV2.sqlite` 의 이름·전화번호를 맥 주소록과 맞춰 봅니다.
- [페이스타임과 통화 기록 (FaceTime·CallHistory)](facetime-callhistory.md) — 같은 시간대의 다른 통화 기록과 견줘 봅니다.
- [아이폰·아이패드 연결 (iOS Devices)](../external-devices/ios-devices/index.md) — 휴대폰 쪽 기록과 맞춰 볼 때 씁니다.
- [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md), [바이옴 (Biome)](../execution/biome/index.md) — 앱을 쓴 시간대를 봅니다.
- [앱별 네트워크 사용량 (netusage)](../network/netusage.md) — 그 시간대에 앱이 통신한 양을 봅니다.
- [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md) — 시각 기준을 맞춰 다른 아티팩트와 한 시간축에 놓습니다.
- [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) — 이 기록을 쓰는 조사 흐름입니다.

## 실습

NIST CFReDS 같은 공개 시험 이미지 가운데 왓츠앱을 쓴 맥 이미지나 iOS 추출물을 골라 아래 질문을 풀어 봅니다.

1. 맥 이미지에서 이 페이지의 두 후보 폴더 가운데 어느 쪽이 있나요? 둘 다 있나요?
2. 찾은 `ChatStorage.sqlite` 에 `ZWAMESSAGE` 표가 있나요? iOS 설명의 열 가운데 없는 열이 있나요?
3. `ChatStorage.sqlite` 만 연 결과와 짝 파일을 함께 둔 사본을 연 결과에서 `ZWAMESSAGE` 행 수가 다른가요?
4. 가장 이른 메시지와 가장 늦은 메시지의 `ZMESSAGEDATE` 를 UTC 와 현지 시각으로 바꿔 보세요.
5. `ZOUTCOME` 이 1(받지 못한 통화)인 통화의 상대 식별자를 `ContactsV2.sqlite` 의 `ZWHATSAPPID` 와 맞춰 이름을 찾아보세요.
6. `ZMEDIALOCALPATH` 가 가리키는 첨부 파일이 이미지에 실제로 남아 있나요?

## 참고 문헌

1. abrignoni/iLEAPP, scripts/artifacts/whatsApp.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/whatsApp.py
2. ForensicArtifacts, instant_messaging.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/instant_messaging.yaml
