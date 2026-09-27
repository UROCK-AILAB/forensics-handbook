---
title: "네트워크 로그의 종류"
parent: "기반 · 기록 체계"
nav_order: 110
---

# 네트워크 로그의 종류 (Network Log Types)

네트워크 조사에서 만나는 기록은 패킷 캡처, 흐름 기록, Zeek·Suricata 같은 센서 로그, 방화벽·프록시·DNS·DHCP·VPN 장비 로그로 나뉩니다. 종류마다 한 줄이 가리키는 단위(패킷·흐름·연결·요청·임대)와 시각의 기준이 달라서, 줄 수를 서로 비교하거나 시각을 그대로 맞추면 틀린 결론이 나옵니다. 여기서는 종류별로 한 줄의 모양과 읽는 법을 정리하고, 필드 하나하나의 뜻은 각 아티팩트 페이지에서 다룹니다.

## 이 형식을 쓰는 아티팩트

네트워크 기록은 어디서 무엇을 보고 남겼는지에 따라 내용이 정해집니다. 센서는 지나가는 패킷을 보고 연결 단위로 정리하고, 방화벽·프록시·DNS 서버는 자기가 처리한 요청만 남깁니다. 종류별 기록 단위와 시각은 아래 표와 같습니다. 시각의 기준과 시간대는 [네트워크 기록의 시각](timestamps.md)에서 자세히 다룹니다.

| 종류 | 대표 형식·도구 | 한 줄(레코드)의 단위 | 시각 필드 | 자세히 |
|---|---|---|---|---|
| 패킷 캡처 | pcap, pcapng | 패킷 하나 | 패킷 레코드 헤더의 epoch 시각 | [pcap 형식](../capture/pcap.md), [pcapng 형식](../capture/pcapng.md) |
| 흐름 기록 | NetFlow v9, IPFIX, sFlow | 흐름 하나(sFlow 는 표본 하나) | 흐름의 첫·마지막 패킷 | [흐름 기록](flow-records.md) |
| 네트워크 보안 감시 로그 | Zeek conn.log·dns.log·http.log 등 | 연결 하나 또는 트랜잭션 하나 | `ts`, conn.log 는 첫 패킷 시각[2] | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) |
| 침입 탐지 이벤트 | Suricata EVE JSON | 이벤트 하나(alert·flow·http 등) | `timestamp`, 센서 현지 시각과 오프셋[5][22] | [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md) |
| 방화벽 | iptables·nftables LOG, pf 의 pflog | 규칙에 걸린 패킷 하나 | LOG 줄 안에는 없고 커널 로그·syslog 가 붙임, pflog 는 pcap 시각[8][11] | [방화벽 로그](../../02-artifacts/devices/firewall-logs.md) |
| 웹 프록시 | Squid access.log | HTTP 요청 하나 | 기록할 때의 epoch 초·밀리초[13] | [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md) |
| DNS 서버 | BIND 질의 로그, Windows DNS 분석 로그 | 질의 하나 | BIND 는 print-time 설정, Windows 는 이벤트 로그[14][15] | [DNS 서버 로그](../../02-artifacts/devices/dns-server-logs.md) |
| DHCP | Windows DHCP 감사 로그 | 임대 이벤트 하나 | Date, Time[16] | [DHCP 로그](../../02-artifacts/devices/dhcp-logs.md) |
| VPN | OpenVPN 로그·상태 파일, WireGuard | 연결·세션 | 로그 줄 앞 시각, 상태 파일의 Connected Since[17] | [VPN 서버 로그](../../02-artifacts/devices/vpn-logs.md) |
| 로그 전송 | syslog(RFC 5424, RFC 3164) | 메시지 하나 | 보낸 장비가 적은 TIMESTAMP[19][20] | 이 페이지 |

호스트에 남는 네트워크 기록은 다른 핸드북에서 다룹니다. Windows 방화벽의 pfirewall.log 는 [윈도 방화벽](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/windows-firewall-pfirewall-log.html), Linux 의 방화벽 설정은 [Linux 방화벽](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/firewall.html), 클라우드의 흐름 로그는 [AWS VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/aws/vpc-flow-logs.html)·[Azure 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/azure/flow-logs.html)·[GCP VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/gcp/vpc-flow-logs.html)에 있습니다.

