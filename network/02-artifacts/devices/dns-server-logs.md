---
title: "DNS 서버 로그"
parent: "아티팩트 · 네트워크 장비와 서버 로그"
nav_order: 270
---

# DNS 서버 로그 (BIND·Windows DNS)

DNS 서버 로그는 이름 해석을 맡은 서버가 자기가 받은 질의와 보낸 응답, 설정 변경을 남긴 기록이라서, 어느 내부 주소가 언제 어떤 이름을 물었는지를 패킷 캡처가 없는 곳에서도 확인할 수 있게 해 줍니다. 이 페이지는 BIND 9 의 로깅 채널과 쿼리 로그, Windows DNS 서버의 감사·분석 이벤트와 디버그 로그(dns.log)를 다루고, 기본 설정에서 무엇이 빠지는지와 한 줄로 주장할 수 있는 범위를 정리합니다. DNS 메시지 자체의 구조는 [DNS](../../01-foundations/protocols/dns.md) 에서, 패킷에서 만든 질의·응답 기록은 [Zeek dns.log](../zeek/zeek-logs/dns-log.md) 에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

사내 PC 와 서버는 보통 조직이 운영하는 DNS 서버에 이름을 묻고, 그 서버가 캐시에 없는 이름을 상위 서버에 대신 물어 답을 돌려줍니다. 서버 로그는 운영자가 장애를 찾고 설정 변경을 추적하려고 켜 두는 기록이라서, 무엇이 남는지는 설정에 달려 있습니다.

BIND 9 는 로그를 채널 (channel) 과 범주 (category) 로 나눕니다. 채널은 파일·syslog·표준 오류·버림(null) 가운데 어디로 보낼지를 정하고, 범주는 쿼리·존 전송·동적 업데이트·보안처럼 메시지의 종류를 정합니다[1]. 조사에서 가장 자주 찾는 쿼리 로그는 `queries` 범주이고, 질의 하나마다 한 줄을 남기지만 응답 내용은 남기지 않습니다[1].

Windows DNS 서버는 기록이 세 가지입니다. 감사 이벤트 (Audit) 는 서버·존·레코드 설정이 바뀔 때마다 남고 기본으로 켜져 있습니다. 분석 이벤트 (Analytical) 는 서버가 DNS 정보를 주고받을 때마다 남고 기본으로 꺼져 있습니다. 디버그 로그 (dns.log) 는 분석 이벤트가 나오기 전부터 쓰던 텍스트 파일 방식이고, 모든 옵션이 기본으로 꺼져 있습니다[3].

## 위치와 버전별 차이

### BIND 9

BIND 의 로그 파일 경로는 정해진 기본값이 없고 `named.conf` 의 `logging { }` 블록에 적힌 채널 정의를 따릅니다. 따로 정의가 없으면 모든 범주가 `default` 범주를 따라 `default_syslog`(syslog 의 daemon 시설, info 이상)와 `default_debug` 로 갑니다[1]. `default_debug` 는 서버의 디버그 수준이 0 이 아닐 때만 서버 작업 디렉터리의 `named.run` 에 씁니다. 작업 디렉터리는 `options` 의 `directory` 값이고, 지정하지 않으면 named 를 시작한 디렉터리입니다[1]. named 를 `-L 파일` 로 시작하면 `default_logfile` 채널이 더해져 `default` 범주가 syslog 대신 그 파일로 갑니다[1].

그래서 BIND 서버에서는 먼저 `named.conf` 와 그 파일이 포함하는 설정에서 `channel`·`category`·`querylog` 줄을 찾고, 파일 채널이면 적힌 경로와 백업 파일을, syslog 채널이면 syslog 가 저장하는 위치를 수집합니다. 수집 순서와 보존 방법은 [로그 수집과 보존](../../03-techniques/acquisition/log-collection.md) 에서 다룹니다.

