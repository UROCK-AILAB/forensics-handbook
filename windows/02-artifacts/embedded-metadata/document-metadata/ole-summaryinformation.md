---
title: "옛 오피스 문서 속성"
parent: "문서 메타데이터"
grand_parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 2950
---

# 옛 오피스 문서 속성 (OLE SummaryInformation)

.doc 같은 옛 오피스 문서는 OLE 복합 파일이고, 그 안의 `\005SummaryInformation` 과 `\005DocumentSummaryInformation` 스트림에 문서 속성이 들어 있습니다. 값마다 속성 ID 와 값 형식이 붙고, 시각은 FILETIME (UTC) 입니다.

> 이 페이지의 예시 값은 Word 16.0 빌드 16.0.20326 (Microsoft 365) 에서 새 문서를 docx 로 저장한 뒤, 같은 세션에서 .doc 로 다른 이름 저장한 파일의 값입니다. 시간대는 KST (UTC+9) 입니다.

## 무엇을 기록하나 · 왜 생기나

속성은 속성 집합 (property set) 이라는 묶음에 들어 있습니다. 문서 속성에 쓰는 속성 집합은 아래와 같습니다.

| 스트림 | 속성 집합 | 형식 식별자 (FMTID) |
|---|---|---|
| `\005SummaryInformation` | Summary Information | `F29F85E0-4FF9-1068-AB91-08002B27B3D9` |
| `\005DocumentSummaryInformation` 첫 섹션 | DocumentSummaryInformation | `D5CDD502-2E9C-101B-9397-08002B2CF9AE` |
| `\005DocumentSummaryInformation` 둘째 섹션 | 사용자 정의 속성 (UserDefined) | `D5CDD505-2E9C-101B-9397-08002B2CF9AE` |

스트림 이름 앞의 `\005` (0x05) 는 여러 프로그램이 함께 쓰는 속성 집합이라는 표시입니다. 한 스트림에 속성 집합 두 개가 들어가는 경우는 DocumentSummaryInformation 과 UserDefined 뿐이고, 속성 이름은 보통 파일에 저장하지 않아서 속성 ID 로 무슨 속성인지 알아냅니다.

한글 HWP 5.0 문서도 같은 속성 집합 구조를 씁니다. 한글 쪽 속성은 [한글 문서 (HWP·HWPX)](hwp-hwpx.md) 에서 다룹니다.

## 위치와 버전별 차이

스트림은 OLE 복합 파일 안에 있습니다. 파일 서명으로 OLE 복합 파일인지 확인하고 스트림을 찾는 법은 [OLE 복합 파일](../../../01-foundations/shell-document-formats/compound-file-binary.md) 에 있습니다.

Word 16 이 저장한 .doc 에는 스트림이 다섯 개 있습니다.

```
\001CompObj
\005DocumentSummaryInformation
\005SummaryInformation
1Table
WordDocument
```

값의 모양은 Windows 버전이 아니라 저장한 프로그램과 그 판에 따라 달라집니다.

## 구조

### 속성 집합 스트림

오프셋 단위는 바이트입니다.

**머리글 (28바이트, 스트림 시작 기준)**

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0 | 2 | 바이트 순서 |
| 2 | 2 | 형식 |
| 4 | 4 | 시스템 판. 위 16비트가 플랫폼입니다 (0x0000 Win16, 0x0001 Macintosh, 0x0002 Win32) |
| 8 | 16 | 클래스 식별자 (GUID) |
| 24 | 4 | 섹션 수 |

**섹션 목록 항목 (20바이트, 머리글 바로 뒤에 섹션 수만큼)**

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0 | 16 | FMTID |
| 16 | 4 | 섹션 위치 (머리글 시작 기준) |

**섹션 머리 (8바이트)**

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0 | 4 | 섹션 데이터 크기 |
| 4 | 4 | 속성 수 |

**속성 목록 항목 (8바이트, 섹션 머리 바로 뒤에 속성 수만큼)**

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0 | 4 | 속성 ID |
| 4 | 4 | 값 위치 (섹션 머리 시작 기준) |

**속성 값**

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0 | 4 | 값 형식 |
| 4 | 가변 | 값 데이터 |

Word 16 이 저장한 .doc 에 나오는 값 형식 코드는 VT_LPSTR 0x1E, VT_FILETIME 0x40, VT_I4 0x03 입니다.

### Summary Information 속성

