---
title: "인쇄 흔적"
parent: "아티팩트 · 외부 장치"
nav_order: 1570
---

# 인쇄 흔적 (Print Spooler: SPL·SHD·프린터 목록)

## 한 줄 요약

Windows 는 인쇄할 때 먼저 스풀 파일 (spool file) 을 만들고, 차례가 오면 이 파일을 읽어 프린터로 보냅니다. 스풀 파일은 프린터 설정에 따라 인쇄가 끝나면 지워지거나 남습니다. 레지스트리의 프린터 목록은 어떤 실물 프린터와 가상 프린터가 설치돼 있었는지 보여 줍니다. 인쇄 이벤트는 로그 채널을 켜 둔 경우에만 남습니다.

> 이 페이지에서 "관찰 PC" 는 Windows 11 Home 25H2(빌드 26200.9457) PC 한 대를 말합니다. 관찰 PC 에서 본 내용은 모두 "확인 범위: Win11 25H2 한 대" 입니다.

## 무엇을 기록하나 · 왜 생기나

### 스풀 파일이 생기고 쓰이는 순서

Microsoft 문서가 설명하는 로컬 인쇄 공급자 (Local Print Provider) 의 흐름입니다.

1. 로컬 인쇄 공급자는 로컬 포트 모니터로 접근하는 프린터의 작업과 프린터를 관리합니다. Windows 2000 부터 이렇게 동작합니다.
2. 앱은 GDI 를 불러 인쇄 작업을 만듭니다.
3. 로컬 인쇄 공급자의 작업 생성 API 가 스풀 파일을 만듭니다. 작업의 처음 출력 형식이 EMF 이든 아니든 같습니다.
4. 작업 차례가 오면 스풀 파일을 읽습니다.
5. 형식이 EMF 이면 EMF 인쇄 처리기 (print processor) 가 작업을 GDI 로 돌려보냅니다. GDI 는 프린터 그래픽 DLL 의 도움을 받아 작업을 RAW 형식으로 바꿉니다.
6. 바꾼 데이터는 다시 스풀하지 않고 바로 프린터로 보냅니다.

> 그림 자리: 앱 → GDI → 로컬 인쇄 공급자(스풀 파일 생성) → 인쇄 처리기(EMF 이면 GDI 로 RAW 변환) → 프린터 흐름과, 스풀 파일이 생기는 지점·지워지는 지점

인쇄 작업을 남기는 설정이 꺼져 있으면 인쇄가 끝난 작업을 지우고, 켜져 있으면 남깁니다(`PRINTER_ATTRIBUTE_KEEPPRINTEDJOBS`). 그래서 이 설정이 꺼진 프린터에서는 스풀 파일이 인쇄하는 동안만 있다가 사라집니다.

### SPL 과 SHD

작업마다 인쇄 데이터를 담은 SPL 파일과 작업 정보를 담은 SHD 파일 (shadow file) 이 생긴다고 널리 설명하지만, 이 글에서는 이 설명을 명세로 확인하지 못했습니다. 형식 문서를 열었지만 내용이 비어 있었습니다. 파일 이름 규칙, SHD 안의 칸과 오프셋, Windows 판별 서명 값도 확인하지 못했으므로 이 페이지는 SHD 오프셋을 적지 않습니다.

`PRINTER_INFO_2` 구조체의 `pDatatype` 은 "인쇄 작업을 기록할 때 쓰는 데이터 형식" 입니다. SPL 에 EMF 가 그대로 담기는지, 프린터로 보낼 RAW 데이터가 담기는지는 작업의 데이터 형식에 따릅니다. EMF 스풀 형식 명세(MS-EMFSPOOL)는 이 글에서 열어 보지 않았습니다.

### 프린터 목록

관찰 PC 에서는 프린터마다 SYSTEM 하이브 `Control\Print\Printers` 아래에 하위 키가 하나 있었고, 사용자 하이브(NTUSER.DAT)에도 프린터 이름과 기본 프린터가 남아 있었습니다.

## 위치와 버전별 차이

