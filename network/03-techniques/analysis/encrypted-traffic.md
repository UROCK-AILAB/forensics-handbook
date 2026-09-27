---
title: "암호화된 트래픽 분석"
parent: "기법 · 분석"
nav_order: 380
---

# 암호화된 트래픽 분석 (Encrypted Traffic)

HTTPS·QUIC·SSH 처럼 암호화된 연결은 주고받은 내용을 볼 수 없지만, 암호화가 시작되기 전의 핸드셰이크와 연결의 시각·크기·방향은 평문으로 남습니다. 이 페이지에서는 이 두 가지로 어느 호스트가 언제 어떤 이름의 서버와 어떤 방식으로 통신했는지를 확인하는 순서를 다루고, 조사 대상 환경에 TLS 키 로그 파일이 이미 있을 때 그 파일을 읽고 캡처에 적용하는 방법까지 설명합니다. 결과는 "이런 핸드셰이크와 흐름 기록이 있다" 까지만 증명하고, 무엇을 보냈는지는 증명하지 못합니다.

## 언제 쓰나

인터넷 트래픽 가운데 암호화된 비율은 2017년 약 55% 에서 2020년 약 85% 로 늘었고[16], 웹 접속·클라우드 업로드·원격 접속은 대부분 암호화된 연결로 남습니다. 그래서 "이 PC 가 이 서비스에 접속했는가", "이 연결이 악성 코드의 통신과 같은 방식인가", "이 시간대에 밖으로 많이 보냈는가" 같은 질문에는 내용 대신 핸드셰이크 값과 흐름의 모양으로 답해야 합니다. 핸드셰이크 메시지의 구조는 [TLS와 인증서](../../01-foundations/protocols/tls.md)에 있습니다.

프로토콜마다 평문으로 남는 범위가 다릅니다. 먼저 조사할 연결이 어느 분류인지 확인합니다.

| 연결 | 평문으로 보이는 것 | 보이지 않는 것 |
|---|---|---|
| TLS 1.2 이하 | ClientHello·ServerHello(SNI, 제안한 암호 스위트·확장, 서버가 고른 버전·암호), 서버 인증서 | 응용 데이터 전체 |
| TLS 1.3 | ClientHello·ServerHello. ServerHello 뒤의 핸드셰이크 메시지는 모두 암호화됩니다[1] | 서버 인증서. Zeek ssl.log 에 인증서 관련 값이 남지 않습니다[3] |
| ESNI·ECH 를 쓴 TLS | 버전·암호·곡선 | SNI. Zeek ssl.log 에 `server_name` 이 없습니다[3] |
| QUIC | Zeek 6.1 부터 quic.log 에 `version`, `client_initial_dcid`, `server_scid`, `server_name`, `client_protocol`(ALPN 첫 값), `history`[6] | 응용 데이터 전체 |
| SSH | 양쪽이 보낸 버전 문자열, 알고리즘 협상 | 명령·파일. 인증 결과는 암호화된 패킷의 크기로 추정한 값만 있습니다[7] |
| DNS over TLS·HTTPS | 853번 포트 연결[18]이나 DoH 서버로 가는 HTTPS 연결 | 질의한 이름. [DNS](../../01-foundations/protocols/dns.md) 참고 |

## 절차

### 1. 암호화된 연결을 흐름 기록과 함께 목록으로 정리한다

조사 시간대의 TLS·QUIC·SSH 연결을 뽑고, 연결마다 시각·양 끝 주소와 포트·보낸 바이트와 받은 바이트·지속 시간을 함께 적습니다. Zeek 는 ssl.log 와 conn.log 에 같은 `uid` 를 쓰므로 둘을 이어 한 줄로 만들 수 있고, conn.log 의 `service` 가 `ssl` 이면 TLS 로 판별한 연결입니다[3]. conn.log 필드는 [연결 기록](../../02-artifacts/zeek/zeek-logs/conn-log.md)에, Suricata 의 `tls`·`flow` 기록은 [프로토콜 기록](../../02-artifacts/suricata/eve-json/protocol-events.md)에 있습니다. 패킷 캡처만 있으면 tshark 로 ClientHello(핸드셰이크 종류 1)만 골라 같은 목록을 만듭니다[1][10][13].

