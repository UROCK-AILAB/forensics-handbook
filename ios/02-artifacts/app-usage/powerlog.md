---
title: "전원 로그"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 450
---

# 전원 로그 (PowerLog)

전원 로그 (PowerLog)는 아이폰이 전력 사용을 재려고 남기는 SQLite 기록이고, 앱이 앞화면과 백그라운드에서 돈 시간, 화면 잠금과 해제, 배터리 잔량과 충전, 오디오 출력 경로, 카메라와 손전등 사용까지 시각과 함께 담겨 있어 "그 시각에 기기가 어떤 상태였나" 를 짧은 기간 동안 촘촘하게 보여 줍니다.

## 무엇을 기록하나 · 왜 생기나

운영체제는 배터리를 어디에 썼는지 계산하려고 여러 구성 요소의 상태 변화를 계속 적어 두고, 그 결과가 전원 로그입니다. 목적이 전력 계산이라서 사용자가 무엇을 봤는지가 아니라 어떤 앱이 얼마나 돌았는지, 화면이 켜졌는지, 어떤 장치가 전기를 썼는지가 남습니다. iOS 10.2 기준으로 손전등·카메라·블루투스·Wi-Fi·앱 사용·음량·오디오 출력·잠금 화면 활동이 기록됩니다[4].

기록은 오래 남지 않습니다. 기기는 하루 단위로 내용을 압축본으로 내보내고[5], 켜져 있는 동안 오래된 기록을 계속 지워 나갑니다. 그래서 관심 시점 이후 기기를 오래 켜 둘수록 기록이 사라질 가능성이 커집니다(iOS 10.2 탈옥 기기 기준)[4]. 압축본을 며칠 치 남기는지는 실제 기기에서 확인해야 합니다.

## 위치와 버전별 차이

### 기기 안 경로

현재 기록은 공유 시스템 그룹 컨테이너 안의 `BatteryLife` 폴더에 있습니다[5][6].

```
/private/var/containers/Shared/SystemGroup/<GUID>/Library/BatteryLife/CurrentPowerlog.PLSQL
/private/var/containers/Shared/SystemGroup/<GUID>/Library/BatteryLife/CurrentPowerlog.PLSQL-wal
/private/var/containers/Shared/SystemGroup/<GUID>/Library/BatteryLife/CurrentPowerlog.PLSQL-shm
```

지난 기록은 gzip 으로 압축한 파일로 따로 남고, 이름은 `powerlog_2018-10-07_7F9FC438.PLSQL.gz` 처럼 날짜 뒤에 16진수 8자리가 붙는 형식입니다[5]. 압축본은 같은 `BatteryLife` 폴더 아래 `Archives` 하위 폴더에 있습니다[5].

확장 기록인 PerfPowerTelemetry 는 배터리 자료를 담은 `.EPSQL` 과 백그라운드 작업을 담은 `.BGSQL` 로 나뉩니다[3]. 기기 안 전체 경로는 공개 자료가 없고, 공개 파서 iLEAPP 가 찾는 위치는 다음과 같습니다[3].

```
*/BatteryLife/*.PLSQL*
*/[Pp]ower[Ll]og/*.PLSQL*
*/powerlogs/*.PLSQL*
*/sysdiagnose_*.tar.gz
*/PerfPowerTelemetry/*/*.EPSQL*
*/PerfPowerTelemetry/*/*.BGSQL*
```

### 수집 방식에 따라 얻는 범위

| 수집 방식 | 전원 로그 |
|---|---|
| AFU 상태 수집(전체 파일시스템) | `CurrentPowerlog.PLSQL` 전체를 얻습니다[6] |
| sysdiagnose | 일부만 얻습니다[6]. 묶음 안 `logs/powerlogs/` 아래에 `.PLSQL`·`.EPSQL`·`.BGSQL` 파일이 있고, sysdiagnose(iOS 13.3.1~26)에는 DB 파일만 있고 `-wal`·`-shm` 은 없습니다[3]. 전체 파일시스템 수집 안에서는 `DiagnosticLogs/sysdiagnose` 아래에 sysdiagnose 가 들어 있는 경우도 있습니다[3] |
| 로컬 백업 | 로컬 백업에는 `CurrentPowerlog.PLSQL`·`BatteryLife` 폴더·`.PLSQL`/`.EPSQL`/`.BGSQL` 파일이 들어 있지 않습니다[4] |

