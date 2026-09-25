---
title: "로그온 자동실행"
parent: "아티팩트 · 자동실행·지속성"
nav_order: 690
---

# 로그온 자동실행 (Run·RunOnce·Startup Folder)

## 한 줄 요약

Run·RunOnce 키와 시작프로그램 폴더 (Startup Folder) 는 사용자가 로그온할 때 프로그램을 실행하게 하는 자리입니다. Run 은 로그온할 때마다 실행하고, RunOnce 는 한 번 실행한 뒤 값을 지웁니다. 값이 있다는 것은 등록되어 있다는 뜻이고, 실행됐다는 증거는 아닙니다.

## 무엇을 기록하나 · 왜 생기나

Run 키와 RunOnce 키는 사용자가 로그온할 때 프로그램을 실행하게 하며, 사용자별(HKCU)과 컴퓨터 전체(HKLM)에 한 벌씩 있습니다. 값 하나가 명령 하나이고, 값 이름은 설명 문자열이며 값 데이터는 260자 이하의 명령줄입니다. 한 키에 값을 여러 개 둘 수 있지만 이때 실행 순서는 정해져 있지 않습니다. 시스템은 Run 키 프로그램을 언제 실행할지 보장하지 않으며, 사용자가 쓰는 화면을 방해하지 않도록 Run 키와 시작프로그램 그룹의 실행을 늦출 수 있습니다.

- 정상 프로그램도 이 자리를 씁니다. Windows 11 PC 한 대의 HKCU Run 키에는 값이 6개 있었습니다.
- 악성코드도 Run 키와 시작프로그램 폴더를 자동실행 수단으로 씁니다. 이 수단은 MITRE ATT&CK 의 T1547.001 에 해당합니다[2].

## 위치와 버전별 차이

### Run·RunOnce 키

기본 키는 네 개입니다[1].

| 경로 | 범위 | 실행 |
|---|---|---|
| `HKLM\Software\Microsoft\Windows\CurrentVersion\Run` | 컴퓨터 전체 | 로그온할 때마다 |
| `HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce` | 컴퓨터 전체 | 한 번 |
| `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` | 그 사용자 | 로그온할 때마다 |
| `HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce` | 그 사용자 | 한 번 |

- HKLM 과 HKCU 가 각각 어느 하이브 파일인지는 [하이브 파일 종류](../../01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md) 에서 다룹니다.
- 64비트 Windows 11 PC 한 대에서는 32비트 프로그램이 등록한 항목이 `HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run` 에 있었습니다. 이 경로를 빼먹으면 그 항목을 놓칩니다.

### 그 밖의 Run 계열 키

아래 자리도 같은 기법에 쓰입니다[2].

| 경로 | 비고 |
|---|---|
| `HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnceEx` | Vista 이후에는 기본으로 만들어지지 않습니다 |
| `HKLM·HKCU\Software\Microsoft\Windows\CurrentVersion\RunServices` | 실제로 동작하는 Windows 버전은 검체에서 확인합니다 |
| `HKLM·HKCU\Software\Microsoft\Windows\CurrentVersion\RunServicesOnce` | 위와 같습니다 |
| `HKLM·HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run` | |

`Load` 값과 `BootExecute` 값은 [기타 자동실행 위치](winlogon-ifeo-appinit-dlls.md) 에서 다룹니다.

같은 PC 에서 본 상태는 이렇습니다.

| 키 | 상태 |
|---|---|
| HKLM Run | 값 1개 |
| HKLM RunOnce | 값 2개 |
| WOW6432Node Run | 값 2개 |
| WOW6432Node RunOnce | 값 0개 |
| HKCU Run | 값 6개 |
| HKCU RunOnce | 값 0개 |
| RunOnceEx, Policies\Explorer\Run(HKLM·HKCU), RunServices·RunServicesOnce(HKLM) | 키가 없었습니다 |

### 시작프로그램 폴더

| 범위 | 경로 |
|---|---|
| 사용자별 | `C:\Users\[사용자]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup` |
| 모든 사용자 | `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp` |

- 폴더 위치는 `HKCU·HKLM\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders` 와 같은 경로의 `Shell Folders` 값이 정하므로, 기본 경로만 보지 말고 이 값이 가리키는 폴더를 봅니다.
- Windows 11 PC 한 대에서 본 값은 아래와 같습니다.

