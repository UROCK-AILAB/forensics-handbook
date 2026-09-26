---
title: "시각 값"
parent: "ext4"
grand_parent: "기반 · 파일 시스템"
nav_order: 50
---

# 시각 값 (atime·mtime·ctime·crtime)

ext4 아이노드에는 접근·수정·변경·생성 시각과 삭제 시각이 들어 있고, 256 바이트 아이노드라면 앞의 네 시각은 초와 나노초로, 삭제 시각은 초로만 기록됩니다.

## 이 값을 쓰는 곳

파일과 디렉터리의 시각은 모두 아이노드에 있고 디렉터리 항목에는 시각이 없습니다([ext4 허브](index.md) 참고). 타임라인 도구가 쓰는 bodyfile 의 네 필드 `atime|mtime|ctime|crtime` 이 이 값이고[12], 지운 파일의 삭제 시각 (dtime) 도 같은 아이노드에 남습니다[1]. 파일 시스템 전체의 마운트·쓰기 시각은 [슈퍼블록과 블록 그룹](superblock-block-group.md), 트랜잭션 커밋 시각은 [저널 (jbd2)](journal-jbd2.md) 에서 다룹니다. 아이노드의 나머지 필드와 아이노드 위치 계산은 [아이노드와 익스텐트](inode-extent.md) 에 있습니다.

## 다섯 시각과 바뀌는 때

모든 시각은 1970-01-01 00:00:00 UTC 를 0 으로 하는 초이고, 현지 시각이 아닙니다[1][2].

| 시각 | 아이노드 필드 | 바뀌는 때 | 바뀌지 않는 때 |
|---|---|---|---|
| 접근 시각 (atime) | `i_atime` 0x8, `i_atime_extra` 0x8C | `execve`, `mknod`, `pipe`, `utime`, 0 바이트 넘게 `read` 할 때. `mmap` 은 바꿀 수도 있고 안 바꿀 수도 있음[2] | `noatime`·`nodiratime` 마운트, `relatime` 마운트에서 갱신 조건에 맞지 않을 때, `O_NOATIME` 로 연 파일[2][5], `A` 속성이 붙은 파일[6][14] |
| 수정 시각 (mtime) | `i_mtime` 0x10, `i_mtime_extra` 0x88 | `mknod`, `truncate`, `utime`, 0 바이트 넘게 `write` 할 때. 디렉터리는 그 안에 파일을 만들거나 지울 때[2] | 소유자·그룹·링크 수·모드만 바꿀 때[2] |
| 변경 시각 (ctime) | `i_ctime` 0xC, `i_ctime_extra` 0x84 | 쓰기, 그리고 소유자·그룹·링크 수·모드 같은 아이노드 정보를 바꿀 때[2] | 읽기만 할 때 |
| 생성 시각 (crtime) | `i_crtime` 0x90, `i_crtime_extra` 0x94 | 파일을 만들 때 정해지고 그 뒤로 바뀌지 않음[2] | 내용·속성 변경 |
| 삭제 시각 (dtime) | `i_dtime` 0x14 | 링크가 모두 없어지고 마지막으로 연 곳도 닫혀 커널이 아이노드를 풀 때, 그 순간의 실시간 초[4] | 지워지지 않은 파일 |

오프셋은 아이노드 시작 기준이고 모든 값은 리틀 엔디언입니다[1]. `utimensat`·`futimens` 호출로는 atime(`times[0]`)과 mtime(`times[1]`) 두 값만 나노초까지 정할 수 있고, ctime 을 넘기는 자리는 없습니다[7]. ctime 은 쓰기나 아이노드 정보 변경 때 커널이 정합니다[2].

생성 시각은 `stat` 구조체에는 없고 `statx` 의 `stx_btime` 으로만 나옵니다[2]. `statx` 는 Linux 4.11, glibc 2.28 부터 있고[3], ext4 는 `STATX_BTIME` 을 요청받으면 `i_crtime` 이 아이노드 안에 들어 있을 때 그 값을 돌려줍니다[4]. dtime 은 `stat()` 으로 볼 수 없고 debugfs 로 봅니다[1].

