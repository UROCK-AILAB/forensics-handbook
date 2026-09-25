---
title: "표와 스트림 구조"
parent: "KnowledgeC"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 670
---

# 표와 스트림 구조 (ZOBJECT·Stream)

knowledgeC.db는 SQLite 데이터베이스이고, 사용 기록 한 건은 ZOBJECT 표의 한 행에 시작·끝 시각과 값으로 들어 있으며 어떤 종류의 기록인지는 `ZSTREAMNAME` 칸의 스트림 이름이 정합니다.

## 무엇이 들어 있나

기록의 본체는 ZOBJECT 표이고, 기록이 어디서 왔는지는 ZSOURCE 표에, 앱이 남긴 추가 정보는 ZSTRUCTUREDMETADATA 표에 들어 있습니다 [1]. 한 행은 "어떤 스트림에서, 언제부터 언제까지, 어떤 값이었다" 를 적은 구간이라서, 앱을 쓴 기록이든 화면이 켜져 있던 기록이든 같은 모양으로 읽습니다. 두 DB 파일이 있는 위치는 [KnowledgeC (knowledgeC.db)](index.md) 허브에 정리했고, SQLite 파일 자체를 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

아래 내용은 Sarah Edwards의 블로그 글 [1]과 그가 공개한 분석 도구 APOLLO의 모듈 SQL [2]~[5]에서 확인한 것이고, 블로그 글은 macOS 10.13과 iOS 11을 기준으로 썼습니다.

## 표 관계

APOLLO 모듈은 ZOBJECT를 기준으로 두 표를 LEFT JOIN으로 붙입니다 [2]~[5].

```
ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
ZOBJECT.ZSOURCE             = ZSOURCE.Z_PK
```

`/app/usage` 스트림을 읽는 모듈만 표 두 개를 더 거칩니다 [2].

```
ZOBJECT.Z_PK = Z_4EVENT.Z_11EVENT
Z_4EVENT.Z_4CUSTOMMETADATA = ZCUSTOMMETADATA.Z_PK
```

`Z_4EVENT`, `Z_11EVENT` 처럼 숫자가 붙은 이름이 macOS 버전마다 같은지는 참고 자료로 확인하지 못했습니다. 다른 버전의 검체에서 이 쿼리가 오류를 내면 먼저 표 목록에서 비슷한 이름을 찾아 봅니다.

> 그림 자리: ZOBJECT를 가운데 두고 ZSOURCE·ZSTRUCTUREDMETADATA가 붙고, `/app/usage` 일 때만 Z_4EVENT를 거쳐 ZCUSTOMMETADATA로 이어지는 관계도

## ZOBJECT 주요 칸

| 칸 | 뜻 | 출처 |
|---|---|---|
| `ZSTREAMNAME` | 스트림 이름(기록 종류). 예 `/app/inFocus` | [1]~[5] |
| `ZSTARTDATE` / `ZENDDATE` | 구간의 시작과 끝(맥 절대 시각). 끝에서 시작을 빼면 사용 시간(초) | [1]~[5] |
| `ZVALUESTRING` | 앱 기록이면 번들 ID, `/safari/history` 면 URL | [1][2][3] |
| `ZVALUEINTEGER` | 상태형 스트림의 값(0 또는 1) | [1][4][5] |
| `ZSTARTDAYOFWEEK` | 요일 숫자. 1이 일요일, 7이 토요일 | [1][2] |
| `ZSECONDSFROMGMT` | UTC와의 차이(초). APOLLO는 3600으로 나눠 시간 단위로 보여 줌 | [1][2] |
| `ZCREATIONDATE` | 기록을 DB에 쓴 시각 | [1][2] |
| `ZUUID` | 기록 UUID | [2]~[5] |
| `Z_PK` | 행 번호 | [2]~[5] |
| `ZSTRUCTUREDMETADATA` / `ZSOURCE` | 다른 표로 가는 연결 칸 | [2]~[5] |

값이 문자열인 스트림은 `ZVALUESTRING` 을, 켜짐·꺼짐처럼 상태를 적는 스트림은 `ZVALUEINTEGER` 를 읽습니다. 번들 ID (Bundle ID) 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다.

## 딸린 표

### ZSOURCE

`ZDEVICEID` 는 기기를 가리키는 칸이고, APOLLO는 이 칸에 "DEVICE ID (HARDWARE UUID)" 라는 이름을 붙여 보여 줍니다 [1][2][4]. `ZBUNDLEID` 는 동기화된 데이터를 보낸 앱을 가리킵니다 [1]. 블로그 글에서는 ZSOURCE의 OS 빌드 칸에 iOS 버전이 있고 `ZDEVICEID` 에 GUID가 들어 있는 행이 필자의 iPhone에서 온 기록이었다고 설명해서 [1], 다른 기기에서 동기화한 기록은 그 기기를 가리키는 값을 달고 들어올 수 있습니다(macOS 10.13·iOS 11 기준). 이 Mac 자신의 기록에서 `ZDEVICEID` 가 늘 하드웨어 UUID와 같은지는 확인하지 못해서, 값을 보고서에 쓸 때는 [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../../system-account/computer-name-hardware.md)의 하드웨어 UUID와 직접 맞춰 봅니다.

