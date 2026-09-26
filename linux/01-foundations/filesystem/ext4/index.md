---
title: "ext4"
parent: "기반 · 파일 시스템"
nav_order: 0
has_children: true
has_toc: false
---

# ext4 (ext4)

ext4 는 장치를 블록 그룹 (block group) 으로 나눠 쓰는 Linux 파일 시스템이고, 파일 하나의 흔적이 슈퍼블록 (superblock)·아이노드 (inode)·디렉터리 블록·저널 (journal) 에 나뉘어 남습니다.

## 왜 중요한가

Ubuntu 24.04 설치 프로그램에서 안내 설치를 고르면 루트 파일 시스템이 ext4 로 만들어집니다. 디스크에 바로 설치하면 `/` 가 ext4 이고, LVM 설치를 고르면 `/boot` 가 ext4, 볼륨 그룹 `ubuntu-vg` 의 논리 볼륨 `ubuntu-lv` 가 ext4 로 `/` 에 붙습니다[10]. RHEL 9 설치 프로그램은 기본 파일 시스템이 XFS 라서[11], RHEL 시스템의 루트는 [XFS](../xfs.md) 페이지를 먼저 봅니다. 어느 배포판이든 실제로 어떤 파일 시스템이 어디에 붙었는지는 실제 시스템의 `/etc/fstab` 과 각 볼륨의 슈퍼블록으로 확인합니다.

파일 하나를 설명하는 정보는 한곳에 모여 있지 않습니다. 이름은 디렉터리 블록의 항목에, 파일 종류·권한·UID·GID·크기·시각·데이터 위치는 아이노드에 있고[3][4], 디렉터리 항목에는 시각 필드가 없습니다[4]. 그래서 "이 이름의 파일이 언제 생겼나" 는 이름에서 아이노드 번호를 찾은 뒤 그 아이노드의 시각을 읽어야 답할 수 있습니다. 아이노드의 시각은 1970-01-01 UTC 기준 초이고, 생성 시각 (crtime) 과 삭제 시각 (dtime) 은 `stat()` 으로는 보이지 않고 debugfs 로 봅니다[3].

지운 파일을 다룰 때 ext4 는 ext2 와 다릅니다. ext3·ext4 에서는 아이노드를 풀 때 데이터 블록 정보가 사라지므로, debugfs 의 `lsdel` 같은 옛 복구 방법이 통하지 않습니다[7]. Linux 5.13 부터는 파일을 지울 때 디렉터리 항목에서 `rec_len` 을 뺀 나머지 필드(아이노드 번호·이름 길이·파일 종류·이름)을 0 으로 채웁니다[9]. 지워진 내용의 옛 사본은 저널에 남아 있을 수 있어서[9], ext4 분석에서는 저널을 따로 읽는 일이 잦습니다.

저널 때문에 원본을 다루는 방법도 조심해야 합니다. 읽기 전용 (`ro`) 으로 마운트해도 파일 시스템이 깨끗하게 해제되지 않은 상태면 커널이 저널을 재생하면서 장치에 씁니다. 이를 막으려면 `ro,noload` 로 마운트하거나 블록 장치 자체를 읽기 전용으로 둡니다[8]. 분석은 [디스크 이미징](../../../03-techniques/acquisition/disk-imaging.md) 으로 뜬 사본에서 합니다.

헥스로 읽을 때 바이트 순서가 두 가지라는 점도 먼저 알아 둡니다. ext4 의 모든 필드는 리틀 엔디언이고, 저널 (jbd2) 의 모든 필드는 빅 엔디언입니다[1][5].

## 한눈에 보기

