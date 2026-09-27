---
title: "DNS 기록"
parent: "Zeek 로그"
grand_parent: "아티팩트 · Zeek"
nav_order: 160
---

# DNS 기록 (dns.log)

Zeek 의 dns.log 는 DNS 질의와 응답을 트랜잭션 ID 로 짝지어 트랜잭션 하나를 한 줄로 남긴 기록이라서, 어느 호스트가 어느 리졸버에 어떤 이름과 유형을 물었고 어떤 응답 코드와 응답 레코드를 받았는지를 연결 uid 와 함께 볼 수 있습니다. 이 페이지는 필드가 채워지는 조건, 줄이 기록되는 시점과 시각, 한 줄로 주장할 수 있는 범위를 다룹니다. Zeek 로그에 공통인 형식(TSV·JSON, 메타 줄, uid)은 [Zeek 로그](index.md) 에서, DNS 메시지 자체의 구조는 [DNS](../../../01-foundations/protocols/dns.md) 에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

Zeek 는 `DNS::ports` 에 등록된 53/udp, 53/tcp, 137/udp, 5353/udp, 5355/udp 에서 DNS 분석기를 돌립니다[4]. 차례로 일반 DNS, NetBIOS 이름 서비스, mDNS, LLMNR 가 쓰는 포트입니다. 137/udp 질의는 NetBIOS 인코딩을 풀어 `query` 에 넣고, 유형이 SRV 로 해석되면 `qtype_name` 을 `NBSTAT` 으로 바꿔 씁니다[4].

한 줄은 DNS 트랜잭션 하나입니다. 같은 연결 안에서 질의를 보면 트랜잭션 ID 로 대기열에 넣고, 같은 ID 의 응답이 오면 둘을 짝지어 줄을 씁니다. 응답을 먼저 보면 거꾸로 응답을 대기열에 넣고 질의를 기다립니다[4]. 끝까지 짝이 없는 질의와 응답은 연결 상태가 지워질 때 한꺼번에 기록되므로, 응답이 없던 질의도 한 줄로 남습니다[4]. 한 트랜잭션 ID 에 짝 없는 메시지가 50개(`DNS::max_pending_msgs`)를 넘거나 짝 없는 트랜잭션 ID 가 50개(`DNS::max_pending_query_ids`)를 넘으면, 쌓인 것을 짝 없이 그대로 씁니다[4].

기록하는 opcode 는 표준 질의(0), 동적 업데이트(RFC 2136), NOTIFY(4) 세 가지입니다[4][9]. 그 밖의 opcode 는 줄을 쓰지 않습니다. NetBIOS 이름 서비스(137/udp)가 아닌 연결에서는 weird `DNS_unknown_opcode` 를 남기고 conn.log 의 history 에 `X` 를 붙입니다[4][6]. 질문 섹션 개수가 25개(`dns_max_queries`)를 넘는 메시지는 DNS 가 아닌 트래픽으로 보고 해석을 멈춥니다[6][8].

## 위치와 버전별 차이

dns.log 는 다른 Zeek 로그와 같은 디렉터리에 생기고, 저장 위치·교대(rotation)·압축은 [Zeek 로그](index.md) 에서 다룹니다. 필드 구성은 Zeek 버전과 로드한 스크립트에 따라 달라집니다.

| 버전 | 바뀐 것 |
|---|---|
| 3.0.0 | DNSSEC 레코드(RRSIG·DNSKEY·DS·NSEC·NSEC3)와 SPF 레코드를 해석하기 시작[9] |
| 6.0.0 | 헤더의 AD·CD 비트를 따로 해석. 로그의 `Z` 는 호환을 위해 두 비트를 그대로 포함[9] |
| 7.1.0 | 처리하지 않는 opcode 에 weird `DNS_unknown_opcode` 를 남김[9] |
| 8.1.0 | 동적 업데이트를 기록. `query` 에 존 이름, `answers` 에 전제 조건과 변경 내용. `opcode`·`opcode_name` 필드 추가[9] |
| 8.2.0 | NOTIFY 메시지 기록. `opcode` 는 4[9] |
| 9.0.0 | 멀티캐스트 목적지(`DNS::multicast_subnets`, 기본 224.0.0.0/4·ff00::/8)로 간 메시지는 짝짓지 않고 메시지마다 한 줄[4][9] |

