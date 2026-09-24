# PowerShell 실행 기록 (PowerShell Event Logs: 4103·4104)

## 한 줄 요약

PowerShell 은 실행한 코드와 명령을 이벤트 로그에 남깁니다. 4104 에는 스크립트 블록 (Script Block) 의 내용이, 4103 에는 명령과 인자 값이 남습니다. 옛 방식 "Windows PowerShell" 로그의 400 에는 PowerShell 을 띄운 명령줄이 남습니다. 정책을 켜지 않아도 의심스러운 내용이 든 스크립트 블록은 4104 로 자동 기록됩니다.

## 무엇을 기록하나 · 왜 생기나

| 기록 | 로그 | 남는 때 | 알려 주는 것 |
|---|---|---|---|
| 4104 스크립트 블록 기록 (Script Block Logging) | PowerShell/Operational | 정책을 켜면 모든 스크립트 블록. 정책이 없어도 의심 내용이 든 블록 | 스크립트 블록 내용, ScriptBlock ID, 파일 경로 |
| 4105 · 4106 실행 시작·끝 | PowerShell/Operational | 실행 시작·끝 기록을 따로 켰을 때 | 스크립트 블록이 실행될 때마다 시작·끝 |
| 4103 모듈 기록 (Module Logging) | PowerShell/Operational | 모듈 기록을 켰을 때 | 명령 이름과 인자 값, 실행 환경 |
| 400 · 403 · 600 · 800 | Windows PowerShell | PowerShell 엔진이 시작·멈춤할 때 등 | 호스트 명령줄, 엔진 상태, 파이프라인 실행 내용 |
| 40961 · 40962 · 53504 | PowerShell/Operational | PowerShell 이 뜰 때 | PowerShell 이 떴다는 사실 |
| 녹취 (Transcription) | 로그가 아닌 텍스트 파일 | 녹취 정책을 켰을 때 | 입력한 명령과 출력 |

- 4104 를 켜면 PowerShell 이 처리하는 모든 스크립트 블록의 내용이 남습니다.
- 켠 뒤 새로 뜬 PowerShell 세션부터 남습니다.
- `Invoke-Expression` 처럼 실행 중에 만든 코드도 따로 스크립트 블록으로 남습니다.
- 그래서 난독화하거나 암호화한 스크립트도 푼 뒤의 내용을 볼 수 있습니다. Microsoft 블로그의 예에서는 Base64·XOR 로 감춘 코드가 풀린 `Write-Host 'Pwnd'` 로 남았습니다.
- 대화형 셸에 입력한 명령의 기록 파일은 [PowerShell 명령 기록 (ConsoleHost_history.txt)](../execution/consolehost-history-txt.md)에서 다룹니다.

## 위치와 버전별 차이

### 로그와 공급자

| PowerShell | 로그 | 공급자 | 파일 |
|---|---|---|---|
| Windows PowerShell (5.1 이하) | Microsoft-Windows-PowerShell/Operational | Microsoft-Windows-PowerShell `{A0C1853B-5C40-4B15-8766-3CF1C58F985A}` | `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-PowerShell%4Operational.evtx` |
| Windows PowerShell (옛 방식 로그) | Windows PowerShell | PowerShell | `%SystemRoot%\System32\Winevt\Logs\Windows PowerShell.evtx` (이름에 빈칸) |
| PowerShell 7 | PowerShellCore/Operational | `{f90714a8-5509-434a-bf6d-b1624c8a19a2}` | — |

- Microsoft-Windows-PowerShell 공급자의 메시지 파일은 `%windir%\system32\WindowsPowerShell\v1.0\PSEvents.dll` 이었습니다. (확인 범위: Win11 빌드 26200 한 대)
- 옛 방식 PowerShell 공급자의 메시지 파일은 `%SystemRoot%\system32\WindowsPowerShell\v1.0\pwrshmsg.dll` 이었습니다. (같은 PC)
- PowerShell 7 은 Windows 에서 `$PSHOME\RegisterManifest.ps1` 로 공급자를 등록해야 이벤트를 씁니다.
- 조사한 PC 에는 PowerShell 7 이 없었고 PowerShellCore/Operational 로그도 없었습니다.

### 켜는 설정

