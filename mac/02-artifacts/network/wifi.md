---
title: "와이파이 기록"
parent: "아티팩트 · 네트워크"
nav_order: 1600
---

# 와이파이 기록 (Wi-Fi)

맥은 접속했던 와이파이 망을 시스템 설정 plist 에 남기고, 이 파일에서 망 이름(SSID)과 보안 방식, 마지막 접속 시각, 접속했던 무선 공유기(AP)의 MAC 주소(BSSID)를 읽으면 이 맥이 언제 어느 망에 붙었는지 가늠할 수 있습니다.

Apple 이 공개한 형식 명세가 없어서, 아래 키의 뜻은 키 이름과 공개 도구 mac_apt 가 값을 다루는 방식 [1]에서 읽어 낸 것입니다.

## 무엇을 기록하나 · 왜 생기나

맥이 와이파이 망에 붙으면 그 망이 "알고 있는 망" 목록에 들어가고, 이 목록이 시스템 설정 폴더의 plist 에 남습니다. 망 목록은 예전부터 쓰던 `com.apple.airport.preferences.plist` 와 새 형식 파일 `com.apple.wifi.known-networks.plist` 에 나뉘어 남습니다 [1]. 두 파일 모두 `/Library/Preferences` 아래에 있는 시스템 전체 설정이라서, 이 목록만으로는 어느 사용자 계정이 망을 골랐는지 가르지 못합니다.

망마다 이름과 보안 방식뿐만 아니라 접속 시각, 채널 기록, 접속했던 AP 의 BSSID 까지 남을 수 있고, 새 형식 파일에는 AP 항목에 위도·경도 칸이 붙기도 합니다 [1]. 그래서 이 기록은 "이 맥이 어떤 장소의 망을 알고 있었나" 를 좁히는 출발점이 됩니다.

## 위치와 버전별 차이

| 파일 | 경로 | 비고 |
|---|---|---|
| AirPort 설정 | `/Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist` | ForensicArtifacts 이름 `MacOSAirportPreferencesPlistFile`, 별칭 `MacOSWirelessNetworks` [2] |
| AirPort 설정 백업 | `/Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist.backup` | mac_apt 가 함께 읽습니다 [1] |
| 알고 있는 망 목록 | `/Library/Preferences/com.apple.wifi.known-networks.plist` | ForensicArtifacts 정의에는 없습니다 [2] |

`com.apple.airport.preferences.plist` 는 최상위 `Version` 값에 따라 형식이 달라지므로, 이 값을 먼저 보고 읽는 법을 고릅니다 [1].

| `Version` 값 | macOS 버전 | 망 목록이 있는 곳 |
|---|---|---|
| 없음 | 10.6 Snow Leopard | 옛 형식 |
| 12 | 10.8 | `RememberedNetworks` 배열 |
| 14 | 10.9 | `RememberedNetworks` 배열 |
| 1900, 2100 | 버전 대응 공개 자료 없음 | `KnownNetworks` 사전 |
| 2200 | 10.10 이후 | `KnownNetworks` 사전 |
| 2500 이상 | 버전 대응 공개 자료 없음 | `KnownNetworks` 사전(SSID 키를 푸는 법이 다름) |

새 형식 파일 `com.apple.wifi.known-networks.plist` 가 처음 생긴 macOS 버전과, 그 뒤에도 `com.apple.airport.preferences.plist` 에 `KnownNetworks` 가 계속 남는지는 공개 자료가 없습니다. 그래서 macOS 10.15 Catalina 이후 검체에서는 두 파일과 백업 파일을 모두 찾아 따로 적습니다. 새 파일의 `LastDiscoveredAt` 키는 macOS 13 에서 보입니다 [1].

## 구조

두 파일 모두 속성 목록 파일이고, 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)을 따릅니다.

### com.apple.airport.preferences.plist

