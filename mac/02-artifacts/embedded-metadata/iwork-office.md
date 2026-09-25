---
title: "문서 메타데이터"
parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 1880
---

# 문서 메타데이터 (iWork·Office)

iWork 문서는 문서 패키지 안의 `Metadata/` 폴더에 문서 식별자와 버전 기록, 문서 속성을 따로 담아 두고, Word·Excel·PowerPoint 의 Office Open XML 문서는 ZIP 안의 `docProps` 폴더에 작성자·날짜·편집 통계·작성 앱을 담아 두어서, 파일 시스템 시각과 별개로 문서가 스스로 적어 둔 이력을 볼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

**iWork.** iWork '13 문서는 문서 패키지 (document package), 곧 폴더 하나를 파일처럼 다루는 번들을 바탕으로 한 형식이고, 여러 오픈소스 기술 위에 만들었습니다 [1]. 패키지 안에는 본문 객체를 직렬화해 담은 `Index.zip`, 이미지·동영상 같은 미디어를 담은 `Data/`, 가벼운 메타데이터를 담은 `Metadata/` 가 있고, 맨 위에는 미리보기 이미지가 있습니다 [1]. 조사에서 메타데이터로 먼저 보는 곳은 `Metadata/` 이고, 여기에는 버전 기록, 문서 고유 식별자, 문서 속성이 각각 파일로 들어 있습니다 [1].

**Office Open XML.** docx·xlsx·pptx 같은 Office Open XML (OOXML) 문서는 본질적으로 XML 파일 여러 개를 담은 ZIP 이고, 문서 속성은 ZIP 안 `docProps` 폴더의 XML 파일에 들어 있습니다 [2]. ExifTool 은 이 폴더의 XML 에서 찾은 태그를 모두 뽑아 작성자, 날짜, 통계, 문서 속성, 보안 설정으로 보여 줍니다 [2].

두 형식 모두 문서를 저장하는 앱이 문서 안에 함께 적어 두는 값이라서, 파일이 다른 곳으로 복사되거나 메일로 전달되어도 문서 안에 그대로 따라갑니다. 옛 이진 형식(.doc·.xls)의 속성은 이 페이지에서 다루지 않습니다.

## 위치와 버전별 차이

문서 안에 들어 있는 값이라서 정해진 시스템 경로가 없고, 문서 파일이 곧 위치입니다.

| 형식 | 속성이 있는 곳 | 다루는 범위 | 출처 |
|---|---|---|---|
| iWork | 패키지 안 `Metadata/` | iWork '13 형식 | [1] |
| iWork | 패키지 안 `Index.zip` 의 `.iwa` 파일 | iWork '13 형식 | [1] |
| OOXML | ZIP 안 `docProps` 폴더의 XML | ExifTool 이 뽑는 태그 이름 | [2] |

이 페이지의 iWork 구조는 iWork '13 형식 기준이고, 그 뒤 버전의 구조는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 최근 검체에서 문서가 패키지 폴더가 아니라 파일 하나로 보이면 이 페이지의 구조를 그대로 대입하지 말고 먼저 안을 열어 구성이 같은지 봅니다. macOS 버전에 따라 이 값들이 달라지는지도 검체에서 확인합니다.

## 구조

### iWork 문서 패키지

| 위치 | 담긴 것 |
|---|---|
| `Data/` | 이미지·동영상 같은 미디어 |
| `Index.zip` | 직렬화한 객체(`.iwa` 파일들) |
| `Metadata/BuildVersionHistory.plist` | 버전 기록 |
| `Metadata/DocumentIdentifier` | 문서 고유 식별자 |
| `Metadata/Properties.plist` | 문서 속성 |
| `preview.jpg`, `preview-web.jpg`, `preview-micro.jpg` | 패키지 맨 위의 미리보기 이미지 |

`Metadata/` 의 두 plist 는 속성 목록 파일이라서 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에 적은 방법으로 읽습니다. 다만 그 안의 키 이름과 값, 예를 들어 작성 앱 버전을 어떤 키로 적는지는 공개 자료에 없어 검체에서 확인합니다. 식별자 값을 읽는 일반적인 방법은 [식별자 읽기 (UUID·UID·GUID)](../../01-foundations/value-decoding/uuid-uid.md)에서 다룹니다.

