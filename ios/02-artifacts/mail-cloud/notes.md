---
title: "메모"
parent: "아티팩트 · 메일·클라우드·애플 앱"
nav_order: 1000
---

# 메모 (Notes)

## 한 줄 요약

아이폰 메모 앱은 메모를 앱 그룹 `group.com.apple.notes` 의 `NoteStore.sqlite` 에 저장하고, 본문은 `ZICNOTEDATA` 표의 `ZDATA` 칸에 gzip 으로 압축한 protobuf 로 들어 있어서, 압축을 풀고 protobuf 를 읽어야 글자가 보입니다.

## 무엇을 기록하나 · 왜 생기나

메모 앱은 iOS 9 부터 지금의 `NoteStore.sqlite` 형식을 쓰고, 그 전에는 본문을 평문으로 담은 옛 형식 DB 를 썼습니다 [1]. 공개 도구 Apple Cloud Notes Parser 는 두 형식을 모두 읽으며, 지원 범위를 iOS 9 부터 iOS 26 까지로 적었습니다 [1]. 새 형식에서 본문은 `ZICNOTEDATA` 표 `ZDATA` 칸에 gzip 으로 압축한 protobuf 로 저장되고, 파서는 압축을 푼 뒤 protobuf 를 읽어 본문을 되살립니다 [1].

사용자는 메모를 암호로 잠글 수 있고, 잠근 메모와 그 첨부 파일은 AES-GCM 으로 암호화됩니다 [2]. 암호화 키(16바이트)는 사용자 암호에서 PBKDF2·SHA-256 으로 만들고, 암호화를 지원하는 첨부는 이미지, 스케치, 표, 지도, 웹 사이트입니다 [2]. iOS 16 부터는 따로 정한 암호 대신 기기 암호로 메모를 잠글 수도 있습니다 [1].

iCloud 에 동기화하는 메모는 표준 보호에서 서버 저장 시 암호화하고 키는 Apple 이 보관하며, 고급 데이터 보호를 켜면 종단 간 암호화됩니다 [3]. 메모는 이미 iCloud 로 동기화되는 데이터라서 iCloud 백업에 들어가지 않습니다 [4]. 계정 쪽 자료 확보는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에서 다룹니다.

## 위치와 버전별 차이

| 무엇 | 위치 | 확인 정도 |
|---|---|---|
| 현재 메모 DB | `AppDomainGroup-group.com.apple.notes :: NoteStore.sqlite` | 관찰(확인 범위: iOS 27.0) |
| 손글씨·그림 관련으로 보이는 DB | `AppDomainGroup-group.com.apple.notes :: Accounts/<UUID>/Paper/Bundles/<UUID>.bundle/Database/data.sqlite` | 관찰(확인 범위: iOS 27.0), 용도는 확인 못 함 |
| 옛 메모 DB | `HomeDomain :: Library/Notes/notes.sqlite` | 관찰(확인 범위: iOS 27.0), 행이 있는지는 읽지 않음 |
| 메모 앱 설정 | `HomeDomain :: Library/Preferences/com.apple.mobilenotes.plist` | 관찰(확인 범위: iOS 27.0) |
| 메모 앱 그룹 설정 | `AppDomainGroup-group.com.apple.notes :: Library/Preferences/group.com.apple.notes.plist` | 관찰(확인 범위: iOS 27.0) |

맥에서는 같은 DB 가 `~/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite` 에 있습니다 [1]. 관찰한 백업에서 메모 관련 도메인은 `AppDomain-com.apple.mobilenotes`(항목 5개), `AppDomainGroup-group.com.apple.notes`(85개), `AppDomainGroup-group.com.apple.notes.import`(3개)와 `AppDomainPlugin-com.apple.mobilenotes.` 로 시작하는 확장 도메인 7개(EditorExtension, IntentsExtension, NotesAppMigrationExtension, QuickLookExtension, SharingExtension, SpotlightIndexExtension, WidgetExtension)였습니다(확인 범위: iOS 27.0).

