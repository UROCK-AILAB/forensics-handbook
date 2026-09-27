---
title: "흐름 기록"
parent: "기반 · 기록 체계"
nav_order: 100
---

# 흐름 기록 (NetFlow·IPFIX·sFlow)

흐름 기록은 라우터·스위치·방화벽·센서가 지나가는 패킷을 주소·포트·프로토콜 같은 공통 속성으로 묶어, 언제부터 언제까지 어느 주소가 어느 주소로 몇 패킷·몇 바이트를 보냈는지 한 레코드로 남긴 것입니다. 패킷 내용은 없지만 연결 하나가 레코드 몇 개로 줄어들어서, 패킷 캡처가 없는 네트워크나 기간에도 통신 사실을 확인하는 데 씁니다. 이 페이지는 NetFlow v9·IPFIX 의 바이트 구조, 템플릿이 없으면 레코드를 풀 수 없는 문제, 흐름 시각을 절대 시각으로 바꾸는 방법, sFlow 가 흐름이 아니라 표본이라는 점을 다룹니다.

## 이 형식을 쓰는 아티팩트

흐름 (Flow) 은 관측 지점 (Observation Point) 을 일정 시간 동안 지나간 IP 패킷 가운데, 패킷 헤더와 처리 결과에서 나온 속성이 같은 패킷의 묶음입니다[1][2]. 흐름을 만들어 내보내는 장비를 익스포터 (Exporter), 받아서 저장하는 쪽을 컬렉터 (Collector) 라고 부릅니다[1]. 조사에서는 주로 컬렉터가 디스크에 쌓아 둔 파일을 읽습니다.

| 형식 | 명세 | 레코드 하나가 뜻하는 것 | 전송과 포트 |
|---|---|---|---|
| NetFlow v9 | RFC 3954 (Informational, 2004) | 흐름 하나 | 보통 UDP, 전송 방식에 묶이지 않아 SCTP 도 쓸 수 있음[1] |
| IPFIX | RFC 7011 (Standards Track, 2013) | 흐름 하나 | SCTP·TCP·UDP 4739, TLS·DTLS 는 4740[2] |
| sFlow v5 | sFlow.org (2004) | 표본으로 뜬 패킷 하나, 또는 인터페이스 카운터 | UDP 6343[6] |

IPFIX 는 NetFlow v9 을 이어받은 표준이라 버전 번호가 10이고, 정보 요소 번호 1~127 은 NetFlow v9 필드 형식 번호와 호환됩니다[2][4]. 그래서 두 형식의 필드 번호 표는 앞부분이 거의 같습니다. sFlow 의 옛 판(v4)은 RFC 3176 으로 나와 있고 데이터그램 버전 값이 4입니다[7].

컬렉터 쪽에서는 공개 도구 모음 nfdump 가 많이 쓰입니다. nfcapd 는 NetFlow v1, v5/v7, v9, IPFIX 를 받아 바이너리 파일로 저장하고, ASA 방화벽·NAT 장비가 보내는 이벤트 로깅도 받습니다[9]. sFlow 는 같은 도구 모음의 sfcapd 가 받습니다[16]. nfpcapd 는 인터페이스나 pcap 파일에서 패킷을 읽어 nfdump 형식의 흐름 레코드를 직접 만듭니다[15]. Security Onion 2.4 는 Elastic 의 NetFlow Records 통합으로 흐름을 받습니다[17]. IDS 가 만드는 흐름 이벤트(Suricata 의 `flow`·`netflow`)는 [네트워크 로그의 종류](log-types.md)와 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)에서, 클라우드의 흐름 로그는 클라우드 핸드북의 [AWS VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/aws/vpc-flow-logs.html)·[Azure 네트워크 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/azure/flow-logs.html)·[GCP VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/gcp/vpc-flow-logs.html)에서 다룹니다.

### 흐름이 레코드로 나오는 조건

익스포터는 흐름을 메모리에 들고 있다가 아래 조건 가운데 하나가 맞으면 레코드로 내보냅니다[1]. TCP 의 FIN 이나 RST 를 보는 것처럼 흐름이 끝난 것을 알아챘을 때, 정해진 시간 동안 그 흐름의 패킷이 없을 때(비활성 시간 제한, inactivity timeout), 오래 이어지는 흐름을 정기적으로 내보낼 때(활성 시간 제한, active timeout), 카운터가 넘치거나 메모리가 모자라 강제로 끝낼 때입니다. IPFIX 는 이 이유를 flowEndReason(정보 요소 136) 필드에 남길 수 있고, 값은 1 비활성 시간 초과, 2 활성 시간 초과, 3 흐름 끝 감지(예: TCP FIN), 4 외부 사건으로 강제 종료, 5 자원 부족입니다[4].

