---
title: "웹 프록시 로그"
parent: "아티팩트 · 네트워크 장비와 서버 로그"
nav_order: 260
---

# 웹 프록시 로그 (Squid)

웹 프록시(Web Proxy)는 내부 PC 의 웹 요청을 받아 대신 바깥 서버에 접속하고, 요청이 끝날 때마다 access.log 에 한 줄을 남깁니다. 그 한 줄로 어느 내부 주소가 언제 어느 URL 이나 `호스트:포트` 로 요청했고, 프록시가 허용·거부·캐시·터널 가운데 무엇으로 처리했으며, 클라이언트에 몇 바이트를 돌려줬는지 알 수 있습니다. 이 페이지는 오픈 소스 프록시 서버 Squid 를 예로 access.log 의 형식과 기록 시점, 한 줄로 주장할 수 있는 범위를 다룹니다.

## 무엇을 기록하나 · 왜 생기나

프록시를 쓰는 망에서는 PC 가 바깥 서버에 직접 붙지 않고 프록시에 요청을 보냅니다. 그래서 방화벽이나 흐름 기록에는 "PC → 프록시", "프록시 → 바깥 서버" 두 연결이 따로 남고, 둘을 이어 주는 기록이 프록시 로그입니다. Squid 는 access_log 설정에 맞는 HTTP·ICP 요청마다 한 줄을 씁니다[1].

Squid 가 남기는 파일은 여럿이고, 조사에서 쓰임새가 다릅니다.

| 파일 | 내용 | 기본 상태 |
|---|---|---|
| access.log | 요청 하나에 한 줄. 조사의 중심 기록 | 켜짐[1] |
| cache.log | 시작·설정·오류 메시지. FATAL, ERROR, WARNING, SECURITY ERROR, SECURITY ALERT, SECURITY NOTICE 같은 머리말이 붙음 | 켜짐[1][2] |
| store.log | 캐시에 저장·삭제한 객체의 기록. 개발자들도 디버그용으로 보라고 권함 | 꺼짐(`cache_store_log none`)[1][2] |
| swap.state | 디스크 캐시의 색인 저널. 캐시 객체마다 MD5 해시를 씀 | 캐시 디렉터리마다 있음[1][2] |
| icap_log | ICAP 서버와 주고받은 기록 | 꺼짐(`icap_log none`). ICAP 을 넣어 빌드해야 쓸 수 있음[1] |

예전의 useragent.log 는 Squid 3.2 부터 따로 있는 파일이 아니라 access.log 형식 가운데 하나가 됐습니다[2]. cache.log 는 요청 단위 기록은 아니지만, Squid 가 멈춘 시각(FATAL)이나 설정을 다시 읽은 시각을 찾을 때 access.log 의 빈 구간과 맞춰 봅니다.

HTTPS 는 기록되는 모양이 다릅니다. 브라우저는 프록시에 `CONNECT www.example.com:443` 처럼 호스트와 포트만 담은 요청을 보내고, 2xx 응답을 받은 뒤부터 프록시는 양쪽 데이터를 그대로 넘기는 터널이 됩니다[9]. Squid 는 이런 요청을 결과 코드 `TCP_TUNNEL` 로 기록합니다[2][5]. 암호를 풀어 내용을 보는 SslBump 는 `http_port`·`https_port` 에 `ssl-bump` 를 달아야 동작하고, 이때도 규칙이 없으면 기본 동작이 암호를 풀지 않는 터널(`splice`)입니다[1]. 그래서 기본 설정의 HTTPS 요청은 access.log 에 `CONNECT 호스트:443` 한 줄로만 남고 경로와 쿼리는 없습니다. TLS 자체는 [TLS와 인증서](../../01-foundations/protocols/tls.md) 페이지에서 다룹니다.

## 위치와 버전별 차이

### 파일 위치와 설정

access.log 의 기본 설정은 `access_log daemon:@DEFAULT_ACCESS_LOG@ squid` 이고, `@DEFAULT_ACCESS_LOG@` 는 빌드할 때 실제 경로로 바뀝니다[1][8]. cache.log 와 설정 파일 squid.conf 도 마찬가지라서, 실제 경로는 배포판과 빌드 옵션마다 다릅니다[1][7]. 분석 대상에서는 squid.conf 를 먼저 찾아 다음 지시어를 확인합니다.

| 지시어 | 확인할 것 | 기본값 |
|---|---|---|
| `access_log` | 파일 경로, 기록 모듈, 형식 이름, 요청 일부만 남기는 ACL | `daemon:… squid`[1] |
| `logformat` | 직접 정의한 형식이 있는지, 어떤 코드를 넣었는지 | 기본 형식 5개[1] |
| `cache_log` | cache.log 경로 | 빌드 때 정함[1] |
| `logfile_rotate` | 교대로 남기는 이전 파일 개수 | 10[1] |
| `strip_query_terms` | URL 의 쿼리를 지우고 기록하는지 | on[1] |
| `client_netmask` | 클라이언트 주소를 줄여 기록하는지 | 전체 주소[1] |
| `follow_x_forwarded_for`, `log_uses_indirect_client` | 클라이언트 주소 대신 X-Forwarded-For 값을 쓰는지 | deny all, on[1] |
| `log_mime_hdrs` | 요청·응답 헤더를 줄 끝에 붙이는지 | off[1] |
| `cache_store_log` | store.log 를 켰는지 | none[1] |

