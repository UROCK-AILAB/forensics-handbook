---
title: "NTFS 트랜잭션 로그"
parent: "아티팩트 · 파일시스템"
nav_order: 1430
---

# NTFS 트랜잭션 로그 ($LogFile)

## 한 줄 요약

`$LogFile` 은 NTFS 가 메타데이터 변경을 적는 트랜잭션 저널입니다. MFT 항목 2번입니다(참고 1). 파일을 만들고, 이름을 바꾸고, 폴더 목록에서 빼는 동작이 레코드로 남고, 레코드마다 다시 할 동작 (redo) 과 되돌릴 동작 (undo) 이 들어 있어 바뀌기 전 값도 볼 수 있습니다. 파일이 원을 그리듯 돌며 옛 기록을 덮어쓰므로 최근 몇 시간에서 며칠 분량만 남습니다.

## 무엇을 기록하나 · 왜 생기나

### 장애 복구용 기록입니다

NTFS 는 복구 가능한 파일시스템으로 설계돼, 볼륨 구조를 바꾸는 트랜잭션을 모두 기록해 두고 장애가 나면 되돌립니다(참고 4). NTFS 체크포인트 때 운영체제는 장애 복구에 필요한 처리를 알 수 있도록 로그 파일에 기록을 씁니다(참고 2). 로그 파일은 원을 그리듯 돌며 쓰이고, 새 트랜잭션이 가장 오래된 기록을 덮어씁니다(참고 4).

그래서 `$LogFile` 은 사람이 한 일을 적으려고 만든 기록이 아니라 파일시스템이 스스로를 고치려고 남긴 기록입니다.

### 레코드에 남는 동작

해석 도구 설명서는 redo·undo 에 들어 있는 동작을 아래 이름으로 나눕니다(참고 4). 뜻이 설명서에 적힌 것만 풀었습니다.

| 동작 이름 | 뜻 (참고 4) |
|---|---|
| InitializeFileRecordSegment | 새 파일을 만듭니다. `$FILE_NAME` 과 처음 `$DATA`(데이터 런 포함)가 들어 있습니다 |
| CreateAttribute | 속성을 처음 만듭니다. 파일 이름은 없고 데이터 런 위치가 있습니다 |
| UpdateMappingPairs | 데이터 런이 바뀝니다(내용 변경). 새로 붙은 값만 들어 있습니다 |
| SetNewAttributeSizes | `$DATA` 의 크기 값이 바뀝니다 |
| UpdateResidentValue | 상주 값이 바뀝니다. 담기는 내용은 Windows 버전에 따라 다릅니다(아래 "위치와 버전별 차이") |
| AddIndexEntryRoot · AddIndexEntryAllocation | 폴더 색인에 항목을 더합니다 |
| DeleteIndexEntryRoot · DeleteIndexEntryAllocation | 폴더 색인에서 항목을 뺍니다 |
| WriteEndOfIndexBuffer | 색인 버퍼 끝을 씁니다 |

설명서가 해석하는 동작은 이 밖에도 더 있습니다. DeleteAttribute, UpdateNonResidentValue, SetIndexEntryVcnRoot, SetIndexEntryVcnAllocation, UpdateFileNameRoot, UpdateFileNameAllocation, SetBitsInNonresidentBitMap, ClearBitsInNonresidentBitMap, OpenNonresidentAttribute, OpenAttributeTableDump, AttributeNamesDump, DirtyPageTableDump, TransactionTableDump, UpdateRecordDataRoot, UpdateRecordDataAllocation, CompensationLogRecord 입니다(참고 4).

### 레코드에서 얻는 것

- **파일 이름 이력**: 색인 항목 추가·삭제와 WriteEndOfIndexBuffer 같은 동작에서 이름을 모읍니다. 한 MFT 레코드가 그 기간에 거친 이름들을 볼 수 있습니다(참고 4).
- **지운 폴더 색인 항목**: 폴더 색인(INDX)에서 항목을 지우는 undo 동작을 따로 뽑을 수 있습니다(참고 4).
- **덮인 삭제 파일의 데이터 런**: InitializeFileRecordSegment, CreateAttribute, UpdateMappingPairs, SetNewAttributeSizes 를 이어 붙이면 MFT 레코드가 이미 덮인 삭제 파일의 데이터 런을 되살릴 수 있습니다. 조각난 파일도 됩니다. 다만 최근 이력만 남으므로 일부만 되살아날 수 있습니다(참고 4).
- **바뀌기 전 값**: undo 쪽에는 바뀌기 전 값이 들어 있습니다(참고 4).
- **USN 레코드**: `$UsnJrnl` 이 켜져 있으면, `$LogFile` 이 덮는 기간에 `$UsnJrnl` 에 쓴 레코드도 `$LogFile` 안에 있습니다(참고 4).

