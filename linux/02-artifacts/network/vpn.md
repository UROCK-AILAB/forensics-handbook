---
title: "VPN"
parent: "아티팩트 · 네트워크"
nav_order: 730
---

# VPN (WireGuard·OpenVPN)

WireGuard 와 OpenVPN 의 설정 파일, 서비스 유닛이 남긴 저널 줄, OpenVPN 서버의 상태 파일을 모으면 이 시스템이 어느 상대와 터널을 맺도록 설정됐고 언제 터널을 올리고 내렸는지를 좁힐 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

WireGuard 는 가상 네트워크 인터페이스이고, 흔히 `wg-quick` 스크립트가 설정 파일 하나를 읽어 인터페이스를 만들고 주소·경로·DNS 를 붙입니다[2]. 커널 모듈이 없으면 wg-quick 은 사용자 공간 구현(wireguard-go)으로 대신 인터페이스를 만듭니다[4]. 설정 파일에는 이 시스템의 개인 키와 상대 (Peer) 의 공개 키, 상대 주소 (Endpoint), 터널로 보낼 대역 (AllowedIPs) 이 적혀 있습니다[1]. WireGuard 자체는 연결 기록 파일을 쓰지 않습니다. 마지막 핸드셰이크 시각과 주고받은 바이트 수는 실행 중인 인터페이스의 상태라서 실행 중일 때 `wg show` 로만 볼 수 있습니다[1][5].

OpenVPN 은 사용자 공간 데몬입니다. 설정 파일에 상대 서버 (`remote`) 나 서버 쪽 주소 대역 (`server`) 을 적고, 실행하면 로그 줄을 내보냅니다[7][18]. 서버는 접속한 클라이언트 목록을 상태 파일 (status file) 에 주기적으로 다시 쓰고[7], 클라이언트 이름과 가상 IP 의 짝을 따로 저장할 수도 있습니다[7].

두 VPN 모두 NetworkManager 연결 프로필로 만들 수도 있습니다. 이 경우 설정은 NetworkManager 의 연결 파일에 들어가고, 연결·해제는 NetworkManager 감사 기록과 디스패처 이벤트로 남습니다[13][14].

## 위치와 버전별 차이

| 흔적 | 경로·이름 | 남는 곳 |
|---|---|---|
| wg-quick 설정 | `/etc/wireguard/IFACE.conf`. 파일 이름이 곧 인터페이스 이름입니다. `/etc/wireguard/` 를 먼저 찾고 그다음 배포판별 경로를 찾습니다[2] | 디스크 |
| wg-quick 유닛 | `wg-quick@IFACE.service`, `WantedBy=multi-user.target wg-quick.target`[3] | 디스크(켜 둔 링크) |
| OpenVPN 클라이언트 설정 | `/etc/openvpn/client/NAME.conf`, 유닛 `openvpn-client@NAME`[6] | 디스크 |
| OpenVPN 서버 설정 | `/etc/openvpn/server/NAME.conf`, 유닛 `openvpn-server@NAME`[6] | 디스크 |
| OpenVPN 서버 상태 파일 | `/run/openvpn-server/status-NAME.log`(유닛 기본값)[6] | 라이브·메모리 |
| OpenVPN 가상 IP 저장 파일 | 설정의 `ifconfig-pool-persist` 가 가리키는 파일[7] | 디스크 |
| NetworkManager 연결 파일 | `/etc/NetworkManager/system-connections/`[10] | 디스크 |
| Ubuntu 23.10 이후 NM 연결 | `/etc/netplan/90-NM-UUID.yaml`[15] | 디스크 |
| 실행 중 터널 상태 | `wg show all dump`, `ip link show`, `nmcli connection show`[1][19] | 라이브 |

OpenVPN 이 2.4 부터 함께 배포하는 유닛은 클라이언트와 서버를 나눠, 클라이언트 설정은 `/etc/openvpn/client`, 서버 설정은 `/etc/openvpn/server` 에서 찾습니다[6]. 설정 파일은 확장자가 `.conf` 여야 합니다[6]. 이 유닛 이름이 아닌 `openvpn@NAME` 으로 돌리는 설정은 `/etc/openvpn/` 바로 아래에 있을 수 있어서, dissect.target 은 `/etc/openvpn/` 아래 `*.conf`·`*.ovpn` 을 하위 폴더까지 모두 훑습니다[18]. Ubuntu 24.04 와 RHEL 9 의 패키지가 이 유닛을 고쳐 배포하는지는 검체의 `/usr/lib/systemd/system/openvpn-client@.service`·`openvpn-server@.service` 를 열어 `ExecStart=` 줄을 확인하면 됩니다.

