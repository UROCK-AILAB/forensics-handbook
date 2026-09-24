# 기록이 남는 위치 (로컬 PC와 도메인 컨트롤러)

> 위치: 아티팩트 사전 > 이벤트 로그 > [로그온·로그오프 (Logon Events)](index.md)

## 한 줄 요약

로그온 관련 이벤트는 이벤트마다 남는 컴퓨터가 다릅니다. 세션이 만들어진 도착 PC, 자격 증명을 넣은 출발 PC, 인증을 처리한 도메인 컨트롤러 (Domain Controller) 에 각각 다른 기록이 남습니다. 한 컴퓨터의 로그만 보면 접속의 일부만 보입니다. 이 페이지로 어느 컴퓨터의 보안 로그를 모아야 하는지 정합니다.

## 무엇을 기록하나 · 왜 생기나

이벤트는 그 일을 처리한 컴퓨터에 남습니다. 로그온 한 번에는 여러 일이 들어 있고, 일마다 처리하는 컴퓨터가 다릅니다.

| 하는 일 | 처리하는 컴퓨터 | 남는 이벤트 |
|---|---|---|
| 로그온 세션을 만듭니다 | 접속을 받은 컴퓨터 | 4624, 4625 |
| Kerberos 티켓을 발급합니다 | 도메인 컨트롤러 | 4768, 4769 |
| NTLM 자격 증명을 확인합니다 | 자격 증명의 주인인 컴퓨터 | 4776 |
| 자격 증명을 직접 지정해 로그온을 시도합니다 | 문서에 직접 적혀 있지 않습니다 (아래 설명) | 4648 |

Microsoft 의 로그온 감사 (Audit Logon) 문서는 이 하위 범주를 이렇게 설명합니다.

로그온 감사 이벤트는 로그온 세션을 만드는 일과 관련이 있고 접속을 받은 컴퓨터에 남습니다. 대화형 로그온이면 로그온한 그 컴퓨터에 남고, 공유 폴더 접근 같은 네트워크 로그온이면 접근한 자원이 있는 컴퓨터에 남습니다. 이 하위 범주에 드는 이벤트는 4624, 4625, 4648, 4675 입니다.

4648 은 이 하위 범주에 들어 있지만 성격이 다릅니다. 그래서 아래에서 따로 다룹니다.

## 위치와 버전별 차이

### 이벤트별로 남는 컴퓨터

"근거" 칸의 "문서" 는 Microsoft 문서에 그대로 적힌 내용입니다. "해석" 은 문서의 다른 사실에서 끌어낸 판단입니다.

| 이벤트 | 남는 컴퓨터 | 근거 | 자세히 |
|---|---|---|---|
| 4624 | 접속을 받은 컴퓨터. 곧 세션이 만들어진 컴퓨터 | 문서 | [로그온 세션 잇기](logon-id-4624-4634-4647.md) |
| 4625 | 접속을 받은 컴퓨터 | 문서 (로그온 감사 하위 범주 설명) | [로그온 실패와 실패 코드](4625.md) |
| 4634 · 4647 | 세션이 있던 컴퓨터 | 해석. 문서는 로그온 ID 로 같은 컴퓨터의 4624 와 짝짓는다고 적습니다. 로그오프 감사 문서는 이번에 확인하지 못했습니다 | [로그온 세션 잇기](logon-id-4624-4634-4647.md) |
| 4648 | 자격 증명을 넣은 프로세스가 돈 컴퓨터 | 해석. 아래 "4648 을 따로 보는 이유" 를 봅니다 | [명시적 자격 증명·특수 권한](4648-4672.md) |
| 4672 | 권한이 붙은 세션이 있는 컴퓨터 | 해석. 문서는 `SubjectLogonId` 로 4624 와 잇는다고만 적습니다 | [명시적 자격 증명·특수 권한](4648-4672.md) |
| 4768 · 4769 | 도메인 컨트롤러만 | 문서 | [도메인 인증 이벤트](4768-4769-4776.md) |
| 4776 | 자격 증명의 주인인 컴퓨터. 도메인 계정은 도메인 컨트롤러, 로컬 계정은 그 컴퓨터 | 문서 | [도메인 인증 이벤트](4768-4769-4776.md) |