하이브 파일 위치와 `ControlSet00X` 를 고르는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)를 봅니다.

| 기록 | 위치 | 주로 보는 것 |
|---|---|---|
| 기본 스풀 폴더 | SYSTEM `ControlSet00X\Control\Print\Printers` 의 `DefaultSpoolDirectory` 값 | 관찰 PC: `C:\Windows\system32\spool\PRINTERS` |
| 프린터별 설정 | SYSTEM `ControlSet00X\Control\Print\Printers\<프린터 이름>` | `Attributes`, `Port`, `Printer Driver`, `Print Processor`, `Datatype`, `SpoolDirectory` |
| 사용자별 프린터 목록 | NTUSER.DAT `Software\Microsoft\Windows NT\CurrentVersion\Devices`, 같은 곳의 `PrinterPorts` | 값 이름이 프린터 이름입니다. |
| 기본 프린터 | NTUSER.DAT `Software\Microsoft\Windows NT\CurrentVersion\Windows` 의 `Device` 값 | `<프린터 이름>,winspool,<포트>` 모양 |
| 인쇄 이벤트 | `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-PrintService%4Operational.evtx` | [인쇄 이벤트](../event-logs/printservice-307.md) |

- 라이브 PC 에서는 SYSTEM 쪽 키를 `HKLM\SYSTEM\CurrentControlSet\Control\Print\Printers` 로 엽니다.
- 관찰 PC 에서 기본 프린터 `Device` 값은 `<가상 PDF 프린터 이름>,winspool,Ne01:` 모양이었고, 같은 키의 `LegacyDefaultPrinterMode` 는 0 이었습니다.

| Windows | 내용 | 근거 |
|---|---|---|
| 2000 이후 | 로컬 인쇄 공급자가 작업과 프린터를 관리합니다. `PRINTER_INFO_2` 의 최소 지원 판입니다. | Microsoft |
| XP 이후 | 속성 비트 `PRINTER_ATTRIBUTE_FAX` 를 쓸 수 있습니다. | Microsoft |
| Server 2003 | 속성 비트 `PRINTER_ATTRIBUTE_TS` 를 쓸 수 있습니다. | Microsoft |
| Vista 이후 | 속성 비트 `FRIENDLY_NAME`·`MACHINE`·`PUSHED_USER`·`PUSHED_MACHINE` 을 쓸 수 있습니다. | Microsoft |
| 10 이후 | 타사 인쇄 공급자 API 를 더 이상 권장하지 않습니다. | Microsoft |
| 11 25H2 | 이 페이지의 레지스트리 값과 이벤트 채널 상태를 관찰했습니다. | 관찰 PC |

- Windows 판마다 SPL·SHD 형식이 어떻게 다른지는 확인하지 못했습니다.

## 구조

### 프린터 키의 값

- 관찰 PC 의 프린터 키에서 본 값: `Name`, `Share Name`, `Print Processor`, `Datatype`, `Parameters`, `Description`, `Printer Driver`, `Default DevMode`, `Priority`, `Default Priority`, `StartTime`, `UntilTime`, `Separator File`, `Location`, `Attributes`, `Port`, `SpoolDirectory`, `Status`, `StatusExt`, `ChangeID`, `CreatorSid`, `QueueInstanceId`, `DeviceInterfaceId`, `Security`, `ObjectGUID` 등.
- 하위 키: `DsDriver`, `DsSpooler`, `PnPData`, `PrinterDriverData`. 일부 프린터에는 `ConfigDriverResources`, `PsaData` 도 있었습니다.
- 값 이름 여럿이 `PRINTER_INFO_2` 구조체 멤버와 이름이 비슷합니다(`Attributes`, `Priority`, `StartTime` 등). 레지스트리 값과 구조체 멤버가 하나씩 같은지는 확인하지 못했습니다.
- 관찰 PC 의 프린터 5개는 모두 `Print Processor` 가 `winprint`, `Datatype` 이 `RAW` 였습니다.
- 프린터별 `SpoolDirectory` 값은 5개 모두 비어 있었습니다. 이 경우 기본 스풀 폴더를 씁니다.

