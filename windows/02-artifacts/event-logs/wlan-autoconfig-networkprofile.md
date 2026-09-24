# 네트워크 연결 이벤트 (WLAN-AutoConfig·NetworkProfile)

## 한 줄 요약

Wi-Fi 에 연결하거나 연결이 끊기면 `Microsoft-Windows-WLAN-AutoConfig/Operational` 로그에 기록이 남습니다. Windows 가 네트워크에 연결됐다고 판단하거나 연결이 끊겼다고 판단하면 `Microsoft-Windows-NetworkProfile/Operational` 로그에 기록이 남습니다. WLAN 쪽은 SSID·프로필 이름·인증 방식·암호화 방식을 알려 줍니다. NetworkProfile 쪽은 Windows 가 붙인 네트워크 이름과 프로필 GUID 를 알려 줍니다. 두 로그를 시각으로 맞추고, GUID 로 레지스트리의 네트워크 목록과 잇습니다.

이 페이지의 사실은 모두 Windows 11 25H2 PC 한 대의 공급자 매니페스트와 실제 기록에서 읽었습니다. 두 공급자를 설명한 공식 문서는 이번에 열어 보지 못했습니다. 그래서 거의 모든 내용에 "(확인 범위: Win11 25H2 한 대)" 가 붙습니다.

## 무엇을 기록하나 · 왜 생기나

| 로그 | 남는 때 | 알려 주는 것 |
|---|---|---|
| WLAN-AutoConfig/Operational | 무선 연결을 시작할 때, 성공하거나 실패할 때, 끊길 때. 결합 (association) 과 보안 단계마다 | 어댑터, 연결 방식, 프로필 이름, SSID, 인증·암호화 방식, 무선 규격, 끊긴 사유 코드 |
| NetworkProfile/Operational | 네트워크에 연결되거나 끊길 때, 네트워크 범주가 바뀔 때, 연결 상태가 바뀔 때 | Windows 가 붙인 네트워크 이름, 설명, 프로필 GUID, 상태 값, 범주 값 |

- NetworkProfile 의 메시지 문구 "Network Connected" 는 무선 전용이 아닙니다. 유선(이더넷)·모바일 연결에도 이 이벤트가 생기는지는 확인하지 못했습니다.
- Wi-Fi 프로필 파일에 남는 설정은 [Wi-Fi 프로필](/02-artifacts/network/wlan-profiles.md)에서 다룹니다.
- 레지스트리의 네트워크 프로필은 [네트워크 목록](/02-artifacts/network/networklist.md)에서 다룹니다.
- 이 페이지는 이벤트만 다룹니다.

## 위치와 버전별 차이

### 공급자와 로그

| 항목 | WLAN-AutoConfig | NetworkProfile |
|---|---|---|
| 공급자 (Provider) | Microsoft-Windows-WLAN-AutoConfig | Microsoft-Windows-NetworkProfile |
| 공급자 GUID | `{9580d7dd-0379-4658-9870-d5be7d52d6de}` | `{fbcfac3f-8459-419f-8e48-1f0b49cdb85e}` |
| 이 페이지에서 보는 로그 | `Microsoft-Windows-WLAN-AutoConfig/Operational` | `Microsoft-Windows-NetworkProfile/Operational` |
| 같은 공급자가 쓰는 다른 로그 | System, `Microsoft-Windows-WLAN-Autoconfig/Diagnostic`, `Microsoft-Windows-WLAN-AutoConfig/WiFiAwareDiagnostic` | `Microsoft-Windows-NetworkProfile/Diagnostic` |
| 파일 | `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-WLAN-AutoConfig%4Operational.evtx` | `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-NetworkProfile%4Operational.evtx` |
| 레코드의 Security UserID | 8001 기록에서 S-1-5-18 | 10000 기록에서 S-1-5-20 |

(확인 범위: Win11 25H2 한 대)

- 8001 실제 기록의 Task 는 24010, Opcode 는 190, Keywords 는 `0x8000000000000600` 이었습니다.
- S-1-5-18 은 SYSTEM, S-1-5-20 은 NETWORK SERVICE 입니다. 두 값 모두 연결한 사람의 계정이 아닙니다.

### 한 PC 의 설정과 기록량

한 PC 에서 읽은 결과는 다음과 같습니다. (확인 범위: Win11 25H2 한 대)

