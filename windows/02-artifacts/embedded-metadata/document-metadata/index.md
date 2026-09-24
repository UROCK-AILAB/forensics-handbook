# 문서 메타데이터 (Document Metadata)

## 한 줄 요약

문서 메타데이터 (document metadata) 는 문서를 저장한 프로그램이 파일 안에 함께 적는 속성입니다. 작성자, 마지막으로 저장한 사람, 만든 시각, 저장한 시각, 저장한 프로그램 같은 값이 들어갑니다. 형식마다 값이 들어가는 곳과 시각을 적는 방식이 다릅니다.

> 이 페이지에서 "(관찰)" 을 붙인 내용은 PC 한 대에서 직접 만든 시험 파일을 보고 확인한 것입니다. 확인 범위: Windows 11 (빌드 26200), 시간대 KST (UTC+9), Word 16.0 빌드 16.0.20326 (Microsoft 365), 한글 13.0.0.3621 (한컴오피스 2024), pypdf 6.19.0. 한 대·한 판에서 본 결과라 다른 판에서도 같다고 장담하지 못합니다.

## 왜 중요한가

- 값이 파일 내용 안에 있습니다. 그래서 파일 시스템 시각과 따로 견줄 수 있습니다.
- 두 시각은 서로 다를 수 있습니다. Microsoft 의 Summary Information 문서는 파일을 옮기는 방식 (예: BBS 내려받기) 에 따라 파일 시스템 쪽 시각이 제대로 남지 않을 수 있다고 적었습니다. XMP 명세도 문서 속 만든 시각이 파일 시스템 생성 시각과 같을 필요가 없다고 적었습니다.
- 작성자와 마지막으로 저장한 사람 칸에는 저장한 프로그램에 설정된 사용자 이름이 들어갔습니다. (관찰) 어느 프로그램 설정으로 저장했는지 좁히는 단서가 됩니다.
- 저장한 프로그램의 이름과 판이 남습니다.
- 고치기 전 판이 파일 안에 남는 구조가 있습니다. PDF 증분 저장은 고친 내용을 파일 끝에 덧붙이고 옛 내용을 지우지 않습니다. 한글의 문서 이력 관리는 이력을 파일 안의 `DocHistory` 스토리지에 둡니다.
- docx 본문에는 편집 세션 식별자 (RSID) 가 붙습니다. 본문의 어느 부분을 같은 편집 세션에 저장했는지 읽을 수 있습니다.
- PDF 는 같은 종류의 값을 두 곳에 적습니다. 두 값이 어긋나면 한쪽만 고친 도구의 흔적일 수 있습니다.

증명하지 못하는 것도 분명합니다.

- 이름 칸의 사람이 문서를 썼다는 것. 사용자 이름은 프로그램 설정값입니다.
- 값이 처음 적힌 그대로라는 것. 파일 속 값은 다른 도구로 고쳐 쓸 수 있습니다.
- 어떤 개수가 저장 횟수라는 것. RSID 개수와 `%%EOF` 개수는 저장 횟수와 맞지 않았습니다. 까닭은 [편집 흔적 식별자 (RSID)](rsid.md) 와 [PDF 증분 저장과 이전 판 복원](incremental-update.md) 에 있습니다.
- 확장자가 실제 형식이라는 것. 확장자가 .doc 인 RTF 파일이 있었습니다. (관찰) 확장자보다 첫 바이트를 먼저 봅니다.

## 한눈에 보기

> 그림 자리: docx·doc·hwp·hwpx·PDF 파일을 나란히 놓고, 파일마다 메타데이터가 들어가는 자리를 표시한 그림

### 형식별 위치

