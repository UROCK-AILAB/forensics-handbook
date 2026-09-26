---
title: "블루투스 장치"
parent: "아티팩트 · 네트워크·연결"
nav_order: 670
---

# 블루투스 장치 (Bluetooth)

아이폰은 페어링한 장치와 주변에서 감지한 저전력(LE) 장치를 블루투스 시스템 그룹 영역의 SQLite DB 두 개와 plist 하나에 남기고, 여기서 장치 이름·주소·마지막 감지 시각을 읽어 차량 같은 장치와 언제 이어져 있었는지 짚어 봅니다.

## 무엇을 기록하나 · 왜 생기나

블루투스 기록은 세 파일에 나뉘어 있습니다. `com.apple.MobileBluetooth.ledevices.paired.db` 는 기기와 페어링한 저전력(Bluetooth Low Energy) 장치를, `com.apple.MobileBluetooth.ledevices.other.db` 는 기기가 감지했거나 범위 안에 들어온 저전력 장치를 기록하고, `com.apple.MobileBluetooth.devices.plist` 는 페어링한 장치와 그 장치를 마지막으로 감지한 시각을 기록합니다 [1]. 이어폰·워치·차량처럼 사용자가 연결해 쓰는 장치뿐만 아니라, 페어링하지 않았지만 근처에 있던 저전력 장치까지 남을 수 있어서 "그 시각 그 장치 근처에 있었나" 를 묻는 단서가 됩니다.

차량 연결 사례에서는 `devices.plist` 의 `LastSeenTime` 이 차량과 블루투스 연결이 끊긴 시각이었습니다 [1]. 이 사례의 iOS 버전은 밝혀져 있지 않습니다 [1].

로컬 백업에는 이 세 파일 말고도 연결 종류별 횟수·시간으로 보이는 키가 든 `com.apple.MobileBluetooth.debug.plist` 가 있습니다.

## 위치와 버전별 차이

### 기기 안 경로

기기 안 경로는 아래와 같고 [1], `<GUID>` 는 기기마다 다른 시스템 그룹 폴더 이름입니다.

```
/private/var/containers/Shared/SystemGroup/<GUID>/Library/Database/com.apple.MobileBluetooth.ledevices.paired.db
/private/var/containers/Shared/SystemGroup/<GUID>/Library/Database/com.apple.MobileBluetooth.ledevices.other.db
/private/var/containers/Shared/SystemGroup/<GUID>/Library/Preferences/com.apple.MobileBluetooth.devices.plist
```

### 로컬 백업 안의 위치

암호화하지 않은 로컬 백업에서도 세 파일은 모두 `SysSharedContainerDomain-systemgroup.com.apple.bluetooth` 도메인에 들어 있습니다.

| 도메인 :: 상대 경로 | 형식 |
|---|---|
| `SysSharedContainerDomain-systemgroup.com.apple.bluetooth :: Library/Database/com.apple.MobileBluetooth.ledevices.paired.db` | SQLite |
| `SysSharedContainerDomain-systemgroup.com.apple.bluetooth :: Library/Database/com.apple.MobileBluetooth.ledevices.other.db` | SQLite |
| `SysSharedContainerDomain-systemgroup.com.apple.bluetooth :: Library/Preferences/com.apple.MobileBluetooth.devices.plist` | plist |
| `HomeDomain :: Library/Preferences/com.apple.MobileBluetooth.debug.plist` | plist |
| `HomeDomain :: Library/Preferences/com.apple.bluetooth.plist` | plist |
| `HomeDomain :: Library/Preferences/com.apple.bluetoothuserd.plist` | plist |

위 표는 iOS 27.0 기준입니다. 백업 도메인 이름을 읽는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

### 버전

| iOS | 알려진 내용 | 근거 |
|---|---|---|
| 밝히지 않음 | 세 파일의 역할, `devices.plist` 시각이 현지 시각이라는 점, WAL 을 함께 파싱해야 한다는 점 | [1] |
| 27.0 | 두 DB 의 표·열 이름, `devices.plist`·`debug.plist` 키 이름 | |

