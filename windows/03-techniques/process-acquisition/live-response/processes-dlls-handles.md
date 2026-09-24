---
title: "프로세스·DLL·핸들 수집"
parent: "라이브 응답"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 3130
---

# 프로세스·DLL·핸들 수집 (Processes·DLLs·Handles)

## 한 줄 요약

켜진 시스템에서 실행 중인 프로세스 목록, 프로세스가 불러온 DLL, 프로세스가 연 핸들을 글자 파일로 남깁니다. Windows 기본 명령 `tasklist` 로 목록·서비스·모듈을 얻습니다. `tasklist` 에 없는 명령줄·부모 프로세스·시작 시각은 WMI 의 `Win32_Process` 클래스에서 얻습니다. 핸들 목록은 Sysinternals Handle 같은 도구로 얻습니다.

## 언제 쓰나

NIST SP 800-86 은 프로세스 목록의 쓰임을 이렇게 적습니다. 켜져 있는 서비스와 사용자가 돌리는 프로그램(암호화 도구가 한 예입니다)을 확인하고, 프로그램을 어떤 명령 옵션으로 실행했는지 봅니다. 돌아야 하는데 꺼졌거나 지워진 프로그램(백신과 방화벽이 한 예입니다)도 찾습니다.

OS 는 열린 파일 목록과 그 파일을 연 사용자·프로세스를 관리할 수 있고, 핸들 목록이 이 정보를 보여 줍니다.

NIST 순서에서 실행 중 프로세스는 넷째, 열린 파일은 다섯째입니다. 순서 전체와 도구 준비는 [수집 순서와 원칙](order-of-volatility.md)에서 다룹니다.

## 절차

NIST 는 Windows 에서 작업 관리자 화면보다 글자 목록이 낫다고 적습니다. 그래서 아래 단계는 모두 결과를 파일로 남깁니다. 명령 예의 `E:` 는 결과를 받는 외장 매체라고 가정한 것입니다.

1. **관리자 권한 명령 창을 엽니다.** 명령 파일은 도구 매체의 사본을 씁니다.
2. **프로세스 목록을 자세히 남깁니다.**
   ```
   tasklist /v /fo csv > E:\out\tasklist_v.csv
   ```
3. **프로세스마다 서비스를 남깁니다.**
   ```
   tasklist /svc /fo csv > E:\out\tasklist_svc.csv
   ```
4. **프로세스마다 불러온 모듈(DLL)을 남깁니다.**
   ```
   tasklist /m /fo csv > E:\out\tasklist_m.csv
   ```
   특정 DLL 을 불러온 프로세스만 보려면 `/m` 뒤에 모듈 이름을 줍니다.
5. **`Win32_Process` 를 읽습니다.** 명령줄, 부모 프로세스 ID, 시작 시각, 실행 파일 경로를 얻습니다. WMI 를 읽는 명령이나 스크립트라면 무엇이든 씁니다. 아래 "Win32_Process 의 속성" 표에서 남길 속성을 고릅니다.
6. **프로세스 소유자를 남깁니다.** `Win32_Process` 의 `GetOwner` 메서드를 쓰거나, PowerShell 에서 `Get-Process -IncludeUserName` 을 씁니다.
7. **핸들 목록을 남깁니다.** Sysinternals Handle 은 관리자 권한에서만 돌아갑니다.
   ```
   handle -a -u > E:\out\handle_all.txt
   ```
8. **결과 파일의 해시와 명령을 돌린 시각을 적습니다.**

## 도구

### tasklist

로컬 또는 원격 컴퓨터에서 실행 중인 프로세스 목록을 보여 주는 Windows 기본 명령입니다. 옛 명령 `tlist` 를 대신합니다.

| 옵션 | 뜻 |
|---|---|
| `/v` | 자세한 정보를 보여 줍니다 |
| `/svc` | 프로세스마다 서비스 정보를 잘리지 않게 보여 줍니다. 문서는 `/fo table` 과 함께 쓰는 옵션으로 적습니다 |
| `/m [모듈]` | 모듈 이름을 주면 그 DLL 을 불러온 작업만 보여 줍니다. 이름을 안 주면 작업마다 불러온 모듈을 모두 보여 줍니다 |
| `/fo {table \| list \| csv}` | 출력 형식 |
| `/nh` | 머리글을 뺍니다 |

문서는 잘리지 않은 정보를 보려면 `/v` 와 `/svc` 를 함께 쓰라고 적습니다. 필터로 거를 수 있는 이름은 `STATUS`, `IMAGENAME`, `PID`, `SESSION`, `SESSIONNAME`, `CPUtime`, `MEMUSAGE`(KB), `USERNAME`, `SERVICES`, `WINDOWTITLE`, `MODULES` 입니다. 원격 시스템에서는 `STATUS` 와 `WINDOWTITLE` 로 거를 수 없습니다.

