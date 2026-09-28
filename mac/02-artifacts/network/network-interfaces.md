---
title: "네트워크 인터페이스와 설정"
parent: "아티팩트 · 네트워크"
nav_order: 1610
---

# 네트워크 인터페이스와 설정 (SystemConfiguration)

`/Library/Preferences/SystemConfiguration/` 폴더의 `NetworkInterfaces.plist` 와 `preferences.plist`, 그리고 DHCP 임대 파일을 보면 이 맥에 어떤 네트워크 인터페이스가 있었고 MAC 주소가 무엇이었는지, 네트워크 서비스를 어떻게 설정했는지, 마지막으로 어떤 IP 와 공유기를 받았는지 알 수 있습니다.

Apple 이 공개한 형식 명세는 없어서, 키의 뜻은 키 이름과 공개 도구의 처리 방식에서 읽어 낼 수 있는 만큼만 적습니다 [1].

## 무엇을 기록하나 · 왜 생기나

macOS 의 시스템 구성 (SystemConfiguration) 설정은 네트워크를 인터페이스와 서비스로 나눠 저장합니다. `NetworkInterfaces.plist` 에는 운영체제가 알아본 인터페이스 목록이 BSD 이름(예 `en0`)과 MAC 주소와 함께 들어 있고, `preferences.plist` 의 `NetworkServices` 에는 인터페이스마다 붙은 서비스 설정, 곧 IP 를 받는 방식과 DNS, 프록시 같은 값이 들어 있습니다 [1]. 인터페이스가 DHCP 로 주소를 받으면 `/private/var/db/dhcpclient/leases/` 폴더에 그 인터페이스의 임대 파일이 남고, 여기에는 받은 IP 와 공유기 정보뿐만 아니라 그때 붙어 있던 와이파이 이름까지 들어 있습니다 [1].

세 곳을 함께 보면 "이 맥이 어떤 하드웨어 주소로, 어떤 설정을 거쳐, 마지막으로 어느 네트워크에 붙어 있었나" 를 한 줄로 이을 수 있습니다.

## 위치와 버전별 차이

| 파일 | 경로 | 알려 주는 것 |
|---|---|---|
| 인터페이스 목록 | `/Library/Preferences/SystemConfiguration/NetworkInterfaces.plist` [1] | 인터페이스 BSD 이름, 종류, MAC 주소 |
| 시스템 구성 설정 | `/Library/Preferences/SystemConfiguration/preferences.plist` [1][2] | 네트워크 서비스별 설정 |
| DHCP 임대 | `/private/var/db/dhcpclient/leases/` 아래 인터페이스별 파일 [1] | 받은 IP, 임대 시작 시각, 공유기, SSID |
| DHCP 식별자 | `/private/var/db/dhcpclient/DUID_IA.plist` [1] | mac_apt 는 경로만 적어 두고 아직 읽지 않습니다 |

`preferences.plist` 는 ForensicArtifacts 에 `MacOSSystemConfigurationPreferencesPlistFile` 로 올라 있습니다 [2]. 함께 네트워크 설정을 담는 `/private/var/run/resolv.conf` 와 `/private/etc/hosts` [1]는 [hosts와 DNS 설정 (hosts·DNS)](hosts-dns.md)에서 다룹니다.

iOS 에서는 `NetworkInterfaces.plist` 가 `/private/var/Preferences/SystemConfiguration/` 아래에 있고, iOS 14 의 DHCP 임대 파일에는 `.plist` 확장자가 붙습니다 [1]. macOS 버전에 따라 이 파일들의 키 배치가 달라질 수 있어서, 기기마다 실제 키를 열어 보고 적습니다.

## 구조

`NetworkInterfaces.plist`, `preferences.plist`, DHCP 임대 파일은 모두 속성 목록 파일이고, 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)을 따릅니다.

### NetworkInterfaces.plist

최상위에는 정보 키 `Model`, `__VERSION__` 과, 이름이 `Interface` 로 시작하는 배열이 있고, 이 배열이 인터페이스 목록입니다 [1]. 인터페이스 항목 하나에는 아래 키가 있습니다 [1].

| 키 | 형태 | 비고 |
|---|---|---|
| `BSD Name` | 문자열 | 예 `en0` |
| `IOMACAddress` | 바이너리 | MAC 주소로 풀어 읽습니다 |
| `IOInterfaceType` | 정수 | |
| `IOInterfaceUnit` | 정수 | |
| `IOInterfaceNamePrefix` | | |
| `IOBuiltin` | | |
| `IOPathMatch` | | |
| `Active` | | |
| `SCNetworkInterfaceType` | | |
| `SCNetworkInterfaceInfo` | 사전 | 안에 `UserDefinedName` |

비고가 빈 키는 값의 뜻과 가능한 값 목록을 실제 데이터로 확인합니다.

### preferences.plist 의 NetworkServices

