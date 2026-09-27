---
title: "Zeek 로그"
parent: "아티팩트 · Zeek"
nav_order: 140
has_children: true
has_toc: false
---

# Zeek 로그 (Zeek Logs)

Zeek 는 센서가 본 패킷을 프로토콜별로 해석해 연결·DNS·HTTP·TLS·파일 같은 기록을 로그 파일 여러 개로 나눠 씁니다. 연결에서 나온 로그 줄에는 연결마다 붙는 `uid` 와 5-튜플(`id.orig_h`·`id.orig_p`·`id.resp_h`·`id.resp_p`)이 들어 있어서, `uid` 하나로 한 연결의 여러 로그 줄을 이어 볼 수 있습니다. 기록은 대부분 연결이나 거래가 끝난 뒤에 쓰기 때문에 파일 안의 줄 순서가 시간 순서와 다르고, 로그 모양은 설치본의 설정과 패키지에 따라 달라집니다.

## 왜 중요한가

Zeek 로그는 패킷을 통째로 저장하지 않고 연결과 거래의 요약만 남깁니다. 그래서 패킷이 남아 있지 않을 때 "그 시각에 이 내부 IP 가 어느 외부 주소와 어떤 프로토콜로 얼마나 주고받았나", "어떤 도메인을 물었나", "어떤 파일이 오갔나" 를 확인할 수 있는 기록이 Zeek 로그뿐인 경우가 있습니다. Security Onion 같은 보안 관제 배포판은 Zeek 로그를 JSON 으로 `/nsm/zeek/logs` 에 쓰고 Elasticsearch 로 모읍니다[20]. RITA 는 Zeek 로그(TSV·JSON)를 읽어 비컨과 긴 연결을 찾고[22], 연구용 분석 도구인 Granef 는 Zeek 로그 형식과 로그 사이의 관계를 그대로 살려 호스트·연결·응용 데이터를 그래프로 잇습니다[23].

Zeek 로그로는 "센서가 본 패킷에서, 이 시각에, 이 주소 사이에 이런 연결과 응용 계층 거래가 있었다" 는 데까지 증명할 수 있습니다. 패킷 본문은 남지 않고, 파일은 추출 설정을 켰을 때만 따로 저장됩니다. 캡처 위치 때문에 센서에 닿지 않았거나 도중에 버린 트래픽, 암호화된 응용 내용, 호스트 안에서 어떤 프로세스나 사용자가 통신했는지는 로그에 없습니다. 로그와 필드 구성도 설치본마다 달라서, 어떤 필드나 로그가 없다고 해서 그런 일이 없었다고 쓸 수 없습니다[1]. 센서 위치에 따라 보이는 범위는 [어디서 캡처하나](../../../01-foundations/capture/capture-points.md)에 있습니다.

## 한눈에 보기

조사에서 자주 여는 로그와 한 줄이 무엇을 뜻하는지, 언제 파일에 쓰이는지를 정리하면 다음과 같습니다.

| 로그 | 한 줄의 단위 | 알려 주는 것 | 파일에 쓰는 때 | 자세히 |
|---|---|---|---|---|
| `conn.log` | 연결(TCP) 또는 흐름(UDP·ICMP 등) 하나 | 누가 누구와 언제, 얼마나 오래, 몇 바이트를, 어떤 프로토콜로 | 연결 상태를 지울 때[8] | [연결 기록](conn-log.md) |
| `dns.log` | DNS 질의·응답 한 쌍 | 질의 이름·유형, 응답 값, 응답 코드 | 질의와 응답이 짝지어질 때, 못 짝지은 것은 연결이 끝날 때[9] | [DNS 기록](dns-log.md) |
| `http.log` | HTTP 요청·응답 한 쌍 | 메서드·Host·URI·User-Agent·상태 코드·본문 크기·파일 ID | 응답 메시지가 끝날 때[10] | [HTTP 기록](http-log.md) |
| `ssl.log` | TLS 세션 하나 | 버전·암호 스위트·SNI·인증서 지문 | 핸드셰이크가 끝나거나 연결이 끝날 때[11] | [TLS·인증서 기록](ssl-x509-log.md) |
| `x509.log` | 인증서 하나 | 주체·발급자·유효 기간·주체 대체 이름 | 인증서 분석이 끝날 때. 같은 인증서는 기본으로 하루 동안 다시 쓰지 않음[12] | [TLS·인증서 기록](ssl-x509-log.md) |
| `files.log` | 파일 하나 | MIME 유형·크기·해시·추출한 파일 이름 | 파일 분석 상태를 지울 때[13] | [파일 기록](files-log.md) |
| `notice.log` | 스크립트가 올린 알림 하나 | 알림 종류·메시지·관련 호스트 | 알림이 생길 때[14] | [경고와 이상 기록](notice-weird-log.md) |
| `weird.log` | 프로토콜 이상 하나 | 이상 이름·추가 정보 | 이상을 알아챘을 때[15] | [경고와 이상 기록](notice-weird-log.md) |

