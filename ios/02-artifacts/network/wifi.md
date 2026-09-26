---
title: "와이파이 기록"
parent: "아티팩트 · 네트워크·연결"
nav_order: 660
---

# 와이파이 기록 (Wi-Fi)

## 한 줄 요약

아이폰은 들어갔던 와이파이 네트워크와 지운 네트워크, 네트워크마다 쓴 개인 Wi-Fi 주소를 시스템 plist 에 남기고, 여기서 네트워크 이름(SSID)·접속 지점 주소(BSSID)·접속 시각을 읽어 기기가 어느 네트워크에 붙었는지 짚어 볼 수 있지만, 수집 방식에 따라 보이는 파일이 크게 다릅니다.

## 무엇을 기록하나 · 왜 생기나

아이폰은 한 번 들어간 와이파이 네트워크를 알려진 네트워크(Known Networks) 목록에 적어 둡니다. 이 목록에는 네트워크 이름 `SSID`, 숨은 네트워크 표시 `Hidden`, 추가 경위로 보이는 `AddReason`, 번들 ID `BundleID` 와 함께 추가·갱신·발견·접속 시각 키가 있고, 접속 시각은 사용자가 들어간 때(`JoinedByUserAt`)와 시스템이 들어간 때(`JoinedBySystemAt`)로 키가 나뉩니다 [1]. 접속 지점(AP)마다 채널, 마지막 연결 시각, 위도·경도·정확도 키도 있어서 [1], 네트워크 이름뿐만 아니라 어느 곳의 공유기에 붙었는지까지 살펴볼 수 있습니다.

iOS 14 이상에서는 개인 Wi-Fi 주소(Private Wi-Fi Address)를 쓸 수 있고, 기기는 네트워크마다 다른 Wi-Fi 주소로 자신을 알립니다 [2]. 네트워크별 개인 MAC 주소 목록에는 쓰고 있는 주소 값과 주소를 만든 시각 등이 들어 있습니다 [1]. 공유기나 사내 무선망 기록에 남은 MAC 주소를 기기와 맞춰 볼 때 이 목록이 다리 역할을 합니다.

로컬 백업에는 지운 네트워크로 보이는 목록과, 와이파이 접속 지점·신호 세기·위치 칸이 한 표에 모인 데이터 사용량 DB 의 `ZWIFIDATA` 표도 들어 있습니다. 백업에 알려진 네트워크 목록이 없을 때 이 두 가지가 그 빈자리를 일부 메웁니다.

## 위치와 버전별 차이

### 공개 자료에 나온 파일

와이파이 기록은 아래 네 파일 이름으로 찾습니다 [1]. 기기 안 경로는 검체에서 파일 이름으로 찾아 확인합니다.

| 파일 이름 | 담는 것 | 근거 |
|---|---|---|
| `com.apple.wifi.known-networks.plist` | 알려진 네트워크(새 형식) | [1] |
| `com.apple.wifi.plist` | 알려진 네트워크(예전 형식) | [1] |
| `com.apple.wifi-networks.plist.backup` | iLEAPP 가 함께 찾는 사본 | [1] |
| `com.apple.wifi-private-mac-networks.plist` | 네트워크별 개인 MAC 주소 | [1] |

### 로컬 백업에 있는 파일

암호화하지 않은 로컬 백업(iOS 27.0)에는 아래 파일이 있고, `com.apple.wifi.known-networks.plist` 와 `com.apple.wifi.plist` 는 없을 수 있습니다. 알려진 네트워크 목록이 암호화한 백업에 들어가는지는 공식 자료가 없습니다.

