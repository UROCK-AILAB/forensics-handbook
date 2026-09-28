---
title: "표와 스트림 구조"
parent: "KnowledgeC"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 340
---

# 표와 스트림 구조 (ZOBJECT·Stream)

knowledgeC.db 는 사용 기록 한 건을 ZOBJECT 표의 행 하나로 남기고, 그 행이 어떤 종류의 기록인지는 스트림 (stream) 이름으로 나눕니다. 이 페이지에서는 표 세 개가 서로 어떻게 이어지는지, 열마다 무엇이 들어가는지, 스트림 이름을 어떻게 읽는지를 다룹니다.

## 무엇을 기록하나

knowledgeC.db 에는 앱 사용, 잠금 상태, 화면 켜짐처럼 성격이 다른 기록이 한 표에 섞여 들어갑니다. 기록 종류마다 표를 따로 두지 않고 ZOBJECT 표의 ZSTREAMNAME 열에 "/app/inFocus" 같은 스트림 이름을 적어 종류를 구분하는 구조이고 [1][2][3], 공개 도구 APOLLO 의 모듈도 이 열로 행을 걸러서 스트림별로 조회합니다 [3][4].

파일 위치, 수집 방법, iOS 버전에 따라 스트림 수가 줄어든 흐름은 [KnowledgeC 허브](index.md)에 정리했습니다.

## 구조

### 표 세 개와 연결

사용 기록의 본체는 ZOBJECT 이고, 세부 정보는 ZSTRUCTUREDMETADATA 에, 기록이 어디서 왔는지는 ZSOURCE 에 따로 들어갑니다 [1][2]. ZOBJECT 행이 나머지 두 표의 기본 키(Z_PK)를 가리키는 방식이라서 APOLLO 는 두 표를 LEFT JOIN 으로 붙여 읽습니다 [3].

| 표 | 담는 것 | ZOBJECT 와 잇는 조건 |
|---|---|---|
| ZOBJECT | 사용 기록 한 건 | (본체) |
| ZSTRUCTUREDMETADATA | 기록에 덧붙는 세부 정보 | `ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK` |
| ZSOURCE | 기록의 출처. ZDEVICEID 열에 기기 ID 가 있고, APOLLO 는 이를 "하드웨어 UUID" 로 표시합니다 [1][5] | `ZOBJECT.ZSOURCE = ZSOURCE.Z_PK` |

스트림에 따라 이 세 표 말고 다른 표가 더 붙기도 하고, /app/usage 가 그런 예입니다. 자세한 내용은 [앱 사용 기록](app-usage.md) 페이지에 있습니다.

> 그림 자리: ZOBJECT 한 행에서 ZSTRUCTUREDMETADATA·ZSOURCE 행으로 이어지는 화살표와, 각 표의 주요 열

### ZOBJECT 의 열

| 열 | 담는 것 | 출처 |
|---|---|---|
| ZSTREAMNAME | 스트림 이름. 예: `/app/inFocus` | [1][2][3] |
| ZVALUESTRING | 기록 대상 값. 앱 스트림에서는 번들 ID | [2][3] |
| ZVALUEINTEGER | 켜짐·꺼짐 같은 참/거짓 스트림에서 1 또는 0 | [2] |
| ZSTARTDATE, ZENDDATE | 구간의 시작·끝 시각 (Mac 절대 시각) | [2][3] |
| ZCREATIONDATE | 행을 만든 시각 (Mac 절대 시각) | [1][3] |
| ZSECONDSFROMGMT | UTC 와의 차이(초) | [1][3] |
| ZSTARTDAYOFWEEK | 요일 숫자. 1 이 일요일이고 7 이 토요일 | [3] |
| ZHASSTRUCTUREDMETADATA | 부가 정보가 있으면 1 | [2] |
| ZSTRUCTUREDMETADATA, ZSOURCE | 다른 두 표의 Z_PK 를 가리키는 값 | [3] |
| ZUUID, Z_PK | 행 식별 값. APOLLO 출력에도 나옵니다 | [3] |

값이 무엇인지는 스트림마다 다르게 읽습니다. 앱 스트림은 ZVALUESTRING 에 번들 ID (Bundle ID) 가 들어가고, 잠금이나 화면처럼 켜짐과 꺼짐만 있는 스트림은 ZVALUEINTEGER 의 1 과 0 을 봅니다 [2]. 번들 ID 를 앱 이름과 맞추는 방법은 [번들 ID와 앱 그룹](../../../01-foundations/value-decoding/bundle-id-app-group.md) 페이지를 봅니다.

