---
title: "이 시각에 이 IP 를 누가 썼나"
parent: "시나리오 · 사용자 행위"
nav_order: 520
---

# 이 시각에 이 IP 를 누가 썼나 (IP Attribution)

경고·서버 로그·외부 기관의 요청서에 적힌 IP 주소 하나를 기기와 계정까지 이어 가는 순서를 다룹니다. 공유 주소(NAT·CGN) 뒤에서는 IP 만으로는 사용자를 특정할 수 없고 출발지 포트와 초 단위 시각이 함께 있어야 하며, 내부에서는 IP → MAC → 기기 이름 → 계정 순서로 그 시각에 맞는 기록을 하나씩 잇습니다. 각 로그의 필드 설명은 아티팩트 페이지에 있고, 이 페이지는 어떤 기록을 어떤 순서로 맞춰 보는지만 씁니다.

## 조사 질문

- 문제의 IP 는 한 기기만 쓰는 주소인가, 여러 기기가 나눠 쓰는 공유 주소(NAT·CGN·프록시·VPN 출구)인가.
- 공유 주소라면 그 시각에 그 출발지 포트를 쓴 내부 주소는 무엇인가.
- 그 내부 주소는 그 시각에 어느 MAC 주소·기기 이름에 할당돼 있었나.
- 그 기기에서 그 시각 앞뒤로 어떤 계정이 인증했나.

## 먼저 확인할 것

**받은 정보에 포트와 초 단위 시각이 있나.** 인터넷 쪽 서버가 IP 만 남겼다면 공유 주소 뒤의 가입자를 되찾을 수 없습니다. 들어온 IP 를 기록하는 서버는 출발지 포트, 초 단위 이상으로 정확한 시각(UTC 권장, NTP 같은 추적 가능한 시간원), 여러 전송 프로토콜·포트를 쓰는 서비스라면 전송 프로토콜과 목적지 포트를 함께 남기도록 권고합니다[1]. CGN 은 포트를 거의 곧바로 재사용하기도 하고 몇 분 기다렸다 재사용하기도 해서, 서버는 포트가 얼마나 빨리 재사용되는지 알 수 없습니다[1]. 그래서 초 단위 정확도가 필요합니다. 부하 분산기가 서버 대신 연결을 받는다면 같은 권고가 부하 분산기에도 적용됩니다[1].

**요청서의 시각 기준.** UTC 가 아닌 현지 시각과 오프셋으로 적힌 시각은 보고 과정에서 오프셋이 빠질 수 있습니다[1]. 받은 시각이 UTC 인지, 어느 시간대인지, 서버 시계가 얼마나 틀려 있었는지를 먼저 확인합니다([네트워크 기록의 시각](../../01-foundations/records/timestamps.md)).

**서버 앞에 무엇이 있었나.** 부하 분산기·프록시·DDoS 대응 장비가 연결을 끝내고 서버로 새 연결을 열면, 서버가 남긴 출발지 포트는 그 내부 구간에서만 뜻이 있습니다[4]. 이때는 앞단 장비의 기록이 필요합니다.

