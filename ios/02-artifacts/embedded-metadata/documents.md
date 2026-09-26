---
title: "문서 메타데이터"
parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 1140
---

# 문서 메타데이터 (PDF·Office·iWork)

## 한 줄 요약

Office 문서 안에는 만든 사람·마지막으로 고친 사람·만든 시각·마지막 인쇄 시각 같은 핵심 속성이 들어 있고, iWork 문서는 미리보기 그림과 Metadata 폴더를 담은 번들이며, 아이폰 백업에는 iCloud Drive 컨테이너 설정·파일 제공자 DB·문서 관련 확장 도메인이 남습니다.

## 무엇을 기록하나 · 왜 생기나

문서 파일은 본문과 함께 그 문서를 누가 언제 만들고 고쳤는지 적은 속성을 파일 안에 담습니다. 이 속성은 파일이 다른 기기로 옮겨 가도 함께 따라가서, 아이폰에서 찾은 문서가 처음 어디서 만들어졌는지 짐작하는 단서가 됩니다. 사진 파일 안의 촬영 정보(EXIF)는 [카메라 사진과 메타데이터 (DCIM·EXIF·HEIC)](../media/dcim-exif.md)에서 다루고, 이 페이지는 Office·iWork·PDF 문서를 다룹니다.

아이폰 쪽에서는 문서 파일 자체보다 문서가 오간 길목이 먼저 보입니다. 파일 앱, iCloud Drive, 파일 제공자 (File Provider) 확장, 도서 앱이 각자 설정과 DB 를 남깁니다. 문서 파일이 로컬 백업에 들어가는지와 iCloud Drive 에서 내려받은 문서가 기기 어디에 놓이는지는 실제 기기에서 확인합니다.

## 위치와 버전별 차이

### 문서 형식별로 속성이 들어 있는 곳

| 형식 | 속성이 들어 있는 곳 | 출처 |
|---|---|---|
| Office(docx·xlsx·pptx) | 개방형 패키징 규약 (Open Packaging Conventions, OPC) 패키지의 핵심 속성 (core properties) | [2] |
| iWork(Pages·Numbers·Keynote) | 번들 최상위의 `Metadata/` 폴더와 미리보기 그림 | [1] |
| PDF | 실제 데이터로 확인 | — |

Office 핵심 속성이 패키지 안의 어느 부분(part)에 저장되는지와, 응용 프로그램 이름·편집 시간 같은 확장 속성은 이 페이지에서 다루지 않습니다. iWork 구조는 iWork '13 기준이고[1], 요즘 iWork 가 번들과 파일 하나 가운데 어느 쪽으로 저장하는지는 실제 데이터로 확인합니다.

### 아이폰에서 문서 흔적이 보이는 곳

| 대상 | 위치 |
|---|---|
| iCloud Drive 컨테이너 설정 | HomeDomain :: `Library/Application Support/CloudDocs/session/containers/` 아래 `com.apple.Pages.plist`, `com.apple.Numbers.plist`, `com.apple.Keynote.plist`, `iCloud.com.apple.DocumentsApp.plist` |
| 파일 제공자 목록 DB | HomeDomain :: `Library/Application Support/FileProvider/<UUID>/wharf/wharf/directoryManifest/manifest.db` |
| 파일 제공자 백업 목록 DB | HomeDomain :: `Library/Application Support/FileProvider/backup/backup_manifest.db` |
| 도서 앱 내려받기 DB | `SysSharedContainerDomain-systemgroup.com.apple.media.shared.books` :: `Documents/BLDatabaseManager/BLDatabaseManager.sqlite` |
| 파일 앱 데이터 | `AppDomain-com.apple.DocumentsApp`(항목 4개) |

같은 FileProvider 폴더에는 제공자별 `Domains.plist` 가 있고, 제공자로는 `com.apple.CloudDocs.iCloudDriveFileProvider`, `com.apple.SMBClientProvider.FileProvider`, `com.apple.filesystems.UserFS.FileProvider`, `com.apple.mobileslideshow.PhotosFileProvider` 가 있습니다. 파일 앱의 번들 ID 는 `com.apple.DocumentsApp` 입니다. iOS 버전에 따라 위치가 다를 수 있으므로, 다른 버전에서는 같은 경로가 있는지부터 확인합니다.

