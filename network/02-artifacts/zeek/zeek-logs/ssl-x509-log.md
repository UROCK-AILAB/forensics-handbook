---
title: "TLS·인증서 기록"
parent: "Zeek 로그"
grand_parent: "아티팩트 · Zeek"
nav_order: 180
---

# TLS·인증서 기록 (ssl.log·x509.log)

Zeek 는 TLS 핸드셰이크를 해석해 연결마다 ssl.log 에 한 줄을 쓰고, 핸드셰이크에서 본 X.509 인증서는 x509.log 에 따로 씁니다. 두 로그로 암호화된 연결의 버전·암호 스위트·요청한 서버 이름(SNI)·인증서 주체와 발급자를 알 수 있지만, TLS 1.3 에서는 인증서가 암호화되어 x509.log 가 생기지 않습니다. Zeek 4.1.0 에서 두 로그의 모양이 크게 바뀌어서, 로그를 읽기 전에 어느 버전의 모양인지부터 확인해야 합니다.

## 무엇을 기록하나 · 왜 생기나

HTTPS 처럼 TLS 로 감싼 트래픽은 Zeek 가 안의 HTTP 를 읽지 못해서 http.log 에 나오지 않고, 대신 핸드셰이크에서 평문으로 오가는 값이 ssl.log 에 남습니다[7]. TLS 는 HTTPS 말고도 SMTP 같은 여러 프로토콜을 암호화하므로 ssl.log 에는 웹 말고 다른 서비스의 연결도 섞여 있습니다[7]. 로그 이름의 SSL 은 TLS 이전에 쓰던 Secure Sockets Layer 를 가리킵니다[7].

Zeek 는 기본으로 443·465·563·585·614·636·989·990·992·993·995·5223/tcp 를 SSL 포트로, 443/udp 를 DTLS 포트로 둡니다[1]. Zeek 6.1.0 부터는 QUIC 버전 1 의 INITIAL 패킷을 풀 수 있으면 그 안의 핸드셰이크를 SSL 분석기로 넘겨 ssl.log 에 한 줄을 쓰고, conn.log 의 service 에 `quic` 과 `ssl` 을 함께 적습니다(예: `quic,ssl`)[9].

x509.log 는 인증서를 파일로 보고 파일 분석을 거쳐 씁니다. 서버나 클라이언트가 Certificate 메시지로 보낸 인증서는 한 장씩 x509.log 의 한 줄이 되고(같은 인증서는 중복을 지웁니다, 아래 함정 참고), ssl.log 에는 기본으로 그 인증서들의 지문 목록만 남습니다[3][5].

## 위치와 버전별 차이

두 로그 모두 Zeek 가 로그를 쓰는 디렉터리에 `ssl.log`·`x509.log` 로 생깁니다. 저장 위치, TSV 와 JSON 형식, 교대된 로그 파일 이름은 [Zeek 로그](index.md)에 있습니다.

Zeek 4.1.0 에서 SSL·X509 처리를 다시 짜면서 기본 로그의 필드가 바뀌었습니다[9]. 공개된 해설 문서 가운데에는 4.1.0 이전 모양으로 예시를 든 것이 있어서, 필드 이름을 보고 어느 쪽인지 먼저 구분합니다[7][8].

| 항목 | 4.1.0 이전 | 4.1.0 이후 |
|---|---|---|
| ssl.log 의 인증서 연결 | `cert_chain_fuids`·`client_cert_chain_fuids`(파일 ID) | `cert_chain_fps`·`client_cert_chain_fps`(인증서 지문) |
| ssl.log 의 `subject`·`issuer` | 기본으로 기록 | 기본으로 빠짐. 설정으로 되살림 |
| ssl.log 의 `ssl_history` | 없음 | 있음 |
| ssl.log 의 `sni_matches_cert` | 없음 | 있음 |
| x509.log 의 열쇠 | `id`(파일 ID) | `fingerprint`(기본 SHA-256) |
| x509.log 중복 제거 | 없음 | 같은 인증서는 기본 하루에 한 번 |
| x509.log 의 `host_cert`·`client_cert` | 없음 | 있음 |
| 인증서의 files.log 기록 | 기록 | 기본으로 기록 안 함 |

