---
title: "피싱 링크를 눌렀나"
parent: "시나리오 · 사용자 행위"
nav_order: 510
---

# 피싱 링크를 눌렀나 (Phishing Click)

메일로 받은 링크를 사용자가 열었는지, 연 뒤에 파일을 받거나 계정 정보를 보냈는지를 네트워크 기록으로 확인하는 순서를 다룹니다. 네트워크 기록으로 확인되는 것은 "이 시간대에 이 내부 IP 가 이 호스트 이름이나 URL 로 요청을 보냈고 서버가 이렇게 답했다" 까지이고, 사람이 직접 눌렀는지와 그 IP 를 누가 썼는지는 따로 판단합니다. 각 로그의 필드 설명은 아티팩트 페이지에 있고, 여기서는 어느 필드를 어떤 순서로 보는지만 씁니다.

## 조사 질문

- 피싱 메일이 언제, 누구에게 들어왔나?
- 받은 사람의 PC 가 메일 속 링크의 호스트로 연결했나? 몇 시에, 몇 번?
- 그 요청이 다른 주소로 넘겨졌나(리다이렉트), 마지막으로 어느 페이지에 닿았나?
- 그 페이지에서 파일을 내려받았나, 또는 무언가를 입력해 보냈나(POST)?
- 그 뒤 같은 PC 에서 처음 보는 외부 주소로 새 연결이 생겼나?
- 이 요청을 사람이 눌러서 보냈나, 프로그램이 자동으로 보냈나?

## 먼저 확인할 것

**링크가 HTTP 인지 HTTPS 인지부터 봅니다.** Zeek 의 http.log 는 평문 HTTP 이거나, HTTPS 를 풀어서 HTTP 로 보여 주는 장비 뒤에서만 채워집니다[1]. HTTPS 링크라면 복호화 없이 남는 것은 ssl.log 의 `server_name`(TLS 의 SNI 확장 값)과 연결 시각 정도이고, 경로(URI)·Referer·POST 본문은 없습니다[3]. QUIC(HTTP/3)으로 연결했으면 Zeek 6.1 부터 생긴 quic.log 의 `server_name` 을 봅니다[5]. 조사 대상 환경에 TLS 키 로그 파일이 이미 있을 때 쓰는 법은 [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md) 에 있습니다.

**센서가 프록시 앞에 있는지 뒤에 있는지 확인합니다.** 센서가 웹 프록시와 인터넷 사이에 있으면 모든 요청의 출발지가 프록시 IP 로 남습니다. Zeek http.log 의 `proxied` 필드에는 프록시를 거친 요청임을 나타낼 수 있는 헤더(기본 목록은 CLIENT-IP, X-FORWARDED-FROM, VIA, XROXY-CONNECTION, PROXY-CONNECTION, X-FORWARDED-FOR, FORWARDED)가 모입니다[2]. 다만 Forwarded 같은 헤더는 요청을 보낸 클라이언트를 포함해 경로의 어느 노드든 바꿀 수 있어서 그대로 믿을 수 없습니다[15]. 이럴 때는 프록시 자체의 access.log 가 더 정확한 출발지를 줍니다.

**로그 설정을 확인합니다.** 같은 도구라도 설정에 따라 남는 필드가 다릅니다.

| 기록 | Referer | 호스트 이름(HTTPS) | 확인할 설정 |
|---|---|---|---|
| Zeek http.log | `referrer` 필드(기본으로 남음)[2] | 해당 없음 | 없음 |
| Zeek ssl.log | 없음 | `server_name`[3] | 없음 |
| Suricata EVE `http` | `http_refer` 는 `extended: yes` 일 때만[11] | 해당 없음 | `eve-log` 의 `http` 항목 |
| Suricata EVE `tls` | 없음 | `sni` 는 extended 일 때만[11] | `eve-log` 의 `tls` 항목 |
| Squid access.log | 기본 `squid` 형식에는 없음. `combined`·`referrer` 형식에만 있음[12] | 기본 형식에는 없음. `ssl::>sni` 코드를 넣은 형식에만 있음[12] | `access_log`·`logformat` 줄 |

