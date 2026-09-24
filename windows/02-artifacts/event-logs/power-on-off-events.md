# 켜짐·꺼짐 (Power On·Off Events)

## 한 줄 요약

Windows 는 켜질 때, 꺼질 때, 절전에 들어가고 나올 때 System 로그에 여러 이벤트를 남깁니다. 켜진 시각은 Kernel-General 12 에, 꺼진 시각은 Kernel-General 13 에 들어 있습니다. 누가 어떤 프로세스로 종료·재시작했는지는 User32 1074 에 남습니다. 정상적으로 꺼지지 않았으면 다음 부팅 때 Kernel-Power 41 과 EventLog 6008 이 남습니다.

## 무엇을 기록하나 · 왜 생기나

| 상황 | 로그 | 공급자 · ID | 알려 주는 것 |
|---|---|---|---|
| 켜짐 | System | Kernel-General 12 | OS 가 시작한 시각 (StartTime) |
| 켜짐 | System | Kernel-Boot 20 | 직전 종료와 직전 부팅이 성공했는지 |
| 켜짐 | System | Kernel-Boot 27 | 부팅 종류 (BootType) |
| 켜짐 | System | EventLog 6009 · 6005 · 6013 | OS 버전 문자열, 이벤트 로그 서비스 시작, 가동 시간 |
| 켜짐 | Security | 4608 | LSASS 가 시작하고 감사 기능이 준비됨 |
| 꺼짐 | System | User32 1074 | 종료·재시작을 일으킨 프로세스, 사용자, 이유 |
| 꺼짐 | System | Winlogon 7002 | 사용자 로그오프 알림 |
| 꺼짐 | System | EventLog 6006 | 이벤트 로그 서비스가 멈춤 (제대로 꺼짐) |
| 꺼짐 | System | Kernel-Power 109 | 커널 전원 관리자가 종료를 시작함 |
| 꺼짐 | System | Kernel-General 13 | OS 가 꺼지는 시각 (StopTime) |
| 꺼짐 | Security | 4609 · 1100 | Windows 종료, 이벤트 로그 서비스 종료 |
| 비정상 종료 뒤 | System | Kernel-Power 41 · EventLog 6008 | 직전에 깨끗하게 꺼지지 않았음 |
| 절전 | System | Kernel-Power 42 · 107 | 절전에 들어감, 절전에서 돌아옴 |
| 절전 | System | Power-Troubleshooter 1 | 잠든 시각과 깨어난 시각, 깨운 원인 |
| 모던 스탠바이 | System | Kernel-Power 506 · 507 · 566 | 모던 스탠바이에 들어감·나옴, 세션 상태 변화 |

- Microsoft 는 1074 가 두 경우에 남는다고 적었습니다. 응용 프로그램이 종료·재시작을 일으켰을 때, 그리고 사용자가 시작 메뉴나 Ctrl+Alt+Del 로 종료·재시작했을 때입니다.
- `shutdown.exe` 도 꺼지기 직전에 Source=User32, ID 1074 로 사용자 이름·날짜·시각·이유 코드·설명을 남깁니다.
- 41 은 예기치 않게 꺼진 뒤 다음 부팅 때 남습니다.
- Windows 는 꺼질 때 오류 코드를 기록할 수 있으면 기록합니다. 다음 시작의 커널 단계에서 그 코드를 41 의 데이터에 넣습니다.
- 6006 은 제대로 꺼졌다는 뜻입니다. 6008 은 직전 종료가 예기치 않았다는 뜻입니다.
- Winlogon 7001 은 로그온 알림입니다. 로그온 자체는 [로그온·로그오프](logon-events/index.md)에서 다룹니다.

## 위치와 버전별 차이

- 대부분 System 로그에 남습니다. 4608·4609·1100 은 Security 로그에 남습니다.
- 한 PC 의 Security 로그에는 4608·4609 가 없었습니다. 약 이틀 치만 남아 있어 마지막 부팅 기록이 이미 밀려났습니다. (확인 범위: Win11 빌드 26200 한 대)
- 4608 이 어느 감사 하위 범주에 속하는지는 확인하지 못했습니다.
- 부팅 상태 파일 `%SystemRoot%\Bootstat.dat` 에 부팅·종료·최대 절전/절전에서 돌아옴의 성공 여부가 기록됩니다. Microsoft 문서가 Windows Internals 6판을 인용해 적은 내용입니다. 내부 구조는 확인하지 못했습니다.

