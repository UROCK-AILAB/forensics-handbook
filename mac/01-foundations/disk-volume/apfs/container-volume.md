---
title: "컨테이너와 볼륨"
parent: "APFS 구조"
grand_parent: "기반 · 디스크·볼륨"
nav_order: 10
---

# 컨테이너와 볼륨 (Container·Volume)

APFS 파티션 하나에는 컨테이너 (container)가 하나 있고 그 안에 볼륨 (volume)이 여럿 들어가며 [1], 컨테이너 슈퍼블록과 볼륨 슈퍼블록에는 블록 크기와 볼륨 목록뿐만 아니라 볼륨의 역할, 볼륨을 만들고 고친 소프트웨어와 그 시각까지 적혀 있습니다 [1].

APFS가 두 층(컨테이너 층과 파일 시스템 층)으로 나뉜다는 점과 숫자를 리틀 엔디언으로 저장한다는 점은 [APFS 구조 (APFS)](index.md)에 있고, 이 페이지는 두 슈퍼블록과 볼륨 배치만 다룹니다. 슈퍼블록 앞머리의 객체 헤더와 체크포인트는 [객체와 체크포인트 (Object·Checkpoint)](object-checkpoint.md)에서 설명합니다.

## 이 구조를 쓰는 곳

맥의 시동 디스크와 APFS로 포맷한 외장 디스크가 모두 이 구조이고, 어느 볼륨에 무엇이 들어 있는지를 알아야 아티팩트를 찾을 곳이 정해집니다. macOS 10.15 이상에서 사용자 폴더와 `/Library`, `/private`, `/var` 는 Data 볼륨에 있고 [2], 두 볼륨이 하나처럼 보이는 방식은 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../volume-group-firmlinks.md)에서 다룹니다. 볼륨 암호화는 [파일볼트 (FileVault)](../../protection/filevault/index.md)와 이어지고, Time Machine 백업을 담는 볼륨도 역할 값으로 구별합니다 [1].

## 파티션에서 컨테이너까지

GPT에서 APFS 파티션의 유형 UUID는 `7C3457EF-0000-11AA-AA11-00306543ECAC` 입니다 [1]. 파티션 표 읽는 법은 [파티션 구조 (GPT·APFS 파티션)](../gpt-partitions.md)에 있습니다.

파티션의 블록 0에는 컨테이너 슈퍼블록 `nx_superblock_t` 의 사본이 있고, 깨끗이 언마운트했는지에 따라 이 사본은 최신일 수도 있고 옛것일 수도 있습니다 [1]. 블록 0 사본은 체크포인트를 찾는 데에만 쓰고, 나머지 정보는 체크포인트에 있는 최신 슈퍼블록에서 읽습니다 [1].

블록 크기는 최소·기본이 4096바이트이고 최대가 65536바이트이며, 컨테이너는 1048576바이트보다 작을 수 없습니다 [1]. 한 컨테이너에 들어가는 볼륨은 최대 100개(`NX_MAX_FILE_SYSTEMS`)이지만, 실제 상한 `nx_max_file_systems` 는 컨테이너 크기를 512 MiB로 나눠 올림한 값이라서 1.3 GiB 컨테이너라면 3개입니다 [1].

볼륨들은 컨테이너의 여유 공간을 나눠 씁니다(space sharing). 한 볼륨이 쓸 수 있는 공간은 컨테이너 크기에서 모든 볼륨이 쓴 공간을 뺀 만큼이라서 [2], 볼륨마다 크기를 정해 두는 파티션과 다릅니다.

## 컨테이너 슈퍼블록

