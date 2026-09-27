---
title: "인증서로 서버 알아보기"
parent: "아티팩트 · 식별 정보"
nav_order: 310
---

# 인증서로 서버 알아보기 (Certificates)

TLS 연결을 맺을 때 서버는 자기 X.509 인증서와 그 인증서를 발급한 중간 인증서들을 클라이언트에 보냅니다. TLS 1.2 이하에서는 이 인증서가 암호화되지 않은 채 오가서, 패킷 캡처나 Zeek·Suricata 로그에 주체 이름·발급자·일련번호·유효기간·지문이 남습니다. 같은 인증서 지문이 여러 IP 와 여러 날짜에 나오면 그 서버들을 하나로 묶을 수 있지만, TLS 1.3 에서는 인증서가 암호화되고 인증서 안의 값은 만든 사람이 정하므로, 무엇이 기록으로 확인되는지를 나눠서 읽어야 합니다.

## 무엇을 기록하나 · 왜 생기나

TLS 핸드셰이크에서 서버는 Certificate 메시지로 인증서 체인을 보내고, 클라이언트는 이 체인으로 서버가 접속하려던 상대인지 확인합니다. 인증서는 발급자(CA)가 서명한 X.509 구조이고, 누구의 인증서인지(주체·주체 대체 이름), 누가 발급했는지(발급자·일련번호), 언제까지 유효한지(유효기간), 어떤 공개키를 쓰는지가 들어 있습니다[1]. 핸드셰이크 흐름과 메시지 순서는 [TLS와 인증서](../../01-foundations/protocols/tls.md)에 있습니다.

조사에서는 이 인증서를 서버를 알아보는 식별 정보로 씁니다. IP 주소는 호스팅 업체가 다시 나눠 주거나 CDN 이 여러 고객에게 함께 쓰지만, 인증서 전체를 해시한 지문(fingerprint)은 인증서 하나를 가리킵니다[19]. 그래서 "이 내부 PC 가 접속한 서버가 보낸 인증서" 를 알면, 같은 인증서를 보낸 다른 IP·다른 시각의 연결을 찾을 수 있습니다. 반대로 TLS 1.3 연결이나 세션을 재개한 연결에서는 인증서가 보이지 않아 이 방법을 쓸 수 없습니다.

클라이언트도 인증서를 보낼 때가 있습니다. 서버가 CertificateRequest 를 보낸 경우에만 클라이언트가 Certificate 메시지를 보내고, 이때 목록이 비어 있을 수도 있습니다[2]. 클라이언트 인증서는 Zeek 의 `client_cert_chain_fps`, x509.log 의 `client_cert` 필드와 Suricata EVE 의 `tls.client` 객체에 따로 남습니다[6][7][16].

## 위치와 버전별 차이

인증서 정보가 남는 곳은 다음과 같습니다.

| 기록 | 남는 것 | 조건 |
|---|---|---|
| 패킷 캡처(pcap·pcapng) | Certificate 메시지 안의 인증서 DER 바이트 전체 | TLS 1.2 이하, 또는 복호 키가 있는 캡처 |
| Zeek `x509.log` | 인증서 하나마다 한 줄. 주체·발급자·일련번호·유효기간·주체 대체 이름·지문 | TLS 1.2 이하. 같은 인증서는 기본으로 하루에 한 번[6] |
| Zeek `ssl.log` | 연결마다 서버 체인의 지문 목록(`cert_chain_fps`), SNI 와 인증서가 맞는지(`sni_matches_cert`) | Zeek 4.1 이상[7][9] |
| Suricata EVE `tls` | 서버 인증서의 `subject`·`issuerdn`, 확장 기록이면 `serial`·`fingerprint`·`notbefore`·`notafter` | TLS 1.2 이하, `extended: yes` 또는 `custom`[11][12] |
| Suricata 인증서 파일 | 규칙에 `tls.store` 를 쓴 경우 인증서를 디스크에 저장 | 저장 폴더는 `output.tls-store.certs-log-dir`[13] |
| Suricata `tls.log` | 텍스트 한 줄에 SNI·버전·유효기간·SHA-1 지문 | Suricata 8.0 에서 폐지 예정, 9.0 에서 제거[14][15] |
| 복호하는 프록시·방화벽 | 제품마다 다름 | TLS 1.3 도 볼 수 있는 곳. [웹 프록시 로그](../devices/proxy-logs.md) 참고 |

