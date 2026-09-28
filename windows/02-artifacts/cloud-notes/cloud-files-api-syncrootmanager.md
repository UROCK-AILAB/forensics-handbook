---
title: "클라우드 동기화 공통 구조"
parent: "아티팩트 · 클라우드·노트"
nav_order: 2160
---

# 클라우드 동기화 공통 구조 (Cloud Files API·SyncRootManager)

Windows 10 1709 부터 클라우드 파일 API (Cloud Files API) 가 들어 있습니다. 동기화 앱은 이 API 로 클라우드와 맞출 폴더를 동기화 루트 (sync root) 로 등록하고, 폴더 안 파일을 자리표시자 (placeholder) 로 만듭니다. 등록 정보는 SOFTWARE 하이브의 `SyncRootManager` 키에 남습니다. 파일마다 내용이 PC 에 있는지는 재분석 지점과 파일 특성 (file attribute) 에 남습니다.

> 아래 키 이름과 값의 예는 Windows 11 빌드 26200 의 OneDrive 동기화 루트(개인 계정 1개, 회사 계정 1개) 기준입니다. 다른 업체의 앱은 값이 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

클라우드 파일 API 의 중심은 미니필터 드라이버 `cldflt.sys` 이고, 이 드라이버는 NTFS 볼륨만 지원합니다. 동기화 앱은 동기화 루트마다 ID 를 하나 정하며, 이 등록은 `SyncRootManager` 키 아래에 루트마다 하위 키 하나로 남습니다.

자리표시자는 재분석 지점 (reparse point) 으로 만들며, 동기화 엔진과 `%systemroot%` 아래 프로그램이 아닌 앱에는 이 재분석 지점을 숨깁니다. 자리표시자는 파일 시스템 머리 1KB 만 차지합니다. 실행 중인 PC 에서 자리표시자를 읽으면 내용을 내려받는데, 이 동작을 내려받기 (hydration) 라고 부릅니다.

파일은 세 상태 가운데 하나입니다.

| 상태 | 뜻 |
|---|---|
| 자리표시자 | 내용이 PC 에 없습니다. 서비스에 닿을 때만 열립니다 |
| 전체 파일 | 사용자가 따로 고르지 않았는데 내용을 받은 파일입니다(파일을 열 때 등). 공간이 모자라면 시스템이 다시 비울 수 있습니다 |
| 고정된 전체 파일 | 사용자가 탐색기에서 직접 받은 파일입니다. 오프라인에서도 쓸 수 있습니다 |

포렌식에서 이 구조를 보는 이유는 두 가지입니다.

- 동기화 루트 등록으로 어느 사용자가 어느 폴더를 클라우드와 맞췄는지 봅니다.
- 파일 특성으로 파일 내용이 PC 에 있었는지 확인합니다. 파일 목록에 이름이 있어도 내용은 클라우드에만 있었을 수 있습니다.

## 위치와 버전별 차이

| 기록 | 위치 | 하이브·저장 위치 |
|---|---|---|
| 동기화 루트 등록 | `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\SyncRootManager\<동기화 루트 ID>` | `SOFTWARE` |
| 루트별 사용자와 폴더 | 위 키의 하위 키 `UserSyncRoots` | `SOFTWARE` |
| 필터 드라이버 서비스 | `HKLM\SYSTEM\CurrentControlSet\Services\CldFlt` | `SYSTEM` |
| 탐색 창 등록(OneDrive) | `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{CLSID}` | 사용자 `NTUSER.DAT` |
| 자리표시자 표시 | 동기화 폴더 안 파일의 재분석 지점과 파일 특성 | NTFS 파일 시스템 |

- 하이브 파일을 읽는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.
- 오프라인 `SYSTEM` 하이브에서 서비스 키를 찾는 법은 [서비스·드라이버](../persistence/services-drivers.md) 에 있습니다.

| Windows | 내용 |
|---|---|
| Windows 10 1709 (빌드 16299) 부터 | 클라우드 파일 API 가 생겼습니다 |
| 같은 빌드부터 | `StorageProviderSyncRootInfo.Id` 속성을 winrt-16299 부터 쓸 수 있습니다[2] |
| Windows 11 빌드 26200 | 이 페이지의 OneDrive 키 이름과 값의 예는 이 빌드 기준입니다 |

