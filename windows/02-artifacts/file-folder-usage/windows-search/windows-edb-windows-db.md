---
title: "위치와 형식"
parent: "윈도 검색 색인 DB"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1270
---

# 위치와 형식 (Windows.edb·Windows.db)

> 위치: [윈도 검색 색인 DB (Windows Search)](index.md) > 위치와 형식

## 한 줄 요약

윈도 검색 색인 DB 는 한 폴더에 모여 있습니다. Windows 10 까지는 ESE 형식의 `Windows.edb` 가 본 DB 이고, Windows 11 은 SQLite 형식의 `Windows.db` 와 `Windows-gather.db` 로 나뉩니다. 이 페이지는 폴더 위치, 함께 모을 파일, 표 목록, 바이트 순서, 그리고 Windows 11 PC 한 대에서 본 `AesGcm1 SQLite3` 헤더를 다룹니다.

## 무엇을 기록하나 · 왜 생기나

윈도 검색이 쓰는 색인의 이름은 SystemIndex 이고, 속성 저장소 (Property Store), 속성과 본문을 담은 색인, 글자로 찾는 데 쓰는 역색인 (Inverted Index) 세 부분으로 이루어집니다. DB 파일 안의 표 이름은 Windows 버전마다 다릅니다.

파일마다 남는 속성은 [파일 속성 되살리기](propertystore.md) 에서, 수집기가 남기는 기록은 [수집 기록](systemindex-gthr.md) 에서 다룹니다.

## 위치와 버전별 차이

### 폴더

| 항목 | 값 | 근거 |
|---|---|---|
| 기본 폴더 (Vista 이후) | `C:\ProgramData\Microsoft\Search\Data\Applications\Windows\` | libyal |
| 기본 폴더 (XP) | `C:\Documents and Settings\All Users\Application Data\Microsoft\Search\Data\Applications\Windows\` | libyal |
| 폴더를 정하는 값 | `HKLM\Software\Microsoft\Windows Search` 키의 `DataDirectory` 값 | libyal |

폴더는 `DataDirectory` 값이 정하므로, 수집할 때는 SOFTWARE 하이브에서 이 값을 먼저 읽습니다. 한 PC 에서 이 값은 `REG_EXPAND_SZ` 형식의 `%ProgramData%\Microsoft\Search\Data\` 였고, DB 파일은 그 아래 `Applications\Windows\` 에 있었습니다. 같은 키의 `SetupCompletedSuccessfully` 값은 그 PC 에서 1 이었지만, 이 값의 뜻을 설명한 자료는 확인하지 못했습니다.

하이브를 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

### Windows 버전별 본 DB

| Windows | 본 DB | 형식 | 근거 |
|---|---|---|---|
| XP~8 | `Windows.edb` | ESE | libyal |
| 10 | `C:\ProgramData\Microsoft\Search\Data\Applications\Windows\Windows.edb` | ESE | LevelBlue |
| 11 | `Windows.db`, `Windows-gather.db`, `Windows-usn.db` | SQLite | LevelBlue |
| 11 25H2 (PC 한 대) | 위와 같은 세 파일 | 첫 16바이트가 `AesGcm1 SQLite3`. 보통 SQLite 도구로 열리지 않았습니다. | 관찰 |

- LevelBlue 글은 `Windows-usn.db` 의 포렌식 가치가 낮다고 적습니다.
- libyal 문서는 Windows 10·11 과 `Windows.db` 를 다루지 않습니다. 그래서 Windows 10 이후 칸 구성과 바이트 순서는 검체에서 직접 확인합니다.
- `AesGcm1 SQLite3` 형식이 어느 빌드부터 쓰였는지는 확인한 자료가 없습니다.

## 구조

### ESE 판 폴더의 파일

libyal 문서(XP~8 기준)가 적은 파일입니다.

| 파일 | 하는 일 |
|---|---|
| `Windows.edb` | 본 DB |
| `MSS.chk` | 체크포인트 파일 |
| `MSS#####.log` | 트랜잭션 로그 |
| `MSSres00001.jrs`, `MSSres00002.jrs` | 예약 로그 |
| `tmp.edb` | 색인을 합칠 (merge) 때 쓰는 임시 DB |

- Windows 10 이후의 윈도 검색은 트랜잭션 로그를 `.jtx`, 체크포인트를 `.jcp` 확장자로 씁니다. 예전 확장자는 `.log`·`.chk` 였습니다. (현장 관찰)
- 로그로 복구할 때는 이 이름 규칙을 맞춰야 도구가 로그를 찾습니다. (현장 관찰)
- 트랜잭션 로그와 체크포인트의 역할은 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다.

