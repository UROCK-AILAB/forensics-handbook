---
title: "이름 해석"
parent: "아티팩트 · 네트워크"
nav_order: 710
---

# 이름 해석 (hosts·resolv.conf)

`/etc/hosts` 에서 고정된 이름·주소 짝을, `/etc/resolv.conf` 와 그 뒤에 있는 systemd-resolved·NetworkManager 파일에서 기계가 묻던 DNS 서버와 검색 도메인을, `/etc/nsswitch.conf` 에서 둘을 어떤 순서로 쓰는지를 읽습니다.

## 무엇을 기록하나 · 왜 생기나

프로그램이 호스트 이름을 주소로 바꿀 때 C 라이브러리는 `/etc/nsswitch.conf` 의 `hosts:` 줄에 적힌 서비스를 적힌 순서대로 묻고, 결과가 나오면 멈춥니다[3]. `files` 서비스는 `/etc/hosts` 를 읽고, `dns` 서비스는 `/etc/resolv.conf` 에 적힌 네임서버에 질의합니다[3][2]. systemd-resolved 를 쓰는 기계에서는 `resolve` 서비스(nss-resolve)가 이 일을 resolved 에 넘깁니다[6].

`/etc/hosts` 는 관리자가 손으로 고치는 파일입니다. 설치 때 기본 줄이 들어가고, 이후 줄이 늘었다면 누군가 특정 이름을 특정 주소로 고정한 것입니다. 파일을 고치면 보통 곧바로 효과가 나고, 프로그램이 파일 내용을 캐시한 경우만 예외입니다[1]. 그래서 특정 도메인을 다른 주소로 돌리는 변조가 한 줄로 끝나고, 조사에서는 기본 줄이 아닌 줄을 먼저 봅니다.

`/etc/resolv.conf` 는 요즘 사람이 쓰는 경우가 드뭅니다. NetworkManager 나 systemd-resolved 가 네트워크에 붙을 때마다 받은 DNS 서버로 파일을 새로 쓰거나, `/etc/resolv.conf` 자체가 `/run` 아래 파일로 가는 심볼릭 링크 (symbolic link) 입니다[4][9]. 따라서 이 파일에서는 "누가 이 파일을 관리했나" 와 "마지막으로 붙은 네트워크가 준 DNS 설정이 무엇이었나" 를 읽습니다. DNS 서버를 어디서 받았는지는 [네트워크 설정](./network-config.md)에서 다룹니다.

## 위치와 버전별 차이

| 경로 | 담는 것 | 비고 |
|---|---|---|
| `/etc/hosts` | IP 와 이름 짝 | ForensicArtifacts `UnixHostsFile`[13] |
| `/etc/resolv.conf` | 해석기 설정(네임서버·검색 도메인·옵션) | ForensicArtifacts `DNSResolvConfFile`[13]. 일반 파일일 수도, 링크일 수도 있습니다 |
| `/etc/nsswitch.conf` | 조회 순서(`hosts:` 줄) | authselect 를 쓰면 `/etc/authselect/nsswitch.conf` 로 가는 링크입니다[11] |
| `/run/systemd/resolve/stub-resolv.conf` | `nameserver 127.0.0.53` 만 적은 파일 | systemd-resolved 가 씁니다[4][7] |
| `/run/systemd/resolve/resolv.conf` | resolved 가 아는 실제 상위 DNS 서버 | systemd-resolved 가 씁니다[4][7] |
| `/usr/lib/systemd/resolv.conf` | 127.0.0.53 만 적은 고정 파일 | systemd 패키지에 들어 있습니다[4] |
| `/run/NetworkManager/resolv.conf` | NetworkManager 가 만든 resolv.conf | NM 은 설정과 상관없이 항상 이 파일을 씁니다[9][10] |
| `/run/NetworkManager/no-stub-resolv.conf` | 캐시 DNS 플러그인을 쓸 때 원래 서버 목록 | dnsmasq·systemd-resolved·dnsconfd 플러그인일 때[9][10] |
| `/etc/systemd/resolved.conf`, `/etc/systemd/resolved.conf.d/*.conf` | resolved 설정 | `/run/systemd/`, `/usr/local/lib/systemd/`, `/usr/lib/systemd/` 아래 같은 이름도 읽습니다[5] |
| `/etc/hosts.allow`, `/etc/hosts.deny` | 접근 제어 | 이름이 비슷하지만 이름 해석과 관계없는 파일입니다[13] |

