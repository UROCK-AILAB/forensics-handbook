---
title: "Suricata EVE 로그"
parent: "아티팩트 · Suricata"
nav_order: 210
has_children: true
has_toc: false
---

# Suricata EVE 로그 (EVE JSON)

Suricata 는 규칙에 걸린 경고뿐 아니라 DNS·HTTP·TLS 같은 프로토콜 기록, 흐름 기록, 파일 정보, 이상 징후, 통계를 모두 EVE 라는 JSON 출력으로 내보냅니다. 한 줄이 JSON 객체 하나이고, 모든 기록이 같은 공통 필드(시각·`flow_id`·5-튜플·`event_type`)를 앞에 달고 있어서 `flow_id` 하나로 한 세션의 경고와 프로토콜 기록을 묶어 볼 수 있습니다. 대신 센서가 본 트래픽만, 켜 둔 기록 종류만 남고, 시각에는 센서의 시간대 오프셋이 붙습니다.

## 왜 중요한가

EVE 는 경고가 없어도 모든 세션에 대해 프로토콜 기록과 흐름 기록을 남기도록 설정할 수 있어서, 탐지 규칙이 놓친 통신도 나중에 찾아볼 수 있습니다[3]. Security Onion 같은 보안 관제 배포판은 Suricata 경고를 화면에 모아 보여 주고, 메타데이터 엔진을 Zeek 에서 Suricata 로 바꾸면 연결·DHCP·DNS·파일·FTP·HTTP·SSL 메타데이터도 Suricata 로 기록합니다[13].

EVE 로 증명할 수 있는 것은 "센서가 본 트래픽에서, 이 시각에, 이 5-튜플의 흐름·트랜잭션·규칙 일치가 있었다" 는 데까지입니다. 탭·미러 포트 위치 때문에 센서에 닿지 않은 트래픽, 커널이나 센서가 처리하지 못하고 버린 패킷, 암호화된 내용, 설정에서 꺼 둔 기록 종류는 남지 않습니다. 그래서 기록이 없다고 해서 그 통신이 없었다고 쓰면 안 되고, 같은 기간의 `stats` 기록과 센서의 `suricata.yaml` 설정을 함께 확인해야 합니다[2][8]. 센서 위치에 따라 무엇이 보이는지는 [어디서 캡처하나](../../../01-foundations/capture/capture-points.md)에 있습니다.

## 한눈에 보기

EVE 의 기록 종류는 `event_type` 필드 값으로 구분합니다. 조사에서 자주 쓰는 종류는 다음과 같습니다.

| 기록 (`event_type`) | 알려 주는 것 | 기본 설정 | 자세히 |
|---|---|---|---|
| `alert` | 어떤 규칙(`signature_id`)이 어느 흐름에서 일치했는지, 관련 HTTP·DNS 같은 앱 계층 정보 | 켜짐 | [경고 기록](alert.md) |
| `dns`·`http`·`tls` 등 프로토콜 기록 | 질의 이름·응답, URL·호스트·User-Agent, SNI·인증서 | 켜짐 | [프로토콜 기록](protocol-events.md) |
| `flow` | 양방향 흐름 하나의 시작·끝 시각, 방향별 패킷 수·바이트 수, 끝난 이유 | 켜짐 | [프로토콜 기록](protocol-events.md) |
| `netflow` | 한 방향씩 나눈 흐름 기록(`flow` 의 두 배 개수) | 꺼짐 | [프로토콜 기록](protocol-events.md) |
| `fileinfo` | HTTP·SMB·SMTP 등으로 오간 파일의 이름·크기·해시·저장 여부 | 켜짐 | [파일 추출](filestore.md) |
| `anomaly` | 잘린 패킷, 잘못된 길이 값, TCP 연결 상태 이상 같은 디코딩·스트림·앱 계층 이상 | 설정 파일에서 켜짐 | 아래 설명 |
| `stats` | 캡처·디코딩·스트림 처리 카운터(버린 패킷 수 등) | 켜짐 | 아래 설명 |
| `drop` | 엔진이 버린 패킷 | 꺼짐 | [경고 기록](alert.md) |

기본 설정은 Suricata 가 함께 배포하는 `eve-log` 설정 예시 기준입니다[2]. 이 밖에 SMTP·FTP·SMB·RDP·SSH·Kerberos·DHCP·QUIC·HTTP/2 같은 프로토콜 기록도 기본으로 켜져 있고, `arp`·`ntp`·`pgsql`·`frame` 은 꺼져 있습니다[2]. 설치본마다 설정이 달라서, 실제 센서의 `suricata.yaml` 에서 `outputs:` 아래 `eve-log` 의 `types:` 목록을 먼저 확인합니다. `anomaly` 는 문서 본문에는 "기본으로 꺼져 있다" 고 되어 있고 배포 설정 예시에는 `enabled: yes` 로 켜져 있어서, 두 설명이 다릅니다[1][2]. 이 경우에도 센서의 설정 파일이 기준입니다.

