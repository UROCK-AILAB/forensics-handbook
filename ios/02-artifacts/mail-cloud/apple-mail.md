---
title: "메일 앱"
parent: "아티팩트 · 메일·클라우드·애플 앱"
nav_order: 970
---

# 메일 앱 (Apple Mail)

## 한 줄 요약

아이폰 기본 메일 앱은 메일 본문을 `.emlx` 파일로, 메일 목록과 겉봉 정보를 `Envelope Index`·`Protected Index` 두 SQLite DB 로 남기지만, 관찰한 로컬 백업에는 이 파일들이 보이지 않고 설정 plist 와 계정 DB 만 보여서 수집 방식부터 확인해야 합니다.

## 무엇을 기록하나 · 왜 생기나

메일 앱은 계정마다 메일함(받은 편지함·보낸 편지함·임시 보관함·지운 편지함 등)을 기기에 내려받아 두고, 본문은 파일로, 목록은 DB 로 따로 관리합니다 [1]. 본문 파일은 `.emlx` 와 `.partial.emlx` 두 가지이고, 목록 쪽은 `Envelope Index` 와 `Protected Index` 두 DB 가 나눠 맡습니다 [1]. `Envelope Index` 에는 계정별 메일함에 관한 표가 많고 보낸 날짜, 스레드 ID·메시지 ID, 메일함 위치 같은 겉봉 정보가 들어 있으며, `Protected Index` 는 표 수가 적지만 제목·주소·본문 앞부분처럼 증거 가치가 큰 내용을 담습니다 [1].

메일 앱을 쓰면 이 밖에도 설정 plist 여러 개에 앱을 마지막으로 띄운 시각, 검색 색인을 다시 만든 시각, 메일함 URL 같은 값이 쌓입니다(확인 범위: iOS 27.0). 어떤 메일 계정이 기기에 등록되어 있었는지는 메일 앱 폴더가 아니라 시스템 계정 DB 에서 확인합니다.

iCloud 메일은 표준 보호에서도, 고급 데이터 보호(Advanced Data Protection)를 켠 상태에서도 종단 간 암호화 대상이 아니고, Apple 은 그 이유를 전 세계 이메일 체계와 호환해야 하기 때문이라고 설명합니다 [2]. 기기에서 찾지 못한 iCloud 메일은 계정 쪽 자료 요청으로 확보할 수 있는 범위에 들어가고, 그 절차는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에 있습니다.

## 위치와 버전별 차이

| 무엇 | 위치 | 확인 정도 |
|---|---|---|
| 메일 본문·메일함 폴더 | 기기 `/private/var/mobile/Library/Mail/` 아래 계정별 폴더 | [1] (iOS 12·13) |
| `Envelope Index`, `Protected Index` (각각 `-shm`·`-wal` 동반) | 같은 `Library/Mail` 폴더 | [1] (iOS 12·13) |
| 메일함 모음 설정 | `HomeDomain :: Library/Mail/MailboxCollections.plist` | 관찰(확인 범위: iOS 27.0) |
| 계정별 메일함 캐시 | `HomeDomain :: Library/DataAccess/<계정>/.mboxCache.plist` | 관찰(확인 범위: iOS 27.0), 계정 이름은 가림 |
| 메일 앱 그룹 설정 | `AppDomainGroup-group.com.apple.mail :: Library/Preferences/group.com.apple.mail.plist` | 관찰(확인 범위: iOS 27.0) |
| 메일 앱 설정 | `AppDomain-com.apple.mobilemail :: Library/Preferences/com.apple.mobilemail.plist` | 관찰(확인 범위: iOS 27.0) |
| 메일 데몬 설정 | `HomeDomain :: Library/Preferences/com.apple.email.maild.plist` | 관찰(확인 범위: iOS 27.0) |
| iCloud 메일 동기화 설정 | `HomeDomain :: Library/Preferences/com.apple.icloudmailagent.plist` | 관찰(확인 범위: iOS 27.0) |
| 기기에 등록된 계정 | `HomeDomain :: Library/Accounts/Accounts#.sqlite` (`#` 은 가린 숫자) | 관찰(확인 범위: iOS 27.0) |

