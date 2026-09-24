# 스티커 메모 (Sticky Notes)

## 한 줄 요약

스티커 메모는 Windows 에 딸려 오는 메모 앱입니다. Windows 10 1607 이후 스토어 앱은 메모를 패키지 폴더의 `plum.sqlite` 에 두고, 그 전 앱은 `StickyNotes.snt` 에 둡니다. `plum.sqlite` 의 `Note` 표에는 메모 본문과 만든·고친·지운 시각이 들어 있습니다.

> **(관찰)** 표시는 Windows 11 빌드 26200 PC 한 대에서 직접 본 내용입니다. 이 PC 에는 스티커 메모 패키지 6.1.4.0 이 깔려 있었고, 앱을 쓴 적이 없어 DB 가 없었습니다.
>
> **(설치 파일 문자열)** 표시는 그 패키지의 DLL 안에서 본 문자열입니다. 앱이 이 이름을 쓴다는 강한 단서이지만, 메모가 든 검체 DB 로 확인한 것은 아닙니다.

## 무엇을 기록하나 · 왜 생기나

- 사용자가 바탕 화면에 붙이는 짧은 메모를 저장합니다.
- 메모마다 본문, 색(테마), 창 위치, 열림 여부, 항상 위 여부가 남습니다.
- 메모마다 만든·고친·지운 시각이 남습니다.
- 서버 동기화에 쓰는 것으로 보이는 칸도 있습니다(아래 "동기화 흔적").

## 위치와 버전별 차이

