---
title: "프로토콜 기록"
parent: "Suricata EVE 로그"
grand_parent: "아티팩트 · Suricata"
nav_order: 230
---

# 프로토콜 기록 (dns·http·tls·flow)

Suricata 는 경고가 없어도 자신이 해석한 응용 계층 대화를 EVE 로그에 `event_type` 별로 한 줄씩 남깁니다. DNS 는 요청과 응답마다, HTTP 는 요청·응답 한 쌍마다, TLS 는 세션마다 한 줄이 생기고, 흐름(flow) 기록은 연결이 끝난 뒤 패킷 수·바이트 수·시작과 끝 시각을 한 줄로 정리합니다. 기록마다 방향을 정하는 규칙과 `timestamp` 가 뜻하는 시각이 달라서, 이 차이를 알고 읽어야 타임라인과 주소 해석이 틀어지지 않습니다.

## 무엇을 기록하나 · 왜 생기나

Suricata 의 응용 계층 파서는 대화를 트랜잭션(transaction) 단위로 나누고, 로거는 트랜잭션마다 JSON 한 줄을 씁니다. 모든 줄은 같은 머리 필드(`timestamp`·`flow_id`·`event_type`·주소와 포트·`proto`·`app_proto` 등)로 시작하고, 그 뒤에 종류 이름과 같은 객체(`"dns":{...}`, `"http":{...}`)가 붙습니다[1]. 머리 필드 전체와 `flow_id`·`community_id` 로 기록을 묶는 법, 시각 문자열 형식은 [Suricata EVE 로그](index.md)에 있습니다. 규칙에 걸려 생긴 경고 기록은 [경고 기록 (alert)](alert.md)에, 파일 메타데이터는 [파일 추출 (filestore)](filestore.md)에 있습니다.

기본 설정 파일(suricata.yaml 의 `outputs` → `eve-log` → `types`)에서 이 페이지가 다루는 종류는 아래처럼 켜져 있습니다[3]. 설치본마다 이 절이 다르므로, 실제 센서의 suricata.yaml 에서 `types:` 목록을 먼저 확인합니다.

| event_type | 한 줄이 뜻하는 것 | 기본 설정 |
|---|---|---|
| `dns` | DNS 요청 하나 또는 응답 하나 | 켜짐 |
| `http` | HTTP/1.x 요청·응답 한 쌍 | 켜짐, `extended: yes` |
| `tls` | TLS 세션 하나 | 켜짐, `extended: yes` |
| `flow` | 양방향 흐름 하나(흐름이 끝날 때) | 켜짐 |
| `netflow` | 한 방향 흐름 하나 | 꺼짐(주석 처리) |
| `http2`, `quic`, `ssh`, `smb`, `krb5`, `dhcp`, `ftp` 등 | 프로토콜별 트랜잭션 | 켜짐(`dhcp` 는 `extended: no`) |

## 위치와 버전별 차이

기록은 경고와 같은 `eve.json` 에 섞여 들어가는 것이 기본이지만, EVE 출력을 여러 개 두어 `eve-nsm.json` 처럼 프로토콜 기록만 따로 쓰게 설정할 수도 있습니다[2]. 파일 위치와 회전 설정은 [Suricata EVE 로그](index.md)를 봅니다.

DNS 기록 형식은 버전에 따라 크게 바뀌었습니다. 같은 센서라도 업그레이드 전후 기록을 합치면 두 형식이 섞일 수 있어서, `dns.version` 값부터 확인합니다.

| 항목 | 형식 v2 (Suricata 7.x) | 형식 v3 (Suricata 8.0 기본) |
|---|---|---|
| 요청의 `type` | `query` | `request` |
| 응답의 `type` | `answer` | `response` |
| 질의 이름·유형 | 최상위 `rrname`·`rrtype` | `queries` 배열 |
| 질의가 여러 개인 요청 | 질의마다 기록을 따로 씀 | 한 기록의 `queries` 배열에 모음 |
| 응답 기록의 `src_ip` | 클라이언트 | 응답한 쪽(DNS 서버) |
| alert 안의 `dns` 객체 | `dns.query[]`, `dns.answer{}` 로 따로 | `dns` 기록과 같은 모양 |

8.0 에서도 `version: 2` 로 7.x 형식을 유지할 수 있지만, 이 설정은 Suricata 9 에서 없어질 예정입니다[1][2]. 형식 v1 은 7.0 에서 이미 없어졌습니다[2]. 9.0 에서는 `ike` 기록의 속성이 이름을 키로 쓰는 객체에서 `attributes` 배열(`key`·`value`·`raw`)로 바뀌고, 객체에 `"_v": 2` 가 붙습니다[6].