### 이벤트 버전

아래는 한 PC 의 공급자 메타데이터에서 읽은 버전입니다. (확인 범위: Win11 빌드 26200 한 대) 버전마다 어느 Windows 부터 쓰였는지는 확인하지 못했습니다.

| 이벤트 | 버전 | 차이 |
|---|---|---|
| Kernel-Power 41 | 0 ~ 10 | 버전 0·1 의 메시지는 "The last sleep transition was unsuccessful…" 입니다. 뒤 버전의 메시지는 "The system has rebooted without cleanly shutting down first…" 입니다. 버전이 올라갈수록 칸이 늘어납니다 |
| Kernel-Boot 20 · 27 | 1 | — |
| Kernel-Power 42 | 3 | — |
| Power-Troubleshooter 1 | 3 | — |

### 같은 번호를 다른 공급자가 씁니다

한 PC 의 System 로그에서 본 예입니다. (확인 범위: Win11 빌드 26200 한 대)

- ID 12 는 Kernel-General (부팅) 말고도 BTHUSB·UserModePowerService·Wininit 이 썼습니다.
- ID 1 은 Kernel-General (시각 변경)·Power-Troubleshooter (깨어남) 말고도 Configuration-Change-Monitor·FilterManager·Hyper-V-Hypervisor·IsolatedUserMode 가 썼습니다.
- 7001·7002 도 Winlogon 말고 다른 드라이버가 썼습니다.

그래서 번호만으로 거르지 않습니다. 공급자 이름을 함께 거릅니다. Kernel-General 1 (시각 변경) 은 [시간 변경 (4616·Kernel-General)](4616-kernel-general.md)에서 다룹니다.

## 구조

아래 메시지와 칸은 한 PC 의 공급자 메타데이터에서 읽었습니다. (확인 범위: Win11 빌드 26200 한 대) 공급자 이름은 `Microsoft-Windows-` 를 뺀 짧은 이름으로 적었습니다.

### 켜짐·꺼짐

| 공급자 · ID | 메시지 | 칸 |
|---|---|---|
| Kernel-General 12 | The operating system started at system time %7. | MajorVersion, MinorVersion, BuildVersion, QfeVersion, ServiceVersion, BootMode, StartTime (FILETIME) |
| Kernel-General 13 | The operating system is shutting down at system time %1. | StopTime (FILETIME) |
| Kernel-Boot 20 | The last shutdown's success status was %1. The last boot's success status was %2. | LastShutdownGood, LastBootGood, LastBootId, BootStatusPolicy |
| Kernel-Boot 27 | The boot type was %1. | BootType, LoadOptions |
| Kernel-Power 109 | The kernel power manager has initiated a shutdown transition. | ShutdownActionType, ShutdownEventCode, ShutdownReason |
| Winlogon 7001 · 7002 | User Logon (Logoff) Notification for Customer Experience Improvement Program | TSId, UserSid |
| Security 4608 | Windows is starting up. This event is logged when LSASS.EXE starts and the auditing subsystem is initialized. | 없음 |
| Security 4609 | Windows is shutting down. All logon sessions will be terminated by this shutdown. | 없음 |

### 칸 이름이 없는 옛 방식 이벤트

EventLog 공급자와 User32 공급자는 매니페스트가 없는 옛 방식입니다. 메시지 파일은 각각 `%SystemRoot%\System32\netevent.dll`, `%SystemRoot%\system32\user32.dll` 이었습니다. 그래서 칸 이름이 없고, 순서로 읽습니다. 공급자와 메시지 파일의 관계는 [공급자와 메시지 파일](../../01-foundations/database-log-formats/evtx-evt-etl/provider-message-table.md)에서 다룹니다.

| ID | 메시지 |
|---|---|
| 6005 | The Event log service was started. |
| 6006 | The Event log service was stopped. |
| 6008 | The previous system shutdown at … on … was unexpected. |
| 6009 | OS 버전 문자열 (예: `10.00. 26200 Multiprocessor Free`) |
| 6013 | The system uptime is N seconds. |

User32 1074 의 메시지는 "The process … has initiated the [종류] of computer … on behalf of user … for the following reason: …" 입니다. 뒤에 Reason Code·Shutdown Type·Comment 가 붙습니다. 칸은 param1 ~ param7 입니다.