## 저장 형식

아이노드 앞 128 바이트에는 ctime·atime·mtime·dtime 네 필드가 부호 있는 32비트 초로 들어 있고, 이것만으로는 2038년 1월에 넘칩니다[1]. 아이노드 기록 크기(`s_inode_size`)가 128 바이트보다 크고 `i_extra_isize` 가 해당 `_extra` 필드까지 덮으면, ctime·atime·mtime 에 32비트 `_extra` 필드가 더해집니다[1]. `_extra` 필드의 하위 2비트는 초를 34비트로 늘리는 epoch 비트이고, 상위 30비트는 나노초입니다[1]. 그래서 2446년 5월까지 표현할 수 있습니다[1]. crtime 은 `i_crtime` 과 `i_crtime_extra` 로 같은 방식이고, dtime 은 늘어나지 않아 초 단위 32비트뿐입니다[1].

| `_extra` 하위 2비트 | 32비트 초의 최상위 비트 | 풀어낸 초의 범위 | 날짜 범위(UTC) |
|---|---|---|---|
| 00 | 1 | -0x80000000 ~ -0x00000001 | 1901-12-13 ~ 1969-12-31 |
| 00 | 0 | 0x000000000 ~ 0x07fffffff | 1970-01-01 ~ 2038-01-19 |
| 01 | 1 | 0x080000000 ~ 0x0ffffffff | 2038-01-19 ~ 2106-02-07 |
| 01 | 0 | 0x100000000 ~ 0x17fffffff | 2106-02-07 ~ 2174-02-25 |
| 10 | 1 | 0x180000000 ~ 0x1ffffffff | 2174-02-25 ~ 2242-03-16 |
| 10 | 0 | 0x200000000 ~ 0x27fffffff | 2242-03-16 ~ 2310-04-04 |
| 11 | 1 | 0x280000000 ~ 0x2ffffffff | 2310-04-04 ~ 2378-04-22 |
| 11 | 0 | 0x300000000 ~ 0x37fffffff | 2378-04-22 ~ 2446-05-10 |

풀어내는 식은 "32비트 초를 부호 있는 수로 읽은 값 + 2^32 × epoch 비트" 입니다[1]. 나노초는 `_extra` 값을 오른쪽으로 2비트 밀어서 얻습니다[1][10].

아이노드가 128 바이트이면 `_extra` 필드와 crtime 이 없어서 초 단위 네 시각만 남습니다[1]. `mke2fs.conf` 의 기본 아이노드 크기는 256 바이트이고, `hurd` 유형은 128 바이트입니다[8]. ext2·ext3 은 나노초를 쓰지 않고, ext4 는 Linux 2.6.23 부터 나노초를 씁니다[2].

64비트 커널은 1901~1970 사이 날짜에 epoch 비트를 11 로 잘못 쓰는 오래된 버그가 있고, 커널 3.12·e2fsprogs 1.42.8 까지는 고쳐지지 않은 상태였습니다[1]. 1970 년 이전 날짜가 들어간 파일은 epoch 비트가 11 인지 보고, 위 표 대로 풀었을 때 2310 년 이후로 나오면 이 경우일 가능성이 있습니다.

## 헥스로 읽기

아래는 명세로 만든 예시 바이트이고, 실제 데이터 값이 아닙니다. 256 바이트 아이노드의 0x10(`i_mtime`)과 0x88(`i_mtime_extra`)이 이렇다고 합니다.

```text
0x10: 80 99 66 66   → i_mtime       = 0x66669980
0x88: 54 34 6f 1d   → i_mtime_extra = 0x1D6F3454
```

