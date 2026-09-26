---
title: "네트워크 설정"
parent: "아티팩트 · 네트워크"
nav_order: 690
---

# 네트워크 설정 (NetworkManager·netplan)

어떤 네트워크 프로필이 설정돼 있었는지는 NetworkManager 의 연결 프로필 파일이나 netplan YAML 에 남습니다. 그 프로필로 주소를 받았는지, 누가 언제 프로필을 바꾸거나 켰는지는 `/var/lib/NetworkManager` 아래의 상태 파일과 NetworkManager 로그에 남습니다.

## 무엇을 기록하나 · 왜 생기나

NetworkManager 는 연결 프로필 (connection profile) 을 단위로 네트워크를 설정합니다. 프로필 하나에는 이름(`id`), UUID, 연결 종류, 고정 주소·DNS·게이트웨이, 묶을 인터페이스나 MAC 주소가 들어갑니다[3]. 사용자가 GNOME 설정 창이나 `nmcli` 로 유선·무선·VPN 연결을 만들면 NetworkManager 가 이 프로필을 디스크에 저장합니다. 저장을 맡는 것은 설정 플러그인이고, keyfile 플러그인은 늘 켜져 있어 다른 플러그인이 저장하지 못하는 프로필을 모두 저장합니다[1][3].

Ubuntu 는 netplan 이라는 자체 설정 형식을 함께 씁니다. netplan 은 YAML 파일을 읽어 NetworkManager 나 systemd-networkd 가 읽을 설정을 `/run` 아래에 만들어 주는 생성기입니다[13][16]. Ubuntu 23.10 이후에는 NetworkManager 가 새 프로필을 keyfile 대신 netplan YAML 로 저장합니다[12]. 그래서 Ubuntu 24.04 데스크톱과 RHEL 9 는 같은 NetworkManager 를 쓰면서도 프로필이 남는 곳이 다릅니다.

설정 파일 말고도 NetworkManager 는 몇 가지 상태를 따로 적습니다. 내장 DHCP 클라이언트가 받은 주소는 임대 파일에[7], 프로필마다 마지막으로 활성화된 시각은 `timestamps` 파일에[6] 남습니다. D-Bus 로 들어온 프로필 추가·삭제·활성화 요청은 감사 기록 (audit record) 으로 로그에 남습니다[9].

## 위치와 버전별 차이

| 기록 | 위치 | 성격 |
|---|---|---|
| 데몬 설정 | `/etc/NetworkManager/NetworkManager.conf`, `/etc/NetworkManager/conf.d/*.conf`, `/usr/lib/NetworkManager/conf.d/*.conf`, `/run/NetworkManager/conf.d/*.conf` | `/run` 쪽은 부팅마다 두는 설정[1] |
| NetworkManager 가 스스로 고친 설정 | `/var/lib/NetworkManager/NetworkManager-intern.conf` | 마지막에 읽혀 사용자 설정을 덮음[1] |
| 연결 프로필(keyfile) | `/etc/NetworkManager/system-connections/*.nmconnection`, `/usr/lib/NetworkManager/system-connections/`, `/run/NetworkManager/system-connections/` | root 전용 권한[3][5] |
| netplan 설정 | `/etc/netplan/*.yaml`, `/lib/netplan/*.yaml`, `/run/netplan/*.yaml` | 권장 권한 600[13][15] |
| netplan 이 만든 설정 | `/run/NetworkManager/system-connections/netplan-*.nmconnection`, `/run/NetworkManager/conf.d/netplan.conf`, `/run/systemd/network/10-netplan-*` | 휘발성, 부팅 때 생성기가 다시 만듦[12][13][16] |
| systemd-networkd 설정 | `/etc/systemd/network`, `/run/systemd/network`, `/usr/lib/systemd/network` 의 `.network`·`.netdev` | [17] |
| DHCP 임대(내장 클라이언트) | `/var/lib/NetworkManager/internal-UUID-인터페이스.lease` | 마지막으로 받은 IPv4 주소[7] |
| 마지막 활성화 시각 | `/var/lib/NetworkManager/timestamps` | UUID 별 epoch 초[6] |
| 기계 식별 값 | `/var/lib/NetworkManager/secret_key` | 안정 MAC·IPv6 주소 생성의 씨앗[2] |
| 디스패처 스크립트 | `/etc/NetworkManager/dispatcher.d`, `/usr/lib/NetworkManager/dispatcher.d` | 네트워크 이벤트마다 실행[4] |
| 로그 | systemd 저널 또는 syslog | 백엔드는 `[logging] backend`[1] |

