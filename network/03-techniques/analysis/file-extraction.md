---
title: "세션 복원과 파일 꺼내기"
parent: "기법 · 분석"
nav_order: 370
---

# 세션 복원과 파일 꺼내기 (Reassembly·File Extraction)

TCP 는 데이터를 세그먼트로 잘라 보내므로, 패킷 캡처에서 파일이나 대화 내용을 읽으려면 세그먼트를 순서대로 다시 이어 붙이는 재조립 (reassembly) 을 거쳐야 합니다. 이 페이지는 캡처에 빠진 부분이 있는지 먼저 확인하고, 한 흐름을 이어 읽은 뒤, Wireshark·tcpflow·Zeek·Suricata 로 파일을 꺼내 해시로 서로 대조하는 순서를 다룹니다. 꺼낸 파일은 센서가 본 바이트로 다시 만든 사본이므로, 받은 호스트가 저장하거나 실행했는지는 따로 확인해야 합니다.

## 언제 쓰나

피싱 메일 링크를 눌러 받은 파일이 무엇인지, 내부 PC 가 밖으로 올려 보낸 자료가 무엇인지처럼 "무엇이 오갔나" 를 내용으로 확인해야 할 때 씁니다. 흐름 기록이나 연결 로그로는 누가 누구에게 몇 바이트를 보냈는지만 알 수 있어서, 내용과 해시가 필요하면 패킷 캡처로 돌아와 재조립합니다. 호스트에서 찾은 파일과 네트워크로 받은 파일이 같은지 해시로 맞춰 볼 때, 공유 폴더(SMB)로 읽고 쓴 파일을 되살릴 때도 이 순서를 따릅니다.

평문으로 오간 전송만 내용을 되살릴 수 있습니다. HTTPS 나 암호화된 SMB3 로 오간 파일은 암호문만 이어 붙게 되므로, 그런 전송에서 무엇을 볼 수 있는지는 [암호화된 트래픽 분석](encrypted-traffic.md) 을 봅니다. TCP 연결과 순서 번호의 기초는 [TCP 연결과 흐름](../../01-foundations/protocols/tcp-sessions.md) 에 있습니다.

## 절차

아래 예시의 주소·포트·파일 이름·시각·숫자는 모두 만든 예시입니다. 명령마다 도구 버전과 입력·출력 파일의 해시를 작업 기록에 함께 적습니다.

### 1. 원본은 두고 사본으로 작업한다

재조립과 파일 추출은 캡처 파일을 바꾸지 않지만, 도구가 출력 폴더에 파일을 많이 만들고 설정에 따라 결과가 달라집니다. 원본 캡처의 해시를 먼저 남기고 사본에서 작업합니다. 캡처가 너무 크면 사건 시간대만 잘라 낸 뒤 작업하고, 자르는 방법은 [큰 캡처 파일 다루기](../acquisition/large-captures.md) 를 봅니다.

### 2. 빠진 부분이 있는지 먼저 확인한다

캡처에서 패킷이 빠지면 어떤 도구로도 그 부분의 내용은 되살릴 수 없습니다. 그래서 파일을 꺼내기 전에 흐름마다 빠진 바이트가 있는지부터 봅니다.

Zeek 의 conn.log 에서 `missed_bytes` 는 내용 틈 (content gap) 으로 놓친 바이트 수이고, 패킷 손실을 뜻합니다. 0 이 아니면 보통 프로토콜 분석이 실패하지만 손실 전까지는 분석됐을 수 있습니다[11]. `history` 에 `g` 나 `G` 가 있으면 내용 틈이 있었다는 뜻이고, 연결을 연 쪽에서 생긴 틈은 대문자 `G`, 응답한 쪽에서 생긴 틈은 소문자 `g` 로 적힙니다[11]. conn.log 읽는 법은 [연결 기록](../../02-artifacts/zeek/zeek-logs/conn-log.md) 에 있습니다.

