---
title: "파일 기록"
parent: "Zeek 로그"
grand_parent: "아티팩트 · Zeek"
nav_order: 190
---

# 파일 기록 (files.log)

Zeek 는 HTTP·SMTP·FTP 같은 연결에 실려 가는 파일을 따로 떼어 분석하고, 파일 하나마다 files.log 에 한 줄을 남깁니다. 한 줄에는 파일 ID(fuid), 그 파일을 나른 연결(uid), 보낸 방향, 내용으로 판별한 MIME 형식, 본 바이트 수와 놓친 바이트 수가 들어가고, 설정에 따라 해시와 추출 파일 이름이 붙습니다. 이 페이지는 files.log 의 필드를 읽는 법과 이 기록으로 주장할 수 있는 범위를 다룹니다. 로그 형식(TSV·JSON)과 공통 읽기 도구는 [Zeek 로그](index.md) 에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

Zeek 의 파일 분석 프레임워크 (File Analysis Framework) 는 프로토콜 분석기가 넘겨준 파일 내용을 연결과 따로 분석합니다. 기본으로 파일을 넘겨주는 프로토콜은 FTP, HTTP, IRC, Kerberos, MIME, RDP, SMTP, SSL/TLS/DTLS 이고, 패키지로 더 붙일 수 있습니다[3]. HTTP 라면 헤더를 뺀 본문이, SMTP 라면 MIME 첨부 하나하나가 파일이 됩니다[2][4]. 그래서 응답 본문이 39바이트뿐인 평범한 웹 요청도 files.log 에 한 줄을 남깁니다[1].

files.log 에 줄이 있다고 해서 파일 내용을 디스크에 저장한 것은 아닙니다. 파일을 꺼내 쓰려면 추출 분석기를 따로 붙이도록 설정해야 합니다[2]. 해시도 마찬가지로, 해시 분석기를 붙였을 때만 `md5`·`sha1`·`sha256` 필드가 채워집니다[5].

## 위치와 버전별 차이

files.log 는 다른 Zeek 로그와 같은 디렉터리에 `files` 라는 이름으로 생깁니다[4]. 저장 위치와 교대(rotation) 방식은 [Zeek 로그](index.md) 를 봅니다.

어떤 필드가 채워지는지는 불러온 스크립트에 따라 달라집니다. zeekctl 이 기본으로 싣는 local.zeek 에는 `@load frameworks/files/hash-all-files` 가 들어 있어 모든 파일의 해시를 구하지만[16][7], local.zeek 없이 `zeek -r` 로 pcap 만 돌리면 해시 필드가 `-` 로 남습니다[1]. 추출은 local.zeek 에도 켜져 있지 않고, `policy/frameworks/files/extract-all-files.zeek` 를 출발점으로 삼아 따로 설정합니다[3]. Security Onion 은 기본으로 파일을 추출해 Strelka 로 분석합니다[14].

| Zeek 버전 | 바뀐 점 |
|---|---|
| 4.1.0 | X.509 인증서를 기본으로 files.log 에 쓰지 않음. `X509::log_x509_in_files_log` 로 예전처럼 되돌릴 수 있음[8] |
| 5.1.0 | `tx_hosts`·`rx_hosts`·`conn_uids` 필드가 빠지고 `uid`·`id` 로 바뀜. 한 파일이 여러 연결에 걸치면 연결마다 한 줄씩 씀(fuid 는 같고 uid 가 다름)[8][4] |
| 8.1.0 | `hash-all-files` 가 MD5·SHA1 에 더해 SHA256 도 구함[8] |
| 8.2.0 | SMTP 분석기가 RFC 822 메시지 분석 중 만난 첫 틈을 파일 객체로 넘겨, 분석이 틈 때문에 멈췄는지 `missing_bytes` 로 확인할 수 있음[8] |

5.1.0 이전 로그와 이후 로그가 섞여 있으면 같은 질문에 쓰는 필드 이름이 다릅니다. 5.1.0 이전에는 한 파일에 `tx_hosts`·`rx_hosts`·`conn_uids` 값을 여러 개 붙여 한 줄로 썼고[4], 이후 로그에서 파일을 보낸 호스트는 `id` 와 `is_orig` 를 함께 봐야 알 수 있습니다[4].

