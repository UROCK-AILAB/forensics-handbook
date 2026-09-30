---
title: "다른 PC 에서 원격 실행했나"
parent: "계정 탈취와 측면 이동"
grand_parent: "시나리오 · 침해 사고"
nav_order: 3750
---

# 다른 PC 에서 원격 실행했나 (PsExec·WMI·WinRM)

이 페이지는 손에 넣은 자격 증명으로 다른 PC 에서 명령을 실행했는지 확인하는 순서를 다룹니다. 원격 실행은 출발 PC 와 도착 PC 양쪽에 다른 흔적을 남깁니다. 그래서 이 페이지는 도구마다 두 쪽을 나눠 봅니다.

아래 이벤트 흔적 예시는 JPCERT/CC 도구 분석 시트의 시험 결과이고, 시험한 윈도 버전은 시트에 적혀 있지 않습니다[1][2][3].

## 조사 질문

- 이 PC 에서 다른 PC 로 원격 명령을 보냈습니까(출발)?
- 다른 PC 에서 이 PC 로 원격 명령이 들어왔습니까(도착)?
- 어느 도구(PsExec·WMI·WinRM)를 썼고, 어느 계정으로 어느 시각에 실행했습니까?
- 원격 실행에 쓴 자격 증명이 앞선 단계에서 빼낸 것과 이어집니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| 출발·도착 구분 | 흔적이 양쪽에 나뉩니다. 두 PC 의 로그를 모두 확보해야 한 번의 실행을 이어 봅니다. |
| 시간대 | 두 PC 의 시계 오차를 확인해 같은 기준으로 맞춥니다([시간대 설정](../../../02-artifacts/system-account/time-zone.md)). |
| 감사·Sysmon 설정 | 기본 설정에서도 남는 흔적과, 감사 정책·Sysmon 을 켜야 남는 흔적이 나뉩니다[1][2][3]. [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) 을 봅니다. |
| 로그 크기 | WMI-Activity·WinRM 운영 로그는 1MB 순환으로 설정돼 있을 수 있습니다(Windows 11 빌드 26200). 그러면 오래된 기록은 밀려나므로 분석 대상 PC 의 로그 크기를 확인합니다. |

WMI 명령줄 도구 (WMIC) 가 PC 에 있는지는 Windows 11 버전과 업데이트에 따라 다릅니다. 23H2·24H2 에서는 WMIC 가 기본으로 꺼져 있지만 선택적 기능 (Feature on Demand) 으로 추가할 수 있었고, 25H2 로 올리면 설치돼 있던 WMIC 가 지워지지만 다시 추가할 수 있었습니다[5]. 24H2·25H2 에서는 2026년 8월 미리 보기 업데이트부터 WMIC 가 빠집니다[5]. 26H1 에서도 빠졌고, 24H2 이상에서는 선택적 기능으로도 받을 수 없습니다[4][5]. 그래서 이 업데이트가 설치된 PC 에 wmic.exe 실행 흔적(프리페치·4688·Sysmon 1)이 있으면 그 파일이 어디서 왔는지 경로와 해시로 확인합니다. 마이크로소프트가 임시 조치로 내놓은 WMIC 패키지 (wmic_dlc.zip) 는 설치 스크립트가 WMIC 파일을 `C:\Windows\System32\wbem` 에 복사하므로[5], 이 경로에 있다고 해서 Windows 에 원래 있던 파일로 보지 않습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 서비스 설치 (System 7045·Security 4697) | PsExec 의 도착 PC 에 서비스가 설치됐나 | [서비스 설치](../../../02-artifacts/event-logs/7045-4697.md) |
| 2 | 공유 폴더 접근 (5140·5145) | ADMIN$·IPC$ 접근, 올린 파일 이름과 출발 PC 이름 | [공유 폴더 접근](../../../02-artifacts/event-logs/5140-5145.md) |
| 3 | 로그온 (4624·4634·4672) | 도착 PC 의 원격 로그온과 특수 권한 | [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) |
| 4 | 프로세스 생성 (4688·Sysmon 1) | 실행 프로세스의 명령줄과 부모 프로세스 | [프로세스 생성](../../../02-artifacts/event-logs/4688.md), [Sysmon 이벤트 1](../../../02-artifacts/event-logs/sysmon/1.md) |
| 5 | WMI-Activity·WinRM 운영 로그 | WMI·WinRM 공급자 시작과 세션 생성 | [원격 명령 실행 이벤트](../../../02-artifacts/event-logs/winrm-wmi-activity.md) |
| 6 | 실행 흔적 (프리페치·레지스트리) | 도구 실행 기록, EULA 동의 값 | [프리페치](../../../02-artifacts/execution/prefetch/index.md) |
| 7 | 네트워크 연결 (Sysmon 3) | 도착 포트 135·445·5985 로의 연결 | [네트워크 연결·DNS 질의](../../../02-artifacts/event-logs/sysmon/3-22.md) |

