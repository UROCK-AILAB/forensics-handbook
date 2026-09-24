---
title: "크래시 덤프"
parent: "메모리 분석"
grand_parent: "기법 · 분석"
nav_order: 3250
---

# 크래시 덤프 (MEMORY.DMP·Minidump)

> 상위 허브: [메모리 분석 (Memory Forensics)](index.md)

## 한 줄 요약

크래시 덤프 (Crash Dump) 는 시스템이나 프로그램이 멈춘 순간의 메모리를 담은 파일입니다.
커널 크래시 덤프는 Windows 가 파란 화면, 곧 버그 체크 (Bug Check) 때 만들고 [1], 사용자 모드 덤프는 프로그램이 죽을 때 WER 로컬 덤프 설정에 따라 남습니다 [2].

## 언제 쓰나

- 파란 화면이 난 뒤, 그 순간 올라와 있던 드라이버와 멈춘 프로세스를 볼 때 씁니다.
- 전원이 꺼진 PC 에서 메모리 조각을 찾을 때 씁니다.
- 디스크에서 덤프 파일을 찾았을 때, 무엇이 언제 만든 파일인지 가릴 때 씁니다.
- lsass 같은 프로세스의 덤프가 남았는지 볼 때 씁니다. 자격증명과의 관계는 [메모리 속 문자열·자격증명·암호 키](strings-credentials-keys.md) 에 있습니다.

## 커널 크래시 덤프 종류

Windows 는 버그 체크 때 덤프 파일을 만들 수 있고, 만들지 않게 설정할 수도 있습니다 [1].
아래 표는 Microsoft 문서 "Memory dump file options"(KB 254649) 에서 확인한 내용입니다 [1].

| 종류 | 담는 것 | 필요한 페이지 파일 | 다음 크래시 때 |
|---|---|---|---|
| 완전 메모리 덤프 (Complete Memory Dump) | 시스템 메모리 전체. 실행 중이던 프로세스의 자료가 들어 있을 수 있습니다 | 로컬 볼륨에 물리 RAM + 257MB 이상 | 이전 파일을 덮어씁니다 |
| 커널 메모리 덤프 (Kernel Memory Dump) | 커널·HAL·커널 모드 드라이버의 메모리. 할당하지 않은 메모리와 사용자 모드 프로그램 메모리는 없습니다 | 이 글의 참고 문헌에 나오지 않습니다 | "기존 파일 덮어쓰기" 설정이 켜져 있으면 덮어씁니다 |
| 작은 메모리 덤프 (Small Memory Dump) | 아래 목록 | 부트 볼륨에 2MB 이상 | 이전 파일을 남기고 새 이름으로 만듭니다 |
| 활성 메모리 덤프 (Active Memory Dump) | 이 글의 참고 문헌에는 자세한 설명이 없습니다 | — | — |

- 문서는 32비트 시스템의 커널 메모리가 보통 150MB ~ 2GB 라고 적습니다 [1].
- 자동 메모리 덤프 (Automatic Memory Dump) 도 있습니다. 아래 CrashDumpEnabled 표에 값이 있습니다 [1].
- 활성·자동 메모리 덤프는 별도 Microsoft 문서가 자세히 설명합니다. 그 문서는 이 글의 참고 문헌에 들지 않습니다.

### 작은 메모리 덤프에 든 것

작은 메모리 덤프에는 아래 내용이 들어 있습니다 [1].

- 중지 메시지와 그 인수
- 로드된 드라이버 목록
- 멈춘 프로세서의 PRCB
- 멈춘 프로세스의 EPROCESS
- 멈춘 스레드의 ETHREAD
- 멈춘 스레드의 커널 모드 호출 스택

작은 메모리 덤프는 크래시마다 새 파일을 만들어 폴더에 쌓고, 파일 이름에는 날짜가 들어갑니다 [1].
문서의 예 `Mini022900-01.dmp` 는 2000년 2월 29일의 첫 덤프입니다 [1].
요즘 Windows 가 쓰는 이름 형식은 이 글의 참고 문헌으로 확인하지 못했습니다.

## 설정 레지스트리 — CrashControl

커널 크래시 덤프 설정은 `HKLM\System\CurrentControlSet\Control\CrashControl` 에 있습니다 [1].

