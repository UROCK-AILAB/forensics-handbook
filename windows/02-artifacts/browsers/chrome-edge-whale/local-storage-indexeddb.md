---
title: "웹 저장소 (Local Storage·IndexedDB)"
parent: "크롬 계열 브라우저"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1650
---

# 웹 저장소 (Local Storage·IndexedDB)

## 한 줄 요약

웹 저장소는 웹 사이트의 스크립트가 브라우저 안에 넣어 둔 데이터입니다. 크롬 계열 브라우저는 로컬 스토리지 (Local Storage), 세션 스토리지 (Session Storage), IndexedDB 를 프로필 폴더 안의 LevelDB 데이터베이스에 저장합니다. 이 데이터로 어느 사이트가 이 프로필에서 스크립트를 돌렸는지, 그 사이트가 무엇을 남겼는지 알 수 있습니다. 지운 값도 한동안 파일 안에 남습니다.

## 무엇을 기록하나 · 왜 생기나

브라우저가 스스로 적는 기록이 아니라 사이트의 스크립트가 필요해서 저장한 값이라서, 무엇이 들어 있는지는 사이트마다 다릅니다.

- **로컬 스토리지**는 출처 (Origin) 마다 문자열 키와 값을 저장하며 창을 닫아도 남습니다. 사이트 설정, 최근 본 항목, 방문자 식별자 같은 값이 흔히 들어 있습니다.
- **세션 스토리지**는 탭 하나에 묶인 키와 값이지만, 이름과 달리 디스크의 `Session Storage` 폴더에도 저장됩니다.
- **IndexedDB** 는 사이트가 쓰는 데이터베이스로 객체, 배열, 파일(blob)까지 저장합니다. 웹 메일, 웹 메신저, 문서 편집기가 오프라인용 자료를 여기에 두는 경우가 많습니다.

Teams·Discord·Slack 같은 Electron 앱과 WebView2 앱도 같은 코드를 써서 같은 구조의 폴더가 앱 데이터 폴더 안에 생기며, 위치는 [Electron·WebView2 앱 데이터 위치](../../../01-foundations/app-mail-data/chromium-electron-webview2/teams-discord-slack.md)에서 다룹니다.

## 위치와 버전별 차이

아래 경로는 프로필 폴더 기준입니다. 버킷 (Storage Bucket) 은 Chromium 이 한 사이트의 저장소를 묶어 관리하는 단위입니다. 브라우저별 프로필 폴더 위치는 [프로필 폴더와 계열 브라우저 구분](../../../01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md)에서 다룹니다.

