---
title: "파일 추출"
parent: "Suricata EVE 로그"
grand_parent: "아티팩트 · Suricata"
nav_order: 240
---

# 파일 추출 (filestore)

Suricata 는 평문 HTTP·SMTP·FTP·NFS·SMB·HTTP/2 로 오간 파일을 알아보고, 파일마다 EVE 로그에 `fileinfo` 기록을 한 줄 남깁니다[1]. 규칙이 고른 파일은 내용까지 디스크에 저장하는데, 내용의 SHA256 을 파일 이름으로 써서 같은 파일은 하나만 남습니다[1]. 누가 언제 어느 방향으로 주고받았는지는 저장된 파일이 아니라 `fileinfo` 기록과 같은 흐름의 다른 기록으로 확인합니다.

## 무엇을 기록하나 · 왜 생기나

파일 추출은 프로토콜 파서 위에서 동작하고, 파서는 TCP 스트림 재조립과 UDP 흐름 추적 위에서 동작합니다[1]. 그래서 스트림 엔진·재조립·파서 설정이 모두 추출 결과를 바꿉니다. HTTP 는 파서가 청크 전송(chunked transfer)을 합치고 압축을 푼 다음의 내용을 파일로 다룹니다[1].

출력은 두 가지이고 켜는 조건이 서로 다릅니다[1].

| 출력 | 설정 위치 | 남는 것 | 켜는 조건 |
|---|---|---|---|
| `fileinfo` 기록 | `eve-log` 의 `types` 아래 `files` | 파일 이름·크기·상태·해시 같은 메타데이터 한 줄. 내용은 없습니다 | 기본 설정 파일에 켜져 있습니다[10] |
| 파일 저장 (file-store) | `outputs` 아래 `file-store` | 파일 내용 | `enabled: yes`(기본 `no`)에 더해 규칙의 `filestore` 키워드나 `force-filestore: yes` 가 있어야 합니다[1][2] |

`force-filestore` 를 켜지 않았다면 규칙이 없을 때 file-store 를 켜도 아무 파일도 저장하지 않습니다[1][7]. 규칙 키워드는 `filestore:방향,범위;` 형식입니다[5]. 방향은 `request`·`to_server`, `response`·`to_client`, `both` 가운데 하나이고, 범위는 `file`(조건에 맞은 파일만), `tx`(그 HTTP 트랜잭션의 모든 파일), `ssn`·`flow`(그 세션의 모든 파일) 가운데 하나입니다. 둘 다 생략하면 규칙의 방향을 따르고 파일 하나 단위로 저장합니다[5]. 보통 확장자(`fileext`), 파일 형식(`filemagic`), 해시 목록(`filemd5`·`filesha1`·`filesha256`) 조건과 함께 써서 저장할 파일을 고릅니다[1][5]. 규칙 자체를 읽는 법은 [탐지 규칙 활용](../../../03-techniques/analysis/detection-rules.md)에 있습니다.

## 위치와 버전별 차이

저장 폴더는 `file-store` 의 `dir` 값이고 기본은 `filestore` 입니다. 상대 경로면 기본 로그 폴더(`default-log-dir`, 기본값 `/var/log/suricata`) 아래에 만들어집니다[1][2]. 실행할 때 `-l 폴더` 를 줬다면 yaml 의 `default-log-dir` 대신 그 폴더가 기준이 됩니다[13]. 센서를 조사할 때는 suricata.yaml 에서 `file-store` 의 `enabled`·`dir`·`write-fileinfo`·`force-filestore`·`stream-depth`·`force-hash` 값과, 불러온 규칙 파일 가운데 `filestore` 가 들어간 규칙을 먼저 확인합니다. 이 값들에 따라 무엇이 저장됐고 무엇이 빠졌는지가 정해집니다.

| 버전 | 달라지는 점 |
|---|---|
| file-store v1 (6.0 에서 없어짐) | 설정 이름 `log-dir`·`waldo`·`write-meta`·`include-pid`, 파일 옆에 `.meta` 파일을 씁니다[3] |
| 6.0 부터 | v1 이 없어졌습니다. `version: 2` 가 없거나 2보다 작으면 `File-store v1 has been removed. Please update to file-store v2.` 경고를 내고 파일 저장을 켜지 않습니다[1][7] |
| v2 설정 | `version: 2`, `dir`, `write-fileinfo`, `force-filestore`, `stream-depth`, `max-open-files`, `force-hash`[2][3] |

