---
title: "HFS+ 구조"
parent: "기반 · 디스크·볼륨"
nav_order: 100
---

# HFS+ 구조 (HFS+)

## 한 줄 요약

HFS+ 는 볼륨 앞쪽 1024바이트 위치의 볼륨 헤더에서 출발해 할당 파일·카탈로그 파일·익스텐트 오버플로 파일·속성 파일 같은 특수 파일을 따라가며 읽는 Apple 의 예전 파일 시스템이고, 날짜는 1904년부터 센 초로 적지만 볼륨 헤더의 생성일만은 현지 시각으로 적습니다.

## 이 형식을 쓰는 아티팩트

HFS+ 볼륨은 파티션 유형이 HFS+ 인 파티션, 파일볼트를 켠 옛 맥의 Core Storage 컨테이너 안, 디스크 이미지 안에서 만납니다. 파티션 유형 GUID 는 [파티션 구조](gpt-partitions.md)에, 디스크 이미지 안의 볼륨을 꺼내는 법은 [디스크 이미지 형식](dmg-sparsebundle.md)에 정리했습니다. APFS 명세는 복구 볼륨 역할(`APFS_VOL_ROLE_RECOVERY`)을 "HFS+ 의 복구 파티션과 같은 용도" 라고 적어서, 오래된 맥의 복구 영역이 HFS+ 파티션으로 남아 있을 수 있습니다. 부팅 볼륨이 어느 macOS 버전부터 APFS 로 바뀌었는지, HFS+ 부팅을 언제까지 지원했는지는 이번에 확인한 자료에 없어서 적지 않습니다.

기준 명세는 Apple Technical Note TN1150 "HFS Plus Volume Format" 이고 마지막 개정은 2004-03-05 입니다. 파일 시스템 투명 압축 (decmpfs) 과 하드 링크처럼 이후에 붙은 기능은 libyal 의 libfshfs 문서로 보충했습니다.

## 구조

### 볼륨 헤더

볼륨 헤더는 볼륨 시작에서 1024바이트 위치에 512바이트 크기로 있고, 예비 볼륨 헤더는 볼륨 끝에서 1024바이트 앞에 있습니다. 볼륨의 처음 1024바이트와 마지막 512바이트는 예약 영역입니다. 시그니처는 HFS+ 가 `'H+'` (0x482B) 에 버전 4 이고, 대소문자를 가리는 HFSX 가 `'HX'` (0x4858) 에 버전 5 입니다.

| 오프셋 | 필드 | 설명 |
|---|---|---|
| 0 | signature (UInt16) | `'H+'` 또는 `'HX'` |
| 2 | version (UInt16) | 4 또는 5 |
| 4 | attributes (UInt32) | 볼륨 상태 비트 (아래 표) |
| 8 | lastMountedVersion (UInt32) | 저널 볼륨이면 `'HFSJ'` |
| 12 | journalInfoBlock (UInt32) | 저널 정보 블록의 할당 블록 번호 |
| 16 | createDate | 볼륨 생성일, **현지 시각** |
| 20 | modifyDate | 마지막 수정, GMT |
| 24 | backupDate | 마지막 백업, GMT |
| 28 | checkedDate | 마지막 검사, GMT |
| 32 | fileCount | 파일 수 |
| 36 | folderCount | 폴더 수 |
| 40 | blockSize | 할당 블록 크기 |
| 44 | totalBlocks | 전체 할당 블록 수 |
| 48 | freeBlocks | 빈 할당 블록 수 |
| 52 | nextAllocation | 다음 할당 위치 |
| 56 | rsrcClumpSize | 리소스 포크 기본 할당 단위 |
| 60 | dataClumpSize | 데이터 포크 기본 할당 단위 |
| 64 | nextCatalogID | 다음에 줄 카탈로그 노드 ID |
| 68 | writeCount | 쓰기 횟수 |
| 72 | encodingsBitmap (UInt64) | 쓰인 텍스트 인코딩 |
| 80 | finderInfo[8] (32바이트) | Finder 정보 |
| 112 | allocationFile (HFSPlusForkData, 80바이트) | 할당 파일 포크 |
| 192 | extentsFile | 익스텐트 오버플로 파일 포크 |
| 272 | catalogFile | 카탈로그 파일 포크 |
| 352 | attributesFile | 속성 파일 포크 |
| 432 | startupFile | 시작 파일 포크 (512 에서 끝) |

