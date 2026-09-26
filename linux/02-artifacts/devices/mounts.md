---
title: "마운트 기록"
parent: "아티팩트 · 외부 장치"
nav_order: 890
---

# 마운트 기록 (Mount)

어떤 볼륨을 언제, 어디에, 어떤 옵션으로 붙였는지는 설정 파일(`/etc/fstab`), 라이브 시스템의 `/proc` 목록, 로그의 마운트 줄, 그리고 ext 계열 볼륨의 슈퍼블록에 나뉘어 남습니다.

## 무엇을 기록하나 · 왜 생기나

Linux 는 USB 저장 장치를 꽂는 것만으로 파일을 읽을 수 있게 되지 않습니다. 커널이 장치를 블록 장치(`sdb` 등)로 잡은 뒤, 누군가 그 위의 파일 시스템을 디렉터리에 마운트 (mount) 해야 합니다. 장치를 잡는 과정의 흔적은 [USB 장치 연결 기록](usb.md)에서 다루고, 이 페이지는 그다음 단계인 마운트의 흔적을 다룹니다.

마운트를 하는 주체는 셋으로 나뉩니다. 부팅 때는 systemd 가 `/etc/fstab` 을 읽어 마운트 단위 (mount unit) 로 바꾼 뒤 마운트합니다[6]. 관리자는 `mount` 명령으로 직접 붙입니다[2]. 데스크톱에서는 udisks2 데몬(udisksd)이 사용자를 대신해 이동식 매체를 `/media` 나 `/run/media` 아래에 붙입니다[13]. 주체마다 남기는 로그 줄이 다르고, 파일 시스템 드라이버(ext4, XFS)는 주체와 상관없이 커널 로그에 따로 줄을 남깁니다[10][12].

ext 계열(ext2·ext3·ext4) 볼륨은 슈퍼블록에 마지막 마운트 시각, 마운트 횟수, 마지막으로 마운트된 디렉터리를 적습니다[9]. 이 값은 매체 자체에 남기 때문에 USB 매체를 다른 컴퓨터에 꽂았던 흔적까지 매체를 확보하면 읽을 수 있습니다.

## 위치와 버전별 차이

| 기록 | 위치 | 성격 |
|---|---|---|
| 마운트 설정 | `/etc/fstab` | 디스크에 남음. 부팅 때 마운트할 목록[1] |
| 현재 마운트 목록 | `/proc/mounts` (`/proc/self/mounts` 로 가는 링크) | 라이브 전용. 읽는 프로세스의 마운트 이름공간만 보임[3] |
| 현재 마운트 자세히 | `/proc/[pid]/mountinfo` | 라이브 전용. 마운트 ID·부모 ID·전파 정보[4] |
| mtab | `/etc/mtab` | `../proc/self/mounts` 로 가는 심볼릭 링크[5] |
| libmount 사설 파일 | `/run/mount` | tmpfs, `user` 옵션 마운트의 사용자 이름을 적음[2] |
| fstab 에서 만든 단위 | `/run/systemd/generator` | tmpfs, 부팅마다 다시 만듦[6] |
| udisks 상태 (비영구 마운트 지점) | `/run/udisks2/mounted-fs` | tmpfs[13] |
| udisks 상태 (영구 마운트 지점) | `/var/lib/udisks2/mounted-fs-persistent` | 디스크에 남음[13] |
| 로그 | systemd 저널, rsyslog 파일 | 커널·systemd·udisksd 가 남긴 줄 |
| ext 계열 슈퍼블록 | 볼륨 시작에서 1024바이트 위치 | 매체 자체에 남음[9] |
| 메모리 | 커널의 마운트 이름공간 구조 | 메모리 이미지에서 복원[21] |

`/run` 은 tmpfs 라서 부팅할 때마다 비워집니다[8]. 전원을 끈 뒤 만든 디스크 이미지에는 `/run` 아래 파일이 없고, `/etc/mtab` 도 가리킬 곳이 없는 링크로만 남습니다. util-linux 는 일반 파일인 mtab 을 쓰는 기능을 컴파일할 때 기본으로 끄므로[2], 일반 파일인 `/etc/mtab` 이 있다면 오래된 시스템일 가능성이 있습니다.

배포판마다 달라지는 곳은 udisks 의 마운트 위치와 로그 파일입니다.

