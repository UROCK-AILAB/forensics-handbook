# 예약 작업 이벤트 (TaskScheduler·4698)

## 한 줄 요약

예약 작업 (Scheduled Task) 을 만들거나 바꾸거나 실행하면 이벤트 로그 두 곳에 기록이 남을 수 있습니다. 보안 로그 (Security) 의 4698 에는 작업을 만든 계정과 작업 XML 전체가 남습니다. `Microsoft-Windows-TaskScheduler/Operational` 로그에는 작업 등록·수정·삭제와 실행의 시작·끝이 남습니다. Microsoft 는 두 기록 모두 기본으로 꺼져 있다고 적었습니다. 켜 두지 않았으면 아무것도 남지 않습니다.

## 무엇을 기록하나 · 왜 생기나

두 로그는 서로 다른 것을 남깁니다.

| 로그 | 남는 때 | 알려 주는 것 |
|---|---|---|
| 보안 로그 4698~4702 | 작업을 만들 때, 지울 때, 사용·사용 안 함으로 바꿀 때, 수정할 때 | 요청한 계정과 로그온 ID, 작업 이름, 작업 XML |
| TaskScheduler/Operational | 작업을 등록·수정·삭제할 때, 작업과 동작 (Action) 이 시작하고 끝날 때 | 작업 이름, 사용자 이름, 실행 인스턴스, 반환 코드 |

4698 은 새 예약 작업이 만들어질 때마다 남고, TaskContent 칸에 새 작업의 XML 전체가 들어가며 실행할 명령도 이 XML 안에 있습니다. Operational 로그의 등록 이벤트 106 에는 작업 이름과 사용자만 있고 작업 내용은 없습니다. 그래서 "무엇을 실행하게 했나" 는 4698 에서 찾고, "실제로 실행했나" 는 Operational 로그에서 찾습니다.

작업 정의 파일과 레지스트리에 남는 흔적은 [예약 작업](../persistence/scheduled-tasks/index.md)에서 다룹니다. 이 페이지는 이벤트만 다룹니다.

## 위치와 버전별 차이

### 로그와 켜는 설정

| 항목 | 보안 로그 4698~4702 | TaskScheduler/Operational |
|---|---|---|
| 공급자 (Provider) | Microsoft-Windows-Security-Auditing `{54849625-5478-4994-A5BA-3E3B0328C30D}` | Microsoft-Windows-TaskScheduler |
| 파일 | 보안 로그 파일 | `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-TaskScheduler%4Operational.evtx` |
| 켜는 방법 | 감사 하위 범주 기타 개체 액세스 이벤트 (Audit Other Object Access Events) 를 켭니다 | 로그를 사용하도록 켭니다 |
| 기본 상태 | 꺼짐 | 꺼짐 |

- Microsoft 는 4698 과 TaskScheduler Operational 로그를 두고 "Neither of these are audited by default and must be explicitly turned on by an administrator." 라고 적었습니다. 관리자가 따로 켜야 한다는 뜻입니다. 4698 의 감사 하위 범주는 Other Object Access Events 이고, 4699~4702 의 감사 하위 범주도 같은지는 이번에 확인하지 못했습니다.
- TaskScheduler 공급자는 Operational 말고도 System 로그와 `Microsoft-Windows-TaskScheduler/Debug`·`/Diagnostic`·`/Maintenance` 로그에 씁니다. (확인 범위: Win11 25H2 한 대)

한 PC 에서 설정을 읽어 본 결과는 다음과 같습니다. (확인 범위: Win11 25H2 한 대)

- Operational 로그는 꺼져 있었습니다 (IsEnabled False).
- Operational 로그의 최대 크기는 10,485,760바이트였고, 보관 방식은 순환 (Circular) 이었습니다.
- 위 .evtx 파일은 디스크에 없었습니다.
- 감사 하위 범주 Other Object Access Events `{0CCE9227-69AE-11D9-BED3-505054503030}` 는 감사 안 함 (No Auditing) 이었습니다.
- 보안 로그에 4698 은 0건이었습니다.

감사 설정과 로그 크기를 확인하는 방법은 [감사 정책과 로그 설정](audit-policy-log-settings.md)에서 다룹니다.

### 이벤트 버전

| 이벤트 | 버전 | Windows | 더해진 칸 |
|---|---|---|---|
| 4698 | 0 | Windows Vista · Windows Server 2008 부터 | — |
| 4698 | 1 | Windows 10 1903 부터 | ClientProcessStartKey, ClientProcessId, ParentProcessId, RpcCallClientLocality, FQDN |
| 4699~4702 | 0 · 1 | 매니페스트에 두 버전이 모두 있습니다 (확인 범위: Win11 25H2 한 대) | 버전 1 에 위와 같은 다섯 칸 |

