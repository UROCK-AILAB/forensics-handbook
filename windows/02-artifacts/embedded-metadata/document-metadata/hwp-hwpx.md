---
title: "한글 문서"
parent: "문서 메타데이터"
grand_parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 2990
---

# 한글 문서 (HWP·HWPX)

> 상위 페이지: [문서 메타데이터 (Document Metadata)](index.md)

## 한 줄 요약

한글은 문서를 HWP 5.0 과 HWPX 두 형식으로 저장합니다. HWP 5.0 은 OLE 복합 파일이고, 문서 속성은 `\005HwpSummaryInformation` 스트림에 들어 있습니다. HWPX 는 ZIP 파일이고, 문서 속성은 `Contents/content.hpf` 의 metadata 에 들어 있습니다. 두 형식 모두 작성자, 마지막으로 저장한 사람, 만든 시각, 마지막으로 저장한 시각을 적습니다.

> "(관찰)" 은 시간대 KST (UTC+9), 한글 13.0.0.3621 (한컴오피스 2024) 기준입니다. 판마다 다를 수 있습니다.
>
> 시험 파일은 이렇게 만들었습니다. 새 문서에 글을 한 줄 넣었습니다. 문서 정보는 손대지 않았습니다. hwp 로 저장하고, 약 3초 뒤 같은 문서를 hwpx 로 저장했습니다.

## 무엇을 기록하나 · 왜 생기나

HWP 5.0 명세는 "파일-문서 정보-문서 요약" 에서 입력한 내용이 문서 요약 스트림에 들어간다고 적었습니다. 그런데 문서 정보를 입력하지 않은 시험 파일에도 값이 들어 있었습니다. (관찰)

제목 칸에는 본문 첫 줄 글이 들어갔고, 작성자와 마지막으로 저장한 사람 칸에는 한글에 설정된 사용자 이름이 들어갔습니다. 프로그램에 설정된 값이라는 점을 기억합니다. 만든 시각과 마지막으로 저장한 시각은 한글이 저장하면서 적었습니다. (관찰)

문서 속성 말고도 파일 안에 남는 정보가 있습니다.

| 정보 | HWP 5.0 | HWPX |
|---|---|---|
| 문서 속성 (작성자·시각 등) | `\005HwpSummaryInformation` 스트림 | `Contents/content.hpf` |
| 저장한 한글의 판 | 문서 요약의 속성 0x09 (관찰) | `version.xml` |
| 미리보기 글 | `PrvText` 스트림 | `Preview/PrvText.txt` (관찰) |
| 미리보기 그림 | `PrvImage` 스트림 | `Preview/PrvImage.png` (관찰) |
| 암호를 걸었는지 | `FileHeader` 속성 비트 1 | `META-INF/manifest.xml` 의 암호화 정보 |
| 배포용·DRM·전자 서명·변경 추적 여부 | `FileHeader` 속성 비트 | 확인하지 못했습니다 |
| 이전 판 | `DocHistory` 스토리지 | 확인하지 못했습니다 |
| 마지막 커서 위치 | — | `settings.xml` (관찰) |

## 위치와 버전별 차이

| 항목 | HWP 5.0 | HWPX |
|---|---|---|
| 담는 틀 | OLE 복합 파일 | ZIP 파일 |
| 첫 바이트 | `D0 CF 11 E0 A1 B1 1A E1` (OLE 복합 파일 서명) | ZIP 파일. 맨 앞 항목 `mimetype` 의 내용은 `application/hwp+zip` 이었습니다 (관찰) |
| 문서 속성 위치 | `\005HwpSummaryInformation` 스트림 | `Contents/content.hpf` 의 `<opf:metadata>` |
| 시각 표기 | FILETIME (UTC) 과 현지 시각 글자열 | UTC 초 단위 값과 현지 시각 글자열 (관찰) |
| 공개 문서 | 한글과컴퓨터 "한글 문서 파일 형식 5.0" revision 1.3 (2018-11-08) | 국가 표준 KS X 6101 |

HWP 5.0 은 스토리지와 스트림으로 나뉘고, 스트림에 따라 압축하거나 암호화합니다. HWPX 의 표준 이름은 OWPML (Open Word-Processor Markup Language) 이며, 2011년 12월 30일에 KS X 6101 로 제정됐습니다. 한글 몇 판부터 HWPX 를 기본 저장 형식으로 쓰는지는 확인하지 못했습니다.

