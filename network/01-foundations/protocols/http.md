---
title: "HTTP"
parent: "기반 · 프로토콜 기초"
nav_order: 60
---

# HTTP

HTTP 는 웹 브라우저와 여러 프로그램이 서버에 자원을 요청하고 응답을 받는 프로토콜입니다. 암호화하지 않은 HTTP/1.1 은 요청 줄·상태 줄·헤더가 글자 그대로 오가서, 캡처 파일이나 Zeek·Suricata·프록시 로그만으로 누가 어느 호스트의 어떤 경로를 요청했고 서버가 어떤 상태 코드와 본문을 돌려줬는지 알 수 있습니다. 대신 Host·User-Agent·Referer 는 클라이언트가 마음대로 넣는 값이고, 요청이 사람의 클릭에서 나왔는지는 HTTP 기록에 나오지 않습니다.

## 이 형식을 쓰는 아티팩트

HTTP 요청과 응답은 여러 기록에 흔적을 남깁니다. 패킷 캡처(pcap·pcapng)에는 메시지 바이트가 그대로 남고, Zeek 는 요청과 응답 한 쌍을 `http.log` 의 레코드 하나로 묶어 기록합니다[4][5]. Suricata 는 EVE JSON 의 `event_type` 이 `http` 인 이벤트로 남기고[10], 웹 프록시는 요청마다 access.log 에 한 줄을 씁니다. Squid 의 기본 형식은 `%ts.%03tu %6tr %>a %Ss/%03>Hs %<st %rm %ru %[un %Sh/%<a %mt` 로, 메서드(`%rm`)·URL(`%ru`)·상태 코드(`%>Hs`)가 한 줄에 들어갑니다[18]. 프록시 로그 해석은 [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md), Zeek·Suricata 로그 전체 구성은 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md)와 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)에서 다룹니다.

HTTPS 는 TLS 안에 HTTP 를 담아 보내므로 네트워크 기록에는 HTTP 메시지가 남지 않습니다. Zeek 도 `https.log` 를 따로 만들지 않고 TLS 핸드셰이크 정보를 `ssl.log` 에 남깁니다[9]. 암호화된 웹 트래픽은 [TLS와 인증서](tls.md)와 [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md)에서 다룹니다. 조사 대상 PC 의 브라우저 방문 기록은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) 같은 운영체제 핸드북 페이지에 있습니다.

## 구조 — 표와 오프셋

### 메시지 모양 (HTTP/1.1)

HTTP/1.1 메시지는 시작 줄(start-line) 하나, 헤더 줄 0개 이상, 헤더가 끝났음을 알리는 빈 줄, 그리고 선택적인 본문(message body)으로 이뤄집니다. 줄 끝은 CRLF(0x0D 0x0A)입니다. 요청과 응답은 시작 줄 모양과 본문 길이를 정하는 규칙만 다릅니다[2].

| 부분 | 요청 | 응답 |
|---|---|---|
| 시작 줄 | 요청 줄: `메서드 SP 요청 대상 SP HTTP-버전` | 상태 줄: `HTTP-버전 SP 상태 코드 SP 이유 문구` |
| 헤더 | `이름: 값` 한 줄씩, 이름은 대소문자를 구분하지 않음 | 같은 형식 |
| 빈 줄 | CRLF 하나 | CRLF 하나 |
| 본문 | Content-Length·Transfer-Encoding 이 없으면 본문 없음 | 길이 규칙에 따라 읽음(아래) |

메서드(method)는 대소문자를 구분하는 토큰이고, 표준 메서드는 관례상 대문자로 씁니다[1][2]. 상태 코드(status code)는 세 자리 숫자이고, 이유 문구(reason phrase)는 권고일 뿐이라 서버가 바꾸거나 뺄 수 있습니다. 이유 문구를 빼도 상태 코드 뒤 공백은 남겨야 합니다[1][2].

### 요청 대상의 네 가지 형식

요청 줄의 요청 대상(request-target)은 요청을 누구에게 보내느냐에 따라 모양이 다릅니다[2]. 서버는 absolute-form 도 받아야 하지만 HTTP/1.1 클라이언트는 대개 프록시에 보낼 때만 이 형식을 쓰므로[2], 요청 대상의 모양을 보면 그 요청이 프록시로 가던 것인지 짐작할 수 있습니다.

