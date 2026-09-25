---
title: "문서 메타데이터"
parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 1280
---

# 문서 메타데이터 (PDF·Office)

## 한 줄 요약

PDF 는 Info 사전에, Office 의 OOXML 문서(DOCX·XLSX·PPTX)는 핵심 속성(core properties) 파트와 문서 속성에 작성자·작성 프로그램·만든 시각·고친 시각 같은 값을 적어 두기 때문에, 폰에 남은 문서 파일만 있어도 누가 어떤 프로그램으로 만들고 고쳤다고 적혀 있는지 읽을 수 있습니다 [1][2][3].

## 무엇을 기록하나 · 왜 생기나

문서를 만드는 프로그램은 본문과 함께 문서에 관한 정보를 파일 안에 적습니다. 공개 도구 ExifTool 은 PDF 의 Info 사전에서 Author, CreateDate, Creator, Keywords, ModifyDate, Producer, Subject, Title, AppleKeywords, SourceModified, Trapped 태그를 읽습니다 [1]. 이 이름은 ExifTool 이 보여 주는 표시 이름이고, PDF 안의 원래 키 이름은 CreateDate 가 `CreationDate`, ModifyDate 가 `ModDate` 입니다 [1]. Keywords 는 문자열 하나로 저장되지만, ExifTool 은 쉼표나 세미콜론이 있으면 둘 가운데 더 많이 나온 쪽을 구분자로, 둘 다 없으면 공백을 구분자로 보고 목록으로 나눠 보여 줍니다 [1].

OOXML 형식은 Microsoft Office 2007 에서 들어왔고 DOCX, PPTX, XLSX, VSDX 가 이 형식을 쓰며, 파일은 XML 파일 여러 개를 담은 압축 묶음(archive)입니다 [2]. 묶음 안의 핵심 속성 파트에는 만든 사람, 마지막으로 고친 사람, 만든 시각과 바꾼 시각, 마지막 인쇄 시각, 개정 번호 같은 값이 들어가고 [3][4], ExifTool 은 이와 별도로 작성 프로그램, 회사, 누적 편집 시간, 쪽수·단어 수 같은 문서 속성도 읽습니다 [2].

폰은 이런 문서를 받아 두거나 열어 보는 장소라서, 문서가 어디서 왔는지는 폰의 기록으로 보고 문서가 무엇이라고 스스로 적고 있는지는 파일 안의 메타데이터로 봅니다. 파일의 색인 행(경로, MIME 형식, 넣은 앱, 시각)은 [미디어 저장소 (MediaStore)](../media/mediastore/index.md) 페이지에서 다루고, 이 페이지는 파일 안의 값을 다룹니다.

## 위치와 버전별 차이

문서 안의 메타데이터는 PDF 와 OOXML 형식이 정한 것이라서 Android 버전이나 제조사에 따라 구조가 달라지지 않습니다. 폰에서 이런 파일을 찾을 곳은 공용 저장 공간의 `/sdcard/Documents`, `/sdcard/Download` 같은 폴더와 각 앱의 데이터 폴더입니다.

공용 저장 공간의 폴더 구성은 [공용 저장 공간 (Shared Storage·/sdcard)](../../01-foundations/storage/shared-storage.md), 앱 데이터 폴더는 [앱 데이터 폴더 구조 (/data/data·/data/user)](../../01-foundations/storage/app-data-layout.md) 페이지에 있습니다. MediaStore 가 PDF·Office 파일 안의 작성자 같은 값을 읽어 칸에 넣는지, 삼성 내 파일 앱이나 모바일 문서 편집 앱이 문서를 저장하거나 고칠 때 작성 프로그램 칸에 어떤 값을 남기는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다.

## 구조

### PDF 와 증분 업데이트