.hwp 와 .doc 는 첫 바이트가 같습니다. 둘 다 OLE 복합 파일이기 때문입니다. `FileHeader` 스트림이 있고 그 첫 32바이트가 `HWP Document File` 로 시작하면 HWP 5.0 입니다. OLE 복합 파일에서 스트림을 찾는 법은 [OLE 복합 파일](../../../01-foundations/shell-document-formats/compound-file-binary.md) 에 있습니다.

값을 적는 쪽은 Windows 가 아니라 한글입니다. 그래서 Windows 버전보다 저장한 한글의 판을 먼저 확인합니다. 관찰한 hwp 의 파일 버전은 5.1.1.0 이었습니다. hwpx 의 `version.xml` 에도 major 5, minor 1, micro 1 이 적혀 있었습니다. (관찰)

## 구조

### HWP 5.0 의 스트림

명세의 전체 구조 표입니다.

| 스토리지·스트림 | 담는 것 | 명세의 표시 |
|---|---|---|
| `FileHeader` | 파일 인식 정보 | 고정 길이 |
| `DocInfo` | 문서 정보 (레코드 구조) | 압축·암호화 대상 |
| `BodyText/Section0`, `Section1` … | 본문 (레코드 구조) | 압축·암호화 대상 |
| `\005HwpSummaryInformation` | 문서 요약 | 고정 |
| `BinData/BinaryData0` … | 그림·OLE 개체 같은 첨부 바이너리 | 압축 대상 |
| `PrvText` | 미리보기 텍스트 | 유니코드 문자열 |
| `PrvImage` | 미리보기 이미지 | BMP 또는 GIF |
| `DocOptions/_LinkDoc`, `DrmLicense`, `DrmRootSect`, `CertDrmHeader`, `CertDrmInfo`, `DigitalSignature`, `PublicKeyInfo` | 연결 문서 경로·DRM·전자 서명 정보 | |
| `Scripts/DefaultJScript`, `JScriptVersion` | 스크립트 | |
| `XMLTemplate/_SchemaName`, `Schema`, `Instance` | XML 템플릿 | |
| `DocHistory/VersionLog0`, `VersionLog1` …, `HistoryLastDoc` | 문서 이력 관리 | 압축·암호화 대상 |
| `Bibliography` | 참고문헌 (XML) | |

명세는 압축에 zlib 을 쓴다고 적었습니다. 실제 파일과 다른 점은 "함정과 한계" 에 있습니다.

한글 13 이 저장한 시험 hwp 에는 아래 스트림이 있었습니다. (관찰)

```
\005HwpSummaryInformation   (485바이트)
BodyText/Section0
DocInfo
DocOptions/_LinkDoc
FileHeader                  (256바이트)
PrvImage
PrvText
Scripts/DefaultJScript
Scripts/JScriptVersion
```

- 글만 넣은 문서에도 `Scripts` 스트림과 `DocOptions/_LinkDoc` 이 있었습니다. (관찰) 스트림이 있다는 것만으로 스크립트나 연결 문서를 넣었다고 보지 않습니다.
- 문서 이력 관리를 쓰지 않은 이 파일에는 `DocHistory` 가 없었습니다. (관찰)

### FileHeader

`FileHeader` 는 256바이트입니다. 아래 오프셋은 명세 표의 자료형 길이를 차례로 더해 계산한 값입니다.

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0 | 32 | 서명 `HWP Document File` |
| 32 | 4 | 파일 버전. 0xMMnnPPrr 꼴입니다 (예: 5.0.3.0) |
| 36 | 4 | 속성 |
| 40 | 4 | 속성 2 |
| 44 | 4 | 암호화 판 (EncryptVersion) |
| 48 | 1 | 공공누리 라이선스 지원 국가 (6 KOR, 15 US) |
| 49 | 207 | 예약 |

- 파일 버전의 MM·nn 이 다르면 옛 판과 호환되지 않습니다. PP·rr 은 달라도 호환됩니다.
- 암호화 판 값은 0 없음, 1 한글 2.5 이하, 2 한글 3.0 Enhanced, 3 한글 3.0 Old, 4 한글 7.0 이후입니다.
- 속성 2 는 비트 0 이 CCL·공공누리 라이선스 정보, 비트 1 이 복제 제한, 비트 2 가 동일 조건 하 복제 허가입니다.

**속성 (오프셋 36) 의 비트**

