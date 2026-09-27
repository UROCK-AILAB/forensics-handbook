---
title: "IP 주소·포트·NAT 해석"
parent: "기반 · 기록 체계"
nav_order: 130
---

# IP 주소·포트·NAT 해석 (IP·Port·NAT)

네트워크 기록에 남은 IP 주소와 포트는 기록한 장비가 그 자리에서 본 값이고, 그 사이에 주소 변환 (NAT, Network Address Translation) 장비가 있으면 같은 연결도 기록마다 다른 주소로 남습니다. 이 페이지에서는 특수 주소 대역과 포트 번호 범위를 읽는 법, NAT 가 주소와 포트를 바꾸는 방식, 변환 전후 주소를 잇는 기록이 어디에 남는지를 설명합니다. 공인 IP 주소 하나로 사람이나 기기를 특정할 수 있는지 판단할 때 필요한 조건도 함께 다룹니다.

## 이 내용이 필요한 기록

패킷 캡처(pcap·pcapng), 흐름 기록(NetFlow·IPFIX), Zeek 로그, Suricata EVE 로그, 방화벽·프록시·DNS·DHCP·VPN 로그에는 모두 출발지·목적지 주소와 포트가 들어 있습니다. 이 값을 사람이나 기기로 이으려면 먼저 그 주소가 어떤 대역인지, 기록 지점이 NAT 안쪽인지 바깥쪽인지 알아야 합니다. 캡처 지점에 따라 보이는 주소가 달라지는 것은 [어디서 캡처하나](../capture/capture-points.md)에서, 로그 종류별 개요는 [네트워크 로그의 종류](log-types.md)에서, 기록마다 시각을 읽는 법은 [네트워크 기록의 시각](timestamps.md)에서 다룹니다. 실제 사건에서 공인 IP 의 사용자를 찾는 흐름은 [이 시각에 이 IP 를 누가 썼나](../../04-scenarios/user-activity/ip-attribution.md)에 있습니다.

## 구조

### 특수 주소 대역

아래 대역은 인터넷의 한 기기를 가리키는 주소가 아니므로, 로그에 나오면 먼저 대역부터 확인합니다.

| 대역 | 이름·용도 | 해석할 때 |
|---|---|---|
| 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 | 사설 주소[1] | 조직마다 같은 값을 다시 쓰므로 그 망 안에서만 뜻이 있습니다 |
| 100.64.0.0/10 | 공유 주소 공간 (Shared Address Space)[2] | 통신사의 대규모 NAT (CGN, Carrier-Grade NAT) 와 가입자 장비 사이에 씁니다. 통신사 경계를 넘어 전달하면 안 됩니다[2] |
| 127.0.0.0/8, ::1/128 | 루프백[5] | 같은 기기 안의 통신입니다 |
| 169.254.0.0/16, fe80::/10 | 링크 로컬[5] | 같은 링크 안에서만 쓰는 주소입니다 |
| fc00::/7 | IPv6 고유 로컬 주소 (ULA)[5] | IPv6 의 사설 주소에 해당합니다 |
| 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24, 2001:db8::/32 | 문서용[3][4] | 실제 통신에 나오면 설정 오류나 만든 값일 가능성이 있습니다 |
| 192.0.0.0/29 | DS-Lite[5] | IPv4 를 IPv6 로 감싸 보내는 DS-Lite 에 씁니다[11] |
| 198.18.0.0/15 | 장비 성능 시험용[5] | |
| 0.0.0.0/8, ::/128, 240.0.0.0/4, 255.255.255.255/32 | 이 네트워크·지정 안 됨·예약·브로드캐스트[5] | |
| ::ffff:0:0/96 | IPv4 매핑 IPv6 주소[5] | 대응하는 IPv4 주소가 있습니다 |
| 64:ff9b::/96 | IPv4-IPv6 변환 (NAT64)[5] | 주소 안에 IPv4 주소가 들어 있습니다(예: 64:ff9b::c633:6464 → 198.51.100.100)[19] |
| 2001::/32 | Teredo[5] | |