| 기록 | 설정 | 근거 |
|---|---|---|
| 4104 | 정책 "Turn on Script Block Logging". 레지스트리 값 이름은 EnableScriptBlockLogging 입니다 | Microsoft 블로그 |
| 4105 · 4106 | 같은 정책의 "Log script block invocation start / stop events". 레지스트리 `HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging` 의 EnableScriptBlockInvocationLogging = 1 | Microsoft 블로그 |
| 4103 | 세션과 모듈 양쪽에서 켭니다. 세션 안에서는 모듈의 LogPipelineExecutionDetails 속성으로 켜고 끕니다 | PowerShell 7 문서 |
| 녹취 | 정책 "Turn on PowerShell Transcription". `HKLM:\Software\Policies\Microsoft\Windows\PowerShell\Transcription` 의 EnableTranscripting (1), OutputDirectory, IncludeInvocationHeader (1) | Microsoft 블로그 |
| 보호된 이벤트 기록 | Administrative Templates -> Windows Components -> Event Logging -> Enable Protected Event Logging | Windows PowerShell 5.1 문서 |

- Windows PowerShell 5.1 의 모듈 기록 정책이 레지스트리 어디에 저장되는지는 이번에 연 자료에 없었습니다.
- 조사한 PC 에는 `HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell` 키 자체가 없었습니다. 그런데도 4104 가 수백 건 남아 있었습니다. (확인 범위: Win11 빌드 26200 한 대)

### 버전별 차이

| 항목 | 차이 |
|---|---|
| 녹취 | PowerShell 5 부터 녹취 파일 이름에 컴퓨터 이름과 충돌 방지 값이 들어갑니다. 시작 시각 정밀도도 높아졌습니다. 콘솔 말고 ISE·화면 없는 호스트에도 적용됩니다 |
| 보호된 이벤트 기록 | Windows 10 부터 있습니다 |
| 로그 이름 | PowerShell 7 은 Windows PowerShell 과 로그·공급자가 다릅니다 |

## 구조

### 4104 스크립트 블록

| 항목 | 값 |
|---|---|
| EventId | 4104 (0x1008) |
| Channel | Operational |
| Level | Verbose |
| Opcode | Create |
| Task | CommandStart |
| Keyword | Runspace |

한 PC 의 공급자 메타데이터에서 읽은 메시지와 칸은 다음과 같습니다. (확인 범위: Win11 빌드 26200 한 대)

- 메시지: `Creating Scriptblock text (%1 of %2): %3 ScriptBlock ID: %4 Path: %5`
- 칸: MessageNumber (Int32), MessageTotal (Int32), ScriptBlockText, ScriptBlockId, Path

| 칸 | 뜻 | 읽을 때 주의 |
|---|---|---|
| MessageNumber · MessageTotal | 나눈 조각의 번호와 전체 개수 | 긴 스크립트는 여러 이벤트로 나뉩니다 |
| ScriptBlockText | 스크립트 블록 내용 | 조각을 이어야 전체가 됩니다 |
| ScriptBlockId | 스크립트 블록이 살아 있는 동안 유지되는 GUID | 4105·4106 과 이을 때 씁니다 |
| Path | 스크립트 파일 경로 | 조사한 PC 의 4104 는 모두 명령줄로 넘긴 코드라 비어 있었습니다 |

- 한 이벤트에 담기 너무 긴 스크립트는 여러 이벤트로 나뉩니다.
- MessageNumber 로 정렬해 ScriptBlockText 를 이으면 원래 스크립트가 됩니다.
- 조사한 PC 에서 1/2·2/2, 1/3~3/3, 5/5 처럼 나뉜 예가 있었습니다.
- 한 이벤트에 들어가는 최대 길이는 확인하지 못했습니다.

### 정책 없이 남는 4104

- 스크립트 블록 기록을 켜지 않았어도 PowerShell 은 악성 스크립트가 자주 쓰는 내용이 든 블록을 자동으로 남깁니다.
- Microsoft 블로그는 이 기록을 "최후의 기록" 이라고 적었습니다. 백신이나 전체 기록을 대신하지 않습니다.
- 어떤 낱말이 걸리는지 목록은 확인하지 못했습니다.

정책이 없는 PC 에서 본 4104 의 머리 값입니다. (확인 범위: Win11 빌드 26200 한 대)

| 항목 | 값 |
|---|---|
| Version | 1 |
| Level | 3 (Warning) |
| Task | 2 |
| Opcode | 15 |
| Keywords | 0x0 |
| Security UserID | 실행한 사용자 SID |
| Execution ProcessID | 실행한 `powershell.exe` 의 PID |

