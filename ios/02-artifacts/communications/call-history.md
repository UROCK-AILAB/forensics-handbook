---
title: "통화 기록"
parent: "아티팩트 · 통화·메시지·연락처"
nav_order: 500
---

# 통화 기록 (CallHistory)

아이폰의 전화 앱 "최근 기록" 뒤에 있는 SQLite 데이터베이스로, 통화 한 건마다 시각·통화 시간·방향·상대 주소·처리한 서비스를 한 행씩 남기며 FaceTime 과 다른 회사 앱의 통화도 같은 표에 섞여 들어갑니다.

## 무엇을 기록하나 · 왜 생기나

iOS 는 전화를 걸거나 받을 때마다 통화 기록 데이터베이스 `CallHistory.storedata` 의 `ZCALLRECORD` 표에 한 행을 씁니다 [1][2]. 이동통신 전화만 들어가는 곳이 아니라서 FaceTime 영상·음성 통화와, 전화 앱과 연동하는 다른 회사 앱(예: WhatsApp)의 통화도 같은 표에 남고, 어느 서비스가 처리했는지는 `ZSERVICE_PROVIDER` 열에 적힙니다 [1].

한 행에는 통화를 시작한 시각, 통화 시간(초), 건 통화인지 받은 통화인지, 받았는지, 상대 주소(번호), 끊긴 사유, 국가 코드, 위치 문자열이 들어갑니다 [1]. 사용자가 전화 앱에서 보는 최근 기록 목록과 같은 자료라서, "누구와 언제 통화했나" 를 묻는 조사에서 가장 먼저 여는 곳입니다. 조사 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 에서 다룹니다.

## 위치와 버전별 차이

기기 안의 경로는 `/private/var/mobile/Library/CallHistoryDB/` 이고, 공개 도구 iLEAPP 는 이 폴더에서 이름이 `CallHistory` 로 시작하는 파일(`CallHistory.storedata`, `CallHistoryTemp.storedata`)과 예전 형식의 `call_history.db` 를 찾습니다 [1]. `CallHistoryTemp.storedata` 의 용도를 밝힌 공개 자료는 없습니다.

로컬 백업에는 이 파일이 늘 들어가지는 않습니다. 암호화하지 않은 백업에는 `CallHistoryDB` 경로가 없고, 이름에 CallHistory 가 들어간 파일은 설정 파일 `HomeDomain :: Library/Preferences/com.apple.CallHistorySyncHelper.plist` 하나뿐일 수 있습니다. 백업을 암호화해야 들어가는 자료의 범위는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다루고, 통화 기록이 필요하면 수집 방법부터 정해야 합니다. 수집 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 를 봅니다.

| 구분 | 내용 | 출처 |
|---|---|---|
| 예전 형식 | `call_history.db` 의 `call` 표. `flags` 값을 풀어 방향을 읽고 시각 기준이 Core Data 시각과 다릅니다. 어느 iOS 까지 이 형식이었는지는 공개 자료가 없습니다 | [1] |
| 현재 형식 | `CallHistory.storedata` 의 `ZCALLRECORD` 표 (Core Data) | [1][2] |
| 도구 시험 범위 | iLEAPP 통화 기록 모듈은 iOS 12.4 ~ 18.7.8 표본 15개로 시험되었습니다 | [1] |
| iOS 26 | `ZAUTOANSWEREDREASON`, `ZCOMMUNICATIONTRUSTSCORE`, `ZORIGINATINGDEVICENAME`, `ZBLOCKEDBYEXTENSIONNAME` 열이 새로 보입니다 | [1] |
| iOS 27 | 열 변화는 실제 데이터로 확인해야 합니다 | |

## 구조

`ZCALLRECORD` 는 통화 한 건이 한 행이고, 분석에 쓰는 열은 다음과 같습니다 [1].