Squid 의 `access_log` 기본값은 `daemon:@DEFAULT_ACCESS_LOG@ squid` 이라서 따로 바꾸지 않았다면 Referer 와 User-Agent 가 없는 `squid` 형식입니다[12].

**로그마다 시각이 가리키는 시점과 시간대를 맞춥니다.**

| 기록 | 시각 필드 | 가리키는 시점 | 시간대 |
|---|---|---|---|
| Zeek smtp.log | `ts` | 메시지를 처음 본 시각[7] | UTC. 출력 설정에 따라 에포크 초나 ISO 8601(`Z` 로 끝남) 형식[1][22] |
| Zeek dns.log | `ts` | 그 연결에서 DNS 메시지를 처음 본 시각[9] | 위와 같음 |
| Zeek conn.log | `ts` | 연결의 첫 패킷 시각[8] | 위와 같음 |
| Zeek http.log | `ts` | 요청 시각[2] | 위와 같음 |
| Zeek ssl.log | `ts` | TLS 연결을 처음 알아챈 시각[3] | 위와 같음 |
| Zeek files.log | `ts` | 파일을 처음 본 시각[10] | 위와 같음 |
| Suricata EVE | `timestamp` | 이벤트 시각 | `+0100` 같은 UTC 오프셋이 붙은 시각[11] |
| Squid 기본 형식 | 첫 필드 `%ts.%03tu` | 로그를 쓰는 시각 | 에포크 초와 밀리초[12] |
| Squid `common`·`combined` | `%tl` | 로그를 쓰는 시각 | 현지 시각과 오프셋(`%d/%b/%Y:%H:%M:%S %z`)[12] |

Squid 는 완전한 요청 헤더를 받은 때를 트랜잭션 시작 시각(`%tS`)으로 보고, 응답 시간 `%tr`(밀리초)을 이 시각에서 계산합니다[12]. 그래서 기본 형식의 첫 필드에서 `%tr` 을 빼면 요청 시작 시각을 추정할 수 있습니다. 시각 전반의 해석은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | Zeek smtp.log·files.log, 메일 서버 기록 | 메일이 들어온 시각, 받는 사람, 제목, 본문·첨부 파일 ID | [메일 프로토콜](../../01-foundations/protocols/mail-protocols.md) |
| 2 | Zeek dns.log, DNS 서버 로그 | 링크 호스트 이름을 조회한 내부 IP 와 시각 | [DNS 분석](../../03-techniques/analysis/dns-analysis.md), [DNS 서버 로그](../../02-artifacts/devices/dns-server-logs.md) |
| 3 | Zeek conn.log, 흐름 기록 | 그 호스트의 IP 로 연결을 연 시각과 주고받은 크기 | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md), [흐름 기록](../../01-foundations/records/flow-records.md) |
| 4 | Zeek http.log·ssl.log·quic.log, Suricata EVE `http`·`tls` | 요청한 호스트·URI·Referer·상태 코드, HTTPS 면 SNI | [HTTP](../../01-foundations/protocols/http.md), [TLS와 인증서](../../01-foundations/protocols/tls.md), [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md) |
| 5 | 웹 프록시 access.log | 출발지 IP, 인증했으면 사용자 이름, 요청 URL, 응답 코드 | [웹 프록시 로그 (Squid)](../../02-artifacts/devices/proxy-logs.md) |
| 6 | Zeek files.log, Suricata EVE `fileinfo`, 패킷 캡처 | 내려받은 파일의 형식·크기·해시, POST 본문 | [세션 복원과 파일 꺼내기](../../03-techniques/analysis/file-extraction.md) |
| 7 | conn.log, 흐름 기록, 방화벽 로그 | 클릭 뒤에 새로 생긴 외부 연결 | [악성 코드가 C2 서버와 통신했나](../intrusion/c2-communication.md) |
| 8 | DHCP·VPN·인증 기록 | 그 시각에 그 내부 IP 를 쓴 기기와 계정 | [이 시각에 이 IP 를 누가 썼나](ip-attribution.md) |

