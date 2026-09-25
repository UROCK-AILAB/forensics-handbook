---
title: "작업표시줄 사용 기록"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 1050
---

# 작업표시줄 사용 기록 (FeatureUsage)

## 한 줄 요약

Windows 10 1903 이후 사용자 하이브(NTUSER.DAT)의 `FeatureUsage` 키에 작업 표시줄에서 앱을 띄우고, 누르고, 오른쪽 클릭한 횟수가 앱마다 쌓이지만 값에는 시각이 없고, 키의 `KeyCreationTime` 값은 그 사용자가 처음 대화형 로그온한 무렵을 가리킵니다.

## 무엇을 기록하나 · 왜 생기나

작업 표시줄에서 일어난 동작을 종류별 하위 키에 나눠 세며, 값 하나가 앱 하나이고 값 데이터는 횟수입니다. 기록은 계정마다 따로 남습니다. CrowdStrike 에 따르면 그 계정이 대화형으로 로그온한 적이 없으면 키가 없고, 작업 표시줄로 다루지 않은 앱은 이 숫자에 잡히지 않습니다.

## 위치와 버전별 차이

```
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage
```

CrowdStrike 는 이 경로를 `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage` 로 적고, Windows 10 1903 이후에서 이 키를 관찰했다고 적습니다. 그보다 앞선 버전에는 없을 수 있습니다.

| 하위 키 | Windows 10 1903 이후 (CrowdStrike) | Windows 11 25H2 한 대 |
|---|---|---|
| AppBadgeUpdated | 있음 | 있음 |
| AppLaunch | 있음 | 있음 |
| AppSwitched | 있음 | 있음 |
| ShowJumpView | 있음 | 있음 |
| TrayButtonClicked | 있음 | 없음 |

Windows 11 열은 PC 한 대에서 본 결과입니다.

하이브 파일의 구조와 수집 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 구조

```
FeatureUsage
    KeyCreationTime        REG_QWORD  (FILETIME 숫자)
    AppBadgeUpdated\       <앱 이름> = REG_DWORD 횟수
    AppLaunch\             <앱 이름> = REG_DWORD 횟수
    AppSwitched\           <앱 이름> = REG_DWORD 횟수
    ShowJumpView\          <앱 이름> = REG_DWORD 횟수
    TrayButtonClicked\     <버튼 이름> = REG_DWORD 횟수
```

**하위 키의 뜻 (CrowdStrike 의 정의)**

| 하위 키 | 세는 것 |
|---|---|
| AppBadgeUpdated | 실행 중인 앱의 배지 아이콘이 바뀐 횟수 |
| AppLaunch | 작업 표시줄에 고정한 앱을 실행한 횟수 |
| AppSwitched | 앱으로 포커스를 옮긴 횟수(작업 표시줄에서 왼쪽 클릭) |
| ShowJumpView | 작업 표시줄에서 앱을 오른쪽 클릭한 횟수 |
| TrayButtonClicked | 작업 표시줄의 기본 단추(시계, 시작 단추 등)를 누른 횟수 |

**값 이름의 형태**

Windows 11 PC 한 대에서 본 값은 모두 REG_DWORD 횟수였습니다. 값 이름은 아래 형태였습니다.

- 앱 사용자 모델 ID (AppUserModelID). `…!App` 처럼 이름에 `!` 가 들어 있습니다
- `!` 없는 앱 ID. 예를 들어 `MSEdge`, `Microsoft.Windows.Explorer` 입니다
- `C:\…` 로 시작하는 전체 경로
- 알려진 폴더 GUID 로 시작하는 경로. 예를 들어 `{6D809377-…}\…` 은 Program Files 아래입니다. GUID 를 경로로 푸는 표는 [UserAssist](userassist.md) 페이지에 있습니다
- `*PID` 뒤에 16진수 8자리가 붙은 이름. AppSwitched 에 6개 있었습니다
- 숫자만으로 된 이름

`*PID…` 이름과 숫자 이름이 무엇을 가리키는지는 확인하지 못했습니다.

같은 PC 의 값 수는 AppBadgeUpdated 11개, AppLaunch 9개, AppSwitched 61개, ShowJumpView 19개였습니다.

## 증거로서 의미

### 증명하는 것

