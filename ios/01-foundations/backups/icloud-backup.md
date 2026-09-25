---
title: "아이클라우드 백업"
parent: "기반 · 백업 형식"
nav_order: 250
---

# 아이클라우드 백업 (iCloud Backup)

## 한 줄 요약

아이클라우드 백업 (iCloud Backup)은 기기에 있는 정보 가운데 iCloud 로 따로 동기화하지 않는 부분을 Apple 서버에 복사해 두는 백업이고, 백업 본문은 서버에 있지만 기기 안에는 백업을 켰는지, 언제 백업하거나 복원했는지를 가리키는 설정 파일이 남습니다.

## 이 형식을 쓰는 아티팩트

Apple 은 iCloud 백업이 기기의 정보 가운데 이미 iCloud 로 동기화되지 않는 것을 복사한다고 설명합니다 [3]. 그래서 어떤 항목이 백업에 들어가는지는 사용자가 어떤 iCloud 동기화를 켰는지에 따라 달라집니다.

| 구분 | 항목 | 출처 |
|---|---|---|
| 들어감 | 기기 설정, 홈 화면 배치와 앱 정리, 내려받은 앱의 데이터(다른 회사 앱과 iCloud 로 동기화하지 않는 Apple 앱 포함), 구입한 벨소리, Visual Voicemail 암호, Apple Watch 백업(아이폰 백업 안에 들어감) | [3] |
| 조건부로 들어감 | 메시지(iMessage·SMS·MMS)는 "iCloud 에 메시지" 를 끈 경우에만, 사진·동영상과 "사람 및 반려동물" 얼굴 정보는 iCloud 사진을 끈 경우에만 들어감 | [3] |
| 기록만 들어감 | 구입한 음악·영화·앱·책은 파일 대신 구입 기록만 백업하고, 복원할 때 다시 내려받음 | [1][3] |
| 따로 암호화해 들어감 | 기기의 로컬 키체인 (아래 "키체인" 절) | [1] |
| 빠짐 | 이미 iCloud 에 동기화되는 데이터. Apple 은 연락처, 캘린더, 메모, 미리 알림, Mail, iCloud 사진, iCloud 에 메시지, iCloud Drive 파일, 건강 데이터, 음성 메모, Safari 책갈피와 방문 기록을 이 목록에 적음 | [3] |

"빠짐" 줄의 항목마다 "동기화를 켰을 때만 빠진다" 는 조건이 원문에 붙어 있는지는 확인하지 못해서, 사건마다 대상 계정의 동기화 설정과 함께 봐야 합니다. 앱별 저장 위치는 [메시지](../../02-artifacts/communications/messages/index.md), [사진 보관함](../../02-artifacts/media/photos/index.md), [건강 데이터](../../02-artifacts/health-wallet/health.md), [애플 워치 연결](../../02-artifacts/health-wallet/apple-watch.md) 페이지에서 다룹니다.

### 언제 만들어지나

Apple Platform Security Guide 는 iCloud 백업이 기기가 잠겨 있으면서 전원에 연결돼 있고 Wi-Fi 로 인터넷에 연결돼 있을 때만 이뤄진다고 설명합니다 [1]. 얼마나 자주 백업하는지는 이 페이지의 자료로 확인하지 못했습니다. iCloud 백업을 끄면 iCloud 에 있던 그 기기의 백업을 180일 동안 보관한 뒤 지웁니다 [3]. iCloud 백업을 쓰는 기기는 iPhone, iPad, Apple Vision Pro 입니다 [3].

## 구조

### 암호화 층

Apple Platform Security Guide 는 iCloud 백업의 암호화를 아래처럼 설명합니다 [1]. 위에서 아래로 갈수록 바깥쪽 층입니다.

| 층 | 무엇으로 보호하나 | 출처 |
|---|---|---|
| 파일 | 파일마다 따로 키가 있음 | [1] |
| 파일별 키 | "iCloud 백업 키백" 의 등급 키로 암호화함. 잠금 상태에서 쓸 수 없는 데이터 보호 등급에는 비대칭 키(Curve25519)를 씀 | [1] |
| iCloud 백업 키백 | 임의로 만든 키로 보호하고, 그 키도 백업 묶음과 함께 저장함 | [1] |
| 저장 | 전송 중에 암호화하고, 저장할 때는 계정 기반 키로 암호화함 | [1] |
| iCloud 백업 서비스 키 | 기본 상태에서는 Apple 데이터 센터의 iCloud 하드웨어 보안 모듈(HSM)에 백업해 둠 | [1] |

