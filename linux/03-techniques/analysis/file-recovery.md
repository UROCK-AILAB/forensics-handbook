---
title: "지운 파일 되살리기"
parent: "기법 · 분석"
nav_order: 980
---

# 지운 파일 되살리기 (File Recovery)

디스크 이미지에서 지운 파일의 이름·메타데이터·내용을 따로따로 찾아 다시 잇고, 되살린 것마다 어디서 나왔는지 적어 두는 절차입니다.

## 언제 쓰나

지운 문서·도구·로그를 되찾아야 할 때, 또는 어떤 파일이 한때 있었는지를 보여야 할 때 씁니다. Linux 에는 NTFS 의 MFT 처럼 이름·시각·데이터 위치를 한 기록에 모아 둔 구조가 없습니다. 이름은 디렉터리 항목에, 소유자·시각·데이터 위치는 아이노드에, 내용은 데이터 블록에 따로 있고, 파일을 지울 때 이 셋이 서로 다른 정도로 지워집니다. 그래서 "파일 하나를 되살린다" 기보다 이름·아이노드·내용을 각각 찾아 맞춰 보는 작업이 됩니다.

먼저 볼륨의 파일 시스템을 확인합니다. 기준 두 배포판은 설치 기본값부터 다릅니다.

| 배포판 | 설치 기본 파일 시스템 | 근거 |
|---|---|---|
| Ubuntu 24.04 LTS | ext4 (`/` 와 `/boot`) | [1] |
| RHEL 9 | XFS (`file_system_type = xfs`) | [2] |

같은 "지운 파일 복구" 라도 Ubuntu 서버에서는 ext4 도구를, RHEL 서버에서는 XFS 도구를 먼저 꺼내야 합니다. 설치 뒤에 볼륨을 따로 만들었을 수 있으므로 검체의 `/etc/fstab` 과 [마운트 기록](../../02-artifacts/devices/mounts.md) 으로 볼륨마다 확인합니다.

## 절차

1. **원본에는 쓰지 않습니다.** [디스크 이미징](../acquisition/disk-imaging.md) 으로 뜬 사본에서만 작업합니다. debugfs 는 `-w` 를 주지 않으면 읽기 전용으로 열고, 손상이 심하면 `-c`(catastrophic) 로 비트맵을 읽지 않고 읽기 전용으로 강제해 엽니다[6]. debugfs 의 `undel` 은 아이노드와 블록을 사용 중으로 표시하는 쓰기 명령이고 뒤에 e2fsck 를 돌려야 하므로[6], 증거 사본에서 쓰지 않습니다. 이미지를 마운트하면 저널을 재생해 흔적이 바뀔 수 있으니, 마운트가 필요하면 [저널](../../01-foundations/filesystem/ext4/journal-jbd2.md) 의 `noload` 설명을 먼저 봅니다.

2. **파일 시스템 종류와 커널 판을 확인합니다.** ext4 는 Linux 5.13 부터 파일을 지울 때 디렉터리 항목의 `rec_len` 을 뺀 모든 필드를 0 으로 채웁니다[3]. 그래서 커널 판에 따라 디렉터리 블록에서 지운 이름을 기대할 수 있는지가 갈립니다. 커널 판은 [부팅과 종료 기록](../../02-artifacts/system-info/boot-shutdown.md) 이나 [커널 로그](../../02-artifacts/system-info/kernel-log.md) 로 확인합니다.

3. **지우지 않은 사본부터 찾습니다.** 데스크톱에서 "삭제" 한 파일은 먼저 [휴지통](../../02-artifacts/file-activity/trash.md) 으로 옮겨지고, 편집기가 남기는 사본은 [편집기 흔적](../../02-artifacts/file-activity/editor-artifacts.md) 에, 작업 파일은 [임시 폴더와 메모리 파일 시스템](../../02-artifacts/file-activity/tmp-shm.md) 에 남을 수 있습니다. Btrfs 는 스냅숏과 옛 세대에 지우기 전 판이 남습니다([Btrfs](../../01-foundations/filesystem/btrfs.md)). 이런 곳에서 찾은 파일은 이름·시각이 온전하므로 미할당 영역을 뒤지기 전에 확인합니다.