```
tshark -r case.pcapng -Y "tls.handshake.type == 1" -T fields -e frame.time_epoch -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e tls.handshake.extensions_server_name -e tls.handshake.extensions_alpn_str -e tls.handshake.ja4
```

`tls.handshake.ja4` 는 Wireshark 4.2.0 부터 있는 필드입니다[10]. 흐름 기록만 있을 때의 분석은 [흐름 기록 분석](flow-analysis.md)에서 다룹니다.

### 2. 핸드셰이크 값으로 서버 이름과 버전을 확인한다

SNI 는 클라이언트가 접속하려는 서버의 이름을 ClientHello 에 적은 값입니다. 명세상 끝에 점이 없는 ASCII 도메인 이름이어야 하고, IPv4·IPv6 주소를 그대로 넣을 수 없습니다[2]. 그래서 SNI 가 없는 연결은 IP 로 바로 접속했거나 SNI 를 암호화했을 가능성이 있고, 이런 연결은 5단계에서 따로 봅니다.

버전은 레코드나 ClientHello 의 버전 필드로 판단하지 않습니다. TLS 1.3 은 ClientHello·ServerHello 의 `legacy_version` 을 0x0303(TLS 1.2)으로 고정하고, 실제 버전을 supported_versions 확장으로 알립니다[1]. 서버가 고른 버전은 Zeek ssl.log 의 `version` 이나 Wireshark 의 `tls.handshake.extensions.supported_version` 으로 확인합니다[4][10]. `established` 가 F 이면 핸드셰이크가 끝까지 성립하지 않은 연결입니다[4]. 각 필드의 뜻과 `ssl_history` 글자표는 [TLS·인증서 기록](../../02-artifacts/zeek/zeek-logs/ssl-x509-log.md)에 있습니다.

### 3. TLS 1.2 이하 연결은 서버 인증서를 확인한다

TLS 1.2 이하에서는 서버 인증서가 평문으로 오가므로 주체·발급자·유효 기간·SAN 과 지문을 볼 수 있습니다. Zeek 의 `sni_matches_cert` 로 SNI 와 인증서의 이름이 맞는지도 확인하고, 클라이언트가 SNI 를 보내지 않았으면 이 필드는 비어 있습니다[4]. 같은 지문의 인증서를 쓴 다른 서버를 찾는 방법은 [인증서로 서버 알아보기](../../02-artifacts/fingerprints/certificates.md)에 있습니다.

### 4. 클라이언트 지문으로 연결을 묶는다

JA3·JA4 로 같은 TLS 라이브러리와 설정을 쓰는 연결을 묶고, 처음 보는 지문이 나온 호스트를 추립니다. 계산 방법과 도구별 필드는 [TLS 지문 (JA3·JA4)](../../02-artifacts/fingerprints/ja3-ja4.md)에 있습니다. JA4 는 앱의 TLS 라이브러리가 갱신되면 대략 1년에 한 번 정도 바뀌므로[8], 예전에 만든 지문 목록과 맞지 않는다고 다른 프로그램이라고 판단하지 않습니다. SSH 는 Zeek HASSH 패키지를 올린 센서라면 ssh.log 에 `hassh`·`hasshServer` 가 남아 같은 방식으로 묶을 수 있습니다[19].

### 5. 서버 이름이 없는 연결은 다른 기록과 비교한다

ESNI·ECH 를 쓰고 DNS 까지 DoH 로 보낸 접속은 ssl.log 에 `server_name` 이 없고 dns.log 에도 서버 이름을 알려 주는 기록이 없습니다[3]. 이때 네트워크 기록으로 남는 것은 목적지 IP 와 포트, 흐름의 크기와 시각입니다. 목적지 IP 는 같은 시간대의 다른 호스트가 남긴 DNS 응답, 프록시 로그, 과거 인증서 기록에서 이름을 찾아 비교합니다. 방법은 [DNS 분석](dns-analysis.md)과 [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md)에 있습니다. 어느 프로그램이 연결했는지는 호스트 기록으로 확인해야 하고, Windows 에서는 [메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/)이 그 출발점입니다.

### 6. 크기와 시간의 모양을 본다

