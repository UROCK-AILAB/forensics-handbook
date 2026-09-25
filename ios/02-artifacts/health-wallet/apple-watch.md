---
title: "애플 워치 연결"
parent: "아티팩트 · 건강·지갑·워치"
nav_order: 1060
---

# 애플 워치 연결 (Apple Watch)

짝지은 애플 워치의 데이터가 아이폰과 그 백업에 어떻게 들어오는지, 폰에 남는 워치 관련 도메인과 설정 파일은 무엇인지, 그리고 이 흔적만으로 워치 사용을 어디까지 말할 수 있는지를 정리합니다.

## 무엇을 기록하나 · 왜 생기나

애플 워치는 짝지은 아이폰에 데이터를 자동으로 백업하고, 짝을 풀면(unpair) 최신 데이터를 남기려고 아이폰에 한 번 더 백업합니다[1]. 아이폰을 iCloud 나 컴퓨터에 백업하면 그 백업에 워치 데이터도 들어갑니다[1]. 그래서 워치를 따로 확보하지 못한 사건에서도 폰이나 폰 백업에서 워치의 흔적을 찾을 수 있습니다.

워치의 건강 기록은 워치 백업과 별도로 폰의 건강 데이터베이스로 동기화되고[2], 폰 쪽에서는 기록마다 붙은 출처 기기 정보로 워치에서 온 기록을 가려냅니다[3]. 건강 기록 자체는 [건강 데이터](health.md)에서 다루고, 이 페이지는 워치 백업의 범위와 폰에 남는 연결 흔적을 다룹니다.

## 위치와 버전별 차이

### 워치 백업에 들어가는 것과 빠지는 것

워치 백업의 범위는 아래와 같습니다[1].

| 구분 | 항목 |
|---|---|
| 들어가는 것 | 앱 데이터와 설정, 시스템 설정, 알림·Siri 설정, 홈 화면 배치, 시계 모드, 건강·피트니스 데이터와 이력, 음악 재생 목록, 사진 앨범, 시간대 |
| 조건이 붙는 것 | 건강·피트니스 데이터는 iCloud 백업이나 **암호화한** 컴퓨터 백업일 때만 남습니다[1][2]. |
| 빠지는 것 | 블루투스 짝 정보, Apple Pay 에 쓰는 카드, 워치 암호, 음성 메모처럼 iCloud 로 동기화되는 내용, iCloud 메시지를 쓰는 경우의 메시지 |

가족 설정으로 쓰는 자녀용 워치는 충전 중이면서 Wi-Fi 에 연결되어 있을 때 자동으로 백업되고, 그 백업은 부모의 아이폰이 아니라 그 가족 구성원의 iCloud 로 갑니다[1]. 자녀용 워치의 데이터를 부모 폰에서 찾으면 안 되는 이유가 여기에 있습니다.

워치 백업이 아이폰 안 어느 폴더에 저장되는지, 짝 정보가 어느 데이터베이스의 어느 표에 있는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 검체에서 찾은 경로는 조사 기록에 따로 남깁니다.

### 로컬 백업의 도메인

암호화하지 않은 로컬 백업에도 워치와 관련된 이름의 도메인이 있습니다.

| 도메인 | 비고 |
|---|---|
| `AppDomain-com.apple.Bridge` | 항목 4개 |
| `AppDomainGroup-group.com.apple.bridge` | 항목 3개 |
| `AppDomainPlugin-com.apple.Bridge.BridgeWidgetExtension` | |
| `AppDomainPlugin-com.apple.PBBridgeSupport.BridgeIntents` | |
| `AppDomain-com.apple.CompanionSetup` | |
| `AppDomain-com.apple.chrono.WidgetRenderer-WatchFaces` | |
| `AppDomainPlugin-com.apple.NanoTimeKit.CreateWatchFace` | |
| `AppDomainPlugin-com.apple.NanoTimeKit.NTKDiagnosticExtensionCompanion` | |

