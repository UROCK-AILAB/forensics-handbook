---
title: "파일 시스템 트리와 아이노드"
parent: "APFS 구조"
grand_parent: "기반 · 디스크·볼륨"
nav_order: 30
---

# 파일 시스템 트리와 아이노드 (FS Tree·Inode)

APFS 볼륨의 파일과 디렉터리는 파일 시스템 트리 (file-system tree)라는 B-트리의 레코드로 저장되고, 파일 하나가 아이노드 (inode)·디렉터리 항목·익스텐트·확장 속성 같은 여러 레코드로 나뉘어 객체 ID 순서로 나란히 놓입니다 [1].

볼륨 슈퍼블록에서 이 트리를 찾아오는 과정은 [객체와 체크포인트 (Object·Checkpoint)](object-checkpoint.md)에 있고, 이 페이지는 트리 안의 레코드를 다룹니다. 아이노드의 시각 필드는 [APFS의 시각 네 가지 (Create·Modify·Change·Access)](timestamps.md)에서, 확장 속성 레코드는 [확장 속성 (Extended Attributes)](extended-attributes.md)에서 따로 설명합니다.

## 이 구조를 쓰는 곳

APFS 볼륨에 있는 모든 파일의 이름, 부모 디렉터리, 소유자, 크기, 시각, 데이터 위치가 이 트리에 있습니다 [1]. 파일 경로를 다시 짜 맞추거나 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)에 파일 시스템 시각을 넣을 때, [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md)에서 옛 레코드를 풀 때 모두 이 레코드 형식을 읽습니다.

## 레코드 키

파일 시스템 레코드의 키는 `j_key_t` 로 시작하고, 그 안의 `obj_id_and_type` (uint64) 하나가 하위 60비트에 객체 ID(`OBJ_ID_MASK` 0x0fffffffffffffff)를, 상위 4비트에 레코드 형식(`OBJ_TYPE_SHIFT` 60)을 담습니다 [1]. 트리는 객체 ID, 레코드 형식, 그리고 확장 속성과 디렉터리 항목이면 이름 순서로 정렬해서 한 파일의 레코드가 서로 붙어 있습니다 [1]. 예를 들어 파일 두 개를 담은 디렉터리는 아이노드 레코드 1개와 디렉터리 항목 레코드 2개로 이루어집니다 [1]. 레코드 형식 값과 객체마다 있는 레코드는 아래 두 표와 같습니다 [1].

| 값 | 레코드 형식 | 뜻 |
|---|---|---|
| 1 | SNAP_METADATA | 스냅숏 메타데이터 |
| 2 | EXTENT | 물리 익스텐트(키는 시작 블록 주소) |
| 3 | INODE | 아이노드 |
| 4 | XATTR | 확장 속성 |
| 5 | SIBLING_LINK | 아이노드에서 하드 링크들로 |
| 6 | DSTREAM_ID | 데이터 스트림(참조 수) |
| 7 | CRYPTO_STATE | 파일별 암호화 상태. iOS용이고 macOS에는 자리표시만 있음 |
| 8 | FILE_EXTENT | 파일 익스텐트 |
| 9 | DIR_REC | 디렉터리 항목 |
| 10 | DIR_STATS | 디렉터리 통계 |
| 11 | SNAP_NAME | 스냅숏 이름 |
| 12 | SIBLING_MAP | 하드 링크에서 대상 아이노드로 |
| 13 | FILE_INFO | 파일 데이터 추가 정보 |

| 객체 | 반드시 있는 레코드 | 있을 수 있는 레코드 |
|---|---|---|
| 파일 | INODE | CRYPTO_STATE, DSTREAM_ID, EXTENT, FILE_EXTENT, SIBLING_LINK, XATTR |
| 디렉터리 | INODE | CRYPTO_STATE, DIR_REC, DIR_STATS, XATTR |
| 심볼릭 링크 | INODE, XATTR(`com.apple.fs.symlink`) | |

## 예약된 아이노드 번호

| 번호 | 뜻 |
|---|---|
| 0 | 무효 |
| 1 | 루트의 부모. 디스크에 실제 아이노드는 없음 |
| 2 | 루트 디렉터리 |
| 3 | 개인 디렉터리 "private-dir". 볼륨을 만들 때 반드시 만듦 |
| 6 | 스냅숏 메타데이터 디렉터리(`SNAP_DIR_INO_NUM`) |
| 7 | 제거 가능(purgeable) 파일을 참조하는 번호. 실제 디렉터리는 없음 |
| 16 | 사용자 콘텐츠가 쓰는 가장 작은 번호. 16 미만은 모두 예약 |

