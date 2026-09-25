---
title: "백업 폴더 구조"
parent: "로컬 백업"
grand_parent: "기반 · 백업 형식"
nav_order: 220
---

# 백업 폴더 구조 (Manifest.db·Info.plist·Status.plist)

로컬 백업 폴더 하나의 맨 위에는 plist 세 개와 SQLite 데이터베이스 하나가 있고, 백업한 파일 전체의 목록은 Manifest.db 에 들어 있습니다.

## 이 형식을 쓰는 아티팩트

컴퓨터에 만든 로컬 백업에서 꺼내는 아티팩트는 모두 이 폴더 구조를 거칩니다. 메시지 데이터베이스든 사파리 기록이든 백업 폴더 안에서 파일을 찾으려면 먼저 Manifest.db 에서 도메인과 경로로 항목을 찾고, 그 항목의 파일 이름(fileID)으로 실제 파일을 엽니다. 파일 이름을 만드는 규칙과 도메인은 [도메인과 파일 이름](domains-fileid.md) 에서 다룹니다.

백업 폴더가 컴퓨터 어디에 생기는지는 허브 [로컬 백업](index.md) 에 정리했습니다.

## 구조

### 최상위 파일

실제 백업 폴더 하나의 맨 위에서 본 파일은 아래 여섯 개입니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
Info.plist
Manifest.db
Manifest.db-shm
Manifest.db-wal
Manifest.plist
Status.plist
```

관찰한 백업은 Windows 의 Apple 기기 앱으로 만들었고 암호를 걸지 않았습니다. iOS 10 기기부터는 이 파일들 옆에 fileID 앞 두 글자로 이름 붙인 하위 폴더들이 함께 있습니다 [2](폴더를 나누는 방식은 [도메인과 파일 이름](domains-fileid.md) 참고).

| 파일 | 형식 | 담는 내용 |
|---|---|---|
| Info.plist | 일반 텍스트 plist | 기기 이름, 소프트웨어 버전, 설치한 앱, 일련번호 [2] |
| Manifest.plist | 이진 plist | 암호화 여부, 앱 목록, 백업 키백(BackupKeyBag) [2] |
| Status.plist | 이진 plist | 형식 버전, 백업 완료 상태, 백업 날짜, 전체 백업 여부 [2] |
| Manifest.db | SQLite | 백업 안 모든 파일의 목록 [2] |

### iOS 버전별 차이

Rich Infante 의 분석 [2] 은 백업 형식을 버전 번호로 나눕니다.

| 기기 iOS | 형식 버전(예) | 파일 목록 | 파일 배치 |
|---|---|---|---|
| iOS 9 기기 | 2.4 | Manifest.mbdb (이진 파일) | 모든 파일이 폴더 하나에 있음 |
| iOS 10·11 기기 | 3.2 | Manifest.db (SQLite) | fileID 앞 두 글자로 하위 폴더를 나눔 |

[2] 는 iOS 11 까지만 다뤘지만, 관찰한 iOS 27.0 백업도 Manifest.db 를 썼습니다(확인 범위: iPhone 13 mini, iOS 27.0). 그 사이 버전의 형식 버전 번호는 확인하지 못했으니 Status.plist 에서 직접 읽습니다.

### Info.plist 키

관찰한 백업의 Info.plist 에 있던 키 이름은 아래와 같습니다. 이름을 가린 키가 하나 더 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
Applications          Build Version         Device Name
Devices Version       Display Name          GUID
IMEI                  Installed Applications
Last Backup Date      MEID                  Product Name
Product Type          Product Version       Serial Number
Target Identifier     Target Type           Unique Identifier
Windows OS Version    iTunes Files          iTunes Settings
```

Windows 에서 만든 백업이라 Windows OS Version 키가 들어 있고, 맥에서 만든 백업에 어떤 키가 대신 들어가는지는 확인하지 못했습니다. IMEI·Serial Number·Unique Identifier 같은 식별자를 읽는 법은 [기기 식별자](../../value-decoding/device-identifiers.md) 에서 다룹니다.

### Manifest.plist 키