## 구조

### dns

DNS 기록의 `dns` 객체에는 메시지 종류 `type`, 트랜잭션 ID `id`, 형식 버전 `version`, 16진 문자열 `flags`(앞에 `0x` 없이 `8180` 처럼 씀), 플래그 불리언 `qr`·`aa`·`tc`·`rd`·`ra`·`z`, `opcode`, 응답 코드 `rcode`(`NOERROR`, `NXDOMAIN` 등)가 들어갑니다[1][5]. 질의는 `queries` 배열(`rrname`·`rrtype`)에, 응답 레코드는 `answers`·`authorities`·`additionals` 배열(`rrname`·`rrtype`·`ttl`·`rdata`)에 담깁니다[1]. SOA·SSHFP·SRV 처럼 구조가 있는 레코드는 `soa`(`mname`·`rname`·`serial` 등), `sshfp`(`fingerprint`·`algo`·`type`), `srv`(`target`·`priority`·`weight`·`port`) 객체로 풀어 씁니다[1].

응답을 적는 방식은 `formats` 설정으로 고릅니다. `detailed` 는 응답 레코드마다 배열 항목 하나를 쓰고, `grouped` 는 `"grouped":{"A":[...],"CNAME":[...]}` 처럼 유형별로 값만 모읍니다. `requests`·`responses` 로 요청과 응답 기록을 따로 끌 수 있고, `types` 로 질의 유형을 골라 기록할 수 있습니다[1][2][3].

```json
{"timestamp":"2026-03-02T09:14:05.118204+0900","flow_id":1234567890123456,"event_type":"dns","src_ip":"192.168.10.1","src_port":53,"dest_ip":"192.168.10.23","dest_port":51544,"proto":"UDP","dns":{"version":3,"type":"response","tx_id":1,"id":4711,"flags":"8180","qr":true,"rd":true,"ra":true,"opcode":0,"rcode":"NOERROR","queries":[{"rrname":"www.example.com","rrtype":"A"}],"answers":[{"rrname":"www.example.com","rrtype":"CNAME","ttl":300,"rdata":"example.com"},{"rrname":"example.com","rrtype":"A","ttl":60,"rdata":"203.0.113.10"}]}}
```

위 줄은 v3 응답 기록의 만든 예시입니다. 응답 기록이라서 `src_ip` 가 DNS 서버(192.168.10.1)이고, 질의한 PC 는 `dest_ip` 에 있습니다. v3 에서 UDP 는 그 패킷의 방향을 그대로 쓰고, TCP 는 트랜잭션이 요청인지 응답인지로 방향을 정하는데, 이 TCP 쪽 방향은 틀릴 수 있습니다[8].

LLMNR(224.0.0.252, ff02::1:3, 포트 5355)은 DNS 메시지 형식을 쓰지만 `event_type` 이 `llmnr` 로 따로 기록됩니다. UDP 에서는 질의가 멀티캐스트로 나가고 응답이 유니캐스트로 돌아오므로 요청과 응답이 서로 다른 흐름으로 잡힙니다[1].

### http

HTTP 기록은 트랜잭션(요청·응답 한 쌍)마다 한 줄이고, 머리의 `src_ip` 는 항상 연결을 연 클라이언트입니다[9]. 기본으로 들어가는 필드는 아래와 같습니다[1][9].

| 필드 | 값 |
|---|---|
| `hostname` | 요청의 호스트 이름 |
| `http_port` | 호스트 이름에 포트가 붙어 있을 때만. TCP 목적지 포트와는 관계없음 |
| `url` | 요청 URI |
| `http_user_agent` | User-Agent 헤더 |
| `xff` | X-Forwarded-For 헤더가 있을 때 |
| `http_content_type` | 응답 Content-Type 에서 `;` 앞부분만(`text/html; charset=utf-8` → `text/html`) |
| `content_range` | 응답 Content-Range 헤더(`raw`·`start`·`end`·`size`) |

`extended: yes`(기본 설정 파일의 값)이면 `http_refer`(Referer 헤더, 철자가 `refer` 입니다), `http_method`, `protocol`(`HTTP/1.1`), `status`, `redirect`(응답 Location 헤더), `length` 가 더해집니다. `status` 는 정수로 쓰고, 상태 줄이 숫자가 아니면 `status_string` 에 원문을 씁니다. `length` 는 응답 메시지 본문의 길이입니다[1][9]. extended 기록으로 요청이 POST 였는지, 실행 파일 다운로드가 실제로 바이트를 돌려줬는지 확인할 수 있습니다[1].

