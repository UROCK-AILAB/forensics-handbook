---
title: "슈퍼블록과 블록 그룹"
parent: "ext4"
grand_parent: "기반 · 파일 시스템"
nav_order: 10
---

# 슈퍼블록과 블록 그룹 (Superblock·Block Group)

ext4 는 장치를 같은 크기의 블록 그룹으로 나누고, 파티션 시작에서 1024바이트 떨어진 곳의 슈퍼블록에 파일 시스템 전체의 크기·기능·시각을 적어 두며, 그룹마다 그룹 서술자로 비트맵과 아이노드 테이블 위치를 알려 줍니다.

## 이 구조를 쓰는 곳

ext4 의 다른 구조는 모두 슈퍼블록과 그룹 서술자를 거쳐 찾습니다. 아이노드 번호로 아이노드를 찾으려면 그룹당 아이노드 수와 아이노드 크기, 그 그룹의 아이노드 테이블 위치가 필요하고([아이노드와 익스텐트](inode-extent.md)), 저널을 찾으려면 슈퍼블록의 저널 아이노드 번호가 필요합니다([저널](journal-jbd2.md)). 지운 파일을 따질 때 보는 블록·아이노드 비트맵과 고아 아이노드 목록도 여기서 시작합니다([지운 파일이 남기는 것](deleted-files.md)).

슈퍼블록 자체도 증거입니다. 파일 시스템을 만든 시각, 마지막으로 마운트한 시각과 경로, 커널이 기록한 오류가 들어 있어서 설치 시점과 사용 흔적을 추정하는 데 씁니다.

## 구조

### 블록 크기와 블록 그룹

블록 크기는 2^(10 + `s_log_block_size`) 바이트이고, 보통 4 KiB 입니다[1][4]. 블록 비트맵 한 비트가 블록 하나를 나타내므로 그룹 하나의 블록 수는 8 × 블록 크기(바이트)로도 계산됩니다[4]. 4 KiB 블록이면 그룹 하나가 32,768 블록, 곧 128 MiB 이고, 그룹 수는 장치 크기를 그룹 크기로 나눈 값입니다[4]. ext4 필드는 모두 리틀 엔디언으로 저장합니다[4].

그룹 N 은 `s_first_data_block + N × s_blocks_per_group` 번 블록에서 시작합니다. `s_first_data_block` 은 1 KiB 블록 파일 시스템에서는 1 이상이고 다른 블록 크기에서는 보통 0 입니다[1].

### 그룹 안의 배치

표준 블록 그룹은 다음 순서로 놓입니다[2].

| 순서 | 구조 | 크기 |
|---|---|---|
| 1 | 그룹 0 앞 여백 | 1024바이트 (그룹 0 에만) |
| 2 | 슈퍼블록 | 1 블록 |
| 3 | 그룹 서술자 표 (Group Descriptors) | 여러 블록 |
| 4 | 예약 GDT 블록 (Reserved GDT Blocks) | 여러 블록 |
| 5 | 블록 비트맵 | 1 블록 |
| 6 | 아이노드 비트맵 | 1 블록 |
| 7 | 아이노드 테이블 | 여러 블록 |
| 8 | 데이터 블록 | 나머지 |

그룹 0 의 앞 1024바이트는 부트 섹터 같은 것을 두도록 비워 두고, 슈퍼블록은 바이트 1024 에서 시작합니다[2]. 블록 크기가 1024 이면 블록 0 을 사용 중으로 표시하고 슈퍼블록은 블록 1 에 둡니다[2]. 다른 그룹에는 앞 여백이 없습니다[2].

그룹 안에서 위치가 정해진 것은 슈퍼블록과 그룹 서술자 표뿐이고, 비트맵과 아이노드 테이블은 그룹 서술자가 가리키는 곳에 있습니다[3]. 그래서 비트맵이 아이노드 테이블 뒤에 오거나 다른 그룹에 있을 수 있습니다[2]. 예약 GDT 블록은 mkfs 가 나중에 파일 시스템을 키울 때 그룹 서술자 표가 늘어날 자리로 잡아 두는 공간이고, 기본으로 처음 크기의 1024배까지 키울 수 있게 잡습니다[2][7]. 이 기능이 `resize_inode` 입니다[7].

### 사본이 있는 그룹

커널은 주로 그룹 0 의 슈퍼블록과 그룹 서술자를 쓰고, 디스크 앞부분이 망가질 때를 대비해 일부 그룹에 사본을 둡니다[2]. 사본이 없는 그룹은 블록 비트맵부터 시작합니다[2].