| 항목 | WLAN-AutoConfig/Operational | NetworkProfile/Operational |
|---|---|---|
| 켜짐 여부 | 켜짐 | 켜짐 |
| 최대 크기 · 보관 방식 | 1,052,672바이트 · 순환 (Circular) | 1,052,672바이트 · 순환 |
| 기록 수 | 1,395건 | 2,036건 |
| 남은 기간 | 2026-06-27 ~ 2026-09-23, 약 3개월 | 같음 |

- 두 로그가 기본으로 켜져 있는지는 확인하지 못했습니다. 한 PC 에서 켜져 있었을 뿐입니다.
- 로그 크기와 보관 방식을 확인하는 방법은 [감사 정책과 로그 설정](/02-artifacts/event-logs/audit-policy-log-settings.md)에서 다룹니다.

### 버전

- 이 페이지의 칸 구성은 빌드 26200 한 대에서 읽었습니다.
- 예전 Windows 버전에서 8001 의 칸 구성이 어떻게 달랐는지는 확인하지 못했습니다.
- 검체의 Windows 버전이 다르면 레코드의 칸을 직접 봅니다.

## 구조

### WLAN-AutoConfig/Operational — 연결 이벤트

아래 표는 한 PC 의 공급자 매니페스트에서 읽었습니다. (확인 범위: Win11 25H2 한 대)

| ID | 뜻 | 칸 |
|---|---|---|
| 8000 | 연결 시작 | InterfaceGuid, InterfaceDescription (어댑터), ConnectionMode, ProfileName, SSID, BSSType, ConnectionId |
| 8001 | 연결 성공 | 8000 의 칸 + PHYType, AuthenticationAlgorithm, CipherAlgorithm, OnexEnabled (802.1x), NonBroadcast (숨긴 네트워크) |
| 8002 | 연결 실패 (Error) | 8000 의 칸 + FailureReason (문장), ReasonCode, RSSI |
| 8003 | 연결 끊음 | 8000 의 칸 + Reason (문장), ReasonCode |
| 8011 | "Connect to last good network" | InterfaceGuid, InterfaceDescription, ProfileName, SSID, BSSType |

- 8001 의 메시지는 "WLAN AutoConfig service has successfully connected to a wireless network." 입니다.
- 8003 의 메시지는 "WLAN AutoConfig service has successfully disconnected from a wireless network." 입니다.

### WLAN-AutoConfig/Operational — 결합·보안 단계

| ID | 뜻 | 칸 |
|---|---|---|
| 11000 · 11001 · 11002 | 결합 시작 · 성공 · 실패 (11002 는 Error) | Adapter, DeviceGuid, LocalMac, SSID, BSSType 등. 11002 에는 Dot11StatusCode·RSSI 가 더 있습니다 |
| 11010 · 11005 · 11004 · 11006 | 보안 시작 · 성공 · 멈춤 · 실패 (11006 은 Error) | 11006 에는 PeerMac·ReasonCode·ErrorCode 가 있습니다 |
| 20019 | 호스트 네트워크 (hosted network) 에 클라이언트가 결합함 | InterfaceGuid, SSID, LocalMAC, PeerMAC |

Operational 채널에 정의된 ID 는 8000~8012, 11000~11010, 12011~12014, 13001·13002·13011~13014·13100~13103, 20019~20021, 60001~60004·60101~60103 입니다. (확인 범위: Win11 25H2 한 대)

### MAC 칸

- 이 빌드의 Operational 이벤트에는 BSSID 라는 칸이 없습니다.
- MAC 칸은 LocalMac 과 PeerMac 뿐입니다.
- LocalMac 은 11000번대와 12011~12014 에 있습니다.
- PeerMac 은 11006·11009·12013·20019·20020 에 있습니다.
- 8001 에는 접속한 AP 의 MAC (BSSID) 이 없습니다.
- PeerMac 이 AP 의 MAC 인지는 확인하지 못했습니다.

### NetworkProfile/Operational

| ID | 뜻 | 칸 |
|---|---|---|
| 10000 | Network Connected | Name, Description, Guid, Type, State, Category |
| 10001 | Network Disconnected | 10000 과 같음 |
| 10002 | Network Category Changed | 10000 과 같음 |
| 4001 | Entered State | |
| 4002 · 4003 | Transitioning to State | InterfaceGuid, CurrentOrNextState |
| 4004 | Network State Change Fired | 새 인터넷 연결 프로필, 비용, 도메인 연결 수준, 네트워크 연결 수준, 호스트 이름, WWAN, 테더링이 바뀌었는지. 모두 Boolean 입니다 |
| 20002 | NSI Set Category Result | Profile GUID, Interface GUID, Network Category, IPv4 Error Code, IPv6 Error Code, Context |

