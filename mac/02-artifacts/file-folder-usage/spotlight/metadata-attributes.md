---
title: "메타데이터 속성"
parent: "스포트라이트"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 850
---

# 메타데이터 속성 (kMDItem)

스포트라이트 색인은 항목마다 `kMDItem` 으로 시작하는 이름의 속성 값을 담고 있고, 그 가운데 마지막 사용 시각·출처·작성자 같은 값은 파일을 어디서 받아 언제 썼는지 따져 볼 단서가 됩니다.

## 무엇을 기록하나

메타데이터 속성 (Metadata Attribute)은 파일의 이름·종류·시각·작성자처럼 파일을 설명하는 값에 붙인 이름이고, 스포트라이트 색인은 이 이름과 값을 짝으로 저장합니다 [1][2]. 이름은 `kMDItemWhereFroms`, `kMDItemLastUsedDate` 처럼 `kMDItem` 으로 시작합니다 [2][3]. 값이 색인 파일 안에 어떤 형식으로 들어 있는지는 [색인 저장소 구조 (.Spotlight-V100·store.db)](store-structure.md)에서 다루고, 이 페이지는 속성마다 무엇을 뜻하는지를 다룹니다.

아래 공통 속성은 OS X 10.4 이후에 쓰입니다 [3][4]. 표의 형식 열은 CF 형식 이름입니다.

## 주요 속성 (Apple 문서에 있는 것)

### 시각

| 속성 | 뜻 | 형식 |
|---|---|---|
| `kMDItemLastUsedDate` | 파일을 마지막으로 쓴 날짜·시각. 더블클릭하거나 LaunchServices에 열기를 요청해 파일을 열 때마다 LaunchServices가 자동으로 갱신 [3][4] | CFDate |
| `kMDItemContentCreationDate` | 내용을 만든 시각 [3][4] | CFDate |
| `kMDItemContentModificationDate` | 내용을 고친 시각 [3][4] | CFDate |
| `kMDItemFSCreationDate` | 파일 시스템 쪽 생성 시각(Apple 문서 표현은 "파일 내용을 만든 날짜") [3] | CFDate |
| `kMDItemFSContentChangeDate` | 파일 시스템 쪽 내용 변경 시각 [3] | CFDate |
| `kMDItemAttributeChangeDate` | 메타데이터 속성이 마지막으로 바뀐 시각 [3][4] | CFDate |

### 출처·이름·종류

| 속성 | 뜻 |
|---|---|
| `kMDItemWhereFroms` | 어디서 얻었나. 내려받은 파일은 URL, 메일로 받은 파일은 보낸 사람 주소·제목 등. CFString 배열 [3][4] |
| `kMDItemFSName` | 파일 이름(CFString) [3] |
| `kMDItemDisplayName` | 지역화된 이름 [3] |
| `kMDItemPath` | 전체 경로. 값은 읽을 수 있지만 쿼리·정렬에는 쓰지 못함 [3] |
| `kMDItemContentType` | UTI(예: `public.jpeg`) [3] |
| `kMDItemContentTypeTree` | UTI 계층 배열 [3] |
| `kMDItemKind` | 종류 설명 [3] |
| `kMDItemCFBundleIdentifier` | 항목이 번들이면 그 번들 ID [4] |

`kMDItemWhereFroms` 로 내려받은 파일의 출처를 따지는 방법은 [다운로드 출처 속성 (kMDItemWhereFroms)](../../filesystem/where-froms.md)에서 따로 다룹니다. 번들 ID를 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다.

### 작성자·앱·내용

| 속성 | 뜻 |
|---|---|
| `kMDItemAuthors` | 작성자 배열 [3][4] |
| `kMDItemCreator` | 내용을 만든 앱(예: "Pages") [3][4] |
| `kMDItemEncodingApplications` | 변환에 쓴 앱(예: PDF의 "Distiller") [3][4] |
| `kMDItemFinderComment` | Finder 설명 [3][4] |
| `kMDItemComment` | 파일에 붙은 주석. Finder에는 보이지 않음 [3][4] |
| `kMDItemTextContent` | 문서 본문의 텍스트 표현. 앱은 쿼리에는 쓸 수 있지만 값을 직접 읽지는 못함 [3][4] |
| `kMDItemTitle`, `kMDItemSubject` | 제목, 주제 [4] |
| `kMDItemAuthorEmailAddresses`, `kMDItemRecipientEmailAddresses` | 작성자·받는 사람 메일 주소 [4] |
| `kMDItemPhoneNumbers` | 전화번호 [4] |
| `kMDItemCity`, `kMDItemStateOrProvince`, `kMDItemCountry` | 도시, 주·도, 나라 [4] |
| `kMDItemURL` | URL [4] |

