---
title: "기기 백업"
parent: "아이폰·아이패드 연결"
grand_parent: "아티팩트 · 외부 장치"
nav_order: 1110
---

# 기기 백업 (MobileSync)

기기 백업 (MobileSync Backup)은 아이폰·아이패드를 맥에 백업할 때 사용자 홈의 `~/Library/Application Support/MobileSync/Backup/` 아래에 기기별 폴더로 남는 사본이고, 기기 식별값과 마지막 백업 시점, 설치된 앱 목록뿐만 아니라 기기에서 옮겨 온 파일까지 담깁니다.

## 무엇을 기록하나 · 왜 생기나

맥에서 기기를 백업하면 `Backup/` 아래에 기기 UDID 이름의 폴더가 기기마다 하나 생기고, 그 안에 `Info.plist`, `Status.plist`, `Manifest.plist` 가 놓입니다 [2]. `Info.plist` 에는 기기 정보와 설치된 앱 목록이, `Manifest.db` 에는 백업한 파일과 기기 안 원래 경로의 대응이 들어가고 [2][3], 파일 내용은 같은 폴더 아래 하위 폴더에 따로 저장됩니다 [4].

맥에서는 Finder에서 기기를 고른 뒤 일반 탭의 백업 관리로 백업을 다루고, 이 화면에서 백업을 지우거나 보관(Archive)하거나 Finder에서 위치를 열 수 있습니다 [1]. Apple Devices 앱은 윈도우 PC에서 쓰는 앱입니다 [1]. 보관하면 별도 사본 폴더가 생깁니다.

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 위치 | `~/Library/Application Support/MobileSync/Backup/` [1] |
| 기기별 폴더 | `Backup/` 아래 기기 UDID 이름의 폴더 [2] |
| 범위 | 사용자 홈 아래라서 사용자 계정마다 따로 있음 [1] |
| 관리 화면 | Finder → 기기 선택 → 일반 → 백업 관리 [1] |
| macOS 버전 | 10.15 Catalina 이후 Finder, 10.14 Mojave 이전 iTunes [6] |

macOS 10.15 Catalina 이후에는 Finder로, 10.14 Mojave 이전에는 iTunes로 백업하고 [6], 백업 위치는 위 경로 하나입니다 [1]. 윈도우에서는 Apple Devices 앱과 Microsoft Store판 iTunes가 `%USERPROFILE%` 아래에, 예전 iTunes가 `%AppData%` 아래에 백업을 둡니다 [1].

## 구조

아래는 폴더 구성을 명세로 만든 예시이고, 특정 기기에서 나온 이름이 아닙니다.

```
~/Library/Application Support/MobileSync/Backup/
└── <UDID>/
    ├── Info.plist
    ├── Status.plist
    ├── Manifest.plist
    ├── Manifest.db
    └── <fileID 앞 두 글자>/
        └── <fileID>
```

### Info.plist

`Info.plist` 의 키 이름은 아래와 같습니다 [2]. 묶음은 키 이름을 기준으로 나눈 것입니다.

| 묶음 | 키 |
|---|---|
| 기기 식별 | `Unique Identifier`, `Target Identifier`, `Target Type`, `GUID`, `Serial Number`, `IMEI`, `MEID`, `ICCID`, `Phone Number` |
| 기기 이름·모델·OS | `Device Name`, `Display Name`, `Product Type`, `Product Version`, `Build Version` |
| 백업 | `Last Backup Date`, `iTunes Version`, `iTunes Settings`, `iTunes Files`, `iBooks Data 2` |
| 앱 | `Installed Applications`, `Applications` |

`Info.plist` 에 든 설치 앱 목록은 기기에 어떤 앱이 있었는지 확인하는 데 쓰이고, 공개 도구 MVT도 이 목록을 뽑아 냅니다 [3][2].

### Status.plist와 Manifest.plist

`Status.plist` 의 `SnapshotState` 값이 `finished` 면 백업이 끝까지 완료된 것입니다 [2]. 이 파일에 `IsFullBackup`, `Date`, `UUID`, `Version`, `BackupState` 같은 키가 더 있다는 설명도 있습니다.

`Manifest.plist` 의 `IsEncrypted` 는 백업이 암호화됐는지를 알려 주고 [2], 암호화 백업이면 `BackupKeyBag` 과 `ManifestKey` 가 함께 들어갑니다 [4]. `ManifestKey` 는 앞 4바이트 보호 클래스 값(리틀 엔디언 정수) 뒤에 키 자료가 이어지는 구조이고, 암호화 백업에서는 `Manifest.db` 도 이 키로 암호화돼 있어서 풀기 전에는 SQLite로 열리지 않습니다 [4]. 기기 쪽에서 백업 암호화가 켜져 있는지는 lockdown 도메인 `com.apple.mobile.backup` 의 `WillEncrypt` 키로 조회합니다 [2].