`Version` 이 14 이하인 옛 형식은 최상위 `RememberedNetworks` 배열에 망이 들어 있습니다 [1]. 그보다 새 형식은 최상위에 `KnownNetworks`(사전), `PreferredOrder`(선호 순서 배열), `UpdateHistory`(배열)가 있고, `UpdateHistory` 항목마다 `Previous` 사전 안에 이전 판의 `Version`, `RememberedNetworks`, `KnownNetworks`, `PreferredOrder` 가 남습니다 [1]. `UpdateHistory` 쪽 망은 업데이트 전에 기억해 두었던 망이고, mac_apt 는 이를 "PREVIOUSREMEMBERED" 로 따로 분류합니다 [1].

`KnownNetworks` 사전의 키 이름은 SSID 를 16진수로 적은 문자열입니다. `Version` 이 2500 이상이면 앞 10글자를 떼고, 그 미만이면 앞 11글자와 끝 1글자를 뗀 뒤, 공백과 `<`, `>` 를 지우고 남은 16진수를 UTF-8 로 풀면 SSID 가 나옵니다 [1]. 떼어 내는 접두어 문자열의 실제 모양은 검체에서 확인합니다.

망 하나의 사전에는 아래 키가 있습니다 [1].

```
AutoLogin  Captive  Closed  CollocatedGroup  Disabled  LastConnected
Passpoint  PersonalHotspot  PossiblyHiddenNetwork  RoamingProfileType
SPRoaming  SSID  SSIDString  SecurityType  SystemMode  TemporarilyDisabled
ChannelHistory  (항목마다 Channel, Timestamp)
BSSIDHistory    (항목마다 BSSID, Timestamp)
```

`BSSIDHistory` 는 접속한 AP 의 MAC 과 시각을 담고, `Version` 1900 에 있습니다 [1]. 나머지 키의 정확한 뜻은 공개 자료가 없어서, 보고서에는 키 이름과 값을 그대로 옮기고 뜻을 덧붙이지 않습니다.

### com.apple.wifi.known-networks.plist

최상위가 망마다 하나씩인 사전이고, 망 하나에 아래 키가 있습니다 [1].

| 키 | 형태 | 비고 |
|---|---|---|
| `SSID` | 바이트 | UTF-8 로 풀면 망 이름입니다 |
| `AddReason` | | 값 목록은 공개 자료 없음 |
| `SupportedSecurityTypes` | | 보안 방식 |
| `SystemMode` | | |
| `AddedAt` | 시각 | 목록에 들어간 때로 보이는 키 |
| `JoinedBySystemAt` | 시각 | 시스템이 붙은 때로 보이는 키 |
| `JoinedByUserAt` | 시각 | 사용자가 붙은 때로 보이는 키 |
| `UpdatedAt` | 시각 | |
| `LastDiscoveredAt` | 시각 | macOS 13 에서 보임 |

`__OSSpecific__` 사전 안에는 `BSSIDList`(항목마다 `LEAKY_AP_BSSID`), `CollocatedGroup`(문자열 `wifi.ssid.` 뒤에 SSID 16진수), `ChannelHistory`(`Channel`, `Timestamp`), `RoamingProfileType`, `CaptiveProfile/CaptiveNetwork`, `TemporarilyDisabled` 가 있습니다 [1].

`BSSList` 배열은 AP 마다 `BSSID`, `LastAssociatedAt`, `Location` 사전을 담고, `Location` 안에는 `LocationLatitude`, `LocationLongitude`, `LocationTimestamp`, `LocationAccuracy` 가 있습니다 [1]. 어떤 조건에서 좌표가 기록되는지는 공개 자료가 없습니다.

## 증거로서 의미

**증명하는 것.** 망 항목이 있으면 이 맥이 그 SSID 를 알고 있는 망으로 적어 두었다는 기록이 있다는 뜻이고, `BSSIDHistory` 나 `BSSList` 에 BSSID 가 있으면 그 MAC 주소의 AP 가 이 맥의 기록에 남아 있다는 뜻입니다 [1]. `JoinedByUserAt` 과 `JoinedBySystemAt` 은 키 이름으로 보아 사용자가 직접 고른 접속과 시스템의 자동 접속을 가를 수 있는 한 쌍이지만, 이 구분은 키 이름에서 끌어낸 해석이라서 보고서에는 키 이름을 함께 적습니다. `UpdateHistory` 에서 나온 망은 macOS 업데이트 전부터 이 맥이 알고 있던 망이라는 기록으로 읽습니다 [1].

