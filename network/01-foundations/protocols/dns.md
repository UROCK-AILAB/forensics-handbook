---
title: "DNS"
parent: "기반 · 프로토콜 기초"
nav_order: 50
---

# DNS

DNS 는 이름을 IP 주소로 바꿔 주는 프로토콜이라서, 어느 내부 주소가 언제 어떤 이름을 물었고 어떤 답을 받았는지가 네트워크 조사에서 가장 먼저 보는 기록이 됩니다. 메시지는 12바이트 헤더 뒤에 질문과 자원 레코드가 이어지는 단순한 구조라서 캡처에서 바이트를 직접 따라가기 쉽고, Zeek·Suricata 로그의 필드도 이 헤더 비트를 거의 그대로 옮겨 적습니다. 대신 캐시에서 답을 꺼낸 조회, hosts 파일로 끝난 조회, DNS over TLS·DNS over HTTPS 로 암호화된 조회는 평문 DNS 기록에 남지 않습니다.

## 이 형식을 쓰는 아티팩트

평문 DNS 메시지는 패킷 캡처(pcap·pcapng)에 그대로 들어 있고, Zeek 는 이를 해석해 `dns.log` 를, Suricata 는 EVE 로그의 `dns` 이벤트를 남깁니다[4][7]. 두 로그의 공통 필드와 파일 구조는 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md)와 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)에서 다루고, 이 페이지는 DNS 에 딸린 필드만 설명합니다. 해석기 (resolver) 와 권한 서버가 직접 남기는 기록, 곧 BIND 쿼리 로그와 Windows DNS 서버의 분석 로그는 [DNS 서버 로그](../../02-artifacts/devices/dns-server-logs.md)에 있습니다.

흐름 기록(NetFlow·IPFIX)에는 DNS 메시지 내용이 없고, UDP·TCP 53 번 포트로 오간 바이트와 패킷 수만 남습니다. 흐름 기록의 구조는 [흐름 기록](../records/flow-records.md)에 있습니다. 탐지 규칙도 DNS 필드를 그대로 씁니다. Sigma 의 일반 `dns` 범주 규칙은 `query`, `record_type`, `answer` 필드를 쓰고, Zeek 용 규칙은 `query`, `qtype_name`, `answers`, `Z`, `id.resp_p` 같은 dns.log 필드 이름을 씁니다[11][13][14]. 규칙을 쓰는 방법은 [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md)에 있습니다.

호스트에 남는 이름 해석 설정과 hosts 파일은 운영체제별 핸드북에서 다룹니다. Windows 는 [hosts 파일](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/hosts.html), macOS 는 [hosts와 DNS 설정](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/network/hosts-dns.html), Linux 는 [이름 해석](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/name-resolution.html)을 봅니다.

## 구조 — 표와 오프셋

DNS 메시지는 헤더, 질문(Question), 답(Answer), 권한(Authority), 추가(Additional) 다섯 부분으로 이뤄집니다. 답·권한·추가 부분은 모두 같은 자원 레코드 (Resource Record, RR) 형식을 쓰고, 각 부분에 레코드가 몇 개 있는지는 헤더의 개수 필드가 정합니다[1]. 숫자 필드는 모두 네트워크 바이트 순서(빅 엔디언)입니다.

### 헤더 (12바이트)

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 2 | ID | 질의를 만든 프로그램이 정하는 16비트 값. 응답에 그대로 복사되어 질의와 응답의 짝을 맞추는 데 씁니다 |
| 2 | 2 | 플래그 | QR·Opcode·AA·TC·RD·RA·Z·RCODE (아래 표) |
| 4 | 2 | QDCOUNT | 질문 개수 |
| 6 | 2 | ANCOUNT | 답 부분의 레코드 개수 |
| 8 | 2 | NSCOUNT | 권한 부분의 네임 서버 레코드 개수 |
| 10 | 2 | ARCOUNT | 추가 부분의 레코드 개수 |

플래그 2바이트는 가장 높은 비트부터 아래 순서로 나뉩니다[1].