iOS 15 ~ 18 사이에 표·열 이름이 바뀌었는지는 알려져 있지 않아서, 분석 대상의 iOS 버전을 먼저 적고 열 이름을 직접 확인합니다.

## 구조

### 두 DB

`ledevices.paired.db` 에는 `PairedDevices`, `CustomProperties`, `_SqliteDatabaseProperties` 표가 있고, `ledevices.other.db` 에는 `PairedDevices` 대신 `OtherDevices` 표가 있습니다. `PairedDevices` 와 `OtherDevices` 의 열은 같습니다.

| 표 | 열 |
|---|---|
| `PairedDevices` · `OtherDevices` | `Uuid`, `Name`, `NameOrigin`, `Address`, `ResolvedAddress`, `LastSeenTime`, `LastConnectionTime`, `GATTServiceChangeConfig`, `Tags`, `iCloudIdentifier` |
| `CustomProperties` | `Uuid`, `JSON` |
| `_SqliteDatabaseProperties` | `key`, `value` |



`Uuid` 로 장치 표와 `CustomProperties` 를 이어 볼 수 있을 것으로 보이지만, 두 표의 관계와 `JSON` 열 내용은 실제 데이터로 확인해야 합니다. `Address` 와 `ResolvedAddress` 가 따로 있어서 두 값이 다를 수 있다는 점만 열 구성으로 알 수 있고, `NameOrigin`·`Tags`·`iCloudIdentifier` 값의 뜻을 설명한 공개 자료는 없습니다. SQLite 파일을 읽는 방법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

### devices.plist

`com.apple.MobileBluetooth.devices.plist` 는 장치 주소를 키로 한 사전이고, 장치 항목 안에서 `Name`, `DefaultName`, `DeviceClass`, `LastSeenTime`, `EncryptionKeySize`, `EncryptionMode`, `CarPlayType`, `AppleDevFeatures`, `CaseInfoColor`, `CaseInfoVersion`, `DoubleTapAction`, `UserNameKey` 와 `ServiceHID`, `ServiceMAP`, `ServicePhoneBook`, `ServiceAACP`, `ServiceGATT`, `ServiceWiAP` 같은 서비스 키, `LastHandsfreeVersion`, `LastAVRCPVersion` 같은 프로필 판 키가 있습니다.

`CarPlayType` 과 `ServicePhoneBook`·`ServiceMAP`·`LastHandsfreeVersion` 이 함께 있는 장치 항목은 차량이나 핸즈프리 장치로 보입니다. 키 이름으로 장치 종류를 짐작할 수는 있어도, 보고서에는 `Name`·`DeviceClass` 값과 함께 "이런 키가 있는 장치" 로 적습니다.

### debug.plist 와 그 밖의 plist

`com.apple.MobileBluetooth.debug.plist` 는 연결 종류마다 사전을 두고, 사전마다 `BtConnectionTypeCounter`, `BtConnectionTypeDuration`, `BtConnectionTypeStartTimeStamp` 키가 있습니다. 연결 종류 이름은 `HID`, `HFP`, `SENSOR`, `WIRELESSIAP`, `NETSHARING`, `PASSIVEMULTISTREAM`, `IDLE`, `LEGATTCLIENT`, `MAP`, `BRAILLE` 등이고, `LeDeviceCache` 아래에는 `WipeNameOrigin` 키가 있습니다. 키 이름으로 보면 연결 종류별 횟수·지속 시간·시작 시각이지만, 장치별 기록이 아니라 종류별로 모인 값이라서 특정 장치와 바로 잇지 않습니다.

