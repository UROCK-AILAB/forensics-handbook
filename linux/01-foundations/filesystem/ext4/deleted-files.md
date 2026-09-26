---
title: "지운 파일이 남기는 것"
parent: "ext4"
grand_parent: "기반 · 파일 시스템"
nav_order: 60
---

# 지운 파일이 남기는 것 (Deleted Files)

ext4 에서 파일을 지우면 이름·데이터 위치·크기는 지워지지만, 아이노드의 소유자·권한·시각과 데이터 블록의 내용은 덮어쓸 때까지 남고, 지우기 전 메타데이터의 사본이 저널에 남을 수 있습니다.

## 지울 때 커널이 하는 일

파일 삭제는 두 단계로 나뉩니다. 먼저 디렉터리에서 이름을 빼고, 그 결과 아이노드를 가리키는 이름이 하나도 남지 않으면 아이노드와 블록을 풉니다. 커널의 `ext4_evict_inode` 는 링크 수가 0 이 아닌 아이노드를 풀지 않고 그대로 둡니다[1]. 그래서 하드 링크가 여럿인 파일은 이름 하나를 지워도 아이노드·블록·내용이 모두 살아 있고, 달라지는 것은 지운 이름이 있던 디렉터리 항목뿐입니다.

이름을 뺄 때 `ext4_generic_delete_entry` 는 지울 항목 앞에 다른 항목이 있으면 앞 항목의 `rec_len` 을 늘려 지울 항목 자리를 덮고, 지울 항목 영역 전체를 0 으로 채웁니다. 블록의 첫 항목이면 `rec_len` 만 두고 아이노드 번호와 나머지를 0 으로 채웁니다[4]. 이 0 채우기는 Linux 5.13 에 들어간 변경이고, 해시 트리로 바꾸거나 노드를 나눌 때 옮긴 항목 자리도 같은 방식으로 지웁니다[5]. 5.13 전 커널에서는 앞 항목의 `rec_len` 안쪽 빈 공간에 지운 이름이 남아 있을 수 있습니다. 항목 구조와 옛 커널에서 지운 이름을 읽는 방법은 [디렉터리 항목과 해시 트리](directory-htree.md) 에서 다룹니다.

마지막 이름까지 사라지고 파일을 연 프로세스도 없으면 커널은 아이노드를 풉니다. 순서는 아래와 같습니다[1][2][3].

1. 빠른 심볼릭 링크 (fast symlink) 면 `i_block` 에 들어 있던 대상 경로를 0 으로 채웁니다.
2. `i_size` 를 0 으로 만들고 블록을 모두 해제합니다. 완전히 해제한 익스텐트는 물리 시작 블록과 `ee_len` 을 0 으로 만들고 헤더의 `eh_entries` 를 줄입니다. 트리가 모두 비면 아이노드 안 헤더의 `eh_depth` 를 0 으로, `eh_max` 를 아이노드 안 최대 개수로 되돌립니다.
3. 확장 속성 참조를 지우고 고아 기록을 뺀 뒤, `i_dtime` 에 현재 시각(초)을 넣습니다.
4. 아이노드 비트맵에서 그 아이노드의 비트를 끄고 그룹 서술자의 빈 아이노드 수를 늘립니다.

4 번에서 커널은 아이노드 테이블의 아이노드 기록 자체를 0 으로 채우지 않습니다[2]. 블록도 비트맵에서 빈 것으로 표시할 뿐이라서[9], 내용은 새 파일이 그 블록을 받아 덮어쓸 때까지 남습니다. `chattr` 의 파일 속성 `s`·`u` 로 안전 삭제나 복구 보존을 요청해도 ext2·ext3·ext4 는 지키지 않습니다[13]. 아이노드 플래그 표에도 `EXT4_SECRM_FL`(0x1) 과 `EXT4_UNRM_FL`(0x2) 은 "구현되지 않음" 으로 적혀 있습니다[6].

