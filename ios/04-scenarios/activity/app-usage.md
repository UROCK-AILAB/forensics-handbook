---
title: "어떤 앱을 언제 썼나"
parent: "시나리오 · 행위 재구성"
nav_order: 1430
---

# 어떤 앱을 언제 썼나 (App Usage)

특정 앱을 언제부터 언제까지 앞 화면에 띄워 썼는지, 그 앱이 기기에 언제 설치됐고 언제 통신했는지를 기록으로 거슬러 올라가 찾는 시나리오입니다. 화면이 켜져 있었는지와 하루 사용 시간은 [폰 사용 시간 재구성 (Usage Time)](usage-time.md) 에서 다루고, 이 페이지는 "어느 앱을, 언제" 에 집중합니다.

## 조사 질문

"사고 시각에 운전자가 메신저 앱을 띄워 두었나", "이 앱을 처음 쓴 때는 언제인가", "지운 앱을 예전에 쓴 적이 있나" 같은 질문입니다. 답은 네 가지 기록에서 나오는데, 앱이 앞 화면에 있던 구간, 앱을 설치하거나 띄운 사건, 일정 구간마다 모은 사용 시간 합계, 앱이 통신한 흔적이 그것입니다. 앞의 두 가지가 "언제" 에 가장 가깝고, 합계와 통신 흔적은 그 구간을 받쳐 주는 보조 근거로 씁니다.

## 먼저 확인할 것

**수집 범위**를 가장 먼저 봅니다. KnowledgeC, 바이옴 (Biome), 전원 로그 (PowerLog) 는 전체 파일 시스템 추출에서만 얻을 수 있고 [14], knowledgeC.db 는 iCloud·iTunes 백업에 들어가지 않습니다 [15]. 암호를 걸지 않은 로컬 백업의 DB 목록에도 `knowledgeC.db` 와 `CurrentPowerlog.PLSQL` 이 없습니다. 그래서 로컬 백업만 있다면 앱을 쓴 시각을 직접 적은 기록은 얻기 어렵고, 남는 시각 근거는 아래 표의 앱별 데이터 사용량 DB 정도라는 점을 처음부터 알고 시작합니다.

**iOS 버전**에 따라 앞 화면 기록이 있는 곳이 다릅니다.

| iOS 버전 | 앱 사용 구간이 있는 곳 | 참고할 점 |
|---|---|---|
| iOS 11~15 | knowledgeC.db 의 `/app/inFocus` 스트림 [1][2] | 보관 기간은 약 4주입니다 [1] |
| iOS 16 | `/app/inFocus` 와 설치 기록 등이 knowledgeC.db 에서 빠지고 바이옴으로 옮겨 갔습니다 [3] | 바이옴 파일은 SEGB v1 형식입니다 [16] |
| iOS 17~26 | 바이옴, 같은 위치 [17] | SEGB v2 형식이고 [17], `ScreenTime.AppUsage` 스트림이 보입니다 [4] |
| iOS 27 | 스트림 이름과 위치는 실제 기기에서 확인 | 실제 기기의 폴더와 공개 도구의 해석을 대조합니다 |