| 항목 | Ubuntu 24.04 (Debian 계열) | RHEL 9 |
|---|---|---|
| udisks 마운트 지점 | `/media/사용자/레이블` — Debian 패키징이 `--enable-fhs-media` 로 빌드[15] | `/run/media/사용자/레이블` — upstream 기본값[13][16] |
| udisks 상태 파일 | `/var/lib/udisks2/mounted-fs-persistent` 에 남음(`/media` 는 영구 경로) | 사용자 폴더 아래 마운트는 `/run/udisks2/mounted-fs` 에만 있음(tmpfs) |
| 커널 줄이 가는 rsyslog 파일 | `/var/log/kern.log`, `/var/log/syslog` | `/var/log/messages` |

udisks 의 두 경로 차이는 빌드 옵션 하나에서 나옵니다. configure 의 `--enable-fhs-media` 를 켜면 `/run/media` 대신 `/media` 에 마운트하고 마운트 지점을 영구 경로로 분류하며, 기본값은 꺼짐입니다[13]. RHEL 9 계열인 Rocky Linux 9.4 재빌드 spec(udisks2 2.9.4)에는 이 옵션이 없습니다[16]. rsyslog 파일 배치는 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)에서 다룹니다.

## 구조

### /etc/fstab

한 줄에 파일 시스템 하나를 적고, 필드는 탭이나 공백으로 나눕니다. 그래서 필드 안의 공백과 탭은 따옴표 안에서도 `\040`, `\011` 로 적어야 합니다[1]. 필드는 여섯 개입니다.

| 순서 | 이름 | 뜻 |
|---|---|---|
| 1 | fs_spec | 장치. `/dev/sdb1` 말고도 `LABEL=`, `UUID=`, `PARTUUID=`, `PARTLABEL=` 로 적을 수 있음 |
| 2 | fs_file | 마운트 지점 |
| 3 | fs_vfstype | 파일 시스템 형식 |
| 4 | fs_mntops | 마운트 옵션 |
| 5 | fs_freq | dump 용. 없으면 0 |
| 6 | fs_passno | fsck 순서. 루트는 1, 나머지는 2, 없으면 0 |

UUID 는 소문자 문자열로 적고, FAT·NTFS 볼륨 ID 는 `UUID="A40D-85E7"` 처럼 대문자로 적습니다[1]. 흔적 해석에 쓸모 있는 옵션은 `noauto`(부팅 때 마운트하지 않음), `nofail`(장치가 없어도 오류로 보지 않음), `user`(일반 사용자에게 마운트 허용)입니다[1]. `user` 는 `noexec`, `nosuid`, `nodev` 를 함께 뜻하고, 마운트한 사용자 이름을 mtab 이나 `/run/mount` 사설 파일에 적습니다[2].

systemd-fstab-generator 는 fstab 줄마다 마운트 단위를 만들고, 단위 이름은 마운트 지점 경로를 바꾼 것입니다(`/home/lennart` → `home-lennart.mount`)[6]. fstab 에 없이 런타임에 생긴 마운트도 systemd 가 `/proc/self/mountinfo` 를 보고 마운트 단위로 나타냅니다[6].

### /proc/[pid]/mountinfo

커널 문서의 예시 줄과 필드는 아래와 같습니다[4].

```
36 35 98:0 /mnt1 /mnt2 rw,noatime master:1 - ext3 /dev/root rw,errors=continue
```

| 필드 | 예시 값 | 뜻 |
|---|---|---|
| mount ID | `36` | 마운트 고유 번호. 해제 뒤 다시 쓰일 수 있음 |
| parent ID | `35` | 부모 마운트 번호 |
| major:minor | `98:0` | 장치 번호(st_dev) |
| root | `/mnt1` | 파일 시스템 안에서 이 마운트의 뿌리. bind 마운트를 가려내는 단서 |
| mount point | `/mnt2` | 프로세스 루트 기준 마운트 지점 |
| mount options | `rw,noatime` | 마운트별 옵션 |
| 선택 필드 | `master:1` | `shared:X`, `master:X`, `propagate_from:X`, `unbindable` |
| 구분자 | `-` | 선택 필드의 끝 |
| filesystem type | `ext3` | `형식[.하위형식]` |
| mount source | `/dev/root` | 장치나 원본 |
| super options | `rw,errors=continue` | 슈퍼블록 옵션 |

같은 위치에 마운트를 겹치면 새 마운트의 부모는 이전 마운트가 됩니다[3]. 그래서 어떤 줄의 부모 ID 가 같은 마운트 지점에 있는 다른 줄의 마운트 ID 이면, 그 부모 마운트는 새 마운트에 가려진 것입니다. `/proc/mounts` 는 fstab 과 같은 형식이고 읽는 프로세스의 이름공간만 보여 주므로, 컨테이너처럼 다른 이름공간의 마운트는 그 안의 프로세스 번호로 `/proc/[pid]/mountinfo` 를 따로 읽어야 합니다[3].

