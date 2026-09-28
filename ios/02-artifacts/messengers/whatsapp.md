---
title: "왓츠앱"
parent: "아티팩트 · 메신저"
nav_order: 850
---

# 왓츠앱 (WhatsApp)

왓츠앱 iOS 앱은 앱 그룹 공유 폴더에 대화(`ChatStorage.sqlite`)·연락처(`ContactsV2.sqlite`)·통화 기록(`CallHistory.sqlite`) DB 를 따로 두고, 세 DB 모두 표 이름이 `Z` 로 시작하고 시각은 Mac 절대 시각으로 읽습니다.

## 무엇을 기록하나 · 왜 생기나

왓츠앱은 대화 내용과 첨부, 주소록과 맞춘 연락처, 음성·영상 통화 기록을 기기에 저장해 두고 화면에 보여 줍니다. 대화 DB 에는 메시지 본문·보낸 쪽·상대·시각·첨부 경로·위치 메시지 좌표가 남고, 연락처 DB 에는 주소록 이름과 왓츠앱 ID·소개글이, 통화 기록 DB 에는 통화 시각·길이·결과·주고받은 바이트 수·참가자가 남습니다 [1].

## 위치와 버전별 차이

아래 파일은 모두 앱 그룹 공유 폴더 아래에 있고, 전체 파일 시스템 추출에서 찾을 수 있습니다 [1]. 앱 그룹 개념은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 을 봅니다.

| 파일 | 내용 |
|---|---|
| `ChatStorage.sqlite` | 대화와 첨부 정보 [1] |
| `ContactsV2.sqlite` | 연락처 [1] |
| `CallHistory.sqlite` | 왓츠앱 통화 기록 [1] |
| `Message/Media/*/*/*/*` | 첨부 미디어 [1] |

`CallHistory.sqlite` 는 Apple 기본 통화 기록 DB 와 파일 이름이 같으니, 경로로 어느 쪽인지 구분합니다 [1]. Apple 쪽은 [통화 기록](../communications/call-history.md) 에서 다룹니다.

번들 ID 는 `net.whatsapp.WhatsApp` 입니다 [1]. 앱 그룹 ID 와 로컬 백업의 도메인 이름은 실제 데이터로 확인해야 합니다. 로컬 백업에서는 앱 그룹 공유 폴더가 `AppDomainGroup-` 으로 시작하는 도메인으로 따로 나뉘므로, 왓츠앱 파일이 어느 도메인에 들어갔는지는 백업의 도메인 목록에서 찾습니다([로컬 백업](../../01-foundations/backups/local-backup/index.md)).

iLEAPP 의 시험 표본(iOS 12.4 부터 iOS 18.7.8·왓츠앱 26.14.76 까지)에서는 통화 기록 DB 의 열과 표가 표본마다 다릅니다 [1].

| 표본 | 차이 |
|---|---|
| iOS 14.3(왓츠앱 2.21.20) | `ZWACDCALLEVENT.ZGROUPCALLCREATORUSERJIDSTRING` 열이 없고 `ZWAUPCOMINGCALLEVENT` 표도 없다 [1] |
| iOS 14.3, iOS 17.1 | `ZCALLIDSTRING` 열이 없다 [1] |

이 차이는 표본에서 본 것이라서, 어느 앱 버전부터 열이 생겼는지까지는 알 수 없습니다. 분석할 DB 에서 열이 있는지 먼저 확인하고 질의를 짭니다.

## 구조

**대화 DB(`ChatStorage.sqlite`).** 주요 표와 열은 다음과 같습니다 [1].

| 표 | 열 |
|---|---|
| `ZWAMESSAGE` | `ZMESSAGEDATE`, `ZISFROMME`, `ZPARTNERNAME`, `ZFROMJID`, `ZTOJID`, `ZMEDIAITEM`, `ZTEXT`, `ZSTARRED`, `ZMESSAGETYPE`, `ZCHATSESSION` |
| `ZWAMEDIAITEM` | `ZMESSAGE`, `ZLONGITUDE`, `ZLATITUDE`, `ZMEDIALOCALPATH`, `ZXMPPTHUMBPATH`, `ZMETADATA` |
| `ZWACHATSESSION` | `Z_PK`, `ZCONTACTJID` |

