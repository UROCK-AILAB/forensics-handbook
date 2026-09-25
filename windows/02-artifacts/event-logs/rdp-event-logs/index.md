---
title: "원격 데스크톱 이벤트"
parent: "아티팩트 · 이벤트 로그"
nav_order: 2570
has_children: true
has_toc: false
---

# 원격 데스크톱 이벤트 (RDP Event Logs)

## 한 줄 요약

원격 데스크톱 이벤트 (RDP Event Logs) 는 원격 데스크톱 프로토콜 (Remote Desktop Protocol, RDP) 로 들어오고 나간 접속을 Windows 가 여러 이벤트 로그에 나눠 남긴 기록입니다. 접속을 받은 컴퓨터에는 연결·인증·세션 기록이 남고, 접속을 건 컴퓨터에는 어느 서버로 나갔는지가 남습니다.

## 왜 중요한가

한 번의 접속이 단계마다 다른 로그에 남기 때문에, 여러 로그를 맞추면 연결, 인증, 세션 로그온, 끊김, 로그오프를 차례로 이을 수 있습니다. 접속을 받은 컴퓨터 (대상) 의 기록에는 접속해 온 주소와 사용자 이름이 남고, 접속을 건 컴퓨터 (출발) 의 기록에는 연결하려던 서버가 남습니다. 두 쪽을 맞추면 한 번의 접속을 양 끝에서 확인할 수 있고, 세션 ID 와 로그온 ID 로 한 세션의 시작과 끝을 따라갈 수 있습니다.

증명하지 못하는 것도 분명합니다.

- 기록에는 계정과 주소가 남습니다. 키보드 앞에 있던 사람은 남지 않습니다.
- 이벤트 번호만으로 원격 접속이라고 할 수 없습니다. 원격 데스크톱을 받지 않는 PC 에도 같은 번호의 세션 이벤트가 남습니다 ([세션 단계](localsessionmanager-21-25-4778-4779.md)).
- 1149 의 메시지는 "사용자 인증 성공" 이지만, 이 한 건만으로 로그온했다고 쓰기 어렵습니다 ([해석 함정](1149-nla-3-10.md)).
- 세션 안에서 무엇을 했는지는 이 로그들에 남지 않습니다.
- 기록이 없다고 접속이 없었다고 할 수 없습니다. 감사 설정, 로그 크기, 로그 삭제를 먼저 확인합니다.

## 한눈에 보기

> 그림 자리: 출발 컴퓨터와 대상 컴퓨터를 나란히 그리고, 한 번의 접속이 단계마다 어느 로그에 어떤 이벤트를 남기는지 화살표로 보여 주는 그림

### 어느 컴퓨터에 어떤 로그가 남나

| 컴퓨터 | 로그 | 주요 이벤트 | 알려 주는 것 | 자세히 |
|---|---|---|---|---|
| 대상 | RemoteConnectionManager/Operational | 1149 | 원격 데스크톱 연결, 사용자·도메인·원본 주소 | [인증 단계](1149-4624-10-4625.md) |
| 대상 | RdpCoreTS/Operational | 131, 98, 140 | 연결 시도, 연결 성립, 비밀번호가 틀려 실패한 주소 | [인증 단계](1149-4624-10-4625.md) |
| 대상 | Security | 4624 (유형 10), 4625 | 로그온 성공·실패, 로그온 유형, 원본 주소 | [인증 단계](1149-4624-10-4625.md) |
| 대상 | LocalSessionManager/Operational | 21~25, 39, 40 | 세션 로그온·끊김·다시 연결·로그오프, 세션 ID, 원본 주소 | [세션 단계](localsessionmanager-21-25-4778-4779.md) |
| 대상 | Security | 4778, 4779, 4634, 4647 | 세션 다시 연결·끊김, 로그오프 | [세션 단계](localsessionmanager-21-25-4778-4779.md) |
| 대상 | System | 9009 | 연결이 정식으로 닫혔다는 표시일 수 있음 | [세션 단계](localsessionmanager-21-25-4778-4779.md) |
| 출발 | RDPClient/Operational | 1024, 1102 | 연결하려던 서버의 이름·주소 | [나간 접속](rdpclient-1024-1102.md) |
| 출발 | Security | 4648 | 명시적 자격 증명으로 로그온을 시도한 기록. 대상 서버와 계정 | [나간 접속](rdpclient-1024-1102.md) |