`com.apple.Bridge` 를 아이폰의 Watch 앱 번들 ID 로 부르는 일이 흔하지만, 공식 자료로 밝혀진 것은 아닙니다. 도메인 이름을 읽는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md)을, 백업 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md)을 봅니다.

### 버전별 차이

iOS 버전별로 워치 백업 범위나 파일 위치가 어떻게 달라지는지는 공개된 자료가 없습니다. 위 도메인과 아래 설정 파일은 iOS 27.0 백업 기준이라, 다른 버전의 검체에서는 같은 이름이 있는지부터 확인합니다.

## 구조

### 설정 파일

백업의 `HomeDomain` 안 `Library/Preferences/` 에는 아래 파일과 키가 있고, 값의 뜻은 검체에서 확인합니다. 형식은 [속성 목록 파일](../../01-foundations/data-formats/plist.md)에서 다룹니다.

| 파일 | 키 |
|---|---|
| `com.apple.NanoRegistry.plist` | 키 없음(빈 파일) |
| `com.apple.nanoregistryd.plist` | `latestAssetURL`, `lastAssetUpdateCheckDate`(실수), `lastVersionBroadcastTimestamp`(실수) |
| `com.apple.NanoRegistry.NRRootCommander.volatile.plist` | `daemonsEnabled`, `cleanupIndex`, `__BOOTTIME` |
| `com.apple.NanoRegistry.NRLaunchNotificationController.volatile.plist` | `__BOOTTIME` 과 이름이 `.enabled` 로 끝나는 알림 키들 |
| `com.apple.NanoTimeKit.daemon.plist` | `DateOfLastActivity_CleanSnapshotCache`, `DateOfLastActivity_CleanupResources`, `DateOfLastActivity_CleanupUnpairedDevices`(날짜) |
| `com.apple.NanoTimeKit.face.plist` | `LastSystemVersionMigrated` |
| `com.apple.nanotimekitcompaniond.plist` | `CC_OncePerBootBackingData`, `CKPerBootTasks`, `CKStartupTime` |
| `com.apple.wcd.plist` | `WCDStoredInstalledWatchApps`(목록) |
| `com.apple.nanolifestyle.plist` | `HasWatchOnAccount`(정수), `HasWatchOnAccountLastFetchDate`(날짜), `FitnessMode`, `IsStandalonePhoneFitnessMode`, `ActivityMoveMode`, `cachedSleepUserDay` |
| `com.apple.nanolifestyle.connectedgym.plist` | `ConnectedGymNFCAlwaysOn` 등 |
| `com.apple.healthd.plist` | `ShowMedicalIdOnWatch`(참·거짓) |

이 밖에 `com.apple.NanoMail.plist`(`NanoMailDefaultAccountUidKey` 등), `com.apple.NanoMusicSync.plist`, `com.apple.nanoprefsyncd.plist`(`cache-is-valid`), `com.apple.nanonews.sync.plist`(`companionSeenResetDate` 등), `com.apple.sync.NanoHome.plist` 도 있습니다.

키 이름으로 짐작하면 `WCDStoredInstalledWatchApps` 는 워치에 설치된 앱 목록이고, `HasWatchOnAccount` 는 계정에 워치가 있는지를 적은 값으로 보입니다. 두 가지 모두 이름에서 끌어낸 짐작이라, 값을 읽고 다른 기록과 맞춰 본 뒤에 씁니다.

## 증거로서 의미

**증명하는 것**

- 폰의 건강 데이터베이스에 출처 기기가 워치로 적힌 기록이 있고, 그 기기의 이름·모델·펌웨어가 무엇으로 적혀 있는지[3]. 이 기록이 워치에서 이 폰으로 바로 왔는지, iCloud 로 같은 계정의 다른 기기를 거쳐 왔는지는 이것만으로 가를 수 없습니다.

**증명하지 못하는 것**