매직은 `NX_MAGIC` = `'BSXN'` 이고 리틀 엔디언으로 저장해서 헥스 덤프에는 "NXSB"로 보입니다 [1]. 구조체 크기는 4096바이트이고, 필드와 오프셋은 아래와 같습니다 [1][3].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 32 | `nx_o` | 객체 헤더. 형식 값 0x80000001 [3] |
| 32 | 4 | `nx_magic` | "NXSB" |
| 36 | 4 | `nx_block_size` | 논리 블록 크기 |
| 40 | 8 | `nx_block_count` | 블록 수 |
| 48 / 56 / 64 | 8씩 | `nx_features` / `nx_readonly_compatible_features` / `nx_incompatible_features` | 기능 플래그 |
| 72 | 16 | `nx_uuid` | 컨테이너 UUID. 빅 엔디언으로 저장 [3] |
| 88 | 8 | `nx_next_oid` | 다음에 쓸 가상·임시 객체 ID |
| 96 | 8 | `nx_next_xid` | 다음 트랜잭션 ID |
| 104~148 | | `nx_xp_desc_*`, `nx_xp_data_*` | 체크포인트 영역의 위치와 크기 |
| 152 | 8 | `nx_spaceman_oid` | 공간 관리자(임시 객체) |
| 160 | 8 | `nx_omap_oid` | 컨테이너 객체 맵(물리 객체) |
| 168 | 8 | `nx_reaper_oid` | 리퍼(임시 객체) |
| 180 | 4 | `nx_max_file_systems` | 최대 볼륨 수 |
| 184 | 800 | `nx_fs_oid[100]` | 볼륨 슈퍼블록의 가상 객체 ID 배열 |
| 984 | 256 | `nx_counters[32]` | 개발용 카운터 |
| 1264 | 8 | `nx_flags` | 컨테이너 플래그 |
| 1272 | 8 | `nx_efi_jumpstart` | EFI 드라이버 정보 위치 |
| 1280 | 16 | `nx_fusion_uuid` | Fusion 세트 UUID(Fusion이 아니면 0) |
| 1296 | 16 | `nx_keylocker` | 컨테이너 키백 위치 |
| 1384 | 8 | `nx_newest_mounted_version` | 이 컨테이너를 마운트한 가장 새 소프트웨어 버전 |
| 1392 | 16 | `nx_mkb_locker` | 감싼 미디어 키 |

104~148번 칸의 뜻과 가상 객체 ID를 실제 블록으로 바꾸는 방법은 [객체와 체크포인트 (Object·Checkpoint)](object-checkpoint.md)에 있습니다.

`nx_newest_mounted_version` 에는 Apple 구현이 이 컨테이너를 마운트한 가장 새 소프트웨어 버전이 aaaaaaa.bbb.ccc.ddd.eee 모양의 고정소수점 10진수로 적힙니다 [1]. 이 값과 macOS 버전 번호의 대응은 공개 자료에 없어서, 값을 macOS 버전으로 바꿔 보고서에 쓰지 않습니다.

`nx_counters` 의 0번 `NX_CNTR_OBJ_CKSUM_SET` 은 쓸 때 체크섬을 계산한 횟수이고, 1번 `NX_CNTR_OBJ_CKSUM_FAIL` 은 읽을 때 체크섬이 틀린 횟수입니다 [1]. 컨테이너 플래그 `NX_CRYPTO_SW` (0x4)가 켜져 있으면 소프트웨어 암호화를 쓰는 컨테이너입니다 [1].

Fusion 드라이브는 `NX_INCOMPAT_FUSION` (0x100)으로 표시하고, `nx_fusion_uuid` 의 최상위 비트가 1이면 주 장치(SSD), 0이면 2차 장치(HDD)입니다 [1]. `nx_efi_jumpstart` 가 가리키는 곳에는 부팅용 EFI 드라이버가 파티션 안에 들어 있고, 그 매직 `'RDSJ'` 은 헥스 덤프에서 "JSDR"로 보입니다 [1].

## 볼륨 슈퍼블록