## 구조

### 필드

기본 필드는 `Files::Info` 레코드가 정하고, 해시와 추출 필드는 해당 스크립트가 레코드에 덧붙입니다[4][5][6].

| 필드 | 뜻 |
|---|---|
| `ts` | 파일을 처음 본 시각 |
| `fuid` | 파일 ID |
| `uid`·`id` | 파일을 나른 연결의 uid 와 주소·포트 네 개(`id.orig_h`·`id.orig_p`·`id.resp_h`·`id.resp_p`). 연결 없이 읽은 파일이면 없음 |
| `source` | 파일이 온 곳. `HTTP`·`SMTP` 같은 프로토콜 이름이나 로컬 파일 경로 |
| `depth` | 출처 안에서의 깊이. SMTP 는 MIME 첨부의 깊이, HTTP 는 TCP 연결 안에서 몇 번째 요청인지 |
| `analyzers` | 이 파일에 붙은 파일 분석기 집합. 예 `EXTRACT`, `PE`, `MD5` |
| `mime_type` | 파일 앞부분에 가장 강하게 맞은 내용 시그니처의 MIME 형식 |
| `filename` | 출처가 알려 준 파일 이름. 대개 `Content-Disposition` 헤더에서 옴 |
| `duration` | 분석한 기간(마지막으로 본 시각 − `ts`) |
| `local_orig` | 파일을 보낸 호스트가 `Site::local_nets` 안에 있는지. local_nets 를 설정하지 않으면 없음 |
| `is_orig` | 연결을 연 측(originator)이 보냈으면 `T`, 응답한 측(responder)이 보냈으면 `F` |
| `seen_bytes` | 파일 분석 엔진에 들어온 바이트 수 |
| `total_bytes` | 전체 파일 크기. 프로토콜이 알려 줄 때만 있음 |
| `missing_bytes` | 패킷 손실 같은 이유로 통째로 놓친 바이트 수 |
| `overflow_bytes` | 스트림 분석기에 넘기지 못한 바이트 수(겹친 바이트, 재조립하지 못한 바이트) |
| `timedout` | 분석이 한 번이라도 시간 초과됐는지 |
| `parent_fuid` | 압축 파일 같은 컨테이너에서 꺼낸 파일이면 부모 파일의 fuid |
| `md5`·`sha1`·`sha256` | 해시 분석기를 붙였을 때만 |
| `extracted` | 추출한 파일의 로컬 이름 |
| `extracted_cutoff` | 추출 크기 한도에 걸려 파일이 잘렸으면 `T` |
| `extracted_size` | 디스크에 쓴 바이트 수 |

`seen_bytes` 와 `missing_bytes` 는 이 연결 하나의 값이 아니라, 이 Zeek 인스턴스가 본 모든 연결에서 이 파일에 대해 센 합계입니다[4]. 파일 크기로 전송량을 말할 때는 이 점을 염두에 두고 [연결 기록](conn-log.md) 의 바이트 수와 함께 봅니다.

추출 설정의 기본값은 다음과 같습니다[6][3].

| 설정 | 기본값 | 뜻 |
|---|---|---|
| `FileExtract::prefix` | `./extract_files/` | 추출 파일을 쓰는 디렉터리 |
| `FileExtract::default_limit` | `104857600` (100MB) | 추출 파일의 최대 크기. 0 이면 제한 없음 |
| `FileExtract::default_limit_includes_missing` | `T` | 놓친 바이트도 한도에 포함. `F` 면 놓친 부분이 성긴 파일(sparse file)로 생겨 겉보기 크기가 한도를 넘을 수 있음 |

### 한 줄의 모양

다음은 HTTP 로 실행 파일을 받은 흐름의 JSON 한 줄입니다(만든 예시, 보기 좋게 줄을 나눔)[2].