`subject`·`issuer` 는 `SSL::log_include_server_certificate_subject_issuer` 를, 클라이언트 인증서의 `client_subject`·`client_issuer` 는 `SSL::log_include_client_certificate_subject_issuer` 를 T 로 바꾸면 다시 나옵니다. 둘 다 기본값은 F 입니다[3]. 인증서를 files.log 에도 쓰려면 `X509::log_x509_in_files_log` 를 T 로 바꿉니다[5]. 그 밖에 6.0.0 에서 Hello Retry Request 를 `s` 가 아닌 `j` 로 기록하도록 고쳤고, 6.1.0 부터 `ssl_history` 길이가 100글자로 제한됩니다[9].

## 구조

### ssl.log 필드

아래는 기본 설정의 ssl.log 필드입니다[1][2][3].

| 필드 | 뜻 |
|---|---|
| `ts` | 이 연결에서 SSL 관련 메시지를 처음 본 시각 |
| `uid`, `id.*` | 연결 ID 와 주소·포트. conn.log 와 같은 값 |
| `version` | 서버가 고른 버전. supported_versions 확장으로 서버가 버전 하나를 알리면 그 값 |
| `cipher` | 서버가 고른 암호 스위트 |
| `curve` | ECDH(E) 에서 서버가 고른 곡선, TLS 1.3 이면 서버 key_share 의 그룹 |
| `server_name` | 클라이언트가 SNI 확장에 적은 첫 번째 이름 |
| `resumed` | 이전 연결의 키를 다시 쓴 세션 재개 여부 |
| `last_alert` | 연결에서 마지막으로 본 경고(alert) |
| `next_protocol` | 서버가 ALPN 확장으로 고른 프로토콜(`h2`, `http/1.1` 등) |
| `established` | 핸드셰이크가 끝까지 성립했는지 |
| `ssl_history` | 핸드셰이크 메시지를 본 순서 |
| `cert_chain_fps` | 서버가 보낸 인증서들의 지문, 보낸 순서대로 |
| `client_cert_chain_fps` | 클라이언트가 보낸 인증서들의 지문 |
| `sni_matches_cert` | SNI 가 서버의 첫 인증서 이름과 맞으면 T, 안 맞으면 F. SNI 가 없으면 값 없음 |

`version` 값은 숫자를 문자열로 바꾼 것입니다. 2 는 `SSLv2`, 768 은 `SSLv3`, 769·770·771·772 는 `TLSv10`·`TLSv11`·`TLSv12`·`TLSv13`, 65279·65277·65276 은 `DTLSv10`·`DTLSv12`·`DTLSv13` 입니다. TLS 1.3 초안 번호는 `TLSv13-draft` 뒤에 초안 번호를 붙이고, 그 밖에 표에 없는 번호는 `unknown-64282` 처럼 `unknown-` 뒤에 숫자를 붙입니다[4][7].

`resumed` 는 세 경우에 T 가 됩니다. 클라이언트가 보낸 세션 ID 를 서버가 그대로 돌려준 경우(TLS 1.3 제외), 클라이언트가 빈 세션 ID 와 세션 티켓을 보내고 client_key_exchange 없이 change_cipher_spec 으로 넘어간 경우, TLS 1.3 에서 클라이언트가 내민 PSK 를 서버가 받아들인 경우입니다[1].

`ssl_history` 는 메시지 하나를 글자 하나로 적고, 클라이언트가 보낸 것은 대문자, 서버가 보낸 것은 소문자로 씁니다[1].

| 글자 | 메시지 | 글자 | 메시지 |
|---|---|---|---|
| `^` | 방향 뒤집힘 | `A` | supplemental_data |
| `H` | hello_request | `Z` | 할당되지 않은 핸드셰이크 종류 |
| `C` | client_hello | `I` | change_cipher_spec |
| `S` | server_hello | `B` | heartbeat |
| `V` | hello_verify_request | `D` | application_data |
| `T` | NewSessionTicket | `E` | end_of_early_data |
| `X` | certificate | `O` | encrypted_extensions |
| `K` | server_key_exchange | `P` | key_update |
| `R` | certificate_request | `M` | message_hash |
| `N` | server_hello_done | `J` | hello_retry_request |
| `Y` | certificate_verify | `L` | alert |
| `G` | client_key_exchange | `Q` | 알 수 없는 content type |
| `F` | finished | | |
| `W` | certificate_url | | |
| `U` | certificate_status | | |