볼륨 슈퍼블록 `apfs_superblock_t` 의 매직은 `APFS_MAGIC` = `'BSPA'` 이고 헥스 덤프에는 "APSB"로 보입니다 [1]. 크기는 1056바이트이고, 객체 형식 값은 보통 0x0000000d(가상)이지만 스냅숏에 딸린 볼륨 슈퍼블록은 0x4000000d(물리)입니다 [3].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 32 | 4 | `apfs_magic` | "APSB" |
| 36 | 4 | `apfs_fs_index` | 컨테이너 `nx_fs_oid` 배열 안의 자리 |
| 40 / 48 / 56 | 8씩 | `apfs_features` / `apfs_readonly_compatible_features` / `apfs_incompatible_features` | 기능 플래그 |
| 64 | 8 | `apfs_unmount_time` | 마지막 언마운트 시각 |
| 96 | 20 | `apfs_meta_crypto` | 메타데이터 암호화 키 정보 |
| 128 | 8 | `apfs_omap_oid` | 볼륨 객체 맵(물리) |
| 136 | 8 | `apfs_root_tree_oid` | 파일 시스템 트리(가상) |
| 144 | 8 | `apfs_extentref_tree_oid` | 익스텐트 참조 트리(물리) |
| 152 | 8 | `apfs_snap_meta_tree_oid` | 스냅숏 메타데이터 트리 |
| 160 | 8 | `apfs_revert_to_xid` | 되돌릴 스냅숏의 xid |
| 176 | 8 | `apfs_next_obj_id` | 다음 파일 시스템 객체 ID |
| 184~216 | 8씩 | `apfs_num_files`, `apfs_num_directories`, `apfs_num_symlinks`, `apfs_num_other_fsobjects`, `apfs_num_snapshots` | 개수 |
| 224 / 232 | 8씩 | `apfs_total_blocks_alloced` / `apfs_total_blocks_freed` | 누적 할당·해제 블록 수 |
| 240 | 16 | `apfs_vol_uuid` | 볼륨 UUID |
| 256 | 8 | `apfs_last_mod_time` | 마지막 수정 시각 |
| 264 | 8 | `apfs_fs_flags` | 볼륨 플래그 |
| 272 | 48 | `apfs_formatted_by` | 볼륨을 만든 소프트웨어 |
| 320 | 384 | `apfs_modified_by[8]` | 볼륨을 고친 소프트웨어 8개 |
| 704 | 256 | `apfs_volname` | 볼륨 이름(NULL로 끝나는 UTF-8) |
| 960 | 4 | `apfs_next_doc_id` | 다음 문서 ID |
| 964 | 2 | `apfs_role` | 볼륨 역할 |
| 968 | 8 | `apfs_root_to_xid` | 0이 아니면 이 xid의 스냅숏에서 루트로 시작 |
| 976 | 8 | `apfs_er_state_oid` | 암호화·복호화 진행 상태 |
| 984 / 992 | 8씩 | `apfs_cloneinfo_id_epoch` / `apfs_cloneinfo_xid` | macOS 10.13.3에서 추가 |
| 1000 | 8 | `apfs_snap_meta_ext_oid` | macOS 10.15에서 추가 |
| 1008 | 16 | `apfs_volume_group_id` | 볼륨 그룹 UUID. macOS 10.15에서 추가 |
| 1024 / 1032 / 1040 | | `apfs_integrity_meta_oid`, `apfs_fext_tree_oid`, `apfs_fext_tree_type` | macOS 11에서 추가(봉인 볼륨) |

시각 칸의 단위와 증거로서의 뜻은 [APFS의 시각 네 가지 (Create·Modify·Change·Access)](timestamps.md)에서, 스냅숏 관련 칸은 [스냅숏 (Snapshots)](snapshots.md)에서, clone 관련 칸은 [복제·희소·압축 파일 (Clone·Sparse·Compression)](clone-sparse-compression.md)에서 다룹니다.

`apfs_formatted_by` 는 볼륨을 만들 때 한 번만 쓰고, `apfs_modified_by` 는 볼륨을 고친 구현을 8개까지 적는 배열입니다 [1]. 두 칸 모두 `apfs_modified_by_t` 구조(48바이트)이고, 32바이트 `id` 에 프로그램 이름과 버전 문자열이, 그 뒤 8바이트 `timestamp` 와 8바이트 `last_xid` 가 들어 있습니다 [1][3]. 배열의 0번이 가장 새 항목이고, 볼륨을 고칠 때마다 한 칸씩 밀고 0번에 새로 적되 같은 구현이 이미 마지막 항목이면 그대로 둘 수도 있습니다 [1]. libyal 문서는 순서를 "옛것에서 새것?"으로 물음표를 달아 적었지만 [3], 순서는 명세 [1]를 기준으로 읽습니다.