| 비트 | 필드 | 값과 뜻 |
|---|---|---|
| 15 | QR | 0 이면 질의, 1 이면 응답 |
| 14–11 | Opcode | 0 표준 질의(QUERY), 1 역질의(IQUERY), 2 서버 상태(STATUS), 3–15 예약. 질의한 쪽이 정하고 응답에 복사됩니다 |
| 10 | AA | 응답한 서버가 질문한 이름의 권한 서버라는 표시. 응답에서만 뜻이 있습니다 |
| 9 | TC | 전송 경로의 허용 길이를 넘어 메시지가 잘렸다는 표시 |
| 8 | RD | 재귀 조회를 원한다는 표시. 질의에 넣으면 응답에 복사됩니다 |
| 7 | RA | 응답한 서버가 재귀 조회를 지원한다는 표시 |
| 6–4 | Z | 예약. 모든 질의와 응답에서 0 이어야 합니다 |
| 3–0 | RCODE | 응답 코드(아래 표) |

RCODE 값은 다음과 같습니다[1].

| RCODE | 이름 | 뜻 |
|---|---|---|
| 0 | 오류 없음 | 정상 응답 |
| 1 | Format error | 서버가 질의를 해석하지 못함 |
| 2 | Server failure | 서버 문제로 처리하지 못함 |
| 3 | Name Error | 질의한 이름이 없음. 권한 서버의 응답에서만 뜻이 있습니다 |
| 4 | Not Implemented | 그 종류의 질의를 지원하지 않음 |
| 5 | Refused | 정책 때문에 거부(예: 특정 요청자에게 답하지 않거나 존 전송을 거부) |
| 6–15 | 예약 | — |

Zeek 는 3 을 `NXDOMAIN`, 5 를 `REFUSED` 라는 이름으로 `rcode_name` 필드에 적습니다[15].

### 질문 부분

질문 하나는 QNAME, QTYPE(2바이트), QCLASS(2바이트)로 이뤄집니다. QNAME 은 "길이 1바이트 + 그 길이만큼의 라벨" 을 되풀이하다가 길이 0 바이트로 끝나고, 길이가 홀수여도 채움 바이트를 넣지 않습니다[1]. 그래서 `www.example.com` 은 `03 77 77 77 07 65 78 61 6D 70 6C 65 03 63 6F 6D 00` 17바이트가 됩니다. 라벨 하나는 63바이트, 이름 전체는 255바이트를 넘을 수 없습니다[1].

### 자원 레코드

자원 레코드 하나는 아래 순서로 이어집니다[1].

| 순서 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 1 | 가변 | NAME | 이 레코드가 설명하는 이름 |
| 2 | 2 | TYPE | 레코드 종류(아래 표) |
| 3 | 2 | CLASS | 1 이면 인터넷(IN) |
| 4 | 4 | TTL | 이 레코드를 캐시에 둬도 되는 시간(초). 0 이면 이번 조회에만 쓰고 캐시하지 않습니다 |
| 5 | 2 | RDLENGTH | RDATA 길이(바이트) |
| 6 | 가변 | RDATA | 레코드 내용. TYPE 이 A, CLASS 가 IN 이면 4바이트 IPv4 주소 |

조사에서 자주 만나는 TYPE 값은 A 1, NS 2, CNAME 5, SOA 6, PTR 12, MX 15, TXT 16 이고, 질문에만 쓰는 QTYPE 으로는 존 전체를 달라는 AXFR 252 와 모든 레코드를 달라는 `*` 255 가 있습니다[1]. IPv6 주소 레코드 AAAA 는 28 이고, Zeek 로그에서는 `"qtype":28,"qtype_name":"AAAA"` 로 나옵니다[4].

### 이름 압축