### 업체별로 이 API 를 쓰는지

| 앱 | 클라우드 파일 API 사용 | 근거 |
|---|---|---|
| OneDrive | 씁니다 | [원드라이브](onedrive/index.md) |
| 아이클라우드 | 실제 기기에서 확인합니다. 저장 위치를 다른 드라이브로 옮기려면 그 드라이브가 NTFS 여야 합니다. `cldflt.sys` 가 NTFS 만 지원한다는 점과 들어맞지만 직접 근거는 아닙니다 | [아이클라우드](icloud-for-windows.md) |
| 구글 드라이브 | 설정 `DefaultMountPoint` 가 드라이브 문자나 경로를 정합니다. 가상 드라이브 방식인지 이 API 방식인지는 실제 기기에서 확인합니다 | [구글 드라이브](drivefs-backup-and-sync.md) |
| 드롭박스 | 실제 기기에서 확인합니다 | [드롭박스](dropbox.md) |
| 네이버 MYBOX | 실제 기기에서 확인합니다 | [네이버 MYBOX](naver-mybox.md) |

실제 기기에서는 `SyncRootManager` 하위 키 이름의 앞부분을 보면 어느 공급자가 등록했는지 알 수 있습니다. 아래 "동기화 루트 ID" 절의 형식을 따릅니다.

## 구조

### 동기화 루트 ID

형식은 아래와 같습니다[2].

```
[Storage Provider ID]![Windows SID]![Account ID]
```

- 예: `OneDrive!S-1-1234!Personal`[2]
- ID 는 최대 174자이고, 이보다 길면 `ERROR_INSUFFICIENT_BUFFER` 오류가 날 수 있습니다.
- 실제 OneDrive 키 이름에는 이 형식 뒤에 `|` 와 32자리 16진 값이 더 붙습니다.
- 예: `OneDrive!<SID>!Personal|<32자리 16진>`, `OneDrive!<SID>!Business1|<32자리 16진>`
- 뒤에 붙은 16진 값의 뜻은 키 이름만으로 알 수 없습니다. OneDrive 에서 이 값을 다른 키와 잇는 법은 [원드라이브](onedrive/index.md) 에 있습니다.

### `SyncRootManager` 동기화 루트 키

동기화 루트마다 하위 키가 하나 있습니다. OneDrive 키 안의 값은 아래와 같습니다.

| 값 | 형식 | 내용 |
|---|---|---|
| `DisplayNameResource` | REG_SZ | 탐색기에 보이는 이름 |
| `IconResource` | REG_SZ | 아이콘 자원입니다. 동기화 앱 실행 파일 경로가 들어 있습니다. 예: `C:\Program Files\Microsoft OneDrive\OneDrive.exe,-501` |
| `Flags` | DWORD | 1314(10진) 인 예가 있습니다. 비트의 뜻은 단정하지 않고 값만 적습니다 |
| `Handler`, `BannerNotificationHandler`, `CustomStateHandler`, `ThumbnailProvider`, `UriHandler`, `ShareHandler`, `CopyHook`, `SuggestionHandlerFactory`, `SearchHandlerFactory`, `StorageProviderStatusUISourceFactory` | REG_SZ | CLSID 입니다 |
| `AUMID` | REG_SZ | 앱 ID 입니다. 예: `Microsoft.OneDriveSync_8wekyb3d8bbwe!OneDrive` |
| `Cid`, `TenantName` | REG_SZ | OneDrive 회사 계정 키에 있는 값입니다. 다른 업체도 쓰는지는 실제 데이터로 확인합니다 |

- `CopyHook`, `ShareHandler`, `SearchHandlerFactory` 는 동기화 루트 레지스트리 키에 두는 값이고, 데이터는 COM 서버의 CLSID 입니다[3].
- CLSID 를 읽는 법은 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에 있습니다.
- OneDrive 가 이 키에 적는 값의 뜻은 [원드라이브](onedrive/index.md) 에서 다룹니다.

### `UserSyncRoots` 하위 키

| 항목 | 내용 |
|---|---|
| 값 이름 | 사용자 SID |
| 값 데이터 | 동기화 폴더 전체 경로 (REG_SZ). 예: `C:\Users\<사용자>\OneDrive - <회사 이름>` |

