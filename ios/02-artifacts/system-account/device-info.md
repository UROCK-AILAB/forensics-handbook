---
title: "기기 정보"
parent: "아티팩트 · 시스템·계정"
nav_order: 270
---

# 기기 정보 (Device Info·Lockdown)

기기 정보는 조사 대상 아이폰의 기종·iOS 버전·빌드·식별자·기기 이름을 알려 주는 기록이고, 한 파일에 모여 있지 않아서 전체 파일 시스템 추출에서는 Lockdown 폴더와 여러 시스템 설정 파일을, 로컬 백업에서는 백업 폴더 맨 위의 `Info.plist` 와 백업 안 설정 파일을 함께 읽어야 합니다.

## 무엇을 기록하나 · 왜 생기나

기종 이름, 일련번호, UDID, Wi-Fi·블루투스 MAC 주소, iOS 버전과 빌드, 기기 이름, 전화번호와 ICCID, 마지막 백업 날짜가 기기 곳곳의 파일에 따로 적혀 있습니다[1]. 기기 이름은 컴퓨터와 기기를 짝짓고 기기 정보를 넘겨주는 lockdownd 쪽 폴더(`Lockdown`)에 있고, 기종 이름은 네트워크 구성 파일에, 전화번호와 ICCID 는 통신 설정 파일에 있는 식으로 기록을 쓰는 구성 요소가 저마다 다릅니다[1].

컴퓨터로 로컬 백업을 만들면 기기 정보 가운데 일부가 기기 밖 백업 폴더에도 남습니다. 로컬 백업의 `Info.plist` 에는 기기 이름, 기종, iOS 버전, 빌드, 일련번호, IMEI, MEID, 고유 식별자, 마지막 백업 날짜를 담는 키가 있습니다.

조사에서 기기 정보를 가장 먼저 보는 이유는 두 가지입니다. iOS 버전을 알아야 다른 아티팩트의 경로와 DB 표 구성을 버전에 맞게 고를 수 있고, 식별자를 알아야 압수한 기기와 추출물·백업이 같은 기기에서 나왔는지 맞춰 볼 수 있습니다. 식별자 하나하나를 읽는 법은 [기기 식별자](../../01-foundations/value-decoding/device-identifiers.md) 에서 다룹니다.

## 위치와 버전별 차이

### 전체 파일 시스템 추출

아래 경로는 iOS 15 이미지 기준입니다[1]. 파일 안의 어느 키에 값이 들어 있는지는 파일을 직접 열어 확인합니다.

| 알고 싶은 것 | 경로 |
|---|---|
| 기종 내부 이름 | `/private/var/preferences/SystemConfiguration/preferences.plist` |
| 일련번호 | `/private/var/root/Library/Caches/locationd/consolidated.db` |
| UDID | `/private/var/root/Library/Caches/locationd/cache.plist` |
| Wi-Fi MAC 주소 | `/private/var/preferences/SystemConfiguration/NetworkInterfaces.plist` |
| 블루투스 MAC 주소 | `backup_keychain_v2.plist` (전체 경로는 추출물에서 파일 이름으로 찾아 확인) |
| iOS 버전·빌드 | `/private/var/installd/Library/MobileInstallation/LastBuildInfo.plist` |
| 기기 이름 | `/private/var/root/Library/Lockdown/data_ark.plist` |
| 전화번호(MSISDN)·ICCID | `/private/var/wireless/Library/Preferences/com.apple.commcenter.plist` |
| 마지막 백업 날짜 | `/private/var/mobile/Library/Preferences/com.apple.ldbackup.plist` |

`LastBuildInfo.plist` 의 경로는 자료마다 다릅니다. `installd/Library/MobileInstallation/` 아래로 적은 자료[1]와 `/installd/Library/Logs/MobileInstallation/LastBuildInfo.plist` 로 적은 자료[8]가 있습니다. iOS 버전마다 다를 수 있으니 추출물에서 두 경로를 모두 찾아봅니다.

`data_ark.plist` 에 첫 설정을 마친 시각과 복원 방법을 담는 키가 있다는 내용은 [초기화와 복원 흔적](erase-restore.md) 에서 다룹니다.

### 로컬 백업

로컬 백업에서는 기기 정보를 아래 자리에서 볼 수 있습니다.