| 형식 | 담는 틀 | 파일 첫 부분 | 메타데이터 위치 | 자세히 |
|---|---|---|---|---|
| docx 같은 OOXML | ZIP 파일 | ZIP | `docProps/core.xml`, `docProps/app.xml` | [오피스 문서 속성](ooxml-docprops.md) |
| .doc 같은 옛 오피스 | OLE 복합 파일 | `D0 CF 11 E0 A1 B1 1A E1` | `\005SummaryInformation`, `\005DocumentSummaryInformation` 스트림 | [옛 오피스 문서 속성](ole-summaryinformation.md) |
| HWP 5.0 | OLE 복합 파일 | `D0 CF 11 E0 A1 B1 1A E1` | `\005HwpSummaryInformation` 스트림 | [한글 문서](hwp-hwpx.md) |
| HWPX | ZIP 파일 | ZIP | `Contents/content.hpf` 의 metadata | [한글 문서](hwp-hwpx.md) |
| PDF | PDF | `%PDF-` 뒤에 판 번호 (예: `%PDF-1.7`) | 트레일러가 가리키는 정보 사전 (Info), 카탈로그가 가리키는 XMP 스트림 | [PDF 정보 사전과 XMP](pdf-info-xmp.md) |

- 시험 .doc 와 .hwp 는 모두 OLE 복합 파일 서명으로 시작했습니다. (관찰)
- Word 가 내보낸 PDF 는 `%PDF-1.7` 로 시작했습니다. (관찰)
- 이 값들은 Windows 가 아니라 문서를 저장한 프로그램이 적습니다. 그래서 Windows 버전보다 저장한 프로그램과 그 판을 먼저 확인합니다.

### 시각을 적는 방식

같은 PC 에서 만든 시험 파일의 시각 표기입니다. (관찰)

| 형식과 위치 | 저장한 프로그램 | 기준 | 정밀도 |
|---|---|---|---|
| docx `core.xml` | Word 16 | UTC. 끝에 `Z` | 분. 초는 항상 00 |
| .doc SummaryInformation | Word 16 | FILETIME, UTC | 초는 00 |
| hwp HwpSummaryInformation | 한글 13 | FILETIME, UTC. 현지 시각 글자열이 따로 있음 | 1초보다 작은 단위까지 |
| hwpx `content.hpf` | 한글 13 | UTC. 현지 시각 글자열이 따로 있음 | 초 |
| PDF 정보 사전 | Word 16 의 PDF 로 내보내기 | 현지 시각과 `+09'00'` | 초 |
| PDF XMP | Word 16 의 PDF 로 내보내기 | 현지 시각과 `+09:00` | 초 |

- docx 와 hwpx 의 ZIP 항목 시각은 모두 1980-01-01 00:00:00 이었습니다. (관찰) ZIP 항목 시각으로는 저장 시각을 알 수 없습니다.
- FILETIME 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- 현지 시각으로 적힌 값은 [시간대 설정](../../system-account/time-zone.md) 과 함께 봅니다.

### 알려 주는 것

| 알 수 있는 것 | 어디에 남나 | 자세히 |
|---|---|---|
| 작성자·마지막으로 저장한 사람 | docx `dc:creator`·`cp:lastModifiedBy`, .doc·hwp 속성 0x04·0x08, hwpx `creator`·`lastsaveby`, PDF `Author` | 형식별 페이지 |
| 만든 시각·마지막으로 저장한 시각 | docx `dcterms:created`·`dcterms:modified`, .doc·hwp 속성 0x0C·0x0D, hwpx `CreatedDate`·`ModifiedDate`, PDF `CreationDate`·`ModDate` 와 `xmp:CreateDate`·`xmp:ModifyDate` | 형식별 페이지 |
| 저장한 프로그램과 판 | docx `app.xml`, .doc 속성 0x12, hwp 속성 0x09, hwpx `version.xml`, PDF `Producer`·`Creator` | 형식별 페이지 |
| 마지막으로 인쇄한 시각 | .doc·hwp 속성 0x0B | [옛 오피스 문서 속성](ole-summaryinformation.md), [한글 문서](hwp-hwpx.md) |
| 같은 편집 세션에 저장한 부분 | docx 의 RSID | [편집 흔적 식별자 (RSID)](rsid.md) |
| 고치기 전 판 | PDF 끝에 덧붙은 부분, 한글의 `DocHistory` | [PDF 증분 저장과 이전 판 복원](incremental-update.md), [한글 문서](hwp-hwpx.md) |
| 한쪽만 고친 흔적 | PDF 정보 사전과 XMP 의 어긋남 | [PDF 정보 사전과 XMP](pdf-info-xmp.md) |