### 파일 위치와 나뉨

기본 출력 방식은 `filetype: regular` 이고, 기본 파일 이름은 `eve.json` 입니다[2]. 파일은 기본 로그 폴더 `/var/log/suricata` 아래에 생깁니다[4]. 명령행 `-l 폴더` 를 주면 설정 파일의 `default-log-dir` 대신 그 폴더를 씁니다[5]. 출력 방식이 `syslog`·`unix_dgram`·`unix_stream`·`redis` 이면 센서 디스크에는 `eve.json` 이 없고, 받는 쪽(syslog 서버, SIEM)에 기록이 있습니다[1]. `prefix` 설정으로 줄마다 앞에 `@cee: ` 같은 접두어를 붙일 수도 있습니다[1].

한 센서의 EVE 가 파일 여러 개로 나뉘는 경우가 셋 있습니다. `eve-log` 설정을 여러 개 두면 예를 들어 경고와 drop 은 `eve-ips.json` 에, HTTP·DNS·TLS 는 `eve-nsm.json` 에 따로 쓸 수 있습니다[1]. `threaded: on` 이면 출력 스레드마다 `eve.7.json` 처럼 이름에 번호를 붙인 파일을 따로 쓰므로, 모든 파일을 합쳐야 전체 기록이 됩니다[1]. 파일 이름에 `eve-%s.json` 처럼 strftime 치환자를 쓰고 `rotate-interval`(`minute`·`hour`·`day` 또는 `30s`·`30m` 같은 값)을 주면 시간마다 새 파일을 만듭니다[1]. 오래된 파일을 지우는 일은 Suricata 가 하지 않고 외부 도구가 합니다[7].

logrotate 로 파일을 돌리는 센서에서 Suricata 는 SIGHUP 을 받으면 로그 파일을 닫고 추가(append) 모드로 다시 엽니다. 그 사이 이름이 바뀌었으면 새 파일을 만듭니다[7]. logrotate 설정에 `rotate 3` 처럼 보관 개수가 있으면 그보다 오래된 파일은 지워지므로, 조사 기간의 파일이 남아 있는지 먼저 확인합니다[7]. 수집 방법은 [로그 수집과 보존](../../../03-techniques/acquisition/log-collection.md)에 있습니다.

`buffer-size` 가 0(기본)이면 기록을 바로 파일에 씁니다. 0 보다 크면 그 크기만큼 메모리에 모았다가 쓰기 때문에, 센서가 비정상 종료하면 마지막 기록 일부가 파일에 남지 않을 수 있습니다[1].

### 공통 필드

모든 기록은 다음 모양으로 시작합니다[3].

```json
{"timestamp":"2026-03-02T14:05:11.482913+0900","flow_id":1127453392018734,"in_iface":"eth1","event_type":"flow","src_ip":"10.0.5.23","src_port":53144,"dest_ip":"203.0.113.80","dest_port":443,"proto":"TCP","app_proto":"tls","flow":{"pkts_toserver":12,"pkts_toclient":10,"bytes_toserver":1834,"bytes_toclient":6120,"start":"2026-03-02T14:04:10.117402+0900","end":"2026-03-02T14:04:12.902155+0900","age":2,"state":"closed","reason":"timeout","alerted":false}}
```

(만든 예시)

공통 필드와 각 필드가 남는 조건은 다음과 같습니다[1][2][3][10].

