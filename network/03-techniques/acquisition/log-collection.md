---
title: "로그 수집과 보존"
parent: "기법 · 조사 절차·수집"
nav_order: 350
---

# 로그 수집과 보존 (Log Collection)

방화벽·프록시·DNS·DHCP·VPN 로그와 흐름 기록, Zeek·Suricata 로그는 대부분 크기나 주기를 정해 두고 오래된 것을 지우거나 덮어쓰기 때문에, 사고를 알아챈 뒤에도 남은 시간이 그리 길지 않습니다. 이 페이지에서는 출처별로 남은 시간을 확인하는 방법, 원본 파일과 순환된 파일과 설정 파일을 함께 받는 순서, syslog 로 모인 사본을 원본과 대조하는 방법, 로그마다 다른 시각 기준을 읽는 법을 다룹니다. 로그 종류별 필드 설명은 [네트워크 로그의 종류](../../01-foundations/records/log-types.md)와 장비별 페이지에 있습니다.

## 언제 쓰나

로그 보관(archival)은 두 가지입니다. 보유(retention)는 평소 운영 절차로 정해진 기간 동안 로그를 모아 두는 일이고, 보존(preservation)은 원래라면 버려질 로그를 관심 있는 활동이 들어 있다는 이유로 남기는 일입니다. 사고 대응과 조사에서 하는 일은 보존입니다[3]. 그래서 이 절차는 IDS 경보나 사용자 신고로 조사 대상 기간이 정해진 직후, 그 기간의 로그가 순환·덮어쓰기로 사라지기 전에 씁니다.

수집 순서를 정할 때는 가치, 휘발성, 드는 노력을 함께 따집니다. 로그 파일은 전원을 꺼도 남는 데이터지만 새 이벤트가 들어오면 덮어쓰이므로 휘발성 데이터처럼 다뤄야 할 때가 있습니다[1]. RFC 3227 의 휘발성 순서에서는 원격 로깅·모니터링 데이터가 디스크보다 뒤에 있지만[2], 순환 주기가 짧은 네트워크 장비 로그는 이 순서보다 앞당겨 받습니다. 전체 조사 흐름은 [조사 절차](investigation-process.md)에, 패킷을 직접 캡처하는 방법은 [패킷 캡처하기](packet-capture.md)에 있습니다.

로그를 증거로 쓸 가능성이 있으면 원본 로그 파일, 중앙 로그 서버에 모인 사본, 해석된 로그 데이터(SIEM 에 들어간 값 등)를 모두 받아 둡니다. 복사하거나 해석하는 과정에서 내용이 충실하게 옮겨졌는지 나중에 따질 수 있기 때문입니다[1][3]. 보안 이벤트 관리(SEM, SIEM) 제품은 정규화 과정에서 오류를 만들거나 데이터를 잃을 수 있지만 원래 출처는 바꾸지 않으므로, 원본 로그 사본으로 정확성을 확인할 수 있습니다[1].

## 절차

### 1. 출처 목록을 만들고 소유자를 확인한다

조사 기간에 해당 트래픽이 지났을 장비와 서버를 목록으로 정리합니다. 방화벽·라우터는 거부된 연결 시도의 날짜·시각, 출발지·목적지 IP, 프로토콜, 포트를 남기는 설정이 흔하고, VPN 같은 원격 접속 서버는 연결 출처와 인증 계정과 할당 IP 를, DHCP 서버는 IP 할당과 MAC 주소와 시각을 남깁니다[1]. 로그 종류별로 무엇이 남는지는 [네트워크 로그의 종류](../../01-foundations/records/log-types.md)에 정리되어 있습니다.

목록에는 각 출처를 누가 관리하는지도 적습니다. ISP 기록은 대개 법원 명령이 있어야 받을 수 있고, 일상 기록은 며칠 또는 몇 시간만 보관하는 경우가 많습니다[1]. 클라우드 흐름 기록은 [클라우드 VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/aws/vpc-flow-logs.html) 페이지를 따릅니다. 호스트에 남은 방화벽 로그는 [Windows 방화벽](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/windows-firewall-pfirewall-log.html)과 [Linux 방화벽](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/firewall.html) 페이지에 있습니다.

