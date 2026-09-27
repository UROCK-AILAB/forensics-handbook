---
title: "HTTP 기록"
parent: "Zeek 로그"
grand_parent: "아티팩트 · Zeek"
nav_order: 170
---

# HTTP 기록 (http.log)

Zeek 는 평문 HTTP 를 해석해 요청 하나와 그 응답을 한 줄로 묶어 http.log 에 씁니다. 한 줄에는 누가 어느 서버에 어떤 메서드로 무엇을 요청했는지, 서버가 어떤 상태 코드로 몇 바이트를 돌려줬는지, 오간 파일의 ID 가 들어갑니다. 이 페이지는 http.log 의 필드와 시각, 기록 시점, 그리고 한 줄로 주장할 수 있는 범위를 다룹니다. 로그 형식(TSV·JSON)과 uid 의 성질은 [Zeek 로그](index.md) 에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

Zeek 의 HTTP 분석기는 요청·응답 한 쌍과 관련 정보를 레코드 하나에 모아 기록합니다[4]. 한 TCP 연결 안에서 요청이 여러 번 오가면 쌍마다 줄이 하나씩 생기고, `trans_depth` 가 그 연결 안에서 몇 번째 쌍인지 나타냅니다[3][4]. 연결 자체는 [conn.log](conn-log.md) 에 한 줄로 남고, 두 로그는 같은 `uid` 로 이어집니다[2].

분석기는 기본 포트 80, 81, 631, 1080, 3128, 8000, 8080, 8888/tcp 에 붙습니다[4]. 이 밖의 포트에서도 동적 프로토콜 탐지로 HTTP 를 알아보면 기록되는데, 그 연결이 HTTP 로 해석됐는지는 conn.log 의 `service` 필드에 `http` 가 있는지로 확인합니다[1]. HTTP 프로토콜 자체의 요청·응답 구조는 [HTTP](../../../01-foundations/protocols/http.md) 페이지에 있습니다.

HTTPS 는 내용이 암호화돼 있어 http.log 에 남지 않고, 핸드셰이크 정보만 [ssl.log](ssl-x509-log.md) 에 남습니다. 그래서 암호화 비율이 높은 망에서는 http.log 가 적게 쌓이고, HTTPS 를 풀어 평문 HTTP 로 넘기는 구간을 센서가 볼 때 다시 쓸모가 커집니다[2].

## 위치와 버전별 차이

파일 이름은 `http.log` 이고 저장 위치와 교대(rotate) 규칙은 다른 Zeek 로그와 같습니다([Zeek 로그](index.md)). 필드 구성은 Zeek 버전과 불러온 스크립트에 따라 달라집니다.

| 버전 | 바뀐 점 |
|---|---|
| Zeek 3.0.0 | `origin` 필드(Origin 헤더) 추가[7]. `orig_fuids`·`resp_fuids` 같은 파일 필드를 방향마다 최대 15개(`HTTP::max_files_orig`·`HTTP::max_files_resp`)까지만 기록[5][7] |
| Zeek 4.2.0 | `host` 에 Host 헤더를 원래 값 그대로 기록. 그 전에는 `example.com:8080` 의 포트 부분을 빼고 기록[7] |
| Zeek 6.1.0 | 응답을 받지 못한 요청이 100개(`HTTP::max_pending_requests`)를 넘으면 쌓인 요청을 한꺼번에 기록하고 짝 맞추기를 처음부터 다시 함[7] |
| Zeek 8.1.0 | JSON 로그에서 출력할 수 없는 제어 문자를 `\uXXXX` 로 씀. 예: `"uri":"/non_printable_\\x07"` 이 `"uri":"/non_printable_\u0007"` 로 바뀜[7] |
| Zeek 9.0.0 | `QUERY` 메서드를 알려진 메서드 목록에 넣어 더는 weird 를 남기지 않음[4][7] |

