---
title: "연락처"
parent: "아티팩트 · 통화·메시지·연락처"
nav_order: 510
---

# 연락처 (AddressBook)

## 한 줄 요약

아이폰 연락처 앱의 사람·번호·그룹을 담는 SQLite 데이터베이스로, 통화 기록과 메시지에 남은 번호가 누구인지 밝히는 데 쓰고 만든 시각·고친 시각도 함께 남습니다.

## 무엇을 기록하나 · 왜 생기나

연락처 앱에 사람을 저장하면 이름·회사·메모·생일 같은 한 사람의 정보는 `AddressBook.sqlitedb` 의 `ABPerson` 표에 한 행으로 들어가고, 전화번호·이메일·주소처럼 여러 개일 수 있는 값은 `ABMultiValue` 표에 한 줄씩 따로 들어갑니다 [1]. 사진은 옆의 `AddressBookImages.sqlitedb` 에 따로 저장됩니다.

조사에서 연락처는 그 자체보다 다른 기록을 읽는 사전 노릇을 합니다. [통화 기록](call-history.md) 과 [메시지](messages/index.md) 에는 번호나 이메일만 남아서, 그 주소를 사용자가 어떤 이름으로 저장해 두었는지는 연락처에서 찾습니다. 이름을 저장해 둔 연락처는 사용자가 상대를 알았다는 정황으로 쓰이기도 하지만, 계정 동기화로 들어온 연락처일 수도 있어서 아래 "증명하지 못하는 것" 과 함께 읽습니다.

## 위치와 버전별 차이

기기 안에서는 `/private/var/mobile/Library/AddressBook/` 아래에 있고, iLEAPP 는 `AddressBook*.sqlitedb` 이름으로 찾습니다 [1]. 로컬 백업에서는 다음 파일로 보였습니다.

| 백업 경로 | 내용 |
|---|---|
| `HomeDomain :: Library/AddressBook/AddressBook.sqlitedb` | 사람·여러 값·그룹·계정 |
| `HomeDomain :: Library/AddressBook/AddressBookImages.sqlitedb` | 연락처 사진 |
| `HomeDomain :: Library/ContactsMetadata/CNContactMetadata.db` | 연락처 사진·포스터 기록 |
| `AppDomain-com.apple.MobileAddressBook :: Library/Application Support/CNDuplication/ManagedDuplicateStore.sqlite` | 중복 연락처 관련으로 보이는 DB |
| `HomeDomain :: Library/AddressBook/Family/family.plist` | 키 `Mappings`, `Generation` |

연락처 앱의 백업 도메인 이름은 `AppDomain-com.apple.MobileAddressBook` 이었습니다. 번들 ID 와 도메인의 관계는 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에서 다룹니다.

버전별 차이를 표로 정리할 만큼 확인한 자료는 없습니다. iLEAPP 는 `ABStore` 표도 읽는데 [1], 관찰한 iOS 27.0 백업의 표 목록에는 `ABStore` 가 없었습니다. 다만 관찰 과정에서 이 DB 를 끝까지 열지 못한 오류가 기록되어 있어서, 표가 정말 없어진 것인지 목록이 덜 읽힌 것인지는 가리지 못했습니다.

## 구조

### AddressBook.sqlitedb

관찰한 표는 `ABAccount`, `ABGroup`, `ABGroupChanges`, `ABGroupMembers`, `ABMultiValue`, `ABMultiValueEntry`, `ABMultiValueEntryKey`, `ABMultiValueLabel`, `ABPerson`, `ABPersonChanges` 입니다. 분석의 뼈대는 아래 네 표입니다.

| 표 | 주요 칸 | 역할 |
|---|---|---|
| `ABPerson` | `ROWID`, `First`, `Last`, `Middle`, `Organization`, `Department`, `JobTitle`, `Nickname`, `Note`, `Birthday`, `CreationDate`, `ModificationDate`, `DisplayName`, `StoreID`, `ExternalIdentifier`, `guid` | 한 사람이 한 행 |
| `ABMultiValue` | `UID`, `record_id`, `property`, `identifier`, `label`, `value`, `guid` | 번호·이메일 등 여러 값. `record_id` 가 `ABPerson.ROWID` 를 가리킵니다 |
| `ABMultiValueLabel` | `value` | 라벨 문자열 |
| `ABMultiValueEntry` | `parent_id`, `key`, `value` | 주소처럼 여러 부분으로 나뉘는 값의 조각 |

`ABPerson` 에는 이 밖에도 발음·정렬용 칸과 `MemojiMetadata`, `Wallpaper`, `WallpaperMetadata`, `SensitiveContentConfiguration`, `ImageSyncFailedTime` 같은 사진·포스터 관련 칸까지 약 60개가 있습니다.

`ABMultiValue.property` 는 값의 종류를 숫자로 적는데, iLEAPP 는 다음처럼 읽습니다 [1].

