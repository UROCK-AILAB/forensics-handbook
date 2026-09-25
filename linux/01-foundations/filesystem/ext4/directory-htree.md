---
title: "디렉터리 항목과 해시 트리"
parent: "ext4"
grand_parent: "기반 · 파일 시스템"
nav_order: 30
---

# 디렉터리 항목과 해시 트리 (Directory Entry·HTree)

ext4 디렉터리는 "이름 → 아이노드 번호" 짝을 담은 파일이고, 항목이 많은 디렉터리는 이름의 해시로 찾아가는 해시 트리 (HTree) 를 같은 파일 안에 숨겨 둡니다[1].

아이노드 번호로 아이노드를 읽는 방법은 [아이노드와 익스텐트](inode-extent.md), 해시 씨앗이 있는 슈퍼블록은 [슈퍼블록과 블록 그룹](superblock-block-group.md), 지운 파일 전체에 무엇이 남는지는 [지운 파일이 남기는 것](deleted-files.md) 에서 다룹니다. 이 쪽은 디렉터리 블록 안의 항목과 해시 트리 노드를 읽는 방법, 그리고 지울 때 항목이 어떻게 바뀌는지를 다룹니다.

## 이 형식을 쓰는 아티팩트

ext4 볼륨의 모든 경로 이름이 디렉터리 항목에서 나옵니다. 아이노드에는 이름이 없으므로 파일 목록, bodyfile 타임라인, 지운 파일 이름 복구는 모두 디렉터리 블록을 읽는 일에서 시작합니다. 같은 아이노드 번호를 가리키는 항목이 여럿이면 그것이 하드 링크이고, 하드 링크가 다른 파일 시스템의 파일을 가리킬 수 없는 까닭도 항목에 아이노드 번호만 적기 때문입니다[1].

해시 트리는 `dir_index` 기능이 켜진 볼륨에서 씁니다[8]. e2fsprogs 의 mke2fs 설정 파일은 `base_features` 에 `dir_index` 와 `filetype` 을 넣어 두어서, 기본 설정으로 만든 ext4 볼륨이면 두 기능이 켜져 있습니다[9]. 기능 목록은 `dumpe2fs -h` 로 확인합니다([슈퍼블록과 블록 그룹](superblock-block-group.md)).

## 구조

모든 필드는 리틀 엔디언입니다[1].

### 선형 디렉터리

디렉터리 파일은 데이터 블록의 연속이고, 블록마다 항목이 앞에서부터 차례로 놓입니다. 항목 하나가 두 블록에 걸치는 일은 없습니다. 블록의 마지막 항목은 `rec_len` 이 블록 끝까지 늘어나 있어서, `rec_len` 을 따라가다 블록 끝에 닿으면 그 블록이 끝납니다. `inode` 가 0 인 항목은 쓰지 않는 항목입니다[1].

`filetype` 기능이 켜져 있으면 `ext4_dir_entry_2` 형식을 씁니다[1].

| 오프셋 | 크기 | 이름 | 뜻 |
|---|---|---|---|
| 0x0 | 4 | `inode` | 이 이름이 가리키는 아이노드 번호. 0 이면 빈 항목 |
| 0x4 | 2 | `rec_len` | 이 항목의 길이(다음 항목까지 거리) |
| 0x6 | 1 | `name_len` | 이름 길이(바이트) |
| 0x7 | 1 | `file_type` | 파일 종류 코드 |
| 0x8 | 가변 | `name` | 이름(최대 255 바이트) |

항목 하나는 최대 263 바이트입니다. `filetype` 기능이 없는 옛 형식 `ext4_dir_entry` 는 0x6 의 `name_len` 이 2 바이트이고 `file_type` 칸이 없습니다[1]. 항목이 실제로 차지해야 하는 길이는 8 + `name_len` 을 4 의 배수로 올린 값입니다[2]. 그래서 `rec_len` 이 이 값보다 크면 항목 뒤에 빈 공간이 있다는 뜻이고, 지운 이름을 찾는 도구는 이 빈 공간을 훑습니다(아래 "지울 때 항목이 바뀌는 방식").