`SyncRootManager` 는 HKLM 에 있습니다. 그런데도 키 이름과 `UserSyncRoots` 에 사용자 SID 가 들어갑니다. 그래서 `SOFTWARE` 하이브 하나로 어느 사용자가 어느 폴더를 동기화 루트로 썼는지 볼 수 있을 것으로 보입니다.

### 탐색 창 등록

- `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{CLSID}` 의 기본값은 동기화 루트 표시 이름입니다. 예: `OneDrive - Personal`.
- 다른 업체도 같은 방식으로 등록하는지는 실제 데이터로 확인합니다.
- OneDrive 는 `HKCU\Software\SyncEngines\Providers\OneDrive\<ID>` 에도 `MountPoint`, `LastModifiedTime`, `UrlNamespace`, `LibraryType`, `CID` 같은 값을 적습니다. 이 키는 OneDrive 전용으로 보입니다. 다른 업체도 `HKCU\Software\SyncEngines\Providers` 아래에 키를 두는지는 실제 데이터로 확인합니다.

### 필터 드라이버 `CldFlt`

서비스 키 값은 아래와 같습니다.

| 값 | 데이터 |
|---|---|
| `Start` | 2 |
| `Type` | 2 |
| `ImagePath` | `system32\drivers\cldflt.sys` |
| `DisplayName` | `Windows Cloud Files Filter Driver` |

`Start`·`Type` 숫자의 뜻은 [서비스·드라이버](../persistence/services-drivers.md) 에서 다룹니다.

### 재분석 태그

- OneDrive 폴더에서 이미 내려받은 파일(`.pst`, `.lnk`)을 `fsutil reparsepoint query` 로 보면 재분석 태그가 모두 `0x9000601A` 입니다.
- 내려받은 뒤에도 재분석 지점은 그대로 남습니다.
- `0x9000601A` 의 이름은 `IO_REPARSE_TAG_CLOUD_6` 입니다[4].
- `0x9000001A`(`IO_REPARSE_TAG_CLOUD`)부터 `0x9000F01A`(`IO_REPARSE_TAG_CLOUD_F`)까지 16개는 모두 클라우드 파일 필터 (Cloud Files filter) 의 태그입니다[4]. 가운데 자리(`1`~`F`)의 뜻은 명세에 없습니다.
- 그래서 이 16개 값 가운데 하나가 보이면 클라우드 파일 필터가 관리하는 파일로 봅니다. 어느 앱이 관리하는지는 태그만으로 판별하지 않습니다.
- 재분석 지점이 MFT 에 어떻게 저장되는지는 [NTFS 구조](../../01-foundations/disk-volume/ntfs/index.md) 에 있습니다.

### 파일 특성 값

아래는 파일 특성 값의 정의입니다[1]. 이름 앞의 `FILE_ATTRIBUTE_` 는 생략했습니다.

| 값 | 이름 | 설명 |
|---|---|---|
| `0x20` | `ARCHIVE` | — |
| `0x200` | `SPARSE_FILE` | 희소 파일입니다 |
| `0x400` | `REPARSE_POINT` | 재분석 지점이 붙은 파일·디렉터리, 또는 심볼릭 링크 |
| `0x1000` | `OFFLINE` | 파일 데이터를 바로 쓸 수 없습니다. 데이터를 오프라인 저장소로 옮겼습니다. 원격 저장소 (Remote Storage) 같은 계층형 저장소 관리 소프트웨어가 이 값을 씁니다 |
| `0x40000` | `RECALL_ON_OPEN` | 디렉터리 열거 구조(`FILE_DIRECTORY_INFORMATION`, `FILE_BOTH_DIR_INFORMATION` 등)에만 나타납니다. 켜져 있으면 로컬에 실체가 없는 가상 항목입니다. 열면 원격 저장소에서 일부라도 가져옵니다 |
| `0x80000` | `PINNED` | 사용자가 항목을 로컬에 늘 온전히 두려 한다는 뜻입니다 |
| `0x100000` | `UNPINNED` | 쓰고 있을 때만 로컬에 온전히 둔다는 뜻입니다 |
| `0x400000` | `RECALL_ON_DATA_ACCESS` | 로컬에 데이터가 다 있지 않습니다. 일부만 있는 희소 파일일 수 있습니다. 읽으면 원격 저장소에서 가져옵니다. 커널 모드 호출자만 켤 수 있습니다 |

