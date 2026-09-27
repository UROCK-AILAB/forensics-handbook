---
title: "자료를 밖으로 보냈나"
parent: "시나리오 · 자료 유출"
nav_order: 490
---

# 자료를 밖으로 보냈나 (Data Exfiltration)

내부 PC 가 자료를 밖으로 보내면 네트워크 기록에는 "연결을 연 쪽이 받은 양보다 훨씬 많이 보낸 연결" 이 남고, 평문 프로토콜이면 파일 이름·크기·해시까지 남습니다. 이 페이지에서는 흐름 기록, Zeek·Suricata 로그, 프록시 로그로 유출 후보 연결을 찾고, 어떤 프로토콜로 무엇을 보냈는지 좁혀 가는 순서를 다룹니다. 각 로그의 필드 설명은 아티팩트 페이지에 있고, 여기서는 어느 필드를 어떤 순서로 보는지와 해석할 때 틀리기 쉬운 점만 씁니다.

## 조사 질문

- 어느 내부 주소가 어느 외부 주소로, 언제, 얼마나 보냈나?
- 보낸 양이 받은 양보다 크게 많은 연결, 평소 없던 목적지, 오래 이어진 연결이 있나?
- 어떤 프로토콜로 보냈나(HTTP 업로드, FTP, 메일, SMB, TLS 로 감싼 연결)?
- 평문이라면 파일 이름·크기·MIME 형식·해시를 알 수 있나?
- 그 시각에 그 내부 주소를 쓴 기기와 사용자는 누구인가?

DNS 질의 이름에 자료를 실어 보냈는지는 [DNS 로 몰래 보냈나](dns-tunneling.md) 에서 따로 다룹니다.

## 먼저 확인할 것

**센서와 로그를 만든 장비가 어디에 있었는지 확인합니다.** 센서가 프록시 뒤(인터넷 쪽)에 있으면 모든 웹 연결의 출발지가 프록시 하나로 보이고, NAT 장비 바깥에 있으면 출발지가 공인 주소 하나로 모입니다. 이때 내부 PC 는 프록시 로그나 NAT 기록으로 찾아야 합니다. 주소 변환을 읽는 법은 [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md) 에 있습니다.

**기록마다 양을 세는 방식과 빠지는 부분을 확인합니다.** 같은 전송이라도 설정에 따라 기록되는 양이 다릅니다.

| 확인할 것 | 기본값·동작 | 해석에 주는 영향 |
|---|---|---|
| Zeek `Site::local_nets` | 정의하지 않으면 conn.log `local_orig`·`local_resp` 가 늘 비어 있음[2] | 내부→외부 연결을 필드 하나로 골라낼 수 없어 주소 대역으로 걸러야 합니다. |
| Zeek `use_conn_size_analyzer` | 이 값이 T 일 때만 `orig_pkts`·`orig_ip_bytes`·`resp_pkts`·`resp_ip_bytes` 가 채워짐[2] | 이 필드가 비어 있으면 페이로드 바이트(`orig_bytes`)만으로 양을 봅니다. |
| Zeek `SMB::logged_file_actions` | `PRINT_CLOSE`, `FILE_DELETE`, `FILE_OPEN`, `FILE_RENAME`, `PRINT_OPEN`[11] | 기본 설정의 smb_files.log 에는 `FILE_READ`·`FILE_WRITE` 가 남지 않습니다. 파일 내용 전송은 files.log 로 봅니다. |
| Suricata `netflow` 이벤트 | 기본으로 꺼짐, 켜면 한 방향씩 따로 기록해 `flow` 이벤트의 두 배 개수[14] | 양방향 합계는 `flow` 이벤트로 봅니다. |
| Squid `logformat` | 기본 `squid`·`common`·`combined` 형식에는 응답 크기 `%<st` 만 있고 요청 크기 `%>st` 가 없음[15] | 기본 형식의 프록시 로그로는 업로드한 양을 알 수 없습니다. |
| NetFlow·IPFIX 샘플링 | `SAMPLING_INTERVAL` 이 100 이면 패킷 100개 중 1개만 표본으로 셈[17] | 샘플링한 흐름의 바이트 수는 실제 전송량이 아닙니다. |

