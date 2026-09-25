---
title: "백업으로 수집"
parent: "모바일 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1190
---

# 백업으로 수집 (Backup Acquisition)

아이폰을 컴퓨터에 연결해 로컬 백업을 만들고, 만든 백업 폴더와 이미 컴퓨터에 남아 있던 백업을 찾아 증거로 확보하는 방법을 다룹니다.

## 언제 쓰나

로컬 백업은 아이폰 수집에서 가장 먼저 시도하는 방식입니다. 백업이 다른 방식과 견줘 무엇을 담고 빠뜨리는지, 암호화 백업을 만들지는 [수집 방식 비교](methods.md)에서 정하고 여기서는 절차와 결과물을 봅니다. 기기를 새로 백업하지 못하더라도 사용자가 쓰던 컴퓨터에 예전 백업이 남아 있을 수 있어서, 컴퓨터를 함께 확보했다면 그쪽도 찾습니다.

## 백업이 저장되는 곳

| 만든 곳 | 찾아 들어가는 위치 |
|---|---|
| macOS (Finder) | `~/Library/Application Support/MobileSync/Backup/` |
| Windows (Apple 기기 앱, Microsoft Store 판 iTunes) | `%USERPROFILE%` 에서 시작 |
| Windows (예전 iTunes) | `%AppData%` 에서 시작 |

Windows 에서는 찾아 들어갈 시작 폴더만 알려져 있어서, 그 아래 전체 경로는 검체에서 직접 확인합니다. Finder 나 Apple 기기 앱에서 백업을 오른쪽 클릭하면 삭제, 보관(Archive), 위치 보기를 할 수 있습니다. Windows 의 Apple 기기 앱으로 만든 백업은 Info.plist 에 `Windows OS Version` 키가 있습니다.

## 절차

1. 기기가 [압수와 보관](seizure-handling.md)의 조건대로 격리돼 있고 컴퓨터와 데이터 연결이 가능한지 확인합니다.
2. 수집용 컴퓨터에서 Finder 나 Apple 기기 앱으로 백업을 만들고, 암호화를 켰는지와 쓴 암호를 수집 기록에 적습니다.
3. 백업이 끝나면 백업 폴더 전체를 증거 저장소로 복사합니다. 최상위의 `Manifest.db` 옆에 `Manifest.db-shm` 과 `Manifest.db-wal` 이 함께 있으면 셋을 같이 옮깁니다.
4. 복사한 폴더의 해시를 남기고([결과물 형식과 해시](formats-hash.md)), 분석은 해시를 남긴 뒤 만든 사본으로 합니다.
5. 최상위 plist 로 기기와 백업 형식을 확인한 뒤(아래), `Manifest.db` 로 파일 목록을 읽어 들어갑니다.

## 백업 폴더 구조

백업 폴더의 최상위에는 아래 파일과, 해시 이름으로 된 하위 폴더들이 있습니다.

```
Info.plist
Manifest.db
Manifest.db-shm
Manifest.db-wal
Manifest.plist
Status.plist
```

백업 안 파일의 이름은 40자 SHA‑1 값이고, 파일 이름 앞 두 글자와 같은 이름의 하위 폴더에 나뉘어 들어갑니다(백업 형식 3.2, iOS 10 이후). 파일 이름은 `sha1(도메인 + "-" + 상대 경로)` 로 계산합니다. 파일 목록은 iOS 9 까지(형식 2.4)는 `Manifest.mbdb`, iOS 10 부터(형식 3.2)는 `Manifest.db` 에 들어 있고, `Status.plist` 의 `Version` 키가 이 형식 번호를 나타냅니다.

아래는 계산식대로 구한 예시입니다. 기기 쪽 백업 설정 파일의 도메인과 상대 경로를 이어 SHA‑1 을 구하면 백업 안에서 그 파일이 놓이는 이름과 하위 폴더를 알 수 있습니다.

```
입력 : HomeDomain-Library/Preferences/com.apple.mobile.ldbackup.plist
SHA-1: 2f771621fd3c627d0db75fe173f3dae8ce50e98b
위치 : 2f/2f771621fd3c627d0db75fe173f3dae8ce50e98b
```

백업 형식의 자세한 구조는 [로컬 백업](../../../01-foundations/backups/local-backup/index.md)에서 다룹니다.

## Manifest.db

`Manifest.db` 의 표와 색인은 다음과 같습니다.

```
CREATE TABLE Files (fileID TEXT PRIMARY KEY, domain TEXT, relativePath TEXT, flags INTEGER, file BLOB)
CREATE INDEX FilesRelativePathIdx ON Files(relativePath)
CREATE INDEX FilesFlagsIdx ON Files(flags)
CREATE TABLE Properties (key TEXT PRIMARY KEY, value BLOB)
CREATE INDEX FilesDomainsRelativePathIdx ON Files(domain, relativePath)
```

