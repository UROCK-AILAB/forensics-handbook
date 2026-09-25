---
title: "초기화와 복원 흔적"
parent: "아티팩트 · 시스템·계정"
nav_order: 320
---

# 초기화와 복원 흔적 (Erase·Restore)

## 한 줄 요약

아이폰을 초기화하면 이전 데이터는 읽을 수 없게 되지만, 초기화 뒤 첫 부팅과 설정 과정, 백업·다른 기기에서 데이터를 되살린 과정은 여러 plist·로그·DB 에 시각과 함께 남습니다.

## 무엇을 기록하나 · 왜 생기나

iOS 는 파일 시스템 키를 감싸는 키를 지울 수 있는 저장소 (Effaceable Storage) 에 두고, 이 키는 기밀성을 더하려는 것이 아니라 빨리 지우려고 있습니다[1]. 사용자가 "모든 콘텐츠 및 설정 지우기" 를 하거나 기기 관리(MDM)·Microsoft Exchange ActiveSync·iCloud 에서 원격 지우기 명령을 보내면 이 키를 지우고, 그 순간 모든 파일을 암호학적으로 읽을 수 없게 됩니다[1]. 키를 감싸는 키는 지울 때마다 바뀌고, A9 이후 칩에서는 Secure Enclave 가 엔트로피와 재사용 방지 (anti-replay) 장치로 지우기를 보장합니다[1]. 키 구조는 [데이터 보호](../../01-foundations/storage/data-protection/index.md) 에서 다룹니다.

이 설명대로라면 초기화 전 사용자 데이터는 복구할 대상이 아니고, 분석할 수 있는 것은 "초기화가 있었다" 는 흔적과 그 뒤 설정 과정의 흔적입니다(공식 문서를 바탕으로 한 해석입니다). 초기화된 기기가 처음 켜지면 설정 지원 (Setup Assistant, 내부 이름 Purple Buddy) 이 언어·국가 선택부터 복원 방법 선택까지 사용자를 이끄는데, 이 과정에서 설정 파일에 단계별 표시와 시각이 쌓입니다. 사용자가 새 기기로 설정하지 않고 iCloud 백업·컴퓨터 백업·다른 기기에서 데이터를 옮기면 복원 방법과 복원 시각을 담은 기록도 따로 생깁니다.

조사에서는 두 질문에 답하려고 이 흔적을 봅니다. 하나는 "기기를 언제 초기화했나" 이고, 다른 하나는 "지금 기기의 데이터가 어디서 왔나(새로 시작했나, 백업에서 되살렸나, 다른 기기에서 옮겼나)" 입니다. 증거 인멸을 의심하는 사건이면 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 와 함께 봅니다.

## 위치와 버전별 차이

흔적마다 볼 수 있는 추출 방식이 다릅니다. 아래 표의 "자료가 시험한 iOS" 는 참고 문헌 저자가 시험한 버전이고, 그 뒤 버전에서도 같은지는 확인하지 못했습니다. "로컬 백업" 칸은 실제 로컬 백업에서 파일과 키 이름이 보였는지만 적었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

| 흔적 | 기기 경로 | 자료가 시험한 iOS | 로컬 백업 |
|---|---|---|---|
| `.obliterated` | `/private/var/root/.obliterated` | 13.7·14.2[2] | 보이지 않음 |
| containermanagerd 로그 | `/private/var/root/Library/Logs/MobileContainerManager/containermanagerd.log.0` (`.1`, `.2`) | 13.7·14.2[2] | 보이지 않음 |
| 설정 지원 설정 | `/private/var/mobile/Library/Preferences/com.apple.purplebuddy.plist` | 13.7·14.2[2], 15.1·16.7.5[3] | HomeDomain `Library/Preferences/com.apple.purplebuddy.plist` |
| Lockdown 기록 | `/private/var/root/Library/Lockdown/data_ark.plist` | 버전 명시 없음(2021년 글)[4] | 보이지 않음 |
| 백업·복원 설정 | `*/Library/Preferences/com.apple.MobileBackup.plist`[3] | 15.1·16.7.5[3] | HomeDomain `Library/Preferences/com.apple.MobileBackup.plist` |
| 이전 설정 | `/private/var/mobile/Library/Preferences/com.apple.migration.plist` | 버전 명시 없음(2021년 글)[4] | 보이지 않음 |
| 사진 보관함 이전 기록 | `Photos.sqlite` 의 `ZMIGRATIONHISTORY` 표 | 15.1·16.7.5[3] | CameraRollDomain `Media/PhotoData/Photos.sqlite` 에 표가 있음 |
| OS 업데이트 기록 | `/private/var/mobile/MobileSoftwareUpdate/restore.log` | 버전 명시 없음(2021년 글)[5] | 보이지 않음 |