`custom` 목록으로 헤더 50여 개(cookie, authorization, origin, server, set-cookie 등)를 더할 수 있고, `dump-all-headers: both|request|response` 이면 `request_headers`·`response_headers` 배열(`name`·`value`)에 헤더 전부가 들어갑니다[1][2]. 본문은 http 기록에 들어가지 않고, 경고 기록에 `http-body` 옵션을 켰을 때만 경고와 함께 Base64 로 남습니다([경고 기록](alert.md)). HTTP/2 는 `http2` 라는 다른 event_type 으로 기록됩니다[3].

```json
{"timestamp":"2026-03-02T09:14:07.402911+0900","flow_id":987654321098765,"event_type":"http","src_ip":"192.168.10.23","src_port":51560,"dest_ip":"198.51.100.20","dest_port":80,"proto":"TCP","tx_id":0,"http":{"hostname":"download.example.net","url":"\/files\/setup.exe","http_user_agent":"Mozilla\/5.0","http_content_type":"application\/octet-stream","http_method":"GET","protocol":"HTTP\/1.1","status":200,"length":482304}}
```

위 줄은 만든 예시입니다. EVE 는 기본 설정(`escape-slash: yes`)에서 `/` 를 `\/` 로 적으므로, 원본 파일을 문자열로 검색할 때는 `\/files\/setup.exe` 처럼 찾거나 jq 로 풀어서 찾습니다[2].

### tls

TLS 기록은 세션마다 한 줄이고[2], 아무 세션이나 기록하지는 않습니다. 서버 인증서의 subject 와 issuer 를 둘 다 읽었거나, 세션 재개(session resumption)이면서 `session-resumption` 설정을 끄지 않았거나, 서버가 TLS 1.3 을 골랐을 때만 기록합니다[10][11]. 서버가 TLS 1.3(초안 버전 포함)을 고르거나 supported_versions 확장으로 1.2 보다 높은 버전을 고르면 인증서 없이도 기록하라는 표시가 켜집니다[11]. TLS 1.3 에서는 ServerHello 뒤의 핸드셰이크 메시지가 모두 암호화되어 인증서를 볼 수 없기 때문입니다[22]. 그래서 TLS 1.2 이하 연결에서 인증서 패킷을 캡처하지 못했고 세션 재개도 아니면 tls 기록이 아예 없고, flow 기록만 남습니다.

| 설정 | 기록되는 필드[1][3][10] |
|---|---|
| 기본 | `subject`, `issuerdn`, `subjectaltname`(배열), `session_resumed` |
| `extended: yes`(기본 설정 파일의 값) | 위 필드 + `serial`, `fingerprint`, `sni`, `version`, `notbefore`, `notafter`, `ja3`, `ja3s`, `ja4`, `client`, `client_alpns`, `server_alpns` |
| `custom: [...]` | 목록에 적은 것만. `certificate`·`chain`(Base64), `client_certificate`, `client_chain`, `client_handshake`, `server_handshake` 는 custom 으로만 켤 수 있음 |

`custom` 을 쓰면 extended 가 꺼집니다[2][3]. 필드 값의 모양은 이렇습니다. `serial` 은 콜론으로 구분한 대문자 16진, `fingerprint` 는 인증서 SHA-1 을 콜론으로 구분한 소문자 16진, `sni` 는 클라이언트가 보낸 Server Name Indication 값입니다. `version` 은 `TLS 1.2` 같은 문자열이고 서버 버전을 모르면 클라이언트 버전을 씁니다[1][10]. `session_resumed` 는 세션을 재개했고 인증서를 보지 못했으며 TLS 1.3 이 아닐 때만 `true` 로 붙습니다[10]. STARTTLS 나 HTTP CONNECT 로 다른 프로토콜에서 TLS 로 바뀐 흐름에는 원래 프로토콜 이름이 `from_proto` 에 들어갑니다[10].

```json
"tls":{"subject":"CN=www.example.com","issuerdn":"C=US, O=Example CA, CN=Example Issuing CA","subjectaltname":["www.example.com","example.com"],"serial":"0A:1B:2C:3D:4E:5F","fingerprint":"3f:2a:91:0c:5b:77:e4:12:9d:08:c6:af:31:5e:02:bb:6d:40:9a:c1","sni":"www.example.com","version":"TLS 1.2","notbefore":"2026-01-05T00:00:00","notafter":"2026-04-05T23:59:59"}
```

```json
"tls":{"sni":"www.example.net","version":"TLS 1.3","client_alpns":["h2","http/1.1"],"server_alpns":["h2"]}
```

두 줄 모두 만든 예시입니다. 첫 줄은 TLS 1.2 세션이라 인증서 정보가 있고, 둘째 줄은 TLS 1.3 세션이라 인증서 필드가 빠져 있습니다.

