---
title: "들어온 접속: 세션 단계"
parent: "원격 데스크톱 이벤트"
grand_parent: "아티팩트 · 이벤트 로그"
nav_order: 2590
---

# 들어온 접속: 세션 단계 (LocalSessionManager 21~25·4778·4779)

원격 데스크톱 (Remote Desktop, RDP) 로그온이 끝나면 세션이 열리고, 끊기고, 다시 붙고, 닫힙니다. 접속을 받은 컴퓨터는 이 과정을 LocalSessionManager/Operational 로그의 21~25·39·40 과 보안 로그 (Security Log) 의 4778·4779 에 남깁니다. 이 페이지는 이벤트마다 적히는 필드, 끊긴 이유 코드, 원격 접속과 로컬 로그온을 구분하는 법을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

들어온 접속은 다섯 단계로 나눠 볼 수 있습니다. 이 페이지는 그 가운데 로그온, 끊김·다시 연결, 로그오프 단계를 다룹니다. 앞의 연결·인증 단계는 [인증 단계](1149-4624-10-4625.md) 에서 다룹니다.

| 단계 | LocalSessionManager/Operational | Security | System |
|---|---|---|---|
| 로그온 | 21, 22 | | |
| 끊김·다시 연결 | 24, 25, 39, 40 | 4778, 4779 | |
| 로그오프 | 23 | 4634, 4647 | 9009 |

세션 ID (Session ID) 로 한 세션의 활동을 이어서 따라갑니다. 로그온 단계의 4624 는 [인증 단계](1149-4624-10-4625.md) 에서 다룹니다.

## 위치와 버전별 차이

LocalSessionManager/Operational 의 공급자는 Microsoft-Windows-TerminalServices-LocalSessionManager 이고, 이 채널의 파일 위치와 기본 크기는 [허브](index.md) 의 "채널 이름과 파일 경로" 표에 모았습니다. 4778·4779 는 보안 로그에 남으며 하위 범주는 기타 로그온/로그오프 감사 (Audit Other Logon/Logoff Events) 입니다. 9009 는 System 로그에 남습니다.

| Windows | 내용 |
|---|---|
| Vista · Server 2008 이후 | 4778·4779 의 최소 지원 버전입니다. 두 이벤트의 이벤트 버전은 0 하나뿐입니다. 이유 코드 열거형 ExtendedDisconnectReasonCode (MsTscAx.dll) 의 최소 지원 버전도 같습니다. 위 단계 구분도 Vista 이후에 맞습니다 |
| 11 Home 빌드 26200 | 아래 LocalSessionManager 이벤트의 메시지 원문과 XML 필드 위치는 이 빌드 기준입니다 |

## 구조

### LocalSessionManager/Operational

| 이벤트 | 메시지 원문 | 필드 |
|---|---|---|
| 21 | `Remote Desktop Services: Session logon succeeded:` | User, Session ID, Source Network Address |
| 22 | `Remote Desktop Services: Shell start notification received:` | User, Session ID, Source Network Address |
| 23 | `Remote Desktop Services: Session logoff succeeded:` | User, Session ID. 주소 필드가 없습니다 |
| 24 | `Remote Desktop Services: Session has been disconnected:` | User, Session ID, Source Network Address |
| 25 | `Remote Desktop Services: Session reconnection succeeded:` | User, Session ID, Source Network Address |
| 39 | `Session %1 has been disconnected by session %2` | TargetSession, Source |
| 40 | `Session %1 has been disconnected, reason code %2` | Session, Reason |
| 41 | `Begin session arbitration:` | User, Session ID |
| 42 | `End session arbitration:` | User, Session ID |

메시지 원문은 Windows 11 Home 빌드 26200 의 공급자 정의 기준입니다. XML 에서 이 값들은 EventData 아래에 있지 않고 UserData 아래 EventXML 요소에 있으며, 요소 이름은 User, SessionID, Address 입니다. 40 의 요소 이름은 Session, Reason 입니다.

아래는 요소 배치만 보여 주는 틀입니다. 괄호 안은 자리표시이고, 실제 XML 과 글자 하나하나까지 같지는 않습니다.

```xml
<UserData>
  <EventXML>
    <User>(사용자)</User>
    <SessionID>(세션 번호)</SessionID>
    <Address>(원격 IP 또는 LOCAL)</Address>
  </EventXML>
</UserData>
```

### 이벤트마다 뜻과 흔한 짝

| 이벤트 | 뜻 | 흔한 짝 |
|---|---|---|
| 21 · 22 | 세션 로그온, 셸 시작. 원격 데스크톱 로그온이면 주소 필드에 원격 IP 가 있어야 합니다 | |
| 23 | 정식 로그오프. 단순히 끊긴 것이 아닙니다 | Security 4634 |
| 24 | 세션 끊김 | 40, 4779 |
| 25 | 다시 연결 | 40 (이유 코드 5), 4778 |
| 39 | 시작 메뉴의 "연결 끊기" 로 정식으로 끊음. 두 세션 번호가 다르면 한 세션이 다른 세션을 끊어 냈을 수 있습니다 | 40 (이유 코드 11), 4779 |
| 40 | 끊긴 이유 코드를 적음 | 24, 25, 39, 4779 |

### 이유 코드 (40)

40 의 이유 코드는 IMsRdpClient::ExtendedDisconnectReason 값이고, 이 값은 ExtendedDisconnectReasonCode 열거형으로 정의돼 있습니다.

| 코드 | 이름 | Microsoft 정의 | Ponder The Bits 해석 |
|---|---|---|---|
| 0 | exDiscReasonNoInfo | 추가 정보 없음 | 창의 X 를 눌러 닫음. 24 와 짝 |
| 1 | exDiscReasonAPIInitiatedDisconnect | 응용 프로그램이 끊음 | |
| 2 | exDiscReasonAPIInitiatedLogoff | 응용 프로그램이 로그오프함 | |
| 3 | exDiscReasonServerIdleTimeout | 유휴 시간이 정한 시간을 넘어 서버가 끊음 | 유휴 시간 초과 |
| 4 | exDiscReasonServerLogonTimeout | 연결이 정한 시간을 넘어 서버가 끊음 | |
| 5 | exDiscReasonReplacedByOtherConnection | 다른 연결로 바뀜 | 다른 연결이 대신함. 25 와 짝 |
| 6 | exDiscReasonOutOfMemory | 메모리 없음 | |
| 7 | exDiscReasonServerDeniedConnection | 서버가 연결을 거부함 | |
| 8 | exDiscReasonServerDeniedConnectionFips | 보안상 이유로 서버가 거부함 | |
| 9 | exDiscReasonServerInsufficientPrivileges | 보안상 이유로 서버가 거부함 | |
| 10 | exDiscReasonServerFreshCredsRequired | 새 자격 증명이 필요함 | |
| 11 | exDiscReasonRpcInitiatedDisconnectByUser | 사용자 동작으로 끊음 | 39 와 짝 |
| 12 | exDiscReasonLogoffByUser | 사용자가 로그오프해 세션이 끊김 | |

- 256~267 은 라이선스 오류 범위입니다.
- 768 은 잘못된 자격 증명 (exDiscReasonRdpEncInvalidCredentials) 입니다.
- 4096~32767 은 내부 프로토콜 오류 범위입니다.
- 코드 0 은 두 자료의 설명이 다릅니다. Microsoft 정의는 "추가 정보 없음" 입니다. 보고서에는 Microsoft 정의를 쓰고, 창을 닫았다는 해석은 다른 기록으로 받칩니다.

### 4778 · 4779 (Security)

| 이벤트 | 메시지 | 남는 때 |
|---|---|---|
| 4778 | `A session was reconnected to a Window Station.` | 기존 터미널 서비스 세션에 다시 붙을 때. 빠른 사용자 전환 (Fast User Switching) 으로 기존 데스크톱에 돌아올 때. Hyper-V 확장 세션 (Enhanced Session) 에 다시 붙을 때 |
| 4779 | `A session was disconnected from a Window Station.` | 터미널 서비스 세션에서 끊을 때. 빠른 사용자 전환으로 다른 데스크톱으로 넘어갈 때. Hyper-V 확장 세션을 끊을 때 |

| XML 필드 | 내용 |
|---|---|
| AccountName · AccountDomain | 계정과 도메인 |
| LogonID | 로그온 ID (Logon ID). 4624 의 로그온 ID 와 묶습니다 |
| SessionName | 원격 데스크톱 세션은 `RDP-Tcp#N`, 콘솔은 `Console`, Hyper-V 확장 세션은 `31C5CE94259D4006A9E4#3` 같은 값입니다 |
| ClientName | 클라이언트 이름. 콘솔 세션이면 `Unknown` 입니다 |
| ClientAddress | 클라이언트 주소. 콘솔 세션이면 `LOCAL` 입니다. IPv6 나 `::ffff:IPv4` 형식으로 올 수 있습니다 |

Microsoft 문서 본문에는 원격 데스크톱 세션 이름이 `RDP-Rcp#N` 으로 적혀 있지만, 같은 문서의 XML 예시에는 `RDP-Tcp#6`, `RDP-Tcp#3` 이 나오므로 본문 쪽이 오타입니다.

### 세션이 끝날 때 남는 다른 기록

4634 는 끊김과 로그오프 둘 다에서 남고, 로그온 유형은 10 이나 7 입니다. 4647 (사용자가 로그오프를 시작함) 은 원격 데스크톱 전용 이벤트가 아닙니다. System 로그의 9009 `The Desktop Window Manager has exited with code (<X>)` 는 원격 데스크톱 연결이 정식으로 닫혔다는 표시일 수 있지만 늘 남지는 않습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 주소 필드가 원격 IP 인 21·22 가 있으면, 그 시각에 그 주소에서 들어온 이 사용자의 세션이 열렸습니다 | 주소 필드가 `LOCAL` 인 21·22 는 원격 접속의 근거가 아닙니다 |
| 24·40 이 있으면, 그 세션이 끊겼고 40 에 끊긴 이유 코드가 남았습니다 | 24 가 로그오프인지. 24 뒤에 25 로 다시 붙을 수 있습니다 |
| 25·4778 이 있으면, 기존 세션에 다시 붙었습니다. 4778 에는 클라이언트 이름과 주소가 남습니다 | 4778·4779 한 건으로 원격 데스크톱인지. 빠른 사용자 전환과 Hyper-V 확장 세션에서도 남습니다 |
| 23 이 있으면, 그 세션이 정식으로 로그오프했습니다 | 23 으로 접속 주소. 23 에는 주소 필드가 없습니다 |
| | 세션 안에서 무엇을 했는지 |

### 보고서 문장 예

아래 `< >` 는 자리표시입니다.

- 쓸 수 있는 문장: "LocalSessionManager/Operational 로그에 `<시각>` UTC 의 21 기록이 있습니다. 사용자는 `<계정>`, 세션 ID 는 `<번호>`, 주소는 `<주소>` 입니다."
- 쓰면 안 되는 문장: "21 기록이 있으므로 원격 접속이 있었습니다." 주소 필드를 보지 않고 이렇게 쓰지 않습니다.

## 시각 해석

- 시각이 어느 기준으로 저장되는지는 [허브](index.md) 의 "시각" 절을 봅니다.
- 21 의 시각은 세션 로그온에 성공한 때, 22 는 셸 시작 알림을 받은 때, 24 는 세션이 끊긴 때, 23 은 로그오프에 성공한 때입니다.
- 세션 길이를 셀 때 24 를 끝으로 잡으면, 25 로 다시 붙은 뒤의 시간이 빠집니다.

LocalSessionManager 21~25 에는 로그온 ID 필드가 없고 4778·4779 에는 세션 ID 필드가 없어서, 두 로그는 시각과 사용자로 맞춥니다. 4778·4779 와 4624 는 로그온 ID 로 잇습니다.

## 함정과 한계

1. **21·22 를 모두 원격 접속으로 봅니다.** 주소 필드가 `LOCAL` 이면 로컬 로그온입니다. 로컬 로그온의 21 은 부팅 뒤나 로컬 사용자가 로그인할 때도 남습니다.
2. **이벤트 번호만 보고 원격 접속이라고 합니다.** 원격 데스크톱을 받지 않는 PC 에도 이 번호들이 남습니다. 아래는 원격 데스크톱 받기가 꺼진 Windows 11 PC 한 대의 건수 예입니다.

   | 이벤트 | 21 | 22 | 23 | 24 | 25 | 39 | 40 | 41 | 42 |
   |---|---|---|---|---|---|---|---|---|---|
   | 건수 | 24 | 24 | 20 | 3 | 0 | 3 | 3 | 24 | 24 |

   - 21·22·24 의 주소 필드 51건이 모두 `LOCAL` 이었습니다.
   - 39 세 건은 모두 `Session 1 has been disconnected by session 1` 이었습니다.
   - 40 세 건은 모두 이유 코드 11 이었습니다.
   - 32·34·36·54 도 있었습니다. 이 네 이벤트의 뜻은 공급자 정의의 메시지 원문으로 확인합니다.
   - 그러므로 주소 필드를 보지 않고 21·22·24·39·40 의 번호만으로 원격 접속이라고 하지 않습니다.
3. **23 에서 접속 주소를 찾습니다.** 21~25 를 한데 묶어 "원본 IP 와 사용자 이름을 적는 이벤트" 로 소개하는 자료가 있습니다. 공급자 정의에서 23 에는 주소 필드가 없습니다. 주소는 같은 세션 ID 의 21·22·25 에서 찾습니다.
4. **4778·4779 를 모두 원격 데스크톱으로 봅니다.** 빠른 사용자 전환과 Hyper-V 확장 세션에서도 남습니다. SessionName 필드의 `RDP-Tcp#N` 과 `Console` 로 나눕니다.
5. **4778·4779 가 없으면 다시 연결도 없었다고 봅니다.** 두 이벤트는 기타 로그온/로그오프 감사가 켜져 있어야 남습니다. 이 하위 범주가 No Auditing 이면 보안 로그에 4778·4779 가 남지 않습니다. 이 설정은 기기마다 [감사 정책과 로그 설정](../audit-policy-log-settings.md) 으로 확인합니다.
6. **4647·9009 를 원격 데스크톱 세션의 끝으로 바로 읽습니다.** 4647 은 원격 데스크톱 전용이 아니어서 시각을 맞춰 봐야 합니다. 9009 는 늘 남지 않습니다.
7. **오래된 세션 기록을 찾습니다.** 로그 크기 한도가 작으면 오래된 기록이 밀려납니다. 채널별 기본 크기는 [허브](index.md) 에 있습니다.

## 직접 분석해 보기

### 헥스로 읽을 때

EVTX 레코드를 바이트 단위로 읽는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다. 이 페이지는 XML 보기와 명령으로만 따라갑니다.

### 공개 도구로 한 번

- 이벤트 뷰어에서 21 을 열고 "자세히" 탭의 XML 보기로 UserData 아래 Address 요소를 봅니다.
- Windows 에 들어 있는 PowerShell 의 Get-WinEvent 로 아래처럼 뽑습니다. 명령은 수집한 로그 사본에 씁니다.

```powershell
$lsm = '.\Microsoft-Windows-TerminalServices-LocalSessionManager%4Operational.evtx'

# 21~25: 시각(UTC)·ID·사용자·세션 ID·주소 (23 은 주소 자리가 비어 나옵니다)
Get-WinEvent -Path $lsm -FilterXPath "*[System[(EventID>=21 and EventID<=25)]]" |
  ForEach-Object { '{0:o} {1} {2} {3} {4}' -f $_.TimeCreated.ToUniversalTime(), $_.Id, $_.Properties[0].Value, $_.Properties[1].Value, $_.Properties[2].Value }

# 주소 칸이 LOCAL 이 아닌 21·22·24·25 만
Get-WinEvent -Path $lsm -FilterXPath "*[System[(EventID=21 or EventID=22 or EventID=24 or EventID=25)] and UserData[EventXML[Address!='LOCAL']]]"

# 40: 세션 번호와 이유 코드
Get-WinEvent -Path $lsm -FilterXPath "*[System[EventID=40]]" |
  ForEach-Object { $x = ([xml]$_.ToXml()).Event.UserData.EventXML; '{0:o} 세션 {1} 이유 {2}' -f $_.TimeCreated.ToUniversalTime(), $x.Session, $x.Reason }

# 4778·4779: 시각(UTC)·ID·계정·로그온 ID·세션 이름·클라이언트 이름·주소
$sec = '.\Security.evtx'
Get-WinEvent -Path $sec -FilterXPath "*[System[(EventID=4778 or EventID=4779)]]" |
  ForEach-Object {
    $d = @{}
    ([xml]$_.ToXml()).Event.EventData.Data | ForEach-Object { $d[$_.Name] = $_.'#text' }
    '{0:o} {1} {2} {3} {4} {5} {6}' -f $_.TimeCreated.ToUniversalTime(), $_.Id, $d.AccountName, $d.LogonID, $d.SessionName, $d.ClientName, $d.ClientAddress
  }
```

- 조건에 맞는 이벤트가 하나도 없으면 Get-WinEvent 는 "No events were found that match the specified selection criteria." 오류를 냅니다. 이 오류는 해당 기록이 없다는 뜻입니다.
- 다른 공개 EVTX 파서로 뽑았다면 UserData 필드를 제대로 읽었는지 한두 건을 XML 원문과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 | 링크 |
|---|---|---|
| 1149, 4624 유형 10 | 같은 사용자와 주소, 21 바로 앞의 시각 | [인증 단계](1149-4624-10-4625.md) |
| 4624 | 4778·4779 의 LogonID 와 같은 로그온 ID | [인증 단계](1149-4624-10-4625.md) |
| 4634 · 4647 | 23 과 같은 시각대의 로그오프 | [로그온·로그오프](../logon-events/index.md) |
| 대상 컴퓨터의 TSTHEME.EXE·RDPCLIP.EXE 프리패치 | 원격 데스크톱 접속을 받은 쪽에 생기는 프리패치 파일 | [프리패치](../../execution/prefetch/index.md) |
| 대상 컴퓨터의 프린터 드라이버 설치 | 처음 접속할 때 Remote Desktop Easy Print 드라이버가 설치됩니다 | |
| 출발 컴퓨터의 RDPClient 1026 | 끊긴 시각 | [나간 접속](rdpclient-1024-1102.md) |
| 전원 기록 | 로그오프 기록 없이 끝난 세션 | [켜짐·꺼짐](../power-on-off-events.md) |

- 프리패치와 Easy Print 드라이버 흔적이 어느 Windows 버전에서 남는지는 실제 데이터로 확인해야 합니다.
- 세션 기록으로 그 시각의 사용자를 좁히는 흐름은 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 를 봅니다.

## 실습

NIST CFReDS 같은 공개 시험 데이터 가운데 원격 데스크톱 접속을 받은 Windows 이미지를 골라 풉니다. 알맞은 이미지가 없으면 시험용 가상 머신 두 대로 접속, 창 닫기, 다시 연결, 로그오프를 차례로 해 보고 기록을 봅니다.

1. 21 가운데 주소 필드가 `LOCAL` 이 아닌 기록은 몇 건입니까? 그 주소는 1149 의 원본 주소와 같습니까?
2. 한 세션 ID 를 골라 21 부터 23 까지 이어 봅니다. 사이에 24·25 가 몇 번 있습니까?
3. 40 의 이유 코드는 무엇입니까? 바로 앞에 24·25·39 가운데 무엇이 있습니까?
4. 39 의 두 세션 번호가 다른 기록이 있습니까?
5. 4778·4779 가 있다면 SessionName 은 `RDP-Tcp#N` 입니까, `Console` 입니까? LogonID 가 같은 4624 는 무엇입니까?
6. 23 이 없는 세션은 어떻게 끝났습니까? 같은 시각대의 4634·9009·전원 기록을 찾아봅니다.

## 참고 문헌

- Jonathon Poling, "Windows RDP-Related Event Logs: Identification, Tracking, and Investigation", Ponder The Bits, 2018-02-20. https://ponderthebits.com/2018/02/windows-rdp-related-event-logs-identification-tracking-and-investigation/
- JPCERT/CC, Tool Analysis Result Sheet — mstsc. https://jpcertcc.github.io/ToolAnalysisResultSheet/details/mstsc.htm
- Microsoft Learn, "4778(S) A session was reconnected to a Window Station." https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4778
- Microsoft Learn, "4779(S) A session was disconnected from a Window Station." https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4779
- Microsoft Learn, "ExtendedDisconnectReasonCode enumeration". https://learn.microsoft.com/en-us/windows/win32/termserv/extendeddisconnectreasoncode
- The DFIR Spot, "Lateral Movement: Remote Desktop Protocol (RDP) Event Logs", 2024-10-01 (2025-05-21 수정). https://www.thedfirspot.com/post/lateral-movement-remote-desktop-protocol-rdp-event-logs
