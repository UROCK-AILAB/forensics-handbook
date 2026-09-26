---
title: "앱 사용 기록"
parent: "KnowledgeC"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 350
---

# 앱 사용 기록 (App Usage)

knowledgeC.db 의 /app/inFocus 스트림은 어떤 앱이 언제부터 언제까지 앞 화면에 있었는지를 번들 ID 와 시각 구간으로 남기고, /app/usage 스트림은 앱 사용 사건을 남깁니다. 표와 열의 기본 구조는 [표와 스트림 구조](structure.md) 페이지에 있고, 이 페이지는 앱 스트림만 다룹니다.

## 무엇을 기록하나

/app/inFocus 는 앱이 앞 화면(포커스, focus) 상태로 바뀐 사건을 적는 스트림이고, 번들 ID 와 바뀐 이유가 함께 들어갑니다 [6]. ZVALUESTRING 에 번들 ID 가 들어가고, ZSTARTDATE 부터 ZENDDATE 까지가 앞 화면에 있던 구간이며, 두 값의 차이가 사용한 초입니다 [3].

/app/inFocus 행에는 ZSTRUCTUREDMETADATA 표를 통해 부가 정보가 붙습니다 [3].

| 열 | 뜻 |
|---|---|
| `Z_DKAPPLICATIONMETADATAKEY__LAUNCHREASON` | 실행 이유 |
| `Z_DKAPPLICATIONMETADATAKEY__EXTENSIONCONTAININGBUNDLEIDENTIFIER` | 확장 기능이 들어 있는 앱의 번들 ID |
| `Z_DKAPPLICATIONMETADATAKEY__EXTENSIONHOSTIDENTIFIER` | 확장 기능을 띄운 쪽(호스트)의 ID |

실행 이유 열에 어떤 값이 오는지는 공개된 자료가 없어서, 값을 볼 때는 그대로 옮겨 적고 뜻을 짐작해 붙이지 않습니다.

/app/usage 는 앱 사용 사건을 적는 스트림입니다 [6]. /app/usage 를 읽을 때는 ZOBJECT 에 ZSOURCE 의 ZDEVICEID(기기 ID)를 붙이고, 그 밖에 Z_4EVENT 표(`ZOBJECT.Z_PK = Z_4EVENT.Z_11EVENT`)와 ZCUSTOMMETADATA 표(`Z_4EVENT.Z_4CUSTOMMETADATA = ZCUSTOMMETADATA.Z_PK`)를 더 이어 ZCUSTOMMETADATA 의 ZNAME·ZDOUBLEVALUE 열을 함께 봅니다 [4]. 기기 ID 열이 있어서 한 DB 안에 기기가 여럿 나오는지 구분할 때 쓸 수 있고, 식별자 종류는 [기기 식별자](../../../01-foundations/value-decoding/device-identifiers.md) 페이지에 정리했습니다. Z_4EVENT·Z_11EVENT 같은 표·열 이름의 숫자 부분은 iOS 버전에 따라 달라질 수 있어서, 표 이름은 실제 DB 에서 `.tables` 로 먼저 확인합니다. /app/inFocus 와 /app/usage 가 각각 무엇을 더 담는지는 실제 데이터로 확인해야 합니다.

/app/install 은 iOS 에 있던 설치 기록 스트림이고 [1], 설치 이력은 [설치된 앱](../installed-apps.md) 페이지에서 함께 다룹니다.

## 위치와 버전별 차이

앱 기록은 iOS 16 에서 크게 바뀝니다. /app/inFocus 는 iOS 16 부터 knowledgeC 대신 바이옴 (Biome) 의 `/private/var/db/biome/streams/restricted/_DKEvent.App.inFocus` 폴더에 있는 바이너리 파일에 남고, 같은 버전에서 설치 기록도 knowledgeC 에서 보이지 않게 되었습니다 [2]. iOS 17 이후에는 바이옴 ScreenTime.AppUsage 스트림에 SEGB 시각, 번들 ID, 이벤트가 남고 보관 기간은 28 일입니다 [5].

| iOS | /app/inFocus | /app/usage | /app/install |
|---|---|---|---|
| 11~13 | knowledgeC. APOLLO 모듈 대상 버전 (iOS 11·12·13) [3] | knowledgeC. APOLLO 모듈 대상 버전 (iOS 12·13) [4] | knowledgeC 에 있음 [1] |
| 14~15 | 열 구성은 실제 데이터로 확인 | 공개 자료 없음 | 공개 자료 없음 |
| 16 | 바이옴 _DKEvent.App.inFocus 로 옮겨 감 [2] | knowledgeC 에 계속 남는지 실제 데이터로 확인 | knowledgeC 에서 사라짐 [2] |
| 17 이후 | 바이옴 ScreenTime.AppUsage 스트림 함께 확인 [5] | 공개 자료 없음 | 공개 자료 없음 |