### 포트 번호 범위

IANA 는 포트를 시스템 포트(잘 알려진 포트) 0~1023, 사용자 포트(등록 포트) 1024~49151, 동적 포트(사설·임시 포트) 49152~65535 로 나누고, 동적 포트는 어떤 서비스에도 할당하지 않습니다[6]. 연결을 여는 쪽이 고르는 임시 포트 (ephemeral port) 범위는 운영체제마다 기본값이 다릅니다.

| 기준 | 임시 포트 범위 |
|---|---|
| IANA 동적 포트[6] | 49152~65535 |
| RFC 6056 권고[7] | 1024~65535 전체를 쓰는 것이 좋습니다 |
| Linux `net.ipv4.ip_local_port_range` 기본값[8] | 32768~60999 |
| Windows Vista·Server 2008 이후[9] | 49152~65535 |
| 그 이전 Windows[9] | 1025~5000 |

Windows 는 TCP 와 UDP 범위를 따로 설정하고, `netsh int ipv4 show dynamicport tcp`, `netsh int ipv4 show dynamicport udp` 로 현재 값을 확인합니다[9]. 범위는 설정으로 바꿀 수 있고 NAT 를 지나면 출발지 포트가 바뀌므로, 출발지 포트 범위로는 운영체제를 "그럴 가능성이 있다" 는 정도까지만 짐작할 수 있습니다.

### NAT 가 주소와 포트를 바꾸는 방식

NAT 는 내부 주소·포트(X:x)를 외부 주소·포트(X':x')로 바꾸는 매핑 (mapping) 을 만듭니다. 같은 X:x 가 어느 목적지로 가든 같은 X':x' 를 쓰면 끝점 독립 매핑 (Endpoint-Independent Mapping), 목적지 주소가 같을 때만 다시 쓰면 주소 의존 매핑, 목적지 주소와 포트가 모두 같을 때만 다시 쓰면 주소·포트 의존 매핑이라고 합니다[10]. RFC 4787 은 UDP 에 대해 끝점 독립 매핑을 필수로 정했습니다[10].

외부 주소가 여러 개인 NAT 는 한 내부 주소에 세션마다 다른 외부 주소를 줄 수도 있고("Arbitrary"), 한 내부 주소에는 늘 같은 외부 주소를 줄 수도 있습니다("Paired")[10]. RFC 4787 은 Paired 를 권하고[10], CGN 요구 사항인 RFC 6888 은 CGN 의 기본 동작을 Paired 로 정했습니다[11]. Arbitrary 로 설정한 NAT 뒤에서는 한 내부 기기가 같은 시간대에 여러 공인 주소로 나타날 수 있습니다.

외부 포트를 고르는 방식도 장비마다 다릅니다. 내부 포트를 그대로 외부 포트로 쓰려는 방식을 포트 보존 (port preservation) 이라고 하는데, 포트가 겹치면 다른 외부 주소를 쓰거나 결국 다른 포트를 고릅니다[10]. 처음부터 포트를 맞추지 않는 NAT 도 있습니다[10]. 그래서 외부 로그의 출발지 포트가 내부 기기의 출발지 포트와 같다고 가정할 수 없습니다. 패킷이 오가지 않는 UDP 매핑도 2분 안에 없애면 안 되고(잘 알려진 목적지 포트는 예외), 기본값은 5분 이상이 권장됩니다[10]. 매핑이 사라진 뒤에는 같은 외부 포트를 다른 내부 기기가 받을 수 있고, 포트를 곧바로 다시 쓰는 CGN 도 있습니다[12].

### 변환 전후 주소가 남는 곳