```json
{"ts":1772413530.604,"fuid":"FqZx3a1bCdEf5gHi2","uid":"CkT2m84pQrStUvWx9",
 "id.orig_h":"192.168.0.10","id.orig_p":49812,"id.resp_h":"203.0.113.20","id.resp_p":80,
 "source":"HTTP","depth":0,"analyzers":["EXTRACT","PE"],
 "mime_type":"application/x-dosexec","duration":0.0155,"is_orig":false,
 "seen_bytes":179272,"total_bytes":179272,"missing_bytes":0,"overflow_bytes":0,
 "timedout":false,"extracted":"HTTP-FqZx3a1bCdEf5gHi2.exe","extracted_cutoff":false}
```

`is_orig` 가 `false` 라서 응답한 웹 서버(203.0.113.20)가 파일을 보냈고 192.168.0.10 이 받았습니다[2]. 추출 파일 이름은 `출처-fuid.확장자` 형식입니다[2]. 해시 필드가 없으니 해시 분석기를 붙이지 않은 설정입니다. JSON 은 값 없는 필드를 아예 빼고 쓰고, TSV 는 `-` 로 씁니다. 빈 `analyzers` 는 JSON 에서 `[]`, TSV 에서 `(empty)` 입니다[1].

## 증거로서 의미

**증명하는 것:** 센서가 본 트래픽에서, 이 연결(uid)을 통해 이 방향(`is_orig`)으로 이 MIME 형식과 이 크기의 파일 내용이 흘렀다는 것입니다. `missing_bytes` 가 0 이고 `seen_bytes` 가 `total_bytes` 와 같으면 센서가 파일 전체를 받아 분석했다는 뜻입니다. 해시가 있으면 호스트에서 찾은 파일이나 위협 정보의 해시와 대조해 같은 내용인지 확인할 수 있습니다.

**증명하지 못하는 것:** 받은 호스트가 파일을 디스크에 저장했는지, 실행했는지는 알 수 없어서 호스트 쪽 기록으로 확인합니다. `missing_bytes` 가 0 보다 크거나 `extracted_cutoff` 가 `T` 면 추출 파일과 해시가 원래 파일 전체의 것이 아닙니다. HTTPS 처럼 암호화된 채널로 오간 파일은 Zeek 가 내용을 보지 못해 files.log 에 남지 않습니다. 또 어느 사용자나 프로세스가 받았는지는 files.log 에 없습니다.

보고서에는 "이 시각에 203.0.113.20 이 192.168.0.10 에 application/x-dosexec 형식으로 판별되는 179,272바이트 파일을 HTTP 로 보낸 기록이 있다"(만든 예시) 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`ts` 는 Zeek 가 파일을 처음 만난 때의 네트워크 시각이고, 줄을 쓰는 것은 파일 상태를 지우는 `file_state_remove` 때입니다[4]. HTTP 응답이라면 `ts` 는 요청 시각이 아니라 응답 본문이 담긴 패킷의 시각이라서, 요청 시각인 http.log 의 `ts` 보다 늦습니다[1]. `duration` 은 마지막으로 파일 데이터를 본 시각에서 `ts` 를 뺀 값입니다[4].

기록 시점이 파일이 끝날 때라서 files.log 안의 줄 순서는 `ts` 순서와 다를 수 있습니다. 시간순으로 볼 때는 `ts` 로 정렬합니다. 시각 형식(에포크 초, UTC)과 `#open` 줄의 의미는 [Zeek 로그](index.md) 와 [네트워크 기록의 시각](../../../01-foundations/records/timestamps.md) 을 봅니다.

추출 파일의 파일시스템 시각은 센서가 그 파일을 디스크에 쓴 시각이고, 원래 파일이 만들어지거나 수정된 시각이 아닙니다.

## 함정과 한계

`is_orig` 는 방향을 판단하는 필드입니다. HTTP 다운로드는 서버가 응답으로 보내므로 `F`, 업로드(POST 본문)는 클라이언트가 보내므로 `T` 입니다[2][4]. 주소만 보고 "외부 IP 가 있으니 유출" 이라고 판단하지 않습니다.