화면 잠금·해제 이벤트는 [화면 잠금·해제](4800-4801.md)에서 다룹니다.

- 4624·4634·4647·4648·4672·4776 은 Vista·Server 2008 부터 있습니다.
- 4768·4769 는 Windows Server 2008 이후의 Active Directory 도메인 컨트롤러에서 생깁니다.

### 4648 을 따로 보는 이유

4648 문서는 이 이벤트가 어느 컴퓨터에 남는지 직접 적지 않고, 프로세스가 자격 증명을 지정해 로그온을 시도할 때 4648 이 생긴다고만 적습니다. 자격 증명을 쓸 대상은 `TargetServerName` 칸에 따로 적히며, 대상이 로컬이면 `localhost` 입니다. 그래서 4648 은 자격 증명을 넣은 프로세스가 돈 컴퓨터, 곧 출발 쪽에 남는다고 해석합니다. 다만 대상이 원격 컴퓨터일 때 실제로 출발 PC 에 남는지는 이번에 연 자료로 확인하지 못했습니다.

로그온 감사 문서는 이 하위 범주가 "접속을 받은 컴퓨터" 에 남는다고 적는데, 이 설명은 4648 과 맞지 않을 수 있습니다. 4769 문서는 로그온 GUID 가 "티켓이 발급된 대상 컴퓨터" 의 4624·4648·4964 와 이어진다고 적으며, 4648 이 출발 쪽에 남는다는 해석과 이 문장이 어떻게 맞는지는 이번 자료로 가리지 못했습니다.

이런 까닭에 4648 을 찾을 때는 출발 PC 와 도착 PC 를 모두 봅니다. 찾은 4648 이 어느 컴퓨터의 로그에서 나왔는지 보고서에 적습니다.

### 감사 설정과 기록 양

Microsoft 의 로그온 감사 문서는 도메인 컨트롤러·멤버 서버·워크스테이션 모두에서 성공과 실패를 감사하라고 권하지만, 권장은 권장일 뿐이므로 컴퓨터마다 실제 감사 설정을 [감사 정책과 로그 설정](../audit-policy-log-settings.md)에서 확인합니다. 같은 문서는 로그온 감사 이벤트의 양이 클라이언트에서는 적고, 도메인 컨트롤러·네트워크 서버에서는 중간이라고 적습니다. 컴퓨터마다 쌓이는 양이 다르므로 로그가 거슬러 올라가는 기간도 다를 수 있어서, 모은 로그마다 첫 기록의 시각을 적어 둡니다.

## 구조

### 한 번의 원격 접속이 남기는 기록

아래 표는 위 문서들의 사실을 이어 붙인 해석입니다. 한 문서에 이 그림이 그대로 적혀 있지는 않습니다. 도메인 계정으로 출발 PC 에서 도착 PC 에 접속하는 경우입니다.

> 그림 자리: 출발 PC, 도메인 컨트롤러, 도착 PC 세 대를 그리고 각 컴퓨터에 남는 이벤트(출발 PC 4648 / 도메인 컨트롤러 4768·4769 또는 4776 / 도착 PC 4624·4672·4634)와, 셋을 잇는 값(로그온 GUID, IP 주소, 컴퓨터 이름)을 선으로 이어 보여 주는 그림

