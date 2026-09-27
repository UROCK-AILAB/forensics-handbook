---
title: "TCP 연결과 흐름"
parent: "기반 · 프로토콜 기초"
nav_order: 40
---

# TCP 연결과 흐름 (TCP Sessions)

패킷 캡처, Zeek conn.log, Suricata flow 기록, Wireshark 대화 목록은 모두 TCP 연결 하나를 기록 한 단위로 삼지만, 연결을 어디서 나누고 방향을 어떻게 부르는지가 도구마다 다릅니다. 이 페이지는 TCP 헤더와 연결이 열리고 닫히는 순서를 명세대로 정리하고, 그 패킷 흐름이 각 기록에 어떤 값으로 남는지 연결해 봅니다. 기록마다 자세한 필드는 해당 아티팩트 페이지로 링크합니다.

## 이 형식을 쓰는 아티팩트

TCP 는 두 끝점이 순서 번호를 맞춘 뒤 데이터를 주고받는 연결형 프로토콜이라서, 패킷을 모아 "연결" 하나로 묶을 수 있습니다[6]. 네트워크 기록은 대부분 이 묶음을 한 줄로 요약합니다.

| 기록 | 한 줄(한 항목)의 단위 | 자세한 페이지 |
|---|---|---|
| pcap·pcapng 캡처 | 세그먼트 하나. 연결은 분석 도구가 다시 묶음 | [pcap 형식](../capture/pcap.md) |
| Zeek conn.log | TCP 연결 하나. UDP·ICMP 는 같은 출발지 주소·포트에서 같은 목적지 주소·포트로 가는 패킷 묶음[2] | [연결 기록 (conn.log)](../../02-artifacts/zeek/zeek-logs/conn-log.md) |
| Suricata EVE `flow` | 양방향 흐름 하나. `netflow` 를 켜면 한 방향씩 따로 적어 `flow` 의 두 배 개수가 됨[4] | [프로토콜 기록](../../02-artifacts/suricata/eve-json/protocol-events.md) |
| Wireshark·tshark 대화 | TCP 스트림 하나(`tcp.stream` 번호, 첫 스트림은 0)[8] | [Wireshark·tshark로 읽기](../../03-techniques/analysis/wireshark.md) |
| tcpflow 출력 파일 | 한 방향 데이터 하나. 파일 이름이 출발지 IP.포트-목적지 IP.포트[9] | [세션 복원과 파일 꺼내기](../../03-techniques/analysis/file-extraction.md) |
| NetFlow·IPFIX, 방화벽 로그 | 장비마다 다름 | [흐름 기록](../records/flow-records.md), [방화벽 로그](../../02-artifacts/devices/firewall-logs.md) |

