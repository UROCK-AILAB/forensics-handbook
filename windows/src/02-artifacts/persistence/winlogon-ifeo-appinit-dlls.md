# 기타 자동실행 위치 (Winlogon·IFEO·AppInit_DLLs)

## 한 줄 요약

Run 키 말고도 로그온, 프로그램 시작, DLL 로드에 끼어드는 레지스트리 자리가 있습니다. 이 페이지는 Winlogon 의 Shell·Userinit·Notify, IFEO 의 Debugger, AppInit_DLLs, 그리고 BootExecute·Load 값을 다룹니다. 이 자리들은 정상 값이 정해져 있거나 대개 비어 있어서, 기준과 다른 값이 보이면 살펴볼 대상입니다.

## 무엇을 기록하나 · 왜 생기나

### Winlogon

- `Winlogon\Userinit` 는 사용자가 로그온할 때 실행되는 사용자 초기화 프로그램 userinit.exe 를 가리킵니다.
- `Winlogon\Shell` 은 사용자가 로그온할 때 실행되는 시스템 셸 explorer.exe 를 가리킵니다.
- `Winlogon\Notify` 는 Winlogon 이벤트를 처리하는 알림 패키지 DLL 을 가리킵니다.
- MITRE ATT&CK 는 이 자리를 쓰는 수법을 T1547.004(Winlogon Helper DLL) 로 분류합니다.

### IFEO (Image File Execution Options)

이미지 파일 실행 옵션 (Image File Execution Options, IFEO) 키 아래에는 실행 파일 이름마다 하위 키를 둘 수 있습니다. 하위 키에 `Debugger` 값을 넣으면 그 프로그램이 만들어질 때 지정한 디버거가 대신 실행되고, 대상 프로그램은 디버거의 인자로 넘어갑니다. MITRE ATT&CK 는 이 자리를 쓰는 수법을 T1546.012(Image File Execution Options Injection) 로 분류합니다.

MITRE 는 조용한 프로세스 종료 (silent process exit) 감시도 같은 수법으로 적습니다. 관련 값은 `SilentProcessExit` 키 아래 `ReportingMode`·`MonitorProcess` 값과, IFEO 하위 키의 `GlobalFlag` 에 켠 플래그 512(0x200, FLG_MONITOR_SILENT_PROCESS_EXIT) 이고, 레지스트리를 직접 고치거나 GFlags(gflags.exe) 로 설정합니다.

### AppInit_DLLs

AppInit_DLLs 는 사용자가 지정한 DLL 을 모든 대화형 응용 프로그램의 주소 공간에 올리게 하는 장치입니다. 정상 앱은 거의 쓰지 않지만 많은 악성코드가 API 를 가로채는 데 씁니다. Microsoft 는 이 장치를 쓰지 말라고 권하고, Windows 8 데스크톱 앱 인증 요건은 AppInit_DLLs 로 임의 DLL 을 올려 Win32 API 를 가로채는 것을 금지합니다.

### BootExecute·Load

- MITRE ATT&CK 는 T1547.001 에서 이 두 값도 자동실행 자리로 적습니다.
- `BootExecute` 는 `HKLM\System\CurrentControlSet\Control\Session Manager` 의 값입니다. 기본값은 `autocheck autochk *` 입니다.
- `Load` 는 `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows` 의 값입니다.

## 위치와 버전별 차이