sysdiagnose 묶음을 여는 법은 [sysdiagnose 묶음](../../01-foundations/backups/sysdiagnose.md), 수집 방식 차이는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

### 로컬 백업에 보이는 전원 관련 설정 파일

로컬 백업에 전원 로그 DB 는 없지만, 이름에 전원 로그나 전원 관리가 들어간 설정 파일과 도메인은 있습니다. 이 plist 들이 무엇을 기록하는지는 공개 자료가 없어서, 아래에는 키 이름만 적습니다.

| 도메인 :: 경로 | 키 |
|---|---|
| `HomeDomain :: Library/Preferences/com.apple.powerlogHelperd.plist` | `BootSessionUUID` (str) |
| `HomeDomain :: Library/Preferences/com.apple.powerlogd.plist` | 키 없음(빈 파일) |
| `HomeDomain :: Library/Preferences/com.apple.powerui.cec.plist` | `currentPhase` (int), `bootUUIDOnLastInit` (str) |
| `HomeDomain :: Library/Preferences/com.apple.powerui.lowSOCAnalyzer.plist` | `kDefaultsMinSOCDate` (datetime), `predictionConfidence` (float), `pluggedinTime` (datetime) |
| `HomeDomain :: Library/Preferences/com.apple.powerui.notification.plist` | 키 없음(빈 파일) |
| `HomeDomain :: Library/Preferences/com.apple.powerui.runtimeAwareness.plist` | `bootUUIDOnLastInit` (str) |
| `SysSharedContainerDomain-systemgroup.com.apple.powerexceptions :: RepeatOffenders.plist` | 키 없음(빈 파일) |

도메인 이름으로는 `AppDomainPlugin-com.apple.PowerlogCore.DEPowerlogEPL`, `AppDomainPlugin-com.apple.PowerlogCore.diagnosticextension`, `AppDomainPlugin-com.apple.DiagnosticExtensions.sysdiagnose` 가 있습니다. 백업 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md), plist 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

### 버전별로 달라지는 표와 열

아래는 iOS 12.4~26 시험 이미지에서 드러난 차이입니다[3]. iOS 27 의 스키마는 실제 데이터로 확인해야 합니다. 이 밖에도 버전마다 다른 표가 더 있어 따로 검증해야 합니다[3].

| iOS 버전 | 달라지는 점 |
|---|---|
| 15 이하 | `PLBatteryAgent_EventBackward_Adapter` 에 행이 없었습니다. 16.1.1 이미지부터 행이 있는 경우가 나왔지만 16.5·18.3.2 이미지 가운데에도 행이 0 인 것이 있었고, 일부 iOS 16 스키마에는 전압·전류 열이 없습니다 |
| 17 부터 | `PLAudioAgent_EventForward_Routing` 에 `BTEndpointType` 열이 생깁니다 |
| 18 부터 | 같은 표에서 `ActivePID` 열이 없어지고, `ANE_modelLoad_1_2`·`ANE_modelUnload_1_2`, `BatteryTrustedData_Daily`, `GenerativeFunctionMetrics_*` 표가 나옵니다 |
| 18 후반 | `PLAppTimeService_Aggregate_AppRunTime` 에 `InCall*` 열이 생깁니다 |
| 26 | `.BGSQL` 에 `BackgroundProcessing_TaskInstanceData`·`BackgroundProcessing_TaskMetadata` 표가 나옵니다 |

## 구조

`.PLSQL` 은 SQLite 데이터베이스이고, 표 이름이 `PL` + 기록하는 에이전트 + 사건 종류 형식으로 붙습니다. SQLite 자체의 구조와 `-wal` 처리는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다. 조사에서 자주 쓰는 표는 다음과 같고, 열 이름은 iLEAPP 의 `powerlog.py` 기준입니다[3].