- 4699~4702 의 버전 1 이 어느 Windows 버전부터 쓰였는지는 확인하지 못했습니다.
- Windows XP · 2003 의 작업 기록 파일은 이번에 확인하지 못했습니다. 옛 작업 형식은 [옛 작업 파일 (.job·at)](../persistence/scheduled-tasks/job-at.md)에서 다룹니다.

## 구조

### 4698 칸

| 칸 (XML 이름) | 뜻 | 읽을 때 주의 |
|---|---|---|
| SubjectUserSid · SubjectUserName · SubjectDomainName | 작업을 만든 계정 | 계정입니다. 사람이 아닙니다 |
| SubjectLogonId | 그 계정의 로그온 ID | 4624 의 Logon ID 와 이을 수 있습니다 |
| TaskName | 작업 경로와 이름 | `\task_path\task_name` 꼴입니다. 경로는 작업 스케줄러의 "Task Scheduler Library" 뿌리부터 적습니다 |
| TaskContent | 새 작업의 XML 전체 | 명령, 트리거, 실행 계정 설정이 여기 있습니다 |
| ClientProcessStartKey · ClientProcessId · ParentProcessId · RpcCallClientLocality · FQDN | 버전 1 에만 있는 칸 | 이번에는 칸 이름만 확인했습니다 |

Microsoft 문서의 예시 이벤트 가운데 일부입니다. 문서가 보여 주는 예시이며 검체에서 나온 값이 아닙니다.

```xml
<Provider Name="Microsoft-Windows-Security-Auditing" Guid="{54849625-5478-4994-A5BA-3E3B0328C30D}" />
<EventID>4698</EventID>
<Version>0</Version>
<Task>12804</Task>
<Keywords>0x8020000000000000</Keywords>
<TimeCreated SystemTime="2015-09-23T02:03:06.944522200Z" />
<Channel>Security</Channel>
```

같은 예시의 TaskContent 에서 두 곳을 옮기면 다음과 같습니다.

- RegistrationInfo 의 Date: `2015-09-22T19:03:06.9258653`
- 실행할 동작: `<Exec><Command>C:\Documents\listener.exe</Command></Exec>`

작업 XML 의 각 요소가 무슨 뜻인지는 [작업 정의 파일 (System32\Tasks XML)](../persistence/scheduled-tasks/system32-tasks-xml.md)에서 다룹니다.

### 4699~4702 칸

네 이벤트 모두 Subject 네 칸과 TaskName 이 있습니다. 작업 내용이 들어가는 칸 이름은 이벤트마다 다릅니다. (확인 범위: Win11 25H2 한 대의 매니페스트)

| ID | 메시지 | 작업 내용 칸 |
|---|---|---|
| 4699 | A scheduled task was deleted. (작업 삭제) | TaskContent |
| 4700 | A scheduled task was enabled. (작업 사용) | TaskContent |
| 4701 | A scheduled task was disabled. (작업 사용 안 함) | TaskContent |
| 4702 | A scheduled task was updated. (작업 수정) | TaskContentNew |

- 4702 에는 수정한 뒤의 내용만 있습니다. 수정하기 전 내용은 앞선 4698 이나 4702 에서 찾습니다.
- 4699 에 TaskContent 칸이 있다는 것까지만 확인했습니다. 지운 작업의 XML 이 실제로 들어가는지는 확인하지 못했습니다.

### TaskScheduler/Operational 이벤트

아래 표는 한 PC 의 공급자 매니페스트에서 읽었습니다. (확인 범위: Win11 25H2 한 대)