Security Onion 2.4 에서 메타데이터 엔진을 Suricata 로 바꾸면 기본으로 켜지는 SO_EXTRACTIONS 규칙 묶음이 꺼낼 파일 종류를 정하고, Strelka 가 그 파일을 분석해 `/nsm/strelka/processed/` 에 둡니다[11][12]. 같은 해시의 파일은 48시간 안에 다시 분석하지 않습니다[12].

## 구조

### 디스크 배치 (file-store v2)

| 경로 | 내용 |
|---|---|
| `filestore/00` ~ `filestore/ff` | 시작할 때 256개를 모두 만듭니다[7]. 파일은 SHA256 16진 문자열의 앞 두 글자와 같은 이름의 폴더에 들어갑니다[1] |
| `filestore/f9/f9bc6d…` | 파일 내용. 이름은 내용의 SHA256 16진 문자열(64자)입니다[1][7] |
| `filestore/f9/f9bc6d….SECONDS.ID.json` | `write-fileinfo: yes` 일 때만 생깁니다. 형식은 `<SHA256>.<SECONDS>.<ID>.json` 이고 내용은 EVE 의 `fileinfo` 기록과 같습니다[1] |
| `filestore/tmp/file.ID` | 아직 쓰는 중인 파일입니다[7] |

파일 데이터가 들어오는 동안 Suricata 는 `tmp/file.번호` 에 이어 쓰고, 파일이 닫히면 SHA256 이름으로 옮깁니다(rename)[7]. 같은 이름의 파일이 이미 있으면 새로 쓰지 않습니다. 이때 기존 파일의 접근·수정 시각을 방금 쓴 임시 파일의 시각으로 바꾸고 임시 파일은 지웁니다[1][7]. 그래서 같은 내용이 몇 번을 오가도 디스크에는 파일 하나만 남습니다.

`write-fileinfo` 파일 이름의 SECONDS 는 파일을 닫게 한 패킷 시각의 초 값(유닉스 시각)이고, ID 는 한 번 실행하는 동안만 고유한 번호입니다[1][7]. 두 값은 이름이 겹치지 않게 붙인 것이라 분석 근거로 삼기에 알맞지 않습니다[1]. 같은 내용이 EVE 의 `fileinfo` 기록에 이미 남아서 이 설정은 기본으로 꺼져 있습니다[2][3].

`max-open-files` 는 동시에 열어 둘 파일 수이고, 기본 0 이면 쓸 때마다 파일을 닫습니다[2]. 값을 정했는데 한도를 넘으면 `file_store.open_files_max_hit` 카운터가 오르고, 그 파일은 열어 두지 않고 쓸 때마다 열었다 닫습니다[7]. 파일을 열거나 쓰거나 옮기다 실패하면 `file_store.fs_errors` 카운터가 오르고, 로그 경고는 종류마다 한 번만 남습니다[7]. 옮기기(rename)가 실패하면 임시 파일을 지우므로 그 파일은 디스크에 남지 않습니다[7]. 카운터는 EVE 의 `stats` 기록에서 봅니다([Suricata EVE 로그](index.md)).

### fileinfo 기록

공통 머리 필드(`timestamp`·`flow_id`·5-tuple 등)는 [Suricata EVE 로그](index.md)에서 다룹니다. 아래는 HTTP 로 파일을 내려받은 `fileinfo` 기록입니다(만든 예시).

```json
{
  "timestamp": "2026-03-02T01:15:42.518230+0000",
  "flow_id": 1532087766123456,
  "event_type": "fileinfo",
  "src_ip": "203.0.113.10",
  "src_port": 80,
  "dest_ip": "192.168.1.20",
  "dest_port": 51234,
  "proto": "TCP",
  "http": {
    "hostname": "downloads.example.com",
    "url": "/files/report.pdf",
    "http_user_agent": "Mozilla/5.0",
    "http_content_type": "application/pdf",
    "http_method": "GET",
    "protocol": "HTTP/1.1",
    "status": 200,
    "length": 48213
  },
  "app_proto": "http",
  "fileinfo": {
    "filename": "/files/report.pdf",
    "sid": [2],
    "magic": "PDF document, version 1.7",
    "gaps": false,
    "state": "CLOSED",
    "md5": "5d41a2c3b6e87f0914c2d9e0a7b3f611",
    "sha256": "9c1f7e0b4a2d58c6e3f1a0b9d7c4e2f58a6b3c1d0e9f8a7b6c5d4e3f2a1b0c9d",
    "stored": true,
    "file_id": 12,
    "size": 48213,
    "tx_id": 0
  }
}
```