**시각 기준을 맞춥니다.** Zeek conn.log 의 `ts` 는 연결의 첫 패킷 시각이고[2], files.log 의 `ts` 는 파일을 처음 본 시각입니다[6]. Zeek 로그의 시각은 기본적으로 epoch 초이고, `zeek-cut -d` 를 쓰면 사람이 읽는 형식으로, `-u` 를 쓰면 UTC 로 바꿔 보여 줍니다(두 옵션의 기본 형식 `%Y-%m-%dT%H:%M:%S%z`)[3]. Suricata EVE 의 `timestamp` 에는 시간대 오프셋이 붙어 나오므로 센서의 시간대 설정을 확인합니다[13]. Squid 기본 형식의 첫 필드(`%ts.%03tu`)는 로그를 쓸 때의 시각이고, 트랜잭션 시작 시각은 `%tS`(요청 헤더를 다 받은 시각)입니다[15]. Squid 는 응답 시간(`%tr`, 밀리초)을 `%tS` 부터 계산하므로[15], 오래 걸린 업로드는 첫 필드의 시각이 트랜잭션 시작보다 대략 `%tr` 만큼 늦습니다. 자세한 내용은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에 있습니다.

## 볼 아티팩트와 순서

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 흐름 기록(NetFlow v9·IPFIX, nfdump) | 출발지·목적지·포트별 바이트·패킷 수, 첫·마지막 패킷 시각 | [흐름 기록](../../01-foundations/records/flow-records.md), [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md) |
| Zeek conn.log | 연결을 연 쪽·받은 쪽이 각각 보낸 페이로드 바이트, 길이, 확인된 프로토콜(`service`) | [conn.log](../../02-artifacts/zeek/zeek-logs/conn-log.md) |
| Suricata EVE `flow` | 서버 쪽으로 간 바이트·패킷(`bytes_toserver`)과 반대 방향 양, 흐름 시작·끝 | [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md) |
| Zeek http.log | 메서드(POST·PUT), 호스트, URI, 요청 본문 크기, 올린 파일 목록 | [http.log](../../02-artifacts/zeek/zeek-logs/http-log.md) |
| Zeek ftp.log · smtp.log | FTP 올리기 명령(STOR·STOU·APPE)과 파일 크기, 메일 발신자·수신자·첨부 파일 ID | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) |
| Zeek files.log · Suricata `fileinfo` | 파일을 보낸 방향(`is_orig`), 이름, MIME 형식, 크기, 해시 | [files.log](../../02-artifacts/zeek/zeek-logs/files-log.md), [파일 꺼내기](../../03-techniques/analysis/file-extraction.md) |
| Zeek ssl.log | 암호화된 연결의 서버 이름(SNI), 핸드셰이크 성공 여부 | [ssl·x509 로그](../../02-artifacts/zeek/zeek-logs/ssl-x509-log.md), [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md) |
| 프록시·방화벽 로그 | 사용자 이름(인증 프록시), 요청 URL, 허용·차단 | [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md), [방화벽 로그](../../02-artifacts/devices/firewall-logs.md) |
| DHCP·VPN 로그 | 그 시각에 그 내부 주소를 받은 기기·계정 | [DHCP 로그](../../02-artifacts/devices/dhcp-logs.md), [VPN 서버 로그](../../02-artifacts/devices/vpn-logs.md) |

## 분석 흐름

1. **내부→외부로 많이 보낸 출발지를 찾습니다.** 흐름 기록이 있으면 nfdump 로 내부 대역에서 외부로 나간 흐름만 골라 출발지별 바이트 합을 봅니다. NetFlow v9 의 흐름은 한 방향 패킷 묶음이라[17], 출발지가 내부이고 목적지가 외부인 흐름의 바이트는 곧 내부에서 보낸 양입니다.

   ```bash
   # 조사 구간의 흐름 파일 디렉터리를 읽어, 내부→외부 흐름의 출발지별 바이트 상위 20개
   nfdump -r /data/flows -n 20 -s srcip/bytes \
     'src net 10.0.0.0/8 and not dst net 10.0.0.0/8 and first seen >= 2025-03-14T00:00:00 and last seen <= 2025-03-14T06:00:00'
   ```

   `-s` 는 상위 N개 통계이고 기본 개수는 10개이며, `-n 0` 이면 제한이 없습니다[16]. `-t` 옵션은 예전 방식이라 시간 범위는 `first seen`·`last seen` 필터로 줍니다[16]. 출발지를 좁혔으면 `-s record/bytes` 로 흐름 레코드별 상위 목록을 봅니다[16]. 오래 이어진 연결은 장비가 일정 간격으로 끊어 여러 레코드로 내보내므로[17], 연결 단위 합계는 5튜플로 묶는 `-a` 를 붙여 확인합니다[16]. 양방향을 한 줄로 보려면 `-b` 를 씁니다[16]. `-B` 는 포트 번호로 클라이언트→서버 방향을 추측해 뒤집는 편의 옵션이라[16], 방향 판단에 쓰기 전에 원래 레코드와 비교합니다.

