---
title: "로그온 세션·클립보드·화면 수집"
parent: "라이브 응답"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 3150
---

# 로그온 세션·클립보드·화면 수집 (Sessions·Clipboard·Screen)

## 한 줄 요약

켜진 시스템에서 화면에 보이는 것, 지금 로그온한 세션, 클립보드 내용을 남깁니다. 화면은 시스템을 만지기 전에 사진으로 찍습니다. 로그온 세션은 순간마다 바뀌므로 네트워크 연결 다음으로 모읍니다. 클립보드 기록은 다시 시작하면 고정한 항목만 남기고 지워집니다.

## 언제 쓰나

시스템을 켜진 채로 발견했을 때는 무엇이든 만지기 전에 화면부터 씁니다. 누가 이 시스템에 로그온해 있는지, 원격으로 붙은 사용자가 있는지 확인할 때와 복사해 둔 글·그림이 사건과 이어질 수 있을 때도 씁니다.

NIST SP 800-86 순서에서 로그인 세션은 둘째인데, 접속한 사용자 목록이 순간마다 바뀌기 때문입니다. 순서 전체는 [수집 순서와 원칙](order-of-volatility.md)에서 다룹니다.

## 절차

1. **화면을 사진으로 남깁니다.** 키보드와 마우스를 만지기 전에 찍습니다. 아래 "화면" 을 봅니다.
2. **잠금·절전 상태면 어떻게 할지 정합니다.** 깨우거나 암호를 풀어 휘발성 데이터를 모을지 정합니다. 재부팅은 휘발성 데이터를 모두 잃습니다.
3. **로그온 세션을 남깁니다.** `query user`, `Win32_LogonSession`, `tasklist /v` 결과를 파일로 남깁니다. 아래 "로그온 세션" 을 봅니다.
4. **클립보드를 남깁니다.** 지금 클립보드 내용과 클립보드 기록을 남깁니다. 아래 "클립보드" 를 봅니다.
5. **컴퓨터 구성과 주변 장치를 사진으로 남깁니다.**
6. **명령을 돌린 시각과 결과 파일의 해시를 적습니다.**

## 화면

증거가 필요할 수 있으면 시스템을 만지기 전에 화면에 보이는 것을 모두 기록하고, 모니터에 보이는 사진, 문서, 실행 중인 프로그램을 메모하거나 사진으로 찍습니다[1]. 화면 보호기가 켜져 있으면 암호가 걸려 있을 수 있으므로 그것도 기록합니다.

절전 상태이거나 암호 보호가 보이면 깨우거나 암호를 풀어 휘발성 데이터를 모을지 정해야 합니다. 암호 걸린 화면 보호기는 재부팅하면 넘어갈 수 있지만 휘발성 데이터가 모두 사라지고, 지문 인식 같은 추가 인증이 걸려 있어도 같은 문제가 생깁니다. 컴퓨터 구성과 주변 장치도 사진으로 남깁니다.

> 그림 자리: 화면 → 잠금 상태 판단 → 세션 → 클립보드 → 주변 장치 사진으로 이어지는 현장 순서도

## 로그온 세션

### OS 가 관리하는 정보

OS 는 아래 정보를 관리할 수 있습니다[1].

- 지금 로그인한 사용자, 세션 시작 시각과 길이
- 이전 로그온의 성공과 실패
- 특권 사용
- 가장 (impersonation)

다만 로그온 감사를 켜 두어야 남는 정보도 있습니다. 감사 설정은 [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md)에서 다룹니다. 로그온 기록은 어떤 사건이 일어날 때 그 계정이 쓰이고 있었는지 확인하는 데 씁니다.

### query user

| 열 | 뜻 |
|---|---|
| 사용자 이름 | 세션의 사용자 |
| 세션 이름 | 세션 이름 |
| 세션 ID | 세션 번호 |
| 상태 | 활성 또는 연결 끊김 |
| 유휴 시간 | 마지막 키 입력이나 마우스 움직임 뒤로 지난 분 |
| 로그온 시각 | 로그온한 날짜와 시각 |

현재 세션 앞에는 `>` 가 붙습니다. 이 명령을 쓰려면 모든 권한 (Full Control) 이나 특별 접근 권한이 있어야 하며, 명령 설명은 원격 데스크톱 세션 호스트 서버를 기준으로 합니다[4]. Windows 11 Home 에는 `quser.exe` 도 `query.exe` 도 없습니다. 다른 판에서도 명령이 있는지 먼저 확인합니다.

### Win32_LogonSession

WMI 의 `Win32_LogonSession` 클래스는 로그온 세션을 하나씩 보여 줍니다[3]. 속성으로는 `LogonId`, `LogonType`, `StartTime`, `AuthenticationPackage` 가 나옵니다. 보통 PC 에서는 `LogonType` 0, 2, 5 세션이 함께 보입니다 (예: 0 이 1개, 2 가 6개, 5 가 4개).

`LogonType` 값의 뜻은 아래와 같습니다[3].

| 값 | 이름 | 뜻 |
|---|---|---|
| 0 | — | System 계정만 씁니다 |
| 2 | Interactive | 이 컴퓨터를 대화형으로 쓰는 사용자 |
| 3 | Network | 네트워크 로그온 |
| 4 | Batch | 사용자가 직접 개입하지 않는 일괄 처리 |
| 5 | Service | 서비스 로그온 |
| 7 | Unlock | 워크스테이션 잠금 해제 |
| 8 | NetworkCleartext | 인증 패키지에 이름과 암호를 남겨 두는 네트워크 로그온 |
| 9 | NewCredentials | 현재 토큰을 복제하고 바깥 연결에만 다른 자격 증명을 씁니다 |
| 10 | RemoteInteractive | 원격이면서 대화형인 터미널 서비스 세션 |
| 11 | CachedInteractive | 네트워크에 묻지 않고 캐시한 자격 증명으로 로그온 |

