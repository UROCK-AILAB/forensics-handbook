---
title: "기기 식별자"
parent: "기반 · 값 읽는 법"
nav_order: 200
---

# 기기 식별자 (UDID·ECID·일련번호)

아이폰 한 대에는 UDID·ECID·일련번호·IMEI 같은 식별자가 여럿 있고 로컬 백업의 Info.plist 에도 이 이름의 키가 남아서, 수집한 자료가 어느 기기에서 나왔는지 맞출 때 이 값들을 서로 대조합니다.

## 이 형식을 쓰는 아티팩트

로컬 백업 폴더 맨 위의 Info.plist 에는 아래 키가 있었고, 이름을 가린 키가 하나 더 있었습니다 (확인 범위: iOS 27.0). 키 이름만 확인했고 값은 읽지 않았습니다.

| 묶음 | Info.plist 키 |
|---|---|
| 식별자 | `Unique Identifier`, `Target Identifier`, `GUID`, `Serial Number`, `IMEI`, `MEID` |
| 기종과 OS | `Product Type`, `Product Name`, `Product Version`, `Build Version` |
| 이름과 백업 | `Device Name`, `Display Name`, `Target Type`, `Last Backup Date`, `Windows OS Version` |

관찰한 백업의 `Product Type` 에 해당하는 기종 식별자는 iOS 27.0 기기였고, OS 는 iOS 27.0 빌드 24A5418b 였습니다. 같은 백업의 Manifest.plist 에는 `Lockdown` 키가 있었지만 그 아래 키는 확인하지 못했습니다 (확인 범위: iOS 27.0).

Info.plist 밖에서 식별자와 관련된 이름이 보인 곳은 아래와 같습니다 (확인 범위: iOS 27.0).

| 위치 | 확인한 내용 |
|---|---|
| `HomeDomain` :: `Library/DeviceRegistry.state/UDIDChangeTracker.plist` | 파일이 있음. 키 이름은 모두 가려져 있고 형은 int·str·dict·list |
| `SysSharedContainerDomain-systemgroup.com.apple.mobilegestaltcache` | 도메인이 있고 항목 1개. 안의 파일과 키는 확인하지 못함 |
| `RootDomain` :: `Library/Caches/locationd/consolidated.db`, gyroCal.db | `TableInfo` 표에 `TableName`, `SoftwareVersion`, `SerialNumber` 칸 |
| 같은 consolidated.db | `FenceHandOffDeviceId` 표(`DeviceIdIndex`, `DeviceId`), `GeoFence.DeviceIdIndex` 칸 |
| 블루투스 DB `PairedDevices`·`OtherDevices` | `Uuid`, `Address`, `ResolvedAddress`, `iCloudIdentifier` 칸. 상대 기기의 식별자 |

기기 정보를 증거로 읽는 법은 [기기 정보](../../02-artifacts/system-account/device-info.md) 에서, 백업 파일의 짜임은 [로컬 백업](../backups/local-backup/index.md) 에서 다룹니다.

## 구조

### UDID 와 ECID

UDID (Unique Device Identifier) 는 ECID 같은 하드웨어 값으로 계산한 기기 고유 식별자이고, 모양은 기종이 나온 시기에 따라 다릅니다 [2].

| 기종 출시 시기 | UDID 모양 | 근거 |
|---|---|---|
| 2007~2018년 | 소문자 16진수 40자리 | [2] |
| 2018년 이후 | 대문자 16진수 25자리 | [2] |

위키백과는 옛 형식의 계산식을 `SHA1(serial + IMEI + wifiMac + bluetoothMac)` 로 적지만, 문서 스스로 이 문단에 출처가 부족하다고 표시해 두었습니다 [2]. 새 형식이 어떤 값을 어떻게 이어 붙인 것인지와 정확한 기종 경계는 이번에 연 자료로 확인하지 못했습니다. 위키백과는 Apple 이 Apple ID·iCloud 에서 기기를 가릴 때 UDID 를 쓰고, iOS 11 부터 설정 과정에서 확인 서버가 UDID 를 검사한다고도 쓰지만 이 문단 역시 출처 표시가 부족합니다 [2].