이 밖에도 `analyzer`·`ftp`·`smtp`·`ssh`·`pe`·`dhcp`·`ntp`·`smb`·`irc`·`ldap`·`postgresql`·`quic`·`rdp`·`traceroute`·`tunnel`·`known_*`·`software`·`capture_loss`·`reporter` 같은 로그가 있습니다[2]. pcap 을 한 번 돌리기만 해도 `packet_filter.log` 가 생기는데, 이 파일에는 Zeek 가 적용한 캡처 필터(기본 `ip or not ip`)가 남습니다[1].

### 파일 위치

`zeek -r 파일.pcap` 처럼 명령행에서 돌리면 현재 폴더에 로그를 씁니다[1][7]. ZeekControl(`zeekctl`)로 운영하는 센서는 실행 중인 로그를 `$PREFIX/logs/current` 에 쓰고, 교대(rotation)하거나 멈추면 `$PREFIX/logs/YYYY-MM-DD/` 폴더로 옮기면서 gzip 으로 압축합니다[1][7]. 옮긴 파일 이름은 `weird.11:03:38-11:03:43.log.gz` 처럼 로그 종류 뒤에 그 파일이 담은 시간 구간을 붙인 형식입니다[1][7]. ZeekControl 기본 설정에서는 한 시간마다 교대하지만, `zeek -i eth0` 처럼 명령행으로 직접 실시간 캡처하면 교대하지 않습니다[1]. 스크립트 쪽 기본값 `Log::default_rotation_interval` 은 `0secs`(교대 안 함)이고 ZeekControl 설정이 이 값을 덮어씁니다[3].

센서가 비정상 종료하면 교대되지 않은 로그가 남을 수 있습니다. `LogAscii::enable_leftover_log_rotation` 을 켜면 다음 실행 때 이런 파일을 찾아 교대하는데(교대 주기가 0보다 클 때만), 기본값은 꺼짐(`F`)이라서 `current` 에 남은 파일도 함께 수집합니다[4]. Security Onion 에서는 `/nsm/zeek/logs` 아래를 봅니다[20]. 수집과 보관 기간은 [로그 수집과 보존](../../../03-techniques/acquisition/log-collection.md)에 있습니다.

### 두 가지 형식: TSV 와 JSON

기본 형식은 탭으로 필드를 나눈 TSV 입니다. 파일 머리에 `#` 로 시작하는 메타 줄이 붙고, 파일을 닫을 때 `#close` 줄이 마지막에 붙습니다[1][5].

```
#separator \x09
#set_separator	,
#empty_field	(empty)
#unset_field	-
#path	conn
#open	2026-03-02-14-10-05
#fields	ts	uid	id.orig_h	id.orig_p	id.resp_h	id.resp_p	proto	service	duration	...
#types	time	string	addr	port	addr	port	enum	string	interval	...
1772427851.482913	CmES5u32sYpV7JYN	10.0.5.23	53144	203.0.113.80	443	tcp	ssl	2.784753	...
#close	2026-03-02-15-00-00
```

(만든 예시, 필드 일부 생략)