**내부 기록의 보존 기간.** 내부 장비의 로그는 오래 남지 않을 수 있습니다. 예를 들어 Windows DHCP 서버 감사 로그는 요일마다 파일 하나를 쓰고 일주일 뒤 같은 요일 파일을 덮어씁니다(아래 3단계). 사건 시각이 보존 기간 안에 있는지부터 확인하고, 필요하면 바로 수집합니다([로그 수집과 보존](../../03-techniques/acquisition/log-collection.md)).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 인터넷 쪽 서버·부하 분산기 로그 | 공인 IP·출발지 포트·시각 | [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md) |
| 2 | NAT·CGN 변환 기록, 방화벽 로그 | 공인 IP:포트 ↔ 내부 IP:포트 | [방화벽 로그](../../02-artifacts/devices/firewall-logs.md) |
| 3 | 프록시 로그 | 요청마다 클라이언트 IP, 인증했다면 사용자 이름 | [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md) |
| 4 | VPN 서버 로그 | 가상 주소 ↔ 인증서 이름·사용자 이름 ↔ 실제 접속 주소 | [VPN 서버 로그](../../02-artifacts/devices/vpn-logs.md) |
| 5 | DHCP 서버 로그, Zeek dhcp.log, Suricata dhcp 이벤트 | 내부 IP ↔ MAC ↔ 호스트 이름, 임대 기간 | [DHCP 로그](../../02-artifacts/devices/dhcp-logs.md) |
| 6 | Suricata arp·ethernet, Zeek conn.log MAC 필드 | 그 시각 패킷의 MAC 주소 | [연결 기록 (conn.log)](../../02-artifacts/zeek/zeek-logs/conn-log.md), [프로토콜 이벤트](../../02-artifacts/suricata/eve-json/protocol-events.md) |
| 7 | Zeek kerberos.log·ntlm.log·radius.log, software.log | 그 IP 에서 인증한 계정, 그 IP 의 소프트웨어 문자열 | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) |
| 8 | 기기 쪽 기록 | 기기가 받은 주소, 로그인한 사용자 | [Windows 네트워크 인터페이스 설정](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/tcp-ip-interfaces.html), [Linux 네트워크 설정](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/network-config.html) |

## 분석 흐름

**1. 공인 IP 를 내부 주소로 되돌립니다.** 조직의 NAT 장비나 ISP 의 CGN 변환 기록에서 "공인 IP, 출발지 포트, 시각" 세 값이 모두 맞는 항목을 찾습니다. 내부 포트와 외부 포트가 같다고 가정하면 안 됩니다. 내부 포트를 외부에서도 그대로 쓰는 동작(port preservation)은 NAT 마다 다르고, 이 동작을 쓰는 NAT 도 포트가 겹치면 이전 매핑을 덮어쓰거나 다른 외부 주소나 다른 포트를 씁니다[2]. UDP 매핑은 잘 알려진 포트(0~1023)용 예외를 빼면 패킷이 없어도 2분 전에는 만료되면 안 되고 기본값은 5분 이상이 권고되며, 이 값은 장비에서 바꿀 수 있습니다[2]. 그래서 짧은 시간 창 안에서도 같은 외부 포트가 한 내부 주소에 이어져 있을 수도, 다른 주소로 넘어갔을 수도 있습니다.

CGN 이 연결마다 기록하지 않고 결정적 매핑(deterministic CGN)을 쓰면 계산으로 되돌립니다. 이 방식은 내부 주소마다 외부 주소와 포트 범위를 미리 정해 두고, 외부 주소와 포트로 내부 주소를 계산합니다[3]. 명세의 예에서는 외부 주소 하나를 내부 주소 14개와 동적 할당 몫 2개를 더한 16몫으로 나누고(1:16), 내부 주소마다 (65536−1024)/16 = 4032개 포트를 받아 198.51.100.1 이 192.0.2.1 의 1024~5055번 포트에 대응합니다[3]. 미리 받은 범위를 넘어 동적으로 더 준 포트 블록은 장비가 반드시 기록해야 합니다(MUST)[3]. 운영자가 쓰는 알고리즘과 설정값이 있어야 계산할 수 있으므로 ISP 에 함께 요청합니다. DS-Lite 에서는 이 계산으로 가입자의 IPv6 주소·프리픽스까지만 되찾고, 그 안에 캡슐화된 내부 IPv4 주소는 알 수 없습니다[3].

연결마다 기록하는 CGN 은 보존 부담이 커서 오래 남기지 않을 수 있습니다. 미국 여러 운영사 보고로는 가구당 하루 약 33,000개 연결이고, 실험실에서 잰 변환 로그 한 건이 약 150바이트(NAT444)~175바이트(DS-Lite)라서 가입자 한 명당 하루 약 5MB 가 쌓입니다[3].

**2. 조직 안의 중간 장비를 거꾸로 따라갑니다.** 내부 주소가 프록시·VPN 서버 주소라면 한 단계 더 거슬러 올라가야 합니다.

