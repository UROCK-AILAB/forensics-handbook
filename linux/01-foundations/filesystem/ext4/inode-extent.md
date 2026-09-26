---
title: "아이노드와 익스텐트"
parent: "ext4"
grand_parent: "기반 · 파일 시스템"
nav_order: 20
---

# 아이노드와 익스텐트 (Inode·Extent)

아이노드 (inode) 하나에는 파일 한 개의 종류·권한·소유자 번호·크기·시각과 데이터 블록 위치가 들어 있고, ext4 는 그 위치를 익스텐트 (extent) 라는 "시작 블록 + 길이" 묶음으로 적습니다.

파일 이름은 아이노드가 아니라 디렉터리 항목에 있습니다. 이름에서 아이노드 번호를 찾는 과정은 [디렉터리 항목과 해시 트리](directory-htree.md) 에서, 아이노드 테이블이 디스크 어디에 있는지는 [슈퍼블록과 블록 그룹](superblock-block-group.md) 에서 다룹니다. 이 페이지는 번호로 아이노드를 찾아 읽고, 익스텐트를 따라 데이터 블록까지 가는 방법을 다룹니다.

## 이 형식을 쓰는 아티팩트

ext4 볼륨의 모든 파일·디렉터리·심볼릭 링크·장치 파일에 아이노드가 하나씩 있습니다. 파일 목록 타임라인(bodyfile), 파일 복구, 소유자 확인처럼 파일 시스템 메타데이터를 쓰는 분석은 모두 아이노드를 읽는 일에서 시작합니다. 시각 다섯 개의 해석은 [시각 값](timestamps.md), 지운 파일의 아이노드에 무엇이 남는지는 [지운 파일이 남기는 것](deleted-files.md) 에 모았습니다.

## 구조

ext4 의 모든 필드는 리틀 엔디언입니다[16].

### 아이노드 찾기

아이노드 번호는 1 부터 시작하고 0 번은 없습니다. 번호로 위치를 구하는 식은 아래와 같습니다[1].

```
블록 그룹 = (아이노드 번호 - 1) / s_inodes_per_group
그룹 안 순번 = (아이노드 번호 - 1) % s_inodes_per_group
아이노드 테이블 안 바이트 위치 = 그룹 안 순번 × s_inode_size
```

`s_inodes_per_group` 과 `s_inode_size` 는 슈퍼블록에, 그룹별 아이노드 테이블 시작 블록은 그룹 서술자에 있습니다([슈퍼블록과 블록 그룹](superblock-block-group.md)).

아이노드 기록 하나의 크기는 두 가지를 나눠 봐야 합니다. 디스크에 잡힌 기록 크기는 슈퍼블록의 `s_inode_size` 이고, 그 안에서 구조체가 실제로 쓰는 크기는 128 + `i_extra_isize` 입니다. ext2·ext3 는 128바이트 고정이었고, ext4 는 기본 기록 크기가 256바이트, 구조체가 160바이트(`i_extra_isize` = 32, 2019년 8월 기준)입니다[1]. 구조체 끝과 기록 끝 사이에는 확장 속성을 둡니다[1]. mke2fs 설정 파일의 기본값도 `inode_size = 256` 이고, `hurd` 유형은 128 입니다[8]. 확장 속성 해석은 [권한·확장 속성·ACL·Capabilities](../permissions-xattr.md) 에서 다룹니다.

### 특수 아이노드

1~10 번은 예약 번호이고 11 번이 보통 첫 일반 아이노드(대개 `lost+found`)입니다[5].

| 번호 | 쓰임 |
|---|---|
| 1 | 불량 블록 목록 |
| 2 | 루트 디렉터리 |
| 3·4 | 사용자·그룹 쿼터 |
| 5 | 부트로더 |
| 6 | 복구용 디렉터리(undelete) |
| 7 | 예약 그룹 서술자(resize inode) |
| 8 | 저널([저널](journal-jbd2.md)) |
| 9·10 | exclude(스냅숏용)·replica(비표준 기능용) |
| 11 | 첫 일반 아이노드(`s_first_ino`), 보통 `lost+found` |

