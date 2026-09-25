---
title: "원격 명령 실행 이벤트"
parent: "아티팩트 · 이벤트 로그"
nav_order: 2630
---

# 원격 명령 실행 이벤트 (WinRM·WMI-Activity)

## 한 줄 요약

Windows 원격 관리 (WinRM, Windows Remote Management) 와 WMI (Windows Management Instrumentation) 는 다른 컴퓨터에 명령을 보내는 관리 통로입니다. 두 통로는 각자 Operational 로그를 씁니다. `Microsoft-Windows-WinRM/Operational` 에는 세션을 열고 셸과 명령을 만든 기록, 인증 실패가 남습니다. `Microsoft-Windows-WMI-Activity/Operational` 에는 WMI 공급자 시작과 실패한 WMI 호출이 남습니다. 두 로그 모두 작고 잡음이 많아서 빨리 밀려납니다.

## 무엇을 기록하나 · 왜 생기나

| 로그 | 남는 때 | 알려 주는 것 |
|---|---|---|
| WinRM/Operational | WSMan 세션·셸·명령을 만들고 닫을 때, 인증에 실패할 때, 서비스가 시작·멈출 때 | 연결 문자열, 리소스 URI, 셸 ID, 명령 ID, 인증 실패 내용, 가상 계정으로 실행한 사용자 |
| WMI-Activity/Operational | WMI 공급자가 시작할 때, WMI 호출이 실패할 때, 이벤트 구독이 동작할 때 | 공급자 이름과 호스트 프로세스, 호출한 사용자·컴퓨터·프로세스, 네임스페이스와 쿼리 원문 |

WinRM 은 지금 지원되는 모든 Windows 에 기본으로 설치돼 있지만, 서비스가 돌아도 리스너 (Listener) 가 없으면 요청을 주고받지 못하고 기본으로는 리스너가 없습니다. `winrm quickconfig` (`winrm qc`) 는 서비스를 자동 시작으로 바꾸고 시작한 뒤 HTTP 또는 HTTPS 리스너를 모든 IP 에 만들고 방화벽 예외를 엽니다.

WMI 는 Vista 부터 옛 로그 파일 대신 ETW 를 쓰므로 이벤트 뷰어나 `wevtutil` 로 봅니다.

원격 실행 도구가 도착 PC 에 남기는 흔적 전체는 [다른 PC 에서 원격 실행했나 (PsExec·WMI·WinRM)](../../04-scenarios/incident/credential-theft-lateral-movement/psexec-wmi-winrm.md)에서 다룹니다. 이 페이지는 두 로그와 설정 흔적만 다룹니다.

## 위치와 버전별 차이

### 로그와 공급자

| 항목 | WinRM | WMI-Activity |
|---|---|---|
| 공급자 | Microsoft-Windows-WinRM `{a7975c8f-ac13-49f1-87da-5a984a4ab417}` | Microsoft-Windows-WMI-Activity `{1418ef04-b0b4-4623-bf7e-d74ab47bbdaa}` |
| 메시지 파일 | `%windir%\system32\wsmres.dll` | `%SystemRoot%\system32\wbem\WinMgmtR.dll` |
| 파일 | `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-WinRM%4Operational.evtx` | `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-WMI-Activity%4Operational.evtx` |
| 채널 | Operational·Analytic·Debug | Operational·Trace |
| 켜짐 | 켜짐, 1MB, 순환 | 켜짐, 1MB, 순환 |



- Microsoft 의 WMI 추적 문서는 이벤트 원본을 "Microsoft-Windows-WMI" 라고 적습니다. 조사한 PC 의 공급자 이름은 Microsoft-Windows-WMI-Activity 였습니다.
- WMI-Activity 의 Trace 채널은 기본으로 꺼져 있습니다. `wevtutil sl Microsoft-Windows-WMI-Activity/Trace /e:true` 로 켭니다.
- Trace 채널의 Event 1·2·3 에는 GroupOperationID, OperationId, Operation, User, Namespace, ProviderName, Path 가 있다고 문서에 적혀 있습니다.
- 다른 채널의 크기와 켜짐은 [감사 정책과 로그 설정](audit-policy-log-settings.md)에서 다룹니다.

### WinRM 기본 동작과 버전

