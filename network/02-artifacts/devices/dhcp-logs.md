---
title: "DHCP 로그"
parent: "아티팩트 · 네트워크 장비와 서버 로그"
nav_order: 280
---

# DHCP 로그 (DHCP)

DHCP 서버는 어느 IP 주소를 언제부터 언제까지 어느 하드웨어 주소(MAC)에 빌려줬는지를 로그와 임대 데이터베이스에 남깁니다. 방화벽·프록시·DNS 로그에는 내부 IP 만 남아서, 그 IP 를 그 시각에 쓴 기기를 찾으려면 DHCP 기록을 함께 봐야 합니다. 다만 MAC·호스트 이름은 클라이언트가 스스로 보내는 값이고, 서버 제품마다 시간대와 보존 기간이 달라서 어느 서버의 어느 파일인지부터 확인하고 읽습니다.

## 무엇을 기록하나 · 왜 생기나

DHCP (Dynamic Host Configuration Protocol) 클라이언트는 UDP 68번 포트에서 서버의 67번 포트로 요청을 보내 주소와 설정값을 받습니다[19]. 처음 주소를 받을 때는 DISCOVER, OFFER, REQUEST, ACK 네 메시지가 오가고, 메시지 종류는 옵션 53 의 값으로 구분합니다[1][2].

| 옵션 53 값 | 메시지 | 보내는 곳 | 뜻 |
|---|---|---|---|
| 1 | DHCPDISCOVER | 클라이언트 | 브로드캐스트로 서버를 찾습니다[1]. |
| 2 | DHCPOFFER | 서버 | 설정값을 제안합니다. |
| 3 | DHCPREQUEST | 클라이언트 | 제안받은 설정을 요청하거나, 재부팅 뒤 쓰던 주소를 확인하거나, 임대를 연장합니다[1]. |
| 4 | DHCPDECLINE | 클라이언트 | 받은 주소가 이미 쓰이고 있다고 알립니다. |
| 5 | DHCPACK | 서버 | 주소를 확정해 줍니다. |
| 6 | DHCPNAK | 서버 | 클라이언트가 아는 주소가 틀렸다고 알립니다. 다른 서브넷으로 옮겼거나 임대가 끝난 경우입니다[1]. |
| 7 | DHCPRELEASE | 클라이언트 | 주소를 반납하고 남은 임대를 취소합니다. |
| 8 | DHCPINFORM | 클라이언트 | 주소는 이미 있고 다른 설정값만 요청합니다. |

서버는 주소를 내줄 때마다, 그리고 클라이언트가 임대를 연장하거나 반납할 때마다 기록을 남깁니다. 클라이언트는 기본으로 임대 기간의 절반(T1)이 지나면 연장을 시도하므로[1], 기기가 네트워크에 붙어 있는 동안에는 연장 기록이 일정한 간격으로 이어집니다. 반납(RELEASE)은 클라이언트가 골라서 보내는 메시지라서[1], 반납 기록 없이 임대가 끝나는 일도 흔합니다.

서버 기록은 세 종류로 나눠 봅니다. 첫째는 이벤트가 생길 때마다 한 줄씩 쓰는 텍스트 로그(Windows 감사 로그, ISC dhcpd 의 syslog, Kea 의 포렌식 로그)입니다. 둘째는 현재 임대 상태를 담는 임대 데이터베이스(ISC `dhcpd.leases`, Kea `kea-leases4.csv`)이고, 셋째는 서버 설정 변경·필터·장애 조치를 남기는 Windows 이벤트 로그입니다. 서버 기록이 없으면 네트워크 센서가 패킷에서 만든 기록(Zeek `dhcp.log`, Suricata EVE `dhcp`)으로 같은 대응 관계를 찾습니다.

## 위치와 버전별 차이

| 서버·센서 | 기록 | 기본 위치·이름 | 형식 |
|---|---|---|---|
| Windows DHCP 서버 | 감사 로그 | `%windir%\System32\Dhcp`, 요일 이름이 들어간 파일 | 쉼표로 구분한 텍스트, 한 줄에 이벤트 하나[3] |
| Windows DHCP 서버 | 이벤트 로그 | 응용 프로그램 및 서비스 로그 > Microsoft > Windows > DHCP-Server | Operational·Administrative·System·FilterNotifications·Audit 채널[7] |
| ISC DHCP (dhcpd) | syslog | syslog 설정이 정한 파일 | 한 줄 텍스트[11] |
| ISC DHCP (dhcpd) | 임대 데이터베이스 | `DBDIR/dhcpd.leases`, 직전 판 `DBDIR/dhcpd.leases~` | 자유 형식 ASCII[10] |
| Kea DHCPv4 | 임대 파일(memfile) | `[kea-install-dir]/var/lib/kea/kea-leases4.csv` | CSV[13] |
| Kea DHCPv4 | 포렌식 로그 훅 | `[kea-install-dir]/var/log/kea/kea-legal.CCYYMMDD.txt` | 한 줄 텍스트, DB 에도 저장 가능[17] |
| Zeek | `dhcp.log` | Zeek 로그 폴더 | TSV 또는 JSON. [Zeek 로그](../zeek/zeek-logs/index.md) 참고 |
| Suricata | EVE `dhcp` | `eve.json` | JSON. [프로토콜 기록](../suricata/eve-json/protocol-events.md) 참고 |

