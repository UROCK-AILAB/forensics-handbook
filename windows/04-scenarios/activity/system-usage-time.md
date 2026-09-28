---
title: "PC 사용 시간 재구성 (켜짐·꺼짐·로그온)"
parent: "시나리오 · 행위 재구성"
nav_order: 3850
---

# PC 사용 시간 재구성 (켜짐·꺼짐·로그온) (System Usage Time)

PC 한 대를 두고 "언제 켜져 있었고, 언제 꺼졌고, 그 사이 언제 로그온하고 자리를 비웠나" 를 묻는 조사를 다룹니다. 전원 기록과 세션 기록은 서로 다른 로그와 레지스트리에 흩어져 있는데, 이 페이지는 두 기록을 어떤 순서로 이어 붙이는지와 기록이 빈 구간을 어떻게 읽는지를 정리합니다.

이벤트마다의 전체 필드와 다른 켜짐·꺼짐 이벤트는 [켜짐·꺼짐](../../02-artifacts/event-logs/power-on-off-events.md) 과 [로그온·로그오프](../../02-artifacts/event-logs/logon-events/index.md) 에 있습니다.

## 조사 질문

- PC 는 언제 켜지고 언제 꺼졌습니까?
- 정상으로 꺼졌습니까, 갑자기 꺼졌습니까?
- 켜져 있는 동안 언제 로그온했고, 언제 화면을 잠갔습니까?
- 원격 세션으로 쓴 시간이 있습니까?
- 기록이 빈 구간은 PC 가 꺼져 있던 시간입니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| Windows 버전 | 이벤트의 버전과 필드가 Windows 버전마다 다를 수 있습니다. [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 버전과 빌드를 먼저 적습니다. |
| 시간대 | 이벤트 로그 도구가 보여 주는 .evtx 시각은 보는 PC 의 시각 설정에 맞춰 바꾼 값이라 시간대를 먼저 확인합니다[1]. [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽고, Bias 값은 [이 파일을 누가 언제 열었나](file-access.md) 의 "먼저 확인할 것" 에 적은 대로 부호 있는 수로 읽습니다. |
| 감사 정책 | 잠금·해제와 원격 세션 이벤트는 감사 하위 범주 하나에 묶여 있습니다[2]. [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 분석 대상의 설정을 확인합니다. |
| 로그 삭제·시각 변경 | 로그를 지웠거나 시스템 시각을 바꿨다면 순서가 틀어집니다. [이벤트 로그 삭제](../../02-artifacts/event-logs/1102-104.md) 와 [시간 변경](../../02-artifacts/event-logs/4616-kernel-general.md) 을 먼저 봅니다. |
| 수집 범위 | System·Security 이벤트 로그, SYSTEM·SOFTWARE 하이브, `%SystemRoot%\Bootstat.dat`, SRUDB.dat 를 함께 확보합니다. 이벤트 로그 파일 형식은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에 있습니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | System 로그 1074·6006·6008·41 | 종료·재시작의 종류와 시각 | [켜짐·꺼짐](../../02-artifacts/event-logs/power-on-off-events.md) |
| 2 | 레지스트리의 마지막 종료 시각 | 마지막으로 꺼진 시각 | [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) |
| 3 | `Bootstat.dat` · Reliability 키 | 부팅·종료·재개가 성공했는지, 비정상 종료와 관계있는 값 | [켜짐·꺼짐](../../02-artifacts/event-logs/power-on-off-events.md) |
| 4 | Security 로그의 로그온·로그오프 | 세션이 열리고 닫힌 시각 | [로그온·로그오프](../../02-artifacts/event-logs/logon-events/index.md) |
| 5 | Security 로그 4800·4801·4802·4803 | 잠금·해제·화면 보호기 | [로그온·로그오프](../../02-artifacts/event-logs/logon-events/index.md) |
| 6 | Security 로그 4778·4779 | 원격 세션 다시 연결·끊김 | [원격 데스크톱 이벤트](../../02-artifacts/event-logs/rdp-event-logs/index.md) |
| 7 | SRUM | 앱별 사용량 | [SRUM](../../02-artifacts/execution/system-resource-usage-monitor/index.md) |
| 8 | 프리페치·윈도 오류 보고 | 켜져 있던 동안의 실행 흔적 | [프리페치](../../02-artifacts/execution/prefetch/index.md) · [윈도 오류 보고](../../02-artifacts/execution/wer.md) |

전원 기록(1~3)으로 켜져 있던 구간을 먼저 정합니다. 그 구간 안에 세션 기록(4~6)을 올립니다. 로그가 빈 구간은 7~8 로 채웁니다.

## 종료와 재시작 이벤트

모두 System 로그에 남습니다[1].

| ID | 남는 때 | 기록 시각이 가리키는 것 |
|---|---|---|
| 1074 | 응용 프로그램이 시스템 종료·재시작을 일으켰을 때[1]. 사용자가 시작 메뉴나 Ctrl+Alt+Del 로 끄거나 다시 시작할 때도 남습니다[1]. | 꺼지기 전 |
| 6006 | Windows 가 제대로 꺼졌을 때[1] | 앞뒤 이벤트의 시각과 맞춰 확인 |
| 6008 | 직전 종료가 예기치 않았을 때(dirty shutdown)[1] | 다시 켜진 뒤. 메시지 안에 직전 종료 시각이 따로 있습니다[1]. |
| 41 | 깨끗하게 꺼지지 않고 다시 켜졌을 때[1] | 다시 켜진 뒤 |

**1074.**

`shutdown.exe` 는 꺼지기 직전 System 로그에 원본(Source) User32, ID 1074 를 남기고, 여기에는 사용자 지정 메시지와 이유 코드, 사용자 이름, shutdown 명령을 낸 날짜·시각이 함께 들어갑니다[1].

**6008.**

- 6008 에서 얻은 종료 시각 이전의 Application·System 로그를 살핍니다[1]. 6008 메시지 안의 시각이 직전 종료 시각의 단서입니다.
- 이 시각이 UTC 인지 현지 시각 문자열인지는 앞뒤 이벤트의 시각과 맞춰 보고 정합니다.

## Kernel-Power 41 을 읽는 법

- 로그는 System, 공급자는 Microsoft-Windows-Kernel-Power, ID 는 41, 수준은 Critical(위험), 버전은 6.1 입니다[1].
- 메시지는 "The system has rebooted without cleanly shutting down first. This error could be caused if the system stopped responding, crashed, or lost power unexpectedly." 입니다[1].
- Windows 는 켜질 때 직전에 깨끗하게 꺼졌는지 확인하고 아니면 41 을 만들기 때문에[1], 41 의 기록 시각은 꺼진 시각이 아니라 다시 켜진 뒤의 시각입니다.
- EventData 필드는 BugcheckCode, BugcheckParameter1~4, SleepInProgress, PowerButtonTimestamp, BootAppStatus 입니다[1].

**경우마다 필드 값.** 아래 표는 "이런 일이 있으면 필드 값이 이렇다" 는 방향입니다[1]. 거꾸로 필드 값 하나로 원인을 단정하지 말고, 여러 필드와 앞뒤 이벤트를 함께 봅니다.

| 경우 | 필드 값 |
|---|---|
| Stop 오류(블루스크린)로 다시 켜짐 | BugcheckCode 에 버그체크 코드가 10진으로 들어갑니다[1]. 예: 159 = 0x9F[1] |
| 전원 버튼을 길게 눌러 다시 켬 | PowerButtonTimestamp 가 0 이 아닙니다[1]. |
| 전원이 끊김 | 41 이 아예 남지 않거나, 남아도 BugcheckCode 가 0 입니다[1]. |
| 응답 없는 PC 의 전원을 끊음. 또는 디스크 쓰기가 막힌 상태에서 전원 버튼을 4초 넘게 눌러 끔 | PowerButtonTimestamp 가 0 일 수 있습니다[1]. 그래서 이 값이 0 이라고 전원 버튼을 누르지 않았다고 보지 않습니다. |
| 덤프 파일 설정이 없음 | 모든 값이 0 인 41 과 함께 volmgr 46 "Crash dump initialization failed!" 이 있습니다[1]. |

- PowerButtonTimestamp 예시 값은 131728546170882432 이고, 이 필드의 단위는 공개되어 있지 않습니다[1].
- 예시 값을 FILETIME 으로 풀면 2018-06-07 14:16:57 UTC 가 나옵니다. 이 필드를 FILETIME 이라고 단정하지는 않습니다. FILETIME 형식은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- 물리 서버의 자동 서버 복구 (Automatic Server Recovery, ASR) 소프트웨어나 Hyper-V·VMware 하트비트 기능이 응답 없는 컴퓨터·VM 을 다시 켰을 수도 있습니다[1]. 41 이 있다고 사람이 전원을 만졌다고 보지 않습니다.

## 부팅 상태 파일과 Reliability 키

`%SystemRoot%\Bootstat.dat` 는 부팅, 종료, 최대 절전·절전에서 재개가 성공했는지를 적는 이진 파일입니다[1]. 사용자는 이 파일을 편집할 수 없습니다[1].

`HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Reliability` 에는 DirtyShutdown, LastAliveStamp, TimeStampInterval 값이 있고, 이 값들을 지우면 비정상 종료 뒤 종료 이벤트 추적기 창이 뜨지 않게 할 수 있습니다[1]. 세 값의 형식과 뜻은 [켜짐·꺼짐](../../02-artifacts/event-logs/power-on-off-events.md) 에서 확인합니다.

- 레지스트리에 남는 마지막 종료 시각은 [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 다룹니다.

## 로그온·잠금·원격 세션

세션이 열리고 닫힌 기록은 [로그온·로그오프](../../02-artifacts/event-logs/logon-events/index.md) 에서 다룹니다. 로그온 ID 로 한 세션의 시작과 끝을 잇는 법, 로그온 유형의 뜻도 그 페이지에 있습니다. 여기서는 세션 안의 잠금과 원격 연결을 적습니다.

"Audit Other Logon/Logoff Events" 하위 범주가 아래 이벤트를 남깁니다[2].

| ID | 메시지 |
|---|---|
| 4800 | The workstation was locked |
| 4801 | The workstation was unlocked |
| 4802 | The screen saver was invoked |
| 4803 | The screen saver was dismissed |
| 4778 | A session was reconnected to a Window Station |
| 4779 | A session was disconnected from a Window Station |

이 하위 범주는 원격 데스크톱 세션 연결·끊김, 워크스테이션 잠금·해제, 화면 보호기 켜짐·꺼짐을 다루고, 재전송 공격 탐지와 무선·유선(802.1x) 네트워크 접근 허용도 같은 범주입니다[2]. 워크스테이션·멤버 서버·도메인 컨트롤러 모두 Success 감사를 켜는 것이 권장 설정이고, 이벤트 양은 적습니다[2].

4800 과 4801 사이에는 그 세션의 화면이 잠겨 있었고, 4779 와 다음 4778 사이에는 그 원격 세션이 끊겨 있었습니다.

- 원격 세션 전체의 흐름은 [원격 데스크톱 이벤트](../../02-artifacts/event-logs/rdp-event-logs/index.md) 에서 봅니다.

## 로그가 빈 구간 채우기

- 프로그램을 실행한 시각은 그때 PC 가 켜져 있었다는 보조 근거입니다. [프리페치](../../02-artifacts/execution/prefetch/index.md) 와 [윈도 오류 보고](../../02-artifacts/execution/wer.md) 를 봅니다.
- SRUM 에는 앱별 사용량이 남습니다. 기록 간격과 표 구조는 [SRUM](../../02-artifacts/execution/system-resource-usage-monitor/index.md) 에서 확인합니다.
- 압수 이미지의 SRUDB.dat 같은 ESE 데이터베이스는 비정상 종료 상태인 경우가 많습니다. 트랜잭션 로그 사슬이 끊겨 JET API 로 복구가 안 되는 경우가 있습니다. 항상 사본에서 작업합니다.
- 손상된 데이터베이스는 읽는 방식에 따라 행 수가 달라질 수 있습니다. 두 가지 이상 방식으로 열어 비교합니다. 사례는 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에 있습니다.

## 분석 흐름

1. Windows 버전·시간대·감사 정책을 정리합니다.
2. 이벤트 로그를 지웠는지, 시스템 시각을 바꿨는지 먼저 봅니다. 흔적이 있으면 [증거를 없애려 했나](anti-forensics/index.md) 를 함께 봅니다.
3. System 로그에서 1074·6006·6008·41 을 시각 순으로 뽑습니다. 켜진 시각을 알려 주는 이벤트는 [켜짐·꺼짐](../../02-artifacts/event-logs/power-on-off-events.md) 에서 골라 함께 뽑습니다.
4. 종료 이벤트마다 다음 켜짐을 짝짓습니다. 6008·41 은 다시 켜진 뒤의 기록이므로 꺼진 시각으로 쓰지 않습니다. 6008 메시지 안의 직전 종료 시각을 따로 적습니다.
5. 41 이 있으면 필드 값으로 원인을 구분합니다.
6. 레지스트리의 마지막 종료 시각, `Bootstat.dat`, Reliability 키로 마지막 종료를 한 번 더 확인합니다.
7. 켜져 있던 구간마다 Security 로그의 로그온 세션을 올립니다.
8. 세션 안에 4800·4801·4802·4803 으로 잠금 구간을, 4778·4779 로 원격 연결 구간을 표시합니다.
9. 로그가 빈 구간은 SRUM·프리페치로 채웁니다. 채우지 못한 구간은 "기록 없음" 으로 남깁니다.
10. 모든 시각을 UTC 로 맞춰 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다. 이벤트 뷰어 화면에서 옮겨 적은 시각이면 보는 PC 의 시간대를 함께 적습니다.
11. 그 구간에 PC 앞에 있던 사람은 [그 시각에 PC 를 쓴 사람이 누구인가](user-attribution.md) 를 따라 좁힙니다.

## 흔한 오판

1. **41·6008 의 기록 시각을 꺼진 시각으로 씁니다.** Windows 는 다음에 켜질 때 41 을 남깁니다[1]. 6008 도 직전 종료가 예기치 않았을 때 남는 기록입니다[1].
2. **41 이 있으면 누군가 전원 버튼을 눌렀다고 봅니다.** 블루스크린, 전원 끊김, 복구 소프트웨어·가상화 하트비트도 41 을 남깁니다[1]. 필드 값으로 구분합니다.
3. **41 이 없으니 전원이 끊긴 적이 없다고 봅니다.** 전원이 끊기면 41 이 아예 남지 않을 수 있습니다[1].
4. **이벤트 뷰어 화면의 시각을 그대로 옮깁니다.** 그 시각은 보는 PC 의 시각 설정에 맞춰 바꾼 값입니다[1].
5. **4800 이 없으니 화면을 잠그지 않았다고 봅니다.** 이 이벤트는 감사 하위 범주가 켜져 있어야 남습니다[2]. 설정부터 확인합니다.
6. **로그가 빈 구간을 PC 가 꺼져 있던 시간으로 봅니다.** 로그 삭제, 감사 꺼짐, 절전 상태에서도 빈 구간이 생깁니다. 절전·재개 이벤트는 [켜짐·꺼짐](../../02-artifacts/event-logs/power-on-off-events.md) 에서 봅니다.
7. **1074 의 사용자 이름을 끈 사람으로 씁니다.** 1074 에 들어가는 것은 계정 이름입니다[1]. 사람은 따로 좁힙니다.
8. **Reliability 값이 없으니 비정상 종료가 없었다고 봅니다.** 이 값들은 지울 수 있습니다[1].

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 ○○ 에 PC 를 강제로 껐습니다."
- 쓸 문장: "System 로그에 Kernel-Power 41 이벤트가 ○○(UTC)에 기록돼 있습니다. 이 이벤트는 깨끗하게 꺼지지 않은 PC 가 다시 켜질 때 남습니다. 이 이벤트의 BugcheckCode 는 0 이고 PowerButtonTimestamp 는 0 이 아닙니다. Microsoft 문서는 전원 버튼을 길게 눌러 다시 켜면 PowerButtonTimestamp 가 0 이 아니라고 적었습니다. 이 기록은 그 경우와 맞습니다. 직전에 PC 가 꺼진 시각은 이 이벤트의 기록 시각보다 앞입니다. 누가 버튼을 눌렀는지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [켜짐·꺼짐](../../02-artifacts/event-logs/power-on-off-events.md) — 전원 이벤트 전체와 필드입니다.
- [로그온·로그오프](../../02-artifacts/event-logs/logon-events/index.md) — 세션을 잇는 법과 로그온 유형입니다.
- [원격 데스크톱 이벤트](../../02-artifacts/event-logs/rdp-event-logs/index.md) — 원격 세션의 흐름입니다.
- [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) — 이벤트가 남는 조건입니다.
- [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) — 마지막 종료 시각입니다.
- [SRUM](../../02-artifacts/execution/system-resource-usage-monitor/index.md) — 로그가 빈 구간을 채우는 사용량 기록입니다.
- [타임라인 작성](../../03-techniques/analysis/timeline/index.md) — 시각을 시간순으로 합칩니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](user-attribution.md) — 구간에서 사람으로 좁힙니다.
- [증거를 없애려 했나](anti-forensics/index.md) — 로그 삭제와 시각 변경입니다.

## 참고 문헌

1. Microsoft Learn, "Event ID 41 The system has rebooted without cleanly shutting down first" (2026-02-12) — https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/event-id-41-restart
2. Microsoft Learn, "Audit Other Logon/Logoff Events" (Windows 10 보관 문서, 2021-09-06, 갱신 2026-04-27) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-other-logonlogoff-events
