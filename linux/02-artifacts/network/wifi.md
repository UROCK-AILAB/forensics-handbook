---
title: "Wi-Fi 연결 기록"
parent: "아티팩트 · 네트워크"
nav_order: 720
---

# Wi-Fi 연결 기록 (Wi-Fi)

Linux 데스크톱의 Wi-Fi 기록은 NetworkManager 의 연결 프로필(어느 SSID 를 설정했나), `/var/lib/NetworkManager/timestamps`(마지막으로 연결된 시각), `/var/lib/NetworkManager/seen-bssids`(실제로 붙은 AP 의 BSSID), 그리고 NetworkManager 로그 줄에 나뉘어 남습니다.

## 무엇을 기록하나 · 왜 생기나

Ubuntu·RHEL 데스크톱에서 Wi-Fi 는 보통 NetworkManager 가 관리합니다. 사용자가 새 무선 네트워크에 접속하면 NetworkManager 는 그 네트워크를 연결 프로필 (connection profile) 로 저장하고, 다음부터 같은 SSID 가 보이면 이 프로필로 자동 연결합니다. 프로필에는 SSID, 보안 방식, 경우에 따라 암호까지 들어갑니다[1][2].

연결 시각과 접속한 AP 는 프로필 파일에 적지 않습니다. 프로필을 연결할 때마다 고쳐 쓰면 `/etc` 를 계속 다시 쓰게 되므로, NetworkManager 는 실제 시각과 BSSID 목록을 `/var/lib/NetworkManager` 아래의 따로 된 파일 두 개에 둡니다[5]. 두 파일 모두 연결 프로필의 UUID 를 키로 씁니다[4][5]. 그래서 분석은 프로필에서 UUID 와 SSID 를 얻고, 그 UUID 로 두 파일과 로그를 잇는 순서로 합니다.

프로필 파일의 위치와 일반 구조, NetworkManager 로그 줄 형식, 감사 기록은 [네트워크 설정](network-config.md)에서 다룹니다. 이 페이지는 Wi-Fi 에만 해당하는 내용을 다룹니다.

## 위치와 버전별 차이

| 기록 | 위치 | 성격 |
|---|---|---|
| 연결 프로필 (keyfile) | `/etc/NetworkManager/system-connections/*.nmconnection` | 디스크에 남음. root 전용 권한[1] |
| netplan 에 저장한 프로필 | `/etc/netplan/90-NM-<UUID>.yaml` | Ubuntu 23.10 이후. 디스크에 남음[12] |
| netplan 이 만든 NM 프로필 | `/run/NetworkManager/system-connections/netplan-<ID>-<SSID>.nmconnection` | tmpfs. 전원을 끈 이미지에는 없음[15] |
| 이관 전 사본 | `/root/NetworkManager.bak/system-connections/` | Ubuntu 23.10 이후 설치 때 만든 사본[12] |
| 마지막 연결 시각 | `/var/lib/NetworkManager/timestamps` | 디스크에 남음[4] |
| 붙은 AP 목록 | `/var/lib/NetworkManager/seen-bssids` | 디스크에 남음[4][2] |
| iwd 형식 사본 | iwd 상태 폴더(보통 `/var/lib/iwd`) | NetworkManager 가 iwd 를 백엔드로 쓸 때[3] |
| 로그 | systemd 저널, rsyslog 파일 | NetworkManager 가 남긴 줄[9][10] |

배포판에 따라 프로필이 있는 곳이 다릅니다.

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| Wi-Fi 프로필 | `/etc/netplan/90-NM-<UUID>.yaml` 이 원본이고, 이것으로 `/run/NetworkManager/system-connections/` 에 임시 NM 프로필을 새로 만듦[12] | `/etc/NetworkManager/system-connections/*.nmconnection`. 옛 `ifcfg` 형식이 남아 있는지는 [네트워크 설정](network-config.md) 참고 |
| timestamps·seen-bssids | `/var/lib/NetworkManager/` | `/var/lib/NetworkManager/` |

Ubuntu 23.10 이후 NetworkManager 는 임시 연결이 아닌 새 연결을 `.nmconnection` 으로 두지 않고 netplan YAML 로 저장합니다[12]. 그래서 Ubuntu 24.04 데스크톱 이미지는 `/etc/NetworkManager/system-connections/` 가 비어 있어도 Wi-Fi 를 쓰지 않았다는 뜻이 아닙니다. 이관 과정은 [네트워크 설정](network-config.md)에서 다룹니다.