관찰한 로컬 백업에는 `.obliterated`, MobileContainerManager 로그, `data_ark.plist`, `restore.log` 가 나오지 않았습니다(확인 범위: iPhone 13 mini, iOS 27.0). 이 넷은 관찰 범위에서 보면 전체 파일 시스템 추출에서만 볼 수 있고, 추출 방식별 차이는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 와 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

## 구조

### 초기화 뒤 첫 부팅 — `.obliterated` 와 containermanagerd 로그

`/private/var/root/.obliterated` 는 초기화 뒤 기기가 부팅할 때 만들어지는 0바이트 파일이라서 내용은 없고 생성 시각만 뜻이 있습니다[2]. 모든 추출본에서 이 파일이 나오지는 않습니다[2].

`containermanagerd.log.0`·`.1`·`.2` 는 번호가 돌아가는 로그로, `.0` 이 가장 새 것이고 숫자가 클수록 오래된 것입니다[2]. 초기화 뒤 첫 부팅에서는 이 로그에 이전 OS 빌드 정보가 없다는 "Upgrade from NULL" 기록이 남습니다[2]. 초기화한 기기는 시간대가 미국 태평양 시간(UTC-8)으로 돌아가서 첫 부팅 직후 줄은 이 시간대로 찍히다가 설정 과정에서 기기 시간대로 바뀌고, 시간대가 바뀌는 지점을 직접 확인해야 합니다[2]. `/private/var/db/diagnostics/logd.0.log` 에 시간대 변경과 종료 기록이 있어 이 보정을 맞춰 볼 때 씁니다[2].

초기화 뒤 새로 만드는 DB 의 생성 시각도 참고가 되고, [2] 는 `/private/var/mobile/Library/AddressBook/AddressBook.sqlitedb` 와 `/private/var/mobile/Library/CallHistoryDB/CallHistory.storedata` 를 예로 듭니다. 이때는 생성 시각만 뜻이 있고, 수정 시각은 초기화와 관계없습니다[2].

### 설정 지원 — `com.apple.purplebuddy.plist`

설정 지원이 단계를 지나며 값을 적는 파일입니다. 관찰한 로컬 백업에서 확인한 키 가운데 초기화·복원과 관계있는 것은 아래와 같습니다(확인 범위: iPhone 13 mini, iOS 27.0). 파일 형식은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 을 봅니다.

| 키 | 형식 | 자료에서 밝힌 뜻 |
|---|---|---|
| `GuessedCountry` | list | 초기화 뒤 처음 성공적으로 부팅한 때, 곧 "국가 또는 지역 선택" 단계 무렵을 보여 줍니다[2]. [3] 은 설정을 처음 시작한 시각일 뿐 설정을 끝냈다는 뜻은 아니라고 봅니다[3] |
| `SetupLastExit` | datetime | [4] 는 설정 지원을 끝낸 시각으로 보고, [2] 는 사용자가 설정 화면에서 마지막으로 무언가 바꾼 시각을 반영해 믿기 어렵다고 봅니다[2][4] |
| `SetupState` | str | 설정 방법. "SetupUsingAssistant"(기기 간 이전 또는 로컬 백업), "RestoredFromCloudBackup"(iCloud 복원)[4], "RestoredFromDevice"(기기 간 이전)[3]. iCloud 복원 값을 [2] 는 "RestoredFromiCloudBackup" 으로 적어서 자료마다 표기가 다릅니다 |
| `lastPrepareLaunchSentinel` | list | 설정 완료 표시로 쓸 수 있습니다[3] |
| `SetupDone`, `SetupFinishedAllSteps`, `SetupVersion`, `RestoreChoice`, `RestoredMobileSyncSettings`, `setupMigratorVersion` | bool·int | 관찰만 했고, 뜻을 밝힌 자료는 찾지 못했습니다 |