### 2. 출처마다 남은 시간을 확인한다

많은 로그에는 최대 크기가 있습니다. 예를 들어 최근 이벤트 10,000개나 100 MB 까지만 두도록 정하고, 한도에 이르면 오래된 데이터를 덮어쓰거나 기록을 아예 멈춥니다[3]. 로그 순환(rotation)은 파일을 닫고 새 파일을 여는 일로, 매시·매일·매주 같은 일정이나 파일 크기를 기준으로 일어납니다. 순환된 파일은 압축될 수 있고, 순환할 때 도는 스크립트가 일부 항목만 남기도록 걸러 낼 수도 있습니다[3]. 그래서 수집 전에 각 출처의 순환 설정을 먼저 읽고, 조사 기간의 로그가 아직 남아 있는지와 언제 사라지는지를 계산합니다.

| 출처 | 순환·삭제 설정 | 수집 전에 볼 것 |
|---|---|---|
| BIND `logging` 채널 | `file "경로" versions N size S suffix increment` 형식(`suffix` 는 `increment` 또는 `timestamp`). 크기 제한과 백업은 기본으로 없고 기존 파일에 이어 씁니다. `size` 만 있고 `versions` 가 없으면 한도에서 기록을 멈춥니다. `increment` 면 `.0` 이 `.1` 로 밀리는 식으로 이름이 바뀝니다[6] | `size` 만 설정된 채널은 한도 이후 기록이 없습니다. ISC 권장 예시는 대부분 채널 `versions 3 size 20m`, queries 채널 `versions 600 size 20m` 입니다[7] |
| Windows DHCP 감사 로그 | 기본 위치 `%windir%\System32\Dhcp`, 쉼표 구분 텍스트(Windows Server 2008 기준)[8] | ID `01`(로그 중지)과 `02`(디스크 공간 부족으로 일시 중지) 이벤트가 있으면 그 뒤로 기록 공백이 있습니다[8] |
| Squid | `logfile_rotate` 기본 10(확장자 0~9), `squid -k rotate` 로 순환. 0 이면 이름을 바꾸지 않고 닫았다 다시 엽니다. Squid 4 부터는 stdio 모듈 access.log 의 기본값일 뿐이고 `access_log ... rotate=N` 으로 따로 정할 수 있습니다[9] | 순환된 `access.log.0` ~ `.9` 까지 받습니다 |
| nfcapd(NetFlow·IPFIX 수집기) | 기본 300초마다 파일 순환(최소 2초), 이름 `nfcapd.YYYYMMddhhmm` 은 그 시각부터의 흐름. `-e` 면 순환 때마다 nfexpire 규칙(최대 보관 기간·최대 크기)으로 오래된 파일을 지웁니다[10] | `-e` 가 켜져 있는지, 지금 쓰는 중인 마지막 파일이 아직 닫히지 않았는지 확인합니다 |
| Zeek(ZeekControl 기본 구성) | 매시 순환, `YYYY-MM-DD` 디렉터리로 옮기고 gzip 으로 압축, 이름에 로그 종류와 시간 범위 포함. 명령줄에서 `zeek -i eth0` 처럼 바로 실행하면 해당하지 않습니다[12] | 압축된 날짜 디렉터리까지 받습니다 |
| Suricata | 대부분 출력은 logrotate 같은 외부 도구가 순환하고 SIGHUP 을 보냅니다. EVE 와 pcap-log 는 자체 시간 순환(`rotate-interval` 에 `minute`·`hour`·`day` 또는 `30s`·`30m` 같은 값)을 지원하지만 오래된 파일 삭제는 여전히 외부 도구가 합니다[13][14] | logrotate 설정의 `rotate` 개수를 확인합니다 |
| OpenBSD pflogd | pf 가 기록한 패킷을 `/var/log/pflog` 에 tcpdump(pcap) 형식으로 씁니다. SIGHUP 을 받으면 파일을 닫았다 다시 열어 newsyslog 가 순환합니다[16] | 기본 snaplen 160바이트는 IP·ICMP·TCP·UDP 헤더에는 충분하지만 다른 프로토콜 정보는 잘릴 수 있습니다[16] |
| Security Onion 전수 캡처(Stenographer) | `/nsm/pcap/` 에 쓰고, 여유 공간이 `DiskFreePercentage` 아래로 떨어지면 오래된 파일부터 지웁니다. 분산 구성에서 기본값 10 이 적당하고, Elasticsearch 와 함께 도는 구성은 21 이상을 권합니다[17] | 디렉터리 파일 수 제한(기본 30000)에 먼저 걸려 기간이 짧아질 수 있습니다[17] |