Wireshark 4.6.0 부터는 `tcp.stream.client.contiguity_count`·`tcp.stream.server.contiguity_count` 필드가 방향별로 끊긴 곳을 셉니다[5]. 값이 1 이면 이어져 있고, 0 이면 그 방향에 TCP 세그먼트가 아예 없고, 2 이상이면 데이터가 빠진 것입니다[2]. 앞의 100곳까지만 세는데, 이 정도면 그 캡처를 데이터 추출에 쓸 수 없거나 캡처에 큰 문제가 있었다고 판단하기에 충분합니다[2]. 그보다 오래된 버전에서는 "Previous segment(s) not captured (common at capture start)" 표시(`tcp.analysis.lost_segment`)로 빠진 세그먼트를 찾습니다[5].

```
tshark -r case.pcap -Y "tcp.stream.server.contiguity_count > 1" -T fields -e tcp.stream | sort -u
```

캡처할 때 패킷 앞부분만 저장했다면(snaplen) 모든 패킷의 내용이 잘려 있어서 재조립할 것이 없습니다. 이 경우는 [캡처 필터와 잘린 패킷](../../01-foundations/capture/capture-filters.md) 에서 확인합니다. 캡처를 시작하기 전에 이미 열려 있던 연결은 앞부분이 캡처에 없어서, 그 연결로 받은 파일은 처음부터 꺼낼 수 없습니다.

### 3. 어떤 파일이 오갔는지 목록부터 본다

파일을 모두 꺼내기 전에 목록으로 범위를 좁히면 일이 줄어듭니다. 이미 센서가 만든 로그가 있으면 그 로그를 먼저 봅니다.

Zeek 는 파일마다 files.log 에 한 줄을 남기고, 그 줄의 `uid` 로 파일을 나른 연결을, http.log 의 `resp_fuids`·`orig_fuids` 로 요청 URL 을 찾습니다[8]. files.log 에 줄이 있다고 파일을 디스크에 꺼낸 것은 아니고, 추출은 따로 설정해야 합니다[8]. 필드와 연결 방법은 [파일 기록 (files.log)](../../02-artifacts/zeek/zeek-logs/files-log.md) 에서 다룹니다. Suricata 는 EVE 의 `fileinfo` 기록에 파일마다 이름·크기·틈 여부·해시를 남기고, 같은 흐름의 `http`·`alert` 기록과 `flow_id` 로 묶입니다[14]. 이 기록은 [파일 추출 (filestore)](../../02-artifacts/suricata/eve-json/filestore.md) 에서 다룹니다.

로그가 없으면 Wireshark 의 File → Export Objects 창에서 프로토콜을 고르면 재조립된 객체 목록이 나옵니다. 목록에는 객체를 찾은 패킷 번호(Packet), 객체를 보낸 서버(Hostname), Content Type, 크기(Size, 바이트), 파일 이름(Filename)이 나옵니다[3]. 파일 이름은 프로토콜마다 만드는 방식이 달라서, HTTP 는 URI 의 마지막 부분을, 메일(IMF)은 메일 제목을 씁니다[3]. 트래픽에 실린 이름일 뿐 받은 호스트가 저장한 이름은 아닙니다. HTTP 본문 바이트만 필드로 뽑을 때는 `http.file_data` 필드(2.2.0 이후)를 씁니다[4].

### 4. 한 흐름을 이어 읽는다

파일을 꺼내기 전에 흐름 하나를 사람이 읽을 수 있게 이어 보면, 요청과 응답이 어떻게 오갔는지, 전송 인코딩이 무엇인지 알 수 있습니다. Wireshark 의 Analyze → Follow → TCP Stream 은 네트워크에 나타난 순서대로 내용을 보여 주고, 클라이언트가 보낸 데이터와 서버가 보낸 데이터를 색으로 나눕니다[2]. 재조립 설정과 상관없이 Follow TCP Stream 은 세그먼트를 올바른 순서로 보여 줍니다[2].

