---
title: "나의 찾기"
parent: "아티팩트 · 위치"
nav_order: 620
---

# 나의 찾기 (Find My)

## 한 줄 요약

나의 찾기는 기기·물건·가족의 위치를 찾고 위치를 공유하는 Apple 기능이고, 앱 캐시(`fmipcore`)에는 기기·물건·가족·안전 위치 목록이, 나의 찾기 네트워크 데몬(`searchpartyd`)의 DB 에는 주변에서 관찰한 비콘 기록이 남지만, iOS 16 이상 검체에서 본 이 DB 들은 암호화되어 있고 로컬 백업에는 설정 plist 만 보입니다.

## 무엇을 기록하나 · 왜 생기나

사용자는 현재 위치를 다른 사람과 잠시 또는 계속 공유할 수 있고, 이 공유는 메시지나 나의 찾기 앱 등에서 합니다 [1]. 나의 찾기 앱의 캐시에는 기기, AirTag 같은 물건, 가족 구성원, 안전 위치 목록이 남습니다 [2].

이와 별개로 `searchpartyd` 는 주변에서 나의 찾기 호환 기기가 내보내는 블루투스 광고를 관찰해 기록합니다 [3]. 원치 않는 추적기 관련 정보도 이 데몬 폴더에 남습니다 [3]. 그래서 나의 찾기 흔적은 "누구의 기기·물건을 이 기기에 등록했나" 와 "이 기기 주변에 어떤 추적기가 있었나" 라는 두 질문에 쓰입니다.

## 위치와 버전별 차이

### 앱 캐시

`*/Caches/com.apple.findmy.fmipcore/` 아래에 다음 파일이 있습니다 [2].

| 파일 | 담긴 내용 [2] |
|---|---|
| `Devices.data` | 기기 식별자, 표시 이름, 모델·종류, 소유자 ID, "위치 켜짐"·"분실 모드"·암호 길이 표시 |
| `Items.data` | 물건(AirTag 등) 식별자, 이름, 종류, 제조사, 일련번호, 연결된 안전 위치 ID |
| `ItemGroups.data` | [2] 에 파일 이름만 있고 내용 설명은 확인하지 못함 |
| `FamilyMembers.data` | Apple ID, 이름, 전화번호, 사용자 ID |
| `SafeLocations.data` | 위도·경도, 주소, 장소 이름, 추가된 시각 |
| `Owner.data` | [2] 에 파일 이름만 있고 내용 설명은 확인하지 못함 |

이 파일들의 저장 형식, 암호화 여부, 어느 iOS 버전 기준인지는 [2] 에 나와 있지 않습니다.

### 나의 찾기 네트워크 데몬

`/private/var/mobile/Library/com.apple.icloud.searchpartyd` 폴더에 DB 와 하위 폴더가 있습니다 [3].

| 파일·폴더 | 담긴 내용 [3] |
|---|---|
| `Observations.db` | 주변에서 관찰한 호환 기기. 표 `ObservedAdvertisement`(스캔 시각, MAC 주소, RSSI, 일시 공개키), `ObservedAdvertisementBeaconInfo`(비콘 UUID, 순번), `ObservedAdvertisementLocation`(위도·경도) |
| `ItemSharingKeys.db` | `NearOwnerKeys` 표에 공유된 비콘의 현재·앞으로의 광고 값과 블루투스 MAC |
| `BeaconNamingRecords/` | 소유 비콘의 UUID 정보 |
| `SharedBeacons/` | 공유받은 비콘 정보 |
| `WildModeAssociationRecord/` | 원치 않는 추적기를 감지한 기록. 위치와 알림 여부가 담긴 암호화된 plist |

### 버전별로 확인한 내용

| 시기·버전 | 확인한 내용 | 근거 |
|---|---|---|
| iOS 16.x 이상 | 글쓴이가 본 검체에서 `searchpartyd` DB 를 SQLite Encryption Extension(AES-256 OFB)으로 암호화, DB 이름마다 키체인 항목이 따로 있음. 이 파일들은 iOS 16.x 이상에서만 보였다고 적음 | [3] |
| iOS 27.0 로컬 백업 | `fmipcore` 캐시와 `searchpartyd` DB 는 백업 DB 목록에 없음, 설정 plist 와 도메인만 있음 | |

