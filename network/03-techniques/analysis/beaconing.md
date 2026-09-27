---
title: "비컨 찾기"
parent: "기법 · 분석"
nav_order: 400
---

# 비컨 찾기 (Beacon Detection)

감염된 PC 의 악성 코드는 명령을 받으려고 정해진 간격마다 같은 서버에 짧게 접속하는 경우가 많은데, 이렇게 되풀이되는 접속을 비컨 (beacon) 이라고 부릅니다. 한 번의 접속은 평범해 보여도 몇 시간치 기록을 모아 보면 간격과 크기가 고른 모양이 드러납니다. 이 페이지는 Zeek 로그·패킷 캡처·흐름 기록에서 출발지와 목적지 쌍별로 접속 시각을 뽑아 간격과 크기를 보는 절차와, 공개 도구 RITA 가 비컨 점수를 매기는 방법, 그리고 결과를 보고서에 쓸 수 있는 만큼만 해석하는 기준을 다룹니다.

## 언제 쓰나

경보나 침해 지표 없이 "이 네트워크에 밖으로 주기적으로 연락하는 PC 가 있나" 를 찾아야 할 때 씁니다. 암호화된 통신이라 내용을 볼 수 없어도 접속 시각과 바이트 수는 남기 때문에, 내용 분석이 막힌 곳에서도 쓸 수 있습니다. 이미 의심 주소가 있으면 그 주소로 가는 접속이 규칙적인지 확인하는 데도 쓰고, 한 PC 에서 비컨을 찾았으면 같은 목적지로 같은 모양의 접속을 하는 다른 PC 를 찾는 데도 씁니다.

조사 전체 흐름은 [악성 코드가 C2 서버와 통신했나](../../04-scenarios/intrusion/c2-communication.md) 시나리오에 있고, 이 페이지는 그 가운데 "규칙적인 접속 후보를 뽑고 판단하는" 부분을 자세히 다룹니다.

## 절차

아래 IP·도메인·시각·바이트 수는 모두 만든 예시입니다.

1. **기록의 범위와 위치를 확인합니다.** 비컨은 여러 시간에 걸쳐 되풀이되어야 드러나므로, 먼저 기록이 몇 시간치인지 봅니다. 한두 시간치 기록으로는 주기가 긴 비컨이 네 번도 잡히지 않을 수 있습니다. 그다음 센서가 어디에 있는지 확인합니다. 센서가 NAT 장비나 프록시 바깥에 있으면 내부 PC 여러 대가 주소 하나로 합쳐져 보이므로, 합쳐진 주소를 PC 로 나누는 방법은 [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md) 과 [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md) 를 봅니다.

2. **출발지와 목적지 쌍으로 묶습니다.** 기본 단위는 "내부 IP 하나와 외부 IP 하나" 의 쌍입니다. 목적지가 CDN 이나 클라우드처럼 IP 를 자주 바꾸거나 여러 이름이 IP 하나를 함께 쓰면, IP 대신 TLS 의 SNI 나 HTTP 의 Host 값으로 묶어야 같은 서버로 가는 접속이 한데 모입니다. RITA 도 비컨을 IP 쌍 기준(`ip`)과 SNI·HTTP 이름 기준(`sni`) 두 유형으로 나누고, 이름 기준 비컨에 쓰인 연결은 IP 기준 계산에서 뺍니다[3][5]. 출발지 포트는 접속마다 바뀌므로 묶는 기준에 넣지 않습니다.

