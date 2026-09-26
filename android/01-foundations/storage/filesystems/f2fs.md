---
title: "F2FS 구조"
parent: "파일 시스템"
grand_parent: "기반 · 저장 구조"
nav_order: 60
---

# F2FS 구조 (F2FS)

F2FS 는 로그 구조 파일 시스템 (Log-structured File System, LFS) 을 바탕으로 한 리눅스 파일 시스템이고, 이 페이지는 볼륨을 이루는 여섯 영역과 파일·디렉터리가 놓이는 방식을 분석하는 쪽에서 읽는 법을 다룹니다.

## 이 형식을 쓰는 곳

Android 의 파일 기반 암호화가 지원하는 파일 시스템은 ext4 와 F2FS 두 가지라서, 사용자 데이터 파티션(userdata)은 둘 가운데 하나로 만들어집니다. 어느 쪽을 쓰는지는 기기의 fstab 설정에 달려 있어서, 분석하는 이미지의 파일 시스템 종류를 먼저 확인합니다. 두 파일 시스템을 나란히 놓고 보는 표는 허브인 [파일 시스템 (ext4·F2FS)](index.md)에 있습니다.

파일 내용과 이름을 암호화하는 리눅스 fscrypt 는 ext4 와 마찬가지로 F2FS 안에서도 동작하고, F2FS 에도 인라인 암호화 하드웨어를 쓰게 하는 `inlinecrypt` 마운트 옵션이 있습니다. fscrypt 가 무엇을 가리고 무엇을 남기는지는 [ext4 구조](ext4.md)의 "암호화된 inode" 절과 [저장 공간 암호화](../encryption/index.md)에서 다루고, 이 페이지에서는 되풀이하지 않습니다.

## 구조

### 여섯 영역

F2FS 는 볼륨을 여섯 영역으로 나눕니다.

| 영역 | 담는 것 |
|---|---|
| 슈퍼블록 (Superblock, SB) | 파티션 기본 정보와 기본 매개변수. 파티션 앞쪽에 두 벌을 둠 |
| 체크포인트 (Checkpoint, CP) | 파일 시스템 정보, 유효한 NAT·SIT 묶음을 가리키는 비트맵, orphan inode 목록, 지금 쓰고 있는 세그먼트의 요약 항목 |
| SIT (Segment Information Table) | 세그먼트마다 유효 블록 수와, 블록 하나하나가 유효한지 적은 비트맵 |
| NAT (Node Address Table) | Main 영역에 있는 모든 node 블록의 주소표 |
| SSA (Segment Summary Area) | data 블록과 node 블록마다 그 블록의 주인을 적은 요약 항목 |
| Main 영역 | 파일·디렉터리 데이터와 그 인덱스 |

크기 단위는 세그먼트 (Segment) 이고 2MB 로 고정돼 있습니다. 이어진 세그먼트 몇 개를 묶어 섹션 (Section), 섹션 몇 개를 묶어 존 (Zone) 이라 하고, 기본값은 섹션과 존 모두 세그먼트 한 개입니다.

> 그림 자리: 파티션 앞의 SB 두 벌과 CP·SIT·NAT·SSA·Main 여섯 영역, Main 영역이 2MB 세그먼트로 나뉜 모양

### 쓰는 방식

F2FS 는 블록을 고칠 때 원래 자리에 덮어쓰지 않고 다른 자리에 새로 씁니다(out-of-place update). 그래서 옛 블록은 무효 (invalid) 블록으로 남고, 파일 시스템은 가비지 컬렉션 (Garbage Collection, GC) 으로 세그먼트를 비워 다시 씁니다. 블록이 옮겨질 때마다 위쪽 인덱스까지 줄줄이 고쳐야 하는 문제(wandering tree)는 NAT 가 끊습니다.