- 워치 관련 도메인이나 설정 키가 있다는 것만으로 워치를 짝지어 썼다는 사실. 워치를 쓰지 않은 폰에도 이런 키가 생기는지는 알려지지 않았습니다.
- 워치를 찬 사람이 폰 주인이라는 사실
- 워치의 Apple Pay 카드. 워치 백업에 들어가지 않고, iCloud 메시지를 쓰는 경우 메시지도 빠집니다[1].

보고서에는 "피의자가 워치를 썼다" 가 아니라 "폰의 건강 기록 가운데 이 모델의 워치에서 온 기록이 이 기간에 있다" 처럼 씁니다.

## 시각 해석

`com.apple.NanoTimeKit.daemon.plist` 의 `DateOfLastActivity_*` 와 `com.apple.nanolifestyle.plist` 의 `HasWatchOnAccountLastFetchDate` 는 plist 의 날짜형으로 저장됩니다. 반면 `com.apple.nanoregistryd.plist` 의 `lastAssetUpdateCheckDate` 와 `lastVersionBroadcastTimestamp` 는 실수로 저장되고, 이 실수가 유닉스 시각인지 Mac 절대 시각인지는 알려지지 않았습니다. 두 기준 사이에는 978,307,200초(약 31년) 차이가 있어서, 두 방식으로 모두 바꿔 보고 백업 시각이나 iOS 설치 시기와 앞뒤가 맞는 쪽을 고릅니다. 이 판단 과정은 보고서에 함께 적습니다. 바꾸는 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md)에 있습니다.

워치에서 온 건강 기록의 시각은 [건강 데이터](health.md)의 시각 해석 절을 따릅니다.

## 함정과 한계

**블루투스 짝 정보는 워치 백업에 없습니다.** 블루투스 짝 정보는 워치 백업에서 빠집니다[1]. 폰 쪽 블루투스 짝 목록에 워치가 올라가는지는 검체에서 확인하고, 블루투스 기록 일반은 [블루투스 장치](../network/bluetooth.md)에서 다룹니다.

**건강 데이터는 백업 방식에 따라 빠집니다.** 워치의 건강·피트니스 데이터는 iCloud 백업이나 암호화한 컴퓨터 백업에만 남습니다[1][2]. 암호화하지 않은 백업에서 워치 건강 기록이 없다고 해서 워치를 쓰지 않았다고 읽지 않습니다.

**자녀용 워치는 다른 계정으로 갑니다.** 가족 설정 워치의 백업은 그 가족 구성원의 iCloud 로 가므로[1], 부모 폰이나 부모 계정에서는 찾을 수 없습니다. 계정 쪽 자료 요청은 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md)에서 다룹니다.

**짝을 푼 시점.** 짝을 풀 때 워치가 아이폰에 한 번 더 백업되므로[1], 워치를 초기화하거나 다른 폰으로 옮긴 경우에도 이전 폰에 그 시점까지의 워치 백업이 남아 있을 수 있습니다. 이 백업이 폰 안 어디에, 얼마 동안 남는지는 공개된 자료가 없습니다. `com.apple.NanoTimeKit.daemon.plist` 에 `DateOfLastActivity_CleanupUnpairedDevices` 라는 날짜 키가 있지만, 이 값과 짝을 푼 시각의 관계도 알려지지 않았습니다.

## 직접 분석해 보기

### 백업 목록에서 워치 도메인 찾기

로컬 백업의 목록 데이터베이스 `Manifest.db` 에는 `Files` 표가 있고, 칸은 `fileID`, `domain`, `relativePath`, `flags`, `file` 입니다. 아래 쿼리로 워치 관련 이름의 도메인과 설정 파일을 한 번에 뽑을 수 있습니다.

```sql
SELECT domain, relativePath, fileID
FROM Files
WHERE domain LIKE '%Bridge%'
   OR domain LIKE '%NanoTimeKit%'
   OR domain LIKE '%CompanionSetup%'
   OR (domain = 'HomeDomain'
       AND relativePath LIKE 'Library/Preferences/com.apple.%nano%')
ORDER BY domain, relativePath;
```

