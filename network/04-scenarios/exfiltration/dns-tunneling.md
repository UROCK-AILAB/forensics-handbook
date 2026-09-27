---
title: "DNS 로 몰래 보냈나"
parent: "시나리오 · 자료 유출"
nav_order: 500
---

# DNS 로 몰래 보냈나 (DNS Tunneling)

DNS 터널 (DNS Tunneling) 은 보낼 자료를 질의 이름의 하위 라벨에 인코딩해 담고, 받을 자료는 TXT·NULL 같은 응답 레코드에 담아 DNS 메시지로 주고받는 방식입니다. 대부분의 네트워크가 DNS 를 막지 않아서 다른 통신이 막힌 곳에서도 쓰이지만, 한 도메인 아래에 처음 보는 긴 이름이 수백·수천 개 쌓이는 흔적이 dns.log·EVE·DNS 서버 로그·흐름 기록에 남습니다. 이 페이지는 그 흔적을 어떤 순서로 보고, 보고서에 어디까지 쓸 수 있는지를 다룹니다.

## 조사 질문

DNS 터널을 의심하는 조사는 아래 질문으로 나눠서 답합니다.

- 어떤 등록 도메인 아래로 고유한 이름이 비정상으로 많이 질의됐나.
- 그 질의를 보낸 것은 어느 내부 호스트이고, 언제부터 언제까지였나.
- 질의 이름과 응답의 모양(라벨 길이, 글자 분포, 레코드 종류, 응답 크기)이 일반 조회와 다른가.
- 그 도메인이 가리키는 IP 로 실제 연결한 기록이 있나, 아니면 DNS 로만 오갔나.

자료 유출 전반(HTTP 업로드·메일·클라우드 저장소 등)은 [자료를 밖으로 보냈나](data-exfiltration.md) 에서, DNS 를 명령 수신에 쓰는 경우는 [악성 코드가 C2 서버와 통신했나](../intrusion/c2-communication.md) 에서 다룹니다.

## 먼저 확인할 것

**센서와 DNS 서버의 위치.** 클라이언트가 내부 재귀 서버에 묻고 그 서버가 바깥에 다시 묻는 구조에서, 센서가 서버 바깥에 있으면 질의의 출발지는 모두 DNS 서버 하나로 보입니다. 이때 실제 클라이언트는 DNS 서버 로그로 찾아야 합니다. 흐름 기록에서도 터널 클라이언트가 어느 리졸버를 거치느냐에 따라 흔적이 크게 달라집니다(분석 흐름 6단계)[26].

**DNS 서버 로그가 켜져 있었나.** BIND 는 `querylog` 옵션이나 `rndc querylog on` 으로 질의 기록을 켜고, `responselog` 로 응답 코드를 남깁니다[14]. Windows DNS 서버의 분석 (Analytic) 로그는 기본으로 꺼져 있고, 켜면 `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-DNSServer%4Analytical.etl` 에 쌓입니다[15]. 이 로그 기능은 Windows Server 2016(Technical Preview)부터 기본으로 들어 있고, 2012 R2 는 KB2956577 핫픽스를 설치해야 씁니다[15]. 사고 당시 꺼져 있었다면 서버 쪽에서 클라이언트를 찾을 수 없으므로 DHCP·VPN 기록과 센서 위치를 함께 따져야 합니다. 로그 형식과 해석은 [DNS 서버 로그](../../02-artifacts/devices/dns-server-logs.md) 에 있습니다.

**로그 도구와 버전.** Zeek dns.log 의 `query` 는 모두 소문자로 바꾼 값입니다[6]. 터널 도구는 대소문자를 모두 쓰는 base64 로 인코딩하는 경우가 많아서[27], 글자 분포나 인코딩을 따지려면 원래 대소문자가 필요합니다. 이 값은 `policy/protocols/dns/log-original-query-case.zeek` 를 불러왔을 때만 `original_query` 필드로 남습니다[7]. Suricata 는 8.0 부터 DNS 기록 형식이 버전 3 으로 바뀌었습니다[12]. 요청의 `type` 이 `query` 에서 `request` 로, 응답이 `answer` 에서 `response` 로 바뀌었고, 버전 3 응답 이벤트의 `src_ip` 는 클라이언트가 아니라 응답한 서버입니다[12]. 그래서 7.0 과 8.0 로그를 섞어 집계하면 응답 이벤트의 출발지가 뒤바뀝니다. 8.0 에서도 `version: 2` 로 7.0 형식을 남길 수 있으므로 실제 로그의 `version` 필드를 확인합니다[11]. EVE 설정의 `types` 로 기록할 레코드 종류를 좁혔다면 TXT·NULL 질의가 빠져 있을 수도 있습니다[11].

