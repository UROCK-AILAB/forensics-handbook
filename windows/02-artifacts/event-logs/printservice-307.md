---
title: "인쇄 이벤트"
parent: "아티팩트 · 이벤트 로그"
nav_order: 2770
---

# 인쇄 이벤트 (PrintService 307)

## 한 줄 요약

이벤트 307 은 문서 한 건을 프린터로 인쇄했다는 기록입니다. 작업 번호, 문서 이름, 사용자, 컴퓨터, 프린터, 포트, 바이트 수, 쪽수가 들어갑니다. 이 이벤트는 `Microsoft-Windows-PrintService/Operational` 채널에 남고, 이 채널이 켜져 있을 때만 기록됩니다. 문서 이름은 "Allow job name in event logs" 정책을 켜야 들어갑니다. 시각은 UTC 입니다.

## 무엇을 기록하나 · 왜 생기나

307 의 메시지 틀은 아래와 같습니다.

```
Document %1, %2 owned by %3 on %4 was printed on %5 through port %6.  Size in bytes: %7. Pages printed: %8. No user action is required.
```

공급자 메타데이터에서 307 의 작업 분류 (Task) 는 "Printing a document" 이고 키워드는 "Classic Spooler Event" 와 "Document Print Job" 입니다.

인쇄 작업이 스풀 파일을 거쳐 프린터로 가는 흐름은 [인쇄 흔적](../external-devices/print-spooler-spl-shd.md)에서 다룹니다.

307 이 쓸모 있으려면 두 가지 설정을 먼저 봐야 합니다.

| 설정 | 꺼져 있으면 | 예 (Windows 11 25H2 한 대) |
|---|---|---|
| `PrintService/Operational` 채널 | 307 이 아예 남지 않습니다 | 꺼짐 |
| "Allow job name in event logs" 정책 | 307 에 문서 이름이 들어가지 않습니다 | 값 없음(설정 안 함) |

## 위치와 버전별 차이

### 공급자와 채널

| 항목 | 내용 |
|---|---|
| 공급자 | Microsoft-Windows-PrintService |
| 공급자 GUID | `{747ef6fd-e535-4d16-b510-42c90f6873a1}` |
| 채널 | `Microsoft-Windows-PrintService/Operational` |
| 수준 | 정보 (Informational) |
| 이벤트 버전 | 0 |
| 로그 파일 | `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-PrintService%4Operational.evtx` |

Windows 11 25H2 한 대의 두 채널 설정은 아래와 같습니다.

| 채널 | 켜짐 | 최대 크기 | 꽉 찼을 때 | 레코드 |
|---|---|---|---|---|
| `PrintService/Operational` | 꺼짐 | 1,052,672 바이트 | 오래된 기록부터 덮어씁니다 (retention false). 자동 백업도 하지 않습니다 (autoBackup false) | 꺼져 있어 기록이 없습니다 |
| `PrintService/Admin` | 켜짐 | 1,052,672 바이트 | 오래된 기록부터 덮어씁니다 | 0건 |

- 307 은 Operational 채널의 이벤트라서 Admin 채널이 켜져 있어도 그쪽에 남지 않습니다.
- 이 채널이 꺼져 있는 PC 가 있으므로 분석 대상마다 설정을 확인합니다.
- 약 1MB 로그에 며칠치가 남는지는 인쇄량에 따라 다릅니다. 로그의 가장 오래된 레코드 시각을 먼저 적어 둡니다.

### 채널이 켜져 있었는지 오프라인에서 보기

SOFTWARE 하이브의 아래 키에서 `Enabled` 값을 봅니다.

```
Microsoft\Windows\CurrentVersion\WINEVT\Channels\Microsoft-Windows-PrintService/Operational
```

- 마지막 키 이름 `Microsoft-Windows-PrintService/Operational` 에는 슬래시가 들어 있습니다. 슬래시까지가 키 이름 하나입니다.
- `Enabled` 가 0 이면 꺼짐, 1 이면 켜짐입니다. 앞 표의 PC 에서는 Operational 이 0, 같은 위치의 `…/Admin` 이 1 입니다.
- 같은 키의 `OwningPublisher` 값은 공급자 GUID `{747ef6fd-e535-4d16-b510-42c90f6873a1}` 입니다.
- 하이브 파일 위치는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

