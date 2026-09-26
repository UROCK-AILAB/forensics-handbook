---
title: "원격 제어 프로그램으로 누가 조작했나"
parent: "시나리오 · 침해 사고"
nav_order: 3710
---

# 원격 제어 프로그램으로 누가 조작했나 (Remote Access Tool Abuse)

이 페이지는 원격 제어 프로그램으로 누군가 이 PC 를 조작했는지 확인하는 순서를 다룹니다. 어떤 도구가 있었는지, 언제 누가 접속했는지를 먼저 찾습니다. 그다음 접속 구간 안의 행위가 원격 쪽이 한 일인지, 현장 사용자가 한 일인지를 구분합니다. 도구별 로그 위치와 필드는 [원격 제어 프로그램](../../02-artifacts/network/remote-access-tools/index.md) 과 그 하위 페이지에 있습니다.

## 조사 질문

- 이 PC 에 어떤 원격 제어 프로그램이 있었습니까? 설치형입니까, 설치 없이 도는 휴대용입니까?
- 그 도구는 조직이 승인한 도구입니까?
- 언제, 어느 원격 ID 나 계정에서 접속했습니까?
- 접속 구간 안에서 어떤 프로그램이 실행되고 어떤 파일이 생겼습니까?
- 그 행위는 원격 쪽이 했습니까, 현장 사용자가 했습니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| Windows 버전 | 버전과 빌드를 [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 적습니다. |
| 시간대 | 도구 로그, 이벤트 로그, 파일 시스템의 시각을 한 기준으로 맞춥니다. [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽습니다. 도구 로그의 시각 기준은 [원격 제어 프로그램](../../02-artifacts/network/remote-access-tools/index.md) 의 "시각을 읽을 때" 에서 확인합니다. |
| 승인된 도구 목록 | 네트워크에서 쓰는 원격 관리 도구를 조사해 승인된 것을 가려냅니다[2]. 조직에서 승인 목록과 헬프데스크 접속 기록을 먼저 받습니다. |
| 사용자·권한 | 휴대용 실행 파일은 관리자 권한 없이 사용자 권한으로 돕니다[2]. 어느 계정의 세션에서 실행됐는지 적습니다. [사용자 프로필 목록](../../02-artifacts/system-account/profilelist.md) 으로 프로필을 짝지어 둡니다. |
| 감사 정책·Sysmon | 프로세스 생성 기록(4688·Sysmon 1)이 없으면 부모·자식 관계를 보기 어렵습니다. 설정에 따라 기록이 남지 않을 수 있으므로 [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 먼저 확인합니다. |
| 수집 범위 | 도구의 설치 폴더와 로그 폴더, 사용자 프로필 안의 도구 폴더, SYSTEM·SOFTWARE 하이브, 이벤트 로그, SRUM 을 확보합니다. |

## 원격 접속 도구 악용 기법 (T1219)

MITRE ATT&CK 의 T1219 Remote Access Tools 는 공격자가 정상 원격 접속 도구로 네트워크 안에 대화형 명령·제어 통로를 만드는 기법입니다[1]. 그래픽 화면, 명령줄, 개발·관리 소프트웨어의 터널, KVM over IP 같은 하드웨어 접속이 모두 여기에 듭니다[1]. 하위 기법은 T1219.001 IDE Tunneling, T1219.002 Remote Desktop Software, T1219.003 Remote Access Hardware 입니다[1].

이런 도구에는 AnyDesk, PuTTY, TeamViewer, Ammyy Admin, VNC, ConnectWise Control, MeshCentral, LogMeIn, ngrok 등이 있습니다[1]. 원격 접속 모듈이 다른 소프트웨어 안에 들어 있기도 한데, 예를 들면 Google Chrome 의 원격 데스크톱입니다[1]. 설치 과정은 흔히 Windows 서비스로 지속성을 만듭니다[1].

**탐지 사슬을 흔적으로 옮기기.** 탐지 사슬은 네 단계입니다[1]. 아래 표는 각 단계를 받는 PC 의 흔적과 짝지은 것입니다.

| 단계 (MITRE) | 받는 PC 에서 볼 흔적 | 링크 |
|---|---|---|
| 1. 사용자 권한으로 원격 제어 에이전트나 화면을 실행 | 도구 실행 흔적 | [프리페치](../../02-artifacts/execution/prefetch/index.md) · [AmCache](../../02-artifacts/execution/amcache-hve/index.md) · [프로세스 생성 (Sysmon 1)](../../02-artifacts/event-logs/sysmon/1.md) |
| 2. 서비스·자동실행으로 지속성 | 서비스 설치 이벤트, 프로그램 설치 이벤트 | [서비스 설치](../../02-artifacts/event-logs/7045-4697.md) · [프로그램 설치·삭제 이벤트](../../02-artifacts/event-logs/msiinstaller.md) · [악성코드 지속성(자동실행) 찾기](persistence.md) |
| 3. 외부로 오래 이어지는 연결·터널 | 네트워크 연결·DNS 질의 이벤트, 앱별 네트워크 사용량 | [네트워크 연결·DNS 질의 (Sysmon 3·22)](../../02-artifacts/event-logs/sysmon/3-22.md) · [네트워크 사용량](../../02-artifacts/execution/system-resource-usage-monitor/network-data-usage.md) |
| 4. 셸·파일 관리자 같은 자식 프로세스로 드러나는 대화형 조작 | 원격 도구 프로세스를 부모로 둔 프로세스 | [프로세스 생성 (Sysmon 1)](../../02-artifacts/event-logs/sysmon/1.md) · [프로세스 생성](../../02-artifacts/event-logs/4688.md) |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 설치 흔적 | 설치형 도구의 설치 시각과 서비스 | [설치 프로그램](../../02-artifacts/system-account/uninstall.md) · [서비스·드라이버](../../02-artifacts/persistence/services-drivers.md) · [서비스 설치](../../02-artifacts/event-logs/7045-4697.md) |
| 2 | 실행 흔적 | 휴대용 도구를 포함한 도구 실행 | [프리페치](../../02-artifacts/execution/prefetch/index.md) · [AmCache](../../02-artifacts/execution/amcache-hve/index.md) |
| 3 | 도구 자체 로그 | 접속 구간, 원격 쪽 ID | [팀뷰어](../../02-artifacts/network/remote-access-tools/teamviewer.md) · [애니데스크](../../02-artifacts/network/remote-access-tools/anydesk.md) · [스크린커넥트](../../02-artifacts/network/remote-access-tools/screenconnect.md) · [기타 원격 제어 도구](../../02-artifacts/network/remote-access-tools/rustdesk-splashtop-chrome-remote-desktop.md) |
| 4 | 네트워크 흔적 | 외부 연결이 이어진 구간 | [네트워크 연결·DNS 질의 (Sysmon 3·22)](../../02-artifacts/event-logs/sysmon/3-22.md) · [네트워크 사용량](../../02-artifacts/execution/system-resource-usage-monitor/network-data-usage.md) |
| 5 | 프로세스 생성 | 구간 안의 행위와 부모 프로세스 | [프로세스 생성 (Sysmon 1)](../../02-artifacts/event-logs/sysmon/1.md) · [프로세스 생성](../../02-artifacts/event-logs/4688.md) |
| 6 | 다운로드 흔적 | 도구를 받은 경로 | [이 파일은 어디서 왔나](../activity/file-origin.md) |

1~2 로 도구가 있었는지 확인합니다. 3~4 로 접속 구간을 만듭니다. 5 로 구간 안의 행위를 확인합니다. 6 은 도구가 처음 들어온 길을 봅니다.

## 설치형과 휴대용

**설치형.**

- 설치형 도구는 흔히 서비스를 남깁니다[1]. 서비스 설치 이벤트와 서비스 키로 설치 시각과 실행 경로를 봅니다.
- 공개 사례에서 서비스로 남은 원격 관리 도구는 [악성코드 지속성(자동실행) 찾기](persistence.md) 의 "공개 사례에서 본 지속성" 에 있습니다.
- 설치 폴더, 서비스 명령줄, 중계 서버 같은 세부는 [스크린커넥트](../../02-artifacts/network/remote-access-tools/screenconnect.md) 에 있습니다.

**휴대용.**

휴대용 (portable) 실행 파일은 설치 없이 사용자 권한으로 돕니다[2]. 이 방식은 관리자 권한이 필요 없어서, 설치를 감사·차단하는 통제가 있어도 승인되지 않은 소프트웨어가 돌 수 있습니다[2]. 원격 관리 프로그램 실행 로그에서 휴대용 실행 파일로 돈 비정상 사용을 찾습니다[2].

휴대용 도구는 서비스나 설치 이벤트를 남기지 않을 수 있으므로, 실행 흔적(프리페치·AmCache·4688·Sysmon 1)과 다운로드 흔적으로 찾습니다.

## 공개 사례에서 본 원격 조작

CISA 권고 AA23-025A 에서 공격자는 ScreenConnect(지금 이름 ConnectWise Control)와 AnyDesk 를 썼습니다[2]. 공격자는 피해자 PC 에 접속해 피해자가 은행 계좌에 로그인하게 한 뒤, 계좌 요약 화면을 고쳐 가짜 환불을 보여 주고 돈을 돌려보내게 했습니다(환불 사기)[2]. 이 사례에서는 현장 사용자와 원격 쪽이 같은 세션에서 함께 움직였기 때문에, "원격 쪽만" 또는 "사용자만" 으로 나눌 수 없는 행위도 있습니다.

The DFIR Report 사례(2023-09-25)에서 ScreenConnect 는 스크립트를 디스크에 떨군 뒤 명령 프롬프트나 PowerShell 로 실행했고, 이 흔적은 Sysmon 11(파일 생성)과 1(프로세스 생성)에 드러났습니다[3]. 같은 사례에서 원격 관리 도구로 실행한 발견 명령은 [스크린커넥트](../../02-artifacts/network/remote-access-tools/screenconnect.md) 에 있습니다.

## 원격 조작과 현장 사용자 가르기

행위 하나를 "원격 쪽이 했다" 고 쓰려면 아래를 차례로 맞춥니다.

1. **원격 세션 구간을 만듭니다.** 도구 로그에서 접속 시작·끝 시각과 원격 쪽 ID 를 뽑습니다. 네트워크 흔적으로 외부 연결이 이어진 구간을 맞춥니다.
2. **행위 시각을 구간과 겹쳐 봅니다.** 구간 밖의 행위는 원격 쪽이 했다고 쓰지 않습니다.
3. **행위 프로세스의 부모를 봅니다.** 원격 도구 프로세스의 자식이면 위 탐지 사슬의 4단계와 맞는 모양입니다[1]. 부모가 탐색기 같은 일반 셸이면 다른 근거를 더 찾습니다.
4. **원격 쪽 ID 를 승인 목록과 맞춥니다.** 헬프데스크가 쓰는 ID 인지 확인합니다.
5. **현장 사용자의 흔적을 함께 봅니다.** 같은 시각에 그 계정을 누가 쓰고 있었는지는 [그 시각에 PC 를 쓴 사람이 누구인가](../activity/user-attribution.md) 를 따라 좁힙니다.

## 분석 흐름

1. Windows 버전·시간대·사용자를 정리합니다. 조직에서 승인된 원격 도구 목록과 헬프데스크 기록을 받습니다.
2. 설치형 도구를 찾습니다. 설치 프로그램 목록, 서비스, 서비스 설치 이벤트, 프로그램 설치 이벤트를 봅니다.
3. 휴대용 도구를 찾습니다. 실행 흔적과 다운로드 흔적에서 원격 도구의 이름과 해시를 찾습니다.
4. 도구 자체 로그에서 접속 구간과 원격 쪽 ID 를 뽑습니다.
5. 네트워크 연결 이벤트와 [네트워크 사용량](../../02-artifacts/execution/system-resource-usage-monitor/network-data-usage.md) 으로 외부 연결이 이어진 구간을 맞춥니다.
6. 구간 안의 프로세스 생성과 파일 생성을 봅니다. 부모가 원격 도구 프로세스인지 확인합니다.
7. 위 "원격 조작과 현장 사용자 가르기" 다섯 가지를 행위마다 적습니다.
8. 도구가 처음 들어온 길은 [악성코드는 어디서 들어왔나](initial-access.md) 로, 서비스로 남은 지속성은 [악성코드 지속성(자동실행) 찾기](persistence.md) 로 이어 갑니다.

## 흔한 오판

1. **회사에서 쓰는 정상 원격 도구라 문제없다고 봅니다.** 공개 사례와 권고 모두 정상 원격 관리 도구를 악용한 경우입니다[1][2][3].
2. **설치 기록이 없으니 원격 도구는 쓰지 않았다고 봅니다.** 휴대용 실행 파일은 설치 없이 돕니다[2].
3. **원격 도구 접속이 있었으니 공격자가 했다고 봅니다.** 사용자가 직접 부른 헬프데스크 접속일 수 있습니다. 원격 쪽 ID 와 상대를 확인합니다.
4. **도구 로그가 없으니 접속이 없었다고 봅니다.** 로그 파일을 지웠을 수 있습니다. 서비스·실행·네트워크 흔적과 [지운 파일의 흔적 찾기](../activity/deleted-file-traces.md) 로 따로 봅니다.

## 보고서 문장 예

- 쓰지 않을 문장: "공격자가 ○○ 로 원격 접속해 ○○ 파일을 실행했습니다."
- 쓸 문장: "○○ 의 로그에 ○○(UTC) 부터 ○○(UTC) 까지 원격 ID ○○ 의 접속 기록이 있습니다. 같은 구간에 ○○.exe 의 프로세스 생성 기록이 있습니다. 이 프로세스의 부모는 ○○ 입니다. 이 기록은 이 구간에 원격 제어 프로그램의 자식 프로세스로 이 파일이 실행됐음을 보여 줍니다. 원격 ID ○○ 를 쓴 사람이 누구인지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [원격 제어 프로그램](../../02-artifacts/network/remote-access-tools/index.md) — 도구별 흔적의 길잡이입니다.
- [팀뷰어](../../02-artifacts/network/remote-access-tools/teamviewer.md) · [애니데스크](../../02-artifacts/network/remote-access-tools/anydesk.md) · [스크린커넥트](../../02-artifacts/network/remote-access-tools/screenconnect.md) · [기타 원격 제어 도구](../../02-artifacts/network/remote-access-tools/rustdesk-splashtop-chrome-remote-desktop.md) — 도구 자체 로그의 위치와 필드입니다.
- [서비스 설치](../../02-artifacts/event-logs/7045-4697.md) · [프로그램 설치·삭제 이벤트](../../02-artifacts/event-logs/msiinstaller.md) — 설치형 도구의 흔적입니다.
- [프로세스 생성 (Sysmon 1)](../../02-artifacts/event-logs/sysmon/1.md) · [네트워크 연결·DNS 질의 (Sysmon 3·22)](../../02-artifacts/event-logs/sysmon/3-22.md) — 실행과 연결을 봅니다.
- [프리페치](../../02-artifacts/execution/prefetch/index.md) · [AmCache](../../02-artifacts/execution/amcache-hve/index.md) · [네트워크 사용량](../../02-artifacts/execution/system-resource-usage-monitor/network-data-usage.md) — 휴대용 도구의 흔적입니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](../activity/user-attribution.md) — 계정에서 사람으로 좁힙니다.
- [악성코드 지속성(자동실행) 찾기](persistence.md) · [악성코드는 어디서 들어왔나](initial-access.md) — 앞뒤 단계를 봅니다.

## 참고 문헌

1. MITRE ATT&CK, "Remote Access Tools, Technique T1219" (v3.0, 2026-05-12 수정) — https://attack.mitre.org/techniques/T1219/
2. CISA, "Protecting Against Malicious Use of Remote Monitoring and Management Software" (AA23-025A, 2023-01-26 마지막 수정) — https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-025a
3. The DFIR Report, "From ScreenConnect to Hive Ransomware in 61 hours" (2023-09-25) — https://thedfirreport.com/2023/09/25/from-screenconnect-to-hive-ransomware-in-61-hours/