| 필드 | 뜻 |
|---|---|
| `filename` | 트래픽에 보인 이름입니다[6]. HTTP 는 URL 경로라서 `"/"` 처럼 파일 이름으로 보이지 않는 값일 수도 있습니다[6] |
| `sid` | 이 파일을 저장하게 한 `filestore` 규칙 번호의 배열입니다[6][9] |
| `magic` | libmagic 으로 판별한 파일 형식입니다. libmagic 을 넣어 빌드했을 때만 나오고, 모든 파일에 남기려면 `files` 설정의 `force-magic` 을 켭니다[6][9][10] |
| `gaps` | 파일 중간에 빠진 부분이 있으면 `true` 입니다[6] |
| `state` | 기록을 쓸 때의 파일 상태. `CLOSED`·`TRUNCATED`·`ERROR`·`UNKNOWN`[6][9] |
| `md5`·`sha1` | `state` 가 `CLOSED` 일 때만 나옵니다[6][9] |
| `sha256` | 계산했으면 나옵니다. file-store 를 켜면 파일 이름에 써야 해서 SHA256 계산이 강제로 켜집니다[2][7][9] |
| `stored` | 디스크에 저장했으면 `true` 이고, 이때 `file_id` 가 함께 나옵니다[6][9] |
| `storing` | 저장 대상이지만 아직 저장이 끝나지 않았으면 `true` 입니다[6][9] |
| `size` | Suricata 가 추적한 파일 크기(바이트)입니다[6][9] |
| `start`·`end` | 부분 전송일 때 잡힌 첫 바이트와 마지막 바이트의 위치입니다. HTTP Content-Range 헤더의 값과 같습니다[6] |
| `tx_id` | 파일이 실린 트랜잭션 번호입니다[6] |

해시는 `--disable-hashing` 옵션을 쓰지 않았고 파일에 빠진 부분이 없을 때만 나옵니다[6]. 이 옵션을 쓰면 파일 저장(filestore)도 함께 꺼집니다[13]. 어떤 해시를 남길지는 `files` 설정의 `force-hash`(md5·sha1·sha256)로 정합니다[1][10].

`fileinfo` 줄에는 그 파일이 실린 프로토콜 기록이 함께 붙습니다. HTTP 는 `http`, SMTP 는 `smtp`·`email`, NFS 는 `rpc`·`nfs`, SMB 는 `smb` 객체이고, `app_proto` 도 같이 씁니다[8]. `http` 객체 필드의 뜻은 [프로토콜 기록](protocol-events.md)에 있습니다.

주소 방향은 파일이 흘러간 방향을 따릅니다. 파일이 서버에서 클라이언트로 갔으면(내려받기) `src_ip` 가 서버이고, 클라이언트에서 서버로 갔으면(올리기·POST 본문) `src_ip` 가 클라이언트입니다[8][9]. POST 요청 본문으로 올린 파일의 `fileinfo` 기록도 `src_ip` 가 클라이언트입니다[6]. 같은 트랜잭션의 `http` 기록은 늘 클라이언트를 `src_ip` 로 쓰므로, 두 기록의 src·dest 가 뒤바뀌어 보여도 이상한 것이 아닙니다. HTTP 에서 X-Forwarded-For 설정이 `overwrite` 모드면 IP 필드가 패킷의 주소가 아니라 헤더 값으로 바뀝니다[8].

## 증거로서 의미

### 증명하는 것

- 센서가 본 평문 전송에서 이 SHA256 의 내용이 이 5-tuple·트랜잭션으로 이 방향으로 오갔다는 것. `state` 가 `CLOSED` 이고 `gaps` 가 `false` 일 때 해시가 전송된 파일 전체를 가리킵니다.
- 저장된 파일이 있으면 그 내용 자체. 해시 목록 대조나 악성 코드 검사를 다시 할 수 있고, 이름과 내용 해시가 같은지로 저장 뒤 바뀌지 않았는지 확인할 수 있습니다.
- `sid` 가 있으면 어느 규칙 조건에 맞아 저장됐는지.

### 증명하지 못하는 것