바이옴 쪽 경로와 파일 읽는 법은 [바이옴](../biome/index.md) 허브에 있습니다.

로컬 백업에는 knowledgeC.db 가 없지만(허브 참고), 앱 사용과 이름이 닿는 설정 키와 영역은 보입니다. `HomeDomain :: Library/Preferences/com.apple.appstored.plist` 에 `AppUsageBiomeStartDate`, `AppUsageNextPostTargetDate` 키(둘 다 datetime 형)가 있고, 백업 영역 목록에 `AppDomain-com.apple.ScreenTimeUnlock`, `AppDomain-com.apple.ScreenTimeWidgetApplication`, `AppDomainGroup-group.com.apple.ScreenTime` 이 있습니다. 이 키의 뜻과, 이 영역에 앱 사용 기록이 들어 있는지는 공개된 분석 자료가 없습니다. 화면 사용 시간 기능의 기록은 [화면 사용 시간](../screen-time.md) 페이지에서 다룹니다.

## 구조

/app/inFocus 는 ZOBJECT 한 행이 앞 화면 구간 하나이고, 부가 정보는 ZSTRUCTUREDMETADATA 에서 가져옵니다. 아래 조회문은 APOLLO 모듈의 연결 방식을 본떠 줄인 예시입니다 [3].

```sql
SELECT
  DATETIME(ZOBJECT.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS START_UTC,
  DATETIME(ZOBJECT.ZENDDATE + 978307200, 'UNIXEPOCH')   AS END_UTC,
  ZOBJECT.ZVALUESTRING                                  AS BUNDLE_ID,
  ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE                 AS USAGE_SECONDS,
  ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONMETADATAKEY__LAUNCHREASON AS LAUNCH_REASON,
  ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONMETADATAKEY__EXTENSIONCONTAININGBUNDLEIDENTIFIER AS EXT_CONTAINING_BUNDLE,
  ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONMETADATAKEY__EXTENSIONHOSTIDENTIFIER AS EXT_HOST,
  ZOBJECT.ZSECONDSFROMGMT / 3600                        AS GMT_OFFSET
FROM ZOBJECT
LEFT JOIN ZSTRUCTUREDMETADATA ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
LEFT JOIN ZSOURCE ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
WHERE ZOBJECT.ZSTREAMNAME = '/app/inFocus'
ORDER BY ZOBJECT.ZSTARTDATE;
```

/app/usage 는 표 연결 조건이 더 많아서 손으로 새로 짜기보다 APOLLO 의 knowledge_app_usage 모듈 원문을 열어 조건을 그대로 따라가는 편이 낫습니다 [4].

## 증거로서 의미

/app/inFocus 행 하나로는 "이 UTC 구간에 이 번들 ID 의 앱이 앞 화면 상태로 기록되어 있다" 는 사실을 알 수 있고, 구간 길이로 그 앱이 앞 화면에 머문 초를 셀 수 있습니다. 부가 정보 열이 채워져 있으면 실행 이유와, 확장 기능으로 뜬 경우 어느 앱의 확장이었는지도 함께 볼 수 있습니다 [3].