쿼리 로그가 켜지는 조건은 두 가지입니다. `options` 의 `querylog yes;` 가 있으면 시작할 때 켜지고, 이 옵션이 없으면 `queries` 범주를 설정에 적었는지로 정해집니다. 실행 중에는 `rndc querylog on|off` 로 바꿀 수 있고, `rndc reconfig`·`rndc reload` 는 이 옵션에 영향을 주지 않습니다[1]. BIND 9.20 참조 문서에는 응답 코드를 남기는 `responselog` 옵션과 `responses` 범주도 있고, 실행 중 `rndc responselog on|off` 로 바꿉니다[1].

BIND 의 권장 로깅 설정은 파일 채널마다 `print-time yes; print-category yes; print-severity yes;` 를 켜고 범주별로 파일을 나눕니다. 쿼리 로그는 `querylog no;` 로 두었다가 필요할 때 `rndc querylog` 로 켜고, 쿼리 로그 채널은 `versions 600 size 20m` 입니다[2]. 쿼리 로깅은 부하가 큰 서버에서 성능 비용이 클 수 있어서[1], 조사하는 서버에서 쿼리 로그가 꺼져 있었을 가능성부터 확인합니다.

패킷 수준 기록이 필요하면 dnstap 을 씁니다. BIND 를 `--enable-dnstap` 으로 빌드해야 쓸 수 있고, `dnstap { }` 에 client·auth·resolver·forwarder·update 가운데 남길 종류를 적으며 종류마다 query 나 response 만 고를 수 있습니다(지정하지 않으면 둘 다). 출력은 `dnstap-output file|unix 경로` 로 정하고 `dnstap-read` 로 읽습니다[1]. 쿼리 로그와 달리 응답 메시지까지 남길 수 있습니다.

### Windows DNS 서버

| 기록 | 기본 상태 | 위치 | 버전 |
|---|---|---|---|
| 감사 이벤트 (Audit) | 켜짐 | 이벤트 뷰어 Applications and Services Logs > Microsoft > Windows > DNS-Server > Audit | Windows Server 2016 부터 기본 포함, 2012 R2 는 핫픽스 KB2956577 설치 시[3][4] |
| 분석 이벤트 (Analytical) | 꺼짐 | 같은 위치의 Analytical("Show Analytic and Debug Logs" 를 켜야 보임), 파일은 `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-DNSServer%4Analytical.etl` | 위와 같음[3][4] |
| 디버그 로그 (dns.log) | 모든 옵션 꺼짐 | 기본 `%windir%\System32\Dns\dns.log`, 파일 이름 옵션으로 바꿀 수 있음(`temp\dns.log` 로 적으면 `%windir%\Temp`) | Windows Server 2003 문서에 같은 옵션이 있음[3][5] |
| DNS Server 이벤트 로그 | — | 탐지 규칙에서 `service: dns-server` 로 부르는 로그(존 전송 실패 6004, 서버 플러그인 DLL 관련 150·770·771)[6][7] | — |

분석 로그를 켜면 최신 하드웨어에서 초당 10만 질의(QPS)를 받는 서버는 성능이 5% 떨어질 수 있고, 5만 QPS 이하에서는 눈에 띄는 영향이 없습니다[3][4]. 분석 로그를 켤 때 "Do not overwrite events" 를 고르면 이벤트 뷰어에서 바로 조회할 수 있고, "Overwrite as needed" 로 순환 기록을 고르면 오류 창이 뜨지만 기록은 계속되며 지금 기록 중인 이벤트를 이벤트 뷰어로 볼 수 없습니다[3]. 분석·감사 이벤트는 ETW 공급자 `{EB79061A-A566-4698-9119-3ED2807060E7}` 로도 받을 수 있어서, 운영자가 `tracelog.exe` 로 따로 .etl 파일을 만들어 두었을 수도 있습니다[3].

디버그 로그의 설정은 PowerShell `Get-DnsServerDiagnostics` 로 확인합니다. 기본값은 `Queries`·`Answers`·`SendPackets`·`ReceivePackets`·`FullPackets` 등이 모두 `False`, `EnableLogFileRollover` 가 `False`, `MaxMBFileSize` 가 `500000000` 입니다[3].