- 이 PC 의 4104 는 모두 Level 3 (Warning) 이었습니다.
- 그래서 Warning 인 4104 는 자동 기록, Verbose (5) 인 4104 는 정책으로 켠 전체 기록으로 가를 수 있어 보입니다. 이 구분은 해석입니다. 이 PC 에서 Verbose 4104 를 만들어 보지는 않았습니다. 정책을 켠 PC 에서 의심 내용이 든 블록이 어느 Level 로 남는지도 확인하지 못했습니다. 그래서 Warning 이라고 정책이 꺼져 있었다고 단정하지 않습니다.

### 4105 · 4106 실행 시작·끝

| ID | 메시지 | 칸 |
|---|---|---|
| 4105 (0x1009) | Started invocation of ScriptBlock ID: %1 Runspace ID: %2 | ScriptBlockId, RunspaceId |
| 4106 (0x100A) | Completed invocation of ScriptBlock ID: %1 Runspace ID: %2 | ScriptBlockId, RunspaceId |

- ScriptBlock ID 로 4104 와 이을 수 있습니다.
- Runspace ID 는 그 블록이 돈 런스페이스 (Runspace) 입니다.
- 스크립트 블록이 실행될 때마다 남으므로 양이 매우 많아질 수 있습니다.

### 4103 모듈 기록

- 메시지: `%3 Context: %1 User Data: %2`
- 칸: ContextInfo, UserData, Payload
- 4100 (오류) 과 4102 도 같은 세 칸을 씁니다.

(확인 범위: Win11 빌드 26200 한 대)

조사한 PC 의 4103 은 Level 4, Task 106, Opcode 20 이었습니다. Payload 에는 명령과 인자 값이 이런 꼴로 들어 있었습니다.

```
CommandInvocation(Add-Type): "Add-Type"
ParameterBinding(Add-Type): name="TypeDefinition"; value="…"
```

ContextInfo 는 "키 = 값" 줄 묶음입니다. 키 이름은 화면 언어로 저장돼 있었습니다. 한국어 PC 의 키는 다음과 같았습니다.

- 심각도, 호스트 이름, 호스트 버전, 호스트 ID, 호스트 응용 프로그램, 엔진 버전
- Runspace ID, 파이프라인 ID, 명령 이름, 명령 유형, 스크립트 이름, 명령 경로
- 시퀀스 번호, 사용자, 연결된 사용자, 셸 ID

"호스트 응용 프로그램" 에는 `powershell.exe` 의 전체 명령줄이 들어 있었습니다. 예: `-NoProfile -NonInteractive -ExecutionPolicy Bypass -Command …`.

- 조사한 PC 는 모듈 기록 정책이 없는데도 4103 이 9건 있었습니다. 그중 7건이 `Add-Type` 이었습니다. 왜 남았는지는 확인하지 못했습니다.
- 영어 PC 의 키 이름 목록은 확인하지 못했습니다.

### 옛 방식 "Windows PowerShell" 로그

조사한 PC 에서 본 이벤트입니다. (확인 범위: Win11 빌드 26200 한 대)

| ID | 메시지 | 건수 |
|---|---|---|
| 600 | Provider "Variable" is Started. (ProviderName, NewProviderState …) | 512 |
| 400 | Engine state is changed from None to Available. | 86 |
| 403 | Engine state is changed from Available to Stopped. | 84 |
| 800 | Pipeline execution details for command line: … | 1 |

- EventData 안에 이름 없는 Data 3개로 들어 있습니다. 칸 이름이 없습니다.
- 400 의 Details 에는 NewEngineState, PreviousEngineState, SequenceNumber, HostName, HostVersion, HostId, HostApplication, EngineVersion, RunspaceId, PipelineId, CommandName, CommandType, ScriptName, CommandPath, CommandLine 이 있습니다.
- 800 의 Context 에는 DetailSequence, DetailTotal, UserId, HostName … CommandLine 이 있고, 이어서 Details 에 CommandInvocation·ParameterBinding 이 있습니다.
- 이 로그의 Details 키는 4103 과 달리 영어였습니다 (예: `HostName=ConsoleHost`).
- HostApplication 에는 `-EncodedCommand` 로 넘긴 Base64 전체가 그대로 들어 있었습니다.
- 그래서 스크립트 블록 기록이 꺼져 있어도 400 의 HostApplication 으로 실행 명령줄을 볼 수 있습니다.

