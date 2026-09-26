---
title: "저널"
parent: "ext4"
grand_parent: "기반 · 파일 시스템"
nav_order: 40
---

# 저널 (jbd2)

ext4 는 메타데이터를 제자리에 쓰기 전에 저널 (journal) 에 먼저 적어 두는데, 이 저널에는 최근에 바뀐 아이노드·디렉터리·비트맵 블록의 옛 사본과 트랜잭션마다 커밋 시각이 남아 있어서 지운 파일의 이름과 익스텐트를 되찾는 단서가 됩니다.

## 저널에 무엇이 남나

ext4 저널은 ext3 에서 들어왔고, 시스템이 갑자기 꺼져도 메타데이터가 반쯤 바뀐 채로 남지 않게 하려고 둡니다[1]. 저널을 다루는 커널 계층 이름이 jbd2 이고, ocfs2 도 같은 jbd2 를 씁니다[1]. 바뀔 블록을 한 트랜잭션 (transaction) 으로 묶어 저널에 먼저 쓰고, 커밋 기록까지 디스크에 닿은 뒤에 원래 자리에 옮겨 씁니다. 도중에 시스템이 멈추면 마지막 커밋까지 저널을 다시 적용하는데, 이 과정을 재생 (replay) 이라고 부릅니다[1].

저널에 무엇이 들어가는지는 마운트 옵션 `data=` 가 정합니다[1][3].

| 모드 | 저널에 들어가는 것 | 비고 |
|---|---|---|
| `data=ordered` | 메타데이터만 | 기본값. 파일 데이터를 먼저 디스크에 쓴 뒤 메타데이터를 커밋합니다[3] |
| `data=journal` | 메타데이터와 파일 데이터 | 지연 할당과 O_DIRECT 가 꺼집니다[3] |
| `data=writeback` | 메타데이터만 | 데이터와 메타데이터의 쓰기 순서를 지키지 않습니다[3] |

기본 모드에서도 파일 하나만 데이터까지 저널에 쓰게 할 수 있습니다. 아이노드 플래그 0x4000 `EXT4_JOURNAL_DATA_FL` 이 켜진 파일이 그렇고[10], `chattr +j` 가 이 속성을 켭니다. 이 속성은 root 나 `CAP_SYS_RESOURCE` 권한이 있는 프로세스만 바꿀 수 있습니다[11]. 슈퍼블록의 `s_default_mount_opts`(0x100) 값 0x0020·0x0040·0x0060 은 각각 journal·ordered·writeback 모드를 기본으로 정해 둔 것입니다[2]. 실제로 어느 모드로 마운트했는지는 `/etc/fstab` 과 마운트 기록에서 확인합니다([마운트 기록](../../../02-artifacts/devices/mounts.md)).

기본 모드라면 저널에는 아이노드 테이블 블록, 디렉터리 블록, 블록·아이노드 비트맵, 익스텐트 트리 블록 같은 메타데이터가 블록 단위 통째로 들어갑니다[1][16]. 블록 크기 4096 B, 아이노드 크기 256 B 인 기본 설정[12]이라면 아이노드 테이블 블록 하나에 아이노드 16 개가 들어 있으므로, 한 파일을 바꿔도 이웃 아이노드 15 개의 그 시점 모습이 함께 저널에 남습니다.

## 위치와 배포판 차이

내부 저널은 숨은 일반 파일이고, 보통 아이노드 8 번입니다[1]. 슈퍼블록 `s_journal_inum`(0xE0) 에 저널 아이노드 번호가 있고, `s_jnl_blocks[17]`(0x10C) 에는 저널 아이노드의 `i_block[]` 15 개 값과 `i_size_high`·`i_size` 사본이 있습니다[2]. 저널 아이노드가 망가져도 이 사본으로 저널을 찾을 수 있습니다. 파일 시스템 안 저널은 최대 2^32 블록까지 둘 수 있습니다[1].