| 키 | 값 이름 | 데이터 |
|---|---|---|
| HKCU ...\User Shell Folders | `Startup` | `%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup` (REG_EXPAND_SZ, 환경 변수를 펼치지 않은 원문) |
| HKLM ...\User Shell Folders | `Common Startup` | `%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup` |
| HKLM ...\Shell Folders | `Common Startup` | `C:\ProgramData\...\Startup` (펼친 경로) |

- 같은 PC 의 두 시작프로그램 폴더에는 모두 desktop.ini(174바이트)가 들어 있었습니다. 이 파일만 있는 것은 정상 모습입니다.

### 작업 관리자 "시작 앱" 사용 여부 (StartupApproved)

이 키를 설명한 공식 문서가 없어 검체에서 확인해야 합니다. 아래는 모두 Windows 11 PC 한 대에서 본 모습입니다.

- 위치는 `HKLM·HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved` 입니다.
- 그 아래에 `Run`, `Run32`, `StartupFolder` 하위 키가 있었습니다.
- HKCU 쪽에는 `Run32` 가 없었고, `StartupFolder` 에는 값이 없었습니다.
- `Run32` 의 값 이름은 WOW6432Node Run 의 값 이름과 맞았습니다(2개 중 2개).

## 구조

### Run·RunOnce 값

```
Run
    <설명 이름>    REG_SZ 또는 REG_EXPAND_SZ    <명령줄>
```

- Windows 11 PC 한 대에서 HKLM Run 의 값 1개는 REG_EXPAND_SZ 였고, 나머지 Run 값은 REG_SZ 였습니다. 두 형식이 섞입니다.
- REG_EXPAND_SZ 는 `%...%` 환경 변수를 펼치지 않은 채 저장합니다. 실제 경로는 그 계정의 환경 변수로 펼쳐서 확인합니다.

### RunOnce 값 이름의 접두사

| 값 이름 | 동작 |
|---|---|
| 접두사 없음 | 명령을 실행하기 **전에** 값을 지웁니다. 실행이 실패해도 다음 부팅 때 다시 실행하지 않습니다 |
| `!` 로 시작 | 명령을 실행한 **뒤에** 값을 지웁니다 |
| `*` 로 시작 | 안전 모드에서도 실행합니다 |

- 안전 모드에서는 이 키들을 기본으로 무시합니다.
- HKLM RunOnce 는 재부팅 뒤 Administrators 그룹 구성원이 로그온할 때만 실행됩니다.

### StartupApproved 값

아래는 Windows 11 PC 한 대에서 본 형태입니다.

```
StartupApproved\Run
    <Run 키의 값 이름>    REG_BINARY    12바이트
```

| 바이트 | 내용 |
|---|---|
| 0–3 | 플래그로 보이는 값. 01·02·03·04·07 이 나왔습니다 |
| 4–11 | 02·04 항목은 모두 0이었습니다. 01·03·07 항목은 FILETIME 으로 읽혔고, UTC 로 읽으면 2026년 6~8월 사이의 그럴듯한 시각이었습니다 |

- 값 이름은 Run 키의 값 이름과 같았습니다. `StartupFolder` 쪽은 폴더 속 파일 이름으로 추정합니다.
- "02 = 사용, 03 = 사용 안 함, FILETIME = 사용 안 함으로 바꾼 시각" 이라는 해석이 널리 쓰이지만 공식 문서는 없습니다. 01·07 의 뜻도 공개 자료가 없습니다.

## 증거로서 의미

### 증명하는 것

- 수집 시점에 이 키에 이 이름으로 이 명령줄이 등록되어 있었습니다.
- HKCU 쪽 값이면 그 사용자 하이브에 등록되어 있었습니다. 그 계정이 로그온할 때 실행 대상이 됩니다.
- 시작프로그램 폴더에 파일이 있으면, 수집 시점에 그 파일이 로그온 때 실행될 자리에 있었습니다.
- StartupApproved 에는 지금 Run 키에 없는 이름도 남아 있었습니다(HKLM Run 쪽 2개, HKCU Run 쪽 1개). Run 값을 지워도 이 항목은 남을 수 있습니다. 그 이름으로 등록된 항목이 예전에 있었다는 실마리가 됩니다.

### 증명하지 못하는 것