`file_type` 값은 아래와 같습니다[1]. 이 칸이 있으면 아이노드를 읽지 않고도 항목의 종류를 알 수 있습니다.

| 값 | 종류 |
|---|---|
| 0x0 | 모름 |
| 0x1 | 일반 파일 |
| 0x2 | 디렉터리 |
| 0x3 | 문자 장치 |
| 0x4 | 블록 장치 |
| 0x5 | FIFO |
| 0x6 | 소켓 |
| 0x7 | 심볼릭 링크 |

암호화와 대소문자 무시(casefold)가 함께 켜진 디렉터리는 `.`·`..` 을 뺀 항목의 이름 뒤에 `hash`·`minor_hash`(각 4 바이트)를 덧붙이고, 이 8 바이트도 `rec_len` 에 들어갑니다. 이런 항목은 최대 271 바이트입니다[1][2].

### 잎 블록 체크섬 꼬리

메타데이터 체크섬(`metadata_csum`)이 켜져 있으면 선형 블록(해시 트리의 잎 블록 포함) 끝 12 바이트에 가짜 항목 `ext4_dir_entry_tail` 을 둡니다[1].

| 오프셋 | 크기 | 이름 | 값 |
|---|---|---|---|
| 0x0 | 4 | `det_reserved_zero1` | 0(빈 항목처럼 보이게) |
| 0x4 | 2 | `det_rec_len` | 12 |
| 0x6 | 1 | `det_reserved_zero2` | 0(이름 길이) |
| 0x7 | 1 | `det_reserved_ft` | 0xDE |
| 0x8 | 4 | `det_checksum` | 잎 블록 체크섬 |

체크섬은 파일 시스템 UUID(또는 체크섬 씨앗), 디렉터리의 아이노드 번호와 세대 번호, 꼬리 앞까지의 블록 전체로 계산합니다[1]. 블록 끝 12 바이트가 `00 00 00 00 0C 00 00 DE` 로 시작하면 체크섬 꼬리입니다.

### 해시 트리

디렉터리 아이노드의 `i_flags` 에 `EXT4_INDEX_FL`(0x1000)이 서 있으면 해시 트리 디렉터리입니다[1]. 트리의 뿌리와 중간 노드는 `inode` 가 0 이고 블록 전체를 덮는 "빈 항목" 으로 꾸며져 있어서, 선형으로 읽는 옛 코드는 그 블록을 건너뜁니다. 선형으로 읽으면 뿌리 블록에는 `.`·`..` 만, 중간 노드 블록에는 아무것도 없는 것처럼 보이고, 이름은 잎 블록에만 있습니다[1]. 잎 블록의 모양은 선형 블록과 같습니다.

뿌리 `dx_root` 는 디렉터리의 첫 데이터 블록(논리 블록 0)에 있습니다[1][3].

| 오프셋 | 크기 | 이름 | 뜻 |
|---|---|---|---|
| 0x00 | 12 | `.` 항목 | `inode` = 이 디렉터리, `rec_len` = 12, `name_len` = 1, `file_type` = 2 |
| 0x0C | 12 | `..` 항목 | `inode` = 부모 디렉터리, `rec_len` = 블록 크기 − 12(뒤의 트리 정보를 덮음), `name_len` = 2 |
| 0x18 | 4 | `reserved_zero` | 0 |
| 0x1C | 1 | `hash_version` | 해시 종류(아래 표) |
| 0x1D | 1 | `info_length` | 8 |
| 0x1E | 1 | `indirect_levels` | 중간 노드 층 수 |
| 0x1F | 1 | `unused_flags` | |
| 0x20 | 2 | `limit` | 들어갈 수 있는 `dx_entry` 수(머리 1 칸 포함) |
| 0x22 | 2 | `count` | 실제 `dx_entry` 수(머리 1 칸 포함) |
| 0x24 | 4 | `block` | 해시 값이 가장 작은 쪽 자식 노드의 블록 번호 |
| 0x28 | 8 × n | `dx_entry` 배열 | `hash`(4) + `block`(4) |