| 필드 | 뜻 | 남는 조건 |
|---|---|---|
| `timestamp` | 기록 시각. 아래 "시각" 절 참고 | 항상 |
| `flow_id` | 같은 흐름에 속한 기록을 묶는 정수 | 흐름이 있을 때 |
| `parent_id` | 부모 흐름의 `flow_id` | 부모 흐름이 있을 때 |
| `event_type` | 기록 종류 | 항상 |
| `src_ip`·`src_port`·`dest_ip`·`dest_port`·`proto` | 5-튜플. `proto` 는 `"TCP"` 같은 문자열 | 해당될 때 |
| `in_iface` | 캡처한 인터페이스 이름 | 실시간 캡처 |
| `pcap_cnt` | pcap 파일 안에서 몇 번째 패킷인지 | pcap 을 읽을 때, 실제 패킷에서 나온 기록만 |
| `pcap_filename` | 읽은 pcap 파일 경로 | pcap 을 읽을 때, `pcap-file: true` 로 켰을 때 |
| `pkt_src` | 패킷 출처. 예 `"wire/pcap"`, `"stream (flow timeout)"` | 해당될 때 |
| `app_proto` | 알아낸 앱 계층 프로토콜 | 알아냈을 때 |
| `tx_id` | 앱 계층 트랜잭션 번호 | 트랜잭션 기록 |
| `community_id` | 도구끼리 같은 흐름을 잇는 해시 | `community-id: true` 일 때 |
| `host` | 센서 이름 | `sensor-name` 을 설정했을 때 |
| `vlan` | VLAN ID 배열 | VLAN 태그가 있을 때 |
| `ether` | 출발·목적 MAC 주소 | `ethernet: yes` 일 때 |

`pcap_cnt` 는 pcap 파일 안의 패킷 번호라서 Wireshark 에서 `frame.number == 130` 같은 필터로 그 패킷을 찾을 수 있습니다[3][16]. 흐름 타임아웃처럼 Suricata 가 안에서 만든 패킷에서 나온 기록에는 `pcap_cnt` 가 없습니다[3].

JSON 출력 설정은 기본으로 `ensure-ascii`(ASCII 밖 문자를 이스케이프)와 `escape-slash`(`/` 를 `\/` 로 씀)가 켜져 있습니다[1]. 그래서 원본 파일에서 URL 을 문자열로 grep 하면 `/index.html` 이 아니라 `\/index.html` 을 찾아야 하고, jq 로 읽으면 원래 문자로 풀려서 나옵니다. IPv6 주소도 기본으로 `fe80:0000:0000:0000:020c:29ff:faf2:ab42` 처럼 줄이지 않은 형식으로 쓰므로, 줄인 형식(`fe80::20c:29ff:faf2:ab42`)을 쓰는 다른 도구의 기록과 문자열로 맞출 때 형식을 먼저 통일합니다[1].

`xff` 설정을 켜면 HTTP `X-Forwarded-For` 헤더 값을 쓰는데, `mode: overwrite` 이면 `src_ip` 나 `dest_ip` 를 그 값으로 덮어씁니다[2]. 이 경우 IP 필드는 패킷의 IP 주소가 아니므로 센서 설정을 확인합니다.

### flow_id 와 community_id

`flow_id` 는 흐름 시작 시각(초·마이크로초의 하위 16비트씩)과 흐름 해시를 합친 뒤 51비트로 자른 값입니다[11]. 흐름 해시에는 Suricata 가 시작할 때마다 새로 뽑는 난수가 섞이므로, 같은 pcap 을 다시 돌려도 `flow_id` 가 달라집니다[11]. 그래서 `flow_id` 는 한 번 실행한 한 센서의 기록 안에서만 묶는 키로 씁니다. 예를 들어 `jq 'select(.flow_id==1127453392018734)' eve.json` 으로 그 흐름의 경고·HTTP·fileinfo·flow 기록을 한꺼번에 뽑습니다[3].

센서 두 대의 기록, 원래 센서 기록과 다시 돌린 기록, Suricata 와 Zeek 기록을 잇는 데는 커뮤니티 ID (Community ID)를 씁니다. 커뮤니티 ID v1 은 시드(2바이트)·두 IP·프로토콜·두 포트를 SHA-1 로 해시해 base64 로 쓴 값에 `1:` 을 붙인 것이고, 숫자가 작은 쪽 주소·포트를 앞에 두기 때문에 방향과 상관없이 같은 값이 나옵니다[12]. 도구마다 시드(`community-id-seed`, 기본 0)가 같아야 값이 일치합니다[1]. VLAN 을 계산에 넣는 도구와 넣지 않는 도구의 값은 서로 맞지 않고, 서로 다른 흐름이 같은 값을 가질 수도 있으므로 시각과 함께 비교합니다[12]. Zeek 쪽 필드는 [Zeek 로그](../../zeek/zeek-logs/index.md)에 있습니다.

### 시각

`timestamp` 는 `2026-03-02T14:05:11.482913+0900`(만든 예시)처럼 마이크로초 6자리와 콜론 없는 시간대 오프셋이 붙은 센서 현지 시각입니다[9]. 한 사건의 기록이 센서 여러 대에서 나오면 오프셋이 서로 다를 수 있으므로, 합치기 전에 모두 UTC 로 바꿉니다. 시각을 바꾸지 못하면 문자열 `"ts-error"` 가 들어갑니다[9]. 문서 첫머리의 공통 형식 설명에 나오는 `2009-11-24T21:27:09.534255` 는 오프셋이 없는 옛 예시이고, 지금 코드는 Windows 가 아닌 빌드에서 항상 오프셋을 붙입니다[3][9].