| 형식 | 예 (만든 예시) | 쓰는 경우 |
|---|---|---|
| origin-form | `GET /report.pdf?id=7 HTTP/1.1` | 서버에 직접 보낼 때. 경로와 쿼리만 쓰고 호스트는 Host 헤더에 |
| absolute-form | `GET http://www.example.com/report.pdf HTTP/1.1` | 프록시에 보낼 때. 전체 URI 를 씀 |
| authority-form | `CONNECT www.example.com:443 HTTP/1.1` | CONNECT 로 터널을 열 때. 호스트와 포트만 |
| asterisk-form | `OPTIONS * HTTP/1.1` | 서버 전체에 대한 OPTIONS |

CONNECT 요청에 2xx 로 응답하면 빈 줄 바로 다음부터 그 연결은 터널이 됩니다[2]. 그래서 프록시 앞에서 캡처한 HTTPS 는 `CONNECT 호스트:포트` 요청 한 번과 그 뒤의 TLS 바이트로 보입니다.

### 포렌식에서 자주 보는 헤더

| 헤더 | 뜻 | 해석할 때 |
|---|---|---|
| Host | 대상 URI 의 호스트와 포트 | HTTP/1.1 요청에는 반드시 있어야 하고, 없거나 두 번 나오면 서버는 400 으로 응답해야 합니다[2]. HTTP/2·HTTP/3 에서는 `:authority` 의사 헤더(pseudo-header)가 대신할 수 있습니다[1] |
| User-Agent | 요청한 프로그램의 제품 이름과 버전 | 보내도록 권장(SHOULD)되지만 설정으로 안 보낼 수 있습니다[1] |
| Referer | 대상 URI 를 얻은 자원의 URI | 표준 헤더 이름부터 referrer 의 철자를 틀리게 적은 것입니다. 조각(fragment)과 사용자 정보는 넣지 않고, 모든 요청에 있지는 않습니다. HTTPS 페이지에서 HTTP 요청으로 넘어갈 때는 보내면 안 됩니다(MUST NOT)[1] |
| Date | 메시지를 만든 시각의 근사값 | 시계가 있는 서버는 2xx·3xx·4xx 응답에 반드시 넣습니다[1] |
| Content-Length, Transfer-Encoding | 본문 길이, 청크 전송 | 아래 "본문 길이" 참고 |
| Via, Forwarded, X-Forwarded-For | 중간 프록시와 원래 클라이언트 정보 | 프록시는 전달하는 메시지마다 Via 를 붙여야 합니다[1]. Forwarded 는 선택 헤더이고, 중간 프록시가 앞서 붙은 값을 지울 수도 있습니다[3] |

### 본문 길이

본문이 어디서 끝나는지는 정해진 순서대로 판단합니다[2]. HEAD 요청에 대한 응답과 1xx·204·304 응답에는 본문이 없습니다. Transfer-Encoding 과 Content-Length 가 함께 있으면 Transfer-Encoding 이 우선하고, 이런 메시지는 요청 밀반입(request smuggling) 시도일 수 있어 오류로 다뤄야 합니다. 청크 전송(chunked)은 16진수 청크 크기, CRLF, 데이터, CRLF 를 되풀이하고 크기가 0 인 청크로 끝납니다. 길이 정보가 없는 응답은 서버가 연결을 닫을 때까지가 본문이라서, 끝까지 받은 응답과 도중에 끊긴 응답을 구분할 수 없습니다[2].

### 헥스로 따라가기

아래는 명세로 만든 예시 요청 51바이트입니다. 요청 줄이 0x00~0x19, Host 헤더 줄이 0x1A~0x30, 헤더 끝을 알리는 빈 줄이 0x31~0x32 입니다.

```
0000  47 45 54 20 2f 72 65 70 6f 72 74 2e 70 64 66 20   GET /report.pdf
0010  48 54 54 50 2f 31 2e 31 0d 0a 48 6f 73 74 3a 20   HTTP/1.1..Host:
0020  77 77 77 2e 65 78 61 6d 70 6c 65 2e 63 6f 6d 0d   www.example.com.
0030  0a 0d 0a                                          ...
```

응답도 같은 방식으로 읽습니다. 아래 명세로 만든 예시에서 상태 줄은 `HTTP/1.1 200 OK`, 헤더는 `Content-Length: 5` 하나입니다. 0x22~0x23 은 헤더 줄의 끝, 0x24~0x25 는 빈 줄이고, 그 뒤 5바이트 `hello` 가 본문입니다.