위 설정은 버전·배포판마다 다를 수 있어서, 표의 값은 출발점으로만 쓰고 실제 장비의 설정 파일로 확인합니다. AWS VPC 흐름 로그는 최대 집계 간격이 기본 10분(1분 선택 가능)이고 CloudWatch Logs 로 약 5분, S3 로 약 10분 뒤에 도착하며 더 늦을 수도 있으므로, 수집 직후에는 최근 구간이 비어 있을 수 있습니다[11].

### 3. 설정 파일과 시계 상태를 함께 받는다

로그 파일만 받으면 시각이 어느 시간대인지, 어떤 필드가 어떤 순서로 적혔는지 알 수 없는 경우가 많습니다. 그래서 로그를 만든 설정 파일을 함께 받습니다. BIND 는 `print-time` 설정에 따라 시각이 아예 없거나(기본 `no`), 현지 시각이거나(`yes`·`local`·`iso8601`), UTC 입니다(`iso8601-utc`)[6]. Squid 는 `logformat` 에 따라 epoch 초(`%ts`)로 적기도 하고 현지 시각(`%tl`)으로 적기도 합니다[9]. Suricata 의 EVE 출력은 `filetype` 이 `regular` 가 아니면 파일이 아니라 syslog·유닉스 소켓·Redis 로만 나가고, `threaded: on` 이면 스레드마다 `eve.7.json` 같은 파일로 나뉘어 모두 합쳐 봐야 합니다[14].

각 장비의 시스템 시계가 UTC 와 얼마나 차이 나는지도 수집할 때 기록합니다. 적어 두는 시각마다 UTC 인지 현지 시각인지 밝힙니다[2]. 시계가 틀린 장비의 로그로는 "A 가 B 보다 45초 먼저 일어났다" 고 보이지만 실제로는 A 가 B 보다 2분 뒤에 일어났을 수 있습니다[3]. Cisco 장비에 AAA 명령 기록이 켜져 있으면 수집 중에 NTP 서버 설정을 바꾼 것도 명령 로그에 남으므로, 조사자가 한 설정 변경은 시각과 함께 따로 적어 둡니다(아래 "함정과 한계" 참고).

### 4. 버퍼를 비우고 순환된 파일까지 복사한다

일부 데몬은 기록을 한동안 메모리에 두었다가 파일에 씁니다. pflogd 는 기본 60초(5~3600초로 조정)마다 버퍼를 디스크에 쓰고, SIGALRM 을 받으면 바로 씁니다[16]. Suricata EVE 는 `buffer-size` 가 0 이 아니면 데이터 일부가 아직 파일에 쓰이지 않았을 수 있습니다[14]. 복사 직전에 버퍼를 비우면 마지막 몇십 초가 빠지는 일을 줄일 수 있습니다.