기본 스크립트 밖에서 필드를 더하는 스크립트도 있습니다. `policy/protocols/http/header-names.zeek` 를 불러오면 요청·응답 헤더 이름만 모은 `client_header_names`·`server_header_names` 가, `var-extraction-cookies.zeek`·`var-extraction-uri.zeek` 를 불러오면 쿠키와 URI 의 변수 이름을 모은 `cookie_vars`·`uri_vars` 가 붙습니다[3]. 기본 설정 파일 local.zeek 은 `detect-sql-injection` 을 불러오고[9], 이 스크립트는 URI 가 SQL 삽입 모양이면 `tags` 에 `URI_SQLI` 를 넣습니다[8]. JA4H 같은 HTTP 지문 필드는 별도 플러그인이 더하며, [TLS 지문](../../fingerprints/ja3-ja4.md) 페이지에서 다룹니다.

## 구조

### 한 줄의 모양

다음은 기본 설정의 http.log 형식으로 만든 TSV 한 줄과 같은 내용의 JSON 한 줄입니다(만든 예시). 필드 순서는 기본 설정 TSV 의 `#fields` 줄과 같습니다[1].

```text
#fields	ts	uid	id.orig_h	id.orig_p	id.resp_h	id.resp_p	trans_depth	method	host	uri	referrer	version	user_agent	origin	request_body_len	response_body_len	status_code	status_msg	info_code	info_msg	tags	username	password	proxied	orig_fuids	orig_filenames	orig_mime_types	resp_fuids	resp_filenames	resp_mime_types
1772446530.512593	CAbcdE1fGhIjKlMn2	192.168.0.10	49152	203.0.113.5	80	1	GET	www.example.com	/	-	1.1	curl/8.5.0	-	0	39	200	OK	-	-	(empty)	-	-	-	-	-	-	FAbcdE1fGhIjKlMn2	-	text/plain
```

```json
{"ts":1772446530.512593,"uid":"CAbcdE1fGhIjKlMn2","id.orig_h":"192.168.0.10","id.orig_p":49152,"id.resp_h":"203.0.113.5","id.resp_p":80,"trans_depth":1,"method":"GET","host":"www.example.com","uri":"/","version":"1.1","user_agent":"curl/8.5.0","request_body_len":0,"response_body_len":39,"status_code":200,"status_msg":"OK","tags":[],"resp_fuids":["FAbcdE1fGhIjKlMn2"],"resp_mime_types":["text/plain"]}
```

TSV 에서 값이 없는 필드는 `-`, 빈 집합은 `(empty)` 로 쓰고, JSON 에서는 값이 없는 필드의 키가 아예 빠지고 빈 집합은 `[]` 가 됩니다[1]. 위 예에서 `referrer`·`origin` 이 JSON 에 없는 것도 그래서입니다.

### 필드

기본 설정에서 기록되는 필드는 다음과 같습니다[3][4][5].

| 필드 | 뜻 |
|---|---|
| `ts` | 요청 레코드를 만든 시각(아래 "시각 해석") |
| `uid`, `id.orig_h`·`id.orig_p`·`id.resp_h`·`id.resp_p` | 연결 ID 와 양 끝 주소·포트. conn.log 와 같은 값 |
| `trans_depth` | 이 연결 안에서 몇 번째 요청·응답 쌍인지(1부터) |
| `method` | 요청 메서드(GET·POST·PUT 등) |
| `host` | 요청의 Host 헤더 값. 4.2.0 부터 포트까지 그대로 |
| `uri` | 요청 URI. 퍼센트 인코딩(`%7E` 등)을 모두 푼 값 |
| `referrer` | Referer 헤더 값. 필드 이름은 올바른 철자로 씀 |
| `version` | 응답 상태 줄의 HTTP 버전(요청 쪽 버전이 아님) |
| `user_agent` | 요청의 User-Agent 헤더 값 |
| `origin` | 요청의 Origin 헤더 값 |
| `request_body_len`·`response_body_len` | 압축을 푼 실제 본문 크기(바이트). 본문이 없으면 0 |
| `status_code`·`status_msg` | 응답 상태 코드와 메시지 |
| `info_code`·`info_msg` | 마지막으로 본 1xx 응답의 코드와 메시지 |
| `tags` | 스크립트가 붙이는 표시 집합. 기본 스크립트만으로는 비어 있음 |
| `username`·`password` | Basic 인증 사용자 이름과 비밀번호 |
| `proxied` | 프록시를 거쳤음을 뜻하는 헤더 모음. 값 하나가 `헤더 -> 값` 형식 |
| `orig_fuids`·`orig_filenames`·`orig_mime_types` | 클라이언트가 보낸 본문(업로드)의 파일 ID·파일 이름·MIME 형식 |
| `resp_fuids`·`resp_filenames`·`resp_mime_types` | 서버가 보낸 본문(다운로드)의 파일 ID·파일 이름·MIME 형식 |