이 밖에 슈퍼블록의 `s_lpf_ino`, `s_prj_quota_inum`, `s_orphan_file_inum` 이 가리키는 아이노드는 예약 번호 밖에서 잡히지만 표준 디렉터리 트리에서는 가리키지 않습니다[5].

### 아이노드 필드

오프셋은 아이노드 기록 시작 기준입니다[1].

| 오프셋 | 크기 | 이름 | 뜻 |
|---|---|---|---|
| 0x00 | 2 | `i_mode` | 파일 종류 + 권한 비트 |
| 0x02 | 2 | `i_uid` | 소유자 UID 하위 16비트 |
| 0x04 | 4 | `i_size_lo` | 크기(바이트) 하위 32비트 |
| 0x08 | 4 | `i_atime` | 마지막 접근 시각(초) |
| 0x0C | 4 | `i_ctime` | 아이노드 변경 시각(초) |
| 0x10 | 4 | `i_mtime` | 데이터 수정 시각(초) |
| 0x14 | 4 | `i_dtime` | 지운 시각(초) |
| 0x18 | 2 | `i_gid` | GID 하위 16비트 |
| 0x1A | 2 | `i_links_count` | 하드 링크 수 |
| 0x1C | 4 | `i_blocks_lo` | 차지한 블록 수 하위 32비트 |
| 0x20 | 4 | `i_flags` | 아이노드 플래그 |
| 0x24 | 4 | `osd1` | Linux 에서는 `l_i_version` |
| 0x28 | 60 | `i_block` | 블록 맵, 익스텐트 트리, 짧은 링크 대상, 인라인 데이터 |
| 0x64 | 4 | `i_generation` | 파일 판 번호(NFS 용) |
| 0x68 | 4 | `i_file_acl_lo` | 확장 속성 블록 번호 하위 32비트 |
| 0x6C | 4 | `i_size_high` | 크기 상위 32비트 |
| 0x74 | 12 | `osd2` | Linux 에서는 0x74 `l_i_blocks_high`, 0x76 `l_i_file_acl_high`, 0x78 `l_i_uid_high`, 0x7A `l_i_gid_high`, 0x7C `l_i_checksum_lo` |
| 0x80 | 2 | `i_extra_isize` | 128 을 넘는 구조체 크기 |
| 0x82 | 2 | `i_checksum_hi` | 체크섬 상위 16비트 |
| 0x84·0x88·0x8C | 4씩 | `i_ctime_extra`·`i_mtime_extra`·`i_atime_extra` | 시각 확장 비트·나노초 |
| 0x90 | 4 | `i_crtime` | 만든 시각(초) |
| 0x94 | 4 | `i_crtime_extra` | 만든 시각 확장 비트·나노초 |
| 0x98 | 4 | `i_version_hi` | 판 번호 상위 32비트 |
| 0x9C | 4 | `i_projid` | 프로젝트 ID |

값을 합칠 때 주의할 곳이 세 군데 있습니다. 크기는 `i_size_lo` + (`i_size_high` × 2^32) 이고, UID·GID 는 앞쪽 16비트에 `osd2` 안의 상위 16비트를 붙여야 온전한 값이 됩니다[1]. `i_blocks_lo` 의 단위는 파일 시스템 기능에 따라 다릅니다. huge_file 기능이 꺼져 있거나, 켜져 있어도 아이노드에 `EXT4_HUGE_FILE_FL`(0x40000) 이 없으면 512바이트 단위이고, 그 플래그가 있으면 파일 시스템 블록 단위입니다[1].

`i_links_count` 는 보통 65,000 을 넘지 않습니다. dir_nlink 기능이 켜진 볼륨에서 하위 디렉터리가 64,998 개를 넘으면 디렉터리의 이 값을 1 로 두어 "개수 모름" 을 나타냅니다[1].

시각 필드의 초·나노초·확장 비트를 푸는 법은 [시각 값](timestamps.md) 에 있습니다.

### i_mode

위 4비트가 파일 종류이고 아래 12비트가 권한입니다[1].