112 이후 오프셋은 TN1150 의 구조체 순서에 HFSPlusForkData 크기(8+4+4+8×8 = 80바이트)를 더해 계산한 값입니다. 포크 데이터 구조는 logicalSize(UInt64), clumpSize, totalBlocks, extents[8] 순서이고, 익스텐트 기술자 하나는 startBlock(UInt32) 과 blockCount(UInt32) 로 이루어집니다. 구조로 보아 익스텐트가 8개를 넘는 파일은 나머지 익스텐트를 익스텐트 오버플로 파일에 둡니다.

| attributes 비트 | 이름 | 뜻 |
|---|---|---|
| 8 | `kHFSVolumeUnmountedBit` | 정상적으로 마운트 해제함 |
| 11 | `kHFSBootVolumeInconsistentBit` | 부팅 볼륨이 일관되지 않음 |
| 13 | `kHFSVolumeJournaledBit` | 저널이 있음 |
| 15 | `kHFSVolumeSoftwareLockBit` | 소프트웨어 잠금 |

### 예약 카탈로그 노드 ID

HFS+ 는 파일과 폴더를 카탈로그 노드 ID (CNID) 로 구분하고, 앞 번호는 특수 파일에 예약해 둡니다.

| CNID | 이름 | 뜻 |
|---|---|---|
| 1 | `kHFSRootParentID` | 루트 폴더의 부모 |
| 2 | `kHFSRootFolderID` | 루트 폴더 |
| 3 | `kHFSExtentsFileID` | 익스텐트 오버플로 파일 |
| 4 | `kHFSCatalogFileID` | 카탈로그 파일 |
| 5 | `kHFSBadBlockFileID` | 불량 블록 파일 |
| 6 | `kHFSAllocationFileID` | 할당 파일 |
| 7 | `kHFSStartupFileID` | 시작 파일 |
| 8 | `kHFSAttributesFileID` | 속성 파일 |
| 14 | `kHFSRepairCatalogFileID` | 카탈로그 수리용 |
| 15 | `kHFSBogusExtentFileID` | 임시 익스텐트용 |
| 16 | `kHFSFirstUserCatalogNodeID` | 사용자 파일이 쓰는 첫 번호 |

### 특수 파일과 B-tree

할당 파일 (Allocation File) 은 할당 블록마다 사용 중인지 비었는지를 비트 하나로 표시하는 비트맵이고, 옛 HFS 의 볼륨 비트맵을 파일로 옮긴 것입니다. 카탈로그 파일과 속성 파일은 B-tree 이고 둘 다 최소 노드 크기가 4KB(`kHFSPlusCatalogMinNodeSize`, `kHFSPlusAttrMinNodeSize`) 이며, 카탈로그 B-tree 에는 `kBTBigKeysMask` 와 `kBTVariableIndexKeysMask` 가 켜져 있어야 합니다. B-tree 노드 종류는 `kBTLeafNode` -1, `kBTIndexNode` 0, `kBTHeaderNode` 1, `kBTMapNode` 2 입니다.

### 카탈로그 레코드

카탈로그 키는 keyLength(UInt16), parentID(CNID), nodeName(HFSUniStr255) 순서이고, 먼저 parentID 로 비교한 다음 이름으로 비교합니다. 파일 이름은 UTF-16 으로 최대 255자이고, 완전히 분해한 (decomposed) 형태를 정규 순서로 저장합니다. 정규화 차이는 [유니코드 정규화](../value-decoding/unicode-normalization.md)에서 다룹니다. 이름을 비교할 때 HFS+ 는 대소문자를 가리지 않고 HFSX 는 가립니다.

레코드 종류는 폴더 0x0001, 파일 0x0002, 폴더 스레드 0x0003, 파일 스레드 0x0004 입니다. HFS 에서는 파일 스레드 레코드가 선택이었지만 HFS+ 에서는 파일과 폴더 모두 스레드 레코드가 있어야 합니다. 파일 레코드 (HFSPlusCatalogFile) 의 배치는 다음과 같습니다.

| 오프셋 | 필드 | 설명 |
|---|---|---|
| 0 | recordType (SInt16) | 0x0002 |
| 2 | flags | 아래 플래그 |
| 4 | reserved1 | 예약 |
| 8 | fileID (CNID) | 파일 번호 |
| 12 | createDate | 생성 |
| 16 | contentModDate | 내용 수정 |
| 20 | attributeModDate | 메타데이터 변경 |
| 24 | accessDate | 마지막 읽기 (POSIX 용) |
| 28 | backupDate | 백업 |
| 32 | permissions (HFSPlusBSDInfo, 16바이트) | 소유자·권한 |
| 48 | userInfo (FileInfo) | Finder 정보 |
| 64 | finderInfo (ExtendedFileInfo) | 확장 Finder 정보 |
| 80 | textEncoding | 이름 인코딩 힌트 |
| 84 | reserved2 | 예약 |
| 88 | dataFork (HFSPlusForkData) | 데이터 포크 |
| 168 | resourceFork (HFSPlusForkData) | 리소스 포크 |