4. **지운 이름을 찾습니다.** The Sleuth Kit 의 `fls -r -d -p` 는 지운 항목만 전체 경로로 보여 줍니다[7]. ext4 에서 5.13 이상 커널이면 이 결과가 거의 비어 나오는 것이 정상이고, 지운 이름은 저널에 남은 옛 디렉터리 블록 사본에서 찾습니다[3]. `jls` 로 저널 블록 목록을 뽑고, 원래 디렉터리 블록 번호가 붙은 `FS Block` 줄을 골라 `jcat` 으로 그 저널 블록을 꺼냅니다[7][8]. debugfs 에서는 `logdump -O -b 블록번호 -c` 로 같은 블록의 옛 기록을 한 번에 봅니다[6].

5. **지운 아이노드를 찾습니다.** `ils` 는 옵션 없이 쓰면 지운 파일의 아이노드만 보여 주고, `-p` 는 이름이 가리키지 않는 미할당 아이노드(고아)를, `-O` 는 지웠지만 아직 열려 있거나 실행 중이던 아이노드를 보여 줍니다[7]. ext4 는 지울 때 익스텐트 항목의 물리 블록 번호를 0 으로 만들므로[16], 데이터 위치는 저널에 남은 옛 아이노드 테이블 블록 사본에서 찾습니다. 아이노드가 든 블록 번호는 debugfs `imap` 으로 얻어 4 번과 같은 방법으로 저널에서 그 블록의 옛 사본을 찾습니다([지운 파일이 남기는 것](../../01-foundations/filesystem/ext4/deleted-files.md)).

6. **내용을 꺼냅니다.** 아이노드에 데이터 위치가 남아 있으면 `icat` 으로 꺼냅니다. `-r` 은 지운 파일이면 복구 기법을 쓰고, `-s` 는 슬랙까지, `-h` 는 희소 파일의 구멍을 건너뜁니다[7]. 여러 파일을 한꺼번에 꺼낼 때는 `tsk_recover` 를 쓰고, 기본값이 미할당 파일만 내보내는 것이라 `-e` 를 주면 전부, `-a` 를 주면 할당 파일만 내보냅니다[7]. 저널 사본으로 옛 익스텐트를 찾았으면 그 블록을 직접 읽습니다. 블록이 지금 어느 아이노드에 할당됐는지는 `ifind -d 블록` 이나 debugfs `icheck 블록` 으로 확인합니다[6][7].

7. **위치를 모르는 내용은 카빙합니다.** `blkls` 는 기본으로 미할당 블록 내용만 이어 붙여 출력하므로[7], 이 결과를 카빙 도구에 넣으면 이미 쓰는 블록을 뺀 영역만 훑을 수 있습니다. PhotoRec 은 파일 시스템을 보지 않고 밑의 데이터를 뒤지므로 파일 시스템이 망가지거나 다시 포맷돼도 동작하고, 복구 대상 장치에는 쓰지 않습니다[9]. 480 개가 넘는 확장자(약 300 개 파일 계열)를 알아봅니다[10].

8. **되살린 파일마다 출처를 적습니다.** 이름은 저널 디렉터리 블록에서, 메타데이터는 미할당 아이노드에서, 내용은 카빙에서 나오는 식으로 한 파일의 세 요소가 서로 다른 곳에서 나올 수 있습니다. 파일마다 이름·아이노드·내용의 출처(블록 번호, 저널 블록 번호와 트랜잭션 번호, 도구와 옵션)를 따로 적어 둡니다.

아래는 3~7 단계를 ext4 이미지 사본에 적용한 모양입니다. 이미지 이름·아이노드·블록 번호는 모두 만든 예시입니다.

```
fls -r -d -p ext4.img                      # 지운 이름(전체 경로)
ils -p ext4.img                            # 이름 없는 미할당 아이노드
jls ext4.img                               # 저널 블록 목록
jcat ext4.img 8 1234 | xxd                 # 저널 블록 1234 의 원래 바이트
debugfs -R 'imap <1573>' ext4.img          # 아이노드 1573 이 든 아이노드 테이블 블록
debugfs -R 'logdump -O -b 6291 -c' ext4.img  # 그 블록의 옛 저널 기록과 내용
icat -r ext4.img 1573 > inode1573.bin      # 아이노드로 내용 꺼내기
ifind -d 542753 ext4.img                   # 블록 542753 을 쓰는 아이노드
blkls ext4.img > unalloc.bin               # 미할당 블록만 모으기(카빙 입력)
```