| 컴퓨터 | 남을 수 있는 이벤트 | 여기서 읽을 값 |
|---|---|---|
| 출발 PC | 4648. 자격 증명을 직접 지정했을 때입니다 | 자격 증명을 넣은 계정과 쓰인 계정, `TargetServerName`, `ProcessName`, 로그온 GUID |
| 도메인 컨트롤러 (Kerberos) | 4768, 4769 | 요청한 계정, 요청한 컴퓨터의 IP, 4769 의 `ServiceName`(대상 계정·컴퓨터), 4769 의 로그온 GUID |
| 도메인 컨트롤러 (NTLM) | 4776 | 확인한 계정, `Workstation`(출발 컴퓨터 이름) |
| 도착 PC | 4624, 4672, 4634 | 로그온 유형, 워크스테이션 이름, IP, 로그온 ID, 로그온 GUID |

### 컴퓨터 사이를 잇는 값

| 잇는 값 | 잇는 기록 | 조건 |
|---|---|---|
| 로그온 GUID (Logon GUID) | 도메인 컨트롤러의 4769 와 대상 컴퓨터의 4624·4648·4964. 4648 문서는 4769 와 같은 컴퓨터의 4624·4964 를 잇는다고 적습니다 | 잡히지 않으면 모두 0 입니다. 0 끼리는 이을 수 없습니다 |
| IP 주소 | 도메인 컨트롤러 4768·4769 의 `IpAddress` 는 요청을 보낸 컴퓨터의 IP 입니다. 도착 PC 4624 의 `IpAddress` 와 맞춥니다 | NTLM 로그온의 4624 에는 TCP/IP 정보가 없기 쉽습니다 |
| 컴퓨터 이름 | 4776 의 `Workstation` 은 출발 컴퓨터 이름입니다. 도착 PC 4624 의 `WorkstationName` 과 맞춥니다 | Kerberos 네트워크 로그온의 4624 에는 워크스테이션 정보가 없기 쉽습니다 |
| 계정 이름 | 모든 이벤트 | 4769 는 `이름@전체 도메인 이름` 꼴이라 모양이 다릅니다 |
| 로그온 ID (Logon ID) | 한 컴퓨터 안의 4624·4634·4647·4648·4672 | 다른 컴퓨터끼리는 쓸 수 없습니다. 같은 컴퓨터에서도 재부팅 사이에서만 겹치지 않습니다 |

IP 와 이름을 컴퓨터로 바꿀 때는 [네트워크 인터페이스 설정](../../network/tcp-ip-interfaces.md)과 [시스템 기본 정보](../../system-account/os-version-computer-name-install-date-shutdown-t.md)를 봅니다.

### 인증 방식과 계정 종류에 따른 차이

| 경우 | 도메인 컨트롤러에 남는 것 | 로그온한 컴퓨터에 남는 것 | 근거 |
|---|---|---|---|
| 도메인 계정, Kerberos | 4768, 4769 | 4624. 네트워크 로그온이면 워크스테이션 정보가 없기 쉽습니다 | 문서 |
| 도메인 계정, NTLM | 4776. 출발 컴퓨터 이름만 있습니다 | 4624. TCP/IP 정보가 없기 쉽습니다 | 문서 |
| 로컬 계정 | 이 계정의 4776 은 남지 않습니다 | 4624 가 남습니다. NTLM 으로 자격 증명을 확인했으면 4776 도 이 컴퓨터에 남습니다 | 문서 |
| 캐시된 자격 증명으로 로그온 (유형 11, CachedInteractive) | 기록이 없을 수 있습니다 | 4624 유형 11 | 해석. 문서는 이 유형이 도메인 컨트롤러에 연락하지 않고 확인한다고 적습니다 |
| 도메인 계정이 도메인 컨트롤러에 직접 로그온 | 4776 은 생기지 않습니다 | (로그온한 컴퓨터가 곧 도메인 컨트롤러입니다) | 문서 |