외부 저널 (external journal) 을 쓰는 파일 시스템은 `s_journal_inum` 이 0 이고 `s_journal_uuid`(0xD0) 가 채워져 있으며, 저널 장치 쪽 슈퍼블록에는 `journal_dev` 기능이 켜집니다[1][2][13]. 저널 장치에는 1024 B 여백, ext4 슈퍼블록, 그다음 블록에 저널 슈퍼블록이 옵니다[1]. 이 경우 저널은 다른 장치에 있으므로 그 장치도 함께 이미징해야 합니다.

| 기준 판 | 설치 프로그램 기본 루트 파일 시스템 | 저널 |
|---|---|---|
| Ubuntu 24.04 LTS | ext4[14] | 이 페이지의 jbd2 |
| RHEL 9 | XFS[19] | XFS 로그. [XFS](../xfs.md) 페이지에서 다룹니다 |

e2fsprogs 원본 `mke2fs.conf` 의 ext4 기능 목록은 `has_journal,extent,huge_file,flex_bg,metadata_csum,metadata_csum_seed,64bit,dir_nlink,extra_isize,orphan_file` 이고 `fast_commit` 은 없습니다[12]. 배포판 패키지가 이 파일을 바꿔 넣었을 수 있으므로 실제 시스템의 `/etc/mke2fs.conf` 와 슈퍼블록 기능 비트를 직접 확인합니다.

## 구조

jbd2 의 모든 필드는 빅 엔디언 (big-endian) 입니다. ext4 본체가 리틀 엔디언인 것과 반대입니다[1]. 슈퍼블록 필드는 [슈퍼블록과 블록 그룹](superblock-block-group.md) 페이지에서 다룹니다.

저널은 저널 슈퍼블록 뒤에 트랜잭션이 이어지는 원형 기록입니다[1][16]. 한 트랜잭션은 서술자 블록과 그 뒤의 데이터 블록(또는 취소 블록)으로 시작해 커밋 블록으로 끝납니다. 커밋 기록이 없거나 체크섬이 맞지 않는 트랜잭션은 재생할 때 버립니다[1].

### 블록 공통 머리 (12 B)

데이터 블록을 뺀 저널 블록은 모두 이 머리로 시작합니다[1].

| 오프셋 | 크기 | 이름 | 뜻 |
|---|---|---|---|
| 0x0 | 4 | `h_magic` | `0xC03B3998` |
| 0x4 | 4 | `h_blocktype` | 1 서술자, 2 커밋, 3 저널 슈퍼블록 v1, 4 저널 슈퍼블록 v2, 5 취소 |
| 0x8 | 4 | `h_sequence` | 이 블록이 속한 트랜잭션 ID |

### 저널 슈퍼블록 (1024 B)

| 오프셋 | 크기 | 이름 | 뜻 |
|---|---|---|---|
| 0x0 | 12 | `s_header` | 공통 머리 |
| 0xC | 4 | `s_blocksize` | 저널 블록 크기 |
| 0x10 | 4 | `s_maxlen` | 저널 전체 블록 수 |
| 0x14 | 4 | `s_first` | 기록이 시작되는 첫 블록 |
| 0x18 | 4 | `s_sequence` | 로그에서 기대하는 첫 커밋 ID |
| 0x1C | 4 | `s_start` | 로그 시작 블록. 0 이라고 저널이 깨끗하다는 뜻은 아닙니다 |
| 0x20 | 4 | `s_errno` | 저널을 중단할 때 남긴 오류 값 |
| 0x24 | 4 | `s_feature_compat` | 0x1 데이터 블록 체크섬 |
| 0x28 | 4 | `s_feature_incompat` | 0x1 REVOKE, 0x2 64BIT, 0x4 ASYNC_COMMIT, 0x8 CSUM_V2, 0x10 CSUM_V3, 0x20 FAST_COMMIT |
| 0x2C | 4 | `s_feature_ro_compat` | 현재 쓰는 비트 없음 |
| 0x30 | 16 | `s_uuid` | 저널 UUID. 마운트할 때 ext4 슈퍼블록의 사본과 비교합니다 |
| 0x50 | 1 | `s_checksum_type` | 1 CRC32, 2 MD5, 3 SHA1, 4 CRC32C |
| 0x54 | 4 | `s_num_fc_blocks` | 빠른 커밋 블록 수 |
| 0x58 | 4 | `s_head` | 첫 빈 블록. 저널이 비었을 때만 최신 값입니다 |
| 0xFC | 4 | `s_checksum` | 슈퍼블록 체크섬 |