## 구조 — 종류별 한 줄의 모양

### 패킷 캡처와 흐름 기록

패킷 캡처는 패킷 바이트를 그대로 담은 바이너리 파일이고, 흐름 기록은 장비가 패킷을 흐름 단위로 묶어 주소·포트·바이트 수·시각만 내보낸 레코드입니다. 두 형식의 구조와 오프셋은 [pcap 형식](../capture/pcap.md), [pcapng 형식](../capture/pcapng.md), [흐름 기록](flow-records.md)에서 다룹니다.

### Zeek 로그

Zeek 는 기본으로 탭으로 구분한 텍스트(TSV)를 씁니다. 파일 머리에 `#` 로 시작하는 줄이 붙어 구분 문자, 빈 값 표시, 로그 이름, 필드 이름과 형식을 알려 주고, 파일을 닫을 때 끝에 `#close` 줄이 붙습니다[1][3].

```
#separator \x09
#set_separator	,
#empty_field	(empty)
#unset_field	-
#path	conn
#open	2026-01-05-09-00-00
#fields	ts	uid	id.orig_h	id.orig_p	id.resp_h	id.resp_p	proto	...
#types	time	string	addr	port	addr	port	enum	...
1767603600.123456	CAbcdEf1234567890	192.168.10.23	51544	203.0.113.80	443	tcp	...
#close	2026-01-05-10-00-00
```

(만든 예시. 머리 줄 모양은 Zeek 기본 TSV 와 같습니다[1].)

`LogAscii::use_json=T` 로 실행하면 한 줄이 JSON 객체 하나가 됩니다[1]. 이때는 머리 줄이 저절로 빠지고, 값이 없는 선택 필드는 키째 빠집니다(`json_include_unset_fields` 기본 F)[3]. JSON 에는 TSV 의 `#types` 같은 형식 정보도 없습니다[1].

로그끼리는 연결 식별자 `uid` 로 이어집니다[2]. 같은 연결의 conn.log 와 http.log 는 `uid` 가 같고, files.log 에는 파일 식별자 `fuid` 와 함께 `uid` 가 들어갑니다[1]. 어떤 로그가 어떤 필드로 켜져 있는지는 설치마다 다릅니다. 기본 로그 말고도 선택 로그와 추가 패키지가 필드를 더하기 때문이고, logschema 패키지로 그 설치의 스키마를 뽑아 확인할 수 있습니다[1]. 필드별 뜻은 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md)에 있습니다.

### Suricata EVE

EVE 는 한 줄에 JSON 객체 하나를 쓰는 형식이고, 모든 이벤트에 공통 머리가 붙은 뒤 `event_type` 이름과 같은 키 아래에 종류별 내용이 들어갑니다[5].

```
{"timestamp":"2026-01-05T18:00:00.123456+0900","flow_id":1234567890123456,"event_type":"flow","src_ip":"192.168.10.23","src_port":51544,"dest_ip":"203.0.113.80","dest_port":443,"proto":"TCP","flow":{"pkts_toserver":12,"pkts_toclient":10,"bytes_toserver":1840,"bytes_toclient":9120,"start":"2026-01-05T17:58:40.001122+0900","end":"2026-01-05T17:59:12.334455+0900","age":32,"state":"closed","reason":"timeout","alerted":false}}
```

(만든 예시)

`flow_id` 는 같은 흐름에서 나온 alert·http·fileinfo·anomaly·flow 이벤트를 하나로 묶는 값입니다[5]. flow 이벤트에는 방향별 패킷·바이트 수, 흐름 시작 `start`, 마지막 패킷 `end`, 지속 시간 `age`, 상태 `state`(new·established·closed·bypassed), 끝난 이유 `reason`(timeout·forced·shutdown), 경보 여부 `alerted` 가 들어갑니다[5]. 흐름을 단방향으로 나눠 쓰는 netflow 이벤트도 있는데, 기본으로 꺼져 있고 켜면 flow 레코드의 두 배가 생깁니다[6]. 이벤트의 `timestamp` 와 흐름의 `start` 가 다른 시각일 수 있다는 점은 [네트워크 기록의 시각](timestamps.md)에서 다룹니다. 필드별 뜻은 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)에 있습니다.

### 방화벽 로그