## 구조

### Office 핵심 속성

OPC 패키지의 핵심 속성은 아래 16가지이고[2], 조사에서 자주 보는 속성의 뜻은 표에 함께 적습니다.

| 속성 | 뜻 |
|---|---|
| `Creator` | 패키지와 내용을 만든 사람이나 주체 |
| `LastModifiedBy` | 마지막으로 고친 사용자 |
| `Created` | 만든 날짜와 시각 |
| `Modified` | 마지막으로 바뀐 날짜와 시각 |
| `LastPrinted` | 마지막으로 인쇄한 날짜와 시각 |
| `Revision` | 개정 번호 |
| `Category`, `ContentStatus`, `ContentType`, `Description`, `Identifier`, `Keywords`, `Language`, `Subject`, `Title`, `Version` | 문서 분류·설명·제목 등 |

### iWork 번들

iWork '13 이후 문서는 폴더처럼 여러 파일을 묶은 번들 (package) 형식이고, 최상위 구성은 아래와 같습니다[1].

```
Index.zip              문서 객체(IWA 파일들)
preview-micro.jpg      미리보기 그림
preview-web.jpg        미리보기 그림
preview.jpg            미리보기 그림
Data/                  그림·동영상 같은 미디어
Metadata/
  DocumentIdentifier
  Properties.plist
  BuildVersionHistory.plist
```

`Index.zip` 안에는 문서 객체를 구성 요소 (Component) 단위로 나눈 IWA 파일이 들어 있고, 이 zip 은 압축과 Zip64 를 쓰지 않는 최소 구현이라 일반 도구로 다시 묶으면 호환이 깨집니다[1]. `.iwa` 파일은 Snappy 로 압축한 프로토콜 버퍼 직렬화 데이터입니다. 압축 스트림은 표준 Snappy 프레임 형식이 아니라 4바이트 머리(첫 바이트는 조각 종류, 다음 3바이트는 리틀 엔디언 24비트 길이)가 붙은 조각을 이어 붙인 것이라서, 표준 프레임을 기대하는 도구로는 바로 풀리지 않습니다[1]. 압축을 푼 데이터에서는 객체마다 varint 길이와 `ArchiveInfo` 메시지가 앞에 붙으며 `MessageInfo` 가 뒤따르는 내용을 설명합니다[1]. 프로토콜 버퍼를 읽는 법은 [프로토콜 버퍼 (Protocol Buffers)](../../01-foundations/data-formats/protobuf.md)에서 다룹니다.

`BuildVersionHistory.plist` 는 이름으로 보면 문서를 저장한 앱의 빌드 이력을 담는 파일이지만, 값의 형식은 실제 데이터로 확인합니다. 암호를 건 iWork 문서는 번들 안 거의 모든 파일을 AES128(PKCS7 채우기)로 암호화합니다[1].

### iCloud Drive 컨테이너 설정

CloudDocs 의 컨테이너 plist 는 최상위 키가 번들 ID(`com.apple.Pages`, `com.apple.iWork.Pages` 등)이고, 그 아래에 `BRContainerDocumentTypes`, `BRContainerExportedTypes`, `BRContainerFormatVersionNumber`, `BRContainerName`, `BRContainerVersionNumber`, `BRContainerIsDocumentScopePublic` 같은 키가 있으며, 파일에 따라 `BRContainerImportedTypes`, `BRContainerIconGeneratorVersionNumber`, `BRContainerLocalizedNames` 가 더 있습니다. 이 plist 는 앱별 iCloud Drive 컨테이너 설정이고 개별 문서 목록이 아닙니다. iCloud Drive 의 문서 목록 DB 는 [아이클라우드 드라이브 (iCloud Drive)](../mail-cloud/icloud-drive.md)에서 다룹니다.

### 파일 제공자 DB

두 DB 의 표와 열은 아래와 같고, 열의 뜻을 설명한 공개 문서는 없습니다.

```
manifest.db
  manifest: destination_parent_id, destination_id, source_id, source_parent_id, data
  state: rowid, db_uuid

backup_manifest.db
  backup_manifest: relative_path, file_id, doc_id, gen_count,
                   new_file_id, new_doc_id, new_gen_count
```