### 채널 이름과 파일 경로

네 채널의 파일은 모두 `%SystemRoot%\System32\Winevt\Logs\` 아래에 있습니다.

| 채널 | 파일 이름 |
|---|---|
| Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational | `Microsoft-Windows-TerminalServices-RemoteConnectionManager%4Operational.evtx` |
| Microsoft-Windows-TerminalServices-LocalSessionManager/Operational | `Microsoft-Windows-TerminalServices-LocalSessionManager%4Operational.evtx` |
| Microsoft-Windows-TerminalServices-RDPClient/Operational | `Microsoft-Windows-TerminalServices-RDPClient%4Operational.evtx` |
| Microsoft-Windows-RemoteDesktopServices-RdpCoreTS/Operational | `Microsoft-Windows-RemoteDesktopServices-RdpCoreTS%4Operational.evtx` |

파일 이름에서는 채널 이름의 `/` 자리에 `%4` 가 들어가고, 채널 이름은 JPCERT/CC 자료와 같습니다. 보안 로그 파일의 위치는 [로그온·로그오프](../logon-events/index.md) 에서 다룹니다.

아래는 원격 데스크톱 받기가 꺼진 PC 한 대에서 `wevtutil gl` 로 본 결과입니다.

- 네 채널 모두 켜져 (enabled: true) 있었습니다.
- 네 채널 모두 최대 크기가 1052672 바이트 (약 1MB) 였고, retention 은 false 였습니다.
- LocalSessionManager 파일만 폴더에 있었고, RemoteConnectionManager·RDPClient·RdpCoreTS 파일은 폴더에 없었습니다.
- 파일이 첫 이벤트를 쓸 때 만들어지는지는 확인하지 못했습니다. 그래서 파일이 없다고 곧바로 지운 흔적으로 보지 않습니다.
- LocalSessionManager 파일 (약 1MB) 에는 이벤트 227건이 있었습니다. 기간은 2026-06-26 ~ 2026-09-20 (UTC) 였습니다.
- 크기 한도가 이만큼 작으면 오래된 접속 기록은 밀려나 없을 수 있습니다.

### 단계별로 보는 이벤트

Ponder The Bits 는 들어온 접속을 다섯 단계로 나눠 정리했습니다. 이 정리는 Vista 이후만 다루고 XP 시절 이벤트는 뺐습니다. 2018-02-20 에 쓴 글입니다.

| 단계 | 이벤트 | 자세히 |
|---|---|---|
| 네트워크 연결 | 1149 | [인증 단계](1149-4624-10-4625.md) |
| 인증 | 4624, 4625 | [인증 단계](1149-4624-10-4625.md), [해석 함정](1149-nla-3-10.md) |
| 로그온 | LocalSessionManager 21, 22 | [세션 단계](localsessionmanager-21-25-4778-4779.md) |
| 끊김·다시 연결 | 24, 25, 39, 40, 4778, 4779 | [세션 단계](localsessionmanager-21-25-4778-4779.md) |
| 로그오프 | 23, 4634, 4647, System 9009 | [세션 단계](localsessionmanager-21-25-4778-4779.md) |

### Windows 버전

| 범위 | 이 허브에서 다루는 것 |
|---|---|
| XP | 다루지 않습니다. Ponder The Bits 의 정리에서도 빠져 있습니다 |
| Vista · Server 2008 이후 | 단계 정리가 다루는 범위입니다. 4778·4779 의 버전은 [세션 단계](localsessionmanager-21-25-4778-4779.md) 에서 다룹니다 |
| 8.1 · 10 | 4624 의 제한된 관리자 모드 칸이 생긴 과정은 [인증 단계](1149-4624-10-4625.md) 에서 다룹니다 |
| 11 Home 빌드 26200 (관찰) | 네 채널의 설정과 메시지 원문을 확인했습니다 |

### 시각

- 이벤트 XML 의 `TimeCreated` 요소에 있는 `SystemTime` 값은 UTC 이고 끝에 `Z` 가 붙습니다. 보고서에는 어느 시간대로 적었는지 밝힙니다.
- 출발 컴퓨터와 대상 컴퓨터의 기록을 합칠 때는 두 컴퓨터의 시계 차이를 먼저 확인합니다. 방법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 을 봅니다.
- 시각 값의 저장 형식은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 과 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 을 봅니다.

## 읽는 순서

1. [들어온 접속: 인증 단계 (1149·4624 유형 10·4625)](1149-4624-10-4625.md) — 대상 컴퓨터에 남는 연결·인증 기록의 칸을 읽습니다. RdpCoreTS 의 연결 기록도 함께 다룹니다.
2. [들어온 접속: 세션 단계 (LocalSessionManager 21~25·4778·4779)](localsessionmanager-21-25-4778-4779.md) — 세션 로그온·끊김·다시 연결·로그오프를 세션 ID 로 따라갑니다. 끊긴 이유 코드와 주소 칸 `LOCAL` 을 가르는 법도 다룹니다.
3. [나간 접속 (RDPClient 1024·1102)](rdpclient-1024-1102.md) — 출발 컴퓨터에 남는 연결 시도 기록을 읽습니다. 함께 볼 레지스트리·파일 흔적도 정리합니다.
4. [해석 함정 (1149의 뜻·NLA·유형 3과 10 구분)](1149-nla-3-10.md) — 1149 의 뜻, 네트워크 수준 인증 (NLA) 설정, 로그온 유형 3 과 10 을 함께 읽는 법을 다룹니다.

## 함께 볼 페이지

- [로그온·로그오프 (Logon Events)](../logon-events/index.md) — 4624·4625·4648 의 칸, 로그온 유형, 실패 코드를 모두 다룹니다.
- [감사 정책과 로그 설정](../audit-policy-log-settings.md) — 4624·4625·4778·4779 가 남도록 켜져 있었는지, 로그 크기 한도가 얼마였는지 확인합니다.
- [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) — EVTX 파일을 바이트 단위로 읽고, 손상된 레코드를 다룹니다.
- [이벤트 로그 삭제 (1102·104)](../1102-104.md) — 로그를 지운 흔적을 찾습니다.
- [원격 데스크톱 접속 기록](../../network/rdp-client-mru.md) · [원격 데스크톱 비트맵 캐시](../../network/rdp-bitmap-cache.md) · [프리패치](../../execution/prefetch/index.md) — 출발 컴퓨터에 남는 다른 흔적입니다.
- [원격 제어 프로그램](../../network/remote-access-tools/index.md) — 원격 데스크톱이 아닌 원격 제어 도구의 흔적입니다.
- [공유 폴더 접근 (5140·5145)](../5140-5145.md) — 원격 데스크톱과 관계없는 네트워크 로그온을 걸러 냅니다.
- [이벤트 로그 규칙 검색 (Sigma Rules)](../../../03-techniques/analysis/sigma-rules.md) — 많은 로그에서 의심스러운 접속을 골라냅니다.
- [원격 데스크톱 침입 확인](../../../04-scenarios/incident/rdp-intrusion.md) · [계정 탈취와 측면 이동](../../../04-scenarios/incident/credential-theft-lateral-movement/index.md) — 침해 조사에서 이 기록을 읽는 순서입니다.

## 참고 문헌

- Jonathon Poling, "Windows RDP-Related Event Logs: Identification, Tracking, and Investigation", Ponder The Bits, 2018-02-20. https://ponderthebits.com/2018/02/windows-rdp-related-event-logs-identification-tracking-and-investigation/
- JPCERT/CC, Tool Analysis Result Sheet — mstsc. https://jpcertcc.github.io/ToolAnalysisResultSheet/details/mstsc.htm
- Microsoft Learn, "4624(S) An account was successfully logged on." https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4624
- The DFIR Spot, "Lateral Movement: Remote Desktop Protocol (RDP) Event Logs", 2024-10-01 (2025-05-21 수정). https://www.thedfirspot.com/post/lateral-movement-remote-desktop-protocol-rdp-event-logs
