---
title: "화면 사용 시간"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 400
---

# 화면 사용 시간 (Screen Time)

## 한 줄 요약

화면 사용 시간 (Screen Time) 은 앱별 사용 시간, 알림 수, 기기를 들어 올린 횟수를 집계 구간마다 모아 두는 iOS 기능이고, 집계 DB 에서 "이 구간에 이 앱이 이만큼 쓰였다" 는 합계를, 설정 plist 에서 기능을 켠 상태와 관련 시각 키를 읽습니다.

## 무엇을 기록하나 · 왜 생기나

화면 사용 시간은 일간·주간 보고서를 만들고, 기기 화면에서는 그중 7일치만 보여 줍니다[1]. 보고서의 바탕이 되는 기록을 iOS 12 기준으로 정리한 Magnet Forensics 글은 두 묶음을 듭니다. 한 묶음에는 앱 이름, 기기 UDID, 기기 이름, 사용자 이름(이름과 성), 계정 종류가 함께 있고, 다른 묶음에는 앱 이름, 집계 구간이 시작한 시각, 그 구간에 앱을 쓴 시간(초), 알림 수, 기기를 들어 올린 횟수 (pickups) 가 있습니다[1]. Forensafe 글은 같은 DB 에서 번들 ID, 도메인, 첫 들어 올림 시각 (First Pickup), 알림 수, 들어 올린 횟수를 보여 줍니다[2].

가족 공유로 묶인 계정들이 모두 화면 사용 시간을 켜 두면, 수집한 기기에서 다른 가족 기기의 앱 사용까지 보이고 그 자리에 없는 기기의 UDID 도 나옵니다[1]. 그래서 이 DB 에는 수집한 기기 한 대가 아니라 계정으로 이어진 여러 기기의 기록이 섞여 있을 수 있습니다.

## 위치와 버전별 차이

### 기기 안 경로

집계 DB 는 `com.apple.remotemanagementd` 폴더에 있습니다[1][2].

```
/private/var/mobile/Library/Application Support/com.apple.remotemanagementd/RMAdminStore-Local.sqlite
```

Magnet 글은 같은 폴더의 `RMAdminStore-Cloud.sqlite` 를 동기화된 기기의 기록을 담는 파일로 따로 듭니다[1].

### 버전별로 확인한 범위

| 범위 | 내용 | 출처 |
|---|---|---|
| iOS 12 | `RMAdminStore-Local.sqlite`, 동기화 기록용 `RMAdminStore-Cloud.sqlite`. 표와 칸 이름은 글에 없음 | [1] |
| 버전 밝히지 않음 | `RMAdminStore-Local.sqlite` 의 `ZUSAGETIMEDITEM`(시간 항목), `ZUSAGECOUNTEDITEM`(횟수 항목) 표 | [2] |
| iOS 17 이후 | 바이옴 (Biome) 에도 `ScreenTime.AppUsage` 스트림이 있고, SEGB 시각·번들 ID·이벤트를 담으며 보관 기간은 28일 | [3] |
| iOS 27.0 로컬 백업 | 아래 "로컬 백업에 보이는 것" 참고 | 관찰 |

iOS 15 이후 DB 의 표 구조가 바뀌었는지, DB 에 기록을 며칠 치 남기는지는 확인한 자료가 없습니다. 바이옴 스트림을 읽는 법은 [바이옴](biome/index.md) 에서 다룹니다.

### 로컬 백업에 보이는 것

관찰한 로컬 백업에는 `SysContainerDomain-com.apple.remotemanagementd` 도메인(항목 6개)이 있었지만, 관찰 메모에는 도메인 이름과 항목 수만 적혀 있고 안의 파일 이름은 없습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 그래서 백업에 `RMAdminStore-Local.sqlite` 가 들어가는지는 이 관찰로 판단할 수 없습니다. 이름에 화면 사용 시간이 들어간 도메인은 다음과 같았습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

