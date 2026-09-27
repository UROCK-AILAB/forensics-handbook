---
title: "TLS와 인증서"
parent: "기반 · 프로토콜 기초"
nav_order: 70
---

# TLS와 인증서 (TLS·X.509)

전송 계층 보안 (Transport Layer Security, TLS) 은 HTTPS·메일·DNS over TLS 같은 응용 프로토콜을 암호화하는 프로토콜입니다. 본문은 암호화되지만 연결 처음의 핸드셰이크 일부는 평문으로 오가서, 패킷 캡처와 Zeek·Suricata 로그에 요청한 서버 이름·협상한 버전·암호 스위트·(TLS 1.2 이하라면) 서버 인증서가 남습니다. 이 페이지에서는 레코드와 핸드셰이크 메시지의 구조, TLS 1.2 와 1.3 에서 평문으로 보이는 범위, 실제 버전을 판별하는 순서, 조사 대상에 키 로그 파일이 있을 때 읽는 법을 다룹니다.

## 이 형식을 쓰는 아티팩트

TLS 는 보통 TCP 위에서 쓰이고, 응용 프로토콜마다 TLS 를 시작하는 방법이 다릅니다. 연결하자마자 핸드셰이크를 시작하는 방식(Implicit TLS)이 있고, 평문으로 시작했다가 STARTTLS 명령으로 TLS 로 바꾸는 방식이 있습니다[6].

| 쓰는 곳 | 포트·방식 | 자세한 설명 |
|---|---|---|
| HTTPS | TCP 443 | [HTTP](http.md) |
| 메일 제출(SMTP) | 465 는 연결 즉시 TLS, 587 은 STARTTLS[6] | [메일 프로토콜](mail-protocols.md) |
| IMAP·POP3 | 993·995 는 연결 즉시 TLS[6] | [메일 프로토콜](mail-protocols.md) |
| DNS over TLS | TCP 853[5] | [DNS](dns.md) |
| DNS over HTTPS | HTTPS 연결 안의 요청 | [DNS](dns.md) |
| RDP | RDP 협상 뒤 TLS 핸드셰이크로 전환[13] | [SMB와 원격 관리 프로토콜](remote-protocols.md) |
| QUIC | UDP. 기본으로 TLS 1.3 을 씀[10] | Zeek quic.log (아래) |

TLS 연결에서 나온 정보는 여러 기록에 나뉘어 남습니다.

- 패킷 캡처(pcap·pcapng): 핸드셰이크의 평문 부분 전체와, 암호화된 레코드의 방향·길이·순서.
- Zeek `ssl.log`·`x509.log`: 연결마다 버전·암호 스위트·SNI·ALPN·핸드셰이크 메시지 순서(`ssl_history`), TLS 1.2 이하라면 인증서. 필드와 버전별 모양은 [TLS·인증서 기록 (ssl.log·x509.log)](../../02-artifacts/zeek/zeek-logs/ssl-x509-log.md) 에 있습니다.
- Zeek `quic.log`(Zeek 6.1 부터): QUIC 연결의 버전, 연결 ID, ClientHello 의 SNI(`server_name`)와 첫 ALPN 값(`client_protocol`)[10][11].
- Suricata EVE `tls`: 기본은 인증서의 `subject`·`issuer`, 확장 기록(`extended: yes`)이면 `sni`·`version`·일련번호·지문·유효기간·ALPN 까지 씁니다[13]. 기록 조건은 [프로토콜 기록](../../02-artifacts/suricata/eve-json/protocol-events.md) 에 있습니다.
- TLS 지문(JA3·JA4): ClientHello·ServerHello 값으로 계산한 해시. [TLS 지문 (JA3·JA4)](../../02-artifacts/fingerprints/ja3-ja4.md) 에서 다룹니다.
- 서버 인증서: [인증서로 서버 알아보기](../../02-artifacts/fingerprints/certificates.md) 에서 다룹니다.
- 키 로그 파일(SSLKEYLOGFILE): 끝점 프로그램이 연결마다 비밀 값을 적은 텍스트 파일. 이 페이지의 "키 로그 파일이 있을 때" 에서 다룹니다.

## 구조

### 레코드

TLS 는 주고받는 모든 데이터를 레코드 (record) 로 나눠 보냅니다. 레코드 머리는 5바이트이고 그 뒤에 내용이 옵니다[1].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 1 | type (ContentType) | 내용 종류(아래 표) |
| 1 | 2 | legacy_record_version | 레코드 버전. TLS 1.3 에서는 뜻이 없어 받는 쪽이 무시합니다 |
| 3 | 2 | length | 뒤따르는 내용의 바이트 수. 평문 레코드는 2^14(16,384) 이하, 암호화된 레코드는 2^14+256 이하 |
| 5 | length | fragment | 내용 |

