---
title: "파일 속성 되살리기"
parent: "윈도 검색 색인 DB"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1280
---

# 파일 속성 되살리기 (PropertyStore)

> 위치: [윈도 검색 색인 DB (Windows Search)](index.md) > 파일 속성 되살리기

속성 저장소 (Property Store) 는 색인한 항목마다 이름·전체 경로·크기·특성·시각·소유자 같은 속성을 모아 둔 표입니다. 표 이름과 모양은 Windows 버전마다 다릅니다. 이 표를 풀면 색인이 그 파일에 대해 모아 둔 속성을 파일마다 읽을 수 있습니다. IE·Edge 로 연 주소와 활동 기록도 이 표에 들어갑니다.

## 무엇을 기록하나

윈도 검색은 파일 형식별 속성을 색인합니다. 기본 설정에서는 파일 이름과 전체 경로를 포함해 파일의 모든 속성을 색인하고, 글자가 든 파일은 본문도 색인합니다. 파일에 맞는 필터가 없으면 `System.ItemName` 같은 최소한의 시스템 속성만 색인합니다.

- 문서라면 제목·주제·작성자·키워드·설명 같은 문서 속성이 들어갑니다.
- 메일이라면 보낸 사람·받는 사람·제목·받은 시각·첨부 여부가 들어갑니다.
- 사진·음악·동영상이라면 찍은 날짜·아티스트·프레임 폭 같은 미디어 속성이 들어갑니다.

파일 말고도 IE·Edge 로 연 주소와 활동 기록 (ActivityHistory) 이 들어갈 수 있습니다.

## 위치와 버전별 차이

| Windows | DB 파일 | 표 | 모양 |
|---|---|---|---|
| XP·Vista·7 | `Windows.edb` | `SystemIndex_0A` | 속성마다 열이 하나 있습니다. 열은 300개가 넘습니다. |
| 8·10 | `Windows.edb` | `SystemIndex_PropertyStore` | 속성마다 열이 하나 있습니다. 열은 600개가 넘습니다. |
| 11 | `Windows.db` | `SystemIndex_1_PropertyStore`, `SystemIndex_1_PropertyStore_Metadata` | 한 행에 (문서 번호, 속성 번호, 값) 이 하나씩 들어갑니다. |

- 폴더 위치와 DB 파일 목록은 [위치와 형식](windows-edb-windows-db.md) 에 있습니다.
- Windows 11 의 모양은 공개 도구 SIDR 의 소스 코드가 읽는 열에서 나온 것입니다[6].

## 구조

### ESE 판 (Windows 8~10) — `SystemIndex_PropertyStore`

- 기본 키 열은 `WorkID` 입니다. 32비트 부호 없는 정수입니다.
- 속성 열 이름은 "[속성 ID]-[속성 이름]" 형식입니다. 예: `4447-System_ItemPathDisplay`, `22-System_FileFRN`, `11-System_FileName`.
- 실제 열 이름에는 숫자 뒤에 `F` 가 붙기도 합니다. 예: `4456-System_Kind`, `4637-System_Search_Store`, `4631F-System_Search_GatherTime`.
- `F` 가 무슨 뜻인지, 숫자 ID 가 PC 마다 같은지는 공개된 자료가 없습니다.
- 열의 저장 형식은 문자열, 긴 문자열, 긴 이진값, 8·16·32비트 정수(부호 있음·없음), 64비트 통화, 배정밀도 실수 가운데 하나입니다.

분석에 쓸 만한 열은 아래와 같습니다[3].

| 열 | 내용 |
|---|---|
| `WorkID` | 행 번호 |
| `System_Search_GatherTime` | 색인이 이 항목을 처리한 시각. 아래 "시각 해석" 에서 다룹니다. |
| `System_Size` | 크기 |
| `System_FileOwner` | 파일 소유자 |
| `System_ItemPathDisplay` | 전체 경로 |
| `System_ItemType` | 항목 종류 |
| `System_FileAttributes` | 파일 특성 값 |
| `System_Search_AutoSummary` | 자동 요약 글 |

수정·생성 시각 열도 있습니다[3]. 이 열의 정확한 이름은 실제 DB 의 열 목록에서 확인합니다.

### 옛 판 (XP·Vista·7) — `SystemIndex_0A`

주요 열은 아래와 같습니다[1].