같은 이름이 메시지 안에 여러 번 나오면, 뒤에 나오는 이름을 앞의 이름을 가리키는 2바이트 포인터로 바꿀 수 있습니다. 포인터는 첫 두 비트가 `11` 이고 나머지 14비트가 오프셋인데, 이 오프셋은 메시지 시작(ID 의 첫 바이트)부터 셉니다[1]. 라벨 길이는 63 이하라서 첫 두 비트가 늘 `00` 이므로 포인터와 헷갈리지 않습니다. 응답의 답 레코드 NAME 자리에 흔히 나오는 `C0 0C` 는 "오프셋 12 의 이름", 곧 헤더 바로 뒤 질문의 QNAME 을 가리킵니다.

### 전송 방식

| 방식 | 포트 | 메시지 앞 길이 필드 | 근거 |
|---|---|---|---|
| UDP | 53 | 없음. 원 명세는 512바이트까지이고, 넘으면 잘라서 TC 를 켭니다 | [1] |
| TCP | 53 | 2바이트 길이(길이 필드 자신은 빼고 셉니다) | [1] |
| DNS over TLS (DoT) | TCP 853 | TLS 안에서도 TCP 와 같은 2바이트 길이 | [2] |
| DNS over HTTPS (DoH) | HTTPS | 없음. HTTP 본문이 곧 DNS 메시지 | [3] |

UDP 는 존 전송 (zone transfer) 에 쓸 수 없습니다[1]. 512바이트 제한은 뒤에 RFC 6891(EDNS)이 고쳤고, DoH 의 `application/dns-message` 형식은 메시지 크기를 65535바이트까지로 둡니다[3].

DoT 는 기본으로 TCP 853 을 쓰고, 853 에서는 평문 DNS 를 주고받으면 안 됩니다(MUST NOT). 서로 합의하면 다른 포트를 쓸 수 있지만 53 은 쓰지 않습니다[2]. DoH 서버는 GET 과 POST 를 모두 구현해야 합니다(MUST). GET 은 DNS 메시지를 base64url 로 인코딩해 URL 변수 `dns` 에 넣고 채움 문자 `=` 를 붙이지 않으며, POST 는 메시지를 본문에 넣고 `content-type` 을 `application/dns-message` 로 둡니다[3]. HTTP 캐시가 같은 질의를 한 번에 처리하도록 DoH 클라이언트는 ID 를 0 으로 두는 것이 좋습니다(SHOULD). 권장하는 최소 HTTP 버전은 HTTP/2 입니다[3].

## 읽는 법

캡처에서 DNS 를 읽을 때는 먼저 헤더의 QR 비트로 질의와 응답을 나누고, ID 와 양쪽 주소·포트가 같은 질의·응답을 한 쌍으로 묶습니다. 그다음 응답의 RCODE 로 성공 여부를 보고, ANCOUNT 만큼 답 레코드를 읽어 TYPE·TTL·RDATA 를 꺼냅니다. UDP 는 질의와 응답이 사라지거나 순서가 바뀔 수 있어서, 해석기는 응답이 순서대로 온다고 가정하지 말아야 합니다[1]. 분석할 때도 같은 이유로 패킷 순서가 아니라 ID 로 짝을 맞춥니다.

### 헥스로 따라가기 (명세로 만든 예시)

아래는 RFC 1035 형식대로 만든 질의와 응답입니다. UDP 헤더 뒤의 DNS 메시지만 보입니다.

```
질의 (33바이트)
0000    1A 2B 01 00 00 01 00 00 00 00 00 00 03 77 77 77
0010    07 65 78 61 6D 70 6C 65 03 63 6F 6D 00 00 01 00
0020    01

응답 (49바이트)
0000    1A 2B 81 80 00 01 00 01 00 00 00 00 03 77 77 77
0010    07 65 78 61 6D 70 6C 65 03 63 6F 6D 00 00 01 00
0020    01 C0 0C 00 01 00 01 00 00 0E 10 00 04 C6 33 64
0030    0A
```