### Attributes 비트

| 비트 | .NET 이름 | Win32 상수와 Microsoft 설명 |
|---|---|---|
| 0x1 | Queued | `QUEUED`. 켜져 있으면 마지막 쪽까지 스풀한 뒤 인쇄를 시작합니다. 꺼져 있고 Direct 도 아니면 스풀하면서 인쇄합니다. |
| 0x2 | Direct | `DIRECT`. 스풀하지 않고 바로 프린터로 보냅니다. |
| 0x8 | Shared | `SHARED` |
| 0x20 | Hidden | `HIDDEN` |
| 0x40 | (없음) | `LOCAL` |
| 0x80 | EnableDevQuery | `ENABLE_DEVQ` |
| 0x100 | KeepPrintedJobs | `KEEPPRINTEDJOBS`. 켜져 있으면 인쇄가 끝난 작업을 남기고, 꺼져 있으면 지웁니다. |
| 0x200 | ScheduleCompletedJobsFirst | `DO_COMPLETE_FIRST`. 스풀이 끝난 작업을 먼저 인쇄하도록 차례를 잡습니다. |
| 0x800 | EnableBidi | `ENABLE_BIDI` |
| 0x1000 | RawOnly | `RAW_ONLY` |
| 0x2000 | Published | `PUBLISHED` |

- 비트 값은 관찰 PC 의 .NET `System.Printing.PrintQueueAttributes` 에서 읽었습니다.
- Wine 의 `winspool.h` 에서 `PRINTER_ATTRIBUTE_*` 상수가 위와 같은 숫자인 것을 확인했습니다. 0x40 은 `LOCAL` 이고, .NET 열거형에는 없습니다.
- 같은 헤더에는 0x4(`DEFAULT`), 0x10(`NETWORK`), 0x400(`WORK_OFFLINE`) 도 있습니다.
- 관찰 PC 에서는 `Get-Printer` 의 `KeepPrintedJobs` 가 True 인 프린터만 레지스트리 `Attributes` 의 0x100 비트가 켜져 있었습니다.

관찰 PC 의 프린터 5개는 아래와 같았습니다.

| 프린터 종류 | 포트 | `Attributes` | 켜진 비트 |
|---|---|---|---|
| 실물 프린터 (드라이버 Microsoft IPP Class Driver) | WSD 포트 | 0x200 | ScheduleCompletedJobsFirst |
| 같은 기기의 팩스 항목 | WSD 포트 | 0xA00 | ScheduleCompletedJobsFirst, EnableBidi |
| 타사 PDF 가상 프린터 | 그 프로그램 전용 포트 | 0x901 | Queued, KeepPrintedJobs, EnableBidi |
| Microsoft Print to PDF | `PORTPROMPT:` | 0x200 | ScheduleCompletedJobsFirst |
| OneNote (Desktop) | `nul:` | 0x240 | ScheduleCompletedJobsFirst, 0x40(`LOCAL`) |

타사 PDF 프린터는 인쇄 작업을 남기도록 설정돼 있었는데도 스풀 폴더는 비어 있었습니다(0개). 그 프린터로 인쇄하지 않았거나 파일을 지웠을 수 있지만, 이유는 확인하지 못했습니다.

### 스풀 폴더

관찰 PC 의 `C:\Windows\System32\spool\PRINTERS` 는 관리자 권한으로 목록을 볼 수 있었고 비어 있었습니다. 스풀 파일이 남아 있으면 프린터로 보낼 작업 데이터를 볼 수 있습니다. SHD 에서 사용자 이름·컴퓨터 이름·문서 이름·프린터 이름·제출 시각·쪽수를 읽을 수 있다는 설명이 있습니다. 이 글에서는 형식을 확인하지 못했습니다.

### 인쇄 이벤트 (요약)

