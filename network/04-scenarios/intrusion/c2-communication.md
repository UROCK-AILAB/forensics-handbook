---
title: "악성 코드가 C2 서버와 통신했나"
parent: "시나리오 · 침입"
nav_order: 450
---

# 악성 코드가 C2 서버와 통신했나 (C2 Communication)

감염된 호스트는 공격자가 둔 명령 제어 서버 (Command and Control, C2) 에 주기적으로 접속해 명령을 받고 결과를 보냅니다. 내용이 암호화돼 있어도 접속 간격·크기·지속 시간, TLS 지문과 인증서, DNS 질의와 HTTP 헤더 모양은 Zeek·Suricata 로그와 흐름 기록에 남습니다. 이 페이지는 이 흔적들을 어떤 순서로 보고, 어디까지 보고서에 쓸 수 있는지를 다룹니다.

## 조사 질문

사고 대응에서 흔히 묻는 질문은 다섯 가지입니다. 호스트가 어떻게 감염됐나, 공격자가 열린 서비스나 취약점을 탐색했나, 호스트가 C2 나 수상한 IP 와 통신했나, 큰 자료를 밖으로 보냈나, 내부의 다른 장비와 통신했나입니다[26]. 이 페이지는 세 번째 질문을 다루고, 아래처럼 나눠서 답합니다.

- 이 내부 호스트가 일정한 간격으로 같은 외부 주소나 같은 서버 이름 표시 (Server Name Indication, SNI) 에 접속했나.
- 한 연결이 몇 시간 넘게 이어졌나.
- 목적지 도메인·IP·인증서·TLS 지문·User-Agent·URI 가 알려진 C2 지표와 겹치나.
- 같은 지표를 다른 내부 호스트도 썼나.

## 먼저 확인할 것

**시각 기준.** Zeek conn.log 의 `ts` 는 연결의 첫 패킷 시각이고[1], 기본 TSV 출력에는 epoch 초로 들어가고, `zeek-cut -d` 로 읽을 수 있는 시각으로, `-u` 로 UTC 시각으로 바꿉니다[4]. Suricata EVE 의 `timestamp` 는 `+0000` 같은 오프셋이 붙은 ISO 형식입니다[5]. 방화벽·프록시·DNS 서버 로그는 장비마다 현지 시각일 수 있으니, 합치기 전에 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 대로 기준을 맞춥니다.

**센서 위치와 수집 범위.** 센서가 프록시나 NAT 장비 바깥에 있으면 내부 호스트가 모두 같은 IP 로 보입니다. 그럴 때는 프록시 로그나 DHCP 로그로 실제 내부 호스트를 찾아야 합니다([IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md), [이 시각에 이 IP 를 누가 썼나](../user-activity/ip-attribution.md)). RITA 는 하루(24시간)를 시간대로 나눠 연결 분포를 보고, 연결이 보인 시간대 수가 `duration_min_hours_seen`(기본 6)에 못 미치면 지속 시간 점수를 계산하지 않으므로[9][12], 로그가 며칠 치 남아 있는지도 먼저 봅니다.

**센서 설정.** 같은 규칙이라도 설정에 따라 기록이 달라집니다. Suricata 의 EVE tls 기록은 기본으로 `subject`·`issuer`·`session_resumed` 만 남기고, `sni`·`serial`·`fingerprint`·`ja3`·`ja4` 는 확장 로깅 (extended) 을 켜야 남습니다[5]. JA3·JA4 계산은 `app-layer.protocols.tls.ja3-fingerprints`·`ja4-fingerprints` 로 켜는데, 배포하는 suricata.yaml 에는 이 줄이 주석 처리돼 있고 따로 정하지 않으면 꺼져 있다가 불러온 규칙이 요구할 때만 켜집니다[5][6][7]. Zeek 의 ssl.log 에 `ja3`·`ja3s` 필드가 생기려면 JA3 스크립트 패키지를 따로 설치해야 합니다[14]. 그래서 과거 로그에 지문 필드가 없으면 지문 비교는 할 수 없고, pcap 이 남아 있을 때만 다시 계산할 수 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | Zeek conn.log 또는 흐름 기록 | 내부 IP·외부 IP·포트별 연결 시각, 지속 시간, 주고받은 바이트 | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md), [흐름 기록](../../01-foundations/records/flow-records.md) |
| 2 | RITA 결과 | 비컨 점수, 긴 연결, DNS 하위 도메인 수, 위협 정보 목록 일치 | [비컨 찾기](../../03-techniques/analysis/beaconing.md) |
| 3 | Zeek ssl.log·x509.log, EVE tls | SNI, 인증서 일련번호·주체·발급자, JA3·JA4 | [TLS 지문](../../02-artifacts/fingerprints/ja3-ja4.md), [인증서로 서버 알아보기](../../02-artifacts/fingerprints/certificates.md) |
| 4 | Zeek dns.log, DNS 서버 로그 | 질의한 이름, 응답 IP, 레코드 종류 | [DNS 분석](../../03-techniques/analysis/dns-analysis.md), [DNS 서버 로그](../../02-artifacts/devices/dns-server-logs.md) |
| 5 | Zeek http.log, 프록시 로그 | Host, URI, User-Agent, 응답 코드 | [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md), [HTTP](../../01-foundations/protocols/http.md) |
| 6 | Suricata EVE alert | 어떤 규칙이 어느 흐름에 걸렸나 | [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md), [경고 기록](../../02-artifacts/suricata/eve-json/alert.md) |
| 7 | 방화벽 로그 | 허용·차단 여부, NAT 전후 주소 | [방화벽 로그](../../02-artifacts/devices/firewall-logs.md) |
| 8 | 호스트 기록 | 연결을 만든 프로세스 | 아래 "함께 볼 페이지" 의 Windows·Linux 핸드북 |

