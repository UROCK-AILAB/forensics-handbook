---
title: "ETW 추적 로그"
parent: "이벤트 로그 형식"
grand_parent: "기반 · 데이터베이스·로그 형식"
nav_order: 380
---

# ETW 추적 로그 (ETL)

## 한 줄 요약

ETW (Event Tracing for Windows) 는 커널 수준에서 동작하는 Windows 의 추적 기능입니다. 커널이나 앱이 정한 이벤트를 실시간으로 넘기거나 로그 파일(`.etl`)에 씁니다. `.etl` 파일의 첫 이벤트에는 세션 머리 정보 (TRACE_LOGFILE_HEADER) 가 들어 있고, 여기에 세션 시작 시각과 시스템 부팅 시각이 남습니다.

이 페이지는 [이벤트 로그 형식 (EVTX·EVT·ETL)](index.md) 의 하위 주제입니다. 이벤트 뷰어가 여는 `.evtx` 파일은 [EVTX 파일 구조 (File Header·Chunk·Record)](file-header-chunk-record.md) 에서 다룹니다.

## 이 형식을 쓰는 아티팩트

- 부팅 초기 추적 세션인 AutoLogger 가 `.etl` 파일을 남깁니다. 세션 설정에 FileName 값이 없으면 `%SystemRoot%\System32\LogFiles\WMI\<세션이름>.etl` 에 씁니다.
- 확인 PC 의 `C:\Windows\System32\LogFiles\WMI` 에는 LwtNetLog.etl·NetCore.etl·RadioMgr.etl·Wifi.etl·ReFSLog.etl·NtfsLog.etl.002 ~ .006 등이 있었습니다(확인 범위: Windows 11 25H2 PC 한 대, 이하 같음).
- 같은 폴더의 `RtBackup` 에는 `EtwRT<세션이름>.etl` 파일들이 있었습니다. EtwRTDiagLog.etl 은 72바이트였고, EtwRTAdmin_PS_Provider.etl 은 약 26MB 였습니다.
- 이벤트 로그 쪽 세션도 ETW 설정 키에 있습니다. 아래 "이벤트 로그(EVTX)와의 관계" 를 봅니다.

## 구조

> 그림 자리: 컨트롤러가 세션을 열고, 공급자가 이벤트를 내고, 세션이 이벤트를 버퍼에 모아 소비자(실시간) 또는 `.etl` 파일로 넘기는 흐름. 그 아래에 `.etl` 파일이 같은 크기의 버퍼로 나뉘고 첫 버퍼에 머리 정보가 들어 있는 모습

### ETW 의 세 부분

| 부분 | 하는 일 |
|---|---|
| 컨트롤러 (Controller) | 세션을 시작하고 멈춥니다. 공급자를 켭니다. 로그 파일의 크기와 위치, 버퍼 풀 크기를 정합니다 |
| 공급자 (Provider) | 이벤트를 냅니다 |
| 소비자 (Consumer) | 이벤트를 받습니다. 여러 세션을 동시에 받을 수 있고, 시스템이 이벤트를 시간 순서로 넘깁니다. 로그 파일에서도 받고 실시간으로도 받습니다 |

### 공급자 종류

공급자는 MOF(고전)·WPP·매니페스트 기반·TraceLogging 네 종류이고, 종류마다 이벤트 값의 형식과 해석 정보를 두는 곳이 다릅니다. MOF·WPP 공급자는 한 번에 세션 하나에만 켤 수 있지만, 매니페스트 기반·TraceLogging 공급자는 세션 8개까지 동시에 켤 수 있습니다.

WPP 공급자의 해석 정보는 TMF 파일에 있고, TMF 는 바이너리의 `.pdb` 안에 들어 있습니다. TraceLogging 이벤트는 해석에 필요한 정보를 이벤트 안에 모두 담습니다(self-describing). 매니페스트는 PE 파일의 WEVT_TEMPLATE 리소스에 이진 형태로 들어갈 수 있으며, 리소스 구조는 [공급자와 메시지 파일 (Provider·Message Table)](provider-message-table.md) 에서 다룹니다.

### 로그 모드 (LogFileMode)

