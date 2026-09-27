---
title: "경고 기록"
parent: "Suricata EVE 로그"
grand_parent: "아티팩트 · Suricata"
nav_order: 220
---

# 경고 기록 (alert)

Suricata 는 패킷이나 재조립한 스트림이 규칙 조건에 맞으면 EVE 로그에 `event_type` 이 `alert` 인 줄을 남깁니다. 이 줄에는 어떤 규칙(gid·sid·rev)이 어느 패킷에 걸렸는지가 들어가고, 설정에 따라 앱 계층 기록·흐름 계수·페이로드·패킷 원본이 붙습니다. 이 페이지는 alert 줄의 필드와 주소 방향, 시각을 읽는 법과 경고 한 줄로 주장할 수 있는 범위를 다루고, EVE 로그 전체에 공통인 머리 필드(`flow_id`·`community_id` 등)와 시각 형식은 [Suricata EVE 로그](index.md) 에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

alert 는 규칙 일치 기록입니다[2]. 규칙 동작 (action) 가운데 `alert` 는 경고를 남기고, `drop` 은 패킷을 버리면서 경고를 남기고, `reject`·`rejectsrc`·`rejectdst`·`rejectboth` 는 RST 나 ICMP 오류 패킷을 보냅니다. IPS 모드에서는 reject 계열이 drop 도 함께 합니다. `pass` 는 그 패킷의 나머지 검사를 멈춥니다[9]. 규칙 본문의 `noalert` 키워드가 있으면 규칙이 일치해도 경고를 남기지 않는데, 흐름 표시 (flowbits) 만 설정하는 규칙에 흔히 씁니다. 반대로 `alert` 키워드를 넣은 pass 규칙은 경고를 남깁니다[10]. 한 패킷이 여러 규칙에 걸리면 경고를 남기는 규칙마다 alert 줄을 하나씩 씁니다[5].

앱 계층 키워드(`http.uri` 같은)를 쓴 규칙의 경고에는 그 트랜잭션의 앱 계층 기록이 붙습니다. UDP 프로토콜은 패킷 하나에 메시지 하나가 들어 있다고 보고 똑같이 붙입니다[2]. 그 밖의 규칙은 `detect.guess-applayer-tx`(기본 no)를 켜면 엔진이 트랜잭션을 추정해 붙이는데, 처리 중인 트랜잭션이 여럿이면 아무것도 붙이지 않고, 추정해 붙인 경고에는 `tx_guessed: true` 가 들어갑니다[2][4]. 앱 계층 키워드가 없는 규칙에서 한 트랜잭션이 기록되는 횟수는 `detect.stream-tx-log-limit`(기본 4)까지입니다[4].

IPv4·IPv6 가 아닌 패킷에서 난 경고(디코더 이벤트 규칙 등)에는 흐름·앱 계층·페이로드 정보가 붙지 않고, alert 객체와 설정에 따라 `packet`·`verdict` 정도만 남습니다[5]. 규칙에 `tag` 키워드가 있고 `tagged-packets` 가 켜져 있으면 태그된 패킷이 `event_type: "packet"` 줄로 따로 기록됩니다[3][5].

## 설정과 버전별 차이

alert 줄에 무엇이 붙는지는 suricata.yaml 의 `outputs` → `eve-log` → `types` → `alert` 설정이 정합니다. 설정을 적지 않았을 때의 기본값은 코드 기준이고, 배포하는 yaml 에는 `tagged-packets: yes` 만 켜져 있고 나머지는 주석 처리돼 있습니다[3][5].