## PsExec

### 출발 PC

- 기본 설정에서 남는 것은 EULA 동의 레지스트리 값과 프리페치입니다[1].
- EULA 동의 값: `HKEY_USERS\[User SID]\SOFTWARE\Sysinternals\PsExec\EulaAccepted` = DWORD 0x00000001[1].
- 프리페치: `C:\Windows\Prefetch\[실행 파일 이름]-[무작위].pf`[1].
- 감사 정책·Sysmon 을 켜면 Security 4688·4689·5156, Sysmon 1(명령줄)·3(네트워크)·12·13(EULA 레지스트리)이 남습니다[1].
- 도착 포트는 135, 445, 그리고 무작위 높은 포트입니다[1].

### 도착 PC

- 기본 설정에서 남는 것은 PSEXESVC 서비스가 설치·시작·종료된 사실과 프리페치입니다[1].
- System 7045: Service Name PSEXESVC, Service File Name `%SystemRoot%\PSEXESVC.exe`, 계정 LocalSystem, demand start[1].
- System 7036: PSEXESVC 가 Running·Stopped 로 바뀝니다[1].
- Security 5140: Share Name `\\*\ADMIN$`, `\\*\IPC$`[1].
- Security 5145: Share Path `\??\C:\Windows`, Relative Target Name `PSEXESVC.exe` 와 `PSEXESVC-[출발 PC 이름]-[출발 프로세스 ID]-stdin/stdout/stderr`[1].
- 5145 의 Relative Target Name 에 출발 PC 이름이 들어가므로[1] 출발 PC 를 찾는 단서가 됩니다.
- Security 4624: 로그온 유형 3(Network), 인증 패키지 NTLM, 로그온 프로세스 NtLmSsp(시트 예시)[1].
- Security 4672: SeSecurityPrivilege·SeBackupPrivilege·SeRestorePrivilege 같은 특수 권한이 붙습니다[1].
- Security 4688: 부모가 `services.exe`, 사용자가 SYSTEM 입니다[1].
- 레지스트리 `SYSTEM\ControlSet001\services\PSEXESVC`: Type 0x10, Start 0x3 → 0x4 로 바뀜, ImagePath `%SystemRoot%\PSEXESVC.exe`, ObjectName LocalSystem, DeleteFlag 1[1].
- 프리페치: `C:\Windows\Prefetch\PSEXESVC.EXE-[무작위].pf`[1].
- USN 저널: PSEXESVC.exe 의 생성과 종료·삭제, 프리페치 파일의 생성 기록[1].

### 읽을 때 주의

- 5145·4674 는 기본 설정이 아닌 추가 감사 정책이 있어야 남습니다[1].
- 쓴 뒤에 PSEXESVC.exe 는 지워집니다(4660·USN 삭제)[1]. 그래서 파일 자체보다 7045·프리페치·USN 을 봅니다.
- 같은 시트 안에서 프리페치 이름을 한 곳은 `PSEXESVC.EXE-*.pf` 로, 다른 곳은 `PSEXECSVC.EXE-*.pf` 로 적어 서로 다릅니다[1]. 이름 철자에 기대지 말고 7045·USN 과 맞춰 봅니다.

## WMI (wmic)

### 출발 PC

- Sysmon 1 의 명령줄 예: `wmic /NODE:"[대상]" [프로세스]`[2].
- Sysmon 3: svchost.exe 를 거쳐 도착 포트 135 로 연결[2].
- 프리페치: `C:\Windows\Prefetch\WMIC.EXE-[무작위].pf`[2].
- Sysmon 12: `\REGISTRY\MACHINE\SOFTWARE\Microsoft\Wbem\CIMOM` 키 생성[2].