`jls` 는 저널 슈퍼블록 줄과 `Unused` 줄을 빼면 블록마다 `번호:` 뒤에 `Allocated` 또는 `Unallocated` 를 붙여 `Descriptor Block (seq: N)`, `FS Block N`, `Commit Block (seq: N, … sec: 초.소수)`, `Revoke Block (seq: N)` 을 찍고, 설명 블록으로 짝을 찾지 못한 블록은 `Unallocated FS Block Unknown` 으로 찍습니다[8]. `FS Block` 뒤 숫자가 원래 파일 시스템 블록 번호이고, 줄 맨 앞 숫자가 `jcat` 에 넣을 저널 블록 번호입니다[7][8]. 커밋 시각 소수부를 읽는 주의점은 [저널](../../01-foundations/filesystem/ext4/journal-jbd2.md) 에 있습니다.

## 파일 시스템별 차이

| 파일 시스템 | 되살릴 수 있는 곳 | 먼저 볼 쪽 |
|---|---|---|
| ext4 | 저널 안 옛 아이노드·디렉터리 블록, 미할당 아이노드의 소유자·시각, 미할당 블록 내용 | [지운 파일이 남기는 것](../../01-foundations/filesystem/ext4/deleted-files.md), [저널](../../01-foundations/filesystem/ext4/journal-jbd2.md) |
| XFS | 빈 아이노드 칸에 남은 익스텐트 레코드, 로그 안 아이노드 기록 | [XFS](../../01-foundations/filesystem/xfs.md) |
| Btrfs | 스냅숏, 옛 세대 트리(백업 루트) | [Btrfs](../../01-foundations/filesystem/btrfs.md) |

XFS 에서 The Sleuth Kit 은 미할당 파일의 크기가 0 이면 데이터 포크에 남은 첫 익스텐트 레코드의 블록 수에 블록 크기를 곱해 크기를 정합니다[15]. 이렇게 꺼낸 파일은 원래 크기가 아니라 블록 크기의 배수라서 끝에 다른 내용이 붙어 있을 가능성이 있습니다. Btrfs 는 아이노드 테이블 같은 고정 자리가 없어 미할당 메타데이터를 훑는 방법이 통하지 않고, 옛 세대 트리로 들어가 파일을 꺼냅니다[14]. 옛 세대를 여는 `-T` 옵션은 FKIE 가 고친 판의 옵션이고[14], upstream The Sleuth Kit 의 `fls` 설명서에는 없습니다[7].

## 살아 있는 시스템과 메모리에서

프로세스가 연 채로 지운 파일은 링크 수가 0 이어도 아이노드가 살아 있습니다[5]. 전원이 켜져 있는 동안에는 `/proc/PID/fd/` 로 그 내용을 읽을 수 있고, 전원을 끄면 이 길은 사라집니다. UAC 는 실행 파일이 `(deleted)` 로 표시된 프로세스에 대해서만 그 실행 파일과 그 프로세스가 연 지운 파일(`/dev/`·`/proc/` 제외)과 `/dev/shm` 의 지운 파일을 복사하고, memfd 로 열린 지운 파일은 모든 프로세스에서 복사합니다[11]. 복사는 `dd ... bs=1024 count=20000` 이라 앞 20 MB 까지만 남습니다[11]. 수집 절차는 [라이브 응답 수집](../acquisition/live-response.md), `/proc` 해석은 [실행 중인 프로세스](../../02-artifacts/execution/proc.md) 에 있습니다.

메모리 이미지만 있으면 Volatility 3 의 `linux.pagecache.Files` 로 페이지 캐시에 남은 파일 목록을, `linux.pagecache.InodePages` 로 캐시된 아이노드 페이지의 내용을, `linux.pagecache.RecoverFs` 로 캐시된 파일 시스템 전체를 tar 로 꺼냅니다[12]. `RecoverFs` 는 원래 메타데이터를 옮기지 않고 수정 시각을 플러그인을 돌린 시각으로 넣으며, 절대 경로 심볼릭 링크를 상대 경로로 바꿉니다[12]. `tmpfs_only` 옵션을 주면 tmpfs 의 파일만 꺼냅니다[12]. 메모리 분석 절차는 [메모리 분석](memory-analysis.md) 에서 다룹니다.

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| The Sleuth Kit `fls`·`ils`·`icat`·`ifind`·`blkls`·`tsk_recover` | 지운 이름, 미할당·고아 아이노드, 아이노드로 내용 꺼내기, 블록에서 아이노드 찾기, 미할당 블록 모으기, 일괄 내보내기[7] |
| The Sleuth Kit `jls`·`jcat` | ext4 저널 블록 목록과 저널 블록 원래 바이트[7][8] |
| debugfs (e2fsprogs) | `imap`, `logdump`, `icheck`, `ncheck`, `dump`, `rdump`. `dump_unused` 는 0 이 아닌 바이트가 든 미사용 블록을 출력합니다[6] |
| PhotoRec | 파일 시스템을 보지 않는 카빙[9][10] |
| AFEIC | 권한·시각 범위·익스텐트 헤더 같은 패턴을 조합한 ext4 아이노드 카빙(연구 도구)[13] |
| FKIE 판 The Sleuth Kit | Btrfs 여러 장치 풀과 옛 세대[14] |
| Volatility 3 `linux.pagecache` | 메모리의 페이지 캐시에서 파일 꺼내기[12] |
| UAC | 라이브 시스템에서 지웠지만 열린 파일 복사[11] |