ExifTool 은 PDF 2.0 까지 읽고 쓸 수 있고, RC4·AES-128·AES-256 으로 암호화한 PDF 도 다룹니다 [1]. ExifTool 이 PDF 를 고칠 때는 파일 뒤에 바뀐 부분을 덧붙이는 증분 업데이트(incremental update) 방식을 쓰고, 원래 상태는 PDF-update 가상 그룹을 지워 되살릴 수 있습니다 [1]. 이 방식에서는 고치기 전 정보가 파일에서 실제로 지워지지 않아 보안 문제가 될 수 있고, 선형화(linearized)한 PDF 는 업데이트 뒤 선형화가 풀립니다 [1].

그래서 증분 업데이트로 고친 PDF 에는 고치기 전의 메타데이터가 파일 안에 남아 있을 수 있고, 선형화가 풀린 PDF 는 나중에 편집한 단서가 될 수 있습니다. 다른 편집기가 증분 업데이트를 쓰는지는 편집기마다 다를 수 있어 검체에서 확인합니다.

### OOXML 핵심 속성

핵심 속성의 이름은 Category, ContentStatus, ContentType, Created, Creator, Description, Identifier, Keywords, Language, LastModifiedBy, LastPrinted, Modified, Revision, Subject, Title, Version 의 16개이고 [3][4], 조사에서 자주 보는 속성의 뜻은 다음과 같습니다 [3].

| 속성 | 뜻 |
|---|---|
| Creator | 패키지와 내용을 만든 사람이나 주체 |
| LastModifiedBy | 마지막으로 내용을 고친 사용자 |
| Created | 만든 날짜와 시각 |
| Modified | 마지막으로 바꾼 날짜와 시각 |
| LastPrinted | 마지막으로 인쇄한 시각 |
| Revision | 개정 번호 |

핵심 속성 파트는 파일 이름이 아니라 관계 유형으로 찾습니다. 관계 유형은 `http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties` 이고, 파트의 콘텐츠 유형은 `application/vnd.openxmlformats-package.core-properties+xml` 입니다 [4]. .NET 구현은 이 파트를 새로 만들 때 `/package/services/metadata/core-properties/{guid}.psmdcp` 라는 이름을 쓰니 [4], 파트 이름은 만든 프로그램마다 다를 수 있고, 관계 파일(`_rels/.rels`)의 core-properties 관계가 가리키는 파트를 여는 쪽이 안전합니다.

파트 안의 XML 은 다음 네임스페이스를 씁니다 [4].

| 이름 | 네임스페이스 |
|---|---|
| core-properties | `http://schemas.openxmlformats.org/officeDocument/2006/metadata/core-properties` |
| Dublin Core | `http://purl.org/dc/elements/1.1/` |
| DC Terms | `http://purl.org/dc/terms/` |
| XML Schema Instance | 날짜 속성의 `xsi:type` 에 씀 |

### ExifTool 이 읽는 문서 속성

ExifTool 은 OOXML 의 문서 속성에서 Application, AppVersion, Company, CreateDate, ModifyDate, LastModifiedBy, LastPrinted, RevisionNumber, TotalEditTime(누적 편집 시간), Template, Pages, Words, Characters, CharactersWithSpaces, Lines, Paragraphs, Slides, HiddenSlides, Manager, HyperlinkBase, DocSecurity, Keywords, Language 같은 태그를 뽑고, 이 태그들은 모두 쓰기를 지원하지 않습니다(Writable: no) [2]. 이 이름은 확장 속성 파트의 원래 XML 요소 이름이 아니라 ExifTool 태그 이름입니다. DocSecurity 값은 다음과 같습니다 [2].

| 값 | 뜻 |
|---|---|
| 0 | None |
| 1 | Password |
| 2 | Read-only recommended |
| 4 | Read-only enforced |
| 8 | Locked for annotations |

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 파일 안에 이 작성자·작성 프로그램·시각 값이 적혀 있다는 것 | 그 값이 사실이라는 것(파일 안의 문자열이라 고칠 수 있음) |
| Creator·LastModifiedBy 칸에 이 이름이 있다는 것 | 그 이름의 사람이 실제로 만들거나 고쳤다는 것(프로그램에 설정된 이름일 뿐) |
| 이 폰의 폴더에 이 문서가 있다는 것 | 이 폰에서 문서를 만들거나 고쳤다는 것 |
| DocSecurity 에 암호·읽기 전용 표시가 있다는 것 | 누가, 왜 그 설정을 했는지 |
| 증분 업데이트 흔적이나 선형화가 풀린 흔적이 있다는 것(해석) | 누가, 어느 기기에서 고쳤는지 |