`proxied` 에 들어가는 헤더는 FORWARDED, X-FORWARDED-FOR, X-FORWARDED-FROM, CLIENT-IP, VIA, XROXY-CONNECTION, PROXY-CONNECTION 입니다[4]. 예를 들어 `X-FORWARDED-FOR -> 198.51.100.7`(만든 예시)이 있으면, 요청을 보낸 주소 앞에 다른 클라이언트가 있었다고 헤더가 주장한다는 뜻입니다.

Authorization 이나 Proxy-Authorization 헤더가 Basic 방식이면 Zeek 가 base64 를 풀어 `:` 앞부분을 `username` 에 넣습니다[4]. 비밀번호는 `HTTP::default_capture_password` 가 기본 F 라서 기록하지 않습니다[4]. 풀어 낸 값에 `:` 가 없으면 `username` 에 `<problem-decoding> (헤더 원래 값)` 을 씁니다[4].

## 증거로서 의미

**증명하는 것.** 센서가 본 평문 HTTP 트래픽에서, 어느 내부 주소가 어느 서버 주소·포트로 어떤 Host 와 URI 를 어떤 메서드로 요청했고, 서버가 어떤 상태 코드와 크기로 응답했는지를 보여 줍니다. `resp_fuids` 의 파일 ID 로 [files.log](files-log.md) 의 해시·MIME 형식, 설정했다면 추출한 파일까지 이어 갈 수 있어서, "이 시각에 이 주소가 이 URI 에서 이 해시의 파일을 받은 기록이 있다" 까지 쓸 수 있습니다[10]. `request_body_len` 이 큰 POST·PUT 은 클라이언트가 밖으로 보낸 양을 보여 줍니다.

**증명하지 못하는 것.** 누가, 어느 프로세스가 요청했는지는 기록되지 않습니다. `user_agent` 는 클라이언트가 마음대로 적는 값이라서, `Wget/1.19.4 (linux-gnu)` 가 찍혔다면 wget 을 썼을 가능성이 높다는 정도로만 해석합니다[10]. 사용자가 링크를 직접 눌렀는지, 페이지가 스스로 불러온 요청인지도 구분되지 않고, `referrer` 도 클라이언트가 보낸 헤더일 뿐입니다. HTTPS 요청의 URI 와 본문은 없으며, 센서가 보지 못한 구간이나 패킷 손실이 있던 구간의 요청은 빠집니다. 응답 헤더 가운데 `Server`·`Date` 같은 값은 기본 로그에 없습니다[2][4].

## 시각 해석

`ts` 는 Zeek 가 그 요청의 레코드를 처음 만들 때의 네트워크 시각(`network_time()`)입니다[4]. 보통은 요청 줄을 담은 패킷을 처리한 때라서, 연결을 여는 SYN 시각인 conn.log 의 `ts` 보다 조금 늦습니다. 예를 들어 SYN 이 14:39:59.430166(UTC), GET 요청 패킷이 14:39:59.512593 인 연결에서 http.log 의 `ts` 는 1591367999.512593 으로 GET 패킷 시각과 같습니다[1]. 값은 1970-01-01 UTC 기준 초라서 시간대가 없고, JSON 에서 ISO 8601 로 바꾸는 설정과 읽는 법은 [Zeek 로그](index.md) 와 [네트워크 기록의 시각](../../../01-foundations/records/timestamps.md) 에 있습니다.

줄이 파일에 쓰이는 때는 응답 본문이 끝났을 때입니다[4]. 100 Continue 같은 1xx 응답을 받으면 같은 레코드를 계속 쓰다가 최종 응답이 끝난 뒤 한 줄로 남기고, `info_code` 에 마지막 1xx 가 남습니다[4]. 응답이 오지 않은 요청은 연결이 정리될 때 한꺼번에 기록되고, 이때는 `status_code` 가 비어 있습니다[4]. 그래서 파일 안의 줄 순서는 요청 순서와 다를 수 있고, 시간순으로 볼 때는 `ts` 로 정렬합니다.