**암호화된 DNS 를 허용하나.** dns.log 는 암호화되지 않은 DNS 만 담고, DNS over HTTPS (DoH) 나 DNS over TLS (DoT) 는 담지 못합니다[4]. DoH 는 POST 요청이면 DNS 메시지를 HTTP 본문에 그대로 싣고, GET 요청이면 `dns` 변수에 base64url 로 인코딩해 싣습니다[2]. DoT 는 TCP 853 번을 씁니다[3]. 이런 통신은 conn.log·ssl.log 의 443·853 연결로만 남으므로 [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md) 으로 넘어갑니다.

**시각 기준.** Zeek dns.log 의 `ts` 는 그 연결에서 DNS 메시지를 처음 본 시각이고, `rtt` 는 요청을 본 때부터 응답이 시작될 때까지의 간격입니다[5]. 값은 epoch 초라 `zeek-cut -u` 로 UTC 시각으로 바꿔 읽습니다[9]. EVE 는 요청과 응답이 따로 된 이벤트라 각자 `timestamp` 가 있습니다[11]. BIND 질의 로그 줄의 시각 모양은 로깅 채널 설정에 따라 다르므로 서버의 `logging` 설정을 먼저 확인합니다. 여러 로그를 합치는 기준은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 을 따릅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | Zeek dns.log, Suricata EVE dns | 질의 이름·레코드 종류·응답·응답 코드, 요청마다 한 줄 | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md), [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md) |
| 2 | RITA 결과 | 등록 도메인별 고유 하위 이름 수, 직접 연결 유무 | [DNS 분석](../../03-techniques/analysis/dns-analysis.md) |
| 3 | pcap | 원래 대소문자, 라벨 길이, TXT·NULL 응답의 실제 바이트 | [DNS](../../01-foundations/protocols/dns.md) |
| 4 | DNS 서버 로그 | 내부 재귀 서버 뒤의 실제 클라이언트 IP | [DNS 서버 로그](../../02-artifacts/devices/dns-server-logs.md) |
| 5 | 흐름 기록, Zeek conn.log | 53번 흐름의 바이트·패킷·지속 시간 | [흐름 기록](../../01-foundations/records/flow-records.md), [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md) |
| 6 | 탐지 규칙 경보 | base64 모양 질의, Z 비트, TXT 응답 속 명령 문자열 | [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md) |
| 7 | DHCP·VPN 로그 | 그 시각에 그 내부 IP 를 쓴 기기·계정 | [DHCP 로그](../../02-artifacts/devices/dhcp-logs.md), [VPN 로그](../../02-artifacts/devices/vpn-logs.md) |

## 분석 흐름

1. **등록 도메인별로 고유 이름 수를 셉니다.** 터널은 자료 조각마다 다른 이름을 만들어서, 한 등록 도메인 아래 고유한 전체 이름 (FQDN) 이 크게 늘어납니다. RITA 는 등록 도메인 단위로 이 수를 세고(`.arpa`·`.local` 은 뺍니다), 기본 설정에서 100개 이상을 base, 500·800·1000개를 low·medium·high 로 나눕니다[17][19]. 결과는 `subdomains:>=100 sort:subdomains-desc` 같은 검색식으로 추립니다[16]. RITA 의 가져오기 필터(`internal_subnets` 등)는 DNS 로그에 적용되지 않고, DNS 결과는 conn 로그와 이어 보지 않으므로[17][18], 내부↔내부 질의도 집계에 들어갑니다. RITA 가 없으면 dns.log 에서 `query` 를 뽑아 등록 도메인별로 직접 셉니다. 이때 `co.kr` 같은 2단계 최상위 도메인을 잘못 자르지 않게 주의합니다. 자세한 집계 방법은 [DNS 분석](../../03-techniques/analysis/dns-analysis.md) 에 있습니다.

   ```sh
   # 만든 예시: Zeek TSV dns.log 에서 출발지·질의 이름만 뽑기
   zeek-cut -u ts id.orig_h query qtype_name < dns.log
   # 만든 예시: Suricata 8.0 EVE 에서 요청의 질의 이름만 뽑기
   jq -r 'select(.event_type=="dns" and .dns.type=="request") | .dns.queries[].rrname' eve.json
   ```