### Manifest.db

`Manifest.db` 는 SQLite 데이터베이스이고(암호화 백업은 복호화한 뒤), 백업한 파일을 기기의 원래 경로와 이어 줍니다 [3][4]. `Files` 표의 열은 다음과 같습니다 [4].

| 열 | 내용 |
|---|---|
| `fileID` | 백업 폴더 안에 저장된 실제 파일의 이름. 16진수 소문자 40글자 [4] |
| `domain`, `relativePath` | 기기 안 원래 위치를 나타내는 두 값 [3] |
| `flags` | `1` 이면 일반 파일(공개 도구가 파일을 꺼낼 때 쓰는 조건). 다른 값의 뜻은 공개 자료 없음 |
| `file` | NSKeyedArchiver 형식의 바이너리 plist로 된 파일 메타데이터. `EncryptionKey`(암호화 백업), `ProtectionClass`, `Size`, `LastModified` 등이 들어감 [4] |

실제 파일은 백업 폴더 아래 `fileID` 앞 두 글자 이름의 하위 폴더에 `fileID` 이름으로 저장됩니다 [4]. SQLite를 읽는 방법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에, plist를 읽는 방법은 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에 있습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 맥의 해당 사용자 홈에 그 기기(UDID·일련번호·IMEI·기기 이름)의 백업이 있다는 것 [2][1] | 백업을 실행한 사람이 누구인지 |
| `Last Backup Date` 에 적힌 마지막 백업 시점 [2][1] | 첫 백업 시점이나 백업한 횟수 |
| `SnapshotState` 가 `finished` 면 그 백업이 끝까지 완료됐다는 것 [2] | 백업 이후 기기에서 일어난 일 |
| 백업 시점에 기기에 설치돼 있던 앱 목록 [2][3] | 기기를 쓴 사람이 맥 계정 주인과 같은 사람이라는 것 |
| 백업한 파일과 기기 안 원래 경로의 대응 [3] | |

보고서에는 "이 계정 홈에 이 기기의 백업이 있고, 마지막 백업 시점이 ○○로 기록돼 있다" 처럼 기록으로 확인되는 만큼만 씁니다. 계정과 사람을 잇는 방법은 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)에서 다룹니다.

## 시각 해석

마지막 백업 시점은 `Info.plist` 의 `Last Backup Date` 로 확인합니다 [2][1]. libimobiledevice는 백업할 때 호스트 시계의 현재 시각을 plist 날짜형으로 이 키에 적고 [2], plist 날짜형은 시간대 없이 UTC 기준으로 저장되므로 값은 기기가 아니라 백업한 컴퓨터의 시계를 따릅니다. Finder로 만든 백업도 같은 방식인지는 실제 백업으로 확인합니다. `Manifest.db` 의 `file` 열 안에 든 `LastModified` 는 유닉스 초 값이고 [4], 기기 안 파일의 수정 시각이지 백업 시각이 아닙니다. 도구가 보여 주는 날짜를 그대로 옮기지 말고 원본 값의 형식과 기준 시간대를 확인한 뒤 보고서에 적고, 값을 푸는 방법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에, 맥의 시간대 설정은 [시간대와 시계 설정 (Time Zone·NTP)](../../system-account/time-zone.md)에 있습니다.

## 함정과 한계

백업을 열기 전에 `Manifest.plist` 의 `IsEncrypted` 값부터 확인하고 [2], 암호화된 백업이면 [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md)를 따릅니다.

백업 관리 화면에서 백업을 지울 수 있어서 [1], 백업 폴더가 없다는 사실만으로 백업한 적이 없다고 말하지 않습니다. 지운 폴더의 흔적은 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)와 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)로 찾아봅니다. 보관한 백업은 별도 사본 폴더로 남으니 [1], `Backup/` 아래에 UDID가 아닌 이름의 폴더가 있으면 안의 `Info.plist` 를 열어 어느 기기의 백업인지 확인합니다.

백업은 사용자 홈마다 따로 있어서 [1], 맥에 계정이 여러 개라면 모든 홈을 봅니다. 계정 목록은 [사용자 계정 (Local Accounts)](../../system-account/user-accounts/index.md)에서 확인합니다.

`fileID` 는 16진수 40글자로 SHA-1 값의 길이와 같고 [4], `domain` 과 `relativePath` 를 이은 문자열의 SHA-1이라는 설명이 있습니다. 두 글자 하위 폴더 구조와 `Manifest.db` 가 iOS 10부터 예전 `Manifest.mbdb` 를 대신했다는 설명도 있습니다. 오래된 백업을 만나면 이 페이지의 구조를 전제하지 말고 폴더 구성부터 확인합니다. `flags` 의 `1` 이외 값은 뜻을 밝힌 공개 자료가 없으니, 도구가 이 값을 어떻게 걸러 내는지는 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)의 방법으로 확인합니다.