- 받은 PC 의 디스크에 파일이 저장되거나 실행됐는지. 호스트 기록으로 확인합니다.
- 암호화된 채널(HTTPS 등) 안의 파일. Suricata 는 암호를 풀지 않으므로 이런 파일은 `fileinfo` 기록도 저장 파일도 없습니다[2].
- `TRUNCATED` 이거나 `gaps` 가 `true` 인 파일의 원래 해시. 저장된 파일은 잡힌 부분만 담습니다.
- 받은 쪽에서 쓴 파일 이름. HTTP 의 `filename` 은 URL 경로입니다[6].
- 저장된 파일이 없다는 사실만으로 전송이 없었다는 것. 저장은 규칙에 맞은 파일에만 일어납니다[1].

보고서에는 "파일을 내려받았다" 대신 "2026-03-02 01:15:42 UTC 에 203.0.113.10:80 에서 192.168.1.20 으로 SHA256 9c1f…0c9d 인 48,213바이트 파일이 HTTP 응답으로 전송된 기록(state CLOSED)이 있다(만든 예시)" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

| 시각 | 무엇을 기준으로 찍히나 |
|---|---|
| `fileinfo` 의 `timestamp` | 기록을 쓰게 한 패킷의 시각이고, 센서 로컬 시간대 오프셋이 붙습니다[9][16]. 파일 첫 바이트가 오간 시각이 아닙니다 |
| `write-fileinfo` 파일 이름의 SECONDS | 파일을 닫게 한 패킷 시각의 초 값입니다[1][7] |
| 저장 파일의 수정·접근 시각 | 센서 운영체제가 임시 파일을 마지막으로 쓴 시각입니다. 같은 파일이 다시 추출되면 그때 시각으로 덮입니다[1][7] |

같은 트랜잭션의 `fileinfo` 기록과 `http` 기록은 `timestamp` 가 같고, 흐름의 첫 패킷 시각(`flow.start`)보다 늦습니다. 예를 들어 `flow.start` 가 06:13:33.324862 인 흐름에서 두 기록의 `timestamp` 는 06:13:33.903924 입니다[6]. 전송이 언제 시작됐는지는 같은 `flow_id` 의 flow 기록 `start` 로 확인합니다. `timestamp` 형식과 오프셋 처리는 [Suricata EVE 로그](index.md)와 [네트워크 기록의 시각](../../../01-foundations/records/timestamps.md)에 있습니다.

저장 파일의 수정 시각은 패킷 시각과 관계가 없습니다. 실시간 센서면 센서 시스템 시계로 찍힌 마지막 추출 시각이고, pcap 을 다시 돌려 꺼낸 파일이면 다시 돌린 날의 시각입니다. 같은 파일이 처음 오간 때는 EVE 에서 그 `sha256` 의 `fileinfo` 기록 가운데 가장 이른 것을 찾아 확인합니다.

## 함정과 한계

**파일이 잘립니다.** 파일 추출 세션의 재조립 깊이는 `file-store.stream-depth` 가 정합니다. 0 이면 끝까지 재조립하고, 설정하지 않았거나 `no` 면 `stream.reassembly.depth`(기본 1MB)를 따릅니다[1][2]. `stream.reassembly.depth` 이하의 값을 적으면 경고만 내고 무시합니다[1][7]. 깊이에 닿으면 파일이 잘려 끝까지 저장되지 않을 수 있습니다[1]. HTTP 는 `libhtp` 의 `request-body-limit`·`response-body-limit` 도 파일 검사 범위를 제한하고, 0 이면 제한이 없습니다[1]. 이 값은 `default-config` 뿐 아니라 주소별 `server-config` 에도 따로 있을 수 있어 둘 다 봐야 합니다[2]. 파일을 끝까지 꺼내려면 재조립 깊이와 두 본문 한도를 0 으로 둡니다[4].

**체크섬 검사로 패킷이 버려집니다.** `stream.checksum_validation` 은 기본으로 켜져 있어서, 네트워크 카드가 체크섬 계산을 대신하는(checksum offloading) 환경에서 캡처한 패킷은 깨진 것처럼 보여 버려질 수 있습니다[1]. pcap 을 다시 돌릴 때는 `-k none` 으로 체크섬 검사를 끕니다[13].

**저장 파일의 해시가 전송 바이트의 해시와 다를 수 있습니다.** HTTP 는 청크를 합치고 압축을 푼 내용을 파일로 다루므로[1], pcap 에서 응답 본문 바이트를 그대로 떼어 해시하면 값이 다를 수 있습니다. 다른 도구로 꺼낸 파일과 비교할 때는 그 도구도 전송 인코딩을 풀었는지 확인합니다.