## 위치와 버전별 차이

### 위치와 크기

MFT 항목 2번 `$LogFile` 입니다(참고 1). 크기는 `chkdsk /l:<크기>` 로 바꾸고, 크기를 빼고 `/l` 만 주면 지금 크기를 보여 줍니다. NTFS 에서만 씁니다(참고 3).

`chkdsk` 문서에는 크기 단위가 적혀 있지 않습니다. 해석 도구 설명서는 `chkdsk D: /L:2097152` 를 2GB 로 설명하므로(참고 4), 이 설명대로면 단위는 KB 입니다. 같은 설명서는 흔한 크기를 "65 MB 파일" 로 적었습니다(참고 4). Windows 기본 크기와 최소 크기는 이 페이지에서 확인하지 못했으니 검체의 `$LogFile` 크기를 직접 봅니다.

### 얼마나 남나

크기가 클수록 오래 남습니다(참고 4). 자주 쓰는 시스템 드라이브는 몇 시간 분량만 남기 쉽고, 백업용 외장 디스크나 보조 디스크는 더 오래 남습니다(참고 4). 같은 설명서는 시스템 볼륨에서 일주일 분량이면 기대 이상이라고도 적었습니다(참고 4). 정리하면 몇 시간에서 며칠이고 볼륨 쓰임새에 따라 크게 다르므로, 검체마다 남은 기간을 직접 잽니다(아래 "시각 해석").

### Windows 버전별 차이

| 볼륨을 다룬 Windows | 상주 파일의 내용을 바꿀 때 `$LogFile` 에 남는 것 |
|---|---|
| XP·Server 2003 (NT 5.x) | 상주 `$DATA` 의 바뀐 내용 전체가 UpdateResidentValue 의 redo·undo 에 남습니다(참고 4) |
| 요즘 Windows | 내용은 남지 않습니다. 바뀌었다는 사실만 남습니다(참고 4) |

- libyal 문서는 재시작 페이지 머리의 주 버전 값으로 -1(베타), 0(전환), 1(update sequence 지원) 만 적었습니다(참고 1). 이 표에 없는 값이 나올 수 있으므로, 값이 다르면 오류로 단정하지 않습니다.
- `fsutil fsinfo ntfsinfo` 는 LFS 버전을 보여 줍니다. 한 PC 에서는 2.0 이었습니다. (확인 범위: Windows 11 25H2 한 대) 이 값과 재시작 페이지 머리의 버전 칸이 어떻게 이어지는지는 확인하지 못했습니다.

## 구조

### 페이지

`$LogFile` 은 페이지 단위로 읽습니다. 페이지 서명은 세 가지입니다(참고 1).

| 서명 | 페이지 |
|---|---|
| `RSTR` | 재시작 페이지 |
| `RCRD` | 레코드 페이지 |
| `CHKD` | 이 서명의 뜻은 이번 자료에 적혀 있지 않습니다 |

- RCRD 페이지는 보통 0x1000(4096)바이트입니다(참고 4).
- 페이지 머리에도 fix-up 위치와 개수가 있습니다(참고 1). MFT 항목처럼 fix-up 을 적용한 뒤 읽습니다.

### 재시작 페이지 머리 (LFS_RESTART_PAGE_HEADER, 30바이트)

| 오프셋 | 크기 | 칸 (참고 1) |
|---|---|---|
| 0 | 4 | 서명 `RSTR` |
| 4 | 2 | fix-up 위치 |
| 6 | 2 | fix-up 개수 |
| 8 | 8 | chkdsk 가 남긴 마지막 LSN |
| 16 | 4 | 시스템 페이지 크기 |
| 20 | 4 | 로그 페이지 크기 |
| 24 | 2 | 재시작 영역 위치 |
| 26 | 2 | 부 버전 |
| 28 | 2 | 주 버전 (-1 베타, 0 전환, 1 update sequence 지원) |

### 레코드 머리 (LFS_RECORD_HEADER)

