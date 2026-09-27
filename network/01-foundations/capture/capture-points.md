---
title: "어디서 캡처하나"
parent: "기반 · 패킷 캡처"
nav_order: 20
---

# 어디서 캡처하나 (SPAN·TAP·호스트)

캡처 파일에는 캡처한 지점을 지나간 패킷만 들어 있습니다. 같은 사건이라도 호스트에서 캡처했는지, 스위치의 미러 포트나 네트워크 탭에서 캡처했는지, 클라우드 미러링으로 받았는지에 따라 빠지는 트래픽과 손실이 기록되는 곳이 달라집니다. 이 페이지에서는 캡처 지점마다 무엇이 보이고 무엇이 빠지는지, 그 차이를 캡처 파일과 Zeek·Suricata 기록에서 어떻게 확인하는지 설명합니다.

## 이 내용이 필요한 기록

캡처 지점에 따라 pcap·pcapng 파일의 범위가 정해지고, 그 패킷을 읽어 만든 Zeek 로그와 Suricata EVE 로그의 범위도 똑같이 정해집니다. 센서가 받지 못한 패킷은 어느 로그에도 남지 않으므로, conn.log 에 연결이 없다는 것만으로 통신이 없었다고 쓸 수 없습니다. 파일 형식은 [pcap 형식](pcap.md)과 [pcapng 형식](pcapng.md)에서, 캡처할 때 걸러 내거나 잘라 낸 부분은 [캡처 필터와 잘린 패킷](capture-filters.md)에서, 캡처 명령은 [패킷 캡처하기](../../03-techniques/acquisition/packet-capture.md)에서 다룹니다.

## 캡처 지점별 차이

### 호스트에서 캡처

그 기계가 주고받는 트래픽만 필요하면 그 기계의 네트워크 인터페이스에서 캡처하면 됩니다[1]. 네트워크 카드는 기본으로 자기 주소로 온 유니캐스트와 멀티캐스트, 브로드캐스트만 호스트에 넘기고, 드라이버는 내보내는 패킷의 사본도 캡처 경로로 넘깁니다[1]. 다른 기계끼리 주고받는 트래픽까지 받으려면 이 거르기를 끄는 무차별 모드 (promiscuous mode) 가 필요합니다. 다만 스위치로 연결된 망에서는 스위치가 남의 유니캐스트를 그 포트로 보내지 않아서 무차별 모드로도 보이지 않습니다[1].

같은 기계 안에서 오가는 트래픽은 목적지가 그 기계 네트워크 카드의 주소라도 실제 인터페이스를 지나지 않으므로, 루프백 인터페이스에서 캡처해야만 보입니다[2]. Linux·BSD·macOS 는 루프백 캡처를 지원하고, Windows 는 Npcap 이 있어야 캡처할 수 있으며 이때 링크 형식은 DLT_NULL 입니다[2].

tcpdump 의 `-p` 는 인터페이스를 무차별 모드로 바꾸지 않는다는 뜻일 뿐이라, 다른 이유로 이미 무차별 모드였다면 자기 트래픽이 아닌 패킷도 들어옵니다[5]. Linux 와 최근 macOS·Solaris 의 `any` 가상 인터페이스로 캡처하면 무차별 모드가 켜지지 않습니다[5].

### 포트 미러링 (SPAN)

관리형 스위치는 지정한 포트의 트래픽을 다른 포트로 복사해 내보낼 수 있습니다. 이 기능을 포트 미러링 (port mirroring), 포트 모니터링이라고 하고, Cisco 에서는 SPAN (Switched Port Analyzer) 이라고 부릅니다[1]. 미러 포트가 감시하는 포트보다 느리면 패킷을 잃습니다[1]. 전이중 링크는 보내는 방향과 받는 방향을 한 포트로 합쳐 내보내기 때문에, 보내기 500 Mbps·받기 500 Mbps 인 링크를 미러링하면 미러 포트는 한 방향으로 1 Gbps 를 내보내야 합니다[1]. 스위치 전체가 아니라 특정 포트의 트래픽만 미러링할 수 있는 스위치도 있습니다[1].