보고서에는 "이 사람이 이 문서를 작성했다" 보다 "이 파일의 핵심 속성에 Creator 는 이 값, Modified 는 이 시각으로 적혀 있고, 폰의 Download 폴더에 있었다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

| 값 | 형식 | 무엇이 바뀔 때 바뀌나 |
|---|---|---|
| OOXML Created | `xsi:type="dcterms:W3CDTF"` 날짜. .NET 구현은 UTC `yyyy-MM-ddTHH:mm:ss.fffffffZ` 로 씀 [4] | 만들 때 [3] |
| OOXML Modified | 위와 같음 [4] | 마지막으로 바꿀 때 [3] |
| OOXML LastPrinted | 검체에서 확인 | 마지막으로 인쇄할 때 [3] |
| ExifTool TotalEditTime | 단위는 검체에서 확인 | 누적 편집 시간 [2] |
| PDF CreationDate·ModDate | ExifTool 표시 이름은 CreateDate·ModifyDate [1]. 날짜 문자열 형식은 검체에서 확인 | 검체에서 확인 |

.NET 구현은 읽을 때 소수 초가 0~7자리인 형식을 받아들이니 [4], 같은 W3CDTF 날짜라도 파일마다 소수 초 자릿수가 다를 수 있다고 보고 읽습니다. Office 나 모바일 앱이 쓰는 정밀도와 시간대는 앱마다 다를 수 있으니, 끝에 `Z` 가 없는 값을 UTC 로 단정하지 않습니다.

문서 안의 시각은 파일을 만든 프로그램이 적은 값이고, 폰의 파일 시스템 시각이나 MediaStore 칸의 시각은 폰이 적은 값입니다. 둘을 나란히 놓고 보면 문서가 폰에 들어오기 전에 만들어졌는지 판단하는 재료가 됩니다. 시각 값 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md), 여러 기록을 한 줄로 놓는 법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md) 페이지에 있습니다.

## 함정과 한계

- ExifTool 이 보여 주는 태그 이름(CreateDate, ModifyDate, RevisionNumber 등)은 표시 이름이라서, 보고서에 원래 키나 요소 이름처럼 적지 않습니다.
- OOXML 핵심 속성 파트의 이름은 만든 프로그램마다 다를 수 있으니 [4], 특정 파일 이름이 없다고 핵심 속성이 없다고 판단하지 않습니다.
- ExifTool 은 OOXML 태그를 쓰지 못하지만 [2], 다른 프로그램으로는 값을 바꿀 수 있습니다. 메타데이터만으로 작성자나 작성 시각을 확정하지 않습니다.
- 작성 프로그램 값만 보고 폰에서 편집했다고 단정하지 않습니다.
- 작성자 같은 값은 MediaStore DB 가 아니라 원본 파일에서 읽습니다.

## 직접 분석해 보기

작업은 해시를 적어 둔 사본으로 합니다. 확보 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지에 있습니다.

**헥스로 OOXML 날짜 찾기.** OOXML 파일은 압축 묶음이니 [2] 먼저 풀고, `_rels/.rels` 에서 core-properties 관계가 가리키는 파트를 찾아 헥스 편집기로 엽니다. 날짜 속성에는 `xsi:type="dcterms:W3CDTF"` 가 붙어 있어서 [4] 이 문자열 뒤의 값을 읽으면 됩니다. 아래는 .NET 구현의 쓰기 형식으로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다.

