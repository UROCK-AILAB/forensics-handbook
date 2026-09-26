---
title: "코드 주입·숨긴 프로세스 탐지"
parent: "메모리 분석"
grand_parent: "기법 · 분석"
nav_order: 3210
---

# 코드 주입·숨긴 프로세스 탐지 (Injection·Rootkit)

> 상위 허브: [메모리 분석 (Memory Forensics)](index.md)

## 한 줄 요약

다른 프로세스 안에 몰래 넣은 코드와, 목록에서 감춘 프로세스·모듈·드라이버를 메모리 이미지에서 찾습니다.
방법은 같은 대상을 서로 다른 길로 센 목록을 맞대 보는 것이며, 찾은 결과는 결론이 아니라 더 들여다볼 후보 목록입니다.

## 언제 쓰나

- 프로세스 목록에는 정상 프로그램만 보이는데 악성 활동의 흔적이 있을 때 씁니다.
- [메모리 속 네트워크 흔적](network-artifacts.md) 에서 정상 프로세스가 수상한 곳과 연결되어 있을 때 씁니다.
- [프로세스와 DLL 분석](process-analysis.md) 에서 목록끼리 어긋나는 프로세스를 찾았을 때 씁니다.

## 코드 주입이란

이 기법은 MITRE ATT&CK 의 T1055 코드 주입 (Process Injection) 입니다 [1].

전술은 Stealth 와 Privilege Escalation 이고, 플랫폼은 Linux·Windows·macOS 입니다 [1].
주입한 코드는 정상 프로세스 이름 아래에서 돌기 때문에 보안 제품의 탐지를 피할 수 있습니다 [1].

하위 기법은 아래와 같습니다 [1].

| ID | 이름 |
|---|---|
| T1055.001 | Dynamic-link Library Injection |
| T1055.002 | Portable Executable Injection |
| T1055.003 | Thread Execution Hijacking |
| T1055.004 | Asynchronous Procedure Call |
| T1055.005 | Thread Local Storage |
| T1055.008 | Ptrace System Calls |
| T1055.009 | Proc Memory |
| T1055.011 | Extra Window Memory Injection |
| T1055.012 | Process Hollowing |
| T1055.013 | Process Doppelgänging |
| T1055.014 | VDSO Hijacking |
| T1055.015 | ListPlanting |

.009 (Proc Memory) 의 플랫폼은 Linux 뿐입니다 [3]. .008·.014 도 이름으로 짐작하면 Linux 쪽 기법입니다.

탐지할 때는 아래를 봅니다 [1].

- 메모리를 다루는 API 호출: VirtualAllocEx, WriteProcessMemory
- 의심스러운 스레드 생성: CreateRemoteThread
- 다른 프로세스 안에서 벌어지는 이상한 DLL 로드

메모리 이미지로 보는 것은 이 호출 자체보다 호출이 남긴 결과, 곧 다른 프로세스에 새로 잡힌 메모리 영역, 새 스레드, 새로 올라온 DLL 입니다.
호출 순간의 기록이 필요하면 실시간 감시 기록인 [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md) 를 봅니다.

## 플러그인

Volatility 3 의 Windows 플러그인 가운데 아래를 씁니다 [2].
왼쪽 열의 묶음은 플러그인 이름으로 나눈 것입니다.
같은 플러그인이 windows.malfind 와 windows.malware.malfind 처럼 두 이름으로 나오기도 합니다. 이 점은 [프로세스와 DLL 분석](process-analysis.md) 의 "플러그인 이름 읽는 법" 에 있습니다.

| 찾는 것 | 플러그인 [2] |
|---|---|
| 주입한 코드 | windows.malfind, windows.hollowprocesses, windows.processghosting, windows.malware.pebmasquerade |
| 숨긴 프로세스 | windows.psxview, windows.pslist 와 windows.psscan 비교 |
| 숨긴 모듈 | windows.ldrmodules, windows.modules 와 windows.modscan, windows.unloadedmodules |
| 수상한 스레드 | windows.malware.suspicious_threads, windows.orphan_kernel_threads |
| 시스템 호출 우회 | windows.direct_system_calls, windows.indirect_system_calls, windows.malware.unhooked_system_calls |
| 커널 후킹·드라이버 | windows.ssdt, windows.callbacks, windows.driverirp, windows.driverscan, windows.drivermodule, windows.devicetree, windows.timers |
| 기타 | windows.etwpatch, windows.malware.skeleton_key_check, windows.malware.svcdiff, windows.debugregisters |