활성 시간 제한 때문에 한 TCP 연결이 레코드 여러 개로 쪼개집니다. Cisco 장비에서 `ip flow-cache timeout active 5` 로 설정하면 긴 흐름을 5분 단위로 나누고, 이 값은 1~60분 사이에서 정할 수 있습니다[11]. nfpcapd 의 기본값은 활성 300초, 비활성 60초입니다[15]. 장비마다 값이 달라서, 실제 값은 장비 설정이나 옵션 레코드의 FLOW_ACTIVE_TIMEOUT(36)·FLOW_INACTIVE_TIMEOUT(37), IPFIX 의 flowActiveTimeout(36)·flowIdleTimeout(37) 으로 확인합니다[1][4].

### 컬렉터 파일

nfcapd 는 받은 흐름을 flowdir 에 저장하고 기본 300초(5분)마다 새 파일로 바꿉니다. 가장 짧은 간격은 2초입니다[9]. 파일 이름은 `nfcapd.YYYYMMddhhmm` 형식이라 `nfcapd.202207110845` 는 2022-07-11 08:45 부터의 흐름이 든 파일이고, 간격을 60초보다 짧게 잡으면 이름에 초까지 붙습니다[9]. `-S` 로 날짜별 하위 폴더 구조를 고를 수 있어서, 같은 도구라도 설치마다 폴더 모양이 다릅니다[9]. 기본 수신 포트는 nfcapd·sfcapd 둘 다 9995 입니다[9][16]. nfdump 바이너리 파일은 NetFlow 버전과 상관없는 형식이지만, 파일을 쓴 기계의 바이트 순서(엔디언)에 따라 달라집니다[11].

## 구조 — 표와 오프셋

### NetFlow v9 내보내기 패킷

내보내기 패킷 (Export Packet) 은 20바이트 헤더 뒤에 FlowSet 이 하나 이상 이어지는 구조입니다[1]. 모든 숫자는 빅 엔디언입니다.

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 2 | Version | 9 |
| 2 | 2 | Count | 이 패킷에 든 레코드 수. 템플릿·옵션 템플릿·데이터 레코드를 모두 합한 값 |
| 4 | 4 | sysUpTime | 장비가 부팅한 뒤 지난 밀리초 |
| 8 | 4 | UNIX Secs | 이 패킷이 익스포터를 떠난 시각. 1970-01-01 00:00 UTC 이후 초 |
| 12 | 4 | Sequence Number | 이 관측 도메인에서 보낸 내보내기 패킷의 누적 번호. 컬렉터가 빠진 패킷을 찾는 데 씁니다 |
| 16 | 4 | Source ID | 익스포터의 관측 도메인 식별자 |

필드 정의는 RFC 3954 기준입니다[1]. 컬렉터는 보낸 IP 주소와 Source ID 를 묶어 같은 익스포터에서 온 여러 흐름 스트림을 구분합니다[1]. Source ID 는 v5·v8 헤더의 engine type·engine ID 에 해당하고, Cisco 구현에서는 앞 2바이트가 0, 셋째 바이트가 라우팅 엔진, 넷째 바이트가 라인카드를 나타냅니다[8].

헤더 뒤의 FlowSet 은 앞 4바이트(FlowSet ID 2바이트, Length 2바이트)로 종류와 길이를 알립니다. FlowSet ID 0 은 템플릿 FlowSet, 1 은 옵션 템플릿 FlowSet 이고, 256 이상이면 데이터 FlowSet 이며 그 ID 가 곧 데이터를 풀 템플릿의 ID 입니다. 템플릿 ID 0~255 는 예약돼 있습니다[1]. 템플릿 레코드는 템플릿 ID 와 필드 수 뒤에 (필드 형식 2바이트, 필드 길이 2바이트) 쌍을 필드 수만큼 늘어놓습니다[1].

데이터 레코드에는 필드 이름도 길이도 없고 값만 이어 붙어 있습니다. 그래서 같은 ID 의 템플릿을 먼저 받아 두지 않으면 데이터 레코드를 풀 수 없습니다[1]. 익스포터는 데이터 FlowSet 끝에 4바이트 경계를 맞추는 채움 바이트를 넣어야 하고(SHOULD, 0으로 채움), Length 에는 채움 바이트도 들어갑니다[1].

자주 보는 필드 형식은 아래와 같습니다[1]. 괄호 없는 길이는 고정 길이이고, N 은 템플릿이 길이를 정한다는 뜻입니다.

