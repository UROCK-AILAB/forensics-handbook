---
title: "폰 사용 시간 재구성"
parent: "시나리오 · 행위 재구성"
nav_order: 1470
---

# 폰 사용 시간 재구성 (Usage Time)

특정 시간대에 폰 화면이 켜져 있었는지, 잠금이 풀려 있었는지, 하루에 얼마나 오래 썼는지를 기록으로 되짚는 시나리오입니다. 어떤 앱을 썼는지는 [어떤 앱을 언제 썼나 (App Usage)](app-usage.md) 에서, 누가 썼는지는 [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](user-attribution.md) 에서 다루고, 이 페이지는 "언제, 얼마나" 에 집중합니다.

## 조사 질문

사고가 난 시각에 운전자의 폰 화면이 켜져 있었는지, 근무 시간에 폰을 얼마나 오래 썼는지, 새벽 특정 시각에 폰을 집어 들었는지 같은 질문입니다. 이런 질문의 답은 화면이 켜지고 꺼진 구간, 잠금이 풀린 구간, 앞에 떠 있던 앱의 구간, 스크린 타임이 모은 한 시간 단위 합계로 나뉩니다. 하나만으로는 "쓰고 있었다" 까지 말하기 어려워서 넷을 겹쳐 보고, 겹치는 만큼만 결론에 씁니다.

## 먼저 확인할 것

**iOS 버전**이 가장 먼저입니다. iOS 16 에서 사용 기록의 상당 부분이 knowledgeC.db 에서 바이옴 (Biome) 으로 옮겨 가서, 버전에 따라 먼저 열 파일이 달라집니다.

| iOS 버전 | 사용 시간의 중심 기록 | 참고할 점 |
|---|---|---|
| iOS 12 이후 | 스크린 타임 DB 가 생깁니다 [3] | 앱별 사용 시간과 들어 올림 횟수를 한 시간 단위로 모읍니다 [3][4] |
| iOS 15 이하 | knowledgeC.db 의 `/app/inFocus`·`/display/isBacklit`·`/device/isLocked` 스트림이 중심입니다 [1][2] | 보관 기간은 약 4주입니다 [1] |
| iOS 16 이후 | 앱 초점·Safari 기록·설치 기록·기기 방향·충전 상태 등이 바이옴으로 옮겨 갔습니다 [2] | knowledgeC.db 파일은 남지만 iOS 15 보다 기록이 크게 줄고 여러 범주가 빠졌습니다 [2] |
| iOS 17 이후 | 버전별 세부 변화는 이 핸드북에서 확인하지 못했습니다 | 검체의 실제 폴더와 공개 도구의 해석을 대조합니다 |

**수집 범위**도 확인합니다. knowledgeC.db 는 물리 추출이나 탈옥 기기에서만 얻을 수 있었고 iTunes 식 백업에서는 본 적이 없다고 2018년 글의 저자가 적었으며 [1], 스크린 타임 DB 도 표준 iOS 백업에는 들어 있지 않아 전체 파일 시스템 추출이 필요하다고 Magnet 이 적었습니다 [3]. 바이옴이 로컬 백업에 들어가는지는 이 핸드북에서 확인하지 못했습니다. 손에 있는 자료가 로컬 백업뿐이라면 아래 표의 1~3번은 없을 수 있다고 보고, 필요한 추출 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 고릅니다.

**시각 기준**은 knowledgeC.db 와 바이옴 모두 Mac 절대 시각 (2001-01-01 기준) 이라서 Unix 시각으로 바꾸려면 978307200 을 더합니다 [1][2]. 스크린 타임 DB 의 시각 형식은 이번에 연 두 출처 모두 밝히지 않았습니다. 푼 값을 현지 시각으로 옮기기 전에 기기의 시간대를 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md) 에서 확인하고, 변환 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을 따릅니다.