| 기능 | 사본이 있는 그룹 |
|---|---|
| 기능 없음 | 모든 그룹[1] |
| `sparse_super` | 그룹 0, 그리고 번호가 3·5·7 의 거듭제곱인 그룹(1, 3, 5, 7, 9, 25, 27, 49 …)[1] |
| `sparse_super2` | 슈퍼블록 0x24C 의 `s_backup_bgs[2]` 가 가리키는 두 그룹. 보통 그룹 1 과 마지막 그룹[1][7] |
| `meta_bg` | 메타블록 그룹마다 첫째 그룹에 서술자 블록, 둘째·마지막 그룹에 사본[2][3] |

`sparse_super` 는 요즘 만드는 ext2·ext3·ext4 에 모두 켜져 있습니다[7]. 1 은 3 의 0제곱이라서 그룹 1 에도 사본이 있습니다[15].

`meta_bg` 는 그룹 서술자 한 블록에 들어가는 그룹들을 메타블록 그룹 하나로 묶습니다[2]. 서술자가 64바이트이면 4 KiB 블록에서 메타블록 그룹 하나가 64 그룹(8 GiB)이고, 1 KiB 블록에서는 16 그룹입니다[2]. 이 배치를 쓰기 시작하는 그룹 번호는 `s_first_meta_bg` 에 있습니다[2].

`flex_bg` 는 그룹 여러 개를 하나로 묶어서, 묶음의 첫 그룹에 모든 그룹의 비트맵과 아이노드 테이블을 이어서 둡니다[2]. 묶음 크기는 2^`s_log_groups_per_flex` 그룹입니다[2]. 묶음 크기가 4 이면 그룹 0 에 슈퍼블록, 그룹 서술자, 그룹 0~3 의 블록 비트맵, 그룹 0~3 의 아이노드 비트맵, 그룹 0~3 의 아이노드 테이블이 차례로 오고 나머지가 데이터 블록입니다[2]. `flex_bg` 를 켜도 사본 슈퍼블록과 서술자는 늘 그룹 맨 앞에 있습니다[2]. `flex_bg` 와 `meta_bg` 는 함께 켤 수 있습니다[3].

### 슈퍼블록 필드

