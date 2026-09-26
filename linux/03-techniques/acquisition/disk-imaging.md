---
title: "디스크 이미징"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 920
---

# 디스크 이미징 (Disk Imaging)

Linux 저장 장치를 처음부터 끝까지 비트 단위로 떠서 해시로 묶고, 원본에도 이미지에도 쓰지 않는 방법으로 여는 절차입니다.

## 언제 쓰나

지운 파일, 할당되지 않은 영역, 파일 시스템 저널까지 보려면 파일 사본이 아니라 장치 전체의 사본이 필요합니다. 장치를 떼어 분석 PC 에 붙일 수 있으면 그대로 뜨고, 떼기 어려운 서버라면 켜진 채로 뜹니다. 켜진 시스템에서 프로세스·네트워크처럼 사라지는 값을 먼저 모으는 일은 [라이브 응답 수집](live-response.md), 수집 순서와 기록 남기기는 [조사 절차](investigation-process.md), 메모리는 [메모리 수집](memory-acquisition.md), 클라우드 디스크 스냅숏은 [클라우드 가상 머신 수집](cloud-vm.md) 에서 다룹니다.

Linux 서버는 디스크 하나가 파일 시스템 하나로 끝나지 않을 수 있습니다. LVM 논리 볼륨 (Logical Volume), md RAID, 여러 장치를 묶은 Btrfs, dm-crypt 로 암호화한 볼륨을 쓰는 서버라면, 어떤 장치를 떠야 파일 시스템이 온전히 살아나는지를 이미징 전에 정해야 합니다.

## 절차

1. **켜진 시스템이면 저장 장치 구성부터 기록합니다.** 장치·파티션·파일 시스템 종류·UUID·마운트 지점과 LVM·RAID·Btrfs 구성을 남겨 두면, 어떤 물리 장치가 어떤 볼륨의 구성원인지 나중에 맞춰 볼 수 있습니다. UAC 는 아래 명령의 결과를 남깁니다[9].

   | 알려 주는 것 | 명령 |
   |---|---|
   | 장치·파티션 트리, 파일 시스템 종류·UUID | `lsblk`, `lsblk -f`, `lsblk -J`, `blkid` |
   | 마운트 지점과 옵션 | `findmnt --ascii`, `findmnt -J` |
   | LVM 물리 볼륨·볼륨 그룹·논리 볼륨 | `pvs`, `vgs`, `lvs` |
   | md RAID 구성 | `cat /proc/mdstat`, `mdadm --detail --scan --verbose` |
   | Btrfs 하위 볼륨 | `btrfs subvolume list -a -p -c -u -q -R` (마운트 지점마다), `btrfs subvolume show` |

   LVM 구조는 [LVM 논리 볼륨](../../01-foundations/disk-volume/lvm.md), 파티션 표는 [파티션](../../01-foundations/disk-volume/partitions.md) 에서 설명합니다.

2. **암호화 볼륨이 풀려 있는지 확인합니다.** dm-crypt 는 블록 장치를 투명하게 암호화하고, 키는 16진수로 넘기거나 커널 키링 (kernel keyring) 에 있는 키를 가리키는 식으로 커널에 들어갑니다[8]. 매핑된 장치는 보통 `/dev/mapper/` 아래에 생기므로[14], 잠금이 풀린 시스템에서 이 장치를 읽으면 평문이 나오고, 그 밑의 원래 파티션을 읽으면 암호문이 나옵니다. 전원을 끄면 다시 풀 때 암호나 키가 있어야 하므로, 끄기 전에 풀린 장치를 따로 뜰지 먼저 정합니다. LUKS 머리 구조와 키 슬롯은 [LUKS 디스크 암호화](../../01-foundations/disk-volume/luks.md) 에서 다룹니다.

3. **분석 PC 에 붙인 원본 장치를 읽기 전용으로 만듭니다.** `blockdev --setro` 는 장치를 읽기 전용으로 표시하고, `blockdev --getro` 가 1 을 내면 설정된 것입니다[3]. 이미 읽기·쓰기로 마운트된 파일 시스템에는 이 설정이 곧바로 먹지 않고 다시 마운트해야 적용되므로[3], 자동 마운트가 일어나기 전에 설정합니다.