암호화된 DB 는 일반 SQLite 열람기로 바로 열리지 않고, 키체인과 보호 등급의 관계는 [키체인](../../01-foundations/storage/keychain.md) 과 [데이터 보호](../../01-foundations/storage/data-protection/index.md) 에서 다룹니다. `searchpartyd` DB 가 로컬 백업에 들어가는지는 [3] 에 나와 있지 않고, 관찰한 백업에서는 보이지 않았습니다.

### 로컬 백업에서 보이는 것

로컬 백업에는 나의 찾기 관련 도메인으로 `AppDomain-com.apple.findmy`, `AppDomain-com.apple.findmy.FindingUIAngel`, `AppDomain-com.apple.findmy.remoteuiservice`, `AppDomain-com.apple.icloud.FindMyDevice.FindMyExtensionContainer`, `AppDomainGroup-group.com.apple.icloud.findmydevice.magsafe`, `AppDomainGroup-group.com.apple.icloud.findmydevice.shared-configuration`, `SysContainerDomain-com.apple.icloud.findmydeviced`, `SysSharedContainerDomain-systemgroup.com.apple.icloud.findmydevice.managed`, `SysSharedContainerDomain-systemgroup.com.apple.icloud.searchpartyd.sharedsettings` 가 있었습니다. 도메인 체계는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 설명합니다.

## 구조

### 로컬 백업의 설정 plist

다음 plist 들에서 키 이름을 확인했습니다. 값은 가려져 있어 읽지 않았습니다.

| 파일 | 조사와 관련 있어 보이는 키 |
|---|---|
| `SysSharedContainerDomain-systemgroup.com.apple.icloud.findmydevice.managed :: Library/Preferences/FMIPStateInfo.plist` | `fmipActive`(bool), `fmipLostModeType`(int) |
| `HomeDomain :: Library/Preferences/com.apple.icloud.findmydeviced.FMIPAccounts.plist` | `addTime`(float), `osVersion`(str), `versionHistory`(list), `lowBatteryLocate`(bool), `dsid`(str), `enableContext`(int) |
| `HomeDomain :: Library/Preferences/com.apple.icloud.findmydeviced.plist` | `command-register-id`, `command-locate-id`, `command-locate-ackData`(`message`, `status`), `command-dataUpdate-id`, `LastLaunchVersion`, `Daemon::LastOSLaunchVersion` |
| `HomeDomain :: Library/Preferences/com.apple.findmy.fmipcore.notbackedup.plist` | `FMLastLocationRequestPrefKeys.timestamp`(datetime), `FMLastLocationRequestPrefKeys.count`(int), `FMLastLocationRequestPrefKeys.enabled`(bool), `FMIPLimitedPrecisionPrefKey.limitedPrecision`(bool), `itemLearnMoreURL`, `publicAPSToken` |
| `HomeDomain :: Library/Preferences/com.apple.findmy.fmfcore.notbackedup.plist` | `FMFLimitedPrecisionPrefKey.limitedPrecision`(bool), `publicAPSToken` |
| `HomeDomain :: Library/Preferences/com.apple.findmy.findmylocated.plist` | `SecureLocationConfigNextCheck`, `LabelledLocationFetchStatus`, `DataManager::lastRefreshClientSuccessDate`(datetime), `NITokenService::setLocalDeviceFindable`(bool), `NITokenService::lastTokenRequestAttemptDate`(datetime), `lastShownSaveMeAlertIdentifier` |
| `HomeDomain :: Library/Preferences/com.apple.icloud.searchpartyd.plist` | `lastPairingEvents`(bytes), `lastFinderPublishDates`(`batteryWiFi`, `powerWiFi`), `lastFinderAttemptDate`(datetime), `OwnedDeviceLastPublishDate`(datetime), `lastLOISyncDate`(datetime), `userHasAcknowledgedFindMy`(bool), `FinderStateInfo-finderState`(bool), `FinderStateInfo-beaconFindMyAccessoryAssociated`(bool), `FMIPStateManager.fmipState`(bool), `observationStorePersistenceVersion`(int), `BeaconStore::lastMetricsPublish`(datetime) |
| `HomeDomain :: Library/Preferences/systemgroup.com.apple.icloud.searchpartyd.sharedsettings.plist` | `SPSettingsServiceDisabledReasonsKey`(list), `SPBeaconZoneCreationDateKey`(datetime) |
| `HomeDomain :: Library/Preferences/com.apple.findmy.plist` | `tabInfo`, `CustomMapStyle`, `restoreState`, `CustomMapMode_Options_explore` |