| 비트 | 뜻 | 비트 | 뜻 |
|---|---|---|---|
| 0 | 압축 | 9 | 전자 서명 예비 저장 |
| 1 | 암호 설정 | 10 | 공인 인증서 DRM 보안 문서 |
| 2 | 배포용 문서 | 11 | CCL 문서 |
| 3 | 스크립트 저장 | 12 | 모바일 최적화 |
| 4 | DRM 보안 문서 | 13 | 개인 정보 보안 문서 |
| 5 | XMLTemplate 스토리지 있음 | 14 | 변경 추적 문서 |
| 6 | 문서 이력 관리 있음 | 15 | 공공누리 (KOGL) 저작권 문서 |
| 7 | 전자 서명 정보 있음 | 16 | 비디오 컨트롤 포함 |
| 8 | 공인 인증서 암호화 | 17 | 차례 필드 컨트롤 포함 |
| | | 18~31 | 예약 |

관찰한 hwp 의 속성은 0x00000001 이었습니다. 압축 비트만 켜져 있었습니다. (관찰)

### 문서 요약 스트림

`\005HwpSummaryInformation` 은 옛 오피스 문서와 같은 속성 집합 (property set) 구조를 씁니다. 머리글·섹션·속성 목록의 오프셋은 [옛 오피스 문서 속성 (OLE SummaryInformation)](ole-summaryinformation.md) 에 있습니다. 명세도 자세한 설명은 Microsoft 의 Summary Information 문서를 보라고 적었습니다.

관찰한 hwp 에서 섹션의 형식 식별자 (FMTID) 는 `9FA2B660-1061-11D4-B4C6-006097C09D8C` 였습니다. (관찰)

명세의 속성 표와 관찰한 값은 아래와 같습니다.

| ID | 명세 이름 | 뜻 | 관찰한 값 |
|---|---|---|---|
| 0x02 | Title | 제목 | 본문 첫 줄 글 |
| 0x03 | Subject | 주제 | |
| 0x04 | Author | 작성자 | 한글에 설정된 사용자 이름 |
| 0x05 | Keywords | 키워드 | |
| 0x06 | Comments | 설명 | |
| 0x08 | Last Saved By | 마지막으로 저장한 사람 | 한글에 설정된 사용자 이름 |
| 0x09 | Revision Number | 개정 번호 | `13, 0, 0, 3621 WIN32LEWindows_10` |
| 0x0B | Last Printed | 마지막으로 인쇄한 시각 | FILETIME 0 |
| 0x0C | Create Time/Date | 만든 시각 | 2026-09-23 11:30:07.026 UTC |
| 0x0D | Last saved Time/Date | 마지막으로 저장한 시각 | 2026-09-23 11:30:10.35 UTC |
| 0x0E | Number of Pages | 쪽 수 | 0 |
| 0x14 | Date String (HWPPIDSI_DATE_STR) | 날짜 글자열 | `2026년 9월 23일 수요일 오후 8:30:07` |
| 0x15 | Para Count (HWPPIDSI_PARACOUNT) | 문단 수 | 0 |

- 명세는 FILETIME 값이 UTC 라고 적었습니다.
- 0x14 와 0x15 는 한글에만 있는 속성입니다. 명세의 형식은 0x14 가 VT_LPSTR, 0x15 가 VT_I4 입니다.
- 옛 오피스 표에 있는 0x07 (Template), 0x0A (Total Editing Time), 0x12 (프로그램 이름) 같은 속성은 한글 명세 표에 없습니다.
- 속성 목록 맨 끝에 속성 ID 0x00, 값 형식 0x0001 인 항목이 하나 더 있었습니다. (관찰) 이 항목의 뜻은 확인하지 못했습니다.

### 문서 이력 관리 (DocHistory)

한글 2005 (6.5.0.724), 문서 형식 5.0.1.7 부터 지원하며, 한글 2005~2007 에서는 이름이 "버전 비교" 였습니다. 메뉴 "파일-문서 이력 관리" 에서 이력을 만들면 `DocHistory` 스토리지 안의 `VersionLog%d` 스트림에 하나씩 들어가고, 이 스트림들은 압축하고 암호화합니다. 최종 문서는 `HistoryLastDoc` 스트림에 들어갑니다. `FileHeader` 속성 비트 6 이 켜져 있으면 이력이 있는 문서입니다.

이력 레코드의 태그는 아래와 같습니다.

