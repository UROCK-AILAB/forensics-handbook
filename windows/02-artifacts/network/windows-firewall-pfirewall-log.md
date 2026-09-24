# 윈도 방화벽 (Windows Firewall: 규칙·pfirewall.log)

> 이 페이지에서 "(확인 범위: 조사 PC)" 는 Windows 11 Home 25H2(빌드 26200.9457) PC 한 대에서 직접 본 사실을 뜻합니다. "(확인 범위: 조사 PC 시험)" 은 같은 PC 에서 방화벽 로그를 일부러 켰다가 끄며 본 사실입니다. 다른 버전이나 다른 PC 에서는 따로 확인해야 합니다.

## 한 줄 요약

윈도 방화벽의 흔적은 세 곳에 남습니다. 설정과 규칙은 SYSTEM 하이브의 `FirewallPolicy` 키에, 규칙을 더하거나 지운 기록은 방화벽 이벤트 채널에 남습니다. 허용·차단한 통신은 `pfirewall.log` 에 남지만, 이 로그는 기본으로 꺼져 있습니다.

## 무엇을 기록하나 · 왜 생기나

방화벽은 규칙에 따라 드나드는 연결을 허용하거나 막습니다. 프로그램을 설치하거나 사용자가 설정을 바꾸면 규칙이 생기거나 바뀝니다. 그때마다 레지스트리 값과 이벤트가 남습니다.

| 기록 | 생기는 때 | 알려 주는 것 |
|---|---|---|
| 프로필 설정 (레지스트리) | 방화벽을 켜거나 끌 때, 기본 동작을 바꿀 때 | 프로필마다 방화벽이 켜져 있는지, 알림을 끄는지 |
| 규칙 (레지스트리) | 규칙을 만들거나 고칠 때 | 방향, 허용·차단, 프로그램 경로, 포트, 주소 |
| 로그 설정 (레지스트리) | 로그 설정을 바꿀 때 | 로그를 켰는지, 로그 파일 경로와 크기 |
| `pfirewall.log` | 로그를 켠 뒤 패킷을 허용하거나 막을 때 | 시각, 허용·차단, 주소·포트, 방향, 프로세스 ID |
| 방화벽 이벤트 채널 | 규칙·설정이 바뀔 때, 네트워크 프로필이 바뀔 때 | 바꾼 규칙, 바꾼 사용자 SID, 바꾼 프로그램 |
| Security 로그 (4946~4948·4950, 5024·5025·5031, 5152·5156·5157) | 감사를 켜 둔 PC 에서 | 규칙 변경, 서비스 시작·중지, 연결 허용·차단과 프로그램 경로 |

이 기록으로 아래 질문에 답합니다.

- 방화벽이 꺼져 있었나, 언제 누가 설정을 바꿨나
- 어떤 프로그램에 받는 연결을 허용하는 규칙이 있나, 그 규칙은 언제 누가 만들었나
- 로그를 켜 둔 PC 라면, 어느 주소와 어느 포트로 통신했나

## 위치와 버전별 차이

| 기록 | 위치 | 메모 |
|---|---|---|
| 방화벽 설정 기본 키 | SYSTEM `CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy` | ForensicArtifacts 가 정의한 위치입니다. 조사 PC 에서도 같았습니다 |
| 프로필 설정 | `...\FirewallPolicy\DomainProfile`·`StandardProfile`·`PublicProfile` | `StandardProfile` 이 "개인 (Private)" 프로필이라는 대응은 이번에 확인하지 못했습니다 |
| 규칙 | `...\FirewallPolicy\FirewallRules` | 조사 PC 에는 581개가 있었습니다 (확인 범위: 조사 PC) |
| 스토어 앱 규칙 | `...\FirewallPolicy\RestrictedServices\AppIso\FirewallRules` | 조사 PC 에는 540개가 있었습니다 (확인 범위: 조사 PC) |
| 로그 설정 | 각 프로필 키 아래 `Logging` | (확인 범위: 조사 PC) |
| 통신 로그 | `%windir%\system32\logfiles\firewall\pfirewall.log` | 기본 경로입니다(Microsoft 문서, ForensicArtifacts) |
| 이벤트 채널 | `Microsoft-Windows-Windows Firewall With Advanced Security/Firewall` | 파일은 `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-Windows Firewall With Advanced Security%4Firewall.evtx` 입니다. 기본으로 켜져 있고 최대 1MB 입니다 (확인 범위: 조사 PC) |
| 같은 공급자의 다른 채널 | ConnectionSecurity·FirewallDiagnostics(켜짐), FirewallVerbose·ConnectionSecurityVerbose(꺼짐) | 내용은 이번에 확인하지 않았습니다 (확인 범위: 조사 PC) |
| Security 로그 | 4946~4948·4950, 5024·5025, 5031, 5152·5156·5157 | 감사 정책을 켜야 남습니다 |
| 그룹 정책 | `HKLM\SOFTWARE\Policies\Microsoft\WindowsFirewall` | 조사 PC 에는 이 키가 없었습니다. 그룹 정책을 적용하지 않은 PC 입니다 (확인 범위: 조사 PC) |