tshark 에서는 `-z follow,tcp,hex,스트림번호` 로 같은 내용을 헥스로 봅니다. 스트림 번호는 0 부터 셉니다[1]. 두 번째 노드(Node 1)가 보낸 데이터는 줄 앞에 탭이 붙고, 왼쪽 오프셋은 방향마다 따로 셉니다[1].

```
tshark -r case.pcap -q -z follow,tcp,hex,3
```

```
===================================================================
Follow: tcp,hex
Filter: tcp.stream eq 3
Node 0: 192.168.0.10:49152
Node 1: 203.0.113.20:80
00000000  47 45 54 20 2f 61 2e 65  78 65 20 48 54 54 50 2f  GET /a.e xe HTTP/
...
	00000000  48 54 54 50 2f 31 2e 31  20 32 30 30 20 4f 4b 0d  HTTP/1.1  200 OK.
...
```

위 출력은 명세에 맞춰 만든 예시입니다. 내부 PC 192.168.0.10 이 `GET /a.exe` 를 요청했고 203.0.113.20 이 `200 OK` 로 응답했습니다. HTTP 응답은 헤더가 끝나는 빈 줄(`0d 0a 0d 0a`) 다음부터 본문이고, 헤더의 `Transfer-Encoding`·`Content-Encoding` 에 따라 본문이 청크로 나뉘거나 압축돼 있을 수 있습니다. HTTP 메시지 구조는 [HTTP](../../01-foundations/protocols/http.md) 에 있습니다.

Wireshark 의 Follow 창에서 형식을 Raw 로 두고 Save as 를 누르면 줄바꿈을 더하지 않은 이진 파일로 저장됩니다[2]. YAML 형식은 조각마다 원래 캡처의 패킷 번호와 초 단위 시각을 함께 적어서, 파일의 어느 부분이 언제 도착했는지 확인할 때 씁니다[2].

### 5. 파일을 꺼낸다

도구마다 꺼내는 범위와 이름 짓는 방식이 달라서, 한 도구 결과만 보고 판단하지 않고 적어도 두 도구로 꺼내 비교합니다.

**Wireshark·tshark.** Export Objects 창의 Save All 은 화면에 보이지 않는 것까지 모든 객체를 Filename 열의 이름으로 저장합니다[3]. tshark 는 `--export-objects 프로토콜,폴더` 로 같은 일을 하고, 쓸 수 있는 프로토콜 목록은 `--export-objects help` 로 봅니다[1]. 이름이 겹치면 덮어쓰지 않고 확장자 앞에 번호를 붙입니다[1]. HTTP 응답은 Wireshark 의 Packet Bytes 창에 "Uncompressed entity body" 탭이 따로 생겨 본문을 보여 줍니다[2].

```
tshark -r case.pcap -q --export-objects http,out_http
```

**tcpflow.** TCP 흐름마다 파일 하나에 데이터를 저장합니다[6]. 기본 파일 이름은 보낸 주소·포트와 받는 주소·포트를 0 으로 채워 이은 `203.000.113.020.00080-192.168.000.010.49152` 형식(만든 예시)이고, 이 파일에는 203.0.113.20 의 80번 포트가 192.168.0.10 의 49152번 포트로 보낸 데이터가 들어 있습니다[6]. `-a` 는 모든 후처리(`-e all` 과 같음), `-Fk` 는 흐름 1000개씩 폴더를 나누는 옵션입니다[6]. HTTP 후처리(`-e http`)를 켜면 흐름 파일 옆에 `-HTTP`·`-HTTPBODY` 파일이 생기고, 본문이 gzip 으로 압축돼 있었다면 `-HTTPBODY-GZIP` 파일이 하나 더 생길 수 있습니다[6]. 흐름마다 주소·포트·패킷 수 같은 정보는 DFXML 보고서(기본 이름 `report.xml`)에 남고, `-FM` 을 주거나 HTTP 후처리를 켜면 흐름의 MD5 도 들어갑니다[6]. `startime`·`endtime` 은 첫 패킷과 마지막 패킷을 받은 시각이고, 끝에 `Z` 가 붙은 ISO 8601 형식으로 적힙니다[6]. 캡처가 TCP 세션의 시작을 담지 못한 경우처럼 내용이 빠진 곳은 흐름 파일에 0 으로 채워지고, 채운 횟수가 `out_of_order_count` 에 남습니다[6].