### 자리별로 남는 것

| 자리 | 지운 뒤 상태 | 근거 |
|---|---|---|
| 디렉터리 항목 (이름·아이노드 번호) | Linux 5.13 이상은 0 으로 채움. 그 전에는 빈 공간에 남을 수 있음 | [4][5] |
| 아이노드 비트맵 비트 | 꺼짐. 아이노드 번호는 언제든 다시 쓰일 수 있음 | [2][16] |
| 아이노드 `i_mode`·`i_uid`·`i_gid`·`i_crtime`·`i_atime` | 남음(새 파일이 그 아이노드를 받기 전까지) | [1][2][16] |
| `i_links_count` | 0 | [1] |
| `i_size` | 0 | [1] |
| `i_dtime` | 아이노드를 푼 시각(초) | [1] |
| `i_ctime`·`i_mtime` 과 나노초 필드 | 지운 시각으로 바뀜. 이름을 뺄 때 ctime 을, 블록을 해제할 때 ctime·mtime 을 현재 시각으로 씀 | [1][4][16] |
| 아이노드 안 익스텐트 | 해제한 익스텐트의 물리 블록·길이가 0, `eh_entries` 감소 | [3] |
| 블록 비트맵 비트 | 꺼짐 | [9] |
| 데이터 블록 내용 | 덮어쓸 때까지 남음. 카빙 대상 | [9][18] |
| 저널 | 지우기 전 트랜잭션이 기록한 아이노드 테이블·디렉터리 블록 사본이 남을 수 있음 | [5][10][18] |

익스텐트 코드는 해제한 익스텐트의 논리 시작 블록 `ee_block` 은 지우지 않고, 뿌리가 인덱스인 트리에서 인덱스 항목을 뺄 때도 항목 수만 줄이고 그 항목이 마지막이면 자리를 옮기지 않습니다[3]. 그래서 트리 깊이가 1 이상이던 파일은 아이노드 안에 잎 블록 번호가 남아 있을 가능성이 있습니다. Fairbanks 는 2012 년 발표에서 "아이노드 안 익스텐트가 0 이 되는지는 익스텐트 트리가 만들어졌는지에 달렸고, 익스텐트 인덱스 노드는 0 이 되지 않는다" 고 정리했습니다[17]. 익스텐트 구조 자체는 [아이노드와 익스텐트](inode-extent.md) 를 봅니다.

## 고아 아이노드 (열린 채로 지운 파일)

프로세스가 연 채로 지운 파일은 이름이 없고 링크 수가 0 인데도 살아 있습니다. 이런 아이노드를 고아 (orphan) 라고 하고, 시스템이 갑자기 꺼지면 다음 마운트 때 정리할 수 있도록 파일 시스템이 목록으로 적어 둡니다[8].

| 방식 | 기록 위치 | 읽는 법 |
|---|---|---|
| 옛 방식 (`orphan_file` 기능 꺼짐) | 슈퍼블록 `s_last_orphan` 이 목록의 첫 아이노드를 가리키고, 각 아이노드의 `i_dtime` 필드에 목록의 다음 고아 아이노드 번호가 들어감. 0 이면 목록 끝 | [6][8] |
| `orphan_file` 기능 (COMPAT_ORPHAN_FILE) | 슈퍼블록 `s_orphan_file_inum` 이 가리키는 특수 아이노드의 블록마다 `__le32` 아이노드 번호 배열. 블록 끝에서 8 바이트 앞에 `ob_magic` `0x0b10ca04`, 4 바이트 앞에 `ob_checksum` | [8] |