| 항목 | 내용 |
|---|---|
| 서비스 시작 | Windows Server 2008 이후 자동으로 시작합니다. 그 전 버전은 손으로 시작해야 합니다 |
| 기본 포트 (WinRM 2.0) | HTTP 5985, HTTPS 5986 |
| 기본 URL 접두사 | `wsman` |
| 인증 | 도메인 계정은 Kerberos, 로컬 계정은 NTLM 을 서버가 고릅니다. CredSSP 기본값은 False 입니다 |
| TrustedHosts | 클라이언트 쪽 목록입니다. 워크그룹이나 다른 도메인의 컴퓨터를 넣습니다. 목록 안의 컴퓨터는 인증하지 않습니다 |
| Winrs (원격 셸 명령) | AllowRemoteShellAccess 기본 True, 한 컴퓨터의 원격 셸 동시 사용자 기본 5명 |

### 레지스트리에 남는 WinRM 설정

조사한 PC 의 `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WSMAN` 입니다. (Windows 11 빌드 26200, 클라이언트 기준)

- 하위 키: AutoRestartList, CertMapping, Client, Listener, Plugin, SafeClientList, Service, WinRS
- `Listener\*+HTTP` 키에 Port 5985, uriprefix `wsman` 이 있었습니다.
- `Service` 키에 allow_remote_requests = 1 이 있었습니다.
- `Plugin` 아래에 Event Forwarding Plugin, Microsoft.PowerShell, Microsoft.PowerShell.Workflow, Microsoft.PowerShell32, WMI Provider 가 있었습니다.
- Microsoft.PowerShell 플러그인의 ConfigXML 에는 `Filename="%windir%\system32\pwrshplugin.dll"`, PSVersion 5.1 이 있었습니다.
- 그런데 WinRM 서비스는 수동·중지 상태였습니다. 리스너 키가 있다고 원격 요청을 받고 있었다고 볼 수는 없습니다.
- TrustedHosts 가 레지스트리 어디에 저장되는지는 확인하지 못했습니다. `WSMAN\Client` 키에는 값이 없었습니다.
- `C:\Windows\System32` 에 `wsmprovhost.exe`·`winrshost.exe` 가, `C:\Windows\System32\wbem` 에 `WmiPrvSE.exe` 가 있었습니다.

## 구조

### WinRM/Operational 이벤트

아래 메시지와 칸은 한 PC 의 공급자 메타데이터에서 읽었습니다. "보이는 쪽" 은 메시지 문구로 가른 해석입니다. 실제 원격 실행으로 확인하지 않았습니다.

| ID | 메시지 | 칸 | 보이는 쪽 |
|---|---|---|---|
| 6 | Creating WSMan Session. The connection string is: %1 | connection | 세션을 여는 쪽 |
| 8 · 31 · 33 | Closing WSMan Session / WSMan Create Session operation completed successfuly / Closing WSMan Session completed successfuly | — | 세션을 여는 쪽 |
| 11 | Creating WSMan shell with the ResourceUri: %1 and ShellId: %2 | resourceUri, shellId | 세션을 여는 쪽 |
| 13 · 15 · 16 | Running WSMan command with CommandId: %1 / Closing WSMan command / Closing WSMan shell | — | 세션을 여는 쪽 |
| 145 · 132 · 142 | WSMan operation %1 started with resourceUri %2 / completed successfully / failed, error code %2 | operationName, resourceUri, errorCode | 세션을 여는 쪽 |
| 91 | Creating WSMan shell on server with ResourceUri: %1 | resourceUri | 받는 쪽 |
| 193 | Request for user %1 (%2) will be executed using WinRM virtual account %3 (%4) | — | 받는 쪽 |
| 192 | The authorization of the user failed with error %1 | — | 받는 쪽 |
| 208 · 209 · 211 · 212 | 서비스 시작 중 / 시작됨 / 멈추는 중 / 멈춤 | — | 받는 쪽 |
| 161 | %1 | authFailureMessage | 인증 실패 |
| 162 | Authenticating the user failed. The credentials didn't work. | — | 인증 실패 |
| 163 | 지원하지 않는 인증 방식 | — | 인증 실패 |
| 164 | The destination computer (%1) returned an 'access denied' error. | destinationMachine | 인증 실패 |
| 44 | The WinRM protocol handler started to create a session at the following destination: %1. | destination | WMI 를 WinRM 으로 부를 때로 보임 |
| 47 | …operation of type %1 to the server. The operation accesses class %3 under the %2 namespace. | — | WMI 를 WinRM 으로 부를 때로 보임 |

이 공급자 메타데이터에는 80·81·82·143·166·168·169 정의가 없었고 Operational·Analytic·Debug 채널 모두 같았으며, 다른 자료가 적은 80·143·166 은 이 빌드에서 확인하지 못했습니다.

### WMI-Activity/Operational 이벤트

