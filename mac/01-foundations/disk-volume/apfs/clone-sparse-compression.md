---
title: "복제·희소·압축 파일"
parent: "APFS 구조"
grand_parent: "기반 · 디스크·볼륨"
nav_order: 70
---

# 복제·희소·압축 파일 (Clone·Sparse·Compression)

APFS에는 다른 파일과 물리 블록을 나눠 쓰는 복제 파일 (clone), 빈 구간에 블록을 두지 않는 희소 파일 (sparse file), 내용을 확장 속성이나 리소스 포크에 압축해 두는 투명 압축 파일 (decmpfs)이 있고 [1][2], 셋 모두 파일 익스텐트만 읽지 말고 아이노드 플래그와 확장 필드, 확장 속성을 함께 봐야 내용과 크기를 바르게 읽을 수 있습니다.

아이노드 플래그 전체 표와 익스텐트 레코드 구조는 [파일 시스템 트리와 아이노드 (FS Tree·Inode)](fs-tree-inode.md)에, 확장 속성이 저장되는 방식은 [확장 속성 (Extended Attributes)](extended-attributes.md)에 있습니다. zlib·LZVN·LZFSE 같은 압축 알고리즘 자체는 [압축 형식 (LZFSE·LZ4·zlib)](../../value-decoding/compression.md)에서 다루고, 이 페이지는 세 종류의 파일을 APFS가 어떻게 표시하고 저장하는지만 다룹니다.

## 이 구조를 쓰는 곳

APFS는 파일과 디렉터리 복제를 지원하고 [3], 중복 제거(dedup) 기능은 따로 없지만 복제 파일로 저장 공간과 중복을 줄입니다 [4]. 투명 압축은 파일 크기와 내용을 읽는 모든 도구에 영향을 주고, 데이터 없는 (dataless) 파일 형식도 같은 압축 헤더에 정의되어 있습니다 [5]. 복제와 압축은 [지운 파일과 옛 체크포인트 (Deleted Files·Old Checkpoints)](deleted-files.md)에서 블록이 언제 풀리는지를 판단할 때와 [콘텐츠 검색 (Content Search)](../../../03-techniques/analysis/content-search.md)에서 원시 블록을 검색할 때 다시 나옵니다.

## 버전별 차이

| macOS | 달라진 점 |
|---|---|
| 10.13.3 전 | `INODE_WAS_EVER_CLONED` 가 잘못 켜지는 문제가 있었고, 볼륨 슈퍼블록에 복제 정보 필드가 없음 [1] |
| 10.13.3 이상 | 볼륨 슈퍼블록에 `apfs_cloneinfo_id_epoch`·`apfs_cloneinfo_xid` 추가 [1] |
| 10.15 전 | Apple 구현이 아이노드의 `INODE_HAS_UNCOMPRESSED_SIZE` 를 무시하고 `uncompressed_size` 필드를 늘 패딩으로 다룸 [1] |

## 복제 (clone)

아이노드 플래그 `INODE_WAS_CLONED` (0x10)는 다른 아이노드를 복제해서 만든 아이노드라는 표시이고, `INODE_WAS_EVER_CLONED` (0x400)는 한 번 이상 복제된 적이 있어서 이 아이노드의 블록을 다른 아이노드도 쓰고 있을 수 있다는 표시입니다 [1]. 그래서 `INODE_WAS_EVER_CLONED` 가 켜진 파일을 지울 때는 블록의 참조 수를 확인해야 합니다 [1].

macOS 10.13.3 전에는 `INODE_WAS_EVER_CLONED` 가 잘못 켜지는 문제가 있었으므로, 이 플래그를 믿기 전에 두 가지를 확인합니다. 먼저 아이노드 ID가 볼륨의 `apfs_cloneinfo_id_epoch` 보다 커야 하고, 다음으로 `apfs_cloneinfo_xid` 가 `apfs_modified_by` 의 값과 같아서 옛 OS가 그 뒤에 볼륨을 고치지 않았어야 합니다 [1]. 두 필드는 10.13.3에서 추가됐고, 둘 다 0이면 옛 구현이 만든 볼륨입니다 [1]. 볼륨 슈퍼블록의 필드 위치는 [컨테이너와 볼륨 (Container·Volume)](container-volume.md)에 있습니다.

복제할 때 새 아이노드로 넘어가는 내부 플래그는 `INODE_CLONED_INTERNAL_FLAGS` 로 정해져 있고, `INODE_HAS_RSRC_FORK`, `INODE_NO_RSRC_FORK`, `INODE_HAS_FINDER_INFO`, `INODE_SNAPSHOT_COW_EXEMPTION` 이 여기에 들어갑니다 [1]. 확장 필드 플래그 `XF_DO_NOT_COPY` (0x2)가 켜진 확장 필드는 복사할 때 빼야 합니다 [1].