0x24 부터는 v2 슈퍼블록에만 있는 필드입니다[1].

### 서술자 블록과 태그

서술자 블록은 공통 머리 뒤 0xC 부터 태그 배열을 두고, 태그마다 뒤따르는 데이터 블록 하나가 원래 어느 파일 시스템 블록에 쓰일지 적습니다[1]. 데이터 블록은 원래 블록 내용을 그대로 담습니다. 다만 데이터 블록의 첫 4 B 가 우연히 `0xC03B3998` 이면 그 4 B 를 0 으로 바꾸고 태그에 escaped 플래그를 켭니다[1]. 이런 블록을 되살릴 때는 첫 4 B 를 마법 수로 되돌려야 원래 내용이 됩니다.

태그 모양은 기능 비트에 따라 달라집니다[1].

| 조건 | 태그 크기 | 필드 순서 |
|---|---|---|
| CSUM_V3 켜짐 | 16 B, UUID 붙으면 32 B | `t_blocknr`(0x0) · `t_flags`(0x4, 4 B) · `t_blocknr_high`(0x8) · `t_checksum`(0xC) |
| CSUM_V3 꺼짐 | 8·12·24·28 B | `t_blocknr`(0x0) · `t_checksum`(0x4, 2 B) · `t_flags`(0x6, 2 B) · 64BIT 이면 `t_blocknr_high`(0x8) |

두 경우 모두 "같은 UUID" 플래그가 없으면 태그 끝에 UUID 16 B 가 붙습니다. 태그 플래그는 0x1 escaped, 0x2 같은 UUID, 0x4 지운 블록(쓰이지 않는 것으로 보임), 0x8 이 서술자의 마지막 태그입니다. CSUM_V2 나 CSUM_V3 가 켜지면 블록 끝 4 B 에 서술자 블록 체크섬이 붙습니다[1].

### 취소 블록

취소 블록 (revocation block) 은 공통 머리 뒤 `r_count`(0xC, 이 블록에서 쓴 바이트 수) 와 취소할 파일 시스템 블록 번호 배열(0x10 부터, 64BIT 면 8 B, 아니면 4 B)로 이루어집니다[1]. 앞선 트랜잭션에 있던 블록을 재생하지 말라는 표시입니다. 메타데이터 블록이 해제된 뒤 파일 데이터 블록으로 다시 쓰인 경우가 대표적입니다. 취소는 "이 저널 블록이 다른 저널 블록으로 대체됐다" 는 뜻이 아닙니다[1].

### 커밋 블록

| 오프셋 | 크기 | 이름 | 뜻 |
|---|---|---|---|
| 0x0 | 12 | 공통 머리 | `h_blocktype` = 2 |
| 0xC | 1 | `h_chksum_type` | 체크섬 종류 |
| 0xD | 1 | `h_chksum_size` | 체크섬 바이트 수 |
| 0x10 | 32 | `h_chksum[]` | CSUM_V2·V3 면 첫 4 B 가 커밋 블록 체크섬 |
| 0x30 | 8 | `h_commit_sec` | 커밋 시각, epoch 초 |
| 0x38 | 4 | `h_commit_nsec` | 커밋 시각의 나노초 |

### 빠른 커밋

빠른 커밋 (fast commit) 은 `data=ordered` 모드에서 쓸 수 있고 mkfs 때 켜야 합니다[1]. 켜진 파일 시스템은 슈퍼블록 compat 0x400 이 켜져 있고, 저널에 빠른 커밋 블록이 실제로 있으면 저널 incompat 0x20 이 켜집니다[2]. 빠른 커밋 영역은 태그·길이·값 (TLV) 기록이고, 블록 사본 대신 작업 결과를 적습니다[1].