| 저장소 | 위치 | 형식 | 특징 |
|---|---|---|---|
| 로컬 스토리지 | `Local Storage\leveldb\` | LevelDB | 모든 사이트가 DB 하나를 같이 씁니다 |
| 세션 스토리지 | `Session Storage\` | LevelDB | 모든 탭이 DB 하나를 같이 씁니다 |
| IndexedDB (직접 연 사이트의 기본 버킷) | `IndexedDB\https_www.example.com_0.indexeddb.leveldb\` | LevelDB | 사이트마다 폴더가 따로 있습니다 |
| IndexedDB 파일(blob) | `IndexedDB\https_www.example.com_0.indexeddb.blob\` | 일반 파일 | 큰 값과 파일은 여기에 따로 둡니다 |
| 분할 저장·추가 버킷의 IndexedDB | `WebStorage\<버킷 번호>\IndexedDB\indexeddb.leveldb\` | LevelDB | 아래 "분할 저장" 을 봅니다 |
| 버킷 목록 | `WebStorage\QuotaManager` | SQLite | `buckets` 표에 버킷 번호와 저장 키가 있습니다 |
| SQLite 방식 DOM 저장소 | `LocalStorage\` · `SessionStorage\` | SQLite | 아래 "SQLite 로 옮기는 중" 을 봅니다 |

위 폴더 이름과 파일 이름은 Chromium 소스로 확인했습니다. 크롬, 엣지, 웨일은 모두 Chromium 코드를 씁니다. 다만 브라우저마다 따르는 Chromium 버전이 다르므로 아래 변화가 들어온 시점도 다를 수 있습니다.

### 분할 저장 (Storage Partitioning)

Chrome 115 부터 모든 사용자에게 분할 저장이 켜졌습니다(Google Privacy Sandbox 문서). 분할 저장을 켜면 다른 사이트 안에 끼워 넣은 프레임(iframe)의 저장소가 최상위 사이트별로 나뉩니다. 로컬 스토리지, 세션 스토리지, IndexedDB 가 모두 대상입니다.

- 로컬 스토리지에서는 저장 키 (Storage Key) 에 최상위 사이트가 붙습니다. 모양은 아래 구조 절에서 다룹니다.
- IndexedDB 에서는 직접 연 사이트(퍼스트 파티, First-party)의 기본 버킷만 옛 위치(`IndexedDB\`)를 씁니다. Chromium 소스 주석은 제3자 IndexedDB 를 `WebStorage\<버킷 번호>\IndexedDB\` 에 둔다고 적습니다.
- 버킷 번호가 어느 사이트인지는 `WebStorage\QuotaManager` 의 `buckets` 표에서 찾습니다. 이 표에는 `id`·`storage_key`·`host`·`name`·`use_count`·`last_accessed`·`last_modified` 열이 있습니다.

### SQLite 로 옮기는 중

Chromium 소스에는 로컬 스토리지와 세션 스토리지를 SQLite 에 저장하는 코드가 있습니다. SQLite 방식의 폴더 이름은 `LocalStorage`·`SessionStorage` 로, 띄어쓰기가 없습니다. 2026년 9월의 Chromium 소스에서는 이 기능의 기본값이 꺼져 있습니다. 단계적으로 켜는 설정(새 DB 만 SQLite, 모두 SQLite 등)이 소스에 있습니다. IndexedDB 에도 SQLite 저장 코드가 있습니다.

그래서 검체에서는 LevelDB 폴더와 SQLite 폴더를 모두 확인합니다. SQLite 파일 해석은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md)를 봅니다.

## 구조

LevelDB 의 파일 구성(`.log`·`.ldb`·`MANIFEST-*`·`CURRENT`), 순서 번호 (Sequence Number), 압축 정리 (Compaction) 는 [LevelDB 저장소](../../../01-foundations/database-log-formats/leveldb.md)에서 다룹니다. 이 페이지에서 알아야 할 점은 세 가지입니다.

- 레코드마다 순서 번호와 상태(살아 있음·지움)가 붙습니다.
- 같은 키의 레코드가 여러 개 남을 수 있습니다. 살아 있으면서 순서 번호가 가장 큰 레코드가 현재 값입니다.
- `.ldb` 파일의 데이터는 Snappy 로 압축될 수 있습니다.

### 로컬 스토리지

DB 하나에 모든 사이트의 값이 들어 있습니다. 키의 첫 글자로 레코드 종류를 나눕니다.

| 키 | 값 |
|---|---|
| `_` + 저장 키 + `00` + 스크립트 키 | 사이트가 저장한 값 |
| `META:` + 저장 키 | `LocalStorageAreaWriteMetaData`: `last_modified`(필드 1), `size_bytes`(필드 2) |
| `METAACCESS:` + 저장 키 | `LocalStorageAreaAccessMetaData`: `last_accessed`(필드 1) |

`META:` 와 `METAACCESS:` 의 값은 프로토콜 버퍼 (Protocol Buffers) 로 인코딩됩니다. 스크립트 키와 값은 첫 1바이트가 문자 인코딩을 가리키는데, `00` 은 UTF-16LE 이고 `01` 은 한 바이트 문자(Latin-1 계열)입니다. CCL 의 공개 파서 소스는 `META:` 만 설명하므로 `METAACCESS:` 는 그 뒤 Chromium 에 들어온 것으로 보이며, 옛 버전 검체에는 없을 수 있습니다.

저장 키의 모양은 맥락에 따라 다릅니다(Chromium `StorageKey` 소스).

| 맥락 | 저장 키 예 |
|---|---|
| 사이트를 직접 연 경우 (퍼스트 파티) | `https://www.example.com` (끝에 `/` 가 없습니다) |
| 다른 사이트 안에 끼워 넣은 경우 (제3자) | `https://widget.example.net/^0https://news.example.com` |

`^0` 뒤는 최상위 사이트입니다. 그래서 제3자 저장 키에서 "어느 사이트 안에서 이 프레임이 열렸는지" 를 읽을 수 있습니다. 문자 인코딩 일반은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)을 봅니다.

### 세션 스토리지

Chromium 소스 주석에 따른 키 모양입니다.