`limit`·`count`·`block` 8 바이트는 커널 코드에서 `dx_entry` 배열의 첫 칸이고, `limit`·`count` 가 그 칸의 `hash` 자리를 대신 씁니다[3]. 그래서 두 값에 "머리 1 칸" 이 들어가고, `count` 가 3 이면 0x24 의 `block` 을 포함해 자식 노드가 셋입니다. 블록 번호는 파일 시스템 블록 번호가 아니라 디렉터리 파일 안의 논리 블록 번호이고, 물리 위치는 디렉터리 아이노드의 익스텐트로 바꿔야 합니다[1]([아이노드와 익스텐트](inode-extent.md)).

`indirect_levels` 가 0 이면 뿌리가 곧바로 잎 블록을 가리키고, 0 보다 크면 그만큼 중간 노드 층이 있습니다. 이 값은 `large_dir`(INCOMPAT_LARGEDIR) 기능이 없으면 2 를, 있으면 3 을 넘지 못합니다[1][8].

중간 노드 `dx_node` 도 블록 하나를 다 씁니다. 커널 구조체로 보면 0x0 에 `inode` 0, 0x4 에 `rec_len` = 블록 크기, 0x6·0x7 에 0 인 가짜 항목 8 바이트가 있고, 곧바로 0x8 부터 `dx_entry` 배열이 이어집니다[3]. 따라서 `limit` 은 0x8, `count` 는 0xA, 첫 자식의 `block` 은 0xC, 둘째 `dx_entry` 는 0x10 에 있습니다. 커널 디스크 형식 문서의 `dx_node` 표는 `block` 을 0xE, 배열을 0x12 로 적어 구조체와 2 바이트 어긋나므로[1], 헥스를 읽을 때는 구조체 기준 오프셋을 씁니다.

해시 값은 실제로 31 비트이고 맨 아래 비트는 0 입니다. 해시가 같은 이름들이 잎 블록 하나에 다 들어가지 않아 나뉘면, 중간 노드의 `hash` 맨 아래 비트가 1 이 될 수 있습니다[1]. 이름을 찾을 때는 이름의 해시를 계산해 그 값이 속하는 범위의 잎 블록으로 내려가고, 해시가 겹치면 뒤따르는 잎 블록도 훑습니다[1].

`hash_version` 값은 아래와 같습니다[1].

| 값 | 해시 |
|---|---|
| 0x0 | Legacy |
| 0x1 | Half MD4 |
| 0x2 | Tea |
| 0x3 | Legacy, unsigned |
| 0x4 | Half MD4, unsigned |
| 0x5 | Tea, unsigned |
| 0x6 | Siphash |

해시 씨앗은 슈퍼블록 0xEC 의 `s_hash_seed`(4 바이트 × 4)이고, 기본 해시 종류는 0xFC 의 `s_def_hash_version` 입니다[6]. 새로 해시 트리로 바꾸는 디렉터리의 `hash_version` 에는 `s_def_hash_version` 을 적고, 암호화와 대소문자 무시가 함께 켜진 디렉터리면 Siphash 를 적습니다[3].

메타데이터 체크섬이 켜져 있으면 `dx_root`·`dx_node` 블록 끝 8 바이트에 `dx_tail`(`dt_reserved` 4 + `dt_checksum` 4)을 두고, 그만큼 `limit` 을 줄입니다[1][3]. 블록 크기 4096 바이트에서 뿌리의 `limit` 은 체크섬이 없으면 508, 있으면 507 입니다[3].

### 인라인 디렉터리

`inline_data` 기능이 켜진 볼륨에서는 작은 디렉터리의 항목이 데이터 블록 없이 아이노드 안에 들어갑니다. `i_block` 의 첫 4 바이트가 부모 디렉터리의 아이노드 번호이고, 이어지는 56 바이트에 `ext4_dir_entry` 배열이 있습니다. 아이노드 본체에 확장 속성 `system.data` 가 있으면 그 값도 항목 배열입니다. 두 자리 사이를 걸치는 항목은 없고, 인라인 항목에는 체크섬 꼬리가 없습니다[7]. 이 경우 디렉터리 블록을 찾지 말고 아이노드를 읽어야 합니다([아이노드와 익스텐트](inode-extent.md)).