**시각 기준**은 knowledgeC.db 와 바이옴이 Mac 절대 시각이고, 전원 로그는 Unix 시각이지만 내부 시계 보정 값(`PLStorageOperator_EventForward_TimeOffset.system`)을 더해야 합니다 [8]. 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을 따르고, 번들 ID 를 앱 이름으로 옮기는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 을 봅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | knowledgeC.db `/app/inFocus` (iOS 15 이하) — `/private/var/mobile/Library/CoreDuet/Knowledge/knowledgeC.db` [1] | `ZOBJECT.ZVALUESTRING` 이 번들 ID 이고, `ZSTARTDATE` 와 `ZENDDATE` 의 차이가 그 앱을 앞 화면에 둔 초입니다 [2] | [KnowledgeC](../../02-artifacts/app-usage/knowledgec/index.md) |
| 2 | 바이옴 `App.InFocus` (iOS 16 이후) — `/private/var/mobile/Library/Biome/streams/restricted/` [4] | 시작 시각, 번들 ID, 동작(Background/Foreground), 보관 28일 [4]. 필드 3 의 1 을 Foreground, 0 을 Background 로 보는 해석이 있습니다 [5] | [바이옴](../../02-artifacts/app-usage/biome/index.md) |
| 3 | 바이옴 `AppLaunch` (iOS 16) | 앱을 띄운 경로(idleTimer, homescreen, appswitcher, spotlight 등)와 앱 정보, 보관 28일 [6] | [바이옴](../../02-artifacts/app-usage/biome/index.md) |
| 4 | 바이옴 `App.Install` — 같은 폴더 [4] | Timestamp, Time End, Time Write, 번들 ID, 번들 정보, 앱 정보, Action GUID, 보관 28일 [4] | [설치된 앱](../../02-artifacts/app-usage/installed-apps.md) |
| 5 | 바이옴 `ScreenTime.AppUsage` — 같은 폴더 [4] | 번들 ID 와 이벤트, 보관 28일 [4] | [화면 사용 시간](../../02-artifacts/app-usage/screen-time.md) |
| 6 | 화면 사용 시간 DB — `/private/var/mobile/Library/Application Support/com.apple.remotemanagementd/RMAdminStore-Local.sqlite` 의 `ZUSAGETIMEDITEM`·`ZUSAGECOUNTEDITEM` 표 [10] | 앱별 사용 시간 합계. 가족 공유로 묶인 다른 기기의 앱 사용도 보일 수 있습니다 [11] | [화면 사용 시간](../../02-artifacts/app-usage/screen-time.md) |
| 7 | 전원 로그 `PLAppTimeService_Aggregate_AppRunTime` [8] | 앱별 앞 화면·백그라운드 실행 시간을 표본 구간 단위로 모은 값이라서 한 번 한 번의 실행 시각은 아닙니다 [8] | [전원 로그](../../02-artifacts/app-usage/powerlog.md) |
| 8 | 앱별 데이터 사용량 — 백업 WirelessDomain `Library/Databases/DataUsage.sqlite` | `ZPROCESS` 의 `ZFIRSTTIMESTAMP` 는 그 프로세스를 처음 기록한 때, `ZTIMESTAMP` 는 가장 최근 활동으로 보입니다 [13] | [앱별 데이터 사용량](../../02-artifacts/network/data-usage.md) |
| 9 | 백업에서 보이는 앱 상태 — HomeDomain `Library/FrontBoard/applicationState.db`, `Library/SpringBoard/IconState.plist`, 백업 `Info.plist` 의 `Installed Applications` 키 | 수집 시점에 어떤 앱이 있었고 홈 화면 어디에 놓였는지 | [설치된 앱](../../02-artifacts/app-usage/installed-apps.md) |

iOS 16 에서 앱을 띄운 경로는 `com.apple.SpringBoard.transitionReason.homescreen`, `…externalrequest`, `…appswitcher`, `…spotlight` 같은 값으로 남습니다 [3]. 사용자가 홈 화면에서 직접 눌렀는지, 다른 앱의 요청으로 열렸는지를 가르는 데 쓸 수 있지만, 값 전체 목록은 실제 데이터로 확인해야 합니다.

암호 없는 로컬 백업에는 이 밖에도 앱 사용과 이름이 닿아 있는 설정 파일이 보입니다. HomeDomain `Library/Preferences/com.apple.ScreenTimeAgent.plist` 에 `ScreenTimeEnabled`, `UsageGenesisDate`, `LastTimeZoneName` 키가, `com.apple.appstored.plist` 에 `AppUsageBiomeStartDate`, `AppUsageLaunchesIntervalStartDate` 같은 날짜 키가, `com.apple.mt.lastLaunch.plist` 의 `launches` 아래에 번들 ID 이름의 키가 있습니다. 각 값의 뜻이 정해져 있지 않아서, 앱을 쓴 시각의 근거로 쓰기 전에 시험 기기에서 앱을 띄우고 값이 어떻게 바뀌는지 먼저 대조합니다.

## 분석 흐름