`ja3`·`ja3s` 는 `hash`·`string` 을 담은 객체이고 `ja4` 는 문자열입니다. 이 값은 `app-layer.protocols.tls.ja3-fingerprints`·`ja4-fingerprints` 를 `yes` 로 켜야 기록되는데, 명시적으로 `no` 로 끄지 않았으면 불러온 규칙이 JA3·JA4 를 쓸 때 저절로 켜집니다. 컴파일할 때 기능을 뺄 수도 있습니다[1][16]. 그래서 같은 센서에서도 규칙 묶음이 바뀌면 이 필드가 있다가 없어질 수 있습니다. 지문 값의 계산과 해석은 [TLS 지문 (JA3·JA4)](../../fingerprints/ja3-ja4.md)에 있습니다.

QUIC 은 `quic` 기록에 `version`, `cyu`(`hash`·`string`), `ja3`, `ja3s`, `ja4` 를 남깁니다[1]. SSH 는 `ssh` 기록의 `client`·`server` 객체에 `proto_version`, `software_version`, `hassh` 를 남깁니다[1].

### flow 와 netflow

flow 기록은 흐름이 끝나면(타임아웃, 강제 종료, 엔진 종료) 한 줄 생깁니다. 머리의 `src_ip` 는 흐름을 연 쪽이고, Suricata 가 흐름 방향을 거꾸로 잡았다고 판단한 흐름은 주소를 바꿔 써서 연 쪽이 `src_ip` 에 오게 합니다[12].

| 필드 | 값[1][12] |
|---|---|
| `pkts_toserver`·`pkts_toclient` | 방향별 패킷 수(우회된 패킷 포함) |
| `bytes_toserver`·`bytes_toclient` | 방향별 바이트 수 |
| `bypassed` | 우회된 패킷·바이트 수(방향별) |
| `start`·`end` | 첫 패킷 시각, 마지막 패킷 시각 |
| `age` | `end` 의 초에서 `start` 의 초를 뺀 정수 |
| `state` | `new`·`established`·`closed`·`bypassed` |
| `bypass` | 우회했으면 `local` 또는 `capture` |
| `reason` | `timeout`·`forced`·`shutdown`·`tcp_reuse`·`unknown` |
| `alerted` | 이 흐름에서 경고가 났는지 |
| `action` | `pass`·`drop`·`accept`(없으면 필드 없음) |
| `tx_cnt` | 응용 계층 트랜잭션 수 |
| `exception_policy` | 적용된 예외 정책(`target`·`policy`) 배열 |
| `emergency`, `elephant`, `wrong_thread` | 해당될 때만 `true`. `elephant` 이면 `elephant_direction` 배열에 방향(`toserver`·`toclient`)이 붙음 |

TCP 흐름에는 `tcp` 객체가 붙습니다. `tcp_flags` 는 양쪽에서 본 TCP 플래그를 OR 한 값이고, `tcp_flags_ts` 는 클라이언트→서버, `tcp_flags_tc` 는 서버→클라이언트 값입니다. 셋 다 두 자리 16진 문자열이고, `tcp_flags` 값은 `syn`·`fin`·`rst`·`psh`·`ack`·`urg`·`ecn`·`cwr` 불리언으로도 씁니다. 그 밖에 TCP 상태 `state`, 스트림에 빈 곳이 있으면 `ts_gap`·`tc_gap` 이 붙습니다[12].

netflow 기록(기본 꺼짐)은 한 흐름을 방향별로 나눠 씁니다. 첫 줄은 클라이언트→서버 방향이고, 응답 패킷을 하나라도 봤을 때만 서버→클라이언트 줄을 하나 더 씁니다. 필드는 `pkts`·`bytes`·`start`·`end`·`age`·`min_ttl`·`max_ttl`·`tx_cnt` 이고, 둘째 줄은 머리의 주소가 뒤집혀 있습니다[13]. 형식 문서의 필드 설명에는 `pkts`·`bytes` 가 "클라이언트로 간" 값이라고 되어 있지만, 소스 코드는 각 줄의 방향에 맞는 값을 씁니다[1][13]. NetFlow·IPFIX 같은 장비 흐름 기록과의 차이는 [흐름 기록](../../../01-foundations/records/flow-records.md)을 봅니다.

### 그 밖의 프로토콜 기록

