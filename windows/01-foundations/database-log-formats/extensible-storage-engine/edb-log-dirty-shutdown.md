---
title: "트랜잭션 로그와 비정상 종료 상태"
parent: "ESE 데이터베이스"
grand_parent: "기반 · 데이터베이스·로그 형식"
nav_order: 230
---

# 트랜잭션 로그와 비정상 종료 상태 (edb.log·Dirty Shutdown)

> 위치: [ESE 데이터베이스 (Extensible Storage Engine)](index.md) > 트랜잭션 로그와 비정상 종료 상태

## 한 줄 요약

ESE 는 DB 를 바꾸는 작업을 DB 파일보다 트랜잭션 로그 (Transaction Log) 에 먼저 적고, DB 를 깨끗하게 닫지 못하면 DB 파일 머리에 비정상 종료 (Dirty Shutdown) 상태가 남습니다. 압수 이미지에서 꺼낸 ESE DB 는 대부분 이 상태이므로 (현장 관찰), 로그를 함께 모으고 로그를 적용하기 전과 후를 나눠 읽어야 합니다.

## 이 형식을 쓰는 아티팩트

ESE DB 를 쓰는 아티팩트는 모두 같은 로그 방식을 씁니다.

- [SRUM](../../../02-artifacts/execution/system-resource-usage-monitor/index.md) — SRUDB.dat
- [웹캐시 DB](../../../02-artifacts/browsers/ie-edgehtml/webcachev01-dat.md) — WebCacheV01.dat
- [윈도 검색 색인 DB](../../../02-artifacts/file-folder-usage/windows-search/windows-edb-windows-db.md) — Windows.edb
- [액티브 디렉터리 DB](../../../02-artifacts/credentials/ntds-dit.md) — NTDS.dit

로그와 체크포인트 파일은 보통 DB 파일과 같은 폴더에 있지만, 앱은 로그 폴더(JET_paramLogFilePath)와 체크포인트 폴더(JET_paramSystemPath)를 따로 정할 수 있습니다.

### 파일 구성

아래 이름은 기본 이름 (Base Name) 이 `edb` 일 때의 예입니다.

| 파일 | 옛 이름 규칙 | 새 이름 규칙 | 담는 것 |
|---|---|---|---|
| 현재 로그 | `edb.log` | `edb.jtx` | 지금 쓰고 있는 로그 |
| 지난 로그 | `edb00001.log` … | `edb00001.jtx` … | 다 찬 로그. 이름의 숫자가 세대 번호입니다 |
| 임시 로그 | `edbtmp.log` | `edbtmp.jtx` | 다음 로그를 미리 만들어 둔 파일. 쓸 만한 내용이 없습니다 |
| 예약 로그 | `res1.log`·`res2.log` | `edbRES00001.jrs` 형태 | 디스크가 꽉 찰 때를 대비한 파일. 쓸 만한 내용이 없습니다 |
| 체크포인트 | `edb.chk` | `edb.jcp` | 어디까지 DB 파일에 반영했는지 |
| 플러시 맵 | 없음 | `<DB 이름>.jfm` | 쓰기가 사라진 사고를 잡으려는 메타데이터 |

기본 이름은 세 글자이고 기본값은 `edb` 지만 앱마다 달라서, 웹캐시 DB 는 `V01` 을 씁니다. 기본 이름은 폴더 안 체크포인트 파일 이름으로 알 수 있습니다. 세대 번호는 16진 다섯 자리라서 `edb00001.log` 가 첫 로그이고 `edb000ff.log` 가 255번째 로그이며, 1,048,576번째 로그부터는 `edb00100000.log` 처럼 11.3 형식이 됩니다. 로그 파일은 확장자가 .log 이지만 텍스트 파일이 아니라 이진 형식입니다.

현장 관찰로는 Win10 이후 Windows Search 가 로그에 .jtx, 체크포인트에 .jcp 를 씁니다. 예전 형식은 .log·.chk 였습니다.

### Windows 버전별 차이