### 그 밖의 Operational 이벤트

| ID | 메시지 | Level |
|---|---|---|
| 40961 | PowerShell console is starting up | — |
| 40962 | PowerShell console is ready for user input | — |
| 53504 | Windows PowerShell has started an IPC listening thread on process: %1 in AppDomain: %2. | — |
| 8193 · 8194 · 8197 · 12039 | Creating Runspace object / Creating RunspacePool object / Runspace state changed to %1 / Modifying activity Id and correlating | Verbose |

- 40961·40962·53504 는 PowerShell 이 뜰 때마다 남았습니다. 조사한 PC 에서 셋 다 329건으로 같았습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 기록 시각에 이 내용의 스크립트 블록을 PowerShell 이 처리했다는 것 (4104) | 그 블록이 끝까지 실행되고 뜻한 결과를 냈는지 |
| 그 블록을 처리한 프로세스 PID 와 사용자 SID (4104 머리 값) | 그 계정 뒤에 있던 사람이 누구인지 |
| 명령 이름과 넘긴 인자 값 (4103, 800) | 로그가 꺼져 있던 기간이나 밀려난 기간에 실행이 없었다는 것 |
| PowerShell 을 띄운 명령줄 (400 의 HostApplication, 4103 의 호스트 응용 프로그램) | 녹취 파일이나 기록 파일이 없다고 명령 입력이 없었다는 것 |

### 보고서 문장

- 쓸 수 있는 문장: "PowerShell/Operational 로그에 ○○(UTC) 의 4104 (Level Warning) 가 있습니다. ScriptBlock ID ○○ 의 조각 3개를 이은 내용은 부록 ○ 과 같습니다. 머리 값의 Execution ProcessID 는 ○○ 입니다."
- 쓰면 안 되는 문장: "사용자가 악성 스크립트를 실행해 정보를 빼냈다."

두 번째 문장은 사람과 의도, 결과를 적습니다. 4104 는 블록을 처리했다는 기록입니다. 결과는 다른 흔적으로 확인합니다.

## 시각 해석

- 4104 의 기록 시각은 스크립트 블록을 처음 만들 때 (컴파일) 입니다.
- 기본 설정에서는 같은 블록을 다시 실행해도 다시 남지 않습니다. 스크립트 블록을 처음 쓸 때 한 번만 남기기 때문입니다.
- 실행할 때마다의 시각은 4105·4106 에서 봅니다. 따로 켜야 남습니다.
- 400 의 메시지는 엔진이 사용 가능 (Available) 상태가 됐다는 뜻이고, 403 은 멈춤 (Stopped) 상태가 됐다는 뜻입니다.
- 그래서 400 과 403 사이를 엔진이 떠 있던 구간으로 볼 수 있습니다. 이 판단은 메시지에서 이끈 해석입니다.
- 시각 값 저장 형식은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

## 함정과 한계

1. **자동 기록을 전체 기록으로 읽습니다.** 정책이 없으면 의심 내용이 든 블록만 남습니다. 남지 않은 블록이 없었다는 뜻이 아닙니다.
2. **메시지 글자로 거릅니다.** 이 PC 메타데이터의 메시지는 "Creating Scriptblock text" 였습니다. Microsoft 블로그의 예시 출력은 "Compiling Scriptblock text" 였습니다. 글자가 아니라 ID 와 칸으로 거릅니다.
3. **조각 하나만 봅니다.** MessageTotal 이 1 보다 크면 같은 ScriptBlock ID 의 조각을 모두 모읍니다.
4. **4103 을 영어 키로 찾습니다.** ContextInfo 의 키 이름은 화면 언어로 저장됩니다. "Host Application" 으로 찾는 도구는 한국어 PC 의 4103 에서 값을 찾지 못합니다.
5. **스크립트 내용만 봅니다.** 스크립트 내용 (4104) 과 실행 명령줄 (400 의 HostApplication, 4103 의 호스트 응용 프로그램) 은 다른 곳에 있습니다. 둘 다 봅니다.
6. **로그가 오래 남는다고 봅니다.** 조사한 PC 의 Operational 로그는 15MB 였습니다. 가장 오래된 기록은 조사 시점 약 3시간 반 전이었습니다 (1,868건). 조사하는 30분 사이에 952건으로 줄었습니다. 이 PC 는 자동화 도구가 PowerShell 을 쉴 새 없이 돌리는 특수한 경우입니다. (확인 범위: Win11 빌드 26200 한 대)
7. **보호된 이벤트 기록을 흘려봅니다.** 이 정책을 켜면 공개키 (CMS, RFC 5652) 로 로그 내용을 암호화합니다. 개인키가 없으면 내용을 읽을 수 없습니다. 인증서는 Document Encryption EKU (1.3.6.1.4.1.311.80.1) 가 있어야 합니다. 이 정책이 켜진 PC 의 4104 가 어떤 모양인지는 확인하지 못했습니다.
8. **보호된 이벤트 기록이 켜져 있으면 스크립트 블록 기록도 켜졌다고 봅니다.** 보호된 이벤트 기록을 켜도 스크립트 블록 기록은 자동으로 켜지지 않습니다.
9. **PowerShell 7 을 흘려봅니다.** PowerShell 7 은 PowerShellCore/Operational 에 씁니다. Windows PowerShell 로그만 보면 빠집니다.