| 키 | 값 |
|---|---|
| `namespace-` + 세션 GUID + `-` + 저장 키 | 맵 번호 |
| `map-` + 맵 번호 + `-` + 스크립트 키 | 사이트가 저장한 값 |

세션 GUID 는 탭 하나를 가리킵니다. 같은 사이트라도 탭마다 맵이 따로 생길 수 있습니다.

### IndexedDB

사이트마다 LevelDB 폴더가 따로 있습니다. 아래는 CCL 의 분석 글을 따른 요약입니다.

- **키 앞머리**: 모든 키가 데이터베이스 번호, 객체 저장소 번호, 인덱스 번호로 시작합니다. 첫 1바이트가 세 번호의 길이를 적습니다. 번호가 모두 256 미만이면 이 바이트가 `00` 이고 앞머리는 4바이트입니다.
- **전체 메타데이터**: 앞머리가 `00 00 00 00` 인 레코드입니다. 종류 `C9`(201) 레코드에 출처와 데이터베이스 이름이 있고, 값이 데이터베이스 번호입니다.
- **인덱스 번호 1·2·3**: 1 은 기본 키로 찾는 실제 레코드입니다. 2 는 버전 표시("exists") 레코드입니다. 3 은 외부 파일(blob) 목록입니다.
- **값**: 저장소 버전 varint, `FF` + Blink 버전, `FF` + V8 버전이 앞에 옵니다. 그 뒤는 V8 의 구조화 복제 (Structured Clone) 직렬화 형식입니다.
- **blob 파일**: `.indexeddb.blob` 폴더 아래 `데이터베이스 번호\앞자리 16진\blob 번호 16진` 경로에 있습니다. CCL 의 예에서 데이터베이스 1 의 blob 270 은 `1/01/10E` 입니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 프로필에서 그 출처의 스크립트가 저장소에 값을 썼습니다 | 사용자가 그 사이트를 일부러 열었는지 (광고·위젯 프레임도 값을 씁니다) |
| 제3자 저장 키가 있으면 그 프레임이 어느 최상위 사이트 안에서 열렸는지 | 사용자가 화면에서 그 내용을 봤는지 |
| 값의 내용 (계정 식별자, 앱 설정, 캐시한 메시지 등) | 값이 사이트가 쓴 그대로인지 (개발자 도구로 고칠 수 있습니다) |
| 지운 레코드가 남아 있으면 예전 값 | 레코드 하나하나를 쓴 시각 (레코드에는 시각이 없습니다) |
| | 방문 횟수와 방문 시각 전체 |

### 보고서 문장

아래 출처와 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 의 크롬 기본 프로필 로컬 스토리지에 `https://mail.example.com` 출처의 키 12개가 있습니다. 이 출처의 `META:` 레코드의 마지막 기록 시각은 2025-03-14 01:23:45 UTC 입니다."
- 쓰면 안 되는 문장: "사용자 A 는 2025-03-14 01:23 에 웹 메일에 로그인해 메일을 읽었습니다."

## 시각 해석

LevelDB 레코드에는 시각이 없어 순서 번호로 앞뒤만 알 수 있고, 시각은 아래 자리에서 얻습니다.

| 시각 | 자리 | 무엇이 바뀔 때 바뀌나 | 형식 |
|---|---|---|---|
| `last_modified` | 로컬 스토리지 `META:` 값 | 그 저장 키의 저장소를 디스크에 쓸 때 | 1601-01-01 UTC 부터 센 마이크로초 |
| `last_accessed` | 로컬 스토리지 `METAACCESS:` 값 | 페이지가 그 저장소에 연결될 때 한 번 | 같음 |
| 파일 수정 시각 | IndexedDB 외부 파일 목록 | blob 파일의 수정 시각 | 1601-01-01 UTC 부터 센 마이크로초 (CCL) |
| `last_accessed`·`last_modified` | `WebStorage\QuotaManager` 의 `buckets` 표 | 버킷 단위 사용·수정 | 정수. 이 글에서는 단위를 소스로 확인하지 못했습니다. 검체에서 다른 시각과 맞춰 봅니다 |
| 앱이 넣은 시각 | 값 안 | 사이트가 정합니다 | 사이트마다 다릅니다. JavaScript `Date` 는 1970-01-01 UTC 부터 센 밀리초입니다 |
| 파일 시스템 시각 | `.log`·`.ldb` 파일 | 파일이 생기거나 쓰일 때 | NTFS 시각 |