## 구조

### BIND 쿼리 로그 한 줄

쿼리 로그 한 줄은 클라이언트 객체 식별자(`@0x` 뒤 16진수), 클라이언트 IP 와 포트, 괄호 안의 질의 이름, `query:` 뒤의 이름·클래스·유형, 플래그, 괄호 안의 목적지 주소 순서입니다. 질의에 CLIENT-SUBNET 옵션이 있으면 끝에 `[ECS 주소/source/scope]` 가 붙습니다[1]. 줄 앞에는 채널 설정에 따라 시각·범주·심각도가 이 순서로 붙습니다[1].

```
27-Sep-2026 10:15:02.118 queries: info: client @0x7f0a1c00d2a0 192.168.10.23#50112 (www.example.com): query: www.example.com IN A +E(0)K (192.168.10.2)
27-Sep-2026 10:15:04.530 queries: info: client @0x7f0a1c00e110 192.168.10.41#61022 (example.net): query: example.net IN TXT -E(0)TD (192.168.10.2)
```

위 두 줄은 `print-time yes; print-category yes; print-severity yes;` 로 둔 파일 채널을 가정해 형식대로 만든 예시입니다(만든 예시). 목적지 주소는 질의가 도착한 이 서버의 주소라서, 주소가 여러 개인 서버에서는 어느 인터페이스로 들어왔는지 알 수 있습니다.

| 플래그 | 뜻[1] |
|---|---|
| `+` / `-` | 재귀 요청 (RD, Recursion Desired) 비트가 켜짐 / 꺼짐 |
| `S` | 서명된 질의 |
| `E(#)` | EDNS 사용, 괄호 안은 EDNS 버전 |
| `T` | TCP 로 받음 |
| `D` | DO(DNSSEC OK) 비트 |
| `C` | CD(Checking Disabled) 비트 |
| `V` | 유효한 서버 쿠키를 받음 |
| `K` | 유효한 서버 쿠키 없이 쿠키 옵션만 있음 |

같은 질의에 관련된 뒤따르는 메시지에는 클라이언트 주소·포트와 질의 이름 부분이 되풀이됩니다[1]. 그래서 쿼리 로그 줄과 오류 줄을 이 앞부분으로 이어 볼 수 있습니다.

### BIND 의 그 밖의 범주

`query-errors` 범주는 쿼리 로깅이 켜져 있거나 디버그 수준이 1 이상이면 SERVFAIL 응답을 `client 192.168.10.23#50112: query failed (SERVFAIL) for bad.example.net/IN/A at query.c:3880` 모양으로 남깁니다(값은 만든 예시). `at` 뒤는 SERVFAIL 을 정한 소스 파일과 줄 번호입니다. 디버그 수준 2 이상이면 SERVFAIL 로 끝난 재귀 해석이 몇 초 걸렸고 어떤 결과로 끝났는지를 `fetch completed at resolver.c:…` 로 시작하는 줄에 더 자세히 남깁니다[1].

조사에 자주 쓰는 범주는 요청 승인·거부를 남기는 `security`, 동적 업데이트의 `update`·`update-security`, 존 전송의 `xfer-in`·`xfer-out`, 응답 속도 제한의 `rate-limit`, 응답 정책 존의 `rpz` 입니다[1]. BIND 가 syslog 로 남기는 `denied AXFR from`(존 전송 거부), `dropping source port zero packet from`, `exiting (due to fatal error)` 문자열은 탐지 규칙이 찾는 문자열이기도 합니다[8].

### Windows 분석 이벤트

분석 이벤트는 이벤트 텍스트 안에 `이름=값` 쌍을 세미콜론으로 이어 씁니다. 조사에 자주 쓰는 ID 와 필드는 다음과 같습니다[3].

