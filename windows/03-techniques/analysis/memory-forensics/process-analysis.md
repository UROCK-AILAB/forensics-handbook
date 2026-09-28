---
title: "프로세스와 DLL 분석"
parent: "메모리 분석"
grand_parent: "기법 · 분석"
nav_order: 3190
---

# 프로세스와 DLL 분석 (Process Analysis)

메모리 이미지에서 확보한 순간에 돌던 프로세스를 꺼낸 뒤 프로세스마다 명령줄·DLL·핸들·스레드를 봅니다.
이렇게 디스크 기록만으로는 답하기 어려운 "그 순간 무엇이 돌고 있었나" 에 답합니다.

## 언제 쓰나

- 메모리 이미지를 받은 뒤 가장 먼저 합니다. 네트워크 흔적과 코드 주입도 여기서 뽑은 프로세스 목록 위에서 봅니다.
- 의심 프로그램이 돌고 있었는지, 어떤 명령줄로 떴는지 볼 때 씁니다.
- 그 프로세스가 어떤 파일·레지스트리 키를 열고 있었는지 볼 때 씁니다.
- 이미지를 뜨는 방법은 [메모리 덤프 확보](memory-acquisition.md) 에 있습니다.

## 플러그인 이름 읽는 법

이 페이지는 공개 도구 Volatility 3 의 플러그인 이름으로 설명합니다. 다른 도구를 써도 묻는 질문은 같습니다.
메모리 분석 묶음의 다른 페이지도 이 절의 주의를 따릅니다.

- 같은 플러그인이 두 이름으로 함께 있기도 합니다. 예를 들어 windows.psxview 와 windows.malware.psxview 가 둘 다 있습니다 [1].
- windows.hashdump 와 windows.registry.hashdump 처럼 windows 아래와 windows.registry 아래에 함께 있는 이름도 있습니다 [1].
- 어느 쪽이 지금 이름인지는 버전마다 다를 수 있으니, 쓰는 버전의 플러그인 목록으로 이름을 확인합니다.
- 이 묶음에서 "알려진 동작" 으로 적은 설명은 널리 알려진 설명입니다. 쓰는 버전의 도움말이나 소스 코드로 확인하고 씁니다.

## 질문별 플러그인

| 묻는 것 | 플러그인 [1] |
|---|---|
| 이미지의 시스템 정보 | windows.info |
| 어떤 프로세스가 있었나 | windows.pslist, windows.psscan, windows.pstree |
| 여러 프로세스 목록 맞대 보기 | windows.psxview — [코드 주입·숨긴 프로세스 탐지](injection-rootkit.md) 에서 다룹니다 |
| 어떤 명령줄·환경 변수로 떴나 | windows.cmdline, windows.envars |
| 어떤 DLL·모듈을 올렸나 | windows.dlllist, windows.ldrmodules, windows.unloadedmodules, windows.verinfo, windows.iat |
| 무엇을 열고 있었나, 어떤 권한·SID 로 돌았나 | windows.handles, windows.privileges, windows.getsids, windows.getservicesids |
| 스레드 | windows.threads, windows.thrdscan, windows.suspended_threads |
| 프로세스의 메모리 영역 | windows.vadinfo, windows.vadwalk, windows.memmap, windows.virtmap |
| 서비스 | windows.svcscan |
| 세션·데스크톱 | windows.sessions, windows.windowstations, windows.desktops, windows.deskscan |
| 콘솔 창에서 친 명령 | windows.cmdscan, windows.consoles |
| 뮤텍스 | windows.mutantscan |
| 파일 객체 찾기·파일 꺼내기 | windows.filescan, windows.dumpfiles |

## 절차