4. **이미지를 뜹니다.** 형식은 원시 (raw) 이미지와 EWF (Expert Witness Compression Format, `.E01`) 가 흔합니다.

   원시 이미지는 GNU coreutils 의 `dd` 로 뜰 수 있습니다. `conv=noerror` 는 읽기 오류가 나도 계속 읽고, `conv=sync` 는 입력 블록마다 `ibs` 크기가 되도록 뒤를 0 으로 채우며, `iflag=fullblock` 은 `read` 가 덜 채워 돌아오면 블록이 찰 때까지 다시 읽습니다[1]. `ibs` 기본값은 512바이트이고, `bs` 는 입력·출력 블록 크기를 함께 정합니다[1]. `status=progress` 는 진행 상황을 표준 오류로 내고, `conv=fsync` 나 `conv=fdatasync` 는 끝나기 직전에 출력 데이터를 실제로 디스크에 씁니다[1]. 망가져 가는 장치의 파티션을 마운트 해제한 뒤 간단히 복구하는 예는 아래와 같습니다[1].

   ```
   dd conv=noerror,sync iflag=fullblock </dev/sda1 > /mnt/rescue.img
   ```

   망가져 가는 장치에서 데이터를 최대한 건지는 기능은 GNU ddrescue 처럼 이런 상황을 위해 만든 도구에 더 많습니다[1].

   EWF 이미지는 libewf 의 `ewfacquire` 로 뜹니다. Linux 에서는 장치 파일을 직접 읽고, 사건 번호 같은 메타데이터를 이미지 안에 함께 담습니다[2]. 주요 옵션은 아래와 같습니다[2].

   | 옵션 | 뜻 | 기본값 |
   |---|---|---|
   | `-f` | EWF 형식(ewf, smart, ftk, encase1~7, encase7-v2, linen5~7, ewfx) | encase6 |
   | `-d` | MD5 말고 더 계산할 해시(sha1, sha256) | MD5 만 |
   | `-C` `-E` `-D` `-e` `-N` | 사건 번호, 증거 번호, 설명, 분석관 이름, 메모 | 각 항목 이름 |
   | `-l` | 획득 오류와 해시를 기록할 로그 파일 | 없음 |
   | `-S` | 세그먼트 파일 크기 | 1.4 GiB |
   | `-r` | 읽기 오류가 났을 때 다시 읽는 횟수 | 2 |
   | `-g` | 오류 단위로 쓸 섹터 수 | 64(대화형 입력의 기본값) |
   | `-w` | 읽기 오류 때 오류 단위 섹터를 모두 0 으로 채움(EnCase 방식) | 끔 |
   | `-P` | 섹터 크기(자동 감지를 덮어씀) | 512 |
   | `-m` / `-M` | 매체 종류(fixed, removable, optical, memory) / logical·physical | fixed / physical |
   | `-2` | 같은 내용을 두 번째 대상에도 씀 | 없음 |
   | `-R` | 안전 지점부터 이어서 획득 | 끔 |
   | `-u` | 묻지 않고 진행 | 끔 |

   아래는 만든 예시입니다. 장치 이름, 저장 경로, 사건 정보는 모두 지어낸 값입니다.

   ```
   ewfacquire -u -f encase6 -d sha256 \
     -C 2026-001 -E 001 -e examiner01 -D "web server sdb" \
     -l /mnt/evidence/case2026-001_sdb.log \
     -t /mnt/evidence/case2026-001_sdb /dev/sdb
   ```

   LVM, md RAID, 여러 장치 Btrfs 라면 풀 (pool) 에 들어간 장치를 모두 뜹니다. 데이터는 raid0, 메타데이터는 raid1 로 묶은 디스크 3개짜리 Btrfs 에서 하나가 빠지면 `mount -o degraded` 가 `missing devices(1) exceeds the limit(0), writeable mount is not allowed` 를 내고 읽기 전용으로만 붙으며, 메타데이터는 보이지만 파일을 열면 `Input/output error` 가 납니다[11]. 이런 구성에서는 파일 시스템을 보기 전에 풀의 논리 주소를 물리 주소로 옮기는 풀 분석 단계가 하나 더 필요합니다[11]. Btrfs 구조는 [Btrfs](../../01-foundations/filesystem/btrfs.md) 에서 다룹니다.