번호의 뜻은 위와 같고 [1], 실제 이미지에서 2번 디렉터리의 이름은 "root", 3번은 "private-dir" 입니다 [2]. 볼륨 그룹에서 System 볼륨이 쓰는 번호 범위는 [컨테이너와 볼륨 (Container·Volume)](container-volume.md)에 있습니다.

## 아이노드

아이노드 레코드의 값 `j_inode_val_t` 는 아래와 같습니다 [1][2].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 8 | `parent_id` | 부모 디렉터리 ID |
| 8 | 8 | `private_id` | 데이터 스트림 ID. 데이터가 없으면 자기 ID |
| 16 / 24 / 32 / 40 | 8씩 | `create_time` / `mod_time` / `change_time` / `access_time` | 시각 네 가지 |
| 48 | 8 | `internal_flags` | 아이노드 플래그 |
| 56 | 4 | `nchildren` / `nlink` | 디렉터리면 항목 수, 아니면 하드 링크 수 |
| 60 | 4 | `default_protection_class` | 기본 보호 등급 |
| 64 | 4 | `write_generation_counter` | 아이노드나 데이터가 바뀔 때마다 1 증가. 넘치면 0부터 |
| 68 | 4 | `bsd_flags` | chflags 플래그 |
| 72 | 4 | `owner` | UID |
| 76 | 4 | `group` | GID |
| 80 | 2 | `mode` | 파일 모드 |
| 82 | 2 | `pad1` | |
| 84 | 8 | `uncompressed_size` | 압축 전 크기(`INODE_HAS_UNCOMPRESSED_SIZE` 일 때만) |
| 92 | | `xfields` | 확장 필드 |

오프셋 84는 [2]에서 "pad2(Unknown)"이지만 [1]은 `uncompressed_size` 로 정의합니다. macOS 10.15 전에는 Apple 구현이 `INODE_HAS_UNCOMPRESSED_SIZE` 플래그를 무시하고 이 필드를 늘 패딩으로 다뤘습니다 [1].

`mode` 의 파일 형식은 `S_IFMT` (0170000)로 걸러 내고, S_IFIFO 0010000, S_IFCHR 0020000, S_IFDIR 0040000, S_IFBLK 0060000, S_IFREG 0100000, S_IFLNK 0120000, S_IFSOCK 0140000, S_IFWHT 0160000 가운데 하나입니다 [1].

`bsd_flags` 에는 `sys/stat.h` 의 chflags 값이 들어갑니다 [2].

| 사용자 플래그 | 값 | 시스템 플래그 | 값 |
|---|---|---|---|
| UF_NODUMP | 0x1 | SF_ARCHIVED | 0x10000 |
| UF_IMMUTABLE | 0x2 | SF_IMMUTABLE | 0x20000 |
| UF_APPEND | 0x4 | SF_APPEND | 0x40000 |
| UF_COMPRESSED | 0x20 | SF_RESTRICTED | 0x80000 |
| UF_TRACKED | 0x40 | SF_NOUNLINK | 0x100000 |
| UF_DATAVAULT | 0x80 | | |
| UF_HIDDEN | 0x8000 | | |

### 아이노드 플래그

`internal_flags` 의 값은 아래와 같습니다 [1].

| 플래그 | 값 | 뜻 |
|---|---|---|
| `INODE_IS_APFS_PRIVATE` | 0x1 | 구현 내부용. 파일 수 세기와 목록에서 숨김. Apple 구현은 임시 파일에 씀 |
| `INODE_MAINTAIN_DIR_STATS` | 0x2 | |
| `INODE_DIR_STATS_ORIGIN` | 0x4 | |
| `INODE_PROT_CLASS_EXPLICIT` | 0x8 | |
| `INODE_WAS_CLONED` | 0x10 | 복제로 만든 아이노드 |
| `INODE_HAS_SECURITY_EA` | 0x40 | ACL이 있음 |
| `INODE_BEING_TRUNCATED` | 0x80 | 파일을 자르던 중. 충돌 뒤 복구할 때 씀 |
| `INODE_HAS_FINDER_INFO` | 0x100 | |
| `INODE_IS_SPARSE` | 0x200 | 희소 파일 |
| `INODE_WAS_EVER_CLONED` | 0x400 | 한 번 이상 복제된 적 있음 |
| `INODE_HAS_RSRC_FORK` / `INODE_NO_RSRC_FORK` | 0x4000 / 0x8000 | 리소스 포크 유무 |
| `INODE_HAS_UNCOMPRESSED_SIZE` | 0x40000 | `uncompressed_size` 필드가 유효 |
| `INODE_IS_PURGEABLE` | 0x80000 | 다음 정리 때 지워질 파일 |
| `INODE_WANTS_TO_BE_PURGEABLE` | 0x100000 | |
| `INODE_IS_SYNC_ROOT` | 0x200000 | fileproviderd 동기화 계층의 뿌리 |
| `INODE_SNAPSHOT_COW_EXEMPTION` | 0x400000 | 스냅숏에 속한 데이터라도 copy-on-write를 하지 않음 |