| Windows 버전 | 파일 | 위치 |
|---|---|---|
| 7, 8, 10 1511 이하 | `StickyNotes.snt` | `C:\Users\<USER>\AppData\Roaming\Microsoft\StickyNotes\` 또는 `…\Microsoft\Sticky Notes\` |
| 10 1607 이후 | `plum.sqlite` (+ `plum.sqlite-wal`, `plum.sqlite-shm`) | `C:\Users\<USER>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\` |

- 옛 파일의 폴더 이름 철자가 자료마다 다릅니다. KAPE 대상 파일은 공백 없는 `StickyNotes` 를, 한 포렌식 블로그의 예시는 공백 있는 `Sticky Notes` 를 씁니다. 검체에서 두 이름을 모두 찾습니다.
- KAPE 대상 파일은 `Microsoft.MicrosoftStickyNotes*\LocalState\` 아래를 `plum.sqlite*` 로 모읍니다. 그래서 `-wal`·`-shm` 까지 함께 들어옵니다.
- KAPE 대상 파일은 옛 파일을 공백 없는 `StickyNotes` 폴더에서만 찾습니다. `Sticky Notes` 폴더는 따로 모읍니다.
- OneNote 앱 안에 들어간 새 스티커 메모가 어디에 저장되는지는 확인하지 못했습니다. [원노트](/02-artifacts/cloud-notes/onenote.md) 쪽도 함께 봅니다.

### 패키지 폴더 (관찰)

- 관찰한 PC 에는 패키지 `Microsoft.MicrosoftStickyNotes` 6.1.4.0 이 깔려 있었습니다.
- 패키지 폴더 안에는 `AC`, `AppData`, `LocalCache`, `LocalState`, `RoamingState`, `Settings`, `SystemAppData`, `TempState` 가 있었습니다.
- `Settings` 에는 `settings.dat`, `settings.dat.LOG1`, `settings.dat.LOG2` 가 있었습니다. 이 폴더의 구조는 [UWP 앱 데이터 구조](/01-foundations/app-mail-data/packages-settings-dat.md) 에 있습니다.
- 앱을 쓴 적이 없어 `LocalState` 는 비어 있었습니다.

## 구조

### plum.sqlite 판정

- SQLECmd 맵은 `Note`, `Media`, `Insight`, `User`, `Stroke` 다섯 표가 모두 있으면 스티커 메모 DB 로 판정합니다.
- 메모는 `Note` 표에 들어갑니다.
- SQLite 파일 구조는 [SQLite 데이터베이스](/01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.

### Note 표

두 자료에 나오는 칸을 합쳤습니다. "맵" 은 SQLECmd 맵이 읽는 칸, "설치 파일" 은 설치 파일 안 표 옮기기(마이그레이션) SQL 에 나오는 칸입니다.

| 칸 | 맵 | 설치 파일 | 내용 |
|---|---|---|---|
| `Id` | ○ | ○ | 메모 ID |
| `ParentId` | ○ | ○ | 부모 ID |
| `Text` | ○ | ○ | 메모 본문 |
| `Theme` | ○ | ○ | 메모 색 |
| `WindowPosition` | ○ | ○ | 창 위치 |
| `CreatedAt` | ○ | ○ | 만든 시각 |
| `UpdatedAt` | ○ | ○ | 고친 시각 |
| `DeletedAt` | ○ | ○ | 지운 시각 |
| `IsOpen` | ○ | | 열림 여부 (0/1) |
| `IsAlwaysOnTop` | ○ | | 항상 위 여부 (0/1) |
| `LastServerVersion` | ○ | | 서버 판 번호로 보입니다(이름에서 추론) |
| `Type`, `Revision`, `SyncRevision`, `CreationNoteIdAnchor` | | ○ | 이름만 확인했습니다 |
| `CreatedById`, `UpdatedById`, `DeletedById` | | ○ | 만든·고친·지운 주체 ID 로 보입니다(이름에서 추론) |

- 두 자료의 칸 목록이 다릅니다. 앱 판에 따라 칸이 늘거나 줄 수 있습니다. 검체에서 `.schema Note` 로 확인합니다.
- 설치 파일에 `UPDATE Note SET Theme='Yellow' WHERE Theme IS NULL` 이 있습니다 (설치 파일 문자열). 테마가 비어 있던 옛 메모를 노란색으로 채운다는 뜻입니다.

### 다른 표 (설치 파일 문자열)

| 표 | 칸 |
|---|---|
| `Stroke` | `Data`, `FormatVersion` |
| `StrokeMetadata` | `InkListItemId`, `InsightId`, `OffsetX`, `OffsetY`, `ReminderId`, `StrokeId` |
| `UpgradedNote` | `OldNoteId`, `NewNoteId`, `UpgradeManagerVersion`, `UpgraderVersion`, `ModifiedByUser` |
| `User` | — |
| `Insight` | — |

- `Media` 표는 SQLECmd 맵의 판정 조건에 나옵니다. 칸은 확인하지 못했습니다.
- `Stroke` 는 이름으로 보아 펜 입력 획을 담는 것으로 보입니다. 확인하지 못했습니다.
- `UpgradedNote` 는 이름으로 보아 옛 메모를 새 메모로 옮긴 기록으로 보입니다. `OldNoteId` 와 `NewNoteId` 가 짝을 이룹니다. 확인하지 못했습니다.

### 저널과 곁 파일

- 설치 파일에 `PRAGMA journal_mode=WAL` 이 있습니다 (설치 파일 문자열). 그래서 `plum.sqlite-wal`·`plum.sqlite-shm` 이 생깁니다.
- 아직 본 파일에 반영되지 않은 변경이 `-wal` 에 남아 있을 수 있습니다. 뜻과 읽는 법은 [WAL과 롤백 저널](/01-foundations/database-log-formats/sqlite/wal-journal-shm.md) 에 있습니다.

### 본문(Text)

- `Text` 칸의 형식은 확인하지 못했습니다.
- 앱 판에 따라 평문인지 서식 문서인지가 다를 수 있습니다. 검체에서 값을 원문 그대로 보고 형식을 정합니다.

### 옛 형식(.snt)과 업그레이드

- 한 포렌식 블로그는 옛 앱에서 "Note Text" 와 "Modification Date" 두 가지를 뽑습니다.
- `.snt` 의 내부 형식은 이 글의 자료로 확인하지 못했습니다. 파일 머리가 OLE 복합 파일 머리이면 [OLE 복합 파일](/01-foundations/shell-document-formats/compound-file-binary.md) 방법으로 엽니다.
- 업그레이드 모듈 `Microsoft.Notes.Upgrade.dll` 에 `Legacy`, `ThresholdNotes.snt`, `Version`, `Metafile`, `_text.rtf`, `_ink.bin` 문자열이 있습니다 (설치 파일 문자열).
- 앱이 옛 메모를 옮겨 올 때 쓰는 이름으로 보입니다. 정확한 경로와 각 문자열의 뜻은 확인하지 못했습니다. 패키지 폴더에서 이 이름들을 찾아봅니다.

### 동기화 흔적

- 설치 파일과 맵에 `RemoteId`, `ChangeKey`, `LastServerVersion`, `SyncState` 같은 이름이 나옵니다.
- 메모가 Microsoft 계정으로 서버와 동기화된다는 단서입니다(이름에서 추론).
- 어느 서비스와 동기화하는지, 서버 쪽에 무엇이 남는지는 확인하지 못했습니다.

## 증거로서 의미

### 증명하는 것

- `Note` 행으로 메모 본문과 만든·고친 시각을 알 수 있습니다.
- `DeletedAt` 에 값이 있는 행은 지운 메모가 행으로 남아 있는 것으로 보입니다(칸 이름에서 추론).
- `IsOpen`, `WindowPosition` 으로 메모 창의 열림 여부와 창 위치 값을 알 수 있습니다. 이 값이 어느 때 기준인지는 확인하지 못했습니다.
- 패키지 폴더는 있는데 `LocalState` 에 `plum.sqlite` 가 없으면 앱을 연 적이 없을 수 있습니다(관찰에서 추론).

### 증명하지 못하는 것

- 패키지 폴더가 있다고 앱을 썼다는 뜻은 아닙니다. Windows 에 기본으로 깔리는 앱입니다(관찰).
- 메모가 DB 에 있다고 이 PC 에서 쓴 메모라는 뜻은 아닙니다. 서버 동기화로 내려온 메모일 수 있습니다(추론).
- 지운 메모가 얼마나 오래 행으로 남는지는 확인하지 못했습니다. `DeletedAt` 행이 없다고 지운 메모가 없었던 것은 아닙니다.
- 시각 값이 UTC 인지 현지 시각인지 확인하지 못했습니다.
- `Theme` 가 `Yellow` 라도 사용자가 고른 색이 아닐 수 있습니다. 표를 옮길 때 테마가 비어 있던 메모는 앱이 노란색으로 채웁니다(설치 파일 문자열).

보고서에는 "사용자가 X 라고 적었다" 대신 이렇게 씁니다. "`plum.sqlite` 의 `Note` 표에 본문이 X 인 행이 있고, `CreatedAt` 값을 .NET 틱으로 보고 바꾸면 Y 이다. 이 값이 UTC 인지는 검체의 다른 시각과 맞춰 확인했다."

## 시각 해석

- SQLECmd 맵은 `CreatedAt`·`UpdatedAt`·`DeletedAt` 을 아래 식으로 바꿉니다.

```sql
datetime((값 / 10000000) - 62135596800, 'unixepoch')
```

- 곧 맵은 이 값을 .NET 틱으로 봅니다. .NET 틱은 0001-01-01 부터 센 100나노초 단위입니다.
- 62135596800 은 0001-01-01 과 1970-01-01 사이 초 수입니다(파이썬으로 계산해 확인).
- 맵은 `'unixepoch'` 로만 바꾸므로 값을 UTC 로 다룹니다. 저장값이 실제로 UTC 인지는 확인하지 못했습니다.
- 아래는 식으로 만든 계산 예시입니다. 검체 값이 아닙니다.

| 값 (10진) | 값 (16진) | 변환 결과 |
|---|---|---|
| 638396640000000000 | 0x08DC0A5C9900C000 | 2024-01-01 00:00:00 |

- 계산은 이렇게 합니다. 638396640000000000 ÷ 10000000 = 63839664000 초이고, 여기서 62135596800 을 빼면 1704067200 초입니다. 이 값은 1970-01-01 00:00 부터 센 Unix 초로 2024-01-01 00:00:00 입니다.
- 다른 시각 형식과의 관계는 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

## 함정과 한계

- **옛 폴더 이름 철자가 둘입니다.** `StickyNotes` 와 `Sticky Notes` 를 모두 찾습니다.
- **`-wal` 을 빠뜨리지 않습니다.** 최근 메모나 최근 수정이 `-wal` 에만 있을 수 있습니다. 도구로 원본을 바로 열면 `-wal` 이 본 파일에 합쳐질 수 있으므로 사본에서 엽니다.
- **패키지 폴더를 사용 증거로 쓰지 않습니다.** 기본 설치 앱입니다.
- **칸 목록이 판마다 다릅니다.** 맵과 설치 파일의 칸이 서로 다릅니다.
- **`Theme` 값을 사용자의 선택으로 단정하지 않습니다.**
- **OneNote 안의 새 스티커 메모는 이 글의 범위 밖입니다.** 저장 위치를 확인하지 못했습니다.
- **지운 메모가 파일 빈 공간에 남을 수 있습니다.** `DeletedAt` 행이 없어도 [파일 안에 남은 지운 레코드](/01-foundations/database-log-formats/sqlite/freelist-freeblock.md) 방법으로 찾아봅니다.

## 직접 분석해 보기

### 헥스로 한 번

1. `LocalState` 폴더의 `plum.sqlite`, `plum.sqlite-wal`, `plum.sqlite-shm` 을 함께 사본으로 뜹니다.
2. `plum.sqlite` 를 헥스 편집기로 열어 맨 앞이 SQLite 머리 문자열인지 봅니다.
3. 조사 대상 메모의 문구 하나를 검색합니다. `plum.sqlite` 와 `-wal` 에서 각각 찾아, 어느 쪽에 어떤 판이 있는지 적습니다.
4. 시각 값을 위 식으로 바꿉니다. 예를 들어 16진 `08 DC 0A 5C 99 00 C0 00` 여덟 바이트를 정수로 읽으면 638396640000000000 이고, 2024-01-01 00:00:00 이 됩니다. 이 바이트는 식으로 만든 예시이며 검체 값이 아닙니다. SQLite 레코드 안에서 정수가 어떤 바이트 순서로 놓이는지는 [파일·페이지 구조](/01-foundations/database-log-formats/sqlite/b-tree-record-format.md) 에 있습니다.

### 공개 도구로 한 번

- KAPE 대상 `MicrosoftStickyNotes` 는 `plum.sqlite*` 와 옛 `StickyNotes.snt` 를 모읍니다.
- SQLECmd 는 맵 `Windows_MicrosoftStickyNotes_NotesDB` 로 `Note` 표를 뽑고 시각을 바꿔 줍니다.
- SQLite 명령줄 도구(sqlite3) 같은 공개 도구로 직접 확인할 때는 아래처럼 뽑아 봅니다.

```sql
SELECT Id, ParentId, Theme, IsOpen, Text,
       datetime((CreatedAt / 10000000) - 62135596800, 'unixepoch') AS created,
       datetime((UpdatedAt / 10000000) - 62135596800, 'unixepoch') AS updated,
       datetime((DeletedAt / 10000000) - 62135596800, 'unixepoch') AS deleted