2. **Zeek conn.log 로 연결 단위의 방향과 양을 확인합니다.** `orig_bytes` 는 연결을 연 쪽이 보낸 페이로드 바이트, `resp_bytes` 는 받은 쪽이 보낸 페이로드 바이트입니다[2]. 내부 PC 가 연 연결에서 `orig_bytes` 가 `resp_bytes` 보다 크게 많으면 올리기에 가까운 모양입니다.

   ```bash
   # TSV 형식 conn.log 기준: 보낸 양(6번째 열) 순으로 정렬
   zeek-cut -u ts uid id.orig_h id.resp_h id.resp_p orig_bytes resp_bytes duration service < conn.log \
     | sort -t$'\t' -k6,6nr | head -20
   ```

   `Site::local_nets` 가 설정돼 있으면 `local_orig` 가 `T` 이고 `local_resp` 가 `F` 인 줄만 남겨 내부→외부 연결로 좁힙니다[2]. 같은 연결을 Suricata 로 보면 `flow` 이벤트의 `bytes_toserver`·`bytes_toclient` 가 두 방향의 양입니다[13]. 예를 들어 클라이언트가 많이 보낸 HTTP 흐름은 `bytes_toserver` 가 3,536,402, `bytes_toclient` 가 94,102 바이트처럼 서버 쪽으로 보낸 양이 받은 양의 37배를 넘는 모양으로 남습니다[13]. 두 도구의 흐름은 `uid`(Zeek)와 `flow_id`(Suricata)로 각각 다른 로그 줄과 이어 볼 수 있습니다[1][13].

3. **오래 이어진 연결과 처음 보는 목적지를 봅니다.** 한 번에 많이 보내지 않고 긴 연결 하나로 천천히 보내는 경우도 있습니다. RITA 는 Zeek 로그를 가져와(`rita import --database=이름 --logs=경로`) 오래 이어진 연결에 점수를 매기는데, 기본 기준은 1시간(3600초)부터이고 4·8·12시간에서 단계가 올라갑니다[19][20]. 위협 정보 목록에 있는 목적지와 25 MB(25,000,000 바이트) 이상 주고받았으면 점수를 15% 올립니다[19]. RITA 는 기본적으로 내부↔내부, 외부↔외부 연결을 가져올 때 버리고, 외부에서 내부로 연 연결도 무시합니다[19]. 내부 프록시를 거치는 환경이면 프록시 주소를 `always_included_subnets` 에 넣어야 합니다[19]. 같은 목적지로 짧은 연결이 규칙적으로 반복되는 모양은 [비컨 찾기](../../03-techniques/analysis/beaconing.md) 에서 다룹니다.