| iOS | 내용 | 근거 |
|---|---|---|
| 9 이전 | 옛 형식 DB, 본문 평문 | [1] |
| 9 ~ 26 | `NoteStore.sqlite`, 공개 파서 지원 범위 | [1] |
| 16 부터 | 기기 암호로 메모 잠금 가능, 공개 파서는 이 방식을 아직 풀지 못함 | [1] |
| 27.0 | `NoteStore.sqlite` 와 옛 `notes.sqlite` 가 로컬 백업에 함께 있음 | 확인 범위: iOS 27.0 |

## 구조

### NoteStore.sqlite 의 표

관찰한 `NoteStore.sqlite` 에는 아래 표가 있었습니다(확인 범위: iOS 27.0).

```
ZICCLOUDSYNCINGOBJECT, ZICNOTEDATA, ZICLOCATION, ZICINVITATION, ZICNOTEPARTICIPANT,
ZICASSETSIGNATURE, ZICCLOUDSTATE, ZICSEARCHINDEXSTATE, ZICSERVERCHANGETOKEN,
ACHANGE, ATRANSACTION, ATRANSACTIONSTRING, Z_METADATA, Z_MODELCACHE, Z_PRIMARYKEY
```

`ZICCLOUDSYNCINGOBJECT` 는 칸 이름으로 보아 메모·첨부·계정과 관련된 행이 함께 들어 있는 표이고, 관찰한 칸 가운데 분석에 쓸 만한 것은 아래와 같습니다(확인 범위: iOS 27.0).

```
ZICCLOUDSYNCINGOBJECT (일부)
ZISPASSWORDPROTECTED, ZCRYPTOITERATIONCOUNT, ZLOCKEDNOTESMODE, ZHASMISSINGKEYCHAINITEM,
ZMARKEDFORDELETION, ZISRECOVERINGFROMTRASH,
ZACCOUNT, ZNOTE, ZMEDIA, ZLOCATION, ZATTACHMENT, ZPARENTATTACHMENT,
ZTYPE, ZFILESIZE, ZHASCHECKLIST, ZNEEDSTRANSCRIPTION, ZHASMARKUPDATA
```

관찰 메모에서 이 표의 칸 여러 개가 가려져 있어서, 제목·만든 날짜·고친 날짜 칸 이름(`ZTITLE1`, `ZCREATIONDATE1` 등으로 알려짐)은 확인하지 못했습니다. 검체에서는 `PRAGMA table_info(ZICCLOUDSYNCINGOBJECT);` 로 칸 목록을 먼저 뽑고, 이름에 `TITLE`·`DATE` 가 들어간 칸을 찾습니다. `ZLOCKEDNOTESMODE` 가 잠금 방식(별도 암호와 기기 암호)을 나타내는지도 확인하지 못했습니다.

본문 표 `ZICNOTEDATA` 의 칸은 `Z_PK`, `Z_ENT`, `Z_OPT`, `ZNOTE`, `ZCRYPTOINITIALIZATIONVECTOR`, `ZCRYPTOTAG`, `ZDATA` 입니다(확인 범위: iOS 27.0). 칸 이름으로 보아 `ZNOTE` 는 `ZICCLOUDSYNCINGOBJECT` 의 메모 행을 가리키고, `ZCRYPTOINITIALIZATIONVECTOR`·`ZCRYPTOTAG` 는 잠근 메모의 AES-GCM 암호화 [2] 에 쓰는 값으로 보이지만 확인하지 못했습니다.

### 위치·공유 관련 표

위치로 보이는 값은 `ZICLOCATION` 표의 `ZLATITUDE`, `ZLONGITUDE`, `ZPLACEMARKDATA`, `ZPLACEUPDATED`, `ZATTACHMENT` 칸에 있고, `ZATTACHMENT` 로 첨부 행과 이어지는 것으로 보입니다(확인 범위: iOS 27.0). 공유와 관련된 표로는 `ZICINVITATION`(`ZCREATIONDATE`, `ZMODIFICATIONDATE`, `ZRECEIVEDDATE`, `ZTITLE`, `ZSNIPPET`, `ZSHAREURL`, `ZSERVERSHAREDATA` 등)과 `ZICNOTEPARTICIPANT`(`ZNOTE`, `ZPARTICIPANTID`, `ZUSERID`)가 있습니다(확인 범위: iOS 27.0). 공유한 메모에서는 만든 날짜·고친 날짜 같은 메타데이터가 암호화되지 않고, 공유 메모는 사용자 암호 기반 종단 간 암호화가 아니라 CloudKit 암호화 데이터 형식과 CloudKit 키 관리를 씁니다 [2].