`^` 는 연결을 연 쪽(originator)이 아니라 받은 쪽이 client_hello 를 보냈다는 표시이고, 예를 들어 STUN 으로 연결을 연 뒤 DTLS 를 쓰면 생깁니다[1].

기본으로 빠진 필드도 스크립트를 올리면 생깁니다. `policy/protocols/ssl/ssl-log-ext.zeek` 는 클라이언트가 내민 암호 스위트(`client_ciphers`), 확장 번호(`ssl_client_exts`), 곡선(`client_curves`), ALPN 목록(`orig_alpn`), 지원 버전(`client_supported_versions`) 같은 필드를 더합니다[2]. `validate-certs.zeek` 를 올리면 인증서 검증 결과 `validation_status` 가 붙는데[2], zeekctl 이 기본으로 싣는 local.zeek 에 이 스크립트가 들어 있습니다[10][12]. JA3·JA3S 패키지(`zkg install ja3`)는 `ja3`·`ja3s` 를, FoxIO 의 JA4 플러그인(`zkg install zeek/foxio/ja4`, Zeek 7.0 이상)은 JA4 계열 필드를 ssl.log 에 더합니다[13][14]. 지문 값의 계산과 해석은 [TLS 지문 (JA3·JA4)](../../fingerprints/ja3-ja4.md)에 있습니다.

### x509.log 필드

x509.log 는 인증서 한 장이 한 줄입니다[5][6].

| 필드 | 뜻 |
|---|---|
| `ts` | 이 인증서를 파일로 처음 본 시각 |
| `fingerprint` | 인증서 DER 바이트의 해시. 기본 SHA-256 |
| `certificate.version` | 인증서 버전 |
| `certificate.serial` | 일련번호 |
| `certificate.subject`, `certificate.issuer` | 주체와 발급자 DN |
| `certificate.not_valid_before`, `certificate.not_valid_after` | 유효 기간 시작과 끝 |
| `certificate.key_alg`, `certificate.sig_alg` | 공개 키 알고리즘과 서명 알고리즘 이름 |
| `certificate.key_type`, `certificate.key_length` | 키 종류(rsa·dsa·ec)와 비트 수 |
| `certificate.exponent` | RSA 인증서의 공개 지수 |
| `certificate.curve` | EC 인증서의 곡선 |
| `san.dns`, `san.uri`, `san.email`, `san.ip` | 주체 대체 이름(SAN) 확장의 값 목록 |
| `basic_constraints.ca`, `basic_constraints.path_len` | CA 인증서인지, 허용하는 경로 길이 |
| `host_cert` | 체인에서 첫 번째로 보낸 말단 인증서면 T |
| `client_cert` | 클라이언트가 보낸 인증서면 T |

ssl.log 와 x509.log 에는 공통 uid 가 없습니다. 두 로그는 ssl.log 의 `cert_chain_fps` 에 든 지문과 x509.log 의 `fingerprint` 로 잇습니다[3][5]. `cert_chain_fps` 의 첫 값이 서버의 말단 인증서이고, `sni_matches_cert` 도 이 첫 인증서로 판단합니다[3].

### 로그 줄 모양

TLS 1.2 연결 하나를 Zeek 4.1.0 이후 모양의 JSON 으로 만든 예시입니다(만든 예시, 지문은 앞부분만 적음).

```json
{"ts":1767225600.123456,"uid":"C7kd2Q3sXvLb9aPe1","id.orig_h":"10.0.0.15","id.orig_p":51514,"id.resp_h":"203.0.113.20","id.resp_p":443,"version":"TLSv12","cipher":"TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256","curve":"x25519","server_name":"www.example.com","resumed":false,"next_protocol":"h2","established":true,"ssl_history":"CsxknGIi","cert_chain_fps":["3b7c0e…","9d2e41…"],"client_cert_chain_fps":[],"sni_matches_cert":true}
```