## 읽는 법

### 헥스로 한 번

아래는 블록 크기 4096 바이트, `metadata_csum` 이 켜진 볼륨의 선형 디렉터리 블록을 명세대로 만든 예시입니다. 디렉터리 아이노드 1234(0x4D2), 부모 2, 파일 `notes.txt`(아이노드 1240 = 0x4D8)는 모두 만든 값입니다.

```
0000  D2 04 00 00 0C 00 01 02  2E 00 00 00 02 00 00 00  |................|
0010  0C 00 02 02 2E 2E 00 00  D8 04 00 00 DC 0F 09 01  |................|
0020  6E 6F 74 65 73 2E 74 78  74 00 00 00 00 00 00 00  |notes.txt.......|
...
0FF0  00 00 00 00 00 00 00 00  0C 00 00 DE xx xx xx xx  |................|
```

1. 0x00: `inode` 0x4D2, `rec_len` 12, `name_len` 1, `file_type` 2, 이름 `.`.
2. 0x0C: `inode` 2, `rec_len` 12, `name_len` 2, `file_type` 2, 이름 `..`.
3. 0x18: `inode` 0x4D8, `rec_len` 0x0FDC(4060), `name_len` 9, `file_type` 1(일반 파일), 이름 `notes.txt`. 이 항목이 실제로 필요한 길이는 8 + 9 = 17 을 4 의 배수로 올린 20 이므로 뒤에 빈 공간이 4040 바이트 있습니다.
4. 0x18 + 4060 = 0xFF4 에 체크섬 꼬리(`rec_len` 12, `file_type` 0xDE)가 있습니다. `xx` 는 체크섬 자리입니다.

같은 블록에서 커널 5.13 이상이 `notes.txt` 를 지우면 `..` 항목의 `rec_len` 이 12 + 4060 = 4072(0x0FE8)로 늘고 0x18~0xFF3 은 0 으로 채워집니다[3][5]. 5.12 이하였다면 `rec_len` 만 늘고 0x18 부터의 `D8 04 00 00 ... notes.txt` 는 그대로 남습니다[4].

해시 트리 뿌리 블록은 0x18 뒤를 읽습니다. 예를 들어 0x18 부터 `00 00 00 00 01 08 00 00 FB 01 03 00 01 00 00 00` 이면(만든 예시) `hash_version` 1(Half MD4), `info_length` 8, `indirect_levels` 0, `limit` 507, `count` 3, 가장 작은 해시 쪽 잎은 논리 블록 1 이고, 0x28·0x30 의 `dx_entry` 두 개가 나머지 잎의 시작 해시와 블록 번호입니다.

### 공개 도구로 한 번

debugfs 는 `-w` 를 주지 않으면 읽기 전용으로 열고, `-R` 로 명령 하나를 실행할 수 있습니다(`debugfs -R '명령' 이미지`)[10].

| 명령 | 하는 일 |
|---|---|
| `ls -l 경로` | 디렉터리 항목 목록 |
| `ls -d 경로` | 지운 항목까지 표시 |
| `ls -c 경로` | 디렉터리 블록 체크섬 표시 |
| `htree_dump 경로` | 해시 트리 구조 덤프 |
| `dx_hash -h 알고리즘 -s 씨앗 이름` | 이름의 해시 계산. 볼륨이 열려 있으면 그 볼륨의 씨앗과 기본 알고리즘을 씀 |
| `dirsearch 경로 이름` | 디렉터리에서 이름 찾기 |
| `ncheck 아이노드번호` | 아이노드 번호로 경로 이름 찾기. `-c` 는 항목의 종류와 아이노드 종류 비교 |
| `blocks 경로`, `block_dump -f 경로 번호` | 디렉터리의 블록 목록, 디렉터리 안 논리 블록을 헥스로 덤프 |