### Paper 번들 DB

`Accounts/<UUID>/Paper/Bundles/<UUID>.bundle/Database/data.sqlite` 에는 `Assets`(`Id`, `RetainCount`, `Data`)와 `Reference`(`Id`, `Version`, `RetainCount`, `ChildRetainCounts`, `Data`) 표가 있었습니다(확인 범위: iOS 27.0). 경로 이름으로 보아 손글씨나 그림 데이터와 관련이 있어 보이지만 확인하지 못했습니다.

### 옛 메모 DB (notes.sqlite)

관찰한 백업에는 옛 형식 DB 도 남아 있었고, 표와 칸은 아래와 같습니다(확인 범위: iOS 27.0). 안에 행이 있는지는 읽지 않았습니다.

```
HomeDomain :: Library/Notes/notes.sqlite (일부)
ZNOTE: ZCREATIONDATE, ZMODIFICATIONDATE, ZTITLE, ZSUMMARY, ZAUTHOR, ZDELETEDFLAG, ZGUID, ZBODY, ZSTORE
ZNOTEBODY: ZOWNER, ZCONTENT, ZEXTERNALCONTENTREF, ZEXTERNALREPRESENTATION
ZNOTEATTACHMENT: ZNOTE, ZFILENAME, ZMIMETYPE
ZACCOUNT, ZSTORE, ZNOTECHANGE
```

IMAP 메일 계정에 메모를 저장하는 계정 유형 `com.apple.account.IMAPNotes` 가 `com.apple.accountsd.plist` 의 플러그인 목록에 있었습니다(확인 범위: iOS 27.0). 메일 계정에 저장한 메모가 이 옛 DB 로 가는지는 확인하지 못했습니다.

### 설정 plist

`com.apple.mobilenotes.plist` 에는 `LastVacuumDate`(float), `lastBackgroundedState`(`currentNoteLastViewedDate`, `currentNoteContainerViewMode` 등이 든 사전), `didShowMoveToRecentyDeletedFolderAlert`(bool), `DidMigrateLocalAccount`(bool), `DidChooseToMigrateLocalAccount`(bool), `ReindexOnLaunch`(bool), `hasShownWelcomeScreen`(bool)이 있었습니다(확인 범위: iOS 27.0). `group.com.apple.notes.plist` 에는 `CloudKitAccountStatus`(int), `IntialCloudKitSyncCompleted`(bool, 철자 그대로), `AccountDevicesCache-<UUID>`(bytes), `AccountDevicesCacheDate-<UUID>`(datetime), `CloudConfigurationPath`(str)가 있었고, `HomeDomain` 의 같은 이름 plist 에도 비슷한 키가 있었습니다(확인 범위: iOS 27.0).

`lastBackgroundedState` 안의 `currentNoteLastViewedDate` 는 이름으로 보아 앱을 뒤로 보낼 때 열려 있던 메모를 마지막으로 본 시각이지만, 값의 형식과 동작은 확인하지 못했습니다.

## 증거로서 의미

### 증명하는 것

`NoteStore.sqlite` 의 메모 행과 `ZDATA` 는 수집 시점에 그 내용의 메모가 기기에 있었다는 기록입니다. 첨부 행과 `ZICLOCATION` 은 메모에 붙은 파일과 지도 위치를, `ZICINVITATION`·`ZICNOTEPARTICIPANT` 는 공유 관계를 보여 줍니다. `ZISPASSWORDPROTECTED` 같은 칸은 메모가 잠겨 있었다는 사실을 본문을 풀지 않고도 보여 줍니다.

### 증명하지 못하는 것