| 번호 | 이름 | 길이(바이트) | 뜻 |
|---|---|---|---|
| 1 | IN_BYTES | N (기본 4) | 흐름의 바이트 수 |
| 2 | IN_PKTS | N (기본 4) | 흐름의 패킷 수 |
| 4 | PROTOCOL | 1 | IP 프로토콜 번호 |
| 6 | TCP_FLAGS | 1 | 흐름에서 본 모든 TCP 플래그 |
| 7 / 11 | L4_SRC_PORT / L4_DST_PORT | 2 | 출발지·목적지 포트 |
| 8 / 12 | IPV4_SRC_ADDR / IPV4_DST_ADDR | 4 | 출발지·목적지 IPv4 |
| 10 / 14 | INPUT_SNMP / OUTPUT_SNMP | N (기본 2) | 들어온·나간 인터페이스 번호 |
| 21 | LAST_SWITCHED | 4 | 마지막 패킷을 처리한 때의 sysUpTime(밀리초) |
| 22 | FIRST_SWITCHED | 4 | 첫 패킷을 처리한 때의 sysUpTime(밀리초) |
| 27 / 28 | IPV6_SRC_ADDR / IPV6_DST_ADDR | 16 | 출발지·목적지 IPv6 |
| 32 | ICMP_TYPE | 2 | ICMP Type × 256 + Code |
| 34 | SAMPLING_INTERVAL | 4 | 100 이면 100개 중 1개를 표본으로 씀 |
| 35 | SAMPLING_ALGORITHM | 1 | 0x01 결정적, 0x02 무작위 표본 |
| 36 / 37 | FLOW_ACTIVE_TIMEOUT / FLOW_INACTIVE_TIMEOUT | 2 | 활성·비활성 시간 제한(초) |
| 60 | IP_PROTOCOL_VERSION | 1 | 템플릿에 없으면 4로 봅니다 |
| 61 | DIRECTION | 1 | 0 들어오는 흐름, 1 나가는 흐름 |

템플릿은 모든 패킷에 실리지 않으므로 컬렉터가 저장해 둬야 합니다[1]. 익스포터는 패킷 N개마다, 또는 N분마다 템플릿을 다시 보내야 하고, 두 간격 모두 사용자가 설정할 수 있어야 합니다(MUST)[1]. 익스포터나 NetFlow 프로세스가 다시 시작하면 템플릿 정보가 모두 사라지고 ID 를 새로 매기므로, 재시작 앞뒤의 같은 ID 가 같은 템플릿이라는 보장이 없습니다[1]. 컬렉터는 이미 있는 ID 에 새 정의가 오면 옛 정의를 버리고 새 정의를 써야 하고(MUST), 새로 고치지 않은 템플릿은 만료시키며 만료된 템플릿으로 데이터를 풀면 안 됩니다(MUST NOT)[1].

Sequence Number 의 단위는 버전마다 다릅니다. v5·v8 헤더에서는 흐름 수(total flows)였고 v9 에서 내보내기 패킷 수로 바뀌었습니다[8].

### IPFIX 메시지

IPFIX 메시지는 16바이트 헤더 뒤에 세트 (Set) 가 이어지는 구조이고, string·octetArray 를 뺀 모든 값은 빅 엔디언입니다[2].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 2 | Version | 0x000a (10) |
| 2 | 2 | Length | 헤더와 세트를 합친 메시지 전체 바이트 수 |
| 4 | 4 | Export Time | 헤더가 익스포터를 떠난 시각. 1970-01-01 00:00 UTC 이후 초, 부호 없는 32비트 |
| 8 | 4 | Sequence Number | 이 스트림·관측 도메인에서 보낸 데이터 레코드의 누적 수(2^32 로 나눈 나머지). 템플릿 레코드는 세지 않습니다 |
| 12 | 4 | Observation Domain ID | 흐름을 잰 관측 도메인 식별자 |

필드 정의는 RFC 7011 기준입니다[2]. UDP 로 보낼 때 Sequence Number 는 이 메시지 앞까지 보낸 데이터 레코드의 총수입니다[2]. 따라서 다음 메시지의 번호는 이번 번호에 이번 메시지의 데이터 레코드 수를 더한 값이 돼야 하고, 그보다 크면 그만큼 레코드가 빠진 것입니다.

세트 ID 2 는 템플릿 세트, 3 은 옵션 템플릿 세트, 4~255 는 예약, 256 이상은 데이터 세트입니다. 0 과 1 은 NetFlow v9 과 겹치지 않게 쓰지 않습니다[2]. 템플릿 안의 필드 지정자 (Field Specifier) 는 첫 비트가 엔터프라이즈 비트(E), 나머지 15비트가 정보 요소 번호, 그 뒤 2바이트가 필드 길이입니다. E 가 1 이면 IANA 기업 번호 4바이트가 뒤따르고, 이 필드는 IANA 목록이 아니라 그 기업이 정한 정보 요소입니다[2]. 필드 길이 65535 는 길이가 바뀌는 정보 요소라는 표시이고, 실제 길이는 값 앞 1바이트에 들어 있습니다. 그 1바이트가 255 이면 뒤 2바이트가 실제 길이입니다[2]. boolean 은 1 이 참, 2 가 거짓입니다[2].

정보 요소 (Information Element) 정의의 기준은 지금 IANA 의 IPFIX 레지스트리이고, RFC 7012 가 옛 정의 문서 RFC 5102 를 대체했습니다[3]. 조사에서 자주 보는 번호는 아래와 같습니다[4].