4. **후보 연결의 프로토콜을 확인하고 내용 로그를 붙입니다.** conn.log 의 `service` 에 확인된 프로토콜이 쉼표로 나옵니다[2]. 같은 `uid` 로 아래 로그를 찾습니다.

   | 프로토콜 | 볼 로그와 필드 | 올리기로 읽는 기준 |
   |---|---|---|
   | HTTP | http.log `method`, `host`, `uri`, `user_agent`, `request_body_len`, `orig_fuids`·`orig_filenames`·`orig_mime_types`[4] | POST·PUT 이고 `request_body_len`(클라이언트가 보낸 본문의 압축 풀린 크기)이 큼[4] |
   | FTP | ftp.log `user`, `command`, `arg`, `file_size`, `data_channel`[9] | `command` 가 STOR·STOU·APPE[8] |
   | SMTP | smtp.log `mailfrom`, `rcptto`, `subject`, `tls`, `fuids`[10] | 외부 수신자 앞 메일의 `fuids`(첨부 등 파일 ID) |
   | SMB | files.log(`source` 가 SMB), smb_files.log[11] | files.log `is_orig` 가 `true`[6] |
   | TLS | ssl.log `server_name`, `established`[12] | 내용은 안 보이므로 SNI 와 conn.log `orig_bytes` 로만 판단 |

   http.log 의 `orig_fuids` 같은 올린 파일 목록은 `entities.zeek` 가 로드돼 있을 때만 있고, http.log 한 줄에 기본 15개(`HTTP::max_files_orig`)까지만 기록합니다[4][5]. ftp.log 에서 기본으로 기록하는 명령은 ACCT·DELE·APPE·RETR·PORT·STOR·EPRT·PASV·STOU·EPSV 이고[8], `user` 를 알 수 없으면 `<unknown>` 이 들어갑니다[9]. 비밀번호는 `FTP::default_capture_password` 가 기본값 F 라서 기본 설정에서는 남지 않습니다[9]. smtp.log 의 `fuids` 는 `smtp/files.zeek` 가 로드돼 있을 때 있습니다[10]. 프로토콜별 구조는 [HTTP](../../01-foundations/protocols/http.md), [메일 프로토콜](../../01-foundations/protocols/mail-protocols.md), [SMB와 원격 관리 프로토콜](../../01-foundations/protocols/remote-protocols.md) 에 있습니다.

5. **파일이 어느 방향으로 갔는지 files.log 로 정합니다.** files.log 의 `is_orig` 는 연결을 연 쪽이 파일을 보냈는지를 나타냅니다[6]. 내부 PC 가 연 연결에서 `is_orig` 가 `true` 면 내부에서 밖으로 보낸 파일이고, `false` 면 받은 쪽(서버)이 보낸 파일, 곧 내려받은 파일입니다[6][7]. `filename` 은 주로 Content-Disposition 헤더에서 오고[6], `mime_type` 은 파일 앞부분의 매직 시그니처로 정합니다[6]. `seen_bytes`·`missing_bytes` 는 이 Zeek 인스턴스가 본 모든 연결에 걸친 합계라서[6] 한 연결의 양과 다를 수 있습니다.

   ```bash
   # JSON 형식 files.log 기준: 연결을 연 쪽이 보낸 파일만
   jq -c 'select(.is_orig==true) | [.ts, .uid, .source, .filename, .mime_type, .seen_bytes, .total_bytes, .missing_bytes, .sha256]' files.log
   ```

   Suricata 의 `fileinfo` 이벤트에는 `filename`, `magic`, `size`, `gaps`, `sha256` 이 있고, `md5`·`sha1` 은 파일이 닫혔을 때만 들어갑니다[13]. `gaps` 가 true 이면 파일에 빠진 부분이 있고, 이때는 해시도 남지 않습니다[13]. 캡처가 있으면 파일을 떼어 내 해시를 계산합니다. 방법은 [세션 복원과 파일 꺼내기](../../03-techniques/analysis/file-extraction.md) 에 있습니다.

6. **SMB 로 옮긴 파일은 캡처에서 되살립니다.** 기본 설정의 smb_files.log 에는 읽기·쓰기가 남지 않으므로[11], 원본 패킷이 있으면 SMB2 요청·응답으로 파일 목록을 되살립니다. SMB2 CREATE 응답에는 생성·마지막 접근·마지막 쓰기·변경 시각과 16바이트 FileId 가 있고, READ·WRITE 요청에는 FileId·오프셋·길이가 있어, 이것만으로 공유 폴더 구조·메타데이터·내용을 되살릴 수 있습니다[24]. 내용이 캡처에 없어도 이름·경로·속성·시각을 담은 빈 파일(hollow file)로 만들 수 있고, 공개 도구 pcapFS 가 이 방식을 씁니다[24]. 이 방법을 낸 연구에서 Windows 11 Pro(Build 22621.3155) 두 대를 SMB 공유와 클라이언트로 두고 시험했을 때는, Windows API `ReadFile` 로 2,097,152 바이트를 넘게 읽으면 READ 요청 여러 개로, `WriteFile` 로 3,473,408 바이트를 넘게 쓰면 WRITE 요청 여러 개로 나뉘었습니다[24]. 다른 버전에서는 값이 다를 수 있으므로 실제 캡처로 확인합니다.