| property | 종류 |
|---|---|
| 3 | 전화번호 |
| 4 | 이메일 |
| 5 | 주소 |
| 13 | 메신저 계정 |
| 22 | URL |
| 23 | 관계 이름 |
| 46 | 프로필 |

iLEAPP 작성자는 이 숫자를 밝힌 Apple 문서를 찾지 못했고 DB 의 라벨과 맞춰 정했다고 적었습니다 [1]. 검체마다 라벨과 함께 보고 맞는지 확인합니다.

라벨은 `_$!<Mobile>!$_` 처럼 앞뒤를 `_$!<` 와 `>!$_` 로 감싼 형태로 저장되어 iLEAPP 가 이 표시를 벗겨 "Mobile" 로 보여 줍니다 [1]. 사용자가 직접 만든 라벨도 같은 모양인지는 확인하지 못했습니다.

`ABPersonChanges` 와 `ABGroupChanges` 는 이름과 칸(`record`, `type`, `sequence_number` 등)으로 보아 변경을 추적하는 표로 보이지만, 무엇이 언제 들어가고 언제 비워지는지는 확인하지 못했습니다. `ABAccount` 와 `StoreID`, `ExternalIdentifier` 칸으로 보아 연락처가 여러 계정 저장소에서 올 수 있는 구조이지만, 실제 동작을 설명한 자료는 이번에 확인하지 못했습니다.

### AddressBookImages.sqlitedb

사진은 `ABThumbnailImage`(`record_id`, `format`, `data`)와 `ABFullSizeImage`(`record_id`, `crop_x`, `crop_y`, `crop_width`, `data`), 그리고 `ABAvatarRecipe`(`record_id`, `data`) 표에 들어가고 `record_id` 로 사람과 이어집니다. iLEAPP 결과에도 썸네일과 원본 크기 사진이 함께 나옵니다 [1].

### CNContactMetadata.db 와 그 밖의 파일

`CNContactMetadata.db` 에는 `ZCNCONTACTIMAGE`(`ZCONTACTIDENTIFIER`, `ZIMAGEDATA`, `ZDELETIONDATE`, `ZLASTUSEDDATE` 등)와 `ZCNCONTACTPOSTER`(`ZCONTACTIDENTIFIER`, `ZPOSTERDATA`, `ZCONTENTISSENSITIVE`, `ZDELETIONDATE`, `ZLASTUSEDDATE` 등) 표가 있고, CloudKit 동기화 표(`ANSCK` 로 시작하는 표)도 여럿 있습니다. 칸 이름으로 보아 연락처 사진과 연락처 포스터의 기록이지만 `ZDELETIONDATE` 가 언제 채워지는지는 확인하지 못했습니다.

`ManagedDuplicateStore.sqlite` 에는 `ZDUPLICATESET`(`ZISIGNORED`, `ZPRIMARYID`, `ZSIGNATURE` 등)과 `ZDUPLICATECOHORT` 표가 있고, 같은 이름의 파일이 `AppDomain-com.apple.mobilephone` 아래에도 있었습니다. 이름으로 보아 중복 연락처를 묶는 데 쓰는 것으로 보이지만 용도는 확인하지 못했습니다. 설정 파일 가운데 `com.apple.contacts.sharedProfile.plist` 에는 `LastBannerInteractionDate`, `LastBannerRevealDate` 키가 있었습니다.

## 증거로서 의미

**증명하는 것.** 기기의 연락처 저장소에 이 이름과 이 번호가 한 사람으로 묶여 있었다는 사실과, 그 연락처를 만든 시각·마지막으로 고친 시각이 기록되어 있다는 사실을 보여 줍니다 [1]. 통화 기록이나 메시지의 번호에 이름을 붙여 읽을 근거가 됩니다.

**증명하지 못하는 것.** 연락처에 이름이 있다고 그 번호의 실제 사용자가 그 사람이라는 뜻은 아니고, 사용자가 붙인 이름일 뿐입니다. 연락처가 이 기기에서 직접 입력되었는지, 계정 동기화로 들어왔는지도 이 표만으로는 가리지 못합니다. 지운 연락처가 어떻게 처리되는지 확인한 자료가 없어서, 연락처에 없다고 사용자가 그 사람을 몰랐다고 쓸 수도 없습니다.

보고서에는 "이 기기의 연락처에 번호 X 가 '홍길동' 이라는 이름으로 저장되어 있고, 그 연락처의 생성 시각은 T 로 기록되어 있다" 처럼 씁니다.

## 시각 해석

`CreationDate` 와 `ModificationDate` 는 Mac 절대 시각, 곧 2001-01-01 00:00:00 UTC 부터 흐른 초로 읽습니다 [1]. 값은 UTC 이고 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다. `ModificationDate` 는 마지막으로 고친 한 시각만 남아서 무엇을 고쳤는지는 알려 주지 않습니다.

