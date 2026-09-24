# 시간 변경 (4616·Kernel-General)

## 한 줄 요약

시스템 시각이 바뀌면 보안 로그에 4616 이, 시스템 로그에 Kernel-General 1 이 남습니다. 두 이벤트 모두 바뀌기 전 시각과 바뀐 뒤 시각을 UTC 로 적습니다. 4616 은 감사 정책 설정과 상관없이 늘 남습니다. Kernel-General 1 에는 바꾼 까닭 (Reason) 과 바뀐 폭이 더 들어 있습니다. 대부분은 Windows 시간 서비스가 하는 보정이므로, 먼저 어느 계정과 어느 프로세스가 바꿨는지를 봅니다.

## 무엇을 기록하나 · 왜 생기나

### 보안 로그 4616

- 제목은 "4616(S) The system time was changed." 입니다.
- 시스템 시각이 바뀔 때마다 생깁니다.
- 하위 범주는 보안 상태 변경 감사 (Audit Security State Change) 입니다. 그러나 이 하위 범주를 어떻게 설정하든 늘 남습니다.
- Subject 칸은 시스템 시각 바꾸기를 요청한 계정입니다.
- Microsoft 문서는 Subject 가 LOCAL SERVICE 인 4616 을 흔히 보는 정상 보정이라고 적습니다.

### 시스템 로그 Kernel-General 1

- 공급자는 Microsoft-Windows-Kernel-General 이고, 채널은 System 입니다.
- 메시지 틀은 "The system time has changed to %1 from %2." 입니다. 버전 1 부터 "Change Reason: %3." 이 붙습니다 (확인 범위: Win11 25H2 한 대의 공급자 템플릿).
- Reason 칸은 시각을 바꾼 까닭을 숫자로 적습니다. 공개 도구 EvtxECmd 의 맵은 아래처럼 풉니다.

| Reason | 맵의 풀이 |
|---|---|
| 1 | 앱이나 시스템 구성 요소가 시각을 바꿈 |
| 2 | 하드웨어 시계 (RTC) 와 맞춤 |
| 3 | 새 시간대로 맞춤 |
| 그 밖 | "Unknown code" |

- 맵은 근거로 다른 사이트의 이벤트 설명 페이지를 적었습니다. 그 페이지와 Microsoft 공식 문서의 Reason 표는 확인하지 못했습니다.

조사한 PC 의 Kernel-General 1 은 199건이었습니다. Reason 마다 모습이 달랐습니다 (확인 범위: Win11 25H2 한 대).

| Reason | 건수 | ProcessName | 기록 계정 | 언제 |
|---|---|---|---|---|
| 1 | 187 | `\Device\HarddiskVolume3\Windows\System32\svchost.exe` | `S-1-5-19` (LOCAL SERVICE) | 평소 |
| 2 | 10 | 빈 값 (ProcessID 4) | 없음 | 모두 절전·최대 절전에서 깨어날 때 |
| 3 | 2 | `msoobe.exe`, `CloudExperienceHostBroker.exe` | `S-1-5-18` (SYSTEM) | OOBE (첫 설정) 때. TimeDeltaInMs 0 |

- Reason 2 뒤 몇 초 안에 Kernel-Boot 18·25·27·30·32, Kernel-Power 506·507·566(또는 105·107), Power-Troubleshooter 1 이 뒤따랐습니다.
- 관찰은 맵의 풀이와 맞습니다. 2 는 깨어날 때 하드웨어 시계에서 시각을 다시 읽은 것으로, 3 은 설치 중 시간대를 정한 것으로 보입니다.

### 같은 공급자의 다른 시각 이벤트

Kernel-General 공급자는 시각과 관련된 이벤트를 더 남깁니다. 메시지 틀과 칸은 공급자 템플릿에서 읽었습니다 (확인 범위: Win11 25H2 한 대).

| ID | 메시지 틀 | 주요 칸 |
|---|---|---|
| 12 | "The operating system started at system time %7." | StartTime 등 |
| 13 | "The operating system is shutting down at system time %1." | StopTime |
| 20 | 윤초 설정 변경 | |
| 24 | "The time zone information was refreshed … Current time zone bias is %2." | ExitReason, CurrentBias, CurrentTimeZoneID 등 |
| 25 | "The system time was initialized to %1." | SystemTime, LoaderTime, HalRtcErrorCode, RealTimeIsUniversal, IsSoftBoot 등 |