### ZSTRUCTUREDMETADATA 의 열 이름

이 표의 열 이름에는 어떤 종류의 부가 정보인지가 이름째로 들어갑니다. APOLLO 의 /app/inFocus 조회에 쓰인 열은 아래와 같습니다 [3].

```
Z_DKAPPLICATIONMETADATAKEY__LAUNCHREASON
Z_DKAPPLICATIONMETADATAKEY__EXTENSIONCONTAININGBUNDLEIDENTIFIER
Z_DKAPPLICATIONMETADATAKEY__EXTENSIONHOSTIDENTIFIER
ZMETADATAHASH
```

이 열들이 앱 기록에서 무엇을 뜻하는지는 [앱 사용 기록](app-usage.md) 페이지에서 설명합니다.

### 스트림 이름 읽는 법

스트림 이름은 "/분류/항목" 형식이라서 앞부분만 보고도 앱·기기·화면 가운데 무엇에 관한 기록인지 짐작할 수 있습니다 [1][2][5]. iOS 에서 쓰이는 이름과 이 핸드북에서 다루는 곳은 아래와 같습니다.

| 스트림 | 다루는 곳 |
|---|---|
| `/app/inFocus`, `/app/usage`, `/app/install` | [앱 사용 기록](app-usage.md) |
| `/device/isLocked`, `/display/isBacklit`, `/device/isPluggedIn`, `/device/batteryPercentage`, `/display/orientation` | [화면·잠금 상태](device-state.md) |
| `/safari/history` | [사파리](../../browsers/safari/index.md) |
| `/audio/outputRoute` | 이 핸드북에서는 따로 다루지 않습니다 |

iOS 18.5 에서 스트림 이름과 설명은 시스템 plist 인 `/System/Library/PrivateFrameworks/CoreDuet.framework/com.apple.coreduet.systemevents.plist` 에 적혀 있습니다 [6]. 이 plist 에서 스트림마다 쓰이는 항목은 아래와 같고, 이름으로 보면 기록 횟수 제한(RateLimit…)과 시각 정밀도(TimestampPrecisionInSeconds)를 스트림마다 따로 정하는 것으로 보입니다 [6]. 기록 횟수 제한이 앱 기록에 어떤 빈틈을 만드는지는 [앱 사용 기록](app-usage.md) 페이지에 있습니다.

```
KnowledgeBaseEventName
EventFormattedName
EventDescription
IsHistorical
RateLimitCount
RateLimitPeriodInSeconds
ShouldSaveCurrentEventOnShutdown
TimestampPrecisionInSeconds
```

plist 형식 자체는 [속성 목록 파일](../../../01-foundations/data-formats/plist.md) 페이지를 봅니다.

## 시각 해석

ZSTARTDATE, ZENDDATE, ZCREATIONDATE 는 모두 Mac 절대 시각 (Mac Absolute Time) 으로, 2001-01-01 00:00:00 UTC 부터 센 초이고 유닉스 시각으로 바꾸려면 978307200 을 더합니다 [1][2][3]. 저장된 값 자체는 UTC 기준이라서 현지 시각으로 보려면 시간대를 따로 적용해야 하고, APOLLO 는 ZSECONDSFROMGMT 를 3600 으로 나눠 시간대 차이를 함께 보여 줍니다 [1][3].

세 열은 뜻이 다릅니다. ZSTARTDATE 와 ZENDDATE 는 기록이 가리키는 구간의 처음과 끝이고, 두 값을 빼면 그 구간이 몇 초였는지 나옵니다 [2][3]. ZCREATIONDATE 는 행을 만든 시각이라서 구간의 시작과 같은 값이라고 가정하지 않습니다 [1][3].

사용자가 기기 시각을 손으로 바꾸면 기록되는 시각도 함께 틀어집니다 [2]. 시각 값 형식 전반은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지를, 기기의 시간대 설정은 [시간대와 시각 설정](../../system-account/time-zone.md) 페이지를 봅니다.

## 함정과 한계

공개 자료에 나온 표와 열 구성은 대부분 iOS 11~13 과 macOS 기준입니다 [3][4]. 로컬 백업에는 knowledgeC.db 가 들어 있지 않을 수 있습니다. 그래서 새 버전 데이터를 열 때는 열 이름부터 `PRAGMA table_info(ZOBJECT);` 로 확인하고 나서 조회문을 돌리는 편이 안전합니다.

맥에도 같은 이름의 DB 가 있고 [1] 공개 자료에는 맥에서 확인한 내용이 섞여 있어서, 글을 인용할 때는 iOS 에 관한 내용인지 먼저 확인합니다.

