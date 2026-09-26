---
title: "Btrfs"
parent: "기반 · 파일 시스템"
nav_order: 80
---

# Btrfs (Btrfs)

Btrfs 는 슈퍼블록을 뺀 모든 구조를 쓸 때 복사하는 트리 (copy-on-write B-tree) 로 저장하는 파일 시스템이라서, 고친 메타데이터의 옛 판이 새 자리에 쓰인 판과 함께 디스크에 남습니다[1][13].

## 이 형식을 쓰는 아티팩트

Btrfs 는 기준 배포판 두 곳에서는 기본값이 아니고 Fedora 에서 기본값입니다. Ubuntu 24.04 설치 프로그램의 안내 설치는 `/` 를 ext4 로 만들고[6], RHEL 9 설치 프로그램은 기본 파일 시스템이 XFS 이며 `btrfs-progs` 를 설치하지 않을 꾸러미 목록 (`ignored_packages`) 에 넣습니다[4]. Fedora 설치 프로그램은 기본 구성이 `default_scheme = BTRFS` 이고 압축 설정이 `btrfs_compression = zstd:1` 입니다[5].

| 항목 | Ubuntu 24.04 LTS | RHEL 9 | Fedora |
|---|---|---|---|
| 설치 기본 파일 시스템 | ext4[6] | XFS (`file_system_type = xfs`)[4] | Btrfs (`default_scheme = BTRFS`)[5] |
| 설치 프로그램의 Btrfs 관련 설정 | 안내 설치 선택지는 ext4·ZFS[6] | `btrfs-progs` 를 `ignored_packages` 에 넣음[4] | `btrfs_compression = zstd:1`[5] |

그래서 Btrfs 는 주로 Fedora 계열 시스템, 사용자가 직접 만든 데이터 볼륨, 여러 디스크를 묶은 저장 장치에서 만납니다. 어느 볼륨이 Btrfs 인지는 실제 시스템의 `/etc/fstab` 과 파티션 시작에서 `0x10040` 의 마법 수로 확인합니다. 파일 시스템 안의 모든 파일 흔적(이름, 아이노드, 시각, 데이터 위치)이 이 구조에 담기므로, [타임라인](../../03-techniques/analysis/timeline.md) 과 [지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md) 가 모두 여기서 출발합니다. 볼륨 아래에 LVM 이나 LUKS 가 있으면 [LVM 논리 볼륨](../disk-volume/lvm.md), [LUKS 디스크 암호화](../disk-volume/luks.md) 에서 먼저 풉니다.

주요 기능은 쓰기 가능한 스냅숏 (snapshot), 서브볼륨 (subvolume, 파일 시스템 안의 별도 루트), 데이터·메타데이터 체크섬, 압축, reflink·중복 제거, 여러 장치를 묶는 RAID, 증분 백업용 send/receive 입니다[3].

## 구조

모든 필드는 리틀 엔디언이고, 오프셋은 16 진수입니다[1]. btrfs-progs 의 형식 문서는 옛 위키에서 거의 검토 없이 옮긴 문서라서[1], 구조체 오프셋은 커널 헤더 `btrfs_tree.h` 의 필드 순서를 기준으로 삼고 둘이 다르면 헤더를 따릅니다[2].

### 주소 두 가지

파일 시스템 구조 안의 주소는 논리 주소이고, 디스크의 바이트 위치는 물리 주소입니다. 논리 주소 하나가 RAID 설정에 따라 여러 디스크의 물리 주소에 대응하고, 청크 트리 (chunk tree) 가 논리 주소를 물리 주소로, 장치 트리 (dev tree) 가 그 반대로 바꿉니다[1]. 슈퍼블록에는 시스템 청크의 청크 항목이 들어 있어서 이것으로 청크 트리를 찾고, 청크 트리로 나머지 트리를 찾습니다[1].

### 슈퍼블록