| Windows | 달라진 점 |
|---|---|
| XP 전 | 비정상 종료 상태를 "inconsistent" 라고 불렀습니다. XP 부터 "dirty shutdown" 이라고 부릅니다 |
| Server 2003 까지 | 예약 로그 이름이 `res1.log`·`res2.log` 입니다 |
| Vista 이후 | 예약 로그 이름이 `<기본 이름>RES#####.jrs` 입니다. 앱 설정(JET_paramLegacyFileNames)에 따라 로그·체크포인트 확장자가 .log·.chk 또는 .jtx·.jcp 가 됩니다 |
| Win10 1607·Server 2016 이후 | DB 마다 플러시 맵(.jfm)이 생깁니다 |
| Win10·Server 2016 이후 | esentutl 복사 모드에 `/vss`·`/vssrec` 선택지가 있습니다 |

Microsoft 문서는 새 이름 규칙을 기본이라고 적는데, 같은 문서 모음의 매개변수 설명은 JET_paramLegacyFileNames 의 기본값을 옛 이름 규칙으로 적습니다. 그래서 실제 이름은 폴더를 열어 확인합니다.

## 로그를 먼저 쓰는 까닭

ESE 는 DB 를 바꾸는 작업을 먼저 로그에 적고 DB 파일에는 나중에 씁니다. 곧바로 쓸 수도 있고 한참 뒤에 쓸 수도 있으며, DB 파일에 쓰는 순서도 로그에 적은 순서와 다를 수 있습니다.

체크포인트 (Checkpoint) 는 "이 지점 앞의 작업은 모두 DB 파일에 들어갔다" 는 표시입니다. 체크포인트 파일은 복구할 때 다시 적용해야 하는 가장 오래된 로그를 기억하고, 체크포인트 뒤의 작업은 일부만 DB 파일에 들어갔을 수 있으므로 복구에는 체크포인트 뒤의 로그만 있으면 됩니다.

프로세스가 갑자기 끝나거나 시스템이 멈춰도 작업은 로그에 남습니다. 로그를 다시 적용해 DB 를 깨끗한 상태로 만드는 일을 소프트 복구 (Soft Recovery) 라고 하며, 엔진을 시작할 때(JetInit) 자동으로 하고 `esentutl /r` 로 손수 할 수도 있습니다. 끝나지 않은 트랜잭션은 복구할 때 되돌립니다. 백업에서 되살린 DB 에 로그를 적용하는 일은 하드 복구 (Hard Recovery) 라고 합니다.

DB 는 엔진을 정상적으로 끝낼 때(JetTerm)만 깨끗하게 닫힙니다.

같은 생각으로 만든 다른 형식으로 [레지스트리 .LOG1·.LOG2](../registry-hive/log1-log2.md), [SQLite WAL](../sqlite/wal-journal-shm.md), [NTFS $LogFile](../../../02-artifacts/filesystem/logfile.md) 이 있습니다.

### 로그 크기와 순환 로깅

로그 파일은 크기가 정해져 있고, 크기는 앱이 1,024바이트 단위로 정합니다(JET_paramLogFileSize, 기본값 5120). 현재 로그(`edb.log`)가 차면 이름이 `edb<세대>.log` 로 바뀌고 새 현재 로그를 씁니다.

순환 로깅 (Circular Logging) 을 켜면 엔진은 체크포인트보다 오래된 로그를 지우고, 끄면 전체 백업을 할 때까지 로그를 모두 남깁니다. 문서상 기본값은 꺼짐이지만 앱이 켤 수 있습니다.

> 그림 자리: 로그 세대가 이어지는 모습(edb00028.log → edb00029.log → edb.log)과 체크포인트 위치, 복구에 필요한 구간을 한 줄로 표시

## 구조

### DB 파일 머리에서 종료 상태를 보는 칸

DB 파일 머리 (File Header) 는 첫 페이지에 있고 둘째 페이지에 머리의 사본이 있습니다. 첫 페이지가 망가졌으면 페이지 크기만큼 떨어진 곳의 사본과 비교합니다. 머리 전체와 페이지 구조는 [파일 구조 (Page·B+Tree·Catalog)](page-b-tree-catalog.md) 에 있고, 여기서는 종료 상태와 로그에 관련된 칸만 봅니다. 숫자는 모두 리틀 엔디언입니다.

