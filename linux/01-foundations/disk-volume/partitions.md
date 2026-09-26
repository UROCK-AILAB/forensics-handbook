---
title: "파티션"
parent: "기반 · 디스크와 볼륨"
nav_order: 110
---

# 파티션 (MBR·GPT)

디스크 앞쪽의 파티션 표를 읽으면 디스크를 어떤 범위로 나눴는지, 각 조각에 어떤 용도 표시를 달았는지, 다른 흔적과 맞춰 볼 식별자가 무엇인지 알 수 있습니다.

MBR (Master Boot Record) 와 GPT (GUID Partition Table) 의 공통 구조는 Windows 판 [파티션 구조 (MBR·GPT)](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/disk-volume/mbr-gpt.html) 와 맥 판 [파티션 구조 (GPT·APFS 파티션)](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/disk-volume/gpt-partitions.html) 에도 있습니다. 이 쪽은 리눅스에서 쓰는 형식 번호·형식 GUID, 리눅스 도구가 표를 읽는 방식, 파티션과 마운트 설정을 잇는 방법을 다룹니다.

## 이 형식을 쓰는 아티팩트

파티션 표는 그 자체로 기록이라기보다 다른 흔적을 찾아 들어가는 입구입니다. 파티션 안에는 ext4·XFS·Btrfs 같은 파일 시스템, LVM 물리 볼륨, LUKS 머리글, 스왑 영역이 놓이고, 각각은 아래 쪽에서 이어서 다룹니다.

| 파티션 안에 놓이는 것 | 이어서 볼 쪽 |
|---|---|
| ext4·XFS·Btrfs 파일 시스템 | [ext4](../filesystem/ext4/index.md), [XFS](../filesystem/xfs.md), [Btrfs](../filesystem/btrfs.md) |
| LVM 물리 볼륨 | [LVM 논리 볼륨](lvm.md) |
| LUKS 로 암호화한 볼륨 | [LUKS 디스크 암호화](luks.md) |
| 스왑 영역·최대 절전 이미지 | [스왑과 최대 절전](swap-hibernation.md) |

라이브 시스템에서는 `/etc/fstab`, `/proc/partitions`, `/proc/mounts`, `/dev/disk/by-*` 링크가 파티션을 이름·UUID 로 가리킵니다[11][17][10]. 이 연결을 해석하는 방법은 [마운트 기록](../../02-artifacts/devices/mounts.md) 쪽에 모았습니다.

## 구조

### MBR

MBR 은 디스크 첫 섹터(512바이트)입니다. 0x1B8(440) 에 4바이트 디스크 식별자 (disk signature) 가 있고, 0x1BE(446) 부터 16바이트 항목 4개가 파티션 표를 이루며, 0x1FE 에 `55 AA` 두 바이트가 옵니다[1][5]. TSK 는 매직을 `DOS_MAGIC 0xaa55` 로 정의하는데, 리틀엔디언 2바이트로 읽은 값이라 디스크 바이트로는 `55 AA` 입니다[1].

항목 하나의 구성은 다음과 같습니다[1].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0x00 | 1 | 부트 표시 (0x00 또는 0x80) |
| 0x01 | 3 | 시작 CHS 주소 |
| 0x04 | 1 | 파티션 형식 번호 |
| 0x05 | 3 | 끝 CHS 주소 |
| 0x08 | 4 | 시작 LBA (리틀엔디언) |
| 0x0C | 4 | 섹터 수 (리틀엔디언) |

리눅스에서 만나는 형식 번호는 아래와 같고, 설명 문자열은 TSK 가 쓰는 이름입니다[2].

| 형식 번호 | TSK 설명 |
|---|---|
| 0x82 | Linux Swap / Solaris x86 |
| 0x83 | Linux |
| 0x85 | Linux Extended |
| 0x8e | Linux Logical Volume Manager |
| 0xfd | Linux RAID |
| 0xee | GPT Safety Partition |

형식 번호가 0x05·0x0F·0x85 인 항목은 확장 파티션이고, 그 안의 연결 표(EBR)를 따라가면 논리 파티션이 나옵니다[2]. 리눅스는 논리 파티션에 5번부터 번호를 붙이고, 비어 있는 주 파티션 칸의 번호는 다시 쓰지 않습니다[5]. 따라서 `/dev/sda5` 가 있다고 `/dev/sda1`~`sda4` 가 모두 있는 것은 아닙니다.

### GPT