```
tcpflow -a -o out_flow -Fk -r case.pcap
```

`-I` 를 주면 흐름 파일마다 `*.findx` 파일이 따로 생기고, 한 줄에 `byte-index|timestamp|length` 를 적습니다[6]. `byte-index` 는 흐름 파일 안의 위치, `timestamp` 는 에포크 초(마이크로초까지), `length` 는 그 시각에 해당하는 바이트 수입니다[6]. 예를 들어 `0|1767225600.123456|1448`(만든 예시)이면 흐름 파일의 처음 1448바이트가 2026-01-01 00:00:00.123456 UTC 에 받은 패킷(여러 개일 수 있음)에 실려 왔다는 뜻입니다. 그 밖에 흐름당 저장량 한도 `-b`(기본 무제한, 1.4 이전에는 흐름당 4GiB 까지), 캡처 파일이 여러 개일 때 `-l`(뒤의 인자를 모두 입력 파일로 읽음)과 `-R`(앞 시간대 파일에서 시작한 흐름을 완성하는 데만 씀)이 있습니다[6].

**Zeek.** 파일 추출 분석기(EXTRACT)를 붙여야 파일이 디스크에 저장됩니다[7][8]. 배포판에 들어 있는 `policy/frameworks/files/extract-all-files.zeek` 스크립트를 실으면 본 파일을 모두 저장합니다[7]. `-C` 는 체크섬 오류를 무시하는 옵션으로, 체크섬 계산을 네트워크 카드에 맡긴 환경(checksum offloading)에서 뜬 캡처에 씁니다[12].

```
zeek -C -r case.pcap frameworks/files/extract-all-files.zeek
```

추출 파일은 기본으로 `./extract_files/` 에 저장되고(`FileExtract::prefix`), 파일 하나의 크기 한도는 `FileExtract::default_limit` 가 정하며 기본 104857600바이트(100MB)입니다[10]. 한도에는 기본으로 놓친 바이트도 포함됩니다(`FileExtract::default_limit_includes_missing = T`)[10]. files.log 의 `extracted` 에 저장한 파일 이름이, `extracted_cutoff` 에 한도 때문에 잘렸는지가 남습니다[10].

**Suricata.** 규칙이 없으면 아무것도 저장하지 않습니다[13]. 모든 HTTP 파일을 저장하는 가장 단순한 규칙은 다음과 같고, `fileext`·`filemagic`·`filemd5` 같은 키워드로 대상을 좁힐 수 있습니다[13]. 이 예시 규칙은 HTTP 만 대상으로 하므로 SMTP·FTP·SMB 같은 다른 프로토콜은 그 프로토콜로 규칙을 따로 적습니다.

```
alert http any any -> any any (msg:"FILE store all"; filestore; sid:1; rev:1;)
```

이 규칙을 파일에 저장해 `-S` 로 넘기면 설정 파일의 다른 규칙 없이 이 규칙만 싣고, `-r` 은 캡처 파일을, `-l` 은 로그 폴더를 정합니다[15]. `-k none` 은 체크섬 검사를 끕니다[15]. 파일을 디스크에 쓰려면 suricata.yaml 에서 file-store 출력도 켜야 하고, 켜는 방법과 저장 폴더 구조는 [파일 추출 (filestore)](../../02-artifacts/suricata/eve-json/filestore.md) 에 있습니다.