| ID | 뜻 | 칸 |
|---|---|---|
| 106 | 작업 등록 | TaskName, UserContext |
| 140 | 작업 수정 | TaskName, UserName |
| 141 | 작업 삭제 | TaskName, UserName |
| 142 | 작업 사용 안 함 | TaskName, UserName |
| 100 | 작업 시작 | TaskName, UserContext, InstanceId |
| 107 | 시간 트리거로 실행 | TaskName, InstanceId |
| 108 | 이벤트 트리거로 실행 | TaskName, InstanceId |
| 109 | 등록 트리거로 실행 | TaskName, InstanceId |
| 110 | 사용자가 실행 | TaskName, InstanceId, UserContext |
| 118 | 시스템 시작 때 실행 | TaskName, InstanceId |
| 119 | 로그온 때 실행 | TaskName, UserName, InstanceId |
| 129 | 작업 프로세스를 만듦 | TaskName, Path, ProcessID (UInt32), Priority |
| 200 | 동작 시작 | TaskName, ActionName, TaskInstanceId. 버전 1 에 EnginePID |
| 201 | 동작 완료 | 버전 0 은 TaskName, ActionName, TaskInstanceId. 버전 1 에 ResultCode (반환 코드), 버전 2 에 EnginePID |
| 202 | 동작 완료 실패 (Error) | TaskName, TaskInstanceId, ActionName, ResultCode |
| 203 | 동작 시작 실패 (Error) | TaskName, TaskInstanceId, ActionName, ResultCode |
| 102 | 작업 완료 | TaskName, UserContext, InstanceId |

매니페스트의 메시지 몇 개는 다음과 같습니다.

- 106: `User "%2" registered Task Scheduler task "%1"`
- 129: `Task Scheduler launch task "%1", instance "%2" with process ID %3.`
- 200: `Task Scheduler launched action "%2" in instance "%3" of task "%1".`

읽을 때 다음을 기억합니다.

- 106·140·141 에는 작업 이름과 사용자만 있습니다. 작업 XML 과 명령은 없습니다.
- 200 의 ActionName 에 무엇이 들어가는지는 매니페스트로 알 수 없습니다. 매니페스트는 칸 이름만 알려 줍니다.
- 129 의 Path 칸도 같습니다. 무엇이 들어가는지는 검체에서 확인합니다.
- 201 의 반환 코드는 버전 1 부터 있습니다. 버전 0 기록에서는 성공·실패를 201 로 가릴 수 없습니다.
- 100·102·107~110·118·119 의 InstanceId 와 200~203 의 TaskInstanceId 는 이름으로 보아 같은 실행 인스턴스를 가리킵니다. 같은 값끼리 묶으면 한 번의 실행을 처음부터 끝까지 볼 수 있습니다. 이 방법은 칸 이름에서 나온 해석입니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 기록 시각에 이 이름의 작업이 등록됐고, 요청이 이 계정·로그온 세션에서 왔다는 것 (4698) | 그 계정 뒤에 있던 사람이 누구인지 |
| 등록 당시의 작업 XML: 명령, 트리거, 실행 계정 설정 (4698) | 작업이 실제로 실행됐는지 (4698 만으로는 알 수 없습니다) |
| 수정한 뒤의 작업 XML (4702) | 수정 전 XML (4702 에는 없습니다) |
| 등록한 사용자 이름 (106) | 무엇을 실행하게 했는지 (106 에는 내용이 없습니다) |
| 동작이 시작하고 끝났다는 것, 버전 1 이상이면 반환 코드 (200·201) | 실행한 프로그램이 무슨 일을 했는지 |
| | 로그가 꺼져 있던 기간에 작업이 없었다는 것 |
| | 목록에서 숨긴 작업이 없었다는 것 |

### 보고서 문장

- 쓸 수 있는 문장: "보안 로그에 4698 이 ○○(UTC) 에 있습니다. 작업 이름은 `\○○` 이고, TaskContent 의 Command 는 `○○` 입니다. Subject 는 ○○\○○ 이고 로그온 ID 는 ○○ 입니다."
- 쓰면 안 되는 문장: "사용자 ○○가 악성 프로그램이 자동으로 실행되게 심었다."

두 번째 문장은 기록에 없는 사람과 의도를 적습니다. 로그온 ID 로 세션을 잇고, 실행 기록(200·201)과 파일 흔적을 따로 확인해 적습니다.

## 시각 해석

- 이벤트의 TimeCreated 는 UTC 입니다. Microsoft 예시의 값도 끝에 `Z` 가 붙어 있습니다.
- TaskContent 안의 RegistrationInfo Date 에는 시간대 표시가 없습니다.
- Microsoft 예시에서 Date 는 `2015-09-22T19:03:06` 이고, 같은 이벤트의 TimeCreated 는 `2015-09-23T02:03:06Z` 입니다. 7시간 차이입니다.
- 그래서 Date 는 작업을 만든 컴퓨터의 현지 시각으로 보입니다. 두 값을 비교한 추론이며, Microsoft 문서가 밝힌 내용은 아닙니다.
- 100·107~110·118·119·200 의 시각은 실행이 시작된 때입니다. 102·201 의 시각은 끝난 때입니다.
- 시각 값 저장 형식은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서, 여러 기록의 시각 맞추기는 [시간대·시계 오차 보정](../../03-techniques/analysis/timeline/time-normalization.md)에서 다룹니다.