슈퍼블록은 1024바이트이고, 아래 오프셋은 슈퍼블록 시작 기준입니다[1]. 주 슈퍼블록의 절대 위치는 파티션 시작 + 0x400 이므로 매직 값은 파티션 시작 + 0x438 에 있습니다.

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x0 | 4 | `s_inodes_count` | 전체 아이노드 수 |
| 0x4 | 4 | `s_blocks_count_lo` | 전체 블록 수 (상위 32비트는 0x150) |
| 0xC | 4 | `s_free_blocks_count_lo` | 빈 블록 수 |
| 0x10 | 4 | `s_free_inodes_count` | 빈 아이노드 수 |
| 0x14 | 4 | `s_first_data_block` | 첫 데이터 블록 |
| 0x18 | 4 | `s_log_block_size` | 블록 크기 = 2^(10 + 값) |
| 0x20 | 4 | `s_blocks_per_group` | 그룹당 블록 수 |
| 0x28 | 4 | `s_inodes_per_group` | 그룹당 아이노드 수 |
| 0x2C | 4 | `s_mtime` | 마운트 시각 |
| 0x30 | 4 | `s_wtime` | 쓰기 시각 |
| 0x34 | 2 | `s_mnt_count` | 마지막 fsck 뒤 마운트 횟수 |
| 0x38 | 2 | `s_magic` | 0xEF53 |
| 0x3A | 2 | `s_state` | 파일 시스템 상태 (아래 표) |
| 0x3C | 2 | `s_errors` | 오류를 만났을 때 할 일: 1 계속, 2 읽기 전용으로 다시 마운트, 3 패닉 |
| 0x40 | 4 | `s_lastcheck` | 마지막 검사 시각 |
| 0x48 | 4 | `s_creator_os` | 만든 OS: 0 Linux, 1 Hurd, 2 Masix, 3 FreeBSD, 4 Lites |
| 0x4C | 4 | `s_rev_level` | 0 원래 형식, 1 아이노드 크기가 가변인 형식 |
| 0x54 | 4 | `s_first_ino` | 예약되지 않은 첫 아이노드 |
| 0x58 | 2 | `s_inode_size` | 아이노드 크기 (바이트) |
| 0x5A | 2 | `s_block_group_nr` | 이 슈퍼블록이 있는 그룹 번호 |
| 0x5C | 4 | `s_feature_compat` | 호환 기능 비트 |
| 0x60 | 4 | `s_feature_incompat` | 비호환 기능 비트 |
| 0x64 | 4 | `s_feature_ro_compat` | 읽기 전용 호환 기능 비트 |
| 0x68 | 16 | `s_uuid` | 볼륨 UUID |
| 0x78 | 16 | `s_volume_name` | 볼륨 레이블 |
| 0x88 | 64 | `s_last_mounted` | 마지막으로 마운트한 디렉터리 |
| 0xCE | 2 | `s_reserved_gdt_blocks` | 예약 GDT 블록 수 |
| 0xE0 | 4 | `s_journal_inum` | 저널 파일의 아이노드 번호 |
| 0xE8 | 4 | `s_last_orphan` | 지울 고아 아이노드 목록의 시작 |
| 0xFE | 2 | `s_desc_size` | 그룹 서술자 크기 (`64bit` 일 때) |
| 0x100 | 4 | `s_default_mount_opts` | 기본 마운트 옵션 비트 |
| 0x104 | 4 | `s_first_meta_bg` | `meta_bg` 배치를 쓰는 첫 그룹 |
| 0x108 | 4 | `s_mkfs_time` | 파일 시스템을 만든 시각 |
| 0x10C | 68 | `s_jnl_blocks[17]` | 저널 아이노드의 `i_block[]` 과 `i_size` 사본 |
| 0x174 | 1 | `s_log_groups_per_flex` | `flex_bg` 묶음 크기 = 2^값 |
| 0x178 | 8 | `s_kbytes_written` | 만든 뒤로 이 파일 시스템에 쓴 양 (KiB) |
| 0x194 | 4 | `s_error_count` | 본 오류 수 |
| 0x198 | 4 | `s_first_error_time` | 첫 오류 시각 |
| 0x19C | 4 | `s_first_error_ino` | 첫 오류에 걸린 아이노드 |
| 0x1A0 | 8 | `s_first_error_block` | 첫 오류에 걸린 블록 |
| 0x1A8 | 32 | `s_first_error_func` | 첫 오류가 난 함수 이름 |
| 0x1C8 | 4 | `s_first_error_line` | 첫 오류가 난 줄 번호 |
| 0x1CC | 4 | `s_last_error_time` | 마지막 오류 시각 |
| 0x1D0 | 4 | `s_last_error_ino` | 마지막 오류에 걸린 아이노드 |
| 0x1D4 | 4 | `s_last_error_line` | 마지막 오류가 난 줄 번호 |
| 0x1D8 | 8 | `s_last_error_block` | 마지막 오류에 걸린 블록 |
| 0x1E0 | 32 | `s_last_error_func` | 마지막 오류가 난 함수 이름 |
| 0x200 | 64 | `s_mount_opts` | 마운트 옵션 문자열 (NUL 로 끝남) |
| 0x24C | 8 | `s_backup_bgs[2]` | `sparse_super2` 에서 사본이 있는 두 그룹 |
| 0x270 | 4 | `s_checksum_seed` | `metadata_csum` 계산에 쓰는 씨앗 값 |
| 0x274~0x279 | 1씩 | `s_wtime_hi`, `s_mtime_hi`, `s_mkfs_time_hi`, `s_lastcheck_hi`, `s_first_error_time_hi`, `s_last_error_time_hi` | 각 시각의 상위 8비트 |
| 0x280 | 4 | `s_orphan_file_inum` | 고아 파일 (orphan file) 아이노드 번호 |
| 0x3FC | 4 | `s_checksum` | 슈퍼블록 체크섬 |

`s_state` 는 다음 값을 합친 것입니다[1].

| 값 | 뜻 |
|---|---|
| 0x0001 | 깨끗하게 마운트 해제함 |
| 0x0002 | 오류를 발견함 |
| 0x0004 | 고아 아이노드를 복구하는 중 |

기능 비트 가운데 해석에 자주 쓰는 것은 다음과 같습니다[1].

| 필드 | 값 | 이름 | 뜻 |
|---|---|---|---|
| compat | 0x4 | `HAS_JOURNAL` | 저널이 있음 |
| compat | 0x10 | `RESIZE_INODE` | 예약 GDT 블록이 있음 |
| compat | 0x200 | `SPARSE_SUPER2` | 사본이 두 그룹에만 있음 |
| compat | 0x1000 | `ORPHAN_FILE` | 고아 파일이 있음 |
| incompat | 0x4 | `RECOVER` | 복구가 필요함 |
| incompat | 0x10 | `META_BG` | 메타블록 그룹 배치 |
| incompat | 0x40 | `EXTENTS` | 익스텐트를 씀 |
| incompat | 0x80 | `64BIT` | 2^64 블록까지 씀 |
| incompat | 0x200 | `FLEX_BG` | 유연한 블록 그룹 |
| incompat | 0x2000 | `CSUM_SEED` | 체크섬 씨앗을 슈퍼블록에 둠 |
| incompat | 0x8000 | `INLINE_DATA` | 아이노드 안에 데이터를 둠 |
| incompat | 0x10000 | `ENCRYPT` | 암호화한 아이노드가 있을 수 있음 |
| incompat | 0x20000 | `CASEFOLD` | 대소문자를 구분하지 않는 디렉터리가 있을 수 있음 |
| ro_compat | 0x1 | `SPARSE_SUPER` | 사본이 일부 그룹에만 있음 |
| ro_compat | 0x10 | `GDT_CSUM` | 그룹 서술자 체크섬, 미초기화 그룹 |
| ro_compat | 0x400 | `METADATA_CSUM` | 메타데이터 체크섬 |
| ro_compat | 0x10000 | `ORPHAN_PRESENT` | 고아 파일에 정리할 항목이 있을 수 있음 |

