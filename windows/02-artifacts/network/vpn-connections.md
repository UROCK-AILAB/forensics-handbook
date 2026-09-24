# VPN 연결 기록 (VPN Connections)

> 이 페이지에서 "(확인 범위: 조사 PC)" 는 Windows 11 Home 25H2(빌드 26200.9457) PC 한 대에서 직접 본 사실을 뜻합니다. "(확인 범위: 조사 PC 시험)" 은 같은 PC 에서 시험용 VPN 프로필을 일부러 만들었다가 지우며 본 사실입니다. 다른 버전이나 다른 PC 에서는 따로 확인해야 합니다.

## 한 줄 요약

윈도 내장 VPN 의 흔적은 세 곳에 남습니다. 연결 프로필은 전화번호부 파일 (phonebook) `rasphone.pbk` 에, 접속 시도와 결과는 Application 로그의 RasClient 이벤트에, 프로필을 만들고 지운 기록은 `Microsoft-Windows-VPN-Client/Operational` 로그에 남습니다. 프로필을 지우면 파일에서는 사라지지만 삭제 이벤트는 남습니다.

## 무엇을 기록하나 · 왜 생기나

PowerShell(`Add-VpnConnection`)로 VPN 프로필을 만들자 전화번호부 파일에 절이 하나 생겼습니다. 이 프로필로 `rasdial` 접속을 시도하자 Application 로그에 RasClient 이벤트가 남았습니다. (확인 범위: 조사 PC 시험) 설정 앱으로 만든 프로필은 이번에 보지 못했습니다.

| 기록 | 생기는 때 | 알려 주는 것 |
|---|---|---|
| `rasphone.pbk` | 프로필을 만들 때 | 연결 이름, 서버 주소, 장치, 만든 시각으로 보이는 값 |
| Application 로그, 원본 RasClient (20220~20227) | 접속할 때 | 어떤 프로필로 어느 서버에 접속했는지, 성공·실패·끊김, 오류 코드 |
| `Microsoft-Windows-VPN-Client/Operational` (10001~10008) | 프로필을 만들거나 고치거나 지울 때 | 프로필 속성, 삭제한 프로필 이름 |
| 추적 로그 (tracing) | 추적을 켰을 때만 | 기본값이 꺼져 있어 보통 비어 있습니다 |

이 기록으로 아래 질문에 답합니다.

- 이 PC 에 어떤 VPN 프로필이 있었나
- 언제 어느 서버로 접속을 시도했고, 성공했나
- 지금은 없는 프로필이 예전에 있었나

이 페이지는 윈도 내장 VPN 클라이언트만 다룹니다. OpenVPN·WireGuard·FortiClient·Cisco 같은 서드파티 VPN 프로그램의 설정과 로그 위치는 이번에 확인하지 않았습니다.

## 위치와 버전별 차이

아래 위치는 모두 조사 PC 에서 확인했습니다. 다른 Windows 버전의 위치는 확인하지 않았습니다.

| 기록 | 위치 | 메모 |
|---|---|---|
| 사용자별 프로필 | `%APPDATA%\Microsoft\Network\Connections\Pbk\rasphone.pbk` | (확인 범위: 조사 PC 시험) |
| 모든 사용자용 프로필 | `%ProgramData%\Microsoft\Network\Connections\Pbk\rasphone.pbk` | `-AllUserConnection` 으로 만든 프로필입니다. 이때는 사용자별 파일이 생기지 않았습니다 (확인 범위: 조사 PC 시험) |
| 숨은 폴더 | 사용자별 `Pbk` 폴더 안의 `_hiddenPbk` | 쓰임새는 확인하지 않았습니다. 폴더째 수집합니다 (확인 범위: 조사 PC) |
| 접속 이벤트 | Application 로그, 원본 RasClient | 메시지 파일은 `C:\Windows\System32\mprmsg.dll` 입니다 (확인 범위: 조사 PC) |
| 프로필 이벤트 | `Microsoft-Windows-VPN-Client/Operational` | 기본으로 켜져 있고 최대 크기는 1MB 입니다 (확인 범위: 조사 PC) |
| 그 밖의 채널 | `Microsoft-Windows-VPN/Operational`(켜짐), `Microsoft-Windows-RasAgileVpn/Operational`(꺼짐), `Windows Networking Vpn Plugin Platform/Operational`(꺼짐) | 내용은 확인하지 않았습니다 (확인 범위: 조사 PC) |
| 추적 설정 | `HKLM\SOFTWARE\Microsoft\Tracing\RASMAN` | `EnableFileTracing=0`, `FileDirectory=C:\WINDOWS\tracing`, `MaxFileSize=1048576` (확인 범위: 조사 PC) |