| 오프셋 | 크기 | 칸 | 뜻 |
|---|---|---|---|
| 0 | 4 | 검사합 (Checksum) | XOR 값. 시작값은 0x89ABCDEF 입니다. 계산 범위는 명세도 확정하지 않았습니다 |
| 4 | 4 | 서명 | `EF CD AB 89` |
| 8 | 4 | 형식 버전 | 0x620 등 |
| 16 (0x10) | 8 | DB 시각 (Database time) | 시계 시각이 아닙니다 |
| 52 (0x34) | 4 | DB 상태 (Database state) | 아래 표 |
| 56 (0x38) | 8 | 일관 위치 (Consistent position) | 마지막으로 깨끗하게 닫았을 때의 로그 위치. 비정상 종료 상태면 0 |
| 64 (0x40) | 8 | 일관 시각 (Consistent time) | 마지막으로 깨끗하게 닫은 시각. 비정상 종료 상태면 0 |
| 72 (0x48) | 8 | 붙인 시각 (Attach time) | 엔진이 DB 를 마지막으로 붙인 시각 |
| 80 (0x50) | 8 | 붙인 위치 (Attach position) | 그때의 로그 위치 |
| 88 (0x58) | 8 | 뗀 시각 (Detach time) | 엔진이 DB 를 마지막으로 뗀 시각 |
| 96 (0x60) | 8 | 뗀 위치 (Detach position) | 그때의 로그 위치 |
| 108 (0x6C) | 28 | 로그 서명 (Log signature) | 짝이 되는 로그 묶음의 서명 |
| 236 (0xEC) | 4 | 페이지 크기 | 바이트 단위 |

붙이기 (Attach) 는 엔진이 DB 파일을 열어 쓸 수 있게 연결하는 일이고 떼기 (Detach) 는 그 반대입니다. libyal 명세에 따르면 깨끗한 DB 에서는 일관 위치·시각이 뗀 위치·시각과 같습니다.

DB 시각은 이름과 달리 시계 시각이 아니며, libyal 명세의 예시 값은 449(0x1C1) 입니다. 페이지 머리에도 DB 시각 칸이 있는데, 명세는 이 값을 그 페이지를 마지막으로 바꾼 때의 DB 시각이라고 설명합니다.

DB 상태 값은 다음과 같습니다.

| 값 | 이름 | 뜻 |
|---|---|---|
| 1 | JET_dbstateJustCreated | 막 만든 DB |
| 2 | JET_dbstateDirtyShutdown | 비정상 종료. 소프트 복구나 하드 복구를 해야 쓸 수 있습니다 |
| 3 | JET_dbstateCleanShutdown | 정상 종료. 로그 없이 붙일 수 있습니다 |
| 4 | JET_dbstateBeingConverted | 형식을 올리는 중 |
| 5 | JET_dbstateForceDetach | 내부용 |

비정상 종료 DB 와 손상된 DB 는 다릅니다. 손상은 비트가 뒤집히는 것 같은 물리적·논리적 망가짐이고 소프트 복구로 고치지 못합니다.

### 로그 위치 (LGPOS)

로그 위치는 로그 안의 한 지점을 가리키는 8바이트 값입니다.

| 오프셋 | 크기 | 칸 |
|---|---|---|
| 0 | 2 | 섹터 안 위치 (ib) |
| 2 | 2 | 섹터 번호 (isec) |
| 4 | 4 | 세대 (lGeneration) |

세대는 로그 파일 이름에 붙는 16진 번호와 같은 수입니다. Microsoft 는 이 구조를 내부용이라고만 설명하고, 앞 두 칸의 정확한 뜻은 libyal 명세도 확정하지 않았습니다.

### 로그 시각 (LOGTIME)

머리의 일관 시각·붙인 시각·뗀 시각은 FILETIME 이 아닙니다. 바이트 하나에 날짜 칸 하나씩 담는 8바이트 구조입니다.

| 오프셋 | 크기 | 칸 |
|---|---|---|
| 0 | 1 | 초 |
| 1 | 1 | 분 |
| 2 | 1 | 시 |
| 3 | 1 | 일 |
| 4 | 1 | 월 |
| 5 | 1 | 연. 1900 을 더합니다 |
| 6 | 1 | 가장 낮은 비트가 UTC 표시 (fTimeIsUTC) |
| 7 | 1 | 채움 바이트 |

- 모든 칸이 0 이면 빈 값입니다.
- 다른 시각 형식과의 차이는 [시각 값 형식](../../value-decoding/filetime-unix-webkit-dos-ole.md) 을 봅니다.

### 로그 파일과 체크포인트 파일의 안쪽

