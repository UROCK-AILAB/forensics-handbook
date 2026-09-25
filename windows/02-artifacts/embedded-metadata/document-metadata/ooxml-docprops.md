---
title: "오피스 문서 속성"
parent: "문서 메타데이터"
grand_parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 2940
---

# 오피스 문서 속성 (OOXML docProps)

> 상위 페이지: [문서 메타데이터 (Document Metadata)](index.md)

## 한 줄 요약

docx 같은 OOXML 문서는 ZIP 파일이고, ZIP 안의 `docProps/core.xml` 과 `docProps/app.xml` 에 문서 속성이 XML 로 들어 있습니다. 작성자, 마지막으로 저장한 사람, 개정 번호, 만든 시각, 수정 시각, 총 편집 시간 같은 값입니다.

> "(관찰)" 은 시간대 KST (UTC+9), Word 16.0 빌드 16.0.20326 (Microsoft 365) 기준입니다. 판마다 다를 수 있습니다.
>
> 시험 docx 는 두 번 저장했습니다. 새 문서에 글을 넣고 docx 로 다른 이름 저장을 했습니다. 문서를 닫고 약 1분 뒤 다시 열어 글을 덧붙이고 저장했습니다.

## 무엇을 기록하나 · 왜 생기나

Word 16 이 저장한 docx 에는 속성 파일이 두 개 있었습니다. (관찰)

| ZIP 안 경로 | 담는 것 |
|---|---|
| `docProps/core.xml` | 핵심 속성 (core properties). 제목·작성자·마지막으로 저장한 사람·개정 번호·만든 시각·수정 시각 |
| `docProps/app.xml` | 확장 속성 (extended properties). 템플릿·총 편집 시간·쪽 수·단어 수·프로그램 이름과 판·회사 |

사용자 정의 속성을 담는 `docProps/custom.xml` 은 시험 파일에 없었습니다. 이 파일이 어떤 조건에서 생기는지는 확인하지 못했습니다.

작성자와 마지막으로 저장한 사람 칸에는 Word 에 설정된 사용자 이름이 들어갔습니다. (관찰) 이 이름은 Windows 계정 이름이 아니라 프로그램 설정값입니다.

## 위치와 버전별 차이

값의 모양은 Windows 버전이 아니라 문서를 저장한 프로그램과 그 판에 따라 달라집니다.

Word 16 이 저장한 docx 의 ZIP 항목은 아래 순서였습니다. (관찰)

```
[Content_Types].xml
_rels/.rels
word/document.xml
word/_rels/document.xml.rels
word/footnotes.xml
word/endnotes.xml
word/theme/theme1.xml
word/settings.xml
word/styles.xml
word/webSettings.xml
word/fontTable.xml
docProps/core.xml
docProps/app.xml
```

`app.xml` 의 이름공간 (namespace) 은 파일마다 다를 수 있습니다. (관찰)

| 파일 | `app.xml` 이름공간 |
|---|---|
| Word 16 새 문서 | `http://schemas.openxmlformats.org/officeDocument/2006/extended-properties` |
| 공개 학회 논문 템플릿 docx | `http://purl.oclc.org/ooxml/officeDocument/extendedProperties` |

Excel (xlsx) 과 PowerPoint (pptx) 파일은 이번에 직접 보지 않았습니다. 같은 구조인지는 파일을 열어 확인합니다.

## 구조

### core.xml

뿌리 요소는 `cp:coreProperties` 입니다. 이름공간 세 개를 씁니다. (관찰)

| 접두어 | 이름공간 |
|---|---|
| `cp` | `http://schemas.openxmlformats.org/package/2006/metadata/core-properties` |
| `dc` | `http://purl.org/dc/elements/1.1/` |
| `dcterms` | `http://purl.org/dc/terms/` |

Word 16 이 쓴 요소는 아래와 같습니다. (관찰)

| 요소 | 뜻 | 관찰한 값 |
|---|---|---|
| `dc:title` | 제목 | |
| `dc:subject` | 주제 | |
| `dc:creator` | 작성자 | Word 에 설정된 사용자 이름 |
| `cp:keywords` | 키워드 | |
| `dc:description` | 설명 | |
| `cp:lastModifiedBy` | 마지막으로 저장한 사람 | Word 에 설정된 사용자 이름 |
| `cp:revision` | 개정 번호 | `2` (두 번 저장한 파일) |
| `dcterms:created` | 만든 시각 | `2026-09-23T11:27:00Z` |
| `dcterms:modified` | 수정 시각 | `2026-09-23T11:28:00Z` |