## 분석 흐름

1. **규칙적인 접속 후보를 뽑습니다.** Zeek 로그가 있으면 RITA 로 가져옵니다(`rita import --database=이름 --logs=경로`). 24시간 안의 최신 로그를 계속 쌓을 때만 `--rolling` 을 쓰고, 지난 사고의 로그에 `--rolling` 을 쓰면 결과가 틀릴 수 있습니다[8]. RITA 는 고유 연결 시각이 `unique_connection_threshold`(기본 4) 개 이상이고 전체 연결 수가 86400 개보다 적은 쌍만 비컨으로 분석하고, 86400 개 이상이면 스트로브 (strobe) 로 따로 표시합니다[9][11]. 비컨 점수는 접속 간격·데이터 크기·지속 시간·시간대 분포 네 부분 점수를 각각 0.25 씩 가중 평균한 값입니다[9][12]. 결과는 `beacon:>=90 sort:duration-desc` 같은 검색식으로 추리고, `rita view --stdout 데이터셋` 으로 CSV 로 뽑습니다[8]. 흐름 기록만 있으면 nfdump 의 `-A srcip,dstip,dstport` 로 쌍별로 묶고 `-s` 로 흐름 수·바이트 순위를 봅니다. 시간 범위는 `-t` 대신 `'first seen >= … and last seen <= …'` 필터로 정합니다[16]. 자세한 절차는 [비컨 찾기](../../03-techniques/analysis/beaconing.md) 와 [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md) 에 있습니다.

2. **긴 연결을 따로 봅니다.** 명령을 기다리며 연결을 열어 두는 C2 는 짧은 연결이 반복되지 않고 한 연결이 오래 이어집니다. RITA 기본 설정은 1시간(3600초) 이상을 base, 4시간·8시간·12시간을 low·medium·high 로 나눕니다[9]. conn.log 에서는 `duration` 과 `orig_bytes`·`resp_bytes` 를 함께 보는데, TCP 의 바이트 수는 시퀀스 번호로 계산해서 큰 연결에서 틀릴 수 있으므로 IP 헤더 기준인 `orig_ip_bytes`·`resp_ip_bytes` 도 봅니다[1].

3. **목적지가 네트워크 안에서 얼마나 흔한지 봅니다.** 업데이트·원격 측정·시간 동기화처럼 정상 소프트웨어도 규칙적으로 접속합니다. RITA 는 목적지에 붙은 내부 호스트 비율(prevalence)이 2% 이하면 점수를 15% 올리고, 50% 이상이면 15% 내립니다[9][10]. 후보 목적지마다 내부 호스트 몇 대가 접속했는지 세어 봅니다.