## 함정과 한계

- **ext4 에서 debugfs `lsdel` 결과가 비어도 지운 파일이 없는 것이 아닙니다.** 이 명령은 ext2 에서 쓰던 것이고, ext3·ext4 는 아이노드를 풀 때 데이터 블록 정보가 사라지므로 쓸모가 없습니다[6].
- **도구 설명서끼리 말이 다릅니다.** `fls` 설명서에는 "Linux 에서는 최근 지운 파일을 쉽게 되살릴 수 있다" 는 문장이 있지만[7], debugfs 설명서는 ext3·ext4 에서 데이터 블록 정보가 사라진다고 적고[6], ext4 커널 코드는 지운 익스텐트의 물리 블록 번호를 0 으로 만듭니다[16]. `fls` 문장은 ext2 시절 설명일 가능성이 있으므로 기대치를 여기에 맞추지 않습니다.
- **`icat -r` 이 ext4 에서 무엇을 하는지는 설명서에 없습니다**[7]. 결과를 저널 사본의 익스텐트나 블록 헥스와 대조합니다.
- **기본 설정의 ext4 저널에는 파일 내용이 없습니다.** 기본 `data=ordered` 는 메타데이터만 저널에 쓰고, `data=journal` 일 때만 데이터도 씁니다[4]. 저널에서는 이름과 위치를 찾고, 내용은 데이터 블록에서 찾습니다.
- **저널의 옛 사본은 덮입니다.** 저널은 돌아가며 다시 쓰이므로 오래전에 지운 파일일수록 사본이 없을 가능성이 큽니다([저널](../../01-foundations/filesystem/ext4/journal-jbd2.md)).
- **SSD 와 `discard`.** `discard` 마운트 옵션이 켜져 있었으면 해제한 블록 내용이 장치에서 사라졌을 가능성이 있습니다([지운 파일이 남기는 것](../../01-foundations/filesystem/ext4/deleted-files.md)).
- **라이브 수집의 20 MB 제한.** UAC 로 복사한 지운 실행 파일·열린 파일은 20 MB 에서 잘립니다[11].

## 결과를 어떻게 해석하나

**증명하는 것.** 되살린 내용이 이 볼륨의 미할당 영역, 저널, 옛 세대 가운데 어디에 있었다는 것을 보여 줍니다. 저널 사본에서 나온 메타데이터라면 그 블록이 커밋 블록의 `h_commit_sec` 시각쯤 그 내용으로 기록됐다는 것을 보여 줍니다[4]. 이 값은 UTC 기준 epoch 초이고, 파일을 바꾼 시각이 아니라 트랜잭션을 커밋한 시각입니다.

**증명하지 못하는 것.** 카빙으로 되찾은 파일에는 원래 이름·경로·소유자·시각이 없습니다. PhotoRec 이 파일 시스템을 보지 않는다는 점에서 곧바로 나오는 한계입니다[9]. 저널 사본에서 얻은 옛 익스텐트가 가리키는 블록은 그 뒤 다른 파일이 받아 덮어썼을 수 있으므로, 지금 그 블록에 있는 내용이 옛 파일의 것이라는 보장은 없습니다. 누가 지웠는지도 이 결과로는 알 수 없으므로 [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md) 이나 [감사 로그의 파일 감시](../../02-artifacts/file-activity/auditd-watches.md) 에서 따로 찾습니다. 아무것도 되살리지 못했다는 결과로 그 파일이 없었다고 말할 수 없습니다.