`com.apple.bluetooth.plist` 에는 `deviceLastRebootTime`, `lastNowPlayedTime` 키가, `com.apple.bluetoothuserd.plist` 에는 `lastLaunchBootSessionUUID`, `CKPerBootTasks`, `CKStartupTime`, `LastOSLaunchVersion`, `CC_OncePerBootBackingData` 키가 있습니다. 두 파일 모두 장치 목록이 아니라 서비스 상태로 보입니다.

## 증거로서 의미

**증명하는 것**

- `PairedDevices` 나 `devices.plist` 에 장치 항목이 있으면, 수집 시점에 그 기기에 해당 장치의 페어링 기록이 있었다는 사실을 보여 줍니다.
- `OtherDevices` 에 장치 항목이 있으면, 기기가 그 저전력 장치를 감지했거나 범위 안에 들어온 기록이 있다는 뜻입니다 [1].
- `LastSeenTime`·`LastConnectionTime` 에 값이 있으면, 그 장치를 그 시각에 마지막으로 감지하거나 연결한 기록이 있다는 사실까지 말할 수 있습니다.

**증명하지 못하는 것**

- `OtherDevices` 의 감지 기록은 장치를 사용자가 조작했거나 소유했다는 증거가 아니고, 근처를 지나간 남의 장치도 남을 수 있습니다.
- 장치 이름은 제조사 기본 이름이거나 소유자가 붙인 이름이라서, 이름 속 사람 이름을 그 장치 주인으로 단정하지 않습니다. `Name`·`DefaultName`·`NameOrigin` 을 함께 봅니다.
- 차량과 연결된 기록은 그 차량에 탔다는 단서가 되지만, 누가 운전했는지나 이동 경로는 알려 주지 않습니다. 이동은 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md) 의 흐름으로 따로 확인합니다.
- 장치마다 마지막 감지·연결 시각 열만 있어서, 그 전의 연결 횟수와 시각은 이 기록만으로 알 수 없습니다.

보고서에는 "페어링된 장치 목록에 이 이름의 장치가 있고, 마지막 감지 시각은 이것이다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`devices.plist` 의 시각 값은 UTC 가 아니라 기기 현지 시각으로 저장되고 [1], 차량 사례에서 `LastSeenTime` 은 연결이 끊긴 시각이었습니다 [1]. `LastSeenTime` 숫자가 유닉스 시각인지 Mac 절대 시각인지는 공개 자료에 나와 있지 않습니다. 두 DB 의 `LastSeenTime`·`LastConnectionTime` 과 `debug.plist` 의 `BtConnectionTypeStartTimeStamp` 도 기준과 시간대가 알려져 있지 않습니다.

그래서 숫자를 찾으면 자릿수로 기준을 판별해 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 따라 바꾸고, 현지 시각이라면 수집 당시 기기 시간대를 [시간대와 시각 설정](../system-account/time-zone.md) 에서 확인한 뒤 UTC 로 맞춥니다. 시간대를 옮겨 다닌 기기라면 현지 시각 값은 기록한 순간의 시간대를 따로 알아야 해서 해석이 더 어렵습니다. 이름이 `Last` 로 시작하는 열은 가장 최근 값 하나로 보여서, 새 연결이 생기면 이전 값이 남지 않을 수 있습니다.

## 함정과 한계

두 DB 는 WAL 파일도 함께 파싱해야 합니다 [1]. 본체 파일만 복사하면 최근 기록을 놓칠 수 있어서, `-wal`·`-shm` 파일을 같은 폴더에 함께 복사한 뒤 복사본을 엽니다. WAL 의 동작과 지운 행을 되살리는 방법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 와 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

공개 자료가 시험한 iOS 버전을 밝히지 않아서 [1], 다른 버전의 기기에서는 표·열 이름을 직접 확인합니다. `devices.plist` 가 현지 시각이라는 보고를 다른 파일에 그대로 넓혀 쓰지도 않습니다.

KnowledgeC·바이옴에 블루투스 연결을 담는 스트림이 있는지, 있다면 이름이 무엇인지는 실제 데이터로 확인해야 합니다. 연결 순간을 더 촘촘하게 보려면 [통합 로그에서 찾을 것](../logs/unified-log-events.md) 을 살펴봅니다.