`Language`, `Locale`, `UserChoseLanguage`, `PrivacyPresented`, `ScreenTimePresented`, `AutoUpdatePresented` 처럼 설정 화면을 보여 줬는지 적는 키도 함께 있습니다(확인 범위: iPhone 13 mini, iOS 27.0). 같은 계열로 `com.apple.SetupAssistant.plist`(`CKPerBootTasks`, `CKStartupTime`), `com.apple.setupassistant.privacypane.plist`(`HasSeenPrivacy`, `LastSeenPrivacyVersion`), `com.apple.keyboard.plist` 의 `BuddySetupDone` 도 보였지만(확인 범위: iPhone 13 mini, iOS 27.0), 이 키로 초기화·복원을 판단한 자료는 찾지 못했습니다.

### 첫 설정 완료와 복원 방법 — `data_ark.plist`

Lockdown 폴더의 `data_ark.plist` 에서 `FirstPurpleBuddyCompletion` 은 설정 지원을 처음 끝낸 시각이고 Unix 밀리초로 적습니다[4]. `com.apple.purplebuddy-SetupState` 와 `com.apple.purplebuddy-RestoreState` 는 복원 방법을 나타내며, 값으로 RestoredFromDevice(기기 간), RestoredFromiTunesBackup(컴퓨터 백업), RestoredFromiCloudBackup(iCloud 백업)이 나옵니다[4]. 컴퓨터 백업으로 복원했으면 그 백업을 만든 컴퓨터 이름도 남는다고 하지만[4], 어떤 키에 남는지는 확인하지 못했습니다. Lockdown 폴더의 다른 기록은 [기기 정보](device-info.md) 에서 다룹니다.

### 백업에서 복원한 기록 — `com.apple.MobileBackup.plist`

관찰한 로컬 백업에서는 HomeDomain `Library/Preferences/com.apple.MobileBackup.plist` 에 들어 있고, 복원과 관계있는 키는 아래와 같습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
RestoreInfo: {BackupBuildVersion, DeviceBuildVersion, RestoreDate, WasCloudRestore}
RestoreStateInfo: {backupAttemptCount, date, errors, estimatedTimeRemaining, isBackground, isCloud, progress, restoredSnapshotBackupPolicy, state}
RestoreCloudFormatInfo: {AccountType, LastForegroundRestoreFailureDate, RestoredFromFileList, SnapshotAccountType, SnapshotCommitID, SnapshotFormat, SnapshotFormatEnum, SnapshotID}
ForegroundRestorePerformance: {state-Annotating, state-Downloading, state-FindingRestorables, state-InstallingAppPlaceholders, state-RefreshCache, state-RestoringEntitlements, state-SynchronizeFileLists, state-Verifying}
AirTrafficFinishedRestoring (bool)
BackupStateInfo: {backupAttemptCount, date, errors, estimatedTimeRemaining, isBackground, isCloud, progress, state}
AccountEnabledDate (datetime)
```

`RestoreInfo` 에 복원 방법 정보가 들어 있고, 그 안의 `WasCloudRestore` 가 참이면 iCloud 복원입니다[3]. `BackupBuildVersion` 은 백업한 쪽 OS 빌드, `DeviceBuildVersion` 은 복원받은 기기의 빌드로 보이지만 이름에서 짐작한 것이고, `RestoreDate` 의 저장 형식도 확인하지 못했습니다.

기기 간 이전(빠른 시작)을 하면 `DeviceTransferInfo` 가 생기고, 그 안에 `FileTransferStartDate`, `SourceDeviceBuildVersion`, `SourceDeviceUDID`(원래 기기 식별자), `BuildVersion` 이 들어갑니다[3]. 관찰한 백업에는 `DeviceTransferInfo` 가 없었는데(확인 범위: iPhone 13 mini, iOS 27.0), 이 기기가 기기 간 이전을 하지 않아서인지 키 구성이 바뀌어서인지는 알 수 없습니다. 식별자 읽는 법은 [기기 식별자](../../01-foundations/value-decoding/device-identifiers.md) 에서 다룹니다.

### 다른 기기에서 옮긴 기록 — `com.apple.migration.plist` 와 `ZMIGRATIONHISTORY`

`com.apple.migration.plist` 에는 `RestoredBackupProductType`(원래 기기 모델 ID), `BackupDeviceUUID`(어디서 온 값인지 원문도 밝히지 못한 식별자), `Reason`(대상 기기 UDID 와 복원 일시)이 남습니다[4]. 관찰한 백업에는 이 파일이 없었고 대신 `AppDomain-com.apple.Migration` 도메인이 있었지만(확인 범위: iPhone 13 mini, iOS 27.0), 그 내용은 확인하지 못했습니다.

사진 보관함 DB 인 `Photos.sqlite` 의 `ZMIGRATIONHISTORY` 표도 이전 과정을 적습니다[3]. `ZMIGRATIONDATE` 는 이전 시각, `ZOSVERSION` 은 iOS 빌드이고, `ZORIGIN` 은 3 이면 다른 기기에서 온 데이터, 2 면 출처를 알 수 없는 이전이라고 저자가 제한된 시험을 바탕으로 적었습니다[3]. `ZSOURCEMODELVERSION` 은 비어 있는 행이 있고, 그 뜻은 자료에서 분명하지 않습니다. 관찰한 백업의 표에는 다음 칸이 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
Z_PK, Z_ENT, Z_OPT, ZCPLENABLED, ZFORCEREBUILDREASON, ZINDEX, ZMIGRATIONTYPE, ZMODELVERSION, ZORIGIN,
ZSOURCEMODELVERSION, ZINITIALSYNCDATE, ZMIGRATIONDATE, ZDEVICEUNIQUEID, ZFRAMEWORKUUID, ZHARDWAREMODEL,
ZOSVERSION, ZSTOREUUID, ZGLOBALKEYVALUES
```

