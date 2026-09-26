---
title: "페이스타임과 통화 기록"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1380
---

# 페이스타임과 통화 기록 (FaceTime·CallHistory)

통화 기록은 Core Data 형식 SQLite 파일 `CallHistory.storedata` 에 들어 있고, 통화 한 건이 `ZCALLRECORD` 표의 한 행이라서 행마다 시작 시각·길이·상대 주소·방향·응답 여부를 읽습니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

통화 기록 DB는 걸거나 받은 통화 한 건마다 `ZCALLRECORD` 표에 행을 하나 만듭니다 [1][2]. 같은 DB가 iOS와 macOS 양쪽에 있고 [2], iOS 추출본을 읽는 공개 도구 iLEAPP도 같은 표를 읽습니다 [1].

행 하나에는 통화가 시작된 시각과 길이, 상대 번호나 주소, 이쪽에서 건 통화인지 걸려 온 통화인지, 받았는지, 어떤 종류의 통화였는지, 어떻게 끊겼는지가 함께 담깁니다 [1][2]. 다만 맥에서 어떤 경로의 통화가 이 DB에 행으로 남는지는 공개 자료가 없습니다. 맥에서 직접 건 FaceTime 통화, 아이폰으로 온 전화를 맥에서 받은 통화, 아이폰의 통화 기록이 iCloud로 넘어온 행이 각각 남는지와 그 조건은 검체에서 따로 확인해야 합니다.

## 위치와 버전별 차이

파일 이름은 `CallHistory.storedata` 입니다 [2]. 맥의 전체 경로로 `~/Library/Application Support/CallHistoryDB/CallHistory.storedata` 가 흔히 알려져 있지만 이를 밝힌 공개 분석 자료는 없어서, 수집한 이미지 전체에서 파일 이름으로 찾은 뒤 실제 경로를 보고서에 적습니다.

iOS 추출본에서는 아래 경로 패턴에 같은 DB가 있습니다 [1]. 아이폰 백업이나 추출본을 맥과 함께 볼 때는 [아이폰·아이패드 연결 (iOS Devices)](../external-devices/ios-devices/index.md)도 봅니다.

```
*/mobile/Library/CallHistoryDB/CallHistory*
*/mobile/Library/CallHistoryDB/call_history.db*
```

APOLLO 모듈이 적은 버전 목록은 `8,9,10,11,12,13,10.13,10.14,10.15,10.16,14` 이고 [2], 이 가운데 10.x는 macOS 버전, 8~14는 iOS 버전으로 보입니다.

| 버전 | 알려진 내용 |
|---|---|
| macOS 10.13 ~ 10.16 | APOLLO 모듈의 버전 목록에 있습니다 [2] |
| macOS 11 이후 | 모듈 목록에 따로 없어서, 표와 칸이 같은지는 검체에서 확인합니다 |
| iOS 8 ~ 14 | APOLLO 모듈의 버전 목록에 있습니다 [2] |
| iOS 26 | 칸 4개(`ZAUTOANSWEREDREASON`, `ZCOMMUNICATIONTRUSTSCORE`, `ZORIGINATINGDEVICENAME`, `ZBLOCKEDBYEXTENSIONNAME`)가 늘었습니다 [1]. macOS 26에 같은 칸이 생겼는지는 공개 자료가 없습니다 |

## 구조

칸 이름에 `Z` 가 붙은 Core Data 형식이라서 [1][2], 표와 칸을 읽는 일반 규칙은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 봅니다. `ZCALLRECORD` 의 주요 칸은 아래와 같습니다.

| 칸 | 뜻 |
|---|---|
| `Z_PK` | 행 번호 [2] |
| `ZDATE` | 통화 시작 시각. 2001-01-01 기준 초로 센 맥 절대 시각입니다 [1][2] |
| `ZDURATION` | 통화 길이(초) [1][2] |
| `ZADDRESS` | 상대 번호나 주소. APOLLO는 macOS 10.13~10.16 쿼리에서 `HEX(CAST(ZADDRESS AS TEXT))` 로 16진 출력하고, iOS 쿼리에서는 `CAST(ZADDRESS AS TEXT)` 로 글자 그대로 뽑습니다 [2] |
| `ZANSWERED` | 0 = 받지 않음, 1 = 받음 [1] |
| `ZORIGINATED` | 0 = 걸려 온 통화, 1 = 건 통화 [1] |
| `ZCALLTYPE` | 0 = 서드파티 앱, 1 = 전화, 8 = FaceTime 영상, 16 = FaceTime 음성 [1] |
| `ZSERVICE_PROVIDER` | 통화를 맡은 서비스를 가리키는 문자열 [1][2] |
| `ZDISCONNECTED_CAUSE` | 끊긴 이유 번호 [1][2] |
| `ZISO_COUNTRY_CODE`, `ZLOCATION` | 나라 코드와 지역 [1][2] |
| `ZFACE_TIME_DATA` | 데이터 양(바이트 수), KB·MB 같은 단위로 바꿔 읽습니다 [1]. 맥 DB에서도 같은 뜻인지는 검체에서 확인합니다 |