GPT 디스크의 LBA 0 에는 보호용 MBR (Protective MBR) 이 있고, 형식 0xEE 항목 하나가 보통 디스크 전체를 덮고, 2TiB 를 넘는 디스크에서는 2TiB 까지만 덮습니다[6][3]. GPT 머리글은 LBA 1 에 있고 서명은 `EFI PART` 입니다[3][6]. 필드는 모두 리틀엔디언입니다[6].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x00 | 8 | signature | `EFI PART` |
| 0x08 | 4 | revision | 판 번호 |
| 0x0C | 4 | header_size | 머리글 크기, 보통 92 |
| 0x10 | 4 | header_crc32 | 머리글 CRC32 (이 칸을 0 으로 두고 계산) |
| 0x14 | 4 | reserved | 예약 |
| 0x18 | 8 | my_lba | 이 머리글이 놓인 LBA |
| 0x20 | 8 | alternate_lba | 다른 쪽 머리글의 LBA |
| 0x28 | 8 | first_usable_lba | 파티션에 쓸 수 있는 첫 LBA |
| 0x30 | 8 | last_usable_lba | 파티션에 쓸 수 있는 마지막 LBA |
| 0x38 | 16 | disk_guid | 디스크 GUID |
| 0x48 | 8 | partition_entries_lba | 항목 배열 시작 LBA, 주 머리글에서는 늘 2 |
| 0x50 | 4 | num_partition_entries | 항목 개수 |
| 0x54 | 4 | sizeof_partition_entry | 항목 하나의 크기 |
| 0x58 | 4 | partition_entry_array_crc32 | 항목 배열 CRC32 |

항목 하나는 128바이트이고 구성은 다음과 같습니다[6][3].

| 오프셋 | 크기 | 필드 |
|---|---|---|
| 0x00 | 16 | 형식 GUID (partition type GUID) |
| 0x10 | 16 | 고유 GUID (unique partition GUID) |
| 0x20 | 8 | 시작 LBA |
| 0x28 | 8 | 끝 LBA (이 LBA 까지 포함) |
| 0x30 | 8 | 속성 |
| 0x38 | 72 | 이름 (UTF-16LE) |

보조 머리글 (backup header) 은 디스크 마지막 LBA 에 있습니다[6][4]. CRC32 는 초깃값 ~0 으로 계산한 뒤 끝에서 ~0 과 XOR 합니다[6].

GUID 16바이트는 앞 세 필드(4·2·2바이트)만 리틀엔디언이고 나머지 8바이트는 적힌 순서 그대로입니다[6]. 그래서 `lsblk`·`blkid` 가 보여 주는 문자열과 디스크 바이트의 순서가 앞부분에서 다릅니다.

리눅스와 관련된 형식 GUID 는 아래와 같습니다[7][8]. 표의 루트·/usr 는 x86-64 용 값이고, 다른 CPU 는 GUID 가 따로 있습니다[8].

| 형식 GUID | 이름 |
|---|---|
| 0FC63DAF-8483-4772-8E79-3D69D8477DE4 | Linux filesystem |
| 0657FD6D-A4AB-43C4-84E5-0933C84B4F4F | Linux swap |
| E6D6D379-F507-44C2-A23C-238F2A3DF928 | Linux LVM |
| A19D880F-05FC-4D3B-A006-743F0F84911E | Linux RAID |
| CA7D7CCB-63ED-4C53-861C-1742536059CC | Linux LUKS |
| 7FFEC5C9-2D00-49B7-8941-3EA10A5586B7 | Linux plain dm-crypt |
| 4F68BCE3-E8CD-4DB1-96E7-FBCAF984B709 | Linux root (x86-64) |
| 8484680C-9521-48C6-9C11-B0720656F69E | Linux /usr (x86-64) |
| 933AC7E1-2EB4-4F13-B844-0E14E2AEF915 | Linux home |
| 3B8F8425-20E0-4F3B-907F-1A25A76F98E8 | Linux server data (/srv) |
| 4D21B016-B534-45C2-A9FB-5C16E091FD2D | Linux variable data (/var) |
| 7EC6F557-3BC5-4ACA-B293-16EF5DF639D1 | Linux temporary data (/var/tmp) |
| C12A7328-F81F-11D2-BA4B-00A0C93EC93B | EFI System |
| BC13C2FF-59E6-4262-A352-B275FD6F7172 | Linux extended boot (XBOOTLDR) |
| 21686148-6449-6E6F-744E-656564454649 | BIOS boot |
| EBD0A0A2-B9E5-4433-87C0-68B6B72699C7 | Microsoft basic data |

