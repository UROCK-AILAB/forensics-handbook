---
title: "ext4 구조"
parent: "파일 시스템"
grand_parent: "기반 · 저장 구조"
nav_order: 50
---

# ext4 구조 (ext4)

ext4 는 Android 의 사용자 데이터 영역에 쓰이는 두 파일 시스템 가운데 하나이고, 이 페이지는 inode 와 시각 칸을 중심으로 구조를 읽는 법을 다룹니다.

## 이 형식을 쓰는 곳

Android 의 파일 기반 암호화 (File-Based Encryption, FBE) 는 ext4 와 F2FS 두 파일 시스템을 지원하고, 커널 3.18 이상이 필요합니다. Android 10 이상으로 출시되는 기기는 FBE 를 반드시 써야 해서, 앱 데이터와 공용 저장 공간이 들어 있는 사용자 데이터 파티션(userdata)은 이 두 파일 시스템 가운데 하나로 만들어집니다. 앱 폴더가 어떻게 놓이는지는 [앱 데이터 폴더 구조](../app-data-layout.md)에서, 파티션 배치는 [파티션과 저장 영역](../partitions/index.md)에서 다룹니다.

어느 기기가 ext4 를 쓰고 어느 기기가 F2FS 를 쓰는지는 기기의 fstab 설정에 달려 있습니다. 삼성 갤럭시의 userdata 가 어느 파일 시스템인지는 이 페이지의 출처로 확인하지 못했고, 기기 관찰 메모에도 마운트 정보가 없어서 Android 16 기기의 경우도 관찰하지 못했습니다. 분석하는 이미지의 파일 시스템 종류를 먼저 확인하고 이 페이지와 [F2FS 구조](f2fs.md) 가운데 맞는 쪽을 봅니다.

## 구조

### 큰 구조

ext4 는 파일 시스템을 여러 블록 그룹으로 나누고, 그룹마다 정해진 자리에 고정된 메타데이터를 둡니다. 전역 구조는 아래와 같습니다.

| 구조 | 하는 일 |
|---|---|
| 슈퍼블록 (Superblock) | 파일 시스템 전체 설정을 담는 첫 구조 |
| 블록 그룹 디스크립터 (Block Group Descriptor) | 그룹마다 비트맵·inode 테이블이 어디 있는지 적은 표 |
| 블록 비트맵·inode 비트맵 | 블록과 inode 가 쓰이고 있는지 한 비트씩 표시 |
| inode 테이블 | 그룹에 속한 inode 들 |
| MMP (Multiple Mount Protection) | 여러 곳에서 동시에 마운트하지 못하게 막음 |
| 저널 (jbd2) | 변경을 먼저 기록해 두는 영역. [지운 파일과 저널](deleted-files-journal.md)에서 다룸 |
| orphan file | 연결이 끊겼지만 아직 정리되지 않은 inode 를 추적 |

슈퍼블록의 위치·매직 값·필드 이름, extent 트리 헤더, 디렉터리 항목의 필드 배치는 이 페이지가 연 출처에 세부가 없어서 적지 않습니다. 디렉터리를 저장하는 방식에는 선형 디렉터리와 해시 트리 디렉터리 두 가지가 있다는 것까지만 확인했습니다.

> 그림 자리: 블록 그룹이 이어진 볼륨과, 한 그룹 안의 디스크립터·비트맵·inode 테이블·데이터 블록 배치

### inode

inode 크기는 기본 256바이트이고, 그중 128바이트를 넘는 부분의 크기를 적는 i_extra_isize 는 기본 32바이트입니다. 128바이트는 ext2 의 원래 inode 크기(EXT2_GOOD_OLD_INODE_SIZE)입니다.

inode 번호에서 블록 그룹 번호는 아래 식으로 구합니다.

```
bg = (inode_num - 1) / sb->s_inodes_per_group
```

i_block 칸은 60바이트이고, 파일 데이터 위치를 블록 맵 또는 extent 트리 형태로 담습니다. i_links_count 는 하드 링크 수이고, ext4 는 inode 하나에 하드 링크가 65,000개를 넘지 않게 해서 한 디렉터리의 하위 디렉터리는 64,998개까지입니다. 다만 DIR_NLINK 기능이 켜져 있으면 이보다 많은 하위 디렉터리를 허용하고, 이때는 링크 수를 모른다는 뜻으로 이 칸에 1 을 적기 때문에 디렉터리의 i_links_count 를 하위 디렉터리 수로 읽지 않습니다.