`orphan_file` 기능이 켜진 파일 시스템은 쓰기 가능으로 마운트된 동안 슈퍼블록에 `RO_COMPAT_ORPHAN_PRESENT` 를 켜 두고, 정상으로 해제할 때 끕니다[8]. 이미지에서 이 기능 비트가 켜져 있으면 정상 해제 전에 뜬 이미지일 가능성이 있고, 고아 파일에 쓸 만한 항목이 있을 수 있습니다. 옛 방식에서는 `i_dtime` 이 시각이 아니라 작은 정수(아이노드 번호)로 보이는 아이노드가 고아 목록에 걸린 것일 가능성이 있습니다[6][8]. 어느 기능이 켜졌는지는 [슈퍼블록과 블록 그룹](superblock-block-group.md) 의 기능 비트로 확인합니다.

라이브 시스템에서는 열린 채로 지운 파일의 내용을 프로세스의 파일 서술자로 읽을 수 있고, 이 방법은 [실행 중인 프로세스](../../../02-artifacts/execution/proc.md) 에서 다룹니다.

## 읽는 법

### debugfs 로 한 번

debugfs 는 장치뿐 아니라 파일 시스템 이미지 파일도 열 수 있고, `-w` 를 주지 않으면 읽기 전용으로 엽니다[12]. `-R` 로 명령 하나만 실행할 수 있습니다[12]. 아래 명령은 원본 장치가 아니라 이미지 사본에 씁니다.

```
debugfs -R 'stat <12>' ext4.img          # 아이노드 내용(crtime·dtime 포함)
debugfs -R 'testi <12>' ext4.img         # 아이노드 비트맵에서 쓰는 중인지
debugfs -R 'imap <12>' ext4.img          # 아이노드 테이블 안 위치
debugfs -R 'ls -d /home/user1' ext4.img  # 지운 항목까지 목록(5.13 전 커널에서 지운 이름)
debugfs -R 'orphan_inodes' ext4.img      # 고아 아이노드 목록
debugfs -R 'icheck 542753' ext4.img      # 이 블록을 쓰는 아이노드
debugfs -R 'logdump -O -b 1058 -c' ext4.img  # 이 블록을 가리키는 저널 기록(체크포인트된 옛 기록 포함)과 내용
```

(아이노드 번호·경로·블록 번호는 만든 예시)

`imap` 으로 아이노드가 든 아이노드 테이블 블록 번호를 얻고, 그 번호를 `logdump -O -b` 에 넣으면 그 블록이 저널에 기록된 트랜잭션을 볼 수 있습니다[12]. `-c` 는 그 데이터 블록의 내용까지 출력합니다[12]. 지우기 전에 기록된 사본에는 지우기 전의 `i_size` 와 익스텐트가 남아 있을 수 있습니다. 저널 블록 구조와 커밋 시각은 [저널](journal-jbd2.md) 에서 다룹니다.

debugfs 의 `lsdel`(`list_deleted_inodes`) 은 ext2 에서 지운 파일을 되찾는 데 쓰던 명령이고, ext3·ext4 에서는 아이노드를 풀 때 데이터 블록 정보가 사라지므로 쓸모가 없습니다[12]. `undel` 은 아이노드와 블록을 사용 중으로 표시하는 쓰기 명령이고 뒤에 `e2fsck` 를 반드시 돌려야 하므로[12], 증거 사본에는 쓰지 않습니다.

### 헥스로 한 번

아래는 ext4 명세[6][7]로 만든 예시입니다. 4 KiB 블록 3 개(12,000 바이트)를 쓰는 파일이 지워지기 전과 후, 아이노드 기록의 해당 바이트를 비교합니다. 오프셋은 아이노드 기록 시작 기준이고 모두 리틀 엔디언입니다.

| 오프셋 | 필드 | 지우기 전 | 지운 뒤 |
|---|---|---|---|
| 0x04 | `i_size_lo` | `E0 2E 00 00` (12,000) | `00 00 00 00` |
| 0x14 | `i_dtime` | `00 00 00 00` | `C0 A2 F4 66` (1727308480 = 2024-09-25 23:54:40 UTC) |
| 0x1A | `i_links_count` | `01 00` | `00 00` |
| 0x28 | 익스텐트 헤더 `eh_magic`·`eh_entries`·`eh_max`·`eh_depth` | `0A F3 01 00 04 00 00 00` | `0A F3 00 00 04 00 00 00` |
| 0x34 | 첫 익스텐트 `ee_block` | `00 00 00 00` | `00 00 00 00` (지우지 않는 필드) |
| 0x38 | `ee_len`·`ee_start_hi` | `03 00 00 00` | `00 00 00 00` |
| 0x3C | `ee_start_lo` | `21 48 08 00` (블록 542,753) | `00 00 00 00` |