내용을 풀 수 없어도 보낸 바이트와 받은 바이트의 비율, 연결 간격, 지속 시간은 그대로 남습니다. 받은 양보다 보낸 양이 훨씬 큰 연결은 업로드 후보이고([자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration.md)), 일정한 간격으로 되풀이되는 작은 연결은 비컨 후보입니다([비컨 찾기](beaconing.md)). Zeek 가 SSH 인증 성공 여부를 판단하는 방법도 암호화된 패킷의 크기 분석이고, 조금이라도 의심스러우면 판단하지 않습니다[7]. SSH 로그인 시도를 해석하는 법은 [비밀번호를 무작위로 넣어 봤나](../../04-scenarios/intrusion/brute-force.md)에 있습니다.

### 7. 조사 대상에 키 로그 파일이 이미 있으면 형식을 확인하고 적용한다

TLS 키 로그 파일(SSLKEYLOGFILE)은 연결마다의 비밀을 적은 텍스트 파일이고, 형식은 RFC 9850(2025년 12월)에 정리되어 있습니다[14]. 파일은 UTF-8 이고 BOM 이 없으며, 빈 줄과 `#` 으로 시작하는 줄은 무시합니다. 나머지 줄은 한 줄에 비밀 하나이고, `레이블 client_random 비밀` 세 값을 공백 하나로 구분합니다[14]. client_random 은 ClientHello 의 Random 32바이트를 헥스 64글자로 쓴 값이고, 비밀은 비밀의 크기에 따라 길이가 다른 헥스입니다. 두 값 모두 대문자와 소문자가 섞일 수 있습니다[14].

| 레이블 | 쓰는 버전 | 담긴 비밀 |
|---|---|---|
| `CLIENT_RANDOM` | TLS 1.2 이하 | 마스터 시크릿(48바이트, 헥스 96글자)[14][15] |
| `CLIENT_HANDSHAKE_TRAFFIC_SECRET`, `SERVER_HANDSHAKE_TRAFFIC_SECRET` | TLS 1.3 | 핸드셰이크 트래픽 비밀[14] |
| `CLIENT_TRAFFIC_SECRET_0`, `SERVER_TRAFFIC_SECRET_0` | TLS 1.3 | 첫 응용 데이터 트래픽 비밀[14] |
| `CLIENT_EARLY_TRAFFIC_SECRET`, `EARLY_EXPORTER_SECRET`, `EXPORTER_SECRET` | TLS 1.3 | 0-RTT 조기 데이터와 exporter 비밀[14] |
| `ECH_SECRET`, `ECH_CONFIG` | ECH | 안쪽 ClientHello(Inner ClientHello)를 HPKE 로 암호화할 때 쓴 공유 비밀과 ECH 설정. 늘 바깥 ClientHello(Outer ClientHello)의 Random 을 씁니다[14] |
| `RSA` | 옛 NSS 형식 | 프리마스터 시크릿. NSS 3.34 에서 없어졌습니다[15] |

TLS 1.3 비밀의 헥스 길이는 암호 스위트의 해시에 따라 SHA256 이면 64글자, SHA384 이면 96글자, SHA512 이면 128글자입니다[15]. 아래는 형식만 보여 주는 만든 예시입니다.

```
# 만든 예시
CLIENT_RANDOM a1b2c3d4a1b2c3d4a1b2c3d4a1b2c3d4a1b2c3d4a1b2c3d4a1b2c3d4a1b2c3d4 0f1e2d3c4b5a69780f1e2d3c4b5a69780f1e2d3c4b5a69780f1e2d3c4b5a69780f1e2d3c4b5a69780f1e2d3c4b5a6978
CLIENT_TRAFFIC_SECRET_0 5e6f70815e6f70815e6f70815e6f70815e6f70815e6f70815e6f70815e6f7081 9c8b7a6f9c8b7a6f9c8b7a6f9c8b7a6f9c8b7a6f9c8b7a6f9c8b7a6f9c8b7a6f
```

줄에는 시각도, 주소도, 암호 스위트도 없습니다[14]. 그래서 어느 연결의 비밀인지는 client_random 을 캡처의 ClientHello Random(`tls.handshake.random`)과 맞춰서 찾고[10], 1단계의 tshark 명령에 `-e tls.handshake.random` 을 더해 연결 목록과 이으면 됩니다. 다만 ECH 가 성립한 연결에서는 TLS 1.3 레이블 줄에 안쪽 ClientHello 의 Random 이 들어가므로[14], 캡처에 보이는 바깥 ClientHello 의 Random 과 맞지 않습니다. 도구마다 헥스를 콜론으로 나누거나 대문자로 쓸 수 있으므로 구분자를 지우고 소문자로 맞춘 뒤 비교합니다.