SQLite 의 `LIKE` 는 영문 대소문자를 가리지 않으므로 `Nano` 와 `nano` 가 함께 걸립니다. 찾은 `fileID` 로 백업 폴더에서 실제 파일을 여는 방법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md)에 있습니다.

### 실수 시각 두 방식으로 바꿔 보기

아래는 명세로 만든 예시이고, 실제 검체의 값이 아닙니다. `lastAssetUpdateCheckDate` 에 `1700000000.0` 이 들어 있다고 하면, 유닉스 시각으로 읽을 때 2023-11-14 22:13:20 UTC 이고 Mac 절대 시각으로 읽을 때 2054-11-14 22:13:20 UTC 입니다. 미래 날짜가 나오는 쪽은 버리고 유닉스 시각으로 판단하며, 반대로 `700000000.0` 이면 유닉스 시각으로는 1992-03-07, Mac 절대 시각으로는 2023-03-08 이 되어 Mac 절대 시각 쪽이 맞습니다.

```
값 1700000000.0
  유닉스 시각       → 2023-11-14 22:13:20 UTC
  Mac 절대 시각     → 2054-11-14 22:13:20 UTC  (미래라서 버림)
값  700000000.0
  유닉스 시각       → 1992-03-07 20:26:40 UTC  (아이폰 이전이라 버림)
  Mac 절대 시각     → 2023-03-08 20:26:40 UTC
```

### 공개 도구

iLEAPP 의 건강 모듈은 `data_provenances` 와 `source_devices` 를 읽어 기록마다 기기 이름·모델을 보여 주므로[3], 워치에서 온 기록을 가려내는 데 쓸 수 있습니다. plist 는 공개 plist 뷰어나 파이썬의 `plistlib` 로 열어 키와 값을 확인합니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 내용 |
|---|---|
| [건강 데이터](health.md) | 출처 기기가 워치인 기록이 있는지, 착용(`data_type` 70) 기록이 언제 있는지 |
| [지갑과 Apple Pay](wallet.md) | 워치 쪽 패스 데이터베이스가 있는지 |
| [블루투스 장치](../network/bluetooth.md) | 폰에 워치가 연결된 흔적이 있는지 |
| [기기 정보](../system-account/device-info.md) | 폰의 iOS 버전과 백업 시각 |
| [KnowledgeC](../app-usage/knowledgec/index.md)·[바이옴](../app-usage/biome/index.md) | 같은 시각에 폰을 쓰고 있었는지 |

기록한 사람이 누구인지 따지는 흐름은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)를 봅니다.

## 실습

공개 검체(NIST CFReDS 등)에서 아이폰 이미지나 백업을 구해 아래 질문을 풀어 봅니다. 워치를 짝지은 검체가 아니면 흔적이 거의 없을 수 있고, 그 사실을 적는 것도 답입니다.

1. `Manifest.db` 에서 위 쿼리를 돌려 워치 관련 도메인이 몇 개 나오는지 세고, 이 페이지의 표와 이름이 같은지 비교합니다.
2. `com.apple.wcd.plist` 의 `WCDStoredInstalledWatchApps` 값을 읽고, 목록이 비어 있는지 적습니다.
3. 건강 데이터베이스가 있으면 `source_devices` 에서 워치로 보이는 기기를 찾고, 그 기기에서 온 첫 기록과 마지막 기록의 시각을 구합니다.
4. `com.apple.nanoregistryd.plist` 의 실수 시각을 두 방식으로 바꾸고, 어느 쪽이 맞는지 근거와 함께 적습니다.

## 참고 문헌

1. Apple Support, "Back up your Apple Watch" — https://support.apple.com/HT204518
2. Apple Platform Security, "Protecting access to user's health data" — https://support.apple.com/guide/security/protecting-access-to-users-health-data-sec88be9900f/web
3. iLEAPP, `scripts/artifacts/health.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/health.py
