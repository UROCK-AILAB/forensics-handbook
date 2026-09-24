# 본문 추출과 글자 인식 (Text Extraction·OCR)

## 한 줄 요약

문서 파일에서 서식을 걷어 내고 글만 뽑아 검색할 수 있게 만들고, 그림 속 글자는 글자 인식 (Optical Character Recognition, OCR) 으로 글로 바꿉니다.

이 글은 [파일 내용 검색 (Content Search)](index.md) 묶음의 한 편입니다.
ZIP 이나 OLE 복합 파일은 먼저 [압축·복합 파일 펼치기](archive-expansion.md) 를 거친 뒤 이 단계로 옵니다.

## 언제 쓰나

- **문서 형식 파일을 검색할 때** 씁니다. 문서 파일에는 글과 서식 정보가 섞여 있어서 글만 뽑아야 낱말 단위로 찾을 수 있습니다.
- **원시 바이트로 문장이 안 잡힐 때** 씁니다. OLE 복합 파일은 4,096바이트보다 작은 스트림을 64바이트 미니 섹터로 나눠 저장합니다. 그래서 한 스트림의 글이 여러 조각으로 흩어져 있을 수 있습니다. 스트림을 이어 붙여 뽑아야 문장이 이어집니다.
- **스캔 문서·화면 캡처를 검색할 때** 씁니다. 그림 파일에는 글이 글자 값으로 들어 있지 않아서 글자 인식을 거쳐야 검색할 수 있습니다.

## 본문 추출: Windows 의 필터 방식

Windows Search 가 본문을 뽑는 방식은 추출기가 무엇을 하는지 보여 주는 공개된 예입니다.
근거는 Microsoft Learn 의 "Understanding filter handlers in Windows Search" 입니다.

### 필터가 하는 일

필터 처리기 (Filter Handler) 는 IFilter 인터페이스를 구현한 구성 요소로, 문서에서 글과 속성을 찾아냅니다.
문서 속 서식을 걸러 내고 글을 조각 (Chunk) 단위로 뽑으며, 뽑을 때 글의 위치 정보도 남기고 문서 속성 값도 조각으로 뽑습니다.
Windows Search 는 IFilter::GetText 가 돌려준 글을 낱말로 끊고, 정규화한 뒤 색인에 저장합니다.

IFilter 의 메서드는 다섯 개입니다.

| 메서드 | 하는 일 |
|---|---|
| Init | 필터링을 시작합니다 |
| GetChunk | 다음 조각으로 옮겨 가고 그 조각의 설명을 돌려줍니다 |
| GetText | 현재 조각의 글을 돌려줍니다 |
| GetValue | 현재 조각의 속성 값을 돌려줍니다 |
| BindRegion | 예약돼 있습니다 |

문서 속에 든 개체 (Embedded Object) 에 필터를 붙일 때는 BindIFilterFromStorage(IStorage 개체용)·BindIFilterFromStream·LoadIFilter 를 씁니다.

### 필터를 찾는 순서

필터는 레지스트리에서 이 순서로 찾습니다.

1. `HKLM\SOFTWARE\Classes\.<확장자>\PersistentHandler` 가 있으면 그 값(GUID)을 씁니다.
2. 없으면 문서 형식의 CLSID 에 등록된 PersistentHandler 를 씁니다.
3. `HKLM\SOFTWARE\Classes\CLSID\<PersistentHandler GUID>\PersistentAddinsRegistered\{89BCB740-6119-101A-BCB7-00DD010655AF}` 에서 IFilter 를 찾습니다. `{89BCB740-…}` 은 IFilter 인터페이스의 GUID 이고, 이 키의 기본값이 필터 클래스의 CLSID 입니다.

문서의 예를 따르면 `.htm` 의 PersistentHandler 는 `{EEC97550-47A9-11CF-B952-00AA0051FE20}` 입니다.
그 아래 PersistentAddinsRegistered 키의 기본값은 `{E0CA5340-4534-11CF-B952-00AA0051FE20}` 입니다.
문서는 이 예에서 HTML 용 IFilter DLL 이 `nlhtml.dll` 이라고 적습니다.

분석 대상 PC 의 레지스트리에서 이 경로를 따라가면, 확장자마다 어떤 필터가 등록돼 있었는지 볼 수 있고, 색인에 어떤 파일의 본문이 없을 때 까닭을 찾는 출발점이 됩니다.
레지스트리 파일 자체는 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에서, 색인은 [윈도 검색 색인 DB](../../../02-artifacts/file-folder-usage/windows-search/index.md) 에서 다룹니다.

### 필터를 돌리는 프로세스

Windows Search 는 필터를 SearchFilterHost.exe 안에서 돌리는데, 이 프로세스는 항목의 클래스·인지 형식 (Perceived Type)·확장자에 등록된 IFilter 에 붙습니다.
이 격리 프로세스는 Local System 보안 문맥에서 권한을 줄여 돌며 디스크·네트워크·사용자 화면·클립보드에는 접근하지 못합니다.
작업 개체 (Job Object) 아래에서 돌기 때문에 자식 프로세스를 만들지 못하고, 작업 집합 (Working Set) 은 100MB 로 제한됩니다.
Windows 7 이후로는 관리 코드(.NET)로 만든 필터가 막힙니다.

