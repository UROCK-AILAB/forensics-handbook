# 자격 증명을 빼냈나 (Credential Dumping)

> 상위 허브: [계정 탈취와 측면 이동 (Credential Theft·Lateral Movement)](index.md)

이 페이지는 이미 들어온 PC 에서 비밀번호·해시·티켓 같은 자격 증명을 빼내려 한 흔적을 찾는 순서를 다룹니다. SAM·LSA 시크릿·NTDS 같은 저장 구조는 각 아티팩트 페이지에서 다룹니다. 이 페이지는 그 자료를 빼내려 할 때 로그·레지스트리·파일에 무엇이 남는지, 그 흔적을 어디까지 읽을 수 있는지를 다룹니다.

이 페이지에서 "(관찰)" 을 붙인 내용은 Windows 11 Home(빌드 26200) 분석 PC 한 대에서 직접 본 것입니다(확인 범위: Win11 Home 한 대). 다른 빌드에서는 다를 수 있습니다.

## 조사 질문

- 이 PC 에서 LSASS 메모리, SAM·SECURITY·SYSTEM 하이브, NTDS.dit 을 빼내려 한 흔적이 있습니까?
- LSA 보호(RunAsPPL)나 Credential Guard 가 켜져 있었습니까? 사고 전후로 꺼진 흔적이 있습니까?
- 빼낸 자격 증명이 어디에 쓰였는지 이어지는 흔적이 있습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | LSA 보호·Credential Guard 의 기본값이 버전마다 다릅니다. 아래 표에서 확인합니다. |
| 시간대 | 이벤트·레지스트리 시각을 같은 기준으로 맞춥니다([시간대 설정](../../../02-artifacts/system-account/time-zone.md)). |
| 감사·Sysmon 설정 | 프로세스 접근·명령줄·파일 생성 기록은 감사 정책이나 Sysmon 을 켜야 남습니다. [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) 을 봅니다. |
| 수집 범위 | 보안 로그, Sysmon 로그, CodeIntegrity 로그, SYSTEM·SOFTWARE 하이브, 사용자 프로필, 메모리 이미지가 있으면 메모리도 확보합니다. |

## 무엇을 노리나

MITRE ATT&CK 은 자격 증명 빼내기를 T1003(OS Credential Dumping) 으로 두고, 아래로 나눕니다[1].

| 하위 기법 | 노리는 것 | 저장 구조 페이지 |
|---|---|---|
| T1003.001 LSASS Memory | LSASS 프로세스 메모리 속 자격 증명 | 이 페이지 아래 |
| T1003.002 Security Account Manager | SAM 하이브의 로컬 계정 해시 | [레지스트리 속 비밀번호 정보](../../../02-artifacts/credentials/sam-security/index.md) |
| T1003.003 NTDS | 도메인 계정 데이터베이스 | [액티브 디렉터리 DB](../../../02-artifacts/credentials/ntds-dit.md) |
| T1003.004 LSA Secrets | LSA 시크릿 | [레지스트리 속 비밀번호 정보](../../../02-artifacts/credentials/sam-security/index.md) |
| T1003.005 Cached Domain Credentials | 캐시된 도메인 자격 증명 | [레지스트리 속 비밀번호 정보](../../../02-artifacts/credentials/sam-security/index.md) |
| T1003.006 DCSync | 도메인 컨트롤러에 복제를 요청해 얻는 해시 | [액티브 디렉터리 DB](../../../02-artifacts/credentials/ntds-dit.md) |

