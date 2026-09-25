---
title: "윈도 검색 색인 DB"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1260
has_children: true
has_toc: false
---

# 윈도 검색 색인 DB (Windows Search)

## 한 줄 요약

윈도 검색 (Windows Search) 은 파일을 빨리 찾으려고 파일의 이름·경로·속성·본문을 미리 모아 두는 기능입니다. 모은 결과는 색인 DB 에 쌓입니다. Windows 10 까지는 ESE 형식의 `Windows.edb` 를 쓰고, Windows 11 은 SQLite 형식의 `Windows.db` 와 `Windows-gather.db` 를 씁니다. 이 DB 를 풀면 그 PC 에 어떤 파일이 어느 경로에 있었는지 목록을 얻을 수 있습니다.

## 왜 중요한가

윈도 검색은 파일 시스템뿐 아니라 Outlook 편지함 같은 저장소도 색인합니다. 기본 설정에서는 파일 이름과 전체 경로를 포함해 파일의 모든 속성을 색인하고, 글자가 든 파일은 본문도 색인합니다. 그래서 색인 DB 는 "이 이름의 파일이 이 경로에 있었다" 는 목록 구실을 하고, 파일 크기·특성·소유자·요약 글 같은 속성도 파일마다 한 행에 남습니다. 파일 말고도 IE·Edge 로 연 주소와 활동 기록 (ActivityHistory) 이 들어갈 수 있습니다. 수집기 (Gatherer) 가 무엇을 처리했는지 적는 표와 글자 로그 파일도 따로 있습니다.

Windows 11 에서는 파일을 지운 뒤에도 한동안 그 파일의 기록이 본 DB 에 남습니다. 지운 변경이 WAL 파일에 머물다가 재부팅이나 체크포인트 때 본 DB 에 쓰이기 때문입니다.

증명하지 못하는 것도 분명합니다.

- 색인 범위 밖의 파일은 처음부터 색인하지 않습니다. 그래서 "색인에 없다" 가 "파일이 없었다" 는 뜻은 아닙니다.
- 색인의 수집 시각 (GatherTime) 은 색인이 파일을 처리한 시각입니다. 사용자가 파일을 연 시각이 아닙니다.
- 색인을 초기화하면 DB 를 새로 만듭니다. 초기화 전 기록이 새 DB 에 이어지는지는 확인한 자료가 없습니다.
- 색인 기록을 특정 사용자와 잇는 방법은 공개 자료에서 확인하지 못했습니다.
- Windows 11 25H2 PC 한 대에서는 DB 파일이 보통 SQLite 형식이 아니었습니다. 첫 16바이트가 `AesGcm1 SQLite3` 였고, SQLite 도구로 열리지 않았습니다.

## 한눈에 보기

> 그림 자리: 수집기가 파일 시스템(USN 변경 알림)과 Outlook(알림)에서 항목을 받아 대기열에 넣고, 속성 저장소·수집 기록 표·GatherLogs 로 나눠 남기는 흐름. Windows 10(Windows.edb 한 파일)과 Windows 11(Windows.db·Windows-gather.db·WAL)의 파일 배치를 나란히 보여 주는 그림

### 위치