## 구조

### keyfile 의 Wi-Fi 프로필

keyfile 은 ini 형식이고, Wi-Fi 설정 그룹은 `[wifi]`(정식 이름 `802-11-wireless`), 보안 설정 그룹은 `[wifi-security]`(정식 이름 `802-11-wireless-security`)입니다[1]. 아래는 명세의 예시 구조로 만든 예시입니다.

```
[connection]
id=ExampleNet
uuid=3f0c9a52-1d2e-4b6a-8c11-5e7d20a1b0c4
type=wifi

[wifi]
ssid=ExampleNet
mode=infrastructure
security=802-11-wireless-security

[wifi-security]
key-mgmt=wpa-psk
psk=example-passphrase
```

분석에 쓰는 키는 아래와 같습니다.

| 그룹 | 키 | 뜻 |
|---|---|---|
| `[connection]` | `id`, `uuid`, `type=wifi` | 프로필 이름, 다른 파일과 잇는 UUID, 종류[1] |
| `[wifi]` | `ssid` | 네트워크 이름. 반드시 있음[2] |
| `[wifi]` | `mode` | `infrastructure`, `mesh`, `adhoc`, `ap`. 비어 있으면 infrastructure[2] |
| `[wifi]` | `hidden` | 참이면 SSID 를 알리지 않는 숨긴 네트워크[2] |
| `[wifi]` | `bssid` | 특정 AP 에만 붙도록 고정한 값[2] |
| `[wifi]` | `cloned-mac-address` | `preserve`, `permanent`, `random`, `stable`, `stable-ssid` 또는 MAC 주소[2] |
| `[wifi]` | `mac-address-randomization` | `default`, `never`, `always`[2] |
| `[wifi-security]` | `key-mgmt` | `none`, `ieee8021x`, `owe`, `wpa-psk`, `sae`, `wpa-eap`, `wpa-eap-suite-b-192`[2] |
| `[wifi-security]` | `psk`, `psk-flags` | 미리 나눈 키 (Pre-Shared Key) 와 그 비밀 플래그[1][2] |
| `[802-1x]` | `eap`, `identity`, `ca-cert`, `password-flags` | 기업용(WPA-EAP) 인증 설정[1] |

`psk` 는 WPA-PSK 이면 8~63자 ASCII 암호나 64자 헥스 키이고, WPA3-Personal(SAE) 이면 길이 제한이 없습니다[2]. 비밀 플래그가 0 이면 시스템이 비밀을 보관하므로 `psk=` 가 keyfile 에 평문으로 들어가고, 1 이면 사용자 세션의 비밀 에이전트가, 2 이면 매번 묻고 저장하지 않습니다[1]. `mode=ap` 인 프로필은 이 컴퓨터가 핫스폿 (hotspot) 을 만든 설정입니다[2].

### netplan YAML 의 Wi-Fi 프로필

netplan 형식에서 Wi-Fi 는 `network:` → `wifis:` → 인터페이스 이름 → `access-points:` 아래에 SSID 를 키로 둡니다[13]. SSID 아래에는 `password`, `mode`(`infrastructure`, `ap`, `adhoc`), `bssid`, `band`, `channel`, `hidden` 이 올 수 있습니다[13]. NetworkManager 가 쓰는 프로필 이름과 UUID 는 `networkmanager:` 아래 `name`, `uuid` 에 둡니다[13]. netplan 은 Wi-Fi 암호를 YAML 에 다른 설정과 함께 저장하므로 파일 권한을 root 전용(600)으로 두라고 권합니다[14].

netplan 생성기는 이 YAML 로 `/run/NetworkManager/system-connections/netplan-<ID>-<SSID>.nmconnection` 을 만들고(파일 이름의 ID 와 SSID 는 URI 이스케이프한 값), 파일 안의 `[wifi-security] psk` 에 암호를 옮겨 적습니다[15]. 프로필 이름을 정하지 않았으면 `netplan-<ID>-<SSID>` 를 이름으로 씁니다[15]. NetworkManager 대신 systemd-networkd 로 Wi-Fi 를 쓰면 `/run/netplan/wpa-<ID>.conf` 에 wpa_supplicant 설정을 만듭니다[15].