| type 값 | 이름 | 내용 | Zeek `ssl_history` 글자 |
|---|---|---|---|
| 20 | change_cipher_spec | 암호화 전환 알림 | `I` |
| 21 | alert | 경고·종료 알림 | `L` |
| 22 | handshake | 핸드셰이크 메시지 | 메시지마다 다름(다음 표) |
| 23 | application_data | 응용 데이터 | `D` |
| 24 | heartbeat | 연결 확인 | `B` |

type 값과 Zeek `ssl_history` 글자의 대응은 위 표와 같습니다[1][8]. `ssl_history` 는 클라이언트가 보낸 것을 대문자, 서버가 보낸 것을 소문자로 적습니다[8].

버전 필드에는 아래 값이 들어갑니다. 오른쪽 두 열은 Zeek 가 쓰는 번호와 `version` 필드 문자열입니다[1][9].

| 16진 값 | 프로토콜 | 10진 | Zeek `version` |
|---|---|---|---|
| 0x0300 | SSL 3.0 | 768 | `SSLv3` |
| 0x0301 | TLS 1.0 | 769 | `TLSv10` |
| 0x0302 | TLS 1.1 | 770 | `TLSv11` |
| 0x0303 | TLS 1.2 | 771 | `TLSv12` |
| 0x0304 | TLS 1.3 | 772 | `TLSv13` |
| 0xFEFF | DTLS 1.0 | 65279 | `DTLSv10` |
| 0xFEFD | DTLS 1.2 | 65277 | `DTLSv12` |
| 0xFEFC | DTLS 1.3 | 65276 | `DTLSv13` |

실제 ssl.log 의 `version` 에는 표에 없는 `unknown-64282` 같은 값이나, 값이 비어 있는(`null`) 줄도 나옵니다[7].

TLS 1.3 은 레코드 버전을 호환용으로만 씁니다. 처음 보내는 ClientHello 레코드는 0x0301 로 쓰는 것이 권장되고, 그 밖의 레코드는 0x0303 입니다[1]. 암호화된 레코드는 바깥 type 이 항상 23(application_data), 버전이 항상 0x0303 이고, 실제 종류는 복호한 뒤 안쪽 type 필드로 알 수 있습니다[1]. 그래서 TLS 1.3 캡처에서는 암호화된 핸드셰이크 메시지와 경고까지 모두 application_data 레코드로 보입니다.

### 핸드셰이크 메시지

handshake 레코드 안에는 1바이트 msg_type 과 3바이트 length 로 시작하는 메시지가 들어 있습니다[1]. 레코드 하나에 메시지 여러 개가 들어갈 수 있고, 메시지 하나가 레코드 여러 개로 나뉠 수도 있습니다[1]. 그래서 "패킷 하나 = 메시지 하나" 로 읽지 않습니다.

| 값 | 메시지 | 보내는 곳 | Zeek 글자 | TLS 1.3 에서 |
|---|---|---|---|---|
| 0 | hello_request | 서버 | `H` | 쓰지 않음(1.2 이하 전용) |
| 1 | client_hello | 클라이언트 | `C` | 평문 |
| 2 | server_hello | 서버 | `S` | 평문 |
| 4 | new_session_ticket | 서버 | `T` | 암호화 |
| 5 | end_of_early_data | 클라이언트 | `E` | 암호화 |
| 8 | encrypted_extensions | 서버 | `O` | 암호화 |
| 11 | certificate | 서버(요청받으면 클라이언트도) | `X` | 암호화 |
| 12 | server_key_exchange | 서버 | `K` | 쓰지 않음 |
| 13 | certificate_request | 서버 | `R` | 암호화 |
| 14 | server_hello_done | 서버 | `N` | 쓰지 않음 |
| 15 | certificate_verify | 서버·클라이언트 | `Y` | 암호화 |
| 16 | client_key_exchange | 클라이언트 | `G` | 쓰지 않음 |
| 20 | finished | 서버·클라이언트 | `F` | 암호화 |
| 24 | key_update | 서버·클라이언트 | `P` | 암호화 |

"쓰지 않음" 은 TLS 1.3 이 예약값(RESERVED)으로만 남긴 TLS 1.2 이하의 메시지입니다[1]. 서버가 ClientHello 를 다시 요구하는 HelloRetryRequest 는 ServerHello 와 같은 형식이라 값 2 를 쓰고, Zeek 는 이를 따로 `J` 로 적습니다[1][8].

### TLS 1.2 와 1.3 에서 평문으로 보이는 범위

TLS 1.2 에서는 ServerHello 뒤에 Certificate·ServerKeyExchange·ServerHelloDone 이 평문으로 이어지고, 각자 ChangeCipherSpec 을 보낸 뒤의 레코드(Finished 부터)가 새로 협상한 키로 암호화됩니다[2]. 그래서 중간에서 캡처만 한 트래픽에서도 서버 인증서를 그대로 읽을 수 있습니다.

```text
TLS 1.2 전체 핸드셰이크 (RFC 5246 Figure 1 을 옮김, * 는 상황에 따라 생략)
클라이언트                                     서버
ClientHello              -------->
                                               ServerHello
                                               Certificate*
                                               ServerKeyExchange*
                                               CertificateRequest*
                         <--------             ServerHelloDone
Certificate*
ClientKeyExchange
CertificateVerify*
[ChangeCipherSpec]
Finished                 -------->
                                               [ChangeCipherSpec]
                         <--------             Finished
Application Data         <------->             Application Data
```