| 번호 | 이름 | 뜻 |
|---|---|---|
| 1 / 2 | octetDeltaCount / packetDeltaCount | 이번 레코드 동안의 바이트·패킷 수 |
| 4 | protocolIdentifier | IP 프로토콜 번호 |
| 6 | tcpControlBits | 흐름에서 본 TCP 플래그 |
| 7 / 11 | sourceTransportPort / destinationTransportPort | 출발지·목적지 포트 |
| 8 / 12 | sourceIPv4Address / destinationIPv4Address | 출발지·목적지 IPv4 |
| 21 / 22 | flowEndSysUpTime / flowStartSysUpTime | 마지막·첫 패킷의 부팅 뒤 밀리초 |
| 36 / 37 | flowActiveTimeout / flowIdleTimeout | 활성·비활성 시간 제한 |
| 85 | octetTotalCount | 측정 프로세스가 (다시) 시작된 뒤로 이 흐름에서 센 누적 바이트 수 |
| 130 | exporterIPv4Address | 익스포터 주소 |
| 136 | flowEndReason | 흐름을 끝낸 이유 |
| 150 / 151 | flowStartSeconds / flowEndSeconds | 첫·마지막 패킷 시각(초) |
| 152 / 153 | flowStartMilliseconds / flowEndMilliseconds | 첫·마지막 패킷 시각(밀리초) |
| 154 | flowStartMicroseconds | 첫 패킷 시각(NTP 형식) |
| 158 | flowStartDeltaMicroseconds | Export Time 을 기준으로 한 첫 패킷 시각 차 |
| 160 | systemInitTimeMilliseconds | 장비가 마지막으로 (다시) 초기화된 시각 |
| 161 | flowDurationMilliseconds | 흐름 지속 시간 |

tcpControlBits 는 흐름 안의 어느 패킷이라도 그 플래그가 켜져 있었으면 해당 비트가 1 입니다. 비트는 앞에서부터 예약 2비트, URG, ACK, PSH, RST, SYN, FIN 순서입니다[4]. NetFlow v9 의 TCP_FLAGS 도 흐름에서 본 모든 플래그를 모은 값입니다[1]. 두 필드 모두 플래그가 어떤 순서로 나왔는지는 알 수 없습니다.

UDP 로 보낼 때 익스포터는 템플릿을 주기적으로 다시 보내야 하고(MUST), 템플릿 철회 (Template Withdrawal) 메시지는 보내지 않습니다[2]. 템플릿 ID 는 재전송 간격의 3배 이상 기다린 뒤 다시 쓸 수 있어서, 재전송 간격과 컬렉터의 템플릿 수명이 맞지 않으면 데이터 레코드를 잘못 해석할 수 있습니다[2].

### 양방향 흐름

기본 흐름 레코드는 한 방향입니다. 그래서 TCP 연결 하나는 보통 레코드 두 개(요청 방향, 응답 방향)로 남습니다. IPFIX 는 RFC 5103 의 양방향 흐름 (Biflow) 으로 두 방향을 한 레코드에 담을 수 있고, 역방향 값은 기업 번호 29305 를 붙인 "역방향 정보 요소 (Reverse IE)" 로 적습니다[5]. 누가 시작했는지 알아야 하는 측정이면 측정 장비는 가능한 한 흐름을 시작한 쪽을 출발지(Source)로 둬야 하는데(SHOULD), 가장 단순한 방법은 처음 본 패킷을 시작 패킷으로 보는 것입니다[5]. 방향을 정한 방법은 biflowDirection(정보 요소 239)에 0x00 임의, 0x01 출발지가 시작한 쪽, 0x02 목적지가 시작한 쪽, 0x03 경계 밖이 출발지로 남길 수 있습니다[5].

### sFlow v5 데이터그램

sFlow 는 흐름을 만들지 않고 패킷을 표본으로 뜹니다. 방식은 통계적 패킷 샘플링 (Packet Flow Sampling) 과 시간 간격으로 인터페이스 카운터를 보내는 카운터 샘플링 (Counter Sampling) 두 가지입니다[6]. 패킷 샘플링은 패킷마다 카운터를 하나씩 줄이다가 0 이 되면 표본을 뜨고, 표본으로는 패킷 헤더를 복사하거나 특징을 뽑아 보냅니다[6]. 복사하는 헤더 길이의 기본값(sFlowFsMaximumHeaderSize)은 128바이트입니다[6].

데이터그램 헤더 sample_datagram_v5 에는 agent_address, sub_agent_id, 데이터그램마다 1씩 늘어나는 sequence_number, 장비 부팅 뒤 밀리초인 uptime, 표본 목록이 들어 있습니다[6]. 절대 시각 필드는 없습니다. uptime 은 송신 직전 값으로 채우라고 돼 있고, 받는 쪽은 서브 에이전트끼리 uptime 이 맞는다고 가정하면 안 됩니다(must not assume)[6].

흐름 표본(flow_sample)에는 sequence_number, source_id, 표본 비율 sampling_rate, 표본이 될 수 있었던 전체 패킷 수 sample_pool, 자원이 모자라 표본을 버린 횟수 drops, 들어온·나간 인터페이스, 흐름 레코드가 들어 있습니다[6]. drops 를 감지하지 못하는 에이전트는 이 값을 항상 0 으로 보냅니다[6]. 복사된 헤더 레코드(sampled_header)의 frame_length 는 표본을 뜨기 전 원래 패킷 길이입니다[6].