속성 8바이트 가운데 비트 63(no-auto), 60(read-only), 59(grow-file-system) 은 자동 발견 규칙에서 쓰는 표시입니다[8]. 비트 63 이 켜진 파티션은 자동으로 마운트하거나 스왑으로 켜지 않고, 비트 60 이 켜진 파티션은 읽기 전용으로 마운트합니다[8].

## 읽는 법

### 헥스로 한 번

아래는 명세로 만든 예시이고, 값은 모두 지어낸 것입니다. 512바이트 섹터 디스크에서 LBA 1 은 바이트 오프셋 0x200 입니다. CRC 와 판 번호 칸은 `..` 로 가렸습니다.

```
오프셋     00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000200  45 46 49 20 50 41 52 54  .. .. .. ..  5C 00 00 00   EFI PART ....\...
00000210  .. .. .. ..  00 00 00 00  01 00 00 00 00 00 00 00
00000220  FF FF 1F 00 00 00 00 00  22 00 00 00 00 00 00 00
00000230  DE FF 1F 00 00 00 00 00  (disk_guid 16바이트)
00000240  (disk_guid 이어짐)       02 00 00 00 00 00 00 00
00000250  80 00 00 00 80 00 00 00  .. .. .. ..
```

읽는 순서는 이렇습니다. 0x20C 의 `5C 00 00 00` 은 머리글 크기 92 입니다. 0x218 의 my_lba 는 1, 0x220 의 alternate_lba 는 0x1FFFFF 라서 보조 머리글이 LBA 2,097,151 에 있고, 디스크가 2,097,152 섹터(1GiB)라는 뜻입니다. 0x228·0x230 은 파티션에 쓸 수 있는 범위(LBA 34~2,097,118)이고, 0x248 의 2 는 항목 배열이 LBA 2(바이트 0x400)에서 시작한다는 뜻입니다. 0x250 은 항목 128개, 항목 크기 128바이트입니다.

항목 배열의 첫 항목(0x400)이 아래처럼 시작하면, 앞 16바이트는 형식 GUID 0FC63DAF-8483-4772-8E79-3D69D8477DE4(Linux filesystem) 입니다. 앞 세 필드의 바이트 순서가 뒤집혀 있는 점을 보면 됩니다. 이것도 명세로 만든 예시입니다.

```
00000400  AF 3D C6 0F 83 84 72 47  8E 79 3D 69 D8 47 7D E4
```

0x420 의 시작 LBA 와 0x428 의 끝 LBA 로 범위를 구하고, 시작 LBA 에 섹터 크기를 곱한 위치에서 파일 시스템 서명을 확인합니다. 0x438 부터 72바이트는 UTF-16LE 이름이라 영문 이름이면 한 글자 뒤에 `00` 이 하나씩 붙습니다.

MBR 디스크라면 0x1BE 부터 16바이트씩 네 번 끊어 읽고, 각 항목의 0x04 에서 형식 번호를, 0x08·0x0C 에서 시작 LBA 와 섹터 수를 읽습니다[1].

### 공개 도구로 한 번

오프라인 이미지에서는 TSK 의 `mmls` 로 파티션 배치를 봅니다. TSK 는 GPT 에서 보호용 MBR 을 "Safety Table", 머리글을 "GPT Header", 항목 배열을 "Partition Table" 이라는 메타 항목으로 목록에 함께 넣습니다[4]. dissect.volume 은 GPT·MBR·LVM2 를 파이썬에서 읽습니다[14].

라이브 시스템에서는 `blkid`, `lsblk`, `fdisk -l` 결과와 `/dev/disk/by-*` 링크 목록을 함께 남깁니다[16]. udev 는 `by-partuuid` 링크를 파티션 고유 ID 로 만들고, `by-partlabel` 링크는 GPT 이면서 파티션 이름이 있을 때만 만듭니다[10]. `by-uuid`·`by-label` 은 파티션이 아니라 그 안의 파일 시스템(또는 LUKS 같은 암호 볼륨)의 UUID·이름입니다[10]. MBR 디스크에서는 libblkid 가 디스크 식별자 4바이트를 8자리 16진수 문자열로 표의 ID 로 씁니다[5]. MBR 파티션의 PARTUUID 문자열 모양은 검체의 `blkid` 출력과 `/dev/disk/by-partuuid` 링크 이름으로 확인합니다.

## 포렌식에서 중요한 점

### 증명하는 것