### timestamps

`/var/lib/NetworkManager/timestamps` 는 GLib 키 파일 (GKeyFile) 형식이고, `[timestamps]` 그룹 하나에 `UUID=epoch초` 줄이 프로필마다 하나씩 있습니다[4][5][6].

```
[timestamps]
3f0c9a52-1d2e-4b6a-8c11-5e7d20a1b0c4=1767225600
```

(만든 예시)

값의 뜻은 세 가지입니다. 0 이 아니면 그 프로필이 활성화에 성공한 적이 있고, 0 이면 활성화를 시도했지만 실패한 것이며, 키가 없으면 시도한 적이 없는 것입니다[8].

### seen-bssids

`/var/lib/NetworkManager/seen-bssids` 도 GKeyFile 형식이고, `[seen-bssids]` 그룹에 `UUID=BSSID목록` 줄이 있습니다[4][6]. 목록 구분자는 쉼표이고[6], GLib 은 목록을 쓸 때 항목마다 뒤에 구분자를 붙이므로 줄 끝에도 쉼표가 남습니다[7].

```
[seen-bssids]
3f0c9a52-1d2e-4b6a-8c11-5e7d20a1b0c4=02:00:5e:10:00:02,02:00:5e:10:00:01,
```

(만든 예시)

프로필 하나에 BSSID 는 30개까지 남습니다[5]. 새로 붙은 BSSID 는 목록 맨 앞에 넣고, 30개를 넘으면 맨 뒤(가장 오래된 것)를 뺍니다[5]. 이미 있는 BSSID 에 다시 붙으면 맨 앞으로 옮깁니다[5]. 그래서 목록 순서는 최근에 붙은 순서입니다. NetworkManager 는 장치가 연결 완료 상태이고 적용된 설정을 고치지 않았을 때, 인프라 모드 AP 에 대해서만 BSSID 를 더합니다[9]. Ad-Hoc 망의 BSSID 는 남지 않습니다[9].

### 로그 줄

Wi-Fi 연결에 성공하면 NetworkManager 는 info 수준으로 아래 줄을 남기고, 끝에 SSID 를 붙입니다[9]. 핫스폿을 만들었으면 `Connected to wireless network` 대신 `Started Wi-Fi Hotspot` 이 들어갑니다[9].

```
<info>  [1767225600.1234] device (wlp2s0): Activation: (wifi) Stage 2 of 5 (Device Configure) successful. Connected to wireless network ExampleNet
```

(만든 예시. 대괄호 값은 epoch 초와 1/10000 초[10])

그 밖에 연결 과정에서 남는 줄은 아래와 같습니다[9].

| 줄 | 뜻 |
|---|---|
| `Activation: (wifi) connection '%s' has security, and secrets exist.  No new secrets needed.` | 저장된 비밀로 연결 시도 |
| `Activation: (wifi) connection '%s' requires no security.  No secrets needed.` | 암호 없는 망 |
| `Activation: (wifi) access point '%s' has security, but secrets are required.` | 비밀이 없어 요청 |
| `Activation: (wifi) psk mismatch reported by supplicant, ...` | 암호 불일치 |
| `Activation: (wifi) SAE password mismatch reported by supplicant, asking for new key` | WPA3 암호 불일치 |
| `Activation: (wifi) association took too long` | 연결 시간 초과 |
| `Activation: (wifi) disconnected during association, ...` | 연결 중 끊김 |