- 조사 PC 의 `FirewallPolicy` 아래에는 DomainProfile, StandardProfile, PublicProfile, FirewallRules, RestrictedServices, RestrictedInterfaces, DynamicKeywords, HyperVFirewallPolicy, HyperVVMCreators, Mdm, TenantRestrictions 하위 키가 있었습니다. (확인 범위: 조사 PC)
- 오프라인 SYSTEM 하이브에는 `CurrentControlSet` 이 없습니다. `Select` 키가 가리키는 `ControlSet00n` 을 읽습니다. 하이브 구조는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

옛 방식의 예외 목록은 윈도 버전마다 위치가 다릅니다. ForensicArtifacts 는 아래 위치를 수집 대상으로 정의합니다.

| 윈도 | 예외 목록 위치 |
|---|---|
| XP·2003 | `HKLM\Software\Policies\Microsoft\WindowsFirewall\<프로필>\...` |
| Vista 이후 | `...\FirewallPolicy\<프로필>\AuthorizedApplications\List`, `...\FirewallPolicy\<프로필>\GloballyOpenPorts\List` |

규칙 이벤트 번호도 두 벌입니다. 공급자에는 옛 번호와 새 번호가 모두 정의돼 있지만, 조사 PC 에 실제로 남은 것은 새 번호뿐이었습니다. (확인 범위: 조사 PC) 어느 윈도 버전부터 새 번호로 바뀌었는지는 확인하지 못했습니다.

| 뜻 | 옛 번호 | 새 번호 |
|---|---|---|
| 규칙 추가 | 2004 | 2097 |
| 규칙 수정 | 2005 | 2099 |
| 규칙 삭제 | 2006 | 2052 |
| 프로필 설정 변경 | 2003 | 2082 |
| 설정 변경 | 2002 | 2083 |
| 기본값으로 초기화 | 2032 | 2060 |
| 모든 규칙 삭제 | 2033 | 2059 |

새 번호의 메시지에는 Error Code 가 붙습니다. 2097·2099 에는 PolicyAppId 도 붙습니다. (확인 범위: 조사 PC)

## 구조

### 프로필 설정

ForensicArtifacts 는 프로필 키에서 아래 값을 봅니다. 조사 PC 의 `StandardProfile` 값을 함께 적었습니다.

| 값 | 조사 PC `StandardProfile` |
|---|---|
| `EnableFirewall` | 1 |
| `DisableNotifications` | 0 |
| `DoNotAllowExceptions` | 적지 않았습니다 |
| `DefaultInboundAction` | 적지 않았습니다 |
| `DefaultOutboundAction` | 적지 않았습니다 |

ForensicArtifacts 설명에 따르면 악성코드가 이 값들을 바꿔 통신을 쉽게 만들며, Emotet 이 그 예입니다.

### 규칙 문자열

규칙은 `FirewallRules` 키에 값 하나당 하나씩 들어 있습니다. 값 데이터는 `|` 로 나눈 문자열입니다. 아래는 조사 PC 의 윈도 기본 규칙 하나입니다.

```
v2.33|Action=Allow|Active=FALSE|Dir=Out|Protocol=6|Profile=Public|RPort=2869|RA4=LocalSubnet|RA6=LocalSubnet|App=%SystemRoot%\system32\svchost.exe|Svc=fdphost|Name=@FirewallAPI.dll,-32765|Desc=@FirewallAPI.dll,-32768|EmbedCtxt=@FirewallAPI.dll,-32752|
```

