---
title: "메모"
parent: "아티팩트 · 클라우드·애플 앱"
nav_order: 1560
---

# 메모 (Notes)

맥의 메모 앱은 macOS 10.13 High Sierra 이후 `NoteStore.sqlite` 한 파일에 메모의 제목·미리보기·만든 시각과 압축된 본문을 담고 첨부 파일은 그룹 컨테이너 아래 폴더에 따로 두므로, 어떤 메모가 언제 만들어졌고 무엇을 적었는지 읽을 수 있습니다.

이 페이지는 메모 DB의 위치와 표 구조, 잠긴 메모의 암호화 방식을 다룹니다. SQLite 파일 자체를 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

메모 앱은 메모마다 제목, 본문 앞부분을 뽑은 미리보기, 만든 시각과 수정 시각, 들어 있는 폴더와 계정, 잠금 여부와 암호 힌트를 한 표에 적고, 본문은 다른 표에 압축해서 넣습니다 [1]. 첨부한 이미지나 파일은 DB 밖의 폴더에 원래 파일 이름으로 남습니다 [1].

메모는 아이클라우드 계정으로 다른 기기와 동기화되기도 해서, 맥의 DB에 있는 메모가 그 맥에서 쓴 것인지 다른 기기에서 넘어온 것인지는 DB만으로 구분하지 못합니다. 조사에서는 계정 열과 [아이클라우드 계정 (iCloud Account)](icloud-account.md)을 함께 봅니다.

## 위치와 버전별 차이

현재 DB는 아래 자리에 있습니다 [1][2].

```
~/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite
```

macOS 버전마다 메모 DB 파일은 아래와 같습니다 [1].

| macOS | 메모 DB 파일 |
|---|---|
| 10.8 Mountain Lion | `~/Library/Containers/com.apple.Notes/Data/Library/Notes/NotesV1.storedata` |
| 10.9 Mavericks | 같은 폴더의 `NotesV2.storedata` |
| 10.10 Yosemite | 같은 폴더의 `NotesV4.storedata` |
| 10.11 El Capitan, 10.12 Sierra | `NotesV6.storedata` 와 `NoteStore.sqlite` 둘 다 |
| 10.13 High Sierra 이후 | `NoteStore.sqlite` 만 |

Catalina 이후 맥에서는 `NoteStore.sqlite` 를 보면 되지만, 예전 macOS에서 올린 맥이라면 컨테이너 폴더에 `NotesV*.storedata` 가 남아 있는지도 찾아봅니다. ForensicArtifacts 정의에는 `NotesV*.storedata` 항목만 있고 `NoteStore.sqlite` 항목은 없어서 [4], 이 정의만 쓰는 도구로 자동 수집하면 현재 DB가 빠질 수 있습니다.

High Sierra 이후 첨부 파일은 그룹 컨테이너 안의 `Media` 폴더 아래 이런 모양으로 놓이고, `{generation}` 폴더는 DB에 generation 값이 있을 때만 끼어듭니다 [1].

```
Media/{첨부 UUID}/{generation}/{파일 이름}
```

`Media` 폴더는 계정마다 `Accounts/{계정 식별자}/` 아래에 있고, 로컬 계정("이 Mac에")은 계정 폴더 없이 그룹 컨테이너 바로 아래를 쓰기도 합니다 [5]. 그래서 실제 데이터에서는 두 자리를 모두 찾아봅니다.

DB가 WAL 모드로 `NoteStore.sqlite-wal` 을 쓰는지와 미리보기 이미지 폴더의 경로는 공개 자료에 나와 있지 않아 실제 데이터로 확인합니다.

## 구조

### 현재 형식

