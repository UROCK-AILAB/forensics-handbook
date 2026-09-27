---
title: "캡처 필터와 잘린 패킷"
parent: "기반 · 패킷 캡처"
nav_order: 30
---

# 캡처 필터와 잘린 패킷 (Capture Filter·Snaplen)

캡처 파일에는 네트워크에 흐른 모든 것이 아니라, 캡처 필터를 통과하고 스냅 길이 안에 든 바이트만 남습니다. 이 페이지는 두 설정이 파일 어디에 흔적을 남기는지, 그 흔적으로 무엇이 빠졌는지 판단하는 방법을 다룹니다. 필터에 걸러진 패킷과 스냅 길이 밖의 바이트는 파일에 아예 없어서 나중에 되살릴 수 없습니다.

## 이 형식을 쓰는 아티팩트

캡처 필터 (capture filter) 는 libpcap 의 `pcap_compile` 이 BPF (Berkeley Packet Filter) 프로그램으로 컴파일해 캡처 단계에서 적용하는 식입니다[9]. tcpdump, Wireshark 의 캡처 엔진인 dumpcap, WinDump 가 모두 같은 문법(pcap-filter(7))을 씁니다[3][11]. 스냅 길이 (SnapLen) 는 패킷마다 저장할 최대 바이트 수이고, 이 길이를 넘는 부분은 파일에 저장되지 않습니다[1][2].

두 설정은 다음 기록에 영향을 줍니다.

- tcpdump·dumpcap·tshark 로 만든 pcap·pcapng 파일. 파일 구조는 [pcap 형식](pcap.md), [pcapng 형식](pcapng.md) 에서 다룹니다.
- Suricata 가 경보와 함께 남기는 pcap-log 파일. `bpf-filter` 를 설정하면 식에 맞지 않는 패킷은 기록하지 않습니다[15].
- Suricata 가 pcap 파일을 읽어 분석할 때. `-F` 로 지정한 파일의 BPF 식이 적용됩니다[16].
- Security Onion 같은 센서. BPF 설정을 PCAP 엔진(Stenographer 또는 Suricata)·Suricata·Zeek 에 따로 줄 수 있고, PCAP 엔진이 Suricata 일 때 PCAP 엔진용 BPF 는 PCAP 에만 적용되고 경보와 메타데이터에는 적용되지 않습니다[13].

어디에서 캡처했는지(SPAN·TAP·호스트)에 따라 빠지는 패킷은 [어디서 캡처하나](capture-points.md) 에서 다룹니다.

## 구조

### 캡처 필터 식

필터 식은 기본 단위 (primitive) 를 `and`·`or`·`not` 으로 이은 것이고, 기본 단위는 한정어 (qualifier) 와 값 (id) 으로 이뤄집니다[3]. 한정어는 세 종류입니다.

| 한정어 | 쓸 수 있는 값 | 생략하면 |
|---|---|---|
| type | host, net, port, portrange, proto, protochain, gateway | host |
| dir | src, dst, src or dst, src and dst, ra, ta, addr1~addr4 (ra 이하는 802.11 전용) | src or dst |
| proto | ether, link, wlan, ip, ip6, arp, tcp, udp, sctp 등 | type 과 맞는 프로토콜 전부 |

proto 를 생략하면 가능한 프로토콜을 모두 넣은 것으로 해석해서, `port 53` 은 `(tcp or udp or sctp) port 53` 과 같습니다[3]. 캡처 필터 `tcp port 80` 과 Wireshark 디스플레이 필터 `tcp.port == 80` 은 다른 문법입니다. 캡처 필터는 캡처를 시작하기 전에 정하고 캡처 중에는 바꿀 수 없지만, 디스플레이 필터는 이미 저장된 패킷을 화면에서 숨길 뿐입니다[11].

libpcap 버전에 따라 쓸 수 있는 키워드가 다릅니다. 필터 문자열을 해석할 때 캡처 호스트의 libpcap 버전도 함께 확인합니다[3].

| 키워드 | 쓸 수 있게 된 libpcap 버전 |
|---|---|
| `geneve` | 1.8.0 |
| ICMPv6 유형 이름, `tcp-ece`·`tcp-cwr` | 1.9.0 |
| `ifindex` | 1.10.0 |
| `vxlan` | 1.11.0 |
| `gateway` | 1.11.0 전에는 정의가 달랐고, 1.0.0 부터 기본으로 꺼져 있었음 |