### 도착 PC

- Security 4624: 로그온 유형 3, 출발 PC 에서 Kerberos 로 인증(시트 예시)[2].
- 실행 프로세스: `WmiPrvSE.exe -secured -Embedding`, 부모 `svchost.exe -k DcomLaunch`(Sysmon 1·Security 4688)[2].
- Sysmon 10: WmiPrvSE.exe 가 lsass.exe·services.exe·csrss.exe 에 접근[2]. 정상 원격 wmic 실행에서도 남습니다. 그래서 이 접근만으로 덤프라고 보지 않습니다. [자격 증명을 빼냈나](credential-dumping.md) 를 봅니다.
- Security 4673: SeTcbPrivilege 사용[2].
- 필요한 감사 정책: 프로세스 생성은 "Audit Process Creation", 권한 사용은 "Audit Sensitive Privilege Use", 필터링 플랫폼 연결은 "Audit Filtering Platform Connection" 입니다[2]. 레지스트리 추적은 Sysmon 이 있어야 합니다[2].

### WMI-Activity 운영 로그

- 로그: `Microsoft-Windows-WMI-Activity/Operational`. 1MB 순환이면 오래된 기록은 밀려납니다.
- 5857: 공급자 시작. 필드는 ProviderName, Code, HostProcess, ProcessID, ProviderPath 입니다.
- 5858: 필드는 Id, ClientMachine, User, ClientProcessId, Component, Operation, ResultCode, PossibleCause 입니다.
- WinRM 으로 명령을 받은 도착 PC 에도 WMI-Activity 5857 이 남습니다[3].
- 5861 은 영구 이벤트 구독 쪽입니다. [WMI 영구 이벤트 구독](../../../02-artifacts/persistence/wmi-event-subscription.md) 을 봅니다.

## WinRM

JPCERT 시트의 예시 명령은 원격 명령 실행이 아니라 설정 조회입니다[3]. 그래서 아래 흔적은 그 예시가 남긴 것입니다. 실제 원격 명령 실행에서는 도착 프로세스가 다를 수 있습니다.

### 출발 PC

- Microsoft-Windows-WinRM/Operational 80·143·166·132, 프리페치 `CSCRIPT.EXE-*.pf`, 레지스트리 `\REGISTRY\MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\WSMAN\Client`[3].
- 포트: 5985/tcp(HTTP), 5986/tcp(HTTPS). 예시 인증은 Kerberos 입니다[3].

### 도착 PC

- 4624 유형 3·4634·4672[3].
- 실행 프로세스: `C:\Windows\System32\wbem\wmiprvse.exe -secured -Embedding`, 사용자 NT AUTHORITY\NETWORK SERVICE, 부모 `svchost.exe -k DcomLaunch`[3].
- 프리페치 `WMIPRVSE.EXE-*.pf`, WMI-Activity 5857[3].
- 레지스트리: `HKLM\SOFTWARE\Microsoft\Wbem`, `HKLM\SOFTWARE\Microsoft\Reliability Analysis\RAC\WmiLastTime`, wsmsvc.dll 을 가리키는 MuiCache 항목[3].

### WinRM 운영 로그

- 로그: `Microsoft-Windows-WinRM/Operational`. 1MB 순환이면 오래된 기록은 밀려납니다.
- 6 "Creating WSMan Session. The connection string is: %1".
- 91 "Creating WSMan shell on server with ResourceUri: %1".
- 162 "Authenticating the user failed. The credentials didn't work.".
- 메시지 문구로 보면 6 은 세션을 여는 쪽(클라이언트), 91 은 서버 쪽 셸 생성입니다. 출발·도착 어느 쪽에 남는지는 실제 기기에서 측정해 확인해야 합니다.
- PowerShell 원격 명령의 내용은 PowerShell 로그(4103·4104)로 넘깁니다: [PowerShell 실행 기록](../../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md).

## 서비스 설치 이벤트 (7045·4697)

PsExec 처럼 도착 PC 에 서비스를 설치하는 도구는 서비스 설치 이벤트를 남깁니다.

