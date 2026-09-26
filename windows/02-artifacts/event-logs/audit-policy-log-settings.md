---
title: "감사 정책과 로그 설정"
parent: "아티팩트 · 이벤트 로그"
nav_order: 2470
---

# 감사 정책과 로그 설정 (Audit Policy·Log Settings)

## 한 줄 요약

보안 로그 (Security) 에 무엇을 남길지는 감사 정책 (Audit Policy) 이 정하고, 로그마다 최대 크기와 덮어쓰기 방식도 정해져 있어서 크기 한도에 이르면 오래된 기록부터 밀려납니다. 그래서 어떤 이벤트가 없을 때는 "그 일이 없었다" 고 읽기 전에 이 두 설정부터 확인합니다.

## 무엇을 기록하나 · 왜 생기나

이 페이지는 이벤트 하나가 아니라 다른 이벤트가 남을지 말지를 정하는 설정을 다룹니다.

| 설정 | 정하는 것 | 확인하는 곳 |
|---|---|---|
| 감사 정책 | 보안 로그에 어떤 하위 범주 (Subcategory) 의 성공·실패를 남길지 | 라이브 시스템의 `auditpol`, 정책이 바뀔 때 남는 4719 등 |
| 로그 설정 | 로그 파일 위치, 최대 크기, 가득 찼을 때 덮어쓸지 | 레지스트리 `Services\Eventlog`·`WINEVT\Channels` |

감사 정책에서 꺼진 하위 범주의 이벤트는 처음부터 기록하지 않습니다. 그래서 이벤트가 없다는 사실은 "일이 없었다" 가 아니라 "기록하지 않았다" 일 수 있습니다. 로그가 가득 차면 기본 설정에서는 오래된 기록을 덮어씁니다.

## 위치와 버전별 차이

### Windows 클라이언트의 기본 감사 정책

Windows 기본값은 Microsoft 의 "Recommended System Audit Policy by operating system" 표에 있습니다[1]. 표는 Windows Client 와 Windows Server 두 개이고, 칸은 Windows Default·Baseline Recommendation·Stronger Recommendation 세 가지이며, 칸마다 성공 (Success) 과 실패 (Failure) 를 나눠 적습니다.

아래는 Windows Client 표의 Windows Default 칸에 값이 적힌 하위 범주입니다.

| 하위 범주 | 성공 | 실패 |
|---|---|---|
| Audit Credential Validation | No | No |
| Audit User Account Management | Yes | No |
| Audit Account Lockout | Yes | No |
| Audit Logoff | Yes | No |
| Audit Logon | Yes | Yes |
| Audit Network Policy Server | Yes | Yes |
| Audit Special Logon | Yes | No |
| Audit Audit Policy Change | Yes | No |
| Audit Authentication Policy Change | Yes | No |
| Audit Other System Events | Yes | Yes |
| Audit Security State Change | Yes | No |
| Audit System Integrity | Yes | Yes |

Audit Credential Validation 은 표에 "No" 라고 적혀 있으며, 칸이 빈 것과 다릅니다. 나머지 하위 범주는 기본값 칸이 비어 있으며, 기본으로 켜 있지 않다고 읽습니다. 다만 칸이 빈 하위 범주가 켜져 있는 PC 도 있습니다(아래 예의 보안 그룹 관리). 칸이 빈 하위 범주의 예: Audit Process Creation, Audit Security System Extension, Audit File Share, Audit File System, Audit Registry, Audit Other Logon/Logoff Events, Audit Kerberos Authentication Service, Audit Removable Storage. Audit Process Creation 을 켜야 [프로세스 생성 (4688)](4688.md) 이 남고, Audit Security System Extension 을 켜야 [서비스 설치 (7045·4697)](7045-4697.md) 의 4697 이 남습니다.

버전에 따라 다른 값이 하나 있습니다.

| Windows 버전 | Audit Logon 기본값 |
|---|---|
| Windows 10 1809 전 | 성공만 |
| Windows 10 1809 부터 | 성공·실패 둘 다 |

로그온 이벤트 자체는 [로그온·로그오프](logon-events/index.md)에서 다룹니다.

### 실제 감사 정책의 예

아래는 Windows 11 빌드 26200 (한국어 화면) PC 의 `auditpol /get /category:*` 결과입니다.

