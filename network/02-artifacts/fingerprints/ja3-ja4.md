---
title: "TLS 지문"
parent: "아티팩트 · 식별 정보"
nav_order: 300
---

# TLS 지문 (JA3·JA4)

TLS 지문 (TLS fingerprint) 은 암호화가 시작되기 전에 평문으로 오가는 ClientHello·ServerHello 의 매개변수를 정해진 순서로 이어 붙여 해시한 값입니다. 트래픽 내용을 풀지 않고도 어떤 TLS 라이브러리와 설정을 쓰는 클라이언트인지 짐작하고, 같은 지문이 나온 연결을 묶을 수 있습니다. 이 페이지는 JA3·JA3S 와 JA4·JA4S 를 계산하는 법, Zeek·Suricata·Wireshark·nfdump 에서 지문이 남는 필드, 지문으로 주장할 수 있는 범위를 다룹니다. 인증서로 만드는 JA4X 는 [인증서로 서버 알아보기](certificates.md) 에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

TLS 연결은 TCP 연결 뒤에 클라이언트가 ClientHello 를 보내면서 시작하고, 서버가 ServerHello 로 답합니다. 두 메시지는 암호화 전에 평문으로 오가고, ClientHello 의 모양은 클라이언트 프로그램을 만들 때 쓴 TLS 라이브러리와 설정에 따라 정해집니다[1][13]. TLS 1.3 에서도 ClientHello·ServerHello 는 평문이고, 그 뒤의 EncryptedExtensions·Certificate 부터 핸드셰이크 키로 암호화됩니다[23]. 그래서 TLS 1.3 연결에서도 지문을 만들 수 있습니다. 메시지 구조와 확장의 뜻은 [TLS와 인증서](../../01-foundations/protocols/tls.md) 에서 다룹니다.

지문은 TLS 메시지 안에 들어 있는 값이 아니라, 센서·분석 도구나 지문 모듈을 넣은 웹 서버가 핸드셰이크를 보고 계산해 기록에 덧붙이는 값입니다[1][6]. 계산 방법은 두 계열입니다.

JA3 는 Salesforce 가 2017년에 만든 방법으로, ClientHello 의 버전·암호 모음·확장·타원 곡선·점 형식을 10진수로 이어 쓴 문자열의 MD5 입니다. 서버 응답을 같은 방식으로 계산한 값이 JA3S 입니다[1]. Salesforce 는 더 이상 JA3 를 관리하지 않고, JA3 를 만든 사람이 FoxIO 에서 JA4 를 이어 만들고 있습니다[1].

JA4 는 FoxIO 가 만든 방법으로, 사람이 읽을 수 있는 앞부분과 해시 두 개를 `a_b_c` 형식으로 잇습니다[5]. 확장과 암호 모음을 정렬해서 계산하기 때문에 순서만 바뀐 ClientHello 는 같은 JA4 가 나옵니다. JA4S(ServerHello), JA4X(인증서), JA4H(HTTP), JA4SSH, JA4T(TCP) 같은 방법을 묶어 JA4+ 라고 부릅니다[6]. JA4X 는 인증서에 든 값이 아니라 발급자·주체·확장의 OID 목록을 해시해서, 인증서를 어떤 방식으로 만들었는지를 봅니다[9][13]. JA4 는 BSD 3-Clause 로 공개됐고, JA4S·JA4X 같은 JA4+ 는 특허 출원 중이며 FoxIO License 1.1 을 따릅니다[6]. 도구마다 지원 범위가 달라서 JA4 만 계산하고 JA4S 는 없는 제품도 있습니다[6].

두 방법 모두 GREASE 값을 빼고 계산합니다[1][5]. GREASE 는 서버가 특정 값에 기대지 않도록 클라이언트가 섞어 넣는 예약값으로, 확장·그룹·서명 알고리즘·버전에서는 `0x0A0A`, `0x1A1A` … `0xFAFA` 의 16개 값을 씁니다[24]. 같은 브라우저도 연결마다 다른 GREASE 값을 고르므로 이 값을 빼야 지문이 한 가지로 나옵니다.

## 위치와 버전별 차이

지문을 남기는 도구와 필드는 다음과 같습니다. 모든 도구가 기본으로 지문을 남기지는 않으므로, 로그에 필드가 없으면 먼저 설정을 확인합니다.