Windows 감사 로그는 Windows 2000 부터 요일별 파일을 씁니다. 그 전 Windows NT 는 `Dhcpsrv.log` 한 파일에 기록했습니다[4]. 파일 이름은 버전에 따라 다릅니다. Windows 2000 은 `DhcpSrvLog.Sat`·`DhcpSrvLog.wed` 처럼 요일 약자를 확장자로 쓰고[4], 그 뒤 버전은 `DhcpSrvLog-Wed.log`·`DhcpSrvLog-Fri.log` 형식을 씁니다[5][9]. IPv6 기록은 `DhcpV6SrvLog-Fri.log` 처럼 따로 남습니다[9]. 실제 서버에서는 `Get-DhcpServerAuditLog` 로 경로·사용 여부·크기 한도를 먼저 확인합니다[6][9]. Windows Server 2016 이후에는 감사 로그가 기본으로 켜져 있습니다[7].

필드 구성도 버전마다 다릅니다. Windows Server 2008 의 필드는 `ID, Date, Time, Description, IP Address, Host Name, MAC Address` 일곱 개이고[3], Windows Server 2016~2025 의 머리말에는 그 뒤에 `User Name, TransactionID, QResult, Probationtime, CorrelationID, Dhcid, VendorClass(Hex), VendorClass(ASCII), UserClass(Hex), UserClass(ASCII), RelayAgentInformation, DnsRegError` 가 더 붙습니다[9]. 로그 파일 머리말에 필드 구성이 적혀 있으므로[4], 파일마다 머리말을 먼저 읽고 필드 순서를 맞춥니다.

ISC DHCP 는 4.4.3 을 마지막 계획 릴리스로 개발이 끝났습니다(4.4.3-P1, 2022년 10월 5일)[12]. 그래도 설치된 장비가 남아 있을 수 있어서 기록 형식을 알아 둘 필요가 있습니다. Kea 2.7.9 부터는 임대 파일을 빌드할 때 정한 데이터 폴더에서만 읽고(`KEA_DHCP_DATA_DIR` 로 바꿈), 포렌식 로그도 정해진 로그 폴더에만 씁니다(`KEA_LEGAL_LOG_DIR` 로 바꿈)[13][17]. 포렌식 로그 훅 `libdhcp_legal_log.so` 는 예전에는 유료 지원 고객에게만 제공했고 지금은 공개 코드에 들어 있습니다[17].

## 구조

### 메시지와 옵션

DHCP 메시지 머리에는 서버 기록의 원천이 되는 필드가 있습니다. `yiaddr` 는 서버가 클라이언트에게 주는 주소, `giaddr` 는 릴레이 에이전트 주소, `chaddr` 는 16바이트 클라이언트 하드웨어 주소입니다[1]. `giaddr` 가 0 이면 클라이언트가 서버와 같은 서브넷에 있다는 뜻입니다[1].

| 옵션 | 이름 | 조사에서 볼 점 |
|---|---|---|
| 12 | Host Name | 클라이언트 이름. 도메인이 붙어 있을 수도, 없을 수도 있습니다[2]. |
| 15 | Domain Name | 서버가 알려 주는 도메인[2][20]. |
| 50 | Requested IP Address | 클라이언트가 달라고 한 주소. 예전에 쓰던 주소를 다시 요청하기도 합니다[19]. |
| 51 | IP Address Lease Time | 임대 기간(초)[2]. |
| 60 | Vendor class identifier | 클라이언트 종류·설정을 알리는 문자열. 예: `MSFT 5.0`[2][19]. |
| 61 | Client-identifier | 서버가 임대 데이터베이스의 색인으로 쓰는 값. 보통 하드웨어 종류와 MAC 이지만, 종류 0 이면 FQDN 같은 다른 식별자입니다[2]. |
| 81 | Client FQDN | 클라이언트가 알린 FQDN[20]. |
| 82 | Relay Agent Information | 릴레이가 붙이는 circuit-id·remote-id. 스위치 포트를 알아내는 단서입니다[10][20]. |

### Windows 감사 로그

한 줄이 이벤트 하나이고, 맨 앞 `ID` 가 이벤트 종류입니다[3].