| ID | 이름 | 필드 |
|---|---|---|
| 257 | RESPONSE_SUCCESS | TCP, InterfaceIP, Destination, AA, AD, QNAME, QTYPE, XID, DNSSEC, RCODE, Port, Flags, Scope, Zone, PolicyName, PacketData |
| 258 | RESPONSE_FAILURE | TCP, InterfaceIP, Reason, Destination, QNAME, QTYPE, XID, RCODE, Port, Flags, Zone, PolicyName, PacketData |
| 259 | IGNORED_QUERY | TCP, InterfaceIP, Reason, QNAME, QTYPE, XID, Zone, PolicyName |
| 260 | RECURSE_QUERY_OUT | TCP, Destination, InterfaceIP, RD, QNAME, QTYPE, XID, Port, Flags, ServerScope, CacheScope, PolicyName, PacketData |
| 261 | RECURSE_RESPONSE_IN | TCP, Source, InterfaceIP, AA, AD, QNAME, QTYPE, XID, Port, Flags, ServerScope, CacheScope, PacketData |
| 262 | RECURSE_QUERY_TIMEOUT | TCP, InterfaceIP, Destination, QNAME, QTYPE, XID, Port, Flags, ServerScope, CacheScope |
| 263 | DYN_UPDATE_RECV | TCP, InterfaceIP, Source, QNAME, XID, Port, Flags, SECURE, PacketData |
| 270 | AXFR_REQ_RECV | TCP, Source, InterfaceIP, QNAME, XID, ZoneScope, Zone, PacketData |

257·258 은 클라이언트에게 보낸 응답이라서 `Destination`·`Port` 가 질의를 보낸 클라이언트의 주소와 포트입니다. 260·261 은 이 서버가 상위 서버에 대신 물은 질의와 받은 응답이라서 `Destination`·`Source` 가 상위 서버입니다. 응답에 들어 있던 주소는 따로 필드가 없고 `PacketData` 에 들어 있는 DNS 메시지를 풀어야 알 수 있습니다[3]. 공개된 분석 이벤트 목록은 257 부터 280 까지이고, 질의를 받은 것 자체를 나타내는 이벤트는 이 목록에 없습니다[3]. 그래서 실제 .etl 파일에서 어떤 ID 가 몇 개 있는지 먼저 세어 봅니다.

### Windows 감사 이벤트와 DNS Server 이벤트 로그

감사 이벤트 ID 는 513 부터 582 까지입니다. 조사에서 먼저 보는 것은 동적 업데이트로 레코드를 만든 519 와 지운 520 이고, 두 이벤트 모두 이벤트 텍스트 끝에 요청을 보낸 IP 주소("via dynamic update from IP Address %8")가 들어 있습니다[3]. 그 밖에 존 삭제 513, 레코드 생성·삭제 515·516, 전달자 목록 변경 537, 서버 설정 변경 541, 서비스 재시작 요청 548, 디버그 로그 삭제 549, 통계 삭제 551, 수신 주소 변경 557, 정책 생성·삭제 577–582 가 있습니다[3].

DNS Server 이벤트 로그의 6004 는 없는 존이나 권한이 없는 존에 대한 존 전송 요청을 받았다는 이벤트이고 요청한 주소가 들어 있습니다[6]. 150·770·771 은 레지스트리에 지정된 서버 플러그인 DLL(ServerLevelPluginDll)을 불러오지 못한 오류를 찾는 탐지 규칙이 보는 ID 입니다[7].

### Windows 디버그 로그 (dns.log)

디버그 로그는 옵션으로 남길 범위를 고릅니다. 방향(보낸 패킷 Send, 받은 패킷 Receive), 내용(표준 질의, 동적 업데이트, NOTIFY), 전송(UDP, TCP), 종류(질의 Request = QR 비트 0, 응답 Response = QR 비트 1), IP 주소 필터, 파일 이름, 최대 크기가 있습니다[3][5]. 줄 형식은 실제 파일의 줄을 보고 열 순서를 확인한 뒤 해석합니다. 어느 옵션이 켜져 있었는지에 따라 파일에 없는 방향·종류가 생기므로 `Get-DnsServerDiagnostics` 결과를 함께 보존합니다.

## 증거로서 의미

### 증명하는 것