| 열 | 형식·내용 |
|---|---|
| `DocID` | 문서 번호 |
| `System_Size` | 64비트 값. XP·7 은 빅엔디언, Vista 는 리틀엔디언 |
| `System_FileAttributes` | 32비트 파일 특성 값 |
| `System_DateModified`, `System_DateCreated`, `System_DateAccessed` | FILETIME 이진값 |
| `System_ItemName`, `System_FileName` | 긴 문자열 |
| `System_Title`, `System_Subject`, `System_Author`, `System_Keywords`, `System_Comment` | 문서 속성 |
| `System_Message_FromAddress`, `System_Message_ToAddress`, `System_Message_Subject`, `System_Message_DateReceived`, `System_Message_HasAttachments` | 메일 속성 |
| `System_Photo_DateTaken`(FILETIME), `System_Music_Artist`, `System_Video_FrameWidth` 등 | 미디어 속성 |
| `System_Contact_FirstName`, `System_Contact_EmailAddress` 등 | 연락처 속성 |
| `System_Search_Rank`, `System_Search_GatherTime`(FILETIME), `System_Search_AutoSummary`(압축된 문자열), `System_Search_HitCount` | 검색 관련 속성 |

### `System_FileAttributes` 값

| 값 | 뜻 |
|---|---|
| `0x1` | 읽기 전용 |
| `0x2` | 숨김 |
| `0x4` | 시스템 |
| `0x10` | 폴더 |
| `0x20` | 보관 |
| `0x200` | 스파스 |
| `0x400` | 재분석 지점 (심볼릭 링크) |
| `0x800` | 압축 |
| `0x1000` | 오프라인 |
| `0x2000` | 본문 색인 안 함 |
| `0x4000` | 암호화 |

값은 여러 비트를 더한 형태입니다. 예를 들어 `0x21` 은 보관(`0x20`)과 읽기 전용(`0x1`)입니다.

### 문자열 압축과 난독화

- Vista 는 문자열 대부분을, XP·7 은 문자열 일부를 압축된 이진값으로 저장합니다[1].
- 이 값은 난독화돼 있습니다. 난독화는 32비트 XOR 마스크 `0x05000113` 에 데이터 크기를 XOR 한 값을 씁니다. 바이트 위치에 따라 마스크를 돌려 씁니다. 정확한 절차는 libyal 문서[1]를 봅니다.
- 난독화를 풀면 첫 바이트가 압축 종류입니다.

| 첫 바이트 | 압축 종류 |
|---|---|
| `0x00` | 런렝스 압축 UTF-16LE |
| `0x01` | 8비트 압축 UTF-16LE |
| `0x02` | 런렝스 + LZXPRESS 허프만 |
| `0x03` | 8비트 + LZXPRESS 허프만 |
| `0x04` | 압축 안 함 |
| `0x06` | LZXPRESS 허프만 |
| `0x08` | 알 수 없음 |

- LZXPRESS 허프만 데이터는 앞 2바이트가 풀었을 때의 크기입니다.
- LZXPRESS 허프만 자체는 [윈도 압축 형식](../../../01-foundations/value-decoding/lznt1-xpress-xpress-huffman.md) 에서 다룹니다.
- 이 압축은 ESE 가 스스로 하는 긴 값 압축과 다릅니다. ESE 긴 값 압축 종류는 7비트 ASCII(1), 7비트 유니코드(2), XPRESS(3), XPRESS9(5), XPRESS10(6), LZ4(7) 입니다. Windows 10·11 의 ESENT 는 잘 줄어드는 값에 LZ4 를 고릅니다.
- 그래서 한 값을 풀 때 ESE 긴 값 압축과 윈도 검색의 압축·난독화를 차례로 풀어야 할 수 있습니다.
- ESE 긴 값은 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다.

### SQLite 판 (Windows 11)

아래 표는 SIDR 소스 코드가 읽는 열 기준입니다[6].

| 표 | SIDR 이 읽는 열 |
|---|---|
| `SystemIndex_1_PropertyStore` | `WorkId`, `ColumnId`, `Value` |
| `SystemIndex_1_PropertyStore_Metadata` | `Id`, `Name`, `StorageType` |

- ESE 판과 달리 속성마다 열이 있지 않고, 한 행에 (문서 번호, 속성 번호, 값) 이 하나씩 들어갑니다.
- `ColumnId` 가 Metadata 의 `Id` 와 짝이 되는지는 공개된 자료가 없습니다.
- Metadata 의 `Name` 에는 점으로 이은 이름이 쓰입니다. SIDR 이 찾는 이름은 `System.Link.TargetUrl`, `System.ItemType`, `System.ComputerName` 입니다.
- SIDR 은 `StorageType` 11 을 문자열로 읽습니다.
- SIDR 은 `StorageType` 12 를, 이름에 `Date`·`Time` 이 들어가면 FILETIME 시각으로 읽고 아니면 정수로 읽습니다.
- SIDR 의 시험 DB 에서는 속성 597개가 매핑됐습니다.
- SIDR 은 보고서 파일 이름에 넣는 호스트 이름을 DB 안의 `System.ComputerName` 에서 가져옵니다.

