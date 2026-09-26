---
title: "시스템 기본 정보"
parent: "아티팩트 · 시스템·계정"
nav_order: 620
---

# 시스템 기본 정보 (OS Version·Computer Name·Install Date·Shutdown Time)

## 한 줄 요약

레지스트리의 SOFTWARE 하이브에는 윈도 제품 이름과 설치 시각이, SYSTEM 하이브에는 컴퓨터 이름과 마지막 정상 종료 시각이 있습니다. 분석을 시작할 때 가장 먼저 읽는 값들이며, 시각은 모두 UTC 로 해석합니다.

## 무엇을 기록하나 · 왜 생기나

윈도는 이 PC 에 깔린 윈도가 무엇이고 언제 설치됐는지를 SOFTWARE 하이브에 두고, 컴퓨터 이름은 SYSTEM 하이브의 설정 값으로 둡니다. 윈도를 정상으로 끄면 그 시각도 SYSTEM 하이브에 남습니다.

이 값들은 다음 일에 씁니다.

- **윈도 버전**을 알아야 다른 아티팩트의 위치와 형식을 고를 수 있습니다.
- **컴퓨터 이름**은 이벤트 로그나 다른 PC 의 기록에서 이 PC 를 찾을 때 씁니다.
- **설치 시각**은 지금 윈도에서 생긴 기록의 출발점입니다. 이보다 이른 시각이 나오면 이유를 따로 확인합니다.
- **마지막 정상 종료 시각**은 PC 사용 시간을 재구성할 때 끝점 하나가 됩니다.

조사 첫머리에 무엇을 확인하는지는 [포렌식 조사 절차](../../03-techniques/process-acquisition/investigation-process.md)에서 다룹니다. 시간대는 따로 [시간대 설정](time-zone.md)에서 다룹니다.

## 위치와 버전별 차이

| 알고 싶은 것 | 하이브 | 하이브 안의 키 경로 | 값 이름 |
|---|---|---|---|
| 제품 이름·수정 번호 | SOFTWARE | `Microsoft\Windows NT\CurrentVersion` | ProductName, UBR |
| 설치 시각 | SOFTWARE | `Microsoft\Windows NT\CurrentVersion` | InstallDate, InstallTime |
| 컴퓨터 이름 | SYSTEM | `ControlSet00x\Control\ComputerName\ComputerName` | ComputerName |
| 호스트 이름 | SYSTEM | `ControlSet00x\Services\Tcpip\Parameters` | Hostname |
| 마지막 정상 종료 시각 | SYSTEM | `ControlSet00x\Control\Windows` | ShutdownTime |

