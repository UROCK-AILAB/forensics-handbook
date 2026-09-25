---
title: "LevelDB와 IndexedDB"
parent: "기반 · 데이터 저장 형식"
nav_order: 290
---

# LevelDB와 IndexedDB (LevelDB·IndexedDB)

LevelDB는 폴더 하나에 든 파일 묶음으로 키·값 데이터베이스 하나를 이루는 저장 형식이고, 새 변경은 `.log` 파일에 덧붙였다가 정렬 테이블(`.ldb`)로 옮기며 합치기(compaction)를 하기 전까지는 지우거나 덮어쓴 옛 값도 파일에 남을 수 있습니다. 크롬 같은 Chromium 계열 브라우저와 그 비슷한 앱은 IndexedDB·Local Storage·Session Storage를 LevelDB 위에 저장합니다 [4]. 이 페이지는 폴더 구성과 두 파일 형식, 지운 값이 남는 원리, Chromium 계열에서 IndexedDB를 읽는 법을 다룹니다.

## 이 형식을 쓰는 아티팩트

Chrome·Chromium 과 Electron 앱 같은 Chromium 기반 앱의 저장소는 ccl_chromium_reader 로 읽을 수 있고, 이 도구는 LevelDB 와 함께 IndexedDB, Web Storage(Local Storage·Session Storage)를 읽습니다 [4]. 크롬 프로필 폴더의 위치와 브라우저 기록 전반은 [크롬·엣지·웨일 (Chromium 계열)](../../02-artifacts/browsers/chromium/index.md)에서 다룹니다.

크롬 프로필의 `IndexedDB` 폴더 안에는 origin마다 `https_archive.org_0.indexeddb.leveldb` 처럼 "호스트의 구분 문자를 밑줄로 바꾼 이름_데이터베이스 번호.indexeddb.leveldb" 폴더가 있고, 값에 파일이 들어 있으면 `https_docs.google.com_0.indexeddb.blob` 처럼 같은 이름에 `.indexeddb.blob` 이 붙은 폴더가 함께 있습니다 [5]. Local Storage는 프로필 아래 `Local Storage\leveldb` 에, Session Storage는 `Session Storage` 에 있습니다. 이 경로는 Windows 기준이라서 [6] macOS 검체에서는 크롬 프로필 폴더 안에서 같은 이름의 폴더를 찾아 확인합니다. 사파리·파이어폭스의 IndexedDB는 [사파리 (Safari)](../../02-artifacts/browsers/safari/index.md)와 [파이어폭스 (Firefox)](../../02-artifacts/browsers/firefox.md)에서 따로 봅니다. 채팅 앱처럼 브라우저 엔진을 품은 앱이 macOS 어디에 LevelDB를 두는지도 앱마다 해당 페이지에서 확인합니다.

## 구조

### 폴더 구성

LevelDB 데이터베이스 하나는 폴더 하나 안의 파일 묶음입니다 [1].

| 파일 | 내용 [1] |
|---|---|
| `*.log` | 최근 변경을 차례로 덧붙이는 로그. 현재 로그의 내용은 메모리 테이블(memtable)에도 있음 |
| `*.ldb` | 정렬 테이블(sorted table). 키 순서로 정렬한 항목이고, 항목은 값이거나 삭제 표시(deletion marker) |
| `MANIFEST-번호` | 레벨마다 어떤 테이블이 있고 키 범위가 어디까지인지 적은 메타데이터. 로그 형식으로 씀 |
| `CURRENT` | 최신 MANIFEST 파일 이름이 든 텍스트 파일 |
| `LOG`, `LOG.old` | 정보 메시지(텍스트) |
| `LOCK`, `*.dbtmp` | 그 밖의 파일 |

`.log` 파일이 약 4MB(기본값)가 되면 정렬 테이블로 바뀌고 새 로그 파일이 생깁니다 [1]. 로그에서 만든 테이블은 level-0이고, level-0 파일이 4개를 넘으면 level-1과 합치며 level-1은 2MB마다 새 파일을 만듭니다 [1]. level-L(L≥1)의 합계가 10^L MB를 넘으면 다음 레벨로 합칩니다 [1]. 삭제 표시는 더 오래된 테이블에 있는 옛 값을 가리려고 남는 항목이고 [1], 합치기가 덮어쓴 옛 값을 버리며 겹치는 더 높은 레벨이 없으면 삭제 표시도 버립니다 [1].

