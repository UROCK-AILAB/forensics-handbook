---
title: "네트워크 타임라인"
parent: "기법 · 분석"
nav_order: 430
---

# 네트워크 타임라인 (Timeline)

패킷 캡처, 흐름 기록, Zeek·Suricata 로그, 방화벽·프록시·DNS 로그는 저마다 다른 시계로, 다른 순간을 찍어 둡니다. 이 페이지에서는 소스마다 시각 필드가 어느 순간을 뜻하는지 확인하고, 모두 UTC 로 바꾸고, 연결 식별자로 같은 연결을 묶어 한 시간축으로 합치는 순서를 다룹니다. 서로 다른 장비의 기록을 합쳤을 때 무엇까지 선후를 말할 수 있는지도 함께 봅니다.

## 언제 쓰나

사건 하나를 여러 기록으로 확인해야 할 때 씁니다. 예를 들어 내부 PC 가 어떤 도메인을 조회하고, 그 주소로 연결하고, 파일을 받고, 경보가 울린 순서를 한 줄로 이어 보려면 DNS 로그, 연결 로그, 파일 로그, 경보 로그를 합쳐야 합니다. 방화벽·프록시·DHCP·VPN 로그를 붙이면 그 시각에 그 내부 IP 를 누가 썼는지까지 이어 볼 수 있습니다.

기록마다 시각의 기준이 다르면 순서가 뒤바뀌어 보입니다. 로그 하나는 첫 패킷 시각을, 다른 로그는 감지한 시각을, 또 다른 로그는 수집기가 받은 시각을 찍고, 어떤 로그는 현지 시각에 연도도 없습니다. 그래서 합치기 전에 각 시각이 무엇을 뜻하는지부터 확인합니다. 시각을 저장하는 형식 자체(epoch, 오프셋, 정밀도)는 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)에 있습니다.

## 절차

아래 IP, 도메인, 식별자, 시각은 모두 만든 예시입니다.

### 1. 소스마다 시각 필드가 어느 순간인지 표로 정리한다

같은 연결을 다룬 로그라도 `ts` 가 가리키는 순간이 다릅니다. 타임라인에 올릴 필드와 그 뜻을 먼저 표로 정리해 두면, 나중에 순서가 이상해 보일 때 원인을 바로 찾을 수 있습니다.

| 소스 | 필드 | 찍히는 순간 | 형식 |
|---|---|---|---|
| pcap·pcapng | 패킷 시각 | 캡처 도구가 패킷을 받은 시각 | UTC 기준 값([pcap 형식](../../01-foundations/capture/pcap.md)) |
| Zeek conn.log | `ts` | 연결의 첫 패킷[1] | epoch 초(기본) |
| Zeek conn.log | `duration` | 연결 길이. 한 방향이 닫힌 뒤의 마지막 ACK 같은 패킷은 빠짐[1] | 초 |
| Zeek dns.log | `ts` | 그 연결에서 DNS 메시지를 가장 먼저 본 시각[2] | epoch 초 |
| Zeek http.log | `ts` | 요청이 일어난 시각[3] | epoch 초 |
| Zeek ssl.log | `ts` | SSL·TLS 연결을 처음 감지한 시각[4] | epoch 초 |
| Zeek files.log | `ts` | 파일을 처음 본 시각[5] | epoch 초 |
| Zeek x509.log | `ts` | 인증서 파일을 처음 본 시각(같은 파일의 files.log `ts` 를 그대로 씀)[6] | epoch 초 |
| Suricata EVE | `timestamp` | 이벤트 시각[11] | ISO 8601, UTC 오프셋 포함 |
| Suricata EVE flow | `flow.start`, `flow.end`, `flow.age` | 흐름의 시작, 마지막 패킷, 길이[11] | ISO 8601 + 오프셋, 초 |
| nfdump | `%ts`·`%te`, `%tr` | 흐름을 처음·마지막으로 본 시각, 수집기가 흐름 기록을 받은 시각[15] | 형식 태그마다 다름 |
| NetFlow v9 | `FIRST_SWITCHED`, `LAST_SWITCHED` | 흐름의 첫·마지막 패킷을 처리한 시각을 장비 가동 시간(sysUptime, ms)으로[17] | 장비 시계 기준 |
| syslog (RFC 3164) | TIMESTAMP | 장비의 현지 시각, "Mmm dd hh:mm:ss" 형식, 연도 없음[18] | 현지 |
| syslog (RFC 5424) | TIMESTAMP | 날짜 "T" 시각, 끝에 "Z" 나 ±hh:mm, 소수 초는 6자리까지[19] | 오프셋 명시 |