저널 백엔드로 남긴 줄에는 `NM_DEVICE=`(인터페이스 이름)와 `NM_CONNECTION=`(프로필 UUID) 필드가 붙습니다[10]. 줄 형식과 감사 기록(`op=connection-activate`, 무선을 켜고 끈 `op=radio-control`)[11]은 [네트워크 설정](network-config.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것**

- 프로필이 있으면 그 SSID 를 이 컴퓨터에 설정한 적이 있습니다. `mode=ap` 이면 이 컴퓨터가 그 이름으로 핫스폿을 만들도록 설정한 것입니다.
- timestamps 값이 0 이 아니면 그 프로필이 적어도 한 번 활성화에 성공했고, 값은 마지막으로 연결이 완료되었거나 끊긴 시각, 또는 NetworkManager 가 장치 상태를 저장한 시각입니다[8].
- seen-bssids 에 BSSID 가 있으면 그 프로필로 연결된 상태에서 그 AP 에 붙은 적이 있습니다[9]. 목록 순서로 최근 순서까지 말할 수 있습니다[5].
- 저널이 남아 있으면 `NM_CONNECTION=` 으로 한 프로필의 연결 성공·실패 줄을 시각과 함께 모을 수 있습니다[10].

**증명하지 못하는 것**

- timestamps 에는 마지막 값 하나만 남습니다. 연결 횟수나 전체 연결 기간은 알 수 없습니다.
- timestamps 값만으로는 연결을 시작한 시각인지 끊긴 시각인지 가를 수 없습니다. 두 경우 모두 값을 바꾸기 때문입니다[8]. 로그 줄로 나눕니다.
- seen-bssids 는 주변에 보이기만 한 AP 를 담지 않습니다[9]. 스캔 결과 목록이 아닙니다.
- BSSID 와 SSID 만으로 물리적 위치는 나오지 않습니다. 위치는 외부 자료와 맞춰야 하는 추정입니다.
- 프로필을 지우면 NetworkManager 가 timestamps 와 seen-bssids 에서 그 UUID 줄을 함께 지웁니다[4]. 지운 프로필의 연결 기록은 이 두 파일에 없습니다.

보고서에는 "UUID 3f0c9a52-… 인 'ExampleNet' 프로필이 2026-01-01 00:00:00 UTC 에 마지막으로 연결 상태가 바뀐 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다(만든 예시).

## 시각 해석

timestamps 값은 `time()` 으로 얻은 epoch 초라서 시간대가 없는 UTC 기준 값입니다[8]. 1767225600 은 2026-01-01 00:00:00 UTC 입니다. 컴퓨터 시계가 틀렸으면 값도 틀립니다.

코드에서 이 값을 바꾸는 곳은 세 곳입니다. 활성 연결이 연결 완료 상태로 들어가거나 그 상태에서 벗어날 때 현재 시각을 적고, NetworkManager 가 모든 장치 상태를 기록할 때 활성 연결을 "내리는 것처럼" 현재 시각을 적으며, 활성화가 실패했는데 아직 값이 없으면 0 을 적습니다[8]. 속성 설명문은 활성 중에 "주기적으로" 갱신한다고 적어 코드와 다릅니다[2]. 파일은 값이 바뀔 때마다 바로 쓰지 않고, 다른 할 일이 없을 때(유휴 시간) 몰아서 씁니다[4]. 전원을 갑자기 끊으면 마지막 값이 파일에 반영되지 않았을 가능성이 있습니다.

keyfile 의 `[connection] timestamp=` 는 이 파일과 다른 값입니다. NetworkManager 는 `/etc` 를 주기적으로 다시 쓰지 않으려고 실제 시각을 이 속성에 넣지 않습니다[5]. keyfile 의 값은 비어 있거나 오래된 값일 수 있으므로 마지막 연결 시각은 timestamps 파일에서 읽습니다.

seen-bssids 에는 시각이 없습니다. 파일 수정 시각은 어느 프로필이든 마지막으로 목록이 바뀐 때일 뿐입니다.

로그 줄의 대괄호 값은 `g_get_real_time()` 으로 얻은 epoch 초와 1/10000 초입니다[10]. 저널과 rsyslog 파일의 시각 해석은 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md), [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md), 값 변환은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)을 봅니다.

## 함정과 한계

