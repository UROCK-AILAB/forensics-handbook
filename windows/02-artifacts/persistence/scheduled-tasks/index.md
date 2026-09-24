# 예약 작업 (Scheduled Tasks)

## 한 줄 요약

예약 작업 (Scheduled Tasks) 은 정해진 때에 프로그램을 자동으로 실행하는 Windows 기능입니다. 작업 하나를 등록하면 XML 파일 하나와 레지스트리 키 두 개가 생깁니다. 이 흔적으로 어떤 프로그램을, 언제, 어느 계정으로 자동 실행하도록 설정했는지 알 수 있습니다.

## 왜 중요한가

- Microsoft 는 악성코드가 재부팅 뒤에도 남으려고 예약 작업을 자주 쓴다고 설명합니다. 그래서 자동실행 흔적을 찾을 때 먼저 보는 곳입니다.
- 흔적이 여러 곳에 나뉘어 남습니다. XML 파일에는 작업 정의가 있습니다. 레지스트리에는 XML 의 해시와 마지막 실행 시각이 있습니다. 한쪽이 지워지거나 바뀌어도 다른 쪽과 맞춰 볼 수 있습니다.
- 작업 생성을 기록하는 보안 로그 4698 과, 작업 등록·실행을 기록하는 TaskScheduler/Operational 로그는 둘 다 기본으로 꺼져 있습니다. 그래서 로그 없이 파일과 레지스트리만으로 판단해야 할 때가 있습니다.
- 목록 도구에서 작업을 감추는 방법이 있습니다. Tarrask 악성코드는 레지스트리의 SD 값을 지워 `schtasks /query` 결과와 작업 스케줄러 화면에서 작업을 감췄습니다.

다만 이 흔적만으로는 알 수 없는 것도 있습니다.

- 작업 정의가 있다고 해서 실제로 실행되었다는 뜻은 아닙니다. 실행 여부는 마지막 실행 시각과 다른 실행 흔적으로 확인합니다.
- 작성자와 등록 일시 칸은 작업을 만든 쪽이 적은 값일 수 있습니다. 등록한 계정은 4698 이벤트에서 찾습니다.
- 로그가 꺼져 있으면 누가, 언제 등록했는지 남지 않을 수 있습니다.

## 한눈에 보기

> 그림 자리: 작업 하나를 등록했을 때 생기는 세 흔적(Tree 키, Tasks 키, XML 파일)과 이들을 잇는 값(Tree 의 Id → Tasks 의 GUID, Tasks 의 Path → XML 파일 경로, Tasks 의 Hash → XML 내용)을 한 장에 보여 주는 그림

### 위치

