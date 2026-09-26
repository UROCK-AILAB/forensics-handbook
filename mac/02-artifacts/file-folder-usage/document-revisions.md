---
title: "문서 버전"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 900
---

# 문서 버전 (DocumentRevisions-V100)

버전 기능을 지원하는 앱이 문서를 저장할 때마다 macOS 는 볼륨 루트의 숨김 폴더 `.DocumentRevisions-V100` 에 그 시점의 버전을 쌓아 두고, 그 안의 데이터베이스에 파일 경로와 버전이 추가된 시각이 남아서 문서가 언제 어떤 모습으로 저장됐는지 되짚을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

미리보기, TextEdit, Pages, Numbers 처럼 버전 기능을 지원하는 앱은 파일을 저장할 때 현재 버전을 하나 추가하고, 이 일은 `revisiond` 서비스가 맡습니다 [1]. 파일 메뉴에 "되돌리기 (Revert To)" 가 있는 앱은 대체로 이 기능을 지원하고, 앱별로 끌 방법은 없습니다 [1]. 사용자가 이전 버전으로 되돌아갈 수 있게 하려고 만든 기능이지만, 조사에서는 문서가 저장된 시각의 목록과 예전 내용 자체가 함께 남는 자리가 됩니다.

버전은 영원히 남지 않습니다. 원본 파일을 지우면 버전도 사라지고, 파일을 복제해 이름을 바꾸면 복제본에는 버전이 따라가지 않습니다. 전용 도구로 버전을 하나씩 지울 수도 있고, 지운 버전은 되살릴 수 없습니다 [1]. 다만 공개 도구 mac_apt 는 데이터베이스가 더는 가리키지 않는 저장 조각(고아 조각)에서 지워진 내용이 나올 수 있다고 보고 이런 조각을 따로 추출합니다 [2].

## 위치와 버전별 차이

일반 작업 파일을 두는 볼륨마다 루트에 `.DocumentRevisions-V100` 폴더가 하나씩 있습니다 [1]. 10.15 Catalina 이후 시스템 볼륨과 데이터 볼륨이 나뉜 구조에서는 아래 두 곳을 모두 찾아봅니다 [2]. 두 볼륨이 어떻게 이어져 보이는지는 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../01-foundations/disk-volume/volume-group-firmlinks.md)에서 다룹니다.

```
/.DocumentRevisions-V100
/System/Volumes/Data/.DocumentRevisions-V100
```

폴더 안은 아래처럼 짜여 있습니다 [1][2].

| 항목 | 내용 |
|---|---|
| `db-V1/db.sqlite` | 버전 데이터베이스 |
| `.cs/ChunkStoreDatabase` | 저장 조각 데이터베이스 |
| `.cs/ChunkStorage/` | 번호 붙은 저장 조각 폴더 |
| `AllUIDs/` | 안에 `com.apple.documentVersion` 폴더가 있음 |
| `LibraryStatus` | 데이터베이스 상태를 믿을 수 있는지 적은 plist |
| `metadata`, `purgatory`, `staging` | 그 밖의 하위 항목 |

iOS 이미지에서는 `/private/var/mobile/.DocumentRevisions-V100/db-V1/db.sqlite` 에 같은 데이터베이스가 있습니다 [2].

버전별로 알려진 차이는 아래와 같습니다.

| 범위 | 내용 | 출처 |
|---|---|---|
| 10.15 Catalina 이후 | 시스템 볼륨 루트와 `/System/Volumes/Data` 두 곳을 모두 찾아야 함 | [2] |
| 10.15 Catalina 까지 | Time Machine 이 이 폴더를 백업했지만 제대로 복원하지는 못함 | [1] |
| 15 Sequoia (15.6.1) | 사용자별 번호 폴더가 든 `PerUID` 가 보인다는 독자 댓글. 댓글이라 믿을 정도가 낮음 | [1] |
| 검체에서 확인 | 썸네일 파일이 `thumbnail.png` 인지 `thumbnail.jpeg` 인지가 macOS 버전에 따라 갈리는지 | [2] |

## 구조

### 버전 데이터베이스 (db.sqlite)

`db-V1/db.sqlite` 는 SQLite 파일이라서 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)를 따르고, 여기서는 버전 분석에 쓰는 표와 칸만 봅니다 [2].

