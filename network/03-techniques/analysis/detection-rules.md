---
title: "탐지 규칙 활용"
parent: "기법 · 분석"
nav_order: 420
---

# 탐지 규칙 활용 (Suricata·Sigma)

탐지 규칙(detection rule)은 "이런 조건에 맞는 패킷이나 로그 줄을 찾아라" 를 정해진 형식으로 적은 것입니다. 이 페이지에서는 확보한 패킷 캡처에 Suricata 규칙을 다시 돌려 경고를 얻는 법과, Zeek·방화벽·프록시 로그에 Sigma 규칙을 적용하는 법을 다룹니다. 규칙에 걸렸다는 결과로 주장할 수 있는 범위와, 규칙과 로그 필드 이름이 어긋나 아무 경고 없이 놓치는 경우도 함께 봅니다.

## 언제 쓰나

수 GB 캡처나 몇 주치 로그를 처음부터 한 줄씩 볼 수는 없습니다. 이때 이미 알려진 흔적과 맞는 부분부터 골라내려고 탐지 규칙을 씁니다. 사건 당시 센서가 낸 경고를 같은 캡처로 다시 재현해 확인할 때도 쓰고, 사건 뒤에 새로 나온 규칙으로 보관해 둔 옛 캡처를 다시 검사할 때도 씁니다.

규칙은 대상에 따라 두 종류로 나뉩니다. Suricata 규칙은 패킷과 재조립한 TCP 스트림에 조건을 맞춰 보고, Suricata 가 pcap 을 읽으면서 바로 실행합니다[1][4]. Sigma 규칙은 이미 남은 로그 줄에 조건을 맞춰 보는 YAML 형식이고, 그대로 실행되는 것이 아니라 sigma-cli 로 로그를 검색하는 시스템의 질의로 바꿔서 씁니다[7][11].

| 구분 | Suricata 규칙 | Sigma 규칙 |
|---|---|---|
| 대상 | 패킷·재조립 스트림 (pcap 파일, 실시간 캡처) | 로그 줄 (Zeek 로그, 방화벽·프록시·DNS 로그 등) |
| 형식 | 한 줄: 동작·머리·옵션[1] | YAML: `title`·`logsource`·`detection`[7] |
| 실행 | Suricata 가 직접 실행[4] | sigma-cli 로 검색 질의로 바꾼 뒤 그 시스템에서 실행[11] |
| 결과 | EVE 로그의 `alert` 줄[6] | 변환한 시스템의 검색 결과 |

경고 줄의 필드와 시각은 [경고 기록 (alert)](../../02-artifacts/suricata/eve-json/alert.md)에서, Zeek 로그 필드는 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md)에서 다룹니다. 이 페이지는 규칙을 돌리고 결과를 확인하는 순서에 집중합니다.

## 절차

아래 파일 이름, IP, `flow_id` 값은 모두 만든 예시입니다.

### 1. 원본은 두고 사본에 돌린다

Suricata 는 설정 `pcap-file.delete-when-done` 이 `true` 이면 처리한 pcap 을 지우고, `"non-alerts"` 이면 경고가 나지 않은 pcap 을 지웁니다[5]. 기본값은 `false` 지만 명령줄의 `--pcap-file-delete` 는 설정과 상관없이 모두 지우게 만듭니다[4][5]. 그래서 증거 원본이 아닌 사본에 돌리고, 돌리기 전에 사본의 해시를 작업 기록에 적습니다. 다시 돌린 결과를 원래 센서 기록과 왜 나눠 적어야 하는지는 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)의 "pcap 을 다시 돌릴 때" 에 있습니다.

### 2. 규칙과 설정을 고정하고 기록한다

같은 캡처라도 규칙 파일과 설정이 바뀌면 경고가 달라집니다. 규칙마다 번호 `sid` 가 있고, 규칙 작성자가 규칙을 고칠 때마다 `rev` 를 올립니다[2]. `gid` 는 규칙 묶음 번호로 기본값이 1 입니다[2]. 같은 `sid` 라도 `rev` 가 다르면 조건이 다를 수 있으므로, 돌린 규칙 파일의 사본과 해시, `suricata -V` 로 확인한 버전, 쓴 suricata.yaml 을 함께 보관합니다[2][4]. 규칙 묶음(ruleset)은 suricata-update 로 설치하는 것이 공식 방법이고, 무료 규칙 묶음인 Emerging Threats Open 을 이 방법으로 받을 수 있습니다[1].