- 이 계정으로 작업 표시줄에서 이 앱을 다룬 기록이 있습니다. 어떤 동작인지는 하위 키가 말합니다.
- AppLaunch 에 값이 있으면, 작업 표시줄에 고정한 그 앱을 작업 표시줄에서 실행한 횟수가 기록돼 있습니다.
- `FeatureUsage` 키가 있으면 그 계정이 대화형으로 로그온한 적이 있습니다(CrowdStrike).
- `KeyCreationTime` 은 그 계정이 처음 대화형 로그온한 무렵을 가리킵니다(CrowdStrike).

### 증명하지 못하는 것

- **언제 했나.** 값에는 시각이 없습니다.
- **작업 표시줄 밖의 사용.** CrowdStrike 에 따르면 작업 표시줄로 다루지 않은 앱은 이 숫자에 잡히지 않습니다. 시작 메뉴나 명령줄로만 띄운 앱은 값이 없을 수 있습니다. 값이 없다고 실행하지 않은 것은 아닙니다.
- **정확한 첫 로그온 시각.** 아래 "시각 해석" 에서 보듯 다른 흔적보다 늦을 수 있습니다.
- **키보드 앞의 사람.** 하이브가 가리키는 것은 계정입니다. 사람을 좁히는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

보고서에는 "이 계정의 FeatureUsage\AppSwitched 에 이 앱의 값이 있고, 횟수는 N 이다" 처럼 씁니다. 횟수에 시각을 붙이지 않습니다.

## 시각 해석

`KeyCreationTime` 은 REG_QWORD 이며 CrowdStrike 는 이 값을 64비트 FILETIME 숫자로 설명합니다. UTC 로 읽고, 변환은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다. CrowdStrike 는 이 값을 키가 처음 만들어진 때, 곧 그 사용자가 처음 대화형 로그온한 때로 봅니다.

Windows 11 PC 한 대에서 `KeyCreationTime` 은 같은 날 가장 오래된 UserAssist·BAM 항목보다 20여 분 늦었으므로 첫 로그온 시각 그 자체로 쓰지 말고 "그 무렵" 으로 씁니다. 첫 로그온 시각은 [로그온·로그오프](../event-logs/logon-events/index.md) 이벤트와 맞춰 봅니다.
같은 PC 에서 하위 키의 마지막 기록 시각 (LastWrite) 은 사용할 때마다 바뀌었고, AppBadgeUpdated·AppSwitched 의 마지막 기록 시각은 조사 당일이었습니다. 하위 키의 마지막 기록 시각은 그 종류의 동작이 마지막으로 셈에 들어간 무렵을 말하며, 어느 앱의 값이 바뀌었는지는 말하지 않습니다.

같은 PC 에서 부모 키 `FeatureUsage` 의 마지막 기록 시각은 `KeyCreationTime` 과 같은 날이었습니다. 하위 키가 바뀌어도 부모 키의 시각은 따라 바뀌지 않았습니다.

## 함정과 한계