`NetworkServices` 사전의 키는 서비스 UUID 이고, 서비스 하나에 아래 키가 있습니다 [1].

| 키 | 안에 든 것 | 자세한 내용 |
|---|---|---|
| `UserDefinedName` | 서비스 이름 | |
| `Interface` | `DeviceName`, `Hardware`, `Type`, `UserDefinedName` | 이 서비스가 붙은 인터페이스 |
| `IPv4/ConfigMethod`, `IPv6/ConfigMethod` | 주소를 설정하는 방식 | 값은 실제 데이터로 확인 |
| `DNS` | DNS 설정 | [hosts와 DNS 설정 (hosts·DNS)](hosts-dns.md) |
| `Proxies` | 프록시 설정, 안에 `ExceptionsList` | |
| `SMB` | `NetBIOSName`, `Workgroup` 등 | [공유 폴더 연결 기록 (SMB·AFP)](network-shares.md) |
| `PPP`, `Modem` | PPP·모뎀 설정 | VPN 쪽은 [VPN 구성 (VPN)](vpn.md) |

`Interface/DeviceName` 이 `NetworkInterfaces.plist` 의 `BSD Name` 과 같은 값을 쓰는지 맞춰 보면 서비스와 인터페이스를 이을 수 있습니다. 같은 파일에 있는 컴퓨터 이름과 호스트 이름 키는 [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../system-account/computer-name-hardware.md)에서 다룹니다. 서비스 묶음을 가리키는 `Sets`, `CurrentSet` 같은 키는 실제 기기에서 확인합니다. mac_apt 는 `VirtualNetworkInterfaces/Bridge` 를 읽지 않아서 [1], 이 값은 도구 결과에 나오지 않습니다.

### DHCP 임대 파일

`/private/var/db/dhcpclient/leases/` 아래 파일 이름이 `인터페이스이름,MAC주소` 모양이고, 쉼표 앞이 인터페이스, 뒤가 MAC 입니다 [1]. 파일 안에는 아래 키가 있습니다 [1].

| 키 | 알려 주는 것 |
|---|---|
| `IPAddress` | 받은 IP 주소 |
| `LeaseStartDate` | 임대 시작 시각 |
| `LeaseLength` | 임대 기간 |
| `RouterIPAddress` | 공유기 IP |
| `RouterHardwareAddress` | 공유기 MAC(바이너리) |
| `SSID` | 그때 붙어 있던 와이파이 이름 |
| `PacketData` | DHCP 패킷 원본 |
| `ClientIdentifier` | iOS 14 에서 보이는 키, 첫 바이트 뒤가 MAC |

## 증거로서 의미

**증명하는 것.** `NetworkInterfaces.plist` 는 이 맥이 알아본 인터페이스와 그 `IOMACAddress` 값을 알려 주고, 네트워크 장비 기록에 남은 MAC 과 이 맥을 잇는 근거가 됩니다 [1]. `preferences.plist` 의 서비스 항목은 어떤 인터페이스에 어떤 주소 설정 방식과 DNS, 프록시가 설정되어 있었는지 알려 줍니다 [1]. DHCP 임대 파일 하나에서 마지막으로 받은 IP, 임대 시작 시각, 공유기 IP 와 MAC, 그때의 와이파이 이름을 함께 볼 수 있어서 [1], 사내 네트워크 기록과 시각·IP 를 맞추는 출발점이 됩니다.

**증명하지 못하는 것.** 임대 파일에는 마지막 임대만 남아 있을 수 있어서, 임대 파일을 이 맥의 접속 이력 전체로 읽지 않습니다. 이 파일들은 시스템 전체 설정이라 어느 사용자가 네트워크를 썼는지 알려 주지 않고, 무엇을 주고받았는지도 알려 주지 않습니다. `IOMACAddress` 는 운영체제가 적어 둔 값이고, 특정 시각에 이 맥이 실제로 어떤 MAC 으로 통신했는지는 이 값만으로 단정하지 않습니다. 프록시 설정이 있으면 트래픽을 한곳으로 모으는 설정이 있었다는 기록이지만, 누가 왜 넣었는지는 다른 기록으로 받칩니다.

보고서에는 "`en0` 인터페이스의 DHCP 임대 파일에 이 IP 와 임대 시작 시각, SSID 가 적혀 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`NetworkInterfaces.plist` 와 `preferences.plist` 의 위 키에는 시각 값이 없습니다. 설정이 언제 바뀌었는지는 파일 수정 시각과 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 좁히고, 파일 수정 시각은 마지막으로 바뀐 때만 알려 줄 뿐 어느 키가 그때 바뀌었는지는 알려 주지 않습니다.

DHCP 임대 파일의 `LeaseStartDate` 는 plist 날짜 형식으로 보이고, `LeaseLength` 의 단위는 실제 데이터로 확인해야 합니다. 값을 읽을 때는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에서 기준을 맞춰 보고, 도구가 보여 주는 시각이 UTC 인지 현지 시각으로 바꾼 값인지 함께 적습니다.

