---
title: "Core Data 저장소"
parent: "SQLite 데이터베이스"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 130
---

# Core Data 저장소 (Core Data)

Core Data 는 Apple 앱이 데이터를 객체 단위로 저장할 때 쓰는 프레임워크이고, SQLite 로 저장하면 Z 로 시작하는 표·칸 이름과 `Z_PRIMARYKEY`·`Z_METADATA`·`Z_MODELCACHE` 같은 관리 표를 만듭니다. 이 이름 규칙을 알면 처음 보는 Apple 앱 DB 에서도 어느 표가 어느 엔터티이고 행들이 어떻게 이어지는지 읽어 낼 수 있습니다.

## 이 형식을 쓰는 아티팩트

iOS 27.0 로컬 백업 하나를 보면 Apple 영역 DB 131개 가운데 52개에 Core Data 관리 표(`Z_PRIMARYKEY`·`Z_METADATA`·`Z_MODELCACHE`)가 있고, 52개 모두 칸 이름이 같습니다. 예를 들면 아래 저장소들입니다(도메인 :: 경로, `#` 은 가린 숫자).

```
AppDomainGroup-group.com.apple.notes :: NoteStore.sqlite
AppDomainGroup-group.com.apple.reminders :: Container_v#/Stores/Data-local.sqlite
HomeDomain :: Library/Accounts/Accounts#.sqlite
HomeDomain :: Library/Shortcuts/Shortcuts.sqlite
HomeDomain :: Library/Calendar/Extras.db
WirelessDomain :: Library/Databases/DataUsage.sqlite
SysSharedContainerDomain-systemgroup.com.apple.mobiletimerd :: Library/local.sqlite
여러 앱의 .tipkit/tips-store.db
```

`CameraRollDomain :: Media/PhotoData/Photos.sqlite` 도 `Z_PK`·`Z_ENT`·`Z_OPT` 칸을 쓰는 Core Data 저장소이고, `Z_PRIMARYKEY` 가 있는지는 검체에서 확인합니다. 반대로 `HomeDomain :: Library/SMS/sms.db` 에는 Core Data 표가 없고 `ROWID` 칸을 쓰는 일반 SQLite DB 입니다. 각 앱의 표 내용은 [메모](../../../02-artifacts/mail-cloud/notes.md), [미리 알림과 캘린더](../../../02-artifacts/mail-cloud/reminders-calendar.md), [사진 보관함](../../../02-artifacts/media/photos/index.md), [앱별 데이터 사용량](../../../02-artifacts/network/data-usage.md) 페이지에서 다룹니다.

## 구조

### 이름 규칙

엔터티 표 이름은 Z 뒤에 엔터티 이름을 대문자로 붙이고(Item → `ZITEM`), 속성 칸 이름도 Z 뒤에 속성 이름을 대문자로 붙입니다(timestamp → `ZTIMESTAMP`). 대문자로 바꾸다 이름이 겹치면 `ZTIMESTAMP1` 처럼 숫자가 붙습니다.

### 모든 엔터티 표에 붙는 세 칸

| 칸 | 뜻 |
|---|---|
| `Z_PK` | 1 부터 1 씩 늘어나는 기본 키 |
| `Z_ENT` | `Z_PRIMARYKEY` 에 등록된 엔터티 번호. `Z_PK` 와 함께 써야 DB 전체에서 행 하나를 가리킨다 |
| `Z_OPT` | 행의 버전 번호. 행을 고칠 때마다 1 늘어난다 |

### 관리 표

| 표 | 칸 | 뜻 |
|---|---|---|
| `Z_PRIMARYKEY` | `Z_ENT`, `Z_NAME`, `Z_SUPER`, `Z_MAX` | 엔터티 목록. `Z_NAME` 은 모델의 엔터티 이름(대소문자 구분), `Z_SUPER` 는 부모 엔터티의 `Z_ENT`(없으면 0), `Z_MAX` 는 그 엔터티에 마지막으로 쓴 `Z_PK` |
| `Z_METADATA` | `Z_VERSION`, `Z_UUID`, `Z_PLIST` | `Z_UUID` 는 이 저장소 파일의 UUID, `Z_PLIST` 는 저장소 메타데이터 plist. `Z_VERSION` 은 늘 1 이고, 용도는 추정만 있다[1] |
| `Z_MODELCACHE` | `Z_CONTENT` | 현재 데이터에 맞는 데이터 모델의 캐시 |