| 알고 싶은 것 | 백업 안 위치 | 키 |
|---|---|---|
| 기기 이름·기종·버전·식별자 | 백업 폴더 맨 위 `Info.plist` | `Device Name`, `Product Name`, `Product Type`, `Product Version`, `Build Version`, `Serial Number`, `IMEI`, `MEID`, `Unique Identifier`, `Last Backup Date` |
| 기종 내부 이름으로 보이는 값 | `SystemPreferencesDomain :: SystemConfiguration/preferences.plist` | `Model` |
| 통신 설정 | `WirelessDomain :: Library/Preferences/com.apple.commcenter.plist` 외 `com.apple.coretelephony.plist`, `com.apple.commcenter.data.plist` | 이 페이지에서는 다루지 않음 |
| 지역 코드 | `HomeDomain :: Library/Preferences/com.apple.AppSupport.plist` | `CPHomeCountryCode`, `CPActiveCountryCode`, `CPNetworkCountryCode`, `CPLastKnownNetworkCountryCode` |
| 기기 쪽 백업 설정 | `HomeDomain :: Library/Preferences/com.apple.mobile.ldbackup.plist` | `CloudBackupEnabled`, `LastCloudBackupDate`, `LastCloudBackupTZ`, `RequiresEncryption`, `WillEncrypt`, `Version` |
| 기종 정보 묶음 | `HomeDomain :: Library/Preferences/com.apple.itunesstored.plist`, `com.apple.Preferences.plist` | `SSDeviceType` 안의 `buildVersion`, `deviceTypeNumber`, `hardwareModel` |

`Info.plist` 의 키 전체와 `Manifest.plist`·`Status.plist` 의 짜임은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다. `Unique Identifier` 는 이름으로 보면 UDID 자리입니다. `Model` 키에는 "기종 내부 이름"[1] 이 들어 있는 것으로 보입니다. 같은 도메인에는 키 구성이 똑같은 `SystemConfiguration/preferences-D##AP.plist`(`#` 은 숫자) 도 있습니다.

`/private/var/root/Library/Lockdown/` 과 `/private/var/installd/` 에 해당하는 도메인 경로는 로컬 백업에 나오지 않을 수 있습니다. 그래서 `data_ark.plist` 와 `LastBuildInfo.plist` 는 전체 파일 시스템 추출에서만 볼 수 있을 가능성이 높습니다. 수집 방식에 따라 얻는 범위는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

### 여러 설정 파일에 흩어진 버전 기록

iOS 버전이나 빌드를 적는 키는 `Info.plist` 말고도 여러 설정 파일에 있습니다. 모두 `HomeDomain :: Library/Preferences/` 아래 파일이고, `MCMeta.plist` 만 `HomeDomain :: Library/UserConfigurationProfiles/PublicInfo/` 아래에 있습니다.

| 파일 | 키 |
|---|---|
| `com.apple.accountsd.plist` | `LastSystemVersion`, `LastMigrationSystemVersion` |
| `com.apple.springboard.plist` | `SBLastSystemVersion` |
| `com.apple.locationd.plist` | `LastSystemVersion` |
| `com.apple.springboard.datamigrator.plist` | `lastBuildVersion` |
| `com.apple.icloud.findmydeviced.plist` | `LastLaunchVersion`, `Daemon::LastOSLaunchVersion` |
| `com.apple.AppleMediaServices.plist` | `AMSLastMigratedBuildVersion` |
| `MCMeta.plist` | `LastMigratedBuild` |

구성 요소마다 자기가 마지막으로 돈 버전을 따로 적는 것으로 보여서, 값을 나란히 놓으면 업데이트 뒤 어느 구성 요소가 아직 옛 버전 값을 남기고 있는지 볼 수 있을 것으로 보입니다. 다만 이 키들로 업데이트 이력을 재구성하는 방법은 정해져 있지 않으므로, 보고서에는 "이 키에 이 버전이 적혀 있다" 까지만 씁니다.

같은 `com.apple.springboard.plist` 에는 `SBLastKnownShutdownDate` (datetime) 와 `SBLastRestoreIdentifier` (str) 키가 있고, `com.apple.centaurid.plist` 에는 `SystemBootUUID` 와 `RestoreVersion` 키가 있습니다. 이름으로는 마지막 종료 시각, 복원 식별자, 부팅 식별자로 읽히지만 뜻이 정해져 있지 않으므로, 보고서에는 값만 옮기고 뜻을 단정하지 않습니다.

## 구조

