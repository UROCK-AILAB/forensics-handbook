# 나간 접속 (RDPClient 1024·1102)

## 한 줄 요약

원격 데스크톱 (Remote Desktop, RDP) 연결을 건 컴퓨터 (출발 컴퓨터) 에는 RDPClient/Operational 로그가 남습니다. 이 로그의 1024 에는 연결하려던 서버가 적히고, 1102 에는 다중 전송 연결을 시작한 서버가 적힙니다. 이 페이지는 1024·1102 를 중심으로 이 로그의 이벤트와 출발 쪽에서 함께 볼 흔적을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

- 접속을 받은 컴퓨터 (대상) 의 기록에는 접속해 온 주소가 남습니다. 대상 쪽 기록은 [인증 단계](/02-artifacts/event-logs/rdp-event-logs/1149-4624-10-4625.md) 와 [세션 단계](/02-artifacts/event-logs/rdp-event-logs/localsessionmanager-21-25-4778-4779.md) 에서 다룹니다.
- 출발 컴퓨터의 기록에는 어느 서버로 나갔는지가 남습니다.
- 두 쪽을 맞추면 한 번의 접속을 양 끝에서 확인할 수 있습니다.
- 이벤트를 쓰는 공급자 (Provider) 이름은 Microsoft-Windows-TerminalServices-ClientActiveXCore 입니다.
- 채널 이름에는 RDPClient 가 들어가지만 공급자 이름은 다릅니다. 공급자 이름으로 이벤트를 거를 때는 이 이름을 씁니다.
- The DFIR Spot 은 이 로그가 원격 데스크톱 전용이라 보안 로그보다 덜 자주 덮어쓴다고 적었습니다.

## 위치와 버전별 차이

- 채널: Microsoft-Windows-TerminalServices-RDPClient/Operational
- 파일 위치와 기본 크기는 [허브](/02-artifacts/event-logs/rdp-event-logs/index.md) 의 "채널 이름과 파일 경로" 표에 모았습니다.
- 이번에 연 자료에는 Windows 버전마다 달라지는 점이 없었습니다.
- 메시지 원문은 Windows 11 Home 빌드 26200 의 공급자 정의에서 읽었습니다.
- 그 PC 에는 RDPClient/Operational 파일이 없었습니다. 그래서 실제 이벤트 예시는 보지 못했습니다.

## 구조

| 이벤트 | 메시지 원문 | 칸 |
|---|---|---|
| 1024 | `RDP ClientActiveX is trying to connect to the server (%2)` | Name, Value, CustomLevel. `%2` 는 Value 입니다 |
| 1025 | `RDP ClientActiveX has connected to the server` | |
| 1026 | `RDP ClientActiveX has been disconnected (Reason= %2)` | Name, Value, CustomLevel. `%2` 는 Value 이고, 부호 없는 32비트 정수 (UInt32) 입니다 |
| 1027 | `Connected to domain (%1) with session %2.` | DomainName, SessionId |
| 1028 | `Server supports SSL = %1` | |
| 1029 | `Base64(SHA256(UserName)) is = %1` | TraceMessage |
| 1102 | `The client has initiated a multi-transport connection to the server %2.` | Name, Value, CustomLevel |
| 1103 | `The client has established a multi-transport connection to the server.` | |
| 1105 | `The multi-transport connection has been disconnected.` | |

칸 이름을 비워 둔 이벤트는 이번에 칸 정의를 확인하지 않았습니다.

### 이벤트마다 뜻

- **1024** 는 연결을 시도한 서버를 적습니다. The DFIR Spot 은 1024 가 대상 호스트 이름을 적는다고 소개합니다.
- **1025** 는 서버에 연결됐다는 기록입니다.
- **1026** 은 연결이 끊겼다는 기록입니다. 끊긴 이유가 숫자로 남습니다.
- **1027** 은 연결한 도메인 이름과 세션 번호를 적습니다.
- **1028** 은 서버가 SSL 을 지원하는지 적습니다.
- **1029** 는 사용자 이름을 SHA256 으로 해시한 뒤 Base64 로 적습니다. 사용자 이름 원문은 남지 않습니다.
- **1102** 는 다중 전송 (Multi-Transport) 연결을 시작할 때 남습니다. 다중 전송은 UDP 를 함께 쓰는 연결입니다. The DFIR Spot 은 1102 가 대상 IP 주소를 적는다고 소개합니다.
- **1103** 은 다중 전송 연결이 이루어졌다는 기록입니다.
- **1105** 는 다중 전송 연결이 끊겼다는 기록입니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 1024 가 있으면, 그 시각에 이 컴퓨터의 원격 데스크톱 클라이언트가 기록된 서버로 연결을 시도했습니다 | 1024 한 건으로 연결에 성공했는지. 1025·1027 과 대상 쪽 기록으로 확인합니다 |
| 1025 가 있으면, 서버에 연결됐습니다 | 대상에 로그온까지 했는지. 대상 쪽 4624·21 로 확인합니다 |
| 1027 이 있으면, 연결한 도메인 이름과 세션 번호가 남았습니다 | 사용자 이름 원문. 1029 에는 해시만 남습니다 |
| 1029 가 있으면, 후보 사용자 이름을 해시해 맞춰 볼 수 있습니다 | 해시를 만든 규칙. 도메인을 붙이는지, 대소문자를 어떻게 다루는지 확인하지 못했습니다 |
| 1102 가 있으면, 다중 전송 연결을 시작한 서버의 주소가 남았습니다 | 1102 가 없을 때 연결도 없었는지 |
| | 연결을 건 사람이 누구인지 |