```
0000  48 54 54 50 2f 31 2e 31 20 32 30 30 20 4f 4b 0d   HTTP/1.1 200 OK.
0010  0a 43 6f 6e 74 65 6e 74 2d 4c 65 6e 67 74 68 3a   .Content-Length:
0020  20 35 0d 0a 0d 0a 68 65 6c 6c 6f                   5....hello
```

캡처에서 요청 줄 첫 바이트를 찾으려면 TCP 페이로드 시작에서 `47 45 54 20`(GET 과 공백)이나 `50 4f 53 54 20`(POST 와 공백) 같은 메서드 바이트를 찾고, 응답은 `48 54 54 50 2f`(HTTP/)로 찾습니다. TCP 페이로드 위치와 세그먼트 재조립은 [TCP 연결과 흐름](tcp-sessions.md)에서 다룹니다.

## 읽는 법

### Zeek http.log

Zeek 는 요청과 응답 한 쌍을 레코드 하나로 기록합니다[5]. 주요 필드는 아래와 같습니다[5][6].

| 필드 | 뜻 |
|---|---|
| `ts` | 요청이 일어난 시각 |
| `uid`, `id.*` | 연결 ID 와 주소·포트. `uid` 로 `conn.log` 와 잇습니다 |
| `trans_depth` | 한 연결 안에서 몇 번째 요청·응답인지 |
| `method`, `host`, `uri` | 메서드, Host 헤더 값, 요청 URI |
| `referrer` | Referer 헤더 값. 필드 이름은 바른 철자입니다 |
| `version` | 응답 상태 줄의 버전 부분 |
| `user_agent`, `origin` | User-Agent·Origin 헤더 값 |
| `request_body_len`, `response_body_len` | 압축을 푼 실제 본문 크기(기본값 0) |
| `status_code`, `status_msg` | 상태 코드(숫자)와 서버가 보낸 이유 문구 |
| `info_code`, `info_msg` | 마지막으로 본 1xx 응답 |
| `username`, `password` | Basic 인증을 쓴 요청의 사용자 이름과 비밀번호 |
| `proxied` | 프록시를 거쳤음을 알리는 헤더 모음 |
| `orig_fuids`·`orig_filenames`·`orig_mime_types`, `resp_fuids`·`resp_filenames`·`resp_mime_types` | 요청·응답 본문으로 오간 파일의 ID·이름·MIME 형식 |

아래는 필드 모양을 보이려고 만든 예시입니다.

```
{"ts":1767261600.512593,"uid":"CxAmPle0000000001","id.orig_h":"10.0.0.15","id.orig_p":49321,"id.resp_h":"203.0.113.10","id.resp_p":80,"trans_depth":1,"method":"GET","host":"www.example.com","uri":"/report.pdf","version":"1.1","user_agent":"curl/8.5.0","request_body_len":0,"response_body_len":48213,"status_code":200,"status_msg":"OK","tags":[],"resp_fuids":["FxAmPle00000001"],"resp_mime_types":["application/pdf"]}
```

기본 설정에서는 비어 있거나 아예 없는 필드도 있습니다. `HTTP::default_capture_password` 기본값이 F 라서 `password` 필드는 비어 있습니다[5]. `client_header_names`·`server_header_names`(헤더 이름만, 값 없음)는 `header-names.zeek` 를, `cookie_vars`·`uri_vars` 는 `var-extraction-cookies.zeek`·`var-extraction-uri.zeek` 를 불러와야 생깁니다[5]. 응답의 Server 헤더 같은 값은 기본 `http.log` 에 들어가지 않습니다[4]. `proxied` 필드에 모으는 헤더는 기본으로 CLIENT-IP, X-FORWARDED-FROM, VIA, XROXY-CONNECTION, PROXY-CONNECTION, X-FORWARDED-FOR, FORWARDED 입니다[5].

본문으로 오간 파일은 `resp_fuids` 의 파일 ID(fuid)로 `files.log` 에서 찾습니다. `files.log` 레코드에도 같은 `uid` 가 있고, 추출 설정이 켜져 있으면 `extracted` 필드에 저장된 파일 이름이 나옵니다[8]. 파일을 꺼내는 절차는 [세션 복원과 파일 꺼내기](../../03-techniques/analysis/file-extraction.md)에서 다룹니다.

### Suricata EVE http

Suricata 는 `hostname`, `url`, `http_user_agent`, `http_content_type`, `cookie` 를 기본으로 남기고, `extended: yes` 이면 `length`, `status`, `protocol`, `http_method`, `http_refer` 를 더합니다. Host 헤더에 포트가 있으면 `http_port` 가 따로 나옵니다[10]. `custom` 목록으로 50개 넘는 헤더를 더 남길 수 있고, `dump-all-headers` 를 `both`·`request`·`response` 로 두면 `request_headers`·`response_headers` 배열에 헤더 이름과 값이 모두 들어갑니다[10][11]. 아래는 만든 예시입니다.