*프록시.* Squid 의 기본 `squid` 형식은 `%ts.%03tu %6tr %>a %Ss/%03>Hs %<st %rm %ru %[un %Sh/%<a %mt` 이고, 클라이언트 IP(`%>a`)와 사용자 이름(`%[un`)은 들어 있지만 클라이언트 출발지 포트(`%>p`)는 없습니다[20]. `%un` 은 프록시 인증 이름, 외부 ACL 이 준 이름, SSL 클라이언트 이름 가운데 처음 있는 값이라[20] 셋 다 없으면 값이 없습니다. 클라이언트 MAC(`%>eui`)은 형식에 넣어야 남습니다[20]. 요청 헤더의 Forwarded 로 원래 주소를 읽을 때는, 이 헤더를 요청한 클라이언트를 포함해 경로의 모든 노드가 바꿀 수 있어 믿을 수 없다는 점을 적습니다[21]. 비표준 헤더인 X-Forwarded-For 는 여러 프록시가 붙인 값 가운데 어느 값끼리 한 묶음인지도 알 수 없습니다[21].

*VPN.* OpenVPN 서버의 상태 파일(`--status`)은 기본 60초마다 새로 씁니다[22]. 기본 형식(`--status-version 1`)의 클라이언트 목록에는 Common Name, Real Address, Bytes Received, Bytes Sent, Connected Since 가 있고, 버전 2·3 에는 Virtual Address, Virtual IPv6 Address, Username 등이 더 붙습니다[22]. 상태 파일에는 쓴 시점의 접속 목록만 있으므로 지난 시각의 대응은 서버 로그나 접속·종료 스크립트가 남긴 기록에서 찾습니다. 접속·종료 스크립트에는 인증된 실제 접속 주소·포트(`trusted_ip`·`trusted_port`), 가상 주소(`ifconfig_pool_remote_ip`), 접속 시각(`time_unix`·`time_ascii`), 세션 길이(`time_duration`)가 환경 변수로 넘어갑니다[22]. 이 값을 기록하도록 스크립트를 짜 두었는지는 서버 설정에서 확인합니다. WireGuard 는 피어를 공개키로 구분하고, 피어가 외부 IP 를 바꿔 가며 붙을 수 있습니다[23]. 필드와 보존 방식은 [VPN 서버 로그](../../02-artifacts/devices/vpn-logs.md) 에 있습니다.

*클라우드.* AWS VPC 흐름 로그에서 나가는 트래픽의 `srcaddr` 는 보낸 네트워크 인터페이스의 사설 IPv4 주소나 IPv6 주소이고, NAT 게이트웨이처럼 중간 계층이 있으면 원래 출발지는 `pkt-srcaddr` 로 구분합니다[24]. 자세한 내용은 [AWS VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/aws/vpc-flow-logs.html) 에 있습니다.

**3. 내부 IP 를 그 시각의 MAC 주소로 잇습니다.** DHCP 주소는 정해진 기간 동안만 빌려주는 임대(lease)라서, 만료된 주소는 다른 클라이언트에게 다시 나갈 수 있습니다[5]. 주소가 모자라면 서버는 만료된 주소를 재사용하고, 이때 가장 오래전에 할당한 주소부터 고를 수 있습니다[5]. 그래서 "이 IP 의 주인" 이 아니라 "사건 시각을 포함하는 임대 구간의 주인" 을 찾습니다. 클라이언트는 기본으로 임대 기간의 0.5배(T1)가 지나면 갱신을 시도하고 0.875배(T2)가 지나면 브로드캐스트로 갱신을 요청합니다[5]. 기기가 예전 주소를 다시 요청해 같은 주소를 오래 쓰기도 하고, MAC 기준으로 주소를 고정해 둔 네트워크도 있습니다[6].

*Zeek dhcp.log.* DHCP 네 단계(DISCOVER·OFFER·REQUEST·ACK)를 한 줄로 합쳐 `mac`, `assigned_addr`, `lease_time`, `host_name`(옵션 12), `client_fqdn`(옵션 81), `msg_types` 를 남깁니다[6][7]. 트랜잭션 ID 로 메시지를 묶는 시간은 기본 30초(`DHCP::max_txid_watch_time`)입니다[7]. `ts` 는 첫 메시지를 본 시각이고 `duration` 은 첫 메시지부터 마지막 메시지까지의 간격이라 임대 기간이 아닙니다[7]. 임대 기간은 `lease_time` 입니다. DISCOVER 만 있는 줄에는 `server_addr` 가 없고[6], `client_addr` 는 클라이언트가 브로드캐스트가 아닌 주소로 메시지를 하나 이상 보냈을 때만 채워집니다[7].