4. **TLS 흔적을 붙입니다.** 후보 연결의 `uid` 로 ssl.log 를 찾아 `server_name`(SNI), `established`, `cert_chain_fps` 를 보고, TLS 1.2 이하면 x509.log 의 인증서 일련번호·주체·발급자·유효 기간을 봅니다[2][3]. Zeek 에서 TLS 1.3 연결은 인증서가 암호화 구간에 있어 x509.log 가 생기지 않고, ESNI·ECH 를 쓰면 `server_name` 도 비어 있습니다[3]. JA3 는 목적지 IP·도메인이 바뀌어도 같은 클라이언트 프로그램이면 같은 값이 나오므로, 주소가 자주 바뀌는 C2 를 묶는 데 씁니다[13]. JA3·JA4 값은 공개 지문 목록(ja4db.com, JA4 저장소의 ja4plus-mapping.csv)과 비교합니다[15]. 계산 방법은 [TLS 지문](../../02-artifacts/fingerprints/ja3-ja4.md) 에 있습니다.

5. **DNS 와 HTTP 모양을 봅니다.** 공개 탐지 규칙에 C2 와 관련된 모양이 정리돼 있습니다. 아래 표의 필드 이름은 Sigma 규칙이 쓰는 이름이라, 실제 로그에 옮길 때는 대응하는 필드를 찾아야 합니다(Zeek dns.log 는 `answers`·`qtype_name`)[4].

   | 로그 | 필드와 모양 | 뜻 |
   |---|---|---|
   | DNS | `query` 가 `aaa.stage.`·`post.1` 로 시작하거나 `.stage.123456.` 을 포함 | Cobalt Strike DNS 비컨으로 알려진 질의[17] |
   | DNS | `query` 에 `==.` 포함 | Base64 로 보이는 문자열을 담은 질의[18] |
   | DNS | `record_type` 이 TXT 이고 `answer` 에 `IEX`·`Invoke-Expression`·`cmd.exe` | TXT 응답에 명령 실행 문자열[19] |
   | Zeek dns | `query` 가 `.onion`·`.onion.to`·`.onion.link` 등으로 끝남 | Tor 프록시 도메인 질의[24] |
   | 프록시 | `c-useragent` 가 빈 문자열 | PowerShell `Net.WebClient` 같은 요청에서 나오는 모양[20] |
   | 프록시 | `cs-host` 가 `api.telegram.org` 인데 `c-useragent` 에 Telegram·Bot 이 없음 | 봇이 아닌 프로그램의 Telegram API 접근[21] |
   | 프록시 | `c-uri` 에 `.pastebin.com/raw/` 등 | 붙여넣기 서비스의 원문 링크 접근. 2단계 악성 코드를 받아 오는 데 쓰입니다[22] |
   | Zeek http | `host` 가 `.xyz`·`.top`·`.tk` 등으로 끝나고, `uri` 가 `.exe`·`.dll`·`.bin` 등으로 끝나거나 `resp_mime_types` 가 `application/x-dosexec` 등 | 평판 낮은 최상위 도메인에서 실행 파일을 받는 요청[25] |
   | Zeek x509 | `certificate.serial` 이 `8BB00EE` | Cobalt Strike 기본 인증서[23] |

   DNS 하위 도메인이 아주 많은 경우는 DNS 를 통한 C2 나 터널일 수 있습니다. RITA 는 하위 도메인 수 100·500·800·1000 을 기준으로 등급을 나누고[9], 판단 방법은 [DNS 로 몰래 보냈나](../exfiltration/dns-tunneling.md) 에서 다룹니다.

6. **경보와 대조합니다.** Suricata 경보가 있으면 `flow_id` 로 같은 흐름의 alert·tls·http·flow 줄을 묶습니다[5]. 경보 한 줄로 주장할 수 있는 범위는 [경고 기록](../../02-artifacts/suricata/eve-json/alert.md) 을 따릅니다.

7. **범위를 넓힙니다.** 확인한 지표(도메인·IP·인증서 일련번호·JA3·JA4)로 전체 로그를 다시 검색해 같은 목적지나 같은 지문을 쓴 다른 내부 호스트를 찾습니다. IDS 경보에서 출발하면 해당 연결의 TLS 기록으로 호스트 이름을 확인하고, 위협 정보(MISP 지표 등)와 대조한 뒤, 같은 악성 호스트와 통신한 다른 내부 호스트까지 넓혀 갑니다[26]. 찾은 연결은 [네트워크 타임라인](../../03-techniques/analysis/timeline.md) 에 합칩니다.

8. **호스트 기록으로 넘깁니다.** 네트워크 기록만으로는 어느 프로세스가 연결을 만들었는지 알 수 없습니다. 후보 호스트와 시각을 정해 호스트 쪽 메모리·실행 흔적을 봅니다.

## 흔한 오판