TLS 1.3 에서는 ServerHello 다음의 EncryptedExtensions·Certificate 부터 핸드셰이크 키로 암호화됩니다[2]. 그래서 수동으로 캡처한 트래픽에는 서버 인증서가 없고, Zeek 도 TLS 1.3 연결에는 인증서 식별자를 쓰지 않으며 x509.log 줄도 만들지 않습니다[4]. SNI 는 ClientHello 에 평문으로 있어 TLS 1.3 에서도 보이지만, ESNI·ECH 를 쓴 연결은 `ssl.log` 에 `server_name` 이 없습니다[4][5]. SNI 와 ClientHello 지문은 [TLS 지문 (JA3·JA4)](ja3-ja4.md)에서 다룹니다.

Zeek 는 4.1 에서 인증서 기록 방식을 크게 바꿨습니다[6][7][8][9]. 공식 문서의 로그 예시(`logs/ssl.rst`·`logs/x509.rst`)는 바뀌기 전 형식이라, 예시와 실제 로그의 필드가 다를 수 있습니다[4][5].

| 항목 | Zeek 4.0 까지 | Zeek 4.1 부터 |
|---|---|---|
| `ssl.log` 의 체인 | `cert_chain_fuids`·`client_cert_chain_fuids`(파일 ID) | `cert_chain_fps`·`client_cert_chain_fps`(인증서 지문) |
| `ssl.log` 의 `subject`·`issuer` | 기본으로 기록 | 기본으로 기록하지 않음. `SSL::log_include_server_certificate_subject_issuer` 를 켜면 기록 |
| `x509.log` 의 키 | `id`(파일 ID) | `fingerprint`(SHA-256), 파일 ID 없음 |
| 같은 인증서의 중복 기록 | 볼 때마다 기록 | 기본으로 하루에 한 번 |
| `files.log` 의 인증서 | 기록 | 기본으로 기록하지 않음(`X509::log_x509_in_files_log = F`) |
| 새 필드 | — | `host_cert`, `client_cert`, `sni_matches_cert`, `ssl_history`. OCSP 로그 기본으로 켜짐 |

Zeek 로그의 필드 하나하나는 [TLS·인증서 기록 (ssl.log·x509.log)](../zeek/zeek-logs/ssl-x509-log.md)에, Suricata `tls` 기록이 생기는 조건과 필드는 [프로토콜 기록](../suricata/eve-json/protocol-events.md)에 있습니다.

## 구조

인증서는 `tbsCertificate`(서명할 본문), `signatureAlgorithm`, `signatureValue` 세 부분으로 된 ASN.1 SEQUENCE 이고, DER 로 인코딩합니다[1]. 서버를 알아보는 데 쓰는 값은 모두 `tbsCertificate` 안에 있습니다.

| 필드 | 내용 | 조사에서 볼 점 |
|---|---|---|
| `version` | v1(0)·v2(1)·v3(2). 생략하면 v1 | 확장이 있으면 v3 입니다[1]. |
| `serialNumber` | CA 가 붙이는 양의 정수, 20옥텟까지 | 발급자 이름과 일련번호를 함께 봐야 인증서 하나가 정해집니다. 규칙을 따르지 않는 CA 는 음수나 0 을 쓰기도 합니다[1]. |
| `signature` | 서명 알고리즘 | 끝의 `signatureAlgorithm` 과 같아야 합니다[1]. |
| `issuer` | 발급자 이름(DN) | 자체 서명 인증서는 `subject` 와 같습니다. |
| `validity` | `notBefore`·`notAfter` | 발급자가 정한 유효기간이고 연결 시각과 관계없습니다. |
| `subject` | 주체 이름(DN). 흔히 CN 에 호스트 이름 | 비어 있을 수 있고, 이때는 주체 대체 이름 확장이 critical 이어야 합니다[1]. |
| `subjectPublicKeyInfo` | 공개키 알고리즘과 공개키 | 인증서를 새로 발급해도 같은 키를 쓰면 이 값이 같습니다. |
| `extensions` | `extnID`(OID)·`critical`(기본 FALSE)·`extnValue` | 주체 대체 이름(SAN), 기본 제약(CA 여부), 키 식별자, CT 의 SCT 등이 여기에 들어갑니다[1][3]. |

주체 대체 이름 (Subject Alternative Name, SAN) 에는 DNS 이름·IP 주소·전자 메일·URI 를 넣을 수 있습니다[1]. DNS 이름을 인증서에 넣을 때는 SAN 을 반드시 써야 하고, 주체 필드에는 domainComponent 로 함께 넣을 수만 있습니다[1]. CA 는 SAN 의 모든 값을 확인해야 하므로, 인증서가 어느 도메인용인지는 주체의 CN 보다 SAN 으로 판단합니다[1].