데이터베이스를 다시 열 때마다 번호가 새로 붙은 MANIFEST가 생기고, 복구는 CURRENT를 읽고 → MANIFEST를 읽고 → 오래된 파일을 정리하고 → 로그 내용을 새 level-0 테이블로 옮기고 → 새 로그를 시작하는 순서로 진행합니다 [1]. 합치기나 복구가 끝날 때마다 현재 로그가 아닌 로그 파일과 어느 레벨에도 속하지 않는 테이블 파일을 지우고, 이 정리를 RemoveObsoleteFiles 라고 합니다 [1].

### `.log` 파일

`.log` 파일은 32KB(32768바이트) 블록이 이어진 모양이고, 파일 끝 블록만 덜 찰 수 있습니다 [2]. 블록 안에는 기록(record)이 이어지고, 기록마다 헤더가 7바이트입니다 [2].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | checksum. 유형과 데이터에 대한 crc32c, uint32 LE |
| 4 | 2 | length. 데이터 길이, uint16 LE |
| 6 | 1 | type |
| 7 | length | data |

| type | 뜻 [2] |
|---|---|
| 1 | FULL. 사용자 기록 하나가 통째로 들어 있음 |
| 2 | FIRST. 블록 경계에 걸린 사용자 기록의 첫 조각 |
| 3 | MIDDLE. 가운데 조각 |
| 4 | LAST. 마지막 조각 |

블록 끝에 6바이트 이하가 남으면 그 자리에서는 기록을 시작하지 않고 0으로 채우며(trailer), 정확히 7바이트가 남으면 데이터가 0바이트인 FIRST 기록을 씁니다 [2]. 로그 형식 자체에는 압축이 없고 [2], MANIFEST도 이 로그 형식으로 씁니다 [1].

### `.ldb` 테이블 파일

테이블 파일은 데이터 블록들, 메타 블록들, metaindex 블록, index 블록, Footer가 이 순서로 붙은 모양이고, Footer는 파일 끝에 있는 고정 길이 영역입니다 [3]. 블록의 위치는 BlockHandle로 가리키는데, BlockHandle은 offset(varint64)과 size(varint64) 두 값입니다 [3].

| Footer 안 순서 | 내용 [3] |
|---|---|
| 1 | metaindex_handle (BlockHandle) |
| 2 | index_handle (BlockHandle) |
| 3 | 두 핸들 뒤를 0으로 채워 여기까지 40바이트를 맞춤 |
| 4 | magic, fixed64 LE = `0xdb4775248b80fb57` |

Footer 전체는 40 + 8 = 48바이트입니다 [3]. 데이터 블록과 메타 블록은 선택적으로 압축하고 [3], ccl_chromium_reader는 Snappy 압축을 풀 수 있습니다 [4]. filter 메타 블록은 metaindex에 `filter.이름` 으로 등록하고 2KB 단위로 만듭니다 [3].

## 읽는 법

아래는 명세대로 만든 예시이고 실제 검체에서 나온 값이 아닙니다.

`.ldb` 파일은 끝에서부터 읽습니다.

```
파일 끝 -48 : [metaindex_handle][index_handle][00 00 ... 00]   합쳐서 40바이트
파일 끝  -8 : 57 FB 80 8B 24 75 47 DB                          magic 0xdb4775248b80fb57 (LE)
```

1. 파일 끝 8바이트가 `57 FB 80 8B 24 75 47 DB` 인지 봅니다. 맞으면 LevelDB 테이블 파일이고, 비할당 영역에서 찾은 조각이라면 이 8바이트가 조각의 끝입니다.
2. 끝에서 48바이트 앞부터 metaindex_handle과 index_handle을 차례로 읽습니다.
3. index_handle이 가리키는 index 블록을 읽어 데이터 블록 위치를 얻고, metaindex_handle로 filter 같은 메타 블록을 찾습니다.
4. 데이터 블록이 압축돼 있으면 풀고 나서 키·값 항목을 읽고, 항목이 값인지 삭제 표시인지를 함께 적습니다.

