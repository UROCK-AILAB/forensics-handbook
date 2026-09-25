---
title: "원노트"
parent: "아티팩트 · 클라우드·노트"
nav_order: 2310
---

# 원노트 (OneNote)

> 위치: 아티팩트 사전 > 클라우드·노트

## 한 줄 요약

원노트는 전자 필기장을 구역마다 `.one` 파일 하나로 저장하고, 필기장 목차를 `.onetoc2` 파일로 저장합니다. 두 파일 모두 맨 앞 1,024바이트가 파일 머리이며, 여기서 파일 종류, 소속 필기장, 바뀐 횟수를 알 수 있습니다. 파일 안의 속성에서는 제목·작성자·시각·첨부 파일을 꺼낼 수 있습니다. 동기화한 필기장은 로컬 백업 폴더와 캐시 폴더에도 흔적이 남습니다. 스토어 앱 원노트는 앱 폴더의 SQLite DB 에 검색 색인과 최근 필기장 주소를 남깁니다.

이 페이지에서 "관찰" 이라고 적은 것은 Windows 11(빌드 26200) PC 한 대에서 폴더와 레지스트리 키가 있는지만 본 결과입니다. 한 대의 결과이므로 모든 PC 에 맞는다고 보장하지 못합니다.

## 무엇을 기록하나 · 왜 생기나

원노트 파일은 개정 저장 파일 (revision store file) 형식입니다. 구역 (section) 파일은 `.one` 이고, 목차 (table of contents) 파일은 `.onetoc2` 입니다. (MS-ONESTORE)

Microsoft 는 이 형식을 공개 명세 두 개로 설명합니다. [MS-ONESTORE] 는 저장 구조를, [MS-ONE] 은 원노트 내용 구조를 다룹니다. (MS-ONESTORE)

원노트는 쓰는 방식에 따라 흔적을 여러 곳에 남깁니다.

- **내 PC 에 저장한 전자 필기장 (notebook)**: 구역 하나가 `.one` 파일 하나입니다. (Obsidian 도움말)
- **동기화한 전자 필기장**: 원노트가 로컬 백업 폴더에 사본을 둡니다. (Obsidian 도움말)
- **캐시**: 원노트가 전자 필기장·구역·페이지를 받아 캐시 폴더에 둡니다. 페이지에 넣은 파일도 캐시 폴더에 `.bin` 파일로 있습니다. (OneMore)
- **스토어 앱 원노트**: 앱 폴더에 검색 색인, 최근 본 필기장 주소, 태그, 최근 검색어 DB 가 있습니다. (KAPE 대상 파일)

## 위치와 버전별 차이

참고한 자료는 Windows 버전이 아니라 원노트 종류로 위치를 나눕니다. Windows 버전별 차이는 확인하지 못했습니다.

### 데스크톱 원노트 (Microsoft 365·2016 계열)