키 이름으로 보아 `fmipActive` 는 나의 iPhone 찾기가 켜져 있는지, `fmipLostModeType` 은 분실 모드 종류, `command-locate-*` 는 원격 위치 조회 명령과 관련 있어 보이지만, 각 값의 뜻(예: `fmipLostModeType` 숫자가 무엇을 뜻하는지)은 확인하지 못했습니다. 파일 이름에 `notbackedup` 이 들어간 plist 도 관찰한 로컬 백업에 들어 있었습니다. plist 를 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

### 다른 곳에 남는 흔적

위치 권한 기록 `RootDomain :: Library/Caches/locationd/clients.plist` 에는 `icom.apple.findmy:` 항목이 있고 키에 `Authorization`, `LocationTimeStopped`, `ReceivingLocationInformationTimeStopped` 등이 있습니다. 이 파일 전체는 [위치 기록 데몬](routined.md) 에서 다룹니다. 푸시 설정 `HomeDomain :: Library/Preferences/com.apple.apsd.plist` 의 `APSPersistentTopics` 목록에는 `com.apple.icloud.searchpartyd.aps`, `com.apple.icloud.findmydeviced.aps-production`, `com.apple.icloud.fmfd.aps`, `com.apple.findmy.push.com.apple.findmy.container` 가 있습니다.

## 증거로서 의미

**증명하는 것**

- `fmipcore` 캐시의 기기·물건·가족 목록은 그 기기의 나의 찾기 앱이 해당 기기·물건·구성원을 보여 줄 수 있었다는 사실을 보여 줍니다.
- `SafeLocations.data` 의 추가 시각은 그 안전 위치가 추가된 시각을 보여 줍니다 [2].
- `Observations.db` 의 행은 그 시각에 이 기기가 해당 광고를 수신했고, 수신 세기(RSSI)가 얼마였는지를 보여 줍니다 [3].

**증명하지 못하는 것**

- 관찰 기록의 일시 공개키는 28바이트이고 앞 6바이트가 블루투스 MAC 주소이며, 15분마다 바뀌어서 [3], 서로 다른 시각의 관찰이 같은 추적기인지 공개키만으로 이을 수 없습니다.
- 관찰 기록은 주변에 신호가 있었다는 뜻이지, 누가 추적기를 숨겼는지나 추적기 주인이 누구인지는 알려 주지 않습니다.
- 캐시에 있는 가족·물건 목록은 앱이 받아 둔 목록이라서, 기기 주인이 그 물건을 직접 등록했다고 단정할 수 없습니다.
- 로컬 백업의 plist 키 이름만으로 나의 찾기 켜짐이나 분실 모드 상태를 확정할 수 없습니다.

보고서에는 "이 기기의 `Observations.db` 에 이 시각, 이 비콘 UUID 의 광고를 RSSI 얼마로 수신한 기록이 있다" 처럼 씁니다.

## 시각 해석

`searchpartyd` DB 의 시각 형식은 유닉스 시각이라는 요약을 보았지만 원문으로 확인하지 못했고, `fmipcore` 캐시 파일의 시각 형식도 [2] 에 나와 있지 않습니다. 값을 찾으면 자릿수와 기준 시점을 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 따라 가리고, 같은 시각대의 다른 기록과 맞춰 기준을 확인한 뒤에 씁니다. 현지 시각 변환은 [시간대와 시각 설정](../system-account/time-zone.md) 을 봅니다.

기기가 정지해 있을 때 관찰이 늘고, 한 비콘이 2~4초 간격으로 기록된 예가 있습니다 [3]. 관찰 간격이 촘촘한 구간은 이동보다 머문 구간일 수 있어서 [위치 기록 데몬](routined.md) 의 위치 점과 함께 봅니다.

## 함정과 한계