| event_type | 조사에 쓰는 필드[1][3] |
|---|---|
| `smb` | `command`(예 `SMB2_COMMAND_CREATE`), `status`, `filename`, `share`, `share_type`, `disposition`, `created`·`accessed`·`modified`·`changed`(유닉스 epoch 초), `fuid`, `ntlmssp`(`domain`·`user`·`host`·`version`), `dcerpc` |
| `krb5` | `msg_type`, `cname`, `realm`, `sname`, `encryption`, `weak_encryption`, `ticket_encryption`, `error_code` |
| `dhcp` | 기본은 MAC·IP 대응만(`client_mac`, `assigned_ip`, `dhcp_type`, `client_id` 등), extended 이면 `hostname`, `lease_time`, `routers`, `dns_servers` 등 |
| `ftp` | `command`, `command_data`, `reply`(배열), `completion_code`(배열), `dynamic_port`, `mode` |
| `ftp_data` | `filename`, `command` |

SMB·Kerberos 기록은 Windows 측면 이동 조사에서 호스트 쪽 기록과 맞춰 봅니다. 호스트 쪽 흔적은 [Windows 계정 탈취와 측면 이동](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/credential-theft-lateral-movement/)에 있습니다.

## 증거로서 의미

**증명하는 것**

- `dns`: 그 시각에 그 클라이언트가 그 이름을 질의했고, 센서가 본 응답에 그 값(`rdata`)과 응답 코드가 있었다는 것.
- `http`: 평문 HTTP 요청의 호스트·URI·User-Agent·메서드와, 서버가 돌려준 상태 코드·응답 길이.
- `tls`: 클라이언트가 보낸 SNI, 협상된 버전, TLS 1.2 이하라면 서버 인증서의 subject·issuer·일련번호·유효기간·SHA-1 지문.
- `flow`: 두 끝점 사이에 오간 방향별 패킷 수·바이트 수, 첫 패킷과 마지막 패킷 시각, 흐름이 어떻게 끝났는지.

**증명하지 못하는 것**

- DNS 응답을 받은 PC 가 그 주소로 실제로 연결했는지는 dns 기록만으로 알 수 없습니다. 같은 주소로 가는 flow 기록을 찾아야 합니다. DoH·DoT 로 암호화한 질의는 dns 기록에 없습니다.
- HTTPS 안의 URL·본문은 기록되지 않습니다. http 기록에도 본문은 없습니다.
- SNI 는 클라이언트가 적어 보낸 값이라 실제로 접속한 서버와 다를 수 있습니다. TLS 1.3 세션은 인증서 내용이 없습니다.
- flow 기록의 바이트 수는 무엇을 보냈는지 알려 주지 않습니다. "파일을 보냈다" 가 아니라 "이 시간대에 이 내부 IP 가 이 외부 주소로 이만큼 보낸 흐름이 있다" 까지만 씁니다.
- 기록이 없다고 트래픽이 없었던 것은 아닙니다. 끈 로거, 캡처 손실, 우회(bypass), 재조립 깊이 초과로도 기록이 빠집니다(아래 "함정과 한계").

## 시각 해석

시각 문자열은 센서의 현지 시간대 오프셋이 붙은 `2026-03-02T09:14:05.118204+0900` 형식입니다. 형식과 UTC 로 바꾸는 법은 [Suricata EVE 로그](index.md)와 [네트워크 기록의 시각](../../../01-foundations/records/timestamps.md)에 있습니다. 여기서는 기록 종류마다 `timestamp` 가 무엇을 뜻하는지만 다룹니다.

dns·http·tls 기록의 `timestamp` 는 로거가 그 기록을 쓰게 만든 패킷의 캡처 시각입니다[7]. 트랜잭션이 끝나는 시점의 패킷이므로 요청 패킷이 나간 순간과 조금 다를 가능성이 있습니다. 정확한 순간이 필요하면 pcap 에서 해당 패킷을 찾아 비교합니다.

flow 기록의 `timestamp` 는 흐름의 시각이 아닙니다. 소스는 이 값에 `TimeGet()` 을 쓰는데[12], 실시간 캡처에서는 기록을 쓰는 순간의 센서 시스템 시계이고, pcap 을 읽는 모드에서는 스레드들이 처리 중인 패킷 시각 가운데 가장 이른 값입니다[14]. 문서의 flow 예시에서도 `timestamp` 가 `06:13:21.216460` 인데 `flow.start` 는 `06:13:33.324862` 로 더 늦습니다[1]. 타임라인에는 `flow.start`·`flow.end` 를 쓰고, `timestamp` 는 "기록을 쓴 시각" 정도로만 봅니다. netflow 기록의 `timestamp` 도 같은 방식입니다[13].

실시간 캡처에서 flow 기록은 마지막 패킷보다 한참 뒤에 써질 수 있습니다. 흐름은 마지막 패킷 뒤로 타임아웃만큼 기다렸다가 끝나기 때문입니다. suricata.yaml 설정 예의 타임아웃(초)은 아래와 같고, 흐름 메모리 한도(memcap)에 닿아 비상(emergency) 모드가 되면 더 짧은 값을 씁니다[4].