| 값 | 형식 | 문서에 나온 값 [1] |
|---|---|---|
| CrashDumpEnabled | REG_DWORD | 0 = 없음, 1 = 완전, 2 = 커널, 3 = 작은 덤프, 7 = 자동 메모리 덤프 |
| FilterPages | 이 글의 참고 문헌에 나오지 않음 | CrashDumpEnabled 가 1 이고 FilterPages 가 1 이면 활성 메모리 덤프입니다 |
| DumpFile | REG_EXPAND_SZ | `%SystemRoot%\Memory.dmp` |
| MinidumpDir | REG_EXPAND_SZ | `%SystemRoot%\Minidump` |
| Overwrite | REG_DWORD | 1 |
| AutoReboot | REG_DWORD | 1 |
| LogEvent | REG_DWORD | 1 |
| SendAlert | REG_DWORD | 1 |

- DumpFile, MinidumpDir, Overwrite, AutoReboot, LogEvent, SendAlert 는 문서에 값의 예만 있고 뜻 설명은 따로 없습니다 [1].
- 바뀐 설정은 재부팅해야 적용됩니다 [1].
- Windows 버전별 기본값은 이 글의 참고 문헌으로 확인하지 못했습니다. 이미지마다 값을 직접 읽습니다.
- 디스크 이미지에서 떼어 낸 SYSTEM 하이브를 읽을 때는 경로의 `CurrentControlSet` 부분을 실제로 쓰던 제어 집합으로 바꿔 읽습니다. 방법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.

## 사용자 모드 덤프 — WER 로컬 덤프

Windows Server 2008 과 Windows Vista SP1 부터 WER (Windows Error Reporting) 로 로컬 덤프를 남길 수 있습니다 [2].
사용자 모드 프로그램이 죽을 때 그 프로그램의 전체 덤프를 로컬에 남기는 기능으로, 기본으로 꺼져 있고 켜려면 관리자 권한이 필요합니다 [2].

설정 키는 `HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps` 입니다 [2].

| 값 | 형식 | 기본값 | 뜻 [2] |
|---|---|---|---|
| DumpFolder | REG_EXPAND_SZ | `%LOCALAPPDATA%\CrashDumps` | 덤프를 저장할 폴더입니다 |
| DumpCount | REG_DWORD | 10 | 남길 덤프 수입니다. 넘으면 가장 오래된 덤프를 새 것으로 바꿉니다 |
| DumpType | REG_DWORD | 1 | 0 = 사용자 지정, 1 = 미니 덤프, 2 = 전체 덤프 |
| CustomDumpFlags | REG_DWORD | — | DumpType 이 0 일 때만 씁니다. MINIDUMP_TYPE 값의 조합입니다. 문서의 예는 0x00000121 입니다 |

서비스가 죽으면 서비스 계정의 프로필 폴더에 덤프를 씁니다 [2].

| 서비스 계정 | 덤프를 쓰는 폴더 |
|---|---|
| System | `%WINDIR%\System32\Config\SystemProfile` |
| Network Service, Local Service | `%WINDIR%\ServiceProfiles` |

- LocalDumps 아래에 프로그램 이름으로 키를 만들면 그 프로그램에는 전역 설정 대신 그 키의 설정을 씁니다 [2]. 문서의 예는 `LocalDumps\MyApplication.exe` 입니다.
- 자체 크래시 보고를 하는 프로그램은 이 기능의 대상이 아닙니다 [2].
- 프로그램 크래시용 자동 디버깅을 설정해 두면 덤프를 모으지 않습니다 [2].
- WER 을 꺼 두었거나 사용자가 보고를 취소해도 로컬 덤프는 남을 수 있습니다 [2].
- 로컬 덤프는 Microsoft 로 보낸 덤프와 다를 수 있습니다 [2].
- WER 보고서 파일은 [윈도 오류 보고](../../../02-artifacts/execution/wer.md) 에서 다룹니다.
- 작업 관리자나 ProcDump 로 만든 덤프는 [메모리 덤프 확보](memory-acquisition.md) 에서 다룹니다. 이런 덤프의 기본 저장 위치는 이 글의 참고 문헌으로 확인하지 못했습니다.

## 구조 — 미니덤프 헤더

미니덤프 파일의 헤더 구조체는 MINIDUMP_HEADER 입니다 [3].
이 구조체는 헤더 파일 minidumpapiset.h 에 있고, DbgHelp.h 가 이 파일을 포함하며, 칸은 아래 순서로 놓입니다 [3].

