# 증거를 없애려 했나 (Anti-Forensics)

## 한 줄 요약

안티포렌식 (Anti-Forensics) 은 조사에 쓰일 기록을 없애거나 흐리는 행위입니다. 이 허브는 이벤트 로그 지우기, 완전삭제, PC 초기화, 시각 바꾸기, 보안 프로그램 끄기를 찾는 조사 다섯 가지를 묶습니다.

## 왜 중요한가

지우거나 끄는 행위도 또 다른 기록을 남깁니다.

- 보안 로그를 지우면 1102 가 남습니다[1].
- 완전삭제 도구 SDelete 는 파일 내용을 덮어쓰고 이름을 바꾼 뒤 지웁니다[3]. 이름을 바꾼 기록은 USN 변경 저널에 남습니다[4].
- Defender 의 실시간 보호가 꺼지면 5001 이, 설정이 바뀌면 5007 이 운영 로그에 남습니다[8].
- "내 파일 유지" 로 PC 를 초기화해도 옛 AppData 폴더는 `C:\Windows.old` 에서 볼 수 있습니다[5].

시각 바꾸기는 다른 기록의 시각까지 흔듭니다. Microsoft 문서는 시스템 시각을 바꾸면 이벤트 로그 항목과 파일의 타임스탬프가 틀어질 수 있다고 적습니다[7]. 그래서 어떤 조사든 시각을 바꾼 기록부터 확인해 두면 뒤의 판단이 흔들리지 않습니다.

증명하지 못하는 것도 분명합니다.

- 이 기록들은 행위를 보여 줍니다. 왜 했는지는 보여 주지 않습니다.
- 정상 작업이나 오류도 같은 기록을 남깁니다. LOCAL SERVICE 계정이 남긴 4616 은 보통 보이는 정상 시각 보정입니다[6]. Defender 플랫폼이 만료돼도 보호가 꺼집니다[8].
- 기록에 남는 것은 계정입니다. 그 계정을 쓴 사람은 [그 시각에 PC 를 쓴 사람이 누구인가](/04-scenarios/activity/user-attribution.md) 를 따라 따로 확인합니다.
- 흔적이 없다고 해서 행위가 없었다고 단정하지 않습니다. 흔적이 없으면 그 흔적을 담은 로그를 지웠는지부터 봅니다.

## 한눈에 보기

| 행위 | 볼 곳 | Windows 버전 | 알려 주는 것 |
|---|---|---|---|
| [이벤트 로그 지우기](/04-scenarios/activity/anti-forensics/log-clearing.md) | 보안 로그의 1102[1]. System 로그를 지운 분석 예에서는 지운 로그 맨 앞의 104[2] | 1102 는 Windows Vista·Server 2008 부터[1] | 로그를 지운 때와 지운 계정 |
| [완전삭제 도구](/04-scenarios/activity/anti-forensics/wiping-tools.md) | 프리패치·UserAssist·사용자 하이브, USN 변경 저널[4] | 도구마다 다름. SDelete 는 Windows 10·Server 2012 이상에서 돕니다[3] | 도구를 실행한 때, 지울 파일의 이름을 바꾼 기록 |
| [초기화·재설치](/04-scenarios/activity/anti-forensics/reset-reinstall.md) | 새로 만든 `\Windows`·`\Program Files`·`\ProgramData`·각 사용자 AppData, `C:\Windows.old`[5] | Windows 10·11[5] | 초기화 옵션, 초기화 전 기록이 남은 곳 |
| [시각 바꾸기](/04-scenarios/activity/anti-forensics/system-time-change.md) | 보안 로그의 4616. 감사 설정과 상관없이 항상 남습니다[6] | Windows Vista·Server 2008 부터[6] | 바뀌기 전후 시각, 바꾼 계정과 프로세스 |
| [보안 프로그램 끄기](/04-scenarios/activity/anti-forensics/defense-evasion.md) | `Microsoft-Windows-Windows Defender/Operational` 채널의 5001·5007·5013[8] | 이번 자료로 확인하지 못함 | 실시간 보호가 꺼진 구간, 바뀐 설정, 막힌 변경 시도 |

### 어느 경우든 같이 볼 기록

- 도구를 실행한 흔적은 도구 종류와 상관없이 같이 봅니다. [프리패치](/02-artifacts/execution/prefetch/index.md)·[UserAssist](/02-artifacts/execution/userassist.md)·[프로세스 생성 (4688)](/02-artifacts/event-logs/4688.md) 이 여기에 듭니다.
- JPCERT/CC 분석에서는 SDelete 와 wevtutil 모두 프리패치와 4688 로 실행을 확인했습니다[2][4].
- 행위를 찾으면 그 시각의 로그온 세션을 [로그온·로그오프](/02-artifacts/event-logs/logon-events/index.md) 에서 찾습니다.
- 모든 시각을 UTC 하나로 맞춰 [타임라인](/03-techniques/analysis/timeline/index.md) 에 놓습니다. 시각을 바꾼 기록이 있으면 틀어진 구간을 타임라인에 표시합니다.