### 필터 문자열이 남는 곳

pcap 파일 헤더에는 필터를 적는 필드가 없습니다[1]. pcapng 는 인터페이스 설명 블록 (Interface Description Block, IDB) 의 `if_filter` 옵션(코드 11)에 필터를 적을 수 있고, 옵션 데이터의 첫 바이트는 필터 종류(libpcap 문자열인지 BPF 바이트코드인지 등)를 나타냅니다[2]. dumpcap 은 IDB 를 쓸 때 캡처 필터 문자열을 이 옵션에 넣습니다[9]. dumpcap 기본 저장 형식은 pcapng 이고 `-F pcap` 이나 `-P` 를 주면 pcap 으로 저장해서[5], 이렇게 만든 파일에는 필터 문자열이 남지 않습니다. 여러 인터페이스에서 캡처하면 `-P` 를 줘도 pcapng 로 저장합니다[5].

아래는 IDB 옵션 영역에 `port 53` 필터가 들어 있는 모양을 명세로 만든 예시(리틀 엔디언)입니다.

```
0B 00          옵션 코드 11 (if_filter)
08 00          옵션 길이 8
00             필터 종류 0 (libpcap 필터 문자열)
70 6F 72 74 20 35 33    "port 53"
```

### 스냅 길이와 두 길이 필드

스냅 길이는 파일 헤더와 패킷 레코드 두 곳에서 확인합니다.

| 위치 | 필드 | 뜻 |
|---|---|---|
| pcap 파일 헤더 오프셋 16 | SnapLen | 패킷당 최대 저장 바이트. 0 이면 안 됨[1] |
| pcapng IDB | SnapLen | 인터페이스별 최대 저장 바이트. 0 이면 제한 없음[2] |
| pcap 패킷 레코드 오프셋 8 / 12 | Captured Packet Length / Original Packet Length | 저장한 길이 / 원래 길이[1] |
| pcapng EPB 오프셋 20 / 24 | Captured Packet Length / Original Packet Length | 저장한 길이 / 원래 길이[2] |

저장한 길이가 원래 길이보다 작으면 그 패킷은 잘린 것입니다. 원래 길이는 잘리지 않았다면 저장됐을 길이이고, 스냅 길이뿐 아니라 캡처 장치가 거는 길이 제한 때문에 잘려도 저장한 길이와 달라집니다[1]. 아래는 1514바이트 이더넷 프레임을 96바이트만 저장한 pcapng 강화 패킷 블록 (Enhanced Packet Block, EPB) 의 일부를 명세로 만든 예시(리틀 엔디언)입니다.

```
오프셋 20: 60 00 00 00    Captured Packet Length = 96
오프셋 24: EA 05 00 00    Original Packet Length = 1514
```

### 도구별 기본 스냅 길이

| 도구 | 옵션 | 기본값 |
|---|---|---|
| tcpdump | `-s`, `--snapshot-length` | 262144바이트. `-s 0` 도 262144[4] |
| dumpcap | `-s`, `--snapshot-length` | 0 = 262144바이트, 패킷 전체 저장[5] |

Wireshark 위키의 SnapLen 글은 tcpdump 기본값을 IPv4 68바이트, IPv6 96바이트로 적었지만[12], 현재 tcpdump 매뉴얼의 기본값은 262144바이트입니다[4]. 오래된 tcpdump 로 만든 파일은 스냅 길이가 68·96 처럼 작을 수 있으니 파일 헤더 값을 직접 확인합니다.

## 읽는 법

잘린 패킷이 있는지는 Wireshark 필드로 바로 찾습니다. `frame.cap_len` 이 저장한 길이, `frame.len` 이 원래 길이라서[10], 디스플레이 필터 `frame.cap_len < frame.len` 으로 잘린 패킷만 골라냅니다. capinfos `-l` 은 파일 헤더와 잘린 레코드를 보고 스냅 길이를 출력합니다[7]. tcpdump 로 읽을 때 잘린 지점은 `[|tcp]` 처럼 `[|프로토콜]` 로 표시되며, 이 예라면 TCP 헤더를 다 담지 못했다는 뜻입니다[4].

