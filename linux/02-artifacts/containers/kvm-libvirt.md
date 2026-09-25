---
title: "가상 머신"
parent: "아티팩트 · 컨테이너와 가상화"
nav_order: 830
---

# 가상 머신 (KVM·libvirt)

libvirt 로 관리하는 KVM 가상 머신은 호스트에 정의 XML·QEMU 로그·스냅숏 메타데이터·DHCP 임대 파일·디스크 이미지를 남기고, 이 파일들로 어떤 가상 머신을 언제 어떤 구성으로 켜고 껐는지 알 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

libvirt 는 가상 머신을 도메인 (domain) 이라고 부르고, 도메인마다 구성을 XML 로 저장합니다. QEMU 드라이버는 root 권한으로 도는 시스템 모드 (`qemu:///system`) 와 일반 사용자 권한으로 도는 세션 모드 (`qemu:///session`) 로 나뉘며, 모드에 따라 파일이 쌓이는 위치가 다릅니다[1][9].

흔적이 생기는 까닭은 다섯 가지입니다. 도메인을 정의하면 영구 정의 XML 이 생기고, 켜면 실행 상태 XML 과 QEMU 로그 줄이 생깁니다[1][2][4]. 스냅숏·저장(save)·메모리 덤프를 하면 메타데이터와 큰 이미지 파일이 생기고[1][10][12], 가상 네트워크에서 게스트가 주소를 받으면 임대 파일이 바뀝니다[11]. 게스트의 디스크는 호스트 파일 시스템의 이미지 파일(qcow2 등)이거나 호스트의 블록 장치입니다[9][14].

libvirt 데몬은 두 가지 구성이 있습니다. 하나는 모든 드라이버를 맡는 단일 데몬 `libvirtd` 이고, 다른 하나는 드라이버마다 따로 도는 모듈형 데몬 `virt${DRIVER}d`(QEMU 는 `virtqemud`)와 원격 접속용 `virtproxyd` 입니다[8]. 둘 다 기본으로 빌드되므로, 검체에서는 어느 쪽 systemd 단위(`libvirtd.service` 또는 `virtqemud.service`)가 켜져 있었는지 먼저 확인합니다[8]. 단위 파일 읽는 법은 [systemd 서비스와 타이머](../persistence/systemd-units.md)에서 다룹니다.

## 위치와 버전별 차이

### 시스템 모드와 세션 모드

| 용도 | 시스템 모드 (`qemu:///system`) | 세션 모드 (`qemu:///session`) |
|---|---|---|
| 영구 정의 XML | `/etc/libvirt/qemu/이름.xml` | `$XDG_CONFIG_HOME/libvirt/qemu/이름.xml` |
| 자동 시작 링크 | `/etc/libvirt/qemu/autostart/이름.xml` | `$XDG_CONFIG_HOME/libvirt/qemu/autostart/이름.xml` |
| 실행 상태 XML | `/run/libvirt/qemu/이름.xml` | `$XDG_RUNTIME_DIR/libvirt/qemu/run/이름.xml` |
| QEMU 로그 | `/var/log/libvirt/qemu/이름.log` | 사용자 캐시 폴더 아래 `libvirt/qemu/log/이름.log` |
| 저장 이미지 | `/var/lib/libvirt/qemu/save/` | `$XDG_CONFIG_HOME/libvirt/qemu/save/` |
| 스냅숏 메타데이터 | `/var/lib/libvirt/qemu/snapshot/` | `$XDG_CONFIG_HOME/libvirt/qemu/snapshot/` |
| 자동 메모리 덤프 | `/var/lib/libvirt/qemu/dump/` | `$XDG_CONFIG_HOME/libvirt/qemu/dump/` |
| UEFI 변수 | `/var/lib/libvirt/qemu/nvram/` | `$XDG_CONFIG_HOME/libvirt/qemu/nvram/` |
| 드라이버 설정 | `/etc/libvirt/qemu.conf` | `$XDG_CONFIG_HOME/libvirt/qemu.conf` |

표의 경로는 libvirt 코드가 정하는 기본값입니다[1][9]. 세션 모드에서 libvirt 는 사용자 설정·캐시·런타임 폴더 아래에 `libvirt` 폴더를 두고 그 아래에 `qemu/…` 를 붙입니다[1][18]. `$XDG_CONFIG_HOME` 이 비어 있으면 `$HOME/.config` 로 봅니다[9]. 로그는 캐시 폴더 쪽에 있으므로, 검체에서는 사용자 홈의 `.cache` 아래 `libvirt` 폴더를 찾습니다.