LogFileMode 는 아래 상수를 비트로 합친 값입니다.

| 이름 | 값 | 뜻 |
|---|---|---|
| NONE | 0x0 | 최대 크기가 없는 SEQUENTIAL 입니다 |
| SEQUENTIAL | 0x1 | 순서대로 쓰다가 최대 크기에 닿으면 멈춥니다 |
| CIRCULAR | 0x2 | 최대 크기에 닿으면 가장 오래된 이벤트 자리에 새 이벤트를 씁니다. 프로세서가 여럿이면 순서가 뒤섞여 보일 수 있습니다 |
| APPEND | 0x4 | 기존 순차 파일 뒤에 덧붙입니다 |
| NEWFILE | 0x8 | 최대 크기에 닿으면 새 파일로 넘어갑니다. 파일 이름의 `%d` 자리 번호가 늘어납니다(예: `c:\test%d.etl`) |
| PREALLOCATE | 0x20 | 최대 크기만큼 디스크 공간을 미리 잡습니다. 세션을 멈추면 필요한 크기로 줄입니다 |
| REAL_TIME | 0x100 | 버퍼를 비울 때 소비자에게 넘깁니다. 파일 모드와 함께 쓰면 덜 찬 버퍼도 1초마다 파일에 씁니다 |
| BUFFERING | 0x400 | 메모리의 원형 버퍼에만 쓰고 파일로 내보내지 않습니다 |
| PRIVATE_LOGGER | 0x800 | 공급자와 같은 프로세스 안에서 도는 세션입니다. 프로세스가 여럿이면 파일 이름 뒤에 `_프로세스ID` 가 붙습니다(예: `myprivatelog.etl_nnnn`). 처음 프로세스의 파일에는 붙지 않습니다 |
| NO_PER_PROCESSOR_BUFFERING | 0x10000000 | 여러 프로세서의 이벤트를 버퍼 하나에 씁니다. 이 모드 없이 시스템 시각을 시계로 쓰면 버퍼가 프로세서마다 따로 있어 순서가 뒤바뀌어 보일 수 있습니다. Windows 7 부터 지원합니다 |

### AutoLogger 설정 (레지스트리)

AutoLogger 는 부팅 초기, 로그인 전의 이벤트를 기록하는 세션입니다. Windows Vista 부터 지원합니다. 그 전에는 Global Logger 를 썼습니다.

설정은 `HKLM\SYSTEM\CurrentControlSet\Control\WMI\Autologger\<세션 이름>` 키에 있습니다. 그 아래에 공급자 GUID 를 이름으로 쓴 키가 있습니다. 하이브를 읽는 법은 [레지스트리 하이브 구조](../registry-hive/index.md) 에 있습니다.

| 세션 키 값 | 뜻 |
|---|---|
| BufferSize | 버퍼 크기(KB) |
| ClockType | 시계 종류. 1 성능 카운터, 2 시스템 타이머, 3 CPU 사이클. Vista 이후 기본값은 1 입니다 |
| FileName | 로그 파일 경로. 없으면 `%SystemRoot%\System32\LogFiles\WMI\<세션이름>.etl` 입니다 |
| FileMax | 만들 파일 개수 한도. 최대 16 입니다 |
| FileCounter | 파일 이름 번호. 문서는 이 값을 건드리지 말라고 적습니다 |
| FlushTimer | 버퍼를 강제로 비우는 간격(초). 기본 0 이면 버퍼가 찰 때만 비웁니다. 실시간 세션은 0 이면 1초입니다 |
| LogFileMode | 위 로그 모드 |
| MaxFileSize | 최대 파일 크기(MB). 기본 100, 0 이면 제한이 없습니다. LogFileMode 에 USE_KBYTES_FOR_SIZE(0x2000) 가 있으면 단위가 KB 입니다 |
| Start | 1 이면 다음 부팅에 세션을 시작합니다 |
| Status | 세션을 시작한 결과. Win32 오류 코드입니다 |
| DisableRealtimePersistence | 기본 0(켜짐)입니다. 켜져 있으면 종료 때까지 넘기지 못한 실시간 이벤트를 저장해 둡니다. 다음에 소비자가 붙으면 그 이벤트를 넘깁니다 |

