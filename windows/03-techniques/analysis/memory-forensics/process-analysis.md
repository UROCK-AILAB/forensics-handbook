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

도구 하나의 결과만 믿지 않습니다. 중요한 결과는 다른 도구나 다른 플러그인으로 한 번 더 봅니다. [도구 결과 교차 검증](../../reporting/tool-validation.md) 을 봅니다.

## 참고 문헌

1. Volatility 3 documentation, "volatility3.plugins.windows package" (latest) — https://volatility3.readthedocs.io/en/latest/volatility3.plugins.windows.html