- **값에 시각이 없습니다.** 횟수를 타임라인에 올리려면 다른 아티팩트의 시각이 필요합니다.
- **하위 키가 버전마다 다를 수 있습니다.** Windows 11 PC 한 대에는 TrayButtonClicked 가 없었습니다.
- **값 이름 형태가 여러 가지입니다.** 같은 앱이 앱 ID, 전체 경로, 알려진 폴더 GUID 경로 가운데 어느 것으로든 남을 수 있습니다. 하나로 묶기 전에 같은 앱인지 확인합니다.
- **뜻을 모르는 이름이 있습니다.** `*PID…` 이름과 숫자 이름은 해석하지 않고 그대로 적어 둡니다.
- **값과 키는 지울 수 있습니다.** 값이 적거나 없으면 이전 시점 하이브를 [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에서 꺼내 비교합니다. 조작 흔적을 찾는 흐름은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에 있습니다.
- **하이브 사본만 보면 최근 변경이 빠질 수 있습니다.** 하이브 로그를 함께 수집합니다.

## 직접 분석해 보기

### 헥스로 한 번

**`KeyCreationTime` 값 8바이트.** 아래 바이트는 CrowdStrike 글의 예시 값 132286223503288727 을 리틀 엔디언 바이트로 옮긴 것입니다. 특정 검체에서 꺼낸 값이 아닙니다.

```
97 69 97 90 9E F9 D5 01
```

1. 8바이트를 리틀 엔디언으로 읽으면 `0x01D5F99E90976997` 입니다.
2. 10진수로 바꾸면 132286223503288727 입니다. REG_QWORD 를 10진수로 보여 주는 도구에는 이 숫자가 보입니다.
3. 이 수는 1601-01-01 부터 센 100나노초 단위의 수입니다.
4. UTC 로 바꾸면 2020-03-14 01:19:10 입니다.

**횟수 값 4바이트.** 아래 바이트는 명세로 만든 예시입니다.

```
05 00 00 00
```

REG_DWORD 를 리틀 엔디언으로 읽으면 5 입니다. 그 하위 키가 세는 동작이 5번 있었다는 뜻입니다.

### 공개 도구로 한 번

1. 사용자 프로필에서 NTUSER.DAT 와 하이브 로그를 함께 사본으로 뜹니다.
2. 레지스트리 뷰어로 `Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage` 를 엽니다.
3. `KeyCreationTime` 을 위 풀이대로 직접 바꿔 봅니다.
4. 하위 키마다 값 이름과 횟수를 목록으로 뽑고, 하위 키의 마지막 기록 시각도 적습니다.
5. 알려진 폴더 GUID 로 시작하는 이름은 경로로 풀어 둡니다.
6. FeatureUsage 를 풀어 주는 공개 레지스트리 도구가 있으면 결과를 직접 뽑은 목록과 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| UserAssist | 같은 계정이 탐색기로 띄운 횟수와 마지막 실행 시각을 봅니다 | [UserAssist](userassist.md) |
| BAM | 같은 앱의 최근 실행 시각을 봅니다 | [BAM·DAM](background-activity-moderator.md) |
| 점프리스트 | 작업 표시줄 오른쪽 클릭 메뉴와 같은 앱의 최근 파일을 봅니다 | [점프리스트](../file-folder-usage/jump-lists.md) |
| 바로가기 파일 | 작업 표시줄에 고정한 앱의 바로 가기를 봅니다 | [바로가기 파일](../file-folder-usage/lnk.md) |
| 로그온·로그오프 | `KeyCreationTime` 을 첫 로그온 이벤트와 맞춰 봅니다 | [로그온·로그오프](../event-logs/logon-events/index.md) |
| 스토어 앱 설치 목록 | 앱 사용자 모델 ID 가 어떤 앱인지 봅니다 | [스토어 앱 설치 목록](../system-account/appx-staterepository.md) |
| 사용자 프로필 목록 | 하이브가 어느 계정의 것인지 확인합니다 | [사용자 프로필 목록](../system-account/profilelist.md) |

실행 흔적 전체를 엮는 흐름은 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 에, PC 사용 시간을 재구성하는 흐름은 [PC 사용 시간 재구성](../../04-scenarios/activity/system-usage-time.md) 에 있습니다.

## 실습

Windows 10 1903 이후 공개 검체(NIST CFReDS 등)에서 사용자 NTUSER.DAT 를 꺼내 아래 질문을 풀어 봅니다.

1. `FeatureUsage` 키가 있습니까? 없다면 그 계정은 대화형으로 로그온한 적이 있습니까?
2. 어떤 하위 키가 있습니까? TrayButtonClicked 가 있습니까?
3. `KeyCreationTime` 을 직접 UTC 로 바꿔 봅니다. 첫 로그온 이벤트의 시각과 얼마나 차이 납니까?
4. AppSwitched 에서 횟수가 가장 큰 앱은 무엇입니까? 같은 앱이 UserAssist 나 BAM 에도 있습니까?
5. AppLaunch 에 있는 앱은 작업 표시줄에 고정돼 있습니까? 고정 바로 가기가 남아 있습니까?

## 참고 문헌

1. Jai Minton, CrowdStrike 블로그, 2020-05-18, FeatureUsage 로 Windows 10 작업 표시줄 사용을 분석하는 글 (키 위치, 1903 이후 관찰, 하위 키의 정의, 값에 시각이 없다는 점, `KeyCreationTime` 의 뜻과 예시 값, 대화형 로그온이 없으면 키가 없다는 점). https://www.crowdstrike.com/blog/how-to-employ-featureusage-for-windows-10-taskbar-forensics/