복사할 때는 지금 쓰고 있는 파일, 순환된 파일(`.0`·`.1` 같은 번호 파일과 `.gz` 압축 파일), 중앙 서버의 사본, 설정 파일을 한 묶음으로 받습니다[1][3][6][9]. Suricata 는 SIGHUP 을 받으면 열린 로그를 모두 닫고 이어쓰기 모드로 다시 엽니다. 외부 도구가 이름을 바꿨으면 새 파일이 생기고 그렇지 않으면 같은 파일에 이어 씁니다[13]. 그래서 복사하는 동안 순환이 일어나면 파일 이름과 내용이 바뀔 수 있으므로, 복사를 마친 뒤 디렉터리 목록을 다시 받아 처음 목록과 비교합니다.

### 5. 해시를 계산하고 보관 연속성을 기록한다

받은 파일마다 메시지 다이제스트를 계산해 안전한 곳에 따로 보관합니다[3]. 2006년 무렵에는 MD5 와 SHA-1 을 가장 흔히 썼지만, 다이제스트를 만드는 운영체제나 프로그램이 지원하면 SHA-256 을 쓰는 것이 좋습니다[3]. 이 핸드북은 SHA-256 을 기준으로 적습니다. Security Onion 의 Cases 기능은 첨부 파일마다 SHA256·SHA1·MD5 를 자동으로 계산합니다[18].

```
sha256sum fw01_messages fw01_messages.1.gz named_queries.log.0 > hashes_20260314.txt
```
(만든 예시: 파일 이름은 지어낸 값입니다.)

보관 연속성(chain of custody) 기록에는 누가 언제 어디서 찾아서 수집했고, 누가 어느 기간 보관했으며 어떻게 저장했는지, 언제 어떤 방법으로 넘겼는지를 적습니다[2]. 수집 방법은 다른 사람이 그대로 되풀이할 수 있어야 합니다[2]. 해시와 보관 기록을 보고서로 옮기는 방법은 [네트워크 포렌식 보고서](../reporting/forensic-report.md)에 있습니다.

### 6. 중앙 수집본을 원본과 대조한다

syslog 는 받았다는 확인을 주고받지 않는 단방향 프로토콜이고, 같은 메시지를 여러 수집기로 보낼 수 있습니다[4]. RFC 5424 는 모든 구현이 TLS 전송(RFC 5425)을 지원해야 하고 UDP 전송(RFC 5426)도 지원하는 것이 좋다고 정하며, 운영에는 TLS 를 권합니다[4]. 그런데 대부분의 syslog 구현은 UDP 를 써서 메시지가 도착했는지와 순서를 보장하지 않고, 접근 제어가 없어 아무 호스트나 메시지를 보낼 수 있습니다[3]. 재전송(replay)을 알아낼 수단도 없어서, 기록해 둔 메시지를 시각만 고쳐 다시 보내도 수집기는 구분하지 못합니다[4].

그래서 중앙 서버의 사본만으로 결론을 내리지 않고, 가능하면 원래 장비에 남은 로컬 로그와 같은 기간을 비교합니다. 한쪽에만 있는 줄은 전송 중 유실, 크기 제한에 따른 잘림, 위조 가운데 하나일 가능성이 있습니다[3][4]. 크기 제한을 넘는 메시지는 버려지거나 잘릴 수 있고, 막힐 때는 심각도가 낮은 메시지부터 버리도록 권하므로 빠진 줄이 낮은 심각도에 몰려 있을 수 있습니다[4].

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| `sha256sum` 등 해시 도구 | 받은 파일마다 SHA-256 계산 |
| Security Onion Cases | 첨부 파일의 SHA256·SHA1·MD5 자동 계산[18] |
| `zcat` | Zeek 가 순환하며 gzip 으로 압축한 로그 읽기[12] |
| `tcpdump -r /var/log/pflog` | pflogd 가 pcap 형식으로 남긴 방화벽 로그 읽기[16] |
| `pflogd -x` | 기존 pflog 파일의 무결성만 확인하고 끝냅니다[16] |
| nfdump | nfcapd 파일 읽기. 사용법은 [흐름 기록 분석](../analysis/flow-analysis.md)에 있습니다 |