| 칸 | 뜻 | 한 PC 에서 본 값 |
|---|---|---|
| param1 | 종료를 일으킨 프로세스와 컴퓨터 | 시작 메뉴 재시작: `C:\Windows\SystemApps\Microsoft.Windows.StartMenuExperienceHost_cw5n1h2txyewy\StartMenuExperienceHost.exe ([컴퓨터 이름])`. 업데이트 재시작: `C:\WINDOWS\servicing\TrustedInstaller.exe` |
| param2 | 컴퓨터 | — |
| param3 | 이유 글자 | "기타(계획되지 않음)", "운영 체제: 업그레이드(계획됨)" |
| param4 | 이유 코드 | 0x0, 0x80020003 |
| param5 | 종료 종류 | "다시 시작" |
| param6 | 설명 | — |
| param7 | 사용자 | `[컴퓨터 이름]\[사용자]`, `NT AUTHORITY\SYSTEM` |

(확인 범위: Win11 빌드 26200 한 대, 한국어 화면)

### 비정상 종료 (Kernel-Power 41)

버전 10 의 칸은 다음과 같습니다: BugcheckCode, BugcheckParameter1~4, SleepInProgress, PowerButtonTimestamp, BootAppStatus, Checkpoint, ConnectedStandbyInProgress, SystemSleepTransitionsToOn, CsEntryScenarioInstanceId, BugcheckInfoFromEFI, CheckpointStatus, CsEntryScenarioInstanceIdV2, LongPowerButtonPressDetected, LidReliability, InputSuppressionState, PowerButtonSuppressionState, LidState, WHEABootErrorCount.

Microsoft 문서는 몇 칸을 이렇게 설명합니다.

- BugcheckCode 는 10진수로 들어 있습니다. 예를 들어 159 는 0x9F 입니다.
- 전원 버튼을 길게 눌러 재시작하면 PowerButtonTimestamp 가 0 이 아닙니다. 문서의 예시 값은 131728546170882432 입니다.
- 41 이 아예 없거나 BugcheckCode 가 0 이면 전원 문제일 수 있습니다. 배터리 분리·방전, 플러그 뽑힘, 정전 같은 경우입니다.
- 모든 값이 0 이면 volmgr 46 ("Crash dump initialization failed!") 도 확인하라고 적었습니다.

### 절전·최대 절전·모던 스탠바이

| 공급자 · ID | 메시지 | 칸 |
|---|---|---|
| Kernel-Power 42 | The system is entering sleep. Sleep Reason: %3 | TargetState, EffectiveState, Reason, Flags, TransitionsToOn |
| Kernel-Power 107 | The system has resumed from sleep. | TargetState, EffectiveState, WakeFromState, ProgrammedWakeTimeAc, ProgrammedWakeTimeDc, WakeRequesterTypeAc, WakeRequesterTypeDc |
| Power-Troubleshooter 1 | The system has returned from a low power state. Sleep Time: %1 Wake Time: %2 Wake Source: … | SleepTime (FILETIME), WakeTime (FILETIME), SleepDuration, WakeDuration, HiberWriteDuration, HiberReadDuration, HiberPagesWritten, WakeSourceType, WakeSourceText 등 |
| Kernel-Power 506 | The system is entering Modern Standby Reason: %1. | — |
| Kernel-Power 507 | The system is exiting Modern Standby Reason: %10. | — |
| Kernel-Power 566 | The system session has transitioned from %3 to %10. Reason %2 BootId: %1 | — |
| Kernel-Power 105 | Power source change. | AcOnline, RemainingCapacity, FullChargeCapacity |

## 증거로서 의미

한 PC 에서 본 정상 재시작의 순서입니다. 시작 메뉴로 재시작한 경우입니다. (확인 범위: Win11 빌드 26200 한 대, 시각은 UTC)

| 시각 | 이벤트 | 값 |
|---|---|---|
| 21:53:09 | User32 1074 | param1 StartMenuExperienceHost.exe, param3 "기타(계획되지 않음)", param5 "다시 시작" |
| 21:54:10 | Winlogon 7002 | TSId 1 |
| 21:54:29 | EventLog 6006 | — |
| 21:54:34 | Kernel-Power 109 | ShutdownActionType 5, ShutdownEventCode 0, ShutdownReason 5 |
| 21:54:36 | Kernel-General 13 | StopTime 21:54:36.8545988Z |
| 21:54:50 | Kernel-General 12 | StartTime 21:54:49.5000000Z |
| 21:54:50 | Kernel-Boot 20 · 27 | LastShutdownGood true, LastBootGood true, BootType 0 |
| 21:55:18 | EventLog 6009 → 6005 → 6013 | 거의 같은 시각 |