| 태그 | 뜻 |
|---|---|
| 0x10 | 아이템 시작. flag 는 0x01 버전, 0x02 날짜, 0x04 작성자, 0x08 설명, 0x10 Diff Data, 0x40 Lock 입니다. option 0x00000001 은 저장할 때 자동 저장입니다 |
| 0x11 | 아이템 끝 |
| 0x20 | 버전 (DWORD) |
| 0x21 | 날짜 (SYSTEMDATE) |
| 0x22 | 작성자 (WCHAR) |
| 0x23 | 설명 (WCHAR) |
| 0x30 | 비교 정보 DiffML (WCHAR) |
| 0x31 | 가장 마지막 최근 문서 HWPML (WCHAR) |

0x21 날짜가 UTC 인지 현지 시각인지는 확인하지 못했습니다.

### HWPX 의 ZIP 구성

한컴 테크 블로그가 설명한 구성입니다.

| ZIP 안 경로 | 담는 것 |
|---|---|
| `mimetype` | HWPX 임을 확인하는 서명 |
| `version.xml` | OWPML 판과 저장 환경 |
| `settings.xml` | 커서 위치 같은 설정 |
| `META-INF/container.xml` | 주요 파일 목록 |
| `META-INF/manifest.xml` | 암호화한 파일이면 암호화 정보 |
| `META-INF/container.rdf` | 구성 파일 목록 |
| `Contents/content.hpf` | 패키징 파일 목록 (OPF 표준). 작성자·제목·생성 날짜 같은 메타데이터 |
| `Contents/header.xml` | 글자 모양·문단 모양 같은 서식 |
| `Contents/section0.xml` | 구역별 본문 |
| `BinData/` | 이미지·OLE 개체 |
| `Preview/PrvImage` | 미리보기 이미지 |

한글 13 이 저장한 hwpx 의 ZIP 항목은 아래 순서였습니다. (관찰)

```
mimetype                  (압축 안 함)
version.xml               (압축 안 함)
Contents/header.xml
Contents/section0.xml
Preview/PrvText.txt
settings.xml
Preview/PrvImage.png      (압축 안 함)
META-INF/container.rdf
Contents/content.hpf
META-INF/container.xml
META-INF/manifest.xml
```

- 표시하지 않은 항목은 deflate 로 압축했습니다. (관찰)
- 그림이 든 문서에는 `BinData/image1.PNG` 같은 항목이 더 있었습니다. 이 그림도 압축하지 않았습니다. (관찰)
- `container.xml` 의 rootfile 은 `Contents/content.hpf` (application/hwpml-package+xml), `Preview/PrvText.txt` (text/plain), `META-INF/container.rdf` (application/rdf+xml) 세 개였습니다. (관찰)
- 암호를 걸지 않은 문서의 `manifest.xml` 은 빈 `<odf:manifest/>` 였습니다. (관찰)
- `settings.xml` 에는 마지막 커서 위치 `<ha:CaretPosition listIDRef=… paraIDRef=… pos=…/>` 가 있었습니다. (관찰) 이 값을 포렌식에 쓸 수 있는지는 확인하지 못했습니다.

`version.xml` 의 내용은 아래와 같았습니다. (관찰)

```xml
<hv:HCFVersion tagetApplication="WORDPROCESSOR" major="5" minor="1" micro="1" buildNumber="0" os="1" xmlVersion="1.5" application="Hancom Office Hangul" appVersion="13, 0, 0, 3621 WIN32LEWindows_10"/>
```

`appVersion` 은 hwp 의 속성 0x09 와 같은 글자열입니다. (관찰)

### content.hpf 의 metadata

`<opf:metadata>` 안에는 아래 항목이 있었습니다. (관찰)

- `opf:title`: 본문 첫 줄 글이 들어 있었습니다.
- `opf:language`: `ko` 였습니다.
- `opf:meta` 여덟 개: `name` 이 `creator`, `subject`, `description`, `lastsaveby`, `CreatedDate`, `ModifiedDate`, `date`, `keyword` 였습니다. 모두 `content="text"` 가 붙어 있었습니다.

시각 항목의 값은 아래와 같았습니다. (관찰)

| 항목 | 값 | 표기 |
|---|---|---|
| `CreatedDate` | `2026-09-23T11:30:07Z` | UTC, 초 단위 |
| `ModifiedDate` | `2026-09-23T11:30:10Z` | UTC, 초 단위 |
| `date` | `2026년 9월 23일 수요일 오후 8:30:07` | 현지 시각 글자열. hwp 의 0x14 와 같은 값 |

- 다른 사람이 한글 13.0.0.3066 으로 저장한 hwpx 도 같은 항목이 있었습니다. (관찰)
- `content.hpf` 에는 이력 이름공간 `hhs` (`http://www.hancom.co.kr/hwpml/2011/history`) 가 선언돼 있었습니다. (관찰) HWPX 에서 문서 이력을 어디에 어떻게 두는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것**

- 파일 안에 작성자·마지막으로 저장한 사람·만든 시각·마지막으로 저장한 시각이 적혀 있습니다.
- 사용자 이름 칸에는 저장한 한글에 설정돼 있던 사용자 이름이 들어갑니다. (관찰)
- hwp 의 0x09 와 hwpx 의 `version.xml` 에 저장한 한글의 판이 남습니다. (관찰)
- `FileHeader` 속성 비트로 암호·배포용·DRM·전자 서명·변경 추적·문서 이력이 있는 문서인지 가릴 수 있습니다.
- `DocHistory` 가 있으면 이전 판이 파일 안에 남아 있을 수 있습니다.
- `PrvText` 에는 본문 글이 유니코드로 들어 있었습니다. (관찰) 본문 스트림의 압축을 풀지 않고도 글을 확인할 수 있었습니다. 긴 문서에서 `PrvText` 에 본문이 어디까지 들어가는지는 확인하지 못했습니다.

**증명하지 못하는 것**

- 그 이름의 사람이 문서를 썼다는 것. 사용자 이름은 프로그램 설정값입니다. 이 문제는 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- 제목이 사용자가 붙인 제목이라는 것. 문서 정보를 입력하지 않아도 본문 첫 줄이 제목 칸에 들어갔습니다. (관찰)
- 0x09 가 고친 횟수라는 것. 관찰한 파일의 0x09 에는 프로그램 판 글자열이 있었습니다.
- 쪽 수·문단 수가 0 이면 빈 문서라는 것. 한 줄짜리 시험 문서에서도 둘 다 0 이었습니다. (관찰)
- 스트림이 있으면 그 기능을 썼다는 것. 글만 넣은 문서에도 `Scripts` 스트림이 있었습니다. (관찰)
- 다른 이름으로 저장한 hwpx 의 `ModifiedDate` 가 그 파일을 쓴 시각이라는 것. 아래 "시각 해석" 을 봅니다.
- 값이 저장한 뒤로 바뀌지 않았다는 것. 스트림과 XML 속 값은 다른 도구로 고쳐 쓸 수 있습니다.

보고서 문장은 기록이 말하는 만큼만 씁니다.

- 쓰지 않을 문장: "A 가 2026년 9월 23일 오후 8시 30분에 이 문서를 작성했다."
- 쓸 문장: "plan.hwp 의 `\005HwpSummaryInformation` 스트림에서 Create Time/Date (0x0C) 값은 2026-09-23 11:30:07 UTC 이다. 같은 스트림의 Author (0x04) 칸에는 'A' 가 적혀 있다." (예시 문장입니다.)

## 시각 해석

**hwp 의 0x0C·0x0D**

- FILETIME 이고 UTC 입니다. 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- 1초보다 작은 단위까지 적혀 있었습니다. (관찰)
- 0x0D 는 11:30:10.35 UTC 였습니다. 같은 파일의 파일 시스템 수정 시각은 11:30:10.729 UTC 였습니다. (관찰) 두 값은 1초 안쪽으로 가까웠습니다.
- 다른 형식과 정밀도를 견준 표는 [문서 메타데이터 (Document Metadata)](index.md) 에 있습니다.

**hwp 의 0x0B**

- 인쇄한 적 없는 시험 파일의 0x0B 는 FILETIME 0 이었습니다. (관찰)
- FILETIME 0 을 날짜로 풀면 1601-01-01 00:00:00 UTC 입니다. 도구가 이 날짜를 보여 주면 인쇄 시각으로 옮기지 않습니다.

**날짜 글자열 (hwp 0x14, hwpx `date`)**

- 현지 시각 글자열이고 시간대 표기가 없습니다. (관찰)
- 관찰한 값은 0x0C (만든 시각, UTC) 에 9시간을 더한 값이었습니다. 0x0D (마지막으로 저장한 시각) 와는 맞지 않았습니다. (관찰)
- 다른 사람이 저장한 hwpx 도 `CreatedDate` 03:51:47Z 와 `date` "오후 12:51:47" 이 9시간 차이였습니다. (관찰)
- 그래서 이 글자열과 UTC 값의 차이로 저장한 PC 의 시간대를 짐작할 수 있습니다. 짐작한 값은 [시간대 설정](../../system-account/time-zone.md) 과 맞춰 봅니다.
- 글자열은 "오전·오후" 가 붙은 12시간제입니다. 24시간제로 옮길 때 틀리지 않게 봅니다.

