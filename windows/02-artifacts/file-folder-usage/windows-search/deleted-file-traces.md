---
title: "지운 파일·옛 파일 흔적 찾기"
parent: "윈도 검색 색인 DB"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1300
---

# 지운 파일·옛 파일 흔적 찾기

> 위치: [윈도 검색 색인 DB (Windows Search)](index.md) > 지운 파일·옛 파일 흔적 찾기

## 한 줄 요약

색인 DB 에는 지금 디스크에 없는 파일의 기록이 남을 수 있습니다. Windows 11 에서는 파일을 지워도 WAL 파일의 변경이 본 DB 에 쓰이기 전까지 그 파일의 기록이 본 DB 에 남습니다. ESE 판에는 지운 문서 번호를 적는 표가 따로 있습니다. 이 페이지는 이런 흔적을 어디서 찾고 어디까지 말할 수 있는지 다룹니다.

## 무엇을 기록하나 · 왜 생기나

### 색인에서 파일이 빠지는 흐름

색인에 파일 변경을 알리는 쪽은 NTFS 입니다. 파일이 추가·삭제·수정되면 NTFS 가 USN 변경 저널로 수집기 (Gatherer) 에 알리므로, 색인 범위 안의 파일을 지우면 색인에서도 그 파일이 빠집니다[3]. 서비스가 갑자기 멈추거나 알림이 빠지면 수집기는 새로 생기거나 바뀐 항목을 모릅니다[3].

알림이 빠졌을 때 지운 파일의 기록이나 옛 속성이 색인에 남는지는 실제 데이터로 확인해야 합니다. 알려진 흔적은 아래 두 가지입니다.

### 알려진 흔적 두 가지

| Windows | 흔적 | 근거 |
|---|---|---|
| 11 | 파일을 지워도, WAL 에 쌓인 변경이 재부팅이나 체크포인트 때 본 DB 에 쓰이기 전까지는 파일 기록이 본 DB 에 남아 있습니다. | LevelBlue |
| XP~8 (ESE) | `SystemIndex_DeletedDocIds` 표가 지운 문서 번호를 적습니다. | libyal |

- Vista 에는 이 표의 사본 표(`SystemIndex_DeletedDocIds_S`)도 있습니다. 사본 표 목록은 [위치와 형식](windows-edb-windows-db.md) 에 있습니다.

## 위치와 버전별 차이

### Windows 11 — WAL 파일

임시 기록을 담는 WAL 파일 (Write-Ahead Log) 은 본 DB 와 같은 폴더에 있습니다.

| 본 DB | WAL 파일 |
|---|---|
| `Windows.db` | `Windows.db-wal` |
| `Windows-gather.db` | `Windows-gather.db-wal` |

Windows 11 25H2 의 WAL 파일 예입니다.

| 파일 | 크기 | 첫 4바이트 |
|---|---|---|
| `Windows.db-wal` | 135,992바이트 | `37 7F 06 82` |
| `Windows-gather.db-wal` | 4,124,152바이트 | `37 7F 06 82` |
| `Windows-usn.db-wal` | 0바이트 | — |

`0x377F0682` 는 SQLite WAL 의 표준 시작값이고, 두 WAL 의 페이지 크기 필드는 4096 입니다. 본 DB 는 `AesGcm1 SQLite3` 로 시작하지만 WAL 파일의 시작값은 표준 값입니다. WAL 안의 페이지 내용도 암호화돼 있는지는 실제 데이터로 확인해야 합니다. 크기는 그 순간의 값이고 쓰기와 체크포인트에 따라 바뀝니다. WAL 의 구조는 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

### ESE 판 — `SystemIndex_DeletedDocIds`

| 열 | Windows |
|---|---|
| `DocumentId` | XP~8 |
| `CheckpointVersion` | Vista 부터 |

이 표는 지운 문서의 번호만 적고, 파일 이름이나 경로 열은 없습니다[2]. 이 번호가 속성 저장소의 `WorkID` 와 같은 번호인지는 실제 데이터로 확인해야 합니다.

## 찾는 절차