TLS 1.3 에서는 ServerHello 다음의 핸드셰이크 메시지가 모두 암호화됩니다[1]. 평문으로 남는 것은 ClientHello 와 ServerHello(와 HelloRetryRequest)뿐이고, 서버 인증서는 핸드셰이크 키로 암호화된 Certificate 메시지 안에 들어갑니다.

```text
TLS 1.3 전체 핸드셰이크 (RFC 8446 Figure 1 을 옮김)
{} 는 핸드셰이크 키, [] 는 응용 데이터 키로 암호화한 것
클라이언트                                     서버
ClientHello
 + key_share, signature_algorithms,
   psk_key_exchange_modes, pre_shared_key   -------->
                                               ServerHello
                                                + key_share, pre_shared_key
                                               {EncryptedExtensions}
                                               {CertificateRequest*}
                                               {Certificate*}
                                               {CertificateVerify*}
                                               {Finished}
                         <--------             [Application Data*]
{Certificate*}
{CertificateVerify*}
{Finished}               -------->
[Application Data]       <------->             [Application Data]
```

TLS 1.3 에는 중간 장비와 호환하기 위한 모드가 있습니다. 이 모드에서 클라이언트는 ClientHello 의 세션 ID 에 새로 만든 32바이트 값을 넣고, 양쪽은 의미 없는 change_cipher_spec 레코드를 한 번씩 보냅니다[1]. 그래서 TLS 1.3 연결에도 세션 ID 와 change_cipher_spec 이 보일 수 있습니다.

세션을 재개하는 방법도 버전마다 다릅니다. TLS 1.2 이하는 세션 ID 와 세션 티켓으로 재개했습니다[1][2]. TLS 1.3 은 핸드셰이크가 끝난 뒤 서버가 NewSessionTicket 을 보내고, 다음 연결에서 클라이언트가 그 값을 pre_shared_key 확장에 넣습니다. 서버가 받아들이면 ServerHello 에 pre_shared_key 확장이 붙고, 서버는 Certificate·CertificateVerify 를 보내지 않습니다[1].

### ClientHello 와 ServerHello

두 메시지는 앞부분 모양이 거의 같습니다[1].

| 순서 | ClientHello | ServerHello |
|---|---|---|
| 1 | legacy_version (2바이트) | legacy_version (2바이트) |
| 2 | random (32바이트) | random (32바이트) |
| 3 | legacy_session_id (길이 1바이트 + 0~32바이트) | legacy_session_id_echo (클라이언트 값을 그대로 돌려줌) |
| 4 | cipher_suites (길이 2바이트 + 2바이트씩) | cipher_suite (고른 값 하나, 2바이트) |
| 5 | legacy_compression_methods | legacy_compression_method (0) |
| 6 | extensions (길이 2바이트 + 확장들) | extensions |

확장은 2바이트 종류, 2바이트 길이, 값 순서로 이어 붙입니다[1]. 조사에서 자주 보는 확장은 다음과 같습니다[1][8][13].

| 번호 | 확장 | 보이는 정보 | 기록되는 곳 |
|---|---|---|---|
| 0 | server_name | 클라이언트가 접속하려는 서버 이름(SNI) | Zeek `server_name`, Suricata `sni` |
| 10 | supported_groups | 클라이언트가 지원하는 키 교환 그룹 | 지문 계산에 쓰임 |
| 13 | signature_algorithms | 지원하는 서명 알고리즘 | 지문 계산에 쓰임 |
| 16 | application_layer_protocol_negotiation (ALPN) | 위에서 쓸 응용 프로토콜(`h2`, `http/1.1` 등) | Zeek `next_protocol`(서버가 고른 값), Suricata `client_alpns`·`server_alpns` |
| 41 | pre_shared_key | 재개·PSK 연결에 쓰는 식별자 | 재개 판정에 쓰임 |
| 43 | supported_versions | 클라이언트가 지원하는 버전 목록, 서버가 고른 버전 | 버전 판별에 쓰임 |
| 45 | psk_key_exchange_modes | PSK 사용 방식 | — |
| 51 | key_share | 키 교환 값 | — |

SNI (Server Name Indication) 는 server_name 확장 안의 이름 목록이고, 이름 종류는 host_name(0) 하나입니다[3]. 이름은 끝에 점이 없는 ASCII 도메인 이름이고, 국제화 도메인은 `xn--` 로 시작하는 A-label 로 쓰며, 대소문자를 구분하지 않습니다[3]. IPv4·IPv6 주소를 그대로 넣는 것은 금지돼 있습니다[3]. SNI 를 보고 인증서를 고른 서버는 값이 빈 server_name 확장으로 답하고, 세션을 재개할 때는 답하지 않습니다[3]. 이 답은 TLS 1.2 이하에서는 평문 ServerHello 에, TLS 1.3 에서는 암호화된 EncryptedExtensions 에 들어갑니다[1][3].