설정에서 먼저 볼 것은 주소 변수입니다. 규칙 머리의 `$HOME_NET`·`$EXTERNAL_NET` 은 suricata.yaml 에 적은 주소로 바뀌므로[1], 조사 대상 망의 내부 대역으로 맞추지 않으면 방향이 정해진 규칙이 맞지 않을 수 있습니다. `HOME_NET: any` 에 `EXTERNAL_NET: !$HOME_NET` 으로 두면 `$EXTERNAL_NET` 이 "any 가 아닌 것" 이 되어 이 변수를 쓰는 규칙을 쓸 수 없습니다[1]. 앱 계층 프로토콜(http·tls·dns·smb 등)도 suricata.yaml 에서 켠 것만 규칙에 쓸 수 있고, modbus·dnp3·enip 은 기본으로 꺼져 있습니다[1]. 쓸 수 있는 프로토콜 이름은 `suricata --list-rule-protos` 로 봅니다[1].

규칙이 조용히 빠지는 경우도 확인합니다. `requires` 키워드의 조건(기능·키워드·Suricata 버전)을 맞추지 못한 규칙은 오류로 처리하지 않고 무시합니다[2]. `--init-errors-fatal` 을 주면 규칙을 읽다 오류가 날 때 실패로 끝나고, `-T` 로 설정을 미리 시험할 수 있습니다[4].

### 3. pcap 에 규칙을 돌린다

```
suricata -c case-suricata.yaml -r case01-copy.pcap -S case-rules/all.rules -l ./out -k none
```

`-r` 은 pcap 파일을 읽는 모드입니다[4]. 경로가 폴더면 그 안의 파일을 **수정 시각 순서**로 처리하고 흐름 상태를 파일 사이에 이어 갑니다[4]. 캡처 파일을 복사하면서 수정 시각이 바뀌었다면 처리 순서가 캡처 순서와 달라질 수 있으므로, 파일 수정 시각을 확인하거나 파일을 하나씩 따로 돌립니다. 하위 폴더까지 읽으려면 `--pcap-file-recursive` 를 쓰는데, 깊이는 255 단계까지이고 심볼릭 링크는 무시하며 `--pcap-file-continuous` 와 함께 쓸 수 없습니다[4][5].

`-S` 는 지정한 규칙 파일만 읽고 suricata.yaml 에 적힌 규칙은 쓰지 않습니다[4]. `-s` 는 yaml 의 규칙에 지정한 파일을 더합니다[4]. 규칙 범위를 분명히 하려면 `-S` 를 씁니다. `-l` 은 로그 폴더로, yaml 의 `default-log-dir` 보다 먼저 적용됩니다[4]. `-k none` 은 체크섬 검사를 모두 끄고 `-k all` 은 모두 켭니다[4]. pcap 을 읽을 때 기본값은 `checksum-checks: auto` 로, 체크섬 오프로딩(checksum offloading)을 통계로 감지합니다[5]. `-k none` 없이 돌렸을 때 경고가 예상보다 적으면 `-k none` 으로 다시 돌려 결과를 비교합니다. 특정 주소만 보고 싶으면 BPF 필터를 파일에 적어 `-F` 로 줍니다[4][5].

### 4. 경고에서 패킷과 흐름을 찾아간다

결과는 `-l` 폴더의 eve.json 에 `event_type` 이 `alert` 인 줄로 남습니다[6]. `alert.signature_id` 가 규칙의 `sid`, `alert.signature` 가 규칙의 `msg` 입니다[6]. pcap 을 읽는 모드에서는 `pcap_cnt` 에 규칙에 걸린 패킷의 번호가 들어가서, Wireshark 에서 그 번호의 패킷을 바로 찾을 수 있습니다[6]. 흐름 타임아웃처럼 Suricata 가 내부에서 만든 가짜 패킷에는 `pcap_cnt` 가 없습니다[6].

`flow_id` 는 같은 흐름의 alert·fileinfo·http·anomaly·flow 기록에 같은 값으로 붙습니다[6]. 경고 하나를 찾았으면 같은 흐름의 기록을 모아 앞뒤 요청과 응답, 주고받은 바이트 수를 함께 봅니다.