| 무엇 | 위치 | 근거 |
|---|---|---|
| 내 PC 에 저장한 전자 필기장 | `Documents\OneNote Notebooks\` 아래. 구역 하나가 `.one` 하나 | Obsidian 도움말 |
| 동기화한 필기장의 백업 | `%LOCALAPPDATA%\Microsoft\OneNote\16.0\Backup` | Obsidian 도움말 |
| 캐시 | `%LOCALAPPDATA%\Microsoft\OneNote\16.0\cache` | OneMore |
| 페이지에 넣은 파일 | 캐시 폴더의 `000007LE.bin`, `00000065.bin` 같은 이름의 `.bin` 파일 | OneMore |

- 데스크톱 원노트의 위치는 공식 문서로 확인하지 못했습니다. 위 표는 다른 프로그램의 도움말과 소스에서 가져온 것입니다.
- 캐시를 지우고 원노트를 열면 원노트가 전자 필기장·구역·페이지를 다시 받아 캐시를 새로 만듭니다. (OneMore)
- 원노트 API 가 돌려주는 페이지 XML 에는 첨부 파일마다 `InsertedFile` 요소가 있습니다. 이 요소에 세 값이 적힙니다. (OneMore)

| 속성 | 뜻 |
|---|---|
| `pathCache` | 캐시 폴더의 `.bin` 경로 |
| `pathSource` | 파일을 넣을 때 원래 파일이 있던 경로 |
| `preferredName` | 원래 파일 이름 |

`pathSource` 는 첨부한 원본 파일이 어디 있었는지 보여 줍니다. OneMore 의 예시에는 OneDrive·SkyDrive 경로가 나옵니다. (OneMore)

### 원노트 for Windows 10 (스토어 앱)

앱 폴더는 이렇습니다. (KAPE 대상 파일)

`C:\Users\<사용자>\AppData\Local\Packages\Microsoft.Office.OneNote_8wekyb3d8bbwe\LocalState\AppData\Local\OneNote\`

KAPE 수집 대상 파일(작성자 Andrew Rathbun, 버전 1.0)은 이 폴더 아래에서 다섯 가지를 잡습니다. 작성자는 원노트가 많은 정보를 SQLite DB 에 둔다고 적었습니다. 다만 `RecentNotebooks_SeenURLs` 는 "파일" 이라고만 적었습니다. (KAPE 대상 파일)

| 항목 | 작성자 설명 |
|---|---|
| `OneNote\*\FullTextSearchIndex` | 전자 필기장마다 DB 가 하나씩 있습니다. 필기장 글 전체가 들어 있습니다 |
| `OneNote\Notifications\RecentNotebooks_SeenURLs` | 최근 본 전자 필기장을 적는 파일로 보입니다. 작성자 PC 에서는 외부와 공유한 필기장 두 개의 URL 이 보였습니다 |
| `OneNote\16.0\AccessibilityCheckerIndex` | 필기장 동기화 오류(페이지 충돌) 이력으로 보입니다 |
| `OneNote\16.0\NoteTags\*LiveId.db` | 사용자가 정한 태그입니다 |
| `OneNote\16.0\RecentSearches\RecentSearches.db` | 최근 검색어입니다. 작성자 PC 에서는 비어 있었습니다 |

- 위 설명은 모두 작성자가 자기 PC 에서 본 것입니다. 작성자는 여러 항목에 "~로 보인다 (appears to)" 라고 적었고, 공식 문서로 확인한 내용도 아닙니다.
- 각 DB 의 표와 칸 이름은 확인하지 못했습니다. DB 읽는 법은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.
- 이 KAPE 대상에는 데스크톱 원노트의 `Backup`·`cache` 경로가 없습니다. (KAPE 대상 파일)
- 스토어 앱 폴더 구조는 [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) 에서 다룹니다.

### 관찰: 설치만 된 PC

관찰한 PC 에는 `C:\Program Files\Microsoft Office\root\Office16\` 에 `ONENOTE.EXE`, `ONENOTEM.EXE`, `onenotecapture.exe` 가 있었습니다. 클릭 투 런 설치였습니다.

그런데 그 사용자 프로필에는 아래 네 가지가 모두 없었습니다.

- `%LOCALAPPDATA%\Microsoft\OneNote` 폴더
- `%APPDATA%\Microsoft\OneNote` 폴더
- `HKCU\Software\Microsoft\Office\16.0\OneNote` 키
- `Packages\Microsoft.Office.OneNote_*` 폴더

원노트를 한 번도 열지 않은 계정으로 보입니다(추정). 프로그램이 깔려 있다는 것만으로 사용 흔적이 생기지는 않습니다. 같은 PC 에는 "OneNote (Desktop)" 가상 프린터(포트 `nul:`)도 있었습니다.

## 구조

### 파일 머리 (Header)

파일 머리는 파일 맨 앞에 있어야 합니다. `.one` 과 `.onetoc2` 는 같은 파일 머리 구조를 씁니다. (MS-ONESTORE)

아래 칸 이름과 크기는 명세를 따릅니다. 오프셋은 명세의 칸 크기를 차례로 더해 계산한 값입니다.

| 오프셋 | 칸 | 크기 | 뜻 |
|---|---|---|---|
| 0x000 | guidFileType | 16 | 파일 종류. 아래 "첫 16바이트로 가리기" 참고 |
| 0x010 | guidFile | 16 | 이 파일의 고유 ID |
| 0x020 | guidLegacyFileVersion | 16 | 반드시 0. 무시 |
| 0x030 | guidFileFormat | 16 | 반드시 `{109ADD3F-911B-49F5-A5D0-1791EDC8AED8}` |
| 0x040 | ffvLastCodeThatWroteToThisFile | 4 | 0x040~0x04F 의 네 칸은 `.one` 이면 모두 0x2A, `.onetoc2` 면 모두 0x1B |
| 0x044 | ffvOldestCodeThatHasWrittenToThisFile | 4 | 위와 같음 |
| 0x048 | ffvNewestCodeThatHasWrittenToThisFile | 4 | 위와 같음 |
| 0x04C | ffvOldestCodeThatMayReadThisFile | 4 | 위와 같음 |
| 0x050 | fcrLegacyFreeChunkList | 8 | fcrZero |
| 0x058 | fcrLegacyTransactionLog | 8 | fcrNil |
| 0x060 | cTransactionsInLog | 4 | 트랜잭션 로그 안의 트랜잭션 수. 0 이면 안 됩니다 |
| 0x064 | cbLegacyExpectedFileLength | 4 | 0. 무시 |
| 0x068 | rgbPlaceholder | 8 | 0. 무시 |
| 0x070 | fcrLegacyFileNodeListRoot | 8 | fcrNil |
| 0x078 | cbLegacyFreeSpaceInFreeChunkList | 4 | 0. 무시 |
| 0x07C | fNeedsDefrag | 1 | 무시 |
| 0x07D | fRepairedFile | 1 | 무시 |
| 0x07E | fNeedsGarbageCollect | 1 | 무시 |
| 0x07F | fHasNoEmbeddedFileObjects | 1 | 반드시 0. 무시 |
| 0x080 | guidAncestor | 16 | 목차 파일의 guidFile 값. 아래 설명 참고 |
| 0x090 | crcName | 4 | 파일 이름의 CRC |
| 0x094 | fcrHashedChunkList | 12 | 해시 조각 목록의 첫 조각. fcrZero·fcrNil 이면 목록이 없습니다 |
| 0x0A0 | fcrTransactionLog | 12 | 트랜잭션 로그의 첫 조각. fcrZero·fcrNil 이면 안 됩니다 |
| 0x0AC | fcrFileNodeListRoot | 12 | 루트 파일 노드 목록. fcrZero·fcrNil 이면 안 됩니다 |
| 0x0B8 | fcrFreeChunkList | 12 | 빈 조각 목록의 첫 조각. fcrZero·fcrNil 이면 목록이 없습니다 |
| 0x0C4 | cbExpectedFileLength | 8 | 이 파일의 크기(바이트) |
| 0x0CC | cbFreeSpaceInFreeChunkList | 8 | 빈 조각 목록이 가리키는 빈 공간의 크기 |
| 0x0D4 | guidFileVersion | 16 | cTransactionsInLog 나 guidDenyReadFileVersion 이 바뀔 때마다 새 GUID 로 바뀝니다 |
| 0x0E4 | nFileVersionGeneration | 8 | 파일이 바뀐 횟수. guidFileVersion 이 바뀔 때 1 늘어납니다 |
| 0x0EC | guidDenyReadFileVersion | 16 | 파일 머리와 안 쓰는 블록을 뺀 파일 내용이 바뀔 때 새 GUID 로 바뀝니다 |
| 0x0FC | grfDebugLogFlags | 4 | 0. 무시 |
| 0x100 | fcrDebugLog | 12 | fcrZero. 무시 |
| 0x10C | fcrAllocVerificationFreeChunkList | 12 | fcrZero. 무시 |
| 0x118 | bnCreated | 4 | 이 파일을 만든 프로그램의 빌드 번호 |
| 0x11C | bnLastWroteToThisFile | 4 | 마지막으로 쓴 프로그램의 빌드 번호 |
| 0x120 | bnOldestWritten | 4 | 이 파일에 쓴 프로그램 가운데 가장 오래된 빌드 번호 |
| 0x124 | bnNewestWritten | 4 | 이 파일에 쓴 프로그램 가운데 가장 새 빌드 번호 |
| 0x128 | rgbReserved | 728 | 0. 무시 |

- 파일 머리는 0x128 + 728(0x2D8) = 0x400, 곧 1,024바이트입니다.
- `fcr` 로 시작하는 칸은 파일 조각 참조 (file chunk reference) 입니다. 파일 안의 다른 영역을 가리킵니다. 8바이트짜리와 12바이트짜리가 있습니다. (MS-ONESTORE)
- fcrZero·fcrNil 은 조각 참조의 특수값입니다. 두 값의 실제 바이트 모양은 확인하지 못했습니다.
- **guidAncestor** 는 목차 파일(`.onetoc2`)의 guidFile 값입니다. `.one` 이면 같은 폴더의 목차 파일을 가리킵니다. `.onetoc2` 면 상위 폴더의 목차 파일을 가리킵니다. 값이 전부 0 이면 가리키는 목차 파일이 없습니다. (MS-ONESTORE)
- **crcName** 은 파일 이름으로 계산합니다. 이름은 확장자를 포함하고 끝에 널 문자 하나를 붙인 유니코드 문자열입니다. 파일 형식과 관계없이 `.one` 용 CRC 알고리즘을 씁니다. (MS-ONESTORE)
- **bn 으로 시작하는 네 칸**은 명세가 "무시해도 된다 (SHOULD be ignored)" 고 적었습니다. (MS-ONESTORE)

### 첫 16바이트로 가리기

GUID 는 디스크에 적힐 때 앞 세 부분(4·2·2바이트)의 바이트 순서가 뒤집힙니다(리틀 엔디언). pyOneNote 도 GUID 를 이 순서로 읽습니다. (pyOneNote) GUID 바이트 순서는 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에서 다룹니다.

명세의 GUID 를 이 순서로 바꾸면 파일에 적히는 바이트가 나옵니다.

| 파일 | GUID (명세) | 파일에 적히는 바이트 |
|---|---|---|
| `.one` 의 guidFileType | `{7B5C52E4-D88C-4DA7-AEB1-5378D02996D3}` | `E4 52 5C 7B 8C D8 A7 4D AE B1 53 78 D0 29 96 D3` |
| `.onetoc2` 의 guidFileType | `{43FF2FA1-EFD9-4C76-9EE2-10EA5722765F}` | `A1 2F FF 43 EF D9 76 4C 9E E2 10 EA 57 22 76 5F` |
| 두 파일의 guidFileFormat (0x030) | `{109ADD3F-911B-49F5-A5D0-1791EDC8AED8}` | `3F DD 9A 10 1B 91 F5 49 A5 D0 17 91 ED C8 AE D8` |

파일 머리는 파일 맨 앞에 있어야 하고 guidFileType 값은 형식마다 정해져 있어서 첫 16바이트로 `.one` 과 `.onetoc2` 를 가릴 수 있습니다. 확장자를 바꾼 파일도 이 16바이트로 찾습니다. 지운 파일을 찾는 방법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

### 페이지 속성 (pyOneNote 기준)

아래는 pyOneNote 코드에 있는 속성 ID 와 이름입니다. 명세로 대조하지 않았습니다. "이름 풀이" 는 영어 이름을 옮긴 것입니다. (pyOneNote)

| 속성 ID | 이름 | 이름 풀이 |
|---|---|---|
| 0x1C001D75 | Author | 작성자 |
| 0x1C001CF3 | CachedTitleString | 캐시한 제목 문자열 |
| 0x18001D77 | LastModifiedTimeStamp | 마지막 수정 시각 |
| 0x14001D09 | CreationTimeStamp | 만든 시각 |
| 0x14001D7A | LastModifiedTime | 마지막 수정 시각 |
| 0x1C001D9C | EmbeddedFileName | 넣은 파일의 이름 |
| 0x1C001D9D | SourceFilepath | 원래 파일 경로 |
| 0x1C001E58 | ImageAltText | 그림의 대체 텍스트 |

### 첨부 파일

pyOneNote 는 `.one` 에서 페이지에 넣은 파일을 꺼냅니다. 관련 파일 노드 (file node) 는 세 가지입니다. (pyOneNote)

| 파일 노드 | ID |
|---|---|
| FileDataStoreListReferenceFND | 0x090 |
| FileDataStoreObjectReferenceFND | 0x094 |
| ObjectDeclarationFileData3RefCountFND | 0x072 |

- ObjectDeclarationFileData3RefCountFND 에는 파일 데이터 참조 문자열(FileDataReference)과 확장자(Extension)가 들어 있습니다. 둘 다 UTF-16 문자열입니다. (pyOneNote)
- 파일 내용은 FileDataStoreObject 에 들어 있습니다. pyOneNote 는 이 구조를 아래처럼 읽습니다. 오프셋은 크기를 더해 계산한 값입니다. (pyOneNote)

| 오프셋 | 칸 | 크기 | 뜻 |
|---|---|---|---|
| 0x00 | guidHeader | 16 | 머리 GUID |
| 0x10 | cbLength | 8 | 파일 데이터 길이 |
| 0x18 | unused | 4 | 안 씀 |
| 0x1C | reserved | 8 | 예약 |
| 0x24 | 파일 데이터 | cbLength | 넣은 파일의 내용 |
| 영역 끝 − 16 | guidFooter | 16 | 꼬리 GUID. 조각 참조가 가리키는 영역의 마지막 16바이트 |

guidHeader·guidFooter 의 실제 GUID 값은 확인하지 못했습니다.

## 증거로서 의미

### 증명하는 것

- **원노트 파일이라는 것.** 첫 16바이트로 구역 파일인지 목차 파일인지 가립니다. 확장자와 관계없습니다.
- **구역이 속한 전자 필기장.** `.one` 의 guidAncestor 를 `.onetoc2` 의 guidFile 과 맞추면 어느 필기장의 구역인지 이을 수 있습니다. (MS-ONESTORE)
- **파일이 바뀐 횟수.** nFileVersionGeneration 은 파일이 바뀐 횟수입니다. (MS-ONESTORE)
- **페이지의 내용 속성.** 제목 문자열, 작성자 문자열, 시각 값을 꺼낼 수 있습니다. (pyOneNote)
- **첨부 파일.** 파일 이름과 내용을 `.one` 에서 꺼낼 수 있습니다. pyOneNote 의 속성 목록에는 SourceFilepath 도 있습니다. (pyOneNote)
- **첨부 파일의 원래 위치.** 원노트 API 의 페이지 XML 에서 `pathSource` 는 파일을 넣을 때 원본이 있던 경로입니다. 그 경로가 OneDrive 같은 동기화 폴더일 수도 있습니다. (OneMore)
- **동기화 필기장의 로컬 사본.** 데스크톱 원노트는 백업 폴더와 캐시 폴더에 사본을 남길 수 있습니다. 서버에서 지운 필기장이라도 로컬 사본을 찾아볼 곳이 됩니다. (Obsidian 도움말, OneMore)
- **스토어 앱 원노트의 사용 흔적.** 최근 본 필기장 URL, 필기장 글 전체가 든 검색 색인, 태그, 최근 검색어가 남을 수 있습니다. 모두 KAPE 대상 작성자의 관찰입니다. (KAPE 대상 파일)
- **계정.** 위치가 모두 사용자 프로필 아래이므로 어느 계정의 원노트인지 알 수 있습니다.

### 증명하지 못하는 것

- **누가 썼는지.** Author 는 원노트에 설정한 이름 문자열입니다. 계정과 사람은 다를 수 있습니다. 사람을 좁히는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- **프로그램을 썼다는 것.** 관찰한 PC 에는 원노트 실행 파일이 있었지만 프로필에 흔적이 하나도 없었습니다. 설치 기록만으로 사용을 말할 수 없습니다.
- **파일 머리로 본 시각.** 파일 머리에는 날짜·시각 칸이 없습니다. 바뀐 횟수와 바뀔 때마다 새로 생기는 GUID 만 있습니다. (MS-ONESTORE)
- **파일을 만든 프로그램의 버전.** bn 칸 네 개에 빌드 번호가 적힙니다. 하지만 명세는 이 칸을 무시해도 된다고 적었습니다. 버전 추정에 쓸 수 있는지는 확인하지 못했습니다.
- **사용자가 그 페이지를 열어 봤다는 것.** 원노트는 캐시를 다시 받아 새로 만들 수 있습니다. 캐시에 페이지나 첨부 파일이 있다는 것만으로 사용자가 그 페이지를 봤다고 말하기 어렵습니다.
- **첨부 원본이 지금도 그 경로에 있다는 것.** `pathSource` 는 넣을 때의 경로입니다.
- **`.one` 안의 SourceFilepath 가 API 의 `pathSource` 와 같은 값이라는 것.** 두 값이 같은 값인지는 확인하지 못했습니다.

보고서에는 "피의자가 이 문서를 원노트에 붙였다" 가 아니라 이렇게 씁니다. "A 계정 프로필 아래 구역 파일 `X.one` 에 이름이 `Y` 인 첨부 파일이 들어 있다. 같은 첨부 파일의 SourceFilepath 속성 값은 `Z` 다. 값은 pyOneNote 로 읽었고 헥스로 확인했다." X·Y·Z 는 설명을 위한 자리입니다.

## 시각 해석

pyOneNote 는 시각 속성을 값 길이에 따라 두 가지로 풉니다. (pyOneNote)

| 값 길이 | 형식 | 기준 시각 | 단위 | pyOneNote 의 변환 |
|---|---|---|---|---|
| 8바이트 | FILETIME | 1601-01-01 | 100ns | 초로 바꾼 뒤 11644473600 을 빼 Unix 시각으로 만듭니다 |
| 4바이트 | Time32 | 1980-01-01 00:00:00 | 초 | 1980-01-01 부터 초를 더합니다 |

- pyOneNote 는 속성 이름에 `time` 이 든 속성만 시각으로 풉니다. TopologyCreationTimeStamp, CreationTimeStamp, LastModifiedTimeStamp, LastModifiedTime 이 여기에 듭니다. NoteTagCreated, NoteTagCompleted, TaskTagDueDate 는 이름에 `time` 이 없어서 pyOneNote 가 시각으로 풀지 않습니다. 이 값들이 시각인지는 확인하지 못했습니다. (pyOneNote)
- 어느 속성이 몇 바이트인지는 명세로 확인하지 못했습니다. 값 길이를 보고 형식을 가립니다.
- Time32 는 초 단위이고 FILETIME 은 100ns 단위라서 같은 사건이라도 두 값의 정밀도가 다릅니다. 두 값이 초 아래에서 어긋나도 이상한 일이 아닙니다.
- Time32 의 기준이 UTC 인지는 명세로 확인하지 못했습니다. pyOneNote 코드 주석은 기준을 "1980-01-01 UTC" 라고 적었습니다. 하지만 계산할 때는 시간대를 붙이지 않습니다. 같은 PC 의 UTC 기록과 맞춰 본 뒤 씁니다.
- FILETIME·Time32 형식은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- 속성 시각이 어떤 동작에서 바뀌는지는 참고한 자료로 확인하지 못했습니다.

파일 머리에는 시각이 없지만 순서를 알려 주는 칸이 있습니다. (MS-ONESTORE)

| 칸 | 언제 바뀌나 |
|---|---|
| guidDenyReadFileVersion | 파일 머리와 안 쓰는 블록을 뺀 파일 내용이 바뀔 때 |
| guidFileVersion | cTransactionsInLog 나 guidDenyReadFileVersion 이 바뀔 때 |
| nFileVersionGeneration | guidFileVersion 이 바뀔 때 1 늘어납니다 |

guidFile 이 같은 두 파일을 찾았다면 nFileVersionGeneration 을 비교합니다. 명세의 정의대로라면 값이 큰 쪽이 나중 상태입니다. 두 값의 차이는 그사이에 바뀐 횟수입니다.

파일 시스템 시각은 [마스터 파일 테이블](../filesystem/mft.md) 에서 다룹니다. 캐시를 새로 만들었다면 캐시 파일의 파일 시스템 시각은 다시 만든 때를 가리킬 수 있습니다.

## 함정과 한계

- **데스크톱 원노트 위치는 공식 문서로 확인하지 못했습니다.** `Backup`·`cache` 경로는 다른 프로그램의 도움말과 소스에서 가져왔습니다. 증거 PC 에서 실제 폴더를 확인합니다.
- **수집 도구의 대상 범위를 봅니다.** 앞에서 본 KAPE 대상은 스토어 앱 폴더만 잡습니다. 데스크톱 원노트의 `Backup`·`cache` 와 `Documents\OneNote Notebooks` 는 따로 수집합니다.
- **증거 PC 에서 원노트를 열지 않습니다.** 원노트는 캐시를 다시 받아 새로 만들 수 있습니다. 폴더를 먼저 복사합니다. 수집 순서는 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 에서 다룹니다.
- **스토어 앱 DB 설명은 한 사람의 관찰입니다.** 필기장 글 전체가 검색 색인에 있다는 설명도 KAPE 대상 작성자의 관찰입니다. 표와 칸을 직접 열어 확인합니다.
- **설치와 사용을 섞지 않습니다.** 관찰한 PC 처럼 원노트가 깔려 있어도 프로필에 흔적이 없을 수 있습니다.
- **시각 형식이 두 가지입니다.** 4바이트 Time32 를 FILETIME 으로 풀거나 반대로 풀면 엉뚱한 날짜가 나옵니다. Time32 의 시간대 기준도 확인하지 못했습니다.
- **bn 칸은 명세가 무시하라고 한 칸입니다.** 이 값으로 프로그램 버전을 단정하지 않습니다.
- **crcName 과 cbExpectedFileLength 로 결론을 내지 않습니다.** 원노트 밖에서 이름을 바꾸면 crcName 이 안 맞을 것이라는 추론은 확인하지 못했습니다. cbExpectedFileLength 가 실제 크기와 다르면 잘린 파일일 것이라는 추론도 확인하지 못했습니다. 명세는 cbExpectedFileLength 가 파일 크기라고만 적습니다. 두 추론은 아래 실습에서 시험해 봅니다.
- **이 페이지에서 확인하지 못한 곳이 있습니다.** 전자 필기장 목록을 담는 레지스트리 값, 필기장 안에서 지운 페이지를 보관하는 곳, 전자 필기장 내보내기 파일, 캐시 파일의 내부 형식은 확인하지 못했습니다. 조사에서 이 흔적이 필요하면 따로 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세의 값으로 만든 `.one` 파일 머리의 앞 64바이트 예시입니다. 실제 검체에서 나온 값이 아닙니다. guidFile 은 파일마다 다르므로 `??` 로 비워 두었습니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x000  E4 52 5C 7B 8C D8 A7 4D AE B1 53 78 D0 29 96 D3
0x010  ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??
0x020  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0x030  3F DD 9A 10 1B 91 F5 49 A5 D0 17 91 ED C8 AE D8
```

1. 0x000 의 16바이트는 guidFileType 입니다. 앞 4바이트 `E4 52 5C 7B` 를 뒤집으면 `7B5C52E4` 입니다.
2. 다음 2바이트 `8C D8` 을 뒤집으면 `D88C` 이고, 그다음 2바이트 `A7 4D` 를 뒤집으면 `4DA7` 입니다.
3. 나머지 8바이트는 그대로 읽습니다. `AEB1`, `5378D02996D3` 입니다.
4. 합치면 `{7B5C52E4-D88C-4DA7-AEB1-5378D02996D3}` 입니다. 구역 파일(`.one`)입니다. 목차 파일이면 이 줄이 `A1 2F FF 43 …` 으로 시작합니다.
5. 0x010 의 16바이트는 이 파일의 guidFile 입니다. 같은 방법으로 GUID 로 바꿔 적어 둡니다.
6. 0x020 의 16바이트는 guidLegacyFileVersion 입니다. 모두 0 이어야 합니다.
7. 0x030 의 16바이트는 guidFileFormat 입니다. `{109ADD3F-911B-49F5-A5D0-1791EDC8AED8}` 이어야 합니다.

실제 파일에서는 이어서 이렇게 확인합니다.

- 0x040~0x04F 의 4바이트 값 네 개가 `.one` 이면 모두 0x2A 인지 봅니다. `.onetoc2` 면 모두 0x1B 입니다.
- 0x080 의 guidAncestor 를 GUID 로 바꿉니다. 같은 폴더 `.onetoc2` 의 0x010(guidFile)과 같은지 봅니다.
- 0x0C4 의 cbExpectedFileLength 를 실제 파일 크기와 비교합니다.
- 0x0E4 의 nFileVersionGeneration 을 적어 둡니다. 같은 guidFile 의 다른 사본이 있으면 값을 비교합니다.
- 0x118~0x127 의 빌드 번호 네 개를 적어 둡니다. 결론에는 쓰지 않습니다.

