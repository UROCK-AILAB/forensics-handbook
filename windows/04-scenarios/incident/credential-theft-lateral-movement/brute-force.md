# 비밀번호 대입 공격이 있었나 (Brute Force)

> 상위 허브: [계정 탈취와 측면 이동 (Credential Theft·Lateral Movement)](index.md)

이 페이지는 누군가 비밀번호를 거듭 맞혀 보려 했는지, 그러다 계정이 잠겼는지, 결국 들어오는 데 성공했는지를 로그로 확인하는 순서를 다룹니다. 로그온 실패 이벤트(4625)의 칸과 실패 코드는 [로그온 실패와 실패 코드](../../../02-artifacts/event-logs/logon-events/4625.md) 에 있습니다. 이 페이지는 그 이벤트를 대입 공격 판단에 쓰는 방법과 계정 잠김(4740)을 다룹니다.

이 페이지에서 "(관찰)" 을 붙인 내용은 Windows 11 Home(빌드 26200) 분석 PC 한 대에서 직접 본 것입니다(확인 범위: Win11 Home 한 대). 다른 빌드에서는 다를 수 있습니다.

## 조사 질문

- 이 PC 나 이 도메인에서 비밀번호를 거듭 틀린 시도가 있었습니까?
- 한 계정을 집중해서 노렸습니까, 아니면 여러 계정에 흔한 비밀번호 몇 개를 뿌렸습니까?
- 대입 도중 계정이 잠겼습니까?
- 실패가 이어진 뒤에 같은 계정으로 로그온에 성공한 기록이 있습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 로그온 실패 감사는 Windows 10 1809 부터 기본으로 켜집니다. 그 전 클라이언트는 설정을 바꾸지 않았다면 4625 가 남지 않습니다. 자세한 표는 [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) 에 있습니다. |
| 시간대 | 이벤트 시각은 UTC 로 저장됩니다. 뷰어가 현지 시각으로 바꿔 보여 주기도 합니다. [시간대 설정](../../../02-artifacts/system-account/time-zone.md) 을 먼저 정합니다. |
| 계정 종류 | 4625 는 로그온을 시도한 컴퓨터에 남습니다. 도메인 계정이면 도메인 컨트롤러에도 4771·4776 이 남습니다[4]. |
| 수집 범위 | 이 PC 의 보안 로그를 확보합니다. 도메인 환경이면 도메인 컨트롤러의 보안 로그도 확보합니다. |
| 감사 정책·로그 크기 | 감사가 꺼져 있었으면 시도가 있어도 4625 가 없습니다. 실패가 한꺼번에 쏟아지면 그 전 기록이 밀려납니다. [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 확인합니다. |

## 공격 모양 나누기

MITRE ATT&CK 은 비밀번호 대입을 T1110(Brute Force) 으로 두고, 아래 네 가지로 나눕니다[1].

| 하위 기법 | 뜻 | 대상 PC 에 시도가 남나 |
|---|---|---|
| T1110.001 Password Guessing | 한 계정에 비밀번호를 거듭 짐작합니다 | 남습니다 |
| T1110.002 Password Cracking | 이미 손에 넣은 해시 같은 자료를 대상 밖에서 풉니다 | 남지 않습니다 |
| T1110.003 Password Spraying | 흔한 비밀번호 몇 개를 여러 계정에 시도합니다 | 남습니다 |
| T1110.004 Credential Stuffing | 다른 사고에서 새어 나온 자격 증명을 시도합니다 | 남습니다 |

- 크래킹(T1110.002)은 대상 PC 밖에서 일어납니다. 그래서 대상 PC 로그에는 시도가 남지 않습니다. 손에 넣은 해시가 어디서 나왔는지는 [자격 증명을 빼냈나](credential-dumping.md) 에서 다룹니다.
- MITRE 는 대입이 지나가는 길로 RPC 인증, SMB, SSH, RDP, 외부 원격 서비스를 듭니다[1].
- MITRE 의 탐지 절은 로그온 실패·인증 실패·스프레이 모양을 보라고 하면서도, 윈도 이벤트 ID 를 직접 적지는 않습니다[1]. 그래서 아래는 MITRE 의 정의를 윈도 4625 칸에 옮겨 읽은 것입니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 보안 로그 4625 | 실패한 계정 이름, 로그온 유형, 원본 주소, 실패 코드 | [로그온 실패와 실패 코드](../../../02-artifacts/event-logs/logon-events/4625.md) |
| 2 | 보안 로그 4740 | 계정이 잠긴 시각, 잠금을 부른 컴퓨터 이름 | 이 페이지 아래 |
| 3 | 보안 로그 4624 | 실패가 이어진 뒤 같은 계정·같은 주소로 성공했는지 | [로그온 세션 잇기](../../../02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md) |
| 4 | 도메인 컨트롤러 4771·4776 | 도메인 계정 실패가 도메인 쪽에 어떻게 남았나 | [도메인 인증 이벤트](../../../02-artifacts/event-logs/logon-events/4768-4769-4776.md) |
| 5 | 원격 데스크톱 이벤트 | 원격 데스크톱으로 들어온 대입 시도 | [원격 데스크톱 이벤트](../../../02-artifacts/event-logs/rdp-event-logs/1149-4624-10-4625.md) |

## 4625 로 대입 모양 읽기

- 4625 의 칸·로그온 유형·실패 코드는 [로그온 실패와 실패 코드](../../../02-artifacts/event-logs/logon-events/4625.md) 에 정리돼 있습니다. 여기서는 여러 건을 묶어 모양을 보는 방법만 다룹니다.
- 한 계정에 비밀번호를 여러 번 틀린 모양이면 짐작(Guessing)에 가깝습니다.
- 계정 여러 개에 한두 번씩 틀린 모양이면 스프레이(Spraying)에 가깝습니다.
- 실패 코드로도 나눕니다. 없는 계정을 뜻하는 Sub Status 0xC0000064 가 이어지면 계정 이름을 짐작하는 단계일 수 있습니다. Microsoft 도 이 코드가 연달아 나오면 계정 이름 탐색의 신호일 수 있다고 적습니다[4]. 실제 계정에 비밀번호만 틀리는 0xC000006A 가 이어지면 그 계정 이름은 맞았다는 뜻입니다. 코드 뜻은 [로그온 실패와 실패 코드](../../../02-artifacts/event-logs/logon-events/4625.md) 의 실패 코드 표에 있습니다.
- 실패가 이어질 때는 간격도 봅니다. 사람이 손으로 치기 어려운 짧은 간격으로 수십·수백 건이 이어지면 프로그램이 보낸 시도일 수 있습니다.

## 4740 (계정 잠김)

계정이 잠길 때마다 4740 이 생깁니다[2]. 사용자 계정에 대해 도메인 컨트롤러·멤버 서버·워크스테이션 모두에서 남습니다[2]. 하위 범주는 계정 관리 감사(Audit User Account Management)입니다[2].

### 칸

Microsoft 문서의 예시에 나오는 EventData 칸은 아래 순서입니다[2].

| 묶음 | 칸 이름 | 뜻 |
|---|---|---|
| 잠긴 계정 | TargetUserName, TargetSid | 잠긴 계정의 이름과 SID |
| 잠금을 남긴 쪽 | SubjectUserSid, SubjectUserName, SubjectDomainName, SubjectLogonId | 계정을 잠근 계정. 보통 SYSTEM 입니다 |

- 잠금을 남긴 쪽(Subject)은 예시에서 SYSTEM(S-1-5-18)입니다[2]. 사람이 아니라 시스템이 잠금을 기록합니다.
- 화면에 보이는 "Caller Computer Name" 은 로그온 시도를 받아 계정을 잠그게 만든 컴퓨터 이름입니다[2]. 도메인 밖 컴퓨터라도 이 칸에는 IP 가 아니라 컴퓨터 이름이 들어갑니다[2].

### TargetDomainName 을 도메인으로 읽으면 안 됩니다

- XML 에는 CallerComputerName 이라는 칸이 따로 없습니다. Caller Computer Name 값은 XML 의 TargetDomainName 칸에 들어 있습니다(관찰). 이 PC 의 4740 메시지 틀이 "Caller Computer Name: %2" 이고, %2 는 두 번째 칸인 TargetDomainName 입니다(관찰).
- Microsoft 예시도 TargetDomainName 값과 Caller Computer Name 설명의 예가 같습니다[2].
- 그래서 XML 로 거를 때 TargetDomainName 을 "잠긴 계정의 도메인" 으로 읽으면 안 됩니다. 이 칸은 시도를 보낸 컴퓨터를 가리킵니다.
- 이 컴퓨터 이름은 대입 시도가 어디서 왔는지 좁히는 단서가 됩니다.

### 무엇을 보나

- 잠금을 남긴 쪽(Subject)이 SYSTEM 이 아니면 따로 봅니다[2].
- 중요한 계정이 잠겼으면 모두 봅니다[2].
- 그 계정을 써서는 안 되는 컴퓨터가 Caller Computer Name 에 있으면 눈여겨봅니다[2].
- 도메인 밖 컴퓨터 이름이 Caller Computer Name 에 있는지 봅니다[2].
- 계정을 다시 푼 기록은 4767 로 남습니다. 같은 계정 관리 감사 하위 범주입니다[3].

## 잠금 정책과 실패 코드의 관계

- 이 분석 PC 의 `net accounts` 결과는 잠금 임계값 10, 잠금 기간 10분, 관찰 창 10분이었습니다(관찰). 실제 임계값은 검체마다 다릅니다.
- 잠금 정책이 있으면 대입 도중 임계값에 이르는 순간 4740 이 생깁니다.
- 그 뒤로는 비밀번호가 맞아도 4625 의 실패 코드가 잠김(0xC0000234)으로 바뀝니다. 코드 뜻은 [로그온 실패와 실패 코드](../../../02-artifacts/event-logs/logon-events/4625.md) 를 봅니다.
- MITRE 는 대입을 막는 수단으로 잠금 정책을 들면서, 정책이 너무 엄격하면 서비스 거부 상태를 만들 수 있다고 적습니다[1].

## 도메인 계정과 원격 데스크톱

- 4625 는 로그온을 시도한 컴퓨터에 남습니다[4]. 도메인 계정의 인증 실패는 도메인 컨트롤러에도 4771·4776 으로 남습니다. 도메인 컨트롤러에 직접 인증을 시도하면 다른 PC 에는 4625 가 없고 도메인 컨트롤러에만 남을 수 있습니다. [도메인 인증 이벤트](../../../02-artifacts/event-logs/logon-events/4768-4769-4776.md) 와 [기록이 남는 위치](../../../02-artifacts/event-logs/logon-events/pc.md) 를 봅니다.
- 원격 데스크톱으로 들어온 대입은 로그온 유형이 NLA 설정에 따라 달라집니다. [원격 데스크톱 이벤트](../../../02-artifacts/event-logs/rdp-event-logs/1149-4624-10-4625.md) 와 [원격 데스크톱 침입 확인](../rdp-intrusion.md) 을 봅니다.

## 분석 흐름

1. 시간대 설정을 읽어 UTC 와 현지 시각의 차이를 정합니다.
2. 감사 정책과 로그 크기를 확인해 그 기간에 4625 가 남을 조건이었는지 봅니다.
3. 4625 를 시각순으로 모읍니다. 계정 이름, 원본 주소, 로그온 유형, Status·Sub Status 를 표로 적습니다.
4. 계정 이름이 하나로 몰리는지(짐작), 여러 계정에 흩어지는지(스프레이) 봅니다.
5. 같은 구간의 4740 을 찾습니다. Caller Computer Name(XML 의 TargetDomainName 칸)으로 시도를 보낸 컴퓨터를 좁힙니다.
6. 실패가 이어진 뒤 같은 계정·같은 주소로 4624 가 있는지 봅니다. 있으면 성공 가능성을 다른 근거와 함께 봅니다.
7. 도메인 계정이 섞여 있으면 도메인 컨트롤러의 4771·4776 을 함께 봅니다.
8. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **실패 건수만으로 공격이라고 봅니다.** 비밀번호를 바꾼 뒤 옛 비밀번호를 쥔 서비스·예약 작업·네트워크 드라이브가 계속 실패를 만들 수 있습니다. 호출 프로세스, 로그온 유형, 반복 간격을 함께 봅니다.
2. **4740 의 TargetDomainName 을 잠긴 계정의 도메인으로 읽습니다.** 이 칸에는 시도를 보낸 컴퓨터 이름이 들어갑니다.
3. **잠금을 남긴 Subject 를 공격자로 봅니다.** 이 칸은 보통 SYSTEM 입니다. 잠금을 부른 컴퓨터는 Caller Computer Name 에 있습니다.
4. **4625 가 없으면 대입도 없었다고 봅니다.** 감사가 꺼져 있었거나, 크래킹처럼 대상 밖에서 일어났거나, 도메인 계정이라 도메인 컨트롤러에만 남았을 수 있습니다.
5. **로그에 남은 첫 실패를 공격의 시작으로 봅니다.** 실패가 쏟아지면 그 전 기록이 밀려납니다. 남은 첫 레코드보다 앞선 일은 이 로그로 말할 수 없습니다.
6. **원본 주소를 사람이 있던 곳으로 읽습니다.** IP 는 이 컴퓨터가 본 상대 주소입니다. NAT·VPN·중계 서버 뒤의 실제 출발지는 다른 기록으로 찾습니다.

## 보고서 문장 예

아래 시각·개수는 설명을 위해 만든 예입니다.

- 쓰지 않을 문장: "공격자가 무차별 대입으로 관리자 계정을 뚫었습니다."
- 쓸 문장: "이 PC 의 Security.evtx 에는 ○○부터 ○○(UTC) 사이 4625 가 ○○건 있습니다. 모두 로그온 유형 3 이고, `admin` 한 계정에 몰려 있습니다. Sub Status 는 모두 0xC000006A(비밀번호 틀림)입니다. 같은 구간에 그 계정의 4740 이 ○개 있고, Caller Computer Name 은 ○○입니다. 대입이 이어진 뒤 같은 계정으로 성공한 4624 는 이 로그에 없습니다. 이 기록은 해당 계정 이름이 실제 계정과 맞고 반복 실패가 있었음을 보여 줍니다. 시도한 사람과 성공 여부는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [로그온 실패와 실패 코드 (4625)](../../../02-artifacts/event-logs/logon-events/4625.md) — 4625 의 칸과 실패 코드입니다.
- [로그온 유형 해석](../../../02-artifacts/event-logs/logon-events/logon-type.md) · [로그온 세션 잇기](../../../02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md) — 시도 방식과 성공 여부를 잇습니다.
- [도메인 인증 이벤트 (4768·4769·4776)](../../../02-artifacts/event-logs/logon-events/4768-4769-4776.md) · [기록이 남는 위치](../../../02-artifacts/event-logs/logon-events/pc.md) — 도메인 계정 실패가 남는 곳입니다.
- [계정 생성·변경](../../../02-artifacts/event-logs/account-management-events.md) — 4740·4767 같은 계정 관리 이벤트 목록입니다.
- [원격 데스크톱 이벤트](../../../02-artifacts/event-logs/rdp-event-logs/1149-4624-10-4625.md) · [원격 데스크톱 침입 확인](../rdp-intrusion.md) — 원격 데스크톱 대입입니다.
- [윈도 방화벽](../../../02-artifacts/network/windows-firewall-pfirewall-log.md) — 같은 주소의 연결 기록입니다.
- [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) — 실패가 남을 조건과 로그 크기입니다.

## 참고 문헌

1. MITRE ATT&CK, "Brute Force, Technique T1110" — https://attack.mitre.org/techniques/T1110/
2. Microsoft Learn, "4740(S) A user account was locked out." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4740
3. Microsoft Learn, "Audit User Account Management" — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-user-account-management
4. Microsoft Learn, "4625(F) An account failed to log on." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4625