`s_default_mount_opts` 의 0x0004 는 사용자 확장 속성, 0x0008 은 POSIX ACL, 0x0020·0x0040·0x0060 은 저널 모드(data·ordered·writeback), 0x0400 은 discard 지원입니다[1]. e2fsprogs 의 기본 설정은 `acl,user_xattr` 이라서 새로 만든 ext4 에서는 보통 0x000C 입니다[8].

### 그룹 서술자

그룹 서술자 표는 슈퍼블록 다음 블록부터 그룹 번호 순서로 서술자를 늘어놓습니다[2][3]. `64bit` 기능이 꺼져 있으면 서술자 하나가 32바이트이고 `bg_checksum` 에서 끝납니다[3]. `64bit` 이 켜져 있으면 64바이트 이상이고 크기는 슈퍼블록 `s_desc_size` 에 있습니다[3].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x0 | 4 | `bg_block_bitmap_lo` | 블록 비트맵 위치 |
| 0x4 | 4 | `bg_inode_bitmap_lo` | 아이노드 비트맵 위치 |
| 0x8 | 4 | `bg_inode_table_lo` | 아이노드 테이블 위치 |
| 0xC | 2 | `bg_free_blocks_count_lo` | 빈 블록 수 |
| 0xE | 2 | `bg_free_inodes_count_lo` | 빈 아이노드 수 |
| 0x10 | 2 | `bg_used_dirs_count_lo` | 디렉터리 수 |
| 0x12 | 2 | `bg_flags` | 그룹 플래그 (아래 표) |
| 0x18 | 2 | `bg_block_bitmap_csum_lo` | 블록 비트맵 체크섬 하위 16비트 |
| 0x1A | 2 | `bg_inode_bitmap_csum_lo` | 아이노드 비트맵 체크섬 하위 16비트 |
| 0x1C | 2 | `bg_itable_unused_lo` | 쓰지 않은 아이노드 수 |
| 0x1E | 2 | `bg_checksum` | 서술자 체크섬 |
| 0x20~0x3A | | `_hi` 필드들 | 위 값의 상위 부분 (`64bit` 이고 `s_desc_size` 가 32 보다 클 때만) |

`bg_flags` 값은 다음과 같습니다[3].

| 값 | 이름 | 뜻 |
|---|---|---|
| 0x1 | `INODE_UNINIT` | 아이노드 테이블과 비트맵을 초기화하지 않음 |
| 0x2 | `BLOCK_UNINIT` | 블록 비트맵을 초기화하지 않음 |
| 0x4 | `INODE_ZEROED` | 아이노드 테이블을 0 으로 채움 |

이 세 플래그는 mkfs 가 빈 그룹의 비트맵과 아이노드 테이블을 쓰지 않고 넘어가게 하려고 만든 것입니다[2]. mkfs 는 `INODE_ZEROED` 를 끈 채로 두고, 커널이 나중에 뒤에서 아이노드 테이블을 0 으로 채웁니다[2]. 이 기능의 이름은 `RO_COMPAT_GDT_CSUM` 이고 dumpe2fs 는 `uninit_bg` 로 표시하는데 둘은 같은 것입니다[2]. 마운트 옵션 `noinit_itable` 을 주면 이 채우기를 하지 않고, `init_itable=n` 은 채우는 속도를 늦춥니다[6]. `bg_itable_unused` 가 있으면 아이노드 테이블에서 `s_inodes_per_group - bg_itable_unused` 번째 항목 뒤는 살펴보지 않아도 됩니다[3].

## 읽는 법

### 헥스로 한 번

아래는 명세대로 만든 1 GiB ext4 의 슈퍼블록 일부입니다(만든 예시: 4 KiB 블록, 그룹 8개, 볼륨 레이블 `data`, 마지막 마운트 경로 `/srv/data`). 오프셋은 파티션 시작 기준이고, 체크섬은 계산하지 않았습니다.