서버 유닛의 상태 파일 경로 `%t/openvpn-server/` 에서 `%t` 는 런타임 폴더라 시스템 유닛에서는 `/run` 이고, tmpfiles 설정이 `/run/openvpn-client` 와 `/run/openvpn-server` 를 root 소유 0710 으로 만듭니다[6]. `/run` 은 부팅 때 비워지는 tmpfs 라서 꺼진 시스템의 디스크 이미지에는 이 상태 파일이 없습니다([디렉터리 구조와 주요 경로](../../01-foundations/filesystem/fhs-paths.md) 참고).

Ubuntu 23.10 이후에는 NetworkManager 가 새 연결을 `.nmconnection` 대신 `/etc/netplan/90-NM-UUID.yaml` 로 저장합니다[15]. netplan 이 모르는 OpenVPN 같은 연결은 `nm-devices` 아래 `passthrough` 에 `vpn.remote`, `vpn.service-type` 같은 NetworkManager 키를 그대로 둡니다[15]. 이 이관 방식과 두 배포판의 네트워크 설정 차이는 [네트워크 설정](network-config.md) 에서 다룹니다.

## 구조

### WireGuard 설정 파일

INI 형식이고, `[Interface]` 절은 하나, `[Peer]` 절은 여러 개 올 수 있습니다[1]. `#` 부터 줄 끝까지는 주석입니다[1].

| 절 | 키 | 뜻 |
|---|---|---|
| Interface | `PrivateKey` | base64 개인 키, 필수[1] |
| Interface | `ListenPort`, `FwMark` | 받는 포트, 나가는 패킷 표시값[1] |
| Interface | `Address`, `DNS`, `MTU`, `Table` | wg-quick 이 더한 키. 인터페이스 주소, DNS 서버(또는 검색 도메인), MTU, 경로 표[2] |
| Interface | `PreUp`, `PostUp`, `PreDown`, `PostDown` | wg-quick 이 bash 로 실행하는 명령. `%i` 는 인터페이스 이름으로 바뀜[2] |
| Interface | `SaveConfig` | `true` 면 내려갈 때 현재 상태로 파일을 다시 씀[2] |
| Peer | `PublicKey` | 상대 공개 키, 필수[1] |
| Peer | `PresharedKey` | 대칭 키, 선택[1] |
| Peer | `AllowedIPs` | 쉼표로 나눈 대역 목록, 여러 번 쓸 수 있음[1] |
| Peer | `Endpoint` | 상대 IP 또는 호스트 이름과 포트[1] |
| Peer | `PersistentKeepalive` | 1~65535 초 간격, 기본은 꺼짐[1] |

아래는 wg(8)·wg-quick(8) 형식으로 만든 예시입니다. 키와 주소는 지어낸 값입니다.

```
[Interface]
Address = 10.66.0.2/24
DNS = 10.66.0.1
PrivateKey = (base64 개인 키)
PostUp = /usr/local/bin/example-hook.sh %i

[Peer]
PublicKey = (base64 공개 키)
AllowedIPs = 0.0.0.0/0
Endpoint = 203.0.113.10:51820
```

`AllowedIPs` 에 기본 경로(`0.0.0.0/0` 또는 `::/0`)가 있으면 wg-quick 은 모든 통신을 터널로 돌리려고 정책 경로 규칙을 더합니다[2]. 이때 fwmark 가 없으면 51820 번부터 빈 경로 표 번호를 골라 fwmark 로 쓰고, `ip rule` 과 방화벽 규칙을 추가합니다[4]. iptables 규칙에는 `-m comment --comment "wg-quick(8) rule for IFACE"` 주석이 붙고, nft 를 쓰면 `wg-quick-IFACE` 라는 표를 만듭니다[4]. 이 표지는 실행 중인 방화벽 규칙에만 있고, 규칙 목록을 읽는 법은 [방화벽](firewall.md) 에서 다룹니다.

NetworkManager 로 만든 WireGuard 연결은 연결 파일의 `[wireguard]` 절에 `private-key`(256비트 base64)·`private-key-flags`·`listen-port`·`fwmark`·`mtu`·`peer-routes` 를 두고[11], 상대마다 `[wireguard-peer.공개키]` 절을 둡니다[12]. `private-key-flags` 에 따라 개인 키를 파일 대신 키 보관함에 둘 수 있습니다[16].