| ID | 뜻 |
|---|---|
| 00, 01 | 로그 시작, 로그 중지 |
| 02 | 디스크 공간이 모자라 로그를 잠시 멈춤 |
| 10 | 새 주소를 클라이언트에 임대 |
| 11 | 클라이언트가 임대를 연장 |
| 12 | 클라이언트가 임대를 반납 |
| 13 | 네트워크에서 이미 쓰이는 주소를 발견 |
| 14 | 범위(scope)의 주소가 바닥나 요청을 처리하지 못함 |
| 15 | 임대 거부 |
| 20 | BOOTP 주소 임대 |
| 30, 31, 32 | DNS 동적 업데이트 요청, 실패, 성공 |
| 50–64 | 서버 권한 부여(authorization)와 다른 DHCP 서버 탐지. 51 권한 부여 성공, 54 실패, 62 다른 DHCP 서버 발견 등 |

최근 서버에서는 16(임대 삭제), 17·18(임대 만료), 21–25(동적 BOOTP·주소 정리), 33·36(NAP 정책이나 장애 조치 대기 역할 때문에 버린 패킷), 34·35(DNS 업데이트 요청 실패)도 쓰입니다[9]. 날짜는 `MM/DD/YY`, 시각은 `HH:MM:SS` 형식입니다[3][9]. 아래는 필드 순서만 보여 주는 만든 예시이고, 괄호 부분은 실제 파일에서 설명 문자열과 MAC 표기를 확인해 읽습니다.

```
ID,Date,Time,Description,IP Address,Host Name,MAC Address
00,09/27/26,10:00:01,Started,,,
10,09/27/26,10:15:02,(설명 문자열),192.168.10.57,laptop-a1.example.com,(MAC 주소)
```

같은 서버의 이벤트 로그에는 감사 로그에 없는 내용이 남습니다. Operational 채널의 70번대 이벤트는 범위를 만들거나 바꾸거나 지울 때 `Scope: %1 for IPv4 is Modified by %2.` 처럼 누가 바꿨는지를 적습니다[7]. FilterNotifications 채널의 20096·20097·20099·20100 은 MAC 허용 목록·차단 목록 때문에 서비스를 거부한 기록이고, 하드웨어 주소와 FQDN/호스트 이름이 함께 남습니다[7]. 1033 은 콜아웃 DLL 을 불러온 기록이고, 1031·1032·1034 는 콜아웃 DLL 의 예외나 로드 실패 기록입니다[7]. Sigma 규칙은 System 로그에서 이 번호로 레지스트리에 지정된 콜아웃 DLL 이 로드됐거나 로드에 실패한 기록을 찾습니다[8]. Audit 채널의 20289 이후 번호는 장애 조치(failover) 상대 서버와 주고받은 메시지입니다[7].

### ISC dhcpd syslog 와 dhcpd.leases

dhcpd 는 메시지를 받거나 보낼 때마다 syslog 에 한 줄을 씁니다[11].

```
DHCPDISCOVER from 02:00:00:00:00:57 (laptop-a1) via eth1
DHCPOFFER on 192.168.10.57 to 02:00:00:00:00:57 (laptop-a1) via eth1
DHCPREQUEST for 192.168.10.57 (10.0.0.5) from 02:00:00:00:00:57 (laptop-a1) via eth1
DHCPACK on 192.168.10.57 to 02:00:00:00:00:57 (laptop-a1) via eth1
DHCPRELEASE of 192.168.10.57 from 02:00:00:00:00:57 (laptop-a1) via eth1 (found)
```

위 줄은 소스 코드의 출력 형식으로 만든 예시이고, 앞에 붙는 syslog 시각·호스트 이름은 뺐습니다. 괄호 안 이름은 클라이언트가 보낸 호스트 이름이고 없으면 괄호째 빠집니다. `via` 뒤에는 릴레이를 거친 요청이면 `giaddr` IP 가, 아니면 요청을 받은 인터페이스 이름이 옵니다[11]. 하드웨어 주소가 없는 요청은 client identifier 를 16진수로 적거나 `<no identifier>` 로 적습니다[11]. 요청을 처리하지 않은 경우에는 줄 끝에 `: wrong network.`, `: ignored (not authoritative).`, `: lease 주소 unavailable.`, `: unknown lease 주소.` 같은 판정이 붙습니다[11]. 이 밖에 `DHCPNAK on`, `DHCPDECLINE of`, `DHCPINFORM from` 줄이 있습니다[11].

`dhcpd.leases` 는 로그처럼 덧붙이는 파일입니다. 임대를 받거나 연장하거나 반납할 때마다 그 임대의 새 값을 파일 끝에 쓰므로, 같은 주소의 `lease` 선언이 여러 번 나오면 마지막 것이 현재 값입니다[10]. 아래는 설명서의 문법으로 만든 예시입니다.

```
authoring-byte-order little-endian;

lease 192.168.10.57 {
  starts 0 2026/09/27 01:15:02;
  ends 0 2026/09/27 03:15:02;
  cltt 0 2026/09/27 01:15:02;
  binding state active;
  next binding state free;
  hardware ethernet 02:00:00:00:00:57;
  uid "\001\002\000\000\000\000W";
  client-hostname "laptop-a1";
}
```

