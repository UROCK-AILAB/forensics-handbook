---
title: "메모리 속 문자열·자격증명·암호 키"
parent: "메모리 분석"
grand_parent: "기법 · 분석"
nav_order: 3220
---

# 메모리 속 문자열·자격증명·암호 키 (Strings·Credentials·Keys)

> 상위 허브: [메모리 분석 (Memory Forensics)](index.md)

## 한 줄 요약

메모리 이미지에서 문자열, 계정 해시·비밀, 암호 키를 찾습니다. 이런 값은 디스크에 남지 않고 메모리에만 잠시 있다가 사라지기도 하지만, Credential Guard 가 켜진 PC 에서는 lsass 메모리에서 꺼낼 수 있는 값이 줄어듭니다.

## 언제 쓰나

- 계정 탈취가 의심될 때, 어떤 자격증명이 메모리에 드러나 있었는지 볼 때 씁니다. [계정 탈취와 측면 이동](../../../04-scenarios/incident/credential-theft-lateral-movement/index.md) 을 봅니다.
- 프로세스 메모리에 남은 주소·명령·문서 조각을 찾을 때 씁니다.
- 암호화된 볼륨이나 파일을 풀 실마리를 찾을 때 씁니다. [암호화 증거 다루기](../encrypted-evidence/index.md) 를 봅니다.

## 문자열 찾기

Volatility 3 에는 windows.strings 와 windows.vadyarascan 이 있습니다 [1].
windows.vadyarascan 은 YARA 규칙으로 검색하는 플러그인입니다. 규칙을 쓰는 법은 [의심 실행 파일 선별](../code-signing-yara.md) 에 있습니다.

- Windows 는 문자열을 UTF-16LE 로 담는 경우가 많아서 검색할 때 ASCII 와 UTF-16LE 를 둘 다 찾습니다. 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에 있습니다.
- 메모리 이미지 전체를 그냥 검색하면 문자열이 어느 프로세스 것인지 모르므로, 찾은 위치를 프로세스에 잇는 과정이 따로 필요합니다.
- windows.strings 플러그인은 strings 명령의 출력을 읽어, 문자열마다 어느 프로세스의 것인지 알려 줍니다 [4]. 그러니 먼저 이미지에서 문자열과 그 위치를 뽑아 둡니다. 입력 형식과 옵션 이름은 쓰는 버전의 도움말로 확인합니다.
- 가상 주소로 이어진 내용도 물리 메모리에서는 떨어져 있을 수 있어서, 이미지 전체를 그냥 검색하면 긴 문자열이 끊겨 나올 수 있습니다.
- 키워드 목록을 만들고 검색 결과를 정리하는 방법은 [파일 내용 검색](../content-search/index.md) 과 같습니다.

## 자격증명과 Credential Guard

예전 Windows 는 비밀 정보를 LSA 프로세스 lsass.exe 의 메모리에 두었습니다. Credential Guard 를 켜면 lsass 는 격리된 LSA 프로세스 LSAIso.exe 와 RPC 로 통신하고, 이때 비밀은 LSAIso.exe 가 가상화 기반 보안 (VBS, Virtualization-based Security) 으로 보호해 둡니다. 나머지 운영체제는 이 자료에 접근할 수 없습니다. NTLM 해시와 Kerberos TGT 는 보통 디스크에 남지 않으며, 재부팅하면 사라지고 로그온할 때 새로 만듭니다 [2].

Credential Guard 가 켜졌을 때 무엇을 보호하는지는 아래와 같습니다 [2].

| 대상 | Credential Guard 의 보호 |
|---|---|
| NTLM 해시, Kerberos TGT | 보호합니다 |
| Kerberos 서비스 티켓 | 보호하지 않습니다 |
| 로컬 계정, Microsoft 계정 | 보호하지 않습니다 |
| Windows 기능 밖에서 자격증명을 다루는 소프트웨어 | 보호하지 않습니다 |
| Microsoft 가 아닌 보안 패키지 | 보호하지 않습니다 |
| NTLM 인증에서 사용자가 창에 직접 입력한 자격증명 | 보호하지 않습니다. 이 값은 LSASS 메모리에서 읽힐 수 있습니다 |
| 캐시된 도메인 로그온 정보 | 레지스트리에 저장합니다. Credential Guard 가 말하는 "자격증명" 에 들지 않습니다 |