```
AppDomain-com.apple.ScreenTimeUnlock
AppDomain-com.apple.ScreenTimeWidgetApplication
AppDomain-com.apple.internal.ScreenTimeSettingsShield
AppDomainGroup-group.com.apple.ScreenTime                  (항목 3개)
SysSharedContainerDomain-systemgroup.com.apple.DeviceActivity  (항목 3개)
AppDomainPlugin-com.apple.DiagnosticExtensions.ScreenTime
AppDomainPlugin-com.apple.FamilyControls.ActivityPickerExtension
```

설정 plist 는 값을 읽지 않고 키 이름과 형만 보았습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

| 도메인 :: 경로 | 관찰한 키 |
|---|---|
| `HomeDomain :: Library/Preferences/com.apple.ScreenTimeAgent.plist` | `ScreenTimeEnabled` (bool), `SyncEnabled` (bool), `UsageGenesisDate` (datetime), `LastViewedAllActivityDate` (datetime), `LastCheckinDate` (datetime), `LastTimeZoneName` (str), `RestrictionsMigrationVersion` (int), `AutomaticSyncEnableOccurred` (bool), `GenesisCloudMirroringImportOccurred` (bool) 등 |
| `HomeDomain :: Library/Preferences/com.apple.UsageTrackingAgent.plist` | `lastRefreshDate` (datetime), `<UUID>_Hourly`·`<UUID>_Daily`·`<UUID>_Weekly` (bool), `didResetLocalDeviceIdentifier` (bool) |
| `HomeDomain :: Library/Preferences/com.apple.FamilyControlsAgent.plist` | `DidDeleteActivityRecords` (bool), `DidSaveAuthorizationZone` (bool), `didMigrateSharingAppleIDs` (bool) 등 |
| `HomeDomain :: Library/Preferences/com.apple.ScreenTimeSettingsAgent.plist` | `ManagedChildMigrationRemediation` (bool), `TimeAllowanceClientIdentifierMigration` (bool) 등 |
| `HomeDomain :: Library/Preferences/com.apple.coreduetd.plist` | `ScreenTimeSyncDisabled` (bool) 등 |

키 이름만 보면 `UsageGenesisDate` 는 사용 기록이 시작된 시각, `ScreenTimeEnabled` 는 기능을 켰는지로 읽히지만, 어느 키의 뜻도 문서로 확인하지 못했습니다. 보고서에는 키 이름과 값을 그대로 옮기고 해석은 다른 기록과 맞춘 뒤에 붙입니다. 백업 파일을 도메인과 경로로 찾는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md), plist 를 여는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

## 구조

`RMAdminStore-Local.sqlite` 는 SQLite DB 이고, 사용 시간은 `ZUSAGETIMEDITEM` 표에, 알림 수와 들어 올린 횟수 같은 횟수는 `ZUSAGECOUNTEDITEM` 표에 있습니다[2]. 도구 화면에 나오는 "First Pickup" 같은 이름은 도구가 붙인 이름이고 실제 칸 이름은 원문에 없어서[2], 칸 이름을 쓰기 전에 검체의 스키마를 직접 확인합니다. SQLite 구조와 `-wal` 처리는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 기록이 남은 기간 안에서, 어떤 앱이 어느 집계 구간에 몇 초 쓰였는지, 그 구간에 알림이 몇 개 왔고 기기를 몇 번 들어 올렸는지를 보여 줍니다[1][2]. 같은 기록 묶음에 기기 UDID·기기 이름·사용자 이름이 함께 있어서[1], 사용 시간이 어느 기기에서 나온 것인지 가를 수 있고, 가족 공유로 이어진 다른 기기가 있었다는 사실도 보여 줍니다[1]. 기기 식별자를 읽는 법은 [기기 식별자](../../01-foundations/value-decoding/device-identifiers.md) 에서 다룹니다.