**Linux netfilter 연결 추적(conntrack).** 연결 추적 테이블은 연결마다 원래 방향 (original) 과 응답 방향 (reply) 을 따로 등록합니다[15]. SNAT 된 연결은 원래 방향의 출발지 주소와 응답 방향의 목적지 주소가 다르므로, 두 방향을 비교하면 변환 전후 주소를 알 수 있습니다. `conntrack -L` 은 현재 테이블을, `conntrack -L --src-nat` 과 `--dst-nat` 은 NAT 된 연결만 보여 주고, `--orig-src`·`--orig-dst`·`--reply-src`·`--reply-dst` 로 방향별 주소를 걸러 냅니다[16]. `conntrack -E -o timestamp` 는 연결 이벤트를 시각과 함께 실시간으로 보여 줍니다[16]. 이 테이블은 커널 메모리에 있으므로 실행 중인 시스템에서 수집해야 하고, 이벤트를 따로 기록해 두지 않았다면 과거 매핑은 남아 있지 않을 가능성이 큽니다. 기본 설정에서는 바이트·패킷 수(`nf_conntrack_acct`)와 흐름 시각(`nf_conntrack_timestamp`)을 모으지 않습니다[15]. 제한 시간 기본값은 설정된 TCP 연결이 432000초(5일), UDP 가 30초(스트림으로 판단하면 120초)입니다[15].

**iptables NAT 대상.** MASQUERADE 는 nat 테이블의 POSTROUTING 체인에서만 쓰고, 나가는 인터페이스의 주소로 바꾸며 인터페이스가 내려가면 연결을 잊습니다[17]. SNAT(`--to-source`)은 포트 범위를 주지 않으면 512 미만 포트는 512 미만으로, 512~1023 은 1024 미만으로, 나머지는 1024 이상으로 바꾸고, 가능하면 포트를 바꾸지 않습니다[17]. DNAT(`--to-destination`)은 PREROUTING·OUTPUT 체인에서 목적지를 바꿉니다[17]. `--random`(커널 2.6.21 이상), `--random-fully`(SNAT 은 3.14, MASQUERADE 는 3.13 이상)를 쓰면 출발지 포트를 무작위로 고르고, 커널 5.0 부터 MASQUERADE 의 `--random` 은 `--random-fully` 와 같습니다[17]. `--persistent` 는 한 클라이언트에 늘 같은 주소를 줍니다[17]. 규칙 파일에 이 옵션이 있는지 보면 외부 포트와 내부 포트가 같을 가능성을 판단할 수 있습니다.

**netfilter 에서 로그 규칙이 보는 주소.** 다른 기기로 넘기는 패킷은 prerouting → forward → postrouting 훅을 차례로 지나고, 같은 훅 안에서는 우선순위가 낮은 숫자부터 처리합니다[18]. 연결 추적은 -200, 목적지 NAT(dstnat)는 -100, filter 는 0, 출발지 NAT(srcnat)는 100 입니다[18]. 이 순서라서 FORWARD 체인에 둔 LOG 규칙에는 DNAT 을 거친 뒤의 목적지 주소와 SNAT 을 거치기 전의 출발지 주소(내부 사설 주소)가 남습니다. 같은 방화벽이라도 LOG 규칙을 어느 체인에 두었는지에 따라 남는 주소가 달라지므로, 실제 규칙 위치를 확인하고 해석합니다. 방화벽 로그 형식은 [방화벽 로그](../../02-artifacts/devices/firewall-logs.md)에서 다룹니다.

**OpenBSD pf.** `nat-to` 는 주로 나가는 쪽에 쓰고 출발지 포트도 암묵적으로 바꾸며, `rdr-to` 는 주로 들어오는 쪽에 쓰고 포트를 명시적으로 바꿉니다[19]. `binat-to` 는 외부 대역과 내부 대역을 양방향으로 잇고 포트는 바꾸지 않습니다[19]. pflog 헤더에는 `rewritten` 필드와 `saddr`·`daddr`·`sport`·`dport` 필드가 있고, pflog 인터페이스는 `tcpdump -n -e -ttt -i pflog1` 처럼 읽습니다[20]. 이 주소가 변환 전인지 후인지는 읽은 출력과 규칙을 맞춰 보고 판단합니다.

