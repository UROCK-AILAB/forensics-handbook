---
title: "DNS 분석"
parent: "기법 · 분석"
nav_order: 410
---

# DNS 분석 (DNS Analysis)

거의 모든 통신은 이름을 주소로 바꾸는 DNS 질의로 시작해서, DNS 기록을 보면 어느 호스트가 언제 어떤 도메인과 통신하려 했는지를 넓게 살펴볼 수 있습니다. 이 페이지는 Zeek dns.log, Suricata EVE dns 기록, pcap, DNS 서버 로그를 한 모양으로 맞춘 뒤 누가 물었고, 무엇을 물었고, 누가 답했고, 어떻게 답했는지를 차례로 보는 절차를 다룹니다. 필드 하나하나의 뜻은 각 아티팩트 페이지에 있고, 여기서는 여러 기록을 묶어 이상한 이름을 골라내고 연결 기록과 잇는 방법을 씁니다.

## 언제 쓰나

DNS 분석은 조사 범위가 넓을 때 먼저 씁니다. 연결 기록은 IP 만 남기지만 DNS 기록에는 사람이 읽을 수 있는 도메인 이름이 남아서, 악성 도메인 목록과 대조하거나 처음 보는 도메인을 찾을 때 연결 기록보다 빨리 좁힐 수 있습니다. 악성 코드가 C2 서버를 찾는 질의, 피싱 링크를 누른 뒤의 질의, DNS 메시지에 자료를 실어 보내는 터널처럼 이름 자체가 단서인 조사에 맞습니다.

DNS 기록은 질의·응답의 겉모습을 남기는 기록이라, 실제로 무엇을 주고받았는지는 연결·HTTP·TLS 기록과 함께 봐야 합니다. DNS 메시지의 구조는 [DNS](../../01-foundations/protocols/dns.md), 로그별 필드는 [DNS 기록 (dns.log)](../../02-artifacts/zeek/zeek-logs/dns-log.md) 과 [Suricata 프로토콜 기록](../../02-artifacts/suricata/eve-json/protocol-events.md), 서버 로그는 [DNS 서버 로그](../../02-artifacts/devices/dns-server-logs.md) 에서 다룹니다.

## 절차

1. **센서가 어느 구간을 봤는지 확인합니다.** 클라이언트가 내부 리졸버에 재귀 질의를 보내면 리졸버가 대신 바깥 서버에 묻습니다[5]. 그래서 센서가 리졸버 바깥에 있으면 바깥으로 나가는 질의의 출발지가 모두 리졸버로 보입니다. 이때 실제 클라이언트는 리졸버의 질의 로그에서 찾습니다. BIND 질의 로그 한 줄에는 클라이언트 IP·포트, 질의 이름, 클래스, 유형, 플래그, 질의를 받은 주소가 차례로 나옵니다[6]. 센서 위치별로 보이는 주소는 [어디서 캡처하나](../../01-foundations/capture/capture-points.md) 에서 다룹니다.

   ```text
   client @0x7f2a1c004d10 10.0.5.23#51724 (www.example.com): query: www.example.com IN A +E(0)K (10.0.0.53)
   ```

   위 줄은 만든 예시입니다. `+` 는 재귀 요청(RD) 비트가 켜졌다는 뜻이고, `E(0)` 은 EDNS 버전 0, `K` 는 유효한 서버 쿠키 없이 쿠키 옵션만 있었다는 뜻입니다[6].

2. **로그 설정 때문에 빠진 것이 없는지 확인합니다.** Suricata 는 `requests`·`responses` 로 요청과 응답 기록을 따로 켜고 끄며, `types` 에 질의 유형 목록을 적으면 그 유형만 남깁니다[3]. 기본값은 요청·응답 모두 기록, 유형은 전부입니다[3]. Zeek 는 원래 대소문자를 살린 질의 이름(`original_query`)과 권한·추가 섹션(`auth`·`addl`)을 정책 스크립트를 로드해야 남깁니다[2]. 실제 로그의 필드 목록과 센서의 설정 파일부터 확인합니다.

