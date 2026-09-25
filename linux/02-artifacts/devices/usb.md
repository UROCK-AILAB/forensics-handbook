---
title: "USB 장치 연결 기록"
parent: "아티팩트 · 외부 장치"
nav_order: 880
---

# USB 장치 연결 기록 (USB)

USB 장치를 꽂고 뽑을 때 커널이 남기는 로그 줄과 udev 가 만드는 장치 정보를 모으면, 어느 부팅에서 어떤 장치가 언제 붙었다 떨어졌는지를 좁힐 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

장치를 꽂으면 USB 코어가 장치에 주소를 매기면서 커널 로그에 `new high-speed USB device number 5 using xhci_hcd` 같은 줄을 남깁니다[1]. 줄 머리는 드라이버 이름(드라이버가 없으면 버스 이름)과 장치 이름 뒤에 콜론을 붙인 꼴이라 `usb 1-2:` 처럼 나옵니다[7]. 여기서 `1-2` 는 버스와 포트를 따라간 경로입니다.

커널을 `CONFIG_USB_ANNOUNCE_NEW_DEVICES` 로 빌드했으면 이어서 장치가 보고한 제조사 번호 (idVendor)·제품 번호 (idProduct)·제조사·제품 이름·시리얼 번호 줄이 나옵니다[1]. 이 설정은 보통 배포판이 디버깅을 돕고 어떤 장치가 어디에 붙었는지 알리려고 켜는 옵션입니다[2]. 저장 장치이면 usb-storage 드라이버가 `USB Mass Storage device detected` 를 찍고, SCSI 디스크 드라이버가 `sdb` 같은 디스크 이름을 붙이면서 용량·쓰기 보호·이동식 여부를 찍습니다[4][5]. 장치를 뽑으면 `USB disconnect, device number 5` 가 남고 장치 번호는 반환됩니다[1].

커널 줄과 따로, udev 가 규칙을 적용해 장치 속성을 udev 데이터베이스에 쓰고 `/dev/disk/by-id/` 아래 링크를 만듭니다[11][12]. 사용자가 데스크톱에서 매체를 열면 마운트 기록이 이어지고, 이 부분은 [마운트 기록](mounts.md) 에서 다룹니다.

## 위치와 버전별 차이

| 저장 위치 | Ubuntu 24.04 LTS | RHEL 9 | 남는 기간 |
|---|---|---|---|
| 커널 링 버퍼 | `dmesg`, 메모리 이미지 | 같음 | 재부팅하면 사라짐 |
| systemd 저널 | `_TRANSPORT=kernel` 항목[9] | 같음 | 저널 보존 설정에 따름 |
| rsyslog 텍스트 | `/var/log/kern.log`, `/var/log/syslog`[20] | `/var/log/messages`[21] | 순환 설정에 따름 |
| udev 데이터베이스 | `/run/udev/data/`[11] | 같음 | 라이브·메모리에서만 |
| 영구 이름 링크 | `/dev/disk/by-id/` 등[12] | 같음 | 라이브에서만 |
| sysfs 속성 | USB 장치 폴더의 `idVendor`·`serial` 등[6] | 같음 | 라이브에서만 |
| GNOME 메타데이터 | `~/.local/share/gvfs-metadata/`[15][16] | 같음 | 디스크에 남음 |

커널 로그가 어느 파일에 어떤 설정으로 들어가는지, 두 배포판의 rsyslog 가 커널 메시지를 받는 길이 어떻게 다른지는 [커널 로그](../system-info/kernel-log.md) 에서 다룹니다. USB 코어의 연결 줄은 info 등급이라[1] RHEL 의 `*.info` 규칙에 걸립니다[21].

`/run` 은 tmpfs 라 부팅할 때 비워지고, `/dev` 는 보통 devtmpfs 입니다[14]. 그래서 udev 데이터베이스·`/dev/disk/by-*` 링크·sysfs 는 꺼진 시스템의 디스크 이미지에는 없습니다. 디스크 이미지로 볼 수 있는 것은 저널·rsyslog 파일·gvfs 메타데이터입니다.