**점수가 높으면 감염이다.** RITA 점수는 설정값(가중치·보정값)과 가져온 데이터에 따라 달라지고[9][10], 공개된 악성 코드 JA3 값도 표본에서 나온 예시일 뿐 그 악성 코드의 모든 버전에 해당하지는 않습니다[13]. 지표 일치는 조사할 대상을 좁히는 근거이지 감염을 확정하는 근거가 아닙니다. Client Hello 는 클라이언트 프로그램을 만들 때 쓴 패키지와 방식에 따라 정해지므로[13], 같은 방식으로 만든 정상 프로그램과 JA3 값이 겹칠 수 있습니다.

**RITA 에 안 나오면 C2 가 없다.** RITA 기본 설정은 내부↔내부, 외부↔외부 연결을 가져올 때 버리고, 외부→내부 연결도 무시합니다[9]. 그래서 내부 호스트를 거쳐 중계하는 C2 나 밖에서 안으로 들어오는 연결은 결과에 나오지 않습니다. 내부 프록시를 쓰는 네트워크에서는 프록시 IP 를 `always_included_subnets` 에 넣지 않으면 프록시와의 연결이 내부↔내부로 버려집니다[9]. SNI 로 묶여 비컨으로 분석된 연결은 IP 기준 분석에서 빠지므로, 같은 연결을 IP 목록에서 찾으면 없을 수 있습니다[12]. 이 조건들 때문에 결과가 비었다는 사실만으로 C2 가 없었다고 쓰지 않습니다.

**RITA 등급 이름을 그대로 옮긴다.** 기본 설정 파일의 비컨 등급 키는 base 50·low 70·medium 90·high 100 인데[9], 설정 문서의 설명은 50~69 를 low, 70~89 를 medium, 90 이상을 high 로 적어 한 단계씩 어긋납니다[10]. 보고서에는 점수 값을 쓰고, 등급 이름은 실제 출력으로 확인합니다.

**경보 `action: allowed` 는 통신이 성공했다는 뜻이다.** EVE 의 `alert.action` 은 drop(IPS 모드)이나 reject 규칙이 아니면 "allowed" 이고, 한 패킷이 여러 규칙에 걸릴 수 있어 최종 처리 결과도 아닙니다[5]. 통신이 성립했는지는 conn.log 의 `conn_state`(`SF` 는 정상 연결·종료, `S0` 는 응답 없는 시도)와 바이트 수로 확인합니다[1].

**인증서 규칙에 걸린 것이 없으면 기본 인증서를 쓰지 않았다.** TLS 1.3 연결은 Zeek 에서 x509.log 가 생기지 않아 인증서 일련번호 규칙이 걸릴 수 없습니다[3][23].

**Suricata 인증서 필드 이름을 문서대로 찾는다.** EVE tls 필드 목록은 `issuer` 인데 같은 문서의 예시에는 `"issuerdn"` 이 나옵니다[5]. 실제 eve.json 의 키 이름을 확인하고 검색합니다.

## 보고서 문장 예

네트워크 기록으로 확인되는 것은 "이 시간대에 이 내부 IP 가 이 외부 주소(또는 SNI)로 이런 간격·크기로 연결한 기록" 과 "그 연결의 지문·인증서·User-Agent 가 공개 지표와 같다는 사실" 까지입니다. 연결 내용(암호화 구간)과 연결을 만든 프로세스, 사람의 의도는 이 기록만으로 알 수 없습니다. 아래 문장의 IP·도메인·시각은 모두 만든 예시입니다.

> 2026-03-02 00:00(UTC)부터 2026-03-04 23:59(UTC)까지의 Zeek conn.log 에 내부 IP 10.20.30.41 이 198.51.100.23 의 443/tcp 로 맺은 연결이 4,310건 있습니다. 연결 간격의 중앙값은 60초이고, 각 연결에서 보낸 바이트는 모두 1 KB 이하입니다. 같은 연결의 ssl.log 에서 SNI 는 update.example.net 이고, 이 목적지에 접속한 내부 호스트는 전체 412대 중 10.20.30.41 한 대입니다. 이 기록만으로는 연결을 만든 프로세스와 주고받은 내용을 알 수 없습니다.

> 같은 기간 dns.log 에서 10.20.30.41 이 example.com 의 하위 도메인을 1,250개 질의한 기록이 있습니다. 질의 이름의 모양은 공개 탐지 규칙(Sigma)의 "Base64 로 보이는 DNS 질의" 조건과 일치합니다.

## 함께 볼 페이지

