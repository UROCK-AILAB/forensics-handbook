---
title: "보안 프로그램을 끄거나 지웠나"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 3930
---

# 보안 프로그램을 끄거나 지웠나 (Defense Evasion)

보안 프로그램을 끄거나 설정을 바꾸면 그 일도 기록으로 남습니다. Windows 에 들어 있는 Microsoft Defender 바이러스 백신 (Microsoft Defender Antivirus) 은 실시간 보호 (Real-time protection) 가 꺼지거나 설정이 바뀔 때 운영 로그 (Operational log) 에 이벤트를 남깁니다[1]. 이 페이지는 이 운영 로그로 언제 무엇을 껐는지 찾고 누가 했는지 좁히는 순서를 다룹니다. 탐지 이벤트 1116·1117 의 구조는 [Windows Defender 탐지](../../../02-artifacts/event-logs/1116-1117.md) 에서, 검사 로그와 격리 파일은 [디펜더 검사 로그·격리 파일](../../../02-artifacts/execution/mplog-detectionhistory-quarantine.md) 에서 다룹니다. 다른 보안 제품은 제품마다 기록이 달라 여기서 다루지 않습니다.

## 조사 질문

- 실시간 보호를 끈 적이 있습니까? 언제 끄고 언제 다시 켰습니까?
- Defender 설정을 바꿨습니까? 어느 값을 어떻게 바꿨습니까?
- 설정을 바꾸려다 막힌 적이 있습니까?
- 위협을 탐지하고도 치료하지 않고 두었습니까? 탐지 기록을 지웠습니까?
- 보안 프로그램의 서비스를 멈추거나 프로그램을 지웠습니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| Windows 버전 | 분석 대상의 OS 버전을 적어 둡니다. 이 페이지의 이벤트가 그 버전에서 남는지는 로그에 실제로 남은 이벤트 ID 로 확인합니다. |
| 보안 프로그램 | 어떤 보안 프로그램을 설치했는지 [설치 프로그램](../../../02-artifacts/system-account/uninstall.md) 에서 먼저 봅니다. 이 페이지의 이벤트는 Microsoft Defender 바이러스 백신이 남기는 것입니다[1]. |
| 시간대 | 이벤트 레코드의 기록 시각은 FILETIME 형식의 UTC 입니다[2]. 1151 상태 보고서의 시각도 UTC 입니다[1]. 현지 시각으로 옮길 때는 [시간대 설정](../../../02-artifacts/system-account/time-zone.md) 을 먼저 읽습니다. |
| 사용자 | 1116 과 1013 에는 User 필드가 있습니다[1]. 5001·5007 같은 끄기·설정 이벤트에 계정 필드가 있는지는 실제 이벤트에서 확인합니다. 누가 했는지는 같은 시각의 로그온 세션과 실행 기록으로 좁힙니다. |
| 수집 범위 | 로그 폴더(기본 위치 `C:\Windows\System32\winevt\Logs\`)[2] 전체를 확보합니다. Defender 운영 로그 파일만 골라내지 말고 폴더째 확보합니다. SOFTWARE·SYSTEM 하이브, 프리패치, Defender 검사 로그와 격리 파일도 함께 확보합니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | Defender 운영 로그 5001·5000 | 실시간 보호가 꺼진 때와 켜진 때 | 이 페이지 아래 |
| 2 | 5004·5007 | 바뀐 설정과 바뀌기 전후 값 | 이 페이지 아래 |
| 3 | 5013 | 변조 방지가 막은 설정 변경 | 이 페이지 아래 |
| 4 | 5010·5012 | 악성·원치 않는 소프트웨어 검사와 바이러스 검사가 꺼진 때 | 이 페이지 아래 |
| 5 | 5008·3002·5101 | 오류나 만료로 보호가 멈춘 기록 | 이 페이지 아래 |
| 6 | 1116·1117·1118·1013 | 탐지, 조치, 조치 실패, 탐지 기록 지움 | [Windows Defender 탐지](../../../02-artifacts/event-logs/1116-1117.md) |
| 7 | 1150·1151 | 정상 동작 보고와 상태 보고서 | 이 페이지 아래 |
| 8 | 보안 4624·4688, 프리패치, PowerShell 기록 | 그 시각의 로그온 세션과 실행한 프로그램·명령 | [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) · [프로세스 생성](../../../02-artifacts/event-logs/4688.md) · [프리패치](../../../02-artifacts/execution/prefetch/index.md) · [PowerShell 실행 기록](../../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md) |
| 9 | 서비스·프로그램 설치 기록 | 보안 프로그램의 서비스를 멈추거나 프로그램을 지웠는지 | [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md) · [프로그램 설치·삭제 이벤트](../../../02-artifacts/event-logs/msiinstaller.md) |
| 10 | Defender 검사 로그·격리 파일 | 탐지하고 격리한 파일 | [디펜더 검사 로그·격리 파일](../../../02-artifacts/execution/mplog-detectionhistory-quarantine.md) |

## Defender 운영 로그 찾기

이벤트 뷰어에서는 Applications and Services Logs > Microsoft > Windows > Windows Defender > Operational 에 있고[1], 채널 이름은 `Microsoft-Windows-Windows Defender/Operational` 입니다[1]. 수집한 로그를 도구로 열 때는 이 채널 이름으로 찾습니다.

## 끄기와 설정 바꾸기

| 이벤트 ID | 기호 이름 | 뜻 | 필드 |
|---|---|---|---|
| 5000 | MALWAREPROTECTION_RTP_ENABLED | 실시간 보호 켜짐 | |
| 5001 | MALWAREPROTECTION_RTP_DISABLED | 실시간 보호 꺼짐. "Real-time protection is disabled." | |
| 5004 | MALWAREPROTECTION_RTP_FEATURE_CONFIGURED | 실시간 보호 기능의 설정이 바뀜 | Feature, Configuration |
| 5007 | MALWAREPROTECTION_CONFIG_CHANGED | 악성코드 방지 플랫폼의 설정이 바뀜. "The antimalware platform configuration changed." | Old value, New value |
| 5009 · 5010 | MALWAREPROTECTION_ANTISPYWARE_ENABLED · _DISABLED | 악성·원치 않는 소프트웨어 검사 켜짐 · 꺼짐 | |
| 5011 · 5012 | MALWAREPROTECTION_ANTIVIRUS_ENABLED · _DISABLED | 바이러스 검사 켜짐 · 꺼짐 | |
| 5013 | 아래 설명 | 변조 방지가 설정 변경을 막음. "Tamper protection blocked a change to Microsoft Defender Antivirus." | |

(출처 [1]. 칸이 빈 곳의 필드는 실제 이벤트에서 확인합니다.)

5001 과 그 뒤의 5000 을 짝지으면 실시간 보호가 꺼져 있던 구간이 나오고, 5007 의 Old value 와 New value 로 어느 설정이 어떻게 바뀌었는지 볼 수 있습니다[1]. 예상하지 못한 5007 은 악성코드 때문일 수 있으니, 이때는 설정을 살핍니다[1].

변조 방지 (Tamper protection) 가 켜져 있으면 Defender 는 설정을 바꾸려는 시도를 막고[1], 5013 에는 어떤 설정 변경을 막았는지 남습니다[1]. 5013 은 설정을 바꾸려다 막힌 기록이지 설정이 바뀐 기록이 아닙니다.

- Microsoft 문서에는 5013 의 기호 이름이 MALWAREPROTECTION_SCAN_CANCELLED 로 적혀 있습니다[1]. 이 이름은 1002(검사 중단)의 기호 이름과 같습니다[1]. 문서의 잘못일 수 있으니 기호 이름이 아니라 이벤트 ID 로 거릅니다.

## 사람이 껐는지, 오류로 멈췄는지

보호가 꺼진 기록이 모두 사람이 끈 것은 아닙니다. 아래 이벤트는 오류나 만료로 보호가 멈춘 기록입니다[1].

| 이벤트 ID | 기호 이름 | 뜻 | 필드 |
|---|---|---|---|
| 5008 | MALWAREPROTECTION_ENGINE_FAILURE | 엔진이 예기치 않은 오류로 끝남 | Failure Type(Crash·Hang), Exception Code, Resource |
| 3002 | MALWAREPROTECTION_RTP_FEATURE_FAILURE | 실시간 보호 기능에 오류가 남 | Feature, Error Code, Reason |
| 5100 | | 플랫폼 만료가 가까움 | |
| 5101 | MALWAREPROTECTION_DISABLED_EXPIRED_STATE | 플랫폼이 만료됨. 보호가 꺼짐 | Error Code, Error Description |

(출처 [1])

- 3002 뒤에 3007 이 이어지면 일시적인 실패에서 회복한 것입니다[1].
- 실시간 보호가 꺼진 구간 앞뒤에서 이 이벤트들을 찾습니다. 찾으면 오류로 멈춘 구간과 끈 구간을 나눠 적습니다.

## 탐지하고도 두었나, 탐지 기록을 지웠나

1116 은 위협을 탐지한 기록이고, 1117 은 조치한 기록이며, 1118 은 조치에 실패한 기록입니다[1]. 1117 의 Action 값은 Clean, Quarantine, Remove, Allow, User defined, No action, Block 가운데 하나입니다[1]. Allow·No action·None 은 위협을 치료하지 않는데[1], Allow 는 이후 탐지 이벤트를 억누르고 None 은 알림과 보호 기록을 계속 만듭니다[1]. 변조 방지가 켜져 있으면 이 조치들을 설정할 수 없습니다[1].

ThreatSeverityDefaultAction 이 None 이면 1116 이 남고[1], 뒤따르는 1117 의 Action 이 Allow 이면 탐지는 했지만 치료하지 않았다는 뜻입니다[1]. 1013 (MALWAREPROTECTION_MALWARE_HISTORY_DELETE) 은 악성코드 탐지 기록을 지운 기록이며[1], Time 필드는 기록을 지운 때이고 User 필드도 있습니다[1].

- 1116 의 다른 필드와 Detection Source 값은 [Windows Defender 탐지](../../../02-artifacts/event-logs/1116-1117.md) 에서 다룹니다.

Defender 는 악성코드를 탐지하면 악성코드가 바꿨을 수 있는 설정을 되돌립니다[1]. 되돌리는 설정은 아래와 같습니다[1].

- 기본 브라우저 설정, UAC 설정, Chrome 설정
- Boot Control Data
- Regedit·작업 관리자 레지스트리 설정
- Windows Update·BITS·RPC 서비스
- OS 파일

그래서 분석 대상 PC 의 지금 설정만 보고 바뀐 적이 없다고 판단하지 않습니다. 바뀐 이력은 5007 의 Old value·New value 로 봅니다.

## 상태 보고 (1150·1151)

1150 은 Defender 가 정상으로 돌고 있다는 보고이며 한 시간마다 남습니다[1]. 1151 은 상태 보고서이고 시각은 UTC 입니다[1]. 1151 에는 RTP state, OA state, IOAV state, BM state 가 남고 값은 Enabled·Disabled 가운데 하나이며[1], 서명 나이와 생성 시각, 마지막 빠른 검사·전체 검사의 시작·끝 시각 같은 값도 남습니다[1].

1150 은 상태를 모니터링 플랫폼에 보고하는 환경을 전제로 합니다[1]. 따로 보고하지 않는 가정용 PC 에도 남는지는 실제 기기에서 확인해야 합니다. 1151 이 남은 기기에서는 RTP state 가 Disabled 인 보고로 실시간 보호가 꺼져 있던 시점을 따로 확인합니다.

## 서비스를 멈추거나 프로그램을 지운 흔적

- 보안 프로그램의 서비스를 멈추거나 바꾼 흔적은 [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md) 에서 찾습니다.
- 프로그램을 지운 흔적은 [프로그램 설치·삭제 이벤트](../../../02-artifacts/event-logs/msiinstaller.md) 와 [설치 프로그램](../../../02-artifacts/system-account/uninstall.md) 에서 찾습니다.
- 감사 정책을 바꿨는지는 [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 봅니다.
- 이런 일에 남는 이벤트 ID 는 각 페이지의 설명을 따릅니다.
- 로그를 지운 흔적은 [이벤트 로그를 지웠나 (Log Clearing)](log-clearing.md) 에서 다룹니다.

## 분석 흐름

1. [설치 프로그램](../../../02-artifacts/system-account/uninstall.md) 에서 어떤 보안 프로그램이 있었는지 봅니다.
2. 로그 폴더에서 Defender 운영 로그를 채널 이름으로 찾습니다. 첫 레코드의 기록 시각을 적어 로그가 언제부터 남아 있는지 확인합니다.
3. 5001 과 5000 을 짝지어 실시간 보호가 꺼져 있던 구간을 표로 만듭니다.
4. 5004·5007 에서 바뀐 설정과 바뀌기 전후 값을 읽습니다. 5010·5012 로 검사 기능이 꺼진 기록도 봅니다.
5. 5013 을 찾아 변조 방지가 막은 시도를 적습니다.
6. 꺼진 구간 앞뒤에서 5008·3002·5101 을 찾습니다. 오류나 만료로 멈춘 구간을 따로 표시합니다.
7. 1116·1117·1118 을 시각 순서로 놓습니다. 1117 의 Action 이 Allow·No action 인 탐지를 따로 봅니다. 1013 으로 탐지 기록을 지운 때도 찾습니다.
8. 3~7 단계에서 찾은 시각마다 그 시각의 로그온 세션을 [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) 에서 찾습니다.
9. 같은 무렵 실행한 프로그램과 명령을 [프로세스 생성](../../../02-artifacts/event-logs/4688.md)·[프리패치](../../../02-artifacts/execution/prefetch/index.md)·[PowerShell 실행 기록](../../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md) 에서 찾습니다.
10. 서비스 변경, 프로그램 삭제, 로그 지우기를 각 페이지를 따라 확인합니다.
11. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다. 보호가 꺼진 구간과 탐지 기록을 한 타임라인에 놓습니다.

## 흔한 오판

1. **5001 이 있으니 사람이 일부러 껐다고 봅니다.** 5001 은 실시간 보호가 꺼졌다는 기록입니다[1]. 누가 무엇으로 껐는지는 그 시각의 로그온 세션과 실행 기록으로 따로 확인합니다. 플랫폼이 만료돼도 보호가 꺼집니다(5101)[1].
2. **5013 을 설정이 바뀐 기록으로 읽습니다.** 5013 은 변조 방지가 설정 변경을 막은 기록입니다[1].
3. **기호 이름으로 이벤트를 거릅니다.** 문서에서 5013 과 1002 의 기호 이름이 같습니다[1]. 이벤트 ID 로 거릅니다.
4. **1116 이 있으니 위협을 치료했다고 봅니다.** 뒤따르는 1117 의 Action 을 봅니다. Allow·No action 은 위협을 치료하지 않습니다[1].
5. **탐지 이벤트가 없으니 탐지가 없었다고 봅니다.** Allow 는 이후 탐지 이벤트를 억누릅니다[1]. 1013 이 있으면 그 전에 탐지 기록을 지운 것입니다[1].
6. **지금 설정이 정상이니 바뀐 적이 없다고 봅니다.** Defender 는 악성코드를 탐지하면 악성코드가 바꿨을 수 있는 설정을 되돌립니다[1]. 5007 로 바뀐 이력을 봅니다.
7. **1150·1151 이 없으니 Defender 가 멈춰 있었다고 봅니다.** 이 보고는 모니터링 플랫폼에 보고하는 환경을 전제로 합니다[1]. 처음부터 남지 않는 환경일 수 있습니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 악성코드를 숨기려고 백신을 껐습니다."
- 쓸 문장: "Microsoft Defender 운영 로그에 5001(실시간 보호 꺼짐) 이벤트가 ○○(UTC) 에, 5000(실시간 보호 켜짐) 이벤트가 ○○(UTC) 에 있습니다. 이 기록은 두 시각 사이 약 ○시간 동안 실시간 보호가 꺼져 있었음을 보여 줍니다. 같은 구간에 엔진 오류(5008)나 플랫폼 만료(5101) 이벤트는 없습니다. 5001 무렵 ○○\○○ 계정의 로그온 세션이 있고, ○○ 프로그램을 실행한 기록이 있습니다. 실시간 보호를 끈 이유는 이 기록만으로 알 수 없습니다."

## 함께 볼 페이지

- [Windows Defender 탐지](../../../02-artifacts/event-logs/1116-1117.md) — 1116·1117 탐지·조치 이벤트의 구조입니다.
- [디펜더 검사 로그·격리 파일](../../../02-artifacts/execution/mplog-detectionhistory-quarantine.md) — 이벤트 로그 밖에 남는 탐지·격리 기록입니다.
- [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md) · [프로그램 설치·삭제 이벤트](../../../02-artifacts/event-logs/msiinstaller.md) · [설치 프로그램](../../../02-artifacts/system-account/uninstall.md) — 보안 프로그램을 멈추거나 지운 흔적입니다.
- [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) — 로그가 남는 조건입니다.
- [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) · [프로세스 생성](../../../02-artifacts/event-logs/4688.md) · [PowerShell 실행 기록](../../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md) — 보호를 끈 시각의 계정과 명령을 잇는 기록입니다.
- [이벤트 로그를 지웠나 (Log Clearing)](log-clearing.md) — 보호를 끈 뒤 로그를 지웠는지 봅니다.
- [악성코드는 어디서 들어왔나](../../incident/initial-access.md) · [랜섬웨어는 언제 어떻게 퍼졌나](../../incident/ransomware.md) — 침해 조사에서 보호가 꺼진 구간을 함께 봅니다.
- [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) — 꺼진 구간과 탐지 기록을 한 줄로 정리합니다.

## 참고 문헌

1. Microsoft Learn, "Microsoft Defender Antivirus event IDs and error codes" — https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus
2. libyal libevtx, "Windows XML Event Log (EVTX) format" — https://raw.githubusercontent.com/libyal/libevtx/main/documentation/Windows%20XML%20Event%20Log%20(EVTX).asciidoc