GC 에는 빈 세그먼트가 모자랄 때 바로 하는 포그라운드 GC 와, 기기가 한가할 때 커널 스레드가 하는 백그라운드 GC 가 있습니다. 비울 세그먼트는 포그라운드에서는 유효 블록이 가장 적은 세그먼트를 고르고(greedy), 백그라운드에서는 세그먼트 나이와 유효 블록 수를 함께 따져 고릅니다(cost-benefit).

새 블록을 쓰는 활성 로그는 여섯 개이고, node 쪽은 Hot·Warm·Cold 세 로그, data 쪽도 Hot·Warm·Cold 세 로그로 나뉩니다. node 쪽은 디렉터리의 direct node, 그 밖의 direct node, indirect node 를 각각 받고, data 쪽은 디렉터리 항목 블록, 일반 데이터 블록, 멀티미디어 블록이나 GC 로 옮긴 블록을 각각 받습니다.

### node 와 inode

파일 하나의 데이터 위치는 node 블록이 적습니다. inode 블록 하나는 4KB 이고, 아래 인덱스가 들어 있습니다.

| 칸 | 개수 | 가리키는 것 |
|---|---|---|
| data 블록 인덱스 | 923 | data 블록 |
| direct node 포인터 | 2 | direct node(data 블록 1018개를 가리킴) |
| indirect node 포인터 | 2 | indirect node(node 블록 1018개를 가리킴) |
| double indirect node 포인터 | 1 | double indirect node |

이 구조로 파일 하나는 약 3.94TB 까지 커질 수 있습니다.

작은 데이터는 따로 블록을 쓰지 않고 inode 블록 안에 넣을 수 있습니다. `inline_data` 는 약 3.4KB 보다 작은 파일의 내용을, `inline_dentry` 는 디렉터리 항목을, `inline_xattr` 는 확장 속성을 inode 블록 안에 둡니다.

ext4 의 i_crtime·i_dtime 같은 칸 이름을 F2FS 에 그대로 옮겨 읽지 않습니다.

### 디렉터리

디렉터리는 여러 단계로 된 해시 테이블입니다. 디렉터리 항목 하나는 11바이트이고 이름 해시, inode 번호, 이름 길이, 파일 종류가 들어 있습니다. 4KB 크기의 dentry 블록 하나에는 슬롯 214개와 파일 이름들, 어느 슬롯이 유효한지 적은 비트맵이 함께 들어 있습니다.

### 일관성과 복구

F2FS 에는 ext4 의 jbd2 같은 저널이 없고, 체크포인트로 일관성을 지킵니다. CP·SIT·NAT 를 두 벌씩 두고(shadow copy), 둘 가운데 하나가 늘 마지막으로 유효했던 상태를 가리킵니다. 마지막 체크포인트 뒤에 쓴 내용을 되살리는 롤포워드 복구 (roll-forward recovery) 도 지원하고, `disable_roll_forward` 옵션으로 끌 수 있습니다.

### 압축

F2FS 는 파일을 클러스터 단위로 압축할 수 있고, 클러스터 크기는 논리 페이지 `4 << n` 개입니다. 클러스터 안 논리 블록이 모두 유효하고 압축률이 기준보다 좋을 때만 압축하며, 압축된 클러스터와 일반 클러스터는 특별한 블록 주소로 구분합니다.

### 마운트 옵션

분석에 영향을 줄 만한 마운트 옵션은 아래와 같습니다.

| 옵션 | 하는 일 |
|---|---|
| `background_gc=on\|off\|sync`, `gc_merge`, `atgc` | 백그라운드 GC 동작. `atgc` 는 나이 기준(Age-threshold) GC |
| `mode=adaptive` / `lfs` | 블록 할당 방식. 기본은 `adaptive` 이고, `lfs` 는 Main 영역에 임의 쓰기를 하지 않음 |
| `discard` / `nodiscard` | 세그먼트를 비울 때 저장 장치에 discard(TRIM) 명령을 바로 보낼지 |
| `fsync_mode=posix` / `strict` / `nobarrier` | fsync 처리 방식. `posix` 가 기본이고 가벼우며, `strict` 는 ext4 수준으로 처리 |
| `checkpoint=disable`, `checkpoint_merge` | 체크포인트 동작 |
| `compress_algorithm=lzo\|lz4\|zstd\|lzo-rle`, `compress_extension=ext`, `compress_mode=fs\|user` | 압축 알고리즘, 압축할 확장자, 압축을 파일 시스템이 정할지(기본 `fs`) 사용자가 정할지 |
| `inlinecrypt` | 인라인 암호화 하드웨어 사용 |