`dcterms:created` 와 `dcterms:modified` 에는 `xsi:type="dcterms:W3CDTF"` 속성이 붙습니다. (관찰)

`cp:lastPrinted` 같은 다른 요소는 시험 파일에 없었습니다. 전체 요소 목록은 명세 원문으로 확인하지 못했습니다.

### app.xml

값 형식에는 이름공간 `http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes` 를 씁니다. (관찰)

Word 16 이 쓴 요소는 아래와 같습니다. (관찰)

| 요소 | 관찰한 값·설명 |
|---|---|
| `Template` | `Normal.dotm` |
| `TotalTime` | 총 편집 시간. 몇 초만 편집한 시험 파일에서는 `0` |
| `Pages`, `Words`, `Characters`, `CharactersWithSpaces`, `Lines`, `Paragraphs` | 쪽·단어·글자·줄·문단 수 |
| `Application` | `Microsoft Office Word` |
| `AppVersion` | `16.0000` |
| `DocSecurity`, `ScaleCrop`, `Company`, `LinksUpToDate`, `SharedDoc`, `HyperlinksChanged` | 보안 설정·회사 이름 같은 값 |

`TotalTime` 은 ISO/IEC 29500-1 에 "문서를 편집한 총 시간" 으로 정의돼 있고, 기본 단위는 분이며 값은 XML Schema 의 int 형식입니다.

`HeadingPairs`, `TitlesOfParts`, `Company`, `LinksUpToDate`, `ScaleCrop` 은 옛 오피스 형식의 DocumentSummaryInformation 속성과 이름이 같습니다. 옛 형식의 속성 표는 [옛 오피스 문서 속성 (OLE SummaryInformation)](ole-summaryinformation.md) 에 있습니다.

## 증거로서 의미

**증명하는 것**

- 파일 안에 이 속성 값들이 적혀 있습니다.
- `dc:creator`·`cp:lastModifiedBy` 는 저장한 프로그램에 설정돼 있던 사용자 이름으로 적힌 값입니다. (관찰)
- `Application`·`AppVersion` 은 이 파일을 쓴 프로그램 이름과 판으로 적힌 값입니다.
- `Template` 은 문서가 쓴 템플릿 이름입니다.

**증명하지 못하는 것**

- 그 이름의 사람이 문서를 썼다는 것. 사용자 이름은 프로그램 설정값이라 누구나 바꿀 수 있습니다. PC 앞에 누가 있었는지는 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- 작성자가 이 PC 에서 문서를 처음 만들었다는 것. 공개 템플릿 파일 자체에 이미 작성자·회사·시각이 들어 있었습니다. 아래 "함정과 한계" 를 봅니다.
- 초 단위 저장 시각. Word 16 은 분 아래를 버렸습니다. (관찰)
- 실제로 일한 시간. `TotalTime` 은 분 단위라 짧은 편집은 `0` 이 됩니다. (관찰)
- 값이 저장한 뒤로 바뀌지 않았다는 것. `core.xml` 은 ZIP 안의 텍스트 XML 입니다. ZIP 을 풀어 값을 고치고 다시 묶을 수 있습니다.

보고서 문장은 기록이 말하는 만큼만 씁니다.

- 쓰지 않을 문장: "홍길동이 2026-09-23 11:27 에 이 문서를 작성했다."
- 쓸 문장: "report.docx 의 `docProps/core.xml` 에서 `dc:creator` 값은 '홍길동' 이고, `dcterms:created` 값은 2026-09-23T11:27:00Z (UTC) 이다. 이 값은 문서를 저장한 프로그램에 설정된 사용자 이름과, 분 단위로 적힌 시각이다." (예시 문장입니다.)

## 시각 해석

`dcterms:created`·`dcterms:modified` 는 UTC 로 적히고 끝에 `Z` 가 붙었습니다. PC 시간대가 KST 였는데도 UTC 였습니다. (관찰)

파일 시스템 시각과 견주면 아래와 같았습니다. (관찰)