`.log` 파일은 32768바이트 블록 단위로 앞에서부터 읽습니다. 아래는 16바이트짜리 사용자 기록 하나가 FULL로 들어간 모양이고, `cc` 는 계산하지 않은 checksum 자리입니다.

```
00000000: cc cc cc cc 10 00 01 [데이터 16바이트 ...]
```

1. 앞 4바이트는 checksum, 다음 2바이트 `10 00` 은 리틀엔디언이라서 데이터 길이 16, 다음 1바이트 `01` 은 FULL입니다.
2. 헤더 7바이트 뒤 16바이트가 데이터이고, 그다음 바이트에서 다음 기록 헤더가 시작합니다.
3. type이 2(FIRST)이면 3(MIDDLE)과 4(LAST)가 나올 때까지 조각을 이어 붙여 사용자 기록 하나를 만듭니다.
4. 블록 끝에 6바이트 이하가 남아 0으로 채워져 있으면 다음 블록의 처음으로 건너뜁니다.

## 포렌식에서 중요한 점

### 지우거나 덮어쓴 값

LevelDB는 값을 지워도 그 자리를 바로 지우지 않고 삭제 표시를 새로 쓰며, 덮어쓴 옛 값과 삭제 표시는 합치기를 해야 버려집니다 [1]. 그래서 지우거나 덮어쓴 값이 합치기 전까지 `.log` 나 옛 `.ldb` 에 남아 있을 수 있습니다. ccl_chromium_reader의 LevelDB 모듈은 살아 있는 기록과 삭제된·옛 버전 기록을 가리지 않고 모두 내보내서 [4], 이 도구의 결과에는 지금은 없는 값도 섞여 나올 수 있습니다. 결과를 보고서에 옮길 때는 기록마다 삭제 표시인지, 같은 키의 더 새 기록이 있는지를 확인해 "지금 값" 과 "예전 값" 을 나눠 적습니다.

합치기나 복구가 끝나면 쓸모없어진 로그·테이블 파일을 지우니 [1], 그 파일들은 파일 시스템에서는 사라졌어도 비할당 영역에 남아 있을 수 있습니다. 테이블 파일은 끝 8바이트 magic으로, 로그 파일은 32KB 블록과 7바이트 기록 헤더 규칙으로 조각을 알아볼 수 있습니다. 일반 절차는 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)에 있습니다.

### 원본을 열면 바뀐다

데이터베이스를 여는 과정 자체가 복구 순서를 밟아 로그를 새 테이블로 옮기고 새 로그와 새 MANIFEST를 만들며 오래된 파일을 지웁니다 [1]. LevelDB 라이브러리로 원본 폴더를 그대로 열면 남아 있던 옛 로그와 옛 테이블이 사라질 수 있다는 뜻이라서, 폴더 전체를 사본으로 떠서 사본만 열고, 원본의 파일 목록과 크기·해시는 열기 전에 기록해 둡니다.

### 손상과 비정상 종료

`.log` 파일은 손상된 곳이 있으면 다음 블록 경계로 건너뛰어 읽을 수 있어서 [2], 앞 블록이 깨져도 뒤 블록의 기록은 살릴 수 있습니다. 현재 로그의 내용은 메모리 테이블에도 있지만 [1], 디스크에서는 아직 테이블로 옮기지 않은 최근 변경이 `.log` 에만 있습니다. 앱이 비정상 종료된 검체라면 마지막 변경은 `.log` 에서 찾고, 복구 순서가 `CURRENT` 와 MANIFEST부터 읽으니 [1] 폴더의 파일을 하나도 빠뜨리지 않고 확보합니다.

### 시각이 없다

테이블 형식에는 기록 시각 칸이 없습니다 [3]. 기록 사이의 앞뒤는 LevelDB 순번(sequence number)으로 따질 수 있지만 순번은 시각이 아닙니다. Local Storage 기록은 LevelDB 순번으로 "batch" 와 연결하면 5~60초 안의 대략적인 시각을 얻을 수 있습니다 [4]. 이 시각은 LevelDB가 아니라 Local Storage가 `META:` 키의 protobuf 값에 적어 두는 batch 기록 시각입니다. 크롬은 기록마다 5초를 기다렸다 쓰고 호스트마다 한 시간에 60번까지만 쓰기 때문에, 스크립트가 값을 저장한 때와 데이터베이스에 들어간 때가 5~60초 벌어질 수 있습니다 [6]. 이런 시각은 대략값이라고 밝혀 쓰고, 파일 시스템 시각이나 브라우저 기록처럼 다른 시각과 맞춰 봅니다. 여러 시각을 한 시간축에 놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)에서 다룹니다.