```json
{"ts":1767225600.187654,"fingerprint":"3b7c0e…","certificate.version":3,"certificate.serial":"04A1B2C3D4E5F60718","certificate.subject":"CN=www.example.com","certificate.issuer":"CN=Example Issuing CA,O=Example CA,C=US","certificate.not_valid_before":1764547200,"certificate.not_valid_after":1772323199,"certificate.key_alg":"rsaEncryption","certificate.sig_alg":"sha256WithRSAEncryption","certificate.key_type":"rsa","certificate.key_length":2048,"certificate.exponent":"65537","san.dns":["www.example.com","example.com"],"basic_constraints.ca":false,"host_cert":true,"client_cert":false}
```

`ssl_history` 의 `CsxknGIi` 는 client_hello, server_hello, 서버 인증서, server_key_exchange, server_hello_done, client_key_exchange, 클라이언트 change_cipher_spec, 서버 change_cipher_spec 순서로 메시지를 봤다는 뜻입니다. DN 값 안의 쉼표는 백슬래시로 이스케이프하고, JSON 로그에서는 `Example\\, Inc.` 처럼 백슬래시가 두 개로 보입니다[8]. 유효 기간 필드는 에포크 초이고[6][8], 이 예시에서는 2025-12-01 00:00:00 UTC 부터 2026-02-28 23:59:59 UTC 까지입니다.

## 증거로서 의미

**증명하는 것.** 이 시각에 이 내부 주소가 이 외부 주소·포트와 TLS 핸드셰이크를 했고, 어떤 버전과 암호 스위트로 합의했는지, 핸드셰이크가 성립했는지(`established`)를 보여 줍니다. 클라이언트가 SNI 에 적어 보낸 서버 이름과 ALPN 으로 고른 응용 프로토콜도 남습니다[1][7]. TLS 1.2 이하에서는 서버가 보낸 인증서의 주체·발급자·유효 기간·SAN·일련번호가 x509.log 에 남아서, 같은 인증서를 쓴 다른 서버나 다른 시각의 연결을 지문으로 찾을 수 있습니다[3][8].

**증명하지 못하는 것.** 주고받은 내용, 요청한 URL 경로와 파일은 알 수 없습니다. SNI 는 클라이언트가 적어 보낸 값이라 실제로 응답한 서버가 그 이름의 주인이라는 보장은 없고, `sni_matches_cert` 가 F 이면 인증서의 이름과 맞지 않았다는 뜻입니다[3]. TLS 1.3 은 ServerHello 뒤의 핸드셰이크 메시지를 모두 암호화해서[17] 인증서가 보이지 않고, x509.log 에 줄이 생기지 않습니다[8]. 암호화된 SNI(ESNI)나 암호화된 ClientHello(ECH)를 쓰면 `server_name` 도 비고, 같은 접속에서 DNS over HTTPS 까지 쓰면 dns.log 에도 서버 이름이 남지 않습니다[7]. 어떤 프로세스나 사용자가 연결을 만들었는지도 ssl.log 로는 알 수 없습니다.

보고서에는 "이 사이트에 접속했다" 가 아니라 "이 시각에 10.0.0.15 가 203.0.113.20:443 과 SNI `www.example.com` 으로 TLS 1.2 핸드셰이크를 마쳤고, 서버는 `CN=www.example.com` 인증서를 보냈다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

ssl.log 의 `ts` 는 이 연결에서 SSL 관련 메시지를 처음 본 네트워크 시각이고[1], 보통 ClientHello 무렵입니다. 그래서 TCP 연결 시작 시각인 conn.log 의 `ts` 보다 조금 늦고, 한 TLS 1.2 연결에서는 conn.log 가 1598377391.716515, ssl.log 가 1598377391.921726 으로 약 0.2초 차이가 났습니다[7]. 줄을 쓰는 시점은 핸드셰이크가 성립했을 때(`ssl_established`)이고, 성립하지 못한 연결은 연결 상태가 지워질 때 씁니다[1]. 파일 안의 줄 순서가 `ts` 순서와 다를 수 있으므로 시간순으로 볼 때는 `ts` 로 정렬합니다.