### 로그 줄

로그 줄 모양은 커널 판과 udisks 판에 따라 다릅니다. 아래 표의 `%s`, `%pU` 자리에는 장치 이름이나 UUID 가 들어갑니다.

**ext4.** 줄 머리는 `EXT4-fs (장치이름): ` 이고, 장치 이름은 `sdb1` 같은 커널 블록 장치 이름입니다[10].

| 동작 | Linux v5.14 | Linux v6.8 |
|---|---|---|
| 마운트 | `mounted filesystem with%s. Opts: %.*s%s%s. Quota mode: %s.` | `mounted filesystem %pU %s with%s. Quota mode: %s.` |
| 다시 마운트 | `re-mounted. Opts: %s. Quota mode: %s.` | `re-mounted %pU %s. Quota mode: %s.` |
| 해제 | 줄 없음 | `unmounting filesystem %pU.` |

v6.8 형식의 둘째 `%s` 는 `ro` 나 `r/w` 이고, `with%s` 는 ` ordered data mode` 같은 데이터 모드가 붙어 `with ordered data mode` 가 되며 저널이 없으면 `without journal` 이 됩니다[10][11]. v5.14 형식에는 UUID 가 없고 대신 옵션 문자열이 들어갑니다[11]. 최신 커널(master)은 다시 마운트 줄이 `re-mounted %pU%s.` 로 또 바뀌었습니다[10]. 어느 형식인지는 실제 로그 줄을 보고 정합니다.

쓰기 가능으로 마운트할 때 볼륨 상태에 따라 `warning: mounting unchecked fs, running e2fsck is recommended`, `warning: mounting fs with errors, running e2fsck is recommended`, `warning: maximal mount count reached, ...`, `warning: checktime reached, ...` 가운데 한 줄이 남을 수 있습니다[10]. 첫 줄은 s_state 의 정상 해제 비트가 꺼진 볼륨에서, 둘째 줄은 오류 비트가 켜진 볼륨에서 남습니다[10]. 저널이 있는 ext4 는 마운트 중에도 정상 해제 비트를 끄지 않으므로, 첫 줄은 주로 저널 없는 볼륨을 정상 해제하지 않았다는 단서입니다.

**XFS.** 줄 머리는 `XFS (장치이름): ` 이고, 마운트하면 `Mounting V%d Filesystem %pU` 다음에 `Ending clean mount` 가 남습니다[12]. 저널을 되살렸으면 `Ending recovery (logdev: %s)` 가, 해제하면 `Unmounting Filesystem %pU` 가 남습니다[12].

**systemd.** 마운트 단위의 작업이 시작되고 끝날 때 `Mounting %s...`, `Mounted %s.`, `Failed to mount %s.`, `Timed out mounting %s.`, `Unmounting %s...`, `Unmounted %s.`, `Failed unmounting %s.` 가 남습니다[7]. `%s` 는 단위 설명이고, 설명이 없으면 마운트 지점 경로를 설명으로 씁니다[7]. fstab 에서 만든 단위라면 `Mounted /boot.` 같은 줄이 됩니다(만든 예시).

**udisks2.** 데스크톱 자동 마운트는 사용자 번호(uid)를 남깁니다.

| udisks 판 | 마운트 | 해제 |
|---|---|---|
| 2.9.4 | `Mounted %s at %s on behalf of uid %u`, fstab 항목은 `Mounted %s (system) at %s on behalf of uid %u` | `Unmounted %s on behalf of uid %u`, `Unmounted %s (system) from %s on behalf of uid %u` |
| 2.10.1 | `Mounted %s%s at %s on behalf of uid %u` (둘째 `%s` 가 ` (system)`) | 2.9.4 와 같음 |
| 최신(master) | 같은 문구에 요청자가 다르면 ` (requested by uid %u)` 가 붙음 | 같은 문구 |

2.9.4 와 2.10.1 은 이 줄을 notice 매크로로 남기고, 이 매크로는 GLib 의 MESSAGE 수준입니다[13][14]. 최신 코드는 같은 줄을 info 매크로로 바꿨는데, 이 매크로는 디버그 빌드에서만 코드가 들어가고 기본 빌드에서는 빈 매크로입니다[13]. 그래서 udisks 판에 따라 이 줄이 아예 없을 수 있으므로, 분석 대상의 udisks2 패키지 판을 먼저 봅니다. 암호화 볼륨을 열고 닫으면 `Unlocked device %s as %s`, `Locked device %s (was unlocked as %s)` 도 남습니다[13].