| ID | 메시지 | Level |
|---|---|---|
| 5857 | %1 provider started with result code %2. HostProcess = %3; ProcessID = %4; ProviderPath = %5 | 0 |
| 5858 | Id = %1; ClientMachine = %2; User = %3; ClientProcessId = %4; Component = %5; Operation = %6; ResultCode = %7; PossibleCause = %8 | Error |
| 5859 | Namespace = %1; NotificationQuery = %2; OwnerName = %3; HostProcessID = %4; Provider= %5, queryID = %6; PossibleCause = %7 | — |
| 5860 | Namespace = %1; NotificationQuery = %2; UserName = %3; ClientProcessID = %4, ClientMachine = %5; PossibleCause = %6 | — |
| 5861 | Namespace = %1; Eventfilter = %2 (refer to its activate eventid:5859); Consumer = %3; PossibleCause = %4 | — |



이 이벤트들의 값은 EventData 가 아니라 UserData 아래에 들어 있었습니다. 5857 은 `UserData\Operation_StartedOperational`, 5858 은 `UserData\Operation_ClientFailure` 요소였고 네임스페이스는 `http://manifests.microsoft.com/win/2006/windows/WMI` 였습니다.

- 5857 의 칸은 ProviderName, Code, HostProcess, ProcessID, ProviderPath 입니다.
- 5861 은 영구 이벤트 구독과 관련된 이벤트입니다. [WMI 영구 이벤트 구독](../persistence/wmi-event-subscription.md)에서 다룹니다.

조사한 PC 에서 본 값입니다. 컴퓨터 이름과 사용자는 가렸습니다.

| 이벤트 | 값 |
|---|---|
| 5857 | ProviderName CIMWin32, Code 0x0, HostProcess `wmiprvse.exe`, ProviderPath `%systemroot%\system32\wbem\cimwin32.dll`, Security UserID S-1-5-20 (NETWORK SERVICE), Level 0 |
| 5858 | ClientMachine [컴퓨터 이름], User [컴퓨터 이름]\[사용자], ClientProcessId, Operation `Start IWbemServices::ExecQuery - root\CIMV2 : SELECT * FROM Win32_ComputerSystem`, ResultCode 0x80041032, Security UserID S-1-5-18 |

5858 의 Operation 칸에는 네임스페이스와 WQL 쿼리 원문이 들어 있어서, 실패한 호출만이라도 누가 (User), 어느 컴퓨터에서 (ClientMachine), 어떤 프로세스로 (ClientProcessId), 무엇을 물었는지 볼 수 있습니다. 5858 이 실패한 작업만 남는지, 원격 호출일 때 ClientMachine 에 출발 PC 이름이 들어가는지는 확인하지 못했습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 기록 시각에 WSMan 세션·셸·명령을 만들었다는 것 (6·11·13·91) | 셸 안에서 어떤 명령을 실행했는지 (명령 내용은 WinRM 로그에 없습니다) |
| 받는 쪽에서 요청을 어느 사용자로, 어느 가상 계정으로 실행했는지 (193) | 그 계정 뒤에 있던 사람이 누구인지 |
| 인증 실패와 그 내용 (161·162·164, 192) | 인증 실패가 공격이었는지, 설정 실수였는지 |
| 실패한 WMI 호출의 사용자·컴퓨터·프로세스·쿼리 원문 (5858) | 성공한 WMI 호출 (Operational 에는 남지 않을 수 있습니다) |
| WMI 공급자가 어느 호스트 프로세스에서 시작했는지 (5857) | 그 공급자를 누가 불렀는지 |

### 보고서 문장

- 쓸 수 있는 문장: "WinRM/Operational 로그에 ○○(UTC) 의 91 이 있습니다. resourceUri 는 ○○ 입니다. 같은 분 안에 193 이 있고, 요청 사용자는 ○○\○○ 입니다."
- 쓰면 안 되는 문장: "공격자가 WinRM 으로 원격 명령을 실행했다."

두 번째 문장은 사람과 명령을 적지만, 이 로그에는 둘 다 없습니다. 명령 내용은 [PowerShell 실행 기록 (4103·4104)](powershell-event-logs-4103-4104.md)과 프로세스 생성 기록에서 따로 찾습니다.

## 시각 해석