복제·희소 플래그는 [복제·희소·압축 파일 (Clone·Sparse·Compression)](clone-sparse-compression.md)에서, 정리(purge) 대상 파일은 [지운 파일과 옛 체크포인트 (Deleted Files·Old Checkpoints)](deleted-files.md)에서 더 다룹니다. `INODE_IS_SYNC_ROOT` 가 켜진 디렉터리는 [파일 공급자 (File Provider)](../../../02-artifacts/cloud-apps/file-provider.md)와 이어 볼 수 있습니다.

## 디렉터리 항목

디렉터리 항목 레코드의 키 `j_drec_hashed_key_t` 는 부모 디렉터리 ID와 형식 9를 담은 머리, `name_len_and_hash` (uint32), 이름으로 되어 있고, `name_len_and_hash` 의 하위 10비트가 NULL을 포함한 이름 길이, 상위 22비트가 해시입니다 [1]. 해시는 이름을 NFD로 정규화하고 UTF-32로 바꿔 CRC-32C를 구한 뒤 비트를 뒤집어 하위 22비트를 취한 값입니다 [1]. 정규화 형태는 [유니코드 정규화 (NFD·NFC)](../../value-decoding/unicode-normalization.md)에서 설명합니다.

파일 이름은 디스크에 UTF-8로 저장하고 입력한 정규화 형태를 그대로 보존하며, `readdir(2)` 는 APFS에서 해시 순서로 이름을 돌려줍니다 [3]. HFS+는 이름을 UTF-16으로 저장했고 사전 순서로 돌려줬습니다 [3].

값 `j_drec_val_t` 는 대상 아이노드 번호 `file_id` (오프셋 0, 8바이트), 항목이 추가된 시각 `date_added` (8, 8), `flags` (16, 2), 확장 필드(18부터)로 되어 있습니다 [1][2]. `flags` 의 하위 4비트가 파일 형식이고, DT_UNKNOWN 0, DT_FIFO 1, DT_CHR 2, DT_DIR 4, DT_BLK 6, DT_REG 8, DT_LNK 10, DT_SOCK 12, DT_WHT 14 가운데 하나입니다 [1]. `date_added` 의 뜻은 시각 페이지에서 다룹니다.

## 확장 필드

아이노드와 디렉터리 항목 값의 끝에는 확장 필드가 붙고, `xf_blob_t` (`xf_num_exts`, `xf_used_data`) 뒤에 `x_field_t` (`x_type`, `x_flags`, `x_size`) 배열이 오고 그 뒤에 8바이트 경계로 맞춘 데이터가 이어집니다 [1].

| 아이노드 확장 필드 | 값 | 뜻 |
|---|---|---|
| SNAP_XID / DELTA_TREE_OID | 1 / 2 | |
| DOCUMENT_ID | 3 | uint32. 원자적 저장(atomic save)으로 파일이 바뀌어도 경로에 붙어 유지됨 |
| NAME | 4 | 하드 링크 이름 |
| PREV_FSIZE | 5 | 충돌 복구용 이전 크기 |
| FINDER_INFO | 7 | 32바이트 |
| DSTREAM | 8 | `j_dstream_t`. 파일 크기가 여기에 있음 |
| DIR_STATS_KEY | 10 | |
| FS_UUID | 11 | 이 디렉터리에 자동으로 마운트되는 볼륨의 UUID |
| SPARSE_BYTES / RDEV / PURGEABLE_FLAGS / ORIG_SYNC_ROOT_ID | 13 / 14 / 15 / 16 | |