## 읽는 법

흐름 기록은 템플릿이 있어야 풀리기 때문에, 컬렉터가 이미 풀어서 저장한 파일(nfdump 파일, SIEM 에 들어간 레코드)을 읽는 경우가 대부분입니다. 익스포터가 컬렉터로 보내는 내보내기 패킷을 캡처한 pcap 이 있으면, 아래처럼 UDP 페이로드를 헤더부터 직접 따라갈 수 있습니다.

### 헥스로 따라가기 (명세로 만든 예시)

아래 20바이트는 RFC 3954 헤더 정의대로 만든 NetFlow v9 헤더입니다. 버전 9, 레코드 3개, sysUpTime 86,400,000밀리초(1일), UNIX Secs 2026-01-01 00:00:00 UTC, 순번 1, Source ID 0 입니다.

```
00 09  00 03  05 26 5C 00  69 55 B9 00  00 00 00 01  00 00 00 00
버전   Count  sysUpTime    UNIX Secs    Sequence     Source ID
```

FIRST_SWITCHED·LAST_SWITCHED 는 부팅 뒤 밀리초라서 헤더 값으로 바꿔야 절대 시각이 됩니다. 명세의 정의대로 계산하면 절대 시각은 `UNIX Secs − (sysUpTime − FIRST_SWITCHED) ÷ 1000` 입니다[1]. 이 패킷 안 데이터 레코드의 FIRST_SWITCHED 가 86,340,000(`05 25 71 A0`)이면, 1767225600 − (86,400,000 − 86,340,000) ÷ 1000 = 1767225540 이고 이는 2025-12-31 23:59:00 UTC 입니다. UNIX Secs 가 초 단위라서 이렇게 구한 값은 1초보다 정밀하지 않습니다.

아래 68바이트는 RFC 7011 정의대로 만든 IPFIX 메시지입니다. 템플릿 세트 하나와 그 템플릿으로 풀리는 데이터 레코드 하나가 들어 있습니다. 주소는 만든 예시입니다.

```
오프셋  바이트                                          뜻
0000    00 0A 00 44 69 55 B9 00 00 00 00 10 00 00 00 01  버전 10, 길이 68, Export Time 2026-01-01 00:00:00 UTC, 순번 16, 관측 도메인 1
0010    00 02 00 18 01 00 00 04                          템플릿 세트(ID 2, 길이 24), 템플릿 ID 256, 필드 4개
0018    00 08 00 04 00 0C 00 04                          sourceIPv4Address 4바이트, destinationIPv4Address 4바이트
0020    00 01 00 08 00 98 00 08                          octetDeltaCount 8바이트, flowStartMilliseconds(152) 8바이트
0028    01 00 00 1C                                      데이터 세트(ID 256 = 템플릿 256, 길이 28)
002C    C0 A8 01 0A CB 00 71 05                          192.168.1.10 → 203.0.113.5
0034    00 00 00 00 00 01 E2 40                          123,456 바이트
003C    00 00 01 9B 76 D9 BD A0                          1767225540000 ms = 2025-12-31 23:59:00.000 UTC
```

데이터 세트의 ID 256 을 보고 템플릿 256 을 찾아, 필드 길이 4·4·8·8 바이트대로 값을 자릅니다. 템플릿 세트가 이 메시지에 없고 컬렉터도 템플릿을 받아 두지 않았다면, 데이터 세트의 24바이트는 어디서 어디까지가 주소이고 바이트 수인지 알 수 없습니다. 순번 16 은 이 메시지 앞까지 데이터 레코드 16개를 보냈다는 뜻이라서, 같은 스트림의 다음 메시지 순번은 17 이어야 합니다[2].

### nfdump 로 읽기

nfdump 파일은 `nfdump -r` 로 읽습니다. `-r` 에는 파일 하나나 폴더를 줄 수 있고, 폴더를 주면 그 아래 파일을 모두 읽습니다[10]. 시간 범위는 예전 `-t` 옵션 대신 `first seen`·`last seen` 필터로 거릅니다[10]. 시각이 어느 시간대로 찍히는지 한 번에 보려면 epoch 과 GMT 태그를 함께 출력합니다.

```
nfdump -r /flows/2026/01/01 -o 'fmt:%tsr %ts %tsg %td %pr %sa %sp %da %dp %pkt %byt' 'host 192.0.2.10'
```

`%tsr` 은 첫 패킷 시각의 epoch 초(소수), `%ts` 는 같은 시각을 사람이 읽는 형식으로, `%tsg` 는 GMT 로 보여 줍니다. `%te`·`%ter`·`%teg` 는 마지막 패킷, `%tr`·`%trr`·`%trg` 는 컬렉터가 받은 시각, `%td` 는 지속 시간입니다[10]. 흐름 여러 개를 연결 단위로 합칠 때는 5-튜플로 묶는 `-a`, 묶을 요소를 고르는 `-A`, 두 방향을 한 줄로 합치는 `-b` 를 씁니다[10]. 분석 절차는 [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md)에서 다룹니다.