- 16 "The access history in hive %2 was cleared …" 도 같은 공급자입니다. 시각 변경과는 관계가 없습니다.
- 12·13 으로 켜짐·꺼짐을 읽는 법은 [켜짐·꺼짐](/02-artifacts/event-logs/power-on-off-events.md)에서 다룹니다.

## 위치와 버전별 차이

### 공급자와 로그

| 항목 | 4616 | Kernel-General 1 |
|---|---|---|
| 로그 (채널) | 보안 (Security) | 시스템 (System) |
| 공급자 | Microsoft-Windows-Security-Auditing | Microsoft-Windows-Kernel-General |
| 공급자 GUID | `{54849625-5478-4994-A5BA-3E3B0328C30D}` | 확인하지 않음 |
| Task | 12288 (Microsoft 예시) | SystemTimeChange. 맵 예시 값은 5 |
| Keywords | `0x8020000000000000` (Microsoft 예시) | KERNEL_GENERAL_KEYWORD_TIME. 맵 예시 값은 `0x8000000000000010` |
| 최소 OS | Windows Vista · Windows Server 2008 | 확인하지 못함 |

### 4616 의 이벤트 버전

| 버전 | Windows | 달라진 점 |
|---|---|---|
| 0 | Windows Server 2008 · Windows Vista | |
| 1 | Windows Server 2008 R2 · Windows 7 | "Process Information" 절(ProcessId, ProcessName)이 더해졌습니다 |

### Kernel-General 1 의 이벤트 버전

공급자 템플릿에는 버전 0~4 가 있었습니다 (확인 범위: Win11 25H2 한 대).

| 버전 | 더해진 칸 |
|---|---|
| 0 | NewTime, OldTime (FILETIME) |
| 1 | Reason (UInt32) |
| 2 | ProcessName (문자열), ProcessID (UInt32, 10진) |
| 3 | CmosTime (FILETIME), TimeZoneBias (Int32), RealTimeIsUniversal (Boolean), SystemInCmosMode (Boolean) |
| 4 | TimeDeltaInMs (Int64, 밀리초) |

- 버전마다 어느 Windows 빌드에서 쓰이는지는 확인하지 못했습니다.
- EvtxECmd 맵의 예시(2020년)는 버전 2 였습니다.
- 조사한 PC(Win11 25H2)의 199건은 모두 버전 4 였습니다.

### 로그 보존 기간

조사한 PC 에서 보안 로그(20MB)는 약 2일치, 시스템 로그(20MB)는 약 3개월치가 남아 있었습니다 (확인 범위: Win11 25H2 한 대). 4616 이 밀려난 뒤에도 Kernel-General 1 은 남아 있을 수 있습니다.

## 구조

### 4616 칸

| 칸 | 뜻 |
|---|---|
| SubjectUserSid · SubjectUserName · SubjectDomainName | 시스템 시각 바꾸기를 요청한 계정입니다 |
| SubjectLogonId | 그 계정의 로그온 ID 입니다. 16진 64비트 정수 (HexInt64) 로, 4624 의 같은 로그온 ID 와 이을 수 있습니다 |
| PreviousTime | 바뀌기 전 시각입니다. FILETIME 을 UTC 로 적습니다 |
| NewTime | 바뀐 뒤 시각입니다. FILETIME 을 UTC 로 적습니다 |
| ProcessId | 시각을 바꾼 프로세스의 ID 입니다. 16진으로 적습니다. 4688 의 New Process ID 와 이을 수 있습니다 |
| ProcessName | 그 프로세스의 실행 파일 경로입니다 |

PreviousTime·NewTime 의 표시 형식은 `YYYY-MM-DDThh:mm:ss.nnnnnnnZ` 입니다.

### Kernel-General 1 칸 (버전 4)

칸은 아래 순서로 들어 있습니다.

