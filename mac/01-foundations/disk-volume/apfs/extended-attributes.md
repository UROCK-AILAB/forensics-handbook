---
title: "확장 속성"
parent: "APFS 구조"
grand_parent: "기반 · 디스크·볼륨"
nav_order: 50
---

# 확장 속성 (Extended Attributes)

APFS에서 확장 속성 (extended attribute, xattr)은 파일 시스템 트리 안의 XATTR 레코드(형식 4)로 파일마다 따로 붙고, 데이터가 3804바이트 이하면 레코드 안에 바로 들어가며 그보다 크면 별도 데이터 스트림에 저장됩니다 [1].

레코드 키의 공통 머리와 트리의 정렬 순서는 [파일 시스템 트리와 아이노드 (FS Tree·Inode)](fs-tree-inode.md)에 있고, 이 페이지는 XATTR 레코드의 모양과 속성 이름만 다룹니다. 속성 값 하나하나의 형식과 뜻은 그 값을 쓰는 아티팩트 페이지에서 설명합니다.

## 이 구조를 쓰는 곳

실제 이미지에는 `com.apple.quarantine` 과 `com.apple.metadata:kMDItemWhereFroms` 같은 속성이 붙어 있고 [2], 이 두 값의 해석은 [격리 속성과 다운로드 기록 (Quarantine)](../../../02-artifacts/filesystem/quarantine/index.md)과 [다운로드 출처 속성 (kMDItemWhereFroms)](../../../02-artifacts/filesystem/where-froms.md)에서 다룹니다. 파일 시스템도 이 레코드를 자기 용도로 써서 심볼릭 링크의 대상 경로와 펌링크의 대상을 확장 속성에 적습니다 [1]. 펌링크가 두 볼륨을 잇는 방식은 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../volume-group-firmlinks.md)에 있습니다.

투명 압축 파일은 압축 정보를 `com.apple.decmpfs` 속성에 두고 [2][3], 압축 데이터 자체도 이 속성이나 `com.apple.ResourceFork` 속성에 들어갑니다 [2]. 압축 헤더와 방식 번호는 [복제·희소·압축 파일 (Clone·Sparse·Compression)](clone-sparse-compression.md)에서 설명합니다.

## 구조

### 키

키 `j_xattr_key_t` 는 공통 머리, 이름 길이, 이름 순서로 되어 있고 이름은 키의 오프셋 10부터 시작합니다 [1][2].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 8 | `obj_id_and_type` | 하위 60비트는 속성이 붙은 파일의 객체 ID, 상위 4비트는 레코드 형식 4 |
| 8 | 2 | `name_len` | 이름 길이. 끝의 NULL을 포함 |
| 10 | `name_len` | `name` | UTF-8 이름 |

### 값

값 `j_xattr_val_t` 는 `flags`(uint16), 데이터 길이 `xdata_len`(uint16), 데이터 `xdata` 가 이어진 구조이고, `flags` 로 데이터가 어디 있는지 가립니다 [1].

| 플래그 | 값 | 뜻 |
|---|---|---|
| `XATTR_DATA_STREAM` | 0x1 | 데이터가 별도 데이터 스트림에 있고, `xdata` 에는 `j_xattr_dstream_t` 가 들어 있음 |
| `XATTR_DATA_EMBEDDED` | 0x2 | 데이터가 레코드 안의 `xdata` 에 바로 있음 |
| `XATTR_FILE_SYSTEM_OWNED` | 0x4 | 파일 시스템이 소유한 속성(예: 심볼릭 링크 대상) |
| `XATTR_RESERVED_8` | 0x8 | 예약 |

레코드 안에 바로 넣을 수 있는 데이터는 3804바이트(`XATTR_MAX_EMBEDDED_SIZE`)까지이고, 더 크면 데이터 스트림으로 갑니다 [1]. 이때 `xdata` 에 든 `j_xattr_dstream_t` 는 `xattr_obj_id`(8바이트)와 `j_dstream_t`(40바이트)를 합친 48바이트입니다 [1]. `j_dstream_t` 의 칸(`size`, `alloced_size` 등)은 파일 데이터 스트림과 같은 구조라서 [파일 시스템 트리와 아이노드 (FS Tree·Inode)](fs-tree-inode.md)의 설명을 그대로 따릅니다. 데이터 스트림에 담긴 속성의 물리 익스텐트에서는 `owning_obj_id` 가 그 xattr 레코드의 ID입니다 [1].