| 설정 | 기본 | 켜면 붙는 필드 |
|---|---|---|
| `metadata.app-layer` | 켜짐 | `http`·`dns`·`tls`·`smtp`+`email`·`nfs`+`rpc`·`smb`·`dcerpc` 등 앱 계층 객체 |
| `metadata.flow` | 켜짐 | `flow` 객체 (경고 시점의 흐름 계수) |
| `metadata.rule.metadata` | 켜짐 | `alert.metadata`, 루트의 `files` 배열 |
| `metadata.rule.raw` | 꺼짐 | `alert.rule` (규칙 원문) |
| `metadata.rule.reference` | 꺼짐 | `alert.references` |
| `metadata: no` | — | 위 세 기본값(앱 계층·흐름·규칙 메타데이터)을 모두 끔 |
| `payload` / `payload-printable` / `payload-length` | 꺼짐 | `payload`(Base64) / `payload_printable` / `payload_length`, 그리고 `stream` |
| `payload-buffer-size` | 4kb | 스트림 페이로드를 담는 최대 크기 |
| `packet` | 꺼짐 | `packet`(Base64), `packet_info` |
| `http-body` / `http-body-printable` | 꺼짐 | `http` 안의 `http_request_body`·`http_response_body`(Base64)와 `_printable` 판 |
| `websocket-payload` / `websocket-payload-printable` | 꺼짐 | 웹소켓 페이로드 |
| `tagged-packets` | 코드 꺼짐, 배포 yaml 켜짐 | `event_type: "packet"` 줄 |
| `verdict` | 꺼짐 | `verdict` 객체 |

HTTP 본문·웹소켓 페이로드 옵션은 `metadata.app-layer` 가 꺼져 있으면 경고 메시지를 남기고 무시됩니다[5]. 옛 설정 이름 `http`·`tls`·`ssh`·`smtp`·`dnp3`·`app-layer`·`flow` 를 alert 바로 아래에 쓰면 효과가 없다는 경고만 나옵니다[5]. 그래서 센서의 yaml 을 볼 때는 들여쓰기 위치까지 확인해야 합니다.

`alert.engine`(`fw`·`td`)과 `firewall` 객체는 방화벽 모드에서만 나옵니다[1][5]. 규칙의 `requires` 키워드는 Suricata 7.0.3 과 8.0.0 에서 들어왔고, 조건에 맞지 않는 규칙은 오류 없이 건너뜁니다[8]. 옛 개별 로거(alert-json-log)는 [Suricata EVE 로그](index.md) 에서 다룹니다.

## 구조

### 한 줄의 모양

다음은 alert 한 줄의 예입니다(만든 예시, 보기 좋게 줄을 나눔).

```json
{"timestamp":"2026-03-02T10:15:30.123456+0900","flow_id":1234567890123456,"pcap_cnt":42,
 "event_type":"alert","src_ip":"192.168.0.10","src_port":49152,"dest_ip":"203.0.113.5",
 "dest_port":80,"proto":"TCP","ip_v":4,"pkt_src":"wire/pcap",
 "alert":{"action":"allowed","gid":1,"signature_id":1000001,"rev":2,
  "signature":"LOCAL example GET to external host","category":"Potentially Bad Traffic","severity":2},
 "app_proto":"http","direction":"to_server",
 "flow":{"pkts_toserver":3,"pkts_toclient":1,"bytes_toserver":252,"bytes_toclient":66,
  "start":"2026-03-02T10:15:30.101200+0900","src_ip":"192.168.0.10","dest_ip":"203.0.113.5",
  "src_port":49152,"dest_port":80},
 "payload":"R0VUIC8gSFRUUC8xLjENCg==","stream":0,
 "packet":"AABeAFMCAABeAFMBCABFAAA4EjRAAEAGK9TAqAAKywBxBcAAAFAAAAPoAAAH0FAY+vAadAAAR0VUIC8gSFRUUC8xLjENCg==",
 "packet_info":{"linktype":1,"linktype_name":"EN10MB"}}
```

### alert 객체

alert 객체의 필드와 각 필드가 오는 규칙 키워드는 다음과 같습니다[1][5][8].

