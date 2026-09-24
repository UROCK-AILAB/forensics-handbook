# WMI 영구 이벤트 구독 (WMI Event Subscription)

## 한 줄 요약

WMI 영구 이벤트 구독은 필터·소비자·바인딩 세 객체로 이루어집니다. 등록을 지울 때까지 조건이 맞을 때마다 정한 동작을 하고, 그 동작에는 스크립트 실행과 프로그램 실행도 들어갑니다. 구독은 레지스트리가 아니라 WMI 저장소 파일에 남습니다.

## 무엇을 기록하나 · 왜 생기나

- 영구 이벤트 소비자 (permanent event consumer) 는 등록을 명시적으로 지울 때까지 이벤트를 받습니다.
- 구독은 세 객체로 이루어집니다.
  - 필터: 이벤트 쿼리를 담은 `__EventFilter` 인스턴스입니다.
  - 논리 소비자: 할 일을 정한 소비자 클래스 인스턴스입니다.
  - 바인딩: 둘을 잇는 `__FilterToConsumerBinding` 인스턴스입니다.
- 필터 하나를 여러 소비자에, 소비자 하나를 여러 필터에 묶을 수 있습니다.
- WMI 는 영구 소비자를 보통 시작할 때나 이벤트가 생길 때처럼 필요할 때 메모리에 올리며, 등록한 프로그램이 계속 떠 있을 필요는 없습니다.
- 세 객체는 `CreatorSID` 속성의 SID 가 같아야 합니다.
- 필터의 `EventNamespace` 속성으로 다른 네임스페이스의 이벤트를 받을 수 있습니다. 레지스트리 이벤트(`RegistryTreeChangeEvent` 등)는 `root\default` 에서만 발생합니다.
- 소비자가 스크립트나 프로그램을 실행할 수 있으므로 자동실행 위치로 점검하는데, 이 문장은 아래 표준 소비자의 동작에서 끌어낸 해석입니다.

## 위치와 버전별 차이

### 저장소 파일

아래는 Windows 11 PC 한 대에서 본 모습입니다. (확인 범위: Win11 25H2 한 대)

구독은 WMI 저장소 (repository) 에 저장되며, 저장소 폴더는 `C:\Windows\System32\wbem\Repository` 였습니다. 이 폴더는 `HKLM\SOFTWARE\Microsoft\Wbem\CIMOM` 의 `Repository Directory` 값(`C:\WINDOWS\system32\wbem\repository`)에 적혀 있었습니다.

| 파일 | 크기 |
|---|---|
| OBJECTS.DATA | 약 44MB |
| INDEX.BTR | 약 7.6MB |
| MAPPING1.MAP·MAPPING2.MAP·MAPPING3.MAP | 각 140,336바이트 |

### 표준 소비자의 네임스페이스

표준 소비자 클래스가 컴파일되는 기본 네임스페이스는 OS 마다 다르며, Microsoft 문서는 "Windows Server 2003 에서는 모두 `Root\Subscription`" 이라는 예만 듭니다. Windows 11 PC 한 대에서는 `root\subscription` 에 표준 소비자 5개 클래스가 모두 있었습니다. `root\cimv2` 에는 `__EventConsumer` 파생 클래스가 없었습니다. (확인 범위: Win11 25H2 한 대)

### 이벤트 로그

- 로그 이름은 `Microsoft-Windows-WMI-Activity/Operational` 입니다.
- 파일은 `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-WMI-Activity%4Operational.evtx` 였습니다. (확인 범위: Win11 25H2 한 대)

## 구조

### 세 객체의 속성

아래 속성은 Windows 11 PC 한 대에서 클래스 정의를 읽어 확인했습니다. (확인 범위: Win11 25H2 한 대)

| 클래스 | 속성 | 분석 때 볼 칸 |
|---|---|---|
| `__EventFilter` | CreatorSID, EventAccess, EventNamespace, Name, Query, QueryLanguage | Query, EventNamespace |
| `__FilterToConsumerBinding` | Consumer, CreatorSID, DeliverSynchronously, DeliveryQoS, Filter, MaintainSecurityContext, SlowDownProviders | Filter, Consumer(두 객체의 경로) |
| `ActiveScriptEventConsumer` | CreatorSID, MachineName, MaximumQueueSize, KillTimeout, Name, ScriptFilename, ScriptingEngine, ScriptText | ScriptText, ScriptFilename |
| `CommandLineEventConsumer` | CommandLineTemplate, ExecutablePath, WorkingDirectory, RunInteractively, ShowWindowCommand 등 26개(CreatorSID·Name 포함) | CommandLineTemplate, ExecutablePath |