### SQLite 판 폴더의 파일

아래는 Windows 11 25H2 PC 한 대의 `Applications\Windows\` 폴더에서 본 파일입니다.

| 파일·폴더 | 내용 |
|---|---|
| `Windows.db`, `Windows.db-wal`, `Windows.db-shm` | 파일 속성 DB 와 그 `-wal`·`-shm` 파일 |
| `Windows-gather.db`, `Windows-gather.db-wal`, `Windows-gather.db-shm` | 수집 기록 DB 와 그 `-wal`·`-shm` 파일 |
| `Windows-usn.db`, `Windows-usn.db-wal`, `Windows-usn.db-shm` | 세 번째 DB 와 그 `-wal`·`-shm` 파일 |
| `GatherLogs\SystemIndex\` | 수집 로그 폴더. [수집 기록](systemindex-gthr.md) 에서 다룹니다. |
| `Projects\SystemIndex\PropMap\PropMap.db` | 첫 16바이트가 `AesGcm1 SQLite3` 였습니다 |
| `Projects\SystemIndex\SecStore\SecStore.db` | 첫 16바이트가 `AesGcm1 SQLite3` 였습니다 |

- `-wal` 파일에는 아직 본 DB 에 쓰지 않은 변경이 들어 있습니다. 그래서 `.db` 와 함께 `-wal`·`-shm` 도 모읍니다.
- WAL 파일의 헤더와 지운 파일 흔적은 [지운 파일·옛 파일 흔적 찾기](deleted-file-traces.md) 에서 다룹니다.

### 표 목록 — ESE 판 (libyal, XP~8)

| 표 | 내용 |
|---|---|
| `__NameTable__` | 칸: Version, MaxDocId, MaxSubId, CurrentMaster, DocCount, StatusFlags, AppCatName, BaseTableName |
| `SystemIndex_0A` | XP·Vista·7 의 본 색인 표입니다. 칸이 300개가 넘습니다. |
| `SystemIndex_0P` | `SystemIndex_0A` 의 칸 정보입니다. 칸: PID, ColumnID, Type, MaxSize, Fixed, Sparse, Compress, JetCompress, Name |
| `SystemIndex_PropertyStore` | Windows 8 부터 있습니다. 칸이 600개가 넘습니다. |
| `SystemIndex_Gthr`, `SystemIndex_GthrPth` | 수집 기록 표입니다. |
| `SystemIndex_DeletedDocIds` | 지운 문서 번호 |
| `SystemIndex_MaxDoc` | 가장 큰 문서 번호 |
| `SystemIndex_1`, `SystemIndex_1_Properties`, `SystemIndex_1_DATA_#`, `SystemIndex_1_OCC_#` | Windows 8 의 역색인 관련 표 |
| `SystemIndex_Gthr_S`, `SystemIndex_GthrPth_S`, `SystemIndex_MaxDoc_S`, `SystemIndex_DeletedDocIds_S` | Vista 에만 있는 사본 표입니다. 이름 끝에 `_S` 가 붙습니다. |

- 속성 표의 칸은 [파일 속성 되살리기](propertystore.md) 에서 다룹니다.
- 수집 기록 표의 칸은 [수집 기록](systemindex-gthr.md) 에서 다룹니다.
- 지운 문서 번호 표는 [지운 파일·옛 파일 흔적 찾기](deleted-file-traces.md) 에서 다룹니다.

### 표 목록 — SQLite 판 (Windows 11)

| 파일 | 표 |
|---|---|
| `Windows.db` | `SystemIndex_1_PropertyStore`, `SystemIndex_1_PropertyStore_Metadata` |
| `Windows-gather.db` | `SystemIndex_Gthr`, `SystemIndex_GthrPth` |

수집 기록 표가 `Windows.db` 가 아니라 `Windows-gather.db` 에 있다는 점을 기억합니다.

### 바이트 순서

libyal 문서는 이진 값의 바이트 순서가 Windows 버전마다 다르다고 적습니다.

| Windows | 이진 값 | FILETIME |
|---|---|---|
| XP | 빅엔디언 | 빅엔디언 |
| Vista | 리틀엔디언 | 리틀엔디언 |
| 7 | 빅엔디언 | 빅엔디언 |
| 8 | 칸마다 다릅니다 | 칸마다 다릅니다 |

- FILETIME 은 1601-01-01 부터 센 100나노초 단위 값입니다. 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- 빅엔디언 FILETIME 을 실제로 풀어 보는 예는 [파일 속성 되살리기](propertystore.md) 의 헥스 예시에 있습니다.