`PINNED` 와 `UNPINNED` 는 계층형 저장소 관리 소프트웨어용 값입니다[1]. 동기화 앱이 이 두 값을 같은 뜻으로 쓴다고 단정하지 않습니다.

OneDrive 폴더 파일의 특성 값 조합 예는 아래와 같습니다.

| 파일 | 특성 값 | 켜진 특성 | 풀이 |
|---|---|---|---|
| 표본 400개 가운데 398개 | `0x401620` | `ARCHIVE`, `SPARSE_FILE`, `REPARSE_POINT`, `OFFLINE`, `RECALL_ON_DATA_ACCESS` | 온라인 전용 자리표시자로 보입니다 |
| 내려받은 `.pst` | `0x420` | `ARCHIVE`, `REPARSE_POINT` | 내용이 PC 에 있는 파일입니다 |
| `.lnk` 한 개 | `0x180420` | `ARCHIVE`, `REPARSE_POINT`, `PINNED`, `UNPINNED` | `PINNED` 와 `UNPINNED` 가 함께 켜져 있어 뜻을 단정하지 않습니다 |

디스크 이미지에서 파일 특성을 읽는 법은 [마스터 파일 테이블](../filesystem/mft.md) 에 있습니다.

## 증거로서 의미

### 증명하는 것

- `SyncRootManager` 에 하위 키가 있으면, 그 공급자의 동기화 루트가 이 PC 에 등록돼 있었습니다.
- 키 이름 앞부분으로 어느 공급자가 등록했는지 봅니다.
- `IconResource` 에 동기화 앱 실행 파일 경로가 있으므로, 어떤 프로그램이 등록했는지도 알 수 있을 것으로 보입니다.
- `UserSyncRoots` 로 어느 사용자 SID 가 어느 폴더를 동기화 루트로 썼는지 봅니다.
- 파일 특성에 `OFFLINE` 이나 `RECALL_ON_DATA_ACCESS` 가 켜져 있으면, 그 시점에 로컬에 내용이 다 있지 않았습니다.
- 내려받은 파일에는 `OFFLINE` 과 `RECALL_ON_DATA_ACCESS` 가 없습니다.

### 증명하지 못하는 것

- 등록 키만으로 어떤 파일을 올리거나 내려받았다고 쓰지 않습니다. 파일 단위 기록은 각 앱의 DB 와 로그에서 찾습니다.
- 키가 없다고 그 앱을 쓰지 않았다고 단정하지 않습니다. OneDrive 설정에 연결이 끊긴 회사 계정(`Business2`) 흔적이 남아 있어도, `SyncRootManager` 에는 그 계정 키가 없을 수 있습니다.
- 연결을 끊으면 키가 지워지는 것으로 보입니다.
- 자리표시자의 파일 이름·크기·시각이 보여도, 내용이 PC 에 있었다는 뜻은 아닙니다.
- 클라우드 파일 API 를 쓰지 않는 앱의 동기화 폴더는 이 키에 남지 않습니다.
- 그 시각에 누가 PC 앞에 있었는지는 알 수 없습니다.

## 시각 해석

- `SyncRootManager` 값 가운데 시각 값은 없습니다.
- 레지스트리 키에는 마지막 쓰기 시각이 있습니다. 그 시각을 동기화 루트를 처음 등록한 시각으로 읽지 않습니다. 등록한 뒤에 값이 바뀌었을 수 있습니다.
- 디스크 이미지에서 자리표시자의 이름·크기·시각은 보이지만 내용은 없습니다.
- 자리표시자의 파일 시스템 시각이 클라우드 쪽 시각을 옮겨 적은 것인지, PC 에서 자리표시자를 만든 시각인지는 각 앱의 DB 시각과 맞춰 본 뒤에 정합니다.
- 시각 값을 바꾸는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.

## 함정과 한계