| ID | 이름 | 형식 | 뜻 |
|---|---|---|---|
| 0x02 | Title | VT_LPSTR | 제목 |
| 0x03 | Subject | VT_LPSTR | 주제 |
| 0x04 | Author | VT_LPSTR | 작성자 |
| 0x05 | Keywords | VT_LPSTR | 키워드 |
| 0x06 | Comments | VT_LPSTR | 설명 |
| 0x07 | Template | VT_LPSTR | 템플릿 |
| 0x08 | Last Saved By | VT_LPSTR | 마지막으로 저장한 사람 |
| 0x09 | Revision Number | VT_LPSTR | 개정 번호 |
| 0x0A | Total Editing Time | VT_FILETIME (UTC) | 총 편집 시간 |
| 0x0B | Last Printed | VT_FILETIME (UTC) | 마지막으로 인쇄한 시각 |
| 0x0C | Create Time/Date | VT_FILETIME (UTC) | 만든 시각 |
| 0x0D | Last saved Time/Date | VT_FILETIME (UTC) | 마지막으로 저장한 시각 |
| 0x0E | Number of Pages | VT_I4 | 쪽 수 |
| 0x0F | Number of Words | VT_I4 | 단어 수 |
| 0x10 | Number of Characters | VT_I4 | 글자 수 |
| 0x11 | Thumbnail | VT_CF | 미리보기 그림 |
| 0x12 | Name of Creating Application | VT_LPSTR | 만든 프로그램 이름 |
| 0x13 | Security | VT_I4 | 보안 설정 |

Word 16 이 저장한 .doc 의 값은 아래와 같습니다.

| ID | 값 |
|---|---|
| 0x01 | VT_I2 값. 코드 페이지 949 입니다 |
| 0x07 | `Normal.dotm` |
| 0x09 | `2` |
| 0x0A | 0 |
| 0x0C·0x0D | 둘 다 2026-09-23 11:27:00 UTC (초 00) |
| 0x0E | 1 |
| 0x12 | `Microsoft Office Word` |
| 0x13 | 0 |

0x04 와 0x08 에는 Word 에 설정된 사용자 이름이 들어갑니다. 인쇄한 적 없는 이 문서에는 0x0B 와 0x11 이 아예 없습니다.

### DocumentSummaryInformation 속성

| ID | 이름 | ID | 이름 |
|---|---|---|---|
| 0x02 | Category | 0x0A | MMClips |
| 0x03 | PresentationTarget | 0x0B | ScaleCrop |
| 0x04 | Bytes | 0x0C | HeadingPairs |
| 0x05 | Lines | 0x0D | TitlesofParts |
| 0x06 | Paragraphs | 0x0E | Manager |
| 0x07 | Slides | 0x0F | Company |
| 0x08 | Notes | 0x10 | LinksUpToDate |
| 0x09 | HiddenSlides | | |

Category 는 사용자가 넣은 분류로 메모·제안서 같은 값입니다. Manager 는 프로젝트 관리자, Company 는 회사 이름입니다. HeadingPairs 는 이름 글자열과 개수 (VT_I4) 를 짝지은 목록이고, TitlesofParts 는 문서 부분 이름 목록입니다.

Word 16 이 저장한 .doc 의 DocumentSummaryInformation 에는 이 표에 없는 ID 0x11·0x13·0x16·0x17 도 있습니다. 형식은 VT_I4 나 VT_BOOL 입니다. 이 ID 들의 이름은 공개 자료에 없습니다.

docx 에도 같은 이름의 속성이 있습니다. [오피스 문서 속성 (OOXML docProps)](ooxml-docprops.md) 을 봅니다.

## 증거로서 의미

**증명하는 것**

- 스트림에 작성자·마지막으로 저장한 사람·템플릿·프로그램 이름·시각 값이 적혀 있습니다.
- 작성자와 마지막으로 저장한 사람은 저장한 프로그램에 설정돼 있던 사용자 이름으로 적힌 값입니다.
- 0x0B 가 있으면 파일에 마지막 인쇄 시각이 적혀 있습니다.

**증명하지 못하는 것**

- 그 이름의 사람이 문서를 썼다는 것. 사용자 이름은 프로그램 설정값입니다. 이 문제는 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- 0x0B 가 없으면 한 번도 인쇄하지 않았다는 것. 알려진 것은 인쇄하지 않은 문서에 0x0B 가 없다는 것뿐입니다.
- 초 단위 저장 시각. Word 16 은 초를 00 으로 적습니다.
- 실제로 일한 시간. 몇 초 편집한 문서의 총 편집 시간은 0 으로 적힙니다.
- 값이 저장한 뒤로 바뀌지 않았다는 것. 스트림 속 값은 다른 도구로 고쳐 쓸 수 있습니다.

보고서 문장은 기록으로 확인되는 만큼만 씁니다.

- 쓰지 않을 문장: "이 문서는 한 번도 인쇄한 적이 없다."
- 쓸 문장: "plan.doc 의 `\005SummaryInformation` 스트림에는 Last Printed (속성 ID 0x0B) 속성이 없다. Create Time/Date (0x0C) 값은 2026-09-23 11:27:00 UTC 이다." (예시 문장입니다.)