메모리 분석에서 이 표가 뜻하는 것은 아래와 같습니다.

- Credential Guard 가 켜진 PC 의 메모리 이미지에서는 lsass 로부터 NTLM 해시와 TGT 를 꺼내기 어려울 것으로 보입니다.
- 보호하지 않는 항목은 lsass 메모리에 남아 있을 수 있습니다.
- Credential Guard 가 켜져 있으면 lsass 가 LSAIso.exe 와 통신합니다 [2]. 그래서 첫 확인은 프로세스 목록에서 LSAIso.exe 를 찾는 일입니다. 목록을 만드는 법은 [프로세스와 DLL 분석](process-analysis.md) 에 있습니다.
- Credential Guard 가 켜져 있었는지는 이미지마다 확인합니다.

## 레지스트리와 해시

Volatility 3 에는 메모리에 올라온 레지스트리를 보는 플러그인과 해시·비밀을 다루는 플러그인이 있습니다 [1].

왼쪽 칸의 묶음은 플러그인 이름을 보고 나눈 것입니다.

| 묻는 것 | 플러그인 [1] |
|---|---|
| 메모리에 있는 하이브 목록 | windows.registry.hivelist, windows.registry.hivescan |
| 키와 값 읽기 | windows.registry.printkey |
| 계정 해시·LSA 비밀·캐시된 로그온 정보 | windows.hashdump, windows.lsadump, windows.cachedump |
| 커널 풀 할당 | windows.bigpools, windows.poolscanner |

- hashdump·lsadump·cachedump 는 windows.registry 아래에도 같은 이름이 있습니다 [1]. 이름을 읽는 법은 [프로세스와 DLL 분석](process-analysis.md) 의 "플러그인 이름 읽는 법" 에 있습니다.
- 세 플러그인이 정확히 어느 하이브에서 무엇을 읽는지는 쓰는 버전의 도움말로 확인합니다.
- 디스크에서 같은 정보를 읽는 법은 [레지스트리 속 비밀번호 정보](../../../02-artifacts/credentials/sam-security/index.md) 에 있습니다. 하이브 구조는 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.

## 암호 키

- Volatility 3 에는 windows.truecrypt 플러그인이 있습니다 [1].
- 볼륨이 열려 있는 동안에는 디스크 암호화 키가 메모리에 있어 꺼낼 수 있다는 설명이 널리 알려져 있습니다.
- 암호화 볼륨을 다루는 순서는 [암호화 증거 다루기](../encrypted-evidence/index.md) 에 있습니다.
- DPAPI 로 보호한 자료를 디스크에서 푸는 방법은 [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) 에 있습니다.

## 디스크에 남은 프로세스 덤프

- 작업 관리자나 ProcDump 로 만든 프로세스 덤프는 파일로 남고 [3], 로컬 덤프 설정을 켜 둔 PC 에서는 사용자 모드 프로그램이 죽을 때도 덤프가 남습니다 [3]. 설정과 저장 위치는 [크래시 덤프](memory-dmp-minidump.md) 와 [윈도 오류 보고](../../../02-artifacts/execution/wer.md) 에 있습니다.
- 디스크에서 lsass 프로세스의 덤프 파일을 찾았다면 누가 언제 만들었는지 확인합니다. 파일 시각은 [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md) 에서, 만든 프로그램의 실행은 [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md) 에서 봅니다.

## 절차