| 표 | 주요 열 | 알려 주는 것 |
|---|---|---|
| `PLAppTimeService_Aggregate_AppRunTime` | `timestamp`, `BundleID`, `BackgroundTime`, `ScreenOnTime`, `InCallBackgroundTime`, `InCallScreenOnTime` | 앱별 앞화면·백그라운드 실행 시간. 초 단위로 읽으면 표본 구간 길이와 맞았습니다 |
| `PLApplicationAgent_EventForward_Application` | `timestamp`, `Identifier`, `pid`, `State`, `Reason` | 앱 상태 전환. `State` 관찰값 0, 1, 2, 4, 8, 32, `Reason` 관찰값 0, 1 |
| `PLSpringBoardAgent_EventForward_SBLock` | `timestamp`, `Locked` (0/1) | 화면 잠금·잠금 해제 상태 변화. iOS 12.4~26 에서 스키마가 같았습니다 |
| `PLSpringBoardAgent_EventPoint_SBAutoLock` | `timestamp`, `AutoLockType` | 자동 잠금. 관찰값 1, 4 |
| `PLSleepWakeAgent_EventForward_PowerState` | `timestamp`, `Event`, `State`, `Reason`, `UUID` | 잠자기·깨어남. 관찰값 `State` 0~2, `Event` 0~5, `Reason` 1 또는 null |
| `PLBatteryAgent_EventBackward_BatteryUI` | `timestamp`, `Level` (1~100), `IsCharging` (0/1) | 배터리 잔량(백분율로 보임)과 충전 여부 |
| `PLBatteryAgent_EventBackward_Adapter` | `timestamp`, `SystemInputVoltage`, `SystemInputCurrent`, `SystemPowerIn`, `SystemLoad`, `AdapterEfficiencyLoss` | 충전기 입력. 연결 중 `SystemInputVoltage` 가 5000·9000 근처에 모였고 단위는 단정하지 않습니다 |
| `PLDisplayAgent_EventForward_Display` | `timestamp`, `Brightness`, `SliderValue`, `lux`, `mNits` | 화면 밝기. `Brightness` 관찰값 0~100 |
| `PLAudioAgent_EventForward_Routing` | `timestamp`, `Active`, `ActiveRoute`, `OutputCategory`, `HeadphonesConnected`, `BTEndpointType`, `ActivePID` | 오디오 출력 경로와 분류 |
| `PLCameraAgent_EventForward_Camera` | `timestamp`, `BundleId`, `CameraType` (0~4), `State` (0/1) | 카메라 사용. 전체 열 구성은 버전마다 다릅니다 |
| `PLCameraAgent_EventForward_Torch` | `timestamp`, `BundleId`, `Level` | 손전등. 시험 이미지마다 23행 이하로 드뭅니다 |
| `ANE_modelLoad_1_2` / `ANE_modelUnload_1_2` | `timestamp`, `csIdentity`, `modelURL` (load 는 `modelSize`, `modelLoadingTime`, `cacheHit`, `isPrecompiled` 추가) | 온디바이스 모델 적재. iOS 18·26 시험 이미지에서만 나왔습니다 |
| `GenerativeFunctionMetrics_*_1_2` (Summarization, tgiExecuteRequest, mmExecuteRequest, assetLoad, OptIn) | `mmExecuteRequest` 의 `useCaseIdentifier` 관찰값 예: `summarization.summarizeMailMessage` | Apple Intelligence 관련 기록 |

오디오 경로 열에는 `Speaker`, `Receiver`, `HeadphonesBT`, `CarAudioOutput`, `INVALID` 값이, 분류 열에는 `Alarm`, `Ringtone`, `PhoneCall`, `Audio/Video`, `FindMyPhone`, `VoiceCommand` 값이 나옵니다[3]. `GenerativeFunctionMetrics_*` 표는 iOS 18~26 이미지 여럿에 있었지만 행이 있는 경우는 Apple Intelligence 지원 기기(iPhone 16, iOS 26.5.2 sysdiagnose)뿐이었고 나머지는 행이 0 이었습니다[3].

PerfPowerTelemetry 쪽 표는 다음과 같습니다[3].

| 파일 | 표 | 주요 열 |
|---|---|---|
| `.EPSQL` | `BatteryDataCollection_BDC_Daily` | `CycleCount`, `MaxCapacityPercent`, `NominalChargeCapacity`, `ChargingVoltage` |
| `.EPSQL` | `BatteryDataCollection_BDC_SmartCharging`, `BatteryDataCollection_BDC_Once` | `BDC_Once` 에 `DesignCapacity` 등 |
| `.EPSQL` | `BatteryTrustedData_Daily` (iOS 18 이상) | `TrustedCycleCount`, `TrustedMaximumCapacity`, `TrustedDateOfFirstUse` |
| `.BGSQL` | `BackgroundProcessing_TaskInstanceData` | `ProcessName`, `PID`, `StartDate`, `EndDate`, `StartedOnBattery` 등 |
| `.BGSQL` | `BackgroundProcessing_TaskMetadata` | `BundleID`, `Name`, `ServiceName`, `GroupName`, `LaunchReason` |