요청은 보지 못하고 응답만 본 경우에는 응답을 처리할 때 레코드를 만들기 때문에 `ts` 가 응답 시각이 되고 `method`·`host`·`uri` 가 비어 있습니다[4]. 응답의 `Date` 헤더는 서버 시계 값이라 패킷 시각과 다를 수 있고, 기본 http.log 에는 기록되지 않습니다[2][4].

## 함정과 한계

**MIME 형식은 헤더가 아니라 내용으로 정합니다.** Zeek 는 libmagic 이 아니라 자체 콘텐츠 시그니처로 본문 내용을 보고 MIME 형식을 정합니다[9]. 그래서 응답 헤더의 Content-Type 과 `resp_mime_types` 가 다를 수 있습니다. 예를 들어 응답 헤더가 `text/html; charset=UTF-8` 인 짧은 텍스트 응답이 `resp_mime_types` 에는 `text/plain` 으로 남습니다[1][2]. 확장자를 바꿔 실행 파일을 내려받은 경우에는 오히려 이 차이가 단서가 됩니다.

**uri 는 디코딩된 값입니다.** `uri` 에는 퍼센트 인코딩을 모두 푼 URI 가 들어갑니다[4][6]. 공격 문자열이 원래 어떻게 인코딩돼 있었는지, 이중 인코딩을 썼는지는 로그만으로 알 수 없어서 패킷을 봐야 합니다. Zeek 8.1.0 부터는 JSON 에서 제어 문자 표기가 바뀌었으므로, 버전이 섞인 로그를 문자열로 검색할 때 `\x07` 과 `\u0007` 을 둘 다 찾습니다[7].

**host 에 포트가 붙을 수 있습니다.** 4.2.0 이후 로그는 `www.example.com:8080` 처럼 포트까지 기록하므로[7], 도메인 목록과 비교하거나 `host` 끝부분으로 최상위 도메인을 거를 때는 포트를 떼고 비교합니다.

**비밀번호가 찍혀 있으면 설정을 먼저 봅니다.** `password` 는 기본으로 비어 있습니다[4]. 값이 있다면 그 센서가 `HTTP::default_capture_password` 를 켰거나 스크립트로 비밀번호 기록을 켠 것이므로, 로그를 넘기거나 보고서에 옮길 때 다루는 범위를 정해야 합니다.

**필드 길이 제한이 없습니다.** Zeek 8.1.0 부터 로그는 문자열 필드 하나를 기본 4096바이트(`Log::default_max_field_string_bytes`)에서 자릅니다[7][15]. HTTP 로그는 URI 처럼 길이 제한이 없는 값이 많아서 `HTTP::default_max_field_string_bytes` 가 0(제한 없음)이고, 그래서 아주 긴 URI 도 잘리지 않고 남습니다[4].

**파일 필드는 15개까지입니다.** 한 요청·응답에 MIME 파트가 많으면 방향마다 15개까지만 `*_fuids` 등에 남습니다[5]. 나머지 파일은 files.log 에서 같은 `uid` 로 찾습니다.

**파이프라이닝과 한쪽만 잡힌 캡처.** 응답이 요청보다 많이 보이면 weird `HTTP_response_before_request` 를, 응답 없는 요청이 100개를 넘으면 weird `HTTP_excessive_pipelining` 을 남기고 쌓인 요청을 한꺼번에 기록합니다[4]. 이 weird 가 있는 연결은 요청과 응답의 짝이 틀렸을 수 있으므로, 상태 코드나 파일 ID 를 해석하기 전에 패킷으로 짝을 다시 확인합니다. weird 는 [notice.log·weird.log](notice-weird-log.md) 에서 다룹니다.

**알려지지 않은 메서드.** 목록에 없는 메서드는 그대로 `method` 에 남고, weird.log 에 `unknown_HTTP_method` 가 메서드 이름과 함께 남습니다[4][11]. 분석기는 영문자로만 된 메서드만 받아들입니다[4].