같은 PC 에서 본 비정상 종료 한 번입니다.

| 시각 | 이벤트 | 값 |
|---|---|---|
| 그 전 | 13·6006·109·1074 없음 | — |
| 21:44:18 | Kernel-General 12, Kernel-Boot 20 | LastShutdownGood false, LastBootGood true |
| 21:44:24 | Kernel-Power 41 (버전 10) | BugcheckCode 159 (0x9F), BugcheckParameter1 0x3, SleepInProgress 0, ConnectedStandbyInProgress true, Checkpoint 16, BugcheckInfoFromEFI true, PowerButtonTimestamp 0 아님 |
| 21:44:36 | EventLog 6008 → 6009 → 6005 → 6013 | 6008 의 종료 시각은 20:57:17 UTC |

- 같은 PC 의 41 은 세 건이었고 6008 도 세 건으로 날짜가 맞았습니다.
- 다른 두 건의 41 은 BugcheckCode 0 이었습니다. 한 건은 PowerButtonTimestamp 0·SleepInProgress 6, 다른 한 건은 모든 값이 0 이었습니다.

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| OS 가 시작하고 꺼진 시각 (12 의 StartTime, 13 의 StopTime) | 그 사이에 사람이 PC 앞에 있었는지 |
| 종료·재시작을 일으킨 프로세스와 사용자 계정, 선택한 이유 (1074) | 그 계정 뒤에 있던 사람이 누구인지 |
| 직전 종료가 깨끗하지 않았다는 것 (20 의 LastShutdownGood false, 41, 6008) | 정확히 언제 꺼졌는지 (6008 시각은 정확하지 않을 수 있습니다) |
| 절전에 들어간 시각과 깨어난 시각 (Power-Troubleshooter 1) | 모던 스탠바이 중에 PC 가 아무 일도 하지 않았는지 |

### 보고서 문장

- 쓸 수 있는 문장: "System 로그의 User32 1074 에 따르면 ○○(UTC) 에 `StartMenuExperienceHost.exe` 가 ○○\○○ 계정으로 재시작을 일으켰습니다. 이어서 Kernel-General 13 의 StopTime 은 ○○, 다음 Kernel-General 12 의 StartTime 은 ○○ 입니다."
- 쓰면 안 되는 문장: "사용자가 ○○시에 PC 를 껐다."

두 번째 문장은 계정을 사람으로 바꾸고, 어떤 기록인지도 밝히지 않습니다. 사용 시간 전체를 재구성하는 방법은 [PC 사용 시간 재구성](../../04-scenarios/activity/system-usage-time.md)에서 다룹니다.

## 시각 해석

- 12 의 StartTime, 13 의 StopTime, Power-Troubleshooter 1 의 SleepTime·WakeTime 은 FILETIME 입니다. 값 형식은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다.
- Microsoft 문서는 이벤트 뷰어가 .evtx 의 시각을 시스템 시간대로 바꿔 보여 준다고 주의를 줍니다. 서버 시간대를 확인하라고 적었습니다. 시간대 설정은 [시간대 설정](../system-account/time-zone.md)에서 다룹니다.

한 PC 에서 본 시각의 특징입니다. (확인 범위: Win11 빌드 26200 한 대)