7. **암호화된 연결은 서버 이름과 양으로만 판단합니다.** HTTPS 로 올린 경우 파일 이름과 내용은 로그에 없습니다. ssl.log 의 `server_name`(클라이언트가 요청한 서버 이름)[12]과 conn.log 의 `orig_bytes`, 인증서 정보를 묶어 "어느 서비스로 얼마나 보냈는가" 까지만 씁니다. 서버를 알아보는 법은 [인증서로 서버 알아보기](../../02-artifacts/fingerprints/certificates.md) 와 [TLS 지문](../../02-artifacts/fingerprints/ja3-ja4.md) 에 있습니다. 패킷 캡처만 있을 때는 `tshark -z conv,tcp` 로 대화마다 양방향 프레임·바이트 수, 상대 시작 시각, 길이를 볼 수 있습니다[18].

8. **탐지 규칙으로 도구와 서비스의 흔적을 더합니다.** Sigma 규칙 중에는 프록시 로그에서 User-Agent 가 `rclone/v` 로 시작하는 요청(클라우드 저장소 동기화 도구 rclone 의 기본 값)을 찾는 규칙이 있고, 수준은 medium 이며 정상 스크립트·관리 작업이 오탐으로 적혀 있습니다[21]. Zeek http.log 에서 User-Agent 에 `WebDAV` 가 들어 있고 메서드가 `PUT` 이며 목적지가 사설·루프백·링크 로컬 대역(10/8, 127/8, 172.16/12, 192.168/16, 169.254/16)이 아닌 요청을 찾는 규칙은 수준이 low 입니다[22]. 텔레그램 봇 API(`api.telegram.org`)에 User-Agent 에 `Telegram`·`Bot` 이 없는 채로 접근한 요청을 찾는 규칙도 있습니다[23]. 경보 하나로 유출을 판단하지 않고, 1~7단계의 양과 방향으로 확인합니다. 규칙을 쓰는 법은 [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md) 에 있습니다.

9. **내부 주소를 기기와 사람으로 이어 붙입니다.** IP 주소는 기기를 가리킬 뿐입니다. 그 시각에 그 주소를 받은 기기는 DHCP 로그로, 원격 접속 사용자는 VPN 로그로, 사용자 이름은 인증 프록시 로그로 찾습니다. 순서는 [이 시각에 이 IP 를 누가 썼나](../user-activity/ip-attribution.md) 에 있습니다.