**IPFIX NAT 로그(RFC 8158).** NAT 장비가 IPFIX 로 매핑을 내보내면 `natEvent` 필드(IE 230)에 이벤트 종류가 들어가고, `timeStamp` 필드에는 이벤트를 기록한 시각이 들어갑니다[14].

| natEvent | 뜻 |
|---|---|
| 1, 2 | NAT 변환 생성·삭제(Historic) |
| 3 | NAT 주소 소진 |
| 4, 5 | NAT44 세션 생성·삭제 |
| 6, 7 | NAT64 세션 생성·삭제 |
| 8, 9 / 10, 11 | NAT44 / NAT64 BIB 생성·삭제 |
| 12 | NAT 포트 소진 |
| 13 | 할당량 초과 |
| 14, 15 | 주소 바인딩 생성·삭제 |
| 16, 17 | 포트 블록 할당·해제 |
| 18 | 임계값 도달 |

NAT44 세션 생성·삭제 레코드의 필수 필드는 `timeStamp`(64비트, IE 323 observationTimeMilliseconds), `natEvent`, `sourceIPv4Address`(8), `postNATSourceIPv4Address`(225), `protocolIdentifier`(4), `sourceTransportPort`(7), `postNAPTSourceTransportPort`(227)이고, 목적지 주소와 포트는 선택 필드입니다[14]. 포트 블록 할당 레코드는 `portRangeStart` 가 필수이고 `portRangeEnd` 는 선택입니다[14]. Cisco ASA 의 NSEL·NEL 레코드는 nfdump 로 읽을 수 있고, NSEL 지원으로 빌드한 nfdump 는 변환 주소를 `-A xsrcip,xdstip` 으로 집계합니다. `-s nat`·`-s natsrcip`·`-s natsrcport` 같은 통계도 냅니다[21]. 흐름 기록 전체 구조는 [흐름 기록](flow-records.md)에서, nfdump 사용법은 [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md)에서 다룹니다.

**통신사 CGN 로그.** 공인 주소·포트·시각으로 가입자를 찾으려면 CGN 이 매핑마다 전송 프로토콜, 가입자 식별자, 외부 출발지 주소, 외부 출발지 포트, 시각을 기록해야 합니다[11]. 가입자 식별자는 보통 내부 출발지 주소이지만, DS-Lite 처럼 여러 가입자가 같은 내부 주소를 쓰면 터널 끝점의 IPv6 주소입니다[11]. 목적지 주소와 포트는 관리상 필요한 경우가 아니면 개인정보 문제로 기록하지 않는 것이 권고입니다(REQ-12)[11]. 포트를 가입자별 블록으로 나눠 주는 방식에서는 블록을 할당하거나 해제할 때만 로그를 남깁니다[13]. 이런 로그는 통신사가 보관하므로 조사에서는 법적 절차로 요청해야 합니다.

## 읽는 법

### 로그별로 주소를 읽는 기준