```
jq 'select(.flow_id==1234567890123456)' out/eve.json
```

규칙(gid·sid·rev)별로 경고 수를 세는 명령과 alert 줄의 필드 설명은 [경고 기록 (alert)](../../02-artifacts/suricata/eve-json/alert.md)에, 패킷 번호로 캡처를 여는 방법은 [Wireshark·tshark로 읽기](wireshark.md)에 있습니다.

### 5. 규칙 원문을 읽는다

경고의 `signature` 는 규칙 작성자가 붙인 이름일 뿐이라, 무엇에 맞았는지는 규칙 원문을 읽어야 압니다. Suricata 규칙은 동작(action), 머리(header), 괄호 안 옵션(rule options) 세 부분으로 이뤄집니다[1]. 아래는 Suricata 문서의 예제 규칙입니다[1].

```
alert http $HOME_NET any -> $EXTERNAL_NET any (msg:"HTTP GET Request Containing Rule in URI"; flow:established,to_server; http.method; content:"GET"; http.uri; content:"rule"; fast_pattern; classtype:bad-unknown; sid:123; rev:1;)
```

`alert` 가 동작이고, `http $HOME_NET any -> $EXTERNAL_NET any` 가 머리로 프로토콜·출발지 주소·출발지 포트·방향·목적지 주소·목적지 포트 순서입니다[1]. 괄호 안에서는 `http.method` 다음의 `content:"GET"` 이 HTTP 메서드를, `http.uri` 다음의 `content:"rule"` 이 URI 를 검사합니다. 이렇게 버퍼 이름을 먼저 쓰고 뒤따르는 키워드를 그 버퍼에 적용하는 방식을 sticky buffer 라고 하고, 옵션 순서를 바꾸면 규칙의 뜻이 달라집니다[1].

방향 표시는 세 가지입니다. `->` 는 그 방향의 패킷만 맞추고, `<>` 는 양방향 규칙 두 개로 복제해 어느 방향이든 맞추며, `=>` 는 요청과 응답을 모두 본 트랜잭션에만 맞춥니다[1]. `<-` 는 없습니다[1].

규칙이 보는 데이터가 원래 바이트가 아닐 수 있다는 점도 기억합니다. HTTP 키워드, 재조립한 스트림, TLS·SSL·SSH·FTP·dcerpc 버퍼는 Suricata 가 이상한 내용을 지우고 패킷을 합쳐 만든 정규화 버퍼(normalized buffer)라서, 원래 바이트를 해석한 결과입니다(`http_raw_uri` 같은 예외가 있습니다)[1]. 경고가 가리키는 문자열은 [Wireshark·tshark로 읽기](wireshark.md)의 방법으로 패킷 원본에서 다시 확인합니다.

한 규칙만 봐서는 조건을 다 알 수 없는 경우도 있습니다. `noalert` 가 붙은 규칙은 맞아도 경고를 남기지 않고 나머지 동작만 수행하는데, 주로 flowbits·xbits·datasets 로 상태를 기록해 두고 다른 규칙이 그 상태를 확인해 경고를 내게 할 때 씁니다[1]. 경고를 낸 규칙에 `xbits:isset` 처럼 상태를 확인하는 키워드가 있으면 상태를 설정한 규칙을 규칙 파일에서 찾아 함께 읽습니다. `threshold`·`detection_filter` 가 있는 규칙은 경고 수를 줄이므로 경고 수가 실제로 맞은 횟수와 다릅니다[3]. 자세한 동작은 [경고 기록 (alert)](../../02-artifacts/suricata/eve-json/alert.md)에 있습니다.

### 6. 로그에 Sigma 규칙을 적용한다