**시각.** 지운 아이노드에 남은 `i_dtime`·ctime·mtime·crtime 이 각각 언제를 가리키는지는 [지운 파일이 남기는 것](../../01-foundations/filesystem/ext4/deleted-files.md) 에, 다른 기록과 한 줄로 늘어놓는 방법은 [타임라인 만들기](timeline.md) 에 있습니다. `RecoverFs` 로 꺼낸 파일의 수정 시각은 분석한 시각이라 증거로 쓰지 않습니다[12].

보고서에는 기록이 말하는 만큼만 씁니다. 만든 예시: "ext4 볼륨의 저널 블록 1234(트랜잭션 5021, 커밋 2025-03-14 02:17:09 UTC)에 담긴 디렉터리 블록 사본에 `/home/user1/plan.odt` 항목과 아이노드 번호 1573 이 있다. 같은 저널의 아이노드 테이블 사본에 적힌 블록 542753 부터 3 블록을 읽은 내용은 ODF 문서 형식이다. 이 블록은 지금 미할당 상태이다."

## 함께 볼 페이지

- [지운 파일이 남기는 것](../../01-foundations/filesystem/ext4/deleted-files.md), [저널](../../01-foundations/filesystem/ext4/journal-jbd2.md), [ext4](../../01-foundations/filesystem/ext4/index.md), [XFS](../../01-foundations/filesystem/xfs.md), [Btrfs](../../01-foundations/filesystem/btrfs.md), [LVM 논리 볼륨](../../01-foundations/disk-volume/lvm.md)
- [디스크 이미징](../acquisition/disk-imaging.md), [라이브 응답 수집](../acquisition/live-response.md)
- [타임라인 만들기](timeline.md), [메모리 분석](memory-analysis.md)
- [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md), [랜섬웨어가 돌았나](../../04-scenarios/intrusion/ransomware.md)

## 참고 문헌

1. Canonical, subiquity (ubuntu/noble), subiquity/server/controllers/storage.py. https://github.com/canonical/subiquity/blob/ubuntu/noble/subiquity/server/controllers/storage.py
2. Red Hat, anaconda (rhel-9), data/product.d/rhel.conf. https://github.com/rhinstaller/anaconda/blob/rhel-9/data/product.d/rhel.conf
3. Linux kernel, 커밋 6c0912739699 "ext4: wipe ext4_dir_entry2 upon file deletion" (Linux 5.13). https://github.com/torvalds/linux/commit/6c0912739699d8e4b6a87086401bf3ad3c59502d
4. Linux kernel, Documentation/filesystems/ext4/journal.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/journal.rst
5. Linux kernel, Documentation/filesystems/ext4/orphan.rst. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/orphan.rst
6. e2fsprogs, debugfs/debugfs.8.in. https://github.com/tytso/e2fsprogs/blob/master/debugfs/debugfs.8.in
7. The Sleuth Kit, man/ (fls.1, ils.1, icat.1, ifind.1, blkls.1, tsk_recover.1, jls.1, jcat.1). https://github.com/sleuthkit/sleuthkit/tree/develop/man
8. The Sleuth Kit, tsk/fs/ext2fs_journal.cpp. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs_journal.cpp
9. CGSecurity, TestDisk, man/photorec.8.in. https://github.com/cgsecurity/testdisk/blob/master/man/photorec.8.in
10. CGSecurity, TestDisk README.md. https://github.com/cgsecurity/testdisk/blob/master/README.md
11. UAC, artifacts/live_response/process/deleted.yaml. https://github.com/tclahr/uac/blob/main/artifacts/live_response/process/deleted.yaml
12. Volatility 3, volatility3/framework/plugins/linux/pagecache.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/pagecache.py
13. Andreas Dewald, Sabine Seufert, "AFEIC: Advanced Forensic Ext4 Inode Carving", DFRWS 2017 Europe 발표 슬라이드. https://dfrws.org/presentation/afeic-advanced-forensic-ext4-inode-carving/
14. Jan-Niclas Hilgert, Martin Lambertz, Shujian Yang, "Forensic Analysis of Multiple Device BTRFS Configurations using The Sleuth Kit", DFRWS 발표 슬라이드. https://dfrws.org/presentation/forensic-analysis-of-multiple-device-btrfs-configurations-using-the-sleuth-kit/
15. The Sleuth Kit, tsk/fs/xfs.cpp. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/xfs.cpp
16. Linux kernel, fs/ext4/extents.c. https://github.com/torvalds/linux/blob/master/fs/ext4/extents.c