### OpenVPN 설정 파일

한 줄에 옵션 하나를 쓰는 텍스트입니다. 분석에 쓰는 키는 클라이언트의 `client`·`remote`, 서버의 `local`·`port`·`server`·`topology`·`ifconfig-pool-persist`·`push`·`client-to-client`·`duplicate-cn`, 공통의 `proto`·`dev`·`ca`·`cert`·`key`·`tls-auth`·`status`·`log` 입니다[18]. dissect.target 은 `client` 키가 있으면 클라이언트로, 없으면 서버로 나누고, 값이 없을 때 `proto` 는 udp, `port` 는 1194, `local` 은 0.0.0.0 으로 채웁니다[18]. 인증서와 키는 파일 경로 대신 `<ca>`·`<key>` 같은 인라인 블록으로 설정 파일 안에 들어 있을 수 있습니다[18].

NetworkManager 로 만든 OpenVPN 연결은 `[connection]` 의 `type=vpn`, `[vpn]` 의 `service-type=org.freedesktop.NetworkManager.openvpn` 으로 알아보고, 같은 절에 `remote`·`port`·`username`·`ca`·`cipher`·`connection-type`·`password-flags` 가 들어갑니다[10]. 저장한 비밀번호 같은 비밀 값은 `[vpn-secrets]` 절에 있습니다[12].

### OpenVPN 상태 파일

`--status file n` 을 주면 n 초마다(기본 60초) 파일을 다시 씁니다[7]. 여러 클라이언트를 받는 서버에서는 클라이언트 목록과 경로 표가 들어가고, `--status-version` 으로 형식을 고릅니다[7]. 클라이언트나 1:1 모드에서는 송수신 통계가 들어갑니다[7].

| 판 | 머리 줄 | 클라이언트 줄의 칸 |
|---|---|---|
| 1 | `OpenVPN CLIENT LIST`, `Updated,시각`[8] | Common Name, Real Address, Bytes Received, Bytes Sent, Connected Since[7][8] |
| 2(쉼표)·3(탭) | `TITLE`, `TIME,현지 시각,epoch`[8] | Common Name, Real Address, Virtual Address, Virtual IPv6 Address, Bytes Received, Bytes Sent, Connected Since, Connected Since (time_t), Username, Client ID, Peer ID, Data Channel Cipher[7][8] |

2·3판은 줄 머리가 `HEADER`, `CLIENT_LIST`, `ROUTING_TABLE`, `GLOBAL_STATS`, `END` 로 나뉩니다[8]. 경로 표 줄의 칸은 Virtual Address, Common Name, Real Address, Last Ref, Last Ref (time_t) 입니다[8]. 업스트림 서버 유닛은 `--status-version 2` 를 씁니다[6]. 아래는 2판 형식으로 만든 예시입니다.

```
TITLE,OpenVPN 2.x.x ...
TIME,2026-03-14 09:30:05,1773448205
HEADER,CLIENT_LIST,Common Name,Real Address,Virtual Address,Virtual IPv6 Address,Bytes Received,Bytes Sent,Connected Since,Connected Since (time_t),Username,Client ID,Peer ID,Data Channel Cipher
CLIENT_LIST,laptop01,198.51.100.23:51234,10.8.0.6,,184320,902144,2026-03-14 09:12:40,1773447160,user01,3,0,AES-256-GCM
HEADER,ROUTING_TABLE,Virtual Address,Common Name,Real Address,Last Ref,Last Ref (time_t)
ROUTING_TABLE,10.8.0.6,laptop01,198.51.100.23:51234,2026-03-14 09:29:58,1773448198
END
```

`--ifconfig-pool-persist file [seconds]` 를 쓰면 서버는 시작할 때, 끝날 때, 그리고 기본 600초마다 `Common-Name,IP-address` 꼴의 쉼표 줄을 파일에 씁니다[7]. 클라이언트 이름과 가상 IP 의 오래 가는 짝이라서, 상태 파일이 사라진 뒤에도 어느 이름이 어느 가상 IP 를 받았는지 알 수 있습니다.

### 로그 줄