배포판에 따라 프로필이 남는 곳은 아래와 같이 나뉩니다.

| 항목 | Ubuntu 24.04 (데스크톱) | RHEL 9 |
|---|---|---|
| 새 프로필 저장 위치 | `/etc/netplan/90-NM-UUID.yaml`[12] | `plugins=` 목록이 정함. keyfile 이면 `/etc/NetworkManager/system-connections/*.nmconnection`[1] |
| 실제로 NetworkManager 가 읽는 파일 | `/run/NetworkManager/system-connections/netplan-NM-UUID.nmconnection`[12][16] | 위와 같음 |
| 옛 형식 | 이관 전 사본 `/root/NetworkManager.bak/system-connections/`[12] | `/etc/sysconfig/network-scripts/ifcfg-*` 가 남아 있을 수 있음[18] |
| 옛 Debian 방식 | `/etc/network/interfaces` (ifupdown 플러그인이 읽기 전용으로 읽음)[1] | — |

ifcfg-rh 플러그인은 NetworkManager 1.44 에서 폐기 예고됐고 1.60 에서 제거됐습니다. 최근 Fedora·RHEL 에서는 이미 꺼져 있고, 남은 ifcfg 프로필은 `nmcli connection migrate` 로 keyfile 로 옮기게 돼 있습니다[10]. RHEL 9 시스템에서 `ifcfg-*` 와 `.nmconnection` 이 함께 보이면 `NetworkManager.conf` 와 `conf.d` 의 `plugins=` 값, 설치된 NetworkManager 판을 함께 보고 어느 쪽을 읽었는지 판별합니다.

## 구조

### 데몬 설정의 읽는 순서

NetworkManager 는 `/usr/lib/NetworkManager/conf.d` 를 가장 먼저 읽고, `/run/NetworkManager/conf.d` 를 그다음에, `NetworkManager.conf` 를 그 뒤에, `/etc/NetworkManager/conf.d` 를 그다음에 읽고, `NetworkManager-intern.conf` 를 맨 마지막에 읽습니다. 한 폴더 안에서는 파일 이름을 바이트 단위로 비교한 순서로 읽기 때문에 `10-a.conf` 가 `9-a.conf` 보다 먼저 읽힙니다. 같은 키가 여러 파일에 있으면 나중에 읽은 값이 쓰입니다[1]. `NetworkManager-intern.conf` 는 사용자가 고치는 파일이 아니고, NetworkManager 가 D-Bus 요청 등으로 바꾼 값을 적어 두는 파일입니다[1].

형식은 `[main]` 같은 절 아래 `plugins=keyfile` 처럼 키와 값을 적는 key file 이고, 목록 값은 `plugins+=` 와 `plugins-=` 로 더하고 뺍니다[1]. 흔적 해석에 쓸모 있는 키는 아래와 같습니다.

| 절·키 | 뜻 |
|---|---|
| `[main] plugins` | 프로필을 읽고 쓸 설정 플러그인 목록[1] |
| `[keyfile] path` | keyfile 을 두는 폴더. 기본 `/etc/NetworkManager/system-connections`[1] |
| `[keyfile] rename` | 프로필 이름을 바꿀 때 파일 이름도 바꿀지. 기본 false[1] |
| `[logging] level`, `domains` | 로그 수준. 기본은 INFO[1] |
| `[logging] backend` | `syslog` 또는 `journal`[1] |
| `[logging] audit` | 감사 기록을 auditd 에도 보낼지[1] |

### 연결 프로필(keyfile)

keyfile 은 GLib key file 형식의 텍스트이고, 절 이름은 설정 이름, 키는 속성 이름입니다. `802-3-ethernet` 은 `ethernet`, `802-11-wireless` 는 `wifi`, `802-11-wireless-security` 는 `wifi-security` 로 줄여 써도 됩니다. 주소·경로·라우팅 규칙처럼 여러 개인 값은 `address1`, `address2` 처럼 번호 붙은 키로 하나씩 적습니다[3]. 파일 확장자는 `.nmconnection` 입니다[5].