| 값 | 파일 종류 |
|---|---|
| 0x1000 | FIFO |
| 0x2000 | 문자 장치 |
| 0x4000 | 디렉터리 |
| 0x6000 | 블록 장치 |
| 0x8000 | 일반 파일 |
| 0xA000 | 심볼릭 링크 |
| 0xC000 | 소켓 |

권한 비트는 0x800 SUID, 0x400 SGID, 0x200 sticky 와 소유자·그룹·기타의 rwx 9비트입니다[1].

### i_flags

분석에 자주 쓰는 값만 추렸습니다[1].

| 값 | 이름 | 뜻 |
|---|---|---|
| 0x10 | `EXT4_IMMUTABLE_FL` | 바꿀 수 없는 파일(chattr `i`) |
| 0x20 | `EXT4_APPEND_FL` | 덧붙이기만 가능(chattr `a`) |
| 0x80 | `EXT4_NOATIME_FL` | 접근 시각을 갱신하지 않음 |
| 0x800 | `EXT4_ENCRYPT_FL` | 암호화한 아이노드 |
| 0x1000 | `EXT4_INDEX_FL` | 해시 트리 디렉터리 |
| 0x4000 | `EXT4_JOURNAL_DATA_FL` | 데이터도 저널을 거쳐 기록 |
| 0x40000 | `EXT4_HUGE_FILE_FL` | 블록 수를 파일 시스템 블록 단위로 셈 |
| 0x80000 | `EXT4_EXTENTS_FL` | `i_block` 이 익스텐트 트리 |
| 0x100000 | `EXT4_VERITY_FL` | verity 보호 파일 |
| 0x200000 | `EXT4_EA_INODE_FL` | 큰 확장 속성 값을 담은 아이노드 |
| 0x10000000 | `EXT4_INLINE_DATA_FL` | 데이터가 아이노드 안에 있음 |
| 0x40000000 | `EXT4_CASEFOLD_FL` | 대소문자를 구분하지 않는 디렉터리 |

0x1(보안 삭제)과 0x2(복구 보존)는 정의만 있고 구현되지 않은 값입니다[1]. 이 플래그가 켜져 있어도 지울 때 동작은 달라지지 않습니다.

### i_block 의 네 가지 쓰임

`i_block` 60바이트는 아이노드 종류와 플래그에 따라 다르게 읽습니다[2].

**짧은 심볼릭 링크.** 링크 대상 문자열이 60바이트보다 짧으면 `i_block` 에 문자열을 바로 적고 데이터 블록을 쓰지 않습니다[2].

**블록 맵 (ext2·ext3 방식).** 4바이트 블록 번호 15개로, 0~11 은 파일 블록 0~11 을 직접 가리키고 12·13·14 는 단일·이중·삼중 간접 블록을 가리킵니다[2][3]. 4KiB 블록이면 단일 간접이 파일 블록 12~1035, 이중 간접이 1036~1049611 을 맡습니다[3]. 이 방식에는 마법 수도 체크섬도 없어서 간접 블록이 쓰레기인지 알아볼 표시가 없고, 2^32 블록 넘는 위치를 가리킬 수 없습니다[2].

**익스텐트 트리.** `i_flags` 에 0x80000 이 있으면 `i_block` 은 익스텐트 트리의 뿌리입니다[2]. 구조는 아래에서 설명합니다.

**인라인 데이터.** inline_data 기능이 켜진 볼륨에서 아이노드에 0x10000000 이 있으면 60바이트보다 작은 파일은 `i_block` 에 내용을 바로 담습니다[4]. 그보다 큰 파일도 나머지가 아이노드 안 확장 속성 공간에 들어가면 확장 속성 `system.data` 에 담고, 그마저 넘치면 일반 블록을 잡아 내용을 옮깁니다[4]. 인라인 디렉터리는 `i_block` 첫 4바이트가 부모 디렉터리 아이노드 번호이고 나머지 56바이트가 디렉터리 항목 배열입니다[4]. inline_data 는 mke2fs 기본 기능 목록에 없으므로[8], 실제 볼륨 슈퍼블록의 기능 비트로 켜져 있는지 확인합니다.

### 익스텐트 트리

트리의 모든 노드는 12바이트 머리 (`ext4_extent_header`) 로 시작합니다[2].