(값은 모두 만든 예시)

지운 뒤에도 헤더의 마법 수 `0xF30A` 와 `eh_max` 는 그대로라서 이 아이노드가 익스텐트를 쓰던 파일이라는 점은 알 수 있지만, 데이터가 어느 블록에 있었는지는 이 기록만으로 알 수 없습니다. 같은 아이노드가 든 블록의 저널 사본에서 0x34~0x3F 가 0 이 아닌 값을 찾으면 지우기 전 위치를 얻습니다.

## 포렌식에서 중요한 점

**증명하는 것.** 비트맵에서 꺼진 아이노드에 0 이 아닌 `i_dtime` 과 0 인 `i_links_count` 가 있으면, 그 번호의 아이노드를 쓰던 파일이 해제됐다는 것을 보여 줍니다. 남아 있는 `i_mode`·`i_uid`·`i_gid`·`i_crtime` 으로 어떤 종류의 파일을 어느 UID 가 언제 만들었는지 알 수 있습니다. 저널 사본이나 카빙으로 되찾은 내용은 그 블록에 그 내용이 있었다는 것을 보여 줍니다.

**증명하지 못하는 것.** 아이노드 기록만으로는 지운 파일의 이름·경로를 알 수 없습니다. 디렉터리 항목에는 시각이 없고([디렉터리 항목과 해시 트리](directory-htree.md)), 5.13 이상 커널에서는 이름도 0 으로 채워집니다[5]. 누가 지웠는지도 알 수 없습니다. 지운 명령을 실행한 계정은 [셸 명령 기록](../../../02-artifacts/execution/shell-history/index.md) 이나 [감사 로그의 파일 감시](../../../02-artifacts/file-activity/auditd-watches.md) 같은 다른 기록에서 찾아야 합니다. 아이노드 번호가 다시 쓰였으면 남은 필드는 새 파일의 것이라서, 예전 파일에 대해서는 아무것도 알 수 없습니다. 비어 있는 블록에서 찾은 내용도 어느 아이노드의 것이었는지는 따로 이어 붙여야 합니다.

### 시각 해석

`i_dtime` 은 1970-01-01 UTC 기준 32 비트 초이고, 다른 시각과 달리 나노초 필드가 없습니다[6]. 커널은 이 값을 아이노드를 풀 때 넣습니다[1]. 그래서 연 채로 지운 파일이면 `i_dtime` 은 이름을 지운 때가 아니라 마지막으로 파일을 닫아 아이노드를 푼 때일 가능성이 있습니다. 갑자기 꺼져 다음 마운트 때 고아 정리로 풀린 아이노드라면 그 마운트 시각에 가까울 가능성이 있습니다. 풀기 전 고아 목록에 걸려 있는 동안 `i_dtime` 필드는 시각이 아니라 아이노드 번호입니다[6].

ext4 파일을 지운 시험(Göbel·Baier, 2018)에서는 `i_ctime_extra`·`i_mtime_extra` 가 지운 시각의 나노초로 바뀌었고 `i_atime_extra`·`i_crtime_extra` 는 바뀌지 않았습니다[16]. 따라서 지운 아이노드의 ctime·mtime 은 마지막 수정 시각이 아니라 삭제 시각에 가깝다고 보고[1], 생성 시각은 crtime 으로 읽습니다. 이름을 지우면 그 이름이 있던 디렉터리의 mtime 도 바뀝니다[20]. 네 시각이 바뀌는 조건과 나노초·epoch 비트를 푸는 법은 [시각 값](timestamps.md) 에서 다룹니다.