| 무엇 | 경로 | 출처 |
|---|---|---|
| Winlogon (컴퓨터) | `HKLM\Software[\Wow6432Node]\Microsoft\Windows NT\CurrentVersion\Winlogon\` | MITRE T1547.004 |
| Winlogon (사용자) | `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\` | MITRE T1547.004 |
| IFEO | `HKLM\SOFTWARE\{Wow6432Node}\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<실행 파일 이름>` | MITRE T1546.012 |
| 조용한 종료 감시 | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SilentProcessExit\<실행 파일 이름>` | MITRE T1546.012, Microsoft 디버거 문서 |
| AppInit_DLLs | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows` (`AppInit_DLLs`·`LoadAppInit_DLLs`) | Win11 25H2 PC 한 대에서 확인 |
| AppInit_DLLs (32비트) | `HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows NT\CurrentVersion\Windows` | Win11 25H2 PC 한 대에서 확인 |
| BootExecute | `HKLM\System\CurrentControlSet\Control\Session Manager` | MITRE T1547.001 |
| Load | `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows` | MITRE T1547.001 |

- AppInit_DLLs 의 Microsoft 문서에는 레지스트리 경로가 적혀 있지 않습니다. 표의 경로는 PC 한 대에서 본 것입니다.
- MITRE 페이지는 Notify 가 어느 Windows 버전에서 없어졌는지 적지 않습니다.

### AppInit_DLLs 의 버전별 차이

| Windows | 동작 |
|---|---|
| Windows 7·Server 2008 R2 | 별도 백서에 동작이 정리되어 있다고만 Microsoft 문서가 적습니다 |
| Windows 8 이후, Secure Boot 켜짐 | AppInit_DLLs 기능이 꺼집니다 |

서명을 요구하는 설정(`RequireSignedAppInit_DLLs`)이 Windows 7 에서 생겼다는 설명은 이번에 연 자료로 확인하지 못했습니다.

## 구조

### Winlogon 값

Windows 11 PC 한 대에서 본 값은 아래와 같습니다. (확인 범위: Win11 25H2 한 대)

| 키 | 값 |
|---|---|
| HKLM ...\Winlogon | `Userinit` = `C:\Windows\system32\userinit.exe,` (끝에 쉼표가 붙어 있었습니다), `Shell` = `explorer.exe`, `AutoAdminLogon` = `0`, `VMApplet` = `SystemPropertiesPerformance.exe /pagefile` |
| HKLM ...\WOW6432Node\...\Winlogon | `Shell` = `explorer.exe`, `Userinit` 없음 |
| HKCU ...\Winlogon | `Shell`·`Userinit` 값 없음 |

- 같은 PC 에는 `Winlogon\Notify` 키가 없었습니다.
- 하위 키로는 `AlternateShells`, `GPExtensions`(27개), `ShellPrograms`, `UserDefaults`, `AutoLogonChecked`, `VolatileUserMgrKey` 가 있었습니다.
- Winlogon 키에는 `DefaultUserName`·`LastUsedUsername` 같은 계정 이름 값도 있었습니다.
- `Userinit` 에 쉼표로 여러 프로그램을 이어 붙일 수 있다는 설명이 있지만, 이번에 연 자료로는 확인하지 못했습니다. 끝 쉼표가 왜 붙는지도 확인하지 못했습니다.

### IFEO 하위 키

Windows 11 PC 한 대에서 본 모습입니다. (확인 범위: Win11 25H2 한 대)

- IFEO 하위 키가 59개 있었습니다.
- `Debugger` 값이 있는 키는 0개였습니다.
- `GlobalFlag` 값이 있는 키도 0개였습니다. 전역 플래그는 IFEO 하위 키의 `GlobalFlag` 값에 들어갑니다(Microsoft 디버거 문서).
- 하위 키에 흔히 있는 값은 `MitigationOptions`(47개 키), `ImageExpansionMitigation`(5), `DisableExceptionChainValidation`(3), `CFGOptions`(2) 등이었습니다.
- 즉 IFEO 하위 키가 있다는 것만으로는 이상하지 않습니다. `Debugger` 나 전역 플래그 같은 값을 봐야 합니다.
- WOW6432Node 쪽 IFEO 도 하위 키가 59개로 같았습니다. 두 경로가 같은 키를 공유하는지는 확인하지 못했습니다.
- `SilentProcessExit` 키는 없었습니다.

`SilentProcessExit` 의 동작은 Microsoft 디버거 문서에 있습니다.

Windows 7 부터 쓸 수 있고, 감시 대상은 IFEO 하위 키 `GlobalFlag` 에 0x200 이 켜진 프로그램입니다. 대상이 ExitProcess 로 스스로 끝나거나 다른 프로세스가 TerminateProcess 로 끝낼 때만 반응하며, 마지막 스레드가 끝나는 보통 종료에는 반응하지 않습니다.

프로그램별 설정은 `SilentProcessExit\<실행 파일 이름>` 키에 있습니다. `ReportingMode` 에 0x1 비트가 켜져 있으면 `MonitorProcess` 에 적힌 명령줄을 실행하고, 0x2 는 덤프 생성, 0x4 는 팝업 알림입니다. 감시 대상이 이렇게 끝나면 Application 로그에 원본 "Process Exit Monitor" 항목이 남습니다. 그래서 이 키가 있고 `MonitorProcess` 에 프로그램 경로가 있으면 살펴볼 대상으로 둡니다.

### AppInit_DLLs 값

Windows 11 PC 한 대에서 본 값입니다. 이 PC 는 Secure Boot 가 켜져 있었습니다. (확인 범위: Win11 25H2 한 대)

| 키 | `AppInit_DLLs` | `LoadAppInit_DLLs` | `RequireSignedAppInit_DLLs` |
|---|---|---|---|
| HKLM ...\Windows | 빈 문자열 (REG_SZ) | 0 (REG_DWORD) | 없음 |
| HKLM\SOFTWARE\WOW6432Node\...\Windows | 빈 문자열 | 0 | 없음 |

- User32.dll 을 올리는 프로세스만 해당된다는 설명, `LoadAppInit_DLLs`=1 이어야 동작한다는 설명, DLL 목록의 구분자가 무엇인지는 이번에 연 자료로 확인하지 못했습니다.

### BootExecute·Load 값

- Windows 11 PC 한 대에서 `BootExecute` 는 `autocheck autochk *` 였습니다. (확인 범위: Win11 25H2 한 대)
- 같은 PC 의 `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows` 에는 `Load` 값도 `Run` 값도 없었습니다. (확인 범위: Win11 25H2 한 대)

## 증거로서 의미

### 증명하는 것

- 수집 시점에 이 자리에 이 값이 설정되어 있었습니다.
- `Shell`·`Userinit` 이 explorer.exe·userinit.exe 말고 다른 프로그램을 가리키면, 로그온 때 그 프로그램이 실행되도록 설정되어 있었습니다.
- IFEO 하위 키에 `Debugger` 가 있으면, 그 이름의 프로그램이 시작될 때 지정한 프로그램이 대신 실행되도록 설정되어 있었습니다.
- `BootExecute` 가 기본값과 다르면 그 설정이 바뀌어 있었습니다.

### 증명하지 못하는 것

- **실행됐나.** 설정만 알려 줍니다. 실행은 [프로세스 생성](../event-logs/4688.md) 이나 [Sysmon 이벤트 1](../event-logs/sysmon/1.md) 에서 따로 봅니다.
- **AppInit DLL 이 올라갔나.** Secure Boot 가 켜진 Windows 8 이후 PC 에서는 AppInit_DLLs 에 값이 있어도 기능이 꺼져 있습니다. 그래서 값이 있다는 것은 "시도" 의 흔적이지 "실행" 의 증거가 아닙니다. 이 문장은 Microsoft 문서에서 끌어낸 해석입니다. 조사 대상 PC 의 Secure Boot 상태를 따로 확인해야 합니다.
- **언제 설정했나.** 값에는 시각이 없습니다. 아래 "시각 해석" 을 봅니다.
- **누가 설정했나.** 값에는 설정한 프로세스를 적는 칸이 없습니다.

보고서에는 "수집 시점에 IFEO 의 이 실행 파일 이름 키에 `Debugger` 값이 이 경로로 설정되어 있다" 처럼 씁니다.

## 시각 해석

- 이 자리의 값에는 값마다 붙은 시각이 없습니다. 키 단위 시각은 [키 마지막 기록 시각](../../01-foundations/database-log-formats/registry-hive/last-write-time.md) 에서 다룹니다.
- Winlogon 키에는 값이 많습니다. 키 시각이 바뀌었어도 `Shell`·`Userinit` 이 바뀌었다는 뜻은 아닙니다.
- IFEO 는 실행 파일 이름마다 하위 키가 따로 있습니다. `Debugger` 가 있는 하위 키의 시각은 그 키 안의 변경만 가리킵니다. 이 문장은 키 단위 시각의 성질에서 끌어낸 해석입니다.
- 설정한 순간을 잡으려면 [Sysmon 레지스트리 이벤트](../event-logs/sysmon/12-13-14.md) 가 켜져 있었는지 봅니다.

## 함정과 한계

- **WOW6432Node 를 빼먹습니다.** Winlogon·IFEO·AppInit_DLLs 모두 WOW6432Node 쪽 경로가 따로 있습니다.
- **HKCU 쪽 Winlogon 도 봅니다.** MITRE 는 HKCU 경로도 적습니다. 사용자 하이브마다 확인합니다.
- **`Userinit` 끝의 쉼표를 이상 신호로 보지 않습니다.** Windows 11 PC 한 대의 정상 값에도 쉼표가 붙어 있었습니다. 쉼표 뒤에 다른 경로가 이어지는지를 봅니다. (확인 범위: Win11 25H2 한 대)
- **IFEO 하위 키는 원래 많습니다.** 보안 완화 설정이 흔합니다. `Debugger`·전역 플래그 값을 봅니다.
- **보안 제품 이름의 IFEO 키를 먼저 봅니다.** MITRE 는 IFEO 경로 아래 변경, 특히 보안 제품 실행 파일을 대상으로 한 변경을 보라고 권합니다.
- **AppInit_DLLs 의 뜻은 Secure Boot 상태에 따라 갈립니다.** 값만 보고 DLL 이 올라갔다고 쓰지 않습니다.
- **Winlogon 에는 계정 이름 값이 있습니다.** 보고서에 옮길 때 필요한 범위만 적습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 값 형식에 맞춰 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다.

**`Userinit` 값 데이터의 끝부분 (`userinit.exe,`).**

```
75 00 73 00 65 00 72 00 69 00 6E 00 69 00 74 00   u.s.e.r.i.n.i.t.
2E 00 65 00 78 00 65 00 2C 00                     ..e.x.e.,.
```

1. REG_SZ 문자열은 UTF-16LE 입니다. 한 글자가 2바이트입니다.
2. 마지막 `2C 00` 이 쉼표입니다.
3. 쉼표 뒤에 글자 바이트가 더 이어지면 다른 경로가 붙어 있다는 뜻입니다. 그 경로를 끝까지 읽습니다.

**`LoadAppInit_DLLs` 값 (REG_DWORD).**

```
00 00 00 00
```

4바이트를 리틀 엔디언으로 읽으면 0 입니다. 도구가 DWORD 를 문자열로 보여 줄 때는 원시 바이트로 한 번 확인합니다.

### 공개 도구로 한 번

1. HKLM 쪽 하이브와 사용자마다의 사용자 하이브를 하이브 로그와 함께 사본으로 뜹니다. 하이브 파일 종류는 [하이브 파일 종류](../../01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md) 에서 다룹니다.
2. 레지스트리 뷰어로 위 표의 경로를 WOW6432Node 쪽까지 차례로 엽니다.
3. Winlogon 의 `Shell`·`Userinit`, IFEO 하위 키의 `Debugger`·전역 플래그, `AppInit_DLLs`·`LoadAppInit_DLLs`, `BootExecute`, `Load` 를 한 표로 모읍니다.
4. 각 값을 이 페이지의 기준 값과 맞춰 다른 것만 남깁니다.
5. 켜진 PC 에서는 `reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options" /s /v Debugger` 처럼 읽기만 하는 명령으로 같은 값을 찾을 수 있습니다.
6. 값이 가리키는 파일의 서명을 확인합니다. 방법은 [의심 실행 파일 선별](../../03-techniques/analysis/code-signing-yara.md) 에 있습니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| Sysmon 12·13·14 | 이 자리의 값을 만들거나 바꾼 프로세스와 시각 | [레지스트리 변경](../event-logs/sysmon/12-13-14.md) |
| Sysmon 7 | AppInit 이나 Notify DLL 이 실제로 올라갔나 | [이미지 로드·프로세스 접근](../event-logs/sysmon/7-8-10.md) |
| 4688·Sysmon 1 | winlogon.exe·userinit.exe 에서 이어진 프로세스, 디버거로 대신 뜬 프로세스 | [프로세스 생성](../event-logs/4688.md), [Sysmon 이벤트 1](../event-logs/sysmon/1.md) |
| 로그온 자동실행 | Run·RunOnce·시작프로그램 폴더 | [로그온 자동실행](run-runonce-startup-folder.md) |
| 서비스·드라이버 | 부팅 때 도는 서비스와 드라이버 | [서비스·드라이버](services-drivers.md) |