### 네트워크 탭 (TAP)

탭은 회선 중간에 끼워 지나가는 트래픽을 복사하는 장비로, breakout·aggregation·replicating·bypass·media changing 같은 종류가 있습니다[1]. breakout 탭은 방향별 출력이 두 개라서, 두 출력을 모두 캡처해 합쳐야 한 연결의 양방향이 모입니다[1]. 전원이 켜질 때 최대 약 2초 동안 패킷을 통과시키지 않는 탭도 있어서, 그동안은 캡처뿐 아니라 실제 통신도 끊깁니다[1].

두 네트워크 카드를 단 기계를 투명 브리지로 두고 캡처하는 방법도 있습니다. 이 방법은 전송이 조금 늦어지고 이더넷 수준에서는 완전히 투명하지 않습니다[1]. 옛 허브를 끼우는 방법은 전이중 트래픽의 성능을 떨어뜨리고, "스위칭 허브" 는 실제로 스위치라서 이 용도로 쓸 수 없습니다[1].

### 클라우드 미러링

AWS VPC 트래픽 미러링 (Traffic Mirroring) 은 원래 패킷을 VXLAN 으로 감싸 UDP 4789 번 포트로 수집 대상에 보냅니다[16]. 바깥 헤더의 출발지 IP 는 미러링하는 네트워크 인터페이스의 주 IP, 도착지 IP 는 수집 장비나 그 앞 로드 밸런서의 주 IP 입니다. 출발지 포트는 원래 L2 패킷의 5-tuple(ICMP·TCP·UDP) 또는 3-tuple 해시로 정합니다[16]. VXLAN ID 에는 세션에 지정한 값이 들어가고, 지정하지 않으면 계정 안에서 겹치지 않는 임의 값이 들어갑니다[16]. Gateway Load Balancer 를 거쳐 받으면 바깥 GENEVE 캡슐화 안에 VXLAN 이 한 겹 더 있습니다[16].

AWS 미러링은 ARP·DHCP·인스턴스 메타데이터 서비스·NTP·Windows 정품 인증 트래픽을 복사하지 않고, IPv6 전용 서브넷에서는 쓸 수 없습니다[16]. 인스턴스의 대역폭이나 초당 패킷 수 한도를 넘으면 운영 트래픽을 살리려고 미러 트래픽부터 버립니다[16]. 수집 대상이 단독 인스턴스이고 캡슐화한 패킷이 대상 MTU 보다 크면 패킷을 MTU 길이로 자르는데, 이를 피하려면 미러링하는 인터페이스의 MTU 를 대상보다 IPv4 는 54바이트, IPv6 는 74바이트 작게 둡니다[16]. 잘린 미러 패킷은 L4 체크섬이 계산되지 않고, L3 헤더까지 잘렸으면 L3 체크섬도 계산되지 않습니다[16]. 수집 대상이 Network Load Balancer 나 Gateway Load Balancer 엔드포인트이면 미러 패킷의 순서가 바뀔 수 있습니다[16]. 한 패킷은 한 번만 미러링하고, 세션은 세션 번호가 낮은 것부터 적용하며, 미러링하던 네트워크 인터페이스를 지우면 세션도 함께 지워집니다[16].

Google Cloud 패킷 미러링 (Packet Mirroring) 은 망이 아니라 VM 에서 트래픽을 복제하므로 VM 의 대역폭을 씁니다[17]. 기본으로 IPv4 트래픽을 모두 모으고, 필터로 IPv6·프로토콜·CIDR 범위·방향(들어오는 것만, 나가는 것만)을 정합니다[17]. 네트워크 인터페이스가 여러 개인 VM 은 정책을 건 인터페이스만 미러링하고, 같은 인터페이스에서 미러링과 수집을 함께 하지 못합니다[17]. 수집 대상은 내부 패스스루 Network Load Balancer 뒤의 인스턴스 그룹입니다[17].