**부분 전송입니다.** `start`·`end` 가 있으면 HTTP Content-Range 로 파일 일부만 오간 것입니다[6]. SMB 도 READ·WRITE 명령마다 오프셋과 길이를 실어 보내므로 클라이언트가 실제로 읽거나 쓴 범위만 네트워크에 나타납니다[15]. 이런 파일은 네트워크에서 꺼낸 내용이 원본 파일 전체가 아닙니다.

**파일 하나에 전송이 여럿입니다.** 같은 내용은 디스크에 하나만 남으므로, 전송 횟수와 상대 주소는 `fileinfo` 기록을 `sha256` 으로 모아 봐야 알 수 있습니다[1].

**`tmp/` 에 조각이 남습니다.** 쓰는 도중에 센서가 멈췄거나 그 상태로 수집했다면 `tmp/file.번호` 에 끝나지 않은 파일이 남을 수 있습니다[7]. 이 파일은 이름에 해시가 없고 `fileinfo` 의 `file_id` 와 번호가 같아 보여도 같은 실행의 번호인지 따로 확인해야 합니다.

**설정 이름이 틀리면 조용히 무시됩니다.** 코드는 `force-filestore` 라는 이름만 읽습니다[7]. v1→v2 변환 문서의 예시에는 `file-filestore: no` 라는 이름이 들어 있는데[3], 이 이름을 그대로 옮긴 설정은 효과가 없습니다.

## 직접 분석해 보기

EVE 에서 디스크에 저장된 파일만 골라 시각·주소·이름·해시를 한 줄씩 봅니다.

```sh
jq -c 'select(.event_type=="fileinfo" and .fileinfo.stored==true)
  | [.timestamp, .src_ip, .dest_ip, .fileinfo.filename, .fileinfo.state, .fileinfo.sha256]' eve.json
```

같은 해시가 몇 번, 누구와 오갔는지 해시 순으로 모읍니다.

```sh
jq -r 'select(.event_type=="fileinfo" and .fileinfo.sha256 != null)
  | [.fileinfo.sha256, .timestamp, .src_ip, .dest_ip, .fileinfo.filename] | @tsv' eve.json | sort
```

저장 폴더의 파일 이름과 내용 해시가 같은지 확인합니다. 이름이 곧 SHA256 이므로 다르면 저장 뒤에 내용이 바뀐 것입니다.

```sh
find filestore -path filestore/tmp -prune -o -type f ! -name '*.json' -print |
while read -r f; do
  h=$(sha256sum "$f" | cut -d' ' -f1)
  [ "$h" = "$(basename "$f")" ] || echo "다름: $f"
done
```

헥스로 파일 앞부분을 보고 `magic` 필드, HTTP `http_content_type`, URL 확장자가 서로 맞는지 비교합니다. 확장자와 실제 형식이 다르면 파일을 다른 형식으로 꾸며 보냈을 가능성이 있습니다.

```sh
xxd -l 32 filestore/9c/9c1f7e0b4a2d58c6e3f1a0b9d7c4e2f58a6b3c1d0e9f8a7b6c5d4e3f2a1b0c9d
stat filestore/9c/9c1f7e0b4a2d58c6e3f1a0b9d7c4e2f58a6b3c1d0e9f8a7b6c5d4e3f2a1b0c9d
```

`stat` 의 수정 시각은 앞의 시각 해석 절에서 본 것처럼 마지막으로 추출한 시각이라 전송 시각으로 쓰지 않습니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 | 링크 |
|---|---|---|
| 같은 `flow_id` 의 `http` 기록 | 요청 URL·Host·상태 코드·응답 길이 | [프로토콜 기록](protocol-events.md) |
| 같은 `flow_id` 의 `flow` 기록 | 흐름 시작·끝 시각, 오간 바이트 수 | [프로토콜 기록](protocol-events.md) |
| `alert` 기록 | `filestore` 규칙의 경고와 `fileinfo` 의 `sid` 가 같은지 | [경고 기록](alert.md) |
| 원본 pcap | 다른 도구로 같은 파일을 다시 꺼내 해시 비교 | [세션 복원과 파일 꺼내기](../../../03-techniques/analysis/file-extraction.md) |
| Zeek 로그 | 같은 시각·주소의 파일 기록 | [Zeek 로그](../../zeek/zeek-logs/index.md) |
| 받은 PC 의 기록 | 브라우저 다운로드 기록, 파일 생성 흔적 | [크롬 계열 브라우저 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) |