| 기록 | 주소 필드 | 읽을 때 |
|---|---|---|
| Zeek conn.log | `id.orig_h`·`id.orig_p`(연결을 연 쪽), `id.resp_h`·`id.resp_p`(응답한 쪽)[22] | `history` 에 `^` 가 있으면 Zeek 가 방향을 뒤집은 것입니다. `conn_state` 가 `OTH` 이면 SYN 없이 중간부터 본 연결이라 방향 근거가 약합니다[22] |
| Zeek `local_orig`·`local_resp` | `Site::local_nets` 에 든 대역이면 T[22] | `Site::local_nets` 를 정의하지 않으면 늘 비어 있습니다[22]. 100.64.0.0/10 을 넣었는지도 확인합니다 |
| Suricata EVE | `src_ip`·`dest_ip`, alert 등의 `direction`(`to_server`·`to_client`)[23] | `flow_id` 는 Suricata 내부 값이라, 다른 도구의 기록과 맞추려면 `community_id` 를 켭니다[24] |
| AWS VPC 흐름 로그 | `srcaddr`·`dstaddr`, `pkt-srcaddr`·`pkt-dstaddr`[25] | 나가는 트래픽의 `srcaddr` 는 네트워크 인터페이스의 IPv4 사설 주소나 IPv6 주소이고, `pkt-srcaddr` 는 패킷의 원래 출발지 주소입니다[25]. 자세한 내용은 [VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/aws/vpc-flow-logs.html)에 있습니다 |
| Squid access.log | `%>a`(클라이언트 출발지 주소), `%>p`(클라이언트 출발지 포트)[26] | 기본 `squid` 형식에는 `%>a` 만 있고 포트가 없습니다[26]. 프록시 앞에 NAT 가 있으면 `%>a` 는 NAT 주소입니다. 자세한 내용은 [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md) |
| OpenVPN 상태 파일 | Real Address, Virtual Address[27] | 여러 클라이언트를 받는 서버의 상태 파일에서 `--status-version 1`(기본)의 클라이언트 목록에는 실제 접속 주소(Real Address)가 있고, 2·3 의 목록에는 가상 주소(Virtual Address)도 들어가 가상 IP 와 실제 IP 를 잇는 근거가 됩니다[27] |
| WireGuard | 피어의 끝점(endpoint)[28] | 올바르게 인증된 패킷의 바깥 출발지 주소로 끝점을 정해 피어가 주소를 옮겨 다닐 수 있으므로[28], 현재 상태만으로는 과거 접속 주소를 알 수 없습니다. [VPN 서버 로그](../../02-artifacts/devices/vpn-logs.md) 참고 |
| DHCP 감사 로그 | IP 주소, 호스트 이름, MAC 주소[29] | 이벤트 10(새 임대)·11(갱신)·12(해제)로 시간대별 IP 와 기기를 잇습니다[29]. [DHCP 로그](../../02-artifacts/devices/dhcp-logs.md) 참고 |

Zeek 와 Suricata 의 필드 세부는 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md)와 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)에서 다룹니다.

### 외부 기록을 내부 기기로 잇기 (만든 예시)

외부 웹 서버 로그에 `203.0.113.50` 포트 `40123` 에서 들어온 요청이 있다고 가정합니다. 아래 표는 모두 만든 예시입니다.

| 순서 | 기록 | 맞추는 값 | 얻는 값 |
|---|---|---|---|
| 1 | 외부 웹 서버 로그 | — | 출발지 `203.0.113.50:40123`, TCP, 2026-03-05 02:14:07 UTC |
| 2 | 조직 경계 NAT 의 IPFIX 로그(`natEvent` 4) | `postNATSourceIPv4Address` = 203.0.113.50, `postNAPTSourceTransportPort` = 40123, `protocolIdentifier` = 6, `timeStamp` 가 1의 시각 이전이고 같은 매핑의 삭제(5) 이벤트가 1의 시각 이후 | `sourceIPv4Address` = 10.0.5.23, `sourceTransportPort` = 52311 |
| 3 | 내부 방화벽 FORWARD 로그 또는 Zeek conn.log | 10.0.5.23:52311, 같은 시간대 | 목적지와 주고받은 양 |
| 4 | DHCP 감사 로그 | 그 시각에 10.0.5.23 을 임대한 기록 | 호스트 이름, MAC 주소 |

2단계에서 외부 포트가 빠지면 같은 공인 주소를 쓴 내부 기기가 여럿 나오고, 시각이 어긋나면 이미 다른 기기에 다시 배정된 매핑을 고를 수 있습니다. 여기까지 이어도 알 수 있는 것은 그 시각에 그 IP 를 쓴 기기까지이고, 기기를 쓴 사람은 호스트 쪽 기록으로 따로 확인합니다.

## 포렌식에서 중요한 점

### 증명하는 것