```
"http":{"hostname":"www.example.com","url":"/report.pdf","http_user_agent":"curl/8.5.0","http_content_type":"application/pdf","http_method":"GET","protocol":"HTTP/1.1","status":200,"length":48213}
```

`flow_id` 로 같은 흐름의 `alert`·`fileinfo`·`flow` 이벤트와 잇습니다[10].

### Wireshark·tshark

Wireshark 표시 필터로 `http.request.method`, `http.request.uri`, `http.request.full_uri`, `http.host`, `http.user_agent`, `http.referer`, `http.response.code`, `http.response.phrase`, `http.date`, `http.server`, `http.x_forwarded_for`, `http.content_length`, `http.file_data` 를 봅니다. `http.request_in`·`http.response_in` 은 짝이 되는 요청·응답의 프레임 번호이고, `http.time` 은 요청부터 응답까지 걸린 시간입니다[12].

```
tshark -r 사건.pcap -Y "http.request" -T fields -e frame.time_epoch -e ip.src -e http.host -e http.request.uri -e http.user_agent
tshark -r 사건.pcap -q -z http_req,tree
tshark -r 사건.pcap -q --export-objects http,꺼낸파일
```

`-z http,stat` 은 상태 코드와 메서드 개수를, `-z http_req,tree` 는 서버별 요청 URI 를, `-z http_srv,tree` 는 요청을 서버 IP·호스트 이름별로, 응답을 서버 IP·상태별로, `-z http_seq,tree` 는 Referer 와 요청 URI 의 관계를 보여 줍니다[13]. `--export-objects` 는 이름이 같은 파일을 덮어쓰지 않고 확장자 앞에 번호를 붙여 저장합니다[13]. 화면 사용법은 [Wireshark·tshark로 읽기](../../03-techniques/analysis/wireshark.md)에 있습니다.

## 포렌식에서 중요한 점

### 증명하는 것

HTTP 기록으로는 어느 시각에 어느 내부 주소가 어느 서버 주소로 어떤 Host·URI·메서드의 요청을 보냈고, 서버가 어떤 상태 코드와 몇 바이트의 본문을 돌려줬는지 확인할 수 있습니다[4][5]. 응답 본문의 MIME 형식과 파일 ID 로 실행 파일 같은 특정 파일이 내려왔는지도 알 수 있습니다[8]. 보고서에는 "이 시각에 10.0.0.15 가 www.example.com 의 /report.pdf 를 GET 으로 요청했고 200 응답과 48,213바이트 본문을 받은 기록이 있다"(만든 예시)처럼 기록에 나온 만큼만 씁니다.

### 증명하지 못하는 것

Host, User-Agent, Referer 는 클라이언트가 채우는 값이라 조작할 수 있습니다[1]. User-Agent 에 브라우저 이름이 있어도 실제로 그 브라우저가 보냈다는 뜻은 아니고, User-Agent 가 비어 있다고 사람이 아니라는 뜻도 아닙니다. 브라우저는 페이지 하나를 열 때 이미지·스크립트 같은 요청을 자동으로 여러 번 보내므로, 요청 기록만으로는 사용자가 그 링크를 직접 눌렀는지 구분할 수 없습니다. 클릭 여부는 [피싱 링크를 눌렀나](../../04-scenarios/user-activity/phishing-click.md)처럼 단말 기록과 함께 판단합니다. HTTPS 의 요청 경로와 본문은 네트워크 기록에 남지 않습니다[9].

### 시각

Zeek `http.log` 의 `ts` 는 요청 시각이라 같은 연결의 `conn.log` `ts`(연결 첫 패킷)보다 늦습니다[5][7]. Zeek 문서의 예시 트래픽에서는 `conn.log` 가 1591367999.430166, `http.log` 가 1591367999.512593 으로 약 0.08초 차이가 납니다[4][7].

응답의 Date 헤더는 서버 시계로 찍은 UTC 시각입니다. 권장 형식은 IMF-fixdate 이고, 받는 쪽은 옛 형식 둘도 읽어야 합니다[1].

