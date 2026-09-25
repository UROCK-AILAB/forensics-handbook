---
title: "이벤트 로그 형식"
parent: "기반 · 데이터베이스·로그 형식"
nav_order: 320
has_children: true
has_toc: false
---

# 이벤트 로그 형식 (EVTX·EVT·ETL)

## 한 줄 요약

Windows Vista 부터 이벤트 로그는 EVTX 형식으로 저장됩니다. XP·Server 2003 까지는 EVT 형식을 썼습니다. ETW (Event Tracing for Windows) 추적 세션은 이와 별도로 ETL 형식의 `.etl` 파일을 남깁니다. 세 형식 모두 이진 파일이라서 구조를 알면 도구가 보여 준 결과를 헥스로 직접 확인할 수 있습니다.

## 왜 중요한가

- 이벤트 아티팩트는 모두 이 파일에서 읽습니다. [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md), [서비스 설치](../../../02-artifacts/event-logs/7045-4697.md), [프로세스 생성](../../../02-artifacts/event-logs/4688.md), [PowerShell 실행 기록](../../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md) 이 그 예입니다.
- Vista 에서 이벤트 기록 구조를 새로 짜면서 EVT 는 이때부터 쓰지 않습니다. Microsoft 문서도 Vista 부터 이 파일 형식을 더 이상 쓰지 않는다고 적습니다. 옛 PC 의 이미지에서는 EVT 를 읽어야 합니다.
- 이벤트 뷰어가 보여 주는 설명 문장은 로그 파일 안에 없고, 레코드에는 문장의 빈자리(`%1`, `%2` …)에 들어갈 값만 있습니다. 문장 틀은 공급자 (Provider) 의 메시지 파일에 있습니다.
- 메시지를 보여 주는 프로그램마다 레지스트리와 메시지 파일을 따로 읽습니다. 그래서 프로그램마다 이벤트 뷰어와 다른 문장이 나올 수 있습니다.
- EVTX 파일 안에는 정상 레코드 목록에서 빠진 옛 레코드가 남을 수 있습니다.
- 손상된 EVTX 파일은 도구마다 읽어 내는 건수가 달랐습니다(libevtx 명세의 사례). 한 도구의 건수만 믿지 않습니다.
- `.etl` 파일의 머리 정보에는 세션 시작 시각과 시스템 부팅 시각이 남습니다. 확인 PC 에서는 번호가 붙은 `.etl` 파일에 이전 부팅의 시각도 남아 있었습니다.
- EVTX 와 ETW 는 레지스트리 설정에서 이어집니다. 확인 PC 의 ETW 설정 키(Autologger)에는 System 채널을 가리키는 세션이 있었습니다. 자세한 값은 [ETW 추적 로그 (ETL)](etl.md) 에 있습니다.

## 한눈에 보기

> 그림 자리: 같은 PC 안에서 EVTX(`winevt\Logs`)·ETL(`LogFiles\WMI`) 파일이 놓인 폴더와, 옛 PC 의 EVT(`System32\config`) 폴더를 나란히 보여 주는 그림. 각 파일의 머리 → 저장 단위(청크·레코드·버퍼) 순서도 함께 표시

### 위치와 버전