블록을 나눠 쓰는 정도는 참조 수로 셉니다. 물리 익스텐트 레코드 `j_phys_ext_val_t` 에 `refcnt` 가 있어서 이 값이 0이 되면 그 익스텐트를 지울 수 있고, 데이터 스트림 레코드 `j_dstream_id_val_t` 에도 `refcnt` 가 있습니다 [1]. 이 구조로 보아 복제본과 원본의 파일 익스텐트는 같은 물리 블록 주소를 가리키는 것으로 보입니다.

Finder나 명령줄의 복사가 복제를 쓰는지, 복제본의 생성·수정 시각이 어떻게 정해지는지는 명세에 나오지 않아 실제 기기에서 확인해야 합니다.

## 희소 파일 (sparse)

아이노드 플래그 `INODE_IS_SPARSE` (0x200)가 켜진 파일에는 희소 바이트 수를 적은 확장 필드 `INO_EXT_TYPE_SPARSE_BYTES` (형식 13, uint64)가 있습니다 [1]. 희소 구간의 파일 익스텐트는 물리 블록 번호가 0입니다 [2].

블록 0은 컨테이너 슈퍼블록 사본이 있는 자리라서 [1] 파일 데이터를 가리키는 값으로 쓰이지 않는 것으로 보입니다. 물리 블록 번호 0을 만나면 블록 0을 읽지 말고 블록을 두지 않은 구간으로 처리합니다.

## 투명 압축 (decmpfs)

### 표시와 헤더

압축 파일은 BSD 플래그 `UF_COMPRESSED` (0x20)가 켜져 있고 [2], 압축 정보는 확장 속성 `com.apple.decmpfs` 에 들어 있습니다 [2][5]. 이 속성은 16바이트 헤더로 시작하고, 디스크에는 리틀 엔디언으로 저장합니다 [5].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 4 | `compression_magic` | 0x636d7066('cmpf'). 디스크 바이트로는 "fpmc"로 보임 [2][5] |
| 4 | 4 | `compression_type` | 압축 방식 번호 |
| 8 | 8 | `uncompressed_size` | 압축 전 크기 |
| 16 | … | `attr_bytes` | 헤더 뒤 데이터 |

아이노드에도 `uncompressed_size` 필드와 이 필드가 유효하다는 플래그 `INODE_HAS_UNCOMPRESSED_SIZE` 가 있지만, macOS 10.15 전에는 Apple 구현이 이 플래그를 무시했습니다 [1].

### 압축 방식 번호

방식 번호와 이름은 다음과 같습니다 [2].

| 값 | 데이터 위치 | 방식 |
|---|---|---|
| 1 | 확장 속성 | 압축 안 된 데이터(xnu의 `CMP_Type1` [5]) |
| 3 | 확장 속성 | zlib |
| 4 | 리소스 포크 | zlib, 64k 조각 |
| 5 | — | 0바이트로 된 데이터로 보임([2]는 Unknown으로 적음) |
| 7 | 확장 속성 | LZVN |
| 8 | 리소스 포크 | LZVN, 64k 조각 |
| 9 | 확장 속성 | 압축 안 함(raw) |
| 10 | 리소스 포크 | raw, 64k 조각 |
| 11 | 확장 속성 | LZFSE |
| 12 | 리소스 포크 | LZFSE, 64k 조각 |
| 13 | 확장 속성 | LZBITMAP |
| 14 | 리소스 포크 | LZBITMAP, 64k 조각 |

리소스 포크 방식(4, 8 등)은 데이터가 확장 속성 `com.apple.ResourceFork` 에 들어 있고, 앞머리에 압축 블록들의 오프셋이 있습니다 [2]. xnu 헤더에는 `CMP_Type1` 하나만 정의되어 있고, 나머지 형식은 AppleFSCompression 프로젝트에서 정의합니다 [5].

### 데이터 없는 파일

xnu 헤더에는 데이터 없는 파일과 디렉터리를 뜻하는 `DATALESS_CMPFS_TYPE` (0x80000001)과, 루트 자식 수와 전체 크기를 인코딩한 데이터 없는 패키지 `DATALESS_PKG_CMPFS_TYPE` (0x80000002)이 정의되어 있습니다 [5]. [2]는 0x80000001을 "faulting file"이라 부르며 뜻을 Unknown으로 적습니다 [2]. 아이클라우드처럼 내용이 아직 내려오지 않은 파일이 이런 모양일 가능성이 있고, 동기화 쪽 기록은 [파일 공급자 (File Provider)](../../../02-artifacts/cloud-apps/file-provider.md)와 [아이클라우드 드라이브 (iCloud Drive·CloudDocs)](../../../02-artifacts/cloud-apps/icloud-drive.md)에서 따로 봅니다.

## 읽는 법

### 헥스로 한 번

아래 바이트는 실제 데이터가 아니라 명세 [2][5]의 정의에 맞춰 만든 예시입니다. 어떤 파일의 `com.apple.decmpfs` 속성 값이 이렇게 시작한다고 합시다.