| 열 | 뜻 |
|---|---|
| `ZDATE` | 통화 시작 시각. Mac 절대 시각(초) |
| `ZDURATION` | 통화 시간(초) |
| `ZORIGINATED` | 0 = 받은 통화, 1 = 건 통화 |
| `ZANSWERED` | 0 = 안 받음, 1 = 받음 |
| `ZCALLTYPE` | 0 = 다른 회사 앱, 1 = 전화, 8 = FaceTime 영상, 16 = FaceTime 음성 |
| `ZSERVICE_PROVIDER` | 통화를 처리한 서비스. 다른 회사 앱이면 앱 이름이 들어갑니다 |
| `ZADDRESS` | 상대 주소(번호) |
| `ZDISCONNECTED_CAUSE` | 끊긴 사유. iLEAPP 는 0 을 정상 종료, 6 을 거절로 읽습니다 |
| `ZFACE_TIME_DATA` | FaceTime 관련 데이터. 담긴 내용은 공개 자료 없음 |
| `ZISO_COUNTRY_CODE`, `ZLOCATION` | 국가 코드와 위치 문자열 |

`ZDISCONNECTED_CAUSE` 의 뜻은 iLEAPP 의 해석이고 Apple 문서에는 없는 값입니다. 게다가 WhatsApp 통화에서는 iLEAPP 가 6 을 통화 시간과 방향에 따라 종료·부재중·거절로 나눠 읽고 2 를 거절로 읽을 만큼 앱마다 쓰임이 달라서, 보고서에는 "끊긴 사유 값이 6 으로 기록됨" 처럼 저장된 값을 함께 적는 편이 안전합니다 [1]. iOS 26 에서 새로 보인 열 4개도 iLEAPP 는 저장된 값 그대로만 보여 줍니다 [1].

여럿이 함께한 통화는 `ZCALLRECORD` 한 행으로는 드러나지 않습니다. 이 표에는 그룹 통화를 표시하는 열이 따로 없어서, 참여자 번호를 담은 `ZHANDLE` 표(`Z_PK`, `ZVALUE`)와 연결 표 `Z_2REMOTEPARTICIPANTHANDLES`(열 `Z_2REMOTEPARTICIPANTCALLS`, `Z_4REMOTEPARTICIPANTHANDLES`)를 이어 읽어야 한 통화에 상대가 여러 명이었는지 알 수 있습니다 [2]. 이 구조는 그룹 FaceTime 통화 시험의 결과이고, 시험한 iOS 버전은 알려져 있지 않습니다 [2]. 연결 표 이름의 숫자는 Core Data 가 붙이는 번호라 버전마다 바뀔 수 있으니, 표 이름을 고정해 두지 말고 `sqlite_master` 에서 먼저 찾습니다.

Core Data 가 만드는 SQLite 의 일반 구조는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

### 곁에 있는 설정 파일

암호화하지 않은 백업에는 통화 기록 DB 대신 통화 기능의 설정 파일이 남습니다. 값의 뜻을 밝힌 공개 자료가 없어서 단서로만 씁니다.

| 파일 (HomeDomain) | 키 |
|---|---|
| `Library/Preferences/com.apple.CallHistorySyncHelper.plist` | `com.apple.private.alloy.callhistorysync.devices`, `CHSpotlightReindexingReasonKey`, `kCHLastFetchedContactHistoryToken`, `CHFacetimeSearchableStatus`, `CKStartupTime` 등 |
| `Library/Preferences/com.apple.mobilephone.plist` | `RecentsListFilter`, `DialerShouldSuppressShowingLastDialedNumber`, `CallScreeningEnabledCached`, `PHLastTabTypeKey` 등 |
| `Library/Preferences/com.apple.TelephonyUtilities.plist` | `CallScreeningDisabled`, `ReceptionistDisabled`, `SiriGreetings`, `IntelligentRoutingServiceToken` 등 |
| `Library/Accessibility/com.apple.RTTTranscripts.sqlite` | `ZTTYHISTORY`(`ZCALLUID`, `ZDATA` 등), `ZTTYCONTACTLIST`(`ZCALLUID`, `ZCONTACTID` 등) 표 |