| 순서 | 칸 | 형식 | 뜻 |
|---|---|---|---|
| 1 | NewTime | FILETIME | 바뀐 뒤 시각 |
| 2 | OldTime | FILETIME | 바뀌기 전 시각 |
| 3 | TimeDeltaInMs | Int64 | 바뀐 폭(밀리초). 음수면 시각을 뒤로 돌린 것입니다 |
| 4 | Reason | UInt32 | 바꾼 까닭 |
| 5 | ProcessName | 문자열 | 바꾼 프로세스. `\Device\HarddiskVolume…` 모양의 경로입니다 |
| 6 | ProcessID | UInt32 | 바꾼 프로세스의 ID. 10진입니다 |
| 7 | CmosTime | FILETIME | 하드웨어 시계의 시각 |
| 8 | TimeZoneBias | Int32 | 시간대 차이(분). 부호가 있습니다 |
| 9 | RealTimeIsUniversal | Boolean | 하드웨어 시계가 UTC 인지 |
| 10 | SystemInCmosMode | Boolean | |

- 칸 이름과 형식은 공급자 템플릿에서 읽었습니다 (확인 범위: Win11 25H2 한 대).
- "뜻" 은 칸 이름과 관찰한 값으로 풀었습니다. SystemInCmosMode 의 뜻은 확인하지 못했습니다.

### Microsoft 의 4616 예시 값

| 칸 | 값 |
|---|---|
| Version | 1 |
| Execution ProcessID | 4 |
| PreviousTime | `2015-10-09T05:04:30.000941900Z` |
| NewTime | `2015-10-09T05:04:30.000000000Z` |
| ProcessName | `…\WinSxS\amd64_microsoft-windows-com-surrogate-core_…\dllhost.exe` |

예시의 NewTime 은 PreviousTime 보다 0.0009419초 앞선 시각입니다. 시각을 아주 조금 뒤로 돌린 기록입니다.

### 두 이벤트의 짝

조사한 PC 에서 보안 로그가 남아 있던 기간(2026-09-21T22:39Z 이후)에 두 이벤트를 맞대 봤습니다 (확인 범위: Win11 25H2 한 대).

- Kernel-General 1 이 4건, 4616 이 4건이었고 하나씩 짝이 맞았습니다.
- 짝끼리 기록 시각 차이는 1ms 미만이었습니다.
- 4616 의 PreviousTime·NewTime 과 Kernel-General 1 의 OldTime·NewTime 이 100ns 단위까지 같았습니다.
- 4616 4건은 모두 버전 1 이었습니다. SubjectUserSid 는 `S-1-5-19`(LOCAL SERVICE), SubjectLogonId 는 `0x3e5`, ProcessName 은 `C:\Windows\System32\svchost.exe` 였습니다.

같은 변경인데 적는 방식이 다릅니다.

| 항목 | 4616 | Kernel-General 1 |
|---|---|---|
| 바뀌기 전·뒤 칸 이름 | PreviousTime · NewTime | OldTime · NewTime |
| 프로세스 경로 | `C:\Windows\System32\svchost.exe` | `\Device\HarddiskVolume3\Windows\System32\svchost.exe` |
| 프로세스 ID | `0x1768` (16진) | `5992` (10진) |
| 까닭·폭 | 없음 | Reason, TimeDeltaInMs |

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 기록된 시각에 시스템 시각이 PreviousTime 에서 NewTime 으로 바뀌었습니다 | 계정 뒤의 사람이 누구인지 |
| 시각 바꾸기를 요청한 계정과 로그온 ID, 프로세스 (4616) | Reason 1 이 사람이 손으로 바꾼 것인지. 앱과 시스템 구성 요소가 바꿔도 1 입니다 |
| 바꾼 까닭의 분류와 바뀐 폭·방향 (Kernel-General 1) | 기록이 없으니 시각이 바뀌지 않았다는 것. 로그가 밀려났을 수 있습니다 |
| 깨어날 때의 보정인지 (Reason 2 와 전원 이벤트) | 그 사이 다른 기록의 시각이 모두 틀렸다는 것. 어떤 기록이 영향을 받는지는 기록마다 따로 봅니다 |

### 보고서 문장

아래 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "시스템 로그에는 <시각> UTC 에 Kernel-General 1 이 있습니다. 시스템 시각이 <OldTime> 에서 <NewTime> 으로 약 ○시간 뒤로 바뀌었고, Reason 은 1, 프로세스는 ○○ 입니다. 보안 로그의 4616 은 같은 변경을 계정 ○○ (로그온 ID ○○) 이 요청했다고 적습니다."
- 쓰면 안 되는 문장: "○○ 이 증거를 숨기려고 시각을 조작했다."