3. **기록을 한 모양으로 맞춥니다.** 도구마다 같은 값을 다른 이름으로 적고, Suricata 는 8.0 부터 DNS 기록 형식이 버전 3 으로 바뀌었습니다[4]. 섞인 기록을 합치기 전에 아래처럼 필드를 맞춥니다.

   | 볼 값 | Zeek dns.log | Suricata 8.0 (버전 3) | Suricata 7.x (버전 2) | tshark 필드 |
   |---|---|---|---|---|
   | 질의 이름 | `query` | `dns.queries[].rrname` | `dns.rrname` | `dns.qry.name` |
   | 질의 유형 | `qtype_name` | `dns.queries[].rrtype` | `dns.rrtype` | `dns.qry.type`(숫자) |
   | 응답 코드 | `rcode_name` | `dns.rcode` | `dns.rcode` | `dns.flags.rcode`(숫자) |
   | 응답 데이터 | `answers` | `dns.answers[].rdata` | `dns.answers[].rdata` | `dns.a`, `dns.aaaa`, `dns.cname`, `dns.txt` |
   | TTL | `TTLs` | `dns.answers[].ttl` | `dns.answers[].ttl` | `dns.resp.ttl` |
   | 트랜잭션 ID | `trans_id` | `dns.id` | `dns.id` | `dns.id` |

   출처는 차례로 Zeek[2], Suricata[3][4], Wireshark 표시 필터 목록[9]입니다. Suricata 버전 3 은 요청의 `type` 을 `query` 에서 `request` 로, 응답을 `answer` 에서 `response` 로 바꿨고, 응답 이벤트의 `src_ip` 를 클라이언트가 아니라 응답한 서버 주소로 적습니다[4]. 그래서 7.x 와 8.0 기록을 `src_ip` 로 함께 묶으면 출발지가 뒤바뀝니다. 버전 2 형식은 `version: 2` 설정으로 남길 수 있고, Suricata 9 에서 없어질 예정입니다[3].

   Sigma 규칙은 또 다른 이름을 씁니다. `category: dns` 규칙은 `query`·`record_type`·`answer` 를 쓰고[12][13], 2025-08-02 에 나온 분류 명세 2.1.0 의 `category: network`, `service: dns` 는 `dns.question.name`·`dns.question.type`·`dns.answers.data`·`dns.response.code` 를 씁니다[18].

4. **평소 모습부터 봅니다.** 질의 유형 분포, 응답 코드 분포, 질의를 받은 서버 목록을 먼저 뽑습니다. 내부 리졸버가 아닌 바깥 주소로 곧바로 53번 질의를 보낸 호스트가 있으면 설정이 다르거나 리졸버를 거치지 않으려는 프로그램이 있다는 뜻일 수 있습니다. pcap 이 있으면 `tshark -z dns,tree` 가 질의 유형·클래스 분포와 질의 이름 길이·DNS 페이로드 크기의 최대·최소·평균을 한 번에 보여 줍니다[7]. Wireshark 의 DNS 통계 창에서 요청·응답이 비정상으로 크면 DNS 터널이나 C2 통신일 가능성이 있습니다[8].

   ```sh
   # 만든 예시: 질의를 받은 서버와 포트·프로토콜별 개수 (Zeek TSV)
   zeek-cut id.resp_h id.resp_p proto < dns.log | sort | uniq -c | sort -rn
   # 만든 예시: 질의 유형과 응답 코드 분포
   zeek-cut qtype_name rcode_name < dns.log | sort | uniq -c | sort -rn
   # 만든 예시: pcap 에서 DNS 요약 통계
   tshark -r capture.pcapng -q -z dns,tree
   ```

5. **실패한 질의를 호스트별로 셉니다.** NXDOMAIN 은 RFC 1035 의 rcode 3(Name Error)으로, 질의한 이름이 없다는 응답입니다[5]. 이 응답이 한 호스트에 몰리면 없어진 서비스를 계속 찾는 설정 문제일 수도 있고, 이름을 자동으로 만들어 차례로 묻는 프로그램일 수도 있습니다. 몇 개의 서로 다른 이름이 실패했는지, 그 이름들의 모양이 비슷한지를 함께 봅니다.

   ```sh
   # 만든 예시: 호스트별 NXDOMAIN 수 (Zeek TSV)
   zeek-cut id.orig_h rcode_name < dns.log | awk -F'\t' '$2=="NXDOMAIN"{print $1}' | sort | uniq -c | sort -rn | head
   # 만든 예시: Suricata 8.0 EVE 에서 NXDOMAIN 응답의 질의 이름
   jq -r 'select(.event_type=="dns" and .dns.type=="response" and .dns.rcode=="NXDOMAIN") | .dns.queries[]?.rrname' eve.json | sort | uniq -c | sort -rn | head
   # 만든 예시: pcap 에서 rcode 3 응답
   tshark -r capture.pcapng -Y "dns.flags.response == 1 && dns.flags.rcode == 3" -T fields -e frame.time_epoch -e ip.dst -e dns.qry.name
   ```