wg-quick 은 실행하는 명령마다 앞에 `[#] ` 를 붙여 표준 오류로 찍고, PreUp·PostUp 같은 훅 명령도 같은 꼴로 찍습니다[4]. 유닛의 표준 오류는 따로 정하지 않으면 표준 출력과 같은 곳으로 가고, 표준 출력의 기본값은 저널입니다[17]. 그래서 `wg-quick@wg0.service` 로 올린 터널은 저널에 `[#] ip link add dev wg0 type wireguard`(만든 예시) 같은 줄을 남깁니다. `[#] ` 줄에는 `PostUp` 으로 실행한 명령이 그대로 찍히므로 설정 파일을 나중에 고쳤더라도 당시 실행한 명령을 볼 수 있습니다[4].

OpenVPN 은 상대와 연결이 맺어지면 `Peer Connection Initiated with` 뒤에 상대 주소를 붙인 줄을 찍고, 상대 인증서의 이름(Common Name)을 알면 앞에 `[이름] ` 이 붙습니다[9]. 초기화가 끝나면 `Initialization Sequence Completed` 를 찍습니다[9]. 로그 양은 `--verb n` 으로 정하고, 기본은 1, 권장은 3 입니다[7].

## 증거로서 의미

### 증명하는 것

- 설정 파일이 있으면 이 시스템이 어느 상대 주소(`Endpoint`·`remote`)와 터널을 맺도록 설정됐고, 터널에 어떤 가상 주소와 대역을 붙이도록 했는지 알 수 있습니다[1][2][18].
- 유닛 켜기 링크가 있으면 부팅 때 터널을 자동으로 올리도록 설정됐다는 뜻입니다[3][6].
- 저널에 wg-quick 의 `[#]` 줄이나 OpenVPN 의 `Initialization Sequence Completed` 줄이 있으면 그 시각에 터널을 올리는 과정이 돌았다는 뜻입니다[4][9].
- 서버 상태 파일이 있으면 어느 클라이언트 이름이 어느 실제 주소에서 붙어 어떤 가상 IP 를 받았고 언제부터 붙어 있었는지를 보여 줍니다[8]. 가상 IP 저장 파일은 이름과 가상 IP 의 짝을 보여 줍니다[7].
- `PostUp` 같은 훅이 있으면 터널을 올릴 때마다 그 명령이 실행되도록 설정됐다는 뜻입니다[2].

### 증명하지 못하는 것

- 설정 파일만으로는 실제로 연결했는지, 언제 연결했는지를 알 수 없습니다. WireGuard 에는 연결 기록 파일이 없습니다.
- `wg-quick up` 이 끝났다는 줄은 인터페이스를 만들었다는 뜻일 뿐, 상대와 핸드셰이크가 됐다는 뜻이 아닙니다. 핸드셰이크 여부는 실행 중 `latest-handshake` 값으로만 볼 수 있습니다[1][5].
- 터널 안으로 무엇이 오갔는지는 이 흔적들로 알 수 없습니다. 상태 파일의 바이트 수는 양만 보여 줍니다[8].
- 상태 파일의 `Real Address` 는 서버가 본 출발 주소라서 NAT 뒤의 실제 사용자 기기 주소가 아닐 수 있습니다.
- 클라이언트 이름(Common Name)은 인증서에 적힌 이름이고, 누가 그 인증서를 썼는지는 따로 밝혀야 합니다.

## 시각 해석

