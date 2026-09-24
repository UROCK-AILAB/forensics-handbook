# PDF 정보 사전과 XMP (PDF Info·XMP)

> 상위 페이지: [문서 메타데이터 (Document Metadata)](/02-artifacts/embedded-metadata/document-metadata/index.md)

## 한 줄 요약

PDF 의 문서 정보는 두 곳에 들어갑니다. 하나는 트레일러가 가리키는 정보 사전 (Info dictionary) 이고, 다른 하나는 카탈로그가 가리키는 XMP 메타데이터 스트림입니다. 두 곳에 값을 따로 적으므로 값이 서로 어긋날 수 있습니다. 어긋남 자체가 도구가 손댄 흔적일 수 있습니다.

> 이 페이지에서 "(관찰)" 을 붙인 내용은 PC 한 대에서 직접 만든 시험 파일을 보고 확인한 것입니다. 확인 범위: Windows 11 (빌드 26200), 시간대 KST (UTC+9), Word 16.0 빌드 16.0.20326 (Microsoft 365) 의 "PDF 로 내보내기", pypdf 6.19.0. 시험 PDF 는 작성자가 적힌 docx 를 Word 에서 PDF 로 내보내 만들었습니다. 한 대·한 판에서 본 결과라 다른 판에서도 같다고 장담하지 못합니다.

## 무엇을 기록하나 · 왜 생기나

### 정보 사전의 키

PDF Association 의 Arlington PDF 모델에 실린 키입니다. 필수 키는 하나도 없습니다.

| 키 | 값 형식 | 들어온 판 | PDF 2.0 |
|---|---|---|---|
| `Title` | text | 1.1 | 폐기 |
| `Author` | text | 1.0 | 폐기 |
| `Subject` | text | 1.1 | 폐기 |
| `Keywords` | text | 1.1 | 폐기 |
| `Creator` | text | 1.0 | 폐기 |
| `Producer` | text | 1.0 | 폐기 |
| `CreationDate` | date | 1.0 | 폐기 표시 없음 |
| `ModDate` | date | 1.1 | 폐기 표시 없음 |
| `Trapped` | name (`True`/`False`/`Unknown`, 기본 `Unknown`) | 1.3 | 폐기 |
| 그 밖의 임의 키 | text | 1.1 | 폐기 |

- PDF 2.0 에서는 `CreationDate`·`ModDate` 말고 나머지 키가 모두 폐기로 표시돼 있습니다.
- 확장 키로 `AAPL:Keywords` (배열) 와 `GTS_PDFXVersion` (PDF/X) 이 실려 있습니다.

### XMP 속성

XMP (Extensible Metadata Platform) 명세 Part 1 (2012, ISO 16684-1:2011) 에 실린 속성 가운데 포렌식에서 자주 보는 것입니다.

| 속성 | 뜻 |
|---|---|
| `xmp:CreateDate` | 자원을 만든 시각. 파일 시스템 생성 시각과 같을 필요가 없습니다 |
| `xmp:ModifyDate` | 자원을 마지막으로 바꾼 시각 |
| `xmp:MetadataDate` | 메타데이터를 마지막으로 바꾼 시각. `ModifyDate` 와 같거나 더 나중이어야 합니다 |
| `xmp:CreatorTool` | 자원을 만든 첫 도구 이름 |
| `xmpMM:DocumentID` | 한 자원의 모든 판과 변환본에 공통인 식별자. 새 자원에 한 번 만듭니다 |
| `xmpMM:InstanceID` | 특정 상태의 식별자. 저장할 때마다 바뀝니다 |
| `xmpMM:OriginalDocumentID` | 다른 형식으로 저장해 이어 온 경우 원래 자원의 `DocumentID` |
| `xmpMM:DerivedFrom` | 이 자원이 나온 자원에 대한 참조 |