- 계정이 저장된 컴퓨터에 로컬로 로그온하면 늘 NTLM 인증을 씁니다.
- 로그온 유형의 뜻은 [로그온 유형 해석](logon-type.md)에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 한 컴퓨터의 로그에 이벤트가 있으면, 그 컴퓨터가 그 일을 처리했습니다 | 한 컴퓨터에 기록이 없으면 그 일이 없었다는 것. 다른 컴퓨터에 남았을 수 있습니다 |
| 로그온 GUID 가 0 이 아니고 같으면, 문서가 잇는 값이라고 적은 두 기록이 이어집니다 | IP·이름·시각으로 이은 두 기록이 같은 접속이라는 것. 이렇게 이은 것은 추정입니다 |
| 도메인 컨트롤러의 4768·4769·4776 은 요청한 쪽의 주소나 이름을 보여 줍니다 | 도메인 컨트롤러가 여러 대일 때 어느 컨트롤러가 요청을 처리했는지. 이번 자료로는 정하지 못합니다 |

보고서에는 어느 컴퓨터의 로그에서 나온 기록인지, 기록을 무엇으로 이었는지 함께 적습니다. 아래 컴퓨터 이름과 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "PC-B 의 Security 로그에 2024-03-15 01:02:05 UTC 의 4624(유형 3)가 있습니다. 도메인 컨트롤러 DC-1 의 Security 로그에 01:02:04 UTC 의 4769 가 있습니다. 두 기록의 로그온 GUID 는 같습니다. DC-1 의 시각은 PC-B 와의 시계 차이를 보정한 값입니다."
- 쓰면 안 되는 문장: "PC-B 의 로그인 기록으로 보아 PC-A 에서 접속한 것이 확실합니다."

두 번째 문장은 PC-A 의 기록을 보지 않고 출발지를 단정합니다.

## 시각 해석

- 모든 이벤트의 `TimeCreated SystemTime` 은 끝에 `Z` 가 붙은 UTC 형식입니다.
- 시각은 이벤트를 남긴 컴퓨터의 시계를 따릅니다. 출발 PC, 도착 PC, 도메인 컨트롤러의 시계는 서로 다를 수 있습니다.
- 세 컴퓨터의 기록을 한 줄로 세우기 전에 컴퓨터마다 시계 차이를 구합니다. 방법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md)에서 다룹니다.
- 보정하기 전에는 컴퓨터를 넘나드는 앞뒤 순서를 단정하지 않습니다.
- 도메인 컨트롤러의 4768 Result Code 0x25 는 시계 차이가 너무 크다는 뜻입니다. [도메인 인증 이벤트](4768-4769-4776.md)를 봅니다.
- 시스템 시각을 바꾼 기록은 컴퓨터마다 [시간 변경](../4616-kernel-general.md)에서 찾습니다.

## 함정과 한계

1. **도착 PC 한 대의 로그만 봅니다.** 출발 PC 의 4648 과 도메인 컨트롤러의 인증 기록이 빠집니다. 도착 PC 의 4624 에는 출발지 정보가 비어 있을 수도 있습니다.
2. **PC 에서 Kerberos 기록을 찾습니다.** 4768·4769 는 도메인 컨트롤러에만 남습니다.
3. **4776 으로 도착 컴퓨터를 찾습니다.** 4776 에는 출발 컴퓨터 이름만 있습니다. 도착 컴퓨터는 그 컴퓨터의 4624 에서 찾습니다.
4. **로그온 ID 를 컴퓨터끼리 맞춥니다.** 로그온 ID 는 한 컴퓨터 안에서만 뜻이 있습니다. 컴퓨터 사이는 로그온 GUID, IP, 이름으로 잇습니다.
5. **로그온 감사 문서의 설명을 4648 에도 적용합니다.** "접속을 받은 컴퓨터에 남는다" 는 설명은 4648 과 맞지 않을 수 있습니다. 4648 은 출발 PC 와 도착 PC 에서 모두 찾아봅니다.
6. **도메인 컨트롤러에 기록이 없으면 로그온도 없었다고 봅니다.** 캐시된 자격 증명 로그온은 도메인 컨트롤러에 연락하지 않습니다. 로컬 계정의 자격 증명 확인은 그 컴퓨터에 남습니다.
7. **도메인 컨트롤러 한 대의 로그만 모읍니다.** 인증을 처리한 컨트롤러에만 기록이 남는다는 설명이 흔하지만, 이번에 연 Microsoft 문서에서는 확인하지 못했습니다. 어느 컨트롤러가 처리했는지 이 자료로는 정하지 못하므로, 빠짐없이 보려면 모든 컨트롤러의 보안 로그를 모읍니다.
8. **모든 컴퓨터의 감사 설정이 같다고 봅니다.** 컴퓨터마다 감사 정책과 로그 크기가 다를 수 있습니다. 한 컴퓨터에만 기록이 없다면 그 컴퓨터의 설정을 먼저 확인합니다.
9. **모든 로그가 같은 날까지 거슬러 올라간다고 봅니다.** 기록이 쌓이는 양이 컴퓨터마다 다릅니다. 로그마다 첫 기록의 시각을 적고, 그보다 앞선 일은 그 로그로 말하지 않습니다.