9.0.0 이전에는 mDNS·LLMNR 의 질의와 응답을 트랜잭션 ID 로 짝지었는데, 이 프로토콜은 응답이 다른 연결로 오기 때문에 서로 관계없는 메시지가 한 줄에 섞였습니다[9]. 그래서 9.0.0 이전 로그의 mDNS·LLMNR 줄은 질의와 응답을 한 사건으로 읽지 않습니다. `redef DNS::multicast_subnets = {};` 로 예전 동작을 되살릴 수 있으므로, 9.0.0 이후 센서라도 이 설정을 확인합니다[9].

기본 로그에 없는 필드는 정책 스크립트를 로드해야 생깁니다. `policy/protocols/dns/auth-addl.zeek` 은 권한 섹션과 추가 섹션의 이름을 `auth`·`addl`(문자열 집합)로 붙이고[2][3], `policy/protocols/dns/log-original-query-case.zeek` 은 대소문자를 바꾸지 않은 질의 이름을 `original_query` 로 붙입니다. `original_query` 는 opcode 0 인 표준 질의에만 채워집니다[7]. 8.1.0 이후 로그에서 `opcode` 필드가 없다면 `policy/protocols/dns/disable-opcode-log-fields.zeek` 을 로드한 설정입니다[9]. 실제 로그의 필드 구성은 TSV 의 `#fields` 줄이나 JSON 키 목록으로 확인합니다.

## 구조

### 한 줄의 모양

다음은 Zeek 문서의 예시 구성을 따라 문서용 주소로 만든 TSV 입니다(만든 예시, Zeek 8.1 이전 필드 구성). 실제 파일은 탭으로 필드를 나눕니다[1].

```text
#fields	ts	uid	id.orig_h	id.orig_p	id.resp_h	id.resp_p	proto	trans_id	rtt	query	qclass	qclass_name	qtype	qtype_name	rcode	rcode_name	AA	TC	RD	RA	Z	answers	TTLs	rejected
#types	time	string	addr	port	addr	port	enum	count	interval	string	count	string	count	string	count	string	bool	bool	bool	bool	count	vector[string]	vector[interval]	bool
1772414415.306059	CwXk3p1Qz8aB2mNd7	192.168.0.20	36844	192.168.0.1	53	udp	8555	-	www.example.com	1	C_INTERNET	28	AAAA	0	NOERROR	F	F	T	F	0	-	-	F
1772414415.305988	CwXk3p1Qz8aB2mNd7	192.168.0.20	36844	192.168.0.1	53	udp	19671	0.066852	www.example.com	1	C_INTERNET	1	A	0	NOERROR	F	F	T	T	0	203.0.113.10	3600.000000	F
```

같은 호스트가 같은 출발지 포트로 A 와 AAAA 를 잇달아 물어서 두 줄의 uid 가 같습니다. conn.log 에는 이 UDP 흐름이 한 줄로만 남습니다[2]. AAAA 응답에는 응답 레코드 없이 권한 섹션 레코드 하나만 들어 있어서 `answers`·`TTLs`·`rtt` 가 비어 있고 `RA` 가 F 입니다. 같은 JSON 줄은 값이 없는 키를 아예 빼고 씁니다(만든 예시)[1][2].

```json
{"ts":1772414415.305988,"uid":"CwXk3p1Qz8aB2mNd7","id.orig_h":"192.168.0.20","id.orig_p":36844,"id.resp_h":"192.168.0.1","id.resp_p":53,"proto":"udp","trans_id":19671,"rtt":0.06685185432434082,"query":"www.example.com","qclass":1,"qclass_name":"C_INTERNET","qtype":1,"qtype_name":"A","rcode":0,"rcode_name":"NOERROR","AA":false,"TC":false,"RD":true,"RA":true,"Z":0,"answers":["203.0.113.10"],"TTLs":[3600.0],"rejected":false}
```

8.1.0 이후에는 줄 끝에 `opcode`·`opcode_name` 이 붙습니다[4][9].

### 필드

필드의 뜻과 값이 채워지는 조건은 다음과 같습니다[3][4][6][10].

