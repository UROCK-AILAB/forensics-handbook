---
title: "인쇄해서 가져갔나"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 3650
---

# 인쇄해서 가져갔나 (Print)

> 상위 허브: [자료를 밖으로 빼돌렸나 (Data Exfiltration)](index.md)

이 페이지는 자료를 종이로 인쇄했는지, 또는 PDF 프린터 같은 가상 프린터로 파일을 만들었는지 확인하는 순서를 다룹니다. 인쇄 이벤트와 스풀 파일의 구조는 [인쇄 이벤트](../../../02-artifacts/event-logs/printservice-307.md) 와 [인쇄 흔적](../../../02-artifacts/external-devices/print-spooler-spl-shd.md) 에서 다룹니다.

이벤트의 메시지 틀과 칸 이름, 레지스트리 값은 Windows 11 Home 25H2(빌드 26200.9457) 기준입니다.

## 조사 질문

- 조사 기간에 누가 어떤 문서를 어느 프린터로 인쇄했습니까?
- 그 프린터는 종이 프린터였습니까, 파일을 만드는 가상 프린터였습니까?
- 인쇄 기록이 없을 때 "인쇄하지 않았다" 고 말할 수 있습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| PrintService/Operational 로그가 켜져 있었나 | 인쇄 이벤트 307 은 이 로그가 켜져 있을 때만 남으며, 꺼져 있는 PC 도 있습니다. 로그 설정을 읽는 법은 [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 다룹니다. |
| 로그 크기 | 이 로그의 최대 크기가 1MB 이고 순환 방식이면, 켜져 있어도 오래된 인쇄 기록은 새 기록에 밀려 사라집니다. |
| 설치된 프린터 | 종이 프린터와 가상 프린터를 먼저 나눕니다. 아래 "프린터 목록과 스풀 폴더" 를 봅니다. |
| 시간대 | 이벤트 시각과 다른 기록의 시각을 같은 기준으로 맞춥니다([시간대 설정](../../../02-artifacts/system-account/time-zone.md)). |
| 수집 범위 | 이벤트 로그 폴더, SYSTEM 하이브, 스풀 폴더, 사용자 프로필(바로가기 파일·최근 문서)을 확보합니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | PrintService/Operational 307 | 작업 번호, 문서 이름, 사용자, 컴퓨터, 프린터, 포트, 바이트 수, 쪽수 | [인쇄 이벤트](../../../02-artifacts/event-logs/printservice-307.md) |
| 2 | PrintService/Operational 842 | 작업 번호, 인쇄 프로세서, 프린터, 드라이버, 격리 모드 | [인쇄 이벤트](../../../02-artifacts/event-logs/printservice-307.md) |
| 3 | SYSTEM 하이브의 프린터 목록 | 프린터 이름, 포트, 인쇄 프로세서, 데이터 형식, 스풀 폴더 위치 | [인쇄 흔적](../../../02-artifacts/external-devices/print-spooler-spl-shd.md) |
| 4 | 스풀 폴더 | 남아 있다면 인쇄 작업 파일 | [인쇄 흔적](../../../02-artifacts/external-devices/print-spooler-spl-shd.md) |
| 5 | 바로가기 파일·최근 문서·점프리스트 | 인쇄한 문서를 연 흔적, PDF 로 인쇄해 만든 파일 | [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md), [최근 문서](../../../02-artifacts/file-folder-usage/recentdocs.md), [점프리스트](../../../02-artifacts/file-folder-usage/jump-lists.md) |

## 인쇄 이벤트

로그 파일을 읽는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다.

### 307

307 은 `Microsoft-Windows-PrintService/Operational` 채널의 이벤트이고, 수준은 정보, 이벤트 버전은 0 입니다. 메시지 틀은 아래와 같습니다.

```
Document %1, %2 owned by %3 on %4 was printed on %5 through port %6. Size in bytes: %7. Pages printed: %8. No user action is required.
```

칸 이름은 param1~param8 입니다. 칸 이름만으로는 뜻을 알 수 없으므로 메시지 틀에서 칸의 자리를 보고 뜻을 읽습니다.

| 칸 | 메시지 틀 자리 | 뜻 |
|---|---|---|
| param1 | %1 | 작업 번호 |
| param2 | %2 | 문서 이름 |
| param3 | %3 | 사용자 |
| param4 | %4 | 컴퓨터 |
| param5 | %5 | 프린터 |
| param6 | %6 | 포트 |
| param7 | %7 | 바이트 수 |
| param8 | %8 | 인쇄한 쪽수 |

### 842

같은 채널에 842 도 있습니다. 메시지 틀의 앞부분은 아래와 같습니다. 뒷부분은 줄였습니다.

```
The print job %1 was sent through the print processor %2 on printer %3, driver %4, in the isolation mode %5 …
```

칸 이름은 JobId, Processor, Printer, Driver, IsolationMode, Error 입니다. 842 의 JobId 와 307 의 작업 번호로 같은 인쇄 작업의 두 이벤트를 잇는데, 작업 번호만으로 묶지 않고 시각이 가까운지도 봅니다.

### 로그가 꺼져 있을 때

PrintService/Operational 로그는 꺼져 있을 수 있습니다. 기본값이 꺼짐인지는 판마다 다를 수 있어 검체에서 확인합니다. 꺼져 있던 기간에는 307 이 남지 않으므로 307 이 없다는 것이 인쇄하지 않았다는 뜻은 아닙니다. 이때 PrintService/Admin 로그는 켜져 있어도 이벤트가 한 건도 없을 수 있습니다.

## 프린터 목록과 스풀 폴더

### 프린터 목록

프린터 설정은 아래 키에 있습니다.

```
HKLM\SYSTEM\CurrentControlSet\Control\Print\Printers
    DefaultSpoolDirectory    (스풀 폴더 위치)
    <프린터 이름>\
        Attributes
        Port
        Print Processor
        Datatype
```

프린터마다 `Printers\<프린터 이름>` 하위 키가 있고, 하위 키에는 `Attributes`, `Port`, `Print Processor`, `Datatype` 값이 있습니다. 인쇄 프로세서는 보통 `winprint`, 데이터 형식은 `RAW` 입니다.

이미지에서 볼 때는 SYSTEM 하이브에서 실제로 쓰던 컨트롤 세트를 먼저 정하고 그 아래에서 찾습니다([레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)).

### 가상 프린터

종이를 쓰지 않는 가상 프린터에는 아래와 같은 것이 있습니다.

| 프린터 이름 | Port 값 |
|---|---|
| Microsoft Print to PDF | `PORTPROMPT:` |
| Hancom PDF | `Hancom PDF Port` |
| OneNote (Desktop) | `nul:` |

PDF 프린터로 인쇄하면 종이가 아니라 PDF 파일이 생기므로, 307 의 프린터(%5)·포트(%6) 칸을 이 목록과 맞춰 종이 프린터인지 가립니다. PDF 프린터로 만든 파일은 바로가기 파일·최근 문서로 추적합니다. 그 PDF 가 다시 밖으로 나갔는지는 [USB 로 무엇을 가져갔나](usb.md), [메일로 밖에 보냈나](email.md), [웹메일·웹하드로 올렸나](web-upload.md) 를 따라 봅니다.

### 스풀 폴더

`DefaultSpoolDirectory` 값은 보통 `C:\Windows\system32\spool\PRINTERS` 이고, 인쇄 작업이 없을 때 이 폴더는 비어 있을 수 있습니다.

스풀 폴더의 SPL(인쇄 데이터)·SHD(작업 정보) 파일 구조, 인쇄가 끝난 뒤 지워지는지, "인쇄한 문서 유지 (Keep printed documents)" 설정과 `Attributes` 값의 관계는 [인쇄 흔적](../../../02-artifacts/external-devices/print-spooler-spl-shd.md) 에서 다룹니다.

스풀 폴더가 비어 있다는 것만으로 인쇄하지 않았다고 보지 않으며, 스풀 파일이 지워졌다면 [지운 파일의 흔적 찾기](../../activity/deleted-file-traces.md) 순서로 찾아봅니다.

## 분석 흐름

1. PrintService/Operational 로그가 켜져 있었는지, 가장 오래된 이벤트가 언제인지 확인합니다.
2. 켜져 있었다면 307 을 모두 뽑아 표로 만듭니다. 칸은 시각, 작업 번호, 문서 이름, 사용자, 컴퓨터, 프린터, 포트, 바이트 수, 쪽수입니다.
3. 842 를 작업 번호와 시각으로 307 에 잇습니다.
4. SYSTEM 하이브에서 프린터 목록을 뽑아 종이 프린터와 가상 프린터를 나눕니다.
5. 307 의 문서 이름을 바로가기 파일·최근 문서·점프리스트와 맞춰 디스크의 어느 파일인지 좁힙니다.
6. 가상 프린터로 인쇄했다면 만든 파일을 찾습니다. 그 파일이 이후 밖으로 나갔는지 다른 하위 페이지로 이어 봅니다.
7. 스풀 폴더에 남은 파일이 있으면 사본으로 확보합니다.
8. 로그가 꺼져 있었다면 인쇄 여부는 "정하지 못함" 으로 적습니다. 원본 문서를 연 흔적은 따로 적습니다.
9. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **307 이 없으니 인쇄하지 않았다고 봅니다.** 로그가 꺼져 있었거나 기록이 밀려났을 수 있습니다.
2. **스풀 폴더가 비었으니 인쇄하지 않았다고 봅니다.** 인쇄 작업이 끝나면 스풀 폴더는 비어 있을 수 있습니다.
3. **PDF 프린터 기록을 종이 인쇄로 적습니다.** 프린터 이름과 포트로 가상 프린터인지 먼저 가립니다.
4. **307 의 문서 이름을 디스크의 파일 경로로 읽습니다.** 문서 이름은 메시지 틀의 한 자리입니다. 디스크의 어느 파일인지는 다른 기록과 맞춰 정합니다.
5. **307 의 사용자 칸으로 사람을 정합니다.** 이 칸은 계정 이름입니다. 그 시각에 그 계정을 쓴 사람은 [그 시각에 PC 를 쓴 사람이 누구인가](../../activity/user-attribution.md) 순서로 따로 확인합니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 고객 명단을 인쇄해 가져갔습니다."
- 쓸 문장: "Microsoft-Windows-PrintService/Operational 로그에 ○○(UTC) 에 기록된 307 이벤트가 있습니다. 이 이벤트에는 사용자 ○○ 의 문서 ○○ 를 프린터 ○○(포트 ○○) 로 ○쪽 인쇄한 작업이 적혀 있습니다. 이 기록은 그 시각에 해당 문서의 인쇄 작업이 이 프린터로 넘어갔음을 보여 줍니다. 인쇄물을 누가 가져갔는지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [인쇄 이벤트](../../../02-artifacts/event-logs/printservice-307.md) · [인쇄 흔적](../../../02-artifacts/external-devices/print-spooler-spl-shd.md) — 307 과 스풀 파일의 구조입니다.
- [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) · [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) — 로그가 켜져 있었는지, 로그 파일을 어떻게 읽는지입니다.
- [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) — 프린터 목록 키를 이미지에서 찾는 법입니다.
- [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md) · [최근 문서](../../../02-artifacts/file-folder-usage/recentdocs.md) · [점프리스트](../../../02-artifacts/file-folder-usage/jump-lists.md) · [오피스 사용 흔적](../../../02-artifacts/file-folder-usage/microsoft-office/index.md) — 인쇄한 문서를 연 흔적입니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](../../activity/user-attribution.md) — 계정과 사람을 잇습니다.
- [퇴사 전 자료를 모으고 압축했나 (Staging)](staging.md) — 인쇄하기 전에 자료를 모은 흔적입니다.

## 참고 문헌

외부 참고 문헌은 없습니다. 메시지 틀과 칸 이름은 PrintService 이벤트 공급자 메타데이터에 적힌 것입니다.