페어링을 지운 장치가 목록에서 바로 빠지는지, 지운 흔적이 어디에 남는지는 공개된 분석 자료가 없습니다. 장치 목록이 비어 있을 때 지우기를 의심한다면 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름으로 확인합니다.

## 직접 분석해 보기

먼저 복사본의 첫 16바이트로 SQLite 파일인지 확인합니다. 아래는 SQLite 파일 형식 명세로 만든 예시이고 특정 기기의 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F   문자
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

헤더를 확인했으면 SQLite 명령행 도구(`sqlite3` 등)나 DB Browser for SQLite 같은 공개 도구로 복사본을 열고 장치 목록을 뽑습니다.

```sql
SELECT Uuid, Name, NameOrigin, Address, ResolvedAddress,
       LastSeenTime, LastConnectionTime
FROM PairedDevices
ORDER BY LastSeenTime DESC;
```

`ledevices.other.db` 에서는 표 이름만 `OtherDevices` 로 바꿔 같은 질의를 씁니다. 시각 열은 원래 숫자 그대로 두고, 기준을 확인한 뒤 새 열로 바꾼 값을 붙입니다.

`devices.plist` 는 Python 표준 모듈로 장치마다 이름과 마지막 감지 시각을 뽑아 볼 수 있습니다.

```python
import plistlib

with open("MobileBluetooth-devices-copy.plist", "rb") as f:
    devices = plistlib.load(f)

for addr, item in devices.items():
    print(addr, item.get("Name"), item.get("DefaultName"),
          item.get("DeviceClass"), item.get("LastSeenTime"))
```

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [애플 워치 연결](../health-wallet/apple-watch.md) | 짝지은 워치가 블루투스 목록의 장치와 같은지 |
| [통합 로그에서 찾을 것](../logs/unified-log-events.md) | 연결·해제가 일어난 순간 |
| [전원 로그](../app-usage/powerlog.md) | 같은 시간대의 기기 상태 |
| [중요 위치](../location/significant-locations.md) · [위치 기록 데몬](../location/routined.md) | 차량 연결 시각 전후의 이동 |
| [개인용 핫스폿](hotspot.md) | 블루투스로 인터넷을 나눈 기록(`NETSHARING` 과 비교) |
| [나의 찾기](../location/find-my.md) | 분실물 찾기 장치와 등록 기록 |
| [시간대와 시각 설정](../system-account/time-zone.md) | 현지 시각 값을 UTC 로 바꿀 기준 |

여러 기록을 시간순으로 합치는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 시험 데이터(NIST CFReDS 등)에 아이폰 추출이 있으면 아래 질문으로 풀어 봅니다. 없으면 연습용 기기에 블루투스 이어폰이나 차량을 연결했다가 끊은 뒤 백업을 떠서 풀어 봅니다.

1. 백업의 `SysSharedContainerDomain-systemgroup.com.apple.bluetooth` 도메인에 어떤 파일이 있습니까? `-wal` 파일도 있습니까?
2. `PairedDevices` 와 `devices.plist` 에 같은 장치가 모두 있습니까? 이름이 같습니까?
3. `devices.plist` 의 `LastSeenTime` 을 어느 기준으로 읽어야 실제로 연결을 끊은 시각과 맞습니까? 현지 시각입니까?
4. `OtherDevices` 에 연결한 적 없는 장치가 몇 개 있습니까? 그 장치들의 `LastSeenTime` 은 어느 시간대에 몰려 있습니까?
5. WAL 파일을 빼고 연 결과와 함께 연 결과에서 행 수나 시각이 달라집니까?

## 참고 문헌

1. Cellebrite, "How to Use iOS Bluetooth Connections to Solve Crimes Faster" — https://cellebrite.com/en/blog/how-to-use-ios-bluetooth-connections-to-solve-crimes-faster/