| 도메인 :: 상대 경로 | 내용 |
|---|---|
| `HomeDomain :: Library/Preferences/com.apple.wifi.removed-networks.plist` | 지운 네트워크로 보이는 항목 5개 |
| `HomeDomain :: Library/Preferences/com.apple.wifi.nearby-recommended-networks.plist` | 키가 비어 있음 |
| `SystemPreferencesDomain :: SystemConfiguration/com.apple.wifi-networks.plist` | 키가 비어 있음 |
| `SystemPreferencesDomain :: SystemConfiguration/com.apple.wifi-class-d-private-mac-networks.plist` | 최상위에 목록 하나(이름 가림) |
| `SystemPreferencesDomain :: SystemConfiguration/preferences.plist` | `Sets`, `NetworkServices`, `CurrentSet`, `__VERSION__`, `Model`, `System` 키 |
| `RootDomain :: Library/Preferences/com.apple.wifid.plist` | `joinPMAssertionResetTimestamp`, `joinPMAssertionTimeUsedKey` 키 |
| `WirelessDomain :: Library/Databases/DataUsage.sqlite` | `ZWIFIDATA` 표 |

공개 자료의 `com.apple.wifi-private-mac-networks.plist` 와 백업의 `com.apple.wifi-class-d-private-mac-networks.plist` 는 이름이 다르고, 두 파일이 같은 역할인지는 공개 자료가 없습니다. 이 밖에 `SysSharedContainerDomain-systemgroup.com.apple.WiFiAssist` 도메인(항목 3개)과 `AppDomainPlugin-com.apple.wifi.settingscontrols`, `AppDomainPlugin-com.apple.DiagnosticExtensions.WiFi` 같은 확장 도메인도 있습니다. 백업 도메인이 무엇인지는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

### 버전별 차이

| iOS | 달라지는 점 | 근거 |
|---|---|---|
| 12.4 ~ 18.x | iLEAPP 스크립트가 이 범위의 표본을 기준으로 만들어졌고, 버전마다 plist 구조가 다름 | [1] |
| 14 전후 | 예전 `com.apple.wifi.plist` 에서 `com.apple.wifi.known-networks.plist` 로 바뀐 것으로 흔히 알려져 있음(공개 자료 없음) | — |
| 14 이상 | 개인 Wi-Fi 주소 사용 가능 | [2] |
| 18 이상 | 개인 Wi-Fi 주소 설정이 끔·고정·순환 세 가지 | [2] |
| 27.0 | 암호화하지 않은 백업에 알려진 네트워크 목록 없음, 지운 네트워크 목록 있음 | |

## 구조

plist 를 읽는 방법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다루고, 여기서는 키 이름만 정리합니다.

### 알려진 네트워크 (새 형식)

| 무리 | 키 [1] |
|---|---|
| 네트워크 항목 | `SSID`, `AddReason`, `BundleID`, `Hidden`, `AddedAt`, `UpdatedAt`, `JoinedBySystemAt`, `JoinedByUserAt`, `LastDiscoveredAt` |
| `__OSSpecific__` 아래 | `BSSID`, `networkUsage`, `CarPlayNetwork`, `WiFiNetworkPasswordModificationDate`, `prevJoined` |
| `CaptiveProfile` 아래 | `WhitelistedCaptiveNetworkProbeDate`, `CaptiveWebSheetLoginDate` |
| `BSSList` 아래(접속 지점마다) | `Channel`, `ChannelFlags`, `LastAssociatedAt`, `LocationAccuracy`, `LocationTimestamp`, `LocationLatitude`, `LocationLongitude` |

`CaptiveProfile` 은 호텔·카페처럼 로그인 화면을 띄우는 네트워크(캡티브 포털)와 관련된 키로 보이고, `BSSList` 에는 접속 지점마다 위치 값이 들어 있을 수 있습니다 [1].

### 알려진 네트워크 (예전 형식)

예전 `com.apple.wifi.plist` 의 네트워크 목록에 있는 키는 `SSID_STR`, `BSSID`, `networkUsage`, `80211D_IE`(그 안의 `IE_KEY_80211D_COUNTRY_CODE`), `enabled`, `CarPlayNetwork`, `CARPLAY_NETWORK`, `Hidden`, `WPS_PROB_RESP_IE`, `CaptiveProfile`(`CaptiveNetwork`, `UserPortalURL`), `lastUpdated`, `lastAutoJoined`, `lastJoined`, `WiFiNetworkPasswordModificationDate`, `prevJoined` 입니다 [1]. 새 형식과 키 이름이 달라서, 파서가 두 형식을 모두 읽는지 먼저 확인합니다.

