---
title: "네트워크 목록"
parent: "아티팩트 · 네트워크"
nav_order: 2330
---

# 네트워크 목록 (NetworkList)

## 한 줄 요약

SOFTWARE 하이브의 `NetworkList` 키에는 네트워크마다 이름·종류·처음 만든 시각·마지막 연결 시각이 남습니다. 서명 (Signatures) 하위 키에는 기본 게이트웨이의 MAC 주소가 남습니다.

## 무엇을 기록하나 · 왜 생기나

네트워크 하나는 `Profiles` 아래 GUID 하위 키 하나이고, 프로필 키에는 네트워크 이름, 네트워크 종류, 범주 (Category), 처음 만든 시각, 마지막 연결 시각이 들어 있습니다. `Signatures` 아래 하위 키는 `ProfileGuid` 값으로 프로필과 이어 보며, 여기에 기본 게이트웨이 MAC 주소가 남을 수 있지만 비어 있는 서명도 있습니다.

분석에서 보는 하위 키는 `Profiles`, `Signatures\Managed`, `Signatures\Unmanaged`, `Nla\Cache\Intranet`, `Nla\Wireless` 입니다[2]. 이 키들은 HKLM 에 있으므로 PC 전체에 하나이며 사용자별로 나뉘지 않습니다.

## 위치와 버전별 차이

```
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList
```

- 오프라인 이미지에서는 SOFTWARE 하이브에서 읽습니다. 하이브 파일 위치와 수집 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.
- 네트워크 범주를 나타내는 NLM_NETWORK_CATEGORY 열거는 Windows Vista·Server 2008 이후에 있습니다.
- 윈도 버전마다 하위 키나 값이 다를 수 있어 실제 데이터로 확인합니다.

Windows 11 PC 한 대에서 본 하위 키는 아래와 같습니다.

| 하위 키 | 이 PC 에서 본 것 |
|---|---|
| `Profiles` | 네트워크 프로필 10개 |
| `Signatures\Managed`, `Signatures\Unmanaged` | 서명 키 3개, 7개 |
| `Nla\Wireless` | 하위 키 4개 |
| `Nla\IntranetEnabled` | 이름이 64자인 하위 키 3개. 값은 없었습니다 |
| `Nla\Cache` | 없었습니다 |
| `DefaultMediaCost`, `NewNetworks`, `Permissions`, `Policies`, `FirewallSync` | 있었습니다. 내용은 이 페이지에서 다루지 않습니다 |

## 구조

### Profiles\{GUID}

Windows 11 PC 한 대에서 본 값은 아래와 같습니다.

| 값 | 형식 | 내용 |
|---|---|---|
| `ProfileName` | REG_SZ | 네트워크 이름 |
| `Description` | REG_SZ | 설명. 대부분 `ProfileName` 과 같았습니다 |
| `Managed` | REG_DWORD | 아래 "Managed" 절 |
| `Category` | REG_DWORD | 아래 "Category" 절 |
| `DateCreated` | REG_BINARY 16바이트 | 처음 만든 시각 |
| `NameType` | REG_DWORD | 네트워크 종류 |
| `DateLastConnected` | REG_BINARY 16바이트 | 마지막 연결 시각 |

- 프로필 10개 모두 `DateCreated`·`DateLastConnected` 가 16바이트였습니다.
- `ProfileName` 과 `Description` 은 10개 가운데 8개가 같았습니다. 나머지 2개는 `ProfileName` 뒤에 " 2" 가 더 붙어 있었습니다.

### NameType

| 16진 | 10진 | 종류 | 근거 |
|---|---|---|---|
| `0x47` | 71 | 무선 | [2] |
| `0x06` | 6 | 유선 | [2] |
| `0x17` | 23 | 광대역 (3G) | [2] |
| `0x01` | 1 | 공개 자료 없음 | Windows 11 PC 한 대에서 이 프로필 이름은 "로컬 영역 연결" 이었습니다 |

- Windows 11 PC 한 대에서는 71 이 6개, 6 이 3개, 1 이 1개였습니다.
- 레지스트리 도구는 REG_DWORD 를 10진으로 보여 주기도 합니다. 그러면 무선은 `0x47` 이 아니라 71 로 보입니다.
- 위 표에 없는 값은 뜻을 밝힌 공개 자료가 없습니다.

### Category

NLM_NETWORK_CATEGORY 열거의 값은 아래와 같습니다.

