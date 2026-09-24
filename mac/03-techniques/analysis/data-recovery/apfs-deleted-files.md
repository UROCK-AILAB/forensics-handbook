---
title: "APFS에서 지운 파일"
parent: "삭제 데이터 복구"
grand_parent: "기법 · 분석"
nav_order: 2130
---

# APFS에서 지운 파일 (APFS)

APFS가 객체를 제자리에서 고치지 않고 늘 새 위치에 쓰는 성질을 이용해, 옛 체크포인트·스냅샷·오브젝트 맵에 남은 이전 시점의 파일 시스템 트리에서 지운 파일의 메타데이터와 내용을 찾는 방법을 다룹니다.

## 언제 쓰나

지금의 파일 시스템 트리에는 없는 파일이 언제까지 있었는지, 내용이 무엇이었는지를 확인해야 할 때 씁니다. APFS 명세는 저장 방식과 상관없이 디스크의 객체를 제자리에서 고치지 않고, 고친 사본은 늘 디스크의 새 위치에 쓴다고 적고 있어서 [1], 파일을 지운 뒤에도 지우기 직전 상태를 가리키는 옛 메타데이터가 한동안 남을 수 있습니다.

휴지통에 아직 있는 파일은 [휴지통 (.Trash)](../../../02-artifacts/file-folder-usage/trash.md) 에서, 이름·경로만 남은 흔적은 [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md) 에서 다루고, 이 페이지는 파일 시스템 구조 안에서 옛 상태를 되짚는 일만 봅니다. 컨테이너·볼륨·B-트리의 기본 구조는 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md) 에 있습니다. Apple 실리콘·T2 Mac 은 FileVault 를 켜지 않아도 볼륨이 암호화돼 있어서 [2], 시작하기 전에 [트림과 복구 한계 (TRIM)](trim.md) 에서 무엇을 기대할 수 있는지부터 정합니다.

## 옛 상태가 남는 자리

### 체크포인트와 옛 컨테이너 수퍼블록

컨테이너 하나가 공간 관리와 충돌 보호를 맡고, 그 안의 여러 볼륨이 빈 공간을 함께 씁니다 [1]. 컨테이너 수퍼블록(nx_superblock_t)은 한 벌이 아니라 여러 벌이고, 명세는 이 사본들이 과거 여러 시점의 컨테이너 상태를 담는다고 적고 있습니다 [1].

마운트할 때는 체크포인트 설명 영역에서 매직과 체크섬이 맞으면서 트랜잭션 ID 가 가장 큰 수퍼블록을 고르고, 이 영역은 링 버퍼로 돌아가며, 체크포인트가 망가졌으면 더 옛 체크포인트로 마운트합니다 [1]. 명세의 최소 체크포인트 수 상수(NX_TX_MIN_CHECKPOINT_COUNT)는 4입니다 [1]. 블록 0 에도 수퍼블록 사본이 있지만 깨끗이 내리지 않았으면 옛 버전일 수 있고, 실제로는 이 사본으로 체크포인트 설명 영역의 위치(nx_xp_desc_base)만 찾습니다 [1].

설명 영역에 남은 옛 수퍼블록 하나하나가 그 시점의 오브젝트 맵과 파일 시스템 트리로 거슬러 가는 입구가 되고(명세 문장에서 끌어낸 판단입니다), 아래 절차는 여기서 출발합니다.

### 오브젝트 맵과 트랜잭션 ID

명세는 객체를 저장하는 방식을 셋으로 나눕니다 [1].

| 저장 방식 | 주소를 찾는 법 | 고칠 때 |
|---|---|---|
| 임시 (ephemeral) | 체크포인트에 저장 | — |
| 물리 (physical) | 블록 주소가 곧 객체 ID | 새 위치에 쓰고 ID 도 바뀜 |
| 가상 (virtual) | 오브젝트 맵(omap)에서 찾음 | ID 는 그대로이고, 트랜잭션 ID 로 시점을 고름 |

오브젝트 맵 B-트리의 키(omap_key_t)는 가상 객체 ID(ok_oid)와 트랜잭션 ID(ok_xid)로 이뤄지고, 값(omap_val_t)에는 ov_flags, ov_size, ov_paddr 가 들어 있습니다 [1]. 같은 가상 객체 ID 에 트랜잭션 ID 가 다른 항목이 여럿 남아 있다면 시점마다 물리 주소가 따로 적혀 있는 셈이라서, 옛 트랜잭션 ID 로 고르면 그때의 트리 노드를 읽을 수 있습니다. ov_flags 의 OMAP_VAL_DELETED(0x00000001)는 객체가 지워져 이 매핑이 자리만 지키고 있다는 뜻이고, B-트리의 "ghost" 키는 문맥에 따라 지워져서 무시해야 할 키를 뜻할 수 있습니다 [1].