- 이 밖에 Guid·MaximumBuffers·MinimumBuffers 값이 있습니다.
- 공급자 키에는 Enabled·EnableLevel·EnableFlags·EnableProperty·MatchAnyKeyword·MatchAllKeyword 값이 있습니다.
- EnableProperty 가 0x1 이면 이벤트의 확장 데이터에 사용자 SID 가 들어갑니다. SID 를 읽는 법은 [윈도 식별자 형식](../../value-decoding/sid-guid-clsid-known-folder-id.md) 에 있습니다.
- AutoLogger 는 NEWFILE 모드를 지원하지 않습니다.
- FileMax 를 쓰면 문서상 파일 이름이 `<세션이름>.etl.0001`, `.0002` … 로 늘어납니다. 한도를 넘으면 1 로 돌아가 덮어씁니다.

확인 PC 의 Autologger 키 아래에는 Circular Kernel Context Logger·DefenderApiLogger·DiagLog·Diagtrack-Listener·EventLog-Application·EventLog-Security·EventLog-System·LwtNetLog·NetCore·NtfsLog·RadioMgr·ReFSLog·WdiContextLog 등의 세션 키가 있었습니다. 그중 몇 개의 값입니다.

| 세션 | LogFileMode | MaxFileSize | BufferSize | 그 밖의 값 | 파일 |
|---|---|---|---|---|---|
| NetCore | 0x22 (CIRCULAR + PREALLOCATE) | 0x16 (22MB) | 0x80 | FileName=`%SystemRoot%\System32\LogFiles\WMI\NetCore.etl` | NetCore.etl, 23,068,672바이트 |
| LwtNetLog | 0x2 (CIRCULAR) | 0x10 (16MB) | 0x40 | | LwtNetLog.etl |
| NtfsLog | | 8 | 8 | FileName 없음, FileMax=8, FileCounter=6 | NtfsLog.etl.002 ~ .006 |
| ReFSLog | 값 없음 | 값 없음 | 값 없음 | ClockType·Start·Status 만 있음 | ReFSLog.etl |

- NetCore.etl 의 크기 23,068,672바이트는 정확히 22 × 1,048,576 입니다. PREALLOCATE 모드가 최대 크기만큼 공간을 미리 잡은 결과와 맞습니다.
- NtfsLog 파일 번호는 세 자리(`.002`)였습니다. 문서의 네 자리(`.0001`)와 다릅니다.
- 빈칸은 확인하지 않은 값입니다.

### 파일 안 모양 (버퍼)

버퍼 머리 구조 (WMI_BUFFER_HEADER) 의 공식 필드 표는 이 페이지가 참고한 자료로 확인하지 못했습니다. 아래는 확인 PC 의 `.etl` 4개(LwtNetLog·NtfsLog·ReFSLog·NetCore)를 읽어 본 결과입니다.

파일 맨 앞에는 고정 서명이 없었고, 첫 4바이트가 버퍼 크기였습니다. LwtNetLog 는 0x10000, NtfsLog 는 0x2000, ReFSLog 는 0x1000, NetCore 는 0x20000 이었습니다. 레지스트리에 BufferSize 가 있는 세션은 이 값과 맞았으며, LwtNetLog 0x40, NtfsLog 0x8, NetCore 0x80 이고 단위는 KB 입니다.

파일 크기는 버퍼 크기의 정수배였고, 모든 버퍼의 첫 4바이트가 같은 버퍼 크기였습니다. LwtNetLog 는 버퍼 81개가 모두 그랬습니다. 첫 버퍼의 TRACE_LOGFILE_HEADER 는 파일 오프셋 0x68 에서 시작했습니다.

### 머리 정보 (TRACE_LOGFILE_HEADER)

Microsoft 문서는 이 구조를 ETW 로그 파일 머리의 원시 데이터 형식으로 설명합니다. 어떤 로그 파일이든 첫 이벤트에 이 구조의 데이터가 들어 있습니다.