```
$ capinfos -l capture.pcapng
$ tshark -r capture.pcapng -Y "frame.cap_len < frame.len" -T fields -e frame.number -e frame.cap_len -e frame.len
```

필터가 걸려 있었는지는 pcapng 의 IDB `if_filter` 를 봅니다. capinfos `-I` 로 인터페이스 정보를 자세히 출력해 확인합니다[7]. 필터 문자열이 실제로 어떤 패킷을 통과시키는지는 컴파일 결과로 확인합니다. tcpdump `-d` 는 컴파일한 코드를 사람이 읽을 수 있게 출력하고 멈추며[4], dumpcap `-d` 는 인터페이스마다 컴파일 결과를 출력합니다. 같은 필터도 인터페이스(링크 계층 형식)가 다르면 다르게 컴파일될 수 있습니다[5]. `--no-optimize` 를 주면 libpcap 최적화 없이 컴파일합니다[5]. tcpdump `-F 파일` 은 파일에서 필터 식을 읽고 명령줄에 준 식은 무시해서[4], 명령줄 기록만 보고 필터를 판단하면 틀릴 수 있습니다.

```
$ tcpdump -d "port 53"
$ dumpcap -i eth0 -f "port 53" -d
```

## 포렌식에서 중요한 점

### 증명하는 것 / 증명하지 못하는 것

캡처 파일에 있는 패킷은 필터를 통과해 그 시각에 캡처 지점을 지나갔다는 기록입니다. 잘린 패킷도 원래 길이 필드가 남아서, 본문을 못 읽어도 "1514바이트짜리 프레임이 있었다" 는 것까지는 말할 수 있습니다.

반대로 캡처 파일에 어떤 트래픽이 없다는 사실만으로는 그 트래픽이 없었다고 할 수 없습니다. 캡처 필터에 걸러졌을 수 있고, 필터가 없었더라도 스냅 길이 밖의 바이트는 없습니다. 잘린 패킷에서는 HTTP 본문이나 전송된 파일 내용을 되살릴 수 없고, IP 조각 재조립처럼 상위 계층을 이어 붙이는 작업도 못 할 수 있습니다[12]. 원래 길이 필드도 캡처 도구가 적은 값이라, editcap `-L` 로 고쳐 쓰면 바뀝니다[6].

### 흐름 뒷부분이 통째로 없는 경우

스냅 길이는 패킷 하나의 뒷부분을 자르지만, 센서의 PCAP 기록 설정은 흐름 뒷부분의 패킷 자체를 빼기도 합니다. Suricata pcap-log 는 기본으로 `stream.reassembly.depth` 를 넘은 TCP 스트림과 키 교환 뒤의 암호화된 스트림을 기록하지 않습니다[15]. Security Onion 은 Suricata 로 PCAP 을 기록할 때 스트림 깊이를 기본 1MB 로 둬서, 흐름이 1MB 에 이르면 그 흐름의 패킷 기록을 멈춥니다. `use-stream-depth` 를 `no` 로 바꾸면 흐름 전체를 기록합니다[14]. 이런 파일에서 큰 파일 전송은 앞부분만 남고 저장한 길이와 원래 길이는 같게 보여서, `frame.cap_len < frame.len` 으로는 찾을 수 없습니다.

Suricata pcap-log 의 `conditional` 값이 `alerts` 이면 경보가 난 흐름만, `tag` 이면 규칙이 태그한 패킷만 기록합니다[15]. 이런 센서에서 받은 pcap 은 처음부터 선별된 기록입니다.

### 시각

캡처 필터와 스냅 길이는 시각 필드에 영향을 주지 않습니다. 잘린 패킷도 레코드 헤더의 타임스탬프는 그대로 남습니다[1]. 시각 기준과 정밀도는 [네트워크 기록의 시각](../records/timestamps.md) 에서 다룹니다.

## 함정