칸의 공식 정의는 이번 자료로 확인하지 않았고, 아래 표의 뜻은 칸 이름과 2097 이벤트의 데이터 칸 이름(LocalPorts·RemotePorts·RemoteAddresses·ApplicationPath·ServiceName 등)을 보고 읽은 것입니다.

| 칸 | 예의 값 | 읽는 법 |
|---|---|---|
| 맨 앞 | `v2.33` | 규칙 문자열의 버전입니다 |
| `Action` | `Allow` | 허용인지 차단인지 |
| `Active` | `FALSE` | 규칙이 켜져 있는지 |
| `Dir` | `Out` | 방향입니다. 받는 방향은 `In` 입니다 |
| `Protocol` | `6` | IP 프로토콜 번호입니다. 6 은 TCP 입니다 |
| `Profile` | `Public` | 규칙을 적용할 프로필 |
| `LPort`·`RPort` | `5353`·`2869` | 로컬 포트·원격 포트 (`LPort=5353` 은 다른 규칙에서 본 값입니다) |
| `RA4`·`RA6` | `LocalSubnet` | IPv4·IPv6 원격 주소 조건 |
| `App` | `%SystemRoot%\system32\svchost.exe` | 규칙이 가리키는 프로그램 경로 |
| `Svc` | `fdphost` | 규칙이 가리키는 서비스 이름 |
| `Name`·`Desc`·`EmbedCtxt` | `@FirewallAPI.dll,-32765` | dll 의 문자열 리소스를 가리키는 참조입니다 |
| `Defer` | `User` | 다른 규칙에서 본 칸입니다. 뜻은 확인하지 못했습니다 |
| `TTK2_22` | `WFDPrint` | 다른 규칙에서 본 칸입니다. 뜻은 확인하지 못했습니다 |

값 이름과 `Name` 칸의 모양으로 규칙이 어디서 왔는지 가립니다. (확인 범위: 조사 PC)

| 규칙 | 값 이름 | `Name` 칸 |
|---|---|---|
| 윈도 기본 규칙 | 규칙 ID. 예: `NETDIS-UPnPHost-Out-TCP` | `@FirewallAPI.dll,-번호` 같은 리소스 참조 |
| 프로그램이 추가한 규칙 | `{GUID}` | 평문 이름. 조사 PC 에는 72개가 있었습니다 |

- 조사 PC 의 규칙 581개 가운데 569개는 버전이 `v2.33`, 12개는 `v2.10` 이었습니다. (확인 범위: 조사 PC)
- `v2.10` 12개는 이름이 모두 `TCP Query User{GUID}<실행 파일 경로>` 나 `UDP Query User{GUID}<경로>` 꼴이었습니다. 모두 받는 방향(`Dir=In`) 허용 규칙이었고 `Defer=User` 가 붙어 있었습니다. (확인 범위: 조사 PC)
- 이 Query User 규칙에는 사용자 폴더 아래 실행 파일 경로가 그대로 들어 있었습니다. (확인 범위: 조사 PC)
- Query User 규칙이 "방화벽이 일부 기능을 차단했습니다" 알림에 사용자가 답할 때 생긴다는 설명은 확인하지 못했습니다.

### 로그 설정

각 프로필 키 아래 `Logging` 하위 키에 로그 설정이 있습니다. (확인 범위: 조사 PC)

| 값 | 조사 PC 값 |
|---|---|
| `LogDroppedPackets` | 0 |
| `LogSuccessfulConnections` | 0 |
| `LogFileSize` | 4096 |
| `LogFilePath` | `C:\WINDOWS\system32\LogFiles\Firewall\pfirewall.log` |

Microsoft 문서에 따르면 로그의 기본 최대 크기는 4,096KB 입니다. "Log dropped packets" 나 "Log successful connections" 가운데 하나를 Yes 로 바꾸기 전에는 아무것도 기록하지 않습니다. 문서는 20,480KB 이상을 권하고, 최대 크기는 32,767KB 입니다. 프로필마다 `pfirewall_Domain.log`·`pfirewall_Private.log`·`pfirewall_Public.log` 로 나누라고도 권합니다. 그래서 파일 이름은 `LogFilePath` 값에서 확인합니다.