### 인터넷 기록과 활동 기록

| Windows | 무엇 | 어디에 남나 | 근거 |
|---|---|---|---|
| 10 | IE·Edge 로 연 주소 | 연결할 수 있는 주소면 `ItemPathDisplay`, 아니면 `Activity_ContentUri`·`Activity_Description` | [3] |
| 11 | 인터넷 주소 | `SystemIndex_1_PropertyStore` 의 `System_Link_TargetURL` 속성 | [3] |
| 버전 구분 없음 | 활동 기록 | `System_ItemPathDisplay`, `ActivityHistory_StartTime`, `ActivityHistory_EndTime`, `ActivityHistory_AppId`. 이 네 열로 파일 열기를 보여 줍니다. | [3] |

- SIDR 은 `System.Link.TargetUrl` 이 `http` 로 시작하는 행을 인터넷 기록으로 나눕니다.
- SIDR 은 `System.ItemType` 이 `ActivityHistoryItem` 인 행을 활동 기록으로 나눕니다.
- 활동 기록 자체는 [윈도 타임라인](../activitiescache-db.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것**

- 행이 있으면 색인이 그 항목을 처리한 적이 있습니다.
- `System_ItemPathDisplay` 는 그 항목의 전체 경로를 보여 줍니다.
- `System_Search_GatherTime` 은 수집기 (Gatherer) 가 그 항목의 속성을 마지막으로 넘긴 시각을 보여 줍니다.
- 활동 기록 행은 어떤 앱으로 어떤 파일을 열었는지와 시작·끝 시각을 보여 줍니다.
- 인터넷 기록 행은 IE·Edge 로 연 주소를 보여 줍니다.

**증명하지 못하는 것**

- 활동 기록 행을 빼면, 행이 있다고 해서 사용자가 그 파일을 열었다는 뜻은 아닙니다. 색인은 사용자가 열지 않은 파일도 처리합니다.
- 그 파일이 지금도 디스크에 있다는 뜻도 아닙니다. 이 문제는 [지운 파일·옛 파일 흔적 찾기](deleted-file-traces.md) 에서 다룹니다.
- 수정·생성·접근 시각 열이 지금 파일 시스템의 값과 같다고 볼 수 없습니다. 이 값이 색인 당시의 값을 옮겨 적은 것인지, 파일이 바뀌면 따라 바뀌는지는 공개된 자료가 없습니다.
- `System_FileOwner` 로 기록을 사용자와 잇는 방법은 공개된 자료가 없습니다. [색인 해석 함정](pitfalls.md) 에서 다룹니다.

보고서에는 표·열·값을 그대로 적고, 시각의 뜻을 함께 적습니다.
예: "Windows.edb 의 `SystemIndex_PropertyStore` 에 `WorkID` ○○ 행이 있습니다. 이 행의 `System_ItemPathDisplay` 는 `C:\Users\○○\Documents\계약서.docx` 입니다. `System_Search_GatherTime` 은 ○○ 입니다. 이 시각은 색인이 이 파일의 속성을 처리한 시각입니다." (번호·경로는 설명용 예시입니다.)

## 시각 해석

### `System.Search.GatherTime`

| 항목 | 값 |
|---|---|
| 뜻 | 수집기가 이 문서의 속성을 수집기 플러그인에 마지막으로 넘긴 시각 |
| 형식 ID | `0B63E350-9CCC-11D0-BCDB-00805FCCCE04` |
| 속성 ID | 8 |
| 형식 | DateTime |
| 저장 | 역색인 (Inverted Index) 에 넣지 않고 (`InInvertedIndex=false`) 열로 저장합니다 (`IsColumn=true`). Windows 7~Windows 10 1703 기준입니다[4]. |

- GatherTime 은 사용자가 파일을 연 시각이 아니라 색인이 그 파일을 처리한 시각입니다.
- 처음 색인과 재구성 때 이 값이 어떻게 몰리는지는 [색인 해석 함정](pitfalls.md) 에서 다룹니다.

### 파일 시각 열

- `System_DateModified`·`System_DateCreated`·`System_DateAccessed` 는 FILETIME 이진값입니다.
- XP·7 은 이 값을 빅엔디언으로, Vista 는 리틀엔디언으로 저장합니다. 버전별 표는 [위치와 형식](windows-edb-windows-db.md) 에 있습니다.
- 이 값이 UTC 인지 현지 시각인지는 공개된 자료가 없습니다. 같은 파일의 [마스터 파일 테이블](../../filesystem/mft.md) 시각과 맞춰 확인합니다.
- Windows 11 에서 SIDR 은 이름에 `Date`·`Time` 이 들어간 `StorageType` 12 속성을 FILETIME 으로 읽습니다. 이 규칙은 도구의 판단이고, 명세에 적힌 규칙은 아닙니다.
- FILETIME 을 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

## 함정과 한계

1. **열 이름에 `F` 가 붙습니다.** 실제 열 이름은 `4631F-System_Search_GatherTime` 처럼 숫자 뒤에 `F` 가 붙기도 합니다. 속성 이름을 정확히 맞춰 찾는 도구는 이 표에서 0건을 낼 수 있습니다. 열은 이름 뒷부분으로 찾습니다.
2. **숫자 ID 에 기대지 않습니다.** 숫자 ID 가 PC 마다 같은지는 공개된 자료가 없습니다. 분석 대상마다 열 목록을 새로 읽습니다.
3. **자료마다 속성 이름 표기가 다릅니다.** ESE 판 열 이름은 `System_ItemType` 처럼 밑줄을 씁니다. SQLite 판 Metadata 는 `System.ItemType` 처럼 점을 씁니다. 같은 속성도 LevelBlue 글은 `System_Link_TargetURL`, SIDR 코드는 `System.Link.TargetUrl` 로 적습니다. 이름을 찾을 때 구분 기호와 대소문자를 구분하지 않습니다.
4. **압축과 난독화를 두 번 풀어야 할 수 있습니다.** 윈도 검색의 문자열 압축과 ESE 의 긴 값 압축은 서로 다릅니다. 한쪽만 풀면 글자가 깨져 나옵니다.
5. **긴 값 조각 경계를 틀리면 값이 조용히 망가집니다.** ESE 긴 값은 여러 조각으로 나뉘어 저장됩니다. 조각 경계를 잘못 계산한 파서가 오류 없이 6,000바이트 값을 11,158바이트로 낸 사례가 있습니다. 경로나 요약 글 끝이 이상하면 다른 도구로 다시 읽습니다.
6. **Windows 11 의 열 짝은 알려져 있지 않습니다.** `ColumnId` 와 Metadata 의 `Id` 가 짝인지는 공개된 자료가 없습니다. 도구 결과의 속성 이름이 값과 맞는지 몇 행을 골라 확인합니다.
7. **속성이 이름뿐인 행이 있습니다.** 맞는 필터가 없는 파일은 `System.ItemName` 같은 최소한의 속성만 남습니다. 속성이 적다고 파일이 비어 있다는 뜻은 아닙니다.
8. **Windows 11 DB 가 열리지 않을 수 있습니다.** `AesGcm1 SQLite3` 로 시작하는 파일은 [위치와 형식](windows-edb-windows-db.md) 을 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 **명세로 만든 예시**입니다. 실제 데이터에서 나온 값이 아닙니다.
Windows 7 의 `SystemIndex_0A` 한 행에서 `System_DateModified` 열 값을 꺼냈다고 봅니다.

```
System_DateModified 열 값, 8바이트 (명세로 만든 예시)
01 CD 31 9B 24 C2 07 80
```

1. Windows 7 은 FILETIME 을 빅엔디언으로 저장하므로 앞 바이트부터 그대로 잇습니다.
2. 이은 값은 `0x01CD319B24C20780` 입니다. 10진수로 129,814,506,670,000,000 입니다.
3. 1601-01-01 00:00:00 부터 100나노초 단위로 세면 2012-05-14 06:31:07 입니다.
4. 같은 바이트를 리틀엔디언으로 거꾸로 읽으면 `0x8007C2249B31CD01` 입니다. 이 값은 1601년에서 2만 9천 년쯤 뒤를 가리킵니다. 날짜로 쓸 수 없는 값입니다.
5. 도구가 이런 날짜를 내거나 날짜를 비워 두면 바이트 순서를 먼저 의심합니다.

같은 행의 `System_FileAttributes` 가 `0x2020` 이라고 봅니다.

1. `0x2000` 은 본문 색인 안 함입니다.
2. `0x20` 은 보관입니다.
3. 이 파일은 본문을 색인하지 않도록 표시된 파일입니다. 본문 검색으로 찾지 못한 이유가 여기에 있을 수 있습니다.

### 공개 도구로 한 번

- ESE 판(`Windows.edb`)은 ESEDatabaseView 로 사본을 엽니다. 속성 표의 열 목록을 내보내 `F` 가 붙은 열이 있는지 봅니다.
- WinSearchDBAnalyzer 로도 열 수 있습니다[3].
- SIDR 은 `Windows.edb`(Windows 10 이하)와 `Windows.db`(Windows 11)를 모두 읽습니다. 파일·인터넷 기록·활동 기록 세 가지 보고서를 냅니다.
- Windows 11 의 평문 SQLite `Windows.db` 는 SQLite DB Browser 로 열어 두 표를 직접 볼 수 있습니다.

두 가지 이상 방식으로 열어 아래를 맞춰 봅니다.

- 속성 표의 전체 행 수
- 같은 `WorkID` 의 `System_ItemPathDisplay` 값
- 같은 행의 시각 값. 날짜가 수만 년 뒤로 나오면 바이트 순서를 의심합니다.
- 요약 글·경로 같은 긴 문자열의 길이

## 교차 검증

- [마스터 파일 테이블](../../filesystem/mft.md) — 색인의 경로·크기·시각을 지금 파일 시스템과 맞춰 봅니다.
- [바로가기 파일](../lnk.md) · [점프리스트](../jump-lists.md) · [최근 문서](../recentdocs.md) — 사용자가 파일을 열었다는 기록을 따로 찾습니다.
- [윈도 타임라인](../activitiescache-db.md) — 색인의 활동 기록 행과 맞춰 봅니다.
- [인터넷 익스플로러·옛 엣지](../../browsers/ie-edgehtml/index.md) — 색인에 남은 주소를 브라우저 기록과 맞춰 봅니다.
- [문서 메타데이터](../../embedded-metadata/document-metadata/index.md) · [사진 EXIF](../../embedded-metadata/exif.md) — 색인의 작성자·제목·찍은 날짜를 파일 안의 값과 맞춰 봅니다.
- [아웃룩](../../mail/outlook/index.md) — 색인의 메일 속성을 편지함과 맞춰 봅니다.
- [시스템 기본 정보](../../system-account/os-version-computer-name-install-date-shutdown-t.md) — `System.ComputerName` 을 레지스트리의 컴퓨터 이름과 맞춰 봅니다.
- [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) — 도구마다 행 수와 값이 다를 때 따릅니다.

## 실습

공개 자료(NIST CFReDS 등)에서 Windows 7 이미지와 Windows 10 이미지를 하나씩 골라 풀어 봅니다.

1. 각 이미지의 속성 표 이름은 무엇입니까? 열은 몇 개입니까?
2. Windows 10 이미지의 열 이름 가운데 숫자 뒤에 `F` 가 붙은 열은 몇 개입니까?
3. 사용자 문서 폴더의 파일 하나를 골라 `System_ItemPathDisplay`·`System_Size`·`System_Search_GatherTime` 을 적습니다. 같은 파일의 $MFT 값과 무엇이 같고 무엇이 다릅니까?
4. Windows 7 이미지에서 `System_DateModified` 의 8바이트를 직접 꺼내 빅엔디언으로 풉니다. 도구가 낸 값과 같습니까?
5. `System_FileAttributes` 에 `0x2000` 이 켜진 행이 있습니까? 그 파일은 어떤 종류입니까?
6. 활동 기록 행이나 `http` 로 시작하는 주소 행이 있습니까? 윈도 타임라인·브라우저 기록과 맞습니까?

## 참고 문헌

1. libyal esedb-kb, "Windows Search" (XP~8 기준) — https://raw.githubusercontent.com/libyal/esedb-kb/main/documentation/Windows%20Search.asciidoc
2. Stroz Friedberg, "SIDR — Search Index DB Reporter" README — https://github.com/strozfriedberg/sidr
3. Phalgun Kulkarni·Julia Paluch, "Windows Search Index: The Forensic Artifact You've Been Searching For" (2023-04-26, LevelBlue/Stroz Friedberg 블로그) — https://levelblue.com/blogs/strozfriedberg/windows-search-index-the-forensic-artifact-youve-been-searching-for
4. Microsoft Learn, "System.Search.GatherTime" — https://learn.microsoft.com/en-us/windows/win32/properties/props-system-search-gathertime
5. Microsoft 지원, "Search indexing in Windows" — https://support.microsoft.com/en-us/windows/search-indexing-in-windows-da061c83-af6b-095c-0f7a-4dfecda4d15a
6. Stroz Friedberg, SIDR 소스 `src/sqlite.rs` — https://raw.githubusercontent.com/strozfriedberg/sidr/main/src/sqlite.rs
7. Microsoft Learn, "Indexing process in Windows Search" — https://learn.microsoft.com/en-us/windows/win32/search/-search-indexing-process-overview