| 도구 | 필드 | 조건 |
|---|---|---|
| Zeek + Salesforce `ja3` 패키지 | ssl.log `ja3`, `ja3s` (MD5 만) | `zkg install ja3`. 원래 문자열 필드(`ja3_version` 등)는 스크립트의 주석을 풀어야 기록[3] |
| Zeek + FoxIO `ja4` 플러그인 | ssl.log `ja4`, `ja4s`. 원래 목록 필드 `ja4_o`, `ja4_r`, `ja4_ro`, `ja4s_r` | `zkg install zeek/foxio/ja4`, Zeek 7.0 이상. 원래 목록 필드는 빌드 전에 `config.zeek` 의 `JA4_raw`·`JA4S_raw` 를 `T` 로 바꿔야 생김. `FINGERPRINT::JA4X_enabled` 기본값은 `F` 이고 x509.log 의 JA4X 는 아직 지원하지 않음[11] |
| Suricata EVE `tls` 기록 | `tls.ja3.hash`, `tls.ja3.string`, `tls.ja3s.hash`, `tls.ja3s.string`, `tls.ja4` | `app-layer.protocols.tls.ja3-fingerprints`·`ja4-fingerprints` 가 켜져 있고 `extended: yes` 이거나 `custom:` 목록에 넣었을 때[14][15] |
| Suricata EVE `quic` 기록 | `quic.ja3`, `quic.ja3s`, `quic.ja4` | `ja3-fingerprints`·`ja4-fingerprints` 가 켜져 있을 때[14][16] |
| Wireshark·tshark | `tls.handshake.ja3`, `tls.handshake.ja3_full`, `tls.handshake.ja3s`, `tls.handshake.ja3s_full` | 3.6.0 부터 내장[20] |
| Wireshark·tshark | `tls.handshake.ja4`, `tls.handshake.ja4_r` | 4.2.0 부터 내장[20] |
| Wireshark + FoxIO 플러그인 | `ja4.ja4s`, `ja4.ja4x`, `ja4.ja4h`, `ja4.ja4t` 등 | Wireshark 4.4.0 이상[12] |
| nfdump | 출력 형식 `%ja3`·`%ja4`, 통계 `-s ja3`·`-s ja4`·`-s ja4s`, 필터 `payload ja3`·`payload ja4`·`payload ja4s` | nfpcapd 가 `-o payload` 로 연결 첫 패킷의 페이로드를 저장한 흐름만. JA4 는 `./configure --enable-ja4` 로 빌드해야 함(기본은 꺼짐)[22] |
| Salesforce `ja3.py` | JSON 필드 `source_ip`, `destination_ip`, `source_port`, `destination_port`, `ja3`(문자열), `ja3_digest`(MD5), `timestamp` | 기본은 443번 포트만, `-a` 로 모든 포트[2] |
| FoxIO `ja4.py` | 키 `stream`, `src`, `dst`, `srcport`, `dstport`, `domain`, `JA4.1`, `JA4_r.1`, `JA4_o.1`, `JA4_ro.1`, `JA4S`, `JA4X.1` 등 | tshark 4.0.6 이상 권장. `-J` JSON, `-r` 원래 목록, `-o` 원래 순서[7][8] |

Suricata 는 설정 파일에서 `no` 로 명시해 끄지 않았으면, 불러온 규칙이 JA3·JA4 를 쓸 때 계산을 저절로 켭니다. 컴파일할 때 기능을 뺀 빌드도 있습니다[16]. `custom:` 목록을 쓰면 `extended` 가 꺼지므로, 목록에 `ja3`·`ja3s`·`ja4` 가 없으면 필드도 없습니다[15]. EVE 의 다른 TLS 필드와 설정은 [Suricata 프로토콜 기록](../suricata/eve-json/protocol-events.md), Zeek ssl.log 의 다른 필드는 [TLS·인증서 기록](../zeek/zeek-logs/ssl-x509-log.md) 에서 다룹니다.

Suricata 규칙에서는 `ja3.hash`, `ja3.string`, `ja3s.hash`, `ja3s.string`, `ja4.hash` 를 버퍼 키워드로 씁니다. 옛 이름 `ja3_hash` 도 아직 받습니다[16]. Suricata 8.0 부터 `ja3.hash`·`ja3s.hash` 에 16진수가 아닌 내용을 쓴 규칙은 받지 않습니다[17].

## 구조

### JA3 와 JA3S

JA3 는 ClientHello 의 다섯 필드를 다음 순서로 적습니다. 필드 사이는 `,`, 한 필드 안의 값 사이는 `-` 로 잇고, 값은 10진수입니다[1].

```text
SSLVersion,Cipher,SSLExtension,EllipticCurve,EllipticCurvePointFormat
```

`SSLVersion` 은 ClientHello 의 `legacy_version` 이고, `EllipticCurve` 는 supported_groups(10) 확장, `EllipticCurvePointFormat` 은 ec_point_formats(11) 확장의 값입니다[2]. 목록은 ClientHello 에 나온 순서 그대로 쓰고 정렬하지 않습니다[2]. 확장이 없으면 뒤의 필드를 비웁니다. 이 문자열의 MD5 가 32자 16진수 JA3 입니다[1].

```text
769,47-53-5-10-49161-49162-49171-49172-50-56-19-4,0-10-11,23-24-25,0  →  ada70206e40642a3e4461f35503241d5
769,4-5-10-9-100-98-3-6-19-18-99,,,                                  →  de350869b8c85de67a350c8d186f11e6
```