x509.log 의 `ts` 는 인증서를 파일로 처음 본 시각입니다[5]. 인증서는 ClientHello 뒤에 오므로 같은 연결의 ssl.log `ts` 보다 늦고, 앞의 TLS 1.2 연결에서는 1598377391.938343 이었습니다[8]. 줄을 쓰는 시점은 파일 분석이 끝날 때입니다[5]. 모든 `ts` 는 패킷 캡처 시각을 에포크 초(UTC 기준)로 적은 값이고, JSON 에서 ISO 8601 문자열로 바꾸는 설정은 [Zeek 로그](index.md)에 있습니다.

`certificate.not_valid_before`·`not_valid_after` 는 발급자가 인증서 안에 적은 값이라 연결 시각과 관계가 없습니다. 연결 시각이 유효 기간 밖이면 만료되었거나 아직 유효하지 않은 인증서를 쓴 연결이라는 뜻입니다. Zeek 8.0.0 부터 이 두 값을 GMT 로 기록하고, 그 전 버전은 인증서 안의 시각을 현지 시각으로 해석해서 Zeek 를 돌린 시스템의 시간대에 따라 값이 달라졌습니다[9].

## 함정과 한계

**x509.log 는 중복을 지웁니다.** 같은 지문·`host_cert`·`client_cert` 조합의 인증서는 기본으로 하루에 한 번만 기록합니다(`X509::relog_known_certificates_after = 1day`)[5]. 그래서 x509.log 에 인증서가 처음 나온 시각은 그 서버에 처음 접속한 시각이 아니고, 둘째 연결부터는 x509.log 에 줄이 없습니다. 연결마다의 인증서는 ssl.log 의 `cert_chain_fps` 로 확인합니다. 중복 기록 상태는 설정에 따라 워커마다 따로일 수 있고, Zeek 를 다시 시작하면 초기화되며, 최대 1,000,000개까지 기억하고, 이 수를 넘으면 새 인증서는 중복을 지우지 않고 볼 때마다 씁니다. 0secs 로 두면 중복 제거를 끕니다[5].

**실행 방법에 따라 x509.log 내용이 다릅니다.** zeekctl 이 싣는 local.zeek 에는 CA 인증서를 x509.log 에서 빼는 `log-hostcerts-only` 와 `validate-certs` 가 들어 있습니다[10][12]. `zeek -r` 로 pcap 만 돌리면 local.zeek 을 싣지 않아서 중간 CA 인증서까지 x509.log 에 나오고 `validation_status` 는 없습니다[10][12]. 운영 센서의 로그와 나중에 pcap 을 다시 돌린 로그를 비교할 때 이 차이를 먼저 확인합니다.

**지문 해시를 바꾸면 값이 모두 바뀝니다.** `X509::hash_function` 을 바꾸면 ssl.log 와 x509.log 의 지문이 함께 바뀌어[5], 다른 센서나 위협 정보의 SHA-256 지문과 맞지 않게 됩니다. Suricata 의 tls 기록은 SHA-1 지문을 쓰므로 그대로 비교하지 않습니다([프로토콜 기록](../../suricata/eve-json/protocol-events.md)).

**TLS 1.3 과 세션 재개.** TLS 1.3 연결은 인증서가 보이지 않아 `cert_chain_fps` 도 빕니다[7][8]. 세션을 재개한 연결도 인증서가 없을 수 있고, TLS 1.3 에서 PSK 로 재개하면 서버가 Certificate 메시지를 보내지 않습니다[17]. 인증서가 없는 줄을 "인증서 없이 접속했다" 로 해석하지 않습니다.

**기록 뒤의 메시지.** 기본값 `SSL::disable_analyzer_after_detection = T` 라서 핸드셰이크가 성립하면 줄을 쓰고 분석기를 떼어 냅니다[1]. 그 뒤에 오는 경고나 메시지는 기본 ssl.log 에 담기지 않을 가능성이 있습니다.