`META:` 값의 시각은 `base::Time::ToInternalValue()` 로 저장하고(Chromium 소스 주석), CCL 파서는 이 값을 1601년 기준 마이크로초로 풉니다. 이 형식은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)의 WebKit 시각과 같습니다.

`last_modified` 는 저장 키 하나에 하나뿐이라서 그 사이트의 마지막 쓰기만 남고 이전 시각은 덮어씁니다. 이전 `META:` 레코드가 지운 레코드로 남아 있으면 예전 시각도 볼 수 있습니다.

CCL 의 파서는 `META:` 레코드와 순서 번호가 이어지는 값 레코드를 한 번의 쓰기로 묶어 값 레코드에 대략의 시각을 붙이는데, 이 방법은 추정이므로 보고서에는 추정이라고 밝힙니다.

모든 시각은 UTC 입니다. 현지 시각 변환은 [시간대·시계 오차 보정](../../../03-techniques/analysis/timeline/time-normalization.md)을 봅니다.

## 함정과 한계

1. **현재 값만 봅니다.** LevelDB 는 값을 덮어쓰지 않고 새 레코드를 더합니다. 지운 레코드와 예전 값이 압축 정리 전까지 남습니다. 도구가 살아 있는 값만 보여 주는지, 지운 레코드도 보여 주는지 확인합니다.
2. **살아 있는 레코드를 모두 현재 값으로 봅니다.** 같은 키에 살아 있는 레코드가 여러 개 있을 수 있습니다. 순서 번호가 가장 큰 것만 현재 값입니다.
3. **원본 폴더를 LevelDB 라이브러리로 엽니다.** 라이브러리는 열 때 `.log` 를 새 `.ldb` 로 옮기고 압축 정리를 할 수 있습니다. 그러면 지운 레코드가 사라집니다. 항상 사본에서 작업합니다.
4. **문자열 검색만 합니다.** `.ldb` 의 데이터는 Snappy 로 압축될 수 있습니다. 압축된 블록 안의 글자는 검색에 걸리지 않습니다. UTF-16LE 로 저장된 값도 한 바이트 문자 검색에 걸리지 않습니다.
5. **출처가 있으면 방문했다고 봅니다.** 광고, 분석 스크립트, 위젯 프레임도 저장소에 씁니다. 방문 여부는 [방문·다운로드 기록](history.md)과 맞춰 봅니다.
6. **`IndexedDB\` 폴더만 봅니다.** 분할 저장 이후 제3자와 추가 버킷의 IndexedDB 는 `WebStorage\` 아래에 있습니다. SQLite 방식이 켜진 브라우저는 `LocalStorage\`·`SessionStorage\` 에 씁니다.
7. **세션 스토리지는 디스크에 없다고 봅니다.** 크롬 계열은 세션 스토리지도 `Session Storage\` 폴더에 씁니다.
8. **값을 사이트가 쓴 그대로라고 봅니다.** 사용자는 개발자 도구에서 로컬 스토리지 값을 고치거나 지울 수 있습니다. 확장 프로그램도 페이지 스크립트로 값을 바꿀 수 있습니다.

### 지우기와 조작

- **사이트 데이터 삭제**: 로컬 스토리지는 모든 사이트가 DB 하나를 같이 씁니다. LevelDB 는 지울 때 지움 레코드를 더하므로, 압축 정리 전까지 예전 레코드를 찾을 수 있습니다. 압축 정리가 언제 도는지는 미리 알 수 없습니다.
- **폴더 삭제**: IndexedDB 는 사이트마다 폴더가 따로 있어서 폴더째 지워질 수 있습니다. 이때는 [$MFT](../../filesystem/mft.md), [$UsnJrnl](../../filesystem/usnjrnl.md), [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md), [레코드 카빙](../../../03-techniques/analysis/data-recovery/record-carving.md)으로 찾습니다.
- **시크릿 창**: 시크릿 창에서 쓴 웹 저장소는 이 폴더들에 남지 않습니다. 흐름은 [시크릿 모드로 무엇을 했나](../../../04-scenarios/activity/private-browsing.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번 — 로컬 스토리지 레코드 읽기

아래는 Chromium 소스와 CCL 자료의 형식 설명으로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. `.log` 파일에서는 레코드가 LevelDB 쓰기 묶음 (WriteBatch) 안에 길이 값과 함께 들어 있습니다. 그 겉포장은 [LevelDB 저장소](../../../01-foundations/database-log-formats/leveldb.md)를 봅니다. 여기서는 키와 값만 떼어 봅니다.

**값 레코드**

```
키 (31바이트)
0x00  5F 68 74 74 70 73 3A 2F 2F 77 77 77 2E 65 78 61   _https://www.exa
0x10  6D 70 6C 65 2E 63 6F 6D 00 01 74 68 65 6D 65      mple.com..theme
값 (5바이트)
0x00  01 64 61 72 6B                                     .dark
```

1. 첫 바이트 `5F` 는 `_` 입니다. 사이트가 저장한 값 레코드입니다.
2. `00` 앞까지가 저장 키 `https://www.example.com` 입니다. 끝에 `/` 가 없으므로 직접 연 사이트의 저장 키입니다.
3. `00` 뒤의 `01` 은 스크립트 키가 한 바이트 문자라는 뜻입니다. 스크립트 키는 `theme` 입니다.
4. 값의 첫 바이트 `01` 도 한 바이트 문자라는 뜻입니다. 값은 `dark` 입니다. `00` 이었다면 뒤를 UTF-16LE 로 읽습니다.