Zeek 로그 사이의 차이는 연결 하나를 두고도 드러납니다. conn.log 의 `ts` 는 TCP 첫 패킷이고, ssl.log 의 `ts` 는 Zeek 가 TLS 로 알아본 시각이라 조금 뒤이며, files.log 의 `ts` 는 그 연결 안에서 파일이 처음 보인 시각입니다[1][4][5]. x509.log 의 `ts` 는 인증서를 파일로 처음 본 시각이라 같은 인증서의 files.log `ts` 와 값이 같습니다[6]. 각 로그의 나머지 필드는 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md)와 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)에 있습니다.

Suricata flow 이벤트의 `timestamp` 는 흐름 시작 시각이 아닙니다. 같은 흐름인데 flow 이벤트의 `timestamp` 가 06:13:21 이고 `flow.start` 가 06:13:33 이어서 `timestamp` 가 흐름 시작보다 12초 이른 기록도 있습니다[11]. 흐름의 시작과 끝은 `flow.start` 와 `flow.end` 로 올립니다.

흐름 기록은 수집기가 받은 시각(`%tr`)과 흐름 자체의 시각(`%ts`·`%te`)이 따로 있습니다[15]. 수신 시각은 장비가 흐름을 내보낸 뒤라 늦게 찍히므로 사건 시각으로 쓰지 않습니다. 흐름 기록 필드는 [흐름 기록](../../01-foundations/records/flow-records.md)과 [흐름 기록 분석](flow-analysis.md)에 있습니다.

### 2. 모든 시각을 UTC 로 바꾸고 원래 값도 함께 둔다

합칠 때는 모든 행을 UTC epoch 초(소수 포함)로 바꾸고, 원래 적힌 값은 옆 열에 그대로 둡니다. 원래 값이 있어야 변환이 틀렸을 때 다시 확인할 수 있고, 보고서에서 근거를 보여 줄 수 있습니다.

Zeek 는 TSV 로그의 `ts` 를 epoch 초로 쓰고, JSON 로그도 기본값(`LogAscii::json_timestamps = JSON::TS_EPOCH`)이면 epoch 초 실수로 씁니다[8]. 이 설정을 바꾼 센서는 다른 형식으로 쓰므로, 받은 로그의 `ts` 가 소수점 있는 epoch 초인지 먼저 봅니다. `zeek-cut` 으로 필드를 뽑으면 epoch 값이 그대로 나옵니다[7].

```
zeek-cut ts uid id.orig_h id.orig_p id.resp_h id.resp_p proto duration < conn.log
```

`zeek-cut -d` 는 epoch 를 사람이 읽는 시각으로 바꾸고, `-u` 는 UTC 로 바꿉니다[7]. 두 옵션의 기본 형식은 `%Y-%m-%dT%H:%M:%S%z` 이고 `-D`·`-U` 로 형식을 바꿉니다[7]. 이 기본 형식에는 소수 초가 없어서 1초 안에 일어난 일의 순서가 사라집니다. 정렬과 대조에는 원래 epoch 값을 쓰고, 사람이 읽는 시각은 보고서 표에만 씁니다.

Suricata EVE 의 `timestamp` 는 `2017-04-07T22:24:37.251547+0100` 처럼 끝에 UTC 오프셋이 붙고, 이 오프셋은 `+0000`, `+0100`, `+0200`, `-0800` 처럼 센서마다 다를 수 있습니다[11]. 오프셋을 떼어 버리지 말고 그 값으로 UTC 를 계산합니다. flow 이벤트의 시작·끝만 뽑으려면 jq 를 씁니다.

```
jq -r 'select(.event_type=="flow") | [.flow.start, .flow.end, .flow_id, .src_ip, .src_port, .dest_ip, .dest_port, .proto] | @tsv' eve.json
```