`/run` 은 부팅할 때마다 비우는 tmpfs 라서 꺼진 디스크 이미지에는 `/run` 아래 파일이 없습니다([디렉터리 구조와 주요 경로](../../01-foundations/filesystem/fhs-paths.md)).

### resolv.conf 를 관리하는 방식

systemd-resolved 는 `/etc/resolv.conf` 를 다루는 방식 네 가지를 둡니다[4]. `/run/systemd/resolve/stub-resolv.conf` 로 링크하는 방식(권장), `/usr/lib/systemd/resolv.conf` 로 링크하는 방식, `/run/systemd/resolve/resolv.conf` 로 링크해 프로그램이 resolved 를 거치지 않고 상위 서버에 직접 묻게 하는 방식, 다른 패키지가 `/etc/resolv.conf` 를 관리하고 resolved 는 그 파일을 읽기만 하는 방식입니다. resolved 는 `/etc/resolv.conf` 가 앞의 세 파일 가운데 하나로 가는 링크가 아닐 때만 그 파일에서 DNS 서버를 읽습니다[4].

NetworkManager 는 `NetworkManager.conf` 의 `[main]` 절 `dns=` 와 `rc-manager=` 키로 동작을 정합니다[9]. `dns=` 키가 없어도 `/etc/resolv.conf` 가 `/run/systemd/resolve/stub-resolv.conf`, `/run/systemd/resolve/resolv.conf`, `/lib/systemd/resolv.conf`, `/usr/lib/systemd/resolv.conf` 로 가는 링크면 systemd-resolved 모드를 자동으로 고릅니다[9].

| `rc-manager=` 값 | `/etc/resolv.conf` 에 하는 일[9] |
|---|---|
| `symlink` | 일반 파일이거나 없으면 직접 쓰고, 링크면 건드리지 않습니다. 링크가 `/run/NetworkManager/resolv.conf` 를 가리킬 때만 링크를 다시 만듭니다 |
| `file` | 일반 파일로 쓰고, 대상이 있는 링크면 링크 대상 파일을 고칩니다. 있던 링크를 파일로 바꾸지는 않습니다 |
| `resolvconf`, `netconfig` | 해당 프로그램을 실행해 맡깁니다 |
| `unmanaged` | 건드리지 않습니다 |
| `auto` | resolved 모드면 resolved 만 갱신하고, 아니면 resolvconf·netconfig, 마지막으로 `symlink` 를 씁니다 |
| `none` | `symlink` 의 옛 이름입니다 |

`dns=none` 이거나 `/etc/resolv.conf` 에 `chattr +i` 로 변경 불가 속성을 걸어 두면 NM 은 설정과 상관없이 `unmanaged` 로 동작합니다[9].

Ubuntu 24.04 와 RHEL 9 가운데 어느 쪽이 기본으로 어떤 링크를 쓰는지는 배포판 패키지에 달려 있으므로, 대상 시스템에서 `/etc/resolv.conf` 가 링크인지, 링크라면 대상 문자열이 무엇인지부터 봅니다. RHEL 계열처럼 authselect 가 `nsswitch.conf` 를 만드는 기계는 판과 프로필에 따라 `hosts:` 줄이 나오는 곳이 다릅니다. authselect 1.2.x 가지의 `sssd` 프로필 파일에는 `hosts:` 줄이 없고, 프로필이 정하지 않은 줄은 `/etc/authselect/user-nsswitch.conf` 에서 가져옵니다[11]. upstream master 의 `local`·`sssd` 프로필은 `hosts:` 줄에 `files myhostname` 을 먼저 두고, 켠 기능에 따라 libvirt·mDNS 항목을 넣은 뒤 `resolve [!UNAVAIL=return] dns` 를 둡니다[11]. 그래서 분석할 때는 `/etc/nsswitch.conf` 링크 대상 파일의 `hosts:` 줄을 직접 읽습니다.

## 구조

### /etc/hosts

한 줄에 IP 주소 하나를 적고, 그 뒤에 대표 이름과 별칭을 적습니다[1].

```
IP_address canonical_hostname [aliases...]
```

IPv4·IPv6 모두 쓸 수 있고, 필드 사이는 공백이나 탭을 몇 개든 둘 수 있으며, `#` 부터 줄 끝까지는 주석입니다[1]. 호스트 이름은 영숫자·`-`·`.` 만 쓰고 영문자로 시작해 영숫자로 끝나야 합니다[1]. 기계 자신의 FQDN 에는 `127.0.1.1` 을 흔히 씁니다[1].