유효기간은 UTCTime 이나 GeneralizedTime 으로 씁니다. 2049년까지는 UTCTime `YYMMDDHHMMSSZ`, 2050년부터는 GeneralizedTime `YYYYMMDDHHMMSSZ` 를 쓰고, 둘 다 GMT(`Z`)이며 초까지 적습니다[1]. UTCTime 의 두 자리 연도는 50 이상이면 19YY, 50 미만이면 20YY 로 읽습니다[1]. 만료일이 따로 없는 인증서는 `notAfter` 에 `99991231235959Z` 를 넣습니다[1].

발급자와 주체가 같은 CA 인증서를 자체 발행 (self-issued) 인증서라 하고, 그중 인증서 안의 공개키로 서명이 검증되는 것을 자체 서명 (self-signed) 인증서라 합니다[1]. 인증서 지문은 인증서 전체 DER 바이트의 해시입니다. 해시가 같은 두 인증서는 같은 인증서로 봅니다[19].

## 증거로서 의미

### 증명하는 것

TLS 1.2 이하 연결이거나 복호한 지점의 기록이라면, "이 시각에 이 서버 IP·포트가 이 인증서 체인을 보냈다" 는 것을 증명합니다. 주체·발급자·일련번호·SAN·유효기간·지문이 모두 그 인증서에 들어 있던 값입니다[4][6]. 같은 지문이 다른 IP 나 다른 날짜의 연결에도 나오면, 그 서버들이 같은 인증서를 쓴다고 묶을 수 있습니다.

Zeek 는 클라이언트가 보낸 SNI 가 인증서 이름과 맞는지 `sni_matches_cert` 로 남깁니다. 맞으면 `T`, 다르면 `F`, 클라이언트가 SNI 를 보내지 않았으면 값이 없습니다[7]. `policy/protocols/ssl/validate-certs.zeek` 을 불러온 센서라면 `validation_status` 에 체인을 검증한 결과가 남습니다[7]. 검증에 쓰는 루트 인증서 목록은 Zeek 에 들어 있는 `SSL::root_certs`(`mozilla-ca-list.zeek`)입니다[28]. 이 두 값으로 "SNI 에 적힌 도메인과 다른 인증서를 받았다", "공인 CA 로 검증되지 않는 인증서였다" 를 기록으로 보일 수 있습니다.

### 증명하지 못하는 것

- **클라이언트가 인증서를 받아들였는지.** `ssl.log` 의 `established` 는 핸드셰이크가 끝났는지만 알려 줍니다[7]. 브라우저가 경고를 띄웠는지, 사용자가 경고를 무시하고 들어갔는지는 네트워크 기록에 없습니다.
- **인증서 이름이 실제 운영자라는 것.** 자체 서명 인증서는 누구나 주체·발급자·일련번호·유효기간을 마음대로 넣어 만들 수 있습니다. openssl 도 `-subj`·`-set_serial`·`-not_before`·`-not_after` 로 이 값을 정합니다[19].
- **인증서가 없었다는 것.** TLS 1.3 에서 x509.log 가 없는 것은 인증서가 암호화됐기 때문입니다[2][4]. 세션을 재개한 TLS 1.2 이하 연결도 인증서를 주고받지 않아서, Suricata 는 `session_resumed: true` 만 남기고 `subject`·`issuerdn` 을 쓰지 않습니다[11].
- **자체 서명 = 악성.** 2015–2016년 기업망과 샌드박스 데이터에서 자체 서명 인증서를 쓴 TLS 세션은 기업망 세션 1,500,005개 중 1,352개(약 0.09%), 악성 코드가 맺은 세션 133,744개 중 947개(약 0.7%)였습니다[22]. 악성 코드 쪽이 약 10배 잦지만 양쪽 모두 소수입니다. 2013년 인터넷 전체를 조사한 결과로는 한 번 조사할 때마다 나온 신뢰되지 않는 인증서 평균 490만 개 중 48% 가 자체 서명이었고, 자체 서명 인증서의 33% 는 석 달 동안 36번 조사하는 사이 한 번만 보였습니다[23]. 이런 인증서는 대부분 임베디드 장비가 주기적으로 새로 만드는 것으로 보여서, 자체 서명과 짧은 수명만으로 수상하다고 판단하지 않습니다.
- **일련번호 하나로 인증서 하나.** 일련번호는 발급자 안에서만 유일합니다[1].

## 시각 해석

인증서와 관련된 시각은 뜻이 서로 다릅니다.