1. **폴더를 통째로 모읍니다.** 본 DB 와 함께 `-wal`·`-shm` 파일, ESE 판이면 로그 파일까지 모읍니다. 켜져 있는 PC 라면 아래 "함정" 의 라이브 수집 경고를 먼저 봅니다.
2. **사본에서 작업합니다.** 원본을 열면 바뀔 수 있습니다.
3. **Windows 11 이면 본 DB 만 연 결과와 WAL 을 함께 연 결과를 따로 뽑습니다.** 본 DB 사본만 둔 폴더와, 본 DB·WAL 사본을 함께 둔 폴더를 따로 만듭니다. 두 결과의 차이가 WAL 에 쌓인 변경입니다.
4. **색인에 남은 경로 목록을 뽑습니다.** 속성 저장소의 `System_ItemPathDisplay` 를 씁니다. 방법은 [파일 속성 되살리기](propertystore.md) 에 있습니다.
5. **지금 파일 시스템과 대조합니다.** 경로 목록을 [마스터 파일 테이블](../../filesystem/mft.md) 의 경로와 맞춥니다. 색인에만 있는 경로가 지운 파일의 후보입니다.
6. **ESE 판이면 지운 문서 번호를 봅니다.** `SystemIndex_DeletedDocIds` 의 번호를 적어 둡니다. 속성 저장소와 번호가 맞는지는 알려져 있지 않으므로, 번호가 겹치는 행이 있으면 경로와 시각을 함께 보고 판단합니다.
7. **후보마다 다른 흔적을 찾습니다.** [USN 변경 저널](../../filesystem/usnjrnl.md) 에서 그 파일의 삭제·이름 바꿈 기록을 찾습니다. [휴지통](../recycle-bin.md) 에 들어갔는지도 봅니다.
8. **손상된 DB 는 두 가지 이상 방식으로 엽니다.** 행 수가 다르면 적게 나온 쪽이 끝까지 읽지 못한 것일 수 있습니다. (아래 함정 참고)

ESE 페이지에 남은 지운 레코드를 찾는 일반 방법은 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 와 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것**

- 색인에 경로가 있고 지금 디스크에 없으면, 색인이 그 경로의 항목을 처리한 적이 있다는 것까지는 말할 수 있습니다.
- Windows 11 에서 본 DB 에만 있고 WAL 을 합치면 사라지는 행은, 그 사이에 그 행을 바꾸는 변경이 WAL 에 쌓였다는 뜻입니다.
- ESE 판의 `SystemIndex_DeletedDocIds` 에 번호가 있으면 색인이 그 번호의 문서를 지운 것으로 적었다는 뜻입니다.

**증명하지 못하는 것**

- 사용자가 그 파일을 지웠다는 것. 파일을 옮기거나 이름을 바꿔도 그 경로에서는 사라집니다. 색인만으로는 셋을 가르지 않습니다.
- 언제 지웠는지. 지운 파일의 행에 남은 수집 시각 (GatherTime) 은 색인이 그 파일을 마지막으로 처리한 시각입니다. 삭제 시각이 아닙니다.
- 색인에 없던 파일이 없었다는 것. 이 문제는 [색인 해석 함정](pitfalls.md) 에서 다룹니다.

보고서에는 기록으로 확인되는 만큼만 적습니다.
예: "Windows.db 의 속성 저장소에 `C:\Users\○○\Documents\계약서.docx` 행이 있습니다. 이 경로는 지금 $MFT 에 없습니다. 이 행의 수집 시각은 ○○ 입니다. 이 시각은 색인이 이 파일을 처리한 시각이며 삭제 시각은 아닙니다." (경로는 설명용 예시입니다.)

## 시각 해석

지운 파일의 행에 남은 시각은 그 파일이 있던 때의 기록이며, 수집 시각의 뜻은 [파일 속성 되살리기](propertystore.md) 에 있습니다. 삭제 시각은 색인이 아니라 USN 변경 저널이나 휴지통 기록에서 찾습니다. WAL 이 언제 본 DB 에 합쳐졌는지 알려 주는 값은 알려져 있지 않습니다.

## 함정과 한계