아래는 2.10.1 형식으로 만든 예시입니다.

```
Mounted /dev/sdb1 at /media/alice/EXAMPLE on behalf of uid 1000
```

**udisks 마운트 지점 이름.** 사용자 이름을 알면 `마운트기준/사용자` 폴더를 만들고, 그 아래 이름은 볼륨 레이블, 레이블이 없으면 UUID, 둘 다 없으면 `disk` 로 정합니다[13]. 같은 이름이 이미 있으면 뒤에 숫자를 붙이고, `UDISKS_FILESYSTEM_SHARED` 속성이 붙은 장치는 `/media` 바로 아래에 붙입니다[13]. 해제할 때 fstab 마운트가 아니면 마운트 지점 폴더를 지우므로, `/media/사용자/` 는 남아도 그 아래 레이블 폴더는 남지 않는 것이 정상입니다[13].

**udisks 상태 파일.** `mounted-fs` 와 `mounted-fs-persistent` 는 GVariant 로 직렬화한 파일이고, 마운트 지점마다 `block-device`(장치 번호), `mounted-by-uid`(사용자 번호), `fstab-mount`(fstab 여부)를 담습니다[13]. 항목은 여전히 마운트되어 있고 장치가 있을 때만 유지되므로 정상 해제 뒤에는 지워집니다[13]. 이 파일에 항목이 남아 있으면 수집 시점에 마운트 중이었거나 비정상 종료로 정리되지 못한 경우일 가능성이 있습니다.

### ext 계열 슈퍼블록

슈퍼블록은 볼륨 시작에서 1024바이트(0x400) 위치에 있습니다[9]. 아래 절대 위치는 0x400 에 필드 오프셋을 더해 계산한 값이고, 전체 필드 설명은 [슈퍼블록과 블록 그룹](../../01-foundations/filesystem/ext4/superblock-block-group.md) 페이지에 있습니다.

| 필드 | 오프셋 | 절대 위치 | 크기 | 뜻 |
|---|---|---|---|---|
| s_mtime | 0x2C | 0x42C | le32 | 마지막 마운트 시각(epoch 초) |
| s_wtime | 0x30 | 0x430 | le32 | 마지막 슈퍼블록 쓰기 시각 |
| s_mnt_count | 0x34 | 0x434 | le16 | 마지막 fsck 이후 마운트 횟수 |
| s_max_mnt_count | 0x36 | 0x436 | le16 | 이 횟수를 넘으면 fsck 필요 |
| s_magic | 0x38 | 0x438 | le16 | 0xEF53 |
| s_state | 0x3A | 0x43A | le16 | 0x0001 정상 해제, 0x0002 오류, 0x0004 고아 아이노드 복구 중 |
| s_lastcheck | 0x40 | 0x440 | le32 | 마지막 점검 시각 |
| s_feature_incompat | 0x60 | 0x460 | le32 | 0x4 비트는 needs recovery(INCOMPAT_RECOVER) |
| s_uuid | 0x68 | 0x468 | 16바이트 | 볼륨 UUID |
| s_volume_name | 0x78 | 0x478 | 16바이트 | 볼륨 레이블 |
| s_last_mounted | 0x88 | 0x488 | 64바이트 | 마지막으로 마운트된 디렉터리 |
| s_kbytes_written | 0x178 | 0x578 | le64 | 볼륨이 생긴 뒤 쓴 양(KiB) |
| s_mount_opts | 0x200 | 0x600 | 64바이트 | 마운트 옵션 문자열(ASCIIZ) |
| s_wtime_hi, s_mtime_hi | 0x274, 0x275 | 0x674, 0x675 | 각 1바이트 | 시각 값의 상위 8비트 |

커널 코드로 보면 각 값은 이렇게 바뀝니다[10].

- **s_mnt_count, s_mtime**: 마운트할 때 횟수를 1 올리고 현재 시각을 적습니다. 읽기 전용 마운트는 이 과정을 건너뛰므로 두 값이 바뀌지 않습니다.
- **s_last_mounted**: 마운트하는 순간이 아니라, 마운트 뒤 처음 파일을 열 때 한 번 마운트 지점 경로를 적습니다. 읽기 전용이면 적지 않습니다. 경로를 담는 필드는 64바이트입니다.
- **s_wtime**: 슈퍼블록을 디스크에 쓸 때마다 바뀝니다. 읽기 전용이면 바꾸지 않습니다.
- **needs recovery (0x4)**: 저널이 있는 볼륨을 쓰기 가능으로 마운트하면 켜고, 정상 해제하면 끕니다.
- **s_state**: 저널이 있는 ext4 는 마운트 중에도 s_state 의 정상 해제 비트를 끄지 않고, 저널이 없을 때만 끕니다.