| 표 | 칸 | 뜻 |
|---|---|---|
| `files` | `file_inode` | 원본 파일의 inode |
| | `file_path` | 원본 파일 경로 |
| | `file_last_seen` | mac_apt 출력 이름 `File_Last_Seen_UTC` |
| | `file_storage_id` | `generations` 와 잇는 값 |
| `generations` | `generation_id` | 버전 번호 |
| | `generation_storage_id` | `files.file_storage_id` 와 같은 값 |
| | `generation_add_time` | mac_apt 출력 이름 `Generation_Added_UTC` |
| | `generation_path` | `.DocumentRevisions-V100` 기준 상대 경로 |
| | `generation_size` | 버전 크기 |

두 표는 `generations.generation_storage_id = files.file_storage_id` 로 이어서 한 원본 파일에 딸린 버전을 모두 모읍니다 [2]. `generation_path` 가 `:QLThumbnailAdditionName` 으로 끝나는 항목은 버전 파일이 아니라 썸네일 폴더이고, mac_apt 는 그 안에서 `thumbnail.png`, `thumbnail.jpeg` 순서로 찾고 둘 다 없으면 첫 번째 파일을 씁니다 [2].

저장된 버전 파일에는 원래 이름을 담은 확장 속성 두 개가 붙습니다 [2]. `com.apple.genstore.origdisplayname` 은 원래 표시 이름이고 `com.apple.genstore.origposixname` 은 원래 파일 이름이라서, 원본 파일이 지워지거나 이름이 바뀐 뒤에도 버전 파일만 보고 원래 이름을 알 수 있습니다.

### 저장 조각 (ChunkStoreDatabase·ChunkStorage)

버전 내용 일부는 `.cs` 아래 조각 저장소에 나뉘어 들어가고, 조각은 아래 두 표로 찾아 이어 붙입니다 [2].

| 표 | 칸 | 뜻 |
|---|---|---|
| `CSStorageChunkListTable` | `clt_rowid`, `clt_count` | 행 번호, 조각 개수 |
| | `clt_inode` | 저장된 버전 파일의 inode 와 맞추는 값 |
| | `clt_chunkRowIDs` | 리틀엔디언 8바이트 행 번호를 나열한 값 |
| `CSChunkTable` | `ct_rowid` | 조각 행 번호 |
| | `ft_rowid` | 조각 파일 이름 |
| | `offset`, `dataLen` | 조각 파일 안의 위치와 길이 |
| | `cid`, `timeStamp` | 조각 식별자, 시각 |

조각 파일은 `ChunkStorage` 아래 4단계 경로에 정수 이름으로 놓이고, 조각마다 25바이트 머리 뒤에 내용이 옵니다 [2]. 머리의 앞 4바이트는 머리를 포함한 크기(빅엔디언)이고 나머지 21바이트는 `cid` 입니다.

```
.cs/ChunkStorage/<xx>/<yy>/<zz>/<정수 이름>
```

버전 하나를 되살릴 때는 버전 파일의 inode 로 `CSStorageChunkListTable` 행을 찾고, `clt_chunkRowIDs` 를 8바이트씩 끊어 `CSChunkTable` 의 `ct_rowid` 를 찾은 뒤, `ft_rowid` 이름의 조각 파일에서 `offset`·`dataLen` 만큼 읽어 차례로 붙입니다 [2].

> 그림 자리: `files` → `generations` → 버전 파일(inode) → `CSStorageChunkListTable` → `CSChunkTable` → `ChunkStorage` 조각 파일로 이어지는 연결 그림

## 증거로서 의미

**증명하는 것.** `files` 에 경로가 있고 `generations` 에 버전이 딸려 있으면, 그 경로의 파일을 버전 기능을 지원하는 앱이 저장한 기록이 이 볼륨에 있다는 뜻입니다 [1][2]. 버전 파일이나 조각을 되살리면 그 시점의 내용을 직접 볼 수 있고, 버전이 여러 개면 문서가 어떤 순서로 바뀌어 왔는지 비교할 수 있습니다. 원본 파일이 이미 없어도 버전 파일의 확장 속성으로 원래 이름을 확인할 수 있습니다 [2].