| 오프셋 | 크기 | 칸 (참고 1) |
|---|---|---|
| 0 | 8 | 이 레코드의 LSN |
| 8 | 8 | 이전 LSN |
| 16 | 8 | undo 다음 LSN |

- 그 뒤에 데이터 길이, 클라이언트 ID, 레코드 종류, 트랜잭션 ID, 플래그가 이어집니다(참고 1). 이 칸들의 오프셋은 이번 자료의 표에 없습니다.
- 클라이언트 데이터는 64비트 경계에서 시작합니다(참고 1).
- libyal 이 정리한 레코드 머리 칸에는 시각 칸이 없습니다(참고 1). 이 표는 일부만 정리된 것입니다.

### LSN 으로 이어지는 곳

MFT 항목 머리 오프셋 8 에 `$LogFile` 순번(LSN)이 있고, 폴더 색인 INDX 머리 오프셋 8 에도 LSN 이 있습니다(참고 1). 그래서 LSN 은 [$MFT](mft.md)·[$I30](i30.md)과 `$LogFile` 을 잇는 고리입니다.

이 LSN 이 "그 항목을 마지막으로 바꾼 기록" 을 뜻한다는 설명은 이번 자료로 확인하지 못했습니다. 보고서에는 "항목에 적힌 LSN 과 같은 LSN 의 레코드가 있다" 까지만 씁니다.

### `$LogFile` 슬랙

RCRD 페이지에서 마지막 트랜잭션 뒤부터 페이지 끝까지 빈 공간이 남고, 이 자리에 로그가 한 바퀴 돌기 전의 트랜잭션이 남아 있습니다(참고 4). 옛 기록이 여러 겹으로 남을 수 있고, 머리가 잘린 트랜잭션도 있습니다(참고 4).

> 그림 자리: `$LogFile` 을 원형 띠로 그리고, 재시작 페이지 뒤에 RCRD 페이지가 이어지는 모습. RCRD 페이지 하나를 펼쳐 레코드들과 그 뒤 슬랙(한 바퀴 전 트랜잭션 조각)을 색으로 나눈 그림

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 로그가 덮는 기간에 이 MFT 항목에 이런 메타데이터 동작이 있었습니다 | 로그가 덮는 기간 밖에서 일어난 일 |
| 한 MFT 레코드가 그 기간에 거친 이름들 | 요즘 Windows 에서 상주 파일 내용이 무엇으로 바뀌었는지 |
| 폴더 색인에서 이름이 빠진 기록과 빠지기 전 값 (undo) | 누가 했는지. 정리된 레코드 머리 칸에는 사용자나 프로세스를 가리키는 칸이 없습니다 |
| 이미 덮인 삭제 파일의 데이터 런 일부 | 그 데이터 런이 가리키던 클러스터 내용이 지금도 남아 있는지 |
| XP·2003 이 다룬 볼륨이라면 상주 파일 내용의 바뀌기 전·후 | 동작이 일어난 정확한 시각 (아래 "시각 해석") |
| 레코드 사이의 앞뒤 순서 (LSN) | 사람이 직접 한 동작인지, 시스템이나 프로그램이 스스로 한 동작인지 |

### 보고서 문장

아래 이름과 번호는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`$LogFile` 에 MFT 41,456번 항목을 가리키는 폴더 색인 항목 삭제(DeleteIndexEntryAllocation) 레코드가 있습니다. 이 레코드의 undo 쪽에 이름 `계약서.docx` 가 남아 있습니다. 같은 기간의 USN 레코드와 순서로 맞춰 보면 이 동작은 2025-02-03 01:20~01:25 UTC 사이에 있었습니다."
- 쓰면 안 되는 문장: "사용자가 01:22 에 계약서.docx 를 지웠다."

## 시각 해석

libyal 이 정리한 레코드 머리 칸에는 시각이 없고(참고 1), 레코드마다 기록 시각 칸이 있는지는 확인하지 못했습니다. 해석 도구가 내보내는 시각은 redo·undo 안에서 해석한 파일 시각으로, 생성·수정·MFT 수정·접근 시각입니다(참고 4). 곧 도구 결과의 시각 칸은 대개 "그 동작이 파일에 써 넣은 시각 값" 이며 "그 동작이 일어난 시각" 과 다를 수 있습니다.