### 도서 앱 내려받기 DB

`BLDatabaseManager.sqlite` 의 `ZBLDOWNLOADINFO` 표에는 `ZASSETPATH`, `ZFILEEXTENSION`, `ZTITLE`, `ZARTISTNAME`, `ZPURCHASEDATE`, `ZSTARTTIME`, `ZLASTSTATECHANGETIME` 같은 열이 있습니다. 표와 열 이름으로 보면 스토어에서 내려받은 기록이고, 사용자가 도서 앱에 직접 넣은 PDF 가 여기에 남는지는 실제 데이터로 확인합니다.

### 확장 도메인

`com.apple.PDFKit.PDFImporter` 같은 PDFKit 확장과 `com.apple.quicklook.thumbnail.iWorkExtension` 이 `AppDomainPlugin-` 도메인으로 있습니다. 이 도메인은 백업에 그 확장의 도메인이 있다는 사실만 보여 주고, 사용자가 PDF 나 iWork 문서를 열었다는 뜻은 아닙니다.

## 증거로서 의미

**증명하는 것**

Office 문서의 `Creator`·`LastModifiedBy`·`Created`·`Modified`·`LastPrinted` 는 문서 안에 적힌 작성자 이름과 시각을 보여 주고, 아이폰에서 찾은 문서가 어떤 이름으로 만들어지고 고쳐졌는지 알 수 있게 합니다. iWork 번들의 미리보기 그림으로는 본문을 풀지 않고도 문서 모습을 볼 수 있습니다. 아이폰 쪽 흔적은 iCloud Drive 컨테이너와 파일 제공자가 기기에 설정되어 있었다는 점을 보여 줍니다.

**증명하지 못하는 것**

문서 속성의 작성자 이름은 파일 안에 적힌 글자라서, 그 이름의 실제 사람이 썼다는 증거가 되지 않습니다. `Created`·`Modified` 는 파일 안에 든 값이라 아이폰 파일 시스템의 시각이나 아이폰에서 문서를 연 시각과 다를 수 있습니다. 컨테이너 설정과 확장 도메인만으로는 어떤 문서를 열었는지, 문서를 밖으로 보냈는지 말할 수 없습니다.

보고서에는 "이 파일의 핵심 속성에 만든 사람 이름이 이렇게, 만든 시각이 이렇게 적혀 있다" 처럼 파일로 확인되는 만큼만 씁니다.

## 시각 해석