1. iOS 버전, 시간대, 수집 방법을 적고 위 버전 표로 앞 화면 기록이 있는 곳을 고릅니다. 조사 대상 앱의 번들 ID 를 백업 `Info.plist` 의 `Installed Applications` 나 `AppDomain-` 로 시작하는 도메인 이름에서 확인합니다.
2. 조사 기간이 보관 기간 안에 드는지 봅니다. knowledgeC.db 는 약 4주 [1], 바이옴 `App.InFocus`·`App.Install`·`ScreenTime.AppUsage` 는 28일입니다 [4]. 기간 밖의 빈칸은 쓰지 않았다는 뜻이 되지 않습니다.
3. iOS 15 이하라면 knowledgeC.db 에서 그 번들 ID 의 `/app/inFocus` 구간을 뽑습니다.

   ```sql
   SELECT ZVALUESTRING AS bundle_id,
          datetime(ZSTARTDATE + 978307200, 'unixepoch') AS start_utc,
          datetime(ZENDDATE + 978307200, 'unixepoch')   AS end_utc,
          ZENDDATE - ZSTARTDATE                         AS seconds
   FROM ZOBJECT
   WHERE ZSTREAMNAME = '/app/inFocus'
     AND ZVALUESTRING = 'com.example.app'
   ORDER BY ZSTARTDATE;
   ```

   `com.example.app` 은 자리 표시용 번들 ID 입니다.
4. iOS 16 이후라면 바이옴 `App.InFocus` 에서 Foreground·Background 전환을 시각 순으로 늘어놓아 구간을 만듭니다. SEGB 파일을 직접 읽는 법은 [SEGB 형식](../../01-foundations/data-formats/segb.md) 과 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 를 봅니다. `remote` 폴더의 기록은 같은 Apple 계정의 다른 기기에서 온 것이라 [5][12] 빼고 봅니다.
5. `AppLaunch` 의 전환 이유와 `App.Install` 의 시각을 붙여 "언제 설치했고, 어떤 경로로 띄웠는지" 를 구간 옆에 적습니다 [4][6].
6. 화면 사용 시간 DB 와 전원 로그의 합계를 4번 구간의 합과 비교합니다. 합계가 구간보다 크게 많다면 가족 공유 기기의 기록이 섞였는지 [11], 스트림 기록 수 제한으로 빠른 전환이 빠졌는지 [7] 를 따집니다.
7. 앱별 데이터 사용량 DB 의 `ZPROCESS` 에서 번들 이름으로 행을 찾아 처음·마지막 기록 시각을 붙입니다. `ZLIVEUSAGE.ZHASPROCESS` 는 `ZPROCESS.Z_PK` 와 이어지고, iLEAPP 는 `ZKIND` 가 257 인 행을 뺍니다 [9]. `ZKIND` 값의 뜻은 문서화되지 않았습니다 [9]. 시각은 Mac 절대 시각입니다 [9].
8. 확정한 구간을 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올리고, 같은 시각의 메시지·통화·위치 기록과 맞춰 봅니다. 지운 앱이라면 [설치된 앱](../../02-artifacts/app-usage/installed-apps.md) 과 [앱 스토어 기록](../../02-artifacts/app-usage/app-store.md) 에서 설치·삭제 흔적을 따로 찾습니다.

## 흔한 오판

앞 화면 기록을 "사람이 그 앱을 조작했다" 로 옮기는 실수가 가장 흔합니다. `/app/inFocus` 와 `App.InFocus` 는 그 앱이 앞 화면에 있었다는 것까지만 말해서, 화면 켜짐·잠금 해제 구간과 겹쳐 봐야 조작 가능성을 적을 수 있습니다. 그 방법은 [폰 사용 시간 재구성](usage-time.md) 을 따릅니다.

도구가 보여 주는 Foreground·Background 표시를 원본 값처럼 적는 일도 조심합니다. 필드 3 의 1·0 을 Foreground·Background 로 보는 것은 해석이라서 [5], 보고서에는 원래 값과 해석을 나눠 적습니다.

전원 로그의 앱 실행 시간을 실행 시각으로 쓰는 실수도 있습니다. `PLAppTimeService_Aggregate_AppRunTime` 은 표본 구간마다 모은 값이라서 [8], 그 구간 안 어느 때에 앱을 썼는지는 나와 있지 않습니다.

데이터 사용량 DB 에 행이 없다고 앱을 쓰지 않았다고 읽는 일도 있습니다. `ZLIVEUSAGE` 에는 셀룰러 열 `ZWWANIN`·`ZWWANOUT` 만 있고 Wi-Fi 열 `ZWIFIIN`·`ZWIFIOUT` 이 없을 수 있어서, iLEAPP 도 Wi-Fi 열이 없을 때는 셀룰러 열만 읽는 쿼리를 씁니다 [9]. 거꾸로 이 DB 는 백업에 들어가 오래된 기록이 남기도 해서, 2013년 기록이 남은 기기도 있습니다 [13].