`Tracing` 키 아래에는 RASMAN·RASAPI32·RasIpsec 같은 구성 요소별 키가 있고, "프로그램 이름_RASAPI32" 꼴의 키도 많습니다. 추적이 꺼져 있으면 `C:\WINDOWS\tracing` 에 로그가 쌓이지 않는데, 조사 PC 에서도 이 폴더는 비어 있었습니다. (확인 범위: 조사 PC)

## 구조

### 전화번호부 파일 (rasphone.pbk)

파일은 INI 형식이고, 프로필마다 `[연결 이름]` 절이 있으며 그 아래에 "이름=값" 줄이 이어집니다. (확인 범위: 조사 PC 시험)

아래는 시험 프로필(`ZZTestVPN`)에서 메모한 줄만 골라 모은 것입니다. 실제 파일의 줄 순서·개수와 다릅니다.

```
[ZZTestVPN]
Type=2
PhoneNumber=vpn.invalid
Device=WAN Miniport (IKEv2)
DEVICE=vpn
MEDIA=rastapi
Port=VPN2-0
VpnStrategy=0
Guid=<32자리 16진수>
PreSharedKey=
IpDnsSuffix=
NumRoutes=0
PowershellCreatedProfile=1
LowDateTime=1806595920
HighDateTime=31279980
```

| 칸 | 시험 값 | 읽는 법 |
|---|---|---|
| `[절 이름]` | `ZZTestVPN` | 연결 이름입니다 |
| `PhoneNumber` | `vpn.invalid` | 서버 주소가 이 칸에 들어갑니다 |
| `Device` | `WAN Miniport (IKEv2)` | 장치 이름입니다. 시험 프로필은 터널 종류를 Automatic 으로 만들었습니다 |
| `DEVICE`·`MEDIA`·`Port` | `vpn`·`rastapi`·`VPN2-0` | 장치에 딸린 칸입니다. 칸마다 뜻은 확인하지 않았습니다 |
| `Type` | `2` | 이 값이 VPN 을 뜻하는지는 확인하지 못했습니다 |
| `VpnStrategy` | `0` | 숫자마다 뜻은 확인하지 못했습니다 |
| `PreSharedKey` | 비어 있음 | 사전 공유 키 (pre-shared key) 칸입니다. 시험 프로필에서는 비어 있었습니다 |
| `PowershellCreatedProfile` | `1` | PowerShell 로 만든 프로필에서 본 값입니다. 설정 앱으로 만든 프로필은 보지 못했습니다 |
| `LowDateTime`·`HighDateTime` | `1806595920`·`31279980` | 두 칸을 합치면 FILETIME 이 됩니다. 시험에서는 프로필을 만든 시각과 같았습니다 |

`LowDateTime`·`HighDateTime` 이 접속할 때마다 바뀌는지는 확인하지 못했습니다.

### 접속 이벤트 (Application 로그, RasClient)

메시지 틀은 `mprmsg.dll` 에서 읽었습니다. 원문은 영어이고, 아래는 뜻을 줄여 옮긴 것입니다. (확인 범위: 조사 PC)

| ID | 뜻 | 빈자리에 들어가는 값 |
|---|---|---|
| 20221 | 접속을 시작했습니다 | `%1` CoId, `%2` 사용자, `%3` 연결 종류, `%4` 프로필 종류, `%5` 프로필 이름, `%6` 설정 목록 |
| 20222 | 원격 접속 서버와 링크를 맺으려 합니다 | `%3` 연결 이름, `%4` 장치 |
| 20223 | 링크를 맺었습니다 | `%3` 장치 |
| 20224 | 사용자가 링크를 맺었습니다 | `%2` 사용자 |
| 20225 | 접속에 성공했습니다 | `%3` 연결 이름, `%4` 접속 값 |
| 20226 | 접속이 끝났습니다 | `%3` 연결 이름, `%4` 끝난 이유 코드 |
| 20227 | 접속에 실패했습니다 | `%3` 연결 이름, `%4` 오류 코드 |
| 20220 | 장치로 맺은 연결이 끊겼습니다 | `%1` 대상, `%2` 장치 |

같은 dll 에는 20267(연결 성공)과 20268(연결 끊김)도 있습니다. RasClient 가 이 둘을 쓰는지, 서버 쪽 메시지인지는 확인하지 못했습니다.