| 순서 | 칸 | 형식 | 뜻 [3] |
|---|---|---|---|
| 1 | Signature | ULONG32 | MINIDUMP_SIGNATURE 로 채웁니다 |
| 2 | Version | ULONG32 | 아래 워드는 MINIDUMP_VERSION 입니다. 위 워드는 구현마다 다른 내부 값입니다 |
| 3 | NumberOfStreams | ULONG32 | 스트림 수입니다 |
| 4 | StreamDirectoryRva | RVA | 스트림 목록인 MINIDUMP_DIRECTORY 배열이 시작하는 RVA 입니다 |
| 5 | CheckSum | ULONG32 | 0 일 수 있습니다 |
| 6 | Reserved / TimeDateStamp | ULONG32 (공용체) | time_t 형식의 날짜·시각입니다 |
| 7 | Flags | ULONG64 | MINIDUMP_TYPE 값의 조합입니다 |

- 칸의 바이트 위치와 MINIDUMP_SIGNATURE 의 실제 값은 이 문서에 나오지 않아서 이 글에는 헥스 예시를 싣지 않습니다. 헤더 파일로 확인합니다.
- Flags 는 LocalDumps 의 CustomDumpFlags 와 같은 MINIDUMP_TYPE 조합입니다 [2][3]. 덤프에 무엇을 담았는지 가늠하는 단서가 됩니다.
- 커널 크래시 덤프의 파일 머리글 형식은 이 글의 참고 문헌으로 확인하지 못했습니다.

## 절차

1. SYSTEM 하이브의 CrashControl 값을 읽습니다. 어떤 종류의 덤프를 어디에 남기게 했는지 봅니다.
2. DumpFile 과 MinidumpDir 에 적힌 경로에서 파일을 찾습니다.
3. SOFTWARE 하이브에서 LocalDumps 키를 찾습니다. 키가 있으면 DumpFolder, 서비스 프로필 폴더, 프로그램별 키를 봅니다.
4. `%LOCALAPPDATA%` 는 사용자마다 다릅니다. 모든 사용자 프로필에서 찾습니다. 프로필 목록은 [사용자 프로필 목록](../../../02-artifacts/system-account/profilelist.md) 에 있습니다.
5. 이미지 전체에서 확장자가 `.dmp` 인 파일을 찾습니다. 작업 관리자나 ProcDump 로 만든 덤프는 설정과 다른 곳에 있을 수 있습니다.
6. 찾은 파일의 파일 시스템 시각을 적습니다. [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md) 을 봅니다.
7. 완전·커널 덤프는 Windows 디버거 (WinDbg) 로 엽니다 [1].
8. 작은 덤프에서는 중지 메시지, 드라이버 목록, 멈춘 프로세스·스레드를 봅니다. 드라이버가 의심스러우면 [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md) 에서 등록 기록을 찾습니다.
9. 크래시가 난 때를 이벤트 로그와 맞대 봅니다. [켜짐·꺼짐](../../../02-artifacts/event-logs/power-on-off-events.md) 과 [윈도 오류 보고](../../../02-artifacts/execution/wer.md) 를 봅니다.

## 시각 해석

- 작은 덤프는 파일 이름에 날짜가 들어갑니다 [1]. 이름 형식은 문서의 예로만 확인했습니다.
- 미니덤프 헤더의 TimeDateStamp 는 time_t 형식입니다 [3]. UTC 인지는 문서에 적혀 있지 않습니다. time_t 를 읽는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- 완전 덤프는 다음 크래시 때 이전 파일을 덮어씁니다 [1]. 커널 덤프도 덮어쓰기 설정이 켜져 있으면 덮어씁니다 [1]. 덮어썼다면 이 파일에는 마지막 크래시만 남습니다.
- 파일 시스템 시각과 헤더 시각이 크게 다르면 파일을 옮기거나 복사했는지 봅니다.

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| WinDbg (Windows 디버거) | 완전·커널 덤프를 엽니다 [1] |
| Volatility 3 (공개) | windows.crashinfo 플러그인이 있습니다 [4]. 무엇을 보여 주는지는 쓰는 버전의 도움말로 확인합니다 |
| 레지스트리 뷰어 | CrashControl 과 LocalDumps 값을 읽습니다 |

## 함정과 한계

