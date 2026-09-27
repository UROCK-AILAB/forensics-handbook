---
title: "Wireshark·tshark로 읽기"
parent: "기법 · 분석"
nav_order: 360
---

# Wireshark·tshark로 읽기 (Wireshark)

패킷 캡처 파일을 열어 볼 때 가장 먼저 쓰는 도구가 Wireshark 이고, 같은 해부 엔진을 명령줄에서 쓰는 도구가 tshark 입니다. 이 페이지에서는 캡처 파일을 읽을 때 시각을 UTC 로 맞춰 보고, 표시 필터로 범위를 좁히고, 대화 표와 스트림 따라가기로 흐름을 확인한 뒤, 필요한 필드만 표로 뽑는 순서를 다룹니다. 화면에 보이는 값 가운데 무엇이 캡처 파일에 실제로 들어 있는 값이고 무엇이 도구가 추정한 값인지 구분하는 방법도 함께 봅니다.

## 언제 쓰나

사건 시간대의 캡처 파일을 받아 어느 주소가 누구와 얼마나 주고받았는지, 그 안에 어떤 요청과 응답이 있었는지를 패킷 단위로 확인할 때 씁니다. Zeek·Suricata 로그나 흐름 기록에서 의심 연결을 찾은 뒤, 그 연결의 실제 내용을 캡처에서 다시 확인할 때도 씁니다. 화면에서 하나씩 보는 일은 Wireshark 가 편하고, 같은 작업을 기록으로 남기거나 여러 파일에 되풀이하려면 tshark 명령으로 합니다. 이 페이지는 tshark 명령을 기준으로 쓰고, Wireshark 화면에서 같은 기능이 있으면 함께 적습니다.

파일이 너무 커서 한 번에 열기 어렵거나 여러 파일을 합쳐야 하면 먼저 [큰 캡처 파일 다루기](../acquisition/large-captures.md)에서 필요한 구간을 잘라 냅니다. pcap·pcapng 파일 안에 시각과 패킷이 어떻게 저장되는지는 [pcap 형식](../../01-foundations/capture/pcap.md)과 [pcapng 형식](../../01-foundations/capture/pcapng.md)에 있습니다.

## 절차

아래 파일 이름, IP, 포트, 도메인은 모두 만든 예시입니다. 명령마다 tshark 버전(`tshark -v`)과 입력 파일 해시를 작업 기록에 함께 적습니다.

### 1. 이름 해석을 끄고 읽는다

tshark 는 `-r` 로 캡처 파일을 읽으면 패킷마다 요약 한 줄을 표준 출력에 씁니다[1]. 파일 형식과 gzip·Zstandard·LZ4 압축은 확장자가 없어도 스스로 판별합니다[1]. `-n` 이나 `-N` 을 주지 않으면 환경설정 값을 따르는데, 환경설정 기본값은 `-N dmN` 입니다[2]. `d` 는 캡처 안의 DNS 패킷으로, `m` 은 MAC 주소를 이름으로 바꾸고, `N` 은 DNS 같은 외부 해석기를 쓰는데 `n`(네트워크 주소 해석)이 함께 켜져 있어야 효과가 있습니다[2].

증거 분석에서는 이 기본값이 문제가 됩니다. 이름 해석은 실패할 수 있고, 나중에 다른 PC 에서 열면 결과가 달라집니다[4]. 외부 DNS 질의를 보내게 설정하면 그 질의와 응답 패킷이 분석 PC 에서 캡처하는 트래픽에 더해집니다[4]. Wireshark 는 해석한 DNS 이름을 캐시에 두기 때문에 실행 중에 바뀐 정보는 반영하지 않습니다[4]. 그래서 처음부터 `-n` 으로 이름 해석을 끄고 IP 주소 그대로 봅니다[2].

```
tshark -n -r case01.pcapng
```

Wireshark 화면에서는 환경설정(Preferences)의 Name Resolution 항목에서 같은 설정을 끕니다[4].

### 2. 시각을 UTC 날짜와 함께 보이게 한다