존재하지 않는 서버 이름으로 시험 접속을 해 봤습니다. (확인 범위: 조사 PC 시험, `rasdial` 사용)

- 20221 → 20222 → 20227 순서로 남았습니다. 20227 의 오류 코드는 868(서버 이름을 풀지 못함)이었습니다.
- 세 이벤트의 CoId(GUID)가 같았습니다. CoId 로 한 번의 접속 시도에 속한 이벤트를 묶습니다.
- 20221 의 `%3` 은 "VPN", `%4` 는 "per-user" 였습니다.
- 20221 의 `%6` 에는 설정이 여러 줄로 들어 있었습니다. 예: `VpnStrategy = IKEv2 , SSTP , PPTP then L2TP`, `Authentication Type = MS-CHAPv2`, `Ipv4DefaultGateway = Yes`
- 20222 의 `%4` 에는 `Server address/Phone Number = vpn.invalid`, `Device = WAN Miniport (SSTP)`, `Port = VPN1-1`, `MediaType = VPN` 이 들어 있었습니다.

### 프로필 이벤트 (VPN-Client/Operational)

| ID | 뜻 |
|---|---|
| 10001 | 프로필 생성. 메시지에 속성 목록이 들어갑니다 |
| 10002 | 프로필 생성 실패 |
| 10003 | 프로필 삭제 |
| 10004 | 프로필 삭제 실패 |
| 10005 | 프로필 수정 |
| 10006 | 프로필 수정 실패 |
| 10007·10008 | 일부 속성을 반영하지 못함 |

(확인 범위: 조사 PC)

- `Add-VpnConnection` 으로 만든 시험 프로필의 10001 에는 ServerAddress, RememberCredential, SplitTunneling, AllUserConnection, TunnelType, L2tpPsk 가 적혔습니다. (확인 범위: 조사 PC 시험)
- 프로필을 지우자 10003 "VPN Profile ZZTestVPN has been deleted." 가 남았습니다. (확인 범위: 조사 PC 시험)
- 설정 앱이나 rasphone 으로 만든 프로필도 10001 을 남기는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것**

- `rasphone.pbk` 의 절 하나는 수집 시점에 그 이름의 VPN 프로필이 있었다는 기록입니다.
- `PhoneNumber` 는 그 프로필에 적힌 서버 주소입니다.
- 파일 위치로 사용자별 프로필인지 모든 사용자용 프로필인지 가립니다.
- 20227 은 그 시각에 그 프로필로 접속을 시도했고 실패했다는 기록입니다. 오류 코드가 같이 남습니다.
- 20225 는 접속 성공, 20226 은 접속 종료와 이유 코드를 보여 줍니다.
- 10003 은 파일에서 사라진 프로필의 이름과 삭제 시각을 보여 줍니다.

**증명하지 못하는 것**

- 프로필이 있다고 접속했다는 뜻은 아닙니다. 접속은 RasClient 이벤트로 따로 확인합니다.
- RasClient 의 사용자 칸이 접속한 사람을 가리키지 않을 수 있습니다(아래 함정 참고).
- 접속 성공 기록은 VPN 으로 무엇을 주고받았는지 보여 주지 않습니다.
- 서드파티 VPN 프로그램은 이 기록을 남기는지 확인하지 않았습니다. RasClient 기록이 없다고 VPN 을 쓰지 않았다고 단정하지 않습니다.

보고서에는 기록이 말하는 만큼만 씁니다. 예를 들면 "Application 로그에 사용자별 VPN 프로필 `ZZTestVPN` 으로 서버 `vpn.invalid` 에 접속을 시도해 오류 코드 868 로 실패한 기록(20221·20222·20227, 같은 CoId)이 있다. 이벤트의 사용자 칸은 SYSTEM 이라 접속을 시도한 사용자를 이 기록만으로 알 수 없다." 처럼 씁니다. 예의 값은 조사 PC 시험 값입니다.

## 시각 해석

- `LowDateTime` 은 FILETIME 의 아래 32비트, `HighDateTime` 은 위 32비트로 읽습니다. 합친 값은 UTC 입니다. 계산은 아래 "헥스로 한 번" 에서 따라갑니다.
- 시험 프로필에서 두 칸을 합친 값은 2026-09-23T15:01:32.613Z 로, 프로필을 만든 시각과 같았습니다. (확인 범위: 조사 PC 시험)
- 이벤트 시각은 레코드 시각입니다. 레코드 시각을 읽는 법은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.
- 같은 CoId 의 20225 와 20226 이 있으면 두 시각의 차이로 접속이 이어진 시간을 가늠합니다. 이번 시험은 실패한 접속이라 이 쌍을 직접 보지는 못했습니다.
- `rasphone.pbk` 파일의 파일 시스템 시각은 [마스터 파일 테이블](../filesystem/mft.md)에서 읽습니다.