- System 7045(공급자 Service Control Manager): 필드는 ServiceName, ImagePath, ServiceType, StartType, AccountName 입니다.
- 7045 의 공급자 원시 ID 는 1073748869(0x40001B85)입니다. 도구에 따라 7045 가 아니라 이 값으로 보일 수 있습니다.
- Security 4697 은 누가 설치했는지(Subject)를 함께 남깁니다. 두 이벤트 템플릿을 비교하면 7045 에는 그 필드가 없습니다.
- 두 이벤트의 필드와 차이는 [서비스 설치](../../../02-artifacts/event-logs/7045-4697.md) 에서 다룹니다.

## 공통 판단

- PsExec·wmic·WinRM 모두 도착 PC 에 로그온 유형 3 을 남겼습니다[1][2][3]. 유형 3 은 파일 공유 접근 같은 흔한 일에도 생깁니다. 그래서 같은 Logon ID·같은 시각대의 서비스 설치·프로세스 생성과 이어서 봅니다.
- 인증 패키지가 PsExec 예시에서는 NTLM, wmic·WinRM 예시에서는 Kerberos 였습니다[1][2][3]. 인증 패키지 하나로 도구를 가를 수 없습니다.
- 로그온 유형·세션 잇기는 [로그온 유형 해석](../../../02-artifacts/event-logs/logon-events/logon-type.md) 과 [로그온 세션 잇기](../../../02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md) 에서 다룹니다.

## 분석 흐름

1. 두 PC 의 시계 오차를 확인해 같은 기준으로 맞춥니다.
2. 도착 PC 에서 로그온 유형 3 의 4624 를 시각순으로 모읍니다. Logon ID·계정·원본 주소를 적습니다.
3. 각 4624 의 Logon ID·시각과 이어지는 서비스 설치(7045·4697), 공유 접근(5140·5145), 프로세스 생성(4688·Sysmon 1)을 묶습니다.
4. 묶음의 실행 프로세스로 도구를 구분합니다. PSEXESVC 서비스는 PsExec 입니다[1]. wmic 와 JPCERT 의 WinRM 예시는 모두 도착 PC 에 WmiPrvSE.exe 를 남겼습니다[2][3]. 그래서 WmiPrvSE.exe 하나로 WMI 와 WinRM 을 가르지 않고, WinRM 운영 로그와 출발 PC 기록을 함께 봅니다. PowerShell 원격의 도착 프로세스는 실제 기기에서 확인해야 합니다.
5. 5145 의 Relative Target Name 이나 명령줄에서 출발 PC 이름을 꺼냅니다.
6. 출발 PC 를 특정하면 그 PC 의 프리페치·EULA 값·Sysmon 3·WinRM 클라이언트 로그로 출발 쪽을 맞춰 봅니다.
7. 원격 실행에 쓴 계정이 앞선 [자격 증명을 빼냈나](credential-dumping.md) 단계와 이어지는지 봅니다.
8. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **로그온 유형 3 하나로 원격 실행이라고 봅니다.** 유형 3 은 파일 공유 접근에도 생깁니다. 같은 Logon ID 의 서비스 설치·프로세스 생성과 이어서 봅니다.
2. **한쪽 PC 로그만 봅니다.** 흔적이 출발·도착에 나뉘어 있어 한쪽만 보면 반쪽 그림이 됩니다.
3. **PSEXESVC 파일이 없으니 PsExec 을 안 썼다고 봅니다.** 이 파일은 쓴 뒤 지워집니다[1]. 7045·프리페치·USN 을 봅니다.
4. **인증 패키지로 도구를 가릅니다.** NTLM·Kerberos 는 도구가 아니라 인증 방식에 따라 달라집니다[1][2][3].
5. **로그에 없으니 원격 실행도 없었다고 봅니다.** WMI-Activity·WinRM 운영 로그는 1MB 순환일 수 있어 오래된 기록이 밀려납니다.
6. **WMI-Activity 5861 을 원격 실행으로 봅니다.** 5861 은 영구 이벤트 구독 쪽입니다. [WMI 영구 이벤트 구독](../../../02-artifacts/persistence/wmi-event-subscription.md) 을 봅니다.
7. **wmic.exe 흔적이 없으니 WMI 를 쓰지 않았다고 봅니다.** WMIC 가 빠진 PC 에서도 WMI 자체는 계속 지원되고, Get-CimInstance·Invoke-CimMethod 같은 PowerShell cmdlet 으로 WMI 를 쓸 수 있습니다[5]. 도착 PC 의 WMI-Activity 운영 로그와 [PowerShell 실행 기록](../../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md) 을 함께 봅니다.