`apfs_total_blocks_alloced` 는 블록을 할당할 때만 늘고 해제할 때는 그대로이며, `apfs_total_blocks_freed` 는 그 반대입니다 [1].

## 볼륨 역할

`apfs_role` 에는 볼륨의 역할이 하나만 적힙니다 [1]. 아래 표는 macOS에 해당하는 역할만 추렸고, 0x0040 이상 세 값은 `n << 6` 정의(`APFS_VOLUME_ENUM_SHIFT` = 6)로 계산한 16진수입니다 [1].

| 상수 | 값 | 뜻 |
|---|---|---|
| `APFS_VOL_ROLE_NONE` | 0x0000 | 역할 없음 |
| `APFS_VOL_ROLE_SYSTEM` | 0x0001 | 시스템 루트. macOS 10.15 이상에서 읽기 전용으로 마운트 |
| `APFS_VOL_ROLE_USER` | 0x0002 | 사용자 홈 |
| `APFS_VOL_ROLE_RECOVERY` | 0x0004 | 복구 시스템 |
| `APFS_VOL_ROLE_VM` | 0x0008 | 가상 메모리 스왑, `/var/vm` 에 마운트 |
| `APFS_VOL_ROLE_PREBOOT` | 0x0010 | 암호화된 볼륨으로 부팅할 때 필요한 파일 |
| `APFS_VOL_ROLE_INSTALLER` | 0x0020 | OS 설치 프로그램(설치 로그 등) |
| `APFS_VOL_ROLE_DATA` | 0x0040 | 바뀌는 데이터(사용자 데이터와 바뀌는 시스템 데이터) |
| `APFS_VOL_ROLE_BACKUP` | 0x0180 | Time Machine 백업 저장, macOS 전용 |
| `APFS_VOL_ROLE_PRELOGIN` | 0x02C0 | 로그인 전에 쓰는 시스템 데이터, macOS 전용 |

하위 6비트에 적는 역할과 DATA는 모든 macOS가 지원하고, 상위 10비트에 적는 나머지 역할은 macOS 10.15 이상만 지원합니다 [1].

## macOS 10.15 이후의 볼륨 배치

macOS 10.15 이상에서 시동용 APFS 컨테이너에는 볼륨이 적어도 다섯 개 있고, 그중 Preboot·VM·Recovery 셋은 사용자에게 숨겨져 있습니다 [2].

| 볼륨 | 암호화 | 담는 것 |
|---|---|---|
| Preboot | 안 됨 | 컨테이너 안 각 시스템 볼륨의 부팅에 필요한 데이터 |
| VM | 안 됨 | 암호화된 스왑 파일 |
| Recovery | 안 됨 | recoveryOS. 시스템 볼륨을 풀지 않고 시동할 수 있어야 해서 암호화하지 않음 |
| System | | 시동 파일과 macOS 기본 앱(`/System/Applications`). 기본값으로 어떤 프로세스도 쓸 수 없음 |
| Data | | 사용자 폴더 데이터, 사용자가 설치한 앱, `/Applications`, `/Library`, `/Users`, `/Volumes`, `/usr/local`, `/private`, `/var`, `/tmp` 등 |

시스템 볼륨을 하나 더 만들 때마다 Data 볼륨도 하나씩 생기고, Preboot·VM·Recovery는 함께 씁니다 [2]. 한 컨테이너에 macOS를 둘 이상 설치했다면 System·Data 쌍이 여럿 보이는 까닭이 여기에 있습니다.

| macOS | 시스템 볼륨 |
|---|---|
| 10.15 | 읽기 전용 시스템 볼륨을 처음 도입하고 System과 Data를 나눔 [2][4] |
| 11 이상 | 서명된 시스템 볼륨 (Signed System Volume, SSV). 시스템 볼륨을 스냅숏으로 잡고 그 스냅숏에서 부팅함 [2][4] |