## 함정과 한계

- **사용자 칸이 SYSTEM 으로 남을 수 있습니다.** 관리자 권한 PowerShell 에서 `rasdial` 로 접속하자 `%2` 가 로그인한 사용자 이름이 아니라 "SYSTEM" 이었습니다. 이벤트 레코드의 UserId(보안 SID)도 비어 있었습니다. (확인 범위: 조사 PC 시험) 설정 앱에서 접속했을 때 어떻게 남는지는 확인하지 못했습니다.
- **지운 프로필은 파일에 남지 않습니다.** 프로필을 지우자 그 절만 빠진 것이 아니라 `rasphone.pbk` 파일 자체가 사라졌습니다. 시험 파일에는 항목이 하나뿐이었습니다. 사용자용·모든 사용자용 둘 다 같았습니다. (확인 범위: 조사 PC 시험) 지운 프로필 내용은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)나 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md)으로 찾습니다. 이 판단은 시험 관찰에서 나온 추론입니다.
- **pbk 의 장치와 이벤트의 장치가 다를 수 있습니다.** 시험 프로필의 `Device` 칸은 IKEv2 였지만 20222 의 장치는 SSTP 였습니다. (확인 범위: 조사 PC 시험) 한 칸만 보고 실제로 쓴 터널 종류를 단정하지 않습니다.
- **기록이 아예 없을 수 있습니다.** 조사 PC 에는 시험 전까지 RasClient 이벤트가 한 건도 없었습니다. (확인 범위: 조사 PC)
- **VPN-Client/Operational 은 최대 1MB 입니다.** 오래 쓴 PC 에서는 앞선 기록이 밀려났을 수 있습니다.
- **추적 로그는 기본값이 꺼져 있습니다.** `EnableFileTracing` 이 1 이 아니면 추적 로그를 기대하지 않습니다.
- **네트워크 목록과의 관계가 확인되지 않았습니다.** RegRipper networklist 플러그인은 NameType 0x17 을 "broadband (3g)" 로 표시합니다. VPN 연결이 이 값으로 네트워크 목록에 남는다는 설명이 흔하지만 이번에 확인하지 못했습니다. 시험 접속은 실패해서 네트워크 목록에 새 프로필이 생기지 않았습니다. (확인 범위: 조사 PC 시험) 목록을 읽는 법은 [네트워크 목록](networklist.md)에서 다룹니다.
- **메시지 문장은 분석 PC 에서 만듭니다.** RasClient 레코드에는 빈자리 값만 들어 있고 문장 틀은 메시지 파일에서 읽습니다. 자세한 내용은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

`rasphone.pbk` 는 텍스트 파일입니다. 헥스로 풀어야 할 이진 구조는 시각 두 칸뿐입니다. 아래는 조사 PC 시험 프로필의 값으로 FILETIME 을 만드는 과정입니다.

| 단계 | 값 |
|---|---|
| `HighDateTime` (10진) | 31279980 |
| `HighDateTime` (16진) | `0x01DD4B6C` |
| `LowDateTime` (10진) | 1806595920 |
| `LowDateTime` (16진) | `0x6BAE7750` |
| 합친 64비트 값 (High 를 위, Low 를 아래에) | `0x01DD4B6C6BAE7750` = 134346492926130000 |
| 1601-01-01 부터 센 100ns 단위로 읽음 | 2026-09-23T15:01:32.613Z |

다른 아티팩트에서 이 FILETIME 을 리틀 엔디언 8바이트로 찾는다면 `50 77 AE 6B 6C 4B DD 01` 로 보입니다. 이 바이트열은 위 값을 규칙대로 뒤집어 만든 예시입니다. FILETIME 을 읽는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다.

파일 인코딩은 이번에 기록하지 않았습니다. 파일 앞 몇 바이트로 BOM 이 있는지 먼저 확인합니다. 인코딩을 가리는 법은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.

### 공개 도구로 한 번

전화번호부 파일에서 연결 이름과 주요 칸을 뽑습니다. `Device` 와 `DEVICE` 가 대소문자만 다른 칸이라 INI 읽기 라이브러리 대신 줄을 직접 나눕니다.