위 두 줄은 JA3 명세에 실린 예입니다[1]. TLS 1.3 클라이언트도 `legacy_version` 에는 `0x0303` 을 넣고 실제 지원 버전은 supported_versions(43) 확장에 넣으므로[23], TLS 1.3 클라이언트의 JA3 문자열도 `771` 로 시작합니다. QUIC 클라이언트의 JA3 문자열도 `771,4865-4866-4867,...` 처럼 `771` 로 시작합니다[14].

JA3S 는 ServerHello 의 `SSLVersion,Cipher,SSLExtension` 을 같은 방식으로 적어 MD5 로 해시한 값입니다[1]. 서버는 클라이언트마다 다르게 응답할 수 있지만 같은 클라이언트에는 늘 같게 응답하므로, JA3 와 JA3S 를 한 쌍으로 보면 클라이언트와 서버 사이의 협상 전체를 식별할 수 있습니다[1].

### JA4

JA4 는 `a_b_c` 세 부분으로 이뤄집니다[5]. 예를 들어 `t13d1516h2_8daaf6152771_e5627efa2ab1` 의 앞부분 `t13d1516h2` 는 다음처럼 읽습니다.

| 자리 | 예 | 뜻 |
|---|---|---|
| 1 | `t` | 전송 방식. `t` TCP 위의 TLS, `q` QUIC, `d` DTLS |
| 2~3 | `13` | TLS 버전. supported_versions 확장이 있으면 GREASE 를 뺀 최댓값, 없으면 ClientHello 의 버전. `13`·`12`·`11`·`10`·`s3`·`s2`, DTLS 는 `d1`·`d2`·`d3`, 모르면 `00` |
| 4 | `d` | SNI 확장이 있으면 `d`(도메인), 없으면 `i`(IP) |
| 5~6 | `15` | 암호 모음 개수(GREASE 제외, 99 넘으면 `99`) |
| 7~8 | `16` | 확장 개수(GREASE 제외, SNI·ALPN 포함, 99 넘으면 `99`) |
| 9~10 | `h2` | 첫 ALPN 값의 첫 글자와 끝 글자. `http/1.1` 이면 `h1`, ALPN 이 없으면 `00` |

버전은 레코드 헤더의 버전을 보지 않습니다. 개수를 셀 때 GREASE 는 빼지만 SCSV(`0x00FF`, `0x5600`) 와 실험용 값(`0xFE00`–`0xFEFF`)은 셉니다[5].

`b` 는 암호 모음을 4자리 소문자 16진수로 적어 16진 순서로 정렬하고 쉼표로 이은 문자열의 SHA256 앞 12자입니다. 암호 모음이 없으면 `000000000000` 입니다[5].

`c` 는 확장을 같은 방식으로 정렬하되 SNI(`0000`)·ALPN(`0010`)을 빼고, 뒤에 `_` 와 서명 알고리즘 목록을 붙인 문자열의 SHA256 앞 12자입니다. 서명 알고리즘은 정렬하지 않고 나온 순서대로 씁니다. 서명 알고리즘이 없으면 `_` 없이 확장 목록만 해시하고, 확장이 없으면 `000000000000` 입니다[5]. SNI·ALPN 은 `a` 에 이미 들어 있어서 뺍니다. 그래서 같은 프로그램이 도메인으로 접속하든 IP 로 접속하든 `c` 는 같습니다[5].

JA4 는 해시 앞의 원래 목록을 보여 주는 형식도 정해 두었습니다[5].

| 이름 | 내용 |
|---|---|
| `JA4_r` | 해시 대신 정렬한 목록을 그대로 씀 |
| `JA4_ro` | 해시 대신 나온 순서 그대로의 목록을 씀. SNI·ALPN 포함 |
| `JA4_o` | 나온 순서 그대로의 목록(SNI·ALPN 포함)을 해시 |

한 연결에서 서버가 HelloRetryRequest 를 보내면 클라이언트는 두 번째 ClientHello 를 보냅니다[23]. `ja4.py` 는 스트림마다 ClientHello 순서대로 `JA4.1`, `JA4.2` 처럼 번호를 붙여 따로 냅니다[8].

### JA4S

JA4S 는 ServerHello 로 만든 지문입니다. `ja4.py` 는 전송 방식·버전·확장 개수·ALPN 을 이은 앞부분, 서버가 고른 암호 모음 하나(4자리 16진수), 확장 목록을 나온 순서대로(정렬하지 않고) 해시한 SHA256 앞 12자를 `_` 로 잇습니다[8]. 예를 들어 `t120300_c030_5e2616a54c73` 은 TCP 위의 TLS 1.2, 확장 3개, ALPN 없음, 암호 모음 `0xC030` 을 고른 응답입니다[6]. JA4 의 버전은 클라이언트가 제안한 최고 버전이고, 실제로 협상된 버전은 JA4S 에 나옵니다.

## 증거로서 의미