BIND 쿼리 로그 한 줄로는 기록된 시각에 이 클라이언트 IP·포트가 이 서버의 이 주소로 이 이름·클래스·유형을 물었다는 것, 그리고 재귀를 요청했는지와 TCP·EDNS 를 썼는지가 확인됩니다[1]. `responselog` 가 켜져 있으면 그 질의의 응답 코드까지 확인됩니다[1]. Windows 257·258 로는 이 서버가 어느 클라이언트 주소·포트에 어떤 응답 코드로 답했는지가, `PacketData` 를 풀면 응답에 넣은 주소까지 확인됩니다[3].

동적 업데이트 519·520 으로는 어느 IP 가 어떤 레코드를 만들거나 지웠는지가 확인됩니다[3]. 270·6004 와 BIND 의 `denied AXFR from` 줄로는 어느 주소가 존 전체를 받아 가려 했는지가 확인됩니다[3][6][8].

보고서에는 "2026-09-27 10:15:02(서버 현지 시각)에 192.168.10.23 이 사내 DNS 서버 192.168.10.2 에 www.example.com 의 A 레코드를 물은 쿼리 로그 줄이 있다"(만든 예시)처럼 기록으로 확인되는 만큼만 씁니다.

### 증명하지 못하는 것

클라이언트가 그 응답을 받아 실제로 접속했는지는 알 수 없습니다. 접속은 방화벽·흐름 기록·프록시 로그로 따로 확인합니다. 서버 로그에는 클라이언트 IP 만 있어서 어느 프로세스나 사용자가 물었는지도 알 수 없습니다.

클라이언트 IP 가 실제 PC 가 아닐 수 있습니다. 지점 DNS 서버나 다른 리졸버가 이 서버에 전달하면 로그의 클라이언트는 그 장비이고, NAT 뒤라면 변환된 주소입니다. 이 경우는 [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md) 과 앞단 장비의 로그로 이어 갑니다.

기록이 없다고 질의가 없었던 것도 아닙니다. 클라이언트 운영체제나 브라우저의 캐시, 중간 리졸버의 캐시가 답한 질의는 이 서버까지 오지 않습니다. DNS over HTTPS(DoH)·DNS over TLS(DoT) 로 다른 리졸버를 쓰거나 외부 DNS 서버에 바로 물은 질의도 남지 않습니다([암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md)). 쿼리 로깅이 꺼져 있었거나, 파일 크기 제한으로 기록이 멈췄거나, 덮어써진 경우도 있습니다.

BIND 쿼리 로그만으로는 서버가 어떤 주소를 답했는지 알 수 없습니다[1]. 그래서 응답 값을 조건으로 쓰는 탐지 규칙(예: Sigma 의 `answer` 필드를 쓰는 DNS 규칙)은 쿼리 로그만으로 판정할 수 없고, `query` 필드 조건만 적용할 수 있습니다[9].

## 시각 해석

BIND 파일 채널의 시각은 `print-time` 설정을 따릅니다[1].

| `print-time` | 기록 |
|---|---|
| `no` (기본) | 시각을 남기지 않음 |
| `yes`, `local` | 서버 현지 시각, 사람이 읽는 형식(예: `28-Feb-2000 15:05:32.863`) |
| `iso8601` | 현지 시각, ISO 8601 형식 |
| `iso8601-utc` | UTC, ISO 8601 형식 |

기본값이 `no` 라서 파일 채널 설정을 바꾸지 않은 서버의 로그 파일에는 줄마다 시각이 아예 없을 수 있습니다. 이때는 파일 시스템의 수정 시각과 백업 파일 순서로 대략의 구간만 알 수 있습니다. syslog 채널에는 syslog 가 시각을 붙이고, RFC 3164 형식이면 연도와 시간대가 없는 현지 시각입니다[1][11]. syslog 시각을 다루는 방법은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에서 다룹니다.