1. windows.info 로 이미지의 시스템 정보를 봅니다. 디스크에서 확인한 OS 버전과 맞는지 봅니다. [시스템 기본 정보](../../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 를 봅니다.
2. windows.pslist 와 windows.pstree 로 프로세스 목록과 부모·자식 관계를 봅니다.
3. windows.psscan 결과를 pslist 결과 옆에 둡니다. 한쪽에만 있는 프로세스가 있으면 [코드 주입·숨긴 프로세스 탐지](injection-rootkit.md) 로 넘어갑니다.
4. 눈에 띄는 프로세스마다 명령줄과 환경 변수를 봅니다(windows.cmdline, windows.envars).
5. 그 프로세스가 올린 DLL 을 봅니다(windows.dlllist). 경로가 이상한 DLL 은 windows.verinfo 로 버전 정보를 봅니다. 서명과 버전 정보를 읽는 법은 [실행 파일 메타데이터](../../../02-artifacts/embedded-metadata/pe-header-version-info-digital-signature.md) 에 있습니다.
6. 핸들 목록으로 그 프로세스가 열고 있던 객체를 봅니다(windows.handles). 뮤텍스는 windows.mutantscan 으로 따로 봅니다.
7. 권한과 SID 로 어느 계정의 프로세스인지 좁힙니다(windows.privileges, windows.getsids). SID 를 읽는 법은 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에 있습니다.
8. 서비스로 뜬 프로세스는 windows.svcscan 결과와 잇습니다. 디스크의 서비스 등록은 [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md) 에서 봅니다.
9. 콘솔 창에서 친 명령이 메모리에 남았는지 봅니다(windows.cmdscan, windows.consoles).
10. 더 봐야 할 파일은 windows.dumpfiles 로 꺼냅니다. 꺼낸 파일은 해시를 계산해 [해시셋 대조와 유사 해시](../hash-set-fuzzy-hash.md) 나 [의심 실행 파일 선별](../code-signing-yara.md) 로 넘깁니다.
11. 메모리에서 본 것을 디스크 기록과 맞대 봅니다(아래 "결과를 어떻게 해석하나").

## 알려진 동작

아래는 널리 알려진 설명입니다. 쓰는 버전의 도움말이나 소스 코드로 확인하고 씁니다.

- windows.pslist 는 커널이 관리하는 활성 프로세스 목록을 따라간다고 알려져 있습니다.
- windows.psscan 은 메모리 전체에서 프로세스 객체(EPROCESS)의 흔적을 긁어 찾기 때문에, 이미 끝난 프로세스나 목록에서 떼어 낸 프로세스도 나올 수 있다고 알려져 있습니다.
- windows.dlllist 는 프로세스 환경 블록 (PEB, Process Environment Block) 의 로더 목록을 읽는다고 알려져 있습니다.
- windows.ldrmodules 는 이 로더 목록과, 메모리 영역에 매핑된 파일을 비교한다고 알려져 있습니다. 비교 결과를 읽는 법은 [코드 주입·숨긴 프로세스 탐지](injection-rootkit.md) 에 있습니다.

## 함정과 한계

- **이름만 보고 판단하지 않습니다.** 주입한 코드는 정상 프로세스 이름 아래에서 돌 수 있습니다. [코드 주입·숨긴 프로세스 탐지](injection-rootkit.md) 를 봅니다.
- **정상 부모·자식 관계는 비교해서 판단합니다.** 같은 Windows 버전의 깨끗한 PC 에서 뜬 이미지를 기준으로 삼습니다.
- **psscan 에만 있는 프로세스를 바로 숨긴 프로세스로 보지 않습니다.** 이미 끝난 프로세스일 수 있습니다.
- **페이지 파일로 나간 내용은 읽지 못합니다.** 프로세스 메모리의 일부가 페이지 파일로 나가 있으면 물리 메모리 이미지에서 그 부분을 읽을 수 없습니다. 명령줄이나 DLL 목록이 비어 나오면 이 경우일 수 있습니다. [페이지 파일](pagefile-sys-swapfile-sys.md) 을 봅니다.
- **시각 기준을 확인합니다.** 도구가 프로세스 시작·종료 시각을 UTC 로 보여 주는지 도구 설정과 출력으로 확인하고 보고서에 기준을 적습니다. 시각 형식은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- **확보 도구 자신이 목록에 있습니다.** 확보 기록의 시각과 도구 이름으로 가려냅니다. [메모리 덤프 확보](memory-acquisition.md) 를 봅니다.
- **크래시 덤프에는 프로세스 정보가 일부만 있습니다.** 어떤 정보가 남는지는 [크래시 덤프](memory-dmp-minidump.md) 에 있습니다.

## 결과를 어떻게 해석하나

프로세스 목록은 확보한 순간 메모리에 있던 것만 보여 주므로, 그 전에 끝난 실행은 디스크 기록으로 찾습니다. [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md) 를 봅니다.
메모리에서 본 것은 아래 디스크 기록과 맞대 봅니다.

| 메모리에서 본 것 | 맞대 볼 페이지 |
|---|---|
| 프로세스 이름·명령줄·부모 프로세스 | [프로세스 생성](../../../02-artifacts/event-logs/4688.md), [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md) |
| 실행 파일 | [프리페치](../../../02-artifacts/execution/prefetch/index.md), [AmCache](../../../02-artifacts/execution/amcache-hve/index.md) |
| 서비스로 뜬 프로세스 | [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md), [서비스 설치](../../../02-artifacts/event-logs/7045-4697.md) |
| 콘솔 명령 | [PowerShell 명령 기록](../../../02-artifacts/execution/consolehost-history-txt.md), [PowerShell 실행 기록](../../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md) |
| DLL·실행 파일의 서명과 버전 | [실행 파일 메타데이터](../../../02-artifacts/embedded-metadata/pe-header-version-info-digital-signature.md) |
| 프로세스의 SID | [사용자 계정](../../../02-artifacts/system-account/sam.md), [사용자 프로필 목록](../../../02-artifacts/system-account/profilelist.md) |

보고서 문장 예입니다.

- 쓰지 않을 문장: "피조사자가 ○○.exe 를 실행했습니다."
- 쓸 문장: "○○(UTC) 에 확보한 메모리 이미지의 프로세스 목록에 PID ○○ 인 ○○.exe 가 있습니다. 부모 프로세스는 PID ○○ 인 ○○.exe 입니다. 명령줄은 ○○ 입니다. 이 프로세스의 SID 는 계정 ○○ 을 가리킵니다. 그 계정을 누가 조작했는지는 이 기록만으로 정할 수 없습니다."

계정과 사람을 잇는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 에 있습니다.

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| Volatility 3 (공개) | 위 표의 플러그인으로 프로세스·DLL·핸들·스레드를 봅니다 [1] |
| MemProcFS (공개) | 메모리 이미지를 파일 시스템처럼 열어 폴더와 파일로 보여 줍니다. 포렌식 모드를 켜면 아래 결과를 한꺼번에 만듭니다 [2] |

도구 하나의 결과만 믿지 않습니다. 중요한 결과는 다른 도구나 다른 플러그인으로 한 번 더 봅니다. [도구 결과 교차 검증](../../reporting/tool-validation.md) 을 봅니다.

### MemProcFS 포렌식 모드

MemProcFS 의 포렌식 모드 (forensic mode) 는 메모리 이미지를 처음부터 끝까지 한 번 읽으면서 여러 분석을 함께 돌리고, 결과를 SQLite DB 에 저장한 뒤 `forensic` 폴더 아래에 시간순 기록 (timeline)·CSV·NTFS 복원 결과를 만듭니다 [2].
기본값은 꺼져 있고 1~4 중 한 값으로 켜는데, 1 은 DB 를 메모리에만 두고 2 는 종료할 때 지우며 3·4 는 종료 뒤에도 남깁니다 [2].
나중에 같은 결과를 다시 보여 줘야 하는 사건이면 DB 를 남기는 값을 고르고, 남은 DB 파일도 해시를 계산해 확보 기록에 적습니다.

| 결과 폴더 | 담는 것 | 해석할 때 주의 |
|---|---|---|
| `timeline` | 이벤트 로그·네트워크 연결·NTFS MFT·프로세스·레지스트리·스레드 기록을 시각순으로 합친 텍스트 파일입니다. 모두 합친 파일은 timeline_all.txt 입니다. 필드는 DATE, TYPE, ACTION, PID, NUM, HEX, DESC 이고, ACTION 은 CRE(생성·시작), MOD(수정), RD(읽기), DEL(삭제·종료) 중 하나입니다 [3] | NUM·HEX 필드의 뜻이 TYPE 마다 다릅니다. PROC 줄의 NUM 은 부모 PID 이고, NTFS 줄의 NUM 은 파일 크기, HEX 는 MFT 레코드의 물리 주소입니다 [3] |
| `csv` | 프로세스·핸들·모듈·드라이버·서비스·예약 작업·네트워크·DNS 캐시·이벤트 로그 표와, timeline_all.csv 를 비롯한 시간순 기록 CSV 입니다 [5] | 시각은 UTC 입니다 [5]. 현지 시각으로 바꿔 둔 다른 도구 결과와 합칠 때는 한쪽 기준으로 맞춥니다 |
| `ntfs` | 메모리에 남은 MFT 레코드로 되살린 파일 시스템과, 레코드마다 생성·수정 시각, 크기, 플래그, 경로를 적은 ntfs_files.txt 입니다 [4] | 가능한 만큼만 복원하므로 경로가 틀리거나 파일·폴더가 빠질 수 있습니다. 내용은 MFT 레코드 안에 들어 있는 상주 (resident) 데이터만 꺼낼 수 있고, 플래그 R 로 표시합니다 [4] |
| `findevil` | 코드 주입 같은 이상 징후를 프로세스·주소와 함께 적은 findevil.txt 입니다 [6] | 사용자 모드 악성코드만 찾고, 놓치는 종류와 오탐이 있습니다. 주로 64비트 Windows 10·11 에서 동작합니다 [6] |

NTFS 결과의 폴더 번호도 확인합니다.
0 번 폴더는 물리 메모리에서만 찾은 레코드이고, 1 번 이후는 레코드 수가 많은 파일 시스템 순서라서 1 번이 보통 시스템 드라이브이지만 늘 그렇지는 않습니다 [4].
부모 폴더를 알 수 없는 파일은 파일 시스템마다 `$_ORPHAN` 폴더에 모이고, 물리 주소가 0 으로 나온 항목은 MFT 레코드가 아니라 $I30 인덱스 항목에서 되살린 것일 수 있습니다 [4].
이 결과는 메모리에 있던 MFT 레코드만 담기 때문에, 파일이 디스크에 있었는지와 전체 시각 값은 디스크의 [MFT](../../../02-artifacts/filesystem/mft.md) 로 확인합니다.

레지스트리는 포렌식 모드와 따로 루트의 `registry` 폴더에 보이는데, 이것도 메모리 조각으로 되살린 것입니다 [7].
하이브 파일은 가능한 만큼만 복원하고 페이지 파일로 나가 읽지 못한 페이지는 0 으로 채우므로 일부가 깨져 있을 수 있습니다 [7].
키의 마지막 쓰기 시각은 그 키를 나타내는 폴더의 수정 시각으로 보이고, 부모를 모르는 키는 하이브마다 ORPHAN 키 아래에 모입니다 [7].
값이 비었거나 깨져 있으면 먼저 페이지 파일로 나간 부분인지 의심하고, 디스크 하이브와 비교합니다.

FindEvil 결과는 조사할 곳을 좁히는 목록으로만 씁니다.
일부 탐지 종류는 페이지 파일로 나갔거나 확보하는 동안 바뀐 메모리에서도 뜨고, SYSTEM 이 아닌 프로세스의 SeDebugPrivilege 를 찾는 탐지(PROC_DEBUG)는 이 권한이 있는 정상 프로그램에서도 뜹니다 [6].
뜬 항목은 [코드 주입·숨긴 프로세스 탐지](injection-rootkit.md) 의 방법으로 다시 확인합니다.

포렌식 모드는 확보한 이미지 파일에 씁니다.
실행 중인 PC 의 메모리를 직접 읽으면서 켜면 읽는 동안 메모리가 바뀌어 결과 품질이 떨어집니다 [2].
시간순 기록은 [슈퍼 타임라인](../timeline/super-timeline.md) 에 합쳐 디스크 기록과 함께 봅니다.

기능은 버전마다 늘어나므로 쓰는 버전의 릴리스 노트와 위키로 확인하고, 보고서에 도구 버전을 적습니다 [8].

| 버전 | 공개일(UTC) | 바뀐 내용 [8] |
|---|---|---|
| 5.10 | 2024-07-11 | Windows 11 24H2 지원, 최대 절전 파일 지원, 프리페치 해석, 이벤트 로그 파일을 보여 주는 모듈 |
| 5.15 | 2025-06-22 | FindEvil 에 높은 엔트로피 (High Entropy) 영역 탐지 추가, DNS 캐시 해석 |
| 5.16 | 2025-10-05 | Windows 11 25H2 지원 |
| 5.17 | 2026-02-22 | Windows 11 26H1 지원, 레지스트리 해석 개선 |
| 5.18 | 2026-07-25 | Amcache 포렌식 모듈(Windows 10 이상), Windows Terminal 해석 모듈(Windows 11 이상) |

Amcache 항목의 뜻은 [AmCache](../../../02-artifacts/execution/amcache-hve/index.md) 를 봅니다.

## 참고 문헌

1. Volatility 3 documentation, "volatility3.plugins.windows package" (latest) — https://volatility3.readthedocs.io/en/latest/volatility3.plugins.windows.html
2. Ulf Frisk, MemProcFS Wiki "FS_Forensic" (GitHub) — https://github.com/ufrisk/MemProcFS/wiki/FS_Forensic
3. Ulf Frisk, MemProcFS Wiki "FS_Forensic_Timeline" (GitHub) — https://github.com/ufrisk/MemProcFS/wiki/FS_Forensic_Timeline
4. Ulf Frisk, MemProcFS Wiki "FS_Forensic_Ntfs" (GitHub) — https://github.com/ufrisk/MemProcFS/wiki/FS_Forensic_Ntfs
5. Ulf Frisk, MemProcFS Wiki "FS_Forensic_CSV" (GitHub) — https://github.com/ufrisk/MemProcFS/wiki/FS_Forensic_CSV
6. Ulf Frisk, MemProcFS Wiki "FS_FindEvil" (GitHub) — https://github.com/ufrisk/MemProcFS/wiki/FS_FindEvil
7. Ulf Frisk, MemProcFS Wiki "FS_Registry" (GitHub) — https://github.com/ufrisk/MemProcFS/wiki/FS_Registry
8. Ulf Frisk, MemProcFS Releases (GitHub, v5.10~v5.18) — https://github.com/ufrisk/MemProcFS/releases