## 시각 해석

- 0x0B·0x0C·0x0D 는 FILETIME 이고 UTC 입니다. 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- 위 예시 .doc 의 0x0C·0x0D 는 11:27:00 UTC 이고, 같은 파일의 파일 시스템 생성 시각은 11:27:51 UTC 입니다. 초를 버린 값으로 보입니다.
- 파일을 옮기는 방식 (예: BBS 내려받기) 에 따라 파일 시스템 쪽 시각이 제대로 남지 않을 수 있습니다. 파일 시스템 시각과 문서 속 시각이 다르면 둘 다 적어 둡니다.
- 0x0A (총 편집 시간) 는 표에 VT_FILETIME 으로 적혀 있지만 이름으로 보면 시점이 아니라 길이입니다. 도구가 이 값을 날짜로 보여 주면 그대로 옮기지 않습니다.
- 0x09 (개정 번호) 는 숫자가 아니라 글자열 (VT_LPSTR) 입니다. 첫 세션에서 두 번째로 저장한 .doc 의 값은 `2` 입니다. 무엇을 세는 값인지 밝힌 공개 자료는 없습니다.

## 함정과 한계

- **확장자가 .doc 라도 OLE 가 아닐 수 있습니다.** 공공 법령 사이트에서 내려받는 .doc 파일 가운데 RTF 인 것이 있습니다. 이런 파일은 `{\rtf1\ansi` 로 시작하고, OLE 도구로 열면 "OLE 파일이 아니다" 오류가 납니다. 확장자보다 첫 바이트를 먼저 봅니다.
- **코드 페이지를 알아야 합니다.** 글자열이 VT_LPSTR 이라 코드 페이지를 모르면 한글이 깨집니다. 위 예시 .doc 는 949 입니다. 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 을 봅니다.
- **같은 ID 라도 섹션마다 뜻이 다릅니다.** 0x02 는 Summary Information 에서 Title 이고 DocumentSummaryInformation 에서 Category 입니다. 어느 FMTID 의 섹션인지 먼저 확인합니다.
- **표에 없는 ID 가 있습니다.** 이름을 모르는 ID 는 번호와 형식, 값만 적습니다. 짐작으로 이름을 붙이지 않습니다.
- **없는 속성과 0 은 다릅니다.** Word 16 은 인쇄하지 않은 문서에 0x0B 를 아예 쓰지 않습니다. 도구가 빈 값을 0 이나 1601-01-01 로 보여 주면 원래 없던 값인지 확인합니다.
- **초가 00 인 시각.** 초를 버린 값일 수 있습니다. 위 예시 .doc 는 파일 시스템 생성 시각과 51초 차이가 납니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 머리글 구조와 Summary Information 의 FMTID 로 만든 예시입니다. Word 16 이 저장한 .doc 의 `\005SummaryInformation` 첫 48바이트도 이와 같습니다.

```
오프셋    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  FE FF 00 00 0A 00 02 00  00 00 00 00 00 00 00 00
00000010  00 00 00 00 00 00 00 00  01 00 00 00 E0 85 9F F2
00000020  F9 4F 68 10 AB 91 08 00  2B 27 B3 D9 30 00 00 00
```

| 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0x00 | `FE FF` | 바이트 순서 필드 |
| 0x02 | `00 00` | 형식 필드 |
| 0x04 | `0A 00 02 00` | 시스템 판 0x0002000A. 위 16비트 0x0002 는 Win32 입니다 |
| 0x08 | `00` × 16 | 클래스 식별자. 여기서는 모두 0 입니다 |
| 0x18 | `01 00 00 00` | 섹션 1개 |
| 0x1C | `E0 85 9F F2 … B3 D9` | FMTID `F29F85E0-4FF9-1068-AB91-08002B27B3D9` |
| 0x2C | `30 00 00 00` | 섹션 위치 0x30 |

FMTID 는 앞 세 부분의 바이트 순서를 뒤집어 적습니다. `F29F85E0` 이 `E0 85 9F F2` 로, `4FF9` 가 `F9 4F` 로, `1068` 이 `68 10` 으로 적혔습니다. GUID 바이트 순서는 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에 있습니다.

섹션부터는 이렇게 따라갑니다.

1. 스트림 오프셋 0x30 에서 섹션 머리 8바이트를 읽습니다. 섹션 크기와 속성 수가 나옵니다.
2. 바로 뒤 속성 목록에서 속성 ID 가 0x0C 인 항목을 찾습니다. 항목은 8바이트입니다.
3. 항목의 값 위치에 0x30 을 더합니다. 값 위치는 섹션 머리 시작 기준이기 때문입니다.
4. 그 자리의 값을 읽습니다.