큰 캡처 파일을 나누고 합치는 도구(editcap·mergecap·capinfos)는 [큰 캡처 파일 다루기](large-captures.md)에서 다룹니다.

## 함정과 한계

**설정 때문에 처음부터 없는 기록.** BIND 는 `print-time` 기본값이 `no` 라서 시각이 없는 로그가 남을 수 있고, `size` 만 정하고 `versions` 를 정하지 않으면 한도 뒤로는 아무것도 쓰지 않습니다[6]. Windows DHCP 감사 로그의 `01`·`02` 이벤트 뒤에는 기록이 멈춘 구간이 있습니다[8]. AWS VPC 흐름 로그의 `log-status` 가 `SKIPDATA` 면 그 집계 간격에 일부 기록이 빠졌다는 뜻입니다[11].

**아직 파일에 없는 기록.** pflogd 는 기본 설정에서 최대 60초 분량을 버퍼에만 둘 수 있고[16], nfcapd 는 지금 순환 구간의 파일을 아직 닫지 않았을 수 있습니다[10].

**BSD syslog(RFC 3164) 형식의 시각.** RFC 3164 의 TIMESTAMP 는 `Mmm dd hh:mm:ss` 형식의 현지 시각이고 연도와 시간대가 없습니다. 날짜가 10 미만이면 `Aug  7` 처럼 공백 두 개를 넣어 씁니다[5]. 그래서 연말·연초에 걸친 로그는 연도를 추정해야 하고, 일광 절약 시간이 바뀌는 구간의 시각은 두 가지로 읽힐 수 있습니다. RFC 3164 메시지를 RFC 5424 형식으로 바꿀 때는 현재 연도를 넣고 relay 나 수집기의 시간대를 써도 된다고 정해져 있어서[4], 변환된 로그의 연도와 시간대는 원래 장비가 아니라 변환한 서버가 붙인 값일 수 있습니다.

**relay 가 붙인 시각과 호스트 이름.** RFC 3164 relay 는 받은 메시지에서 유효한 TIMESTAMP 를 찾지 못하면 자기 현지 시각으로 TIMESTAMP 를 붙이고, HOSTNAME 도 자기가 아는 장비 이름이나 IP 로 붙입니다[5]. 받는 쪽은 TIMESTAMP 의 시각이 맞는지, HOSTNAME 이 보낸 장비와 같은지 검증하지 않아도 됩니다[5].

**로그 내용 자체의 조작.** 루트킷 가운데는 설치·실행 흔적을 지우도록 로그를 고치는 것이 많습니다[3]. 텍스트 로그라도 공격자가 넣은 이진 데이터가 들어 있어 관리 도구가 잘못 처리할 수 있습니다[3]. 중앙 로깅은 권한 없는 사용자의 로그 조작을 막는 데 쓰입니다[1]. 방화벽 로그의 포트 순서에 정보를 숨겨 syslog 로 중앙 서버까지 전달하는 은닉 명령 제어(C2, Command and Control) 채널을 시연한 연구도 있습니다. 이 연구(UFW·OPNsense 두 방화벽으로 시험)가 제시한 지표는 같은 IP 의 연속 포트 스캔, ARP 캐시 오염, 흔하지 않은 클라이언트의 방화벽·syslog 로그 접근입니다[20]. 그래서 로그 서버 자체의 접근 기록도 수집 대상에 넣습니다.

**장비 명령 로그에 남은 삭제·변경.** Cisco 장비의 AAA 명령 기록이 있으면 SigmaHQ 규칙으로 로그 삭제와 설정 변경을 찾을 수 있습니다. `clear logging`·`clear archive`(Cisco Clear Logs), `no logging`·`no aaa new-model`(Cisco Disabling Logging), `erase`·`delete`·`format`(Cisco File Deletion), `ntp server`·`access-list`·`archive maximum` 등(Cisco Modify Configuration)이 규칙의 키워드입니다[19]. Clear Logs·File Deletion·Modify Configuration 규칙은 관리자의 정상 작업에도 걸리므로[19], 조사자가 수집 중에 입력한 명령은 시각과 함께 기록해 두어야 공격자의 행위와 구분할 수 있습니다.

