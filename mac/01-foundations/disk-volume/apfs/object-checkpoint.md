---
title: "객체와 체크포인트"
parent: "APFS 구조"
grand_parent: "기반 · 디스크·볼륨"
nav_order: 20
---

# 객체와 체크포인트 (Object·Checkpoint)

APFS 컨테이너 층의 객체는 모두 32바이트 객체 헤더로 시작하고 물리·가상·임시 세 방식 가운데 하나로 저장되며, 디스크의 객체를 제자리에서 고치지 않고 고친 사본을 늘 새 위치에 쓰는 데다 [1] 체크포인트 영역이 링 버퍼로 돌아가서, 한 컨테이너 안에 같은 객체의 여러 시점 사본이 함께 남을 수 있습니다.

컨테이너와 볼륨 슈퍼블록의 칸은 [컨테이너와 볼륨 (Container·Volume)](container-volume.md)에, 파일 시스템 층의 레코드는 [파일 시스템 트리와 아이노드 (FS Tree·Inode)](fs-tree-inode.md)에 있고, 이 페이지는 그 둘을 잇는 객체 헤더, 체크포인트, 객체 맵 (object map), B-트리 노드를 다룹니다.

## 이 구조를 쓰는 곳

컨테이너 슈퍼블록, 볼륨 슈퍼블록, 객체 맵, 공간 관리자, 리퍼, 체크포인트 맵, 모든 B-트리 노드가 같은 객체 헤더로 시작합니다 [1]. 파일 시스템 트리도 B-트리라서 파일 하나를 찾으려면 이 페이지의 객체 맵과 B-트리 노드를 거쳐야 하고, 삭제 흔적을 찾을 때도 옛 체크포인트와 옛 노드 사본을 이 구조로 읽습니다.

## 객체 헤더

`obj_phys_t` 는 32바이트이고 칸은 아래와 같습니다 [1][2].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 8 | `o_cksum` | Fletcher-64 체크섬 |
| 8 | 8 | `o_oid` | 객체 ID |
| 16 | 8 | `o_xid` | 이 객체를 마지막으로 고친 트랜잭션 ID |
| 24 | 4 | `o_type` | 하위 16비트는 형식, 상위 16비트는 플래그 |
| 28 | 4 | `o_subtype` | 하위 형식(예: B-트리 노드가 담은 데이터의 종류) |

체크섬은 블록에서 체크섬 칸 8바이트를 뺀 나머지로 초깃값 0에서 Fletcher-64를 계산합니다 [2]. 합계 두 개를 구한 뒤 낮은 32비트는 0xffffffff에서 (하위합 + 상위합) mod 0xffffffff를 뺀 값이고, 높은 32비트는 0xffffffff에서 (하위합 + 낮은 32비트) mod 0xffffffff를 뺀 값입니다 [2]. 새 객체를 쓸 때 블록의 빈 곳은 0으로 채웁니다 [1].

## 저장 방식 세 가지

객체는 아래 세 방식 가운데 하나로 저장됩니다 [1].

| 방식 | 찾는 법 | 고치면 | 형식 플래그 |
|---|---|---|---|
| 물리 (physical) | 객체 ID가 곧 블록 주소 | 새 위치에 쓰므로 ID가 바뀜 | `OBJ_PHYSICAL` 0x40000000 |
| 가상 (virtual) | 객체 맵에서 위치를 찾음 | 원본과 사본의 ID가 같아서 트랜잭션 ID로 구별함 | 없음(`OBJ_VIRTUAL` = 0) |
| 임시 (ephemeral) | 마운트 중에는 메모리에, 언마운트 상태에서는 체크포인트에 있음 | 메모리에서는 제자리에서 고치지만 디스크에는 늘 새 체크포인트로 씀 | `OBJ_EPHEMERAL` 0x80000000 |