| 필드 | 형 | 뜻 | 채워지는 조건 |
|---|---|---|---|
| `ts` | time | 이 트랜잭션의 첫 메시지를 본 시각 | 항상 |
| `uid`·`id.*`·`proto` | string·addr·port·enum | 연결 ID, 4-튜플, 전송 프로토콜(udp·tcp) | 항상 |
| `trans_id` | count | 16비트 트랜잭션 ID | 항상 |
| `rtt` | interval | 질의를 본 때부터 응답 레코드를 처리할 때까지 | 응답에 응답 레코드가 있고 그 값이 0초가 아닐 때 |
| `query` | string | 질의 이름. 소문자로 바꾼 값 | 질의를 봤거나 응답 레코드가 있을 때 |
| `qclass`·`qclass_name` | count·string | 질의 클래스. 예: 1, `C_INTERNET` | 질의를 봤을 때 |
| `qtype`·`qtype_name` | count·string | 질의 유형. 예: 1 `A`, 28 `AAAA`, 16 `TXT`, 255 `*` | 질의를 봤을 때 |
| `rcode`·`rcode_name` | count·string | 응답 코드. 예: 0 `NOERROR`, 3 `NXDOMAIN`, 5 `REFUSED` | 응답을 봤을 때 |
| `AA`·`RA` | bool | 권한 응답 비트, 재귀 가능 비트(기본 F) | 응답에 응답 레코드가 있을 때 응답 헤더에서 |
| `TC`·`RD` | bool | 잘림 비트, 재귀 요청 비트(기본 F) | 질의를 봤을 때 질의 헤더에서 |
| `Z` | count | 헤더의 3비트 예약 필드(기본 0). AD·CD 비트를 포함 | 질의를 봤을 때 질의 헤더에서 |
| `answers` | vector[string] | 응답 레코드를 문자열로 줄인 목록 | 응답 레코드가 있을 때 |
| `TTLs` | vector[interval] | `answers` 각 항목의 TTL, 같은 순서 | `answers` 와 같음 |
| `rejected` | bool | 서버가 질의를 거부했다고 본 경우(기본 F) | 아래 설명 |
| `opcode`·`opcode_name` | count·string | 메시지의 opcode 와 이름(8.1.0+) | 항상 |

질의 이름과 유형은 질의 메시지에서, `AA`·`RA` 는 응답 메시지에서 가져옵니다[4]. 분석기는 헤더 두 번째 16비트에서 `Z` 를 `(flags & 0x0070) >> 4` 로 꺼내므로, AD 비트가 켜지면 2, CD 비트가 켜지면 1 이 `Z` 에 더해집니다[6][9]. 헤더 비트의 배치는 RFC 1035 를 따릅니다[11].

`rejected` 는 두 경우에 T 가 됩니다. 응답의 rcode 가 0 이 아니면서 질문 섹션이 비어 있을 때, 그리고 응답·권한·추가 섹션이 모두 비어 있는 응답을 받았을 때입니다[4][6]. 그래서 NXDOMAIN 이나 REFUSED 응답이라도 권한 섹션에 레코드가 하나 있으면 `rejected` 는 F 입니다. 이름 해석에 실패했는지는 `rcode_name` 으로 판단합니다.

### answers 의 모양

`answers` 는 레코드 전체가 아니라 유형마다 정해진 요약 문자열입니다[4].

| 레코드 유형 | answers 항목 |
|---|---|
| A·AAAA | 주소. 동적 업데이트면 `A 이름 주소`·`AAAA 이름 주소` 모양 |
| CNAME·NS·PTR | 이름 |
| MX | 메일 서버 이름만(우선순위 없음) |
| SRV | 대상 이름만(우선순위·가중치·포트 없음) |
| SOA | 주 서버 이름(mname)만 |
| TXT·SPF | 문자열마다 `TXT 길이 내용`·`SPF 길이 내용`, 여러 개면 공백으로 이음 |
| NAPTR | `NAPTR order preference flags service` 뒤에 regexp·replacement |
| RRSIG·DNSKEY·DS·NSEC | `RRSIG 유형 서명자`, `DNSKEY 알고리즘`, `DS 알고리즘 다이제스트유형`, `NSEC 이름 다음이름` |
| NSEC3·NSEC3PARAM | 유형 이름만 |
| SSHFP | `SSHFP: ` 뒤에 지문 헥스 |
| Zeek 가 해석하지 않는 유형 | `<unknown type=N>` |
| 동적 업데이트 | 전제 조건은 `pre: `, 추가는 `add: `, 삭제는 `del: ` 로 시작 |