- **읽은 설정이 크래시 때 설정과 다를 수 있습니다.** 바뀐 설정은 재부팅해야 적용됩니다 [1]. 설정을 바꾸고 재부팅하기 전에 크래시가 났다면 이전 설정을 따랐습니다.
- **설정이 켜져 있어도 덤프가 없을 수 있습니다.** 완전 덤프와 작은 덤프는 페이지 파일 조건이 맞아야 합니다 [1]. 페이지 파일은 [페이지 파일](pagefile-sys-swapfile-sys.md) 에 있습니다.
- **이전 크래시는 사라졌을 수 있습니다.** 완전·커널 덤프는 덮어씁니다 [1]. 사용자 모드 덤프는 DumpCount 를 넘으면 가장 오래된 것부터 바꿉니다 [2].
- **커널 덤프에는 사용자 프로그램 메모리가 없습니다** [1]. 커널 덤프에 사용자 프로그램의 흔적이 없다고 해서 그 프로그램을 쓰지 않았다고 볼 수 없습니다.
- **파일 크기로 덤프 종류를 가리지 않습니다.** 문서는 작은 메모리 덤프를 64KB 로 적습니다 [1]. 실제 파일 크기는 이 값과 다를 수 있습니다. CrashDumpEnabled 값과 파일 위치로 가립니다.
- **사용자 모드 덤프에는 비밀 정보가 들 수 있습니다.** 덤프 파일은 사건 자료로 따로 다룹니다. 보고서에 내용을 그대로 옮기지 않습니다.

## 결과를 어떻게 해석하나

증명하는 것은 아래와 같습니다.

- 커널 크래시 덤프가 있으면 그 PC 에서 버그 체크가 있었다고 볼 수 있습니다.
- 작은 덤프는 버그 체크 순간의 중지 메시지, 로드된 드라이버, 멈춘 프로세스·스레드를 보여 줍니다 [1].
- LocalDumps 폴더의 덤프는 그 프로그램이 죽었을 때 남았을 가능성이 큽니다. 다른 도구로 만든 뒤 옮겼을 수도 있습니다. 파일 시각과 실행 흔적을 함께 봅니다.

증명하지 못하는 것은 아래와 같습니다.

- 덤프가 있다는 것만으로 크래시 원인을 알 수는 없습니다. 원인은 디버거 분석으로 따로 밝힙니다.
- 덤프가 없다고 해서 크래시가 없었다는 뜻은 아닙니다. 설정을 꺼 두었거나, 페이지 파일 조건이 맞지 않았거나, 덮어썼거나, 누가 지웠을 수 있습니다.
- 덤프 파일만으로는 누가 만들었는지 알 수 없습니다. 작업 관리자나 ProcDump 를 실행한 흔적은 [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md) 에서 찾습니다.

보고서 문장 예입니다.

- 쓰지 않을 문장: "악성 드라이버 때문에 시스템이 멈췄습니다."
- 쓸 문장: "`%SystemRoot%\Minidump` 에 덤프 파일 ○○ 가 있습니다. 파일 이름의 날짜는 ○○ 입니다. 덤프의 로드된 드라이버 목록에 ○○ 가 있습니다. 이 기록은 이 버그 체크 순간 이 드라이버가 올라와 있었음을 보여 줍니다. 버그 체크의 원인은 디버거 분석 결과로 따로 적습니다."

## 함께 볼 페이지

- [메모리 덤프 확보](memory-acquisition.md) — 켜진 PC 에서 덤프를 만드는 방법입니다.
- [프로세스와 DLL 분석](process-analysis.md) — 덤프에서 프로세스 정보를 읽는 법입니다.
- [윈도 오류 보고](../../../02-artifacts/execution/wer.md) — WER 보고서 파일에 남는 크래시 기록입니다.
- [켜짐·꺼짐](../../../02-artifacts/event-logs/power-on-off-events.md) — 크래시로 꺼진 시점을 맞대 봅니다.

## 참고 문헌

1. Microsoft Learn, "Memory dump file options" (KB 254649, 2026-02-12) — https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/memory-dump-file-options
2. Microsoft Learn, "Collecting User-Mode Dumps" (2024-07-18) — https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps
3. Microsoft Learn, "MINIDUMP_HEADER structure (minidumpapiset.h)" (2018-12-05, 갱신 2024-02-22) — https://learn.microsoft.com/en-us/windows/win32/api/minidumpapiset/ns-minidumpapiset-minidump_header
4. Volatility 3 documentation, "volatility3.plugins.windows package" (latest) — https://volatility3.readthedocs.io/en/latest/volatility3.plugins.windows.html