임시 객체는 공간 관리자나 리퍼처럼 자주 바뀌는 정보에 씁니다 [1]. 이 밖에 헤더가 없는 객체(예: 공간 관리자 비트맵)를 뜻하는 `OBJ_NOHEADER` 0x20000000, `OBJ_ENCRYPTED` 0x10000000, 디스크에 나오면 안 되는 `OBJ_NONPERSISTENT` 0x08000000 플래그가 있습니다 [1].

객체 ID는 같은 저장 방식 안에서 컨테이너 전체에 하나뿐이고, 새 가상·임시 객체 ID는 컨테이너 슈퍼블록의 `nx_next_oid` 에서 가져오며 계속 커져야 합니다 [1]. 1024 미만(`OID_RESERVED_COUNT`)은 예약 번호이고, 지금 예약 ID를 쓰는 객체는 컨테이너 슈퍼블록(`OID_NX_SUPERBLOCK` = 1)뿐입니다 [1].

트랜잭션 ID(xid)는 계속 커지는 번호이고, 0은 디스크에 나오면 안 되며 1부터 다시 세거나 재사용하는 일도 허용되지 않습니다 [1]. 그래서 같은 객체의 여러 사본은 xid로 앞뒤를 정할 수 있습니다.

## 객체 형식 값

`o_type & 0xffff` 로 얻는 형식 값 가운데 자주 보는 것은 아래와 같습니다 [1].

| 값 | 이름 | 값 | 이름 |
|---|---|---|---|
| 0x01 | NX_SUPERBLOCK | 0x0f | BLOCKREFTREE |
| 0x02 | BTREE | 0x10 | SNAPMETATREE |
| 0x03 | BTREE_NODE | 0x11 | NX_REAPER |
| 0x05 | SPACEMAN | 0x12 | NX_REAP_LIST |
| 0x06 | SPACEMAN_CAB | 0x13 | OMAP_SNAPSHOT |
| 0x07 | SPACEMAN_CIB | 0x14 | EFI_JUMPSTART |
| 0x08 | SPACEMAN_BITMAP | 0x15 | FUSION_MIDDLE_TREE |
| 0x09 | SPACEMAN_FREE_QUEUE | 0x18 | ER_STATE |
| 0x0a | EXTENT_LIST_TREE | 0x1d | SNAP_META_EXT |
| 0x0b | OMAP | 0x1e | INTEGRITY_META |
| 0x0c | CHECKPOINT_MAP | 0x1f | FEXT_TREE |
| 0x0d | FS(볼륨 슈퍼블록) | | |
| 0x0e | FSTREE | | |

키백은 따로 형식 값 'keys'(컨테이너), 'recs'(볼륨), 'mkey'(미디어)를 씁니다 [1]. 플래그까지 합친 32비트 값으로 보면 컨테이너 슈퍼블록은 0x80000001, 체크포인트 맵은 0x4000000c입니다 [2].

## 체크포인트

체크포인트는 두 영역에 나뉘어 있습니다 [1]. 체크포인트 서술자 영역 (checkpoint descriptor area)에는 체크포인트 맵 `checkpoint_map_phys_t` 와 컨테이너 슈퍼블록이 들어 있고, 체크포인트 데이터 영역 (checkpoint data area)에는 체크포인트를 쓴 시점의 메모리 상태, 곧 임시 객체가 들어 있습니다 [1].

메모리 상태를 주기적으로 체크포인트로 쓰고 그 뒤에 그 시점의 컨테이너 슈퍼블록 사본을 쓰며, 쓰다가 멈춘 체크포인트는 무효라서 다음 마운트 때 무시되고 마지막 유효 상태로 돌아갑니다 [1]. 서술자 영역은 배열로 저장한 링 버퍼라서, 최신 슈퍼블록에서 거꾸로 읽다 보면 영역의 첫 블록에서 마지막 블록으로 넘어갈 때가 있습니다 [1].