| 필드 | 규칙 쪽 원천 | 뜻 |
|---|---|---|
| `action` | 규칙 동작 + 엔진 모드 | `allowed` 또는 `blocked` 둘 중 하나 |
| `engine` | — | 방화벽 모드에서만. 방화벽 규칙이면 `fw`, 위협 탐지 규칙이면 `td` |
| `gid` | `gid` | 규칙 그룹 번호. 기본 1이고 값을 바꿔도 기록에만 영향 |
| `signature_id` | `sid` | 규칙 번호. 0보다 큰 수 |
| `rev` | `rev` | 규칙 개정 번호. 규칙을 고칠 때마다 올림 |
| `signature` | `msg` | 규칙 설명. 없으면 빈 문자열 |
| `category` | `classtype` | classification.config 의 긴 이름. classtype 이 없으면 빈 문자열 |
| `severity` | 우선순위 | classtype 의 우선순위 또는 `priority` 키워드 값. 1~255, 1이 가장 높음 |
| `tenant_id` | — | 멀티테넌트 설정일 때 |
| `source`·`target` | `target` | 규칙에 `target:src_ip` 나 `target:dest_ip` 가 있을 때 공격한 쪽과 당한 쪽의 `ip`·`port` |
| `references` | `reference` | `metadata.rule.reference` 를 켰을 때 |
| `metadata` | `metadata` | 키마다 값 배열. 예 `"signature_severity":["Major"]` |
| `context` | — | 경고에 덧붙은 추가 JSON 정보 (있을 때만) |
| `rule` | 규칙 원문 | `metadata.rule.raw` 를 켰을 때 |
| `xff` | X-Forwarded-For 헤더 | xff 를 `extra-data` 모드로 켰을 때 |

classtype 은 classification.config 의 `config classification: web-application-attack,Web Application Attack,1` 같은 줄에서 짧은 이름·긴 이름·우선순위를 가져옵니다[8]. Emerging Threats 규칙의 metadata 에는 `affected_product`·`attack_target`·`created_at`·`deployment`·`former_category`·`malware_family`·`signature_severity`·`updated_at` 같은 키가 들어가고, 값은 모두 배열입니다[1].

### alert 객체 밖에 붙는 필드

`tx_id` 는 경고가 트랜잭션에 묶였을 때 루트에 들어가고, 같은 `flow_id` 의 http·dns·fileinfo 줄과 잇는 데 씁니다[5]. `direction` 은 흐름이 있을 때 경고를 일으킨 패킷의 방향(`to_server`·`to_client`)입니다[5]. `files` 배열에는 그 트랜잭션의 파일 정보가 fileinfo 와 같은 필드로 들어갑니다([파일 추출](filestore.md) 참고)[1][5].

`flow` 객체에는 경고를 쓴 순간까지의 `pkts_toserver`·`pkts_toclient`·`bytes_toserver`·`bytes_toclient`·`start` 와, 흐름을 연 쪽 기준의 `src_ip`·`dest_ip`·`src_port`·`dest_port` 가 들어갑니다[1][5].

페이로드 옵션을 켜면 `payload`·`payload_printable`·`payload_length` 와 함께 `stream` 이 붙습니다. TCP 에서 스트림이나 앱 계층 상태로 일치했으면 `stream` 이 1이고, 이때 `payload` 는 걸린 패킷 하나가 아니라 그 방향으로 재조립한 스트림 데이터를 `payload-buffer-size` 만큼 담습니다[5]. 재조립 데이터 중간에 빈 곳이 있으면 그 자리에 `[120 bytes missing]` 같은 문자열을 끼워 넣고 Base64 로 바꿉니다[5]. 스트림 데이터가 없으면 패킷 페이로드로 대신합니다[5].

`packet` 은 링크 계층 헤더부터 담은 패킷 원본(스트림 세그먼트는 제외)이고, `packet_info` 에는 링크 유형 번호 `linktype` 과 이름 `linktype_name` 이 들어갑니다[2][6]. 터널 안의 패킷이면 바깥 패킷의 5-tuple·`depth`·`pcap_cnt`·`pkt_src` 가 `tunnel` 객체로 붙습니다[5]. pcap-log 를 `multi` 모드로 켰으면 그 패킷이 저장된 pcap 파일 경로가 `capture_file` 에 들어갑니다[1][5].

### action 과 verdict

`action` 은 기본이 `allowed` 입니다. 규칙이 reject 계열이면 `blocked`, drop 이면서 IPS 모드이면 `blocked` 가 됩니다. 비율 필터 (rate_filter) 가 동작을 바꾼 경고는 패킷이 실제로 버려지거나 거부됐는지로 정합니다[5]. 한 패킷이 여러 규칙에 걸릴 수 있어서 `action` 이 그 패킷의 최종 처리 결과는 아닙니다[1].