Windows 에서 돌린 Suricata 는 오프셋 문자열을 따로 계산하는데, 시간대에 서머타임이 있는지를 나타내는 값(`_daylight`)을 시(時)에 그대로 더합니다[9]. 그래서 서머타임이 있는 시간대의 Windows 센서라면 오프셋이 실제와 다를 가능성이 있고, 같은 패킷의 pcap 시각(UTC 기준 epoch)과 비교해 확인합니다.

무엇의 시각인지는 기록 종류마다 다릅니다.

| 기록 | `timestamp` 의 기준 |
|---|---|
| `alert`·`dns`·`http`·`tls`·`fileinfo`·`anomaly` | 그 기록을 만든 패킷의 캡처 시각[10] |
| `flow`·`netflow` | 흐름 기록을 쓴 시점. 실시간 캡처면 센서 시스템 시계, pcap 을 읽을 때면 처리 중인 패킷 시각 가운데 가장 이른 값[9][17] |

그래서 `flow` 기록의 `timestamp` 는 통신 시각과 다르고, pcap 을 읽은 결과에서는 `flow.start` 보다 이를 수도 있습니다[3]. 통신 시각은 `flow.start`·`flow.end` 로 확인합니다[3]. 인증서 유효 기간처럼 형식이 다른 시각 필드는 [프로토콜 기록](protocol-events.md)에서 다룹니다. 여러 로그의 시각을 합치는 방법은 [네트워크 기록의 시각](../../../01-foundations/records/timestamps.md)에 있습니다.

### 비어 있는 기록을 해석할 때

`stats` 기록은 기본으로 값이 0 인 카운터까지 모두 씁니다[1]. AF_PACKET 캡처에서 `capture.kernel_drops` 는 사용자 영역으로 보내지 못하고 버린 패킷 수입니다[8]. `tcp.reassembly_gap` 은 TCP 스트림에서 빠진 데이터 수이고, 패킷 손실 말고도 잘못된 체크섬이나 스트림 엔진의 메모리 부족 때문에 늘어납니다[8]. 조사 시간대에 이 값이 크게 늘었다면 그 시간대에 기록이 없는 것을 "통신이 없었다" 로 해석할 수 없습니다. `anomaly` 기록의 `type` 은 주로 `decode`·`stream`·`applayer` 이고, `decoder.udp.pkt_too_small` 처럼 무엇이 이상했는지 `event` 필드에 이름으로 남습니다[3].

### pcap 을 다시 돌릴 때

보관한 pcap 을 Suricata 로 다시 분석해 EVE 를 만들 수도 있습니다. `-r 경로` 는 pcap 파일을 읽는 모드이고, 경로가 폴더면 그 안의 파일을 수정 시각 순으로 처리하면서 흐름 상태를 파일 사이에 이어 갑니다[5]. `--pcap-file-delete` 옵션이나 설정의 `pcap-file.delete-when-done: true`(또는 경고가 없는 파일만 지우는 `"non-alerts"`)가 있으면 처리한 pcap 을 지우므로, 증거 원본이 아닌 사본에 돌립니다[5][6]. 체크섬 오프로딩 때문에 체크섬이 틀린 캡처는 `-k none` 으로 체크섬 검사를 끄고 돌립니다[5][6]. 다시 돌린 결과는 원래 센서의 기록과 `flow_id` 가 다르고 규칙 세트·설정도 다를 수 있으므로, 두 결과를 섞지 않고 출처를 나눠 적습니다.

### 읽는 도구

`eve.json` 은 jq 로 바로 읽을 수 있습니다[1]. `jq -c 'select(.event_type=="alert")' eve.json` 처럼 종류별로 고르거나, `jq -c 'select(.event_type=="flow")|[.proto, .dest_port]' eve.json | sort | uniq -c | sort -nr | head -n10` 으로 목적 포트 상위 10개를 셉니다[15]. SIEM 에 들어간 기록은 필드 이름이 바뀝니다. Security Onion 은 경고를 `source.ip`·`destination.ip`·`rule.name` 같은 이름으로 옮기고 `event.module:"suricata"`·`event.dataset:"alert"` 로 조회합니다[14]. 보고서에 근거로 쓸 때는 SIEM 화면의 값을 원본 `eve.json` 의 필드와 맞춰 둡니다.

## 읽는 순서