## 증거로서 의미

**증명하는 것**

- `/etc/fstab` 은 관리자가 부팅 때 붙이도록 설정한 장치·위치·옵션을 보여 줍니다. 설정일 뿐 실제로 마운트한 기록은 아닙니다.
- `/proc/mounts`, `/proc/[pid]/mountinfo`, 메모리의 마운트 목록은 수집 시점에 붙어 있던 마운트와 옵션(`ro`·`rw`, `noexec` 등), 그리고 어느 이름공간의 마운트인지를 보여 줍니다.
- 커널과 systemd 의 줄은 그 시각에 어떤 장치 이름(`sdb1`)이나 UUID 의 볼륨이 어떤 모드로 마운트·해제되었는지를 보여 줍니다.
- udisks 줄은 이 줄을 남기는 판이라면 어떤 장치를 어느 경로에 어느 uid 를 대신해 붙였는지를 보여 줍니다. 마운트를 사용자 계정과 잇는 기록은 사실상 이것뿐입니다.
- ext 계열 슈퍼블록은 그 매체가 마지막으로 쓰기 가능 마운트된 시각(s_mtime), 마운트 뒤 파일이 처음 열렸을 때의 마운트 경로(s_last_mounted), 마지막 fsck 이후 마운트 횟수를 보여 줍니다.

**증명하지 못하는 것**

- 마운트는 파일을 열람하거나 복사했다는 뜻이 아닙니다. s_last_mounted 가 채워졌다면 파일이 하나 이상 열렸다는 것까지만 알 수 있고, 어떤 파일인지는 알 수 없습니다[10].
- s_mtime 과 s_last_mounted 는 마지막 값 하나만 남고 이전 값은 덮어씁니다. 읽기 전용 마운트는 두 값을 바꾸지 않습니다[10].
- s_last_mounted 에는 경로만 있고 어느 컴퓨터에서 마운트했는지는 없습니다. `/media/alice/EXAMPLE` 같은 경로가 있다면 사용자 이름이 `alice` 인 컴퓨터에서 udisks 가 붙였을 가능성이 있다는 정도로만 씁니다.
- fstab 에 없다고 해서 마운트가 없었던 것은 아닙니다. 수동 마운트와 udisks 마운트는 fstab 을 거치지 않습니다.

보고서에는 "2024-07-24 07:48:16 UTC 에 커널 로그에 sdb1 볼륨을 쓰기 가능으로 마운트한 기록이 있다"처럼 기록으로 확인되는 만큼만 씁니다(만든 예시).

## 시각 해석

로그 줄의 시각은 어디에 저장되었는지에 따라 다릅니다. 저널은 UTC 기준 마이크로초 값을 저장하고, rsyslog 전통 형식 파일은 연도와 시간대가 없는 현지 시각을 적습니다. 자세한 내용은 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md), [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md), [시간대](../system-info/hostname-timezone.md) 페이지를 봅니다.

ext 슈퍼블록 시각은 epoch 초로 적은 UTC 기준 값입니다[9]. 커널은 하위 32비트를 부호 없는 값으로 적고 그 위 자리를 상위 8비트(`_hi`)에 적으므로[10], 2106년 이후 값은 둘을 합쳐야 맞습니다. 커널은 적을 때 시스템 시계를 그대로 쓰므로 시계가 틀리면 값도 틀립니다[10]. Windows 와 맞추려고 하드웨어 시계를 현지 시각으로 두는 컴퓨터는 시계가 시간대만큼 앞서 있을 수 있으므로[10], 이중 부팅 컴퓨터에서 쓴 매체는 시간대만큼 어긋났을 가능성을 따져 봅니다. 값 변환은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)을 봅니다.

mountinfo 에는 시각이 없습니다[4]. 마운트 시각은 로그나 슈퍼블록에서만 얻습니다.

마운트 옵션은 그 볼륨 파일들의 접근 시각 (atime) 갱신 방식을 정합니다. Linux 2.6.30 부터 커널 기본값인 `relatime` 은 이전 접근 시각이 수정·변경 시각보다 이르거나 같을 때, 또는 1일 넘게 지났을 때만 접근 시각을 갱신합니다[2]. `noatime` 은 아예 갱신하지 않고 `nodiratime` 도 포함합니다[2]. 접근 시각을 끄는 설정은 SSD 와 USB 플래시 드라이브에 흔히 권장됩니다[23]. 그래서 USB 매체 파일의 접근 시각으로 열람을 주장하기 전에 mountinfo, fstab, 슈퍼블록 s_mount_opts 에서 옵션을 먼저 확인합니다.