"분석 때 볼 칸" 은 속성의 쓰임새에서 고른 해석입니다.

### 표준 소비자 5종

| 클래스 | 이벤트를 받으면 |
|---|---|
| `ActiveScriptEventConsumer` | 스크립트를 실행합니다 |
| `CommandLineEventConsumer` | 프로세스를 실행합니다. 실행 파일을 안전한 위치에 두거나 강한 ACL 로 보호하라는 주의가 문서에 붙어 있습니다 |
| `LogFileEventConsumer` | 텍스트 로그 파일에 문자열을 씁니다 |
| `NTEventLogEventConsumer` | Application 이벤트 로그에 메시지를 씁니다 |
| `SMTPEventConsumer` | SMTP 로 메일을 보냅니다 |

- 소비자가 어느 계정 권한으로 도는지, 스크립트를 돌리는 호스트 프로세스가 무엇인지는 이번에 연 자료로 확인하지 못했습니다.

### 한 PC 에 있던 구독

Windows 11 PC 한 대의 `root\subscription` 에는 구독이 딱 한 벌 있었습니다. (확인 범위: Win11 25H2 한 대)

| 객체 | 내용 |
|---|---|
| `__EventFilter` | Name "SCM Event Log Filter", QueryLanguage WQL, EventNamespace `root\cimv2`, Query `select * from MSFT_SCMEventLogEvent` |
| `NTEventLogEventConsumer` | Name "SCM Event Log Consumer" |
| `__FilterToConsumerBinding` | 위 둘을 잇습니다 |

- 필터의 `CreatorSID` 는 S-1-5-32-544(Administrators) 였습니다.
- 이 한 벌이 Windows 기본 설치에 들어 있는 정상 구독인지는 확인하지 못했고 PC 한 대에서 본 것뿐입니다. 다른 검체에서 같은 구독을 보면 오탐일 수 있으니 이 표와 맞춰 봅니다.

### 실패 기록

- 영구 소비자의 쿼리가 실패하면 NT 이벤트 로그에 원본 WinMgmt, 이벤트 ID 10, 유형 Error 가 남습니다.
- 소비자가 실패하면 WMI 가 `__ConsumerFailureEvent` 를 냅니다.
- 이벤트가 버려지면 WMI 가 `__EventDroppedEvent` 를 냅니다.

## 증거로서 의미

### 증명하는 것

- 수집 시점에 저장소에 이 필터·소비자·바인딩이 있었습니다.
- 필터의 Query 로 어떤 조건에 반응하도록 했는지 알 수 있습니다.
- 소비자의 ScriptText·ScriptFilename·CommandLineTemplate·ExecutablePath 로 무엇을 하도록 했는지 알 수 있습니다.
- `CreatorSID` 는 등록에 쓰인 계정을 좁히는 실마리가 됩니다. 이 문장은 속성 이름에서 끌어낸 해석입니다.

### 증명하지 못하는 것

- **동작했나.** 구독이 있다는 것만 알려 줍니다. 소비자가 실제로 실행한 프로그램은 [프로세스 생성](../event-logs/4688.md) 이나 [Sysmon 이벤트 1](../event-logs/sysmon/1.md) 에서 따로 찾습니다.
- **언제 만들었나.** 저장소 파일 안에 객체별 생성 시각이 있는지 확인하지 못했습니다.
- **바인딩이 없는 필터나 소비자가 동작하나.** 바인딩이 필터와 소비자를 잇습니다. 바인딩 없이 남은 객체만으로 동작했다고 보지 않습니다. 이 문장은 구성 방식에서 끌어낸 해석입니다.
- **지운 구독이 있었나.** 지운 구독을 OBJECTS.DATA 에서 찾을 수 있는지 확인하지 못했습니다.

보고서에는 "수집 시점에 `root\subscription` 에 이 Query 의 필터와 이 명령줄의 `CommandLineEventConsumer` 가 바인딩으로 묶여 있다" 처럼 씁니다.

## 시각 해석