```python
from datetime import datetime, timedelta

path = r"E:\mount\Users\<사용자>\AppData\Roaming\Microsoft\Network\Connections\Pbk\rasphone.pbk"   # 마운트한 경로로 바꿉니다
keys = {"PhoneNumber", "Device", "Type", "VpnStrategy", "LowDateTime", "HighDateTime"}

with open(path, encoding="utf-8", errors="replace") as f:   # BOM 을 확인한 뒤 인코딩을 맞춥니다
    entry = {}
    for line in f:
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            entry = {"name": line[1:-1]}
            print("\n연결 이름:", entry["name"])
        elif "=" in line:
            k, v = line.split("=", 1)
            if k in keys:
                print(f"  {k} = {v}")
                entry[k] = v
            if "LowDateTime" in entry and "HighDateTime" in entry:
                ft = (int(entry["HighDateTime"]) << 32) | int(entry["LowDateTime"])
                print("  FILETIME(UTC):", datetime(1601, 1, 1) + timedelta(microseconds=ft // 10))
                entry.pop("LowDateTime"); entry.pop("HighDateTime")
```

RasClient 이벤트는 PowerShell 로 CoId 별로 묶습니다. 수집한 evtx 파일을 열 때는 `Path` 에 그 파일 경로를 넣습니다.

```powershell
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\Application.evtx'; ProviderName = 'RasClient'; Id = 20220..20227 } |
  Select-Object @{ n = 'UTC'; e = { $_.TimeCreated.ToUniversalTime() } }, Id,
                @{ n = 'CoId'; e = { if ($_.Message -match 'CoId=([^:]+):') { $Matches[1] } } }, Message |
  Sort-Object CoId, UTC
```

프로필 생성·삭제는 `Id = 10001, 10003` 으로 거릅니다. 수집한 `VPN-Client/Operational` evtx 파일 경로를 `Path` 에 넣습니다. `TimeCreated` 는 분석 PC 의 시간대로 보여서 위 코드는 UTC 로 바꿔 출력합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 프리페치 | `rasdial` 을 실행한 뒤 `RASDIAL.EXE-0870CD35.pf` 가 생겼습니다 (확인 범위: 조사 PC 시험) | [프리페치](../execution/prefetch/index.md) |
| PowerShell 명령 기록 | PowerShell 로 프로필을 만들거나 접속한 명령이 남았는지 봅니다 | [PowerShell 명령 기록](../execution/consolehost-history-txt.md) |
| 네트워크 목록 | VPN 접속으로 새 네트워크 프로필이 생겼는지 봅니다 | [네트워크 목록](networklist.md) |
| 네트워크 인터페이스 설정 | 접속 때 받은 주소 설정이 남았는지 봅니다 | [네트워크 인터페이스 설정](tcp-ip-interfaces.md) |
| 섀도 복사본 | 지운 `rasphone.pbk` 의 예전 내용 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 로그온·로그오프 | 접속 시각에 로그온해 있던 사용자 | [로그온·로그오프](../event-logs/logon-events/index.md) |
| 시간대 설정 | 다른 현지 시각 기록과 맞출 때 | [시간대 설정](../system-account/time-zone.md) |

## 실습

공개 검체(NIST CFReDS 등) 가운데 윈도 내장 VPN 을 쓴 이미지를 골라 아래 질문을 풀어 봅니다.

1. 사용자별 `rasphone.pbk` 와 모든 사용자용 `rasphone.pbk` 가 각각 있습니까? 절은 몇 개입니까?
2. 각 절의 `PhoneNumber` 와 `Device` 는 무엇입니까? `LowDateTime`·`HighDateTime` 을 합친 시각은 언제입니까?
3. Application 로그에 RasClient 이벤트가 있습니까? CoId 로 묶으면 접속 시도는 몇 번이고, 성공(20225)·실패(20227)는 각각 몇 번입니까?
4. 20227 의 오류 코드와 20226 의 이유 코드는 무엇입니까?
5. `VPN-Client/Operational` 에 10003 이 있습니까? 지금 `rasphone.pbk` 에 없는 프로필 이름이 있습니까?
6. 20221 의 사용자 칸은 로그인한 사용자 이름입니까, SYSTEM 입니까?

## 참고 문헌

1. keydet89/RegRipper3.0, plugins/networklist.pl (master, 커밋 ec96dd4a). https://codeload.github.com/keydet89/RegRipper3.0/tar.gz/refs/heads/master

이 페이지의 나머지 사실은 조사 PC 에서 직접 확인했습니다.