3. **쌍마다 접속 시각 목록을 뽑습니다.** 기록 종류마다 "접속 한 번" 에 해당하는 시각이 다릅니다.

   | 기록 | 접속 한 번의 시각 | 크기 |
   |---|---|---|
   | Zeek `conn.log` | `ts`(연결의 첫 패킷 시각)[7] | `orig_bytes`(보낸 페이로드 바이트), `orig_ip_bytes`(보낸 IP 계층 바이트)[7] |
   | 패킷 캡처(tshark) | SYN 패킷의 `frame.time_epoch`(패킷 도착 시각)[9][10] | 연결별로 따로 합쳐야 함 |
   | 흐름 기록(nfdump) | `%tsr`(흐름 시작 시각, epoch 초)[12] | `%byt`·`%ibyt`[12] |
   | Suricata EVE `flow` | `flow.start`(흐름 시작)[13] | `flow.bytes_toserver`[13] |

   Zeek 로그가 TSV 형식이면 `zeek-cut` 으로 필요한 필드만 뽑습니다[8]. 아래는 한 쌍의 연결만 골라 시간순으로 정렬한 예입니다.

   ```
   cat conn.log | zeek-cut ts id.orig_h id.resp_h id.resp_p orig_ip_bytes \
     | awk '$2=="10.0.5.23" && $3=="203.0.113.50"' | sort -n
   1773900012.184211	10.0.5.23	203.0.113.50	443	1842
   1773900311.902144	10.0.5.23	203.0.113.50	443	1838
   1773900612.117530	10.0.5.23	203.0.113.50	443	1846
   1773900910.664018	10.0.5.23	203.0.113.50	443	1842
   ```
   (만든 예시)

   패킷 캡처만 있으면 TCP 연결을 여는 SYN 패킷(`tcp.flags.syn==1 && tcp.flags.ack==0`)만 골라 시각과 주소를 뽑습니다[11]. `-z io,stat` 은 정해진 초 단위 구간마다 패킷 수와 바이트 수를 세므로, 같은 필터로 1분마다의 SYN 수를 보면 주기가 눈에 띕니다[9].

   ```
   tshark -r capture.pcapng -Y "tcp.flags.syn==1 && tcp.flags.ack==0" \
     -T fields -e frame.time_epoch -e ip.src -e ip.dst -e tcp.dstport
   tshark -r capture.pcapng -q -z "io,stat,60,ip.dst==203.0.113.50 && tcp.flags.syn==1 && tcp.flags.ack==0"
   ```

   흐름 기록은 `nfdump -r 폴더 -O tstart -o "csv:%tsr,%sa,%da,%dp,%byt" 'src ip 10.0.5.23 and dst ip 203.0.113.50'` 처럼 시작 시각 순서로 정렬해 뽑습니다[12]. 흐름 기록을 거르고 합치는 방법은 [흐름 기록 분석](flow-analysis.md) 에 있습니다.

4. **간격을 계산해 모양을 봅니다.** 정렬한 시각에서 앞 줄과의 차이를 구하고, 간격별 개수를 셉니다.

   ```
   ... | awk 'NR>1{printf "%.0f\n", $1-prev} {prev=$1}' | sort -n | uniq -c
         1 299
         2 300
   ```
   (만든 예시. 실제로는 몇십~몇백 줄이 나옵니다.)

   사람이 쓰는 웹 접속은 간격이 몇 초에서 몇 시간까지 흩어지지만, 비컨은 간격이 한 값 주변에 몰립니다. 간격에 일부러 무작위 흔들림(지터, jitter)을 넣은 비컨은 간격이 한 값이 아니라 일정한 폭 안에 고르게 퍼집니다. 보낸 바이트 수도 같은 방법으로 봅니다. 보낸 양이 몇 개 값에 몰리면 같은 요청을 되풀이한 것일 가능성이 있고, RITA 도 연결별 크기가 고른지를 점수에 넣습니다[3].

5. **하루 중 언제 접속했는지 봅니다.** 간격만 보면 짧은 시간에 몰린 접속과 하루 종일 이어진 접속을 구분하지 못합니다. 기록 범위를 시간 단위 구간으로 나눠 구간마다 접속 수를 세면, 사람의 업무 시간에만 몰린 접속인지 밤낮 없이 고르게 이어진 접속인지 드러납니다. 구간별 접속 수가 들쭉날쭉하더라도 대부분의 구간에 접속이 있으면 지터를 넣은 비컨일 가능성이 있습니다.