## Apple 문서에 없지만 도구가 뽑는 속성

공개 도구 mac_apt의 SPOTLIGHT 플러그인은 아래 속성도 뽑아 줍니다 [2].

```
kMDItemUseCount            kMDItemUsedDates           kMDItemDateAdded
kMDItemDownloadedDate      kMDItemUserCreatedDate     kMDItemUserModifiedDate
kMDItemUserPrintedDate     kMDItemUserCreatedUserHandle
kMDItemUserModifiedUserHandle                          kMDItemUserPrintedUserHandle
_kMDItemOwnerUserID        _kMDItemOwnerGroupID       _kMDItemFileName
_kMDItemContentChangeDate  _kMDItemCreationDate       kMDItemLatitude
kMDItemLongitude           kMDItemTimestamp           kMDItemGPSDateStamp
kMDItemPhysicalSize        kMDItemLogicalSize         kMDItemAlternateNames
kMDItemMediaTypes
```

현행 Apple 문서 "Common Metadata Attribute Keys" 에도 `kMDItemDateAdded`, `kMDItemUseCount`, `kMDItemUsedDates`, `kMDItemDownloadedDate` 는 없습니다 [4]. `kMDItemUsedDates` 는 날짜·시각 값의 배열이고, `kMDItemDownloadedDate` 는 날짜·시각 값(값 형식 0x0c)입니다 [1]. 이 속성들이 언제 갱신되는지, 예를 들어 무엇이 `kMDItemUseCount` 를 올리는지나 `kMDItemUsedDates` 에 날짜가 어떤 단위로 쌓이는지는 공개된 설명이 없습니다. 이름만 보고 뜻을 짐작해 보고서에 쓰지 않고, 쓰려면 알려진 동작을 재현해서 값이 어떻게 바뀌는지 먼저 확인합니다. 재현 시험은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)의 방법을 따릅니다.

## 시각 해석

색인 안의 날짜 값은 2001-01-01 기준 초를 64비트 실수로 적은 Cocoa 시각입니다 [1]. 같은 저장소의 레코드 갱신 시각은 기준이 다른 유닉스 마이크로초라서, 두 값을 구분하는 법은 [색인 저장소 구조 (.Spotlight-V100·store.db)](store-structure.md)의 시각 해석 절에서 봅니다. 시각 체계 자체는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에서 설명합니다.

속성마다 바뀌는 때가 다릅니다. `kMDItemLastUsedDate` 는 LaunchServices가 파일을 열 때 갱신되고 [3][4], `kMDItemAttributeChangeDate` 는 메타데이터 속성이 바뀔 때 갱신됩니다 [3][4]. `kMDItemContentCreationDate`·`kMDItemContentModificationDate` 는 내용 쪽 시각이고 `kMDItemFSCreationDate`·`kMDItemFSContentChangeDate` 는 파일 시스템 쪽 시각입니다 [3]. 두 쪽 값이 각각 어떤 동작에 따라 바뀌는지는 자세히 알려져 있지 않아서, 문서 날짜를 따질 때는 [이 문서의 날짜를 믿을 수 있나 (Document Date)](../../../04-scenarios/activity/document-date.md)의 절차로 여러 값을 함께 봅니다.

## 증거로서 의미

### 증명하는 것

색인에 `kMDItemLastUsedDate` 가 있으면, 색인이 그 값을 기록한 때까지 LaunchServices를 거쳐 그 파일을 연 일이 있었고 마지막으로 연 시각이 그 값이라는 기록이 됩니다 [3][4]. `kMDItemWhereFroms` 는 파일을 얻은 URL이나 메일 정보를 [3][4], `kMDItemCreator`·`kMDItemEncodingApplications` 는 내용을 만들거나 변환한 앱 이름을 알려 줍니다 [3][4].

### 증명하지 못하는 것

`kMDItemLastUsedDate` 의 갱신 조건으로 알려진 것은 LaunchServices가 파일을 여는 경우뿐이라서 [3][4], 다른 방법으로 파일을 읽은 일도 이 값에 반영되는지는 알 수 없습니다. 이 값으로는 누가 열었는지도 알 수 없어서, 사용자 단위 색인인지 볼륨 단위 색인인지와 로그인 기록을 함께 보고, 그 절차는 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)에 있습니다. 작성자·앱 이름 같은 값만으로 실제 작성자를 단정하지도 않습니다. 보고서에는 "이 색인 항목에 마지막 사용 시각이 이 값으로 기록돼 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 함정과 한계