- 0x00 `1A 2B`: ID 0x1A2B(6699)입니다. 응답에도 같은 값이 있어서 두 메시지가 한 쌍입니다.
- 질의 0x02 `01 00`: RD 만 켜진 표준 질의입니다.
- 응답 0x02 `81 80`: 2진수 `1000 0001 1000 0000` 이라서 QR=1(응답), Opcode=0, AA=0, TC=0, RD=1, RA=1, Z=0, RCODE=0(오류 없음)입니다.
- 0x04–0x0B: 질의는 QDCOUNT 1, 나머지 0 이고, 응답은 QDCOUNT 1, ANCOUNT 1 입니다.
- 0x0C–0x1C: QNAME `www.example.com` 입니다.
- 0x1D `00 01` / 0x1F `00 01`: QTYPE A, QCLASS IN 입니다.
- 응답 0x21 `C0 0C`: 압축 포인터이고, 오프셋 12 의 `www.example.com` 을 가리킵니다.
- 응답 0x23 `00 01` / 0x25 `00 01`: TYPE A, CLASS IN 입니다.
- 응답 0x27 `00 00 0E 10`: TTL 3600초입니다.
- 응답 0x2B `00 04`: RDLENGTH 4바이트입니다.
- 응답 0x2D `C6 33 64 0A`: 198.51.100.10 입니다.

DoH 의 GET 요청에 들어 있는 `dns` 값도 같은 메시지입니다. RFC 8484 의 예시 `/dns-query?dns=AAABAAABAAAAAAAAA3d3dwdleGFtcGxlA2NvbQAAAQAB` 를 base64url 로 풀면 `00 00 01 00 00 01 00 …` 으로 시작하는 33바이트가 나오는데, 위 질의와 비교하면 ID 만 0 이고 나머지는 같습니다[3].

### Zeek dns.log

Zeek 는 질의와 그 응답을 묶어 dns.log 한 줄로 적습니다[4]. 아래는 위 헥스와 같은 교환을 dns.log JSON 으로 옮긴 것입니다(만든 예시).

```
{"ts":1767225600.123456,"uid":"CAbCdE1fGhIjKlMn01","id.orig_h":"10.1.2.30","id.orig_p":51514,"id.resp_h":"10.1.2.1","id.resp_p":53,"proto":"udp","trans_id":6699,"rtt":0.021,"query":"www.example.com","qclass":1,"qclass_name":"C_INTERNET","qtype":1,"qtype_name":"A","rcode":0,"rcode_name":"NOERROR","AA":false,"TC":false,"RD":true,"RA":true,"Z":0,"answers":["198.51.100.10"],"TTLs":[3600.0],"rejected":false}
```

각 필드의 뜻은 다음과 같습니다[5].

| 필드 | 뜻 |
|---|---|
| `ts` | 이 연결에서 DNS 메시지를 처음 본 시각 |
| `uid`, `id.*`, `proto` | 연결 식별자와 4-튜플, 전송 프로토콜. conn.log 와 같은 uid 로 이어집니다 |
| `trans_id` | 헤더의 16비트 ID |
| `rtt` | 요청을 본 때부터 응답이 시작될 때까지의 시간 |
| `query`, `qclass`/`qclass_name`, `qtype`/`qtype_name` | 질문 부분 |
| `rcode`/`rcode_name` | 응답 코드 |
| `AA`, `TC`, `RD`, `RA` | 헤더 플래그. 기본값 거짓 |
| `Z` | 3비트 예약 필드. DNSSEC 를 쓰지 않으면 0, 기본값 0 |
| `answers`, `TTLs` | 답 레코드 내용과 각각의 캐시 시간 |
| `rejected` | 서버가 질의를 거절했는지 |

`auth-addl.zeek` 를 로드하면 권한 부분과 추가 부분의 내용이 `auth`·`addl` 필드에 더 남고, `log-original-query-case.zeek` 를 로드하면 질의 이름의 원래 대소문자가 `original_query` 필드에 남습니다[5]. TSV 형식에서는 `TTLs` 의 형식이 `vector[interval]` 이라서 `3600.000000` 처럼 적히고, 값이 없으면 `-` 가 들어갑니다[6].