Sigma 규칙은 YAML 파일이고 `title`·`logsource`·`detection` 이 필수입니다[7]. `logsource` 는 어떤 로그에 적용하는지를 `category`(firewall·proxy 등), `product`(zeek 등), `service`(http 등)로 적고, 값은 소문자로 쓰며 공백은 `_` 로 바꿉니다[7]. `detection` 에는 검색 조건 묶음(search identifier)을 이름 붙여 적고 `condition` 에서 `and`·`or`·`not`·괄호와 `1 of selection*`·`all of them` 같은 표현으로 조합합니다[7]. 조건 묶음 안에서 필드 여러 개를 나열한 맵은 AND, 값 목록은 OR 로 묶입니다[7]. 연산자는 `or` 가 가장 약하게 묶이고 `and`, `not`, `x of`, 괄호 순으로 더 강하게 묶이며, `1 of them`·`all of them` 은 이름이 `_` 로 시작하는 조건 묶음을 빼고 계산합니다[7].

아래는 SigmaHQ 규칙 저장소의 Zeek http.log 규칙에서 판단에 필요한 부분만 옮긴 것입니다[12].

```yaml
title: WebDav Put Request
logsource:
    product: zeek
    service: http
detection:
    selection:
        user_agent|contains: 'WebDAV'
        method: 'PUT'
    filter:
        id.resp_h|cidr:
            - '10.0.0.0/8'
            - '127.0.0.0/8'
            - '172.16.0.0/12'
            - '192.168.0.0/16'
            - '169.254.0.0/16'
    condition: selection and not filter
level: low
```

http.log 에서 `user_agent` 에 "WebDAV" 가 들어 있고 `method` 가 PUT 인 줄 가운데, 응답한 쪽 주소 `id.resp_h` 가 사설·루프백·링크 로컬 대역이 아닌 줄을 찾습니다[12]. 필드 이름 뒤의 `|contains`·`|cidr` 는 수식어(modifier)로, 값을 어떻게 비교할지 정합니다[8].

| 수식어 | 뜻 |
|---|---|
| `contains`, `startswith`, `endswith` | 값이 필드 안에, 앞에, 끝에 있음[8] |
| `cased` | 대소문자를 구분해 비교(기본은 구분하지 않음)[8] |
| `exists` | 필드가 있는지만 봄. 값이 비었거나 null 인지는 보지 않음[8] |
| `re` | 정규식. 기본으로 대소문자를 구분[8] |
| `cidr` | IPv4·IPv6 주소 대역[8] |
| `lt`, `lte`, `gt`, `gte` | 숫자 크기 비교[8] |
| `minute`, `hour`, `day`, `week`, `month`, `year` | 날짜에서 숫자를 꺼냄. 시간대·형식은 바꾸지 않음[8] |

수식어가 없는 값은 대소문자를 구분하지 않는 문자열로 비교하고 `*`·`?` 와일드카드를 쓸 수 있습니다[7].

필드 이름은 `logsource` 에 따라 다릅니다. 같은 "목적지 주소" 라도 Zeek 규칙은 Zeek 로그의 필드 이름을, 분류(taxonomy) 규칙은 Sigma 가 정한 이름을 씁니다.

| logsource | 쓰는 필드 이름 예 |
|---|---|
| `product: zeek` + `service: dce_rpc`·`dns`·`http`·`kerberos`·`rdp`·`smb_files`·`x509` | Zeek 로그 필드 그대로: `id.orig_h`, `id.resp_h`, `user_agent`, `method`, `certificate.serial`[9][12][13][16] |
| `category: firewall` | `src_ip`, `src_port`, `dst_ip`, `dst_port`, `username`[9] |
| `category: proxy` | W3C 확장 로그 형식 이름: `c-uri`, `c-useragent`, `cs-host`, `cs-method`, `sc-status`, `cs-bytes`, `sc-bytes`, `src_ip`, `dst_ip`[9] |
| `category: network` + `service: connection`·`dns` (명세 2.1.0 에서 추가) | `source.ip`, `destination.ip`, `destination.port`, `network.community_id`, `dns.question.name` 등[9] |

규칙을 쓰려면 sigma-cli 로 검색 질의로 바꿉니다[11].

```
sigma plugin list
sigma plugin install splunk
sigma convert -t splunk -p 파이프라인이름 -o out.txt rules/network/zeek
```

`-t` 는 변환할 대상 시스템(backend), `-p` 는 처리 파이프라인(processing pipeline), `-o` 는 출력 파일, `-f` 는 출력 형식입니다[11]. 대상 시스템 플러그인은 `sigma plugin install` 로 먼저 설치하고, 설치된 대상과 파이프라인은 `sigma list` 로 봅니다[11]. 규칙의 필드 이름을 실제 로그의 필드 이름으로 바꾸는 필드 대응(field mapping)과, `category: firewall` 을 어느 색인에서 찾을지는 변환 설정이 정합니다[7][11]. sigma-cli 는 아직 정식판 전(pre-release) 상태입니다[11].