**`META:` 레코드**

```
키 (28바이트)  "META:https://www.example.com"
값 (11바이트)
0x00  08 C0 94 A4 95 99 DB E3 17 10 12
```

1. `08` 은 프로토콜 버퍼의 필드 1, varint 형식입니다. `last_modified` 입니다.
2. 이어지는 `C0 94 A4 95 99 DB E3 17` 은 varint 입니다. 각 바이트의 아래 7비트를 뒤쪽이 높은 자리가 되게 이어 붙입니다. 결과는 13,386,389,025,000,000 입니다.
3. 이 수는 1601-01-01 UTC 부터 센 마이크로초입니다. 초로 바꾸면 13,386,389,025 초입니다. 여기서 11,644,473,600 초(1601년부터 1970년까지)를 빼면 Unix 시각 1,741,915,425 입니다. 이는 2025-03-14 01:23:45 UTC 입니다.
4. `10` 은 필드 2, varint 형식입니다. `size_bytes` 입니다. `12` 는 18 입니다.

**`.ldb` 안 키 끝의 8바이트**

`.ldb` 파일에서는 키 끝에 8바이트가 더 붙습니다. 리틀 엔디언 64비트 정수로 읽습니다. 가장 낮은 바이트가 상태이고, 나머지 7바이트가 순서 번호입니다(CCL).

```
01 2A 00 00 00 00 00 00
```

첫 바이트 `01` 은 살아 있는 레코드입니다(`00` 이면 지운 레코드). 나머지는 순서 번호 0x2A(42)입니다.

> 그림 자리: 로컬 스토리지 값 레코드의 키를 `_`·저장 키·`00`·인코딩 바이트·스크립트 키로 색을 나누고, 같은 저장 키의 `META:` 레코드와 선으로 잇는 그림

### 공개 도구로 한 번

CCL 이 공개한 파이썬 라이브러리 `ccl_chromium_reader` 로 로컬 스토리지, 세션 스토리지, IndexedDB 를 읽을 수 있습니다. 로컬 스토리지 모듈 소스는 지운 레코드도 읽어 순서 번호로 쓰기 묶음을 만듭니다. 소스 주석은 `META:` 시각을 살아 있는 레코드에서만 쓴다고 적습니다. 도구가 무엇이든 다음을 확인합니다.