### 개인 MAC 주소 목록

이 목록에는 `SSID_STR`, `BSSID`, `lastUpdated`, `lastJoined`, `addedAt`, `PresentInKnownNetworks`, `LinkDownTimestamp`, `MacGenerationTimeStamp`, `FirstJoinWithNewMacTimestamp` 와 `PRIVATE_MAC_ADDRESS` 아래의 `PRIVATE_MAC_ADDRESS_IN_USE`, `PRIVATE_MAC_ADDRESS_VALUE`, `PRIVATE_MAC_ADDRESS_VALID` 키가 있습니다 [1]. `PresentInKnownNetworks` 라는 키 이름으로 보아, 알려진 네트워크 목록에서 빠진 네트워크도 이 목록에는 남을 수 있습니다.

iOS 18 이상의 개인 Wi-Fi 주소 설정은 다음과 같습니다 [2].

| 설정 | 동작 | 새 네트워크의 기본값 |
|---|---|---|
| 끔(Off) | 하드웨어 MAC 주소를 씀 | — |
| 고정(Fixed) | 개인 주소를 쓰되 바꾸지 않음 | WPA2 이상 보안의 네트워크 |
| 순환(Rotating) | 2주마다 다른 개인 주소로 바꿈 | 보안이 약하거나 없는 네트워크 |

### 지운 네트워크 목록

`com.apple.wifi.removed-networks.plist` 의 항목 키는 `wifi.network.ssid.<SSID>` 꼴이고, 항목마다 `RemovedAt`, `SSID`, `SupportedSecurityTypes` 키가 있습니다. 파일 이름과 `RemovedAt` 키로 보아 사용자가 지운 네트워크의 목록으로 보이지만, 어떤 조작이 이 목록에 항목을 더하는지는 공개 자료가 없습니다.

### 데이터 사용량 DB 의 ZWIFIDATA 표