Office 핵심 속성의 `Created`·`Modified`·`LastPrinted` 는 만든·마지막으로 바뀐·마지막으로 인쇄한 날짜와 시각이지만[2], 이 값이 UTC 로 적히는지는 실제 데이터로 확인합니다. 도서 앱 DB 의 `ZPURCHASEDATE`·`ZSTARTTIME`·`ZLASTSTATECHANGETIME` 은 Core Data 표의 날짜 열이라 Mac 절대 시각일 가능성이 높지만, 값의 크기로 기준을 먼저 판별합니다. 시각 기준을 판별하는 법은 [시각 값 (Mac 절대 시각·Unix·기타)](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

## 함정과 한계

iWork 문서를 조사하면서 `Index.zip` 을 풀었다가 다시 묶으면, 원본과 해시가 달라질 뿐 아니라 최소 구현 zip 과의 호환도 깨집니다[1]. 먼저 원본 해시를 기록하고, 사본에서만 풀어 봅니다.

암호를 건 iWork 문서는 번들 안 파일 대부분이 암호화되어 있어서[1] 미리보기 그림이나 속성이 보이지 않을 수 있습니다. 이 페이지는 암호를 푸는 방법을 다루지 않습니다.

문서 속성은 파일 안의 값이라 파일을 고치면 함께 바뀔 수 있고, 운영체제가 따로 지키는 값이 아닙니다. 속성의 시각이 다른 기록과 어긋나면 조작을 의심하기 전에 시간대와 저장 프로그램부터 확인합니다.

PDF 의 내부 구조, Office 확장 속성, 요즘 iWork 의 단일 파일 저장, 문서 파일의 백업 포함 여부는 이 페이지에서 다루지 않으므로, 이 부분을 근거로 보고할 때는 따로 출처를 확인합니다.

## 직접 분석해 보기

**헥스로 한 번.** iWork 번들의 `Index.zip` 사본에서 `.iwa` 파일 하나를 꺼내 헥스로 열면 맨 앞 4바이트가 조각 머리이고, 이 머리를 떼어 내고 조각마다 Snappy 압축을 푼 결과를 다시 헥스로 엽니다. 객체마다 맨 앞에 varint 로 적은 길이와 `ArchiveInfo` 메시지가 붙어 있습니다[1]. varint 를 읽는 법은 프로토콜 버퍼 페이지에 있습니다. varint 가 끝난 바이트 뒤부터 프로토콜 버퍼 메시지로 읽어 보면 객체 경계를 제대로 잡았는지 확인할 수 있습니다.

**공개 도구로 한 번.** `sqlite3` 로 사본 DB 를 열어 파일 제공자와 도서 앱의 기록을 뽑습니다.

```sql
-- backup_manifest.db
SELECT relative_path, file_id, doc_id, gen_count,
       new_file_id, new_doc_id, new_gen_count
FROM backup_manifest;

-- BLDatabaseManager.sqlite: PDF 확장자 행만
SELECT ZTITLE, ZARTISTNAME, ZFILEEXTENSION, ZASSETPATH,
       ZPURCHASEDATE, ZSTARTTIME, ZLASTSTATECHANGETIME
FROM ZBLDOWNLOADINFO
WHERE lower(ZFILEEXTENSION) = 'pdf';
```

`ZFILEEXTENSION` 에 확장자가 점 없이 적히는지는 기기마다 확인해야 하므로, 결과가 비면 조건을 `LIKE '%pdf%'` 로 넓혀 봅니다. Office 파일은 OPC 패키지를 여는 공개 도구나 라이브러리로 사본의 핵심 속성을 읽고, 값을 위 표와 맞춰 봅니다.

## 교차 검증

| 확인할 것 | 볼 페이지 |
|---|---|
| iCloud Drive 문서 목록과 동기화 기록 | [아이클라우드 드라이브 (iCloud Drive)](../mail-cloud/icloud-drive.md) |
| 문서가 기기로 들어온 길(메일·메신저·에어드롭) | [메일 앱 (Apple Mail)](../mail-cloud/apple-mail.md), [에어드롭 (AirDrop)](../network/airdrop.md) |
| 문서 안 글자 검색 | [콘텐츠 검색 (Content Search)](../../03-techniques/analysis/content-search.md) |
| 문서를 밖으로 보냈는지 | [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) |
| 문서 시각을 다른 기록과 한 줄에 놓기 | [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md) |

## 실습

공개 시험 데이터(NIST CFReDS 등에서 받을 수 있는 아이폰 이미지나 로컬 백업)와 직접 만든 시험 문서로 아래 질문을 풀어 봅니다.

1. 시험용 docx 를 만들고 핵심 속성의 `Creator`·`Created`·`Modified` 를 읽는다. 다른 프로그램에서 한 번 저장한 뒤 어떤 값이 바뀌었는가?
2. Pages 로 만든 문서의 번들에서 `Metadata/` 폴더의 세 파일을 찾고, `Properties.plist` 에 어떤 키가 있는지 적는다.
3. 백업의 CloudDocs 컨테이너 plist 에서 Pages·Numbers·Keynote 별 최상위 번들 ID 를 나열하고, 문서 목록이 아니라는 점을 보고서 문장으로 어떻게 적을지 써 본다.
4. `ZBLDOWNLOADINFO` 의 날짜 열 값이 Mac 절대 시각과 Unix 시각 가운데 어느 쪽에 맞는지 값의 크기로 판별해 본다.

## 참고 문헌

1. obriensp, "iWork '13 File Format", iWorkFileFormat (Docs/index.md) — https://github.com/obriensp/iWorkFileFormat/blob/master/Docs/index.md
2. Microsoft, "PackageProperties Class (System.IO.Packaging)", Microsoft Learn — https://learn.microsoft.com/en-us/dotnet/api/system.io.packaging.packageproperties