### /etc/resolv.conf

키워드는 줄 맨 앞에 쓰고 값은 같은 줄에 공백으로 띄워 씁니다[2]. 첫 글자가 `;` 이나 `#` 인 줄은 주석입니다[2].

| 키워드 | 뜻[2] |
|---|---|
| `nameserver` | 질의할 네임서버 주소. 한 줄에 하나, 최대 MAXNS(현재 3)개이고 적힌 순서대로 묻습니다 |
| `search` | 검색 도메인 목록. 여러 줄이면 마지막 줄만 씁니다. glibc 2.25 까지는 여섯 개·256자 제한, 2.26 부터 제한이 없습니다 |
| `domain` | `search` 의 옛 이름으로 도메인 하나만 받습니다 |
| `sortlist` | 결과 주소를 정렬할 망 목록(최대 10쌍) |
| `options` | `ndots:n`(기본 1, 최대 15), `timeout:n`(기본 5초, 최대 30), `attempts:n`(기본 2, 최대 5), `rotate`, `edns0`, `single-request`, `use-vc`, `no-reload`(glibc 2.26+), `trust-ad`(glibc 2.31+) 등 |

파일이 없으면 로컬 기계의 네임서버에만 묻습니다[2]. 환경 변수 `LOCALDOMAIN` 은 프로세스마다 `search` 를 덮어쓰고, `RES_OPTIONS` 는 프로세스마다 `options` 를 고칩니다[2]. systemd-resolved 는 이 두 환경 변수를 지원하지 않습니다[4].

### 누가 썼는지 알려 주는 머리 주석

파일 첫 줄에서 작성 주체를 가릴 수 있습니다.

| 첫 줄 | 쓴 주체 |
|---|---|
| `# Generated by NetworkManager` | NetworkManager[10] |
| `# This is /run/systemd/resolve/stub-resolv.conf managed by man:systemd-resolved(8).` | systemd-resolved 의 스텁 파일[7] |
| `# This is /run/systemd/resolve/resolv.conf managed by man:systemd-resolved(8).` | systemd-resolved 의 상위 서버 파일[7] |

resolved 의 스텁 파일은 머리 주석 뒤에 `nameserver 127.0.0.53` 과 `options edns0 trust-ad` 를 고정으로 적고, 검색 도메인이 없으면 `search .` 을 적습니다[7]. 상위 서버 파일은 서버마다 `nameserver` 줄을 적는데, 53번이 아닌 포트를 쓰는 서버와 특정 도메인 전용으로만 쓰는 서버는 빼고, 서버가 하나도 없으면 `# No DNS servers known.` 을 적습니다[7]. 서버가 세 개를 넘으면 넷째 서버 앞에 `# Too many DNS servers configured, the following entries may be ignored.` 줄을 넣습니다[7]. `DNSStubListener=no` 로 스텁을 끄면 resolved 는 `stub-resolv.conf` 를 상위 서버 파일로 가는 링크로 만듭니다[7].

### systemd-resolved 가 hosts 를 다루는 방식

resolved 는 127.0.0.53 과 127.0.0.54 의 53번 포트에서 질의를 받습니다[4]. 127.0.0.53 은 LLMNR·mDNS 를 포함한 전체 기능을, 127.0.0.54 는 DNSSEC 검증과 LLMNR·mDNS 없이 상위 서버로 넘기는 기능만 제공합니다[4]. resolved 는 `/etc/hosts` 를 스스로 읽어 캐시하고 가장 높은 우선순위로 쓰며, `ReadEtcHosts=no` 로 끌 수 있습니다[4][5]. 이 때문에 nss-resolve 는 `hosts:` 줄에서 `files` 앞에 두기를 권하고, 권장 예는 `hosts: mymachines resolve [!UNAVAIL=return] files myhostname dns` 입니다[6].

## 증거로서 의미

**증명하는 것.** 수집 시점에 `/etc/hosts` 에 고정되어 있던 이름·주소 짝, `/etc/resolv.conf` 와 링크 대상에 적힌 네임서버·검색 도메인·옵션, 그리고 머리 주석으로 드러나는 관리 주체입니다. `/etc/nsswitch.conf` 의 `hosts:` 줄을 함께 보면 hosts 항목이 DNS 보다 먼저 쓰였는지 판단할 수 있습니다[3]. 보고서에는 "수집 시점 `/etc/hosts` 에 `update.example.com` 을 203.0.113.7 로 고정한 줄이 있다" 처럼 파일로 확인되는 만큼만 씁니다(만든 예시).