## 함정과 한계

- **이력이 쌓이지 않을 수 있는 임대 파일.** 임대 파일에는 마지막 임대 한 건만 남았다고 보고, 다른 시기는 다른 기록으로 채웁니다.
- **파일 이름에만 있는 정보.** 인터페이스 이름과 MAC 이 파일 이름에 들어 있어서 [1], 파일 내용만 뽑아 두면 어느 인터페이스의 임대인지 잃습니다.
- **읽지 않는 파일.** `DUID_IA.plist` 는 mac_apt 가 아직 읽지 않아서 [1], 도구 결과에 없다고 파일이 없다는 뜻은 아닙니다.
- **여러 페이지가 나눠 보는 한 파일.** `preferences.plist` 한 파일에 네트워크 서비스, DNS, SMB, 컴퓨터 이름이 함께 들어 있어서, 한 페이지 관점으로만 보면 다른 키를 놓칩니다.
- **뜻을 단정할 수 없는 키.** `Active`, `IOBuiltin`, `ConfigMethod` 값처럼 뜻이 정해져 있지 않은 키는 도구가 설명을 붙여 보여 주더라도 근거를 확인한 뒤에 씁니다.

## 직접 분석해 보기

원본을 바로 열지 말고 `NetworkInterfaces.plist`, `preferences.plist`, DHCP 임대 폴더 전체를 파일 이름과 시각을 지키는 방식으로 작업 폴더에 복사한 뒤 사본으로 봅니다.

### 헥스로 한 번

`IOMACAddress` 와 `RouterHardwareAddress` 는 바이너리 값이라 [1], 헥스로 보면 바이트가 그대로 나옵니다. 아래는 문서용 예시 MAC 범위의 값으로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다.

```
IOMACAddress 바이트:   00 00 5E 00 53 01
콜론으로 이으면:       00:00:5e:00:53:01
```

바이너리 plist 에서 이 바이트가 담긴 객체를 찾아가는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)을 따릅니다. 임대 파일 이름에 들어 있는 MAC 과 `NetworkInterfaces.plist` 의 같은 인터페이스 `IOMACAddress` 가 같은 바이트인지 맞춰 봅니다.

### 공개 도구로 한 번

macOS 의 `plutil` 로 사본을 엽니다.

```
plutil -p NetworkInterfaces.plist
plutil -p preferences.plist
plutil -p "leases/<임대 파일 이름>"
```

인터페이스 목록에서 `BSD Name` 과 `IOMACAddress` 를 표로 옮기고, `NetworkServices` 에서 서비스마다 `Interface/DeviceName` 과 `ConfigMethod`, `Proxies` 를 옮겨 적은 뒤, 임대 파일에서 `IPAddress`, `LeaseStartDate`, `RouterHardwareAddress`, `SSID` 를 덧붙입니다. mac_apt NETWORKING 플러그인 [1]을 돌려 같은 값이 나오는지 맞춰 보면 직접 읽은 값과 도구 결과를 서로 검증할 수 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [와이파이 기록 (Wi-Fi)](wifi.md) | 임대 파일의 `SSID` 가 알고 있는 망 목록에 있는지, 접속 시각과 임대 시작 시각이 가까운지 |
| [hosts와 DNS 설정 (hosts·DNS)](hosts-dns.md) | 서비스별 `DNS` 와 `resolv.conf` |
| [VPN 구성 (VPN)](vpn.md) | `PPP` 사전이 있는 서비스가 VPN 설정인지 |
| [공유 폴더 연결 기록 (SMB·AFP)](network-shares.md) | 서비스의 `SMB` 값 |
| [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../system-account/computer-name-hardware.md) | 네트워크에 보인 이 맥의 이름 |
| [원격 접속 (Remote Access)](remote-access/index.md) | 접속 기록의 주소가 그때 쓰던 네트워크 대역인지 |

## 실습

공개 시험 데이터(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. `NetworkInterfaces.plist` 의 인터페이스마다 `BSD Name` 과 `IOMACAddress` 를 표로 정리해 보세요.
2. `NetworkServices` 에서 서비스마다 어느 인터페이스에 붙어 있는지 `Interface/DeviceName` 으로 찾아 1번 표와 이어 보세요.
3. `Proxies` 에 값이 들어 있는 서비스가 있나요? 있다면 `ExceptionsList` 까지 옮겨 적어 보세요.
4. DHCP 임대 폴더에 파일이 몇 개 있고, 파일 이름의 MAC 이 1번 표의 MAC 과 같은가요?
5. 임대 파일의 `SSID` 와 `LeaseStartDate` 를 와이파이 기록의 접속 시각과 나란히 놓아 보세요.

## 참고 문헌

1. mac_apt `networking.py` NETWORKING 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/networking.py
2. ForensicArtifacts `macos.yaml` (MacOSSystemConfigurationPreferencesPlistFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