- 세션을 여는 쪽과 받는 쪽의 기록은 서로 다른 PC 에 있으므로 두 PC 의 시계가 맞는지 먼저 확인합니다. 방법은 [시간대·시계 오차 보정](../../03-techniques/analysis/timeline/time-normalization.md)에서 다룹니다.
- 145 의 메시지는 작업 시작, 132·142 의 메시지는 작업 성공·실패입니다. 같은 operationName 의 145 와 132·142 사이를 작업 시간으로 볼 수 있습니다. 이 판단은 메시지에서 이끈 해석입니다.
- 두 로그는 1MB 라 덮는 기간이 짧습니다. 조사한 PC 에서 WinRM 로그 1,984건은 가장 오래된 기록이 약 40일 전이었습니다. WMI-Activity 로그는 약 하루 치만 있었습니다 (5858 1,080건, 5857 112건).
- 시각 값 저장 형식은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

## 함정과 한계

1. **WinRM 로그의 기록을 모두 원격 실행으로 읽습니다.** 조사한 PC 에서 254 (Activity Transfer)·161·142·145 가 각 약 496건 있었습니다. 모두 SYSTEM 권한 프로세스 하나가 로컬 리스너 설정 (`http://schemas.microsoft.com/wbem/wsman/1/config/listener`) 을 되풀이해 조회하다 실패한 기록이었습니다. 원격 실행과 상관없는 잡음입니다.
2. **보이는 쪽을 단정합니다.** 위 표의 "보이는 쪽" 은 메시지 문구로 가른 해석입니다. 실제 기록으로 확인한 뒤 보고서에 씁니다.
3. **다른 자료의 이벤트 ID 를 그대로 찾습니다.** 조사한 빌드에는 80·143·166 정의가 없었습니다. 검체의 Windows 버전에서 공급자 메타데이터를 확인합니다.
4. **오류 문장을 영어로 찾습니다.** 161 의 authFailureMessage 에는 한국어 오류 문장이 그대로 저장돼 있었습니다.
5. **오류 코드의 진법을 섞습니다.** 142 의 errorCode 는 10진수 (2150858770) 로 들어 있었습니다. 5858 의 ResultCode 는 16진 (0x80041032) 이었습니다. 같은 진법으로 바꾼 뒤 비교합니다.
6. **WMI 값을 EventData 에서 찾습니다.** WMI-Activity 이벤트는 UserData 아래에 있습니다. EventData 만 읽는 도구는 빈 값을 보여 줄 수 있습니다.
7. **리스너 키를 원격 허용의 증거로 씁니다.** 조사한 PC 에는 리스너 키와 allow_remote_requests = 1 이 있었지만 서비스는 수동·중지였습니다.

### 지우기와 조작