### 언어와 낱말 끊기

한 파일 안에서도 언어 (LCID) 가 바뀔 수 있는데, Windows Search 가 LCID 를 보고 낱말 끊기 (Word Breaker) 를 고르기 때문에 필터는 LCID 가 바뀔 때마다 새 조각을 시작해야 합니다.
필터가 언어를 모르면 LCID 0 을 돌려주고, 그러면 Windows Search 는 언어 자동 감지 (LAD) 를 쓰며, 그래도 못 찾으면 시스템 기본 로캘을 씁니다.
언어와 맞지 않는 낱말 끊기를 쓰면 검색 결과가 나빠집니다.

한국어와 영어가 섞인 문서라면 이 점이 검색 결과에 영향을 줄 수 있습니다.
색인 검색과 원문 검색을 나란히 돌려 보는 방법은 [키워드 검색](keyword-search.md) 에 있습니다.

## 형식마다 본문이 있는 곳

- **OOXML(DOCX·XLSX·PPTX)** 은 ZIP 입니다. 먼저 펼쳐야 본문 XML 에 닿습니다.
- **OLE 복합 파일(DOC·XLS·PPT 등)** 은 스트림을 이어 붙여야 글이 이어집니다. 스트림을 따라가는 방법은 [OLE 복합 파일](../../../01-foundations/shell-document-formats/compound-file-binary.md) 에 있습니다.
- **그 밖의 문서 형식** 은 형식마다 본문 위치와 저장 방식이 다릅니다. 형식에 맞는 추출기를 씁니다. 문서 속성과 메타데이터는 [문서 메타데이터](../../../02-artifacts/embedded-metadata/document-metadata/index.md) 에서 다룹니다.

## 글자 인식 (OCR)

공개 OCR 엔진 Tesseract 의 문서 "Improving the quality of the output" 을 기준으로 정리합니다.
이 문서는 Tesseract 3.05·3.0x·4.00·4.x·5.0.0 을 언급합니다.

### 인식 품질을 떨어뜨리는 것

| 요인 | 문서의 설명 | 대응 |
|---|---|---|
| 해상도 | DPI 가 적어도 300 인 이미지에서 가장 잘 동작합니다. 글자 크기(대문자 높이, 픽셀)에도 알맞은 값이 있습니다 | 크기를 다시 맞춥니다 (Rescaling) |
| 배경 밝기 | 내부에서 Otsu 알고리즘으로 흑백 변환(이진화)을 합니다. 배경 밝기가 고르지 않으면 결과가 나쁠 수 있습니다 | 5.0.0 에서 Adaptive Otsu 와 Sauvola 이진화가 추가됐습니다 |
| 잡음 | 밝기·색의 무작위 변화는 글을 읽기 어렵게 합니다 | 잡음을 줄입니다 |
| 글자 굵기 | 굵거나 가는 글자는 인식이 어렵습니다 | 팽창 (Dilation)·침식 (Erosion) 으로 보정합니다. 번진 잉크는 침식으로 보정합니다 |
| 기울기 | 페이지가 기울면 줄 나누기 품질이 크게 떨어집니다. 인식 품질도 크게 떨어집니다 | 기울기를 바로잡습니다 |
| 테두리 | 스캔 페이지 가장자리의 검은 테두리를 글자로 잘못 읽을 수 있습니다. 반대로 글 둘레의 빈 여백이 너무 넓으면 "빈 페이지 (empty page)" 문제가 날 수 있습니다. 글자 하나나 낱말 하나를 큰 바탕 위에서 읽을 때 특히 그렇습니다 | 검은 테두리는 잘라 냅니다. 여백은 알맞게 줄입니다 |
| 투명 채널 | 3.0x 는 알파 채널을 미리 없애야 합니다. 4.00 이후는 자동으로 처리합니다. 영화 자막 같은 경우에는 문제가 생길 수 있습니다 | 알파 채널을 없앤 뒤 인식해 봅니다 |

### 페이지 분할 방식

`--psm` 은 페이지를 어떻게 나눠 읽을지 정합니다.
값은 0~13 의 14가지이고, 기본값은 3 입니다.

| 값 | 뜻 | 쓰는 곳 |
|---|---|---|
| 0 | 방향·문자 체계 감지 (OSD) 만 합니다 | 페이지 방향을 먼저 알아볼 때 |
| 1 | OSD 를 곁들인 자동 분할 | 방향이 섞인 스캔 |
| 3 | 기본값 | 일반 문서 |
| 7 | 이미지를 한 줄로 취급 | 잘라 낸 한 줄 |
| 8 | 한 낱말로 취급 | 잘라 낸 낱말 |
| 10 | 한 글자로 취급 | 잘라 낸 글자 |
| 11 | 드문드문 흩어진 글. 순서 없이 최대한 찾습니다 | 화면 캡처·영수증처럼 글이 흩어진 그림 |