```text
2020-12-15T00:06:26.0000000Z
32 30 32 30 2D 31 32 2D 31 35 54 30 30 3A 30 36 3A 32 36 2E 30 30 30 30 30 30 30 5A
해석: 끝의 Z(5A) 는 UTC 표시 → UTC 2020-12-15 00:06:26, 한국 시각(+09:00)으로 09:06:26
```

PDF 의 날짜는 아래처럼 공개 도구로 읽습니다.

**공개 도구로 읽기.** ExifTool 로 PDF 나 OOXML 파일을 열면 이 페이지의 태그 이름으로 값이 나옵니다 [1][2]. ExifTool 로 고친 PDF 라면 PDF-update 가상 그룹을 지워 원래 상태로 되돌릴 수 있으니 [1], 사본의 사본에서만 아래 명령을 돌리고 되돌린 결과를 지금 값과 비교합니다. 파일을 고치는 명령이라서 원본이나 증거 사본에는 쓰지 않습니다.

```text
exiftool -PDF-update:all= copy_of_copy.pdf
```

그다음 같은 파일의 MediaStore 행을 [미디어 저장소 (MediaStore)](../media/mediastore/index.md) 페이지의 방법으로 찾아, 문서 안의 시각·작성 프로그램과 MediaStore 의 시각·넣은 앱을 나란히 놓습니다.

## 교차 검증

- [미디어 저장소 (MediaStore)](../media/mediastore/index.md) — 같은 문서의 색인 행에서 경로, MIME 형식, 넣은 앱, 시각을 봅니다.
- [크롬 (Chrome for Android)](../browsers/chrome/index.md) — Download 폴더의 문서를 웹에서 받은 기록이 있는지 봅니다.
- [카카오톡 (KakaoTalk)](../messengers/kakaotalk/index.md) — 메신저로 주고받은 파일인지 봅니다.
- [지메일 (Gmail)](../mail-cloud/gmail.md), [구글 드라이브 (Google Drive)](../mail-cloud/google-drive.md) — 메일 첨부나 클라우드에서 받은 파일인지 봅니다.
- [콘텐츠 검색 (Content Search)](../../03-techniques/analysis/content-search.md) — 문서 본문과 메타데이터에서 이름이나 낱말을 찾습니다.
- [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) — 이 기록을 쓰는 조사 시나리오입니다.

## 실습

공개 검체(NIST CFReDS 등)에서 Android 이미지를 구할 수 있으면 다음을 풀어 봅니다.

1. Download 폴더에서 DOCX·XLSX·PPTX 파일 하나를 골라 `_rels/.rels` 의 core-properties 관계가 가리키는 파트 이름을 적고, Created·Modified·Creator·LastModifiedBy 값을 읽습니다.
2. 같은 파일의 MediaStore 행을 찾아, 문서 안의 Modified 와 MediaStore 의 시각 가운데 어느 쪽이 먼저인지 비교합니다.
3. ExifTool 로 PDF 하나의 Creator·Producer·CreateDate(원래 키 CreationDate)·ModifyDate(원래 키 ModDate) 를 읽고, 두 시각이 다르면 어떤 설명이 가능한지 적어 봅니다.
4. DocSecurity 가 0 이 아닌 문서가 있는지 찾아, 그 값이 무엇을 뜻하는지 위 표로 풀어 봅니다.

## 참고 문헌

1. PDF Tags — ExifTool Tag Names, https://exiftool.org/TagNames/PDF.html
2. OOXML Tags — ExifTool Tag Names, https://exiftool.org/TagNames/OOXML.html
3. PackageProperties Class (System.IO.Packaging) — Microsoft Learn, https://learn.microsoft.com/en-us/dotnet/api/system.io.packaging.packageproperties
4. PartBasedPackageProperties.cs — dotnet/runtime (GitHub, main), https://raw.githubusercontent.com/dotnet/runtime/main/src/libraries/System.IO.Packaging/src/System/IO/Packaging/PartBasedPackageProperties.cs
