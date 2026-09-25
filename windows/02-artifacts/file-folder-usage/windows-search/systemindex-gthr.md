---
title: "수집 기록"
parent: "윈도 검색 색인 DB"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1290
---

# 수집 기록 (SystemIndex_Gthr)

> 위치: [윈도 검색 색인 DB (Windows Search)](index.md) > 수집 기록

## 한 줄 요약

수집기 (Gatherer) 는 색인할 항목을 찾아 대기열에 넣고 처리하는 윈도 검색의 한 부분입니다. `SystemIndex_Gthr` 표에는 수집기가 다룬 문서의 번호·파일 이름·수정 시각 같은 칸이 있습니다. `SystemIndex_GthrPth` 표에는 경로 조각을 담는 칸이 있습니다. 수집기는 DB 밖에도 탭으로 나뉜 글자 로그를 남깁니다(관찰).

## 무엇을 기록하나 · 왜 생기나

### 수집기가 하는 일

Microsoft 문서가 설명하는 색인 과정입니다.

- 색인은 수집기가 이끄는 세 단계로 진행됩니다.
  1. 주소 (URL) 를 대기열에 넣습니다.
  2. 항목에 접근해 자료를 모읍니다.
  3. 색인에 반영합니다.
- 대기열은 높은 우선순위 알림, 보통 알림, 주기적 훑기 세 개이고, 알림 대기열을 먼저 처리합니다.
- 검색 프로토콜 호스트 (Search Protocol Host) 프로세스는 보통 두 개가 뜹니다. 하나는 시스템 권한용이고 하나는 사용자 권한용이며, 사용자 자료는 시스템 권한으로 처리하지 않습니다.

### 원본마다 다른 처리

| 원본 | 처리 방식 |
|---|---|
| NTFS | 처음 한 번만 전체를 훑습니다. 그 뒤로는 USN 변경 저널의 알림으로 처리합니다. |
| Outlook | 훑지 않고 알림(`mapi://`)만 받습니다. |
| FAT 처럼 알림이 없는 곳 | 수집기가 주기적으로 전체를 다시 훑습니다. |

같은 문서는 원본을 두 무리로도 나눕니다.

| 무리 | 예 | 처리 방식 |
|---|---|---|
| 알림만 (notification-only) | NTFS, Outlook | 첫 훑기 뒤에는 전체를 다시 훑지 않습니다. USN 저널이 한 바퀴 돌아 넘치는 것 같은 실패가 있을 때만 다시 훑습니다. |
| 알림 가능 (notification-enabled) | IE, FAT | 색인기가 시작될 때 바뀐 것만 훑습니다. 그 뒤로는 알림을 듣습니다. |

- 이 문서는 FAT 를 "주기적으로 다시 훑는 곳" 과 "알림 가능 원본" 양쪽에 예로 들므로, FAT 볼륨의 항목은 NTFS 와 처리 흐름이 다르다는 점만 기억해 둡니다.
- USN 변경 저널은 [USN 변경 저널](../../filesystem/usnjrnl.md) 에서 다룹니다.

## 위치와 버전별 차이