5. **해시를 계산하고 검증합니다.** `ewfacquire` 는 MD5 를 늘 계산하고 `-d` 로 SHA-1·SHA-256 을 더하며, `-l` 로그에 해시를 남깁니다[2]. `ewfverify` 는 이미지에 저장된 해시 종류를 다시 계산해 비교하고, 저장된 해시가 없으면 MD5 를 씁니다[2]. `ewfinfo` 는 획득 정보(`-i`), 매체 정보(`-m`), 읽기 오류 정보(`-e`)를 따로 보여 줍니다[2]. 원시 이미지는 coreutils 의 `sha256sum` 같은 명령으로 해시를 계산해 이미지와 함께 보관합니다[1].

6. **이미지를 읽기 전용으로 엽니다.** 파일 시스템을 마운트하기 전에 The Sleuth Kit 의 `mmls` 로 파티션 위치를, `fsstat` 으로 파일 시스템 상태를 먼저 확인합니다[13]. 이미지 파일은 `losetup -r` 로 읽기 전용 루프 장치 (loop device) 에 붙입니다. `-P` 는 파티션 표를 읽어 파티션별 장치를 만들고, 섹터 크기 기본값이 512바이트라 다르면 `--sector-size` 를 함께 줍니다[4]. 파티션 하나만 붙이려면 `-o`(시작 바이트)와 `--sizelimit`(크기)를 씁니다[4]. `mount -o loop` 도 `offset`·`sizelimit` 를 받습니다[5].

   마운트 옵션은 파일 시스템마다 다릅니다.

   | 파일 시스템 | 옵션 | 이유 |
   |---|---|---|
   | ext3·ext4 | `ro,noload` | `ro` 만 주면 비정상 종료된 파일 시스템의 저널을 재생하면서 장치에 씁니다[5][6] |
   | XFS | `ro,norecovery` | 로그 복구를 건너뜁니다. `norecovery` 는 읽기 전용이 아니면 마운트가 실패합니다[7] |
   | XFS(LVM 스냅숏, 같은 UUID 가 이미 붙어 있을 때) | `ro,norecovery,nouuid` | 같은 UUID 의 이중 마운트 검사를 끕니다[7] |

   아래는 만든 예시입니다(이미지 이름과 루프 장치 번호는 지어낸 값).

   ```
   losetup -r -P -f --show /cases/2026-001/sdb.raw      # /dev/loop3 을 받았다고 가정
   mount -o ro,noload /dev/loop3p2 /mnt/case_root        # ext4
   ```

   ext4 구조는 [ext4](../../01-foundations/filesystem/ext4/index.md), XFS 는 [XFS](../../01-foundations/filesystem/xfs.md) 를 봅니다.

## 도구

| 도구 | 하는 일 |
|---|---|
| `dd`(GNU coreutils) | 원시 이미지 획득[1] |
| GNU ddrescue | 망가져 가는 장치 획득[1] |
| `ewfacquire`·`ewfverify`·`ewfinfo`(libewf) | EWF 획득·검증·획득 정보 확인[2] |
| `blockdev`·`losetup`·`mount`(util-linux) | 장치 읽기 전용 표시, 읽기 전용 루프 장치, 이미지 마운트[3][4][5] |
| The Sleuth Kit(`mmls`, `fsstat`, `fls`, `istat`, `icat`) | 마운트하지 않고 파티션·파일 시스템 읽기[11][13]. 여러 장치 Btrfs 는 Fraunhofer FKIE 가 늘린 포크(github.com/fkie-cad/sleuthkit)가 다룹니다[11] |
| dissect `acquire` | 디스크 이미지나 켜진 시스템에서 아티팩트를 골라 모읍니다. 켜진 시스템에서는 OS 파일 API 대신 원시 디스크를 읽으려고 관리자 권한을 요구하고, `--fallback`·`--force-fallback` 으로 OS 파일 읽기를 씁니다[10] |

## 함정과 한계