주 슈퍼블록은 물리 주소 `0x10000`(64 KiB) 에 있고, 사본은 `0x4000000`(64 MiB) 과 `0x4000000000`(256 GiB) 에 장치가 그만큼 클 때만 있습니다. 사본은 주 슈퍼블록과 함께 갱신되지만, 커널은 마운트할 때 첫 슈퍼블록만 읽고 오류가 있으면 마운트에 실패합니다[1]. 크기는 4096 바이트입니다[2].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x0 | 0x20 | `csum` | `0x20` 부터 끝까지의 체크섬[1] |
| 0x20 | 0x10 | `fsid` | 파일 시스템 UUID[1] |
| 0x30 | 0x8 | `bytenr` | 이 블록의 물리 주소(사본마다 다름)[1] |
| 0x38 | 0x8 | `flags` | 플래그[1] |
| 0x40 | 0x8 | `magic` | `_BHRfS_M` (정수로 `0x4D5F53665248425F`)[1][2] |
| 0x48 | 0x8 | `generation` | 세대 번호[1] |
| 0x50 | 0x8 | `root` | 루트 트리 (root tree) 의 논리 주소[1] |
| 0x58 | 0x8 | `chunk_root` | 청크 트리의 논리 주소[1] |
| 0x60 | 0x8 | `log_root` | 로그 트리의 논리 주소[1] |
| 0x70 | 0x8 | `total_bytes` | 전체 크기[1] |
| 0x78 | 0x8 | `bytes_used` | 쓴 크기[1] |
| 0x80 | 0x8 | `root_dir_objectid` | 보통 6[1] |
| 0x88 | 0x8 | `num_devices` | 묶인 장치 수[1] |
| 0x90 | 0x4 | `sectorsize` | 섹터 크기[1] |
| 0x94 | 0x4 | `nodesize` | 트리 노드 크기[1] |
| 0xa0 | 0x4 | `sys_chunk_array_size` | 시스템 청크 배열에서 쓰는 바이트 수[1] |
| 0xa4 | 0x8 | `chunk_root_generation` | 청크 트리의 세대[1] |
| 0xc4 | 0x2 | `csum_type` | 체크섬 종류. 0 CRC32, 1 XXHASH, 2 SHA256, 3 BLAKE2[2] |
| 0xc9 | 0x62 | `dev_item` | 이 장치의 장치 항목[1] |
| 0x12b | 0x100 | `label` | 볼륨 이름표[1] |
| 0x32b | 0x800 | `sys_chunk_array` | 시스템 청크의 (키, 청크 항목) 쌍[1][2] |
| 0xb2b | 0x2a0 | `super_roots` | 백업 루트 4 개[1][2] |

`super_roots` 는 `btrfs_root_backup` 구조체 4 개이고, 하나(0xa8 바이트)에 루트·청크·익스텐트·파일 시스템·장치·체크섬 트리의 주소와 그 세대가 짝으로 들어 있습니다[2]. 앞선 트랜잭션들의 트리 루트를 남겨 두려는 자리라서[2], 지운 파일을 찾을 때 옛 트리로 들어가는 입구가 됩니다.

### 노드 머리와 키

트리의 모든 노드(잎과 내부 노드)는 같은 머리로 시작합니다[1][2].

| 오프셋 | 크기 | 필드 |
|---|---|---|
| 0x0 | 0x20 | 체크섬 |
| 0x20 | 0x10 | 파일 시스템 UUID |
| 0x30 | 0x8 | 이 노드의 논리 주소 |
| 0x38 | 0x8 | 플래그 |
| 0x40 | 0x10 | 청크 트리 UUID |
| 0x50 | 0x8 | 세대 (generation) |
| 0x58 | 0x8 | 이 노드를 가진 트리의 ID |
| 0x60 | 0x4 | 항목 수 |
| 0x64 | 0x1 | 높이 (0 이면 잎) |

머리는 `0x65` 바이트이고, 잎 노드는 그 뒤에 항목 머리(키 0x11 바이트 + 데이터 오프셋 4 바이트 + 데이터 크기 4 바이트)를 늘어놓고 항목 데이터는 노드 끝에서부터 채웁니다. 데이터 오프셋은 머리 끝(`0x65`)에서 센 값입니다[1].

키 (key) 는 objectid(8 바이트), 항목 종류(1 바이트), offset(8 바이트) 로 17 바이트입니다. objectid 는 트리마다 따로 매깁니다[1]. 파일 트리에서 objectid 는 아이노드 번호로 쓰이고[1], 첫 사용자 objectid 는 256 입니다[2].