`CallHistorySyncHelper.plist` 의 `callhistorysync.devices` 키는 이름으로 짐작하면 기기 사이 통화 기록 동기화와 관련된 것으로 보입니다. `RTTTranscripts.sqlite` 는 열 이름으로 짐작하면 RTT·TTY 통화의 대화 기록을 담는 곳으로 보입니다. 이 밖에 `WirelessDomain :: Library/Preferences/com.apple.commcenter.callservices.plist` 에 `last.known.icloud.id` 키가 있습니다.

## 증거로서 의미

**증명하는 것.** 기록된 시각에 이 기기의 전화 기능이 해당 주소와 통화를 시작했거나 받으려 했다는 사실, 그리고 받았는지·건 것인지·몇 초 동안 이어졌는지를 보여 줍니다 [1]. `ZSERVICE_PROVIDER` 와 `ZCALLTYPE` 으로 이동통신 통화인지, FaceTime 인지, 다른 회사 앱 통화인지 가를 수 있습니다 [1].

**증명하지 못하는 것.** 통화 내용은 남지 않고, 기기를 손에 든 사람이 누구였는지도 알려 주지 않습니다. 사람을 좁히는 방법은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다. 표에 행이 없다고 통화가 없었다고 쓸 수도 없는데, 지운 통화와 보존 기간이 이 DB 에서 어떻게 처리되는지 밝힌 공개 자료가 없기 때문입니다. `ZADDRESS` 는 번호 또는 주소 문자열일 뿐이라서 그 번호가 누구인지는 [연락처](contacts.md) 와 맞춰 봐야 합니다.

보고서 문장은 "피의자가 A 와 통화했다" 가 아니라 "이 기기의 통화 기록에 2026-05-09 06:13:20 UTC, 상대 번호 X, 건 통화, 받음, 통화 시간 N초로 기록된 행이 있다" 처럼 씁니다.

## 시각 해석

`ZDATE` 는 Mac 절대 시각, 곧 2001-01-01 00:00:00 UTC 부터 흐른 초이고 iLEAPP 도 이 기준으로 UTC 로 바꿉니다 [1]. 값은 UTC 라서 보고서에 현지 시각을 쓸 때는 기기의 시간대를 따로 확인해야 하며, 시간대 흔적은 [시간대와 시각 설정](../system-account/time-zone.md) 에서 봅니다. Mac 절대 시각과 UNIX 시각을 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 정리되어 있습니다.

`ZDATE` 는 통화가 시작된 시각이고, iLEAPP 는 끝 시각을 `ZDATE + ZDURATION` 으로 계산하며 통화 시간이 0 이면 끝 시각을 비워 둡니다 [1]. 끝 시각은 기록된 값이 아니라 계산한 값이라는 점을 보고서에 밝힙니다.

## 함정과 한계

- **전화 앱 기록을 이동통신 통화로 보는 오해.** `ZCALLTYPE` 0 행은 다른 회사 앱 통화이고 `ZSERVICE_PROVIDER` 에 앱 이름이 들어갑니다 [1]. 통신사 통화 내역과 대조할 때 이런 행을 빼야 개수가 맞습니다. 이동통신·FaceTime 행의 `ZSERVICE_PROVIDER` 에 어떤 문자열이 들어가는지는 실제 데이터에서 값을 직접 봅니다.
- **예전 형식과 섞어 읽는 실수.** 예전 `call_history.db` 는 표·열·시각 기준이 모두 달라서 [1], 도구가 어느 형식을 읽었는지 확인합니다.
- **백업에 없는 DB.** 암호화하지 않은 백업에는 이 DB 가 없습니다. 결과가 비었을 때 "통화가 없다" 가 아니라 "수집 범위에 없다" 로 적습니다.
- **그룹 통화 누락.** `ZADDRESS` 만 보면 여럿이 한 통화의 다른 참여자를 놓칩니다 [2].
- **해석값에 기대기.** `ZDISCONNECTED_CAUSE` 와 iOS 26 새 열은 뜻을 밝힌 공식 문서가 없습니다 [1].

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 파일 형식 명세로 만든 예시이고 실제 기기의 값이 아닙니다. Core Data 는 `ZDATE` 를 실수(REAL)로 저장하고, SQLite 레코드 안에서 실수는 형식 번호(serial type) 7, 곧 8바이트 빅 엔디언 IEEE 754 로 들어갑니다.