| 기록 | 시각의 뜻 | 기준 |
|---|---|---|
| 저널 항목 | 줄을 받은 시각 | [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 참고 |
| OpenVPN 로그 줄(유닛 실행) | 자체 시각 없음. 유닛이 `--suppress-timestamps` 로 실행하므로 저널 시각만 있음[6][7] | 저널과 같음 |
| 상태 파일 `TIME`·`Updated` | 파일을 마지막으로 다시 쓴 시각[8] | 문자열은 현지 시각, 2·3판의 옆 칸은 epoch 초[8] |
| 상태 파일 `Connected Since` | 서버가 그 클라이언트 인스턴스를 만든 시각[8] | 위와 같음 |
| 상태 파일 `Last Ref` | 그 가상 주소 경로를 마지막으로 쓴 시각[8] | 위와 같음 |
| `wg show dump` 의 latest-handshake | 마지막 핸드셰이크 시각[1] | epoch 초[5] |
| WireGuard·OpenVPN 설정 파일 | 파일 안에 시각 없음. 파일 시스템 시각만 있음 | [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 참고 |

상태 파일의 시각 문자열은 `localtime()` 으로 만든 `YYYY-MM-DD HH:MM:SS` 이고 시간대 표기가 없습니다[8]. 2·3판은 같은 줄에 epoch 초를 함께 쓰므로, 문자열과 epoch 의 차이로 서버가 쓰던 시간대를 거꾸로 알 수 있습니다. OpenVPN 을 유닛 없이 `--log` 로 직접 실행했다면 줄 앞에 시각이 붙을 수 있는데, 그 형식은 검체의 로그 파일에서 확인합니다.

`SaveConfig = true` 인 WireGuard 설정 파일은 터널을 내릴 때 wg-quick 이 `.tmp` 파일에 쓴 뒤 이름을 바꿔 덮습니다[4]. 그래서 이 파일의 수정 시각은 사용자가 편집한 때가 아니라 마지막으로 터널을 내린 때일 가능성이 있습니다.

## 함정과 한계

1. `SaveConfig = true` 이면 내려갈 때 `wg showconf` 결과로 파일을 다시 씁니다[4]. `Endpoint` 는 상대가 보낸 인증된 패킷의 가장 최근 출발 주소로 자동으로 바뀌므로[1], 이렇게 다시 쓴 파일의 `Endpoint` 는 처음 적은 주소가 아니라 마지막으로 통신한 상대 주소일 가능성이 있습니다. 반대로 그 전에 손으로 고친 내용은 덮여 사라집니다[2].
2. OpenVPN 의 `--log file` 은 시작할 때 파일을 비웁니다. 이어 쓰려면 `--log-append` 를 씁니다[7]. `--log` 로 설정된 서버를 다시 시작했다면 그 이전 로그는 파일에 없습니다.
3. 서버 상태 파일은 `/run` 아래라 디스크 이미지에는 없습니다[6]. 라이브 응답에서 먼저 복사합니다.
4. dissect.target 의 WireGuard 결과는 `PrivateKey` 를 그대로 담습니다[18]. OpenVPN 결과는 `PRIVATE KEY` 가 든 `key` 값을 기본으로 가리고 `--export-key` 인자를 줄 때만 담습니다[18]. 결과를 보고서에 옮길 때 키 값을 지웁니다.
5. dissect.target 의 WireGuard 파서는 키 이름을 대소문자까지 그대로 찾는데, `PreSharedKey`·`PersistentKeepAlive` 로 찾습니다[18]. wg(8) 표기(`PresharedKey`·`PersistentKeepalive`)[1]로 쓴 파일에서는 이 두 칸이 비어 나올 가능성이 있으므로 빈 칸을 "설정 없음" 으로 읽기 전에 원본 파일을 엽니다.
6. dissect.target 의 WireGuard 파서는 Linux 에서 `/etc/wireguard/*.conf` 만 읽고, NetworkManager 연결 파일, systemd-networkd 의 `.netdev`, 홈 폴더의 설정은 아직 읽지 않습니다[18]. OpenVPN 파서도 Linux 에서는 `/etc/openvpn/` 만 봅니다[18]. 홈 폴더에 둔 `.ovpn`·`.conf` 는 따로 찾습니다.
7. `PreUp`·`PostUp` 에는 아무 명령이나 넣을 수 있고 wg-quick 이 bash 로 실행합니다[2]. VPN 설정이 지속성 수단으로 쓰였을 수 있으므로 훅 명령이 가리키는 파일까지 확인합니다. 지속성 흔적 전반은 [systemd 서비스와 타이머](../persistence/systemd-units.md) 에서 다룹니다.
8. WireGuard 커널 모듈의 디버그 정보는 동적 디버그 (dynamic debug) 를 켜야 dmesg 에 남습니다[1]. 커널 로그에 WireGuard 줄이 없다고 터널이 없었다고 볼 수 없습니다.
9. VPN 이 만드는 임시 가상 인터페이스 연결은 netplan 파일로 남지 않습니다[15]. Ubuntu 의 `/etc/netplan/` 에는 VPN 프로필만 남고, 연결할 때마다 생긴 인터페이스는 남지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번: OpenVPN 상태 파일의 TIME 줄

아래는 2판 상태 파일의 `TIME` 줄을 형식대로 만든 예시입니다. 시각은 지어낸 값입니다.

```
00000000: 5449 4d45 2c32 3032 362d 3033 2d31 3420  TIME,2026-03-14 
00000010: 3039 3a33 303a 3035 2c31 3737 3334 3438  09:30:05,1773448
00000020: 3230 350a                                205.
```

1. 0x00 의 `54 49 4d 45`(`TIME`) 뒤 0x04 의 `2c` 는 칸 구분자입니다. 3판이면 이 자리가 탭 `09` 입니다[8].
2. 0x05 부터 0x17 까지 19바이트가 현지 시각 문자열 `2026-03-14 09:30:05` 입니다[8].
3. 0x18 의 `2c` 다음 0x19 부터 0x22 까지가 epoch 초 `1773448205` 이고, 0x23 의 `0a` 로 줄이 끝납니다[8].
4. `1773448205` 는 UTC 2026-03-14 00:30:05 입니다. 문자열이 09:30:05 이므로 이 서버는 UTC+9 로 시각을 썼습니다.

### 공개 도구로 한 번

```
target-query -f wireguard.config /mnt/evidence/image.E01
target-query -f openvpn.config /mnt/evidence/image.E01
journalctl -D /mnt/evidence/var/log/journal -u 'wg-quick@*' -o short-iso
journalctl -D /mnt/evidence/var/log/journal -u 'openvpn-client@*' -u 'openvpn-server@*' -o short-iso
ls -l /mnt/evidence/etc/systemd/system/multi-user.target.wants/ | grep -E 'wg-quick|openvpn'
grep -rlE '^\[wireguard\]|service-type=org.freedesktop.NetworkManager.openvpn' /mnt/evidence/etc/NetworkManager/system-connections/
```

dissect.target 의 `wireguard.config` 는 `[Interface]` 와 `[Peer]` 를 각각 레코드로 내고, `openvpn.config` 는 클라이언트와 서버를 나눈 레코드를 냅니다[18]. 저널은 유닛 이름으로 거르면 터널을 올리고 내린 순서가 나옵니다. 라이브에서는 `wg show all dump` 를 받습니다. 첫 줄에는 private-key, public-key, listen-port, fwmark 가, 상대마다 한 줄에 public-key, preshared-key, endpoint, allowed-ips, latest-handshake, transfer-rx, transfer-tx, persistent-keepalive 가 탭으로 나뉘어 나옵니다[1]. UAC 는 `/etc` 전체와 `nmcli connection show`·`ip link show` 결과를 받으므로 이 설정 파일들과 실행 중 인터페이스 목록이 수집본에 들어갑니다[19]. 라이브 수집 순서는 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md), 메모리에 남은 인터페이스·프로세스를 보는 법은 [메모리 분석](../../03-techniques/analysis/memory-analysis.md) 에서 다룹니다.

## 교차 검증

| 맞춰 볼 기록 | 확인할 것 |
|---|---|
| 저널의 `wg-quick@`·`openvpn-*@` 줄 ↔ [systemd 서비스와 타이머](../persistence/systemd-units.md) | 유닛을 켠 링크가 있는지, 부팅마다 자동으로 올라왔는지 |
| NetworkManager VPN 프로필 ↔ [네트워크 설정](network-config.md) | NetworkManager 로그·감사 기록의 `connection-activate`·`connection-deactivate`[14] |
| NetworkManager 디스패처 `vpn-up`·`vpn-down`[13] ↔ `dispatcher.d` 스크립트 | VPN 이벤트마다 실행되는 스크립트가 있는지 |
| wg-quick 기본 경로 설정 ↔ [방화벽](firewall.md) | 실행 중 규칙에 `wg-quick(8) rule for IFACE` 주석이나 `wg-quick-IFACE` 표가 있는지[4] |
| `DNS =` 키 ↔ [이름 해석](name-resolution.md) | wg-quick 이 `resolvconf -a tun.IFACE` 로 넣은 DNS 서버[2] |
| 터널 시간대 ↔ [셸 명령 기록](../execution/shell-history/index.md) | `wg-quick up`, `openvpn --config`, `systemctl start openvpn-client@` 같은 명령 |
| 설정 파일 생성 시각 ↔ [dpkg·apt 기록](../packages/dpkg-apt.md)·[rpm·dnf·yum 기록](../packages/rpm-dnf.md) | wireguard-tools·openvpn 패키지를 언제 설치했는지 |
| 상태 파일의 `Real Address` ↔ [인증 로그](../logins/auth-log.md) | 같은 주소에서 들어온 로그인이 있는지 |

여러 기록을 시간순으로 합치는 법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 실습

NIST CFReDS 등에 공개된 Linux 디스크·메모리 이미지로 다음 질문을 풀어 봅니다.

1. `/etc/wireguard/` 와 `/etc/openvpn/` 아래 설정 파일은 몇 개이고, 각 파일의 상대 주소(`Endpoint`·`remote`)는 무엇인가?
2. `SaveConfig = true` 인 WireGuard 설정이 있다면, 파일 수정 시각과 저널의 마지막 `wg-quick down` 줄 시각이 맞는가?
3. 저널에서 `Initialization Sequence Completed` 줄을 부팅별로 뽑으면 OpenVPN 터널을 몇 번 올렸는가?
4. `PostUp`·`PreUp` 에 적힌 명령이 가리키는 파일이 디스크에 남아 있는가? 그 파일의 생성 시각은 언제인가?
5. 서버 설정에 `ifconfig-pool-persist` 가 있다면, 그 파일에 적힌 클라이언트 이름과 가상 IP 는 무엇인가?
6. 메모리 이미지가 있다면 wireguard 인터페이스나 openvpn 프로세스가 남아 있는가?

## 참고 문헌

1. WireGuard wireguard-tools, src/man/wg.8. https://github.com/WireGuard/wireguard-tools/blob/master/src/man/wg.8
2. WireGuard wireguard-tools, src/man/wg-quick.8. https://github.com/WireGuard/wireguard-tools/blob/master/src/man/wg-quick.8
3. WireGuard wireguard-tools, src/systemd/wg-quick@.service. https://github.com/WireGuard/wireguard-tools/blob/master/src/systemd/wg-quick@.service
4. WireGuard wireguard-tools, src/wg-quick/linux.bash. https://github.com/WireGuard/wireguard-tools/blob/master/src/wg-quick/linux.bash
5. WireGuard wireguard-tools, src/show.c. https://github.com/WireGuard/wireguard-tools/blob/master/src/show.c
6. OpenVPN, distro/systemd(openvpn-client@.service.in·openvpn-server@.service.in·tmpfiles-openvpn.conf·README.systemd). https://github.com/OpenVPN/openvpn/tree/master/distro/systemd
7. OpenVPN, doc/man-sections(log-options.rst·generic-options.rst·server-options.rst). https://github.com/OpenVPN/openvpn/tree/master/doc/man-sections
8. OpenVPN, src/openvpn/multi.c·otime.c. https://github.com/OpenVPN/openvpn/blob/master/src/openvpn/multi.c , https://github.com/OpenVPN/openvpn/blob/master/src/openvpn/otime.c
9. OpenVPN, src/openvpn/socket.c·init.c. https://github.com/OpenVPN/openvpn/blob/master/src/openvpn/socket.c , https://github.com/OpenVPN/openvpn/blob/master/src/openvpn/init.c
10. NetworkManager, man/nm-settings-keyfile.xsl. https://github.com/NetworkManager/NetworkManager/blob/main/man/nm-settings-keyfile.xsl
11. NetworkManager, src/libnmc-setting/settings-docs.h.in. https://github.com/NetworkManager/NetworkManager/blob/main/src/libnmc-setting/settings-docs.h.in
12. NetworkManager, src/libnm-core-intern/nm-keyfile-utils.h. https://github.com/NetworkManager/NetworkManager/blob/main/src/libnm-core-intern/nm-keyfile-utils.h
13. NetworkManager, man/NetworkManager-dispatcher.xml. https://github.com/NetworkManager/NetworkManager/blob/main/man/NetworkManager-dispatcher.xml
14. NetworkManager, src/core/nm-audit-manager.h. https://github.com/NetworkManager/NetworkManager/blob/main/src/core/nm-audit-manager.h
15. netplan, doc/netplan-everywhere.md. https://github.com/canonical/netplan/blob/main/doc/netplan-everywhere.md
16. netplan, doc/security.md. https://github.com/canonical/netplan/blob/main/doc/security.md
17. systemd, man/systemd.exec.xml. https://github.com/systemd/systemd/blob/main/man/systemd.exec.xml
18. fox-it dissect.target, dissect/target/plugins/apps/vpn/wireguard.py·openvpn.py. https://github.com/fox-it/dissect.target/tree/main/dissect/target/plugins/apps/vpn
19. UAC, artifacts(files/system/etc.yaml·live_response/network/nmcli.yaml·live_response/network/ip.yaml). https://github.com/tclahr/uac/tree/main/artifacts