| Windows | 파일 | 표 | 근거 |
|---|---|---|---|
| XP·Vista | `Windows.edb` | `SystemIndex_Gthr`, `SystemIndex_GthrPth` | libyal |
| 7·8 | `Windows.edb` | `SystemIndex_Gthr`, `SystemIndex_GthrPth` | libyal |
| 10 | `Windows.edb` | `SystemIndex_Gthr`, `SystemIndex_GthrPth` | LevelBlue |
| 11 | `Windows-gather.db` | `SystemIndex_Gthr`, `SystemIndex_GthrPth` | LevelBlue |
| 11 25H2 (PC 한 대) | `GatherLogs\SystemIndex\` 폴더 | 글자 로그 파일 `.Crwl`·`.gthr` | 관찰 |

- Windows 11 에서는 두 표가 `Windows.db` 가 아니라 `Windows-gather.db` 에 있습니다.
- Vista 에는 두 표의 사본 표(`_S`)가 따로 있습니다. 목록은 [위치와 형식](windows-edb-windows-db.md) 에 있습니다.

## 구조

### `SystemIndex_Gthr` 칸

| Windows 7·8 (libyal) | XP·Vista (libyal) |
|---|---|
| `ScopeID` | `PathId` |
| `DocumentID` | `DocumentID` |
| `SDID` — 32비트 정수 | `ContentIdentifierID` |
| `LastModified` — 빅엔디언 FILETIME 이진값 | `LastModified` |
| `TransactionFlags` | `FirstAccess`, `LastAccess` |
| `CrawlNumberCrawled` | `CrawlNumberCrawled` |
| `Priority` — 8비트 | `FailureUpdateAttempts` |
| `FileName` — 압축된 긴 문자열 | `DeletedCount`, `NeedsDeleting`, `NeedsIndexing`, `Failed` |
| `RequiredSIDs` — 이진값 | `FileName1`, `FileName2` — UTF-16LE |
| `FailureUpdateAttempts` — 8비트 | |

- 두 열은 같은 줄끼리 짝이 아닙니다. 버전별 칸 목록을 나란히 둔 것입니다.
- Windows 10 의 주요 칸은 `ScopeID`, `DocumentID`, `SDID`, `LastModified`, `FileName` 입니다(LevelBlue).
- `FileName` 은 압축된 문자열입니다. 압축과 난독화를 푸는 법은 [파일 속성 되살리기](propertystore.md) 에 있습니다.

### `SystemIndex_GthrPth` 칸

| Windows | 칸 | 근거 |
|---|---|---|
| 7·8·10 | `Scope`, `Parent`, `Name` | libyal, LevelBlue |
| XP·Vista | `LookupMD5`, `LookupValue` | libyal |

### 두 표를 잇는 법 — 확인하지 못한 부분

- 칸 이름만 보면 `Gthr.ScopeID` 를 `GthrPth.Scope` 에 맞추고 `Parent` 를 따라 올라가 폴더 경로를 조립할 수 있을 것처럼 보입니다. 이 방법을 설명한 명세는 확인하지 못했습니다.
- `Gthr.DocumentID` 가 속성 저장소의 `WorkID` 와 같은 번호인지도 확인하지 못했습니다.
- `LastModified` 가 정확히 어떤 시각인지도 확인하지 못했습니다. 파일 수정 시각을 옮겨 적은 값인지 알 수 없습니다.
- 그래서 조립한 경로나 번호 짝은 속성 저장소의 `System_ItemPathDisplay` 와 몇 행씩 맞춰 본 뒤에 씁니다.

### 수집 로그 파일 (GatherLogs)

아래는 Windows 11 25H2 PC 한 대에서 본 내용입니다.

**로그 위치를 정하는 값**

`HKLM\SOFTWARE\Microsoft\Windows Search\Gather\Windows\SystemIndex` 키에 아래 값이 있었습니다.

| 값 이름 | 본 값 |
|---|---|
| `StreamLogsDirectory` | `...\Applications\Windows\GatherLogs` |
| `LogDirectory` | `...\Applications\Windows\Projects\SystemIndex` |
| `CatalogResetSignature`, `CheckPointNumber`, `NewCrawlNumber` | 값은 있었으나 뜻은 확인하지 못했습니다 |

**로그 파일**

- `GatherLogs\SystemIndex\` 에 `SystemIndex.<번호>.Crwl` 파일 95개와 `SystemIndex.<번호>.gthr` 파일 5개가 있었습니다.
- 두 파일 모두 UTF-16LE 글자 파일이었습니다. 파일 첫머리에 BOM `FF FE` 가 있었습니다.
- 한 줄의 칸은 탭으로 나뉘어 있었습니다.
- `.gthr` 에는 수집 대상 주소(`file:` 경로)가 그대로 적혀 있었습니다.

`.gthr` 한 줄의 예입니다. 사용자 이름과 파일 이름은 가렸습니다.

```
1296503f<탭>1dd4ab1<탭>file:C:/Users/<사용자>/<파일 이름>/<탭>8000000c<탭>0<탭>80041201<탭><탭>1<탭>4294967295<탭>34181
```

| 칸 | 풀이 |
|---|---|
| 첫째 칸 | FILETIME 의 하위 32비트 (16진수) |
| 둘째 칸 | FILETIME 의 상위 32비트 (16진수) |
| 셋째 칸 | 수집 대상 주소 |
| 나머지 칸 (`8000000c`, `80041201` 등) | 뜻을 확인하지 못했습니다 |

- 첫째 칸과 둘째 칸을 합치면 UTC FILETIME 이 됩니다.
- `.Crwl` 첫 줄의 값을 이렇게 풀면 2026-06-26 18:10:36 UTC 였습니다. 이 값은 그 폴더를 만든 시각(2026-06-27 03:10 한국 시각)과 맞았습니다.
- 위 줄의 둘째 칸 `1dd4ab1` 은 일곱 자리입니다. 앞자리 0 을 적지 않은 것으로 보입니다. 합칠 때는 앞에 0 을 채워 여덟 자리로 맞춥니다.
- 로그가 얼마나 오래 남는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것**

- `.gthr` 줄의 주소는 수집기가 그 경로를 다뤘다는 것을 보여 줍니다.
- `SystemIndex_Gthr` 행의 `FileName` 은 수집기가 다룬 파일 이름입니다.

**증명하지 못하는 것**

- 수집기는 파일 변경 알림을 받아 움직이므로, 수집 기록만으로는 누가 파일을 바꿨는지, 사용자의 손인지 프로그램의 동작인지도 가리지 못합니다.
- `LastModified` 의 정확한 뜻은 확인하지 못했습니다. 이 값을 파일 수정 시각이라고 단정해 적지 않습니다.
- 로그가 얼마나 남는지 모르므로, 로그에 없는 경로가 수집된 적이 없다고 말할 수 없습니다.
- 앞 두 칸의 시각이 정확히 무엇을 뜻하는지는 확인하지 못했습니다. `.Crwl` 첫 줄 하나를 폴더 생성 시각과 맞춰 본 것이 전부입니다. 검체에서 다른 기록과 한 번 더 맞춰 봅니다.
- `SDID`·`RequiredSIDs` 로 기록을 사용자와 잇는 방법은 확인하지 못했습니다. [색인 해석 함정](pitfalls.md) 에서 다룹니다.

보고서에는 기록이 말하는 만큼만 적습니다.
예: "GatherLogs 의 `SystemIndex.○○.gthr` 에 `file:C:/Users/○○/Documents/계약서.docx` 줄이 있습니다. 이 줄의 앞 두 칸을 FILETIME 으로 풀면 ○○ UTC 입니다." (경로는 설명용 예시입니다.)

## 시각 해석

| 값 | 형식 | 뜻 |
|---|---|---|
| `SystemIndex_Gthr.LastModified` (Windows 7·8) | 빅엔디언 FILETIME 이진값 | 확인하지 못했습니다 |
| `SystemIndex_Gthr.FirstAccess`·`LastAccess` (XP·Vista) | 형식을 확인하지 못했습니다 | 확인하지 못했습니다 |
| GatherLogs 한 줄의 첫째·둘째 칸 | 16진수 글자 두 조각으로 적은 FILETIME. UTC 입니다. (관찰) | 이 PC 에서 폴더 생성 시각과 맞았습니다 |

- FILETIME 을 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- 빅엔디언 FILETIME 을 푸는 예는 [파일 속성 되살리기](propertystore.md) 에 있습니다.
- 속성 저장소의 GatherTime 과 수집 기록의 시각은 다른 칸입니다. GatherTime 의 뜻은 [파일 속성 되살리기](propertystore.md) 에 있습니다.

## 함정과 한계

1. **Windows 11 에서는 파일이 따로 있습니다.** 수집 기록 표는 `Windows-gather.db` 에 있습니다. `Windows.db` 만 보면 표가 없다고 착각합니다.
2. **DB 가 안 열려도 로그는 읽힐 수 있습니다.** 같은 PC 에서 DB 파일은 `AesGcm1 SQLite3` 로 시작했지만 GatherLogs 파일은 UTF-16LE 글자 파일이었습니다.
3. **16진수 칸의 자릿수가 다를 수 있습니다.** 앞자리 0 을 빼고 적은 칸이 있었습니다. 상위·하위 칸을 합칠 때 각각 여덟 자리로 채웁니다.
4. **칸 순서를 바꿔 읽지 않습니다.** 앞 칸이 하위 32비트, 뒤 칸이 상위 32비트입니다. 거꾸로 합치면 터무니없는 날짜가 나옵니다.
5. **FAT 볼륨은 처리 흐름이 다릅니다.** 알림이 없는 곳은 주기적으로 다시 훑습니다. 그래서 수집 시각이 파일이 바뀐 때와 멀리 떨어질 수 있습니다.
6. **USN 저널이 넘치면 다시 훑습니다.** 이때는 많은 항목이 한꺼번에 다시 수집됩니다. 한 시간대에 기록이 몰려 있으면 처음 색인·재구성과 함께 이런 다시 훑기도 까닭의 후보로 둡니다.
7. **파일 이름 칸은 압축돼 있습니다.** Windows 7·8 의 `FileName` 은 압축된 긴 문자열입니다. 풀지 않은 값을 그대로 읽으면 글자가 깨집니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 **관찰한 칸 배치로 만든 예시**입니다. 실제 검체에서 나온 값이 아닙니다.

```
.gthr 파일 첫머리 (UTF-16LE BOM)
FF FE

