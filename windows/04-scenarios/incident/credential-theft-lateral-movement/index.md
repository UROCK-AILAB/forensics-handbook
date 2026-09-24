---
title: "계정 탈취와 측면 이동"
parent: "시나리오 · 침해 사고"
nav_order: 3720
has_children: true
has_toc: false
---

# 계정 탈취와 측면 이동 (Credential Theft·Lateral Movement)

## 한 줄 요약

계정 탈취 (Credential Theft) 는 남의 비밀번호나 해시 같은 자격 증명 (Credential) 을 손에 넣는 일입니다. 측면 이동 (Lateral Movement) 은 손에 넣은 자격 증명으로 다른 PC 에 들어가 명령을 실행하는 일입니다. 이 허브는 비밀번호 대입, 자격 증명 빼내기, 원격 실행, 계정 생성·권한 상승의 흔적을 어디서 찾는지 안내합니다.

## 왜 중요한가

- MITRE ATT&CK 은 비밀번호 대입을 T1110(Brute Force) 으로, 자격 증명 빼내기를 T1003(OS Credential Dumping) 으로 나눕니다[1][2].
- 하위 페이지는 흔히 일어나는 순서대로 놓았습니다. 비밀번호를 맞혀 들어온 뒤 자격 증명을 빼내고, 그 자격 증명으로 다른 PC 에서 명령을 실행하고, 끝으로 계정을 만들거나 권한을 올리는 순서입니다.
- 실제 사건이 늘 이 순서를 따르지는 않습니다. 피싱으로 얻은 자격 증명을 쓰면 대입 흔적이 없습니다.
- MITRE T1110 도 다른 사고에서 새어 나온 자격 증명을 넣어 보는 방식(Credential Stuffing)을 따로 둡니다[1]. 그래서 대입 흔적이 없어도 다음 단계를 봅니다.
- 원격 실행은 명령을 보낸 출발 PC 와 명령을 받은 도착 PC 에 서로 다른 흔적을 남깁니다[3][4][5]. 조사하는 PC 가 어느 쪽인지부터 정해야 볼 곳을 고를 수 있습니다.
- 흔적 가운데 일부는 기본 설정에서도 남습니다. 나머지는 감사 정책 (Audit Policy) 이나 Sysmon 을 켜야 남습니다[3][4][5].

증명하지 못하는 것도 분명합니다.

- 기록이 없다고 일이 없었다고 읽지 않습니다. 감사 정책이 꺼져 있었으면 그 흔적은 처음부터 생기지 않습니다.
- 흔적 하나로 공격을 단정하지 않습니다. 정상적인 원격 wmic 실행에서도 도착 PC 의 WmiPrvSE.exe 가 lsass.exe 에 접근한 기록(Sysmon 10)이 남았습니다[4].
- 네트워크 로그온(로그온 유형 3) 하나만으로 원격 실행이라고 보지 않습니다. 유형 3 은 파일 공유 접근 같은 흔한 일에도 생깁니다. 같은 로그온 ID·같은 시각대의 서비스 설치·프로세스 생성과 이어 봅니다.
- 이벤트에 남는 것은 계정입니다. 계정 주인이 한 일인지, 계정을 훔친 사람이 한 일인지는 이벤트만으로 알 수 없습니다.

## 한눈에 보기

> 그림 자리: 네 단계(대입 → 자격 증명 빼내기 → 원격 실행 → 계정·권한)를 가로로 놓고, 단계마다 흔적이 남는 PC(시도를 받은 PC, 출발 PC, 도착 PC, 도메인 컨트롤러)와 먼저 볼 이벤트를 적은 그림

### 질문별 먼저 볼 흔적

| 질문 | 흔적이 남는 곳 | 먼저 볼 흔적 | Windows 버전·설정 | 자세히 |
|---|---|---|---|---|
| 비밀번호 대입이 있었나 | 비밀번호 시도를 받은 PC. 도메인 계정이면 도메인 컨트롤러 | 보안 로그 4625(로그온 실패), 4740(계정 잠김), 실패 뒤의 4624(로그온 성공) | 4740 은 Windows Vista·Windows Server 2008 부터 있습니다[6] | [비밀번호 대입 공격이 있었나](brute-force.md) |
| 자격 증명을 빼냈나 | 공격자가 이미 들어온 PC | lsass.exe 에 접근한 기록(Sysmon 10), 덤프 도구의 명령줄(4688·Sysmon 1), 덤프 파일 생성, LSA 보호 설정(RunAsPPL) | LSA 추가 보호는 Windows 8.1 부터 있습니다. Windows 11 22H2 이후 새로 설치한 PC 는 조건을 만족하면 기본으로 켜집니다[8] | [자격 증명을 빼냈나](credential-dumping.md) |
| 다른 PC 에서 원격 실행했나 | 출발 PC 와 도착 PC 양쪽 | 도착 PC: 서비스 설치(System 7045), ADMIN$·IPC$ 공유 접근(5140·5145), 로그온 유형 3, WmiPrvSE.exe 실행. 출발 PC: 도구의 프리페치, PsExec 사용권 동의 값(EulaAccepted) | JPCERT/CC 시트는 시험한 윈도 버전을 적지 않았습니다[3][4][5] | [다른 PC 에서 원격 실행했나](psexec-wmi-winrm.md) |
| 새 계정을 만들거나 권한을 올렸나 | 4732 는 워크스테이션·멤버 서버·도메인 컨트롤러 모두에서 생깁니다[7] | 4720(계정 생성), 4732(로컬 그룹에 구성원 추가), 4798·4799(그룹 구성원 조회), 뒤이은 4672(특수 권한) | 4732 는 Windows Vista·Windows Server 2008 부터 있습니다[7]. Microsoft 는 계정 관리 감사의 성공·실패를 모두 켜라고 권합니다[9] | [새 계정을 만들거나 권한을 올렸나](account-privilege.md) |