2. **상위 도메인의 이름 모양을 봅니다.** DNS 라벨은 63옥텟, 이름 전체는 255옥텟을 넘을 수 없으므로[1], 라벨 길이가 이 한계에 가까운 질의가 한 도메인에 몰리는지 봅니다. 라벨에는 어떤 8비트 값도 들어갈 수 있지만 대소문자는 구분하지 않고 비교합니다[1]. 인기 도메인 100만 개의 글자 빈도는 자연어처럼 Zipf 분포를 따릅니다[27]. iodine·dns2tcp·TCP-over-DNS 로 PDF 파일의 SCP 전송을 터널링하고 도구마다 연속 질의 100개를 살펴본 시험에서는, 세션 ID·카운터 때문에 상위 1~2위 글자만 빈도가 튀고 나머지 순위는 무작위로 만든 도메인과 거의 같았습니다[27]. pcap 이 있으면 tshark 로 이름 길이를 봅니다. `-z dns,tree` 는 질의 종류 분포와 질의 이름 길이·DNS 페이로드의 최대·최소·평균을 보여 주고[23], `dns.qry.name.len`·`dns.count.labels` 필드(Wireshark 1.12.0 부터)로 긴 이름만 골라냅니다[24].

   ```sh
   # 만든 예시
   tshark -r capture.pcapng -q -z dns,tree
   tshark -r capture.pcapng -Y "dns.flags.response == 0 && dns.qry.name.len > 100" -T fields -e ip.src -e dns.qry.name
   ```

3. **응답 쪽을 봅니다.** 받는 방향의 자료는 응답에 실립니다. TXT 레코드는 길이 1바이트와 문자열이 이어진 문자열을 하나 이상 담고, NULL 레코드는 65535옥텟까지 아무 값이나 담을 수 있습니다[1]. Zeek 는 TXT 응답을 `answers` 에 `TXT 길이 문자열` 형식으로 적고, 레코드 하나에 문자열이 여러 개면 공백으로 이어 붙입니다[8]. 예를 들어 `TXT 12 aGVsbG8td29y` 같은 값입니다(만든 예시). 한 도메인에 TXT·NULL 질의만 몰리는지, 응답 코드가 NXDOMAIN 만 계속되는지, `TC`(잘림) 비트가 켜진 뒤 같은 질의가 TCP 로 다시 오는지 봅니다. UDP DNS 메시지는 512옥텟으로 제한돼 있어서 그보다 큰 응답은 잘린 표시와 함께 옵니다[1]. dns.log 의 `proto` 로 UDP·TCP 를 구분합니다[5].

4. **직접 연결이 있었는지 봅니다.** 정상 도메인은 이름을 푼 뒤 그 IP 로 접속하지만, 터널 도메인은 DNS 질의만 오가고 직접 연결이 없는 경우가 많습니다. RITA 는 질의만 있고 직접 연결이 없는 도메인의 점수를 15% 올립니다(`c2_over_dns_direct_conn_score_increase`)[17]. 수동으로 볼 때는 그 도메인의 `answers` 에 나온 IP 를 conn.log 의 `id.resp_h` 에서 찾습니다.