`kMDItemPath` 는 쿼리·정렬에 못 쓰고, `kMDItemTextContent` 는 앱이 값을 직접 읽지 못합니다 [3][4]. 이 제약은 앱이 쿼리할 때의 이야기이고, 색인 파일을 직접 파싱하는 도구가 이 값들을 뽑는지는 도구마다 다를 수 있습니다. 그래서 도구 결과에 본문 텍스트가 없다고 색인에 없다고 단정하지 않고, 도구가 그 속성을 뽑는지 먼저 확인합니다.

도구가 뽑는 속성 가운데 앞에 밑줄이 붙은 `_kMDItem` 속성과 Apple 문서에 없는 속성은 뜻을 문서로 확인할 수 없습니다. 같은 이름의 속성이 볼륨 단위 색인과 사용자 단위 CoreSpotlight 색인에서 같은 뜻인지도 실제 데이터로 확인해야 합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 8바이트는 실제 데이터가 아니라 날짜 형식(값 형식 0x0c, 64비트 실수, Cocoa 시각)에 맞춰 만든 예시입니다 [1].

```
00 00 00 80 93 DC C4 41
```

1. 8바이트를 little-endian 64비트 실수로 읽으면 700000000.0입니다.
2. 이 값은 2001-01-01 00:00:00부터 지난 초라서, 더하면 2023-03-08 20:26:40이 됩니다.
3. 같은 순간을 유닉스 시각으로 적으면 1678307200초이고, 레코드 갱신 시각 필드처럼 마이크로초로 적으면 1678307200000000입니다. 같은 순간이어도 필드에 따라 숫자가 이렇게 달라집니다.

### 공개 도구로 한 번

mac_apt의 SPOTLIGHT 플러그인은 사용자·볼륨·iOS 색인을 읽어 항목마다 위 속성들을 뽑아 주고 [2], spotlight_parser는 같은 색인을 텍스트로 풀어 줍니다 [5]. 두 도구의 결과에서 같은 항목의 같은 속성을 골라 값이 같은지 대조하면 파서 차이로 생긴 오류를 걸러 낼 수 있습니다.

## 교차 검증

`kMDItemWhereFroms` 는 [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md)과 브라우저 다운로드 기록과 함께 보고, 전체 흐름은 [이 파일은 어디서 왔나 (File Origin)](../../../04-scenarios/activity/file-origin.md)에 있습니다. `kMDItemLastUsedDate` 는 [최근 항목 (Shared File Lists)](../recent-items/index.md), [KnowledgeC (knowledgeC.db)](../../execution/knowledgec/index.md)와 맞춰 보고, 파일을 연 사람과 시각을 따지는 절차는 [이 파일을 누가 언제 열었나 (File Access)](../../../04-scenarios/activity/file-access.md)에 있습니다. 작성자·만든 앱은 [문서 메타데이터 (iWork·Office)](../../embedded-metadata/iwork-office.md)에서, 위도·경도 같은 위치 값은 [사진 메타데이터 (EXIF·HEIC)](../../embedded-metadata/exif-heic.md)에서 파일 안의 값과 비교합니다.

## 실습

macOS 공개 시험 데이터(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다.

1. 사용자의 다운로드 폴더에 있는 파일 하나를 골라 색인에서 `kMDItemWhereFroms` 와 `kMDItemLastUsedDate` 값을 찾고, 시각을 UTC로 바꿔 적습니다.
2. 같은 파일의 `kMDItemFSCreationDate` 와 `kMDItemContentCreationDate` 가 같은지 보고, 다르면 어떤 일로 달라질 수 있는지 적어 봅니다.
3. Apple 문서에 없는 속성(`kMDItemUseCount` 등)이 나온 항목을 하나 찾고, 그 값을 보고서에 쓰려면 무엇을 더 확인해야 하는지 적어 봅니다.

## 참고 문헌

1. Apple Spotlight store database file format (libyal/dtformats, Joachim Metz, 0.0.3, 2024-01) — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Spotlight%20store%20database%20file%20format.asciidoc
2. mac_apt 플러그인 spotlight.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/spotlight.py
3. Apple, Spotlight Metadata Attributes Reference — Common Attributes (Documentation Archive, 2014-07-15) — https://developer.apple.com/library/archive/documentation/CoreServices/Reference/MetadataAttributesRef/Reference/CommonAttrs.html
4. Apple Developer, Common Metadata Attribute Keys (MDItem) — https://developer.apple.com/tutorials/data/documentation/coreservices/file_metadata/mditem/common_metadata_attribute_keys.json
5. spotlight_parser README (Yogesh Khatri) — https://github.com/ydkhatri/spotlight_parser