시스템 모드에는 이 밖에도 `/var/lib/libvirt/qemu/` 아래 `checkpoint/`·`varstore/`·`ram/`, 캐시 `/var/cache/libvirt/qemu`, 가상 TPM 로그 `/var/log/swtpm/libvirt/qemu` 와 저장 폴더 `/var/lib/libvirt/swtpm` 이 있습니다[1]. 디스크 이미지의 기본 폴더는 `/var/lib/libvirt/images` 입니다[9]. 가상 네트워크의 DHCP 임대 파일은 `/var/lib/libvirt/dnsmasq/인터페이스이름.status` 입니다[11].

데몬 설정 파일은 단일 데몬이면 `/etc/libvirt/libvirtd.conf`, 모듈형이면 `/etc/libvirt/virt${DRIVER}d.conf` 입니다[8]. 시스템 모드의 단일 데몬 소켓은 `/var/run/libvirt/libvirt-sock`(읽기 전용은 `libvirt-sock-ro`, 관리용은 `libvirt-admin-sock`)이고, 모듈형 데몬은 `/var/run/libvirt/virt${DRIVER}d-sock` 입니다[8]. 배포판에 따라 `/var/run` 대신 `/run` 을 씁니다[8].

### 배포판 차이

| 항목 | Ubuntu 24.04 LTS 계열 | RHEL 9 계열 |
|---|---|---|
| 게스트 격리 방식 | AppArmor sVirt | SELinux sVirt |
| 게스트마다 남는 것 | `/etc/apparmor.d/libvirt/libvirt-UUID` 와 `libvirt-UUID.files` | 켜진 게스트의 XML 에 배정된 라벨이 들어갑니다 |
| 함께 볼 것 | 공통 틀 `/etc/apparmor.d/libvirt/TEMPLATE` | 디스크 폴더 `/var/lib/libvirt/images` 의 라벨 `system_u:object_r:virt_image_t` |

AppArmor sVirt 는 `qemu:///system` 가상 머신을 켤 때 그 UUID 로 된 프로필이 없으면 새로 만들고, 디스크를 붙이는 등 접근할 파일이 바뀌면 `.files` 를 고쳐 씁니다[9]. SELinux sVirt 는 기본 설정에서 게스트를 켤 때마다 `svirt_t` 에 고유 범주를 붙인 라벨(예: `system_u:system_r:svirt_t:s0:c34,c44`)을 배정하고, 그 게스트만 쓰는 디스크 이미지도 같은 범주로 다시 라벨을 붙입니다[9]. 어느 방식이 켜져 있었는지는 검체의 보안 모듈 설정으로 확인합니다.

## 구조

### 정의 XML 과 자동 시작

영구 정의 XML 은 도메인 이름·UUID·메모리·디스크 경로·네트워크 인터페이스(MAC 주소 포함)를 담습니다. 자동 시작은 `autostart/이름.xml` 이 영구 정의 파일을 가리키는 심볼릭 링크이고, 한 번만 자동 시작하는 설정은 `이름.xml.once` 링크입니다[2]. 링크가 정의 파일을 가리키는지를 libvirt 가 직접 확인하므로[2], 링크 대상 경로도 함께 기록합니다.

### QEMU 로그 줄

도메인을 켤 때 로그에 아래 모양의 줄이 붙고, 바로 다음 줄에 QEMU 실행 명령줄이 통째로 적힙니다[4].

```
시각: starting up libvirt version: 판, qemu version: 주.부.수정패키지문자열, kernel: 커널릴리스, hostname: 호스트이름
QEMU 실행 명령줄
```

libvirt 를 패키지 판 정보와 함께 빌드했으면 `libvirt version: 판` 뒤에 `, package: 패키지판` 이 붙습니다[17]. QEMU 판 번호 바로 뒤에는 QEMU 패키지 문자열이 빈칸 없이 붙고, 비어 있을 수도 있습니다[4]. 멈출 때는 `시각: shutting down, reason=이유` 한 줄이 붙고, 디스크 입출력 오류로 멈추면 `시각: IO error device='…' node-name='…' reason='…'` 줄이 붙습니다[4]. 아래는 만든 예시입니다.

