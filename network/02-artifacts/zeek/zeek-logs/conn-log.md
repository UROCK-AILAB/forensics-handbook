---
title: "연결 기록"
parent: "Zeek 로그"
grand_parent: "아티팩트 · Zeek"
nav_order: 150
---

# 연결 기록 (conn.log)

Zeek 는 센서가 본 TCP 연결과 UDP·ICMP 흐름마다 conn.log 에 한 줄을 씁니다. 이 한 줄로 누가 누구와, 언제, 얼마 동안, 어떤 프로토콜로, 몇 바이트를 주고받았는지와 연결이 어떻게 열리고 닫혔는지를 알 수 있습니다. 이 페이지는 conn.log 의 필드와 `conn_state`·`history` 값, 시각을 읽는 법, 한 줄로 주장할 수 있는 범위를 다룹니다. TSV·JSON 형식, `#open` 같은 머리 줄, `uid` 의 성질, zeek-cut·jq 사용법은 [Zeek 로그](index.md) 에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

conn.log 는 3계층(IP)과 4계층(TCP·UDP) 수준의 요약입니다[1]. TCP 는 연결 단위로 기록하고, 상태가 없는 UDP·ICMP 는 같은 출발지 호스트·포트에서 같은 목적지 호스트·포트로 가는 패킷 묶음을 하나의 "연결" 로 보고 기록합니다[2]. ICMP 줄에서는 출발지 포트 자리에 ICMP 유형 (type), 목적지 포트 자리에 ICMP 코드 (code) 가 들어갑니다[2].

Zeek 7.1.0 부터는 TCP·UDP·ICMP 가 아닌 IP 프로토콜(IGMP·OSPF 등)의 흐름도 conn.log 에 나옵니다. 이런 줄은 `proto` 가 `unknown_transport`, 포트가 0, `conn_state` 가 `OTH` 이고, 프로토콜은 `ip_proto` 번호(OSPF 이면 89)로만 알 수 있습니다[1][7].