메일 앱의 번들 ID 는 `com.apple.mobilemail` 이고, 관찰한 백업에서는 앱 도메인 `AppDomain-com.apple.mobilemail` 에 항목이 22개 있었습니다(확인 범위: iOS 27.0). 같은 백업에는 `AppDomainGroup-group.com.apple.mail`(6개), `AppDomainGroup-com.apple.MailPersonaStorage`(3개), `AppDomain-com.apple.MailCompositionService`(4개) 도메인과 `AppDomainPlugin-com.apple.mobilemail.` 으로 시작하는 확장 도메인 7개(DiagnosticExtension, MailIntentsExtension, MailNotificationContentExtension, MailQuickLookExtension, MailSettingsIntentsExtension, MailShortcutsExtension, MailWidgetExtension)도 있었습니다(확인 범위: iOS 27.0). 도메인 이름을 읽는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에 있습니다.

버전에 따라 확인한 내용은 아래와 같습니다.

| iOS | `Protected Index` 구조 | 근거 |
|---|---|---|
| 12 | `messages`(보낸 사람·제목·받는 사람/참조/숨은 참조), `message_data`(본문 앞 500바이트) | [1] |
| 13 | `Addresses`, `Subjects`, `Summaries`, `protected_message_data` | [1] |
| 15 이후 | 확인하지 못함 | — |
| 27.0 로컬 백업 | `Envelope Index`·`Protected Index`·`.emlx` 가 관찰 메모에 나오지 않음 | 확인 범위: iOS 27.0 |

iOS 12 와 13 사이에 `Protected Index` 구조가 바뀌었다는 점은 [1] 이 확인했지만, iOS 15 이후 `Envelope Index` 의 표·칸 이름이 그대로인지는 이번 자료로 확인하지 못했습니다. 버전이 다른 검체에서는 표 목록부터 새로 뽑아 봅니다.

## 구조

### 메일 폴더와 본문 파일

`Library/Mail` 아래에는 계정마다 폴더가 있고, 그 안에 메일함 폴더가 있으며, 메일 한 통은 `.emlx` 또는 `.partial.emlx` 파일 하나로 남습니다 [1]. 본문은 Quoted-Printable 이나 Base64 로 인코딩되어 있어서 그대로 읽으면 깨져 보이고, 디코딩한 뒤에 읽습니다 [1]. Quoted-Printable 은 `=` 를 이스케이프 문자로 쓰고, `=0D` 는 줄바꿈, `=3D` 는 `=` 글자 자체를 뜻합니다 [1].

### Envelope Index

`Envelope Index` 는 메일 목록을 그리는 데 쓰는 겉봉 정보를 담고, `Mailboxes` 표의 URL 칸이 각 메일함 폴더를 가리킵니다 [1]. 이 URL 안에 폴더 식별자가 들어 있으면 이름만 보고는 어떤 메일함인지 알기 어려운데, 계정별 `.mboxCache.plist` 의 `mboxes` 아래 메일함마다 `MailboxName` 과 `DAFolderID` 가 함께 있어서 그 식별자를 메일함 이름에 이어 줍니다 [1]. 관찰한 백업의 `.mboxCache.plist` 에는 `mboxes`(list), `separator`(str), `capabilities`(list) 키가 있었습니다(확인 범위: iOS 27.0).

### Protected Index

iOS 13 기준으로 `Addresses` 표에는 메일 주소와 이름 역할을 하는 `Comments` 칸이, `Subjects` 표에는 제목이, `Summaries` 표에는 본문 앞 500바이트가 들어 있습니다 [1]. `protected_message_data` 표는 [1] 의 시험 기기에서 비어 있었습니다. 본문 전체가 필요하면 `.emlx` 파일로 가고, `.emlx` 가 없거나 일부만 내려받은 경우에는 `Summaries` 의 앞부분이 남은 내용의 전부일 수 있습니다.

### 로컬 백업에서 보이는 것

관찰한 백업에서는 `HomeDomain` 의 `Library/Mail` 아래로 `MailboxCollections.plist` 하나만 나왔고, 그 키는 아래와 같습니다(확인 범위: iOS 27.0).

```
HomeDomain :: Library/Mail/MailboxCollections.plist
buildVersion (str)
lastSelectedItem: {expanded, selected, shouldSync, type, uniqueID}
collections (list)
version (int)
```