두 번째 문장은 사람과 의도를 단정합니다. 이벤트에는 계정과 프로세스와 시각만 있습니다.

## 시각 해석

- 이벤트 시각은 `<TimeCreated SystemTime>` 에 들어 있습니다. 끝에 Z 가 붙은 UTC 값입니다.
- PreviousTime·NewTime·OldTime 도 UTC 입니다.
- CmosTime 도 끝에 Z 를 붙여 보여 줍니다. 그러나 RealTimeIsUniversal 이 false 이면 현지 시각입니다. 조사한 PC 에서는 CmosTime 이 NewTime 에 9시간을 더한 값이었습니다 (확인 범위: Win11 25H2 한 대).
- TimeZoneBias 는 부호 있는 32비트 값입니다. 조사한 PC 에서는 -540(UTC+9)이었습니다.
- TimeDeltaInMs 는 음수가 될 수 있습니다. 조사한 PC 에서 -1995 는 약 2초 뒤로 돌린 것이었고, 깨어날 때 121010 은 약 2분 앞으로 옮긴 것이었습니다. 뒤로 간 변경을 찾을 때는 이 칸의 부호를 봅니다.
- 현지 시각으로 바꿀 때는 [시간대 설정](/02-artifacts/system-account/time-zone.md)을 씁니다.
- 시각을 되돌리면, 레코드 번호는 늘어나는데 기록 시각은 거꾸로 가는 곳이 생길 수 있습니다. 이 방법으로 되돌림을 찾을 수 있는지는 확인하지 못했습니다. "실습" 에서 직접 확인해 봅니다.
- 여러 기록의 시각을 한 기준으로 맞추는 법은 [타임라인 작성](/03-techniques/analysis/timeline/index.md)에서 다룹니다.

## 함정과 한계

1. **4616 을 모두 의심합니다.** Subject 가 LOCAL SERVICE 이고 프로세스가 `svchost.exe` 인 4616 은 흔히 보는 시간 서비스 보정입니다.
2. **Reason 2 를 조작으로 읽습니다.** 조사한 PC 의 Reason 2 는 모두 절전에서 깨어날 때 남았습니다. 몇 초 안의 Kernel-Boot·Kernel-Power 이벤트와 함께 봅니다.
3. **Reason 1 을 사람의 손으로 읽습니다.** 시간 서비스의 보정도 Reason 1 이었습니다. ProcessName 과 기록 계정을 함께 봅니다.
4. **프로세스 경로를 글자 그대로 맞춥니다.** 4616 은 드라이브 문자 경로, Kernel-General 1 은 `\Device\HarddiskVolume…` 경로입니다.
5. **프로세스 ID 의 진법을 섞습니다.** 4616 은 16진, Kernel-General 1 은 10진입니다. `0x1768` 과 `5992` 는 같은 값입니다.
6. **4616 이 없으니 시각 변경도 없었다고 봅니다.** 보안 로그는 빨리 밀려납니다. 시스템 로그의 Kernel-General 1 을 따로 찾습니다.
7. **깨어날 때도 4616 이 남는다고 봅니다.** 조사한 PC 에서는 보안 로그가 그 기간까지 남아 있지 않았습니다. Reason 2 때 4616 이 남는지는 확인하지 못했습니다.
8. **TimeZoneBias 를 부호 없이 읽습니다.** -540 을 부호 없는 32비트로 읽으면 4294966756 이 됩니다. 레지스트리의 시간대 Bias 값도 같은 함정이 있습니다.
9. **CmosTime 의 Z 를 믿습니다.** RealTimeIsUniversal 을 먼저 봅니다.
10. **Kernel-General 16 을 시각 기록으로 읽습니다.** 16 은 하이브의 접근 기록을 지운 이벤트입니다.
11. **Reason 표를 공식 값으로 씁니다.** 이 페이지의 Reason 풀이는 EvtxECmd 맵의 것입니다. 보고서에는 출처를 밝힙니다.

### 지우기와 조작

Microsoft 문서는 4616 을 이렇게 지켜보라고 권합니다.