필드는 이 순서로 놓입니다: BufferSize, Version, ProviderVersion, NumberOfProcessors, EndTime, TimerResolution, MaximumFileSize, LogFileMode, BuffersWritten, (StartBuffers·PointerSize·EventsLost·CpuSpeedInMHz), LoggerName, LogFileName, TimeZone, BootTime, PerfFreq, StartTime, ReservedFlags, BuffersLost.

| 필드 | 뜻 |
|---|---|
| Version | 주·부 버전 |
| ProviderVersion | OS 빌드 번호 |
| NumberOfProcessors | 프로세서 수 |
| EndTime | 세션이 멈춘 시각. 제대로 닫히지 않은 파일은 0 일 수 있습니다 |
| MaximumFileSize | 최대 파일 크기(MB) |
| LogFileMode | 로그 모드 |
| PointerSize | 포인터 크기. 이 값에 따라 구조 크기가 달라집니다 |
| EventsLost | 세션 동안 잃은 이벤트 수 |
| LoggerName·LogFileName | 포인터 칸이라 값으로 쓰지 않습니다. 구조 바로 뒤의 첫째 널 종료 문자열이 세션 이름, 둘째가 로그 파일 이름입니다 |
| TimeZone | TIME_ZONE_INFORMATION 구조. BootTime·EndTime·StartTime 의 시간대입니다 |
| BootTime | 시스템 부팅 시각. 문서는 Global Logger 세션 추적에서만 지원한다고 적습니다 |
| StartTime | 세션 시작 시각 |
| ReservedFlags | 시계 종류 |
| BuffersLost | 세션 동안 잃은 버퍼 수 |