| 형식 | 예 (명세의 예) |
|---|---|
| IMF-fixdate (보낼 때 쓰는 형식) | `Sun, 06 Nov 1994 08:49:37 GMT` |
| RFC 850 (옛 형식) | `Sunday, 06-Nov-94 08:49:37 GMT` |
| asctime (옛 형식, UTC 로 가정) | `Sun Nov  6 08:49:37 1994` |

Date 헤더와 캡처 시각을 비교하면 서버 시계가 얼마나 어긋났는지 추정할 수 있습니다. 같은 Zeek 문서 예시에서 요청 `ts` 는 2020-06-05 14:39:59.51 UTC 이고 응답 Date 는 `Fri, 05 Jun 2020 14:40:07 GMT` 라서 약 8초 차이가 납니다[4]. 이 차이만으로는 서버 시계와 센서 시계 가운데 어느 쪽이 틀렸는지 알 수 없습니다. Date 가 없는 응답을 중간 장비가 캐시하거나 전달하면 받은 시각으로 Date 를 붙이므로[1], 프록시를 거친 응답의 Date 는 원래 서버 시계가 아닐 수 있습니다. 로그마다 시각이 무엇을 기준으로 찍히는지는 [네트워크 기록의 시각](../records/timestamps.md)에서 비교합니다.

### 잘린 캡처와 중간부터 잡은 연결

TCP 재조립이 안 되거나, 연결이 이미 시작된 뒤에 캡처를 시작했거나, 세그먼트가 빠지거나 순서가 뒤바뀌어 도착하면 Wireshark 는 HTTP 메시지를 "Continuation" 으로만 보여 줄 수 있습니다[14]. 이런 경우 요청 줄이 없는 응답이나 본문 조각만 남으므로, 헥스에서 `HTTP/` 나 메서드 바이트를 직접 찾아 메시지 경계를 확인합니다. 길이 정보 없이 연결 종료로 끝나는 응답은 완전한 응답인지 끊긴 응답인지 구분할 수 없습니다[2].

## 함정

**Host 와 목적지 IP 가 서로 다를 수 있습니다.** 서버 하나가 Host 값으로 여러 호스트 이름을 구분해 서비스할 수 있고, Host 는 클라이언트가 적는 값이라 악성 코드가 캐시를 오염시키거나 요청을 엉뚱한 서버로 보내려고 조작하기도 합니다[1]. 호스트 이름은 DNS 응답과 함께 확인합니다([DNS](dns.md)).

**한 연결에 요청이 여러 개 들어 있습니다.** HTTP/1.1 은 기본으로 연결을 유지하고, 클라이언트는 응답을 기다리지 않고 요청을 이어 보낼 수(pipelining) 있습니다[2]. Zeek 는 이 순서를 `trans_depth` 로 적고, 한 연결에 대기 중인 요청이 `HTTP::max_pending_requests`(기본 100)를 넘으면 대기 요청을 비우고 추적을 처음부터 다시 합니다[5]. `conn.log` 한 줄의 바이트 수를 요청 하나의 크기로 읽지 않습니다.

**본문 크기와 전송 바이트 수가 다릅니다.** `response_body_len` 은 압축을 푼 본문 크기라서[5], 응답자가 보낸 페이로드 바이트 수인 `conn.log` 의 `resp_bytes` 와 값이 다릅니다[7]. 앞의 Zeek 문서 예시에서도 `response_body_len` 은 39, 같은 연결의 `resp_bytes` 는 295 입니다[4][7].

**파일 ID 목록은 잘릴 수 있습니다.** Zeek 는 요청 쪽과 응답 쪽 파일을 기본으로 각각 15개까지만 `http.log` 에 적습니다(`HTTP::max_files_orig`, `HTTP::max_files_resp`)[6]. 한 연결에서 파일이 많이 오갔으면 `files.log` 를 `uid` 로 따로 찾습니다[8].

**비표준 메서드는 따로 기록됩니다.** Zeek 의 `HTTP::http_methods` 기본 목록(GET, POST, PUT, CONNECT, WebDAV 메서드 등 20개)에 없는 메서드는 weird 로 남고, 영문자로만 된 메서드만 HTTP 로 받아들입니다[5]. 드문 메서드가 보이면 `weird.log` 도 함께 봅니다.

**상태 코드 형식이 도구마다 다릅니다.** Zeek `status_code` 는 숫자이고 `status_msg` 는 서버가 보낸 문구 그대로라 표준 문구와 다를 수 있습니다[1][5]. Suricata `status` 는 설명서의 예시에 숫자 `200` 과 문자열 `"200"` 이 모두 나오므로[10], 쿼리를 쓰기 전에 실제 로그의 형식을 확인합니다.