Wireshark 는 환경설정의 `tls.keylog_file`((Pre)-Master-Secret log filename)에 이 파일을 지정하면 복호화하고, TCP 설정의 "Allow subdissector to reassemble TCP streams"(기본 켜짐)와 "Reassemble out-of-order segments"(3.0 부터, 기본 꺼짐)를 함께 켜야 합니다[11]. tshark 에서는 `-o` 로 같은 설정을 줍니다[13].

```
tshark -r case.pcapng -o "tls.keylog_file:keys.txt" -Y "http or http2" -T fields -e frame.time_epoch -e ip.dst -e http.host -e http.request.uri
```

키를 캡처 파일에 넣어 함께 넘기려면 `editcap --inject-secrets tls,keys.txt in.pcap out-dsb.pcapng` 을 씁니다. 결과는 pcapng 의 Decryption Secrets Block(DSB)에 키가 들어간 새 파일이고(Wireshark 3.0 부터), 받는 사람은 설정을 바꾸지 않고 복호화할 수 있습니다[11][12]. 들어 있는 DSB 를 꺼낼 때는 `--extract-secrets`, 지울 때는 `--discard-all-secrets` 를 씁니다[12]. 원본 캡처는 그대로 두고, 새로 만든 파일과 키 파일의 해시를 따로 기록합니다. 파일 가공 순서는 [큰 캡처 파일 다루기](../acquisition/large-captures.md)에 있습니다.

키 로그 파일 말고도 서버의 RSA 개인 키로 복호화할 수 있지만 조건이 까다롭습니다. 서버가 고른 암호 스위트가 (EC)DHE 가 아니고, 버전이 SSLv3~TLS 1.2 이고, 키가 서버 인증서와 맞고, 세션을 재개하지 않아 ClientKeyExchange 가 있는 연결이어야 합니다. TLS 1.3 은 이 방법으로 풀리지 않습니다[11].

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| Zeek | ssl.log·x509.log(TLS), quic.log(QUIC, 6.1 부터), ssh.log(SSH)[4][5][6][7] |
| Suricata | EVE `tls`·`quic`·`ssh` 기록[9] |
| Wireshark·tshark | `tls.handshake.*` 필드로 핸드셰이크 읽기, `tls.ech.*` 필드로 ECH 확장 보기(4.2.0 부터)[10], 키 로그 파일로 복호화[11] |
| editcap | 키 로그를 DSB 로 넣고 빼기[12] |
| JA3·JA4 도구 | 지문 계산. [TLS 지문 (JA3·JA4)](../../02-artifacts/fingerprints/ja3-ja4.md) 참고 |

Wireshark 위키에는 키가 들어간 TLS 1.2 시험 캡처(`tls12-dsb.pcapng`)가 올라 있어서, 7단계의 복호화 결과를 실제 데이터로 따라가 볼 수 있습니다[11].

## 함정과 한계

**인증서가 없는 것이 정상인 연결이 많습니다.** TLS 1.3 은 인증서를 암호화하고[1], 세션을 재개한 연결은 인증서를 다시 보내지 않습니다. Suricata 는 세션 ID 로 재개한 연결에 `session_resumed` 를 true 로 쓰고 `subject`·`issuer` 를 쓰지 않습니다[9]. Zeek 는 기본으로 인증서 중복을 없애서, 한 번 기록한 인증서는 `X509::relog_known_certificates_after`(기본 1일)가 지나야 x509.log 에 다시 씁니다[5]. "x509.log 에 인증서가 없다" 는 "인증서를 주고받지 않았다" 는 뜻이 아닙니다.

**`771`·`0x0303` 이 TLS 1.2 라는 뜻은 아닙니다.** TLS 1.3 도 `legacy_version` 은 0x0303 입니다[1]. JA3 문자열의 첫 값이나 레코드 버전만 보고 버전을 적지 않습니다.

**SNI 는 클라이언트가 적은 값입니다.** SNI 에 적힌 이름의 서버가 실제로 응답했다는 보장은 없습니다. TLS 1.2 이하에서는 `sni_matches_cert` 로 인증서와 비교할 수 있지만[4], TLS 1.3 에서는 인증서가 보이지 않아 이 비교를 할 수 없습니다.