하위 범주는 60개이고, Microsoft 표와 다른 값은 하나입니다. 보안 그룹 관리 (Security Group Management) 가 "성공" 으로 켜져 있으며, Microsoft 표에서는 이 칸이 비어 있습니다. 그룹 구성원·플러그 앤 플레이 이벤트·토큰 권한 조정 이벤트·액세스 권한, 이 네 하위 범주는 Microsoft 표에 없고, 이 PC 에서는 넷 다 "감사 없음" 입니다. 꺼져 있는 하위 범주 가운데 포렌식에서 자주 찾는 것은 다음과 같습니다: 프로세스 만들기, 보안 시스템 확장, 파일 공유, 세부 파일 공유, 파일 시스템, 레지스트리, 기타 로그온/로그오프 이벤트, 필터링 플랫폼 연결, 자격 증명 유효성 검사, Kerberos 인증 서비스.

이미지에서는 아래 "구조" 의 Task 값으로 보안 로그에 실제로 남은 하위 범주를 세어 보는 방법을 씁니다.

### 로그 설정이 저장되는 곳

| 로그 종류 | 설정 키 |
|---|---|
| 클래식 로그 (Application·Security·System 등) | `HKLM\SYSTEM\CurrentControlSet\Services\Eventlog\<로그 이름>`[3] |
| 그 밖의 채널 (`Microsoft-Windows-…/Operational` 등) | `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WINEVT\Channels\<채널 이름>` |

`WINEVT\Channels\Security` 키는 없을 수 있고, 이때 보안 로그 설정은 `Services\Eventlog\Security` 에만 있습니다. 이미지에서는 `CurrentControlSet` 이 없으며, 실제로 쓰인 컨트롤셋 번호를 골라 읽습니다. 고르는 방법은 [컨트롤셋 고르기 (ControlSet·Select)](../../01-foundations/database-log-formats/registry-hive/controlset-select.md)에서 다룹니다.

`Services\Eventlog\<로그 이름>` 키의 값은 다음과 같습니다[3].