아래는 유선 프로필을 명세에 맞춰 만든 예시입니다. 이름·UUID·주소는 지어낸 값입니다.

```
[connection]
id=사무실 유선
uuid=0b7f4a2e-1111-4c3d-9e8f-000000000001
type=ethernet
interface-name=enp1s0
autoconnect=true

[ethernet]
mac-address=02:00:5e:10:00:01

[ipv4]
method=manual
address1=192.0.2.15/24
gateway=192.0.2.1
dns=198.51.100.53;

[ipv6]
method=auto
```

비밀 값에는 `psk-flags`, `password-flags` 처럼 `-flags` 키가 짝으로 붙습니다. 값은 0~7 이고, 0 은 NetworkManager 가 보관, 1 은 사용자 세션의 비밀 에이전트가 보관, 2 는 저장하지 않고 매번 물음, 4 는 필요 없음을 더한 값입니다[3]. 플래그가 0 이면 비밀 값이 keyfile 안에 평문으로 들어가고, 그래서 keyfile 플러그인은 root 말고 다른 사용자가 읽거나 쓸 수 있는 파일을 무시합니다[3]. Wi-Fi 암호가 남는 모양은 [Wi-Fi 연결 기록](wifi.md)에서 다룹니다.

`/usr/lib/NetworkManager/system-connections` 에 있는 프로필을 지우면 NetworkManager 는 그 파일을 지우지 않고 `/etc/NetworkManager/system-connections` 에 `UUID.nmmeta` 라는 파일을 만듭니다. 같은 UUID 의 다른 파일을 가려야 할 때는 `/run/NetworkManager/system-connections` 에 만들기도 합니다[5][6]. 이 파일이 `/dev/null` 을 가리키는 심볼릭 링크이면 그 UUID 프로필을 지웠다는 표시(tombstone)입니다[5].

### netplan YAML

netplan 파일의 맨 위는 `network:` 이고 그 아래에 `version`(2), `renderer`(`networkd` 또는 `NetworkManager`, 적지 않으면 `networkd`), 장치 종류별 목록(`ethernets`, `wifis`, `bonds`, `bridges`, `vlans`, `tunnels`, `nm-devices` 등)이 옵니다[14]. NetworkManager 가 저장한 파일에서는 장치 정의 이름이 `NM-UUID` 이고, `networkmanager:` 아래에 `uuid`, `name`, `passthrough` 가 붙습니다. `passthrough` 는 netplan 이 모르는 NetworkManager 키를 그대로 담아 두는 자리이고, 여기 적힌 값은 만들어지는 `.nmconnection` 에 그대로 옮겨집니다[12]. OpenVPN 클라이언트처럼 netplan 이 지원하지 않는 연결은 `nm-devices` 아래에 `vpn.remote`, `vpn.service-type` 같은 키를 `passthrough` 로 담습니다[12].

아래는 NetworkManager 가 저장한 파일 모양을 따라 만든 예시입니다.

```yaml
network:
  version: 2
  ethernets:
    NM-0b7f4a2e-1111-4c3d-9e8f-000000000001:
      renderer: NetworkManager
      match:
        name: "enp1s0"
      addresses:
        - "192.0.2.15/24"
      nameservers:
        addresses:
          - 198.51.100.53
      networkmanager:
        uuid: "0b7f4a2e-1111-4c3d-9e8f-000000000001"
        name: "사무실 유선"
        passthrough:
          ipv6.method: "auto"
```

netplan 은 `/lib/netplan`, `/etc/netplan`, `/run/netplan` 세 곳을 읽습니다. 이름이 같은 파일은 `/run` 이 `/etc` 를, `/etc` 가 `/lib` 를 가리고, 이름이 다른 파일은 폴더와 상관없이 이름의 사전 순서로 읽어 뒤 파일이 앞 파일의 값을 덮거나 더합니다[13]. 파일 하나만 보고 최종 설정을 단정하지 말고 세 폴더의 파일을 모두 모아 순서대로 겹쳐 봅니다.