체크포인트 영역의 위치는 컨테이너 슈퍼블록의 아래 칸에 적혀 있습니다 [1][2].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 104 / 108 | 4씩 | `nx_xp_desc_blocks` / `nx_xp_data_blocks` | 영역의 블록 수. 최상위 비트는 플래그 |
| 112 / 120 | 8씩 | `nx_xp_desc_base` / `nx_xp_data_base` | 영역의 첫 블록 주소, 또는 조각 위치를 담은 B-트리 |
| 128 / 132 | 4씩 | `nx_xp_desc_next` / `nx_xp_data_next` | 다음에 쓸 자리 |
| 136 / 140 | 4씩 | `nx_xp_desc_index` / `nx_xp_desc_len` | 이 슈퍼블록이 속한 체크포인트의 서술자 시작 자리와 블록 수 |
| 144 / 148 | 4씩 | `nx_xp_data_index` / `nx_xp_data_len` | 같은 체크포인트의 데이터 시작 자리와 블록 수 |

블록 수 칸의 최상위 비트가 0이면 영역이 연속이고 base가 첫 블록 주소이지만, 1이면 영역이 연속이 아니고 base는 조각 위치를 담은 B-트리의 물리 객체 ID입니다 [1]. 블록 0에 있는 슈퍼블록 사본에서는 next·index·len 값에 뜻이 없습니다 [1].

체크포인트 맵은 헤더 `cpm_o` 뒤에 `cpm_flags`(32), `cpm_count`(36), 매핑 배열 `cpm_map[]`(40부터)이 이어지는 구조입니다 [1][2]. 매핑 하나 `checkpoint_mapping_t` 는 40바이트이고 `cpm_type`, `cpm_subtype`, `cpm_size`, `cpm_pad`, 관련 볼륨의 가상 ID `cpm_fs_oid`, 임시 객체 ID `cpm_oid`, 데이터 영역 안의 주소 `cpm_paddr` 로 되어 있습니다 [1][2]. 매핑이 한 블록에 다 들어가지 않으면 여러 블록을 연속으로 쓰고 마지막 블록에만 `CHECKPOINT_MAP_LAST` (0x1)를 켭니다 [1]. 이 객체의 크기는 4080바이트이고 매핑은 최대 101개입니다 [2].

컨테이너를 새로 만들 때 데이터 영역에 체크포인트가 적어도 4개(`NX_TX_MIN_CHECKPOINT_COUNT`) 들어가게 크기를 정합니다 [1]. 실제 이미지에 옛 체크포인트가 몇 개까지 남는지는 공개 자료가 없어 검체에서 확인합니다.

## 객체 맵

객체 맵 `omap_phys_t` 는 가상 객체 ID를 물리 주소로 바꿔 주는 B-트리이고, 컨테이너에 하나, 볼륨마다 하나씩 있습니다 [1]. 필드는 `om_flags`, 스냅숏 수 `om_snap_count`, 매핑 트리 `om_tree_oid`, 스냅숏 트리 `om_snapshot_tree_oid`, 가장 최근 스냅숏의 xid `om_most_recent_snap`, `om_pending_revert_min`·`om_pending_revert_max` 입니다 [1].

매핑 트리의 키 `omap_key_t` 는 (`ok_oid`, `ok_xid`)이고 값 `omap_val_t` 는 (`ov_flags`, `ov_size`, `ov_paddr`)이며, 트리는 객체 ID로 먼저 정렬하고 그다음 트랜잭션 ID로 정렬합니다 [1]. 그래서 같은 가상 객체의 여러 시점 매핑이 트리 안에서 나란히 놓이고, 가상 객체를 찾을 때는 트랜잭션 ID로 어느 시점의 사본인지 정합니다 [1].

| 값 플래그 | 값 | 뜻 |
|---|---|---|
| `OMAP_VAL_DELETED` | 0x1 | 객체가 지워졌고 이 매핑은 자리표시 |
| `OMAP_VAL_ENCRYPTED` | 0x4 | |
| `OMAP_VAL_NOHEADER` | 0x8 | |
| `OMAP_VAL_CRYPTO_GENERATION` | 0x10 | |