| 흔적 | 위치 | Windows 버전 | 알려 주는 것 |
|---|---|---|---|
| 작업 정의 XML | `C:\Windows\System32\Tasks\<작업 경로>` (확장자 없음) | Vista · 2008 이후 | 실행할 명령과 인자, 트리거, 실행 계정, 설정 |
| 작업 캐시 Tree | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\<작업 경로>` | Vista 이후 | 작업 경로, Tasks 쪽 GUID(Id), 보안 설명자(SD) |
| 작업 캐시 Tasks | `...\Schedule\TaskCache\Tasks\{GUID}` | Vista 이후 | XML 해시, 동작, 마지막 실행 시각 |
| `.job` 파일 | XP 는 SchedulingAgent 키의 TasksFolder 값부터 봅니다 | 형식 표의 제품 버전 값은 NT 4.0 ~ Windows 10 | 명령, 작성자, 마지막 실행 시각, 상태 |
| XP 레지스트리 | `HKLM\Software\Microsoft\SchedulingAgent` | XP | 작업 폴더·로그 경로로 보이는 값 |
| 이벤트 로그 | 보안 로그 4698, `Microsoft-Windows-TaskScheduler/Operational` | 4698 은 Vista · 2008 이후. 둘 다 기본으로 꺼짐 | 등록한 계정, 작업 XML 전체, 실행 기록 |

### Windows 버전에 따라 달라지는 점

| 구분 | XP 까지 | Vista · 2008 이후 |
|---|---|---|
| 작업 정의 | `.job` 바이너리 파일 | `System32\Tasks` 의 XML 파일 |
| 레지스트리 | `SchedulingAgent` 키 | `Schedule\TaskCache` 키 |
| 작업 생성 감사 이벤트 | 없음 | 보안 로그 4698 (기본 꺼짐) |

### 알려 주는 것

| 알고 싶은 것 | 어디에 남나 | 자세히 |
|---|---|---|
| 무엇을 실행하도록 했나 | XML 의 Actions, Tasks 키의 Actions 값 | [작업 정의 파일](system32-tasks-xml.md) |
| 언제 실행하도록 했나 | XML 의 Triggers | [작업 정의 파일](system32-tasks-xml.md) |
| 어느 계정으로 실행하나 | XML 의 Principals | [작업 정의 파일](system32-tasks-xml.md) |
| 마지막으로 언제 실행했나 | Tasks 키의 DynamicInfo | [작업 캐시 레지스트리](taskcache-tree-tasks.md) |
| XML 이 등록 뒤에 바뀌었나 | Tasks 키의 Hash | [작업 캐시 레지스트리](taskcache-tree-tasks.md) |
| 목록에서 숨긴 작업이 있나 | Tree 키의 SD 값 | [숨긴 예약 작업 찾기](sd.md) |
| 옛 시스템의 작업은 무엇인가 | `.job` 파일 | [옛 작업 파일](job-at.md) |
| 누가 등록했나 | 4698 이벤트 (켜 둔 경우) | [예약 작업 이벤트](../../event-logs/taskscheduler-4698.md) |

## 읽는 순서

1. [작업 정의 파일 (System32\Tasks XML)](system32-tasks-xml.md) — 작업 정의 XML 의 위치와 요소를 읽습니다. 실행할 명령, 트리거, 실행 계정, 등록 일시(Date)를 해석하는 법을 다룹니다.
2. [작업 캐시 레지스트리 (TaskCache Tree·Tasks)](taskcache-tree-tasks.md) — Tree 와 Tasks 키의 값을 읽습니다. XML 해시를 검증하고, DynamicInfo 에서 마지막 실행 시각을 꺼내는 법을 다룹니다.
3. [옛 작업 파일 (.job·at)](job-at.md) — XP 까지 쓰인 `.job` 파일의 구조와 `at` 명령을 다룹니다. 상태 값과 마지막 실행 시각을 읽습니다.
4. [숨긴 예약 작업 찾기 (SD 값 삭제)](sd.md) — SD 값을 지워 목록에서 감춘 작업을 레지스트리로 찾는 절차입니다. XML 의 Hidden 설정과 다른 점도 다룹니다.

## 함께 볼 페이지

- [예약 작업 이벤트 (TaskScheduler·4698)](../../event-logs/taskscheduler-4698.md) — 작업을 등록한 계정, 실행 기록, 작업 XML 전체가 남는 이벤트입니다.
- [악성코드 지속성(자동실행) 찾기](../../../04-scenarios/incident/persistence.md) — 예약 작업을 다른 자동실행 위치와 함께 훑는 순서입니다.
- [로그온 자동실행](../run-runonce-startup-folder.md) · [서비스·드라이버](../services-drivers.md) · [WMI 영구 이벤트 구독](../wmi-event-subscription.md) · [BITS 전송 작업](../bits-jobs-qmgr-db.md) · [기타 자동실행 위치](../winlogon-ifeo-appinit-dlls.md) — 다른 자동실행 흔적입니다.
- [감사 정책과 로그 설정](../../event-logs/audit-policy-log-settings.md) — 4698 과 TaskScheduler 로그가 켜져 있었는지 확인합니다.
- [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) — TaskCache 키를 오프라인 하이브에서 읽는 바탕입니다.
- [자격 증명 관리자와 볼트](../../credentials/credential-manager-windows-vault.md) — 비밀번호를 저장해 실행하는 작업의 자격 증명이 남는 곳입니다.
- [계정 탈취와 측면 이동](../../../04-scenarios/incident/credential-theft-lateral-movement/index.md) — 원격 컴퓨터에 작업을 넣어 명령을 실행한 경우를 다룹니다.
- [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) — 작업을 숨기거나 지운 흔적을 다른 안티포렌식 흔적과 함께 봅니다.
- [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) — 등록 시각, 마지막 실행 시각, 파일 시각을 한 줄로 늘어놓습니다.

## 참고 문헌

- Microsoft Security Blog, "Tarrask malware uses scheduled tasks for defense evasion" (2022-04-12) — https://www.microsoft.com/en-us/security/blog/2022/04/12/tarrask-malware-uses-scheduled-tasks-for-defense-evasion/
- libyal winreg-kb, "Task scheduler" — https://github.com/libyal/winreg-kb/blob/main/docs/sources/system-keys/Task-scheduler.md
- libyal dtformats, "Job file format" — https://github.com/libyal/dtformats/blob/main/documentation/Job%20file%20format.asciidoc
- Microsoft Learn, "4698(S) A scheduled task was created." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4698
- Microsoft Learn, "RegistrationInfo (taskType) Element" — https://learn.microsoft.com/en-us/windows/win32/taskschd/taskschedulerschema-registrationinfo-tasktype-element