libyal 명세는 DB 파일 형식을 다루고 로그 파일의 안쪽 배치는 다루지 않으므로, 이 글은 로그 파일과 체크포인트 파일의 오프셋을 적지 않습니다. 대신 Microsoft 의 오류 코드 설명으로 엔진이 무엇을 검사하는지 알 수 있습니다.

| 오류 | 번호 | 뜻 |
|---|---|---|
| JET_errDatabaseDirtyShutdown | -550 | DB 가 깨끗하게 닫히지 않았습니다. 먼저 복구를 해야 합니다 |
| JET_errMissingPreviousLogFile | -509 | 체크포인트가 가리키는 로그가 없습니다 |
| JET_errMissingLogFile | -528 | 현재 로그가 없습니다 |
| JET_errRequiredLogFilesMissing | -543 | 복구에 필요한 로그가 없습니다 |
| JET_errLogGenerationMismatch | -513 | 로그 파일 이름과 안에 적힌 세대 번호가 다릅니다 |
| JET_errInvalidLogSequence | -515 | 다음 로그의 시각이 기대한 값과 다릅니다 |
| JET_errDatabaseLogSetMismatch | -539 | DB 가 지금 로그 묶음과 짝이 아닙니다 |
| JET_errAttachedDatabaseMismatch | -1216 | 복구 중에 붙어 있어야 할 DB 가 없거나 맞지 않습니다 |

로그 파일 이름을 바꿔 사슬을 맞추면 세대 번호 검사에 걸리고, 다른 시점의 DB 와 로그를 섞으면 서명이나 시각 검사에 걸립니다.

## 읽는 법

### 헥스로 한 번 — 종료 상태와 시각 읽기

아래 바이트는 **명세로 만든 예시**입니다. 실제 검체에서 나온 값이 아닙니다.
`..` 은 이 설명에 필요 없는 바이트입니다. 0x20 줄은 뺐습니다.

```
DB 파일 사본, 오프셋 0x00 (명세로 만든 예시)
00000000  .. .. .. .. EF CD AB 89  20 06 00 00 00 00 00 00
00000010  C1 01 00 00 00 00 00 00  .. .. .. .. .. .. .. ..
00000030  .. .. .. .. 02 00 00 00  00 00 00 00 00 00 00 00
00000040  00 00 00 00 00 00 00 00  1E 2D 09 0E 03 7D 01 00
00000050  .. .. .. .. 2A 00 00 00  10 05 17 0D 03 7D 01 00
00000060  .. .. .. .. 29 00 00 00  .. .. .. .. .. .. .. ..
```

1. 오프셋 4 의 서명이 `EF CD AB 89` 입니다. ESE DB 파일입니다.
2. 오프셋 8 의 형식 버전은 0x620 입니다.
3. 오프셋 0x10 의 DB 시각은 0x1C1(449) 입니다. 시계 시각으로 읽지 않습니다.
4. 오프셋 0x34 의 상태는 2 입니다. 비정상 종료 상태입니다.
5. 오프셋 0x38 의 일관 위치와 0x40 의 일관 시각은 모두 0 입니다. 상태 2 와 맞습니다.
6. 오프셋 0x48 의 붙인 시각은 30초·45분·9시·14일·3월·125년입니다. 125 에 1900 을 더하면 2025년입니다.
7. 오프셋 0x4E 의 값이 1 입니다. 이 시각은 UTC 입니다. 붙인 시각은 2025-03-14 09:45:30 UTC 입니다.
8. 오프셋 0x54 에서 붙인 위치의 세대는 0x2A 입니다. 기본 이름이 `edb` 라면 이 세대의 로그는 지금 `edb0002A.log` 입니다. 아직 다 차지 않았다면 `edb.log` 입니다.
9. 오프셋 0x58 의 뗀 시각은 2025-03-13 23:05:16 UTC 입니다. 오프셋 0x64 에서 그때의 세대는 0x29 입니다.

이 예시는 다음처럼 읽습니다. DB 는 2025-03-13 23:05:16 에 깨끗하게 떨어졌고 2025-03-14 09:45:30 에 다시 붙었으며, 그 뒤로 깨끗하게 떨어진 기록은 없습니다.

### 도구로 한 번 — esentutl 로 확인하고 사본에서 복구하기

esentutl 은 Windows 에 들어 있는 ESE 도구입니다. 아래는 순서를 보여 주는 예입니다.