**증명하지 못하는 것.** 어떤 이름을 실제로 조회했는지는 알 수 없습니다. 두 파일은 설정일 뿐 질의 기록이 아니고, resolved 캐시 내용은 SIGUSR1 을 보내 시스템 로그로 내보내야 볼 수 있습니다[4]. hosts 줄이 언제 들어갔는지, 들어간 뒤 어느 프로그램이 그 줄로 접속했는지도 파일만으로는 모릅니다. `/etc/resolv.conf` 가 `/run` 아래 파일로 가는 링크면 꺼진 이미지에는 링크 문자열만 남고 실제 서버 목록은 없습니다.

## 시각 해석

세 파일 모두 내용 안에 시각이 없습니다. 쓸 수 있는 시각은 파일 시스템의 mtime·ctime 이고, ext4 는 이 값을 UTC 기준 epoch 로 저장합니다([Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)).

`/etc/hosts` 의 mtime 은 마지막으로 내용을 고친 때입니다. 편집기가 새 파일을 만들어 바꿔 넣는 방식이면 아이노드 번호와 생성 시각도 함께 바뀌었을 가능성이 있습니다.

`/etc/resolv.conf` 가 일반 파일이고 NetworkManager 가 관리하면 mtime 은 NM 이 마지막으로 다시 쓴 때, 곧 대개 마지막으로 네트워크 설정이 바뀐 때입니다[9][10]. 링크라면 링크 자체의 시각(lstat)은 링크를 만든 때이고, 대상 파일의 시각과는 다릅니다. resolved 는 새 내용을 임시 파일에 쓴 뒤 옮겨 넣는데, 내용과 기본 속성이 기존 파일과 같으면 옮기지 않고 임시 파일을 지우므로[7][8], `/run/systemd/resolve/` 아래 파일의 mtime 은 내용이 마지막으로 달라진 때입니다(라이브 수집에서만 볼 수 있습니다).

## 함정과 한계

resolved 를 쓰는 기계에서 `/etc/resolv.conf` 를 읽으면 `nameserver 127.0.0.53` 만 보입니다[7]. 이 주소는 상위 DNS 서버가 아니라 로컬 스텁 주소이므로, 실제 서버는 라이브에서 `/run/systemd/resolve/resolv.conf` 나 `resolvectl status` 로, 꺼진 이미지에서는 NM 연결 프로필·netplan·resolved.conf 의 `DNS=` 설정으로 찾습니다([네트워크 설정](./network-config.md)). NM 이 캐시 플러그인을 쓰면 `/run/NetworkManager/no-stub-resolv.conf` 에 원래 서버가 남습니다[9].

분석 PC 에서 이미지의 `/etc/resolv.conf` 링크를 따라가면 분석 PC 의 `/run` 파일을 읽게 됩니다. 절대 경로 링크는 대상 문자열만 읽습니다.

`/etc/resolv.conf` 에 변경 불가 속성이 걸려 있으면 NM 은 파일을 건드리지 않습니다[9]. 누군가 DNS 서버를 고정하려고 이 속성을 걸었을 가능성이 있으므로, 파일 내용과 함께 속성도 확인합니다([권한·확장 속성·ACL·Capabilities](../../01-foundations/filesystem/permissions-xattr.md)).

hosts 에 줄이 있다고 그 줄이 쓰였다고 단정할 수 없습니다. `hosts:` 줄에서 `files` 앞에 다른 서비스가 있고 그 서비스가 답을 내면 hosts 까지 가지 않습니다[3]. 반대로 질의가 resolved 로 넘어가면, resolved 는 `ReadEtcHosts=yes`(기본)일 때 DNS 서버에 묻기 전에 hosts 항목부터 씁니다[4][5]. resolved 가 hosts 로 답하는 것은 주소 조회와 그 역방향 조회뿐이고 MX 같은 다른 형식에는 쓰지 않습니다[4].