## 보고서 문장 예

아래 값은 설명을 위해 만든 예입니다.

- 쓰지 않을 문장: "공격자가 PsExec 으로 이 서버를 장악했습니다."
- 쓸 문장: "이 PC 의 System 로그에는 ○○(UTC)에 Service Name PSEXESVC, Service File Name `%SystemRoot%\PSEXESVC.exe` 인 7045 가 있습니다. 같은 시각대의 5145 Relative Target Name 에 출발 PC 이름 ○○이 있습니다. 같은 Logon ID 의 4624 는 로그온 유형 3, 계정 ○○, 원본 주소 ○○입니다. 이 기록은 출발 PC ○○에서 계정 ○○으로 이 PC 에 서비스가 설치·실행됐음을 보여 줍니다. 실행된 명령의 내용은 명령줄 기록이 없어 이 로그만으로는 정할 수 없습니다."

## 함께 볼 페이지

- [서비스 설치 (7045·4697)](../../../02-artifacts/event-logs/7045-4697.md) · [공유 폴더 접근 (5140·5145)](../../../02-artifacts/event-logs/5140-5145.md) — 도착 PC 의 서비스·공유 흔적입니다.
- [원격 명령 실행 이벤트 (WinRM·WMI-Activity)](../../../02-artifacts/event-logs/winrm-wmi-activity.md) · [PowerShell 실행 기록](../../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md) — WMI·WinRM·PowerShell 원격의 로그입니다.
- [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) · [로그온 유형 해석](../../../02-artifacts/event-logs/logon-events/logon-type.md) · [로그온 세션 잇기](../../../02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md) · [명시적 자격 증명·특수 권한 (4648·4672)](../../../02-artifacts/event-logs/logon-events/4648-4672.md) — 도착 PC 의 로그온과 권한입니다.
- [프로세스 생성 (4688)](../../../02-artifacts/event-logs/4688.md) · [Sysmon 이벤트 1](../../../02-artifacts/event-logs/sysmon/1.md) · [네트워크 연결 (Sysmon 3·22)](../../../02-artifacts/event-logs/sysmon/3-22.md) — 실행 프로세스와 연결입니다.
- [프리페치](../../../02-artifacts/execution/prefetch/index.md) · [공유 폴더·네트워크 드라이브](../../../02-artifacts/network/network-shares-mapped-drives.md) — 실행과 공유 흔적입니다.
- [예약 작업 이벤트 (4698)](../../../02-artifacts/event-logs/taskscheduler-4698.md) · [WMI 영구 이벤트 구독](../../../02-artifacts/persistence/wmi-event-subscription.md) — 원격 실행에 자주 쓰이는 다른 수단입니다.
- [자격 증명을 빼냈나](credential-dumping.md) · [새 계정을 만들거나 권한을 올렸나](account-privilege.md) — 앞뒤 단계입니다.

## 참고 문헌

1. JPCERT/CC, Tool Analysis Result Sheet — PsExec — https://jpcertcc.github.io/ToolAnalysisResultSheet/details/PsExec.htm
2. JPCERT/CC, Tool Analysis Result Sheet — wmic — https://jpcertcc.github.io/ToolAnalysisResultSheet/details/wmic.htm
3. JPCERT/CC, Tool Analysis Result Sheet — WinRM — https://jpcertcc.github.io/ToolAnalysisResultSheet/details/WinRM.htm
4. Microsoft Learn, What's new in Windows 11, version 26H2 for IT pros — Features removed in Windows 11, version 26H2 — https://learn.microsoft.com/en-us/windows/whats-new/whats-new-windows-11-version-26h2
5. Microsoft Support, Windows Management Instrumentation Command-line (WMIC) removal from Windows — https://support.microsoft.com/servicing/os/windows/docs/2025/09/windows-management-instrumentation-command-line-wmic-removal-from-windows