- **빈 system-connections.** Ubuntu 24.04 는 Wi-Fi 프로필을 `/etc/netplan/90-NM-*.yaml` 에 둡니다[12]. `/run` 쪽 `.nmconnection` 은 전원을 끈 이미지에 없습니다.
- **평문 암호.** 플래그가 0 이면 keyfile 의 `psk=` 에[1], netplan 이면 YAML 의 `password:` 에[14] 암호가 평문으로 있습니다. 보고서나 도구 출력에 옮길 때 가립니다.
- **무작위 MAC.** `cloned-mac-address` 가 `random`, `stable`, `stable-ssid` 이면 AP 가 본 MAC 은 하드웨어 MAC 과 다릅니다[2]. `random` 은 연결할 때마다 바뀝니다[2]. AP 쪽 기록과 맞출 때 이 값을 먼저 봅니다.
- **권한이 넓은 keyfile.** NetworkManager 는 root 말고 다른 사용자가 읽거나 쓸 수 있는 keyfile 을 무시합니다[1]. 권한이 넓은 파일은 NetworkManager 가 쓰지 않았을 가능성이 있어서, 누가 손으로 넣었는지 따져 볼 단서가 됩니다.
- **파일 이름과 SSID.** keyfile 파일 이름과 `id=` 는 사용자가 정한 이름이고 SSID 와 다를 수 있습니다. SSID 는 `[wifi] ssid=` 에서 읽습니다.
- **도구가 읽지 않는 값.** dissect.target 의 NetworkManager 해석은 keyfile 의 주소·인터페이스·UUID 와 `[connection] timestamp` 를 읽고, SSID·timestamps 파일·seen-bssids 파일은 읽지 않습니다[16]. 이 도구가 보여 주는 마지막 연결 시각은 keyfile 값이라 timestamps 파일과 다를 수 있습니다. 세 파일 모두 텍스트이므로 직접 읽습니다.
- **흔적 지우기.** 프로필을 지우면 두 파일의 줄도 사라집니다[4]. 이때는 로그 줄, 감사 기록의 `connection-delete`[11], Ubuntu 의 `/root/NetworkManager.bak/` 사본[12]에서 흔적을 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

timestamps 파일을 헥스로 보면 아래와 같습니다. 형식에 맞춰 만든 예시이고 값은 지어낸 것입니다.

```
00000000  5b 74 69 6d 65 73 74 61  6d 70 73 5d 0a 33 66 30  |[timestamps].3f0|
00000010  63 39 61 35 32 2d 31 64  32 65 2d 34 62 36 61 2d  |c9a52-1d2e-4b6a-|
00000020  38 63 31 31 2d 35 65 37  64 32 30 61 31 62 30 63  |8c11-5e7d20a1b0c|
00000030  34 3d 31 37 36 37 32 32  35 36 30 30 0a           |4=1767225600.|
```

1. 첫 줄 `[timestamps]` 가 그룹 이름입니다. seen-bssids 파일은 이 자리에 `[seen-bssids]` 가 옵니다.
2. `=` 앞의 36글자가 프로필 UUID 입니다. 이 값으로 keyfile 의 `uuid=` 나 netplan 파일 이름 `90-NM-<UUID>.yaml` 을 찾습니다.
3. `=` 뒤의 `1767225600` 은 이진 값이 아니라 10진수 글자입니다. epoch 초로 읽으면 2026-01-01 00:00:00 UTC 입니다.

### 공개 도구로 한 번

- **사후 이미지**: UAC 는 `/var/lib/NetworkManager` 폴더와 `/etc` 전체를 모으므로 `/etc/netplan` 까지 들어옵니다[17]. ForensicArtifacts 의 `LinuxNetworkManager` 는 `/etc/NetworkManager/system-connections` 와 `/var/lib/NetworkManager/*` 를 모으도록 정의하고 `/etc/netplan` 은 넣지 않으므로, Ubuntu 24.04 에서는 따로 챙깁니다[18]. 모은 뒤 `grep -r '^ssid=' system-connections/` 로 SSID 를 뽑고, timestamps·seen-bssids 줄을 UUID 로 잇습니다.
- **라이브**: `nmcli connection show` 는 메모리와 디스크에 있는 연결 프로필 목록을, `nmcli radio all` 은 무선 스위치 상태를 보여 줍니다[17].
- **로그**: `journalctl NM_CONNECTION=UUID` 로 한 프로필의 줄만 고르거나[10], `Connected to wireless network` 로 연결 성공 줄을 찾습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [네트워크 설정](network-config.md) | 같은 UUID 의 DHCP 임대 파일(받은 주소), NetworkManager 감사 기록의 uid·pid |
| [이름 해석](name-resolution.md) | 그 망에서 받은 DNS 서버 |
| [VPN](vpn.md) | Wi-Fi 연결 뒤 곧바로 올린 터널 |
| [로그인 기록](../logins/wtmp-btmp-lastlog.md) | 연결 시각에 로그인해 있던 계정 |
| [부팅과 종료 기록](../system-info/boot-shutdown.md) | 가장 늦은 timestamps 값과 마지막 부팅·종료 시각의 선후 |