메모가 기기에 있다고 이 기기에서 썼다고 말할 수 없고, iCloud 로 동기화한 메모는 같은 계정의 다른 기기에서 썼을 수도 있습니다. 공유 메모의 내용 가운데 어느 부분을 누가 썼는지는 이 페이지의 칸만으로 가릴 수 없습니다. 잠근 메모의 본문은 암호 없이는 읽을 수 없고 [1], 암호를 잊어 Apple 계정으로 재설정해도 이미 잠근 메모는 볼 수 없습니다 [2]. 옛 `notes.sqlite` 가 백업에 있다는 사실만으로 그 안에 메모가 있다고 쓰지 않습니다.

보고서에는 "메모를 작성했다" 대신 "수집 시점에 이 계정의 메모 DB 에 이런 본문의 메모가 있고, 만든 날짜 칸 값은 이렇다" 처럼 씁니다.

## 시각 해석

`NoteStore.sqlite` 의 날짜 칸은 Mac 절대 시각(2001-01-01 UTC 기준 초)으로 알려져 있지만, 이번 자료로는 확인하지 못했습니다. 검체에서는 값에 978307200 을 더해 Unix 시각으로 바꾼 결과가 그럴듯한지 보고, 메모 앱 화면에 보이는 날짜와 견주어 확인합니다. 변환 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

`com.apple.mobilenotes.plist` 의 `LastVacuumDate` 는 float 로, `group.com.apple.notes.plist` 의 `AccountDevicesCacheDate-<UUID>` 는 plist 날짜형으로 저장되어 있었습니다(확인 범위: iOS 27.0).

## 함정과 한계

`ZDATA` 를 그대로 문자열 검색하면 압축된 바이트라서 본문 낱말이 걸리지 않습니다. 키워드 검색은 압축을 풀고 protobuf 를 읽은 뒤에 하고, 검색 전략은 [콘텐츠 검색](../../03-techniques/analysis/content-search.md) 에 있습니다.

iOS 16 부터 쓸 수 있는 "기기 암호로 잠근 메모" 는 공개 파서가 아직 처리하지 못합니다 [1]. 도구가 이런 메모를 빈 칸이나 오류로 보여 줘도 메모가 없었다는 뜻은 아닙니다. 잠금 해제·보안 우회 방법은 이 핸드북에서 다루지 않습니다.

지운 메모가 옮겨 가는 "최근 삭제된 항목" 폴더의 보관 기간은 이번 자료로 확인하지 못했습니다. `ZMARKEDFORDELETION`, `ZISRECOVERINGFROMTRASH` 칸이 삭제·복원 상태와 관련 있어 보이지만 값의 뜻은 확인하지 못했고, 완전히 지운 메모의 흔적을 찾을 때는 SQLite 의 `-wal`·빈 페이지를 함께 봅니다. 방법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다. `LastVacuumDate` 라는 키가 있다는 점은 메모 앱이 DB 를 정리(VACUUM)한 적이 있을 수 있다는 단서이고, VACUUM 뒤에는 빈 페이지의 옛 내용이 사라질 수 있습니다.

메모는 iCloud 백업에 들어가지 않아서 [4], iCloud 백업만 받은 사건에서 메모가 없다고 결론 내면 안 됩니다.

## 직접 분석해 보기

### 헥스로 한 번

잠그지 않은 메모의 `ZDATA` 를 헥스로 보면 gzip 스트림으로 시작합니다 [1]. gzip 명세는 첫 두 바이트를 `1F 8B`, 셋째 바이트를 압축 방식(`08` 은 deflate)으로 정합니다. 아래는 명세로 만든 예시이고 검체에서 나온 값이 아닙니다.

```
00000000  1F 8B 08 00 00 00 00 00  00 03 ...                 gzip 머리 10바이트
```

이 머리가 보이면 압축을 풀고, 풀린 바이트를 protobuf 로 읽습니다. protobuf 는 필드 번호와 형식을 담은 태그 바이트 뒤에 값이 이어지는 구조이고, 읽는 법은 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 에 있습니다. 잠근 메모는 AES-GCM 으로 암호화되어 있어서 [2] 이 머리가 보이지 않는 것이 보통이고, 검체에서 `ZCRYPTOTAG` 칸과 함께 확인합니다.

### 공개 도구로 한 번

1. 로컬 백업이라면 `Manifest.db` 에서 메모 DB 와 곁가지 파일을 찾습니다.

   ```sql
   SELECT fileID, domain, relativePath FROM Files
   WHERE (domain = 'AppDomainGroup-group.com.apple.notes' AND relativePath LIKE 'NoteStore.sqlite%')
      OR (domain = 'HomeDomain' AND relativePath LIKE 'Library/Notes/notes.sqlite%');
   ```

2. Apple Cloud Notes Parser 에 백업 폴더를 넣으면 해시 이름 파일 구조에서 `NoteStore.sqlite` 를 찾아 읽습니다 [1].
3. 도구 결과를 검증하려고 Python 표준 라이브러리로 `ZDATA` 를 직접 풀어 봅니다.

   ```python
   import sqlite3, gzip
   con = sqlite3.connect("NoteStore.sqlite")
   for pk, note, data in con.execute(
           "SELECT Z_PK, ZNOTE, ZDATA FROM ZICNOTEDATA WHERE ZDATA IS NOT NULL"):
       if data[:2] == b"\x1f\x8b":
           print(pk, note, len(gzip.decompress(data)), "bytes after gunzip")
       else:
           print(pk, note, "not gzip (locked or other format)")
   ```

4. 풀린 바이트를 protobuf 디코더에 넣어 본문 글자가 들어 있는 필드를 찾고, 파서가 보여 준 본문과 같은지 견줍니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [애플 계정](../system-account/apple-account.md) | 메모를 동기화한 계정 |
| [KnowledgeC](../app-usage/knowledgec/index.md)·[바이옴](../app-usage/biome/index.md) | 메모 앱을 앞에 띄워 쓴 시각 |
| [사진 보관함](../media/photos/index.md) | 메모에 넣은 사진이 보관함에도 있는지 |
| [키보드 입력 기록](../input-assistant/keyboard.md) | 메모에 입력한 낱말이 학습 사전에 남았는지 |
| [아이클라우드 드라이브](icloud-drive.md) | 같은 iCloud 계정의 다른 동기화 데이터 |
| [키체인](../../01-foundations/storage/keychain.md) | 잠근 메모와 관련된 키체인 항목 |

지운 메모를 찾는 사건이라면 [지운 대화와 사진 찾기](../../04-scenarios/activity/deleted-content.md) 에서, 증거를 없애려 했는지를 묻는 사건이라면 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에서 이 흔적을 어떤 순서로 맞추는지 봅니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 메모를 쓴 iOS 검체가 있는지 먼저 확인하고, 있으면 아래 질문을 풀어 봅니다.

1. `NoteStore.sqlite` 의 `ZICCLOUDSYNCINGOBJECT` 칸 목록을 뽑아, 제목과 날짜로 보이는 칸 이름을 적습니다.
2. `ZICNOTEDATA` 에서 `ZDATA` 가 `1F 8B` 로 시작하는 행과 그렇지 않은 행의 수를 셉니다.
3. 잠근 메모(`ZISPASSWORDPROTECTED` 가 참인 행)가 몇 개인지 세고, 그 메모의 `ZICNOTEDATA` 행에서 `ZCRYPTOTAG` 가 채워져 있는지 봅니다.
4. 메모 하나의 만든 날짜 값을 Mac 절대 시각으로 바꿔 UTC 로 적습니다.
5. 옛 `notes.sqlite` 가 있으면 `ZNOTE` 에 행이 있는지, `ZDELETEDFLAG` 가 켜진 행이 있는지 봅니다.

## 참고 문헌

1. threeplanetssoftware, "Apple Cloud Notes Parser" (GitHub README) — https://github.com/threeplanetssoftware/apple_cloud_notes_parser
2. Apple Platform Security, "Secure features in the Notes app" — https://support.apple.com/guide/security/secure-features-in-the-notes-app-sec1782bcab1/web
3. Apple 지원 102651, "iCloud data security overview" — https://support.apple.com/en-us/102651
4. Apple 지원 108770, "What does iCloud back up?" — https://support.apple.com/en-us/108770