`i_mtime_extra` 의 하위 2비트는 `00` 이라 epoch 비트는 0 이고, 0x1D6F3454 를 2비트 밀면 123456789 나노초입니다. 0x66669980 은 1718000000 초이므로 mtime 은 2024-06-10 06:13:20.123456789 UTC 입니다.

최상위 비트가 켜진 초 값은 epoch 비트에 따라 뜻이 크게 바뀝니다. 역시 만든 예시입니다.

```text
0x08: 00 00 00 8a   → i_atime       = 0x8A000000
0x8C: 01 94 35 77   → i_atime_extra = 0x77359401
```

0x8A000000 을 부호 있는 32비트로 읽으면 -1979711488 입니다. epoch 비트가 `01` 이므로 2^32 를 더해 2315255808 초가 되고, 나노초는 0x77359401 을 2비트 밀어 500000000 이라 atime 은 2043-05-14 22:36:48.5 UTC 입니다. 같은 초 값에 epoch 비트가 `00` 이면 1907-04-08 16:08:32 UTC 가 됩니다.

debugfs 의 `stat` 은 아이노드 내용을 crtime·dtime 까지 보여 주고, `inode_dump` 는 아이노드를 헥스로 출력합니다[1][9]. 도구가 보여 준 시각이 의심스러우면 `inode_dump` 로 위 방식대로 직접 풀어 비교하면 됩니다.

## 포렌식에서 중요한 점

### 증명하는 것

- 기록될 때의 커널 시계를 기준으로 한 마지막 수정 시각(mtime), 마지막 아이노드 변경 시각(ctime), 생성 시각(crtime)
- 조건이 맞을 때의 마지막 접근 시각(atime). 아래 relatime 설명 참고
- 아이노드를 푼 시각(dtime, 초 단위). 지운 파일에서 무엇이 남는지는 [지운 파일이 남기는 것](deleted-files.md) 에서 다룹니다

### 증명하지 못하는 것

- 접근이 없었다는 것. relatime·noatime·lazytime 마운트나 `A` 속성이 있으면 읽어도 atime 이 그대로이거나 디스크에 늦게 적힙니다[5][6]
- 시계가 맞았다는 것. 모든 값은 그때 커널 시계의 값일 뿐입니다
- mtime·atime 이 실제 사건 시각이라는 것. 두 값은 `utimensat` 으로 원하는 값을 넣을 수 있습니다[7]
- 누가 바꿨는지. 시각에는 사용자 정보가 없습니다

### atime 갱신 규칙 (relatime·lazytime)

Linux 2.6.30 부터 커널은 `noatime` 을 주지 않으면 기본으로 `relatime` 처럼 동작합니다[5]. `relatime` 은 기존 atime 이 mtime 이나 ctime 보다 이르거나 같을 때만 atime 을 바꾸고, 기존 atime 이 하루보다 오래됐으면 항상 바꿉니다[5]. 그래서 atime 은 "마지막으로 읽은 시각" 이 아니라 "수정 뒤 처음 읽은 시각이나 하루 단위로 갱신된 시각" 에 가깝습니다. 예전처럼 매번 바꾸려면 `strictatime` 을 줘야 하고, `noatime` 은 `nodiratime` 까지 포함합니다[5].

`lazytime` 을 주면 시각을 메모리의 아이노드에서만 바꾸고, 시각과 무관한 아이노드 변경이 있을 때, `fsync`·`syncfs`·`sync` 를 부를 때, 지우지 않은 아이노드가 메모리에서 밀려날 때, 디스크에 쓴 지 24시간이 넘었을 때에만 디스크에 적습니다[5]. 이런 파일 시스템의 이미지에서는 디스크의 시각이 실제 마지막 시각보다 최대 24시간 늦을 수 있습니다.

실제 시스템에 어떤 옵션이 걸렸는지는 `/etc/fstab` 에서, 라이브 시스템이면 `/proc/mounts` 에서 확인합니다[5]. 파일 하나의 `A` 속성은 아이노드 `i_flags` 의 `0x80`(`EXT4_NOATIME_FL`) 비트입니다[1][14].