같은 출발지·목적지 주소와 포트로 오간 UDP 패킷은 Zeek 가 연결 하나로 묶습니다. 그래서 한 호스트가 같은 출발지 포트로 A 와 AAAA 를 연달아 물으면 dns.log 에는 두 줄, conn.log 에는 같은 uid 로 한 줄이 생기고, conn.log 의 `ts` 는 두 dns.log 줄 가운데 더 이른 시각과 같습니다[4]. conn.log 필드는 [TCP 연결과 흐름](tcp-sessions.md)에서 다룹니다.

### Suricata EVE dns

Suricata 는 요청과 응답을 따로 한 줄씩 적고, 기본으로 둘 다 기록합니다[8]. 설정의 `types` 로 기록할 레코드 종류를 줄일 수 있고, 지정하지 않으면 모두 기록합니다[7]. 아래는 버전 3 형식의 `dns` 객체만 옮긴 것입니다(만든 예시).

```
"dns": {"version":3,"type":"request","id":6699,"queries":[{"rrname":"www.example.com","rrtype":"A"}]}
"dns": {"version":3,"type":"answer","id":6699,"flags":"8180","qr":true,"rd":true,"ra":true,"rcode":"NOERROR","queries":[{"rrname":"www.example.com","rrtype":"A"}],"answers":[{"rrname":"www.example.com","rrtype":"A","ttl":3600,"rdata":"198.51.100.10"}]}
```

`flags` 는 헤더 플래그 2바이트를 `0x` 없이 16진수로 적은 값이고, `qr`·`aa`·`tc`·`rd`·`ra`·`z` 는 각 비트가 켜졌는지를 참·거짓으로 적습니다[7]. 답 목록은 `answers`, 권한 부분은 `authorities`, 추가 부분은 `additionals` 에 들어갑니다. SOA·SSHFP·SRV 레코드는 `soa`, `sshfp`, `srv` 객체로 세부 필드가 따로 나옵니다[7]. 답을 적는 형식에는 답마다 `rrname`·`rrtype`·`ttl`·`rdata` 를 적는 detailed 와 레코드 종류별로 묶어 `grouped` 객체에 적는 grouped 두 가지가 있고, 함께 쓸 수도 있습니다[7].

로그 형식 버전은 Suricata 버전에 따라 다릅니다[7][8].

| Suricata | DNS 로그 형식 |
|---|---|
| 7.0 | 버전 1 형식 제거, 버전 2 사용 |
| 8.0.0 | 버전 3 도입·기본값. `dns` 이벤트와 `alert` 의 `dns` 객체 형식이 같아집니다. `version: 2` 로 7.0 형식을 유지할 수 있습니다 |
| 9 (예정) | 버전 2 형식 제거 |

한 파일 안에서 버전이 섞였는지는 각 줄의 `dns.version` 값으로 확인합니다.

### Wireshark·tshark

Wireshark 는 질의 패킷에 `dns.response_in`(응답이 있는 프레임 번호), 응답 패킷에 `dns.response_to`(질의가 있는 프레임 번호)를 붙여 짝을 보여 줍니다. 2.6.0 부터는 같은 질의·응답이 다시 보내졌으면 `dns.retransmission`, 짝이 되는 질의가 없는 응답이면 `dns.unsolicited` 가 붙습니다[9]. 자주 쓰는 필드는 `dns.id`, `dns.flags.response`, `dns.flags.rcode`, `dns.flags.truncated`, `dns.qry.name`, `dns.qry.type`, `dns.resp.ttl`, `dns.a`, `dns.aaaa`, `dns.cname`, `dns.txt` 입니다[9].

```
tshark -r 사건.pcap -Y dns -T fields -e frame.time_epoch -e ip.src -e ip.dst -e dns.id -e dns.flags.response -e dns.qry.name -e dns.flags.rcode -e dns.a
tshark -r 사건.pcap -q -z dns,tree
```

`-T fields` 와 `-e` 로 필요한 필드만 뽑고, `-z dns,tree` 로 qtype·qclass 분포와 qname 길이의 최댓값·최솟값·평균을 봅니다[10]. 분석 절차는 [DNS 분석](../../03-techniques/analysis/dns-analysis.md)과 [Wireshark·tshark로 읽기](../../03-techniques/analysis/wireshark.md)에 있습니다.