**`server_name` 은 첫 이름뿐입니다.** SNI 에 이름이 여러 개면 첫 이름만 쓰고 weird `SSL_many_server_names` 를 올립니다. `ssl_history` 가 100글자에 이르면 `SSL_max_ssl_history_length_reached`, 핸드셰이크 전에 응용 데이터가 오면 `ssl_early_application_data` 가 weird.log 에 남습니다[1]. weird 해석은 [경고와 이상 기록](notice-weird-log.md)에 있습니다.

**긴 SAN 목록은 잘립니다.** Zeek 8.1.0 부터 로그 필드에 길이 제한이 생겼고, x509.log 는 목록 필드 하나에 500개, 한 줄 전체에 1500개까지만 씁니다[5][9].

## 직접 분석해 보기

### 헥스로 SNI 찾기

`server_name` 이 어디서 오는지 ClientHello 의 바이트로 한 번 따라갑니다. TLS 레코드 첫 바이트가 `16`(handshake, 22)이고 핸드셰이크 메시지 첫 바이트가 `01`(client_hello)인 패킷에서 확장 목록을 찾습니다[17]. SNI 확장은 종류 번호가 0 이고, 안에 ServerNameList → 이름 종류 host_name(0) → 2바이트 길이와 이름이 들어갑니다[16].

아래는 `www.example.com` 을 담은 SNI 확장을 RFC 6066 구조대로 만든 예시입니다(명세로 만든 예시).

```
00 00                   확장 종류 server_name(0)
00 14                   확장 데이터 길이 20
00 12                   ServerNameList 길이 18
00                      이름 종류 host_name(0)
00 0f                   이름 길이 15
77 77 77 2e 65 78 61 6d 70 6c 65 2e 63 6f 6d    "www.example.com"
```

Zeek 는 이 목록의 첫 이름을 `server_name` 에 넣습니다[1]. 실제 pcap 에서 같은 바이트를 찾아 ssl.log 의 값과 같은지 확인하면, 로그를 만든 센서가 그 패킷을 제대로 봤는지도 함께 확인됩니다.

### 공개 도구로 읽기

pcap 사본을 JSON 로그로 돌립니다[11][12].

```
zeek -C -r trace.pcap LogAscii::use_json=T
```

성립한 TLS 연결을 서버 이름·버전·첫 인증서 지문과 함께 뽑고, 그 지문으로 x509.log 에서 인증서를 찾습니다.

```
jq -c 'select(.established==true) | [.uid, ."id.resp_h", .server_name, .version, .cert_chain_fps[0]]' ssl.log
jq -c 'select(.fingerprint=="찾을 지문") | [."certificate.subject", ."certificate.issuer", ."san.dns"]' x509.log
```

TSV 로그라면 `zeek-cut uid server_name version cert_chain_fps < ssl.log` 처럼 필드 이름으로 고릅니다[11]. local.zeek 과 같은 결과가 필요하면 local.zeek 경로를 스크립트 인수로 함께 줍니다[12].

탐지 규칙의 필드 이름도 이 로그를 따릅니다. Sigma 의 Zeek x509 규칙은 `certificate.serial` 이 `8BB00EE` 인 인증서를 Cobalt Strike 기본 인증서로 찾습니다[15]. `validate-certs` 가 검증에 실패한 서버 인증서를 만나면 notice.log 에 `SSL::Invalid_Server_Cert` 를 올립니다[18].

## 교차 검증

| 함께 볼 기록 | 확인할 것 | 링크 |
|---|---|---|
| conn.log | 같은 uid 의 바이트 수·지속 시간·`conn_state`, 핸드셰이크 뒤 데이터가 실제로 오갔는지 | [연결 기록](conn-log.md) |
| dns.log | 연결 직전에 `server_name` 을 조회했고 답이 `id.resp_h` 였는지 | [DNS 기록](dns-log.md) |
| files.log | 4.1.0 이전 로그에서 `cert_chain_fuids` 의 파일 ID | [파일 기록](files-log.md) |
| notice.log·weird.log | 인증서 검증 실패, SNI 여러 개, history 길이 초과 | [경고와 이상 기록](notice-weird-log.md) |
| Suricata tls 기록 | 같은 흐름의 SNI·버전·인증서(SHA-1 지문) | [프로토콜 기록](../../suricata/eve-json/protocol-events.md) |
| JA3·JA4 | 클라이언트·서버 TLS 구현 식별 | [TLS 지문 (JA3·JA4)](../../fingerprints/ja3-ja4.md) |
| 인증서 조회 | 같은 인증서를 쓰는 다른 서버 | [인증서로 서버 알아보기](../../fingerprints/certificates.md) |