MDM 으로 Firewall CSP 를 써서 관리하는 PC 는 프로필마다 `./Vendor/MSFT/Firewall/MdmStore/<프로필>/...` 아래 `EnableLogDroppedPackets`, `EnableLogSuccessConnections`, `LogFilePath`, `LogMaxFileSize` 로 설정합니다(Microsoft 문서).

### pfirewall.log

머리글은 네 줄입니다. (확인 범위: 조사 PC 시험)

```
#Version: 1.5
#Software: Microsoft Windows Firewall
#Time Format: Local
#Fields: date time action protocol src-ip dst-ip src-port dst-port size tcpflags tcpsyn tcpack tcpwin icmptype icmpcode info path pid
```

기록 한 줄은 칸 18개를 공백으로 나눈 것입니다. 아래는 조사 PC 시험에서 본 줄입니다.

```
2026-09-24 00:07:09 ALLOW TCP 192.168.1.239 172.66.147.243 57261 80 0 - 0 0 0 - - - SEND 41752
```

| 칸 | 예의 값 | 읽는 법 |
|---|---|---|
| `date`·`time` | `2026-09-24`·`00:07:09` | 현지 시각입니다. 시간대 표시가 없습니다 |
| `action` | `ALLOW` | `ALLOW` 나 `DROP` 입니다 |
| `protocol` | `TCP` | 프로토콜 |
| `src-ip`·`dst-ip` | `192.168.1.239`·`172.66.147.243` | 출발지·목적지 주소 |
| `src-port`·`dst-port` | `57261`·`80` | 출발지·목적지 포트 |
| `size` | `0` | 패킷 크기입니다. 시험에서 `ALLOW` 줄은 모두 0 이었습니다. `DROP` 줄에는 426·435 같은 크기가 있었습니다 |
| `tcpflags`·`tcpsyn`·`tcpack`·`tcpwin` | `-`·`0`·`0`·`0` | TCP 머리 값 |
| `icmptype`·`icmpcode` | `-`·`-` | ICMP 줄에서만 값이 들어갑니다. 예: `8 0` |
| `info` | `-` | |
| `path` | `SEND` | `SEND` 나 `RECEIVE` 입니다 |
| `pid` | `41752` | 프로세스 ID 입니다. 프로그램 이름은 없습니다 |

- 빈 칸은 `-` 로 채웁니다. (확인 범위: 조사 PC 시험)
- 파일 인코딩은 ASCII, 줄바꿈은 CRLF 였습니다. (확인 범위: 조사 PC 시험)
- 머리글 바로 뒤에 NUL(0x00) 212바이트가 있었고, 그 뒤에 첫 기록이 이어졌습니다. (확인 범위: 조사 PC 시험)
- Public 프로필에서 두 옵션을 모두 켜자 약 6분 동안 54줄이 쌓였습니다. `ALLOW` 가 37줄, `DROP` 이 13줄이었습니다. (확인 범위: 조사 PC 시험)

### 방화벽 이벤트 채널

조사 PC 에 실제로 남은 이벤트 수입니다. (확인 범위: 조사 PC)

| ID | 뜻 | 건수 |
|---|---|---|
| 2052 | 규칙 삭제 | 417 |
| 2097 | 규칙 추가 | 414 |
| 2010 | 인터페이스의 네트워크 프로필 변경 | 92 |
| 2084 | 뜻은 이번에 확인하지 않았습니다 | 31 |
| 2099 | 규칙 수정 | 24 |
| 2051 | 뜻은 이번에 확인하지 않았습니다 | 7 |
| 2059 | 모든 규칙 삭제 | 7 |
| 2004·2005·2006 | 옛 번호 규칙 추가·수정·삭제 | 0 |

2097 메시지에는 아래 칸이 있습니다. (확인 범위: 조사 PC)

- Rule ID, Rule Name, Origin, Active, Direction, Profiles, Action, Application Path, Service Name, Protocol, Security Options, Edge Traversal, Modifying User, Modifying Application, PolicyAppId, Error Code

2097 이벤트 데이터의 칸 이름은 RuleId, RuleName, Origin, ApplicationPath, ServiceName, Direction, Protocol, LocalPorts, RemotePorts, Action, Profiles, LocalAddresses, RemoteAddresses, EmbeddedContext, Flags, Active, EdgeTraversal, SecurityOptions, ModifyingUser, ModifyingApplication, SchemaVersion, RuleStatus, PolicyAppId, ErrorCode 등입니다. (확인 범위: 조사 PC)