## 증거로서 의미

**증명하는 것.** 센서가 본 패킷에서 이 시각에 이 호스트(`id.orig_h`)가 이 서버(`id.resp_h`)에 이 이름과 유형을 물었다는 것, 그리고 센서가 본 응답의 응답 코드·주소·TTL 입니다. uid 로 같은 연결의 conn.log 줄을 찾으면 그 DNS 흐름의 바이트 수와 패킷 수까지 확인됩니다[2]. 보고서에는 "2026-03-02 01:20:15 UTC 에 192.168.0.20 이 192.168.0.1 에 www.example.com 의 A 레코드를 물었고, 센서가 본 응답은 203.0.113.10 이었다"(만든 예시)처럼 기록으로 확인되는 만큼만 씁니다.

**증명하지 못하는 것.** 이름을 물었다고 해서 그 주소에 접속했다는 뜻은 아니어서, 접속 여부는 conn.log 의 `id.resp_h`, http.log 의 `host`, ssl.log 의 `server_name` 으로 따로 확인합니다[14]. 호스트 안의 캐시나 hosts 파일로 해결된 이름은 네트워크에 질의가 나가지 않으므로 dns.log 에 없습니다. dns.log 는 암호화되지 않은 DNS 를 전제로 하므로 DNS over HTTPS(DoH)·DNS over TLS(DoT) 질의는 여기에 나오지 않습니다[2]. 어떤 프로세스나 사용자가 물었는지도 알 수 없습니다. 센서가 내부 리졸버와 외부 사이만 본다면 `id.orig_h` 는 끝단 PC 가 아니라 리졸버입니다([어디서 캡처하나](../../../01-foundations/capture/capture-points.md)).

## 시각 해석

`ts` 는 이 트랜잭션의 첫 메시지를 처리할 때의 네트워크 시각이고, 에포크 초라서 시간대가 없는 UTC 기준 값입니다[4]. 보통은 질의 패킷이 도착한 시각입니다. Zeek 문서의 예시에서 A 질의 패킷 14:39:59.305988 과 AAAA 질의 패킷 14:39:59.306059 가 각 줄의 `ts` 와 같고, conn.log 의 `ts` 는 그 흐름의 첫 dns.log 줄과 같습니다[1][2]. 질의가 캡처되지 않고 응답만 보였다면 `ts` 는 응답을 본 시각입니다[4].

응답 시각은 `ts + rtt` 로 계산합니다. `rtt` 는 응답 레코드를 처리할 때 잰 값이라서 응답 레코드가 없는 응답(NXDOMAIN, 레코드 없는 NOERROR)에는 비어 있고, 그런 줄의 응답 시각은 패킷에서 확인합니다[4]. 위 예시의 A 줄은 `ts` .305988 에 `rtt` 0.066852 를 더해 .372840 이 응답 시각입니다(만든 예시).

줄은 질의와 응답이 모두 보인 순간이나 연결 상태가 지워지는 순간에 기록됩니다[4]. 그래서 파일 안의 줄 순서는 `ts` 순서가 아니라 짝이 맞은 순서입니다. 앞 예시에서 `ts` 가 늦은 AAAA 줄이 먼저 나온 것도 AAAA 응답이 먼저 도착했기 때문입니다[1]. UDP 에서는 DNS 분석기가 `dns_session_timeout`(기본 10초) 동안 패킷이 없는 연결의 상태를 지우고, 짝이 없는 줄은 이때 기록됩니다[4][6][8]. 그래서 로그 파일 교대 경계에서는 질의 시각과 다른 파일에 들어갈 수 있습니다. 연결 상태가 지워지는 일반 규칙은 [연결 기록](conn-log.md) 에서 다룹니다. 파일 머리의 `#open`·`#close` 는 Zeek 가 파일을 열고 닫은 시각이라 트래픽 시각이 아닙니다([Zeek 로그](index.md)). 여러 기록의 시각을 맞추는 일반 원칙은 [네트워크 기록의 시각](../../../01-foundations/records/timestamps.md) 에서 다룹니다.

## 함정과 한계