6. **RITA 로 전체를 한 번에 점수 매깁니다.** 쌍이 많으면 3~5단계를 손으로 할 수 없으므로 RITA 로 모든 쌍에 점수를 매기고 위에서부터 봅니다. RITA 는 Zeek 로그(TSV·JSON)를 읽어 비컨, 긴 연결, DNS 터널 의심 도메인, 위협 정보 목록 일치를 찾습니다[1].

   ```
   rita import --database=case0319 --logs=/evidence/zeek
   rita view --stdout case0319 > case0319.csv
   ```

   지난 사고의 로그처럼 24시간보다 오래된 로그는 `--rolling` 없이 가져옵니다. `--rolling` 은 24시간 안의 최신 로그를 계속 쌓는 용도이고, 오래된 로그에 쓰면 결과가 틀릴 수 있습니다[1]. 데이터셋을 지우고 다시 만들 때는 `--rebuild` 를 씁니다[1]. `--stdout`(`-o`)은 데이터셋 이름 앞에 적어야 합니다[1]. 화면에서는 `beacon:>=90 sort:duration-desc` 처럼 `필드:값` 형식으로 검색하며, 검색 필드는 `severity`·`src`·`dst`·`beacon`·`duration`·`subdomains`·`threat_intel` 입니다[1]. 점수 계산 방법은 아래 [RITA 의 비컨 점수](#rita-의-비컨-점수) 에 있습니다.

   가져오기 전에 설정 파일(설치하면 `/etc/rita/config.hjson`, 다른 파일은 `-c` 로 지정)의 필터를 확인합니다[6]. 기본값은 `internal_subnets` 에 10.0.0.0/8·172.16.0.0/12·192.168.0.0/16·fd00::/8 을 넣고, 내부↔내부와 외부↔외부 연결을 가져올 때 버리며, `filter_external_to_internal: true` 라서 외부에서 내부로 연 연결도 무시합니다[2]. 내부에 프록시가 있으면 프록시 주소를 `always_included_subnets` 에 넣어야 프록시를 거친 연결이 빠지지 않습니다[2]. 이 필터는 conn 로그에만 적용되고 DNS 로그에는 적용되지 않습니다[2]. 설정을 바꾸면 `--rebuild` 로 데이터셋을 다시 만들어야 바로 반영됩니다[6].

7. **후보를 한 건씩 확인합니다.** 점수가 높은 쌍마다 목적지가 무엇인지부터 봅니다. 운영체제·백신 업데이트 확인, 시간 동기화(NTP), 모니터링 에이전트, 메신저, 클라우드 동기화 프로그램도 일정한 간격으로 같은 서버에 접속하므로 점수만으로는 구분되지 않습니다. 목적지 도메인과 인증서([인증서로 서버 알아보기](../../02-artifacts/fingerprints/certificates.md)), 클라이언트 TLS 지문([TLS 지문](../../02-artifacts/fingerprints/ja3-ja4.md)), 그 도메인을 물은 DNS 기록([DNS 분석](dns-analysis.md))을 확인하고, 같은 목적지에 같은 모양으로 접속하는 내부 PC 가 몇 대인지 셉니다. 조직 PC 대부분이 똑같이 접속하면 정상 프로그램일 가능성이 높고, 한두 대만 접속하면 더 자세히 봅니다. DNS 질의 이름에 도구 기본값이 그대로 남는 경우도 있습니다. 예를 들어 Sigma 의 Cobalt Strike DNS Beaconing 규칙은 `aaa.stage.`·`post.1` 로 시작하거나 `.stage.123456.` 을 포함하는 질의를 잡습니다[15]. 이런 규칙을 돌리는 방법은 [탐지 규칙 활용](detection-rules.md) 에 있습니다.

8. **호스트 기록과 잇습니다.** 네트워크 기록으로는 어느 PC 가 접속했는지까지만 알 수 있고, 어느 프로그램이 접속했는지는 알 수 없습니다. 비컨 시각에 그 PC 에서 어떤 프로세스가 네트워크 연결을 열었는지는 Windows 의 [라이브 응답](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/live-response/) 과 [메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/), Linux 의 [라이브 응답 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/live-response.html), macOS 의 [라이브 대응](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/process-acquisition/live-response/) 으로 확인합니다. 네트워크 기록과 호스트 기록을 한 시간축에 합치는 방법은 [네트워크 타임라인](timeline.md) 에 있습니다.

## 도구

| 도구 | 입력 | 비컨 찾기에 쓰는 기능 |
|---|---|---|
| RITA | Zeek 로그(TSV·JSON) | 쌍별 비컨 점수, 긴 연결, 스트로브 표시. Docker Engine 과 Compose 플러그인이 필요하고 CentOS 9 Stream·Rocky 9·RHEL 9·Ubuntu 22.04/24.04(amd64)를 지원합니다[1] |
| Zeek | 패킷 캡처·실시간 트래픽 | `conn.log` 의 시각·바이트 수. 필드 설명은 [연결 기록 (conn.log)](../../02-artifacts/zeek/zeek-logs/conn-log.md)[7] |
| tshark | pcap·pcapng | SYN 시각 목록(`-T fields -e frame.time_epoch`), 구간별 개수(`-z io,stat`)[9]. 사용법은 [Wireshark·tshark로 읽기](wireshark.md) |
| nfdump | NetFlow·IPFIX·sFlow 흐름 파일 | 시작 시각 정렬(`-O tstart`), epoch 초 출력(`%tsr`)[12] |
| Suricata | 패킷 캡처·실시간 트래픽 | EVE `flow` 기록의 `start`·`end`·`age`·방향별 바이트 수[13]. 형식은 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md) |