### 지우기·조작과 시각

ext4 에서 파일을 지우는 시험에서는 `i_ctime_extra`·`i_mtime_extra` 가 지운 순간의 나노초로 바뀌었고 `i_atime_extra`·`i_crtime_extra` 는 그대로였습니다[13]. crtime 과 atime 이 지운 뒤에도 남을 수 있다는 뜻입니다.

나노초 필드 30비트에는 아무 값이나 들어갈 수 있어서 네 `_extra` 필드에 데이터를 숨길 수 있습니다[13]. epoch 비트까지 쓰면 2038 년 이후 날짜가 되어 눈에 띄고, 상위 30비트만 쓰고 암호화한 시험에서는 정상 파일의 나노초 하위 10비트 분포와 구별되지 않았습니다[13]. 아이노드를 직접 고치면 아이노드 체크섬(metadata checksum)이 내용과 맞지 않게 되고, 이를 감추려면 체크섬을 다시 계산해야 합니다[13]. 체크섬이 맞지 않는 아이노드는 직접 편집한 흔적일 가능성이 있습니다.

조작을 찾을 때는 있을 수 없는 순서를 봅니다. atime·mtime 이 crtime 보다 앞서거나 ctime·mtime 이 crtime 뒤 몇 나노초밖에 안 되는 경우가 그렇습니다[13]. 백업이 있으면 같은 파일의 시각을 비교하고, 운영체제 파일이라면 같이 설치된 파일들의 시각 순서와 비교합니다[13]. 시각 조작 조사 전체 흐름은 [시각을 조작했나](../../../04-scenarios/insider/time-manipulation.md) 에서 다룹니다.

## 함정

- dtime 필드가 작은 정수면 시각이 아닐 수 있습니다. `orphan_file` 기능이 없는 파일 시스템에서는 열린 채로 지운 아이노드(고아 아이노드)의 dtime 필드에 다음 고아 아이노드 번호가 들어가고, 슈퍼블록의 `s_last_orphan` 이 첫 고아를 가리킵니다[1].
- `i_flags` 에 `EA_INODE` 가 켜진 아이노드는 확장 속성 값을 담는 아이노드입니다. 이 아이노드의 `i_atime` 에는 값의 체크섬, `i_ctime` 에는 참조 횟수 하위 32비트, `i_mtime` 에는 속성을 가진 아이노드 번호가 들어가므로 시각으로 읽으면 안 됩니다[1].
- The Sleuth Kit 의 ext4 코드는 초 필드를 부호 없는 32비트로 읽고 epoch 비트를 초에 더하지 않으며, 나노초만 `_extra` 를 2비트 밀어 구합니다[10]. 그래서 1970-01-01 ~ 2106-02-07 밖의 시각은 다르게 나옵니다. TSK 4.4.2 로 시험했을 때는 `istat` 이 2038 년 이후 시각을 잘못 풀었습니다[13].
- 수집 도구가 초 단위만 남기는 경우가 있습니다. UAC 는 `statx` 도구를 쓸 수 없고 GNU `stat` 이 있으면 `stat -c "0|%N|%i|%A|%u|%g|%s|%X|%Y|%Z|%W"` 로 bodyfile 을 만들고, 이때 시각은 초 단위 정수입니다[11]. 나노초가 필요하면 이미지에서 아이노드를 직접 읽습니다.
- plaso 의 bodyfile 파서는 읽은 시각에 현지 시각 표시(`is_local_time`)를 붙입니다[12]. 분석할 때 UTC 가 아닌 시간대를 주면 bodyfile 시각이 그만큼 옮겨질 가능성이 있으니, UTC 로 맞춰 돌리고 결과를 원래 epoch 값과 한 번 비교합니다.
- 사람이 읽는 형식으로 바꿀 때는 UTC 로 적고, 실제 시스템의 시간대는 [호스트 이름·시간대·로캘](../../../02-artifacts/system-info/hostname-timezone.md) 에서 따로 확인해 보고서에 함께 씁니다.
- inode(7) 매뉴얼에는 생성 시각을 "대부분의 Linux 파일 시스템이 아직 지원하지 않는다" 고 적혀 있지만[2], ext4 커널 코드는 `statx` 요청에 crtime 을 돌려줍니다[4]. 매뉴얼 문장만 보고 ext4 에 생성 시각이 없다고 판단하지 않습니다.