## 증거로서 의미

**증명하는 것.** 기록이 남아 있는 기간 안에서는 특정 시각에 화면이 잠겨 있었는지 풀려 있었는지, 어떤 번들 ID 의 앱이 표본 구간마다 앞화면과 백그라운드에서 몇 초 돌았는지, 충전기가 연결되어 있었는지와 배터리 잔량이 얼마였는지, 오디오가 스피커·수화부·블루투스 헤드폰·차량 중 어디로 나갔는지, 어떤 앱이 카메라나 손전등을 켰는지를 보여 줍니다. 번들 ID 를 앱 이름으로 바꾸는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에서 다룹니다. 보고서에는 "이 시각에 화면 잠금이 풀린 기록이 있다", "이 구간에 이 앱의 앞화면 실행 시간이 N초로 기록되어 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

**증명하지 못하는 것.** 잠금 해제 기록으로는 누가 풀었는지 알 수 없고, 앱 실행 시간으로는 앱 안에서 무엇을 했는지 알 수 없습니다. 앱 실행 시간 표는 집계 표(Aggregate)라서 개별 실행이 시작된 시각이 아니라 표본 구간 단위의 합계입니다[3]. 카메라 기록도 사진을 찍었다는 뜻이 아니라 카메라가 켜졌다는 사실만 보여 줍니다. 기록이 짧게 돌아가며 지워지기 때문에, 행이 없다고 해서 그 사건이 없었다고 말할 수 없습니다[4].

## 시각 해석

표의 `timestamp` 열은 1970년 기준 초인 유닉스 시각이고, 2001년 기준인 Mac 절대 시각이 아닙니다[3]. 유닉스 시각이라서 시간대 없이 UTC 로 읽고 현지 시각은 따로 더합니다. 시각 형식 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

가장 중요한 주의점은 raw `timestamp` 가 전원 로그 내부 시계를 따른다는 점이고, 이 값이 실제 시각과 크게 어긋날 수 있습니다[3]. 보정값은 `PLStorageOperator_EventForward_TimeOffset` 표의 `system` 열(초 단위)에 있습니다. 각 행의 raw 값에는 그 값과 같거나 그 이전인 가장 가까운 보정 행의 `system` 값을 더합니다. 가장 오래된 보정 행보다 앞선 행에는 가장 오래된 보정 행의 값을 쓰고, 보정 표가 없으면 raw 값을 그대로 씁니다[3].

iLEAPP 시험에서 어긋난 정도는 다음과 같았고, 보정한 뒤에는 모두 수집일과 맞았습니다[3].

| 시험 자료 | raw 값의 어긋남 |
|---|---|
| iOS 12.4 이미지 | 수집일보다 69초 앞섬 |
| iOS 18.7 이미지 | 수집일보다 약 32일 늦음 |
| iOS 26.5.2 sysdiagnose | 내부 시계가 1971년을 가리켜 약 54.7년(약 17.3억 초) 뒤처짐 |

PerfPowerTelemetry 도 같은 방식이라 `.EPSQL` 은 `PPTStorageOperator_TimeOffset` 표(뒤에 붙는 보존 기간 접미사가 iOS 버전마다 다름), `.BGSQL` 은 `BackgroundProcessing_TimeOffset` 표로 보정합니다[3]. 다만 `BatteryTrustedData_Daily` 의 `TrustedDateOfFirstUse` 와 `BackgroundProcessing_TaskInstanceData` 의 `StartDate`·`EndDate` 는 보정이 필요 없는 일반 유닉스 시각입니다[3].

사용자가 기기 시각을 직접 바꿀 때 보정 표에 행이 생기는지는 공개 자료로 밝혀지지 않았습니다. 그래서 시각 조작을 의심할 때는 보정 표의 값이 바뀐 지점을 표시해 두고 다른 기록과 맞춰 보는 데 그칩니다.

## 함정과 한계