- T1003.007·T1003.008 은 리눅스 대상이라 이 위키 범위 밖입니다[1].
- 하이브에서 부트키로 해시를 풀고 LSA 시크릿·캐시 자격 증명으로 이어지는 구조는 [레지스트리 속 비밀번호 정보](../../../02-artifacts/credentials/sam-security/index.md) 에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | Sysmon 이벤트 10 | 어떤 프로세스가 lsass.exe 에 어떤 권한으로 접근했나 | [이미지 로드·프로세스 접근](../../../02-artifacts/event-logs/sysmon/7-8-10.md) |
| 2 | 프로세스 생성 (4688·Sysmon 1) | 덤프 도구의 명령줄, 하이브 복사 명령 | [프로세스 생성](../../../02-artifacts/event-logs/4688.md), [Sysmon 이벤트 1](../../../02-artifacts/event-logs/sysmon/1.md) |
| 3 | 파일 생성 (Sysmon 11·MFT·USN) | 덤프 파일이 생겼나 | [Sysmon 파일 이벤트](../../../02-artifacts/event-logs/sysmon/11-23-26.md), [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) |
| 4 | 실행 흔적 (프리페치 등) | 덤프 도구가 실행됐나 | [프리페치](../../../02-artifacts/execution/prefetch/index.md) |
| 5 | 레지스트리 (SSP·RunAsPPL·WDigest) | 자격 증명을 더 캐내려는 설정이 바뀌었나 | 이 페이지 아래 |
| 6 | CodeIntegrity·WinInit 이벤트 | LSA 보호가 켜져 있었나, 꺼졌나 | 이 페이지 아래 |
| 7 | Windows Defender 탐지 | 덤프 도구를 탐지했나 | [Windows Defender 탐지](../../../02-artifacts/event-logs/1116-1117.md) |

## LSASS 메모리 (T1003.001)

LSASS 프로세스 메모리에는 로그온한 계정의 자격 증명이 들어 있을 수 있습니다. 공격자는 이 메모리를 파일로 떠서 다른 PC 로 옮겨 읽습니다.

### 명령줄에서 찾는 것

MITRE 는 LSASS 메모리를 파일로 뜨는 예로 아래를 듭니다[1]. 조사에서는 이 문자열을 프로세스 생성 로그(4688·Sysmon 1)에서 찾습니다.

- 공개 덤프 도구를 쓰는 명령줄(예: `procdump -ma lsass.exe`)[1].
- 윈도에 들어 있는 comsvcs.dll 의 MiniDump 를 rundll32.exe 로 부르는 명령줄[1].
- 작업 관리자에서 LSASS 메모리를 디스크에 뜨는 방법[1].
- Silent Process Exit 로 WerFault.exe 를 이용해 뜨는 방법[1].

뜬 파일은 대상 PC 밖에서 공개 도구로 읽습니다[1]. 그래서 대상 PC 에는 읽는 과정이 남지 않을 수 있습니다.

- MITRE 예시의 파일 이름은 예시일 뿐입니다. 이름으로만 찾으면 놓칩니다. 파일 이름이 아니라 접근한 프로세스·권한·이어지는 파일 생성을 함께 봅니다.

### Sysmon 이벤트 10 으로 LSASS 접근 보기

- MITRE 의 탐지 절은 권한 없는 또는 이상한 프로세스가 lsass.exe 에 전체 권한(0x1F0FFF) 핸들을 연 뒤, 메모리 덤프·파일 생성·레지스트리 변경이 이어지는 것을 보라고 합니다[1].
- Sysmon 이벤트 10 은 어떤 프로세스가 다른 프로세스에 접근했는지와 그때의 GrantedAccess 값을 남깁니다. 칸과 설정은 [이미지 로드·프로세스 접근](../../../02-artifacts/event-logs/sysmon/7-8-10.md) 에 있습니다.
- 정상 동작에서도 lsass.exe 접근은 남습니다. 원격으로 wmic 명령을 실행하면 도착 PC 의 WmiPrvSE.exe 가 lsass.exe·services.exe·csrss.exe 에 접근하는 Sysmon 10 이 남았습니다[2].
- 원격 실행 도구가 남긴 Sysmon 10 의 GrantedAccess 예로는 0x1FFFFF, 0x1400, 0x1410, 0x101410 이 있었습니다[3].
- 그래서 "lsass 에 접근한 기록이 있다" 만으로 덤프라고 단정하지 않습니다. 접근한 프로세스 이름, 권한 값, 뒤이은 파일 생성을 함께 봅니다[1][2].