사용자의 iCloud 암호는 이 암호화에 쓰이지 않아서, iCloud 암호를 바꿔도 기존 백업은 그대로 쓸 수 있습니다 [1]. 데이터 보호 등급 자체는 [데이터 보호](../storage/data-protection/index.md) 페이지에서 설명합니다.

복원할 때는 백업 파일과 키백, 키백을 푸는 키를 Apple 계정에서 받아 키백을 풀고, 파일별 키로 파일을 푼 다음 새 파일로 쓰면서 파일마다 원래 데이터 보호 등급에 맞춰 다시 암호화합니다 [1].

### 키체인

백업 안의 키체인은 Secure Enclave 의 UID 루트 키에서 나온 키로 암호화합니다. 이 키는 기기마다 다르고 Apple 도 알지 못해서, 키체인은 원래 기기에만 복원할 수 있습니다 [1]. 키체인 구조는 [키체인](../storage/keychain.md) 페이지에서 다룹니다.

참고로 암호화하지 않은 로컬 백업에서는 `KeychainDomain :: keychain-backup.plist` 에 `keybag-uuid`, `genp`, `inet`, `cert`, `keys` 키가 있었습니다(확인 범위: iOS 27.0). iCloud 백업 안의 키체인이 같은 모양인지는 확인하지 못했습니다.

### 표준 데이터 보호와 고급 데이터 보호

고급 데이터 보호 (Advanced Data Protection, ADP)를 켜면 iCloud 백업을 다루는 방식이 바뀝니다.

| 항목 | 표준 데이터 보호 | 고급 데이터 보호 |
|---|---|---|
| iCloud 백업 | 전송 중과 서버에서 암호화하고, 키는 Apple 데이터 센터에 보관함 [2] | 종단 간 암호화하고, 키는 사용자가 신뢰하는 기기에만 있음 [2] |
| iCloud 백업 서비스 키 | iCloud HSM 에 백업해 둠 [1] | 종단 간 암호화해서 신뢰하는 기기에서만 쓸 수 있음 [1] |
| iCloud 에 메시지 | iCloud 백업을 끄면 종단 간 암호화이고, 백업을 켜면 백업 안에 "iCloud 에 메시지" 암호화 키 사본이 들어감 [2] | 늘 종단 간 암호화이고, 백업을 켜도 그 안의 메시지 키까지 종단 간 암호화함 [2] |

ADP 를 켜려면 iOS 16.2, iPadOS 16.2, macOS 13.1 이상이 필요합니다 [2]. ADP 를 켜도 iCloud Mail, 연락처, 캘린더, 일부 메타데이터(파일 체크섬, 수정 날짜 등)는 종단 간 암호화하지 않습니다 [2].

## 읽는 법

iCloud 백업 본문은 서버에 있어서 기기를 분석하는 쪽에서는 직접 열 수 없고, 계정 데이터를 요청하는 절차는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 페이지에서 다룹니다. 기기 쪽에서는 로컬 백업이나 전체 이미지 안의 설정 파일에서 iCloud 백업과 복원의 흔적을 찾습니다.

로컬 백업(Apple 기기 앱으로 만든 것, 암호화 안 함)에서 아래 파일과 키 이름을 확인했습니다(확인 범위: iOS 27.0). 값은 읽지 않았고, 오른쪽 칸의 뜻은 키 이름으로 짐작한 것이라 Apple 이 설명한 내용은 아닙니다.