ECID 는 UDID 계산에 들어가는 하드웨어 값으로 나오고 [2], 길이와 형식은 이번에 연 자료로 확인하지 못했습니다.

### 일련번호·IMEI·EID·ICCID

Apple 지원 문서 [1] 는 이 번호들을 볼 수 있는 곳을 아래처럼 안내하고, 같은 문서에 UDID 는 나오지 않습니다.

| 볼 수 있는 곳 | 보이는 번호 |
|---|---|
| 설정의 일반 메뉴에 있는 정보 화면 | 일련번호 |
| 컴퓨터 연결(macOS Catalina 10.15 이후 Finder, Windows 의 Apple 기기 앱 또는 iTunes)에서 기기 이름 아래 전화번호나 모델을 누름 | EID, IMEI/MEID, ICCID 가 번갈아 보임 |
| account.apple.com 에 로그인해 기기를 고름 | 일련번호, EID, IMEI/MEID |
| 원래 포장 상자의 바코드 | 일련번호, EID, IMEI/MEID |
| 처음 켤 때 "Hello" 화면 오른쪽 아래 정보(i) 단추 | 기기 정보 |

기기 본체에 IMEI/MEID 가 새겨진 자리는 기종마다 다릅니다. iPhone 13 계열·12 계열·11 계열, SE 2·3세대, XS·XS Max·XR·X, 8·8 Plus, 7·7 Plus, 6s·6s Plus, 3G·3GS·4(GSM)·4s 는 SIM 트레이에, iPhone 6·6 Plus, SE 1세대, 5s·5c·5 는 뒷면에 적혀 있습니다 [1]. 같은 문서는 iPhone 14 이후 기종에는 IMEI/MEID 가 새겨져 있지 않다고 쓰고, 듀얼 SIM 기기의 IMEI 두 개는 설명하지 않습니다.

## 읽는 법

수집한 백업이 압수한 기기에서 나왔는지 확인할 때는 아래 순서를 따릅니다.

1. **백업의 Info.plist 를 읽습니다.** `Serial Number`, `IMEI`, `MEID`, `Product Type`, `Product Version`, `Build Version` 을 적습니다.
2. **기기 쪽 번호를 따로 확인합니다.** 설정 화면, 컴퓨터 연결 화면, SIM 트레이(iPhone 13 이전 기종)나 상자처럼 Apple 문서 [1] 가 안내하는 곳에서 같은 번호를 읽습니다.
3. **두 쪽을 대조합니다.** 일련번호와 IMEI 가 같고 기종 식별자가 기기 모델과 맞는지 봅니다.
4. **확인하지 못한 키는 뜻을 붙이지 않습니다.** `Unique Identifier`·`Target Identifier` 가 UDID 를 담는지, `GUID` 가 기기와 백업한 컴퓨터 가운데 어느 쪽의 식별자인지는 확인하지 못했으니 보고서에는 키 이름과 값을 그대로 적습니다.

Python 표준 라이브러리로 Info.plist 의 키를 읽는 예입니다. 결과 값은 적지 않았습니다.

```python
import plistlib

with open("Info.plist", "rb") as f:
    info = plistlib.load(f)

for key in ("Product Type", "Product Version", "Build Version",
            "Serial Number", "IMEI", "MEID", "Unique Identifier"):
    print(key, "=", info.get(key))
```

plist 의 형식은 [속성 목록 파일](../data-formats/plist.md) 에서 다룹니다.

## 포렌식에서 중요한 점