두 클라우드 모두 미러링한 패킷은 VPC 흐름 로그에 기록되지 않습니다[16][17]. 흐름 로그는 [AWS VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/aws/vpc-flow-logs.html)와 [Google Cloud VPC 흐름 로그](https://urock-ailab.github.io/forensics-handbook/cloud/02-artifacts/gcp/vpc-flow-logs.html)에서 다룹니다.

### 한눈에 비교

| 캡처 지점 | 보이는 트래픽 | 빠지기 쉬운 트래픽 | 손실이 기록되는 곳 |
|---|---|---|---|
| 호스트 인터페이스 | 그 기계가 주고받은 패킷(무차별 모드면 그 포트에 도착한 패킷 전부) | 스위치가 그 포트로 보내지 않은 남의 유니캐스트, 루프백 트래픽 | 캡처 도구의 커널 버림 수, pcapng 인터페이스 통계 |
| SPAN | 미러링하도록 지정한 포트의 양방향 | 미러 포트 대역을 넘은 패킷, 스위치 설정에 따라 VLAN 태그 | 스위치에서 버린 패킷은 캡처 호스트 통계에 나오지 않음 |
| TAP | 회선을 지나는 양방향 | breakout 탭의 한 출력만 캡처했을 때 반대 방향 | 캡처 호스트 안의 손실만 기록됨 |
| AWS 트래픽 미러링 | 미러 세션이 고른 네트워크 인터페이스의 트래픽 | ARP·DHCP·메타데이터·NTP·Windows 정품 인증, 한도를 넘었을 때의 미러 트래픽 | 한도를 넘어 버린 미러 패킷은 수집 장비에 남지 않음. 잘린 패킷은 잘린 길이와 계산되지 않은 체크섬으로 드러남 |
| Google Cloud 패킷 미러링 | 정책과 필터가 고른 VM 인터페이스의 트래픽 | 정책을 걸지 않은 다른 인터페이스, 필터로 뺀 트래픽 | 미러링 정책과 필터 설정으로 확인 |

## 읽는 법 — 캡처 지점 확인하기

캡처 지점은 캡처 파일보다 수집 기록으로 먼저 확인합니다. 누가 어느 장비의 어느 포트나 인터페이스에서 언제 캡처했는지, 스위치의 미러 설정과 클라우드 미러 세션·정책이 어땠는지를 함께 받아 둡니다. pcap 파일 헤더에는 캡처 방식을 적는 필드가 없고([pcap 형식](pcap.md)), pcapng 에는 인터페이스 이름(`if_name`)·설명(`if_description`)·하드웨어(`if_hardware`), 그 섹션을 만든 하드웨어(`shb_hardware`), 주석(`opt_comment`) 옵션이 있지만 SPAN 인지 TAP 인지를 정해 적는 필드는 없습니다[7]. 그래서 캡처한 사람이 이 옵션에 적어 둔 경우에만 파일에서 알 수 있습니다.

수집 기록이 없으면 캡처 파일 안의 모양으로 짐작할 수 있습니다. 아래 표의 단서는 그런 캡처 방식일 가능성을 보여 줄 뿐이고, 확정은 수집 기록과 장비 설정으로 합니다.

| 캡처 파일에서 보이는 것 | 가능성이 있는 캡처 방식 |
|---|---|
| 보내는 패킷의 IP·TCP·UDP 체크섬이 틀렸다고 표시됨 | 체크섬 오프로딩을 켠 호스트에서 캡처. 네트워크 카드가 체크섬을 계산하기 전에 캡처 도구가 패킷을 받기 때문입니다. Wireshark 1.2 부터는 새로 설치하면 체크섬 검사가 꺼져 있고, 4.2 부터는 Linux·Windows 가 의사 헤더 (pseudo header) 몫만 채워 둔 체크섬을 오류가 아닌 부분 체크섬으로 표시합니다[4] |
| MTU 1500 인 망에서 2900바이트 같은 큰 패킷 | 세그먼트 오프로딩(LRO·GRO 등)을 켠 호스트에서 캡처[4][11] |
| 링크 형식이 DLT_NULL 인 Windows 캡처 | Npcap 루프백 어댑터에서 캡처[2] |
| 바깥에 UDP 4789 번 VXLAN 헤더가 있고 그 안에 원래 이더넷 프레임 | AWS 트래픽 미러링처럼 VXLAN 으로 감싸 보내는 미러링[16] |
| 바깥 GENEVE 안에 VXLAN | AWS 트래픽 미러링을 Gateway Load Balancer 를 거쳐 받음[16] |
| 같은 패킷이 두 번 이상 | VLAN 태그를 넘기지 않는 미러 포트에서 캡처했거나[1], 여러 지점에서 캡처한 파일을 합침[8] |
| 한 연결의 한 방향만 있음 | breakout 탭의 한 출력만 캡처[1]. 미러 설정이 한 방향만 복사했거나 트래픽이 다른 경로로 돌아갔을 가능성도 있음 |

VXLAN 으로 감싼 패킷은 바깥 헤더를 한 겹 벗겨야 원래 패킷의 IP 와 포트가 보입니다. 분석 도구가 자동으로 풀지 않으면 UDP 4789 번을 VXLAN 으로 해석하도록 지정한 뒤, 안쪽 이더넷 프레임이 제대로 풀리는지 확인합니다.

## 포렌식에서 중요한 점

### 증명하는 것과 증명하지 못하는 것

캡처 파일로는 그 시간에 그 캡처 지점을 지나가서 장비가 캡처 도구에 넘겨 준 패킷이 있었다는 사실을 증명할 수 있습니다. 캡처 지점 밖의 트래픽, 곧 같은 스위치의 다른 포트, 같은 기계 안의 루프백, 다른 경로로 나간 트래픽은 증명하지 못합니다. 캡처 파일에 없다는 것도 통신이 없었다는 증거가 되지 못하는데, 스위치나 클라우드가 미러 트래픽을 버렸다면 그 수가 캡처 파일 어디에도 남지 않기 때문입니다[1][16].

### 손실이 어디서 기록되나

tcpdump 가 끝날 때 보여 주는 "dropped by kernel" 은 캡처 장치의 버퍼가 모자라 운영체제가 버린 패킷 수이고, 운영체제가 이 수를 알려 주지 않으면 0 으로 나옵니다[5]. "received by filter" 는 운영체제에 따라 필터를 통과하기 전의 수이기도 하고 통과한 뒤의 수이기도 해서, 운영체제마다 뜻이 다릅니다[5]. pcapng 인터페이스 통계 블록에는 인터페이스가 버린 수(`isb_ifdrop`)와 운영체제가 버린 수(`isb_osdrop`)를 적는 옵션이 있습니다[7].

이 수들은 모두 캡처 호스트 안에서 생긴 손실만 셉니다. 스위치·탭·클라우드처럼 캡처 호스트 앞에서 생긴 손실은 TCP 흐름에 생긴 빈틈으로만 드러납니다. Zeek 는 TCP 순서 번호를 보고 빈틈을 찾아 capture_loss.log 에 기록합니다[9]. 이 로그의 `percent_lost` 는 백분율이라 `0.41` 은 41% 가 아니라 0.41% 입니다[9]. 아래는 만든 예시입니다.

```json
{"ts":"2026-03-02T01:15:00.000000Z","ts_delta":900.0,"peer":"sensor-eth1-1","gaps":12,"acks":8400,"percent_lost":0.142857}
```

연결 하나하나에서는 conn.log 의 `missed_bytes` 가 빈틈에서 놓친 바이트 수이고, 0 이 아니면 대개 그 연결의 프로토콜 분석이 실패합니다[10]. 같은 연결의 `history` 에 `g` 가 있으면 내용에 빈틈이 있었다는 뜻입니다[10]. Suricata stats.log 의 `tcp.reassembly_gap` 은 TCP 스트림에서 빠진 데이터 패킷을 세는데, 이 값은 패킷 손실뿐 아니라 체크섬 불량과 스트림 엔진의 메모리 부족으로도 올라갑니다[12]. AF_PACKET 모드에서 `capture.kernel_packets` 는 사용자 공간으로 넘긴 패킷 수, `capture.kernel_drops` 는 넘기지 못하고 버린 패킷 수이고, 버린 수는 넘긴 수의 1% 아래가 목표입니다[12].

Zeek 가 capture loss 는 보고하는데 packet loss 는 보고하지 않으면, 손실은 대개 탭이나 SPAN 포트 자체, 곧 센서 앞에서 생긴 것입니다[14]. packet loss 를 보고할 때는 Zeek 워커 수를 조정하거나 BPF 로 트래픽을 걸러 줄여야 합니다[14].

### 시각

캡처 파일의 시각은 캡처한 기계가 붙입니다. 받는 패킷에는 도착 시각을, 보내는 패킷에는 전송 시각을 근사해 붙이고, 네트워크 스택이 패킷을 늦게 처리하면 그만큼 늦은 시각이 들어갑니다[6]. 캡처 장치가 직접 붙이는 시각은 더 정밀하지만 호스트 운영체제의 시계와 맞춰져 있지 않을 수 있습니다[6]. 그래서 SPAN·TAP·클라우드 미러링으로 받은 캡처의 시각은 통신한 기계가 아니라 센서의 시계이고, 통신한 기계의 로그와 비교할 때는 두 시계의 차이를 먼저 확인합니다. 시각 비교 방법은 [네트워크 기록의 시각](../records/timestamps.md)에서 다룹니다.

### VLAN 태그와 NAT

많은 네트워크 카드는 받은 패킷의 VLAN 태그를 기본으로 떼어 내고, 스위치가 미러 포트에서 태그를 떼기도 합니다[1]. VLAN 을 설정한 호스트에서 캡처하면 물리 장치에서 캡처해도 드라이버가 먼저 태그를 떼어 태그가 보이지 않을 가능성이 큽니다[3]. Security Onion 의 Stenographer 는 AF_PACKET 을 쓰는 방식 때문에 VLAN 트래픽은 기록하지만 태그는 남기지 않습니다[15]. 반대로 같은 환경의 Zeek 와 Suricata 는 트래픽에 VLAN 태그가 있으면 로그에 남깁니다[14]. 그래서 캡처 파일에 태그가 없다고 VLAN 이 없었다고 판단하지 않습니다.

NAT 경계 근처에서 캡처할 때는 경계 안쪽에서 캡처해야 실제 내부 IP 주소가 보입니다[13]. 바깥쪽에서 캡처한 파일에는 변환된 주소만 남으므로, 내부 기계를 찾으려면 NAT 장비의 기록이 따로 필요합니다. 자세한 내용은 [IP 주소·포트·NAT 해석](../records/ip-nat.md)에 있습니다.

## 함정

**SPAN 과 TAP 중 무엇이 나은지는 의견이 갈립니다.** Wireshark 위키에는 두 주장이 함께 실려 있습니다[1]. 한쪽은 미러 포트가 불량 프레임과 너무 짧거나 긴 프레임을 넘기지 않고, VLAN 태그를 넘기지 않아 같은 패킷이 두 번 이상 보일 수 있으며, 패킷 간격이 바뀌고, 법정에서 합리적 의심의 여지를 남긴다고 봅니다. 다른 쪽은 많은 스위치가 태그까지 미러링하도록 설정할 수 있고(Cisco 는 SPAN 포트를 트렁크로 설정), 복사는 스위치 칩에서 하므로 지연이 마이크로초 단위라고 봅니다. 이 주장에서는 9000바이트 점보 프레임을 1 Gbps 로 끼워 넣을 때 생기는 지연을 72 µs 로 계산합니다. Security Onion 문서는 가능하면 전용 탭을 쓰라고 권합니다[13]. 어느 쪽이든 결과는 스위치 모델과 설정에 따라 달라지므로, 보고서에는 쓴 장비와 설정을 적고 그 장비의 동작을 설정과 문서로 확인합니다.

**중복 패킷을 손실이나 재전송으로 잘못 읽을 수 있습니다.** 미러 포트가 VLAN 태그를 넘기지 않거나[1] 여러 지점에서 캡처한 파일을 합치면[8] 같은 패킷이 한 파일에 두 번 이상 들어갑니다. editcap 의 `-d` 는 앞의 네 패킷과 길이·MD5 해시를 비교해 같은 패킷을 빼고(`-D 5` 와 같음), `-I` 는 해시를 계산할 때 앞부분 바이트를 무시해 라우터마다 MAC 주소가 다른 사본도 같은 패킷으로 묶습니다[8]. 중복 제거 절차는 [큰 캡처 파일 다루기](../../03-techniques/acquisition/large-captures.md)에서 다룹니다.

**센서 설정 때문에 생긴 이상을 트래픽의 특징으로 읽을 수 있습니다.** 호스트에서 캡처하면 오프로딩 때문에 MTU 보다 큰 패킷과 틀린 체크섬이 보입니다[4]. Suricata 는 LRO·GRO 가 작은 패킷을 큰 패킷으로 합쳐 TCP 상태 추적을 깨뜨리므로 끄라고 권하고[11], Security Onion 설치 프로그램은 캡처용 인터페이스에서 `tso`·`gso`·`gro` 를 끕니다[13]. 네트워크 카드의 수신 분산 (RSS, Receive Side Scaling) 해시는 대개 대칭이 아니라서, SPAN·탭 트래픽의 두 방향이 서로 다른 큐로 들어가 처리 순서가 뒤섞입니다. 그러면 Suricata 가 SYN/ACK 를 데이터보다 한참 늦게 받아 정상 트래픽을 잘못된 트래픽으로 볼 수 있어서, RSS 큐를 하나로 줄이는 설정을 권합니다[11]. 센서에서 나온 TCP 이상 경보는 센서의 오프로딩·RSS 설정을 먼저 확인하고 해석합니다.

**전수 캡처 시스템에도 오래된 기간과 긴 흐름은 빠져 있을 수 있습니다.** Stenographer 는 디스크 여유 공간이 DiskFreePercentage 설정 아래로 떨어지면 오래된 파일부터 지우고, 기본으로 캡처 디렉터리의 파일 수를 30000 개로 제한합니다[15]. Security Onion 에서 Suricata 가 캡처를 맡으면 흐름이 stream depth 에 이르는 순간 그 흐름의 패킷 기록을 멈추는데, 기본값은 1MB 입니다[14]. Arkime 의 PCAP 보존 기간은 센서의 디스크 용량에 따라 정해집니다[18]. 그래서 전수 캡처 장비에서 꺼낸 파일이라도 긴 파일 전송의 뒷부분이나 오래된 날짜가 빠져 있을 수 있습니다.

**클라우드 미러링의 잘림과 체크섬 오류는 미러링 제약일 수 있습니다.** AWS 에서 대상 MTU 를 넘은 미러 패킷은 잘리고 체크섬이 계산되지 않으므로[16], 이런 패킷을 조작이나 공격의 흔적으로 읽기 전에 미러링하는 인터페이스와 대상의 MTU 를 비교합니다.

## 도구

| 도구 | 캡처 지점을 확인할 때 쓰는 것 |
|---|---|
| tcpdump | `-D` 로 캡처할 수 있는 인터페이스 목록, `-p` 로 무차별 모드 끄기, `-Q in`·`out`·`inout` 으로 방향 고르기(일부 플랫폼만), 끝날 때의 "dropped by kernel" 수[5] |
| editcap | `-d`·`-D`·`-w`·`-I` 로 여러 지점에서 복사된 중복 패킷 제거[8] |
| Zeek | capture_loss.log 의 `gaps`·`acks`·`percent_lost`, conn.log 의 `missed_bytes` 와 `history` 의 `g`[9][10] |
| Suricata | stats.log 의 `capture.kernel_packets`·`capture.kernel_drops`·`tcp.reassembly_gap`[12] |
| Stenographer·Suricata·Arkime 전수 캡처 | 보존 기간과 흐름별 기록 한도 확인[14][15][18] |

Zeek 와 Suricata 로그 전체는 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md)와 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)에서 다룹니다.