```
2026-01-02 03:20:11.482+0000: starting up libvirt version: 10.0.0, qemu version: 8.2.2, kernel: 6.8.0-51-generic, hostname: kvm-host01.example
/usr/bin/qemu-system-x86_64 -name guest=web01 ... -netdev ... -device virtio-net-pci,mac=52:54:00:12:34:56 ...
```

명령줄에는 디스크 이미지 경로·MAC 주소·원격 화면 설정이 들어가므로, "그 시각에 어떤 구성으로 켰는가" 를 이 두 줄로 확인합니다.

### 스냅숏 메타데이터

스냅숏 XML 의 최상위 요소는 `domainsnapshot` 이고, 분석에 쓰는 요소는 아래와 같습니다[10].

| 요소 | 뜻 |
|---|---|
| `name` | 스냅숏 이름 |
| `creationTime` | 만든 시각. Epoch 초, UTC |
| `state` | 찍을 때 도메인 상태. 디스크만 찍었으면 `disk-snapshot` |
| `parent` | 부모 스냅숏 이름. 스냅숏 나무를 잇습니다 |
| `memory`·`disks` | 메모리를 담았는지, 디스크마다 내부·외부 중 무엇인지 |
| `domain` | 찍을 때의 비활성 도메인 정의 전체(0.9.5 이후) |

스냅숏은 세 종류입니다. 디스크 스냅숏은 qcow2 한 파일 안에 담는 내부형과 새 파일을 만드는 외부형이 있고, 메모리 상태 스냅숏과 둘을 합친 전체 시스템 스냅숏이 있습니다[10]. 켜진 게스트에서 찍은 디스크 스냅숏은 갑자기 전원이 나간 상태와 같습니다[10]. 메타데이터 파일의 이름과 하위 폴더 구성은 검체의 `snapshot/` 폴더에서 확인합니다[1].

### 저장 이미지

`virsh save` 와 `virsh managedsave` 는 게스트 메모리 상태를 파일로 떠 두고 게스트를 멈춥니다. managedsave 로 저장한 게스트는 다음 `start` 때 그 상태에서 이어서 켜집니다[13]. 저장 이미지 머리는 아래와 같습니다[12].

| 오프셋 | 크기 | 필드 |
|---|---|---|
| 0 | 16 | `magic` — `LibvirtQemudSave`, 쓰는 도중이면 `LibvirtQemudPart` |
| 16 | 4 | `version` (현재 2) |
| 20 | 4 | `data_len` |
| 24 | 4 | `was_running` |
| 28 | 4 | `format` |
| 32 | 4 | `cookieOffset` |
| 36 | 56 | 쓰지 않는 칸 |

머리 뒤에 도메인 XML 이 이어지므로, 정의 XML 이 지워졌어도 저장 이미지에서 구성을 되살릴 수 있습니다[12]. 정수의 바이트 순서는 `version` 칸이 2 로 읽히는 쪽으로 판단합니다.

### 메모리 덤프

`virsh dump` 에 `--memory-only` 를 주면 게스트 메모리와 CPU 공통 레지스터만 담은 ELF 파일이 생기고, `--format` 으로 `elf`, `kdump-zlib`, `kdump-lzo`, `kdump-snappy`, `win-dmp` 를 고를 수 있습니다[13]. `--live` 를 주면 게스트를 먼저 멈추지 않고, 덤프가 끝날 때까지 게스트가 계속 돕니다[13]. QEMU/KVM 가상 머신을 멈춘 채 QEMU 의 `dump_guest_memory` 명령으로 뜬 메모리를 한 순간의 기준값으로 삼아, 게스트 안에서 뜬 LiME·AVML·LEMON 덤프와 바이트 단위로 비교한 시험이 있습니다[16]. 메모리 수집 방법은 [메모리 수집](../../03-techniques/acquisition/memory-acquisition.md)에서 다룹니다.

### DHCP 임대 파일

`인터페이스이름.status` 는 JSON 배열이고, 항목마다 `ip-address`, `mac-address`, `expiry-time` 이 들어가며, 알려진 경우 `hostname`, `client-id` 가 붙습니다[11]. IPv6 임대에는 `iaid` 와 `server-duid` 가 붙습니다[11]. `hostname` 은 게스트가 DHCP 로 알린 이름이고, 새로 알리지 않으면 이전에 알린 이름을 이어 씁니다[11]. 아래는 만든 예시입니다.