## 포렌식에서 중요한 점

### 증명하는 것

질의와 응답이 한 쌍으로 남아 있으면 "이 시각에 이 내부 주소가 이 해석기에 이 이름을 물었고, 이런 답을 받았다" 까지 말할 수 있습니다[1][4]. RCODE 3(NXDOMAIN)이 돌아왔다면 그 이름이 그 시점에 없었다는 답을 받았다는 뜻이고, 답에 CNAME 이 이어져 있으면 요청한 이름이 어떤 이름을 거쳐 어느 주소로 풀렸는지도 알 수 있습니다. 답의 IP 로 곧이어 연결한 기록이 conn.log 나 흐름 기록에 있으면, 그 연결이 어떤 이름을 보고 간 것인지 이어 붙일 근거가 됩니다. 예를 들어 한 캡처에서는 A 레코드 질의 뒤 약 0.12초, 답이 온 뒤 약 0.06초 만에 답으로 받은 주소의 80번 포트로 HTTP 연결이 시작됩니다[6].

### 증명하지 못하는 것

DNS 기록은 이름을 물었다는 사실까지만 보여 줍니다. 받은 IP 로 실제 접속했는지는 conn.log·흐름 기록·방화벽 로그로 따로 확인해야 하고, 사람이 주소를 입력했는지 프로그램이 스스로 물었는지도 DNS 기록만으로는 구분할 수 없습니다. 헤더와 질문 부분에는 질의를 만든 프로그램을 알려 주는 필드가 없습니다[1].

캡처 위치에 따라 출발지도 달라집니다. 내부 해석기가 재귀 조회를 대신하는 구조에서 해석기 바깥에서 캡처하면, 외부 서버로 나가는 질의의 출발지는 모두 해석기 주소입니다. 어느 클라이언트가 물었는지는 해석기 안쪽 캡처나 [DNS 서버 로그](../../02-artifacts/devices/dns-server-logs.md)로 확인합니다. 캡처 위치별 차이는 [어디서 캡처하나](../capture/capture-points.md)에 있습니다.

질의가 없다고 접속이 없었던 것도 아닙니다. 답은 TTL 동안 클라이언트와 해석기의 캐시에 남아서 다시 물을 필요가 없고[1], hosts 파일로 풀린 이름이나 IP 로 바로 접속한 경우에는 질의 자체가 생기지 않습니다. DoT·DoH 로 보낸 질의는 평문 DNS 로 보이지 않아서 Zeek 도 dns.log 를 만들지 않습니다[4]. 이때는 853 번 포트 연결이나 DoH 서버로 가는 HTTPS 연결만 보이고, 무엇을 볼 수 있는지는 [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md)에서 다룹니다.

### 시각 해석

Zeek dns.log 의 `ts` 는 그 연결에서 DNS 메시지를 처음 본 시각이고, `rtt` 는 요청을 본 때부터 응답이 시작될 때까지의 간격입니다[5]. 한 파일 안에서도 줄 순서가 `ts` 순서와 다를 수 있습니다. 예를 들어 한 연결에서 A 질의(`ts` 1591367999.305988)와 AAAA 질의(`ts` 1591367999.306059)를 연달아 보내면, dns.log 에 AAAA 줄이 A 줄보다 먼저 적힐 수 있습니다[4][6]. 그래서 시간순으로 비교하기 전에 `ts` 로 정렬합니다. TTL 은 시각이 아니라 캐시에 둘 수 있는 초 단위 길이입니다[1]. 각 로그의 시각이 UTC 인지, 기록 시각과 패킷 시각이 어떻게 다른지는 [네트워크 기록의 시각](../records/timestamps.md)에서 다룹니다.

### 기록이 빠지거나 짝이 안 맞는 경우