Linux 의 iptables LOG 대상은 규칙에 걸린 패킷 정보를 커널 로그로 보내고, 이 내용은 dmesg 나 syslog 에서 읽습니다[7]. LOG 는 규칙 평가를 끝내지 않는 대상이라, 차단한 패킷을 남기려면 LOG 규칙 뒤에 DROP 이나 REJECT 규칙을 따로 둡니다[7]. `--log-prefix` 로 붙이는 접두어는 29자까지이고, NFLOG 대상은 패킷을 nfnetlink_log 로 사용자 공간 프로그램에 넘기며 접두어가 64자까지입니다[7]. nftables 의 `log` 문도 평가를 끝내지 않고, `log group` 으로 nfnetlink_log 에 넘기거나 `log level audit` 로 auditd 형식으로 쓸 수 있습니다[9].

커널이 쓰는 LOG 한 줄은 접두어, 들어온·나간 인터페이스, MAC, IP 헤더, 전송 계층 헤더 순서로 이어집니다[8].

```
FW-DROP IN=eth0 OUT= MAC=00:00:5e:00:53:01:00:00:5e:00:53:02:08:00 SRC=203.0.113.25 DST=192.168.10.5 LEN=60 TOS=0x00 PREC=0x00 TTL=52 ID=41234 DF PROTO=TCP SPT=51544 DPT=22 WINDOW=64240 RES=0x00 SYN URGP=0
```

(만든 예시. 필드 순서는 커널이 쓰는 순서와 같습니다[8].)

이 줄 안에는 시각이 없습니다. 시각은 커널 로그나 syslog 가 줄 앞에 붙이므로, 어느 시계로 찍혔는지는 그 로그 수집 설정으로 확인합니다. `--log-uid` 를 준 규칙이면 전송 계층 헤더 뒤에 패킷을 만든 프로세스의 `UID=`·`GID=` 가 붙습니다[7][8].

OpenBSD 의 pf 는 규칙에 `log` 를 달면 상태를 만드는 패킷만 기록하고, `log (all)` 이면 연결의 모든 패킷을 기록합니다[10]. 기록은 pflog0 인터페이스로 가고, pflogd 가 이를 /var/log/pflog 에 tcpdump 바이너리(pcap) 형식으로 저장합니다[10][11]. pflogd 의 기본 snaplen 은 160바이트이고 버퍼는 기본 60초마다 디스크에 씁니다(`-d` 로 5~3600초)[11]. 패킷마다 붙는 pflog 헤더(pfloghdr)에는 주소 체계(af), 동작(action), 이유(reason), 인터페이스 이름(ifname), 규칙 집합(ruleset)과 규칙 번호(rulenr), 방향(dir), rewritten, 주소·포트(saddr·daddr·sport·dport) 필드가 있습니다[12]. 저장한 파일은 `tcpdump -n -e -ttt -r /var/log/pflog` 로 읽습니다[11]. 장비별 세부는 [방화벽 로그](../../02-artifacts/devices/firewall-logs.md)에 있습니다.

### 웹 프록시 로그

Squid 의 access.log 는 기본으로 `squid` 형식을 씁니다[13]. 내장 형식 세 개는 아래와 같습니다[13].

| 이름 | 형식 문자열 |
|---|---|
| squid | `%ts.%03tu %6tr %>a %Ss/%03>Hs %<st %rm %ru %[un %Sh/%<a %mt` |
| common | `%>a - %[un [%tl] "%rm %ru HTTP/%rv" %>Hs %<st %Ss:%Sh` |
| combined | `%>a - %[un [%tl] "%rm %ru HTTP/%rv" %>Hs %<st "%{Referer}>h" "%{User-Agent}>h" %Ss:%Sh` |

`%ts.%03tu` 는 기록할 때의 epoch 초와 밀리초, `%tr` 은 응답 시간(밀리초), `%>a` 는 클라이언트 IP, `%Ss` 는 Squid 처리 결과(TCP_MISS 등), `%>Hs` 는 HTTP 상태 코드, `%<st` 는 응답 바이트, `%rm`·`%ru` 는 메서드와 URL, `%un` 은 사용자 이름, `%Sh` 는 계층 상태(DEFAULT_PARENT 등), `%<a` 는 마지막으로 연결한 서버나 상위 프록시의 IP, `%mt` 는 MIME 형식입니다[13].