라이브 시스템에서는 `wevtutil sl Microsoft-Windows-PrintService/Operational /e:true` 로 채널을 켤 수 있습니다. 앞으로의 인쇄를 기록하려고 미리 켜 두는 설정이라서, 조사 대상 PC 에서 켜면 증거 PC 의 설정을 바꾸게 됩니다.

### 문서 이름 정책

| 항목 | 내용 |
|---|---|
| 정책 이름 | Allow job name in event logs |
| 분류 | 컴퓨터 정책, Printers |
| 레지스트리 | `HKLM\Software\Policies\Microsoft\Windows NT\Printers` 의 `ShowJobTitleInEventLogs` |
| 값 | 사용 = 1, 사용 안 함 = 0 |
| 오프라인 위치 | SOFTWARE 하이브 `Policies\Microsoft\Windows NT\Printers\ShowJobTitleInEventLogs` |

정책을 켜지 않으면 작업 이름 (job name) 이 인쇄 이벤트에 들어가지 않습니다. "사용 안 함" 과 "구성되지 않음" 모두 이름을 빼며, 정책을 켜면 그 뒤에 생기는 새 기록에만 이름이 들어갑니다. 지점 직접 인쇄 (Branch Office Direct Printing) 작업에는 이 정책이 적용되지 않습니다[2].

- 스풀러 구성 요소 `C:\Windows\System32\localspl.dll` 안에는 UTF-16 문자열 `ShowJobTitleInEventLogs` 와 `Software\Policies\Microsoft\Windows NT\Printers` 가 있습니다.
- 정책을 설정하지 않은 PC 에는 이 값이 없습니다. 앞 표의 PC 에서는 `Printers` 정책 키 아래에 `DriverRanking` 하위 키만 있습니다.
- 이름을 뺄 때 문서 이름 필드에 무엇이 들어가는지는 실제 데이터나 시험으로 확인합니다.

### 버전별 차이

| Windows | 내용 | 근거 |
|---|---|---|
| 8 이후 | 정책 파일이 적은 지원 대상 (supportedOn) 이 `SUPPORTED_Windows8` 입니다 | [2] |
| 11 25H2 | Operational 꺼짐, Admin 켜짐, 이름 정책 값 없음 (한 대) | [3] |

지원 대상 값에는 정책을 적용할 수 있는 Windows 판만 나와 있습니다. 이름을 빼는 동작이 언제부터 기본값이 됐는지는 나와 있지 않습니다.

## 구조

### 307 의 필드

필드 이름은 param1~param8 이고, 모두 유니코드 문자열 (UnicodeString) 입니다. 필드의 뜻은 메시지 틀의 자리로 알 수 있습니다.

| 필드 | 메시지 자리 | 뜻 | 실제 데이터로 확인할 것 |
|---|---|---|---|
| param1 | `Document %1` | 작업 번호 (Job ID) | 스풀 폴더의 SPL·SHD 파일 이름 번호와 같은지 |
| param2 | `, %2` | 문서 이름. 정책이 켜져 있을 때만 들어갑니다 | 정책이 꺼져 있을 때 들어가는 값 |
| param3 | `owned by %3` | 작업 주인인 사용자 | |
| param4 | `on %4` | 컴퓨터 | 인쇄를 보낸 컴퓨터인지, 어떤 모양(예: `\\이름`)으로 들어가는지 |
| param5 | `printed on %5` | 프린터 | |
| param6 | `through port %6` | 포트 | |
| param7 | `Size in bytes: %7` | 바이트 수 | |
| param8 | `Pages printed: %8` | 쪽수 | 복사 매수가 반영되는지, 드라이버가 센 쪽수인지 |

바이트 수와 쪽수도 문자열로 저장됩니다. 정렬하거나 합계를 낼 때는 숫자로 바꿔야 합니다.

### 같은 채널의 다른 이벤트

모두 Operational 채널, 이벤트 버전 0 입니다.