패킷의 최종 처리 결과는 `verdict` 객체에 있습니다. `verdict.action` 은 `alert`·`pass`·`drop`(IPS 모드에서만) 중 하나이고, 코드에는 `accept` 도 있습니다. reject 규칙이면 `reject_target`(`to_server`·`to_client`·`both`)과 보낸 패킷 종류 배열 `reject`(`tcp-reset` 또는 `icmp-prohib`)가 붙습니다[1][5]. IPS 모드에서는 `action: allowed` 인 경고의 verdict 가 `drop` 일 수 있는데, 같은 패킷이 다른 경고나 흐름 드롭 때문에 버려진 경우입니다[1].

### 주소 방향

alert 줄의 `src_ip`·`dest_ip` 는 규칙에 걸린 그 패킷의 출발지와 도착지입니다[5][6]. 서버가 보낸 응답에서 규칙이 걸리면 서버가 `src_ip` 에 들어갑니다. 이런 경고는 머리의 `src_ip` 가 외부 서버, `dest_ip` 가 내부 PC 이고 `direction` 은 `to_client` 이지만, `flow.src_ip` 는 연결을 연 내부 PC 입니다[1][5]. 누가 연결을 열었는지는 `flow` 객체나 같은 `flow_id` 의 flow 줄([프로토콜 기록](protocol-events.md))로 판단합니다. 규칙에 `target` 이 있으면 `alert.source`·`alert.target` 이 공격 방향을 따로 적어 줍니다[1][8].