**같은 클라이언트도 지문이 하나로 고정되지 않습니다.** 같은 curl 로 TLS 1.3 사이트 세 곳에 접속한 Zeek 문서의 예에서 두 곳은 JA3 가 같았지만 한 곳은 달랐고, 다시 접속해도 같은 결과가 나왔습니다[3]. 지문이 다르다고 다른 프로그램이라고 단정하지 않습니다.

**엔트로피만으로 암호화 여부를 판단하면 틀립니다.** IoT 기기 32대를 시험한 연구에서 섀넌 엔트로피 7 이하(0~8 척도)를 평문 후보로 삼았더니, TLS 를 쓰면서 데이터를 인코딩만 한 전구는 엔트로피가 낮게 나왔고, 영상을 압축해 평문 HTTP 로 보내는 카메라 두 대는 높게 나왔습니다[17]. 같은 연구에서 평소에는 암호화된 채널을 쓰는 일부 기기가 움직임을 감지한 영상이나 업데이트 때의 식별 정보는 평문으로 보냈습니다[17]. "443번 포트니까 암호화" 나 "엔트로피가 높으니 암호화" 로 판단하지 않고, 핸드셰이크가 있는지 먼저 확인합니다.

**SSH 압축을 쓰면 인증 결과를 믿을 수 없습니다.** Zeek 는 `zlib`·`zlib@openssh.com` 압축을 쓴 연결에서 인증 성공 여부를 정확히 판단하지 못합니다[7]. 또 기본값 `SSH::disable_analyzer_after_detection = T` 라서 판별이 끝나면 분석기를 뗍니다[7].

**Zeek 버전마다 인증서 연결 필드 이름이 다릅니다.** 문서 예시는 `cert_chain_fuids`(파일 ID)를 쓰고 현재 스크립트는 `cert_chain_fps`(지문)를 씁니다[3][4]. 실제 로그의 `#fields` 줄이나 JSON 키로 확인합니다. 바뀐 버전은 [TLS·인증서 기록](../../02-artifacts/zeek/zeek-logs/ssl-x509-log.md)에 정리되어 있습니다.

**키가 일부만 있으면 풀리지 않을 수 있습니다.** 2024년 기준으로 Wireshark 같은 도구는 TLS 1.3 트래픽을 모든 키 자료가 있을 때만 복호화합니다[16]. 키 로그의 비밀에는 암호 스위트나 다른 연결 정보가 붙어 있지 않아서, 비밀을 쓰려면 핸드셰이크 기록이 필요할 수 있습니다[14]. 캡처가 핸드셰이크 뒤부터 시작했으면 키가 있어도 풀리지 않을 가능성이 있습니다.

**키 로그 파일에는 캡처와 관계없는 연결의 비밀도 들어 있습니다.** 파일을 그대로 DSB 로 넣어 넘기면 다른 연결의 비밀까지 함께 넘어가므로, 필요한 비밀만 골라 넣습니다[11]. Wireshark 4.2 부터 "Export TLS Session Keys" 로 내보낸 파일은 현재 캡처의 패킷이 참조하는 비밀만 담습니다[11].

## 결과를 어떻게 해석하나

**증명하는 것.** 연결 시각, 양 끝 주소와 포트, 주고받은 바이트 수, 클라이언트가 SNI 에 적은 서버 이름(ECH·ESNI 를 쓰지 않았을 때), 협상한 버전과 암호, TLS 1.2 이하라면 서버가 보낸 인증서, 클라이언트 TLS 구현의 지문입니다. 키 로그 파일로 복호화했다면 그 연결에서 오간 HTTP 요청과 응답도 확인됩니다.

**증명하지 못하는 것.** 키가 없는 연결의 내용, URL 경로, 주고받은 파일 이름은 알 수 없습니다. SNI 에 적힌 이름의 서버가 실제로 응답했다는 것, 지문이 같으니 같은 악성 코드라는 것, 어느 사용자나 프로세스가 연결을 만들었는지도 네트워크 기록만으로는 증명하지 못합니다. 세션을 재개한 연결과 TLS 1.3 연결의 서버 인증서도 알 수 없습니다.