### 지우기와 조작

- 한 컴퓨터의 로그를 지워도 다른 컴퓨터의 기록은 남습니다. PC 의 로그가 지워졌으면 도메인 컨트롤러와 상대 PC 의 기록으로 빈자리를 메웁니다.
- 지운 흔적은 [이벤트 로그 삭제](../1102-104.md)에서 찾습니다. 여러 흔적을 모아 읽는 순서는 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 직접 분석해 보기

### 수집 범위 정하기

1. 조사 대상 컴퓨터(도착 PC)의 보안 로그를 모읍니다.
2. 도착 PC 의 4624 에 적힌 IP·워크스테이션 이름으로 출발 PC 를 찾습니다. 찾으면 출발 PC 의 보안 로그도 모읍니다.
3. 도메인 계정이 쓰였으면 도메인 컨트롤러의 보안 로그를 모읍니다. 컨트롤러가 여러 대면 모두 모읍니다.
4. 로컬 계정이 쓰였으면 그 계정이 있는 컴퓨터의 4776 을 봅니다.
5. 컴퓨터마다 감사 설정, 로그 크기, 첫 기록 시각, 시계 차이를 적습니다.

모으는 방법은 [증거 획득](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)과 [라이브 응답](../../../03-techniques/process-acquisition/live-response/index.md)에서 다룹니다.

### 공개 도구로 한 번

모은 로그마다 어떤 이벤트가 몇 건, 어느 기간에 있는지 먼저 봅니다. 아래는 Windows 에 들어 있는 PowerShell 로 한 폴더의 사본 파일들을 훑는 예입니다. 파일 이름은 컴퓨터 이름으로 붙여 둡니다.

```powershell
$xpath = "*[System[(EventID=4624 or EventID=4634 or EventID=4647 or EventID=4648 or EventID=4672 or EventID=4768 or EventID=4769 or EventID=4776)]]"
Get-ChildItem .\logs\*.evtx | ForEach-Object {
  $file = $_.Name
  Get-WinEvent -Path $_.FullName -FilterXPath $xpath -Oldest -ErrorAction SilentlyContinue |
    Group-Object Id | ForEach-Object {
      $t = $_.Group.TimeCreated | Sort-Object
      [pscustomobject]@{
        File     = $file
        EventId  = $_.Name
        Count    = $_.Count
        FirstUtc = $t[0].ToUniversalTime()
        LastUtc  = $t[-1].ToUniversalTime()
      }
    }
} | Sort-Object File, EventId | Format-Table
```