**스크린 타임 동기화** 여부도 미리 봅니다. 스크린 타임은 기본값으로 기기 사이에 동기화되지 않지만 사용자가 켤 수 있고, 켜면 가족 공유 계정의 기기 사용 기록이 함께 보여서 손에 없는 기기의 앱 사용까지 보일 수 있습니다 [3].

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | knowledgeC.db (iOS 15 이하에서 중심) — 기기 경로 `/private/var/mobile/Library/CoreDuet/Knowledge/` [1] | `ZOBJECT` 표의 스트림별 시작·끝 시각. `/display/isBacklit` 은 화면 켜짐·꺼짐, `/device/isLocked` 는 잠금 상태, `/app/inFocus` 는 앞에 떠 있던 앱이고, `/device/isPluggedIn`·`/device/batteryPercentage` 가 충전과 배터리를 보여 줍니다 [1] | [KnowledgeC](../../02-artifacts/app-usage/knowledgec/index.md) |
| 2 | 바이옴 (iOS 16 이후) — `/private/var/mobile/Library/Biome`, `/private/var/db/biome` 아래 `streams/public`, `streams/restricted` [2] | 앱 초점 기록이 `_DKEvent.App.inFocus` 폴더에서 보인다고 보고됐습니다 (iOS 16 기준) [2]. 잠금·화면 켜짐에 해당하는 스트림 이름은 이 핸드북에서 확인하지 못했습니다 | [바이옴](../../02-artifacts/app-usage/biome/index.md), [SEGB 형식](../../01-foundations/data-formats/segb.md) |
| 3 | 스크린 타임 DB — `/private/var/mobile/Library/Application Support/com.apple.remotemanagementd/RMAdminStore-Local.sqlite` [3][4] | 앱 이름과 사용 시간(초), 기기를 들어 올린 횟수와 시각, 앱별 알림 수, 한 시간 단위 구간과 그 시작 시각 [3][4] | [화면 사용 시간](../../02-artifacts/app-usage/screen-time.md) |
| 4 | 스크린 타임 설정 — 백업의 HomeDomain `Library/Preferences/com.apple.ScreenTimeAgent.plist` | `ScreenTimeEnabled`, `SyncEnabled`, `UsageGenesisDate`, `LastViewedAllActivityDate`, `LastTimeZoneName`, `AutomaticSyncEnableOccurred` 같은 키 이름이 있습니다 (확인 범위: iOS 27.0). 각 키 값의 뜻은 문서로 확인하지 못했습니다 | [화면 사용 시간](../../02-artifacts/app-usage/screen-time.md), [설정 값](../../02-artifacts/system-account/preferences.md) |
| 5 | 앱별 데이터 사용량 — 백업의 WirelessDomain `Library/Databases/DataUsage.sqlite` | `ZPROCESS` 표에 `ZFIRSTTIMESTAMP`, `ZTIMESTAMP`, `ZBUNDLENAME`, `ZPROCNAME` 칸이, `ZLIVEUSAGE` 표에 `ZTIMESTAMP`, `ZWWANIN`, `ZWWANOUT` 칸이 있습니다 (확인 범위: iOS 27.0). 이 시각을 앱의 첫·마지막 통신 시각으로 읽어도 되는지와 시각 기준은 확인하지 못했습니다 | [앱별 데이터 사용량](../../02-artifacts/network/data-usage.md) |
| 6 | 백업을 만든 시각 — `Manifest.plist` 의 `Date`, `Info.plist` 의 `Last Backup Date` (확인 범위: iOS 27.0) | 수집 시점을 적어 두는 기준점 | [로컬 백업](../../01-foundations/backups/local-backup/index.md) |

백업에는 스크린 타임과 관련된 도메인 `AppDomainGroup-group.com.apple.ScreenTime`, `SysSharedContainerDomain-systemgroup.com.apple.DeviceActivity` 와 설정 파일 `com.apple.ScreenTimeSettingsAgent.plist` 도 보이지만 (확인 범위: iOS 27.0), 그 안에 사용 기록 DB 가 있는지는 확인하지 못했습니다.