tshark 시각 열의 기본 표시는 첫 패킷부터 지난 초(relative, `r`)라서 이대로는 보고서에 쓸 시각이 나오지 않습니다[2]. `-t` 로 형식을 바꾸는데, 조사에서 자주 쓰는 값은 아래와 같습니다[2].

| `-t` 값 | 표시 |
|---|---|
| `ud` | UTC 날짜(YYYY-MM-DD)와 시각, 끝에 "Z" |
| `u` | UTC 시각만(날짜 없음), 끝에 "Z" |
| `ad` | 분석 PC 시간대의 날짜와 시각 |
| `e` | 1970-01-01 00:00:00 이후 초(epoch) |
| `r` | 첫 패킷 이후 지난 시간(기본값) |
| `d`, `dd` | 직전 패킷, 직전에 표시된 패킷과의 시간 차 |

소수 자릿수는 `.N`(0~9)으로 정하고 `.` 만 쓰면 파일에 맞춰 정합니다[2]. 예를 들어 `-t ud.6` 은 UTC 날짜·시각을 마이크로초까지 보여 줍니다.

```
tshark -n -t ud.6 -r case01.pcapng
```

`ad`·`a` 처럼 현지 시각으로 표시하는 값은 캡처한 곳이 아니라 **파일을 여는 PC 의 시간대**를 씁니다. pcap 처럼 도착 시각을 UTC 로 저장하는 형식은 여는 PC 가 UTC 에서 현지 시각으로 바꿔 보여 주므로, 로스앤젤레스에서 현지 02:00 에 캡처한 패킷(파일에는 10:00 UTC)이 베를린에서 열면 11:00 으로 보입니다[4]. 반대로 옛 DOS 기반 Sniffer 형식이나 옛 Microsoft Network Monitor·Observer 형식은 도착 시각을 현지 시각으로 저장해서, Wireshark 가 여는 PC 의 시간대로 UTC 를 계산하면 틀린 값이 나올 수 있습니다[4]. 보고서에는 `ud` 나 epoch 값을 쓰고 기준이 UTC 라는 것을 함께 적습니다. 네트워크 기록 전반의 시각 기준은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)에서 다룹니다.

Wireshark 는 시각을 스스로 만들지 않고 캡처할 때 libpcap·Npcap 이 넘겨준 값을 그대로 씁니다[4]. USB 로 연결한 네트워크 어댑터는 시각 정확도가 나쁘다는 점도 캡처 환경을 확인할 때 봅니다[4].

### 3. 표시 필터로 범위를 좁힌다

tshark 의 `-Y` 는 표시 필터(display filter)를 걸어 맞는 패킷만 출력합니다[1]. 표시 필터는 캡처할 때 쓰는 캡처 필터(`-f`, pcap-filter 문법)와 문법이 다릅니다[1][3]. 캡처 필터 문법은 [캡처 필터와 잘린 패킷](../../01-foundations/capture/capture-filters.md)에 있습니다.

```
tshark -n -t ud.6 -r case01.pcapng -Y "ip.addr == 203.0.113.50 && tcp.port in {80,443}"
```

필드나 프로토콜 이름만 쓰면 그 필드가 있는 패킷을 고릅니다[3]. 비교는 `==`, `!=`, `>`, `<`, `>=`, `<=`(또는 `eq`, `ne` 같은 글자 연산자)로 하고, IP 주소는 `ip.addr == 10.1.0.0/16` 처럼 CIDR 로도 씁니다[3]. `in {80,443}` 은 집합 비교이고, 집합 안에 `{443, 4430..4434}` 처럼 범위도 넣을 수 있습니다[3]. `contains` 는 문자열이나 바이트 순서가 들어 있는지 보고, `matches`(또는 `~`)는 정규식(PCRE2)으로 비교하는데 기본으로 대소문자를 구분하지 않습니다[3]. `contains` 는 숫자나 IP 주소 같은 원자 필드에는 쓸 수 없습니다[3].