## 보고서 문장 예

> 바이옴 `App.InFocus` 스트림의 `local` 폴더에 (번들 ID) 가 (시각, UTC) 에 앞 화면으로 전환되고 (시각, UTC) 에 뒤로 전환된 기록이 있습니다. 이 기록은 해당 구간에 이 앱이 이 기기의 앞 화면에 있었다는 것까지 보여 주며, 누가 조작했는지와 앱 안에서 무엇을 했는지는 보여 주지 않습니다.

> `DataUsage.sqlite` 의 `ZPROCESS` 표에 (번들 이름) 행이 있고, `ZFIRSTTIMESTAMP` 는 (시각, UTC), `ZTIMESTAMP` 는 (시각, UTC) 입니다. 두 열의 뜻은 공개 자료의 해석을 따른 것이며, 이 앱의 통신 기록이 이 DB 에 이 기간에 걸쳐 남아 있다는 뜻으로만 씁니다.

## 함께 볼 페이지

- [폰 사용 시간 재구성 (Usage Time)](usage-time.md) — 화면·잠금 구간
- [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](user-attribution.md)
- [KnowledgeC (knowledgeC.db)](../../02-artifacts/app-usage/knowledgec/index.md)
- [바이옴 (Biome)](../../02-artifacts/app-usage/biome/index.md)
- [설치된 앱 (Installed Apps·applicationState.db)](../../02-artifacts/app-usage/installed-apps.md)
- [전원 로그 (PowerLog)](../../02-artifacts/app-usage/powerlog.md)
- [앱 화면 스냅숏 (App Snapshots·KTX)](../../02-artifacts/app-usage/app-snapshots.md) — 앱을 뒤로 보낼 때 남은 마지막 화면
- [앱별 데이터 사용량 (DataUsage.sqlite)](../../02-artifacts/network/data-usage.md)

## 참고 문헌

1. Sarah Edwards (mac4n6), "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (2018-08) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. APOLLO, `modules/knowledge_app_inFocus.txt` (mac4n6) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_app_inFocus.txt
3. D20 Forensics, "iOS 16 - Now You 'C' It, Now You Don't -- Breaking Down The Biomes Part 1" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-now-you-c-it-now-you-dont.html
4. digital-forensics.it, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
5. iLEAPP, `scripts/artifacts/biomeInfocus.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/biomeInfocus.py
6. D20 Forensics, "iOS 16 Breaking Down the Biomes Part 2 - AppInstalls, AppLaunch, & AppIntents" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-breaking-down-biomes-part-2.html
7. John Hyla (Blue Crew Forensics), "iOS Stream Names" (2025-06-03) — https://bluecrewforensics.com/2025/06/03/ios-stream-names/
8. iLEAPP, `scripts/artifacts/powerlog.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/powerlog.py
9. iLEAPP, `scripts/artifacts/DataUsage.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/DataUsage.py
10. Forensafe, "Apple Screen Time" — https://forensafe.com/blogs/apple-screen-time.html
11. Magnet Forensics, "Getting Evidence from iOS Screen Time Artifacts" — https://www.magnetforensics.com/blog/getting-evidence-from-ios-screen-time-artifacts/
12. Magnet Forensics, "Bringing it Back With Biome Data" — https://www.magnetforensics.com/blog/bringing-it-back-with-biome-data/
13. Sarah Edwards (mac4n6), "Network and Application Usage using netusage.sqlite & DataUsage.sqlite iOS Databases" (2019-01) — http://www.mac4n6.com/blog/2019/1/6/network-and-application-usage-using-netusagesqlite-amp-datausagesqlite-ios-databases
14. digital-forensics.it, "Has the user ever used the XYZ application? aka traces of application execution on mobile devices" (2023-12) — https://blog.digital-forensics.it/2023/12/has-user-ever-used-xyz-application-aka.html
15. Belkasoft, "KnowledgeC Database Forensics: A Comprehensive Guide" — https://belkasoft.com/knowledgec-database-forensics-with-belkasoft
16. Be-binary 4n6, "Beyond the C — SEGB and Biome Forensics with crush" (2026-05) — https://bebinary4n6.blogspot.com/2026/05/beyond-c-segb-and-biome-forensics-with.html
17. digital-forensics.it, "84 Streams Later: Exploring the Evolution of Apple Biome in iOS" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-exploring-evolution-of.html
