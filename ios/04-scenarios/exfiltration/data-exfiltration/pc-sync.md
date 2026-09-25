---
title: "PC 동기화로"
parent: "자료를 밖으로 보냈나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 1600
---

# PC 동기화로 (PC Sync)

아이폰을 컴퓨터에 연결해 백업이나 동기화로 자료를 옮겼는지 가리는 페이지입니다. 이 경로는 흔적이 주로 컴퓨터 쪽에 남고 기기 쪽 기록은 적어서, 컴퓨터에서 찾은 백업 폴더로 기기를 특정하는 흐름과 기기에 남는 설정 파일을 함께 다룹니다. 다른 유출 경로와 전체 흐름은 허브 [자료를 밖으로 보냈나 (Data Exfiltration)](index.md) 에 있습니다.

## 조사 질문

"이 아이폰의 자료가 어느 컴퓨터로 옮겨졌는가, 그 컴퓨터에 남은 백업이 이 아이폰의 것인가, 언제 만들어졌는가" 를 묻습니다. 컴퓨터를 확보했으면 백업 폴더가 가장 직접적인 근거이고, 기기만 있으면 기기 쪽 설정 파일로 백업·복원 이력을 가늠하는 데까지 답합니다.

## 먼저 확인할 것

처음 컴퓨터에 연결하면 기기에 "이 컴퓨터를 신뢰하겠습니까" 알림이 뜨고, 신뢰한 컴퓨터는 기기와 동기화하고 사진·비디오·연락처 같은 콘텐츠에 접근할 수 있습니다[1]. 암호가 설정된 기기는 신뢰하려면 잠금을 풀어야 하고, iOS 16 이상에서는 백업할 때도 이 알림이 뜨고, 자동 백업을 켜 두었으면 컴퓨터에 연결할 때마다 뜹니다[1]. 그래서 iOS 버전과 암호 설정 여부를 먼저 적어 두면, 연결 당시 기기를 쥔 사람이 잠금을 풀었어야 했는지를 판단하는 데 씁니다. 버전은 [기기 정보 (Device Info·Lockdown)](../../../02-artifacts/system-account/device-info.md), 암호 설정은 [암호와 Face ID 설정 흔적 (Passcode·Biometrics)](../../../02-artifacts/system-account/passcode-biometrics.md) 에서 봅니다.

로컬 백업을 만드는 도구는 Mac 에서는 Finder(macOS Mojave 이하는 iTunes), Windows 에서는 Apple 기기 앱 또는 iTunes 입니다[2]. 백업이 암호화되었는지는 도구의 기기 목록에 자물쇠 표시가 있는지, "로컬 백업 암호화" 가 체크되어 있는지로 확인합니다[2]. 암호화한 백업에만 들어가는 항목은 허브와 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md) 에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 컴퓨터의 백업 폴더 `Info.plist` | 어느 기기의 백업인지, 마지막 백업 날짜 | [기기 식별자 (UDID·ECID·일련번호)](../../../01-foundations/value-decoding/device-identifiers.md) |
| 2 | 백업 폴더 `Manifest.plist`·`Manifest.db` | 암호화 여부, 백업에 든 도메인과 파일 목록 | [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md) |
| 3 | 기기의 `com.apple.MobileBackup.plist` | 백업 상태와 복원 이력의 키 | [초기화와 복원 흔적 (Erase·Restore)](../../../02-artifacts/system-account/erase-restore.md) |
| 4 | 기기의 `com.apple.mobile.ldpair.plist` | 공개 자료 없음 | [설정 값 (Preferences)](../../../02-artifacts/system-account/preferences.md) |

### 컴퓨터에 남은 백업 폴더

Windows 의 Apple 기기 앱으로 만든 백업은 최상위에 `Info.plist`, `Manifest.db`(`-shm`·`-wal` 함께), `Manifest.plist`, `Status.plist` 파일이 있습니다. 두 plist 의 키는 아래와 같습니다.

| 파일 | 키 |
|---|---|
| `Info.plist` | Applications, Build Version, Device Name, Devices Version, Display Name, GUID, IMEI, Installed Applications, Last Backup Date, MEID, Product Name, Product Type, Product Version, Serial Number, Target Identifier, Target Type, Unique Identifier, Windows OS Version, iTunes Files, iTunes Settings, 이름을 가린 키 하나 |
| `Manifest.plist` | IsEncrypted, Version, Containers, Date, SystemDomainsVersion, WasPasscodeSet, Lockdown, Applications, BackupKeyBag |

`Info.plist` 의 Serial Number·Unique Identifier·Product Type·Product Version 을 조사 대상 기기의 값과 맞추면 이 백업이 그 기기의 것인지 가릴 수 있고, 식별자 읽는 법은 [기기 식별자 (UDID·ECID·일련번호)](../../../01-foundations/value-decoding/device-identifiers.md) 에 있습니다. Windows OS Version 키는 Windows 에서 만든 백업이라서 들어간 것으로 보입니다. Last Backup Date 와 `Manifest.plist` 의 Date 가 어떤 시각을 담는지, 어느 시간대 기준인지 밝힌 공개 자료가 없으니 원래 값을 함께 적습니다.