설정 사본을 Squid 로 검사할 때는 `squid -k parse -f squid.conf` 를 씁니다. `-k parse` 는 설정 파일만 읽어 검사하고, 다른 `-k` 명령과 달리 실행 중인 Squid 에 신호를 보내지 않습니다[7].

### 기록 모듈

`access_log` 의 앞부분 `모듈:위치` 에 따라 기록이 가는 곳이 달라집니다[1]. 수집할 때는 모듈부터 확인해야 파일이 없는 이유를 알 수 있습니다.

| 모듈 | 기록 방법 |
|---|---|
| `stdio` | 요청이 끝날 때마다 바로 디스크에 씀 |
| `daemon` | 도우미 프로세스에 넘겨 따로 씀(기본값) |
| `syslog` | `facility.priority` 로 syslog 에 보냄 |
| `udp`, `tcp` | `//host:port` 의 수집 서버로 한 줄씩 보냄 |
| `none` | 맞는 요청을 기록하지 않음 |

`buffered_logs` 를 켜면 여러 줄을 모아 한꺼번에 쓰는데, 이 설정은 `daemon`·`tcp`·`udp` 모듈에만 적용되고 늦게 쓰는 만큼 기록을 잃을 위험이 커집니다[1]. `syslog` 모듈로 보냈다면 줄 앞에 syslog 머리말과 그 시각이 한 번 더 붙으므로, 두 시각을 읽는 법은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에서 봅니다. 중앙 수집 서버로 보내는 구성은 [로그 수집과 보존](../../03-techniques/acquisition/log-collection.md) 에서 다룹니다.

### 교대와 보존

`squid -k rotate` 를 실행하면 현재 파일을 닫고 `.0`, `.1` … 번호를 붙여 이름을 바꿉니다[2]. 기본값 `logfile_rotate 10` 이면 `.0` 부터 `.9` 까지 10개만 남고, 더 오래된 파일은 사라집니다[1][2]. Squid-4 부터 `logfile_rotate` 는 `stdio` 모듈로 쓰는 access.log 의 기본값일 뿐이고, 각 `access_log` 줄의 `rotate=N` 옵션으로 따로 정할 수 있습니다(`stdio` 모듈만)[1]. `logfile_rotate 0` 이면 Squid 는 파일을 닫았다 다시 열기만 하고, 이름 바꾸기는 logrotate 같은 바깥 도구가 맡습니다[2].

### 버전별 차이

| 버전 | 바뀐 점 |
|---|---|
| Squid 2.6 | `logformat` 으로 로그 형식을 직접 정할 수 있게 됨[3] |
| Squid 3.2 | useragent.log 가 access.log 형식 가운데 하나(`useragent`)로 바뀜[2] |
| Squid-4 | `logfile_rotate` 가 `stdio` access.log 에만 기본값으로 적용됨[1] |
| Squid v5 (2018-06-18 커밋) | 결과 코드에 `_CF`(요청 합치기, collapsed forwarding) 태그 추가[2][5] |
| Squid v6 | `_ABORTED` 가 서버·피어와 통신하지 못하거나 중간에 끊긴 경우에도 붙음. 그 전에는 주로 클라이언트가 먼저 끊은 경우[2] |

기본 형식의 계층 필드에 찍히는 서버 주소도 달라졌습니다. 옛 버전은 원 서버의 호스트 이름을, 요즘 버전은 IP 주소를 씁니다[3].

## 구조

### 기본 형식(squid) 한 줄

별도 설정이 없으면 access.log 는 Squid 고유 형식(native, 형식 이름 `squid`)으로 쓰입니다[1]. 형식 정의는 다음과 같습니다[1].

```text
logformat squid      %ts.%03tu %6tr %>a %Ss/%03>Hs %<st %rm %ru %[un %Sh/%<a %mt
```

다음은 이 형식으로 만든 세 줄입니다(만든 예시).

```text
1772446529.880 1843210 192.168.10.23 TCP_TUNNEL/200 48213 CONNECT www.example.com:443 - HIER_DIRECT/203.0.113.10 -
1772446530.512     87 192.168.10.23 TCP_MISS/200 1830 GET http://www.example.net/index.html - HIER_DIRECT/198.51.100.7 text/html
1772446531.004      0 192.168.10.23 TCP_DENIED/403 3894 CONNECT upload.example.org:443 - HIER_NONE/- text/html
```

필드는 공백으로 나뉘며 10개입니다[3][4]. 두 번째 필드는 여섯 자리 폭에 오른쪽 정렬이라 값이 짧으면 앞에 공백이 여러 개 들어가고, 여섯 자리를 넘으면 공백이 하나뿐입니다[4].