| 오프셋 | 크기 | 이름 | 뜻 |
|---|---|---|---|
| 0x0 | 2 | `eh_magic` | 0xF30A |
| 0x2 | 2 | `eh_entries` | 유효한 항목 수 |
| 0x4 | 2 | `eh_max` | 들어갈 수 있는 최대 항목 수 |
| 0x6 | 2 | `eh_depth` | 0 이면 잎(데이터 블록을 가리킴), 1 이상이면 안쪽 노드 |
| 0x8 | 4 | `eh_generation` | 트리 세대(Lustre 용, 표준 ext4 는 쓰지 않음) |

머리 뒤에는 `eh_entries` 개의 항목이 옵니다. 안쪽 노드 (index node) 의 항목은 `ext4_extent_idx`, 잎 노드 (leaf node) 의 항목은 `ext4_extent` 이고 둘 다 12바이트입니다[2].

| 구조 | 오프셋 | 크기 | 이름 | 뜻 |
|---|---|---|---|---|
| `ext4_extent_idx` | 0x0 | 4 | `ei_block` | 이 노드가 맡는 첫 파일 블록 |
| | 0x4 | 4 | `ei_leaf_lo` | 아래 단계 노드의 블록 번호 하위 32비트 |
| | 0x8 | 2 | `ei_leaf_hi` | 블록 번호 상위 16비트 |
| | 0xA | 2 | `ei_unused` | 쓰지 않음 |
| `ext4_extent` | 0x0 | 4 | `ee_block` | 이 익스텐트가 맡는 첫 파일 블록(논리 블록) |
| | 0x4 | 2 | `ee_len` | 블록 수 |
| | 0x6 | 2 | `ee_start_hi` | 데이터 시작 블록 상위 16비트 |
| | 0x8 | 4 | `ee_start_lo` | 데이터 시작 블록 하위 32비트 |

뿌리는 `i_block` 안에 있어서 머리 12바이트 뒤에 익스텐트 4개(4 × 12 = 48바이트)까지는 추가 블록 없이 적힙니다[2]. 익스텐트가 5개 이상이면 뿌리가 안쪽 노드가 되고 아래 단계 노드는 별도 블록에 놓입니다. 트리 깊이는 최대 5단계입니다[2].

`ee_len` 이 32768 이하면 초기화된 익스텐트이고, 32768 을 넘으면 미초기화 익스텐트 (uninitialized extent) 이고 실제 길이는 `ee_len` − 32768 입니다[2].

아이노드 밖에 놓인 익스텐트 블록은 끝 4바이트(`ext4_extent_tail`)에 체크섬을 둡니다. metadata_csum 기능이 켜져 있으면 값은 crc32c(파일 시스템 UUID + 아이노드 번호 + 아이노드 generation + 체크섬 앞까지의 블록 내용) 입니다[2][6]. `i_block` 안의 뿌리는 아이노드 체크섬이 함께 보호합니다[2].

### 아이노드 체크섬

metadata_csum 기능이 켜져 있으면 아이노드마다 crc32c(파일 시스템 UUID + 아이노드 번호 + generation + 체크섬 필드를 0 으로 둔 아이노드 전체) 를 계산해 하위 16비트는 `l_i_checksum_lo`(0x7C), 상위 16비트는 `i_checksum_hi`(0x82)에 둡니다[1][6]. 아이노드를 직접 편집하고 체크섬을 다시 계산하지 않으면 이 값이 어긋납니다.

## 읽는 법

### 헥스로 한 번

아래는 명세로 만든 예시이고 값은 모두 지어낸 것입니다. 4KiB 블록, `s_inode_size` 256, huge_file 기능이 켜진 볼륨의 일반 파일 아이노드이며, 시각 필드는 `..` 로 가렸습니다.

```
오프셋     00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  A4 81 E8 03 88 13 00 00  .. .. .. ..  .. .. .. ..
00000010  .. .. .. ..  00 00 00 00  E8 03 01 00  10 00 00 00
00000020  00 00 08 00  .. .. .. ..  0A F3 01 00  04 00 00 00
00000030  00 00 00 00  00 00 00 00  02 00 00 00  00 80 08 00
...
00000080  20 00 .. ..
```