## 구조

### 커널 로그 줄

| 줄 모양 | 뜻 | 조건 |
|---|---|---|
| `%s %s USB device number %d using %s` | `new`(새 연결) 또는 `reset`(재설정), 속도, 장치 번호, 호스트 컨트롤러 드라이버[1] | high-speed 이하 |
| `%s SuperSpeed%s%s USB device number %d using %s` | 같음, 속도 자리에 ` Plus`·` Gen 2x2` 등이 붙음[1] | SuperSpeed 이상 |
| `New USB device found, idVendor=%04x, idProduct=%04x, bcdDevice=%2x.%02x` | 장치 설명자의 번호들[1] | 설정 켬 |
| `New USB device strings: Mfr=%d, Product=%d, SerialNumber=%d` | 문자열 설명자의 번호. 0 이면 그 문자열이 없음[1] | 설정 켬 |
| `Product: %s`, `Manufacturer: %s`, `SerialNumber: %s` | 장치가 보고한 문자열. 문자열이 없으면 줄 자체를 찍지 않음[1] | 설정 켬 |
| `USB Mass Storage device detected` | usb-storage 드라이버가 붙음[4] | 저장 장치 |
| `%llu %d-byte logical blocks: (%s/%s)` | 블록 수·블록 크기, 10진·2진 단위 용량[5] | SCSI 디스크 |
| `Write Protect is %s` | 쓰기 보호 여부[5] | SCSI 디스크 |
| `Attached SCSI %sdisk` | 이동식이면 `removable ` 이 들어감[5] | SCSI 디스크 |
| `USB disconnect, device number %d` | 장치가 떨어짐[1] | 항상 |

high-speed 이하 줄의 속도 자리에는 `low-speed`, `full-speed`, `high-speed`, `wireless` 중 하나가 들어가고, SuperSpeed 이상 줄은 속도 문자열 대신 `SuperSpeed` 를 그대로 씁니다[1][3]. SCSI 디스크 줄은 머리에 SCSI 장치 주소와 함께 `sdb` 같은 디스크 이름이 붙습니다[5]. 아래는 형식에 맞춰 만든 예시이며 값은 모두 지어낸 것입니다.

```
usb 1-2: new high-speed USB device number 5 using xhci_hcd
usb 1-2: New USB device found, idVendor=abcd, idProduct=1234, bcdDevice= 1.00
usb 1-2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
usb 1-2: Product: EXAMPLE DISK
usb 1-2: Manufacturer: EXAMPLE
usb 1-2: SerialNumber: 0123456789AB
usb-storage 1-2:1.0: USB Mass Storage device detected
sd 6:0:0:0: [sdb] 30031872 512-byte logical blocks: (15.4 GB/14.3 GiB)
sd 6:0:0:0: [sdb] Attached SCSI removable disk
usb 1-2: USB disconnect, device number 5
```

`bcdDevice=%2x` 는 두 칸 폭이라 앞자리가 한 자리면 공백이 들어갑니다[1]. 드라이버 이름과 SCSI 주소는 검체마다 다릅니다.

### 저널 필드

journald 가 커널 메시지를 받으면 아래 필드가 붙고, 다섯 필드 모두 systemd 189 부터 있습니다[8]. 저널 항목의 공통 필드와 파일 구조는 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 에서 다룹니다.

| 필드 | 값 |
|---|---|
| `_KERNEL_DEVICE=` | 블록 장치는 `b주:부`, 문자 장치는 `c주:부`, 네트워크 장치는 `n인터페이스번호`, 그 밖은 `+서브시스템:장치이름`[8] |
| `_KERNEL_SUBSYSTEM=` | 커널 서브시스템 이름[8] |
| `_UDEV_SYSNAME=` | `/sys/` 아래 장치 이름[8] |
| `_UDEV_DEVNODE=` | `/dev/` 아래 장치 노드 경로[8] |
| `_UDEV_DEVLINK=` | 장치 노드를 가리키는 링크, 여러 번 나올 수 있음[8] |