**시각.** Zeek ssl.log 의 `ts` 는 SSL 연결을 처음 감지한 시각이라서[4] 같은 연결의 conn.log `ts` 보다 조금 늦습니다. Zeek 문서의 TLS 1.3 예에서 conn.log 는 `1598983678.546522`, ssl.log 는 `1598983678.585087` 입니다[3]. tshark 의 `frame.time_epoch` 는 패킷을 캡처한 시각입니다. 키 로그 파일의 줄에는 시각이 없으므로[14], 파일이 언제 만들어졌는지는 호스트의 파일 시스템 시각으로 따로 확인합니다. 시각 기준의 차이는 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)에 있습니다.

**키 로그 파일이 있다는 것 자체.** SSLKEYLOGFILE 형식은 TLS 가 시험 데이터만 보호하는 시스템용이고, 운영 시스템에서는 쓰면 안 됩니다(MUST NOT)[14]. 파일을 손에 넣은 사람은 거기 적힌 모든 연결의 기밀성과 무결성을 깨뜨릴 수 있고, 이미 저장해 둔 암호화 트래픽도 풀 수 있습니다[14]. 업무용 PC 나 서버에서 이 파일이 나오면, 어느 프로그램이 언제부터 파일을 썼고 누가 읽을 수 있었는지를 호스트 기록으로 확인합니다.

보고서에는 "피의자가 클라우드에 파일을 올렸다" 가 아니라 "2026-03-02 10:14:05 UTC 에 10.0.0.15 가 203.0.113.40:443 과 SNI `upload.example.com` 으로 TLS 1.3 핸드셰이크를 마쳤고, 이 연결에서 약 48MB 를 보내고 약 20KB 를 받은 흐름 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다(만든 예시).

## 참고 문헌

1. E. Rescorla, 「The Transport Layer Security (TLS) Protocol Version 1.3」, RFC 8446. https://www.rfc-editor.org/rfc/rfc8446.txt
2. D. Eastlake 3rd, 「Transport Layer Security (TLS) Extensions: Extension Definitions」, RFC 6066. https://www.rfc-editor.org/rfc/rfc6066.txt
3. Zeek 문서, "ssl.log". https://github.com/zeek/zeek-docs/blob/master/logs/ssl.rst
4. Zeek 문서, "base/protocols/ssl/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/main.zeek.rst
5. Zeek 문서, "base/files/x509/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/files/x509/main.zeek.rst
6. Zeek 문서, "quic.log". https://github.com/zeek/zeek-docs/blob/master/logs/quic.rst
7. Zeek 문서, "base/protocols/ssh/main.zeek". https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssh/main.zeek.rst
8. FoxIO, "JA4+ Network Fingerprinting" README. https://github.com/FoxIO-LLC/ja4/blob/main/README.md
9. Suricata 사용자 안내서, "Eve JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
10. Wireshark 표시 필터 참조, "Transport Layer Security (tls)". https://www.wireshark.org/docs/dfref/t/tls.html
11. Wireshark 위키, "TLS". https://wiki.wireshark.org/TLS
12. Wireshark 매뉴얼, "editcap". https://github.com/wireshark/wireshark/blob/master/doc/man_pages/editcap.adoc
13. Wireshark 매뉴얼, "tshark". https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
14. M. Thomson, Y. Rosomakho, H. Tschofenig, 「The SSLKEYLOGFILE Format for TLS」, RFC 9850, 2025. https://www.rfc-editor.org/rfc/rfc9850
15. Mozilla NSS 문서, "NSS Key Log Format". https://udn.realityripple.com/docs/Mozilla/Projects/NSS/Key_Log_Format
16. Daniel Baier, Alexander Basse, Jan-Niclas Hilgert, Martin Lambertz, 「TLS key material identification and extraction in memory: Current state and future challenges」, Forensic Science International: Digital Investigation 49, 301766, 2024. doi:10.1016/j.fsidi.2024.301766
17. Tina Wu, Frank Breitinger, Stephen Niemann, 「IoT network traffic analysis: Opportunities and challenges for forensic investigators?」, Forensic Science International: Digital Investigation, 2021. doi:10.1016/j.fsidi.2021.301123
18. Z. Hu 외, 「Specification for DNS over Transport Layer Security (TLS)」, RFC 7858. https://www.rfc-editor.org/rfc/rfc7858.txt
19. Zeek 문서, "ssh.log". https://github.com/zeek/zeek-docs/blob/master/logs/ssh.rst