1. 이미지를 뜬 Windows 버전과 확보 방법을 확인합니다. [메모리 덤프 확보](memory-acquisition.md) 를 봅니다.
2. 프로세스 목록에서 lsass.exe 와 LSAIso.exe 를 찾습니다. Credential Guard 가 돌고 있었는지 가늠합니다.
3. 메모리에 있는 하이브 목록을 봅니다(windows.registry.hivelist, windows.registry.hivescan).
4. 해시·비밀 플러그인을 돌립니다(windows.hashdump, windows.lsadump, windows.cachedump).
5. 조사 질문에 맞춰 키워드와 YARA 규칙을 정합니다. 대상 프로세스를 정해 windows.vadyarascan 으로 검색합니다.
6. 이미지 전체에서 뽑은 문자열을 프로세스에 이어야 하면, strings 명령으로 뽑은 결과를 windows.strings 에 넣습니다 [4]. 입력 형식은 도움말로 확인합니다.
7. 암호화 볼륨이 있으면 windows.truecrypt 같은 관련 플러그인을 돌립니다. 플러그인이 무엇을 보여 주는지는 쓰는 버전의 도움말로 확인합니다.
8. 찾은 값을 디스크 기록과 맞대 봅니다. [자격 증명 관리자와 볼트](../../../02-artifacts/credentials/credential-manager-windows-vault.md), [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) 를 봅니다.
9. 꺼낸 해시·비밀번호·키는 사건 자료로 따로 보관합니다. 보고서 본문에는 필요한 만큼만 적습니다.

## 함정과 한계

- **Credential Guard 가 켜져 있으면 NTLM 해시와 TGT 가 lsass 메모리에 없을 수 있습니다.** 값이 안 나온다고 해서 도구가 틀린 것은 아닙니다.
- **재부팅하면 NTLM 해시와 TGT 는 사라집니다** [2]. 재부팅 뒤에 뜬 이미지에는 그 전 세션의 값이 없습니다.
- **캐시된 도메인 로그온 정보는 레지스트리에 있습니다** [2]. lsass 메모리만 보고 "자격증명이 없다" 고 쓰지 않습니다.
- **문자열은 조각입니다.** 문자열 하나만으로는 누가 입력했는지, 어디에 썼는지 알 수 없습니다.
- **인코딩을 하나만 찾으면 놓칩니다.** ASCII 와 UTF-16LE 를 둘 다 찾습니다.
- **페이지 파일로 나간 내용은 이미지에 없습니다.** [페이지 파일](pagefile-sys-swapfile-sys.md) 도 함께 검색합니다.
- **민감한 값을 다룹니다.** 꺼낸 비밀번호와 해시가 보고서나 작업 기록에 그대로 퍼지지 않게 합니다.

## 결과를 어떻게 해석하나

- 메모리에서 찾은 값은 확보한 순간 그 값이 메모리에 있었음을 보여 줍니다.
- 해시를 찾았다고 해서 공격자가 그 해시를 가져갔다는 뜻은 아닙니다. 빼 간 흔적은 따로 찾습니다.
- 비밀번호 문자열을 찾았다고 해서 그 비밀번호를 썼다는 뜻은 아닙니다. 로그온 기록과 맞대 봅니다.
- 값이 없다고 해서 없었다는 뜻은 아닙니다. 재부팅, Credential Guard, 페이지 파일 때문일 수 있습니다.

보고서 문장 예입니다.

- 쓰지 않을 문장: "피조사자가 메모장에 비밀번호를 입력했습니다."
- 쓸 문장: "○○(UTC) 에 확보한 메모리 이미지에서 ○○.exe(PID ○○) 의 메모리 영역에 문자열 ○○ 가 UTF-16LE 로 있습니다. 이 기록은 확보한 순간 이 문자열이 이 프로세스 메모리에 있었음을 보여 줍니다. 이 문자열을 누가 입력했는지, 어디에 썼는지는 이 기록만으로 정할 수 없습니다."

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| Volatility 3 (공개) | 문자열·레지스트리·해시·암호 키 플러그인 [1] |
| YARA (공개) | 키워드와 패턴을 규칙으로 검색합니다. windows.vadyarascan 과 함께 씁니다 [1] |

## 참고 문헌

1. Volatility 3 documentation, "volatility3.plugins.windows package" (latest) — https://volatility3.readthedocs.io/en/latest/volatility3.plugins.windows.html
2. Microsoft Learn, "How Credential Guard works" (2025-06-12) — https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/how-it-works
3. Microsoft Learn, "Collecting User-Mode Dumps" (2024-07-18) — https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps
4. Volatility 3 documentation, "volatility3.plugins.windows.strings module" (latest) — https://volatility3.readthedocs.io/en/latest/volatility3.plugins.windows.strings.html