파일 크기는 DSTREAM 확장 필드에 있습니다 [2]. 디렉터리 항목에는 하드 링크 전용 확장 필드 `DREC_EXT_TYPE_SIBLING_ID` (1)가 있습니다 [1]. 확장 필드 플래그 `XF_USER_FIELD` (0x10)는 사용자 공간 프로그램이 추가한 필드이고, `XF_SYSTEM_FIELD` (0x20)는 커널이나 시스템이 추가해서 사용자 공간에서 고칠 수 없는 필드입니다 [1].

## 데이터 스트림과 익스텐트

데이터 스트림 `j_dstream_t` (40바이트)는 `size`, `alloced_size`, `default_crypto_id`, `total_bytes_written`, `total_bytes_read` 로 되어 있고, 뒤의 두 필드는 쓰기·읽기 때마다 늘어나는 누적값이며 넘치면 0부터 다시 셉니다 [1].

파일 익스텐트 레코드의 키 `j_file_extent_key_t` 는 파일 객체 ID와 파일 안의 바이트 오프셋 `logical_addr` 이고, 값은 하위 56비트가 바이트 길이(블록 크기의 배수)인 `len_and_flags`, 물리 블록 번호 `phys_block_num`, `crypto_id` 입니다 [1]. 물리 익스텐트 레코드는 시작 블록 주소를 키로 쓰고, 값은 하위 60비트가 블록 수이고 상위 4비트가 종류(kind)인 `len_and_kind`, `owning_obj_id`, `refcnt` 이며, `refcnt` 가 0이 되면 그 익스텐트를 지울 수 있습니다 [1].

## 하드 링크

`SIBLING_LINK` 레코드는 아이노드 번호와 `sibling_id` 를 키로, 링크의 `parent_id` 와 이름을 값으로 담고, `SIBLING_MAP` 레코드는 `sibling_id` 를 키로, 대상 아이노드 `file_id` 를 값으로 담습니다 [1]. 이 구조대로라면 한 아이노드에 걸린 모든 이름과 부모 디렉터리를 SIBLING_LINK 레코드로 모두 찾을 수 있습니다.

하드 링크가 여럿인 아이노드의 `parent_id` 와 이름은 주 링크 (primary link)의 것이고, 주 링크는 형제 ID가 가장 작은 링크이며, 링크마다의 이름은 확장 필드 NAME에 있습니다 [1]. APFS는 디렉터리 하드 링크를 지원하지 않아서 HFS+에서 변환할 때 심볼릭 링크나 별칭(alias)으로 바뀝니다 [3].

## 읽는 법

### 헥스로 한 번

아래 바이트는 실제 데이터가 아니라 명세 [1]과 형식 문서 [2]에 맞춰 만든 아이노드 레코드이고, `xx` 는 값이 이미지마다 다른 자리입니다.

```
키
10 00 00 00 00 00 00 30

값 내 오프셋
0000  02 00 00 00 00 00 00 00 10 00 00 00 00 00 00 00
0010  xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx
0020  xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx
0030  00 00 00 00 00 00 00 00 01 00 00 00 xx xx xx xx
0040  xx xx xx xx 00 00 00 00 F5 01 00 00 14 00 00 00
0050  A4 81 00 00 ...
```

키를 리틀 엔디언으로 읽으면 0x3000000000000010이고, 상위 4비트 3은 INODE, 하위 60비트 0x10은 객체 ID 16, 곧 사용자 콘텐츠의 첫 번호입니다. 값의 `parent_id` 가 2라서 루트 디렉터리 바로 아래에 있고, `private_id` 가 자기 번호 16입니다. 0x30의 `internal_flags` 는 0이고, 0x38의 `nlink` 는 1입니다. 0x44의 `bsd_flags` 가 0이고, `owner` 는 0x1F5(501), `group` 은 0x14(20)이며, 0x50의 `mode` 0x81A4는 8진수 0100644, 곧 일반 파일(S_IFREG)에 권한 644입니다. 0x10~0x2F의 시각 네 필드는 시각 페이지에서 푸는 방법을 봅니다.

### 절차

1. 볼륨 객체 맵으로 `apfs_root_tree_oid` 를 찾아 파일 시스템 트리의 루트 노드를 읽습니다.
2. 객체 ID 2(루트 디렉터리)의 INODE 레코드를 찾고, 같은 객체 ID 아래의 DIR_REC 레코드로 자식 이름과 아이노드 번호를 모읍니다.
3. 자식마다 INODE 레코드의 `parent_id`, `owner`, `mode`, 플래그, 시각을 읽고, DSTREAM 확장 필드에서 크기를 읽습니다.
4. 파일이면 같은 객체 ID 아래의 FILE_EXTENT 레코드를 `logical_addr` 순서로 모아 데이터 블록을 찾습니다.
5. XATTR 레코드가 있으면 [확장 속성 (Extended Attributes)](extended-attributes.md)의 방법으로 풉니다.
6. `nlink` 가 1보다 크면 SIBLING_LINK 레코드로 다른 이름과 부모를 모두 모읍니다.
7. 부모 쪽으로 `parent_id` 를 따라 올라가 전체 경로를 짜 맞춥니다.