### 7. 여러 사건을 묶는 상관 규칙을 쓴다

"한 시간에 같은 목적지로 실패한 로그인이 100번 이상" 처럼 여러 로그 줄을 묶어 판단하려면 Sigma 상관 규칙(correlation rule)을 씁니다[10]. `type` 은 `event_count`(건수), `value_count`(서로 다른 값의 수), `temporal`(정한 시간 안에 모두 나타남), `temporal_ordered`(순서까지 맞음), `value_sum`, `value_avg`, `value_percentile` 이고, 묶을 규칙 `rules`, 묶는 기준 필드 `group-by`, 시간 범위 `timespan`, `condition` 을 적습니다[10]. `timespan` 은 `90m` 처럼 숫자에 `s`·`m`·`h`·`d` 를 붙여 씁니다[10].

변환 대상 시스템에 따라서는 정각 단위 같은 고정 구간 안에서만 셀 수 있습니다. 이때 `timespan: 1h` 는 한 정각 구간 안에 모든 사건이 있어야 맞고, 두 구간에 걸친 사건은 놓칩니다[10]. 이런 제약이 있으면 변환기가 경고를 내야 하므로[10], 변환할 때 나온 경고를 버리지 말고 작업 기록에 남깁니다.

### 8. 걸린 줄을 원본 기록으로 확인한다

규칙에 걸린 줄마다 원본 기록을 다시 엽니다. Suricata 경고는 `pcap_cnt` 로 패킷을, Sigma 검색 결과는 원래 로그 파일의 그 줄을 확인합니다. 규칙 이름이 가리키는 행위를 주장하려면, 그 행위를 보여 주는 앞뒤 기록(요청과 응답, 전송량, 이어진 연결)을 따로 찾아야 합니다. 시간순으로 모으는 방법은 [네트워크 타임라인](timeline.md)에 있습니다.

## 도구

| 도구 | 쓰임 |
|---|---|
| Suricata | pcap 에 규칙을 돌려 EVE 로그를 만듭니다[1][4] |
| suricata-update, Emerging Threats Open | 규칙 묶음 설치와 무료 규칙 묶음[1] |
| SigmaHQ 규칙 저장소 | `rules/network` 아래 zeek·firewall·dns 폴더와 `rules/web` 아래 proxy_generic 폴더에 네트워크 로그용 규칙이 있습니다[12][13][14][15][16] |
| sigma-cli (pySigma 기반) | Sigma 규칙을 검색 질의로 바꿉니다[11] |
| jq | eve.json 을 `flow_id`·`sid` 로 걸러 봅니다[6] |
| Wireshark·tshark | 경고가 가리킨 패킷을 확인합니다 ([Wireshark·tshark로 읽기](wireshark.md)) |

## 함정과 한계