**증명하지 못하는 것.** 사용 시간은 구간별 합계라서 앱을 연 시각과 닫은 시각을 하나하나 알려 주지 않고, 앱 안에서 무엇을 했는지도 알려 주지 않습니다. 기기를 들어 올린 사람이 누구인지도 이 기록만으로는 알 수 없습니다. 다른 가족 기기의 행은 그 기기에서 일어난 사용이지 수집한 기기에서 일어난 사용이 아닙니다[1]. 기록이 없다는 사실은 앱을 쓰지 않았다는 뜻이 아닐 수 있고, 화면 사용 시간이 꺼져 있었거나 기간이 지나 사라졌을 수도 있습니다.

보고서에는 "이 앱을 오래 봤다" 대신 "기기 UDID 가 이 값인 기록에서, 이 날짜의 이 구간에 번들 ID `com.example.app` 의 사용 시간이 N초로 집계되어 있다" 처럼 씁니다.

## 시각 해석

Magnet 글이 든 시각은 집계 구간이 시작한 시각이고, 사용 시간은 초 단위입니다[1]. DB 안 시각 칸이 Mac 절대 시각(2001-01-01 기준 초)인지는 확인한 자료가 없어서, 값을 풀 때는 같은 날 다른 기록과 맞춰 기준을 먼저 확인합니다. 설정 plist 의 `datetime` 형은 plist 날짜 형식이라 도구가 날짜로 풀어 줍니다. 시각 기준 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

`ScreenTimeAgent.plist` 에는 `LastTimeZoneName` (str) 키가 있어서 (확인 범위: iPhone 13 mini, iOS 27.0) 시간대와 관련된 값으로 보이지만 뜻은 확인하지 못했습니다. 일간 합계를 다른 기록과 맞출 때는 기기 시간대를 [시간대와 시각 설정](../system-account/time-zone.md) 에서 따로 확인하고, 하루를 UTC 로 끊었는지 현지 시각으로 끊었는지 단정하지 않습니다.

## 함정과 한계

**여러 기기의 기록이 섞입니다.** 가족 공유와 동기화 때문에 수집한 기기에 없는 기기의 UDID 와 사용 기록이 나올 수 있습니다[1]. 행마다 기기 UDID·기기 이름을 확인하고, 수집한 기기의 식별자는 [기기 정보](../system-account/device-info.md) 에서 얻어 맞춰 봅니다.

**화면에 보이는 7일과 DB 의 보관 기간은 다를 수 있습니다.** 설정 화면이 7일치만 보여 준다는 점은 확인했지만[1] DB 쪽 보관 기간은 확인하지 못했습니다. 화면으로 본 결과와 DB 로 본 결과를 섞어 쓰지 않습니다.

**칸 이름은 검체에서 직접 확인합니다.** 참고한 글들은 표 이름과 도구 표시 이름만 알려 주고 실제 칸 이름을 적지 않았습니다[2]. 버전마다 스키마가 달라질 수도 있어서, 도구 출력만 옮기지 말고 `PRAGMA table_info` 로 칸을 확인한 결과를 함께 남깁니다.

**iOS 17 이후에는 바이옴 쪽도 봅니다.** 같은 종류의 기록이 바이옴 `ScreenTime.AppUsage` 스트림에도 있고 보관 기간이 28일이라[3], DB 와 스트림의 합계가 다르면 기간과 집계 방식이 다른지부터 확인합니다.

**지우기와 조작.** 사용자는 화면 사용 시간을 끄거나 켤 수 있고, `FamilyControlsAgent.plist` 에는 이름에 삭제가 들어간 `DidDeleteActivityRecords` 키도 있습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 이 키가 사용 기록을 지운 사건을 뜻하는지는 확인하지 못해서 삭제의 근거로 쓰지 않고, 기록이 비어 있는 구간은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름으로 다른 기록과 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시이고 특정 검체에서 나온 값이 아닙니다. `RMAdminStore-Local.sqlite` 는 SQLite 파일이라 첫 16바이트가 SQLite 머리글입니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