**증명하는 것.** 센서가 본 패킷에서, 이 시각에 이 출발지 IP·포트가 이 목적지로 이런 매개변수(버전·암호 모음·확장·ALPN·SNI 유무)를 담은 ClientHello 를 보냈다는 것을 증명합니다. JA3S·JA4S 가 있으면 서버가 ServerHello 로 응답해 핸드셰이크가 그만큼 진행됐다는 것도 알 수 있습니다[1][5]. 같은 지문이 여러 호스트와 여러 시각에 나오면 같은 TLS 라이브러리와 설정을 쓰는 클라이언트일 가능성이 높아서, 연결을 묶고 다른 기록으로 넘어가는 출발점으로 씁니다[6][13]. 실행하는 프로그램이 거의 바뀌지 않는 운영망에서 처음 보는 지문이 나타나면 살펴볼 만한 신호가 됩니다[13].

**증명하지 못하는 것.** 지문은 대체로 프로그램이 아니라 TLS 라이브러리와 설정을 식별합니다. Go 로 만든 프로그램은 다른 Go 프로그램과 JA4 가 같을 가능성이 높고, Python·Java 도 마찬가지입니다[13]. 2015–2016년 샌드박스에서 모은 악성 코드 18개 계열 가운데 10개 계열은 가장 흔한 TLS 클라이언트가 샌드박스 Windows 의 기본 TLS 라이브러리와 같았습니다[27]. 따라서 악성 코드와 정상 프로그램이 같은 지문을 낼 수 있습니다.

지문 하나로 악성 여부를 판단할 수도 없습니다. abuse.ch SSLBL 의 JA3 목록은 악성 코드가 만든 pcap 2,500만 개가 넘는 자료에서 모았지만, 정상 트래픽과 대조하지 않아서 오탐이 많을 수 있습니다[26]. 어느 사용자와 어느 프로세스가 연결했는지는 지문에 없으므로 호스트 기록으로 확인합니다([Windows 메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/), [Windows 크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/)). ClientHello 만 있고 ServerHello 가 없으면 연결이 맺어지지 않았을 수 있고, 지문으로는 주고받은 내용을 알 수 없습니다.

보고서에는 "10.0.0.5 에서 악성 코드가 실행됐다" 가 아니라 "2026-03-02 01:15:30 UTC 에 10.0.0.5:49152 가 203.0.113.5:443 으로 보낸 ClientHello 의 JA4 가 `t13d0306h2_40b44b994229_0d385148b956` 이고, 같은 JA4 가 같은 날 다른 내부 호스트 두 대에서도 기록됐다" 처럼 기록으로 확인되는 만큼만 씁니다(만든 예시).

## 시각 해석

JA3·JA4 값에는 시각이 없습니다. 시각은 지문을 담은 기록에서 읽고, 기록마다 기준이 다릅니다.

| 기록 | 시각 필드 | 기준 |
|---|---|---|
| pcap 을 tshark 로 읽은 결과 | `frame.time_epoch` | ClientHello 패킷이 도착한 시각(에포크 초)[21] |
| `ja3.py` | `timestamp` | ClientHello 를 담은 pcap 레코드의 시각(에포크 초)[2] |
| Zeek ssl.log | `ts` | TLS 연결을 처음 알아챈 시각[19] |
| Suricata EVE | `timestamp` | 이벤트 기록의 시각([Suricata EVE 로그](../suricata/eve-json/index.md)) |
| nfdump | `%ts`·`%te` | 흐름의 처음·마지막 패킷 시각. 지문은 첫 패킷 페이로드로 계산[22] |

Zeek ssl.log 의 `ts` 는 같은 연결의 conn.log `ts`(첫 패킷 시각)와 다릅니다. Zeek 문서 예에서 같은 `uid` 의 conn.log `ts` 는 `1598377391.716515`, ssl.log `ts` 는 `1598377391.921726` 으로 약 0.2초 차이가 납니다[18]. 두 로그를 `uid` 로 이을 때 이 차이를 알고 씁니다. Zeek 로그의 시각은 에포크 초(`1598377391.921726`)로도, `2020-09-16T14:01:26.194646Z` 같은 ISO 8601(UTC) 문자열로도 나옵니다[18]. 형식의 세부는 [Zeek 로그](../zeek/zeek-logs/index.md) 와 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에서 다룹니다.

## 함정과 한계

**JA3 해시는 되돌릴 수 없습니다.** MD5 만 남기면 어떤 매개변수가 달랐는지 알 수 없으므로, 비교하고 설명하려면 원래 문자열(Suricata `ja3.string`, Wireshark `ja3_full`, `ja3.py` 의 `ja3`)을 함께 남깁니다[1][14][20].