### 인증서

서버 인증서는 X.509 구조이고, 유효기간(notBefore·notAfter)은 UTC 로 적습니다. 2049년까지는 `YYMMDDHHMMSSZ` 형식의 UTCTime, 2050년부터는 `YYYYMMDDHHMMSSZ` 형식의 GeneralizedTime 을 씁니다[4]. 인증서의 구조, 지문으로 서버를 묶는 방법, Zeek 가 같은 인증서를 하루에 한 번만 기록하는 문제는 [인증서로 서버 알아보기](../../02-artifacts/fingerprints/certificates.md) 에서 다룹니다.

## 읽는 법

### 실제 버전을 판별하는 순서

레코드 머리와 Hello 메시지의 버전 필드만 보면 TLS 1.3 연결도 TLS 1.0 이나 1.2 로 읽힙니다. 아래 순서로 판별합니다.

1. 레코드 버전은 보지 않습니다. TLS 1.3 클라이언트도 첫 ClientHello 레코드에는 0x0301 을 쓰도록 권장됩니다[1].
2. ClientHello 에서 클라이언트가 제안한 버전을 봅니다. legacy_version 은 0x0303 으로 고정이고, supported_versions 확장의 최고값이 0x0304 이면 TLS 1.3 을 제안한 ClientHello 입니다[1]. JA4 의 버전 두 글자가 이 값입니다([TLS 지문](../../02-artifacts/fingerprints/ja3-ja4.md)).
3. ServerHello 에서 서버가 고른 버전을 봅니다. supported_versions 확장이 있으면 그 값(TLS 1.3 이면 0x0304)이 실제 버전이고, legacy_version(0x0303)은 무시합니다. 확장이 없으면 legacy_version 이 고른 버전입니다[1]. Zeek `ssl.log` 의 `version` 은 서버가 고른 버전입니다[8].
4. ServerHello 의 random 값을 확인합니다. 값이 `CF 21 AD 74 E5 9A 61 11 BE 1D 8C 02 1E 65 B8 91 C2 A2 11 16 7A BB 8C 5E 07 9E 09 E2 C8 A8 33 9C` 이면 ServerHello 가 아니라 HelloRetryRequest 입니다[1]. random 의 마지막 8바이트가 `44 4F 57 4E 47 52 44 01`(ASCII 로 "DOWNGRD" 와 01)이면 TLS 1.3 을 지원하는 서버가 TLS 1.2 를 고른 것이고, 끝이 `00` 이면 TLS 1.1 이하를 고른 것입니다. TLS 1.2 서버도 TLS 1.1 이하를 고를 때 `00` 값을 넣도록 권장되지만, 실제로는 이 규칙을 따르지 않는 TLS 1.2 구현이 많습니다[1].

### 헥스로 따라가기 (명세로 만든 예시)

아래는 TLS 1.3 ServerHello 레코드 하나를 RFC 8446 의 구조대로 만든 예시입니다. random 과 키 값은 0 으로 채웠고, 세션 ID 는 비웠습니다.

```text
오프셋  바이트                                   뜻
0000   16 03 03 00 5a                           레코드: handshake(22), 버전 0x0303, 길이 90
0005   02 00 00 56                              핸드셰이크: server_hello(2), 길이 86
0009   03 03                                    legacy_version 0x0303
000b   00 00 ... 00                             random 32바이트
002b   00                                       legacy_session_id_echo 길이 0
002c   13 01                                    cipher_suite 0x1301 (TLS_AES_128_GCM_SHA256)
002e   00                                       legacy_compression_method 0
002f   00 2e                                    확장 전체 길이 46
0031   00 2b 00 02 03 04                        supported_versions(43): 0x0304
0037   00 33 00 24 00 1d 00 20 00 ... 00        key_share(51): 그룹 0x001d(x25519), 키 32바이트
005f   17 03 03 .. ..                           다음 레코드: application_data(23), 버전 0x0303
```

legacy_version 은 0x0303 이지만 supported_versions 확장이 0x0304 이므로 이 연결은 TLS 1.3 입니다[1]. 암호 스위트 0x1301 은 TLS_AES_128_GCM_SHA256, 그룹 0x001d 는 x25519 입니다[1]. 오프셋 0x005f 부터는 바깥 type 이 23 인 레코드가 이어지는데, 이 안에 EncryptedExtensions·Certificate·Finished 가 암호화돼 들어 있습니다[1]. 같은 연결이 TLS 1.2 였다면 확장 목록에 supported_versions 가 없고, 0x005f 다음에 type 22 레코드로 Certificate(11) 메시지가 평문으로 이어집니다.

ClientHello 를 바이트 단위로 따라가는 예시는 [TLS 지문 (JA3·JA4)](../../02-artifacts/fingerprints/ja3-ja4.md) 의 "헥스로 한 번" 에 있습니다.