**사본마다 시각이 다르게 나옵니다.** 같은 사건이 현재 로그·압축본·sysdiagnose 여러 사본에 들어 있으면 사본마다 자기 보정값을 쓰기 때문에 표시 시각이 달라질 수 있습니다. iLEAPP 시험 이미지 하나에서는 손전등 사건 하나가 사본 7개에 있었고, 최대 6초 차이로 세 가지 시각에 나왔습니다[3]. 몇 초 차이 나는 같은 사건을 서로 다른 사건으로 세지 않습니다.

**도구가 중복을 없애 주지 않습니다.** iLEAPP 는 사본 사이 중복을 걸러 내지 않습니다. sysdiagnose 가 현재 로그 기간 안에 있던 이미지 두 개에서는 sysdiagnose 행의 99.9% 가 현재 로그와 겹쳤고, sysdiagnose 가 몇 달 앞선 이미지에서는 99.2% 가 겹치지 않았습니다[3]. 건수를 세거나 그래프를 그릴 때는 사본별로 나누어 보고, 겹치는 기간을 먼저 확인합니다.

**정수 코드의 뜻을 단정하지 않습니다.** `State`, `Reason`, `Event`, `AutoLockType`, `CameraType` 은 정수 코드이고 iLEAPP 도 뜻을 풀지 않았습니다[3]. 예를 들어 `PLApplicationAgent_EventForward_Application` 의 `State` 값 하나를 "앞화면으로 올라왔다" 라고 적으려면, 같은 기기에서 다른 아티팩트로 그 시각의 행동을 확인한 근거가 따로 있어야 합니다.

**`-wal` 을 빠뜨리면 최근 기록이 빠집니다.** 전체 파일시스템 수집에서는 `CurrentPowerlog.PLSQL` 을 `-wal`·`-shm` 과 함께 복사해 열어야 가장 최근 행까지 보입니다. sysdiagnose 안 사본에는 `-wal` 이 없습니다[3].

**버전마다 표가 다릅니다.** 같은 표라도 열이 생기고 사라지고, 일부 표는 특정 버전이나 기기에서만 행이 있습니다. 표가 비어 있을 때는 그 기능을 쓰지 않았다고 보기 전에 그 버전·기기에서 원래 행이 생기는 표인지부터 확인합니다.

**지우기와 조작.** 기기를 오래 켜 두기만 해도 오래된 기록이 스스로 사라집니다[4]. 관심 시점 앞뒤로 기록이 끊겨 있으면 먼저 보존 기간이 지나 사라진 것인지 확인하고, [초기화와 복원 흔적](../system-account/erase-restore.md) 과 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 를 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시이고 실제 데이터에서 나온 값이 아닙니다. 현재 로그 `CurrentPowerlog.PLSQL` 은 SQLite 파일이라 첫 16바이트가 SQLite 머리글 문자열입니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

압축본 `powerlog_*.PLSQL.gz` 은 gzip 파일이라 첫 두 바이트가 `1F 8B` 이고, 풀면 같은 SQLite 머리글이 나옵니다.

```
00000000  1F 8B 08 ...
```

확장자가 `.PLSQL` 이 아니거나 이름이 바뀐 파일도 이 머리글로 전원 로그 후보를 가려낼 수 있고, 그다음 `sqlite_master` 에서 `PLStorageOperator_EventForward_TimeOffset` 같은 표 이름이 있는지 보면 전원 로그인지 확인할 수 있습니다.

### SQL 로 보정 시각 읽기

아래는 위 보정 방법을 SQL 로 옮긴 예시이고[3], 결과는 공개 도구의 출력과 맞춰 보고 씁니다. 원본이 아니라 사본에서 실행합니다.

```sql
SELECT a.timestamp AS raw_ts,
       a.timestamp + COALESCE(
         (SELECT o.system FROM PLStorageOperator_EventForward_TimeOffset o
           WHERE o.timestamp <= a.timestamp
           ORDER BY o.timestamp DESC LIMIT 1),
         (SELECT o.system FROM PLStorageOperator_EventForward_TimeOffset o
           ORDER BY o.timestamp ASC LIMIT 1),
         0) AS adjusted_ts,
       datetime(a.timestamp + COALESCE(
         (SELECT o.system FROM PLStorageOperator_EventForward_TimeOffset o
           WHERE o.timestamp <= a.timestamp
           ORDER BY o.timestamp DESC LIMIT 1),
         (SELECT o.system FROM PLStorageOperator_EventForward_TimeOffset o
           ORDER BY o.timestamp ASC LIMIT 1),
         0), 'unixepoch') AS adjusted_utc,
       a.Locked
FROM PLSpringBoardAgent_EventForward_SBLock a
ORDER BY a.timestamp;
```