6. **드물게 질의된 도메인을 찾습니다.** 업무용 도메인은 여러 호스트가 함께 묻지만, 한두 대만 묻는 도메인은 따로 볼 가치가 있습니다. 질의 이름을 등록 도메인 단위로 줄인 뒤 도메인마다 질의한 내부 호스트 수를 세고 적은 순으로 봅니다. RITA 도 드문 정도(prevalence)를 점수에 반영해서, 기본 설정에서 prevalence 가 2% 이하이면 점수를 15% 올리고 50% 이상이면 15% 내립니다[11]. 실시간 센서의 로그를 쌓아 가는 데이터셋에서는 처음 본 지 7일 이내인 대상의 점수도 15% 올립니다[11].

   ```sh
   # 만든 예시: 마지막 두 레이블로 줄인 도메인별 질의 호스트 수 (적은 순)
   zeek-cut id.orig_h query < dns.log \
     | awk -F'\t' '{n=split($2,a,"."); if(n>=2) print a[n-1]"."a[n]"\t"$1}' \
     | sort -u | cut -f1 | uniq -c | sort -n | head -50
   ```

   마지막 두 레이블로 자르는 방법은 `example.co.kr` 같은 2단계 최상위 도메인을 `co.kr` 로 뭉쳐 버리므로, 결과에 이런 값이 보이면 그 도메인은 세 레이블로 다시 셉니다.

7. **이름의 모양을 봅니다.** DNS 레이블은 63옥텟, 이름 전체는 255옥텟을 넘을 수 없습니다[5]. 터널은 이 한도 안에서 가장 왼쪽 레이블에 자료를 인코딩해 싣고, 리졸버 캐시를 피하려고 이 레이블을 매번 다르게 만듭니다[20]. 그래서 한 등록 도메인 아래 고유한 이름 수가 크게 늘어납니다. RITA 는 도메인별 하위 이름 수를 세어 기본 100·500·800·1000개를 기준으로 등급을 매기고[11], 결과는 `subdomains:>=100 sort:subdomains-desc` 같은 검색식으로 추립니다[10]. 인기 도메인 100만 개의 글자 빈도는 자연어처럼 Zipf 분포를 따르지만, 터널이 만든 이름은 글자가 고르게 퍼집니다[20]. 글자 분포를 따질 때는 Zeek `query` 가 원래 대소문자가 아닐 수 있으므로 `original_query` 나 pcap 을 씁니다[2]. pcap 에서는 `dns.qry.name.len`(이름 길이)과 `dns.count.labels`(레이블 수)로 긴 이름만 골라냅니다[9].

   ```sh
   # 만든 예시: 도메인별 고유 이름 수 (많은 순)
   zeek-cut query < dns.log | sort -u | awk -F. 'NF>=2{print $(NF-1)"."$NF}' | sort | uniq -c | sort -rn | head
   # 만든 예시: 100자가 넘는 질의 이름
   tshark -r capture.pcapng -Y "dns.flags.response == 0 && dns.qry.name.len > 100" -T fields -e ip.src -e dns.qry.name
   ```

   터널을 의심할 때의 전체 흐름과 보고서 문장은 [DNS 로 몰래 보냈나](../../04-scenarios/exfiltration/dns-tunneling.md) 에서 이어서 다룹니다.

8. **응답을 봅니다.** A·AAAA 응답의 주소, CNAME 으로 이어지는 이름, TTL 을 봅니다. UDP DNS 메시지는 512옥텟으로 제한돼 있고 TTL 은 부호 있는 32비트 정수의 양수 값입니다[5]. TXT 응답에 명령 문자열이 들어 있으면 명령을 내려받는 통로일 가능성이 있어서, Sigma 규칙은 TXT 응답에 `IEX`·`Invoke-Expression`·`cmd.exe` 가 들어 있으면 높은 등급으로 알립니다[13]. 응답 형식이 도구마다 어떻게 줄여 적히는지는 각 로그 페이지를 봅니다.