```
00000400: 0000 0100 0000 0400 3333 0000 400d 0300  ........33..@...
00000410: defd 0000 0000 0000 0200 0000 0200 0000  ................
00000420: 0080 0000 0080 0000 0020 0000 907d 5b69  ......... ...}[i
00000430: 2803 5c69 0c00 ffff 53ef 0100 0100 0000  (.\i....S.......
00000440: b004 2d69 0000 0000 0000 0000 0100 0000  ..-i............
00000450: 0000 0000 0b00 0000 0001 0000 3c10 0000  ............<...
00000460: c222 0000 6b04 0000 3f2a 9c10 b7d4 4e5a  ."..k...?*....NZ
00000470: 8e01 c2d3 e4f5 a6b7 6461 7461 0000 0000  ........data....
00000480: 0000 0000 0000 0000 2f73 7276 2f64 6174  ......../srv/dat
00000490: 6100 0000 0000 0000 0000 0000 0000 0000  a...............
...
000004c0: 0000 0000 0000 0000 0000 0000 0000 7f00  ................
000004d0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000004e0: 0800 0000 0000 0000 0000 0000 0000 0000  ................
000004f0: 0000 0000 0000 0000 0000 0000 0101 4000  ..............@.
00000500: 0c00 0000 0000 0000 b004 2d69 0000 0000  ..........-i....
...
00000570: 0000 0000 0401 0000 0000 5000 0000 0000  ..........P.....
```

1. 0x438 의 `53 ef` 가 매직 0xEF53 입니다. 이 두 바이트로 ext 계열 슈퍼블록인지 먼저 판별합니다.
2. 0x400 의 `00 00 01 00` 은 아이노드 65,536개, 0x404 의 `00 00 04 00` 은 블록 262,144개입니다. 0x418 의 `02` 로 블록 크기가 2^(10+2) = 4096 이므로 전체 크기는 1 GiB 입니다.
3. 0x420 의 `00 80 00 00` 은 그룹당 32,768 블록, 0x428 의 `00 20 00 00` 은 그룹당 아이노드 8,192개입니다. 262,144 ÷ 32,768 = 8 이라서 그룹은 0~7 이고, `sparse_super` 가 켜져 있으면 사본은 그룹 1·3·5·7 에 있습니다.
4. 0x42C 의 `90 7d 5b 69` 는 0x695B7D90 이라서 `s_mtime` 이 2026-01-05 09:00:00 UTC, 0x430 의 `28 03 5c 69` 는 `s_wtime` 이 2026-01-05 18:30:00 UTC 입니다. 0x434 의 `0c 00` 은 마지막 fsck 뒤 12번 마운트했다는 뜻입니다.
5. 0x43A 의 `01 00` 은 `s_state` 0x0001 로 깨끗하게 마운트 해제한 상태이고, 0x43C 의 `01 00` 은 오류가 나면 계속 진행하는 설정입니다.
6. 0x45C 의 `3c 10 00 00` 은 compat 0x103C(`HAS_JOURNAL`·`EXT_ATTR`·`RESIZE_INODE`·`DIR_INDEX`·`ORPHAN_FILE`), 0x460 의 `c2 22 00 00` 은 incompat 0x22C2(`FILETYPE`·`EXTENTS`·`64BIT`·`FLEX_BG`·`CSUM_SEED`), 0x464 의 `6b 04 00 00` 은 ro_compat 0x046B(`SPARSE_SUPER`·`LARGE_FILE`·`HUGE_FILE`·`DIR_NLINK`·`EXTRA_ISIZE`·`METADATA_CSUM`) 입니다. incompat 에 `RECOVER`(0x4) 가 없으니 저널을 재생할 필요가 없는 상태입니다.
7. 0x468 부터 16바이트가 UUID `3f2a9c10-b7d4-4e5a-8e01-c2d3e4f5a6b7`, 0x478 부터 볼륨 레이블 `data`, 0x488 부터 마지막 마운트 경로 `/srv/data` 입니다.
8. 0x4E0 의 `08` 은 저널 아이노드 8, 0x4FE 의 `40 00` 은 서술자 크기 64바이트, 0x500 의 `0c 00 00 00` 은 기본 마운트 옵션 `user_xattr`·`acl` 입니다.
9. 0x508 의 `b0 04 2d 69` 는 `s_mkfs_time` 으로 2025-12-01 03:00:00 UTC 입니다.
10. 0x574 의 `04` 로 `flex_bg` 묶음은 16 그룹이고, 0x575 의 `01` 은 `s_checksum_type` 으로 체크섬 방식이 crc32c 라는 뜻입니다. 0x578 의 `00 00 50 00 …` 은 `s_kbytes_written` 5,242,880 KiB(5 GiB)입니다.

블록 크기가 4096 이고 `s_first_data_block` 이 0 이므로 슈퍼블록은 블록 0 에 있고, 그룹 서술자 표는 블록 1(바이트 0x1000)부터입니다. 아래는 같은 방식으로 만든 그룹 0 의 64바이트 서술자입니다.