읽는 순서는 이렇습니다.

1. 0x00 의 `A4 81` 은 0x81A4 입니다. 위 4비트 0x8000 이 일반 파일이고, 아래 0x1A4 는 권한 0644 입니다.
2. 0x02 의 `E8 03` 은 UID 하위 16비트 1000 이고, 0x04 의 `88 13 00 00` 은 크기 5,000바이트입니다. 0x78 의 `l_i_uid_high` 가 0 이면 UID 는 1000 입니다.
3. 0x14 의 `i_dtime` 이 0 이라 지운 기록이 없고, 0x1A 의 링크 수는 1 입니다.
4. 0x1C 의 `10 00 00 00` 은 16 입니다. 아이노드에 huge_file 플래그가 없으므로 512바이트 단위이고, 8,192바이트 곧 4KiB 블록 2개를 차지합니다.
5. 0x20 의 `00 00 08 00` 은 0x80000 이라 `i_block` 을 익스텐트 트리로 읽습니다.
6. 0x28 부터 머리입니다. `0A F3` 는 마법 수 0xF30A, 항목 1개, 최대 4개, 깊이 0(잎)입니다.
7. 0x34 부터 익스텐트 하나입니다. `ee_block` 0, `ee_len` 2, `ee_start_hi` 0, `ee_start_lo` 0x00088000 이므로 파일 블록 0~1 이 물리 블록 557,056~557,057 에 있습니다. 볼륨 시작에서 바이트 위치는 557,056 × 4,096 = 0x88000000 입니다.
8. 5,000바이트만 파일 내용이고, 두 번째 블록의 나머지 3,192바이트는 크기 밖 영역입니다.
9. 0x80 의 `20 00` 은 `i_extra_isize` 32 라서 구조체가 160바이트이고, 0x84~0x97 의 시각 확장 필드가 유효합니다.

이 아이노드가 12 번이고 `s_inodes_per_group` 이 8,192 라면 그룹 0 의 순번 11 이므로, 그룹 0 아이노드 테이블 시작에서 11 × 256 = 0xB00 바이트 떨어진 곳에 있습니다.

### 공개 도구로 한 번

e2fsprogs 의 `debugfs` 는 `-w` 를 주지 않으면 읽기 전용으로 열고, `-c` 를 주면 비트맵을 읽지 않는 읽기 전용 모드로 엽니다[9]. 명령은 아이노드를 경로나 꺾쇠로 감싼 번호로 받습니다[9].

```
debugfs -R 'stat <12>' ext4.img
debugfs -R 'inode_dump <12>' ext4.img
debugfs -R 'dump_extents <12>' ext4.img
debugfs -R 'imap <12>' ext4.img
debugfs -R 'icheck 557056' ext4.img
debugfs -R 'ncheck 12' ext4.img
```

`stat` 은 아이노드 내용을 풀어서 보여 줍니다[9]. `crtime`·`dtime` 은 stat() 으로는 볼 수 없고 debugfs 로 볼 수 있습니다[1]. `inode_dump` 는 헥스로, `-b` 는 `i_block` 만, `-e`·`-x` 는 구조체 뒤 확장 속성 영역을 보여 줍니다[9]. `dump_extents` 는 익스텐트 트리를 출력하고 `-n` 은 안쪽 노드만, `-l` 은 잎만 보여 줍니다[9]. `imap` 은 아이노드가 아이노드 테이블 어디에 있는지, `icheck` 는 블록 번호를 쓰는 아이노드를, `ncheck` 는 아이노드 번호의 경로를 알려 줍니다[9].

TSK 는 `istat` 으로 아이노드를, `icat` 으로 익스텐트를 따라간 내용을 꺼냅니다. TSK 는 UID·GID 를 상위 16비트까지 합쳐 읽습니다[11].

## 포렌식에서 중요한 점

### 증명하는 것

