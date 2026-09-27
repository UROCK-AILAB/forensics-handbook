---
title: "방화벽 로그"
parent: "아티팩트 · 네트워크 장비와 서버 로그"
nav_order: 250
---

# 방화벽 로그 (iptables·nftables·pf)

Linux 방화벽(iptables·nftables)과 OpenBSD pf 는 규칙에 맞은 패킷의 헤더를 로그로 남깁니다. Linux 는 패킷 하나를 `SRC=… DST=… DPT=…` 같은 텍스트 한 줄로 커널 로그에 쓰고, pf 는 패킷 앞부분을 pcap 파일에 담습니다. 이 페이지는 두 기록의 필드와 모양, 기록이 남는 조건과 빠지는 조건, 한 줄로 주장할 수 있는 범위를 다룹니다. syslog 시각 형식은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에서, NAT 주소 해석은 [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md) 에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

방화벽은 관리자가 로그 규칙을 넣은 곳에서만 기록합니다. 모든 패킷을 저절로 남기지 않으므로, 로그가 있는지와 무엇이 남는지는 규칙 집합이 정합니다.

iptables 의 `LOG` 타깃은 규칙에 맞은 패킷의 IP·IPv6 헤더 필드 대부분을 커널 로그로 보내고, 이 로그는 `dmesg` 나 syslog 에서 읽습니다[1]. `LOG` 는 비종료 타깃 (non-terminating target) 이라서 기록한 뒤 다음 규칙으로 넘어갑니다. 그래서 버린 패킷을 남기려면 같은 조건의 규칙 두 개를 두고, 앞 규칙은 `LOG`, 뒤 규칙은 `DROP` 이나 `REJECT` 로 씁니다[1]. nftables 의 `log` 문도 비종료 문이라 기록 뒤에 규칙 평가가 이어집니다[2].

pf 는 규칙에 `log` 를 달면 그 규칙의 동작(pass·block)과 별도로 패킷을 기록합니다. 기본으로는 상태 (state) 를 만드는 패킷 하나만 기록하고, `no state` 규칙이면 맞는 패킷마다 기록합니다[5]. 기록한 패킷은 pflog 인터페이스(기본 `pflog0`)로 가고, pflogd 가 이것을 `/var/log/pflog` 에 pcap 형식으로 저장합니다[5][7].

## 위치와 버전별 차이

| 방화벽 | 로그 규칙 | 보내는 곳 | 파일로 남는 곳 |
|---|---|---|---|
| iptables | `-j LOG` | 커널 로그 | syslog 데몬이 쓰는 파일, journald 저널[1][14] |
| iptables | `-j NFLOG` | nfnetlink_log 를 거쳐 netlink 멀티캐스트 그룹 | 그룹을 받는 사용자 공간 프로그램이 정한 곳[1] |
| iptables | `-j AUDIT` | 감사 (audit) 레코드 | auditd 가 쓰는 곳[1] |
| nftables | `log [prefix …] [level …] [flags …]` | 커널 로그 | syslog 데몬이 쓰는 파일, journald 저널[2][14] |
| nftables | `log group N …` | nfnetlink_log | ulogd 같은 수집 프로그램이 정한 곳[2] |
| nftables | `log level audit` | 감사 버퍼 | auditd 가 쓰는 곳. 이 형식에는 prefix·flags 를 못 씁니다[2] |
| pf | `log`, `log (all)` 등 | pflog 인터페이스 | pflogd 가 쓰는 `/var/log/pflog`(pcap)[5][7] |

NFLOG 소켓 로그 메시지를 담은 pcap 파일은 링크 타입이 `LINKTYPE_NFLOG`(239)이고, pflog 파일의 링크 타입은 `LINKTYPE_PFLOG`(117)입니다[9]. 링크 타입을 읽는 법은 [pcap 형식](../../01-foundations/capture/pcap.md) 에 있습니다.

배포판 프런트엔드는 결국 위 규칙을 만들어 넣습니다. 확인할 설정은 다음과 같습니다.