`ZCALLTYPE` 값의 뜻은 iOS 기준이고 [1], 맥 DB에서도 같은 값을 쓰는지는 공개 자료가 없습니다. `ZSERVICE_PROVIDER` 에 실제로 어떤 철자의 문자열이 들어가는지도 공개 자료가 없어서, 검체에서 나온 값을 그대로 옮겨 적습니다.

`ZDISCONNECTED_CAUSE` 는 앱에 따라 뜻이 달라집니다. 일반 앱에서는 0이 정상 종료, 6이 거절입니다. WhatsApp 행에서는 2가 거절이고, 6은 통화 길이와 방향에 따라 길이가 0이 아니면 정상 종료, 건 통화면 부재 중이거나 거절, 나머지는 부재 중입니다 [1]. 그래서 이 칸은 `ZSERVICE_PROVIDER` 와 함께 읽습니다.

APOLLO가 macOS 쿼리에서만 `ZADDRESS` 를 16진으로 찍는 것으로 보아, 맥 DB에서는 이 칸이 문자열이 아닌 BLOB로 저장될 가능성이 있습니다 [2]. 검체에서 `typeof(ZADDRESS)` 로 저장 형식을 먼저 봅니다.

## 증거로서 의미

**증명하는 것.** 행이 있으면 이 DB에 그 시각에 시작해 그만큼 이어진 통화가 기록되어 있고, 상대 주소와 방향(`ZORIGINATED`), 응답 여부(`ZANSWERED`)가 그렇게 적혀 있다는 사실을 보여 줍니다. `ZCALLTYPE` 과 `ZSERVICE_PROVIDER` 를 함께 보면 전화였는지 FaceTime이었는지, 영상이었는지 음성이었는지를 기록 수준에서 가를 수 있습니다.

**증명하지 못하는 것.** 통화에서 무슨 말이 오갔는지는 이 DB에 없습니다. 통화할 때 맥 앞에 누가 있었는지도 이 기록만으로는 알 수 없어서, 로그인 기록과 사용 시간을 따로 봅니다. 행이 이 맥에서 일어난 통화인지, 다른 기기의 기록이 넘어온 것인지를 가르는 방법은 공개 자료가 없고, iOS 26에서 생긴 `ZORIGINATINGDEVICENAME` 이 이름대로 걸었던 기기를 가리키는지도 알려지지 않았습니다.

`ZDURATION` 이 0인 행을 곧바로 "받지 않은 통화" 로 적지 않습니다. 응답 여부는 `ZANSWERED` 가 따로 말해 주고, 끊긴 이유는 `ZDISCONNECTED_CAUSE` 가 말해 주니 세 칸을 함께 읽습니다.

보고서에는 "`ZCALLRECORD` 의 `Z_PK` ○○ 행에 UTC ○○시 ○○분에 시작해 ○○초 동안 이어진, `ZORIGINATED` 값 1(건 통화)·`ZCALLTYPE` 값 ○인 통화가 기록되어 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

`ZDATE` 는 2001-01-01 00:00:00 UTC부터 센 초라서, 유닉스 시각으로 바꾸려면 978307200을 더합니다 [2]. 이 값은 Cocoa Core Data 시각이고 [1], SQL로는 `DATETIME(ZDATE+978307200,'UNIXEPOCH')` 로 바꿉니다 [2]. 현지 시각으로 옮길 때는 검체의 시간대 설정을 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)에서 확인하고, 값의 기준점과 단위는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 봅니다.

끝 시각은 DB에 따로 있지 않아서 `ZDATE + ZDURATION` 으로 계산합니다. iLEAPP는 이렇게 계산하되 길이가 0이면 끝 시각을 비워 둡니다 [1]. APOLLO는 길이를 초와 분(`ZDURATION/60.00`)으로 함께 보여 줍니다 [2].

## 함정과 한계