`Index.zip` 안에는 `.iwa` 파일이 여러 개 있고, 예를 들면 `AnnotationAuthorStorage.iwa`, `CalculationEngine.iwa`, `Document.iwa`, `DocumentStylesheet.iwa`, `MasterSlide-1.iwa` 가 있습니다 [1]. `.iwa` 는 Protobuf 스트림을 Snappy 스트림으로 감싼 자체 형식이라서 [1], 읽으려면 ZIP 을 풀고, Snappy 조각을 풀고, 그 결과를 Protobuf 로 풀어야 합니다.

Snappy 조각은 머리 4바이트로 시작하고, 첫 바이트는 조각 종류이고 다음 3바이트는 조각 길이를 24비트 리틀 엔디언 정수로 적은 값입니다 [1]. iWork 에서는 조각 종류가 실제로 늘 0x00(Snappy 압축 조각)이고, 표준 Snappy 프레임 형식과 달리 스트림 식별자 조각과 CRC-32C 체크섬을 넣지 않아서 [1], 표준 Snappy 프레임을 기대하는 도구로는 바로 풀리지 않을 수 있습니다.

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0x00 | 1 | 조각 종류, 0x00 = 압축 |
| 0x01 | 3 | 조각 길이, 24비트 리틀 엔디언 |

암호를 건 iWork 문서는 패키지 안 파일 거의 전부를 AES128 과 PKCS7 채움으로 암호화합니다 [1]. 암호화된 증거를 다루는 절차는 [암호화된 증거 다루기 (Encrypted Evidence)](../../03-techniques/analysis/encrypted-evidence/index.md)를 따릅니다.

### OOXML 문서 속성

ExifTool 이 `docProps` 에서 뽑아 보여 주는 태그 가운데 조사에서 자주 보는 것을 묶으면 아래와 같습니다 [2].

| 갈래 | 태그 |
|---|---|
| 작성자 | Creator, LastModifiedBy, Manager |
| 날짜 | CreateDate, ModifyDate, LastPrinted |
| 통계 | Pages, Words, Characters, Paragraphs, Lines, Slides, HiddenSlides, TotalEditTime |
| 문서 속성 | Application, AppVersion, Company, Template, Revision, Keywords, Subject, Category |
| 보안 | DocSecurity |

DocSecurity 는 숫자 값이고, ExifTool 은 0 = None, 1 = Password protected, 2 = Read-only recommended, 4 = Read-only enforced, 8 = Locked for annotations 로 풀어 보여 줍니다 [2]. 위 태그가 `docProps` 안 어느 XML 파일의 어떤 요소에서 오는지는 공개 자료에 나와 있지 않아서, 이 페이지에서는 ExifTool 태그 이름으로 적습니다.

## 증거로서 의미

**증명하는 것.** 문서 안에 적힌 작성자 이름, 날짜, 편집 통계, 작성 앱, 보안 설정을 보여 줍니다. OOXML 이면 처음 만든 사람으로 적힌 이름(Creator)과 마지막으로 고친 사람으로 적힌 이름(LastModifiedBy)을 나눠 볼 수 있고, Application·AppVersion 으로 어떤 앱이 저장했다고 적혀 있는지, Template·Company 로 어떤 서식과 조직 설정에서 나왔는지 단서를 얻습니다 [2]. Revision 과 TotalEditTime 은 문서를 몇 번 고쳤고 얼마나 편집했는지 적힌 값이고, 본문 길이와 함께 보면 작성 이력을 가늠하는 데 씁니다 [2]. iWork 문서는 `DocumentIdentifier` 로 문서마다 고유 식별자를 적어 두고 [1], 두 파일의 식별자가 같으면 한 문서에서 갈라져 나온 사본일 가능성이 있어 살펴볼 만합니다. 미리보기 이미지가 패키지 맨 위에 따로 있어서 [1], 본문을 풀기 전에 문서 겉모습을 먼저 볼 수 있습니다.

**증명하지 못하는 것.** Creator·LastModifiedBy 에 적힌 이름은 문서 안의 문자열이라서, 그 사람이 실제로 문서를 만들거나 고쳤다는 뜻은 아닙니다. 앱이 그 이름을 어디서 가져와 적는지는 공개 자료에 없습니다. 문서 안의 날짜도 파일 안에 적힌 값일 뿐이라서, 그 시각에 그 맥에서 문서를 저장했다는 것까지 보여 주지는 않습니다. `AnnotationAuthorStorage.iwa` 는 파일 이름만 보면 주석 작성자와 관련 있어 보이지만, 안에 무엇이 들어 있는지 공개된 분석 자료가 없어서 작성자 근거로 쓰지 않습니다.