| 항목 종류 | 값 | 담는 것 |
|---|---|---|
| `INODE_ITEM` | 1 | 아이노드의 stat 정보[1][2] |
| `INODE_REF` | 12 | 아이노드에서 부모 디렉터리와 이름으로[1][2] |
| `XATTR_ITEM` | 24 | 확장 속성[1][2] |
| `ORPHAN_ITEM` | 48 | 고아 항목[1][2] |
| `DIR_ITEM` | 84 | 이름 해시로 찾는 디렉터리 항목[1][2] |
| `DIR_INDEX` | 96 | 순서 번호로 찾는 디렉터리 항목(항목 하나)[1][2] |
| `EXTENT_DATA` | 108 | 파일 내용의 위치 또는 인라인 데이터[1][2] |
| `ROOT_ITEM` | 132 | 트리 하나의 루트 위치와 속성(루트 트리에만)[1][2] |
| `ROOT_BACKREF` / `ROOT_REF` | 144 / 156 | 서브볼륨의 부모·자식 연결[2] |

루트 트리 안에서 objectid 5 는 기본 파일 시스템 트리 (FS_TREE) 이고, 256 이상은 서브볼륨·스냅숏의 파일 트리입니다[1]. objectid 6 은 루트 트리 안의 디렉터리이고, 그 안의 `default` 항목 하나가 루트 디렉터리로 쓸 트리를 가리킵니다[1].

### 아이노드 항목

`btrfs_inode_item` 은 160 바이트이고, 아래 오프셋은 헤더의 필드 순서에서 나오며[2] The Sleuth Kit 도 같은 오프셋으로 읽습니다[7].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x0 | 0x8 | `generation` | NFS 용 세대 번호 |
| 0x8 | 0x8 | `transid` | 이 아이노드를 마지막으로 건드린 트랜잭션 |
| 0x10 | 0x8 | `size` | 파일 크기 |
| 0x18 | 0x8 | `nbytes` | 차지한 바이트 |
| 0x28 | 0x4 | `nlink` | 링크 수 |
| 0x2c | 0x4 | `uid` | 소유자 UID |
| 0x30 | 0x4 | `gid` | 소유 그룹 GID |
| 0x34 | 0x4 | `mode` | 종류와 권한 |
| 0x40 | 0x8 | `flags` | 아이노드 플래그 |
| 0x70 | 0xc | `atime` | 접근 시각 |
| 0x7c | 0xc | `ctime` | 아이노드 변경 시각 |
| 0x88 | 0xc | `mtime` | 내용 변경 시각 |
| 0x94 | 0xc | `otime` | 생성 시각 |

시각 하나는 1970-01-01 UTC 부터 센 부호 있는 64 비트 초와, 그 초 안의 32 비트 나노초로 12 바이트입니다[1][2]. 네 시각이 바뀌는 조건과 `stat` 결과로 보는 법은 [ext4 의 시각 값](ext4/timestamps.md) 과 [Linux 의 시각 값](../value-decoding/time-values.md) 에서 다룹니다.

### 파일 내용 항목

`EXTENT_DATA` 의 키 offset 은 파일 안의 위치입니다. 항목 앞부분은 모든 경우에 같습니다[1][2].

| 오프셋 | 크기 | 필드 |
|---|---|---|
| 0x0 | 0x8 | 이 익스텐트를 만든 트랜잭션 |
| 0x8 | 0x8 | 풀어 낸 크기 |
| 0x10 | 0x1 | 압축 방식(0 없음, 1 zlib, 2 LZO 로 문서화)[1] |
| 0x11 | 0x1 | 암호화(0 없음) |
| 0x12 | 0x2 | 그 밖의 인코딩(0 없음) |
| 0x14 | 0x1 | 종류(0 인라인, 1 일반, 2 미리 할당) |

인라인이면 나머지 바이트가 곧 파일 데이터입니다. 인라인이 아니면 `0x15` 에 익스텐트의 논리 주소, `0x1d` 에 익스텐트 크기, `0x25` 에 익스텐트 안의 오프셋, `0x2d` 에 파일에서 쓰는 바이트 수가 이어지고, 논리 주소가 0 이면 전부 0 인 빈 구간입니다[1].

### 서브볼륨·스냅숏 항목

`btrfs_root_item` 은 아이노드 항목 하나로 시작하고, 그 뒤에 트리 루트의 주소(`bytenr`)·마지막 스냅숏 세대(`last_snapshot`)·참조 수 같은 값이 옵니다[2][7]. 그 뒤의 필드는 서브볼륨 UUID 와 시각이 들어온 뒤에 더한 부분입니다[2].