## 분석 흐름

1. 기기의 iOS 버전, 시간대, 수집 방법을 적고 위 버전 표로 중심 기록을 고릅니다. 로컬 백업만 있다면 4~6번 기록으로 할 수 있는 말이 좁다는 점을 처음부터 보고서 초안에 적어 둡니다.
2. 조사 대상 기간이 보관 기간 안에 드는지 봅니다. knowledgeC.db 는 약 4주를 보관하고 [1], iOS 16 사례에서 바이옴 스트림 메타데이터 plist 의 `maxAge` 가 2419200초(약 28일)였습니다 [2]. 기간 밖이라면 기록이 없다는 사실이 사용하지 않았다는 뜻이 되지 않습니다.
3. iOS 15 이하라면 knowledgeC.db 의 `ZOBJECT` 표에서 화면·잠금·앱 초점 스트림을 시각 순으로 뽑습니다. `ZSTARTDATE`·`ZENDDATE` 는 활동의 시작과 끝이고 `ZCREATIONDATE` 는 DB 에 쓴 시각이라서 [1], 구간은 앞의 두 칸으로 만듭니다. 켜짐·꺼짐 같은 값이 어느 칸에 어떤 모양으로 들어가는지는 [KnowledgeC](../../02-artifacts/app-usage/knowledgec/index.md) 를 따릅니다.

   ```sql
   SELECT ZSTREAMNAME, ZVALUESTRING,
          datetime(ZSTARTDATE + 978307200, 'unixepoch')   AS start_time,
          datetime(ZENDDATE + 978307200, 'unixepoch')     AS end_time,
          datetime(ZCREATIONDATE + 978307200, 'unixepoch') AS written_time
   FROM ZOBJECT
   WHERE ZSTREAMNAME IN ('/display/isBacklit', '/device/isLocked', '/app/inFocus')
   ORDER BY ZSTARTDATE;
   ```

   SQLite 의 `datetime(..., 'unixepoch')` 는 결과를 UTC 로 내놓아서, 현지 시각은 따로 시간대를 더해 씁니다.
4. iOS 16 이후라면 바이옴의 앱 초점 스트림에서 같은 구간을 만들고, knowledgeC.db 에 남은 기록과 겹쳐 봅니다. 잠금·화면 켜짐에 해당하는 바이옴 스트림은 이름을 확인하지 못해서, 공개 도구가 붙인 이름을 그대로 믿지 말고 시험 기기에서 화면을 켜고 끄며 어느 스트림에 기록이 생기는지 대조합니다. SEGB 파일을 직접 읽는 법은 [SEGB 형식](../../01-foundations/data-formats/segb.md) 과 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 를 봅니다.
5. 화면이 켜진 구간, 잠금이 풀린 구간, 앱이 앞에 떠 있던 구간을 한 줄 위에 올려 겹치는 부분을 찾습니다. 세 구간이 겹치는 부분이 "기기를 조작하고 있었을 가능성이 높은 구간" 이고, 화면만 켜져 있던 부분은 따로 표시합니다.
6. 전체 파일 시스템 추출이 있다면 스크린 타임 DB 의 한 시간 단위 사용 시간과 들어 올림 횟수를 5번 결과와 비교합니다. 동기화가 켜져 있었다면 도구가 보여 주는 Device ID·Platform 항목 [4] 으로 이 기기의 기록만 남긴 뒤에 합계를 냅니다.
7. 충전 연결(`/device/isPluggedIn`)과 배터리 잔량(`/device/batteryPercentage`) [1], 데이터 사용량 DB 의 시각 칸을 보조 근거로 붙입니다. 데이터 사용량 DB 의 시각 뜻은 확인하지 못해서 주된 근거로 쓰지 않습니다.
8. 확정한 구간을 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올리고, 같은 시각의 통화·메시지·위치 기록과 맞춰 봅니다.