- **ufw**: `ufw logging on` 은 로그 수준 `low` 로 켭니다. `low` 는 정책에 맞지 않아 막힌 패킷(속도 제한 있음)과 log 규칙에 맞은 패킷을, `medium` 은 여기에 정책에 맞지 않는 허용 패킷·INVALID 패킷·새 연결을 더해 기록하며, 둘 다 속도 제한이 붙습니다. `high` 는 `medium` 을 속도 제한 없이 기록하고 나머지 모든 패킷을 속도 제한을 붙여 기록하며, `full` 은 `high` 에서 속도 제한을 뺍니다. 기록은 syslog 의 LOG_KERN 시설로 가고, rsyslog 를 쓰는 시스템은 `/var/log/ufw.log` 에도 남길 수 있습니다[10]. 로그 체인 이름은 `ufw-logging-deny`, `ufw-logging-allow`(IPv6 는 `ufw6-…`)입니다[17].
- **firewalld**: `/etc/firewalld/firewalld.conf` 의 `LogDenied` 가 `all`·`unicast`·`broadcast`·`multicast`·`off` 중 하나이고 기본값은 `off` 입니다. 켜면 INPUT·FORWARD·OUTPUT 체인 기본 규칙의 reject·drop 규칙과 존의 마지막 reject·drop 규칙 바로 앞에 로깅 규칙이 들어갑니다. `FirewallBackend` 기본값은 nftables 입니다[11].

ufw 의 기본 기록 범위는 출처마다 다르게 적혀 있습니다. ufw 매뉴얼은 기본 로그 수준을 `low` 로 적고, 로깅이 꺼져 있을 때 `on` 을 주면 `low` 로 켠다고 적었습니다[10]. Lamshöft 외(2022)는 UFW 가 기본으로 아무 활동도 기록하지 않는다고 적었습니다[18]. 실제 설정은 `ufw status verbose` 로 확인합니다[10].

버전에 따라 달라지는 점도 있습니다. Linux 4.12 부터 iptables `AUDIT --type` 은 감사 메시지에 영향을 주지 않고 호환용으로 받기만 합니다[1]. `TRACE` 타깃은 iptables-legacy 에서는 로깅 백엔드(ip(6)t_LOG 나 nfnetlink_log)를 거쳐 `TRACE: tablename:chainname:type:rulenum` 접두어로 기록됩니다. iptables-nft 에서는 nftables 의 `meta nftrace` 로 바뀌어 netlink 이벤트로 사용자 공간에 전달되고, `xtables-monitor --trace` 로 봅니다[1]. nftables 는 `nft monitor trace` 로 봅니다[2].

## 구조

### netfilter LOG 한 줄

커널이 만드는 부분은 다음 순서로 이어집니다[3].

1. 규칙의 접두어 (prefix) 와 `IN=` 들어온 장치, `OUT=` 나갈 장치. 해당 장치가 없으면 `OUT=` 처럼 값이 빈 채로 찍힙니다. 브리지를 지나면 `PHYSIN=`·`PHYSOUT=` 이 붙습니다.
2. 들어온 패킷(`IN=` 에 값이 있을 때)만 MAC 부분. `MAC=` 뒤에 링크 계층 헤더 바이트를 콜론으로 이어 찍습니다. MAC 해석 플래그를 켰고 이더넷이면 대신 `MACSRC= MACDST= MACPROTO=` 를 찍고, VLAN 이면 `VPROTO= VID=` 가 들어갑니다.
3. IPv4 헤더: `SRC= DST= LEN= TOS= PREC= TTL= ID=` 뒤에 켜진 플래그 `CE`·`DF`·`MF`, 조각 오프셋이 0 이 아니면 `FRAG:`, IP 옵션 플래그를 켰으면 `OPT (…)`.
4. 전송 계층: 아래 표.
5. UID 플래그를 켰고 이 호스트의 소켓이 보낸·받은 패킷이면 `UID= GID=`, 패킷 표시 (mark) 가 0 이 아니면 `MARK=0x…`.

IPv6 는 3번 자리에 `SRC= DST= LEN= TC= HOPLIMIT= FLOWLBL=` 과 확장 헤더가, ARP 는 `ARP HTYPE= PTYPE= OPCODE=` 와 `MACSRC= IPSRC= MACDST= IPDST=` 가 찍힙니다. 헤더가 덜 들어온 패킷은 `INCOMPLETE [n bytes]` 나 `TRUNCATED` 로 끝납니다[3].