"연결 (connection)" 은 TCP 명세의 상태 기계가 있는 대상이고, "흐름 (flow)" 은 도구가 주소·포트가 같은 패킷을 묶은 결과입니다. TCP 에서는 두 말이 거의 같은 것을 가리키지만, 도구가 흐름을 비활동 시간으로 끊기 때문에 연결 하나가 흐름 여러 개로 나뉠 수 있습니다([함정](#함정)).

## 구조

### TCP 헤더

TCP 헤더는 IP 헤더 바로 뒤에 오고, 옵션이 없으면 20바이트입니다[6]. 아래 오프셋은 RFC 9293 그림 1 의 비트 배치에서 계산한 값입니다.

| 오프셋(바이트) | 길이 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 2 | Source Port | 출발지 포트 |
| 2 | 2 | Destination Port | 목적지 포트 |
| 4 | 4 | Sequence Number | 이 세그먼트 첫 데이터 바이트의 순서 번호. SYN 이 켜져 있으면 초기 순서 번호 (ISN) 이고 첫 데이터 바이트는 ISN+1 |
| 8 | 4 | Acknowledgment Number | ACK 비트가 켜져 있을 때만 뜻이 있고, 보낸 쪽이 다음에 받기를 기대하는 순서 번호. 연결이 맺어진 뒤에는 늘 보냄 |
| 12 | 상위 4비트 | Data Offset | 헤더 길이(32비트 워드 수). 옵션이 없으면 5 |
| 12 | 하위 4비트 | Reserved | 0 |
| 13 | 1 | 제어 비트 | CWR·ECE·URG·ACK·PSH·RST·SYN·FIN |
| 14 | 2 | Window | 받을 수 있는 바이트 수. 창 배율 확장을 쓰면 옮긴(shift) 값 |
| 16 | 2 | Checksum | 헤더·데이터와 의사 헤더(출발지·목적지 IP 등)에 대한 검사합 |
| 18 | 2 | Urgent Pointer | URG 가 켜졌을 때만 뜻이 있음 |
| 20 | 가변 | Options | Data Offset×4 − 20 바이트 |

필드의 정의는 RFC 9293 3.1절에 있습니다[6]. 모든 구현이 알아야 하는 옵션은 End of Option List(Kind 0), No-Operation(Kind 1), 최대 세그먼트 크기 (MSS, Kind 2, 길이 4) 셋이고, 그 밖의 옵션도 길이 필드가 있어서 모르는 옵션은 건너뛸 수 있습니다[6].

제어 비트는 오프셋 13 의 한 바이트에 CWR 부터 FIN 까지 높은 비트 순서로 들어 있습니다[6]. 흔한 조합의 바이트 값은 다음과 같고, Suricata flow 기록의 `tcp_flags` 도 같은 값을 16진 두 자리로 적습니다[3]([프로토콜 기록](../../02-artifacts/suricata/eve-json/protocol-events.md)).

| 조합 | 값 | 조합 | 값 |
|---|---|---|---|
| FIN | 0x01 | ACK | 0x10 |
| SYN | 0x02 | SYN+ACK | 0x12 |
| RST | 0x04 | RST+ACK | 0x14 |
| PSH | 0x08 | PSH+ACK | 0x18 |
| URG | 0x20 | FIN+ACK | 0x11 |
| ECE | 0x40 | CWR | 0x80 |

### 연결을 여는 순서

연결은 3방향 핸드셰이크 (three-way handshake) 로 열립니다. 아래는 RFC 9293 그림 6 을 옮긴 것이고, A 가 SYN 을 보내고 B 가 SYN+ACK 로 답한 뒤 A 가 ACK 를 보내면 양쪽이 ESTABLISHED 상태가 됩니다[6].

```
    A                                                    B
1.  CLOSED                                               LISTEN
2.  SYN-SENT    --> <SEQ=100><CTL=SYN>               --> SYN-RECEIVED
3.  ESTABLISHED <-- <SEQ=300><ACK=101><CTL=SYN,ACK>  <-- SYN-RECEIVED
4.  ESTABLISHED --> <SEQ=101><ACK=301><CTL=ACK>       --> ESTABLISHED
5.  ESTABLISHED --> <SEQ=101><ACK=301><CTL=ACK><DATA> --> ESTABLISHED
```

SYN 과 FIN 은 순서 번호를 하나씩 차지해서, 3번 줄의 확인 번호가 100 이 아니라 101 입니다[6]. 양쪽이 동시에 SYN 을 보내 여는 경우도 명세가 허용합니다[6].

### 연결을 닫는 순서

정상 종료는 양쪽이 FIN 을 보내고 서로 ACK 하는 것이고, 비정상 종료 (abort) 는 RST 를 보내 상태를 바로 버리는 것입니다[6]. 두 방향은 따로 닫혀서, 한쪽이 FIN 을 보낸 뒤에도 반대쪽은 계속 데이터를 보낼 수 있습니다(half-close)[6].

```
    A                                                    B
1.  ESTABLISHED                                          ESTABLISHED
2.  FIN-WAIT-1  --> <SEQ=100><ACK=300><CTL=FIN,ACK>  --> CLOSE-WAIT
3.  FIN-WAIT-2  <-- <SEQ=300><ACK=101><CTL=ACK>      <-- CLOSE-WAIT
4.  TIME-WAIT   <-- <SEQ=300><ACK=101><CTL=FIN,ACK>  <-- LAST-ACK
5.  TIME-WAIT   --> <SEQ=101><ACK=301><CTL=ACK>      --> CLOSED
6.  (2 MSL)
    CLOSED
```

먼저 닫은 쪽은 최대 세그먼트 수명 (MSL) 의 두 배만큼 TIME-WAIT 에 머물러야 하고, 이 명세가 정한 MSL 은 2분입니다[6]. RST 를 보낸 쪽도 TIME-WAIT 에 들어가는 편이 좋습니다(필수 요건은 아님)[6]. 명세의 상태는 LISTEN, SYN-SENT, SYN-RECEIVED, ESTABLISHED, FIN-WAIT-1, FIN-WAIT-2, CLOSE-WAIT, CLOSING, LAST-ACK, TIME-WAIT 와 가상의 CLOSED 입니다[6].

### RST 가 나오는 경우

RST 는 들어온 세그먼트가 지금 연결에 속하지 않아 보일 때 나옵니다[6]. 연결이 없는 포트(CLOSED)에 SYN 이 오면 RST 로 거절하는데, 들어온 세그먼트에 ACK 비트가 없으면 RST 의 순서 번호는 0 이고 확인 번호는 들어온 순서 번호에 세그먼트 길이를 더한 값입니다[6]. SYN 은 길이 1 로 세므로, 닫힌 포트에 보낸 SYN 의 답은 확인 번호가 ISN+1 인 RST+ACK 가 됩니다[6]. 들어온 세그먼트에 ACK 비트가 있으면 RST 는 그 확인 번호를 자기 순서 번호로 씁니다[6]. 연결이 맺어진 상태에서 창 밖 세그먼트가 오면 RST 가 아니라 빈 ACK 로 답하고 상태를 유지합니다[6].

### 연결 유지 패킷

연결 유지 (keep-alive) 는 구현이 넣을 수도 있는 선택 기능이고, 넣었다면 기본값은 꺼짐이어야 하며 간격은 설정할 수 있어야 하고 기본 2시간 이상이어야 합니다[6]. 탐침 세그먼트는 보통 순서 번호가 다음 보낼 번호보다 1 작고, 데이터가 없거나 쓰레기 1바이트가 붙습니다[6]. Wireshark 는 길이가 0 또는 1 이고 순서 번호가 기대값보다 1 작으며 SYN·FIN·RST 가 없는 세그먼트에 "TCP Keep-Alive" 를 붙입니다[7].

## 읽는 법

### 헥스로 한 세그먼트 풀기

아래는 192.0.2.10:49152 가 198.51.100.20:443 으로 보내는, 옵션이 없는 SYN 세그먼트의 TCP 헤더입니다(명세로 만든 예시). 체크섬은 두 IP 주소로 만든 의사 헤더를 넣어 계산한 값입니다.

```
c0 00 01 bb 00 00 00 64 00 00 00 00 50 02 ff ff 01 71 00 00
```

| 바이트 | 값 | 해석 |
|---|---|---|
| `c0 00` | 49152 | 출발지 포트 |
| `01 bb` | 443 | 목적지 포트 |
| `00 00 00 64` | 100 | 순서 번호(ISN) |
| `00 00 00 00` | 0 | 확인 번호. ACK 비트가 꺼져 있어 뜻 없음 |
| `50` | 5, 0 | Data Offset 5 → 헤더 20바이트, Reserved 0 |
| `02` | SYN | 제어 비트 |
| `ff ff` | 65535 | Window |
| `01 71` | 0x0171 | Checksum |
| `00 00` | 0 | Urgent Pointer |

B 가 SYN+ACK 로 답하면 제어 비트 바이트가 `12` 가 되고 확인 번호가 `00 00 00 65`(101)가 됩니다. 실제 캡처의 SYN 에는 보통 MSS 같은 옵션이 붙어서 Data Offset 이 5 보다 크고, 오프셋 20 부터 옵션이 이어집니다. Wireshark 는 옵션을 종류(Kind)와 길이로 풀어 보여 주고, 창 배율이 있으면 헤더의 `Window size value` 와 계산한 `[Calculated window size]`·`[Window size scaling factor]` 를 따로 적습니다[1]. 대괄호 값은 Wireshark 가 계산한 값이고 헤더에는 16비트 Window 값만 있습니다[6].

### 패킷 흐름이 기록에 남는 모양

같은 연결을 도구마다 다른 값으로 요약합니다. 대표적인 패킷 흐름이 Zeek 와 Wireshark 에 어떻게 나타나는지 아래 표로 정리했습니다[1][2][7]. Zeek 의 `conn_state`·`history` 전체 값은 [연결 기록 (conn.log)](../../02-artifacts/zeek/zeek-logs/conn-log.md) 에 있습니다.

| 패킷 흐름 | Zeek `conn_state` | Zeek `history` 에 보이는 것 | Wireshark `tcp.completeness` |
|---|---|---|---|
| SYN 만 가고 응답 없음 | `S0` | `S` 만 있고 `h` 가 없음 | 1 (SYN 만) |
| SYN 에 RST 로 거절 | `REJ` | `S` 와 응답 측 `r` | SYN(1)·RST(32) 비트 |
| 핸드셰이크 뒤 데이터 없이 끝남 | 종료 방식에 따름 | `S`·`h`·`A`, `D`·`d` 없음 | 7 에 FIN(16)·RST(32) 비트 |
| 데이터를 주고받고 FIN 으로 정상 종료 | `SF` | 예 `ShADadFf` | 31, 47, 63 가운데 하나 |
| 맺어진 뒤 발신 측이 RST | `RSTO` | 대문자 `R` | RST(32) 비트 포함 |
| 캡처 시작 전부터 열려 있던 연결 | `OTH` | `S`·`h` 없음 | SYN(1)·SYN-ACK(2) 비트 없음 |

`tcp.completeness` 는 SYN 1, SYN-ACK 2, ACK 4, DATA 8, FIN 16, RST 32 를 더한 값이라서, 핸드셰이크만 있는 대화는 7, 데이터가 오가고 FIN 이나 RST 로 끝난 대화는 31·47·63 입니다[7]. `tcp.completeness.str` 로 문자열을 걸러 낼 수도 있습니다[7].

Suricata flow 기록은 `state`(`new`·`established`·`closed`·`bypassed`)와 끝난 이유 `reason`(`timeout`·`forced`·`shutdown`)을 적고[3], `tcp` 객체의 `tcp_flags_ts`·`tcp_flags_tc` 로 방향별로 본 제어 비트를 알 수 있습니다([프로토콜 기록](../../02-artifacts/suricata/eve-json/protocol-events.md)). 서버→클라이언트 값인 `tcp_flags_tc` 에 SYN(0x02) 이 없으면 센서가 서버의 SYN+ACK 를 보지 못한 흐름입니다.

### 방향을 부르는 이름

같은 두 끝점을 도구마다 다르게 부르므로, 기록을 합칠 때는 이름을 맞춰 읽습니다.

| 도구 | 먼저 적는 쪽 | 상대 | 정하는 방법 |
|---|---|---|---|
| Zeek | `orig`(발신 측) | `resp`(응답 측) | 먼저 보냈다고 판단한 쪽. 추정 규칙으로 뒤집으면 `history` 에 `^`[2] |
| Suricata | `src_ip`·`toserver` | `dest_ip`·`toclient` | 흐름을 연 쪽을 클라이언트로 봄([프로토콜 기록](../../02-artifacts/suricata/eve-json/protocol-events.md)) |
| tshark `-z follow` | `Node 0` | `Node 1` | 출력 머리에 두 노드의 주소·포트를 적고, 두 번째 노드가 보낸 데이터는 앞에 탭을 붙임[8] |
| tcpflow | 파일 이름 앞부분(보낸 쪽) | 파일 이름 뒷부분(받는 쪽) | 방향마다 파일이 따로 생김[9] |

### 여러 기록을 한 연결로 잇기

Zeek 는 `uid` 로 conn.log 와 dns.log·http.log 같은 로그를 잇고[1], Suricata 는 `flow_id` 로 한 흐름의 alert·fileinfo·http·anomaly·flow 기록을 묶습니다[3]. 두 값은 각 도구 안에서만 쓰는 키입니다. 서로 다른 도구의 기록을 이으려면 Community ID 를 씁니다. Suricata 는 `community-id: true` 로 켜면 모든 EVE 기록에 `community_id` 필드(예 `"1:LQU9qZlK+B5F3KDmev6m5PMibrg="`)를 붙이고, 기본값은 꺼짐입니다[4]. 시드 `community-id-seed`(0~65535, 기본 0)는 값을 맞춰 볼 모든 도구에서 같아야 합니다[4]. Zeek 는 `community-id-logging.zeek` 를 불러오면 conn.log 에 `community_id` 가 생깁니다[2]. Community ID 가 없으면 4-튜플(두 주소와 두 포트)과 시각 범위를 함께 맞춰 봅니다.

### 시각

캡처 파일의 시각은 패킷마다 캡처 도구가 찍은 도착 시각입니다([pcap 형식](../capture/pcap.md)). Zeek conn.log 의 `ts` 는 연결의 첫 패킷 시각이고[2], `duration` 에는 한쪽 방향이 닫힌 뒤 새 데이터가 없는 끝 패킷(보통 마지막 ACK)이 들어가지 않습니다[2]. Suricata flow 기록의 `flow.start`·`flow.end` 는 흐름의 시작과 마지막으로 본 패킷 시각이고, `age` 는 흐름 지속 시간입니다[3]. 기록 머리의 `timestamp` 는 흐름 기록을 쓴 시점이라 통신 시각과 다릅니다([Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)). tshark `-z conv,tcp` 는 대화마다 방향별 프레임·바이트, 합계, 상대 시작 시각, 지속 시간을 보여 주므로[8], 절대 시각이 필요하면 해당 스트림의 첫 패킷 시각을 따로 확인합니다.

흐름 기록은 대부분 연결이 끝나거나 비활동 한도가 지난 뒤에 한 줄로 나옵니다. 그래서 기록 파일 안의 줄 순서는 연결 시작 순서가 아니고, 수집 기간 끝까지 이어진 연결은 아직 기록에 없을 수 있습니다. 여러 기록의 시각을 합치는 방법은 [네트워크 기록의 시각](../records/timestamps.md) 에서 다룹니다.

## 포렌식에서 중요한 점

### 증명하는 것과 증명하지 못하는 것

TCP 연결 기록으로는 어느 시각에 어떤 주소·포트 쌍 사이에 연결 시도가 있었는지, 핸드셰이크가 끝났는지, 누가 FIN 이나 RST 로 먼저 끊었는지, 방향별로 몇 바이트·몇 패킷이 오갔는지를 증명할 수 있습니다[1][2]. 핸드셰이크가 끝났으면 상대 호스트(또는 그 주소로 응답한 장비)가 그 포트에서 연결을 받은 것입니다.

어떤 사용자나 프로세스가 연결했는지, 무엇을 보냈는지는 흐름 기록에 없습니다. 내용은 캡처에 페이로드가 남아 있을 때만 확인할 수 있고, 암호화돼 있으면 그마저 어렵습니다([TLS와 인증서](tls.md)). NAT 를 거친 주소는 실제 호스트와 다를 수 있습니다([IP 주소·포트·NAT 해석](../records/ip-nat.md)). 보고서에는 "파일을 보냈다" 가 아니라 "이 시각에 이 내부 IP·포트가 이 외부 IP·포트로 TCP 연결을 맺고 이만큼 보낸 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

### 캡처가 놓친 패킷

센서가 패킷을 놓치면 연결 상태 판단과 내용 복원이 함께 틀어집니다. Zeek 는 내용 틈을 `missed_bytes` 에 세고 `history` 에 `g` 를 적습니다. `missed_bytes` 가 0 이 아니면 패킷 손실이 있었다는 뜻이고, 보통 프로토콜 분석이 실패합니다[2]. Wireshark 는 현재 순서 번호가 다음 기대 순서 번호보다 크면 "TCP Previous segment not captured" 를, 상대가 캡처에 없는 세그먼트를 확인(ACK)했으면 "TCP ACKed unseen segment" 를 붙입니다[7]. 뒤의 경우는 받는 쪽이 그 데이터를 받았는데 센서만 보지 못했을 가능성이 큽니다. `tcp.stream.client.contiguity_count`·`tcp.stream.server.contiguity_count` 가 1 이 아니면 그 방향에 세그먼트가 아예 없거나(0) 빠진 데이터가 있는(2 이상) 것이라서, 파일을 꺼내기 전에 먼저 확인합니다[7].

### 중간부터 잡힌 연결

캡처나 센서가 시작되기 전에 열린 연결은 SYN 이 없어서 Zeek 는 `OTH` 로 적습니다[2]. Suricata 는 `midstream` 기본값이 `false` 라서 이런 세션을 스트림으로 받아들이지 않습니다[5]. Wireshark 에서는 재조립이 어긋나 HTTP 가 "Continuation", TLS 가 "Ignored Unknown Record" 로 보일 수 있습니다[7]. 이런 흔적은 연결이 이상하다는 뜻이 아니라 연결 시작이 수집 범위 밖에 있었다는 뜻일 가능성이 큽니다. 연결을 연 쪽과 연 시각은 다른 기록(호스트 기록, 방화벽 로그)으로 확인합니다.

### 거절과 무응답

그 주소의 호스트에 연결을 받는 포트가 없으면 명세대로 SYN 에 RST 로 답합니다[6]. 다만 중간 장비가 대신 RST 를 보냈을 가능성도 있습니다. 응답이 전혀 없으면(`S0`) 호스트가 없거나, 중간 장비가 패킷을 버렸거나, 센서가 반대 방향을 보지 못했을 가능성이 있습니다. 센서 위치에 따른 한 방향 캡처는 [어디서 캡처하나](../capture/capture-points.md) 에서 다룹니다.

### 같은 포트 쌍의 재사용

같은 주소·포트 쌍으로 새 연결이 열리면 도구가 두 연결을 구분해야 합니다. Wireshark 는 SYN(SYN+ACK 아님)이 기존 대화와 같은 주소·포트를 쓰면서 ISN 이 다르면 "TCP Port numbers reused" 를 붙입니다[7]. Zeek `history` 의 `s`·`f`·`h`·`r` 는 같은 종류의 앞 패킷과 순서 번호가 다를 때 다시 적히므로, `S` 가 여러 번 보이면 SYN 을 다른 ISN 으로 여러 번 보낸 것입니다[2].

## 함정

**흐름 하나가 연결 하나는 아닙니다.** 도구는 오가는 패킷이 없는 시간이 한도를 넘으면 흐름을 끝냅니다. Suricata 기본 설정 예의 TCP 한도는 new 60초, established 3600초, closed 120초이고, 모두 마지막 활동 뒤로 잽니다[5]. Zeek 는 21·22·23·513/tcp 포트와 FTP·SSH 분석기가 붙은 연결에 1시간을 쓰고[10], 그 밖의 기본 한도는 [연결 기록 (conn.log)](../../02-artifacts/zeek/zeek-logs/conn-log.md) 에 있습니다. 연결 유지 간격이 이 한도보다 길면 연결이 끊기지 않았어도 기록이 둘 이상으로 나뉠 수 있고, 뒤쪽 기록은 SYN 이 없는 중간 트래픽으로 보일 가능성이 있습니다. 두 도구의 한도가 달라서 같은 연결을 서로 다른 개수로 나눌 수도 있습니다.

**바이트 수의 기준이 다릅니다.** Zeek `orig_bytes` 는 페이로드 바이트이고 TCP 에서는 순서 번호로 계산해 큰 연결에서 틀릴 수 있으며, `orig_ip_bytes` 는 IP 헤더의 total_length 합입니다[2]. Suricata `bytes_toserver` 는 그 방향 전체 바이트 수입니다[3]. 전송량을 적을 때는 어느 필드인지 밝힙니다.

**UDP 의 `SF` 는 TCP 의 `SF` 와 다릅니다.** UDP 에는 연결 상태가 없어서 Zeek 가 정상 시작·종료로 판단했다는 뜻일 뿐입니다[1].

**Wireshark 분석 표시는 캡처 위치에 따라 달라집니다.** 서버 쪽, 클라이언트 쪽, 중간 가운데 어디서 캡처했느냐에 따라 재전송과 순서 뒤바뀜의 해석이 달라질 수 있습니다[7]. Wireshark 는 파일을 처음 열 때 패킷 목록 순서대로 한 번 분석하고, 이 분석은 "Analyze TCP sequence numbers" 설정으로 끄고 켭니다[7]. "Retransmission" 은 네트워크가 실제로 다시 보낸 것일 수도, 센서 쪽 캡처 손실 뒤에 보인 것일 수도 있으니 같은 캡처의 손실 표시와 함께 봅니다.

**재조립 설정의 기본값을 확인합니다.** "Allow subdissector to reassemble TCP streams" 는 기본으로 켜져 있고 "Reassemble out-of-order segments" 는 기본으로 꺼져 있습니다[7]. 순서가 뒤바뀐 세그먼트가 있는 캡처에서 파일을 꺼낼 때는 두 번째 설정도 켜야 합니다[7].

**체크섬 오류가 모두 네트워크 문제는 아닙니다.** Zeek `history` 의 `c` 는 체크섬이 틀린 패킷입니다[2]. 호스트에서 캡처하면 체크섬 계산을 네트워크 카드에 넘기는 설정 때문에 오류가 많이 보일 수 있습니다([어디서 캡처하나](../capture/capture-points.md)).

## 도구

| 도구 | 쓰는 곳 | 예 |
|---|---|---|
| Zeek | conn.log 로 연결 요약 | `conn_state`·`history`·`uid`[1][2] |
| Suricata | EVE `flow`·`netflow` 기록 | `flow_id`, `flow.start`·`flow.end`, `tcp_flags`[3] |
| tshark | 대화 목록과 스트림 내용 | `tshark -r a.pcap -q -z conv,tcp`, `-z "follow,tcp,ascii,0"`(0 은 첫 스트림)[8] |
| Wireshark | 순서 번호 분석과 완결성 필터 | `tcp.completeness==7`, `tcp.analysis` 표시, Follow TCP Stream[7] |
| tcpflow | 방향별 데이터 파일로 복원 | `tcpflow -a -o outdir -Fk -r packets.pcap`(1000 연결마다 디렉터리)[9] |

tcpflow 는 순서 번호를 보고 재전송과 순서 뒤바뀜에 상관없이 스트림을 다시 만듭니다[9]. `-b max_bytes` 로 흐름마다 저장할 최대 바이트를 정하고, 1.4 이전 버전은 흐름마다 4GiB 까지만 저장했습니다[9]. tshark 의 `-z follow` 는 `ascii`·`hex`·`raw`·`yaml` 등 출력 방식을 고를 수 있고, 스트림은 `ip0:port0,ip1:port1` 형식이나 스트림 번호로 지정합니다[8].

## 참고 문헌

1. Zeek 문서, "conn.log". https://github.com/zeek/zeek-docs/blob/master/logs/conn.rst
2. Zeek 스크립트 참조, "base/protocols/conn/main.zeek" (Conn::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
3. OISF, Suricata 사용자 안내서, "EVE JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
4. OISF, Suricata 사용자 안내서, "EVE JSON Output". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
5. OISF, Suricata 사용자 안내서, "suricata.yaml" (Flow Time-Outs, Stream-engine). https://github.com/OISF/suricata/blob/main/doc/userguide/configuration/suricata-yaml.rst
6. W. Eddy, Ed., "Transmission Control Protocol (TCP)", RFC 9293, 2022. https://www.rfc-editor.org/rfc/rfc9293.txt
7. Wireshark User's Guide, "Advanced Topics" (TCP Analysis, TCP Reassembly). https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_advanced.adoc
8. Wireshark, tshark 매뉴얼 페이지. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
9. tcpflow 매뉴얼 페이지. https://github.com/simsong/tcpflow/blob/master/doc/tcpflow.1.in
10. Zeek 스크립트 참조, "base/protocols/conn/inactivity.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/inactivity.zeek.rst