Android 기기가 실제로 어떤 옵션으로 F2FS 를 마운트하는지(discard 를 켜는지, 압축을 쓰는지)는 기기마다 확인합니다.

## 읽는 법

여섯 영역의 구조를 따라 읽으면 순서는 아래와 같습니다.

1. 파티션 앞의 슈퍼블록 두 벌을 읽고 기본 매개변수를 확인합니다.
2. 체크포인트 두 벌 가운데 마지막 유효 상태를 가리키는 쪽을 고르고, 그 체크포인트의 비트맵으로 NAT·SIT 두 벌 가운데 어느 쪽이 유효한지 정합니다.
3. 유효한 NAT 에서 node 블록 주소를 찾아 inode 블록을 읽습니다.
4. inode 블록에서 inline 데이터가 있는지 보고, 없으면 data 블록 인덱스와 direct·indirect node 를 따라 data 블록을 찾습니다.
5. 블록이 지금 유효한지는 SIT 의 비트맵으로, 블록이 어느 파일의 것인지는 SSA 의 요약 항목으로 맞춰 봅니다.

## 포렌식에서 중요한 점

F2FS 는 고친 블록을 새 자리에 쓰기 때문에, 파일을 지우거나 내용을 고친 뒤에도 옛 블록이 무효 블록으로 한동안 남습니다. 이 블록이 언제까지 남는지와 복구에 쓸 단서는 [지운 파일과 저널](deleted-files-journal.md)에서 다룹니다.

`inline_data` 로 저장된 작은 파일은 내용이 inode 블록 안에 있어서, data 블록만 훑는 검색으로는 이런 파일 내용을 놓칠 수 있습니다. 압축된 클러스터는 압축된 채로 저장되니, 원래 파일의 시그니처로 블록을 찾는 방식에도 걸리지 않을 수 있습니다. 파일 기반 암호화가 걸린 영역이라면 두 경우 모두 키 없이는 암호문이라는 점도 함께 따집니다.

## 함정

ext4 를 전제로 만든 해석을 F2FS 이미지에 그대로 쓰지 않습니다. F2FS 에는 jbd2 저널이 없어서 저널에서 옛 메타데이터를 찾는 방법이 통하지 않고, inode 시각 칸도 ext4 와 이름·배치가 같다고 가정할 수 없습니다. 분석을 시작하기 전에 이미지의 파일 시스템 종류부터 확인합니다.

`discard`, 압축, GC 설정처럼 지운 블록이 얼마나 남는지를 좌우하는 옵션은 기기마다 다를 수 있습니다. 라이브 기기나 펌웨어에서 마운트 옵션을 읽을 수 있다면 확보 기록에 함께 남깁니다.

## 도구

The Sleuth Kit 같은 공개 포렌식 도구는 F2FS 이미지를 열지 못하거나 일부만 보여 줄 수 있으니, [도구 검증](../../../03-techniques/reporting/tool-validation.md)의 방법으로 지원 범위를 먼저 확인하고 위 "읽는 법" 순서와 대조합니다.

## 참고 문헌

- General Filesystem Information: F2FS — docs.kernel.org, https://docs.kernel.org/filesystems/f2fs.html
- File-based encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/file-based
- Filesystem-level encryption (fscrypt) — docs.kernel.org, https://docs.kernel.org/filesystems/fscrypt.html