### RITA 의 비컨 점수

아래 계산은 RITA 한 도구가 쓰는 방법입니다. 비컨을 판정하는 기준으로 널리 합의된 방법은 아니지만, 코드가 공개되어 있어서 점수가 왜 그렇게 나왔는지 따라가 볼 수 있습니다.

**어떤 쌍을 계산하나.** 고유한 접속 시각이 `unique_connection_threshold`(기본 4) 개 이상이고 전체 연결 수가 86400 개보다 적은 쌍만 비컨으로 계산합니다[2][4]. 86400 은 하루 동안 1초에 한 번꼴인 수라서, 이 수 이상이면 비컨 대신 스트로브 (strobe) 로 따로 표시하고 기본 설정에서는 높음 (high) 등급에 넣습니다[2][4]. 아직 끝나지 않은 연결은 비컨 계산에 쓰지 않습니다[5]. 시각은 초 단위 정수로 다루고, 쌍마다 시각 목록은 최대 86400 개까지 모읍니다[3][5]. 비컨은 가장 최근 24시간치 기록으로 계산합니다[3][5].

**네 부분 점수.** 전체 점수는 네 부분 점수에 각각 가중치 0.25 를 곱해 더한 값이고, 가중치는 설정에서 바꿀 수 있지만 합이 1 이어야 합니다[2][3].