- **실행 중인 PC 에서 자리표시자를 읽지 않습니다.** 해시를 구하거나 복사하려고 읽으면 내용을 내려받습니다. 그러면 파일이 자리표시자에서 전체 파일로 바뀝니다.
- **희소 파일을 어떻게 뽑았는지 기록합니다.** 자리표시자에는 희소 특성이 붙습니다. 희소 파일을 구멍을 건너뛰고 뽑으면 내용이 앞으로 밀립니다. 구멍을 0 으로 채워 뽑으면 크기와 해시가 달라집니다. 같은 문제는 [USN 변경 저널](../filesystem/usnjrnl.md) 을 뽑을 때도 생깁니다.
- **`0x40000` 을 단정하지 않습니다.** 이 값은 `FILE_ATTRIBUTE_EA` 와 같고, `EA` 는 내부 전용 값입니다[1]. `RECALL_ON_OPEN` 은 디렉터리 열거 구조에만 나타나므로, 다른 곳에서 본 `0x40000` 은 `RECALL_ON_OPEN` 이라고 단정할 수 없습니다.
- **도구에 따라 재분석 지점이 안 보일 수 있습니다.** 동기화 엔진과 `%systemroot%` 아래 프로그램이 아닌 앱에는 재분석 지점을 숨깁니다[3]. 그래서 실행 중인 PC 에서 별도 설치한 도구로 보면 재분석 지점이 없는 것처럼 나올 수 있습니다.
- **내용은 다른 곳에서 찾습니다.** 디스크 이미지에서 자리표시자 내용은 없습니다. 내용은 동기화 앱의 캐시나 클라우드 쪽에서 찾아야 합니다.
- **지워진 키를 찾는 곳.** 지운 레지스트리 키는 하이브 여유 공간, 트랜잭션 로그, 볼륨 섀도 복사본에서 찾아볼 수 있다는 것이 일반론입니다. 이 키가 실제로 되살아나는지는 실제 데이터로 확인합니다. 섀도 복사본을 다루는 법은 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에 있습니다.
- **뜻을 단정할 수 없는 값이 많습니다.** `Flags` 비트, 키 이름 뒤 32자리 16진, 재분석 태그 가운데 자리(`CLOUD_1`~`CLOUD_F`)가 그렇습니다. 보고서에는 값만 적고 뜻을 짐작해 쓰지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

**파일 특성 값.** 아래는 위 상수로 만든 예시입니다. 위 표의 첫 조합과 같은 값이지만, 특정 파일에서 바이트를 옮긴 것은 아닙니다.

```
바이트 (리틀 엔디언):  20 16 40 00
뒤집어 읽기:           0x00401620

0x00400000  RECALL_ON_DATA_ACCESS
0x00001000  OFFLINE
0x00000400  REPARSE_POINT
0x00000200  SPARSE_FILE
0x00000020  ARCHIVE
----------
0x00401620
```

`0x1000` 과 `0x400000` 이 켜져 있으므로 내용이 로컬에 다 있지 않은 자리표시자로 봅니다. 내려받은 파일이라면 `20 04 00 00`(`0x420`) 처럼 두 값이 빠집니다(위 표의 내려받은 `.pst` 값).

**동기화 루트 ID.** 아래는 위 예를 형식대로 나눈 것입니다.

```
OneDrive!S-1-1234!Personal
└ 공급자 ┘└ SID ┘└ 계정 ┘
```

- 첫 번째 `!` 앞이 공급자 ID 입니다. 실제 기기에서 이 부분을 모으면 동기화 루트를 등록한 앱 목록이 나옵니다.
- SID 는 [사용자 프로필 목록](../system-account/profilelist.md) 에서 사용자 이름으로 바꿉니다.
- `UserSyncRoots` 의 값 데이터는 REG_SZ 문자열입니다. 바이트로 읽을 때의 인코딩은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에 있습니다.

### 공개 도구로 한 번

