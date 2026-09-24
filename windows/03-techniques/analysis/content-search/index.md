# 파일 내용 검색 (Content Search)

## 한 줄 요약

파일과 디스크 영역에서 낱말·개인정보 같은 내용을 찾는 기법입니다. 찾기 전에 파일 형식을 가리고, 안쪽 파일을 꺼내고, 글만 뽑으며, 이 묶음은 그 흐름을 다섯 편으로 나눠 다룹니다.

## 왜 중요한가

- **확장자만 보고는 형식을 알 수 없습니다.** 확장자는 파일 이름의 일부라서 이름만 바꾸면 달라지므로, 파일 앞부분의 고정 바이트인 시그니처 (Signature) 를 봐야 실제 형식을 압니다.
- **흔히 쓰는 문서 형식은 다른 파일을 담는 컨테이너 (Container) 입니다.** DOCX·XLSX·PPTX 는 ZIP 이고 DOC·XLS·PPT 는 OLE 복합 파일이라서, 컨테이너를 펼쳐야 본문에 닿습니다.
- **압축된 글은 원시 바이트 검색에 잘 안 걸립니다.** ZIP 항목은 대개 Deflate 로 압축돼 있고 디스크에는 압축된 바이트만 있으므로, 원래 글의 바이트열이 나타나지 않을 수 있습니다.
- **같은 글자도 인코딩마다 바이트가 다릅니다.** 인코딩 하나만 찾으면 다른 인코딩으로 적힌 글을 놓치며, ANSI 코드 페이지는 컴퓨터마다 다를 수 있습니다.
- **그림 속 글은 글자 값이 아닙니다.** 스캔 문서와 화면 캡처는 글자 인식 (Optical Character Recognition, OCR) 을 거쳐야 검색할 수 있습니다.
- **Windows 검색도 본문을 뽑은 뒤에 색인합니다.** Windows Search 는 필터 (IFilter) 로 항목의 본문을 뽑고, 뽑은 글을 낱말로 끊고 정규화한 뒤 전문 색인 (Full-text Index) 에 넣습니다. 필터는 확장자·MIME 형식·CLSID 에 따라 붙습니다.
- **원시 검색은 파일 시스템 밖까지 봅니다.** 원시 검색 (Raw Search) 은 파일 시스템을 해석하지 않으므로 비할당 영역 (Unallocated Space) 도 훑습니다. 공개 도구 bulk_extractor 는 모든 바이트 위치에서 압축 해제를 시도하고, 풀리면 푼 데이터를 처음부터 다시 검사합니다.
- **걸린 것이 없다고 내용이 없었다는 뜻은 아닙니다.** 형식 판단·펼치기·본문 추출·인코딩 가운데 한 단계에서 빠졌을 수 있습니다. 어느 단계까지 거쳤는지 적어 두어야 결과를 설명할 수 있습니다.

## 한눈에 보기

이 묶음은 흐름을 아래 순서로 나눴는데, 이 순서는 이 묶음의 페이지 구성에 따른 것이지 표준 문서가 정한 절차는 아닙니다. 펼쳐 낸 항목은 다시 형식 식별로 돌아가므로, 실제 작업에서는 앞 단계를 여러 번 되풀이합니다.

> 그림 자리: 형식 식별 → 펼치기 → 본문 추출·글자 인식 → 키워드·개인정보 검색으로 이어지는 흐름. 펼쳐 낸 항목이 형식 식별로 되돌아가는 화살표와, 비할당 영역을 원시 검색으로 곧장 보내는 곁가지를 함께 그림

| 단계 | 보는 곳 | 판단 근거 | Windows 버전 | 알려 주는 것 |
|---|---|---|---|---|
| 파일 형식 식별 | 파일 앞부분 바이트. 파일 끝 표시인 트레일러 (Trailer) 를 함께 보는 형식도 있음 | 시그니처와 트레일러 | 해당 없음 (파일 형식 기준) | 실제 형식. 확장자와 내용이 다른 파일 |
| 압축·복합 파일 펼치기 | ZIP (OOXML·ODT·EPUB 등 포함)·OLE 복합 파일·RAR·7z·GZIP 등 | ZIP 의 중앙 디렉터리, OLE 복합 파일의 디렉터리 | 해당 없음 (파일 형식 기준) | 안쪽 항목의 목록·이름·시각·암호화 표시 |
| 본문 추출 | 문서 파일과 펼쳐 낸 항목 | Windows 에서는 확장자·MIME 형식·CLSID 별로 등록된 필터 | 문서에 버전 구분 없음. Windows 7 이후 관리 코드(.NET)로 만든 필터는 막힘 | 서식을 걷어 낸 글과 문서 속성 값 |
| 글자 인식 | 스캔 문서·화면 캡처 같은 그림 | 해상도 (300 DPI 이상에서 잘 됨)·기울기·잡음 | 해당 없음 (Tesseract 문서는 3.0x~5.0.0 을 다룸) | 그림 속 글. 원본에 없는 글자가 섞일 수 있음 |
| 키워드 검색 | 파일, 추출한 글, 비할당 영역·슬랙 같은 원시 영역, 검색 색인 | 인코딩별 바이트열 (UTF-16 LE·UTF-8·CP949 등) | 문서에 버전 구분 없음 | 낱말이 걸린 위치와 앞뒤 글 |
| 개인정보 탐지 | 키워드 검색과 같음 | 형식 + 검증 규칙 (주민등록번호 검증 번호, 카드 번호 Luhn 검사) + 주변 키워드 | 해당 없음 (탐지 규칙 기준) | 개인정보 후보와, 근거에 따라 나눈 신뢰도 등급 |