| 파일 | 키 | 키 이름으로 본 짐작 |
|---|---|---|
| `HomeDomain :: Library/Preferences/com.apple.mobile.ldbackup.plist` | `CloudBackupEnabled`(bool), `LastCloudBackupDate`(int), `LastCloudBackupTZ`(str), `RequiresEncryption`(int), `WillEncrypt`(bool), `Version`(str) | iCloud 백업 사용 여부, 마지막 iCloud 백업 시각과 그때의 시간대 |
| `HomeDomain :: Library/Preferences/com.apple.MobileBackup.plist` | `BackupStateInfo`{`backupAttemptCount`, `date`, `errors`, `estimatedTimeRemaining`, `isBackground`, `isCloud`, `progress`, `state`} | 가장 최근 백업 시도의 상태, `isCloud` 는 iCloud 백업 여부 |
| 같은 파일 | `RestoreStateInfo`{`backupAttemptCount`, `date`, `errors`, `estimatedTimeRemaining`, `isBackground`, `isCloud`, `progress`, `restoredSnapshotBackupPolicy`, `state`} | 복원 진행 상태 |
| 같은 파일 | `RestoreInfo`{`BackupBuildVersion`, `DeviceBuildVersion`, `RestoreDate`, `WasCloudRestore`} | 복원한 시각, 백업을 만든 OS 빌드와 기기 빌드, iCloud 에서 복원했는지 |
| 같은 파일 | `RestoreCloudFormatInfo`{`AccountType`, `LastForegroundRestoreFailureDate`, `RestoredFromFileList`, `SnapshotAccountType`, `SnapshotCommitID`, `SnapshotFormat`, `SnapshotFormatEnum`, `SnapshotID`} | 복원에 쓴 iCloud 스냅숏의 식별자와 형식 |
| 같은 파일 | `ForegroundRestorePerformance`{`state-Annotating`, `state-Downloading`, `state-FindingRestorables`, `state-InstallingAppPlaceholders`, `state-RefreshCache`, `state-RestoringEntitlements`, `state-SynchronizeFileLists`, `state-Verifying`} | 복원 단계별 기록 |
| 같은 파일 | `PreflightSizing`{도메인 이름들, `_TotalSize`} | 백업 도메인별 크기 |
| 같은 파일 | `RemoteConfiguration`{`BackupPeriod`, `BackupWarningPeriod`, `BackupVerificationEnabled`, `RestoreVerificationEnabled`, `LocalSnapshotsDisabled`, `ServerRestrictedDomains` 등}, `RemoteConfigurationExpiration`(datetime), `RemoteConfigurationBuildVersion`(str) | 서버에서 내려받은 백업 설정 |
| 같은 파일 | `AccountEnabledDate`(datetime), `FetchMissingKeysAtNextUnlock`(bool), `NotifyDaemonNextTimeKeyBagIsUnlocked`(bool), `SyncZoneFetched`(bool), `FSEventState`{`dateCreated`, `eventDatabaseUUIDForVolumeUUID`, `eventId`}, `LastOnConditionEvents`(list), `AirTrafficFinishedRestoring`(bool) | 계정에서 백업을 켠 시각 등 |
| `RootDomain :: Library/Preferences/com.apple.backupd.plist` | `CKPerBootTasks`(list), `CC_OncePerBootBackingData`(bytes), `CKStartupTime`(int) | 뜻을 확인하지 못함 |
| `HomeDomain :: Library/Preferences/com.apple.mobileSMS.plist` | `IMDCKBackupControllerBackupDeviceStateKey`{`IMDSavedDeviceStateDidRestoreFromBackupKey`, `IMDSavedDeviceStateDidRestoreFromCloudBackupKey`, `IMDSavedDeviceStateDidMigrateKey`, `IMDSavedDeviceStateDidMigrateFromDifferentDeviceKey`, `IMDSavedDeviceStateDidUpgradeKey`, `IMDSavedDeviceStateBuildVersionKey`, `IMDSavedDeviceStateDateKey`, `IMDSavedDeviceStateIsMigratingKey`}, `IMDCKBackupControllerTimebombStartUserDefaultsKey`(datetime) | 메시지 앱이 본 백업 복원·기기 이전 상태 |

같은 로컬 백업의 도메인 목록에는 `AppDomainPlugin-com.apple.MobileBackup.framework.DiagnosticExtension`, `…FollowUpUIExtension`, `…MBPrebuddyFollowUpExtension` 처럼 백업 기능에 딸린 확장 컨테이너도 있었습니다(확인 범위: iOS 27.0). plist 를 여는 방법은 [속성 목록 파일](../data-formats/plist.md) 페이지를, 로컬 백업의 도메인 구조는 [로컬 백업](local-backup/index.md) 페이지를 봅니다.

## 포렌식에서 중요한 점