- 스토어 앱 규칙을 더하고 지운 기록은 `ModifyingUser` 가 서비스 SID(`S-1-5-80-…`), `ModifyingApplication` 이 `C:\WINDOWS\System32\svchost.exe` 로 남았습니다. (확인 범위: 조사 PC)
- `netsh` 로 로그 설정을 바꾸자 2082 가 두 건 남았습니다. 하나는 "Type: Log Dropped Packets Value: 예", 다른 하나는 "Type: Log Successful Connections Value: 예" 였습니다. Modifying User 에는 사용자 SID, Modifying Application 에는 `C:\Windows\System32\netsh.exe` 가 들어 있었습니다. (확인 범위: 조사 PC 시험)
- 2010 에는 Adapter GUID, Adapter Name, Old Profile, New Profile 칸이 있습니다. (확인 범위: 조사 PC)
- 2011 은 받는 연결을 막았지만 사용자에게 알리지 못한 기록입니다. Application Path, Protocol, Port, Process Id, User 칸이 있습니다. (확인 범위: 조사 PC)

### Security 로그의 방화벽 이벤트

감사 정책을 켜 둔 PC 에서만 남습니다. 어느 감사 하위 범주를 켜야 하는지는 이번에 확인하지 못했습니다. 감사 설정은 [감사 정책과 로그 설정](../event-logs/audit-policy-log-settings.md)에서 다룹니다.

| ID | 뜻 | 칸 |
|---|---|---|
| 4946 | 규칙 추가 | Profile Changed, Rule ID, Rule Name |
| 4947 | 규칙 수정 | 같음 |
| 4948 | 규칙 삭제 | 같음 |
| 4950 | 방화벽 설정 변경 | Changed Profile, Type, Value |
| 5024 | 방화벽 서비스 시작 | |
| 5025 | 방화벽 서비스 중지 | |
| 5031 | 받는 연결을 막음 | Profiles, Application |
| 5152 | WFP 가 패킷을 막음 | Process ID, Application Name, Direction, 주소·포트, Protocol, Filter 정보 |
| 5156 | WFP 가 연결을 허용함 | 같음 |
| 5157 | WFP 가 연결을 막음 | 같음 |

(확인 범위: 조사 PC)

WFP 는 윈도 필터링 플랫폼 (Windows Filtering Platform) 입니다. 5156·5157 에는 프로세스 경로가 있습니다. 그래서 pid 만 남는 `pfirewall.log` 보다 프로그램을 잇기 쉽습니다.

## 증거로서 의미

**증명하는 것**

- 규칙 값 하나는 수집 시점에 그 규칙이 있었다는 기록입니다. `App` 칸은 규칙이 가리키는 프로그램 경로입니다.
- 값 이름이 `{GUID}` 이고 `Name` 이 평문인 규칙은 윈도 기본 규칙이 아닐 가능성이 큽니다. 이 구분은 조사 PC 관찰에서 나온 것입니다.
- Query User 규칙의 경로는 그 실행 파일에 받는 연결을 허용하는 규칙이 있었다는 기록입니다.
- 2097·2099·2052 는 규칙을 더하고 고치고 지운 시각과 규칙 이름을 보여 줍니다. 바꾼 사용자 SID 와 프로그램도 남습니다.
- 2082 는 프로필 설정을 바꾼 시각, 바꾼 사용자 SID, 바꾼 프로그램을 보여 줍니다.
- `pfirewall.log` 한 줄은 그 현지 시각에 그 주소·포트 사이의 패킷을 허용하거나 막았다는 기록입니다.

**증명하지 못하는 것**

- 규칙이 있다고 그 규칙으로 통신했다는 뜻은 아닙니다.
- `pfirewall.log` 가 없거나 비어 있다고 통신이 없었던 것은 아닙니다. 로그는 기본으로 꺼져 있습니다.
- `ALLOW` 줄은 연결을 허용한 기록일 뿐입니다. 주고받은 데이터 양을 알려 주지 않습니다.
- `pfirewall.log` 의 pid 만으로는 프로그램을 특정하지 못합니다.
- 레지스트리의 규칙 값에는 만든 시각이 없습니다.
- `ModifyingUser` 가 서비스 SID 라면 사람이 직접 바꾼 기록이 아닐 수 있습니다. 스토어 앱 규칙은 이렇게 남았습니다.