| 값 | 뜻 | 기준·형식 |
|---|---|---|
| 인증서 `notBefore`·`notAfter` | 발급자가 정한 유효기간 | UTC(GMT)[1]. 자체 서명이면 만든 사람이 정한 값[19] |
| Zeek `x509.log` `ts` | 센서가 그 인증서를 본 시각 | UTC 에포크 초. 문서 예시에서는 한 체인의 인증서 네 개가 같은 `ts` 입니다[4] |
| Zeek `certificate.not_valid_before`·`not_valid_after` | 인증서의 유효기간 | JSON 에서는 에포크 초 정수(예: `1590969600`)[4] |
| Zeek `ssl.log` `ts` | Zeek 가 그 TLS 연결을 처음 알아챈 시각 | UTC 에포크 초[7] |
| Suricata `tls.notbefore`·`notafter` | 인증서의 유효기간 | `2017-01-04T10:48:43` 형식, 시간대 표시 없음[11][16]. 값 자체는 UTC[1] |
| Zeek `ocsp.log` `thisUpdate`·`nextUpdate`·`revoketime` | OCSP 응답에 적힌 시각 | Zeek time 형[10] |

`notBefore` 는 "서버가 이때부터 운영됐다" 는 뜻이 아닙니다. 공인 CA 인증서라면 발급 시각에 가깝다고 볼 수 있지만, 연결이 있었던 시각은 연결 기록의 `ts` 로만 말합니다. Suricata 의 `notbefore` 에는 시간대 표시가 없으므로 다른 기록과 합칠 때 UTC 오프셋을 붙입니다. 여러 기록의 시각을 합치는 방법은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)에 있습니다.

만료된 인증서도 흔합니다. 2013년 조사에서 브라우저가 신뢰하는 CA 의 인증서를 쓰는 호스트의 약 5.8% 가 이미 만료된 인증서를 쓰고 있었고, 인증서의 22% 는 만료된 뒤에야 서버에서 내려갔습니다[23]. 연결 시각이 `notAfter` 뒤라는 사실만으로 악성 서버라고 쓰지 않습니다.

## 함정과 한계

**도구마다 지문 해시가 다릅니다.** Zeek 4.1 이상의 `fingerprint` 와 `cert_chain_fps` 는 기본 SHA-256 이고 `X509::hash_function` 으로 바꿀 수 있습니다[6][9]. Suricata 의 `fingerprint` 와 규칙 키워드 `tls.cert_fingerprint` 는 SHA-1 이고[11][13], openssl `-fingerprint` 도 다른 해시를 지정하지 않으면 SHA-1 입니다[19]. 평판 목록인 abuse.ch SSLBL 의 인증서 목록도 SHA-1 지문입니다[21]. 도구가 다른 기록끼리 대조하려면 인증서 DER 을 구해 같은 해시로 다시 계산합니다.

**같은 값도 표기가 다릅니다.** Suricata 는 지문을 콜론으로 나눈 소문자 16진(`8f:51:12:06:…`), 일련번호를 콜론으로 나눈 대문자 16진(`0C:00:99:B7:…`)으로 씁니다[11]. `tls.fingerprint` 키워드의 버퍼도 소문자라서 규칙의 값을 소문자로 써야 합니다[13]. Zeek 문서 예시의 일련번호는 콜론 없는 대문자 16진(`0B58BC3898391F36592BA1BE1F6B03EF`)입니다[4]. Cobalt Strike 기본 인증서를 찾는 Sigma 규칙은 Zeek x509 로그의 `certificate.serial` 을 `8BB00EE` 로 비교합니다[20]. 콜론·대소문자·앞자리 0 때문에 문자열 비교가 빗나갈 수 있으므로, 비교 전에 콜론을 지우고 대소문자를 맞춘 뒤, 앞자리 0 이 어떻게 적혔는지 실제 로그에서 확인합니다.

**Zeek 는 같은 인증서를 하루에 한 번만 씁니다.** 같은 인증서(지문과 `host_cert`·`client_cert` 가 같은 것)는 `X509::relog_known_certificates_after`(기본 1일) 동안 다시 기록하지 않고, `0secs` 로 하면 중복 제거를 끕니다[6]. 설정에 따라 워커마다 따로 중복을 제거해 같은 인증서가 여러 번 나올 수도 있습니다[6]. 그래서 x509.log 줄 수는 연결 수가 아니고, 연결마다의 인증서는 `ssl.log` 의 `cert_chain_fps` 로 찾아 x509.log 의 `fingerprint` 와 잇습니다.