### 공개 도구로 읽기

Wireshark 3.0 부터 해석기 이름이 SSL 에서 TLS 로 바뀌어, 표시 필터는 `tls` 를 씁니다(`ssl` 은 경고가 뜹니다)[16]. tshark 로 ClientHello(`tls.handshake.type == 1`)마다 시각·주소·SNI·제안한 버전을 뽑으면 다음과 같습니다[17][18][19].

```sh
tshark -r sample.pcapng -Y "tls.handshake.type == 1" -T fields \
  -e frame.time_epoch -e ip.src -e ip.dst \
  -e tls.handshake.extensions_server_name \
  -e tls.handshake.extensions.supported_version
```

서버가 고른 버전은 `tls.handshake.type == 2` 로 ServerHello 를 골라 같은 `tls.handshake.extensions.supported_version` 과 `tls.handshake.version` 을 봅니다. 레코드 종류와 레코드 버전은 `tls.record.content_type`·`tls.record.version` 입니다[17].

Zeek 는 JSON 로그를 쓰도록 실행하면 jq 로 바로 읽을 수 있습니다[10].

```sh
zeek -C LogAscii::use_json=T -r sample.pcapng
jq -c '[.ts, ."id.orig_h", ."id.resp_h", .server_name, .version, .next_protocol, .established, .ssl_history]' ssl.log
```

`established` 는 핸드셰이크가 끝까지 성공했는지, `last_alert` 는 연결 중에 마지막으로 본 경고입니다[8]. 두 값으로 "접속을 시도했지만 핸드셰이크가 실패했다" 를 확인합니다.

### 키 로그 파일이 있을 때

키 로그 파일은 TLS 라이브러리가 연결마다 비밀 값을 적는 텍스트 파일입니다. 많은 구현이 환경 변수 `SSLKEYLOGFILE` 이 가리키는 경로에 이 파일을 써서 이런 이름이 붙었고, 형식은 2025년 12월 RFC 9850(Informational)으로 발행됐습니다[14]. Firefox·Chrome·curl 처럼 NSS·OpenSSL·BoringSSL 을 쓰는 프로그램이 이 방식을 지원하고, OpenSSL 은 3.4 부터 환경 변수를 직접 읽습니다[16]. Safari 와 옛 Edge 가 쓰는 SChannel·SecureTransport 는 2019년 기준으로 이 방식을 지원하지 않았습니다[16].

형식은 다음과 같습니다[14][15].

- UTF-8 텍스트이고 BOM 을 넣지 않습니다. 줄 끝은 CRLF·CR·LF 모두 받아야 합니다.
- 빈 줄과 `#` 로 시작하는 줄은 무시합니다.
- 나머지 줄은 `라벨 client_random 비밀` 세 값을 공백 하나로 구분한 비밀 하나입니다.
- client_random 은 ClientHello 의 random 32바이트를 16진수 64자로 쓴 값이고, 대문자·소문자 어느 쪽이든 됩니다.
- TLS 1.2 이하의 라벨은 `CLIENT_RANDOM` 이고 비밀은 48바이트(96자)입니다.
- TLS 1.3 의 라벨은 `CLIENT_EARLY_TRAFFIC_SECRET`, `EARLY_EXPORTER_SECRET`, `CLIENT_HANDSHAKE_TRAFFIC_SECRET`, `SERVER_HANDSHAKE_TRAFFIC_SECRET`, `CLIENT_TRAFFIC_SECRET_0`, `SERVER_TRAFFIC_SECRET_0`, `EXPORTER_SECRET` 이고, 비밀 길이는 해시가 SHA-256·384·512 일 때 64·96·128자입니다.
- ECH 를 쓴 연결에는 `ECH_SECRET`·`ECH_CONFIG` 라벨이 더 있습니다.
- 옛 NSS 의 `RSA` 라벨은 NSS 3.34 에서 없어졌습니다.

```text
# 만든 예시. 값은 앞뒤만 적고 줄였습니다.
CLIENT_HANDSHAKE_TRAFFIC_SECRET 4f1a…(64자)…0c3d 9b27…(64자)…e811
SERVER_HANDSHAKE_TRAFFIC_SECRET 4f1a…(64자)…0c3d 17d0…(64자)…52aa
CLIENT_RANDOM 8e03…(64자)…71bf 3c95…(96자)…d402
```

줄에는 암호 스위트 같은 연결 정보가 없어서, 복호하려면 같은 연결의 핸드셰이크가 담긴 캡처가 함께 있어야 합니다[14]. 줄 순서도 명세 순서를 따른다는 보장이 없습니다[14]. 키 로그 파일과 캡처는 client_random 으로 잇습니다. 캡처에서 ClientHello 의 `tls.handshake.random` 을 뽑아 파일의 둘째 값과 비교하면, 어느 연결의 비밀이 파일에 있는지 알 수 있습니다[14][17].