```
suricata -r case.pcap -k none -S filestore.rules -l out_suricata
```

저장된 파일은 로그 폴더 아래 `filestore` 에 내용의 SHA256 을 이름으로 해서 들어가고, SHA256 앞 두 글자 이름의 하위 폴더(`00`~`ff`)에 나뉩니다[13].

### 6. 해시를 구하고 도구끼리 대조한다

꺼낸 파일마다 SHA-256 을 구하고 크기를 로그의 값과 맞춰 봅니다. Zeek 는 files.log 의 `seen_bytes`·`missing_bytes`·`extracted_size`, Suricata 는 `fileinfo` 의 `size`·`gaps` 와 비교합니다[9][10][14]. Suricata 의 `md5`·`sha1`·`sha256` 은 해시 계산을 끄지 않았고 파일에 틈이 없을 때만 남습니다[14].

같은 스트림을 두 도구로 꺼내 해시가 같으면 결과를 믿을 수 있습니다. 해시가 다르면 먼저 전송 인코딩을 누가 풀었는지 봅니다. Suricata 는 HTTP 의 청크를 합치고 압축을 푼 내용을 파일로 다루고[13], tcpflow 의 흐름 파일은 HTTP 헤더까지 그대로 담은 TCP 데이터라서 HTTP 본문만 떼어도 인코딩이 남아 있을 수 있습니다. 그다음으로 틈과 크기 한도를 봅니다. tcpflow 는 빠진 곳을 0 으로 채우므로 DFXML 보고서에 `out_of_order_count` 가 있으면 그 흐름 파일의 해시는 원래 데이터의 해시와 다릅니다[6].

### 7. 결과를 기록한다

어떤 도구와 버전으로, 어떤 설정(크기 한도·체크섬 옵션·규칙)으로 꺼냈는지를 파일 해시와 함께 적습니다. 꺼낸 파일마다 그 파일을 나른 연결(주소·포트·Zeek `uid`·Suricata `flow_id`)과 캡처 안 패킷 번호를 이어 두면 나중에 다른 사람이 같은 결과를 다시 만들 수 있습니다. Suricata 를 pcap 파일로 돌리면 EVE 기록의 `pcap_cnt` 에 캡처 안 패킷 번호가 남아 Wireshark 에서 그 패킷을 바로 찾을 수 있습니다[14]. 보고서 쓰는 법은 [네트워크 포렌식 보고서](../reporting/forensic-report.md) 를 봅니다.

## 도구

| 도구 | 단위 | 꺼낸 파일 이름 | 크기 한도(기본) | 틈 표시 |
|---|---|---|---|---|
| Wireshark Export Objects, tshark `--export-objects` | 프로토콜 객체(HTTP 본문, 메일 등) | HTTP 는 URI 마지막 부분, 겹치면 번호 붙임[1][3] | — | 목록에 없음. `contiguity_count` 로 따로 확인[2] |
| tcpflow | TCP 흐름 한 방향 | 주소·포트를 이은 이름, `-F`·`-T` 로 바꿈[6] | 무제한(`-b`)[6] | 빠진 곳은 0 으로 채우고 DFXML `out_of_order_count` 에 횟수. `-m` 을 주면 그만큼 건너뛴 곳에서 새 파일로 나눔[6] |
| Zeek (EXTRACT) | 파일 | 추출을 설정한 스크립트가 정함[7] | 100MB[10] | files.log `missing_bytes`, `extracted_cutoff`[9][10] |
| Suricata (filestore) | 파일 | 내용의 SHA256[13] | `file-store.stream-depth` 1MB[13] | `fileinfo` 의 `gaps`[14] |
| NetworkMiner | 파일·이미지 | — | — | — |