**체인 순서를 믿지 않습니다.** 첫 번째 인증서가 보낸 쪽의 인증서여야 한다는 것만 필수이고, 나머지는 앞 인증서를 인증하는 순서가 권장일 뿐입니다[2]. 루트 인증서는 빠질 수 있고, 쓸데없는 인증서가 섞이거나 순서가 틀린 체인도 받는 쪽이 처리하도록 되어 있습니다[2]. 2013년 조사에서는 호스트의 42.2% 가 필요 없는 루트를 체인에 넣었고 0.24% 는 순서가 틀렸습니다[23]. Zeek 는 끝 호스트 인증서에 `host_cert` 를 `T` 로 표시하므로 이 값으로 서버 인증서를 골라냅니다[6].

**Suricata 필드 이름이 문서와 출력에서 다릅니다.** 형식 문서의 필드 설명은 `issuer`, `custom` 설정 이름은 `issuer`·`not_before`·`not_after` 이지만, 실제 EVE 출력 키는 `issuerdn`·`notbefore`·`notafter` 입니다[11][12][16]. `custom` 을 쓰면 `extended` 가 꺼지므로, `custom` 목록에 없는 필드는 기록되지 않습니다[12].

**유효기간 키워드는 체인을 검증하지 않습니다.** Suricata 의 `tls_cert_valid`·`tls_cert_expired` 는 인증서의 유효기간만 보고 체인 검증은 하지 않습니다[13]. 이 키워드로 뜬 경고를 "신뢰할 수 없는 인증서" 로 쓰지 않습니다.

**TLS 1.3 이 재개로 잘못 표시된 로그가 있습니다.** Zeek 4.0 전에는 일부 TLS 1.3 세션을 `resumed: T` 로 잘못 표시했고 4.0 에서 고쳤습니다[9]. TLS 1.3 호환 모드에서는 클라이언트가 늘 비어 있지 않은 세션 ID 를 보내 TLS 1.2 의 재개처럼 보입니다[2]. 오래된 센서 로그에서 인증서가 없는 이유를 재개로 판단하기 전에 버전을 확인합니다.

**인증서 값은 흉내 낼 수 있고, 바꿀 수도 있습니다.** 인증서의 문자열은 만든 사람이 넣은 값이라, 악성 서버가 정상 서버처럼 보이려고 발급자·SAN·유효기간을 흉내 낼 수 있습니다[22]. 반대로 C2 서버가 인증서 값을 무작위로 바꾸면 지문과 일련번호로는 묶이지 않습니다. JA4X 는 인증서의 값이 아니라 인증서를 만든 방식(이름 항목과 확장의 구성)으로 지문을 만들어, 값을 바꿔도 같은 도구로 만든 인증서를 묶을 수 있습니다[24]. JA4X 계산 방법은 [TLS 지문 (JA3·JA4)](ja3-ja4.md)에 있습니다.

**일련번호 규칙은 오탐이 날 수 있습니다.** 일련번호는 발급자 안에서만 유일하므로, 일련번호 하나로 거는 탐지 규칙은 다른 발급자의 인증서와 겹칠 수 있습니다[1][20]. 규칙에 걸린 인증서는 발급자와 지문까지 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

RFC 5280 부록 C.1 의 578바이트 자체 서명 CA 인증서를 앞부분만 따라가 봅니다. 아래 바이트는 명세에 적힌 구조와 값으로 만든 예시입니다[1].

```
오프셋  바이트                                   뜻
0       30 82 02 3E                              SEQUENCE, 길이 574 (인증서 전체)
4       30 82 01 A7                              SEQUENCE, 길이 423 (tbsCertificate)
8       A0 03                                    [0] 명시 태그 (version)
10      02 01 02                                 INTEGER 2 = v3
13      02 01 11                                 INTEGER 17 = 일련번호
16      30 0D                                    SEQUENCE (서명 알고리즘)
18      06 09 2A 86 48 86 F7 0D 01 01 05         OID 1.2.840.113549.1.1.5 (sha1WithRSAEncryption)
29      05 00                                    NULL
31      30 43 ...                                SEQUENCE, 길이 67 (issuer: dc=com, dc=example, cn=Example CA)
100     30 1E                                    SEQUENCE, 길이 30 (validity)
102     17 0D 30 34 30 34 33 30 31 34 32 35 33 34 5A   UTCTime "040430142534Z"
117     17 0D 30 35 30 34 33 30 31 34 32 35 33 34 5A   UTCTime "050430142534Z"
132     30 43 ...                                SEQUENCE, 길이 67 (subject: issuer 와 같음)
```