- **규칙은 로그 필드 이름에 묶여 있습니다.** Zeek 규칙은 `id.resp_h`, 방화벽 분류 규칙은 `dst_ip`, 네트워크 분류 규칙은 `destination.ip` 를 씁니다[9][12]. 필드 대응이 틀리면 검색 질의는 오류 없이 결과 0건을 냅니다. 규칙을 적용하기 전에 알려진 줄 하나로 질의를 시험해 맞는지 확인합니다.
- **필드 값의 뜻이 제품마다 다릅니다.** SigmaHQ 의 평문 프로토콜 사용 규칙은 허용된 연결을 `action` 값 `forward`·`accept`·`2` 나 `blocked: "false"` 로 찾습니다. `action` 값을 남기지 않고 막았는지 여부만 표시하는 방화벽도 있어서 두 조건을 함께 둔 것입니다[14]. 대상 방화벽 로그의 실제 값은 [방화벽 로그](../../02-artifacts/devices/firewall-logs.md)에서 확인합니다.
- **proxy 의 바이트 필드 설명이 서로 다릅니다.** Sigma 분류 부록의 proxy 절은 `cs-bytes` 를 "서버가 보낸 바이트", `sc-bytes` 를 "클라이언트가 보낸 바이트" 로 적었고, 같은 문서의 webserver 절은 `sc-bytes` 를 서버가 보낸 바이트, `cs-bytes` 를 서버가 받은 바이트로 적었습니다[9]. proxy 절에서도 `cs-cookie`·`cs-host` 는 클라이언트가 서버로 보낸 값으로 적혀 있어[9], `cs-` 를 클라이언트에서 서버로 가는 값으로 보면 webserver 절의 설명과 맞습니다. 전송량 규칙을 쓸 때는 대상 프록시 로그의 필드 정의를 [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md)에서 확인합니다.
- **Sigma 시각 수식어는 시간대를 바꾸지 않습니다.** `hour` 같은 수식어는 로그에 적힌 날짜에서 숫자만 꺼내므로[8], UTC 로그와 현지 시각 로그에 같은 규칙을 쓰면 다른 시간대가 걸립니다. 로그마다 시각 기준은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)에서 확인합니다.
- **대소문자 규칙이 섞여 있습니다.** Sigma 값은 기본으로 대소문자를 구분하지 않지만 `re` 정규식은 구분합니다[7][8]. 변환한 질의가 대상 시스템에서 같은 방식으로 비교하는지 결과로 확인합니다.
- **경고 수는 맞은 횟수가 아닙니다.** `threshold` 의 `limit` 은 기간당 경고 수를 N개로 제한하고, `threshold` 는 N번째에 경고를 냅니다[3]. flowbits 같은 동작은 한도와 상관없이 수행됩니다[3]. 실제 횟수는 flow 기록이나 pcap 으로 셉니다.
- **`alert.action` 은 최종 처리 결과가 아닙니다.** `allowed` 는 그 규칙이 패킷을 막지 않았다는 뜻이고, 한 패킷이 여러 규칙에 맞을 수 있어서 최종 결과는 `verdict` 로 봅니다[6].
- **규칙이 빠진 채로 돌 수 있습니다.** `requires` 조건을 못 맞춘 규칙은 오류 없이 무시되고[2], yaml 에서 꺼진 앱 계층 프로토콜은 규칙에 쓸 수 없습니다[1]. 결과가 없다는 것은 "읽힌 규칙에 맞는 것이 없었다" 는 뜻입니다.
- **규칙은 알려진 흔적만 찾습니다.** 규칙이 없는 행위, 로그에 필드가 없는 행위, 암호화로 내용이 보이지 않는 연결은 경고가 나지 않습니다. 암호화된 연결에서 볼 수 있는 값은 [암호화된 트래픽 분석](encrypted-traffic.md)에 있습니다.
- **오탐은 규칙에 적혀 있기도 합니다.** Sigma 규칙의 `falsepositives` 에 알려진 오탐이 있고, `level` 은 `informational`·`low`·`medium`·`high`·`critical` 중 하나입니다[7]. 예를 들어 rclone 사용자 에이전트 규칙은 `medium` 이고, 같은 사용자 에이전트를 쓰는 정상 스크립트나 관리 작업이 오탐으로 올라 있습니다[15].

## 결과를 어떻게 해석하나

규칙에 걸렸다는 결과로는 "규칙에 적은 조건과 맞는 패킷이나 로그 줄이 있었다" 까지만 증명할 수 있습니다. 규칙 이름(`msg`·`title`)이 가리키는 행위가 실제로 일어났다거나 공격이 성공했다는 것은 증명하지 못합니다. 예를 들어 SigmaHQ 의 Cobalt Strike 기본 인증서 규칙은 x509.log 의 `certificate.serial` 값 하나만 비교하므로[13], 걸린 줄로는 그 일련번호의 인증서가 오갔다는 것만 알 수 있습니다. Zeek 는 같은 인증서를 일정 기간 x509.log 에 다시 쓰지 않을 수 있어서 건수를 셀 때는 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md)의 x509.log 설명을 봅니다.

걸린 것이 없다는 결과도 좁게 해석합니다. 규칙이 없거나, 규칙이 읽히지 않았거나, 로그에 해당 필드가 없거나, 필드 대응이 틀렸거나, 센서가 패킷을 놓쳤으면 경고는 나지 않습니다. 보고서에는 "이 규칙 묶음(파일 해시·rev)으로 이 캡처를 검사했을 때 맞는 것이 없었다" 처럼 검사 조건과 함께 씁니다.