NetworkMiner 는 pcap 파일을 열면 전송된 파일을 자동으로 찾아 꺼내 Files 탭에, 그중 이미지는 Images 탭에 보여 줍니다[16]. Security Onion 에서는 Zeek 나 Suricata 가 평문 트래픽에서 꺼낸 파일을 Strelka 가 YARA 규칙으로 검사하고, 48시간 안에 같은 해시의 파일은 다시 검사하지 않습니다[17]. 그래서 Strelka 기록이 한 번뿐이어도 같은 파일이 그 사이 여러 번 오갔을 수 있습니다.

Wireshark 로 캡처를 여는 법과 표시 필터는 [Wireshark·tshark로 읽기](wireshark.md) 에, Suricata 규칙을 캡처에 돌리는 법은 [탐지 규칙 활용](detection-rules.md) 에 있습니다.

## 함정과 한계

**재전송과 순서 어긋남을 도구마다 다르게 다룹니다.** tcpflow 는 TCP 순서 번호를 따라 재전송이나 순서 어긋남과 상관없이 스트림을 복원하고, 빠진 곳은 0 으로 채웁니다[6]. Wireshark 는 순서가 어긋난 세그먼트를 다시 맞추는 "Reassemble out-of-order segments" 설정이 기본으로 꺼져 있고, 켜더라도 캡처에서 패킷이 실제로 빠졌다면 스트림을 복원할 수 없습니다[2]. 무선 모니터 모드(IEEE 802.11) 캡처는 신호 수신 문제로 패킷이 빠지기 쉬워서 이 설정을 끄는 것이 좋습니다[2]. 그래서 같은 스트림을 두 도구로 꺼내 해시가 같은지 보는 절차가 필요합니다.

**재조립된 데이터는 마지막 패킷에 붙습니다.** Wireshark 는 여러 패킷에 걸친 데이터를 그 덩어리의 마지막 패킷에서 보여 주고, 나머지 세그먼트는 "[TCP segment of a reassembled PDU]" 로 표시합니다[2]. 필터로 파일 내용을 찾으면 걸리는 패킷 번호는 전송이 끝난 패킷이지 시작한 패킷이 아닙니다. 캡처 도중부터 시작한 연결이나 세그먼트가 빠진 연결에서는 HTTP 가 "Continuation" 으로, TLS 레코드가 "Ignored Unknown Record" 로 잘못 표시될 수 있습니다[2]. tshark 에서 재조립에 필요한 앞뒤 관계를 제대로 계산하려면 두 번 읽기(`-2`)를 씁니다[1].

**체크섬 검사로 패킷이 버려질 수 있습니다.** Suricata 의 `stream.checksum_validation` 은 기본으로 켜져 있어서, 체크섬 계산을 네트워크 카드에 맡긴 환경에서 뜬 캡처는 많은 패킷이 깨진 것처럼 보입니다[13]. pcap 파일 읽기의 `checksum-checks` 기본값 `auto` 는 체크섬 오프로딩을 통계로 알아채지만[19], 결과가 비어 보이면 `-k none` 으로 다시 돌려 봅니다. Zeek 는 `-C` 를 씁니다[12].

**큰 파일은 잘립니다.** Zeek 는 기본 100MB, Suricata 는 `file-store.stream-depth` 기본 1MB 에 닿으면 파일이 잘려 끝까지 저장되지 않을 수 있습니다[10][13]. HTTP 는 Suricata 의 `request-body-limit`·`response-body-limit` 도 파일 검사 범위를 제한하고, 0 이면 제한이 없습니다[13]. 잘린 파일의 해시는 원래 파일의 해시와 다릅니다.

**파일 이름은 보낸 쪽의 주장입니다.** Zeek files.log 의 `filename` 은 주로 Content-Disposition 헤더에서 오고[9], Wireshark 의 Filename 은 URI 끝부분이나 메일 제목에서 만듭니다[3]. 확장자와 실제 형식이 다를 수 있으므로 형식은 내용으로 다시 확인합니다.