Zeek 는 연결 상태를 메모리에서 지울 때(`connection_state_remove` 이벤트) conn.log 에 줄을 씁니다[2]. 그래서 한 줄은 연결이 끝났거나, 오래 조용해서 Zeek 가 추적을 그만둔 뒤에 생깁니다. 이 시점이 언제인지는 아래 [시각 해석](#시각-해석) 에서 다룹니다.

## 위치와 버전별 차이

파일 위치·교대(rotate) 규칙·압축은 다른 Zeek 로그와 같아서 [Zeek 로그](index.md) 에서 다룹니다. conn.log 에 영향을 준 버전 변화는 다음과 같습니다.

| 버전 | 바뀐 점 |
|---|---|
| Bro 2.6 | `history` 에 `W`/`w`(0 윈도 광고) 추가. `C`·`T`·`W` 가 10번·100번 단위로 반복 기록되기 시작[7] |
| Zeek 3.0.0 | `history` 에 `G`/`g`(내용 틈) 추가. FIN·RST 와 함께 끝에 온 ACK 가 드러낸 틈은 믿을 수 없다고 보고 `missed_bytes` 에 넣지 않음[7] |
| Zeek 6.1.0 | 브로드캐스트 주소로 가는 연결은 잘 알려진 서버 포트를 근거로 방향을 뒤집지 않음. 이전에는 255.255.255.255 가 발신 측으로 기록되기도 함[7] |
| Zeek 6.2.0 | `history` 에 `X`/`x`(한도 초과 등으로 분석을 일부만 함) 추가[7][2] |
| Zeek 7.1.0 | TCP·UDP·ICMP 아닌 IP 흐름도 기록. 모든 줄에 `ip_proto` 추가[7] |
| Zeek 7.2.0 | 터널 안 연결에도 `ip_proto` 를 채움[7] |

7.1 이전 동작으로 되돌리는 정책 스크립트 `policy/protocols/conn/disable-unknown-ip-proto-support.zeek` 를 불러온 센서에서는 `ip_proto` 가 없습니다[1]. Zeek 스크립트 참조 문서의 필드 목록에는 `ip_proto` 에 기록 표시(`&log`)가 빠져 있지만, 스크립트 원본에는 `&log` 가 붙어 있고 로그 예시에도 나옵니다[3][2][1]. 실제 로그에 이 필드가 있는지는 TSV 의 `#fields` 줄이나 JSON 키로 확인합니다.

## 구조

### 한 줄의 모양

다음은 TCP 연결 하나와 DNS 질의가 오간 UDP 흐름 하나를 TSV 로 쓴 모양입니다(만든 예시, 머리 줄 일부 생략).

```text
#fields	ts	uid	id.orig_h	id.orig_p	id.resp_h	id.resp_p	proto	service	duration	orig_bytes	resp_bytes	conn_state	local_orig	local_resp	missed_bytes	history	orig_pkts	orig_ip_bytes	resp_pkts	resp_ip_bytes	tunnel_parents	ip_proto
#types	time	string	addr	port	addr	port	enum	string	interval	count	count	string	bool	bool	count	string	count	count	count	count	set[string]	count
1772414130.305988	CExample1dns00001	192.168.0.10	36844	192.168.0.1	53	udp	dns	0.066852	62	141	SF	-	-	0	Dd	2	118	2	197	-	17
1772414130.430166	CExample2http0002	192.168.0.10	46378	203.0.113.5	80	tcp	http	0.254115	77	295	SF	-	-	0	ShADadFf	6	397	4	511	-	6
```

같은 TCP 연결을 JSON 으로 쓰면 다음과 같습니다(만든 예시). JSON 은 값이 없는 필드를 기본으로 빼고 쓰므로 `local_orig`·`local_resp`·`tunnel_parents` 키가 없습니다([Zeek 로그](index.md) 참고).

```json
{"ts":1772414130.430166,"uid":"CExample2http0002","id.orig_h":"192.168.0.10","id.orig_p":46378,"id.resp_h":"203.0.113.5","id.resp_p":80,"proto":"tcp","service":"http","duration":0.25411510467529297,"orig_bytes":77,"resp_bytes":295,"conn_state":"SF","missed_bytes":0,"history":"ShADadFf","orig_pkts":6,"orig_ip_bytes":397,"resp_pkts":4,"resp_ip_bytes":511,"ip_proto":6}
```

### 기본 필드

기본으로 기록하는 필드는 다음과 같습니다[2][3].

| 필드 | 형 | 뜻 |
|---|---|---|
| `ts` | time | 첫 패킷 시각 |
| `uid` | string | Zeek 가 연결마다 붙이는 고유 ID. 다른 로그와 잇는 열쇠 |
| `id.orig_h` / `id.orig_p` | addr / port | 발신 측 (originator) 주소·포트 |
| `id.resp_h` / `id.resp_p` | addr / port | 응답 측 (responder) 주소·포트 |
| `proto` | enum | `tcp`·`udp`·`icmp`·`unknown_transport`. 응답 측 포트의 전송 프로토콜에서 가져옴 |
| `service` | string | 프로토콜 분석기가 확인한 프로토콜 목록. 소문자로 바꿔 쉼표로 이음 |
| `duration` | interval | 연결이 이어진 시간(초) |
| `orig_bytes` / `resp_bytes` | count | 방향별 페이로드 바이트. TCP 는 순서 번호로 계산 |
| `conn_state` | string | 연결 상태 요약(아래 표) |
| `local_orig` / `local_resp` | bool | 발신·응답 측 주소가 `Site::local_nets` 안에 있는지 |
| `missed_bytes` | count | 내용 틈 (content gap) 으로 놓친 바이트. 기본 0 |
| `history` | string | 연결에서 일어난 일을 글자로 적은 이력(아래 표) |
| `orig_pkts` / `resp_pkts` | count | 방향별 IP 패킷 수 |
| `orig_ip_bytes` / `resp_ip_bytes` | count | 방향별 IP 계층 바이트. IP 헤더의 total_length 를 더한 값 |
| `tunnel_parents` | set[string] | 터널 안 연결이면 바깥 연결의 `uid` |
| `ip_proto` | count | IP 헤더의 프로토콜 번호(7.1.0 부터) |

몇 필드는 조건이 맞을 때만 값이 들어갑니다. `duration`·`orig_bytes`·`resp_bytes` 는 `duration` 이 0보다 클 때만 채우고, 패킷 수와 IP 바이트는 `duration` 이 0이어도 채웁니다[2]. 패킷 수와 IP 바이트는 `use_conn_size_analyzer` 가 켜져 있어야 채우는데, 기본값이 켜짐(T)입니다[2][4]. `local_orig`·`local_resp` 는 `Site::local_nets` 가 비어 있으면 항상 빈 값입니다[2]. `service` 는 `DPD::track_removed_services_in_connection` 을 켠 센서에서 파싱 오류로 떼어 낸 분석기를 `-` 를 붙여 함께 적습니다[2].

정책 스크립트를 불러와야 생기는 필드도 있습니다[3].

| 필드 | 불러올 스크립트 (`policy/protocols/conn/`) | 뜻 |
|---|---|---|
| `community_id` | `community-id-logging.zeek` | 다른 도구와 흐름을 잇는 해시 |
| `failed_service` | `failed-service-logging.zeek` | 오류로 떼어 낸 분석기를 뗀 순서대로 |
| `ip_proto_name` | `ip-proto-name-logging.zeek` | `ip_proto` 의 이름 |
| `orig_l2_addr` / `resp_l2_addr` | `mac-logging.zeek` | 방향별 링크 계층 주소(MAC) |
| `vlan` / `inner_vlan` | `vlan-logging.zeek` | 바깥·안쪽 VLAN 번호 |
| `pppoe_session_id` | `pppoe-session-id-logging.zeek` | PPPoE 세션 ID |
| `speculative_service` | `speculative-service.zeek` | 시그니처로만 짐작한 프로토콜. 분석기를 붙이지 못해 확인되지 않음 |

### conn_state

`conn_state` 는 연결이 끝났을 때 양쪽 끝의 상태를 보고 정합니다[2].

| 값 | 뜻 |
|---|---|
| `S0` | 연결 시도만 보고 응답은 못 봄 |
| `S1` | 연결이 맺어졌고 종료는 못 봄 |
| `SF` | 정상으로 맺어지고 정상으로 종료됨 |
| `REJ` | 연결 시도가 거부됨 |
| `S2` | 맺어진 뒤 발신 측의 종료 시도만 봄(응답 측 응답 없음) |
| `S3` | 맺어진 뒤 응답 측의 종료 시도만 봄(발신 측 응답 없음) |
| `RSTO` | 맺어진 뒤 발신 측이 RST 로 끊음 |
| `RSTR` | 응답 측이 RST 를 보냄 |
| `RSTOS0` | 발신 측이 SYN 뒤에 RST 를 보냄. 응답 측 SYN-ACK 는 못 봄 |
| `RSTRH` | 응답 측이 SYN-ACK 뒤에 RST 를 보냄. 발신 측 SYN 은 못 봄 |
| `SH` | 발신 측이 SYN 뒤에 FIN 을 보냄. SYN-ACK 는 못 봄(반만 열림) |
| `SHR` | 응답 측이 SYN-ACK 뒤에 FIN 을 보냄. 발신 측 SYN 은 못 봄 |
| `OTH` | SYN 을 못 보고 중간 트래픽만 봄 |

TCP 에서 `REJ` 는 응답 측이 RST 를 보냈고 발신 측이 아직 SYN 이나 SYN-ACK 만 보낸 상태이거나, 양쪽 모두 RST 이면서 주고받은 바이트가 0일 때 붙습니다[2]. UDP 는 양쪽 다 보냈으면 `SF`, 발신 측만 보냈으면 `S0`, 응답 측만 보냈으면 `SHR`, 그 밖에는 `OTH` 이고, TCP·UDP 가 아닌 흐름은 모두 `OTH` 입니다[2]. UDP 에는 연결 상태가 없어서 UDP 줄의 `SF` 는 양쪽이 서로 데이터를 보냈다는 뜻으로만 읽습니다[1].

### history

`history` 는 연결에서 본 사건을 글자로 이어 적습니다. 대문자는 발신 측, 소문자는 응답 측이 한 일입니다[2].

| 글자 | 뜻 |
|---|---|
| `s` | ACK 없는 SYN |
| `h` | SYN+ACK |
| `a` | 페이로드 없는 ACK |
| `d` | 페이로드가 있는 패킷 |
| `f` | FIN 이 켜진 패킷 |
| `r` | RST 가 켜진 패킷 |
| `c` | 체크섬 오류 패킷(UDP 포함) |
| `g` | 내용 틈 |
| `t` | 페이로드 재전송 |
| `w` | 0 윈도 광고 |
| `i` | 모순된 패킷(FIN 과 RST 가 함께 켜짐 등) |
| `q` | 여러 플래그 패킷(SYN+FIN, SYN+RST) |
| `^` | Zeek 가 추정으로 방향을 뒤집음 |
| `x` | 한도 초과 등으로 분석을 일부만 함 |

`a`·`d`·`i`·`q` 는 방향마다 한 번만 적습니다. `f`·`h`·`r`·`s` 는 같은 종류의 앞 패킷과 순서 번호가 다르면 다시 적습니다. `c`·`g`·`t`·`w` 는 로그 단위로 적어서, 두 번 나오면 10번 이상, 세 번 나오면 100번 이상 일어났다는 뜻입니다[2].

예를 들어 `ShADadFf` 는 3단계 핸드셰이크(`S`·`h`·`A`) 뒤에 양쪽이 데이터를 보내고(`D`·`d`, 사이의 `a` 는 응답 측 ACK) 양쪽이 FIN 으로 닫은(`F`·`f`) 연결입니다[1]. DNS 질의·응답 한 번이 오간 UDP 흐름은 `Dd` 입니다[1].

## 증거로서 의미

**증명하는 것.** 센서가 본 패킷에서, 이 시각에 이 발신 측 IP·포트가 이 응답 측 IP·포트와 이 전송 프로토콜로 이만큼의 바이트·패킷을 주고받은 흐름이 있었다는 것을 증명합니다. `conn_state` 와 `history` 로 연결이 실제로 맺어졌는지, 거부됐는지, 누가 먼저 끊었는지를 알 수 있습니다. `service` 가 있으면 Zeek 분석기가 그 프로토콜임을 내용으로 확인했다는 뜻이라서 포트 번호만 보는 것보다 근거가 강합니다.

**증명하지 못하는 것.** 주고받은 내용은 conn.log 에 없습니다. 호스트 안의 어떤 프로세스나 사용자가 연결했는지도 알 수 없습니다. NAT 뒤에 있는 실제 호스트는 NAT 장비 로그가 있어야 알 수 있습니다([IP 주소·포트·NAT 해석](../../../01-foundations/records/ip-nat.md)). 센서가 한 방향만 보는 비대칭 경로에서는 정상 연결도 `S0`·`OTH`·`SHR` 로 보일 가능성이 있습니다([어디서 캡처하나](../../../01-foundations/capture/capture-points.md)). conn.log 에 줄이 없다고 해서 연결이 없었다는 뜻도 아닙니다. 센서가 못 본 구간, 아직 끝나지 않은 연결, 패킷 손실이 모두 빈자리로 남습니다.

보고서에는 "10.0.0.5 가 파일을 올렸다" 가 아니라 "2026-03-02 01:15:30 UTC 에 10.0.0.5:49152 가 203.0.113.5:443 으로 TCP 연결을 열어 약 42MB 를 보낸 기록이 conn.log 에 있다" 처럼 기록으로 확인되는 만큼만 씁니다(만든 예시).

## 시각 해석

`ts` 는 연결의 첫 패킷 시각이고, 에포크 초(1970-01-01 00:00:00 UTC 부터 센 초)라서 시간대가 없습니다[2]. pcap 을 읽어 만든 로그라면 pcap 레코드의 시각이고, 실시간 캡처라면 센서가 패킷을 받은 시각입니다. `date -d @1772414130.430166` 이나 `zeek-cut -u` 로 UTC 로 바꿔 읽습니다([Zeek 로그](index.md)).

연결이 끝난 시각은 `ts` 에 `duration` 을 더해 구하는데, 마지막 ACK 는 들어가지 않습니다. 한쪽 방향이 닫힌 뒤 새 페이로드가 없는 끝 패킷은 `duration` 에서 빠지기 때문입니다[2]. 위 예시 TCP 연결이라면 1772414130.430166 에 0.254115 를 더한 .684281 은 응답 측 FIN 시각이고, 발신 측의 마지막 ACK 는 그 뒤에 옵니다[6]. 이 끝 패킷도 `history` 와 패킷 수에는 들어갑니다([직접 분석해 보기](#직접-분석해-보기) 참고).

줄을 쓰는 시각은 연결 시각과 다릅니다. Zeek 는 연결이 정상으로 닫히면 5초(`tcp_close_delay`), RST 를 보면 5초(`tcp_reset_delay`), SYN 에 응답이 없으면 5초(`tcp_attempt_delay`) 뒤에 상태를 지우고[4], 오가는 패킷이 없으면 비활성 한도가 지난 뒤에 지웁니다. 기본 비활성 한도는 TCP 5분, UDP 1분, ICMP 1분, 그 밖의 IP 1분입니다[4]. FTP·SSH 분석기가 붙은 연결과 513·21·23·22/tcp 포트 연결은 1시간입니다[5]. 그래서 로그 파일 안의 줄 순서는 `ts` 순서가 아니고, 시간순으로 보려면 `ts` 로 정렬해야 합니다. 같은 UDP 4-튜플이라도 1분 넘게 조용하다가 다시 오가면 conn.log 줄이 둘 이상으로 나뉠 수 있습니다.

conn.log 의 시각을 다른 기록과 합치는 방법은 [네트워크 기록의 시각](../../../01-foundations/records/timestamps.md) 과 [네트워크 타임라인](../../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 함정과 한계

**발신 측은 클라이언트와 같은 말이 아닙니다.** `orig` 는 Zeek 가 먼저 보냈다고 본 쪽이고 `resp` 는 그 상대입니다. Zeek 가 추정 규칙으로 방향을 뒤집은 연결은 `history` 에 `^` 가 붙습니다[2]. 6.1.0 이전 버전은 브로드캐스트 주소를 발신 측으로 적기도 했습니다[7]. 누가 연결을 열었는지 주장하려면 `history` 가 `S` 로 시작하는지 봅니다.

**페이로드 바이트와 IP 바이트를 섞지 않습니다.** `orig_bytes` 는 TCP·UDP 페이로드만, `orig_ip_bytes` 는 IP 헤더와 TCP·UDP 헤더까지 센 값입니다[1][2]. TCP 의 `orig_bytes` 는 순서 번호의 차이로 계산해서, 큰 연결에서는 실제와 다를 수 있습니다[2]. 전송량을 주장할 때는 두 값을 함께 적고 어느 쪽인지 밝힙니다.

**`missed_bytes` 가 0이 아니면 패킷 손실이 있었습니다.** 손실이 생기면 보통 프로토콜 분석이 실패하므로, 같은 연결의 [dns.log](dns-log.md)·[http.log](http-log.md)·[files.log](files-log.md) 가 비거나 일부만 있을 수 있습니다[2]. 이때 `history` 에는 `G`·`g` 가 보입니다.

**체크섬 오프로딩 캡처는 `-C` 없이 돌리면 요약이 틀립니다.** Zeek 는 기본으로 체크섬이 틀린 패킷을 버리는데, 체크섬 오프로딩을 쓰는 호스트에서 뜬 캡처는 체크섬이 채워지지 않은 패킷이 많습니다[8][4]. `-C` 없이 돌린 결과에서 `S0`·`OTH` 가 유난히 많으면 이 문제를 먼저 의심합니다. `history` 의 `C`·`c` 도 같은 신호입니다.

**`local_orig`·`local_resp` 는 센서 설정 값입니다.** `Site::local_nets` 에 무엇을 넣었는지에 따라 달라지고, 비어 있으면 필드가 비어 있습니다[2]. 내부·외부 판단은 주소 대역으로 따로 확인합니다.

**`service` 와 포트 번호는 다를 수 있습니다.** 80번 포트인데 `service` 가 비어 있으면 HTTP 로 확인되지 않은 트래픽이고, 표준이 아닌 포트에서도 `service` 가 `http`·`ssl` 로 나올 수 있습니다. `speculative_service` 는 시그니처로만 짐작한 값이라 확인된 프로토콜로 쓰지 않습니다[3].

**끝나지 않은 연결은 conn.log 에 아직 없습니다.** 수집한 로그 기간이 끝날 때까지 이어진 긴 연결은 conn.log 에 없을 수 있는데, 같은 연결의 다른 로그에는 `uid` 가 남아 있을 수 있습니다([경고와 이상 기록](notice-weird-log.md)).

## 직접 분석해 보기

### 헥스로 한 번

conn.log 의 바이트 수는 패킷 헤더로 다시 계산할 수 있습니다. 아래는 위 예시 TCP 연결에서 발신 측이 HTTP 요청을 실어 보낸 패킷의 IP 헤더와 TCP 헤더 앞부분을 명세대로 만든 헥스입니다(만든 예시).

```text
0000  45 00 00 81 7d 12 40 00 40 06 c0 ac c0 a8 00 0a   IP 헤더 20바이트
0010  cb 00 71 05                                        ...
0014  b5 2a 00 50 dd e8 f3 47 b2 71 7e 69 80 18         TCP 헤더 앞 14바이트
```

IP 헤더의 3~4번째 바이트 `00 81` 이 total_length 129 이고, `45` 의 `5` 는 IP 헤더 길이 5×4 = 20바이트입니다. TCP 헤더의 13번째 바이트 `80` 의 위 4비트 `8` 은 TCP 헤더 길이 8×4 = 32바이트입니다. 따라서 페이로드는 129 − 20 − 32 = 77바이트이고, 이 연결의 발신 측 페이로드가 이 패킷 하나뿐이라서 `orig_bytes` 77 과 같습니다. 발신 측 패킷 6개의 total_length(SYN 60, ACK 52, 요청 129, ACK 52, FIN 52, 마지막 ACK 52)를 모두 더하면 397 로 `orig_ip_bytes` 와 같고, 패킷 수 6에도 마지막 ACK 가 들어 있습니다. `duration` 에서는 빠진 마지막 ACK 가 패킷 수와 IP 바이트에는 들어간다는 것을 이렇게 확인할 수 있습니다.

### 공개 도구로 한 번

같은 pcap 을 Zeek 와 tshark 로 읽어 값을 맞춰 봅니다. 체크섬 오프로딩 캡처일 수 있으면 `-C` 를 붙입니다[8].

```sh
zeek -C -r capture.pcap
zeek-cut -u ts uid id.orig_h id.orig_p id.resp_h id.resp_p proto service conn_state history orig_bytes resp_bytes < conn.log
tshark -V -r capture.pcap "tcp.port==46378 and ip.src==192.168.0.10"
tshark -x -r capture.pcap "http and ip.src==192.168.0.10"
```

`tshark -V` 로 패킷을 풀면 패킷마다 `Epoch Time`, IP 헤더의 `Total Length`, TCP 의 `[TCP Segment Len: 77]` 이 나옵니다. 첫 패킷의 `Epoch Time` 은 `ts` 와, 발신 측 패킷의 `Total Length` 합은 `orig_ip_bytes` 와 같아야 합니다[2]. `TCP Segment Len` 의 합은 `orig_bytes` 와 비교하는데, `orig_bytes` 는 순서 번호로 계산한 값이라서 재전송 패킷까지 더한 합과는 다를 수 있습니다[2]. `tshark -x` 는 위 헥스 절처럼 패킷 바이트를 보여 주므로 페이로드를 직접 셀 수 있습니다[1]. 여러 줄을 한꺼번에 볼 때는 jq 로 `conn_state` 별 개수를 셉니다.

```sh
jq -r '.conn_state' conn.log | sort | uniq -c | sort -rn
```

## 교차 검증

같은 `uid` 로 [dns.log](dns-log.md)·[http.log](http-log.md)·[ssl.log·x509.log](ssl-x509-log.md)·[files.log](files-log.md)·[notice.log·weird.log](notice-weird-log.md) 를 찾으면 이 연결에서 오간 응용 계층 내용을 볼 수 있습니다[1]. UDP 흐름 하나에 DNS 질의가 여럿이면 conn.log 한 줄에 dns.log 여러 줄이 이어집니다.

`uid` 는 Zeek 를 다시 돌리면 바뀌므로 다른 도구와 잇는 데 쓸 수 없습니다. Suricata 의 흐름 기록과는 Community ID 로 잇습니다. Community ID 는 주소·포트·프로토콜과 시드(기본 0)로 만든 SHA1 값을 base64 로 바꾸고 앞에 `1:` 을 붙인 문자열이라서 도구가 달라도 같은 흐름이면 같은 값이 나옵니다[10]. Zeek 는 `community-id-logging.zeek` 를 불러와야 이 필드를 쓰는데, 기본 local.zeek 에서는 이 줄이 주석 처리돼 있습니다[9][3]. Suricata 쪽 필드는 [Suricata EVE 로그](../../suricata/eve-json/index.md) 에서 다룹니다.

라우터·방화벽의 흐름 기록(NetFlow·IPFIX)과는 시각과 바이트 수를 비교합니다. 흐름 기록의 바이트가 어느 계층까지 센 값인지, 긴 연결을 어떻게 나눠 기록하는지는 [흐름 기록](../../../01-foundations/records/flow-records.md) 에서 확인하고, 그에 맞춰 `orig_bytes` 나 `orig_ip_bytes` 가운데 하나를 골라 비교합니다. 긴 연결과 일정한 간격의 반복 연결은 conn.log 로 찾을 수 있고, RITA 같은 도구가 Zeek 로그로 이 둘을 찾아 줍니다[11]([비컨 찾기](../../../03-techniques/analysis/beaconing.md)).

## 실습

Zeek 빠른 시작 문서의 예제 캡처 `quickstart.pcap` 을 `zeek -r quickstart.pcap LogAscii::use_json=T` 로 돌리면 conn.log 에 두 줄이 생깁니다[8].

1. 두 연결의 `conn_state` 와 `history` 를 읽고, 각 연결이 3단계 핸드셰이크로 열렸는지, 누가 먼저 FIN 을 보냈는지 답합니다.
2. 두 줄의 `uid` 로 http.log·weird.log 의 줄을 찾고, 각 로그의 `ts` 가 conn.log 의 `ts` 보다 얼마나 늦은지 계산합니다.
3. tshark 로 첫 연결의 마지막 패킷 시각을 구해 `ts` + `duration` 과 비교하고, 차이가 나는 패킷이 무엇인지 확인합니다.
4. 같은 pcap 을 한 번 더 돌려 `uid` 가 바뀌는지 확인합니다.

## 참고 문헌

1. Zeek 문서, "conn.log". https://github.com/zeek/zeek-docs/blob/master/logs/conn.rst
2. Zeek 소스, `scripts/base/protocols/conn/main.zeek`. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/conn/main.zeek
3. Zeek 스크립트 참조, "base/protocols/conn/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
4. Zeek 소스, `scripts/base/init-bare.zeek`. https://github.com/zeek/zeek/blob/master/scripts/base/init-bare.zeek
5. Zeek 스크립트 참조, "base/protocols/conn/inactivity.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/inactivity.zeek.rst
6. Zeek 문서, "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
7. Zeek NEWS. https://github.com/zeek/zeek/blob/master/NEWS
8. Zeek 문서, "Quick Start Guide". https://docs.zeek.org/en/master/quickstart.html
9. Zeek 소스, `scripts/site/local.zeek`. https://github.com/zeek/zeek/blob/master/scripts/site/local.zeek
10. Corelight, "Community ID Flow Hashing". https://github.com/corelight/community-id-spec/blob/master/README.md
11. Active Countermeasures, RITA README. https://github.com/activecm/rita/blob/main/README.md