## 직접 분석해 보기

헥스로 볼 때는 `Manifest.plist` 의 `ManifestKey` 값을 따라가 봅니다. 앞 4바이트가 보호 클래스 값(리틀 엔디언 부호 있는 정수)이고, 그 뒤로 키 자료가 이어집니다 [4]. `Manifest.db` 는 헥스로 열어 첫 바이트가 SQLite 파일 머리인지 확인하는데, 암호화 백업이라면 머리가 보이지 않는 것이 정상입니다 [4]. 머리 구조는 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

암호화하지 않은 백업이라면 SQLite 도구로 `Files` 표를 읽어 원래 경로와 저장 위치를 이어 볼 수 있습니다 [4].

```sql
-- 일반 파일(flags = 1)의 원래 위치와 저장 이름
SELECT fileID, domain, relativePath
FROM Files
WHERE flags = 1;
```

결과의 `fileID` 로 `<fileID 앞 두 글자>/<fileID>` 파일을 찾으면 그 원래 경로의 파일 사본입니다 [4]. 공개 도구로는 MVT가 백업에서 설치 앱 목록 같은 기록을 뽑아 내고 [3], iphone_backup_decrypt는 `Manifest.plist` 의 `BackupKeyBag`·`ManifestKey` 와 `Files` 표를 읽습니다 [4]. 어느 도구를 쓰든 결과 몇 건을 위 방법으로 직접 맞춰 봅니다.

## 교차 검증

`Info.plist` 의 `Unique Identifier`·`Target Identifier` 에 든 UDID를 `/var/db/lockdown` 의 `<UDID>.plist` 파일 이름과 대조하면 페어링과 백업을 같은 기기로 묶을 수 있습니다 [5][2]. libimobiledevice는 `Unique Identifier` 에 UDID를 대문자로 바꿔 적고 `Target Identifier` 에는 받은 그대로 적으므로 [2], 대소문자를 가리지 않고 비교합니다. 백업 폴더 이름도 같은 UDID라서 함께 맞춰 봅니다 [2]. 페어링 기록은 맥 전체에 하나이고 백업은 사용자마다 따로라서 [1], 페어링 기록이 있는 기기가 어느 계정 홈에 백업됐는지를 보면 계정까지 좁힐 수 있습니다. 페어링 기록의 구조는 [페어링 기록 (Lockdown)](lockdown.md)에 있고, 백업 시점을 다른 기록과 한 시간축에 놓을 때는 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)을 봅니다.

## 실습

NIST CFReDS 같은 공개 시험 자료 가운데 iOS 기기를 백업한 흔적이 있는 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 각 사용자 홈의 `MobileSync/Backup/` 아래에 백업 폴더가 몇 개 있나요? 폴더 이름과 `Info.plist` 의 UDID가 모두 같나요?
2. `Status.plist` 의 `SnapshotState` 가 `finished` 가 아닌 백업이 있나요? 있다면 보고서에서 그 백업을 어떻게 설명하겠습니까?
3. `Manifest.plist` 의 `IsEncrypted` 값은 무엇인가요? 암호화하지 않은 백업이라면 `Files` 표에서 `flags` 가 `1` 인 행을 몇 개 골라 실제 파일 위치를 찾아보세요.
4. `Last Backup Date` 를 도구 두 가지로 읽어 같은 시각이 나오는지, 시간대 표시가 어떻게 다른지 비교해 보세요.

## 참고 문헌

1. Apple Support — Locate backups of your iPhone, iPad, and iPod touch — https://support.apple.com/en-us/108809
2. libimobiledevice 소스 tools/idevicebackup2.c — https://raw.githubusercontent.com/libimobiledevice/libimobiledevice/master/tools/idevicebackup2.c
3. MVT(Mobile Verification Toolkit) 문서 — Records extracted — https://docs.mvt.re/en/latest/ios/records/
4. iphone_backup_decrypt 소스 iphone_backup.py·utils.py (jsharkey13) — https://raw.githubusercontent.com/jsharkey13/iphone_backup_decrypt/master/src/iphone_backup_decrypt/iphone_backup.py , https://raw.githubusercontent.com/jsharkey13/iphone_backup_decrypt/master/src/iphone_backup_decrypt/utils.py
5. libimobiledevice 소스 common/userpref.c — https://raw.githubusercontent.com/libimobiledevice/libimobiledevice/master/common/userpref.c
6. Apple Support — How to back up your iPhone or iPad with your Mac — https://support.apple.com/en-us/108796