[3] 의 저자는 시험을 두 번만 했으니 중요한 사건이면 직접 재현해 보라고 적었습니다[3]. 보관함 전체 구조는 [사진 보관함](../media/photos/index.md) 에서 다룹니다.

### OS 업데이트 기록 — `restore.log`

`restore.log` 에는 "data = " 뒤에 JSON 조각이 들어 있고, 칸은 `eventTime`(Unix 시각), `originalOSVersion`(이전 빌드), `currentOSVersion`(이후 빌드), `event`(대부분 "updateFinished"), `deviceClass`, `deviceModel`, `batteryIsCharging` 입니다[5]. 파일 이름에 restore 가 들어 있지만 업데이트 기록이고, 초기화도 기록하는지는 원문도 밝히지 않았습니다[5]. 관찰한 백업에는 이 파일이 없었고 RootDomain `Library/Preferences/com.apple.MobileSoftwareUpdate.plist` 는 키가 비어 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

### 관찰만 된 복원·이전 표시

아래 키는 이름으로 보아 복원·이전과 관계있어 보이지만, 해석한 자료를 찾지 못해 관찰 사실만 적습니다(확인 범위: iPhone 13 mini, iOS 27.0).

| 파일(HomeDomain) | 키 |
|---|---|
| `Library/Preferences/com.apple.imdsmsrecordstore.plist` | `IMDSavedDeviceState` 아래 `IMDSavedDeviceStateDateKey`, `IMDSavedDeviceStateDidMigrateFromDifferentDeviceKey`, `IMDSavedDeviceStateDidRestoreFromBackupKey`, `IMDSavedDeviceStateDidRestoreFromCloudBackupKey`, `IMDSavedDeviceStateDidUpgradeKey` 등 |
| `Library/Preferences/com.apple.mobileSMS.plist` | `IMDCKBackupControllerBackupDeviceStateKey` 아래 같은 하위 키 |
| `Library/Preferences/com.apple.appstored.plist` | `LastOSInstallDate`, `LastOSBuildVersion`, `PerformedPostRestoreUpdate`, `RestoreInstallsFailedWithCodeSigError` |
| `Library/Preferences/com.apple.accountsd.plist` | `LastMigrationSystemVersion`, `LastSystemVersion` |
| `Library/DeviceRegistry.state/GlobalState.plist` | `restoreTracker.identifier`, `restoreTracker.state` |
| `Library/Preferences/com.apple.icloud.findmydeviced.postwipe.plist` | 파일은 있지만 키가 없었습니다 |