## 함정과 한계

- **사후 이미지의 빈자리.** `/etc/mtab`, `/run/mount`, `/run/udisks2/mounted-fs`, `/run/systemd/generator` 는 전원을 끈 이미지에 내용이 없습니다[5][8]. 현재 마운트 상태가 필요하면 라이브 수집이나 메모리 이미지를 씁니다.
- **지워지는 마운트 지점.** udisks 는 해제 때 레이블 폴더를 지웁니다[13]. `/media/사용자/` 아래가 비어 있어도 매체를 붙이지 않았다는 뜻이 아닙니다.
- **없는 udisks 줄.** 최신 udisks 기본 빌드는 `Mounted ... on behalf of uid` 줄을 남기지 않을 수 있습니다[13]. 줄이 없으면 먼저 패키지 판을 봅니다.
- **빠지는 커널 줄.** ext4 마운트·해제 줄은 속도 제한을 거치고, 30초에 64줄로 제한합니다[10][11]. 짧은 시간에 여러 볼륨을 붙였다 떼면 일부 줄이 빠질 수 있습니다.
- **판마다 다른 줄 모양.** ext4 줄은 v5.14 와 v6.8 에서 모양이 다르고, v5.14 형식에는 해제 줄과 UUID 가 없습니다[11]. 줄을 찾는 검색어는 `EXT4-fs (` 처럼 짧게 잡습니다.
- **"Unmounted properly" 문구.** The Sleuth Kit `fsstat` 은 s_state 의 정상 해제 비트만 보고 `Unmounted properly` 나 `Unmounted Improperly` 를 찍습니다[22]. 저널이 있는 ext4 는 마운트 중에도 이 비트를 끄지 않으므로[10], 비정상 해제를 판단할 때는 s_feature_incompat 의 needs recovery(0x4) 비트를 함께 봅니다.
- **fsstat 의 시각 범위.** `fsstat` 은 s_mtime·s_wtime 의 하위 32비트만 읽습니다[22]. 2106년 이후 값은 상위 8비트를 직접 더해 봅니다.
- **도구가 푸는 방식.** Velociraptor `Linux.Mounts` 는 `/proc/mounts` 를 공백 기준 정규식으로 자르므로 `\040` 같은 이스케이프가 그대로 보일 수 있습니다[19][1]. dissect.target 의 fstab 파서는 필드가 정확히 여섯 개인 줄만 받고 swap·tmpfs·overlayfs 등과 `/` 줄은 건너뜁니다[20]. fstab(5) 은 다섯째·여섯째 필드를 생략할 수 있게 하므로[1], 필드가 넷인 줄은 도구 결과에서 빠질 수 있습니다.
- **흔적 지우기.** 로그 줄과 fstab 은 루트 권한으로 고칠 수 있습니다. 슈퍼블록은 매체에 따로 남으므로 로그와 대조하면 어긋난 곳이 드러날 수 있습니다. 로그를 지운 흔적을 찾는 방법은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

ext4 볼륨 이미지의 0x420 부터를 헥스로 보면 아래와 같은 모양이 됩니다. 명세의 오프셋에 맞춰 만든 예시이고 값은 지어낸 것입니다.

```
00000420  00 80 00 00 00 80 00 00  00 20 00 00 c0 b1 a0 66  |......... .....f|
00000430  ec b2 a0 66 07 00 ff ff  53 ef 01 00 01 00 00 00  |...f....S.......|
00000460  c6 02 00 00 7b 00 00 00  3e 2c 8a 51 0d 4f 4b 1e  |....{...>,.Q.OK.|
00000470  9a 61 5c 22 e7 04 b3 d8  45 58 41 4d 50 4c 45 00  |.a\"....EXAMPLE.|
00000480  00 00 00 00 00 00 00 00  2f 6d 65 64 69 61 2f 61  |......../media/a|
00000490  6c 69 63 65 2f 45 58 41  4d 50 4c 45 00 00 00 00  |lice/EXAMPLE....|
```