**꺼낸 파일의 파일시스템 시각은 꺼낸 시각입니다.** 원래 파일이 만들어지거나 수정된 시각이 아닙니다. Suricata 는 같은 파일이 다시 추출되면 새로 쓰지 않고 이미 있는 파일의 시각만 `touch` 처럼 바꿉니다[13].

**일부만 오간 전송이 있습니다.** Suricata `fileinfo` 의 `start`·`end` 는 잡힌 첫 바이트와 마지막 바이트의 오프셋이고, HTTP 의 Content-Range 값과 같습니다[14]. 이런 기록이 있으면 꺼낸 내용은 원래 파일의 일부입니다.

**꺼낸 파일은 악성일 수 있습니다.** 실행 파일이나 문서를 꺼냈다면 분석용으로 격리된 환경에서만 열고, 원래 이름 대신 해시로 다룹니다.

## 결과를 어떻게 해석하나

### 증명하는 것

캡처 지점을 지나간 바이트로 되살린 파일의 내용과 해시, 그 파일을 나른 연결의 주소·포트, 보낸 방향을 증명합니다. Zeek files.log 의 `is_orig` 는 파일을 연결을 연 쪽이 보냈는지 응답한 쪽이 보냈는지를 나타냅니다[9]. 틈이 없고 크기가 로그와 같으며 두 도구로 꺼낸 해시가 같으면, 그 해시로 호스트에서 찾은 파일이나 위협 정보와 대조할 수 있습니다.

### 증명하지 못하는 것

받은 호스트가 그 파일을 디스크에 저장했는지, 열거나 실행했는지는 알 수 없습니다. 이는 호스트 쪽 기록으로 확인합니다. 틈이 있거나 잘린 파일로는 원래 파일의 해시를 알 수 없습니다. 어느 사용자나 프로그램이 파일을 주고받았는지도 네트워크 기록에는 없습니다. 암호화된 전송은 내용을 되살릴 수 없습니다.

### 시각

패킷의 시각은 센서가 패킷을 캡처한 시각이고, 기준 시계와 UTC 여부는 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에서 다룹니다. Zeek files.log 의 `ts` 는 파일을 처음 본 시각입니다[9]. Suricata 가 파일마다 따로 남기는 `SHA256.초.ID.json` 이름의 초는 저장한 파일을 닫게 한 패킷의 초입니다. 이 값은 이름이 겹치지 않게 하려고 넣은 것이라 시각 근거로 쓰지 않고[13], 시각은 `fileinfo` 기록의 `timestamp` 로 봅니다[14]. tcpflow 는 `-Ft`(Unix 시각)나 `-FT`(ISO 8601 시각)로 파일 이름 앞에 시각을 붙이고, `-I` 의 `.findx` 로 바이트 위치마다 도착 시각을 남깁니다[6]. 여러 소스의 시각을 합치는 방법은 [네트워크 타임라인](timeline.md) 을 봅니다.

### SMB 공유 폴더 되살리기

Wireshark 같은 도구는 SMB 로 오간 파일을 하나씩 꺼낼 뿐 폴더 구조나 파일 시각까지 되살리지는 않습니다[18]. Hilgert·Mahr·Lambertz(2024)는 SMB 트래픽에서 공유 폴더의 폴더 구조와 메타데이터, 파일의 여러 버전까지 되살리는 방법을 제안했습니다[18]. 시각·크기 같은 메타데이터는 주로 CREATE 응답에서 얻고 QUERY_INFO 응답, QUERY_DIRECTORY 응답, SET_INFO 요청으로 보태며, CREATE 응답의 16바이트 FileId 로 이후 READ·WRITE 명령을 파일에 연결한 뒤 명령의 오프셋과 길이로 내용을 채웁니다[18]. 내용이 트래픽에 없어도 이름·경로·속성·시각만으로 빈 파일(hollow file)을 만들어 두고, 캡처 기간 중 시각이 바뀌면 이름 뒤에 `@버전` 을 붙인 새 버전으로 남깁니다[18]. 공유 폴더에는 남지 않은 옛 버전이 트래픽에만 있을 수 있다는 점에서 쓸모가 있습니다.