앞 화면에 있었다는 기록은 사람이 화면을 보고 있었다거나 누가 조작했다는 뜻까지는 아니고, 앱 안에서 무엇을 했는지도 담기지 않습니다. 화면이 켜져 있었는지와 잠금이 풀려 있었는지는 [화면·잠금 상태](device-state.md) 기록과 겹쳐 보고, 그 시각에 폰을 쓴 사람이 누구인지는 [그 시각에 폰을 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 시나리오처럼 다른 증거로 따로 좁힙니다.

기록이 없다는 사실도 앱을 쓰지 않았다는 증거가 되지 못합니다. /app/inFocus 와 /app/usage 는 60 초에 30 건까지만 기록하도록 제한되어 있어서 앱을 2 초에 한 번보다 빠르게 바꾸면 일부 사건이 빠질 수 있고 [6], 보관 기간이 지난 기록은 남지 않으며, iOS 16 이후 기기에서는 기록이 아예 바이옴 쪽에 있을 수 있습니다 [2].

보고서에는 "2023-03-08 20:26:40 UTC 부터 900 초 동안 com.example.app 이 앞 화면 상태로 기록되어 있다" 처럼 기록으로 확인되는 만큼만 씁니다(시각과 번들 ID 는 설명을 위한 가상 값입니다).

## 시각 해석

구간의 시작과 끝은 Mac 절대 시각이고 UTC 기준입니다. 유닉스 시각으로 바꾸는 방법과 ZSECONDSFROMGMT 를 읽는 법은 [표와 스트림 구조](structure.md) 페이지에 있습니다. 앱 기록에서는 ZENDDATE 에서 ZSTARTDATE 를 뺀 값이 사용한 초라는 점만 더 기억하면 됩니다 [3].

## 함정과 한계

공개된 조회문과 열 설명은 iOS 11~13 과 macOS 를 대상으로 적힌 것이라서 [3][4], iOS 15 이후 데이터에 그대로 돌리면 열이 없다는 오류가 나거나 결과가 비어 나올 수 있고, 그럴 때는 도구가 틀렸다고 보기 전에 열 이름부터 확인합니다. 기록 횟수 제한 때문에 빠른 앱 전환이 빠질 수 있다는 점 [6], 그리고 iOS 16 이후 /app/usage 가 knowledgeC 에 계속 기록되는지 공개 자료로 밝혀지지 않았다는 점도 결과를 읽을 때 함께 적어 둡니다.

## 직접 분석해 보기

헥스로 시각 열을 읽는 예시는 [표와 스트림 구조](structure.md) 페이지에 있고, 앱 스트림의 값도 같은 방식으로 읽습니다. 공개 도구로는 APOLLO(mac4n6) 의 knowledge_app_inFocus, knowledge_app_usage 모듈이 있고 [3][4], 도구 결과가 위 조회문의 손 결과와 같은지 한 번 맞춰 봅니다. 번들 ID 가 가리키는 앱은 [번들 ID와 앱 그룹](../../../01-foundations/value-decoding/bundle-id-app-group.md) 페이지를 참고해 확인합니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [화면·잠금 상태](device-state.md) | 앞 화면 구간이 화면 켜짐·잠금 해제 구간 안에 들어가는지 |
| [바이옴](../biome/index.md) | iOS 16 이후 App.inFocus 와 ScreenTime.AppUsage 스트림 |
| [화면 사용 시간](../screen-time.md) | 앱별 사용 시간 합계가 비슷한 흐름인지 |
| [설치된 앱](../installed-apps.md) | 기록된 번들 ID 의 앱이 설치되어 있었는지, 지워졌는지 |
| [전원 로그](../powerlog.md) | 같은 시간대의 앱 활동 |

여러 기록을 한 시간 축에 놓는 방법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 페이지를, 조사 흐름 전체는 [어떤 앱을 언제 썼나](../../../04-scenarios/activity/app-usage.md)와 [폰 사용 시간 재구성](../../../04-scenarios/activity/usage-time.md) 시나리오를 봅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 시험 데이터 가운데 전체 파일 시스템 이미지를 골라 아래 질문을 풀어 봅니다.

1. 그 데이터의 iOS 버전을 확인하고, knowledgeC.db 에 /app/inFocus 행이 있는지, 없다면 바이옴 쪽에 해당 기록이 있는지 확인합니다.
2. /app/inFocus 에서 앞 화면에 가장 오래 머문 번들 ID 세 개와 그 합계 시간을 구합니다.
3. 같은 날 /device/isLocked 가 잠금 해제로 기록된 구간과 비교해, 잠금 해제 구간 밖에 놓인 앞 화면 기록이 있는지 찾고 이유를 생각해 봅니다.
4. 확장 기능 열이 채워진 행을 골라, 어느 앱 안에서 어떤 확장이 떴는지 정리합니다.

## 참고 문헌

1. Sarah Edwards (mac4n6), "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (2018-08) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. D20 Forensics, "iOS 16 - Now You 'C' It, Now You Don't -- Breaking Down The Biomes Part 1" (2022-09-23) — https://blog.d204n6.com/2022/09/ios-16-now-you-c-it-now-you-dont.html
3. APOLLO, modules/knowledge_app_inFocus.txt (mac4n6) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_app_inFocus.txt
4. APOLLO, modules/knowledge_app_usage.txt (mac4n6) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_app_usage.txt
5. digital-forensics.it, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
6. John Hyla (Blue Crew Forensics), "iOS Stream Names" (2025-06-03) — https://bluecrewforensics.com/2025/06/03/ios-stream-names/