pcap 만 있고 흐름 기록이 없으면 nfpcapd 로 흐름을 만들 수 있지만, `-r` 은 마이크로초 단위의 기존 pcap 만 읽고 pcapng 와 나노초 pcap 은 읽지 못합니다[15]. pcapng 는 먼저 pcap 으로 바꿔야 하며, 변환 방법은 [큰 캡처 파일 다루기](../../03-techniques/acquisition/large-captures.md)에 있습니다. 이렇게 만든 흐름은 nfpcapd 의 시간 제한(기본 활성 300초, 비활성 60초)을 따르므로, 원래 장비가 만든 흐름과 레코드 경계가 다를 수 있습니다[15].

## 포렌식에서 중요한 점

### 시각이 뜻하는 것

흐름 레코드의 시작·끝 시각은 익스포터 시계로 잰 첫 패킷과 마지막 패킷의 시각입니다. 레코드를 내보낸 시각(NetFlow v9 UNIX Secs, IPFIX Export Time)과 컬렉터가 받은 시각(nfdump `%tr`)은 따로 있습니다[1][2][10]. FIN·RST 없이 끝난 흐름은 비활성 시간 제한(예: 60초)이 지나야 레코드로 나가므로, 받은 시각을 통신 시각으로 쓰면 안 됩니다.

형식마다 시각을 적는 방식이 다릅니다. NetFlow v9 의 FIRST_SWITCHED·LAST_SWITCHED 는 부팅 뒤 밀리초라서 헤더로 환산해야 하고, sysUpTime 이 32비트 밀리초라서 필드 폭으로 계산하면 약 49.7일마다 0 으로 돌아갑니다. IPFIX 의 Export Time 과 초 단위 시각(dateTimeSeconds)은 부호 없는 32비트 초라서 2106-02-07 06:28:16 UTC 에 넘치고, 밀리초 형식(dateTimeMilliseconds)은 64비트라 넘칠 걱정이 없습니다[2]. 마이크로초·나노초 형식은 1900-01-01 UTC 부터 센 NTP 형식이고 지금 NTP 시대는 2036-02-08 까지이며, 마이크로초 형식은 분수 부분의 아래 11비트를 무시해야 합니다(MUST)[2]. flowStartDeltaMicroseconds 처럼 Export Time 기준의 차이를 적는 필드는 32비트라서, 레코드 시각이 Export Time 으로부터 71분 안에 있어야 합니다[2]. 흐름 파일을 오래 보관할 때는 시각 해석에 필요한 맥락 정보도 함께 저장해 둡니다(RECOMMENDED)[2]. sFlow 는 절대 시각 필드가 없어서 컬렉터가 받은 시각에 기대야 합니다[6].

nfdump 는 내부에 epoch 밀리초로 저장하지만, `%ts`·`%te`·`%tr` 과 JSON 출력의 `first`·`last`·`received` 는 nfdump 를 실행한 컴퓨터의 현지 시간대로 바꿔 시간대 표시 없이 찍습니다[12][13]. GMT 로 보려면 `%tsg`·`%teg`·`%trg` 를 씁니다[10][12]. nfcapd 파일 이름의 시각도 컬렉터 컴퓨터의 현지 시각으로 만들어집니다[14]. 여러 기록의 시각을 맞추는 방법은 [네트워크 기록의 시각](timestamps.md)에서 다룹니다.

### 증명하는 것

흐름 레코드로는 이 관측 지점에서 이 시간대에 이 출발지·목적지 주소와 포트, 프로토콜로 이만큼의 패킷·바이트가 오간 기록이 있다는 것을 보일 수 있습니다. 표본을 쓴 흐름이면 이 숫자는 추정값입니다. TCP 플래그를 모은 값으로 흐름 안에 SYN·FIN·RST 가 한 번이라도 있었는지 알 수 있고, IPFIX 의 flowEndReason 이 있으면 흐름이 정상 종료로 끝났는지 시간 초과로 잘렸는지도 알 수 있습니다[4].

### 증명하지 못하는 것

흐름 기록에는 페이로드가 없어서 무엇을 보냈는지, 파일 이름, 사용자 계정은 알 수 없습니다. 플래그가 어떤 순서로 나왔는지도 모릅니다[4]. 어느 쪽이 연결을 시작했는지도 확실하지 않습니다. 단방향 레코드 두 개는 어느 쪽이 먼저인지 시작 시각으로만 추정할 수 있고, 양방향 흐름도 처음 본 패킷을 시작 패킷으로 가정한 결과일 수 있습니다[5]. 활성 시간 제한으로 잘린 긴 흐름에서는 다음 레코드의 "첫 패킷" 이 사실은 중간 패킷이라 이 가정이 틀릴 수 있습니다[5].