설정 plist 는 이진 plist 로 저장된 경우 첫 8바이트가 `bplist00` 입니다.

```
00000000  62 70 6C 69 73 74 30 30                          bplist00
```

### SQL 로 스키마부터 보기

칸 이름을 확인한 자료가 없어서, 먼저 사본에서 표와 칸을 나열합니다.

```sql
SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name;
PRAGMA table_info(ZUSAGETIMEDITEM);
PRAGMA table_info(ZUSAGECOUNTEDITEM);
```

칸 목록에서 번들 ID, 시각, 초 단위 합계로 보이는 칸을 찾은 뒤, 수집한 기기의 설정 화면에 보이는 최근 7일 합계와 몇 개 앱을 맞춰 보면 칸의 뜻을 검체 안에서 확인할 수 있습니다.

### 공개 도구로 한 번

SQLite 는 `sqlite3` 명령줄 도구로, plist 는 Python 표준 라이브러리 `plistlib` 로 열 수 있습니다.

```
python -c "import plistlib,sys; print(plistlib.load(open(sys.argv[1],'rb')))" com.apple.ScreenTimeAgent.plist
```

로컬 백업 안에서는 파일이 해시 이름으로 저장되어 있어서, 먼저 `Manifest.db` 에서 도메인과 경로로 파일을 찾습니다([로컬 백업](../../01-foundations/backups/local-backup/index.md)). 포렌식 도구가 보여 주는 화면 사용 시간 결과는 위 SQL 결과와 몇 행 맞춰 보고 씁니다. 도구를 검증하는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

화면 사용 시간은 합계라서, 개별 사건이 남는 기록과 함께 봐야 언제 썼는지가 드러납니다. 앱을 앞화면에 띄운 시각은 [KnowledgeC](knowledgec/index.md) 와 [바이옴](biome/index.md), 앱이 돈 시간과 잠금 해제는 [전원 로그](powerlog.md), 알림 수는 [알림 기록](notifications.md), 앱별 통신량은 [앱별 데이터 사용량](../network/data-usage.md) 과 맞춰 봅니다. 가족 공유 계정은 [애플 계정](../system-account/apple-account.md) 에서 확인합니다. 조사 흐름은 [폰 사용 시간 재구성](../../04-scenarios/activity/usage-time.md) 과 [어떤 앱을 언제 썼나](../../04-scenarios/activity/app-usage.md) 를 봅니다.

## 실습

공개 검체(NIST CFReDS 등의 iOS 이미지)에 화면 사용 시간 DB 가 있다면 다음 질문을 풀어 봅니다.

1. `RMAdminStore-Local.sqlite` 와 `RMAdminStore-Cloud.sqlite` 가 둘 다 있습니까? 각각 표가 몇 개이고, `ZUSAGETIMEDITEM` 에는 어떤 칸이 있습니까?
2. 기기 UDID 로 보이는 값이 몇 종류 나오고, 그중 수집한 기기의 UDID 와 같은 값이 있습니까?
3. 가장 오래된 집계 구간 시각은 언제이고, 시각 칸을 Mac 절대 시각으로 풀었을 때 다른 기록과 맞습니까?
4. 하루 사용 시간이 가장 긴 앱의 번들 ID 는 무엇이고, 같은 날 전원 로그나 KnowledgeC 의 기록과 합계가 비슷합니까?
5. 로컬 백업이 함께 있다면 `ScreenTimeAgent.plist` 의 `ScreenTimeEnabled` 와 `UsageGenesisDate` 값은 무엇입니까?

## 참고 문헌

- [1] Getting Evidence from iOS Screen Time Artifacts — Magnet Forensics — https://www.magnetforensics.com/blog/getting-evidence-from-ios-screen-time-artifacts/
- [2] Apple Screen Time — Forensafe — https://forensafe.com/blogs/apple-screen-time.html
- [3] 84 Streams Later, Part 2: Inside Apple Biome — digital-forensics.it (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
