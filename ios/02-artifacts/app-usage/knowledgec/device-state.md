---
title: "화면·잠금 상태"
parent: "KnowledgeC"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 360
---

# 화면·잠금 상태 (Display·Device Lock)

knowledgeC.db 의 /device/isLocked 와 /display/isBacklit 스트림은 기기가 잠겨 있던 구간과 화면이 켜져 있던 구간을 1 과 0 으로 남깁니다. 표와 열의 기본 구조는 [표와 스트림 구조](structure.md) 페이지에 있고, 이 페이지는 기기 상태 스트림만 다룹니다.

## 무엇을 기록하나

두 스트림 모두 ZOBJECT 의 ZVALUEINTEGER 열에 상태를 적고, ZSTARTDATE 부터 ZENDDATE 까지가 그 상태가 이어진 구간입니다. /device/isLocked 는 0 이 잠금 해제이고 1 이 잠김이며 [2][4], /display/isBacklit 는 1 이 켜짐이고 0 이 꺼짐입니다 [2]. /device/isLocked 는 화면이 잠겼는지를, /display/isBacklit 는 백라이트 수준을 적는 스트림입니다 [6].

같은 분류에 속한 스트림으로는 충전기가 꽂혔는지를 적는 /device/isPluggedIn [6], 기기 방향을 적는 /display/orientation [1], 그리고 /device/batteryPercentage [1] 가 있습니다. /device/batteryPercentage 값의 형태는 공개된 자료가 없습니다.

APOLLO 의 knowledge_device_locked 모듈은 `ZSTREAMNAME LIKE "/device/isLocked"` 로 행을 거르고, 시작·끝 시각, 잠금 상태, 사용한 초와 분, 기기 ID, 요일, GMT 차이, 행 생성 시각, UUID 를 뽑습니다 [4]. 잠금 구간의 길이는 ZENDDATE 에서 ZSTARTDATE 를 뺀 값입니다 [4].

## 위치와 버전별 차이

APOLLO 의 knowledge_device_locked 모듈이 대상으로 적은 버전은 iOS 11·12·13 과 macOS 10.15·10.16·14 입니다 [4]. iOS 16 에서는 충전기 연결 상태와 기기 방향이 knowledgeC 에서 보이지 않게 되었습니다 [3]. /device/isLocked 와 /display/isBacklit 가 iOS 16 이후에도 knowledgeC 에 남는지는 실제 데이터로 확인해야 합니다. iOS 17 이후에는 바이옴 (Biome) 에 대응하는 스트림이 있고 보관 기간은 28 일입니다 [5].

| knowledgeC 스트림 | 값 | iOS 16 에서 | iOS 17 이후 바이옴 대응 [5] |
|---|---|---|---|
| `/device/isLocked` | 0 해제, 1 잠김 [2][4] | 실제 데이터로 확인 | Device.ScreenLocked (0 해제, 1 잠김) |
| `/display/isBacklit` | 1 켜짐, 0 꺼짐 [2] | 실제 데이터로 확인 | Device.Display.Backlight (0/1) |
| `/device/isPluggedIn` | 충전기 연결 여부 [6] | knowledgeC 에서 빠짐 [3] | Device.Power.PluggedIn (0 안 꽂힘, 1 꽂힘, 어댑터 종류 필드도 있음) |
| `/display/orientation` | 기기 방향 [1] | knowledgeC 에서 빠짐 [3] | 공개 자료 없음 |
| `/device/batteryPercentage` | 공개 자료 없음 | 실제 데이터로 확인 | 공개 자료 없음 |

유선이든 무선이든 충전할 때 기록이 생기므로 "isCharging" 이 더 맞는 이름일 수 있다는 해석이 있습니다 [5]. 충전 중이었다는 뜻으로 읽을지 꽂혀 있었다는 뜻으로 읽을지는 실제 데이터에서 다른 기록과 맞춰 보고 정합니다. 바이옴 쪽 경로와 파일 읽는 법은 [바이옴](../biome/index.md) 허브에 있습니다.

로컬 백업의 `Manifest.plist` 에는 `WasPasscodeSet` 키가 있습니다. 잠금과 이름이 닿지만 knowledgeC 기록과 직접 관계는 없고, 값의 해석도 공개된 자료가 없습니다. 암호 설정 흔적은 [암호와 Face ID 설정 흔적](../../system-account/passcode-biometrics.md) 페이지에서, 백업 파일 구성은 [로컬 백업](../../../01-foundations/backups/local-backup/index.md) 페이지에서 다룹니다.

## 구조

아래 조회문은 APOLLO 모듈의 방식을 본떠 줄인 예시입니다 [4]. 스트림 이름만 `/display/isBacklit` 로 바꾸면 화면 켜짐 구간도 같은 방식으로 뽑을 수 있고, 그때는 CASE 절을 1 이 켜짐, 0 이 꺼짐으로 바꿔 씁니다 [2].

```sql
SELECT
  DATETIME(ZOBJECT.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS START_UTC,
  DATETIME(ZOBJECT.ZENDDATE + 978307200, 'UNIXEPOCH')   AS END_UTC,
  CASE ZOBJECT.ZVALUEINTEGER
    WHEN 0 THEN 'unlocked'
    WHEN 1 THEN 'locked'
  END                                                   AS LOCK_STATE,
  ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE                 AS SECONDS,
  ZOBJECT.ZSECONDSFROMGMT / 3600                        AS GMT_OFFSET,
  ZSOURCE.ZDEVICEID
FROM ZOBJECT
LEFT JOIN ZSOURCE ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
WHERE ZOBJECT.ZSTREAMNAME = '/device/isLocked'
ORDER BY ZOBJECT.ZSTARTDATE;
```

## 증거로서 의미