| 문장 | 뜻 |
|---|---|
| `starts`, `ends` | 임대 시작·끝 시각. 끝이 없으면 `never`[10] |
| `cltt` | 클라이언트가 마지막으로 거래한 시각[10] |
| `tstp`, `tsfp`, `atsfp` | 장애 조치를 쓸 때 상대 서버와 주고받은 만료 시각[10] |
| `binding state` | 장애 조치를 쓰지 않으면 `active`·`free`·`abandoned` 중 하나. 장애 조치를 쓰면 `backup` 등이 더 있음[10] |
| `next binding state` | `ends` 시각에 바뀔 상태[10] |
| `hardware` | 하드웨어 종류와 콜론으로 구분한 MAC[10] |
| `uid` | 클라이언트가 보낸 client identifier. 보내지 않았으면 없음. 기본 표기(`lease-id-format`)는 출력할 수 없는 문자를 8진수로 쓴 문자열[10] |
| `client-hostname` | 클라이언트가 옵션 12 로 호스트 이름을 보냈을 때만 기록[10] |
| `option agent.circuit-id`, `option agent.remote-id` | 릴레이가 붙인 옵션 82 값[10] |
| `set ddns-fwd-name` 등 | 서버가 DNS 를 업데이트한 이름[10] |

파일 첫머리에는 서버가 `authoring-byte-order` 문장을 넣습니다[10]. DHCPv6 임대는 `ia_na`·`ia_ta`·`ia_pd` 선언에 IAID 와 DUID 를 합친 값으로 남고, 그 안에 `iaaddr`·`iaprefix`, `preferred-life`, `max-life`, `ends` 가 있습니다[10]. 지운 group·host 선언은 `{ deleted; }` 를 붙인 선언(rubout)으로 남습니다[10].

### Kea 임대 파일과 포렌식 로그

Kea 의 `kea-leases4.csv` 도 새 임대와 연장을 파일 끝에 덧붙이고, 불러올 때는 클라이언트마다 마지막 항목을 유효한 값으로 봅니다[13]. 열은 `address, hwaddr, client_id, valid_lifetime, expire, subnet_id, fqdn_fwd, fqdn_rev, hostname, state, user_context, pool_id` 순서이고, `state` 는 스키마 2.0, `user_context` 는 2.1, `pool_id` 는 3.0 에서 더해졌습니다[14]. `expire` 는 마지막 거래 시각(cltt)에 `valid_lifetime` 을 더한 유닉스 시각(초)이라서, cltt 는 `expire − valid_lifetime` 으로 되살립니다[14]. `state` 값은 0 기본, 1 거부됨(declined), 2 만료 후 회수됨, 3 반납됨, 4 등록됨입니다[15].

```
address,hwaddr,client_id,valid_lifetime,expire,subnet_id,fqdn_fwd,fqdn_rev,hostname,state,user_context,pool_id
192.168.10.57,02:00:00:00:00:57,01:02:00:00:00:00:57,7200,1790478902,1,0,0,laptop-a1,0,,0
```

위 줄은 만든 예시입니다. `1790478902 − 7200 = 1790471702` 이고, 이 값은 2026-09-27 01:15:02 UTC 입니다.

포렌식 로그 훅은 할당·연장·반납 같은 임대 이벤트를 한 줄에 하나씩 기록합니다[17]. 항목 순서는 다음과 같습니다[17].

```
timestamp address duration device-id {client-info} {relay-info} {user-context}
```

`address` 에는 주소와 함께 할당·연장·반납 중 무엇인지가, `duration` 에는 임대 기간이 들어가고 반납이면 기간이 빠집니다. `device-id` 는 하드웨어 종류와 16진 주소, `client-info` 는 옵션 61, `relay-info` 는 `giaddr` 와 옵션 82 의 circuit-id·remote-id·subscriber-id 입니다[17]. 아래는 설명서의 반납 줄 형식으로 만든 예시입니다.

```
2026-09-27 12:05:40 KST Address: 192.168.10.57 has been released from a device with hardware address: hwtype=1 02:00:00:00:00:57, client-id: 01:02:00:00:00:00:57
```

관리자가 제어 명령 `lease4-add`·`lease4-update`·`lease4-del` 로 임대를 바꾸면 `Administrator added a lease of address: …` 처럼 기록되고, 고가용성(HA) 상대 서버가 보낸 명령은 `HA partner added …` 로 기록됩니다[17]. 사람이 손으로 넣은 임대와 클라이언트가 받은 임대를 이 문구로 구분합니다. Kea 3.3.0 부터는 여러 줄 항목의 이어지는 줄에 시각 뒤 하이픈을 붙여 구분합니다(`mark-continuation-lines`, 기본 켜짐)[17]. Kea 의 일반 로그에도 `DHCP4_LEASE_ALLOC %1: lease %2 has been allocated for %3 seconds` 같은 메시지가 있지만, 반납 메시지 `DHCP4_RELEASE` 는 디버그 수준 50 에서만 나옵니다[16].