`ZISFROMME` 가 1 이면 이 기기의 계정이 보낸 메시지입니다 [1]. 위도·경도는 `ZMESSAGETYPE` 이 5 인 위치 메시지 행에서만 쓰고, 다른 `ZMESSAGETYPE` 값의 뜻은 정해져 있지 않으므로 숫자만으로 메시지 종류를 단정하지 않습니다 [1]. `ZMEDIAITEM`·`ZCHATSESSION` 은 메시지를 첨부 행과 대화 행에 잇고, `ZMEDIALOCALPATH` 는 `Message/Media/` 아래 실제 파일을 가리킵니다 [1].

`ZMETADATA` 는 프로토콜 버퍼 (Protocol Buffers) 이진 값입니다 [1]. 필드 17 은 전달 횟수, 필드 21 은 전달한 사람 ID 라는 해석이 있지만 공식 근거는 없습니다 [1]. 읽는 법은 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 에 있습니다.

**연락처 DB(`ContactsV2.sqlite`).** `ZWAADDRESSBOOKCONTACT` 표에 `ZFULLNAME`, `ZABOUTTEXT`, `ZABOUTTIMESTAMP`, `ZPHONENUMBER`, `ZPHONENUMBERLABEL`, `ZWHATSAPPID`, `ZIDENTIFIER` 열이 있습니다 [1].

**통화 기록 DB(`CallHistory.sqlite`).** 표 세 개를 이어서 읽습니다 [1].

| 표 | 열 |
|---|---|
| `ZWACDCALLEVENT` | `ZDATE`, `ZDURATION`, `ZOUTCOME`, `ZGROUPCALLCREATORUSERJIDSTRING`, `ZBYTESSENT`, `ZBYTESRECEIVED`, `ZCALLIDSTRING`, `ZGROUPJIDSTRING`, `Z1CALLEVENTS` |
| `ZWACDCALLEVENTPARTICIPANT` | `ZJIDSTRING`, `Z1PARTICIPANTS` |
| `ZWAAGGREGATECALLEVENT` | `ZINCOMING`, `ZVIDEO`, `ZMISSED`, `ZMISSEDREASON` |

도구는 `ZOUTCOME` 0·1·4 를 종료·부재중·거절로 표시하지만, 이 뜻도 공식 근거는 없습니다 [1]. 같은 파일에 `ZWAJOINABLECALLEVENT`·`ZWAUPCOMINGCALLEVENT` 표도 있지만 시험 표본에서는 모두 비어 있었습니다 [1].

## 증거로서 의미

**증명하는 것.** `ZWAMESSAGE` 행은 이 기기의 왓츠앱 데이터에 그 시각의 메시지가 남아 있다는 기록이고, `ZISFROMME` 로 보낸 것과 받은 것을 나눕니다 [1]. 통화 기록 DB 의 행은 통화 시각·길이와 함께 주고받은 바이트 수를 알려 주므로, "이 시각에 이 상대와 몇 초 길이의 통화 기록이 있고 이만큼 송신했다" 까지 말할 수 있습니다 [1]. 위치 메시지 행의 좌표는 보낸 메시지라면 그 좌표를 공유한 기록입니다.

**증명하지 못하는 것.** 위치 메시지의 좌표는 공유한 지점이지, 그 시각에 기기가 그 자리에 있었다는 증거는 아닙니다. `ZOUTCOME` 이나 `ZMETADATA` 필드처럼 공식 근거가 없는 값은 도구의 해석이라고 밝히고 씁니다 [1]. 연락처 DB 의 행은 주소록과 왓츠앱을 맞춘 결과라서, 그 사람과 대화했다는 뜻은 아닙니다.

## 시각 해석

`ZMESSAGEDATE`, `ZDATE`, `ZABOUTTIMESTAMP` 는 Mac 절대 시각, 곧 2001-01-01 00:00:00 UTC 부터 흐른 초입니다 [1]. Unix 시각으로 바꾸려면 978,307,200 을 더하고, 결과는 UTC 입니다. 통화 종료 시각은 DB 에 저장된 값이 아니라 시작 시각에 `ZDURATION`(초)을 더해 계산한 것이라서, 보고서에는 계산값이라고 적습니다 [1]. 변환 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