WAL 파일 처리와 지운 행 복구가 knowledgeC.db 에서 어떻게 되는지는 실제 데이터로 확인해야 합니다. SQLite 일반 원리는 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 페이지와 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 페이지에 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 명세에 따라 만든 예시이고, 실제 데이터에서 나온 값이 아닙니다. SQLite 레코드에서 실수는 자료형 번호(serial type) 7 이고, 8 바이트 빅 엔디언 IEEE 754 배정밀도 값으로 저장됩니다. ZSTARTDATE 열의 값이 이렇게 저장되어 있다고 할 때 읽는 순서는 다음과 같습니다.

```
헥스:        41 C4 DC 93 80 20 00 00
실수 값:     700000000.25            (Mac 절대 시각, 초)
유닉스 시각: 700000000.25 + 978307200 = 1678307200.25
UTC:         2023-03-08 20:26:40.25
```

ZENDDATE 가 700000900.25 라면 두 값의 차이인 900 초, 곧 15 분이 이 구간의 길이입니다. 레코드 머리와 자료형 번호를 읽는 법은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 페이지를 봅니다.

### 공개 도구로 한 번

원본은 건드리지 않고 사본에서 작업하며, 같은 폴더에 `-wal`·`-shm` 파일이 있으면 함께 복사합니다. 먼저 어떤 스트림이 몇 건 있는지 봅니다.

```sql
SELECT ZSTREAMNAME, COUNT(*) AS CNT,
       DATETIME(MIN(ZSTARTDATE) + 978307200, 'UNIXEPOCH') AS FIRST_UTC,
       DATETIME(MAX(ZSTARTDATE) + 978307200, 'UNIXEPOCH') AS LAST_UTC
FROM ZOBJECT
GROUP BY ZSTREAMNAME
ORDER BY CNT DESC;
```

그다음 APOLLO 모듈이 쓰는 연결 방식을 본떠 세 표를 이어 봅니다 [3]. 아래 조회문은 설명을 위해 줄인 것입니다.

```sql
SELECT
  ZOBJECT.Z_PK,
  ZOBJECT.ZSTREAMNAME,
  ZOBJECT.ZVALUESTRING,
  ZOBJECT.ZVALUEINTEGER,
  DATETIME(ZOBJECT.ZSTARTDATE + 978307200, 'UNIXEPOCH')    AS START_UTC,
  DATETIME(ZOBJECT.ZENDDATE + 978307200, 'UNIXEPOCH')      AS END_UTC,
  ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE                    AS SECONDS,
  ZOBJECT.ZSECONDSFROMGMT / 3600                           AS GMT_OFFSET,
  DATETIME(ZOBJECT.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS CREATED_UTC,
  ZSOURCE.ZDEVICEID
FROM ZOBJECT
LEFT JOIN ZSTRUCTUREDMETADATA ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
LEFT JOIN ZSOURCE ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
ORDER BY ZOBJECT.ZSTARTDATE;
```

APOLLO(mac4n6) 는 스트림마다 이런 SQL 을 모듈 파일로 나눠 두고 있어서 [3][4][5], 모듈이 어떤 iOS 버전을 대상으로 적혀 있는지 함께 확인하고 쓰면 됩니다. 도구 결과를 손 조회와 맞춰 보는 방법은 [도구 검증](../../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다.

## 교차 검증

새 버전 기기에서는 [바이옴 (Biome)](../biome/index.md) 스트림과 짝을 맞춰 보고, 어느 버전부터 무엇이 옮겨 갔는지는 [KnowledgeC 허브](index.md)를 봅니다. 바이옴 기록 파일의 형식은 [SEGB 형식](../../../01-foundations/data-formats/segb.md) 페이지에 있습니다. 여러 아티팩트의 시각을 한 줄로 늘어놓는 방법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 페이지를 봅니다.

## 참고 문헌

1. Sarah Edwards (mac4n6), "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (2018-08) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. Belkasoft, "KnowledgeC Database Forensics: A Comprehensive Guide" — https://belkasoft.com/knowledgec-database-forensics-with-belkasoft
3. APOLLO, modules/knowledge_app_inFocus.txt (mac4n6) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_app_inFocus.txt
4. APOLLO, modules/knowledge_device_locked.txt (mac4n6) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_device_locked.txt
5. APOLLO, modules/knowledge_app_usage.txt (mac4n6) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_app_usage.txt
6. John Hyla (Blue Crew Forensics), "iOS Stream Names" (2025-06-03) — https://bluecrewforensics.com/2025/06/03/ios-stream-names/