64 이후 오프셋은 TN1150 의 구조체 순서에 userInfo·finderInfo 가 16바이트씩이고 textEncoding 뒤에 4바이트 reserved2 가 있다는 점을 더해 계산한 값이고, 레코드 전체는 248바이트입니다. HFSPlusBSDInfo 안에서는 +0 ownerID, +4 groupID, +8 adminFlags(SF_ARCHIVED·SF_IMMUTABLE·SF_APPEND), +9 ownerFlags(UF_NODUMP·UF_IMMUTABLE·UF_APPEND·UF_OPAQUE), +10 fileMode, +12 special 이 차례로 오고, special 은 iNodeNum·linkCount·rawDevice 가 함께 쓰는 자리입니다. 파일 레코드 flags 에는 `kHFSFileLockedMask` 0x0001, `kHFSThreadExistsMask` 0x0002, 하드 링크 체인을 뜻하는 `kHFSHasLinkChainMask` 0x0020 이 있습니다.

### 하드 링크

파일 하드 링크는 type 이 `'hlnk'` (0x686C6E6B), creator 가 `'hfs+'` (0x6866732B) 인 파일로 보이고, 실제 데이터는 숨겨진 메타데이터 디렉터리 안에 `iNode` 뒤에 10진 번호를 붙인 이름의 간접 노드 (indirect node) 파일에 있습니다. 링크가 가리키는 번호는 HFSPlusBSDInfo 의 special.iNodeNum 에 들어 있습니다. TN1150 은 이 메타데이터 디렉터리가 루트 디렉터리에 있고 이름이 NUL 문자 네 개 뒤에 "HFS+ Private Data" 를 붙인 것이라고 적습니다. libyal 문서의 `/␀␀␀␀HFS+ Private Data` 는 보이지 않는 NUL 을 U+2400 기호로 바꿔 적은 표기라서, 이미지에서 바이트로 찾을 때는 NUL 로 찾습니다. 디렉터리 하드 링크의 구조는 확인하지 못해서 적지 않습니다.

### 속성 파일 레코드

속성 파일 키는 +0 키 크기(2바이트), +4 CNID(4바이트), +12 이름 글자 수(2바이트), +14 UTF-16 빅 엔디언 이름(끝에 널 문자 없음) 순서입니다. 레코드 종류는 0x10 인라인 데이터(`kHFSPlusAttrInlineData`), 0x20 포크 데이터(`kHFSPlusAttrForkData`), 0x30 익스텐트(`kHFSPlusAttrExtents`) 입니다. 키에 CNID 가 들어 있어서, 한 파일에 붙은 속성 레코드는 그 파일의 CNID 로 찾습니다.

### 투명 압축 (decmpfs)

압축한 파일에는 확장 속성 `com.apple.decmpfs` 가 붙고, 속성 값의 16바이트 헤더는 [압축 형식](../value-decoding/compression.md)에서 다룹니다. libfshfs 문서는 헤더 +4 의 압축 방식 번호를 아래처럼 적어서, LZFSE 와 LZBITMAP 번호까지 확인할 수 있습니다.

| 번호 | 방식 | 데이터 위치 |
|---|---|---|
| 3 | zlib | 속성 안 |
| 4 | zlib (64K 조각) | 리소스 포크 |
| 7 | LZVN | 속성 안 |
| 8 | LZVN | 리소스 포크 |
| 9 | 압축 안 함 | 속성 안 |
| 10 | 압축 안 함 | 리소스 포크 |
| 11 | LZFSE | 속성 안 |
| 12 | LZFSE | 리소스 포크 |
| 13 | LZBITMAP | 속성 안 |
| 14 | LZBITMAP | 리소스 포크 |

압축 블록을 푸는 법도 같은 페이지에서 다룹니다.

### 저널

볼륨 헤더 attributes 의 비트 13 이 켜져 있으면 저널 볼륨이고, journalInfoBlock 이 저널 정보 블록의 위치입니다. 저널 정보 블록은 flags 로 시작하고(0x1 파일 시스템 안에 있음, 0x2 다른 장치에 있음, 0x4 초기화 필요), 이어서 장치 시그니처(32바이트), 저널 오프셋(8바이트), 저널 크기(8바이트), 예약 영역(128바이트) 이 와서 TN1150 구조체로 계산하면 모두 180바이트입니다.