**프록시 헤더는 출발지 증거가 아닙니다.** X-Forwarded-For·Forwarded 는 중간 장비가 붙이는 값이지만 클라이언트도 적을 수 있고, 뒤쪽 프록시가 앞 값을 지울 수도 있습니다[3]. 원래 클라이언트는 프록시 로그의 접속 주소와 함께 확인합니다.

**탐지 규칙의 필드 이름이 로그와 다를 수 있습니다.** Sigma 의 Zeek HTTP 규칙 가운데 하나는 Zeek 필드 이름(`user_agent`, `method`, `id.resp_h`)을 쓰지만[16], 같은 `product: zeek, service: http` 규칙인데 프록시 식 필드 이름(`c-useragent`, `c-uri`)을 쓰는 것도 있습니다[17]. 필드 매핑 없이 그대로 적용하면 맞는 기록이 있어도 걸리지 않을 수 있습니다. 규칙 적용은 [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md)에서 다룹니다.

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| Zeek | `http.log` 로 요청·응답 쌍 정리, `files.log` 로 본문 파일 추적[4][8] |
| Suricata | EVE `http` 이벤트, `dump-all-headers` 로 헤더 전체 기록[10][11] |
| Wireshark·tshark | `http.*` 필드 필터, `-z http*` 통계, `--export-objects http` 로 본문 꺼내기[12][13] |
| tcpflow | TCP 흐름을 방향별 파일로 저장해 요청과 응답 원문 확인[4][19] |
| JA4H | 요청 헤더 구성으로 만드는 HTTP 클라이언트 지문. 메서드 앞 두 글자(소문자), 버전(HTTP/1.0 은 10, HTTP/1.1 은 11, HTTP/2 는 20), 쿠키·Referer 유무, Cookie·Referer 를 뺀 헤더 수(두 자리, 99 까지), Accept-Language 첫 언어의 앞 네 글자를 앞부분에 담습니다[15]. 지문 해석은 [TLS 지문](../../02-artifacts/fingerprints/ja3-ja4.md)에서 다룹니다 |
| 헥스 편집기 | 요청 줄·상태 줄·빈 줄 경계 직접 확인 |

## 참고 문헌

1. R. Fielding, M. Nottingham, J. Reschke, RFC 9110 "HTTP Semantics", 2022. https://www.rfc-editor.org/rfc/rfc9110.txt
2. R. Fielding, M. Nottingham, J. Reschke, RFC 9112 "HTTP/1.1", 2022. https://www.rfc-editor.org/rfc/rfc9112.txt
3. A. Petersson, M. Nilsson, RFC 7239 "Forwarded HTTP Extension", 2014. https://www.rfc-editor.org/rfc/rfc7239.txt
4. Zeek, http.log 문서. https://github.com/zeek/zeek-docs/blob/master/logs/http.rst
5. Zeek, base/protocols/http/main.zeek (HTTP::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/http/main.zeek.rst
6. Zeek, base/protocols/http/entities.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/http/entities.zeek.rst
7. Zeek, conn.log 문서와 base/protocols/conn/main.zeek. https://github.com/zeek/zeek-docs/blob/master/logs/conn.rst , https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
8. Zeek, files.log 문서. https://github.com/zeek/zeek-docs/blob/master/logs/files.rst
9. Zeek, ssl.log 문서. https://github.com/zeek/zeek-docs/blob/master/logs/ssl.rst
10. OISF, Suricata EVE JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
11. OISF, Suricata EVE JSON Output. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
12. Wireshark, Display Filter Reference: Hypertext Transfer Protocol. https://www.wireshark.org/docs/dfref/h/http.html
13. Wireshark, tshark(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
14. Wireshark User's Guide, Advanced Topics. https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_advanced.adoc
15. FoxIO, JA4H 기술 문서와 ja4h.py. https://github.com/FoxIO-LLC/ja4/blob/main/technical_details/JA4H.md , https://github.com/FoxIO-LLC/ja4/blob/main/python/ja4h.py
16. SigmaHQ, zeek_http_webdav_put_request.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_webdav_put_request.yml
17. SigmaHQ, zeek_http_executable_download_from_webdav.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_executable_download_from_webdav.yml
18. Squid, cf.data.pre (logformat). https://github.com/squid-cache/squid/blob/master/src/cf.data.pre
19. tcpflow(1) 매뉴얼. https://github.com/simsong/tcpflow/blob/master/doc/tcpflow.1.in
