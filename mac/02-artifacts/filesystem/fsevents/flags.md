---
title: "이벤트 플래그 읽기"
parent: "파일 시스템 이벤트"
grand_parent: "아티팩트 · 파일 시스템"
nav_order: 950
---

# 이벤트 플래그 읽기 (Flags)

FSEvents 레코드의 플래그 필드는 4바이트짜리 비트 묶음이고, 한 레코드에 여러 비트가 함께 켜집니다. 디스크에는 little-endian으로 들어 있지만 도구마다 읽는 바이트 순서가 달라서 같은 값이 다른 16진수로 보이고, 커널 헤더와 공개 API에 있는 비슷한 이름도 디스크 값과 숫자가 맞지 않습니다.

## 플래그 필드 찾기

플래그는 레코드 고정 부분의 오프셋 8부터 4바이트이고, 레코드 전체 구조는 [파일 형식 (.fseventsd)](format.md)에 있습니다. 한 레코드에 여러 플래그가 함께 켜지고 [2], 값은 아래 대조표의 비트별로 나눠 읽습니다. FSEventsParser는 플래그가 0이면 `None` 으로 보여 주고, 이름을 붙이지 않은 비트 11개(빅엔디언 값 0x08, 0x10, 0x40, 0x80, 0x100, 0x200, 0x400, 0x2000, 0x80000, 0x200000, 0x800000)는 `NOT_USED-0x...` 로 보여 줍니다 [2].

## 디스크 값 대조표

libyal 문서 [1]는 플래그를 little-endian 정수로 읽은 값으로 적고, FSEventsParser [2]는 같은 4바이트를 빅엔디언(`>I`)으로 읽은 값으로 적습니다. 그래서 두 표의 16진수는 바이트 순서만 뒤집혀 있고, 아래 표는 바이트를 뒤집어 두 값을 한 줄씩 맞춘 것입니다.

| 디스크 값 (LE) [1] | libyal 이름 [1] | FSEventsParser 값 (BE) · 이름 [2] |
|---|---|---|
| 0x00000001 | Created (FSE_CREATE_FILE) | 0x01000000 Created |
| 0x00000002 | Removed (FSE_DELETE) | 0x02000000 Removed |
| 0x00000004 | InodeMetadataModified (FSE_STAT_CHANGED) | 0x04000000 InodeMetaMod |
| 0x00000008 | Renamed (FSE_RENAME) | 0x08000000 Renamed |
| 0x00000010 | Modified (FSE_CONTENT_MODIFIED) | 0x10000000 Modified |
| 0x00000020 | Exchange (FSE_EXCHANGE) | 0x20000000 Exchange |
| 0x00000040 | FinderInfoModified (FSE_FINDER_INFO_CHANGED) | 0x40000000 FinderInfoMod |
| 0x00000080 | DirectoryCreated (FSE_CREATE_DIR) | 0x80000000 FolderCreated |
| 0x00000100 | PermissionChanged (FSE_CHOWN) | 0x00010000 PermissionChange |
| 0x00000200 | ExtendedAttributeModified (FSE_XATTR_MODIFIED) | 0x00020000 ExtendedAttrModified |
| 0x00000400 | ExtendedAttributeRemoved (FSE_XATTR_REMOVED) | 0x00040000 ExtendedAttrRemoved |
| 0x00000800 | FSE_DOCID_CREATED (설명 없음) | 0x00080000 NOT_USED |
| 0x00001000 | DocumentRevision (FSE_DOCID_CHANGED) | 0x00100000 DocumentRevisioning |
| 0x00002000 | Unmount acknowledgment required (FSE_UNMOUNT_PENDING) | 0x00200000 NOT_USED |
| 0x00004000 | ItemCloned (FSE_CLONE) | 0x00400000 ItemCloned (macOS High Sierra) |
| 0x00010000 | FSE_MODE_CLONE | 0x00000100 NOT_USED |
| 0x00020000 | FSE_TRUNCATED_PATH | 0x00000200 NOT_USED |
| 0x00040000 | FSE_REMOTE_DIR_EVENT | 0x00000400 NOT_USED |
| 0x00080000 | LastHardLinkRemoved (FSE_MODE_LAST_HLINK) | 0x00000800 LastHardLinkRemoved |
| 0x00100000 | IsHardLink (FSE_MODE_HLINK) | 0x00001000 HardLink |
| 0x00400000 | IsSymbolicLink | 0x00004000 SymbolicLink |
| 0x00800000 | IsFile | 0x00008000 FileEvent |
| 0x01000000 | IsDirectory | 0x00000001 FolderEvent |
| 0x02000000 | Mount | 0x00000002 Mount |
| 0x04000000 | Unmount | 0x00000004 Unmount |
| 0x20000000 | EndOfTransaction | 0x00000020 EndOfTransaction |