5. **탐지 규칙에 걸렸는지 대조합니다.** 공개 Sigma 규칙 가운데 DNS 터널·유출과 관련된 조건은 아래와 같습니다. 필드 이름은 규칙이 쓰는 이름이라, 실제 로그에서는 대응하는 필드를 찾아야 합니다.

   | 규칙 | 조건 | 뜻 |
   |---|---|---|
   | Suspicious DNS Query with B64 Encoded String | `query` 에 `==.` 포함 | base64 채움 문자 뒤에 점이 오는 질의. 대소문자와 상관없는 문자열이라 소문자로 바뀐 Zeek `query` 에도 맞습니다[20] |
   | DNS TXT Answer with Possible Execution Strings | `record_type` 이 TXT 이고 `answer` 에 `IEX`·`Invoke-Expression`·`cmd.exe` | 명령이 내려오는 방향의 TXT 응답[21] |
   | Suspicious DNS Z Flag Bit Set (Zeek) | `Z` 가 0 이 아니고 `.arpa`·`.local` 등, NS·MX 질의, 137~139번 포트는 뺌 | 예약 비트를 쓰는 질의. DNSSEC 을 쓰는 정상 도메인이 걸릴 수 있습니다[22] |

   Suricata 규칙의 `dns.query` 버퍼는 요청 메시지의 질의 이름만 검사하고, 응답까지 보려면 `dns.queries.rrname` 을 씁니다[13]. 경보가 없다고 터널이 없었다는 뜻은 아니므로 1~4단계 집계 결과를 먼저 봅니다.

6. **흐름 기록만 있을 때.** 패킷도 DNS 로그도 없으면 53번 흐름의 크기와 길이로 이상 징후까지만 볼 수 있습니다. nfdump 로 `dst port 53` 흐름을 `-A srcip,dstip` 로 묶고 `-O bytes`·`-O bpp`(패킷당 바이트)로 정렬합니다[25]. 한 대학 캠퍼스의 하위 망(약 300명 사용)에서 iodine 으로 파일 전송·대화형 셸·웹 탐색을 흘린 시험에서는, 터널 클라이언트가 지정한 리졸버로 곧바로 보내면 같은 소스 포트를 계속 써서 요청들이 흐름 하나로 묶이고 흐름당 바이트가 크게 늘었습니다[26]. 터널 클라이언트가 자기 호스트의 로컬 리졸버를 거쳐 요청마다 소스 포트가 바뀌면 흐름 하나하나는 정상 DNS 와 거의 같았고, 약 200바이트 패킷이 늘어 패킷 크기 분포가 달라졌습니다[26]. 이 시험의 검출 기준(흐름당 5000바이트 초과이면서 55초 초과, 흐름의 패킷당 바이트 분포에서 KS 거리 0.15 초과)은 YAF 로 활성 타임아웃 60초·비활성 15초 흐름을 만든 그 망의 값입니다[26]. 구간당 바이트·패킷·흐름 수는 정상 DNS 에도 낮·밤 차이가 있어서, 이 값에 문턱을 두려면 시간대별로 따로 둬야 합니다[26]. 다른 망에 그대로 옮겨 쓰지 않습니다.

7. **출발지를 기기와 사람으로 좁힙니다.** 센서에서 본 출발지가 내부 DNS 서버라면 BIND 질의 로그에서 클라이언트 객체 ID(`client @0x…`) 다음에 오는 `IP#포트`[14]나 Windows DNS 분석 로그 257번(RESPONSE_SUCCESS) 이벤트의 `Destination`·`QNAME`·`QTYPE`[15] 으로 실제 클라이언트를 찾습니다. 그 IP 를 그 시각에 쓴 기기·계정은 [이 시각에 이 IP 를 누가 썼나](../user-activity/ip-attribution.md) 의 절차로 확인하고, 호스트 쪽 기록으로 넘어갑니다.

## 흔한 오판

**이름이 길고 무작위처럼 보이면 터널이다.** 정상 이름도 이런 집계와 규칙에 걸립니다. RITA 는 역방향 조회(`.arpa`)와 `.local` 을 집계에서 빼고[19], Z 비트 규칙은 DNSSEC 을 쓰는 정상 도메인을 오탐으로 적어 둡니다[22]. 네임 서버 이름은 `ns1`·`ns2` 처럼 숫자가 붙어 따로 된 글자 분포를 보입니다[27]. 후보 도메인이 나오면 네트워크 안의 몇 대가 그 도메인을 질의했는지, 그 도메인이 정상 서비스의 것인지부터 확인합니다.