`#fields` 줄은 필드 이름이고 `#types` 줄은 Zeek 자료형(`time`·`addr`·`port`·`interval`·`count`·`set[string]` 등)입니다[1]. 값이 없는 필드는 `-`(`unset_field`), 값은 있지만 비어 있는 필드(예: 빈 집합)는 `(empty)`(`empty_field`)로 써서 둘을 구분합니다[1][3]. 집합 안의 값은 쉼표로 나눕니다[3].

`LogAscii::use_json=T` 를 주면 한 줄에 JSON 객체 하나를 씁니다(기본값 `F`)[4]. 예를 들어 `zeek -C -r trace.pcap LogAscii::use_json=T` 로 돌립니다[1]. JSON 로그에는 메타 줄이 없어서 `#types` 같은 자료형 정보와 `#open`·`#close` 도 없습니다[4]. 필드 이름은 `"id.orig_h"` 처럼 점이 들어간 이름을 그대로 키로 씁니다[1].

```json
{"ts":1772427851.482913,"uid":"CmES5u32sYpV7JYN","id.orig_h":"10.0.5.23","id.orig_p":53144,"id.resp_h":"203.0.113.80","id.resp_p":443,"proto":"tcp","service":"ssl","duration":2.784753,"conn_state":"SF","history":"ShADadFf"}
```

(만든 예시, 필드 일부 생략)

두 형식은 값이 없는 필드를 다르게 씁니다. TSV 는 `-` 를 쓰지만 JSON 은 기본으로 그 키를 아예 빼고 씁니다(`LogAscii::json_include_unset_fields = F`)[4]. 같은 트래픽의 `conn.log` 도 TSV 에는 `local_orig`·`local_resp` 필드가 `-` 로 있고 JSON 에는 그 키가 없습니다[1]. 그래서 jq 로 조건을 걸 때 키가 없으면 `null` 로 읽힌다는 점을 생각해야 합니다[1].

JSON 의 시각 형식은 `LogAscii::json_timestamps` 로 정하고, 기본값 `JSON::TS_EPOCH` 는 에포크 초를 소수로 씁니다[4]. 이 밖에 밀리초 정수(`TS_MILLIS`·`TS_MILLIS_UNSIGNED`)와 `2021-01-04T04:59:21.582639Z` 같은 ISO 8601 문자열(`TS_ISO8601`)을 고를 수 있어서, 같은 `ts` 필드라도 센서 설정에 따라 모양이 다릅니다[4][6][16].

형식과 관련해 버전과 설정에 따라 달라지는 점은 다음과 같습니다.

| 항목 | 내용 |
|---|---|
| 압축 | `LogAscii::gzip_level` 기본 0(압축 안 함). 켜면 파일 이름에 `gz` 확장자가 붙습니다[4]. |
| 필드 이름 | `Log::default_scope_sep` 기본값은 `.` 이고, `_` 로 바꾼 설치본은 `id_orig_h` 처럼 씁니다[3]. |
| 헤더 한 줄 TSV | 필터 설정 `tsv` 가 `T` 이면 `#fields` 없이 필드 이름 한 줄만 쓰고 다른 메타 줄은 쓰지 않습니다[4]. |
| 제어 문자 | Zeek 8.1.0 부터 JSON 로그의 출력할 수 없는 ASCII 제어 문자를 `\u0007` 처럼 씁니다. 이전에는 `\\x07` 형식이었습니다[17]. |
| 필드 길이 제한 | Zeek 8.1.0 부터 문자열 필드 하나는 4096바이트, 컨테이너 필드 하나는 원소 100개에서 자르고, 한 레코드의 문자열 합계 256000바이트·컨테이너 원소 합계 500개를 넘으면 그 뒤 값은 비워서 씁니다[6][17]. 자를 때 `weird.log` 에 `log_string_field_truncated`·`log_container_field_truncated` 가 남습니다[17]. `http.log` 는 문자열 필드 제한이 0(제한 없음)입니다[10]. |