관찰한 백업의 Manifest.plist 에는 아래 키가 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
IsEncrypted
Version
Containers
Date
SystemDomainsVersion
WasPasscodeSet
Lockdown
Applications
BackupKeyBag
```

암호를 걸지 않은 백업인데도 BackupKeyBag 키가 있었습니다. IsEncrypted·BackupKeyBag, 그리고 암호 건 백업에만 생기는 키는 [암호 건 백업](encrypted-backup.md) 에서 다룹니다.

### Status.plist

관찰한 백업에는 Status.plist 파일이 있었지만 키 이름은 읽지 않았습니다. [2] 에 따르면 이 파일에는 형식 버전, 백업이 끝났는지를 나타내는 상태, 백업 날짜, 전체 백업인지가 들어 있습니다. 키 이름을 적은 글도 있으나 이번에 원문으로 확인하지 못해 여기에는 적지 않으며, 실제 파일을 열어 키를 직접 확인합니다.

### Manifest.db

관찰한 백업의 Manifest.db 스키마는 아래와 같습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```sql
CREATE TABLE Files (fileID TEXT PRIMARY KEY, domain TEXT, relativePath TEXT, flags INTEGER, file BLOB)
CREATE INDEX FilesRelativePathIdx ON Files(relativePath)
CREATE INDEX FilesFlagsIdx ON Files(flags)
CREATE TABLE Properties (key TEXT PRIMARY KEY, value BLOB)
CREATE INDEX FilesDomainsRelativePathIdx ON Files(domain, relativePath)
```

[2] 도 같은 두 표와 칸을 적었습니다.

| 칸 | 뜻 |
|---|---|
| Files.fileID | 백업 폴더 안 파일 이름. 도메인과 경로로 만든 해시 |
| Files.domain | 파일이 속한 영역 이름(예: HomeDomain) |
| Files.relativePath | 도메인 안에서의 상대 경로 |
| Files.flags | [2] 은 "Unix 파일 플래그" 라고 적음 |
| Files.file | [2] 은 "이진 plist 속성" 이라고 적음 |
| Properties.key / value | 이름과 값 한 쌍. 어떤 key 가 들어가는지는 확인하지 못함 |

flags 칸에는 1, 2, 4 같은 값이 나옵니다 [3]. 이 값을 파일·폴더·심볼릭 링크로 나누는 설명이 있지만 이번에 연 자료로는 확인하지 못했으니, 값의 뜻은 실제 항목과 맞춰 보고 씁니다. file 칸 BLOB 의 안쪽 구조와 그 안 시각 값의 기준도 연 자료([2][3])가 "이진 plist" 라고만 적어서 여기서는 다루지 않습니다. plist 를 읽는 방법은 [속성 목록 파일](../../data-formats/plist.md) 을 봅니다.

### 기기 안에 남는 백업 설정

백업 폴더와 따로, 기기 안에도 백업과 관련된 설정 파일이 남고 이 파일은 백업에도 들어옵니다. 관찰한 백업에서 본 파일과 최상위 키는 아래와 같습니다(확인 범위: iPhone 13 mini, iOS 27.0).

`HomeDomain` 의 `Library/Preferences/com.apple.MobileBackup.plist`

```
RemoteConfigurationExpiration     RestoreCloudFormatInfo
FetchMissingKeysAtNextUnlock      ForegroundRestorePerformance
NotifyDaemonNextTimeKeyBagIsUnlocked
BackupStateInfo                   PreflightSizing
AccountEnabledDate                RestoreStateInfo
SyncZoneFetched                   ServerRestrictedDomains
RestoreInfo                       RemoteConfiguration
FSEventState                      LocalSnapshotsDisabled
RemoteConfigurationBuildVersion   LastOnConditionEvents
AirTrafficFinishedRestoring
```

그 아래 하위 키로는 아래가 있었습니다.

| 키 | 하위 키 |
|---|---|
| BackupStateInfo | backupAttemptCount, date, errors, estimatedTimeRemaining, isBackground, isCloud, progress, state |
| RestoreInfo | BackupBuildVersion, DeviceBuildVersion, RestoreDate, WasCloudRestore |
| RestoreStateInfo | restoredSnapshotBackupPolicy, state 등 |
| PreflightSizing | 도메인 이름(DatabaseDomain, InstallDomain, MediaDomain, NetworkDomain, RootDomain 등)과 _TotalSize |

`RootDomain` 의 `Library/Preferences/com.apple.backupd.plist` 에는 CKPerBootTasks, CC_OncePerBootBackingData, CKStartupTime 키가 있었습니다.

이 키들이 아이클라우드 백업에만 쓰이는지 로컬 백업에도 쓰이는지, RestoreInfo 로 복원 시점을 알 수 있는지는 이번에 확인하지 못했습니다. 이름만 보고 "마지막 백업 시각" 이나 "복원한 날짜" 로 단정하지 않고, 값을 [초기화와 복원 흔적](../../../02-artifacts/system-account/erase-restore.md)·[아이클라우드 백업](../icloud-backup.md) 의 다른 기록과 맞춰 본 뒤에 씁니다.

## 읽는 법

1. 백업 폴더를 통째로 작업용 사본으로 복사합니다. Manifest.db 는 -shm·-wal 파일과 함께 옮깁니다.
2. Manifest.plist 의 IsEncrypted 를 먼저 봅니다. 암호 건 백업이면 Manifest.db 를 바로 열 수 없습니다([암호 건 백업](encrypted-backup.md) 참고).
3. Info.plist 로 어떤 기기의 백업인지(기종·iOS 버전·식별자)를 확인하고, Status.plist 로 백업이 끝났는지와 날짜를 확인합니다.
4. Manifest.db 의 Files 표에서 도메인과 상대 경로로 원하는 항목을 찾습니다.

```sql
-- 메시지 데이터베이스 항목 찾기
SELECT fileID, domain, relativePath, flags
FROM Files
WHERE domain = 'HomeDomain' AND relativePath = 'Library/SMS/sms.db';