- 관찰 PC 에서 `Microsoft-Windows-PrintService/Operational` 채널은 꺼져 있었습니다. `Microsoft-Windows-PrintService/Admin` 채널은 켜져 있었고 0건이었습니다.
- Operational 채널의 최대 크기는 1052672 바이트였습니다. 보존 설정(retention)은 false 여서, 꽉 차면 오래된 이벤트부터 덮어씁니다.
- 이 채널이 켜져 있으면 307 이벤트에 문서, 소유자, 프린터, 포트, 바이트 크기, 쪽수가 남습니다. 칸별 설명은 [인쇄 이벤트](../event-logs/printservice-307.md)에서 다룹니다.
- 같은 채널의 800(스풀), 801(인쇄), 805(렌더링), 842(인쇄 처리기) 이벤트에는 작업 번호(`JobId`) 칸이 있습니다.

## 증거로서 의미

### 증명하는 것

- 프린터 키는 이 PC 에 어떤 프린터와 가상 프린터가 설치돼 있었는지 보여 줍니다.
- 포트와 드라이버로 실물 프린터와 파일을 만드는 가상 프린터를 가를 수 있습니다. 관찰 PC 의 가상 프린터 포트는 `PORTPROMPT:`, `nul:`, 전용 PDF 포트였습니다.
- 사용자 하이브의 `Devices`·`PrinterPorts` 에는 그 사용자 쪽에 적힌 프린터 이름이 있습니다.
- 사용자 하이브의 `Windows\Device` 값은 그 사용자의 기본 프린터를 보여 줍니다.
- `Attributes` 의 KeepPrintedJobs 비트는 인쇄가 끝난 뒤에도 스풀 파일을 남기도록 설정했는지 보여 줍니다.
- 스풀 파일이 남아 있으면 그 작업의 인쇄 데이터를 볼 수 있습니다.

### 증명하지 못하는 것

- 프린터를 언제, 누가 추가했는지 알 수 없습니다. 그런 값은 이 글에서 확인하지 못했습니다. `CreatorSid` 라는 값이 있지만 뜻은 확인하지 못했습니다.
- 프린터 목록은 인쇄 작업 자체를 보여 주지 않습니다.
- 스풀 폴더가 비어 있어도 인쇄를 안 했다는 뜻이 아닙니다. 설정이 꺼져 있으면 인쇄가 끝난 작업을 지웁니다.
- 307 이벤트가 없어도 인쇄를 안 했다는 뜻이 아닙니다. 채널이 꺼져 있을 수 있습니다.
- 가상 PDF 프린터로 만든 파일을 어디에 저장했는지는 이 흔적만으로 알 수 없습니다.

### 보고서 문장 예

- 쓰지 않을 문장: "사용자는 기밀 문서를 인쇄해 가져갔다."
- 쓸 문장: "SYSTEM 하이브에 프린터 ○개가 등록돼 있고, 그중 ○○ 은 PDF 파일을 만드는 가상 프린터이다. 사용자 ○○ 의 기본 프린터는 ○○ 이다. 스풀 폴더에는 파일이 없고 PrintService/Operational 로그는 꺼져 있다. 이 기록만으로는 인쇄 작업이 있었는지 정할 수 없다."

## 시각 해석

| 시각 | 무엇인가 | 기준 |
|---|---|---|
| 프린터 키 `StartTime`·`UntilTime` | 이름이 같은 `PRINTER_INFO_2` 멤버는 프린터 정보의 일부입니다. 인쇄 작업 시각으로 쓰지 않습니다. | 구조체 멤버는 "GMT 0시부터 지난 분" (Microsoft) |
| SHD 안의 제출 시각 | 형식(SYSTEMTIME 인지)과 기준(UTC 인지 현지 시각인지)을 확인하지 못했습니다. | 확인하지 못함 |
| 스풀 폴더 파일의 파일시스템 시각 | 스풀 파일도 NTFS 위의 파일입니다. 파일이나 그 MFT 항목이 남아 있으면 시각을 볼 수 있습니다. | UTC ([마스터 파일 테이블](../filesystem/mft.md)) |
| 프린터 키 마지막 기록 시각 | 무엇이 바뀔 때 바뀌는지 확인하지 못했습니다. 프린터를 추가한 시각으로 쓰지 않습니다. | UTC |
| PrintService 이벤트 기록 시각 | [인쇄 이벤트](../event-logs/printservice-307.md)에서 다룹니다. | UTC |