| 구조 | 위치 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 슈퍼블록 (Superblock) | 파티션 시작에서 1024 바이트 뒤, 일부 블록 그룹에 사본. 마법 수 `0xEF53` 은 슈퍼블록 안 `0x38`[1][2] | 파일 시스템을 만든 시각, 마지막 마운트·쓰기 시각, 마지막으로 마운트된 디렉터리, 첫·마지막 오류 기록, 켜진 기능[2] | [슈퍼블록과 블록 그룹](superblock-block-group.md) |
| 그룹 서술자 (Group Descriptor) | 슈퍼블록 바로 뒤[1] | 그룹마다 비트맵·아이노드 테이블이 있는 블록 | [슈퍼블록과 블록 그룹](superblock-block-group.md) |
| 블록·아이노드 비트맵 (Bitmap) | 그룹마다 한 블록씩. `flex_bg` 면 여러 그룹의 비트맵이 첫 그룹에 모임[1] | 쓰는 블록·아이노드와 빈 자리 | [지운 파일이 남기는 것](deleted-files.md) |
| 아이노드 (Inode) | 아이노드 테이블. 기본 기록 크기 256 바이트[3][6] | 파일 종류·권한·UID·GID·크기·링크 수·시각, 데이터 위치(익스텐트)[3] | [아이노드와 익스텐트](inode-extent.md) |
| 디렉터리 항목 (Directory Entry) | 디렉터리의 데이터 블록[4] | 이름과 아이노드 번호의 짝. 시각은 없음[4] | [디렉터리 항목과 해시 트리](directory-htree.md) |
| 저널 (jbd2) | 보통 아이노드 8 번[5] | 최근 메타데이터 블록의 사본, 트랜잭션 커밋 시각[5] | [저널](journal-jbd2.md) |

블록 크기는 2^(10 + `s_log_block_size`) 바이트이고 보통 4 KiB 입니다[1]. 4 KiB 블록이면 그룹 하나가 32,768 블록, 곧 128 MiB 입니다[1].

> 그림 자리: 블록 그룹 0 의 배치(앞 1024 바이트 · 슈퍼블록 · 그룹 서술자 · 예약 GDT 블록 · 블록 비트맵 · 아이노드 비트맵 · 아이노드 테이블 · 데이터 블록)와, 이름 → 아이노드 → 데이터 블록으로 이어지는 흐름

### 배포판별 기준

| 항목 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| 설치 프로그램이 만드는 파일 시스템 | 안내 설치: `/` ext4, LVM 설치면 `/boot` 도 ext4[10] | `file_system_type = xfs`[11] |
| 기본 볼륨 구성 | 직접 설치 또는 LVM(`ubuntu-vg`/`ubuntu-lv`)[10] | `default_scheme = LVM`[12] |
| ext4 를 확인하는 곳 | 실제 시스템의 `/etc/fstab`, 각 볼륨의 슈퍼블록 | 같음. 설치 뒤 따로 만든 볼륨이 ext4 일 수 있음 |

LVM 과 디스크 암호화 아래에 있는 ext4 는 [LVM 논리 볼륨](../../disk-volume/lvm.md), [LUKS 디스크 암호화](../../disk-volume/luks.md) 에서 볼륨을 먼저 풀어야 읽을 수 있습니다.

### mkfs 기본 기능과 e2fsprogs 판

`mkfs.ext4` 가 켜는 기능은 e2fsprogs 의 `mke2fs.conf` 가 정합니다. 기본값은 블록 4096 바이트, 아이노드 256 바이트이고, ext4 유형에서 켜는 기능은 아래와 같습니다[6].

| e2fsprogs 판 | ext4 유형 기능 목록 |
|---|---|
| 1.46.5 | `has_journal,extent,huge_file,flex_bg,metadata_csum,64bit,dir_nlink,extra_isize`[6] |
| 1.47.0 이후 | 위 목록에 `metadata_csum_seed`, `orphan_file` 이 더해짐[6] |

어느 판으로 만든 파일 시스템인지는 슈퍼블록의 기능 목록으로 판단합니다. `dumpe2fs -h` 는 그룹 서술자를 빼고 슈퍼블록 정보만 출력하고, 마운트된 파일 시스템에 대고 실행하면 값이 오래됐거나 어긋날 수 있습니다[13]. `orphan_file` 이 꺼진 파일 시스템에서는 열린 채로 지운 아이노드의 `dtime` 필드가 삭제 시각 대신 고아 목록 연결에 쓰이고[3], 이 차이는 [시각 값](timestamps.md) 과 [지운 파일이 남기는 것](deleted-files.md) 에서 다룹니다.

## 읽는 순서