- 실행 중인 PC 에서 SOFTWARE 쪽 키는 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion` 으로 보입니다.
- 하이브 파일이 디스크 어디에 있는지는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

### ControlSet 번호 고르기

SYSTEM 하이브의 경로에 나오는 `ControlSet00x` 의 x 자리는 정해진 번호가 아닙니다. SYSTEM 하이브의 `Select` 키에 있는 `Current` 값이 번호를 알려 줍니다. `Current` 가 1 이면 `ControlSet001` 을 읽습니다. 이 페이지와 [시간대 설정](time-zone.md)의 SYSTEM 경로는 모두 이 규칙을 따릅니다.

### 버전별 차이

이 페이지가 기댄 자료는 공개 포렌식 도구(RegRipper)의 플러그인 소스인데, 이 자료는 어느 값이 어느 Windows 버전부터 있는지 적지 않습니다. 도구 출력에 빈칸이 있으면 하이브에서 그 값이 정말 없는지 직접 확인합니다.

## 구조

### `Microsoft\Windows NT\CurrentVersion`

| 값 이름 | 저장 형식 | 뜻 |
|---|---|---|
| ProductName | 글자 | 표시용 제품 이름입니다. 예: "Windows 10 Pro" |
| UBR (Update Build Revision) | 숫자 | 빌드 번호 뒤에 붙는 수정 번호입니다. 예: 빌드 19045 의 .3324 |
| InstallDate | REG_DWORD (4바이트) | 설치 시각입니다. 1970-01-01 00:00:00 UTC 부터 센 초입니다 |
| InstallTime | REG_QWORD (8바이트) | 설치 시각입니다. FILETIME 이라 InstallDate 보다 정밀합니다 |

공개 도구는 이 키에서 ReleaseID, CSDVersion, BuildLab, BuildLabEx, CompositionEditionID, RegisteredOrganization, RegisteredOwner 도 읽어 보여 줍니다. 이 값들은 도구 출력 그대로 옮기고, 뜻을 풀어 쓸 때는 따로 확인합니다.

### 컴퓨터 이름

- `Control\ComputerName\ComputerName` 키의 `ComputerName` 값이 컴퓨터 이름입니다.
- `Services\Tcpip\Parameters` 키의 `Hostname` 값도 호스트 이름으로 읽습니다.
- 공개 도구는 두 값을 함께 보여 줍니다. 두 값이 다르면 이유를 확인합니다.

### ShutdownTime

형식은 REG_BINARY 8바이트입니다. 앞 4바이트와 뒤 4바이트를 각각 32비트 리틀 엔디언 정수로 읽으며, 앞 4바이트가 낮은 자리이고 뒤 4바이트가 높은 자리입니다. 둘을 이은 값이 FILETIME 이고, 8바이트를 한 번에 리틀 엔디언으로 읽은 값과 같습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 하이브를 마지막으로 쓴 때 이 PC 에 깔려 있던 윈도의 제품 이름과 수정 번호 | 조사 대상 날짜에 어떤 버전이었는지. 그사이 갱신했을 수 있습니다 |
| 지금 윈도에 설치 시각으로 적힌 값 | PC 를 처음 산 날이나 하드웨어를 처음 켠 날 |
| 지금 설정된 컴퓨터 이름 | 예전에 쓰던 컴퓨터 이름 |
| 마지막으로 정상 종료한 시각 | 마지막으로 전원이 꺼진 시각. 정상 종료가 아닌 꺼짐까지 담는다고 보면 안 됩니다 |
| | 누가 윈도를 설치했는지. 누가 PC 를 껐는지 |

### 보고서 문장

아래 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "SYSTEM 하이브의 ShutdownTime 값은 2025-03-14 09:05:12 UTC 입니다. 이 값은 마지막 정상 종료 시각입니다."
- 쓰면 안 되는 문장: "이 PC 는 2025-03-14 18:05 에 마지막으로 꺼졌고, 그 뒤로 아무도 쓰지 않았습니다."

## 시각 해석

| 값 | 저장 방식 | 기준 | 바뀌는 때 |
|---|---|---|---|
| InstallDate | 4바이트 정수. 1970-01-01 부터 센 초 | UTC | 설치 |
| InstallTime | 8바이트 FILETIME. 1601-01-01 부터 센 100나노초 | UTC | 설치 |
| ShutdownTime | 8바이트 FILETIME | UTC | 정상 종료 |

- 두 방식의 계산은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다.
- 현지 시각으로 바꿀 때는 이 PC 의 [시간대 설정](time-zone.md)을 씁니다.
- InstallDate 와 InstallTime 은 같은 설치 시각을 다른 정밀도로 적은 값이라서 두 값이 초 단위까지 맞는지 확인하는데, 둘이 늘 맞는다는 규칙은 이 페이지가 기댄 자료에 없습니다. 어긋나면 먼저 도구가 형식을 바르게 읽었는지 봅니다.
- 로컬 계정을 만든 시각은 레지스트리에 직접 없습니다. 추정할 자료가 모자라면 설치 시각을 대신 쓰기도 합니다. 추정 방법은 [사용자 계정 (SAM)](sam.md)에서 다룹니다.

## 함정과 한계

1. **ControlSet 을 잘못 고릅니다.** `Select\Current` 를 보지 않고 `ControlSet001` 을 읽으면 다른 제어 세트의 값을 쓸 수 있습니다.
2. **두 설치 시각의 형식을 바꿔 읽습니다.** InstallDate 를 FILETIME 으로 읽거나 InstallTime 을 Unix 초로 읽으면 터무니없는 날짜가 나옵니다.
3. **설치 시각을 PC 를 처음 쓴 때로 씁니다.** 이 값은 지금 윈도의 설치 시각입니다. 다시 설치했거나 크게 갱신했을 때 어떤 값이 남는지는 이 값만으로 판별하지 못합니다. [윈도 업데이트 기록](windows-update-cbs-log.md)과 맞춰 봅니다.
4. **ShutdownTime 을 마지막 사용 시각으로 씁니다.** 정상 종료 뒤에 PC 를 다시 켰다가 전원이 끊겼다면 그 사용은 이 값에 없습니다.
5. **켜진 PC 에서 수집한 하이브를 그대로 읽습니다.** 수집 당시 PC 가 켜져 있었다면 ShutdownTime 은 그 전의 정상 종료 시각입니다.
6. **도구가 현지 시각으로 바꿔 보여 줍니다.** 도구 설정에 따라 분석 PC 의 시간대로 바뀐 시각이 나올 수 있습니다.

### 지우기와 조작

- 관리자 권한이 있으면 레지스트리 값을 고칠 수 있습니다. 키의 마지막 기록 시각(LastWrite)과 다른 기록을 함께 봅니다.
- 옛 값은 [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 속 하이브에 남아 있을 수 있습니다. 하이브 안의 빈 공간에 남은 옛 값을 찾는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.
- 컴퓨터 이름을 바꾸면 이 키에는 새 이름만 남습니다. 예전 이름은 다른 기록에서 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 값 형식을 보고 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다. 하이브 파일에서 값 데이터를 찾아가는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

```
InstallDate  (4바이트)  00 F1 53 65
InstallTime  (8바이트)  87 D6 7F C6 47 17 DA 01
ShutdownTime (8바이트)  00 54 57 31 C0 94 DB 01
```

**InstallDate**

1. `00 F1 53 65` 를 리틀 엔디언으로 읽으면 0x6553F100 입니다.
2. 이 수는 10진으로 1,700,000,000 입니다.
3. 1970-01-01 00:00:00 UTC 에 1,700,000,000초를 더하면 2023-11-14 22:13:20 UTC 입니다.
4. 한국 시각(UTC+9)으로는 2023-11-15 07:13:20 입니다.

**InstallTime**

1. 8바이트를 리틀 엔디언으로 읽으면 0x01DA1747C67FD687 입니다.
2. 이 수는 10진으로 133,444,736,001,234,567 입니다. 1601-01-01 00:00:00 UTC 부터 센 100나노초 단위 값입니다.
3. 날짜로 바꾸면 2023-11-14 22:13:20.1234567 UTC 입니다.
4. InstallDate 와 초까지 같습니다. InstallTime 에는 1초보다 작은 자리까지 있습니다.

**ShutdownTime**

1. 앞 4바이트 `00 54 57 31` 을 리틀 엔디언으로 읽으면 0x31575400 입니다. 낮은 자리입니다.
2. 뒤 4바이트 `C0 94 DB 01` 을 리틀 엔디언으로 읽으면 0x01DB94C0 입니다. 높은 자리입니다.
3. 높은 자리를 앞에 두고 이으면 0x01DB94C031575400 입니다. 10진으로 133,864,167,120,000,000 입니다.
4. 날짜로 바꾸면 2025-03-14 09:05:12 UTC 입니다. 한국 시각으로는 같은 날 18:05:12 입니다.

> 그림 자리: ShutdownTime 8바이트를 낮은 자리 4바이트와 높은 자리 4바이트로 나눠 FILETIME 으로 잇는 과정을 보여 주는 그림

### 공개 도구로 한 번

RegRipper 의 `winver`·`compname`·`shutdown` 플러그인이 이 값들을 읽습니다. 레지스트리 뷰어로 값을 직접 봐도 됩니다. 도구를 쓸 때는 다음을 확인합니다.

- 시각을 UTC 로 보여 주는지, 현지 시각으로 바꿔 보여 주는지 확인합니다.
- 도구가 어느 ControlSet 을 읽었는지 확인합니다.
- 값 하나쯤은 헥스로 읽은 결과와 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [켜짐·꺼짐](../event-logs/power-on-off-events.md) | 이벤트 로그의 종료 기록과 ShutdownTime. 정상 종료가 아닌 꺼짐도 여기서 찾습니다 |
| [윈도 업데이트 기록](windows-update-cbs-log.md) | 설치 뒤의 갱신 이력. 지금 수정 번호(UBR)가 언제 적용됐는지 |
| [시간대 설정](time-zone.md) | 설치·종료 시각을 현지 시각으로 바꿀 때 쓸 편차 |
| [사용자 계정 (SAM)](sam.md) | 계정 기록의 시각이 설치 시각보다 뒤인지 |
| [마스터 파일 테이블](../filesystem/mft.md) | 설치 시각 무렵에 생긴 파일이 있는지. 설치 시각보다 이른 생성 시각이 있는지 |
| [네트워크 인터페이스 설정](../network/tcp-ip-interfaces.md) | 컴퓨터 이름과 함께 이 PC 를 네트워크에서 가리키는 정보 |

PC 를 켜고 끈 시간을 여러 기록으로 재구성하는 흐름은 [PC 사용 시간 재구성](../../04-scenarios/activity/system-usage-time.md)에서 다룹니다.

## 실습

**NIST CFReDS 같은 공개 시험 이미지**에서 SYSTEM·SOFTWARE 하이브를 꺼내 풀어 봅니다.

1. `Select\Current` 값은 몇입니까? 어느 ControlSet 을 읽어야 합니까?
2. ProductName 과 UBR 은 무엇입니까?
3. InstallDate 를 헥스로 읽어 UTC 로 바꿔 보십시오. 이 PC 의 시간대로 현지 시각도 구해 보십시오.
4. InstallTime 이 있다면 InstallDate 와 초까지 맞는지 확인하십시오.
5. ShutdownTime 을 이벤트 로그의 마지막 종료 기록과 비교해 보십시오.
6. ComputerName 과 Hostname 은 같습니까?

**직접 만든 가상 머신**에서도 해 봅니다.

1. 정상으로 종료한 뒤 ShutdownTime 을 적어 둡니다.
2. 다시 켜서 가상 머신의 전원을 강제로 끊습니다.
3. ShutdownTime 이 바뀌었는지 확인합니다.
4. 컴퓨터 이름을 바꾸고 다시 시작한 뒤, 두 이름 값이 어떻게 바뀌었는지 확인합니다.

## 참고 문헌

- keydet89, RegRipper3.0 `winver.pl` (CurrentVersion 값, InstallDate·InstallTime 해석) — https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/winver.pl
- keydet89, RegRipper3.0 `compname.pl` (ComputerName, Hostname) — https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/compname.pl
- keydet89, RegRipper3.0 `shutdown.pl` (ShutdownTime) — https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/shutdown.pl