| 프로토콜 | new | established | closed |
|---|---|---|---|
| tcp | 60 | 3600 | 120 |
| udp | 30 | 300 | — |
| icmp | 30 | 300 | — |
| default(그 밖) | 30 | 300 | — |

TLS 의 `notbefore`·`notafter` 는 인증서에 적힌 유효기간이고, 소수 초와 오프셋 없이 UTC 로 씁니다[15]. `timestamp` 와 형식이 다르므로 합칠 때 오프셋을 따로 붙입니다. SMB 의 `created`·`modified` 등은 파일 시스템 시각을 유닉스 epoch 초 정수로 옮긴 값이라 패킷 시각과 관계없습니다[1].

## 함정과 한계

**DNS 응답의 방향.** v3 응답 기록은 `src_ip` 가 DNS 서버입니다[5]. 7.x 기록과 8.x 기록을 섞어 `src_ip` 로 "질의한 PC" 를 세면 8.x 쪽 응답은 서버 주소로 잡힙니다. 질의한 PC 를 셀 때는 `dns.type` 이 요청인 기록만 쓰거나, 응답 기록은 `dest_ip` 를 씁니다.

**DNS 응답 `type` 값.** v3 필드 설명과 8.0 변경 문서는 응답을 `response` 라고 하지만, 형식 문서의 v3 응답 예시는 `answer` 로 적혀 있습니다[1][5]. 응답 형식 기본값도 형식 문서는 `detailed`, 설정 문서와 설정 파일 주석은 "Default: all" 로 서로 다릅니다[1][2][3]. 실제 데이터에서 `jq -r 'select(.event_type=="dns")|.dns.type' eve.json | sort | uniq -c` 로 값을 먼저 세어 봅니다.

**tls 기록이 없는 TLS 연결.** TLS 1.2 이하 연결에서 인증서 패킷을 놓치면 tls 기록이 생기지 않습니다[10]. 443 포트 flow 기록은 있는데 tls 기록이 없으면, 캡처 손실이나 비대칭 캡처(한 방향만 보이는 탭 위치)일 가능성을 먼저 봅니다.

**필드 이름과 설정 이름이 다름.** tls 의 실제 출력 키는 `issuerdn`·`notbefore`·`notafter` 인데, 형식 문서의 필드 목록은 `issuer` 이고 `custom` 설정 이름은 `issuer`·`not_before`·`not_after` 입니다[1][10]. 검색식은 출력 키로 씁니다. HTTP 의 Referer 는 `http_refer` 입니다.

**`http_port` 와 `dest_port`.** `http_port` 는 Host 헤더에 적힌 포트일 뿐이고, 실제 연결 포트는 머리의 `dest_port` 입니다[9].

**XFF 로 덮어쓴 주소.** `xff` 설정이 `mode: overwrite` 이면 http 기록의 `src_ip`(또는 `dest_ip`)가 패킷 주소가 아니라 X-Forwarded-For 값입니다[3][9]. 프록시 뒤 센서라면 설정부터 확인합니다.

**재조립 깊이.** TCP 스트림은 `stream.reassembly.depth`(기본 1MB)까지만 재조립합니다[4]. 이 깊이를 넘긴 뒤로는 그 HTTP 세션을 더 추적하지 않으므로[18], 오래 이어지는 연결의 뒤쪽 트랜잭션이 http 기록에서 빠질 수 있습니다. flow 기록의 패킷·바이트 수는 계속 셉니다. stats 기록의 `tcp.stream_depth_reached`, `tcp.reassembly_gap` 카운터로 이런 일이 있었는지 확인합니다[17].

**암호화 뒤 우회.** `app-layer.protocols.tls.encryption-handling` 이 `bypass` 이면 핸드셰이크 뒤로 파싱과 검사를 멈추고 흐름을 우회합니다[4]. 이런 흐름은 flow 기록에 `state: bypassed` 와 `bypass` 값이 붙고, 우회한 뒤의 패킷·바이트 수는 방향별 합계에 더해지면서 `bypassed` 객체에도 따로 나옵니다[1][12].

**체크섬 오프로딩.** `stream.checksum-validation: yes` 가 기본이라, 네트워크 카드가 체크섬 계산을 넘겨받은 호스트에서 뜬 캡처는 패킷이 버려진 것처럼 처리되어 앱 계층 기록이 비어 보일 수 있습니다[4]. 이런 캡처를 다시 돌릴 때는 `-k none` 으로 체크섬 검사를 끕니다[19].