| 이벤트 | 메시지 | 필드 |
|---|---|---|
| 300 | `Printer %1 was created.` | |
| 301 | `Printer %1 was deleted, …` | |
| 302 | `Printer %1 will be deleted.` | |
| 303 | 프린터 일시 중지 | |
| 304 | 프린터 재개 | |
| 305 | 대기열의 작업 삭제 | |
| 306 | `Settings for printer %1 were changed.` | |
| 308 | `Document %1, %2 owned by %3 was paused on %4. …` | |
| 309 | `… was resumed on %4.` | |
| 310 | `Document %1, %2 owned by %3 was deleted on %4.` | |
| 311 | `An administrator moved document %1, %2 owned by %3 to position %4 on %5.` | |
| 312 | `Form %1 was added.` | |
| 800 | `Spooling job %1.` | JobId |
| 801 | `Printing job %1.` | JobId |
| 805 | `Rendering job %1.` | JobId, GdiJobSize, ICMMethod, Color, XRes, YRes, Quality, Copies, TTOption |
| 842 | `The print job %1 was sent through the print processor %2 on printer %3, driver %4, in the isolation mode %5 (…). Win32 error code returned by the print processor: %6.` | JobId, Processor, Printer, Driver, IsolationMode, Error |

- 842 의 격리 모드 (isolation mode) 값은 메시지에 적혀 있습니다. 0 은 스풀러 안에서 불러옴, 1 은 공유 샌드박스, 2 는 격리 샌드박스입니다.
- 805 에는 Copies 필드가 있습니다. 이 필드가 복사 매수를 뜻하는지는 실제 데이터로 확인합니다.
- 307 이 없는 작업 번호가 있으면 같은 번호의 308·309·310 도 찾아봅니다.
- 도구가 메시지 문장을 푸는 방식은 [공급자와 메시지 파일](../../01-foundations/database-log-formats/evtx-evt-etl/provider-message-table.md)에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 기록된 시각에 이 사용자 이름이 주인인 작업을 이 프린터와 포트로 인쇄했다는 스풀러 기록이 있습니다 | 계정 뒤의 사람이 누구인지, 인쇄물을 누가 가져갔는지 |
| 작업의 바이트 수와 쪽수 | 쪽수가 종이 장수와 같다는 것 (복사 매수 반영 여부는 실제 데이터로 확인합니다) |
| 정책이 켜져 있었다면 작업 이름 | 작업 이름이 디스크의 어느 파일인지 (이 필드에는 파일 경로가 아니라 작업 이름이 들어갑니다) |
| | 문서의 내용 (307 에는 내용이 없습니다) |
| | 307 이 없으니 인쇄하지 않았다는 것 (채널이 꺼져 있었을 수 있습니다) |

### 보고서 문장

아래 이름과 숫자는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "PrintService/Operational 로그에는 <시각> UTC 에 307 이 있습니다. 사용자 ○○ 가 주인인 작업 번호 ○ 을 프린터 ○○ 의 포트 ○○ 로 인쇄했다는 기록입니다. 크기는 ○○ 바이트, 쪽수는 ○ 쪽으로 적혀 있습니다. 문서 이름 필드에는 ○○ 이 적혀 있습니다."
- 쓰면 안 되는 문장: "○○ 이 기밀 문서를 인쇄해 가져갔다."
- 307 이 없을 때 쓸 수 있는 문장: "이 PC 의 PrintService/Operational 채널은 꺼져 있었습니다(`Enabled` = 0). 그래서 인쇄 이벤트로는 인쇄 여부를 정할 수 없습니다."

## 시각 해석

- 이벤트 시각은 `<TimeCreated SystemTime>` 에 있습니다. 끝에 Z 가 붙은 UTC 값입니다.
- 현지 시각으로 바꾸는 법은 [시간대 설정](../system-account/time-zone.md)에서 다룹니다.
- 307 의 시각은 인쇄가 끝난 시각일 수도, 스풀러가 작업을 프린터로 넘긴 시각일 수도 있습니다. 그래서 보고서에는 "307 이 기록된 시각" 이라고만 씁니다.
- 800(스풀), 801(인쇄), 805(렌더링), 842(인쇄 처리기) 에도 작업 번호 필드가 있습니다. 307 의 param1 과 같은 번호의 기록을 모아 시각 순으로 늘어놓아 봅니다. 두 번호가 같은 작업을 가리키는지는 실제 데이터로 확인합니다.
- 스풀 폴더 파일의 시각과 맞춰 보는 법은 [인쇄 흔적](../external-devices/print-spooler-spl-shd.md)에서 다룹니다.

## 함정과 한계