MITRE 의 Winlogon 탐지 권고도 같은 방향입니다. `Shell`·`Userinit`·`Notify` 에 새 실행 파일이나 DLL 경로가 생기는 변경을 보고, winlogon.exe·userinit.exe 에서 이어지는 DLL 로드와 프로세스 생성과 엮어 봅니다. IFEO 는 이상한 프로세스 실행이나 높은 권한 토큰과 엮어 봅니다. 자동실행 위치 전체를 훑는 흐름은 [악성코드 지속성(자동실행) 찾기](../../04-scenarios/incident/persistence.md) 에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)에서 레지스트리 하이브를 꺼내 아래 질문을 풀어 봅니다.

1. Winlogon 의 `Shell`·`Userinit` 값은 무엇입니까? HKLM·WOW6432Node·HKCU 에서 각각 확인합니다.
2. `Userinit` 의 쉼표 뒤에 다른 경로가 이어집니까?
3. IFEO 하위 키는 몇 개입니까? 그 가운데 `Debugger` 나 전역 플래그 값이 있는 키가 있습니까?
4. `AppInit_DLLs` 에 값이 있습니까? 검체의 Windows 버전과 Secure Boot 상태로 보아 그 DLL 이 올라갈 수 있었습니까?
5. `BootExecute` 가 `autocheck autochk *` 와 같습니까?