## 참고 문헌

1. Wireshark Wiki, "Ethernet capture setup". https://wiki.wireshark.org/CaptureSetup/Ethernet
2. Wireshark Wiki, "Loopback capture setup". https://wiki.wireshark.org/CaptureSetup/Loopback
3. Wireshark Wiki, "VLAN capture setup". https://wiki.wireshark.org/CaptureSetup/VLAN
4. Wireshark Wiki, "Offloading". https://wiki.wireshark.org/CaptureSetup/Offloading
5. tcpdump 매뉴얼 (tcpdump.1). https://github.com/the-tcpdump-group/tcpdump/blob/master/tcpdump.1.in
6. libpcap 매뉴얼, pcap-tstamp. https://github.com/the-tcpdump-group/libpcap/blob/master/pcap-tstamp.manmisc.in
7. IETF OPSAWG, "PCAP Now Generic (pcapng) Capture File Format" 초안. https://github.com/IETF-OPSAWG-WG/draft-ietf-opsawg-pcap/blob/master/draft-ietf-opsawg-pcapng.md
8. Wireshark 매뉴얼, editcap. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/editcap.adoc
9. Zeek 문서, "capture_loss.log and reporter.log". https://github.com/zeek/zeek-docs/blob/master/logs/capture-loss-and-reporter.rst
10. Zeek 문서, base/protocols/conn/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
11. Suricata 사용자 안내서, "Packet Capture". https://github.com/OISF/suricata/blob/main/doc/userguide/performance/packet-capture.rst
12. Suricata 사용자 안내서, "Statistics"·"Analysis". https://github.com/OISF/suricata/blob/main/doc/userguide/performance/statistics.rst , https://github.com/OISF/suricata/blob/main/doc/userguide/performance/analysis.rst
13. Security Onion 문서, "Best Practices"·"Hardware Requirements". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/best-practices.rst , https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/hardware.rst
14. Security Onion 문서, "Zeek"·"Suricata". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/zeek.rst , https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/suricata.rst
15. Security Onion 문서, "AF-PACKET"·"Stenographer". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/af-packet.rst , https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/stenographer.rst
16. AWS, "Traffic Mirroring" 문서(What is Traffic Mirroring, packet format, target concepts, session concepts, limitations). https://docs.aws.amazon.com/vpc/latest/mirroring/what-is-traffic-mirroring.html , https://docs.aws.amazon.com/vpc/latest/mirroring/traffic-mirroring-packet-formats.html , https://docs.aws.amazon.com/vpc/latest/mirroring/traffic-mirroring-considerations.html , https://docs.aws.amazon.com/vpc/latest/mirroring/traffic-mirroring-sessions.html , https://docs.aws.amazon.com/vpc/latest/mirroring/traffic-mirroring-network-limitations.html
17. Google Cloud, "Packet Mirroring". https://cloud.google.com/vpc/docs/packet-mirroring
18. Arkime README. https://github.com/arkime/arkime/blob/main/README.md