netplan 생성기는 renderer 에 따라 결과를 다른 곳에 씁니다. NetworkManager 쪽은 `/run/NetworkManager/system-connections/netplan-ID.nmconnection`(Wi-Fi 는 `netplan-ID-SSID.nmconnection`)과 `/run/NetworkManager/conf.d/netplan.conf` 이고, networkd 쪽은 `/run/systemd/network/10-netplan-ID.*`, networkd 로 Wi-Fi 를 쓰면 `/run/netplan/wpa-ID.conf` 입니다[16]. 부팅 때 생성기로 돌 때는 구문 오류를 기본으로 무시하므로, 오류가 있는 YAML 은 일부 설정이 빠진 채 적용됐을 수 있습니다[13].

### DHCP 임대 파일

NetworkManager 내장 DHCP 클라이언트(`internal`)의 임대 파일 이름은 `internal-UUID-인터페이스.lease` 이고, IPv6 는 `internal6-` 로 시작합니다. 평소에는 `/var/lib/NetworkManager` 에 쓰고, 같은 이름이 `/run/NetworkManager` 에 있으면 그쪽을 씁니다[7]. 내용은 두 줄뿐입니다[7].

```
# This is private data. Do not parse.
ADDRESS=192.0.2.15
```

파일 이름의 UUID 가 프로필 UUID 이므로, 이 파일로 어느 프로필이 어느 인터페이스에서 마지막으로 어떤 IPv4 주소를 받았는지 이어 볼 수 있습니다. dhclient 를 쓴 시스템은 `/var/lib/dhclient/*.leases` 나 `/var/lib/dhcp/*.leases` 에 `lease { ... }` 블록으로 남습니다[18].

### 로그 줄

NetworkManager 로그 한 줄은 수준 문자열, 대괄호 안 시각, 메시지 순서입니다. 수준 문자열은 `<trace>`, `<debug>`, `<info>`, `<warn>`, `<error>` 를 7칸에 맞춰 적고, 대괄호 안은 epoch 초와 소수점 아래 네 자리입니다[8]. 장치에 딸린 줄은 `device (인터페이스):` 로 시작합니다. 아래는 형식에 맞춰 만든 예시이고, DHCP 줄의 메시지 모양은 dissect.target 이 찾는 모양[18]을 따랐습니다.

```
<info>  [1767225600.2345] dhcp4 (enp1s0): state changed new lease, address=192.0.2.15
<info>  [1767225612.5678] audit: op="connection-update" uuid="0b7f4a2e-1111-4c3d-9e8f-000000000001" name="사무실 유선" pid=2345 uid=1000 result="success"
```

백엔드가 journal 이면 NetworkManager 는 `MESSAGE` 말고도 `NM_LOG_LEVEL`, `NM_LOG_DOMAINS`, `CODE_FUNC`, `TIMESTAMP_MONOTONIC`, `TIMESTAMP_BOOTTIME` 을 붙이고, 장치·프로필에 딸린 줄에는 `NM_DEVICE=인터페이스` 와 `NM_CONNECTION=UUID` 를 붙입니다[8]. 그래서 `journalctl NM_CONNECTION=UUID` 로 한 프로필의 줄만 고를 수 있습니다. 저널 필터 쓰는 법은 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md)을 봅니다.

감사 기록은 `audit:` 접두어를 달고 INFO 수준으로 로그에 남고, `[logging] audit` 이 참이면 auditd 에도 `USYS_CONFIG` 형식으로 갑니다[1][9]. 필드는 `op=`, `uuid=`, `name=`, `args=`, `pid=`, `uid=`, `result=` 순서이고, 로그 쪽에만 `reason=` 이 붙습니다[9]. `op` 값은 `connection-add`, `connection-delete`, `connection-update`, `connection-activate`, `connection-add-activate`, `connection-deactivate`, `connection-clear-secrets`, `connections-reload`, `networking-control`, `radio-control`, `hostname-save`, `device-disconnect` 등입니다[9]. `pid` 와 `uid` 는 D-Bus 로 요청한 프로세스의 값입니다. auditd 레코드 읽는 법은 [감사 로그 형식](../../01-foundations/logging/auditd-format.md)을 봅니다.

DHCP 줄의 모양은 프로그램과 판마다 다릅니다. dissect.target 은 NetworkManager 의 `dhcp4 (eth0): option ip_address => '...'`(옛 형식)과 `dhcp4 (eth0): state changed new lease, address=...`(새 형식), systemd-networkd 의 `IFACE: DHCPv4 address ADDR/PREFIX via GW`, dhclient 의 `bound to ADDR -- renewal in N seconds.` 를 찾습니다[18].