Wireshark 에서는 TLS 설정의 `(Pre)-Master-Secret log filename`(`tls.keylog_file`)에 파일 경로를 넣고, tshark 는 `-o tls.keylog_file:파일경로` 로 같은 설정을 줍니다[16][19]. 비밀을 캡처 파일에 함께 넣으려면 `editcap --inject-secrets tls,keys.txt in.pcap out-dsb.pcapng` 로 pcapng 의 Decryption Secrets Block 에 넣습니다[16]. 이 블록의 구조는 [pcapng 형식](../capture/pcapng.md) 에, 복호해서 분석하는 절차는 [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md) 에 있습니다. Wireshark 4.2 부터 "Export TLS Session Keys" 로 내보낸 파일에는 현재 캡처에서 쓰인 비밀만 들어갑니다[16].

RSA 개인 키로 복호하는 방법은 쓸 수 있는 경우가 좁습니다. 서버가 (EC)DHE 가 아닌 암호 스위트를 골랐고, TLS 1.2 이하이고, 키가 서버 인증서의 키이고, 재개가 아닌 연결(ClientKeyExchange 가 있는 연결)일 때만 됩니다[16].

## 포렌식에서 중요한 점

### 증명하는 것

- 이 시각에 이 내부 주소가 이 서버 주소·포트로 TLS 핸드셰이크를 시작했고, 끝까지 성공했는지(`established`) 또는 경고로 끝났는지(`last_alert`)[8].
- 클라이언트가 SNI 로 요청한 이름과 ALPN 으로 제안한 응용 프로토콜, 서버가 고른 버전·암호 스위트·ALPN 값[3][8].
- TLS 1.2 이하 연결이면 서버가 보낸 인증서 체인. 인증서로 알 수 있는 것은 [인증서로 서버 알아보기](../../02-artifacts/fingerprints/certificates.md) 에 있습니다.
- 암호화된 레코드의 방향·길이·순서. 내용은 몰라도 어느 방향으로 얼마만큼 오갔는지는 캡처로 확인됩니다.

보고서에는 "이 시각에 10.0.0.15 가 203.0.113.20:443 에 SNI `www.example.com` 으로 TLS 1.3 연결을 맺었고, 서버에서 약 2MB 를 받은 흐름 기록이 있다(만든 예시)" 처럼 기록으로 확인되는 만큼만 씁니다.

### 증명하지 못하는 것

- 암호화된 내용. URL 경로, 요청·응답 본문, HTTP 헤더는 복호하지 않으면 보이지 않습니다.
- TLS 1.3 연결의 서버 인증서. Zeek 는 TLS 1.3 연결에 인증서 필드를 쓰지 않습니다[7].
- ECH·ESNI 를 쓴 연결의 실제 서버 이름. 이런 연결은 ssl.log 에 `server_name` 이 남지 않고[7], 실제 이름은 암호화된 안쪽 ClientHello 에 들어 있습니다[14].
- SNI 의 이름이 실제로 연결된 서버라는 것. SNI 는 클라이언트가 적어 보내는 값입니다[3]. 인증서가 보이는 연결이면 Zeek `sni_matches_cert` 로 비교합니다([TLS·인증서 기록](../../02-artifacts/zeek/zeek-logs/ssl-x509-log.md)).
- 어떤 프로그램이나 사용자가 연결했는지. 지문(JA3·JA4)은 TLS 라이브러리와 설정을 알려 줄 뿐이고, 같은 지문을 여러 프로그램이 낼 수 있습니다([TLS 지문](../../02-artifacts/fingerprints/ja3-ja4.md)).

키 로그 파일이 없으면 복호에 필요한 키 자료는 끝점 메모리에서 찾아야 합니다. 2024년 기준으로 사후 메모리 이미지에서 TLS 1.3 키를 찾는 연구는 드뭅니다. TLS 구현마다 키를 메모리에 두는 방식이 달라 방법이 구현에 크게 좌우되고, 키가 메모리에 얼마나 오래 남는지도 거의 연구되지 않았습니다[21]. 메모리 분석은 [Windows 메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/)·[Linux 메모리 분석](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/memory-analysis.html) 에서 다룹니다.

### 시각

ClientHello·ServerHello 에는 시각 필드가 없고, TLS 1.3 의 random 은 32바이트 난수입니다[1]. TLS 1.2 에서는 random 의 앞 4바이트가 보낸 호스트 시계의 UTC 초(gmt_unix_time)이지만, 그 시계가 맞아야 한다는 요구는 없습니다[2]. 이 4바이트를 시각으로 읽으려면 같은 호스트의 다른 연결에서 값이 실제 시각과 맞는지 먼저 확인합니다. 난수로 채우는 구현이면 뜻 없는 값입니다.

그래서 TLS 연결의 시각은 기록한 쪽이 붙인 시각입니다.