`Manifest.db` 의 Files 표에는 fileID, domain, relativePath, flags, file 칸이 있습니다. domain·relativePath 로 백업에 든 파일 목록을 뽑으면 이 백업으로 컴퓨터에 옮겨진 자료의 범위를 볼 수 있습니다.

```sql
SELECT domain, relativePath, flags FROM Files ORDER BY domain, relativePath;
```

컴퓨터 쪽 페어링 기록(lockdown 폴더)의 위치와 형식은 그 운영체제의 포렌식 자료를 따릅니다. 사진 앱으로 사진을 PC 로 가져간 흔적이 기기에 남는지는 공개 자료가 없어 검체로 확인해야 합니다.

### 기기에 남는 설정 파일

기기 쪽에서는 `HomeDomain :: Library/Preferences/com.apple.MobileBackup.plist` 를 봅니다. 이 파일의 BackupStateInfo 에는 date, isCloud, state, progress, errors, backupAttemptCount 같은 하위 키가 있고, RestoreInfo 에는 BackupBuildVersion, DeviceBuildVersion, RestoreDate, WasCloudRestore 가 있습니다. 로컬 백업을 했을 때도 BackupStateInfo 에 기록이 남는지는 검체에서 확인합니다. RestoreInfo 는 이 기기가 백업에서 복원된 이력을 보여 주고, 해석은 [초기화와 복원 흔적 (Erase·Restore)](../../../02-artifacts/system-account/erase-restore.md) 을 따릅니다.

`HomeDomain :: Library/Preferences/com.apple.mobile.ldpair.plist` 에는 실수형 키 하나가 있습니다. 파일 이름이 페어링을 떠올리게 하지만 무엇을 기록하는지 밝힌 공개 자료가 없습니다.

## 분석 흐름

1. 조사 대상 기기의 iOS 버전, 암호 설정 여부, 일련번호·UDID 를 적습니다.
2. 확보한 컴퓨터에서 로컬 백업 폴더를 찾고, 폴더마다 `Info.plist` 의 식별자를 기기 값과 맞춰 이 기기의 백업을 고릅니다. 백업 폴더 위치는 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md) 을 따릅니다.
3. 고른 백업의 `Info.plist` Last Backup Date 와 `Manifest.plist` 의 Date·IsEncrypted·WasPasscodeSet 을 원래 값 그대로 적습니다.
4. `Manifest.db` 의 Files 표로 백업에 든 도메인과 파일 목록을 뽑고, 유출이 의심되는 자료가 든 도메인(사진, 메시지, 앱 도메인 등)이 들어 있는지 봅니다.
5. 기기 쪽 `com.apple.MobileBackup.plist` 의 BackupStateInfo·RestoreInfo 를 적습니다.
6. 찾은 시각을 컴퓨터 쪽 파일 시스템 시각과 함께 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) 에 올립니다.

## 흔한 오판

컴퓨터에 이 기기의 백업이 있다는 사실은 기기 자료가 그 컴퓨터로 복사된 적이 있다는 뜻이지만, 그 컴퓨터를 쓴 사람이 누구인지는 따로 입증합니다.

신뢰한 컴퓨터 목록은 설정 → 일반 → 전송 또는 재설정 → 재설정 → "위치 및 개인정보 보호 재설정" 으로 지울 수 있습니다[1]. 그래서 기기에 신뢰 관계가 보이지 않아도 컴퓨터에 연결한 적이 없다고 쓰지 않습니다. 이 재설정이 기기에 흔적을 남기는지는 공개 자료가 없어 검체로 확인해야 합니다.

암호화하지 않은 백업과 암호화한 백업은 담긴 항목이 다릅니다[2]. 백업에 어떤 자료가 없다고 해서 그 자료를 옮기지 않았다고 쓰기 전에 `Manifest.plist` 의 IsEncrypted 부터 확인합니다.

## 보고서 문장 예

> 확보한 컴퓨터의 로컬 백업 폴더 ○○에 있는 `Info.plist` 의 Serial Number·Unique Identifier 가 조사 대상 기기의 값과 같고, Last Backup Date 값은 ○○입니다. 이 값의 시간대 기준은 확인하지 못해서 원래 값을 함께 적습니다.

> 같은 백업의 `Manifest.db` Files 표에 도메인 ○○의 파일이 ○○개 들어 있습니다. 이 기록은 해당 자료가 백업을 통해 이 컴퓨터에 복사되었음을 보여 주며, 컴퓨터를 사용한 사람은 이 기록으로 알 수 없습니다.

## 함께 볼 페이지

- [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)
- [기기 정보 (Device Info·Lockdown)](../../../02-artifacts/system-account/device-info.md)
- [메신저로 (Messenger)](messenger.md), [클라우드로 (Cloud)](cloud.md), [메일로 (Email)](email.md), [에어드롭으로 (AirDrop)](airdrop.md)
- [증거를 없애려 했나 (Anti-Forensics)](../../activity/anti-forensics/index.md)

## 참고 문헌

1. Apple 지원 문서 109054, "About the 'Trust This Computer' alert" — https://support.apple.com/en-us/109054
2. Apple 지원 문서 108353, "About encrypted backups on your iPhone, iPad, or iPod touch" — https://support.apple.com/en-us/108353
