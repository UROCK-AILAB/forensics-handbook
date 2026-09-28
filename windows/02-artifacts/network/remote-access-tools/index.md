---
title: "원격 제어 프로그램"
parent: "아티팩트 · 네트워크"
nav_order: 2370
has_children: true
has_toc: false
---

# 원격 제어 프로그램 (Remote Access Tools)

원격 제어 프로그램 (Remote Access Tools) 은 멀리 있는 사람이 이 PC 의 화면을 보고 조작하게 해 주는 원격 지원 프로그램입니다. 설치형은 서비스를 등록하고, 도구마다 전용 로그 파일이나 전용 이벤트 로그에 접속 기록을 남깁니다. 이 허브는 TeamViewer, AnyDesk, ScreenConnect, RustDesk, Splashtop, Chrome Remote Desktop 의 흔적을 어디서 찾는지 안내합니다.

## 왜 중요한가

정상 프로그램이지만 공격자도 자주 씁니다. 그래서 이런 도구를 "합법 원격 접속 도구 (Legitimate RATs)" 로 부르기도 합니다[1]. 공격자가 ScreenConnect 로 들어온 뒤 61시간 만에 Hive 랜섬웨어를 실행한 사건도 있습니다[2].

도구마다 접속을 적는 전용 로그가 따로 있고, 이 로그가 "누가 언제 들어왔나" 에 답하는 주된 근거입니다. 받는 쪽 PC 와 거는 쪽 PC 에 남는 흔적이 다르므로, 조사하는 PC 가 어느 쪽인지 정해야 볼 곳이 정해집니다.

증명하지 못하는 것도 분명합니다.

- 도구가 남기는 ID·호스트 이름·IP 는 사람을 가리키지 않습니다. 조작한 사람을 특정하려면 다른 근거가 필요합니다.
- 전용 로그에 세션 중에 한 일이 모두 남지는 않습니다. 도구마다 무엇이 빠지는지는 하위 페이지에서 다룹니다.
- 전용 텍스트 로그의 시간대는 같은 접속의 이벤트 로그 시각과 맞춰 보고 확인합니다.
- 설치하지 않고 실행한 경우에는 서비스 설치 기록에 기대지 못합니다.

## 한눈에 보기

> 그림 자리: 받는 쪽 PC(조종당한 PC)와 거는 쪽 PC(조종한 PC)를 나란히 두고, 도구별로 어느 쪽에 어떤 파일·이벤트가 남는지 보여 주는 그림

### 받는 쪽과 거는 쪽

받는 쪽은 원격으로 조종당한 PC 이고, 거는 쪽은 조종한 PC 입니다. 흔적이 한쪽에만 생기는 파일도 있어서, TeamViewer 의 `Connections_incoming.txt` 와 AnyDesk 의 `connection_trace.txt` 는 받는 쪽에만 생깁니다. 설치하지 않고 실행하는 방식(휴대용)도 있는데, 이때는 로그 위치가 달라질 수 있습니다. TeamViewer 의 예는 [팀뷰어](teamviewer.md)에서 봅니다.

### 도구별 먼저 볼 흔적