### `AesGcm1 SQLite3` 헤더

Windows 11 25H2 PC 한 대에서 `Windows.db`·`Windows-gather.db`·`Windows-usn.db` 의 헤더를 본 결과입니다.

| 오프셋 | 본 값 | 풀이 |
|---|---|---|
| 0~15 | `AesGcm1 SQLite3` + `0x00` | 보통 SQLite 는 이 자리가 `SQLite format 3` + `0x00` 입니다. |
| 16~17 | `0x1000` | 페이지 크기 4096 |
| 18~19 | `02 02` | 쓰기·읽기 버전 2. WAL 방식입니다. |
| 20 | `0x30` | 페이지마다 끝에 48바이트를 예약합니다. |
| 21~23 | `0x40 0x20 0x20` | 보통 SQLite 와 같은 값입니다. |
| 24 이후 | 파일마다 무작위처럼 보이는 값 | 평문 SQLite 헤더값이 아닙니다. |

이 파일을 `sqlite3` 로 열면 "file is not a database" 오류가 났습니다. 48바이트 예약 공간에 암호 검증값(nonce·tag)이 들어 있는지와 암호 키가 어디에 있는지는 확인하지 못했습니다.

- 보통 SQLite 헤더는 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것**

- `DataDirectory` 값은 그 PC 가 색인 DB 를 둔 폴더를 알려 줍니다.
- DB 형식으로 어느 세대의 윈도 검색이 만든 DB 인지 가늠할 수 있습니다. LevelBlue 글은 Windows 10 까지 ESE, Windows 11 은 SQLite 라고 적습니다. 빌드는 [시스템 기본 정보](../../system-account/os-version-computer-name-install-date-shutdown-t.md) 로 따로 확인합니다.
- 폴더 안의 파일 목록은 무엇을 함께 모아야 하는지 알려 줍니다.

**증명하지 못하는 것**

- 폴더에 DB 파일이 있어도 내용을 바로 읽을 수 있는 것은 아닙니다. `AesGcm1 SQLite3` 로 시작하는 파일은 보통 SQLite 도구로 열리지 않았습니다.
- 이 페이지의 정보만으로는 무엇이 색인됐는지 모릅니다. 내용은 표를 풀어야 나옵니다.

## 함정과 한계

1. **압수 이미지의 ESE DB 는 대부분 비정상 종료 상태입니다.** 압수 이미지에서 꺼낸 ESE DB(`Windows.edb` 포함)는 대부분 비정상 종료 (Dirty Shutdown) 상태였습니다. (현장 관찰)
2. **로그 복구가 안 되는 경우가 있습니다.** JET API 로 열려면 같은 폴더의 트랜잭션 로그로 복구해야 하는데, 오래된 로그가 지워져 이미지 안의 로그가 끊겨 있으면 복구가 안 됩니다. 페이지를 직접 해석하는 방식은 로그 없이 읽습니다. (현장 관찰)
3. **원본을 열면 바뀔 수 있습니다.** 항상 사본에서 작업합니다. (현장 관찰)
4. **Windows 10 이후 로그 확장자가 다릅니다.** `.jtx`·`.jcp` 를 `.log`·`.chk` 로 착각하면 로그를 못 찾습니다. (현장 관찰)
5. **Windows 11 파일은 암호화된 것으로 보이는 형식일 수 있습니다.** 보통 SQLite 도구로 열리지 않으면 첫 16바이트부터 확인합니다. WAL 안의 페이지 내용도 암호화돼 있는지는 확인하지 못했습니다.
6. **수집 기록 표는 다른 파일에 있습니다.** Windows 11 에서 `Windows.db` 만 모으면 수집 기록 표를 놓칩니다.
7. **바이트 순서를 틀리면 값이 엉뚱하게 나옵니다.** XP·7 은 빅엔디언, Vista 는 리틀엔디언입니다. 도구가 버전을 가려 읽는지 확인합니다.
8. **libyal 문서는 Windows 8 까지입니다.** Windows 10·11 의 칸 구성은 다른 자료와 검체로 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 **관찰한 헤더 값으로 만든 예시**입니다. 오프셋 24 이후는 파일마다 달라서 `??` 로 적었습니다.

```
AesGcm1 SQLite3 헤더의 첫 32바이트 (관찰 값으로 만든 예시)
00000000  41 65 73 47 63 6D 31 20  53 51 4C 69 74 65 33 00   AesGcm1 SQLite3.
00000010  10 00 02 02 30 40 20 20  ?? ?? ?? ?? ?? ?? ?? ??   ....0@  ........
```