| 프로토콜 | 찍히는 필드[3] |
|---|---|
| TCP | `PROTO=TCP SPT= DPT=`, (SEQ 플래그) `SEQ= ACK=`, `WINDOW= RES=0x..`, 켜진 TCP 플래그 이름(`AE CWR ECE URG ACK PSH RST SYN FIN` 순), `URGP=`, (TCP 옵션 플래그) `OPT (16진수)` |
| UDP | `PROTO=UDP SPT= DPT= LEN=` (UDP-Lite 는 `PROTO=UDPLITE`) |
| ICMP | `PROTO=ICMP TYPE= CODE=`, 종류에 따라 `ID= SEQ=`·`PARAMETER=`·`GATEWAY=`·`MTU=`. 오류 메시지는 담긴 원래 패킷을 `[ … ]` 안에 한 번 더 찍음 |
| ICMPv6 | `PROTO=ICMPv6 TYPE= CODE=` |
| AH·ESP | `PROTO=AH SPI=0x..`, `PROTO=ESP SPI=0x..` |
| 그 밖 | `PROTO=번호` |

로그에 무엇이 더 붙는지는 규칙에 준 옵션으로 정해집니다.

| iptables `LOG` 옵션[1] | nftables `log flags`[2] | 늘어나는 필드 |
|---|---|---|
| `--log-tcp-sequence` | `tcp sequence` | `SEQ= ACK=` |
| `--log-tcp-options` | `tcp options` | TCP `OPT (…)` |
| `--log-ip-options` | `ip options` | IP `OPT (…)` |
| `--log-uid` | `skuid` | `UID= GID=` |
| `--log-macdecode` | `ether` | `MACSRC= MACDST= MACPROTO=` |
| — | `all` | 위 전부 |

iptables `--log-prefix` 는 29자까지, `NFLOG --nflog-prefix` 는 64자까지 받습니다[1]. `--log-level` 은 emerg·alert·crit·error·warning·notice·info·debug 중 하나이고, nftables `level` 은 emerg·alert·crit·err·warn·notice·info·debug·audit 중 하나이며 기본값은 warn 입니다[1][2]. 규칙이 로그 정보를 넘기지 않을 때 커널이 쓰는 기본 수준은 notice 입니다[3].

아래는 접두어를 `DROP-IN ` 으로 준 규칙에 SSH 연결 요청이 걸린 줄입니다(만든 예시). 앞의 시각·호스트 이름·`kernel:` 은 syslog 데몬이 붙인 부분이고, 수집기 설정에 따라 모양이 다릅니다.

```text
Sep 27 10:15:02 fw01 kernel: DROP-IN IN=eth0 OUT= MAC=02:00:00:00:00:01:02:00:00:00:00:02:08:00 SRC=198.51.100.23 DST=192.0.2.10 LEN=60 TOS=0x00 PREC=0x00 TTL=52 ID=31337 DF PROTO=TCP SPT=51514 DPT=22 WINDOW=64240 RES=0x00 SYN URGP=0
```

커널이 만드는 부분에는 시각이 없습니다[3]. 판정도 없어서, `DROP-IN` 은 관리자가 지은 문자열일 뿐 커널이 붙인 결과가 아닙니다.

### pflog 레코드

pflog 파일은 텍스트가 아니라 pcap 이고, 패킷마다 pflog 헤더 뒤에 원래 패킷의 앞부분이 붙습니다. 이 헤더에는 주소 체계, 인터페이스 이름, 규칙 번호, 이유 (reason), 동작 (action), 방향이 들어 있습니다[6]. 헤더 구조체 `struct pfloghdr` 의 필드는 `length`, `af`, `action`, `reason`, `ifname`, `ruleset`, `rulenr`, `subrulenr`, `uid`, `pid`, `rule_uid`, `rule_pid`, `dir`, `rewritten`, `naf`, `pad`, `saddr`, `daddr`, `sport`, `dport` 입니다[6].