9. **이름과 연결을 잇습니다.** 이름을 물은 뒤 그 주소로 실제로 접속했는지는 응답의 주소가 연결 기록의 목적지에 나오는지로 확인합니다. 순서도 봅니다. 질의 시각 뒤에 그 주소로 가는 연결이 이어지면 이름 해석 다음 접속으로 읽을 수 있고, 질의 없이 연결만 있으면 호스트 캐시·hosts 파일·IP 를 직접 쓴 프로그램·암호화된 DNS 가운데 하나일 수 있습니다. 반대로 질의만 있고 그 주소로 가는 연결이 없는 도메인은 RITA 가 DNS 를 통한 C2 점수를 15% 올리는 조건입니다[11]. 두 로그를 잇는 명령은 [DNS 기록 (dns.log)](../../02-artifacts/zeek/zeek-logs/dns-log.md) 에, TLS 의 서버 이름(SNI)으로 잇는 방법은 [암호화된 트래픽 분석](encrypted-traffic.md) 에 있습니다. 한 도메인을 일정한 간격으로 계속 묻는 경우는 [비컨 찾기](beaconing.md) 의 방법으로 간격을 봅니다.

10. **탐지 규칙과 대조합니다.** 공개 Sigma 규칙 가운데 DNS 기록에 바로 쓸 수 있는 조건은 아래와 같습니다. 규칙의 필드 이름은 3단계 표로 실제 로그 필드에 맞춰 바꿉니다.

    | 규칙 | 로그 원본 | 조건 | 등급 |
    |---|---|---|---|
    | Suspicious DNS Query with B64 Encoded String | `category: dns` | `query` 에 `==.` 포함 | medium[12] |
    | DNS TXT Answer with Possible Execution Strings | `category: dns` | `record_type` 이 TXT 이고 `answer` 에 `IEX`·`Invoke-Expression`·`cmd.exe` | high[13] |
    | Cobalt Strike DNS Beaconing | `category: dns` | `query` 가 `aaa.stage.`·`post.1` 로 시작하거나 `.stage.123456.` 포함 | critical[14] |
    | Suspicious DNS Z Flag Bit Set | `product: zeek`, `service: dns` | `Z` 가 0 이 아니고 점이 있는 이름. `.arpa`·`.local` 과 일부 DNS 사업자 도메인, NS·MX 질의, `\x00` 로 끝나는 응답, 137~139번 포트는 뺌 | medium[15] |
    | DNS TOR Proxies | `product: zeek`, `service: dns` | `query` 가 `.onion`·`.onion.to`·`.tor2web.org` 등으로 끝남 | medium[16] |

    규칙을 오프라인 로그에 돌리는 방법과 경보 해석은 [탐지 규칙 활용](detection-rules.md) 에서 다룹니다. 경보가 없었다고 이상한 질의가 없었다는 뜻은 아니므로 5~9단계의 집계 결과를 먼저 봅니다.

11. **출발지를 기기·프로세스로 좁힙니다.** 센서에서 본 출발지가 내부 리졸버라면 1단계처럼 리졸버 로그로 클라이언트 IP 를 찾고, 그 시각에 그 IP 를 쓴 기기는 [DHCP 로그](../../02-artifacts/devices/dhcp-logs.md) 와 [이 시각에 이 IP 를 누가 썼나](../../04-scenarios/user-activity/ip-attribution.md) 의 절차로 확인합니다. 어느 프로세스가 물었는지는 네트워크 기록에 없습니다. Windows 에서 Sysmon 을 쓰고 있었다면 이벤트 ID 22(DNSEvent)가 프로세스가 DNS 질의를 실행할 때마다 성공·실패와 캐시 여부에 상관없이 남습니다(Windows 8.1 이후)[19]. 필드와 해석은 [Sysmon 3·22](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/event-logs/sysmon/3-22.html) 페이지에 있습니다. 호스트의 이름 해석 설정은 [Linux 이름 해석](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/name-resolution.html), [macOS hosts와 DNS 설정](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/network/hosts-dns.html) 에서 다룹니다.

## 도구