흐름 기록이 없다고 통신이 없었던 것도 아닙니다. 내보내기는 보통 UDP 라서 패킷이 빠질 수 있고, 이는 순번이 건너뛴 자리로 확인합니다[1][2]. 템플릿을 받지 못한 데이터 레코드는 풀 수 없고[1], 표본을 쓰면 짧은 연결은 통째로 표본에서 빠질 수 있습니다. 익스포터는 자기 관측 지점을 지나간 트래픽만 보므로, 같은 연결도 NAT 앞과 뒤에서 다른 주소로 남습니다. 주소 변환을 따라가는 법은 [IP 주소·포트·NAT 해석](ip-nat.md)에서, 관측 위치에 따른 차이는 [어디서 캡처하나](../capture/capture-points.md)에서 다룹니다.

sFlow 는 흐름이 아니라 패킷 표본이라서 연결 단위의 합계가 아닙니다[6]. 보고서에는 "이 시간대에 이 내부 주소에서 이 외부 주소로 향한 표본 패킷이 N개 있었고, 표본 비율로 환산하면 약 M바이트" 처럼 표본이라는 점을 밝혀 씁니다.

### 지우기와 손상

흐름 기록은 통신한 PC 가 아니라 컬렉터에 쌓이므로, 조사 대상 PC 에서 흔적을 지워도 컬렉터 파일은 영향을 받지 않습니다. 대신 컬렉터 파일이 지워지거나 보관 기간이 지나 밀려나면 그 기간의 흐름은 다른 곳에서 찾아야 합니다. 수집 중 빠진 부분은 내보내기 헤더 순번의 공백으로, 컬렉터가 멈췄던 기간은 다시 받기 시작한 첫 메시지의 순번이 마지막으로 받은 순번보다 크게 뛴 자리로 확인합니다[1][2].

## 함정

**긴 연결이 여러 레코드로 쪼개집니다.** 활성 시간 제한 단위로 레코드가 나뉘므로 다운로드·업로드 총량은 레코드를 합쳐야 나옵니다[1][11]. nfdump 의 `-a`·`-A` 로 합칩니다[10].

**템플릿 ID 가 바뀌거나 재사용됩니다.** 익스포터가 재시작하면 ID 를 새로 매기고, IPFIX 는 UDP 에서 일정 시간 뒤 같은 ID 를 다른 템플릿에 쓸 수 있습니다[1][2]. 옛 템플릿으로 새 데이터를 풀면 주소 자리에 바이트 수가 들어가는 식으로 값이 엉뚱하게 나옵니다. 값이 이상하면 그 시점 전후의 템플릿 레코드를 다시 확인합니다.

**순번의 단위가 버전마다 다릅니다.** NetFlow v5·v8 은 흐름 수, v9 는 내보내기 패킷 수, IPFIX 는 데이터 레코드 수입니다[8][1][2]. 빠진 양을 계산할 때 단위를 맞춰야 합니다.

**표본 흐름의 숫자는 곱해서 늘린 값입니다.** nfcapd 는 표본 비율만큼 패킷·바이트 카운터를 곱하므로 SNMP 같은 다른 출처의 카운터와 다를 수 있습니다[9]. `-s` 에 음수를 주면 익스포터가 알린 비율을 무시하고 그 절댓값을 모든 레코드에 강제합니다[9]. 컬렉터를 어떻게 설정했는지 먼저 확인합니다.

**카운터가 넘칠 수 있습니다.** NetFlow v5·v7 은 32비트 카운터라 바쁜 라우터에서 넘칠 수 있고, 활성 시간 제한을 줄여 피합니다. nfdump 는 내부에서 64비트를 씁니다[11].

**출발 포트가 고정된 트래픽은 요청이 한 흐름으로 묶입니다.** 운영 네트워크에서 YAF 로 흐름을 만든 실험(활성 60초, 비활성 15초)에서, 같은 출발 포트로 질의를 계속 보내는 DNS 터널은 큰 흐름 하나로 보였습니다. 반면 로컬 리졸버를 거친 터널은 요청마다 새 포트를 써서 흐름 하나하나가 정상 DNS 흐름과 구분되지 않았고, 일정 시간 구간마다 센 흐름 수나 패킷당 평균 바이트 수로 봐야 했습니다[18]. DNS 터널 조사는 [DNS 로 몰래 보냈나](../../04-scenarios/exfiltration/dns-tunneling.md)에서 다룹니다.

**출력 시각은 분석 PC 시간대입니다.** 다른 PC 에서 뽑은 nfdump 결과와 비교하면 몇 시간 어긋날 수 있습니다. `%tsr` 이나 `%tsg` 를 함께 출력해 확인합니다[10][12].

**`-B` 의 방향은 포트 번호 규칙입니다.** `-B` 는 TCP·UDP 에서 출발 포트가 목적지 포트보다 작고 출발 포트가 1024 미만, 목적지 포트가 1024 초과이면 두 방향을 뒤집어 보여 줍니다. 편의를 위한 옵션일 뿐이라, 누가 연결을 시작했는지의 근거로 쓰지 않습니다[10].