아래는 만든 시각 2026-09-23 11:27:00 UTC 를 명세대로 값 형식과 FILETIME 으로 적은 예시입니다.

```
40 00 00 00  00 9A 01 73 4E 4B DD 01
```

| 바이트 | 뜻 |
|---|---|
| `40 00 00 00` | 값 형식 0x40 = VT_FILETIME |
| `00 9A 01 73 4E 4B DD 01` | 리틀 엔디언 FILETIME. 수로는 0x01DD4B4E73019A00 |

0x01DD4B4E73019A00 은 10진수로 134,346,364,200,000,000 입니다. 1601-01-01 UTC 부터 센 100나노초 수입니다. 풀면 2026-09-23 11:27:00 UTC 입니다.

쪽 수 (0x0E) 값 1 을 같은 방식으로 적으면 `03 00 00 00 01 00 00 00` 입니다. 값 형식 0x03 (VT_I4) 뒤에 4바이트 정수 1 이 옵니다. (명세로 만든 예시)

### 공개 도구로 한 번

Python 의 olefile 로 스트림 목록과 속성을 읽을 수 있습니다. 사본에만 씁니다.

```python
import olefile

ole = olefile.OleFileIO("copy.doc")
print(ole.listdir())                                   # 스트림 목록
props = ole.getproperties("\x05SummaryInformation", convert_time=True)
for pid in sorted(props):
    print(hex(pid), props[pid])
```

1. 스트림 목록에 `\x05SummaryInformation` 과 `\x05DocumentSummaryInformation` 이 있는지 봅니다.
2. 0x01 값으로 코드 페이지를 확인합니다. 글자열이 깨지면 이 값으로 다시 풉니다.
3. 0x0C·0x0D 를 헥스로 직접 푼 값과 맞춰 봅니다.
4. 쓰는 포렌식 도구의 결과와도 맞춰 봅니다. 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 따릅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [오피스 문서 속성 (OOXML docProps)](ooxml-docprops.md) | 같은 문서의 docx 판 속성 |
| [한글 문서 (HWP·HWPX)](hwp-hwpx.md) | 같은 속성 집합 구조를 쓰는 한글 문서 |
| [마스터 파일 테이블](../../filesystem/mft.md) | 파일 시스템 생성·수정 시각과 0x0C·0x0D 의 차이 |
| [인쇄 흔적](../../external-devices/print-spooler-spl-shd.md)·[인쇄 이벤트](../../event-logs/printservice-307.md) | 0x0B 마지막 인쇄 시각 무렵의 인쇄 기록 |
| [오피스 사용 흔적](../../file-folder-usage/microsoft-office/index.md) | 이 PC 의 오피스가 그 문서를 다룬 기록 |
| [오피스 매크로](../vba-macro.md) | 같은 문서 파일에 든 매크로 |
| [다운로드 출처 표시](../../filesystem/zone-identifier.md) | 문서를 내려받았는지 |

시나리오로 이어서 보려면 [이 문서의 날짜를 믿을 수 있나](../../../04-scenarios/activity/document-date-verification.md) 를 봅니다.

## 실습

오피스를 설치한 가상 머신을 만들어 직접 해 봅니다. 공개 데이터셋 가운데 .doc 가 들어 있는 이미지를 골라도 됩니다.

1. .doc 파일을 모두 모아 첫 바이트를 봅니다. OLE 가 아닌 파일이 몇 개인가요?
2. .doc 하나를 인쇄하고 저장합니다. 0x0B 가 생기나요? 값이 인쇄 이벤트 시각과 맞나요?
3. 0x01 코드 페이지가 949 가 아닌 파일을 찾아 글자열이 어떻게 보이는지 봅니다.
4. 헥스 편집기로 0x0C 값을 직접 풀고 olefile 결과와 맞춰 봅니다.
5. DocumentSummaryInformation 에서 표에 없는 ID 를 찾아 번호와 형식을 적습니다.
6. 결과로 보고서 문장을 하나 씁니다. 속성이 없다는 사실과 행위를 구분해 씁니다.

## 참고 문헌

- Microsoft Learn, "The Summary Information Property Set". https://learn.microsoft.com/en-us/windows/win32/stg/the-summary-information-property-set
- Microsoft Learn, "The DocumentSummaryInformation and UserDefined Property Sets". https://learn.microsoft.com/en-us/windows/win32/stg/the-documentsummaryinformation-and-userdefined-property-sets
- libyal libolecf, "OLE Compound File format" (속성 집합 스트림 절). https://raw.githubusercontent.com/libyal/libolecf/main/documentation/OLE%20Compound%20File%20format.asciidoc