보고서에는 기록이 말하는 만큼만 씁니다. 예를 들면 "방화벽 이벤트 채널에 사용자 SID `S-1-5-21-…` 가 `netsh.exe` 로 방화벽 로그 설정을 바꾼 기록(2082 두 건)이 있다." 처럼 씁니다. 또 "`pfirewall.log` 에 현지 시각 2026-09-24 00:07:09 에 192.168.1.239 에서 172.66.147.243 의 80번 포트로 나가는(SEND) TCP 통신을 허용한 기록이 있고, 프로세스 ID 는 41752 로 적혀 있다." 처럼 씁니다. 예의 값은 조사 PC 시험 값입니다.

## 시각 해석

- `pfirewall.log` 의 시각은 현지 시각이고 시간대 표시가 없습니다(`#Time Format: Local`). UTC 로 바꾸려면 그 PC 의 [시간대 설정](../system-account/time-zone.md)을 따로 확인합니다.
- 로그를 켠 직후의 통신은 바로 파일에 쓰이지 않았습니다. 약 1분 뒤에 다시 보니 들어와 있었습니다. (확인 범위: 조사 PC 시험) 수집 직전의 통신은 파일에 아직 없을 수 있습니다.
- 레지스트리 값에는 시각이 없습니다. `FirewallRules` 키의 마지막 기록 시각은 어느 규칙이 바뀌었는지 알려 주지 않습니다. 규칙마다 언제 생겼는지는 2097 로 봅니다.
- 이벤트 시각은 레코드 시각입니다. 레코드 시각을 읽는 법은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.
- 조사 PC 의 방화벽 채널(1MB)에는 992건이 있었습니다. 2026-09-05 부터 2026-09-23 까지 약 18일만 남아 있었습니다. (확인 범위: 조사 PC)

## 함정과 한계

1. **로그는 기본으로 꺼져 있습니다.** 조사 PC 는 시험 전에 `LogFiles\Firewall` 폴더 자체가 없었습니다. `netsh` 로 로그를 켜자 방화벽 서비스가 폴더와 파일을 만들었습니다. (확인 범위: 조사 PC 시험)
2. **로그를 켜도 파일이 생기지 않을 수 있습니다.** Microsoft 문서에 따르면 로그 폴더나 파일에 방화벽 서비스(`NT SERVICE\mpssvc`)의 쓰기 권한이 없으면 로그가 생기지 않습니다. 정책으로 로그를 켰는데 기본 폴더 `%windir%\System32\LogFiles\firewall` 이 없을 때도 생기지 않습니다.
3. **로그 크기에 한도가 있습니다.** 문서는 최대 크기에 이르면 오래된 항목을 지우고 새 항목을 쓴다고 적었습니다. 조사 PC 시험에서는 로그를 켜자 `pfirewall.log` 와 함께 0바이트 `pfirewall.log.old` 가 생겼습니다. `.old` 파일도 함께 수집합니다.
4. **파일 이름이 기본값과 다를 수 있습니다.** 프로필마다 파일을 나누었을 수 있습니다. 각 프로필의 `LogFilePath` 를 먼저 읽습니다.
5. **시각이 현지 시각입니다.** UTC 로 적힌 다른 기록과 섞을 때 시간대를 먼저 맞춥니다.
6. **pid 만 있습니다.** 프로세스 ID 는 다시 쓰일 수 있습니다. 같은 시각의 다른 기록으로 프로그램을 잇습니다.
7. **첫 기록 앞에 NUL 바이트가 있습니다.** 텍스트 도구가 첫 줄을 깨뜨려 보여 줄 수 있습니다. NUL 을 지우고 읽습니다.
8. **라이브 수집에서 파일이 잠겨 있습니다.** 서비스가 파일을 연 채로 있어 보통 방식으로 읽으면 "다른 프로세스가 사용 중" 오류가 났습니다. 쓰기 공유(`FileShare.ReadWrite`)를 허용해 열면 읽혔습니다. (확인 범위: 조사 PC 시험) 라이브 수집은 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md)에서 다룹니다.
9. **방화벽 채널은 빨리 밀려납니다.** 최대 1MB 인데 스토어 앱 규칙이 자주 추가·삭제됩니다. 조사 PC 에는 약 18일만 남아 있었습니다.
10. **옛 번호로만 찾으면 놓칩니다.** 조사 PC(25H2)에는 2004·2005·2006 이 한 건도 없었습니다. 2097·2099·2052 도 함께 찾습니다.
11. **값이 표시 언어로 번역돼 남습니다.** 2082 의 Value 가 "예" 로 남았습니다. (확인 범위: 조사 PC 시험) 영어 "Yes" 만 검색하면 놓칩니다.
12. **숫자 칸의 뜻 표를 확인하지 못했습니다.** 규칙 ID 가 `...-Out-Block` 인 규칙의 2097 에서 `Direction=2`, `Action=2`, `Protocol=256`, `Profiles=2147483647` 이었습니다. (확인 범위: 조사 PC) 숫자마다 뜻은 자료로 확인하지 못했습니다. 메시지 문장과 함께 읽습니다.
13. **레지스트리를 직접 고친 경우는 확인하지 못했습니다.** 악성코드가 프로필 값을 바꾼다는 설명이 있습니다(ForensicArtifacts). 레지스트리 값을 직접 고쳐도 2082 가 남는지는 이번에 확인하지 못했습니다. 이벤트가 없다고 설정이 그대로였다고 보지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