아래는 사건 시각을 포함하는 임대를 찾는 예입니다(JSON 로그 기준, 주소는 만든 예시).

```
jq -c 'select(.assigned_addr=="10.0.40.23") | [.ts, .mac, .host_name, .lease_time, .msg_types]' dhcp.log
```

*Suricata dhcp 이벤트.* 기본 수준은 MAC 과 IP 를 잇는 데 필요한 만큼만 남기고, 전체 필드는 extended 설정에서 남습니다[8]. 기본 수준 예에도 `client_mac`, `assigned_ip`, `dhcp_type`, `client_id` 가 들어 있습니다[8].

*Windows DHCP 서버 감사 로그.* 기본 위치는 `%windir%\System32\Dhcp` 이고, 쉼표로 구분한 텍스트에 한 줄이 이벤트 하나입니다[12]. 파일 이름은 `DhcpSrvLog-Fri.log`(IPv4), `DhcpV6SrvLog-Fri.log`(IPv6)처럼 요일로 나뉩니다[15]. 필드는 Windows Server 2008 문서 기준 `ID, Date, Time, Description, IP Address, Host Name, MAC Address` 이고[12], 다른 판의 IPv4 로그 머리 줄에는 `User Name`, `TransactionID`, `QResult`, `VendorClass(ASCII)`, `RelayAgentInformation` 등이 더 있습니다[15]. 버전마다 필드가 다르므로 실제 파일의 머리 줄로 확인합니다. 이벤트 ID 10 은 새 임대, 11 은 갱신, 12 는 해제입니다[12]. 날짜는 `02/27/26` 처럼 월/일/두 자리 연도이고[15] 줄에 시간대 표시가 없습니다. 서버는 현지 시각 자정에 다음 요일 파일로 넘어가고, 그 파일이 24시간 넘게 바뀌지 않았으면 덮어쓰고 24시간 안에 바뀌었으면 이어 씁니다[13]. 이 규칙은 Windows Server 2003 시절 설명이라 최근 서버에서는 파일의 수정 시각과 첫 줄의 날짜로 확인합니다. 디스크 여유 공간이 `MinMBDiskSpace`(0 이나 생략이면 20MB)보다 적으면 서버는 감사 로그 기록을 멈춥니다[14].

*MAC 을 패킷에서 확인하기.* DHCP 기록이 없거나 고정 주소라면 그 시각 패킷의 MAC 을 봅니다. Zeek conn.log 의 `orig_l2_addr` 는 `policy/protocols/conn/mac-logging.zeek` 를 불러와야 남습니다[10]. Suricata 는 `ethernet: yes` 이면 이벤트에 이더넷 헤더를 붙이고(기본 no), arp 이벤트는 양이 많아 기본으로 꺼져 있습니다[9]. 센서가 라우터 바깥에 있으면 패킷의 MAC 은 라우터의 MAC 이므로, 같은 네트워크 구간에서 캡처한 기록인지 확인합니다([어디서 캡처하나](../../01-foundations/capture/capture-points.md)).

**4. MAC 과 기기 이름을 기기로 잇습니다.** DHCP 의 호스트 이름(옵션 12)과 FQDN(옵션 81)은 클라이언트가 스스로 보낸 값입니다[7]. client identifier 옵션에는 하드웨어 주소가 들어갈 수도, DNS 이름 같은 다른 값이 들어갈 수도 있습니다[5]. 그래서 이 값들은 자산 관리 목록, 스위치 포트 기록, 기기 쪽 기록과 맞춰 봐야 기기로 확정됩니다. 기기 이미지가 있으면 그 기기가 그 시각에 그 주소를 받았는지 기기 쪽 기록으로 확인합니다([Windows 네트워크 인터페이스 설정](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/tcp-ip-interfaces.html), [macOS 네트워크 인터페이스와 설정](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/network/network-interfaces.html), [Linux 네트워크 설정](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/network-config.html)).