1. 0x438 의 `53 ef` 가 매직 0xEF53 이면 ext 계열 슈퍼블록입니다.
2. 0x42C 의 `c0 b1 a0 66` 을 리틀 엔디언으로 읽으면 0x66A0B1C0 이고, 0x675 의 s_mtime_hi 가 0 이면 epoch 초 1721807296, 곧 2024-07-24 07:48:16 UTC 입니다. 이 시각이 마지막 쓰기 가능 마운트 시각입니다.
3. 0x430 의 `ec b2 a0 66` 은 s_wtime 이고, 2024-07-24 07:53:16 UTC 입니다.
4. 0x434 의 `07 00` 은 마지막 fsck 이후 7번 마운트했다는 뜻입니다.
5. 0x460 의 `c6 02 00 00` 은 0x2C6 이고 0x4 비트가 켜져 있습니다. 저널을 되살려야 하는 상태, 곧 쓰기 가능으로 마운트된 채 이미지를 떴거나 정상 해제 없이 뽑았을 가능성이 있습니다. 0x43A 의 s_state 는 `01 00` 이지만 저널이 있는 ext4 라서 이 값만으로는 판단하지 않습니다.
6. 0x478 부터 레이블 `EXAMPLE`, 0x488 부터 s_last_mounted `/media/alice/EXAMPLE` 이 이어집니다. udisks 의 `/media/사용자/레이블` 규칙과 모양이 같아서 Debian·Ubuntu 계열 데스크톱에서 붙였을 가능성이 있습니다.

### 공개 도구로 한 번

- **라이브**: `findmnt`, `mount`, `lsblk -f`, `blkid`, `df` 출력을 받습니다. UAC 는 이 명령 출력을 모으고[18], ForensicArtifacts 의 `LinuxMountInfo` 는 `/etc/fstab` 과 `/proc/mounts` 를 묶어 정의합니다[17]. Velociraptor `Linux.Mounts` 는 `/proc/mounts` 를 읽습니다[19]. 컨테이너 등 다른 이름공간은 `/proc/[pid]/mountinfo` 를 따로 모읍니다.
- **사후 이미지**: dissect.target 은 fstab 을 읽어 UUID·LABEL·`/dev/mapper`·LVM 장치를 구분하고 마운트 지점에 파일 시스템을 다시 붙입니다[20]. 이때 ext 볼륨의 last mount 값이 마운트 지점과 같은지도 맞춰 봅니다[20].
- **슈퍼블록**: `fsstat 이미지파일` 을 실행하면 `Volume Name`, `Last Written at`, `Last Checked at`, `Last Mounted at`, `Last mounted on` 이 나옵니다[22]. 앞의 함정 두 가지를 함께 봅니다.
- **메모리**: Volatility 3 `linux.mountinfo` 는 프로세스별 마운트 이름공간을 따라 mountinfo 와 같은 열(MOUNT ID, PARENT_ID, MAJOR:MINOR, ROOT, MOUNT_POINT, MOUNT_OPTIONS, FIELDS, FSTYPE, MOUNT_SRC, SB_OPTIONS)을 내고, `--mntns` 로 이름공간을 거를 수 있습니다[21]. 메모리 분석 일반은 [메모리 분석](../../03-techniques/analysis/memory-analysis.md)을 봅니다.
- **로그**: `journalctl -k` 로 커널 줄을 보고 `EXT4-fs (`, `XFS (`, `on behalf of uid` 로 좁힙니다. 저널 필터는 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md), 커널 로그 파일은 [커널 로그](../system-info/kernel-log.md)를 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [USB 장치 연결 기록](usb.md) | 연결 줄의 장치 이름(`sdb`)·시각과 마운트 줄의 `(sdb1)` |
| [계정 파일](../../01-foundations/users-auth/passwd-shadow-group.md) | udisks 줄의 uid 가 어느 계정인지 |
| [로그인 기록](../logins/wtmp-btmp-lastlog.md) | 마운트 시각에 그 계정이 로그인해 있었는지 |
| [셸 명령 기록](../execution/shell-history/index.md) | `mount`, `umount` 명령과 마운트 지점 경로 |
| [최근 연 파일](../execution/recently-used.md) | `/media`, `/run/media` 아래 파일을 연 기록 |
| [휴지통](../file-activity/trash.md) | 매체 안의 `.Trash-uid` 폴더. dissect.target 은 `/mnt`, `/media` 아래까지 찾음[20] |
| ext 슈퍼블록(매체) | s_mtime·s_last_mounted 와 호스트 로그의 마운트 시각·경로 |

여러 기록의 시각을 한 줄로 늘어놓는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md)를 봅니다.

## 실습

공개 Linux 시험 이미지(NIST CFReDS 등)나 직접 만든 가상 머신 이미지로 아래 질문을 풀어 봅니다.