- **레코드 번호와 시각 순서가 다릅니다.** 꺼질 때의 109·13 과 켜질 때의 12·20·27 은 레코드 번호가 다음 부팅의 6005 보다 뒤였습니다. 예: 6005 (레코드 18209, 21:55:18) → 109 (18214, 21:54:34) → 13 (18216, 21:54:36) → 12 (18217, 21:54:50). 커널 이벤트가 이벤트 로그 서비스가 다시 뜬 뒤에 파일에 쓰인 것으로 보입니다. 이 설명은 해석입니다. 레코드 번호가 아니라 시각으로 정렬합니다.
- **12 의 StartTime 은 0.5초 단위로 끊겨 있었습니다.** 이벤트 기록 시각보다 약 0.6초 빨랐습니다. 13 의 StopTime 은 이벤트 기록 시각과 같았습니다.
- **6005 는 늦습니다.** 네 번의 부팅에서 6005 는 12 의 StartTime 보다 19~29초 늦었습니다. 6005 를 켜진 시각으로 쓰면 그만큼 늦게 잡힙니다.
- **6013 은 하루 한 번도 남습니다.** 부팅 직후 한 번, 그 뒤 매일 03:00 UTC 쯤 한 번씩 남았습니다. 이 PC 시간대로는 정오입니다.
- **6008 의 시각은 현지 시각 글자입니다.** 메시지는 "The previous system shutdown at 오전 5:57:17 on ‎2026-‎09-‎21 was unexpected." 꼴이었습니다. 날짜 글자 안에 보이지 않는 U+200E (왼쪽에서 오른쪽 표시) 문자가 들어 있었습니다. 글자를 그대로 파싱하면 깨지기 쉽습니다.
- **6008 의 이진 데이터에 두 시각이 있습니다.** 앞 32바이트는 SYSTEMTIME 두 개였습니다. 첫째는 현지 시각, 둘째는 UTC 였습니다. 그 뒤 바이트의 뜻은 확인하지 못했습니다.
- **6005 의 이진 데이터 앞 16바이트도 SYSTEMTIME (UTC) 였습니다.**
- **6008 의 시각은 꺼진 시각이 아닐 수 있습니다.** 한 번의 비정상 종료에서 6008 의 시각 (20:57:17 UTC) 은 다음 부팅 (21:44) 보다 47분 앞이었습니다. 그때 이 PC 는 모던 스탠바이 중이었습니다 (41 의 ConnectedStandbyInProgress true). 6008 시각은 "마지막으로 살아 있음을 기록한 시각" 일 수 있습니다. 이 설명은 해석이며, 기록 방식은 확인하지 못했습니다.
- **PowerButtonTimestamp 는 FILETIME 으로 풀립니다.** 같은 41 의 값 134344115099009259 를 FILETIME 으로 풀면 2026-09-20T20:58:29.9Z 입니다. 6008 시각보다 약 1분 뒤입니다. 문서 예시 값도 FILETIME 으로 풀면 2018-06-07T14:16:57Z 입니다. 다만 이 칸이 FILETIME 이라는 설명은 Microsoft 문서에 없습니다. 이 해석은 값을 풀어 본 결과입니다.
- **6013 에는 시간대가 들어 있습니다.** 삽입 문자열 [6] 은 "-540 대한민국 표준시" 였습니다. 시간대 바이어스 (분) 와 현지화된 시간대 이름입니다. -540 은 UTC+9 입니다. 레지스트리의 REG_DWORD Bias 를 부호 없이 읽으면 4294966756 이 됩니다.
- **깨어난 시각은 107 이 아니라 Power-Troubleshooter 1 에서 봅니다.** 한 번의 최대 절전에서 107 의 기록 시각은 05:54:36 이었습니다. Power-Troubleshooter 1 의 WakeTime 은 05:56:39 로 2분 뒤였습니다.

## 함정과 한계

1. **번호만으로 거릅니다.** 12·1·7001·7002 는 다른 공급자도 씁니다. 공급자 이름을 함께 거릅니다.
2. **레코드 번호로 정렬합니다.** 부팅 앞뒤의 커널 이벤트는 레코드 번호 순서가 시각 순서와 다릅니다.
3. **6005 를 켜진 시각으로 씁니다.** 12 의 StartTime 보다 수십 초 늦습니다.
4. **1074 를 영어 글자로 거릅니다.** 이유 글자 (param3) 와 종류 (param5) 는 현지화된 글자로 저장돼 있었습니다. "restart" 로 찾으면 "다시 시작" 을 놓칩니다. (확인 범위: Win11 빌드 26200 한 대, 한국어 화면)
5. **BugcheckCode 를 16진으로 읽습니다.** 10진수입니다. 159 는 0x9F 입니다.
6. **6008 의 시각을 꺼진 시각으로 씁니다.** 모던 스탠바이 중이었다면 한참 앞설 수 있습니다.
7. **모던 스탠바이 PC 에서 42·107 만 찾습니다.** 한 노트북에서 약 3개월 동안 506 은 319건, 507 은 314건, 566 은 687건이었습니다. 42·107 은 7건뿐이었습니다. 이런 PC 에서는 뚜껑을 닫고 여는 일이 506·507 로 남는 것으로 보입니다. 이 판단은 해석입니다.
8. **절전 코드 값을 추측합니다.** 최대 절전 한 번에서 42 의 TargetState 는 5, 27 의 BootType 은 2 였습니다. Power-Troubleshooter 1 에 HiberWriteDuration 11073, HiberReadDuration 14298, HiberPagesWritten 2532886 이 있어 최대 절전과 맞습니다. 그러나 TargetState 5 와 BootType 2 의 공식 대응은 확인하지 못했습니다.
9. **6013 의 OS 이름을 믿습니다.** Windows 11 인데 6013 의 이진 데이터에는 "Windows 10 Home" 으로 적혀 있었습니다.
10. **Security 로그에서 4608·4609 를 기대합니다.** 보안 로그는 빨리 밀려납니다. 한 PC 에서는 이틀 치만 남아 있었습니다. 로그 크기와 보존 기간은 [감사 정책과 로그 설정](audit-policy-log-settings.md)에서 다룹니다.

