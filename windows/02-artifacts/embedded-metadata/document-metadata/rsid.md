---
title: "편집 흔적 식별자"
parent: "문서 메타데이터"
grand_parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 2960
---

# 편집 흔적 식별자 (RSID)

> 상위 페이지: [문서 메타데이터 (Document Metadata)](index.md)

docx 에는 편집 세션을 가리키는 식별자인 RSID (revision save ID) 가 들어 있습니다. `word/settings.xml` 에 문서 전체의 RSID 목록이 있고 본문의 문단과 글자 묶음에도 RSID 가 속성으로 붙으며, 같은 RSID 가 붙은 부분끼리는 같은 편집 세션에 저장된 것으로 읽을 수 있습니다. 다만 RSID 에는 시각이 없습니다.

> 이 페이지의 예시 값은 Word 16.0 빌드 16.0.20326 (Microsoft 365) 에서 세 번 저장한 docx 의 값입니다. 새 문서에 글을 넣고 docx 로 다른 이름 저장을 하고, 같은 세션에서 .doc 로 다른 이름 저장을 한 번 더 한 뒤, 문서를 닫고 약 1분 뒤 docx 를 다시 열어 글을 덧붙이고 저장한 파일입니다.

## 무엇을 기록하나 · 왜 생기나

RSID 값은 이 문서가 지나온 편집 세션 하나하나를 구별하는 16진수 값입니다.

편집 세션 (editing session) 은 프로그램이 연달아 두 번 저장하는 사이의 시간입니다.

RSID 요소는 세 가지입니다.

| 요소 | 명세 절 | 뜻 |
|---|---|---|
| `w:rsids` | 부모는 `settings` (§17.15.1.78) | RSID 값 목록 |
| `w:rsid` | §17.15.1.70 | 한 편집 세션의 RSID (Single Session Revision Save ID) |
| `w:rsidRoot` | §17.15.1.71 | 원래 문서의 RSID (Original Document Revision Save ID) |

명세의 예시에서는 `rsidRoot` 1개와 `rsid` 3개가 있는 문서가 "편집 세션 네 번 (저장 세 번)" 입니다.

문서에 저장된 RSID 는 문서 구성 요소를 마지막으로 저장한 편집 세션을 알려 주는 정보일 뿐입니다. 프로그램은 이 값을 원하는 대로 쓸 수 있습니다.

## 위치와 버전별 차이

RSID 는 docx ZIP 안의 여러 XML 파일에 나옵니다.

| 파일 | 나오는 모양 |
|---|---|
| `word/settings.xml` | `<w:rsids>` 안의 `<w:rsidRoot w:val="…"/>` 하나와 `<w:rsid w:val="…"/>` 여러 개 |
| `word/document.xml` | 요소 속성 `w:rsidR`, `w:rsidRDefault`, `w:rsidP`, `w:rsidRPr`, `w:rsidSect` |
| `word/styles.xml`, `word/footnotes.xml`, `word/endnotes.xml` | RSID 속성 값 |

값의 모양은 Windows 버전이 아니라 저장한 프로그램에 따라 달라집니다.

docx 의 다른 속성 (작성자·시각) 은 [오피스 문서 속성 (OOXML docProps)](ooxml-docprops.md) 에서 다룹니다.

## 구조

**값의 길이.** 명세 문구는 "4자리 16진수" 이지만, 명세 예시 값 (`00464813`) 과 Word 16 이 쓴 값은 모두 16진수 8자리입니다.

**목록의 순서.** `<w:rsids>` 목록은 16진수 값의 오름차순으로 정렬됩니다. `rsidRoot` 값도 목록 맨 앞이 아니라 중간에 있을 수 있습니다. 목록 순서는 시간 순서가 아닙니다.

**본문의 RSID.** 아래는 위 예시 docx 의 RSID 값만 옮기고 나머지는 줄여 만든 예시입니다. 실제 파일의 다른 속성과 요소는 뺐습니다.

`word/settings.xml`

```xml
<w:rsids>
  <w:rsidRoot w:val="005C6D7D"/>
  <w:rsid w:val="…"/>
  …(이 파일에서는 w:rsid 가 8개, 값의 오름차순)
</w:rsids>
```

`word/document.xml`

```xml
<w:p w:rsidR="00A250AE" w:rsidRDefault="005C6D7D">
  <w:r>…첫 세션에 입력한 글…</w:r>
  <w:r w:rsidR="00635A2A">…둘째 세션에 덧붙인 글…</w:r>
</w:p>
```