System과 Data 볼륨의 `apfs_volume_group_id` 값이 같으면 한 볼륨 그룹이고, `APFS_FEATURE_VOLGRP_SYSTEM_INO_SPACE` (0x10)는 두 볼륨을 사용자에게 하나처럼 보이게 마운트하는 기능으로 macOS 10.15 이상에서 씁니다 [1]. 이 기능이 켜지면 Data 볼륨은 `UNIFIED_ID_SPACE_MARK` (0x0800000000000000) 미만의 아이노드 번호를, System 볼륨은 그 이상의 번호를 쓰고, 예약 번호도 System 쪽은 이 값을 더한 번호라서 System 볼륨의 루트는 0x0800000000000002입니다 [1]. `SYSTEM_OBJ_ID_MARK` (0x0fffffff00000000)도 볼륨 그룹에서 이 값 이상이면 시스템 볼륨 객체라는 뜻으로 정의되어 있지만 [1], 두 상수가 어떻게 다른지는 명세에 설명이 없습니다. 볼륨 그룹을 이어 주는 펌링크는 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../volume-group-firmlinks.md)에서 다룹니다.

봉인 (sealed) 볼륨은 역할이 SYSTEM이고, `APFS_INCOMPAT_SEALED_VOLUME` (0x20)가 켜져 있고, `apfs_integrity_meta_oid` 와 `apfs_fext_tree_oid` 가 0이 아니고, 파일 시스템 B-트리에 `BTREE_HASHED`·`BTREE_NOHEADER` 가 켜져 있어야 합니다 [1]. SSV는 SHA-256 해시를 메타데이터 트리에 저장하고 루트 노드의 해시를 "seal"이라 부르며, Apple 실리콘에서는 부트로더가, T2 인텔 Mac에서는 커널이 루트 파일 시스템을 마운트하기 전에 seal을 검증합니다 [4]. 사용자가 보안 수준을 낮추고 SSV를 끄지 않는 한 부팅할 때마다 검증하고, FileVault가 켜진 상태에서는 SSV를 끌 수 없습니다 [4].

## 볼륨 플래그와 기능 플래그

볼륨 플래그와 기능 플래그 값은 다음과 같습니다 [1].

| 필드 | 플래그 | 값 | 뜻 |
|---|---|---|---|
| `apfs_fs_flags` | `APFS_FS_UNENCRYPTED` | 0x1 | 암호화 안 됨 |
| | `APFS_FS_ONEKEY` | 0x8 | 모든 파일을 볼륨 키(VEK) 하나로 암호화. macOS에서만 씀 |
| | `APFS_FS_SPILLEDOVER` | 0x10 | Fusion에서 SSD 몫을 다 씀 |
| incompatible | `APFS_INCOMPAT_CASE_INSENSITIVE` | 0x1 | 대소문자 비구분 |
| | `APFS_INCOMPAT_DATALESS_SNAPS` | 0x2 | 데이터 없는 스냅숏이 하나 이상 있음 |
| | `APFS_INCOMPAT_ENC_ROLLED` | 0x4 | 암호화 키를 한 번 이상 바꿈 |
| | `APFS_INCOMPAT_NORMALIZATION_INSENSITIVE` | 0x8 | 정규화 비구분 |
| | `APFS_INCOMPAT_INCOMPLETE_RESTORE` | 0x10 | 복원 중이거나 복원이 비정상으로 멈춤 |
| | `APFS_INCOMPAT_SEALED_VOLUME` | 0x20 | 봉인 볼륨 |
| features | `APFS_FEATURE_DEFRAG` | 0x4 | macOS 10.14 전에는 무시됨 |
| | `APFS_FEATURE_STRICTATIME` | 0x8 | 읽을 때마다 접근 시각 갱신 |
| | `APFS_FEATURE_VOLGRP_SYSTEM_INO_SPACE` | 0x10 | 볼륨 그룹을 하나처럼 마운트 |

macOS에는 대소문자를 구분하는 변형과 구분하지 않는 변형이 있고 구분하지 않는 쪽이 기본입니다 [5]. 이름 정규화는 [유니코드 정규화 (NFD·NFC)](../../value-decoding/unicode-normalization.md)에서, 접근 시각 규칙은 [APFS의 시각 네 가지 (Create·Modify·Change·Access)](timestamps.md)에서 다룹니다.

## 암호화 구조