맥 쪽 공개 자료는 적습니다. APOLLO 모듈에는 macOS 11 이후가 따로 없고, 칸 값의 뜻은 대부분 iOS 기준인 iLEAPP에서 왔으니, 최신 macOS 검체에서는 `.schema ZCALLRECORD` 로 칸 목록부터 확인하고 모르는 값은 풀지 않고 숫자 그대로 적습니다.

통화 기록을 지웠을 때 이 DB에 무엇이 남는지는 공개 자료가 없습니다. WAL 파일과 빈 페이지에 남는 잔재를 찾는 일반 방법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)와 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)에서 다루고, 그 방법이 이 DB에서 통하는지는 검체마다 확인합니다. FaceTime 앱의 설정 plist와 통화 관련 통합 로그 서브시스템도 공개 분석 자료가 없어 검체에서 확인합니다.

## 직접 분석해 보기

**헥스로 한 번.** 먼저 파일이 평문 SQLite인지 봅니다. SQLite 파일은 첫 16바이트가 `SQLite format 3` 과 널 바이트 하나입니다. 아래는 SQLite 파일 형식 명세로 만든 예시이고, 검체에서 나온 값이 아닙니다.

```
00000000  53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00  |SQLite format 3.|
```

```sh
xxd -l 16 CallHistory.storedata
```

**sqlite3로 한 번.**

1. `CallHistory.storedata` 와 같은 폴더의 `-wal`, `-shm` 파일을 함께 수집하고 사본에서 작업합니다.
2. `.schema ZCALLRECORD` 로 칸 목록을 보고 위 구조 표와 다른 칸이 있는지 적습니다.
3. APOLLO 모듈의 macOS 쿼리 식을 따라 행을 뽑습니다.

   ```sql
   SELECT Z_PK,
          DATETIME(ZDATE + 978307200, 'unixepoch') AS start_utc,
          ZDURATION,
          HEX(CAST(ZADDRESS AS TEXT)) AS address_hex,
          typeof(ZADDRESS) AS address_type,
          ZORIGINATED, ZANSWERED, ZCALLTYPE,
          ZSERVICE_PROVIDER, ZDISCONNECTED_CAUSE,
          ZISO_COUNTRY_CODE, ZLOCATION
   FROM ZCALLRECORD
   ORDER BY ZDATE;
   ```

4. 같은 사본을 공개 도구로 읽어 결과를 맞춰 봅니다. 맥 검체는 APOLLO의 `call_history` 모듈 [2], 아이폰 추출본은 iLEAPP [1]로 읽고, 행 수와 시각이 SQL 결과와 같은지 확인합니다.

## 교차 검증

| 함께 볼 자료 | 확인할 것 |
|---|---|
| [연락처 (Contacts)](../cloud-apps/contacts.md) | `ZADDRESS` 번호나 주소에 붙은 이름 |
| [메시지 (iMessage·SMS)](imessage/index.md) | 같은 상대와 같은 시간대에 주고받은 메시지 |
| [연속성과 유니버설 클립보드 (Continuity·Handoff)](../cloud-apps/continuity.md) | 행이 다른 기기에서 넘어왔을 가능성 |
| [아이폰·아이패드 연결 (iOS Devices)](../external-devices/ios-devices/index.md) | 아이폰 쪽 통화 기록과의 차이 |
| [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../../04-scenarios/activity/usage-time.md) | 통화 시각에 맥이 켜져 있었고 누가 로그인해 있었는지 |
| [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) | 여러 통신 기록을 묶어 보는 조사 흐름 |

## 실습

공개 검체(NIST CFReDS 등) 가운데 맥 사용자 폴더가 들어 있는 이미지를 골라 아래 질문을 풀어 봅니다.

1. 이미지 안에서 `CallHistory.storedata` 는 어느 경로에 있고, 같은 폴더에 `-wal` 파일이 있는가?
2. `ZCALLRECORD` 의 칸 목록은 위 구조 표와 같은가, 다르다면 어떤 칸이 더 있거나 빠졌는가?
3. `ZCALLTYPE` 과 `ZSERVICE_PROVIDER` 에는 어떤 값들이 나오고, 값마다 몇 행인가?
4. `ZANSWERED` 가 0인 걸려 온 통화는 몇 건이고, 그 가운데 `ZDURATION` 이 0이 아닌 행이 있는가?

## 참고 문헌

1. abrignoni/iLEAPP `scripts/artifacts/callHistory.py` (GitHub) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/callHistory.py
2. mac4n6/APOLLO `modules/call_history.txt` (GitHub) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/call_history.txt