raw 값과 보정 값을 둘 다 남겨 두면, 나중에 다른 사본이나 다른 도구와 시각이 다를 때 어디서 차이가 났는지 다시 따라가 볼 수 있습니다.

### 공개 도구로 한 번

공개 도구 iLEAPP 의 `powerlog.py` 는 전원 로그 항목 24개를 다루고, 위 경로에서 현재 로그·압축본·sysdiagnose·PerfPowerTelemetry 를 찾아 보정한 시각으로 보여 줍니다[1][3]. APOLLO 로도 전원 로그를 읽을 수 있습니다[4]. 도구 결과는 사본 경로별로 나누어 보고, 같은 사건이 몇 초 차이로 여러 번 나오는지 확인합니다. 도구를 검증하는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

전원 로그는 기간이 짧은 대신 촘촘해서, 기간이 긴 다른 기록과 맞춰 볼 때 쓸모가 큽니다. 앱 사용 시간은 [KnowledgeC](knowledgec/index.md), [바이옴](biome/index.md), [화면 사용 시간](screen-time.md) 과 비교하고, 화면 잠금과 잠금 해제는 [통합 로그에서 찾을 것](../logs/unified-log-events.md) 과 맞춰 봅니다. 오디오 경로가 블루투스나 차량으로 나간 시각은 [블루투스 장치](../network/bluetooth.md) 와, 통화 분류 오디오는 [통화 기록](../communications/call-history.md) 과, 카메라 사용은 [카메라 사진과 메타데이터](../media/dcim-exif.md) 와 대조합니다. sysdiagnose 안의 다른 기록은 [sysdiagnose 안의 로그](../logs/sysdiagnose-logs.md), 기기 시간대는 [시간대와 시각 설정](../system-account/time-zone.md), 시간 순으로 엮는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다. 조사 흐름은 [어떤 앱을 언제 썼나](../../04-scenarios/activity/app-usage.md) 와 [폰 사용 시간 재구성](../../04-scenarios/activity/usage-time.md) 을 봅니다.

## 실습

공개된 시험 데이터(NIST CFReDS 등의 iOS 이미지)에 전원 로그가 들어 있다면 다음 질문을 풀어 봅니다.

1. 전원 로그 사본이 모두 몇 개이고, 각각 현재 로그·압축본·sysdiagnose 중 어디서 나왔습니까?
2. 사본마다 `PLStorageOperator_EventForward_TimeOffset` 의 `system` 값은 얼마이고, 보정한 뒤 마지막 행의 시각이 수집일과 맞습니까?
3. `PLSpringBoardAgent_EventForward_SBLock` 에서 하루 중 잠금 해제가 가장 잦은 시간대는 언제이고, 같은 시간대에 `PLAppTimeService_Aggregate_AppRunTime` 의 `ScreenOnTime` 이 긴 앱은 무엇입니까?
4. 같은 사건이 두 사본에 모두 있을 때 표시 시각이 몇 초 차이 납니까?
5. 그 데이터의 iOS 버전에서 `BTEndpointType`, `ActivePID`, `InCall*` 열 가운데 어느 것이 있습니까?

## 참고 문헌

- [1] Stream the PowerLog telemetry tables through the shared artifact result (iLEAPP PR #2236) — https://github.com/abrignoni/iLEAPP/pull/2236
- [3] iLEAPP scripts/artifacts/powerlog.py (main, 2026-09-18 갱신) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/powerlog.py
- [4] Playing with the iOS Powerlog — ThinkDFIR (2018) — https://thinkdfir.com/2018/09/15/playing-with-the-ios-powerlog/
- [5] Aggregating iOS PowerLog data using C# - Part 1 — forensicmike1 (2019) — https://www.forensicmike1.com/2019/04/28/aggregating-ios-powerlog-data-using-c-part-1/
- [6] Exploring Data Extraction from iOS Devices: What Data You Can Access and How — digital-forensics.it (2025-09) — https://blog.digital-forensics.it/2025/09/exploring-data-extraction-from-ios.html