`pfirewall.log` 의 머리글 끝과 첫 기록 사이를 봅니다. 아래는 조사 PC 시험에서 본 형식(ASCII, CRLF, NUL 212바이트)대로 만든 예시입니다. 첫 기록의 날짜 바이트는 예시 값입니다.

```
오프셋은 "#Fields:" 줄 끝 기준
00  70 61 74 68 20 70 69 64 0D 0A 00 00 00 00 00 00   path pid........
10  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ................
 …  (NUL 이 이어집니다)
    00 00 32 30 32 36 2D 30 39 2D 32 34 20 …           ..2026-09-24 …
```

1. `70 61 74 68 20 70 69 64` 는 `#Fields:` 줄의 마지막 두 칸 이름 `path pid` 입니다.
2. `0D 0A` 는 CRLF 줄바꿈입니다.
3. 그 뒤에 `00` 이 212바이트 이어집니다.
4. NUL 이 끝나면 첫 기록이 날짜 칸(`32 30 32 36 2D …` = `2026-…`)으로 시작합니다.

### 공개 도구로 한 번

`pfirewall.log` 를 파이썬으로 읽습니다. 칸 이름은 `#Fields:` 줄에서 가져옵니다.

```python
path = r"E:\case\pfirewall.log"   # 수집한 파일 경로로 바꿉니다
fields = []
with open(path, "rb") as f:
    for raw in f:
        line = raw.replace(b"\x00", b"").decode("ascii", "replace").strip()   # 첫 기록 앞 NUL 을 지웁니다
        if line.startswith("#Fields:"):
            fields = line[len("#Fields:"):].split()
        elif line and not line.startswith("#"):
            r = dict(zip(fields, line.split()))
            print(r["date"], r["time"], r["action"], r["protocol"],
                  r["src-ip"], r["src-port"], "->", r["dst-ip"], r["dst-port"], r["path"], "pid", r["pid"])
```

레지스트리에서 뽑은 규칙 문자열은 `|` 로 나눕니다. 칸 이름이 겹칠 경우를 생각해 사전 대신 목록으로 둡니다.

```python
rule = r"v2.33|Action=Allow|Active=FALSE|Dir=Out|Protocol=6|Profile=Public|RPort=2869|App=%SystemRoot%\system32\svchost.exe|Svc=fdphost|"
parts = rule.strip("|").split("|")
print("버전:", parts[0])
for k, v in (p.split("=", 1) for p in parts[1:]):
    print(f"  {k} = {v}")
```

규칙 이벤트는 PowerShell 로 뽑습니다. 아래는 2097 에서 규칙 이름·프로그램·바꾼 사용자를 뽑는 예입니다.

```powershell
$log = 'E:\case\Microsoft-Windows-Windows Firewall With Advanced Security%4Firewall.evtx'
Get-WinEvent -FilterHashtable @{ Path = $log; Id = 2097 } | ForEach-Object {
  $d = @{}
  ([xml]$_.ToXml()).Event.EventData.Data | ForEach-Object { $d[$_.Name] = $_.'#text' }
  [pscustomobject]@{
    UTC = $_.TimeCreated.ToUniversalTime(); RuleId = $d.RuleId; RuleName = $d.RuleName
    App = $d.ApplicationPath; User = $d.ModifyingUser; By = $d.ModifyingApplication
  }
} | Sort-Object UTC
```