- 객체별 시각을 확인하지 못했으므로 쓸 수 있는 시각은 저장소 파일의 파일 시스템 시각뿐일 수 있는데, 이 문장은 해석입니다. 파일 시각은 [마스터 파일 테이블](../filesystem/mft.md) 에서 다룹니다.
- Windows 11 PC 한 대에서 세 MAPPING 파일의 마지막 수정 시각이 서로 달랐습니다. 가장 최근 것이 INDEX.BTR·OBJECTS.DATA 와 같은 시각이었습니다. (확인 범위: Win11 25H2 한 대)
- 파일 시각은 저장소 전체가 마지막으로 바뀐 때를 말할 뿐, 어느 객체가 바뀌었는지 말하지 않습니다.
- WMI-Activity/Operational 로그의 이벤트는 아래와 같습니다. 칸 이름은 Windows 11 PC 한 대의 공급자 메시지에서 읽었습니다. (확인 범위: Win11 25H2 한 대)

| 이벤트 | 칸 |
|---|---|
| 5857 | 공급자 시작. ProviderPath, HostProcess, ProcessID |
| 5858 | 오류. ClientMachine, User, ClientProcessId, Operation, ResultCode |
| 5859 | Namespace, NotificationQuery, OwnerName, HostProcessID, Provider, queryID |
| 5860 | Namespace, NotificationQuery, UserName, ClientProcessID, ClientMachine |
| 5861 | "Namespace = %1; Eventfilter = %2 (refer to its activate eventid:5859); Consumer = %3; PossibleCause = %4" |

- 5861 은 필터와 소비자를 함께 적으며, 영구 구독이 등록될 때 남는 이벤트로 쓰입니다. 다만 "등록할 때 발생한다" 는 공식 설명은 확인하지 못했습니다.
- 이 로그 전반은 [원격 명령 실행 이벤트](../event-logs/winrm-wmi-activity.md) 에서 다룹니다.
- Sysmon 은 이벤트 19·20·21(WmiEvent) 로 필터·소비자·바인딩을 기록합니다. [Sysmon 로그](../event-logs/sysmon/index.md) 를 봅니다.

## 함정과 한계

- **로그가 금방 밀려납니다.** Windows 11 PC 한 대에서 이 로그는 최대 1,052,672바이트(약 1MB)였고 순환 방식이었습니다. 기록 1,143건이 약 9시간 치뿐이었습니다(5858 1,068건, 5857 75건). 5861 은 0건이었습니다. (확인 범위: Win11 25H2 한 대)
- 그래서 구독이 오래전에 만들어졌다면 로그보다 저장소를 봅니다.
- **레지스트리 자동실행 점검만으로는 찾지 못합니다.** 구독은 저장소 파일에 있습니다.
- **정상 구독도 있습니다.** 위 "한 PC 에 있던 구독" 과 같은 한 벌을 악성으로 단정하지 않습니다.
- **네임스페이스는 한 곳만 보지 않습니다.** 표준 소비자의 기본 네임스페이스가 OS 마다 다르고, 필터는 `EventNamespace` 로 다른 네임스페이스를 가리킬 수 있습니다. 이 문장은 위 사실에서 끌어낸 해석입니다.
- **저장소 내부 구조는 이 글에서 다루지 않습니다.** OBJECTS.DATA 의 페이지 크기와 매핑 방식은 확인하지 못했습니다. 오프라인 분석 결과는 켜진 PC 에서 읽은 결과나 다른 도구와 맞춰 봅니다.
- **호스트 프로세스로 잡는 탐지는 따로 확인합니다.** 소비자를 실행하는 프로세스와 계정을 이번 자료로 확인하지 못했습니다.

## 직접 분석해 보기

### 헥스로 한 번

저장소 파일의 구조는 확인하지 못했습니다. 그래서 구조를 따라가는 헥스 풀이는 싣지 않습니다. 아래는 클래스 이름을 문자열로 찾을 때 쓸 바이트 모양입니다. 인코딩 규칙으로 만든 예시이며, 특정 검체에서 꺼낸 값이 아닙니다.

**`CommandLine` 의 ASCII 바이트.**

```
43 6F 6D 6D 61 6E 64 4C 69 6E 65                  CommandLine
```

**같은 글자의 UTF-16LE 바이트.**

```
43 00 6F 00 6D 00 6D 00 61 00 6E 00 64 00 4C 00   C.o.m.m.a.n.d.L.
69 00 6E 00 65 00                                 i.n.e.
```