한 패킷에 같은 필드가 여러 개 있으면(예: `ip.addr` 는 출발지와 목적지 둘) `==` 는 하나라도 같으면 참이고, `!=` 는 모두 달라야 참입니다[3]. 모두 같아야 하면 `===`, 하나라도 달라야 하면 `!==` 를 씁니다[3]. 터널 안쪽 IP 처럼 같은 프로토콜이 두 겹이면 `ip.src#2` 로 안쪽 값을 고릅니다[3].

시각으로 고를 때는 `frame.time >= "2026-03-02T00:30:00Z"` 처럼 ISO 8601 형식을 쓰고 "Z" 나 UTC 오프셋을 꼭 붙입니다. 시간대를 빼면 분석 PC 의 현지 시각으로 해석합니다[3].

### 4. 대화 표와 통계로 전체 모양을 본다

패킷을 하나씩 보기 전에 누가 누구와 얼마나 주고받았는지부터 표로 봅니다. `-z` 통계는 파일을 다 읽은 뒤 결과를 출력하고, 패킷 요약까지 보지 않으려면 `-q` 를 함께 줍니다[1].

```
tshark -n -q -r case01.pcapng -z conv,tcp
tshark -n -q -r case01.pcapng -z endpoints,ip
tshark -n -q -r case01.pcapng -z io,phs
```

`conv,유형` 은 대화 하나에 한 줄씩 방향별 프레임·바이트 수, 합계, 첫 패킷 기준 상대 시작 시각, 지속 시간을 보여 주고 총 프레임 수 순서로 정렬합니다[1]. 유형은 `eth`, `ip`, `ipv6`, `tcp`, `udp` 등입니다[1]. `endpoints,유형` 은 주소별 표이고 총 패킷 수 순서로 정렬합니다[1]. `io,phs` 는 프로토콜 계층 통계입니다[1]. 한 패킷이 IP·TCP·HTTP 처럼 여러 프로토콜로 세어져서 비율을 더하면 100% 를 넘고, "End Packets" 는 그 프로토콜이 가장 위 계층이었던 패킷 수입니다[5].

`io,stat,간격,필터` 는 정한 간격(초)마다 패킷·바이트 수를 셉니다[1]. 간격에 소수를 줄 수 있고 0 이면 파일 전체를 한 구간으로 셉니다[1]. `COUNT`, `SUM`, `MIN`, `MAX`, `AVG`, `LOAD` 로 필드 값을 계산할 때는 필드 이름을 필터 자리에도 다시 써야 합니다(`AVG(smb.time)smb.time`)[1].

```
tshark -n -q -r case01.pcapng -z io,stat,60,"ip.addr == 203.0.113.50"
```

Wireshark 의 Conversations 창에서는 시작 시각을 상대 시각(Rel Start)과 절대 시각(Abs Start)으로 바꿔 볼 수 있습니다[5]. 상대 시작은 첫 패킷 이후 초이고, 절대 시작은 "Time of Day" 표시 형식과 같습니다[5].

### 5. 스트림을 따라가 내용을 본다

의심 대화를 골랐으면 그 스트림의 내용을 이어 붙여 봅니다. TCP 스트림 번호는 `tcp.stream` 필드에 있고 0 부터 셉니다[1][7].

```
tshark -n -q -r case01.pcapng -z follow,tcp,ascii,3
tshark -n -q -r case01.pcapng -z follow,tcp,hex,10.1.2.30:51514,203.0.113.50:80
```

`follow,프로토콜,모드,필터` 에서 프로토콜은 `tcp`, `udp`, `tls`, `http`, `http2`, `quic` 등이고, 모드는 `ascii`, `hex`, `raw`, `utf-8`, `yaml` 등입니다[1]. 필터 자리에는 `주소:포트,주소:포트`, 스트림 번호, HTTP/2·QUIC 은 `스트림 번호,하위 스트림 번호` 를 씁니다[1]. 두 번째 노드가 보낸 데이터는 앞에 탭을 붙여 구분합니다[1]. 출력 머리에는 아래처럼 필터와 두 노드가 나옵니다(만든 예시).