## LSA 보호(RunAsPPL)와 Credential Guard

LSASS 를 덤프하기 어렵게 만드는 두 가지 보호가 있습니다. 조사에서는 이 보호가 켜져 있었는지, 사고 전후로 꺼진 흔적이 있는지를 봅니다.

### RunAsPPL (LSA 추가 보호)

- Windows 8.1 이후의 LSA 추가 보호는 보호되지 않은 프로세스가 LSA 메모리를 읽거나 코드를 주입하지 못하게 합니다[4].
- 설정은 `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa` 의 RunAsPPL(DWORD)입니다[4].

| RunAsPPL 값 | 뜻 |
|---|---|
| 1 | UEFI 변수와 함께 켬 |
| 2 | UEFI 변수 없이 켬 (2 는 Windows 11 22H2 이후에만 적용) |
| 0 또는 값 삭제 | 끔 |

- 설정 변경은 재부팅 뒤에 적용됩니다[4].
- UEFI 잠금으로 켜면 설정이 펌웨어의 UEFI 변수에 저장돼 레지스트리로 끌 수 없습니다[4]. UEFI·Secure Boot 가 없으면 레지스트리 값에만 기대므로 원격으로 끌 수 있습니다[4].
- 새로 설치한 Windows 11 22H2 이후는 조건(새 설치, 기업 가입, HVCI 가능)을 만족하면 UEFI 잠금 없이 기본으로 켜집니다[4].
- LSASS 가 보호 모드로 시작했는지는 System 로그의 WinInit 이벤트 12 로 봅니다. 메시지에 "started as a protected process with level: 4" 가 나옵니다[4].
- 이 분석 PC(Windows 11 Home)에는 RunAsPPL = 2 가 있었고, System 로그에 WinInit 12 가 있었습니다(관찰). 기업에 가입하지 않은 Home 인데도 켜져 있었습니다(관찰). 그 까닭은 이 자료로는 확인하지 못했습니다.
- 조사 해석: RunAsPPL 이 사고 전후로 0 으로 바뀌었거나 값이 지워졌으면 보호를 끈 흔적일 수 있습니다. 재부팅 전에는 적용되지 않으므로 재부팅 기록과 함께 봅니다[4].

### 감사 모드와 CodeIntegrity 이벤트