| 순서 | 필드 | 뜻 |
|---|---|---|
| 1 | 시각 | 1970-01-01 UTC 기준 초와 밀리초. 줄을 쓰기 시작한 시각이라 보통 요청이 끝난 때(아래 "시각 해석")[3][4] |
| 2 | 걸린 시간 | 밀리초. HTTP 는 요청을 받은 때부터 응답의 마지막 바이트를 보낸 때까지[3] |
| 3 | 클라이언트 주소 | 요청을 보낸 IP. `client_netmask` 나 X-Forwarded-For 설정에 따라 바뀔 수 있음[1][3] |
| 4 | 결과 코드/상태 | Squid 결과 코드와 HTTP 상태 코드 세 자리를 `/` 로 이음[3][4] |
| 5 | 바이트 | 클라이언트에 보낸 양. 헤더와 오류 페이지 크기까지 포함[3][4] |
| 6 | 메서드 | GET, POST, CONNECT 등[3] |
| 7 | URL | 요청 URL. CONNECT 는 `호스트:포트`. 기본 설정에서는 쿼리를 지운 값[1][3] |
| 8 | 사용자 | 인증 이름 → 외부 ACL 이 준 이름 → TLS 클라이언트 이름 순서로 처음 있는 값, 없으면 `-`[1][4] |
| 9 | 계층 코드/서버 | 요청을 어떻게 넘겼는지와 마지막으로 연결한 서버·피어의 IP. 없으면 `-`[1][4] |
| 10 | 형식 | 응답의 Content-Type, 없으면 `-`[3] |

`log_mime_hdrs on` 이면 줄 끝에 요청 헤더와 응답 헤더가 `[...] [...]` 두 필드로 더 붙습니다[1][4]. 이 헤더 안의 줄바꿈 같은 제어 문자는 `%` 로 인코딩되지만 공백은 그대로라서, 공백으로 필드를 나누는 도구는 11번째 필드부터 틀리게 읽습니다[1][3]. 앞의 10개 필드는 영향을 받지 않습니다.

### 결과 코드

결과 코드는 `TCP`·`UDP`·`NONE` 가운데 하나로 시작하고, 밑줄로 태그를 이어 붙입니다[2]. 소스 코드에 들어 있는 기본 문자열은 다음과 같습니다[5].

| 분류 | 문자열 |
|---|---|
| 캐시에서 줌 | `TCP_HIT`, `TCP_MEM_HIT`, `TCP_IMS_HIT`, `TCP_INM_HIT`, `TCP_NEGATIVE_HIT`, `TCP_OFFLINE_HIT` |
| 서버에서 받아 옴 | `TCP_MISS`, `TCP_CLIENT_REFRESH_MISS`, `TCP_SWAPFAIL_MISS` |
| 캐시를 서버에 다시 확인 | `TCP_REFRESH`, `TCP_REFRESH_UNMODIFIED`, `TCP_REFRESH_MODIFIED`, `TCP_REFRESH_FAIL_OLD`, `TCP_REFRESH_FAIL_ERR` |
| 거부·전환 | `TCP_DENIED`, `TCP_DENIED_REPLY`, `TCP_REDIRECT` |
| 터널 | `TCP_TUNNEL` |
| ICP | `UDP_HIT`, `UDP_MISS`, `UDP_DENIED`, `UDP_INVALID`, `UDP_MISS_NOFETCH`, `ICP_QUERY` |

여기에 요청 합치기 태그 `_CF` 가 가운데에, 오류 태그 `_IGNORED`, `_TIMEDOUT`, `_ABORTED` 가 끝에 붙을 수 있습니다[5]. 예를 들어 `TCP_MISS_ABORTED/200` 은 서버에서 받아 온 요청이 중간에 끊겼다는 뜻인데, Squid v6 전에는 주로 클라이언트가 먼저 끊은 경우입니다[2]. 분류되기 전에 끝난 요청은 `NONE` 으로 시작하는데, 소스대로라면 `NONE_NONE` 으로 찍힙니다[5]. 위키에는 ASYNC, STALE, SHARED 같은 태그 설명도 있지만 현재 소스의 문자열 목록에는 없으므로[2][5], 이런 태그가 보이면 그 Squid 의 버전을 먼저 확인합니다.

상태 코드 자리에는 HTTP 상태 말고도 Squid 가 쓰는 값이 있습니다. `000` 은 결과 코드가 없는 경우(주로 UDP), `600` 은 헤더를 해석하지 못한 경우, `601` 은 헤더가 너무 큰 경우입니다[2].

### 계층 코드

9번째 필드의 앞부분은 요청을 원 서버로 바로 보냈는지(`HIER_DIRECT`), 상위 프록시(parent)나 이웃 캐시(sibling)로 넘겼는지, 서버로 넘기지 않았는지(`HIER_NONE`, 캐시 적중·실패·거부 등)를 나타냅니다. 로그에 찍히는 문자열은 소스의 이름 그대로이며, `HIER_NONE`, `HIER_DIRECT`, `SIBLING_HIT`, `PARENT_HIT`, `DEFAULT_PARENT`, `SINGLE_PARENT`, `FIRSTUP_PARENT`, `FIRST_PARENT_MISS`, `CLOSEST_PARENT_MISS`, `CLOSEST_PARENT`, `CLOSEST_DIRECT`, `NO_DIRECT_FAIL`, `SOURCE_FASTEST`, `ROUNDROBIN_PARENT`, `CD_PARENT_HIT`·`CD_SIBLING_HIT`(캐시 다이제스트를 넣어 빌드했을 때), `CARP`, `ANY_OLD_PARENT`, `USERHASH_PARENT`, `SOURCEHASH_PARENT`, `PINNED`, `ORIGINAL_DST`, `STANDBY_POOL` 이 있습니다[6]. ICP 응답을 기다리다 시간이 다 되면 앞에 `TIMEOUT_` 이 붙습니다[3][4].