**기본 수신 포트가 도구마다 다릅니다.** IPFIX 명세는 4739[2], nfcapd·sfcapd 는 9995[9][16], Security Onion 2.4 의 NetFlow 수신은 UDP 2055[17], sFlow 명세는 6343[6] 입니다. 캡처에서 내보내기 패킷을 찾을 때는 장비 설정에서 실제 포트를 확인합니다.

**흐름 시간 제한 값이 장비와 도구마다 다릅니다.** nfpcapd 기본값은 활성 300초·비활성 60초이고[15], Cisco 설정 예에는 활성 5분, 또는 활성 1분·비활성 60초가 쓰입니다[11]. 위 DNS 터널 실험은 활성 60초·비활성 15초였습니다[18]. 조사하는 장비의 실제 값은 옵션 레코드나 장비 설정으로 확인합니다[1][4].

## 도구

| 도구 | 하는 일 | 참고 |
|---|---|---|
| nfcapd | NetFlow v1·v5/v7·v9·IPFIX 수신, 파일 저장 | [9] |
| sfcapd | sFlow 수신 | [16] |
| nfpcapd | pcap(마이크로초)에서 흐름 레코드 생성 | [15] |
| nfdump | nfdump 파일 조회·필터·집계·통계, 출력 형식 line·long·extended·csv·json 등 | [10] |
| Security Onion | Elastic NetFlow Records 통합으로 수신 | [17] |
| YAF | 패킷에서 IPFIX 흐름을 만드는 프로브 | [18] |

## 함께 볼 페이지

- [네트워크 로그의 종류](log-types.md) — 흐름 기록과 Zeek·Suricata·방화벽 로그의 단위 차이
- [네트워크 기록의 시각](timestamps.md) — 흐름·로그·캡처 시각 맞추기
- [IP 주소·포트·NAT 해석](ip-nat.md) — NAT 앞뒤 주소 추적
- [TCP 연결과 흐름](../protocols/tcp-sessions.md) — TCP 플래그와 연결 상태
- [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md) — nfdump 분석 절차
- [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration.md) — 흐름 바이트 수로 유출량 추정

## 참고 문헌

1. B. Claise, "Cisco Systems NetFlow Services Export Version 9", RFC 3954 (Informational), 2004. https://www.rfc-editor.org/rfc/rfc3954.txt
2. B. Claise, B. Trammell, P. Aitken, "Specification of the IP Flow Information Export (IPFIX) Protocol for the Exchange of Flow Information", RFC 7011, 2013. https://www.rfc-editor.org/rfc/rfc7011.txt
3. B. Claise, B. Trammell, "Information Model for IP Flow Information Export (IPFIX)", RFC 7012, 2013. https://www.rfc-editor.org/rfc/rfc7012.txt
4. J. Quittek 외, "Information Model for IP Flow Information Export", RFC 5102, 2008. https://www.rfc-editor.org/rfc/rfc5102.txt
5. B. Trammell, E. Boschi, "Bidirectional Flow Export Using IP Flow Information Export (IPFIX)", RFC 5103, 2008. https://www.rfc-editor.org/rfc/rfc5103.txt
6. sFlow.org, "sFlow Version 5", 2004. https://sflow.org/sflow_version_5.txt
7. P. Phaal, S. Panchen, N. McKee, "InMon Corporation's sFlow: A Method for Monitoring Traffic in Switched and Routed Networks", RFC 3176 (Informational), 2001. https://www.rfc-editor.org/rfc/rfc3176.txt
8. Cisco, "NetFlow Version 9 Flow-Record Format" (백서). https://www.cisco.com/en/US/technologies/tk648/tk362/technologies_white_paper09186a00800a3db9.html
9. nfdump, nfcapd(1) 매뉴얼. https://github.com/phaag/nfdump/blob/master/man/nfcapd.1
10. nfdump, nfdump(1) 매뉴얼 (nfdump 1.7.10). https://github.com/phaag/nfdump/blob/master/man/nfdump.1
11. nfdump, README. https://github.com/phaag/nfdump/blob/master/README.md
12. nfdump 소스 코드, src/output/output_fmt.c. https://github.com/phaag/nfdump/blob/master/src/output/output_fmt.c
13. nfdump 소스 코드, src/output/output_json.c. https://github.com/phaag/nfdump/blob/master/src/output/output_json.c
14. nfdump 소스 코드, src/collector/collector.c. https://github.com/phaag/nfdump/blob/master/src/collector/collector.c
15. nfdump, nfpcapd(1) 매뉴얼. https://github.com/phaag/nfdump/blob/master/man/nfpcapd.1
16. nfdump, sfcapd(1) 매뉴얼. https://github.com/phaag/nfdump/blob/master/man/sfcapd.1
17. Security Onion 2.4 문서, "NetFlow". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/netflow.rst
18. W. Ellens, P. Żuraniewski, A. Sperotto, H. Schotanus, M. Mandjes, E. Meeuwissen, "Flow-Based Detection of DNS Tunnels", Lecture Notes in Computer Science 7943 (AIMS 2013), 2013. doi:10.1007/978-3-642-38998-6_16