### Zeek dhcp.log

Zeek 는 같은 트랜잭션 ID 로 짧은 시간 안에 오간 메시지를 묶어 한 줄로 기록합니다[20]. 묶는 시간 한도는 `DHCP::max_txid_watch_time`(기본 30초)입니다[20].

| 필드 | 내용 |
|---|---|
| `ts` | 이 트랜잭션에서 처음 본 DHCP 메시지 시각[20] |
| `uids` | 관련 연결의 uid 목록. 브로드캐스트 때문에 연결이 여럿으로 나뉩니다[19][20]. |
| `client_addr`, `server_addr` | 클라이언트·임대를 내준 서버의 IP. 브로드캐스트가 아닌 주소로 보낸 메시지가 있어야 채워집니다[20]. |
| `mac` | 클라이언트 하드웨어 주소 |
| `host_name`, `client_fqdn`, `domain` | 옵션 12, 81, 15 |
| `requested_addr`, `assigned_addr`, `lease_time` | 요청한 주소, 받은 주소, 임대 기간 |
| `client_message`, `server_message` | DECLINE·NAK 에 붙은 사유 |
| `msg_types`, `duration` | 본 메시지 종류 목록, 첫 메시지부터 마지막 메시지까지 걸린 시간 |

정책 스크립트를 불러오면 `msg_orig`(메시지마다 보낸 주소), `client_software`·`server_software`(옵션 60), `circuit_id`·`agent_remote_id`·`subscriber_id`(옵션 82)가 더 붙습니다[20]. DISCOVER 만 본 줄에는 `server_addr` 가 없습니다[19].

## 증거로서 의미

**증명하는 것.** 서버 기록은 이 서버가 이 시각 구간(임대 시작부터 만료·반납까지)에 이 IP 를 이 하드웨어 주소 또는 client identifier 에 빌려줬다는 사실을 보여 줍니다. 클라이언트가 그때 보낸 호스트 이름·벤더 클래스·FQDN 과, 릴레이를 거쳤다면 릴레이 주소와 옵션 82 값도 함께 확인됩니다[10][17]. Windows 이벤트 로그로는 범위 설정을 언제 누가 바꿨는지, 어떤 MAC 을 필터로 막았는지도 알 수 있습니다[7].

**증명하지 못하는 것.** MAC·호스트 이름·client identifier 는 클라이언트가 보내는 값이라[2], 기록에 적힌 MAC 이 그 기기의 실제 하드웨어라는 증명은 안 됩니다. 고정 IP 로 설정한 기기는 DHCP 를 거치지 않으므로 기록이 없습니다. 임대 기간 안에 다른 기기가 같은 IP 를 몰래 썼는지도 이 기록만으로는 알 수 없고, Windows ID 13 이나 DECLINE 은 주소 충돌이 있었다는 흔적일 뿐입니다[1][3]. 반납 기록이 없다고 기기가 계속 붙어 있었다고 볼 수도 없습니다. 반납은 클라이언트가 골라서 보내는 메시지라서[1], 기기가 조용히 떠나면 임대가 끝나는 시각만 남습니다.

보고서에는 "2026-09-27 10:15(KST)부터 12:05(KST) 사이 192.168.10.57 은 DHCP 서버 기록상 MAC 02:00:00:00:00:57, 호스트 이름 laptop-a1 에 임대되어 있었다"(만든 예시)처럼 기록으로 확인되는 만큼만 씁니다. "laptop-a1 사용자가 접속했다" 는 스위치·인증·호스트 기록까지 맞춘 뒤에 쓸 수 있습니다.

## 시각 해석

제품마다 시각 기준이 달라서 하나의 타임라인으로 합치기 전에 모두 UTC 로 바꿉니다. syslog 로 받은 줄의 시각 해석은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)에 있습니다.

| 기록 | 시각 필드 | 기준 |
|---|---|---|
| Windows 감사 로그 | `Date`, `Time` | 이벤트를 기록한 날짜·시각[3]. 시간대 표시가 없고 파일이 서버 현지 시각 자정에 바뀌므로[4] 서버 현지 시각으로 읽습니다. |
| ISC `dhcpd.leases` | `starts`, `ends`, `cltt` | 기본(`db-time-format default`)은 UTC 이고 현지 시각이 아닙니다[10]. `local` 이면 `epoch 초; # 현지 설명` 형식이고, 주석은 사람이 읽으라고 붙인 값입니다[10]. |
| ISC syslog | syslog 머리 시각 | syslog 형식과 수집기 설정에 따름 |
| Kea `kea-leases4.csv` | `expire` | 유닉스 시각(초). cltt 는 `expire − valid_lifetime`[14] |
| Kea 포렌식 로그 | 줄 앞 `timestamp` | 기록한 시각. 기본 `%Y-%m-%d %H:%M:%S %Z` 로 시간대 이름이 붙고, `timestamp-format` 으로 바꿀 수 있습니다[17]. |
| Zeek `dhcp.log` | `ts` | 그 트랜잭션에서 처음 본 DHCP 메시지 시각(UTC)[19][20] |