"쓰는 곳" 칸은 뜻에서 끌어낸 예입니다.

### 사전과 글자 제한

- 사전에 없는 낱말이 많으면 사전을 끄는 편이 인식률을 높일 수 있습니다. `load_system_dawg` 와 `load_freq_dawg` 를 false 로 둡니다.
- 인식할 글자를 제한할 때는 `tessedit_char_whitelist` 를 씁니다. 숫자만 뽑을 때 쓸 수 있습니다. 주민등록번호·카드 번호를 찾는 일은 [개인정보 탐지](pii-detection.md) 에서 다룹니다.

## 절차

1. [파일 형식 식별](file-signature.md) 결과로 파일을 나눕니다. 글 파일, 문서, 그림, 컨테이너로 나눕니다.
2. 컨테이너는 먼저 펼칩니다.
3. 문서는 형식에 맞는 추출기로 본문과 속성을 따로 뽑습니다.
4. 뽑은 글은 원본 파일 경로와 짝지어 저장합니다. 추출기 이름과 판도 함께 적습니다.
5. 그림은 해상도를 먼저 확인합니다. 300 DPI 보다 낮으면 크기를 키워 봅니다.
6. 기울기·테두리·배경 밝기·글자 굵기를 보고 필요한 전처리를 합니다.
7. 페이지 모양에 맞는 `--psm` 값을 고릅니다.
8. 찾을 글자가 숫자뿐이면 글자를 제한합니다. 사전에 없는 낱말이 많으면 사전을 끕니다.
9. 인식 결과에서 걸린 곳은 원본 그림과 눈으로 맞춰 봅니다.
10. 인식에 쓴 엔진·판·언어 데이터·설정 값을 적습니다.

## 도구

- **Windows 필터 (IFilter)**: 그 PC 에 등록된 필터가 본문을 뽑는데, 분석용 PC 에서 쓰면 분석용 PC 에 설치된 필터에 따라 결과가 달라질 수 있습니다.
- **Tesseract**: 공개 OCR 엔진입니다. 한국어 문서는 쓰는 판과 언어 데이터로 시험 그림을 먼저 인식해 봅니다.
- **형식별 공개 추출 라이브러리**: 형식마다 여러 가지가 있습니다. 같은 파일을 두 도구로 뽑아 결과를 비교합니다. 방법은 [도구 결과 교차 검증](../../reporting/tool-validation.md) 에 있습니다.

## 함정과 한계

- **추출한 글은 원본 바이트가 아닙니다.** 필터는 서식을 걸러 내고 글만 남깁니다. 보고서에 원본 위치를 적으려면 추출기가 남긴 위치 정보를 함께 보관합니다.
- **색인에 본문이 없어도 파일에 글이 없다는 뜻이 아닙니다.** 필터가 없거나 필터가 실패했을 수 있습니다. 이 점은 [윈도 검색 색인 DB](../../../02-artifacts/file-folder-usage/windows-search/index.md) 에서도 다룹니다.
- **언어를 잘못 고르면 낱말이 잘못 끊깁니다.** 낱말 끊기가 언어와 맞지 않으면 검색 결과가 나빠집니다.
- **OCR 결과에는 원본에 없는 글자가 섞이거나 글자가 빠질 수 있습니다.** 위 표의 요인이 하나라도 있으면 인식 품질이 떨어집니다. 숫자 0 과 글자 O 처럼 모양이 비슷한 글자가 바뀌면 검증 규칙이 틀어질 수 있습니다.
- **OCR 결과는 설정에 따라 달라집니다.** 같은 그림도 해상도·`--psm`·사전 설정을 바꾸면 결과가 바뀝니다.

## 결과를 어떻게 해석하나

- 추출한 글에서 찾은 낱말은 "이 추출기가 이 파일에서 뽑은 글에 이 낱말이 있다" 로 씁니다.
- OCR 로 찾은 낱말은 "이 엔진·판·설정으로 인식한 글에서 찾았고, 원본 그림에서 눈으로 확인했다" 로 씁니다.
- 찾지 못한 경우는 "없다" 가 아니라 "이 방법으로 찾지 못했다" 로 씁니다. 추출이나 인식이 실패했을 수 있기 때문입니다.

## 참고 문헌

- Microsoft Learn, "Understanding filter handlers in Windows Search" (ms.date 2018-05-31, 갱신 2025-10-03) — https://learn.microsoft.com/en-us/windows/win32/search/-search-ifilter-about
- Tesseract documentation, "Improving the quality of the output" — https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html
- Gary Kessler, "GCK's File Signatures Table" (최종판) — https://www.garykessler.net/library/file_sigs_GCK_latest.html
- Microsoft Learn, "[MS-CFB]: Compound File Header" — https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb/05060311-bfce-4b12-874d-71fd4ce63aea