**hwpx 의 `CreatedDate`·`ModifiedDate`**

- UTC 이고 끝에 `Z` 가 붙습니다. 초 단위까지만 적혀 있었습니다. (관찰)
- 시험 hwpx 는 hwp 를 저장하고 약 3초 뒤 다른 이름으로 저장했습니다. 그런데 hwpx 의 `CreatedDate`·`ModifiedDate` 는 hwp 의 0x0C·0x0D 와 초까지 같았습니다. (관찰)
- 그래서 `ModifiedDate` 를 그 hwpx 파일을 쓴 시각으로 읽지 않습니다. 파일 시스템 시각과 나란히 적어 둡니다.
- hwpx 의 ZIP 항목 시각은 1980-01-01 00:00:00 이었습니다. (관찰) 이 칸으로는 저장 시각을 알 수 없습니다.

## 함정과 한계

- **명세 본문의 스트림 이름에 오타가 있습니다.** 명세 본문에는 `\005HwpSummaryInfomation` (r 빠짐) 으로 적혀 있습니다. 실제 파일의 이름은 `\005HwpSummaryInformation` 이었습니다. (관찰) 이름으로 스트림을 찾는 도구를 만들 때 실제 이름을 씁니다.
- **글자열 형식이 명세와 다릅니다.** 명세 표는 글자열 속성을 VT_LPSTR 로 적었습니다. 관찰한 파일의 글자열 속성은 VT_LPWSTR (0x1F, 유니코드) 이었습니다. (관찰) 값 앞 4바이트의 값 형식을 보고 풉니다. 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 을 봅니다.
- **본문 압축은 zlib 머리글이 없었습니다.** 명세는 zlib 을 쓴다고 적었습니다. 관찰한 `BodyText/Section0` 은 zlib 머리글이 없는 raw deflate 였습니다. Python zlib 에서 wbits=15 로 풀면 "incorrect header check" 오류가 났습니다. wbits=-15 로는 풀렸습니다. (관찰)
- **미리보기 그림 형식이 명세와 다릅니다.** 명세는 BMP 또는 GIF 라고 적었습니다. 관찰한 `PrvImage` 는 PNG (`89 50 4E 47`) 였습니다. (관찰)
- **0x09 는 개정 번호가 아니었습니다.** 표 이름은 Revision Number 입니다. 그러나 관찰한 값은 프로그램 판 글자열이었습니다. (관찰)
- **인쇄하지 않아도 0x0B 칸이 있습니다.** 한글 13 은 인쇄하지 않은 문서에도 0x0B 를 0 으로 썼습니다. (관찰) 칸이 있다는 것만으로 인쇄했다고 보지 않습니다. Word 가 이 칸을 다루는 방식은 [옛 오피스 문서 속성](ole-summaryinformation.md) 에 있습니다.
- **시스템 판 칸을 믿지 않습니다.** 관찰한 문서 요약 스트림 머리글의 시스템 판 칸은 0x0000000D 였습니다. (관찰) 위 16비트가 0x0000 이므로 libyal 문서의 표대로 읽으면 Win16 입니다. Windows 11 에서 저장한 파일이므로 이 칸으로 플랫폼을 가리지 않습니다.
- **`version.xml` 의 속성 이름 철자가 틀립니다.** `targetApplication` 이 아니라 `tagetApplication` 으로 적혀 있었습니다. (관찰) 바른 철자로 찾는 도구는 이 값을 놓칩니다.
- **암호 문서에서 무엇이 읽히는지 확인하지 못했습니다.** 명세 표에서 암호화 대상으로 적힌 것은 `DocInfo`, `BodyText`, `DocHistory` 입니다. 문서 요약 스트림은 암호화 대상으로 적혀 있지 않습니다. 암호를 건 실제 파일에서 문서 요약을 읽을 수 있는지는 확인하지 못했습니다.

## 직접 분석해 보기

### 헥스로 한 번

**FileHeader 앞 40바이트**

아래 바이트는 명세의 `FileHeader` 구조에 관찰한 값 (파일 버전 5.1.1.0, 속성 0x00000001) 을 넣어 만든 예시입니다.