아이노드는 파일 종류, 권한, 숫자 UID·GID, 크기, 하드 링크 수, 플래그(immutable·append 등), 시각, 데이터 블록 위치를 증명합니다. `i_dtime` 이 0 이 아닌 아이노드는 지운 파일의 아이노드일 가능성이 있습니다. 다만 orphan_file 기능이 없는 볼륨에서 열린 채로 지운 파일은 `i_dtime` 필드에 시각이 아니라 다음 고아 아이노드 번호가 들어갑니다[1]. 자세한 판단은 [지운 파일이 남기는 것](deleted-files.md) 에 있습니다.

### 증명하지 못하는 것

아이노드에는 파일 이름이 없습니다. 이름은 디렉터리 항목에서 찾고, 이름 하나가 아니라 여러 개일 수 있습니다(하드 링크). UID·GID 는 숫자뿐이라 사용자 이름은 실제 시스템의 계정 파일과 맞춰 봐야 합니다([UID·GID 와 사용자 이름 잇기](../../value-decoding/uid-gid.md)). 소유자는 나중에 바꿀 수 있으므로 소유자 UID 가 곧 파일을 만든 계정이라는 뜻은 아닙니다.

### 지운 뒤의 익스텐트

파일을 지우면 커널은 해제한 익스텐트의 물리 시작 블록과 길이를 0 으로 바꾸고 `eh_entries` 를 줄이며, 트리가 모두 비면 뿌리 머리의 `eh_depth` 를 0 으로 되돌립니다[10]. 그래서 지운 파일의 아이노드만으로는 데이터 위치를 찾기 어렵습니다. 저널에 남은 옛 아이노드 사본과 카빙으로 되찾는 방법은 [지운 파일이 남기는 것](deleted-files.md) 과 [저널](journal-jbd2.md) 에서 다룹니다. 익스텐트 안쪽 노드 블록은 지울 때 0 으로 지워지지 않아서, 그 익스텐트 머리를 파일 복구 단서로 쓸 수 있습니다[12].

### 할당 방식으로 데이터 위치 추정하기

ext4 는 파일 데이터 블록을 아이노드와 같은 블록 그룹에, 한 디렉터리 안 파일의 아이노드를 그 디렉터리와 같은 그룹에 두려고 합니다[7]. 루트 바로 아래에 만든 디렉터리는 덜 찬 그룹으로 흩어 놓습니다[7]. 새 파일에는 8KiB 를 미리 잡았다가 닫을 때 남는 부분을 풀고, 지연 할당 (delayed allocation) 으로 실제 위치는 디스크에 쓰기 직전에 정합니다[7]. 지연 할당은 기본으로 켜져 있고 `nodelalloc` 마운트 옵션으로 끕니다[14]. 지운 파일의 데이터를 찾을 때 같은 디렉터리의 다른 파일이 놓인 그룹부터 보는 근거가 됩니다. 다만 이 규칙은 "그렇게 하려 한다" 는 정책이라 위치를 보장하지 않습니다.

### 아이노드 카빙

아이노드에는 마법 수가 없어서 서명 하나로 찾을 수 없습니다. 대신 권한 비트, 시각 범위와 순서, 링크 수, 익스텐트 플래그, 익스텐트 머리(0xF30A), 파일 종류를 조합하면 슈퍼블록 없이도 아이노드를 찾을 수 있습니다[13]. Ubuntu 12.04 16GB 시험에서 걸러 내는 힘이 가장 좋았던 조건은 익스텐트 머리 조건(선택도 0.004%)과 시각 범위 조건(0.003%)이었고, 저널 안의 아이노드도 되찾을 수 있었고, 다시 포맷한 ext4 에도 되찾을 수 있는 데이터가 남아 있었습니다[13]. 블록 크기·아이노드 크기·inode ratio·flex group 크기·sparse·64bit 옵션을 알면 찾은 아이노드의 물리 주소에서 아이노드 번호를 거꾸로 계산할 수 있습니다[13].

## 함정