| 객체 맵 플래그 | 값 |
|---|---|
| `OMAP_MANUALLY_MANAGED` | 0x1 |
| `OMAP_ENCRYPTING` | 0x2 |
| `OMAP_DECRYPTING` | 0x4 |
| `OMAP_KEYROLLING` | 0x8 |
| `OMAP_CRYPTO_GENERATION` | 0x10 |

컨테이너 객체 맵에는 스냅숏을 지원하지 않는다는 뜻의 `OMAP_MANUALLY_MANAGED` 가 반드시 켜져 있고, 볼륨 객체 맵에는 이 플래그를 켜면 안 됩니다 [1]. 볼륨 객체 맵의 스냅숏 트리는 [스냅숏 (Snapshots)](snapshots.md)에서 다룹니다.

## B-트리 노드

APFS의 모든 트리는 같은 노드 구조 `btree_node_phys_t` 를 쓰고, 블록 하나 안에 노드 정보, 목차 (table of contents, TOC), 키 영역, 값 영역이 들어가며 루트 노드에만 끝에 `btree_info_t` 가 붙습니다 [1]. 기본 노드 크기는 4096바이트(`BTREE_NODE_SIZE_DEFAULT`)입니다 [1].

노드에는 부모나 형제를 가리키는 포인터가 없어서 탐색은 늘 루트에서 시작하고, 값은 잎 노드에만 있으며 잎이 아닌 노드의 값은 자식 노드의 객체 ID입니다(B+ 트리) [1]. 키와 값은 영역의 양 끝에서 서로를 향해 자라고, 항목을 지워서 생긴 빈 곳은 키 영역과 값 영역 안의 free list로 관리합니다 [1]. 지운 항목의 바이트를 0으로 지우는지 그대로 두는지는 명세에 정해져 있지 않아 검체에서 확인합니다.

| 노드 플래그 | 값 |
|---|---|
| `BTNODE_ROOT` | 0x1 |
| `BTNODE_LEAF` | 0x2 |
| `BTNODE_FIXED_KV_SIZE` | 0x4 |
| `BTNODE_HASHED` | 0x8 |
| `BTNODE_NOHEADER` | 0x10 |

트리 플래그 `BTREE_ALLOW_GHOSTS` (0x4)는 값 없는 키를 허용한다는 뜻이고, 이런 키는 문맥에 따라 지워져서 무시할 키일 수도, 값이 뻔해서 값을 생략한 키일 수도 있습니다 [1].

## 읽는 법

### 마운트 순서

APFS의 마운트 순서가 그대로 이미지를 손으로 읽는 순서입니다 [1].

1. 블록 0을 읽습니다.
2. `nx_xp_desc_base` 로 체크포인트 서술자 영역을 찾습니다.
3. 영역 안의 컨테이너 슈퍼블록 가운데 매직과 체크섬이 맞고 xid가 가장 큰 것을 고릅니다.
4. 그 체크포인트의 임시 객체를 읽고, 하나라도 깨졌으면 더 옛 체크포인트로 마운트합니다.
5. `nx_omap_oid` 로 컨테이너 객체 맵을 찾습니다.
6. `nx_fs_oid` 의 볼륨 ID를 컨테이너 객체 맵에서 찾아 볼륨 슈퍼블록을 읽습니다.
7. 볼륨 슈퍼블록의 `apfs_omap_oid` 와 `apfs_root_tree_oid` 로 파일 시스템 트리를 찾습니다.

### 헥스로 한 번

아래 바이트는 실제 검체가 아니라 명세 [1]과 형식 문서 [2]에 맞춰 만든 체크포인트 맵 블록의 앞부분이고, `xx` 는 값이 검체마다 다른 자리입니다.