1. [경고 기록 (alert)](alert.md) — `alert` 객체의 규칙 번호·심각도·동작, 경고 줄에 붙는 페이로드·앱 계층 정보, 경고 줄의 출발·목적 주소가 연결을 연 쪽과 다를 수 있는 이유를 다룹니다.
2. [프로토콜 기록 (dns·http·tls·flow)](protocol-events.md) — DNS 질의·응답, HTTP 요청, TLS 핸드셰이크와 인증서, 흐름 기록의 필드와 버전별 형식 차이를 다룹니다.
3. [파일 추출 (filestore)](filestore.md) — `fileinfo` 기록의 필드, filestore 로 저장한 파일의 디스크 배치, 저장된 파일이 잘리는 이유를 다룹니다.

## 함께 볼 페이지

- [Zeek 로그](../../zeek/zeek-logs/index.md) — 같은 트래픽의 연결·프로토콜 기록. 커뮤니티 ID 로 대조합니다.
- [네트워크 기록의 시각](../../../01-foundations/records/timestamps.md) — 오프셋이 다른 기록을 UTC 로 합치는 방법.
- [흐름 기록 (NetFlow·IPFIX·sFlow)](../../../01-foundations/records/flow-records.md) — 라우터·방화벽의 흐름 기록과 `flow`·`netflow` 기록 비교.
- [TLS 지문 (JA3·JA4)](../../fingerprints/ja3-ja4.md) — TLS 기록에 붙는 지문 필드의 해석.
- [탐지 규칙 활용 (Suricata·Sigma)](../../../03-techniques/analysis/detection-rules.md) — 규칙을 읽고 경고를 검증하는 방법.
- [세션 복원과 파일 꺼내기](../../../03-techniques/analysis/file-extraction.md) — pcap 에서 파일을 직접 꺼내 filestore 결과와 비교.
- [네트워크 타임라인](../../../03-techniques/analysis/timeline.md) — EVE 기록을 다른 로그와 시간순으로 합치기.
- [Wireshark·tshark로 읽기](../../../03-techniques/analysis/wireshark.md) — `pcap_cnt` 로 찾은 패킷을 열어 보기.

## 참고 문헌

1. OISF, Suricata User Guide, "Eve JSON Output". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
2. OISF, Suricata 배포 설정 예시 eve-log.yaml. https://github.com/OISF/suricata/blob/main/doc/userguide/partials/eve-log.yaml
3. OISF, Suricata User Guide, "Eve JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
4. OISF, Suricata User Guide, "Suricata.yaml". https://github.com/OISF/suricata/blob/main/doc/userguide/configuration/suricata-yaml.rst
5. OISF, Suricata User Guide, "Command Line Options"(options.rst). https://github.com/OISF/suricata/blob/main/doc/userguide/partials/options.rst
6. OISF, Suricata User Guide, "PCAP File Reading". https://github.com/OISF/suricata/blob/main/doc/userguide/capture-hardware/pcap-file.rst
7. OISF, Suricata User Guide, "Log Rotation". https://github.com/OISF/suricata/blob/main/doc/userguide/output/log-rotation.rst
8. OISF, Suricata User Guide, "Statistics". https://github.com/OISF/suricata/blob/main/doc/userguide/performance/statistics.rst
9. OISF, Suricata 소스 src/util-time.c. https://github.com/OISF/suricata/blob/main/src/util-time.c
10. OISF, Suricata 소스 src/output-json.c. https://github.com/OISF/suricata/blob/main/src/output-json.c
11. OISF, Suricata 소스 src/flow.h, src/flow.c, src/flow-hash.c. https://github.com/OISF/suricata/blob/main/src/flow.h , https://github.com/OISF/suricata/blob/main/src/flow.c , https://github.com/OISF/suricata/blob/main/src/flow-hash.c
12. Corelight, Community ID Flow Hashing 명세. https://github.com/corelight/community-id-spec/blob/master/README.md
13. Security Onion Solutions, Security Onion 2.4 문서 "Suricata". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/suricata.rst
14. Security Onion Solutions, Security Onion 2.4 문서 "Alert Data Fields". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/alert-data-fields.rst
15. OISF, Suricata User Guide, "Eve JSON 'jq' Examples". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-examplesjq.rst
16. Wireshark, Display Filter Reference: Frame. https://www.wireshark.org/docs/dfref/f/frame.html
17. OISF, Suricata 소스 src/output-json-flow.c, src/output-json-netflow.c. https://github.com/OISF/suricata/blob/main/src/output-json-flow.c , https://github.com/OISF/suricata/blob/main/src/output-json-netflow.c