| 태그 | 담는 것 |
|---|---|
| `EXT4_FC_TAG_HEAD` | 이 빠른 커밋들을 적용할 기준 트랜잭션 ID |
| `EXT4_FC_TAG_ADD_RANGE` | 아이노드 번호와 붙일 익스텐트 |
| `EXT4_FC_TAG_DEL_RANGE` | 아이노드 번호와 뗄 논리 오프셋 범위 |
| `EXT4_FC_TAG_CREAT` | 부모 아이노드 번호, 아이노드 번호, 새 파일의 디렉터리 항목 |
| `EXT4_FC_TAG_LINK` | 부모 아이노드 번호, 아이노드 번호, 디렉터리 항목 |
| `EXT4_FC_TAG_UNLINK` | 부모 아이노드 번호, 아이노드 번호, 디렉터리 항목 |
| `EXT4_FC_TAG_PAD` | 빈 자리 |
| `EXT4_FC_TAG_TAIL` | 커밋 ID 와 CRC |

`CREAT`·`LINK`·`UNLINK` 태그에는 디렉터리 항목이 들어 있으므로 만들거나 지운 파일 이름이 남을 수 있습니다[1]. 일반 커밋이 한 번 일어나면 그 전의 빠른 커밋은 모두 무효가 되고 영역을 다시 씁니다[1].

## 읽는 법

1. ext4 슈퍼블록에서 compat 0x4 `HAS_JOURNAL`, incompat 0x4 `RECOVER`, `s_journal_inum`, `s_journal_uuid` 를 읽습니다[2]. `RECOVER` 는 파일 시스템이 복구, 곧 저널 재생을 기다린다는 표시입니다.
2. 저널 아이노드(보통 8)의 익스텐트를 따라가 저널을 파일 하나로 뽑습니다. `debugfs -R 'dump <8> ./journal' 이미지` 로 저널을 파일 하나로 뽑을 수 있습니다[17]. debugfs 는 `-w` 를 주지 않으면 읽기 전용으로 엽니다[5].
3. 저널 슈퍼블록에서 블록 크기, `s_first`, `s_sequence`, `s_start`, 기능 비트를 읽습니다. 기능 비트가 태그 크기를 정하므로 이 단계를 건너뛰면 태그를 잘못 셉니다.
4. 저널 블록을 처음부터 끝까지 차례로 읽어 마법 수가 있는 블록마다 종류와 트랜잭션 ID 를 적고, 서술자 태그를 따라 뒤따르는 데이터 블록의 원래 파일 시스템 블록 번호를 짝짓습니다.
5. 짝지은 블록 번호가 아이노드 테이블 안이면 어느 아이노드들이 들어 있는지 계산하고([아이노드와 익스텐트](inode-extent.md)), 디렉터리 블록이면 항목을 풉니다([디렉터리 항목과 해시 트리](directory-htree.md)).
6. 같은 파일 시스템 블록이 여러 트랜잭션에 나오면 트랜잭션 ID 와 커밋 시각 순서로 늘어놓아 바뀐 과정을 봅니다.

트랜잭션 ID 가 `s_sequence` 보다 작은 기록은 이미 원래 자리에 옮겨 쓴(체크포인트된) 옛 트랜잭션입니다[1][6]. 재생 대상은 아니지만 덮이기 전까지 내용은 남아 있고, 포렌식에서 쓸모 있는 기록은 대부분 여기에 있습니다.

### 헥스로 읽기

아래는 명세로 만든 커밋 블록 예시입니다. 체크섬 필드는 0 으로 두었습니다.

```text
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x000   C0 3B 39 98 00 00 00 02 00 00 1A 2B 00 00 00 00
0x010   00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0x020   00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0x030   00 00 00 00 69 55 CF 40 1D CD 65 00 00 00 00 00
```

- 0x0 `C0 3B 39 98`: jbd2 마법 수
- 0x4 `00 00 00 02`: 커밋 블록
- 0x8 `00 00 1A 2B`: 트랜잭션 ID 6699
- 0x30 `00 00 00 00 69 55 CF 40`: 1767231296 초, 곧 2026-01-01 01:34:56 UTC
- 0x38 `1D CD 65 00`: 500,000,000 나노초

빅 엔디언이라 바이트를 앞에서부터 그대로 읽으면 됩니다. ext4 아이노드 시각처럼 바이트를 뒤집으면 틀린 값이 나옵니다.

## 포렌식에서 중요한 점

### 증명하는 것