**증명하지 못하는 것.** 이 기록만으로는 어느 사용자 계정의 것인지 가리기 어렵습니다(사용자별 `PerUID` 폴더가 보인다는 독자 댓글이 있을 뿐입니다 [1]). 저장하지 않고 열어만 본 문서, 버전 기능을 지원하지 않는 앱으로 고친 문서는 이 기록에 나타나지 않을 수 있습니다. 반대로 기록이 없다고 해서 문서를 고친 적이 없다고 말할 수도 없는데, 원본 삭제·복제 뒤 이름 바꾸기·개별 삭제로 버전이 사라지기 때문입니다 [1]. 버전의 존재는 앱이 그 시각에 저장했다는 기록일 뿐이라서, 사람이 저장 단추를 눌렀는지 앱이 스스로 저장했는지는 따로 판단합니다.

보고서에는 "이 볼륨의 버전 데이터베이스에 이 경로의 파일 버전 N개가 있고, 버전이 추가된 시각은 아래와 같다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

| 값 | 읽는 방식 | 기준 |
|---|---|---|
| `generation_add_time` | 유닉스 시각 (mac_apt `ReadUnixTime`) | UTC 로 출력 (`Generation_Added_UTC`) |
| `file_last_seen` | 유닉스 시각 (mac_apt `ReadUnixTime`) | UTC 로 출력 (`File_Last_Seen_UTC`) |
| `CSChunkTable.timeStamp` | 공개 자료 없음 | 검체에서 확인 |

두 시각 모두 유닉스 시각이고 UTC 로 읽습니다 [2]. `generation_add_time` 은 칸 이름과 mac_apt 출력 이름대로라면 버전이 추가된 시각이지만, `file_last_seen` 이 정확히 어떤 일이 있을 때 바뀌는지는 공개된 설명이 없어서 이름 그대로 "마지막으로 본 시각" 정도로만 적습니다. 값의 단위와 기준 시점은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에서 확인합니다. `timeStamp` 칸은 기준이 알려져 있지 않아서 다른 시각과 섞어 타임라인에 넣지 않습니다.

## 함정과 한계

- **볼륨 하나만 보는 경우.** 폴더는 볼륨마다 있어서 [1], 외장 볼륨이나 데이터 볼륨 쪽을 빼면 버전을 놓칩니다. Catalina 이후 이미지에서는 두 경로를 모두 확인합니다 [2].
- **숨김 폴더를 빼고 수집하는 경우.** `.DocumentRevisions-V100` 과 그 안의 `.cs` 는 이름이 점으로 시작해서, 숨김 항목을 건너뛰는 수집 방법으로는 빠집니다. 폴더 접근 권한과 SIP 보호 여부는 공개 자료가 없으니, 라이브 수집이라면 읽기에 실패한 항목을 수집 기록에 남깁니다.
- **`file_path` 를 지금 위치로 읽는 경우.** 경로는 기록 당시의 값이고, 파일이 지워지거나 옮겨졌을 수 있습니다. 원본은 inode 와 확장 속성으로 다시 맞춰 봅니다.
- **썸네일 폴더를 버전으로 세는 경우.** `:QLThumbnailAdditionName` 으로 끝나는 `generation_path` 는 썸네일이라서 [2] 버전 개수에서 뺍니다.
- **백업에서 되살리려는 경우.** Time Machine 은 Catalina 까지 이 폴더를 백업했지만 제대로 복원하지는 못했습니다 [1]. 백업 속 폴더는 복원하지 말고 파일째 꺼내 분석합니다.
- **`LibraryStatus` 를 건너뛰는 경우.** 데이터베이스 상태를 믿을 수 있는지 적은 plist 라서 [1], 데이터베이스를 해석하기 전에 먼저 열어 봅니다.
- **지우기와 조작.** 버전을 전용 도구로 지우거나 원본 파일을 지우면 버전이 사라지고 되살릴 수 없다는 설명이 있지만 [1], mac_apt 는 고아 조각에서 지워진 내용을 찾습니다 [2]. 일부러 지운 정황은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)의 흐름으로 판단합니다.

## 직접 분석해 보기

이미지에서 볼륨 루트의 `.DocumentRevisions-V100` 폴더 전체를 작업 폴더로 복사하고, 버전 파일의 확장 속성과 inode 가 함께 보존되는지 확인합니다.

### 헥스로 한 번

아래 바이트는 mac_apt 가 읽는 조각 머리 구조에 맞춰 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. 조각 파일에서 `offset` 위치로 가면 이런 머리가 보입니다.

```
조각 하나 (예시)
00 00 00 20                                   크기 = 0x20 = 32바이트 (머리 25바이트 포함, 빅엔디언)
.. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..   cid (21바이트)
.. .. .. .. .. .. ..                          내용 (32 - 25 = 7바이트)
```