1. DB 파일이 있는 폴더를 통째로 사본으로 옮깁니다. 원본과 사본의 해시를 적습니다.
2. `esentutl /mh <DB 파일>` 로 머리를 봅니다. 출력의 `State:` 가 `Dirty Shutdown` 인지 `Clean Shutdown` 인지 봅니다.
3. `esentutl /mk <체크포인트 파일>` 로 체크포인트를 봅니다. 복구에 필요한 첫 세대를 확인합니다.
4. `esentutl /ml <로그 파일>` 로 로그 머리를 봅니다. 폴더의 로그 이름과 세대가 빠짐없이 이어지는지 확인합니다.
5. 사본을 한 벌 더 만듭니다. 그 사본 폴더에서 `esentutl /r <기본 이름>` 으로 소프트 복구를 합니다.
6. 다시 `/mh` 로 상태가 `Clean Shutdown` 인지 봅니다. 복구한 사본의 해시를 적습니다.
7. 복구 전 사본과 복구 후 사본을 둘 다 읽어 결과를 비교합니다.

복구 선택지에서 알아 둘 점은 다음과 같습니다.

- 로그 위치(`/l`)와 체크포인트 위치(`/s`)는 따로 주지 않으면 현재 폴더입니다.
- DB 위치(`/d`)를 주지 않으면 로그에 적힌 원래 폴더에서 DB 를 찾습니다. 사본에서 복구할 때는 DB 위치를 사본 폴더로 지정합니다.
- `/i` 는 짝이 맞지 않거나 없는 DB 붙이기를 무시합니다. 로그가 가리키는 DB 가운데 일부가 사본 폴더에 없을 때 필요할 수 있습니다.
- `/a` 는 DB 가 일관되기만 하면 커밋된 데이터를 잃어도 복구를 진행하게 합니다. 이 선택지를 썼다면 보고서에 적습니다.
- 수리(`esentutl /p`)는 복구가 아닙니다. 수리는 로그를 적용하지 않습니다. Microsoft 는 비정상 종료 DB 라면 수리 전에 먼저 복구를 하라고 권합니다.

## 포렌식에서 중요한 점

### 압수 이미지의 ESE DB 는 대개 비정상 종료 상태입니다

ESE 는 엔진을 정상적으로 끝낼 때에만 DB 를 정상 종료 상태로 적으므로, DB 를 쓰는 프로그램이 돌고 있는 동안 복사하거나 전원을 끊으면 비정상 종료 상태가 남습니다. 현장 관찰로는 압수 이미지에서 꺼낸 SRUDB.dat·WebCacheV01.dat·Windows.edb 가 대부분 비정상 종료 상태였고, 이미지 안의 로그 사슬이 끊겨 오래된 세대가 지워져 있어 복구가 안 되는 경우도 있었습니다.

### 읽는 방식은 두 가지입니다

| 방식 | 로그 | 보이는 것 | 한계 |
|---|---|---|---|
| JET API 로 열기 (esent.dll) | 비정상 종료 DB 는 먼저 소프트 복구가 필요합니다 | 로그까지 반영한 상태 | 로그 사슬이 끊기면 열지 못합니다. 원본 폴더에서 열면 DB 와 로그가 바뀝니다 |
| 페이지 직접 해석 | 없어도 읽습니다 | DB 파일에 실제로 적힌 상태 | 로그에만 있는 최근 변경을 보지 못합니다. B+트리가 어긋난 곳을 만날 수 있습니다 |

엔진은 시작할 때 자동으로 소프트 복구를 하므로 JET API 로 원본 폴더를 열면 복구가 돌 수 있습니다.

libyal 명세는 비정상 종료 DB 에서 가지 페이지 (Branch Page) 의 키가 가리키는 잎 페이지 (Leaf Page) 에 그 레코드가 없고 다음 잎 페이지에 있는 경우를 적어 두었는데, 이런 곳을 도구가 어떻게 다루는지에 따라 결과가 달라집니다. 현장 관찰로는 같은 손상 SRUDB.dat 의 앱 사용량 표에서 도구마다 1,612행과 1,742행처럼 결과가 달랐고, B+트리를 끝까지 따라가지 못한 쪽이 적게 냈습니다.

그래서 손상됐거나 비정상 종료된 DB 는 두 가지 이상 방식으로 열어 비교합니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 에 있습니다.

### 복구 전과 복구 후는 다른 증거입니다