## 분석 흐름

1. **메일에서 링크와 받는 사람을 찾습니다.** 평문 SMTP(25/tcp)라면 Zeek smtp.log 에 `mailfrom`, `rcptto`, `from`, `to`, `subject`, `msg_id`, `x_originating_ip` 같은 필드가 남고, `fuids` 로 본문과 첨부가 files.log 에 이어집니다[7]. 파일 추출을 켜 두었으면 `SMTP-` 로 시작하는 이름의 본문 파일이 생기므로 그 안에서 링크 URL 을 찾습니다[6]. 465·587 포트는 TLS 로 암호화돼 개별 메일이 보이지 않고, 465 연결은 conn.log 에 `service` 가 `ssl` 로만 남습니다[6]. 이때는 메일 서버의 기록이나 받은 사람 PC 의 메일 데이터에서 링크를 구합니다.

2. **링크의 호스트 이름으로 이름 조회와 연결을 찾습니다.** dns.log 에서 그 이름을 조회한 내부 IP 를 모으고, conn.log 에서 같은 내부 IP 가 응답 IP 로 연결한 기록을 찾습니다. 메일이 들어온 시각보다 앞선 기록은 이 메일과 무관한 방문일 수 있으므로 따로 둡니다. HTTPS 이면서 ESNI(Encrypted Server Name Indication)나 ECH(Encrypted Client Hello)를 쓰면 ssl.log 에 `server_name` 이 남지 않고, 같은 방문이 DNS over HTTPS(DoH)를 쓰면 dns.log 에도 그 이름이 없습니다[4]. 이 경우에는 호스트 이름 대신 응답 IP 와 시각으로 찾아야 하고, 한 IP 에 여러 사이트가 있을 수 있어 결과가 약해집니다.

3. **요청 하나하나를 http.log 에서 봅니다.** 같은 연결은 `uid` 로 conn.log·files.log 와 이어집니다[2]. 보는 필드는 `ts`, `id.orig_h`, `method`, `host`, `uri`, `referrer`, `user_agent`, `status_code`, `request_body_len`, `response_body_len`, `resp_mime_types`, `resp_fuids` 입니다[2]. 호스트 이름은 `host` 에, 경로는 `uri` 에 따로 남으므로 전체 URL 은 두 필드를 합쳐 만듭니다[1]. 아래는 만든 예시입니다.

   ```json
   {"ts":1773619961.204113,"uid":"CYq3Tb1Hk2wPz8uLa5","id.orig_h":"10.20.30.41","id.orig_p":52814,"id.resp_h":"198.51.100.23","id.resp_p":80,"trans_depth":1,"method":"GET","host":"track.example.net","uri":"/r/a8f2c1","version":"1.1","user_agent":"Mozilla/5.0","request_body_len":0,"response_body_len":0,"status_code":302,"status_msg":"Found","tags":[]}
   {"ts":1773619961.611502,"uid":"CmR8vX2dQe4Hn7sJb1","id.orig_h":"10.20.30.41","id.orig_p":52816,"id.resp_h":"203.0.113.80","id.resp_p":80,"trans_depth":1,"method":"GET","host":"login.example.com","uri":"/account/verify","version":"1.1","user_agent":"Mozilla/5.0","request_body_len":0,"response_body_len":5120,"status_code":200,"status_msg":"OK","tags":[],"resp_fuids":["FpL0x4bQ2mV9cT7aZ3"],"resp_mime_types":["text/html"]}
   {"ts":1773619993.087224,"uid":"CmR8vX2dQe4Hn7sJb1","id.orig_h":"10.20.30.41","id.orig_p":52816,"id.resp_h":"203.0.113.80","id.resp_p":80,"trans_depth":2,"method":"POST","host":"login.example.com","uri":"/account/submit","referrer":"http://login.example.com/account/verify","version":"1.1","user_agent":"Mozilla/5.0","request_body_len":46,"response_body_len":312,"status_code":200,"status_msg":"OK","tags":[]}
   ```