- **`ro` 마운트는 쓰기를 막지 않습니다.** ext3·ext4 는 파일 시스템이 깨끗하게 내려가지 않았으면 읽기 전용 마운트에서도 저널을 재생해 장치에 씁니다[5][6]. 원본 장치를 직접 마운트할 일이 있으면 `blockdev --setro` 로 장치 자체를 읽기 전용으로 만드는 방법도 함께 씁니다[5].
- **저널을 건너뛰면 보이는 모습이 달라집니다.** `noload`·`norecovery` 로 붙이면 쓰기는 없지만, 비정상 종료된 파일 시스템은 저널에만 있던 변경이 빠진 채 불일치 상태로 보이고, XFS 에서는 일부 파일·디렉터리에 접근하지 못할 수 있습니다[6][7]. 켜진 시스템을 그대로 뜬 이미지는 깨끗하게 내려간 상태가 아니므로 이렇게 보일 가능성이 큽니다. 저널에 남은 내용은 [지운 파일 되살리기](../analysis/file-recovery.md) 에서 다룹니다.
- **켜진 파일 시스템의 디스크 상태는 계속 움직입니다.** 2005년 발표의 예에서는 읽기·쓰기로 마운트된 채 쉬고 있던 노트북(SuSE 9.3)의 루트 파일 시스템에 `e2fsck` 1.36 으로 읽기 전용 검사를 하자 `skipping journal recovery because doing a read-only filesystem check` 경고와 함께 블록·아이노드 비트맵 차이가 나왔고, 이 차이는 평소 파일을 만들고 지우는 활동에서 생긴 것이었습니다[12]. 라이브 이미지에서 이런 불일치가 보여도 그 자체를 조작의 근거로 삼지 않습니다.
- **`conv=sync` 는 0 을 끼워 넣습니다.** 오류가 난 블록은 `ibs` 크기 전체가 0 으로 채워지므로 블록 크기가 클수록 잃는 범위가 넓어집니다[1]. `iflag=fullblock` 없이 `read` 가 덜 채워 돌아오면 그 블록도 0 으로 채워져 뒤 데이터의 위치가 밀릴 가능성이 있습니다. 절차 4 의 복구 예가 두 옵션을 함께 쓰는 까닭입니다[1].
- **`ewfacquire` 도 읽지 못한 곳을 0 으로 채웁니다.** 다시 읽기를 다 해도 실패하면 설정에 따라 오류 단위의 남은 섹터를 0 으로 채우고, `-w` 를 주면 오류 단위 섹터 전체를 0 으로 채웁니다[2].
- **`blockdev --setro` 는 이미 붙은 파일 시스템에는 늦습니다.** 읽기·쓰기로 이미 마운트된 파일 시스템은 다시 마운트해야 설정이 적용됩니다[3].
- **섹터 크기가 512바이트가 아니면 파티션을 잘못 읽습니다.** `losetup -P` 의 파티션 해석은 섹터 크기에 달려 있습니다[4]. `ewfacquire` 는 섹터 크기를 자동으로 감지하고 `-P` 로 덮어씁니다[2].
- **같은 UUID 충돌.** LVM 스냅숏처럼 UUID 가 같은 XFS 가 이미 붙어 있으면 이중 마운트 검사에 걸리므로 `nouuid` 를 씁니다[7].
- **풀 구성원 하나만 뜨면 복원이 안 될 수 있습니다.** 여러 장치 Btrfs 에서 raid0 데이터는 장치가 하나만 빠져도 잃습니다[11]. LVM·md RAID 도 절차 1 의 구성 기록과 대조해 구성원을 빠짐없이 뜹니다.
- **켜진 시스템의 원시 디스크 읽기는 관리자 권한이 필요합니다[10].** 권한이 없어 OS 파일 API 로 읽으면 파일을 읽는 것 자체가 접근 시각을 바꿀 수 있습니다[5]. atime 갱신 규칙은 [조사 절차](investigation-process.md) 에서 다룹니다.

## 결과를 어떻게 해석하나

**증명하는 것**

- 획득 때 계산한 해시와 지금 계산한 해시가 같으면, 획득한 비트열이 그 뒤로 바뀌지 않았다는 뜻입니다[2].
- EWF 이미지 안의 사건 번호·증거 번호·분석관 이름은 획득할 때 입력한 값이고, `ewfinfo -i` 로 획득 정보를 다시 볼 수 있습니다[2].

**증명하지 못하는 것**