메일 앱 그룹 설정에는 앱 사용 시각과 색인 상태를 가늠할 키가 모여 있습니다(확인 범위: iOS 27.0).

```
AppDomainGroup-group.com.apple.mail :: Library/Preferences/group.com.apple.mail.plist (일부)
LastMailAppLaunchTime (datetime)
lastForegroundedTimestamp (int)
LastFullReindexDate (datetime)
IndexStatusCollectAfterDate (datetime)
com.apple.mail.searchableIndex.lastUpgradeDate (datetime)
com.apple.mail.searchableIndex.lastKnownOSVersion (str)
LastKnownReindexReasons (list)
DeviceIdentifier (str)
MobileMailVersion (int)
AllInboxesEnabled (bool)
EMUserDefaultMailDatabaseSize: {main}
FilesMarkedPurgeable (int)
UserNotificationMailboxCutoffs: {imap://<UUID>/INBOX, ...}
BucketBarConfiguration / BucketSelectionConfiguration: {All Inboxes}
```

`UserNotificationMailboxCutoffs` 안의 항목 이름은 `imap://` 로 시작하는 메일함 URL 꼴이라서 기기에 어떤 IMAP 메일함이 있었는지 가늠하는 단서가 되지만, [1] 이 말한 `Mailboxes` 표 URL 과 같은 꼴인지는 확인하지 못했습니다. 같은 plist 에는 `BlackPearl` 로 시작하는 키 여러 개(`BlackPearlModelVersion`, `BlackPearlRolloutID` 등)와 `DisableCategorizationOnboarding` 으로 시작하는 키도 있었고, 메일 분류 기능과 관련이 있어 보이지만 뜻은 확인하지 못했습니다(확인 범위: iOS 27.0).

그 밖에 `com.apple.mobilemail.plist` 에는 `MailAccountsOrder`(list)·`MessageAccountsVersion`(int)이, `com.apple.email.maild.plist` 에는 `com.apple.mobilemail.purge.bodies.purge_markers`·`kDefaultsKeyLastVerifiedMessageID`(int)·`kCloudStoreHistoryTokenUserDefaultsKey`(bytes)·`set-initial-vip-flags`(bool)가, `com.apple.icloudmailagent.plist` 에는 `com.apple.icloud.mail.lastRetryTimestamp`·`com.apple.icloud.mail.lastSyncAllTimestamp`(둘 다 float)가 있었습니다(확인 범위: iOS 27.0). 애플 워치로 메일을 보는 설정은 `HomeDomain :: Library/Preferences/com.apple.NanoMail.plist` 에 `kIncludeMailBoxesKey`, `kAccountIdentitiesKey`, `NanoMailDefaultAccountUidKey`, `NanoMailLoadRemoteImages` 같은 키로 남습니다(확인 범위: iOS 27.0). 워치 연결 흔적 전체는 [애플 워치 연결](../health-wallet/apple-watch.md) 에서 다룹니다.

메일 앱 도메인 안에는 `Library/WebKit/WebsiteData/ResourceLoadStatistics/observations.db` 도 있고, 그 `ObservedDomains` 표에 `registrableDomain`, `lastSeen`, `mostRecentUserInteractionTime` 같은 칸이 있습니다(확인 범위: iOS 27.0). 메일 안의 웹 콘텐츠(원격 이미지 등)를 불러온 기록인지는 확인하지 못해서, 보고서에 쓰기 전에 검체에서 값을 보고 판단합니다.

### 계정 DB