## 함정과 한계

1. **로그가 없는 것을 작업이 없었다는 뜻으로 읽습니다.** 4698 과 Operational 로그는 기본으로 꺼져 있습니다. 먼저 설정을 확인합니다.
2. **106 에서 명령을 찾습니다.** 106·140·141 에는 작업 이름과 사용자뿐입니다. 명령은 4698 의 TaskContent 나 작업 정의 파일에서 찾습니다.
3. **TaskContent 로만 검색합니다.** 4702 는 칸 이름이 TaskContentNew 입니다. 칸 이름으로 거르면 수정 이벤트가 빠집니다.
4. **129 의 PID 를 4688 과 그대로 맞춥니다.** 129 의 ProcessID 는 10진 정수입니다. 4688 의 PID 는 16진으로 적힙니다([프로세스 생성 (4688)](4688.md)). 진법을 맞춘 뒤 비교합니다.
5. **작업 목록에 없으면 작업이 없다고 봅니다.** Microsoft 가 분석한 Tarrask 는 레지스트리 SD 값을 지워 작업을 목록에서 감췄습니다. 감춘 작업도 트리거대로 계속 실행됩니다. SD 값 삭제만 알려 주는 전용 이벤트 ID 는 확인하지 못했습니다. 이벤트에 나온 작업 이름을 `TaskCache\Tree` 와 대조합니다. 자세한 방법은 [숨긴 예약 작업 찾기 (SD 값 삭제)](../persistence/scheduled-tasks/sd.md)에서 다룹니다.
6. **뿌리에 있는 작업을 흘려봅니다.** Microsoft 는 TaskName 이 `\TASK_NAME` 꼴인 작업, 곧 뿌리에 바로 있는 작업을 살피라고 권합니다. 사람이 손으로 만든 작업과 악성 코드가 만든 작업이 흔히 뿌리에 있다고 적었습니다.
7. **`<LogonType>Password</LogonType>` 를 흘려봅니다.** Microsoft 는 TaskContent 에 이 값이 있으면 경보를 울리라고 권합니다. 이때 작업 실행 계정의 비밀번호가 자격 증명 관리자에 평문 형식 (cleartext format) 으로 저장되고, 관리자 권한으로 꺼낼 수 있다고 적었습니다. 저장 위치는 [자격 증명 관리자와 볼트](../credentials/credential-manager-windows-vault.md)에서 다룹니다.
8. **순환 로그의 앞부분을 끝까지 믿습니다.** 한 PC 에서 Operational 로그는 10,485,760바이트 순환 설정이었습니다. (확인 범위: Win11 25H2 한 대) 크기 한도에 이르면 오래된 기록부터 밀려납니다.
9. **원격 등록을 한 컴퓨터에서만 찾습니다.** 다른 컴퓨터에 작업을 등록하면 실행한 쪽과 대상 쪽에 서로 다른 기록이 남습니다. 아래 "교차 검증" 의 JPCERT/CC 시험 결과를 봅니다.

### 지우기와 조작

- **작업을 지웁니다.** 로그를 켜 두었다면 작업 삭제도 4699 와 141 로 남습니다.
- **로그를 지웁니다.** 보안 로그를 지우면 1102 가, 다른 로그를 지우면 104 가 남습니다. [이벤트 로그 삭제](1102-104.md)를 봅니다.
- **레코드 일부만 남아 있습니다.** 지우거나 덮어쓴 레코드가 파일 안에 남아 있을 수 있습니다. [파일 안에 남은 지운·손상 레코드](../../01-foundations/database-log-formats/evtx-evt-etl/chunk-slack-corrupted-evtx.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

이벤트 칸의 값은 이진 XML 의 치환 값으로 들어 있습니다. 값 종류 번호와 배열 구조는 [이진 XML 해석](../../01-foundations/database-log-formats/evtx-evt-etl/binary-xml-template.md)에서 다룹니다. 여기서는 값 데이터 두 개만 봅니다.

아래 바이트는 설명을 위해 만든 예시입니다. 작업 이름과 PID 는 지어낸 값이며, 검체에서 나온 값이 아닙니다.

**1) 뿌리 작업의 TaskName**

작업 이름이 `\Updater` 라고 하겠습니다. 문자열 값은 UTF-16LE 로 들어 있습니다.