Zeek software.log 는 호스트마다 `software_type`, `name`, `unparsed_version`(User-Agent 같은 원문 문자열)을 남깁니다[11]. 한 IP 에서 서로 다른 운영체제·브라우저 문자열이 같은 시간대에 함께 나오면 그 주소 뒤에 기기가 여러 대 있을 가능성이 있습니다.

**5. 기기를 계정으로 잇습니다.** 같은 IP 에서 사건 시각 앞뒤로 일어난 인증 기록을 찾습니다. kerberos.log 에는 요청 종류(`request_type`, AS·TGS), `client`, `service`, `success` 가 있습니다[17]. ntlm.log 의 `username`·`hostname`·`domainname` 은 클라이언트가 준 값이고 `success` 는 인증 성공 여부입니다[18]. RADIUS 로 인증하는 네트워크라면 radius.log 에 `username`, `mac`, `result` 가 남습니다[19]. radius.log 의 `framed_addr` 는 RADIUS 서버가 접속 장비(NAS)에 준 주소지만 접속 장비가 꼭 따르지는 않는 힌트라서[19], 실제 할당 주소는 DHCP·접속 장비 기록으로 확인합니다. 인증 기록으로는 "그 시각 그 IP 에서 이 계정 이름으로 인증했다(또는 시도했다)" 까지만 알 수 있습니다. 로그인한 사람은 기기의 로그온 기록과 맞춰 봅니다([Windows 계정 탈취와 측면 이동](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/credential-theft-lateral-movement/)).

**6. IPv6 주소라면 임시 주소를 고려합니다.** 임시 주소 확장을 쓰는 기기는 SLAAC 프리픽스마다 무작위 인터페이스 ID 로 임시 주소를 만들어 주기적으로 바꾸고, 기본값은 유효 기간 2일, 선호 기간 1일입니다[16]. 구현은 나가는 연결에 임시 주소를 기본으로 쓰도록 할 수 있습니다[16]. 새 임시 주소는 이전 주소와 연관 짓기 어렵게 만들어지므로[16], 같은 기기라도 날마다 다른 주소로 보일 수 있습니다. DHCP 서버를 거치지 않으니 DHCP 로그도 없을 수 있습니다. 이때는 /64 프리픽스로 네트워크 구간을 좁힌 뒤, 그 시각의 주소와 MAC 의 대응 기록(라우터·스위치 기록, 패킷의 MAC)을 찾습니다.

**7. 결과를 시간순으로 합칩니다.** 단계마다 찾은 기록(변환 기록 → 프록시·VPN → DHCP 임대 → MAC → 인증)을 시각과 함께 한 표로 정리하고, 각 기록의 시간대와 시계 차이를 적습니다([네트워크 타임라인](../../03-techniques/analysis/timeline.md)). 기관마다 시계가 다를 때는 일관되게 기록돼 있기만 하면 두 기록의 차이를 계산해 보정할 수 있다는 의견이 있습니다[4]. 반면 RFC 6302 는 추적 가능한 시간원과 UTC 를 권고합니다[1]. 보정했다면 무엇을 기준으로 몇 초를 보정했는지 보고서에 적습니다.

## 흔한 오판

**IP 하나를 사람 하나로 읽는 경우.** 집·회사 공유기, 모바일 망, CGN 뒤에서는 여러 기기가 IP 하나를 나눠 씁니다. 포트와 정확한 시각이 없으면 가입자를 특정할 수 없습니다[1][4]. 공유 주소로 수사가 막히는 문제는 흔해서, 한 설문에서는 응답자의 90% 가 CGN 때문에 귀속 문제를 자주 겪는다고 답했습니다. 이 설문은 한 사람이 쓴 개인 인터넷 초안(draft-daveor-cgn-logging-04, 2018, 만료)에 인용된 것입니다[4].

**서버가 포트를 남겼을 것이라고 가정하는 경우.** 같은 초안에 실린 제품 문서 검토 표에서 출발지 포트를 기본으로 남기는 것은 OpenSSH 7.5 뿐이었습니다. Apache 2.4.25·IIS 10·nginx 1.12.0·Squid 3.5.25·Postfix 2.10.0·Exim 4.89 는 설정하면 남길 수 있지만 기본은 아니었고, UW IMAP·Oracle 12.2·MySQL 5.7.18 은 남기는 방법이 문서에 없거나 남길 수 없었습니다[4]. 상대 기관에 요청하기 전에 그쪽 로그에 포트가 있는지부터 묻습니다.