## 포렌식에서 중요한 점

`owner` 와 `group` 은 숫자 ID라서 사람 이름으로 바꾸려면 [사용자 계정 (Local Accounts)](../../../02-artifacts/system-account/user-accounts/index.md)의 UID와 맞춰 봅니다. 자식 아이노드의 `parent_id` 는 부모 디렉터리를, 부모 아래 디렉터리 항목의 `file_id` 는 자식 아이노드를 가리킵니다 [1]. 그래서 둘 가운데 한쪽 레코드만 옛 노드에서 되살려도 다른 쪽을 찾을 단서가 될 수 있습니다.

`write_generation_counter` 는 아이노드나 데이터가 바뀔 때마다 늘어나고 [1], `total_bytes_written`·`total_bytes_read` 는 쓰기·읽기 누적량입니다 [1]. 이 값들은 시각이 아니라 횟수와 양이라서 언제 바뀌었는지는 알려 주지 않습니다. 이 카운터를 포렌식에 쓴 공개 연구는 없으므로, 분석에 쓰려면 실제 데이터로 확인해야 합니다.

`INODE_IS_APFS_PRIVATE` 가 켜진 아이노드는 파일 수 세기와 목록에서 숨겨지고 [1], afro가 뽑아낸 결과에는 볼륨마다 사용자에게 보이지 않는 `private-dir` 과 `root` 폴더가 나옵니다 [4]. 운영체제의 파일 목록과 트리를 직접 읽은 결과가 다르다면 이런 숨긴 항목부터 확인합니다.

`INODE_BEING_TRUNCATED` 는 파일을 자르던 중이라는 표시이고 확장 필드 PREV_FSIZE와 함께 충돌 뒤 복구에 씁니다 [1]. 이 플래그가 켜진 채 남은 아이노드는 자르기가 끝나기 전에 멈췄을 가능성이 있어서 비정상 종료 흔적과 함께 봅니다. DOCUMENT_ID는 원자적 저장으로 파일이 바뀌어도 경로에 붙어 유지되어서 [1], 여러 번 저장한 문서를 같은 문서로 이어 볼 단서가 됩니다.

## 함정

[1]의 PDF 텍스트에서 아이노드 플래그 목록은 이름과 값이 한 줄씩 어긋나 보입니다. 값은 항목별 설명에 적힌 쪽을 기준으로 삼고, 상수를 옮겨 적을 때도 항목별 설명과 맞춰 봅니다.

디렉터리에서 오프셋 56의 값은 하드 링크 수가 아니라 항목 수인데, macOS의 `stat` 은 이 값을 nlink처럼 다룹니다 [2]. 도구가 보여 주는 링크 수를 그대로 옮기기 전에 대상이 디렉터리인지 확인합니다.

`readdir(2)` 는 APFS에서 해시 순서로 이름을 돌려주므로 [3], 도구가 보여 주는 목록 순서를 만든 순서나 사전 순서로 읽으면 안 됩니다. 이름은 입력한 정규화 형태 그대로 저장하는데 [3], 같은 글자로 보이는 두 이름이 NFC와 NFD처럼 바이트로는 다를 수 있다는 점도 기억해 둡니다.

## 도구

mac_apt는 HFS와 APFS 파서를 자체 구현한 공개 도구이고 [5], afro는 APFS를 파싱해 볼륨마다 파일 시스템을 폴더로 뽑아내며 mactime 타임라인용 body file도 만듭니다 [4]. afro는 지금 유지보수하지 않는 도구라서 [4] 결과를 다른 도구와 헥스로 맞춰 봅니다.

## 참고 문헌

1. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
2. Joachim Metz, libfsapfs — Apple File System (APFS) 형식 문서 (개정 0.0.18, 2026년 8월) — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
3. Apple, Apple File System Guide — Frequently Asked Questions (보관 문서, 2018-06-04) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html
4. afro (APFS file recovery) README, Jonas Plum — https://raw.githubusercontent.com/cugu/afro/master/README.md
5. mac_apt README, Yogesh Khatri (v1.33.2) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/README.md