The Sleuth Kit 의 `fls` 는 디렉터리 블록을 읽어 할당된 이름과 지운 이름을 함께 보여 줍니다[11].

## 포렌식에서 중요한 점

### 증명하는 것

디렉터리 항목은 어떤 이름이 어떤 아이노드 번호를 가리켰는지, 그 이름이 어느 디렉터리에 있었는지를 보여 줍니다. `file_type` 과 아이노드의 종류가 다르면 아이노드가 다른 파일에 다시 쓰였을 가능성이 있습니다(`ncheck -c` 가 이 비교를 합니다)[10].

### 증명하지 못하는 것

디렉터리 항목에는 시각 칸이 없습니다[1]. 이름이 언제 생겼고 언제 지워졌는지는 항목만으로 알 수 없고, 아이노드의 시각([시각 값](timestamps.md))과 디렉터리 아이노드의 mtime·ctime, 저널의 커밋 시각으로 좁혀야 합니다. 지운 항목이 가리키는 아이노드 번호는 이미 다른 파일에 다시 쓰였을 수 있으므로, 지운 이름과 현재 그 번호의 아이노드 내용이 같은 파일이라고 단정하지 않습니다.

### 지울 때 항목이 바뀌는 방식

커널은 지울 항목 앞에 다른 항목이 있으면 앞 항목의 `rec_len` 에 지울 항목의 길이를 더해 흡수합니다. 지울 항목이 블록의 첫 항목이면 `inode` 만 0 으로 만듭니다[3][4].

Linux 5.13 부터는 여기에 0 채우기가 붙었습니다. 앞 항목에 흡수될 때는 지운 항목 영역 전체를, 블록 첫 항목일 때는 `rec_len` 만 남기고 나머지를 0 으로 채웁니다[3][5]. 같은 커밋이 해시 트리로 바꿀 때 뿌리 블록에서 옮긴 항목 자리와, 잎 노드를 나눌 때 옮긴 항목 자리도 0 으로 채우게 했습니다[3][5]. 5.12 이하 커널에서는 `rec_len` 만 바꾸므로 이름과 아이노드 번호가 앞 항목의 빈 공간에 남습니다[4].

TSK 는 `rec_len` 이 실제 필요한 길이보다 긴 항목 뒤의 빈 공간을 4 바이트씩 옮기며 항목 모양(아이노드 번호 범위, 이름 길이 1~255, `rec_len` 이 4 의 배수)을 갖춘 곳을 찾고, 찾은 이름을 지운 이름으로 표시합니다[11]. `name_len` 이 0 인 자리는 건너뛰므로 5.13 이상에서 0 으로 채운 항목은 목록에 나오지 않습니다[11]. 이름을 잃고 아이노드만 남은 파일은 TSK 가 가상 `$OrphanFiles` 디렉터리에 모아 보여 줍니다[11][12].

0 으로 채운 이름의 옛 사본은 저널에 남아 있을 수 있습니다[5]. 저널에서 옛 디렉터리 블록 사본을 찾는 방법은 [저널](journal-jbd2.md) 에서 다룹니다.

### 해시 트리 노드의 옛 데이터

5.13 전 커널이 만든 해시 트리에서는 뿌리·중간·잎 노드 블록에 옛 데이터 (stale data) 가 남을 수 있습니다[13]. 뿌리·중간 노드 블록은 가짜 빈 항목 뒤가 모두 `dx_entry` 자리라서, 쓰이는 `count` 칸 뒤의 바이트는 트리 구조와 관계없는 옛 내용일 수 있습니다. 5.13 에서 0 채우기를 더한 곳은 위에서 말한 세 경우이고 쓰지 않는 `dx_entry` 자리는 여기에 들지 않으므로[5], 선형으로 읽을 때 빈 블록으로 보이는 해시 트리 노드 블록도 헥스로 한 번 훑어 봅니다.

## 함정