| 표 | 열 | 뜻 |
|---|---|---|
| `ZICCLOUDSYNCINGOBJECT` | `ZTITLE1`, `ZSNIPPET` | 제목과 미리보기 [1] |
| | `ZCREATIONDATE1` 또는 `ZCREATIONDATE3` | 만든 시각(아래 설명) [1][5] |
| | `ZMODIFICATIONDATE1` | 수정 시각 [1][5] |
| | `ZFOLDER`, `ZACCOUNT` | 들어 있는 폴더와 계정 [1] |
| | `ZISPASSWORDPROTECTED`, `ZPASSWORDHINT` | 잠금 여부와 암호 힌트 [1] |
| | `ZIDENTIFIER` | 메모의 UUID [2] |
| `ZICNOTEDATA` | `ZDATA` | 압축된 본문 [1][2] |

수정 시각은 `ZMODIFICATIONDATE1` 열에 있습니다 [1][5]. 만든 시각 열은 버전에 따라 자리를 옮겨서, iOS 15부터는 `ZCREATIONDATE1` 대신 `ZCREATIONDATE3` 에 들어갑니다 [5]. 맥에서 어느 macOS 버전부터 바뀌었는지는 공개 자료에 나와 있지 않으니, 실제 데이터에서 열 목록을 먼저 보고 값이 든 열을 고릅니다. 지운 메모를 표시하는 열(`ZMARKEDFORDELETION`)과 "최근 삭제된 항목" 폴더가 DB에 어떻게 남는지도 공개 분석 자료에 나와 있지 않아 실제 데이터로 확인합니다.

`ZDATA` 본문은 gzip으로 압축돼 있고, 압축을 풀면 안에 protobuf가 있습니다 [2][5]. apple_cloud_notes_parser는 푼 결과를 `ZPLAINTEXT` 와 `ZDECOMPRESSEDDATA` 열로 덧붙입니다 [2]. 이 두 열은 원래 DB에 있는 열이 아니라 도구가 만든 열이라서, 도구가 처리한 사본과 원본 DB를 섞지 않습니다. 압축은 zlib 머리말과 gzip 머리말을 모두 알아보게 해서 풀고, 푼 protobuf 비슷한 구조에서 태그 0x1A와 0x12를 따라가면 UTF-8 본문 글자가 나옵니다 [1]. 압축 형식 자체는 [압축 형식 (LZFSE·LZ4·zlib)](../../01-foundations/value-decoding/compression.md)에서 다룹니다.

### 예전 형식

`NotesV*.storedata` 쪽 표는 이렇습니다 [1].

| 표 | 열 |
|---|---|
| `ZNOTEBODY` | `ZHTMLSTRING`(HTML 본문) |
| `ZATTACHMENT` | `ZCONTENTID`, `ZFILEURL` |
| `ZACCOUNT` | `ZEMAILADDRESS`, `ZACCOUNTDESCRIPTION`, `ZUSERNAME` |

### 잠긴 메모

메모 앱은 사용자 암호에서 PBKDF2와 SHA-256으로 16바이트 키를 만들고, 그 키로 메모와 첨부를 AES-GCM으로 암호화합니다 [3]. 반복 횟수는 공개되지 않았고, 초기화 벡터(IV)와 태그는 Core Data와 CloudKit에 저장됩니다 [3]. 만든 날짜와 수정 날짜 같은 메타데이터는 암호화하지 않아서 [3], 잠긴 메모도 시각은 읽힙니다. 잠금을 풀 때는 암호를 넣거나 Touch ID 같은 생체 인증을 쓰고, 맥에서는 메모 앱이 백그라운드로 넘어간 뒤 8분이 지나면 잠금이 다시 걸립니다(iPhone·iPad는 3분) [3]. 잠글 수 있는 첨부는 이미지, 스케치, 표, 지도, 웹 사이트 같은 몇 종류뿐이라서, 다른 종류의 첨부가 든 메모는 잠글 수 없습니다 [3].