### 파일 시스템 레코드

지운 파일을 찾을 때 보는 레코드 종류와 표시는 다음과 같습니다 [1].

| 이름 | 값 | 뜻 |
|---|---|---|
| APFS_TYPE_SNAP_METADATA | 1 | 스냅샷 메타데이터 |
| APFS_TYPE_INODE | 3 | inode |
| APFS_TYPE_XATTR | 4 | 확장 속성 |
| APFS_TYPE_DSTREAM_ID | 6 | 데이터 스트림 |
| APFS_TYPE_CRYPTO_STATE | 7 | 암호화 상태 |
| APFS_TYPE_FILE_EXTENT | 8 | 파일 익스텐트 |
| APFS_TYPE_DIR_REC | 9 | 디렉터리 항목 |
| APFS_KIND_DEAD (레코드 kind) | 3 | 지우는 중인 레코드 |
| INODE_IS_PURGEABLE (inode 플래그) | 0x00080000 | 다음 purge 때 지워질 inode |

파일 익스텐트 값(j_file_extent_val_t)에는 len_and_flags, phys_block_num, crypto_id 가 있어서 [1], 옛 트리에서 익스텐트 레코드를 찾으면 내용이 있던 물리 블록 번호와 길이, 복호에 쓸 값을 함께 얻습니다. 물리 익스텐트는 참조 수(refcnt)가 0 이 될 때 지울 수 있다고 명세에 적혀 있어서 [1], 복제본이나 스냅샷이 같은 블록을 쓰고 있으면 한쪽 파일을 지워도 블록은 남는다고 볼 수 있습니다(필자 판단).

### 공간 관리자와 리퍼

공간 관리자(space manager)는 컨테이너에 하나 있고 블록 할당과 해제를 맡으며, 빈 공간 비트맵(OBJECT_TYPE_SPACEMAN_BITMAP, 0x8)과 해제 대기열(free queue, OBJECT_TYPE_SPACEMAN_FREE_QUEUE, 0x9)을 씁니다 [1]. 해제 대기열은 sm_fq 배열의 SFQ_IP(0), SFQ_MAIN(1), SFQ_TIER2(2) 세 칸이고, 칸마다 sfq_count, sfq_tree_oid, sfq_oldest_xid 가 있습니다 [1]. 리퍼(reaper)는 컨테이너에 하나 있고, 한 트랜잭션 사이에 다 지우기에는 큰 객체를 여러 트랜잭션에 걸쳐 지웁니다 [1].

해제 대기열에 들어간 블록이 언제 실제로 재사용되거나 TRIM 되는지는 이번 출처로 확인하지 못해서, 해제 대기열에 올라 있다는 사실만으로 블록 내용이 남아 있다고 단정하지 않습니다.

### 스냅샷

스냅샷은 특정 시점 파일 시스템의 읽기 전용 사본이고, 만들기는 빠르고 싸지만 지우기는 일이 더 많습니다 [1]. 스냅샷 메타데이터 값(j_snap_metadata_val_t)에는 extentref_tree_oid, sblock_oid, create_time, change_time, inum, extentref_tree_type, flags, name_len, name 이 있고, 키의 객체 ID 가 곧 그 스냅샷의 트랜잭션 ID 입니다 [1]. 오브젝트 맵 쪽 스냅샷 정보(omap_snapshot_t)에는 oms_flags 와 oms_oid 가 있고, OMAP_SNAPSHOT_DELETED(0x1)가 서 있으면 지워진 스냅샷입니다 [1].

스냅샷끼리, 또는 스냅샷과 현재 볼륨을 비교하는 방법은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../snapshot-diff.md) 에서, 타임 머신이 만드는 스냅샷은 [타임 머신 (Time Machine)](../../../02-artifacts/filesystem/time-machine/index.md) 에서 봅니다.

### 객체 머리