**VLAN 태그가 붙은 트래픽.** 식에 처음 나오는 `vlan` 키워드는 패킷이 VLAN 패킷이라고 보고, 식의 나머지 부분을 해석할 위치를 4바이트 옮깁니다. `vlan` 을 한 번 더 쓸 때마다 4바이트씩 더 옮깁니다. `mpls` 도 같습니다[3]. 그래서 `vlan` 없이 쓴 `not host 192.0.2.10` 같은 제외 식은 태그 붙은 패킷에 의도대로 적용되지 않습니다. 태그 붙은 트래픽까지 같은 조건으로 거르려면 `필터 or (vlan and 필터)` 처럼 양쪽에 같은 조건을 넣습니다[13]. 필터 문자열에 `vlan` 이 없는데 트렁크 포트에서 캡처했다면, 뺐다고 생각한 트래픽이 섞여 있거나 원하던 트래픽이 빠졌을 수 있습니다.

**IP 조각과 port 필터.** `port` 는 IPv4 에서 조각나지 않았거나 첫 조각인 패킷에만 맞고, IPv6 에서는 확장 헤더(Routing, Fragment, Destination Options 등)가 없는 패킷에만 맞습니다[3]. `port` 로 캡처했다면 두 번째 이후 IP 조각은 파일에 없습니다. `tcp[0]` 처럼 전송 계층 헤더를 직접 읽는 식은 IPv4 패킷만 봅니다[3].

**IPv6 헤더 체인.** `ip6 proto` 는 확장 헤더를 따라가지 않습니다. IPv6 조각을 잡으려면 `ip6 protochain 44` 를 씁니다[3].

**방향 키워드.** `inbound`·`outbound` 는 DLT_LINUX_SLL·DLT_LINUX_SLL2·DLT_SLIP·DLT_IPNET·DLT_PFLOG·DLT_PPP_PPPD 등 일부 링크 계층 형식에서만 동작하고, `ifindex` 는 리눅스 any 인터페이스(cooked v2)로 캡처한 패킷에만 적용됩니다[3].

**통계 숫자.** tcpdump 가 끝날 때 보여 주는 "received by filter" 는 OS 에 따라 필터와 상관없이 센 수일 수도, 필터에 맞은 수만 센 것일 수도 있습니다[4]. 이 숫자를 캡처 대상 전체 트래픽 양으로 보고서에 쓰지 않습니다. Zeek 을 함께 돌렸다면 `capture_loss.log` 의 `percent_lost` 로 놓친 비율을 따로 확인합니다[17]. 로그 형식은 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) 에서 다룹니다.

**필터 기록이 파일 밖에 있을 때.** pcap 파일은 필터를 적지 않아서 파일만으로는 필터 사용 여부를 알 수 없습니다[1]. 센서 설정 파일이나 로그를 함께 확보합니다. Security Onion 의 Zeek 스크립트(bpfconf.zeek)는 BPF 설정 파일을 정할 때 reporter.log 에 아래 같은 줄을 남깁니다[17].

```
"message": "BPFConf filename set: /etc/nsm/sensor-eth1/bpf-bro.conf (logger)"   (만든 예시)
```

**클라우드 미러의 잘림.** AWS 트래픽 미러링은 대상이 단독 인스턴스이고 미러 패킷이 대상 MTU 보다 크면 패킷을 MTU 에 맞춰 자릅니다. 잘림을 피하려면 미러 원본 인터페이스의 MTU 를 대상 MTU 보다 IPv4 는 54바이트, IPv6 는 74바이트 작게 둬야 합니다[18]. 이렇게 잘린 미러 패킷은 체크섬이 계산되지 않을 수 있어서[18], 체크섬 오류 표시만 보고 조작된 패킷으로 판단하지 않습니다.

**사후에 자른 파일.** editcap `-s` 는 스냅 길이를 줄여 다시 쓰고, `-C` 는 패킷 앞이나 뒤를 지정한 바이트만큼 잘라 냅니다. 저장한 길이는 항상 바뀌지만, 원래 길이는 `-L` 을 줄 때만 함께 바뀝니다[6]. mergecap 도 `-s` 로 합치면서 자를 수 있습니다[8]. `-L` 로 자른 파일은 원래 길이도 함께 줄어 처음부터 작은 패킷이었던 것처럼 보일 수 있으므로, 받은 파일이 원본인지 가공본인지 해시와 인계 기록으로 확인합니다. 파일 자르기·합치기는 [큰 캡처 파일 다루기](../../03-techniques/acquisition/large-captures.md) 에서 다룹니다.

