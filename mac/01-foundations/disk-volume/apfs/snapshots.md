---
title: "스냅숏"
parent: "APFS 구조"
grand_parent: "기반 · 디스크·볼륨"
nav_order: 60
---

# 스냅숏 (Snapshots)

스냅숏 (snapshot)은 한 시점의 파일 시스템을 안정된 읽기 전용 사본으로 잡아 둔 것이고 [1], macOS는 시스템 볼륨 부팅과 Time Machine 로컬 스냅숏에 이 기능을 써서 [3][5] 이미지 한 장에 확보 시점보다 앞선 볼륨 상태가 함께 들어 있을 수 있습니다.

볼륨 객체 맵과 가상 객체를 찾는 규칙은 [객체와 체크포인트 (Object·Checkpoint)](object-checkpoint.md)에, 볼륨 슈퍼블록의 필드 위치는 [컨테이너와 볼륨 (Container·Volume)](container-volume.md)에 있고, 이 페이지는 스냅숏 메타데이터와 macOS가 스냅숏을 쓰는 방식만 다룹니다.

## 이 구조를 쓰는 곳

macOS 11 이상은 시스템 볼륨을 스냅숏으로 잡고 부팅도 그 스냅숏에서 합니다 [3]. 서명된 시스템 볼륨 (signed system volume, SSV)도 APFS 스냅숏을 써서, 업데이트가 실패하면 다시 설치하지 않고 옛 시스템으로 돌아갈 수 있습니다 [4].

Time Machine은 시동 디스크의 스냅숏을 대략 한 시간마다 하나씩 저장해 24시간 보관하고, 마지막으로 성공한 백업의 스냅숏 하나는 공간이 필요해질 때까지 따로 남겨 둡니다 [5]. 로컬 스냅숏은 여유 공간이 넉넉한 디스크에만 저장하고, 오래되거나 공간이 필요해지면 자동으로 지워지며, 스냅숏이 차지한 공간은 "사용 가능"한 공간으로 셉니다 [5]. Time Machine 백업을 담는 볼륨은 역할 값 `APFS_VOL_ROLE_BACKUP` 으로 구별하고 [1], 백업 자체는 [타임 머신 (Time Machine)](../../../02-artifacts/filesystem/time-machine/index.md)에서 다룹니다.

| macOS | 스냅숏과 관련해 달라진 점 |
|---|---|
| 10.13 High Sierra 이상 | macOS 업데이트를 설치하기 전에 로컬 스냅숏을 하나 더 저장 [5] |
| 10.15 Catalina | 볼륨 슈퍼블록에 확장 메타데이터 위치 `apfs_snap_meta_ext_oid` 추가 [1] |
| 11 Big Sur 이상 | 시스템 볼륨을 스냅숏으로 잡고 그 스냅숏에서 부팅. SSV가 스냅숏을 씀 [3][4] |
| 13 Ventura 이상 | 로컬 스냅숏을 손으로 지우려면 백업 빈도를 "수동"으로 바꿈. 그 전 버전은 자동 백업을 잠시 끔 [5] |

## 구조

### 스냅숏 메타데이터 트리

볼륨 슈퍼블록의 `apfs_snap_meta_tree_oid` 가 스냅숏 메타데이터 트리를 가리키고, 이 트리에는 `APFS_TYPE_SNAP_METADATA` 레코드와 `APFS_TYPE_SNAP_NAME` 레코드가 들어 있습니다 [1]. 스냅숏은 만들기는 빠르고 싸지만 지우는 데는 일이 더 듭니다 [1].

메타데이터 레코드의 키 `j_snap_metadata_key_t` 는 객체 ID 자리에 스냅숏의 트랜잭션 ID(xid)를 넣습니다 [1]. 값 `j_snap_metadata_val_t` 는 아래와 같습니다 [1][2].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 8 | `extentref_tree_oid` | 스냅숏의 익스텐트 참조 트리(물리 객체) |
| 8 | 8 | `sblock_oid` | 스냅숏 시점의 볼륨 슈퍼블록(물리 객체) |
| 16 | 8 | `create_time` | 스냅숏을 만든 시각(1970 UTC 기준 나노초) |
| 24 | 8 | `change_time` | 스냅숏을 마지막으로 고친 시각(같은 단위) |
| 32 | 8 | `inum` | 공개된 설명 없음 |
| 40 | 4 | `extentref_tree_type` | 익스텐트 참조 트리의 형식 |
| 44 | 4 | `flags` | `SNAP_META_PENDING_DATALESS` 0x1, `SNAP_META_MERGE_IN_PROGRESS` 0x2 |
| 48 | 2 | `name_len` | 이름 길이. 끝의 NULL을 포함 |
| 50 | `name_len` | `name` | UTF-8 이름 |