**같은 브라우저도 JA3 가 연결마다 바뀔 수 있습니다.** Chromium 은 2023년부터 확장 순서를 무작위로 섞고, 암호 모음 순서를 섞어 JA3 를 피하는 방법(cipher stunting)도 있습니다. JA4 는 정렬해서 이 영향을 줄이고, 대신 서명 알고리즘을 넣어 구별력을 유지합니다[6]. `ja4.py` 문서의 예에서 같은 호스트가 맺은 두 연결은 `JA4_ro` 의 확장 순서가 다르고 `JA4_o` 도 다르지만 JA4 는 `t13d1516h2_8daaf6152771_e5627efa2ab1` 로 같습니다[7]. 암호 모음 하나를 계속 바꾸는 스캐너는 JA3 가 매번 달라지지만 JA4 는 `b` 만 바뀌므로, `a` 와 `c` 만 이은 값(`JA4_ac`)으로 따라갈 수 있습니다[6].

**같은 클라이언트가 늘 같은 JA3 를 내지는 않습니다.** Zeek 문서 예에서 같은 curl 이 두 사이트에는 같은 JA3 를, 다른 한 사이트에는 다른 JA3 를 냈고, 다시 접속해도 결과가 같았습니다. 반대로 서로 다른 두 사이트에서 JA3S 가 같았는데, 두 사이트가 같은 호스팅 회사의 서버를 썼기 때문으로 보입니다[18]. "같은 클라이언트면 같은 JA3", "다른 서버면 다른 JA3S" 로 단정하지 않습니다.

**`771` 이 TLS 1.2 라는 뜻은 아닙니다.** JA3 의 첫 값은 `legacy_version` 이라서 TLS 1.3 클라이언트도 `771` 입니다[23]. JA4 의 버전은 클라이언트가 제안한 최고 버전이고, 서버가 고른 버전은 JA4S 나 Zeek ssl.log 의 `version` 으로 봅니다[19]. FoxIO 시험 데이터 `tls-handshake.pcapng` 에는 JA4 가 `t13d1516h1_…` 인데 JA4S 가 `t120300_c030_…` 인 연결이 있습니다. 서버가 TLS 1.2 를 고른 연결이라서 인증서가 평문으로 오갔고, 그래서 같은 연결에 JA4X 도 나옵니다[8].

**SNI 유무에 따라 JA4 가 두 가지로 나옵니다.** 같은 앱도 도메인으로 접속하면 `d`, IP 로 접속하면 `i` 가 되고 확장 개수도 하나 줄어듭니다. Chromium 은 `t13d1516h2_8daaf6152771_02713d6af862`(SNI 있음)와 `t13i1515h2_8daaf6152771_02713d6af862`(SNI 없음) 두 가지로 나옵니다[10]. `b` 와 `c` 가 같은지로 묶어 봅니다.

**도구마다 계산이 다를 수 있습니다.** 명세는 첫 ALPN 값의 첫·끝 바이트가 영숫자가 아니면 16진 표기의 첫·끝 글자를 쓰라고 정했지만, `ja4.py` 는 128 이상인 바이트를 `9` 로 바꿉니다[5][8]. `ja4.py` 의 버전 표에는 DTLS 값이 없고 전송 방식도 `q`·`t` 만 판정합니다[8]. 도구끼리 JA4 가 맞지 않으면 원래 목록(`JA4_r`)을 비교합니다.

**도구가 ClientHello 를 놓칠 수 있습니다.** `ja3.py` 는 TCP 세그먼트를 하나씩 파싱해서, ClientHello 가 세그먼트 하나에 다 들어 있지 않으면 건너뛰고, 기본으로 443번 포트만 봅니다[2]. nfdump 는 흐름 첫 패킷의 페이로드로만 계산하므로 페이로드를 저장하지 않은 일반 NetFlow·IPFIX 기록에는 지문이 없습니다[22]. 지문이 없다고 ClientHello 가 없었다는 뜻은 아니므로, TCP 를 재조립하는 Zeek·Suricata·Wireshark 결과와 비교합니다.

**로그에 지문이 없다고 TLS 가 없었던 것은 아닙니다.** Zeek 는 패키지를 설치해야 지문을 남기고, Suricata 는 설정과 불러온 규칙에 따라 계산을 켜고 끕니다[3][11][16]. 같은 센서라도 규칙 묶음이 바뀐 시점 앞뒤로 필드가 있다가 없어질 수 있습니다.

**지문은 앱이 갱신되면 바뀝니다.** 앱의 TLS 라이브러리가 갱신되면 JA4 도 바뀌고, 그 주기는 대략 1년에 한 번 정도입니다[6]. 오래전에 만든 지문 목록으로 최근 기록을 비교하면 맞는 것이 없거나 엉뚱한 앱과 맞을 수 있습니다. 지문 목록(Salesforce `osx-nix-ja3.csv`, FoxIO `ja4plus-mapping.csv`)은 앱 이름을 짐작하는 참고 자료로만 씁니다[4][10].

## 직접 분석해 보기

### 헥스로 한 번