어떤 로그와 필드가 있는지는 설치본마다 다릅니다. 기본 로그 말고도 켜야 생기는 로그가 있고, 추가 패키지가 로그나 필드를 더하며, 스크립트로 필드를 바꿀 수 있습니다[1]. Zeek 5.2 이상에서는 `logschema` 패키지(`zkg install logschema` 뒤 `zeek logschema/export/jsonschema packages`)로 그 설치본의 로그별 필드 목록을 JSON Schema 나 CSV 로 뽑을 수 있으므로, 분석 대상 센서에서 뽑아 두면 필드 해석의 근거가 됩니다[1].

### uid 로 로그 잇기

`uid` 는 Zeek 가 연결마다 붙이는 고유 식별자이고, 같은 연결에서 나온 로그 줄에는 같은 값이 들어가서 로그끼리 잇는 열쇠가 됩니다[1][7][8]. 로그에서 연결 `uid` 는 `C` 로, 파일 식별자 `fuid` 는 `F` 로 시작하는 모양입니다[1]. `http.log` 의 `resp_fuids` 에 있는 값을 `files.log` 의 `fuid` 에서 찾으면 그 응답으로 받은 파일의 MIME 유형·크기와, 해시 계산을 켠 센서라면 해시까지 알 수 있습니다[1][18].

`uid` 는 실행할 때마다 새로 만들어서, 같은 pcap 을 다시 돌려도 값이 바뀝니다. 같은 pcap 을 TSV 로 한 번, JSON 으로 한 번 돌리면 같은 DNS 연결의 `uid` 가 서로 다르게 나옵니다[1]. 그래서 원래 센서 로그와 나중에 다시 돌린 로그를 `uid` 로 잇지 않고, 5-튜플과 시각으로 맞춥니다. Suricata 같은 다른 도구의 기록과 잇는 데는 커뮤니티 ID (Community ID)를 씁니다. 커뮤니티 ID 는 두 주소·두 포트·프로토콜과 시드(기본 0)로 계산하는 `1:` 로 시작하는 값이라, 같은 흐름이면 도구가 달라도 같은 값이 나옵니다[19]. `conn.log` 에 `community_id` 필드를 쓰려면 `policy/protocols/conn/community-id-logging` 스크립트를 불러와야 하는데, 배포본 `local.zeek` 에는 이 줄이 주석 처리되어 있습니다[18]. Security Onion 은 커뮤니티 ID 를 켜 둡니다[20]. Suricata 쪽 필드는 [Suricata EVE 로그](../../suricata/eve-json/index.md)에 있습니다.

### 시각

로그 줄의 `ts` 는 패킷 시각을 기준으로 한 UNIX 에포크 초이고, 시간대가 들어가지 않는 UTC 기준 값입니다[1][6]. 무엇의 시각인지는 로그마다 달라서(`conn.log` 는 연결의 첫 패킷 시각입니다[1]) 하위 페이지에서 로그별로 다룹니다.

여러 로그를 합칠 때는 파일 안의 줄 순서가 `ts` 순서가 아니라는 점부터 알아 둡니다. 대부분의 로그를 거래나 연결이 끝날 때 쓰기 때문에, 먼저 시작해 늦게 끝난 기록이 뒤에 나옵니다. 예를 들어 한 연결에서 A 질의를 보내고 바로 AAAA 질의를 보냈는데 AAAA 응답이 먼저 오면, `dns.log` 에는 나중에 보낸 AAAA 질의 줄이 먼저 쓰입니다[1]. 시간순으로 보려면 `ts` 로 정렬합니다.

오래 이어지는 연결은 끝나야 `conn.log` 에 나옵니다. `notice.log` 나 `weird.log` 에는 있는데 `conn.log` 에 없는 연결은 로그 기간 안에 끝나지 않은 긴 연결일 가능성이 있습니다[16].

TSV 머리의 `#open`·`#close` 는 패킷 시각이 아니라 Zeek 가 파일을 열고 닫은 때의 시스템 시각입니다. 센서 기계의 현지 시간대로 `2026-03-02-14-10-05` 형식으로 쓰고 시간대 표시가 없습니다[5]. 보관한 pcap 을 나중에 돌린 로그라면 `#open` 은 분석한 시각이라서 트래픽 시각과 다릅니다. 14시 39분에 캡처한 pcap 을 14시 48분에 돌리면 `ts` 는 14시 39분을, `#open` 은 14시 48분을 가리킵니다[1]. 여러 기록의 시각을 합치는 방법은 [네트워크 기록의 시각](../../../01-foundations/records/timestamps.md)에 있습니다.