| 형식 | 위치 | Windows 버전 | 알려 주는 것 |
|---|---|---|---|
| EVTX | `C:\Windows\System32\winevt\Logs\` | Vista 이후 | 로그(채널)마다 이벤트 레코드 |
| EVT | NT 4: `C:\WINNT\System32\config`<br>2000 이후: `C:\Windows\System32\config` | NT 4 ~ Server 2003 | AppEvent.Evt(응용 프로그램)·SecEvent.Evt(보안)·SysEvent.Evt(시스템) 등의 이벤트 레코드 |
| ETL | AutoLogger 세션에 FileName 이 없으면 `%SystemRoot%\System32\LogFiles\WMI\<세션이름>.etl` | AutoLogger 는 Vista 이후. 그 전에는 Global Logger | 추적 세션의 이벤트, 세션 시작 시각, 시스템 부팅 시각 |

- 로그 설정 키에 File 값이 없으면 EVTX 파일은 `%SystemRoot%\system32\winevt\logs\` 에 키 이름을 딴 이름으로 생깁니다.
- libevt 명세는 EVT 를 NT 4·2000·XP·2003 에서 시험했습니다.
- libevtx 명세는 EVTX 를 Vista·2008·7·8·10(1903 ~ 20H2)·11(21H2) 에서 시험했습니다.

### 세 형식 비교

| | EVTX | EVT | ETL |
|---|---|---|---|
| 파일 머리 | 4096바이트 파일 헤더 | 48바이트 헤더 | 첫 이벤트에 세션 머리 정보 (TRACE_LOGFILE_HEADER) |
| 그 뒤 | 65536바이트 청크 여러 개 | 레코드들과 파일 끝 레코드 | 같은 크기의 버퍼들(확인 PC 관찰) |
| 레코드 본문 | 이진 XML | 고정 칸 뒤에 문자열과 데이터 | 공급자 종류마다 형식이 다릅니다 |
| 시각 | FILETIME, UTC | 32비트 유닉스 시각, UTC | 1601-01-01 부터 센 100ns 단위(FILETIME 과 같은 단위) |

시각 값을 푸는 법은 [시각 값 형식](../../value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.

### 채널과 공급자

- EVTX 의 채널 (Channel) 종류는 Admin·Analytic·Debug·Operational 넷입니다.
- 채널 설정은 `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WINEVT\Channels` 아래에 있습니다. 공급자 설정은 `WINEVT\Publishers` 아래에 있습니다.

확인 PC 에서 본 규모입니다.

- `winevt\Logs` 안의 `.evtx` 파일은 225개였습니다.
- `WINEVT\Channels` 아래 채널 키는 1,169개, `WINEVT\Publishers` 아래 공급자 키는 933개였습니다.
- 채널 키 수와 `.evtx` 파일 수는 같지 않았습니다.
- `Microsoft-Windows-TaskScheduler/Operational` 채널 키에는 OwningPublisher·Enabled(0)·MaxSize(0xa00000)·Type(1) 값이 있었습니다. 이 채널의 이벤트는 [예약 작업 이벤트](../../../02-artifacts/event-logs/taskscheduler-4698.md) 에서 다룹니다.
- 채널 키의 Type 숫자가 어느 채널 종류에 대응하는지는 확인하지 못했습니다.

## 읽는 순서

1. [EVTX 파일 구조 (File Header·Chunk·Record)](file-header-chunk-record.md) — 파일 헤더·청크·레코드를 헥스로 따라갑니다. 체크섬 범위, 한 바퀴 돈 로그의 헤더 모양, 로그 크기·덮어쓰기 설정 키를 다룹니다.
2. [이진 XML 해석 (Binary XML·Template)](binary-xml-template.md) — 토큰과 템플릿으로 레코드 본문을 XML 로 되살립니다. 레코드 하나만 떼어 내면 풀 수 없는 까닭도 다룹니다.
3. [공급자와 메시지 파일 (Provider·Message Table)](provider-message-table.md) — 레지스트리로 메시지 파일을 찾고, 이벤트 식별자로 설명 문장을 고릅니다. WEVT_TEMPLATE 리소스 구조도 다룹니다.
4. [구형 EVT 형식 (Windows XP·2003)](windows-xp-2003.md) — 48바이트 헤더, 레코드, 파일 끝 레코드와 원형 버퍼 동작을 다룹니다.
5. [파일 안에 남은 지운·손상 레코드 (Chunk Slack·Corrupted EVTX)](chunk-slack-corrupted-evtx.md) — 청크 빈 공간에서 진짜 레코드를 골라내는 조건을 다룹니다. 손상 파일을 도구마다 다르게 읽은 사례도 다룹니다.
6. [ETW 추적 로그 (ETL)](etl.md) — AutoLogger 설정, 로그 모드, `.etl` 머리 정보의 시각과 잃은 이벤트 수를 다룹니다.

## 함께 볼 페이지

- [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) — 어떤 이벤트를 기록할지 정하는 설정을 다룹니다.
- [이벤트 로그 삭제](../../../02-artifacts/event-logs/1102-104.md) — 로그를 지운 흔적을 다룹니다.
- [켜짐·꺼짐](../../../02-artifacts/event-logs/power-on-off-events.md) — `.etl` 머리의 부팅 시각과 맞춰 봅니다.
- [레지스트리 하이브 구조](../registry-hive/index.md) — 로그 설정·채널·공급자·AutoLogger 키를 읽습니다.
- [실행 파일 메타데이터](../../../02-artifacts/embedded-metadata/pe-header-version-info-digital-signature.md) — 메시지 파일은 PE 실행 파일입니다.
- [문자 인코딩](../../value-decoding/utf-16le-utf-8-cp949.md) — EVTX·EVT 의 문자열은 UTF-16LE 입니다.
- [이벤트 로그 규칙 검색](../../../03-techniques/analysis/sigma-rules.md) — 규칙으로 이벤트를 골라냅니다.
- [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) — 여러 로그의 시각을 한 줄로 모읍니다.
- [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) — 도구마다 다른 건수와 값을 맞춰 봅니다.

## 참고 문헌

1. Joachim Metz, "Windows XML Event Log (EVTX) format", libyal/libevtx (문서 버전 0.0.27, 2026-07) — https://raw.githubusercontent.com/libyal/libevtx/main/documentation/Windows%20XML%20Event%20Log%20(EVTX).asciidoc
2. Joachim Metz, "Windows Event Viewer Log (EVT) format", libyal/libevt (문서 버전 0.0.16) — https://raw.githubusercontent.com/libyal/libevt/main/documentation/Windows%20Event%20Log%20(EVT)%20format.asciidoc
3. Microsoft Learn, "Event Log File Format" — https://learn.microsoft.com/en-us/windows/win32/eventlog/event-log-file-format
4. Microsoft Learn, "Eventlog Key" — https://learn.microsoft.com/en-us/windows/win32/eventlog/eventlog-key
5. Microsoft Learn, "About Event Tracing" — https://learn.microsoft.com/en-us/windows/win32/etw/about-event-tracing
6. Microsoft Learn, "Configuring and Starting an AutoLogger Session" — https://learn.microsoft.com/en-us/windows/win32/etw/configuring-and-starting-an-autologger-session
7. Microsoft Learn, "TRACE_LOGFILE_HEADER structure (evntrace.h)" — https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-trace_logfile_header
8. Joachim Metz, "Windows Event manifest binary format", libyal/libfwevt (문서 버전 0.0.9, 2024-01) — https://raw.githubusercontent.com/libyal/libfwevt/main/documentation/Windows%20Event%20manifest%20binary%20format.asciidoc