## 직접 분석해 보기

**헥스로 한 번 — TCP 플래그 값 풀기.** flow 기록의 `tcp_flags` 는 TCP 헤더 플래그 바이트를 16진 두 자리로 적은 값입니다[12]. 이 바이트의 비트는 위에서부터 CWR(0x80), ECE(0x40), URG(0x20), ACK(0x10), PSH(0x08), RST(0x04), SYN(0x02), FIN(0x01) 입니다[21]. 문서 flow 예시의 값을 명세대로 풀면 아래와 같습니다[1].

| 필드 | 값 | 비트 | 뜻 |
|---|---|---|---|
| `tcp_flags_ts` | `1e` | 0x10+0x08+0x04+0x02 | 클라이언트가 ACK·PSH·RST·SYN 을 보냄 |
| `tcp_flags_tc` | `1a` | 0x10+0x08+0x02 | 서버가 ACK·PSH·SYN 을 보냄, RST 없음 |
| `tcp_flags` | `1e` | 두 값의 OR | 양쪽 합계 |

양쪽 어디에도 FIN(0x01)이 없으므로 이 연결은 FIN 으로 정상 종료하지 않았고, 클라이언트 쪽 RST 로 끊겼다고 해석할 수 있습니다. 서버 쪽 값에 SYN 이 있으면 서버가 SYN-ACK 로 응답했다는 뜻이라, 연결 시도만 하고 응답이 없던 흐름(`tcp_flags_tc` 가 `00`)과 구분됩니다.

**공개 도구로 한 번 — jq.** EVE 는 한 줄이 JSON 하나라 jq 로 바로 읽습니다. 아래는 공식 예시와 같은 방식의 명령입니다[20].

```sh
# 이름 해석에 실패한 질의
jq -c 'select(.event_type=="dns" and .dns.rcode=="NXDOMAIN")|[.timestamp,.dest_ip,.dns.queries[0].rrname]' eve.json

# User-Agent 별 요청 수
jq -r 'select(.event_type=="http")|.http.http_user_agent' eve.json | sort | uniq -c | sort -nr

# SNI 와 TLS 버전 짝
jq -r 'select(.event_type=="tls")|[.tls.sni,.tls.version]|@tsv' eve.json | sort | uniq -c

# 흐름 시각은 flow.start 로, 보낸 바이트 많은 순
jq -r 'select(.event_type=="flow")|[.flow.start,.src_ip,.dest_ip,.dest_port,.flow.bytes_toserver]|@tsv' eve.json | sort -t$'\t' -k5 -nr | head
```

첫 명령은 v3 기준이라 `dest_ip` 에 질의한 PC 가 나옵니다. v2 기록이라면 `.dns.rrname` 과 `src_ip` 로 바꿉니다.

pcap 을 Suricata 로 다시 돌려 기록을 만들 때는 원본이 아니라 사본에 `suricata -r 사본.pcap -l 출력폴더 -k none` 처럼 실행합니다. `-r` 에 폴더를 주면 수정 시각 순서로 파일을 모두 처리하면서 흐름 상태를 이어 갑니다[19]. 이렇게 만든 기록의 `flow_id` 는 원래 센서 기록과 다르므로, 두 기록을 잇는 방법은 [Suricata EVE 로그](index.md)를 봅니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 | 링크 |
|---|---|---|
| 같은 `flow_id` 의 alert·fileinfo | 이 흐름에서 규칙 일치·파일 전송이 있었는지 | [경고 기록](alert.md), [파일 추출](filestore.md) |
| Zeek 의 dns·http·ssl·conn 로그 | `community_id` 가 같은 줄의 필드 값 | [Zeek 로그](../../zeek/zeek-logs/index.md) |
| DNS 서버 로그 | 센서가 본 응답과 서버가 준 응답이 같은지 | [DNS 서버 로그](../../devices/dns-server-logs.md) |
| 프록시 로그 | HTTPS 안의 URL(프록시가 풀어 본 경우) | [웹 프록시 로그](../../devices/proxy-logs.md) |
| DHCP 로그·dhcp 기록 | 그 시각 내부 IP 를 쓴 기기(MAC) | [DHCP 로그](../../devices/dhcp-logs.md) |
| 원본 pcap | `pcap_cnt` 로 찾은 패킷의 실제 바이트 | [pcap 형식](../../../01-foundations/capture/pcap.md) |

프로토콜 자체의 동작은 [DNS](../../../01-foundations/protocols/dns.md), [HTTP](../../../01-foundations/protocols/http.md), [TLS와 인증서](../../../01-foundations/protocols/tls.md)에 있고, 이 기록들로 조사하는 절차는 [DNS 분석](../../../03-techniques/analysis/dns-analysis.md), [네트워크 타임라인](../../../03-techniques/analysis/timeline.md), [DNS 로 몰래 보냈나](../../../04-scenarios/exfiltration/dns-tunneling.md)에 있습니다.