| 필드 | 뜻 |
|---|---|
| `uuid` | 이 서브볼륨의 UUID |
| `parent_uuid` | 스냅숏이면 원본 서브볼륨의 UUID |
| `received_uuid` | send/receive 로 받은 서브볼륨이면 보낸 쪽 UUID |
| `ctransid` / `ctime` | 서브볼륨 안의 아이노드가 바뀐 트랜잭션과 시각 |
| `otransid` / `otime` | 서브볼륨을 만든 트랜잭션과 시각 |
| `stransid` / `stime` | 보낸 트랜잭션과 시각(받은 서브볼륨에서 0 이 아님) |
| `rtransid` / `rtime` | 받은 트랜잭션과 시각(받은 서브볼륨에서 0 이 아님) |

더한 필드가 맞는지는 `generation_v2` 로 판단합니다. 커널은 루트 항목을 쓸 때마다 `generation` 을 `generation_v2` 에 복사하고, 옛 커널로 마운트한 적이 있어 두 값이 다르면 더한 필드를 무효로 봅니다[2].

## 읽는 법

파일 하나까지 내려가는 순서는 아래와 같습니다[1][13].

1. `0x10000` 에서 슈퍼블록을 읽고 `0x40` 의 마법 수를 확인합니다.
2. `sys_chunk_array` 의 청크 항목으로 청크 트리의 논리 주소(`0x58`)를 물리 주소로 바꿔 청크 트리 전체를 읽습니다.
3. 청크 트리로 루트 트리의 논리 주소(`0x50`)를 풀어 루트 트리를 읽습니다.
4. 루트 트리의 `ROOT_ITEM` 에서 FS_TREE(5) 나 서브볼륨(256 이상)의 트리 루트를 찾습니다.
5. 그 파일 트리에서 `DIR_ITEM`/`DIR_INDEX` 로 이름에서 아이노드 번호를, `INODE_ITEM` 으로 속성과 시각을, `EXTENT_DATA` 로 데이터 위치를 읽습니다.
6. 데이터의 논리 주소를 다시 청크 트리로 물리 주소로 바꿔 읽습니다.

아래는 명세로 만든 예시입니다. 파티션 시작에서 `0x10040` 을 읽으면 마법 수가, 아이노드 항목 데이터의 `0x94` 를 읽으면 생성 시각이 나옵니다.

```text
만든 예시 (명세로 만든 바이트)
0x10040: 5F 42 48 52 66 53 5F 4D                      "_BHRfS_M"
아이노드 항목 +0x94: 80 B4 A0 66 00 00 00 00  00 65 CD 1D
  초   = 0x0000000066A0B480 = 1721808000 → 2024-07-24 08:00:00 UTC
  나노초 = 0x1DCD6500 = 500000000         → 2024-07-24 08:00:00.5 UTC
```

한 파일 시스템 안에서 서브볼륨마다 아이노드 번호를 따로 매기므로[1], 아이노드 번호 257 은 서브볼륨마다 다른 파일일 수 있습니다. 그래서 파일을 가리킬 때는 (서브볼륨 ID, 아이노드 번호) 를 함께 적습니다. 실제 시스템에서 어떤 서브볼륨이 어디에 마운트됐는지는 `/etc/fstab` 의 `subvol=`·`subvolid=` 옵션으로 확인하고, dissect.target 도 이 옵션을 서브볼륨 경로·objectid 와 맞춰 마운트 위치를 정합니다[9]. 마운트 기록은 [마운트 기록](../../02-artifacts/devices/mounts.md) 에서 다룹니다.

## 포렌식에서 중요한 점

**옛 세대가 남습니다.** 쓸 때 복사하는 구조라서 옛 메타데이터와 데이터가 최신 파일 시스템에 속하지 않은 채 디스크에 남고, Btrfs 는 이를 세대로 구분합니다[13]. 반면 ext4 의 아이노드 테이블 같은 고정된 자리가 없어서, 미할당 영역에서 정해진 위치의 메타데이터 구조를 차례로 읽는 방식은 통하지 않습니다[13]. 옛 트리로 들어가는 입구는 슈퍼블록의 백업 루트 4 개이고, btrfs-progs 의 `btrfs-find-root` 로 루트 트리 주소를 더 찾을 수 있습니다[13]. 옛 세대의 루트 트리로 파일 목록을 다시 만들면 최신 세대에서 사라진 파일 이름과 아이노드가 나올 수 있습니다[13].