iOS 16부터 생긴 "기기 암호로 잠금" 방식은 공개 도구 apple_cloud_notes_parser로 풀 수 없고 [2], 맥에서 이 방식이 생긴 macOS 버전은 공개된 자료가 없습니다. 암호화된 증거를 다루는 절차는 [암호화된 증거 다루기 (Encrypted Evidence)](../../03-techniques/analysis/encrypted-evidence/index.md)를 따릅니다.

## 증거로서 의미

**증명하는 것.** `ZICCLOUDSYNCINGOBJECT` 에 행이 있으면 그 제목과 미리보기를 담은 메모가 이 사용자의 메모 DB에 있었다는 기록이고, 만든 시각 열은 그 메모가 만들어진 시각을 알려 줍니다 [1]. `ZISPASSWORDPROTECTED` 가 켜진 메모는 잠겨 있었다는 기록이고, `ZPASSWORDHINT` 에는 사용자가 적은 암호 힌트가 남습니다 [1]. 잠긴 메모도 만든 날짜와 수정 날짜는 암호화하지 않으므로 [3], 본문을 풀지 못해도 메모가 언제 만들어지고 바뀌었는지는 적을 수 있습니다. 첨부 폴더에 파일이 있으면 그 파일이 메모에 첨부된 적이 있다는 기록입니다 [1].

**증명하지 못하는 것.** 메모가 DB에 있다는 사실만으로 이 맥에서 직접 입력했는지, 동기화로 넘어왔는지는 알 수 없습니다. 미리보기 열은 본문 앞부분일 뿐이라서 전체 내용은 `ZDATA` 를 풀어 확인하고, 잠긴 메모는 본문을 풀지 못하면 내용을 알 수 없습니다. 지운 메모가 DB에 어떻게 남는지는 공개 분석 자료에 나와 있지 않아서, 행이 없다고 메모를 만든 적이 없다고 쓰지 않습니다.

보고서에는 "이 사용자의 메모 DB에 이 제목의 메모가 있고, 만든 시각 열의 값은 이 시각이다" 처럼 쓰고, 입력한 기기는 따로 적습니다.

## 시각 해석

메모의 시각 열은 맥 절대 시각(2001-01-01 기준 초)입니다 [1]. 유닉스 시각으로 바꿀 때는 값에 978307200초를 더하고, 기준 시간대와 소수점 처리는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다. 만든 시각은 메모를 만들 때 정해지고, 수정 시각이 정확히 어떤 동작에 바뀌는지를 다룬 공개 자료는 없습니다.

## 함정과 한계

- **만든 시각 열 이름.** 만든 시각은 버전에 따라 `ZCREATIONDATE1` 이나 `ZCREATIONDATE3` 에 들어서 [5], 한 열만 가정한 쿼리는 값을 비워 둔 채 끝날 수 있습니다. 실제 데이터에서 먼저 열 목록으로 확인합니다.
- **도구가 덧붙인 열.** `ZPLAINTEXT`, `ZDECOMPRESSEDDATA` 는 도구가 만든 열입니다 [2]. 보고서에 원본 DB의 열처럼 적지 않습니다.
- **수집 정의 누락.** ForensicArtifacts 정의에 `NoteStore.sqlite` 가 없어서 [4], 수집 목록을 따로 확인합니다.
- **풀 수 없는 잠금 방식.** "기기 암호로 잠금" 방식은 공개 도구로 풀 수 없습니다 [2]. 본문이 안 풀린 메모를 비어 있는 메모로 적지 않습니다.
- **힌트의 무게.** `ZPASSWORDHINT` 는 사용자가 적은 글이라서, 힌트 내용을 암호 자체로 단정하지 않습니다.
- **알려지지 않은 삭제 처리.** 지운 메모 표시 열과 WAL 파일 여부는 공개 분석 자료에 나와 있지 않아 실제 데이터로 확인합니다. 삭제 흔적을 찾는 일반 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