i_flags 가운데 해석에 쓸 만한 값은 아래와 같습니다.

| 플래그 | 값 | 뜻 |
|---|---|---|
| EXT4_ENCRYPT_FL | 0x800 | 암호화된 inode |
| EXT4_INLINE_DATA_FL | 0x10000000 | inline data 가 있는 inode |
| EXT4_EXTENTS_FL | 0x80000 | extent 로 데이터 위치를 적는 inode |
| EXT4_VERITY_FL | 0x100000 | verity 로 보호되는 파일 |
| EXT4_CASEFOLD_FL | 0x40000000 | 디렉터리 안 이름을 대소문자 구분 없이 찾음 |

EXT4_CASEFOLD_FL 은 공용 저장 공간과 이어집니다. Android 11 이상으로 출시되고 커널이 5.4 이상인 기기는 /sdcard 에 SDCardFS 대신 FUSE 를 쓰고, 예전에 SDCardFS 가 맡던 대소문자 무시를 파일 시스템 자체 기능으로, 용량 추적을 project quota 로 처리합니다. 공용 저장 공간 쪽 이야기는 [공용 저장 공간](../shared-storage.md)에서 다룹니다.

### 시각 칸

inode 의 시각 칸은 모두 유닉스 에포크(1970-01-01 00:00:00 UTC)부터 센 초를 부호 있는 32비트로 적습니다. 에포크 기준이라 값에 시간대가 들어 있지 않고, 사람이 읽는 시각으로 바꿀 때 시간대를 따로 적용합니다. 값 바꾸는 법은 [시각 값](../../value-decoding/time-values.md)에서 다룹니다.

| 칸 | 뜻 |
|---|---|
| i_atime | 마지막 접근 시각 |
| i_ctime | 마지막 inode 변경 시각 |
| i_mtime | 마지막 데이터 수정 시각 |
| i_crtime | 파일 생성 시각. 128바이트를 넘는 확장 영역(오프셋 0x90)에 있어서 128바이트 inode 에는 없음 |
| i_dtime | 삭제 시각. 단, orphan inode 에서는 다른 용도로 씀(아래 함정 참고) |

inode 가 128바이트보다 크면 i_ctime_extra, i_mtime_extra, i_atime_extra, i_crtime_extra 가 붙습니다. extra 칸의 아래 2비트는 초 칸을 34비트로 늘리는 데 쓰고, 위 30비트는 나노초입니다.

## 읽는 법

1. inode 번호로 블록 그룹을 구하고, 그 그룹의 블록 그룹 디스크립터에서 inode 테이블 위치를 찾아 inode 를 읽습니다.
2. i_flags 를 먼저 봅니다. EXT4_ENCRYPT_FL 이 서 있으면 이름과 내용이 암호문이고(아래 "암호화된 inode" 참고), EXT4_INLINE_DATA_FL 이 서 있으면 데이터가 inline data 로 들어 있고, EXT4_EXTENTS_FL 이 서 있으면 i_block 을 extent 트리로 읽습니다.
3. 시각 칸을 읽고, inode 가 128바이트보다 크면 extra 칸까지 더해 초와 나노초를 맞춥니다.

extra 칸은 아래처럼 풉니다.

```
초     = (부호 있는 32비트로 읽은 i_mtime) + ((i_mtime_extra & 0x3) << 32)
나노초 = i_mtime_extra >> 2
```

아래 값은 명세대로 만든 예시이고 특정 검체에서 나온 값이 아닙니다. i_mtime_extra 가 `0x77359401` 이면 아래 2비트가 `01` 이라 초 칸에 2의 32제곱 초를 더하고, 오른쪽으로 2비트 민 `0x1DCD6500` 은 500,000,000 나노초, 곧 0.5초입니다.

## 암호화된 inode

Android 의 FBE 는 리눅스 fscrypt 를 씁니다. fscrypt 는 ext4 위에 따로 얹는 층이 아니라 파일 시스템 안에 들어가 있고, 파일 내용과 파일 이름, 심볼릭 링크 대상을 암호화합니다. 파일 크기와 권한, 시각, 확장 속성, 파일 안 빈 블록(hole)이 있는지와 그 위치 같은 파일 시스템 메타데이터는 fscrypt 가 암호화하지 않습니다.