이유 값은 `match`, `bad-offset`, `fragment`, `short`, `normalize`, `memory`, `bad-timestamp`, `congestion`, `ip-option`, `proto-cksum`, `state-mismatch`, `state-insert`, `state-limit`, `src-limit`, `synproxy` 이고[7], 운영체제별로 `map-failed`(FreeBSD), `state-locked`(NetBSD), `translate`·`no-route`(OpenBSD), `dummynet`(macOS)이 더 있습니다[8]. 규칙에 맞아 기록된 패킷은 `match` 입니다.

pf 의 `log` 에는 옵션이 붙습니다. `log (all)` 은 연결의 모든 패킷, `log (matches)` 는 이후에 맞는 모든 규칙에서 기록하고, `log (user)` 는 이 호스트 소켓의 UID·PID 를 더하며, `log (to pflogN)` 은 다른 pflog 인터페이스로 보냅니다[5]. `match` 규칙의 `log` 는 규칙에 맞을 때마다 동작해서 패킷 하나가 여러 번 기록될 수 있습니다[5].

## 증거로서 의미

### 증명하는 것

- 기록된 시각 무렵 그 인터페이스(`IN=`·`OUT=`)에서, 로그에 찍힌 출발지·목적지 주소와 포트, 프로토콜, TCP 플래그로 된 패킷이 로그 규칙에 맞았다는 사실[3].
- 들어온 패킷이면 바로 앞 링크 구간의 MAC 주소(`MAC=`), 플래그를 켰으면 이 호스트에서 패킷을 주고받은 소켓의 UID·GID[3].
- pf 는 한 레코드로 동작(pass·block), 이유, 규칙 번호, 방향까지 확인됩니다[6].

### 증명하지 못하는 것