4. **리다이렉트를 이어 붙입니다.** http.log 에는 응답의 `Location` 헤더가 없어서 넘겨진 주소가 바로 보이지 않습니다[1][2]. 3xx 응답 바로 뒤에 같은 내부 IP 가 보낸 다음 요청을 시각과 `referrer` 로 이어 붙이고, 확실히 해야 하면 패킷 캡처에서 3xx 응답의 `Location` 을 읽습니다. Suricata 는 `custom` 목록에 `location` 을 넣었거나 `dump-all-headers` 를 켰을 때만 이 헤더가 EVE 에 남습니다[11]. 악성 파일을 내려받기까지의 경로를 연구한 WebWitness 는 대학 네트워크에서 모은 사례 가운데 Referer 와 Location 만으로 경로를 끝까지 이은 비율이 사회 공학형 내려받기 41건 중 53%, 드라이브바이 164건 중 0% 였고, 응답 본문에 다음 URL 이 있는지·같은 도메인에서 짧은 간격으로 이어졌는지 같은 근거를 더하면 95%·96% 까지 이었습니다[21]. 사회 공학형 경로가 끊긴 주된 원인은 JavaScript 나 브라우저 플러그인이 만든 요청이었으므로, 끊긴 곳은 앞 응답 본문을 files.log 나 패킷에서 꺼내 다음 URL 이 들어 있는지 봅니다[21].

5. **파일을 받았는지 봅니다.** http.log 의 `resp_fuids` 를 files.log 의 `fuid` 로 찾으면 파일의 MIME 형식과 크기가 나오고, 파일 추출을 설정했으면 내용도 볼 수 있습니다[1][10]. Suricata EVE `fileinfo` 에는 `filename`, `magic`(libmagic 이 있을 때), `size`, `sha256`, `stored` 가 남고, `md5`·`sha1`·`sha256` 은 `disable-hashing` 옵션을 쓰지 않았고 빠진 구간(`gaps`)이 없을 때만 있습니다[11]. 해시로 받은 사람 PC 에 남은 파일과 맞춰 봅니다.

6. **무언가를 보냈는지 봅니다.** `method` 가 POST 이고 `request_body_len` 이 0 보다 크면 그 페이지로 무언가를 보냈다는 것까지 알 수 있습니다[2]. 보낸 내용은 `orig_fuids` 로 추출된 파일이나 패킷 캡처에만 있습니다. Basic 인증 비밀번호를 담는 `password` 필드는 `HTTP::default_capture_password` 의 기본값이 `F` 라서 기본으로는 비어 있습니다[2]. 입력 양식으로 보낸 계정 정보가 실제로 쓰였는지는 그 계정의 로그인 기록으로 확인합니다.

7. **클릭 뒤의 연결을 봅니다.** 같은 내부 IP 가 클릭 뒤에 그전에 연결한 적 없는 외부 주소로 새 연결을 열었는지 conn.log 와 흐름 기록에서 찾습니다. 반복 연결의 판단은 [악성 코드가 C2 서버와 통신했나](../intrusion/c2-communication.md) 를 따릅니다.