- 디스크에 어떤 파티션이 어느 LBA 범위로 정의돼 있는지
- 각 파티션에 어떤 용도 표시(형식 번호·형식 GUID)를 달았는지
- 디스크 GUID·파티션 고유 GUID·MBR 디스크 식별자. 이 값은 fstab 의 `PARTUUID=`, `/dev/disk/by-partuuid`, 저널에 남은 장치 이름과 맞춰 볼 수 있습니다[11][10].

### 증명하지 못하는 것

- 파티션을 언제 만들었는지, 누가 만들었는지. MBR 항목과 GPT 머리글·항목 어디에도 시각 칸이 없습니다[1][3][6].
- 형식 표시가 실제 내용과 맞는지. 형식 GUID 는 쓰는 사람이 정한 표시일 뿐이라, 안의 내용은 시작 LBA 위치의 파일 시스템·LVM·LUKS 서명으로 따로 확인합니다.
- 표에 없는 영역에 무엇이 있었는지. 항목 사이 빈 공간이나 last_usable_lba 뒤는 표가 말해 주지 않으므로 직접 서명을 찾아봅니다.

### 시각

파티션 표에는 시각이 없습니다. 파티션을 만든 시점은 안쪽 파일 시스템 슈퍼블록의 생성 시각([ext4](../filesystem/ext4/index.md) 등), LVM 메타데이터의 `creation_time`([LVM 논리 볼륨](lvm.md)), 설치 기록 같은 다른 흔적으로 좁힙니다.

### 자동 발견과 fstab

GPT 디스크에서는 fstab 에 없는 파티션도 부팅 때 마운트되거나 스왑으로 켜질 수 있습니다. systemd-gpt-auto-generator 는 형식 GUID 를 보고 루트·/home·/srv·/var·/var/tmp·ESP·XBOOTLDR·스왑 파티션을 찾아 마운트·스왑 유닛을 만듭니다[9]. 이 생성기는 GPT 가 아닌 디스크에서는 아무 일도 하지 않고, fstab 에 이미 적힌 마운트 지점이나 파일이 들어 있는 디렉터리에는 유닛을 만들지 않습니다[9]. 이런 형식 GUID 를 쓴 파티션이 디스크에서 그 형식의 첫 파티션이면 설치기는 fstab 항목을 만들지 않아도 됩니다[8].

/var 파티션은 조건이 하나 더 붙습니다. 파티션 고유 GUID 가 `/etc/machine-id` 를 키로 한 형식 UUID 의 HMAC-SHA256 앞 128비트와 같아야 자동으로 마운트합니다[8][9]. 이 조건 때문에 /var 파티션의 고유 GUID 는 그 설치본과 묶입니다.

LUKS 로 감싼 자동 발견 파티션은 `/dev/mapper/root`, `/dev/mapper/home`, `/dev/mapper/srv`, `/dev/mapper/var`, `/dev/mapper/tmp`, `/dev/mapper/swap` 같은 이름으로 열립니다[8]. /var/tmp 용 파티션의 장치 이름이 `tmp` 인 점에 주의합니다.

"Linux filesystem" 형식 GUID 는 자동으로 마운트하지 않고 fstab 에 적어야 합니다[8]. 따라서 형식이 Linux filesystem 인 파티션이 fstab 에도 없다면 평소에는 쓰지 않던 파티션일 가능성이 있습니다.

### 배포판 차이

설치기 코드(현재 개발 중인 가지) 기준으로 기본 배치는 다음과 같습니다. 실린 판과 세부가 다를 수 있으므로 검체에서는 `/etc/fstab` 과 `lsblk` 결과로 확인합니다.

| 항목 | Ubuntu 24.04 (subiquity) | RHEL 9 (anaconda) |
|---|---|---|
| 기본 파일 시스템 | ext4 (안내 설치 LVM 에서 `/` 와 `/boot`) [20] | xfs [18] |
| 기본 배치 | `/boot` 파티션(ext4) 뒤에 나머지를 LVM 물리 볼륨으로, VG `ubuntu-vg` 안에 LV `ubuntu-lv`(`/`) [20] | `/`(최소 1GiB, 최대 70GiB), `/home`, `swap` [18] |
| EFI 시스템 파티션 | 검체의 fstab 으로 확인 | `/boot/efi` 에 마운트 [19], EFI 디렉터리 이름 `redhat` [18] |
| BIOS 부팅 | 검체로 확인 | `biosboot` 파티션 [19] |
| 암호화 선택 시 | 안내 설치에 LVM_LUKS 선택지 [20] | 파티션을 LUKS 로 만들고 그 위에 LVM 물리 볼륨 [19] |