두 출처가 다른 곳이 있습니다. Squid 위키는 계층 코드를 `NONE`, `DIRECT`, `FIRST_UP_PARENT` 로 적고, 이웃 캐시로 보낸 경우 `/` 뒤에 이웃의 호스트 이름이 온다고 설명합니다[2][3]. 소스 코드는 `HIER_` 가 붙은 이름을 쓰고, `/` 뒤에는 마지막으로 연결한 서버·피어의 IP 주소를 찍습니다[4][6]. 검색 조건을 만들 때는 분석 대상 로그에 실제로 찍힌 문자열을 먼저 확인합니다.

### 다른 기본 형식과 직접 정한 형식

`squid` 말고도 네 가지 형식이 기본으로 들어 있습니다[1].

| 형식 이름 | 정의 |
|---|---|
| `common` | `%>a - %[un [%tl] "%rm %ru HTTP/%rv" %>Hs %<st %Ss:%Sh` |
| `combined` | `%>a - %[un [%tl] "%rm %ru HTTP/%rv" %>Hs %<st "%{Referer}>h" "%{User-Agent}>h" %Ss:%Sh` |
| `referrer` | `%ts.%03tu %>a %{Referer}>h %ru` |
| `useragent` | `%>a [%tl] "%{User-Agent}>h"` |

`common` 과 `combined` 은 이름은 웹 서버 형식과 같지만, 끝에 `결과 코드:계층 코드` 가 더 붙어서 Apache 정의와 정확히 같지 않습니다[1]. 웹 서버용 분석 도구에 넣으면 마지막 필드가 남을 수 있습니다. `common` 형식 한 줄은 다음과 같습니다(만든 예시).

```text
192.168.10.23 - - [02/Mar/2026:19:15:30 +0900] "GET http://www.example.net/index.html HTTP/1.1" 200 1830 TCP_MISS:HIER_DIRECT
```

관리자가 `logformat` 으로 형식을 직접 정했다면 다음 코드가 들어갔는지 봅니다. 조사에서 기본 형식에 없는 정보를 채워 주는 코드들입니다[1].

| 코드 | 뜻 |
|---|---|
| `%>st`, `%<st`, `%st` | 클라이언트에게서 받은 요청 총량, 클라이언트에 보낸 응답 총량, 둘의 합 |
| `%tS` | 요청 헤더를 다 받은 시각(트랜잭션 시작, 밀리초 단위) |
| `%tl`, `%tg` | 현지 시각, GMT 시각(기본 `%d/%b/%Y:%H:%M:%S %z`) |
| `%dt` | DNS 조회에 걸린 시간(밀리초) |
| `%>p`, `%>eui` | 클라이언트 포트, 클라이언트 MAC 주소 |
| `%>la`, `%>lp` | 클라이언트가 접속한 프록시의 주소·포트 |
| `%<a`, `%<p`, `%<la`, `%<lp` | 마지막 서버·피어 주소·포트와 그 연결에 쓴 프록시 쪽 주소·포트 |
| `%ul`, `%ue` | 인증으로 얻은 이름, 외부 ACL 이 준 이름 |
| `%ssl::bump_mode` | SslBump 결정(`splice`, `bump`, `peek`, `stare`, `terminate`, `server-first`, `client-first`, 또는 `none`, `-`) |
| `%ssl::>sni` | 클라이언트가 보낸 SNI |
| `%ssl::<cert_subject`, `%ssl::<cert_issuer`, `%ssl::<cert_errors` | 서버 인증서의 주체·발급자·검증 오류 |

`%credentials` 가 들어간 형식이 있으면 로그를 조심해서 다룹니다. Basic 인증에서는 이 코드가 비밀번호 자체를 기록합니다[1]. `%ssl::<cert` 는 인증서 전체를 PEM 으로 찍는데, 큰 인증서는 access.log 한 줄 제한 8KB 를 넘어 줄이 잘릴 수 있습니다[1]. 인증서로 서버를 알아보는 법은 [인증서로 서버 알아보기](../fingerprints/certificates.md) 에 있습니다.

### X-Forwarded-For 와 클라이언트 주소

Squid 는 기본 설정(`forwarded_for on`)에서 바깥 서버로 넘기는 요청에 `X-Forwarded-For: 클라이언트IP` 를 붙입니다[1]. `off` 면 값이 `unknown` 이 되고, `transparent`, `delete`, `truncate` 로 헤더를 그대로 두거나 지우거나 클라이언트 IP 하나만 남길 수도 있습니다[1]. 그래서 바깥 웹 서버가 이 헤더를 기록했다면 그 로그에 원래 PC 의 주소가 남을 수 있습니다. 센서가 프록시와 바깥 서버 사이를 봤다면 [http.log 의 `proxied` 필드](../zeek/zeek-logs/http-log.md)에 X-Forwarded-For 같은 프록시 관련 헤더가 기록됩니다[11].