```
1767603612.345    245 192.168.10.23 TCP_MISS/200 5120 GET http://www.example.com/index.html - DEFAULT_PARENT/198.51.100.8 text/html
```

(만든 예시)

squid 형식에는 클라이언트 포트(`%>p`)가 없습니다[13]. 프록시 앞에 NAT 가 있으면 클라이언트 IP 만으로는 내부 호스트를 특정하기 어려운데, 이 문제는 [IP 주소·포트·NAT 해석](ip-nat.md)에서 다룹니다. 세부는 [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md)에 있습니다.

### DNS 서버 로그

BIND 는 `queries` 범주를 로깅 설정에 넣으면 querylog 옵션이 따로 없을 때 질의 로그가 켜지고, 실행 중에는 `rndc querylog on`·`off` 로 켜고 끕니다[14]. 한 줄에는 클라이언트 객체 주소, 클라이언트 IP#포트, 질의 이름·클래스·형식, 플래그, 질의를 받은 서버 주소가 들어갑니다[14].

```
client @0x7f00a1b2c3d4 192.168.10.23#53124 (www.example.com): query: www.example.com IN A +E(0)K (192.168.10.2)
```

(만든 예시. 줄 모양은 BIND 질의 로그와 같습니다[14].)

BIND 의 `print-time` 은 기본값이 no 라서 파일 채널에 시각이 찍히지 않습니다. yes 나 local 은 현지 시간대, iso8601 은 현지 시각의 ISO 8601, iso8601-utc 는 UTC 의 ISO 8601 로 찍습니다[14]. syslog 채널로 보내면 syslog 가 시각을 붙입니다[14].

Windows DNS 서버는 감사(Audit) 로그가 기본으로 켜져 있고, 질의·응답을 남기는 분석(Analytical) 로그는 기본으로 꺼져 있습니다[15]. 분석 로그의 기본 파일은 `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-DNSServer%4Analytical.etl` 이고, 이벤트 257(응답 성공)의 본문은 `RESPONSE_SUCCESS: TCP=%1; InterfaceIP=%2; Destination=%3; AA=%4; AD=%5; QNAME=%6; QTYPE=%7; XID=%8; DNSSEC=%9; RCODE=%10; Port=%11; …` 형식입니다[15]. 세부는 [DNS 서버 로그](../../02-artifacts/devices/dns-server-logs.md)에 있습니다.

### DHCP 로그

Windows Server 2008 의 DHCP 감사 로그는 기본으로 `%windir%\System32\Dhcp` 에 쉼표로 구분한 텍스트로 쌓이고, 필드 순서는 `ID, Date, Time, Description, IP Address, Host Name, MAC Address` 입니다[16]. ID 는 이벤트 종류를 뜻하는데, 00 로그 시작, 01 중지, 02 디스크 부족으로 일시 중지, 10 새 임대, 11 갱신, 12 해제, 13 주소가 이미 쓰이는 중, 14 주소 풀 소진, 15 임대 거부, 20 BOOTP 임대, 30~32 DNS 동적 업데이트 요청·실패·성공입니다[16]. Date 와 Time 은 DHCP 서버가 그 줄을 기록한 날짜와 시각인데[16] 시간대 표시가 없어서, 어느 시간대인지는 서버 설정으로 확인합니다. 세부는 [DHCP 로그](../../02-artifacts/devices/dhcp-logs.md)에 있습니다.

### VPN 로그

OpenVPN 2.6 은 `--status file [n]` 으로 n초(기본 60초)마다 상태 파일에 운영 상태를 씁니다[17]. 서버가 여러 클라이언트를 받는 모드에서 `--status-version 1`(기본)은 Common Name, Real Address, Bytes Received, Bytes Sent, Connected Since 를 쉼표로 구분해 쓰고, 2는 여기에 Virtual Address, Virtual IPv6 Address, Username, Client ID, Peer ID, Data Channel Cipher 를 더하며, 3은 2와 같은 내용을 탭으로 구분합니다[17]. 상태 파일은 쓰는 시점의 상태라서 지난 접속은 `--log`·`--log-append` 로 남긴 로그 파일에서 찾고, `--suppress-timestamps` 를 주면 로그 줄 앞에 시각이 붙지 않습니다[17].