**증명하지 못하는 것.** SSID 는 누구나 같은 이름으로 만들 수 있어서, 이름만으로 특정 장소의 망이라고 단정하지 않고 BSSID 와 다른 기록으로 받칩니다. 이 파일은 시스템 전체 설정이라 어느 사용자가 붙었는지 알려 주지 않고, 그 망으로 무엇을 주고받았는지도 알려 주지 않습니다. 목록에서 망을 지우는 동작이 파일에 어떻게 남는지는 공개 자료가 없어서, 목록에 없다는 사실만으로 그 망에 붙은 적이 없다고 쓰지 않습니다. `Location` 좌표도 기록되는 조건이 알려지지 않아서, 좌표가 있으면 "이 AP 항목에 이 좌표가 적혀 있다" 까지만 씁니다.

보고서에는 "이 맥의 알고 있는 망 목록에 SSID 이 값이 있고, `JoinedByUserAt` 값이 이 시각이다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

`com.apple.wifi.known-networks.plist` 의 시각 키는 plist 날짜 형식으로 저장된 값으로 보입니다 [1]. plist 날짜 값의 기준은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)과 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다. 도구가 보여 주는 시각이 UTC 인지 분석 PC 의 현지 시각으로 바꾼 값인지는 도구 설정에서 먼저 확인합니다.

mac_apt 는 망의 마지막 연결 시각을 `JoinedByUserAt` 과 `JoinedBySystemAt` 가운데 늦은 값으로 계산하고, 둘 중 하나만 있으면 있는 값을 씁니다 [1]. 도구 결과의 "마지막 연결" 칸은 이렇게 계산한 값이라서, 보고서에는 원래 두 키의 값을 함께 적어 두면 사용자 접속인지 자동 접속인지를 나중에 다시 따질 수 있습니다.

`com.apple.airport.preferences.plist` 의 `LastConnected`, `ChannelHistory` 와 `BSSIDHistory` 의 `Timestamp` 가 어떤 형식으로 저장되는지는 공개 자료가 없어 검체에서 확인합니다.

## 함정과 한계

- **파일 세 개.** 옛 파일, 그 백업, 새 형식 파일에 서로 다른 망이 남을 수 있어서 한 파일만 보면 망을 놓칩니다 [1].
- **수집 정의에서 빠진 새 파일.** ForensicArtifacts 정의에는 `com.apple.airport.preferences.plist` 만 있고 `com.apple.wifi.known-networks.plist` 는 없어서 [2], 이 정의로 수집 목록을 만들었다면 새 파일이 빠지지 않았는지 확인합니다.
- **버전마다 다른 SSID 키.** `KnownNetworks` 의 SSID 키는 `Version` 2500 을 기준으로 떼어 낼 글자 수가 달라서 [1], 직접 풀 때 `Version` 을 먼저 봅니다.
- **업데이트 전 망이 섞인 목록.** `UpdateHistory` 안의 망은 업데이트 전 기록이라서 [1], 현재 목록과 섞어 한 표에 두면 시기를 잘못 읽습니다.
- **뜻이 알려지지 않은 키.** `Closed`, `AddReason`, `LEAKY_AP_BSSID` 같은 키의 뜻은 공개 자료가 없습니다. 도구가 이런 키에 설명을 붙여 보여 주면 그 근거를 확인한 뒤에 씁니다.
- **저장된 와이파이 암호.** 암호가 어느 키체인에 들어가는지는 검체에서 확인하고, 키체인 구조는 [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md)에서 다룹니다.
- **로그 쪽 기록.** 통합 로그의 와이파이 관련 서브시스템 이름과 별도 와이파이 로그 파일은 공개 자료가 없어 검체에서 확인합니다.