CSV 로 받으면 칸은 아래처럼 나옵니다 (확인 범위: Windows 11 Home 10.0.26200, PC 한 대). `/svc` 도 CSV 로 칸이 나왔습니다.

| 명령 | CSV 칸 |
|---|---|
| `tasklist /v` | Image Name, PID, Session Name, Session#, Mem Usage, Status, User Name, CPU Time, Window Title |
| `tasklist /svc` | Image Name, PID, Services |
| `tasklist /m` | Image Name, PID, Modules |

`tasklist` 에는 명령줄, 부모 PID, 시작 시각 칸이 없습니다.

### Win32_Process 의 속성

`Win32_Process` 는 WMI 의 `root\CIMV2` 네임스페이스에 있는 클래스입니다. Windows Vista 와 Windows Server 2008 부터 지원합니다.

| 속성·메서드 | 뜻 |
|---|---|
| `ProcessId` | 프로세스 ID. 생성부터 종료까지만 유효합니다 |
| `ParentProcessId` | 이 프로세스를 만든 프로세스의 ID |
| `CreationDate` | 프로세스가 실행을 시작한 날짜 |
| `CommandLine` | 프로세스를 시작한 명령줄 |
| `ExecutablePath` | 실행 파일 경로. `SeDebugPrivilege` 권한 한정자가 붙어 있습니다 |
| `Name` | 실행 파일 이름. 아래 "함정과 한계" 3번을 봅니다 |
| `SessionId` | 로그온부터 로그오프까지의 세션 번호 |
| `HandleCount` | 이 프로세스가 연 핸들 개수 |
| `GetOwner` | 프로세스를 실행한 사용자 이름과 도메인 이름을 돌려줍니다 |
| `GetOwnerSid` | 소유자 SID 를 돌려줍니다 |

SID 형식은 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md)에서 다룹니다. PowerShell 5.1 의 `Get-Process -IncludeUserName` 도 관리자 권한에서 `UserName` 을 돌려줬습니다 (확인 범위: Windows 11 Home 10.0.26200, PC 한 대).

### Sysinternals Handle

시스템의 모든 프로세스가 연 핸들을 보여 주는 공개 도구입니다. 어떤 프로그램이 파일을 열었는지 찾을 수 있고, 한 프로그램이 연 핸들의 객체 종류와 이름도 볼 수 있습니다. 아래는 2022-10-26 판 문서의 내용입니다.

| 옵션 | 뜻 |
|---|---|
| (없음) | 파일을 가리키는 핸들만 보여 줍니다 |
| `-a` | 파일 말고도 포트, 레지스트리 키, 동기화 객체, 스레드, 프로세스 핸들을 모두 보여 줍니다 |
| `-p` | 이름이 주어진 글자로 시작하는 프로세스나, 주어진 PID 로 좁힙니다 |
| `-u` | 핸들을 소유한 사용자 이름을 보여 줍니다 |
| `-g` | 허용된 접근 권한을 보여 줍니다 |
| `-s` | 종류별 핸들 개수를 보여 줍니다 |
| `-v`, `-vt` | CSV 로 출력합니다 |
| `-c` | 핸들을 닫습니다. 수집 중에는 쓰지 않습니다 |

출력은 프로세스마다 점선으로 나뉩니다. 점선 아래에 프로세스 이름과 PID 가 오고, 그 밑에 핸들마다 한 줄이 오며, 한 줄에는 핸들 값(16진), 객체 종류, 객체 이름이 나옵니다.

## 함정과 한계