| 문서 속 값 | 값 | 같은 파일의 파일 시스템 시각 (UTC) |
|---|---|---|
| `dcterms:created` | 11:27:00Z | 생성 11:27:51 |
| `dcterms:modified` | 11:28:00Z | 수정 11:28:56 |

두 값 모두 초를 버린 분 단위 값이었습니다. 그래서 파일 시스템 시각과 1분 안쪽으로 어긋나는 것은 이 버림으로 설명할 수 있습니다. 1분 넘게 어긋나면 다른 까닭을 찾습니다.

- `TotalTime` 은 시점이 아니라 길이이고, 단위는 분입니다.
- ZIP 항목에도 시각 칸이 있지만 Word 가 만든 docx 와 공개 템플릿 docx 의 ZIP 항목 시각은 모두 1980-01-01 00:00:00 이었습니다. (관찰) 이 칸으로는 언제 저장했는지 알 수 없습니다.
- 현지 시각으로 적힌 다른 기록과 나란히 볼 때는 [시간대 설정](../../system-account/time-zone.md) 을 먼저 확인합니다.

## 함정과 한계

- **템플릿이 값을 싣고 옵니다.** 공개 학회 논문 템플릿 docx 에는 배포 파일 자체에 `dc:creator` ("IEEE"), `cp:lastModifiedBy` (사람 이름), `Company` ("IEEE"), 같은 값의 `created`·`modified` (2024-07-16T13:42:00Z), 개정 번호 2 가 들어 있었습니다. (관찰) 이 템플릿에서 새로 만든 문서가 이 값을 물려받는지는 확인하지 못했습니다. 작성자 이름이 템플릿 배포자와 같으면 이 가능성부터 따져 봅니다.
- **이름공간이 두 가지입니다.** 위 표처럼 `app.xml` 이름공간이 파일마다 달랐습니다. 쓰는 도구가 두 이름공간을 모두 읽는지 확인합니다.
- **개정 번호가 무엇을 세는지 확정하지 못했습니다.** 두 번 저장한 docx 가 `2` 였습니다. 같은 세션에서 두 번째로 저장한 .doc 도 개정 번호가 2 였습니다. (관찰) 저장 횟수로 단정하지 않습니다.
- **ZIP 항목 시각을 믿지 않습니다.** 1980-01-01 로 고정돼 있었습니다. (관찰)
- **custom.xml 이 없을 수 있습니다.** 없다고 해서 누가 지웠다는 뜻은 아닙니다.
- **PDF 로 내보내면 속성이 달라집니다.** 어떤 값이 옮겨 가고 어떤 값이 빠지는지는 [PDF 정보 사전과 XMP (PDF Info·XMP)](pdf-info-xmp.md) 에서 다룹니다.
- **본문 쪽 편집 흔적은 따로 있습니다.** 문단마다 붙는 편집 세션 식별자는 [편집 흔적 식별자 (RSID)](rsid.md) 에서 다룹니다.

## 직접 분석해 보기

### XML 로 한 번

속성은 텍스트 XML 이라 헥스 대신 XML 을 직접 읽습니다.

1. 원본은 두고 사본을 만듭니다.
2. ZIP 을 여는 도구로 사본의 항목 목록을 봅니다. `docProps/core.xml` 과 `docProps/app.xml` 이 있는지 확인합니다.
3. `docProps/core.xml` 을 텍스트 편집기로 엽니다.

아래는 관찰한 시험 파일의 요소 이름과 값 일부로 줄여 만든 예시입니다. 실제 파일과 줄바꿈·요소 순서·이름공간 선언이 다를 수 있습니다.

```xml
<cp:coreProperties
    xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/" …>
  <dc:title/>
  <dc:subject/>
  <dc:creator>(Word 에 설정된 사용자 이름)</dc:creator>
  <cp:keywords/>
  <dc:description/>
  <cp:lastModifiedBy>(Word 에 설정된 사용자 이름)</cp:lastModifiedBy>
  <cp:revision>2</cp:revision>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-09-23T11:27:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-09-23T11:28:00Z</dcterms:modified>
</cp:coreProperties>
```

4. 시각 끝에 `Z` 가 있는지 봅니다. 있으면 UTC 입니다.
5. 초 자리가 `00` 인지 봅니다. `00` 이면 분 단위로 버린 값일 수 있습니다.
6. `docProps/app.xml` 에서 `Application`, `AppVersion`, `Template`, `TotalTime` 을 적습니다.
7. `app.xml` 뿌리 요소의 이름공간을 적습니다. 위 표의 두 값 가운데 어느 쪽인지 봅니다.

