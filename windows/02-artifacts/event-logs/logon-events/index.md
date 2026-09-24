# 로그온·로그오프 (Logon Events)

## 한 줄 요약

로그온·로그오프 이벤트 (Logon Events) 는 윈도가 보안 로그 (Security Log) 에 남기는 로그온 성공·실패, 로그오프, 화면 잠금, 인증 요청 기록입니다. 이 기록으로 어느 계정이 언제, 어떤 방식으로, 어디서 이 컴퓨터에 들어왔는지 확인합니다.

## 왜 중요한가

로그온 성공 (4624) 은 접속을 받은 컴퓨터에 남기 때문에, 이 컴퓨터에 세션을 연 계정과 그 시각을 바로 보여 줍니다. 로그온 유형 (Logon Type) 도 함께 남아서, 앞에 앉아 로그온했는지, 네트워크로 붙었는지, 원격 데스크톱으로 들어왔는지를 이 숫자로 나눕니다.

네트워크로 들어온 로그온에는 상대 컴퓨터 이름과 IP 주소가 남을 수 있으며, 어느 칸이 채워지는지는 인증 방식에 따라 다릅니다. Microsoft 문서는 Kerberos 네트워크 로그온에는 워크스테이션 이름이 없기 쉽고, NTLM 로그온에는 IP 주소·포트가 없다고 설명합니다.

로그온 ID (Logon ID) 가 같은 이벤트를 묶으면 한 세션의 시작, 특수 권한 부여, 끝을 이어 볼 수 있습니다. 로그온 실패 (4625) 에는 실패 이유 코드가 남아서, 없는 계정 이름인지, 비밀번호가 틀렸는지, 잠긴 계정인지를 이 코드로 나눕니다. 도메인에 가입한 환경에서는 도메인 컨트롤러 (Domain Controller) 에도 인증 기록 (4768·4769·4776) 이 남으며, PC 의 보안 로그가 지워졌어도 도메인 컨트롤러 쪽 기록은 따로 남아 있을 수 있습니다.

증명하지 못하는 것도 분명합니다.

- 이벤트에는 계정이 남습니다. 키보드 앞에 앉은 사람은 남지 않습니다. 여러 사람이 계정을 같이 썼거나 비밀번호가 새 나갔다면, 사람을 특정하는 데 다른 근거가 필요합니다.
- 로그오프 시각은 사용을 멈춘 시각이 아닙니다. 전원을 그냥 끄거나 네트워크가 끊기면 로그오프 이벤트가 아예 남지 않을 수 있습니다.
- 네트워크 로그온은 짧은 세션이 자주 생겼다 사라집니다. 로그온·로그오프 한 쌍이 사람이 한 번 접속한 것과 같지 않습니다.
- 감사 정책 (Audit Policy) 이 꺼져 있으면 이벤트가 생기지 않습니다. 화면 잠금·해제 (4800·4801) 는 기본으로 켜져 있지 않은 하위 범주에 속합니다. 그래서 기록이 없다는 것만으로 그 일이 없었다고 단정하지 않습니다.
- 보안 로그에는 크기 한도가 있습니다. 한도에 이르면 설정에 따라 오래된 기록이 밀려납니다. 남아 있는 첫 레코드보다 앞선 일은 이 로그로 말할 수 없습니다.
- 로그온 ID 는 같은 컴퓨터에서 다시 부팅하기 전까지만 겹치지 않습니다. 재부팅을 사이에 두고 같은 값이 나오면 다른 세션일 수 있습니다.

## 한눈에 보기

> 그림 자리: 한 계정이 PC-A 에서 PC-B 로 원격 접속할 때 PC-A(4648), 도메인 컨트롤러(4768·4769 또는 4776), PC-B(4624·4672·4634) 에 각각 남는 이벤트를 화살표로 이어 보여 주는 그림

### 위치와 형식

| 항목 | 내용 |
|---|---|
| 로그 파일 (Vista 이후) | `%SystemRoot%\System32\winevt\Logs\Security.evtx` |
| 로그 파일 (XP · 2003) | `%SystemRoot%\System32\config\SecEvent.Evt` |
| 채널 · 공급자 | 채널 `Security`, 공급자 `Microsoft-Windows-Security-Auditing` |
| 시각 | UTC. EVTX 는 FILETIME, EVT 는 32비트 POSIX 시각입니다. |
| 로그 파일 경로를 바꾼 경우 | SYSTEM 하이브 `ControlSet00X\Services\EventLog\Security` 키의 `File` 값에 경로가 남습니다. 값이 없으면 기본 폴더를 씁니다. |
| 무엇을 남길지 | 감사 정책이 정합니다. 확인하는 법은 [감사 정책과 로그 설정](../audit-policy-log-settings.md) 에서 다룹니다. |