```
===================================================================
Follow: tcp,ascii
Filter: tcp.stream eq 3
Node 0: 10.1.2.30:51514
Node 1: 203.0.113.50:80
```

Wireshark 의 Follow Stream 창은 클라이언트가 보낸 데이터를 빨강, 서버가 보낸 데이터를 파랑으로 칠하고(색은 테마 설정에 따라 바뀝니다) 인쇄할 수 없는 문자는 점으로 바꿉니다[4]. 창을 열면 그 스트림만 보이는 표시 필터가 걸리고, "Back" 을 누르면 이전 필터로 돌아갑니다[4]. 스트림 안의 파일을 꺼내는 방법(`--export-objects`)은 [세션 복원과 파일 꺼내기](file-extraction.md)에, TLS 로 암호화된 스트림을 다루는 방법은 [암호화된 트래픽 분석](encrypted-traffic.md)에 있습니다.

### 6. 필요한 필드만 표로 뽑는다

보고서나 다른 도구에 넘길 값은 `-T fields` 와 `-e` 로 뽑습니다. `-T fields` 를 쓰면 `-e` 로 필드를 하나 이상 지정해야 하고, `_ws.col.` 을 앞에 붙이면 열 값을 뽑습니다[1].

```
tshark -n -r case01.pcapng -Y "http.request" -T fields -E header=y -E separator=, -E quote=d -E occurrence=f \
  -e frame.number -e frame.time_epoch -e ip.src -e ip.dst -e tcp.stream -e http.host -e http.request.method -e http.request.uri -e http.user_agent > http_requests.csv
```

`-E` 의 기본값은 탭 구분(`separator=/t`), 머리글 없음(`header=n`), 따옴표 없음(`quote=n`)이고, 한 패킷에 같은 필드가 여럿이면 모든 값(`occurrence=a`)을 쉼표(`aggregator=,`)로 이어 한 필드 값으로 씁니다[1]. 쉼표로 구분한 CSV 를 만들면서 이 기본값을 그대로 두면 값 안의 쉼표 때문에 열이 밀리므로, 위처럼 `quote=d` 로 감싸거나 `occurrence=f` 로 첫 값만 뽑습니다[1]. 결과를 스프레드시트로 열 예정이면 `escape_formulas=y` 를 줍니다. 이 옵션은 `=`, `+`, `-`, `@` 로 시작하는 값 앞에 아포스트로피를 붙여 패킷 안의 문자열이 수식으로 실행되지 않게 하고, 음수에도 붙기 때문에 기본으로 꺼져 있습니다[1].

시각 필드는 목적에 맞게 고릅니다. `frame.time` 은 도착 시각(Arrival Time), `frame.time_epoch` 는 epoch 초, `frame.time_utc` 는 UTC 도착 시각이고, `frame.time_utc` 는 Wireshark 4.2.0 부터 있습니다[6]. 버전이 섞인 환경에서는 `frame.time_epoch` 가 1.4.0 부터 있어 가장 무난합니다[6].

`-w` 는 해부 결과가 아니라 원시 패킷을 파일로 씁니다[1]. 해부한 내용을 파일로 남기려면 `-w` 를 쓰지 말고 표준 출력을 파일로 돌립니다[1]. `-Y` 와 `-w` 를 함께 써서 일부 패킷만 새 파일로 떼어 낼 때 어떤 패킷이 함께 들어가는지는 [큰 캡처 파일 다루기](../acquisition/large-captures.md)에 있습니다.

### 7. 응답 짝이 필요한 필드는 두 번 읽는다