`com.apple.icloud.findmydeviced.postwipe.plist` 는 이름으로 보아 원격 지우기와 관계있어 보이지만 확인하지 못했습니다. Safari 쪽에도 설정 지원 전용 웹 데이터 `AppDomain-com.apple.mobilesafari` `Library/WebKit/com.apple.purplebuddy/WebsiteData/ResourceLoadStatistics/observations.db` 가 있었지만(확인 범위: iPhone 13 mini, iOS 27.0), 해석 자료는 찾지 못했습니다.

## 증거로서 의미

**증명하는 것**

- `.obliterated` 가 있으면 그 생성 시각에 기기가 초기화 뒤 처음 부팅했다는 기록이 있습니다[2].
- containermanagerd 로그에서 이전 빌드 정보가 없는 부팅 기록이 나오면, 그 줄의 시각을 초기화 뒤 첫 부팅 시각의 근거로 씁니다[2].
- `SetupState`, `data_ark.plist` 의 복원 상태, `WasCloudRestore`, `ZMIGRATIONHISTORY` 의 `ZORIGIN` 은 지금 데이터가 새로 시작한 것인지, 백업이나 다른 기기에서 온 것인지 알려 줍니다[3][4].
- `DeviceTransferInfo` 의 `SourceDeviceUDID` 와 `com.apple.migration.plist` 의 `RestoredBackupProductType` 은 데이터를 넘겨준 기기를 가리킵니다[3][4].

**증명하지 못하는 것**