## 읽는 순서

1. [오피스 문서 속성 (OOXML docProps)](ooxml-docprops.md) — docx 의 `core.xml`·`app.xml` 을 읽습니다. Word 16 이 시각을 분 단위 UTC 로 적는 점을 다룹니다.
2. [옛 오피스 문서 속성 (OLE SummaryInformation)](ole-summaryinformation.md) — .doc 의 속성 집합 스트림 구조와 속성 ID 표를 다룹니다. 한글 HWP 도 이 구조를 쓰므로 한글 문서보다 먼저 읽습니다.
3. [편집 흔적 식별자 (RSID)](rsid.md) — docx 본문에 붙는 편집 세션 식별자를 읽습니다. RSID 개수를 저장 횟수로 읽을 수 없는 까닭도 다룹니다.
4. [PDF 정보 사전과 XMP (PDF Info·XMP)](pdf-info-xmp.md) — PDF 의 두 메타데이터 자리를 읽고 서로 맞춰 봅니다. 두 곳의 시각 표기 차이도 다룹니다.
5. [PDF 증분 저장과 이전 판 복원 (Incremental Update)](incremental-update.md) — 파일 끝에 덧붙은 부분을 찾아 고치기 전 판을 되살립니다. `%%EOF` 개수를 편집 횟수로 읽지 않는 까닭도 다룹니다.
6. [한글 문서 (HWP·HWPX)](hwp-hwpx.md) — HWP 5.0 의 문서 요약 스트림과 `FileHeader`, HWPX 의 `content.hpf` 를 읽습니다. 명세와 실제 파일이 다른 곳도 모았습니다.

## 함께 볼 페이지

- [이 문서의 날짜를 믿을 수 있나](../../../04-scenarios/activity/document-date-verification.md) — 문서 속 시각을 파일 시스템 시각, 사용 흔적과 함께 읽는 순서입니다.
- [이 파일은 어디서 왔나](../../../04-scenarios/activity/file-origin.md) — 문서를 이 PC 에서 만들었는지, 밖에서 들여왔는지 가립니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) — 사용자 이름 칸을 사람과 잇기 전에 봅니다.
- [OLE 복합 파일](../../../01-foundations/shell-document-formats/compound-file-binary.md) — .doc 와 .hwp 를 담는 틀입니다.
- [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) · [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) — 코드 페이지와 UTF-16 글자열, FMTID 의 바이트 순서를 풉니다.
- [마스터 파일 테이블](../../filesystem/mft.md) · [USN 변경 저널](../../filesystem/usnjrnl.md) — 파일 시스템 쪽 시각과 변경 기록입니다.
- [오피스 사용 흔적](../../file-folder-usage/microsoft-office/index.md) — 이 PC 의 오피스가 문서를 다룬 기록입니다.
- [오피스 매크로](../vba-macro.md) · [사진 EXIF](../exif.md) · [실행 파일 메타데이터](../pe-header-version-info-digital-signature.md) — 다른 파일 내장 메타데이터입니다.
- [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) — 문서 속 시각을 다른 기록과 한 줄에 놓습니다.
- [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) — 메타데이터를 지우거나 고친 흔적을 찾습니다.

## 참고 문헌

- Microsoft Learn, "The Summary Information Property Set". https://learn.microsoft.com/en-us/windows/win32/stg/the-summary-information-property-set
- libyal libolecf, "OLE Compound File format". https://raw.githubusercontent.com/libyal/libolecf/main/documentation/OLE%20Compound%20File%20format.asciidoc
- 한글과컴퓨터, "한글 문서 파일 형식 5.0" revision 1.3 (2018-11-08). https://cdn.hancom.com/link/docs/한글문서파일형식_5.0_revision1.3.pdf
- ExifTool, "PDF Tags". https://exiftool.org/TagNames/PDF.html
- Wikipedia, "PDF". https://en.wikipedia.org/wiki/PDF
- Adobe, "XMP Specification Part 1: Data Model, Serialization, and Core Properties" (2012-04, ISO 16684-1:2011). https://raw.githubusercontent.com/adobe/XMP-Toolkit-SDK/main/docs/XMPSpecificationPart1.pdf