쿼리 로그 줄은 질의를 받아 처리할 때 남기는 줄이라서 응답을 보낸 시각이 아닙니다. 응답 시각과 내용이 필요하면 `responselog` 나 dnstap 기록, 또는 패킷 기록을 봅니다. 크기 제한으로 파일을 돌릴 때 `suffix timestamp` 로 붙는 이름의 시각은 파일을 돌린 시각이지 안에 든 줄의 시각이 아닙니다[1].

Windows 분석 이벤트는 서버가 DNS 정보를 보내거나 받을 때마다 남으므로[3], 257 의 시각은 응답을 보낸 때이고 260 의 시각은 상위 서버에 물은 때입니다. 이벤트 뷰어 화면은 보는 컴퓨터의 시간대로 시각을 바꿔 보여 줄 수 있으므로, 보고서에는 이벤트 XML 의 `TimeCreated` 값을 기준으로 적고 시간대를 함께 씁니다. dns.log 의 시각 형식과 시간대는 실제 파일의 줄과 서버 시간대 설정으로 확인합니다.

## 함정과 한계

BIND 파일 채널에 `size` 만 있고 `versions` 가 없으면 크기를 넘은 뒤로는 파일에 더 쓰지 않습니다[1]. 이런 파일의 마지막 줄은 활동이 끝난 시각이 아니라 기록이 멈춘 시각입니다. `versions` 와 `suffix increment` 가 있으면 파일을 돌릴 때마다 `.0` 이 `.1` 로, `.1` 이 `.2` 로 이름이 밀리므로 수집할 때 번호 붙은 파일을 모두 가져옵니다[1]. `buffered yes` 인 채널은 줄마다 디스크에 쓰지 않으므로 서버가 갑자기 멈추면 마지막 부분이 파일에 없을 가능성이 있습니다[1].

named 를 `-u` 로 실행하면 사용자 ID 를 바꾼 뒤에야 `named.run` 을 만들기 때문에, 그 전에 나온 디버그 출력은 버려집니다[1]. `sslkeylog` 범주를 설정한 서버의 로그에는 디버깅용 TLS 프리마스터 시크릿(pre-master secret)이 들어 있으므로 증거물로 다룰 때 접근을 제한합니다[1].

쿼리 로그가 어느 시점부터 끊겼다면 `rndc querylog off` 로 끈 것일 수 있습니다. 설정 파일의 `querylog` 값만 보고 판단하지 말고, 로그가 끊긴 시각 전후의 관리 작업 기록을 함께 봅니다. Windows 에서는 디버그 로그를 지운 549 와 통계를 지운 551 감사 이벤트가 지우기 흔적으로 남습니다[3].

Windows 디버그 로그는 최대 크기에 이르면 가장 오래된 패킷 정보를 새것으로 덮어씁니다[3][5]. 반대로 `Set-DnsServerDiagnostics -All $true` 는 `EnableLogFileRollover` 까지 켜서, 가득 차면 덮어쓰지 않고 새 파일을 만들어 디스크를 채울 수 있습니다[3]. 분석 로그를 순환 모드로 켠 서버는 이벤트 뷰어에서 바로 조회되지 않으므로 .etl 파일을 따로 수집해야 합니다[3].

포워더를 쓰는 구성에서는 서버마다 보이는 클라이언트가 다릅니다. 앞단 서버의 로그에는 PC 가, 뒷단 서버의 로그에는 앞단 서버가 클라이언트로 남고, 앞단 서버의 260 이벤트 `Destination` 이 뒷단 서버입니다[3].

## 직접 분석해 보기

### 헥스로 한 번: PacketData 풀기

Windows 257 이벤트의 `PacketData` 에 DNS 메시지가 아래처럼 들어 있다고 가정합니다. RFC 1035 명세대로 만든 www.example.com A 레코드 응답입니다(명세로 만든 예시)[10].

```
0000  1a 2b 81 80 00 01 00 01 00 00 00 00 03 77 77 77
0010  07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 01 00
0020  01 c0 0c 00 01 00 01 00 00 0e 10 00 04 cb 00 71
0030  0a
```