WireGuard 는 인증된 패킷의 바깥 출발지 IP·포트로 상대의 끝점(endpoint)을 정하고, 상대가 다른 주소로 옮기면 끝점도 그 주소로 바뀝니다[18]. 세부는 [VPN 서버 로그](../../02-artifacts/devices/vpn-logs.md)에 있습니다.

### syslog 로 옮겨진 로그

방화벽·라우터·VPN 장비는 로그를 syslog 로 중앙 서버에 보내는 경우가 많아서, 조사에서는 장비 로그가 syslog 머리를 쓴 채로 도착합니다. RFC 5424 형식은 `PRI VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MSG` 순서이고 값이 없으면 `-` 를 씁니다[19]. PRI 는 꺾쇠 안의 0~191 숫자이고 Facility 에 8을 곱한 뒤 Severity(0 Emergency ~ 7 Debug)를 더한 값입니다[19].

```
<34>1 2003-10-11T22:14:15.003Z mymachine.example.com su - ID47 - BOM'su root' failed for lonvick on /dev/pts/8
```

(RFC 5424 본문의 예시[19])

옛 BSD syslog(RFC 3164)는 `<PRI>Mmm dd hh:mm:ss HOSTNAME TAG: 내용` 모양이고, 날짜가 한 자리면 공백으로 채워 `Aug  7` 처럼 씁니다[20]. 이 TIMESTAMP 는 현지 시각이고 연도와 시간대가 없습니다[20]. 기본 전송은 UDP 514번이고 패킷은 1024바이트 이하입니다[20].

## 읽는 법

첫 단계로 한 줄이 무엇의 단위인지 확인합니다. pcap 은 패킷, 흐름 기록은 흐름, Zeek conn.log 는 연결, Zeek http.log·Squid 는 HTTP 요청, DNS 서버 로그는 질의, DHCP 로그는 임대 이벤트입니다. 그래서 "방화벽 로그 30줄, 프록시 로그 5줄" 을 비교해 어느 한쪽이 빠졌다고 판단하면 안 되고, 같은 단위로 바꾼 뒤에 비교합니다.

그다음 기록 지점을 확인합니다. 프록시 로그는 프록시를 거친 요청만, DNS 서버 로그는 그 서버에 온 질의만, 방화벽 LOG 는 LOG 규칙에 걸린 패킷만 담습니다[7][14]. pf 는 기본으로 상태를 만든 첫 패킷만 남깁니다[10]. 같은 연결이 NAT 앞뒤에서 다른 주소로 남는 문제는 [IP 주소·포트·NAT 해석](ip-nat.md)과 [어디서 캡처하나](../capture/capture-points.md)에서 다룹니다.

여러 로그를 잇는 열쇠는 도구마다 다릅니다. Zeek 안에서는 `uid`, Suricata 안에서는 `flow_id` 를 씁니다[1][5]. 두 도구를 서로 이을 때는 커뮤니티 ID(Community ID)를 씁니다. Suricata 는 `community-id` 옵션을 켜면 모든 레코드에 `community_id` 필드를 붙이는데, 해시 씨앗값 `community-id-seed`(부호 없는 16비트)가 모든 도구에서 같아야 값이 맞습니다[6]. Zeek 는 `policy/protocols/conn/community-id-logging.zeek` 를 불러와야 conn.log 에 `community_id` 가 생깁니다[21]. 이 값이 없으면 5-튜플(출발지·목적지 IP와 포트, 프로토콜)과 시각 범위로 맞춥니다.