### 파일 시스템이 쓰는 이름

파일 시스템 전용 이름은 아래 셋입니다 [1].

| 이름 | 뜻 |
|---|---|
| `com.apple.fs.symlink` | 심볼릭 링크의 대상 경로. `XATTR_FILE_SYSTEM_OWNED` 가 켜져 있고, 심볼릭 링크에는 반드시 있음 |
| `com.apple.fs.firmlink` | 펌링크의 대상 |
| `com.apple.fs.cow-exempt-file-count` | copy-on-write 예외 파일(`INODE_SNAPSHOT_COW_EXEMPTION`)의 수 |

ACL이 붙은 파일은 아이노드 플래그 `INODE_HAS_SECURITY_EA` (0x40)로 표시하고 [1], 실제 이미지에는 `com.apple.system.Security` 속성이 나타납니다 [2]. Finder 정보는 아이노드 확장 필드 `INO_EXT_TYPE_FINDER_INFO` (32바이트)에 들어가는데 [1], 실제 이미지에는 `com.apple.FinderInfo` 속성도 나타납니다 [2]. 두 곳의 관계를 설명한 공개 자료가 없어 검체에서 확인합니다.

### 실제 이미지에 나오는 이름

실제 이미지에는 아래 속성 이름이 나옵니다 [2]. 오른쪽 칸은 이 핸드북에서 이어 볼 곳이고, 빈칸은 값의 형식을 설명한 공개 자료가 없는 이름입니다.

| 이름 [2] | 이어 볼 곳 |
|---|---|
| `com.apple.decmpfs` | [복제·희소·압축 파일 (Clone·Sparse·Compression)](clone-sparse-compression.md) |
| `com.apple.ResourceFork` | 같은 곳(리소스 포크에 담는 압축) |
| `com.apple.FinderInfo` | 위의 Finder 정보 설명 |
| `com.apple.quarantine` | [격리 속성과 다운로드 기록 (Quarantine)](../../../02-artifacts/filesystem/quarantine/index.md) |
| `com.apple.metadata:kMDItemWhereFroms` | [다운로드 출처 속성 (kMDItemWhereFroms)](../../../02-artifacts/filesystem/where-froms.md) |
| `com.apple.metadata:kMDItemDownloadedDate` | |
| `com.apple.metadata:_kMDItemUserTags` | |
| `com.apple.metadata:com_apple_backup_excludeItem` | |
| `com.apple.lastuseddate#PS` | |
| `com.apple.rootless` | |
| `com.apple.system.Security` | 위의 ACL 설명 |
| `com.apple.TextEncoding` | |
| `com.apple.genstore.*`, `com.apple.installd.*`, `com.apple.assetsd.*` | |

## 읽는 법

### 헥스로 한 번

아래 바이트는 실제 검체가 아니라 명세 [1][2]의 정의에 맞춰 만든 예시입니다. 객체 ID 0x22 파일에 `com.apple.quarantine` 속성이 붙어 있고 데이터가 레코드 안에 32바이트 들어 있다고 합시다.

```
키
0000  22 00 00 00 00 00 00 40 15 00 63 6F 6D 2E 61 70   |"......@..com.ap|
0010  70 6C 65 2E 71 75 61 72 61 6E 74 69 6E 65 00      |ple.quarantine.|

값
0000  02 00 20 00 ...                                   (뒤에 xdata 32바이트)
```

키의 첫 8바이트를 리틀 엔디언으로 읽으면 0x4000000000000022이고, 상위 4비트 4가 XATTR 형식이며 하위 60비트 0x22가 속성이 붙은 파일의 객체 ID입니다 [1]. 오프셋 8의 `15 00` 은 이름 길이 21이라서 글자 20개와 끝의 NULL이 오프셋 10부터 이어집니다. 값의 첫 2바이트 `02 00` 은 `XATTR_DATA_EMBEDDED` 이고, 다음 2바이트 `20 00` 은 `xdata_len` 32라서 바로 뒤 32바이트가 속성 데이터입니다 [1]. 만약 `flags` 가 `01 00` 이었다면 뒤의 48바이트는 `j_xattr_dstream_t` 이고, 앞 8바이트가 `xattr_obj_id`, 이어지는 40바이트가 `j_dstream_t` 입니다 [1].