- 어느 커밋 시각에 어느 파일 시스템 블록이 어떤 내용으로 기록됐는지 보여 줍니다[1].
- 옛 아이노드 테이블 블록 사본에서 지우기 전 아이노드의 크기·시각·익스텐트를 볼 수 있습니다. 지운 뒤 아이노드에서 무엇이 0 이 되는지는 [지운 파일이 남기는 것](deleted-files.md) 페이지에 있습니다.
- 옛 디렉터리 블록 사본에서 지운 파일 이름을 볼 수 있습니다. Linux 5.13 부터 커널은 파일을 지울 때 디렉터리 항목의 `rec_len` 을 뺀 필드를 0 으로 지우지만, 지운 값은 저널에 남아 있을 수 있습니다[9].
- 기본 모드가 아닌 `data=journal` 이거나 파일에 `j` 속성이 있으면 파일 데이터의 옛 내용도 저널에 있습니다[3][11].

### 증명하지 못하는 것

- 기본 `data=ordered` 에서는 파일 내용이 저널에 들어가지 않습니다[1]. 저널에서 파일 내용을 되찾을 수 있다고 쓰면 안 됩니다.
- 어느 사용자나 프로세스가 바꿨는지는 저널에 없습니다. 아이노드 사본의 UID 는 파일 소유자이지 바꾼 사람이 아닙니다.
- 저널은 원형으로 다시 쓰이므로[16] 오래된 트랜잭션은 덮입니다. 어떤 변경이 저널에 없다고 해서 그 변경이 없었다고 할 수 없습니다.
- 한 트랜잭션에는 여러 작업이 섞입니다. 같은 트랜잭션 안의 블록 둘이 한 작업에서 나왔다고 단정할 수 없습니다.

### 시각 해석

`h_commit_sec` 는 64비트 epoch 초라서 UTC 이고, 2038 년 넘침 문제가 없습니다[1]. 시각 값 일반은 [Linux 의 시각 값](../../value-decoding/time-values.md) 페이지를 봅니다. 이 값은 트랜잭션을 커밋한 시각이지 파일을 바꾼 시각이 아닙니다. 마운트 옵션 `commit=` 이 열린 트랜잭션의 최대 나이를 정하고 기본값은 5초라서[3], 기본 설정에서는 변경 시각이 커밋 시각보다 조금 이를 수 있습니다. 커밋 시각은 시스템 시계를 따르므로 시계를 바꿔 두면 커밋 시각도 따라 바뀝니다([시각을 조작했나](../../../04-scenarios/insider/time-manipulation.md)).

아이노드 사본 안의 atime·mtime·ctime·crtime 은 그 사본이 저널에 쓰인 시점의 값입니다. 이 값들의 형식과 갱신 규칙은 [시각 값](timestamps.md) 페이지에 있습니다.

### 비정상 종료와 재생

비정상 종료 뒤 뜬 이미지나 실행 중인 시스템에서 뜬 이미지는 incompat `RECOVER` 가 켜져 있을 가능성이 있습니다. 이 상태의 저널에는 아직 제자리에 쓰이지 않은 최신 메타데이터가 있습니다. 저널을 재생하면 파일 시스템 본체는 최신이 되지만 이미지가 바뀌므로, 재생은 원본이 아닌 사본에만 합니다.

## 함정