Operational 채널에 정의된 ID 는 4001~4004, 10000~10002, 20001, 20002 입니다. (확인 범위: Win11 25H2 한 대)

### 한 PC 의 실제 값 — WLAN

(확인 범위: Win11 25H2 한 대. 네트워크 이름과 계정은 옮기지 않았습니다)

| ID | 건수 |
|---|---|
| 11010 | 225 |
| 11004 | 222 |
| 11005 | 208 |
| 8000 | 140 |
| 11000 | 139 |
| 8001 | 131 |
| 11001 | 130 |
| 8003 | 102 |
| 8011 | 85 |
| 8002 | 9 |
| 8005 · 8006 · 8008 · 8012 | 각 1 |

ConnectionMode 는 코드가 아니라 문장으로 저장됐습니다. 한국어판에서는 한국어 문장이었습니다.

- "프로필에 자동 연결"
- "프로필과 수동 연결"
- "프로필 없이 보안 네트워크에 연결"

8003 의 Reason 도 한국어 문장으로 저장됐습니다. ReasonCode 는 숫자입니다. 아래 뜻 열은 저장된 문장을 줄여 옮겼습니다.

| ReasonCode | 뜻 | 건수 |
|---|---|---|
| 0 | 드라이버가 연결을 끊음 | 87 |
| 2 | 사용자가 끊음 | 1 |
| 3 | 새 연결을 설정하려고 끊음 | 5 |
| 5 | 자동 연결을 쓰지 않는 정책 때문에 끊음 | 7 |
| 11 | 작동 상태 변경 요청 | 1 |
| 13 | temporary-disconnect 요청 | 1 |

8001 에 나온 값은 다음과 같습니다.

| 칸 | 나온 값 |
|---|---|
| AuthenticationAlgorithm | WPA3-Personal, WPA2-Personal, Open |
| CipherAlgorithm | AES-CCMP, WEP (7건, 모두 Open 과 함께) |
| PHYType | 802.11a, 802.11g, 802.11n, 802.11ac, 802.11be |
| BSSType | 모두 Infrastructure |
| OnexEnabled | 모두 0 |
| NonBroadcast | 모두 false |

Open 인증에 CipherAlgorithm 이 WEP 로 적힌 까닭은 확인하지 못했습니다.

### 한 PC 의 실제 값 — NetworkProfile

(확인 범위: Win11 25H2 한 대)

| ID | 건수 |
|---|---|
| 4004 | 1,169 |
| 10000 | 354 |
| 4001 | 215 |
| 4002 | 126 |
| 10001 | 123 |
| 20002 | 36 |
| 4003 | 13 |

- 10000 의 Type 은 모두 0 이었습니다. State 는 1 이 248건, 9 가 103건, 41 이 3건이었습니다.
- 10001 의 Type 은 0, State 는 모두 2 였습니다.
- Category 는 모두 0 이었습니다.
- State·Type·Category 값의 뜻은 확인하지 못했습니다.