아래는 RFC 8446 의 ClientHello 구조대로 만든 레코드 하나입니다(만든 예시). 지문 계산에 쓰는 부분만 담은 예시라서, 실제 TLS 1.3 연결에 필요한 key_share 같은 확장은 없습니다.

```text
오프셋  바이트                                        뜻
0000   16 03 01 00 8c                                레코드: handshake(22), 레코드 버전 0x0301, 길이 140
0005   01 00 00 88                                   핸드셰이크: client_hello(1), 길이 136
0009   03 03                                         legacy_version 0x0303
000b   00 00 ... 00                                  random 32바이트(이 예시는 0으로 채움)
002b   00                                            legacy_session_id 길이 0
002c   00 08                                         암호 모음 목록 길이 8바이트
002e   0a 0a 13 01 13 02 c0 2f                       GREASE, 0x1301, 0x1302, 0xc02f
0036   01 00                                         압축 방법 1개: null(0)
0038   00 57                                         확장 전체 길이 87바이트
003a   3a 3a 00 00                                   GREASE 확장(빈 값)
003e   00 00 00 14 00 12 00 00 0f 77 77 77 2e 65 78  server_name(0): www.example.com
       61 6d 70 6c 65 2e 63 6f 6d
0056   00 0a 00 08 00 06 0a 0a 00 1d 00 17           supported_groups(10): GREASE, 0x001d, 0x0017
0062   00 0b 00 02 01 00                             ec_point_formats(11): 0
0068   00 0d 00 08 00 06 04 03 08 04 04 01           signature_algorithms(13): 0403, 0804, 0401
0074   00 10 00 0e 00 0c 02 68 32 08 68 74 74 70 2f  ALPN(16): "h2", "http/1.1"
       31 2e 31
0086   00 2b 00 07 06 7a 7a 03 04 03 03              supported_versions(43): GREASE, 0x0304, 0x0303
```

확장은 2바이트 종류와 2바이트 길이 뒤에 값이 오는 모양이라서, `0x003a` 부터 길이를 따라 건너뛰면 확장 7개를 차례로 읽을 수 있습니다[23]. server_name 값은 목록 길이(`00 12`), 이름 종류 host_name(`00`), 이름 길이(`00 0f`), ASCII 이름 순서로 들어 있습니다[25]. `0a0a`·`3a3a`·`7a7a` 는 GREASE 라서 모두 뺍니다[24].

JA3 는 이 값을 10진수로 옮겨 적습니다. 버전 `0x0303` 은 771, 암호 모음은 4865·4866·49199, 확장은 나온 순서대로 0·10·11·13·16·43, 곡선은 29·23, 점 형식은 0 입니다.

```text
771,4865-4866-49199,0-10-11-13-16-43,29-23,0  →  c9e264cb3675678ee364e81f3b6da7ad
```

JA4 의 `a` 는 TCP 위의 TLS(`t`), supported_versions 의 최댓값 `0x0304`(`13`), SNI 있음(`d`), 암호 모음 3개(`03`), 확장 6개(`06`), 첫 ALPN `h2` 를 이어 `t13d0306h2` 입니다. `b` 는 `1301,1302,c02f` 의 SHA256 앞 12자 `40b44b994229` 이고, `c` 는 SNI·ALPN 을 뺀 `000a,000b,000d,002b` 뒤에 서명 알고리즘 `0403,0804,0401` 을 붙인 문자열의 SHA256 앞 12자 `0d385148b956` 입니다.

```text
JA4   = t13d0306h2_40b44b994229_0d385148b956
JA4_r = t13d0306h2_1301,1302,c02f_000a,000b,000d,002b_0403,0804,0401
```

같은 ClientHello 에서 server_name 과 supported_groups 의 순서만 바꾸면 JA3 문자열이 `771,4865-4866-49199,10-0-11-13-16-43,29-23,0` 이 되어 MD5 가 `f78b245dcbeab13b21d5faaa59e1e054` 로 바뀌지만, JA4 는 정렬 뒤에 계산하므로 그대로입니다. server_name 확장을 빼면 JA4 는 `t13i0305h2_40b44b994229_0d385148b956` 로 `a` 만 바뀝니다. 해시는 셸에서 바로 다시 계산해 볼 수 있습니다.

```sh
printf '%s' '771,4865-4866-49199,0-10-11-13-16-43,29-23,0' | md5sum
printf '%s' '1301,1302,c02f' | sha256sum | cut -c1-12
printf '%s' '000a,000b,000d,002b_0403,0804,0401' | sha256sum | cut -c1-12
```

명세의 예 문자열(`002f,0035,009c,…`)을 같은 방법으로 해시하면 `8daaf6152771`·`e5627efa2ab1` 이 나오는지도 확인할 수 있습니다[5].

### 공개 도구로 한 번

tshark 로 ClientHello(`tls.handshake.type == 1`)만 골라 시각·주소·SNI·지문을 한 줄씩 뽑습니다[20][21]. JA4 필드는 Wireshark 4.2.0 이상에서 나옵니다.