- iptables `LOG`·nftables `log` 한 줄만으로는 그 패킷이 버려졌는지 통과했는지 알 수 없습니다. 비종료 타깃이라 판정은 그다음 규칙이 합니다[1][2]. 판정은 `iptables-save` 나 `nft list ruleset` 으로 로그 규칙 뒤에 무엇이 오는지 보고 판단합니다.
- 연결이 맺어졌는지 알 수 없습니다. SYN 하나만 기록됐을 수 있고, pf 는 기본으로 상태를 만든 첫 패킷만 기록합니다[5].
- 주고받은 양과 내용은 없습니다. 로그는 패킷 하나 단위이고 연결 합계를 쓰지 않습니다. pflog 는 기본으로 패킷마다 앞 160바이트만 저장합니다[7].
- 어느 사용자·프로세스가 보냈는지는 UID 플래그를 켰고 이 호스트의 소켓일 때만 UID 로 남습니다[3]. 이 호스트를 지나가는(FORWARD) 패킷에는 없습니다.
- NAT 뒤의 실제 내부 주소. 로그 줄은 규칙을 지나는 그 순간의 헤더만 찍고 변환 전후를 짝지어 남기지 않습니다[3].
- 기록이 없다고 트래픽이 없었던 것은 아닙니다. 아래 [함정과 한계](#함정과-한계) 의 조건에서는 트래픽이 있어도 줄이 생기지 않습니다.

보고서에는 "10:15:02 무렵 198.51.100.23:51514 에서 192.0.2.10:22 로 가는 SYN 패킷이 `DROP-IN` 접두어 규칙에 기록됐고, 그 규칙 바로 뒤에 같은 조건의 DROP 규칙이 있다" 처럼 로그와 규칙 집합으로 확인되는 만큼만 씁니다(만든 예시).

## 시각 해석

netfilter 로그 줄 내용에는 시각이 없습니다[3]. `dmesg` 는 커널 로그 버퍼에 메시지마다 붙은 부팅 뒤 경과 시간을 보여 주고[13], 줄 앞의 날짜와 시각은 syslog 데몬이 붙입니다[19]. syslog 데몬이 RFC 3164 형식으로 쓰면 시각은 `Mmm dd hh:mm:ss` 형식의 현지 시각이고 연도와 시간대가 없습니다. 날짜가 한 자리이면 `Sep  7` 처럼 공백이 두 개 들어갑니다[19]. 원격 syslog 서버에 모인 로그라면 장비 시각과 수집 서버 시각이 다를 수 있습니다. 여러 기록의 시각을 맞추는 방법은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에 있습니다.

`journalctl` 은 `--utc` 를 주면 시각을 UTC 로, `-o short-iso-precise` 를 주면 마이크로초까지 보여 줍니다[14]. `dmesg` 의 기본 시각은 부팅 뒤 흐른 초이고, `-T` 와 `--time-format iso` 로 바꾼 사람용 시각은 절전 (suspend) 후 재개 (resume) 뒤에 틀릴 수 있습니다. 마지막 재개 뒤의 메시지만 맞게 바뀝니다[13].

pflog 파일의 시각은 pcap 레코드 시각이라 1970-01-01 00:00:00 UTC 부터 흐른 초로 저장됩니다. pflogd 는 버퍼를 기본 60초마다 파일에 쓰므로 파일 수정 시각은 레코드 시각보다 늦을 수 있습니다[7]. pcap 시각 필드는 [pcap 형식](../../01-foundations/capture/pcap.md) 에서 다룹니다.

conntrack 연결 추적 표의 커널 시각(`-o ktimestamp`)은 `net.netfilter.nf_conntrack_timestamp` 를 켰을 때만 있습니다[12].

## 함정과 한계

**규칙 순서.** 앞선 ACCEPT·DROP 규칙에 먼저 맞은 패킷은 LOG 규칙까지 오지 않습니다. 로그를 해석하기 전에 수집 당시의 규칙 집합(`iptables-save`, `nft -a list ruleset`)을 함께 확보합니다[2]. nftables 의 `-a` 는 규칙 핸들을, `-j` 는 JSON 출력을 보여 줍니다[2].

**속도 제한.** `limit` 매치는 토큰 버킷으로 동작하고 기본값이 `--limit 3/hour`, `--limit-burst 5` 입니다. LOG 와 함께 써서 기록량을 줄이는 데 쓰는데[1], 한도를 넘은 패킷은 LOG 규칙에 맞지 않아 줄이 생기지 않습니다. ufw 의 `low`·`medium` 도 속도 제한이 붙습니다[10]. 스캔이나 무작위 대입처럼 짧은 시간에 몰린 패킷은 로그 줄 수가 실제 패킷 수보다 훨씬 적을 수 있습니다.

**컨테이너 네임스페이스.** 커널은 기본으로 호스트 네트워크 네임스페이스(init_net)의 LOG 만 커널 로그에 씁니다. 컨테이너가 호스트 커널 로그를 채우지 못하게 하려는 설정이고, `net.netfilter.nf_log_all_netns`(기본 0)를 켜야 다른 네임스페이스에서도 기록합니다[4][3]. 기본값에서는 컨테이너 안 규칙의 LOG 가 아무 흔적도 남기지 않습니다.

**MAC 필드 순서.** `MAC=` 는 링크 계층 헤더 원본 순서라 이더넷이면 목적지 MAC, 출발지 MAC, EtherType 순입니다. 첫 6바이트를 출발지로 읽으면 틀립니다. 반대로 `--log-macdecode` 형식은 `MACSRC=` 가 먼저입니다[3]. 나가는 패킷 줄에는 MAC 부분이 아예 없습니다[3].

**TCP 순서 번호.** 기본 옵션에서는 `SEQ=`·`ACK=` 가 찍히지 않습니다[3]. `--log-tcp-sequence` 는 로그를 일반 사용자가 읽을 수 있으면 보안 위험이 되는 옵션입니다[1].

**`journalctl -k` 의 범위.** `-k` 는 `--boot=0` 을 함께 뜻해서 현재 부팅의 커널 메시지만 보여 줍니다. 이전 부팅은 `-b` 로 지정하고, 다른 기계에서 가져온 저널은 `-D` 로 디렉터리를 줍니다[14].

**pflog 의 잘림과 flush.** pflogd 기본 snaplen 은 160바이트라서 IP·ICMP·TCP·UDP 헤더에는 충분하지만 그 밖 프로토콜 정보와 페이로드는 잘립니다[7]. 버퍼를 60초(5–3600초로 조정)마다 쓰므로, 장비가 갑자기 꺼지면 마지막 1분 안팎의 기록이 파일에 없을 가능성이 있습니다[7]. pflogd 는 재시작 뒤 기존 파일에 이어 쓰기 전에 파일을 검사하고, 파일이 잘못됐거나 입출력 오류가 나면 SIGHUP·SIGALRM 을 받을 때까지 기록을 멈춥니다[7]. 그 사이 구간은 빠집니다.

**지우기와 조작.** `iptables`·`ip6tables` 를 `-F`·`-Z`·`-X` 옵션과 함께 `ufw-logging-deny`·`ufw-logging-allow`(IPv6 는 `ufw6-…`) 체인 대상으로 실행하면 프로세스 실행 기록에 남을 수 있고, Sigma 규칙 `proc_creation_lnx_iptables_flush_ufw` 가 이를 탐지합니다[17]. 로그 규칙이 언제 사라졌는지는 Linux 호스트의 방화벽 설정 흔적과 함께 봅니다([linux] [방화벽](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/firewall.html)).

**로그가 은닉 채널로 쓰인 경우.** 포트 스캔이 남기는 방화벽 syslog 줄로 정보를 몰래 내보낼 수 있습니다. nmap 기본 스캔은 1,000개 포트를 무작위 순서로 두드리는데, 늘 먼저 나오는 앞 28개를 뺀 972개 포트의 순서를 골라 목적지 포트 번호의 홀짝으로 비트를 하나씩 숨깁니다. 그래서 줄 하나하나는 흔한 스캔 기록처럼 보입니다[18]. Lamshöft 외(2022)가 이 신호를 심층 합성곱 신경망으로 탐지한 시험에서는 학습 데이터 정확도가 약 92%, 시험 데이터 정확도가 약 61%(참 양성률 63%, 참 음성률 53%)였습니다[18].

**SIEM 필드 이름.** Sigma 의 firewall 범주 규칙은 `src_ip`, `dst_ip`, `dst_port`, `action`, `blocked` 같은 필드를 씁니다[15][16]. netfilter 로그 원문에는 이 이름이 없고(`SRC=`, `DST=`, `DPT=`), SIEM 이 파싱해 이름을 바꾼 뒤에야 규칙이 맞습니다. 모든 방화벽이 `action` 을 채우지는 않고 `blocked` 로 표시하기도 합니다[15].

## 직접 분석해 보기

### 헥스로 한 번

`MAC=` 필드는 링크 계층 헤더 바이트를 그대로 찍은 것이라 직접 풀 수 있습니다. 위 예시 줄의 값을 이더넷 헤더 순서로 나누면 다음과 같습니다(만든 예시).

```text
MAC=02:00:00:00:00:01:02:00:00:00:00:02:08:00
    |---- 목적지 ----| |---- 출발지 ----| |EtherType|
    02:00:00:00:00:01  02:00:00:00:00:02  08:00
```

EtherType `08:00` 은 IPv4 이고, 출발지 MAC `02:00:00:00:00:02` 는 이 방화벽에 패킷을 마지막으로 넘긴 장비의 주소입니다. 다른 네트워크에서 라우터를 거쳐 온 패킷이면 이 MAC 은 원래 보낸 호스트가 아니라 그 라우터의 주소입니다.

pflog 파일은 pcap 파일 헤더부터 읽습니다. 아래 24바이트는 pflogd 기본값(snaplen 160)과 pflog 링크 타입으로 만든 파일 헤더 예시이고, 리틀 엔디언·마이크로초 단위를 가정했습니다(명세로 만든 예시).

```text
오프셋  바이트
0000    D4 C3 B2 A1 02 00 04 00 00 00 00 00 00 00 00 00
0010    A0 00 00 00 75 00 00 00
```

- 0x00 `D4 C3 B2 A1`: pcap 매직 번호. 리틀 엔디언, 마이크로초입니다.
- 0x10 `A0 00 00 00`: SnapLen 0xA0 = 160바이트. pflogd `-s` 기본값과 같습니다[7].
- 0x14 `75 00 00 00`: LinkType 0x75 = 117 = `LINKTYPE_PFLOG` 입니다[9].

SnapLen 이 160이 아니면 파일을 처음 만들 때 pflogd 를 `-s` 로 바꿔 띄웠을 가능성이 있습니다. 기존 파일에 이어 쓸 때 pflogd 는 그 파일의 snaplen 을 그대로 씁니다[7]. 각 필드의 오프셋은 [pcap 형식](../../01-foundations/capture/pcap.md) 에 있습니다.

### 공개 도구로 한 번

Linux 커널 로그에서 방화벽 줄만 뽑을 때는 접두어나 `SRC=` 로 거릅니다. 수집한 저널은 다음처럼 UTC 로 읽습니다[14].

```sh
journalctl -D ./journal -k -b -1 -o short-iso-precise --utc | grep 'DROP-IN'
```

`key=value` 형식이라 `awk` 로 필드를 나누기 쉽습니다. 예를 들어 `grep -o 'SRC=[^ ]*' | sort | uniq -c | sort -rn` 으로 출발지별 줄 수를 셉니다. 규칙 집합은 `iptables-save` 와 `nft -a list ruleset` 으로, 변환 전후 주소는 conntrack 연결 추적 표로 확인합니다. `conntrack -L` 은 현재 표를, `conntrack -E` 는 실시간 이벤트를 보여 주고, original·reply 두 방향 주소로 NAT 전후를 확인할 수 있습니다(`--orig-src`, `--reply-src`)[12].

pflog 는 tcpdump 로 읽습니다[7].

```sh
tcpdump -n -e -ttt -r /var/log/pflog
tcpdump -n -e -ttt -r /var/log/pflog 'inbound and action block and on em0'
pflogd -x -f /var/log/pflog
```

`-e` 는 줄마다 링크 계층 헤더를 찍는 옵션이라[20], pflog 파일에서는 pflog 헤더 내용이 함께 나옵니다. 필터에는 pflog 전용 조건 `ifname`(`on`), `rnr`(`rulenum`), `srnr`(`subrulenum`), `rset`(`ruleset`), `reason`, `action` 을 쓰고, 방향은 `inbound`·`outbound` 로 거릅니다[8]. `pflogd -x` 는 기존 로그 파일의 무결성만 검사하고 끝납니다[7]. pflog 파일도 pcap 이라서 Wireshark 로 여는 방법은 [Wireshark·tshark로 읽기](../../03-techniques/analysis/wireshark.md) 와 같고, 먼저 링크 타입이 117 인지 확인합니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [연결 기록 (conn.log)](../zeek/zeek-logs/conn-log.md) | 방화벽이 기록한 SYN 뒤에 연결이 실제로 맺어졌는지(`conn_state`·`history`), 주고받은 바이트 |
| [흐름 기록 (NetFlow·IPFIX·sFlow)](../../01-foundations/records/flow-records.md) | 같은 주소·포트 쌍의 흐름과 양 |
| [Suricata EVE 로그](../suricata/eve-json/index.md) | 같은 시각의 탐지 경보 |
| [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md) | NAT 뒤 내부 주소. conntrack 이나 장비 NAT 기록 |
| [DHCP 로그](dhcp-logs.md) | 로그의 내부 IP 를 그 시각에 쓰던 기기 |
| [웹 프록시 로그 (Squid)](proxy-logs.md) | 프록시를 거친 연결이면 방화벽에는 프록시 주소만 남음 |
| [linux] [방화벽 (iptables·nftables·ufw·firewalld)](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/network/firewall.html) | 규칙 파일, 설정 변경 시각 |
| [windows] [윈도 방화벽 (pfirewall.log)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/windows-firewall-pfirewall-log.html) | 같은 연결을 Windows 호스트 방화벽이 남긴 기록 |
| [mac] [방화벽 (Application Firewall)](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/network/application-firewall.html) | macOS 호스트 방화벽 기록 |

여러 장비의 기록을 한 줄로 합치는 방법은 [네트워크 타임라인](../../03-techniques/analysis/timeline.md) 에, 로그를 모으고 보존하는 방법은 [로그 수집과 보존](../../03-techniques/acquisition/log-collection.md) 에 있습니다. 무작위 대입 흔적을 방화벽 로그로 찾는 흐름은 [비밀번호를 무작위로 넣어 봤나](../../04-scenarios/intrusion/brute-force.md) 에서 다룹니다.

## 실습

시험용 가상 머신 두 대로 방화벽 로그를 직접 만들어 봅니다. 한 대에 nftables 로 `tcp dport 22 log prefix "SSH-IN " drop` 같은 규칙을 넣고, 다른 한 대에서 SSH 접속을 시도하면서 같은 구간을 tcpdump 로 캡처합니다.

1. 로그 줄의 `MAC=` 를 풀어 출발지 MAC 을 구하고, 캡처의 이더넷 헤더와 같은지 확인합니다.
2. 같은 시도에서 로그 줄 수와 캡처의 SYN 수를 비교합니다. 규칙에 `limit rate 3/minute` 을 더한 뒤 다시 시도하면 두 숫자가 어떻게 달라지는지 봅니다.
3. `log` 문을 `drop` 뒤로 옮기면 줄이 생기는지 확인하고, 규칙 순서가 기록에 주는 영향을 설명합니다.
4. `journalctl -k` 와 `journalctl -k --utc -o short-iso-precise` 로 같은 줄의 시각을 읽고, 캡처 파일의 패킷 시각과 몇 밀리초 차이가 나는지 계산합니다.
5. 컨테이너 안에 같은 규칙을 넣고 `net.netfilter.nf_log_all_netns` 가 0 일 때와 1 일 때 호스트 커널 로그에 줄이 생기는지 확인합니다.

## 참고 문헌

1. iptables-extensions(8) 매뉴얼 (LOG, NFLOG, AUDIT, TRACE, limit). https://man7.org/linux/man-pages/man8/iptables-extensions.8.html
2. nft(8) 매뉴얼 (LOG STATEMENT, MONITOR). https://www.netfilter.org/projects/nftables/manpage.html
3. Linux 소스, `net/netfilter/nf_log_syslog.c`. https://github.com/torvalds/linux/blob/master/net/netfilter/nf_log_syslog.c
4. Linux 문서, `Documentation/networking/netfilter-sysctl.rst`. https://github.com/torvalds/linux/blob/master/Documentation/networking/netfilter-sysctl.rst
5. OpenBSD pf.conf(5) 매뉴얼. https://man.openbsd.org/pf.conf.5
6. OpenBSD pflog(4) 매뉴얼. https://man.openbsd.org/pflog.4
7. OpenBSD pflogd(8) 매뉴얼. https://man.openbsd.org/pflogd.8
8. libpcap, pcap-filter(7). https://github.com/the-tcpdump-group/libpcap/blob/master/pcap-filter.manmisc.in
9. IETF OPSAWG, "Link-Layer Types for PCAP and PCAPNG Capture File Formats" (linktypes). https://github.com/IETF-OPSAWG-WG/draft-ietf-opsawg-pcap
10. ufw(8) 매뉴얼. https://manpages.debian.org/testing/ufw/ufw.8.en.html
11. firewalld.conf(5) 매뉴얼. https://firewalld.org/documentation/man-pages/firewalld.conf.html
12. conntrack(8) 매뉴얼. https://manpages.debian.org/testing/conntrack/conntrack.8.en.html
13. dmesg(1) 매뉴얼. https://man7.org/linux/man-pages/man1/dmesg.1.html
14. journalctl(1) 매뉴얼. https://man7.org/linux/man-pages/man1/journalctl.1.html
15. SigmaHQ, `net_firewall_cleartext_protocols.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/network/firewall/net_firewall_cleartext_protocols.yml
16. SigmaHQ, `net_firewall_apt_equationgroup_c2.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules-emerging-threats/2017/TA/Equation-Group/net_firewall_apt_equationgroup_c2.yml
17. SigmaHQ, `proc_creation_lnx_iptables_flush_ufw.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/linux/process_creation/proc_creation_lnx_iptables_flush_ufw.yml
18. K. Lamshöft, T. Neubert, J. Hielscher, C. Vielhauer, J. Dittmann, "Knock, knock, log: Threat analysis, detection & mitigation of covert channels in syslog using port scans as cover", Forensic Science International: Digital Investigation 40, 2022. doi:10.1016/j.fsidi.2022.301335
19. RFC 3164, "The BSD syslog Protocol". https://www.rfc-editor.org/rfc/rfc3164.txt
20. tcpdump(1) 매뉴얼. https://github.com/the-tcpdump-group/tcpdump/blob/master/tcpdump.1.in