## 직접 분석해 보기

원본을 바로 열지 말고 세 파일을 파일 시각을 지키는 방식으로 작업 폴더에 복사한 뒤 사본으로 봅니다.

### 헥스로 한 번

아래는 SSID 16진수를 푸는 방식 [1]에 맞춰 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. 망 이름 `CafeNet` 은 예시로 지은 이름입니다.

```
CollocatedGroup 값:  wifi.ssid.436166654e6574

접두어 wifi.ssid. 를 떼면   436166654e6574
두 글자씩 바이트로          43 61 66 65 4e 65 74
UTF-8 로 풀면               C  a  f  e  N  e  t   → CafeNet
```

`com.apple.wifi.known-networks.plist` 의 `SSID` 는 바이트 값이라 [1], 헥스 편집기에서는 같은 바이트 `43 61 66 65 4e 65 74` 가 그대로 보입니다. 바이너리 plist 에서 이 바이트가 담긴 객체를 찾아가는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)을 따릅니다.

### 공개 도구로 한 번

macOS 의 `plutil` 로 사본을 엽니다.

```
plutil -p com.apple.airport.preferences.plist
plutil -p com.apple.airport.preferences.plist.backup
plutil -p com.apple.wifi.known-networks.plist
```

첫 파일에서는 `Version` 값을 먼저 보고 망 목록이 `RememberedNetworks` 에 있는지 `KnownNetworks` 에 있는지 정하고, 새 형식 파일에서는 망마다 `JoinedByUserAt`, `JoinedBySystemAt`, `BSSList` 를 옮겨 적습니다. mac_apt WIFI 플러그인을 돌려 같은 망이 같은 값으로 나오는지 맞춰 보면, 직접 읽은 값과 도구 결과를 서로 검증할 수 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [네트워크 인터페이스와 설정 (SystemConfiguration)](network-interfaces.md) | DHCP 임대 파일의 `SSID` 와 임대 시작 시각, 공유기 MAC [3] |
| [앱별 네트워크 사용량 (netusage)](netusage.md) | 그 무렵 프로세스별 Wi-Fi 송수신 칸 |
| [hosts와 DNS 설정 (hosts·DNS)](hosts-dns.md) | 그 망에서 쓰인 DNS 설정 |
| [공유 폴더 연결 기록 (SMB·AFP)](network-shares.md) | 그 망 안의 서버에 붙은 흔적 |
| [전원·잠자기 기록 (pmset)](../logs/power-events.md) | 접속 시각 무렵 맥이 깨어 있었는지 |
| [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md) | 시스템 전체 기록을 사용자와 잇는 흐름 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. `com.apple.airport.preferences.plist` 의 `Version` 값은 무엇이고, 망 목록은 `RememberedNetworks` 와 `KnownNetworks` 가운데 어디에 있나요?
2. `KnownNetworks` 의 키 하나를 골라 SSID 16진수를 직접 풀고, `SSIDString` 값과 같은지 확인해 보세요.
3. `UpdateHistory` 에 이전 판의 망 목록이 있나요? 있다면 현재 목록에 없는 망을 따로 표로 적어 보세요.
4. `com.apple.wifi.known-networks.plist` 가 있다면 망마다 `JoinedByUserAt` 과 `JoinedBySystemAt` 을 나란히 적고, 어느 쪽이 더 늦은지 보세요.
5. DHCP 임대 파일의 `SSID` 가 알고 있는 망 목록에 있나요? 있다면 임대 시작 시각과 접속 시각이 가까운가요?

## 참고 문헌

1. mac_apt `airport_preferences.py` WIFI 플러그인 소스 (Michael Geyer, Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/airport_preferences.py
2. ForensicArtifacts `macos.yaml` (MacOSAirportPreferencesPlistFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
3. mac_apt `networking.py` NETWORKING 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/networking.py