`mime_type` 은 Zeek 자체 시그니처(`scripts/base/frameworks/files/magic/`)로 내용을 보고 정한 값이고 libmagic 을 쓰지 않습니다[3]. 그래서 파일 확장자나 HTTP `Content-Type` 헤더와 다를 수 있고, 둘이 다르면 그 자체가 살펴볼 거리입니다. 헤더에 적힌 형식은 [HTTP 기록](http-log.md) 에서 확인합니다.

`filename` 은 출처가 이름을 알려 줄 때만 채워집니다[4]. URI 가 `wfetch.exe` 처럼 파일 이름으로 끝나는 다운로드에도 `filename` 이 비어 있을 수 있어서, 요청한 이름은 http.log 의 `uri` 에서 찾습니다[2].

해시 필드가 비었으면 해시 분석기를 싣지 않은 설정 문제이지, 파일이 없었거나 해시를 구할 수 없었다는 뜻이 아닙니다. 8.1.0 이전 Zeek 는 `hash-all-files` 를 실어도 `sha256` 이 비어 있습니다[8]. 추출 파일이 없을 때도 먼저 추출 설정과 크기 한도를 확인합니다.

같은 pcap 을 다시 처리하면 연결의 uid 는 달라질 수 있지만, 같은 HTTP 응답의 fuid 는 그대로일 수 있습니다[1]. 파일 ID 를 만들 때 설치마다 정하는 `digest_salt` 값이 들어가므로[12][7], 센서가 다르면 같은 파일이라도 fuid 가 다를 수 있습니다. 센서나 실행이 다른 로그끼리 같은 파일인지 비교할 때는 해시를 씁니다.

## 직접 분석해 보기

TSV 로그는 `zeek-cut` 으로 필요한 필드만 골라 봅니다[1]. 방향과 손실 여부를 한 번에 보려면 다음처럼 뽑습니다.

```sh
zeek-cut -d ts fuid uid id.orig_h id.resp_h is_orig mime_type seen_bytes total_bytes missing_bytes extracted < files.log
```

JSON 로그는 jq 로 봅니다. 점이 들어간 키는 따옴표로 감쌉니다[1]. 다음은 연결을 연 쪽이 받았고(`is_orig` 가 false) 실행 파일로 판별된 줄만 고르는 예입니다.

```sh
jq -c 'select(.mime_type=="application/x-dosexec" and .is_orig==false) | [.ts, .fuid, .uid, ."id.resp_h", ."id.orig_h", .seen_bytes, .missing_bytes, .extracted]' files.log
```

추출 파일이 있으면 크기가 `seen_bytes`(또는 `extracted_size`)와 같은지 `ls -l` 로 보고, `file` 명령으로 형식을, `md5sum` 같은 도구로 해시를 확인합니다[2]. `extracted_cutoff` 가 `T` 면 잘린 파일이고, 크기가 다르면 손실이나 잘림을 의심합니다. 추출 파일을 다룰 때 주의할 점과 pcap 에서 직접 꺼내는 방법은 [세션 복원과 파일 꺼내기](../../../03-techniques/analysis/file-extraction.md) 를 봅니다.

## 교차 검증

files.log 는 연결·응용 로그와 두 가지 열쇠로 이어집니다. 첫째는 `uid` 로, 파일을 나른 연결을 [연결 기록](conn-log.md) 에서 찾아 전체 전송량과 연결 상태를 확인합니다. 둘째는 `fuid` 로, 응용 로그 쪽에 파일 ID 목록이 있습니다[2].

| 로그 | 파일 ID 필드 | 함께 알 수 있는 것 |
|---|---|---|
| [http.log](http-log.md) | `orig_fuids`·`resp_fuids` (이름은 `orig_filenames`·`resp_filenames`, 형식은 `orig_mime_types`·`resp_mime_types`) | 요청한 Host·URI·User-Agent·상태 코드[9][1] |
| smtp.log | `fuids` | 보낸 사람·받는 사람·제목 같은 메일 정보[10][15] |
| [notice.log](notice-weird-log.md) | `fuid`, `file_mime_type`, `file_desc` | 파일 때문에 올라간 알림[11] |
| [ssl.log·x509.log](ssl-x509-log.md) | 인증서 지문 | 4.1.0 이후 인증서는 files.log 대신 여기에 남음[8] |