`Birthday` 는 iLEAPP 가 다른 함수로 따로 바꿀 만큼 다른 값이라서 [1], 두 시각 칸과 같은 방식으로 읽으면 안 됩니다. 저장 형식은 이번에 확인하지 못했습니다. 계정 동기화로 들어온 연락처에서 생성 시각이 무엇을 뜻하는지(이 기기에 처음 들어온 때인지, 원래 만든 때인지)도 확인하지 못했으니, 생성 시각을 "사용자가 입력한 시각" 으로 단정하지 않습니다.

## 함정과 한계

- **번호 표기 차이.** 연락처의 번호와 통화 기록의 번호가 국가 번호·하이픈·공백 때문에 글자 그대로는 맞지 않을 수 있으니, 숫자만 남기고 끝자리 기준으로 맞춰 본 뒤 맞춘 방법을 보고서에 적습니다.
- **property 숫자.** 종류 번호는 도구 작성자가 라벨로 맞춘 값입니다 [1].
- **열리지 않는 DB.** 관찰에서도 이 DB 를 끝까지 읽지 못한 오류가 났습니다. 표 목록이 비거나 오류가 나면 WAL 파일을 함께 복사했는지, 사본이 온전한지부터 봅니다. SQLite 의 WAL 과 손상 처리는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.
- **사진 DB 누락.** 사진은 다른 파일에 있어서 `AddressBook.sqlitedb` 만 수집하면 빠집니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 라벨 문자열을 ASCII 로 적은 예시이고 실제 검체 값이 아닙니다. `ABMultiValueLabel.value` 에서 이런 바이트가 보이면 앞뒤 표시를 뺀 가운데가 라벨입니다.

```
5F 24 21 3C 4D 6F 62 69 6C 65 3E 21 24 5F
 _  $  !  <  M  o  b  i  l  e  >  !  $  _
```

헥스 편집기에서 이 문자열 앞뒤로 SQLite 레코드 머리를 찾아 읽으면, 같은 페이지의 다른 라벨들도 차례로 보입니다. 레코드 머리 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에 있습니다.

### 공개 도구로 한 번

사본을 `sqlite3` 로 열고 사람과 번호를 이어 봅니다.

```sql
SELECT p.ROWID, p.First, p.Last, p.Organization,
       datetime(p.CreationDate + 978307200, 'unixepoch')     AS created_utc,
       datetime(p.ModificationDate + 978307200, 'unixepoch') AS modified_utc,
       mv.property, l.value AS label, mv.value
FROM ABPerson p
LEFT JOIN ABMultiValue mv ON mv.record_id = p.ROWID
LEFT JOIN ABMultiValueLabel l ON l.ROWID = mv.label
ORDER BY p.ROWID;
```

라벨은 iLEAPP 와 같은 방식으로 `ABMultiValue.label` 을 `ABMultiValueLabel.ROWID` 에 이어 붙였고 [1], 검체에서도 라벨이 맞게 붙는지 몇 행 눈으로 확인합니다. 같은 파일을 iLEAPP 의 주소록 모듈로도 돌려 사람 수와 번호 수를 맞춰 봅니다 [1].

## 교차 검증

[통화 기록](call-history.md) 의 `ZADDRESS` 와 [메시지](messages/index.md) 의 상대 주소를 연락처 번호에 맞춰 이름을 붙이고, [페이스타임](facetime.md) 상대가 이메일 주소라면 `property` 4 인 값과 맞춰 봅니다. 연락처가 어느 계정에서 왔는지 단서가 필요하면 [애플 계정](../system-account/apple-account.md) 을 함께 봅니다. 사람 사이의 연락 흐름을 한데 모으는 방법은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 에 있습니다.

## 실습

NIST CFReDS 등에 공개된 iOS 검체로 풀어 봅니다.

1. `ABPerson` 에 행이 몇 개이고, 그중 번호(`property` 3)가 하나도 없는 사람은 몇 명입니까?
2. 라벨 표에 `_$!<` 모양이 아닌 라벨이 있습니까? 있다면 사용자가 만든 라벨로 볼 근거가 무엇인지 적어 보십시오.
3. 생성 시각과 수정 시각이 다른 연락처를 뽑고, 같은 시각대에 통화나 메시지가 있었는지 맞춰 보십시오.
4. 통화 기록의 번호 가운데 연락처에 없는 번호는 몇 개입니까? 번호 표기를 맞추기 전과 후의 결과가 어떻게 달라집니까?
5. `AddressBookImages.sqlitedb` 의 `record_id` 가운데 `ABPerson` 에 없는 값이 있습니까?

## 참고 문헌

1. iLEAPP, `scripts/artifacts/addressBook.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/addressBook.py