1. `/etc/fstab` 에 `noauto` 나 `user` 옵션이 붙은 줄이 있는가? 있다면 그 장치는 부팅 뒤 누가 붙였을 가능성이 있는가?
2. 커널 로그의 `EXT4-fs (` 줄은 v5.14 형식인가 v6.8 형식인가? 해제 줄이 있는가?
3. `on behalf of uid` 줄이 있다면 uid 는 어느 계정이고, 같은 시각 USB 연결 줄의 장치 이름과 맞는가?
4. `/var/lib/udisks2/mounted-fs-persistent` 가 있는가? 항목이 남아 있다면 무엇을 뜻하는가?
5. 확보한 USB 매체 이미지의 s_last_mounted 경로와 s_mtime 은 호스트 로그의 마운트 기록과 맞는가? s_feature_incompat 의 0x4 비트는 켜져 있는가?

## 참고 문헌

1. util-linux, fstab(5) — https://github.com/util-linux/util-linux/blob/master/sys-utils/fstab.5.adoc
2. util-linux, mount(8) — https://github.com/util-linux/util-linux/blob/master/sys-utils/mount.8.adoc
3. Linux man-pages, proc(5) — https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
4. Linux kernel, Documentation/filesystems/proc.rst (3.5 /proc/pid/mountinfo) — https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.rst
5. systemd, tmpfiles.d/etc.conf.in — https://github.com/systemd/systemd/blob/main/tmpfiles.d/etc.conf.in ; RHEL 9 source-git — https://github.com/redhat-plumbers/systemd-rhel9/blob/main/tmpfiles.d/etc.conf.in
6. systemd, systemd.mount(5)·systemd-fstab-generator(8)·systemd.generator(7) — https://github.com/systemd/systemd/tree/main/man
7. systemd, src/core/mount.c — https://github.com/systemd/systemd/blob/main/src/core/mount.c
8. UAPI Group, Linux File System Hierarchy — https://github.com/uapi-group/specifications/blob/main/specs/linux_file_system_hierarchy.md
9. Linux kernel, Documentation/filesystems/ext4/super.rst·blockgroup.rst — https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/super.rst , https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/blockgroup.rst
10. Linux kernel, fs/ext4/super.c·file.c — https://github.com/torvalds/linux/blob/master/fs/ext4/super.c , https://github.com/torvalds/linux/blob/master/fs/ext4/file.c
11. Linux kernel v5.14·v6.8, fs/ext4/super.c — https://github.com/torvalds/linux/blob/v5.14/fs/ext4/super.c , https://github.com/torvalds/linux/blob/v6.8/fs/ext4/super.c
12. Linux kernel, fs/xfs (xfs_log.c·xfs_super.c·xfs_message.c) — https://github.com/torvalds/linux/tree/master/fs/xfs
13. udisks, src (udiskslinuxfilesystem.c·udisksstate.c·udiskslogging.h·udiskslinuxencrypted.c)·configure.ac — https://github.com/storaged-project/udisks/tree/master/src
14. udisks 2.9.4·2.10.1, src/udiskslinuxfilesystem.c — https://github.com/storaged-project/udisks/blob/udisks-2.9.4/src/udiskslinuxfilesystem.c , https://github.com/storaged-project/udisks/blob/udisks-2.10.1/src/udiskslinuxfilesystem.c
15. Debian udisks2 패키징(deepin-community 사본), debian/rules·changelog — https://github.com/deepin-community/udisks2/tree/master/debian
16. Rocky Linux 9.4 udisks2 재빌드, SPECS/udisks2.spec — https://github.com/ciq-rocky-lts/udisks2/blob/el-9.4/SPECS/udisks2.spec
17. ForensicArtifacts, linux.yaml·linux_proc.yaml — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml , https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux_proc.yaml
18. UAC, artifacts/live_response/storage — https://github.com/tclahr/uac/tree/main/artifacts
19. Velociraptor, Linux/Mounts.yaml — https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Mounts.yaml
20. dissect.target, plugins/os/unix/_os.py·trash.py — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/_os.py , https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/trash.py
21. Volatility 3, plugins/linux/mountinfo.py — https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/mountinfo.py
22. The Sleuth Kit, tsk/fs/ext2fs.cpp — https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs.cpp
23. Thomas Göbel, Harald Baier, "Anti-forensics in ext4: On secrecy and usability of timestamp-based data hiding", Digital Investigation 24 (2018) S111–S120, https://doi.org/10.1016/j.diin.2018.01.014