`_KERNEL_DEVICE` 는 커널이 장치에 문자·블록 장치 번호가 있는지를 보고 고릅니다[7]. USB 코어는 `New USB device found` 줄을 찍은 뒤, `New USB device strings` 줄을 찍기 직전에 장치에 문자 장치 번호를 붙이고, 부 번호는 `(버스 번호 − 1) × 128 + (장치 번호 − 1)` 입니다[1]. 그래서 같은 장치라도 `new ... USB device number` 줄과 `New USB device found` 줄은 `+usb:1-2` 꼴, 그 뒤 줄들은 `c주:부` 꼴로 나뉠 가능성이 있습니다. 장치 하나의 줄을 모을 때는 한 값으로만 거르지 말고 시각이 이어지는 줄을 함께 봅니다. dissect.target 저널 플러그인은 `_UDEV_*` 필드를 `udev_sysname`, `udev_devnode`, `udev_devlink` 로 옮겨 싣습니다[18].

### udev 데이터베이스

udev 는 장치마다 `/run/udev/data/` 아래에 장치 ID 이름의 파일을 씁니다[11]. 장치 번호가 있으면 `b`·`c` 뒤에 주:부 번호, 네트워크 장치는 `n` 뒤에 인터페이스 번호, 그 밖은 `+서브시스템:장치이름` 이 파일 이름입니다[11]. 파일은 한 줄에 한 항목이고 앞 글자로 종류를 가립니다[11].

| 머리 | 내용 |
|---|---|
| `S:` | `/dev/` 를 뗀 링크 경로 |
| `L:` | 링크 우선순위 |
| `I:` | 장치를 처음 초기화한 시각(마이크로초) |
| `E:` | `키=값` 속성 |
| `G:` | 태그 |
| `Q:` | 현재 태그 |
| `V:` | 데이터베이스 판 |

`I:` 값은 벽시계가 아니라 `CLOCK_MONOTONIC`, 곧 부팅 뒤 흐른 마이크로초이고, 같은 장치의 이전 기록이 있으면 그 값을 그대로 물려받습니다[11]. 규칙에서 `db_persist` 를 준 장치는 파일에 스티키 비트를 켜고, 이 항목은 `udevadm info --cleanup-db` 로 데이터베이스를 비워도 남습니다[11][13]. initrd 에서 실제 루트로 넘어갈 때 장치 상태를 이어 가려고 쓰는 옵션입니다[13]. 라이브에서는 `udevadm info --export-db` 로 데이터베이스 전체를 뽑습니다[13].

### /dev/disk/by-id 링크 이름

systemd 의 영구 저장 장치 규칙은 `sd*` 디스크에 `ID_SERIAL` 이 있으면 `disk/by-id/$env{ID_BUS}-$env{ID_SERIAL}` 링크를 만들고, 파티션이면 뒤에 파티션 접미사를 붙입니다[12]. USB 디스크는 `usb_id` 로 속성을 가져오고, 예전 링크와 이름을 맞추려고 `disk/by-id/usb-$env{ID_USB_SERIAL}` 링크도 따로 만듭니다[12]. 이동식이 아닌 USB 저장 장치, 곧 외장 케이스에 넣은 SATA 디스크는 `ata_id` 를 먼저 돌려 디스크 자체의 정보를 가져옵니다[12]. 링크 이름에 시리얼 정보가 들어가므로 라이브에서 모은 `ls -l /dev/disk/by-*` 결과[16]는 장치 노드와 시리얼을 잇는 표가 됩니다.

### sysfs 속성

USB 장치 폴더의 `product`·`manufacturer`·`serial` 은 문자열, `idVendor`·`idProduct`·`bcdDevice` 는 네 자리 16진수, `bDeviceClass` 는 두 자리 16진수입니다[6]. `speed`·`busnum`·`devnum`·`devpath`·`version` 도 같은 폴더에 있습니다[6]. `lsusb` 가 보여 주는 값이 여기서 나오며, UAC 는 라이브에서 `lsusb` 와 `lsusb -vv` 결과를 받습니다[16].