- 해시는 켜진 채 뜨는 동안 원본이 바뀌지 않았다는 것까지 보여 주지 못합니다. 라이브 이미지는 서로 다른 순간의 블록이 섞인 사본입니다.
- `conv=sync` 나 `ewfacquire` 가 채운 0 은 원본 데이터가 아닙니다. 어디가 채워졌는지는 이미지만 봐서는 알 수 없으므로 `ewfacquire -l` 로그나 `ewfinfo -e`, `dd` 가 표준 오류로 낸 출력을 이미지와 함께 보관합니다[1][2].
- 암호화 볼륨에서 풀린 장치(`/dev/mapper/…`)를 떴는지 원래 파티션을 떴는지에 따라 이미지 내용이 전혀 다릅니다. 이미지만 보고 원래 디스크 전체를 대표한다고 쓰지 않고, 어느 장치 경로를 떴는지 적습니다.

**시각.** `ewfacquire` 가 내는 획득 시작·종료 시각 줄(`Acquiry started at`, `Acquiry completed at`)은 예시 출력에서 `Sun Aug  5 11:32:41 2012` 처럼 시간대 없이 찍힙니다[2]. 획득한 PC 의 시간대와 시계 오차를 따로 기록해 둡니다. 이미지 안 파일의 시각 해석은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 과 [타임라인 만들기](../analysis/timeline.md) 를 봅니다.

**보고서 문장 예(만든 예시).** "2026-09-26 14:05(KST)부터 15:40(KST)까지 서버의 `/dev/sdb` 전체를 전원이 켜진 상태에서 EWF(encase6)로 획득했고, 획득 때 계산한 SHA-256 과 검증 때 계산한 SHA-256 이 같았다. 획득 로그에 읽기 오류는 기록되지 않았다. 켜진 상태에서 획득했으므로 이미지 안의 파일 시스템은 저널 재생 전 상태이다."

다른 운영체제의 증거 확보 절차는 [Windows 포렌식 조사 절차](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/investigation-process.html) 를 봅니다.

## 참고 문헌

1. GNU coreutils, `doc/coreutils.texi`(dd, sha2 utilities 절). https://github.com/coreutils/coreutils/blob/master/doc/coreutils.texi
2. libewf, `manuals/ewfacquire.1`, `manuals/ewfverify.1`, `manuals/ewfinfo.1`. https://github.com/libyal/libewf/tree/main/manuals
3. util-linux, `disk-utils/blockdev.8.adoc`. https://github.com/util-linux/util-linux/blob/master/disk-utils/blockdev.8.adoc
4. util-linux, `sys-utils/losetup.8.adoc`. https://github.com/util-linux/util-linux/blob/master/sys-utils/losetup.8.adoc
5. util-linux, `sys-utils/mount.8.adoc`. https://github.com/util-linux/util-linux/blob/master/sys-utils/mount.8.adoc
6. Linux kernel, `Documentation/admin-guide/ext4.rst`. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/ext4.rst
7. Linux kernel, `Documentation/admin-guide/xfs.rst`. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/xfs.rst
8. Linux kernel, `Documentation/admin-guide/device-mapper/dm-crypt.rst`. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/device-mapper/dm-crypt.rst
9. UAC, `artifacts/live_response/storage/`(lsblk, blkid, findmnt, pvs, vgs, lvs, mdadm, btrfs). https://github.com/tclahr/uac/tree/main/artifacts/live_response/storage
10. Fox-IT, acquire `README.md`. https://github.com/fox-it/acquire/blob/main/README.md
11. Hilgert, J.-N., Lambertz, M., Yang, S. "Forensic Analysis of Multiple Device BTRFS Configurations using The Sleuth Kit". DFRWS 발표 자료. https://dfrws.org/presentation/forensic-analysis-of-multiple-device-btrfs-configurations-using-the-sleuth-kit/
12. Eckstein, K., Jahnke, M. "Data Hiding in Journaling File Systems". DFRWS 2005 USA 발표 자료. https://dfrws.org/presentation/data-hiding-in-journaling-file-systems/
13. Hadi, A., Khader, M., Claflin, T. "Learning Linux Forensic Analysis and Why it Matters". DFRWS 워크숍 자료. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
14. cryptsetup, `man/cryptsetup.8.adoc`(PLAIN MODE 절). https://github.com/mbroz/cryptsetup/blob/main/man/cryptsetup.8.adoc