```
레코드 본문 안의 ZDATE 8바이트
41 C7 D7 84 00 00 00 00
= 800000000.0 (double, 빅 엔디언)
= 2001-01-01 00:00:00 UTC + 800000000초
= 2026-05-09 06:13:20 UTC
```

같은 레코드의 `ZORIGINATED`, `ZANSWERED` 처럼 작은 정수는 형식 번호 1(1바이트 정수)이나, 값이 0·1 이면 본문 바이트 없이 형식 번호 8·9 로만 표시되기도 합니다. 헥스로 행을 따라갈 때는 레코드 머리의 형식 번호부터 읽어야 필드 경계를 맞출 수 있습니다.

### 공개 도구로 한 번

수집한 `CallHistory.storedata` 를 사본으로 떠서 `sqlite3` 로 엽니다. WAL 파일이 함께 있으면 같이 복사해야 최근 행이 빠지지 않습니다.

```sql
SELECT Z_PK,
       datetime(ZDATE + 978307200, 'unixepoch') AS start_utc,
       ZDURATION, ZORIGINATED, ZANSWERED, ZCALLTYPE,
       ZSERVICE_PROVIDER, ZADDRESS, ZDISCONNECTED_CAUSE
FROM ZCALLRECORD
ORDER BY ZDATE;
```

`978307200` 은 1970-01-01 과 2001-01-01 사이의 초입니다. 같은 파일을 iLEAPP 의 통화 기록 모듈로도 돌려 두 결과의 행 수와 시각이 같은지 맞춰 봅니다 [1]. 도구 결과를 서로 맞추는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에 있습니다.

## 교차 검증

상대 번호가 누구인지는 [연락처](contacts.md) 에서, 같은 상대와 주고받은 문자는 [메시지](messages/index.md) 에서 찾습니다. FaceTime 행은 [페이스타임](facetime.md), 부재중 뒤에 남은 음성 메시지와 녹음은 [음성 사서함과 통화 녹음](voicemail-recording.md) 과 이어 봅니다. 다른 회사 앱 통화라면 해당 앱의 데이터와 대조하는데, 예를 들어 [왓츠앱](../messengers/whatsapp.md) 의 통화 기록과 맞춰 봅니다. 통화 무렵 기기를 쓰고 있었는지는 [KnowledgeC](../app-usage/knowledgec/index.md), [바이옴](../app-usage/biome/index.md), [알림 기록](../app-usage/notifications.md) 과 함께 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올려 확인합니다.

## 실습

NIST CFReDS 등에 공개된 iOS 시험 데이터로 풀어 봅니다.

1. 시험 데이터에 `CallHistory.storedata` 가 있습니까? 없다면 어떤 수집 방법이었기 때문인지 데이터 설명에서 찾아 보십시오.
2. `ZCALLTYPE` 값별로 행이 몇 개입니까? 0 인 행의 `ZSERVICE_PROVIDER` 에는 어떤 앱 이름이 들어 있습니까?
3. 받지 않은 받은 통화(`ZORIGINATED` 0, `ZANSWERED` 0)를 시각순으로 뽑고, 같은 시각대의 알림 기록과 맞춰 보십시오.
4. 참여자가 두 명 이상인 통화가 있는지 `ZHANDLE` 과 연결 표를 이어 확인해 보십시오.
5. iLEAPP 결과의 끝 시각과 직접 계산한 `ZDATE + ZDURATION` 이 모든 행에서 같습니까?

## 참고 문헌

1. iLEAPP, `scripts/artifacts/callHistory.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/callHistory.py
2. James McGee, The Metadata Perspective, "Hello! Who is on the Line?" (2025-02-05) — https://metadataperspective.com/2025/02/05/hello-who-is-on-the-line/