### gvfs-metadata 트리 이름

GNOME 의 gvfs 는 파일 관리자가 쓰는 메타데이터를 사용자 데이터 폴더의 `gvfs-metadata/` 아래 트리 파일에 둡니다[15]. 블록 장치 위 파일이면 udev 속성 `ID_FS_UUID_ENC` 가 있을 때 트리 이름이 `uuid-` 뒤에 그 값, 없고 `ID_FS_LABEL_ENC` 가 있으면 `label-` 뒤에 그 값입니다[15]. 홈 폴더 아래 파일은 `home` 트리를 쓰고, 마운트 지점이 `/` 이거나 트리를 정하지 못한 파일은 `root` 트리를 씁니다[15]. 따라서 `uuid-` 로 시작하는 트리 파일은 그 UUID 의 볼륨 위 파일에 GNOME 메타데이터가 쓰인 적이 있다는 뜻일 가능성이 있습니다. UAC 는 `%user_home%/.local/share/gvfs-metadata` 를 통째로 모읍니다[16].

## 증거로서 의미

### 증명하는 것

커널 로그는 그 부팅에서 어느 포트 경로에 어떤 속도의 장치가 붙었고 몇 번 장치 번호를 받았는지, 언제 떨어졌는지를 보여 줍니다[1]. 커널 설정이 켜져 있으면 장치가 보고한 제조사 번호·제품 번호·제조사·제품·시리얼 문자열도 남습니다[1]. 저장 장치로 붙었으면 `sdb` 같은 디스크 이름과 용량, 이동식 여부, 쓰기 보호 여부가 함께 남습니다[5]. 디스크 이름은 [마운트 기록](mounts.md) 의 장치 이름으로, 시리얼은 by-id 링크 이름으로, 볼륨 UUID 는 gvfs 트리 이름으로 이어 한 장치를 여러 기록에서 따라갈 수 있습니다.

보고서에는 "이 부팅의 이 시각에 시리얼 번호가 이것인 USB 저장 장치를 커널이 인식한 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

### 증명하지 못하는 것

커널 로그에는 사용자가 없어서 누가 꽂았는지 알 수 없습니다. 사용자와 잇는 일은 마운트 기록의 uid 와 [로그인 기록](../logins/wtmp-btmp-lastlog.md) 으로 좁힙니다. 연결 기록은 장치가 붙었다는 사실까지만 말하고, 파일을 읽거나 복사했는지는 말하지 않습니다.

제조사 번호와 시리얼은 장치가 설명자로 보고한 값을 커널이 그대로 옮긴 것이라[1] 장치가 진짜 그 제품인지, 같은 시리얼의 다른 장치가 아닌지는 보장하지 않습니다. 시리얼 문자열을 주지 않는 장치는 `SerialNumber` 줄 자체가 없습니다[1]. `usb 1-2` 는 포트 경로라 장치 식별자가 아니고, 장치 번호는 뽑을 때 반환되어 같은 부팅 안에서도 다시 쓰입니다[1].

## 시각 해석

| 값 | 기준 | 바뀌는 때 |
|---|---|---|
| 링 버퍼·`dmesg` 기본 출력 | 부팅 뒤 흐른 초[10] | 커널이 줄을 버퍼에 넣을 때 |
| 저널 `__REALTIME_TIMESTAMP` | UTC 기준 epoch 마이크로초[8] | journald 가 항목을 받을 때 |
| 저널 `__MONOTONIC_TIMESTAMP` | 부팅 뒤 마이크로초, `_BOOT_ID` 와 짝[8] | 같음 |
| `kern.log`·`syslog`·`messages` 줄 앞 시각 | rsyslog 템플릿에 따름. RHEL 9 설정은 전통 형식이라 현지 시각이고 연도가 없음[21] | rsyslog 가 줄을 쓸 때 |
| udev 데이터베이스 `I:` | 부팅 뒤 마이크로초(monotonic)[11] | 그 부팅에서 장치를 처음 초기화할 때 |