- StartTime·EndTime·BootTime 은 1601-01-01 부터 센 100ns 단위입니다. FILETIME 과 단위가 같습니다. 푸는 법은 [시각 값 형식](../../value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- 다른 PC 나 32비트(WOW) 세션에서 만든 파일은 구조 크기가 다를 수 있습니다. 분석 PC 의 구조 정의로 바로 읽으면 값이 틀릴 수 있습니다.

확인 PC 의 `.etl` 4개에서 본 값입니다.

버전은 10.0, ProviderVersion 은 26100, 프로세서 수는 24, PointerSize 는 8 이었습니다. EndTime 은 모두 0 이었는데 쓰는 중인 파일이었습니다. 시간대 Bias 는 −540, 시간대 이름은 `@tzres.dll,-622` 였습니다.

LogFileMode 와 MaximumFileSize 는 레지스트리 값과 같았습니다. NetCore 는 0x22 와 22, LwtNetLog 는 0x2 와 16 이었습니다. ReFSLog 는 레지스트리에 MaxFileSize 값이 없었고, 머리에는 기본값 100 이 들어 있었습니다.

## 읽는 법

1. 원본의 해시를 구하고 사본에서 작업합니다.
2. 이미지의 SYSTEM 하이브에서 `Control\WMI\Autologger` 키를 읽습니다. 세션마다 FileName·LogFileMode·MaxFileSize·BufferSize·FileMax 를 적어 둡니다.
3. FileName 이 없는 세션은 `%SystemRoot%\System32\LogFiles\WMI\<세션이름>.etl` 과 번호가 붙은 파일을 찾습니다. `RtBackup` 폴더도 함께 확보합니다.
4. 파일 앞 4바이트로 버퍼 크기를 읽고, 레지스트리 BufferSize × 1,024 와 비교합니다. 파일 크기가 버퍼 크기의 정수배인지도 확인합니다.
5. 첫 버퍼의 TRACE_LOGFILE_HEADER 에서 PointerSize 를 먼저 확인합니다. 그다음 시각·로그 모드·잃은 이벤트 수를 읽습니다.
6. 세션 이름과 로그 파일 이름은 구조 바로 뒤의 문자열에서 읽습니다.
7. 이벤트 본문은 공급자 종류에 맞는 해석 정보로 풉니다. WPP 이벤트는 TMF 정보가 있어야 풀립니다.

### 헥스로 한 번 따라가기

아래는 확인 PC 의 LwtNetLog.etl 에서 본 규칙으로 만든 예시입니다. 공식 명세로 확인한 구조가 아닙니다. 실제 파일에서 떠낸 바이트도 아닙니다. `??` 는 이 설명에 쓰지 않는 바이트입니다.

```
오프셋    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  00 00 01 00 ?? ?? ?? ??  ?? ?? ?? ?? ?? ?? ?? ??
  ...
00010000  00 00 01 00 ?? ?? ?? ??  ?? ?? ?? ?? ?? ?? ?? ??
  ...
00020000  00 00 01 00 ?? ?? ?? ??  ?? ?? ?? ?? ?? ?? ?? ??
```

- 0x00 `00 00 01 00` 은 리틀 엔디언으로 0x10000, 곧 65,536 입니다. 이 파일의 버퍼 크기입니다.
- 레지스트리의 BufferSize 0x40 은 KB 단위라 64 × 1,024 = 65,536 입니다. 두 값이 같습니다.
- 첫 버퍼에서는 0x68 부터 TRACE_LOGFILE_HEADER 가 이어집니다. 0x04 ~ 0x67 은 버퍼 머리 자리이고, 필드 표는 확인하지 못했습니다.
- 0x10000 과 0x20000 에서도 같은 4바이트가 나옵니다. 버퍼가 65,536바이트마다 이어집니다.
- n 번째 버퍼는 (n − 1) × 0x10000 에서 시작합니다.

## 포렌식에서 중요한 점

### 부팅 시각이 파일마다 남는다

- 확인 PC 의 LwtNetLog·NetCore·NtfsLog.etl.006 은 BootTime 이 2026-09-20 21:44:17, StartTime 이 21:44:18 이었습니다. FILETIME 을 그대로 UTC 로 푼 값입니다.
- 한국 시각으로는 09-21 06:44 입니다. `RtBackup` 파일들의 수정 시각(09-21 06:44)과 맞았습니다. 확인 PC 에서는 이 시각이 UTC 로 저장돼 있었습니다.
- NtfsLog.etl.002 는 BootTime 이 2026-09-10 21:57:03(UTC) 이었습니다. 이전 부팅의 시각이 남아 있었습니다.
- 확인 PC 에서는 부팅마다 번호 파일이 생겨서 번호 파일마다 그때의 부팅 시각이 남았습니다.
- 이 값은 켜짐·꺼짐 기록과 맞춰 볼 수 있습니다. [켜짐·꺼짐](../../../02-artifacts/event-logs/power-on-off-events.md) 과 [PC 사용 시간 재구성](../../../04-scenarios/activity/system-usage-time.md) 을 봅니다.

### 시간대 값

- TimeZone 필드는 머리에 적힌 시각들의 시간대입니다.
- Bias 는 부호 있는 32비트로 읽습니다. UTC+9 는 −540 입니다. 부호 없이 읽으면 엉뚱한 큰 수가 나옵니다. 레지스트리의 시간대 값도 같은 방식입니다. [시간대 설정](../../../02-artifacts/system-account/time-zone.md) 을 봅니다.

### 빠진 이벤트

머리의 EventsLost·BuffersLost 는 세션 동안 잃은 이벤트와 버퍼 수입니다. Microsoft 문서가 드는 이벤트가 빠지는 경우는 넷입니다.

- 이벤트 전체 크기(ETW 헤더 + 값)가 64K 를 넘을 때
- ETW 버퍼가 이벤트보다 작을 때
- 실시간 소비자가 느리거나 없을 때. 예: 이벤트 로그 서비스를 멈췄다 다시 켜는 동안
- 파일에 쓸 때 디스크가 기록 속도를 따라가지 못할 때

기록이 없다는 사실만으로 그 시간에 일이 없었다고 쓰지 않습니다.

### 덮어쓰기와 순서

- CIRCULAR 모드 파일은 최대 크기에 닿으면 가장 오래된 이벤트부터 덮습니다. 파일 안의 이벤트는 세션 전체가 아니라 마지막 구간일 수 있습니다.
- 프로세서별 버퍼를 쓰는 세션은 이벤트 순서가 뒤섞여 보일 수 있습니다. 시각으로 다시 정렬합니다.
- FileMax 를 쓰는 AutoLogger 는 번호가 한도를 넘으면 앞 번호 파일을 덮어씁니다. 번호가 곧 시간 순서라고 보지 않습니다.

### 이벤트 로그(EVTX)와의 관계

- 확인 PC 의 Autologger 키 아래에 EventLog-Application·EventLog-Security·EventLog-System 세션 키가 있었고, EventLog-System 키의 값은 OwningChannel=System, LogFileMode=0x98000180, BufferSize=0x40, FlushTimer=1 이었습니다.
- 0x98000180 을 로그 모드 상수로 풀면 SECURE(0x80)·REAL_TIME(0x100)·INDEPENDENT_SESSION(0x08000000)·NO_PER_PROCESSOR_BUFFERING(0x10000000)·ADDTO_TRIAGE_DUMP(0x80000000) 입니다.
- 파일 모드 비트가 없어서 이 세션은 `.etl` 파일을 쓰지 않고 이벤트를 실시간으로 넘깁니다.
- "About Event Tracing" 문서는 실시간 소비자가 없을 때 이벤트가 빠지는 예로 이벤트 로그 서비스를 멈췄다 켜는 경우를 듭니다. 다만 EventLog-* 세션을 받는 쪽이 이벤트 로그 서비스라고 직접 적은 공식 문서는 확인하지 못했습니다.
- 로그를 없애려 한 흔적은 [이벤트 로그 삭제](../../../02-artifacts/event-logs/1102-104.md) 와 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) 에서 다룹니다.