1. **`tasklist` 만 남깁니다.** 명령줄, 부모 PID, 시작 시각이 빠집니다. `Win32_Process` 결과를 함께 남깁니다.
2. **부모 PID 를 그대로 믿습니다.** PID 는 다시 쓰입니다. 부모가 이미 끝났을 수 있고, 같은 번호를 다시 받은 다른 프로세스를 가리킬 수도 있습니다. Microsoft 문서는 `CreationDate` 를 비교해 부모가 자식보다 먼저 생겼는지 확인하라고 적습니다.
3. **`Name` 만 보고 실행 파일을 판단합니다.** 문서는 `Name` 이 실행 파일에 새겨진 이름이라 파일 이름을 바꿔도 바뀌지 않는다고 적습니다. 실제로는 이름을 바꾼 실행 파일을 돌리면 `Name` 과 `tasklist` 의 Image Name 모두 바꾼 이름으로 나왔습니다 (확인 범위: Windows 11 Home 10.0.26200, PC 한 대, 시스템 명령을 다른 이름으로 복사해 실행). 그래서 `ExecutablePath` 의 경로와 파일의 버전 정보를 함께 봅니다.
4. **빈 칸을 숨긴 흔적으로 읽습니다.** 관리자 권한으로도 352개 가운데 25개 프로세스는 `CommandLine` 과 `ExecutablePath` 가 비어 있었습니다. 대부분 System, Secure System, Registry, smss, csrss, wininit, services, lsass, LsaIso, Memory Compression, MsMpEng 같은 보호되는 프로세스였습니다. 같은 25개는 `tasklist /m` 의 Modules 칸이 "N/A" 였습니다 (확인 범위: Windows 11 Home 10.0.26200, PC 한 대).
5. **`TerminationDate` 와 `Status` 로 상태를 판단합니다.** `TerminationDate` 는 프로세스 핸들을 열어 두지 않으면 NULL 입니다. `Status` 는 구현되지 않아 늘 NULL 입니다.
6. **Handle 의 `-c` 를 씁니다.** 핸들을 닫으면 앱이나 시스템이 불안정해질 수 있다고 문서가 경고합니다. 증거를 바꾸는 옵션이기도 합니다.
7. **목록에 없으면 실행되지 않았다고 봅니다.** 커널 수준 루트킷이 있으면 사용자 수준 도구는 숨긴 프로세스를 보지 못할 수 있습니다. 도구를 믿는 범위는 [수집 순서와 원칙](order-of-volatility.md)에서 다룹니다.
8. **원격으로 같은 필터를 씁니다.** `tasklist` 의 `STATUS` 와 `WINDOWTITLE` 필터는 원격 시스템에서 쓸 수 없습니다.

## 결과를 어떻게 해석하나

### 부모와 자식

`ParentProcessId` 로 프로세스 나무를 그립니다. 부모의 `CreationDate` 가 자식보다 늦으면, 그 부모 PID 는 원래 부모가 끝난 뒤 다시 쓰인 번호입니다. 이런 경우 진짜 부모는 이 목록만으로 알 수 없습니다. 끝난 프로세스의 기록은 [프로세스 생성](../../../02-artifacts/event-logs/4688.md) 이벤트, [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md), [메모리 분석](../../analysis/memory-forensics/index.md)에서 찾습니다.

### 서비스와 DLL

`/svc` 결과로 서비스가 어느 프로세스 안에서 도는지 보고, 서비스 등록 정보는 [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md)와 맞춰 봅니다. `/m` 결과로는 의심 DLL 을 불러온 프로세스를 찾고, DLL 파일은 [의심 실행 파일 선별](../../analysis/code-signing-yara.md)과 [실행 파일 메타데이터](../../../02-artifacts/embedded-metadata/pe-header-version-info-digital-signature.md)로 이어서 봅니다.

### 세션과 사용자

`SessionId` 와 `tasklist /v` 의 Session#, User Name 으로 프로세스가 어느 세션에서 돌았는지 봅니다. 로그온 세션과 잇는 방법은 [로그온 세션·클립보드·화면 수집](sessions-clipboard-screen.md)에서 다룹니다.

### 핸들

핸들 목록은 수집한 순간에 어떤 프로세스가 어떤 파일·레지스트리 키를 열고 있었는지 보여 줍니다. 파일을 연 기록을 디스크에서 찾는 방법은 [이 파일을 누가 언제 열었나](../../../04-scenarios/activity/file-access.md)에서 다룹니다.

### 증명하는 것 / 증명하지 못하는 것

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 수집 시각에 이 프로세스가 이 명령줄로 돌고 있었습니다 | 누가 직접 실행했는지. 다른 프로세스나 예약 작업이 띄웠을 수 있습니다 |
| `CreationDate` 무렵에 프로세스가 시작했습니다 (대상 시스템 시계 기준) | 수집 전에 끝난 프로세스. 목록에는 지금 도는 것만 나옵니다 |
| 수집 시각에 이 프로세스가 이 파일 핸들을 열고 있었습니다 | 파일을 언제부터 열었는지, 무엇을 읽거나 썼는지 |

아래 보고서 문장의 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "2025-03-14 10:20 (KST) 에 수집한 목록에서 PID 4120 프로세스가 `C:\sample\a.exe -k` 명령줄로 실행 중이었습니다. 이 프로세스의 시작 시각은 대상 시스템 시계로 같은 날 09:55 입니다."
- 쓰면 안 되는 문장: "사용자가 09:55 에 a.exe 를 실행했습니다."

## 참고 문헌

- K. Kent, S. Chevalier, T. Grance, H. Dang, "NIST SP 800-86: Guide to Integrating Forensic Techniques into Incident Response", NIST, 2006-08 — https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
- Microsoft Learn, "tasklist" — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tasklist
- Microsoft Learn (Sysinternals), "Handle", Mark Russinovich, 2022-10-26 — https://learn.microsoft.com/en-us/sysinternals/downloads/handle
- Microsoft Learn, "Win32_Process class" — https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process