첫 바이트 `30` 은 SEQUENCE, `82` 는 뒤의 2바이트가 길이라는 뜻이라 `02 3E` = 574 입니다. 머리 4바이트와 합치면 인증서 전체가 578바이트입니다. 태그 `17` 은 UTCTime 이고 13바이트 ASCII `040430142534Z` 는 2004-04-30 14:25:34 UTC 로 읽습니다. 연도 04 가 50 미만이라 2004 년입니다[1]. 오프셋 31 의 발급자와 오프셋 132 의 주체가 같은 이름이므로 이 인증서는 자체 발행이고, 명세의 설명대로 자체 서명 CA 인증서입니다[1].

캡처에서 인증서를 찾을 때는 TLS 레코드 머리의 content type `16`(handshake)과 핸드셰이크 종류 `0B`(certificate, 11) 뒤에서 이 `30 82` 로 시작하는 DER 을 찾습니다[2]. 인증서 목록 안에서는 인증서마다 3바이트 길이가 앞에 붙고(`cert_data<1..2^24-1>`), TLS 1.3 에서는 이 메시지 전체가 암호화되어 있습니다[2].

### 공개 도구로 한 번

tshark 로 Certificate 메시지만 골라 인증서 값을 뽑습니다. 아래는 만든 예시 파일 이름이고, 필드 이름은 Wireshark 필드 참조에 있는 것입니다[17][18].

```
tshark -r capture.pcapng -Y "tls.handshake.type == 11" -T fields \
  -e frame.time_epoch -e ip.src -e tcp.srcport -e ip.dst \
  -e x509af.serialNumber -e x509af.utcTime -e x509ce.dNSName
```

한 메시지에 체인의 인증서가 여러 개 있으면 값 여러 개가 쉼표로 이어져 나옵니다(`-E aggregator` 기본값)[25]. `x509af.notBefore`·`x509af.notAfter` 는 시각 문자열이 아니라 부호 없는 정수 필드라서, 유효기간은 `x509af.utcTime`(2050년 이후는 `x509af.generalizedTime`)으로 뽑습니다[18]. `x509af.serialNumber` 는 바이트 값입니다[18].

인증서 DER 을 파일로 꺼내 지문을 계산하려면 `-e tls.handshake.certificate` 로 바이트를 16진 문자열로 받아 파일로 되돌린 뒤 openssl 로 읽습니다[17][19].

```
openssl x509 -inform DER -in server.der -noout -subject -issuer -serial -dates -ext subjectAltName
openssl x509 -inform DER -in server.der -noout -fingerprint -sha256
openssl x509 -inform DER -in server.der -noout -fingerprint -sha1
```

openssl 은 `-dates` 를 기본으로 `Jul 31 22:20:50 2017 GMT` 같은 형식으로 보여 주고, `-dateopt iso_8601` 로 ISO 8601 형식으로 바꿀 수 있습니다[19]. SHA-256 지문은 Zeek 의 `fingerprint` 와, SHA-1 지문은 Suricata 의 `fingerprint` 와 대조합니다. 콜론과 대소문자는 비교 전에 맞춥니다.

Zeek JSON 로그에서는 연결과 인증서를 지문으로 잇습니다.

```
# 연결마다 서버 IP, SNI, 서버 인증서 지문, SNI 일치 여부
jq -r 'select(.cert_chain_fps) | [.ts, ."id.resp_h", .server_name, .cert_chain_fps[0], .sni_matches_cert] | @tsv' ssl.log

# 끝 호스트 인증서의 지문, 주체, 발급자, 일련번호, SAN DNS 이름
jq -r 'select(.host_cert == true) | [.fingerprint, ."certificate.subject", ."certificate.issuer", ."certificate.serial", ((."san.dns" // []) | join(","))] | @tsv' x509.log
```

첫 결과의 네 번째 값으로 둘째 결과를 찾으면, 하루에 한 번만 기록된 인증서 내용을 모든 연결에 붙일 수 있습니다. 같은 지문으로 첫 결과를 다시 모으면 그 인증서를 보낸 서버 IP 목록이 나옵니다.

Suricata EVE 에서는 확장 기록을 켠 센서라면 다음처럼 뽑습니다.

```
jq -r 'select(.event_type=="tls" and .tls.fingerprint) | [.timestamp, .dest_ip, .tls.sni, .tls.subject, .tls.issuerdn, .tls.serial, .tls.fingerprint, .tls.notafter] | @tsv' eve.json
```

결과는 예를 들어 다음과 같은 모양입니다(만든 예시).

```
2026-03-02T14:11:05.482913+0000	203.0.113.80	www.example.com	CN=www.example.com	C=US, O=Example CA, CN=Example Issuing CA	0A:1B:2C:3D:4E:5F	3f:2a:91:0c:5b:77:e4:12:9d:08:c6:af:31:5e:02:bb:6d:40:9a:c1	2026-04-05T23:59:59
```