| 값 | 형식 | 뜻 |
|---|---|---|
| File | REG_SZ 또는 REG_EXPAND_SZ | 로그 파일 전체 경로. 값이 없으면 `%SystemRoot%\system32\winevt\logs\` 아래에 키 이름을 딴 파일을 씁니다 |
| MaxSize | REG_DWORD | 최대 크기 (바이트). System·Application·Security 는 64K 배수여야 합니다. 기본값은 1MB 입니다 |
| Retention | REG_DWORD | 기본 0. 0 이면 항상 덮어씁니다. 0xFFFFFFFF 이거나 0 이 아니면 덮어쓰지 않습니다. 이때 로그가 가득 차면 새 이벤트를 버립니다 |
| AutoBackupLogFiles | REG_DWORD | 기본 0 (자동 백업 안 함). Retention 이 -1 (0xFFFFFFFF) 일 때만 자동 백업합니다 |
| CustomSD | 문자열 (SDDL) | 로그 접근 권한 |
| Isolation | — | 기본 권한 묶음 (Application·System·Custom) |

DisplayNameFile·DisplayNameID·PrimaryModule·Sources·RestrictGuestAccess 는 쓰지 않는 값입니다[3].

실제 값의 예 (위와 같은 Windows 11 빌드 26200 PC) 는 다음과 같습니다.

| 로그 | File | MaxSize | Retention | 그 밖의 값 |
|---|---|---|---|---|
| Security | `C:\WINDOWS\System32\winevt\Logs\Security.evtx` | 20971520 | 0 | Isolation 2, RestrictGuestAccess 1, Security (REG_BINARY) |
| System | — | 20971520 | 0 | — |
| Application | — | 20971520 | 0 | AutoBackupLogFiles 0 |

세 로그의 MaxSize 는 20MB 로, 문서의 기본값 1MB 와 다릅니다[3]. `wevtutil gl Security` 결과도 같습니다: retention false, autoBackup false, maxSize 20971520, logFileName `%SystemRoot%\System32\Winevt\Logs\Security.evtx`. `WINEVT\Channels\Microsoft-Windows-PowerShell/Operational` 키에는 OwningPublisher `{a0c1853b-…}`, Enabled 1, MaxSize 15728640, MaxSizeUpper 0, Retention 0, Type 1, ChannelAccess (SDDL) 값이 있습니다.

### 채널별 크기와 켜짐의 예

같은 PC 의 `Get-WinEvent -ListLog` 결과입니다.

| 채널 | 켜짐 | 최대 크기 |
|---|---|---|
| Security · System · Application | 켜짐 | 20MB, 순환 (Circular) |
| Microsoft-Windows-PowerShell/Operational · Windows PowerShell | 켜짐 | 15MB |
| Microsoft-Windows-Windows Defender/Operational | 켜짐 | 16MB |
| WinRM · WMI-Activity · TerminalServices-LocalSessionManager · RemoteConnectionManager · RDPClient · Bits-Client · Shell-Core · CodeIntegrity · WLAN-AutoConfig 의 Operational, 그리고 Setup | 켜짐 | 1MB (1052672) |
| Microsoft-Windows-TaskScheduler/Operational | 꺼짐 | 10MB 로 잡혀 있음 |
| Microsoft-Windows-DriverFrameworks-UserMode/Operational · DNS-Client/Operational | 꺼짐 | — |
| Microsoft-Windows-Sysmon/Operational | 없음 (설치 안 됨) | — |

채널은 466개이고 그중 387개가 켜져 있으며, 덮어쓰기 방식은 463개가 순환 (Circular), 3개가 보존 (Retain) 입니다. 채널 설정은 PC 마다 다를 수 있어 실제 기기에서 확인합니다.

## 구조

### 하위 범주 GUID

`auditpol` 은 하위 범주 이름을 화면 언어로 보여 줍니다. 한국어 PC 에서는 "프로세스 만들기" 처럼 나옵니다. 하위 범주 GUID 는 언어와 상관없습니다.

| 하위 범주 | GUID |
|---|---|
| 보안 상태 변경 (Security State Change) | `{0CCE9210-69AE-11D9-BED3-505054503030}` |
| 보안 시스템 확장 (Security System Extension) | `{0CCE9211-69AE-11D9-BED3-505054503030}` |
| 로그온 (Logon) | `{0CCE9215-69AE-11D9-BED3-505054503030}` |
| 프로세스 만들기 (Process Creation) | `{0CCE922B-69AE-11D9-BED3-505054503030}` |
| 감사 정책 변경 (Audit Policy Change) | `{0CCE922F-69AE-11D9-BED3-505054503030}` |
| 보안 그룹 관리 (Security Group Management) | `{0CCE9237-69AE-11D9-BED3-505054503030}` |

GUID 뒷부분은 모두 `-69AE-11D9-BED3-505054503030` 입니다.

### 이벤트의 Task 값은 하위 범주 번호

보안 로그 이벤트의 Task 필드에는 하위 범주 번호가 들어 있습니다. 공급자 메타데이터의 Task 표와 실제 이벤트를 맞춰 보면 다음과 같습니다.

| Task | 하위 범주 | 이벤트 예 |
|---|---|---|
| 12288 | Security State Change | 4616 |
| 12289 | Security System Extension | — |
| 12290 | System Integrity | — |
| 12292 | Other System Events | — |
| 12544 | Logon | 4624 |
| 12545 | Logoff | — |
| 12548 | Special Logon | 4672 |
| 13312 | Process Creation | — |
| 13568 | Audit Policy Change | — |
| 13569 | Authentication Policy Change | — |
| 13824 | (메타데이터 표에 이름 없음) | 4798 |

그래서 이미지의 보안 로그를 Task 값으로 묶어 세면, 그 PC 에서 어떤 하위 범주가 실제로 기록을 남기고 있었는지 추정할 수 있습니다.

### 감사 설정이 바뀔 때 남는 이벤트

아래 메시지와 필드는 공급자 메타데이터에 있는 값입니다.

| ID | 메시지 | 필드 |
|---|---|---|
| 4719 | System audit policy was changed. | SubjectUserSid, SubjectUserName, SubjectDomainName, SubjectLogonId, CategoryId, SubcategoryId, SubcategoryGuid, AuditPolicyChanges. 버전 1 에 ClientProcessId, ClientProcessStartKey |
| 4912 | Per User Audit Policy was changed. | Subject 필드 네 개, TargetUserSid, CategoryId, SubcategoryId, SubcategoryGuid, AuditPolicyChanges |
| 4902 | The Per-user audit policy table was created. | PuaCount, PuaPolicyId |
| 4906 | The CrashOnAuditFail value has changed. | CrashOnAuditFailValue |
| 4715 | The audit policy (SACL) on an object was changed. | Subject 필드 네 개, OldSd, NewSd |
| 4907 | Auditing settings on object were changed. | Subject 필드 네 개, ObjectServer, ObjectType, ObjectName, HandleId, OldSd, NewSd, ProcessId, ProcessName |

로그 자체의 상태를 알리는 이벤트도 있습니다.

| ID | 채널 | 메시지 | 필드 |
|---|---|---|---|
| 1100 | Security | The event logging service has shut down. | — |
| 1104 | Security | The security log is now full. | — |
| 1105 | Security | Event log automatic backup | Channel, BackupPath |
| 105 | System | 1105 와 같은 자동 백업 메시지 | — |

로그를 지울 때 남는 1102 (보안 로그)·104 (다른 로그) 는 [이벤트 로그 삭제 (1102·104)](1102-104.md)에서 다룹니다. 보안 로그에 약 이틀 치만 남은 PC 에서는 4719·4902·1100·1102 가 한 건도 없을 수 있습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 조사한 때 어떤 하위 범주가 켜져 있었는지 (`auditpol`) | 사건 당시에도 같은 설정이었는지 |
| 로그 파일 위치, 최대 크기, 덮어쓰기 방식 (레지스트리 값) | 이미 밀려난 기록에 무엇이 있었는지 |
| 기록 시각에 감사 정책이 바뀌었고, 요청이 이 계정·로그온 세션에서 왔다는 것 (4719) | 그 계정 뒤에 있던 사람이 누구인지 |
| 로그가 덮고 있는 기간의 시작점 (가장 오래된 레코드 시각) | 꺼진 하위 범주에 해당하는 일이 없었다는 것 |

### 보고서 문장

- 쓸 수 있는 문장: "조사 시점에 이 PC 의 '프로세스 만들기' 하위 범주는 감사 없음이었습니다. 보안 로그의 가장 오래된 레코드는 ○○(UTC) 입니다."
- 쓰면 안 되는 문장: "4688 이 없으므로 이 기간에 프로그램이 실행되지 않았다."

두 번째 문장은 기록하지 않은 것을 일어나지 않은 것으로 적습니다. 실행 여부는 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md)의 다른 흔적으로 확인합니다.

## 시각 해석

`auditpol` 결과와 레지스트리 값은 조사한 때의 값이며, 값이 언제 그렇게 바뀌었는지는 알려 주지 않습니다. 사건 당시 설정은 4719 같은 변경 기록으로 따로 확인합니다.

로그의 가장 오래된 레코드 시각이 그 로그가 덮고 있는 기간의 시작입니다. 위 Windows 11 PC 의 예에서 보안 로그 20MB 에는 약 3만 4천 건이 있었고, 가장 오래된 기록은 약 이틀 전이었습니다. 같은 크기의 System 로그에는 약 2만 건, 약 3개월 치가 있었으므로 크기가 같아도 이벤트가 쌓이는 속도에 따라 덮는 기간이 크게 다릅니다.

- 레코드 시각의 저장 형식은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

## 함정과 한계

1. **없는 이벤트를 없었던 일로 읽습니다.** 먼저 그 PC 에서 해당 하위 범주가 켜져 있었는지 봅니다. 다음으로 로그가 그 시각까지 남아 있는지 봅니다.
2. **지금 설정을 사건 당시 설정으로 읽습니다.** 설정은 나중에 바뀔 수 있습니다. 4719 를 찾습니다.
3. **하위 범주를 이름으로 찾습니다.** 화면 언어에 따라 이름이 다릅니다. 스크립트나 규칙에서는 GUID 를 씁니다.
4. **문서의 기본값을 그대로 믿습니다.** MaxSize 가 문서 기본값 1MB 가 아니라 20MB 인 PC 가 있고, 보안 그룹 관리가 문서 표와 달리 켜져 있는 PC 도 있습니다. 기본값은 실제 기기에서 직접 확인합니다.
5. **Retention 을 도구가 보여 주는 숫자로만 읽습니다.** REG_DWORD 값을 문자열로 받는 도구는 부호 없는 10진으로 보여 주는 경우가 많습니다. 그래서 0xFFFFFFFF 가 4294967295 로 보일 수 있습니다. 원시 바이트로 확인합니다.
6. **고급 감사 정책을 설정했다고 그대로 적용됐다고 봅니다.** 고급 감사 정책 (Advanced Audit Policy Configuration) 을 쓸 때는 기본 감사 정책 (basic audit policy) 이 덮어쓰지 않는지 확인합니다[1]. 덮어쓰면 4719 가 남습니다. 이를 막는 설정은 Security Options 의 "Audit: Force audit policy subcategory settings (Windows Vista or later) to override audit policy category settings" 입니다. 이 설정을 Enabled 로 둡니다.
7. **4688 에 명령줄이 당연히 있다고 봅니다.** 프로세스 만들기 감사를 켜도 명령줄은 따로 켜야 남습니다. 켜는 설정과 주의점은 [프로세스 생성 (4688)](4688.md)에서 다룹니다.
8. **채널이 켜져 있다고 봅니다.** TaskScheduler/Operational·DriverFrameworks-UserMode/Operational·DNS-Client/Operational 은 꺼져 있을 수 있습니다. Sysmon 은 따로 설치해야 생깁니다.
9. **Retention 이 0 이 아닌 로그의 끝부분을 믿습니다.** 이 경우 로그가 가득 차면 새 이벤트를 버립니다. 그래서 오래된 기록은 남고 최근 기록이 빠질 수 있습니다. 보안 로그가 가득 차면 1104 가 남습니다.

### 지우기와 조작

- **감사 정책을 끕니다.** 4719 에 바뀐 하위 범주와 요청한 계정이 남습니다.
- **로그를 지웁니다.** 1102·104 가 남습니다. [이벤트 로그를 지웠나](../../04-scenarios/activity/anti-forensics/log-clearing.md)에서 흐름을 봅니다.
- **이벤트 로그 서비스를 멈춥니다.** 1100 이 남습니다.
- **자동 백업을 켭니다.** 1105·105 의 BackupPath 필드에 백업 파일 위치가 적힙니다. 원래 로그에서 밀려난 기록이 그 파일에 있을 수 있습니다.
- **레코드 일부만 남습니다.** 덮어쓰거나 지운 레코드가 파일 안에 남아 있을 수 있습니다. [파일 안에 남은 지운·손상 레코드](../../01-foundations/database-log-formats/evtx-evt-etl/chunk-slack-corrupted-evtx.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

MaxSize 와 Retention 은 REG_DWORD 입니다. 값 데이터는 4바이트 리틀 엔디언입니다. 값이 저장되는 셀 구조는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

아래 바이트는 설명을 위해 명세대로 만든 예시입니다. 실제 기록에서 나온 값이 아닙니다.

**1) MaxSize**

```
00 00 40 01
```

1. 리틀 엔디언으로 읽으면 0x01400000 입니다.
2. 10진으로 20,971,520 바이트, 곧 20MB 입니다.
3. 65,536 (64K) 으로 나누면 320 입니다. 나머지가 없으니 64K 배수 조건을 채웁니다.

**2) Retention**

```
FF FF FF FF
```

1. 0xFFFFFFFF 입니다. 0 이 아니므로 가득 차면 덮어쓰지 않고 새 이벤트를 버립니다.
2. 부호 있는 32비트로 읽으면 -1 입니다. 이 값일 때만 AutoBackupLogFiles 가 쓰입니다.
3. 부호 없는 10진으로 보여 주는 도구에서는 4294967295 로 보입니다.
4. `00 00 00 00` 이면 항상 덮어씁니다.

> 그림 자리: Services\Eventlog\Security 키의 MaxSize·Retention 값 셀을 헥스 편집기로 연 화면과, 각 4바이트를 10진·부호 있는 값으로 바꾸는 과정

### 공개 도구로 한 번

라이브 시스템에서는 Windows 에 들어 있는 명령으로 봅니다.

```powershell
# 감사 정책 전체 (이름은 화면 언어로 나옵니다)
auditpol /get /category:*