파일이 밖으로 나갔는지 묻는 조사라면 `fileinfo` 의 방향(클라이언트→서버)과 흐름 바이트 수를 함께 봅니다([자료를 밖으로 보냈나](../../../04-scenarios/exfiltration/data-exfiltration.md)). 암호화된 전송은 [암호화된 트래픽 분석](../../../03-techniques/analysis/encrypted-traffic.md)에서 다룹니다.

## 실습

공개 실습 캡처 파일(Wireshark 예제 캡처 등) 가운데 HTTP 로 파일을 내려받는 캡처의 사본을 준비합니다. `pcap-file` 의 `delete-when-done` 설정이나 `--pcap-file-delete` 옵션이 켜져 있으면 처리한 pcap 을 지우므로 반드시 사본으로 돌립니다[14]. 설정 파일 사본에서 `file-store` 를 `enabled: yes`, `version: 2` 로 바꾸고, 아래 규칙 한 줄만 담은 `file.rules` 를 만듭니다[1].

```
alert http any any -> any any (msg:"FILE store all"; filestore; sid:1; rev:1;)
```

```sh
suricata -c suricata-copy.yaml -S file.rules -r capture-copy.pcap -l out -k none
```

`-S` 는 지정한 규칙 파일만 불러오고, `-l` 은 로그 폴더를 바꿉니다[13]. 돌린 뒤 아래 질문을 풀어 봅니다.

1. `out/eve.json` 의 `fileinfo` 기록 수와 `out/filestore` 아래 파일 수가 다르다면 이유는 무엇인가? (중복 제거, `TRUNCATED`, 저장 대상 아님)
2. 가장 큰 파일의 `state` 는 무엇인가? `stream.reassembly.depth` 를 0 으로 바꿔 다시 돌리면 달라지는가?
3. 저장 파일의 수정 시각과 `fileinfo` 의 `timestamp` 는 얼마나 차이 나는가? 어느 쪽을 보고서에 쓰는가?
4. 같은 파일의 `fileinfo` 와 `http` 기록에서 `src_ip` 가 서로 다른 주소인가? 이유는 무엇인가?

## 참고 문헌

1. OISF, Suricata User Guide — File Extraction. https://github.com/OISF/suricata/blob/main/doc/userguide/file-extraction/file-extraction.rst
2. OISF, Suricata User Guide — Suricata.yaml (File-store, stream, libhtp). https://github.com/OISF/suricata/blob/main/doc/userguide/configuration/suricata-yaml.rst
3. OISF, Suricata User Guide — Update File-store v1 Configuration to V2. https://github.com/OISF/suricata/blob/main/doc/userguide/file-extraction/config-update.rst
4. OISF, Suricata User Guide — Storing MD5s checksums. https://github.com/OISF/suricata/blob/main/doc/userguide/file-extraction/md5.rst
5. OISF, Suricata User Guide — File Keywords. https://github.com/OISF/suricata/blob/main/doc/userguide/rules/file-keywords.rst
6. OISF, Suricata User Guide — EVE JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
7. OISF, Suricata 소스 src/output-filestore.c. https://github.com/OISF/suricata/blob/main/src/output-filestore.c
8. OISF, Suricata 소스 src/output-json-file.c. https://github.com/OISF/suricata/blob/main/src/output-json-file.c
9. OISF, Suricata 소스 src/output-json.c. https://github.com/OISF/suricata/blob/main/src/output-json.c
10. OISF, Suricata User Guide — eve-log.yaml 설정 예. https://github.com/OISF/suricata/blob/main/doc/userguide/partials/eve-log.yaml
11. Security Onion Solutions, Security Onion Documentation — Suricata. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/suricata.rst
12. Security Onion Solutions, Security Onion Documentation — Strelka. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/strelka.rst
13. OISF, Suricata User Guide — Command Line Options. https://github.com/OISF/suricata/blob/main/doc/userguide/partials/options.rst
14. OISF, Suricata User Guide — PCAP File Reading. https://github.com/OISF/suricata/blob/main/doc/userguide/capture-hardware/pcap-file.rst
15. Jan-Niclas Hilgert, Axel Mahr, Martin Lambertz, "Mount SMB.pcap: Reconstructing file systems and file operations from network traffic", Forensic Science International: Digital Investigation, 2024. doi:10.1016/j.fsidi.2024.301807
16. OISF, Suricata 소스 src/util-time.c. https://github.com/OISF/suricata/blob/main/src/util-time.c