http.log 의 `resp_fuids` 에서 fuid 를 얻어 files.log 를 찾고, 거기서 추출 파일 이름으로 넘어가는 순서로 따라가면 어떤 URL 에서 받은 파일인지까지 이을 수 있습니다[2]. 탐지 규칙에서도 이 필드를 씁니다. WebDAV 로 받은 실행 파일을 찾는 SigmaHQ 규칙은 `resp_mime_types|contains: 'dosexec'` 조건으로 실행 파일 응답을 고릅니다[13]. 규칙 쓰는 법은 [탐지 규칙 활용](../../../03-techniques/analysis/detection-rules.md) 을 봅니다.

같은 트래픽을 Suricata 도 봤다면 [Suricata EVE 로그](../../suricata/eve-json/index.md) 의 파일 기록과 해시로 대조합니다. 받은 파일이 호스트에서 저장·실행됐는지는 호스트 쪽 기록으로 확인하고, 조사 흐름은 [피싱 링크를 눌렀나](../../../04-scenarios/user-activity/phishing-click.md) 와 [자료를 밖으로 보냈나](../../../04-scenarios/exfiltration/data-exfiltration.md) 를 봅니다.

## 실습

HTTP 로 파일을 받는 흐름이 든 공개 실습 캡처(Wireshark 예제 캡처 등)를 `zeek -r` 로 한 번, `frameworks/files/hash-all-files` 스크립트를 함께 실어 한 번 돌려 두 결과를 비교해 봅니다.

1. 두 실행에서 `md5`·`sha1`·`sha256` 필드가 어떻게 다른가?
2. http.log 의 `resp_fuids` 에 있는 fuid 를 files.log 에서 찾고, 두 줄의 `ts` 가 얼마나 차이 나는가? 차이는 무엇을 뜻하는가?
3. `is_orig` 가 `T` 인 줄이 있다면 그 연결의 http.log 에서 메서드는 무엇인가?
4. 두 실행 사이에 uid 와 fuid 가 각각 바뀌었는가?

## 참고 문헌

1. Zeek Project, "Zeek Log Formats and Inspection", https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
2. Zeek Project, "files.log", https://github.com/zeek/zeek-docs/blob/master/logs/files.rst
3. Zeek Project, "File Analysis", https://github.com/zeek/zeek-docs/blob/master/frameworks/file-analysis.rst
4. Zeek Project, scripts/base/frameworks/files/main.zeek, https://github.com/zeek/zeek/blob/master/scripts/base/frameworks/files/main.zeek
5. Zeek Project, base/files/hash/main.zeek, https://github.com/zeek/zeek-docs/blob/master/scripts/base/files/hash/main.zeek.rst
6. Zeek Project, base/files/extract/main.zeek, https://github.com/zeek/zeek-docs/blob/master/scripts/base/files/extract/main.zeek.rst
7. Zeek Project, scripts/site/local.zeek, https://github.com/zeek/zeek/blob/master/scripts/site/local.zeek
8. Zeek Project, NEWS (4.1.0, 5.1.0, 8.1.0, 8.2.0 절), https://github.com/zeek/zeek/blob/master/NEWS
9. Zeek Project, base/protocols/http/entities.zeek, https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/http/entities.zeek.rst
10. Zeek Project, base/protocols/smtp/files.zeek, https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/smtp/files.zeek.rst
11. Zeek Project, scripts/base/frameworks/notice/main.zeek, https://github.com/zeek/zeek/blob/master/scripts/base/frameworks/notice/main.zeek
12. Zeek Project, scripts/base/init-bare.zeek (`digest_salt`), https://github.com/zeek/zeek/blob/master/scripts/base/init-bare.zeek
13. SigmaHQ, "Executable from Webdav", https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_executable_download_from_webdav.yml
14. Security Onion Solutions, "Zeek", https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/zeek.rst
15. Zeek Project, base/protocols/smtp/main.zeek, https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/smtp/main.zeek.rst
16. Zeek Project, "Quick Start Guide", https://docs.zeek.org/en/master/quickstart.html