LVM 이름 규칙과 VG 이름 확인 방법은 [LVM 논리 볼륨](lvm.md) 쪽에 있습니다.

### 지우기·조작에 남는 것

파티션 표를 지우거나 고쳐도 파티션 안의 데이터는 그대로인 경우가 많아서, 표 밖에서 파일 시스템·LVM·LUKS 서명을 찾으면 옛 파티션 범위를 되짚을 수 있습니다. GPT 는 주 머리글·항목 배열과 보조 머리글·항목 배열이 따로 있으므로, 한쪽만 고쳤다면 두 표가 서로 다릅니다[6][4]. 두 표를 모두 읽어 비교하고, CRC 가 맞는지도 계산해 봅니다.

## 함정

**도구마다 손상된 GPT 를 받아들이는 기준이 다릅니다.** libblkid 는 머리글 CRC, 항목 배열 CRC, my_lba 가 실제 위치와 같은지, 사용 가능 범위가 말이 되는지를 모두 검사하고, 하나라도 틀리면 마지막 LBA 의 보조 머리글을 봅니다[6]. TSK 의 GPT 코드는 CRC 를 검사하지 않고, 주 머리글을 읽지 못하면 섹터 크기를 512·1024·2048·4096·8192 로 바꿔 가며 다시 읽은 뒤, 그래도 안 되면 디스크 끝의 보조 머리글을 읽습니다[4]. 그래서 같은 이미지를 두고 `mmls` 와 `blkid` 의 결과가 다를 수 있습니다.

**빈 항목을 가리는 기준도 다릅니다.** libblkid 는 형식 GUID 가 모두 0 인 항목을 건너뛰고, 사용 가능 범위를 벗어난 항목도 버립니다[6]. TSK 는 시작 LBA 가 0 인 항목만 건너뜁니다[4]. 형식 GUID 만 0 으로 지우고 LBA 는 남긴 항목은 TSK 목록에는 나오고 `blkid` 에는 나오지 않습니다.

**보호용 MBR 이 없으면 GPT 로 보지 않을 수 있습니다.** libblkid 는 기본 설정에서 LBA 0 에 0xEE 항목이 있어야 GPT 로 인식하고[6], TSK 도 주 GPT 를 읽을 때 LBA 0 의 매직과 첫 항목 0xEE 를 요구합니다[4]. 반대로 MBR 쪽 코드는 0xEE 항목을 보면 MBR 로 읽지 않습니다[5]. Apple 은 MBR 과 GPT 를 함께 맞춰 둔 하이브리드 디스크를 씁니다[6].

**FAT·NTFS 부트 섹터도 `55 AA` 로 끝납니다.** TSK 는 OEM 이름("MSDOS", "MSWIN", "NTFS", "FAT")을 보고, libblkid 는 FAT·exFAT·NTFS 인지 따로 검사해 파티션 표가 아닌 것을 걸러 냅니다[2][5]. 파티션 없이 파일 시스템을 통째로 만든 USB 저장 장치에서 이 구분이 중요합니다. libblkid 는 부트 표시가 0x00·0x80 이 아닌 항목이 하나라도 있으면 MBR 로 보지 않습니다[5].

**섹터 크기가 4096 인 디스크(4Kn)** 에서는 LBA 1 이 바이트 4096 이라 GPT 머리글이 0x1000 에 있습니다. libblkid 는 논리 섹터 크기에 LBA 를 곱해 위치를 구합니다[6]. 이미지 파일만 받았다면 0x200 과 0x1000 두 곳에서 `EFI PART` 를 찾아봅니다.

**파티션 표 없이 디스크 전체를 LVM 물리 볼륨으로 쓴 경우**가 있습니다. `pvcreate` 는 장치 앞부분을 지우고, libblkid 는 이 범위를 앞 8KiB 로 잡습니다[12]. 또 LVM 물리 볼륨이 있고 MBR 표가 비어 있으면 libblkid 는 MBR 을 무시합니다[5]. 파티션 표가 없다고 빈 디스크로 판단하지 말고 [LVM 논리 볼륨](lvm.md) 쪽의 서명을 찾아봅니다.

