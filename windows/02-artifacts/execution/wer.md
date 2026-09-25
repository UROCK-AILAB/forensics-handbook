---
title: "윈도 오류 보고"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 1090
---

# 윈도 오류 보고 (WER)

## 한 줄 요약

프로그램이 비정상 종료하거나 응답하지 않으면 윈도 오류 보고 (Windows Error Reporting, WER) 가 보고서 폴더와 `Report.wer` 파일을 만듭니다. 같은 사건은 Application 이벤트 로그의 1000·1001·1002 이벤트에도 남습니다. 설정에 따라 덤프 파일도 남습니다. 오류 기록이지만 그 시각에 그 경로의 프로그램이 실행 중이었다는 근거가 됩니다.

## 무엇을 기록하나 · 왜 생기나

WER 은 프로그램 오류를 모아 보고하는 Windows 기능입니다. 오류가 나면 보고서 폴더가 생기고 그 안에 `Report.wer` 가 들어가며, 이 파일에는 실행 파일 경로, 버전, 오류 모듈, 예외 코드, 그때 불러온 모듈 목록이 들어 있습니다. 같은 사건을 Application 이벤트 로그에도 기록합니다.

| 이벤트 ID | 공급자 | 담는 것 |
|---|---|---|
| 1000 | Application Error | 오류 난 프로그램의 이름·버전·타임스탬프, 오류 모듈, 예외 코드, 오류 오프셋, 프로세스 ID(16진), 프로그램 시작 시각(16진 FILETIME), 프로그램 경로, 모듈 경로, Report Id |
| 1001 | Windows Error Reporting | Fault bucket, Event Name, 문제 서명 P1~P10, 붙인 파일 목록 (Attached files), 보고서 폴더 경로, Report Id, Report Status, Hashed bucket |
| 1002 | Application Hang | 응답 없음 |

- 로컬 덤프 (LocalDumps) 를 켜면 오류 순간의 프로세스 덤프가 파일로 남습니다.
- 커널 쪽 보고서는 라이브 커널 보고서 (Live Kernel Reports) 폴더에 남습니다.

## 위치와 버전별 차이

### 파일 위치