"response in frame #" 처럼 뒤에 오는 패킷을 봐야 채워지는 필드는 한 번 읽기로는 비어 있을 수 있습니다. `-2` 를 주면 tshark 가 파일을 처음부터 끝까지 한 번 읽고 나서 출력하므로 이런 필드와 재조립 의존 관계가 제대로 채워집니다[1]. 두 번 읽기에서는 `-R` 이 먼저 읽기 필터로 걸리고, 거기 맞은 패킷만 `-Y` 로 다시 거릅니다[1]. `-2` 는 파일을 되감아 읽어야 해서 실시간 캡처나 파이프 입력에는 쓸 수 없습니다[1]. `-M 패킷수` 를 주면 정한 패킷 수마다 내부 세션을 초기화하지만, `-M` 은 `-2` 와 함께 쓸 수 없습니다[1].

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| Wireshark | 화면에서 패킷 목록·상세·헥스를 보고, Conversations·Protocol Hierarchy·I/O Graph·Follow Stream 창을 씁니다[4][5] |
| tshark | 같은 해부 엔진을 명령줄에서 쓰고, 명령을 작업 기록에 남기기 좋습니다[1] |
| capinfos·editcap·mergecap | 파일 정보 확인, 구간 자르기, 합치기([큰 캡처 파일 다루기](../acquisition/large-captures.md)) |
| Security Onion | 분석용 데스크톱에 Wireshark 가 들어 있고, 받은 pcap 을 Wireshark 로 열어 HTTP 객체를 꺼냅니다[12] |

자주 쓰는 필드 이름은 아래와 같습니다. 버전은 Wireshark 표시 필터 참조에 적힌 첫 버전입니다.

| 필드 | 뜻 | 있는 버전 |
|---|---|---|
| `tcp.stream` | TCP 스트림 번호 | 1.2.0+[7] |
| `tcp.payload` | TCP 페이로드 | 2.4.0+[7] |
| `tcp.analysis.lost_segment` | 앞 세그먼트가 캡처되지 않음 | 1.0.0+[7] |
| `tcp.completeness` | 대화 완결성 비트 | 3.6.0+[7] |
| `http.host`, `http.user_agent` | HTTP Host, User-Agent 헤더 | 1.0.0+[9] |
| `http.request.full_uri` | 전체 요청 URI | 1.6.0+[9] |
| `dns.qry.name`, `dns.flags.rcode` | 질의 이름, 응답 코드 | 1.0.0+[10] |
| `tls.handshake.extensions_server_name` | TLS SNI | 3.0.0+[8] |
| `tls.handshake.ja3`, `tls.handshake.ja3s` | JA3·JA3S 지문 | 3.6.0+[8] |
| `tls.handshake.ja4` | JA4 지문 | 4.2.0+[8] |

Wireshark 3.0 에서 SSL 해부기 이름이 TLS 로 바뀌어서, 옛 문서의 `ssl.` 필터는 `tls.` 로 바꿔 씁니다(`ssl` 을 쓰면 경고가 나옵니다)[11]. DNS 필드를 쓰는 분석 방법은 [DNS 분석](dns-analysis.md)에 있습니다.

## 함정과 한계

- **통계는 표시 필터를 따르지 않습니다.** `-z` 통계는 패킷 출력과 따로 계산해서 `-Y` 의 영향을 받지 않습니다[1]. 범위를 좁히려면 `-z conv,tcp,ip.addr==203.0.113.50` 처럼 통계마다 필터를 따로 줍니다[1].
- **`!=` 는 필드가 없는 패킷을 뺍니다.** `ip.dst != 224.1.2.3` 은 `ip.dst and ip.dst != 224.1.2.3` 과 같아서 IP 가 아닌 패킷(ARP 등)이 모두 빠집니다[3]. IP 가 아닌 패킷까지 보려면 `not ip.dst == 224.1.2.3` 으로 씁니다[3].
- **재조립 설정에 따라 해석이 바뀝니다.** TCP 설정 "Allow subdissector to reassemble TCP streams"(기본 켬)를 끄거나, 캡처가 연결 중간부터 시작했거나, 세그먼트가 빠지거나 순서가 뒤바뀌면 HTTP 가 "Continuation", TLS 가 "Ignored Unknown Record" 로 보일 수 있습니다[4]. "Reassemble out-of-order segments" 는 기본으로 꺼져 있습니다[4]. `-o 설정:값` 으로 바꾼 설정은 그 실행에만 적용되므로 명령과 함께 기록합니다[1].
- **"Previous segment not captured" 는 캡처에서 빠진 것입니다.** 현재 순서 번호가 기대한 다음 순서 번호보다 크면 이 표시가 붙습니다[4]. 캡처 시작 직후에 흔하고[7], 빠진 세그먼트의 내용은 캡처 어디에도 없습니다.
- **여러 값이 한 필드에 합쳐집니다.** `-e` 로 뽑은 필드가 한 패킷에 여럿이면 기본으로 모든 값을 쉼표로 이어 씁니다[1]. 그래서 터널처럼 IP 헤더가 두 번 들어간 패킷에서는 `ip.src` 가 두 값으로 나옵니다[1][3].
- **전문가 정보(Expert Info)는 힌트입니다.** 전문가 정보가 있다고 문제가 있는 것도, 없다고 정상인 것도 아니고, 프로토콜마다 내는 양이 다릅니다[4]. TCP 재전송·순서 어긋남 판정도 캡처 위치(서버 쪽·클라이언트 쪽·중간)에 따라 달라질 수 있습니다[4].
- **pcap 으로 저장하면 나노초가 줄어듭니다.** 나노초 정밀도로 캡처한 패킷을 마이크로초 pcap 형식으로 저장하면 정밀도가 마이크로초로 떨어집니다[4].