키 없이 암호화된 디렉터리를 나열하면 파일 이름이 암호문을 base64url 로 인코딩한 형태로 보이고, 긴 이름은 해시로 줄여서 보입니다. 이런 이름은 원래 이름을 알려 주지 않지만, 같은 디렉터리 안에 항목이 몇 개 있는지와 inode 의 크기·시각은 fscrypt 만으로는 가려지지 않습니다.

Android 는 fscrypt 가 남기는 이 빈틈을 메타데이터 암호화로 덮습니다. Android 11 이상으로 출시되는 기기는 내부 저장소에 메타데이터 암호화를 켜야 하고, Android 11 이상에서는 dm-default-key 커널 모듈이 이 일을 맡습니다. 출처가 직접 적은 문장은 아니지만, 이 구조로 보면 전원이 꺼진 기기의 userdata 를 통째로 떠도 키 없이는 inode 테이블 자체를 읽기 어렵다고 해석할 수 있습니다. 키 구조와 CE·DE 저장 영역 구분은 [저장 공간 암호화](../encryption/index.md)에서 다룹니다.

## 포렌식에서 중요한 점

inode 가 128바이트보다 큰 ext4 에는 생성 시각(i_crtime)까지 들어 있어서, 파일이 처음 만들어진 때와 마지막으로 내용이 바뀐 때(i_mtime), inode 정보가 바뀐 때(i_ctime)를 나눠 볼 수 있습니다. 앱 DB 안에 적힌 시각과 파일 시스템 시각이 서로 다른 사건을 가리키는 일이 흔해서, 둘을 같은 사건으로 묶기 전에 각 값이 무엇이 바뀔 때 바뀌는지 먼저 따집니다.

지운 파일의 inode 와 저널에 남는 흔적은 [지운 파일과 저널](deleted-files-journal.md)에서 다룹니다.

## 함정

i_dtime 을 늘 삭제 시각으로 읽으면 안 됩니다. orphan_file 기능이 없는 파일 시스템에서는 어느 디렉터리에도 연결되지 않았지만 아직 열려 있는 inode(orphan inode)가 dtime 칸을 orphan 목록을 잇는 용도로 씁니다.

초 칸은 부호 있는 32비트라서, 부호 없이 읽거나 extra 칸의 아래 2비트를 빼고 읽으면 초가 틀릴 수 있고, 128바이트 inode 에는 extra 칸이 없어서 나노초를 얻을 수 없습니다.

이 페이지의 출처는 Android 기기가 ext4 를 어떤 마운트 옵션으로 쓰는지 다루지 않습니다. 접근 시각(i_atime)이 언제 갱신되는지처럼 마운트 옵션에 따라 달라질 수 있는 값은 이 페이지만으로 해석을 확정하지 않습니다.

## 도구

ext4 를 읽는 공개 도구로는 리눅스 e2fsprogs 의 debugfs 나 The Sleuth Kit 같은 도구를 예로 들 수 있지만, 이 페이지는 각 도구의 지원 범위를 확인하지 않았습니다. 암호화된 이름이나 extra 시각 칸을 도구가 어떻게 보여 주는지는 [도구 검증](../../../03-techniques/reporting/tool-validation.md)의 방법으로 먼저 확인하고, 필요하면 위 "읽는 법" 순서대로 헥스로 한 번 대조합니다.

## 참고 문헌

- ext4 Global Structures — docs.kernel.org, https://docs.kernel.org/filesystems/ext4/globals.html
- ext4 Dynamic Structures — docs.kernel.org, https://docs.kernel.org/filesystems/ext4/dynamic.html
- ext4 Index Nodes — docs.kernel.org, https://docs.kernel.org/filesystems/ext4/inodes.html
- Filesystem-level encryption (fscrypt) — docs.kernel.org, https://docs.kernel.org/filesystems/fscrypt.html
- File-based encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/file-based
- Metadata encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/metadata
- Deprecate SDCardFS — Android Open Source Project, https://source.android.com/docs/core/storage/sdcardfs-deprecate