8. **탐지 규칙으로 넓혀 봅니다.** Sigma 에는 Zeek http.log 의 `host` 가 평판이 낮은 최상위 도메인으로 끝나고 `uri` 가 `.exe`·`.hta`·`.iso`·`.lnk` 같은 확장자로 끝나거나 `resp_mime_types` 가 `application/x-dosexec` 같은 실행 파일 형식인 요청을 찾는 규칙이 있습니다[18]. 프록시 로그용으로는 `c-uri-extension` 과 `cs-host` 로 같은 일을 하는 규칙[19], IPFS 에 올린 계정 정보 수집 페이지 URL 안에 이메일 주소가 든 것을 찾는 규칙이 있습니다[17]. 규칙마다 URL 필드 이름이 `c-uri`(분류 표 기준)와 `cs-uri`(IPFS 규칙)로 달라서, 쓰는 SIEM 의 필드 매핑을 먼저 확인합니다[16][17]. 규칙을 다루는 법은 [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md) 에 있습니다.

9. **요청한 IP 를 사람으로 잇습니다.** 프록시에서 인증을 받는다면 Squid `%un` 코드가 인증 이름·외부 ACL 이름·SSL 클라이언트 이름 가운데 처음 있는 값을 남기므로 계정까지 바로 이어집니다[12]. 그렇지 않으면 DHCP·VPN·인증 기록으로 그 시각의 내부 IP 사용자를 찾습니다([이 시각에 이 IP 를 누가 썼나](ip-attribution.md)). 같은 방문이 브라우저 기록에도 남았는지는 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/)·[파이어폭스](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/firefox/) 페이지를 따릅니다.

아래는 3단계 예시와 같은 요청이 Squid 기본 `squid` 형식에 남은 모양입니다(만든 예시). 필드는 순서대로 기록 시각, 응답 시간(ms), 클라이언트 IP, 상태/HTTP 코드, 응답 크기, 메서드, URL, 사용자 이름, 계층 상태/서버 주소, MIME 형식입니다[12].

```text
1773619961.921    310 10.20.30.41 TCP_MISS/200 5120 GET http://login.example.com/account/verify - HIER_DIRECT/203.0.113.80 text/html
```

## 흔한 오판

**요청이 있으니 사람이 눌렀다고 판단합니다.** 네트워크 기록에는 요청이 있을 뿐, 누가 어떤 동작으로 그 요청을 만들었는지는 없습니다. 사람이 누른 요청과 브라우저가 페이지를 그리려고 딸려 보낸 요청을 나누는 일은 그 자체로 연구 주제입니다. ReSurf 는 Referer 로 요청을 이은 그래프에서 HTML·XML 객체이고, 3000바이트보다 크고, 딸린 객체가 2개 이상이고, Referer 로 가리킨 요청과 0.5초 넘게 떨어진 요청을 사람이 누른 요청 후보로 골랐습니다. 이 방식은 실제 네트워크 트레이스 4개에서 재현율 91% 이상, 정밀도 95% 이상이었지만 HTTP 헤더를 쓰므로 HTTPS 요청은 분류하지 못합니다[20]. 사람이 눌렀다는 판단은 받은 사람 PC 의 브라우저·메일 프로그램 기록과 함께 내립니다.

**Referer 가 없으니 주소를 직접 입력했다고 봅니다.** 키보드 입력이나 즐겨찾기처럼 자기 URI 가 없는 곳에서 연 주소면 브라우저는 Referer 를 빼거나 `about:blank` 로 보내야 합니다[13]. 메일 프로그램에서 연 링크도 이 경우에 들어갈 수 있습니다. 보안 연결(HTTPS)로 받은 페이지에서 평문 HTTP 로 요청하면 Referer 를 보내면 안 되고, 중간 장비가 Referer 를 지우는 일도 있습니다[13]. `no-referrer` 정책이나 `noreferrer` 링크도 Referer 를 없앱니다[14]. 그래서 Referer 가 없다는 것만으로 입력 방법을 정할 수 없습니다.