| 도구 | 쓰는 곳 | 비고 |
|---|---|---|
| Zeek | pcap·실시간 트래픽에서 dns.log 생성 | 질의·응답을 트랜잭션 ID 로 짝지어 한 줄로 남김[1][2]. `zeek-cut` 에 필드 이름을 주어 원하는 필드만 뽑음[21] |
| Suricata | EVE JSON 의 `dns` 이벤트 | 요청과 응답이 따로 된 이벤트[3]. 8.0 과 7.x 의 형식이 다름[4] |
| Wireshark·tshark | pcap 에서 원래 바이트·대소문자 확인, `-z dns,tree` 통계 | [Wireshark·tshark로 읽기](wireshark.md)[7][9] |
| RITA | Zeek 로그로 고유 하위 이름 수, 직접 연결 없는 도메인 점수 | 연결 로그용 가져오기 필터(`internal_subnets` 등)는 DNS 로그에 적용되지 않음[11] |
| Sigma 규칙 | 필드 조건으로 의심 질의 찾기 | [탐지 규칙 활용](detection-rules.md)[12]~[16] |
| jq·awk | JSON·TSV 로그 집계 | 위 절차의 예시 명령 |

## 함정과 한계

**캐시된 이름은 질의가 없습니다.** 호스트나 리졸버가 캐시한 답은 TTL 이 지날 때까지 다시 묻지 않아서, 네트워크 기록에는 처음 한 번만 남거나 아예 캡처 기간 밖에 있을 수 있습니다[5]. hosts 파일로 해결한 이름도 질의가 나가지 않습니다. 반대로 터널처럼 매번 새 이름을 만드는 통신은 캐시를 피하므로 질의가 빠짐없이 남습니다[20].

**암호화된 DNS 는 dns.log 에 없습니다.** dns.log 는 DNS over HTTPS(DoH)·DNS over TLS(DoT) 처럼 암호화된 DNS 를 담지 못합니다[1]. 이런 질의는 443·853 번 연결로만 보이므로 [암호화된 트래픽 분석](encrypted-traffic.md) 으로 넘어갑니다.

**줄 순서는 시간 순서가 아닙니다.** Zeek 문서의 예시에서도 dns.log 첫 줄의 `ts` 가 둘째 줄보다 늦습니다[1]. 집계 전에 시각으로 정렬합니다.

**대소문자.** Sigma 는 값을 기본으로 대소문자 구분 없이 비교해서[17], Zeek 규칙이 `qtype_name` 을 `ns`·`mx` 처럼 소문자로 적어도[15] 대문자로 기록된 Zeek 로그(`A`, `AAAA`)[1]와 맞습니다. 하지만 grep·jq 로 직접 찾을 때는 로그에 적힌 대로 대문자로 찾아야 합니다. 반대로 Zeek `query` 는 원래 대소문자가 아닐 수 있어서, 글자 분포를 계산할 때는 `original_query` 를 씁니다[2].

**Suricata 기록의 `type` 값.** EVE 문서는 필드 설명에서 `type` 을 `request` 또는 `response` 라고 적지만, 같은 문서의 버전 3 응답 예시에는 `"type": "answer"` 가 나옵니다[3]. 8.0 변경 문서는 응답이 `response` 라고 적습니다[4]. 필터를 짜기 전에 실제 로그의 값을 먼저 확인합니다.

**단순한 문자열 규칙.** `==.` 같은 조건은 base64 로 인코딩된 이름을 다 잡지도 못하고, 정상 이름이 걸릴 수도 있습니다. 규칙에도 오탐 원인이 "Unknown" 으로 적혀 있습니다[12]. Z 비트 규칙은 DNSSEC 을 쓰는 정상 도메인을 오탐 원인으로 적어 둡니다[15].

**모양만으로는 악성인지 알 수 없습니다.** 길거나 무작위처럼 보이는 이름이 나오면 몇 대가 물었는지와 그 도메인이 어떤 서비스의 것인지부터 확인합니다.

**흐름 기록만 있을 때.** 패킷도 DNS 로그도 없으면 53번 흐름의 크기와 지속 시간으로 이상 징후까지만 볼 수 있습니다. 방법은 [흐름 기록 분석](flow-analysis.md) 과 [DNS 로 몰래 보냈나](../../04-scenarios/exfiltration/dns-tunneling.md) 에 있습니다.

## 결과를 어떻게 해석하나

**증명하는 것.** 센서가 본 범위 안에서, 이 시각에 이 주소가 이 서버에 이 이름과 유형을 물었고 센서가 본 응답이 이것이었다는 사실입니다. 여러 기록을 합치면 어느 도메인을 몇 대가 얼마 동안 몇 번 물었는지, 응답 코드와 응답 주소가 어땠는지까지 숫자로 적을 수 있습니다.