- 인쇄한 때를 정하려면 이벤트 로그와 스풀 폴더의 파일시스템 기록을 함께 봅니다. 프린터 키의 시각 값으로 정하지 않습니다.

## 함정과 한계

1. **빈 스풀 폴더를 "인쇄 안 함" 으로 읽는 실수.** KeepPrintedJobs 가 꺼져 있으면 인쇄가 끝난 작업을 지웁니다. 관찰 PC 에서는 켜져 있는 프린터가 있었는데도 폴더가 비어 있었습니다.
2. **스풀하지 않는 프린터.** Direct 비트가 켜져 있으면 스풀하지 않고 바로 프린터로 보냅니다. 이때는 스풀 파일이 생기지 않는다고 볼 수 있지만, 이 글에서 직접 확인하지는 못했습니다.
3. **다른 스풀 폴더.** `DefaultSpoolDirectory` 와 프린터별 `SpoolDirectory` 를 먼저 읽습니다. `SpoolDirectory` 가 비어 있지 않으면 그 폴더도 봅니다. 그 폴더에 스풀 파일이 생기는지는 확인하지 못했습니다.
4. **꺼져 있는 이벤트 채널.** 관찰 PC 에서 PrintService/Operational 은 꺼져 있었습니다. 이 채널이 기본으로 꺼져 있다는 설명이 있지만 이 글에서 확인하지는 못했습니다. 켜져 있어도 1MB 남짓한 크기라 오래된 이벤트는 덮어씁니다.
5. **가상 프린터.** PDF·OneNote 같은 가상 프린터는 종이 대신 파일이나 노트를 만듭니다. 만든 PDF 파일은 [바로가기 파일](../file-folder-usage/lnk.md)과 [최근 문서](../file-folder-usage/recentdocs.md)로 추적합니다.
6. **스풀 파일 형식을 미리 정하는 실수.** 관찰 PC 의 프린터는 모두 `Datatype` 이 RAW 였습니다. 작업마다 형식이 달라질 수 있는지는 확인하지 못했습니다. SPL 을 열 때는 형식을 가정하지 말고 첫 바이트부터 확인합니다.
7. **비트 값의 근거.** 이 페이지의 비트 숫자는 .NET 열거형과 Wine 의 `winspool.h` 에서 나왔습니다. .NET 열거형에는 0x40(`LOCAL`) 같은 비트가 없습니다. 도구가 .NET 이름만 보여 주면 헤더 값으로 다시 풉니다.
8. **지워진 스풀 파일.** 비할당 영역에서 SPL·SHD 를 되살리는 방법은 이 글에서 확인하지 못했습니다. 일반 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)와 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md)을 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

1. SYSTEM 하이브, 사용자마다 NTUSER.DAT, 각 `.LOG1`·`.LOG2` 를 사본으로 확보합니다.
2. `Select` 키의 `Current` 값으로 컨트롤셋 번호를 정합니다.
3. `Control\Print\Printers` 에서 `DefaultSpoolDirectory` 를 읽고, 하위 키 이름(프린터 이름)을 모두 적습니다.
4. 프린터마다 `Attributes`, `Port`, `Printer Driver`, `Datatype`, `SpoolDirectory` 를 읽습니다.
5. `Attributes` 데이터를 리틀 엔디언 정수로 읽어 위 비트 표로 풉니다.
6. NTUSER.DAT 에서 `Devices`·`PrinterPorts` 의 값 이름과 `Windows` 키의 `Device` 값을 읽습니다.
7. 이미지에서 스풀 폴더의 파일 목록을 봅니다. 지워진 항목까지 보려면 MFT 를 직접 읽습니다.
8. SPL·SHD 가 있으면 사본을 헥스 편집기로 엽니다. 형식을 가정하지 말고 앞부분부터 확인합니다.