## 읽는 순서

1. [이벤트 로그를 지웠나 (Log Clearing)](/04-scenarios/activity/anti-forensics/log-clearing.md) — 1102·104 로 로그를 지운 때와 계정을 찾습니다. 원격에서 지운 경우와 지운 뒤 .evtx 파일에서 레코드를 되살리는 법도 다룹니다.
2. [완전삭제 도구를 썼나 (Wiping Tools)](/04-scenarios/activity/anti-forensics/wiping-tools.md) — SDelete 와 `cipher /w` 를 예로 도구 실행 기록과 파일 이름을 바꾼 기록을 찾습니다. 파일을 골라 지웠는지, 빈 공간을 지웠는지도 가립니다.
3. [PC 를 초기화하거나 윈도를 다시 깔았나 (Reset·Reinstall)](/04-scenarios/activity/anti-forensics/reset-reinstall.md) — 초기화 옵션마다 남는 것과 지워지는 것을 정리합니다. `C:\Windows.old` 와 OS 가 아닌 파티션에서 초기화 전 기록을 찾습니다.
4. [시스템 시각을 바꿨나 (System Time Change)](/04-scenarios/activity/anti-forensics/system-time-change.md) — 4616 으로 누가 어느 프로세스로 시각을 바꿨는지 가립니다. 정상 시각 보정과 나누고, 시각이 틀어진 구간을 표시합니다.
5. [보안 프로그램을 끄거나 지웠나 (Defense Evasion)](/04-scenarios/activity/anti-forensics/defense-evasion.md) — Defender 운영 로그로 실시간 보호가 꺼진 구간과 바뀐 설정을 찾습니다. 사람이 끈 것과 오류로 멈춘 것을 나눕니다.

## 함께 볼 페이지

- [이벤트 로그 삭제 (1102·104)](/02-artifacts/event-logs/1102-104.md) · [시간 변경 (4616)](/02-artifacts/event-logs/4616-kernel-general.md) · [Windows Defender 탐지 (1116·1117)](/02-artifacts/event-logs/1116-1117.md) — 각 이벤트의 구조입니다.
- [USN 변경 저널](/02-artifacts/filesystem/usnjrnl.md) · [마스터 파일 테이블](/02-artifacts/filesystem/mft.md) — 파일 이름을 바꾸고 지운 기록입니다.
- [감사 정책과 로그 설정](/02-artifacts/event-logs/audit-policy-log-settings.md) — 이벤트가 남는 조건입니다.
- [지운 파일의 흔적 찾기](/04-scenarios/activity/deleted-file-traces.md) · [삭제 데이터 복구](/03-techniques/analysis/data-recovery/index.md) · [섀도 복사본 활용](/03-techniques/analysis/volume-shadow-copy-analysis.md) — 지운 데이터와 지우기 전 파일을 찾습니다.
- [시스템 기본 정보](/02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) — OS 버전과 설치 날짜를 봅니다.
- [이 문서의 날짜를 믿을 수 있나](/04-scenarios/activity/document-date-verification.md) — 시각이 틀어졌을 때 문서 날짜를 따로 따집니다.
- [어떤 프로그램을 언제 실행했나](/04-scenarios/activity/program-execution.md) — 도구 실행 기록을 찾는 순서입니다.

## 참고 문헌

1. Microsoft Learn, "1102(S) The audit log was cleared." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-1102
2. JPCERT/CC, Tool Analysis Result Sheet, "wevtutil" — https://jpcertcc.github.io/ToolAnalysisResultSheet/details/wevtutil.htm
3. Microsoft Learn (Sysinternals), "SDelete" — https://learn.microsoft.com/en-us/sysinternals/downloads/sdelete
4. JPCERT/CC, Tool Analysis Result Sheet, "sdelete" — https://jpcertcc.github.io/ToolAnalysisResultSheet/details/sdelete.htm
5. Microsoft Learn, "How push-button reset features work" — https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/how-push-button-reset-features-work
6. Microsoft Learn, "4616(S) The system time was changed." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4616
7. Microsoft Learn, "Change the system time - security policy setting" — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/change-the-system-time
8. Microsoft Learn, "Microsoft Defender Antivirus event IDs and error codes" — https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus
