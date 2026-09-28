---
title: "애플 계정"
parent: "아티팩트 · 시스템·계정"
nav_order: 280
---

# 애플 계정 (Apple Account)

기기에 추가한 계정은 `Accounts3.sqlite` 한 곳에 사용자 이름·계정 종류·소유 번들 ID·추가 시각과 함께 모이고, 애플 계정의 로그인 상태와 나의 찾기·스토어·메시지 등록 같은 부속 기록은 `Library/Preferences/` 아래 여러 설정 파일에 따로 남습니다.

## 무엇을 기록하나 · 왜 생기나

`Accounts3.sqlite` 는 기기의 계정 정보를 담는 데이터베이스입니다[7][8]. 여기서는 계정을 추가한 시각, 사용자 이름, 계정 종류, 계정 ID, 계정 설명, 계정을 소유한 번들 ID, 부모 계정, 계정 자격 증명 종류를 읽을 수 있습니다[7]. 계정 종류가 따로 적히는 것처럼 한 DB 에 여러 종류의 계정이 함께 들어가서, 사용자가 기기에 어떤 계정을 붙여 두었는지 한 번에 살펴볼 수 있습니다.

애플 계정의 상태는 이 DB 말고도 기능별 설정 파일에 따로 남습니다. 로컬 백업에는 애플 계정 정보 캐시, 인증(AuthKit), 나의 찾기, App Store·미디어 서비스, 메시지·페이스타임 등록 쪽 설정 파일이 각각 있습니다.

## 위치와 버전별 차이

### 계정 데이터베이스

| 수집 방식 | 경로 | 근거 |
|---|---|---|
| 전체 파일 시스템 추출 | `/private/var/mobile/Library/Accounts/Accounts3.sqlite` | [7][8] |
| 로컬 백업 | `HomeDomain :: Library/Accounts/Accounts#.sqlite` (`#` 은 숫자) | |
| 로컬 백업의 사본 | `HomeDomain :: Library/Accounts/VerifiedBackup/Accounts#.sqlite` | |

백업 쪽 `HomeDomain :: Library/Accounts/` 는 이름으로 보면 전체 파일 시스템 경로 `/private/var/mobile/Library/Accounts/` 와 맞습니다. `VerifiedBackup` 폴더의 사본은 표와 열 구성이 원본과 같습니다. 두 파일의 내용이 다르면 서로 다른 시점의 상태일 수 있으니 따로 읽어 비교합니다.

### 애플 계정 쪽 설정 파일

로컬 백업에서 애플 계정과 관계있어 보이는 설정 파일은 아래와 같습니다. 따로 적지 않은 파일은 모두 `HomeDomain :: Library/Preferences/` 아래에 있습니다.

| 파일 | 키 |
|---|---|
| `com.apple.appleaccount.informationcache.plist` | `AAAccountFullName` (str), `AAIsAccountSignedIn` (bool), `AAPrimaryAccountSignInState` (int), `AAProfilePictureCacheURL` (str) |
| `com.apple.appleaccount.plist` | `com.apple.corecdp.bootSessionID` (str), `AACustodianInfo` 안의 `preflightResults` |
| `com.apple.appleaccountd.plist` | `lastCloudSyncTimestampKey` (datetime), `CKStartupTime` (int), `CKPerBootTasks` (list), `CC_OncePerBootBackingData` (bytes) |
| `com.apple.AuthKit.plist` | `_AKBAACertMarkerKey` (bytes), `timeCfg` (bytes) |
| `com.apple.accountsd.plist` | `LastAccountMigrationPluginsRunVersion`, `LastMigrationSystemVersion`, `LastSystemVersion`, `AuthenticationPluginCache` |
| `com.apple.accounts.suggestions.plist` | `InitialLocalMigration` (bool), `LocalDeviceID` (str) |
| `com.apple.icloud.findmydeviced.FMIPAccounts.plist` | `addTime` (float), `osVersion` (str), `versionHistory` (list), `lowBatteryLocate` (bool), `dsid` (str), `enableContext` (int) |
| `SysSharedContainerDomain-systemgroup.com.apple.icloud.findmydevice.managed :: Library/Preferences/FMIPStateInfo.plist` | `fmipActive` (bool), `fmipLostModeType` (int) |

`com.apple.appleaccount.informationcache.plist` 는 `AppDomain-com.apple.findmy` 와 `AppDomain-com.apple.podcasts` 의 `Library/Preferences/` 에도 있고 그쪽에는 `AAProfilePictureCacheURL` 키만 있습니다. `com.apple.AuthKit.plist` 도 App Store, 음악, 지갑, 나의 찾기, 게임, 메일, 메모, 팟캐스트 같은 여러 앱 도메인에 같은 이름으로 있습니다. 나의 찾기 계정 파일은 `SysContainerDomain-com.apple.icloud.findmydeviced :: Library/Preferences/` 아래에도 같은 이름으로 있습니다.

스토어와 메시지 쪽에는 다음 파일이 있습니다.

```
HomeDomain :: Library/Preferences/com.apple.AppleMediaServices.plist
HomeDomain :: Library/Preferences/com.apple.itunesstored.plist
HomeDomain :: Library/Preferences/com.apple.amsaccountsd.plist
HomeDomain :: Library/com.apple.itunesstored/itunesstored#.sqlitedb
HomeDomain :: Library/com.apple.itunesstored/itunesstored_private.sqlitedb
HomeDomain :: Library/com.apple.itunesstored/kvs.sqlitedb
HomeDomain :: Library/com.apple.itunesstored/purchase_intents.sqlitedb
HomeDomain :: Library/Preferences/com.apple.ids.plist
HomeDomain :: Library/Preferences/com.apple.ids.deviceproperties.plist
HomeDomain :: Library/Preferences/com.apple.imservice.ids.iMessage.plist
HomeDomain :: Library/Preferences/com.apple.imservice.ids.FaceTime.plist
```

전체 파일 시스템 추출에서 스토어 DB 는 `/mobile/Library/com.apple.itunesstored/itunesstored2.sqlitedb` 에 있습니다[8]. 스토어 구매 기록은 [앱 스토어 기록](../app-usage/app-store.md), 메시지·페이스타임 등록은 [메시지](../communications/messages/index.md) 와 [페이스타임](../communications/facetime.md) 에서 다룹니다.

관련 도메인 이름으로는 `AppDomain-com.apple.AppleIDSetupUIService`, `AppDomain-com.apple.AuthKitUIService`, `AppDomainPlugin-com.apple.AuthKitUI.AKSecondFactorAlert`, `AppDomainPlugin-com.apple.AuthKitUI.AKLocationSignInAlert`, `AppDomainPlugin-com.apple.AppleAccountIntents` 가 있습니다.

iOS 15~27 사이에 파일 이름이나 표 구성이 어떻게 바뀌었는지는 실제 데이터로 확인해야 합니다. 파일 이름의 숫자도 판마다 다를 수 있으니, `Library/Accounts/` 아래 `Accounts` 로 시작하는 `.sqlite` 파일을 모두 찾아 어느 번호가 쓰이는지 확인합니다.

## 구조

`Accounts#.sqlite` 의 표와 열은 아래와 같습니다. 이 밖에 표가 다섯 개 더 있고, `Z_METADATA`, `Z_MODELCACHE`, `Z_PRIMARYKEY` 도 있습니다. 표와 열 이름이 `Z` 로 시작하고 `Z_PK`, `Z_ENT`, `Z_OPT` 가 붙는 모양으로 보아 Core Data 가 만든 DB 로 보입니다.

| 표 | 열 |
|---|---|
| `ZACCOUNT` | `Z_PK`, `Z_ENT`, `Z_OPT`, `ZACTIVE`, `ZAUTHENTICATED`, `ZSUPPORTSAUTHENTICATION`, `ZVISIBLE`, `ZWARMINGUP`, `ZACCOUNTTYPE`, `ZPARENTACCOUNT`, `ZDATE`, `ZLASTCREDENTIALRENEWALREJECTIONDATE`, `ZACCOUNTDESCRIPTION`, `ZAUTHENTICATIONTYPE`, `ZCREDENTIALTYPE`, `ZIDENTIFIER`, `ZMODIFICATIONID`, `ZOWNINGBUNDLEID`, `ZUSERNAME`, `ZDATACLASSPROPERTIES` |
| `ZACCOUNTTYPE` | `Z_PK`, `Z_ENT`, `Z_OPT`, `ZOBSOLETE`, `ZSUPPORTSAUTHENTICATION`, `ZSUPPORTSMULTIPLEACCOUNTS`, `ZVISIBILITY`, `ZACCOUNTTYPEDESCRIPTION`, `ZCREDENTIALPROTECTIONPOLICY`, `ZCREDENTIALTYPE`, `ZIDENTIFIER`, `ZOWNINGBUNDLEID` |
| `ZACCOUNTPROPERTY` | `Z_PK`, `Z_ENT`, `Z_OPT`, `ZOWNER`, `ZKEY`, `ZVALUE` |
| `ZAUTHORIZATION` | `Z_PK`, `Z_ENT`, `Z_OPT`, `ZACCOUNTTYPE`, `ZBUNDLEID`, `ZGRANTEDPERMISSIONS`, `ZOPTIONS` |
| `ZCREDENTIALITEM` | `Z_PK`, `Z_ENT`, `Z_OPT`, `ZPERSISTENT`, `ZEXPIRATIONDATE`, `ZACCOUNTIDENTIFIER`, `ZSERVICENAME` |
| `ZACCESSOPTIONSKEY`, `ZDATACLASS` | `Z_PK`, `Z_ENT`, `Z_OPT`, `ZNAME`, `ZENUMVALUE` |

계정 DB 에서 읽는 항목[7]과 열의 대응은 아래와 같습니다. 이 대응은 열 이름으로 짐작한 것이니, 실제 데이터에서 값을 보고 확인한 뒤에 씁니다.

| 항목[7] | 짐작되는 열 |
|---|---|
| 사용자 이름 | `ZACCOUNT.ZUSERNAME` |
| 계정 설명 | `ZACCOUNT.ZACCOUNTDESCRIPTION` |
| 계정 ID | `ZACCOUNT.ZIDENTIFIER` |
| 소유 번들 ID | `ZACCOUNT.ZOWNINGBUNDLEID` |
| 부모 계정 | `ZACCOUNT.ZPARENTACCOUNT` |
| 자격 증명 종류 | `ZACCOUNT.ZCREDENTIALTYPE` |
| 계정 종류 | `ZACCOUNT.ZACCOUNTTYPE` 이 가리키는 `ZACCOUNTTYPE` 행의 `ZACCOUNTTYPEDESCRIPTION`·`ZIDENTIFIER` |
| 추가 시각 | `ZACCOUNT.ZDATE` |

`ZACCOUNTPROPERTY` 는 `ZOWNER`, `ZKEY`, `ZVALUE` 열 이름으로 보면 계정마다 딸린 속성을 키와 값으로 늘어놓는 표로 보입니다. `ZCREDENTIALITEM` 에는 `ZACCOUNTIDENTIFIER`, `ZSERVICENAME`, `ZEXPIRATIONDATE` 열이 있습니다. 비밀번호 같은 자격 증명 값이 이 DB 에 들어 있는지는 이 표의 행을 열어 값을 보고 확인합니다. 저장된 비밀번호와 토큰은 [키체인](../../01-foundations/storage/keychain.md) 과 [저장된 암호](../credentials-security/saved-passwords.md) 에서 다룹니다.

`com.apple.accountsd.plist` 의 `AuthenticationPluginCache` 안에는 계정 종류를 나타내는 식별자가 들어 있습니다.

```
Kerberos
com.apple.account.AppleAccount       com.apple.account.AppleID
com.apple.account.AppleIDAuthentication
com.apple.account.CalDAV             com.apple.account.CardDAV
com.apple.account.CloudKit           com.apple.account.DeviceLocator
com.apple.account.Exchange           com.apple.account.FaceTime
com.apple.account.FindMyFriends      com.apple.account.GameCenter
com.apple.account.Google             com.apple.account.Hotmail
com.apple.account.IMAP               com.apple.account.IMAPNotes
com.apple.account.IdentityServices   com.apple.account.LDAP
com.apple.account.Madrid             com.apple.account.POP
com.apple.account.PublishedCalendar  com.apple.account.SMTP
com.apple.account.SubscribedCalendar com.apple.account.Yahoo
com.apple.account.aol                com.apple.account.iTunesStore
com.apple.account.iTunesStore.sandbox
```

이 목록은 이름 그대로 인증 플러그인 캐시라서, 여기 식별자가 있다고 그 계정이 기기에 로그인되어 있었다는 뜻이 아닙니다. 다만 `ZACCOUNTTYPE.ZIDENTIFIER` 에서 비슷한 식별자가 나오면 계정 종류를 읽는 데 참고할 수 있고, `AppleAccount` 와 `AppleID` 가 함께 있으니 애플 계정을 찾을 때 두 이름을 모두 봅니다.

## 증거로서 의미

**증명하는 것.** 수집 시점에 `ZACCOUNT` 에 행이 있으면 그 사용자 이름과 계정 종류의 계정이 기기에 등록되어 있었다는 기록이 됩니다. 소유 번들 ID 로는 어느 앱이나 시스템 기능이 그 계정을 쓰는지 보고, 부모 계정 열로는 한 계정 아래 딸린 하위 계정을 묶어 볼 수 있습니다. 보고서에는 "이 기기의 계정 DB 에 이 사용자 이름의 이 종류 계정 행이 있고, 추가 시각 열 값은 이렇다" 처럼 씁니다.

**증명하지 못하는 것.** 계정 행은 기기에 계정이 설정되어 있었다는 사실만 보여 줍니다. 그 계정을 누가 만들었는지, 누가 비밀번호를 넣었는지, 서버 쪽에서 계정이 지금도 유효한지는 이 행으로 알 수 없습니다. `AAIsAccountSignedIn`, `AAPrimaryAccountSignInState`, `fmipActive` 같은 키는 이름으로 보면 로그인·나의 찾기 상태를 담지만, 값의 뜻이 정해져 있지 않으므로 값 하나로 "로그인되어 있었다" 고 단정하지 않습니다. `dsid` 도 애플 계정 식별 번호로 흔히 풀이되지만, 보고서에는 값만 옮기고 뜻을 단정하지 않습니다.

## 시각 해석

`ZACCOUNT` 의 `ZDATE`, `ZLASTCREDENTIALRENEWALREJECTIONDATE` 와 `ZCREDENTIALITEM` 의 `ZEXPIRATIONDATE` 가 시각 열로 보입니다. 계정 추가 시각[7]이 어느 열에 어떤 형식으로 적히는지, `ZDATE` 가 2001-01-01 기준 Mac 절대 시각인지는 실제 데이터로 확인해야 합니다. 값의 자릿수를 보고 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 따라 기준을 판별한 뒤, 계정을 추가한 때로 알려진 다른 기록과 한 번 맞춰 보고 씁니다.

설정 파일 쪽에서는 `com.apple.appleaccountd.plist` 의 `lastCloudSyncTimestampKey` 가 날짜(datetime) 형이고, `com.apple.icloud.findmydeviced.FMIPAccounts.plist` 의 `addTime` 은 실수(float) 형입니다. 실수로 적힌 시각은 Mac 절대 시각인지 유닉스 시각인지 키마다 따로 판별해야 합니다. 시간대 없이 적힌 값은 UTC 로 두고, 현지 시각은 [시간대와 시각 설정](time-zone.md) 에서 기기 시간대를 확인한 뒤 따로 더합니다.

## 함정과 한계

**플러그인 목록을 계정 목록으로 읽지 않습니다.** `AuthenticationPluginCache` 의 Google, Exchange, Yahoo 같은 이름은 지원하는 계정 종류이지 사용자가 추가한 계정이 아닙니다. 실제로 추가한 계정은 `ZACCOUNT` 의 행으로 확인합니다.

**같은 이름의 파일이 여러 도메인에 있습니다.** `com.apple.AuthKit.plist` 와 `com.apple.appleaccount.informationcache.plist` 는 여러 앱 도메인에 같은 이름으로 있고, 도메인마다 키 구성이 다릅니다. 파일 이름만 적지 말고 도메인까지 함께 적어야 다른 사람이 같은 파일을 찾을 수 있습니다.

**사본이 두 벌입니다.** `Accounts#.sqlite` 와 `VerifiedBackup/Accounts#.sqlite` 의 내용이 다를 수 있으니, 어느 파일에서 읽은 행인지 밝혀 둡니다. SQLite 의 `-wal` 파일이 함께 있으면 같이 복사해 열어야 최근 변경이 보이고, 이 처리는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

**지우기와 조작.** 계정을 기기에서 지우면 `ZACCOUNT` 의 행도 없어질 것으로 보입니다. 지운 행이 SQLite 빈 페이지나 `-wal` 에 남는지 보는 법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다. 계정이 바뀐 흔적을 조사할 때는 [계정 탈취 흔적](../../04-scenarios/incident/account-takeover.md) 의 흐름을 따릅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 명세로 만든 예시이고 특정 기기에서 나온 바이트가 아닙니다. `Accounts3.sqlite` 가 SQLite 파일이라면 첫 16바이트가 SQLite 머리글 문자열입니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