앞 4바이트 크기에서 25를 빼면 내용 길이가 나오고, 이 값을 `CSChunkTable` 의 `dataLen` 과 견주어 도구가 머리를 빼고 읽는지 확인합니다. `clt_chunkRowIDs` 는 리틀엔디언 8바이트 정수가 이어진 값이라서, 헥스로 볼 때는 8바이트씩 끊고 바이트 순서를 뒤집어 행 번호를 읽습니다 [2].

### 공개 도구로 한 번

mac_apt 의 `DOCUMENTREVISIONS` 플러그인(2.1)은 두 경로를 찾아 데이터베이스를 읽고, 버전 파일과 조각을 이어 붙이며, 고아 조각도 따로 추출합니다 [2]. 결과를 손으로 확인하려면 복사해 둔 `db.sqlite` 에 SQLite 명령행 도구로 mac_apt 와 같은 연결을 걸어 봅니다. mac_apt 는 `generations` 를 기준으로 `files` 를 LEFT JOIN 하므로, `files` 쪽 행이 없는 버전도 결과에서 빠지지 않습니다 [2].

```sql
SELECT f.file_inode,
       f.file_path,
       datetime(f.file_last_seen, 'unixepoch')      AS file_last_seen_utc,
       g.generation_id,
       datetime(g.generation_add_time, 'unixepoch') AS generation_added_utc,
       g.generation_path,
       g.generation_size
FROM generations g
LEFT JOIN files f ON g.generation_storage_id = f.file_storage_id
ORDER BY f.file_path, g.generation_add_time;
```

`generation_path` 가 가리키는 버전 파일을 열 때는 `xattr -l` 로 `com.apple.genstore.origdisplayname` 과 `com.apple.genstore.origposixname` 을 함께 확인해서, 쿼리 결과의 경로와 원래 이름이 맞는지 봅니다 [2].

## 교차 검증

- [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) — 버전이 추가된 시각 무렵 원본 파일의 변경·이름 바꾸기·삭제 흔적
- [빠른 보기 섬네일 캐시 (QuickLook)](quicklook-thumbnails.md) — 버전 썸네일과 별도로 남는 미리보기 흔적
- [최근 항목 (Shared File Lists)](recent-items/index.md), [앱 저장 상태 (Saved Application State)](saved-application-state.md) — 같은 문서를 어느 앱으로 열었는지
- [문서 메타데이터 (iWork·Office)](../embedded-metadata/iwork-office.md) — 버전 내용 안에 든 작성·수정 정보
- [타임 머신 (Time Machine)](../filesystem/time-machine/index.md), [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md) — 버전이 사라진 문서를 다른 곳에서 찾을 때
- [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) — 고아 조각을 다룰 때
- [이 파일을 누가 언제 열었나 (File Access)](../../04-scenarios/activity/file-access.md), [이 문서의 날짜를 믿을 수 있나 (Document Date)](../../04-scenarios/activity/document-date.md) — 이 기록을 쓰는 조사 흐름

## 실습

NIST CFReDS 같은 공개 검체 가운데 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 이미지 안의 볼륨마다 `.DocumentRevisions-V100` 이 있나요? Catalina 이후 이미지라면 두 경로 가운데 어디에 있나요?
2. `files` 에 나온 경로 가운데 지금 파일 시스템에 없는 파일은 몇 개인가요?
3. 버전이 가장 많은 파일을 골라 `generation_add_time` 을 UTC 로 늘어놓고, 같은 시각 무렵 FSEvents 에 그 파일의 변경 기록이 있는지 보세요.
4. `:QLThumbnailAdditionName` 항목을 빼면 버전 개수가 어떻게 달라지나요? 썸네일 파일 확장자는 무엇인가요?
5. 버전 파일의 `com.apple.genstore.origposixname` 과 `file_path` 의 파일 이름이 다른 경우가 있나요?

## 참고 문헌

1. The Eclectic Light Company, "Managing macOS versioning and the DocumentRevisions-V100 folder" (2025-09-08) — https://eclecticlight.co/2025/09/08/managing-macos-versioning-and-the-documentrevisions-v100-folder/
2. mac_apt `plugins/documentrevisions.py` (DOCUMENTREVISIONS 2.1, Yogesh Khatri·Nicole Ibrahim) — https://github.com/ydkhatri/mac_apt/blob/master/plugins/documentrevisions.py