주소와 포트는 그 기록 지점에서 본 값을 증명합니다. NAT 매핑 로그가 있으면 공인 주소·포트·프로토콜·시각으로 내부 주소와 포트를 찾을 수 있고, DHCP 로그를 더하면 그 시각의 기기까지 이을 수 있습니다.

### 증명하지 못하는 것

CGN 이나 조직 NAT 뒤에서는 여러 가입자와 기기가 같은 공인 주소를 쓰므로, 공인 IP 주소 하나로는 사람이나 기기를 특정하지 못합니다[11][12][13]. 사설 주소와 공유 주소 공간은 다른 조직·다른 통신사에서 같은 값을 다시 쓰므로 전역 식별자가 아닙니다[1][2]. NAT 매핑 기록이 없으면 외부 로그의 공인 주소를 내부 주소로 되돌릴 수 없습니다.

### 두 기록을 잇는 조건

인터넷에 공개된 서버는 접속 주소와 함께 출발지 포트와 시각을 기록하는 것이 권고 사항입니다. 시각은 NTP 처럼 추적할 수 있는 시각 원천에 맞춘 UTC 로 초 단위 이상 정확해야 하고, 서버가 여러 전송 프로토콜이나 포트를 쓰면 전송 프로토콜과 목적지 포트도 기록합니다[12]. CGN 은 포트를 바로 다시 쓰기도 하고 몇 분 기다리기도 해서, 서버 쪽 시각이 정확해야 합니다[12]. 완전히 추적하려면 원격 서버가 출발지 주소와 포트를 기록하고, 양쪽 로그에 시각이 있고, 두 시계가 어느 정도 맞아야 합니다[13]. 서버가 포트를 기록하지 않았고 NAT 가 포트 블록 단위로만 기록했다면, 그 시간대에 그 공인 주소에 매핑된 내부 주소 목록까지만 알 수 있습니다[13].

목적지 기록에 대해서는 문서마다 입장이 다릅니다. RFC 6888 은 CGN 이 목적지를 기록하지 않는 것을 권하고[11], RFC 7768 은 서버가 포트를 기록하지 않을 때는 NAT 가 목적지 주소를 기록해야 추적할 수 있지만 그래도 완전하지 않다고 적었습니다[13]. RFC 8158 은 목적지 필드를 선택 항목으로 둡니다[14]. 그래서 NAT 로그에 목적지가 있는지는 장비 설정마다 다르며, 실제 로그 필드로 확인합니다.

### 시각

NAT 로그의 시각은 매핑을 만들거나 지운 이벤트를 기록한 때이고[14], 서버 로그의 시각은 요청을 받은 때라서 둘은 대개 다릅니다. 매핑이 만들어진 시각과 삭제된 시각 사이에 서버 로그 시각이 들어가는지로 판단하고, 두 장비의 시계 차이를 먼저 확인합니다. 포트 블록을 해제할 때 보호 시간(guard time)을 두는 이유 가운데 하나도 양쪽 시계 오차를 견디기 위해서입니다[13]. 기록별 시각 기준과 UTC 여부는 [네트워크 기록의 시각](timestamps.md)에서 다룹니다.

## 함정

**같은 연결이 센서 위치마다 다른 주소로 남습니다.** NAT 안쪽 센서에는 내부 사설 주소가, 바깥쪽 센서와 외부 장비에는 변환된 공인 주소가 남습니다. 두 기록을 같은 기기로 이으려면 conntrack 이벤트나 NAT 로그처럼 변환 전후를 함께 담은 기록이 필요합니다[15][16].

**MASQUERADE 는 회선이 다시 연결되면 매핑을 잊습니다.** 인터페이스가 내려가면 연결을 잊으므로[17], 회선 재연결 전후로 공인 주소와 매핑이 바뀔 수 있습니다.

**포트 범위가 NAT 뒤에서도 유지된다는 보장은 없습니다.** 0~1023 포트를 같은 범위로, 1024 이상을 1024 이상으로 옮기는 것은 권고와 SNAT 기본 동작일 뿐이고[10][17], `--random-fully` 나 포트 보존을 하지 않는 NAT 를 거치면 외부 포트와 내부 포트의 관계가 없어집니다.