nfdump 는 같은 시각을 여러 형식으로 출력합니다. `%tsr`·`%ter`·`%trr` 는 epoch 초 소수이고, `%tsg`·`%teg`·`%trg` 는 GMT 로 나타낸 시각입니다[15]. 타임라인에는 epoch 형식을 뽑고, `-O tstart` 로 시작 시각 순으로 정렬합니다[15].

```
nfdump -r nfcapd.202603020030 -O tstart -o "csv:%tsr,%ter,%trr,%pr,%sa,%sp,%da,%dp,%pkt,%byt"
```

GMT 가 붙지 않은 `%ts`·`%te`·`%tr` 는 분석 PC 의 현지 시각으로 바꿔 출력하므로[28], 사람이 읽는 시각이 필요하면 `%tsg` 같은 GMT 형식을 씁니다. nfcapd 를 `-Z` 로 돌린 수집기는 파일 이름 끝에 현지 시간대 오프셋을 붙이므로[16], 파일 이름의 시각도 그 오프셋을 보고 읽습니다.

NetFlow v9 원본 패킷을 직접 읽는 경우, `FIRST_SWITCHED`·`LAST_SWITCHED` 는 장비가 켜진 뒤 지난 밀리초라서 그대로는 날짜가 되지 않습니다[17]. 같은 패킷 헤더의 sysUptime(장비 가동 시간)과 UNIX Secs(패킷이 장비를 떠난 UTC 초)로 환산해야 하고[17], 결과는 장비 시계를 따릅니다.

패킷 캡처는 tshark 로 `frame.time_epoch` 를 뽑거나 `-t ud` 로 UTC 날짜·시각을 봅니다([Wireshark·tshark로 읽기](wireshark.md)). `frame.time_utc` 필드는 Wireshark 4.2.0 부터 있습니다[12].

syslog 는 형식부터 봅니다. RFC 3164 형식이면 시각이 장비의 현지 시각이고 연도가 없어서[18], 장비의 시간대 설정과 로그를 받은 연도를 따로 확인해 채워야 합니다. 12월 31일에서 1월 1일로 넘어가는 로그는 연도를 잘못 붙이기 쉽습니다. RFC 5424 형식은 시각 값이 있으면 오프셋이 반드시 붙고 윤초를 쓰지 않으므로[19] 그대로 UTC 로 바꿉니다. 방화벽·프록시·DNS 서버 로그의 형식은 [방화벽 로그](../../02-artifacts/devices/firewall-logs.md), [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md), [DNS 서버 로그](../../02-artifacts/devices/dns-server-logs.md)에 있습니다.

### 3. 장비마다 시계가 얼마나 다른지 확인한다

여러 장비의 기록을 한 줄로 잇는 일은 시계가 맞을 때 쉽습니다[21]. 패킷이 장비 사이를 지나는 데는 시간이 걸리므로, 시계가 맞으면 여러 장비의 시각으로 패킷이 지나간 경로를 확인할 수도 있습니다[21]. 기록된 시각이 틀리는 이유로는 시계를 권위 있는 시간 소스와 정기적으로 맞추지 않은 경우, 초나 분을 빼고 기록한 경우, 공격자가 기록된 시각을 바꾼 경우가 있습니다[21].

시차는 두 소스가 함께 본 사건으로 잽니다. 같은 구간을 두 센서가 캡처했다면 같은 패킷을 짝지어 시각 차를 구할 수 있고, 방법은 [큰 캡처 파일 다루기](../acquisition/large-captures.md)의 5단계에 있습니다. 로그끼리는 같은 연결의 시작 시각(Zeek conn.log `ts`, Suricata `flow.start`, 방화벽의 연결 허용 로그)을 여러 건 비교해 차이가 일정한지 봅니다. 차이가 일정하면 그 값을 시차로 적고 보정한 열을 따로 만들며, 원래 열은 지우지 않습니다. 차이가 들쭉날쭉하면 보정하지 않고 "두 장비의 시계 차이는 확인되지 않았다" 고 적습니다.

### 4. 연결 식별자로 같은 연결을 묶는다

시각만으로 행을 짝지으면 같은 순간에 일어난 다른 연결이 섞입니다. 도구마다 연결을 묶는 식별자가 있으니 먼저 그것으로 묶습니다.