FROM Note;
```

- 도구 결과의 행 수와 시각 하나를 위 헥스 절차로 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 스토어 앱 설치 목록 | 패키지가 설치·갱신된 때를 봅니다 | [스토어 앱 설치 목록](/02-artifacts/system-account/appx-staterepository.md) |
| UWP 앱 데이터 구조 | 패키지 폴더와 `settings.dat` 를 읽습니다 | [UWP 앱 데이터 구조](/01-foundations/app-mail-data/packages-settings-dat.md) |
| 원노트 | OneNote 안 새 스티커 메모 쪽 흔적을 봅니다 | [원노트](/02-artifacts/cloud-notes/onenote.md) |
| USN 변경 저널 | `plum.sqlite`·`-wal` 이 언제 바뀌었는지 봅니다 | [USN 변경 저널](/02-artifacts/filesystem/usnjrnl.md) |
| 섀도 복사본 활용 | 예전 시점의 `plum.sqlite` 에서 지금은 없는 메모를 찾습니다 | [섀도 복사본 활용](/03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 시간대 설정 | 시각 값을 현지 시각과 맞출 때 봅니다 | [시간대 설정](/02-artifacts/system-account/time-zone.md) |

## 실습

스티커 메모를 쓴 공개 검체(NIST CFReDS 등)를 구하거나, 시험용 PC 에서 메모를 몇 개 만들고 하나를 지운 뒤 아래 질문을 풀어 봅니다.

1. 검체의 Windows 버전은 무엇입니까? `StickyNotes.snt` 와 `plum.sqlite` 가운데 무엇이 있습니까?
2. `plum.sqlite` 의 표 목록을 뽑습니다. `Note`, `Media`, `Insight`, `User`, `Stroke` 가 모두 있습니까? `UpgradedNote` 가 있습니까?
3. `.schema Note` 의 칸 목록을 위 표와 비교합니다. 없는 칸과 새로 보이는 칸은 무엇입니까?
4. 지운 메모의 행이 남아 있습니까? `DeletedAt` 값을 바꾸면 지운 시각과 맞습니까? UTC 로 맞습니까, 현지 시각으로 맞습니까?
5. 최근에 고친 메모의 문구가 `plum.sqlite` 와 `-wal` 가운데 어디에 있습니까?
6. `Text` 값은 평문입니까, 서식이 섞인 형식입니까?

## 참고 문헌

1. Eric Zimmerman 외, KapeFiles GitHub 저장소 (커밋 ed0f9c7), `Targets/Apps/MicrosoftStickyNotes.tkape` — https://github.com/EricZimmerman/KapeFiles
2. Eric Zimmerman 외, SQLECmd GitHub 저장소 (커밋 7f89270), `SQLMap/Maps/Windows_MicrosoftStickyNotes_NotesDB.smap` — https://github.com/EricZimmerman/SQLECmd
3. Forensafe, Lina Alsoufi, "Sticky Notes" 블로그 (2021-10-18) — https://www.forensafe.com/blogs/stickynotes.html