TLS 핸드셰이크와 인증서 구조 자체는 [TLS와 인증서](../../../01-foundations/protocols/tls.md)에, 암호화된 트래픽을 조사하는 절차는 [암호화된 트래픽 분석](../../../03-techniques/analysis/encrypted-traffic.md)에 있습니다.

## 실습

Wireshark 예제 캡처처럼 TLS 트래픽이 든 공개 캡처 파일의 사본에 Zeek 를 돌린 뒤 아래 질문을 풀어 봅니다.

1. `version` 별 줄 수를 세고, `TLSv13` 연결 가운데 `cert_chain_fps` 가 있는 줄이 있는지 확인합니다.
2. `sni_matches_cert` 가 false 인 연결을 찾아, x509.log 의 `san.dns` 와 `server_name` 을 비교합니다.
3. 같은 인증서 지문이 여러 연결의 `cert_chain_fps` 에 나오는데 x509.log 에는 몇 줄인지 세어 봅니다.
4. `zeek -r` 만으로 돌린 결과와 local.zeek 을 함께 준 결과에서 x509.log 줄 수와 `host_cert` 값이 어떻게 다른지 비교합니다.
5. ssl.log 의 `ts` 와 같은 uid 의 conn.log `ts` 차이를 구하고, pcap 에서 ClientHello 패킷의 시각과 비교합니다.

## 참고 문헌

1. Zeek 소스 scripts/base/protocols/ssl/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/ssl/main.zeek
2. Zeek 문서 — base/protocols/ssl/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/main.zeek.rst
3. Zeek 소스 scripts/base/protocols/ssl/files.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/ssl/files.zeek
4. Zeek 소스 scripts/base/protocols/ssl/consts.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/ssl/consts.zeek
5. Zeek 소스 scripts/base/files/x509/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/files/x509/main.zeek
6. Zeek 소스 scripts/base/init-bare.zeek (X509::Certificate 정의). https://github.com/zeek/zeek/blob/master/scripts/base/init-bare.zeek
7. Zeek 문서 — ssl.log. https://github.com/zeek/zeek-docs/blob/master/logs/ssl.rst
8. Zeek 문서 — x509.log. https://github.com/zeek/zeek-docs/blob/master/logs/x509.rst
9. Zeek NEWS (4.1.0·6.0.0·6.1.0·8.0.0·8.1.0 절). https://github.com/zeek/zeek/blob/master/NEWS
10. Zeek 소스 scripts/site/local.zeek. https://github.com/zeek/zeek/blob/master/scripts/site/local.zeek
11. Zeek 문서 — Zeek Log Formats and Inspection. https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
12. Zeek 문서 — Quick Start Guide. https://docs.zeek.org/en/master/quickstart.html
13. Salesforce, JA3 Zeek 스크립트 README. https://github.com/salesforce/ja3/blob/master/zeek/README.md
14. FoxIO, JA4+ Zeek 플러그인 README. https://github.com/FoxIO-LLC/ja4/blob/main/zeek/README.md
15. SigmaHQ, Default Cobalt Strike Certificate (zeek_default_cobalt_strike_certificate.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_default_cobalt_strike_certificate.yml
16. D. Eastlake 3rd, "Transport Layer Security (TLS) Extensions: Extension Definitions", RFC 6066, 2011. https://www.rfc-editor.org/rfc/rfc6066.txt
17. E. Rescorla, "The Transport Layer Security (TLS) Protocol Version 1.3", RFC 8446, 2018. https://www.rfc-editor.org/rfc/rfc8446.txt
18. Zeek 문서 — Notice Framework. https://github.com/zeek/zeek-docs/blob/master/frameworks/notice.rst