Zeek 는 연결마다 `uid` 를 붙이고, conn.log·dns.log·http.log·ssl.log 가 같은 `uid` 필드를 씁니다[1][2][3][4]. 파일에는 `fuid` 가 붙어서 http.log 의 `orig_fuids`·`resp_fuids` 와 files.log 의 `fuid` 가 이어지고, files.log 에도 그 파일이 오간 연결의 `uid` 가 들어 있습니다[3][5][9]. Suricata 는 한 흐름의 alert·http·fileinfo·anomaly·flow 이벤트에 같은 `flow_id` 를 붙이고, 경보가 없는 흐름도 똑같이 붙입니다[11].

```
jq -c 'select(.flow_id==1676750115612680)' eve.json
```

Zeek 와 Suricata 처럼 서로 다른 도구의 기록을 이을 때는 커뮤니티 ID (Community ID)를 씁니다. 커뮤니티 ID v1 은 시드(기본 0, 2바이트), 두 IP 주소, 프로토콜 번호, 채움 값 0, 두 포트를 네트워크 바이트 순서로 이어 SHA1 을 구하고, 그 20바이트를 base64 로 바꿔 앞에 `1:` 을 붙인 값입니다[22]. 주소와 포트를 숫자가 작은 쪽부터 놓으므로 방향이 반대인 두 기록도 같은 값이 나오고, ICMP 는 type·code 를 포트 자리에 씁니다[22]. 값은 `1:hO+sN4H+MG5MY/8hIrXPqc4ZQz0=` 같은 모양입니다[22]. Security Onion 은 Zeek 와 Suricata 의 커뮤니티 ID 기능을 켜 두고, 이 값이 없는 로그에는 Elasticsearch 처리기로 계산해 넣습니다[23]. Sigma 분류 부록의 네트워크 범주(connection·dns 서비스)에서는 이 값을 `network.community_id` 필드로 부릅니다[25].

커뮤니티 ID 는 다섯 값만으로 만들기 때문에, 같은 주소·포트 조합을 나중에 다시 쓴 연결도 같은 값이 됩니다. 이런 충돌은 흐름의 시각 정보로 구분합니다[22]. 그래서 식별자가 같더라도 시작 시각이 연결 길이 이상 떨어져 있으면 다른 연결로 봅니다. VLAN·MPLS 와 IP 안에 IP 를 넣는 터널은 v1 이 다루지 않아서[22], 도구마다 이 부분을 다르게 처리하면 값이 맞지 않을 수 있습니다.

식별자가 없는 방화벽·프록시·NAT 로그는 다섯 값과 시간 범위로 짝짓습니다. NAT 를 거치면 주소와 포트가 바뀌므로, 변환 전후 주소를 잇는 방법은 [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md)을 봅니다.

### 5. 한 표로 합치고 UTC 시각으로 정렬한다

로그 파일 안의 줄 순서는 시간 순서가 아닙니다. Zeek dns.log 에서도 `ts` 가 1591367999.306059 인 줄이 1591367999.305988 인 줄보다 먼저 나올 수 있습니다[10]. 여러 소스를 합칠 때는 줄을 이어 붙이기만 하지 말고 UTC epoch 열로 다시 정렬합니다. 패킷 캡처 파일을 시간순으로 합치는 방법은 [큰 캡처 파일 다루기](../acquisition/large-captures.md)에 있습니다.

합친 표에는 최소한 UTC 시각, 원래 시각 값, 소스(파일 이름과 줄 번호), 연결 식별자, 주소·포트, 내용을 둡니다. 아래는 합친 결과의 예입니다(만든 예시).

| UTC | 원래 값 | 소스 | 식별자 | 내용 |
|---|---|---|---|---|
| 2026-03-02 00:31:04.812 | 1772411464.812 | Zeek dns.log | `Cq2Fx81` | 10.1.2.30 이 `update.example.com` 을 조회, 응답 203.0.113.50 |
| 2026-03-02 00:31:05.020 | 1772411465.020 | Zeek conn.log | `Cz7Yk42` | 10.1.2.30:51544 → 203.0.113.50:443 TCP 연결 시작, duration 41.2초 |
| 2026-03-02 00:31:05.061 | 1772411465.061 | Zeek ssl.log | `Cz7Yk42` | TLS 감지, SNI `update.example.com` |
| 2026-03-02 00:31:05.140 | 2026-03-02T09:31:05.140000+0900 | Suricata EVE alert | community ID 일치 | 경보 발생 |
| 2026-03-02 00:31:05 | Mar  2 09:31:05 | 방화벽 syslog (RFC 3164) | 다섯 값 일치 | 허용 로그, 연도는 수집 기록으로 채움 |