| 무엇 | 위치 |
|---|---|
| 시스템 보고서 폴더 | `C:\ProgramData\Microsoft\Windows\WER\` 아래 `ReportArchive`, `ReportQueue`, `Temp` |
| 사용자별 보고서 폴더 | `%LOCALAPPDATA%\Microsoft\Windows\WER`. 없을 수도 있습니다 |
| 로컬 덤프 (기본) | `%LOCALAPPDATA%\CrashDumps` |
| 서비스 크래시 덤프 | 서비스 계정 프로필 폴더. System 서비스는 `%WINDIR%\System32\Config\SystemProfile`, Network·Local Service 는 `%WINDIR%\ServiceProfiles` |
| 라이브 커널 보고서 | `%systemroot%\LiveKernelReports` |

- 예전 Windows 에서 사용자별 보고서 폴더를 쓰는지는 검체에서 확인합니다.

### 설정 위치

- WER 설정은 `HKCU\Software\Microsoft\Windows\Windows Error Reporting` 과 `HKLM\Software\Microsoft\Windows\Windows Error Reporting` 에 있습니다.
- 로컬 덤프 설정은 `HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps` 에 있습니다. HKCU 에서는 지원하지 않습니다.

### Windows 버전

| Windows | 달라지는 점 |
|---|---|
| Windows Vista | `ConfigureArchive` 기본값이 2 (모든 데이터) 입니다 |
| Windows Vista SP1, Windows Server 2008 부터 | 로컬 덤프를 모을 수 있습니다 |
| Windows 7 | `ConfigureArchive` 기본값이 1 (매개변수만) 입니다 |
| Windows 10 1607 이하 | 라이브 커널 보고서 설정 키가 `HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting` 입니다 |
| Windows 10 1703 이상 | 라이브 커널 보고서 설정 키가 `HKLM\SYSTEM\CurrentControlSet\Control\CrashControl` 입니다 |

- 오프라인 SYSTEM 하이브에는 `CurrentControlSet` 이 없습니다. 실제 쓰인 컨트롤셋을 고르는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.

## 구조

### 보고서 폴더

아래 수치는 PC 한 대의 예입니다.

- 폴더 수는 `ReportArchive` 254개, `ReportQueue` 1개, `Temp` 0개였습니다.
- 보고서 폴더 이름의 앞머리는 아래와 같았습니다.

| 앞머리 | 폴더 수 |
|---|---|
| `NonCritical` | 121 |
| `AppHang` | 64 |
| `AppCrash` | 46 |
| `Critical` | 23 |
| `Kernel` | 1 |

- `AppCrash` 폴더 이름은 `AppCrash_<프로그램 이름>_<16진 40자>_<16진 8자>_<GUID>` 모양이었습니다.
- 프로그램 이름이 길면 잘려서 `.exe` 가 `.ex` 로 끝났습니다.
- 폴더 이름 끝의 GUID 는 그 안 `Report.wer` 의 `ReportIdentifier` 와 같았습니다. 가운데 16진 40자와 8자가 무엇의 해시인지는 공개 자료에 없습니다.
- `ReportArchive` 폴더 254개에는 모두 `Report.wer` 하나만 있었습니다.
- 이벤트 1001 이 붙인 파일로 적은 덤프·XML·CSV·TXT 는 `WER\Temp` 에 있었는데, `Temp` 는 비어 있었습니다. 보고서를 보낸 뒤 지운 것으로 보입니다.

### Report.wer

- 첫 두 바이트는 `FF FE` (UTF-16 LE BOM) 입니다.
- 한 줄에 `키=값` 하나가 들어가고 줄 끝은 CRLF 입니다.

| 묶음 | 키 | 내용 |
|---|---|---|
| 사건 | `EventType` | `APPCRASH`, `BEX64` 같은 값 |
| | `EventTime`, `UploadTime` | 10진수 FILETIME (UTC) |
| | `ReportIdentifier` | 보고서 폴더 이름 끝의 GUID 와 같음 |
| | `IntegratorReportIdentifier` | 이벤트 1000·1001 의 Report Id 와 같음 |
| | `ReportType`, `ReportStatus`, `Consent`, `IsFatal`, `BootId` | 공개 자료 없음 |
| 프로그램 | `AppPath` | 실행 파일 전체 경로 |
| | `TargetAppId` | `W:<16진>!0000<16진 40자>!<프로그램 이름>` 모양. 가운데 값의 뜻은 공개 자료에 없습니다 |
| | `AppName`, `OriginalFilename`, `TargetAppVer`, `NsAppName`, `ApplicationIdentity`, `AppSessionGuid` | 공개 자료 없음 |
| 오류 서명 | `Sig[n].Name`, `Sig[n].Value` | 프로그램 이름·버전·타임스탬프, 오류 모듈 이름·버전, 예외 코드(예: `e0434352`, `c0000409`), 예외 오프셋 |
| | `DynamicSig[n].Name`, `DynamicSig[n].Value` | 공개 자료 없음 |
| 모듈 | `LoadedModule[n]` | 오류 당시 불러온 모듈 경로. 한 보고서에 95개가 있었습니다 |
| 서버 응답 | `Response.BucketId` | 이벤트 1001 의 Hashed bucket 과 같음 |
| | `Response.BucketTable`, `Response.LegacyBucketId`, `Response.type` | 공개 자료 없음 |
| 그 밖 | `Version`, `FeatureStaging`, `Wow64Host`, `TargetAsId`, `EtwNonCollectReason`, `UI[n]`, `State[n].Key/Value`, `OsInfo[n].Key/Value`, `FriendlyEventName`, `ConsentKey`, `NsPartner`, `NsGroup`, `MetadataHash` | 공개 자료 없음 |

- `Sig[n].Name` 은 OS 표시 언어로 적혔습니다. 한국어 PC 에서는 "응용 프로그램 이름", "오류 모듈 이름", "예외 코드", "예외 오프셋" 처럼 나왔습니다.
- `UploadTime` 이 보고서를 보낸 시각인지는 공개 자료에 없습니다.

### 이벤트와 보고서를 잇는 값

| 이 값이 | 이 값과 같았습니다 |
|---|---|
| 이벤트 1000 의 Report Id | 이벤트 1001 의 Report Id, `Report.wer` 의 `IntegratorReportIdentifier` |
| 이벤트 1001 의 Hashed bucket | `Report.wer` 의 `Response.BucketId` |
| 보고서 폴더 이름 끝 GUID | `Report.wer` 의 `ReportIdentifier` |
| 덤프 파일 이름의 PID (10진) | 이벤트 1000 의 Faulting process id (16진) |

- 이벤트 1001 의 "These files may be available here:" 뒤에는 `ReportArchive` 폴더 경로가 적혔습니다.

### 로컬 덤프 설정 (LocalDumps)

| 값 | 형식 | 기본값 | 뜻 |
|---|---|---|---|
| `DumpFolder` | REG_EXPAND_SZ | `%LOCALAPPDATA%\CrashDumps` | 덤프를 둘 폴더 |
| `DumpCount` | REG_DWORD | 10 | 덤프 수가 이 값을 넘으면 가장 오래된 덤프를 새 덤프로 바꿉니다 |
| `DumpType` | REG_DWORD | 1 | 0 사용자 지정, 1 미니 덤프, 2 전체 덤프 |
| `CustomDumpFlags` | REG_DWORD | | `DumpType` 이 0 일 때만 씁니다 |

- 로컬 덤프는 기본으로 꺼져 있습니다. 켜려면 관리자 권한이 필요합니다.
- `LocalDumps\MyApplication.exe` 처럼 프로그램별 하위 키를 만들 수 있습니다. 그 프로그램이 멈추면 WER 은 전역 설정을 먼저 읽고, 하위 키에 있는 값으로 덮어씁니다.
- WER 이 꺼져 있거나 사용자가 보고를 취소해도 로컬 덤프는 모입니다.
- 자체 크래시 보고를 하는 프로그램은 대상이 아닙니다.
- 응용 프로그램 자동 디버깅이 설정되어 있으면 덤프를 모으지 않습니다.

아래는 PC 한 대의 예입니다.

- `LocalDumps` 키는 있었고, 키 자체에는 값이 없었습니다. 하위 키는 한 제조사의 프로그램 27개뿐이었습니다.
- 그런데도 `%LOCALAPPDATA%\CrashDumps` 에 하위 키가 없는 프로그램의 덤프가 10개 있었습니다. 기본 `DumpCount` 와 같은 수입니다.
- 덤프 파일 이름은 `<프로그램>.exe.<PID>.dmp` 모양이었고, 첫 4바이트는 `MDMP` 였습니다.
- "`LocalDumps` 키가 값 없이 있기만 해도 전역 덤프가 켜진다" 는 해석이 있고, 위 예도 이 해석과 어긋나지 않습니다.

### WER 설정 값

| 값 | 뜻 |
|---|---|
| `Disabled` | 0 사용 (기본), 1 이면 WER 을 끕니다 |
| `LoggingDisabled` | 0 사용 (기본), 1 이면 로깅 (Logging) 을 끕니다 |
| `DisableArchive` | 0 사용, 1 이면 보관을 끕니다 |
| `DisableQueue` | 대기열에 관한 값입니다 |
| `ConfigureArchive` | 1 매개변수만 보관, 2 모든 데이터 보관 |
| `MaxArchiveCount` | 보관할 보고서 수. 범위 1~5000, 기본 1000 |
| `MaxQueueCount` | 대기열 보고서 수. 범위 1~500, 기본 50 |
| `Consent\DefaultConsent` | 1 항상 묻기 (기본), 2 매개변수만, 3 매개변수와 안전한 데이터, 4 모든 데이터 |
| `ExcludedApplications\[프로그램 이름]` | 보고에서 뺄 프로그램 |

## 증거로서 의미

### 증명하는 것

- `Report.wer` 와 이벤트 1000 은 그 시각에 그 경로의 프로그램이 실행 중이었다는 근거입니다. 오류는 실행 중인 프로그램에서만 나며, 프로그램 버전, 오류 모듈, 예외 코드도 알려 줍니다.
- `LoadedModule[n]` 은 오류 순간에 그 프로세스가 불러온 모듈 목록입니다. 뜻밖의 DLL 이 들어 있는지 볼 수 있습니다.
- 이벤트 1000 의 프로그램 시작 시각으로 그 프로세스가 언제 시작했는지 알 수 있습니다.
- 덤프 파일은 오류 순간 프로세스의 메모리를 담습니다. 담는 범위는 `DumpType` 에 따릅니다. 읽는 법은 [메모리 분석](../../03-techniques/analysis/memory-forensics/index.md) 에서 다룹니다.
- 로컬 덤프 기본 폴더는 사용자 프로필 아래입니다. 덤프가 어느 프로필 폴더에 있는지로 사용자를 좁힐 수 있습니다.

### 증명하지 못하는 것

- 누가 실행했는지는 `Report.wer` 만으로 알 수 없습니다. `Report.wer` 에는 사용자 이름을 담은 키가 없습니다. `AppPath` 가 사용자 프로필 아래면 그 경로로 가늠합니다.
- 오류의 원인과 프로그램이 악성인지는 알 수 없습니다.
- 정상으로 실행하고 끝난 프로그램은 남지 않습니다.
- 보고서가 없다고 오류가 없었던 것은 아닙니다. `Disabled`, `ExcludedApplications`, 보관 개수 한도, 사용자의 삭제로 빠질 수 있습니다.
- 무엇을 밖으로 보냈는지는 알 수 없습니다.

보고서에는 "그 프로그램을 실행했다" 대신 "`ReportArchive` 의 보고서 R 에 `AppPath` X, `EventType` APPCRASH, `EventTime` A(UTC) 가 적혀 있다. 같은 Report Id 의 이벤트 1000 이 있다" 처럼 씁니다.

## 시각 해석

| 시각 | 형식 | 관계 |
|---|---|---|
| `Report.wer` 의 `EventTime` | 10진수 FILETIME (UTC) | 한 보고서는 이벤트 1000 의 기록 시각보다 0.1초 늦었습니다. 다른 보고서는 보고서 폴더를 만든 시각보다 약 2.6초 빨랐습니다 |
| 이벤트 1000 의 프로그램 시작 시각 | 16진수 FILETIME (UTC) | 한 예에서 오류보다 5초 앞섰습니다 |
| 이벤트 1000 과 1001 의 기록 시각 | 이벤트 로그 시각 | 1000 이 1001 보다 약 3초 먼저 기록됐습니다 |
| 덤프 파일의 수정 시각 | 파일 시스템 시각 | 이벤트 1001 과 같은 초였습니다 |

- FILETIME 변환은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.
- 보고서 파일은 이벤트 로그보다 오래 남을 수 있습니다. Application 로그의 가장 오래된 이벤트보다 약 한 달 앞선 보고서가 `ReportArchive` 에 남은 예가 있습니다.
- 이벤트 로그가 돌아서 지워졌으면 `Report.wer` 의 `EventTime` 으로 사건 시각을 잡습니다.

## 함정과 한계

- **이벤트 1001 만 보고 크래시로 단정하지 않습니다.** PC 한 대의 Application 로그에는 1001 이 364건, 1002 가 14건, 1000 이 8건 있었습니다. 1001 의 Event Name 을 보고 어떤 보고서인지 가립니다.
- **서명 이름은 OS 언어를 따릅니다.** `Sig[n].Name` 이 한국어로 적힐 수 있습니다. 영어 이름으로 검색하면 놓칩니다. `Sig[n].Value` 를 번호로 읽습니다.
- **폴더 이름의 프로그램 이름은 잘립니다.** 전체 경로는 `AppPath` 로 봅니다.
- **붙인 파일은 사라질 수 있습니다.** `ReportArchive` 에 `Report.wer` 만 남는 경우가 있습니다. 덤프 같은 붙인 파일이 없다고 수집을 빠뜨린 것은 아닙니다.
- **폴더 이름의 16진 값을 파일 해시로 쓰지 않습니다.** 폴더 이름의 16진 40자와 `TargetAppId` 가운데 값이 무엇인지는 공개 자료에 없습니다.
- **PID 는 10진과 16진으로 다르게 적힙니다.** 덤프 이름은 10진, 이벤트 1000 은 16진입니다. 한쪽으로 바꿔 맞춥니다.
- **설정 값을 원시 바이트로 확인합니다.** REG_DWORD 를 글자로 보여 주는 도구는 부호 없는 10진수로 보여 줍니다. 헷갈리면 원시 바이트를 봅니다.
- **지우기와 끄기.** 사용자가 보고서 폴더와 덤프를 지울 수 있습니다. `Disabled`, `ExcludedApplications`, `DisableArchive` 로 기록을 막을 수도 있습니다. 설정 키의 값과 마지막 기록 시각을 함께 봅니다. 지운 보고서는 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 과 [마스터 파일 테이블](../filesystem/mft.md) 에서 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 위 형식으로 만든 예시입니다. 특정 검체에서 나온 값이 아닙니다. BOM 바로 뒤에 `EventType=APPCRASH` 한 줄이 온다고 두었습니다. 실제 파일에서는 줄 순서가 다를 수 있습니다.

```
FF FE 45 00 76 00 65 00 6E 00 74 00 54 00 79 00   ..E.v.e.n.t.T.y.
70 00 65 00 3D 00 41 00 50 00 50 00 43 00 52 00   p.e.=.A.P.P.C.R.
41 00 53 00 48 00 0D 00 0A 00                     A.S.H.....
```

- `FF FE` 는 UTF-16 LE BOM 입니다.
- `3D 00` 은 `=` 입니다. 키와 값을 나눕니다.
- 줄 끝은 `0D 00 0A 00` 입니다.

`EventTime` 과 이벤트 1000 의 프로그램 시작 시각을 푸는 예시입니다. 역시 만든 값입니다.

```
EventTime=133549686000000000
133549686000000000 ÷ 10,000,000 − 11644473600 = 1710495000 → 2024-03-15 09:30:00 UTC