Zeek 는 한 트랜잭션 ID 에 짝을 못 찾은 질의나 응답이 50개 쌓이거나, 짝 없는 메시지가 남은 ID 가 50개가 되면 짝 맞추기를 그만둡니다(`DNS::max_pending_msgs`, `DNS::max_pending_query_ids`, 기본값 둘 다 50)[5]. 이런 상황은 서버나 해석기가 고장 났거나, Zeek 가 DNS 트래픽 일부만 보거나, AXFR 응답이 이어지는 중일 때 생깁니다[5]. 비대칭 경로 때문에 응답만 캡처되거나 질의만 캡처된 구간이 있으면 짝 없는 줄이 몰려서 나오므로, 먼저 캡처 범위를 확인합니다.

UDP 질의는 사라질 수 있어서 클라이언트가 다시 보냅니다[1]. 같은 이름의 질의가 짧은 간격으로 여러 번 보이면 사용자가 여러 번 접속했다고 읽기 전에 재전송인지(Wireshark 의 `dns.retransmission`)부터 확인합니다[9].

흐름 기록만 있을 때는 DNS 질의 하나가 흐름 하나가 되는지가 출발지 포트에 달려 있습니다. Ellens 외(2013)가 약 300명이 쓰는 대학 하위망에서 IPFIX 흐름 기록(활성 제한 60초, 비활성 제한 15초)으로 DNS 터널을 시험했을 때, 요청마다 새 출발지 포트를 쓰는 로컬 해석기(bind)를 거치면 터널 흐름이 정상 DNS 흐름과 같은 모양이 되었고, 같은 포트를 계속 쓰는 경우에는 여러 요청이 큰 흐름 하나로 묶였습니다[12]. 흐름 기록으로 DNS 터널을 찾는 방법은 [DNS 로 몰래 보냈나](../../04-scenarios/exfiltration/dns-tunneling.md)에 있습니다.

## 함정

**AAAA 줄에 답이 없다고 이름이 없는 것은 아닙니다.** AAAA 질의에 답 0개, 권한 레코드 1개인 응답이 오면, dns.log 의 그 줄은 `rcode` 가 `NOERROR` 인데 `answers`·`TTLs`·`rtt` 가 없습니다. `auth-addl.zeek` 를 로드하면 이 줄에 권한 서버 이름이 `auth` 필드로 나옵니다[4][6]. 이름은 있지만 그 종류의 레코드가 없다는 뜻이므로, NXDOMAIN(RCODE 3)과 구분합니다.

**Zeek 와 Suricata 는 같은 비트를 다르게 적습니다.** Zeek 는 플래그 필드를 대문자 `AA`·`TC`·`RD`·`RA` 로 적고 `Z` 는 3비트 정수입니다. Suricata 는 소문자 `aa`·`tc`·`rd`·`ra`·`z` 이고 `z` 는 참·거짓입니다[5][7]. Suricata 의 `id` 와 Zeek 의 `trans_id` 가 같은 헤더 ID 입니다. 두 로그를 합칠 때 필드 이름을 맞춰 두지 않으면 조건 검색이 빠집니다.

**Suricata 문서 안에서도 설명이 엇갈립니다.** 필드 목록은 `type` 값을 `request` 또는 `response` 라고 하지만 버전 3 응답 예시는 `"type": "answer"` 입니다[7]. 답 형식의 기본값도 형식 설명 절은 detailed 라고 하고, 설정 예시의 주석은 `formats` 의 기본값을 "all" 이라고 적었습니다[7][8]. 실제 파일에서 응답 줄의 `type` 값과 `answers`·`grouped` 가 어떻게 나오는지 먼저 확인하고 검색 조건을 만듭니다.

**TTL 의 부호는 RFC 1035 안에서도 다르게 적혀 있습니다.** 레코드 형식 절(3.2.1)은 부호 있는 32비트, 메시지 형식 절(4.1.3)은 부호 없는 32비트라고 하고, 크기 제한 절(2.3.4)은 "부호 있는 32비트의 양수 값" 이라고 합니다[1]. 가장 높은 비트가 켜진 TTL 은 도구마다 아주 큰 양수나 음수로 다르게 표시할 가능성이 있으므로 헥스 값을 함께 적어 둡니다.