모르는 비콘의 관찰 기록은 매우 빨리 지워지고 VACUUM 되며(글쓴이는 확보 장소에서 블루투스를 끈 경우를 예외로 들었습니다), 소유·공유 비콘 기록은 더 오래 남습니다 [3]. 그래서 모르는 추적기 관찰이 비어 있어도 주변에 추적기가 없었다고 볼 수 없습니다. WAL 파일에 본 DB 에 없는 기록이 더 있을 수 있어서 [3] DB 를 확보할 때 `-wal` 파일을 반드시 함께 가져옵니다. WAL 해석은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), 지운 행 복구는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

iOS 16.x 이상 검체에서 본 DB 는 암호화되어 있어서 [3] 파일을 확보해도 내용을 읽을 수 있는지는 수집 방식과 키체인 확보 여부에 달려 있습니다. 로컬 백업만 있으면 캐시와 DB 가 보이지 않고 plist 만 남습니다.

## 직접 분석해 보기

### 헥스로 확인하기

암호화된 DB 인지 먼저 가립니다. 헥스 편집기로 `Observations.db` 사본의 첫 16바이트를 보고, SQLite 머리 문자열이 보이지 않으면 암호화되었을 가능성이 큽니다. 머리 문자열과 머리 구조는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다. 이 판단은 파일이 평문 SQLite 인지 아닌지까지만 알려 주고, 복호화는 이 페이지에서 다루지 않습니다.

### 공개 도구로 읽기

평문으로 읽을 수 있는 경우 `sqlite3` 명령행 도구로 관찰 기록을 시간순으로 뽑습니다. 칸 이름은 검체에서 `.schema` 로 확인한 것으로 바꿔 씁니다.

```sql
.schema ObservedAdvertisement
SELECT *
FROM ObservedAdvertisement
ORDER BY 스캔_시각_칸;
```

로컬 백업이면 `Manifest.db` 의 `Files` 표에서 위 도메인들의 파일 목록을 뽑아 plist 를 꺼내고, `plutil` 같은 plist 도구로 키와 값을 확인합니다. `Files` 표의 칸은 `fileID`, `domain`, `relativePath`, `flags`, `file` 입니다.

```sql
SELECT fileID, domain, relativePath
FROM Files
WHERE domain LIKE '%findmy%' OR domain LIKE '%searchpartyd%'
   OR relativePath LIKE '%findmy%' OR relativePath LIKE '%searchpartyd%'
ORDER BY domain, relativePath;
```

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [위치 기록 데몬](routined.md) | 관찰 시각대에 기기가 있던 위치, `clients.plist` 의 나의 찾기 항목 |
| [블루투스 장치](../network/bluetooth.md) | 이 기기와 연결했던 블루투스 기기 |
| [알림 기록](../app-usage/notifications.md) | 원치 않는 추적기 알림이나 위치 공유 알림 |
| [메시지](../communications/messages/index.md) | 메시지에서 위치를 공유한 기록 |
| [애플 계정](../system-account/apple-account.md) | 나의 찾기가 묶인 계정 |
| [초기화와 복원 흔적](../system-account/erase-restore.md) | 원격 지우기·분실 모드 전후 상황 |

## 실습

공개 검체(NIST CFReDS 등)나 연습용 기기로 풀어 봅니다.

1. 검체의 iOS 버전은 무엇이고, `searchpartyd` 폴더의 DB 첫 부분에 SQLite 머리 문자열이 보입니까?
2. `fmipcore` 캐시가 있다면 `Devices.data` 에 기기가 몇 대 있고, 그중 이 기기 자신은 어느 것입니까?
3. 로컬 백업에서 `FMIPStateInfo.plist` 와 `com.apple.icloud.searchpartyd.plist` 를 꺼내 키 목록이 위 표와 같은지 비교합니다.
4. 연습용 기기에서 나의 iPhone 찾기를 껐다 켠 뒤 백업을 다시 떠서 `fmipActive` 값이 어떻게 바뀌는지 기록합니다.
5. `Observations.db` 를 읽을 수 있다면 한 비콘 UUID 의 관찰 간격이 정지 구간과 이동 구간에서 어떻게 다릅니까?

## 참고 문헌

1. Apple, "Location Services & Privacy" (2026-02-11) — https://www.apple.com/legal/privacy/data/en/location-services/
2. Forensafe, "iOS Find My" — https://www.forensafe.com/blogs/ios-find-my.html
3. The Binary Hick, "Further Observations – More on iOS Search Party" (2025-08-19) — https://thebinaryhick.blog/2025/08/19/further-observations-more-on-ios-search-party/