- 같은 분류: [내부에서 다른 PC 로 옮겨 갔나](lateral-movement.md), [웹 서버의 취약점을 노렸나](web-exploitation.md), [비밀번호를 무작위로 넣어 봤나](brute-force.md)
- 자료 유출: [자료를 밖으로 보냈나](../exfiltration/data-exfiltration.md), [DNS 로 몰래 보냈나](../exfiltration/dns-tunneling.md)
- 사용자 행위: [피싱 링크를 눌렀나](../user-activity/phishing-click.md)
- 분석 기법: [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md), [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md)
- 기반 구조: [TLS와 인증서](../../01-foundations/protocols/tls.md), [TCP 연결과 흐름](../../01-foundations/protocols/tcp-sessions.md)
- 호스트 쪽 기록: [Windows 메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/), [Windows 원격 제어 프로그램으로 누가 조작했나](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/remote-access-tool-abuse.html), [Linux 메모리 분석](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/memory-analysis.html), [Linux 라이브 응답 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/live-response.html)
- 클라우드: [VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/aws/vpc-flow-logs.html)

## 참고 문헌

1. Zeek, "base/protocols/conn/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
2. Zeek, "base/protocols/ssl/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/main.zeek.rst
3. Zeek, "x509.log". https://github.com/zeek/zeek-docs/blob/master/logs/x509.rst
4. Zeek, "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
5. OISF, "Suricata User Guide: EVE JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
6. OISF, "Suricata User Guide: JA3/JA4 Keywords". https://github.com/OISF/suricata/blob/main/doc/userguide/rules/ja-keywords.rst
7. OISF, "suricata.yaml.in". https://github.com/OISF/suricata/blob/main/suricata.yaml.in
8. Active Countermeasures, "RITA README". https://github.com/activecm/rita/blob/main/README.md
9. Active Countermeasures, "RITA default_config.hjson". https://github.com/activecm/rita/blob/main/default_config.hjson
10. Active Countermeasures, "RITA Configuration". https://github.com/activecm/rita/blob/main/docs/Configuration.md
11. Active Countermeasures, "RITA analysis/analysis.go". https://github.com/activecm/rita/blob/main/analysis/analysis.go
12. Active Countermeasures, "RITA analysis/beacons.go", "analysis/uconns.sql". https://github.com/activecm/rita/blob/main/analysis/beacons.go , https://github.com/activecm/rita/blob/main/analysis/uconns.sql
13. Salesforce, "JA3 README". https://github.com/salesforce/ja3/blob/master/README.md
14. Salesforce, "JA3 Zeek scripts (ja3.zeek, ja3s.zeek)". https://github.com/salesforce/ja3/blob/master/zeek/ja3.zeek , https://github.com/salesforce/ja3/blob/master/zeek/ja3s.zeek
15. FoxIO, "JA4+ README". https://github.com/FoxIO-LLC/ja4/blob/main/README.md
16. nfdump, "nfdump(1)". https://github.com/phaag/nfdump/blob/master/man/nfdump.1
17. SigmaHQ, "Cobalt Strike DNS Beaconing". https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_mal_cobaltstrike.yml
18. SigmaHQ, "Suspicious DNS Query with B64 Encoded String". https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_susp_b64_queries.yml
19. SigmaHQ, "DNS TXT Answer with Possible Execution Strings". https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_susp_txt_exec_strings.yml
20. SigmaHQ, "HTTP Request With Empty User Agent". https://github.com/SigmaHQ/sigma/blob/master/rules/web/proxy_generic/proxy_ua_empty.yml
21. SigmaHQ, "Telegram API Access". https://github.com/SigmaHQ/sigma/blob/master/rules/web/proxy_generic/proxy_telegram_api.yml
22. SigmaHQ, "Raw Paste Service Access". https://github.com/SigmaHQ/sigma/blob/master/rules/web/proxy_generic/proxy_raw_paste_service_access.yml
23. SigmaHQ, "Default Cobalt Strike Certificate". https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_default_cobalt_strike_certificate.yml
24. SigmaHQ, "DNS TOR Proxies". https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_dns_torproxy.yml
25. SigmaHQ, "HTTP Request to Low Reputation TLD or Suspicious File Extension". https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_susp_file_ext_from_susp_tld.yml
26. Milan Cermak, Tatiana Fritzová, Vít Rusňák, Denisa Sramkova, "Using relational graphs for exploratory analysis of network traffic data", Forensic Science International: Digital Investigation 45, 301563, 2023. doi:10.1016/j.fsidi.2023.301563