`Z_PLIST` 는 plist 라서 [속성 목록 파일](../plist.md)의 방법으로 풉니다.

### 상속과 관계

부모·자식 엔터티는 `Z_PRIMARYKEY` 의 `Z_SUPER` 로 이어집니다. 일대다 관계에서는 "다" 쪽 표에 "일" 쪽 행의 `Z_PK` 를 담는 칸이 생기고, 다대다 관계에서는 `Z_` 뒤에 숫자와 이름이 붙는 표가 따로 생깁니다.

### 영구 이력 추적 표

영구 이력 추적(persistent history tracking)을 켜면 변경 기록을 담는 표 세 개가 생깁니다. 이 표들은 `Z_ATRANSACTIONSTRING`·`Z_ATRANSACTION`·`Z_ACHANGE` 로 소개되어 있지만[1], iOS 27.0 기기에서는 앞에 `Z_` 가 없는 이름입니다.

| 표(iOS 27.0 이름) | 칸 | 뜻 |
|---|---|---|
| `ACHANGE` | `Z_PK`, `Z_ENT`, `Z_OPT`, `ZCHANGETYPE`, `ZENTITY`, `ZENTITYPK`, `ZTRANSACTIONID`, `ZCOLUMNS` | 변경 한 건. `ZCHANGETYPE` 은 0 추가, 1 수정, 2 삭제 |
| `ATRANSACTION` | `Z_PK`, `Z_ENT`, `Z_OPT`, `ZAUTHORTS`, `ZBUNDLEIDTS`, `ZCONTEXTNAMETS`, `ZTIMESTAMP`, `ZAUTHOR`, `ZBUNDLEID`, `ZCONTEXTNAME`, `ZQUERYGEN`, `ZPROCESSID` 로 시작하는 칸 두 개 | 트랜잭션 한 건. `ZTIMESTAMP` 는 생성 시각 |
| `ATRANSACTIONSTRING` | `Z_PK`, `Z_ENT`, `Z_OPT`, `ZNAME` | 작성자 등 문자열 |

같은 백업에서 `ACHANGE` 표가 있는 DB 는 38개이고, `NoteStore.sqlite` 와 `Photos.sqlite` 에도 있습니다.

이 밖에 `ANSCKEVENT`, `ANSCKEXPORTEDOBJECT`, `ANSCKMIRROREDRELATIONSHIP`, `ANSCKMETADATAENTRY` 처럼 `ANSCK` 로 시작하는 표가 DB 세 개에 있습니다(`HomeDomain :: Library/Accessibility/com.apple.RTTTranscripts.sqlite`, `HomeDomain :: Library/Accessibility/com.apple.personalaudio.sqlite`, `HomeDomain :: Library/ContactsMetadata/CNContactMetadata.db`). 이 표들의 용도는 검체에서 확인합니다.

## 읽는 법

원본이 아닌 복사본을 `sqlite3` 셸로 열고, 먼저 엔터티 목록을 봅니다.

```
SELECT Z_ENT, Z_NAME, Z_SUPER, Z_MAX FROM Z_PRIMARYKEY ORDER BY Z_ENT;
```

엔터티 표의 `Z_ENT` 값을 이 목록과 맞추면 한 표 안에 여러 자식 엔터티의 행이 섞여 있어도 행마다 어느 엔터티인지 가를 수 있습니다. 이력 추적 표가 있다면 삭제 기록을 트랜잭션과 이어 봅니다. 아래 질의에서는 관계 칸 규칙대로 `ZTRANSACTIONID` 를 `ATRANSACTION` 의 `Z_PK` 로 보고, 시각을 초 단위로 보고 변환합니다.