이벤트를 레지스트리 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Profiles` 와 맞춰 본 결과는 다음과 같습니다.

1. 10000·10001 의 Name 은 9종이었습니다.
2. 그 가운데 7종은 Profiles 아래 프로필의 ProfileName 과 같았습니다.
3. 그 7종은 이름마다 Guid 가 하나였고, 그 Guid 가 Profiles 아래 하위 키 이름과 같았습니다.
4. 나머지 2종은 "식별 중..." 과 "식별되지 않은 네트워크" 였습니다. Guid 가 각각 29개·10개였고, 어느 것도 Profiles 하위 키에 없었습니다.
5. 9종 가운데 7종은 Description 이 Name 과 같았습니다.
6. Profiles 아래 프로필 10개의 Category 값도 모두 0 이었습니다. 이름이 같은 7개는 이벤트의 Category 와 값이 같았습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 기록 시각에 이 어댑터가 이 SSID·프로필로 연결에 성공했다는 것 (8001) | 접속한 AP 가 어느 것인지. 8001 에 BSSID 가 없습니다 |
| 연결의 인증 방식·암호화 방식·무선 규격 (8001) | 그 시각에 어디에 있었는지 |
| 연결이 끊긴 시각과 사유 코드 (8003) | 그 컴퓨터를 쓰던 사람이 누구인지. 레코드의 계정은 사람의 계정이 아닙니다 |
| Windows 가 네트워크에 연결됐다고 판단한 시각, 네트워크 이름, 프로필 GUID (10000) | 연결 중에 무엇을 얼마나 주고받았는지 |
| | 같은 SSID 가 늘 같은 네트워크였다는 것. SSID 는 이름일 뿐입니다(해석) |
| | 로그에 남은 기간보다 오래된 연결 |

### 보고서 문장

- 쓸 수 있는 문장: "WLAN-AutoConfig/Operational 로그에 ○○(UTC) 의 8001 이 있습니다. SSID 는 ○○, 프로필 이름은 ○○, 인증 방식은 ○○ 입니다. 같은 ConnectionId 의 8003 은 ○○(UTC) 에 있고 ReasonCode 는 ○○ 입니다."
- 쓰면 안 되는 문장: "피의자는 ○○ 카페에서 ○○시부터 ○○시까지 인터넷을 썼다."

두 번째 문장은 기록에 없는 사람, 장소, 사용 행위를 적습니다. 이 로그가 말하는 것은 이 컴퓨터가 이 이름의 무선 네트워크에 연결됐다는 것까지입니다.

## 시각 해석

- 8000 은 연결을 시작한 때, 8001 은 연결에 성공한 때, 8003 은 연결이 끊긴 때입니다.
- 8000~8003 에는 모두 ConnectionId 칸이 있습니다. 같은 값끼리 묶으면 연결 하나의 시작부터 끝까지 볼 수 있을 것으로 보입니다. 이 방법은 칸 이름에서 나온 해석입니다.
- 10000 은 Windows 가 연결을 판단한 때, 10001 은 끊김을 판단한 때입니다. 8001 과 10000 을 시각으로 맞추면 SSID 와 Windows 의 네트워크 이름을 이을 수 있습니다.
- 한 PC 에서 레지스트리 네트워크 프로필의 마지막 연결 시각과 10000 의 시각을 맞춰 본 결과는 [네트워크 목록](/02-artifacts/network/networklist.md)의 시각 해석 절에 있습니다.
- 이 로그들의 기록 시각이 다른 EVTX 레코드처럼 UTC 로 저장된다는 점은 EVTX 형식의 일반 사실입니다. 이번에 이 두 로그에서 따로 확인하지는 않았습니다. 형식은 [이벤트 로그 형식](/01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.
- 두 로그 모두 1MB 남짓의 순환 로그라서, 한 PC 에서는 약 3개월치만 남아 있었습니다. (확인 범위: Win11 25H2 한 대) 더 오래된 연결은 레지스트리의 네트워크 목록·Wi-Fi 프로필이나 [SRUM](/02-artifacts/execution/system-resource-usage-monitor/index.md)에서 찾습니다. 이 판단은 해석입니다.
- 여러 기록의 시각을 한 기준으로 맞추는 방법은 [시간대·시계 오차 보정](/03-techniques/analysis/timeline/time-normalization.md)에서 다룹니다.

## 함정과 한계

1. **문장 값으로 검색합니다.** ConnectionMode·Reason·FailureReason 은 OS 언어를 따르는 문장입니다. 여러 언어의 검체를 문자열로 찾으면 빠질 수 있습니다. 숫자 칸인 ReasonCode 로 찾는 편이 안전합니다. 이 판단은 해석입니다.
2. **8001 에서 AP 를 찾습니다.** 8001 에는 BSSID 가 없습니다. PeerMac 이 AP 의 MAC 인지도 확인하지 못했습니다.
3. **"식별 중..." 을 네트워크 하나로 묶습니다.** 한 PC 에서 이 이름에는 Guid 가 29개 있었습니다. "식별되지 않은 네트워크" 에는 10개가 있었습니다. 둘 다 레지스트리 프로필과 이어지지 않았습니다.
4. **Category·State·Type 숫자를 뜻으로 바꿔 적습니다.** 이번에는 세 값의 뜻을 확인하지 못했습니다. 레지스트리 Category 의 뜻과 한계는 [네트워크 목록](/02-artifacts/network/networklist.md)에서 다룹니다.
5. **WEP 가 적혔으니 WEP 로 연결했다고 봅니다.** 한 PC 에서 CipherAlgorithm WEP 는 모두 인증 방식 Open 과 함께 나왔습니다. 까닭은 확인하지 못했습니다.
6. **로그가 없으면 연결이 없었다고 봅니다.** 두 로그가 기본으로 켜져 있는지 확인하지 못했습니다. 로그 설정과 남은 기간부터 봅니다.
7. **레코드의 계정을 사용자로 읽습니다.** 8001 은 S-1-5-18, 10000 은 S-1-5-20 으로 기록됐습니다. 사용자는 로그온 기록에서 따로 찾습니다.
8. **분석 PC 의 매니페스트를 검체에 그대로 씁니다.** 이 페이지의 칸 구성은 빌드 26200 한 대의 것입니다.

### 지우기와 조작

- **로그를 지웁니다.** 보안 로그가 아닌 로그를 지우면 System 로그에 104 가 남는 구조입니다. [이벤트 로그 삭제 (1102·104)](/02-artifacts/event-logs/1102-104.md)를 봅니다.
- **Wi-Fi 프로필을 지웁니다.** 프로필 파일을 지워도 이미 남은 이벤트는 따로 지워지지 않습니다. 이벤트의 ProfileName·SSID 로 지금은 없는 프로필을 찾을 수 있습니다. 이 판단은 두 기록이 다른 곳에 저장된다는 점에서 나온 해석입니다.
- **레코드 일부만 남아 있습니다.** 덮어쓴 레코드가 파일 안에 남아 있을 수 있습니다. [파일 안에 남은 지운·손상 레코드](/01-foundations/database-log-formats/evtx-evt-etl/chunk-slack-corrupted-evtx.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

이벤트 칸의 값은 이진 XML 의 치환 값으로 들어 있습니다. 값 종류 번호와 배열 구조는 [이진 XML 해석](/01-foundations/database-log-formats/evtx-evt-etl/binary-xml-template.md)에서 다룹니다.

아래 바이트는 명세로 만든 예시입니다. 검체에서 나온 값이 아닙니다. Reason 칸이 UTF-16 문자열로 들어 있다고 보고 만들었습니다. 이 칸의 값 종류는 이번에 확인하지 않았습니다.

**8003 Reason 문장의 첫 네 글자 "드라이버"**

```
DC B4 7C B7 74 C7 84 BC
드    라    이    버
```

1. 한 글자가 2바이트입니다. 리틀 엔디언이므로 `DC B4` 는 U+B4DC, 곧 "드" 입니다.
2. 영문판이라면 같은 자리에 영어 문장이 들어가므로 바이트가 전혀 다릅니다.
3. 그래서 "드라이버" 로 바이트 검색을 하면 한국어판 검체의 레코드만 걸립니다.
4. ReasonCode 는 숫자 칸이라 언어와 관계없이 같은 값으로 남습니다. 여러 언어의 검체는 ReasonCode 로 찾습니다.

문자 인코딩은 [문자 인코딩](/01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.

> 그림 자리: 같은 ReasonCode 0 이 한국어판과 영문판에서 서로 다른 Reason 문장 바이트로 저장되는 모습을 나란히 놓은 그림

### 공개 도구로 한 번

Windows 에 들어 있는 이벤트 뷰어와 PowerShell 의 `Get-WinEvent` 로 볼 수 있습니다. 분석 PC 로 옮긴 파일은 `Path` 로 엽니다. 아래 `E:\case\` 는 예시 경로입니다.

```powershell
$wlan = 'E:\case\Microsoft-Windows-WLAN-AutoConfig%4Operational.evtx'
$np   = 'E:\case\Microsoft-Windows-NetworkProfile%4Operational.evtx'