## 결과를 어떻게 해석하나

### 시각 기준

같은 사건이라도 출처마다 시각을 적는 방식이 달라서, 합치기 전에 출처별 기준을 표로 정리합니다. 시각 기준 전반은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)에, 여러 출처를 한 줄로 합치는 방법은 [네트워크 타임라인](../analysis/timeline.md)에 있습니다.

| 출처 | 시각 형식 | 기준 |
|---|---|---|
| RFC 5424 syslog | RFC 3339 기반, `T` 필수, 소수 초 최대 6자리, 끝에 `Z` 또는 `±hh:mm`. 시스템 시각을 얻지 못하면 `-`[4] | 오프셋이 있어 UTC 로 바꿀 수 있습니다 |
| RFC 3164 syslog | `Mmm dd hh:mm:ss`[5] | 연도·시간대 없는 현지 시각 |
| BIND | `print-time` 설정에 따름[6] | 현지 시각 또는 UTC, 기본은 시각 없음 |
| Squid | `%ts.%03tu`(기본 `squid` 형식) 또는 `[%tl]`(`common` 형식)[9] | epoch 초 또는 현지 시각 |
| Zeek | `ts` 는 epoch 초[12] | `zeek-cut -d` 로 사람이 읽는 시각으로 바꿔 봅니다[12] |
| Suricata EVE | `2023-09-18T06:13:41.532140+0000` 처럼 끝에 UTC 오프셋이 붙은 `timestamp`[15] | 오프셋이 `+0000` 만 오지 않고 `+0100`·`-0800` 같은 값도 올 수 있어 UTC 로 바꿔 맞춥니다[15] |
| AWS VPC 흐름 로그 | `start`·`end` 가 Unix 초[11] | 집계 간격 안에서 흐름의 첫 패킷·마지막 패킷을 받은 시각이고, 실제 송수신 시각과 최대 60초 차이 날 수 있습니다[11] |

RFC 5424 메시지는 구조화 데이터 `timeQuality` 로 자기 시계 상태를 알릴 수 있습니다. `tzKnown` 은 시간대를 아는지(1/0), `isSynced` 는 NTP 같은 외부 시각과 맞추고 있는지(1/0), `syncAccuracy` 는 시계가 벗어날 수 있는 최대 폭을 마이크로초로 적은 값입니다[4]. `syncAccuracy="60000000"` 이면 60초 이내로 맞는다는 뜻이고, `[timeQuality tzKnown="0" isSynced="0"]` 이면 보낸 장비가 자기 시각을 믿을 수 없다고 밝힌 것이라 수집기가 받은 시각으로 상관 분석하라는 힌트가 될 수 있습니다[4].

```
<134>1 2026-03-14T02:15:07.412Z fw01.example.com fwlog 2210 - [timeQuality tzKnown="1" isSynced="1"] deny tcp 203.0.113.50:51422 -> 10.0.0.8:3389
<134>Mar 14 11:15:07 fw01 fwlog[2210]: deny tcp 203.0.113.50:51422 -> 10.0.0.8:3389
```
(만든 예시: 같은 이벤트를 RFC 5424 형식과 RFC 3164 형식으로 쓴 것입니다. 첫 줄은 UTC 이고, 둘째 줄은 UTC+9 장비의 현지 시각이라 줄만 보고는 연도와 시간대를 알 수 없습니다.)

### 증명하는 것

수집한 로그는 그 장비가 그 설정으로 조사 기간에 이런 이벤트를 기록했다는 것을 보여 줍니다. 해시와 보관 연속성 기록이 있으면 수집한 뒤로 파일이 바뀌지 않았다는 것도 보여 줍니다[2][3]. 보고서에는 "이 시간대(UTC 기준)에 fw01 이 203.0.113.50 에서 10.0.0.8 의 3389 포트로 가는 연결을 거부한 기록이 원본 로그와 중앙 사본에 모두 있다" 처럼 기록으로 확인되는 범위만 씁니다.