```json
[
    {
        "ip-address": "192.0.2.57",
        "mac-address": "52:54:00:12:34:56",
        "hostname": "web01",
        "expiry-time": 1767327907
    }
]
```

## 증거로서 의미

### 증명하는 것

- 이 호스트에 어떤 이름·UUID 의 가상 머신이 정의돼 있었고, 자동 시작으로 설정돼 있었는지(정의 XML·자동 시작 링크).
- 가상 머신을 언제 켜고 껐는지와 켤 때의 디스크·네트워크 구성(QEMU 로그의 시작·종료 줄과 명령줄).
- 게스트가 어떤 MAC 주소로 어떤 IP 를 받았고 어떤 호스트 이름을 알렸는지(임대 파일).
- 스냅숏을 언제 찍었고 어떤 스냅숏에서 갈라져 나왔는지(`creationTime`·`parent`, qcow2 스냅숏 표).
- 호스트 디스크에 게스트 메모리가 통째로 남은 파일이 있는지(저장 이미지·덤프).

### 증명하지 못하는 것

- 게스트 안에서 일어난 일. 게스트 디스크 이미지를 따로 풀어 분석해야 합니다([디스크 이미징](../../03-techniques/acquisition/disk-imaging.md)).
- 누가 `virsh` 로 조작했는지. 데몬 저널, [셸 명령 기록](../execution/shell-history/index.md), 로그인 기록과 맞춰 봐야 합니다.
- 로그 회전으로 밀려난 오래된 시작·종료 기록과, 같은 IP 로 새로 받았거나 지운 임대의 이전 기록.
- 켠 뒤 붙이거나 뗀 장치. 명령줄은 켤 때 한 번만 적습니다[4].

보고서에는 "2026-01-02 03:20:11 UTC 에 호스트 kvm-host01 에서 도메인 web01 이 시작된 기록이 있고, 그때 디스크 이미지는 `/var/lib/libvirt/images/web01.qcow2` 였다" 처럼 기록이 말하는 만큼만 씁니다(만든 예시).

## 시각 해석

| 값 | 형식 | 시간대 | 바뀌는 때 |
|---|---|---|---|
| QEMU 로그 줄 머리 | `YYYY-MM-DD HH:MM:SS.mmm+0000` | UTC, 밀리초까지[5] | 시작·종료·입출력 오류 때 줄이 붙음[4] |
| 스냅숏 XML `creationTime` | Epoch 초 | UTC[10] | 스냅숏을 만들 때 |
| qcow2 스냅숏 표의 시각 | Epoch 초 + 나노초 | Epoch 기준[14] | 내부 스냅숏을 찍을 때 |
| 임대 파일 `expiry-time` | Epoch 초 | Epoch 기준[11] | 임대를 새로 받거나 갱신할 때 |
| 정의 XML·상태 XML | 내용에 시각 없음 | 파일 시스템 시각을 봄 | 정의를 고치거나 켤 때 |

QEMU 로그의 시각은 호스트 시간대 설정과 상관없이 늘 `+0000` 으로 적힙니다[5]. 호스트 시계가 틀렸으면 이 값도 그만큼 틀리므로, 같은 시각대의 저널 기록과 맞춰 봅니다. Epoch 값을 바꾸는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

qcow2 스냅숏 표에는 찍은 시각과 함께 "그때까지 게스트가 돈 시간"(나노초)도 있습니다[14]. 두 값을 같이 보면 게스트를 얼마나 켜 둔 뒤에 스냅숏을 찍었는지 알 수 있습니다.

## 함정과 한계

**실행 상태 XML 은 전원을 끄면 사라집니다.** `/run/libvirt/qemu/` 는 런타임 폴더(RUNSTATEDIR) 아래에 있고[1], 이 폴더는 부팅 때 비워집니다. 켜진 동안 핫플러그한 장치와 SELinux 가 배정한 라벨은 이 파일에 있으므로, 라이브 수집에서 먼저 떠 둡니다([라이브 응답 수집](../../03-techniques/acquisition/live-response.md)). `/run` 의 성격은 [디렉터리 구조와 주요 경로](../../01-foundations/filesystem/fhs-paths.md)에서 다룹니다.