### 지우기와 조작

- **자동 기록을 끕니다.** 정책을 Disabled 로 하거나 EnableScriptBlockLogging 을 0 으로 두면 자동 기록도 남지 않습니다. 이 값이 0 으로 설정돼 있으면 누가 언제 설정했는지 확인합니다.
- **로그를 가짜 이벤트로 채웁니다.** Microsoft 블로그는 로그를 가짜 이벤트로 채워 이전 증거를 밀어내는 공격을 적었습니다. 이벤트를 빨리 다른 곳으로 모으라고 권합니다.
- **로그를 지웁니다.** 104 가 남습니다. [이벤트 로그 삭제 (1102·104)](1102-104.md)를 봅니다.
- **레코드 일부만 남습니다.** 밀려나거나 지운 레코드가 파일 안에 남아 있을 수 있습니다. [파일 안에 남은 지운·손상 레코드](../../01-foundations/database-log-formats/evtx-evt-etl/chunk-slack-corrupted-evtx.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

4104 의 칸 값은 이진 XML 의 치환 값으로 들어 있습니다. 값 종류와 배열은 [이진 XML 해석](../../01-foundations/database-log-formats/evtx-evt-etl/binary-xml-template.md)에서 다룹니다. 여기서는 값 데이터 세 개만 봅니다.

아래 바이트는 설명을 위해 명세대로 만든 예시입니다. 검체에서 나온 값이 아닙니다. 스크립트가 세 조각으로 나뉘었고 그 가운데 첫 조각이라고 하겠습니다.

```
01 00 00 00                                       MessageNumber (Int32)
03 00 00 00                                       MessageTotal  (Int32)
57 00 72 00 69 00 74 00 65 00 2D 00 48 00 6F 00 73 00 74 00   ScriptBlockText 앞부분
```

1. MessageNumber 는 리틀 엔디언 Int32 로 1 입니다.
2. MessageTotal 은 3 입니다. 이 블록은 조각 세 개로 나뉘었습니다.
3. ScriptBlockText 는 UTF-16LE 문자열입니다. 위 바이트는 `Write-Host` 입니다.
4. 지운 레코드를 찾을 때는 찾는 낱말을 UTF-16LE 바이트로 바꿔 검색합니다. `Write-Host` 는 위 20바이트입니다.

> 그림 자리: 4104 레코드 세 개의 MessageNumber·MessageTotal·ScriptBlockText 를 나란히 놓고 이어 붙이는 그림

### 공개 도구로 한 번

Windows 에 들어 있는 PowerShell 의 `Get-WinEvent` 로 조각을 모아 잇습니다. Microsoft 블로그의 방법처럼 Properties[0] (MessageNumber) 으로 정렬하고 Properties[2] (ScriptBlockText) 를 잇습니다. 아래 `E:\case\` 는 예시 경로입니다.

```powershell
$f = 'E:\case\Microsoft-Windows-PowerShell%4Operational.evtx'

# ScriptBlock ID 별로 조각을 모아 원래 스크립트로 잇기
Get-WinEvent -FilterHashtable @{ Path = $f; Id = 4104 } |
  Group-Object { $_.Properties[3].Value } |
  ForEach-Object {
    $parts = $_.Group | Sort-Object { [int]$_.Properties[0].Value }
    [pscustomobject]@{
      ScriptBlockId = $_.Name
      Level         = $parts[0].LevelDisplayName
      First         = ($parts | Sort-Object TimeCreated)[0].TimeCreated
      Text          = ($parts | ForEach-Object { $_.Properties[2].Value }) -join ''
    }
  }

# 옛 방식 로그의 400 에서 HostApplication 줄 꺼내기
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\Windows PowerShell.evtx'; Id = 400 } |
  ForEach-Object { ($_.Message -split "`n") -match 'HostApplication=' }
```

보호된 이벤트 기록으로 암호화된 4104 는 개인키가 있는 PC 에서 이렇게 풉니다.

```powershell
Get-WinEvent Microsoft-Windows-PowerShell/Operational | Where-Object Id -EQ 4104 | Unprotect-CmsMessage
```

도구가 긴 ScriptBlockText 를 자르거나 조각을 따로 보여 주는지 확인합니다. 한두 개는 XML 원문과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [PowerShell 명령 기록 (ConsoleHost_history.txt)](../execution/consolehost-history-txt.md) | 대화형으로 입력한 명령과 4104 내용 |
| [프로세스 생성 (4688)](4688.md) · [Sysmon 프로세스 생성 (이벤트 1)](sysmon/1.md) | 4104 의 Execution ProcessID 와 같은 PID 의 `powershell.exe`, 부모 프로세스, 명령줄 |
| [원격 명령 실행 이벤트 (WinRM·WMI-Activity)](winrm-wmi-activity.md) | 원격 세션과 같은 시각의 4104 |
| [감사 정책과 로그 설정](audit-policy-log-settings.md) | Operational 채널 크기와 로그가 덮는 기간 |
| [프리페치](../execution/prefetch/index.md) | `powershell.exe` 실행 횟수와 시각 |
| [다른 PC 에서 원격 실행했나 (PsExec·WMI·WinRM)](../../04-scenarios/incident/credential-theft-lateral-movement/psexec-wmi-winrm.md) | 원격 실행 흐름 안에서 4104 의 자리 |

원격으로 실행한 PowerShell 도 도착 PC 의 이 로그에 남는다는 설명이 있지만, 이번에 확인하지 못했습니다.

## 실습

**직접 만든 Windows 10·11 가상 머신**에서 해 봅니다. 각 단계의 시각을 적어 둡니다.

1. 정책을 켜기 전에 `Get-Date` 같은 평범한 명령을 실행합니다. 4104 가 남는지 봅니다.
2. 스크립트 블록 기록 정책을 켜고 새 PowerShell 창을 엽니다. 같은 명령의 4104 가 어느 Level 로 남는지 봅니다. 이 페이지가 확인하지 못한 Level 구분입니다.
3. 긴 스크립트 파일을 실행합니다. 몇 조각으로 나뉘는지, Path 칸에 파일 경로가 들어가는지 봅니다.
4. 같은 스크립트를 두 번 실행합니다. 4104 가 한 번만 남는지 봅니다. 실행 시작·끝 기록을 켜고 4105·4106 도 봅니다.
5. `-EncodedCommand` 로 무해한 명령을 넘깁니다. 400 의 HostApplication 과 4104 의 ScriptBlockText 를 비교합니다.
6. 녹취 정책을 켜고 OutputDirectory 를 비워 둡니다. 녹취 파일이 어디에 생기는지 적습니다.

**NIST CFReDS 같은 공개 검체**에서는 다음을 풀어 봅니다.

1. PowerShell/Operational 로그에 4104 가 있습니까? Level 은 무엇입니까? 정책 레지스트리 키가 있습니까?
2. MessageTotal 이 1 보다 큰 블록을 이어 붙이면 어떤 내용입니까?
3. 옛 방식 로그 400 의 HostApplication 에 `-EncodedCommand` 가 있습니까? 있다면 풀어서 4104 와 맞춰 봅니다.
4. 두 로그가 덮는 기간은 각각 언제부터 언제까지입니까?

## 참고 문헌

- Microsoft Learn, "about_Logging" (Windows PowerShell 5.1, 2024-01-09) — https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging?view=powershell-5.1
- Microsoft Learn, "about_Logging_Windows" (PowerShell 7, 2026-01-18) — https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging_windows?view=powershell-5.1
- Microsoft PowerShell Team 블로그, "PowerShell ♥ the Blue Team" (2015-06-09) — https://devblogs.microsoft.com/powershell/powershell-the-blue-team/