SQLite 레코드 머리글에서 직렬 형식 값 `07` 은 그 열이 8바이트 빅엔디언 IEEE 754 실수라는 뜻입니다. `ZDATE` 열 자리에 `07` 이 있으면 바로 뒤 본문의 8바이트를 실수로 읽고, 그 값이 몇 년을 가리키는지 기준 시점별로 계산해 봅니다.

```
... 07 ...                         (레코드 머리글: 이 칸은 8바이트 실수)
... XX XX XX XX XX XX XX XX ...    (레코드 본문: 실수 값 8바이트)
```

### 공개 도구로 한 번

`sqlite3` 명령줄이나 DB Browser for SQLite 같은 공개 도구로 사본을 열고, 아래처럼 계정과 종류를 이어 봅니다. `ZACCOUNT.ZACCOUNTTYPE` 이 `ZACCOUNTTYPE.Z_PK` 를 가리킨다는 것은 열 이름으로 짐작한 연결이라서, 결과의 종류 설명이 사용자 이름과 어울리는지 먼저 확인합니다.

```sql
SELECT a.Z_PK,
       a.ZUSERNAME,
       a.ZACCOUNTDESCRIPTION,
       t.ZACCOUNTTYPEDESCRIPTION,
       t.ZIDENTIFIER      AS type_identifier,
       a.ZOWNINGBUNDLEID,
       a.ZPARENTACCOUNT,
       a.ZACTIVE,
       a.ZAUTHENTICATED,
       a.ZDATE            AS raw_date
FROM ZACCOUNT a
LEFT JOIN ZACCOUNTTYPE t ON a.ZACCOUNTTYPE = t.Z_PK
ORDER BY a.Z_PK;
```

계정마다 딸린 속성은 `ZACCOUNTPROPERTY` 를 `ZOWNER` 로 묶어 봅니다. 이 연결도 열 이름으로 짐작한 것입니다.

```sql
SELECT p.ZOWNER, p.ZKEY, p.ZVALUE
FROM ZACCOUNTPROPERTY p
ORDER BY p.ZOWNER, p.ZKEY;
```

설정 파일은 Python 표준 라이브러리 `plistlib` 나 macOS 의 `plutil -p` 로 엽니다. 로컬 백업에서 파일을 꺼내는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

## 교차 검증

나의 찾기 등록 상태는 [나의 찾기](../location/find-my.md), 스토어 계정과 구매 기록은 [앱 스토어 기록](../app-usage/app-store.md), 메일 계정은 [메일 앱](../mail-cloud/apple-mail.md) 과 [지메일](../mail-cloud/gmail.md), 캘린더 계정은 [미리 알림과 캘린더](../mail-cloud/reminders-calendar.md) 와 맞춰 봅니다. 애플 계정으로 서버에 남은 자료는 [아이클라우드 백업](../../01-foundations/backups/icloud-backup.md) 과 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에서, 계정이 붙은 기기가 어떤 기기인지는 [기기 정보](device-info.md) 에서 확인합니다. 기기를 쓴 사람을 가려내는 흐름은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 를 봅니다.

## 실습

공개 시험 데이터(NIST CFReDS 등의 iOS 이미지나 백업)로 다음 질문을 풀어 봅니다.

1. `ZACCOUNT` 에 행이 몇 개 있고, 계정 종류별로 몇 개씩입니까?
2. `ZPARENTACCOUNT` 로 묶으면 애플 계정 아래에 어떤 하위 계정이 딸려 있습니까?
3. `ZDATE` 값을 Mac 절대 시각과 유닉스 시각으로 각각 풀면 어느 쪽이 그 기기의 사용 기간 안에 들어옵니까?
4. `Accounts#.sqlite` 와 `VerifiedBackup/Accounts#.sqlite` 의 행이 서로 같습니까?
5. `AuthenticationPluginCache` 의 식별자 가운데 `ZACCOUNTTYPE.ZIDENTIFIER` 에도 나오는 것은 무엇입니까?

## 참고 문헌

- [7] Apple Accounts — Forensafe — https://forensafe.com/blogs/AppleAccounts.html
- [8] iOS-Forensics-References README — RealityNet (GitHub) — https://github.com/RealityNet/iOS-Forensics-References/blob/main/README.md