**Referer 에 웹메일 주소 전체가 남는다고 기대합니다.** 브라우저의 기본 정책 `strict-origin-when-cross-origin` 에서는 다른 origin 으로 갈 때 Referer 에 origin(예: `https://mail.example.com/`)만 남고, HTTPS 페이지에서 HTTP 로 갈 때는 아무것도 남지 않습니다[14]. RFC 9110 은 보안 연결로 받은 페이지에서 다른 origin 으로 갈 때 Referer 를 보내지 않도록 권하지만(SHOULD NOT)[13], W3C 기본 정책은 origin 만은 보냅니다[14]. 두 기준이 달라서, 실제 브라우저가 어느 쪽으로 보냈는지는 조사 대상 트래픽에서 확인합니다.

**Host 필드로 사용자가 간 사이트를 정합니다.** 페이지 하나를 열면 광고·추적·콘텐츠 전송 서버로 요청이 함께 나갑니다. ReSurf 의 트레이스에서 Host 필드만으로 사용자가 가려던 사이트를 고르면 20~40% 만 맞았고, 사용자 요청의 50~60% 가 추적이나 광고 서비스를 불렀습니다[20]. 링크의 호스트와 그 페이지가 딸려 부른 호스트를 구분해서 봅니다.

**설정 때문에 없는 필드를 "없었다" 로 읽습니다.** Suricata 의 `http_refer`·`sni` 는 extended 설정일 때만 있고[11], Squid 기본 형식에는 Referer 가 없습니다[12]. 필드가 비어 있으면 먼저 로그 설정을 봅니다.

**헤더 값을 그대로 믿습니다.** Referer, User-Agent, X-Forwarded-For 는 클라이언트가 보내는 값이라 바꿀 수 있습니다. Forwarded 헤더는 경로의 모든 노드가 바꿀 수 있어서 믿을 수 없는 값입니다[15].

## 보고서 문장 예

기록으로 확인되는 것은 "이 시각에 이 내부 IP(프록시 인증이 있으면 이 계정)가 이 호스트나 URL 로 요청했고, 서버가 이 상태 코드·크기·형식으로 답했다" 까지입니다. HTTPS 라면 "이 호스트 이름(SNI)으로 연결했다" 까지만 씁니다. 사람이 직접 눌렀는지, 그 IP 를 누가 썼는지, 보낸 내용이 무엇인지는 다른 기록과 함께 씁니다. 아래는 모두 만든 예시입니다.

- "2026-03-16 09:05:10(KST)에 외부 메일 서버가 10.20.1.5(사내 메일 서버)로 제목 '계정 확인 요청' 인 메일을 보낸 기록이 Zeek smtp.log 에 있고, 받는 사람은 user01@example.com 입니다. 본문 파일에 `http://track.example.net/r/a8f2c1` 링크가 들어 있습니다."
- "09:12:41(KST)에 10.20.30.41 이 track.example.net 에 이 링크 경로로 GET 요청을 보냈고, 서버는 302 로 답했습니다. 0.4초 뒤 같은 IP 가 login.example.com 의 `/account/verify` 를 요청해 200 응답과 text/html 5,120바이트를 받았습니다."
- "09:13:13(KST)에 같은 IP 가 login.example.com 의 `/account/submit` 로 46바이트 본문의 POST 요청을 보낸 기록이 있습니다. 본문의 내용은 패킷 캡처가 없어 이 기록만으로는 확인되지 않습니다."
- "09:00~10:00(KST) 사이 DHCP 서버 기록에서 10.20.30.41 을 할당받은 기기는 MAC 주소 00:00:5E:00:53:2A 인 PC 하나입니다."

## 함께 볼 페이지