### pcap 을 다시 돌릴 때

보관한 pcap 으로 Zeek 로그를 새로 만들 때는 `zeek -C -r 파일.pcap` 을 씁니다. Zeek 는 기본으로 체크섬이 틀린 패킷을 버리는데, 체크섬 오프로딩을 쓰는 기계에서 캡처한 파일은 체크섬 값이 채워지지 않은 채 남아 있어서 `-C` 로 체크섬 검사를 꺼야 연결이 제대로 잡힙니다[1][7]. ZeekControl 로 운영하는 센서는 `$PREFIX/share/zeek/site/local.zeek` 을 기본으로 불러오고, 이 파일에서 파일 해시·인증서 검증 같은 스크립트를 켭니다[7][18]. 다시 돌릴 때 센서와 같은 스크립트와 패키지를 불러오지 않으면, 센서 로그에 있던 필드가 새 로그에는 없을 수 있습니다. 다시 돌린 결과는 `uid`·필드 구성·스크립트가 원래 센서와 다르므로, 출처를 나눠 적습니다.

### 읽는 도구

TSV 로그는 `zeek-cut` 으로 필드 이름을 골라 읽습니다. `zeek-cut id.orig_h query answers < dns.log` 처럼 파이프나 `<` 로만 입력을 받고, 적은 순서대로 필드를 출력합니다[1]. `-d` 는 `ts` 를 `%Y-%m-%dT%H:%M:%S%z` 형식의 사람이 읽는 시각으로 바꾸고, `-u` 는 UTC 로 바꿉니다[1]. 형식은 `-D`·`-U` 로 바꿀 수 있습니다[1]. 이 도구는 Zeek 3.0.0 전에는 `bro-cut` 이라는 이름이었습니다[17]. 필드 위치(열 번호)로 고르는 `awk` 는 필드가 더해지거나 순서가 바뀌면 다른 필드를 읽게 되므로 권하지 않습니다[1]. 압축된 로그는 `zcat` 으로 풀어 파이프로 넘깁니다[1][7].

JSON 로그는 jq 로 읽습니다. 점이 들어간 키는 `jq -c '[."id.orig_h", ."query", ."answers"]' dns.log` 처럼 따옴표로 감쌉니다[1]. SIEM 에 넣은 로그는 필드 이름이 바뀌는데, Security Onion 은 `ts` 를 `@timestamp` 로, `uid` 를 `log.id.uid` 로, `id.orig_h`·`id.resp_h` 를 `source.ip`·`destination.ip` 로 옮깁니다[21]. 보고서에는 SIEM 화면의 값을 원래 Zeek 필드 이름과 맞춰 적습니다.

## 읽는 순서

1. [연결 기록 (conn.log)](conn-log.md) — 모든 연결의 요약입니다. 연결 상태(`conn_state`)와 패킷 흐름 기호(`history`), 바이트 수 필드를 읽는 법을 다룹니다.
2. [DNS 기록 (dns.log)](dns-log.md) — 질의 이름·유형·응답·TTL 필드와 질의·응답을 짝짓는 방식, 응답이 없는 줄의 뜻을 다룹니다.
3. [HTTP 기록 (http.log)](http-log.md) — 요청 메서드·Host·URI·User-Agent·상태 코드와, 본문으로 오간 파일을 `files.log` 와 잇는 방법을 다룹니다.
4. [TLS·인증서 기록 (ssl.log·x509.log)](ssl-x509-log.md) — 암호화된 연결에서 남는 SNI·버전·인증서 정보와 Zeek 버전에 따라 달라진 필드를 다룹니다.
5. [파일 기록 (files.log)](files-log.md) — 여러 프로토콜로 오간 파일의 MIME 유형·해시·크기와 파일 추출 설정을 다룹니다.
6. [경고와 이상 기록 (notice.log·weird.log)](notice-weird-log.md) — Zeek 스크립트가 올린 알림과 프로토콜 이상 기록을 해석하는 법을 다룹니다.