## 증거로서 의미

**증명하는 것**

- 수집 시점에 어떤 프로필(이름·UUID·종류·고정 주소·DNS·게이트웨이·MAC)이 설정돼 있었는지.
- 임대 파일이 있으면, 그 UUID 프로필이 그 인터페이스에서 DHCP 로 IPv4 주소를 받은 적이 있고 마지막 주소가 무엇이었는지[7].
- 감사 기록이 있으면, 어느 uid·pid 가 언제 어느 프로필을 추가·수정·삭제·활성화했는지와 그 요청이 성공했는지[9].
- Ubuntu 23.10 이후 시스템에서 `/root/NetworkManager.bak/system-connections/` 가 있으면, netplan 이관 전에 keyfile 로 저장된 프로필이 있었다는 것[12].

**증명하지 못하는 것**

- 설정 파일만으로는 그 프로필을 실제로 썼는지, 언제 썼는지 알 수 없습니다. 실제 활성화 시각은 `timestamps` 파일과 로그로 봅니다.
- 임대 파일은 마지막 주소 한 개만 담습니다. 주소를 받은 시각과 횟수는 로그로 봅니다.
- 전원을 끈 뒤 뜬 이미지에는 `/run` 아래의 생성된 프로필과 `conf.d` 조각이 없습니다. Ubuntu 24.04 에서 NetworkManager 가 실제로 읽은 `.nmconnection` 은 `/etc/netplan` 의 YAML 에서 다시 만들어 봐야 합니다.
- 감사 기록의 uid 는 D-Bus 요청을 보낸 프로세스의 uid 입니다. 그 계정을 누가 쓰고 있었는지는 [누가 그 명령을 실행했나](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 좁힙니다.

보고서에는 "UUID 0b7f... 프로필이 192.0.2.15 고정 주소로 설정돼 있었고, 로그에 uid 1000 이 이 프로필을 수정한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

| 값 | 기준 | 바뀌는 때 |
|---|---|---|
| NetworkManager 로그 대괄호 값 | Unix epoch 초(UTC), 소수 넷째 자리까지 | 줄을 쓸 때의 시스템 시계 시각[8] |
| `timestamps` 파일 값 | Unix epoch 초(UTC) | 활성 연결이 ACTIVATED 가 되거나 ACTIVATED 에서 벗어날 때[6] |
| keyfile 의 `[connection] timestamp=` | Unix epoch 초(UTC) | 연결할 때마다 바뀌지 않음(아래 함정)[6] |
| 설정 파일·임대 파일 mtime | 파일 시스템 시각 | 마지막으로 파일을 다시 쓴 때 |

로그 대괄호 값은 NetworkManager 가 `g_get_real_time()` 으로 읽은 시스템 시계 값이라서, 시스템 시계를 바꾸면 그 값도 따라 움직입니다[8]. 저널 백엔드라면 같은 줄의 저널 자체 시각과 `TIMESTAMP_BOOTTIME` 을 함께 봅니다. epoch 값 바꾸는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)을, `timestamps` 파일의 형식과 값의 뜻은 [Wi-Fi 연결 기록](wifi.md)을 봅니다.

## 함정과 한계