프로그램 시작 시각 0x01DA76BB56EA2B80
= 133549685950000000 → 2024-03-15 09:29:55 UTC (오류 5초 전)
```

덤프 파일은 첫 4바이트로 알아봅니다.

```
4D 44 4D 50    "MDMP"
```

### 공개 도구로 한 번

Application 로그를 사본으로 떠서 Windows PowerShell 에서 읽습니다.

```powershell
Get-WinEvent -FilterHashtable @{ Path = '.\Application.evtx'; Id = 1000, 1001, 1002 } |
  Select-Object @{ n = 'UtcTime'; e = { $_.TimeCreated.ToUniversalTime() } },
                Id, ProviderName, Message
```

- `TimeCreated` 는 분석 PC 의 현지 시각으로 나옵니다. 위처럼 UTC 로 바꿔 적습니다.

보고서 폴더를 사본으로 뜬 뒤 필요한 키만 뽑습니다.

```powershell
Get-ChildItem .\ReportArchive -Recurse -Filter Report.wer |
  Select-String -Encoding Unicode `
    -Pattern '^(EventType|EventTime|AppPath|ReportIdentifier|IntegratorReportIdentifier)='

[DateTime]::FromFileTimeUtc(133549686000000000)
[DateTime]::FromFileTimeUtc(0x01DA76BB56EA2B80)
```

