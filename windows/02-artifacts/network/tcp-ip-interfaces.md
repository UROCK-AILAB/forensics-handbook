# 네트워크 인터페이스 설정 (TCP/IP Interfaces)

## 한 줄 요약

SYSTEM 하이브의 `Tcpip\Parameters\Interfaces` 키에는 네트워크 인터페이스마다 IP 설정과 DHCP 임대 정보가 남습니다. 무선 인터페이스 아래에는 무선 네트워크(SSID)마다 하위 키가 따로 있습니다.

## 무엇을 기록하나 · 왜 생기나

- 인터페이스 하나가 인터페이스 GUID 이름의 하위 키 하나입니다.
- DHCP 클라이언트 서비스가 임대 값(`LeaseObtainedTime` 등)을 만들고 관리합니다.
- DHCP 를 쓰는 인터페이스에는 받은 IP 주소, DHCP 서버, 기본 게이트웨이, 임대 시각이 남습니다.
- 무선 인터페이스 키 아래에는 SSID 별 하위 키가 있습니다. 하위 키마다 그 네트워크에서 받은 임대 값이 따로 들어 있습니다.

## 위치와 버전별 차이

```
HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\<인터페이스 GUID>
HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\<인터페이스 GUID>\<SSID 하위 키>
```

- 오프라인 이미지에는 `CurrentControlSet` 이 없습니다. 공개 도구 RegRipper 의 nic2 플러그인은 SYSTEM 하이브의 `ControlSet00<현재 번호>\Services\Tcpip\Parameters\Interfaces` 를 읽습니다. 컨트롤 세트는 [레지스트리 하이브 구조](/01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.
- 이 플러그인은 인터페이스 GUID 하위 키와 그 아래 하위 키(무선 SSID)까지 돕니다.

**인터페이스 GUID 를 어댑터 이름으로 바꾸기**

```
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkCards\<번호>
    ServiceName   인터페이스 GUID
    Description   어댑터 이름
```

- `ServiceName` 이 인터페이스 GUID 이고, `Description` 이 어댑터 이름입니다. (확인 범위: Win11 25H2 한 대)
- Windows 11 PC 한 대에서 `ServiceName` 4개 모두 Tcpip `Interfaces` 의 하위 키 이름과 같았습니다. (확인 범위: Win11 25H2 한 대)
- Wi-Fi 프로필 폴더의 인터페이스 GUID 도 이 키 이름과 같았습니다. [Wi-Fi 프로필](/02-artifacts/network/wlan-profiles.md) 에서 다룹니다.

**Windows 11 PC 한 대에서 본 것** (확인 범위: Win11 25H2 한 대)

- 인터페이스 하위 키가 12개였습니다. 그중 2개는 값이 하나도 없었습니다.
- `Tcpip6\Parameters\Interfaces` 도 있었습니다(하위 키 13개). 이 페이지에서는 내용을 다루지 않습니다.
- 고정 IP 인터페이스는 없었습니다. 고정 IP 일 때의 값 이름은 이번에 확인하지 못했습니다.

**버전별 차이**

| Windows | 근거 | 내용 |
|---|---|---|
| 2000 | Microsoft 보관 문서 | `LeaseObtainedTime` 의 뜻, T1·T2 기본값 |
| 11 25H2 | 한 PC 관찰 | 아래 "구조" 절의 값 목록, 시각 기준 |

- `LeaseObtainedTime` 을 설명한 공식 문서는 Windows 2000 자료(보관 문서)입니다. 이후 버전의 공식 문서는 이번에 열어 보지 못했습니다.
- Windows 11 PC 한 대에서 같은 값 이름과 같은 계산이 맞았습니다. 아래 "임대 시각" 절에 적습니다.

## 구조

### 인터페이스 키의 값 (DHCP)

Windows 11 PC 한 대에서 DHCP 를 쓰는 인터페이스에 있던 값입니다. 묶음은 값 이름으로 나눈 것입니다. (확인 범위: Win11 25H2 한 대)

| 묶음 | 값 |
|---|---|
| 주소 | `EnableDHCP`, `DhcpIPAddress`, `DhcpSubnetMask`, `DhcpSubnetMaskOpt`(REG_MULTI_SZ), `AddressType` |
| 서버·도메인 | `DhcpServer`, `NameServer`, `DhcpNameServer`, `Domain`, `DhcpDomain` |
| 게이트웨이 | `DhcpDefaultGateway`(REG_MULTI_SZ), `DhcpGatewayHardware`(REG_BINARY), `DhcpGatewayHardwareCount` |
| 임대 | `Lease`, `LeaseObtainedTime`, `T1`, `T2`, `LeaseTerminatesTime` |
| 기타 | `DhcpNetworkHint`, `DhcpInterfaceOptions`(REG_BINARY), `IsServerNapAware`, `DhcpConnForceBroadcastFlag` |

### 임대 시각

Microsoft 문서가 적는 내용은 아래와 같습니다.

- `LeaseObtainedTime` 은 REG_DWORD 입니다.
- 값은 1970-01-01 0시부터 흐른 초입니다.
- 인터페이스가 IP 주소 임대를 받은 시각입니다.
- 클라이언트는 T1 이 지나면 임대 갱신을 시도합니다. 필요하면 T2 에 다시 시도합니다.
- 기본값은 T1 이 임대 기간의 1/2, T2 가 임대 기간의 7/8(87.5%) 입니다.

RegRipper nic2 플러그인은 `T1`, `T2`, 이름이 `Time` 으로 끝나는 값을 Unix 시각으로 바꿔 UTC(Z)로 표시합니다.

Windows 11 PC 한 대에서 본 관계는 아래와 같습니다. (확인 범위: Win11 25H2 한 대)

| 값 | 이 PC 에서 맞은 계산 |
|---|---|
| `Lease` | 86400(24시간)과 3600(1시간)이 나왔습니다 |
| `LeaseTerminatesTime` | `LeaseObtainedTime` + `Lease` |
| `T1` | `LeaseObtainedTime` + `Lease` / 2 |

### 무선 네트워크별 하위 키

- 무선 인터페이스의 GUID 키 아래 하위 키는 무선 SSID 별로 있습니다.
- 하위 키 이름과 `DhcpNetworkHint` 값은 SSID 를 16진수로 쓰되, 바이트마다 두 자리(니블) 순서를 바꾼 값입니다.

Windows 11 PC 한 대에서 본 모습은 아래와 같습니다. (확인 범위: Win11 25H2 한 대)

- 무선 인터페이스 키 아래에 하위 키가 3개 있었습니다.
- 하위 키 이름은 그 안의 `DhcpNetworkHint` 값과 같았습니다.
- 두 자리씩 바꾸면 [네트워크 목록](/02-artifacts/network/networklist.md) 의 `Nla\Wireless` 에 있는 SSID 16진수와 같았습니다(3/3).
- 하위 키마다 `DhcpIPAddress`·`DhcpServer`·`LeaseObtainedTime` 등 부모 키와 같은 값 묶음이 있었습니다.
- 지금 연결된 네트워크(부모 키의 `DhcpNetworkHint`)와 같은 이름의 하위 키는 없었습니다. 하위 키가 언제 만들어지는지는 확인하지 못했습니다.

### DhcpGatewayHardware

Windows 11 PC 한 대에서 4개 모두 14바이트였습니다. (확인 범위: Win11 25H2 한 대)

| 오프셋 | 크기 | 이 PC 에서 본 내용 |
|---|---|---|
| 0 | 4 | 게이트웨이 IPv4 주소. `DhcpDefaultGateway` 와 같았습니다 |
| 4 | 4 | 정수 6 |
| 8 | 6 | MAC 주소. 네트워크 목록의 `DefaultGatewayMac` 과 같았습니다 |

- 가운데 4바이트가 MAC 길이인지는 확인하지 못했습니다.
- `DhcpGatewayHardwareCount` 는 1 이었습니다.

## 증거로서 의미

### 증명하는 것

- 이 인터페이스가 어느 DHCP 서버에서 어떤 IP 주소를 언제 받았는지 알 수 있습니다. 부모 키에는 한 벌의 임대 값이 있습니다.
- 기본 게이트웨이의 IP 주소와 MAC 주소를 알 수 있습니다.
- 무선 인터페이스면 SSID 하위 키마다 그 네트워크에서 받은 임대 값을 볼 수 있습니다.
- 인터페이스 GUID 를 `NetworkCards` 로 어댑터 이름에 이을 수 있습니다.

### 증명하지 못하는 것

- **이전 임대 이력 전체.** 이 키에서 앞선 임대들이 어디에 남는지는 확인하지 못했습니다. 임대를 새로 받을 때 덮어쓰는 것으로 보이지만 확인하지 못했습니다.
- **누가 썼는지.** SYSTEM 하이브 기록이라 사용자를 적는 칸이 없습니다.
- **모든 무선 네트워크.** 한 PC 에서는 지금 연결된 네트워크의 하위 키가 없었습니다. 하위 키가 없다고 그 네트워크에 연결하지 않은 것은 아닙니다. (확인 범위: Win11 25H2 한 대)
- **장소.** IP 주소와 게이트웨이 MAC 은 다른 자료와 맞춰 볼 수 있는 값입니다. 이 값만으로 장소를 단정하지 않습니다.

보고서에는 "이 인터페이스 키에 DHCP 서버 이 주소에서 이 IP 를 받은 임대 값이 있고, 임대 받은 시각은 이 시각(UTC)으로 기록돼 있다" 처럼 씁니다.

## 시각 해석

- `LeaseObtainedTime` 은 1970-01-01 0시부터 흐른 초입니다. Microsoft 문서는 기준 시간대를 적지 않습니다. RegRipper nic2 플러그인은 UTC 로 읽고, Windows 11 PC 한 대에서도 UTC 였습니다. (확인 범위: Win11 25H2 한 대) 변환은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- `T1`·`T2`·`LeaseTerminatesTime` 도 같은 Unix 시각으로 읽습니다. 기간이 아니라 시각입니다.
- 같은 순간이 두 기록에 다른 기준으로 적혀 있었습니다. (확인 범위: Win11 25H2 한 대)

| 기록 | 형식 | 적힌 값 |
|---|---|---|
| `LeaseObtainedTime` | Unix 초, UTC | 원시값 1790135324 = 2026-09-23 03:48:44 UTC |
| NetworkProfile/Operational 10000 이벤트 | UTC | 03:48:44 로 초까지 같았습니다 |
| `ipconfig /all` 의 "Lease Obtained" | 현지 시각 | 같은 순간을 현지 시각으로 보여 줬습니다 |
| 네트워크 목록 `DateLastConnected` | SYSTEMTIME, 현지 시각 | 같은 순간을 현지 시각으로 적었습니다 |

- 두 레지스트리 값을 나란히 놓을 때는 한쪽을 시간대로 바꿔 맞춥니다. 시간대는 [시간대 설정](/02-artifacts/system-account/time-zone.md) 에서 확인합니다.
- 한 PC 에서 1시간짜리 임대도 있었습니다. 임대를 갱신할 때 `LeaseObtainedTime` 이 바뀌는지는 확인하지 못했습니다. (확인 범위: Win11 25H2 한 대)

## 함정과 한계

- **오프라인에서는 `CurrentControlSet` 이 없습니다.** 현재 쓰는 컨트롤 세트 번호를 먼저 확인하고 `ControlSet00<번호>` 를 읽습니다.
- **SSID 하위 키 이름을 그대로 풀면 틀립니다.** 바이트마다 두 자리를 바꾼 값입니다. 바꾸지 않고 ASCII 로 풀면 엉뚱한 문자가 나옵니다.
- **두 시각의 기준이 다릅니다.** 한 PC 에서 `LeaseObtainedTime` 은 UTC, 네트워크 목록 `DateLastConnected` 는 한 PC 에서 현지 시각이었습니다.
- **T1·T2 는 기간이 아닙니다.** 한 PC 에서 `T1` 은 `LeaseObtainedTime` 에 임대 기간의 절반을 더한 시각이었습니다. (확인 범위: Win11 25H2 한 대)
- **값이 없는 인터페이스 키가 있습니다.** 한 PC 에서 12개 가운데 2개가 비어 있었습니다. (확인 범위: Win11 25H2 한 대)
- **IPv6 는 따로 있습니다.** `Tcpip6\Parameters\Interfaces` 는 이 페이지에서 다루지 않았습니다.
- **공식 설명은 Windows 2000 자료입니다.** 이후 버전은 관찰로 맞춰 본 것입니다.
- **앞선 값은 이전 시점에서 찾습니다.** [섀도 복사본 활용](/03-techniques/analysis/volume-shadow-copy-analysis.md) 과 하이브 로그로 이전 임대 값을 찾아봅니다. 하이브 로그는 [레지스트리 하이브 구조](/01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 문서에 적힌 구조로 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다.

**임대 값 (2024-01-01 00:00:00 UTC 에 24시간 임대를 받은 예시).**

```
LeaseObtainedTime    80 00 92 65   → 0x65920080 = 1704067200 → 2024-01-01 00:00:00 UTC
Lease                80 51 01 00   → 0x00015180 = 86400      → 24시간
T1                   40 A9 92 65   → 0x6592A940 = 1704110400 → 2024-01-01 12:00:00 UTC
T2                   D0 27 93 65   → 0x659327D0 = 1704142800 → 2024-01-01 21:00:00 UTC
LeaseTerminatesTime  00 52 93 65   → 0x65935200 = 1704153600 → 2024-01-02 00:00:00 UTC
```

1. REG_DWORD 4바이트를 리틀 엔디언으로 읽습니다.
2. `LeaseObtainedTime` 은 1970-01-01 0시부터 흐른 초입니다. 1704067200초는 2024-01-01 00:00:00 UTC 입니다.
3. `T1` 은 임대 기간의 1/2(43200초)을 더한 시각입니다.
4. `T2` 는 기본값대로라면 임대 기간의 7/8(75600초)을 더한 시각입니다. 한 PC 에서 계산을 맞춰 본 값은 `T1` 과 `LeaseTerminatesTime` 입니다. (확인 범위: Win11 25H2 한 대)
5. `LeaseTerminatesTime` 은 임대 기간을 모두 더한 시각입니다.

**SSID 하위 키 이름 (SSID `HOME` 으로 만든 예시).**

```
SSID 문자          H    O    M    E
SSID 16진          48   4F   4D   45     ← 네트워크 목록 Nla\Wireless 에 이 모양
두 자리 바꿈        84   F4   D4   54     ← 하위 키 이름·DhcpNetworkHint 는 이 모양
```

1. 하위 키 이름 `84F4D454` 를 두 자리씩 끊습니다.
2. 각 바이트의 두 자리를 바꿉니다. `84` → `48`, `F4` → `4F` 입니다.
3. `484F4D45` 를 문자로 바꾸면 `HOME` 입니다.

**DhcpGatewayHardware 14바이트 (만든 예시).**

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D
0x00    C0 A8 00 01 06 00 00 00 00 11 22 33 44 55
```

1. 앞 4바이트 `C0 A8 00 01` 은 게이트웨이 IPv4 주소입니다. 이 예시는 앞에서부터 한 바이트씩 읽어 192.168.0.1 이 되도록 만들었습니다. 실제 검체에서는 `DhcpDefaultGateway` 문자열과 맞춰 바이트 순서를 확인합니다.
2. 다음 4바이트 `06 00 00 00` 은 리틀 엔디언 정수 6 입니다.
3. 끝 6바이트 `00 11 22 33 44 55` 는 MAC 주소입니다. 네트워크 목록의 `DefaultGatewayMac` 과 맞춰 봅니다.

### 공개 도구로 한 번

1. SYSTEM·SOFTWARE 하이브와 하이브 로그를 함께 사본으로 뜹니다.
2. SOFTWARE 하이브의 `NetworkCards` 에서 인터페이스 GUID 와 어댑터 이름 목록을 만듭니다.
3. RegRipper 의 nic2 플러그인으로 SYSTEM 하이브의 인터페이스 목록을 뽑습니다. 이 플러그인은 임대 시각을 UTC 로 보여 줍니다.
4. 결과의 한 줄을 골라 위 풀이대로 `LeaseObtainedTime` 을 직접 한 번 바꿔 봅니다.
5. SSID 하위 키 이름을 두 자리씩 바꿔 네트워크 목록의 `Nla\Wireless` 와 맞춥니다.
6. 라이브 시스템이면 `ipconfig /all` 의 "Lease Obtained" 와 비교합니다. 이 명령은 현지 시각으로 보여 줍니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 네트워크 목록 | 게이트웨이 MAC, SSID 16진수, 마지막 연결 시각(현지) | [네트워크 목록](/02-artifacts/network/networklist.md) |
| Wi-Fi 프로필 | 같은 인터페이스 GUID 폴더의 무선 설정 | [Wi-Fi 프로필](/02-artifacts/network/wlan-profiles.md) |
| 네트워크 연결 이벤트 | 연결 시각 | [네트워크 연결 이벤트](/02-artifacts/event-logs/wlan-autoconfig-networkprofile.md) |
| SRUM | 네트워크 연결 기록 | [SRUM](/02-artifacts/execution/system-resource-usage-monitor/index.md) |
| 시간대 설정 | UTC 와 현지 시각을 맞출 기준 | [시간대 설정](/02-artifacts/system-account/time-zone.md) |

## 실습

공개 검체(NIST CFReDS 등)에서 SYSTEM·SOFTWARE 하이브를 꺼내 아래 질문을 풀어 봅니다.

1. 현재 컨트롤 세트는 몇 번입니까? 그 아래 `Interfaces` 하위 키는 몇 개입니까?
2. 각 인터페이스 GUID 는 `NetworkCards` 에서 어떤 어댑터입니까?
3. DHCP 로 받은 IP 주소와 DHCP 서버는 무엇입니까?
4. `LeaseObtainedTime` 을 직접 UTC 로 바꿔 봅니다. `T1` 은 임대 기간의 절반을 더한 값과 맞습니까?
5. SSID 하위 키 이름을 두 자리씩 바꾸면 어떤 SSID 가 나옵니까?
6. `DhcpGatewayHardware` 의 끝 6바이트는 네트워크 목록의 `DefaultGatewayMac` 과 같습니까?

## 참고 문헌

1. Microsoft Learn (보관 문서, Windows 2000 Server), *LeaseObtainedTime* (레지스트리 위치, 값 형식과 뜻, DHCP 클라이언트 서비스가 관리함, T1·T2 기본값). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc978465(v=technet.10)
2. H. Carvey (Yogesh Khatri 보완), *RegRipper3.0 plugin nic2.pl* (20200525) (오프라인 컨트롤 세트 경로, SSID 하위 키 순회, SSID 하위 키 이름·DhcpNetworkHint 의 니블 바꿈, 시각 값의 UTC 표시). https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/nic2.pl