| 부분 점수 | 무엇을 보나 | 계산 |
|---|---|---|
| 시각 (timestamp) | 접속 간격이 고른가 | 0 이 아닌 간격들로 Bowley 왜도 점수(1 에서 왜도의 절댓값을 뺀 값)와 MAD 점수((중앙값 − MAD) ÷ 중앙값)를 구해 평균합니다. 사분위 범위(Q3 − Q1)가 10 보다 작거나 중앙값이 Q1 이나 Q3 와 같으면 왜도를 0 으로 봅니다. 시각이 4개 이상, 0 이 아닌 간격이 3개 이상이어야 합니다[3] |
| 크기 (datasize) | 연결마다 보낸 양이 고른가 | 연결별 출발지 IP 바이트 목록에 같은 왜도·MAD 계산을 합니다[3][5] |
| 히스토그램 (histogram) | 분석 기간 동안 고르게 접속했나 | 분석 시간 범위를 24개 구간(범위가 24시간이면 한 시간씩)으로 나눠 구간별 접속 수를 세고, 변동계수(표준편차 ÷ 평균) 점수(1 − 변동계수)와 이중봉(bimodal) 점수 가운데 큰 값을 씁니다[3] |
| 지속 (duration) | 분석 기간 내내 이어졌나 | 접속이 있는 구간이 `duration_min_hours_seen`(기본 6) 개 이상일 때만 계산합니다. (마지막 접속 − 첫 접속) ÷ (분석 범위) 와 가장 긴 연속 구간 수 ÷ `duration_consistency_ideal_hours_seen`(기본 12) 가운데 큰 값입니다[2][3] |

이중봉 점수는 접속이 있는 구간이 `histogram_bimodal_min_hours_seen`(기본 11) 개 이상일 때만 계산합니다. 구간별 접속 수를 가장 큰 값의 `histogram_mode_sensitivity`(기본 0.05, 곧 5%) 폭으로 묶은 뒤, 가장 많은 두 묶음에 든 구간 수를 접속이 있는 구간 수에서 `histogram_bimodal_outlier_removal`(기본 1)을 뺀 값으로 나눕니다[2][3]. 한 시간에 몇 번, 다른 시간에 몇십 번처럼 접속 수가 두 단계로 바뀌는 비컨이 이 점수를 잘 받습니다[3]. 가장 긴 연속 구간은 기간의 끝과 처음을 이어서 셉니다[3].

3단계의 만든 예시는 시각을 초 단위 정수로 바꾸면 간격이 299·301·298초입니다. 이렇게 몰려 있으면 사분위 범위가 10 보다 작아 왜도 점수가 1 이고, 중앙값이 299초, MAD 가 1초라서 MAD 점수는 (299 − 1) ÷ 299 ≈ 0.997 입니다. 그래서 시각 점수는 1 에 가깝습니다. 간격을 240~360초 사이로 흔들면 MAD 가 커져 시각 점수가 떨어지지만, 매시간 비슷한 수로 접속하는 한 히스토그램과 지속 점수는 거의 그대로입니다. 그래서 RITA 는 네 점수를 함께 쓰고, 변동계수 점수는 구간별 접속 수가 조금씩 흔들려도 전체적으로 고른 모양에 높은 점수를 줍니다[3].

**등급.** 전체 점수에 100 을 곱해 기본 기준 50·70·90·100 으로 나눕니다[2][4]. 50 미만은 기준 미달, 50~69 는 낮음, 70~89 는 중간, 90 이상은 높음입니다[6].

**보정.** 비컨 점수와 별개로 결과 전체의 위험 점수를 올리거나 내리는 보정값이 있습니다[2].

| 조건 | 보정 |
|---|---|
| 위협 정보 목록에 있는 목적지와 25MB(25,000,000 바이트) 이상 주고받음 | +15% |
| 목적지에 접속한 내부 호스트 비율이 2% 이하 / 50% 이상 | +15% / −15% |
| 목적지를 처음 본 날이 7일 이내 / 30일 이상 전(`--rolling` 데이터셋에서만) | +15% / −15% |
| HTTP Host 헤더가 없는 연결 | +10% |
| 드문 서명(signature)이 있는 연결 | +15% |
| DNS 로 묻기만 하고 직접 연결은 없는 도메인 | +15% |
| MIME 형식과 URI 가 맞지 않는 연결 | +15% |

긴 연결은 비컨과 따로 점수를 매기며, 기본 기준은 3600초(1시간)부터이고 14400·28800·43200초에서 등급이 올라갑니다[2]. 연결을 하나 열어 두고 계속 쓰는 C2 는 비컨 점수가 아니라 긴 연결 목록에 나타납니다.

