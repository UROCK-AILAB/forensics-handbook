---
title: "네트워크 기록의 시각"
parent: "기반 · 기록 체계"
nav_order: 120
---

# 네트워크 기록의 시각 (Timestamps)

네트워크 기록에 찍힌 시각은 기록마다 뜻이 다릅니다. 패킷을 본 시각, 흐름의 첫 패킷 시각, 로그 줄을 쓴 시각, 컬렉터가 받은 시각이 서로 섞여 있고, 저장된 값이 UTC 라도 보여 주는 도구가 분석 PC 의 시간대로 바꿔 찍기도 합니다. 이 페이지는 기록별로 무엇의 시각인지, 어느 시간대인지 정리하고, 여러 기록을 UTC 하나로 맞추는 방법을 설명합니다.

## 이 형식을 쓰는 아티팩트

여기서 다루는 기록은 패킷 캡처(pcap·pcapng), 흐름 기록(NetFlow v9·IPFIX·sFlow)과 nfdump 출력, Zeek·Suricata 로그, 웹 프록시(Squid)·DNS 서버(BIND)·DHCP 로그, syslog 로 모이는 방화벽과 장비 로그, 클라우드 흐름 로그입니다. 각 형식의 구조는 해당 페이지에 있고, 이 페이지는 시각 필드만 다룹니다. 로그 종류 전체는 [네트워크 로그의 종류](log-types.md), 흐름 기록의 헤더와 템플릿은 [흐름 기록](flow-records.md)에 있습니다.