### 지우기와 조작

- **로그를 지웁니다.** System 로그를 지우면 104 가 남습니다. [이벤트 로그 삭제 (1102·104)](1102-104.md)를 봅니다.
- **Reliability 값을 지웁니다.** Microsoft 문서는 `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Reliability` 에 DirtyShutdown, LastAliveStamp, TimeStampInterval 값이 있다고 적었습니다. 이 값을 지우면 비정상 종료 뒤 종료 이벤트 추적기가 뜨지 않게 할 수 있다고도 적었습니다. 그래서 이 값이 없다고 비정상 종료가 없었다고 보지 않습니다. 41·6008 을 따로 봅니다.
- **시스템 시각을 바꿉니다.** 켜짐·꺼짐 시각 전체가 어긋납니다. [시간 변경 (4616·Kernel-General)](4616-kernel-general.md)을 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

`HKLM\SYSTEM\CurrentControlSet\Control\Windows\ShutdownTime` 은 REG_BINARY 8바이트 FILETIME (UTC) 이었습니다. (확인 범위: Win11 빌드 26200 한 대) 41 의 PowerButtonTimestamp 도 FILETIME 으로 풀렸습니다.

아래 바이트는 설명을 위해 만든 예시입니다. Microsoft 문서 41 예시의 PowerButtonTimestamp 값 131728546170882432 를 8바이트 리틀 엔디언으로 적었습니다. 검체에서 나온 값이 아닙니다.

```
80 49 4B 31 6A FE D3 01
```

1. 리틀 엔디언이므로 뒤에서부터 읽습니다: 0x01D3FE6A314B4980.
2. 10진으로 131,728,546,170,882,432 입니다. 문서 예시 값과 같습니다.
3. FILETIME 으로 풀면 2018-06-07T14:16:57Z (UTC) 입니다.
4. 41 의 PowerButtonTimestamp 는 10진 정수로 보입니다. 시각으로 보려면 직접 풀어야 합니다.

> 그림 자리: 41 레코드의 PowerButtonTimestamp 8바이트를 FILETIME 으로 풀어 6008 의 SYSTEMTIME 과 나란히 놓은 그림

### 공개 도구로 한 번

Windows 에 들어 있는 PowerShell 의 `Get-WinEvent` 로 공급자와 ID 를 함께 거릅니다. 아래 `E:\case\` 는 예시 경로입니다.

```powershell
$f = 'E:\case\System.evtx'

# 켜짐·꺼짐 (공급자를 반드시 함께 거릅니다)
Get-WinEvent -FilterHashtable @{ Path = $f; ProviderName = 'Microsoft-Windows-Kernel-General'; Id = 12, 13 }
Get-WinEvent -FilterHashtable @{ Path = $f; ProviderName = 'Microsoft-Windows-Kernel-Boot'; Id = 20, 27 }
Get-WinEvent -FilterHashtable @{ Path = $f; ProviderName = 'User32'; Id = 1074 }
Get-WinEvent -FilterHashtable @{ Path = $f; ProviderName = 'EventLog'; Id = 6005, 6006, 6008, 6013 }