```
00001000: 8100 0000 9100 0000 a100 0000 c05d f41f  .............]..
00001010: 0200 0400 0000 0000 0000 0000 f41f 0000  ................
00001020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00001030: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

블록 비트맵은 블록 129(0x81), 아이노드 비트맵은 블록 145(0x91), 아이노드 테이블은 블록 161(0xA1, 바이트 0xA1000)에서 시작합니다. 빈 블록은 24,000개(0x5DC0), 빈 아이노드는 8,180개(0x1FF4), 디렉터리는 2개이고, `bg_flags` 가 0x0004 라서 아이노드 테이블을 0 으로 채운 그룹입니다. 아이노드 테이블에서 아이노드 하나를 찾아가는 계산은 [아이노드와 익스텐트](inode-extent.md)에서 다룹니다.

그룹 1 의 사본 슈퍼블록은 앞 여백 없이 그룹 시작에 있으므로 블록 32,768, 곧 바이트 0x8000000 에서 시작하고 매직은 0x8000038 에 있습니다. 사본의 `s_block_group_nr`(0x5A) 에는 1 이 들어가 있어서, 떼어 낸 조각에서 슈퍼블록을 찾았을 때 어느 그룹의 사본인지 알 수 있습니다[1].

### 명령으로 한 번

e2fsprogs 의 dumpe2fs 는 슈퍼블록과 그룹 정보를 출력합니다[9].

```
dumpe2fs -h ext4.img
dumpe2fs ext4.img
dumpe2fs -g ext4.img
dumpe2fs -o superblock=32768 -o blocksize=4096 -h ext4.img
debugfs -R "stats -h" ext4.img
fsstat -o 2048 disk.img
```

`-h` 는 슈퍼블록만 보여 주고 그룹 서술자는 빼고, `-g` 는 그룹마다 첫 블록·슈퍼블록 위치·서술자 범위·비트맵·아이노드 테이블 범위를 콜론으로 나눠 찍습니다[9]. `-o superblock=` 과 `-o blocksize=` 는 사본 슈퍼블록으로 읽을 때 씁니다[9]. 마운트된 파일 시스템에 dumpe2fs 를 쓰면 출력이 오래되었거나 앞뒤가 맞지 않을 수 있습니다[9]. debugfs 는 `-w` 를 주지 않으면 읽기 전용으로 열고, `stats`(`show_super_stats`) 는 슈퍼블록과 그룹 서술자를, `-h` 를 주면 슈퍼블록만 보여 줍니다[10]. debugfs 로 사본 슈퍼블록을 쓰려면 `-s` 로 블록 번호를, `-b` 로 블록 크기를 함께 줍니다[10].

The Sleuth Kit 의 fsstat 는 `s_wtime` 을 "Last Written at", `s_lastcheck` 를 "Last Checked at", `s_mtime` 을 "Last Mounted at" 으로 찍고, `s_state` 의 0x1 비트로 "Unmounted properly" 나 "Unmounted Improperly" 를 찍습니다[11]. `s_last_mounted` 가 비어 있지 않으면 "Last mounted on" 으로 보여 주고, 저널 아이노드와 고아 아이노드 목록도 출력합니다[11].

## 포렌식에서 중요한 점

### 증명하는 것

슈퍼블록은 이 파일 시스템을 언제 만들었는지(`s_mkfs_time`), 마지막으로 언제 마운트했고 언제 썼는지(`s_mtime`·`s_wtime`), 마지막으로 어느 디렉터리에 마운트했는지(`s_last_mounted`) 보여 줍니다[1]. 루트 파일 시스템의 `s_mkfs_time` 은 설치 시점을 추정하는 단서가 됩니다([설치 날짜 가늠하기](../../../02-artifacts/system-info/install-date.md)). `s_mnt_count` 는 마지막 fsck 뒤 마운트 횟수이고, `s_kbytes_written` 은 만든 뒤로 쓴 양의 누계입니다[1].

슈퍼블록에는 파일 시스템 오류 수와 함께 첫 오류와 마지막 오류의 시각·아이노드·블록·함수 이름·줄 번호가 남습니다[1]. 저장 장치 고장이나 비정상 종료를 따질 때 이 값을 커널 로그와 맞춰 봅니다([커널 로그](../../../02-artifacts/system-info/kernel-log.md)).

외장 디스크나 USB 저장 장치의 ext4 는 `s_last_mounted` 와 UUID 로 어느 시스템의 어느 마운트 지점에 붙었는지 잇습니다. dissect.target 도 `/etc/fstab` 의 줄과 파일 시스템을 맞출 때 ext 계열은 UUID, `s_last_mounted`, 볼륨 레이블 가운데 하나가 맞는지 봅니다[12].

### 증명하지 못하는 것

슈퍼블록에는 누가 마운트했는지, 어느 호스트에서 마운트했는지가 없습니다. 여러 호스트의 동시 마운트를 막는 다중 마운트 보호 (Multiple Mount Protection, MMP, incompat 0x100)를 켠 파일 시스템에서는 `s_mmp_block`(0x168) 이 가리키는 MMP 블록에 파일 시스템을 연 호스트 이름(`mmp_nodename`)과 블록 장치 이름(`mmp_bdevname`)이 남지만, 열 때마다 새 값으로 씁니다[1][16]. 마운트 시각·쓰기 시각·마운트 경로는 한 값만 남고 덮어쓰이므로, 이 값으로 마운트 이력 전체를 알 수는 없습니다. `s_last_mounted` 는 경로 문자열이라 어느 호스트의 경로인지는 다른 흔적으로 정합니다.

### 시각 해석

슈퍼블록의 시각은 모두 Unix epoch 초이므로 UTC 로 읽습니다[1]. 하위 32비트는 각 필드에, 상위 8비트는 0x274~0x279 의 `_hi` 바이트에 있어서, 실제 값은 `lo + (hi << 32)` 입니다[1]. 값은 시각을 쓴 순간의 시스템 시계이므로, 시계를 바꾼 시스템에서는 바뀐 시계로 찍힙니다([Linux 의 시각 값](../../value-decoding/time-values.md), [시각을 조작했나](../../../04-scenarios/insider/time-manipulation.md)). 파일 하나하나의 시각은 [시각 값](timestamps.md)에서 다룹니다.

`s_mtime` 은 마운트 시각이라서 증거물을 읽기·쓰기로 마운트하면 분석한 시각으로 바뀔 수 있습니다. 증거물은 이미지로 떠서 dumpe2fs·debugfs·fsstat 처럼 마운트하지 않는 도구로 먼저 읽고 값을 기록해 둡니다.

### 지운 데이터·손상·비정상 종료

켜져 있는 시스템에서 뜬 이미지는 `s_state` 의 0x1 비트가 꺼져 있고 incompat 의 `RECOVER` 가 켜져 있을 가능성이 있습니다. 저널을 아직 재생하지 않은 상태라는 뜻이라서, 최근 메타데이터 변경이 저널에만 있을 수 있습니다([저널](journal-jbd2.md)). `s_last_orphan`·`s_orphan_file_inum` 과 ro_compat 의 `ORPHAN_PRESENT` 는 지웠지만 아직 열려 있던 파일이 정리되지 않았음을 알려 줍니다[1]([지운 파일이 남기는 것](deleted-files.md)).

주 슈퍼블록이 망가져도 사본 슈퍼블록과 사본 서술자로 파일 시스템을 읽을 수 있습니다[2][9]. 파티션 표가 없어진 디스크에서는 블록 경계마다 오프셋 0x38 에 `53 EF` 가 있는 곳을 찾고, 블록 크기·그룹당 블록 수·`s_block_group_nr` 가 서로 맞는지로 걸러 슈퍼블록 후보를 고릅니다. 매직이 2바이트뿐이라 다른 필드로 거르지 않으면 우연히 맞는 자리가 많이 나옵니다. 메타데이터가 거의 남지 않은 영역에서 아이노드를 카빙할 때도 아이노드 번호를 계산하려면 블록 크기, 아이노드 크기, 아이노드 비율, `flex_bg` 크기, `sparse_super`·`64bit` 여부가 필요하고[15], 이 값은 사본 슈퍼블록에서 얻습니다.

예약 GDT 블록(그룹 서술자 성장 블록, Group Descriptor Growth Blocks)에는 데이터가 남아 있을 수 있고[13], 이 블록과 미초기화 그룹의 구조는 데이터를 숨길 수 있는 자리입니다[14]. 이 영역은 평소 파일 데이터가 들어가지 않는 곳이라, 0 이 아닌 내용이 있으면 따로 살펴봅니다.

## 함정

- 사본 슈퍼블록은 주 슈퍼블록과 시각·카운터 값이 다를 가능성이 있습니다. 두 값을 한 파일 시스템의 같은 순간 값으로 섞어 쓰지 않고, 어느 그룹의 슈퍼블록에서 읽었는지 적어 둡니다.
- `BLOCK_UNINIT` 인 그룹은 커널과 e2fsprogs 가 블록 비트맵을 모두 0(모두 빈 블록)으로 여깁니다[4]. `meta_bg` 가 켜져 있으면 그 그룹 안에 비트맵과 서술자가 실제로 있어도 debugfs 가 빈 블록으로 보여 주므로 헷갈리기 쉽습니다[4].
- `metadata_csum` 이 켜져 있으면 슈퍼블록 체크섬은 체크섬 필드 앞까지 슈퍼블록 전체로 계산합니다[5]. 헥스 편집기로 시각만 고치면 체크섬이 맞지 않게 되고, dumpe2fs 는 체크섬이 틀리면 0 이 아닌 종료 코드로 끝납니다[9]. 체크섬이 틀린 슈퍼블록은 손으로 고쳤거나 손상된 것일 가능성이 있습니다.
- `s_checksum_seed` 는 처음 UUID 로 계산한 값입니다[1]. `CSUM_SEED` 가 켜진 파일 시스템에서 현재 UUID 로 계산한 값과 씨앗이 다르면, 만든 뒤에 UUID 를 바꿨을 가능성이 있습니다.
- fsstat 는 시각의 하위 32비트만 읽고 `_hi` 바이트는 쓰지 않습니다[11]. 또 "Volume ID" 는 UUID 16바이트를 거꾸로 이어 붙인 16진 문자열이라서, `/etc/fstab` 의 `UUID=` 값과 맞춰 볼 때는 슈퍼블록 0x68 의 바이트를 직접 읽거나 dumpe2fs 출력을 씁니다[11].
- e2fsprogs 판에 따라 기본 기능이 다릅니다. 기능 비트는 실제 볼륨의 슈퍼블록에서 읽고, 배포판 이름으로 짐작하지 않습니다([ext4](index.md)).

## 도구

| 도구 | 보여 주는 것 | 참고 |
|---|---|---|
| e2fsprogs `dumpe2fs` | 슈퍼블록 전체, 그룹마다 서술자·비트맵·아이노드 테이블 위치 | `-h` 슈퍼블록만, `-g` 기계가 읽을 형식, `-o superblock=` 사본 사용[9] |
| e2fsprogs `debugfs` | `stats` 로 슈퍼블록과 서술자 | 기본 읽기 전용, `-s`·`-b` 로 사본 사용, `-n` 은 체크섬 검사를 끔[10] |
| The Sleuth Kit `fsstat` | 시각·상태·마지막 마운트 경로·기능·저널 아이노드·고아 아이노드 | 이미지 파일을 곧바로 읽음, 시각은 하위 32비트만[11] |
| dissect.target | 파일 시스템을 fstab 마운트 지점에 붙임 | ext 는 UUID·`s_last_mounted`·볼륨 레이블로 맞춤[12] |

파티션 시작 오프셋은 [파티션](../../disk-volume/partitions.md)에서, LVM 안의 ext4 는 [LVM 논리 볼륨](../../disk-volume/lvm.md)에서 찾습니다. 다른 파일 시스템의 같은 구조는 [XFS](../xfs.md)와 [Btrfs](../btrfs.md)에서 다룹니다.

## 참고 문헌

1. Linux kernel, `Documentation/filesystems/ext4/super.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/super.rst
2. Linux kernel, `Documentation/filesystems/ext4/blockgroup.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/blockgroup.rst
3. Linux kernel, `Documentation/filesystems/ext4/group_descr.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/group_descr.rst
4. Linux kernel, `Documentation/filesystems/ext4/overview.rst`·`blocks.rst`·`bitmaps.rst`. https://github.com/torvalds/linux/tree/master/Documentation/filesystems/ext4
5. Linux kernel, `Documentation/filesystems/ext4/checksums.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/checksums.rst
6. Linux kernel, `Documentation/admin-guide/ext4.rst`. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/ext4.rst
7. e2fsprogs, ext4(5). https://github.com/tytso/e2fsprogs/blob/master/misc/ext4.5.in
8. e2fsprogs, `misc/mke2fs.conf.in`. https://github.com/tytso/e2fsprogs/blob/master/misc/mke2fs.conf.in
9. e2fsprogs, dumpe2fs(8). https://github.com/tytso/e2fsprogs/blob/master/misc/dumpe2fs.8.in
10. e2fsprogs, debugfs(8). https://github.com/tytso/e2fsprogs/blob/master/debugfs/debugfs.8.in
11. The Sleuth Kit, `tsk/fs/ext2fs.cpp`. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs.cpp
12. dissect.target, `dissect/target/plugins/os/unix/_os.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/_os.py
13. Kevin D. Fairbanks, "An Analysis of Ext4 for Digital Forensics", DFRWS 2012 USA 발표 자료. https://dfrws.org/presentation/an-analysis-of-ext4-for-digital-forensics/
14. Thomas Göbel, Harald Baier, "Anti-forensics in ext4: On secrecy and usability of timestamp-based data hiding", Digital Investigation 24 (2018) S111–S120, DFRWS 2018 Europe. https://doi.org/10.1016/j.diin.2018.01.014
15. Andreas Dewald, Sabine Seufert, "AFEIC: Advanced Forensic Ext4 Inode Carving", DFRWS 2017 Europe 발표 자료. https://dfrws.org/presentation/afeic-advanced-forensic-ext4-inode-carving/
16. Linux kernel, `Documentation/filesystems/ext4/mmp.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/mmp.rst