1. OBJECTS.DATA 안에서 이 이름이 어느 인코딩으로 저장되는지는 확인하지 못했습니다. 두 모양을 모두 찾습니다.
2. 찾은 문자열이 살아 있는 구독인지, 지운 구독의 잔재인지는 구조를 풀지 않고는 가릴 수 없습니다.
3. 문자열 검색으로 나온 결과는 "이 문자열이 파일 안에 있다" 까지만 씁니다.

### 공개 도구로 한 번

1. 켜진 PC 에서 PowerShell 로 세 객체를 읽습니다. 읽기만 하는 명령입니다.
   - `Get-CimInstance -Namespace root\subscription -ClassName __EventFilter`
   - `Get-CimInstance -Namespace root\subscription -ClassName __EventConsumer`
   - `Get-CimInstance -Namespace root\subscription -ClassName __FilterToConsumerBinding`
2. 바인딩의 Filter·Consumer 경로로 필터와 소비자를 짝지어 한 줄씩 적습니다.
3. 소비자의 ScriptText·CommandLineTemplate·ExecutablePath 를 따로 뽑습니다.
4. 위 "한 PC 에 있던 구독" 과 같은 한 벌은 따로 표시합니다.
5. 오프라인 이미지에서는 저장소 폴더의 파일을 모두 함께 사본으로 뜹니다. 여러 파일이 한 저장소를 이루기 때문입니다.
6. WMI-Activity/Operational 로그에서 5859·5860·5861 을 뽑아 필터 이름과 맞춰 봅니다. 로그 형식은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| WMI-Activity 로그 | 구독 등록과 쿼리 활동의 흔적 | [원격 명령 실행 이벤트](../event-logs/winrm-wmi-activity.md) |
| Sysmon 19·20·21 | 필터·소비자·바인딩을 만든 기록 | [Sysmon 로그](../event-logs/sysmon/index.md) |
| 4688·Sysmon 1 | 소비자가 실행한 프로세스 | [프로세스 생성](../event-logs/4688.md), [Sysmon 이벤트 1](../event-logs/sysmon/1.md) |
| 프리페치 | 소비자가 가리킨 프로그램의 실행 흔적 | [프리페치](../execution/prefetch/index.md) |
| 예약 작업 | 같은 명령이 다른 자동실행 자리에도 있나 | [예약 작업](scheduled-tasks/index.md) |

원격에서 WMI 로 명령을 실행한 흐름은 [PsExec·WMI·WinRM](../../04-scenarios/incident/credential-theft-lateral-movement/psexec-wmi-winrm.md) 에, 자동실행 위치 전체를 훑는 흐름은 [악성코드 지속성(자동실행) 찾기](../../04-scenarios/incident/persistence.md) 에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)에서 WMI 저장소 폴더와 이벤트 로그를 꺼내 아래 질문을 풀어 봅니다.

1. 저장소 폴더에 어떤 파일이 있습니까? 파일마다 마지막 수정 시각은 언제입니까?
2. 저장소에서 `CommandLineEventConsumer`·`ActiveScriptEventConsumer` 문자열을 찾아봅니다. 몇 군데에서 나옵니까?
3. WMI-Activity/Operational 로그는 며칠 치를 담고 있습니까? 5861 이 있습니까?
4. 5861 이 있다면 적힌 필터 이름과 소비자 이름은 무엇입니까? 5859 에서 같은 필터를 찾을 수 있습니까?
5. 구독 하나를 골라 소비자가 가리킨 프로그램의 실행 흔적을 찾아봅니다. "구독이 이 프로그램을 실행했다" 고 쓸 수 있습니까?

## 참고 문헌

1. Microsoft Learn, *Receiving Events at All Times* (ms.date 2018-05-31). 영구 소비자의 수명, 필터·소비자·바인딩 구성, 필요할 때 메모리에 올리는 방식, WinMgmt 이벤트 ID 10. https://learn.microsoft.com/en-us/windows/win32/wmisdk/receiving-events-at-all-times
2. Microsoft Learn, *Monitoring and Responding to Events with Standard Consumers* (ms.date 2018-05-31). 표준 소비자 5종, 기본 네임스페이스, CreatorSID 일치 조건, EventNamespace 와 root\default, 실패 이벤트. https://learn.microsoft.com/en-us/windows/win32/wmisdk/monitoring-and-responding-to-events-with-standard-consumers