- 도메인 컨트롤러 파일에 4768·4769 가 없으면 Kerberos 감사가 꺼져 있었는지 먼저 봅니다.
- PC 파일에 4768·4769 가 있으면 그 파일이 정말 PC 의 로그인지 다시 확인합니다.
- 파일마다 `FirstUtc` 가 다르면 그 차이만큼 볼 수 있는 기간이 다릅니다.
- 도구가 여러 파일을 합쳐 보여 줄 때 어느 컴퓨터의 기록인지 칸이 남는지 확인합니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 무엇을 맞춰 보나 | 링크 |
|---|---|---|
| 도착 PC 의 로그온 유형 | 접속 방식에 따라 출발지 칸이 어떻게 채워지는지 | [로그온 유형 해석](logon-type.md) |
| 원격 데스크톱 로그 | 원격 데스크톱 접속이 출발 PC 와 도착 PC 에 남긴 기록 | [원격 데스크톱 이벤트](../rdp-event-logs/index.md) |
| 공유 폴더 접근 기록 | 네트워크 로그온 뒤 도착 PC 에서 어떤 공유에 접근했는지 | [공유 폴더 접근](../5140-5145.md) |
| 출발 PC 의 연결 흔적 | 출발 PC 에서 연결한 공유·드라이브 | [공유 폴더·네트워크 드라이브](../../network/network-shares-mapped-drives.md) |
| 컴퓨터별 감사 설정 | 기록이 없는 까닭이 설정 때문인지 | [감사 정책과 로그 설정](../audit-policy-log-settings.md) |

세 컴퓨터의 기록을 합쳐 읽는 순서는 [계정 탈취와 측면 이동](../../../04-scenarios/incident/credential-theft-lateral-movement/index.md)과 [원격 데스크톱 침입 확인](../../../04-scenarios/incident/rdp-intrusion.md)에서 다룹니다.

## 실습

도메인 컨트롤러 한 대와 도메인에 가입한 PC-A·PC-B 로 실습 환경을 만듭니다. 각 단계의 시각을 적고, 끝나면 세 컴퓨터의 보안 로그를 모두 모읍니다.

1. PC-A 에 도메인 계정으로 로그온한 뒤, 다른 도메인 계정의 자격 증명을 넣어 PC-B 의 공유 폴더에 접속합니다. 세 컴퓨터에 각각 어떤 이벤트가 남았는지 표로 적습니다.
2. 1번에서 PC-A 에 4648 이 남았습니까? PC-B 에도 4648 이 있습니까? 위 "4648 을 따로 보는 이유" 의 답이 여기서 나옵니다.
3. 도메인 컨트롤러의 4769, PC-B 의 4624, PC-A 의 4648 에서 로그온 GUID 를 비교합니다. 어느 두 기록의 값이 같습니까?
4. PC-B 의 로컬 계정으로 PC-A 에서 PC-B 에 접속합니다. 4776 이 어느 컴퓨터에 남는지, 도메인 컨트롤러에 무엇이 남는지 봅니다.
5. 도메인 컨트롤러를 끈 채 PC-A 에 도메인 계정으로 로그온합니다. PC-A 의 4624 로그온 유형을 보고, 컨트롤러를 켠 뒤 그 시각의 기록이 있는지 봅니다.
6. 도메인 컨트롤러를 두 대로 늘릴 수 있으면 1번을 되풀이합니다. 인증 기록이 한 대에만 남는지, 두 대에 모두 남는지 봅니다. 위 함정 7번의 답이 여기서 나옵니다.

## 참고 문헌

- Microsoft Learn, "Audit Logon" — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-logon
- Microsoft Learn, "4624(S) An account was successfully logged on." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4624
- Microsoft Learn, "4634(S) An account was logged off." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4634
- Microsoft Learn, "4647(S) User initiated logoff." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4647
- Microsoft Learn, "4648(S) A logon was attempted using explicit credentials." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4648
- Microsoft Learn, "4672(S) Special privileges assigned to new logon." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4672
- Microsoft Learn, "4768(S, F) A Kerberos authentication ticket (TGT) was requested." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4768
- Microsoft Learn, "4769(S, F) A Kerberos service ticket was requested." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4769
- Microsoft Learn, "4776(S, F) The computer attempted to validate the credentials for an account." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4776