파일 형식은 [이벤트 로그 형식 (EVTX·EVT·ETL)](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다. XP·2003 의 옛 형식은 [구형 EVT 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/windows-xp-2003.md) 에서 다룹니다.

### 이벤트 목록

| 이벤트 ID | 뜻 | 남는 컴퓨터 | 감사 하위 범주 | Windows 기본값 | XP·2003 의 옛 ID |
|---|---|---|---|---|---|
| 4624 | 로그온 성공 | 접속을 받은 컴퓨터 | 로그온 (Audit Logon) | 성공 켜짐 | 528, 540 |
| 4625 | 로그온 실패 | 로그온 시도를 받은 컴퓨터 | 로그온, 계정 잠금 (Audit Account Lockout) | 주 1 | 529~537, 539 |
| 4634 | 로그온 세션이 끝남 | 세션이 있던 컴퓨터 | 로그오프 (Audit Logoff) | 성공 켜짐 | 538 |
| 4647 | 사용자가 로그오프를 시작함 | 세션이 있던 컴퓨터 | 로그오프 | 성공 켜짐 | 551 |
| 4648 | 명시적 자격 증명으로 로그온을 시도함 | 그 자격 증명을 넣은 프로세스가 돈 컴퓨터 | 로그온 | 성공 켜짐 | 552 |
| 4672 | 새 로그온에 특수 권한이 붙음 | 로그온한 컴퓨터 | 특수 로그온 (Audit Special Logon) | 성공 켜짐 | 576 |
| 4800 · 4801 | 화면 잠금 · 잠금 해제 | 잠근 컴퓨터 | 기타 로그온/로그오프 (Audit Other Logon/Logoff Events) | 주 2 | 없음 |
| 4768 | Kerberos 인증 티켓 (TGT) 요청 | 도메인 컨트롤러 | Kerberos 인증 서비스 (Audit Kerberos Authentication Service) | 주 3 | 672, 676 |
| 4769 | Kerberos 서비스 티켓 요청 | 도메인 컨트롤러 | Kerberos 서비스 티켓 작업 (Audit Kerberos Service Ticket Operations) | 주 3 | 673 |
| 4776 | NTLM 자격 증명 확인 | 계정 정보가 저장된 컴퓨터 (도메인 계정은 도메인 컨트롤러, 로컬 계정은 그 PC) | 자격 증명 확인 (Audit Credential Validation) | 주 3 | 680, 681 |

기본값은 Microsoft 의 감사 정책 권장 표에 적힌 "Windows 기본값" 칸을 따릅니다. 옛 ID 는 Ultimate Windows Security 의 이벤트 사전을 따릅니다.

- 주 1. 권장 표는 Windows 10 1809 부터 로그온 하위 범주의 성공과 실패가 모두 기본으로 켜진다고 적습니다. 그보다 앞선 클라이언트 버전은 성공만 켜져 있습니다. 그래서 1809 보다 앞선 클라이언트에서는 설정을 바꾸지 않았다면 4625 가 남지 않습니다.
- 주 2. 권장 표의 Windows 기본값 칸이 비어 있습니다. 조직 정책으로 켠 경우에만 남는다고 보고, 수집한 감사 정책으로 확인합니다.
- 주 3. 권장 표에서 자격 증명 확인의 기본값은 꺼짐입니다. Kerberos 두 하위 범주의 기본값 칸은 비어 있습니다. 도메인 컨트롤러의 실제 설정은 그룹 정책에 따라 다르므로, 도메인 컨트롤러에서 수집한 감사 정책으로 확인합니다.

### Windows 버전에 따라 달라지는 점

| Windows 버전 | 달라지는 점 |
|---|---|
| XP · 2003 | 보안 로그가 EVT 형식 (`SecEvent.Evt`) 입니다. 이벤트 ID 는 세 자리 (528 등) 입니다. 화면 잠금·해제 이벤트는 없습니다. |
| Vista · Server 2008 | 보안 로그가 EVTX 형식 (`Security.evtx`) 으로 바뀝니다. 이벤트 ID 가 네 자리 (4624 등) 로 바뀝니다. 4624 의 이벤트 버전은 0 입니다. |
| 8 · Server 2012 | 4624 의 이벤트 버전이 1 입니다. 대리 실행 수준 (Impersonation Level) 칸이 생깁니다. |
| 10 | 4624 의 이벤트 버전이 2 입니다. 관리자 권한 토큰 (Elevated Token), 연결된 로그온 ID (Linked Logon ID), 제한된 관리자 모드 (Restricted Admin Mode), 가상 계정 (Virtual Account), 네트워크 계정 이름·도메인 칸이 생깁니다. |
| 10 1809 이후 | 로그온 실패 감사가 기본으로 켜집니다. 그래서 4625 가 기본으로 남습니다. |
| Server 2016 이후 도메인 컨트롤러 (2025년 1월 보안 업데이트 이후) | 4768·4769 의 새 판이 기록됩니다. 암호화 형식 칸이 붙고, 4769 에는 티켓 해시 칸도 붙습니다. |

### 알려 주는 것

| 알 수 있는 것 | 어디에 남나 | 자세히 |
|---|---|---|
| 어느 계정이 언제 로그온했나 | 4624 의 새 로그온 (New Logon) 계정과 기록 시각 | [로그온 세션 잇기](logon-id-4624-4634-4647.md) |
| 어떤 방식으로 들어왔나 | 4624·4625 의 로그온 유형 | [로그온 유형 해석](logon-type.md) |
| 어디서 들어왔나 | 4624·4625 의 워크스테이션 이름, 원본 네트워크 주소 | [로그온 유형 해석](logon-type.md) |
| 왜 실패했나 | 4625 의 상태 (Status) · 하위 상태 (Sub Status) 코드 | [로그온 실패와 실패 코드](4625.md) |
| 세션이 얼마나 이어졌나 | 로그온 ID 로 짝지은 4624 와 4634·4647 | [로그온 세션 잇기](logon-id-4624-4634-4647.md) |
| 자리를 비웠다 돌아왔나 | 4800·4801, 4624 의 로그온 유형 7 (잠금 해제) | [화면 잠금·해제](4800-4801.md) |
| 다른 계정의 자격 증명을 넣어 접속했나 | 4648 | [명시적 자격 증명·특수 권한](4648-4672.md) |
| 관리자급 권한으로 로그온했나 | 4672, 4624 의 관리자 권한 토큰 칸 | [명시적 자격 증명·특수 권한](4648-4672.md) |
| 도메인 계정이 어느 컴퓨터에서 인증을 요청했나 | 도메인 컨트롤러의 4768·4769·4776 | [도메인 인증 이벤트](4768-4769-4776.md) |
| 도착 PC 의 로그온과 도메인 컨트롤러 기록 잇기 | 4624·4648 과 4769 에 같이 남는 로그온 GUID (Logon GUID). 값이 모두 0 으로 비어 있는 경우도 있습니다. | [도메인 인증 이벤트](4768-4769-4776.md) |
| 어느 컴퓨터의 로그를 모아야 하나 | 이벤트마다 남는 컴퓨터가 다름 | [기록이 남는 위치](pc.md) |

### 시각을 읽을 때

레코드 시각은 UTC 로 저장되며, 이벤트 뷰어 같은 도구는 이 값을 보는 PC 의 시간대로 바꿔 보여 줄 수 있으므로 보고서에는 어느 시간대로 적었는지 밝힙니다. 이 시각은 이벤트를 기록한 컴퓨터의 시계를 따르기 때문에, 여러 컴퓨터의 로그를 합칠 때는 컴퓨터마다 시계 오차를 확인합니다. 방법은 [시간대·시계 오차 보정](../../../03-techniques/analysis/timeline/time-normalization.md) 에서 다룹니다. 시스템 시각을 바꾼 기록은 [시간 변경 (4616·Kernel-General)](../4616-kernel-general.md) 에서 찾습니다.

## 읽는 순서

1. [로그온 유형 해석 (Logon Type)](logon-type.md) — 4624·4625 의 로그온 유형 숫자가 어떤 접속 방식인지 정리합니다. 유형마다 원격 주소와 계정 칸이 어떻게 채워지는지도 다룹니다.
2. [로그온 실패와 실패 코드 (4625)](4625.md) — 상태 코드와 하위 상태 코드로 실패 이유를 나눕니다. 짧은 시간에 몰린 실패를 읽는 법도 다룹니다.
3. [로그온 세션 잇기 (Logon ID·4624~4634·4647)](logon-id-4624-4634-4647.md) — 로그온 ID 로 4624 와 4634·4647 을 짝지어 세션 길이를 구합니다. 짝이 없는 이벤트와 재부팅 뒤 같은 ID 가 다시 나오는 경우도 다룹니다.
4. [화면 잠금·해제 (4800·4801)](4800-4801.md) — 자리를 비운 시각과 돌아온 시각을 읽습니다. 이 감사가 꺼져 있을 때 기댈 수 있는 다른 기록도 다룹니다.
5. [명시적 자격 증명·특수 권한 (4648·4672)](4648-4672.md) — 다른 계정의 자격 증명을 넣어 접속한 흔적과 특수 권한이 붙은 로그온을 읽습니다. 4648 을 어느 컴퓨터에서 찾을지도 다룹니다.
6. [도메인 인증 이벤트 (4768·4769·4776)](4768-4769-4776.md) — 도메인 컨트롤러에 남는 Kerberos·NTLM 인증 기록을 읽습니다. 어느 컴퓨터에서 어느 계정이 인증을 요청했는지 좁힙니다.
7. [기록이 남는 위치 (로컬 PC와 도메인 컨트롤러)](pc.md) — 한 번의 접속이 출발 PC, 도착 PC, 도메인 컨트롤러에 각각 무엇을 남기는지 정리합니다. 어느 컴퓨터의 로그를 수집해야 하는지 이 페이지로 정합니다.

## 함께 볼 페이지

- [감사 정책과 로그 설정 (Audit Policy·Log Settings)](../audit-policy-log-settings.md) — 이 이벤트들이 남도록 켜져 있었는지, 로그 크기 한도가 얼마였는지 확인합니다.
- [EVTX 파일 구조 (File Header·Chunk·Record)](../../../01-foundations/database-log-formats/evtx-evt-etl/file-header-chunk-record.md) · [파일 안에 남은 지운·손상 레코드 (Chunk Slack·Corrupted EVTX)](../../../01-foundations/database-log-formats/evtx-evt-etl/chunk-slack-corrupted-evtx.md) — 보안 로그 파일을 직접 읽고, 손상된 레코드를 되살립니다.
- [원격 데스크톱 이벤트 (RDP Event Logs)](../rdp-event-logs/index.md) — 4624 유형 10 과 세션 재연결·연결 끊김 (4778·4779) 을 원격 데스크톱 로그와 함께 읽습니다.
- [켜짐·꺼짐 (Power On·Off Events)](../power-on-off-events.md) — 로그오프 이벤트가 없는 세션의 끝을 전원 기록으로 메웁니다.
- [이벤트 로그 삭제 (1102·104)](../1102-104.md) — 보안 로그를 지운 흔적을 찾습니다.
- [사용자 계정 (SAM)](../../system-account/sam.md) · [사용자 프로필 목록 (ProfileList)](../../system-account/profilelist.md) · [윈도 식별자 형식 (SID·GUID·CLSID·Known Folder ID)](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) — 이벤트에 남은 SID 를 계정 이름과 프로필 폴더에 맞춥니다.
- [공유 폴더 접근 (5140·5145)](../5140-5145.md) · [프로세스 생성 (4688)](../4688.md) — 네트워크 로그온 뒤에 무엇을 했는지 이어 봅니다.
- [이벤트 로그 규칙 검색 (Sigma Rules)](../../../03-techniques/analysis/sigma-rules.md) — 많은 로그온 이벤트에서 의심스러운 형태를 골라냅니다.
- [PC 사용 시간 재구성 (켜짐·꺼짐·로그온)](../../../04-scenarios/activity/system-usage-time.md) · [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) — 로그온 기록을 사용 시간과 사용자 판단에 씁니다.
- [원격 데스크톱 침입 확인](../../../04-scenarios/incident/rdp-intrusion.md) · [비밀번호 대입 공격이 있었나](../../../04-scenarios/incident/credential-theft-lateral-movement/brute-force.md) · [다른 PC 에서 원격 실행했나](../../../04-scenarios/incident/credential-theft-lateral-movement/psexec-wmi-winrm.md) — 침해 조사에서 로그온 이벤트를 읽는 순서입니다.

## 참고 문헌

- Microsoft Learn, 보안 감사 이벤트 설명 (Windows 10 보관 문서)
  - "4624(S): An account was successfully logged on." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4624
  - "4625(F): An account failed to log on." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4625
  - "4634(S): An account was logged off." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4634
  - "4648(S): A logon was attempted using explicit credentials." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4648
  - "4672(S): Special privileges assigned to new logon." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4672
  - "4769(S, F): A Kerberos service ticket was requested." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4769
  - "4776(S, F): The computer attempted to validate the credentials for an account." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4776
  - "4800(S): The workstation was locked." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4800
- Microsoft Learn, "Audit Other Logon/Logoff Events" — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-other-logonlogoff-events
- Microsoft Learn, "System Audit Policy recommendations" — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/audit-policy-recommendations
- Microsoft Learn, "Eventlog Key" — https://learn.microsoft.com/en-us/windows/win32/eventlog/eventlog-key
- Randy Franklin Smith, "Windows Security Log Encyclopedia", Ultimate Windows Security (4624·4625·4634·4647·4648·4672·4768·4769·4776·4800 항목) — https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=4624
- libyal, "Windows XML Event Log (EVTX)" · "Windows Event Log (EVT) format" — https://github.com/libyal/libevtx/blob/main/documentation/Windows%20XML%20Event%20Log%20(EVTX).asciidoc · https://github.com/libyal/libevt/blob/main/documentation/Windows%20Event%20Log%20(EVT)%20format.asciidoc