**Zeek `query` 로 글자 분포를 계산한다.** `query` 는 소문자로 바뀐 값이라[6] 대소문자를 섞는 base64 인코딩[27]의 특징이 사라지고, 엔트로피도 실제보다 낮게 나옵니다. `original_query` 가 없으면 pcap 에서 다시 뽑습니다.

**Zeek tunnel.log 에 없으니 터널이 없다.** tunnel.log 는 Teredo·IPv6-in-IPv4 같은 캡슐화 트래픽을 기록하는 로그이고 DNS 터널과는 관계가 없습니다[10].

**응답 없는 질의가 많으니 서버가 응답을 거부했다.** Zeek 는 짝이 맞지 않는 질의·응답이 한 트랜잭션 ID 에 `DNS::max_pending_msgs`(기본 50)개, 서로 다른 트랜잭션 ID 에 걸쳐 `DNS::max_pending_query_ids`(기본 50)개 쌓이면 짝 맞추기를 포기합니다[5]. 캡처 손실이나 한 방향만 보이는 캡처에서도 응답 없는 줄이 생기므로, 같은 시간대의 캡처 손실 여부를 함께 봅니다.

**질의 이름 길이의 합이 보낸 자료의 양이다.** 이름에는 인코딩 부담과 세션 ID·카운터가 섞이고[27], 같은 질의를 다시 보내는 경우도 있습니다. 길이 합은 대략의 추정치로만 쓰고, 인코딩 방식을 모르면 원래 자료를 되살릴 수 없습니다.

**연구의 문턱값을 그대로 쓴다.** 흐름당 5000바이트·55초 같은 값은 그 망·그 도구·그 흐름 설정의 결과이고[26], RITA 의 100개 기준도 기본 설정값입니다[17]. 보고서에는 문턱값을 넘었다는 사실보다 실제 수치(고유 이름 수, 질의 수, 기간)를 씁니다.

## 보고서 문장 예

DNS 기록으로 확인되는 것은 "이 내부 IP(또는 내부 DNS 서버)가 이 시간대에 이 등록 도메인 아래로 고유 이름 몇 개, 질의 몇 건을 보냈고, 이름과 응답의 모양이 이렇다" 는 사실까지입니다. 질의 이름에 담긴 문자열이 실제로 어떤 파일의 조각인지, 정확히 몇 바이트가 나갔는지, 어떤 프로세스와 사용자가 보냈는지는 이 기록만으로 알 수 없습니다. 센서 위치와 캐시 때문에 일부 질의만 보였을 수도 있습니다. 아래 문장의 IP·도메인·시각은 모두 만든 예시입니다.

> 2026-03-14 02:00(UTC)부터 03:00(UTC)까지의 내부 DNS 서버 질의 로그에 10.0.5.23 이 example.net 아래로 질의한 기록이 6,120건 있고, 그 가운데 고유한 이름은 4,812개입니다. 이름의 첫 라벨은 대부분 52~63자의 영문·숫자 문자열이고, 질의 종류는 TXT 가 97% 입니다. 같은 시간대의 conn.log 에는 example.net 이 가리키는 IP 로 직접 연결한 기록이 없습니다.

> 같은 시간대 경계 센서의 dns.log 에서 이 질의들의 출발지는 내부 DNS 서버 10.0.0.53 으로 기록돼 있어, 실제 클라이언트는 서버 로그로 확인했습니다. 이 기록만으로는 질의 이름에 담긴 내용과 보낸 자료의 정확한 양을 알 수 없습니다.

## 함께 볼 페이지