# 보안 로그 설정
wevtutil gl Security

# 모든 채널의 켜짐·크기·덮어쓰기 방식
Get-WinEvent -ListLog * | Select-Object LogName, IsEnabled, MaximumSizeInBytes, LogMode, RecordCount
```

이미지에서는 하이브 사본을 불러와 값을 읽습니다. 아래 `E:\case\` 는 예시 경로입니다. 컨트롤셋 번호는 먼저 확인합니다.

```powershell
reg load HKLM\CASE_SYS E:\case\SYSTEM
reg query "HKLM\CASE_SYS\ControlSet001\Services\Eventlog\Security"
reg unload HKLM\CASE_SYS

# 보안 로그를 Task 값 (하위 범주 번호) 으로 묶어 세기
Get-WinEvent -Path 'E:\case\Security.evtx' |
  Group-Object Task | Sort-Object Count -Descending | Select-Object Name, Count
```

도구가 REG_DWORD 를 어떻게 보여 주는지 한 값은 원시 바이트와 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [프로세스 생성 (4688)](4688.md) | 4688 이 없을 때 프로세스 만들기 감사가 꺼져 있었는지 |
| [서비스 설치 (7045·4697)](7045-4697.md) | 4697 이 없을 때 보안 시스템 확장 감사가 꺼져 있었는지 |
| [PowerShell 실행 기록 (4103·4104)](powershell-event-logs-4103-4104.md) | Operational 채널 크기와 실제로 남은 기간 |
| [로그온·로그오프](logon-events/index.md) | Audit Logon 기본값이 성공만인지, 실패도 남는지 (Windows 10 1809 전후) |
| [이벤트 로그 삭제 (1102·104)](1102-104.md) | 설정 변경 앞뒤에 로그를 지웠는지 |
| [EVTX 파일 구조](../../01-foundations/database-log-formats/evtx-evt-etl/file-header-chunk-record.md) | 파일 크기와 MaxSize, 가장 오래된 레코드 |
| [Sysmon 개념과 설정 확인](sysmon/sysmon-config.md) | 기본 감사에 없는 기록을 Sysmon 이 채우고 있었는지 |

## 실습

**직접 만든 Windows 10·11 가상 머신**에서 해 봅니다.

1. `auditpol /get /category:*` 결과를 저장합니다. 위 Microsoft 기본값 표와 비교해 다른 하위 범주를 찾습니다.
2. `auditpol /set /subcategory:{0CCE922B-69AE-11D9-BED3-505054503030} /success:enable` 로 프로세스 만들기 감사를 켭니다. 4719 가 남는지 보고 AuditPolicyChanges 필드 값을 적습니다.
3. 레지스트리의 `Services\Eventlog\Security` 값과 `wevtutil gl Security` 결과를 맞춰 봅니다.
4. 테스트용 채널 하나의 최대 크기를 줄이고 이벤트를 쌓습니다. 가장 오래된 레코드 시각이 어떻게 바뀌는지 봅니다.
5. `Get-WinEvent -ListLog *` 로 TaskScheduler/Operational 이 기본으로 꺼져 있는지 확인합니다.

**NIST CFReDS 같은 공개 시험 자료**에서는 다음을 풀어 봅니다.

1. SYSTEM 하이브의 `Services\Eventlog\Security` 에서 MaxSize 와 Retention 은 얼마입니까?
2. Security.evtx 의 가장 오래된 레코드와 가장 새 레코드 시각은 언제입니까? 사건 기간을 덮습니까?
3. 보안 로그를 Task 값으로 묶어 세면 어떤 하위 범주가 보입니까? 13312 (Process Creation) 가 있습니까?
4. 4719 가 있습니까? 있다면 어느 하위 범주를 언제 바꿨습니까?

## 참고 문헌

- Microsoft Learn, "System Audit Policy recommendations" (2025-06-13) — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/audit-policy-recommendations
- Microsoft Learn, "Command line process auditing" (2025-05-12) — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/component-updates/command-line-process-auditing
- Microsoft Learn, "Eventlog Key" (2018-05-31) — https://learn.microsoft.com/en-us/windows/win32/eventlog/eventlog-key