이름 레코드의 키 `j_snap_name_key_t` 는 객체 ID가 늘 ~0(0xffffffffffffffff)이라서 이름으로 찾고, 값 `snap_xid` 는 그 스냅숏에 들어간 마지막 트랜잭션 ID입니다 [1]. 시각 필드의 단위와 읽는 법은 [APFS의 시각 네 가지 (Create·Modify·Change·Access)](timestamps.md)와 같습니다.

### 스냅숏을 만들 때 바뀌는 것

스냅숏을 만들면 볼륨의 현재 익스텐트 참조 트리가 스냅숏 쪽으로 옮겨 가고, 볼륨에는 빈 트리가 새로 생깁니다 [1]. 물리 익스텐트의 종류(kind)는 어느 스냅숏에도 속하지 않은 데이터를 추가한 `APFS_KIND_NEW` (1)와 기존 스냅숏에 속한 데이터를 바꾼 `APFS_KIND_UPDATE` (2)로 나뉘고, 스냅숏이 없는 볼륨에서는 늘 NEW입니다 [1].

### 볼륨 객체 맵 쪽 기록

볼륨 객체 맵에는 스냅숏 수 `om_snap_count`, 가장 최근 스냅숏의 xid `om_most_recent_snap`, 스냅숏 트리 `om_snapshot_tree_oid` 가 있고, 스냅숏 트리는 xid를 키로, `omap_snapshot_t` 를 값으로 씁니다 [1]. 값의 플래그 가운데 `OMAP_SNAPSHOT_DELETED` (0x1)는 지워진 스냅숏, `OMAP_SNAPSHOT_REVERTED` (0x2)는 되돌리기 과정에서 지워진 스냅숏을 뜻합니다 [1]. 볼륨 슈퍼블록에도 스냅숏 수를 적는 `apfs_num_snapshots` 필드가 있습니다 [1].

### 확장 메타데이터

macOS 10.15에서 추가된 `snap_meta_ext_t` 는 `apfs_snap_meta_ext_oid` 로 찾고, `sme_version`, `sme_flags`, `sme_snap_xid`, 스냅숏 UUID `sme_uuid`, `sme_token` 으로 되어 있습니다 [1].

### 되돌리기와 스냅숏에서 시작하기

볼륨 슈퍼블록의 `apfs_revert_to_xid` 가 0이 아니면 다음 마운트 때 그 스냅숏으로 되돌리고, 그보다 뒤의 스냅숏들과 현재 상태를 지운 다음 이 필드를 0으로 만듭니다 [1]. `apfs_root_to_xid` 가 0이 아니면 그 xid의 스냅숏에서 루트로 시작합니다 [1]. 스냅숏에 딸린 볼륨 슈퍼블록은 객체 형식 값이 물리 객체를 뜻하는 0x4000000d이고, 보통 볼륨 슈퍼블록의 0x0000000d와 구별됩니다 [2].

## 읽는 법

### 헥스로 한 번

아래 바이트는 실제 데이터가 아니라 명세 [1][2]의 정의에 맞춰 만든 예시입니다. `j_snap_metadata_val_t` 의 오프셋 16부터와 44부터가 아래와 같다고 합시다.

```
값 내 오프셋
0010  00 00 8C 3D BC 84 28 18 00 A0 44 6E 02 88 28 18
0020  .. .. .. .. .. .. .. .. .. .. .. .. 00 00 00 00
0030  07 00 73 6E 61 70 2D 61 00                        "..snap-a."
```

오프셋 16의 8바이트를 리틀 엔디언으로 읽으면 0x182884BC3D8C0000 = 1740787200000000000이고, 10^9로 나누면 1740787200초라서 `create_time` 은 2025-03-01 00:00:00 UTC입니다. 오프셋 24의 `change_time` 은 같은 방법으로 1740790800초, 곧 2025-03-01 01:00:00 UTC입니다. 오프셋 44의 `flags` 는 0이라서 데이터 없는 스냅숏 대기나 병합 중 표시가 없고, 오프셋 48의 `07 00` 은 이름 길이 7이라서 오프셋 50부터 `snap-a` 와 끝의 NULL이 이어집니다. 예시 이름은 설명을 위해 붙인 것이고, 실제 macOS가 쓰는 스냅숏 이름은 실제 데이터로 확인해야 합니다.

### 절차