**IP 주소의 현재 할당을 과거에 적용하는 경우.** 지금 그 IP 를 쓰는 기기가 사건 시각에도 썼다는 보장이 없습니다. 임대는 만료되면 다른 클라이언트에게 갈 수 있습니다[5]. 반드시 사건 시각을 포함하는 임대 구간을 찾습니다.

**Zeek dhcp.log 의 `duration` 을 임대 기간으로 읽는 경우.** `duration` 은 DHCP 메시지를 주고받은 시간이고, 임대 기간은 `lease_time` 입니다[7].

**MAC·호스트 이름·계정 이름을 확정된 신원으로 쓰는 경우.** DHCP 호스트 이름·client identifier, NTLM 의 사용자·호스트·도메인 이름은 클라이언트가 보낸 값입니다[5][7][18]. 기기가 바꿔 보낼 수 있고, 한 계정을 여러 사람이 쓸 수도 있습니다.

**VPN 인증서 이름 하나를 사람 하나로 읽는 경우.** OpenVPN 은 `--duplicate-cn` 을 켜면 같은 Common Name 으로 여러 클라이언트가 동시에 접속할 수 있고, 끄면 같은 이름으로 새 클라이언트가 붙을 때 먼저 붙은 쪽을 끊습니다[22]. `--ifconfig-pool-persist` 파일(`<Common-Name>,<IP-address>`)의 대응은 제안일 뿐이라 같은 이름이 늘 같은 가상 주소를 받는다는 보장이 없습니다[22]. `--log` 는 시작할 때 기존 로그 파일을 잘라내고 새로 쓰므로(`--log-append` 는 이어 씀), 서버를 다시 시작하면 그전 기록이 사라졌을 수 있습니다[22].

**DHCP 감사 로그가 비어 있으니 그 주소를 아무도 쓰지 않았다고 쓰는 경우.** 일주일이 지나 파일을 덮어썼거나, 디스크 여유 공간이 모자라 기록이 멈췄을 수 있습니다(이벤트 ID 02: 디스크 부족으로 일시 중지)[12][13][14]. 고정 주소를 쓰는 기기는 DHCP 기록이 아예 없습니다.

## 보고서 문장 예

아래 값은 모두 만든 예시입니다.

> 요청서의 공인 주소 203.0.113.10, 출발지 포트 40512, 시각 2026-09-01 13:05:22(UTC)는 조직 방화벽의 NAT 변환 기록에서 내부 주소 10.0.40.23, 출발지 포트 55120 에 대응합니다. 내부 DHCP 서버 감사 로그에는 2026-09-01 08:51:03(서버 현지 시각, UTC+9)에 10.0.40.23 을 MAC 주소 00:00:5e:00:53:17, 호스트 이름 PC-SALES-07 에 새로 임대한 기록(이벤트 ID 10)이 있고, 13:05:22(UTC) 전후로 이 주소의 해제·다른 기기 임대 기록은 없습니다. 같은 날 12:40(UTC) 에 10.0.40.23 에서 계정 kim.example 로 Kerberos AS 요청이 성공한 기록이 있습니다. 이 기록으로는 해당 시각에 이 주소가 이 기기에 할당돼 있었고 이 계정으로 인증이 있었다는 것까지 확인되며, 그 시각에 기기를 조작한 사람은 기기의 로그온 기록과 대조해야 합니다.

> 요청서에는 공인 주소 198.51.100.77 과 시각(분 단위)만 있고 출발지 포트가 없습니다. 이 주소는 이동통신사의 공유 주소 대역으로, 포트와 초 단위 시각 없이는 해당 시각의 가입자를 특정할 수 없습니다.

## 함께 볼 페이지