- 감사 모드는 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\LSASS.exe` 의 AuditLevel = 8(DWORD)로 켭니다. Windows 11 22H2 이후는 기본으로 켜져 있습니다[4].
- 채널 `Microsoft-Windows-CodeIntegrity/Operational` 에 관련 이벤트가 남습니다[4].

| 이벤트 | 뜻 |
|---|---|
| 3065 | 감사 모드에서 조건에 안 맞는 공유 섹션 로드를 허용함 |
| 3066 | 감사 모드에서 조건에 안 맞는 서명 수준 로드를 허용함 |
| 3033 | 보호 모드에서 서명 수준이 맞지 않아 로드 실패 |
| 3063 | 보호 모드에서 공유 섹션이 맞지 않아 로드 실패 |

- Smart App Control 이 켜져 있으면 이 감사 이벤트가 생기지 않습니다[4]. 커널 디버거가 붙어 있어도 이 운영 이벤트가 생기지 않습니다[4].
- 이 분석 PC 의 CodeIntegrity 운영 로그는 켜져 있었고, 최대 1MB 순환이었습니다(관찰). 크기가 작아 오래된 기록은 밀려납니다.

### Credential Guard

- Credential Guard 가 켜지면 비밀은 LSAIso.exe(격리된 LSA 프로세스)에 있고, 가상화 기반 보안(VBS)으로 보호돼 나머지 OS 에서 접근할 수 없습니다[4].
- Windows 11 22H2 부터 요건을 만족하는 장치에서 기본으로 켜집니다[4]. 64비트 Secure Boot 장치만 지원합니다[4].

## 보안 지원 공급자(SSP) 등록

- MITRE 는 자격 증명을 더 캐내려고 SSP 를 등록하는 방법을 듭니다[1]. 조사에서는 아래 값에 낯선 DLL 이름이 더해졌는지 봅니다.
  - `HKLM\SYSTEM\CurrentControlSet\Control\Lsa\Security Packages`[1]
  - `HKLM\SYSTEM\CurrentControlSet\Control\Lsa\OSConfig\Security Packages`[1]
- 자격 증명과 관련된 정상 SSP 이름으로는 Msv, Wdigest, Kerberos, CredSSP 가 있습니다[1]. 이 이름 밖의 낯선 DLL 이 끼어 있는지 봅니다.

## WDigest

- WDigest 는 `HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest` 에서 설정합니다.
- 이 분석 PC 에는 이 키에 UseLogonCredential 값이 없었습니다(관찰). 값이 없으면 기본 동작을 따릅니다.
- UseLogonCredential 값이 1 로 더해졌으면 그 뜻과 시각을 확인합니다. 이 설정의 자세한 동작은 이번 자료로는 확인하지 못했습니다.

## 하이브·NTDS 복사

- SAM·SECURITY·SYSTEM 하이브를 복사해 대상 밖에서 해시를 푸는 방법이 있습니다. 하이브에서 해시를 푸는 구조는 [레지스트리 속 비밀번호 정보](../../../02-artifacts/credentials/sam-security/index.md) 에 있습니다(부트키 → NT 해시 → LSA 시크릿 → 캐시 자격 증명).
- 복사 명령이 실행됐다면 프로세스 생성 로그(4688·Sysmon 1)에서 명령줄을, 파일 생성은 Sysmon 11·MFT·USN 에서 찾습니다.
- 도메인 컨트롤러에서 NTDS.dit 을 복사하는 흔적은 [액티브 디렉터리 DB](../../../02-artifacts/credentials/ntds-dit.md) 에서 다룹니다.

## 메모리에서 찾기

- 메모리 이미지가 있으면 LSASS 영역과 문자열에서 자격 증명 흔적을 찾습니다. 방법은 [메모리 분석](../../../03-techniques/analysis/memory-forensics/index.md) 에서 다룹니다.

## 분석 흐름

1. 시간대와 감사·Sysmon 설정을 먼저 정합니다.
2. RunAsPPL·AuditLevel 값과 WinInit 12 로 사고 당시 LSA 보호 상태를 정합니다.
3. RunAsPPL 값이 바뀐 시각(레지스트리 마지막 기록 시각)과 재부팅 기록을 맞춰, 보호를 끈 흔적이 있는지 봅니다.
4. Sysmon 10 에서 lsass.exe 에 접근한 프로세스를 뽑습니다. 접근한 프로세스 이름과 GrantedAccess 를 표로 적습니다.
5. 4번의 접근 앞뒤로 프로세스 생성(4688·Sysmon 1)의 명령줄을 봅니다. 덤프·복사 명령의 문자열을 찾습니다.
6. 같은 구간의 파일 생성(Sysmon 11·MFT·USN)에서 덤프 파일이 생겼는지 봅니다.
7. Security Packages 값에 낯선 DLL 이, WDigest 에 UseLogonCredential 이 더해졌는지 봅니다.
8. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리하고, 빼낸 자격 증명이 쓰인 흔적은 [다른 PC 에서 원격 실행했나](psexec-wmi-winrm.md) 로 이어 봅니다.

## 흔한 오판

1. **lsass 접근 기록 하나로 덤프라고 단정합니다.** 정상 동작에서도 lsass 접근은 남습니다[2]. 접근한 프로세스·권한·이어지는 파일 생성을 함께 봅니다.
2. **덤프 파일을 이름으로만 찾습니다.** MITRE 예시의 파일 이름은 예시일 뿐입니다[1]. 이름은 얼마든지 바꿀 수 있습니다.
3. **RunAsPPL 이 켜져 있으니 덤프가 없었다고 봅니다.** 레지스트리 값에만 기댄 보호는 원격으로 끌 수 있습니다[4]. 값이 바뀐 흔적과 재부팅 기록을 봅니다.
4. **보호가 켜진 지금 상태를 사고 당시로 봅니다.** RunAsPPL 변경은 재부팅 뒤에 적용됩니다[4]. 지금 켜져 있어도 사고 당시엔 꺼져 있었을 수 있습니다.
5. **명령줄이 안 보이니 실행이 없었다고 봅니다.** 명령줄은 4688 명령줄 기록이나 Sysmon 을 켜야 남습니다. 설정이 꺼져 있었으면 실행이 있어도 명령줄이 없습니다.

## 보고서 문장 예

아래 값은 설명을 위해 만든 예입니다.

- 쓰지 않을 문장: "공격자가 덤프 도구로 관리자 비밀번호를 빼냈습니다."
- 쓸 문장: "이 PC 의 Sysmon 로그에는 ○○(UTC)에 프로세스 ○○이 lsass.exe 에 GrantedAccess ○○으로 접근한 이벤트 10 이 있습니다. 그 직후 ○○ 경로에 크기 ○○의 파일이 생긴 Sysmon 11 이 있습니다. RunAsPPL 값은 ○○이고, 그 값의 마지막 기록 시각은 ○○입니다. 이 기록은 해당 프로세스가 LSASS 에 접근하고 파일을 만들었음을 보여 줍니다. 그 파일에서 실제로 자격 증명을 읽었는지는 이 PC 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [레지스트리 속 비밀번호 정보 (SAM·SECURITY)](../../../02-artifacts/credentials/sam-security/index.md) · [액티브 디렉터리 DB (NTDS.dit)](../../../02-artifacts/credentials/ntds-dit.md) — 하이브·데이터베이스의 저장 구조입니다.
- [자격 증명 관리자와 볼트](../../../02-artifacts/credentials/credential-manager-windows-vault.md) · [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) — 다른 자격 증명 저장소입니다.
- [이미지 로드·프로세스 접근 (Sysmon 7·8·10)](../../../02-artifacts/event-logs/sysmon/7-8-10.md) — lsass 접근을 읽습니다.
- [프로세스 생성 (4688)](../../../02-artifacts/event-logs/4688.md) · [Sysmon 이벤트 1](../../../02-artifacts/event-logs/sysmon/1.md) — 덤프·복사 명령줄입니다.
- [Windows Defender 탐지 (1116·1117)](../../../02-artifacts/event-logs/1116-1117.md) — 덤프 도구 탐지 기록입니다.
- [프리페치](../../../02-artifacts/execution/prefetch/index.md) · [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) — 실행과 파일 생성 흔적입니다.
- [메모리 분석](../../../03-techniques/analysis/memory-forensics/index.md) — 메모리에서 자격 증명을 찾습니다.
- [비밀번호 대입 공격이 있었나](brute-force.md) · [다른 PC 에서 원격 실행했나](psexec-wmi-winrm.md) — 앞뒤 단계입니다.

## 참고 문헌

1. MITRE ATT&CK, "OS Credential Dumping: LSASS Memory, Sub-technique T1003.001" — https://attack.mitre.org/techniques/T1003/001/
2. JPCERT/CC, Tool Analysis Result Sheet — wmic — https://jpcertcc.github.io/ToolAnalysisResultSheet/details/wmic.htm
3. JPCERT/CC, Tool Analysis Result Sheet — PsExec — https://jpcertcc.github.io/ToolAnalysisResultSheet/details/PsExec.htm
4. Microsoft Learn, "Configure added LSA protection" — https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection
