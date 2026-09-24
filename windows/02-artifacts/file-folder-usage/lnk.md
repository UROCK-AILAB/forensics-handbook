# 바로가기 파일 (LNK)

## 한 줄 요약

바로가기 파일 (Shortcut File, LNK) 은 다른 파일이나 폴더를 가리키는 작은 파일입니다. 사용자가 탐색기에서 파일을 열면 윈도가 최근 항목 폴더에 LNK 를 자동으로 만듭니다. LNK 안에는 대상의 경로, 그때의 대상 시각과 크기, 대상이 있던 볼륨과 기계의 정보가 남습니다. 대상 파일을 지우거나 USB 를 뽑은 뒤에도 LNK 는 남습니다.

## 무엇을 기록하나 · 왜 생기나

### 두 갈래로 생깁니다

- **사람이나 프로그램이 만든 LNK**: 설치 프로그램이 바탕화면과 시작 메뉴에 만든 바로가기입니다. 사용자가 직접 만든 바로가기도 여기에 듭니다. 공격자가 메일 첨부나 USB 로 보낸 LNK 도 이쪽입니다.
- **윈도가 자동으로 만든 LNK**: 파일을 열거나 저장할 때 셸이 최근 항목 (Recent Items) 폴더에 만듭니다.

포렌식에서 자주 쓰는 쪽은 두 번째입니다.

### 최근 항목 LNK 가 생기는 조건

Microsoft 문서에 따르면 앱이 `SHAddToRecentDocs` 함수를 부르면 사용자의 최근 항목 폴더에 바로가기가 하나 추가됩니다. 이 함수는 다음 경우에 셸이 앱 대신 부릅니다.

- 사용자가 탐색기에서 항목을 열 때
- 공용 파일 대화상자 (Common File Dialog) 로 파일을 열거나, 저장하거나, 새로 만들 때

자기 화면으로 파일을 고르는 앱은 이 함수를 직접 불러야 합니다. 부르지 않는 앱으로 연 파일은 최근 항목에 오르지 않습니다.

같은 문서에 적힌 예외는 다음과 같습니다.

- 실행 파일(.exe)은 최근 항목 목록에서 걸러집니다(XP 이후). 그래서 최근 항목 LNK 는 프로그램 실행 기록이 아닙니다.
- `IShellLink` 개체로 넘긴 항목은 최근 항목 폴더에 추가되지 않습니다. 앱의 점프리스트에만 반영됩니다.
- 파일 형식 등록에 `NoRecentDocs` 항목이 있으면 그 형식은 추적하지 않습니다.
- Windows 7 이전에는 `open` 동사만 이 함수를 불렀습니다. Windows 7 부터는 다른 동사도 사용 기록을 남길 수 있습니다.

분석가 글에서는 문서 파일을 열면 그 파일의 LNK 와 부모 폴더의 LNK 가 함께 생긴다고 설명합니다. Microsoft 문서에 적힌 동작은 아닙니다. 보고서에 쓸 때는 직접 확인한 Windows 버전을 함께 적습니다.

### LNK 에 남는 값

- 대상의 경로: 로컬 경로, 네트워크 공유 경로, 셸 아이템 목록
- 대상의 생성·접근·수정 시각과 크기: LNK 를 쓸 때의 값
- 대상이 있던 볼륨: 드라이브 종류, 볼륨 일련번호, 볼륨 이름
- 대상이 있던 기계의 NetBIOS 이름
- 파일 추적용 식별자 (Droid): 버전 1 UUID 라면 식별자를 만든 시각과 MAC 주소 칸이 들어 있습니다
- 명령줄 인수, 작업 폴더, 아이콘 위치: 바로가기를 만든 쪽이 채운 경우

## 위치와 버전별 차이

### 최근 항목 폴더

| Windows | 위치 | 근거 |
|---|---|---|
| XP | `%USERPROFILE%\Recent` (예: `C:\Documents and Settings\<사용자>\Recent`) | KNOWNFOLDERID 의 옛 기본 경로 |
| Vista 이후 (7·8·10·11) | `%APPDATA%\Microsoft\Windows\Recent` (예: `C:\Users\<사용자>\AppData\Roaming\Microsoft\Windows\Recent`) | KNOWNFOLDERID 의 기본 경로 (FOLDERID_Recent) |

- 이 폴더는 사용자마다 따로 있습니다. 그래서 어느 프로필 폴더에서 나왔는지가 곧 어느 계정의 기록인지 알려 줍니다.
- 같은 폴더 아래의 `AutomaticDestinations`·`CustomDestinations` 는 점프리스트입니다. 점프리스트 안에도 LNK 형식 데이터가 들어 있습니다([점프리스트](jump-lists.md)).
- 폴더에 보관하는 LNK 개수에는 한도가 있습니다. 한도를 넘으면 오래된 LNK 가 밀려납니다. 한도를 149개로 적는 글이 많습니다. 새 버전에서는 다르다는 설명도 있어 이 숫자를 단정하지 않습니다.

### 그 밖에 LNK 가 있는 곳

아래 기본 경로는 Microsoft 의 KNOWNFOLDERID 문서에서 옮겼습니다(Vista 이후 기준).

| 위치 | 기본 경로 | 주로 만드는 쪽 |
|---|---|---|
| 바탕화면 | `%USERPROFILE%\Desktop`, 모든 사용자는 `%PUBLIC%\Desktop` | 사용자, 설치 프로그램 |
| 시작 메뉴 프로그램 | `%APPDATA%\Microsoft\Windows\Start Menu\Programs`, 모든 사용자는 `%ALLUSERSPROFILE%\Microsoft\Windows\Start Menu\Programs` | 설치 프로그램 |
| 시작프로그램 | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\StartUp`, 모든 사용자는 `%ALLUSERSPROFILE%\Microsoft\Windows\Start Menu\Programs\StartUp` | 사용자, 프로그램. 로그온 때 자동 실행됩니다([로그온 자동실행](../persistence/run-runonce-startup-folder.md)) |
| 고정 항목 | `%APPDATA%\Microsoft\Internet Explorer\Quick Launch\User Pinned` (Windows 7 부터) | 사용자가 고정할 때 |
| 점프리스트 파일 안 | 최근 항목 폴더 아래 | 셸 (Windows 7 부터) |
| 아무 곳 | 이동식 매체, 메일 첨부, 내려받기 폴더 | 공격자, 다른 PC |

시작 메뉴 바로가기 목록은 AmCache 에도 따로 남습니다([바로가기 항목](../execution/amcache-hve/inventoryapplicationshortcut.md)).

### 형식의 버전별 차이

- 같은 형식을 적어도 Windows 95 부터 씁니다.
- 위치 정보 (LinkInfo) 의 유니코드 경로 칸은 위치 정보의 머리 크기 칸 (LinkInfoHeaderSize) 이 0x24 이상일 때만 있습니다. 이 칸이 없으면 경로는 시스템 기본 코드 페이지 문자열로만 남습니다. 한국어 윈도에서 만든 LNK 라면 CP949 로 읽어야 한글 경로가 깨지지 않습니다([문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)).
- libyal 명세는 심 레이어 (0xA0000008), 속성 저장소 (0xA0000009), 알려진 폴더 (0xA000000B), 셸 아이템 목록 (0xA000000C) 블록을 Vista 이후 항목으로 적습니다.

## 구조

형식은 [바로가기 형식 (Shell Link·LNK)](../../01-foundations/shell-document-formats/shell-link-lnk.md)에서 자세히 다룹니다. 여기서는 포렌식에 쓰는 값이 어디 있는지만 정리합니다.

| 부분 | 있는 조건 | 포렌식에 쓰는 값 |
|---|---|---|
| 헤더 (ShellLinkHeader, 76바이트) | 항상 | 링크 플래그, 대상 속성, 대상의 생성·접근·수정 시각, 대상 크기 |
| 대상 ID 목록 (LinkTargetIDList) | 플래그 0x1 | 대상 경로를 이루는 셸 아이템([셸 아이템](../../01-foundations/shell-document-formats/shell-item-pidl.md)) |
| 위치 정보 (LinkInfo) | 플래그 0x2 | 드라이브 종류, 볼륨 일련번호, 볼륨 이름, 로컬 경로, 네트워크 공유 이름 |
| 문자열 (StringData) | 플래그 0x4~0x40 | 설명, 상대 경로, 작업 폴더, 명령줄 인수, 아이콘 위치 |
| 추가 블록 (ExtraData) | 블록마다 다름 | 추적 블록(기계 이름, Droid), 속성 저장소, 환경 변수 경로 등 |

### 헤더에서 읽는 값

헤더는 0x4C(76)바이트입니다. 아래 오프셋은 MS-SHLLINK 의 칸 순서로 센 값입니다.

| 오프셋 | 크기 | 값 |
|---|---|---|
| 0x00 | 4 | 헤더 크기. 반드시 `4C 00 00 00` 입니다 |
| 0x04 | 16 | CLSID `00021401-0000-0000-C000-000000000046` |
| 0x14 | 4 | 링크 플래그 (LinkFlags) |
| 0x18 | 4 | 대상 파일 속성 |
| 0x1C | 8 | 대상 생성 시각 (FILETIME, UTC) |
| 0x24 | 8 | 대상 접근 시각 (FILETIME, UTC) |
| 0x2C | 8 | 대상 수정 시각 (FILETIME, UTC) |
| 0x34 | 4 | 대상 크기. 4GiB 를 넘으면 하위 32비트만 남습니다 |

앞 20바이트는 모든 LNK 가 같습니다. 그래서 비할당 영역에서 LNK 를 찾을 때 이 20바이트를 서명으로 씁니다([파일 카빙](../../03-techniques/analysis/data-recovery/file-carving.md)).

링크 플래그에서 자주 보는 비트는 다음과 같습니다.

| 비트 | 이름 | 뜻 |
|---|---|---|
| 0x00000001 | HasLinkTargetIDList | 대상 ID 목록이 있습니다 |
| 0x00000002 | HasLinkInfo | 위치 정보가 있습니다 |
| 0x00000020 | HasArguments | 명령줄 인수가 있습니다 |
| 0x00000080 | IsUnicode | 문자열이 유니코드입니다 |
| 0x00040000 | ForceNoLinkTrack | 추적 블록을 무시합니다 |
| 0x00080000 | EnableTargetMetadata | 대상 속성을 모아 속성 저장소 블록에 넣습니다 |

### 위치 정보의 드라이브 종류

위치 정보 안의 볼륨 정보 (VolumeID) 에는 대상이 있던 볼륨의 드라이브 종류, 일련번호, 이름이 있습니다. 드라이브 종류 값은 다음과 같습니다.

| 값 | 이름 | 뜻 |
|---|---|---|
| 0 | DRIVE_UNKNOWN | 알 수 없음 |
| 1 | DRIVE_NO_ROOT_DIR | 경로에 볼륨이 없음 |
| 2 | DRIVE_REMOVABLE | 이동식 매체 (USB 메모리, 카드 리더 등) |
| 3 | DRIVE_FIXED | 고정 디스크 |
| 4 | DRIVE_REMOTE | 네트워크 드라이브 |
| 5 | DRIVE_CDROM | CD-ROM |
| 6 | DRIVE_RAMDISK | 램 디스크 |

명세는 고정 디스크의 예로 하드 디스크와 플래시 드라이브를 함께 듭니다. 그래서 USB 로 연결한 외장 디스크도 3 으로 나올 수 있습니다. 2 가 아니라고 해서 내장 디스크라고 단정하지 않습니다.

네트워크에 있던 대상이면 네트워크 위치 (CommonNetworkRelativeLink) 가 있습니다. 여기에 `\\서버\공유` 형태의 이름과 연결한 드라이브 문자가 남습니다.

### 추적 블록

추적 블록 (TrackerDataBlock) 은 서명이 0xA0000003 이고 크기가 0x60(96)바이트입니다. 대상이 원래 자리에 없을 때 링크 추적 서비스 (Distributed Link Tracking) 로 찾으려고 넣는 값입니다.

| 블록 안 오프셋 | 크기 | 값 |
|---|---|---|
| 0x10 | 16 | MachineID. 대상이 마지막으로 있던 기계의 NetBIOS 이름 |
| 0x20 | 32 | Droid. 볼륨 GUID 와 파일 GUID |
| 0x40 | 32 | DroidBirth. 같은 꼴의 볼륨 GUID 와 파일 GUID. 파일이 처음 있던 자리의 값으로 흔히 설명합니다 |

libyal 명세는 파일 GUID 를 대상 파일의 NTFS `$OBJECT_ID` 속성에서 찾을 수 있다고 적습니다([MFT 레코드와 속성](../../01-foundations/disk-volume/ntfs/file-record-attribute.md)). GUID 읽는 법은 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md)에서 다룹니다.

> 그림 자리: LNK 파일을 헤더·대상 ID 목록·위치 정보·문자열·추가 블록으로 나누고, 각 부분에서 포렌식에 쓰는 값(대상 시각, 볼륨 일련번호, 기계 이름, Droid)을 화살표로 짚는 그림

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 프로필의 셸이 이 대상을 최근 항목에 올린 적이 있습니다 (최근 항목 LNK) | 그 계정 앞에 앉은 사람이 누구인지 |
| LNK 를 쓸 때 대상이 이 경로에 있었습니다 | 파일 내용을 읽었는지, 얼마나 봤는지 |
| 그때 대상의 시각과 크기 (크기는 하위 32비트) | 열었는지, 저장했는지, 새로 만들었는지 |
| 대상이 이동식 매체나 네트워크에 있었고, 그 볼륨의 일련번호와 이름 | 파일을 복사하거나 밖으로 보냈는지 |
| 대상이 지금 없어도 한때 있었다는 사실 | 몇 번 열었는지 |
| 추적 블록이 있으면 대상이 있던 기계 이름과 파일 GUID | 프로그램을 실행했는지 (.exe 는 최근 항목에서 걸러집니다) |

바탕화면과 시작 메뉴의 LNK 는 대개 설치 때 생깁니다. 그래서 이 LNK 가 있다는 사실만으로 사용자가 그 프로그램을 썼다고 볼 수 없습니다.

### 보고서 문장

아래 경로와 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 프로필의 최근 항목 폴더에 있는 LNK 하나는 `E:\자료\보고서.docx` 를 가리킵니다. 이 LNK 에는 대상이 이동식 드라이브(볼륨 일련번호 1A2B-3C4D)에 있었다는 기록이 있습니다. 이 LNK 파일의 $MFT 수정 시각은 2025-03-14 01:20 UTC 입니다."
- 쓰면 안 되는 문장: "A 는 3월 14일 USB 에 든 보고서를 열어 읽었다."

## 시각 해석

### 시각이 있는 네 곳

| 시각 | 있는 곳 | 뜻 | 기준 |
|---|---|---|---|
| 대상 생성·접근·수정 | LNK 헤더 0x1C·0x24·0x2C | LNK 를 쓸 때 대상 파일에서 옮겨 적은 시각 | UTC, FILETIME (명세) |
| LNK 파일의 생성 시각 | $MFT (LNK 파일 자신) | 최근 항목에 처음 오른 무렵 (흔한 해석) | UTC |
| LNK 파일의 수정 시각 | $MFT (LNK 파일 자신) | 마지막으로 다시 쓰인 무렵. 마지막으로 연 무렵으로 흔히 읽습니다 | UTC |
| 파일 GUID 의 시각 | 추적 블록 Droid (버전 1 UUID 일 때) | 그 GUID 를 만든 때 | UTC, 1582-10-15 부터 100나노초 단위 |

대상 ID 목록의 셸 아이템에도 시각이 들어 있을 수 있습니다. 읽는 법은 [셸 아이템](../../01-foundations/shell-document-formats/shell-item-pidl.md)에서 다룹니다.

### 헤더 시각은 대상의 시각입니다

헤더 시각은 LNK 의 시각이 아닙니다. 대상 파일의 시각입니다. LNK 는 파일이므로 이 값은 LNK 가 마지막으로 쓰인 순간에 굳어 있습니다. 명세에 따르면 값이 0 이면 대상에 그 시각이 없었다는 뜻입니다.

셸은 파일 시스템에서 이 시각을 읽어 옵니다. 그래서 NTFS 에서는 대개 대상의 $STANDARD_INFORMATION 시각과 맞춰 봅니다([두 벌의 시각](../../01-foundations/disk-volume/ntfs/standard-information-file-name.md)). 대상이 아직 있다면 지금의 $MFT 시각과 비교합니다. 헤더의 수정 시각보다 지금의 수정 시각이 늦으면 LNK 를 쓴 뒤에 대상이 다시 바뀐 것입니다.

접근 시각은 NTFS 설정에 따라 제때 바뀌지 않을 수 있습니다. 접근 시각 하나로 연 시각을 말하지 않습니다([파일 시각 네 가지와 변화 규칙](../../03-techniques/analysis/timeline/macb-timestamp-rules.md)).

### LNK 파일 자신의 시각

LNK 파일의 생성 시각을 "처음 연 때", 수정 시각을 "마지막으로 연 때" 로 읽는 해석이 널리 쓰입니다. 이 해석은 형식 명세가 아니라 동작을 관찰해 나온 것입니다. 다음 경우에는 맞지 않습니다.

- LNK 가 보관 한도로 밀려났다가 다시 만들어지면 생성 시각은 "처음 연 때" 가 아니라 "다시 만든 때" 입니다.
- 사용자가 최근 항목을 지운 뒤 다시 열어도 같습니다.
- 수집할 때 복사 방법에 따라 사본의 파일 시각이 바뀝니다. 파일 시각은 원본 볼륨의 [$MFT](../filesystem/mft.md)에서 읽습니다.

### 현지 시각으로 바꾸기

모든 시각은 UTC 입니다. 현지 시각으로 바꿀 때는 그 PC 의 시간대 설정을 씁니다([시간대 설정](../system-account/time-zone.md), [시간대·시계 오차 보정](../../03-techniques/analysis/timeline/time-normalization.md)). FILETIME 계산은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다.

## 함정과 한계

1. **LNK 시각과 대상 시각을 섞습니다.** 헤더의 세 시각은 대상 파일의 시각입니다. 사용자가 연 시각은 LNK 파일 자신의 NTFS 시각에서 찾습니다.
2. **기계 이름을 이 PC 의 이름으로 읽습니다.** 명세는 MachineID 를 "대상이 마지막으로 있던 기계" 의 NetBIOS 이름으로 정의합니다. 파일 서버의 공유 폴더에 있던 대상이면 파일 서버 이름이 들어갈 수 있습니다.
3. **MAC 주소 칸을 믿습니다.** 파일 GUID 가 버전 1 UUID 가 아니면 시각과 MAC 칸이 없습니다. 버전 1 이어도 노드 칸이 실제 어느 네트워크 카드인지는 다른 기록과 맞춰 봐야 합니다([네트워크 인터페이스 설정](../network/tcp-ip-interfaces.md)).
4. **크기를 그대로 씁니다.** 헤더의 크기는 하위 32비트입니다. 4GiB 가 넘는 파일은 실제보다 작게 보입니다.
5. **LNK 가 없으면 안 열었다고 봅니다.** 최근 항목에 오르지 않는 까닭은 여럿입니다. 앱이 함수를 부르지 않았을 수 있습니다. 파일 형식이 추적에서 빠졌을 수 있습니다. 보관 한도로 밀려났거나 사용자가 지웠을 수도 있습니다.
6. **"열었다" 로 단정합니다.** 공용 파일 대화상자로 저장하거나 새로 만들어도 LNK 가 생깁니다. Windows 7 부터는 `open` 이외의 동사도 기록을 남길 수 있습니다.
7. **이름이 같은 파일을 하나로 봅니다.** 최근 항목 LNK 이름은 대상 이름에서 나옵니다. 폴더가 다른데 이름이 같은 두 파일은 LNK 하나를 다시 쓸 수 있다고 흔히 설명합니다. LNK 이름이 아니라 안의 경로와 볼륨 정보로 대상을 가립니다.
8. **도구가 시각을 바꿔 보여 줍니다.** 도구 설정에 따라 UTC 가 아니라 분석 PC 의 현지 시각으로 나올 수 있습니다.
9. **한글 경로가 깨집니다.** 유니코드 경로 칸이 없는 LNK 는 코드 페이지 문자열만 있습니다. 분석 PC 의 코드 페이지로 읽으면 한글이 깨집니다.

### 지우기와 조작

- **최근 항목을 비웁니다.** LNK 가 한꺼번에 사라집니다. 지운 기록은 [$UsnJrnl](../filesystem/usnjrnl.md)과 $MFT 에 남을 수 있습니다. 옛 LNK 는 [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md)에서 찾습니다. 점프리스트·셸백·RecentDocs 를 함께 지우지 않았다면 그쪽에 흔적이 남아 있을 수 있습니다.
- **대상 파일만 지웁니다.** LNK 는 그대로 남습니다. 지운 파일의 경로와 시각을 LNK 로 되살릴 수 있습니다([지운 파일의 흔적 찾기](../../04-scenarios/activity/deleted-file-traces.md)).
- **LNK 의 NTFS 시각만 바꿉니다.** 헤더 안의 대상 시각과 Droid 시각은 그대로 남습니다. 서로 비교하면 어긋남이 드러납니다([시각 조작 탐지](../../03-techniques/analysis/timeline/timestomping.md)).
- **공격용 LNK 를 만듭니다.** 대상을 명령 해석기로 두고 명령줄 인수 칸에 명령을 넣는 방식이 쓰입니다. 아이콘 위치 칸으로 문서처럼 보이게 꾸미기도 합니다. Windows API 로 만든 LNK 에는 만든 기계의 NetBIOS 이름, MAC 주소, 볼륨 일련번호가 남을 수 있습니다. Harlan Carvey 는 이 값으로 같은 공격자가 만든 LNK 를 더 찾아낸 사례를 적었습니다. 명세보다 긴 MachineID 칸처럼 만든 도구의 흔적이 남는 경우도 적었습니다([악성코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md)).

## 직접 분석해 보기

### 헥스로 한 번

아래는 MS-SHLLINK 명세를 보고 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

**헤더**

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    4C 00 00 00 01 14 02 00 00 00 00 00 C0 00 00 00
0x10    00 00 00 46 9B 00 08 00 20 00 00 00 00 0C D0 22
0x20    51 91 DB 01 80 10 79 37 7F 94 DB 01 80 CD 2C C1
0x30    EE 93 DB 01 55 BC 00 00 00 00 00 00 01 00 00 00
0x40    00 00 00 00 00 00 00 00 00 00 00 00
```

1. 0x00 의 `4C 00 00 00` 은 헤더 크기 0x4C 입니다.
2. 0x04~0x13 은 CLSID 입니다. 앞 세 묶음은 리틀 엔디언으로 적혀 있습니다. 그래서 `01 14 02 00` 이 `00021401` 입니다.
3. 0x14 의 `9B 00 08 00` 은 0x0008009B 입니다. 0x1(대상 ID 목록), 0x2(위치 정보), 0x8(상대 경로), 0x10(작업 폴더), 0x80(유니코드), 0x80000(대상 속성 수집) 비트가 켜져 있습니다.
4. 0x18 의 `20 00 00 00` 은 보관 (Archive) 속성입니다.
5. 0x1C 부터 8바이트씩 세 시각을 읽습니다. 첫 값 `00 0C D0 22 51 91 DB 01` 을 리틀 엔디언으로 읽으면 0x01DB915122D00C00 입니다.
6. 이 수는 10진으로 133,860,391,600,000,000 입니다. 1601-01-01 00:00:00 UTC 부터 100나노초 단위로 센 값입니다.
7. 0x34 의 `55 BC 00 00` 은 48,213바이트입니다.
8. 0x3C 의 `01 00 00 00` 은 창을 보통 크기로 연다는 값 (SW_SHOWNORMAL) 입니다.

| 칸 | 바이트 | UTC | 한국 시각 |
|---|---|---|---|
| 대상 생성 | `00 0C D0 22 51 91 DB 01` | 2025-03-10 00:12:40 | 2025-03-10 09:12:40 |
| 대상 접근 | `80 10 79 37 7F 94 DB 01` | 2025-03-14 01:20:05 | 2025-03-14 10:20:05 |
| 대상 수정 | `80 CD 2C C1 EE 93 DB 01` | 2025-03-13 08:05:59 | 2025-03-13 17:05:59 |

**추적 블록**

추가 블록 안에서 서명 `03 00 00 A0` 을 찾습니다. 아래 오프셋은 블록 시작에서 센 값입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
+0x00   60 00 00 00 03 00 00 A0 58 00 00 00 00 00 00 00
+0x10   44 45 53 4B 54 4F 50 2D 45 58 41 4D 50 4C 45 00
+0x20   10 2A 3C 7F 6E 5B 21 4D 9C 8A 1E 2F 3A 4B 5C 6D
+0x30   00 47 B6 B5 44 FD EF 11 8A 3C 00 11 22 33 44 55
+0x40   10 2A 3C 7F 6E 5B 21 4D 9C 8A 1E 2F 3A 4B 5C 6D
+0x50   00 47 B6 B5 44 FD EF 11 8A 3C 00 11 22 33 44 55
```

1. `60 00 00 00` 은 블록 크기 0x60 입니다. `03 00 00 A0` 은 서명 0xA0000003 입니다. `58 00 00 00` 은 나머지 길이 0x58 입니다.
2. +0x10 의 16바이트는 MachineID `DESKTOP-EXAMPLE` 입니다.
3. +0x20 은 볼륨 GUID `{7F3C2A10-5B6E-4D21-9C8A-1E2F3A4B5C6D}` 입니다. 세 번째 묶음 `4D21` 의 첫 자리가 4 입니다. 버전 4 는 무작위 값이라 시각이 없습니다.
4. +0x30 은 파일 GUID `{B5B64700-FD44-11EF-8A3C-001122334455}` 입니다. 세 번째 묶음 `11EF` 의 첫 자리가 1 입니다. 그래서 버전 1 입니다.
5. 버전 1 의 마지막 6바이트는 노드 칸입니다. 여기서는 `00-11-22-33-44-55` 입니다. 예시용으로 지어낸 주소입니다.
6. 시각은 `11EF` 에서 버전 자리를 뺀 `1EF`, `FD44`, `B5B64700` 을 차례로 이어 붙입니다. 0x1EFFD44B5B64700 은 10진으로 139,608,585,020,000,000 입니다.
7. 이 값은 1582-10-15 00:00:00 UTC 부터 100나노초 단위로 센 값입니다. 날짜로 바꾸면 2025-03-10 00:15:02 UTC 입니다.
8. +0x40 과 +0x50 의 DroidBirth 는 Droid 와 같습니다.

파일 GUID 의 시각은 대상 생성 시각보다 2분쯤 늦습니다. 이 시각은 GUID 를 만든 때입니다. 대상 파일이 생긴 때로 읽지 않습니다.

> 그림 자리: 추적 블록 96바이트를 MachineID·볼륨 GUID·파일 GUID·DroidBirth 로 나누고, 파일 GUID 안에서 버전 자리·시각 칸·노드 칸을 색으로 나눠 보여 주는 그림

### 공개 도구로 한 번

libyal 의 `lnkinfo`, LECmd 같은 공개 도구가 위 값을 풀어 보여 줍니다. 도구를 쓸 때는 다음을 확인합니다.

- 시각을 UTC 로 보여 주는지, 현지 시각으로 바꿔 보여 주는지 확인합니다.
- 헤더의 대상 시각과 LNK 파일 자신의 시각을 어떤 이름으로 나누는지 확인합니다. 도구마다 부르는 이름이 다릅니다.
- 파일 GUID 에서 시각과 MAC 을 풀어 주는지 확인합니다. 풀어 준다면 버전 1 인지 먼저 따지는지 봅니다.
- LNK 한두 개는 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [$MFT](../filesystem/mft.md) | LNK 파일 자신의 생성·수정 시각. 대상 파일이 남아 있다면 지금의 대상 시각 |
| [$UsnJrnl](../filesystem/usnjrnl.md) | LNK 가 다시 쓰이거나 지워진 기록. 대상 파일의 이름 바꾸기·삭제 |
| [점프리스트](jump-lists.md) | 어느 앱으로 열었는지. 같은 대상의 LNK 형식 데이터 |
| [최근 문서 (RecentDocs)](recentdocs.md) · [열기·저장 대화상자 기록](comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) | 같은 파일 이름과 순서. 대화상자를 쓴 앱 |
| [셸백](shellbags/index.md) | 대상이 있던 폴더를 탐색한 흔적 |
| [오피스 최근 파일](microsoft-office/file-mru-place-mru.md) | 오피스 문서라면 오피스가 따로 남긴 경로와 시각 |
| [USB 저장장치 흔적](../external-devices/usb-storage-artifacts/index.md) · [WPD·EMDMgmt](../external-devices/usb-storage-artifacts/wpd-emdmgmt.md) | LNK 의 볼륨 일련번호·이름과 같은 매체가 연결된 기록 |
| [공유 폴더·네트워크 드라이브](../network/network-shares-mapped-drives.md) | LNK 의 공유 이름과 드라이브 문자 |
| [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 지워지거나 다시 쓰이기 전의 LNK |
| [다운로드 출처 표시](../filesystem/zone-identifier.md) | 밖에서 받은 LNK 인지 |

여러 기록을 합쳐 읽는 순서는 [이 파일을 누가 언제 열었나](../../04-scenarios/activity/file-access.md)와 [USB 로 무엇을 가져갔나](../../04-scenarios/exfiltration/data-exfiltration/usb.md)에서 다룹니다. 계정 뒤의 사람을 밝히는 일은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)를 봅니다.

## 실습

**NIST CFReDS Data Leakage Case** 는 자료 유출을 다룬 Windows 7 PC 이미지입니다.

1. 사용자 프로필의 최근 항목 폴더에서 LNK 를 모두 꺼내 보십시오. 드라이브 종류가 2(이동식)인 LNK 는 몇 개입니까?
2. 1번 LNK 들의 볼륨 일련번호와 볼륨 이름은 몇 가지입니까? 같은 매체가 USB 기록에도 남아 있는지 맞춰 보십시오.
3. 드라이브 종류가 4(네트워크)인 LNK 가 있다면 공유 이름을 적어 보십시오.
4. LNK 하나를 골라 헤더의 대상 시각 세 개를 헥스로 직접 읽어 보십시오. 그 LNK 파일의 $MFT 생성·수정 시각과 나란히 적고 뜻을 설명해 보십시오.
5. 추적 블록의 파일 GUID 가 버전 1 인 LNK 가 있다면 시각과 노드 칸을 풀어 보십시오. 그 노드 값이 이 PC 의 네트워크 카드 주소와 같은지도 맞춰 보십시오.

**직접 만든 Windows 10·11 가상 머신**에서도 해 봅니다.

1. 문서 하나를 탐색기에서 두 번 열고, 여는 시각을 적어 둡니다. 최근 항목 폴더에 LNK 가 몇 개 생겼는지 봅니다. 부모 폴더의 LNK 도 생겼는지 확인합니다.
2. 같은 문서를 메모장의 "다른 이름으로 저장" 으로 저장해 봅니다. 저장만으로 LNK 가 생기거나 바뀌는지 봅니다.
3. 다른 폴더에 이름이 같은 파일을 만들어 엽니다. LNK 가 새로 생기는지, 앞의 LNK 가 다시 쓰이는지 봅니다.
4. 대상 파일을 지운 뒤 LNK 에서 경로와 대상 시각을 되살려 봅니다.

## 참고 문헌

- Microsoft, "[MS-SHLLINK]: Shell Link (.LNK) Binary File Format" — ShellLinkHeader·LinkFlags·LinkInfo·VolumeID·TrackerDataBlock 절 — https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-shllink/16cb4ca1-9339-4d0c-a68d-bf1d6cc0f943
- Microsoft, "SHAddToRecentDocs function (shlobj_core.h)" — https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shaddtorecentdocs
- Microsoft, "KNOWNFOLDERID" — https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid
- libyal, "Windows Shortcut File (LNK) format" (liblnk) — https://github.com/libyal/liblnk/blob/main/documentation/Windows%20Shortcut%20File%20(LNK)%20format.asciidoc
- Harlan Carvey, "LNK 'Toolmarks'", Windows Incident Response (2018) — http://windowsir.blogspot.com/2018/07/lnk-toolmarks.html
- The DFIR Spot, "A LNK To The Past: Utilizing LNK Files For Your Investigations" (2023) — https://www.thedfirspot.com/post/a-lnk-to-the-past-utilizing-lnk-files-for-your-investigations