### 절차

1. 대상 파일의 객체 ID를 정하고, 파일 시스템 트리에서 같은 객체 ID에 형식 4인 레코드를 모두 모읍니다. 트리는 객체 ID, 레코드 형식, 이름 순서로 정렬하므로 한 파일의 속성 레코드는 서로 붙어 있습니다 [1].
2. 레코드마다 이름을 바이트 그대로 읽고, 값의 `flags` 로 데이터 위치를 가립니다.
3. `XATTR_DATA_EMBEDDED` 이면 `xdata_len` 만큼 읽습니다.
4. `XATTR_DATA_STREAM` 이면 `j_xattr_dstream_t` 의 `xattr_obj_id` 와 `j_dstream_t` 의 `size` 를 적어 두고, 본문은 그 데이터 스트림의 익스텐트를 따라가 `size` 만큼 읽습니다.
5. 읽은 값은 이름에 맞는 아티팩트 페이지의 방법으로 풉니다. 형식이 알려지지 않은 이름은 원본 바이트를 그대로 보존해 둡니다.

## 포렌식에서 중요한 점

확장 속성은 파일 내용과 따로 저장되는 레코드라서, 다운로드 출처나 격리 정보처럼 파일 내용에는 없는 이력이 이 레코드에만 남을 수 있습니다. 다만 속성이 없다고 해서 그런 이력이 없었다고 단정할 수는 없고, 같은 정보를 담는 다른 기록과 맞춰 봅니다.

심볼릭 링크의 대상 경로는 `com.apple.fs.symlink` 속성에 들어 있으므로 [1], 이미지를 마운트하지 않고 트리만 읽을 때도 링크가 가리키던 경로를 이 레코드에서 확인할 수 있습니다.

데이터 스트림에 담긴 속성의 물리 익스텐트는 `owning_obj_id` 에 xattr 레코드의 ID를 적습니다 [1]. 그래서 익스텐트 참조 레코드만 남은 블록을 만났을 때 그 블록이 파일 본문이 아니라 큰 속성 값의 일부였는지 가릴 단서가 될 수 있습니다.

압축 파일은 내용이 데이터 포크가 아니라 확장 속성이나 리소스 포크 속성에 들어가므로 [2], 파일 본문만 읽는 방식으로는 내용을 놓칩니다. 자세한 영향은 [복제·희소·압축 파일 (Clone·Sparse·Compression)](clone-sparse-compression.md)과 [콘텐츠 검색 (Content Search)](../../../03-techniques/analysis/content-search.md)에서 다룹니다.

## 함정

레코드 안에 넣을 수 있는 최대 크기는 APFS 명세에서 3804바이트이지만 [1], xnu의 `decmpfs.h` 에 있는 `MAX_DECMPFS_XATTR_SIZE` 는 3802입니다 [3]. 두 값은 서로 다른 헤더에 정의된 상수라서, 압축 속성의 한도를 APFS 레코드 한도로 옮겨 적지 않습니다.

[2]는 `j_xattr_dstream_t` 를 48바이트로 적으면서 구조 표에는 "8 | 48"처럼 적어 두 표기가 어긋납니다. [1]의 구조체로 계산하면 `xattr_obj_id` 8바이트와 `j_dstream_t` 40바이트를 합쳐 48바이트입니다.

속성 이름은 대소문자 비구분 파일 시스템에서도 대소문자를 구분하는 것으로 보인다는 해석이 있어서 [2], 이름을 찾을 때는 바이트 그대로 비교합니다. Finder 정보처럼 확장 필드와 속성 두 곳에 나타나는 값은 한쪽만 보고 없다고 판단하지 않습니다.

## 도구

mac_apt는 HFS와 APFS 파서를 자체 구현한 공개 도구입니다 [4]. 도구가 보여 주는 속성 목록과 값은 위 헥스 절차로 레코드 하나쯤 직접 맞춰 보고, 특히 데이터 스트림에 담긴 큰 속성을 도구가 끝까지 읽었는지 `size` 와 비교합니다.

## 참고 문헌

1. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
2. Joachim Metz, libfsapfs — Apple File System (APFS) 형식 문서 (개정 0.0.18, 2026년 8월) — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
3. Apple xnu, bsd/sys/decmpfs.h — https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/sys/decmpfs.h
4. mac_apt README, Yogesh Khatri (v1.33.2) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/README.md