이 표에서 방화벽 행은 초 단위라 Zeek 행과 1초 안의 순서를 비교할 수 없습니다. 이런 행은 같은 초의 맨 앞이나 맨 뒤에 놓지 말고 "같은 초" 로 묶어 보여 줍니다.

### 6. 관심 구간으로 좁힌다

타임라인이 커지면 사건 전후 구간만 잘라 봅니다. 도구마다 시각 조건을 쓰는 방법이 다르고, 시간대를 빼면 현지 시각으로 읽는 도구가 많습니다.

Wireshark 표시 필터에 날짜·시각을 쓸 때 시간대를 빼면 현지 시각으로 해석하므로, 끝에 "Z" 나 오프셋을 붙입니다[13]. 필드 참조를 쓰면 화면에서 고른 패킷 기준으로 "그 전 5분" 같은 필터를 만들 수 있습니다[13].

```
frame.time_relative >= ${frame.time_relative} - 300
```

nfdump 는 `'first seen >= 2026-03-02T00:25:00 and last seen <= 2026-03-02T00:40:00'` 처럼 흐름의 시작·끝 시각으로 거르고, ISO 8601 형식으로 밀리초까지 씁니다[15]. 예전의 `-t` 시간 창 옵션은 이제 레거시라서 새로 쓸 때는 이 필터를 씁니다[15]. editcap 으로 캡처 파일을 시간 구간으로 자르는 방법은 [큰 캡처 파일 다루기](../acquisition/large-captures.md)의 3단계에 있습니다.

Sigma 규칙의 시각 수식어(`minute` 등)는 날짜 값에서 숫자만 꺼내고, 시간대나 형식을 바꾸지 않습니다[24]. 로그를 UTC 로 바꾸지 않은 채 규칙을 돌리면 "업무 시간 밖" 같은 조건이 시간대만큼 어긋납니다.

### 7. 단말과 클라우드 기록을 붙인다