## 흔한 오판

화면 켜짐 기록을 곧바로 "폰을 쓰고 있었다" 로 옮기는 실수가 가장 흔합니다. `/display/isBacklit` 은 화면이 켜져 있었다는 것만 말하고, 사람이 화면을 보고 있었는지나 조작했는지는 말하지 않습니다. 잠금 해제 구간과 앱 초점 구간이 함께 겹칠 때만 조작 가능성을 높게 적습니다.

기록이 없는 시간을 "쓰지 않은 시간" 으로 읽는 실수도 있습니다. 보관 기간이 지났거나, 수집 방법이 해당 파일을 담지 못했거나, iOS 16 이후 기기에서 knowledgeC.db 만 보았을 수 있습니다 [1][2][3].

스크린 타임 합계를 모두 이 기기의 사용으로 적는 일도 조심합니다. 동기화가 켜져 있으면 같은 가족 공유 계정의 다른 기기 기록이 함께 보일 수 있습니다 [3].

도구가 보여 주는 항목 이름을 DB 칸 이름처럼 적는 실수도 있습니다. "First Pickup", "Number of Pickups", "Longest Session Start/End" 같은 이름은 도구 화면의 이름이지 DB 칸 이름이 아니라서 [4], 보고서에는 원래 표와 칸을 확인한 뒤에 씁니다. 도구 결과를 믿어도 되는지는 [도구 검증](../../03-techniques/reporting/tool-validation.md) 으로 따집니다.

`ZCREATIONDATE` 를 활동 시각으로 쓰는 실수도 있습니다. 이 칸은 활동 시각이 아니라 DB 에 쓴 시각이라서 [1], 활동 구간은 `ZSTARTDATE`·`ZENDDATE` 로 잡습니다.

## 보고서 문장 예

> knowledgeC.db 의 `ZOBJECT` 표에 `/display/isBacklit` 스트림 기록이 (시각, UTC) 부터 (시각, UTC) 까지 있고, 같은 구간에 `/device/isLocked` 스트림은 잠금이 풀린 상태를, `/app/inFocus` 스트림은 (번들 ID) 가 앞에 떠 있었음을 보여 줍니다. 이 기록은 해당 구간에 화면이 켜져 있고 잠금이 풀린 채 이 앱이 앞에 떠 있었다는 것까지 보여 주며, 누가 기기를 조작했는지는 보여 주지 않습니다.

> 스크린 타임 DB 에 (날짜) (시각) 시작 한 시간 구간의 기기 사용 기록이 (분) 분으로 남아 있습니다. 스크린 타임 동기화 설정은 (확인 결과) 였고, 이 수치가 이 기기만의 기록인지는 (확인 방법) 으로 가렸습니다.

## 함께 볼 페이지

- [어떤 앱을 언제 썼나 (App Usage)](app-usage.md) — 앱별 사용 구간
- [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](user-attribution.md) — 사용 구간을 사람과 잇기
- [KnowledgeC (knowledgeC.db)](../../02-artifacts/app-usage/knowledgec/index.md)
- [바이옴 (Biome)](../../02-artifacts/app-usage/biome/index.md)
- [화면 사용 시간 (Screen Time)](../../02-artifacts/app-usage/screen-time.md)
- [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. Sarah Edwards (mac4n6), "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (2018-08) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. D20 Forensics, "iOS 16 - Now You 'C' It, Now You Don't -- Breaking Down The Biomes Part 1" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-now-you-c-it-now-you-dont.html
3. Magnet Forensics, "Getting Evidence from iOS Screen Time Artifacts" — https://www.magnetforensics.com/blog/getting-evidence-from-ios-screen-time-artifacts/
4. Forensafe, "Apple Screen Time" — https://forensafe.com/blogs/apple-screen-time.html