첫 세션에 입력한 문단에는 `w:rsidR="00A250AE"` 와 `w:rsidRDefault="005C6D7D"` 가 붙고, 둘째 세션에 덧붙인 글자 묶음 (run) 에는 `w:rsidR="00635A2A"` 가 붙습니다. 이렇게 한 문단 안에서도 세션마다 다른 RSID 가 붙습니다.

## 증거로서 의미

**증명하는 것**

- 명세 정의로는 같은 RSID 값이 같은 편집 세션을 가리킵니다.
- 한 문단 안에 RSID 가 다른 글자 묶음이 있으면, 그 부분은 다른 세션에 저장된 것으로 읽을 수 있습니다. 위 예시 docx 에서는 둘째 세션에 덧붙인 글이 이렇게 나옵니다.
- `settings.xml` 의 RSID 목록은 이 문서가 거쳐 온 편집 세션을 가리키는 값의 모음입니다.

**증명하지 못하는 것**

- 언제 편집했는지. RSID 는 편집 세션을 구별하는 값일 뿐이고 시각을 담지 않습니다.
- 몇 번 저장했는지. 위 예시 docx 는 세 번 저장했는데 목록에 `rsid` 가 8개 있습니다. 아래 "함정과 한계" 를 봅니다.
- 어느 세션이 먼저인지. 목록은 값 순서로 정렬됩니다.
- 누가 편집했는지. RSID 에는 편집한 사람에 대한 정보가 없습니다.
- 두 문서가 한 문서에서 나왔다는 것. 공개 템플릿 docx 자체에 RSID 값이 97개 들어 있기도 합니다. 템플릿에서 만든 문서들에 같은 RSID 가 들어가는지는 실제 데이터로 확인합니다. 같은 값을 찾아도 템플릿에서 온 값일 수 있습니다.

보고서 문장은 기록으로 확인되는 만큼만 씁니다.

- 쓰지 않을 문장: "이 문서는 여덟 번 편집됐고, 마지막 문장은 나중에 몰래 추가됐다."
- 쓸 문장: "report.docx 의 `word/settings.xml` 에는 `w:rsid` 값이 8개 있다. 본문 한 문단의 마지막 글자 묶음에는 같은 문단의 다른 부분과 다른 RSID (`00635A2A`) 가 붙어 있다. RSID 는 편집 세션을 구별하는 값이며 시각이나 편집자를 알려 주지 않는다." (예시 문장입니다.)

## 시각 해석

RSID 에는 시각이 없습니다. 목록 순서도 시간 순서가 아닙니다.

시각은 다른 기록에서 가져옵니다.

- 문서의 만든 시각·수정 시각은 [오피스 문서 속성 (OOXML docProps)](ooxml-docprops.md) 에서 봅니다.
- 파일이 디스크에서 바뀐 시각은 [마스터 파일 테이블](../../filesystem/mft.md) 에서 봅니다.

RSID 로 할 수 있는 일은 본문을 세션별 묶음으로 나누는 것까지입니다. 묶음마다 시각을 붙이려면 이런 다른 기록과 맞춰 봐야 합니다.

## 함정과 한계

- **RSID 개수는 저장 횟수가 아닙니다.** 위 예시 docx 는 세 번 저장했는데 `<w:rsids>` 에는 `rsid` 가 8개 있습니다. 이 8개에는 `rsidRoot` 와 같은 값 `005C6D7D` 도 들어 있습니다.
- **쓰이지 않는 RSID 가 있습니다.** 8개 가운데 4개 (`0087573D`, `008B309C`, `00B35F26`, `00DA3C10`) 는 `settings.xml` 말고 어느 부분에도 나오지 않습니다.
- **"4자리" 라는 명세 문구에 기대지 않습니다.** 실제 값은 8자리입니다. 4자리만 찾는 검색식은 값을 놓칩니다.
- **목록 순서를 시간 순서로 읽지 않습니다.** 목록은 오름차순으로 정렬됩니다.
- **document.xml 만 보면 안 됩니다.** RSID 는 `styles.xml`, `footnotes.xml`, `endnotes.xml` 에도 나옵니다.
- **Word 가 아닌 프로그램.** 프로그램은 RSID 를 원하는 대로 쓸 수 있습니다. Word 가 아닌 프로그램이 저장한 docx 에서는 같은 해석이 맞는지 따로 확인합니다.
- **값을 만드는 방식이 알려져 있지 않습니다.** Word 가 RSID 값을 어떻게 만드는지 (무작위인지), 관련 옵션이 있는지는 실제 데이터로 확인해야 합니다.
- **템플릿에서 온 값.** 공개 템플릿 하나에 RSID 가 97개 들어 있기도 합니다. 문서의 RSID 가 많다고 해서 이 PC 에서 오래 편집했다고 보지 않습니다.