### 출발 PC·도착 PC·도메인 컨트롤러

출발 PC 는 원격 명령을 보낸 PC 이고, 도착 PC 는 원격 명령을 받은 PC 입니다. 측면 이동이 이어지면 한 PC 가 도착 PC 였다가 다시 출발 PC 가 될 수 있어서 두 쪽의 흔적을 모두 봅니다.

- 도착 PC 의 흔적에서 출발 PC 를 찾기도 합니다. PsExec 의 도착 PC 에 남는 공유 폴더 접근 기록(5145)에는 출발 PC 이름이 들어갑니다[3].
- 로그온 실패(4625)는 로그온을 시도한 컴퓨터에 남습니다. 도메인 계정이면 도메인 컨트롤러에도 4771·4776 이 남습니다.
- 전역 그룹과 유니버설 그룹은 도메인에만 있습니다[10].

### 기본 설정과 추가 설정

- JPCERT/CC 의 도구 분석 시트는 기본 설정에서 남는 흔적과 감사 정책·Sysmon 을 켜야 남는 흔적을 나눠 적습니다[3][4][5].
- PsExec 의 도착 PC 에서는 서비스 설치 기록(System 7045)과 프리페치가 기본 설정에서도 남습니다[3].
- 같은 도착 PC 라도 공유 폴더의 파일 접근 기록(5145)은 추가 감사 정책이 있어야 남습니다[3].
- wmic 흔적 가운데 레지스트리 변경은 Sysmon 이 있어야 남습니다[4].
- 그래서 수집한 이미지의 감사 정책을 먼저 확인하고, Sysmon 을 설치했는지도 봅니다. 확인하는 법은 [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) 과 [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md) 에서 다룹니다.

### 자료 기준

하위 페이지는 아래 자료를 기준으로 합니다. 버전이 바뀌면 이벤트 칸과 기본값이 달라질 수 있습니다.

| 자료 | 날짜 | 범위 |
|---|---|---|
| Microsoft 보안 감사 이벤트 문서 (4740, 4732, 계정 관리 감사, 그룹 관리 감사) | 문서 날짜 2021-09, 마지막 갱신 2026-04-27 | Windows 10 보관 문서(previous-versions) 입니다[6][7][9][10] |
| Microsoft "Configure added LSA protection" | — | LSA 보호와 Credential Guard 의 설정·이벤트[8] |
| MITRE ATT&CK T1110 | 버전 2.8, 마지막 수정 2026-05-12 | 비밀번호 대입의 하위 기법과 탐지[1] |
| MITRE ATT&CK T1003.001 | 마지막 수정 2026-05-12 | LSASS 메모리 덤프 방법과 탐지[2] |
| JPCERT/CC 도구 분석 시트 (PsExec·wmic·WinRM) | — | 출발 PC 와 도착 PC 의 흔적입니다. 시험한 윈도 버전은 적지 않았습니다[3][4][5] |
| 분석 PC 직접 조회 | — | Windows 11 Home(빌드 26200) 한 대의 이벤트 공급자 메타데이터, 로그 설정, 레지스트리 값입니다. 하위 페이지에 "(관찰)" 로 표시합니다 |

### 시각을 읽을 때

- Microsoft 문서의 예시 XML 에서 TimeCreated 의 SystemTime 값은 끝에 Z 가 붙은 UTC 입니다(예: `2015-08-21T22:06:08.576887500Z`)[6][7].
- 레코드 시각을 읽는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다.
- PC 의 시간대는 [시간대 설정](../../../02-artifacts/system-account/time-zone.md) 에서 확인합니다.
- 측면 이동은 여러 PC 에 걸칩니다. 출발 PC·도착 PC·도메인 컨트롤러의 기록을 한 줄로 합치는 법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 에서 봅니다.

## 읽는 순서