### 증명하지 못하는 것

로그에 없다는 것만으로 이벤트가 없었다고 할 수 없습니다. UDP 전송 중 유실, 크기 한도에 따른 기록 중지나 덮어쓰기, `SKIPDATA` 같은 수집 누락, 꺼져 있던 로깅이 모두 빈 구간을 만듭니다[3][4][8][11]. 로그의 시각이 정확하다는 것도 증명하지 못합니다. 시각은 원래 장비의 시계를 따르고, syslog 는 재전송된 메시지의 시각이 고쳐졌는지 알 수 없습니다[3][4]. HOSTNAME 필드에 적힌 장비가 실제로 그 메시지를 보냈다는 것도 증명하지 못합니다. 받는 쪽은 HOSTNAME 을 검증하지 않아도 되고, 대부분의 syslog 구현은 아무 호스트의 메시지나 받습니다[3][5]. IP 주소로 기기나 사람을 특정하는 방법은 [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md)과 [DHCP 로그](../../02-artifacts/devices/dhcp-logs.md)에서 다룹니다.

## 참고 문헌

1. Karen Kent, Suzanne Chevalier, Tim Grance, Hung Dang, "Guide to Integrating Forensic Techniques into Incident Response", NIST SP 800-86, 2006-08. https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
2. D. Brezinski, T. Killalea, "Guidelines for Evidence Collection and Archiving", RFC 3227 (BCP 55), 2002-02. https://www.rfc-editor.org/rfc/rfc3227.txt
3. Karen Kent, Murugiah Souppaya, "Guide to Computer Security Log Management", NIST SP 800-92, 2006-09. https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-92.pdf
4. R. Gerhards, "The Syslog Protocol", RFC 5424, 2009-03. https://www.rfc-editor.org/rfc/rfc5424.txt
5. C. Lonvick, "The BSD syslog Protocol", RFC 3164, 2001-08. https://www.rfc-editor.org/rfc/rfc3164.txt
6. BIND 9 Administrator Reference Manual, Configuration Reference (logging). https://bind9.readthedocs.io/en/stable/reference.html
7. ISC Knowledgebase, BIND Logging - some basic recommendations. https://kb.isc.org/docs/aa-01526
8. Microsoft, Analyze DHCP Server Log Files (Windows Server 2008). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/dd183591(v=ws.10)
9. Squid, 설정 지시어 설명(cf.data.pre: logformat, logfile_rotate). https://github.com/squid-cache/squid/blob/master/src/cf.data.pre
10. nfdump, nfcapd 매뉴얼. https://github.com/phaag/nfdump/blob/master/man/nfcapd.1
11. AWS, Amazon VPC User Guide, Flow log records. https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html
12. Zeek 문서, Zeek Log Formats and Inspection. https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
13. Suricata User Guide, Log Rotation. https://github.com/OISF/suricata/blob/main/doc/userguide/output/log-rotation.rst
14. Suricata User Guide, EVE JSON Output. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
15. Suricata User Guide, EVE JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
16. OpenBSD, pflogd(8) 매뉴얼. https://man.openbsd.org/pflogd.8
17. Security Onion 문서, Stenographer. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/stenographer.rst
18. Security Onion 문서, Cases. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/cases.rst
19. SigmaHQ, Cisco AAA 규칙(cisco_cli_clear_logs, cisco_cli_disable_logging, cisco_cli_file_deletion, cisco_cli_modify_config). https://github.com/SigmaHQ/sigma/tree/master/rules/network/cisco/aaa
20. Kevin Lamshöft, Tom Neubert, Jonas Hielscher, Claus Vielhauer, Jana Dittmann, "Knock, knock, log: Threat analysis, detection & mitigation of covert channels in syslog using port scans as cover", Forensic Science International: Digital Investigation 40, 301335, 2022. doi:10.1016/j.fsidi.2022.301335