어떤 메일 계정이 등록되어 있었는지는 `Accounts#.sqlite` 의 `ZACCOUNT` 표(`ZACCOUNTDESCRIPTION`, `ZUSERNAME`, `ZIDENTIFIER`, `ZOWNINGBUNDLEID`, `ZDATE`, `ZACTIVE`, `ZAUTHENTICATED` 등)와 `ZACCOUNTTYPE`·`ZACCOUNTPROPERTY`·`ZDATACLASS` 표를 맞춰 읽습니다(확인 범위: iOS 27.0). `com.apple.accountsd.plist` 의 `AuthenticationPluginCache` 에는 `com.apple.account.IMAP`, `POP`, `SMTP`, `Exchange`, `Google`, `Hotmail`, `Yahoo`, `aol` 같은 이름이 나오지만, 인증 플러그인 목록이라서 그 종류 계정을 실제로 추가했다는 뜻인지는 확인하지 못했습니다(확인 범위: iOS 27.0). 계정 DB 전반은 [애플 계정](../system-account/apple-account.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

`.emlx` 파일이나 `Protected Index` 의 행은 그 메일이 수집 시점에 이 기기의 메일 앱에 내려받혀 있었다는 기록이고, iOS 13 에서는 제목·주소·본문 앞부분이 각각 `Subjects`·`Addresses`·`Summaries` 표에 나뉘어 남습니다 [1]. `Envelope Index` 의 메일함 위치는 수집 시점에 그 메일이 어느 메일함(보낸 편지함, 지운 편지함 등)에 있었는지를 보여 줍니다 [1]. 계정 DB 의 `ZACCOUNT` 행은 그 계정이 기기에 등록되어 있었다는 기록입니다.

### 증명하지 못하는 것

보낸 편지함에 메일이 있다는 기록만으로는 그 기기에서 사용자가 직접 썼다고 말할 수 없고, 같은 계정을 다른 기기에서도 썼다면 그쪽에서 보낸 메일일 수 있습니다. 받은 편지함의 메일도 사용자가 열어 읽었다는 뜻은 아닙니다. 기기에서 메일을 찾지 못했다고 서버에도 없었다고 쓰지 않습니다. 설정 plist 의 시각 키는 앱을 띄우거나 색인을 다시 만든 시점을 짐작하게 하지만, 특정 메일을 다룬 시각은 아닙니다.

보고서에는 "이 메일을 보냈다" 대신 "수집 시점에 이 계정의 보낸 편지함에 이 제목의 메일이 있고, 보낸 날짜 칸 값은 이렇다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

[1] 은 `Envelope Index` 에 보낸 날짜가 들어 있다고 적었지만, iOS 15 이후 표의 날짜 칸 이름과 기준(Unix 초인지 Mac 절대 시각인지)은 이번 자료로 확인하지 못했습니다. 검체에서는 칸 값의 자릿수를 보고 여러 기준으로 바꿔 본 뒤, 메일 앱 화면에 보이는 날짜나 알림 기록 같은 다른 시각과 견주어 기준을 정합니다. 변환 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

설정 plist 가운데 `LastMailAppLaunchTime`, `LastFullReindexDate`, `com.apple.mail.searchableIndex.lastUpgradeDate` 는 plist 날짜형(datetime)으로 저장되어 있었습니다(확인 범위: iOS 27.0). `lastForegroundedTimestamp`(int)와 `com.apple.icloud.mail.lastSyncAllTimestamp`(float)의 단위와 기준 시점은 확인하지 못했고, 계정 DB 의 `ZDATE` 기준도 확인하지 못했습니다.

## 함정과 한계

관찰한 로컬 백업에는 `Envelope Index`·`Protected Index`·`.emlx` 가 나오지 않았습니다(확인 범위: iOS 27.0). 다만 관찰 메모가 어떤 기준으로 DB 파일을 골랐는지 적혀 있지 않아서 "메모에 없다" 가 곧 "백업에 없다" 는 아닐 수 있고, 로컬 백업이 메일 DB 를 빼는지도 이번 자료로 확인하지 못했습니다. 메일 본문이 필요한 사건에서는 백업만 보고 "메일 없음" 이라고 결론 내지 말고, 파일 시스템 전체 수집이 가능한지 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 먼저 검토합니다.

`Protected Index` 의 본문은 앞 500바이트뿐이라서 [1], 이 표만 읽고 메일 내용 전체를 다 봤다고 쓰면 안 됩니다. 인코딩된 본문을 디코딩하지 않고 키워드 검색을 하면 Quoted-Printable 로 쪼개진 낱말이나 Base64 로 바뀐 글자를 놓치고, 검색 전략은 [콘텐츠 검색](../../03-techniques/analysis/content-search.md) 에 있습니다.

`Envelope Index`·`Protected Index` 는 `-wal` 파일과 함께 있어서 [1], 본 DB 만 복사하면 아직 합쳐지지 않은 변경이 빠집니다. 지운 메일의 흔적을 찾을 때도 `-wal` 과 빈 페이지를 함께 보고, 방법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 와 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

`.emlx` 본문이 Quoted-Printable 이면 `=` 뒤 두 글자가 바이트 하나를 16진수로 적은 것입니다 [1]. 아래는 규칙으로 만든 예시이고 검체에서 나온 값이 아닙니다.

```
원문 바이트:  61 3D 33 44 62 3D 30 44        a=3Db=0D
디코딩 결과:  61 3D 62 0D                    a=b(줄바꿈)
```

`3D 33 44` 세 바이트(`=3D`)가 `3D` 한 바이트(`=`)로, `3D 30 44`(`=0D`)가 `0D` 한 바이트로 줄어듭니다. 한글 본문은 UTF-8 바이트가 `=EA=B0=80` 처럼 이어져서, 헥스로 볼 때 `=` 가 세 글자마다 반복되면 Quoted-Printable 로 판단하고 디코딩합니다.

### 공개 도구로 한 번

1. 로컬 백업이라면 `Manifest.db` 를 사본으로 떠서 sqlite3 로 열고 메일 관련 파일을 찾습니다.

   ```sql
   SELECT fileID, domain, relativePath FROM Files
   WHERE relativePath LIKE 'Library/Mail/%'
      OR relativePath LIKE 'Library/DataAccess/%/.mboxCache.plist'
      OR domain IN ('AppDomainGroup-group.com.apple.mail', 'AppDomain-com.apple.mobilemail');
   ```

2. 파일 시스템 전체를 확보했다면 `Library/Mail` 폴더를 통째로 복사하고, `Protected Index` 를 sqlite3 로 열어 `.tables` 로 표 목록을 먼저 확인합니다. iOS 13 과 같은 구조라면 `Subjects`, `Summaries`, `Addresses` 를 읽습니다.
3. `.emlx` 본문은 Python 표준 라이브러리 `quopri`(Quoted-Printable)나 `base64` 로 디코딩합니다.

   ```python
   import quopri
   print(quopri.decodestring(b"a=3Db=0D"))   # b'a=b\r'
   ```

4. 설정 plist 는 `plistlib` 으로 열어 위 표의 키 값을 봅니다. plist 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [애플 계정](../system-account/apple-account.md) | 기기에 등록된 메일 계정과 등록 시점 |
| [알림 기록](../app-usage/notifications.md) | 새 메일 알림이 온 시각과 미리보기 |
| [KnowledgeC](../app-usage/knowledgec/index.md)·[바이옴](../app-usage/biome/index.md) | 메일 앱을 앞에 띄워 쓴 시각 |
| [연락처](../communications/contacts.md) | 주고받은 주소가 연락처에 있는지 |
| [미리 알림과 캘린더](reminders-calendar.md) | 메일에서 온 일정 초대 |
| [지메일](gmail.md) | 같은 지메일 계정을 전용 앱으로 썼는지 |
| [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) | 서버에 남은 메일을 확보하는 절차 |

누구와 연락했는지를 묻는 사건이라면 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 에서, 자료를 메일로 내보냈는지를 묻는 사건이라면 [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에서 이 흔적을 어떤 순서로 맞추는지 봅니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 메일 계정이 설정된 iOS 검체가 있는지 먼저 확인하고, 있으면 아래 질문을 풀어 봅니다.

1. 검체가 로컬 백업인지 파일 시스템 전체인지 확인하고, `Library/Mail` 아래 파일이 몇 개 들어 있는지 셉니다.
2. `Protected Index` 의 표 목록을 뽑아 iOS 12 구조와 iOS 13 구조 가운데 어느 쪽에 가까운지, 둘 다 아닌지 적습니다.
3. `Envelope Index` 의 `Mailboxes` 표 URL 하나를 골라 `.mboxCache.plist` 로 메일함 이름을 풀어 봅니다.
4. `.emlx` 파일 하나를 디코딩해 `Summaries` 의 앞부분과 같은지 견줍니다.
5. `group.com.apple.mail.plist` 의 `LastMailAppLaunchTime` 을 KnowledgeC 의 메일 앱 사용 기록과 견주어 어느 쪽이 더 늦은지 봅니다.

## 참고 문헌

1. DoubleBlak (Ian Whiffin), "iOS Mail" — https://www.doubleblak.com/blogPost.php?k=iosmail
2. Apple 지원 102651, "iCloud data security overview" — https://support.apple.com/en-us/102651