```
보통 SQLite 파일의 첫 16바이트
00000000  53 51 4C 69 74 65 20 66  6F 72 6D 61 74 20 33 00   SQLite format 3.
```

1. 0x00~0x0F 를 봅니다. `41 65 73 47 63 6D 31 20` 은 `AesGcm1 ` 입니다. 보통 SQLite 라면 `53 51 4C 69 74 65 20 66` 으로 시작합니다.
2. 0x10~0x11 의 `10 00` 을 빅엔디언으로 읽으면 0x1000, 곧 4096 입니다. 페이지 크기입니다.
3. 0x12~0x13 의 `02 02` 는 쓰기·읽기 버전 2 입니다. WAL 방식이라는 뜻입니다.
4. 0x14 의 `30` 은 48 입니다. 페이지마다 끝에 48바이트를 비워 둡니다.
5. 0x15~0x17 의 `40 20 20` 은 보통 SQLite 와 같습니다.
6. 0x18 이후가 평문 헤더값으로 풀리지 않으면 이 형식으로 봅니다.

### 공개 도구로 한 번

- `Windows.edb` 는 ESEDatabaseView 같은 ESE 뷰어로 엽니다. 사본에서 엽니다.
- 보통 SQLite 형식인 `Windows.db` 는 SQLite DB Browser 로 엽니다.
- 공개 분석 도구 SIDR 은 `Windows.edb`(Windows 10 이하)와 `Windows.db`(Windows 11)를 모두 읽습니다. `AesGcm1 SQLite3` 로 시작하는 파일을 읽는지는 확인하지 못했습니다.
- 같은 글에는 WinSearchDBAnalyzer 도 나옵니다.

도구로 열기 전에 아래를 적어 둡니다.

- 폴더의 파일 목록과 크기
- 각 `.db`·`.edb` 파일의 첫 16바이트
- ESE 판이면 로그 파일의 확장자와 번호가 이어지는지

## 교차 검증

- [시스템 기본 정보](../../system-account/os-version-computer-name-install-date-shutdown-t.md) — Windows 버전과 빌드를 확인해 어느 형식을 기대할지 정합니다.
- [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) — 비정상 종료 DB 와 로그 복구를 다룹니다.
- [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) — 보통 SQLite 헤더와 WAL 구조를 다룹니다.
- [암호화 증거 다루기](../../../03-techniques/analysis/encrypted-evidence/index.md) — 열리지 않는 DB 를 기록하고 다루는 법입니다.
- [증거 획득](../../../03-techniques/process-acquisition/evidence-acquisition/index.md) · [라이브 응답](../../../03-techniques/process-acquisition/live-response/index.md) — 켜져 있는 PC 에서 색인 폴더를 모을 때 봅니다.

## 실습

공개 검체(NIST CFReDS 등)에서 Windows 이미지를 골라 풀어 봅니다.

1. SOFTWARE 하이브에서 `Windows Search` 키의 `DataDirectory` 값은 무엇입니까? 기본 폴더와 같습니까?
2. 색인 폴더에 어떤 파일이 있습니까? ESE 판이면 로그 확장자는 `.log` 입니까, `.jtx` 입니까?
3. 본 DB 의 첫 16바이트는 무엇입니까?
4. ESE 판이면 표 목록에 `SystemIndex_0A` 와 `SystemIndex_PropertyStore` 가운데 어느 것이 있습니까? 그 결과가 이미지의 Windows 버전과 맞습니까?
5. ESE 판이면 DB 는 비정상 종료 상태입니까? 로그로 복구할 수 있습니까?
6. Windows 11 이미지라면 `Windows-gather.db` 와 `-wal` 파일도 함께 있습니까?

## 참고 문헌

1. libyal esedb-kb, "Windows Search" (XP~8 기준) — https://raw.githubusercontent.com/libyal/esedb-kb/main/documentation/Windows%20Search.asciidoc
2. Phalgun Kulkarni·Julia Paluch, "Windows Search Index: The Forensic Artifact You've Been Searching For" (2023-04-26, LevelBlue/Stroz Friedberg 블로그) — https://levelblue.com/blogs/strozfriedberg/windows-search-index-the-forensic-artifact-youve-been-searching-for
3. Stroz Friedberg, "SIDR — Search Index DB Reporter" README — https://github.com/strozfriedberg/sidr
4. Microsoft Learn, "Indexing process in Windows Search" — https://learn.microsoft.com/en-us/windows/win32/search/-search-indexing-process-overview