10. **호스트 기록과 시간순으로 합칩니다.** 어떤 파일을 어떤 프로그램으로 보냈는지는 PC 쪽 기록으로 확인합니다. 운영체제별 방법은 [Windows](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/exfiltration/data-exfiltration/), [macOS](https://urock-ailab.github.io/forensics-handbook/mac/04-scenarios/exfiltration/data-exfiltration/), [Linux](https://urock-ailab.github.io/forensics-handbook/linux/04-scenarios/insider/data-exfiltration.html) 핸드북에 있고, 합치는 방법은 [네트워크 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다.

## 흔한 오판

**`orig` 는 늘 내부 PC 다.** Zeek 의 `orig` 는 연결을 연 쪽입니다[2]. 외부에서 들어온 연결이면 `orig` 가 외부 주소이고, active FTP 의 데이터 연결은 서버가 소스 포트 20 으로 클라이언트에 연결하므로 서버 쪽이 `orig` 가 됩니다[7]. conn.log `history` 에 `^` 가 있으면 Zeek 가 추측으로 방향을 뒤집은 연결입니다[2]. "보낸 양" 을 읽기 전에 어느 쪽이 연결을 열었는지 먼저 확인합니다.

**`orig_bytes` 는 정확한 전송량이다.** TCP 의 `orig_bytes` 는 시퀀스 번호로 계산해서 큰 연결에서는 부정확할 수 있습니다[2]. `missed_bytes` 가 0 이 아니면 패킷을 놓친 것이고 프로토콜 분석도 보통 실패합니다[2]. 크기를 교차 확인할 때는 IP 헤더의 전체 길이로 센 `orig_ip_bytes` 를 함께 봅니다[2]. HTTP 요청 하나만 보낸 작은 연결은 `orig_bytes` 가 77 바이트여도 `orig_ip_bytes` 는 397 바이트일 만큼 헤더가 차지하는 몫이 큽니다[1].

**conn.log 에 한 줄이 없으니 그 시각에 연결이 없었다.** conn.log 는 연결 하나를 한 줄로 요약한 기록이라[1], 수집 시점에 아직 이어지고 있던 긴 업로드는 그 시점의 로그에 없을 가능성이 있습니다. 흐름 기록은 반대로 긴 연결을 여러 레코드로 쪼개 내보냅니다[17]. 수집 시점과 기록 방식을 확인하고 여러 기록을 겹쳐 봅니다.

**프록시 로그에 업로드 크기가 없으니 올리지 않았다.** Squid 기본 형식에는 요청 크기 필드가 없습니다[15]. 크기가 필요하면 그 프록시의 `logformat` 설정에 `%>st` 가 들어 있는지 확인합니다[15]. 없으면 흐름 기록이나 센서 로그로 양을 봅니다.

**smb_files.log 에 `FILE_WRITE` 가 없으니 공유 폴더에 쓰지 않았다.** 기본 기록 동작에 `FILE_WRITE` 가 없습니다[11]. 반대로 `FILE_WRITE` 줄이 있다면 그 센서는 설정을 바꾼 것입니다. 자세한 설명은 [내부에서 다른 PC 로 옮겨 갔나](../intrusion/lateral-movement.md) 에 있습니다.

**흐름 기록의 바이트가 실제 양이다.** 샘플링을 켠 장비의 흐름 기록은 표본 패킷만 센 값입니다[17]. Suricata 가 우회(bypass)시킨 흐름은 `bypassed.*` 에 따로 세고[13], 그 부분의 내용은 검사하지 않았습니다. 이런 경우의 양은 하한값이나 추정치로 씁니다.

**Sigma 규칙에 exfiltration 태그가 붙어 있으니 유출이다.** 위 규칙들의 수준은 low·medium 이고[21][22][23], rclone·텔레그램 규칙에는 정상 사용이 오탐 사례로 들어 있습니다[21][23]. 텔레그램 API 규칙은 유출이 아니라 명령·제어 태그가 붙어 있습니다[23].

## 증명하는 것 / 증명하지 못하는 것

네트워크 기록으로 증명할 수 있는 것은 이 시간대에 이 내부 주소가 이 외부 주소·포트로 연결을 열고, 연결 단위로 이만큼 보내고 이만큼 받았다는 사실입니다. 평문 HTTP·FTP·SMTP·SMB 라면 올린 파일의 이름·크기·MIME 형식·해시와 메일 수신자까지 확인됩니다. TLS 연결이면 요청한 서버 이름(SNI)과 인증서까지 확인됩니다.

증명하지 못하는 것은 어느 사용자·프로그램이 보냈는지, 암호화된 연결 안에 어떤 파일이 들어 있었는지, 받는 쪽이 자료를 실제로 저장했는지입니다. 흐름 기록만 있으면 파일 단위로 나눌 수 없습니다. 샘플링·우회·패킷 손실(`missed_bytes`)이 있으면 기록된 양은 실제보다 적습니다. IP 주소와 사람을 잇는 일은 DHCP·VPN·NAT·프록시 기록이 있어야 가능합니다.

## 보고서 문장 예

아래 문장의 주소·이름·시각·크기는 모두 만든 예시입니다.

- 2025-03-14 01:10~01:52(UTC)에 내부 주소 10.0.5.23 이 203.0.113.40 의 443/tcp 로 연 TCP 연결 1건이 Zeek conn.log 에 있다. 연결을 연 10.0.5.23 이 보낸 페이로드는 약 1.9 GB 이고 받은 양은 약 3 MB 다.
- 같은 연결(같은 `uid`)의 ssl.log 에서 클라이언트가 요청한 서버 이름은 `files.example.net` 이다. 내용은 TLS 로 암호화돼 있어 어떤 파일을 보냈는지는 네트워크 기록만으로 확인되지 않는다.
- 같은 시간대의 흐름 기록에서도 10.0.5.23 에서 203.0.113.40 으로 가는 흐름의 바이트 합이 conn.log 와 비슷하게 나타난다. 이 흐름 기록은 샘플링하지 않은 설정에서 만들어졌다.
- 해당 시각에 10.0.5.23 을 할당받은 기기는 DHCP 로그상 `ws-015` 이며, 그 기기를 누가 쓰고 있었는지는 PC 쪽 로그인 기록으로 확인해야 한다.

## 함께 볼 페이지

- [흐름 기록](../../01-foundations/records/flow-records.md) · [네트워크 로그의 종류](../../01-foundations/records/log-types.md) · [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) · [TCP 연결과 흐름](../../01-foundations/protocols/tcp-sessions.md) · [TLS와 인증서](../../01-foundations/protocols/tls.md)
- [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) · [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md) · [웹 프록시 로그](../../02-artifacts/devices/proxy-logs.md)
- [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md) · [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md) · [네트워크 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)
- [DNS 로 몰래 보냈나](dns-tunneling.md) · [악성 코드가 C2 서버와 통신했나](../intrusion/c2-communication.md) · [이 시각에 이 IP 를 누가 썼나](../user-activity/ip-attribution.md)
- 다른 핸드북: [Windows 자료 유출](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/exfiltration/data-exfiltration/) · [Windows 개인정보 노출](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/exfiltration/pii-exposure.html) · [Android 자료 유출](https://urock-ailab.github.io/forensics-handbook/android/04-scenarios/exfiltration/data-exfiltration/) · [iOS 자료 유출](https://urock-ailab.github.io/forensics-handbook/ios/04-scenarios/exfiltration/data-exfiltration/)
- 클라우드: [AWS VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/aws/vpc-flow-logs.html) · [Azure 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/azure/flow-logs.html) · [GCP VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/gcp/vpc-flow-logs.html) · [클라우드 저장소에서 자료를 빼 갔나](https://urock-ailab.github.io/forensics-handbook/cloud/04-scenarios/data-leak/storage-exfiltration.html)

## 참고 문헌

1. Zeek Documentation, "conn.log". https://github.com/zeek/zeek-docs/blob/master/logs/conn.rst
2. Zeek Documentation, base/protocols/conn/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
3. Zeek Documentation, "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
4. Zeek Documentation, base/protocols/http/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/http/main.zeek.rst
5. Zeek Documentation, base/protocols/http/entities.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/http/entities.zeek.rst
6. Zeek Documentation, base/frameworks/files/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/frameworks/files/main.zeek.rst
7. Zeek Documentation, "files.log", "ftp.log". https://github.com/zeek/zeek-docs/blob/master/logs/files.rst , https://github.com/zeek/zeek-docs/blob/master/logs/ftp.rst
8. Zeek Documentation, base/protocols/ftp/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ftp/main.zeek.rst
9. Zeek Documentation, base/protocols/ftp/info.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ftp/info.zeek.rst
10. Zeek Documentation, base/protocols/smtp/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/smtp/main.zeek.rst
11. Zeek Documentation, base/protocols/smb/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/smb/main.zeek.rst
12. Zeek Documentation, base/protocols/ssl/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssl/main.zeek.rst
13. OISF Suricata User Guide, "Eve JSON Format". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
14. OISF Suricata User Guide, "Eve JSON Output". https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
15. Squid, src/cf.data.pre (`logformat`, `access_log`). https://github.com/squid-cache/squid/blob/master/src/cf.data.pre
16. nfdump, nfdump(1) 매뉴얼. https://github.com/phaag/nfdump/blob/master/man/nfdump.1
17. B. Claise, Ed., "Cisco Systems NetFlow Services Export Version 9", RFC 3954, 2004. https://www.rfc-editor.org/rfc/rfc3954.txt
18. Wireshark, tshark(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
19. Active Countermeasures RITA, default_config.hjson. https://github.com/activecm/rita/blob/main/default_config.hjson
20. Active Countermeasures RITA, README.md. https://github.com/activecm/rita/blob/main/README.md
21. SigmaHQ, proxy_ua_rclone.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/web/proxy_generic/proxy_ua_rclone.yml
22. SigmaHQ, zeek_http_webdav_put_request.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_webdav_put_request.yml
23. SigmaHQ, proxy_telegram_api.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/web/proxy_generic/proxy_telegram_api.yml
24. Jan-Niclas Hilgert, Axel Mahr, Martin Lambertz, "Mount SMB.pcap: Reconstructing file systems and file operations from network traffic", Forensic Science International: Digital Investigation 50, 301807, 2024. doi:10.1016/j.fsidi.2024.301807