### Chromium 계열의 IndexedDB·Web Storage

IndexedDB 한 인스턴스 안에는 데이터베이스가 여러 개 있고, 데이터베이스마다 object store가 여러 개 있으며 object store 번호는 1부터 셉니다 [4]. 데이터베이스는 번호가 아니라 이름과 origin으로 찾는 편이 낫고, origin은 `file__0@1` 처럼 적습니다 [4]. 값은 V8 직렬화와 Blink 직렬화를 거쳐 저장되고, Blink 호스트 객체 일부는 ccl_chromium_reader가 아직 해석하지 못할 수 있습니다 [4]. 기록 값에 FileInfo가 있으면 파일 데이터는 `.blob` 폴더에 따로 있어서 ccl_chromium_reader는 그 파일을 따라가 읽으니 [4], IndexedDB를 확보할 때는 `.leveldb` 폴더와 `.blob` 폴더를 함께 가져옵니다. Session Storage는 호스트별로 기록을 읽고 기록마다 LevelDB 순번을 함께 줍니다 [4].

## 함정

- **파일 개수와 기록 개수**: 같은 키가 여러 파일에 여러 번 나올 수 있어서 모든 파일의 항목 수를 더한 값은 살아 있는 기록 수가 아닙니다. 삭제 표시와 순번을 보고 키마다 최신 값을 가려야 합니다.
- **압축된 블록**: `.ldb` 데이터 블록은 압축돼 있을 수 있어서 [3], 원본 파일에 문자열 검색을 해도 값이 나오지 않을 수 있습니다. 압축되지 않는 `.log` [2]와 달리, 테이블 파일은 블록을 풀고 나서 검색합니다.
- **직렬화된 값**: IndexedDB 값은 V8·Blink 직렬화 형식이라서 [4] 문자열 검색만으로는 필드 경계를 알 수 없고, 해석하지 못한 호스트 객체가 결과에서 빠질 수 있습니다.
- **도구의 설계 전제**: ccl_chrome_audit.py는 주로 Windows에서, 데이터가 만들어진 그 PC에서 쓰도록 설계됐고 쿠키 복호에 DPAPI를 씁니다 [4]. 맥 검체에 쓸 때는 어느 기능이 이 전제에 기대는지 먼저 확인합니다.

## 도구

ccl_chromium_reader는 Chromium 계열 저장소를 읽는 Python 패키지이고, Snappy, LevelDB, Protobuf, Pickle, V8·Blink 객체 역직렬화, IndexedDB, Local Storage·Session Storage, Cache, SNSS 세션(일부), FileSystem API, Notifications, Downloads, History를 지원 목록에 둡니다 [4]. 대부분 결과에 오프셋과 ID를 함께 내주니 [4], 몇 개를 골라 원본 파일의 같은 자리를 헥스로 열어 위 읽는 법대로 맞춰 봅니다. 형식의 기준은 Google의 LevelDB 설계 문서 세 편 [1][2][3]이고, 도구를 검증하는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)을 따릅니다.

## 참고 문헌

1. Google, LevelDB `doc/impl.md` — https://raw.githubusercontent.com/google/leveldb/main/doc/impl.md
2. Google, LevelDB `doc/log_format.md` — https://raw.githubusercontent.com/google/leveldb/main/doc/log_format.md
3. Google, LevelDB `doc/table_format.md` — https://raw.githubusercontent.com/google/leveldb/main/doc/table_format.md
4. CCL, ccl_chromium_reader 저장소 README — https://github.com/cclgroupltd/ccl_chromium_reader
5. CCL Solutions Group, "IndexedDB on Chromium" — https://www.cclsolutionsgroup.com/post/indexeddb-on-chromium
6. CCL Solutions Group, "Chromium Session Storage and Local Storage" — https://www.cclsolutionsgroup.com/post/chromium-session-storage-and-local-storage