- 결과의 `IntegratorReportIdentifier` 로 이벤트 1000·1001 의 Report Id 를 찾아 짝짓습니다.
- 덤프 파일은 WinDbg 같은 공개 디버거로 엽니다.
- 이벤트 로그 파일 구조는 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 프로그램 호환성 도우미 | `Abnormal process exit` 줄로 같은 비정상 종료 | [프로그램 호환성 도우미](pca.md) |
| AmCache | 같은 경로의 파일 정보 | [AmCache](amcache-hve/index.md) |
| 프리페치 | 실행 횟수와 실행 시각 | [프리페치](prefetch/index.md) |
| 프로세스 생성 이벤트 | 같은 프로세스가 뜬 시각과 부모 프로세스 | [프로세스 생성](../event-logs/4688.md) |
| 메모리 분석 | 덤프 파일 읽기 | [메모리 분석](../../03-techniques/analysis/memory-forensics/index.md) |

실행 흔적 전체를 엮는 흐름은 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 에 있습니다. 악성 프로그램이 오류로 멈춘 흔적을 찾을 때는 [악성코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md) 를 함께 봅니다.

## 실습

공개 검체(NIST CFReDS 등)에서 `C:\ProgramData\Microsoft\Windows\WER\` 폴더와 Application 로그를 꺼내 풀어 봅니다.

1. `ReportArchive` 와 `ReportQueue` 에 보고서가 몇 개 있습니까? 폴더 이름의 앞머리별로 세어 봅니다.
2. `AppCrash` 보고서 하나를 골라 `AppPath`, `EventTime`, 예외 코드를 적습니다. `EventTime` 은 UTC 로 언제입니까?
3. 그 보고서의 `IntegratorReportIdentifier` 와 Report Id 가 같은 이벤트 1000·1001 이 있습니까? 이벤트가 없다면 로그가 돌아서 지워졌습니까?
4. 이벤트 1000 의 프로그램 시작 시각을 풉니다. 오류보다 얼마나 앞섭니까?
5. `LocalDumps` 키와 `CrashDumps` 폴더가 있습니까? 덤프 이름의 PID 가 이벤트 1000 의 프로세스 ID 와 맞습니까?
6. `Disabled`, `ExcludedApplications` 같은 설정 값이 있습니까?

## 참고 문헌

1. Microsoft Learn, *Collecting User-Mode Dumps* (로컬 덤프 지원 버전, `LocalDumps` 키와 값, 기본값, 서비스 덤프 위치, 덤프를 모으지 않는 경우). https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps
2. Microsoft Learn, *WER Settings* (설정 위치, `Disabled`·`LoggingDisabled`·`DisableArchive`·`DisableQueue`·`ConfigureArchive`·`MaxArchiveCount`·`MaxQueueCount`·`DefaultConsent`·`ExcludedApplications`, HKCU 의 `LocalDumps` 미지원, 라이브 커널 보고서 설정). https://learn.microsoft.com/en-us/windows/win32/wer/wer-settings