`dhcpd.leases` 의 요일 숫자(0 = 일요일)는 사람이 보기 쉽게 붙인 값이고 읽을 때는 무시됩니다[10]. ISC `ends` 는 서버가 정한 만료 예정 시각이라서, 그 전에 반납이나 새 임대가 있었는지 뒤따르는 선언을 확인합니다.

## 함정과 한계

- **Windows 감사 로그는 약 일주일치만 남습니다.** 요일 파일을 새로 열 때 그 파일이 24시간 넘게 수정되지 않았으면 덮어쓰고, 24시간 안에 수정됐으면 이어 씁니다[4][5]. 현재 파일이 전체 크기 한도(Windows 2000 기본 7MB)의 7분의 1을 넘거나 디스크 여유가 최소값(기본 20MB) 아래로 내려가면 자정이나 공간이 생길 때까지 기록을 건너뜁니다[4][6]. 오래된 사건은 수집 서버나 SIEM 에 옮겨 둔 사본에서 찾아야 하고, 이 부분은 [로그 수집과 보존](../../03-techniques/acquisition/log-collection.md)에서 다룹니다.
- **임대 데이터베이스는 이력이 아니라 현재 상태에 가깝습니다.** `dhcpd.leases` 는 때때로 알고 있는 임대를 새 파일에 한 번씩만 다시 쓰고 옛 파일은 `dhcpd.leases~` 로 이름을 바꿔 두므로, 직전 파일 하나만 남고 그보다 앞선 이력은 사라집니다[10]. Kea 의 임대 파일 정리(LFC)도 클라이언트마다 마지막 항목만 남기고 기본 3600초마다 돕니다(`lfc-interval`, 0 이면 끔)[13]. 정리는 별도 `kea-lfc` 프로세스가 previous·input·output·finish 파일을 차례로 옮기며 하므로[18], 이 파일들과 백업도 함께 수집합니다.
- **릴레이 환경의 주소를 헷갈리기 쉽습니다.** ISC syslog 의 `via` 뒤 IP 는 클라이언트가 아니라 릴레이 주소(`giaddr`)입니다[11]. 기기가 붙은 스위치 포트는 옵션 82 의 circuit-id·remote-id 가 기록된 경우에만 알 수 있습니다[10][17].
- **호스트 이름은 없을 수도 있습니다.** 옵션 12 는 필수가 아니어서 특수 목적 기기는 보내지 않는 경우가 많고, 그러면 `client-hostname` 문장이 없습니다[10].
- **같은 기기가 오래 같은 IP 를 쓰기도 합니다.** 클라이언트가 예전 주소를 다시 요청하거나 관리자가 MAC 기준 예약을 설정하면 주소가 바뀌지 않습니다[19]. 반대로 임대가 끝나면 같은 IP 가 다른 기기로 넘어가므로, 반드시 사건 시각이 들어간 임대 구간을 찾습니다.
- **Zeek 는 한 트랜잭션을 한 줄로 묶습니다.** `ts` 는 첫 메시지 시각이고 ACK 시각이 아닙니다. `server_addr`·`client_addr` 는 브로드캐스트가 아닌 주소에서 보낸 메시지를 봐야 채워지므로, 캡처 지점에 따라 비어 있을 수 있습니다[19][20]. 캡처 위치는 [어디서 캡처하나](../../01-foundations/capture/capture-points.md)를 참고합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 RFC 2131·2132 의 필드 배치로 만든 DHCPACK 메시지의 UDP 본문 앞부분입니다[1][2]. 값은 모두 만든 예시입니다.

```
오프셋  바이트                          필드
0       02                              op = 2 (BOOTREPLY)
1       01                              htype = 1 (이더넷)
2       06                              hlen = 6
3       00                              hops
4       3A 1B 7C 90                     xid (트랜잭션 ID)
8       00 00                           secs
10      00 00                           flags
12      00 00 00 00                     ciaddr
16      C0 A8 0A 39                     yiaddr = 192.168.10.57
20      00 00 00 00                     siaddr
24      C0 A8 0A 01                     giaddr = 192.168.10.1 (릴레이)
28      02 00 00 00 00 57 00 … 00       chaddr (16바이트, 앞 6바이트가 MAC)
44      00 … 00                         sname (64바이트)
108     00 … 00                         file (128바이트)
236     63 82 53 63                     magic cookie
240     35 01 05                        옵션 53, 길이 1, 값 5 = DHCPACK
243     36 04 0A 00 00 05               옵션 54 서버 식별자 = 10.0.0.5
249     33 04 00 00 1C 20               옵션 51 임대 기간 = 7200초
255     FF                              끝
```