### ZSTRUCTUREDMETADATA

스트림마다 쓰는 칸이 다르고, 이번에 확인한 칸은 아래와 같습니다.

| 칸 | 쓰는 스트림 | 출처 |
|---|---|---|
| `Z_DKAPPLICATIONMETADATAKEY__LAUNCHREASON` | `/app/inFocus` | [3] |
| `Z_DKAPPLICATIONMETADATAKEY__EXTENSIONCONTAININGBUNDLEIDENTIFIER` | `/app/inFocus` | [3] |
| `Z_DKAPPLICATIONMETADATAKEY__EXTENSIONHOSTIDENTIFIER` | `/app/inFocus` | [3] |
| `Z_DKAPPLICATIONACTIVITYMETADATAKEY__ACTIVITYTYPE` | `/app/activity` | [1] |
| `Z_DKAPPLICATIONACTIVITYMETADATAKEY__TITLE` | `/app/activity` | [1] |
| `ZMETADATAHASH` | APOLLO가 `/app/usage`·`/app/inFocus` 에서 함께 뽑음 | [2][3] |

### ZCUSTOMMETADATA

`/app/usage` 모듈은 이 표의 `ZNAME` 과 `ZDOUBLEVALUE` 를 "NAME", "VALUE" 로 뽑지만 [2], 어떤 이름과 값이 들어가는지 설명한 자료는 찾지 못했습니다.

## 스트림 이름

스트림 (Stream)은 기록의 종류이고, `ZSTREAMNAME` 칸에 `/app/inFocus` 같은 경로 모양으로 들어 있습니다. 블로그 글이 macOS 10.13에서 본 스트림과, 그 뒤 APOLLO 모듈에서 macOS 쪽으로 확인한 스트림을 합치면 아래와 같습니다.

| 스트림 | 나오는 버전 | 다루는 페이지 |
|---|---|---|
| `/app/inFocus` | macOS 10.13 [1], APOLLO 목록 10.13~10.16 [3] | [앱 사용 기록](app-usage.md) |
| `/app/usage` | APOLLO 목록 10.14~10.16 [2] | [앱 사용 기록](app-usage.md) |
| `/app/activity` | macOS 10.13 [1] | [앱 사용 기록](app-usage.md) |
| `/safari/history` | macOS 10.13 [1] | [앱 사용 기록](app-usage.md) |
| `/app/intents` | macOS 10.13 [1] | 이 페이지 목록만 |
| `/activity/level` | macOS 10.13 [1] | 이 페이지 목록만 |
| `/display/isBacklit` | macOS 10.13 [1], APOLLO 목록 10.13~10.16 [4] | [화면·잠금 상태](device-state.md) |
| `/device/isPluggedIn` | macOS 10.13 [1] | [화면·잠금 상태](device-state.md) |
| `/device/isLocked` | APOLLO 목록 10.15~10.16 [5] | [화면·잠금 상태](device-state.md) |

10.13·iOS 11 기준 블로그 글에는 iOS에만 있던 스트림도 따로 적혀 있고(`/app/install`, `/audio/outputRoute`, `/device/batteryPercentage`, `/device/isLocked`, `/display/orientation`, `/inferred/motion`, `/media/nowPlaying`, `/portrait/entity`, `/portrait/topic`, `/search/feedback`, `/user/isFirstBacklightOnAfterWakeup`, `/widgets/viewed`) [1], 그중 `/device/isLocked` 는 APOLLO 목록에서 macOS 10.15부터 나타납니다 [5]. 어느 스트림이 시스템 쪽 DB에, 어느 스트림이 사용자 쪽 DB에 들어가는지는 확인하지 못해서 두 DB를 모두 열어 봅니다.

### APOLLO 버전 목록 읽는 법

APOLLO 모듈의 `VERSIONS=` 줄은 iOS 번호(11·12·13·14)와 macOS 번호(10.13~10.16)를 한 줄에 섞어 씁니다 [2]~[5]. 목록 끝의 "14" 는 앞의 11·12·13에 이어지는 iOS 14로 읽히고, macOS 14를 뜻한다는 말은 모듈에 없습니다. 그래서 APOLLO로 확인되는 macOS 범위는 목록에 적힌 10.16까지이고, 그 뒤 버전은 검체에서 직접 확인해야 합니다.

## 시각 해석