저널의 `__REALTIME_TIMESTAMP` 는 journald 가 받은 시각이라 커널이 줄을 낸 순간보다 조금 늦을 수 있습니다[8]. `dmesg -T` 로 바꾼 벽시계 시각은 절전·복귀를 거치면 틀릴 수 있으므로[10] 보고서의 시각은 저널 값을 씁니다. 이 문제와 부팅 뒤 경과 시간을 벽시계로 바꾸는 방법은 [커널 로그](../system-info/kernel-log.md) 와 [부팅과 종료 기록](../system-info/boot-shutdown.md) 에서 다룹니다. udev `I:` 값도 같은 부팅의 저널 항목에서 monotonic 값과 realtime 값의 짝을 구해 벽시계로 바꿉니다.

rsyslog 파일의 시각 형식은 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md), 시간대 확인은 [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md), 시각 값 변환은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

- 커널을 `CONFIG_USB_ANNOUNCE_NEW_DEVICES` 없이 빌드했으면 제조사 번호·시리얼 줄이 없습니다[1][2]. `new ... USB device number` 줄과 `USB disconnect` 줄은 이 설정과 상관없이 나옵니다[1]. 검체 커널이 이 설정을 켰는지는 그 커널의 빌드 설정으로 확인합니다.
- `reset high-speed USB device number` 처럼 첫 낱말이 `reset` 인 줄은 새 연결이 아니라 붙어 있던 장치를 다시 설정한 것입니다[1].
- USB 3 저장 장치가 UAS 드라이버로 붙으면 `USB Mass Storage device detected` 줄이 없을 수 있습니다. 이 문구는 usb-storage 드라이버에만 있습니다[4].
- `journalctl -k` 는 `--boot=0` 을 함께 뜻해서 부팅을 지정하지 않으면 마지막 부팅만 보여 줍니다[9]. 과거 연결은 부팅마다 봅니다.
- 링 버퍼는 한 바퀴 돌면 앞쪽을 다시 쓰므로 오래 켜 둔 시스템의 `dmesg` 에는 앞선 연결이 없을 수 있습니다[19].
- udev 데이터베이스·`/dev/disk/by-*`·sysfs 에 기록이 없다는 것은 연결이 없었다는 뜻이 아닙니다. 이 셋은 디스크에 저장되지 않는 파일 시스템이라 재부팅하면 남지 않습니다[14].
- USB 연결 때 명령을 돌리는 udev 규칙은 지속성에 쓰일 수 있습니다[16]. 규칙 파일의 위치와 수집 범위는 [udev 규칙](../persistence/udev-rules.md) 에서 다룹니다.
- 로그 파일을 지우거나 순환본만 남긴 흔적을 가리는 법은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md) 에서 다룹니다. 저널과 rsyslog 파일 양쪽에 같은 연결 줄이 있는지 맞춰 보면 한쪽만 손댄 경우가 드러납니다.

## 직접 분석해 보기

### 헥스로 한 번: udev 데이터베이스 파일

아래는 udev 데이터베이스 파일의 줄 형식으로 만든 예시입니다. 링크 이름과 값은 지어낸 것입니다.

```
00000000: 533a 6469 736b 2f62 792d 6964 2f75 7362  S:disk/by-id/usb
00000010: 2d45 5841 4d50 4c45 5f53 4552 4941 4c0a  -EXAMPLE_SERIAL.
00000020: 493a 3531 3233 3435 3637 3839 0a45 3a49  I:5123456789.E:I
00000030: 445f 4653 5f55 5549 445f 454e 433d 3132  D_FS_UUID_ENC=12
00000040: 3334 2d41 4243 440a                      34-ABCD.
```