1. **라이브 수집이 증거를 덮을 수 있습니다.** 켜져 있는 시스템에서 DB 의 새 사본을 만들면 미할당 영역 수 GB 를 덮어써 증거가 사라질 수 있습니다[4]. 복사본을 어디에 쓸지 먼저 정합니다. [라이브 응답](../../../03-techniques/process-acquisition/live-response/index.md) 을 봅니다.
2. **재부팅하면 흔적이 줄 수 있습니다.** WAL 의 변경은 재부팅이나 체크포인트 때 본 DB 에 쓰입니다. 그러면 본 DB 에 남아 있던 지운 파일의 기록도 사라질 수 있습니다.
3. **WAL 내용이 읽히는지 확인합니다.** Windows 11 의 본 DB 는 `AesGcm1 SQLite3` 로 시작할 수 있습니다. WAL 안의 페이지 내용도 암호화돼 있는지는 실제 데이터로 확인합니다. [위치와 형식](windows-edb-windows-db.md) 을 봅니다.
4. **손상된 ESE DB 는 도구마다 행 수가 다릅니다.** 다른 ESE DB(SRUDB.dat)의 사례에서, 같은 손상 DB 의 한 표를 도구마다 1,612행과 1,742행으로 다르게 읽었습니다. B-트리를 끝까지 따라가지 못한 쪽이 적게 냈습니다. 지운 파일 후보를 셀 때 이 차이가 그대로 섞입니다. [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 따릅니다.
5. **도구가 WAL 을 어떻게 다루는지 확인합니다.** 도구가 본 DB 와 같은 폴더의 WAL 을 함께 읽는지 문서에서 확인하지 못했다면, 절차 3 처럼 폴더를 나눠 두 번 읽어 봅니다.
6. **`Windows-usn.db` 는 분석 가치가 낮다는 평가가 있습니다[1].** 그래도 파일은 함께 모읍니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 **관찰한 값으로 만든 예시**입니다. 실제 데이터에서 나온 값이 아닙니다.

```
Windows.db-wal 의 첫 4바이트 (관찰 값으로 만든 예시)
00000000  37 7F 06 82
```

1. `-wal` 파일의 크기를 먼저 봅니다. 0바이트면 본 DB 에 아직 쓰지 않은 변경이 없습니다.
2. 크기가 0 보다 크면 첫 4바이트를 봅니다.
3. `37 7F 06 82` 이면 SQLite WAL 의 표준 시작값입니다.
4. 같은 폴더 본 DB 의 첫 16바이트도 봅니다. `AesGcm1 SQLite3` 로 시작하면 WAL 내용도 바로 읽히지 않을 수 있습니다.
5. WAL 헤더의 나머지 필드와 프레임 구조는 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 를 따라 읽습니다.

### 공개 도구로 한 번

- SIDR 은 `Windows.edb`(Windows 10 이하)와 `Windows.db`(Windows 11)를 읽어 파일 보고서를 냅니다. 본 DB 만 둔 폴더와 WAL 을 함께 둔 폴더를 각각 SIDR 로 읽고 파일 보고서의 행을 비교하되, 행 수만 비교하지 않습니다. WAL 의 변경이 기존 행의 값만 바꿨다면 행 수는 같기 때문입니다.
- 두 보고서가 행 수와 값까지 같으면 SIDR 이 WAL 을 읽지 않았거나 WAL 에 파일 기록 변경이 없는 것입니다. 어느 쪽인지는 SQLite DB Browser 같은 다른 도구로 한 번 더 확인합니다.
- ESE 판은 ESEDatabaseView 같은 뷰어로 `SystemIndex_DeletedDocIds` 를 엽니다.

## 교차 검증

- [마스터 파일 테이블](../../filesystem/mft.md) · [폴더 인덱스와 슬랙](../../filesystem/i30.md) — 지금 파일 시스템에 그 경로가 있는지, 지운 항목의 흔적이 남았는지 봅니다.
- [USN 변경 저널](../../filesystem/usnjrnl.md) — 삭제·이름 바꿈의 시각을 찾습니다.
- [휴지통](../recycle-bin.md) — 휴지통을 거쳐 지웠는지 봅니다.
- [바로가기 파일](../lnk.md) · [점프리스트](../jump-lists.md) · [썸네일 캐시](../thumbcache-db-thumbs-db.md) — 지운 파일을 열거나 본 흔적을 더합니다.
- [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 옛 시점의 색인 DB 를 꺼내 지금 DB 와 비교합니다.
- [지운 파일의 흔적 찾기](../../../04-scenarios/activity/deleted-file-traces.md) · [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) — 색인 흔적을 다른 기록과 묶어 읽는 조사 흐름입니다.

## 실습

공개 자료(NIST CFReDS 등)에서 Windows 이미지를 골라 풀어 봅니다.

1. 색인 폴더에 `-wal` 파일이 있습니까? 크기는 얼마입니까?
2. 속성 저장소의 `System_ItemPathDisplay` 가운데 지금 $MFT 에 없는 경로는 몇 개입니까?
3. 그 경로마다 USN 변경 저널에 삭제나 이름 바꿈 기록이 있습니까?
4. ESE 판이면 `SystemIndex_DeletedDocIds` 에 번호가 몇 개 있습니까? 그 번호와 같은 `WorkID` 가 속성 저장소에 남아 있습니까?
5. 볼륨 섀도 복사본이 있으면 옛 색인 DB 를 꺼냅니다. 지금 DB 에는 없고 옛 DB 에만 있는 경로가 있습니까?
6. 같은 DB 를 두 도구로 열어 속성 저장소 행 수를 비교합니다. 다르다면 어느 쪽이 적습니까?

## 참고 문헌

1. Phalgun Kulkarni·Julia Paluch, "Windows Search Index: The Forensic Artifact You've Been Searching For" (2023-04-26, LevelBlue/Stroz Friedberg 블로그) — https://levelblue.com/blogs/strozfriedberg/windows-search-index-the-forensic-artifact-youve-been-searching-for
2. libyal esedb-kb, "Windows Search" (XP~8 기준) — https://raw.githubusercontent.com/libyal/esedb-kb/main/documentation/Windows%20Search.asciidoc
3. Microsoft Learn, "Indexing process in Windows Search" — https://learn.microsoft.com/en-us/windows/win32/search/-search-indexing-process-overview
4. Stroz Friedberg, "SIDR — Search Index DB Reporter" README — https://github.com/strozfriedberg/sidr