### 공개 도구로 한 번

공개 도구의 예로 DissectMalware 의 pyOneNote 가 있습니다. `.one` 을 파싱해 속성과 첨부 파일을 꺼내는 파이썬 코드입니다. (pyOneNote)

- 도구가 낸 제목·작성자·시각을 헥스의 속성 값과 몇 개 맞춰 봅니다.
- 시각은 도구가 8바이트와 4바이트 가운데 어느 형식으로 풀었는지 확인합니다.
- 꺼낸 첨부 파일의 크기가 FileDataStoreObject 의 cbLength 와 같은지 봅니다.

스토어 앱 원노트 폴더는 KAPE 의 `MicrosoftOneNote.tkape` 대상으로 수집할 수 있습니다. 이 대상은 데스크톱 원노트 경로를 잡지 않습니다. (KAPE 대상 파일) 수집한 DB 는 SQLite 도구로 엽니다.

차이가 나면 헥스로 돌아갑니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 점 |
|---|---|
| [원드라이브](onedrive/index.md) | 동기화한 필기장과 첨부 원본 경로(`pathSource`)가 원드라이브 폴더인지 봅니다 |
| [오피스 사용 흔적](../file-folder-usage/microsoft-office/index.md) | 데스크톱 원노트는 오피스 프로그램입니다. 다른 오피스 흔적과 함께 봅니다 |
| [설치 프로그램](../system-account/uninstall.md) | 원노트가 설치됐는지 봅니다. 설치와 사용은 따로 판단합니다 |
| [스토어 앱 설치 목록](../system-account/appx-staterepository.md) | 스토어 앱 원노트가 설치됐는지 봅니다 |
| [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) | 스토어 앱 원노트 DB 를 읽는 법을 봅니다 |
| [마스터 파일 테이블](../filesystem/mft.md) | `.one`·`.onetoc2`·캐시 `.bin` 의 파일 시스템 시각을 봅니다 |
| [볼륨 섀도 복사본 구조](../../01-foundations/disk-volume/volume-shadow-copy.md) | 예전 시점의 `.one` 이 남았는지 봅니다. nFileVersionGeneration 으로 순서를 가립니다 |
| [인쇄 흔적](../external-devices/print-spooler-spl-shd.md) | 관찰한 PC 에는 원노트 가상 프린터가 있었습니다. 원노트로 보낸 인쇄가 남았는지 봅니다 |