```
5C 00 55 00 70 00 64 00 61 00 74 00 65 00 72 00
\     U     p     d     a     t     e     r
```

1. 맨 앞 `5C 00` 은 역슬래시입니다.
2. 그 뒤로 `5C 00` 이 다시 나오지 않습니다. 그래서 이 작업은 뿌리에 바로 있습니다.
3. 하위 폴더에 있는 작업이면 `5C 00` 이 두 번 이상 나옵니다.

**2) 129 의 ProcessID 와 4688 의 PID**

129 의 ProcessID 는 UInt32 입니다. 값이 6,812 라면 값 데이터는 4바이트입니다.

```
9C 1A 00 00
```

1. 리틀 엔디언으로 읽으면 0x00001A9C 입니다.
2. 0x1A9C 는 10진으로 6,812 입니다.
3. 129 의 메시지 `%3` 자리에는 10진 `6812` 로 보일 것으로 봅니다. 이 표시는 칸 형식에서 나온 추측이며 실제 화면으로 확인하지 않았습니다.
4. 같은 프로세스의 4688 에는 New Process ID 가 `0x1a9c` 로 적힙니다.

> 그림 자리: 129 레코드의 ProcessID 4바이트와, 같은 프로세스의 4688 New Process ID 칸을 나란히 놓고 10진·16진 변환을 보여 주는 그림

### 공개 도구로 한 번

Windows 에 들어 있는 이벤트 뷰어와 PowerShell 의 `Get-WinEvent` 로 볼 수 있습니다. 분석 PC 로 옮긴 파일은 `Path` 로 엽니다. 아래 `E:\case\` 는 예시 경로입니다.

```powershell
# 보안 로그의 작업 이벤트
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\Security.evtx'; Id = 4698, 4699, 4700, 4701, 4702 }

# Operational 로그의 등록·수정·삭제·동작 이벤트
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\Microsoft-Windows-TaskScheduler%4Operational.evtx'; Id = 106, 140, 141, 200, 201 }

# 4698 하나에서 TaskName 과 TaskContent 꺼내기
$e = Get-WinEvent -FilterHashtable @{ Path = 'E:\case\Security.evtx'; Id = 4698 } -MaxEvents 1
([xml]$e.ToXml()).Event.EventData.Data | Where-Object { $_.Name -in 'TaskName', 'TaskContent' }
```

칸 구성은 공급자 매니페스트에서 확인할 수 있습니다.

```powershell
(Get-WinEvent -ListProvider Microsoft-Windows-TaskScheduler).Events |
  Where-Object Id -eq 201 | Select-Object Id, Version, Template