호스트와 클라우드 쪽 시각은 각 핸드북의 타임라인 페이지를 봅니다. [Windows 타임라인](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/), [Linux 타임라인](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html), [macOS 타임라인](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/timeline/), [클라우드 타임라인](https://urock-ailab.github.io/forensics-handbook/cloud/03-techniques/analysis/timeline.html)이 있습니다.

## 구조 — 기록별 시각 필드

| 기록 | 필드 | 무엇의 시각 | 저장 형식 | 시간대 |
|---|---|---|---|---|
| pcap | 패킷 레코드 헤더의 초·초 아래 값 | 캡처 도구가 패킷을 본 시각 | epoch 초 + 마이크로초 또는 나노초 | UTC, 파일에 시간대 정보 없음 ([pcap](../capture/pcap.md)) |
| pcapng | EPB 64비트 시각 + IDB 의 if_tsresol·if_tsoffset | 같음 | if_tsresol 단위 수 | UTC, if_tsoffset 을 더해야 절대 시각 ([pcapng](../capture/pcapng.md)) |
| NetFlow v9 | 헤더 UNIX Secs | 내보내기 패킷이 익스포터를 떠난 시각 | epoch 초 | UTC[1] |
| NetFlow v9 | FIRST_SWITCHED·LAST_SWITCHED | 흐름의 첫·마지막 패킷 | 장비 부팅 뒤 흐른 ms(sysUpTime 기준 상대값) | 헤더 값으로 환산해야 함[1] |
| IPFIX | 메시지 헤더 Export Time | 메시지가 익스포터를 떠난 시각 | 부호 없는 32비트 epoch 초 | UTC[2] |
| IPFIX | flowStartSeconds·flowStartMilliseconds 등 | 흐름의 첫·마지막 패킷 | epoch 초 또는 ms | UTC[2][26] |
| IPFIX | flowStartMicroseconds·flowStartNanoseconds 등 | 같음 | NTP 형식(1900-01-01 기준 초 + 분수) | UTC[2][26] |
| sFlow v5 | 데이터그램 헤더 uptime | 데이터그램을 보내는 시각에 최대한 가깝게 잰 값 | 장비 부팅 뒤 흐른 ms | 절대 시각 없음[3] |
| nfdump 출력 | `%ts`·`%te`·`%tr`, JSON 의 first·last·received | 흐름의 첫·마지막 패킷, 컬렉터가 받은 시각 | `YYYY-MM-DD HH:MM:SS.mmm`, JSON 은 `YYYY-MM-DDTHH:MM:SS.mmm` | nfdump 를 실행한 PC 의 현지 시각, 표시 없음[4][5][6] |
| Zeek | ts | conn.log 는 연결의 첫 패킷 | epoch 소수(TSV, JSON 기본값) | UTC[7][9][10] |
| Suricata EVE | timestamp | 이벤트를 만든 패킷의 시각, flow 이벤트는 기록한 시각 | `YYYY-MM-DDTHH:MM:SS.uuuuuu+hhmm` | 센서 현지 시각 + 오프셋[12][13][14] |
| Suricata EVE | flow.start·flow.end | 흐름의 첫·마지막 패킷 | 같음 | 같음[14] |
| Squid (squid 형식) | 첫 필드 `%ts.%03tu` | 로그 줄을 쓴 시각 | epoch 초.ms | UTC[15] |
| Squid (common·combined 형식) | `%tl` | 같음 | `%d/%b/%Y:%H:%M:%S %z` | 프록시 현지 시각 + 오프셋[15] |
| BIND | print-time 설정 | 로그를 쓴 시각 | 설정에 따라 다름 | yes·local·iso8601 은 현지, iso8601-utc 는 UTC, 기본값 no 는 시각을 찍지 않음[16] |
| Windows DHCP 감사 로그 | Date, Time | 서버가 항목을 기록한 시각 | 날짜·시각 두 필드 | 시간대 필드 없음[17] |
| syslog (RFC 5424) | TIMESTAMP | 메시지를 만든 시각 | RFC 3339 을 좁힌 형식 | `Z` 또는 `±hh:mm`[18] |
| syslog (RFC 3164) | TIMESTAMP | 메시지를 만든 시각 | `Mmm dd hh:mm:ss` | 보낸 장비의 현지 시각, 연도·시간대 없음[19] |
| AWS VPC 흐름 로그 | start, end | 집계 구간 안의 첫·마지막 패킷 | Unix 초 | UTC epoch[24] |

## 읽는 법

### 무엇의 시각인지 먼저 구분하기

위 표의 시각은 다섯 종류로 나뉩니다. 패킷을 본 시각(pcap·pcapng), 흐름이나 연결의 첫·마지막 패킷 시각(NetFlow·IPFIX 흐름 필드, Zeek ts, Suricata flow.start), 로그 줄이나 메시지를 쓴 시각(Squid, syslog, DHCP, Suricata flow 이벤트의 timestamp), 컬렉터가 받은 시각(nfdump `%tr`), 익스포터가 내보낸 시각(IPFIX Export Time, NetFlow UNIX Secs)입니다. 연결이 10분 이어졌다면 첫 패킷 시각과 기록한 시각은 10분 넘게 벌어질 수 있으므로, 서로 다른 종류의 시각을 그대로 비교하지 않습니다.

Zeek conn.log 의 ts 는 연결의 첫 패킷 시각입니다[7]. duration 에는 한 방향이 닫힌 뒤 새 데이터를 싣지 않은 TCP 패킷이 빠지는데, 정상 종료 때의 마지막 ACK 가 그런 예입니다[7]. 그래서 ts 에 duration 을 더한 값은 실제 마지막 패킷보다 조금 이를 수 있습니다. conn.log 는 연결 상태를 지울 때(connection_state_remove 이벤트) 줄을 쓰므로[7], 파일 안 줄 순서는 연결이 끝난 순서이지 ts 순서가 아닙니다. 연결 상태를 지우는 기본 시간은 TCP 비활성 5분, UDP·ICMP 비활성 각 1분, 정상 종료 뒤 5초이고 모두 설정으로 바꿀 수 있습니다[8].

Suricata EVE 이벤트 대부분은 이벤트를 만든 패킷의 시각을 timestamp 에 씁니다[13]. flow 이벤트는 다릅니다. timestamp 는 흐름 레코드를 쓰는 순간의 Suricata 시각이고, 실시간 캡처에서는 시스템 시계, pcap 파일을 읽을 때는 처리 스레드들이 다루는 패킷 시각 중 가장 이른 값입니다[12][14]. 흐름의 시각은 flow.start·flow.end 에 있고, age 는 end 의 초에서 start 의 초를 뺀 정수입니다[14]. timestamp 가 기록한 시각이라서 흐름 시작보다 앞서기도 하는데, timestamp 가 06:13:21.216460 이고 flow.start 가 06:13:33.324862 인 이벤트가 그런 예입니다[11].

Squid 기본 형식의 첫 필드는 로그 줄을 쓸 때의 시각입니다[15]. 트랜잭션 시작(`%tS`)은 요청 헤더를 다 받은 시각이고, 응답 시간 `%tr`(ms)은 이 시각부터 잽니다[15]. 그래서 요청이 들어온 시각은 첫 필드에서 `%tr` 을 뺀 값에 가깝습니다.

NetFlow v9 와 sFlow 는 장비가 켜진 뒤 흐른 시간을 씁니다. NetFlow v9 의 흐름 첫 패킷 시각은 헤더의 UNIX Secs 에서 (헤더 sysUpTime − FIRST_SWITCHED) ÷ 1000 초를 빼서 구합니다[1]. 계산 예는 [흐름 기록](flow-records.md)에 있습니다. sysUpTime 은 32비트 ms 값이라 2의 32제곱 ms, 곧 약 49.7일마다 0으로 돌아갑니다. sFlow v5 데이터그램에는 절대 시각 필드가 없어서 컬렉터가 받은 시각에 기댈 수밖에 없고, 한 장비 안의 서브 에이전트끼리도 uptime 이 맞는다고 가정하면 안 됩니다[3].

### 시간대 확인하기

저장된 값이 UTC epoch 여도 도구가 화면에 찍을 때 분석 PC 의 현지 시각으로 바꾸는 경우가 많습니다. nfdump 는 `%ts`·`%te`·`%tr` 과 JSON 의 first·last·received 를 localtime_r 로 만들고 시간대 표시를 붙이지 않습니다[5][6]. UTC 는 `%tsg`·`%teg`·`%trg`, epoch 소수 초는 `%tsr`·`%ter`·`%trr` 로 따로 찍습니다[4]. nfcapd 가 만드는 파일 이름의 시각도 컬렉터 PC 의 현지 시각입니다[20]. tshark 의 `-t` 는 기본값이 첫 패킷 기준 상대 시각(r)이고, `a`·`ad` 는 분석 PC 현지 시각, `u`·`ud` 는 `Z` 가 붙은 UTC, `e` 는 epoch 초입니다[21]. zeek-cut 의 `-d` 는 epoch 을 `%Y-%m-%dT%H:%M:%S%z` 형식으로 바꾸고, UTC 로 바꾸려면 `-u` 를 따로 씁니다[10].

Suricata 는 반대로 저장할 때부터 센서의 현지 시각을 씁니다. EVE 의 timestamp 와 flow.start·flow.end 는 localtime_r 로 바꾼 현지 시각을 `%Y-%m-%dT%H:%M:%S` 뒤에 마이크로초 6자리와 `%z` 를 붙인 형식으로 적어서, `+0900` 처럼 콜론 없는 오프셋이 붙습니다[12][14]. `2026-01-01T09:00:00.123456+0900` 은 `2026-01-01T00:00:00.123456Z` 와 같은 순간입니다(만든 예시). 센서 여러 대의 시간대가 다르면 같은 파일 묶음 안에서도 오프셋이 섞입니다.

시간대가 아예 저장되지 않는 값도 있습니다. RFC 3164 syslog TIMESTAMP, Windows DHCP 감사 로그의 Date·Time, BIND 의 print-time yes·local, nfdump 기본 출력과 nfcapd 파일 이름이 그렇습니다. 이런 값은 장비나 분석 PC 의 시간대 설정을 확인하거나, 아래 "여러 기록을 UTC 로 맞추기" 처럼 같은 사건이 찍힌 다른 기록과 비교해 오프셋을 구합니다.

RFC 3339 에서 `-00:00` 은 UTC 시각은 알지만 현지 오프셋은 모른다는 뜻이라 `Z`·`+00:00` 과 뜻이 다릅니다[22]. 오프셋이 `-00:00` 인 값을 "현지가 UTC 인 장비" 로 읽지 않습니다.

### 헥스로 따라가기 — IPFIX NTP 형식 (명세로 만든 예시)

IPFIX 의 마이크로초·나노초 시각 형식은 Unix epoch 가 아니라 NTP 형식입니다. 앞 4바이트는 1900-01-01 00:00:00 UTC 부터 흐른 초, 뒤 4바이트는 2의 −32제곱 초 단위 분수이고, 둘 다 빅엔디언입니다[2].

2026-01-01 00:00:00 UTC 는 Unix 초로 1767225600 이고, 1900년과 1970년 사이 2208988800 초를 더하면 NTP 초 3976214400 = 0xED003780 입니다. 분수가 0 이면 flowStartMicroseconds 값은 다음 8바이트입니다.

```
ED 00 37 80 00 00 00 00
```

앞 4바이트를 Unix 초로 잘못 읽으면 2096-01-01 이 되고, 반대로 Unix 초 1767225600 을 NTP 초로 읽으면 1956-01-02 가 됩니다. 흐름 시각이 70년쯤 어긋나 보이면 기준 시점을 잘못 고른 경우입니다. 마이크로초 형식은 분수의 하위 11비트를 무시해야 합니다(MUST)[2].

### 여러 기록을 UTC 로 맞추기

1. 확보한 기록마다 위 표처럼 "무엇의 시각인지, 어느 시간대인지, 어떤 형식인지" 를 적습니다.
2. 도구가 현지 시각으로 바꾸지 못하게 epoch 나 UTC 로 뽑습니다. nfdump 는 `%tsr`·`%tsg`, tshark 는 `-t ud` 나 `frame.time_epoch`, zeek-cut 은 `-u`, Suricata 는 오프셋을 반영해 UTC 로 바꿉니다.
3. 같은 사건이 두 기록에 함께 있는 지점을 찾아 차이를 잽니다. 같은 연결의 Zeek ts 와 방화벽 syslog 시각, 같은 DNS 질의의 pcap 시각과 DNS 서버 로그 시각이 그런 예입니다. nfdump 에서 `%tsr` 과 `%ts` 를 함께 찍으면 분석 PC 의 오프셋이 바로 보입니다.
4. 차이가 여러 사건에서 거의 일정하면 시간대 설정이나 장비 시계의 어긋남으로 보고, 사건마다 흔들리면 기록 시점이 다른 것(첫 패킷과 기록 시각 등)으로 봅니다.
5. 보고서에는 UTC 로 통일하고, 기록마다 어떤 오프셋을 적용했는지 근거와 함께 적습니다. 오프셋 정보는 보고 과정에서 사라지기 쉬워서, 인터넷에 노출된 서버 로그도 현지 시각과 오프셋 대신 UTC 로 적기를 권합니다[23].

합친 뒤의 분석 절차는 [네트워크 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 포렌식에서 중요한 점

### 증명하는 것

기록의 시각으로는 그 장비가 자기 시계로 그 시각을 적었다는 것을 알 수 있습니다. 같은 장비의 같은 종류 시각끼리는 앞뒤를 비교할 수 있지만, 줄 순서가 아니라 시각 값으로 비교해야 합니다.

### 증명하지 못하는 것

장비 시계가 맞았다는 것은 기록만으로 알 수 없습니다. RFC 5424 syslog 에는 timeQuality 구조화 데이터가 있어 tzKnown(시간대를 아는지, 1 또는 0), isSynced(NTP 같은 외부 시계와 맞췄는지), syncAccuracy(최대 오차, 마이크로초)를 적을 수 있지만 모두 선택 항목입니다[18]. `[timeQuality tzKnown="0" isSynced="0"]` 이 붙은 메시지는 보낸 장비가 자기 시각을 믿기 어렵다고 알린 것이고, 컬렉터가 메시지 시각 대신 자기 시각을 쓰라는 힌트로 쓰입니다[18]. 이 데이터가 없으면 동기화 여부를 알 수 없습니다.

RFC 3164 syslog 를 받는 쪽은 TIMESTAMP 를 검증할 필요가 없고, 날짜가 틀린 장비도 유효한 메시지를 보낼 수 있습니다[19]. 릴레이가 유효한 TIMESTAMP 를 찾지 못하면 자기 현지 시각을 넣어야 하므로(MUST)[19], 로그의 시각이 원래 장비가 아니라 중간 릴레이의 시각일 수도 있습니다. 미리 받아 둔 메시지를 현재 시각으로 고쳐 다시 보내도 받는 쪽에서 알아챌 장치가 없습니다[19]. syslog 전송의 다른 한계는 [네트워크 로그의 종류](log-types.md)에 있습니다.

### 늦게 쓰이거나 도중에 끊긴 기록

기록이 쓰이는 시점은 사건 시각보다 늦습니다. Zeek conn.log 는 연결이 끝나야 쓰이고[7], NetFlow·IPFIX 는 활성·비활성 시간 제한이 지나야 흐름을 내보냅니다([흐름 기록](flow-records.md)). AWS VPC 흐름 로그는 보통 CloudWatch Logs 로 약 5분, S3 로 약 10분 뒤에 전달되지만 더 늦어질 수도 있습니다[24]. start 값은 실제 패킷보다 최대 60초 이르거나 늦을 수 있고, end 값은 최대 60초 늦을 수 있습니다[24]. 자세한 내용은 [VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/aws/vpc-flow-logs.html)에 있습니다.

Suricata flow 이벤트의 reason 필드에는 흐름이 끝난 이유로 timeout·forced·shutdown 이 들어가고, 코드에는 tcp_reuse·unknown 값도 있습니다[11][14]. shutdown 인 흐름의 flow.end 는 Suricata 가 멈추기 전 마지막으로 본 패킷 시각이지 연결이 끝난 시각이 아닙니다. 센서가 멈춘 뒤의 통신은 Suricata 기록에 없으므로, 센서 시작·정지 시각을 먼저 확인합니다.

## 함정

**줄 순서나 파일 수정 시각으로 사건 순서를 정하지 않습니다.** Zeek conn.log 는 끝난 순서로 쓰이고[7], Suricata flow 이벤트는 흐름이 만료될 때 쓰입니다[14]. syslog 는 한 장비에서 한 컬렉터로 가는 메시지도 순서가 바뀌어 도착할 수 있고, 여러 장비가 보내면 늦게 만든 메시지가 먼저 도착할 수 있습니다[19]. 오래 이어진 연결은 로그 파일 뒤쪽에 늦게 나타납니다.

**Suricata flow 이벤트의 timestamp 를 흐름 시각으로 쓰지 않습니다.** 흐름 시각은 flow.start·flow.end 입니다[14]. 또 Suricata 문서의 공통 구조 예에는 `2009-11-24T21:27:09.534255` 처럼 오프셋 없는 값이 있지만[11], 코드는 언제나 오프셋을 붙입니다[12]. 파서를 만들 때는 코드 기준으로 오프셋이 있다고 보고 처리합니다.

**분석 PC 의 시간대가 결과에 섞입니다.** nfdump 기본 출력과 tshark `-t a`·`-t ad` 는 분석 PC 의 현지 시각입니다[5][21]. 다른 PC 에서 뽑은 결과나 다른 분석가의 결과와 비교하면 몇 시간씩 어긋날 수 있으므로 epoch 값이나 UTC 옵션으로 다시 확인합니다.

**32비트 시각은 한 바퀴 돕니다.** NetFlow sysUpTime 은 약 49.7일마다, IPFIX Export Time 과 dateTimeSeconds 는 2106-02-07 06:28:16 UTC 에, NTP 형식 시각은 2036-02-08 에 넘칩니다[2]. 수십 년 전 파일의 시각을 현재 날짜 기준으로 해석하면 틀릴 수 있어서, IPFIX 파일을 오래 보관할 때는 시각 해석에 필요한 맥락 정보를 함께 저장하도록 권합니다(RECOMMENDED)[2]. flowStartDeltaMicroseconds 처럼 Export Time 에서 뺀 값으로 적는 필드는 32비트라서 Export Time 기준 71분 안의 흐름만 담을 수 있습니다[2].

**RFC 3164 syslog 에는 연도가 없습니다.** 12월 말과 1월 초에 걸친 로그는 연도를 추정해야 합니다. 저장할 때 연도를 붙이는 스크립트나 연도를 적은 줄을 끼워 넣는 방법이 쓰였지만, 어느 방법도 시간대 문제는 풀지 못합니다[19].

**Squid 의 첫 필드는 요청 시각이 아닙니다.** 로그를 쓴 시각이라서 오래 걸린 다운로드는 요청보다 한참 뒤 시각으로 남습니다. 요청 시각은 `%tr` 을 빼서 구합니다[15].

**Windows DHCP 감사 로그의 Date·Time 은 시간대를 따로 확인합니다.** 두 필드는 서버가 항목을 기록한 날짜와 시각이고, 줄 안에 시간대를 적는 필드가 없습니다[17]. 같은 임대가 찍힌 pcap 의 DHCP 패킷 시각과 비교하면 오프셋을 구할 수 있습니다.

## 도구

| 도구 | 시각 관련 옵션 |
|---|---|
| tshark·Wireshark | `-t a/ad/adoy/d/dd/e/r/rc/u/ud/udoy`, `.N` 으로 소수 자리 지정. 기본값은 r[21]. 필드 `frame.time`(도착 시각), `frame.time_epoch`(1.4.0 이상), `frame.time_utc`(4.2.0 이상), `frame.time_relative_capture_start`(4.2.0 이상)[25] |
| zeek-cut | `-d` 사람이 읽는 시각, `-u` UTC, `-D`·`-U` 로 strftime 형식 지정[10] |
| Zeek 설정 | `LogAscii::json_timestamps` 로 JSON 시각 형식 선택: JSON::TS_EPOCH(기본), TS_MILLIS, TS_MILLIS_UNSIGNED, TS_ISO8601[8][9] |
| nfdump | `%ts %te %tr`(현지), `%tsg %teg %trg`(GMT), `%tsr %ter %trr`(epoch 소수 초), `%td`·`%tds`(지속 시간)[4] |
| jq | Suricata EVE·Zeek JSON 에서 시각 필드만 뽑기 |

같은 패킷·흐름·이벤트를 현지 시각과 UTC 로 함께 뽑아 보면 도구가 어느 시간대로 찍는지 바로 확인됩니다.

```
tshark -r sample.pcapng -T fields -e frame.number -e frame.time_epoch -e frame.time_utc
nfdump -r nfcapd.202601010000 -o 'fmt:%tsr %ts %tsg %sa %da'
zeek-cut -u ts uid id.orig_h id.resp_h < conn.log
jq -r 'select(.event_type=="flow") | [.timestamp, .flow.start, .flow.end, .flow.age] | @tsv' eve.json
```

파일 이름은 만든 예시입니다. Wireshark 로 읽는 방법은 [Wireshark·tshark로 읽기](../../03-techniques/analysis/wireshark.md), nfdump 분석 절차는 [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md), Zeek·Suricata 필드는 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md)와 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)에 있습니다.