### 보고서 문장 예

아래 `< >` 는 자리표시입니다.

- 쓸 수 있는 문장: "RDPClient/Operational 로그에 `<시각>` UTC 의 1024 기록이 있습니다. 서버 값은 `<대상>` 입니다."
- 쓰면 안 되는 문장: "`<대상>` 서버에 로그인했습니다." 1024 만 근거로 이렇게 쓰지 않습니다.

## 시각 해석

- 시각이 어느 기준으로 저장되는지는 [허브](/02-artifacts/event-logs/rdp-event-logs/index.md) 의 "시각" 절을 봅니다.
- 1024 의 시각은 연결을 시도한 때입니다.
- 1025 의 시각은 연결된 때입니다.
- 1026 의 시각은 연결이 끊긴 때입니다.
- 출발 컴퓨터의 시각과 대상 컴퓨터의 시각을 맞출 때는 두 컴퓨터의 시계 차이를 먼저 확인합니다. 방법은 [타임라인 작성](/03-techniques/analysis/timeline/index.md) 을 봅니다.

## 함정과 한계

1. **1024 의 값을 사용자가 입력한 문자열로 단정합니다.** 1024 의 값이 입력한 이름이나 IP 그대로인지는 확인하지 못했습니다. 대상은 1102 와 레지스트리의 접속 기록으로 함께 확인합니다.
2. **1102 가 없으면 연결도 없었다고 봅니다.** 1102 는 다중 전송 연결을 시작할 때의 메시지입니다. UDP 를 쓰지 않는 연결에서도 남는지는 확인하지 못했습니다.
3. **1029 에서 사용자 이름을 되살리려 합니다.** 해시에서 원래 이름을 거꾸로 구할 수는 없습니다. 후보 이름을 같은 방법으로 해시해 맞춰 봅니다. 해시 규칙을 확인하지 못했으므로 여러 형태를 시험합니다.
4. **1026 의 Reason 숫자를 LocalSessionManager 40 의 이유 코드 표로 읽습니다.** 1026 의 숫자가 어떤 코드표를 따르는지 확인하지 못했습니다. [세션 단계](/02-artifacts/event-logs/rdp-event-logs/localsessionmanager-21-25-4778-4779.md) 의 표를 그대로 적용하지 않습니다.
5. **파일이 없으면 지웠다고 봅니다.** 채널이 켜져 있어도 파일이 없는 경우를 관찰했습니다. [허브](/02-artifacts/event-logs/rdp-event-logs/index.md) 를 봅니다. 로그를 지운 흔적은 [이벤트 로그 삭제 (1102·104)](/02-artifacts/event-logs/1102-104.md) 에서 찾습니다. 그 페이지의 1102 는 이 페이지의 RDPClient 1102 와 채널이 다른 별개의 이벤트입니다. 번호만 보고 섞지 않습니다.

## 직접 분석해 보기

### 헥스로 읽을 때