- **질의 이름은 소문자로 바뀝니다.** 분석기가 질문 이름을 소문자로 바꿔 넘기므로, `wWw.ExAmple.com` 처럼 대소문자를 섞은 질의는 `original_query` 를 켜야 원래 모양이 보입니다[5][6][7].
- **RA=F 가 재귀 불가를 뜻하지 않습니다.** `AA`·`RA` 는 응답 레코드가 있을 때만 응답 헤더에서 채우고, 없으면 기본값 F 로 남습니다[4]. 앞 예시에서 같은 서버의 A 줄은 `RA` 가 T 이고 AAAA 줄은 F 인 것도 이 때문입니다[1].
- **응답이 없어 보이는 줄.** `answers` 가 비어 있고 rcode 가 NOERROR 이면 이름은 있지만 그 유형의 레코드가 없다는 응답일 수 있습니다. auth-addl.zeek 을 로드하면 권한 섹션의 서버 이름이 `auth` 에 나옵니다[2]. 응답 패킷 자체가 없었는지는 `rcode` 가 비어 있는지로 구분합니다[4].
- **answers 는 요약입니다.** MX 우선순위, SRV 포트, SOA 의 일련번호 같은 값은 빠지므로 패킷에서 확인합니다[4]. 문자열 필드는 기본 4096바이트, 목록 필드는 기본 100개(`Log::default_max_field_string_bytes`, `Log::default_max_field_container_elements`)에서 잘리므로 긴 TXT 응답은 뒤가 없을 수 있습니다[8].
- **Z 가 0 이 아니라고 이상한 것은 아닙니다.** DNSSEC 을 쓰는 리졸버가 AD·CD 비트를 켜면 `Z` 가 0 이 아닙니다[9]. Sigma 의 Z 비트 규칙도 DNSSEC 도메인을 오탐 원인으로 적어 둡니다[12].
- **방향.** 연결의 첫 메시지가 응답이면 Zeek 는 연결 방향을 뒤집어 서버가 `id.resp_h` 에 오게 합니다(멀티캐스트 목적지는 뒤집지 않음)[6]. 질의 패킷이 캡처되지 않아도 `id.orig_h` 가 클라이언트인 이유입니다.
- **한 연결에 여러 줄.** 같은 4-튜플로 여러 질의를 보내면 conn.log 한 줄에 dns.log 여러 줄이 대응합니다[2]. dns.log 줄 수를 연결 수로 쓰지 않습니다.
- **값 표기.** TSV 의 `TTLs` 는 `3600.000000`, JSON 은 `3600` 이나 `3600.0` 으로 찍혀 같은 문서 안에서도 두 모양이 다 나옵니다[1][2]. 문자열 비교보다 숫자로 바꿔 비교합니다.
- **버전이 섞인 로그.** 8.1.0 이전 로그에는 `opcode` 필드와 동적 업데이트 줄이 없고, 9.0.0 이전 로그의 mDNS·LLMNR 줄은 관계없는 메시지를 섞은 것입니다[9].
- **보이지 않는 질의.** DoH·DoT 를 쓰는 클라이언트는 dns.log 에 흔적이 없고, ECH 까지 쓰면 ssl.log 의 서버 이름도 비어 있습니다[13]. 이런 흐름은 [암호화된 트래픽 분석](../../../03-techniques/analysis/encrypted-traffic.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번: 질의·응답 메시지와 필드

아래는 앞 예시의 A 질의와 응답을 RFC 1035 명세대로 만든 DNS 페이로드입니다(명세로 만든 예시, UDP 헤더 뒤부터)[11].

```text
질의
00000000: 4cd7 0100 0001 0000 0000 0000 0377 7777  L............www
00000010: 0765 7861 6d70 6c65 0363 6f6d 0000 0100  .example.com....
00000020: 01                                       .

응답
00000000: 4cd7 8180 0001 0001 0000 0000 0377 7777  L............www
00000010: 0765 7861 6d70 6c65 0363 6f6d 0000 0100  .example.com....
00000020: 01c0 0c00 0100 0100 000e 1000 04cb 0071  ...............q
00000030: 0a                                       .
```

0x00 의 `4cd7` 은 트랜잭션 ID 로, 10진수 19671 이 `trans_id` 입니다. 질의의 플래그 `0100` 은 QR 0(질의), opcode 0, RD 1 이라서 `RD` 가 T 이고, 0x04~0x0B 는 질문 1개와 나머지 섹션 0개입니다. 0x0C 부터는 길이가 앞에 붙은 레이블 `03 www`, `07 example`, `03 com`, `00` 이 이어지고 이것이 `query` 가 됩니다. 이어지는 `0001` 두 개가 `qtype` 1(A)과 `qclass` 1(C_INTERNET)입니다.

응답의 플래그 `8180` 은 QR 1, RD 1, RA 1, rcode 0 이라서 `RA` 가 T, `rcode_name` 이 NOERROR 입니다. 0x06 의 `0001` 은 응답 레코드 1개입니다. 0x21 의 `c00c` 는 이름 압축 포인터로 0x0C 의 질문 이름을 가리키고, 0x27 의 `00000e10` 이 TTL 3600초(`TTLs`), 0x2B 의 `0004` 가 데이터 길이, 0x2D 의 `cb00710a` 가 주소 203.0.113.10(`answers`)입니다. 플래그의 Z 자리(0x0070)는 두 메시지 모두 0이라 `Z` 는 0 입니다[6][11].

실제 캡처에서는 `tshark -r trace.pcap -Y dns -x` 로 DNS 패킷의 헥스를 출력해 같은 방법으로 읽습니다[15].

### 공개 도구로 한 번: zeek-cut·jq

TSV 로그는 `zeek-cut` 에 열 이름을 주어 고르고, `-u` 를 붙이면 `ts` 를 UTC 시각으로 바꿔 보여 줍니다[1]. 열 번호로 자르는 awk 는 필드가 추가되면 결과가 틀어지므로 쓰지 않습니다[1].

```bash
zeek-cut -u ts uid id.orig_h id.resp_h query qtype_name rcode_name answers < dns.log | sort
```

JSON 로그는 점이 들어간 키를 따옴표로 감싸 읽습니다[1].

```bash
# 누가 무엇을 물었고 무엇을 받았나
jq -c '[.ts, ."id.orig_h", .query, .qtype_name, .rcode_name, .answers]' dns.log

# 이름 해석에 실패한 이름 순위
jq -r 'select(.rcode_name=="NXDOMAIN") | .query' dns.log | sort | uniq -c | sort -rn | head

# 응답 시각(ts + rtt)을 함께 출력
jq -r 'select(.rtt) | [.ts, (.ts + .rtt), .query] | @tsv' dns.log
```

`answers` 의 주소로 접속이 있었는지는 같은 주소가 conn.log 의 `id.resp_h` 에 나오는지로 확인합니다[14].

```bash
jq -r '.answers[]? | select(test("^[0-9.]+$"))' dns.log | sort -u > resolved.txt
jq -r '."id.resp_h"' conn.log | sort -u | comm -12 resolved.txt -
```

탐지 규칙은 Zeek 의 필드 이름을 그대로 씁니다. SigmaHQ 의 Zeek DNS 규칙은 `query`, `qtype_name`, `answers`, `rejected`, `Z`, `id.resp_p` 를 쓰고[12][14], 일반 DNS 범주 규칙은 `query`, `record_type`, `answer` 를 써서 `qtype_name`·`answers` 와 대응시켜야 합니다[16]. 규칙 적용 방법은 [탐지 규칙 활용](../../../03-techniques/analysis/detection-rules.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 | 페이지 |
|---|---|---|
| 같은 uid 의 conn.log | DNS 흐름의 바이트·패킷 수, TCP DNS 인지, `missed_bytes` 로 캡처 손실 | [연결 기록](conn-log.md) |
| `answers` 주소로 가는 conn.log 줄 | 이름을 물은 뒤 실제로 접속했는지와 그 시각 | [연결 기록](conn-log.md) |
| http.log 의 `host` | 같은 이름으로 평문 HTTP 요청을 보냈는지 | [HTTP 기록](http-log.md) |
| ssl.log 의 `server_name` | 같은 이름으로 TLS 연결을 열었는지 | [TLS·인증서 기록](ssl-x509-log.md) |
| weird.log | `DNS_unknown_opcode` 처럼 기록되지 않은 DNS 메시지의 흔적 | [경고와 이상 기록](notice-weird-log.md) |
| Suricata EVE 의 dns 기록 | 같은 질의를 다른 엔진이 어떻게 기록했는지 | [Suricata EVE 로그](../../suricata/eve-json/index.md) |
| 리졸버의 질의 로그 | 센서가 못 본 질의, 리졸버가 위로 보낸 질의 | [DNS 서버 로그](../../devices/dns-server-logs.md) |
| 호스트의 hosts 파일·DNS 설정 | 네트워크에 나가지 않고 해결된 이름 | [hosts와 DNS 설정 (mac)](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/network/hosts-dns.html) |

질의 이름의 길이·엔트로피·빈도로 이상한 이름을 골라내는 방법은 [DNS 분석](../../../03-techniques/analysis/dns-analysis.md), DNS 로 자료를 내보낸 흔적은 [DNS 로 몰래 보냈나](../../../04-scenarios/exfiltration/dns-tunneling.md) 에서 다룹니다.

## 실습

DNS 트래픽이 들어 있는 공개 캡처 파일(Wireshark 예제 캡처 등)의 사본에 `zeek -C -r 파일.pcap LogAscii::use_json=T` 를 돌린 뒤 아래 질문을 풀어 봅니다[1].

1. uid 별 dns.log 줄 수를 세고 같은 uid 의 conn.log 줄과 비교합니다. 한 연결에 질의가 여럿인 흐름은 어느 것입니까?
2. 파일 순서대로 읽은 `ts` 와 정렬한 `ts` 를 비교해 순서가 바뀐 줄을 찾고, tshark 로 두 응답이 도착한 순서를 확인합니다.
3. `rtt` 가 없는 줄을 골라 `rcode_name` 과 `answers` 를 봅니다. 응답 패킷이 없었던 줄과 레코드 없는 응답이었던 줄을 구분할 수 있습니까?
4. 같은 캡처를 `protocols/dns/auth-addl.zeek` 을 붙여 다시 돌리고 `auth` 필드를 확인합니다. 다시 돌린 로그의 uid 가 처음 것과 같습니까?
5. `answers` 의 주소 가운데 conn.log 에 접속 기록이 없는 주소를 찾습니다. 그 이름은 왜 물었을지 http.log·ssl.log 와 함께 봅니다.

## 참고 문헌

1. Zeek Project, Zeek Documentation — Zeek Log Formats and Inspection. https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
2. Zeek Project, Zeek Documentation — dns.log. https://github.com/zeek/zeek-docs/blob/master/logs/dns.rst
3. Zeek Project, Zeek Documentation — base/protocols/dns/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dns/main.zeek.rst
4. Zeek Project, Zeek 소스 scripts/base/protocols/dns/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/dns/main.zeek
5. Zeek Project, Zeek 소스 src/analyzer/protocol/dns/events.bif. https://github.com/zeek/zeek/blob/master/src/analyzer/protocol/dns/events.bif
6. Zeek Project, Zeek 소스 src/analyzer/protocol/dns/DNS.cc. https://github.com/zeek/zeek/blob/master/src/analyzer/protocol/dns/DNS.cc
7. Zeek Project, Zeek 소스 scripts/policy/protocols/dns/log-original-query-case.zeek. https://github.com/zeek/zeek/blob/master/scripts/policy/protocols/dns/log-original-query-case.zeek
8. Zeek Project, Zeek 소스 scripts/base/init-bare.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/init-bare.zeek
9. Zeek Project, NEWS (3.0.0·6.0.0·7.1.0·8.1.0·8.2.0·9.0.0 절). https://github.com/zeek/zeek/blob/master/NEWS
10. Zeek Project, Zeek Documentation — base/protocols/dns/consts.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dns/consts.zeek.rst
11. P. Mockapetris, RFC 1035 — Domain Names: Implementation and Specification, 1987. https://www.rfc-editor.org/rfc/rfc1035.txt
12. SigmaHQ, zeek_dns_susp_zbit_flag.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_dns_susp_zbit_flag.yml
13. Zeek Project, Zeek Documentation — ssl.log. https://github.com/zeek/zeek-docs/blob/master/logs/ssl.rst
14. SigmaHQ, zeek_dns_mining_pools.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_dns_mining_pools.yml
15. Wireshark Foundation, tshark(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
16. SigmaHQ, net_dns_susp_b64_queries.yml·net_dns_susp_txt_exec_strings.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_susp_b64_queries.yml , https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_susp_txt_exec_strings.yml