**탐지 규칙의 "내부 주소" 목록이 대역을 빠뜨릴 수 있습니다.** SigmaHQ 의 `zeek_rdp_public_listener` 규칙은 10/8, 127/8, 172.16/12, 192.168/16, 169.254/16, ::1, fc00::/7, fe80::/10, 2620:83:8000::/48 을 내부로 보고 100.64.0.0/10 은 넣지 않았습니다[30]. `proxy_webdav_external_execution` 규칙의 `filter_main_local_ips` 도 100.64.0.0/10 이 없습니다[31]. CGN 이나 일부 클라우드 망처럼 이 대역을 내부에서 쓰는 환경에서는 내부 통신을 외부로 잘못 분류할 수 있으므로, 쓰는 규칙의 대역 목록을 환경에 맞춰 확인합니다. 규칙 활용은 [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md)에서 다룹니다.

**같은 호스트가 두 가지 주소 형식으로 남을 수 있습니다.** IPv4 매핑 IPv6 주소(`::ffff:192.0.2.10` 처럼 ::ffff:0:0/96 대역)는 대응하는 IPv4 주소가 있고[5], NAT64 주소(64:ff9b::/96)는 안에 IPv4 주소가 들어 있습니다[19]. 한 기록은 `192.0.2.10`, 다른 기록은 `::ffff:192.0.2.10` 으로 남으면 문자열 비교로는 같은 호스트임을 놓칩니다(만든 예시).

**conntrack 기본 설정에는 양과 시각이 없습니다.** `nf_conntrack_acct` 와 `nf_conntrack_timestamp` 가 기본으로 꺼져 있어[15], 테이블에서 연결을 찾아도 주고받은 바이트 수와 흐름 시작 시각은 설정을 바꾸지 않았다면 나오지 않습니다.

**Squid 기본 형식에는 클라이언트 포트가 없습니다.** 프록시 앞에 NAT 가 있으면 기본 `squid` 형식만으로는 NAT 뒤의 기기를 구분할 수 없습니다[26].

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| `conntrack -L`, `-L -o extended`, `-L --src-nat`, `-E -o timestamp`[16] | 실행 중인 Linux 라우터·방화벽에서 현재 매핑과 연결 이벤트를 수집합니다 |
| `sysctl net.netfilter.nf_conntrack_acct`, `nf_conntrack_timestamp`[15] | 연결 추적에 양과 시각이 남는 설정인지 확인합니다 |
| `iptables-save`, `nft list ruleset` | NAT 규칙과 LOG 규칙이 어느 체인에 있는지 확인합니다. Linux 쪽 설정 파일 위치는 [방화벽 (Linux)](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/firewall.html) |
| `tcpdump -n -e -ttt -i pflog1`[20] | pflog 인터페이스에 남는 패킷을 실시간으로 읽습니다 |
| nfdump `-A xsrcip,...`, `-s nat`[21] | NSEL·NEL NAT 레코드를 변환 주소로 집계합니다 |
| `zeek-cut id.orig_h id.resp_h local_orig history` | Zeek conn.log 에서 방향과 내부 여부를 뽑습니다 |
| `jq` | EVE 의 `src_ip`·`dest_ip`·`community_id` 를 뽑습니다 |
| `netsh int ipv4 show dynamicport tcp`[9] | Windows 임시 포트 범위를 확인합니다 |

## 참고 문헌