값에는 6 (Proxy), 12 (CachedRemoteInteractive), 13 (CachedUnlock) 도 있습니다[3]. 이벤트 로그의 로그온 유형은 [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md)에서 다룹니다.

### 프로세스와 세션 잇기

`Win32_Process` 와 `Win32_LogonSession` 은 연관 클래스 `Win32_SessionProcess` 로 이어지며, 이 연결로 어떤 프로세스가 어느 로그온 세션에 속하는지 알 수 있습니다. `tasklist /v` 의 세션 열과 사용자 열도 함께 봅니다. 프로세스 쪽 수집 방법은 [프로세스·DLL·핸들 수집](processes-dlls-handles.md)에서 다룹니다.

## 클립보드

### 클립보드 기록의 규칙

Windows 11 과 Windows 10 의 클립보드 기록 규칙은 아래와 같습니다[5].

| 항목 | 내용 |
|---|---|
| 켜는 방법 | Windows 로고 키 + V 를 처음 누를 때 켜거나, 시작 > 설정 > 시스템 > 클립보드에서 켭니다 |
| 개수 | 25개까지 담습니다. 고정하지 않은 오래된 항목은 저절로 지워집니다 |
| 크기 | 항목 하나에 4MB 까지 |
| 형식 | 텍스트, HTML, 비트맵 |
| 재시작 | PC 를 다시 시작할 때마다 고정한 항목을 빼고 기록이 지워집니다 |
| 기기 간 동기화 | Microsoft 계정이나 회사 계정에 묶입니다. 자동 또는 수동으로 동기화합니다 |

재부팅하면 고정하지 않은 기록이 사라지므로 켜진 상태에서 모아야 합니다.

### 모으는 방법

PowerShell 5.1 에는 `Get-Clipboard` 가 있습니다. `Microsoft.PowerShell.Management` 모듈의 명령이고, `-Format`, `-TextFormatType`, `-Raw` 인자를 받습니다. 이 명령은 지금 클립보드에 있는 한 건만 읽고 기록 목록 25개는 읽지 않습니다.

기록이 켜져 있으면 목록 창을 열어 보이는 그대로 사진으로 남깁니다. 기록이 꺼져 있으면 켜는 것이 설정을 바꾸는 일이므로 수집하면서 새로 켜지 않습니다.

## 함정과 한계

1. **화면보다 명령을 먼저 칩니다.** 창이 바뀌거나 화면 보호기가 풀려 처음 모습이 사라집니다. 사진을 먼저 찍습니다.
2. **잠금 화면을 넘으려고 재부팅합니다.** 화면 보호기 암호는 넘어갈 수 있어도 휘발성 데이터가 모두 사라집니다.
3. **`query user` 가 어디에나 있다고 봅니다.** Windows 11 Home 에는 이 명령이 없습니다. `Win32_LogonSession` 과 `tasklist /v` 를 함께 준비합니다.
4. **`LogonType` 숫자를 짐작으로 풉니다.** 위의 표에 적은 뜻으로 읽습니다. 예를 들어 0 은 System 계정의 세션이고, 이상한 로그온이 아닙니다.
5. **`Get-Clipboard` 결과를 클립보드 기록 전체로 씁니다.** 이 명령은 한 건만 읽습니다.
6. **클립보드 기록이 비어 있으면 복사한 적이 없다고 봅니다.** 기록이 꺼져 있었거나, 재시작으로 지워졌거나, 25개를 넘어 밀려났을 수 있습니다.

## 결과를 어떻게 해석하나

### 증명하는 것 / 증명하지 못하는 것

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 수집 시각에 이 사용자의 세션이 활성 또는 연결 끊김 상태였습니다 | 그 세션을 실제로 사람이 조작했는지. 유휴 시간으로 짐작할 뿐입니다 |
| 세션의 로그온 시각 (대상 시스템 시계 기준) | 수집 전에 로그오프한 세션. 이런 세션은 이벤트 로그에서 찾습니다 |
| 수집 시각에 클립보드에 이 내용이 있었습니다 | 이 PC 에서 복사했는지. 기기 간 동기화를 켰다면 다른 기기에서 복사했을 수 있습니다 |
| 화면 사진에 보이는 창과 문서 | 그 창을 연 사람이 누구인지 |

아래 보고서 문장의 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "2025-03-14 10:20 (KST) 에 수집한 세션 목록에서 사용자 user01 의 세션이 활성 상태였고, 유휴 시간은 3분이었습니다."
- 쓰면 안 되는 문장: "user01 이 10:17 까지 PC 를 쓰고 있었습니다."

### 함께 볼 페이지

| 함께 볼 페이지 | 무엇을 맞춰 보나 |
|---|---|
| [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) | 수집 전의 로그온·로그오프 이력 |
| [원격 데스크톱 이벤트](../../../02-artifacts/event-logs/rdp-event-logs/index.md) | 원격으로 붙은 세션의 이력 |
| [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) | 세션 정보를 사용자 특정에 쓰는 흐름 |

## 참고 문헌

- K. Kent, S. Chevalier, T. Grance, H. Dang, "NIST SP 800-86: Guide to Integrating Forensic Techniques into Incident Response", NIST, 2006-08 — https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
- Microsoft Learn, "Win32_Process class" — https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process
- Microsoft Learn, "Win32_LogonSession class" — https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-logonsession
- Microsoft Learn, "query user" — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/query-user
- Microsoft Support, "Clipboard in Windows" — https://support.microsoft.com/en-us/windows/clipboard-in-windows-c436501e-985d-1c8d-97ea-fe46ddf338c6