1. `SOFTWARE`, `SYSTEM`, 사용자 `NTUSER.DAT` 하이브를 사본으로 뜹니다. 하이브 옆의 트랜잭션 로그 파일도 함께 뜹니다.
2. 레지스트리 하이브 뷰어로 `SOFTWARE` 의 `Microsoft\Windows\CurrentVersion\Explorer\SyncRootManager` 를 엽니다.
3. 하위 키 이름을 모두 적고, 첫 번째 `!` 앞 공급자 ID 로 묶습니다.
4. 키마다 `UserSyncRoots` 의 SID 와 폴더 경로, `IconResource` 의 실행 파일 경로를 표로 만듭니다.
5. `SYSTEM` 하이브에서 `CldFlt` 서비스 키를 봅니다.
6. MFT 파서로 동기화 폴더 아래 파일의 특성 값을 뽑습니다. `0x1000`·`0x400000` 이 켜진 파일과 꺼진 파일을 나눠 셉니다.

실행 중인 PC 에서는 Windows 에 들어 있는 명령으로도 볼 수 있습니다.

```
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\SyncRootManager" /s
fsutil reparsepoint query "<내려받은 파일 경로>"
```

`fsutil` 은 내용이 이미 PC 에 있는 파일에만 씁니다. 온라인 전용 자리표시자에는 쓰지 않습니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 각 앱의 기록 | 동기화 폴더 위치, 계정, 파일 단위 기록을 봅니다. `UserSyncRoots` 경로와 맞춰 봅니다 | [원드라이브](onedrive/index.md), [구글 드라이브](drivefs-backup-and-sync.md), [드롭박스](dropbox.md), [네이버 MYBOX](naver-mybox.md), [아이클라우드](icloud-for-windows.md) |
| 사용자 프로필 목록 | `UserSyncRoots` 의 SID 가 어느 사용자인지 봅니다 | [사용자 프로필 목록](../system-account/profilelist.md) |
| 설치 프로그램 | `IconResource` 의 실행 파일이 어느 프로그램인지, 언제 깔았는지 봅니다 | [설치 프로그램](../system-account/uninstall.md) |
| 마스터 파일 테이블 | 동기화 폴더 안 파일의 특성과 시각을 봅니다 | [마스터 파일 테이블](../filesystem/mft.md) |
| USN 변경 저널 | 동기화 폴더 안 파일이 바뀐 기록을 찾습니다. 내려받기 때 어떤 변경 이유가 남는지는 실제 데이터로 확인합니다 | [USN 변경 저널](../filesystem/usnjrnl.md) |
| 셸백·바로가기 파일 | 동기화 폴더를 둘러보거나 그 안 파일을 연 기록을 봅니다 | [셸백](../file-folder-usage/shellbags/index.md), [바로가기 파일](../file-folder-usage/lnk.md) |

반출 여부를 따지는 흐름은 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에 있습니다.

## 실습

클라우드 동기화 앱을 쓴 공개 시험 데이터(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다.

1. `SyncRootManager` 아래 하위 키는 몇 개입니까? 공급자 ID 는 몇 종류입니까?
2. 키 이름에 문서 형식 뒤로 `|` 와 16진 값이 붙어 있습니까? 모든 공급자가 그렇습니까?
3. `UserSyncRoots` 의 SID 는 몇 명입니까? 각 SID 를 사용자 이름으로 바꿉니다.
4. `IconResource` 의 실행 파일 경로를 설치 프로그램 목록과 맞춰 봅니다. 목록에 없는 프로그램이 있습니까?
5. 동기화 폴더 아래 파일 가운데 `OFFLINE`·`RECALL_ON_DATA_ACCESS` 가 켜진 파일은 몇 개입니까? 내용이 PC 에 있는 파일은 몇 개입니까?
6. `PINNED` 와 `UNPINNED` 가 함께 켜진 파일이 있습니까? 있다면 어떤 파일입니까?

## 참고 문헌

1. Microsoft Learn, "File Attribute Constants (WinNT.h)" (2025-09-23 갱신) — https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants
2. Microsoft Learn, "StorageProviderSyncRootInfo.Id Property (Windows.Storage.Provider)" — https://learn.microsoft.com/en-us/uwp/api/windows.storage.provider.storageprovidersyncrootinfo.id
3. Microsoft Learn, "Build a Cloud Sync Engine that Supports Placeholder Files" — https://learn.microsoft.com/en-us/windows/win32/cfapi/build-a-cloud-file-sync-engine
4. Microsoft Learn, [MS-FSCC] "Reparse Tags" (2.1.2.1) — https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/c8e77b37-3909-4fe6-a4ea-2b9d423b1ee4