- **실행됐나.** 등록되어 있다는 것만 알려 줍니다. 실행은 [프리페치](../execution/prefetch/index.md), [AmCache](../execution/amcache-hve/index.md), [프로세스 생성](../event-logs/4688.md), [Sysmon 이벤트 1](../event-logs/sysmon/1.md) 로 따로 확인합니다.
- **언제 등록했나.** 값 하나하나의 시각은 없습니다. 키 단위 시각은 아래 "시각 해석" 을 봅니다.
- **등록된 적이 없나.** RunOnce 는 실행되면 값이 사라집니다. 그래서 사후 분석 때 값이 없다고 해서 등록된 적이 없다는 뜻은 아닙니다.
- **누가 등록했나.** 값에는 등록한 프로세스를 적는 칸이 없습니다. 레지스트리를 바꾼 프로세스는 [Sysmon 레지스트리 이벤트](../event-logs/sysmon/12-13-14.md) 가 켜져 있었을 때만 찾을 수 있습니다.
- **StartupApproved 플래그의 뜻.** 공식 문서가 없습니다. "사용자가 시작 앱을 껐다" 고 단정하지 않습니다.

보고서에는 "수집 시점에 HKCU Run 키에 이 이름으로 이 명령줄이 등록되어 있다" 처럼 씁니다. 실행을 말하려면 "같은 경로의 실행 기록이 프리페치에 있다" 처럼 근거를 따로 적습니다.

## 시각 해석

- Run 값에는 값마다 붙은 시각이 없습니다. 키 단위 시각이 무엇이 바뀔 때 바뀌는지는 [키 마지막 기록 시각](../../01-foundations/database-log-formats/registry-hive/last-write-time.md) 에서 다룹니다.
- 키 시각은 키 안의 어느 값이 바뀌었는지 말하지 않습니다. 값이 여러 개인 키에서는 그 시각을 특정 값의 등록 시각으로 쓰지 않습니다.
- 시작프로그램 폴더의 파일은 파일 시스템 시각으로 언제 놓였는지 짐작합니다. 시각 속성은 [마스터 파일 테이블](../filesystem/mft.md) 에서 다룹니다.
- StartupApproved 뒤 8바이트의 FILETIME 이 무엇의 시각인지는 공식 문서가 없습니다. 시각 형식은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- 시스템은 Run 키 프로그램의 실행을 늦출 수 있습니다. 로그온 시각과 프로그램 실행 시각 사이에 틈이 있어도 이상하지 않습니다.

## 함정과 한계