- 같은 분류: [자료를 밖으로 보냈나](data-exfiltration.md)
- 침해: [악성 코드가 C2 서버와 통신했나](../intrusion/c2-communication.md)
- 사용자 행위: [이 시각에 이 IP 를 누가 썼나](../user-activity/ip-attribution.md)
- 분석 기법: [DNS 분석](../../03-techniques/analysis/dns-analysis.md), [비컨 찾기](../../03-techniques/analysis/beaconing.md), [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md), [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md), [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md)
- 기반 구조: [DNS](../../01-foundations/protocols/dns.md), [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)
- 호스트 쪽 기록: [Windows 자료를 밖으로 빼돌렸나](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/exfiltration/data-exfiltration/), [Linux 이름 해석 (hosts·resolv.conf)](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/name-resolution.html), [macOS hosts와 DNS 설정](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/network/hosts-dns.html)

## 참고 문헌

1. P. Mockapetris, "RFC 1035: Domain Names - Implementation and Specification". https://www.rfc-editor.org/rfc/rfc1035.txt
2. P. Hoffman, P. McManus, "RFC 8484: DNS Queries over HTTPS (DoH)". https://www.rfc-editor.org/rfc/rfc8484.txt
3. Z. Hu 외, "RFC 7858: Specification for DNS over Transport Layer Security (TLS)". https://www.rfc-editor.org/rfc/rfc7858.txt
4. Zeek, "dns.log". https://github.com/zeek/zeek-docs/blob/master/logs/dns.rst
5. Zeek, "base/protocols/dns/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dns/main.zeek.rst
6. Zeek, "src/analyzer/protocol/dns/events.bif". https://github.com/zeek/zeek/blob/master/src/analyzer/protocol/dns/events.bif
7. Zeek, "policy/protocols/dns/log-original-query-case.zeek". https://github.com/zeek/zeek/blob/master/scripts/policy/protocols/dns/log-original-query-case.zeek
8. Zeek, "scripts/base/protocols/dns/main.zeek". https://github.com/zeek/zeek/blob/master/scripts/base/protocols/dns/main.zeek
9. Zeek, "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
10. Zeek, "tunnel.log". https://github.com/zeek/zeek-docs/blob/master/logs/tunnel.rst
11. OISF, "Suricata User Guide: EVE JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
12. OISF, "Suricata User Guide: DNS Logging Changes for 8.0". https://github.com/OISF/suricata/blob/main/doc/userguide/upgrade/8.0-dns-logging-changes.rst
13. OISF, "Suricata User Guide: DNS Keywords". https://github.com/OISF/suricata/blob/main/doc/userguide/rules/dns-keywords.rst
14. ISC, "BIND 9 Configuration Reference". https://bind9.readthedocs.io/en/stable/reference.html
15. Microsoft, "DNS Logging and Diagnostics" (Windows Server 2012 R2). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn800669(v=ws.11)
16. Active Countermeasures, "RITA README". https://github.com/activecm/rita/blob/main/README.md
17. Active Countermeasures, "RITA default_config.hjson". https://github.com/activecm/rita/blob/main/default_config.hjson
18. Active Countermeasures, "RITA analysis/spagooper.go". https://github.com/activecm/rita/blob/main/analysis/spagooper.go
19. Active Countermeasures, "RITA database/tables.go". https://github.com/activecm/rita/blob/main/database/tables.go
20. SigmaHQ, "Suspicious DNS Query with B64 Encoded String". https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_susp_b64_queries.yml
21. SigmaHQ, "DNS TXT Answer with Possible Execution Strings". https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_susp_txt_exec_strings.yml
22. SigmaHQ, "Suspicious DNS Z Flag Bit Set". https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_dns_susp_zbit_flag.yml
23. Wireshark, "tshark(1)". https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
24. Wireshark, "Display Filter Reference: Domain Name System". https://www.wireshark.org/docs/dfref/d/dns.html
25. nfdump, "nfdump(1)". https://github.com/phaag/nfdump/blob/master/man/nfdump.1
26. Wendy Ellens, Piotr Żuraniewski, Anna Sperotto, Harm Schotanus, Michel Mandjes, Erik Meeuwissen, "Flow-Based Detection of DNS Tunnels", AIMS 2013, Lecture Notes in Computer Science 7943, pp. 124–135, 2013. doi:10.1007/978-3-642-38998-6_16
27. Kenton Born, David Gustafson, "Detecting DNS Tunnels Using Character Frequency Analysis", arXiv:1004.4358, 2010. doi:10.48550/arXiv.1004.4358