1. **keyfile 의 `timestamp=` 는 마지막 연결 시각이 아닙니다.** NetworkManager 는 `/etc` 를 주기적으로 다시 쓰지 않으려고 실제 시각을 속성에 넣지 않고 `/var/lib/NetworkManager/timestamps` 에만 둡니다[6]. D-Bus `GetSettings` 응답에는 이 내부 값을 바꿔 넣으므로[6], 라이브에서 본 `nmcli connection show` 의 `connection.timestamp` 와 keyfile 의 값이 다를 가능성이 있습니다. 속성 설명문은 "활성 중 주기적으로 갱신" 이라고 적고 있지만[11], 코드는 활성 연결이 ACTIVATED 상태로 들어가고 나올 때 이 값을 고칩니다[6].
2. **dissect.target 은 keyfile 의 `timestamp` 를 `last_connected` 로 보여 줍니다[18].** 위 이유로 이 값은 비어 있거나 오래된 값일 수 있으니 `timestamps` 파일과 로그로 맞춰 봅니다.
3. **Ubuntu 24.04 에서는 `/etc/NetworkManager/system-connections/` 가 비어 있을 수 있습니다.** 프로필이 `/etc/netplan/90-NM-*.yaml` 에 있고, 이관할 때 원래 keyfile 은 지워집니다[12]. 이 이관은 프로필을 더하거나 고칠 때도 뒤에서 일어나므로[12], YAML 의 mtime 은 사용자가 설정을 바꾼 때가 아니라 NetworkManager 가 다시 쓴 때일 수 있습니다.
4. **파일 이름과 프로필 이름은 다를 수 있습니다.** `[keyfile] rename` 기본값이 false 라서 프로필 이름을 바꿔도 파일 이름은 그대로입니다[1]. 프로필은 파일 이름이 아니라 `uuid=` 로 이어 봅니다.
5. **권한이 넓은 keyfile 은 NetworkManager 가 무시합니다[3].** root 가 아닌 사용자가 읽을 수 있는 `.nmconnection` 이 있다면 NetworkManager 가 쓰지 않은 파일이고, 누가 손으로 넣었는지 따져 볼 단서가 됩니다.
6. **VPN 같은 임시 연결은 netplan 파일로 남지 않습니다[12].** VPN 흔적은 [VPN](vpn.md)을 봅니다.
7. **도구마다 보는 범위가 다릅니다.** dissect.target 의 netplan 해석은 `/etc/netplan/*.yaml` 에서 `addresses`, `dhcp4`, `gateway4` 만 보고, NetworkManager 임대 파일은 파일 이름을 `-` 로 잘라 마지막 조각을 인터페이스 이름으로 씁니다[18]. 인터페이스 이름에 `-` 가 들어 있으면 이름이 잘려 나옵니다. ForensicArtifacts 의 `LinuxNetworkManager` 는 `conf.d` 항목에 man 페이지의 자리 표시 이름 `name.conf` 를 그대로 적고 있어서, 실제 조각 파일은 이 항목만으로 모이지 않을 수 있습니다[20]. UAC 는 `/etc` 전체와 `/var/lib/NetworkManager` 를 모으고[19], `/run/NetworkManager` 는 파일 수집 목록에 없습니다.
8. **디스패처 스크립트는 네트워크 이벤트마다 실행됩니다.** NetworkManager-dispatcher 는 `/etc/NetworkManager/dispatcher.d` 와 `/usr/lib/NetworkManager/dispatcher.d` 의 스크립트를 이름 순서로 실행하고, 이름이 같으면 `/etc` 쪽이 이깁니다. 스크립트는 인터페이스 이름과 동작(`up`, `down`, `vpn-up`, `dhcp4-change`, `connectivity-change` 등)을 인자로 받고, root 소유의 일반 실행 파일이어야 하며 group·other 쓰기 권한이나 setuid 가 없어야 합니다. `pre-up`·`pre-down` 용은 `pre-up.d`·`pre-down.d` 에 둡니다[4]. 패키지가 설치한 적 없는 스크립트가 여기 있으면 지속성 흔적으로 봅니다. 찾는 순서는 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md)를 봅니다. ifupdown 의 `/etc/network/if-up.d/*`, `/etc/network/if-down.d/*` 도 인터페이스가 오르내릴 때 실행되는 스크립트라서 같은 방법으로 봅니다[20].
9. **`secret_key` 를 지우면 안정 MAC 과 IPv6 주소가 바뀝니다.** 이 파일과 `/etc/machine-id` 가 `ethernet.cloned-mac-address=stable`, `ipv6.addr-gen-mode=stable` 의 씨앗이라서[2], 다른 기록의 MAC·IPv6 주소를 이 기기와 맞춰 볼 때 이 파일이 바뀐 적이 있는지도 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

설정 파일은 모두 텍스트라서 헥스로 볼 일이 많지 않지만, 임대 파일처럼 짧은 파일은 줄 끝과 숨은 문자를 확인할 때 헥스로 봅니다. 아래는 앞의 형식[7]으로 만든 예시입니다.