사용자가 iCloud 동기화를 켠 항목은 iCloud 백업이 아니라 iCloud 의 해당 서비스 쪽에 있습니다 [3]. 그래서 백업만 받아서는 연락처나 메모, 사진이 없을 수 있고, 이때 "기기에 그 데이터가 없었다" 고 쓰면 안 됩니다(이 해석은 [3]에서 끌어낸 것입니다).

표준 데이터 보호에서는 iCloud 백업 키가 Apple 쪽에 있어 법적 절차로 받을 여지가 있고, ADP 에서는 키가 사용자의 신뢰하는 기기에만 있습니다([1][2]에서 끌어낸 해석). 그래서 요청하기 전에 대상 계정이 ADP 를 켰는지부터 확인합니다. Apple 의 법 집행 대응 절차는 이 페이지에서 확인하지 못했습니다.

iCloud 백업을 끈 뒤에도 서버의 백업은 180일 동안 남아 있다가 지워집니다 [3]. 그래서 백업을 끈 지 180일이 지나지 않았다면 서버 쪽 사본이 아직 있을 수 있지만, 그보다 늦게 요청하면 사본이 이미 없을 수 있습니다([3]에서 끌어낸 해석).

`RestoreInfo` 와 `mobileSMS.plist` 의 복원·이전 키는 지금 기기가 다른 기기의 백업에서 복원됐는지 판단할 때 실마리가 됩니다. 복원한 기기에는 원래 기기에서 옮겨 온 데이터와 복원 뒤 새로 생긴 데이터가 섞여 있어서, 기록의 시각을 복원 시각과 나란히 놓고 봐야 합니다. 초기화와 복원 흔적 전체는 [초기화와 복원 흔적](../../02-artifacts/system-account/erase-restore.md) 페이지에서 다룹니다.

## 함정

위 표의 키 뜻은 모두 키 이름으로 짐작한 것이고 Apple 이 공개한 설명은 확인하지 못했습니다. 보고서에는 "`WasCloudRestore` 키가 있고 값이 참이다" 처럼 기록 그대로 쓰고, "iCloud 에서 복원했다" 는 다른 흔적과 맞아떨어질 때만 씁니다.

`LastCloudBackupDate` 는 정수형이지만(확인 범위: iOS 27.0) Unix 초인지 Mac 절대 시각인지 확인하지 못했습니다. 두 기준으로 모두 바꿔 보고 `LastCloudBackupTZ` 와 다른 시각 기록에 맞는 쪽을 고릅니다. 시각 기준은 [시각 값](../value-decoding/time-values.md) 페이지에서 설명합니다.

위 키 목록은 암호화하지 않은 로컬 백업 하나에서 본 것이라, iCloud 백업 본문이나 다른 iOS 버전에서 같은 키가 있다고 볼 근거는 없습니다.

### 버전별 차이

| iOS | 내용 | 출처 |
|---|---|---|
| 16.2 이상 | 고급 데이터 보호를 켜면 iCloud 백업을 종단 간 암호화할 수 있음 | [2] |
| 27.0 | `com.apple.MobileBackup.plist` 에 `SnapshotFormat`, `SnapshotFormatEnum` 키가 있음. 어떤 값이 들어가는지, 버전마다 바뀌는지는 확인하지 못함 | (확인 범위: iOS 27.0) |

iOS 15 이후 그 밖의 버전에서 iCloud 백업 구조가 바뀌었는지는 이 페이지의 자료로 확인하지 못했습니다.

## 도구

기기 쪽 흔적은 plist 라서 plist 를 여는 공개 도구라면 어느 것으로도 키와 값을 볼 수 있습니다. 서버에 있는 백업 본문을 받는 방법은 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md)와 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지에서 다룹니다.

## 함께 볼 페이지

- [로컬 백업](local-backup/index.md)
- [sysdiagnose 묶음](sysdiagnose.md)
- [애플 계정](../../02-artifacts/system-account/apple-account.md)
- [저장된 암호](../../02-artifacts/credentials-security/saved-passwords.md)

## 참고 문헌

1. Apple, "iCloud Backup security", Apple Platform Security. https://support.apple.com/guide/security/security-of-icloud-backup-sec2c21e7f49/web
2. Apple Support, "iCloud data security overview" (102651). https://support.apple.com/en-us/102651
3. Apple Support, "What does iCloud back up?" (108770). https://support.apple.com/en-us/108770