꼭 이 순서로 읽지 않아도 됩니다. 사건에서 먼저 드러난 흔적의 페이지부터 펼쳐도 됩니다.

1. [비밀번호 대입 공격이 있었나 (Brute Force)](brute-force.md) — 로그온 실패(4625)가 몰린 모양으로 한 계정 짐작과 여러 계정 스프레이를 나눕니다. 계정 잠김(4740)과 실패 뒤의 로그온 성공도 봅니다.
2. [자격 증명을 빼냈나 (Credential Dumping)](credential-dumping.md) — LSASS 메모리 덤프의 흔적을 lsass.exe 접근, 명령줄, 덤프 파일에서 찾습니다. LSA 보호(RunAsPPL)와 Credential Guard 가 켜져 있었는지, 꺼진 흔적이 있는지도 봅니다.
3. [다른 PC 에서 원격 실행했나 (PsExec·WMI·WinRM)](psexec-wmi-winrm.md) — PsExec·wmic·WinRM 이 출발 PC 와 도착 PC 에 남기는 흔적을 나눠 정리합니다. 서비스 설치 이벤트(7045·4697)도 다룹니다.
4. [새 계정을 만들거나 권한을 올렸나 (Account·Privilege)](account-privilege.md) — 계정 생성(4720)과 그룹 구성원 추가(4732 등)를 읽습니다. 계정을 만들기 전의 조회 이벤트(4798·4799)와 SAM 속 계정 목록도 봅니다.

## 함께 볼 페이지

- [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) — 4624·4625·4648·4672·4768·4769·4776 의 칸을 읽습니다. 이 묶음의 페이지는 이 칸 설명을 되풀이하지 않습니다.
- [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) — 어떤 흔적이 남을 수 있었는지 먼저 정합니다.
- [레지스트리 속 비밀번호 정보](../../../02-artifacts/credentials/sam-security/index.md) · [액티브 디렉터리 DB](../../../02-artifacts/credentials/ntds-dit.md) — 공격자가 빼내려는 자격 증명이 어디에 어떤 구조로 들어 있는지 봅니다.
- [메모리 분석](../../../03-techniques/analysis/memory-forensics/index.md) — 메모리 이미지에서 자격 증명을 찾습니다.
- [서비스 설치](../../../02-artifacts/event-logs/7045-4697.md) · [공유 폴더 접근](../../../02-artifacts/event-logs/5140-5145.md) · [원격 명령 실행 이벤트](../../../02-artifacts/event-logs/winrm-wmi-activity.md) — 원격 실행의 도착 PC 흔적을 읽습니다.
- [프로세스 생성](../../../02-artifacts/event-logs/4688.md) · [프리페치](../../../02-artifacts/execution/prefetch/index.md) — 도구를 실행한 명령줄과 실행 기록을 봅니다.
- [계정 생성·변경](../../../02-artifacts/event-logs/account-management-events.md) · [사용자 계정](../../../02-artifacts/system-account/sam.md) — 계정 이벤트와 SAM 의 계정 목록을 읽습니다.
- [원격 데스크톱 침입 확인](../rdp-intrusion.md) · [원격 제어 프로그램으로 누가 조작했나](../remote-access-tool-abuse.md) — 원격 데스크톱이나 원격 제어 프로그램으로 옮겨 간 경우를 다룹니다.
- [이벤트 로그 삭제](../../../02-artifacts/event-logs/1102-104.md) — 보안 로그를 지운 흔적을 봅니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](../../activity/user-attribution.md) — 계정이 아니라 사람을 특정할 때 봅니다.

## 참고 문헌

1. MITRE ATT&CK, "Brute Force, Technique T1110" (v2.8, 마지막 수정 2026-05-12). https://attack.mitre.org/techniques/T1110/
2. MITRE ATT&CK, "OS Credential Dumping: LSASS Memory, Sub-technique T1003.001" (마지막 수정 2026-05-12). https://attack.mitre.org/techniques/T1003/001/
3. JPCERT/CC, Tool Analysis Result Sheet — PsExec. https://jpcertcc.github.io/ToolAnalysisResultSheet/details/PsExec.htm
4. JPCERT/CC, Tool Analysis Result Sheet — wmic. https://jpcertcc.github.io/ToolAnalysisResultSheet/details/wmic.htm
5. JPCERT/CC, Tool Analysis Result Sheet — WinRM. https://jpcertcc.github.io/ToolAnalysisResultSheet/details/WinRM.htm
6. Microsoft Learn, "4740(S) A user account was locked out." https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4740
7. Microsoft Learn, "4732(S) A member was added to a security-enabled local group." https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4732
8. Microsoft Learn, "Configure added LSA protection". https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection
9. Microsoft Learn, "Audit User Account Management". https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-user-account-management
10. Microsoft Learn, "Audit Security Group Management". https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-security-group-management