```
속성 값 내 오프셋
0000  66 70 6D 63 0B 00 00 00 00 10 00 00 00 00 00 00   "fpmc............"
0010  ...                                                (압축 데이터)
```

첫 4바이트 "fpmc"를 리틀 엔디언으로 읽으면 0x636d7066('cmpf')이라서 decmpfs 헤더가 맞습니다. 다음 4바이트 0x0000000B는 방식 11, 곧 확장 속성 안에 든 LZFSE이고, 다음 8바이트 0x1000은 압축 전 크기 4096바이트입니다 [2][5]. 방식 11은 데이터가 속성 안에 있으므로 오프셋 16부터가 LZFSE 데이터이고, 방식이 12였다면 데이터는 `com.apple.ResourceFork` 속성에서 찾았을 것입니다 [2].

### 절차

1. 아이노드의 `internal_flags` 에서 `INODE_WAS_CLONED`, `INODE_WAS_EVER_CLONED`, `INODE_IS_SPARSE` 를, `bsd_flags` 에서 `UF_COMPRESSED` 를 확인합니다.
2. 압축 파일이면 `com.apple.decmpfs` 속성을 읽어 매직, 방식 번호, 압축 전 크기를 적습니다.
3. 방식 번호로 데이터 위치를 정하고, 확장 속성 안이면 헤더 뒤를, 리소스 포크 방식이면 `com.apple.ResourceFork` 속성 앞머리의 오프셋을 따라 조각을 읽어 풉니다.
4. 푼 크기가 헤더의 `uncompressed_size` 와 같은지 확인합니다.
5. 희소 파일이면 물리 블록 번호가 0인 익스텐트를 블록 없는 구간으로 두고 전체 크기를 맞춥니다.
6. 복제 표시가 있으면 먼저 위의 10.13.3 조건으로 플래그를 믿을 수 있는지 보고, 다른 파일과 같은 물리 블록을 가리키는지 익스텐트 주소와 `refcnt` 로 확인합니다.

## 포렌식에서 중요한 점

압축 파일은 데이터 포크(파일 익스텐트)가 비어 있고 내용이 확장 속성이나 리소스 포크에 들어 있어서 [2], 익스텐트만 보는 도구는 이런 파일을 크기 0으로 보여 줄 수 있습니다. 또 압축된 내용은 원시 블록에서 평문으로 보이지 않으므로 키워드 검색이나 카빙을 할 때는 압축을 푼 뒤에 찾습니다.

`refcnt` 가 0이 되어야 익스텐트를 지울 수 있으므로 [1], 복제본이 남아 있으면 원본을 지워도 그 데이터 블록은 풀리지 않습니다. 이 규칙은 지운 파일의 내용을 복제본에서 다시 찾을 수 있는지 판단할 때 씁니다.

`INODE_WAS_CLONED` 는 그 아이노드가 다른 아이노드를 복제해서 만들어졌다는 기록이지만 [1], 원본이 어느 파일인지는 이 플래그에 적히지 않습니다. 원본 후보는 같은 물리 블록을 가리키는 다른 아이노드를 찾아 좁히고, 보고서에는 "이 파일의 데이터 블록을 다른 파일과 함께 쓰고 있다"처럼 구조로 확인되는 만큼만 씁니다.

## 함정

`INODE_WAS_EVER_CLONED` 는 macOS 10.13.3 전에 잘못 켜진 경우가 있으므로 [1], 복제 정보 필드가 0인 볼륨에서는 이 플래그 하나로 복제 이력을 말하지 않습니다.

`uncompressed_size` 는 아이노드와 decmpfs 헤더 두 곳에 있지만, 아이노드 쪽 필드는 10.15 전 Apple 구현이 무시했으므로 [1] 크기는 decmpfs 헤더 쪽을 기준으로 삼습니다.

매직은 디스크 바이트로 "fpmc"로 보이므로 [2][5], "cmpf"로 원시 검색하면 속성을 찾지 못합니다. 방식 5와 데이터 없는 파일 형식은 뜻이 밝혀지지 않은 값이라서 [2], 도구가 이런 파일을 읽지 못해도 파일이 손상됐다고 단정하지 않습니다.

## 도구

mac_apt는 zlib·LZVN·LZFSE로 압축된 파일을 읽습니다 [6]. 방식 13·14(LZBITMAP)는 이 목록에 없어서, 이런 파일을 만나면 도구가 내용을 풀었는지 크기부터 확인합니다.

## 참고 문헌

1. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
2. Joachim Metz, libfsapfs — Apple File System (APFS) 형식 문서 (개정 0.0.18, 2026년 8월) — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
3. Apple, Apple File System Guide — Features (보관 문서, 2018-06-04) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/Features/Features.html
4. Apple, Apple File System Guide — Frequently Asked Questions (보관 문서, 2018-06-04) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html
5. Apple xnu, bsd/sys/decmpfs.h — https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/sys/decmpfs.h
6. mac_apt README, Yogesh Khatri (v1.33.2) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/README.md