**세션 모드 가상 머신은 사용자 홈에만 흔적이 있습니다.** `/etc/libvirt/qemu` 만 보면 일반 사용자가 만든 가상 머신을 놓칩니다[1].

**로그는 회전합니다.** 기본값 `stdio_handler = "logd"` 이면 virtlogd 가 로그를 받아 쓰고, 파일이 `max_size`(기본 2MiB)를 넘으면 회전해 활성 파일 말고 `max_backups`(기본 3) 개만 남깁니다[6]. `max_age_days` 기본값은 0 이라 나이로는 지우지 않습니다[6]. virtlogd 를 끈 환경을 위해 logrotate 설정이 따로 깔릴 수도 있습니다[6]([로그 순환](../../01-foundations/logging/logrotate.md)).

**세션 모드에서 파일 방식으로 쓰면 켤 때마다 로그가 비워집니다.** virtlogd 를 쓰지 않는 비특권 실행에서는 로그를 연 뒤 길이를 0 으로 자릅니다[3]. 이 경우 로그에는 마지막 실행 기록만 남습니다.

**외부 스냅숏을 만들면 활성 디스크 파일이 바뀝니다.** 원래 이미지는 읽기 전용 스냅숏이 되고, 그 뒤의 변경은 모두 새 파일에 쓰입니다[10]. 가장 최근 내용은 체인 맨 위 파일에 있으므로, 이미지 하나만 떠 오면 최근 변경을 놓칩니다.

**undefine 해도 파일이 남습니다.** 켜진 도메인을 undefine 하면 멈추지 않고 일시 도메인으로 바뀝니다[13]. managedsave 이미지나 NVRAM 파일이 있거나 꺼진 도메인에 스냅숏 메타데이터가 있으면 해당 옵션 없이는 undefine 이 실패하고, 저장소 삭제 옵션을 줘도 백킹 체인의 맨 위 이미지만 지우고 아래 백킹 파일은 남깁니다[13]. 정의 XML 이 없어도 로그·디스크 이미지를 찾아봅니다.

**임대 파일은 이력이 아닙니다.** 헬퍼가 임대를 추가·갱신·삭제할 때마다 같은 IP 항목을 빼고 파일 전체를 다시 씁니다[11]. 그래서 한 IP 에는 마지막 항목 하나만 남고, dnsmasq 가 지운 임대는 파일에서 빠집니다[11].

**qcow2 의 dirty 비트.** v3 이미지의 `incompatible_features` 0번 비트가 켜져 있으면 참조 횟수가 맞지 않을 수 있다는 뜻이고, 이런 이미지는 읽기 전에 참조 횟수를 고치게 돼 있습니다[14]. 원본이 바뀌지 않도록 사본으로 엽니다.

## 직접 분석해 보기

### 헥스로 qcow2 머리 읽기

qcow2 의 숫자는 모두 빅엔디언입니다[14]. 머리는 아래와 같습니다[14].

| 오프셋 | 크기 | 필드 |
|---|---|---|
| 0 | 4 | `magic` — `QFI\xfb` |
| 4 | 4 | `version` (2 또는 3) |
| 8 | 8 | `backing_file_offset` — 0 이면 백킹 파일 없음 |
| 16 | 4 | `backing_file_size` — 최대 1023 |
| 20 | 4 | `cluster_bits` — 클러스터 크기 = 1 을 이만큼 왼쪽으로 민 값 |
| 24 | 8 | `size` — 가상 디스크 크기(바이트) |
| 32 | 4 | `crypt_method` — 0 없음, 1 AES, 2 LUKS |
| 36 | 4 | `l1_size` |
| 40 | 8 | `l1_table_offset` |
| 48 | 8 | `refcount_table_offset` |
| 56 | 4 | `refcount_table_clusters` |
| 60 | 4 | `nb_snapshots` |
| 64 | 8 | `snapshots_offset` |

v2 머리는 72바이트에서 끝나고, v3 은 104바이트 이상입니다[14]. 아래는 명세로 만든 예시입니다.

```
00000000  51 46 49 fb 00 00 00 03  00 00 00 00 00 00 01 70  |QFI............p|
00000010  00 00 00 22 00 00 00 10  00 00 00 05 00 00 00 00  |..."............|
00000020  00 00 00 00 00 00 00 28  00 00 00 00 00 03 00 00  |.......(........|
00000030  00 00 00 00 00 01 00 00  00 00 00 01 00 00 00 01  |................|
00000040  00 00 00 00 00 05 00 00                           |........|
```