1. 볼륨 슈퍼블록에서 `apfs_num_snapshots`, `apfs_snap_meta_tree_oid`, `apfs_revert_to_xid`, `apfs_root_to_xid` 를 읽어 둡니다.
2. 스냅숏 메타데이터 트리에서 이름 레코드를 모두 읽어 이름과 `snap_xid` 의 목록을 만듭니다.
3. 각 xid로 메타데이터 레코드를 찾아 `create_time`, `change_time`, `flags`, `sblock_oid` 를 적습니다.
4. `sblock_oid` 가 가리키는 볼륨 슈퍼블록을 읽고, 거기서 파일 시스템 트리를 찾아 들어갑니다. 가상 객체는 트랜잭션 ID로 어느 시점의 사본인지 정하므로 [1], 객체 맵에서 스냅숏의 xid에 해당하는 사본을 고릅니다.
5. 볼륨 객체 맵의 스냅숏 트리에서 `OMAP_SNAPSHOT_DELETED` 나 `OMAP_SNAPSHOT_REVERTED` 가 켜진 항목이 있는지 따로 적습니다.
6. 스냅숏 안의 파일과 현재 파일을 나란히 놓고 비교합니다. 비교 방법은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md)에 있습니다.

## 포렌식에서 중요한 점

스냅숏은 만든 시점의 파일 시스템 트리와 데이터를 가리키므로, 그 뒤에 지우거나 바꾼 파일이 스냅숏 안에는 남아 있을 수 있습니다 [1][5]. 지운 파일을 찾는 다른 방법은 [지운 파일과 옛 체크포인트 (Deleted Files·Old Checkpoints)](deleted-files.md)에서 다룹니다. 스냅숏 메타데이터의 `create_time` 은 그 스냅숏이 만들어진 시각이라서 [1], 스냅숏 안에서 찾은 파일이 적어도 그 시각에는 있었다는 기준점이 됩니다.

로컬 스냅숏은 오래되거나 공간이 필요하면 저절로 지워지고, 자동 백업을 끄거나 백업 빈도를 "수동"으로 바꾸면 몇 분 안에 지워집니다 [5]. 그래서 스냅숏이 없다는 사실만으로 누군가 일부러 지웠다고 보지 않고, Time Machine 설정이 "수동"으로 바뀐 흔적이 있으면 로컬 스냅숏이 사라진 이유로 함께 적습니다. 설정 흔적을 찾는 방법은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

아이노드 플래그 `INODE_SNAPSHOT_COW_EXEMPTION` 이 켜진 파일은 스냅숏에 속한 데이터라도 copy-on-write를 하지 않습니다 [1]. 그래서 그런 파일은 스냅숏 안에서 읽은 내용이 스냅숏 시점의 내용과 다를 수 있습니다.

`apfs_revert_to_xid` 가 0이 아닌 볼륨은 마운트할 때 그 스냅숏으로 되돌아가고 그보다 뒤의 스냅숏과 현재 상태가 지워지므로 [1], 분석 장비에서 이런 볼륨을 운영체제가 마운트하게 두지 않습니다. 확보는 읽기 전용 이미지로 하고, 방법은 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)를 따릅니다.

## 함정

[1]에 적힌 `apfs_snap_meta_tree_type` 의 전형 값 "OBJ_PHYSICAL | BTREE, 하위 형식 BLOCKREF"는 익스텐트 참조 트리 설명을 옮겨 적은 것으로 보이므로, 실제 값은 이미지에서 직접 확인해야 합니다. [2]의 스냅숏 절은 아직 "TODO"로 비어 있어서 스냅숏 구조는 [1]로 읽어야 합니다.

볼륨 기능 플래그 `APFS_INCOMPAT_DATALESS_SNAPS` (0x2)는 데이터 없는 스냅숏이 하나 이상 있다는 표시이고 [1], 이런 스냅숏에 무엇이 남는지는 실제 데이터로 확인해야 합니다. 데이터 없는 스냅숏에서 파일 내용을 읽지 못해도 도구 오류로 단정하지 않습니다.

xid는 순서만 알려 주는 번호이고 실제 시각이 아니므로, 스냅숏이 언제 만들어졌는지는 `create_time` 으로 적습니다. 스냅숏이 차지한 공간은 "사용 가능"으로 세기 때문에 [5], 사용자 화면의 여유 공간만 보고 스냅숏이 없다고 판단하지 않습니다.

## 도구

mac_apt README에는 스냅숏을 읽는다는 언급이 없습니다 [6]. 어떤 도구를 쓰든 스냅숏 안의 파일을 따로 읽는지 먼저 확인하고, 도구가 보여 주는 스냅숏 수를 볼륨 슈퍼블록의 `apfs_num_snapshots` 와 맞춰 봅니다.

## 참고 문헌

1. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
2. Joachim Metz, libfsapfs — Apple File System (APFS) 형식 문서 (개정 0.0.18, 2026년 8월) — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
3. Apple Platform Security — Role of Apple File System (게시 2024-12-19) — https://support.apple.com/guide/security/role-of-apple-file-system-seca6147599e/web
4. Apple Platform Security — Signed system volume security (게시 2022-05-13) — https://support.apple.com/guide/security/signed-system-volume-security-secd698747c9/web
5. Apple Support, About Time Machine local snapshots (102154, 게시 2026-07-06) — https://support.apple.com/en-us/102154
6. mac_apt README, Yogesh Khatri (v1.33.2) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/README.md