```
오프셋    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  48 57 50 20 44 6F 63 75  6D 65 6E 74 20 46 69 6C   HWP Document Fil
00000010  65 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00   e...............
00000020  00 01 01 05 01 00 00 00                            ........
```

| 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0x00 | `48 57 … 6C 65` | 서명 `HWP Document File` (17바이트). 뒤를 0 으로 채워 32바이트를 맞춥니다 |
| 0x20 | `00 01 01 05` | 파일 버전. 리틀 엔디언이라 0x05010100 이고, 5.1.1.0 입니다 |
| 0x24 | `01 00 00 00` | 속성 0x00000001. 비트 0 (압축) 만 켜져 있습니다 |

비트 0 이 켜져 있으므로 본문 스트림을 풀어야 본문 레코드가 보입니다. 비트 1·2·4·6·7·14 가 켜져 있으면 암호·배포용·DRM·이력·전자 서명·변경 추적 문서입니다.

**문서 요약 스트림 앞 48바이트**

아래 바이트는 속성 집합 머리글 구조에 관찰한 값을 넣어 만든 예시입니다. 관찰한 파일의 머리도 이와 같았습니다. (관찰)

```
오프셋    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  FE FF 00 00 0D 00 00 00  60 B6 A2 9F 61 10 D4 11
00000010  B4 C6 00 60 97 C0 9D 8C  01 00 00 00 60 B6 A2 9F
00000020  61 10 D4 11 B4 C6 00 60  97 C0 9D 8C 30 00 00 00
```

| 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0x00 | `FE FF` | 바이트 순서 칸 |
| 0x02 | `00 00` | 형식 칸 |
| 0x04 | `0D 00 00 00` | 시스템 판 0x0000000D |
| 0x08 | `60 B6 A2 9F … 9D 8C` | 클래스 식별자. FMTID 와 같은 값이었습니다 |
| 0x18 | `01 00 00 00` | 섹션 1개 |
| 0x1C | `60 B6 A2 9F … 9D 8C` | FMTID `9FA2B660-1061-11D4-B4C6-006097C09D8C` |
| 0x2C | `30 00 00 00` | 섹션 위치 0x30 |

- FMTID 는 앞 세 부분의 바이트 순서를 뒤집어 적습니다. `9FA2B660` 이 `60 B6 A2 9F` 로, `1061` 이 `61 10` 으로, `11D4` 가 `D4 11` 로 적혔습니다. GUID 바이트 순서는 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에 있습니다.

섹션부터는 [옛 오피스 문서 속성](ole-summaryinformation.md) 의 헥스 절과 같은 순서로 따라갑니다.

1. 오프셋 0x30 에서 섹션 머리 8바이트를 읽습니다.
2. 속성 목록에서 속성 ID 0x0C 를 찾습니다.
3. 값 위치에 0x30 을 더해 값으로 갑니다.
4. 값 형식이 0x40 (VT_FILETIME) 인지 보고 뒤 8바이트를 FILETIME 으로 풉니다.
5. 0x14 도 같은 방법으로 찾습니다. 값 형식이 0x1F 이면 유니코드 글자열로 풉니다.

### 공개 도구로 한 번

Python 의 olefile 과 표준 라이브러리로 읽을 수 있습니다. 사본에만 씁니다.

**HWP 5.0**

```python
import olefile, zlib

ole = olefile.OleFileIO("copy.hwp")
print(ole.listdir())                                        # 스트림 목록

hdr = ole.openstream("FileHeader").read()
print(hdr[:32].rstrip(b"\0"))                               # 서명
print(hex(int.from_bytes(hdr[32:36], "little")))            # 파일 버전
print(hex(int.from_bytes(hdr[36:40], "little")))            # 속성 비트

props = ole.getproperties("\x05HwpSummaryInformation", convert_time=True)
for pid in sorted(props):
    print(hex(pid), props[pid])

print(ole.openstream("PrvText").read().decode("utf-16-le"))  # 미리보기 글

raw = ole.openstream("BodyText/Section0").read()
body = zlib.decompress(raw, -15)                            # raw deflate. 결과는 레코드 구조입니다
```

**HWPX**

```python
import zipfile

z = zipfile.ZipFile("copy.hwpx")
for info in z.infolist():
    print(info.filename, info.compress_type, info.date_time)  # 0 = 압축 안 함, 8 = deflate
print(z.read("mimetype"))
print(z.read("version.xml").decode("utf-8", errors="replace"))
print(z.read("Contents/content.hpf").decode("utf-8", errors="replace"))
```