동작의 순서는 LSN 으로 잡고, 동작의 시각은 같은 기간의 USN 레코드와 맞춰 좁힙니다. `$LogFile` 이 덮는 기간의 USN 레코드는 `$LogFile` 안에도 있고(참고 4), USN 레코드의 시각은 FILETIME(UTC)입니다(참고 1). 남은 기간은 `$LogFile` 안에서 찾은 가장 이른 USN 레코드와 가장 늦은 USN 레코드의 시각을 적어서 잽니다. 그 사이가 이 검체에서 `$LogFile` 이 덮는 대략의 기간입니다.

- 여러 기록을 한 시간표로 합치는 절차는 [파일시스템 타임라인](../../03-techniques/analysis/timeline/filesystem-timeline-mft-usnjrnl-logfile.md)에서 다룹니다.

## 함정과 한계

1. **기간이 짧습니다.** 시스템 드라이브는 몇 시간 분량만 남을 수 있습니다(참고 4). 사건 뒤에 PC 를 오래 쓰면 필요한 기록이 덮입니다. 수집이 늦어질수록 잃는 것이 많습니다.
2. **실행 중인 볼륨에서는 계속 쓰입니다.** 수집하는 동안에도 새 트랜잭션이 옛 기록을 덮습니다. 수집 순서는 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md)을 봅니다.
3. **도구의 시각 칸을 동작 시각으로 읽습니다.** 그 값은 파일 시각입니다(참고 4). 위 "시각 해석" 을 봅니다.
4. **상주 파일 내용을 기대합니다.** 요즘 Windows 에서는 상주 파일의 바뀐 내용이 남지 않습니다(참고 4).
5. **슬랙의 조각을 온전한 레코드로 읽습니다.** 슬랙에는 머리가 잘린 트랜잭션이 섞여 있습니다(참고 4). 앞뒤 LSN 이 이어지는지 확인합니다.
6. **크기 단위를 짐작합니다.** `chkdsk` 문서에는 단위가 없습니다(참고 3). 단위가 KB 라는 것은 도구 설명서의 예시에서 읽은 것입니다(참고 4).
7. **원본 볼륨을 쓰기 가능하게 연결합니다.** `$LogFile` 은 장애 복구에 쓰는 파일입니다. 원본은 [쓰기 방지](../../03-techniques/process-acquisition/evidence-acquisition/write-blocker.md) 상태로 다룹니다.

### 지우기와 조작