| 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0x00 | `1a 2b` | 트랜잭션 ID 0x1a2b(10진 6699) |
| 0x02 | `81 80` | QR=1(응답), RD=1, RA=1, RCODE=0 |
| 0x04 | `00 01` / `00 01` / `00 00` / `00 00` | 질문 1, 응답 레코드 1, 권한 0, 추가 0 |
| 0x0C | `03 77 77 77 … 00` | 질문 이름 www.example.com |
| 0x1D | `00 01` `00 01` | 유형 A, 클래스 IN |
| 0x21 | `c0 0c` | 응답 이름, 오프셋 0x0C 의 이름을 가리키는 압축 포인터 |
| 0x23 | `00 01` `00 01` | 유형 A, 클래스 IN |
| 0x27 | `00 00 0e 10` | TTL 3600초 |
| 0x2B | `00 04` `cb 00 71 0a` | 데이터 길이 4, 주소 203.0.113.10 |

실제 이벤트에서는 먼저 `PacketData` 의 앞 두 바이트가 같은 이벤트의 `XID` 필드 값과 같은지 비교합니다(진법을 맞춰 비교합니다). 같으면 DNS 헤더부터 들어 있는 것이고, 다르면 앞에 붙은 바이트를 건너뛰고 XID 가 나오는 위치를 찾습니다. 헤더와 레코드 구조의 자세한 설명은 [DNS](../../01-foundations/protocols/dns.md) 에 있습니다.

### 공개 도구로 한 번

BIND 쿼리 로그는 텍스트라서 awk 로 풉니다. 채널 설정에 따라 줄 앞의 시각·범주·심각도 개수가 달라지므로, 필드 위치를 고정하지 않고 `query:` 를 기준으로 앞뒤를 찾습니다.

```
# 클라이언트 IP, 질의 이름, 유형
awk '{for(i=1;i<=NF;i++) if($i=="query:"){split($(i-2),c,"#"); print c[1], $(i+1), $(i+3)}}' queries.log*

# 클라이언트별 질의 수
awk '{for(i=1;i<=NF;i++) if($i=="query:"){split($(i-2),c,"#"); print c[1]}}' queries.log* | sort | uniq -c | sort -rn | head

# SERVFAIL 로 끝난 질의
grep 'query failed (SERVFAIL)' queries.log* query-errors.log*
```

dnstap 파일이 있으면 `dnstap-read 파일` 로 질의와 응답을 사람이 읽는 형식으로 봅니다[1]. 기본 설정에서는 재귀 해석에 쓴 서버 쪽 소켓의 IP 주소가 dnstap 출력에 들어가지 않습니다[1].

Windows 는 수집한 `Microsoft-Windows-DNSServer%4Analytical.etl` 이나 `tracelog` 로 만든 .etl 파일을 이벤트 뷰어의 "Open Saved Log" 로 열고, 현재 로그 필터에서 이벤트 ID 를 골라 봅니다[3]. 실행 중인 서버에서는 `Get-DnsServerDiagnostics` 결과를 파일로 남겨, 조사 기간에 어떤 디버그 옵션이 켜져 있었는지를 증거와 함께 보존합니다[3].

## 교차 검증

| 함께 볼 기록 | 확인하는 것 |
|---|---|
| [Zeek dns.log](../zeek/zeek-logs/dns-log.md), [Suricata EVE 로그](../suricata/eve-json/index.md) | 센서가 본 질의와 응답. 서버 로그에 없는 응답 주소와, 이 서버를 거치지 않은 외부 DNS 질의 |
| [방화벽 로그](firewall-logs.md), [흐름 기록](../../01-foundations/records/flow-records.md) | 응답으로 받은 주소에 실제로 연결했는지 |
| [웹 프록시 로그](proxy-logs.md) | 프록시가 클라이언트 대신 이름을 물은 경우의 실제 요청 |
| [DHCP 로그](dhcp-logs.md) | 그 시각에 클라이언트 IP 를 쓰던 장치 |
| [윈도 hosts 파일](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/hosts.html), [Linux 이름 해석](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/name-resolution.html), [macOS hosts와 DNS 설정](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/network/hosts-dns.html) | 서버에 묻지 않고 호스트에서 답한 이름, 호스트가 쓰도록 설정된 DNS 서버 |