공개된 명세에는 소프트웨어 암호화 구조만 나옵니다 [1]. 하드웨어 암호화는 이를 지원하는 기기의 내장 저장소(T2 칩 Mac 등)에 쓰고 이때 내장 저장소에는 커널만 접근할 수 있으며, 소프트웨어 암호화는 외장 저장소와 하드웨어 암호화를 지원하지 않는 내장 저장소에 씁니다 [1].

키는 사용자 암호(또는 개인·기관 복구 키)로 KEK를 풀고, KEK로 VEK를 풀고, VEK로 파일 시스템 트리와 파일 데이터를 복호하는 순서로 이어집니다 [1]. 컨테이너 키백은 `nx_keylocker` 가 가리키고 볼륨별로 감싼 VEK와 볼륨 키백 위치를 담으며, 볼륨 키백에는 사용자 암호와 복구 키로 감싼 KEK 사본들과 암호 힌트(`KB_TAG_VOLUME_PASSPHRASE_HINT`)가 들어 있을 수 있습니다 [1]. 파일 데이터는 VEK를 AES-XTS 키로, `crypto_id` 를 tweak로 써서 복호합니다 [1]. 키 계층의 자세한 내용은 [파일볼트 (FileVault)](../../protection/filevault/index.md)에, 암호화된 이미지를 다루는 절차는 [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md)에 있습니다.

키백은 컨테이너·볼륨 UUID로 감싸 두어서(RFC 3394), 볼륨 슈퍼블록을 안전하게 지우면 그 볼륨의 암호화된 내용을 읽을 수 없게 됩니다 [1].

## 읽는 법

### 헥스로 한 번

아래 바이트는 실제 검체가 아니라 명세 [1]과 형식 문서 [3]에 맞춰 만든 예시이고, `xx` 는 값이 검체마다 다른 자리입니다. 먼저 컨테이너 슈퍼블록의 앞부분입니다.

```
블록 내 오프셋
0000  xx xx xx xx xx xx xx xx 01 00 00 00 00 00 00 00
0010  xx xx xx xx xx xx xx xx 01 00 00 80 00 00 00 00
0020  4E 58 53 42 00 10 00 00 xx xx xx xx xx xx xx xx
```

0x08의 `01 00 ...` 은 객체 ID 1이고, 이 번호는 컨테이너 슈퍼블록에 예약된 ID입니다 [1]. 0x18의 `01 00 00 80` 은 리틀 엔디언으로 0x80000001, 곧 임시 객체 플래그가 붙은 컨테이너 슈퍼블록 형식입니다 [3]. 0x20의 `4E 58 53 42` 가 "NXSB"이고, 0x24의 `00 10 00 00` 은 블록 크기 0x1000 = 4096바이트입니다.

다음은 Data 역할인 볼륨 슈퍼블록의 두 부분입니다.

```
블록 내 오프셋
0020  41 50 53 42 01 00 00 00 ...
...
03C0  xx xx xx xx 40 00 ...
```

0x20의 `41 50 53 42` 가 "APSB"이고, 0x24의 `01 00 00 00` 은 컨테이너 `nx_fs_oid` 배열의 1번 자리라는 뜻입니다. 0x3C4(964)의 `40 00` 은 역할 0x0040, 곧 Data 볼륨입니다.

### 절차

1. 파티션 표에서 APFS 유형 UUID로 파티션을 찾고, 블록 0에서 "NXSB"와 블록 크기를 확인합니다.
2. 블록 0 사본의 체크포인트 영역 칸으로 최신 컨테이너 슈퍼블록을 찾습니다. 방법은 [객체와 체크포인트 (Object·Checkpoint)](object-checkpoint.md)에 있습니다.
3. 최신 슈퍼블록의 `nx_fs_oid` 배열에서 0이 아닌 ID를 모두 적고, 컨테이너 객체 맵에서 각 ID의 블록 주소를 찾습니다.
4. 볼륨 슈퍼블록마다 이름, UUID, 역할, 볼륨 그룹 UUID, 플래그를 표로 정리합니다.
5. 볼륨마다 `apfs_formatted_by` 와 `apfs_modified_by` 의 프로그램 문자열과 시각을 따로 적어 둡니다.
6. 암호화 플래그를 보고 복호가 필요한 볼륨을 가려낸 뒤, [파일 시스템 트리와 아이노드 (FS Tree·Inode)](fs-tree-inode.md)로 넘어갑니다.