```
SELECT c.Z_PK, c.ZENTITY, c.ZENTITYPK, t.ZTIMESTAMP,
       datetime(t.ZTIMESTAMP + 978307200, 'unixepoch') AS utc
FROM ACHANGE c JOIN ATRANSACTION t ON t.Z_PK = c.ZTRANSACTIONID
WHERE c.ZCHANGETYPE = 2;
```

변환 결과가 엉뚱한 연도로 나오면 단위(초·나노초)를 다시 확인합니다.

## 시각 해석

Core Data 계열 시각은 2001-01-01 00:00:00 GMT 부터 센 초(Mac 절대 시각, CFAbsoluteTime)이고 유닉스 시각과 978307200초 차이가 나며, 일부 값은 나노초 단위입니다. 기준이 GMT 라서 변환한 값은 UTC 이고, 현지 시각으로 바꿀 때는 기기 시간대를 따로 확인합니다. Core Data 날짜 속성이 SQLite 칸에 어떤 자료형으로 들어가는지는 검체에서 확인합니다. 여러 시각 기준을 바꾸는 법은 [시각 값](../../value-decoding/time-values.md)에 정리했습니다.

## 포렌식에서 중요한 점

Core Data 저장소는 iOS 7 부터 기본이 WAL 방식이라 `-wal` 을 함께 봐야 하고, 자세한 내용은 [WAL과 저널](wal-journal.md)에 있습니다. 지운 행이 SQLite 빈 공간에 남는 방식은 일반 SQLite 와 같아서 [지운 레코드 되살리기](freelist-freeblock.md)를 따릅니다.

`ACHANGE` 에서 `ZCHANGETYPE` 이 2 인 행은 원래 행이 지워진 뒤에도 `ZENTITY`·`ZENTITYPK` 로 무엇이 지워졌는지 가리킬 수 있습니다. 다만 이력이 얼마나 오래 남는지는 검체마다 확인해야 하고, 이 행은 "이 엔터티의 이 번호 행을 지운 변경이 기록되어 있다"까지만 말해 줍니다.

`Z_PRIMARYKEY` 의 `Z_MAX` 가 표에 남은 가장 큰 `Z_PK` 보다 크면 그 사이 번호의 행이 지워졌을 수 있다는 단서가 됩니다. 이 판단은 `Z_MAX` 의 정의에서 끌어낸 추론이라서, 보고서에는 추론이라고 밝히고 이력 표나 빈 공간 복원 결과와 함께 씁니다. `Z_OPT` 는 행을 고친 횟수의 단서일 뿐 언제 고쳤는지는 알려 주지 않습니다.

## 함정

이력 추적 표는 이름 앞에 `Z_` 가 붙기도 하고 붙지 않기도 하니, 표 이름만으로 찾지 말고 `ZCHANGETYPE`·`ZENTITYPK` 같은 칸 이름으로도 찾습니다. `Z_PK` 는 엔터티마다 따로 세는 번호라서 `Z_PK` 하나만으로 행을 특정하지 말고 `Z_ENT` 와 짝지어 씁니다. `Z_PK` 가 SQLite 의 rowid 와 같은 값이라는 보장이 없으니, 빈 공간에서 되살린 레코드의 rowid 를 `Z_PK` 로 바로 읽지 않습니다. 모델의 엔터티 이름(`Z_NAME`)은 대소문자를 구분하지만 표 이름은 대문자라서, 이름을 맞출 때 대소문자 차이를 감안합니다.

## 도구

`sqlite3` 셸로 관리 표와 이력 표를 질의하고, `Z_PLIST` 값은 꺼내서 plist 도구로 봅니다. 앱별 표를 해석하는 흐름은 [앱 데이터 분석](../../../03-techniques/analysis/app-data-analysis/index.md)에서 다룹니다.

## 참고 문헌

1. fatbobman, "How Core Data Saves Data in SQLite" — https://fatbobman.com/en/posts/tables_and_fields_of_coredata/
2. Apple, Technical Q&A QA1809 "New default journaling mode for Core Data SQLite stores in iOS 7 and OS X Mavericks" — https://developer.apple.com/library/archive/qa/qa1809/_index.html
3. Epoch Converter, "Cocoa Core Data timestamp converter" — https://www.epochconverter.com/coredata