- **읽기 전용 마운트도 저널을 재생합니다.** `ro` 로 마운트해도 ext3·ext4 가 dirty 상태면 저널을 재생해 장치에 씁니다. 막으려면 `ro,noload` 를 주거나 blockdev 로 장치 자체를 읽기 전용으로 만듭니다[4]. `norecovery`·`noload` 는 마운트할 때 저널을 싣지 않는 옵션이고, 정상 해제되지 않은 파일 시스템이면 본체가 어긋난 상태로 보입니다[3][13]. 이미징 절차는 [디스크 이미징](../../../03-techniques/acquisition/disk-imaging.md) 페이지를 봅니다.
- **`s_start` 가 0 이어도 저널이 비었다는 뜻이 아닙니다**[1]. 체크포인트된 옛 트랜잭션은 그대로 남아 있을 수 있습니다.
- **태그 크기를 고정값으로 보면 블록 짝이 어긋납니다.** 태그 크기는 64BIT·CSUM_V3 비트에 따라 8 B 부터 32 B 까지 달라집니다[1]. Sleuth Kit 의 저널 태그 구조체는 블록 번호 4 B 와 플래그 4 B 로 된 8 B 입니다[7]. 저널 슈퍼블록 incompat 에 64BIT 나 CSUM_V3 가 켜져 있으면 jls 가 찍는 "FS Block" 번호를 그대로 믿지 말고 서술자 블록을 헥스로 대조합니다.
- **jls 커밋 시각의 소수부는 쓰지 않습니다.** jls 는 커밋 블록에 `sec: 초.소수` 를 찍는데, 소수부를 `NSEC_PER_SEC / 10 * h_commit_nsec` 로 계산해 찍습니다[6]. 초 부분만 쓰고 나노초는 0x38 을 직접 읽습니다.
- **체크포인트 ioctl 로 저널 잔재를 지울 수 있습니다.** `EXT4_IOC_CHECKPOINT` 에 `EXT4_IOC_CHECKPOINT_FLAG_ZEROOUT` 이나 `EXT4_IOC_CHECKPOINT_FLAG_DISCARD` 를 주면 체크포인트 뒤 저널 블록을 0 으로 채우거나 discard 합니다[1]. 저널 전체가 0 이거나 체크포인트된 옛 트랜잭션이 하나도 없다면 이런 정리가 있었을 가능성이 있고, 다른 흔적과 함께 봐야 합니다([흔적을 지웠나](../../../04-scenarios/insider/anti-forensics.md)).
- **재생을 이용한 은닉 흔적은 본체와 비트맵의 어긋남으로 남습니다.** Eckstein·Jahnke(2005) 는 ext3 에서 블록 비트맵만 바꾼 뒤 저널 재생을 거치게 해 블록을 숨기는 시험을 했습니다. 이 방식은 읽기 전용 e2fsck 에서 "Block bitmap differences" 가 수천 건 나오므로 드러나지만, 디렉터리 항목이 가리키지 않는 아이노드 하나로 블록을 묶은 변형은 어긋남이 하나뿐이라 평소 생기는 어긋남에 섞여 찾기 어렵습니다[15]. 이 시험은 2005 년 ext3 조건의 결과이므로 체크섬이 붙은 요즘 ext4 에 그대로 옮기지 않습니다.

## 도구

| 도구 | 쓰는 법 | 알려 주는 것 |
|---|---|---|
| Sleuth Kit `jls` | `jls image.raw` | 저널 블록마다 Superblock·Descriptor·Commit·Revoke 종류, `seq`, 서술자가 가리키는 FS Block 번호, 커밋 시각[6][8] |
| Sleuth Kit `jcat` | `jcat image.raw 8 34` | 저널 블록 번호로 지정한 블록의 원래 바이트. 파일 시스템 블록 번호가 아닌 저널 블록 번호를 줍니다[8] |
| debugfs `logdump` | `debugfs -R 'logdump -a' image.raw` | 옵션에 따라 서술자, 특정 블록 기록, 데이터 내용, 저널 슈퍼블록을 보여 줍니다[5] |
| debugfs `imap` | `debugfs -R 'imap <12>' image.raw` | 아이노드가 아이노드 테이블의 어느 블록 어느 오프셋에 있는지[5] |

jls 는 트랜잭션 ID 가 `s_sequence` 보다 작거나 블록 위치가 `s_start` 보다 앞이면 "Unallocated" 로 표시합니다[6]. 이미 체크포인트된 옛 기록이라는 뜻이고, 버려도 된다는 뜻이 아닙니다.