복구 후에는 로그에만 있던 최근 레코드가 나타날 수 있고, 복구하면서 아직 정리되지 않은 지운 레코드의 흔적이 사라질 수 있습니다. 끝나지 않은 트랜잭션도 복구 때 되돌립니다. 그래서 두 벌을 모두 남기고, 보고서에는 어느 쪽에서 나온 값인지 적습니다.

지운 레코드를 DB 파일 안에서 찾는 법은 [파일 안에 남은 지운 레코드](deleted-records.md) 에 있습니다.

### 로그 사슬이 끊겼을 때

체크포인트가 가리키는 세대부터 현재 로그까지 한 세대라도 빠지면 소프트 복구가 실패합니다. 이때는 페이지 직접 해석으로 읽고, 보고서에는 로그에만 있던 변경을 반영하지 못했다고 적습니다.

[볼륨 섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 안에 같은 폴더의 옛 DB·로그 묶음이 남아 있을 수 있는데, DB 와 로그는 반드시 같은 시점의 묶음으로 씁니다. 섀도 복사본의 DB 와 현재 볼륨의 로그를 섞지 않습니다.

### 수집

- DB 파일만 가져오지 않습니다. 같은 폴더의 로그·체크포인트 파일을 함께 가져옵니다.
- 로그 폴더를 앱이 따로 정했을 수 있으므로, DB 폴더에 로그가 없으면 다른 폴더도 찾습니다.
- 켜진 PC 에서는 쓰는 중인 파일이 잠겨 있습니다. Win10·Server 2016 부터 `esentutl /y` 에 `/vss`·`/vssrec` 이 있는데, `/vss` 는 스냅숏에서 복사만 하고 로그를 적용하지 않아 이 사본에는 아직 DB 에 쓰이지 않은 기록이 빠질 수 있습니다. `/vssrec` 은 로그를 적용해 복사하므로 이 사본에서는 아직 정리되지 않은 지운 레코드가 사라질 수 있습니다. 그래서 두 방식으로 두 벌을 떠 두는 방법이 있습니다.
- 수집 절차는 [선별 수집](../../../03-techniques/process-acquisition/evidence-acquisition/triage-collection.md) 과 [실행 중 시스템 이미징](../../../03-techniques/process-acquisition/live-response/live-imaging.md) 을 봅니다.
- 원본에는 복구를 돌리지 않습니다. 원본·복구 전 사본·복구 후 사본의 해시를 모두 적습니다. [해시로 무결성 검증](../../../03-techniques/process-acquisition/evidence-acquisition/hash-verification.md) 을 봅니다.

### 시각 해석

머리의 일관 시각·붙인 시각·뗀 시각은 로그 시각 구조라서 FILETIME 으로 읽으면 틀립니다. 오프셋 6 바이트의 가장 낮은 비트가 1 이면 UTC 이고, 0 이면 명세만으로는 시간대를 알 수 없으므로 다른 기록과 맞춰 봅니다. 방법은 [시간대·시계 오차 보정](../../../03-techniques/analysis/timeline/time-normalization.md) 에 있습니다. 문서화된 칸은 초 단위까지입니다.

붙인 시각은 엔진이 DB 를 붙인 때이지 사용자가 무엇을 한 때가 아닙니다. DB 안 레코드의 시각(예: SRUM 의 기록 시각)은 각 아티팩트 페이지의 설명을 따릅니다.

### 증거로서 — 말해 주는 것과 말해 주지 못하는 것

- **말해 주는 것**: DB 파일을 복사한 시점에 DB 가 깨끗하게 닫혀 있지 않았다는 것.
- **말해 주는 것**: 엔진이 DB 를 마지막으로 붙인 시각과 마지막으로 깨끗하게 뗀 시각.
- **말해 주는 것**: 그때 쓰던 로그의 세대 번호.
- **말해 주지 못하는 것**: 비정상 종료의 원인. 전원 차단, 켜진 상태 이미징, 프로세스 강제 종료를 상태 값만으로는 가리지 못합니다. [켜짐·꺼짐 이벤트](../../../02-artifacts/event-logs/power-on-off-events.md) 와 함께 봅니다.
- **말해 주지 못하는 것**: 누가 PC 를 썼는지, 사용자가 무엇을 했는지.

비정상 종료 상태를 그 자체로 조작 흔적으로 읽지 않습니다. 보고서에는 "DB 머리의 상태 값은 2(비정상 종료)이고, 마지막으로 붙인 시각은 2025-03-14 09:45:30 UTC 이다. 이 값은 그 뒤로 DB 가 깨끗하게 닫힌 기록이 없다는 것만 보여 준다" 처럼 씁니다.

## 함정

- **DB 파일만 수집합니다.** 로그를 빼면 최근 변경을 잃고, 소프트 복구도 할 수 없습니다.
- **원본 폴더에서 엽니다.** JET API 로 열거나 복구하면 DB 와 로그가 바뀝니다. 늘 사본에서 작업합니다.
- **복구 전과 후를 섞어 씁니다.** 두 결과는 다른 증거입니다. 어느 쪽 값인지 적습니다.
- **다른 시점의 DB 와 로그를 섞습니다.** 서명·시각 검사에 걸려 복구가 실패합니다.
- **로그 이름을 바꿔 사슬을 맞춥니다.** 세대 번호 검사에 걸립니다. 증거 파일 이름을 바꾸는 것 자체도 기록에 남겨야 할 변경입니다.
- **.log 만 찾습니다.** 앱에 따라 .jtx·.jcp 를 씁니다. 기본 이름도 앱마다 다릅니다.
- **복구와 수리를 헷갈립니다.** 수리(`/p`)는 로그를 적용하지 않습니다. 수리는 DB 를 고쳐 쓰므로 결과가 원래 기록과 다를 수 있습니다.
- **비정상 종료를 손상으로 읽습니다.** 상태 2 는 복구가 필요하다는 뜻이지 파일이 망가졌다는 뜻이 아닙니다.
- **도구 하나의 행 수를 그대로 믿습니다.** 비정상 종료·손상 DB 는 도구마다 결과가 다를 수 있습니다.
- **임시 로그와 예약 로그에서 내용을 찾습니다.** Microsoft 문서는 두 파일에 쓸 만한 내용이 없다고 설명합니다.
- **머리의 시각을 FILETIME 으로 읽습니다.** 바이트별 날짜 구조입니다.

## 도구

아래 공개 도구는 예로만 듭니다. 한 도구의 결과에만 기대지 않습니다.

| 도구 | 로그·종료 상태와 관련된 기능 |
|---|---|
| esentutl (Windows 기본) | `/mh` 머리와 상태, `/mk` 체크포인트, `/ml` 로그 머리, `/r` 소프트 복구, `/p` 수리, `/y` 복사(`/vss`·`/vssrec`) |
| libesedb (esedbinfo·esedbexport) | 로그 없이 DB 파일 페이지를 직접 해석합니다 |
| 헥스 편집기 | 오프셋 0x34 의 상태, 0x48·0x58 의 시각, 0x54·0x64 의 세대를 직접 읽습니다 |

두 도구의 결과가 다르면 먼저 복구 여부와 읽은 방식을 비교합니다.

## 참고 문헌

- Joachim Metz, libyal/libesedb, *Extensible Storage Engine (ESE) Database File (EDB) format* — https://github.com/libyal/libesedb/blob/main/documentation/Extensible%20Storage%20Engine%20(ESE)%20Database%20File%20(EDB)%20format.asciidoc
- Microsoft Learn, *Extensible Storage Engine Files* — https://learn.microsoft.com/en-us/windows/win32/extensible-storage-engine/extensible-storage-engine-files · *Transaction Log Parameters* — https://learn.microsoft.com/en-us/windows/win32/extensible-storage-engine/transaction-log-parameters
- Microsoft Learn, *JET_LOGTIME Structure* — https://learn.microsoft.com/en-us/windows/win32/extensible-storage-engine/jet-logtime-structure · *JET_LGPOS Structure* — https://learn.microsoft.com/en-us/windows/win32/extensible-storage-engine/jet-lgpos-structure
- Microsoft Learn, *Extensible Storage Engine Error Codes* — https://learn.microsoft.com/en-us/windows/win32/extensible-storage-engine/extensible-storage-engine-error-codes
- Microsoft Learn (보관 문서), *Esentutl /recovery* — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh875590(v=ws.11) · */repair* — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh875504(v=ws.11) · */file dump* — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh875603(v=ws.11)
- DFIR on the Mountain, *Locked File Access Using ESENTUTL.exe* (2018) — https://dfironthemountain.wordpress.com/2018/12/06/locked-file-access-using-esentutl-exe/