- [피싱 링크를 눌렀나](phishing-click.md)
- [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md), [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)
- [DHCP 로그](../../02-artifacts/devices/dhcp-logs.md), [VPN 서버 로그](../../02-artifacts/devices/vpn-logs.md), [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md), [방화벽 로그](../../02-artifacts/devices/firewall-logs.md)
- [비밀번호를 무작위로 넣어 봤나](../intrusion/brute-force.md), [내부에서 다른 PC 로 옮겨 갔나](../intrusion/lateral-movement.md)
- [네트워크 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)
- 기기 쪽 VPN 기록: [Windows VPN 연결 기록](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/vpn-connections.html), [macOS VPN 구성](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/network/vpn.html), [Linux VPN](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/vpn.html)

## 참고 문헌

1. J. Durand, I. Gashinsky, D. Lee, S. Sheppard, "Logging Recommendations for Internet-Facing Servers", RFC 6302 (BCP 162), 2011. https://www.rfc-editor.org/rfc/rfc6302.txt
2. F. Audet, C. Jennings, "Network Address Translation (NAT) Behavioral Requirements for Unicast UDP", RFC 4787 (BCP 127), 2007. https://www.rfc-editor.org/rfc/rfc4787.txt
3. C. Donley 외, "Deterministic Address Mapping to Reduce Logging in Carrier-Grade NAT Deployments", RFC 7422, 2014. https://www.rfc-editor.org/rfc/rfc7422.txt
4. David O'Reilly, "Approaches to Address the Availability of Information in Criminal Investigations Involving Large-Scale IP Address Sharing Technologies", IETF Internet-Draft draft-daveor-cgn-logging-04, 2018. https://datatracker.ietf.org/doc/html/draft-daveor-cgn-logging-04
5. R. Droms, "Dynamic Host Configuration Protocol", RFC 2131, 1997. https://www.rfc-editor.org/rfc/rfc2131.txt
6. Zeek 문서, "dhcp.log". https://github.com/zeek/zeek-docs/blob/master/logs/dhcp.rst
7. Zeek 스크립트 참조, "base/protocols/dhcp/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dhcp/main.zeek.rst
8. Suricata 사용자 안내서, "Eve JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
9. Suricata 사용자 안내서, "Eve JSON Output". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
10. Zeek 스크립트 참조, "base/protocols/conn/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
11. Zeek 문서, "known_*.log and software.log". https://github.com/zeek/zeek-docs/blob/master/logs/known-and-software.rst
12. Microsoft, "Analyze DHCP Server Log Files" (Windows Server 2008). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/dd183591(v=ws.10)
13. Microsoft 보관 블로그, "All about DHCP Auditing", 2006. https://learn.microsoft.com/en-us/archive/blogs/anto_rocks/all-about-dhcp-auditing
14. Microsoft, "Set-DhcpServerAuditLog". https://learn.microsoft.com/en-us/powershell/module/dhcpserver/set-dhcpserverauditlog?view=windowsserver2025-ps
15. NXLog 문서, "Windows DHCP Server". https://docs.nxlog.co/integrate/windows-dhcp-server.html
16. F. Gont, S. Krishnan, T. Narten, R. Draves, "Temporary Address Extensions for Stateless Address Autoconfiguration in IPv6", RFC 8981, 2021. https://www.rfc-editor.org/rfc/rfc8981.txt
17. Zeek 스크립트 참조, "base/protocols/krb/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/krb/main.zeek.rst
18. Zeek 스크립트 참조, "base/protocols/ntlm/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ntlm/main.zeek.rst
19. Zeek 스크립트 참조, "base/protocols/radius/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/radius/main.zeek.rst
20. Squid 설정 원본, `src/cf.data.pre` (logformat, access_log). https://github.com/squid-cache/squid/blob/master/src/cf.data.pre
21. A. Petersson, M. Nilsson, "Forwarded HTTP Extension", RFC 7239, 2014. https://www.rfc-editor.org/rfc/rfc7239.txt
22. OpenVPN, "Reference manual for OpenVPN 2.6". https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/
23. Jason A. Donenfeld, "WireGuard: Next Generation Kernel Network Tunnel", Network and Distributed System Security Symposium (NDSS), 2017. doi:10.14722/ndss.2017.23160
24. AWS, "Logging IP traffic using VPC Flow Logs — Flow log records". https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html