| 값 | 뜻 | 기준 |
|---|---|---|
| 패킷 캡처의 패킷 시각 | 센서가 패킷을 받은 시각 | 캡처 형식에 따름([pcapng 형식](../capture/pcapng.md)) |
| Zeek `ssl.log` `ts` | Zeek 가 그 연결을 SSL/TLS 로 처음 알아챈 시각 | UTC 에포크 초[8]. 같은 연결의 conn.log `ts`(첫 패킷)보다 조금 늦을 수 있습니다[7] |
| Zeek `quic.log` `ts` | 그 줄의 첫 QUIC 패킷 시각 | UTC 에포크 초[11] |
| Suricata `tls` 의 `timestamp` | 기록을 쓰게 만든 패킷의 시각 | [프로토콜 기록](../../02-artifacts/suricata/eve-json/protocol-events.md) |
| 인증서 notBefore·notAfter | 발급자가 정한 유효기간 | UTC[4] |

Zeek JSON 로그의 `ts` 는 설정에 따라 에포크 실수(`1700000000.123456`)로도, ISO 문자열(`"2023-11-14T22:13:20.123456Z"`)로도 나옵니다(만든 예시)[7]. 여러 기록의 시각을 합치는 방법은 [네트워크 기록의 시각](../records/timestamps.md) 에 있습니다.

키 로그 파일의 줄에도 시각이 없습니다. 구현은 비밀이 생기는 대로 파일에 이어 씁니다[14]. 따라서 파일 수정 시각은 마지막 비밀을 쓴 무렵일 가능성이 있고, 줄마다의 연결 시각은 client_random 이 같은 ClientHello 패킷의 시각으로 찾습니다.

### 중간부터 잡힌 연결과 끊긴 핸드셰이크

캡처가 연결 중간부터 시작됐거나 TCP 세그먼트가 빠지면 Wireshark 가 TLS 레코드를 "Ignored Unknown Record" 로 표시할 수 있습니다[20]. ClientHello 가 캡처에 없으면 SNI·지문·제안 버전이 모두 빠지고, Zeek·Suricata 로그에도 그 값이 남지 않습니다. TCP 재조립 설정과 손실 판정은 [TCP 연결과 흐름](tcp-sessions.md) 에 있습니다.

Zeek 는 기본값(`SSL::disable_analyzer_after_detection = T`, `heartbleed.zeek`·`decryption.zeek` 를 불러오면 F)으로 TLS 를 알아본 뒤 암호화된 트래픽 분석을 멈추고 분석기를 연결에서 떼어 냅니다[8]. 그래서 핸드셰이크 뒤에 오간 경고나 레코드는 `ssl_history`·`last_alert` 에 반영되지 않을 가능성이 있습니다. 연결 전체의 레코드 순서가 필요하면 캡처를 직접 봅니다.

## 함정

**0x0303 을 TLS 1.2 로 읽는 실수.** TLS 1.3 의 ClientHello·ServerHello 는 legacy_version 이 0x0303 이고, 암호화된 레코드의 버전도 0x0303 입니다[1]. 버전은 "실제 버전을 판별하는 순서" 대로 supported_versions 로 판별합니다.

**application_data 레코드가 모두 응용 데이터는 아닙니다.** TLS 1.3 은 암호화된 핸드셰이크 메시지와 경고도 바깥 type 23 으로 보냅니다[1]. 레코드 수와 크기로 "데이터를 몇 번 보냈다" 고 쓰지 않습니다.

**세션 ID 가 있다고 재개가 아닙니다.** TLS 1.3 호환 모드에서는 클라이언트가 재개하지 않아도 새 32바이트 세션 ID 를 넣습니다[1]. 재개 여부는 Zeek `resumed`, Suricata `session_resumed` 로 봅니다. 다만 2020년에 만든 Zeek 문서의 TLS 1.3 예시는 모두 `resumed: true` 이고[7], 현재 Zeek 는 TLS 1.3 재개를 클라이언트가 pre_shared_key 확장을 보냈는지로 판단합니다[8]. 센서의 Zeek 버전을 확인하고 읽습니다. 판정 조건은 [TLS·인증서 기록](../../02-artifacts/zeek/zeek-logs/ssl-x509-log.md) 에 있습니다.

**SNI 가 명세를 지키지 않을 수 있습니다.** 명세는 SNI 에 IP 주소를 넣는 것을 금지하지만[3], RDP 연결의 ssl.log 에 `server_name` 이 IP 주소로 남는 경우가 있습니다[12]. SNI 값은 클라이언트 구현이 넣은 문자열 그대로라고 보고 읽습니다.

**SNI 가 없는 연결.** 클라이언트가 IP 주소로 직접 접속했거나 SNI 를 보내지 않는 프로그램이거나 ECH 를 쓴 경우입니다[3][7]. ECH 로 이름을 숨기고 DNS over HTTPS 까지 쓰면 이름을 알 수 있는 DNS 기록도 없습니다[7]. 이때는 서버 주소, 인증서(TLS 1.2 이하), 지문, 같은 시간대의 다른 기록으로 서버를 추정합니다.