```
00000000: 2320 5468 6973 2069 7320 7072 6976 6174  # This is privat
00000010: 6520 6461 7461 2e20 446f 206e 6f74 2070  e data. Do not p
00000020: 6172 7365 2e0a 4144 4452 4553 533d 3139  arse..ADDRESS=19
00000030: 322e 302e 322e 3135 0a                   2.0.2.15.
```

1. 0x00 의 `23` 은 `#` 이고, 0x25 의 `0a` 까지가 첫 줄 주석입니다.
2. 0x26 부터 `ADDRESS=` 뒤에 `192.0.2.15` 가 ASCII 로 이어지고 0x38 의 `0a` 로 끝납니다.
3. 파일 이름에서 `internal-` 뒤 36자가 UUID, 그 뒤 `-` 다음이 인터페이스 이름입니다. 이 UUID 를 keyfile 의 `uuid=`, netplan 의 `NM-UUID`, `timestamps` 의 키, 저널의 `NM_CONNECTION=` 과 맞춥니다.

### 공개 도구로 한 번

- **사후 이미지**: dissect.target 의 `network.interfaces` 는 NetworkManager keyfile, systemd-networkd 설정, dhclient·NetworkManager 임대 파일을 모아 인터페이스 목록을 만들고, `--syslog` 를 주면 syslog·저널 앞부분(기본 1000줄)에서 DHCP 줄도 찾습니다. `network.dhcp` 는 이 가운데 임대 파일에서 나온 항목(종류 `dhcp`)만 거릅니다. netplan·ifcfg·`/etc/network/interfaces` 는 이 목록을 만들 때 읽지 않습니다[18]. 결과에 SSID·`passthrough` 는 나오지 않으므로 원본 파일을 텍스트로 함께 읽습니다.
- **Ubuntu 24.04 이미지**: `/etc/netplan/90-NM-*.yaml` 을 모두 모아 `network.ethernets`·`wifis`·`nm-devices` 아래의 `networkmanager.uuid` 와 `name` 을 표로 만듭니다. 이관 전 사본 `/root/NetworkManager.bak/system-connections/` 와 비교하면 이관 뒤 바뀐 프로필이 드러납니다.
- **로그**: 저널이면 `journalctl -u NetworkManager` 로 전체를, `journalctl NM_CONNECTION=UUID` 로 한 프로필을 봅니다. 감사 기록은 `audit:` 으로, DHCP 는 `dhcp4 (` 로 좁힙니다. rsyslog 파일 위치는 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)를 봅니다.
- **라이브**: UAC 는 `nmcli`, `nmcli connection show`, `nmcli device show`, `nmcli device status`, `nmcli general status`, `nmcli radio all`, `ip addr show`, `ip link show`, `ip neighbor show`, `ip route show` 결과를 모읍니다[19]. `/run/NetworkManager` 와 `/run/netplan` 은 라이브 수집 때 따로 복사해야 남습니다. 절차는 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md)을 봅니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [Wi-Fi 연결 기록](wifi.md) | `timestamps`·`seen-bssids` 의 UUID 와 프로필 UUID |
| [이름 해석](name-resolution.md) | 프로필의 `dns=` 와 `/etc/resolv.conf`, NetworkManager 가 쓴 resolv.conf 머리 주석 |
| [방화벽](firewall.md) | 인터페이스 이름과 주소가 방화벽 규칙·로그의 `IN=`·`OUT=` 과 맞는지 |
| [VPN](vpn.md) | `type=vpn` 프로필, netplan `nm-devices` 의 `vpn.*` 키 |
| [감사 로그 형식](../../01-foundations/logging/auditd-format.md) | `USYS_CONFIG` 레코드의 uid 와 로그인 기록 |
| [dpkg·apt 기록](../packages/dpkg-apt.md) | network-manager 패키지 설치·갱신 시각과 netplan 이관 시각 |
| [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md) | `hostname-save` 감사 기록과 호스트 이름 변경 |

## 실습

공개 Linux 디스크 이미지(NIST CFReDS 등)나 직접 만든 가상 머신 이미지로 아래 질문을 풀어 봅니다.