- **기록 크기와 구조체 크기를 섞지 않습니다.** 다음 아이노드는 `s_inode_size` 만큼 떨어져 있고, 확장 속성은 128 + `i_extra_isize` 뒤부터 기록 끝까지입니다[1]. 128바이트 아이노드 볼륨에는 시각 확장 필드와 `i_crtime` 이 없습니다[1][8].
- **EA_INODE 아이노드의 시각 필드는 시각이 아닙니다.** 0x200000 플래그가 있으면 `i_atime` 은 속성 값 체크섬, `i_ctime` 은 참조 수 하위 32비트, `i_mtime` 은 속성을 가진 아이노드 번호입니다[1].
- **미초기화 익스텐트는 도구마다 다르게 보입니다.** TSK 는 `ee_len` 이 32768 을 넘는 익스텐트를 빈 구간 (sparse) 으로 처리하고 물리 주소를 0 으로 둡니다[11]. 이 구간의 물리 블록에 남은 옛 내용은 TSK 로 꺼낸 내용에 들어가지 않으므로, 필요하면 익스텐트의 `ee_start` 로 블록을 직접 읽습니다. 미리 잡아 둔 익스텐트에는 옛 내용이 남아 있을 수 있습니다[12].
- **`dump_extents` 가 보여 주는 안쪽 노드 마지막 익스텐트의 길이·범위는 추정값입니다.** 디스크 구조에 저장된 값이 아니라 라이브러리가 계산한 값이라 어긋나 보여도 손상 표시가 아닙니다[9].
- **블록 맵 아이노드의 간접 블록은 검증할 표시가 없습니다.** ext2·ext3 에서 올린 볼륨이나 익스텐트 플래그가 없는 아이노드는 간접 블록 내용이 블록 번호 목록인지 쓰레기인지 스스로 판단해야 합니다[2].

## 도구

| 도구 | 쓰임 |
|---|---|
| debugfs `stat`, `inode_dump`, `dump_extents`, `blocks`, `imap`, `icheck`, `ncheck`, `ea_list` | 아이노드 풀어 보기, 헥스, 익스텐트 트리, 블록 ↔ 아이노드 ↔ 경로[9] |
| TSK `istat`, `icat` | 아이노드 해석, 내용 추출[11] |
| dissect.extfs | ext 계열 파일 시스템 파이썬 파서[15] |

## 참고 문헌

1. Linux kernel, `Documentation/filesystems/ext4/inodes.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inodes.rst
2. Linux kernel, `Documentation/filesystems/ext4/ifork.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/ifork.rst
3. Linux kernel, `Documentation/filesystems/ext4/blockmap.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/blockmap.rst
4. Linux kernel, `Documentation/filesystems/ext4/inlinedata.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inlinedata.rst
5. Linux kernel, `Documentation/filesystems/ext4/special_inodes.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/special_inodes.rst
6. Linux kernel, `Documentation/filesystems/ext4/checksums.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/checksums.rst
7. Linux kernel, `Documentation/filesystems/ext4/allocators.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/allocators.rst
8. e2fsprogs, `misc/mke2fs.conf.in`. https://github.com/tytso/e2fsprogs/blob/master/misc/mke2fs.conf.in
9. e2fsprogs, `debugfs/debugfs.8.in`. https://github.com/tytso/e2fsprogs/blob/master/debugfs/debugfs.8.in
10. Linux kernel, `fs/ext4/extents.c` (`ext4_ext_rm_leaf`, `ext4_ext_remove_space`). https://github.com/torvalds/linux/blob/master/fs/ext4/extents.c
11. The Sleuth Kit, `tsk/fs/ext2fs.cpp`. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs.cpp
12. Kevin D. Fairbanks, "An Analysis of Ext4 for Digital Forensics", DFRWS 2012 USA 발표 자료. https://dfrws.org/presentation/an-analysis-of-ext4-for-digital-forensics/
13. Andreas Dewald, Sabine Seufert, "AFEIC: Advanced Forensic Ext4 Inode Carving", DFRWS 2017 발표 자료(2017-03-23). https://dfrws.org/presentation/afeic-advanced-forensic-ext4-inode-carving/
14. Linux kernel, `Documentation/admin-guide/ext4.rst`. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/ext4.rst
15. dissect.extfs, `README.md`. https://github.com/fox-it/dissect.extfs
16. Linux kernel, `Documentation/filesystems/ext4/overview.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/overview.rst