### 공개 도구로 한 번

Python 표준 라이브러리만으로 같은 값을 뽑을 수 있습니다. 사본에만 씁니다.

```python
import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile("copy.docx") as z:
    for info in z.infolist():
        print(info.filename, info.date_time)      # 항목 이름과 ZIP 항목 시각
    for name in ("docProps/core.xml", "docProps/app.xml"):
        root = ET.fromstring(z.read(name))
        print(name, root.tag)                     # 뿌리 요소와 이름공간
        for el in root:
            print(" ", el.tag, el.attrib, el.text)
```

- `el.tag` 는 `{이름공간}요소이름` 꼴로 나옵니다. 이름공간 차이를 여기서 바로 봅니다.
- ZIP 항목 시각이 모두 1980-01-01 이면 위 관찰과 같습니다.
- 쓰는 포렌식 도구의 결과와 이 값을 맞춰 봅니다. 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 따릅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [편집 흔적 식별자 (RSID)](rsid.md) | 본문이 몇 차례의 편집 세션에 걸쳐 저장됐는지 |
| [옛 오피스 문서 속성 (OLE SummaryInformation)](ole-summaryinformation.md) | 같은 문서를 .doc 로도 저장했을 때의 속성 |
| [PDF 정보 사전과 XMP (PDF Info·XMP)](pdf-info-xmp.md) | 이 문서에서 내보낸 PDF 의 속성 |
| [마스터 파일 테이블](../../filesystem/mft.md) | 파일 시스템 생성·수정 시각과 `created`·`modified` 의 차이 |
| [USN 변경 저널](../../filesystem/usnjrnl.md) | 파일이 이 볼륨에서 만들어지고 바뀐 기록 |
| [오피스 사용 흔적](../../file-folder-usage/microsoft-office/index.md) | 이 PC 의 오피스가 그 문서를 다룬 기록 |
| [바로가기 파일](../../file-folder-usage/lnk.md)·[점프리스트](../../file-folder-usage/jump-lists.md) | 같은 파일을 연 다른 기록 |
| [다운로드 출처 표시](../../filesystem/zone-identifier.md) | 문서를 내려받았는지 |

시나리오로 이어서 보려면 [이 문서의 날짜를 믿을 수 있나](../../../04-scenarios/activity/document-date-verification.md) 와 [이 파일은 어디서 왔나](../../../04-scenarios/activity/file-origin.md) 를 봅니다.

## 실습

오피스를 설치한 가상 머신을 만들어 직접 해 봅니다. 공개 검체 가운데 docx 가 들어 있는 이미지를 골라도 됩니다.

1. 새 docx 를 저장하고 1분쯤 뒤 다시 열어 고친 다음 저장합니다. `created`·`modified` 와 파일 시스템 시각을 견줍니다. 초 자리가 버려졌나요?
2. 저장할 때마다 `cp:revision` 이 어떻게 바뀌는지 적습니다. 열기만 하고 닫으면 바뀌나요?
3. Word 의 사용자 이름을 바꾼 뒤 같은 문서를 저장합니다. `dc:creator` 와 `cp:lastModifiedBy` 가운데 어느 쪽이 바뀌나요?
4. 공개 템플릿 docx 를 하나 받아 `core.xml` 을 봅니다. 그 템플릿으로 새 문서를 만들어 저장한 뒤 값을 물려받았는지 봅니다.
5. 10분 넘게 편집한 문서의 `TotalTime` 을 봅니다. 실제로 편집한 시간과 얼마나 맞나요?
6. 결과로 보고서 문장을 하나 씁니다. "작성했다" 가 아니라 기록이 말하는 만큼만 씁니다.

## 참고 문헌

- Microsoft Learn, "TotalTime Class (DocumentFormat.OpenXml.ExtendedProperties)" (ISO/IEC 29500-1 발췌 포함). https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.extendedproperties.totaltime
- Microsoft Learn, "The DocumentSummaryInformation and UserDefined Property Sets". https://learn.microsoft.com/en-us/windows/win32/stg/the-documentsummaryinformation-and-userdefined-property-sets