- 지우기를 누른 시각 자체는 알려 주지 않습니다. 남는 시각은 초기화 뒤 첫 부팅이나 설정 단계 시각입니다[2].
- 누가, 어떤 방법(직접·iCloud·MDM·Exchange)으로 지웠는지 구별하지 못합니다. 네 방법 모두 같은 키 삭제를 쓰고[1], 기기 안에서 방법을 구별하는 흔적은 확인하지 못했습니다. 원격 지우기 쪽은 [나의 찾기](../location/find-my.md), [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md), [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에서 기기 밖 기록과 맞춰 봅니다.
- 초기화 전에 어떤 데이터가 있었는지는 알려 주지 않고, 그 데이터를 되살릴 수도 없습니다[1].
- 초기화를 증거 인멸 목적으로 했다는 뜻은 담기지 않습니다. 보고서에는 "이 시각 무렵 초기화 뒤 첫 부팅 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

흔적마다 가리키는 순간이 다르고, 시간대도 다릅니다. 시각 형식 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

| 흔적 | 가리키는 순간 | 형식·시간대 |
|---|---|---|
| `.obliterated` 생성 시각 | 초기화 뒤 첫 부팅[2] | 파일 시스템 시각 |
| containermanagerd 로그 줄 | 초기화 뒤 첫 부팅[2] | 첫 부팅 무렵 UTC-8, 설정 뒤 기기 시간대[2] |
| `GuessedCountry` | 국가 또는 지역 선택 무렵[2] | [2] 는 기기 현지 시각으로 봄(원문 재확인 못 함) |
| `SetupLastExit` | 설정 지원 종료[4] 또는 설정 화면에서 마지막으로 바꾼 때[2] | plist 날짜형(기준은 확인하지 못함) |
| `FirstPurpleBuddyCompletion` | 설정 지원을 처음 끝낸 때[4] | Unix 밀리초[4] |
| `RestoreInfo` 의 `RestoreDate` | 복원(이름에서 짐작) | 확인하지 못함 |
| `ZMIGRATIONDATE` | 사진 보관함 이전[3] | [3] 은 UTC 로 적음. Mac 절대 시각인지는 확인하지 못함 |
| `restore.log` 의 `eventTime` | OS 업데이트 완료[5] | Unix 시각[5] |

`.obliterated` 와 containermanagerd 로그가 가리키는 순간은 지우기를 누른 때가 아니라 그 뒤 첫 부팅이라서[2], 보고서에는 "초기화 뒤 첫 부팅 시각" 으로 적습니다. 첫 부팅 무렵 기록이 UTC-8 로 찍힐 수 있어서[2], 시간대가 설정되기 전후의 줄을 섞어 읽지 않도록 [시간대와 시각 설정](time-zone.md) 기록과 `logd.0.log` 의 시간대 변경 기록으로 맞춰 봅니다[2].

## 함정과 한계

iCloud 백업으로 복원한 기기는 이전 기기의 설정값이 되살아나서 `GuessedCountry` 가 예전 초기화 날짜를 담고 있을 수 있고[2], 이 값 하나로 초기화 시각을 정하면 과거를 가리키는 날짜를 잘못 쓰게 됩니다. 이럴 때는 `.obliterated` 나 containermanagerd 로그처럼 복원으로 되살아나지 않는 흔적과 함께 봅니다.

`SetupLastExit` 는 자료마다 해석이 갈려서[2][4] 단독 근거로 쓰지 않습니다. `restore.log` 는 이름과 달리 업데이트 기록이라서[5] 초기화 기록으로 읽지 않습니다. `ZMIGRATIONHISTORY` 해석은 두 번의 시험에서 나온 것이라[3] 사건에 쓰려면 같은 iOS 버전 기기로 재현해 보는 편이 안전합니다.

로컬 백업만 확보한 경우에는 `.obliterated`, containermanagerd 로그, `data_ark.plist`, `restore.log` 를 볼 수 없었습니다(확인 범위: iPhone 13 mini, iOS 27.0). 백업 안의 `AddressBook.sqlitedb` 는 HomeDomain `Library/AddressBook/AddressBook.sqlitedb` 로 들어 있지만(확인 범위: iPhone 13 mini, iOS 27.0), 백업 파일의 생성 시각은 원본 기기의 생성 시각과 다를 수 있어서 [2] 의 생성 시각 방법을 백업에 그대로 쓸 수 있는지는 확인하지 못했습니다.

자료가 시험한 버전은 iOS 13.7·14.2[2], 15.1·16.7.5[3] 이고, iOS 17 이후에도 키의 뜻이 같은지는 확인하지 못했습니다. iOS 27.0 백업에서는 키 이름만 확인했습니다. 컴퓨터로 펌웨어를 다시 설치해 복원한 경우 위 흔적이 어떻게 달라지는지도 확인하지 못했습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 바이너리 plist 명세로 만든 예시이고, 실제 검체에서 나온 바이트가 아닙니다. 바이너리 plist 에서 13글자 ASCII 문자열 객체는 표시 바이트 `0x5D`(상위 4비트 `0101` = ASCII 문자열, 하위 4비트 `1101` = 길이 13) 뒤에 글자가 그대로 옵니다. `com.apple.purplebuddy.plist` 를 헥스 편집기로 열고 `SetupLastExit` 를 찾으면 이런 모양입니다.

```
5D 53 65 74 75 70 4C 61 73 74 45 78 69 74     ]SetupLastExit
```

키 문자열은 객체 표에 따로 있고, 값은 딕셔너리가 가리키는 다른 객체에 있습니다. 날짜 객체는 표시 바이트 `0x33` 뒤에 8바이트 값이 오며, 객체 표를 따라가 값을 찾는 법과 날짜 값을 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다. 헥스로 한 번 따라가 보면 도구가 이 키를 빠뜨리거나 다른 키 값과 섞었는지 확인할 수 있습니다.

### 공개 도구로 한 번

1. 로컬 백업이면 `Manifest.db` 에서 HomeDomain `Library/Preferences/com.apple.purplebuddy.plist` 와 `com.apple.MobileBackup.plist` 의 파일 해시 이름을 찾아 꺼냅니다. 백업 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 을 봅니다.
2. macOS 의 `plutil -p` 나 Python 표준 라이브러리 `plistlib` 로 두 파일을 열어 `GuessedCountry`, `SetupState`, `SetupLastExit`, `RestoreInfo` 를 확인합니다.
3. `sqlite3` 로 `Photos.sqlite` 를 열고 `ZMIGRATIONHISTORY` 의 `ZMIGRATIONDATE`, `ZORIGIN`, `ZSOURCEMODELVERSION`, `ZOSVERSION` 을 봅니다. DB 다루는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 를 봅니다.
4. 전체 파일 시스템 추출본이면 `.obliterated` 의 생성 시각, `containermanagerd.log.*`, `data_ark.plist`, `restore.log` 를 차례로 봅니다. iLEAPP 같은 공개 파서도 이 가운데 일부를 읽어 주고, `restore.log` 파서는 [5] 의 저자가 iLEAPP 용으로 만들었습니다[5]. 도구 결과는 위 2~3단계의 직접 확인과 맞춰 봅니다.

## 교차 검증

- [기기 정보](device-info.md) — 현재 OS 버전·빌드와 Lockdown 기록을 복원 기록의 빌드와 비교합니다.
- [로컬 백업](../../01-foundations/backups/local-backup/index.md) — `Info.plist` 의 `Last Backup Date`, `Product Version`, `Build Version` 과 `Manifest.plist` 의 `Date`, `WasPasscodeSet` 은 백업 시점의 기기 상태이고(확인 범위: iPhone 13 mini, iOS 27.0), 복원 날짜와 나란히 놓으면 순서를 맞출 수 있습니다.
- [아이클라우드 백업](../../01-foundations/backups/icloud-backup.md) — `com.apple.mobile.ldbackup.plist` 에 `LastCloudBackupDate`, `LastCloudBackupTZ`, `CloudBackupEnabled` 키가 있고(확인 범위: iPhone 13 mini, iOS 27.0), iCloud 복원이면 어떤 백업에서 왔는지 맞춰 봅니다.
- [연락처](../communications/contacts.md), [통화 기록](../communications/call-history.md) — 초기화 뒤 새로 만든 DB 의 생성 시각을 첫 부팅 시각과 비교합니다[2].
- [사진 보관함](../media/photos/index.md) — `ZMIGRATIONHISTORY` 와 사진 생성 시각의 앞뒤를 봅니다.
- [타임라인 작성](../../03-techniques/analysis/timeline/index.md) — 흔적마다 가리키는 순간이 달라서 시간대를 맞춘 뒤 한 줄로 늘어놓습니다.

## 실습

공개 검체(NIST CFReDS 등에 올라온 iOS 전체 파일 시스템 추출본이나 로컬 백업)를 골라 아래 질문을 풀어 봅니다. 검체마다 들어 있는 흔적이 다르니, 먼저 추출 방식부터 확인합니다.

1. 검체가 로컬 백업인지 전체 파일 시스템 추출본인지 확인하고, 위 표의 흔적 가운데 어떤 것을 볼 수 있는지 적습니다.
2. `com.apple.purplebuddy.plist` 의 `SetupState` 로 이 기기를 새로 설정했는지, 복원했는지, 다른 기기에서 옮겼는지 판단합니다.
3. `GuessedCountry` 시각과 `.obliterated` 생성 시각(있다면)을 비교하고, 둘이 다르면 어느 쪽을 초기화 뒤 첫 부팅 근거로 쓸지 이유와 함께 적습니다.
4. `Photos.sqlite` 의 `ZMIGRATIONHISTORY` 에서 `ZORIGIN` 이 3 인 행이 있는지 보고, `ZMIGRATIONDATE` 를 2번의 판단과 맞춰 봅니다.
5. 흔적마다 시간대를 밝혀 한 줄 타임라인으로 정리하고, 보고서 문장을 "이 시각 무렵 초기화 뒤 첫 부팅 기록이 있다" 의 형태로 써 봅니다.

## 참고 문헌

1. Data Protection in Apple devices — Apple Platform Security — https://support.apple.com/guide/security/data-protection-sece8608431d/web
2. Upgrade from Null: Detecting iOS Wipe Artifacts — Cellebrite — https://cellebrite.com/en/blog/upgrade-from-null-detecting-ios-wipe-artifacts/
3. Device Set-up – Transferring data to new iPhone & Effects to Photos.sqlite — The Forensic Scooter — https://theforensicscooter.com/2024/02/04/device-setup-transferring-data-to-new-iphone-effects-to-photos-sqlite/
4. iOS - Tracking Device Migration — D20 Forensics — https://blog.d204n6.com/2021/06/ios-tracking-device-migration.html
5. Restore Log - Tracking iOS Update History — stark4n6 — https://www.stark4n6.com/2021/10/restore-log-tracking-ios-update-history.html