## 함정

- `.etl` 은 파일 맨 앞에 고정 서명이 없었습니다(확인 PC). 맨 앞 바이트만으로는 파일 종류를 가려낼 수 없었습니다.
- 문서는 ProviderVersion 을 OS 빌드 번호로 설명합니다. 확인 PC 에서는 이 값이 26100 이었습니다. 같은 PC 의 `ver` 출력은 10.0.26200.9457 이었습니다. 이 값으로 OS 버전을 정하지 않습니다. OS 버전은 [시스템 기본 정보](../../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 확인합니다.
- 문서는 BootTime 을 Global Logger 세션에서만 지원한다고 적습니다. 확인 PC 에서는 Global Logger 가 아닌 LwtNetLog 에도 BootTime 이 채워져 있었습니다. 값이 있으면 읽고, 없으면 그 이유를 따로 확인합니다.
- 레지스트리에 MaxFileSize 가 없다고 제한이 없는 것은 아닙니다. 확인 PC 의 ReFSLog 는 머리에 기본값 100 이 들어 있었습니다.
- 번호 파일 이름은 문서와 다를 수 있습니다. 확인 PC 는 세 자리(`.002`)였습니다. 파일을 찾을 때 자릿수를 정해 두지 않습니다.
- `RtBackup` 파일이 DisableRealtimePersistence 가 저장한 실시간 이벤트라고 적은 공식 문서는 확인하지 못했습니다.
- Analytic·Debug 채널이 `.etl` 로 저장되는지는 이 페이지가 참고한 자료로 확인하지 못했습니다.

## 도구

- Microsoft 문서는 분석 도구의 예로 WPA, PerfView, xperf, tracerpt 를 듭니다. tracerpt 는 Windows 에 기본으로 들어 있습니다.
- 도구가 보여 주는 머리 값(시각·로그 모드·잃은 이벤트 수)을 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 에 있습니다.
- 여러 세션의 시각을 한 줄로 모으는 법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 을 봅니다.

## 참고 문헌

1. Microsoft Learn, "About Event Tracing" — https://learn.microsoft.com/en-us/windows/win32/etw/about-event-tracing
2. Microsoft Learn, "Logging Mode Constants" — https://learn.microsoft.com/en-us/windows/win32/etw/logging-mode-constants
3. Microsoft Learn, "Configuring and Starting an AutoLogger Session" — https://learn.microsoft.com/en-us/windows/win32/etw/configuring-and-starting-an-autologger-session
4. Microsoft Learn, "TRACE_LOGFILE_HEADER structure (evntrace.h)" — https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-trace_logfile_header
5. Joachim Metz, "Windows Event manifest binary format", libyal/libfwevt (문서 버전 0.0.9, 2024-01) — https://raw.githubusercontent.com/libyal/libfwevt/main/documentation/Windows%20Event%20manifest%20binary%20format.asciidoc