v3 이고, 오프셋 0x170 에 백킹 파일 이름 34(0x22)바이트가 있습니다. 이름 문자열은 NUL 로 끝나지 않으므로 길이만큼만 읽습니다[14]. 클러스터는 2^16 = 64KiB, 가상 크기는 0x500000000 = 20GiB, 암호화 없음, 내부 스냅숏 1개가 0x50000 에 있습니다.

스냅숏 표 항목은 0~7 L1 표 위치, 8~11 L1 항목 수, 12~13 ID 길이, 14~15 이름 길이, 16~19 찍은 시각(Epoch 초), 20~23 나노초, 24~31 게스트가 돈 시간(나노초), 32~35 메모리 상태 크기(0 이면 메모리 없음), 36~39 추가 데이터 크기이고, 뒤에 추가 데이터·ID·이름이 옵니다[14]. ID 와 이름도 NUL 로 끝나지 않고, 항목 끝은 8의 배수로 채웁니다[14]. v3 이미지는 추가 데이터를 적어도 16바이트(항목 기준 40~47 64비트 메모리 상태 크기, 48~55 스냅숏의 가상 디스크 크기) 넣어야 합니다[14]. 아래도 명세로 만든 예시입니다.

```
00050000  00 00 00 00 00 06 00 00  00 00 00 28 00 01 00 05  |...........(....|
00050010  69 57 3a 93 0b eb c2 00  00 00 00 d1 8c 2e 28 00  |iW:...........(.|
00050020  00 00 00 00 00 00 00 10  00 00 00 00 00 00 00 00  |................|
00050030  00 00 00 05 00 00 00 00  31 63 6c 65 61 6e        |........1clean|
```

시각 0x69573a93 은 1767324307 이고 2026-01-02 03:25:07 UTC 입니다. 나노초 0x0bebc200 은 0.2초, 게스트가 돈 시간 0xd18c2e2800 은 900초입니다. 메모리 상태 크기가 0 이라 디스크만 담은 스냅숏입니다. 추가 데이터 16(0x10)바이트에는 64비트 메모리 상태 크기 0 과 가상 디스크 크기 0x500000000(20GiB)이 들어 있고, 그 뒤 ID 는 `1`, 이름은 `clean` 입니다.

### 공개 도구로

- 라이브 수집: UAC 는 `virsh list --all` 과 도메인마다 `domifaddr`·`dominfo`·`dommemstat`·`snapshot-list`·`vcpuinfo`, `net-list --all` 과 네트워크마다 `net-info`·`net-dhcp-leases`, 그리고 `nodeinfo`·`pool-list --all` 을 모읍니다[15].
- 오프라인: 정의 XML·스냅숏 XML·로그·임대 파일은 텍스트라서 `grep` 으로 도메인 이름·UUID·MAC 주소를 가로질러 찾습니다. qcow2 머리는 QEMU 에 들어 있는 `qemu-img info` 로도 볼 수 있습니다.

## 교차 검증

| 확인할 것 | 함께 볼 곳 |
|---|---|
| 누가 데몬에 명령했나 | 데몬 로그는 출력 설정이 없고 `/run/systemd/journal/socket` 이 있으면 저널로 갑니다[7]([systemd 저널](../../01-foundations/logging/systemd-journal/index.md)). 셸 명령 기록의 `virsh` 줄 |
| 켠 구성과 실제 접근 파일 | QEMU 로그 명령줄 ↔ 정의 XML ↔ AppArmor `.files` |
| SELinux 차단 | RHEL 계열이면 [감사 로그](../../01-foundations/logging/auditd-format.md)의 AVC 거부 기록 |
| 게스트 식별 | 정의 XML 의 MAC ↔ 임대 파일의 `mac-address`·`hostname` ↔ 게스트 안의 호스트 이름 설정 |
| 스냅숏 시각 | 스냅숏 XML `creationTime` ↔ qcow2 스냅숏 표 시각 ↔ 파일 시스템 시각 |
| 호스트 부팅과의 관계 | [부팅과 종료 기록](../system-info/boot-shutdown.md)과 QEMU 로그 시작 줄 |