1. 0x00 의 `53 3a`(`S:`)부터 0x1F 의 `0a` 앞까지가 링크 하나입니다. 앞에 `/dev/` 를 붙이면 `/dev/disk/by-id/usb-EXAMPLE_SERIAL` 이 됩니다[11].
2. 0x20 의 `49 3a`(`I:`) 뒤 `5123456789` 는 부팅 뒤 5,123,456,789마이크로초, 곧 약 85분 23초에 장치를 처음 초기화했다는 뜻입니다[11].
3. 0x2D 의 `45 3a`(`E:`) 뒤는 속성 `ID_FS_UUID_ENC=1234-ABCD` 입니다. 이 값이 gvfs 트리 이름 `uuid-1234-ABCD` 와 같은지 맞춰 봅니다[15].

### 공개 도구로 한 번

```
journalctl -D /mnt/evidence/var/log/journal --list-boots
journalctl -D /mnt/evidence/var/log/journal -k -b -2 -o short-iso | grep -E "USB device number|USB disconnect|SerialNumber|Attached SCSI"
journalctl -D /mnt/evidence/var/log/journal _KERNEL_SUBSYSTEM=usb -o verbose
grep -hE "USB device number|USB disconnect|SerialNumber" /mnt/evidence/var/log/kern.log*
vol -f memory.lime linux.kmsg
```

저널에서는 부팅을 먼저 뽑고 `-k` 와 `-b` 로 한 부팅씩 커널 항목을 거릅니다[9]. `-o verbose` 로 보면 `_KERNEL_DEVICE`·`_UDEV_DEVNODE` 필드까지 나와 어느 장치의 줄인지 가릴 수 있습니다[8]. Velociraptor 의 `Linux.Forensics.Journal.Fields` 는 필드 값마다 처음·마지막 시각과 개수를 뽑으므로, `_KERNEL_DEVICE` 값별로 장치가 붙어 있던 기간을 빠르게 좁힐 수 있습니다[17]. 이 아티팩트는 systemd 252 부터 쓰는 compact 형식 저널만 읽고 옛 형식 파일은 건너뜁니다[17]. 전용 파서 없이 저널·syslog 파서의 결과에서 위 문구로 거르면 됩니다.

라이브에서는 `lsusb`, `lsusb -vv`, `ls -l /dev/disk/by-*`, `udevadm info --export-db` 결과를 받습니다[13][16]. 메모리 이미지에서는 Volatility 3 의 `linux.kmsg` 로 링 버퍼를 읽습니다[19]. 라이브 수집 순서는 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md), 메모리 분석 절차는 [메모리 분석](../../03-techniques/analysis/memory-analysis.md) 에서 다룹니다.

## 교차 검증

| 맞춰 볼 기록 | 확인할 것 |
|---|---|
| `Attached SCSI removable disk` 의 `[sdb]` ↔ [마운트 기록](mounts.md) 의 장치 이름 | 인식한 장치를 언제 어디에 마운트했는지, 어느 uid 가 요청했는지 |
| 커널 로그 연결 시각 ↔ [로그인 기록](../logins/wtmp-btmp-lastlog.md) | 그 시간대에 로그인해 있던 계정 |
| 연결 기간 ↔ [최근 연 파일](../execution/recently-used.md) | 마운트 경로 아래 파일을 연 기록 |
| 연결 기간 ↔ [셸 명령 기록](../execution/shell-history/index.md) | `mount`·`cp`·`rsync` 같은 명령 |
| 매체 볼륨 ↔ [휴지통](../file-activity/trash.md) | 매체 안 `.Trash-*` 폴더. dissect.target 은 마운트 지점과 `/mnt`·`/media` 아래 `.Trash-*` 까지 훑음[18] |
| gvfs 트리 이름 `uuid-`·`label-` ↔ 마운트 기록의 UUID·레이블 | 그 볼륨 위 파일을 GNOME 파일 관리자가 다룬 적이 있는지 |
| 저널 커널 항목 ↔ `kern.log`·`messages` | 같은 연결 줄이 양쪽에 있는지 |

여러 기록을 한 줄로 세우는 법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 실습

NIST CFReDS 등에 공개된 Linux 디스크·메모리 이미지로 다음 질문을 풀어 봅니다.