## 도구

| 도구 | 보여 주는 것 |
|---|---|
| debugfs `stat`, `inode_dump` | 다섯 시각(crtime·dtime 포함), 아이노드 헥스[1][9] |
| TSK `istat` | ext4 이면 atime·mtime·ctime·crtime 과 나노초. epoch 비트는 반영하지 않음[10] |
| GNU `stat`, `statx` | 마운트된 파일의 atime·mtime·ctime·생성 시각. dtime 은 없음[2][3] |
| UAC bodyfile | 라이브 시스템 전체의 네 시각(`stat -c` 로 만들면 초 단위)[11] |
| plaso bodyfile·filestat 파서 | bodyfile 이나 이미지에서 시각 이벤트 생성[12] |

여러 시각을 한 줄로 엮는 방법은 [타임라인 만들기](../../../03-techniques/analysis/timeline.md), epoch 초와 나노초 일반은 [Linux 의 시각 값](../../value-decoding/time-values.md) 에서 다룹니다. XFS 와 Btrfs 의 생성 시각은 [XFS](../xfs.md), [Btrfs](../btrfs.md) 를 봅니다.

## 참고 문헌

1. Linux kernel, Documentation/filesystems/ext4/inodes.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inodes.rst
2. man-pages, man7/inode.7. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
3. man-pages, man2/statx.2. https://github.com/mkerrisk/man-pages/blob/master/man2/statx.2
4. Linux kernel, fs/ext4/inode.c (`ext4_evict_inode`, `ext4_getattr`). https://github.com/torvalds/linux/blob/master/fs/ext4/inode.c
5. util-linux, sys-utils/mount.8.adoc. https://github.com/util-linux/util-linux/blob/master/sys-utils/mount.8.adoc
6. e2fsprogs, misc/chattr.1.in. https://github.com/tytso/e2fsprogs/blob/master/misc/chattr.1.in
7. man-pages, man2/utimensat.2. https://github.com/mkerrisk/man-pages/blob/master/man2/utimensat.2
8. e2fsprogs, misc/mke2fs.conf.in. https://github.com/tytso/e2fsprogs/blob/master/misc/mke2fs.conf.in
9. e2fsprogs, debugfs/debugfs.8.in. https://github.com/tytso/e2fsprogs/blob/master/debugfs/debugfs.8.in
10. The Sleuth Kit, tsk/fs/ext2fs.cpp (develop). https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs.cpp
11. UAC, artifacts/bodyfile/bodyfile.yaml, lib/setup_tools.sh. https://github.com/tclahr/uac/blob/main/artifacts/bodyfile/bodyfile.yaml , https://github.com/tclahr/uac/blob/main/lib/setup_tools.sh
12. plaso, plaso/parsers/bodyfile.py, plaso/parsers/filestat.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/bodyfile.py , https://github.com/log2timeline/plaso/blob/main/plaso/parsers/filestat.py
13. Thomas Göbel, Harald Baier, "Anti-forensics in ext4: On secrecy and usability of timestamp-based data hiding", Digital Investigation 24 (2018) S111–S120 (DFRWS 2018 Europe). https://doi.org/10.1016/j.diin.2018.01.014
14. man-pages, man2/ioctl_iflags.2. https://github.com/mkerrisk/man-pages/blob/master/man2/ioctl_iflags.2