고정 머리는 236바이트이고, 그 뒤 4바이트 `63 82 53 63`(99.130.83.99)이 옵션의 시작을 알립니다[1][2]. 옵션은 코드 1바이트, 길이 1바이트, 값 순서입니다. `giaddr` 가 0 이 아니므로 이 응답은 릴레이 192.168.10.1 을 거쳤고, ISC dhcpd 라면 syslog 의 `via` 뒤에 이 주소가 찍힙니다[11]. 임대 기간 `00 00 1C 20` 은 7200초라서 클라이언트는 기본으로 3600초 뒤에 연장을 시도합니다[1].

### 공개 도구로 한 번

tshark 로 캡처의 DHCP 메시지를 필드별로 뽑습니다. Wireshark 3.0 부터 필드 이름이 `dhcp.` 로 시작하고[21], 그 전 판에서는 `bootp.id`·`bootp.option.dhcp` 처럼 `bootp.` 로 시작하는 이름을 씁니다[19].

```
tshark -r capture.pcapng -Y "dhcp" -T fields \
  -e frame.time_epoch -e dhcp.id -e dhcp.option.dhcp -e dhcp.hw.mac_addr \
  -e dhcp.ip.your -e dhcp.ip.relay -e dhcp.option.hostname \
  -e dhcp.option.requested_ip_address -e dhcp.option.ip_address_lease_time \
  -e dhcp.option.vendor_class_id
```

`dhcp.option.dhcp` 가 5 인 줄이 ACK 입니다[2][21]. 서버는 응답에 요청의 `dhcp.id`(xid)를 그대로 넣으므로 같은 `dhcp.id` 끼리 묶으면 요청과 응답이 짝지어집니다. 다만 클라이언트는 xid 를 차례로 늘려 쓸 수 있어서, 한 번의 주소 받기 과정에서 DISCOVER·OFFER 와 REQUEST·ACK 의 `dhcp.id` 가 다를 수 있습니다[1].

Zeek JSON 로그에서는 사건 IP 를 받은 기록만 골라 시간순으로 봅니다.

```
jq -r 'select(.assigned_addr == "192.168.10.57") | [.ts, .mac, .host_name, .client_fqdn, .lease_time, (.msg_types | join(","))] | @tsv' dhcp.log
```

ISC 서버라면 `dhcpd.leases` 에서 같은 주소의 선언을 모두 뽑아 순서대로 읽고, syslog 에서는 `grep 'on 192.168.10.57 to'` 로 OFFER·ACK 줄을 찾습니다. Windows 감사 로그는 머리말 줄을 빼고 CSV 로 읽은 뒤 ID 10·11·12 줄을 IP 로 거릅니다.

## 교차 검증

| 함께 볼 기록 | 알 수 있는 것 | 링크 |
|---|---|---|
| 방화벽·프록시·DNS 서버 로그 | 그 시각 그 내부 IP 가 한 통신. DHCP 기록으로 IP 를 MAC·호스트 이름으로 바꿉니다. | [방화벽 로그](firewall-logs.md), [웹 프록시 로그](proxy-logs.md), [DNS 서버 로그](dns-server-logs.md) |
| NAT 장비 기록 | 외부 IP·포트를 내부 IP 로 되돌리기 | [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md) |
| Zeek·Suricata 기록 | 서버 로그가 없을 때 패킷에서 본 임대 | [Zeek 로그](../zeek/zeek-logs/index.md), [프로토콜 기록](../suricata/eve-json/protocol-events.md) |
| 클라이언트 쪽 설정 | 기기에 남은 DHCP 서버·받은 주소·임대 시각 | [Windows 네트워크 인터페이스 설정](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/tcp-ip-interfaces.html), [Linux 네트워크 설정](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/network-config.html), [macOS 네트워크 인터페이스와 설정](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/network/network-interfaces.html) |
| 탐지 규칙 | DHCP 서버의 콜아웃 DLL 로드(1031–1034) | [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md) |

서버 기록의 MAC 과 기기에 남은 MAC·받은 주소가 같으면 "그 기기가 그 IP 를 썼다" 는 결론을 더 단단히 쓸 수 있습니다. 여러 기록을 한 시간축에 모으는 방법은 [네트워크 타임라인](../../03-techniques/analysis/timeline.md)에, IP 로 사용자를 찾는 전체 흐름은 [이 시각에 이 IP 를 누가 썼나](../../04-scenarios/user-activity/ip-attribution.md)에 있습니다.

## 실습

FoxIO JA4 저장소 `pcap/` 폴더의 `dhcp.pcapng` 은 DHCP 메시지 네 개가 들어 있는 1.5KB 캡처입니다[22]. 사본을 받아 풀어 봅니다.