## 함정과 한계

**RITA 기본 필터가 빼는 연결이 있습니다.** 내부↔내부와 외부→내부 연결은 기본으로 버리므로[2], 내부의 다른 PC 로 주기적으로 접속하는 모양(측면 이동 뒤의 내부 중계 등)은 RITA 결과에 나오지 않습니다. 이런 접속은 `internal_subnets` 를 조정하거나 3~5단계를 직접 해서 확인하고, 내부 이동은 [내부에서 다른 PC 로 옮겨 갔나](../../04-scenarios/intrusion/lateral-movement.md) 에서 따로 다룹니다.

**기록 기간이 짧으면 점수가 제대로 나오지 않습니다.** 히스토그램은 분석 시간 범위를 24개 구간으로 나누므로 범위가 짧으면 구간도 짧아지고, 지속 점수는 접속이 있는 구간이 6개 이상이어야 계산됩니다[2][3]. 비컨은 가장 최근 24시간치 기록으로 계산하므로[3][5], 하루에 네 번보다 적게 접속하는 느린 비컨은 기록이 며칠치여도 고유 시각 4개 조건을 넘지 못합니다. 이런 쌍은 3~5단계를 직접 해서 확인합니다.

**1초보다 짧은 간격은 사라집니다.** RITA 는 시각을 초 단위 정수로 다루고 간격이 0 인 값은 계산에서 빼므로[3], 같은 초 안에 여러 번 연 연결은 간격 계산에서 한 번처럼 보입니다. 1초에 한 번꼴 이상이면 비컨이 아니라 스트로브로 분류됩니다[4].

**흐름 기록에서는 긴 연결이 주기적인 연결처럼 보일 수 있습니다.** 흐름 내보내기 장비는 오래 이어지는 흐름을 일정 주기로 중간에 내보내므로[14], 연결 하나가 활성 시간 초과 (active timeout) 주기마다 레코드 하나씩으로 나뉩니다. 이 레코드의 시작 시각을 그대로 간격 계산에 넣으면 활성 시간 초과 값과 같은 간격의 "비컨" 이 나옵니다. 간격이 장비의 활성 시간 초과 값(예: 300초)과 같으면 [흐름 기록](../../01-foundations/records/flow-records.md) 페이지의 방법으로 레코드를 합친 뒤 다시 봅니다.

**NAT·프록시 뒤에서는 주소가 합쳐집니다.** 여러 PC 의 접속이 한 주소로 보이면 각각의 규칙적인 접속이 섞여 간격이 흐트러지고, 반대로 프록시 주소 하나에 모든 외부 접속이 몰려 목적지 구분이 사라집니다. 프록시 로그의 요청 URL·Host 나 TLS 의 SNI 로 실제 목적지를 되살려야 합니다.

**지터와 긴 주기는 점수를 낮춥니다.** 간격을 크게 흔들거나 몇 시간에 한 번만 접속하도록 만든 비컨은 시각 점수와 히스토그램 점수가 낮게 나옵니다. 점수가 낮다고 비컨이 없다고 결론 내리지 않고, 의심 목적지가 있으면 그 쌍만 골라 3~5단계를 직접 봅니다.

**정상 프로그램도 비컨처럼 보입니다.** 7단계의 정상 주기 통신은 대부분 점수가 높게 나옵니다. RITA 의 보정값 가운데 "흔한 목적지 −15%" 가 이런 통신의 점수를 조금 내리지만[2], 보정만으로 정상과 악성이 나뉘지는 않습니다.

## 결과를 어떻게 해석하나

### 증명하는 것 / 증명하지 못하는 것

비컨 분석으로는 "이 기간에 이 내부 주소가 이 목적지로 일정한 간격과 크기로 접속한 기록이 있다" 는 통계적 사실까지 확인됩니다. 간격의 분포, 접속 횟수, 첫 접속과 마지막 접속 시각, 보낸 양은 기록에서 그대로 확인됩니다.