시각은 줄마다 기준이 다릅니다. Zeek 의 `ts` 는 epoch 초이고, Suricata 의 `timestamp` 는 센서 시간대의 현지 시각에 `+0900` 같은 오프셋을 붙인 문자열이며, Squid 의 첫 필드는 기록할 때의 epoch 초입니다[2][13][22]. iptables LOG 와 RFC 3164 syslog 는 시간대 정보가 없습니다[8][20]. 서로 다른 로그를 한 타임라인에 합치는 방법은 [네트워크 기록의 시각](timestamps.md)과 [네트워크 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

탐지 규칙을 로그에 적용할 때는 필드 이름을 옮겨야 합니다. Sigma 는 방화벽 범주에 `src_ip`·`src_port`·`dst_ip`·`dst_port`·`username`, 프록시 범주에 W3C 확장 로그식 이름인 `c-uri`·`c-useragent`·`cs-host`·`cs-method`·`sc-status` 같은 공통 이름을 씁니다[23]. 실제 로그의 필드는 이름이 다르므로 규칙을 돌리기 전에 대응표를 만들어야 합니다. 규칙 활용은 [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md)에서 다룹니다.

## 포렌식에서 중요한 점

**증명하는 것.** 각 로그는 그 장비가 자기 시계로 그 시각에 이 주소·요청·질의를 처리했다는 기록입니다. 프록시 로그로는 이 클라이언트 IP 가 이 URL 을 요청했고 이만큼 받았다는 것을, DNS 서버 로그로는 이 IP 가 이 이름을 물었다는 것을, DHCP 로그로는 이 MAC 주소에 이 IP 를 이 시각에 빌려 줬다는 것을 확인할 수 있습니다[13][14][16]. 보고서에는 "이 시간대에 이 내부 IP 가 이 URL 을 요청한 프록시 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

**증명하지 못하는 것.** 기록이 없다고 통신이 없었던 것은 아닙니다. 프록시를 거치지 않은 연결, 다른 리졸버나 DNS over HTTPS 로 간 질의, LOG 규칙에 걸리지 않은 패킷은 해당 로그에 남지 않습니다. 로그 안의 IP 는 그 장비가 본 주소이지 사람이나 기기가 아니고, 사람을 잇는 데는 DHCP·VPN·인증 기록이 더 필요합니다. syslog 로 온 로그의 HOSTNAME 과 TIMESTAMP 는 보낸 장비가 적은 값이고, 받는 쪽이나 중계 서버는 이 값이 맞는지 검증하지 않아도 됩니다[20].

**꺼져 있어서 없는 기록.** 기본으로 꺼진 로그가 많아서 설정부터 확인합니다. BIND print-time 은 기본 no[14], Windows DNS 분석 로그는 기본으로 꺼져 있고[15], Suricata netflow 이벤트도 기본으로 꺼져 있습니다[6]. 이런 기록이 없다면 사건이 없었던 것이 아니라 켜지 않았던 것일 수 있습니다.

**빠지거나 바뀐 기록.** syslog 는 전달을 보장하는 장치가 없어 UDP 처럼 믿을 수 없는 전송으로 보내면 메시지가 빠질 수 있습니다[19]. 같은 메시지를 다시 보내는 재전송(replay)을 감지하는 장치도 없고, 크기 제한 때문에 뒷부분이 잘릴 수 있습니다[19]. 장비에 남은 원본 로그와 중앙 서버에 모인 사본이 있으면 둘을 비교해 빠진 구간을 찾습니다.

**회전과 보존.** Zeek 는 ZeekControl 로 운영하면 매시간 로그를 회전해 `YYYY-MM-DD` 폴더로 옮기고 gzip 으로 압축하지만, `zeek -i eth0` 처럼 직접 실행하면 회전하지 않습니다[1]. 회전 간격 설정(`Log::default_rotation_interval`)의 기본값은 0초로 회전을 하지 않는다는 뜻이고, ZeekControl 이 이 값을 따로 정합니다[4]. 수집과 보존 절차는 [로그 수집과 보존](../../03-techniques/acquisition/log-collection.md)에 있습니다.

## 함정

**Zeek JSON 에서는 "필드 없음" 과 "값 없음" 을 구분하기 어렵습니다.** JSON 은 값이 없는 선택 필드를 키째 빼기 때문입니다[3]. TSV 는 값이 설정되지 않은 필드를 `-`, 빈 값을 `(empty)` 로 나눠 씁니다[1].

**iptables LOG 접두어는 29자까지입니다[7].** 접두어는 규칙을 만든 사람이 붙인 이름일 뿐이라, 어느 규칙에 걸린 패킷인지는 실제 규칙 목록과 대조해 확인합니다.

**Sigma 명세 안에서도 바이트 필드의 방향이 범주마다 다릅니다.** 프록시 범주는 `cs-bytes` 를 서버가 보낸 바이트, `sc-bytes` 를 클라이언트가 보낸 바이트로 설명하고, 웹 서버 범주는 `sc-bytes` 를 서버가 보낸 바이트, `cs-bytes` 를 서버가 받은 바이트로 설명합니다[23]. 전송량 방향은 실제 로그 형식 문서로 확인합니다.

**줄 순서가 시간순이 아닐 수 있습니다.** Zeek conn.log 는 연결 상태를 지울 때 줄을 쓰므로 파일 안 순서는 연결이 끝난 순서입니다[2]. 오래 걸린 연결은 한참 뒤에 기록됩니다. 파일 수정 시각이나 줄 순서로 사건 순서를 정하지 않고 시각 필드로 정렬합니다.

**같은 연결이라도 로그마다 줄 수가 다릅니다.** Suricata 는 netflow 이벤트를 켜면 흐름 하나가 두 줄이 되고[6], 흐름 기록은 긴 연결을 시간 제한 단위로 여러 레코드로 나눕니다([흐름 기록](flow-records.md) 참고).

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| zeek-cut | Zeek TSV 에서 필드 이름으로 골라 보기. 표준 입력만 받고, `-d` 는 epoch 시각을 사람이 읽는 시각으로, `-u` 는 UTC 로 바꿔 보여 줌[1] |
| jq | Zeek JSON·Suricata EVE 에서 필드 고르기, `flow_id` 로 이벤트 묶기[1][5] |
| logschema | 설치된 Zeek 의 로그·필드 목록 뽑기(`zkg install logschema`)[1] |
| tcpdump | pflog 읽기(`tcpdump -n -e -ttt -r /var/log/pflog`)[11][12] |
| rndc | BIND 질의 로그 켜고 끄기(`rndc querylog on`)[14] |
| nfdump | 흐름 기록 읽기와 집계([흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md)) |

## 참고 문헌

1. Zeek Project, "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
2. Zeek Project, 소스 scripts/base/protocols/conn/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/conn/main.zeek
3. Zeek Project, 소스 scripts/base/frameworks/logging/writers/ascii.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/frameworks/logging/writers/ascii.zeek
4. Zeek Project, "Logging Framework". https://github.com/zeek/zeek-docs/blob/master/frameworks/logging.rst
5. OISF, Suricata 사용자 안내서 "EVE JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
6. OISF, Suricata 사용자 안내서 "EVE JSON Output". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
7. iptables-extensions(8) 매뉴얼. https://man7.org/linux/man-pages/man8/iptables-extensions.8.html
8. Linux 커널 소스 net/netfilter/nf_log_syslog.c. https://github.com/torvalds/linux/blob/master/net/netfilter/nf_log_syslog.c
9. netfilter, nftables(8) 매뉴얼. https://www.netfilter.org/projects/nftables/manpage.html
10. OpenBSD, pf.conf(5) 매뉴얼. https://man.openbsd.org/pf.conf.5
11. OpenBSD, pflogd(8) 매뉴얼. https://man.openbsd.org/pflogd.8
12. OpenBSD, pflog(4) 매뉴얼. https://man.openbsd.org/pflog.4
13. Squid, 설정 설명 파일 src/cf.data.pre(logformat, access_log). https://github.com/squid-cache/squid/blob/master/src/cf.data.pre
14. ISC, BIND 9 Configuration Reference. https://bind9.readthedocs.io/en/stable/reference.html
15. Microsoft, "DNS Logging and Diagnostics". https://learn.microsoft.com/en-us/windows-server/networking/dns/dns-logging-and-diagnostics
16. Microsoft, "Analyze DHCP Server Log Files" (Windows Server 2008). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/dd183591(v=ws.10)
17. OpenVPN, Reference Manual for OpenVPN 2.6. https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/
18. J. A. Donenfeld, "WireGuard: Next Generation Kernel Network Tunnel", §2.1 Endpoints & Roaming. https://www.wireguard.com/papers/wireguard.pdf
19. R. Gerhards, RFC 5424 "The Syslog Protocol", 2009. https://www.rfc-editor.org/rfc/rfc5424.txt
20. C. Lonvick, RFC 3164 "The BSD syslog Protocol", 2001. https://www.rfc-editor.org/rfc/rfc3164.txt
21. Zeek Project, scripts/base/protocols/conn/main.zeek 문서(community_id 필드). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
22. OISF, Suricata 소스 src/util-time.c(CreateIsoTimeString). https://github.com/OISF/suricata/blob/main/src/util-time.c
23. SigmaHQ, Sigma 명세 부록 "Taxonomy". https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-appendix-taxonomy.md