| 값 | 이름 | 뜻 |
|---|---|---|
| 0 | 공용 (public) | 신뢰하지 않는 네트워크 |
| 1 | 개인 (private) | 신뢰하는 네트워크 |
| 2 | 도메인 인증 | 액티브 디렉터리 도메인에 인증된 네트워크 |

- 레지스트리 `Category` 값이 이 열거와 같은 번호라고 밝힌 공개 문서는 없습니다. 다른 기록과 맞춰 봅니다.
- Windows 11 PC 한 대에서는 10개 모두 `Category` 가 0 이었습니다. 같은 PC 의 지금 연결도 `Get-NetConnectionProfile` 에서 Public 으로 나왔습니다.
- 범주만 보고 방화벽 포트가 열렸다고 가정하지 않습니다. 사용자가 범주의 기본 설정을 바꿀 수 있기 때문입니다[1].

### Managed

Windows 11 PC 한 대에서 `Managed`=1 인 프로필은 3개였고 `Signatures\Managed` 아래 키도 3개였습니다. 그 3개는 모두 유선(NameType 6)이었으며 이름이 DNS 접미사 모양이었습니다.

### DateCreated · DateLastConnected

16바이트를 2바이트 부호 없는 정수 8개로 읽습니다. 이 모양을 SYSTEMTIME 이라고 부릅니다.

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 2 | 연 |
| 2 | 2 | 월 |
| 4 | 2 | 요일 |
| 6 | 2 | 일 |
| 8 | 2 | 시 |
| 10 | 2 | 분 |
| 12 | 2 | 초 |
| 14 | 2 | 밀리초 |

시각 기준(UTC·현지)은 아래 "시각 해석" 절에서 다룹니다.

### Signatures\Managed · Unmanaged

- 하위 키 이름은 Windows 11 PC 한 대에서 모두 96자 16진 문자열이었습니다.
- `DefaultGatewayMac` 의 앞 6바이트가 MAC 주소입니다[2].

같은 PC 에서 본 값은 아래와 같습니다.

| 값 | 형식 | 이 PC 에서 본 것 |
|---|---|---|
| `ProfileGuid` | — | 10개 모두 `Profiles` 의 하위 키 이름과 같았습니다 |
| `Description` | — | 10개 가운데 8개가 해당 프로필의 `Description` 과 같았습니다 |
| `Source` | REG_DWORD | 8·160·512·1032 가 나왔습니다 |
| `DnsSuffix` | — | 이 페이지에서 다루지 않습니다 |
| `FirstNetwork` | — | 10개 모두 해당 프로필의 `ProfileName` 과 같았습니다 |
| `DefaultGatewayMac` | REG_BINARY | Unmanaged 7개 가운데 6개는 6바이트, 1개는 0바이트였습니다. Managed 3개는 모두 0바이트였습니다 |

- `DefaultGatewayMac` 6바이트 값은 [네트워크 인터페이스 설정](tcp-ip-interfaces.md) 의 게이트웨이 MAC 과 같았습니다(4/4).

### Nla\Wireless

Windows 11 PC 한 대에서 본 모습은 아래와 같습니다.

하위 키는 4개였고, 각 하위 키의 기본값(REG_SZ)은 SSID 바이트를 16진수로 쓴 문자열이었습니다. 각 하위 키에는 4바이트 REG_BINARY 값들이 있었는데 값 이름은 SSID 의 16진수이거나 SSID 그대로였습니다.