한 줄의 앞 두 칸 (관찰한 칸 배치로 만든 예시)
00000000  31 00 30 00 30 00 64 00  30 00 35 00 38 00 30 00   1.0.0.d.0.5.8.0.
00000010  09 00 31 00 64 00 62 00  39 00 31 00 35 00 38 00   ..1.d.b.9.1.5.8.
00000020  09 00                                              ..
```

1. 글자마다 2바이트이고 뒤 바이트가 `00` 입니다. UTF-16LE 영문의 모양입니다. 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.
2. `09 00` 은 탭입니다. 이 줄의 첫째 칸은 `100d0580`, 둘째 칸은 `1db9158` 입니다.
3. 둘째 칸은 일곱 자리입니다. 앞에 0 을 채워 `01db9158` 로 맞춥니다.
4. 둘째 칸을 상위, 첫째 칸을 하위로 이으면 `0x01DB9158100D0580` 입니다.
5. 이 FILETIME 을 풀면 2025-03-10 01:02:15 UTC 입니다.
6. 거꾸로 이으면 `0x100D058001DB9158` 입니다. 이 값은 1601년에서 3천6백 년쯤 뒤를 가리킵니다. 뜻 있는 날짜가 아닙니다.

### 공개 도구로 한 번

- `Windows.edb`(Windows 10 이하)는 ESEDatabaseView 같은 ESE 뷰어로 사본을 열어 두 표를 봅니다.
- Windows 11 의 평문 SQLite `Windows-gather.db` 는 SQLite DB Browser 로 엽니다.
- GatherLogs 파일은 UTF-16LE 를 읽는 글자 편집기로 엽니다. 탭으로 나눠 표 계산 프로그램에 넣으면 칸별로 정렬할 수 있습니다.

아래를 맞춰 봅니다.

- `SystemIndex_Gthr` 의 `FileName` 과 속성 저장소의 `System_FileName` 이 같은 파일을 가리키는지
- `.gthr` 에 나온 경로가 속성 저장소에도 있는지
- `.gthr` 시각과 [USN 변경 저널](../../filesystem/usnjrnl.md) 의 같은 파일 기록이 가까운지

## 교차 검증

- [USN 변경 저널](../../filesystem/usnjrnl.md) — NTFS 수집 알림의 원천입니다. 수집 시각 직전에 그 파일의 변경 기록이 있는지 봅니다.
- [마스터 파일 테이블](../../filesystem/mft.md) — `LastModified` 가 파일 수정 시각과 맞는지 검체에서 확인합니다.
- [FAT·exFAT 구조](../../../01-foundations/disk-volume/fat-exfat.md) — 알림이 없는 볼륨의 파일을 다룰 때 봅니다.
- [아웃룩](../../mail/outlook/index.md) — `mapi://` 주소로 수집된 편지함 항목을 맞춰 봅니다.
- [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) — SOFTWARE 하이브의 `Gather` 키를 읽습니다.
- [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) — 수집 시각을 다른 기록과 한 줄에 놓을 때 "색인 처리" 로 따로 표시합니다.