debugfs `logdump` 의 옵션은 다음과 같습니다[5]. `-a` 는 모든 서술자 블록 내용을, `-b 블록` 은 그 파일 시스템 블록을 가리키는 모든 저널 기록을, `-c` 는 `-a`·`-b` 로 고른 데이터 블록 내용을 보여 줍니다. `-O` 는 체크포인트된 옛 기록까지 보여 주고, `-n 수` 는 마법 수가 없는 블록에서 멈추지 않고 그 수만큼의 트랜잭션까지 계속 읽습니다. `-S` 는 저널 슈퍼블록 내용을 찍고, `-s` 는 슈퍼블록의 백업 정보(`s_jnl_blocks`)로 저널을 찾으며, `-f 파일` 은 따로 뽑아 둔 저널 파일을 읽습니다. `imap` 으로 찾은 아이노드 테이블 블록 번호를 `logdump -b` 에 넣으면 그 아이노드가 담긴 블록의 옛 사본을 모두 볼 수 있습니다.

지운 파일은 저널을 뽑은 뒤 ext4magic 에 날짜 범위(`-a`·`-b`)와 저널 파일(`-j`)을 주어 되살릴 수 있습니다[17]. AFEIC 는 저널 구조를 해석하지 않고도 저널 안에 든 아이노드를 카빙으로 찾아 되살립니다[18]. 복구 절차 전체는 [지운 파일 되살리기](../../../03-techniques/analysis/file-recovery.md) 페이지에서 다룹니다. 커밋 시각을 다른 기록과 한 줄로 늘어놓는 방법은 [타임라인 만들기](../../../03-techniques/analysis/timeline.md) 페이지를 봅니다.

## 참고 문헌

1. Linux kernel, Documentation/filesystems/ext4/journal.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/journal.rst
2. Linux kernel, Documentation/filesystems/ext4/super.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/super.rst
3. Linux kernel, Documentation/admin-guide/ext4.rst. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/ext4.rst
4. util-linux, sys-utils/mount.8.adoc. https://github.com/util-linux/util-linux/blob/master/sys-utils/mount.8.adoc
5. e2fsprogs, debugfs/debugfs.8.in. https://github.com/tytso/e2fsprogs/blob/master/debugfs/debugfs.8.in
6. The Sleuth Kit, tsk/fs/ext2fs_journal.cpp. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs_journal.cpp
7. The Sleuth Kit, tsk/fs/tsk_ext2fs.h. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/tsk_ext2fs.h
8. The Sleuth Kit, man/jls.1, man/jcat.1. https://github.com/sleuthkit/sleuthkit/tree/develop/man
9. Leah Rumancik, "ext4: wipe ext4_dir_entry2 upon file deletion", Linux kernel commit 6c0912739699, 2021. https://github.com/torvalds/linux/commit/6c0912739699d8e4b6a87086401bf3ad3c59502d
10. Linux kernel, Documentation/filesystems/ext4/inodes.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inodes.rst
11. e2fsprogs, misc/chattr.1.in. https://github.com/tytso/e2fsprogs/blob/master/misc/chattr.1.in
12. e2fsprogs, misc/mke2fs.conf.in. https://github.com/tytso/e2fsprogs/blob/master/misc/mke2fs.conf.in
13. e2fsprogs, misc/ext4.5.in. https://github.com/tytso/e2fsprogs/blob/master/misc/ext4.5.in
14. Canonical subiquity (ubuntu/noble), subiquity/server/controllers/storage.py. https://github.com/canonical/subiquity/blob/ubuntu/noble/subiquity/server/controllers/storage.py
15. Knut Eckstein, Marko Jahnke, "Data Hiding in Journaling File Systems", DFRWS 2005 USA 발표 자료. https://dfrws.org/presentation/data-hiding-in-journaling-file-systems/
16. Kevin Fairbanks, "An Analysis of Ext4 for Digital Forensics", DFRWS 2012 USA 발표 자료. https://dfrws.org/presentation/an-analysis-of-ext4-for-digital-forensics/
17. Ali Hadi, Mariam Khader, Thomas Claflin, "Learning Linux Forensic Analysis and Why it Matters", DFRWS 워크숍 발표 자료. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
18. Andreas Dewald, Sabine Seufert, "AFEIC: Advanced Forensic Ext4 Inode Carving", DFRWS 2017 Europe 발표 자료. https://dfrws.org/presentation/afeic-advanced-forensic-ext4-inode-carving/
19. Red Hat anaconda (rhel-9), data/product.d/rhel.conf. https://github.com/rhinstaller/anaconda/blob/rhel-9/data/product.d/rhel.conf