## 알려진 동작

아래는 널리 알려진 설명입니다. 판마다 다를 수 있으므로 쓰는 버전의 도움말이나 소스 코드로 확인하고 씁니다.

- windows.malfind 는 실행할 수 있고 쓸 수 있으면서 파일에 매핑되지 않은 메모리 영역을 찾는다고 알려져 있습니다. 그 영역 앞부분에 실행 파일 머리(MZ)나 코드가 있는지 보여 준다고 알려져 있습니다.
- 루트킷 (Rootkit) 은 커널 구조를 고쳐 자신을 감추는 악성코드를 흔히 이르는 말입니다.
- 루트킷이 프로세스 객체(EPROCESS)를 활성 프로세스 목록에서 떼어 내면 pslist 에는 없고 psscan 에는 보인다고 알려져 있습니다. 이 수법을 DKOM (Direct Kernel Object Manipulation) 이라고 부릅니다.
- 프로세스 비우기 (Process Hollowing) 는 정상 실행 파일로 프로세스를 만든 뒤 메모리 내용을 바꿔치기한다고 알려져 있고, 그래서 디스크의 실행 파일과 메모리에 올라온 내용이 다릅니다.
- windows.ldrmodules 는 프로세스의 로더 목록과, 메모리 영역에 매핑된 파일을 비교한다고 알려져 있습니다. 매핑은 되어 있는데 로더 목록에 없는 DLL 은 감춘 DLL 후보가 됩니다.

## 절차

1. 프로세스 목록을 맞대 봅니다. windows.pslist 와 windows.psscan 결과를 비교하고, windows.psxview 로 여러 목록을 한 번에 봅니다.
2. 한쪽 목록에만 있는 프로세스는 이미 끝난 프로세스일 수 있습니다. 끝난 프로세스가 아니라고 판별한 뒤에 숨긴 프로세스 후보로 둡니다.
3. windows.malfind 로 주입 후보 영역을 찾습니다. 결과가 많으면 다음 단계에서 걸러 냅니다.
4. 후보 영역을 파일로 꺼냅니다. 해시를 계산하고 YARA 규칙으로 검사합니다. [의심 실행 파일 선별](../code-signing-yara.md) 과 [해시셋 대조와 유사 해시](../hash-set-fuzzy-hash.md) 를 봅니다.
5. 비우기·위장을 찾는 플러그인을 돌립니다(windows.hollowprocesses, windows.processghosting, windows.malware.pebmasquerade).
6. 모듈 목록을 맞대 봅니다. 사용자 모드 DLL 은 windows.ldrmodules 로, 커널 모듈은 windows.modules 와 windows.modscan 을 나란히 놓고 봅니다.
7. 스레드와 시스템 호출 쪽을 봅니다(windows.malware.suspicious_threads, windows.orphan_kernel_threads, 시스템 호출 우회 플러그인).
8. 커널 후킹과 드라이버를 봅니다(windows.ssdt, windows.callbacks, windows.driverirp, windows.driverscan 등). 메모리에 있는 드라이버를 디스크의 서비스·드라이버 등록과 비교합니다. [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md) 를 봅니다.
9. 찾은 후보를 디스크 기록과 잇습니다. 어디서 들어왔는지는 [악성코드는 어디서 들어왔나](../../../04-scenarios/incident/initial-access.md) 에서, 어떻게 다시 뜨는지는 [악성코드 지속성(자동실행) 찾기](../../../04-scenarios/incident/persistence.md) 에서 봅니다.
10. 보안 제품의 탐지 기록과 맞대 봅니다. [Windows Defender 탐지](../../../02-artifacts/event-logs/1116-1117.md) 와 [디펜더 검사 로그·격리 파일](../../../02-artifacts/execution/mplog-detectionhistory-quarantine.md) 을 봅니다.

## 함정과 한계