xff 를 `overwrite` 모드로 켠 센서는 HTTP 경고의 출발지나 도착지 IP 를 X-Forwarded-For 헤더 값으로 바꿔 씁니다[5]. 이런 센서의 IP 필드는 패킷 헤더의 IP 가 아닐 수 있어서, 설정을 먼저 확인합니다. 프록시·NAT 뒤 주소 해석은 [IP 주소·포트·NAT 해석](../../../01-foundations/records/ip-nat.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 센서가 본 트래픽에서, 그 시각에 그 5-tuple 의 패킷(또는 재조립 스트림)이 그 gid·sid·rev 규칙 조건에 맞았다는 것을 증명합니다. `action: allowed` 이면 그 규칙 때문에 패킷이 막히지는 않았다는 뜻이고, `verdict` 가 있으면 패킷의 최종 처리 결과까지 알 수 있습니다. `payload`·`packet` 이 켜져 있으면 규칙이 본 바이트를 경고 줄만으로 다시 확인할 수 있습니다.

**증명하지 못하는 것.** 공격이 성공했는지, 트래픽이 실제로 악성인지는 알 수 없습니다. 규칙은 오탐을 낼 수 있고, 규칙이 없거나 꺼진 위협은 경고가 없습니다. 같은 sid 라도 rev 가 다르면 조건이 다르므로, 당시 센서에 올라가 있던 규칙 파일을 rev 까지 확보해야 경고를 해석할 수 있습니다[8]. 경고가 없다는 것도 트래픽이 없었다는 뜻이 아닙니다. 센서가 못 본 트래픽, 드롭된 패킷, 꺼진 규칙은 기록이 남지 않습니다([Suricata EVE 로그](index.md) 의 stats 참고).

경고 수는 발생 횟수가 아닙니다. 규칙의 `threshold`(type `threshold`·`limit`·`both`·`backoff`, track `by_src`·`by_dst`·`by_rule`·`by_both`·`by_flow`)와 `detection_filter` 가 경고를 줄이거나 일정 횟수 뒤부터만 남깁니다[11]. 예를 들어 `threshold: type limit, track by_src, seconds 180, count 1` 이면 출발지 호스트마다 3분에 경고 1건만 남습니다[11]. flowbits 같은 동작과 drop(IPS 모드)·reject 동작은 한도와 상관없이 매 패킷에 적용됩니다[11]. threshold.conf 의 `suppress gen_id 1, sig_id 2001219, track by_src, ip 192.168.50.10` 같은 줄은 특정 주소의 경고를 아예 남기지 않습니다[14]. 보고서에는 "이 규칙이 이 시간대에 N건 기록됐다" 까지만 쓰고, 실제 횟수는 flow 줄이나 pcap 으로 셉니다.

## 시각 해석

`timestamp` 는 규칙에 걸린 패킷의 시각(`p->ts`)이고, 경고를 파일에 쓴 시각이 아닙니다[6]. 실시간 캡처에서는 패킷을 받은 시각이고, `-r` 로 pcap 을 읽을 때는 pcap 레코드의 시각이라서, 나중에 다시 처리해도 원래 패킷 시각이 찍힙니다. 형식은 센서 현지 시간대로 바꾼 값에 `+0900` 같은 오프셋을 붙인 것이고[7], UTC 로 바꾸는 법과 Windows 센서의 오프셋 문제는 [Suricata EVE 로그](index.md) 와 [네트워크 기록의 시각](../../../01-foundations/records/timestamps.md) 에서 다룹니다. pcap 을 읽는 모드에서는 `pcap_cnt` 가 그 패킷의 번호라서 Wireshark 에서 `frame.number == 42` 로 바로 찾을 수 있습니다[1][16].

`stream: 1` 인 경고는 시각을 조심해서 읽습니다. IDS 모드는 상대가 ACK 한 데이터를 기준으로 TCP 를 재조립하므로[4], 경고의 기준 패킷이 데이터를 실어 나른 패킷보다 뒤의 패킷일 가능성이 있습니다. 이때는 pcap 에서 `pcap_cnt` 앞뒤 패킷을 함께 봅니다.

`flow.start` 는 흐름의 첫 패킷 시각이고, `flow` 의 패킷·바이트 수는 경고를 쓴 순간의 값입니다[1][5]. 흐름이 끝났을 때의 전송량과 끝 시각은 같은 `flow_id` 의 flow 줄에 있습니다([프로토콜 기록](protocol-events.md)).

fast.log 줄의 시각 `07/12/2022-21:59:26.713297` 에는 시간대 오프셋이 없습니다[8]. EVE 와 fast.log 를 함께 볼 때는 센서 시간대를 따로 확인합니다.

## 함정과 한계

- `severity` 는 숫자가 작을수록 심각합니다(1이 가장 높음)[8]. SIEM 이 `event.severity_label` 같은 등급 이름으로 바꿔 보여 줄 수 있으니 원래 숫자를 함께 확인합니다[13].
- `tx_guessed: true` 인 경고에 붙은 앱 계층 기록은 엉뚱한 트랜잭션일 수 있습니다[2][4].
- `payload_printable` 은 출력할 수 없는 바이트를 바꿔 쓴 손실 있는 변환입니다. 바이트를 확인할 때는 Base64 인 `payload` 를 풉니다[2].
- 같은 규칙 묶음이라도 `requires` 조건 때문에 센서 버전마다 올라간 규칙이 다를 수 있습니다[8]. HOME_NET 이 실제 내부 대역과 맞지 않으면 `$HOME_NET` 을 쓰는 규칙이 걸리지 않습니다. Security Onion 은 HOME_NET 기본값이 RFC 1918 사설 대역이고 EXTERNAL_NET 기본값이 `any` 입니다[15].
- SIEM 으로 옮긴 뒤에는 필드 이름이 바뀝니다. Security Onion 은 Suricata 경고를 `event.module:"suricata"`·`event.dataset:"alert"` 로 찾고, `source.ip`·`source.port`·`destination.ip`·`destination.port`·`network.transport`·`rule.gid`·`rule.name`·`rule.rule`·`rule.rev`·`rule.severity`·`rule.uuid`·`rule.version` 필드로 보여 줍니다[13]. 보고서의 근거는 원래 eve.json 줄로 다시 확인합니다.
- `metadata: no` 로 설정한 센서는 `flow`·앱 계층 객체가 없고, `metadata` 아래 `flow: false` 이면 `flow` 객체만 빠집니다. 필드가 없는 것이 트래픽 특성인지 설정 때문인지 yaml 로 먼저 확인합니다[5].

## 직접 분석해 보기

### 헥스로 한 번: packet 필드 풀기

위 예시 줄의 `packet` 값을 풀면 경고를 일으킨 패킷을 링크 계층부터 볼 수 있습니다. 아래 바이트는 이더넷·IPv4·TCP 명세대로 만든 예시입니다(만든 예시).

```text
$ echo 'AABeAFMCAABeAFMBCABFAAA4EjRAAEAGK9TAqAAKywBxBcAAAFAAAAPoAAAH0FAY+vAadAAAR0VUIC8gSFRUUC8xLjENCg==' | base64 -d | xxd
00000000: 0000 5e00 5302 0000 5e00 5301 0800 4500  ..^.S...^.S...E.
00000010: 0038 1234 4000 4006 2bd4 c0a8 000a cb00  .8.4@.@.+.......
00000020: 7105 c000 0050 0000 03e8 0000 07d0 5018  q....P........P.
00000030: faf0 1a74 0000 4745 5420 2f20 4854 5450  ...t..GET / HTTP
00000040: 2f31 2e31 0d0a                           /1.1..
```

`packet_info.linktype` 이 1이면 이더넷 헤더부터 시작합니다(링크 유형 번호는 [pcap 형식](../../../01-foundations/capture/pcap.md) 참고). 0x0C 의 `0800` 이 IPv4 이고, IP 헤더는 0x0E 의 `45` 에서 시작합니다. 0x1A 의 `c0a8000a` 가 출발지 192.168.0.10, 0x1E 의 `cb007105` 가 도착지 203.0.113.5 로, 경고 머리의 `src_ip`·`dest_ip` 와 같습니다. TCP 헤더는 0x22 에서 시작해 출발지 포트 `c000`(49152), 도착지 포트 `0050`(80)이 나오고, 0x2F 의 플래그 `18` 은 PSH·ACK 입니다. 0x36 부터가 페이로드 `GET / HTTP/1.1\r\n` 이고, 이 16바이트를 Base64 로 바꾼 값이 `payload` 필드의 `R0VUIC8gSFRUUC8xLjENCg==` 입니다. `stream` 이 0이라서 `payload` 와 패킷 페이로드가 같습니다. `stream` 이 1이면 `payload` 가 재조립 스트림이라 이 둘이 다를 수 있습니다.

### 공개 도구로 한 번: jq

경고만 골라 시각·주소·규칙을 한 줄씩 봅니다[12].

```bash
jq -c 'select(.event_type=="alert")
       | [.timestamp, .src_ip, .src_port, .dest_ip, .dest_port,
          .alert.action, "\(.alert.gid):\(.alert.signature_id):\(.alert.rev)", .alert.signature]' eve.json
```

규칙(gid:sid:rev)별로 경고 수를 셉니다. rev 까지 묶어 세야 개정 전후 규칙이 섞이지 않습니다.

```bash
jq -r 'select(.event_type=="alert")
       | "\(.alert.gid):\(.alert.signature_id):\(.alert.rev)\t\(.alert.signature)"' eve.json \
  | sort | uniq -c | sort -rn
```

경고 하나의 `flow_id` 로 같은 흐름의 http·fileinfo·flow 줄을 모두 모읍니다[1].

```bash
jq -c 'select(.flow_id==1234567890123456)' eve.json
```

페이로드를 바이트로 풉니다[12].

```bash
jq -r 'select(.event_type=="alert") | .payload' eve.json | base64 --decode | xxd | head
```

## 교차 검증

| 함께 볼 기록 | 확인할 것 | 페이지 |
|---|---|---|
| 같은 `flow_id` 의 flow 줄 | 누가 연결을 열었는지, 흐름 끝의 전송량·끝 시각 | [프로토콜 기록](protocol-events.md) |
| 같은 `flow_id`·`tx_id` 의 http·dns·tls 줄 | 경고에 붙은 앱 계층 기록과 같은 트랜잭션인지 | [프로토콜 기록](protocol-events.md) |
| 같은 흐름의 fileinfo 줄 | 오간 파일의 해시·상태 | [파일 추출](filestore.md) |
| 원본 pcap 또는 `capture_file` | `pcap_cnt` 패킷과 그 앞뒤 패킷 | [Wireshark·tshark로 읽기](../../../03-techniques/analysis/wireshark.md) |
| Zeek conn.log | `community_id` 로 같은 연결 찾기 | [Zeek 로그](../../zeek/zeek-logs/index.md) |
| 당시 규칙 파일·threshold.conf | sid·rev 의 실제 조건, 경고를 줄인 설정 | [탐지 규칙 활용](../../../03-techniques/analysis/detection-rules.md) |

여러 기록을 시간순으로 합치는 절차는 [네트워크 타임라인](../../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 실습

Wireshark 예제 캡처처럼 공개된 pcap 의 사본에 Suricata 를 돌려 봅니다. `-r` 은 pcap 파일을 읽고, `-l` 은 로그 폴더를, `-k none` 은 체크섬 검사 끄기를 정합니다[17]. `pcap-file.delete-when-done` 이 `true`·`"non-alerts"` 이거나 `--pcap-file-delete` 를 주면 처리한 pcap 을 지우므로 원본 증거물에는 돌리지 않습니다[17][18].

```bash
suricata -c /etc/suricata/suricata.yaml -r sample-copy.pcap -l ./out -k none
```

1. `./out/eve.json` 에서 규칙(gid:sid:rev)별 경고 수를 세고, 가장 많은 규칙의 `severity` 와 `category` 를 확인합니다.
2. `direction` 이 `to_client` 인 경고를 하나 골라 `src_ip` 와 `flow.src_ip` 가 다른지 확인하고, 누가 연결을 열었는지 설명합니다.
3. 그 경고의 `pcap_cnt` 로 Wireshark 에서 `frame.number == N` 을 찾아, 규칙에 걸린 바이트가 그 패킷에 있는지 확인합니다.
4. 같은 `flow_id` 의 flow 줄을 찾아 `flow` 객체의 `bytes_toclient` 와 흐름 끝의 값을 비교합니다.
5. yaml 의 alert 설정에 `payload: yes`·`verdict: yes` 를 켜고 다시 돌린 뒤, 새로 생긴 필드와 `stream` 값이 1인 경고의 `payload` 를 풀어 봅니다.

## 참고 문헌

1. OISF, Suricata User Guide — Eve JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
2. OISF, Suricata User Guide — Eve JSON Output. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
3. OISF, Suricata User Guide — eve-log.yaml (설정 예시). https://github.com/OISF/suricata/blob/main/doc/userguide/partials/eve-log.yaml
4. OISF, Suricata User Guide — suricata.yaml. https://github.com/OISF/suricata/blob/main/doc/userguide/configuration/suricata-yaml.rst
5. OISF, Suricata 소스 src/output-json-alert.c. https://github.com/OISF/suricata/blob/main/src/output-json-alert.c
6. OISF, Suricata 소스 src/output-json.c. https://github.com/OISF/suricata/blob/main/src/output-json.c
7. OISF, Suricata 소스 src/util-time.c. https://github.com/OISF/suricata/blob/main/src/util-time.c
8. OISF, Suricata User Guide — Rules: Meta Keywords. https://github.com/OISF/suricata/blob/main/doc/userguide/rules/meta.rst
9. OISF, Suricata User Guide — Rules: Introduction (Action). https://github.com/OISF/suricata/blob/main/doc/userguide/rules/intro.rst
10. OISF, Suricata User Guide — Rules: Alert Keywords (noalert·alert). https://github.com/OISF/suricata/blob/main/doc/userguide/rules/noalert.rst
11. OISF, Suricata User Guide — Rules: Thresholding Keywords. https://github.com/OISF/suricata/blob/main/doc/userguide/rules/thresholding.rst
12. OISF, Suricata User Guide — Eve JSON 'jq' Examples. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-examplesjq.rst
13. Security Onion Documentation 2.4, Alert Data Fields; Alerts. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/alert-data-fields.rst , https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/alerts.rst
14. Security Onion Documentation 2.4, NIDS. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/nids.rst
15. Security Onion Documentation 2.4, Suricata. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/suricata.rst
16. Wireshark, Display Filter Reference: Frame. https://www.wireshark.org/docs/dfref/f/frame.html
17. OISF, Suricata User Guide — Command Line Options. https://github.com/OISF/suricata/blob/main/doc/userguide/partials/options.rst
18. OISF, Suricata User Guide — PCAP File Reading. https://github.com/OISF/suricata/blob/main/doc/userguide/capture-hardware/pcap-file.rst