여러 기록의 시각을 한 줄로 늘어놓는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md)를 봅니다.

## 실습

공개 Linux 디스크 이미지(NIST CFReDS 등)나 직접 만든 노트북 가상 머신 이미지로 아래 질문을 풀어 봅니다.

1. 프로필은 `/etc/NetworkManager/system-connections/` 와 `/etc/netplan/90-NM-*.yaml` 중 어디에 있는가? SSID 는 모두 몇 개인가?
2. timestamps 에서 값이 0 인 UUID 가 있는가? 그 프로필의 연결 실패 줄이 저널에 남아 있는가?
3. seen-bssids 목록 맨 앞의 BSSID 는 무엇이고, 같은 프로필에 BSSID 가 여러 개라면 무엇을 뜻하는가?
4. 가장 늦은 timestamps 값은 마지막 부팅·종료 기록과 어떤 관계인가?
5. 평문 `psk=` 나 `password:` 가 있는 프로필이 있는가? 보고서에는 어떻게 적을 것인가?

## 참고 문헌

1. NetworkManager, man/nm-settings-keyfile.xsl — https://github.com/NetworkManager/NetworkManager/blob/main/man/nm-settings-keyfile.xsl
2. NetworkManager, src/libnmc-setting/settings-docs.h.in — https://github.com/NetworkManager/NetworkManager/blob/main/src/libnmc-setting/settings-docs.h.in
3. NetworkManager, man/NetworkManager.conf.xml — https://github.com/NetworkManager/NetworkManager/blob/main/man/NetworkManager.conf.xml
4. NetworkManager, src/core/settings/nm-settings.c — https://github.com/NetworkManager/NetworkManager/blob/main/src/core/settings/nm-settings.c
5. NetworkManager, src/core/settings/nm-settings-connection.c·nm-settings-connection.h — https://github.com/NetworkManager/NetworkManager/tree/main/src/core/settings
6. NetworkManager, src/libnm-glib-aux/nm-keyfile-aux.c — https://github.com/NetworkManager/NetworkManager/blob/main/src/libnm-glib-aux/nm-keyfile-aux.c
7. GLib, glib/gkeyfile.c — https://github.com/GNOME/glib/blob/main/glib/gkeyfile.c
8. NetworkManager, src/core/nm-active-connection.c·nm-manager.c·devices/nm-device.c — https://github.com/NetworkManager/NetworkManager/blob/main/src/core/nm-active-connection.c , https://github.com/NetworkManager/NetworkManager/blob/main/src/core/nm-manager.c , https://github.com/NetworkManager/NetworkManager/blob/main/src/core/devices/nm-device.c
9. NetworkManager, src/core/devices/wifi/nm-device-wifi.c — https://github.com/NetworkManager/NetworkManager/blob/main/src/core/devices/wifi/nm-device-wifi.c
10. NetworkManager, src/libnm-log-core/nm-logging.c — https://github.com/NetworkManager/NetworkManager/blob/main/src/libnm-log-core/nm-logging.c
11. NetworkManager, src/core/nm-audit-manager.h — https://github.com/NetworkManager/NetworkManager/blob/main/src/core/nm-audit-manager.h
12. netplan, doc/netplan-everywhere.md — https://github.com/canonical/netplan/blob/main/doc/netplan-everywhere.md
13. netplan, doc/netplan-yaml.md — https://github.com/canonical/netplan/blob/main/doc/netplan-yaml.md
14. netplan, doc/security.md — https://github.com/canonical/netplan/blob/main/doc/security.md
15. netplan, src/nm.c·networkd.c — https://github.com/canonical/netplan/tree/main/src
16. dissect.target, plugins/os/unix/linux/network.py — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/network.py
17. UAC, artifacts/files/system/networkmanager.yaml·etc.yaml·live_response/network/nmcli.yaml — https://github.com/tclahr/uac/tree/main/artifacts
18. ForensicArtifacts, artifacts/data/linux.yaml — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