**fstab 파서마다 읽는 줄이 다릅니다.** fstab(5) 는 5·6번 필드를 생략하면 0 으로 보고, `LABEL=`·`UUID=`·`PARTUUID=`·`PARTLABEL=` 을 장치 칸에 쓸 수 있게 합니다[11]. dissect.target 의 fstab 파서는 필드가 정확히 6개인 줄만 읽고, `PARTUUID=`·`PARTLABEL=` 로 적은 장치는 지원하지 않는 장치로 건너뛰며, swap·tmpfs 같은 형식도 건너뜁니다[13]. 도구가 만든 마운트 목록에 빠진 항목이 있으면 fstab 원본을 직접 읽습니다. 자동 발견으로 붙은 파티션은 fstab 에 아예 없을 수 있습니다[8].

## 도구

| 도구 | 쓰임 |
|---|---|
| TSK `mmls` | 이미지의 파티션 배치, GPT 메타 항목 표시[4] |
| dissect.volume | GPT·MBR·LVM2 파서[14] |
| `blkid`, `lsblk`, `fdisk -l`, `ls -l /dev/disk/by-*` | 라이브 수집(UAC 가 모으는 명령)[16] |
| `/proc/partitions` | 커널이 아는 파티션 목록[17] |
| ForensicArtifacts `LinuxFstab`, `LinuxProcMounts`, `LinuxMountInfo` | `/etc/fstab` 과 `/proc/mounts` 수집 정의[15][21] |

## 참고 문헌

1. The Sleuth Kit, `tsk/vs/tsk_dos.h`. https://github.com/sleuthkit/sleuthkit/blob/develop-4.1x/tsk/vs/tsk_dos.h
2. The Sleuth Kit, `tsk/vs/dos.c`. https://github.com/sleuthkit/sleuthkit/blob/develop-4.1x/tsk/vs/dos.c
3. The Sleuth Kit, `tsk/vs/tsk_gpt.h`. https://github.com/sleuthkit/sleuthkit/blob/develop-4.1x/tsk/vs/tsk_gpt.h
4. The Sleuth Kit, `tsk/vs/gpt.c`. https://github.com/sleuthkit/sleuthkit/blob/develop-4.1x/tsk/vs/gpt.c
5. util-linux, `libblkid/src/partitions/dos.c`. https://github.com/util-linux/util-linux/blob/master/libblkid/src/partitions/dos.c
6. util-linux, `libblkid/src/partitions/gpt.c`. https://github.com/util-linux/util-linux/blob/master/libblkid/src/partitions/gpt.c
7. util-linux, `include/pt-gpt-partnames.h`. https://github.com/util-linux/util-linux/blob/master/include/pt-gpt-partnames.h
8. UAPI Group, Discoverable Partitions Specification. https://github.com/uapi-group/specifications/blob/main/specs/discoverable_partitions_specification.md
9. systemd, `man/systemd-gpt-auto-generator.xml`. https://github.com/systemd/systemd/blob/main/man/systemd-gpt-auto-generator.xml
10. systemd, `rules.d/60-persistent-storage.rules.in`. https://github.com/systemd/systemd/blob/main/rules.d/60-persistent-storage.rules.in
11. util-linux, `sys-utils/fstab.5.adoc`. https://github.com/util-linux/util-linux/blob/master/sys-utils/fstab.5.adoc
12. util-linux, `libblkid/src/superblocks/lvm.c`. https://github.com/util-linux/util-linux/blob/master/libblkid/src/superblocks/lvm.c
13. dissect.target, `dissect/target/plugins/os/unix/_os.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/_os.py
14. dissect.volume, `README.md`. https://github.com/fox-it/dissect.volume/blob/main/README.md
15. ForensicArtifacts, `artifacts/data/linux.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
16. UAC, `artifacts/live_response/storage/` (blkid.yaml, fdisk.yaml, lsblk.yaml, ls_dev_disk.yaml). https://github.com/tclahr/uac/blob/main/artifacts/live_response/storage/
17. Linux kernel, `Documentation/filesystems/proc.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.rst
18. anaconda, `data/profile.d/rhel.conf`. https://github.com/rhinstaller/anaconda/blob/main/data/profile.d/rhel.conf
19. anaconda, `pyanaconda/modules/storage/partitioning/automatic/utils.py`. https://github.com/rhinstaller/anaconda/blob/main/pyanaconda/modules/storage/partitioning/automatic/utils.py
20. subiquity, `subiquity/server/controllers/storage.py`. https://github.com/canonical/subiquity/blob/main/subiquity/server/controllers/storage.py
21. ForensicArtifacts, `artifacts/data/linux_proc.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux_proc.yaml