1. [슈퍼블록과 블록 그룹 (Superblock·Block Group)](superblock-block-group.md) — 슈퍼블록 필드 오프셋, 사본 슈퍼블록 위치, 그룹 서술자와 미초기화 그룹, 마운트·오류 기록 읽기
2. [아이노드와 익스텐트 (Inode·Extent)](inode-extent.md) — 아이노드 번호로 위치 계산, 아이노드 필드, 익스텐트 트리와 미리 할당된 영역
3. [디렉터리 항목과 해시 트리 (Directory Entry·HTree)](directory-htree.md) — 이름 항목 구조, 해시 트리 노드, 지울 때 항목이 바뀌는 방식
4. [저널 (jbd2)](journal-jbd2.md) — 저널 블록 종류와 커밋 시각, 옛 아이노드·디렉터리 블록 사본 찾기
5. [시각 값 (atime·mtime·ctime·crtime)](timestamps.md) — 네 시각과 dtime 이 바뀌는 조건, 나노초·epoch 비트 풀기, relatime·lazytime
6. [지운 파일이 남기는 것 (Deleted Files)](deleted-files.md) — 지운 뒤 아이노드·익스텐트·디렉터리 항목·저널에 남는 것과 사라지는 것

## 함께 볼 페이지

- [XFS](../xfs.md), [Btrfs](../btrfs.md) — RHEL·Fedora 계열 기본 파일 시스템
- [권한·확장 속성·ACL·Capabilities](../permissions-xattr.md) — 아이노드 안팎에 저장되는 확장 속성과 파일 속성
- [디렉터리 구조와 주요 경로 (FHS)](../fhs-paths.md)
- [파티션 (MBR·GPT)](../../disk-volume/partitions.md) — 파티션 시작 위치를 찾아 슈퍼블록 오프셋을 잡는 법
- [Linux 의 시각 값](../../value-decoding/time-values.md) — epoch 초와 나노초 일반
- [UID·GID 와 사용자 이름 잇기](../../value-decoding/uid-gid.md) — 아이노드에는 숫자 UID 만 있음
- [지운 파일 되살리기](../../../03-techniques/analysis/file-recovery.md), [타임라인 만들기](../../../03-techniques/analysis/timeline.md)
- [시각을 조작했나](../../../04-scenarios/insider/time-manipulation.md), [흔적을 지웠나](../../../04-scenarios/insider/anti-forensics.md)

## 참고 문헌

1. Linux kernel, Documentation/filesystems/ext4 (about.rst, overview.rst, blocks.rst, blockgroup.rst). https://github.com/torvalds/linux/tree/master/Documentation/filesystems/ext4
2. Linux kernel, Documentation/filesystems/ext4/super.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/super.rst
3. Linux kernel, Documentation/filesystems/ext4/inodes.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inodes.rst
4. Linux kernel, Documentation/filesystems/ext4/directory.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/directory.rst
5. Linux kernel, Documentation/filesystems/ext4/journal.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/journal.rst
6. e2fsprogs, misc/mke2fs.conf.in (master, v1.46.5, v1.47.0 태그). https://github.com/tytso/e2fsprogs/blob/master/misc/mke2fs.conf.in
7. e2fsprogs, debugfs/debugfs.8.in. https://github.com/tytso/e2fsprogs/blob/master/debugfs/debugfs.8.in
8. util-linux, sys-utils/mount.8.adoc. https://github.com/util-linux/util-linux/blob/master/sys-utils/mount.8.adoc
9. Linux kernel, 커밋 6c0912739699 "ext4: wipe ext4_dir_entry2 upon file deletion" (Linux 5.13). https://github.com/torvalds/linux/commit/6c0912739699d8e4b6a87086401bf3ad3c59502d
10. Canonical subiquity, subiquity/server/controllers/storage.py (ubuntu/noble 가지). https://github.com/canonical/subiquity/blob/ubuntu/noble/subiquity/server/controllers/storage.py
11. Anaconda, data/product.d/rhel.conf (rhel-9 가지). https://github.com/rhinstaller/anaconda/blob/rhel-9/data/product.d/rhel.conf
12. Anaconda, data/anaconda.conf (rhel-9 가지). https://github.com/rhinstaller/anaconda/blob/rhel-9/data/anaconda.conf
13. e2fsprogs, misc/dumpe2fs.8.in. https://github.com/tytso/e2fsprogs/blob/master/misc/dumpe2fs.8.in