## 포렌식에서 중요한 점

`apfs_modified_by` 배열에는 볼륨을 고친 구현의 이름·버전 문자열과 시각, 마지막 트랜잭션 ID가 8개까지 남습니다 [1]. 이 정의로 보아 증거를 확보하면서 볼륨을 읽기·쓰기로 마운트한 도구나 다른 macOS 버전도 이 배열에 올라갈 수 있습니다. 배열에 없는 구현이라도 볼륨을 고치지 않았다고 단정할 수는 없는데, 칸이 8개뿐이고 같은 구현이 이어서 고치면 새로 적지 않을 수 있기 때문입니다 [1].

블록 0의 슈퍼블록 사본은 옛것일 수 있어서 [1], 볼륨 목록이나 카운터를 이 사본만 보고 적으면 확보 시점의 상태와 다를 수 있습니다. 체크포인트 영역에 남은 옛 슈퍼블록을 과거 상태로 읽는 방법은 [지운 파일과 옛 체크포인트 (Deleted Files·Old Checkpoints)](deleted-files.md)에서 다룹니다.

`APFS_INCOMPAT_INCOMPLETE_RESTORE` 가 켜진 볼륨은 복원이 끝나지 않았거나 비정상으로 멈춘 상태라서 [1], 내용이 완전하지 않을 수 있다는 점을 보고서에 적어 둡니다. 볼륨 키백은 UUID로 감싸 두었기 때문에 암호화된 볼륨의 슈퍼블록이 안전하게 지워졌다면 키를 알아도 내용을 읽을 수 없고 [1], 이 경우는 복구 실패가 아니라 형식상 읽을 수 없는 상태로 설명합니다.

## 함정

어떤 포렌식 도구로 만든 컨테이너에서는 컨테이너 키백이 하드웨어 암호화돼 있거나 무작위 데이터인데 볼륨은 암호화되지 않은 경우가 있습니다 [3]. 키백 모양만 보고 볼륨이 암호화됐다고 판단하지 말고 볼륨 플래그를 함께 봅니다.

`nx_uuid` 는 빅 엔디언으로 저장하는 칸이라서, 다른 숫자 칸처럼 뒤집어 읽으면 UUID가 틀어집니다 [3]. UUID 표기법은 [식별자 읽기 (UUID·UID·GUID)](../../value-decoding/uuid-uid.md)를 봅니다.

System과 Data는 서로 다른 볼륨이라서 같은 경로처럼 보이는 파일이 실제로는 다른 볼륨에 있을 수 있고, 볼륨 그룹에서는 아이노드 번호의 범위로 어느 볼륨인지 구별합니다 [1].

기준 명세 [1]은 2020-06-22 판이라서 macOS 11의 봉인 볼륨 필드까지만 들어 있고, macOS 12 이후에 바뀐 점은 담겨 있지 않습니다.

## 도구

mac_apt는 HFS와 APFS 파서를 자체 구현한 공개 도구이고, macOS 11 봉인 볼륨과 macOS 10.15 이상에서 따로 마운트되는 SYSTEM·DATA 볼륨을 처리하며, 암호나 복구 키가 있으면 암호화된 APFS 이미지도 처리합니다 [6]. 슈퍼블록 칸을 직접 확인할 때는 형식 문서 [3]의 오프셋 표를 기준으로 헥스 편집기에서 따라가고, 도구 결과와 맞춰 봅니다.

## 참고 문헌

1. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
2. Apple Platform Security — Role of Apple File System (게시 2024-12-19) — https://support.apple.com/guide/security/role-of-apple-file-system-seca6147599e/web
3. Joachim Metz, libfsapfs — Apple File System (APFS) 형식 문서 (개정 0.0.18, 2026년 8월) — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
4. Apple Platform Security — Signed system volume security (게시 2022-05-13) — https://support.apple.com/guide/security/signed-system-volume-security-secd698747c9/web
5. Apple, Apple File System Guide — Frequently Asked Questions (보관 문서, 2018-06-04) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html
6. mac_apt README, Yogesh Khatri (v1.33.2) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/README.md