네트워크 기록으로 확인되는 것은 주소와 포트까지라서, 어느 프로그램이나 사용자가 그 연결을 만들었는지는 단말 기록으로 확인합니다. DHCP·VPN 로그로 그 시각에 내부 IP 를 받은 장비와 계정을 먼저 찾고([DHCP 로그](../../02-artifacts/devices/dhcp-logs.md), [VPN 서버 로그](../../02-artifacts/devices/vpn-logs.md)), 그 장비의 타임라인과 UTC 로 맞춰 붙입니다. 운영체제별 타임라인 작성은 [Windows 타임라인](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/), [macOS 타임라인](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/timeline/), [Linux 타임라인](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html), [클라우드 타임라인](https://urock-ailab.github.io/forensics-handbook/cloud/03-techniques/analysis/timeline.html)에 있습니다. 전체 흐름은 [이 시각에 이 IP 를 누가 썼나](../../04-scenarios/user-activity/ip-attribution.md)에서 다룹니다.

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| zeek-cut | Zeek TSV 로그에서 필드를 골라 뽑고, `-d`·`-u` 로 시각을 바꿔 봅니다[7] |
| jq | Zeek JSON·Suricata EVE 에서 필드를 뽑고 `flow_id` 로 거릅니다[11] |
| tshark | 패킷 시각을 `frame.time_epoch` 나 UTC 로 뽑습니다([Wireshark·tshark로 읽기](wireshark.md)) |
| mergecap·reordercap·editcap·capinfos | 캡처 파일을 시간순으로 합치고, 시각을 옮기고, 구간을 자릅니다([큰 캡처 파일 다루기](../acquisition/large-captures.md)) |
| nfdump | 흐름 기록을 시작 시각 순으로 정렬하고 epoch 로 출력합니다[15] |
| 커뮤니티 ID 구현 | 명세 저장소에 pycommunityid 와 pcap 에서 값을 계산하는 스크립트가 있습니다[22] |
| Security Onion | Zeek·Suricata 의 커뮤니티 ID 기능을 켜 두고, 경보·대시보드·헌트 화면의 이벤트에서 해당 PCAP 으로 넘어갑니다[23][26] |

## 함정과 한계

- **로그마다 `ts` 뜻이 다릅니다.** conn.log 는 첫 패킷, ssl.log 는 감지 시각, files.log·x509.log 는 파일(인증서)을 처음 본 시각입니다[1][4][5][6]. 같은 `uid` 인데 시각이 조금씩 어긋나는 것은 정상입니다.
- **기록 시각은 사건 시각이 아닙니다.** nfdump `%tr`(수집기가 받은 시각), Zeek TSV 머리의 `#open`·`#close`(로그 파일을 열고 닫은 시각)는 기록하거나 처리한 시각입니다[7][15].
- **긴 연결은 시작 한 점에만 놓입니다.** Zeek conn.log 는 연결 하나가 한 줄이고 `ts` 는 첫 패킷이라[1], 몇 시간 이어진 연결도 시작 시각에만 보입니다. 끝 시각은 `ts` 에 `duration` 을 더해 따로 행을 만듭니다. 반대로 NetFlow 는 오래 이어지는 흐름을 주기적으로 내보내서[17] 연결 하나가 여러 행으로 나뉩니다.
- **현지 시각으로 해석하는 곳이 많습니다.** Wireshark 표시 필터의 날짜(시간대 생략 시), editcap `-A`·`-B`(시간대 생략 시), `zeek-cut -d`, nfdump `%ts`·`%te`·`%tr`, RFC 3164 syslog, nfcapd `-Z` 파일 이름이 모두 현지 시각 기준입니다[7][13][14][16][18][28]. 명령과 함께 분석 PC 의 시간대를 작업 기록에 적습니다.
- **소수 초가 사라집니다.** `zeek-cut -d` 의 기본 형식과 RFC 3164 syslog 에는 소수 초가 없습니다[7][18]. 1초 안의 순서는 소수 초가 있는 소스끼리만 비교합니다.
- **시간대 오프셋은 전달 중에 빠지기 쉽습니다.** 오프셋이 붙은 현지 시각은 보고 과정에서 오프셋이 사라질 수 있어서 UTC 로 기록하는 편이 낫습니다[20]. CSV 로 옮기거나 스프레드시트에 붙일 때 오프셋 열이 따로 남는지 확인합니다.
- **트래픽으로 되살린 행위 시각은 실제보다 늦습니다.** SMB 트래픽에서 되살린 파일 작업의 시각은 패킷을 잡는 데 걸리는 지연 때문에 실제 명령 실행보다 늦고, 그 정밀도는 네트워크 구성에 따라 크게 달라집니다[27]. cmd.exe 명령 18개를 약 2분 동안 실행한 시험에서는 되살린 시각이 대부분 실제보다 1초 안쪽으로 늦었습니다[27]. 단말의 실행 기록과 네트워크 시각이 조금 어긋나는 것만으로 조작을 의심하지 않습니다.
- **캡처가 빠진 구간은 빈칸으로 보입니다.** 타임라인에 행이 없다고 그 시간에 통신이 없었던 것은 아닙니다. 캡처 장비가 멈췄거나 과부하였는지, 들어오는 패킷과 나가는 패킷이 다른 경로로 지나가 센서가 한 방향만 봤는지 확인합니다[21].

## 결과를 어떻게 해석하나

한 소스 안에서는 시각 순서를 그대로 믿을 수 있습니다. 같은 센서의 Zeek 로그끼리, 같은 캡처 파일의 패킷끼리는 같은 시계로 찍었으므로 순서와 간격이 기록으로 확인됩니다. 보고서에는 "2026-03-02 00:31:04Z 에 10.1.2.30 이 update.example.com 을 조회했고, 0.2초 뒤 같은 센서의 연결 로그에 이 주소가 203.0.113.50:443 으로 연결을 시작한 기록이 있다"(만든 예시)처럼 소스와 기준 시계를 함께 적습니다.

서로 다른 장비의 기록 사이에서는 선후를 시계 오차 범위 안에서만 말할 수 있습니다. 3단계에서 시차가 확인되지 않으면 "방화벽 로그와 센서 로그는 같은 초에 있으나 두 장비의 시계 차이는 확인되지 않았다" 처럼 씁니다. 연결 식별자가 같다는 것은 주소·포트·프로토콜이 같다는 뜻이지, 시각이 멀리 떨어진 두 기록이 한 연결이라는 뜻은 아닙니다[22].

타임라인으로 증명하지 못하는 것도 구분합니다. 로그가 기록된 시각이 곧 사건이 일어난 시각이라는 것, 캡처가 없는 구간에 아무 일도 없었다는 것, 주소 뒤에 있던 사람이나 프로그램이 누구인지는 네트워크 타임라인만으로 확인되지 않습니다. 보고서 문장 쓰는 법은 [네트워크 포렌식 보고서](../reporting/forensic-report.md)에 있습니다.

## 참고 문헌

1. Zeek, base/protocols/conn/main.zeek (Conn::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
2. Zeek, base/protocols/dns/main.zeek (DNS::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dns/main.zeek.rst
3. Zeek, base/protocols/http/main.zeek (HTTP::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/http/main.zeek.rst
4. Zeek, base/protocols/ssl/main.zeek (SSL::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/main.zeek.rst
5. Zeek, base/frameworks/files/main.zeek (Files::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/frameworks/files/main.zeek.rst
6. Zeek, scripts/base/files/x509/main.zeek 소스 코드. https://github.com/zeek/zeek/blob/master/scripts/base/files/x509/main.zeek
7. Zeek, Zeek Log Formats and Inspection. https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
8. Zeek, base/frameworks/logging/writers/ascii.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/frameworks/logging/writers/ascii.zeek.rst
9. Zeek, files.log. https://github.com/zeek/zeek-docs/blob/master/logs/files.rst
10. Zeek, dns.log. https://github.com/zeek/zeek-docs/blob/master/logs/dns.rst
11. Suricata User Guide, EVE JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
12. Wireshark Display Filter Reference: Frame. https://www.wireshark.org/docs/dfref/f/frame.html
13. Wireshark, wireshark-filter(4) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/wireshark-filter.adoc
14. Wireshark, editcap(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/editcap.adoc
15. nfdump, nfdump(1) 매뉴얼. https://github.com/phaag/nfdump/blob/master/man/nfdump.1
16. nfdump, nfcapd(1) 매뉴얼. https://github.com/phaag/nfdump/blob/master/man/nfcapd.1
17. B. Claise, RFC 3954, Cisco Systems NetFlow Services Export Version 9, 2004. https://www.rfc-editor.org/rfc/rfc3954.txt
18. C. Lonvick, RFC 3164, The BSD syslog Protocol, 2001. https://www.rfc-editor.org/rfc/rfc3164.txt
19. R. Gerhards, RFC 5424, The Syslog Protocol, 2009. https://www.rfc-editor.org/rfc/rfc5424.txt
20. A. Durand, I. Gashinsky, D. Lee, S. Sheppard, RFC 6302, Logging Recommendations for Internet-Facing Servers, 2011. https://www.rfc-editor.org/rfc/rfc6302.txt
21. Karen Kent, Suzanne Chevalier, Tim Grance, Hung Dang, 「Guide to Integrating Forensic Techniques into Incident Response」, NIST SP 800-86, 2006. https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
22. Corelight, Community ID Flow Hashing 명세. https://github.com/corelight/community-id-spec/blob/master/README.md
23. Security Onion Documentation, Community ID. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/community-id.rst
24. SigmaHQ, Sigma Modifiers Appendix. https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-appendix-modifiers.md
25. SigmaHQ, Sigma Taxonomy Appendix. https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-appendix-taxonomy.md
26. Security Onion Documentation, PCAP. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/pcap.rst
27. Jan-Niclas Hilgert, Axel Mahr, Martin Lambertz, 「Mount SMB.pcap: Reconstructing file systems and file operations from network traffic」, Forensic Science International: Digital Investigation 50, 301807, 2024. doi:10.1016/j.fsidi.2024.301807
28. nfdump, src/output/output_fmt.c 소스 코드. https://github.com/phaag/nfdump/blob/master/src/output/output_fmt.c