- Subject 가 LOCAL SERVICE 가 아닌 4616 을 보고합니다.
- ProcessName 이 `C:\Windows\System32\svchost.exe` 가 아닌 4616 을 보고합니다. 시간 서비스가 한 변경이 아니라는 뜻입니다.
- 표준 폴더 밖에서 실행된 프로세스를 봅니다.
- 프로세스 이름에 `mimikatz`, `cain.exe` 같은 문자열이 있는지 봅니다.

그 밖에 알아 둘 것입니다.

- 시스템 시각을 바꾸려면 시스템 시각 변경 권한 (SeSystemtimePrivilege) 이 있어야 합니다. 이 권한을 기본으로 받는 계정은 [시스템 시각을 바꿨나](/04-scenarios/activity/anti-forensics/system-time-change.md)에서 다룹니다.
- 보안 로그를 지워도 시스템 로그의 Kernel-General 1 은 따로 남습니다. 로그를 지운 기록은 [이벤트 로그 삭제](/02-artifacts/event-logs/1102-104.md)에서 찾습니다.
- 조사한 PC 에는 Microsoft-Windows-Time-Service/Operational 로그도 켜져 있었습니다(1MB, 764건, ID 257~266·272). 각 ID 의 뜻은 확인하지 못했습니다.

## 직접 분석해 보기

### 헥스로 한 번

PreviousTime·NewTime·OldTime 은 FILETIME 입니다. 값을 시각으로 바꾸는 법은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다. 여기서는 바이트 순서를 뒤집어 저장한다(리틀 엔디언)는 것만 씁니다.

아래는 Microsoft 문서의 예시 값과 조사한 PC 에서 본 값을 형식대로 옮긴 예시입니다. 검체에서 뽑은 바이트가 아닙니다.

```
PreviousTime 2015-10-09T05:04:30.0009419Z
  = 130888406700009419 = 0x01D1024FFA9227CB  →  CB 27 92 FA 4F 02 D1 01

NewTime      2015-10-09T05:04:30.0000000Z
  = 130888406700000000 = 0x01D1024FFA920300  →  00 03 92 FA 4F 02 D1 01

차이 = 9419 (100ns 단위) = 0.9419 밀리초, NewTime 이 더 이릅니다
```

부호 있는 칸은 이렇게 들어갑니다.

```
TimeZoneBias  -540   (Int32)  →  E4 FD FF FF
  부호 없이 읽으면 0xFFFFFDE4 = 4294966756

TimeDeltaInMs -1995  (Int64)  →  35 F8 FF FF FF FF FF FF
TimeDeltaInMs 121010 (Int64)  →  B2 D8 01 00 00 00 00 00
```

1. 시스템 로그 사본에서 Kernel-General 1 레코드를 찾습니다.
2. 값 영역에서 8바이트 FILETIME 두 개(NewTime, OldTime)를 찾습니다.
3. 바이트를 뒤집어 읽고 시각으로 바꿉니다. 두 값의 차이가 TimeDeltaInMs 와 맞는지 봅니다.
4. TimeZoneBias 의 4바이트가 `FF` 로 끝나면 음수입니다. 부호 있는 값으로 읽습니다.