## 직접 분석해 보기

### XML 로 한 번

RSID 는 텍스트 XML 속성이라 헥스 대신 XML 을 직접 읽습니다.

1. 원본은 두고 사본을 만듭니다.
2. 사본의 ZIP 을 풀고 `word/settings.xml` 을 엽니다.
3. `<w:rsidRoot>` 값과 `<w:rsid>` 값을 모두 적습니다.
4. `word/` 아래 다른 XML 파일에서 `w:rsid` 로 시작하는 속성 값을 모두 모읍니다.
5. 목록의 값마다 본문에서 몇 번 쓰였는지 셉니다. 한 번도 쓰이지 않은 값을 따로 적습니다.
6. 본문 문단과 글자 묶음을 RSID 별로 묶습니다. 한 문단 안에서 RSID 가 바뀌는 곳을 찾습니다.

### 공개 도구로 한 번

Python 표준 라이브러리로 위 4~5단계를 할 수 있습니다. 사본에만 씁니다.

```python
import re
import zipfile
from collections import Counter

with zipfile.ZipFile("copy.docx") as z:
    settings = z.read("word/settings.xml")
    root = re.findall(rb'<w:rsidRoot w:val="([0-9A-Fa-f]{8})"', settings)
    listed = re.findall(rb'<w:rsid w:val="([0-9A-Fa-f]{8})"', settings)
    used = Counter()
    for name in z.namelist():
        if name.startswith("word/") and name.endswith(".xml") and name != "word/settings.xml":
            used.update(re.findall(rb'w:rsid\w*="([0-9A-Fa-f]{8})"', z.read(name)))

print("rsidRoot:", root)
for v in listed:
    print(v.decode(), used[v])        # 0 이면 본문 어디에도 쓰이지 않은 값
```

- 이 코드는 Word 16 이 쓴 파일의 모양 (`<w:rsid w:val="…"/>`) 에 맞춘 것입니다. 다른 프로그램이 쓴 파일은 속성 순서나 접두어가 다를 수 있습니다.
- 쓰는 포렌식 도구가 RSID 를 보여 주면 이 결과와 맞춰 봅니다. 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 따릅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [오피스 문서 속성 (OOXML docProps)](ooxml-docprops.md) | 개정 번호, 만든 시각·수정 시각 |
| [마스터 파일 테이블](../../filesystem/mft.md) | 파일이 디스크에서 바뀐 시각 |
| [오피스 사용 흔적](../../file-folder-usage/microsoft-office/index.md) | 이 PC 의 오피스가 그 문서를 다룬 기록 |
| [볼륨 섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 예전 판 파일의 RSID 목록과 지금 판의 차이 |

시나리오로 이어서 보려면 [이 문서의 날짜를 믿을 수 있나](../../../04-scenarios/activity/document-date-verification.md) 와 [이 파일은 어디서 왔나](../../../04-scenarios/activity/file-origin.md) 를 봅니다.

## 실습

Word 를 설치한 가상 머신을 만들어 직접 해 봅니다. 공개 데이터셋 가운데 docx 가 들어 있는 이미지를 골라도 됩니다.

1. 새 docx 에 글을 넣고 저장합니다. `<w:rsids>` 에 값이 몇 개인지 적습니다.
2. 다시 열어 한 문단 끝에 글을 덧붙이고 저장합니다. 목록에 값이 몇 개 늘었나요? 덧붙인 글자 묶음에 새 값이 붙었나요?
3. 고치지 않고 열었다가 저장만 합니다. 목록이 바뀌나요?
4. 공개 템플릿으로 새 문서 두 개를 만들어 저장합니다. 두 문서의 RSID 목록에 겹치는 값이 있나요?
5. 목록의 값 가운데 본문에 한 번도 쓰이지 않은 값을 찾습니다. 어느 저장 단계에서 생겼는지 짐작하지 말고 실험으로 확인해 봅니다.
6. 결과로 보고서 문장을 하나 씁니다. RSID 로 시각이나 편집자를 말하지 않습니다.

## 참고 문헌

- Microsoft Learn, "Rsids Class (DocumentFormat.OpenXml.Wordprocessing)" (ISO/IEC 29500-1 발췌 포함). https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.rsids