복원이나 기기 이전이 있었으면 한 기기의 데이터가 다른 기기에 들어 있을 수 있어서, 식별자와 함께 빌드 번호 흔적도 봅니다. 관찰한 백업에서는 com.apple.MobileBackup.plist 의 `RestoreInfo` 아래 `BackupBuildVersion`, `DeviceBuildVersion`, `RestoreDate`, `WasCloudRestore` 키와 `HomeDomain` :: `Library/Preferences/com.apple.imdsmsrecordstore.plist` 의 `IMDSavedDeviceState` 아래 `IMDSavedDeviceStateBuildVersionKey`, `IMDSavedDeviceStateDidRestoreFromBackupKey`, `IMDSavedDeviceStateDidMigrateFromDifferentDeviceKey` 키가 보였습니다 (확인 범위: iOS 27.0). 같은 백업의 `HomeDomain` :: `Library/Preferences/com.apple.cloudphotod.plist` 에는 `_CPLUpgradeHistory-SystemLibrary` 아래 `lastSeenOSBuildVersion`, `previousOSBuildVersion` 키도 있었습니다. 이 키들은 이름으로 보아 복원·이전 흔적과 엮을 수 있지만 뜻은 출처로 확인하지 못했고, 복원 흔적을 읽는 법은 [초기화와 복원 흔적](../../02-artifacts/system-account/erase-restore.md) 에서 다룹니다.

`UDIDChangeTracker.plist` 도 이름으로 보아 UDID 변화와 관련된 파일이지만 키 이름이 가려져 있어서 무엇을 적는지 확인하지 못했습니다. 이름만으로 "UDID 가 바뀐 기록이 있다" 고 쓰지 않습니다.

## 함정

- **위키백과 한 곳에만 기댄 설명이 많습니다.** UDID 의 모양과 계산식은 출처 표시가 부족한 위키백과 문단 [2] 에서 왔고, 다른 자료는 이번에 열리지 않았습니다. 보고서에 UDID 형식을 근거로 기종을 판단하는 문장을 넣을 때는 이 한계를 함께 적습니다.
- **일련번호라는 칸 이름이 기기 일련번호라는 보장이 없습니다.** consolidated.db·gyroCal.db 의 `TableInfo.SerialNumber` 는 같은 표에 `TableName`·`SoftwareVersion` 이 함께 있어서 표 버전 번호일 수도 있고, 기기 일련번호인지는 확인하지 못했습니다.
- **상대 기기의 식별자를 이 기기의 식별자로 읽지 않습니다.** 블루투스 DB 의 `Uuid`·`Address`·`iCloudIdentifier` 는 상대 기기의 칸이라서, 이 아이폰을 가리키지 않습니다. 해석은 [블루투스 장치](../../02-artifacts/network/bluetooth.md) 에서 다룹니다.
- **백업 폴더 이름과 식별자의 관계를 짐작하지 않습니다.** 로컬 백업 폴더 이름이 UDID 인지는 이번 자료로 확인하지 못했으니, 기기를 가릴 때는 폴더 이름 대신 Info.plist 의 일련번호·IMEI 를 씁니다.
- **consolidated.db 의 `DeviceId` 는 뜻을 모릅니다.** `FenceHandOffDeviceId` 표의 `DeviceId` 는 다른 기기의 식별자로 보이지만 확인하지 못했습니다.

## 도구

Info.plist 는 plist 를 여는 도구나 Python 의 `plistlib` 로 읽고, consolidated.db 와 블루투스 DB 는 SQLite 를 여는 도구로 칸을 조회합니다. 기기 쪽 번호는 Apple 문서 [1] 가 안내하는 설정 화면과 Finder·Apple 기기 앱·iTunes 화면에서 읽을 수 있습니다.

## 참고 문헌

1. Apple 지원 — Find the serial number or IMEI on your iPhone, iPad, or iPod touch (108037) — https://support.apple.com/en-us/108037?device-type=iphone
2. Wikipedia — UDID — https://en.wikipedia.org/wiki/UDID (문서 스스로 출처 부족을 표시한 문단이 있음)