**증명하지 못하는 것.** 이름을 물었다고 그 주소로 접속한 것은 아니어서, 접속 여부는 연결 기록으로 따로 확인합니다. 어떤 프로세스나 사용자가 물었는지는 네트워크 기록에 없고, 리졸버 바깥에서 캡처했다면 실제 클라이언트도 보이지 않습니다. 캐시·hosts 파일·암호화된 DNS 로 처리된 이름은 빠져 있을 수 있습니다. 이름이 이상하다는 것도 그 자체로 악성이라는 증거가 아니라 따로 확인할 후보라는 뜻입니다.

**시각.** Zeek dns.log 의 `ts` 는 그 연결에서 DNS 메시지를 처음 본 시각이고, `rtt` 는 요청을 본 때부터 응답이 시작될 때까지의 간격입니다[2]. `ts` 는 에포크 초(1970-01-01 00:00:00 UTC 부터 지난 초)로 적혀 있고, `zeek-cut -d` 는 이 값을 읽을 수 있는 시각으로, `-u` 는 UTC 시각으로 바꿉니다[21]. Suricata 는 요청과 응답이 따로 된 이벤트라 각자 `timestamp` 가 있습니다[3]. DNS 서버 로그와 Sysmon 은 그 기기의 시계로 기록하므로 센서 시계와 차이가 있는지 확인합니다. 여러 기록의 시각을 합치는 기준은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 과 [네트워크 타임라인](timeline.md) 을 따릅니다.

보고서에는 기록으로 확인되는 만큼만 씁니다. 아래 문장의 IP·도메인·시각·숫자는 모두 만든 예시입니다.

> 2026-03-14 01:00(UTC)부터 04:00(UTC)까지 경계 센서의 dns.log 에서 update.example.net 을 질의한 내부 호스트는 10.0.5.23 한 대이고, 질의는 180건, 응답은 모두 A 레코드 203.0.113.45 였습니다. 같은 시간대 conn.log 에는 10.0.5.23 에서 203.0.113.45:443 으로 가는 연결이 172건 있습니다. 어느 프로세스가 질의했는지는 이 기록만으로 알 수 없습니다.

## 참고 문헌

1. Zeek, "dns.log". https://github.com/zeek/zeek-docs/blob/master/logs/dns.rst
2. Zeek, "base/protocols/dns/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dns/main.zeek.rst
3. OISF, "Suricata User Guide: EVE JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
4. OISF, "Suricata User Guide: DNS EVE Logging Changes for 8.0". https://github.com/OISF/suricata/blob/main/doc/userguide/upgrade/8.0-dns-logging-changes.rst
5. P. Mockapetris, "RFC 1035: Domain Names - Implementation and Specification". https://www.rfc-editor.org/rfc/rfc1035.txt
6. ISC, "BIND 9 Configuration Reference". https://bind9.readthedocs.io/en/stable/reference.html
7. Wireshark, "tshark(1)". https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
8. Wireshark, "Wireshark User's Guide: Statistics". https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_statistics.adoc
9. Wireshark, "Display Filter Reference: Domain Name System". https://www.wireshark.org/docs/dfref/d/dns.html
10. Active Countermeasures, "RITA README". https://github.com/activecm/rita/blob/main/README.md
11. Active Countermeasures, "RITA default_config.hjson". https://github.com/activecm/rita/blob/main/default_config.hjson
12. SigmaHQ, "Suspicious DNS Query with B64 Encoded String". https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_susp_b64_queries.yml
13. SigmaHQ, "DNS TXT Answer with Possible Execution Strings". https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_susp_txt_exec_strings.yml
14. SigmaHQ, "Cobalt Strike DNS Beaconing". https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_mal_cobaltstrike.yml
15. SigmaHQ, "Suspicious DNS Z Flag Bit Set". https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_dns_susp_zbit_flag.yml
16. SigmaHQ, "DNS TOR Proxies". https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_dns_torproxy.yml
17. SigmaHQ, "Sigma Rules Specification". https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-rules-specification.md
18. SigmaHQ, "Sigma Taxonomy Appendix" (v2.1.0). https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-appendix-taxonomy.md
19. Microsoft, "Sysmon". https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
20. Kenton Born, David Gustafson, "Detecting DNS Tunnels Using Character Frequency Analysis", arXiv:1004.4358, 2010. doi:10.48550/arXiv.1004.4358
21. Zeek, "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