```sh
tshark -r capture.pcapng -Y "tls.handshake.type == 1" -T fields \
  -e frame.time_epoch -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport \
  -e tls.handshake.extensions_server_name \
  -e tls.handshake.ja3 -e tls.handshake.ja3_full -e tls.handshake.ja4 -e tls.handshake.ja4_r
```

ServerHello 는 `tls.handshake.type == 2` 로 골라 `tls.handshake.ja3s`·`tls.handshake.ja3s_full` 을 뽑습니다. QUIC 패킷은 `tcp.srcport` 같은 TCP 필드가 비어서 나옵니다[12].

Zeek 는 JA4 플러그인을 설치한 뒤 같은 pcap 을 돌리고, ssl.log 에서 지문과 연결 정보를 함께 봅니다(JSON 로그일 때)[11].

```sh
zeek -C -r capture.pcapng
jq -r '[.ts, .uid, ."id.orig_h", ."id.resp_h", .server_name, .version, .ja4, .ja4s] | @tsv' ssl.log
```

Suricata EVE 에서는 `tls` 기록만 골라 지문별 개수를 셉니다[14].

```sh
jq -r 'select(.event_type=="tls") | .tls.ja4' eve.json | sort | uniq -c | sort -rn
jq -c 'select(.event_type=="tls") | [.timestamp, .src_ip, .dest_ip, .tls.sni, .tls.ja3.string, .tls.ja4]' eve.json
```

nfpcapd 로 페이로드를 저장한 흐름 파일에서는 JA3 를 계산할 수 있는 흐름만 골라 통계를 냅니다[22].

```sh
nfdump -r flowfile -s ja3 -n 0 'payload ja3 defined'
nfdump -r flowfile -o 'fmt:%ts %te %sap -> %dap %ja3' 'payload ja3 defined'
```

같은 연결의 지문이 도구마다 다르면 원래 문자열(`ja3_full`, `ja3.string`, `JA4_r`)을 나란히 놓고 어느 값에서 갈리는지 확인합니다.

## 교차 검증

Zeek 에서는 같은 `uid` 로 [conn.log](../zeek/zeek-logs/conn-log.md) 를 찾아 연결이 맺어졌는지, 몇 바이트가 오갔는지 봅니다. ssl.log 의 `established` 는 핸드셰이크가 끝났는지를, `ssl_history` 는 핸드셰이크 메시지의 순서를 보여 줍니다(`C` client_hello, `S` server_hello, 클라이언트가 보낸 것은 대문자)[19]. 서버가 TLS 1.2 이하를 고른 연결이면 [인증서](certificates.md) 도 함께 봅니다.

SNI 에 적힌 도메인은 [DNS](../../03-techniques/analysis/dns-analysis.md) 질의·응답과 비교해, 그 IP 를 얻으려고 DNS 를 물었는지 확인합니다. 프록시를 거치는 환경이면 [웹 프록시 로그](../devices/proxy-logs.md) 의 CONNECT 기록과 시각을 맞춰 봅니다. 같은 지문이 일정한 간격으로 되풀이되면 [비컨 찾기](../../03-techniques/analysis/beaconing.md) 로 넘어갑니다.

지문으로 묶은 호스트에서 어느 프로세스가 연결했는지는 호스트 기록으로 확인합니다([Windows 라이브 응답](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/live-response/), [Linux 라이브 응답 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/live-response.html)). 같은 호스트의 평문 HTTP User-Agent 로 짐작한 브라우저와 TLS 매개변수가 맞지 않으면 침해 지표가 될 수 있습니다[27]. 암호화 트래픽을 전체적으로 분석하는 순서는 [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md), C2 통신을 확인하는 흐름은 [악성 코드가 C2 서버와 통신했나](../../04-scenarios/intrusion/c2-communication.md) 에서 다룹니다.

## 실습

FoxIO JA4 저장소의 `pcap/` 폴더에는 시험용 캡처가 있고, `python/test/testdata/` 에는 각 캡처를 `python3 ja4.py x.pcap -J -r -o -f out.json` 으로 돌린 기대 결과 JSON 이 있습니다[8].

1. `tls-sni.pcapng` 를 tshark 로 읽어 `tls.handshake.ja4` 를 뽑고, `testdata/tls-sni.pcapng.json` 의 `JA4.1` 과 스트림별로 비교합니다.
2. 같은 파일에서 JA4 가 같은 스트림들의 `JA4_ro.1` 을 비교해, 확장 순서가 연결마다 다른지 확인합니다. 이 스트림들의 JA3 는 같은지 tshark 로 확인합니다.
3. `tls-handshake.pcapng` 의 기대 결과에서 JA4 의 버전과 JA4S 의 버전이 다른 스트림을 찾고, 그 스트림에 JA4X 가 있는 이유를 설명합니다.
4. `tls-non-ascii-alpn.pcapng` 를 tshark(Wireshark 4.2.0 이상)와 `ja4.py` 로 각각 계산해 `a` 부분의 ALPN 두 글자가 같은지 비교합니다.
5. 같은 pcap 을 Zeek(JA4 플러그인)로 돌려 ssl.log 의 `ts` 와 tshark 의 ClientHello `frame.time_epoch` 가 얼마나 다른지 계산합니다.