도구가 `/etc/hosts` 로 호스트 이름을 추정하는 방식도 한계가 있습니다. dissect 는 다른 호스트 이름 파일이 없을 때 `/etc/hosts` 에서 `127.0.0.1 ` 또는 `::1 ` 로 시작하고 `localhost` 가 없는 줄을 찾아 공백 한 칸으로 나눈 둘째 값을 씁니다[12]. 그래서 필드를 탭으로 나눈 줄이나 `127.0.1.1` 줄은 이 규칙에 걸리지 않습니다. 이때는 `127.0.` 이나 `::1` 로 시작하는 마지막 줄의 둘째 필드를 쓰므로[12] `localhost` 류의 값이 나올 수 있습니다. 호스트 이름 파일 전체의 읽는 순서는 [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md)에 있습니다.

라이브 대응 중에 resolved 에 SIGUSR1 을 보내면 모든 DNS 캐시 내용을 시스템 로그로 내보냅니다[4]. 캐시에 남은 최근 조회 이름을 얻는 방법이지만, 대상 시스템의 저널에 새 항목을 더하므로 한 일과 시각을 대응 기록에 남깁니다. SIGUSR2(`resolvectl flush-caches` 와 같음)는 캐시를 비우고, systemd 256 부터는 SIGHUP 도 캐시를 비우며, 네트워크 설정이 바뀔 때마다 resolved 가 스스로 캐시를 비웁니다[4]. 캐시를 보려면 이런 조작 전에 먼저 수집합니다.

## 직접 분석해 보기

### 헥스로 한 번

hosts 는 텍스트 파일이지만, 필드 사이가 탭(0x09)인지 공백(0x20)인지는 헥스로 봐야 확실합니다. 아래는 명세로 만든 예시입니다. 첫 줄은 탭으로, 둘째 줄은 공백으로 나눴습니다.

```
00000000: 3132 372e 302e 302e 3109 7773 3031 0a32  127.0.0.1.ws01.2
00000010: 3033 2e30 2e31 3133 2e37 2075 7064 6174  03.0.113.7 updat
00000020: 652e 6578 616d 706c 652e 636f 6d0a       e.example.com.
```

오프셋 0x09 의 `09` 가 탭이고 0x1A 의 `20` 이 공백입니다. 첫 줄은 hosts 형식으로는 정상 항목이지만[1] 앞에서 본 dissect 의 호스트 이름 규칙에는 걸리지 않습니다[12]. 링크인 `/etc/resolv.conf` 의 대상 문자열을 아이노드에서 직접 읽는 방법은 [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md) 의 `/etc/localtime` 예와 같습니다.

### 공개 도구로 한 번

마운트한 이미지에서는 링크를 따라가지 않고 봅니다.

```
ls -l  /mnt/img/etc/resolv.conf /mnt/img/etc/nsswitch.conf   # 링크 여부와 대상
stat   /mnt/img/etc/resolv.conf /mnt/img/etc/hosts            # 링크 자체의 시각(lstat)
head -1 /mnt/img/etc/resolv.conf                              # 머리 주석(일반 파일일 때)
grep -v '^\s*#' /mnt/img/etc/hosts | grep -v '^\s*$'          # 주석·빈 줄 뺀 hosts 항목
grep '^hosts:' /mnt/img/etc/nsswitch.conf
lsattr /mnt/img/etc/resolv.conf                               # 변경 불가 속성
```

ForensicArtifacts 정의로는 `UnixHostsFile`, `DNSResolvConfFile` 을 모읍니다[13]. UAC 는 `/etc` 를 통째로 모으고(shadow 류 제외), 라이브에서는 `hostname`, `hostname -f`, `hostnamectl` 결과도 받습니다[14]. `/run/systemd/resolve/`, `/run/NetworkManager/` 아래 파일은 라이브에서 따로 복사합니다([라이브 응답 수집](../../03-techniques/acquisition/live-response.md)). 라이브에서 실제 DNS 질의를 보려면 Velociraptor 의 `Linux.Events.DNS` 가 eBPF 로 DNS 패킷을 잡아 프로세스 이름·PID·출발지와 목적지 주소·포트·질의 이름·형식·응답 주소를 남깁니다[15]. 네트워크 패킷에서 얻는 값이라 DNS over HTTPS 는 보이지 않습니다[15].

## 교차 검증

