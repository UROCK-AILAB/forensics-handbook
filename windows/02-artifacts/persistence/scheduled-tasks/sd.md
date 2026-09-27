---
title: "숨긴 예약 작업 찾기"
parent: "예약 작업"
grand_parent: "아티팩트 · 자동실행·지속성"
nav_order: 750
---

# 숨긴 예약 작업 찾기 (SD 값 삭제)

레지스트리 `TaskCache\Tree\<작업 경로>` 키에서 SD 값을 지우면, 그 작업이 `schtasks /query` 결과와 작업 스케줄러 화면에서 사라집니다. 사라진 작업은 그 뒤에도 트리거대로 계속 실행됩니다. Tree 아래에서 Id 값은 있는데 SD 값이 없는 키를 찾으면 이렇게 숨긴 작업을 찾을 수 있습니다.

## 무엇이 일어나나

Tarrask 악성코드가 쓴 숨김 방식은 다음과 같습니다[1].

1. 작업을 만들면 `TaskCache\Tree\<작업 이름>` 키와 `TaskCache\Tasks\{GUID}` 키가 생깁니다. Tree 쪽 키에는 Id·Index·SD 값이 있습니다.
2. Tree 쪽 키에서 SD 값을 지웁니다.
3. 그러면 작업이 `schtasks /query` 결과와 작업 스케줄러 화면에서 사라집니다.
4. 작업은 숨긴 뒤에도 트리거대로 실행됩니다. 시스템을 재부팅하거나, 그 작업을 실행하는 `svchost.exe` 프로세스가 끝날 때까지 그렇습니다.

실행 중인 시스템에서 SD 값을 지우려면 SYSTEM 권한이 있어야 합니다. 관리자 권한 명령 프롬프트에서 지우려 해도 "Access Denied" 가 납니다[1]. 그래서 실행 중인 시스템에서 이 방식으로 숨겼다면, 숨긴 쪽은 이미 SYSTEM 권한을 얻은 상태였습니다. 하이브를 오프라인으로 고친 경우는 이와 따로 따져 봅니다.

재부팅한 뒤에 숨긴 작업이 다시 실행되는지, Tarrask 가 `System32\Tasks` 의 XML 파일도 지웠는지는 실제 기기에서 확인해야 합니다.

예약 작업을 기록하는 이벤트 로그(보안 로그 4698, TaskScheduler/Operational)는 둘 다 기본으로 꺼져 있습니다. 그래서 이런 작업의 흔적은 레지스트리와 파일에만 남을 수 있습니다. 로그 설정은 [감사 정책과 로그 설정](../../event-logs/audit-policy-log-settings.md)에서 확인합니다.

## 위치

| 항목 | 내용 |
|---|---|
| 볼 키 | SOFTWARE 하이브 `Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\<작업 경로>` |
| 숨긴 작업의 모습 | Id 값은 있고 SD 값은 없습니다 |
| 이어서 볼 키 | `TaskCache\Tasks\{Id 의 GUID}` |
| 이어서 볼 파일 | `C:\Windows\System32\Tasks\<작업 경로>` |

Tree 키의 값과 SD 값의 구조는 [작업 캐시 레지스트리 (TaskCache Tree·Tasks)](taskcache-tree-tasks.md)에서 다룹니다.

## Hidden 설정과 다른 점

XML 의 `Settings\Hidden` 도 작업을 화면에서 가립니다. 하지만 두 방식은 다릅니다.

| 구분 | XML 의 Hidden = true | Tree 의 SD 값 삭제 |
|---|---|---|
| 바꾸는 곳 | XML 작업 정의 | 레지스트리 Tree 키 |
| 화면에서 | 기본으로 보이지 않습니다. 관리자가 숨긴 작업을 모두 보이게 하는 스위치로 다시 볼 수 있습니다 | `schtasks /query` 결과와 작업 스케줄러 화면에서 사라집니다 |
| 정상 작업도 쓰나 | 씁니다. 업데이트 작업 가운데에도 Hidden 이 true 인 것이 있습니다 | 정상 PC 에서는 보통 없습니다 (아래 절차 3) |

그래서 Hidden 이 true 인 작업만 보고 숨김 기법이라고 판단하지 않습니다. Hidden 요소는 [작업 정의 파일 (System32\Tasks XML)](system32-tasks-xml.md)에서 다룹니다.

## 찾는 절차