- [이 시각에 이 IP 를 누가 썼나](ip-attribution.md) — 내부 IP 를 기기와 계정으로 잇기
- [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) — http.log·ssl.log·smtp.log·files.log 필드
- [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md) — http·tls·fileinfo 이벤트
- [웹 프록시 로그 (Squid)](../../02-artifacts/devices/proxy-logs.md) — logformat 코드와 기본 형식
- [HTTP](../../01-foundations/protocols/http.md), [TLS와 인증서](../../01-foundations/protocols/tls.md), [메일 프로토콜](../../01-foundations/protocols/mail-protocols.md)
- [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md)
- [세션 복원과 파일 꺼내기](../../03-techniques/analysis/file-extraction.md)
- [네트워크 타임라인](../../03-techniques/analysis/timeline.md)
- [악성 코드가 C2 서버와 통신했나](../intrusion/c2-communication.md)
- [크롬 계열 브라우저 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/), [파이어폭스 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/firefox/), [사파리 (macOS)](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/browsers/safari/) — 받은 사람 PC 의 방문 기록
- [AI로 피싱·사기 문구를 만들었나](https://urock-ailab.github.io/forensics-handbook/ai/04-scenarios/misuse/phishing.html) — 피싱 메일 문구를 만든 쪽의 흔적

## 참고 문헌

1. Zeek Project, Zeek Logs — http.log. https://github.com/zeek/zeek-docs/blob/master/logs/http.rst
2. Zeek Project, base/protocols/http/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/http/main.zeek.rst
3. Zeek Project, base/protocols/ssl/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/main.zeek.rst
4. Zeek Project, Zeek Logs — ssl.log. https://github.com/zeek/zeek-docs/blob/master/logs/ssl.rst
5. Zeek Project, Zeek Logs — quic.log. https://github.com/zeek/zeek-docs/blob/master/logs/quic.rst
6. Zeek Project, Zeek Logs — smtp.log. https://github.com/zeek/zeek-docs/blob/master/logs/smtp.rst
7. Zeek Project, base/protocols/smtp/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/smtp/main.zeek.rst
8. Zeek Project, base/protocols/conn/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
9. Zeek Project, base/protocols/dns/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dns/main.zeek.rst
10. Zeek Project, base/frameworks/files/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/frameworks/files/main.zeek.rst
11. OISF, Suricata User Guide — Eve JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
12. Squid Project, src/cf.data.pre (access_log·logformat). https://github.com/squid-cache/squid/blob/master/src/cf.data.pre
13. R. Fielding, M. Nottingham, J. Reschke, RFC 9110 HTTP Semantics, 10.1.3 Referer, 2022. https://www.rfc-editor.org/rfc/rfc9110.txt
14. W3C, Referrer Policy (Editor's Draft). https://w3c.github.io/webappsec-referrer-policy/
15. A. Petersson, M. Nilsson, RFC 7239 Forwarded HTTP Extension, 8.1 Header Validity and Integrity, 2014. https://www.rfc-editor.org/rfc/rfc7239.txt
16. SigmaHQ, Sigma Taxonomy Appendix. https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-appendix-taxonomy.md
17. SigmaHQ, Suspicious Network Communication With IPFS. https://github.com/SigmaHQ/sigma/blob/master/rules/web/proxy_generic/proxy_susp_ipfs_cred_harvest.yml
18. SigmaHQ, HTTP Request to Low Reputation TLD or Suspicious File Extension. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_susp_file_ext_from_susp_tld.yml
19. SigmaHQ, Download From Suspicious TLD - Blacklist. https://github.com/SigmaHQ/sigma/blob/master/rules/web/proxy_generic/proxy_download_susp_tlds_blacklist.yml
20. Guowu Xie, Marios Iliofotou, Thomas Karagiannis, Michalis Faloutsos, Yaohui Jin, "ReSurf: Reconstructing Web-Surfing Activity From Network Traffic", IFIP Networking Conference, 2013. https://ieeexplore.ieee.org/document/6663499
21. Terry Nelms, Roberto Perdisci, Manos Antonakakis, Mustaque Ahamad, "WebWitness: Investigating, Categorizing, and Mitigating Malware Download Paths", 24th USENIX Security Symposium, 2015, pp.1025–1040. https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/nelms
22. Zeek Project, Zeek Logs — dhcp.log. https://github.com/zeek/zeek-docs/blob/master/logs/dhcp.rst