이 16진 SSID 는 TCP/IP 인터페이스 키의 무선 하위 키 이름과 이어집니다. 잇는 방법은 [네트워크 인터페이스 설정](tcp-ip-interfaces.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- 이 PC 에 이 이름의 네트워크 프로필이 있습니다.
- 그 프로필을 처음 만든 시각과 마지막으로 연결한 시각을 기록으로 확인되는 만큼 쓸 수 있습니다.
- NameType 으로 무선·유선·광대역을 나눌 수 있습니다.
- Unmanaged 서명에 `DefaultGatewayMac` 이 있으면 그 네트워크의 기본 게이트웨이 MAC 을 알 수 있습니다.

### 증명하지 못하는 것

- **누가 연결했는지.** HKLM 기록이라 사용자를 적는 값이 없습니다. 사람을 좁히는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- **몇 번, 얼마 동안 연결했는지.** 처음과 마지막 두 시각만 있습니다. 그 사이의 연결은 [네트워크 연결 이벤트](../event-logs/wlan-autoconfig-networkprofile.md) 와 [SRUM](../execution/system-resource-usage-monitor/index.md) 에서 봅니다.
- **당시 방화벽 상태.** `Category` 값만으로 포트가 열렸는지 판단하지 않습니다.
- **장소.** 게이트웨이 MAC 만으로 장소를 정하지 않습니다. 이 값은 다른 자료와 맞춰 볼 수 있는 값으로만 씁니다.

보고서에는 "이 PC 의 NetworkList 에 이 이름의 무선 네트워크 프로필이 있고, 처음 만든 시각과 마지막 연결 시각이 이렇게 기록돼 있다(현지 시각)" 처럼 씁니다.

## 시각 해석

RegRipper networklist 플러그인은 SYSTEMTIME 을 시간대 변환 없이 그대로 출력합니다[2]. Windows 11 PC 한 대에서 두 값은 현지 시각으로 적혀 있었고, 근거는 아래와 같습니다.

| DateLastConnected | 맞춰 본 기록 |
|---|---|
| 2026-09-23 12:48:44 | NetworkProfile/Operational 10000 이벤트의 현지 시각과 초까지 같았습니다. 그 이벤트의 UTC 는 03:48:44 였습니다 |
| 2026-09-21 06:44:43 | 10000 이벤트의 현지 시각과 같았습니다. 부팅 시각(현지 06:44:15) 28초 뒤였습니다 |

- 보고서에서 UTC 로 바꿀 때는 그 시점의 시간대 설정을 밝힙니다. 시간대 설정은 [시간대 설정](../system-account/time-zone.md) 에서 확인합니다.
- 같은 순간이 TCP/IP 인터페이스 키에는 UTC 로 적혀 있었습니다. [네트워크 인터페이스 설정](tcp-ip-interfaces.md) 에서 다룹니다.
- `DateLastConnected` 는 한 PC 에서 연결 이벤트(10000) 시각과 같았습니다. 끊을 때 바뀌는지는 실제 데이터의 연결·끊김 이벤트와 맞춰 확인합니다.
- `DateCreated` 는 OS 설치 시각보다 앞설 수 있습니다. Windows 11 PC 한 대는 InstallDate 가 2026-06-27 03:07 인데 `DateCreated` 가 2025-04-21 인 프로필이 3개 남아 있었습니다. 업그레이드 뒤에도 이전 프로필이 이어진 것으로 보입니다.
- 같은 PC 에는 InstallDate 1분 뒤(2026-06-27 03:08:24)가 `DateCreated` 인 무선 프로필도 있었습니다.
- Wi-Fi 프로필 파일의 생성 시각과 `DateCreated` 를 맞춰 본 결과는 [Wi-Fi 프로필](wlan-profiles.md) 에서 다룹니다.
- 키의 마지막 기록 시각 (LastWrite) 은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다. 시각 값 형식 전체는 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.

## 함정과 한계

- **10진과 16진을 섞어 읽지 않습니다.** 도구가 71 로 보여 준 NameType 은 `0x47`, 곧 무선입니다. 23 은 `0x17` 입니다.
- **현지 시각일 수 있습니다.** 한 PC 에서는 두 시각이 현지 시각으로 적혀 있었습니다. 다른 UTC 기록과 나란히 놓기 전에 시간대를 맞춥니다.
- **이름에 번호가 붙을 수 있습니다.** `ProfileName` 뒤에 " 2" 가 붙은 프로필이 있었습니다. 이름으로 다른 자료와 맞출 때 `Description`·`FirstNetwork` 도 함께 봅니다.
- **Wi-Fi 프로필 파일과 GUID 가 다릅니다.** 두 자료는 이름으로 맞춰야 합니다. 자세한 것은 [Wi-Fi 프로필](wlan-profiles.md) 에 있습니다.
- **도구가 읽는 키가 없을 수 있습니다.** RegRipper 는 `Nla\Cache\Intranet` 을 읽지만, Windows 11 PC 한 대에는 `Nla\Cache` 가 없었습니다. 결과가 비어도 도구 오류로 단정하지 않습니다.
- **`DefaultGatewayMac` 이 비어 있을 수 있습니다.** 0바이트인 서명이 있었습니다.
- **지운 네트워크.** 설정 앱의 "알려진 네트워크 삭제" 등으로 프로필을 지울 때 이 키도 지워지는지는 실제 데이터로 확인해야 합니다. 지운 키와 값을 찾는 방법, 하이브 로그 반영은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다. 이전 시점은 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 SYSTEMTIME 구조로 만든 예시입니다. 특정 기기에서 꺼낸 값이 아닙니다.

**DateLastConnected 16바이트 (2024-03-15 09:30:05.250 으로 만든 예시).**

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    E8 07 03 00 05 00 0F 00 09 00 1E 00 05 00 FA 00
```

1. 2바이트씩 끊어 리틀 엔디언으로 읽습니다.
2. `E8 07` 은 `0x07E8`, 곧 2024 입니다. 연입니다.
3. `03 00` 은 3월입니다.
4. `05 00` 은 요일 필드의 값 5 입니다. 날짜는 연·월·일 필드로 읽습니다.
5. `0F 00` 은 15일, `09 00` 은 9시, `1E 00` 은 30분, `05 00` 은 5초입니다.
6. `FA 00` 은 250밀리초입니다.
7. 이 값에는 시간대 정보가 없습니다. 현지 시각인지 UTC 인지는 "시각 해석" 절처럼 다른 기록과 맞춰 정합니다.

**NameType (REG_DWORD, 만든 예시).**

```
47 00 00 00
```

리틀 엔디언으로 읽으면 `0x47`, 10진 71 입니다. 무선입니다.

**DefaultGatewayMac (REG_BINARY 6바이트, 만든 예시).**

```
00 11 22 33 44 55
```

앞 6바이트를 순서대로 MAC 주소 `00:11:22:33:44:55` 로 읽습니다.

### 공개 도구로 한 번

1. SOFTWARE 하이브와 하이브 로그를 함께 사본으로 뜹니다.
2. 레지스트리 뷰어로 `Microsoft\Windows NT\CurrentVersion\NetworkList` 를 엽니다.
3. RegRipper 의 networklist 플러그인으로 프로필 목록을 뽑습니다. 이 플러그인은 시각을 시간대 변환 없이 출력합니다.
4. 결과의 한 줄을 골라 위 풀이대로 `DateLastConnected` 를 직접 한 번 읽어 봅니다.
5. `Signatures` 의 `ProfileGuid` 로 서명과 프로필을 잇고, `DefaultGatewayMac` 을 적습니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| Wi-Fi 프로필 | 같은 SSID 의 무선 설정과 인증 방식 | [Wi-Fi 프로필](wlan-profiles.md) |
| 네트워크 인터페이스 설정 | 게이트웨이 IP·MAC, SSID 별 DHCP 임대 시각(UTC) | [네트워크 인터페이스 설정](tcp-ip-interfaces.md) |
| 네트워크 연결 이벤트 | 연결 시각과 시간대 확인 | [네트워크 연결 이벤트](../event-logs/wlan-autoconfig-networkprofile.md) |
| SRUM | 네트워크 연결 기록 | [SRUM](../execution/system-resource-usage-monitor/index.md) |
| 시간대 설정 | 현지 시각을 UTC 로 바꿀 기준 | [시간대 설정](../system-account/time-zone.md) |
| 시스템 기본 정보 | 설치 시각과 `DateCreated` 비교 | [시스템 기본 정보](../system-account/os-version-computer-name-install-date-shutdown-t.md) |

## 실습

공개 시험 이미지(NIST CFReDS 등)에서 SOFTWARE 하이브를 꺼내 아래 질문을 풀어 봅니다.

1. `Profiles` 아래 프로필은 몇 개입니까? NameType 별로 몇 개씩입니까?
2. 도구가 NameType 을 10진으로 보여 줍니까, 16진으로 보여 줍니까?
3. `DateLastConnected` 가 가장 늦은 프로필은 무엇입니까? 16바이트를 직접 풀어 봅니다.
4. 그 시각은 현지 시각입니까? 같은 시각의 연결 이벤트와 시간대 설정으로 확인해 봅니다.
5. `DateCreated` 가 OS 설치 시각보다 앞선 프로필이 있습니까?
6. Unmanaged 서명의 `DefaultGatewayMac` 은 SYSTEM 하이브의 게이트웨이 MAC 과 같습니까?

## 참고 문헌

1. Microsoft Learn, *NLM_NETWORK_CATEGORY enumeration (netlistmgr.h)* (범주 값 0·1·2 의 뜻, 지원 버전, 범주로 방화벽 포트를 가정하지 말라는 주의). https://learn.microsoft.com/en-us/windows/win32/api/netlistmgr/ne-netlistmgr-nlm_network_category
2. H. Carvey, *RegRipper3.0 plugin networklist.pl* (20200518) (읽는 하위 키, NameType 값, SYSTEMTIME 풀이와 시간대 미변환 출력, DefaultGatewayMac 읽기). https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/networklist.pl