체크포인트를 훑거나 원시 영역에서 노드를 찾을 때는 모든 객체 앞에 붙는 머리(obj_phys_t)로 객체를 알아보고 체크섬으로 검증합니다. 오프셋은 명세의 필드 크기로 계산한 값입니다 [1].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 8 | o_cksum | Fletcher 64 체크섬 |
| 8 | 8 | o_oid | 객체 ID |
| 16 | 8 | o_xid | 트랜잭션 ID |
| 24 | 4 | o_type | 아래 16비트는 종류, 위 16비트는 플래그 |
| 28 | 4 | o_subtype | 하위 종류 |

컨테이너 수퍼블록의 매직 상수는 NX_MAGIC('BSXN'), 볼륨 수퍼블록(apfs_superblock_t)은 APFS_MAGIC('BSPA')로 명세에 적혀 있고 [1], 기본이자 최소 블록 크기는 4096 바이트입니다 [1]. 명세는 매직을 C 다중 문자 상수로만 적고 있어서, 디스크에서 바이트가 어떤 순서로 보이는지는 이번 출처로 확인하지 못했습니다.

## 절차

1. **이미지를 확보하고 복호할 수 있는지 봅니다.** APFS 소프트웨어 암호화에서는 사용자 암호로 KEK 를, KEK 로 VEK 를 풀고(RFC 3394), 파일 데이터는 VEK 로 AES-XTS 복호하며 익스텐트의 crypto_id 를 tweak 로 씁니다 [1]. 암호화된 볼륨이라면 옛 체크포인트와 지운 블록도 키가 있어야 읽힌다고 보고(명세와 보안 가이드에서 끌어낸 판단), 키나 복호된 사본을 먼저 확보합니다. 확보 방법은 [맥 증거 확보 (Acquisition)](../../process-acquisition/evidence-acquisition/index.md), 복호는 [암호화된 증거 다루기 (Encrypted Evidence)](../encrypted-evidence/index.md) 와 [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) 를 따릅니다.
2. **체크포인트 설명 영역을 찾습니다.** 블록 0 의 수퍼블록 사본에서 nx_xp_desc_base 를 읽습니다 [1].
3. **옛 수퍼블록을 모두 모읍니다.** 설명 영역을 훑어 매직과 체크섬이 맞는 컨테이너 수퍼블록을 모으고 트랜잭션 ID 순으로 줄 세웁니다. 마운트는 가장 큰 것 하나만 쓰지만 [1], 복구에서는 나머지가 옛 시점으로 가는 입구입니다.
4. **시점별 트리를 읽습니다.** 수퍼블록마다 볼륨 수퍼블록과 오브젝트 맵을 따라가 그 시점의 파일 시스템 트리를 읽고, inode(3)·디렉터리 항목(9)·파일 익스텐트(8) 레코드를 뽑습니다 [1].
5. **현재 트리와 비교합니다.** 옛 트리에만 있는 inode 와 디렉터리 항목을 추리고, 레코드 kind 가 APFS_KIND_DEAD 인 것, 오브젝트 맵 값에 OMAP_VAL_DELETED 가 선 것, inode 에 INODE_IS_PURGEABLE 이 선 것은 따로 표시합니다 [1]. 디렉터리 항목만 사라지고 같은 inode 번호가 다른 이름으로 남아 있으면 지운 것이 아니라 이름을 바꾸거나 옮긴 것일 수 있어서 함께 봅니다.
6. **스냅샷에도 되풀이합니다.** 스냅샷 메타데이터 레코드로 목록을 만들고 스냅샷마다 4~5단계를 되풀이합니다. OMAP_SNAPSHOT_DELETED 가 선 항목도 목록에 남깁니다 [1].
7. **내용을 꺼냅니다.** 추린 파일의 익스텐트에서 물리 블록 번호와 길이를 읽어 블록을 꺼내고, 암호화된 볼륨이면 1단계의 키와 crypto_id 로 복호합니다 [1].
8. **내용이 그 파일의 것인지 확인합니다.** 옛 체크포인트가 가리키는 블록이 그 뒤에 다른 데이터로 채워졌을 수 있다고 보고(필자 판단), 파일 형식의 시그니처와 크기가 맞는지, 같은 블록을 가리키는 다른 시점의 레코드가 있는지 봅니다.
9. **출처를 기록합니다.** 결과마다 어느 컨테이너 수퍼블록(트랜잭션 ID)이나 어느 스냅샷에서 찾았는지, 어떤 표시가 서 있었는지를 적어 둡니다.

## 도구