1. tshark 로 네 패킷의 `dhcp.option.dhcp` 값을 뽑아 DISCOVER·OFFER·REQUEST·ACK 순서인지 확인하십시오. 네 패킷의 `dhcp.id` 는 모두 같습니까?
2. 첫 패킷과 셋째 패킷의 출발지 IP 는 무엇이고, 왜 그렇게 나옵니까? 둘째·넷째 패킷의 `yiaddr` 와 비교하십시오.
3. `dhcp.ip.relay` 값으로 이 클라이언트가 서버와 같은 서브넷에 있었는지 판단하십시오.
4. 같은 파일을 `zeek -C -r dhcp.pcapng LogAscii::use_json=T` 로 돌려 `dhcp.log` 에 몇 줄이 생기는지, 각 줄의 `ts`·`msg_types` 가 어느 패킷과 맞는지, `host_name` 필드가 있는지 확인하십시오. 호스트 이름 옵션이 없는 캡처라면 이 기록만으로 기기를 어디까지 특정할 수 있습니까?
5. 넷째 패킷의 임대 기간으로 T1(연장 시도 시각)을 계산하고, 이 기기가 계속 붙어 있었다면 서버 감사 로그에 연장 기록(Windows ID 11)이 언제쯤 생길지 적어 보십시오.

## 참고 문헌

1. R. Droms, "Dynamic Host Configuration Protocol", RFC 2131, 1997. https://www.rfc-editor.org/rfc/rfc2131.txt
2. S. Alexander, R. Droms, "DHCP Options and BOOTP Vendor Extensions", RFC 2132, 1997. https://www.rfc-editor.org/rfc/rfc2132.txt
3. Microsoft, "Analyze DHCP Server Log Files" (Windows Server 2008). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/dd183591(v=ws.10)
4. Microsoft, "DHCP Audit Logging" (Windows 2000 Server). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc958944(v=technet.10)
5. Microsoft 블로그 보관본, "All about DHCP Auditing", 2006. https://learn.microsoft.com/en-us/archive/blogs/anto_rocks/all-about-dhcp-auditing
6. Microsoft, "Set-DhcpServerAuditLog" (DhcpServer 모듈). https://learn.microsoft.com/en-us/powershell/module/dhcpserver/set-dhcpserverauditlog?view=windowsserver2022-ps
7. Microsoft, "DHCP server events". https://learn.microsoft.com/en-us/windows-server/networking/technologies/dhcp/dhcp-server-events
8. SigmaHQ, "DHCP Server Loaded the CallOut DLL"·"DHCP Server Error Failed Loading the CallOut DLL" 규칙. https://github.com/SigmaHQ/sigma/tree/master/rules/windows/builtin/system/microsoft_windows_dhcp_server
9. NXLog, "Collect logs from Windows DHCP Server". https://docs.nxlog.co/integrate/windows-dhcp-server.html
10. ISC, dhcpd.leases(5) 매뉴얼. https://github.com/isc-projects/dhcp/blob/master/server/dhcpd.leases.5
11. ISC, ISC DHCP 소스 server/dhcp.c. https://github.com/isc-projects/dhcp/blob/master/server/dhcp.c
12. ISC, ISC DHCP README (4.4.3-P1). https://github.com/isc-projects/dhcp/blob/master/README
13. ISC, Kea Administrator Reference Manual "The DHCPv4 Server". https://kea.readthedocs.io/en/latest/arm/dhcp4-srv.html
14. ISC, Kea 소스 src/lib/dhcpsrv/csv_lease_file4.cc. https://github.com/isc-projects/kea/blob/master/src/lib/dhcpsrv/csv_lease_file4.cc
15. ISC, Kea 소스 src/lib/dhcpsrv/lease.h. https://github.com/isc-projects/kea/blob/master/src/lib/dhcpsrv/lease.h
16. ISC, Kea 소스 src/bin/dhcp4/dhcp4_messages.mes. https://github.com/isc-projects/kea/blob/master/src/bin/dhcp4/dhcp4_messages.mes
17. ISC, Kea 문서 "libdhcp_legal_log.so: Forensic Logging". https://github.com/isc-projects/kea/blob/master/doc/sphinx/arm/hooks-legal-log.rst
18. ISC, Kea 문서 "The LFC Process". https://github.com/isc-projects/kea/blob/master/doc/sphinx/arm/lfc.rst
19. Zeek Project, Zeek 문서 "dhcp.log". https://github.com/zeek/zeek-docs/blob/master/logs/dhcp.rst
20. Zeek Project, 스크립트 문서 base/protocols/dhcp/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dhcp/main.zeek.rst
21. Wireshark Foundation, 표시 필터 참조 "Dynamic Host Configuration Protocol (dhcp)". https://www.wireshark.org/docs/dfref/d/dhcp.html
22. FoxIO, JA4 저장소 시험 캡처 pcap/dhcp.pcapng. https://github.com/FoxIO-LLC/ja4/tree/main/pcap