보고서에는 "이 사람이 문서를 만들었다" 가 아니라 "이 문서의 속성에는 Creator 가 이 이름, CreateDate 가 이 값, Application 이 이 값으로 적혀 있다" 처럼 문서에 적힌 만큼만 씁니다.

## 시각 해석

OOXML 문서에서 ExifTool 이 보여 주는 날짜 태그는 만든 시각(CreateDate), 고친 시각(ModifyDate), 마지막으로 인쇄한 시각(LastPrinted) 세 가지입니다 [2]. 이 값의 저장 형식과 UTC 여부, TotalEditTime 의 단위는 검체의 원래 XML 에서 확인합니다. 날짜를 보고서에 옮길 때는 도구가 보여 준 값을 그대로 옮기지 말고, 원래 XML 값을 함께 적은 뒤 파일 시스템 시각이나 다른 기록과 대 봐서 시간대를 정합니다.

iWork 쪽은 `BuildVersionHistory.plist` 가 버전 기록이고 [1], 그 안에 시각 값이 있는지와 `Properties.plist` 에 날짜 키가 있는지는 검체에서 확인합니다.

문서 안의 날짜는 파일 시스템이 적는 만든 시각·수정 시각과 따로 움직입니다. 문서가 복사되면 파일 시스템 시각은 새로 생길 수 있지만 문서 안 날짜는 그대로 따라가고, 그래서 두 쪽을 나란히 놓고 어긋나는 곳을 찾는 방법이 쓸모 있습니다. 이 비교를 처음부터 끝까지 따라가는 흐름은 [이 문서의 날짜를 믿을 수 있나 (Document Date)](../../04-scenarios/activity/document-date.md)에 정리했습니다.

## 함정과 한계

**문서 속성은 고칠 수 있는 값입니다.** 작성자와 날짜는 문서 안에 적힌 데이터라서, 이 값만으로 조작 여부를 가리지 않습니다. 문서 속성의 날짜, 파일 시스템 시각, 문서 버전 데이터베이스, 다운로드·메일 기록이 서로 맞는지 봅니다. Revision 이나 TotalEditTime 이 문서 길이에 비해 지나치게 작거나 크면 다른 문서를 복사해 고쳤을 가능성을 살펴볼 계기로 삼습니다.

**iWork 구조는 '13 형식 기준입니다.** 이 페이지의 iWork 설명은 iWork '13 형식 기준이고 [1], 그 뒤 버전에서 구성이 바뀌었는지는 검체에서 확인합니다.

**ExifTool 태그 이름과 XML 요소 이름은 다를 수 있습니다.** 이 페이지의 OOXML 태그는 ExifTool 이 붙인 이름이고 [2], 원래 XML 요소 이름과 이름공간은 ZIP 을 풀어 직접 확인합니다. 다른 도구의 출력과 견줄 때 이름이 다르다고 다른 값으로 여기지 않습니다.

**암호를 건 문서는 속성을 읽지 못할 수 있습니다.** iWork 는 암호를 건 문서의 패키지 안 파일 거의 전부를 AES128 로 암호화해서 [1], `Metadata/` 의 속성도 풀지 않고는 읽지 못할 수 있습니다. 어떤 파일이 암호화에서 빠지는지는 공개 자료에 없어 검체에서 확인합니다. OOXML 의 DocSecurity 값은 문서에 적힌 보안 설정을 보여 줄 뿐이라서 [2], 파일이 실제로 암호화되어 있는지는 파일을 열어 따로 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세를 바탕으로 만든 예시이고, 특정 검체에서 나온 값이 아닙니다. `Index.zip` 을 풀어 `.iwa` 파일 하나를 헥스로 열면 맨 앞 4바이트가 Snappy 조각 머리입니다 [1].

```text
00                조각 종류: 0x00 = 압축
2A 01 00          조각 길이: 리틀 엔디언으로 읽어 0x00012A = 298바이트
...               이어지는 298바이트가 Snappy 로 압축한 데이터
```