1. **SOFTWARE 하이브와 `System32\Tasks` 폴더를 수집합니다.** 숨긴 작업은 `schtasks /query` 와 작업 스케줄러 화면에 나오지 않습니다. 그래서 목록 도구보다 레지스트리를 직접 읽습니다.
2. **Tree 아래 키를 모두 살펴보고, Id 값이 있는 키만 고릅니다.** 폴더에 해당하는 키에는 Id 가 없고 SD 만 있습니다.
3. **그중 SD 값이 없는 키를 적습니다.** 정상 PC 에서는 Id 가 있는 Tree 키에 모두 SD 값이 있습니다. 예를 들어 Id 가 있는 키 306개 가운데 SD 없는 키가 0개인 식입니다.
4. **Id 의 GUID 로 `Tasks\{GUID}` 키를 찾습니다.** Path, Actions, DynamicInfo 를 읽습니다. Actions 에는 실행 대상 문자열이, DynamicInfo 오프셋 12 에는 마지막 실행 시각(UTC)이 있습니다. 읽는 법은 [작업 캐시 레지스트리](taskcache-tree-tasks.md)를 봅니다.
5. **Path 로 XML 파일을 찾습니다.** 파일이 있으면 Command, Arguments, Triggers 를 읽습니다. 레지스트리 Hash 와 파일 해시가 같은지도 봅니다.
6. **목록과 대조합니다.** `TaskCache\Tasks` 의 작업 경로 목록을 `schtasks /query`·`Get-ScheduledTask` 결과와 맞춰 봅니다. 숨긴 작업이 없으면 두 목록의 개수가 같습니다(예: Tasks 하위 키 269개, Get-ScheduledTask 결과 269개). 레지스트리에만 있는 작업이 있으면 그 작업부터 봅니다.
7. **로그를 켜 두었다면 이벤트를 찾습니다.** 작업 이름으로 [예약 작업 이벤트](../../event-logs/taskscheduler-4698.md)를 검색합니다.

SD 를 지운 작업이 사라지는 곳으로 알려진 것은 `schtasks /query` 결과와 작업 스케줄러 화면입니다[1]. `Get-ScheduledTask` 가 이런 작업을 보여 주는지는 알려져 있지 않습니다. 그래서 6단계는 보조 수단으로 쓰고, 3단계의 레지스트리 검사를 기준으로 삼습니다. SD 값이 없는 작업을 레지스트리에서 찾아보는 방법은 탐지 권고로도 나와 있습니다[1].

## 증거로서 의미

**증명하는 것**

- Id 가 있고 SD 가 없는 Tree 키는 Tarrask 의 숨김 방식과 같은 모습입니다[1]. 정상 PC 에는 이런 키가 보통 없습니다.
- 실행 중인 시스템에서 이 방식으로 숨긴 것이라면, 숨긴 쪽은 SYSTEM 권한으로 레지스트리를 고쳤습니다. 오프라인으로 하이브를 고친 경우는 따로 따져 봅니다.
- `Tasks\{GUID}` 가 남아 있으면 숨긴 작업에 설정한 실행 대상과 마지막 실행 시각을 읽을 수 있습니다.

**증명하지 못하는 것**

- SD 값을 언제 지웠는지는 알 수 없습니다. Tree 키의 마지막 기록 시각으로 추정할 수 있는지도 알려져 있지 않습니다.
- 누가 지웠는지는 레지스트리에 남지 않습니다.
- 지금도 작업이 실행되고 있는지는 알 수 없습니다. 재부팅 뒤에 다시 실행되는지도 알려져 있지 않습니다.
- SD 가 빠진 이유가 숨김 기법 하나뿐이라고 단정하지 못합니다.

보고서에는 "`Tree\<작업 경로>` 키에 Id 값은 있으나 SD 값이 없다. 이 상태는 `schtasks /query` 와 작업 스케줄러 화면에 작업이 나오지 않게 하는 방식으로 Microsoft 가 설명한 모습과 같다." 처럼 씁니다.

## 시각 해석

- 숨긴 뒤에도 작업은 트리거대로 실행됩니다. 그래서 작업이 실행한 프로그램의 흔적은 숨긴 시점 뒤에도 이어질 수 있습니다.
- 마지막 실행 시각은 `Tasks\{GUID}` 의 DynamicInfo 오프셋 12 에 UTC 로 남습니다.
- SD 를 지운 시각은 따로 남지 않습니다. 키의 마지막 기록 시각을 이 용도로 쓸 수 있는지는 알려져 있지 않습니다.

## 함정과 한계

- **Index 0 은 숨김 표시가 아닐 수 있습니다.** Index 가 0 인 Tree 키는 없어진 작업이 남긴 키일 수 있고, 이런 키에도 SD 값은 있습니다(예: 한 시스템에서 37개). "Index 0 이면 숨긴 작업" 이라는 주장이 있지만, 이것만으로 숨김을 판단하지 않습니다.
- **Hidden = true 는 흔합니다.** 정상 작업도 이 설정을 씁니다.
- **실행 중인 시스템의 목록 도구를 믿지 않습니다.** 숨긴 작업은 `schtasks /query` 와 작업 스케줄러 화면에 나오지 않습니다.
- **개수만 비교하지 않습니다.** Tree 키에는 폴더 키와 없어진 작업의 키가 섞여 있습니다. GUID 와 작업 경로로 하나씩 맞춰 봅니다.
- **로그가 없는 것이 보통입니다.** 4698 과 TaskScheduler/Operational 은 기본으로 꺼져 있습니다. 로그가 없다는 사실만으로 작업이 없었다고 보지 않습니다.
- **XML 파일이 남아 있는지는 사례마다 확인합니다.** Tarrask 가 XML 도 지웠는지는 공개 자료에 나와 있지 않습니다.