## 참고 문헌

1. MITRE ATT&CK, *Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder (T1547.001)* (v19, 2026-05-12 수정). BootExecute·Load 값. https://attack.mitre.org/techniques/T1547/001/
2. Microsoft Learn, *AppInit DLLs and Secure Boot* (ms.date 2018-05-31). AppInit_DLLs 의 역할, Windows 8 이후 Secure Boot 에서 꺼지는 점, 인증 요건. https://learn.microsoft.com/en-us/windows/win32/dlls/secure-boot-and-appinit-dlls
3. MITRE ATT&CK, *Boot or Logon Autostart Execution: Winlogon Helper DLL (T1547.004)* (v19, 2025-10-24 수정). Winlogon 경로, Notify·Userinit·Shell, 탐지 권고. https://attack.mitre.org/techniques/T1547/004/
4. MITRE ATT&CK, *Event Triggered Execution: Image File Execution Options Injection (T1546.012)* (v19.2, 2026-05-12 수정). IFEO 경로, Debugger 값, SilentProcessExit 와 전역 플래그, GFlags, 탐지 권고. https://attack.mitre.org/techniques/T1546/012/
5. Microsoft Learn, *Monitoring Silent Process Exit* (ms.date 2023-06-19). `GlobalFlag` 값, SilentProcessExit 키, ReportingMode·MonitorProcess, Windows 7 부터, Application 로그의 Process Exit Monitor. https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/registry-entries-for-silent-process-exit