## 교차 검증

인증서 하나로 결론을 내지 않고, 같은 연결과 같은 서버의 다른 기록과 맞춰 봅니다.

| 함께 볼 기록 | 알 수 있는 것 | 링크 |
|---|---|---|
| Zeek `conn.log`·흐름 기록 | 그 연결의 지속 시간과 주고받은 바이트 수 | [연결 기록](../zeek/zeek-logs/conn-log.md), [흐름 기록](../../01-foundations/records/flow-records.md) |
| DNS 기록 | SNI·SAN 의 도메인을 누가 언제 물었고 어떤 IP 를 받았는지 | [DNS 기록](../zeek/zeek-logs/dns-log.md), [DNS 분석](../../03-techniques/analysis/dns-analysis.md) |
| TLS 지문 | 같은 서버에 접속한 클라이언트 프로그램의 JA3·JA4, 서버의 JA3S·JA4S, 인증서 구성의 JA4X | [TLS 지문 (JA3·JA4)](ja3-ja4.md) |
| 프록시 로그 | CONNECT 요청의 호스트 이름과, 복호하는 프록시라면 TLS 1.3 인증서 | [웹 프록시 로그](../devices/proxy-logs.md) |
| 평판 목록·탐지 규칙 | abuse.ch SSLBL 인증서 목록(등록일 UTC·SHA-1 지문·사유), Sigma·Suricata 규칙 | [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md) |
| 인증서 투명성(CT) 로그 | 공인 CA 가 그 도메인에 언제 어떤 인증서를 발급했는지 | [TLS와 인증서](../../01-foundations/protocols/tls.md) |
| 호스트 쪽 브라우저 기록 | 그 시각에 브라우저가 연 주소 | [Windows 크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) |

abuse.ch SSLBL 은 인증서 목록을 CSV 와 Suricata 규칙으로 제공합니다. 규칙은 `tls.fingerprint` 를 쓰는 판과 더 빠른 `tls_cert_fingerprint` 판(Suricata 4.1.0 이상) 두 가지이고 둘 중 하나만 씁니다. IP 는 다시 쓰이므로 기본 C2 IP 목록은 최근 30일 것만 담고, 지금까지 나온 IP 전체는 따로 받는 목록(Aggressive)에 있습니다[21]. 인증서 투명성은 발급된 인증서를 공개 로그에 남겨 누구나 감사할 수 있게 하는 방식이라, 공인 CA 인증서라면 발급 이력을 로그에서 찾을 수 있습니다[3]. 같은 호스트의 평문 HTTP User-Agent 와 TLS 매개변수가 서로 맞지 않는 것도 침해 지표가 될 수 있습니다[22].

인증서를 C2 조사에 쓰는 흐름은 [악성 코드가 C2 서버와 통신했나](../../04-scenarios/intrusion/c2-communication.md)에, 암호화된 트래픽 전체를 다루는 방법은 [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md)에 있습니다.

## 실습

FoxIO JA4 저장소의 `pcap/` 폴더에는 TLS 시험 캡처가 있고, `python/test/testdata/` 에 파일마다 기대 출력 JSON 이 있습니다[24][26]. Wireshark 위키 TLS 페이지의 `tls12-dsb.pcapng` 은 복호 키가 들어 있는 TLS 1.2 캡처입니다[27].

1. `tls12-dsb.pcapng` 에서 `tls.handshake.type == 11` 인 패킷을 찾고, 인증서 DER 의 첫 4바이트(`30 82 …`)로 인증서 길이를 계산해 Wireshark 가 보여 주는 길이와 맞는지 확인하십시오.
2. 같은 파일을 Zeek(`zeek -C -r`)로 돌려 `x509.log` 의 `fingerprint` 와 openssl 로 계산한 SHA-256 지문이 같은지 확인하십시오. `ssl.log` 의 `cert_chain_fps` 첫 값과도 비교하십시오.
3. `browsers-x509.pcapng` 의 기대 출력에서 stream 0 의 `JA4X.1`(`a373a9f83c6b_2bab15409345_0f2217ba412e`)과 `JA4X.2`(`7d5dbb3783b4_a373a9f83c6b_c34b04c10969`)를 비교하십시오. 첫 인증서의 발급자 부분과 둘째 인증서의 주체 부분이 같은 것으로 체인이 어떻게 이어지는지 설명하십시오[26].
4. 같은 서버에 두 번 이상 접속한 캡처를 Zeek 로 돌리고, `ssl.log` 줄 수와 `x509.log` 줄 수를 비교하십시오. `X509::relog_known_certificates_after=0secs` 를 주고 다시 돌리면 무엇이 달라집니까?
5. Suricata 로 같은 캡처를 돌려 EVE 의 `tls.fingerprint`(SHA-1)와 Zeek 의 `fingerprint`(SHA-256)가 같은 인증서를 가리키는지, 인증서 DER 을 꺼내 두 해시를 모두 계산해 확인하십시오.