## 참고 문헌

1. B. Claise, "Cisco Systems NetFlow Services Export Version 9", RFC 3954, 2004. https://www.rfc-editor.org/rfc/rfc3954.txt
2. B. Claise, B. Trammell, P. Aitken, "Specification of the IP Flow Information Export (IPFIX) Protocol", RFC 7011, 2013. https://www.rfc-editor.org/rfc/rfc7011.txt
3. sFlow.org, "sFlow Version 5", 2004. https://sflow.org/sflow_version_5.txt
4. nfdump, nfdump(1) 매뉴얼. https://github.com/phaag/nfdump/blob/master/man/nfdump.1
5. nfdump, src/output/output_fmt.c. https://github.com/phaag/nfdump/blob/master/src/output/output_fmt.c
6. nfdump, src/output/output_json.c. https://github.com/phaag/nfdump/blob/master/src/output/output_json.c
7. Zeek, scripts/base/protocols/conn/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/conn/main.zeek
8. Zeek, scripts/base/init-bare.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/init-bare.zeek
9. Zeek, scripts/base/frameworks/logging/writers/ascii.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/frameworks/logging/writers/ascii.zeek
10. Zeek 문서, "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
11. Suricata 사용자 안내서, "Eve JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
12. Suricata, src/util-time.c. https://github.com/OISF/suricata/blob/main/src/util-time.c
13. Suricata, src/output-json.c. https://github.com/OISF/suricata/blob/main/src/output-json.c
14. Suricata, src/output-json-flow.c. https://github.com/OISF/suricata/blob/main/src/output-json-flow.c
15. Squid, src/cf.data.pre (logformat, access_log). https://github.com/squid-cache/squid/blob/master/src/cf.data.pre
16. BIND 9 Administrator Reference Manual, "Configuration Reference" (print-time). https://bind9.readthedocs.io/en/stable/reference.html
17. Microsoft, "Analyze DHCP Server Log Files" (Windows Server 2008 R2·2008). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/dd183591(v=ws.10)
18. R. Gerhards, "The Syslog Protocol", RFC 5424, 2009. https://www.rfc-editor.org/rfc/rfc5424.txt
19. C. Lonvick, "The BSD syslog Protocol", RFC 3164, 2001. https://www.rfc-editor.org/rfc/rfc3164.txt
20. nfdump, src/collector/collector.c. https://github.com/phaag/nfdump/blob/master/src/collector/collector.c
21. Wireshark, doc/man_pages/dissection-options.adoc. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/dissection-options.adoc
22. G. Klyne, C. Newman, "Date and Time on the Internet: Timestamps", RFC 3339, 2002. https://www.rfc-editor.org/rfc/rfc3339.txt
23. A. Durand, I. Gashinsky, D. Lee, S. Sheppard, "Logging Recommendations for Internet-Facing Servers", RFC 6302 (BCP 162), 2011. https://www.rfc-editor.org/rfc/rfc6302.txt
24. Amazon Web Services, "Flow log records". https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html
25. Wireshark, "Display Filter Reference: Frame". https://www.wireshark.org/docs/dfref/f/frame.html
26. J. Quittek, S. Bryant, B. Claise, P. Aitken, J. Meyer, "Information Model for IP Flow Information Export", RFC 5102, 2008. https://www.rfc-editor.org/rfc/rfc5102.txt