# ID 별 건수
Get-WinEvent -Path $wlan | Group-Object Id | Sort-Object Count -Descending

# 연결 성공·끊음의 주요 칸
Get-WinEvent -FilterHashtable @{ Path = $wlan; Id = 8001, 8003 } | ForEach-Object {
  $d = @{}; ([xml]$_.ToXml()).Event.EventData.Data | ForEach-Object { $d[$_.Name] = $_.'#text' }
  [pscustomobject]@{ Time = $_.TimeCreated; Id = $_.Id; SSID = $d.SSID; Profile = $d.ProfileName
                     Auth = $d.AuthenticationAlgorithm; ReasonCode = $d.ReasonCode; ConnId = $d.ConnectionId }
}

# 연결됨·끊김의 이름과 GUID
Get-WinEvent -FilterHashtable @{ Path = $np; Id = 10000, 10001 } | ForEach-Object {
  $d = @{}; ([xml]$_.ToXml()).Event.EventData.Data | ForEach-Object { $d[$_.Name] = $_.'#text' }
  [pscustomobject]@{ Time = $_.TimeCreated; Id = $_.Id; Name = $d.Name; Guid = $d.Guid; State = $d.State; Category = $d.Category }
}
```

이벤트의 Guid 는 NetworkList `Profiles` 아래 하위 키 이름과 맞춥니다. 대소문자와 중괄호 표기를 맞춘 뒤 비교합니다. 라이브 시스템의 로그 설정은 `Get-WinEvent -ListLog Microsoft-Windows-WLAN-AutoConfig/Operational, Microsoft-Windows-NetworkProfile/Operational` 로 봅니다. 칸 구성은 `(Get-WinEvent -ListProvider Microsoft-Windows-WLAN-AutoConfig).Events` 로 확인합니다. 이 명령은 분석 PC 의 매니페스트를 읽습니다.

도구가 한국어 문장 칸을 깨뜨리지 않고 보여 주는지 확인합니다. 레코드 한두 개는 XML 원문과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [네트워크 목록](/02-artifacts/network/networklist.md) | 10000 의 Guid 와 Profiles 하위 키, 프로필의 처음·마지막 연결 시각 |
| [Wi-Fi 프로필](/02-artifacts/network/wlan-profiles.md) | 8001 의 ProfileName·SSID 와 저장된 프로필, 지금은 없는 프로필 |
| [네트워크 연결 기록 (Network Connectivity)](/02-artifacts/execution/system-resource-usage-monitor/network-connectivity.md) | 이벤트가 밀려난 기간의 연결 기록 |
| [네트워크 사용량 (Network Data Usage)](/02-artifacts/execution/system-resource-usage-monitor/network-data-usage.md) | 연결된 동안 앱이 주고받은 양 |
| [네트워크 인터페이스 설정](/02-artifacts/network/tcp-ip-interfaces.md) | InterfaceGuid 로 어댑터 설정 찾기. 이 연결 방법은 해석입니다 |
| [로그온·로그오프](/02-artifacts/event-logs/logon-events/index.md) | 연결 시각에 로그온해 있던 사용자 |

## 실습

**무선 어댑터가 있는 시험용 노트북**에서 해 봅니다. 가상 머신에는 무선 어댑터가 없을 때가 많습니다. 각 단계의 시각을 적어 둡니다.

1. `Get-WinEvent -ListLog` 로 두 로그가 켜져 있는지, 크기와 보관 방식이 어떤지 봅니다.
2. 저장된 Wi-Fi 에 연결합니다. 8000·8001·10000 이 어떤 순서로 남는지 봅니다. 세 레코드의 ConnectionId 와 Guid 를 적습니다.
3. 작업 표시줄에서 직접 연결을 끊습니다. 8003 의 ReasonCode 가 무엇인지 봅니다.
4. 처음 가는 네트워크에 연결합니다. 10000 의 Name 이 "식별 중..." 에서 실제 이름으로 바뀌는지, 새 Guid 가 NetworkList 에 생기는지 봅니다.
5. 네트워크 범주를 바꿉니다. 10002 와 레지스트리 Category 값이 어떻게 바뀌는지 봅니다. 이 페이지가 확인하지 못한 값의 뜻을 여기서 확인할 수 있습니다.
6. `netsh wlan show interfaces` 의 BSSID 를 적고, PeerMac 칸이 있는 레코드(11006·11009 등)의 값과 비교합니다.
7. 유선 랜을 꽂았을 때도 10000 이 남는지 봅니다.

**NIST CFReDS 같은 공개 검체**에서는 다음을 풀어 봅니다.

1. 두 로그가 있습니까? 가장 오래된 기록은 언제입니까?
2. 8001 의 SSID 목록과 Wi-Fi 프로필 목록을 비교합니다. 이벤트에만 있는 SSID 가 있습니까?
3. 10000 의 Guid 가운데 NetworkList 에 없는 것은 무엇입니까? 그 Name 은 무엇입니까?

## 참고 문헌

이 페이지의 사실은 공개 문서가 아니라 Windows 11 25H2 (빌드 26200.9457) PC 한 대에서 직접 읽은 것입니다. 공급자 매니페스트는 `Get-WinEvent -ListProvider` 로, 로그 설정은 `Get-WinEvent -ListLog` 로, 실제 기록은 Operational 로그 두 개에서 읽었습니다. WLAN-AutoConfig·NetworkProfile 이벤트를 설명한 공식 문서는 이번에 열어 보지 못했습니다.