업데이트 확인·NTP·모니터링·메신저 같은 정상 통신도 모양이 같아서, 비컨 분석만으로는 그 접속이 악성 코드의 것이라고 증명하지 못합니다. 어느 프로그램이 접속했는지도 알 수 없어서 호스트 기록이 필요합니다(8단계). 프록시나 NAT 뒤에서는 어느 PC 가 접속했는지, 실제 목적지가 어디인지도 다른 기록으로 확인해야 합니다. RITA 점수는 한 도구의 계산 결과이므로, 보고서에는 점수 대신 점수를 만든 근거(간격 분포·접속 횟수·기간)를 적습니다.

### 시각

기록마다 "접속 시각" 의 뜻이 다릅니다. Zeek `ts` 는 연결의 첫 패킷 시각이고[7], tshark `frame.time_epoch` 는 캡처 장비가 패킷을 받은 시각이며[10], nfdump `%tsr` 는 흐름 기록에 적힌 흐름 시작 시각입니다[12]. 셋 다 epoch 초라서 시간대가 없습니다. Suricata EVE 의 `flow.start` 는 시간대 오프셋이 붙은 문자열입니다[13]. 기록마다 시각을 찍는 지점이 달라 같은 접속이라도 시각이 조금씩 어긋나므로, 간격 계산에는 한 기록의 시각만 쓰고 여러 기록을 섞어 간격을 구하지 않습니다. 기록 사이의 시계 차이를 맞추는 방법은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에 있습니다.

간격은 두 시각의 차이라서 센서 시계가 일정하게 틀려 있어도 값이 바뀌지 않습니다. 대신 보고서에 첫 접속·마지막 접속 시각을 적을 때는 그 센서 시계의 오차를 함께 적습니다.

### 보고서 문장 예

> 2026-03-19 06:00:12 UTC 부터 06:15:10 UTC 까지 Zeek conn.log 에 내부 주소 10.0.5.23 이 203.0.113.50 의 443/tcp 로 연결한 기록이 4건 있으며, 연결 사이 간격은 298~301초이고 출발지가 보낸 IP 계층 바이트는 1,838~1,846 바이트입니다. 이 기록만으로는 연결을 연 프로그램을 알 수 없으며, 같은 목적지로 연결한 다른 내부 주소는 이 기간의 conn.log 에 없습니다.

(만든 예시)

## 참고 문헌

1. RITA README. https://github.com/activecm/rita/blob/main/README.md
2. RITA 기본 설정 파일(default_config.hjson). https://github.com/activecm/rita/blob/main/default_config.hjson
3. RITA 소스 코드, analysis/beacons.go. https://github.com/activecm/rita/blob/main/analysis/beacons.go
4. RITA 소스 코드, analysis/analysis.go. https://github.com/activecm/rita/blob/main/analysis/analysis.go
5. RITA 소스 코드, analysis/uconns.sql. https://github.com/activecm/rita/blob/main/analysis/uconns.sql
6. RITA 문서, "Configuration". https://github.com/activecm/rita/blob/main/docs/Configuration.md
7. Zeek 문서, base/protocols/conn/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
8. Zeek 문서, "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
9. tshark(1) 설명서. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
10. Wireshark 표시 필터 참조, frame. https://www.wireshark.org/docs/dfref/f/frame.html
11. Wireshark 표시 필터 참조, tcp. https://www.wireshark.org/docs/dfref/t/tcp.html
12. nfdump(1) 설명서. https://github.com/phaag/nfdump/blob/master/man/nfdump.1
13. Suricata 사용자 안내서, "Eve JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
14. B. Claise, "Cisco Systems NetFlow Services Export Version 9", RFC 3954, 2004. https://www.rfc-editor.org/rfc/rfc3954.txt
15. SigmaHQ, "Cobalt Strike DNS Beaconing" 규칙(net_dns_mal_cobaltstrike.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/network/dns/net_dns_mal_cobaltstrike.yml