1. 첫 바이트로 OLE 복합 파일인지 ZIP 파일인지 가립니다.
2. HWP 는 `FileHeader` 서명과 속성 비트를 먼저 봅니다. 비트 1·2·4·6·7·14 가 켜져 있는지 적습니다.
3. 0x0C·0x0D·0x14 를 파일 시스템 시각과 나란히 적습니다.
4. HWPX 는 `content.hpf` 의 `CreatedDate`·`ModifiedDate`·`date` 와 `version.xml` 의 `appVersion` 을 적습니다.
5. 0x0C 를 헥스로 직접 푼 값과 도구 결과를 맞춰 봅니다. 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 따릅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [옛 오피스 문서 속성 (OLE SummaryInformation)](ole-summaryinformation.md) | 같은 속성 집합 구조를 쓰는 .doc 의 값 모양 |
| [오피스 문서 속성 (OOXML docProps)](ooxml-docprops.md) | ZIP 안 XML 에 속성을 두는 docx 의 값 모양 |
| [마스터 파일 테이블](../../filesystem/mft.md) | 파일 시스템 생성·수정 시각과 0x0C·0x0D 의 차이 |
| [USN 변경 저널](../../filesystem/usnjrnl.md) | 파일이 이 볼륨에서 만들어지고 바뀐 기록 |
| [시간대 설정](../../system-account/time-zone.md) | 날짜 글자열과 UTC 값의 차이 |
| [최근 문서](../../file-folder-usage/recentdocs.md)·[바로가기 파일](../../file-folder-usage/lnk.md)·[점프리스트](../../file-folder-usage/jump-lists.md) | 같은 파일을 연 다른 기록 |
| [인쇄 흔적](../../external-devices/print-spooler-spl-shd.md)·[인쇄 이벤트](../../event-logs/printservice-307.md) | 0x0B 가 0 이 아닐 때 그 무렵의 인쇄 기록 |
| [다운로드 출처 표시](../../filesystem/zone-identifier.md) | 문서를 내려받았는지 |

시나리오로 이어서 보려면 [이 문서의 날짜를 믿을 수 있나](../../../04-scenarios/activity/document-date-verification.md) 와 [이 파일은 어디서 왔나](../../../04-scenarios/activity/file-origin.md) 를 봅니다.

## 실습

한글을 설치한 가상 머신에서 직접 해 봅니다.

1. 새 문서에 글을 한 줄 넣고 hwp 와 hwpx 로 저장합니다. 제목 칸에 무엇이 들어가나요?
2. "파일-문서 정보-문서 요약" 에 제목을 넣고 다시 저장합니다. 0x02 와 `opf:title` 이 어떻게 바뀌나요?
3. 문서를 닫고 몇 분 뒤 다시 열어 고친 다음 저장합니다. 0x14 는 만든 시각을 유지하나요, 저장 시각으로 바뀌나요?
4. PC 시간대를 바꾼 뒤 새 문서를 저장합니다. 0x14 와 0x0C 의 차이가 따라 바뀌나요?
5. 문서를 인쇄한 뒤 저장합니다. 0x0B 가 0 에서 바뀌나요? 인쇄 이벤트 시각과 맞나요?
6. "파일-문서 이력 관리" 로 이력을 두 개 만들고 저장합니다. `DocHistory` 에 스트림이 몇 개 생기나요? `FileHeader` 속성 비트 6 이 켜지나요?
7. 암호를 건 hwp 에서 문서 요약 스트림을 읽을 수 있나요? 암호를 건 hwpx 의 `manifest.xml` 은 어떻게 바뀌나요?
8. 결과로 보고서 문장을 하나 씁니다. "작성했다" 가 아니라 기록이 말하는 만큼만 씁니다.

## 참고 문헌

- 한글과컴퓨터, "한글 문서 파일 형식 5.0" revision 1.3 (2018-11-08). https://cdn.hancom.com/link/docs/한글문서파일형식_5.0_revision1.3.pdf
- 한컴 테크 블로그, HWPX 형식 구조 소개 글. https://tech.hancom.com/hwpxformat/
- libyal libolecf, "OLE Compound File format" (속성 집합 스트림 절). https://raw.githubusercontent.com/libyal/libolecf/main/documentation/OLE%20Compound%20File%20format.asciidoc