같은 논문의 시험에서는 cmd.exe 로 약 2분 동안 실행한 명령 18개(SMB 패킷 약 250개) 가운데 16개를 트래픽만으로 되살렸습니다. 나머지 둘은 SMB 명령을 만들지 않은 `cd` 명령이었고, 연구자들은 캐시 때문으로 봤습니다[18]. 되살린 사건의 시각은 캡처 지연 때문에 실제 실행 시각보다 늦고, 실제 환경에서는 네트워크 구성에 따라 차이가 크게 달라질 수 있습니다[18]. 이 결과는 연구자의 시험 환경에서 나온 것입니다. SMB 프로토콜 기초는 [SMB와 원격 관리 프로토콜](../../01-foundations/protocols/remote-protocols.md) 에 있습니다.

### 보고서 문장

보고서에는 "파일을 내려받았다" 가 아니라 기록으로 확인되는 만큼만 씁니다. 예: "2026-01-01 00:00:00 UTC 부터 약 2초 동안 203.0.113.20:80 이 192.168.0.10:49152 로 보낸 HTTP 응답 본문에서 179,272바이트 파일을 꺼냈고, 빠진 바이트는 없으며 Wireshark 와 Zeek 로 꺼낸 파일의 SHA-256 이 같다"(만든 예시). 받은 파일이 호스트에서 어떻게 쓰였는지는 [피싱 링크를 눌렀나](../../04-scenarios/user-activity/phishing-click.md), 밖으로 보낸 자료를 다루는 흐름은 [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration.md) 를 봅니다.

## 참고 문헌

1. Wireshark, tshark(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
2. Wireshark User's Guide, "Advanced Topics"(Following Protocol Streams, TCP Streams Contiguities, Packet Reassembly). https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_advanced.adoc
3. Wireshark User's Guide, "File Input, Output, And Printing"(The "Export Objects" Dialog Box). https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_io.adoc
4. Wireshark, Display Filter Reference: HTTP. https://www.wireshark.org/docs/dfref/h/http.html
5. Wireshark, Display Filter Reference: TCP. https://www.wireshark.org/docs/dfref/t/tcp.html
6. tcpflow(1) 매뉴얼. https://github.com/simsong/tcpflow/blob/main/doc/tcpflow.1.in
7. Zeek Documentation, "File Analysis". https://github.com/zeek/zeek-docs/blob/master/frameworks/file-analysis.rst
8. Zeek Documentation, "files.log". https://github.com/zeek/zeek-docs/blob/master/logs/files.rst
9. Zeek Documentation, base/frameworks/files/main.zeek (Files::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/frameworks/files/main.zeek.rst
10. Zeek Documentation, base/files/extract/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/files/extract/main.zeek.rst
11. Zeek Documentation, base/protocols/conn/main.zeek (Conn::Info). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
12. Zeek Documentation, "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
13. Suricata User Guide, "File Extraction". https://github.com/OISF/suricata/blob/main/doc/userguide/file-extraction/file-extraction.rst
14. Suricata User Guide, "Eve JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
15. Suricata User Guide, 명령줄 옵션. https://github.com/OISF/suricata/blob/main/doc/userguide/partials/options.rst
16. Security Onion Documentation, "NetworkMiner". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/networkminer.rst
17. Security Onion Documentation, "Strelka". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/strelka.rst
18. Jan-Niclas Hilgert, Axel Mahr, Martin Lambertz, 「Mount SMB.pcap: Reconstructing file systems and file operations from network traffic」, Forensic Science International: Digital Investigation 50, 301807, 2024. doi:10.1016/j.fsidi.2024.301807
19. Suricata User Guide, "PCAP File Reading". https://github.com/OISF/suricata/blob/main/doc/userguide/capture-hardware/pcap-file.rst