- **malfind 결과에는 정상 영역이 섞일 수 있습니다.** .NET 이나 브라우저처럼 실행 중에 코드를 만드는 JIT 컴파일러가 이런 영역을 만든다고 알려져 있습니다. 결과 하나하나를 내용으로 확인합니다.
- **정상 프로그램도 비슷한 흔적을 남길 수 있다고 알려져 있습니다.** 보안 제품처럼 다른 프로세스나 커널에 손대는 프로그램이 그렇습니다. 같은 제품을 설치한 깨끗한 PC 의 이미지와 비교해 봅니다.
- **psscan 에만 있다고 숨긴 프로세스는 아닙니다.** 이미 끝난 프로세스일 수 있습니다.
- **페이지 파일로 나간 영역은 보이지 않습니다.** 주입 영역의 일부가 페이지 파일에 있으면 물리 메모리 이미지에서 읽을 수 없습니다. [페이지 파일](pagefile-sys-swapfile-sys.md) 을 봅니다.
- **플러그인 이름과 결과 형식은 버전마다 다릅니다.** 보고서에는 쓴 도구의 버전과 플러그인 이름을 적습니다.
- **탐지 플러그인의 결과는 판정이 아닙니다.** 결과는 후보입니다. 중요한 결과는 다른 도구로 한 번 더 확인합니다. [도구 결과 교차 검증](../../reporting/tool-validation.md) 을 봅니다.

## 결과를 어떻게 해석하나

주입 흔적은 확보한 순간 그 프로세스 안에 파일과 이어지지 않은 실행 코드가 있었음을 보여 주지만, 누가 언제 어떤 경로로 코드를 넣었는지는 알 수 없으므로 디스크의 실행 기록과 이벤트 로그로 채웁니다.
숨긴 프로세스 후보는 두 목록이 어긋난다는 사실까지만 보여 줍니다. 루트킷이라고 쓰려면 목록에서 떼어 낸 흔적, 수상한 드라이버처럼 다른 근거가 함께 있어야 합니다.
꺼낸 코드의 해시가 알려진 악성코드와 같으면 근거가 단단해지지만, 같지 않다고 해서 정상이라는 뜻은 아닙니다.

보고서 문장 예입니다.

- 쓰지 않을 문장: "공격자가 explorer.exe 에 악성코드를 주입했습니다."
- 쓸 문장: "○○(UTC) 에 확보한 메모리 이미지에서 ○○.exe(PID ○○) 안에 실행할 수 있고 파일에 매핑되지 않은 메모리 영역이 있습니다. 이 영역은 MZ 로 시작합니다. 이 영역을 꺼낸 파일의 SHA-256 은 ○○ 입니다. 이 기록은 확보한 순간 이 프로세스 안에 디스크 파일과 이어지지 않은 실행 코드가 있었음을 보여 줍니다. 누가 어떤 경로로 이 코드를 넣었는지는 이 기록만으로 정할 수 없습니다."

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| Volatility 3 (공개) | 위 표의 플러그인으로 주입 영역·숨긴 프로세스·커널 후킹 후보를 찾습니다 [2] |
| YARA (공개) | 꺼낸 메모리 영역을 규칙으로 검사합니다. Volatility 3 에는 windows.vadyarascan 도 있습니다 [2] |

## 함께 볼 페이지

- [프로세스와 DLL 분석](process-analysis.md) — 프로세스 목록과 DLL 목록을 만드는 법입니다.
- [메모리 속 네트워크 흔적](network-artifacts.md) — 주입당한 프로세스의 연결입니다.
- [메모리 속 문자열·자격증명·암호 키](strings-credentials-keys.md) — 꺼낸 영역의 문자열을 봅니다.
- [계정 탈취와 측면 이동](../../../04-scenarios/incident/credential-theft-lateral-movement/index.md) — 자격증명을 빼 가는 단계를 다룹니다.

## 참고 문헌

1. MITRE ATT&CK, "Process Injection, Technique T1055" (v2.0, last modified 2026-05-12) — https://attack.mitre.org/techniques/T1055/
2. Volatility 3 documentation, "volatility3.plugins.windows package" (latest) — https://volatility3.readthedocs.io/en/latest/volatility3.plugins.windows.html
3. MITRE ATT&CK, "Process Injection: Proc Memory, Sub-technique T1055.009" — https://attack.mitre.org/techniques/T1055/009/
