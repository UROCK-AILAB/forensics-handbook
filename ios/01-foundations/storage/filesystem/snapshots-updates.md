---
title: "시스템 스냅숏과 업데이트"
parent: "iOS의 파일 시스템"
grand_parent: "기반 · 저장 구조"
nav_order: 30
---

# 시스템 스냅숏과 업데이트 (Snapshots·Updates)

iOS 는 서명된 시스템 볼륨을 APFS 스냅숏으로 운영하고 소프트웨어 업데이트 때 시스템 볼륨을 새로 준비하며, 기기가 언제 어느 버전으로 올라갔는지는 스냅숏 자체보다 Data 볼륨의 설정 파일에서 단서를 찾습니다.

## 이 구조를 쓰는 아티팩트

시스템 스냅숏은 사용자 데이터가 아니라 운영체제 쪽 구조입니다. 조사에서 스냅숏이 중요한 경우는 기기의 iOS 버전과 업데이트 이력이 쟁점일 때이고, 그때는 백업에도 들어오는 설정 파일(plist)의 버전 키를 함께 봅니다. 기기의 현재 버전·기종 같은 기본 정보는 [기기 정보](../../../02-artifacts/system-account/device-info.md) 에서, 초기화·복원 흔적은 [초기화와 복원 흔적](../../../02-artifacts/system-account/erase-restore.md) 에서 다룹니다.

## 구조

### 서명된 시스템 볼륨과 스냅숏

서명된 시스템 볼륨(SSV)은 APFS 스냅숏을 쓰고, 그래서 업데이트를 마칠 수 없으면 재설치 없이 이전 시스템 버전으로 돌아갈 수 있습니다 [1]. 소프트웨어 업데이트 때는 시스템 볼륨을 같은 방식으로 준비하고 해시를 다시 계산합니다 [1]. seal 과 서명 검사 자체는 [볼륨 구성](volumes.md) 에서 다룹니다.

APFS 스냅숏은 한 시점의 볼륨을 읽기 전용으로 담은 것이고, 마운트할 수 있으며 내용이 바뀌지 않습니다 [3]. 스냅숏이 있는 동안 현재 쓰이는 파일 시스템은 copy-on-write 로 새 블록에 쓰기 때문에, 스냅숏 이후에 바뀐 만큼 공간을 더 씁니다 [3].

### 루트 스냅숏의 이름

iOS 루트 파일 시스템(/)에는 시스템 볼륨의 스냅숏이 있고, 이름은 `com.apple.os.update-` 뒤에 해시가 붙는 형식이고, 버전에 따라 이름 끝이 다릅니다 [3].

| 예의 버전 | 이름 형식 [3] |
|---|---|
| iOS 15.0 | `com.apple.os.update-` + 해시 |
| iOS 18.3.2 | `com.apple.os.update-` + 해시 + `+restored_default_unsealed` 같은 표시 |

이 예는 가상 기기 서비스 Corellium 의 기기에서 나온 것이고 [3], 실제 아이폰에서도 같은 접미사가 붙는지는 기기에서 직접 확인해야 합니다. 이 스냅숏 명령은 연구용 가상 기기에서 쓰는 것이라 [3], 일반 수사에서 기기를 다루는 절차로 옮겨 쓰지 않습니다.

### Data 볼륨의 스냅숏

Data 볼륨에 스냅숏(예를 들어 로컬 백업용)이 남는지는 실제 기기로 확인해야 합니다. 백업의 `HomeDomain` :: `Library/Preferences/com.apple.MobileBackup.plist` 에는 `RemoteConfiguration` 아래에 `LocalSnapshotsDisabled` 라는 키가 있습니다. 키 이름만으로 Data 볼륨 스냅숏의 동작을 판단하지 않습니다.

## 읽는 법 — 업데이트 흔적이 남는 설정 파일

로컬 백업에는 볼륨과 스냅숏이 들어오지 않아서, 백업으로 업데이트 이력을 볼 때는 설정 파일의 키를 읽습니다. 아래 표는 백업에 들어 있는 키의 이름과 형식입니다. 값의 뜻은 이름만으로 단정하지 않습니다.

| 위치(도메인 :: 상대 경로) | 키(형식) |
|---|---|
| `WirelessDomain` :: `Library/Preferences/com.apple.libtu.timerscaling.firstbootafterupdate.plist` | `CurrentOSVersion`(문자열), `PrevOSVersion`(문자열), `BootSessionUUID`(문자열) |
| `HomeDomain` :: `Library/Preferences/com.apple.softwareupdateservices.ui.ios.plist` | `SUSUISoftwareUpdateOSVersion`(문자열), `SUSUIOSVersion`(문자열), `SUSUISoftwareUpdateState`(사전), `SUSUIState`(사전) |
| `HomeDomain` :: `Library/Preferences/com.apple.softwareupdateservices.security.plist` | `SUSUIFailedAttemptCountsWhileUnlocked`(정수) |
| `HomeDomain` :: `Library/Preferences/com.apple.softwareupdatesettings.plist` | `SUCachedScanResultsFingerprint`(문자열), `SUCachedScanResultsTTL`(날짜) |
| `RootDomain` :: `Library/Preferences/com.apple.NRD.UpdateBrainService.plist` | `LastStatusDate`(실수) |
| `RootDomain` :: `Library/Preferences/com.apple.MobileSoftwareUpdate.plist` | 파일은 있으나 키가 비어 있음 |
| `HomeDomain` :: `Library/Preferences/com.apple.appstored.plist` | `LastOSBuildVersion`(문자열), `PerformedPostRestoreUpdate`(참거짓), `RestoreInstallsFailedWithCodeSigError` |
| `HomeDomain` :: `Library/Preferences/com.apple.accountsd.plist` | `LastSystemVersion`(문자열) |
| `AppDomainGroup-group.com.apple.tipsnext` :: `tips-device-profile.plist` | `lastMajorOSVersionUpdateDate`(날짜) |