**CONNECT 는 터널로 넘어갑니다.** CONNECT 요청에 200 응답이 오면 Zeek 는 그 연결을 HTTP 터널로 등록합니다[4]. 프록시를 거친 HTTPS 는 http.log 에 CONNECT 요청으로 남고, 그 안의 TLS 는 ssl.log 에서 봅니다. 프록시 서버 자체의 기록은 [웹 프록시 로그](../../devices/proxy-logs.md) 에 있습니다.

## 직접 분석해 보기

### 헥스로 한 번: 요청 바이트와 필드

다음은 HTTP 명세의 요청 형식으로 만든 요청 머리 부분입니다(명세로 만든 예시).

```text
00000000: 4745 5420 2f66 696c 6573 2f25 3745 7573  GET /files/%7Eus
00000010: 6572 2f72 6570 6f72 742e 7064 6620 4854  er/report.pdf HT
00000020: 5450 2f31 2e31 0d0a 486f 7374 3a20 7777  TP/1.1..Host: ww
00000030: 772e 6578 616d 706c 652e 636f 6d3a 3830  w.example.com:80
00000040: 3830 0d0a 5573 6572 2d41 6765 6e74 3a20  80..User-Agent:
00000050: 6375 726c 2f38 2e35 2e30 0d0a 0d0a       curl/8.5.0....
```

첫 줄의 공백(0x20)까지가 `method` 인 `GET` 입니다. 다음 공백까지인 `/files/%7Euser/report.pdf` 는 `%7E` 가 `~` 로 풀려 `uri` 에 `/files/~user/report.pdf` 로 남습니다[4][6]. 줄 끝 `0d0a` 뒤의 `Host:` 헤더 값 `www.example.com:8080` 은 4.2.0 이후 로그라면 포트까지 그대로 `host` 에 들어갑니다[7]. `User-Agent:` 값은 `user_agent` 가 되고, 빈 줄(`0d0a 0d0a`)에서 헤더가 끝납니다. 요청 줄 끝의 `HTTP/1.1` 은 로그의 `version` 이 아니며, `version` 은 응답 상태 줄에서 가져옵니다[3][4].

### 공개 도구로 한 번: zeek-cut·jq

TSV 로그에서는 zeek-cut 으로 필요한 필드만 뽑습니다[1].

```text
zeek-cut -d ts uid id.orig_h host uri method status_code resp_mime_types < http.log
```

JSON 로그에서는 점이 들어간 키를 따옴표로 묶어 jq 로 뽑습니다. 다음은 응답 MIME 형식에 실행 파일이 들어간 줄만 고르는 예입니다.

```text
jq -c 'select((.resp_mime_types // []) | index("application/x-dosexec")) | [.ts, ."id.orig_h", .host, .uri, .resp_fuids]' http.log
```

값이 없는 필드는 JSON 에서 키가 빠지므로 `// []` 처럼 기본값을 줍니다. 원래 바이트와 로그를 비교할 때는 `tcpflow -r trace.pcap port 80` 으로 방향별 흐름 파일을 만들어 요청·응답 원문을 봅니다[2]. Wireshark 로 같은 요청을 찾는 법은 [Wireshark·tshark로 읽기](../../../03-techniques/analysis/wireshark.md) 에 있습니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 | 링크 |
|---|---|---|
| conn.log | 같은 `uid` 의 연결 시작·길이·보낸 바이트, `service` 가 http 인지 | [conn.log](conn-log.md) |
| dns.log | 요청 직전에 `host` 이름을 질의했는지, 응답 주소가 `id.resp_h` 와 같은지 | [dns.log](dns-log.md) |
| files.log | `resp_fuids`·`orig_fuids` 의 해시·MIME 형식·추출 파일 | [files.log](files-log.md) |
| weird.log | 같은 `uid` 의 `unknown_HTTP_method`·파이프라이닝 이상 | [notice.log·weird.log](notice-weird-log.md) |
| Suricata EVE 의 http 기록 | 같은 요청을 다른 엔진이 어떻게 기록했는지(커뮤니티 ID 로 연결) | [Suricata 프로토콜 기록](../../suricata/eve-json/protocol-events.md) |
| 웹 서버 로그 | 서버 쪽에 같은 시각·URI·상태 코드가 남았는지 | [웹 서버 로그 (Apache·Nginx)](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/servers/web-server-logs.html) |
| 브라우저 기록 | 요청한 PC 의 방문 기록에 같은 URL 이 있는지 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) |