- **파일을 지우고 흔적을 정리합니다.** 지운 파일의 이름이 폴더 색인 삭제 undo 와 이름 이력에 남을 수 있습니다(참고 4). 로그가 덮는 기간 안이어야 합니다. [지운 파일의 흔적 찾기](../../04-scenarios/activity/deleted-file-traces.md)와 [완전삭제 도구를 썼나](../../04-scenarios/activity/anti-forensics/wiping-tools.md)를 봅니다.
- **파일 시각을 바꿉니다.** 시각을 바꾼 동작이 로그 기간 안에 있었다면, undo 쪽에서 바뀌기 전 값을 찾아볼 수 있습니다. 판단 방법은 [시각 조작 탐지](../../03-techniques/analysis/timeline/timestomping.md)에서 다룹니다.
- **로그 크기를 줄입니다.** `chkdsk /l` 로 크기를 줄이면 남는 기간이 짧아집니다. 검체의 `$LogFile` 크기가 같은 쓰임새의 다른 볼륨보다 눈에 띄게 작으면 크기를 바꾼 적이 있는지 따져 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 libyal 명세를 보고 만든 재시작 페이지 머리 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    52 53 54 52 1E 00 09 00 00 00 00 00 00 00 00 00
0x10    00 10 00 00 00 10 00 00 30 00 01 00 01 00
```

1. `52 53 54 52` 는 ASCII `RSTR` 입니다. 재시작 페이지입니다.
2. 0x04 의 `1E 00` 은 fix-up 위치 0x1E(30) 입니다. 30바이트 머리 바로 뒤입니다.
3. 0x06 의 `09 00` 은 fix-up 개수 9 입니다.
4. 0x08 의 8바이트는 chkdsk 가 남긴 마지막 LSN 입니다. 이 예시에서는 0 입니다.
5. 0x10 의 `00 10 00 00` 은 시스템 페이지 크기 0x1000(4096) 입니다.
6. 0x14 의 `00 10 00 00` 은 로그 페이지 크기 0x1000(4096) 입니다.
7. 0x18 의 `30 00` 은 재시작 영역 위치 0x30 입니다.
8. 0x1A 의 `01 00` 은 부 버전 1, 0x1C 의 `01 00` 은 주 버전 1 입니다. 주 버전 1 은 update sequence 지원입니다.

그다음 할 일은 이렇습니다.

1. 재시작 페이지 뒤에서 `52 43 52 44`(`RCRD`) 로 시작하는 페이지를 찾습니다.
2. fix-up 을 적용하고 레코드 머리의 LSN 을 읽습니다.
3. [$MFT](mft.md) 에서 관심 있는 항목 머리 오프셋 8 의 LSN 을 읽습니다.
4. 같은 LSN 의 레코드를 `$LogFile` 에서 찾습니다. 찾으면 그 레코드의 동작과 redo·undo 를 읽습니다.

### 실행 중인 시스템에서

- `chkdsk C: /l` 은 지금 `$LogFile` 크기를 보여 줍니다(참고 3).
- `fsutil fsinfo ntfsinfo C:` 는 LFS 버전을 보여 줍니다.

### 공개 도구로 한 번

`$LogFile` 을 풀어 주는 공개 해석 도구가 있습니다. 어느 도구를 쓰든 아래를 확인합니다.

- 어떤 동작을 해석하는지 확인합니다. 위 동작 표와 견줘 봅니다.
- 시각 칸이 무엇인지 확인합니다. 파일 시각인지, 동작 시각인지 설명서에서 찾습니다.
- 슬랙과 USN 레코드를 따로 뽑는지 확인합니다.
- MFT 항목 크기(1024·4096)를 볼륨에 맞게 두는지 확인합니다.
- 레코드 몇 개는 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [마스터 파일 테이블 ($MFT)](mft.md) | 항목 머리의 LSN, 지금 남은 이름과 시각. 로그가 보여 주는 바뀌기 전 값과 비교합니다 |
| [USN 변경 저널 ($UsnJrnl)](usnjrnl.md) | 같은 파일 참조의 변경 이유와 시각. `$UsnJrnl` 이 훨씬 긴 기간을 담고, 세부 내용은 적습니다(참고 4) |
| [폴더 인덱스와 슬랙 ($I30)](i30.md) | INDX 머리의 LSN, 색인 항목 추가·삭제 기록과 슬랙에 남은 옛 항목 |
| [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 예전 시점의 볼륨에 남은 `$LogFile` |
| [파일시스템 기반 복구](../../03-techniques/analysis/data-recovery/undelete-ntfs-fat.md) | 로그에서 되살린 데이터 런으로 삭제 파일을 되살리기 |

## 실습

**직접 만든 Windows 10·11 가상 머신**에서 해 봅니다.

1. `chkdsk C: /l` 로 지금 크기를 적습니다.
2. 새 폴더에 텍스트 파일 하나를 만들고, 이름을 두 번 바꾸고, 지웁니다. 각 동작의 시각을 적어 둡니다.
3. 바로 이미지를 뜨거나 `$LogFile` 을 뽑습니다.
4. 그 파일의 MFT 항목 번호로 레코드를 모아 보십시오. 세 이름이 모두 남았습니까?
5. 같은 파일의 USN 레코드를 `$LogFile` 안에서 찾고, 적어 둔 시각과 비교해 보십시오.
6. 한 시간 동안 PC 를 평소처럼 쓴 뒤 다시 뽑아 보십시오. 4번의 레코드가 아직 남아 있습니까?

**NIST CFReDS 같은 공개 검체의 Windows 디스크 이미지**로도 풀어 봅니다.

1. `$LogFile` 크기는 얼마입니까?
2. `$LogFile` 안에서 찾은 가장 이른 USN 레코드와 가장 늦은 USN 레코드의 시각은 언제입니까? 이 검체에서 로그가 덮는 기간은 어느 정도입니까?
3. 폴더 색인 삭제 동작의 undo 에서 이름을 모아 보십시오. 그 이름이 지금 `$MFT` 에 남아 있는지 확인해 보십시오.

## 참고 문헌

1. libyal/libfsntfs, "New Technologies File System (NTFS)" 형식 문서 — https://raw.githubusercontent.com/libyal/libfsntfs/main/documentation/New%20Technologies%20File%20System%20(NTFS).asciidoc
2. Microsoft Learn, "fsutil usn" (Windows Commands) — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-usn
3. Microsoft Learn, "chkdsk" (Windows Commands) — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/chkdsk
4. jschicht/LogFileParser README ($LogFile 해석 도구 설명서) — https://github.com/jschicht/LogFileParser