1. 저널에서 `USB device number` 줄과 `USB disconnect` 줄을 부팅별로 뽑아 연결·해제 쌍을 만들면 몇 쌍인가? 같은 장치 번호가 다시 쓰인 곳이 있는가?
2. `SerialNumber` 줄이 있는 장치는 몇 개이고, 같은 시리얼이 여러 부팅에 걸쳐 나오는가?
3. `Attached SCSI removable disk` 줄의 디스크 이름으로 이어지는 마운트 기록이 있는가?
4. 사용자 홈의 `gvfs-metadata` 에 `uuid-` 로 시작하는 파일이 있다면, 그 UUID 를 가진 볼륨이 로그 어디에 나오는가?
5. 메모리 이미지가 있다면 `linux.kmsg` 결과에만 있고 디스크 저널에는 없는 USB 연결 줄이 있는가?

## 참고 문헌

1. Linux kernel, drivers/usb/core/hub.c. https://github.com/torvalds/linux/blob/master/drivers/usb/core/hub.c
2. Linux kernel, drivers/usb/core/Kconfig. https://github.com/torvalds/linux/blob/master/drivers/usb/core/Kconfig
3. Linux kernel, drivers/usb/common/common.c. https://github.com/torvalds/linux/blob/master/drivers/usb/common/common.c
4. Linux kernel, drivers/usb/storage/usb.c·uas.c. https://github.com/torvalds/linux/tree/master/drivers/usb/storage
5. Linux kernel, drivers/scsi/sd.c·sd.h. https://github.com/torvalds/linux/blob/master/drivers/scsi/sd.c , https://github.com/torvalds/linux/blob/master/drivers/scsi/sd.h
6. Linux kernel, drivers/usb/core/sysfs.c. https://github.com/torvalds/linux/blob/master/drivers/usb/core/sysfs.c
7. Linux kernel, drivers/base/core.c. https://github.com/torvalds/linux/blob/master/drivers/base/core.c
8. systemd, man/systemd.journal-fields.xml. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
9. systemd, man/journalctl.xml. https://github.com/systemd/systemd/blob/main/man/journalctl.xml
10. util-linux, dmesg(1). https://github.com/util-linux/util-linux/blob/master/sys-utils/dmesg.1.adoc
11. systemd, src/libsystemd/sd-device/device-private.c·sd-device.c. https://github.com/systemd/systemd/tree/main/src/libsystemd/sd-device
12. systemd, rules.d/60-persistent-storage.rules.in. https://github.com/systemd/systemd/blob/main/rules.d/60-persistent-storage.rules.in
13. systemd, man/udev.xml·udevadm.xml. https://github.com/systemd/systemd/blob/main/man/udev.xml , https://github.com/systemd/systemd/blob/main/man/udevadm.xml
14. UAPI Group, Linux File System Hierarchy. https://github.com/uapi-group/specifications/blob/main/specs/linux_file_system_hierarchy.md
15. GNOME gvfs, metadata/meta-daemon.c·metatree.c. https://github.com/GNOME/gvfs/tree/master/metadata
16. UAC, artifacts(live_response/hardware/lsusb.yaml·live_response/storage/ls_dev_disk.yaml·files/system/gvfs_metadata.yaml·files/system/udev.yaml). https://github.com/tclahr/uac/tree/main/artifacts
17. Velociraptor, artifacts/definitions/Linux/Forensics/Journal/Fields.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Forensics/Journal/Fields.yaml
18. fox-it dissect.target, dissect/target/plugins/os/unix/log/journal.py·unix/trash.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/journal.py , https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/trash.py
19. Volatility 3, volatility3/framework/plugins/linux/kmsg.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/kmsg.py
20. rsyslog-pkg-ubuntu, noble 패키지 설정(rsyslog.conf·50-default.conf). https://github.com/rsyslog/rsyslog-pkg-ubuntu/tree/master/rsyslog/noble/v8-stable/debian
21. CentOS Stream 9 rsyslog 패키지, rsyslog.conf. https://gitlab.com/redhat/centos-stream/rpms/rsyslog/-/blob/c9s/rsyslog.conf