`NoteStore.sqlite` 사본에서 `ZICNOTEDATA` 의 `ZDATA` 한 칸을 파일로 뽑아 헥스 편집기로 엽니다. 압축 머리말을 확인하는 법은 [압축 형식 (LZFSE·LZ4·zlib)](../../01-foundations/value-decoding/compression.md)에서 다루고, 압축을 푼 바이트에서 태그 0x1A와 0x12를 차례로 따라가면 본문 글자가 UTF-8로 나옵니다 [1].

### 공개 도구로 한 번

사본을 만든 뒤 `sqlite3` 으로 메타데이터를 먼저 봅니다. 만든 시각 열은 실제 데이터에서 확인한 이름(`ZCREATIONDATE1` 또는 `ZCREATIONDATE3`)으로 바꿉니다.

```
sqlite3 NoteStore.sqlite ".schema ZICCLOUDSYNCINGOBJECT"
sqlite3 NoteStore.sqlite "SELECT ZIDENTIFIER, ZTITLE1, ZSNIPPET,
  datetime(ZCREATIONDATE1 + 978307200, 'unixepoch') AS created_utc,
  ZISPASSWORDPROTECTED, ZPASSWORDHINT
  FROM ZICCLOUDSYNCINGOBJECT WHERE ZTITLE1 IS NOT NULL;"
```

본문까지 풀어 보려면 mac_apt의 메모 플러그인 [1]이나 apple_cloud_notes_parser [2]를 씁니다. apple_cloud_notes_parser는 iOS 9~26의 Cloud Notes와 iOS 9 이전의 평문 메모를 다루고, 결과를 CSV·HTML·JSON으로 내며 Ruby 3.0 이상이 필요합니다 [2]. 지원하는 macOS 버전 범위는 공개되지 않았으니, 두 도구의 결과를 위 쿼리 결과와 맞춰 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [아이클라우드 계정 (iCloud Account)](icloud-account.md) | 메모 계정 열이 가리키는 계정과 로그인 기록 |
| [사진 메타데이터 (EXIF·HEIC)](../embedded-metadata/exif-heic.md) | 첨부 이미지의 촬영 정보 |
| [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md) | 메모 앱을 쓴 시간대 |
| [스포트라이트 (Spotlight)](../file-folder-usage/spotlight/index.md) | 메모 내용이 검색 색인에 남았는지 |
| [타임 머신 (Time Machine)](../filesystem/time-machine/index.md) | 예전 시점의 `NoteStore.sqlite` 와 비교 |
| [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md) | 사라진 메모 행을 백업에서 찾기 |

## 실습

공개 시험 데이터(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 이미지의 macOS 버전을 확인하고, 그 버전에서 메모 DB가 어느 파일인지 위 표로 정한 뒤 실제로 있는지 찾아보세요.
2. `ZICCLOUDSYNCINGOBJECT` 의 열 목록에서 만든 시각이 `ZCREATIONDATE1` 과 `ZCREATIONDATE3` 가운데 어느 열에 들어 있는지 확인해 보세요.
3. 잠긴 메모가 있으면 만든 시각과 암호 힌트를 뽑고, 본문을 풀지 않고 적을 수 있는 사실만 정리해 보세요.
4. 첨부 폴더의 파일 하나를 골라 DB의 어느 메모와 이어지는지 따라가 보세요.

## 참고 문헌

1. mac_apt (Yogesh Khatri), plugins/notes.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/notes.py
2. threeplanetssoftware, Apple Cloud Notes Parser (GitHub README) — https://github.com/threeplanetssoftware/apple_cloud_notes_parser
3. Apple Platform Security, "Secure features in the Notes app" — https://support.apple.com/guide/security/secure-features-in-the-notes-app-sec1782bcab1/web
4. ForensicArtifacts, macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
5. threeplanetssoftware, Apple Cloud Notes Parser, lib/AppleNoteStore.rb — https://raw.githubusercontent.com/threeplanetssoftware/apple_cloud_notes_parser/master/lib/AppleNoteStore.rb