/device/isLocked 의 0 구간으로는 "이 UTC 구간에 기기가 잠금 해제 상태로 기록되어 있다" 는 사실을 알 수 있고, /display/isBacklit 의 1 구간은 화면이 켜진 상태로 기록된 구간입니다. 두 구간이 겹치는 시간대는 기기가 사용 가능한 상태였던 때라서, [앱 사용 기록](app-usage.md)의 앞 화면 구간을 이 안에 놓아 보면 앱 기록이 실제 사용 흐름과 어긋나지 않는지 살펴볼 수 있습니다.

값이 1 과 0 뿐이라서 잠금을 누가 어떤 방법으로 풀었는지는 이 스트림에 담기지 않습니다 [2][4]. 화면이 켜진 기록 역시 사람이 화면을 보고 있었다는 뜻까지는 아니라서, 화면 켜짐을 곧 사람의 조작으로 단정하지 않습니다. 기기를 쓴 사람을 가려내는 문제는 [그 시각에 폰을 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 시나리오에서 다른 증거와 함께 다룹니다.

보고서에는 "2023-03-08 20:26:40 UTC 부터 900 초 동안 기기가 잠금 해제 상태로 기록되어 있다" 처럼 씁니다(시각은 설명을 위한 가상 값입니다).

## 시각 해석

구간의 시작과 끝은 Mac 절대 시각이고 UTC 기준입니다. 변환 방법과 ZSECONDSFROMGMT 읽는 법은 [표와 스트림 구조](structure.md) 페이지에 있습니다. 기기 상태 스트림에서는 한 행이 상태 하나가 이어진 구간이라서, 잠금 해제 구간의 끝과 다음 잠김 구간의 시작이 이어지는지를 보면 기록이 빠진 곳을 찾을 수 있습니다.

## 함정과 한계

공개된 조회문과 값 설명은 iOS 11~13 과 macOS 를 대상으로 적힌 것이고 [4], /display/isBacklit 는 자료에 따라 켜짐·꺼짐 [2] 과 "백라이트 수준" [6] 으로 설명이 다릅니다. 그래서 새 버전 기기에서는 ZVALUEINTEGER 에 0 과 1 말고 다른 값이 나오는지 먼저 세어 보고 해석합니다. iOS 16 이후 기기에서는 이 스트림들이 knowledgeC 에 없을 수 있어서, knowledgeC 에 행이 없다고 해서 그 기간에 기기를 쓰지 않았다고 판단하지 않고 바이옴 쪽을 확인합니다.

## 직접 분석해 보기

헥스로 시각 열을 읽는 예시는 [표와 스트림 구조](structure.md) 페이지에 있습니다. 공개 도구로는 APOLLO(mac4n6) 의 knowledge_device_locked 모듈이 있고 [4], 위 조회문으로 뽑은 구간 수와 합계 시간이 도구 결과와 같은지 한 번 맞춰 봅니다. 값 분포는 다음처럼 먼저 확인합니다.

```sql
SELECT ZSTREAMNAME, ZVALUEINTEGER, COUNT(*) AS CNT
FROM ZOBJECT
WHERE ZSTREAMNAME IN ('/device/isLocked', '/display/isBacklit')
GROUP BY ZSTREAMNAME, ZVALUEINTEGER;
```

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [앱 사용 기록](app-usage.md) | 앞 화면 구간이 잠금 해제·화면 켜짐 구간 안에 들어가는지 |
| [바이옴](../biome/index.md) | iOS 17 이후 Device.ScreenLocked, Device.Display.Backlight, Device.Power.PluggedIn |
| [알림 기록](../notifications.md) | 화면이 켜진 시각에 알림이 들어왔는지 |
| [전원 로그](../powerlog.md) | 같은 시간대의 화면·전원 상태 |
| [통합 로그에서 찾을 것](../../logs/unified-log-events.md) | 같은 시각 전후의 시스템 사건 |

사용 시간을 재구성하는 전체 흐름은 [폰 사용 시간 재구성](../../../04-scenarios/activity/usage-time.md) 시나리오를 봅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 시험 데이터 가운데 전체 파일 시스템 이미지를 골라 아래 질문을 풀어 봅니다.

1. 그 데이터의 iOS 버전을 확인하고, knowledgeC.db 에 /device/isLocked 와 /display/isBacklit 행이 있는지 확인합니다.
2. 하루를 골라 잠금 해제 구간의 수와 합계 시간을 구하고, 가장 긴 구간의 시작과 끝을 현지 시각으로 바꿔 적습니다.
3. 화면 켜짐 구간 가운데 잠금 해제 구간과 겹치지 않는 것을 찾아, 알림 기록 같은 다른 기록으로 설명이 되는지 봅니다.
4. 잠금 해제 구간의 끝과 다음 잠김 구간의 시작 사이에 빈틈이 있는 곳을 찾아, 전원이 꺼졌던 때인지 다른 기록으로 확인합니다.

## 참고 문헌

1. Sarah Edwards (mac4n6), "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (2018-08) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. Belkasoft, "KnowledgeC Database Forensics: A Comprehensive Guide" — https://belkasoft.com/knowledgec-database-forensics-with-belkasoft
3. D20 Forensics, "iOS 16 - Now You 'C' It, Now You Don't -- Breaking Down The Biomes Part 1" (2022-09-23) — https://blog.d204n6.com/2022/09/ios-16-now-you-c-it-now-you-dont.html
4. APOLLO, modules/knowledge_device_locked.txt (mac4n6) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_device_locked.txt
5. digital-forensics.it, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
6. John Hyla (Blue Crew Forensics), "iOS Stream Names" (2025-06-03) — https://bluecrewforensics.com/2025/06/03/ios-stream-names/