- **WOW6432Node 를 빼먹습니다.** 64비트 Windows 에서 32비트 프로그램의 항목은 그 아래에 있었습니다.
- **HKCU 는 사용자마다 따로 있습니다.** 로그온한 적 있는 모든 프로필의 사용자 하이브를 수집합니다. 프로필 목록은 [사용자 프로필 목록](../system-account/profilelist.md) 에서 봅니다.
- **RunOnce 는 흔적을 스스로 지웁니다.** 이전 시점 하이브를 [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에서 꺼내 비교합니다. 지운 값이 하이브 안에 남는지는 [지운 키·값 복구](../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md) 에서 다룹니다.
- **폴더 위치가 바뀔 수 있습니다.** `User Shell Folders` 값이 가리키는 폴더를 확인합니다.
- **REG_EXPAND_SZ 는 펼치지 않은 원문입니다.** 환경 변수를 펼친 경로로 파일을 찾습니다.
- **정상 항목이 많습니다.** 같은 조직의 다른 PC 나 설치 직후 상태와 비교하면 새 항목이 드러납니다. 명령줄이 표준이 아닌 폴더의 실행 파일이나 스크립트를 가리키면 먼저 봅니다.
- **안전 모드에서는 동작이 다릅니다.** 기본으로 무시하고, `*` 로 시작하는 RunOnce 값만 실행합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 값 형식에 맞춰 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다.

**REG_EXPAND_SZ 명령줄의 앞부분 (`%ProgramData%`).**

```
25 00 50 00 72 00 6F 00 67 00 72 00 61 00 6D 00   %.P.r.o.g.r.a.m.
44 00 61 00 74 00 61 00 25 00                     D.a.t.a.%.
```

1. 문자열은 UTF-16LE 입니다. 한 글자가 2바이트입니다.
2. `25 00` 은 '%' 입니다. 환경 변수가 펼쳐지지 않은 채 저장되어 있습니다.
3. 인코딩은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.

**StartupApproved 값 12바이트.**

```
03 00 00 00 00 1C D8 81 3C 14 DD 01
```

1. 앞 4바이트 `03 00 00 00` 을 리틀 엔디언으로 읽으면 3 입니다.
2. 뒤 8바이트 `00 1C D8 81 3C 14 DD 01` 을 리틀 엔디언으로 읽으면 0x01DD143C81D81C00 입니다.
3. 이 수를 FILETIME 으로 풀면 2026-07-15 09:30:00 UTC 입니다.
4. 앞 4바이트의 뜻과 이 시각의 뜻은 공식 문서가 없습니다. 읽는 법만 보여 주는 예시입니다.

### 공개 도구로 한 번

1. HKLM 쪽 하이브와 사용자마다의 사용자 하이브를 하이브 로그와 함께 사본으로 뜹니다.
2. 레지스트리 뷰어로 네 키, WOW6432Node 아래 Run·RunOnce, 그 밖의 Run 계열 키를 차례로 엽니다.
3. 같은 뷰어로 `Explorer\StartupApproved` 를 열어 Run 키의 값 이름과 맞춰 봅니다. 한쪽에만 있는 이름을 따로 적습니다.
4. `User Shell Folders` 값이 가리키는 시작프로그램 폴더의 파일 목록과 파일 시각을 뽑습니다.
5. 켜진 PC 에서는 `reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 처럼 읽기만 하는 명령으로 같은 값을 볼 수 있습니다.
6. 명령줄이 가리키는 파일이 아직 있는지 확인하고, 있으면 서명을 봅니다. 방법은 [의심 실행 파일 선별](../../03-techniques/analysis/code-signing-yara.md) 에 있습니다.
7. 도구 결과의 한 줄을 골라 위 풀이대로 값 데이터를 직접 한 번 읽어 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| Sysmon 12·13·14 | Run 키 값을 만들거나 바꾼 프로세스와 시각 | [레지스트리 변경](../event-logs/sysmon/12-13-14.md) |
| 프리페치 | 명령줄이 가리키는 프로그램의 실행 횟수와 시각 | [프리페치](../execution/prefetch/index.md) |
| AmCache | 같은 경로의 실행 파일 기록 | [AmCache](../execution/amcache-hve/index.md) |
| 4688·Sysmon 1 | 로그온 뒤 그 명령이 프로세스로 만들어졌나, 부모 프로세스는 무엇인가 | [프로세스 생성](../event-logs/4688.md), [Sysmon 이벤트 1](../event-logs/sysmon/1.md) |
| 로그온 이벤트 | 그 계정이 언제 로그온했나 | [로그온·로그오프](../event-logs/logon-events/index.md) |
| 서비스·예약 작업 | 같은 파일이 다른 자동실행 자리에도 등록되어 있나 | [서비스·드라이버](services-drivers.md), [예약 작업](scheduled-tasks/index.md) |

탐지할 때는 Run·Startup 키에 새롭거나 이상한 실행 경로·스크립트가 생기는 변경을 보고, 표준이 아닌 폴더에서의 실행이나 이상한 부모-자식 프로세스와 엮어 봅니다[2]. 자동실행 위치 전체를 훑는 흐름은 [악성코드 지속성(자동실행) 찾기](../../04-scenarios/incident/persistence.md) 에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)에서 레지스트리 하이브와 사용자 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. HKLM·HKCU 의 Run·RunOnce 키, WOW6432Node 아래 키에 값이 각각 몇 개입니까?
2. 명령줄이 `%...%` 로 시작하는 값이 있습니까? 펼치면 어느 경로입니까?
3. StartupApproved 에만 있고 지금 Run 키에는 없는 이름이 있습니까? 그 이름을 다른 아티팩트에서 찾을 수 있습니까?
4. 시작프로그램 폴더에 desktop.ini 말고 다른 파일이 있습니까? 그 파일은 언제 놓였습니까?
5. Run 값 하나를 골라 그 프로그램의 실행 흔적을 프리페치에서 찾아봅니다. 실행 시각이 로그온 시각과 어떻게 이어집니까?

## 참고 문헌

1. Microsoft Learn, *Run and RunOnce Registry Keys* (ms.date 2024-07-19). 네 키 경로, 값 형식과 260자 제한, 실행 순서·시점, RunOnce 의 `!`·`*` 접두사와 안전 모드, HKLM RunOnce 실행 조건. https://learn.microsoft.com/en-us/windows/win32/setupapi/run-and-runonce-registry-keys
2. MITRE ATT&CK, *Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder (T1547.001)* (v19, 2026-05-12 수정). 추가 키, 시작프로그램 폴더 경로, User Shell Folders·Shell Folders, 탐지 권고. https://attack.mitre.org/techniques/T1547/001/