- 결과에 순서 번호와 상태(살아 있음·지움)가 나오는지 봅니다.
- `WebStorage\` 아래 버킷과 SQLite 폴더도 읽는지 봅니다.
- IndexedDB 값의 V8 직렬화를 풀지 못하면 원시 바이트로 남기는지 봅니다.
- 값 한두 개는 위 헥스 풀이와 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [방문·다운로드 기록 (History)](history.md) | 그 출처를 실제로 방문한 시각. `META:` 시각과 가까운지 |
| [쿠키 (Cookies)](cookies.md) | 같은 사이트의 쿠키와 그 생성·마지막 접근 시각 |
| [캐시 (Cache)](cache.md) | 같은 사이트에서 받은 스크립트와 응답 |
| [세션·탭 복원 (Sessions)](sessions.md) | 세션 스토리지가 속한 탭과 그 탭의 주소 |
| [확장 프로그램 (Extensions)](extensions.md) | 값을 바꿀 수 있는 확장 프로그램이 있었는지 |
| [Electron·WebView2 앱 데이터 위치](../../../01-foundations/app-mail-data/chromium-electron-webview2/teams-discord-slack.md) | 같은 구조로 남은 앱 데이터 ([팀즈](../../messengers/teams.md)·[디스코드](../../messengers/discord.md)·[슬랙](../../messengers/slack.md)) |
| [$MFT](../../filesystem/mft.md) · [$UsnJrnl](../../filesystem/usnjrnl.md) | `.log`·`.ldb` 파일과 IndexedDB 폴더가 생기고 지워진 시각 |
| [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 예전 시점의 LevelDB 폴더 |

웹 사용 전체 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md)에서 다룹니다.

## 실습

**공개 검체** — NIST CFReDS 등에서 크롬이나 엣지가 설치된 Windows 이미지를 하나 고릅니다.

1. 프로필 폴더에 `Local Storage\leveldb\`, `IndexedDB\`, `WebStorage\`, `LocalStorage\` 중 무엇이 있습니까? 이것으로 브라우저 버전대를 짐작해 보십시오.
2. 로컬 스토리지의 저장 키를 모두 뽑으십시오. `^0` 이 붙은 제3자 저장 키가 있습니까? 최상위 사이트는 어디입니까?
3. `META:` 레코드 하나의 `last_modified` 를 직접 풀어 보십시오. 방문 기록의 같은 사이트 방문 시각과 얼마나 차이가 납니까?
4. 같은 키에 레코드가 여러 개 있습니까? 지운 레코드에 남은 예전 값은 무엇입니까?
5. `.ldb` 파일에서 아는 값으로 문자열 검색을 해 보십시오. 도구로 푼 결과와 건수가 같습니까?

**직접 만든 Windows 10·11 가상 머신**에서도 해 봅니다.

1. 로컬 스토리지를 쓰는 사이트를 열고 시각을 적어 둡니다. 프로필 폴더 사본을 떠서 `META:`·`METAACCESS:` 시각과 비교합니다.
2. 개발자 도구로 값 하나를 고치고 다시 사본을 뜹니다. 같은 키의 레코드가 몇 개 남는지 봅니다.
3. 그 사이트의 데이터를 지우고 다시 사본을 뜹니다. 예전 레코드가 남아 있는지, 브라우저를 여러 번 다시 켠 뒤에도 남는지 봅니다.

## 참고 문헌

- CCL Solutions Group, "Hang on! That's not SQLite! Chrome, Electron, and LevelDB" — https://www.cclsolutionsgroup.com/post/hang-on-thats-not-sqlite-chrome-electron-and-leveldb
- CCL Solutions Group, "IndexedDB on Chromium" — https://www.cclsolutionsgroup.com/post/indexeddb-on-chromium
- CCL Solutions Group, `ccl_chromium_reader` 소스 `ccl_chromium_localstorage.py` — https://github.com/cclgroupltd/ccl_chromium_reader/blob/master/ccl_chromium_reader/ccl_chromium_localstorage.py
- Chromium 소스 (2026년 9월 main 브랜치)
  - `local_storage_database.proto` — https://github.com/chromium/chromium/blob/main/components/services/storage/dom_storage/leveldb/local_storage_database.proto
  - `local_storage_leveldb.cc` — https://github.com/chromium/chromium/blob/main/components/services/storage/dom_storage/leveldb/local_storage_leveldb.cc
  - `dom_storage_database.cc`·`features.cc` — https://github.com/chromium/chromium/tree/main/components/services/storage/dom_storage
  - `indexed_db_context_impl.cc`·`file_path_util.cc` — https://github.com/chromium/chromium/tree/main/content/browser/indexed_db
  - `storage_key.cc` — https://github.com/chromium/chromium/blob/main/third_party/blink/common/storage_key/storage_key.cc
  - `quota_database.cc`·`quota_database.h` — https://github.com/chromium/chromium/tree/main/storage/browser/quota
- Google Privacy Sandbox, "Storage partitioning" — https://privacysandbox.google.com/3pcd/storage-partitioning