아래는 관찰 PC 에서 읽은 비트 값으로 만든 예시입니다. 검체에서 나온 값이 아닙니다.

```
Attributes 데이터 바이트    01 09 00 00
리틀 엔디언 정수            0x00000901

0x00000001   Queued            마지막 쪽까지 스풀한 뒤 인쇄
0x00000100   KeepPrintedJobs   인쇄가 끝난 작업을 남김
0x00000800   EnableBidi
```

- 이 프린터는 인쇄 작업을 남기도록 설정돼 있습니다. 스풀 폴더에 SPL·SHD 가 남았는지 확인할 대상입니다.

### 공개 도구로 한 번

- 라이브 PC 에서는 PowerShell `Get-Printer` 로 프린터마다 `KeepPrintedJobs` 같은 속성을 볼 수 있습니다.
- .NET `System.Printing.PrintQueueAttributes` 로 비트 이름을 확인할 수 있습니다.
- 오프라인 하이브는 레지스트리 뷰어로 `Printers` 키를 열어 값 전체를 기록해 둡니다.
- 이벤트 로그 뷰어로 PrintService 채널이 켜져 있었는지, 이벤트가 몇 건인지 봅니다.
- 도구 결과를 헥스로 읽은 `Attributes` 값과 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 | 링크 |
|---|---|---|
| 인쇄 이벤트 (307 등) | 문서, 소유자, 프린터, 포트, 크기, 쪽수 | [인쇄 이벤트](../event-logs/printservice-307.md) |
| 마스터 파일 테이블 | 스풀 폴더 파일의 생성·삭제 흔적과 시각 | [마스터 파일 테이블](../filesystem/mft.md) |
| USN 변경 저널 | 스풀 폴더 파일이 생기고 지워진 기록 | [USN 변경 저널](../filesystem/usnjrnl.md) |
| 바로가기 파일 | 가상 PDF 프린터로 만든 파일을 열었나 | [바로가기 파일](../file-folder-usage/lnk.md) |
| 최근 문서 | 가상 PDF 프린터로 만든 파일 | [최근 문서](../file-folder-usage/recentdocs.md) |
| 섀도 복사본 | 예전 스풀 폴더와 예전 하이브 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

- 인쇄를 자료 유출 경로로 볼 때의 흐름은 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md)에서 다룹니다.

## 실습

프린터를 쓴 흔적이 있는 공개 검체(NIST CFReDS 등)나, 시험 PC 에서 직접 인쇄해 본 이미지로 풀어 봅니다. 검체 설명에서 OS 판을 먼저 확인합니다.

1. `Printers` 하위 키를 모두 적고 실물 프린터와 가상 프린터로 나눕니다. 무엇을 근거로 나눴습니까?
2. 프린터마다 `Attributes` 를 풀어 봅니다. KeepPrintedJobs 나 Direct 가 켜진 프린터가 있습니까?
3. 사용자마다 기본 프린터를 확인합니다. 사용자별로 다릅니까?
4. 스풀 폴더에 SPL·SHD 가 있습니까? MFT 에 지워진 항목이 남아 있습니까?
5. PrintService/Operational 채널이 켜져 있었습니까? 307 이벤트가 있다면 같은 시각의 스풀 폴더 흔적과 맞춰 봅니다.

## 참고 문헌

1. Microsoft, "Local Print Provider - Windows drivers", Microsoft Learn (갱신 2025-07-18). https://learn.microsoft.com/en-us/windows-hardware/drivers/print/local-print-provider
2. Microsoft, "PRINTER_INFO_2 structure (Winspool.h)", Microsoft Learn (갱신 2021-01-07). https://learn.microsoft.com/en-us/windows/win32/printdocs/printer-info-2
3. Wine 프로젝트, `include/winspool.h` (`PRINTER_ATTRIBUTE_*` 값). https://raw.githubusercontent.com/wine-mirror/wine/master/include/winspool.h