| 도구 | 먼저 볼 흔적 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| TeamViewer | 설치 폴더의 `TeamViewer15_Logfile.log`, `Connections_incoming.txt` | 상대 TeamViewer ID, 접속 시작·끝 시각, 로컬 사용자 | [팀뷰어](teamviewer.md) |
| AnyDesk | `%ProgramData%\AnyDesk\connection_trace.txt`, `ad_svc.trace`, `%AppData%\AnyDesk\ad.trace` | 들어온 접속과 승인 방식, 상대 ID, 외부 IP | [애니데스크](anydesk.md) |
| ScreenConnect | Application 로그의 `ScreenConnect Client (<16진 문자열>)` 원본 이벤트, `C:\Windows\Temp\ScreenConnect\<버전>\` 의 스크립트 | 세션 시작·끝, 파일 전송, 명령 실행 | [스크린커넥트](screenconnect.md) |
| Splashtop | 전용 이벤트 로그 두 개, `SPLog.txt`, `FTCLog.txt` | 상대 호스트 이름과 공인 IP, 파일 전송 | [기타 원격 제어 도구](rustdesk-splashtop-chrome-remote-desktop.md) |
| RustDesk | `%AppData%\RustDesk\log\` 아래 로그 | 이 PC 에서 RustDesk 가 돈 흔적. 로그 형식은 파일을 열어 확인 | [기타 원격 제어 도구](rustdesk-splashtop-chrome-remote-desktop.md) |
| Chrome Remote Desktop | 서비스 이름 chromoting, 이벤트 ID 1~6 | 접속·끊김·거부, 상대 IP | [기타 원격 제어 도구](rustdesk-splashtop-chrome-remote-desktop.md) |

### 여러 도구에 공통으로 남는 흔적

| 흔적 | 내용 | 자세히 |
|---|---|---|
| 서비스 설치 (System 7045) | 설치형은 서비스를 등록하므로 7045 가 남습니다. TeamViewer·AnyDesk·Splashtop·ScreenConnect 모두 7045 가 남습니다[1][2][3] | [서비스 설치](../../event-logs/7045-4697.md) |
| 서비스 설치 (Security 4697) | 감사 정책이 켜져 있으면 남습니다. AnyDesk 도 4697 이 남습니다[3] | [서비스 설치](../../event-logs/7045-4697.md), [감사 정책과 로그 설정](../../event-logs/audit-policy-log-settings.md) |
| Sigma 규칙 | "Remote Access Tool Services Have Been Installed" 는 System 7045·7036 에서 서비스 이름에 TeamViewer, SplashtopRemoteService, SSUService, chromoting 등이 든 것을 찾습니다. 같은 이름의 Security 판 규칙은 4697 에서 찾고, 목록에 AnyDesk 도 들어 있습니다[4] | [이벤트 로그 규칙 검색](../../../03-techniques/analysis/sigma-rules.md) |
| 실행 흔적 | 프리페치 외에 BAM, UserAssist, 심캐시, AmCache, 점프 목록에도 남습니다. AnyDesk·Splashtop 에서 이런 흔적이 남습니다[1] | [프리페치](../../execution/prefetch/index.md), [BAM·DAM](../../execution/background-activity-moderator.md), [UserAssist](../../execution/userassist.md), [심캐시](../../execution/shimcache-appcompatcache.md), [AmCache](../../execution/amcache-hve/index.md), [점프리스트](../../file-folder-usage/jump-lists.md) |
| DNS·프록시 기록 | 도구마다 접속하는 도메인이 있습니다. DNS·프록시 기록에서 찾을 단서가 됩니다. 도메인 목록은 하위 페이지에 있습니다 | 각 하위 페이지 |

### 자료 기준

이 흔적은 도구 버전에 따라 경로와 문구가 달라질 수 있습니다. 하위 페이지는 아래 자료를 기준으로 합니다.

| 자료 | 날짜 | 범위 |
|---|---|---|
| Synacktiv, "Legitimate RATs" | 2022-10-20 | TeamViewer·AnyDesk·Splashtop 을 Windows 에서 시험했습니다. 기본 로그 정책으로 시험했고 Sysmon 은 켜지 않았습니다. 실제 사건 현장과 비슷한 조건입니다 |
| LOLRMM 목록 | 항목별 마지막 수정일: TeamViewer 2025-12-14, AnyDesk 2023-09-29, ScreenConnect 2026-06-16, RustDesk 2024-08-02, Splashtop 2024-08-02, Chrome Remote Desktop 2026-09-01 | 원격 관리 도구의 흔적을 모은 공개 목록입니다 |
| SigmaHQ 규칙 | 2026-09-22 커밋 기준 | 탐지 규칙 |
| The DFIR Report | 2023-09-25 | ScreenConnect 로 시작한 랜섬웨어 사건 |
| Hunt & Hackett | 2021-06-10 | ScreenConnect 의 Application 이벤트 |
| RustDesk FAQ, Chromium 소스 | — | RustDesk 로그 위치, Chrome Remote Desktop 이벤트 정의 |

### 시각을 읽을 때

- 이벤트 로그의 레코드 시각을 읽는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.
- 전용 텍스트 로그는 도구마다 시간대가 다를 수 있습니다. 같은 접속을 두 기록에서 찾아 차이를 직접 잽니다. 방법은 하위 페이지마다 있습니다.
- PC 의 시간대 설정은 [시간대 설정](../../system-account/time-zone.md)에서, 여러 기록을 한 줄로 합치는 법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md)에서 봅니다.

## 읽는 순서

1. [팀뷰어 (TeamViewer)](teamviewer.md) — 설치 폴더의 동작 로그와 받은 접속 목록을 읽습니다. 두 파일의 시각 차이와 거는 쪽 레지스트리 흔적도 다룹니다.
2. [애니데스크 (AnyDesk)](anydesk.md) — `connection_trace.txt` 의 승인 방식과 trace 로그의 상대 ID·외부 IP 를 읽습니다. 설치 때 남는 28115 이벤트와 설정 파일도 다룹니다.
3. [스크린커넥트 (ScreenConnect)](screenconnect.md) — 클라이언트 서비스 명령줄의 접속 정보와 Application 로그의 세션·파일 전송·명령 실행 이벤트를 읽습니다. 자료마다 다른 이벤트 ID 도 다룹니다.
4. [기타 원격 제어 도구 (RustDesk·Splashtop·Chrome Remote Desktop)](rustdesk-splashtop-chrome-remote-desktop.md) — RustDesk 로그 위치, Splashtop 전용 이벤트 로그와 파일 전송 로그, Chrome Remote Desktop 이벤트 ID 1~6 을 정리합니다.

## 함께 볼 페이지

- [원격 제어 프로그램으로 누가 조작했나](../../../04-scenarios/incident/remote-access-tool-abuse.md) — 이 허브의 흔적을 조사 순서로 엮습니다.
- [서비스 설치](../../event-logs/7045-4697.md) · [서비스·드라이버](../../persistence/services-drivers.md) — 서비스 설치 이벤트와 서비스 레지스트리 키를 읽습니다.
- [프로세스 생성](../../event-logs/4688.md) · [Sysmon 로그](../../event-logs/sysmon/index.md) — 원격 세션에서 실행한 프로그램을 찾습니다.
- [이벤트 로그 규칙 검색](../../../03-techniques/analysis/sigma-rules.md) — 원격 제어 도구를 잡는 Sigma 규칙을 씁니다.
- [원격 데스크톱 접속 기록](../rdp-client-mru.md) · [원격 데스크톱 이벤트](../../event-logs/rdp-event-logs/index.md) — Windows 원격 데스크톱으로 들어온 접속은 여기서 다룹니다.
- [설치 프로그램](../../system-account/uninstall.md) — 설치된 원격 제어 도구 목록을 봅니다.
- [랜섬웨어는 언제 어떻게 퍼졌나](../../../04-scenarios/incident/ransomware.md) · [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) — 침해 조사에서 원격 제어 도구 흔적을 씁니다.

## 참고 문헌

1. Synacktiv, "Legitimate RATs: a comprehensive forensic analysis of the usual suspects" (Théo Letailleur, 2022-10-20). https://www.synacktiv.com/publications/legitimate-rats-a-comprehensive-forensic-analysis-of-the-usual-suspects.html
2. The DFIR Report, "From ScreenConnect to Hive Ransomware in 61 hours" (2023-09-25). https://thedfirreport.com/2023/09/25/from-screenconnect-to-hive-ransomware-in-61-hours/
3. LOLRMM API, rmm_tools.json. https://lolrmm.io/api/rmm_tools.json
4. SigmaHQ 규칙 저장소 (커밋 16eb587, 2026-09-22). rules/windows/builtin/system/service_control_manager/win_system_service_install_remote_access_software.yml, rules/windows/builtin/security/win_security_service_install_remote_access_software.yml. https://github.com/SigmaHQ/sigma
5. Hunt & Hackett, "REvil: the usage of legitimate remote admin tooling" (Krijn de Mik, 2021-06-10). https://www.huntandhackett.com/blog/revil-the-usage-of-legitimate-remote-admin-tooling
6. RustDesk GitHub 위키, FAQ. https://github.com/rustdesk/rustdesk/wiki/FAQ
7. Chromium 소스, remoting/host/win/host_messages.mc.jinja2 (HEAD). https://chromium.googlesource.com/chromium/src/+/HEAD/remoting/host/win/host_messages.mc.jinja2