`Files` 표 한 행이 백업 안 파일 하나이고, `domain` 과 `relativePath` 로 원래 위치를 알 수 있습니다. `file` 칸에는 파일 속성을 담은 바이너리 plist 가 들어 있고, `flags` 는 유닉스 파일 플래그이고, 값마다의 뜻은 공개 자료가 없어 검체에서 확인해야 합니다. 이 DB 를 여는 법은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md)에서, `file` 칸의 plist 를 읽는 법은 [속성 목록 파일](../../../01-foundations/data-formats/plist.md)에서 다룹니다.

## Manifest.plist 와 Info.plist

`Manifest.plist` 는 백업의 암호화 여부와 키백(keybag)을 담고, `Info.plist` 는 기기 정보, 소프트웨어 버전, 설치 앱을 담습니다. 두 파일의 키 이름은 아래와 같습니다.

```
Manifest.plist
  IsEncrypted, Version, Containers, Date, SystemDomainsVersion,
  WasPasscodeSet, Lockdown, Applications, BackupKeyBag

Info.plist
  Applications, Build Version, Device Name, Devices Version, Display Name,
  GUID, IMEI, Installed Applications, Last Backup Date, MEID,
  Product Name, Product Type, Product Version, Serial Number,
  Target Identifier, Target Type, Unique Identifier, Windows OS Version,
  iTunes Files, iTunes Settings  (가린 키 1개 더 있음)
```

수집 직후에는 `Info.plist` 의 기종·iOS 버전·일련번호가 압수한 기기와 맞는지, `Manifest.plist` 의 `IsEncrypted` 가 수집 기록과 맞는지를 확인합니다. 암호화하지 않은 백업에는 `Manifest.plist` 에 `ManifestKey` 키가 없습니다. 식별자 값을 읽는 법은 [기기 식별자](../../../01-foundations/value-decoding/device-identifiers.md)와 [기기 정보](../../../02-artifacts/system-account/device-info.md)에서 다룹니다.

## 백업 안에서 먼저 볼 흔적

암호화하지 않은 백업에도 `KeychainDomain` 항목(예: 2개)이 들어 있을 수 있고, 그 안의 `keychain-backup.plist` 에는 `keybag-uuid`, `genp`, `inet`, `cert`, `keys` 키가 있습니다. 이 파일 내용을 풀어 읽을 수 있는지는 검체에서 확인하고, 키체인 구조는 [키체인](../../../01-foundations/storage/keychain.md)에서 다룹니다.

기기가 예전에 백업에서 복원된 적이 있는지는 수집한 자료의 출처를 판단할 때 중요합니다. 아래 두 plist 에 복원 관련 키가 있습니다.

```
HomeDomain :: Library/Preferences/com.apple.MobileBackup.plist
  RestoreInfo: {BackupBuildVersion, DeviceBuildVersion, RestoreDate, WasCloudRestore}
  RestoreStateInfo: {...}

HomeDomain :: Library/Preferences/com.apple.mobileSMS.plist
  IMDCKBackupControllerBackupDeviceStateKey: {..., IMDSavedDeviceStateDidMigrateKey,
    IMDSavedDeviceStateDidRestoreFromBackupKey,
    IMDSavedDeviceStateDidRestoreFromCloudBackupKey, ...}
```

키 이름으로 보면 복원 시각과 iCloud 에서 복원했는지를 가리키는 값으로 보이지만, 뜻을 밝힌 공식 설명은 없어서 다른 기록과 맞춰 해석합니다. 복원 흔적의 해석은 [초기화와 복원 흔적](../../../02-artifacts/system-account/erase-restore.md)에서 다룹니다. 이 밖에 백업 기능과 관련된 플러그인 도메인으로 `AppDomainPlugin-com.apple.MobileBackup.framework.DiagnosticExtension`, `…FollowUpUIExtension`, `…MBPrebuddyFollowUpExtension` 이 있습니다.

## 함정과 한계

암호화하지 않은 백업에는 암호화 백업에만 들어가는 영역이 빠지고, 어떤 영역인지는 [수집 방식 비교](methods.md)에 정리했습니다. 원본 백업 폴더를 분석 도구로 바로 열지 않는 까닭은 [결과물 형식과 해시](formats-hash.md)에서 다룹니다.

## 결과를 어떻게 해석하나

백업에서 찾은 파일은 "이 백업을 만든 시점에 기기에 있던 파일" 입니다. 백업 시각은 키 이름으로 보아 `Manifest.plist` 의 `Date` 와 `Info.plist` 의 `Last Backup Date` 에서 찾을 수 있고, 이 값의 시간대 표기는 [시각 값](../../../01-foundations/value-decoding/time-values.md)을 보고 확인합니다. 컴퓨터에서 찾은 예전 백업은 그 백업 시점의 상태를 보여 주므로, 지금 기기에서 지워진 자료가 남아 있을 수 있습니다. 여러 백업이 있으면 `Info.plist` 의 기기 정보로 같은 기기의 백업인지부터 확인합니다.

## 참고 문헌

- Locate and manage backups of your iPhone, iPad, and iPod touch — Apple Support — https://support.apple.com/en-us/108809
- About encrypted backups on your iPhone, iPad, or iPod touch — Apple Support — https://support.apple.com/en-us/108353
- Reverse Engineering the iOS Backup — Rich Infante (2017) — https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup
