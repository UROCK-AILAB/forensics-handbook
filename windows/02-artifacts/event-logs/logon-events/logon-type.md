# 로그온 유형 해석 (Logon Type)

## 한 줄 요약

로그온 유형 (Logon Type) 은 4624·4625·4634 이벤트에 숫자로 남는 칸입니다. 이 숫자는 로그온 세션이 어떤 길로 만들어졌는지 알려 줍니다. 기록은 로그온을 받은 컴퓨터에 남습니다. 숫자 하나로 "사람이 앞에 있었나", "원격이었나", "자격 증명이 그 PC 메모리에 남았나" 를 1차로 가를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

LSA (Local Security Authority) 는 로그온 세션을 만들 때마다 로그온 프로세스가 요청한 로그온 종류를 받습니다. 이 종류는 `SECURITY_LOGON_TYPE` 이라는 열거형 값입니다. 감사 정책이 켜져 있으면 이 값이 보안 이벤트의 `LogonType` 칸에 그대로 적힙니다.

| 이벤트 | 뜻 | `LogonType` 칸 | 감사 하위 범주 |
|---|---|---|---|
| 4624 | 로그온 성공. 세션이 만들어졌습니다 | 있음 | 로그온 감사 (Audit Logon) |
| 4625 | 로그온 실패 | 있음 | 로그온 감사, 계정 잠금 감사 |
| 4634 | 세션이 끝나 더는 없습니다 | 있음 | 로그오프 감사 (Audit Logoff) |

- 4624 는 접속을 받은 컴퓨터, 곧 세션이 만들어진 컴퓨터에 남습니다.
- 4625 도 로그온을 시도한 대상 컴퓨터에 남습니다.
- 레코드에는 숫자만 들어 있습니다. "Interactive" 같은 이름은 이벤트 뷰어나 분석 도구가 붙여 보여 줍니다.
- 실패 코드와 세션 잇기는 각각 [로그온 실패와 실패 코드](4625.md), [로그온 세션 잇기](logon-id-4624-4634-4647.md)에서 다룹니다.

## 위치와 버전별 차이

세 이벤트 모두 보안 로그 `%SystemRoot%\System32\winevt\Logs\Security.evtx` 에 남습니다. 감사 정책을 확인하는 법은 [감사 정책과 로그 설정](../audit-policy-log-settings.md)을 봅니다. 로컬 PC 와 도메인 컨트롤러 가운데 어디에 남는지는 [기록이 남는 위치](pc.md)를 봅니다.

| Windows | 로그온 성공 이벤트 | 로그온 유형과 관련된 차이 |
|---|---|---|
| XP·Server 2003 | 528 (로그온 성공), 540 (네트워크 로그온 성공) | 구형 EVT 형식입니다. 형식은 [구형 EVT 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/windows-xp-2003.md)을 봅니다 |
| Vista·Server 2008 | 4624 이벤트 버전 0 | 4624·4625·4634 가 이때 생겼습니다 |
| 8·Server 2012 | 4624 이벤트 버전 1 | 가장 수준 (Impersonation Level) 칸이 생겼습니다 |
| 10 이후 | 4624 이벤트 버전 2 | "로그온 정보" 절이 생기고 로그온 유형이 그 절로 옮겨졌습니다. 제한된 관리 모드·가상 계정·상승된 토큰·연결된 로그온 ID·네트워크 계정 이름·네트워크 계정 도메인 칸이 생겼습니다 |

4625 와 4634 는 문서상 이벤트 버전 0 하나뿐입니다.

## 구조

### 유형 번호

아래 뜻은 Microsoft 문서의 설명을 옮긴 것입니다.

| 번호 | 이름 | 뜻 |
|---|---|---|
| 0 | System | 시스템 시작 때처럼 SYSTEM 계정만 씁니다. 열거형에서는 `UndefinedLogonType` 입니다 |
| 2 | Interactive | 이 컴퓨터에서 로그온했습니다 |
| 3 | Network | 사용자나 컴퓨터가 네트워크를 거쳐 이 컴퓨터에 로그온했습니다 |
| 4 | Batch | 사용자가 직접 손대지 않아도 그 사용자 대신 프로세스가 도는 로그온입니다 |
| 5 | Service | 서비스 제어 관리자가 서비스를 시작했습니다 |
| 6 | Proxy | 열거형에만 있고 지원하지 않습니다 |
| 7 | Unlock | 잠긴 워크스테이션을 풀었습니다 |
| 8 | NetworkCleartext | 네트워크 로그온입니다. 비밀번호가 해시되지 않은 채 이 컴퓨터의 인증 패키지에 넘어왔습니다 |
| 9 | NewCredentials | 호출한 쪽이 지금 토큰을 복제하고, 바깥 연결에만 쓸 새 자격 증명을 붙였습니다. 로컬 신원은 그대로입니다 |
| 10 | RemoteInteractive | 터미널 서비스·원격 데스크톱으로 원격에서 로그온했습니다 |
| 11 | CachedInteractive | 이 컴퓨터에 저장해 둔 네트워크 자격 증명으로 로그온했습니다. 도메인 컨트롤러에 묻지 않았습니다 |
| 12 | CachedRemoteInteractive | RemoteInteractive 와 같습니다. 내부 감사용입니다 |
| 13 | CachedUnlock | 열거형 설명은 "워크스테이션 잠금 해제 시도" 입니다 |

1 은 열거형에 정의가 없습니다. 4634 문서의 표에는 2·3·4·5·7·8·9·10·11 만 있습니다. 0·12·13 은 4624 문서의 표와 열거형에 나옵니다.

### 연결 방법과 유형, 남는 자격 증명

Microsoft 는 관리 도구마다 어떤 유형이 생기는지 표로 정리해 두었습니다. "자격 증명이 남음" 은 LM·NT 해시, Kerberos TGT, 평문 비밀번호 가운데 재사용할 수 있는 것이 대상 컴퓨터의 LSASS 메모리에 남는다는 뜻입니다.

| 연결 방법 | 대상 컴퓨터에 남는 유형 | 대상 메모리에 자격 증명이 남나 |
|---|---|---|
| 콘솔 로그온. 네트워크 KVM·서버 원격 관리 카드 포함 | 2 | 남음 |
| RUNAS | 2 | 남음 |
| RUNAS /NETWORK (`/netonly`) | 9 | 남음 |
| 원격 데스크톱 (성공) | 10 | 남음 |
| `net use`, 원격 MMC 스냅인, 원격 레지스트리 | 3 | 남지 않음 |
| PowerShell WinRM (`Enter-PSSession`) | 3 | 남지 않음 |
| PowerShell WinRM + CredSSP | 8 | 남음 |
| PsExec, 자격 증명 지정 없음 | 3 | 남지 않음 |
| PsExec, 자격 증명 지정 (`-u` `-p`) | 3 과 2 (세션이 여러 개 생깁니다) | 남음 |
| 원격 데스크톱 게이트웨이 인증 | 3 (게이트웨이에) | 남지 않음 |
| 예약 작업 | 4 | 남음. 비밀번호가 LSA 시크릿으로 디스크에도 저장됩니다 |
| 서비스로 실행 | 5 | 남음. 비밀번호가 LSA 시크릿으로 디스크에도 저장됩니다 |
| IIS 기본 인증 (IIS 6.0 이후) | 8 | 남음 |
| IIS 통합 Windows 인증 | 3 | 남지 않음 |

유형 3 이라도 위임 (Delegation) 이 켜져 있으면 Kerberos 티켓이 남습니다. LSA 시크릿은 [LSA 시크릿](../../credentials/sam-security/lsa-secrets.md)에서 다룹니다.

> 그림 자리: 출발 PC 와 대상 PC 두 대를 그리고, 원격 데스크톱·공유 폴더 접근·`runas /netonly` 가 각각 어느 PC 에 몇 번 유형으로 남는지 화살표로 보여 줍니다.

### 함께 읽을 칸 (4624)

유형 숫자만으로는 해석이 모자랍니다. 아래 칸을 같이 읽습니다.

| 칸 (XML 이름) | 뜻 | 유형과의 관계 |
|---|---|---|
| `LogonProcessName` | 로그온을 처리한 신뢰된 로그온 프로세스 이름 | Microsoft 예시에서 유형 2 는 `User32` 입니다. 공개 탐지 규칙은 유형 9 의 `seclogo`, NTLM 유형 3 의 `NtLmSsp` 를 씁니다 |
| `AuthenticationPackageName` | 인증 패키지. 흔한 값은 NTLM·Kerberos·Negotiate 입니다 | Negotiate 는 Kerberos 를 먼저 고르고, 못 쓰면 NTLM 을 씁니다 |
| `WorkstationName`, `IpAddress`, `IpPort` | 로그온을 시도한 컴퓨터의 이름·주소·포트 | 대화형 로그온은 포트가 0 입니다. 주소 `127.0.0.1`·`::1` 은 이 컴퓨터 자신입니다 |
| `TargetOutboundUserName`, `TargetOutboundDomainName` | 네트워크 계정 이름·도메인. 바깥 연결에 쓸 계정입니다 | 유형 9 에서만 값이 있습니다. 나머지는 `-` 입니다 |
| `RestrictedAdminMode` | 제한된 관리 모드로 자격 증명을 넘겼는지 (Yes/No) | 유형 10 에서만 값이 있습니다. 나머지는 `-` 입니다 |
| `ElevatedToken` | Yes 면 관리자 권한으로 올라간 세션입니다 | Win10 이후 |
| `TargetLinkedLogonId` | 짝이 되는 세션의 로그온 ID. 없으면 `0x0` 입니다 | Win10 이후 |
| `VirtualAccount` | 관리 서비스 계정 같은 가상 계정인지 (Yes/No) | Win10 이후 |

주소와 워크스테이션 이름은 인증 방식에 따라 채워지기도 하고 비기도 합니다. Microsoft 문서는 Kerberos 네트워크 로그온에는 워크스테이션 정보가 없을 수 있고, NTLM 로그온에는 TCP/IP 정보가 없을 수 있다고 적습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 그 시각에 이 컴퓨터에서 이 계정의 세션이 이 유형으로 만들어졌습니다 (4624) | 그 계정을 쓴 사람이 누구인지 |
| 이 유형의 로그온 시도가 실패했습니다 (4625) | 유형 2 라도 사람이 키보드 앞에 있었는지 |
| 유형 3·8·10 이면 기록된 주소·이름에서 인증 요청이 왔습니다 | 기록된 주소가 실제 출발지인지. 게이트웨이나 주소 변환 장비를 거쳤을 수 있습니다 |
| 유형 2·4·5·8·9·10 이면 세션 동안 재사용할 수 있는 자격 증명이 LSASS 메모리에 있었습니다 (Microsoft 표 기준) | 그 자격 증명을 누가 빼냈는지 |
| 유형 9 이면 이 컴퓨터에서 바깥 연결용 새 자격 증명을 붙인 세션을 만들었습니다 | 그 자격 증명이 상대 컴퓨터에서 통했는지. 상대 컴퓨터에서 무엇을 했는지 |
| | 세션 안에서 무엇을 했는지. 유형 3 이면 어떤 파일을 열었는지 |

보고서에는 기록이 말하는 만큼만 씁니다. 아래 주소는 문서용 예시 주소입니다.

- 쓸 수 있는 문장: "Security.evtx 에 2024-03-15 06:30:00 UTC, 계정 `kim` 의 로그온 유형 10(RemoteInteractive) 성공 기록이 있습니다. 원본 주소는 192.0.2.10 으로 기록되어 있습니다."
- 쓰면 안 되는 문장: "김 씨가 192.0.2.10 에서 원격으로 접속해 작업했습니다."

## 시각 해석

- 이벤트 시각(`TimeCreated`)은 UTC 입니다. 레코드 안에 FILETIME 으로 저장됩니다. 형식은 [EVTX 파일 구조](../../../01-foundations/database-log-formats/evtx-evt-etl/file-header-chunk-record.md)를 봅니다.
- 이벤트 뷰어는 분석 PC 의 시간대로 바꿔 보여 줍니다. 보정은 [시간대·시계 오차 보정](../../../03-techniques/analysis/timeline/time-normalization.md)을 봅니다.
- 4624 의 시각은 이 컴퓨터에 세션이 만들어진 때입니다. 4634 의 시각은 세션이 사라진 때입니다.
- 유형 7 의 4624 시각은 잠금을 푼 때입니다.
- 유형 9 의 시각은 새 자격 증명 세션을 만든 때입니다. 상대 컴퓨터에 실제로 접속한 때가 아닙니다. 접속한 때는 상대 컴퓨터의 유형 3 기록에서 찾습니다.
- 유형 3 세션의 길이는 사람이 자리에 있던 시간과 관계가 없습니다. 네트워크 자원에 접근할 때마다 세션이 생기고 끝날 수 있습니다.
- 로그온 ID 는 한 번 부팅한 동안에만 고유합니다. 재부팅을 넘어 4624 와 4634 를 짝짓지 않습니다.
- 시스템 시각을 바꾸면 이벤트 시각도 그 시계를 따릅니다. [시간 변경 (4616·Kernel-General)](../4616-kernel-general.md)을 함께 봅니다.

## 함정과 한계

1. **유형 2 를 "사람이 앞에 있었다" 로 읽습니다.** RUNAS, 네트워크 KVM, 서버 원격 관리 카드도 유형 2 를 남깁니다. 자격 증명을 지정한 PsExec 도 대상에 유형 2 세션을 만듭니다. Microsoft 의 4634 문서 예시에는 `Window Manager\DWM-1` (S-1-5-90-1) 계정의 유형 2 기록이 나옵니다. 계정 SID 를 보고 시스템 계정을 먼저 걸러 냅니다([윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md)).
2. **한 번 로그온을 4624 두 건으로 셉니다.** UAC 가 켜진 관리자 계정이 대화형으로 로그온하면 권한이 있는 세션과 없는 세션이 함께 생깁니다. 두 기록은 `TargetLinkedLogonId` 로 이어집니다. 자세한 내용은 [로그온 세션 잇기](logon-id-4624-4634-4647.md)를 봅니다.
3. **유형 3 을 모두 사람의 접속으로 봅니다.** 유형 3 은 공유 폴더 접근, 원격 관리 도구, 스캐너가 모두 남깁니다. 계정 이름이 `$` 로 끝나는 컴퓨터 계정과 `ANONYMOUS LOGON` 도 많습니다. 원격 데스크톱에서 유형 3 과 10 이 함께 보이는 이유는 [RDP 해석 함정](../rdp-event-logs/1149-nla-3-10.md)에서 다룹니다.
4. **유형 8 을 "비밀번호가 평문으로 네트워크를 지나갔다" 로 읽습니다.** 유형 8 은 평문 비밀번호가 대상 컴퓨터의 인증 패키지에 넘어왔다는 뜻입니다. Microsoft 문서는 기본 인증 패키지가 자격 증명을 해시한 뒤 네트워크로 보낸다고 적습니다. 전송 구간이 평문이었는지는 프로토콜과 암호화 설정으로 따로 봅니다.
5. **유형 9 의 계정 칸을 거꾸로 읽습니다.** 유형 9 는 로컬 신원을 그대로 둡니다. 그래서 새 로그온 계정 칸에는 원래 사용자가 남습니다. 바깥 연결에 쓸 계정은 `TargetOutboundUserName` 에 있습니다.
6. **유형 9 를 곧바로 공격으로 봅니다.** 공개 탐지 규칙(Sigma)은 유형 9·`seclogo`·Negotiate 조합을 Mimikatz `sekurlsa::pth` 같은 해시 전달 (Pass-the-Hash) 동작과 맞는다고 봅니다. 같은 규칙은 `runas /netonly` 를 오탐 원인으로 적습니다. 판단은 [자격 증명을 빼냈나](../../../04-scenarios/incident/credential-theft-lateral-movement/credential-dumping.md)와 [다른 PC 에서 원격 실행했나](../../../04-scenarios/incident/credential-theft-lateral-movement/psexec-wmi-winrm.md)의 흐름을 따라 여러 기록으로 합니다.
7. **도구가 붙인 이름만 봅니다.** 문서마다 표에 실린 번호가 다릅니다. 도구의 번호-이름 대응표도 다를 수 있습니다. 판단은 숫자 원값으로 합니다.
8. **없다고 안 했다고 봅니다.** 로그온 감사가 꺼져 있으면 4624 가 없습니다. 보안 로그가 크기 한도에 닿으면 오래된 기록부터 덮어씁니다. 로그를 지운 흔적은 [이벤트 로그 삭제](../1102-104.md)에서 찾습니다. 지운 뒤 파일 안에 남은 레코드는 [파일 안에 남은 지운·손상 레코드](../../../01-foundations/database-log-formats/evtx-evt-etl/chunk-slack-corrupted-evtx.md)를 봅니다.
9. **출발 PC 에서 유형 10 을 찾습니다.** 유형은 로그온을 받은 쪽에 남습니다. 원격 데스크톱으로 나간 기록은 출발 PC 의 [나간 접속 (RDPClient 1024·1102)](../rdp-event-logs/rdpclient-1024-1102.md)과 [원격 데스크톱 접속 기록](../../network/rdp-client-mru.md)에서 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

EVTX 레코드 안의 이벤트는 이진 XML 템플릿 (Binary XML Template) 과 값 배열로 저장됩니다. 저장 형식 전체는 [이진 XML 해석](../../../01-foundations/database-log-formats/evtx-evt-etl/binary-xml-template.md)에서 다룹니다. 여기서는 `LogonType` 값 하나만 찾아갑니다.

libevtx 형식 명세에 따르면 템플릿 인스턴스는 세 부분으로 이어집니다.

| 부분 | 크기 | 내용 |
|---|---|---|
| 값 개수 | 4바이트 | 템플릿 값의 개수 |
| 값 기술자 배열 | 값마다 4바이트 | 크기 2바이트, 값 종류 1바이트, 빈 칸 1바이트 (0x00) |
| 값 데이터 | 가변 | 기술자 순서대로 이어 붙은 값 |

아래는 형식 명세로 만든 예시입니다. 실제 검체에서 뽑은 바이트가 아닙니다. 값은 Microsoft 4624 문서의 예시 XML(`TargetLogonId` 0x8dcdc, `LogonType` 2)을 명세대로 바이트로 옮겼습니다. 배열 안에서 두 값의 실제 위치는 템플릿에 따라 다릅니다.

```
[값 기술자 배열 — 4바이트씩]
 ...
 08 00 15 00                ← TargetLogonId 의 기술자
 04 00 08 00                ← LogonType 의 기술자
 ...
[값 데이터 — 기술자 순서대로]
 ...
 DC DC 08 00 00 00 00 00    ← TargetLogonId 값
 02 00 00 00                ← LogonType 값
 ...
```

1. `04 00` 은 리틀 엔디언 크기입니다. 값이 4바이트라는 뜻입니다.
2. `08` 은 값 종류입니다. 0x08 은 부호 없는 32비트 정수 (UInt32) 입니다. Microsoft 문서도 로그온 유형의 자료형을 UInt32 로 적습니다.
3. `02 00 00 00` 을 리틀 엔디언으로 읽으면 2 입니다. 유형 2, Interactive 입니다.
4. `08 00 15 00` 은 8바이트 값이고 종류 0x15 입니다. 0x15 는 16진 64비트 정수 (HexInt64) 입니다.
5. `DC DC 08 00 00 00 00 00` 을 리틀 엔디언으로 읽으면 0x8DCDC 입니다. 이 값이 로그온 ID 입니다.
6. "Interactive" 라는 글자는 레코드 어디에도 없습니다. 숫자만 저장됩니다.

어느 기술자가 `LogonType` 인지는 템플릿 정의에서 찾습니다. 템플릿 안의 `<Data Name="LogonType">` 요소에는 치환 토큰이 들어 있습니다. 토큰은 1바이트 종류(0x0D 보통 치환, 0x0E 선택 치환), 2바이트 치환 번호, 1바이트 값 종류로 되어 있습니다. 이 치환 번호가 값 기술자 배열의 순번입니다.

### 공개 도구로 한 번

- 이벤트 뷰어의 "자세히 → XML 보기" 에서 `<Data Name="LogonType">10</Data>` 처럼 숫자를 바로 볼 수 있습니다.
- Windows 에 들어 있는 PowerShell 로 유형을 골라 뽑을 수 있습니다. 아래는 사본 파일에서 유형 10 성공 기록만 고르는 예입니다.

```powershell
Get-WinEvent -Path .\Security.evtx -FilterXPath "*[System[EventID=4624] and EventData[Data[@Name='LogonType']='10']]"
```

- python-evtx, EvtxECmd, Hayabusa, Chainsaw 같은 공개 도구도 `LogonType` 을 뽑아 줍니다. 도구가 보여 주는 이름이 위 번호표와 맞는지 한두 건을 XML 원문과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.
- 여러 기록을 규칙으로 훑는 방법은 [이벤트 로그 규칙 검색](../../../03-techniques/analysis/sigma-rules.md)을 봅니다.

## 교차 검증

| 유형 | 함께 볼 기록 | 링크 |
|---|---|---|
| 2·7·11 | 잠금·해제, 사용자 로그오프 | [화면 잠금·해제](4800-4801.md), [로그온 세션 잇기](logon-id-4624-4634-4647.md) |
| 11 | 이 PC 에 저장된 도메인 캐시 자격 증명 | [도메인 캐시 자격증명](../../credentials/sam-security/mscache-v2.md) |
| 3 | 출발 PC 의 명시적 자격 증명 기록, 도메인 컨트롤러의 인증 기록, 공유 폴더 접근 | [명시적 자격 증명·특수 권한](4648-4672.md), [도메인 인증 이벤트](4768-4769-4776.md), [공유 폴더 접근](../5140-5145.md) |
| 3·8 | WinRM·WMI 원격 명령 | [원격 명령 실행 이벤트](../winrm-wmi-activity.md) |
| 4 | 예약 작업 등록·실행 | [예약 작업 이벤트](../taskscheduler-4698.md), [예약 작업](../../persistence/scheduled-tasks/index.md) |
| 5 | 서비스 설치 | [서비스 설치 (7045·4697)](../7045-4697.md), [서비스·드라이버](../../persistence/services-drivers.md) |
| 9 | 같은 PC 의 4648, 상대 PC 의 유형 3 | [명시적 자격 증명·특수 권한](4648-4672.md) |
| 10·12 | 원격 데스크톱 인증·세션 기록 | [들어온 접속: 인증 단계](../rdp-event-logs/1149-4624-10-4625.md), [들어온 접속: 세션 단계](../rdp-event-logs/localsessionmanager-21-25-4778-4779.md) |
| 모든 유형 | 같은 로그온 ID 의 특수 권한 부여, 세션 안에서 만든 프로세스 | [명시적 자격 증명·특수 권한](4648-4672.md), [프로세스 생성 (4688)](../4688.md) |

유형 2·4·5·8·9·10 세션이 있었던 PC 는 메모리에 자격 증명이 남았을 수 있습니다. 메모리 덤프가 있으면 [메모리 속 문자열·자격증명·암호 키](../../../03-techniques/analysis/memory-forensics/strings-credentials-keys.md)로 이어서 봅니다. 조사 흐름은 [PC 사용 시간 재구성](../../../04-scenarios/activity/system-usage-time.md), [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md), [원격 데스크톱 침입 확인](../../../04-scenarios/incident/rdp-intrusion.md), [비밀번호 대입 공격이 있었나](../../../04-scenarios/incident/credential-theft-lateral-movement/brute-force.md)를 봅니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 Windows 이미지에서 `Security.evtx` 를 꺼내 사본으로 풀어 봅니다.

1. 4624 를 유형별로 세어 봅니다. 가장 많은 유형은 무엇이고, 어떤 계정이 대부분을 차지합니까?
2. 유형 2 기록에서 `Window Manager` 도메인의 `DWM-` 계정처럼 사람이 아닌 계정을 걸러 내면 몇 건이 남습니까?
3. 유형 10 기록이 있다면 원본 주소는 무엇입니까? 같은 시각대에 유형 3 기록도 있습니까?
4. 유형 3 기록 가운데 계정 이름이 `$` 로 끝나지 않고 `ANONYMOUS LOGON` 도 아닌 기록은 어느 주소에서 왔습니까?
5. `TargetLinkedLogonId` 가 `0x0` 이 아닌 4624 두 건을 찾아 서로 가리키는지 확인해 봅니다.
6. 유형 9 기록이 있다면 `TargetUserName` 과 `TargetOutboundUserName` 은 각각 무엇입니까? 같은 시각대에 4648 이 있습니까?

## 참고 문헌

- Microsoft Learn, "4624(S) An account was successfully logged on", "4625(F) An account failed to log on", "4634(S) An account was logged off" (Windows 10 보안 감사 문서). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4624 , https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4625 , https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4634
- Microsoft Learn, "SECURITY_LOGON_TYPE enumeration (ntsecapi.h)". https://learn.microsoft.com/en-us/windows/win32/api/ntsecapi/ne-ntsecapi-security_logon_type
- Microsoft Learn, "Administrative tools and logon types reference". https://learn.microsoft.com/en-us/windows-server/identity/securing-privileged-access/reference-tools-logon-types
- Joachim Metz, libevtx, "Windows XML Event Log (EVTX) format". https://github.com/libyal/libevtx/blob/main/documentation/Windows%20XML%20Event%20Log%20(EVTX).asciidoc
- SigmaHQ, "Successful Overpass the Hash Attempt" 규칙 (win_security_overpass_the_hash.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/windows/builtin/security/account_management/win_security_overpass_the_hash.yml
- Randy Franklin Smith, Ultimate Windows Security, "Windows Security Log Event ID 4624". https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4624