| 저널 헤더 오프셋 | 필드 |
|---|---|
| 0 | 시그니처 `JNLx` (0x4A4E4C78) |
| 4 | 엔디언 시그니처 0x12345678 |
| 8 | 첫 트랜잭션 시작 |
| 16 | 다음 트랜잭션 시작 |
| 24 | 저널 크기 |
| 32 | 블록 헤더 크기 |
| 36 | 체크섬 |
| 40 | 저널 헤더 크기 |

TN1150 에 따르면 저널 정보 블록은 루트 디렉터리의 `.journal_info_block` 파일에, 저널 헤더와 저널 버퍼는 같은 루트 디렉터리의 `.journal` 파일에 들어 있고, 두 파일은 디스크에서 각각 익스텐트 하나로 이어져 있습니다.

### HFS 래퍼

옛 HFS 볼륨 안에 HFS+ 볼륨을 넣은 래퍼 형태도 있습니다. 이때 래퍼의 `drEmbedSigWord` 가 `'H+'` 이고 `drEmbedExtent` 가 안쪽 볼륨의 위치를 가리키며, 그 공간은 래퍼의 불량 블록 파일에 기록해 두고 래퍼에는 소프트웨어 쓰기 금지를 겁니다.

## 읽는 법

아래 헥스는 명세로 만든 예시이고, 특정 검체에서 나온 값이 아닙니다. `NN` 은 값이 들어갈 자리를 뜻합니다.

```text
볼륨 시작 기준
오프셋  00 01 02 03  04 05 06 07  08 09 0A 0B  0C 0D 0E 0F
0400    48 2B NN NN  NN NN NN NN  NN NN NN NN  NN NN NN NN
        'H  +' 버전  attributes   lastMounted  journalInfoBlock
0410    NN NN NN NN  NN NN NN NN  NN NN NN NN  NN NN NN NN
        createDate   modifyDate   backupDate   checkedDate
        (현지 시각)  (GMT)        (GMT)        (GMT)
```

1. 볼륨 시작에서 1024바이트(0x400) 위치에 `'H+'` 나 `'HX'` 가 있는지 보고, 없으면 볼륨 끝에서 1024바이트 앞의 예비 볼륨 헤더를 봅니다.
2. 오프셋 40 의 blockSize 를 읽어 할당 블록 번호를 바이트 위치로 바꿀 준비를 합니다.
3. 오프셋 272 의 catalogFile 포크에서 익스텐트를 읽어 카탈로그 파일을 이어 붙이고, 노드마다 종류(헤더 1·인덱스 0·리프 -1)를 확인하며 인덱스 노드를 거쳐 리프 노드까지 내려갑니다.
4. 리프 노드의 레코드마다 키의 parentID 와 이름을 읽고, 레코드 종류가 0x0002 이면 파일 레코드 표대로 날짜와 포크를 읽습니다.
5. 포크의 익스텐트 8개로 부족하면 익스텐트 오버플로 파일(CNID 3) 에서 나머지를 찾고, 확장 속성은 속성 파일(CNID 8) 에서 같은 CNID 로 찾습니다.

HFS+ 날짜는 1904-01-01 00:00:00 GMT 부터 센 초를 부호 없는 32비트로 적어서 2040-02-06 06:28:15 GMT 까지 나타낼 수 있습니다. 카탈로그 레코드의 날짜는 GMT 이지만 볼륨 헤더의 createDate 만은 현지 시각입니다. TN1150 은 "볼륨 헤더의 생성일은 GMT 가 아니라 현지 시각으로 저장한다" 고 적고, 백업 도구 같은 프로그램이 볼륨 생성일을 볼륨 고유 식별자처럼 쓰기 때문이라고 이유를 댑니다. 옛 HFS 표준은 날짜를 현지 시각으로 적습니다. 시각 변환은 [맥의 시각 값](../value-decoding/mac-time-values.md)에서 다룹니다.

## 포렌식에서 중요한 점

파일 레코드에는 생성·내용 수정·메타데이터 변경·마지막 읽기·백업 날짜가 들어 있어서, 타임라인에 한 파일의 시각을 다섯 개까지 올릴 수 있습니다. 다만 TN1150 은 옛 Mac OS 가 accessDate 를 관리하지 않아서 거기서 만든 파일은 이 값이 0 이라고 적고, macOS 에서 이 값이 언제 바뀌는지는 이번 자료로 확인하지 못해서, 읽은 시각으로 단정하지 않고 다른 기록과 맞춰 봅니다. 타임라인에 올리는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)에서 다룹니다.