값 영역의 구조는 [이벤트 로그 형식](/01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

### 공개 도구로 한 번

Windows 에 들어 있는 PowerShell 로 사본 파일에서 두 이벤트를 뽑을 수 있습니다.

```powershell
# 보안 로그의 4616
Get-WinEvent -Path .\Security.evtx -FilterXPath "*[System[(EventID=4616)]]" -Oldest |
  ForEach-Object {
    $d = @{}
    ([xml]$_.ToXml()).Event.EventData.Data | ForEach-Object { $d[$_.Name] = $_.'#text' }
    [pscustomobject]@{
      TimeUtc   = $_.TimeCreated.ToUniversalTime()
      Previous  = $d['PreviousTime']
      New       = $d['NewTime']
      Sid       = $d['SubjectUserSid']
      LogonId   = $d['SubjectLogonId']
      ProcessId = $d['ProcessId']
      Process   = $d['ProcessName']
    }
  } | Format-Table

# 시스템 로그의 Kernel-General 1
Get-WinEvent -Path .\System.evtx -FilterXPath "*[System[Provider[@Name='Microsoft-Windows-Kernel-General'] and (EventID=1)]]" -Oldest |
  ForEach-Object {
    $d = @{}
    ([xml]$_.ToXml()).Event.EventData.Data | ForEach-Object { $d[$_.Name] = $_.'#text' }
    [pscustomobject]@{
      TimeUtc   = $_.TimeCreated.ToUniversalTime()
      Old       = $d['OldTime']
      New       = $d['NewTime']
      DeltaMs   = $d['TimeDeltaInMs']
      Reason    = $d['Reason']
      ProcessId = $d['ProcessID']
      Process   = $d['ProcessName']
    }
  } | Format-Table
```

- 두 결과를 기록 시각으로 맞대면 짝을 찾을 수 있습니다. 프로세스 ID 는 진법을 맞춘 뒤 비교합니다.
- EvtxECmd 맵 저장소에는 Security 4616 맵과 System 의 Kernel-General 1·12·13 맵이 있습니다. Kernel-General 1 맵은 Reason 숫자를 위 표의 문구로 바꿔 줍니다.
- 도구가 바꿔 보여 준 값은 XML 원문 한두 건과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 무엇을 맞춰 보나 | 링크 |
|---|---|---|
| 로그온 이벤트 | SubjectLogonId 가 가리키는 로그온 세션 | [로그온·로그오프](/02-artifacts/event-logs/logon-events/index.md) |
| 4688 | ProcessId 로 찾은 프로세스의 부모와 명령줄 | [프로세스 생성](/02-artifacts/event-logs/4688.md) |
| 전원 이벤트 | Reason 2 가 깨어날 때의 보정인지 | [켜짐·꺼짐](/02-artifacts/event-logs/power-on-off-events.md) |
| 시간대 설정 | TimeZoneBias 와 레지스트리 Bias 가 맞는지 | [시간대 설정](/02-artifacts/system-account/time-zone.md) |
| 파일·문서 시각 | 바뀐 시각 동안 만든 파일과 문서의 날짜 | [이 문서의 날짜를 믿을 수 있나](/04-scenarios/activity/document-date-verification.md) |
| 타임라인 | 되돌린 구간의 앞뒤 기록 순서 | [타임라인 작성](/03-techniques/analysis/timeline/index.md) |

시각 조작을 의심할 때 합쳐 읽는 순서는 [증거를 없애려 했나](/04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 실습

직접 만든 Windows 10·11 가상 머신에서 해 봅니다. 가상 머신의 시각 동기화 기능은 끄고 시작합니다.

1. 설정 화면에서 시각을 손으로 하루 앞으로 옮깁니다. 4616 의 Subject 와 ProcessName, Kernel-General 1 의 Reason 을 확인하십시오.
2. 시각을 다시 되돌립니다. TimeDeltaInMs 가 음수로 남는지 보십시오.
3. 가상 머신을 절전 상태로 두었다가 깨웁니다. Reason 2 가 남는지, 그때 4616 도 남는지 보십시오. 함정 7번의 답이 여기서 나옵니다.
4. 시간대만 바꿉니다. Kernel-General 1 과 24 가운데 무엇이 남는지 비교하십시오.
5. 2번 뒤의 시스템 로그에서 레코드 번호 순서와 기록 시각 순서가 어긋나는 곳을 찾아보십시오. "시각 해석" 의 확인하지 못한 부분이 여기서 풀립니다.

NIST CFReDS 같은 공개 검체에서 이벤트 로그를 꺼냈다면, 먼저 Kernel-General 1 가운데 ProcessName 이 `svchost.exe` 가 아니고 Reason 이 2 도 아닌 것을 찾아보십시오.

## 참고 문헌

- Microsoft Learn, "4616(S) The system time was changed." (Windows 10 보관 문서) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4616
- Eric Zimmerman evtx (EvtxECmd) 맵, "System_Microsoft-Windows-Kernel-General_1.map" (작성 Hyun Yi) — https://raw.githubusercontent.com/EricZimmerman/evtx/master/evtx/Maps/System_Microsoft-Windows-Kernel-General_1.map
- GitHub API, EricZimmerman/evtx 저장소 evtx/Maps 폴더 파일 목록 (맵 파일 이름만 확인) — https://api.github.com/repos/EricZimmerman/evtx/contents/evtx/Maps