**스냅숏을 먼저 봅니다.** 스냅숏에는 그 시점의 메타데이터와 데이터가 어긋남 없이 들어 있어서, 옛 세대를 뒤지는 복구보다 스냅숏을 먼저 확인합니다[13]. 스냅숏의 `parent_uuid` 는 어느 서브볼륨을 찍었는지, `otime` 은 언제 찍었는지를 알려 줍니다[2]. 라이브 시스템에서는 UAC 가 `mount -t btrfs` 로 마운트 지점을 모은 뒤 `btrfs subvolume list -a -p -c -u -q -R` 로 전체 서브볼륨을, `-s` 로 스냅숏만, `-r` 로 읽기 전용만, `-d` 로 지운 서브볼륨을, `btrfs subvolume show` 로 각 서브볼륨 정보를 남깁니다[10]. 절차는 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md) 에서 다룹니다.

**지운 서브볼륨은 한 번에 사라지지 않습니다.** 루트를 지우면 디렉터리 연결을 끊고 `ROOT_ITEM` 의 참조 수를 0 으로 둔 뒤 루트 트리에 고아 키 (objectid `-5`) 를 넣고, 정리 스레드가 여러 트랜잭션에 걸쳐 익스텐트를 풉니다[1]. 정리가 끝나기 전에 수집하면 지운 서브볼륨의 `ROOT_ITEM` 이 남아 있을 수 있습니다.

**장치가 빠지면 데이터 일부를 잃습니다.** 여러 장치를 묶으면 논리 주소 공간을 청크로 나누고, 청크마다 여러 장치의 스트라이프 (stripe) 에 RAID0·RAID1·RAID10 으로 나눠 씁니다[13]. RAID0 청크는 장치 하나가 빠지면 그 데이터를 잃습니다[13]. 메타데이터가 raid1, 데이터가 raid0 인 3 장치 구성에서 장치 하나가 없으면 `degraded` 로 마운트해 메타데이터(파일 목록)는 읽기 전용으로 보이지만 파일을 열면 입출력 오류가 납니다[13]. 그래서 이미징할 때는 `num_devices` 와 장치 항목을 보고 풀 (pool) 에 속한 장치를 모두 뜹니다([디스크 이미징](../../03-techniques/acquisition/disk-imaging.md)).

**비정상 종료 뒤에는 슈퍼블록 사이의 세대를 비교합니다.** 커널은 첫 슈퍼블록만 보지만[1], The Sleuth Kit 은 유효한 슈퍼블록 사본 가운데 세대가 가장 높은 것을 고릅니다[7]. 주 슈퍼블록과 사본의 `generation` 이 다르면 도구마다 다른 세대를 보여 줄 수 있습니다.

**증명하는 것**은 아이노드의 생성 시각(`otime`), 서브볼륨·스냅숏을 만든 시각과 원본 서브볼륨의 관계, 옛 세대 트리에 남은 과거 파일 이름과 속성입니다. **증명하지 못하는 것**은 옛 세대가 얼마 동안 남는가입니다. 풀린 공간은 다시 쓰이므로 옛 세대가 없다는 사실로 그 파일이 없었다고 말할 수 없고, 장치가 빠진 풀에서는 메타데이터가 보여도 내용을 되살리지 못할 수 있습니다[13]. 시각은 모두 UTC 기준 epoch 값이라서, 현지 시각으로 옮길 때는 실제 시스템의 시간대 설정을 따로 확인합니다.

## 함정

- 형식 문서의 슈퍼블록 표는 `sys_chunk_array` 오프셋을 `0x2b` 로 적었지만, 바로 앞 `reserved` 필드가 `0x23b` 에서 `0xf0` 바이트이므로 `0x32b` 가 맞고, 커널 헤더의 필드 순서로 세어도 `0x32b` 입니다[1][2].
- 형식 문서는 체크섬을 CRC32c 하나로 설명하지만, 헤더에는 XXHASH·SHA256·BLAKE2 도 있습니다[1][2]. 체크섬을 직접 검증할 때는 `csum_type` 을 먼저 봅니다.
- 형식 문서의 압축 값 표는 zlib·LZO 까지만 적었습니다[1]. Fedora 는 기본으로 zstd 압축을 켜므로[5], 표에 없는 압축 값이 나와도 손상으로 단정하지 않습니다.
- 파일 속성 `C`(쓸 때 복사하지 않음, NOCOW) 는 쓸 때 복사하는 파일 시스템에서만 의미가 있고[12], 이 속성이 붙은 파일은 제자리에 덮어써서 옛 판이 남지 않을 가능성이 있습니다. 속성 `c` 는 압축 저장입니다[12]. 속성과 확장 속성은 [권한·확장 속성·ACL·Capabilities](permissions-xattr.md) 에서 다룹니다.
- 확장 속성 하나의 이름·값·부가 바이트 합은 `nodesize`(기본 16 kB) 를 넘지 못합니다[11].
- The Sleuth Kit 은 (서브볼륨, 아이노드) 쌍에 자체 가상 아이노드 번호를 매기므로[7], TSK 출력의 번호는 디스크의 objectid 와 다릅니다. 보고서에는 실제 서브볼륨 ID 와 objectid 를 함께 적습니다.