```
블록 내 오프셋
0000  xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx
0010  xx xx xx xx xx xx xx xx 0C 00 00 40 00 00 00 00
0020  01 00 00 00 02 00 00 00 ...
```

0x18의 `0C 00 00 40` 은 리틀 엔디언으로 0x4000000c, 곧 물리 객체인 체크포인트 맵입니다 [2]. 0x20의 `01 00 00 00` 은 `CHECKPOINT_MAP_LAST` 가 켜진 마지막 맵 블록이라는 뜻이고, 0x24의 `02 00 00 00` 은 매핑이 두 개라는 뜻이라서 0x28부터 40바이트짜리 매핑 두 개를 읽습니다. 매핑마다 `cpm_paddr` 가 가리키는 데이터 영역 블록에 공간 관리자나 리퍼 같은 임시 객체가 있습니다.

## 포렌식에서 중요한 점

체크포인트 서술자 영역은 링 버퍼라서 최신 체크포인트 앞에 옛 컨테이너 슈퍼블록과 옛 체크포인트 맵이 남아 있을 수 있고 [1][2], 슈퍼블록 사본마다 과거 한 시점의 컨테이너 상태가 담겨 있습니다 [1]. 이 옛 상태를 따라가 지운 파일을 찾는 방법은 [지운 파일과 옛 체크포인트 (Deleted Files·Old Checkpoints)](deleted-files.md)에서 다룹니다.

비정상 종료로 체크포인트를 쓰다가 멈췄다면 다음 마운트는 마지막 유효 체크포인트로 돌아갑니다 [1]. 그래서 멈추기 직전의 변경은 마운트한 상태에 보이지 않고 무효 체크포인트 쪽에만 남을 수 있습니다. 마운트 순서의 3단계대로 매직이나 체크섬이 맞지 않는 슈퍼블록은 최신 사본으로 고르지 않습니다 [1].

xid는 재사용하지 않는 번호라서 [1], 서로 다른 블록에서 찾은 같은 객체의 사본을 시간 순서로 늘어놓는 기준이 됩니다. 다만 xid는 순서만 알려 주고 벽시계 시각은 아니어서, 시각이 필요하면 [APFS의 시각 네 가지 (Create·Modify·Change·Access)](timestamps.md)의 시각 칸과 맞춰 봅니다.

## 함정

[1]의 PDF에서 텍스트를 뽑으면 객체 맵 플래그 표의 이름과 값이 어긋나 `OMAP_MANUALLY_MANAGED` 가 0x4처럼 보입니다. 항목별 설명에 적힌 값은 0x1입니다. PDF를 텍스트로 바꿔 상수를 옮겨 적을 때는 항목별 설명과 한 번 더 맞춰 봅니다.

서술자 영역을 거꾸로 읽을 때 영역 끝으로 넘어가는 경우를 빠뜨리면 옛 슈퍼블록 일부를 놓치고, 블록 수 칸의 최상위 비트가 켜진 영역을 연속 영역으로 읽으면 엉뚱한 블록을 읽게 됩니다 [1].

블록 0의 슈퍼블록 사본에서 next·index·len 칸을 읽어 체크포인트 위치를 정하면 틀립니다 [1]. 블록 0 사본은 서술자 영역을 찾는 데에만 쓰고, 나머지는 영역 안에서 고른 최신 슈퍼블록에서 읽습니다.

## 도구

mac_apt는 HFS와 APFS 파서를 자체 구현한 공개 도구입니다 [3]. 체크포인트 영역과 객체 맵을 직접 확인할 때는 형식 문서 [2]의 오프셋 표를 기준으로 헥스 편집기에서 따라가고, 도구가 고른 최신 슈퍼블록의 xid가 손으로 고른 값과 같은지 맞춰 봅니다.

## 참고 문헌

1. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
2. Joachim Metz, libfsapfs — Apple File System (APFS) 형식 문서 (개정 0.0.18, 2026년 8월) — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
3. mac_apt README, Yogesh Khatri (v1.33.2) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/README.md