## 참고 문헌

1. D. Cooper 외, "Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile", RFC 5280, 2008. https://www.rfc-editor.org/rfc/rfc5280.txt
2. E. Rescorla, "The Transport Layer Security (TLS) Protocol Version 1.3", RFC 8446, 2018. https://www.rfc-editor.org/rfc/rfc8446.txt
3. B. Laurie, A. Langley, E. Kasper, "Certificate Transparency", RFC 6962, 2013. https://www.rfc-editor.org/rfc/rfc6962.txt
4. Zeek Project, Zeek 문서 "x509.log". https://github.com/zeek/zeek-docs/blob/master/logs/x509.rst
5. Zeek Project, Zeek 문서 "ssl.log". https://github.com/zeek/zeek-docs/blob/master/logs/ssl.rst
6. Zeek Project, 스크립트 문서 base/files/x509/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/files/x509/main.zeek.rst
7. Zeek Project, 스크립트 문서 base/protocols/ssl/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/main.zeek.rst
8. Zeek Project, 스크립트 문서 base/protocols/ssl/files.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/files.zeek.rst
9. Zeek Project, NEWS(버전별 변경 사항). https://github.com/zeek/zeek/blob/master/NEWS
10. Zeek Project, 스크립트 문서 base/files/x509/log-ocsp.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/files/x509/log-ocsp.zeek.rst
11. OISF, Suricata 사용자 안내서 "Eve JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
12. OISF, Suricata 사용자 안내서 "Eve JSON Output". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
13. OISF, Suricata 사용자 안내서 "SSL/TLS Keywords". https://github.com/OISF/suricata/blob/main/doc/userguide/rules/tls-keywords.rst
14. OISF, Suricata 사용자 안내서 "Custom tls logging". https://github.com/OISF/suricata/blob/main/doc/userguide/output/custom-tls-logging.rst
15. OISF, Suricata 사용자 안내서 "Upgrading". https://github.com/OISF/suricata/blob/main/doc/userguide/upgrade.rst
16. OISF, Suricata EVE JSON 스키마 etc/schema.json. https://github.com/OISF/suricata/blob/main/etc/schema.json
17. Wireshark Foundation, 표시 필터 참조 "Transport Layer Security (tls)". https://www.wireshark.org/docs/dfref/t/tls.html
18. Wireshark Foundation, 표시 필터 참조 "X.509 Authentication Framework (x509af)"·"X.509 Certificate Extensions (x509ce)". https://www.wireshark.org/docs/dfref/x/x509af.html , https://www.wireshark.org/docs/dfref/x/x509ce.html
19. OpenSSL Project, openssl-x509 매뉴얼. https://docs.openssl.org/master/man1/openssl-x509/
20. SigmaHQ, "Default Cobalt Strike Certificate" 규칙(zeek_default_cobalt_strike_certificate.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_default_cobalt_strike_certificate.yml
21. abuse.ch, SSL Blacklist(SSLBL). https://sslbl.abuse.ch/ , https://sslbl.abuse.ch/blacklist/
22. Blake Anderson, Subharthi Paul, David McGrew, "Deciphering malware's use of TLS (without decryption)", Journal of Computer Virology and Hacking Techniques, 2018. doi:10.1007/s11416-017-0306-6
23. Zakir Durumeric, James Kasten, Michael Bailey, J. Alex Halderman, "Analysis of the HTTPS certificate ecosystem", Proceedings of the 2013 Internet Measurement Conference (IMC '13), 2013. doi:10.1145/2504730.2504755
24. FoxIO, "JA4+ Network Fingerprinting". https://blog.foxio.io/ja4%2B-network-fingerprinting
25. Wireshark Foundation, tshark 매뉴얼(doc/man_pages/tshark.adoc). https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
26. FoxIO, JA4 저장소 Python 구현 시험 데이터와 시험 캡처. https://github.com/FoxIO-LLC/ja4/tree/main/python/test/testdata , https://github.com/FoxIO-LLC/ja4/tree/main/pcap
27. Wireshark Wiki, "TLS". https://wiki.wireshark.org/TLS
28. Zeek Project, 스크립트 문서 base/protocols/ssl/mozilla-ca-list.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/mozilla-ca-list.zeek.rst