## 결과를 어떻게 해석하나

Wireshark·tshark 로는 캡처 파일 안의 패킷 바이트, 캡처 도구가 매긴 도착 시각, 해부기가 그 바이트를 풀어낸 필드 값을 확인할 수 있습니다. 보고서에는 "2026-03-02 00:31:05Z 부터 약 40초 동안 10.1.2.30 이 203.0.113.50 의 80번 포트로 HTTP POST 요청 12건을 보낸 패킷이 캡처에 있다"(만든 예시)처럼 캡처로 확인되는 만큼만 씁니다. 시각에는 UTC 기준인지와 어떤 캡처 지점의 시각인지를 함께 적습니다.

증명하지 못하는 것도 분명히 구분합니다. 해부기가 붙인 프로토콜 이름은 포트 번호, Decode As(`-d`) 설정, 휴리스틱 판단으로 정해져서, 443번 포트라고 모두 TLS 인 것은 아닙니다[2]. 이름 해석 결과는 분석한 PC 와 시점에 따라 달라지므로 주소가 그 이름의 서버였다는 근거가 되지 않습니다[4]. 캡처되지 않은 패킷(`tcp.analysis.lost_segment`)의 내용이나, 캡처 지점을 지나지 않은 통신은 캡처 파일로 판단할 수 없습니다. 캡처에 있는 시각은 캡처한 장비의 시계 기준이라 그 시계가 맞았는지는 따로 확인해야 합니다[4].

같은 연결을 다른 기록과 맞춰 보면 해석이 단단해집니다. Zeek conn.log·Suricata 이벤트의 연결 시각, 방화벽·프록시 로그, 단말의 프로세스 기록을 UTC 로 맞춰 한 줄로 이어 붙이는 방법은 [네트워크 타임라인](timeline.md)에 있습니다.

## 참고 문헌

1. Wireshark, tshark(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
2. Wireshark, dissection-options(해부 옵션) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/dissection-options.adoc
3. Wireshark, wireshark-filter(4) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/wireshark-filter.adoc
4. Wireshark User's Guide, Advanced Topics. https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_advanced.adoc
5. Wireshark User's Guide, Statistics. https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_statistics.adoc
6. Wireshark Display Filter Reference: Frame. https://www.wireshark.org/docs/dfref/f/frame.html
7. Wireshark Display Filter Reference: TCP. https://www.wireshark.org/docs/dfref/t/tcp.html
8. Wireshark Display Filter Reference: TLS. https://www.wireshark.org/docs/dfref/t/tls.html
9. Wireshark Display Filter Reference: HTTP. https://www.wireshark.org/docs/dfref/h/http.html
10. Wireshark Display Filter Reference: DNS. https://www.wireshark.org/docs/dfref/d/dns.html
11. Wireshark Wiki, TLS. https://wiki.wireshark.org/TLS
12. Security Onion Documentation, Wireshark. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/wireshark.rst