## 도구

| 도구 | 쓰임 |
|---|---|
| The Sleuth Kit (`fls`, `istat`, `icat`) | develop 가지의 `btrfs.cpp` 가 Btrfs 를 읽습니다. 압축 익스텐트는 zlib 로 빌드했을 때 zlib 만 풀고, 그 밖의 압축·암호화·인코딩 익스텐트는 내용을 읽으려 하면 "unsupported compression/encryption/encoding mode" 오류를 냅니다[7]. zstd 로 압축된 파일(Fedora 기본)은 내용이 읽히지 않을 가능성이 있습니다 |
| fkie-cad 판 The Sleuth Kit | 여러 장치 풀을 다룹니다. `pls` 로 풀 구성과 백업 루트를 보고, `-P` 로 풀을 열며, `-T 세대` 로 옛 세대, `-S 스냅숏` 으로 스냅숏을 엽니다[13] |
| dissect.btrfs | Python 으로 Btrfs 를 읽고 LZO 압축을 풉니다[8]. dissect.target 은 이것으로 서브볼륨을 `/etc/fstab` 과 맞춰 붙입니다[9] |
| btrfs-progs (`btrfs subvolume list`, `btrfs subvolume show`, `btrfs-find-root`) | 라이브 시스템의 서브볼륨·스냅숏 목록[10], 옛 루트 트리 주소 찾기[13] |

같은 파일 시스템 분류의 다른 형식은 [ext4](ext4/index.md), [XFS](xfs.md) 에서 다룹니다.

## 참고 문헌

1. btrfs-progs, `Documentation/dev/On-disk-format.rst`. https://github.com/kdave/btrfs-progs/blob/master/Documentation/dev/On-disk-format.rst
2. Linux kernel, `include/uapi/linux/btrfs_tree.h`. https://github.com/torvalds/linux/blob/master/include/uapi/linux/btrfs_tree.h
3. Linux kernel, `Documentation/filesystems/btrfs.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/btrfs.rst
4. Anaconda (rhel-9 가지), `data/product.d/rhel.conf`. https://github.com/rhinstaller/anaconda/blob/rhel-9/data/product.d/rhel.conf
5. Anaconda, `data/profile.d/fedora.conf`. https://github.com/rhinstaller/anaconda/blob/main/data/profile.d/fedora.conf
6. Subiquity (ubuntu/noble 가지), `subiquity/server/controllers/storage.py`. https://github.com/canonical/subiquity/blob/ubuntu/noble/subiquity/server/controllers/storage.py
7. The Sleuth Kit, `tsk/fs/btrfs.cpp`. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/btrfs.cpp
8. Fox-IT, dissect.btrfs `README.md`. https://github.com/fox-it/dissect.btrfs
9. Fox-IT, dissect.target `dissect/target/plugins/os/unix/_os.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/_os.py
10. UAC, `artifacts/live_response/storage/btrfs.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/live_response/storage/btrfs.yaml
11. Linux man-pages, `xattr(7)`. https://github.com/mkerrisk/man-pages/blob/master/man7/xattr.7
12. Linux man-pages, `ioctl_iflags(2)`. https://github.com/mkerrisk/man-pages/blob/master/man2/ioctl_iflags.2
13. Jan-Niclas Hilgert, Martin Lambertz, Shujian Yang, "Forensic Analysis of Multiple Device BTRFS Configurations using The Sleuth Kit", DFRWS 발표 슬라이드. https://dfrws.org/presentation/forensic-analysis-of-multiple-device-btrfs-configurations-using-the-sleuth-kit/