- 명세는 다른 변환본 (rendition) 은 `DocumentID` 가 다를 것으로 본다고도 적었습니다. 변환본인지 따질 때는 명세 원문을 직접 확인합니다.
- 이름공간은 `xmp` = `http://ns.adobe.com/xap/1.0/`, `xmpMM` = `http://ns.adobe.com/xap/1.0/mm/` 입니다.

## 위치와 버전별 차이

Word 가 내보낸 PDF 에서 두 곳은 이렇게 연결돼 있었습니다. (관찰)

| 가리키는 쪽 | 값 | 가리키는 곳 |
|---|---|---|
| 카탈로그 | `/Metadata 21 0 R` | XMP 스트림. 스트림 사전은 `/Type/Metadata/Subtype/XML` |
| 트레일러와 교차 참조 스트림 사전 | `/Info 18 0 R` | 정보 사전 |

- 객체 번호는 파일마다 다릅니다.
- 파일 끝에 덧붙여 고친 PDF 는 같은 객체가 여러 번 나올 수 있습니다. 이 구조는 [PDF 증분 저장과 이전 판 복원 (Incremental Update)](/02-artifacts/embedded-metadata/document-metadata/incremental-update.md) 에서 다룹니다.
- 값의 모양은 Windows 버전이 아니라 PDF 를 만든 프로그램과 PDF 판에 따라 달라집니다.

## 구조

### 정보 사전

Word 가 내보낸 PDF 의 정보 사전에는 아래 값이 있었습니다. (관찰)

| 키 | 값 |
|---|---|
| `Producer` | `Microsoft® Word Microsoft 365용` |
| `Creator` | `Producer` 와 같은 값 |
| `CreationDate` | `D:20260923202751+09'00'` |
| `ModDate` | `D:20260923202751+09'00'` |

- `Producer`·`Creator` 는 UTF-16BE 글자열 앞에 BOM (`FE FF`) 을 붙여 적었습니다. (관찰)
- 날짜 값은 현지 시각에 시간대 오프셋을 붙인 꼴이었습니다. 초 단위까지 있었습니다. (관찰)
- 날짜 형식의 명세 원문 (칸마다 생략할 수 있는 규칙) 은 확인하지 못했습니다. 위 관찰 값을 칸으로 나누면 `D:` · `20260923` (날짜) · `202751` (시각) · `+09'00'` (오프셋) 입니다.

### XMP 스트림

Word 가 내보낸 PDF 의 XMP 에서 본 것입니다. (관찰)

- 첫머리: `<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>`
- `x:xmptk="3.1-701"`
- `pdf:Producer`, `xmp:CreatorTool` (정보 사전과 같은 값)
- `xmp:CreateDate`·`xmp:ModifyDate` = `2026-09-23T20:27:51+09:00`
- `xmpMM:DocumentID` 와 `xmpMM:InstanceID` 가 같은 값 `uuid:A3AC86BB-E22F-495D-BEF9-D0E101271BE9` (처음 만든 파일)

XMP 날짜 형식은 명세에 이렇게 실려 있습니다.

```
YYYY
YYYY-MM
YYYY-MM-DD
YYYY-MM-DDThh:mmTZD
YYYY-MM-DDThh:mm:ssTZD
YYYY-MM-DDThh:mm:ss.sTZD
```

`TZD` 는 `Z` 이거나 `+hh:mm`·`-hh:mm` 입니다.

### 트레일러 /ID 와 DocumentID

Word 가 내보낸 PDF 의 트레일러 `/ID` 는 두 칸 모두 `<BB86ACA32FE25D49BEF9D0E101271BE9>` 였습니다. (관찰) 이 16바이트는 XMP 의 `DocumentID` GUID 를 바이트로 적은 것과 같았습니다.

| GUID 부분 | `DocumentID` 글자 | `/ID` 바이트 |
|---|---|---|
| 1 | `A3AC86BB` | `BB 86 AC A3` |
| 2 | `E22F` | `2F E2` |
| 3 | `495D` | `5D 49` |
| 4·5 | `BEF9-D0E101271BE9` | `BE F9 D0 E1 01 27 1B E9` |