## 함정

- 지운 이름이 디렉터리 블록에 보이지 않는 것은 5.13 이상 커널에서 정상입니다[5]. 이미지의 커널 판은 [부팅과 종료 기록](../../../02-artifacts/system-info/boot-shutdown.md) 이나 [커널 로그](../../../02-artifacts/system-info/kernel-log.md) 로 확인합니다.
- 지운 파일 목록을 이름 기준으로만 뽑으면 5.13 이상에서는 거의 비어 나옵니다. The Sleuth Kit 는 디렉터리 항목이 가리키지 않는 미할당 아이노드를 가상 고아 디렉터리 (`$OrphanFiles`) 에 모아 보여 주므로[14][15], 이름 없는 지운 아이노드는 여기서 찾습니다.
- The Sleuth Kit 는 `i_ctime` 이 0 이 아닌 아이노드를 "쓴 적 있음" 으로 분류합니다[14]. 한 번도 쓰지 않은 아이노드와 지운 아이노드를 가를 때는 `i_dtime` 과 `i_crtime` 을 함께 봅니다.
- 기본 저널 모드 `data=ordered` 는 메타데이터만 저널에 씁니다[10]. 저널에서 되찾을 수 있는 것은 아이노드·디렉터리·비트맵 블록이고 파일 내용은 들어 있지 않습니다.
- `EXT4_IOC_CHECKPOINT` 의 `DISCARD`·`ZEROOUT` 플래그를 쓰면 체크포인트 뒤 저널 블록을 discard 하거나 0 으로 채웁니다[10]. 이렇게 비운 저널에서는 지우기 전 사본을 찾을 수 없습니다.
- `discard` 마운트 옵션을 켜면 블록을 해제할 때 장치에 discard/TRIM 명령을 보냅니다. 기본값은 꺼짐입니다[11]. 실제 시스템의 `/etc/fstab` 과 [마운트 기록](../../../02-artifacts/devices/mounts.md) 으로 이 옵션이 있었는지 확인합니다. 켜져 있었다면 SSD 에서 해제한 블록의 내용이 사라졌을 가능성이 있습니다.
- 파일 시스템이 깨끗하지 않은 원본을 마운트하면 커널이 저널을 재생하면서 장치에 씁니다[21]. 마운트 방법은 [ext4](index.md) 허브를 봅니다.

## 도구

- **debugfs** (e2fsprogs): `stat`, `testi`, `testb`, `imap`, `ls -d`, `orphan_inodes`, `icheck`, `ncheck`, `logdump`, `inode_dump`, `block_dump`[12]. 읽기 전용이 기본입니다.
- **The Sleuth Kit**: 디렉터리 블록의 빈 공간에서 지운 항목을 찾아 미할당 이름으로 보여 주고, 이름 없는 미할당 아이노드를 가상 고아 디렉터리로 모읍니다. `fsstat` 은 `s_last_orphan` 부터 `i_dtime` 을 따라가며 고아 아이노드 목록을 출력합니다[14][15].
- **저널 추출 뒤 복구**: 저널 아이노드(8 번)를 `debugfs -R 'dump <8> ./journal'` 로 파일로 뽑은 뒤 ext4magic 에 넘겨 지운 파일을 되찾는 방법도 있습니다[19].
- **아이노드 카빙**: 아이노드에는 마법 수가 없으므로 권한 값·시각 범위·익스텐트 헤더 같은 패턴을 조합해 아이노드 기록을 찾는 방법이 있습니다. AFEIC 발표에서는 슈퍼블록 없이도 아이노드를 찾았고, 저널 안 아이노드와 재포맷한 ext4 에서도 데이터를 되찾았습니다[18].

되찾는 절차 전체는 [지운 파일 되살리기](../../../03-techniques/analysis/file-recovery.md) 에서 다룹니다.