**Z 비트가 0 이 아닌 질의는 먼저 의심하되 DNSSEC 를 확인합니다.** RFC 1035 는 Z 가 늘 0 이어야 한다고 했고[1], Zeek 는 DNSSEC 를 쓰지 않으면 0 이라고 설명합니다[5]. Sigma 에는 Zeek dns.log 에서 Z 가 0 이 아닌 질의를 찾는 규칙이 있는데, `.arpa`·`.local` 같은 이름과 NetBIOS 포트(137–139)를 빼고, DNSSEC 를 쓰는 도메인을 오탐으로 적었습니다[11].

**DoH 질의가 URL 에 남을 수 있습니다.** GET 방식 DoH 는 DNS 메시지를 base64url 로 인코딩해 URL 의 `dns` 변수에 넣습니다[3]. TLS 를 풀어 보는 프록시 로그나 복호화한 캡처에서 `dns=` 가 붙은 URL 을 만나면, 채움 문자 `=` 를 붙여 base64url 로 풀어 위 헥스 표대로 읽으면 질의한 이름이 나옵니다. 프록시 로그 형식은 [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md)에 있습니다.

**TC 가 켜진 응답은 뒤따르는 TCP 연결과 함께 봅니다.** UDP 응답이 길어서 잘리면 TC 가 켜지고[1], 전체 답은 같은 서버의 TCP 53 연결에 있을 수 있습니다. UDP 응답에 든 답만 보고 답 목록이 끝났다고 판단하지 않습니다.

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| Zeek | 질의·응답을 묶은 dns.log. `auth-addl.zeek`, `log-original-query-case.zeek` 로 필드 추가[5] |
| Suricata | EVE 로그의 `dns` 이벤트. 요청·응답을 따로 기록, detailed·grouped 형식[7][8] |
| Wireshark·tshark | 패킷 단위 확인, `dns.response_in`·`dns.response_to` 로 짝 확인, `-z dns,tree` 통계[9][10] |
| Sigma | dns 범주와 Zeek dns.log 필드를 쓰는 탐지 규칙[11][13][14] |

## 참고 문헌

1. P. Mockapetris, 「Domain Names - Implementation and Specification」, RFC 1035, 1987. https://www.rfc-editor.org/rfc/rfc1035.txt
2. Z. Hu, L. Zhu, J. Heidemann, A. Mankin, D. Wessels, P. Hoffman, 「Specification for DNS over Transport Layer Security (TLS)」, RFC 7858, 2016. https://www.rfc-editor.org/rfc/rfc7858.txt
3. P. Hoffman, P. McManus, 「DNS Queries over HTTPS (DoH)」, RFC 8484, 2018. https://www.rfc-editor.org/rfc/rfc8484.txt
4. Zeek 문서, dns.log. https://github.com/zeek/zeek-docs/blob/master/logs/dns.rst
5. Zeek 문서, base/protocols/dns/main.zeek (DNS::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dns/main.zeek.rst
6. Zeek 문서, Zeek Log Formats and Inspection. https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
7. Suricata 사용자 안내서, EVE JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
8. Suricata 사용자 안내서, EVE JSON Output. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
9. Wireshark, Display Filter Reference: Domain Name System. https://www.wireshark.org/docs/dfref/d/dns.html
10. Wireshark, tshark 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
11. SigmaHQ, zeek_dns_susp_zbit_flag.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_dns_susp_zbit_flag.yml
12. Wendy Ellens, Piotr Żuraniewski, Anna Sperotto, Harm Schotanus, Michel Mandjes, Erik Meeuwissen, 「Flow-Based Detection of DNS Tunnels」, Lecture Notes in Computer Science 7943 (AIMS 2013), 2013. doi:10.1007/978-3-642-38998-6_16
13. SigmaHQ, net_dns_susp_b64_queries.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_susp_b64_queries.yml
14. SigmaHQ, net_dns_susp_txt_exec_strings.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_susp_txt_exec_strings.yml
15. Zeek 문서, base/protocols/dns/consts.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dns/consts.zeek.rst