1. Y. Rekhter 외, "Address Allocation for Private Internets", RFC 1918. https://www.rfc-editor.org/rfc/rfc1918.txt
2. J. Weil 외, "IANA-Reserved IPv4 Prefix for Shared Address Space", RFC 6598 (BCP 153). https://www.rfc-editor.org/rfc/rfc6598.txt
3. J. Arkko 외, "IPv4 Address Blocks Reserved for Documentation", RFC 5737. https://www.rfc-editor.org/rfc/rfc5737.txt
4. G. Huston 외, "IPv6 Address Prefix Reserved for Documentation", RFC 3849. https://www.rfc-editor.org/rfc/rfc3849.txt
5. M. Cotton 외, "Special-Purpose IP Address Registries", RFC 6890. https://www.rfc-editor.org/rfc/rfc6890.txt
6. M. Cotton 외, "Internet Assigned Numbers Authority (IANA) Procedures for the Management of the Service Name and Transport Protocol Port Number Registry", RFC 6335. https://www.rfc-editor.org/rfc/rfc6335.txt
7. M. Larsen, F. Gont, "Recommendations for Transport-Protocol Port Randomization", RFC 6056 (BCP 156). https://www.rfc-editor.org/rfc/rfc6056.txt
8. Linux 커널 문서, "IP Sysctl" (ip_local_port_range). https://docs.kernel.org/networking/ip-sysctl.html
9. Microsoft, "The default dynamic port range for TCP/IP has changed" (KB 929851). https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/default-dynamic-port-range-tcpip-chang
10. F. Audet, C. Jennings, "Network Address Translation (NAT) Behavioral Requirements for Unicast UDP", RFC 4787 (BCP 127). https://www.rfc-editor.org/rfc/rfc4787.txt
11. S. Perreault 외, "Common Requirements for Carrier-Grade NATs (CGNs)", RFC 6888 (BCP 127). https://www.rfc-editor.org/rfc/rfc6888.txt
12. A. Durand 외, "Logging Recommendations for Internet-Facing Servers", RFC 6302 (BCP 162). https://www.rfc-editor.org/rfc/rfc6302.txt
13. T. Tsou 외, "Port Management to Reduce Logging in Large-Scale NATs", RFC 7768. https://www.rfc-editor.org/rfc/rfc7768.txt
14. S. Sivakumar, R. Penno, "IP Flow Information Export (IPFIX) Information Elements for Logging NAT Events", RFC 8158. https://www.rfc-editor.org/rfc/rfc8158.txt
15. Linux 커널 문서, "Netfilter Conntrack Sysfs variables". https://docs.kernel.org/networking/nf_conntrack-sysctl.html
16. netfilter 프로젝트, conntrack(8) 매뉴얼. https://conntrack-tools.netfilter.org/conntrack.html
17. iptables-extensions(8) 매뉴얼. https://man7.org/linux/man-pages/man8/iptables-extensions.8.html
18. nftables wiki, "Netfilter hooks". https://wiki.nftables.org/wiki-nftables/index.php/Netfilter_hooks
19. OpenBSD, pf.conf(5) 매뉴얼. https://man.openbsd.org/pf.conf.5
20. OpenBSD, pflog(4) 매뉴얼. https://man.openbsd.org/pflog.4
21. nfdump(1) 매뉴얼 (nfdump 1.7.10). https://github.com/phaag/nfdump/blob/master/man/nfdump.1
22. Zeek, base/protocols/conn/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/conn/main.zeek
23. Suricata 사용자 안내서, "EVE JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
24. Suricata 사용자 안내서, "EVE JSON Output". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
25. AWS, "Flow log records". https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html
26. Squid, src/cf.data.pre (logformat). https://github.com/squid-cache/squid/blob/master/src/cf.data.pre
27. OpenVPN, "Reference manual for OpenVPN 2.6". https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/
28. J. A. Donenfeld, "WireGuard: Next Generation Kernel Network Tunnel" (2.1 Endpoints & Roaming). https://www.wireguard.com/papers/wireguard.pdf
29. Microsoft, "Analyze DHCP Server Log Files" (Windows Server 2008). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/dd183591(v=ws.10)
30. SigmaHQ, zeek_rdp_public_listener.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_rdp_public_listener.yml
31. SigmaHQ, proxy_webdav_external_execution.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/web/proxy_generic/proxy_webdav_external_execution.yml