## 실습

Wireshark 예제 캡처처럼 공개된 캡처 파일의 사본에 Suricata 를 돌린 뒤 아래 질문을 풀어 봅니다.

1. `jq -r .event_type eve.json | sort | uniq -c` 로 종류별 줄 수를 세고, flow 기록 수와 dns·http·tls 기록 수를 비교합니다. 앱 계층 기록이 없는 흐름은 무엇입니까?
2. dns 응답 기록 하나를 골라 `src_ip` 가 서버인지 클라이언트인지 확인하고, 같은 `flow_id` 의 요청 기록과 비교합니다.
3. flow 기록마다 `timestamp` 와 `flow.start` 의 차이를 계산합니다. `timestamp` 가 `start` 보다 이른 기록이 있습니까?
4. 443 포트 흐름 가운데 tls 기록이 없는 것을 찾고, `tcp_flags_tc` 값을 풀어 서버가 응답했는지 확인합니다.
5. http 기록의 `length` 와 같은 흐름의 `flow.bytes_toclient` 를 비교합니다. flow 쪽이 얼마나 더 큰지 보고, 같은 `flow_id` 에 http 기록이 여러 개 있는지도 확인합니다.

## 참고 문헌

1. OISF, Suricata User Guide — Eve JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
2. OISF, Suricata User Guide — Eve JSON Output. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
3. OISF, Suricata 기본 설정 eve-log 부분(partials/eve-log.yaml). https://github.com/OISF/suricata/blob/main/doc/userguide/partials/eve-log.yaml
4. OISF, Suricata User Guide — Suricata.yaml. https://github.com/OISF/suricata/blob/main/doc/userguide/configuration/suricata-yaml.rst
5. OISF, Suricata User Guide — DNS EVE Logging Changes for 8.0. https://github.com/OISF/suricata/blob/main/doc/userguide/upgrade/8.0-dns-logging-changes.rst
6. OISF, Suricata User Guide — Suricata 9.0 Logging Changes. https://github.com/OISF/suricata/blob/main/doc/userguide/upgrade/9.0-logging-changes.rst
7. OISF, Suricata 소스 src/output-json.c. https://github.com/OISF/suricata/blob/main/src/output-json.c
8. OISF, Suricata 소스 src/output-json-dns.c. https://github.com/OISF/suricata/blob/main/src/output-json-dns.c
9. OISF, Suricata 소스 src/output-json-http.c. https://github.com/OISF/suricata/blob/main/src/output-json-http.c
10. OISF, Suricata 소스 src/output-json-tls.c. https://github.com/OISF/suricata/blob/main/src/output-json-tls.c
11. OISF, Suricata 소스 src/app-layer-ssl.c. https://github.com/OISF/suricata/blob/main/src/app-layer-ssl.c
12. OISF, Suricata 소스 src/output-json-flow.c. https://github.com/OISF/suricata/blob/main/src/output-json-flow.c
13. OISF, Suricata 소스 src/output-json-netflow.c. https://github.com/OISF/suricata/blob/main/src/output-json-netflow.c
14. OISF, Suricata 소스 src/util-time.c. https://github.com/OISF/suricata/blob/main/src/util-time.c
15. OISF, Suricata 소스 rust/src/x509/log.rs. https://github.com/OISF/suricata/blob/main/rust/src/x509/log.rs
16. OISF, Suricata User Guide — JA3/JA4 Keywords. https://github.com/OISF/suricata/blob/main/doc/userguide/rules/ja-keywords.rst
17. OISF, Suricata User Guide — Statistics. https://github.com/OISF/suricata/blob/main/doc/userguide/performance/statistics.rst
18. OISF, Suricata User Guide — File Extraction. https://github.com/OISF/suricata/blob/main/doc/userguide/file-extraction/file-extraction.rst
19. OISF, Suricata User Guide — Command Line Options(partials/options.rst). https://github.com/OISF/suricata/blob/main/doc/userguide/partials/options.rst
20. OISF, Suricata User Guide — Eve JSON 'jq' Examples. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-examplesjq.rst
21. W. Eddy, Ed., "Transmission Control Protocol (TCP)", RFC 9293, 2022. https://www.rfc-editor.org/rfc/rfc9293.txt
22. E. Rescorla, "The Transport Layer Security (TLS) Protocol Version 1.3", RFC 8446, 2018. https://www.rfc-editor.org/rfc/rfc8446.txt