## 참고 문헌

1. Salesforce, JA3 README. https://github.com/salesforce/ja3/blob/master/README.md
2. Salesforce, `python/ja3/ja3.py`. https://github.com/salesforce/ja3/blob/master/python/ja3/ja3.py
3. Salesforce, JA3 Zeek 스크립트 README·`ja3.zeek`. https://github.com/salesforce/ja3/blob/master/zeek/README.md , https://github.com/salesforce/ja3/blob/master/zeek/ja3.zeek
4. Salesforce, JA3 lists README. https://github.com/salesforce/ja3/blob/master/lists/README.md
5. FoxIO, "JA4: TLS Client Fingerprinting". https://github.com/FoxIO-LLC/ja4/blob/main/technical_details/JA4.md
6. FoxIO, JA4+ README. https://github.com/FoxIO-LLC/ja4/blob/main/README.md
7. FoxIO, JA4+ Python 구현 README. https://github.com/FoxIO-LLC/ja4/blob/main/python/README.md
8. FoxIO, `python/ja4.py`·`common.py`·시험 데이터. https://github.com/FoxIO-LLC/ja4/blob/main/python/ja4.py , https://github.com/FoxIO-LLC/ja4/blob/main/python/common.py , https://github.com/FoxIO-LLC/ja4/tree/main/python/test/testdata , https://github.com/FoxIO-LLC/ja4/tree/main/pcap
9. FoxIO, `python/ja4x.py`. https://github.com/FoxIO-LLC/ja4/blob/main/python/ja4x.py
10. FoxIO, `ja4plus-mapping.csv`. https://github.com/FoxIO-LLC/ja4/blob/main/ja4plus-mapping.csv
11. FoxIO, JA4+ for Zeek README·`config.zeek`·`ja4/main.zeek`. https://github.com/FoxIO-LLC/ja4/blob/main/zeek/README.md , https://github.com/FoxIO-LLC/ja4/blob/main/zeek/scripts/fingerprints/config.zeek , https://github.com/FoxIO-LLC/ja4/blob/main/zeek/scripts/fingerprints/ja4/main.zeek
12. FoxIO, JA4+ Wireshark 플러그인 README. https://github.com/FoxIO-LLC/ja4/blob/main/wireshark/README.md
13. John Althouse, "JA4+ Network Fingerprinting", FoxIO 블로그. https://blog.foxio.io/ja4%2B-network-fingerprinting
14. OISF, Suricata User Guide — EVE JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
15. OISF, Suricata User Guide — EVE JSON Output. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
16. OISF, Suricata User Guide — JA3/JA4 Keywords. https://github.com/OISF/suricata/blob/main/doc/userguide/rules/ja-keywords.rst
17. OISF, Suricata User Guide — Upgrading. https://github.com/OISF/suricata/blob/main/doc/userguide/upgrade.rst
18. Zeek 문서, "ssl.log". https://github.com/zeek/zeek-docs/blob/master/logs/ssl.rst
19. Zeek 스크립트 참조, "base/protocols/ssl/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/main.zeek.rst
20. Wireshark, Display Filter Reference: Transport Layer Security. https://www.wireshark.org/docs/dfref/t/tls.html
21. Wireshark, Display Filter Reference: Frame. https://www.wireshark.org/docs/dfref/f/frame.html
22. nfdump 매뉴얼 `nfdump.1`·`nfpcapd.1`, README. https://github.com/phaag/nfdump/blob/master/man/nfdump.1 , https://github.com/phaag/nfdump/blob/master/man/nfpcapd.1 , https://github.com/phaag/nfdump/blob/master/README.md
23. E. Rescorla, "The Transport Layer Security (TLS) Protocol Version 1.3", RFC 8446, 2018. https://www.rfc-editor.org/rfc/rfc8446.txt
24. D. Benjamin, "Applying Generate Random Extensions And Sustain Extensibility (GREASE) to TLS Extensibility", RFC 8701, 2020. https://www.rfc-editor.org/rfc/rfc8701.txt
25. D. Eastlake 3rd, "Transport Layer Security (TLS) Extensions: Extension Definitions", RFC 6066, 2011. https://www.rfc-editor.org/rfc/rfc6066.txt
26. abuse.ch, SSL Blacklist. https://sslbl.abuse.ch/ , https://sslbl.abuse.ch/blacklist/
27. Blake Anderson, Subharthi Paul, David McGrew, "Deciphering malware's use of TLS (without decryption)", Journal of Computer Virology and Hacking Techniques, 2018. doi:10.1007/s11416-017-0306-6