## 읽는 순서

1. [파일 형식 식별 (File Signature)](file-signature.md) — 시그니처 표를 읽는 법과 자주 보는 시그니처를 정리합니다. ZIP 계열·OLE 복합 파일 계열처럼 시그니처 하나를 여러 형식이 쓰는 경우를 가르는 법과, 확장자와 내용이 다를 때 할 일을 다룹니다.
2. [압축·복합 파일 펼치기 (Archive Expansion)](archive-expansion.md) — ZIP 의 세 레코드와 로컬 파일 헤더의 칸을 따라갑니다. 암호화·UTF-8 이름 플래그, 압축 방식, 항목 시각을 읽는 법과 OLE 복합 파일에서 스트림을 꺼내는 요점을 다룹니다.
3. [본문 추출과 글자 인식 (Text Extraction·OCR)](text-extraction-ocr.md) — Windows 필터가 본문을 뽑는 방식과 필터를 찾는 순서를 다룹니다. 글자 인식 품질을 떨어뜨리는 요인과 페이지 분할 설정도 정리합니다.
4. [키워드 검색 (Keyword Search)](keyword-search.md) — 파일 단위·원시·색인 세 검색 방식을 비교합니다. 인코딩마다 다른 바이트열과, 뽑은 파일에서 오프셋이 어긋나는 경우를 다룹니다.
5. [개인정보 탐지 (PII Detection)](pii-detection.md) — 형식·검증 규칙·주변 키워드 세 요소로 탐지 규칙을 짭니다. 주민등록번호 구조와 검증 번호, 신용카드 번호 정의, 신뢰도 등급을 다룹니다.

## 함께 볼 페이지

- [윈도 검색 색인 DB](../../../02-artifacts/file-folder-usage/windows-search/index.md) — 대상 PC 에 남은 검색 색인을 아티팩트로 읽습니다.
- [OLE 복합 파일](../../../01-foundations/shell-document-formats/compound-file-binary.md) — DOC·XLS·PPT 안의 디렉터리와 섹터 사슬을 따라가는 법입니다.
- [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) — UTF-16 LE·UTF-8·CP949 의 바이트 구성을 다룹니다.
- [문서 메타데이터](../../../02-artifacts/embedded-metadata/document-metadata/index.md) — 본문 밖의 문서 속성과 메타데이터를 다룹니다.
- [NTFS 구조](../../../01-foundations/disk-volume/ntfs/index.md) — 압축 파일·희소 파일처럼 디스크 바이트와 파일 내용이 다르게 놓이는 경우를 봅니다.
- [삭제 데이터 복구](../data-recovery/index.md) — 비할당 영역에서 걸린 내용을 파일로 되살리는 방법을 다룹니다.
- [암호화 증거 다루기](../encrypted-evidence/index.md) — 암호를 걸어 펼치지 못한 파일과 항목을 넘겨받습니다.
- [해시셋 대조와 유사 해시](../hash-set-fuzzy-hash.md) — 검색 전에 이미 아는 파일을 걸러 냅니다.
- [압축 프로그램 사용 기록](../../../02-artifacts/file-folder-usage/7-zip-winrar-bandizip.md) — 압축 프로그램을 쓴 흔적을 다룹니다.
- [도구 결과 교차 검증](../../reporting/tool-validation.md) — 같은 파일을 두 도구로 추출·검색해 결과를 비교합니다.
- [개인정보 파일이 어디 있고 밖으로 나갔나](../../../04-scenarios/exfiltration/pii-exposure.md) — 개인정보 탐지 결과를 사건 흐름에 넣습니다.
- [자료를 밖으로 빼돌렸나](../../../04-scenarios/exfiltration/data-exfiltration/index.md) — 키워드로 찾은 문서가 밖으로 나갔는지 따집니다.

## 참고 문헌

- Gary Kessler, *GCK's File Signatures Table* — https://www.garykessler.net/library/file_sigs_GCK_latest.html
- PKWARE, *.ZIP File Format Specification* (APPNOTE.TXT 6.3.10, 2022-11-01) — https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT
- Microsoft Learn, *[MS-CFB]: Compound File Header* — https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb/05060311-bfce-4b12-874d-71fd4ce63aea
- Microsoft Learn, *Understanding filter handlers in Windows Search* (ms.date 2018-05-31, 갱신 2025-10-03) — https://learn.microsoft.com/en-us/windows/win32/search/-search-ifilter-about
- Tesseract documentation, *Improving the quality of the output* — https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html
- Microsoft Learn, *Code Page Identifiers* — https://learn.microsoft.com/en-us/windows/win32/intl/code-page-identifiers
- simsong, *bulk_extractor* README (GitHub) — https://github.com/simsong/bulk_extractor
- 한국어 위키백과, *주민등록번호* — https://ko.wikipedia.org/wiki/주민등록번호
- Microsoft Learn, *South Korea resident registration number entity definition* (ms.date 2023-09-13, 갱신 2026-06-15) — https://learn.microsoft.com/en-us/purview/sit-defn-south-korea-resident-registration-number
- Microsoft Learn, *Credit card number entity definition* (ms.date 2024-05-28, 갱신 2026-06-15) — https://learn.microsoft.com/en-us/purview/sit-defn-credit-card-number