# 비정상 종료
Get-WinEvent -FilterHashtable @{ Path = $f; ProviderName = 'Microsoft-Windows-Kernel-Power'; Id = 41 } |
  ForEach-Object { ([xml]$_.ToXml()).Event.EventData.Data | Where-Object Name -in 'BugcheckCode', 'PowerButtonTimestamp', 'ConnectedStandbyInProgress' }

# 레코드 번호가 아니라 시각으로 정렬
Get-WinEvent -Path $f | Sort-Object TimeCreated | Select-Object TimeCreated, RecordId, ProviderName, Id
```

- 10진 PowerButtonTimestamp 는 `[datetime]::FromFileTimeUtc(131728546170882432)` 로 풀 수 있습니다.
- 도구가 레코드 번호 순서로만 보여 주는지 확인합니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [시스템 기본 정보](../system-account/os-version-computer-name-install-date-shutdown-t.md) | ShutdownTime 과 마지막 정상 13 의 StopTime. 한 PC 에서 이 값은 비정상 종료 뒤 바뀌지 않았습니다 |
| Reliability 키 | DirtyShutdownTime (16바이트 SYSTEMTIME) 과 6008 이진 데이터의 UTC SYSTEMTIME. 한 PC 에서 같은 값이었습니다. 하위 키 `shutdown` 의 ReasonCode 는 마지막 1074 의 이유 코드와 같았습니다 |
| `Bootstat.dat` | 파일 수정 시각과 마지막 부팅·깨어남 |
| [로그온·로그오프](logon-events/index.md) | 켜짐과 꺼짐 사이의 로그온 세션 |
| [시간 변경 (4616·Kernel-General)](4616-kernel-general.md) | 시각을 바꿔 켜짐·꺼짐 시각이 어긋났는지 |
| [시간대 설정](../system-account/time-zone.md) | 6008·6013 의 현지 시각과 바이어스 |
| [시간대·시계 오차 보정](../../03-techniques/analysis/timeline/time-normalization.md) | 다른 기록과 시각을 맞출 때 |

Reliability 키와 `Bootstat.dat` 에 대해 한 PC 에서 본 것은 다음과 같습니다. (확인 범위: Win11 빌드 26200 한 대)

- Reliability 키에는 TimeStampInterval 1, DirtyShutdown 1, DirtyShutdownTime, LastAliveStamp (REG_BINARY 4바이트) 가 있었습니다.
- LastAliveStamp·TimeStampInterval 의 뜻과 단위는 확인하지 못했습니다.
- `C:\Windows\bootstat.dat` 는 67,584바이트였습니다. 마지막 수정 시각은 모던 스탠바이에서 깨어난 시각대였습니다.

## 실습

**직접 만든 Windows 10·11 가상 머신**에서 해 봅니다. 각 단계의 시각을 적어 둡니다.

1. 시작 메뉴로 재시작합니다. 1074·7002·6006·109·13·12·20·27·6009·6005·6013 이 어떤 순서로 남는지 봅니다. 레코드 번호 순서와 시각 순서를 비교합니다.
2. `shutdown` 명령으로 이유와 설명을 넣어 재시작합니다. 1074 의 param 칸에 무엇이 들어가는지 봅니다.
3. 가상 머신의 전원을 강제로 끊습니다. 다음 부팅의 20·41·6008 을 확인합니다. 6008 의 시각과 실제로 끊은 시각을 비교합니다.
4. 최대 절전에 들어갔다 나옵니다. 42·107·Power-Troubleshooter 1·27 의 값과 시각을 비교합니다. TargetState 와 BootType 값을 적습니다.
5. `ShutdownTime` 과 Reliability 키 값을 정상 종료 뒤와 강제 종료 뒤에 각각 읽어 비교합니다.

**NIST CFReDS 같은 공개 검체**에서는 다음을 풀어 봅니다.

1. System 로그에서 Kernel-General 12·13 을 모두 뽑아 켜짐·꺼짐 구간 표를 만듭니다. 13 없이 12 가 이어지는 곳이 있습니까?
2. 그 자리에 41 과 6008 이 있습니까? BugcheckCode 와 PowerButtonTimestamp 는 얼마입니까?
3. 마지막 1074 의 param1·param7 은 무엇입니까? `ShutdownTime` 과 맞습니까?

## 참고 문헌

- Microsoft Learn, "Event ID 41 The system has rebooted without cleanly shutting down first" (2026-02-12) — https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/event-id-41-restart