질의 이름의 모양과 빈도로 이상한 이름을 찾는 방법은 [DNS 분석](../../03-techniques/analysis/dns-analysis.md) 과 [DNS 로 몰래 보냈나](../../04-scenarios/exfiltration/dns-tunneling.md) 에서, 여러 기록을 시간순으로 합치는 방법은 [네트워크 타임라인](../../03-techniques/analysis/timeline.md) 에서, 특정 시각의 IP 사용자를 찾는 흐름은 [이 시각에 이 IP 를 누가 썼나](../../04-scenarios/user-activity/ip-attribution.md) 에서 다룹니다.

## 실습

공개 캡처 파일에는 서버 로그가 들어 있지 않으므로, 이 페이지의 만든 예시와 DNS 트래픽이 들어 있는 공개 캡처 파일(Wireshark 예제 캡처 등)로 아래 질문을 풉니다.

1. 쿼리 로그 예시의 두 줄에서 재귀 요청, TCP 사용, DO 비트가 각각 어떻게 다른지 플래그로 읽습니다. 두 번째 줄의 클라이언트가 일반 PC 가 아닐 가능성은 무엇으로 확인합니까?
2. 공개 캡처 파일에서 DNS 응답 패킷 하나를 골라 DNS 메시지 바이트를 16진으로 뽑고, 위 PacketData 표처럼 헤더·질문·응답 레코드를 나눠 봅니다.
3. 같은 캡처를 Zeek 으로 돌려 dns.log 를 만든 뒤, 같은 질의를 BIND 쿼리 로그 형식으로 옮긴다면 어느 정보가 빠지는지 적어 봅니다.
4. `print-time` 이 `no` 인 쿼리 로그 파일 세 개(`.0`·`.1`·현재 파일)만 있을 때, 한 줄이 기록된 시각의 범위를 어떻게 좁힐 수 있습니까?
5. Windows DNS 서버에서 519 이벤트의 IP 와 같은 시각 DHCP 로그의 임대 기록을 비교하면 무엇을 확인할 수 있습니까?

## 참고 문헌

1. Internet Systems Consortium, BIND 9 Administrator Reference Manual, "Configuration Reference"(BIND 9.20 문서). https://bind9.readthedocs.io/en/stable/reference.html
2. Internet Systems Consortium, Knowledge Base AA-01526(BIND 로깅 권장 설정과 예시 구성). https://kb.isc.org/docs/aa-01526
3. Microsoft, "Enable DNS Logging and Diagnostics"(Windows Server 2016–2025). https://learn.microsoft.com/en-us/windows-server/networking/dns/dns-logging-and-diagnostics
4. Microsoft, "DNS Logging and Diagnostics"(Windows Server 2012 R2). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn800669(v=ws.11)
5. Microsoft, "Using server debug logging options"(Windows Server 2003). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc776361(v=ws.10)
6. SigmaHQ, win_dns_server_failed_dns_zone_transfer.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/windows/builtin/dns_server/win_dns_server_failed_dns_zone_transfer.yml
7. SigmaHQ, win_dns_server_susp_server_level_plugin_dll.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/windows/builtin/dns_server/win_dns_server_susp_server_level_plugin_dll.yml
8. SigmaHQ, lnx_syslog_susp_named.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/linux/builtin/syslog/lnx_syslog_susp_named.yml
9. SigmaHQ, rules/network/dns. https://github.com/SigmaHQ/sigma/tree/master/rules/network/dns
10. P. Mockapetris, 「Domain Names - Implementation and Specification」, RFC 1035, 1987. https://www.rfc-editor.org/rfc/rfc1035.txt
11. C. Lonvick, 「The BSD syslog Protocol」, RFC 3164, 2001. https://www.rfc-editor.org/rfc/rfc3164.txt