**포트로 TLS 를 판단하지 않습니다.** 587 처럼 평문으로 시작해 STARTTLS 로 바뀌는 연결이 있고[6], 위 표처럼 443 말고도 TLS 를 쓰는 포트가 많습니다. 캡처에서는 레코드 머리(첫 바이트 `16`, 다음 두 바이트 `03 0x`)와 핸드셰이크 type 1 로 ClientHello 를 확인합니다.

**재개된 연결에는 인증서가 없습니다.** TLS 1.3 에서 PSK 로 재개하면 서버가 Certificate 를 보내지 않고[1], 세션 ID 로 재개한 연결에서도 Suricata 는 인증서 없이 `session_resumed` 만 씁니다[13]. 인증서가 없는 줄을 "인증서 없이 접속했다" 로 해석하지 않습니다.

**키 로그 파일은 운영 시스템에 있으면 안 되는 파일입니다.** 이 파일이 끝점 밖으로 나가면 TLS 의 보호가 모두 무너지므로, 운영 시스템에서는 이 방식을 쓰면 안 됩니다(MUST NOT)[14]. 조사 대상에서 이 파일이나 `SSLKEYLOGFILE` 설정이 발견되면 그 자체가 누가 언제 설정했는지 확인할 발견 사항입니다. 파일을 가진 사람은 기록된 연결을 복호할 수 있으므로 증거로 다룰 때 접근을 제한합니다[14].

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| Wireshark·tshark | `tls` 표시 필터, `tls.handshake.*`·`tls.record.*` 필드 추출, `tls.keylog_file` 로 복호[16][17][19]. 사용법은 [Wireshark·tshark로 읽기](../../03-techniques/analysis/wireshark.md) |
| editcap | `--inject-secrets tls,키파일` 로 키 로그를 pcapng 에 넣기[16] |
| Zeek | `ssl.log`·`x509.log`·`quic.log`[8][10][11] |
| Suricata | EVE `tls` 기록[13] |
| JA3·JA4 구현 | ClientHello·ServerHello 지문 계산([TLS 지문](../../02-artifacts/fingerprints/ja3-ja4.md)) |

## 참고 문헌

1. E. Rescorla, RFC 8446 「The Transport Layer Security (TLS) Protocol Version 1.3」, 2018. https://www.rfc-editor.org/rfc/rfc8446.txt
2. T. Dierks, E. Rescorla, RFC 5246 「The Transport Layer Security (TLS) Protocol Version 1.2」, 2008. https://www.rfc-editor.org/rfc/rfc5246.txt
3. D. Eastlake 3rd, RFC 6066 「Transport Layer Security (TLS) Extensions: Extension Definitions」, 2011. https://www.rfc-editor.org/rfc/rfc6066.txt
4. D. Cooper 외, RFC 5280 「Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile」, 2008. https://www.rfc-editor.org/rfc/rfc5280.txt
5. Z. Hu 외, RFC 7858 「Specification for DNS over Transport Layer Security (TLS)」, 2016. https://www.rfc-editor.org/rfc/rfc7858.txt
6. K. Moore, C. Newman, RFC 8314 「Cleartext Considered Obsolete: Use of Transport Layer Security (TLS) for Email Submission and Access」, 2018. https://www.rfc-editor.org/rfc/rfc8314.txt
7. Zeek 문서 — ssl.log. https://github.com/zeek/zeek-docs/blob/master/logs/ssl.rst
8. Zeek 문서 — base/protocols/ssl/main.zeek (SSL::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/main.zeek.rst
9. Zeek 문서 — base/protocols/ssl/consts.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/consts.zeek.rst
10. Zeek 문서 — quic.log. https://github.com/zeek/zeek-docs/blob/master/logs/quic.rst
11. Zeek 문서 — base/protocols/quic/main.zeek (QUIC::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/quic/main.zeek.rst
12. Zeek 문서 — rdp.log. https://github.com/zeek/zeek-docs/blob/master/logs/rdp.rst
13. Suricata 사용자 안내서 — EVE JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
14. M. Thomson, Y. Rosomakho, H. Tschofenig, RFC 9850 「The SSLKEYLOGFILE Format for TLS」, 2025. https://www.rfc-editor.org/info/rfc9850 (본문: https://tlswg.org/sslkeylogfile/draft-ietf-tls-keylogfile.html)
15. Mozilla NSS — Key Log Format. https://udn.realityripple.com/docs/Mozilla/Projects/NSS/Key_Log_Format
16. Wireshark Wiki — TLS. https://wiki.wireshark.org/TLS
17. Wireshark Display Filter Reference — Transport Layer Security. https://www.wireshark.org/docs/dfref/t/tls.html
18. Wireshark Display Filter Reference — Frame. https://www.wireshark.org/docs/dfref/f/frame.html
19. tshark 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
20. Wireshark User's Guide — Advanced Topics (TCP Reassembly). https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_advanced.adoc
21. Daniel Baier, Alexander Basse, Jan-Niclas Hilgert, Martin Lambertz, 「TLS key material identification and extraction in memory: Current state and future challenges」, Forensic Science International: Digital Investigation 49, 301766, 2024. doi:10.1016/j.fsidi.2024.301766