앞 세 부분은 바이트 순서를 뒤집어 (리틀 엔디언) 적었고, 뒤 두 부분은 그대로 적었습니다. GUID 바이트 순서는 [윈도 식별자 형식](/01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에 있습니다.

## 증거로서 의미

**증명하는 것**

- 정보 사전과 XMP 에 적힌 만든 프로그램 이름·시각 값.
- `DocumentID` 가 같은 두 PDF 는 명세 정의로는 같은 자원의 여러 판으로 적힌 것입니다.
- `InstanceID` 가 다르면 서로 다른 상태로 저장된 것으로 적힌 것입니다.
- 정보 사전과 XMP 값이 다르면, 둘 가운데 하나만 고친 도구가 손댔을 가능성이 있습니다. 아래 "함정과 한계" 의 관찰을 봅니다.

**증명하지 못하는 것**

- 원본 문서에 작성자가 없었다는 것. `dc:creator` 가 있는 docx 를 Word 로 내보냈는데, PDF 정보 사전에는 `/Author` 키가 없었고 XMP 에도 `dc:creator` 가 없었습니다. (관찰)
- 파일 시스템에서 파일이 생긴 시각. XMP 명세는 `CreateDate` 가 파일 시스템 생성 시각과 같을 필요가 없다고 적었습니다. 전송과 복사로 파일 시스템 시각은 얼마든지 달라질 수 있습니다.
- 누가 만들었는지. 작성자 값은 프로그램이 적은 글자열입니다.
- 시간대 표기가 없는 XMP 날짜의 시간대. 명세는 이때 시간대를 모르는 것으로 보고 아무것도 가정하지 말라고 적었습니다.

보고서 문장은 기록이 말하는 만큼만 씁니다.

- 쓰지 않을 문장: "이 PDF 는 2026-09-23 20:27 에 만들어졌고 작성자는 없다."
- 쓸 문장: "result.pdf 의 정보 사전 `CreationDate` 값은 `D:20260923202751+09'00'` 이고, XMP `xmp:CreateDate` 값은 `2026-09-23T20:27:51+09:00` 이다. 두 값은 같은 순간 (2026-09-23 11:27:51 UTC) 을 가리킨다. 정보 사전에 `Author` 키는 없다." (예시 문장입니다.)

## 시각 해석

같은 순간이 두 곳에 다른 표기로 적혔습니다. (관찰)

| 위치 | 값 | 표기 |
|---|---|---|
| 정보 사전 `CreationDate` | `D:20260923202751+09'00'` | 현지 시각 + `+09'00'` |
| XMP `xmp:CreateDate` | `2026-09-23T20:27:51+09:00` | 현지 시각 + `+09:00` |

두 값 모두 UTC 로 바꾸면 2026-09-23 11:27:51 입니다. 오프셋 칸은 PC 시간대 (KST) 와 같았습니다. (관찰)

- XMP 명세는 가능하면 UTC 로 바꾸지 말고 현지 시간대 표기 (`+hh:mm`) 를 쓰라고 권합니다.
- `xmp:ModifyDate` 는 보통 저장하기 전에 정해집니다. 그래서 파일 시스템 수정 시각과 꼭 같지는 않습니다.
- `xmp:MetadataDate` 가 `xmp:ModifyDate` 보다 이르면 명세의 규칙과 맞지 않습니다. 이런 값은 따로 적어 둡니다.
- ExifTool 은 정보 사전의 `CreationDate`·`ModDate` 를 `CreateDate`·`ModifyDate` 라는 태그 이름으로 보여 줍니다. XMP 속성 이름과 비슷하므로 보고서에는 어느 쪽 값인지 원래 키 이름으로 적습니다.

## 함정과 한계

- **정보 사전과 XMP 가 어긋날 수 있습니다.** pypdf 로 정보 사전의 `Author`·`ModDate` 만 바꿔 파일 끝에 덧붙여 저장했습니다. XMP 는 그대로였습니다. (관찰)

  | 값 | 고친 뒤 |
  |---|---|
  | 정보 사전 `ModDate` | `21:00:00+09'00'` (바꾼 값) |
  | XMP `xmp:ModifyDate` | `20:27:51+09:00` (그대로) |
  | 정보 사전 `Author` | 바꾼 값이 있음 |
  | XMP 의 작성자 | 바꾼 값이 없음 |

  두 곳을 모두 읽고 견줍니다. 한쪽만 보여 주는 도구 결과로 판단하지 않습니다.
- **오프셋 표기가 두 가지입니다.** 정보 사전은 `+09'00'`, XMP 는 `+09:00` 이었습니다. (관찰) 둘 다 읽는지 도구를 확인합니다.
- **내보내기에서 빠지는 값.** Word 의 PDF 내보내기는 작성자를 옮기지 않았습니다. (관찰) 원본 문서의 속성은 [오피스 문서 속성 (OOXML docProps)](/02-artifacts/embedded-metadata/document-metadata/ooxml-docprops.md) 에서 따로 봅니다.
- **PDF 2.0 파일.** 정보 사전의 `CreationDate`·`ModDate` 말고 나머지 키가 폐기로 표시돼 있습니다. 2.0 파일에서 정보 사전에 제목·작성자가 없어도 이상하지 않습니다.
- **`Keywords` 는 글자열 하나입니다.** ExifTool 은 읽을 때 이 글자열을 목록으로 나눕니다. 쉼표나 세미콜론이 있으면 둘 가운데 더 많은 쪽으로 나누고, 없으면 공백으로 나눕니다. 도구 결과의 목록과 원래 글자열을 구분합니다.
- **글자열 인코딩.** 글자열이 `FE FF` 로 시작하면 UTF-16BE 로 풉니다. (관찰) 인코딩은 [문자 인코딩](/01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 을 봅니다.
- **덧붙여 고친 파일.** 옛 정보 사전 객체가 파일 앞부분에 남아 있을 수 있습니다. [PDF 증분 저장과 이전 판 복원 (Incremental Update)](/02-artifacts/embedded-metadata/document-metadata/incremental-update.md) 을 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

**정보 사전 글자열.** 아래는 관찰한 `Producer` 값의 첫 단어 `Microsoft` 를 BOM 과 UTF-16BE 규칙대로 적어 본 예시입니다. 파일에서 그대로 떠 온 바이트가 아닙니다.

```
FE FF 00 4D 00 69 00 63 00 72 00 6F 00 73 00 6F 00 66 00 74
```

| 바이트 | 뜻 |
|---|---|
| `FE FF` | BOM. 뒤 글자가 UTF-16BE 라는 표시 |
| `00 4D` | `M`. 글자 하나가 2바이트이고 큰 쪽 바이트가 먼저 옵니다 |
| `00 69` … `00 74` | `icrosoft` |

**정보 사전과 XMP 찾기.**

1. 원본은 두고 사본을 만듭니다.
2. 파일 끝의 트레일러나 교차 참조 스트림 사전에서 `/Info n 0 R` 을 찾습니다. `n` 이 정보 사전 객체 번호입니다.
3. `n 0 obj` 로 시작하는 객체를 찾습니다. 같은 번호가 여러 번 나오면 증분 저장이 있었을 수 있습니다. [증분 저장 페이지](/02-artifacts/embedded-metadata/document-metadata/incremental-update.md) 의 절차로 넘어갑니다.
4. 카탈로그의 `/Metadata m 0 R` 을 따라 XMP 스트림을 찾습니다. 관찰한 파일에서는 `<?xpacket` 으로 시작하는 XML 이었습니다.
5. 두 곳의 만든 시각·수정 시각·작성자·프로그램 이름을 표로 나란히 적습니다.
6. 트레일러 `/ID` 첫 칸을 위 표처럼 GUID 로 바꿔 `xmpMM:DocumentID` 와 견줍니다.

### 공개 도구로 한 번

pypdf 로 두 곳을 모두 읽을 수 있습니다. 사본에만 씁니다.

```python
from pypdf import PdfReader

r = PdfReader("copy.pdf")
print(r.metadata)                                  # 정보 사전
print(r.trailer.get("/ID"))                        # 트레일러 /ID
meta = r.trailer["/Root"].get("/Metadata")
if meta is not None:
    print(meta.get_object().get_data().decode("utf-8", "replace"))   # XMP 원문
```

- ExifTool 로도 같은 파일을 읽어 봅니다. 정보 사전 날짜는 `CreateDate`·`ModifyDate` 라는 이름으로 나옵니다. XMP 값이 따로 나오는지, 어떤 이름으로 나오는지 확인합니다.
- 두 도구 결과가 다르면 [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md) 을 따릅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [PDF 증분 저장과 이전 판 복원 (Incremental Update)](/02-artifacts/embedded-metadata/document-metadata/incremental-update.md) | 덧붙여 고친 부분, 옛 정보 사전 |
| [오피스 문서 속성 (OOXML docProps)](/02-artifacts/embedded-metadata/document-metadata/ooxml-docprops.md) | PDF 로 내보내기 전 원본 문서의 작성자·시각 |
| [마스터 파일 테이블](/02-artifacts/filesystem/mft.md) | 파일 시스템 생성·수정 시각과 `CreationDate`·`ModDate` 의 차이 |
| [다운로드 출처 표시](/02-artifacts/filesystem/zone-identifier.md) | PDF 를 내려받았는지 |
| [크롬 계열 브라우저](/02-artifacts/browsers/chrome-edge-whale/index.md) | 내려받은 기록 |
| [시간대 설정](/02-artifacts/system-account/time-zone.md) | 오프셋이 그 PC 의 시간대와 맞는지 |

시나리오로 이어서 보려면 [이 문서의 날짜를 믿을 수 있나](/04-scenarios/activity/document-date-verification.md) 와 [이 파일은 어디서 왔나](/04-scenarios/activity/file-origin.md) 를 봅니다.

## 실습

공개 검체 가운데 PDF 가 들어 있는 이미지를 고르거나, 가상 머신에서 직접 만듭니다.

1. 작성자를 넣은 docx 를 PDF 로 내보냅니다. 정보 사전과 XMP 에 작성자가 들어갔나요?
2. 정보 사전과 XMP 의 만든 시각을 UTC 로 바꿔 같은 순간인지 봅니다.
3. 트레일러 `/ID` 첫 칸을 GUID 로 바꿔 `DocumentID` 와 견줍니다.
4. 사본 하나를 메타데이터 편집 도구로 고칩니다. 정보 사전과 XMP 가운데 어느 쪽이 바뀌었나요? `InstanceID` 는 바뀌었나요?
5. 시간대 표기가 없는 XMP 날짜를 찾아봅니다. 도구가 그 값을 어느 시간대로 보여 주는지 적습니다.
6. 결과로 보고서 문장을 하나 씁니다. 어느 위치의 어느 키 값인지 밝혀 씁니다.

## 참고 문헌

- PDF Association, Arlington PDF Model "DocInfo.tsv". https://raw.githubusercontent.com/pdf-association/arlington-pdf-model/master/tsv/latest/DocInfo.tsv
- Adobe, "XMP Specification Part 1: Data Model, Serialization, and Core Properties" (2012-04, ISO 16684-1:2011). https://raw.githubusercontent.com/adobe/XMP-Toolkit-SDK/main/docs/XMPSpecificationPart1.pdf
- ExifTool, "PDF Tags". https://exiftool.org/TagNames/PDF.html