| 함께 볼 것 | 맞춰 볼 내용 |
|---|---|
| [네트워크 설정](./network-config.md) | 연결 프로필·netplan 에 적힌 DNS 서버, resolv.conf 를 다시 쓴 시각과 연결 기록 |
| [VPN](./vpn.md) | VPN 연결 때 바뀐 DNS 서버와 검색 도메인 |
| [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) | NetworkManager·systemd-resolved 항목, SIGUSR1 캐시 덤프 |
| [셸 명령 기록](../execution/shell-history/index.md) | hosts·resolv.conf 를 편집하거나 `chattr` 를 쓴 명령 |
| [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md) | hosts 의 127.0.1.1 줄과 `/etc/hostname` 이 같은 이름인지 |
| [메모리 분석](../../03-techniques/analysis/memory-analysis.md) | resolved 프로세스 메모리의 캐시 |
| [타임라인 만들기](../../03-techniques/analysis/timeline.md) | 파일 시각을 다른 기록과 한 줄로 세우기 |

## 실습

공개 자료(NIST CFReDS 의 Linux 디스크 이미지 등)로 다음을 풀어 봅니다.

1. `/etc/resolv.conf` 는 일반 파일인가, 링크인가? 링크라면 대상은 resolved 의 어느 파일이고, NetworkManager 는 이 경우 어떤 모드로 동작했겠는가?
2. 일반 파일이라면 첫 줄은 무엇이고, 적힌 네임서버가 NM 연결 프로필의 DNS 설정과 같은가?
3. `/etc/hosts` 에서 설치 기본 줄(localhost, 127.0.1.1, IPv6 기본 줄)이 아닌 줄은 무엇인가? 그 파일의 mtime 은 다른 기록의 어느 시점과 가까운가?
4. `/etc/nsswitch.conf` 의 `hosts:` 줄에서 `files` 는 몇 번째인가? `resolve` 가 있다면 resolved 의 `ReadEtcHosts=` 설정은 무엇인가?
5. dissect 가 내놓은 호스트 이름은 `/etc/hostname` 과 같은가? 다르다면 어느 파일에서 왔는가?

## 참고 문헌

1. man-pages, `man5/hosts.5` — https://github.com/mkerrisk/man-pages/blob/master/man5/hosts.5
2. man-pages, `man5/resolv.conf.5` — https://github.com/mkerrisk/man-pages/blob/master/man5/resolv.conf.5
3. man-pages, `man5/nsswitch.conf.5` — https://github.com/mkerrisk/man-pages/blob/master/man5/nsswitch.conf.5
4. systemd, `man/systemd-resolved.service.xml` — https://github.com/systemd/systemd/blob/main/man/systemd-resolved.service.xml
5. systemd, `man/resolved.conf.xml` — https://github.com/systemd/systemd/blob/main/man/resolved.conf.xml
6. systemd, `man/nss-resolve.xml` — https://github.com/systemd/systemd/blob/main/man/nss-resolve.xml
7. systemd, `src/resolve/resolved-resolv-conf.c` — https://github.com/systemd/systemd/blob/main/src/resolve/resolved-resolv-conf.c
8. systemd, `src/basic/fs-util.c`(`conservative_renameat`) — https://github.com/systemd/systemd/blob/main/src/basic/fs-util.c
9. NetworkManager, `man/NetworkManager.conf.xml` — https://github.com/NetworkManager/NetworkManager/blob/main/man/NetworkManager.conf.xml
10. NetworkManager, `src/core/dns/nm-dns-manager.c` — https://github.com/NetworkManager/NetworkManager/blob/main/src/core/dns/nm-dns-manager.c
11. authselect, `src/man/authselect.8.adoc`, `src/man/authselect-profiles.5.adoc`·`profiles/sssd/nsswitch.conf`(1.2.x 가지), `profiles/local/nsswitch.conf`·`profiles/sssd/nsswitch.conf`(master) — https://github.com/authselect/authselect/blob/master/src/man/authselect.8.adoc , https://github.com/authselect/authselect/blob/1.2.x/src/man/authselect-profiles.5.adoc , https://github.com/authselect/authselect/blob/1.2.x/profiles/sssd/nsswitch.conf , https://github.com/authselect/authselect/blob/master/profiles/local/nsswitch.conf , https://github.com/authselect/authselect/blob/master/profiles/sssd/nsswitch.conf
12. dissect.target, `plugins/os/unix/_os.py` — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/_os.py
13. ForensicArtifacts, `artifacts/data/linux.yaml`, `unix_common.yaml` — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml , https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/unix_common.yaml
14. UAC, `artifacts/files/system/etc.yaml`, `artifacts/live_response/network/hostname.yaml` — https://github.com/tclahr/uac/tree/main/artifacts
15. Velociraptor, `artifacts/definitions/Linux/Events/DNS.yaml` — https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Events/DNS.yaml