## 실습

공개 검체(NIST CFReDS 등)에서 Windows 10 또는 11 이미지를 골라 풀어 봅니다.

1. 수집 기록 표는 어느 파일에 있습니까? 행은 몇 개입니까?
2. `SystemIndex_GthrPth` 의 `Scope`·`Parent`·`Name` 으로 폴더 경로를 조립해 봅니다. 조립한 경로가 속성 저장소의 `System_ItemPathDisplay` 와 맞습니까?
3. `Gthr.DocumentID` 와 속성 저장소의 `WorkID` 가 같은 파일을 가리키는 행을 몇 개 찾을 수 있습니까?
4. `LastModified` 를 같은 파일의 $MFT 수정 시각과 비교합니다. 같습니까, 다릅니까?
5. Windows 11 이미지라면 `GatherLogs\SystemIndex\` 에 파일이 몇 개 있습니까? 가장 이른 줄과 가장 늦은 줄의 시각은 언제입니까?
6. SOFTWARE 하이브의 `Gather\Windows\SystemIndex` 키에 어떤 값이 있습니까?

## 참고 문헌

1. libyal esedb-kb, "Windows Search" (XP~8 기준) — https://raw.githubusercontent.com/libyal/esedb-kb/main/documentation/Windows%20Search.asciidoc
2. Phalgun Kulkarni·Julia Paluch, "Windows Search Index: The Forensic Artifact You've Been Searching For" (2023-04-26, LevelBlue/Stroz Friedberg 블로그) — https://levelblue.com/blogs/strozfriedberg/windows-search-index-the-forensic-artifact-youve-been-searching-for
3. Microsoft Learn, "Indexing process in Windows Search" — https://learn.microsoft.com/en-us/windows/win32/search/-search-indexing-process-overview