기기 정보를 담는 파일은 대부분 plist 이고, 일련번호가 있다는 `consolidated.db` 는 이름으로 보면 SQLite 데이터베이스입니다. plist 는 키와 값의 사전이라서 원하는 키 이름을 찾아 값을 읽으면 되고, 이진 plist 와 XML plist 를 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md), SQLite 는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

`SystemConfiguration/preferences.plist` 의 최상위 키는 `Sets`, `NetworkServices`, `CurrentSet`, `__VERSION__`, `Model`, `System` 이고, `System` 안에는 `Network` 와 `System` 이 있습니다. 네트워크 구성 파일이라서 기종 이름은 이 가운데 `Model` 하나뿐이고 나머지는 네트워크 설정입니다.

백업 `Manifest.plist` 에도 `Lockdown` 이라는 키가 있습니다. 그 안의 하위 키와 lockdownd 의 관계는 실제 데이터로 확인해야 합니다.

## 증거로서 의미

**증명하는 것.** 추출물이나 백업이 어떤 기종, 어떤 iOS 버전과 빌드, 어떤 일련번호·IMEI·UDID 의 기기에서 나왔는지를 보여 줍니다. 압수한 기기에서 확인한 식별자와 맞춰 보면 추출물과 기기가 같은 것인지 확인할 수 있고, 백업 폴더가 여러 개일 때 어느 백업이 어느 기기의 것인지도 가릴 수 있습니다. 백업의 `Info.plist` 는 백업을 만든 시점의 기기 이름과 버전을 보여 주고, 지금 기기의 상태와 다를 수 있다는 점도 함께 적어 둡니다.

**증명하지 못하는 것.** 기기 이름은 사용자가 바꿀 수 있는 글자라서 이것만으로는 소유자가 누구인지 알 수 없습니다. 전화번호와 ICCID 는 통신 설정에 적힌 값일 뿐이고, 그 번호로 누가 통화했는지는 [통화 기록](../communications/call-history.md) 같은 다른 기록으로 봐야 합니다. 여러 파일의 버전 키도 각 구성 요소가 마지막으로 적은 값이라서, 기기가 언제 어느 버전으로 업데이트했는지를 이 키만으로 단정할 수 없습니다.

## 시각 해석

기기 정보에서 시각으로 쓰는 값은 많지 않습니다. `Info.plist` 의 `Last Backup Date` 는 이름으로 보면 백업을 만든 때이고, `com.apple.mobile.ldbackup.plist` 의 `LastCloudBackupDate` 는 정수(int) 형, `com.apple.springboard.plist` 의 `SBLastKnownShutdownDate` 는 날짜(datetime) 형입니다. 정수로 적힌 시각은 기준 시점과 단위를 자릿수로 판별해야 하고, 그 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다. 현지 시각으로 바꿀 때 쓰는 기기 시간대는 [시간대와 시각 설정](time-zone.md) 에서 봅니다.

## 함정과 한계

**"Lockdown" 이 두 가지를 가리킵니다.** 기기와 컴퓨터를 짝짓는 lockdownd 의 폴더(`/private/var/root/Library/Lockdown/`)와 잠금 모드(Lockdown Mode)는 서로 다른 기능입니다. 백업의 `HomeDomain :: Library/Preferences/com.apple.lockdownmoded.plist` (키 `LDMExemptCNHistoryToken`) 는 이름으로 보면 잠금 모드 쪽 파일이니, lockdownd 기록과 섞어 해석하지 않습니다.

**파일 이름이 자료마다 다릅니다.** 마지막 백업 날짜 파일을 `com.apple.ldbackup.plist` 로 적은 자료[1]가 있지만, 로컬 백업에서는 `com.apple.mobile.ldbackup.plist` 로 나옵니다. `LastBuildInfo.plist` 의 경로도 자료마다 다르니, 경로 하나로 찾아서 없다고 결론 내리지 않고 파일 이름으로 추출물 전체를 검색합니다.

**수집 방식에 따라 보이는 파일이 다릅니다.** 로컬 백업만 있으면 Lockdown 폴더의 기록을 보지 못할 수 있습니다. 그럴 때는 `Info.plist` 와 백업 안 설정 파일로 확인한 범위를 적고, 전체 파일 시스템 추출에서만 나오는 정보는 확인하지 못했다고 씁니다.

**지우기와 조작.** 기기 이름은 언제든 바꿀 수 있고, 초기화하거나 다른 기기의 백업으로 복원하면 설정 파일의 버전·이력 값이 새로 쓰이거나 옮겨 올 수 있습니다. 기기 정보가 다른 기록과 맞지 않으면 [초기화와 복원 흔적](erase-restore.md) 과 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 를 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 plist 명세로 만든 예시이고 특정 기기에서 나온 바이트가 아닙니다. 파일이 이진 plist 이면 첫 8바이트가 `bplist00` 이고, XML plist 이면 `<?xml` 로 시작합니다.