길이 3바이트는 리틀 엔디언이라서 거꾸로 읽어 `00 01 2A` 로 놓아야 올바른 값이 나오고, 이 길이만큼이 조각 데이터입니다. 조각을 Snappy 로 풀면 Protobuf 스트림이 나오고 [1], Protobuf 풀이는 이 페이지 범위 밖입니다.

### 공개 도구로 한 번

1. 원본 증거 대신 사본에서 문서를 꺼냅니다. 이미지를 다루는 절차는 [맥 증거 확보 (Acquisition)](../../03-techniques/process-acquisition/evidence-acquisition/index.md)를 따릅니다.
2. OOXML 문서는 ExifTool 로 읽어 작성자·날짜·통계·문서 속성·DocSecurity 태그를 적습니다 [2].
3. 같은 문서를 ZIP 으로 풀어 `docProps` 폴더의 XML 을 직접 열고, 도구가 보여 준 값이 원래 XML 에 그대로 있는지 확인합니다.
4. iWork 문서는 패키지 안 `Metadata/` 의 두 plist 와 `DocumentIdentifier` 를 읽고, 맨 위의 미리보기 이미지를 봅니다 [1].
5. 본문이 필요하면 `Index.zip` 을 풀어 `.iwa` 파일의 Snappy 조각을 풀고 Protobuf 로 해석합니다 [1].
6. 문서의 파일 시스템 시각과 확장 속성을 함께 적어 둡니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [스포트라이트 (Spotlight)](../file-folder-usage/spotlight/index.md) | 색인에 남은 작성자·작성 앱 속성 |
| [문서 버전 (DocumentRevisions-V100)](../file-folder-usage/document-revisions.md) | 문서를 저장할 때마다 남은 예전 버전 |
| [최근 항목 (Shared File Lists)](../file-folder-usage/recent-items/index.md) | 문서를 연 흔적 |
| [빠른 보기 섬네일 캐시 (QuickLook)](../file-folder-usage/quicklook-thumbnails.md) | 문서 겉모습이 남은 섬네일 |
| [다운로드 출처 속성 (kMDItemWhereFroms)](../filesystem/where-froms.md) | 내려받은 문서면 받은 주소 |
| [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) | 받은 시각과 받은 앱 |
| [애플 메일 (Apple Mail)](../mail/apple-mail/index.md) | 첨부로 들어오거나 나간 문서 |
| [아이클라우드 드라이브 (iCloud Drive·CloudDocs)](../cloud-apps/icloud-drive.md) | 동기화로 들어온 문서 |

문서를 누가 언제 열었는지 따라가는 순서는 [이 파일을 누가 언제 열었나 (File Access)](../../04-scenarios/activity/file-access.md)에, 문서가 어디서 왔는지는 [이 파일은 어디서 왔나 (File Origin)](../../04-scenarios/activity/file-origin.md)에 정리했습니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 문서 파일이 들어 있는 macOS 이미지를 골라 아래 질문을 풀어 봅니다.

1. docx 문서 하나에서 Creator 와 LastModifiedBy 를 찾아 적고, 두 이름이 같은지 다른지와 그 이름이 검체의 사용자 계정 이름과 맞는지 확인할 수 있나요?
2. 같은 문서의 CreateDate·ModifyDate 를 파일 시스템의 만든 시각·수정 시각과 나란히 놓으면 어느 쪽이 먼저인가요? 어긋난다면 어떤 경로로 설명할 수 있나요?
3. Application·AppVersion 값으로 문서를 저장한 앱을 짐작하고, 그 앱이 검체에 설치되어 있는지 확인할 수 있나요?
4. iWork 문서가 있다면 `Metadata/` 안 세 파일을 찾아 열 수 있나요? 다른 iWork 문서와 `DocumentIdentifier` 가 겹치는 경우가 있나요?
5. `.iwa` 파일 하나의 첫 4바이트를 읽어 조각 종류와 길이를 직접 계산할 수 있나요?

## 참고 문헌

1. Sean Patrick O'Brien, "iWork '13 File Format" (GitHub, obriensp/iWorkFileFormat) — https://github.com/obriensp/iWorkFileFormat/blob/master/Docs/index.md
2. ExifTool, "OOXML Tags" — https://exiftool.org/TagNames/OOXML.html