**Suricata 입력 디렉터리.** Suricata 의 pcap-file `delete-when-done` 을 `true` 로 두면 처리한 pcap 을 지우고, `"non-alerts"` 이면 경보가 나지 않은 파일을 지웁니다(기본 `false`). 명령줄 `--pcap-file-delete` 는 설정과 상관없이 항상 지웁니다[16]. 증거 원본은 Suricata 입력 디렉터리에 두지 않고 사본을 넣습니다.

## 도구

| 도구 | 이 페이지와 관련된 옵션 |
|---|---|
| tcpdump | `-s`(스냅 길이), `-d`(필터 컴파일 결과), `-F`(파일에서 필터 읽기)[4] |
| dumpcap | `-f`(캡처 필터), `-s`, `-d`, `--no-optimize`, `-P`(pcap 으로 저장)[5] |
| editcap | `-s`, `-C`, `-L`(원래 길이도 조정)[6] |
| mergecap | `-s`[8] |
| capinfos | `-l`(스냅 길이), `-I`(인터페이스 정보), `-d`(원래 길이 기준 총 바이트)[7] |
| Wireshark·tshark | `frame.cap_len`, `frame.len`[10] |

capinfos `-d` 는 저장한 바이트가 아니라 원래 길이를 더합니다. 1514바이트 패킷을 256바이트만 저장했어도 1514바이트로 셉니다[7]. 파일 크기보다 capinfos 총 바이트가 훨씬 크면 잘린 패킷이 많을 가능성이 있습니다.

캡처를 시작할 때 필터·스냅 길이를 정하는 절차는 [패킷 캡처하기](../../03-techniques/acquisition/packet-capture.md) 에서 다룹니다.

## 참고 문헌

1. IETF OPSAWG, "PCAP Capture File Format" (draft-ietf-opsawg-pcap). https://github.com/IETF-OPSAWG-WG/draft-ietf-opsawg-pcap/blob/master/draft-ietf-opsawg-pcap.md
2. IETF OPSAWG, "PCAP Next Generation (pcapng) Capture File Format" (draft-ietf-opsawg-pcapng). https://github.com/IETF-OPSAWG-WG/draft-ietf-opsawg-pcap/blob/master/draft-ietf-opsawg-pcapng.md
3. The Tcpdump Group, pcap-filter(7). https://github.com/the-tcpdump-group/libpcap/blob/master/pcap-filter.manmisc.in
4. The Tcpdump Group, tcpdump(1). https://github.com/the-tcpdump-group/tcpdump/blob/master/tcpdump.1.in
5. Wireshark, dumpcap(1). https://github.com/wireshark/wireshark/blob/master/doc/man_pages/dumpcap.adoc
6. Wireshark, editcap(1). https://github.com/wireshark/wireshark/blob/master/doc/man_pages/editcap.adoc
7. Wireshark, capinfos(1). https://github.com/wireshark/wireshark/blob/master/doc/man_pages/capinfos.adoc
8. Wireshark, mergecap(1). https://github.com/wireshark/wireshark/blob/master/doc/man_pages/mergecap.adoc
9. Wireshark, dumpcap.c. https://github.com/wireshark/wireshark/blob/master/dumpcap.c
10. Wireshark, Display Filter Reference: Frame. https://www.wireshark.org/docs/dfref/f/frame.html
11. Wireshark Wiki, CaptureFilters. https://wiki.wireshark.org/CaptureFilters
12. Wireshark Wiki, SnapLen. https://wiki.wireshark.org/SnapLen
13. Security Onion Documentation 2.4, BPF. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/bpf.rst
14. Security Onion Documentation 2.4, Suricata. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/suricata.rst
15. OISF, Suricata User Guide — suricata.yaml (pcap-log). https://github.com/OISF/suricata/blob/main/doc/userguide/configuration/suricata-yaml.rst
16. OISF, Suricata User Guide — PCAP File Reading. https://github.com/OISF/suricata/blob/main/doc/userguide/capture-hardware/pcap-file.rst
17. Zeek Documentation, capture_loss.log and reporter.log. https://github.com/zeek/zeek-docs/blob/master/logs/capture-loss-and-reporter.rst
18. AWS, Traffic Mirroring limitations. https://docs.aws.amazon.com/vpc/latest/mirroring/traffic-mirroring-network-limitations.html