## 함께 볼 페이지

- [Suricata EVE 로그](../../suricata/eve-json/index.md) — 같은 트래픽의 경고·프로토콜 기록. 커뮤니티 ID 로 대조합니다.
- [흐름 기록 (NetFlow·IPFIX·sFlow)](../../../01-foundations/records/flow-records.md) — 라우터·방화벽의 흐름 기록과 `conn.log` 비교.
- [네트워크 기록의 시각](../../../01-foundations/records/timestamps.md) — 시간대가 다른 기록을 UTC 로 합치는 방법.
- [TLS 지문 (JA3·JA4)](../../fingerprints/ja3-ja4.md) — `ssl.log` 에 패키지로 더하는 지문 필드의 해석.
- [비컨 찾기](../../../03-techniques/analysis/beaconing.md) — `conn.log` 로 주기적인 통신을 찾는 방법.
- [DNS 분석](../../../03-techniques/analysis/dns-analysis.md) — `dns.log` 로 이상한 질의를 찾는 방법.
- [네트워크 타임라인](../../../03-techniques/analysis/timeline.md) — Zeek 로그를 다른 기록과 시간순으로 합치기.
- [세션 복원과 파일 꺼내기](../../../03-techniques/analysis/file-extraction.md) — pcap 에서 파일을 직접 꺼내 `files.log` 와 비교.

## 참고 문헌

1. Zeek Project, Zeek 문서 "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
2. Zeek Project, Zeek 문서 "Logs" 목록(logs/index.rst). https://github.com/zeek/zeek-docs/blob/master/logs/index.rst
3. Zeek Project, 스크립트 base/frameworks/logging/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/frameworks/logging/main.zeek
4. Zeek Project, 스크립트 base/frameworks/logging/writers/ascii.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/frameworks/logging/writers/ascii.zeek
5. Zeek Project, 소스 src/logging/writers/ascii/Ascii.cc. https://github.com/zeek/zeek/blob/master/src/logging/writers/ascii/Ascii.cc
6. Zeek Project, 스크립트 base/init-bare.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/init-bare.zeek
7. Zeek Project, Zeek 문서 "Quick Start Guide". https://docs.zeek.org/en/master/quickstart.html
8. Zeek Project, 스크립트 base/protocols/conn/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/conn/main.zeek
9. Zeek Project, 스크립트 base/protocols/dns/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/dns/main.zeek
10. Zeek Project, 스크립트 base/protocols/http/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/http/main.zeek
11. Zeek Project, 스크립트 base/protocols/ssl/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/ssl/main.zeek
12. Zeek Project, 스크립트 base/files/x509/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/files/x509/main.zeek
13. Zeek Project, 스크립트 base/frameworks/files/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/frameworks/files/main.zeek
14. Zeek Project, 스크립트 base/frameworks/notice/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/frameworks/notice/main.zeek
15. Zeek Project, 스크립트 base/frameworks/notice/weird.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/frameworks/notice/weird.zeek
16. Zeek Project, Zeek 문서 "weird.log and notice.log". https://github.com/zeek/zeek-docs/blob/master/logs/weird-and-notice.rst
17. Zeek Project, NEWS(버전별 변경 사항). https://github.com/zeek/zeek/blob/master/NEWS
18. Zeek Project, 스크립트 site/local.zeek. https://github.com/zeek/zeek/blob/master/scripts/site/local.zeek
19. Corelight, Community ID Flow Hashing 명세. https://github.com/corelight/community-id-spec/blob/master/README.md
20. Security Onion Solutions, Security Onion 2.4 문서 "Zeek". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/zeek.rst
21. Security Onion Solutions, Security Onion 2.4 문서 "Zeek Fields". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/zeek-fields.rst
22. Active Countermeasures, RITA README. https://github.com/activecm/rita/blob/main/README.md
23. Milan Cermak, Tatiana Fritzová, Vít Rusňák, Denisa Sramkova, "Using relational graphs for exploratory analysis of network traffic data", Forensic Science International: Digital Investigation, 2023. doi:10.1016/j.fsidi.2023.301563