2052·2099·2082 는 `Id` 를 바꿔 같은 방법으로 봅니다. 이 이벤트들의 데이터 칸 이름은 이번에 따로 확인하지 않았습니다. 칸이 비어 나오면 `Message` 를 함께 출력합니다.

살아 있는 PC 에서는 ForensicArtifacts 가 수집 대상으로 정의한 명령 두 개로 규칙 목록을 남깁니다.

```
netsh advfirewall firewall show rule name=all
netsh advfirewall monitor show firewall rule name=all
```

앞 명령은 모든 규칙을, 뒤 명령은 지금 켜진 규칙을 보여 줍니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| Sysmon 로그 | 프로세스와 묶인 네트워크 연결 기록 | [Sysmon 로그](../event-logs/sysmon/index.md) |
| SRUM | 앱별 네트워크 사용량 | [SRUM](../execution/system-resource-usage-monitor/index.md) |
| 프리페치 | `netsh` 로 로그를 켠 뒤 `NETSH.EXE` 항목이 생기거나 갱신됐습니다 (확인 범위: 조사 PC 시험) | [프리페치](../execution/prefetch/index.md) |
| PowerShell 명령 기록 | `netsh`·방화벽 설정 명령이 남았는지 | [PowerShell 명령 기록](../execution/consolehost-history-txt.md) |
| 사용자 계정 | 2097·2082 의 사용자 SID 가 어느 계정인지 | [사용자 계정](../system-account/sam.md), [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) |
| 시간대 설정 | `pfirewall.log` 현지 시각을 UTC 로 바꿀 때 | [시간대 설정](../system-account/time-zone.md) |
| 감사 정책과 로그 설정 | Security 로그의 방화벽 이벤트가 남을 수 있는 설정이었는지 | [감사 정책과 로그 설정](../event-logs/audit-policy-log-settings.md) |
| 이벤트 로그 삭제 | 방화벽 채널이나 Security 로그를 지운 기록 | [이벤트 로그 삭제](../event-logs/1102-104.md) |
| 섀도 복사본 | 예전 SYSTEM 하이브의 규칙·설정 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

방화벽 규칙을 고쳐 자리를 잡는 흔적은 [악성코드 지속성(자동실행) 찾기](../../04-scenarios/incident/persistence.md)와 [악성코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md)에서 함께 다룹니다. 받는 연결 기록은 [원격 데스크톱 침입 확인](../../04-scenarios/incident/rdp-intrusion.md)에서도 씁니다.

## 실습

공개 검체(NIST CFReDS 등) 가운데 윈도 10·11 이미지를 골라 아래 질문을 풀어 봅니다.

1. 세 프로필의 `EnableFirewall` 값은 각각 무엇입니까? 꺼진 프로필이 있습니까?
2. `FirewallRules` 의 값 가운데 이름이 `{GUID}` 이고 `Name` 이 평문인 규칙은 몇 개입니까? `App` 경로가 사용자 폴더 아래인 규칙이 있습니까?
3. `Query User` 규칙이 있습니까? 규칙이 가리키는 실행 파일은 무엇입니까?
4. 각 프로필의 `Logging` 값은 무엇입니까? 로그가 켜져 있었다면 `LogFilePath` 의 파일과 `.old` 파일이 있습니까?
5. `pfirewall.log` 에서 `DROP` 줄의 목적지 포트를 세어 봅니다. 가장 많은 포트는 무엇입니까? 시각을 UTC 로 바꾸면 언제입니까?
6. 방화벽 채널에서 2097·2052·2082 를 뽑습니다. `ModifyingUser` 가 서비스 SID 가 아닌 기록은 몇 건이고, 어느 프로그램으로 바꿨습니까?

## 참고 문헌

1. Microsoft Learn, "Configure Windows Firewall logging" (2025-04-07). https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/configure-logging
2. ForensicArtifacts/artifacts, artifacts/data/windows.yaml (main, 커밋 b4108448). https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/windows.yaml

이 페이지의 나머지 사실은 조사 PC 에서 직접 확인했습니다.