- 5.13 이상 커널에서 디렉터리 블록에 지운 이름이 보이지 않는 것은 정상입니다[5]. 검체 커널 판은 부팅 기록으로 확인하고([부팅과 종료 기록](../../../02-artifacts/system-info/boot-shutdown.md), [커널 로그](../../../02-artifacts/system-info/kernel-log.md)), 지운 이름은 저널에서 찾습니다.
- 디렉터리를 선형으로만 읽는 도구는 해시 트리 뿌리·중간 노드 블록을 빈 블록으로 보고 넘어갑니다[1]. 빈 블록이라고 해서 내용이 없는 것은 아닙니다.
- `dx_entry` 와 `dx_root` 의 `block` 은 디렉터리 안 논리 블록 번호입니다[1]. 볼륨 블록 번호로 읽으면 엉뚱한 블록을 봅니다.
- `dx_node` 오프셋은 커널 디스크 형식 문서의 표와 구조체가 2 바이트 어긋납니다[1][3]. 구조체 기준(0x8 `limit`, 0xC 첫 `block`)으로 읽습니다.
- 인라인 디렉터리의 항목은 아이노드 안에 있어서, 디렉터리 블록만 훑어서는 찾을 수 없습니다[7].
- 체크섬 꼬리(`file_type` 0xDE, `rec_len` 12)는 빈 항목처럼 생겼습니다[1]. 지운 항목으로 세지 않습니다.

## 도구

- e2fsprogs debugfs: `ls -d`, `ls -c`, `htree_dump`, `dx_hash`, `dirsearch`, `ncheck`, `block_dump`[10]. 볼륨의 기능과 해시 씨앗은 `dumpe2fs -h`([슈퍼블록과 블록 그룹](superblock-block-group.md)).
- The Sleuth Kit: `fls`(지운 이름 표시), 가상 `$OrphanFiles` 디렉터리[11][12].

## 참고 문헌

1. Linux kernel, `Documentation/filesystems/ext4/directory.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/directory.rst
2. Linux kernel, `fs/ext4/ext4.h` (`ext4_dir_rec_len`, `EXT4_DIR_ROUND`, `ext4_hash_in_dirent`). https://github.com/torvalds/linux/blob/master/fs/ext4/ext4.h
3. Linux kernel, `fs/ext4/namei.c` (`struct dx_root`, `struct dx_node`, `dx_root_limit`, `ext4_generic_delete_entry`, `dx_move_dirents`, `make_indexed_dir`). https://github.com/torvalds/linux/blob/master/fs/ext4/namei.c
4. Linux kernel v5.12, `fs/ext4/namei.c` (`ext4_generic_delete_entry`). https://github.com/torvalds/linux/blob/v5.12/fs/ext4/namei.c
5. Linux kernel, 커밋 6c0912739699 "ext4: wipe ext4_dir_entry2 upon file deletion" (Linux 5.13). https://github.com/torvalds/linux/commit/6c0912739699d8e4b6a87086401bf3ad3c59502d
6. Linux kernel, `Documentation/filesystems/ext4/super.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/super.rst
7. Linux kernel, `Documentation/filesystems/ext4/inlinedata.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inlinedata.rst
8. e2fsprogs, `misc/ext4.5.in`. https://github.com/tytso/e2fsprogs/blob/master/misc/ext4.5.in
9. e2fsprogs, `misc/mke2fs.conf.in`. https://github.com/tytso/e2fsprogs/blob/master/misc/mke2fs.conf.in
10. e2fsprogs, `debugfs/debugfs.8.in`. https://github.com/tytso/e2fsprogs/blob/master/debugfs/debugfs.8.in
11. The Sleuth Kit, `tsk/fs/ext2fs_dent.cpp`. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs_dent.cpp
12. The Sleuth Kit, `tsk/fs/ext2fs.cpp`. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs.cpp
13. Kevin D. Fairbanks, "An Analysis of Ext4 for Digital Forensics", DFRWS 2012 USA 발표 자료. https://dfrws.org/presentation/an-analysis-of-ext4-for-digital-forensics/