```
00000000  62 70 6C 69 73 74 30 30  ...                     bplist00...
```

이진 plist 에서 5글자 ASCII 문자열 객체는 표시 바이트 `0x55`(상위 4비트 `0101` = ASCII 문자열, 하위 4비트 `0101` = 길이 5) 뒤에 글자가 그대로 옵니다. `SystemConfiguration/preferences.plist` 에서 `Model` 키 이름을 찾으면 이런 모양이고, 값 문자열은 사전의 참조 표를 따라가 찾습니다.

```
55 4D 6F 64 65 6C                                          UModel
```

### 공개 도구로 한 번

1. 로컬 백업이면 `Manifest.db` 에서 필요한 파일의 fileID 를 찾습니다. 백업 폴더 안에서 fileID 로 실제 파일을 여는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

```sql
SELECT fileID, domain, relativePath
FROM Files
WHERE (domain = 'SystemPreferencesDomain' AND relativePath = 'SystemConfiguration/preferences.plist')
   OR (domain = 'HomeDomain' AND relativePath IN (
        'Library/Preferences/com.apple.AppSupport.plist',
        'Library/Preferences/com.apple.mobile.ldbackup.plist',
        'Library/Preferences/com.apple.springboard.plist'));
```

2. 꺼낸 파일과 백업 폴더 맨 위 `Info.plist` 를 Python 표준 라이브러리 `plistlib` 로 엽니다. `plistlib.load` 는 이진 plist 와 XML plist 를 모두 읽습니다. 원본이 아니라 사본에서 실행합니다.

```python
import plistlib

with open("Info.plist", "rb") as f:
    info = plistlib.load(f)

for key in ("Device Name", "Product Type", "Product Version", "Build Version",
            "Serial Number", "Unique Identifier", "Last Backup Date"):
    print(key, "=", info.get(key))
```

3. macOS 에서는 `plutil -p 파일이름` 으로도 같은 내용을 볼 수 있습니다. 도구 출력은 위 헥스 확인과 맞춰 보고, 도구를 검증하는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

식별자는 [기기 식별자](../../01-foundations/value-decoding/device-identifiers.md) 에서 형식을 확인하고, 기기에 로그인한 계정은 [애플 계정](apple-account.md) 에서, 나의 찾기에 등록된 상태는 [나의 찾기](../location/find-my.md) 에서 봅니다. Wi-Fi 와 블루투스 MAC 주소는 [와이파이 기록](../network/wifi.md), [블루투스 장치](../network/bluetooth.md) 와 맞춰 보고, 첫 설정·복원·다른 기기에서 옮긴 기록은 [초기화와 복원 흔적](erase-restore.md) 에서 확인합니다. 백업이 여러 벌이면 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 과 [아이클라우드 백업](../../01-foundations/backups/icloud-backup.md) 을 함께 보고, 보고서에 기기를 적는 방식은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 를 따릅니다.

## 실습

공개 시험 데이터(NIST CFReDS 등의 iOS 이미지나 백업)로 다음 질문을 풀어 봅니다.

1. 분석 대상 기기의 기종(`Product Type`)과 iOS 버전·빌드는 무엇이고, 여러 설정 파일의 버전 키 값은 서로 같습니까?
2. `SystemConfiguration/preferences.plist` 의 `Model` 값은 `Info.plist` 의 `Product Type` 과 어떤 관계로 보입니까?
3. 전체 파일 시스템 추출이라면 `LastBuildInfo.plist` 가 두 경로 가운데 어디에 있습니까?
4. `data_ark.plist` 와 `Info.plist` 의 기기 이름이 같습니까? 다르다면 두 파일은 각각 언제 적힌 값입니까?
5. `com.apple.AppSupport.plist` 의 네 지역 코드가 모두 같습니까?

## 참고 문헌

- [1] iOS 15 Image Forensics Analysis and Tools Comparison: Processing details and general device information — digital-forensics.it (2023-09) — https://blog.digital-forensics.it/2023/09/ios-15-image-forensics-analysis-and.html
- [8] iOS-Forensics-References README — RealityNet (GitHub) — https://github.com/RealityNet/iOS-Forensics-References/blob/main/README.md