`ZSTARTDATE`, `ZENDDATE`, `ZCREATIONDATE` 는 맥 절대 시각 (Mac Absolute Time), 곧 2001-01-01 00:00:00 UTC부터 센 초이고, 유닉스 시각으로 바꾸려면 978307200을 더합니다 [1][2]. 저장된 값은 UTC 기준이고, 기록 당시 현지 시각은 `ZSECONDSFROMGMT` 를 더해 구합니다 [1][2]. 시각 형식을 더 자세히 보려면 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)을 봅니다.

한 행에는 사건 구간의 시작·끝과 DB에 쓴 시각(`ZCREATIONDATE`)이 따로 들어 있으니, 타임라인에 올릴 때는 셋을 섞지 않고 어느 칸에서 온 시각인지 함께 적습니다.

## 직접 분석해 보기

### 값 한 개를 손으로 풀어 보기

아래 숫자는 설명하려고 만든 예시이고, 실제 검체에서 나온 값이 아닙니다.

| 칸 | 저장 값(예시) | 풀이 |
|---|---|---|
| `ZSTARTDATE` | 600000000 | 600000000 + 978307200 = 1578307200 → 2020-01-06 10:40:00 UTC |
| `ZENDDATE` | 600000750 | 2020-01-06 10:52:30 UTC, 사용 시간 750초(12분 30초) |
| `ZSECONDSFROMGMT` | 32400 | 32400 ÷ 3600 = 9시간, 현지 시각 2020-01-06 19:40:00 |

행을 페이지 단위로 헥스에서 따라가는 방법은 SQLite 형식 쪽 이야기라서 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

### SQL로 한 번

원본이 아닌 사본에서 `sqlite3` 같은 공개 도구로 열고, APOLLO 모듈과 같은 방식으로 표를 붙입니다. 아래 쿼리는 이 페이지의 칸 이름만으로 짠 예시입니다.

```sql
SELECT
  datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS start_utc,
  datetime(ZOBJECT.ZENDDATE   + 978307200, 'unixepoch') AS end_utc,
  ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE                 AS seconds,
  ZOBJECT.ZSTREAMNAME,
  ZOBJECT.ZVALUESTRING,
  ZOBJECT.ZVALUEINTEGER,
  ZOBJECT.ZSECONDSFROMGMT / 3600                        AS gmt_offset_hours,
  datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS written_utc,
  ZSOURCE.ZDEVICEID,
  ZOBJECT.ZUUID,
  ZOBJECT.Z_PK
FROM ZOBJECT
LEFT JOIN ZSTRUCTUREDMETADATA
  ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
LEFT JOIN ZSOURCE
  ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
ORDER BY ZOBJECT.ZSTARTDATE;
```

먼저 `SELECT DISTINCT ZSTREAMNAME FROM ZOBJECT;` 로 그 검체에 어떤 스트림이 있는지 본 뒤 `WHERE ZOBJECT.ZSTREAMNAME = '/app/inFocus'` 처럼 좁혀 가면, 버전 차이로 스트림이 없어서 결과가 빈 경우와 기록 자체가 없는 경우를 나눠 볼 수 있습니다. 스트림별로 다듬은 쿼리는 APOLLO 저장소에 `knowledge_` 로 시작하는 모듈 파일로 공개되어 있습니다.

## 함정과 한계

표 구조와 칸 이름은 블로그 글의 10.13 설명과 APOLLO 모듈 SQL로만 확인했고, APOLLO 목록이 가리키는 macOS 범위는 10.16까지입니다. 그 뒤 버전에서 같은 칸과 연결 표가 그대로 있는지는 검체의 표 목록으로 먼저 확인하고, 숫자 붙은 연결 표(`Z_4EVENT` 등)는 특히 이름이 다를 수 있다고 보고 씁니다.

`ZDEVICEID` 에 APOLLO가 붙인 "HARDWARE UUID" 라는 이름은 도구의 표시일 뿐이라서 그대로 옮겨 적지 않고, 다른 기록과 맞춰 본 결과만 씁니다. `ZDEVICEID` 가 여러 값으로 나오면 다른 기기에서 동기화한 기록이 섞였을 수 있으니, 이 Mac에서 일어난 일로 쓰기 전에 기기별로 나눠 봅니다. 두 DB 중 한쪽만 보면 어느 쪽에 들어가는지 모르는 스트림을 놓칠 수 있습니다.

## 참고 문헌

1. Sarah Edwards, "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (mac4n6.com, 2018-08-05) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. APOLLO 모듈 knowledge_app_usage.txt — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_app_usage.txt
3. APOLLO 모듈 knowledge_app_inFocus.txt — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_app_inFocus.txt
4. APOLLO 모듈 knowledge_device_is_backlit.txt — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_device_is_backlit.txt
5. APOLLO 모듈 knowledge_device_locked.txt — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_device_locked.txt