1. **307 이 없으니 인쇄하지 않았다고 씁니다.** Operational 채널이 꺼져 있는 PC 도 있습니다. 채널 설정부터 확인합니다.
2. **Admin 채널이 켜져 있으니 기록이 있으리라 봅니다.** 307 은 Operational 채널의 이벤트입니다.
3. **문서 이름이 비어 있거나 다르니 누가 숨겼다고 봅니다.** 정책을 켜지 않으면 이름이 들어가지 않습니다. 정책 값부터 확인합니다.
4. **정책을 켰으니 예전 기록에도 이름이 있으리라 봅니다.** 정책을 켠 뒤의 새 기록에만 이름이 들어갑니다[2].
5. **바이트 수와 쪽수를 문자열 그대로 정렬합니다.** 문자열로 정렬하면 "10" 이 "9" 보다 앞에 옵니다. 숫자로 바꿔 정렬하고 합칩니다.
6. **쪽수를 종이 장수로 씁니다.** 복사 매수가 반영되는지, 드라이버가 센 값인지는 실제 데이터로 확인합니다.
7. **param4 를 인쇄를 보낸 컴퓨터로 단정합니다.** 이 필드의 뜻과 모양은 실제 데이터로 확인합니다.
8. **공유 프린터 작업을 클라이언트 PC 에서만 찾습니다.** 인쇄 서버로 보낸 작업의 307 이 클라이언트 PC 에 남는지, 서버에만 남는지 정해 두지 말고 두 곳을 모두 봅니다.
9. **가상 프린터도 같다고 봅니다.** "Microsoft Print to PDF" 같은 가상 프린터로 보낸 작업이 307 을 남기는지는 시험으로 확인합니다(실습 3).
10. **지점 직접 인쇄 작업의 이름을 찾습니다.** 이름 정책은 이 작업에 적용되지 않습니다.

### 지우기와 조작

- **로그를 지웁니다.** 지운 흔적은 [이벤트 로그 삭제](1102-104.md)에서 찾습니다.
- **채널을 끕니다.** 끈 뒤로는 307 이 남지 않습니다. 채널과 감사 설정을 함께 보는 법은 [감사 정책과 로그 설정](audit-policy-log-settings.md)에서 다룹니다.
- **로그를 덮어쓰게 합니다.** Operational 최대 크기가 약 1MB 로 설정된 PC 도 있습니다. 꽉 차면 오래된 기록부터 덮어씁니다.
- **스풀 파일을 지웁니다.** 이벤트와 스풀 파일은 따로 남습니다. 스풀 파일 쪽은 [인쇄 흔적](../external-devices/print-spooler-spl-shd.md)에서 다룹니다.

## 직접 분석해 보기

### 먼저 설정 두 가지를 봅니다

1. SOFTWARE 하이브에서 `WINEVT\Channels\Microsoft-Windows-PrintService/Operational` 의 `Enabled` 를 봅니다. 0 이면 307 을 기대하지 않습니다.
2. 같은 하이브에서 `Policies\Microsoft\Windows NT\Printers` 의 `ShowJobTitleInEventLogs` 를 봅니다. 값이 없거나 0 이면 문서 이름을 기대하지 않습니다.
3. `Microsoft-Windows-PrintService%4Operational.evtx` 파일이 있는지, 가장 오래된 레코드가 언제인지 봅니다.

하이브의 값은 조사한 때의 상태입니다. 인쇄한 때에도 같은 설정이었는지는 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 속 옛 하이브로 확인합니다.

### 헥스로 한 번

param1~param8 은 모두 유니코드 문자열입니다. 쪽수 "3" 이나 바이트 수 "12345" 도 숫자가 아니라 글자로 저장됩니다. 글자는 UTF-16LE 로 옮겨 적습니다.

아래는 형식대로 만든 예시입니다. 실제 데이터에서 뽑은 바이트가 아닙니다.

```
param8 "3"      →  33 00
param7 "12345"  →  31 00 32 00 33 00 34 00 35 00
```

- 로그 파일의 빈 공간이나 손상된 영역에서 프린터 이름이나 사용자 이름을 찾을 때는 UTF-16LE 로 검색합니다. 인코딩은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.
- 값이 EVTX 레코드 안에 저장되는 방식은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

### 공개 도구로 한 번

Windows 에 들어 있는 PowerShell 로 사본 파일에서 307 을 뽑아 필드별로 늘어놓을 수 있습니다. 값의 순서가 param1~param8 의 순서입니다.