반대로 Squid 앞에 다른 프록시나 부하 분산기가 있으면 access.log 의 클라이언트 주소가 모두 그 장비 주소로 찍힙니다. 이를 풀려고 `follow_x_forwarded_for` 로 앞 장비를 믿도록 허용하면, Squid 는 들어온 X-Forwarded-For 값에서 "간접 클라이언트 주소" 를 골라내고, `log_uses_indirect_client` 기본값 on 에 따라 이 주소를 로그의 클라이언트 주소 자리에 씁니다[1]. 허용된 장비가 헤더에 거짓 주소를 넣으면 Squid 는 그 주소를 그대로 씁니다[1]. `follow_x_forwarded_for` 는 빌드 옵션에 따라 없을 수도 있으므로 설정 파일과 함께 확인합니다[1]. 클라이언트 주소를 사람이나 기기로 이어 가는 법은 [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md) 에 있습니다.

### store.log

store.log 를 켜 둔 서버라면 캐시에 저장하거나 버린 객체가 한 줄씩 남습니다. 13개 필드가 공백으로 나뉘며, 시각(UTC 초와 밀리초), 동작(`SWAPOUT` 저장, `SWAPIN` 디스크에서 읽음, `RELEASE` 삭제, `CREATE` 는 쓰이지 않음), 캐시 디렉터리 번호, 파일 번호(`FFFFFFFF` 는 메모리에만 있던 객체), MD5 해시, HTTP 상태, Date·Last-Modified·Expires 헤더 값(UTC 초, 해석 못 하면 `-1`, 없으면 `-2`), Content-Type, `광고한 길이/실제 읽은 길이`, 메서드, 키(보통 URL) 순서입니다[2]. 캐시 파일과 URL 을 이어 볼 수 있지만, 삭제가 저장보다 늦게 기록될 수 있어 객체가 지금 디스크에 있는지는 파일 전체를 읽어야 판단할 수 있습니다[2].

## 증거로서 의미

**증명하는 것.** 줄이 남은 시각에 그 클라이언트 주소(또는 간접 클라이언트 주소)가 그 URL 이나 `호스트:포트` 로 요청했고, Squid 가 그 요청을 허용해 서버에서 받아 왔는지, 캐시에서 줬는지, 거부했는지, 터널로 넘겼는지를 보여 줍니다[3][4][5]. 5번째 필드로 클라이언트가 받은 양을, 9번째 필드로 Squid 가 실제로 연결한 서버 IP 를 알 수 있습니다[3][4]. `TCP_DENIED` 줄은 요청 시도가 있었고 정책이 막았다는 기록이라서, 막힌 뒤 다른 경로로 나갔는지 찾는 출발점이 됩니다. 보고서에는 "2026-03-02 09:44:46~10:15:29(UTC)에 192.168.10.23 이 프록시를 거쳐 www.example.com:443 과 터널을 열었고, 이 동안 클라이언트 쪽으로 48,213바이트가 전달된 기록이 있다"(만든 예시)처럼 기록된 만큼만 씁니다.

**증명하지 못하는 것.** 기본 설정의 HTTPS 는 경로·쿼리·내용이 없고 호스트와 포트만 남습니다[1][9]. 기본 형식의 바이트는 클라이언트가 받은 양이라서, 클라이언트가 올려 보낸 양은 `%>st` 를 넣은 형식이 아니면 알 수 없습니다[1][3]. 자료 유출을 판단할 때는 흐름 기록이나 방화벽 기록의 보낸 바이트를 함께 봅니다([자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration.md)). 인증을 쓰지 않는 프록시는 사용자 필드가 `-` 라서 사람을 알 수 없고, User-Agent·Referer·Host 헤더도 기본 형식에는 없습니다[1][3]. 페이지 하나를 열어도 여러 서버로 요청이 수십 개 나가서, 사람이 링크를 눌렀는지는 한 줄로 구분되지 않습니다. 실제 망 트래픽 네 묶음을 분석한 ReSurf 연구에서는 Host 헤더만으로 사용자가 방문하려던 사이트를 고르면 정확도가 20~40% 에 그쳤고, Referer 로 요청을 그래프로 이은 ReSurf 방법은 정밀도 95%·재현율 91% 이상이었습니다[12]. 기본 형식에는 Referer 가 없으므로, 방문 의도를 따지려면 `combined` 같은 형식이나 PC 의 브라우저 기록이 필요합니다.

## 시각 해석

기본 형식의 첫 필드는 Squid 가 그 줄을 쓰기 시작한 시각이고, 보통 요청을 다 받고 응답을 다 보낸 트랜잭션의 끝입니다[3]. 소스에서도 줄을 쓰는 순간의 현재 시각을 찍습니다[4]. 값은 1970-01-01 UTC 기준 초라서 시간대가 없습니다[3]. 요청이 시작된 대략의 시각은 첫 필드에서 걸린 시간을 빼서 구하며, 첫 필드는 초이고 걸린 시간은 밀리초라서 1000 으로 나눈 뒤 뺍니다[3]. 형식에 `%tS` 가 있으면 요청 헤더를 다 받은 시각이 바로 찍히고, Squid 는 걸린 시간(`%tr`)을 이 시각을 기준으로 계산합니다[1].