공개 도구 afro 는 APFS 를 파싱해 다른 도구가 찾지 못하는 지운 파일을 되살린다고 소개하고, 볼륨 안의 여러 파일 시스템 버전과 체크포인트를 처리하며, 출력 폴더 이름에 carve_apsb 가 보여서 [3] 볼륨 수퍼블록도 카빙하는 것으로 짐작됩니다(폴더 이름에서 끌어낸 판단입니다). 결과를 sleuthkit body 파일로도 내보내서 [3] [타임라인 작성 (Timeline)](../timeline/index.md) 에 바로 올릴 수 있고, README 는 논문 "Forensic APFS File Recovery"(DOI 10.1145/3230833.3232808)를 근거로 듭니다 [3].

도구 하나의 결과로 끝내지 말고 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md) 에 따라 위 절차의 몇 단계를 직접 따라가 맞춰 봅니다. 파일 시스템 구조를 거치지 않고 원시 영역에서 APFS 객체를 찾는 방법은 [카빙 (Carving)](carving.md) 에서 다룹니다.

## 시각 해석

inode(j_inode_val_t)의 create_time, mod_time, change_time, access_time 과 디렉터리 항목의 date_added 는 1970-01-01 00:00 UTC 부터 센 나노초이고 윤초는 무시합니다 [1]. date_added 는 같은 폴더 안에서 이름만 바꿀 때는 갱신되지 않고, access_time 을 언제 갱신하는지는 APFS_FEATURE_STRICTATIME 에 따라 다릅니다 [1]. 값 읽는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) 에 있습니다.

옛 트리에서 찾은 inode 의 시각은 그 트랜잭션 시점까지의 값이라서 파일을 지운 시각을 알려 주지 않습니다. 지운 때는 그 파일이 마지막으로 보이는 트랜잭션과 처음으로 사라진 트랜잭션 사이로 좁힐 수 있지만, 트랜잭션 ID 를 벽시계 시각과 잇는 방법은 이번 출처로 확인하지 못했습니다. 스냅샷 메타데이터에는 create_time 이 있어서 [1] 스냅샷 단위로는 시각 기준점을 얻을 수 있고, 더 좁히려면 [파일 시스템 이벤트 (FSEvents)](../../../02-artifacts/filesystem/fsevents/index.md) 의 삭제 기록과 맞춰 봅니다.

## 함정과 한계

체크포인트 설명 영역은 링 버퍼라서 [1] 오래된 체크포인트는 새 것으로 덮인다고 보고(필자 판단), 거슬러 갈 수 있는 기간이 짧을 수 있다는 점을 전제로 합니다. 옛 트리에서 찾지 못했다고 그 파일이 없었다고 말할 수 없고, 반대로 옛 트리에 레코드가 있어도 익스텐트가 가리키는 블록은 이미 재사용됐거나 TRIM 으로 비워졌을 수 있습니다. 내장 SSD 에서 어디까지 기대할 수 있는지는 [트림과 복구 한계 (TRIM)](trim.md) 에서 정리합니다.

복제본이나 스냅샷과 블록을 함께 쓰는 파일은 한쪽을 지워도 내용이 살아 있어서, 되살린 내용이 지운 파일에서 왔는지 아직 살아 있는 복제본에서 왔는지 구분해야 합니다. 명세 상수와 구조체는 2020-06-22 판 명세 기준이고 [1], 그 뒤 macOS 버전에서 바뀐 점은 이번 출처로 확인하지 못했습니다.

## 결과를 어떻게 해석하나

옛 체크포인트나 스냅샷에서 찾은 레코드는 "그 트랜잭션 시점에 이 볼륨의 파일 시스템에 이 이름·크기·시각의 항목이 있었다" 를 말해 주고, 내용 블록을 8단계처럼 검증했다면 그 시점의 내용까지 말해 줍니다. 누가 지웠는지, 일부러 지웠는지, 정확히 언제 지웠는지는 이 기록만으로 알 수 없어서 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md) 의 다른 흔적과 함께 판단합니다.

보고서에는 "트랜잭션 ID 가 가장 큰 체크포인트에서 세 번째로 옛 컨테이너 수퍼블록이 가리키는 파일 시스템 트리에 이 경로의 inode 가 있고, 현재 트리에는 같은 inode 번호가 없다" 처럼 어느 시점의 어느 구조에서 찾았는지를 그대로 적습니다.

## 참고 문헌

1. Apple, Apple File System Reference (2020-06-22) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
2. Apple, Apple Platform Security (2026년 8월) — https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf
3. afro (APFS File Recovery) README — https://raw.githubusercontent.com/cugu/afro/master/README.md