이름으로 보면 표의 윗부분(0x00000001~0x00004000)은 무엇이 바뀌었는지를 나타내고, IsSymbolicLink·IsFile·IsDirectory 같은 이름은 바뀐 대상이 어떤 종류인지를 나타냅니다.

## 바이트 순서 따라가기

아래 4바이트는 실제 데이터가 아니라 명세 [1]로 만든 예시이고, [파일 형식 (.fseventsd)](format.md)의 헥스 예시에 나온 플래그 필드와 같은 값입니다.

```
디스크 바이트      01 00 80 00
LE로 읽은 값       0x00800001 = 0x00000001 (Created) + 0x00800000 (IsFile)
BE로 읽은 값       0x01008000 = 0x01000000 (Created) + 0x00008000 (FileEvent)
```

두 값의 16진수는 다르지만 뜻은 "파일이 만들어졌다" 로 같습니다. 한 도구가 보여 준 16진수를 다른 도구의 표에 그대로 대면 전혀 다른 플래그로 읽힙니다. 16진수를 옮겨 적을 때는 어느 바이트 순서로 읽은 값인지 함께 적습니다.

## 커널 정의와 맞춰 보기

xnu 커널의 `bsd/sys/fsevents.h` 는 이벤트 종류를 비트가 아니라 번호로 정의합니다 [4].

```
FSE_CREATE_FILE          0     FSE_XATTR_MODIFIED     9
FSE_DELETE               1     FSE_XATTR_REMOVED     10
FSE_STAT_CHANGED         2     FSE_DOCID_CREATED     11
FSE_RENAME               3     FSE_DOCID_CHANGED     12
FSE_CONTENT_MODIFIED     4     FSE_UNMOUNT_PENDING   13   (주석 "iOS-only")
FSE_EXCHANGE             5     FSE_CLONE             14
FSE_FINDER_INFO_CHANGED  6     FSE_MAX_EVENTS        16
FSE_CREATE_DIR           7     FSE_ACTIVITY          15
FSE_CHOWN                8
```

디스크 값 0x1~0x4000은 이 번호 n을 `1<<n` 으로 옮긴 값과 하나하나 맞고, 예를 들어 FSE_CLONE은 14번이라 디스크 값 0x4000이 됩니다 [1][4].

이벤트 종류 번호와 따로 붙는 수식 비트는 사정이 다릅니다. 커널 헤더는 FSE_MODE_HLINK를 `1U<<31`, FSE_MODE_LAST_HLINK를 `1U<<30`, FSE_REMOTE_DIR_EVENT를 `1U<<29`, FSE_TRUNCATED_PATH를 `1U<<28`, FSE_MODE_CLONE을 `1U<<27` 로 정의하는데, 이 값은 위 대조표의 디스크 값과 다릅니다 [4]. 디스크 값 0x00100000 같은 비트는 커널과 이름만 같을 뿐이라서 [1], 커널 헤더의 숫자로 디스크 값을 풀면 틀립니다.