EVTX 레코드를 바이트 단위로 읽는 법은 [이벤트 로그 형식](/01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다. 이 페이지는 명령으로만 따라갑니다.

### 공개 도구로 한 번

- 라이브 시스템에서는 `wevtutil gl Microsoft-Windows-TerminalServices-RDPClient/Operational` 로 채널이 켜져 있는지, 최대 크기와 파일 경로가 무엇인지 봅니다.
- 수집한 로그 사본에서는 Windows 에 들어 있는 PowerShell 의 Get-WinEvent 로 뽑습니다.

```powershell
$cli = '.\Microsoft-Windows-TerminalServices-RDPClient%4Operational.evtx'

# 1024·1102: 시각(UTC)·ID·서버 값 (Value 칸)
Get-WinEvent -Path $cli -FilterXPath "*[System[(EventID=1024 or EventID=1102)]]" |
  ForEach-Object { '{0:o} {1} {2}' -f $_.TimeCreated.ToUniversalTime(), $_.Id, $_.Properties[1].Value }

# 1024~1029, 1102~1105 를 오래된 순서로
Get-WinEvent -Path $cli -FilterXPath "*[System[(EventID>=1024 and EventID<=1029) or (EventID>=1102 and EventID<=1105)]]" -Oldest |
  ForEach-Object { '{0:o} {1} {2}' -f $_.TimeCreated.ToUniversalTime(), $_.Id, $_.Message }
```

1029 값과 맞춰 볼 후보 해시는 아래처럼 만듭니다. 이름은 예시입니다. 해시 규칙을 확인하지 못했으므로 대소문자, 도메인 포함 여부, 문자 인코딩을 바꿔 가며 시험합니다. 문자 인코딩은 [문자 인코딩](/01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 을 봅니다.

```powershell
$candidates = 'kim', 'KIM', 'CORP\kim'
foreach ($u in $candidates) {
  foreach ($enc in [Text.Encoding]::Unicode, [Text.Encoding]::UTF8) {
    $h = [Security.Cryptography.SHA256]::Create().ComputeHash($enc.GetBytes($u))
    '{0} {1} {2}' -f $u, $enc.WebName, [Convert]::ToBase64String($h)
  }
}
```

- 어느 조합이 1029 값과 같으면, 그 조합을 보고서에 적습니다.
- 어느 조합도 같지 않으면 "후보와 맞지 않았다" 까지만 씁니다.

## 교차 검증

출발 컴퓨터에서 함께 볼 흔적은 아래와 같습니다. 레지스트리·파일 흔적은 JPCERT/CC 자료를 따릅니다. 이 자료는 시험한 OS 버전을 적지 않았습니다.

| 흔적 | 위치 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 4648 | 보안 로그 | 명시적 자격 증명으로 로그온을 시도한 기록입니다. 대상 서버와 계정이 적힙니다. 시작한 프로세스로 mstsc 등이 보일 수 있습니다 | [로그온·로그오프](/02-artifacts/event-logs/logon-events/index.md) |
| MRU0 | `HKEY_USERS\<SID>\SOFTWARE\Microsoft\Terminal Server Client\Default` | 접속한 대상 호스트 | [원격 데스크톱 접속 기록](/02-artifacts/network/rdp-client-mru.md) |
| UsernameHint | `HKEY_USERS\<SID>\SOFTWARE\Microsoft\Terminal Server Client\Servers\<대상 호스트>` | 그 대상에 쓴 사용자 이름 | [원격 데스크톱 접속 기록](/02-artifacts/network/rdp-client-mru.md) |
| Default.rdp | `C:\Users\<사용자>\Documents\` | 접속 설정 | |
| bcache`<번호>`.bmc | `C:\Users\<사용자>\AppData\Local\Microsoft\Terminal Server Client\Cache\` | 비트맵 캐시 | [원격 데스크톱 비트맵 캐시](/02-artifacts/network/rdp-bitmap-cache.md) |
| MSTSC.EXE-`<해시>`.pf | `C:\Windows\Prefetch\` | mstsc 실행 흔적 | [프리패치](/02-artifacts/execution/prefetch/index.md) |

- 1024·1102 의 대상과 같은 시각대에 대상 컴퓨터의 1149·4624 유형 10 이 있는지 봅니다. [인증 단계](/02-artifacts/event-logs/rdp-event-logs/1149-4624-10-4625.md) 를 봅니다.
- 1026 의 시각은 대상 컴퓨터의 LocalSessionManager 24·40 과 맞춰 봅니다. [세션 단계](/02-artifacts/event-logs/rdp-event-logs/localsessionmanager-21-25-4778-4779.md) 를 봅니다.
- 여러 컴퓨터를 옮겨 다닌 흐름은 [계정 탈취와 측면 이동](/04-scenarios/incident/credential-theft-lateral-movement/index.md) 을 봅니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 원격 데스크톱 연결을 건 Windows 이미지를 골라 풉니다. 알맞은 검체가 없으면 시험용 가상 머신에서 다른 가상 머신으로 직접 접속해 기록을 만듭니다.

1. 1024 의 서버 값은 이름입니까, IP 입니까? 같은 시각대의 1102 값과 어떻게 다릅니까?
2. 1024 다음에 1025·1027 이 이어집니까? 1027 의 도메인 이름은 무엇입니까?
3. 1026 의 Reason 숫자는 무엇입니까? 같은 시각대에 대상 쪽 LocalSessionManager 24·40 이 있습니까?
4. 1029 값을 후보 사용자 이름의 해시와 맞춰 봅니다. 어떤 형태와 인코딩에서 맞습니까?
5. MRU0 에 남은 대상 호스트와 1024 의 서버 값은 같습니까?
6. 같은 시각대의 4648 에 적힌 대상 서버와 프로세스는 무엇입니까?

## 참고 문헌

- JPCERT/CC, Tool Analysis Result Sheet — mstsc. https://jpcertcc.github.io/ToolAnalysisResultSheet/details/mstsc.htm
- The DFIR Spot, "Lateral Movement: Remote Desktop Protocol (RDP) Event Logs", 2024-10-01 (2025-05-21 수정). https://www.thedfirspot.com/post/lateral-movement-remote-desktop-protocol-rdp-event-logs