| 항목 | 내용 |
|---|---|
| 기본 폴더 (Vista 이후) | `C:\ProgramData\Microsoft\Search\Data\Applications\Windows\` |
| 기본 폴더 (XP) | `C:\Documents and Settings\All Users\Application Data\Microsoft\Search\Data\Applications\Windows\` |
| 폴더를 정하는 값 | `HKLM\Software\Microsoft\Windows Search` 키의 `DataDirectory` 값 |
| 형식 | Windows 10 까지 ESE, Windows 11 은 SQLite. 형식 자체는 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 와 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다. |

폴더에 함께 있는 로그·임시 파일과 표 목록은 [위치와 형식](windows-edb-windows-db.md) 에 있습니다.

### Windows 버전에 따라 달라지는 점

| Windows | DB 파일 | 형식 | 파일 속성 표 | 수집 기록 표 |
|---|---|---|---|---|
| XP·Vista·7 | `Windows.edb` | ESE | `SystemIndex_0A` | `SystemIndex_Gthr`·`SystemIndex_GthrPth` |
| 8·10 | `Windows.edb` | ESE | `SystemIndex_PropertyStore` | `SystemIndex_Gthr`·`SystemIndex_GthrPth` |
| 11 | `Windows.db`·`Windows-gather.db`·`Windows-usn.db` | SQLite | `Windows.db` 의 `SystemIndex_1_PropertyStore` | `Windows-gather.db` 의 `SystemIndex_Gthr`·`SystemIndex_GthrPth` |

- XP~8 의 표 구성은 libyal 문서를 따릅니다. Windows 10·11 은 LevelBlue(옛 Aon) 글을 따릅니다.
- 암호화된 것으로 보이는 Windows 11 형식이 어느 빌드부터 쓰였는지는 확인한 자료가 없습니다.

### 알려 주는 것

| 알고 싶은 것 | 어디에 남나 | 자세히 |
|---|---|---|
| 파일 이름·전체 경로·크기·특성·소유자 | 속성 저장소 (Property Store) | [파일 속성 되살리기](propertystore.md) |
| 색인이 파일을 처리한 시각 | 속성 저장소의 `System.Search.GatherTime` | [파일 속성 되살리기](propertystore.md) |
| IE·Edge 로 연 주소, 활동 기록 | 속성 저장소의 주소·활동 기록 속성 | [파일 속성 되살리기](propertystore.md) |
| 수집기가 다룬 파일 이름과 주소 | `SystemIndex_Gthr`·`SystemIndex_GthrPth`, GatherLogs 폴더 | [수집 기록](systemindex-gthr.md) |
| 지운 파일의 흔적 | Windows 11 의 WAL 파일, ESE 판의 `SystemIndex_DeletedDocIds` | [지운 파일·옛 파일 흔적 찾기](deleted-file-traces.md) |
| 어느 폴더가 색인 대상이었나 | SOFTWARE 하이브의 `CrawlScopeManager` 키 | [색인 해석 함정](pitfalls.md) |

## 읽는 순서

1. [위치와 형식 (Windows.edb·Windows.db)](windows-edb-windows-db.md) — 색인 폴더에서 무엇을 모을지 정리합니다. Windows 버전별 파일과 표 목록, 바이트 순서, Windows 11 에서 본 `AesGcm1 SQLite3` 헤더를 다룹니다.
2. [파일 속성 되살리기 (PropertyStore)](propertystore.md) — 파일마다 남은 이름·경로·크기·시각을 읽습니다. 압축된 문자열, IE·Edge 주소, 활동 기록, GatherTime 의 뜻도 다룹니다.
3. [수집 기록 (SystemIndex_Gthr)](systemindex-gthr.md) — 수집기가 파일을 어떻게 찾아 처리하는지 설명합니다. 수집 기록 표의 칸과 GatherLogs 글자 로그를 읽는 법을 다룹니다.
4. [지운 파일·옛 파일 흔적 찾기](deleted-file-traces.md) — 지금 디스크에 없는 파일의 기록을 찾습니다. WAL 파일과 지운 문서 번호 표를 다루고, 라이브 수집 때 조심할 점을 짚습니다.
5. [색인 해석 함정 (색인 범위·재구성)](pitfalls.md) — "색인에 없다" 를 어디까지 말할 수 있는지 정리합니다. 색인 범위 규칙, 색인 방식, 초기화, 사용자 구분 문제를 다룹니다.

## 함께 볼 페이지

- [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) · [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) — 두 DB 형식을 직접 읽는 데 필요한 구조입니다.
- [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) · [윈도 압축 형식](../../../01-foundations/value-decoding/lznt1-xpress-xpress-huffman.md) · [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) — FILETIME, LZXPRESS 허프만, UTF-16LE 를 풉니다.
- [마스터 파일 테이블](../../filesystem/mft.md) · [USN 변경 저널](../../filesystem/usnjrnl.md) — 색인에 남은 경로를 지금 파일 시스템과 맞춰 보고, 수집기가 받은 변경 알림의 원천을 봅니다.
- [바로가기 파일](../lnk.md) · [점프리스트](../jump-lists.md) · [최근 문서](../recentdocs.md) — 색인이 말하지 못하는 "사용자가 열었다" 를 채웁니다.
- [윈도 타임라인](../activitiescache-db.md) · [인터넷 익스플로러·옛 엣지](../../browsers/ie-edgehtml/index.md) — 색인에 들어간 활동 기록과 방문 주소를 맞춰 봅니다.
- [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 옛 시점의 색인 DB 를 꺼냅니다.
- [암호화 증거 다루기](../../../03-techniques/analysis/encrypted-evidence/index.md) — SQLite 도구로 열리지 않는 Windows 11 색인 DB 를 만났을 때 봅니다.
- [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) — 손상된 DB 를 여러 방식으로 읽고 비교합니다.
- [지운 파일의 흔적 찾기](../../../04-scenarios/activity/deleted-file-traces.md) · [이 파일을 누가 언제 열었나](../../../04-scenarios/activity/file-access.md) — 색인 DB 를 다른 기록과 묶어 읽는 조사 흐름입니다.

## 참고 문헌

- libyal esedb-kb, "Windows Search" (XP~8 기준) — https://raw.githubusercontent.com/libyal/esedb-kb/main/documentation/Windows%20Search.asciidoc
- Phalgun Kulkarni·Julia Paluch, "Windows Search Index: The Forensic Artifact You've Been Searching For" (2023-04-26, LevelBlue/Stroz Friedberg 블로그) — https://levelblue.com/blogs/strozfriedberg/windows-search-index-the-forensic-artifact-youve-been-searching-for
- Microsoft 지원, "Search indexing in Windows" — https://support.microsoft.com/en-us/windows/search-indexing-in-windows-da061c83-af6b-095c-0f7a-4dfecda4d15a
- Microsoft Learn, "Indexing process in Windows Search" — https://learn.microsoft.com/en-us/windows/win32/search/-search-indexing-process-overview
- Microsoft Learn, "System.Search.GatherTime" — https://learn.microsoft.com/en-us/windows/win32/properties/props-system-search-gathertime
- Microsoft Learn, "ISearchCatalogManager::Reset" — https://learn.microsoft.com/en-us/windows/win32/api/searchapi/nf-searchapi-isearchcatalogmanager-reset