## 공개 API 이름과 섞지 않기

앱 개발자가 쓰는 공개 API에는 `FSEventStreamEventFlags` 라는 이름의 플래그 묶음(`enum : unsigned int`, macOS 10.5 이상)이 있고, 상수 이름은 모두 `kFSEventStreamEventFlag` 로 시작합니다 [5].

```
None, MustScanSubDirs, UserDropped, KernelDropped, EventIdsWrapped,
HistoryDone, RootChanged, Mount, Unmount, ItemChangeOwner, ItemCreated,
ItemFinderInfoMod, ItemInodeMetaMod, ItemIsDir, ItemIsFile,
ItemIsHardlink, ItemIsLastHardlink, ItemIsSymlink, ItemModified,
ItemRemoved, ItemRenamed, ItemXattrMod, OwnEvent, ItemCloned
```

이름은 디스크 대조표와 비슷해 보이지만, 이 API 문서에는 상수의 숫자 값과 상수별 도입 버전이 나와 있지 않습니다 [5]. 디스크 값을 API 상수 값으로 풀지 말고 위 대조표로 풉니다.

API 쪽 플래그 가운데 몇 개는 기록이 빠지거나 합쳐졌다는 뜻이라서 알아 둘 만합니다. 한 디렉터리와 그 하위 디렉터리에서 거의 동시에 일어난 이벤트가 하나로 합쳐지면 MustScanSubDirs가 붙고, 그 경로는 하위까지 다시 살펴야 합니다 [3]. KernelDropped와 UserDropped는 커널과 데몬 사이 통신 오류로 이벤트가 빠졌다는 뜻이고, 이때 MustScanSubDirs도 함께 켜집니다 [3]. 위 디스크 대조표에는 이 세 이름에 해당하는 항목이 없습니다. 기록이 합쳐지거나 빠지는 일이 해석에 주는 영향은 [해석 함정 (Pitfalls)](pitfalls.md)에서 다룹니다.

## 증거로서 의미

플래그는 그 경로에 어떤 종류의 변경이 기록됐는지와 대상이 파일·디렉터리·심볼릭 링크·하드 링크 가운데 무엇인지를 알려 줍니다. 같은 경로에 Created와 Removed가 켜져 있으면 그 경로에 만들기와 지우기가 기록됐다고 말할 수 있지만, 레코드에 두 동작의 순서를 적는 필드는 없습니다. Renamed도 이름 바꾸기가 기록됐다는 데까지만 알려 줍니다.

레코드에는 경로와 이벤트 ID, 플래그(버전에 따라 노드 ID·UID)만 있어서 플래그만으로는 어느 프로그램이 바꿨는지, 언제 바꿨는지 알 수 없습니다. 짧은 시간 안의 변경이 한 레코드로 합쳐질 수 있어서 플래그 여러 개가 켜진 레코드를 동작 여러 번으로 세지 않습니다. 이 두 가지는 [해석 함정 (Pitfalls)](pitfalls.md)에서 자세히 다룹니다.

## 참고 문헌

1. libyal dtformats — MacOS File System Events Disk Log Stream format — https://github.com/libyal/dtformats/blob/main/documentation/MacOS%20File%20System%20Events%20Disk%20Log%20Stream%20format.asciidoc
2. FSEventsParser 4.1 소스 (Nicole Ibrahim) — https://raw.githubusercontent.com/dlcowen/FSEventsParser/master/FSEParser_V4.1.py
3. Apple, File System Events Programming Guide — Using the File System Events API — https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/FSEvents_ProgGuide/UsingtheFSEventsFramework/UsingtheFSEventsFramework.html
4. Apple xnu bsd/sys/fsevents.h — https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/sys/fsevents.h
5. Apple Developer, FSEventStreamEventFlags (문서 JSON) — https://developer.apple.com/tutorials/data/documentation/coreservices/1455361-fseventstreameventflags.json