-- 도메인별 항목 수
SELECT domain, COUNT(*) FROM Files GROUP BY domain ORDER BY 2 DESC;
```

5. 찾은 fileID 로 백업 폴더 안 파일을 엽니다. 파일 이름과 하위 폴더 규칙은 [도메인과 파일 이름](domains-fileid.md) 에 있습니다.

## 포렌식에서 중요한 점

관찰한 백업에는 Manifest.db 옆에 -shm·-wal 파일이 함께 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0). 백업이 끝난 뒤에도 늘 남는지, 언제 본 파일에 합쳐지는지는 확인하지 못했습니다. WAL 파일에는 본 데이터베이스에 아직 합쳐지지 않은 내용이 있을 수 있어 세 파일을 떼어 놓지 않고, 원본을 SQLite 도구로 직접 열지 않습니다. WAL 을 다루는 법은 [SQLite 데이터베이스](../../data-formats/sqlite/index.md) 에서 다룹니다.

Info.plist 와 Manifest.plist 에는 백업 폴더 안 파일 목록과 별개로 기기와 앱에 관한 정보가 들어 있어, 폴더 안 개별 파일을 열기 전에 어떤 기기의 백업인지와 암호가 걸렸는지를 먼저 판단할 수 있습니다.

## 함정

- 형식 버전과 기기 iOS 버전은 서로 다른 번호입니다. Status.plist 의 2.4·3.2 같은 값을 iOS 버전으로 읽지 않습니다.
- Last Backup Date 의 값 형식과 시간대는 이번에 확인하지 못했습니다. 보고서에 쓰기 전에 값의 형식과 시간대를 직접 확인하고, 시각 값을 읽는 법은 [시각 값](../../value-decoding/time-values.md) 을 봅니다.
- 백업 폴더 안 파일을 손으로 지우거나 옮기면 Manifest.db 목록과 실제 파일이 어긋납니다. Apple 은 백업 폴더를 직접 만지지 말고 Finder·Apple 기기 앱의 백업 관리 화면에서 지우거나 보관하도록 안내합니다 [1].
- 관찰한 키 목록은 Windows 에서 만든 암호 없는 백업 하나에서 본 것입니다. 맥에서 만든 백업이나 암호 건 백업에서는 키가 다를 수 있습니다.

## 도구

Manifest.db 는 sqlite3 명령줄 도구처럼 SQLite 를 여는 도구면 읽을 수 있고, plist 세 개는 Python 의 plistlib 처럼 텍스트와 이진 plist 를 모두 읽는 도구로 엽니다. [3] 은 R 로 Manifest.db 를 조회해 원하는 파일을 찾는 과정을 보여 줍니다. 도구마다 WAL 을 합치는지가 다르니 사본에서 작업합니다.

## 참고 문헌

1. Apple Support — Locate backups of your iPhone, iPad, and iPod touch (108809) — https://support.apple.com/en-us/108809
2. Rich Infante — Reverse Engineering the iOS Backup (2017-03-16) — https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup
3. rud.is — Trawling Through iOS Backups For Treasure (2019-06-02) — https://rud.is/b/2019/06/02/trawling-through-ios-backups-for-treasure-a-k-a-how-to-fish-for-target-files-in-ios-backups-with-r/