`SUSUISoftwareUpdateState` 아래에는 `SUSUISoftwareUpdateAlertFlow`, `SUSUISoftwareUpdateDownloadWasQueuedRemotely`, `SUSUISoftwareUpdateStateAlertRemindMeLaterCount`, `SUSUISoftwareUpdateStateInstallPolicyKey` 같은 하위 키가, `SUSUIState` 아래에는 `SUSUIAlertFlow`, `SUSUIStateAlertRemindMeLaterCount`, `SUSUIStateAlertRemindMeLaterCountSinceRequiringInstallation`, `SUSUIStateInstallPolicyKey` 같은 하위 키가 있습니다.

`firstbootafterupdate.plist` 의 `PrevOSVersion` 과 `CurrentOSVersion` 은 이름대로라면 업데이트 전후의 버전 쌍으로 보이지만, 이름만으로 단정할 수는 없습니다. 보고서에는 "이 파일의 `PrevOSVersion` 키 값이 무엇이었다" 처럼 기록 그대로만 적습니다.

백업에는 소프트웨어 업데이트 관련 확장 도메인 `AppDomainPlugin-com.apple.SoftwareUpdateServices.SUFollowUpRollbackDetectedExtension`, `AppDomainPlugin-com.apple.SoftwareUpdateServices.SUSFollowUpExtension`, `AppDomainPlugin-com.apple.SoftwareUpdateSettingsIntents` 도 있습니다. 이름에 "RollbackDetected" 가 들어 있다는 것만으로 롤백이 있었다고 단정하지 않습니다.

백업 폴더의 `Info.plist` 에는 `Build Version`, `Product Version`, `Last Backup Date` 키가 있어서 백업을 만든 시점의 버전을 설정 파일 속 버전 키와 견줘 볼 수 있습니다. 백업에서 복원한 기기인지 판단하는 키(`com.apple.MobileBackup.plist` 의 `RestoreInfo` 등)는 [초기화와 복원 흔적](../../../02-artifacts/system-account/erase-restore.md) 에서 다룹니다.

## 포렌식에서 중요한 점

시각이 들어 있는 키는 형식이 서로 다릅니다. `SUCachedScanResultsTTL` 과 `lastMajorOSVersionUpdateDate` 는 plist 날짜형이고, `LastStatusDate` 는 실수라서 Unix 시각인지 Mac 절대 시각인지 값을 보고 판별해야 합니다. 값의 기준을 정하는 방법은 [시각 값](../../value-decoding/time-values.md) 에서, plist 날짜형은 [속성 목록 파일](../../data-formats/plist.md) 에서 다룹니다.

업데이트 시각과 앱 사용 시각을 한 타임라인에 올릴 때는 한 파일의 값 하나로 업데이트 시각을 확정하지 않고, 버전 키가 있는 여러 파일을 함께 봅니다. 여러 파일의 버전 키와 시각을 맞춰 보는 방법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 함정

- **스냅숏 이름 예는 가상 기기 기준입니다.** `+restored_default_unsealed` 같은 접미사는 Corellium 기기의 예라서 [3], 실제 아이폰의 이름으로 인용하지 않습니다.
- **키 이름은 해석이 아닙니다.** 위 표는 키의 이름과 형식만 담았고, 값과 동작을 알려 주지 않습니다. 이름에 "Version", "Update" 가 들어 있다는 사실만으로 업데이트 시각이나 업데이트 여부를 단정하지 않습니다.
- **빈 파일도 기록입니다.** `com.apple.MobileSoftwareUpdate.plist` 는 키가 빈 채로 백업에 들어 있을 수 있습니다. 파일이 있다는 사실과 내용이 비어 있다는 사실을 따로 적습니다.
- **스냅숏을 건드리는 절차는 이 핸드북에서 다루지 않습니다.** 시스템 볼륨의 seal 과 스냅숏은 Apple 이 서명으로 보호하는 영역이고 [1], 이 페이지는 남은 흔적을 읽는 방법만 다룹니다.

## 참고 문헌

- [1] Signed system volume security — Apple Platform Security Guide. https://support.apple.com/guide/security/signed-system-volume-security-secd698747c9/web
- [3] iOS APFS Snapshots — Corellium Support Center. https://support.corellium.com/device-settings/ios-apfs-snapshots