할당 파일은 블록마다 사용 여부를 표시하는 비트맵이라서, 비트가 꺼진 블록이 지운 파일 내용을 찾을 빈 영역입니다. 지운 파일의 카탈로그 레코드가 어떤 모양으로 남는지는 확인한 자료가 없어서, 복구 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)를 따릅니다.

저널은 메타데이터 변경을 담는 영역이라, 최근에 바뀐 카탈로그 블록의 이전 모습이 남아 있을 수 있어 삭제 직후 흔적을 찾을 때 출발점으로 삼을 만합니다. 이 판단은 해석이고, 저널을 복구하는 구체 절차와 기록이 얼마나 오래 남는지는 확인한 자료가 없습니다.

비정상 종료 여부는 볼륨 헤더에서 볼 수 있습니다. TN1150 에 따르면 쓰기용으로 마운트할 때 attributes 비트 8 (`kHFSVolumeUnmountedBit`) 을 끄고 마운트 해제의 마지막 단계에서 다시 켜서, 이 비트가 꺼져 있으면 정상적으로 마운트 해제하지 않았다는 뜻입니다. 다만 부팅 볼륨은 이 비트를 늘 켜 두고 비트 11 (`kHFSBootVolumeInconsistentBit`) 로 일관성을 표시하므로, 부팅 볼륨에서는 비트 11 을 봅니다. 마운트한 채로 확보한 이미지도 비트 8 이 꺼져 있을 수 있고, 저널 볼륨이라면 저널 내용이 아직 파일 시스템에 반영되지 않았을 수 있습니다(뒤 두 가지는 해석입니다). 볼륨 헤더가 손상됐으면 볼륨 끝 쪽의 예비 볼륨 헤더로 다시 읽습니다.

## 함정

볼륨 헤더의 createDate 를 다른 날짜처럼 GMT 로 읽으면 시간대만큼 어긋납니다. 이미지를 만든 맥의 시간대를 모르면 이 값은 대략적인 날짜로만 쓰고, 시간대 설정은 [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md)에서 확인합니다.

HFSX 는 이름을 비교할 때 대소문자를 가려서, 대소문자만 다른 두 파일이 한 폴더에 따로 있을 수 있습니다. 시그니처가 `'HX'` 인 볼륨에서 나온 파일 목록을 대소문자를 무시하는 환경으로 옮기면 한쪽이 덮이거나 합쳐지지 않는지 확인합니다. 볼륨 헤더 오프셋 112 이후나 파일 레코드의 dataFork·resourceFork 오프셋을 요약 자료에서 옮길 때는 틀린 값이 섞이기 쉬워서, TN1150 구조체의 필드 크기(포크 데이터 80바이트, reserved 필드 포함)로 직접 다시 계산해 봅니다.

크기가 0 인 파일이라도 `com.apple.decmpfs` 속성이 있으면 내용은 속성이나 리소스 포크에 들어 있습니다. 하드 링크 파일도 `'hlnk'` 파일 자체에는 데이터가 없어서, 간접 노드 파일을 따라가야 내용이 나옵니다. libfshfs 문서에 삭제된 카탈로그 레코드의 키 크기에 대한 문장이 있지만 맥락을 확인하지 못해서 판단 근거로 쓰지 않습니다.

## 도구

| 도구 | 쓰임 |
|---|---|
| Apple TN1150 | 볼륨 헤더, 카탈로그, 예약 CNID, 날짜 규칙의 기준 |
| libyal libfshfs 와 그 HFS 문서 | 하드 링크, 속성 파일 레코드, decmpfs, 저널 구조를 확인하고 HFS+ 볼륨을 읽을 때 씁니다 |
| 헥스 편집기 | 볼륨 헤더와 카탈로그 노드를 위 읽는 법 순서대로 직접 확인합니다 |

도구 이름은 예로 든 것이고, 도구가 현지 시각 createDate 나 하드 링크를 어떻게 보여 주는지는 [도구 검증](../../03-techniques/reporting/tool-validation.md) 방식으로 확인합니다.

## 참고 문헌

1. Apple Technical Note TN1150: HFS Plus Volume Format, https://developer.apple.com/library/archive/technotes/tn/tn1150.html
2. libyal libfshfs — Hierarchical File System (HFS), https://raw.githubusercontent.com/libyal/libfshfs/main/documentation/Hierarchical%20File%20System%20(HFS).asciidoc
3. Apple, Apple File System Reference (2020-06-22 판), https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