```

이 명령은 분석 PC 의 매니페스트를 읽습니다. 검체의 Windows 버전과 분석 PC 의 버전이 다르면 칸 구성이 다를 수 있습니다. 라이브 시스템의 감사 설정은 `auditpol /get /subcategory:{0CCE9227-69AE-11D9-BED3-505054503030} /r` 로 확인합니다.

도구가 TaskContent 를 한 줄로 줄이거나 잘라 보여 주는지 확인합니다. 레코드 한두 개는 XML 원문과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [작업 정의 파일 (System32\Tasks XML)](../persistence/scheduled-tasks/system32-tasks-xml.md) | 4698 의 TaskContent 와 지금 남은 XML 파일이 같은지. 다르면 4702 를 찾습니다 |
| [작업 캐시 레지스트리 (TaskCache Tree·Tasks)](../persistence/scheduled-tasks/taskcache-tree-tasks.md) | 이벤트의 작업 이름이 Tree 아래에 있는지 |
| [숨긴 예약 작업 찾기 (SD 값 삭제)](../persistence/scheduled-tasks/sd.md) | 이벤트에는 있는데 작업 목록에 안 보이는 작업 |
| [프로세스 생성 (4688)](4688.md) · [Sysmon 프로세스 생성 (이벤트 1)](sysmon/1.md) | 129 의 PID 로 실제 실행된 프로세스와 명령줄 |
| [로그온 세션 잇기](logon-events/logon-id-4624-4634-4647.md) | 4698 의 SubjectLogonId 와 같은 로그온 ID 의 4624 |
| [명시적 자격 증명·특수 권한 (4648·4672)](logon-events/4648-4672.md) | 원격 등록 때 실행한 쪽과 대상 쪽의 인증 기록 |
| [프리페치](../execution/prefetch/index.md) | 작업 등록 도구와 작업이 띄운 프로그램의 실행 흔적 |

### 원격 등록 시험 결과 (JPCERT/CC)

JPCERT/CC 는 `schtasks` 로 다른 컴퓨터에 작업을 등록하는 시험을 하고 남은 기록을 표로 정리했습니다. 시험한 OS 는 결과표 요약에 드러나지 않습니다. `taskeng.exe` 가 나오므로 Windows 7 무렵의 옛 버전으로 보입니다. 이 판단은 추론입니다. 보고서에 인용할 때는 원문 표를 직접 확인합니다.

| 쪽 | 남은 기록 |
|---|---|
| 실행한 쪽 | Sysmon 1 (`schtasks.exe /Create /S [대상] ...` 명령줄) |
| 실행한 쪽 | 보안 4688 (Mandatory Label Medium), 4648, 5156, 4689 (Exit Status 0x0) |
| 실행한 쪽 | Sysmon 3 (대상의 135번 포트와 높은 번호 포트), Sysmon 5 |
| 실행한 쪽 | 프리페치 `SCHTASKS.EXE-[해시].pf` |
| 대상 쪽 | 보안 4624 (Logon Type 3), 4672, 4688 |
| 대상 쪽 | Sysmon 1 (`taskeng.exe {작업 GUID}`), Sysmon 13 (DynamicInfo 값 설정) |
| 대상 쪽 | 레지스트리 `TaskCache\Tasks\{GUID}`, `TaskCache\Tree\[작업 이름]` |
| 대상 쪽 | 프리페치 `TASKENG.EXE-[해시].pf` |

JPCERT/CC 가 실행 성공을 판단한 기준은 다음과 같습니다.

- 실행한 쪽: 4689 의 반환 값이 0x0 입니다.
- 대상 쪽: TaskScheduler 106 이 있고, 200·201 에 성공 반환 값이 있습니다.

## 실습

**직접 만든 Windows 10·11 가상 머신**에서 해 봅니다. 각 단계의 시각을 적어 둡니다.

1. 로그를 켜기 전에 `Microsoft-Windows-TaskScheduler%4Operational.evtx` 파일이 있는지 봅니다.
2. `auditpol /set /subcategory:{0CCE9227-69AE-11D9-BED3-505054503030} /success:enable` 로 감사를 켭니다. `wevtutil sl Microsoft-Windows-TaskScheduler/Operational /e:true` 로 Operational 로그를 켭니다.
3. `schtasks` 로 뿌리에 작업을 하나 만듭니다. 4698 의 TaskContent 와 `System32\Tasks` 의 XML 파일을 비교합니다. 106 과 4698 의 시각도 비교합니다.
4. 작업을 바로 실행합니다. 110·129·200·201·102 가 어떤 순서로 남는지 봅니다. 200 의 ActionName 과 129 의 Path 에 무엇이 들어가는지 적습니다. 이 페이지가 확인하지 못한 두 가지입니다.
5. 4688 도 켜 두었다면 129 의 ProcessID 를 16진으로 바꿔 4688 과 맞춥니다.
6. 작업을 수정하고, 사용 안 함으로 바꾸고, 지웁니다. 4702·4701·4699 와 140·142·141 이 짝을 지어 남는지 봅니다. 4699 의 TaskContent 에 무엇이 들어가는지도 봅니다.
7. 4699~4702 가 어느 감사 하위 범주를 켰을 때 남는지 확인합니다.

**NIST CFReDS 같은 공개 검체**에서는 다음을 풀어 봅니다.

1. 보안 로그에 4698 이 있습니까? 없다면 감사 설정이 꺼져 있었는지부터 확인합니다.
2. Operational 로그가 있다면 106 의 작업 이름 목록을 뽑고, `TaskCache\Tree` 의 작업 목록과 비교합니다. 한쪽에만 있는 이름은 무엇입니까?
3. 뿌리에 바로 있는 작업이 있습니까? 있다면 그 작업의 동작과 실행 기록을 찾습니다.

## 참고 문헌

- Microsoft Learn, "4698(S) A scheduled task was created." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4698
- Microsoft Learn, "4688(S) A new process has been created." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4688
- Microsoft Security Blog, "Tarrask malware uses scheduled tasks for defense evasion" (2022-04-12) — https://www.microsoft.com/en-us/security/blog/2022/04/12/tarrask-malware-uses-scheduled-tasks-for-defense-evasion/
- JPCERT/CC, Tool Analysis Result Sheet, "schtasks" — https://jpcertcc.github.io/ToolAnalysisResultSheet/details/schtasks.htm