탐지 규칙도 http.log 필드 이름을 그대로 씁니다. SigmaHQ 의 Zeek HTTP 규칙은 `user_agent`·`method`·`id.resp_h` 로 외부로 나가는 WebDAV PUT 요청을 찾고[12], `host` 끝의 최상위 도메인과 `uri` 끝 확장자나 `resp_mime_types` 를 묶어 의심 도메인에서 받은 실행 파일을 찾습니다[13]. 다만 같은 저장소의 WebDAV 실행 파일 다운로드 규칙은 `c-useragent`·`c-uri` 처럼 프록시 로그식 이름을 섞어 써서 Zeek 로그에 그대로 걸리지 않을 수 있습니다[14]. 규칙을 로그에 맞추는 법은 [탐지 규칙 활용](../../../03-techniques/analysis/detection-rules.md) 에 있습니다.

## 실습

Zeek 빠른 시작 안내서의 quickstart.pcap 을 `zeek -r quickstart.pcap LogAscii::use_json=T` 로 처리하면 conn.log·http.log·weird.log 가 생깁니다[11].

1. http.log 의 두 줄 가운데 `method` 가 `WEIRD` 인 줄의 `uid` 로 weird.log 를 찾아, `name`·`addl` 값과 `ts` 가 http.log 와 같은지 확인합니다.
2. 같은 `uid` 의 conn.log `ts` 와 http.log `ts` 차이는 얼마이고, 그 차이는 연결의 어느 단계에 해당합니까?
3. `resp_mime_types` 와 tcpflow 로 본 응답의 Content-Type 헤더가 같은지 비교합니다.
4. 같은 pcap 을 TSV 로 한 번 더 처리해, 값이 없는 필드가 TSV 의 `-` 와 JSON 의 빠진 키로 어떻게 다르게 나오는지 확인합니다.

## 참고 문헌

1. Zeek Documentation, Zeek Log Formats and Inspection. https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
2. Zeek Documentation, Logs: http.log. https://github.com/zeek/zeek-docs/blob/master/logs/http.rst
3. Zeek Documentation, base/protocols/http/main.zeek (HTTP::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/http/main.zeek.rst
4. Zeek 소스 scripts/base/protocols/http/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/http/main.zeek
5. Zeek Documentation, base/protocols/http/entities.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/http/entities.zeek.rst
6. Zeek 소스 src/analyzer/protocol/http/events.bif (http_request 이벤트). https://github.com/zeek/zeek/blob/master/src/analyzer/protocol/http/events.bif
7. Zeek NEWS (3.0.0·4.2.0·6.1.0·8.1.0·9.0.0 절). https://github.com/zeek/zeek/blob/master/NEWS
8. Zeek 소스 scripts/policy/protocols/http/detect-sql-injection.zeek. https://github.com/zeek/zeek/blob/master/scripts/policy/protocols/http/detect-sql-injection.zeek
9. Zeek Documentation, File Analysis; Zeek 소스 scripts/site/local.zeek. https://github.com/zeek/zeek-docs/blob/master/frameworks/file-analysis.rst , https://github.com/zeek/zeek/blob/master/scripts/site/local.zeek
10. Zeek Documentation, Logs: files.log. https://github.com/zeek/zeek-docs/blob/master/logs/files.rst
11. Zeek Documentation, Quick Start Guide. https://docs.zeek.org/en/master/quickstart.html
12. SigmaHQ, zeek_http_webdav_put_request.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_webdav_put_request.yml
13. SigmaHQ, zeek_http_susp_file_ext_from_susp_tld.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_susp_file_ext_from_susp_tld.yml
14. SigmaHQ, zeek_http_executable_download_from_webdav.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_executable_download_from_webdav.yml
15. Zeek 소스 scripts/base/init-bare.zeek (Log::default_max_field_string_bytes). https://github.com/zeek/zeek/blob/master/scripts/base/init-bare.zeek
