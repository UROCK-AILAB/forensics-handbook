# 원격 데스크톱 침입 확인 (RDP Intrusion)

이 페이지는 누군가 원격 데스크톱 (Remote Desktop Protocol, RDP) 으로 이 PC 에 들어왔는지 확인하는 순서를 다룹니다. 로그온 실패가 몰렸는지, 같은 곳에서 성공 로그온으로 이어졌는지, 세션 안에서 무엇을 했는지를 차례로 봅니다. 이 PC 가 다른 PC 로 원격 데스크톱 접속을 나간 출발점인지도 가립니다. 이벤트마다의 칸과 뜻은 [원격 데스크톱 이벤트](../../02-artifacts/event-logs/rdp-event-logs/index.md) 와 그 하위 페이지에 있습니다. 로그온 실패를 여러 건 묶어 대입 모양을 읽는 법은 [비밀번호 대입 공격이 있었나](credential-theft-lateral-movement/brute-force.md) 에 있습니다.

"(관찰)" 을 붙인 내용은 Windows 11 Home(빌드 26200) 분석 PC 한 대에서 직접 조회한 것입니다(확인 범위: Win11 Home 한 대). 한 대에서 본 값이므로 기본값으로 일반화하지 않습니다.

## 조사 질문

- 이 PC 는 원격 데스크톱 접속을 받도록 켜져 있었습니까? 인터넷에 열려 있었습니까?
- 로그온 실패가 몰린 때가 있었습니까? 어느 주소에서, 어느 계정 이름으로 시도했습니까?
- 같은 주소나 같은 계정으로 원격 데스크톱 로그온에 성공한 기록이 있습니까?
- 세션은 언제 시작해 언제 끝났고, 그 사이에 무엇을 했습니까?
- 이 PC 에서 다른 PC 로 원격 데스크톱 접속을 나갔습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 버전과 빌드를 [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 적습니다. 로그온 실패 이벤트 4625 는 Windows Vista·Windows Server 2008 부터 있습니다[2]. |
| 시간대 | 여러 로그의 시각을 한 기준으로 맞춥니다. [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽습니다. Bias 값을 부호 있는 수로 읽는 법은 [이 파일을 누가 언제 열었나](../activity/file-access.md) 의 "먼저 확인할 것" 에 있습니다. |
| 원격 데스크톱 설정 | 접속을 받도록 켜져 있었는지 레지스트리 설정과 방화벽 규칙으로 봅니다. 분석 PC 는 원격 데스크톱 받기가 꺼진 상태였습니다(관찰). 이때 `HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server` 의 `fDenyTSConnections` 값은 1 이었습니다(관찰). 값마다의 뜻은 이번에 공식 문서로 확인하지 못했습니다. 방화벽 기록은 [윈도 방화벽](../../02-artifacts/network/windows-firewall-pfirewall-log.md) 에서 봅니다. |
| 감사 정책 | 로그온 감사가 꺼져 있으면 Security 로그에 로그온 기록이 남지 않습니다. 기록이 없다고 해서 접속이 없었다고 읽지 않습니다. [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 확인합니다. |
| 수집 범위 | 받는 PC 의 Security 로그, TerminalServices 운영 로그, 방화벽 로그, 레지스트리 하이브를 확보합니다. 출발지로 의심되는 PC 가 조직 안에 있으면 그 PC 의 기록도 확보합니다. |

## MITRE 가 설명하는 원격 데스크톱 악용

MITRE ATT&CK 은 원격 데스크톱으로 옆 PC 로 옮겨 가는 기법을 T1021.001 (Remote Desktop Protocol) 로 둡니다[1]. 공격자는 서비스가 켜져 있고 자격 증명을 아는 계정이 접속할 수 있을 때, 그 유효한 계정으로 원격 데스크톱에 로그인합니다[1]. 탐지 문장은 원격 데스크톱 로그온 직후 짧은 시간 안에 이어지는 이상한 프로세스 실행·파일 접근·측면 이동을 보라고 합니다[1].

같은 페이지는 원격 데스크톱을 접근성 기능(T1546.008)이나 터미널 서비스 DLL(T1505.005)과 함께 지속성에 쓰는 경우도 듭니다[1]. 자동실행 위치를 훑는 법은 [악성코드 지속성(자동실행) 찾기](persistence.md) 에 있습니다. 완화책으로는 필요 없으면 원격 데스크톱 끄기, 다중 인증, 인터넷에서 원격 데스크톱 막기, 세션 시간 제한, Remote Desktop Users 그룹 구성원 감사를 들며[1], 보고서의 권고 절에 쓸 수 있습니다.

MITRE 페이지에는 윈도 이벤트 ID 나 레지스트리 키가 없어서[1], 아래 이벤트는 Microsoft 문서와 분석 PC 조회에서 가져왔습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 원격 데스크톱 설정·방화벽 | 접속을 받도록 켜져 있었는지, 허용한 규칙 | [윈도 방화벽](../../02-artifacts/network/windows-firewall-pfirewall-log.md) |
| 2 | Security 4625 | 실패한 계정 이름, 로그온 유형, 원본 주소, 실패 코드 | [로그온 실패와 실패 코드](../../02-artifacts/event-logs/logon-events/4625.md) · [비밀번호 대입 공격이 있었나](credential-theft-lateral-movement/brute-force.md) |
| 3 | 4624 유형 10 · 1149 | 원격 데스크톱 인증 성공 | [들어온 접속: 인증 단계](../../02-artifacts/event-logs/rdp-event-logs/1149-4624-10-4625.md) |
| 4 | LocalSessionManager · 4778 · 4779 | 세션 접속·끊김·재접속 | [들어온 접속: 세션 단계](../../02-artifacts/event-logs/rdp-event-logs/localsessionmanager-21-25-4778-4779.md) |
| 5 | 로그온 세션 | 같은 세션의 로그온과 로그오프, 로그온 유형의 뜻 | [로그온 세션 잇기](../../02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md) · [로그온 유형 해석](../../02-artifacts/event-logs/logon-events/logon-type.md) |
| 6 | 세션 안의 행위 | 프로세스 실행, 계정 변경 | [어떤 프로그램을 언제 실행했나](../activity/program-execution.md) · [계정 생성·변경](../../02-artifacts/event-logs/account-management-events.md) |
| 7 | 나간 접속 | 이 PC 가 접속한 원격 데스크톱 대상 | [원격 데스크톱 접속 기록](../../02-artifacts/network/rdp-client-mru.md) · [원격 데스크톱 비트맵 캐시](../../02-artifacts/network/rdp-bitmap-cache.md) · [나간 접속 (RDPClient)](../../02-artifacts/event-logs/rdp-event-logs/rdpclient-1024-1102.md) |
| 8 | 로그 삭제 | 로그를 지운 흔적 | [이벤트 로그 삭제](../../02-artifacts/event-logs/1102-104.md) |

1~5 는 받는 쪽에서 들어온 접속을 봅니다. 6 은 접속 구간 안에서 한 일을 봅니다. 7 은 이 PC 가 출발점이었는지 봅니다. 해석이 헷갈리는 지점은 [해석 함정 (1149의 뜻·NLA·유형 3과 10 구분)](../../02-artifacts/event-logs/rdp-event-logs/1149-nla-3-10.md) 에 모아 두었습니다.

## 받는 쪽 기록 읽기

**4625 (로그온 실패).**

로그온에 실패할 때마다 로그온을 받은 쪽 컴퓨터에 남습니다[2]. 로그온 유형 10 은 원격 대화형 (RemoteInteractive) 이고, 터미널 서비스나 원격 데스크톱 로그온이 여기에 듭니다[2]. Workstation Name 칸에는 시도한 컴퓨터의 이름이, Source Network Address 칸에는 시도한 컴퓨터의 IP 가 들어갑니다[2].

Microsoft 문서는 로컬 계정의 4625 는 모두 지켜보라고 권하는데, 로컬 계정은 보통 잠기면 안 되기 때문입니다[2]. 칸 전체와 실패 코드 표는 [로그온 실패와 실패 코드](../../02-artifacts/event-logs/logon-events/4625.md) 에 있고, NLA 가 켜진 서버에서 실패가 어떤 로그온 유형으로 남는지는 [해석 함정 (1149의 뜻·NLA·유형 3과 10 구분)](../../02-artifacts/event-logs/rdp-event-logs/1149-nla-3-10.md) 에서 확인합니다.

**TerminalServices 운영 로그.**

원격 데스크톱 인증 성공은 RemoteConnectionManager 운영 로그의 1149 로도 남으며, 분석 PC 의 공급자 정의에서 메시지가 "User authentication succeeded" 임을 확인했습니다(관찰). 같은 채널의 261 은 리스너가 연결을 받았다는 메시지입니다(관찰). 두 이벤트의 메시지 원문과 칸은 [들어온 접속: 인증 단계](../../02-artifacts/event-logs/rdp-event-logs/1149-4624-10-4625.md) 에 있습니다.

이 채널은 Security 로그와 따로 저장되므로, Security 로그가 비어 있어도 이 채널을 따로 봅니다.

## 공개 사례에서 본 원격 데스크톱

The DFIR Report 가 공개한 사례(2023-09-25)에서 본 흔적입니다[3].

공격자는 원격 데스크톱으로 옆 PC 로 옮겨 갔습니다[3]. 네트워크 로그온 기록의 워크스테이션 이름은 WIN-RRRU9REOK18 이었는데[3], 공격자 쪽 컴퓨터의 기본 이름이 이벤트의 Workstation Name 칸에 남은 예입니다. 로그온 유형 7 (Unlock) 기록도 원격 데스크톱 활동을 더 보여 주는 단서로 쓰였습니다[3].

그 전에 공격자는 netscan.exe 로 3389 포트를 훑고, netping.exe 로 /24 대역에 ICMP 핑을 보냈습니다[3]. 이런 도구의 실행 흔적은 접속 전 단계의 단서가 됩니다.

## 분석 흐름

1. 원격 데스크톱 받기가 켜져 있었는지, 인터넷에 열려 있었는지 확인합니다. 레지스트리 설정과 방화벽 규칙을 함께 봅니다.
2. 받는 PC 의 Security 로그에서 4625 가 몰린 시간대를 찾습니다. 그 시간대의 원본 IP 와 계정 이름을 정리합니다.
3. 같은 IP·같은 계정의 첫 성공 로그온(4624 유형 10 등)과 1149 를 찾습니다.
4. 세션 이벤트(LocalSessionManager·4778·4779)로 접속·끊김·재접속 구간을 만듭니다.
5. 그 구간 안의 프로세스 실행, 파일 접근, 계정 변경, 다른 PC 로의 접속을 봅니다[1].
6. 이 PC 에서 나간 원격 데스크톱 접속을 봅니다. 클라이언트 접속 기록, 비트맵 캐시, RDPClient 로그로 이 PC 가 측면 이동의 출발점인지 가립니다.
7. Security 로그가 비어 있거나 중간이 끊겼으면 [이벤트 로그 삭제](../../02-artifacts/event-logs/1102-104.md) 흔적을 봅니다.
8. 모든 PC 의 시각을 UTC 로 맞춰 한 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다. 계정 탈취와 옆 PC 로의 이동은 [계정 탈취와 측면 이동](credential-theft-lateral-movement/index.md) 에서 이어 봅니다.

## 흔한 오판

1. **4625 가 많으니 침입이 성공했다고 봅니다.** 실패 기록은 시도만 보여 줍니다. 같은 원천에서 성공 로그온으로 이어졌는지 따로 확인합니다.
2. **Workstation Name 이 조직의 PC 이름이 아니니 외부라고 봅니다.** 이 칸은 접속한 쪽이 알려 준 이름입니다. IP 와 다른 로그로 맞춰 봅니다.
3. **원본 IP 를 공격자의 위치로 씁니다.** VPN, 원격 제어 프로그램, 조직 안의 중간 PC 를 거쳤으면 이 주소는 마지막 한 단계의 주소입니다.
4. **Security 로그에 없으니 원격 데스크톱 접속은 없었다고 봅니다.** 감사가 꺼져 있었거나 로그를 지웠을 수 있습니다. TerminalServices 채널을 따로 봅니다.

## 보고서 문장 예

- 쓰지 않을 문장: "공격자가 ○○ 에 비밀번호 대입으로 원격 데스크톱에 침입했습니다."
- 쓸 문장: "○○(UTC) 부터 ○○(UTC) 사이에 원본 주소 ○○ 에서 계정 이름 ○○ 로 4625 가 ○○건 있습니다. 같은 주소에서 ○○(UTC) 에 같은 계정의 4624(로그온 유형 10)와 1149 가 있습니다. 이 기록은 이 주소에서 이 계정으로 원격 데스크톱 인증에 성공한 기록이 있음을 보여 줍니다. 이 주소가 실제 출발지인지, 접속한 사람이 누구인지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [원격 데스크톱 이벤트](../../02-artifacts/event-logs/rdp-event-logs/index.md) — 원격 데스크톱 이벤트 전체의 길잡이입니다.
- [들어온 접속: 인증 단계](../../02-artifacts/event-logs/rdp-event-logs/1149-4624-10-4625.md) · [들어온 접속: 세션 단계](../../02-artifacts/event-logs/rdp-event-logs/localsessionmanager-21-25-4778-4779.md) · [나간 접속 (RDPClient)](../../02-artifacts/event-logs/rdp-event-logs/rdpclient-1024-1102.md) · [해석 함정](../../02-artifacts/event-logs/rdp-event-logs/1149-nla-3-10.md) — 이벤트별 세부입니다.
- [로그온 실패와 실패 코드](../../02-artifacts/event-logs/logon-events/4625.md) · [로그온 유형 해석](../../02-artifacts/event-logs/logon-events/logon-type.md) · [로그온 세션 잇기](../../02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md) — 로그온 이벤트를 읽습니다.
- [원격 데스크톱 접속 기록](../../02-artifacts/network/rdp-client-mru.md) · [원격 데스크톱 비트맵 캐시](../../02-artifacts/network/rdp-bitmap-cache.md) — 나간 접속의 흔적입니다.
- [윈도 방화벽](../../02-artifacts/network/windows-firewall-pfirewall-log.md) — 접속을 허용한 규칙과 기록입니다.
- [계정 생성·변경](../../02-artifacts/event-logs/account-management-events.md) · [이벤트 로그 삭제](../../02-artifacts/event-logs/1102-104.md) — 세션 안에서 한 일과 지운 흔적입니다.
- [비밀번호 대입 공격이 있었나](credential-theft-lateral-movement/brute-force.md) · [계정 탈취와 측면 이동](credential-theft-lateral-movement/index.md) — 대입 판정과 그 뒤의 이동입니다.

## 참고 문헌

1. MITRE ATT&CK, "Remote Services: Remote Desktop Protocol, Sub-technique T1021.001" (v1.4, 2026-05-12 수정) — https://attack.mitre.org/techniques/T1021/001/
2. Microsoft Learn, "4625(F) An account failed to log on." (Windows 10 보관 문서, ms.date 2026-03-29) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4625
3. The DFIR Report, "From ScreenConnect to Hive Ransomware in 61 hours" (2023-09-25) — https://thedfirreport.com/2023/09/25/from-screenconnect-to-hive-ransomware-in-61-hours/