`DataUsage.sqlite` 의 `ZWIFIDATA` 표에는 `ZSSID`, `ZBSSID`, `ZRSSI`, `ZLINKQUALITY`, `ZSTATE`, `ZISADHOC`, `ZISCAPTIVE`, `ZISLINKLOCALADDR`, `ZDHCPLEASETIME`, `ZTIMEAT`, `ZTIMESTAMP`, `ZLATITUDE`, `ZLONGITUDE`, `ZLOCACCURACY` 와 주고받은 바이트·TCP 통계 칸(`ZSTATSINBYTESACTUAL`, `ZSTATSINBYTESBASE`, `ZSTATSOUTBYTESACTUAL`, `ZSTATSOUTBYTESBASE`, `ZSTATSTCPCNTACTUAL`, `ZSTATSTCPCNTBASE`)이 있고, 그 밖에 칸 3개가 더 있습니다. 접속 지점과 위도·경도가 한 행에 모이는 표라서 위치 조사에 쓸 만하지만, `ZTIMEAT`·`ZSTATE` 값의 뜻과 시각 기준은 공개 자료가 없습니다. DB 의 다른 표는 [앱별 데이터 사용량](data-usage.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것**

- 알려진 네트워크 목록에 어떤 SSID 가 있으면, 수집 시점에 그 기기가 그 네트워크를 저장해 두고 있었다는 사실을 보여 줍니다.
- `JoinedByUserAt`·`JoinedBySystemAt`·`LastAssociatedAt` 같은 키에 값이 있으면, 그 시각에 해당 네트워크나 접속 지점에 붙은 기록이 있다는 사실까지 말할 수 있습니다.
- `BSSList` 나 `ZWIFIDATA` 에 위도·경도가 있으면, 기기가 그 접속 지점과 함께 그 위치 값을 적어 둔 기록이 있다는 뜻입니다.
- 지운 네트워크 목록에 항목이 있으면, 그 SSID 가 알려진 네트워크에서 빠진 기록으로 볼 수 있습니다.

**증명하지 못하는 것**

- 저장된 네트워크를 사용자가 직접 골라 들어갔다고 단정할 수 없습니다. `AddReason`·`BundleID` 에 추가 경위가 적혀 있을 수 있으니 먼저 확인하고, 기기 관리 프로필이 넣은 네트워크인지는 [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) 과 맞춰 봅니다.
- SSID 는 누구나 같은 이름으로 만들 수 있어서, 이름만으로 특정 장소의 공유기라고 할 수 없습니다. BSSID 와 위치 값을 함께 봅니다.
- 네트워크에 붙은 기록은 그 네트워크로 무엇을 주고받았는지 알려 주지 않습니다.
- 기기를 누가 들고 있었는지는 이 기록만으로 알 수 없고, [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 의 흐름으로 따로 판단합니다.

보고서에는 "이 기기의 알려진 네트워크 목록에 이 SSID 가 있고, 사용자 접속 시각 키의 값은 이것이다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

알려진 네트워크 목록의 시각 키는 이름대로 읽으면 추가(`AddedAt`), 갱신(`UpdatedAt`), 마지막 발견(`LastDiscoveredAt`), 사용자 접속(`JoinedByUserAt`), 시스템 접속(`JoinedBySystemAt`) 시각이고, 접속 지점마다 마지막 연결(`LastAssociatedAt`)과 위치를 잰 시각(`LocationTimestamp`)이 따로 있습니다 [1]. 이 키들이 UTC 인지 현지 시각인지, plist 날짜형인지 숫자형인지는 공개 자료가 없어 검체에서 확인합니다. plist 날짜형이면 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 의 규칙대로 읽고, 숫자면 자릿수로 기준을 가려 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 따라 바꿉니다.

`Last` 로 시작하는 키는 가장 최근 값 하나만 담는 것으로 보여서, 그 네트워크에 처음 붙은 때나 중간의 접속 이력은 이 목록에 없을 수 있습니다. 지운 네트워크 목록의 `RemovedAt` 과 `ZWIFIDATA` 의 `ZTIMESTAMP`·`ZTIMEAT` 도 시각 기준이 알려져 있지 않아서, 같은 접속을 다른 기록과 맞춰 기준을 확인한 뒤에 씁니다. 기기 시간대는 [시간대와 시각 설정](../system-account/time-zone.md) 에서 봅니다.

## 함정과 한계

암호화하지 않은 로컬 백업만 받았다면 알려진 네트워크 목록이 없을 수 있습니다. 이때 "와이파이 기록이 없다" 고 쓰지 말고, 지운 네트워크 목록과 `ZWIFIDATA` 를 보면서 수집 범위의 한계로 적습니다. 파일 시스템 추출에서 얻는 범위는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

파일 이름과 키 이름이 iOS 버전마다 달라서, 예전 형식만 읽는 파서는 새 기기에서 아무것도 못 찾거나 일부 키를 빠뜨릴 수 있습니다. iLEAPP 스크립트도 iOS 12.4 ~ 18.x 표본을 기준으로 만들어서 [1], 그보다 새 버전에서는 결과를 원본 plist 와 대조합니다.

개인 Wi-Fi 주소 때문에 공유기·무선망 기록의 MAC 주소가 기기 하드웨어 MAC 과 다를 수 있고, 같은 기기라도 네트워크마다, 순환 설정이면 시기마다 주소가 다릅니다 [2]. 네트워크 설정을 지운 뒤 같은 네트워크에 다시 들어가면 다른 개인 주소를 쓰고, iOS 18 이상에서는 네트워크를 지우면 그 네트워크의 개인 주소도 잊습니다(앞선 24시간 안에 이미 지운 적이 있으면 예외) [2]. 그래서 외부 기록의 MAC 주소가 기기 쪽 목록과 맞지 않는다고 해서 다른 기기라고 결론 내리지 않습니다.

사용자가 네트워크를 지우면 알려진 네트워크 목록에서는 빠지지만, 지운 네트워크 목록에 항목이 남을 수 있습니다. 지우기와 초기화 흔적을 함께 따지는 흐름은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 와 [초기화와 복원 흔적](../system-account/erase-restore.md) 에서 다룹니다.

## 직접 분석해 보기

로컬 백업이면 `Manifest.db` 를 SQLite 명령행 도구(`sqlite3` 등)로 열고, 이름에 wifi 가 든 파일을 먼저 뽑습니다.

```sql
SELECT fileID, domain, relativePath
FROM Files
WHERE relativePath LIKE '%wifi%'
ORDER BY domain, relativePath;
```

찾은 `fileID` 로 백업 폴더에서 파일을 찾아 복사본으로 옮기고, 헥스 편집기로 첫 8바이트를 봅니다. 아래는 이진 plist 명세로 만든 예시이고 특정 검체의 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07   문자
00000000  62 70 6C 69 73 74 30 30   bplist00
```

첫 8바이트가 `bplist00` 이면 이진 plist 이고, `<?xml` 로 시작하면 XML plist 입니다. 이진 plist 의 끝 부분(트레일러)에서 오프셋 표를 따라가는 방법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에 있습니다.

도구로는 iLEAPP 의 와이파이 스크립트(`appleWifiPlist.py`)가 알려진 네트워크·예전 형식·개인 MAC 목록을 한 번에 표로 뽑습니다 [1]. 스크립트가 다루지 않는 지운 네트워크 목록은 Python 표준 모듈로 직접 읽을 수 있습니다.

```python
import plistlib

with open("removed-networks-copy.plist", "rb") as f:
    data = plistlib.load(f)

for key, item in data.items():
    print(key, item.get("RemovedAt"), item.get("SupportedSecurityTypes"))
```

`ZWIFIDATA` 는 `DataUsage.sqlite` 복사본을 열어 `SELECT ZSSID, ZBSSID, ZTIMESTAMP, ZTIMEAT, ZLATITUDE, ZLONGITUDE, ZLOCACCURACY FROM ZWIFIDATA;` 로 먼저 훑고, 시각 칸은 기준을 확인한 뒤에 바꿉니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [앱별 데이터 사용량](data-usage.md) | 같은 DB 의 앱별 송수신 기록 |
| [중요 위치](../location/significant-locations.md) · [위치 기록 데몬](../location/routined.md) | 접속 지점의 위치 값과 실제 머문 곳이 맞는지 |
| [개인용 핫스폿](hotspot.md) | 기기가 스스로 와이파이를 내보낸 기록 |
| [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) | 관리 프로필이 넣은 네트워크인지 |
| [통합 로그에서 찾을 것](../logs/unified-log-events.md) | 접속·해제가 일어난 순간의 로그 |
| [전원 로그](../app-usage/powerlog.md) | 같은 시간대의 기기 상태 |
| [시간대와 시각 설정](../system-account/time-zone.md) | 시각을 현지 시각으로 바꿀 기준 |

여러 시각 기록을 시간순으로 합치는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 과 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등)에 아이폰 백업이나 파일 시스템 추출이 있으면 아래 질문으로 풀어 봅니다. 없으면 연습용 기기에서 네트워크 두세 개에 들어갔다가 하나를 지운 뒤 백업을 떠서 풀어 봅니다.

1. `Manifest.db` 에서 이름에 wifi 가 든 파일은 몇 개이고, 어느 도메인에 있습니까? 알려진 네트워크 목록이 있습니까?
2. 지운 네트워크 목록에 방금 지운 SSID 가 있습니까? `RemovedAt` 값은 어떤 형식이고, 지운 시각과 맞습니까?
3. `ZWIFIDATA` 에 들어갔던 네트워크의 SSID 가 있습니까? `ZTIMESTAMP` 를 어느 기준으로 읽어야 실제 접속 시각과 맞습니까?
4. 파일 시스템 추출이 있다면 알려진 네트워크 목록의 `JoinedByUserAt` 과 `JoinedBySystemAt` 중 어느 쪽에 값이 들어갔습니까?
5. 공유기 관리 화면에 보인 MAC 주소가 개인 MAC 주소 목록의 값과 같습니까?

## 참고 문헌

1. iLEAPP, `scripts/artifacts/appleWifiPlist.py` — GitHub abrignoni/iLEAPP — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appleWifiPlist.py
2. Apple 지원 문서 102509 (개인 Wi-Fi 주소) — https://support.apple.com/en-us/102509