## 함께 볼 페이지

- [아이노드와 익스텐트](inode-extent.md), [디렉터리 항목과 해시 트리](directory-htree.md), [저널](journal-jbd2.md), [시각 값](timestamps.md)
- [휴지통](../../../02-artifacts/file-activity/trash.md) — 데스크톱에서 "삭제" 한 파일은 먼저 여기로 옮겨짐
- [지운 파일 되살리기](../../../03-techniques/analysis/file-recovery.md), [타임라인 만들기](../../../03-techniques/analysis/timeline.md)
- [흔적을 지웠나](../../../04-scenarios/insider/anti-forensics.md)

## 참고 문헌

1. Linux kernel, fs/ext4/inode.c (`ext4_evict_inode`, `ext4_truncate`). https://github.com/torvalds/linux/blob/master/fs/ext4/inode.c
2. Linux kernel, fs/ext4/ialloc.c (`ext4_free_inode`). https://github.com/torvalds/linux/blob/master/fs/ext4/ialloc.c
3. Linux kernel, fs/ext4/extents.c (`ext4_ext_rm_leaf`, `ext4_ext_rm_idx`, `ext4_ext_remove_space`). https://github.com/torvalds/linux/blob/master/fs/ext4/extents.c
4. Linux kernel, fs/ext4/namei.c (`ext4_generic_delete_entry`, `__ext4_unlink`). https://github.com/torvalds/linux/blob/master/fs/ext4/namei.c
5. Linux kernel, 커밋 6c0912739699 "ext4: wipe ext4_dir_entry2 upon file deletion" (Linux 5.13). https://github.com/torvalds/linux/commit/6c0912739699d8e4b6a87086401bf3ad3c59502d
6. Linux kernel, Documentation/filesystems/ext4/inodes.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inodes.rst
7. Linux kernel, Documentation/filesystems/ext4/ifork.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/ifork.rst
8. Linux kernel, Documentation/filesystems/ext4/orphan.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/orphan.rst
9. Linux kernel, Documentation/filesystems/ext4/bitmaps.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/bitmaps.rst
10. Linux kernel, Documentation/filesystems/ext4/journal.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/journal.rst
11. Linux kernel, Documentation/admin-guide/ext4.rst. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/ext4.rst
12. e2fsprogs, debugfs/debugfs.8.in. https://github.com/tytso/e2fsprogs/blob/master/debugfs/debugfs.8.in
13. e2fsprogs, misc/chattr.1.in. https://github.com/tytso/e2fsprogs/blob/master/misc/chattr.1.in
14. The Sleuth Kit, tsk/fs/ext2fs.cpp. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs.cpp
15. The Sleuth Kit, tsk/fs/ext2fs_dent.cpp. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs_dent.cpp
16. Thomas Göbel, Harald Baier, "Anti-forensics in ext4: On secrecy and usability of timestamp-based data hiding", Digital Investigation 24 (2018) S111–S120 (DFRWS 2018 Europe). https://doi.org/10.1016/j.diin.2018.01.014
17. Kevin D. Fairbanks, "An Analysis of Ext4 for Digital Forensics", DFRWS 2012 USA 발표 슬라이드. https://dfrws.org/presentation/an-analysis-of-ext4-for-digital-forensics/
18. Andreas Dewald, Sabine Seufert, "AFEIC: Advanced Forensic Ext4 Inode Carving", DFRWS 2017 Europe 발표 슬라이드. https://dfrws.org/presentation/afeic-advanced-forensic-ext4-inode-carving/
19. Ali Hadi, Mariam Khader, Thomas Claflin, "Learning Linux Forensic Analysis and Why it Matters", DFRWS 워크숍 슬라이드. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
20. man-pages, man7/inode.7. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
21. util-linux, sys-utils/mount.8.adoc. https://github.com/util-linux/util-linux/blob/master/sys-utils/mount.8.adoc