## 직접 분석해 보기

### 레지스트리 값으로 한 번

아래는 명세와 관찰을 바탕으로 만든 예시입니다. 실제 기기에서 나온 키가 아닙니다.

| Tree 아래 키 | Id | SD | 판단 |
|---|---|---|---|
| `Microsoft\Windows` | 없음 | 있음 | 폴더 키입니다 |
| `Microsoft\Windows\ExampleMaintenance` | `{GUID-A}` | 있음 (REG_BINARY 148바이트) | 보통 작업입니다 |
| `ExampleUpdater` | `{GUID-B}` | 없음 | 숨긴 작업일 수 있습니다. `Tasks\{GUID-B}` 를 봅니다 |

세 번째 키는 작업 경로가 루트(`\ExampleUpdater`)이기도 합니다. 루트에 있는 작업을 눈여겨보는 이유는 [작업 정의 파일](system32-tasks-xml.md)의 "증거로서 의미" 를 봅니다.

### 공개 도구로 한 번

Windows 에 들어 있는 PowerShell 로 검사할 수 있습니다. 아래 코드는 Id 가 있고 SD 가 없는 Tree 키를 찾습니다. 관리자 권한으로 실행합니다.

```powershell
$tree = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree'
Get-ChildItem $tree -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
  $p = Get-ItemProperty $_.PSPath
  if ($p.Id -and -not $p.SD) { '{0}  {1}' -f $_.Name, $p.Id }
}
```

수집한 하이브를 검사할 때는 사본을 분석용 PC 에 불러와 같은 코드를 씁니다. 하이브를 불러오면 파일이 바뀔 수 있으므로 원본에는 하지 않습니다.

```powershell
reg load HKLM\CASE_SOFT "<수집한 SOFTWARE 하이브 사본>"
$tree = 'HKLM:\CASE_SOFT\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree'
# 위와 같은 검사를 실행한 뒤
reg unload HKLM\CASE_SOFT
```

실행 중인 시스템에서는 레지스트리의 작업 경로와 `Get-ScheduledTask` 결과를 맞춰 볼 수도 있습니다. `<=` 표시가 붙은 줄은 레지스트리에만 있는 작업입니다.

```powershell
$tc  = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache'
$reg = Get-ChildItem "$tc\Tasks" | ForEach-Object { (Get-ItemProperty $_.PSPath).Path }
$api = Get-ScheduledTask | ForEach-Object { $_.TaskPath + $_.TaskName }
Compare-Object $reg $api
```

실행 중인 시스템은 이미 공격자 손에 있을 수 있습니다. 결과가 깨끗해도 수집한 하이브로 한 번 더 확인합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 작업 캐시 레지스트리 | 숨긴 작업의 경로, 실행 대상, 마지막 실행 시각 | [작업 캐시 레지스트리](taskcache-tree-tasks.md) |
| 작업 정의 XML | 실행할 명령, 트리거, 실행 계정 | [작업 정의 파일](system32-tasks-xml.md) |
| 예약 작업 이벤트 | 작업을 만든 계정과 XML 전체 (켜 둔 경우) | [예약 작업 이벤트](../../event-logs/taskscheduler-4698.md) |
| 프로세스 생성 · Sysmon | 작업이 실행한 프로그램이 숨긴 뒤에도 돌았는지 (켜 둔 경우) | [프로세스 생성 (4688)](../../event-logs/4688.md), [Sysmon 로그](../../event-logs/sysmon/index.md) |
| 메모리 | 아직 실행 중인 작업 프로세스 | [메모리 분석](../../../03-techniques/analysis/memory-forensics/index.md) |
| 섀도 복사본 | 예전 SOFTWARE 하이브에서 SD 값이 있던 모습 | [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

## 실습

공개 시험 이미지(NIST CFReDS 등)의 SOFTWARE 하이브로 아래 질문을 풀어 봅니다.

1. Tree 아래에서 Id 가 있는 키는 몇 개입니까? 그중 SD 값이 없는 키가 있습니까?
2. SD 값이 없는 키가 있다면, Id 의 GUID 로 찾은 `Tasks\{GUID}` 의 Path 와 Actions 는 무엇입니까?
3. 그 작업의 XML 파일이 `System32\Tasks` 에 남아 있습니까?
4. Index 가 0 인 Tree 키가 있습니까? 그 키에는 SD 값이 있습니까? GUID 가 Tasks 에 있습니까?
5. Hidden 이 true 인 작업은 몇 개입니까? 그 작업들의 Tree 키에는 SD 값이 있습니까?

## 참고 문헌

1. Microsoft Security Blog, "Tarrask malware uses scheduled tasks for defense evasion" (2022-04-12). https://www.microsoft.com/en-us/security/blog/2022/04/12/tarrask-malware-uses-scheduled-tasks-for-defense-evasion/
2. Microsoft Learn, "Hidden (settingsType) Element". https://learn.microsoft.com/en-us/windows/win32/taskschd/taskschedulerschema-hidden-settingstype-element