## 함정과 한계

`ZWAAGGREGATECALLEVENT` 는 통화 하나가 아니라 통화 묶음 단위 행입니다 [1]. 여러 통화가 같은 묶음 행을 가리키면 수신·영상·부재중 값은 묶음 전체에 대한 것이므로, 통화 한 건마다 그 값을 그대로 붙이면 틀릴 수 있습니다 [1].

이름이 같은 `CallHistory.sqlite` 를 섞으면 Apple 통화 기록과 왓츠앱 통화 기록이 한 표에 뒤섞입니다. 경로를 반드시 함께 적습니다 [1].

표본마다 열이 다르므로 [1], 없는 열을 부르는 질의는 오류가 납니다. 도구 결과가 비어 있으면 먼저 DB 스키마를 확인합니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

지운 메시지는 표에서 행이 빠질 수 있어서, SQLite 파일의 빈 공간을 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 방법으로 따로 봅니다. 저장 형식은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 명세로 만든 예시이고 실제 기기에서 나온 값이 아닙니다. SQLite 는 실수를 8바이트 IEEE 754 빅엔디언으로 저장하므로, 시각 열에 실수 700,000,000.0 이 들어 있다면 레코드 안에서 다음 바이트로 보입니다.

```
41 C4 DC 93 80 00 00 00
```

Mac 절대 시각 700,000,000 에 978,307,200 을 더하면 Unix 1,678,307,200 이고, UTC 2023-03-08 20:26:40 입니다. 같은 값을 Unix 시각으로 착각하면 1992년이 나오므로, 1990년대 초 시각이 보이면 기준 시점부터 의심합니다.

**공개 도구로 한 번.** iLEAPP 의 왓츠앱 분석기로 메시지·연락처·통화 보고서를 만들고 [1], 같은 DB 를 SQLite 뷰어로 열어 다음 질의 결과와 행 수를 맞춰 봅니다.

```sql
SELECT datetime(ZMESSAGEDATE + 978307200, 'unixepoch') AS utc,
       ZISFROMME, ZFROMJID, ZTOJID, ZTEXT, ZMESSAGETYPE
FROM ZWAMESSAGE
ORDER BY ZMESSAGEDATE;
```

## 교차 검증

- [통화 기록](../communications/call-history.md) — 앱 통화가 Apple 통화 기록에도 남았는지 봅니다.
- [연락처](../communications/contacts.md) — `ZPHONENUMBER` 가 기기 주소록과 맞는지 봅니다.
- [알림 기록](../app-usage/notifications.md) — 받은 메시지가 알림으로도 남았는지 봅니다.
- [KnowledgeC](../app-usage/knowledgec/index.md), [바이옴](../app-usage/biome/index.md) — 메시지를 보낸 시각에 앱을 쓰고 있었는지 봅니다.
- [앱별 데이터 사용량](../network/data-usage.md) — 통화 기록의 송신 바이트와 같은 시간대의 사용량을 비교합니다.
- [사진 보관함](../media/photos/index.md) — 받은 미디어를 사진 보관함에 저장했는지 봅니다.
- [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md)

## 실습

공개 시험 데이터(NIST CFReDS 등) 가운데 왓츠앱이 설치된 iOS 전체 파일 시스템 이미지를 골라 풀어 봅니다.

1. `ChatStorage.sqlite` 에서 보낸 메시지와 받은 메시지는 각각 몇 건입니까?
2. `ZMESSAGETYPE` 이 5 인 행의 좌표와 시각을 UTC 로 적어 보십시오.
3. `ZWAMEDIAITEM.ZMEDIALOCALPATH` 가 가리키는 파일 가운데 `Message/Media/` 아래에 실제로 없는 것이 있습니까?
4. 통화 기록 DB 에 어떤 표와 열이 있는지 확인하고, 위 버전 차이 표와 비교해 보십시오.
5. 가장 긴 통화의 시작 시각과 계산한 종료 시각을 적어 보십시오.

## 참고 문헌

1. iLEAPP, scripts/artifacts/whatsApp.py — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/whatsApp.py