첨부 파일의 출처를 따지는 흐름은 [이 파일은 어디서 왔나](../../04-scenarios/activity/file-origin.md) 에서 다룹니다.

## 실습

이 페이지에서는 원노트 파일이 든 공개 검체를 확인하지 못했습니다. Windows 가상 머신에 원노트를 설치해 직접 시험합니다. 시험 전에 원노트 종류와 버전을 적어 둡니다.

1. 원노트를 설치만 하고 열지 않습니다. 사용자 프로필에 `Microsoft\OneNote` 폴더가 생겼습니까?
2. 내 PC 에 전자 필기장 하나와 구역 두 개를 만듭니다. 각 파일의 첫 16바이트와 0x040~0x04F 값은 무엇입니까?
3. 두 `.one` 의 guidAncestor 가 같은 폴더 `.onetoc2` 의 guidFile 과 같습니까?
4. 페이지 하나를 고치기 전과 후에 파일을 복사합니다. nFileVersionGeneration, guidFileVersion, guidDenyReadFileVersion 은 어떻게 바뀌었습니까?
5. 페이지에 파일 하나를 넣습니다. pyOneNote 로 EmbeddedFileName 과 SourceFilepath 가 나옵니까? 캐시 폴더에 새 `.bin` 이 생겼습니까?
6. 원노트를 닫고 탐색기에서 `.one` 이름을 바꿉니다. crcName 은 바뀌었습니까? 새 이름과 맞습니까?
7. cbExpectedFileLength 는 실제 파일 크기와 같습니까?
8. 페이지를 만든 시각을 적어 둡니다. 4바이트 시각 값을 풀어 UTC 와 현지 시각 가운데 어느 쪽과 맞는지 봅니다.
9. 0x118~0x127 의 빌드 번호를 설치한 원노트 버전과 비교합니다.

## 참고 문헌

- Microsoft Learn, "[MS-ONESTORE]: Header" (2025-05-20 갱신) — https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-onestore/2b394c6b-8788-441f-b631-da1583d772fd
- DissectMalware, pyOneNote — FileNode.py — https://raw.githubusercontent.com/DissectMalware/pyOneNote/main/pyOneNote/FileNode.py
- EricZimmerman/KapeFiles, Targets/Apps/MicrosoftOneNote.tkape (작성자 Andrew Rathbun, 버전 1.0) — https://github.com/EricZimmerman/KapeFiles/blob/master/Targets/Apps/MicrosoftOneNote.tkape
- obsidianmd/obsidian-help, "Import from Microsoft OneNote" — https://github.com/obsidianmd/obsidian-help/blob/master/en/Import%20notes/Import%20from%20Microsoft%20OneNote.md
- stevencohn/OneMore — CaptionAttachmentsCommand.cs, AnalyzeCommand.cs, docs/get-started/Troubleshooting.htm — https://github.com/stevencohn/OneMore