1. 이 이미지의 프로필은 `/etc/NetworkManager/system-connections`, `/etc/netplan`, `/etc/sysconfig/network-scripts` 가운데 어디에 있는가? `plugins=` 값은 무엇인가?
2. 각 프로필의 UUID 에 해당하는 `internal-UUID-인터페이스.lease` 가 있는가? 마지막 주소는 무엇인가?
3. keyfile 의 `timestamp=` 와 `/var/lib/NetworkManager/timestamps` 의 같은 UUID 값이 다른가? 어느 쪽이 로그의 활성화 줄과 맞는가?
4. 로그에 `audit: op="connection-add"` 나 `connection-delete` 줄이 있는가? uid 는 어느 계정이고, 그 시각 전후에 무엇이 있었는가?
5. `dispatcher.d` 에 패키지 목록에 없는 스크립트가 있는가? 파일 소유자·권한은 NetworkManager 가 요구하는 조건과 맞는가?

## 참고 문헌

1. NetworkManager, NetworkManager.conf(5) — https://github.com/NetworkManager/NetworkManager/blob/main/man/NetworkManager.conf.xml
2. NetworkManager, NetworkManager(8) — https://github.com/NetworkManager/NetworkManager/blob/main/man/NetworkManager.xml
3. NetworkManager, nm-settings-keyfile(5) — https://github.com/NetworkManager/NetworkManager/blob/main/man/nm-settings-keyfile.xsl
4. NetworkManager, NetworkManager-dispatcher(8) — https://github.com/NetworkManager/NetworkManager/blob/main/man/NetworkManager-dispatcher.xml
5. NetworkManager, keyfile 플러그인 코드(nm-keyfile-internal.h·nms-keyfile-plugin.c·nms-keyfile-utils.c) — https://github.com/NetworkManager/NetworkManager/tree/main/src
6. NetworkManager, src/core/settings/nm-settings.c·nm-settings-connection.c, src/core/nm-active-connection.c — https://github.com/NetworkManager/NetworkManager/tree/main/src/core/settings , https://github.com/NetworkManager/NetworkManager/blob/main/src/core/nm-active-connection.c
7. NetworkManager, src/core/dhcp/nm-dhcp-utils.c·nm-dhcp-nettools.c — https://github.com/NetworkManager/NetworkManager/tree/main/src/core/dhcp
8. NetworkManager, src/libnm-log-core/nm-logging.c, src/libnm-glib-aux/nm-logging-base.c, src/core/devices/nm-device-logging.h — https://github.com/NetworkManager/NetworkManager/blob/main/src/libnm-log-core/nm-logging.c , https://github.com/NetworkManager/NetworkManager/blob/main/src/libnm-glib-aux/nm-logging-base.c , https://github.com/NetworkManager/NetworkManager/blob/main/src/core/devices/nm-device-logging.h
9. NetworkManager, src/core/nm-audit-manager.c·nm-audit-manager.h — https://github.com/NetworkManager/NetworkManager/tree/main/src/core
10. NetworkManager, NEWS(1.44·1.60) — https://github.com/NetworkManager/NetworkManager/blob/main/NEWS
11. NetworkManager, src/libnmc-setting/settings-docs.h.in — https://github.com/NetworkManager/NetworkManager/blob/main/src/libnmc-setting/settings-docs.h.in
12. netplan, doc/netplan-everywhere.md — https://github.com/canonical/netplan/blob/main/doc/netplan-everywhere.md
13. netplan, doc/netplan-generate.md — https://github.com/canonical/netplan/blob/main/doc/netplan-generate.md
14. netplan, doc/netplan-yaml.md — https://github.com/canonical/netplan/blob/main/doc/netplan-yaml.md
15. netplan, doc/security.md — https://github.com/canonical/netplan/blob/main/doc/security.md
16. netplan, src/nm.c·src/networkd.c — https://github.com/canonical/netplan/tree/main/src
17. systemd, systemd-networkd.service(8) — https://github.com/systemd/systemd/blob/main/man/systemd-networkd.service.xml
18. dissect.target, plugins/os/unix/linux/network.py·network_managers.py — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/network.py , https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/network_managers.py
19. UAC, artifacts/files/system/networkmanager.yaml·etc.yaml, live_response/network/nmcli.yaml·ip.yaml — https://github.com/tclahr/uac/tree/main/artifacts
20. ForensicArtifacts, artifacts/data/linux.yaml(LinuxNetworkManager·LinuxIfUpDownScripts) — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