시각도 구분해서 적습니다. Suricata 경고의 `timestamp` 는 규칙에 걸린 패킷의 시각이라 pcap 을 나중에 다시 돌려도 원래 패킷 시각이 찍히는데, 그 근거와 시각 형식, UTC 로 바꾸는 법은 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)와 [경고 기록 (alert)](../../02-artifacts/suricata/eve-json/alert.md)에 있습니다. Sigma 검색 결과의 시각은 원래 로그가 기록한 시각이고, 그 기준은 로그 종류마다 다릅니다([네트워크 로그의 종류](../../01-foundations/records/log-types.md)).

사건 당시 센서가 낸 경고와 분석할 때 다시 돌려 얻은 경고도 나눠 적습니다. Emerging Threats 규칙은 `metadata` 에 `created_at`·`updated_at` 을 두고 이 값이 경고의 `alert.metadata` 에도 나오므로[2][6], 규칙이 사건보다 나중에 만들어졌다면 당시 센서는 그 규칙으로 경고를 낼 수 없었습니다. 보고서 문장은 이렇게 씁니다(만든 예시).

> 2026-03-02 01:10:05Z 부터 01:12:40Z 사이 캡처(case01.pcap, SHA-256 기록)에 Suricata 7 과 규칙 파일 all.rules(SHA-256 기록)를 분석 시점에 다시 적용했을 때, 10.20.1.15 에서 203.0.113.50 의 80번 포트로 가는 흐름에서 sid 1000001 rev 3 규칙에 맞는 패킷 4건이 있었다. 이 규칙은 2026-03-10 에 만들어져 사건 당시 센서에는 없었다.

경고를 받은 뒤 이어서 볼 기록과 순서는 [악성 코드가 C2 서버와 통신했나](../../04-scenarios/intrusion/c2-communication.md) 같은 조사 시나리오 페이지에, 보고서 전체의 틀은 [네트워크 포렌식 보고서](../reporting/forensic-report.md)에 있습니다.

## 참고 문헌

1. OISF, Suricata User Guide — Rules Format. https://github.com/OISF/suricata/blob/main/doc/userguide/rules/intro.rst
2. OISF, Suricata User Guide — Meta Keywords. https://github.com/OISF/suricata/blob/main/doc/userguide/rules/meta.rst
3. OISF, Suricata User Guide — Thresholding Keywords. https://github.com/OISF/suricata/blob/main/doc/userguide/rules/thresholding.rst
4. OISF, Suricata User Guide — Command Line Options. https://github.com/OISF/suricata/blob/main/doc/userguide/partials/options.rst
5. OISF, Suricata User Guide — PCAP File Reading. https://github.com/OISF/suricata/blob/main/doc/userguide/capture-hardware/pcap-file.rst
6. OISF, Suricata User Guide — Eve JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
7. SigmaHQ, Sigma Rules Specification 2.1.0. https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-rules-specification.md
8. SigmaHQ, Sigma Modifiers 2.1.0. https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-appendix-modifiers.md
9. SigmaHQ, Sigma Taxonomy Appendix. https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-appendix-taxonomy.md
10. SigmaHQ, Sigma Correlation Rules Specification 2.1.0. https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-correlation-rules-specification.md
11. SigmaHQ, Sigma Command Line Interface (sigma-cli) README. https://github.com/SigmaHQ/sigma-cli/blob/main/README.md
12. SigmaHQ, WebDav Put Request (zeek_http_webdav_put_request.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_webdav_put_request.yml
13. SigmaHQ, Default Cobalt Strike Certificate (zeek_default_cobalt_strike_certificate.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_default_cobalt_strike_certificate.yml
14. SigmaHQ, Cleartext Protocol Usage (net_firewall_cleartext_protocols.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/network/firewall/net_firewall_cleartext_protocols.yml
15. SigmaHQ, Rclone Activity via Proxy (proxy_ua_rclone.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/web/proxy_generic/proxy_ua_rclone.yml
16. SigmaHQ, Publicly Accessible RDP Service (zeek_rdp_public_listener.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_rdp_public_listener.yml