```powershell
Get-WinEvent -Path '.\Microsoft-Windows-PrintService%4Operational.evtx' -FilterXPath '*[System[EventID=307]]' -Oldest |
  ForEach-Object {
    $p = $_.Properties.Value
    [pscustomobject]@{
      TimeUtc  = $_.TimeCreated.ToUniversalTime()
      JobId    = $p[0]
      Document = $p[1]
      Owner    = $p[2]
      Computer = $p[3]
      Printer  = $p[4]
      Port     = $p[5]
      Bytes    = [int64]$p[6]
      Pages    = [int]$p[7]
    }
  } | Sort-Object TimeUtc | Format-Table -AutoSize
```

- 바이트 수와 쪽수를 숫자로 바꿔 두면 사용자별·프린터별 합계를 낼 수 있습니다.
- 이벤트 뷰어의 "자세히 → XML 보기" 로 필드 원문을 볼 수 있습니다.
- EvtxECmd, python-evtx 같은 공개 도구도 이 채널을 읽습니다. 도구의 풀이는 XML 원문 한두 건과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 무엇을 맞춰 보나 | 링크 |
|---|---|---|
| 스풀 파일과 프린터 목록 | 307 의 프린터가 설치돼 있었는지, 같은 때의 스풀 파일이 남았는지 | [인쇄 흔적](../external-devices/print-spooler-spl-shd.md) |
| 바로가기 파일 | 인쇄한 즈음 작업 이름과 비슷한 이름의 문서를 열었는지 | [바로가기 파일](../file-folder-usage/lnk.md) |
| 로그 설정 | 그 시기에 채널이 켜져 있었는지 | [감사 정책과 로그 설정](audit-policy-log-settings.md) |
| 이벤트 로그 삭제 | 로그가 지워진 적이 있는지 | [이벤트 로그 삭제](1102-104.md) |
| 메시지 파일 | 도구가 문장을 제대로 풀었는지 | [공급자와 메시지 파일](../../01-foundations/database-log-formats/evtx-evt-etl/provider-message-table.md) |

합쳐 읽는 순서는 [인쇄해서 가져갔나](../../04-scenarios/exfiltration/data-exfiltration/print.md)에서 다룹니다.

## 실습

직접 만든 Windows 10·11 가상 머신에서 해 봅니다. 각 단계의 시각을 적어 둡니다.

1. 채널을 켜기 전에 문서 하나를 인쇄합니다. 307 이 남는지 보십시오.
2. Operational 채널을 켜고 같은 문서를 다시 인쇄합니다. 307 의 여덟 필드를 확인하십시오.
3. "Microsoft Print to PDF" 로 인쇄합니다. 307 이 남는지 보십시오. 함정 9번의 답이 여기서 나옵니다.
4. 이름 정책을 켜기 전과 뒤에 한 번씩 인쇄합니다. param2 가 어떻게 달라지는지 비교하십시오. 함정 3번과 4번이 여기서 풀립니다.
5. 두 부를 인쇄합니다. param8 과 805 의 Copies 필드를 비교하십시오.
6. 프린터를 일시 중지하고 인쇄한 뒤 스풀 폴더를 봅니다. 파일 이름의 번호와 param1 이 같은지 비교하십시오.
7. 같은 작업의 800·801·805·842·307 을 시각 순으로 늘어놓으십시오. 307 이 어느 단계 뒤에 남는지 보십시오.

NIST CFReDS 같은 공개 시험 데이터를 풀 때는 먼저 SOFTWARE 하이브에서 채널의 `Enabled` 값을 봅니다. 0 이면 이 로그로 인쇄 여부를 정할 수 없습니다. 그 경우 어떤 기록으로 인쇄를 확인할지 [인쇄 흔적](../external-devices/print-spooler-spl-shd.md)에서 골라 보십시오.

## 참고 문헌

이 페이지는 공개 문서를 인용하지 않았습니다. 모든 사실은 관찰 PC(Windows 11 Home 25H2, 빌드 26200) 에서 아래 자료를 직접 열어 확인했습니다.

- Microsoft-Windows-PrintService 공급자 메타데이터 (이벤트 300~312, 800, 801, 805, 842 의 메시지 틀과 필드)
- `Printing.admx`·`Printing.adml`(en-US) 10.0.26100.8737 — WinSxS 폴더 안 파일
- SOFTWARE 하이브 `Microsoft\Windows\CurrentVersion\WINEVT\Channels` 와 `Policies\Microsoft\Windows NT\Printers`
- `C:\Windows\System32\localspl.dll` 안의 문자열