- **로그를 지웁니다.** 104 가 남습니다. [이벤트 로그 삭제 (1102·104)](1102-104.md)를 봅니다.
- **잡음에 묻힙니다.** 1MB 로그는 잡음만으로도 며칠~몇십 일 만에 밀려납니다. 원격 실행 기록이 이미 밀려났을 수 있습니다.
- **레코드 일부만 남습니다.** 밀려난 레코드가 파일 안에 남아 있을 수 있습니다. [파일 안에 남은 지운·손상 레코드](../../01-foundations/database-log-formats/evtx-evt-etl/chunk-slack-corrupted-evtx.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

142 의 errorCode 는 10진수로 보입니다. 오류 코드 표와 맞춰 보려면 16진으로 바꿉니다.

아래는 조사한 PC 에서 본 10진 값 2150858770 을 바꿔 본 예시입니다. 바이트는 32비트 값을 리틀 엔디언으로 적으면 이렇게 된다는 설명용입니다. 이벤트 레코드 안의 실제 저장 형식을 보여 주는 것이 아닙니다.

```
12 80 33 80
```

1. 2150858770 을 16진으로 바꾸면 0x80338012 입니다.
2. 리틀 엔디언 4바이트로 적으면 위와 같습니다.
3. 맨 앞자리가 8 이므로 부호 있는 32비트로 읽으면 음수가 됩니다. 도구에 따라 음수로 보일 수 있습니다.
4. 5858 의 ResultCode 처럼 `0x8…` 꼴로 맞춘 뒤 비교합니다.

밀려난 레코드를 파일 안에서 찾을 때는 칸 값의 글자를 UTF-16LE 로 바꿔 검색합니다. 아래는 `ExecQuery` 를 UTF-16LE 로 적은 예시입니다.

```
45 00 78 00 65 00 63 00 51 00 75 00 65 00 72 00 79 00
```

> 그림 자리: 5858 레코드의 UserData\Operation_ClientFailure 아래 칸들과 Operation 칸의 UTF-16LE 바이트를 나란히 놓은 그림

### 공개 도구로 한 번

Windows 에 들어 있는 명령으로 봅니다. 아래 `E:\case\` 는 예시 경로입니다.

```powershell
# WinRM 세션·셸·인증 실패
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\Microsoft-Windows-WinRM%4Operational.evtx'; Id = 6, 11, 91, 142, 161, 162, 164, 193 }

# WMI-Activity 5858: 값은 UserData 아래에 있습니다
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\Microsoft-Windows-WMI-Activity%4Operational.evtx'; Id = 5858 } |
  ForEach-Object { ([xml]$_.ToXml()).Event.UserData.Operation_ClientFailure } |
  Select-Object ClientMachine, User, ClientProcessId, Operation, ResultCode

# 라이브 시스템의 리스너 설정
winrm enumerate winrm/config/listener
```

이미지에서는 SOFTWARE 하이브 사본을 불러와 WSMAN 키를 읽습니다.

```powershell
reg load HKLM\CASE_SW E:\case\SOFTWARE
reg query "HKLM\CASE_SW\Microsoft\Windows\CurrentVersion\WSMAN" /s
reg unload HKLM\CASE_SW
```

도구가 UserData 아래 값을 제대로 보여 주는지 한두 개는 XML 원문과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [로그온 세션 잇기 (Logon ID·4624~4634·4647)](logon-events/logon-id-4624-4634-4647.md) | 받는 쪽 PC 의 로그온 유형 3 로그온과 시각 |
| [PowerShell 실행 기록 (4103·4104)](powershell-event-logs-4103-4104.md) | 원격 PowerShell 로 실행한 스크립트 내용 |
| [프로세스 생성 (4688)](4688.md) | 받는 쪽에서 뜬 프로세스. 4688 은 기본으로 꺼져 있습니다 |
| [WMI 영구 이벤트 구독](../persistence/wmi-event-subscription.md) | 5861 과 WMI 저장소의 구독 |
| [서비스 설치 (7045·4697)](7045-4697.md) | 같은 시각대에 서비스를 만든 원격 실행 |
| [다른 PC 에서 원격 실행했나 (PsExec·WMI·WinRM)](../../04-scenarios/incident/credential-theft-lateral-movement/psexec-wmi-winrm.md) | 출발 PC 와 도착 PC 기록을 합친 흐름 |

## 실습

**직접 만든 Windows 10·11 가상 머신 두 대**에서 해 봅니다. 관리자가 쓰는 평범한 원격 관리 작업만으로 충분합니다. 두 PC 의 시계를 맞추고 각 단계의 시각을 적어 둡니다.

1. 받을 쪽 가상 머신에서 `winrm quickconfig` 를 실행합니다. 서비스 상태, `WSMAN\Listener` 키, `winrm enumerate winrm/config/listener` 결과를 비교합니다.
2. 다른 가상 머신에서 원격 세션을 한 번 열고 `hostname` 같은 명령을 실행합니다. 두 PC 의 WinRM/Operational 에 어떤 ID 가 남는지 적습니다. 위 표의 "보이는 쪽" 해석이 맞는지 확인합니다.
3. 받는 쪽에서 원격 세션을 처리한 프로세스를 4688 로 확인합니다. `wsmprovhost.exe` 라는 설명이 있지만 이 페이지는 확인하지 못했습니다.
4. 틀린 비밀번호로 한 번 접속해 봅니다. 161·162·164 가운데 무엇이 남는지 봅니다.
5. 원격 WMI 로 성공하는 조회와 실패하는 조회를 한 번씩 합니다. 5858 이 실패한 것만 남는지, ClientMachine 에 어느 컴퓨터 이름이 들어가는지 봅니다.
6. WMI-Activity/Trace 채널을 켜고 5번을 되풀이합니다. Trace 의 Event 1·2·3 을 봅니다.

**NIST CFReDS 같은 공개 검체**에서는 다음을 풀어 봅니다.

1. WinRM/Operational 에 91·193 이 있습니까? 있다면 요청 사용자와 가상 계정은 무엇입니까?
2. 142·161 은 원격 실행과 관련 있습니까, 아니면 로컬 설정 조회의 잡음입니까? resourceUri 로 가릅니다.
3. WMI-Activity 의 5858 에서 Operation 칸의 쿼리 원문을 모두 뽑습니다. 어떤 클래스를 물었습니까?
4. 두 로그가 덮는 기간은 각각 언제부터 언제까지입니까?

## 참고 문헌

- Microsoft Learn, "Installation and configuration for Windows Remote Management" (2024-07-15) — https://learn.microsoft.com/en-us/windows/win32/winrm/installation-and-configuration-for-windows-remote-management
- Microsoft Learn, "Tracing WMI Activity" (2018-05-31) — https://learn.microsoft.com/en-us/windows/win32/wmisdk/tracing-wmi-activity