이 차이는 오래 열린 터널에서 커집니다. 위 예시의 첫 줄은 10:15:29.880(UTC)에 쓰였지만 걸린 시간이 1,843,210밀리초라서 터널은 약 30분 전인 09:44:46.670 에 열렸습니다(만든 예시). 줄 시각만 보고 "10:15 에 접속했다" 고 쓰면 틀립니다. 파일 안의 줄 순서도 끝난 순서라서, 먼저 시작한 긴 요청이 나중에 시작한 짧은 요청보다 아래에 있을 수 있습니다. 시간순으로 볼 때는 시작 시각을 계산해 정렬합니다.

`common`·`combined` 형식의 `[%tl]` 은 프록시 서버의 현지 시각에 `+0900` 같은 오프셋을 붙인 값이고, `%tg` 는 GMT 입니다[1]. `syslog` 모듈로 보낸 기록은 syslog 머리말 시각이 따로 붙으며 이 시각은 연도와 시간대가 없을 수 있어서, 줄 안의 epoch 시각을 기준으로 삼습니다. store.log 의 시각도 UTC 입니다[2]. 여러 장비의 시각을 맞추는 법은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 과 [네트워크 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다.

## 함정과 한계

**쿼리는 기본으로 지워집니다.** `strip_query_terms` 기본값이 on 이라서 로그의 URL 에서 `?` 뒤가 빠집니다[1]. 피싱 링크의 추적 값이나 명령 서버로 보낸 쿼리는 이 설정을 끈 서버에서만 남습니다. URL 안의 공백도 기본 설정(`uri_whitespace strip`)에서는 지워집니다[1][3].

**클라이언트 주소가 원래 주소가 아닐 수 있습니다.** `client_netmask 255.255.255.0` 이면 주소 마지막 자리가 0 으로 찍혀 같은 대역의 PC 를 구분할 수 없습니다[1]. X-Forwarded-For 를 따르도록 설정한 서버에서는 앞 장비가 넣은 헤더 값이 클라이언트 주소가 됩니다[1]. NAT 뒤의 PC 들도 하나의 주소로 보입니다.

**탐지 규칙의 필드 이름이 로그와 다릅니다.** SigmaHQ 의 프록시 규칙(`logsource: category: proxy`)은 `c-useragent`, `cs-host`, `c-uri`, `cs-method`, `c-uri-extension` 같은 W3C 확장 로그식 이름을 씁니다[10]. 빈 User-Agent 를 찾는 규칙(`c-useragent: ''`), `api.telegram.org` 호스트로 가는데 User-Agent 에 Telegram·Bot 이 없는 요청을 찾는 규칙, 붙여넣기 사이트의 원문 주소를 찾는 규칙, `rclone/v` 로 시작하는 User-Agent 를 찾는 규칙, `Microsoft-WebDAV-MiniRedir/` User-Agent 의 GET 을 찾는 규칙이 있습니다[10]. Squid 기본 형식에는 User-Agent 가 없어서, User-Agent 규칙은 이 로그에서 하나도 걸리지 않고, 빈 User-Agent 규칙은 없는 필드를 빈 값으로 매핑하면 모든 줄에 걸릴 수 있습니다. `cs-host` 는 HTTPS 에서 CONNECT 의 `호스트:포트` 에서 떼어 내야 합니다. 규칙을 로그에 맞추는 법은 [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md) 에 있습니다.

**로그를 쓸 수 없으면 Squid 가 멈춥니다.** 디스크가 가득 차거나 파일이 운영체제 크기 제한을 넘어 쓰기 오류가 나면 Squid 는 스스로 종료하고[2], `access_log` 의 `on-error` 기본값 `die` 도 쓰기 오류가 난 작업 프로세스를 끝냅니다[1]. access.log 에 빈 구간이 있으면 cache.log 의 FATAL 메시지와 디스크 상태를 먼저 봅니다. `on-error=drop` 으로 설정했다면 그 동안의 줄은 조용히 빠집니다[1].

**지우기와 교대.** Squid 가 실행 중일 때 access.log 를 지우면 파일 이름은 사라지지만, 프로세스가 파일을 닫을 때까지 디스크 공간은 풀리지 않습니다[2]. 교대 번호 `.0`~`.9` 가운데 중간 번호가 빠져 있거나, 설정된 교대 주기와 파일 시각이 맞지 않으면 누군가 파일을 옮기거나 지웠을 가능성이 있습니다. 기본 설정에서는 현재 파일과 이전 파일 10개만 남아서, 하루에 한 번 교대하는 서버라면 열하루 정도의 기록만 남습니다[1][2].

**일부 요청만 기록될 수 있습니다.** `access_log` 줄 끝에 ACL 을 달면 그 조건에 맞는 요청만 기록되고, `access_log none` 이면 맞는 요청은 남지 않습니다[1]. ICP 조회도 `log_icp_queries` 를 끄면 기록되지 않습니다[2][3]. 로그에 없다는 사실로 요청이 없었다고 쓰기 전에 설정을 확인합니다.

**SslBump 를 켠 서버.** 설정에 `ssl_bump` 규칙과 `ssl-bump` 포트가 있으면 HTTPS 도 풀어서 GET·POST 줄이 남을 수 있고, `%ssl::bump_mode` 로 줄마다 어떻게 처리했는지 확인할 수 있습니다[1]. 이 경우 같은 연결이 CONNECT 줄과 그 안의 요청 줄로 여러 번 기록되므로, 요청 수를 셀 때 겹치지 않게 봅니다.

## 직접 분석해 보기

### 헥스로 한 번: 공백으로 나뉜 필드

다음은 위 예시의 두 번째 줄을 기본 형식대로 쓴 바이트입니다(형식으로 만든 예시).

```text
00000000: 3137 3732 3434 3635 3330 2e35 3132 2020  1772446530.512
00000010: 2020 2038 3720 3139 322e 3136 382e 3130     87 192.168.10
00000020: 2e32 3320 5443 505f 4d49 5353 2f32 3030  .23 TCP_MISS/200
00000030: 2031 3833 3020 4745 5420 6874 7470 3a2f   1830 GET http:/
00000040: 2f77 7777 2e65 7861 6d70 6c65 2e6e 6574  /www.example.net
00000050: 2f69 6e64 6578 2e68 746d 6c20 2d20 4849  /index.html - HI
00000060: 4552 5f44 4952 4543 542f 3139 382e 3531  ER_DIRECT/198.51
00000070: 2e31 3030 2e37 2074 6578 742f 6874 6d6c  .100.7 text/html
00000080: 0a                                       .
```

첫 10바이트 `31 37 … 30` 은 초 단위 epoch `1772446530` 이고, `2e` 뒤 세 자리 `35 31 32` 가 밀리초입니다. 소스의 출력 형식은 `%9ld.%03d %6ld` 라서 밀리초는 늘 세 자리로 채워지고, 걸린 시간 `87` 은 여섯 자리 폭에 맞추려고 앞에 공백(`20`) 네 개가 더 붙어 모두 다섯 개의 공백 뒤에 옵니다[4]. 그래서 필드를 나눌 때 공백 하나를 기준으로 자르면 빈 필드가 생기고, 연속된 공백을 하나로 보는 도구(awk 기본 동작 등)를 써야 합니다. `TCP_MISS/200` 의 `/` 뒤 상태 코드도 `%03d` 라서 늘 세 자리입니다. 사용자가 없어 `2d`(`-`) 하나가 들어가고, 줄은 `0a` 하나로 끝납니다[4]. `log_mime_hdrs` 가 켜져 있으면 `0a` 앞에 `20 5b`(` [`)로 시작하는 헤더 필드가 두 개 더 붙습니다[4].

### 공개 도구로 한 번: 설정 확인과 awk

먼저 분석 대상의 squid.conf 에서 기록에 영향을 주는 줄만 뽑습니다. include 로 다른 파일을 불러오는 설정이면 그 파일도 같이 봅니다.

```text
grep -E '^[[:space:]]*(access_log|logformat|cache_log|logfile_rotate|strip_query_terms|client_netmask|follow_x_forwarded_for|log_uses_indirect_client|forwarded_for|log_mime_hdrs|cache_store_log|ssl_bump|http_port)' squid.conf
```

기본 형식의 access.log 는 공백으로 나뉘므로 awk 로 바로 읽을 수 있습니다. 다음은 줄마다 시작 시각을 계산해 시작 순서로 정렬하는 명령입니다. 출력은 시작 시각, 끝 시각, 클라이언트, 결과 코드/상태, 메서드, URL 순서입니다.

```text
awk '{ printf "%.3f %.3f %s %s %s %s\n", $1 - $2/1000, $1, $3, $4, $6, $7 }' access.log | sort -n
```

오래 열린 터널(여기서는 10분 이상)과 거부된 요청만 따로 뽑을 수도 있습니다.

```text
awk '$6 == "CONNECT" && $2 > 600000' access.log
awk '$4 ~ /^TCP_DENIED/' access.log
```

epoch 초를 읽기 쉬운 시각으로 바꿀 때는 GNU date 에서 `date -u -d @1772444686` 처럼 씁니다. 결과는 `Mon Mar  2 09:44:46 UTC 2026` 입니다. 교대된 파일까지 한꺼번에 볼 때는 `.9` 부터 `.0` 을 거쳐 현재 파일 순서로 이어 붙인 뒤 정렬합니다. `logformat` 으로 형식을 바꾼 서버는 필드 순서가 다르므로, awk 의 `$번호` 를 그 형식 정의에 맞춰 고칩니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 | 링크 |
|---|---|---|
| 방화벽 로그 | 같은 시각에 프록시가 9번째 필드의 서버 IP 로 연결했는지, PC 가 프록시를 거치지 않고 직접 나간 연결이 있는지 | [방화벽 로그](firewall-logs.md) |
| 흐름 기록 | 터널 동안 PC → 프록시, 프록시 → 서버 방향으로 보낸 바이트(업로드량) | [흐름 기록](../../01-foundations/records/flow-records.md) |
| DNS 서버 로그 | 프록시가 대신 이름을 조회했으므로 질의한 주소가 PC 가 아니라 프록시인지 | [DNS 서버 로그](dns-server-logs.md) |
| DHCP 로그 | 그 시각에 클라이언트 IP 를 받은 기기의 MAC 주소·호스트 이름 | [DHCP 로그](dhcp-logs.md) |
| Zeek http.log·ssl.log | 프록시 앞뒤를 센서가 봤다면 CONNECT 요청, `proxied` 헤더, 터널 안 TLS 의 SNI·인증서 | [http.log](../zeek/zeek-logs/http-log.md), [ssl.log·x509.log](../zeek/zeek-logs/ssl-x509-log.md) |
| 웹 서버 로그 | 서버 쪽에 X-Forwarded-For 로 원래 PC 주소가 남았는지 | [웹 서버 로그 (Apache·Nginx)](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/servers/web-server-logs.html) |
| 브라우저 기록 | 같은 시각·도메인의 방문 기록이 있어 사람이 연 페이지인지 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/), [사파리](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/browsers/safari/), [Linux 의 브라우저 프로필](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/desktop/browsers.html) |
| AI 서비스 접속 | 프록시 로그에 남은 AI 서비스 도메인 | [AI 서비스 도메인과 네트워크 기록](https://urock-ailab.github.io/forensics-handbook/ai/02-artifacts/network-enterprise/network-traces.html) |

프록시 로그로 사람을 찾아가는 흐름은 [이 시각에 이 IP 를 누가 썼나](../../04-scenarios/user-activity/ip-attribution.md), 피싱 링크 접속을 확인하는 흐름은 [피싱 링크를 눌렀나](../../04-scenarios/user-activity/phishing-click.md) 에서 다룹니다.

## 실습

이 페이지 "기본 형식 한 줄" 절의 세 줄(만든 예시)을 access.log 라는 파일로 저장해 풀어 봅니다.

1. 공개 도구 절의 awk 명령으로 세 줄의 시작 시각을 계산하고, 시작 순서가 파일 줄 순서와 어떻게 다른지 확인합니다.
2. 첫 줄의 터널은 한국 시각(UTC+9)으로 몇 시 몇 분에 열리고 닫혔습니까?
3. 세 번째 줄은 `HIER_NONE/-` 입니다. 이 요청으로 프록시가 바깥 서버에 연결했다고 볼 수 있습니까? 방화벽 로그에서 무엇을 찾으면 확인됩니까?
4. 첫 줄의 48213 은 어느 방향의 양입니까? 같은 터널에서 PC 가 올려 보낸 양을 알려면 어떤 설정이나 기록이 필요합니까?
5. 두 번째 줄을 `common` 형식으로 바꿔 쓰면 어떤 정보가 빠지고 어떤 정보가 새로 생깁니까?

## 참고 문헌

1. Squid 소스 src/cf.data.pre (squid.conf 지시어와 logformat 코드 설명). https://github.com/squid-cache/squid/blob/master/src/cf.data.pre
2. Squid Wiki, Squid Log Files. https://wiki.squid-cache.org/SquidFaq/SquidLogs
3. Squid Wiki, Feature: Customizable Log Formats. https://wiki.squid-cache.org/Features/LogFormat
4. Squid 소스 src/log/FormatSquidNative.cc. https://github.com/squid-cache/squid/blob/master/src/log/FormatSquidNative.cc
5. Squid 소스 src/LogTags.cc. https://github.com/squid-cache/squid/blob/master/src/LogTags.cc
6. Squid 소스 src/hier_code.h, src/mk-string-arrays.awk. https://github.com/squid-cache/squid/blob/master/src/hier_code.h , https://github.com/squid-cache/squid/blob/master/src/mk-string-arrays.awk
7. Squid 매뉴얼 squid(8) (src/squid.8.in). https://github.com/squid-cache/squid/blob/master/src/squid.8.in
8. Squid 소스 src/Makefile.am. https://github.com/squid-cache/squid/blob/master/src/Makefile.am
9. R. Fielding, M. Nottingham, J. Reschke, RFC 9110 HTTP Semantics, 9.3.6 CONNECT, 2022. https://www.rfc-editor.org/rfc/rfc9110.txt
10. SigmaHQ, rules/web/proxy_generic (proxy_ua_empty, proxy_telegram_api, proxy_raw_paste_service_access, proxy_ua_rclone, proxy_downloadcradle_webdav, proxy_download_susp_tlds_blacklist). https://github.com/SigmaHQ/sigma/tree/master/rules/web/proxy_generic
11. Zeek Documentation, base/protocols/http/main.zeek (HTTP::proxy_headers, proxied). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/http/main.zeek.rst
12. Guowu Xie, Marios Iliofotou, Thomas Karagiannis, Michalis Faloutsos, Yaohui Jin, 「ReSurf: Reconstructing Web-Surfing Activity From Network Traffic」, IFIP Networking 2013. https://ieeexplore.ieee.org/document/6663499