컨테이너 쪽 흔적은 [Docker](docker/index.md)와 [Podman](podman.md)에서 다룹니다. 여러 흔적을 한 줄로 늘어놓는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 실습

직접 만든 실험 호스트에 libvirt 를 깔고 도메인 하나를 만들어 켜고 끈 뒤, 내부 스냅숏과 외부 스냅숏을 한 번씩 찍고 undefine 해 봅니다.

1. QEMU 로그에서 시작·종료 줄을 찾아 호스트 저널의 같은 시각대 기록과 몇 초 차이가 나는지 맞춰 봅니다.
2. 외부 스냅숏 뒤 활성 디스크 파일은 무엇이고, 그 qcow2 머리의 `backing_file_offset` 이 가리키는 경로는 무엇입니까?
3. 내부 스냅숏의 qcow2 스냅숏 표 시각과 스냅숏 XML 의 `creationTime` 은 몇 초 차이가 납니까?
4. undefine 뒤 `/etc/libvirt/qemu`, `/var/lib/libvirt/qemu`, `/var/log/libvirt/qemu`, `/var/lib/libvirt/images` 에 무엇이 남았습니까?
5. 게스트를 두 번 재부팅한 뒤 임대 파일에 그 게스트 항목이 몇 개 있습니까?

## 참고 문헌

1. libvirt, src/qemu/qemu_conf.c — https://github.com/libvirt/libvirt/blob/master/src/qemu/qemu_conf.c
2. libvirt, src/conf/virdomainobjlist.c — https://github.com/libvirt/libvirt/blob/master/src/conf/virdomainobjlist.c
3. libvirt, src/hypervisor/domain_logcontext.c — https://github.com/libvirt/libvirt/blob/master/src/hypervisor/domain_logcontext.c
4. libvirt, src/qemu/qemu_process.c — https://github.com/libvirt/libvirt/blob/master/src/qemu/qemu_process.c
5. libvirt, src/util/virtime.c — https://github.com/libvirt/libvirt/blob/master/src/util/virtime.c
6. libvirt, src/logging/virtlogd.conf·src/qemu/qemu.conf.in — https://github.com/libvirt/libvirt/blob/master/src/logging/virtlogd.conf , https://github.com/libvirt/libvirt/blob/master/src/qemu/qemu.conf.in
7. libvirt, docs/logging.rst — https://github.com/libvirt/libvirt/blob/master/docs/logging.rst
8. libvirt, docs/daemons.rst — https://github.com/libvirt/libvirt/blob/master/docs/daemons.rst
9. libvirt, docs/drvqemu.rst — https://github.com/libvirt/libvirt/blob/master/docs/drvqemu.rst
10. libvirt, docs/formatsnapshot.rst — https://github.com/libvirt/libvirt/blob/master/docs/formatsnapshot.rst
11. libvirt, src/network/leaseshelper.c·src/util/virlease.c·tests/nssdata/virbr0.status — https://github.com/libvirt/libvirt/blob/master/src/network/leaseshelper.c , https://github.com/libvirt/libvirt/blob/master/src/util/virlease.c , https://github.com/libvirt/libvirt/blob/master/tests/nssdata/virbr0.status
12. libvirt, src/qemu/qemu_saveimage.h — https://github.com/libvirt/libvirt/blob/master/src/qemu/qemu_saveimage.h
13. libvirt, docs/manpages/virsh.rst (managedsave·dump·undefine) — https://github.com/libvirt/libvirt/blob/master/docs/manpages/virsh.rst
14. QEMU, docs/interop/qcow2.rst — https://github.com/qemu/qemu/blob/master/docs/interop/qcow2.rst
15. UAC, artifacts/live_response/vms/virsh.yaml — https://github.com/tclahr/uac/blob/main/artifacts/live_response/vms/virsh.yaml
16. Andrea Oliveri, Marco Cavenati, Stefano De Rosa, Sudharsun Lakshmi Narasimhan, Davide Balzarotti, "LEMON: A universal eBPF-based volatile memory acquisition tool for modern android devices and hardened linux systems", Forensic Science International: Digital Investigation 56 (2026) 302045, https://doi.org/10.1016/j.fsidi.2026.302045
17. libvirt, src/util/virlog.h — https://github.com/libvirt/libvirt/blob/master/src/util/virlog.h
18. libvirt, src/util/virutil.c — https://github.com/libvirt/libvirt/blob/master/src/util/virutil.c
