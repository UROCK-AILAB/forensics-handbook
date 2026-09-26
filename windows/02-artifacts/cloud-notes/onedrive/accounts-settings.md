---
title: "계정·설정 레지스트리"
parent: "원드라이브"
grand_parent: "아티팩트 · 클라우드·노트"
nav_order: 2180
---

# 계정·설정 레지스트리 (Accounts·Settings)

## 한 줄 요약

OneDrive 는 연결한 계정마다 사용자 레지스트리의 `HKCU\Software\Microsoft\OneDrive\Accounts` 아래에 하위 키를 하나씩 만듭니다. 이 키에는 계정 메일, 계정 ID, 동기화 폴더 경로, 로그인 시각이 남습니다. 앱은 같은 동기화 폴더를 `HKCU\Software\SyncEngines` 와 SOFTWARE 하이브의 `SyncRootManager` 키에도 적습니다.

> 이 페이지의 값 이름과 예시 값은 Windows 11 빌드 26200 과 OneDrive 26.168.0830.0006 기준입니다.

## 무엇을 기록하나 · 왜 생기나

OneDrive 동기화 앱은 계정을 연결하면 계정마다 하위 키를 하나 만듭니다. 개인 계정은 `Personal`, 회사·학교 계정은 `Business1`, `Business2` … 이고, 앱은 이 키에 계정을 알아보는 값, 동기화 폴더 경로, 여러 시각 값을 적습니다.

앱은 동기화 폴더를 Windows 클라우드 파일 기능에도 등록하기 때문에 같은 폴더가 `SyncEngines` 키와 `SyncRootManager` 키에 다시 나옵니다. 이 등록 방식 전반은 [클라우드 동기화 공통 구조](../cloud-files-api-syncrootmanager.md) 에서 다룹니다.

계정별 설정 파일은 레지스트리와 별도로 `%LOCALAPPDATA%\Microsoft\OneDrive\settings\` 아래 계정 폴더에 있습니다. 관리자는 그룹 정책 (Group Policy) 으로 OneDrive 설정을 강제할 수 있고, 그룹 정책은 `Policies` 아래에 레지스트리 키를 써서 동작합니다.

## 위치와 버전별 차이

| 위치 | 하이브 | 담긴 것 |
|---|---|---|
| `HKCU\Software\Microsoft\OneDrive` | 사용자 `NTUSER.DAT` | 앱 버전, 로그인한 적이 있는지 표시, 개인 계정 연결을 끊은 기록 |
| `HKCU\Software\Microsoft\OneDrive\Accounts\<Personal 또는 BusinessN>` | 사용자 `NTUSER.DAT` | 계정 신원, 동기화 폴더, 시각 값, 알려진 폴더 이동 상태 |
| `HKCU\Software\SyncEngines\Providers\OneDrive\<…>` | 사용자 `NTUSER.DAT` | 동기화 폴더 경로와 라이브러리 종류 |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\SyncRootManager\OneDrive!<…>` | `SOFTWARE` | 사용자 SID 별 동기화 폴더 등록 |
| `HKLM\SOFTWARE\Policies\Microsoft\OneDrive`, `HKCU\SOFTWARE\Policies\Microsoft\OneDrive` | `SOFTWARE`, 사용자 `NTUSER.DAT` | 관리자 정책 |
| `%LOCALAPPDATA%\Microsoft\OneDrive\settings\<Personal 또는 BusinessN>\` | 파일 | 계정별 ini 설정 파일과 DB |

`settings` 폴더는 회사 계정을 `Business1` 부터 `Business9` 까지 나눠 둡니다. 하이브 파일을 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

값의 이름과 구성은 OneDrive 앱이 정합니다. 이 페이지의 값 목록은 OneDrive 26.168.0830.0006 기준이라 옛 버전에는 없는 값이 있을 수 있습니다.

`SyncRootManager` 키에는 Windows 버전에 따라 생기는 값이 있습니다. 동기화 앱은 아래 값을 동기화 루트 키에 적습니다.

| 값 | 쓰기 시작한 Windows |
|---|---|
| `CopyHook` | Windows 10 Insider 빌드 19624 이후 |
| `ShareHandler` | Windows 11 21H2 이후 |
| `SearchHandlerFactory` | Windows 11 24H2 이후. 이 검색 기능은 Copilot+ PC 와 AI 기능을 켠 Cloud PC 에서 지원합니다[3] |

## 구조

### 루트 키 `HKCU\Software\Microsoft\OneDrive`

| 값 | 형식 | 내용 |
|---|---|---|
| `Version`, `LastRunOneDriveVersion` | REG_SZ | 앱 버전 문자열입니다. 예: `26.168.0830.0006` |
| `UserFolder` | REG_SZ | 동기화 폴더 경로입니다 |
| `InstallerType` | REG_SZ | 예: `Standard` |
| `SilentBusinessConfigCompleted` | DWORD | 자동 연결 정책(SilentAccountConfig)이 사용자를 OneDrive 에 연결하는 데 성공하면 생깁니다. 사용자가 동기화를 멈춘 뒤 다시 자동 연결되지 않게 막는 표시입니다. 예: 1 |
| `ClientEverSignedIn` | DWORD | 예: 1 |
| `PersonalUnlinkedTimeStamp`, `LastPersonalUnlinkedTimeStamp` | QWORD | 개인 계정 연결을 끊은 시각입니다. Unix 초입니다 |
| `LastPersonalUnlinkedReason` | REG_SZ | 개인 계정 연결을 끊은 이유입니다. 예: `12-DeleteAccountSettingsReason::UserTriggeredUnlink` |
| `OneAuthUnrecoverableTimestamp` | — | 아래 SysPrep 안내에 나오는 값입니다 |
| `MachineGuidCollection`, `HostNameCollection`, `UserNameCollection`, `UserDomainCollection` | — | 내용에 관한 공개 자료가 없어 검체에서 확인합니다 |

이미지를 준비(SysPrep)하기 전에는 이 키의 값 네 개를 지웁니다[2]. `SilentBusinessConfigCompleted`, `ClientEverSignedIn`, `PersonalUnlinkedTimeStamp`, `OneAuthUnrecoverableTimestamp` 입니다.

`LastPersonalUnlinkedReason` 의 `UserTriggeredUnlink` 는 이름으로 보아 사용자가 직접 연결을 끊은 경우로 보입니다. 다른 이유 문자열은 공개 자료가 없어 검체에서 확인합니다.

### 계정 키 `Accounts\<계정>`

> 그림 자리: `Accounts` 아래 `Personal`·`Business1` 키와, 각 키 아래 하위 키(`Tenants`·`ScopeIdToMountPointPathCache`·`AuthenticationURLs`·`USQInformation`·`WindowsSecurityCenterIntegration`)를 나무 모양으로 보여 주는 그림

**신원 값**

| 값 | 형식 | 내용 |
|---|---|---|
| `UserEmail` | REG_SZ | 로그인한 계정 메일 |
| `cid` | REG_SZ | 계정 ID. 개인 계정은 16자리 16진수, 회사 계정은 GUID(36자)입니다 |
| `OneAuthAccountId`, `NamespaceRootId` | REG_SZ | 계정 관련 ID |
| `UserFolder` | REG_SZ | 이 계정의 동기화 폴더 경로 |

회사 계정에는 `DisplayName`, `UserName`, `PUID`, `ConfiguredTenantId`, `ServiceEndpointUri`, `SPOResourceId`, `TeamSiteSPOResourceId` 가 더 있습니다. 이 값들은 [회사용 OneDrive와 SharePoint 동기화](business-tenant.md) 에서 다룹니다.

**시각 값**

아래 값은 QWORD 이고, 내용은 Unix 초입니다.

| 값 | 이름으로 짐작한 뜻 |
|---|---|
| `ClientFirstSignInTimestamp` | 처음 로그인한 때 |
| `LastSignInTime`, `LastAttemptedSignInTime` | 마지막 로그인, 마지막 로그인 시도 |
| `LastUserActivityTimestamp` | 마지막 사용자 활동 |
| `LastDAUEventTimestamp_Upload`, `_Download`, `_ActiveUser`, `_FindChanges`, `_Thumbnail` | 올리기·내려받기·활동·변경 찾기·썸네일 쪽 마지막 사건 |
| `KFMOnboardingEnabledStartTime`, `LastKFMOptInTime`, `LastKnownFolderBackupTime` | 알려진 폴더 이동 (Known Folder Move, KFM) 관련 시각 |
| `WebView2InstallCheckedTimeStamp` | WebView2 설치 여부를 확인한 때 |

`FirstRunSignInOriginDateTime` 은 형식이 REG_SZ 이지만 내용은 Unix 초 숫자를 적은 문자열입니다.

각 값을 정확히 언제 적는지는 공개 자료가 없습니다. 예를 들어 `_Upload` 가 올리기를 시작한 때인지 끝낸 때인지 알 수 없습니다. 보고서에는 이름에서 짐작한 뜻이라고 밝힙니다.

**상태 값**

| 값 | 형식 | 값 예 |
|---|---|---|
| `LastSignInResult` | DWORD | 0 |
| `HasMadeFirstUpload` | DWORD | 1 |
| `LastKnownFolderMigrationState` | REG_SZ (JSON) | `{"Camera Roll":5,"Desktop":5,"Documents":5,"Pictures":5,"Screenshots":5}` |
| `KfmFoldersProtectedNow` | DWORD | 3584 |
| `LastKFMOptInSource` | DWORD | (숫자) |
| `LastPerFolderMigrationScanResult` | REG_SZ (JSON) | (JSON) |

알려진 폴더 이동 값은 어느 폴더를 OneDrive 로 옮겼는지 보여 줍니다. 숫자 코드(위의 5, 3584 등)의 뜻은 공개 자료가 없습니다.

**계정 종류에 따라 있는 값**

| 계정 | 값 | 내용 |
|---|---|---|
| 개인 | `VaultShortcutPath` | 개인 중요 보관소 바로가기 경로 |
| 개인 | `AccountMarket` | 국가 코드. 예: `KR` |
| 개인 | `LastKnownSubscriptionState`, `LastKnownSubscriptionExpiry` | 구독 상태(예: `Active`)와 만료 값(QWORD) |
| 회사 | `Business` | DWORD 1 |
| 회사 | `EdpManaged` | DWORD |
| 회사 | `GrooveTakeoverAttemptedOperations`, `GrooveTakeoverSuccessfulOperations` | DWORD. 뜻은 회사용 페이지에서 다룹니다 |

**하위 키**

| 하위 키 | 내용 |
|---|---|
| `Tenants\<동기화 폴더 표시 이름>` | 값 이름이 동기화 폴더 경로입니다. 예: `Personal\Tenants\OneDrive`, `Business1\Tenants\OneDrive - <회사 이름>` |
| `ScopeIdToMountPointPathCache` | 값 이름이 32자리 16진수 범위 ID (scope ID) 입니다 |
| `AuthenticationURLs` | `Authority`, `DiscoveryResourceId`, `DiscoveryApi`, `GraphApi`, `FederationProvider`, `NextEmailHRDUpdate` |
| `USQInformation` (개인 계정) | 저장 공간 정보입니다. 값은 `total`, `used`, `remaining`, `state`, `lastFetchTime` 입니다. 하위 키 `services\OneDrive`, `services\Outlook` 에 `used` 가 있습니다. 단위는 공개 자료가 없어 검체에서 확인합니다 |
| `WindowsSecurityCenterIntegration` | `WscRegistrationGuid` |

연결을 끊은 계정의 키에는 값이 거의 남지 않을 수 있습니다. 예를 들어 `Accounts\Business2` 에 `KFMOnboardingEnabledStartTime` 하나만 남기도 합니다.

### `HKCU\Software\SyncEngines\Providers\OneDrive`

하위 키 이름은 `Personal`, `Business1`, 또는 32자리 범위 ID 입니다. 아래 값의 형식은 모두 REG_SZ 입니다.

| 값 | 내용 |
|---|---|
| `MountPoint` | 동기화 폴더 경로 |
| `LastModifiedTime` | `2026-09-22T22:02:13` 같은 날짜 문자열 |
| `UrlNamespace` | 서비스 쪽 주소 |
| `LibraryType` | `Personal`·`Business1` 키는 `personal`, 범위 ID 키는 `mysite` 입니다. 범위 ID 키는 회사 계정의 개인 문서 라이브러리입니다 |
| `CID` | 계정 ID |
| `IsOfficeSyncIntegrationEnabled` | 오피스 동기화 연동 설정 |

범위 ID 키에는 `WebUrl`, `OpcEnabled`, `AIPIntegrationEnabled`, `ZipItEnabled`, `SequentialID` 가 더 있습니다.

### `HKLM\…\Explorer\SyncRootManager`

키 이름은 `OneDrive!<사용자 SID>!<Personal 또는 Business1>|<32자리 범위 ID>` 모양입니다.

| 항목 | 내용 |
|---|---|
| 값 | `DisplayNameResource`, `IconResource`, `Flags`, `Handler`, `CopyHook`, `ShareHandler`, `SearchHandlerFactory`, `ThumbnailProvider`, `UriHandler`, `AUMID`, `Cid` 등 |
| 회사 계정 키에만 있는 값 | `TenantName` |
| 하위 키 `UserSyncRoots` | 값 이름이 사용자 SID 이고, 데이터(REG_SZ)가 동기화 폴더 경로입니다 |

같은 32자리 범위 ID 가 세 곳에 나옵니다. `ScopeIdToMountPointPathCache` 의 값 이름, `SyncEngines` 의 하위 키 이름, `SyncRootManager` 키 이름의 뒷부분입니다. 이 ID 로 세 키를 이어 읽습니다.

### settings 폴더의 ini 파일

| 파일 | 인코딩 | 내용 |
|---|---|---|
| `settings\Personal\<cid>.ini`, `settings\Business1\<cid>.ini` | UTF-16LE | 줄 이름은 `libraryScope`, `lastRefreshTime`, `installID`, `originatorID`, `OfficeOriginatorID`, `lastKnownOSVersion`, `bytesTransferred`, `requestsSent`, `edpManaged`, `edpManagedSince`, `Subscription` 등입니다 |
| `global.ini` | UTF-16LE | `cid`, `LastCleanShutdownTimestamp`, `IsCleanShutdown`, `LocalMassDeleteDetectedTime`, `LastSyncVerificationCompletedTimestamp` 등이 있습니다 |

- `<cid>.ini` 의 파일 이름은 레지스트리 `Accounts\<계정>` 의 `cid` 값과 같습니다. 회사 계정도 `ConfiguredTenantId` 가 아니라 `cid` 와 같습니다.
- 같은 폴더에는 `ClientPolicy.ini`, `ECSConfig.json`, `SurveyManagerState.json`, `SyncEngineDatabase.db`, `SafeDelete.db`, `SettingsDatabase.db`, `UXDatabase.db`, `OCSI.db`, `CxP.db`, `KFM.db` 등도 있습니다.
- `SyncEngineDatabase.db` 와 `SafeDelete.db` 는 [동기화 DB](syncenginedatabase-db.md) 에서 다룹니다.
- UTF-16LE 파일을 읽는 법은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에 있습니다.

### 정책 키

그룹 정책은 레지스트리 키를 써서 동작합니다. 설정을 "구성 안 됨"으로 되돌려도 이미 쓴 키는 지워지지 않습니다. 아래는 개인 사용과 일반 동작에 관한 정책입니다. 회사 계정과 조직(테넌트)에 관한 정책은 [회사용 OneDrive와 SharePoint 동기화](business-tenant.md) 에 모았습니다.

| 키와 값 | 뜻 |
|---|---|
| `HKCU\SOFTWARE\Policies\Microsoft\OneDrive` `DisablePersonalSync` = 1 | 개인 계정 동기화를 막습니다 |
| `HKCU\Software\Policies\Microsoft\OneDrive` `EnableAutoStart` = 1 | OneDrive 를 자동으로 시작합니다 |
| `HKLM\SOFTWARE\Policies\Microsoft\OneDrive` `ForcedLocalMassDeleteDetection` = 1 | 대량 삭제 확인을 강제합니다 |
| `HKLM\SOFTWARE\Policies\Microsoft\OneDrive` `LocalMassDeleteFileDeleteThreshold` | 로컬에서 몇 개 넘게 지우면 알릴지 0 ~ 100000 사이로 정합니다 |
| `HKLM\SOFTWARE\Policies\Microsoft\OneDrive\EnableODIgnoreListFromGPO` | 올리지 않을 파일 목록입니다 |
| `HKLM\SOFTWARE\Policies\Microsoft\OneDrive` `FilesOnDemandEnabled` = 1 | 파일 주문형 (Files On-Demand) 을 켭니다 |

`LocalMassDeleteFileDeleteThreshold` 를 구성하지 않으면, 짧은 시간에 파일을 200개 넘게 지울 때 알림이 뜹니다. 파일 주문형 옵션이 보이지 않으면 `HKLM\SYSTEM\CurrentControlSet\Services\CldFlt` 의 `Start` 가 2(AUTO_START)인지 보는데, 이 드라이버가 Windows Cloud Files Filter Driver 입니다. 서비스 키 읽는 법은 [서비스·드라이버](../../persistence/services-drivers.md) 에 있습니다. 정책 키는 아예 없을 수도 있습니다.

## 증거로서 의미

### 증명하는 것

- `Accounts` 아래에 계정 하위 키가 있으면, 이 Windows 사용자 프로필에서 그 OneDrive 계정을 연결한 적이 있습니다.
- `UserEmail` 과 `cid` 로 어느 계정을 연결했는지 알 수 있습니다.
- `UserFolder`, `MountPoint`, `UserSyncRoots` 로 동기화 폴더가 어디 있었는지 알 수 있습니다.
- `SyncRootManager` 는 HKLM 에 있지만 키 이름과 `UserSyncRoots` 에 사용자 SID 가 들어갑니다. 그래서 SOFTWARE 하이브 하나로 이 PC 에서 OneDrive 를 쓴 사용자를 가려낼 수 있을 것으로 보입니다.
- `PersonalUnlinkedTimeStamp` 와 `LastPersonalUnlinkedReason` 이 있으면 개인 계정 연결을 끊은 기록이 있습니다.
- `SilentBusinessConfigCompleted` 가 있으면 자동 연결 정책이 회사 계정을 연결하는 데 성공한 적이 있습니다.
- `LastKnownFolderMigrationState` 는 바탕 화면·문서·사진 같은 폴더를 OneDrive 로 옮겼는지 보여 줍니다. 숫자의 뜻은 공개 자료가 없습니다.
- 정책 키에 값이 있으면 관리자가 그 정책을 건 적이 있습니다.

### 증명하지 못하는 것

- 어떤 파일을 올렸거나 내려받았는지는 이 키로 알 수 없습니다. 파일 단위 기록은 [동기화 DB](syncenginedatabase-db.md) 와 [로그](odl-odlgz.md) 에 있습니다.
- 시각 값의 이름이 뜻을 보장하지 않습니다. 정확한 기록 조건은 공개 자료가 없습니다.
- `UserEmail` 은 OneDrive 에 로그인한 계정입니다. 그 시각에 PC 앞에 있던 사람을 알려 주지 않습니다.
- 정책 값이 있다고 지금도 그 정책이 걸려 있다는 뜻은 아닙니다. "구성 안 됨"으로 되돌려도 키가 남기 때문입니다.
- 값이 없다고 쓰지 않았다는 뜻은 아닙니다. 연결을 끊은 계정 키에는 값이 거의 남지 않을 수 있습니다. 이미지로 배포한 PC 라면 관리자가 SysPrep 전에 루트 키 값을 지웠을 수도 있습니다.

보고서에는 "OneDrive 를 썼다" 대신 이렇게 씁니다. "사용자 A 의 NTUSER.DAT 에 OneDrive 계정 키 `Business1` 이 있다. `UserEmail` 은 X 이고, `ClientFirstSignInTimestamp` 는 Y(UTC)이다. 이 값의 정확한 기록 조건은 공개 문서로 확인되지 않았다."

## 시각 해석

| 값 | 형식 | 기준 |
|---|---|---|
| `Accounts\<계정>` 의 시각 값, 루트 키의 `PersonalUnlinkedTimeStamp` 등 | QWORD, Unix 초 | 1970-01-01 00:00 UTC 부터 센 초. 변환하면 UTC 입니다 |
| `FirstRunSignInOriginDateTime` | REG_SZ 에 적은 Unix 초 숫자 | 위와 같습니다 |
| `SyncEngines` 의 `LastModifiedTime` | REG_SZ 날짜 문자열 | 시간대 표시가 없습니다. OneDrive 시작 시각(UTC)과 맞아서 UTC 로 보입니다. 공식 설명은 없습니다 |
| 키의 마지막 기록 시각 | 하이브에 있는 키 단위 시각 | [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 를 참고합니다 |

Unix 초로 읽는 근거는 이렇습니다. `Accounts\Personal` 의 `LastSignInTime` 이 1790114532 이면 2026-09-22 22:02:12 UTC 입니다. 같은 PC 에서 실행 중이던 OneDrive 프로세스의 시작 시각은 22:02:11 UTC 로, 1초 차이입니다.

Unix 초를 변환하는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

## 함정과 한계

- **값 목록은 OneDrive 26.168.0830.0006 기준입니다.** 앱 버전이 다르면 값 이름과 구성이 다를 수 있습니다.
- **숫자 코드의 뜻을 짐작으로 채우지 않습니다.** `LastKnownFolderMigrationState` 의 5, `KfmFoldersProtectedNow` 의 3584, `USQInformation` 의 단위는 모두 공개 자료가 없습니다.
- **QWORD 를 FILETIME 으로 읽지 않습니다.** 레지스트리 도구가 QWORD 를 FILETIME 으로 풀어 보여 주면 1601년 초의 날짜가 나옵니다. 아래 헥스 예시에서 확인합니다.
- **회사 계정의 `UserName` 과 `UserEmail` 은 값이 다를 수 있습니다.** 보고서에는 어느 값을 썼는지 밝힙니다.
- **ini 파일 이름은 테넌트 ID 가 아닙니다.** 회사 계정도 `cid` 로 파일 이름을 짓습니다.
- **`Collection` 으로 끝나는 루트 키 값 네 개는 내용에 관한 공개 자료가 없습니다.** 이름만으로 무엇이 들었는지 단정하지 않습니다.
- **알려진 폴더 이동을 켠 PC 는 바탕 화면·문서 경로가 OneDrive 폴더 안으로 바뀝니다.** 다른 아티팩트의 경로를 읽을 때 [원드라이브 허브](index.md) 의 설명을 참고합니다.

## 직접 분석해 보기

### 헥스로 한 번

**QWORD 시각 값.** 아래는 명세로 만든 예시입니다. 특정 PC 에서 나온 값이 아닙니다. REG_QWORD 는 8바이트 정수를 리틀엔디언 (little-endian) 으로 저장합니다.

```
값 데이터 (8바이트):  80 00 92 65 00 00 00 00
뒤집어 읽기:          0x0000000065920080 = 1704067200
Unix 초로 읽기:       1704067200 → 2024-01-01 00:00:00 UTC
FILETIME 으로 잘못 읽기: 1704067200 × 100ns = 170.4초 → 1601-01-01 00:02:50 UTC
```

날짜가 1601년 초로 나오면 Unix 초를 FILETIME 으로 읽은 것입니다.

**`SyncRootManager` 키 이름.** 아래는 키 이름 형식을 따라 만든 예시입니다. SID 와 범위 ID 자리는 비워 두었습니다.

```
OneDrive!S-1-5-21-…-1001!Business1|0123456789abcdef0123456789abcdef
└ 제공자 ┘└── 사용자 SID ──┘└ 계정 ┘ └────── 32자리 범위 ID ──────┘
```

- 사용자 SID 는 [사용자 프로필 목록](../../system-account/profilelist.md) 에서 사용자 이름으로 바꿉니다.
- 범위 ID 는 같은 사용자 `NTUSER.DAT` 의 `SyncEngines\Providers\OneDrive\<범위 ID>` 키와 맞춰 봅니다.

### 공개 도구로 한 번

1. 사용자 `NTUSER.DAT` 와 `SOFTWARE` 하이브를 사본으로 뜹니다. 하이브 옆의 트랜잭션 로그 파일도 함께 뜹니다.
2. 레지스트리 하이브 뷰어로 `Software\Microsoft\OneDrive\Accounts` 를 열고 계정 키를 모두 내보냅니다.
3. 시각 값은 Unix 초로 변환합니다. 도구가 자동으로 바꿔 준 값은 위 헥스 예시처럼 한 번 직접 맞춰 봅니다.
4. `SOFTWARE` 하이브의 `Microsoft\Windows\CurrentVersion\Explorer\SyncRootManager` 에서 `OneDrive!` 로 시작하는 키를 모읍니다.

살아 있는 PC 에서는 Windows 에 들어 있는 `reg` 명령으로도 볼 수 있습니다.

```
reg query "HKCU\Software\Microsoft\OneDrive\Accounts" /s
```

공개 도구 OneDriveExplorer 는 사용자 레지스트리 하이브로 동기화 폴더 위치를 찾습니다[4]. 도구 결과는 위 수작업 결과와 한 번 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 동기화 DB | `cid` 와 범위 ID 가 같은 라이브러리에서 어떤 파일을 동기화했는지 봅니다 | [동기화 DB](syncenginedatabase-db.md) |
| 로그 | 계정 키의 시각 무렵에 앱이 무엇을 했는지 봅니다 | [로그 (ODL·ODLGZ)](odl-odlgz.md) |
| 회사 계정 값 | 테넌트 ID·SharePoint 주소로 어느 조직 계정인지 봅니다 | [회사용 OneDrive와 SharePoint 동기화](business-tenant.md) |
| 사용자 프로필 목록 | `SyncRootManager` 의 SID 가 어느 사용자인지 봅니다 | [사용자 프로필 목록](../../system-account/profilelist.md) |
| 바로가기 파일·점프리스트 | 동기화 폴더 경로 아래 파일을 연 기록을 찾습니다 | [바로가기 파일](../../file-folder-usage/lnk.md), [점프리스트](../../file-folder-usage/jump-lists.md) |
| 셸백 | 동기화 폴더를 탐색기로 둘러본 기록을 봅니다 | [셸백](../../file-folder-usage/shellbags/index.md) |
| 로그온 기록 | `LastSignInTime` 이 Windows 로그온 시각과 가까운지 봅니다 | [로그온·로그오프](../../event-logs/logon-events/index.md) |

## 실습

OneDrive 를 쓴 공개 검체(NIST CFReDS 등)에서 `NTUSER.DAT` 와 `SOFTWARE` 하이브를 꺼내 아래 질문을 풀어 봅니다.

1. `Accounts` 아래에 어떤 계정 키가 있습니까? 값이 거의 없는 키가 있다면 어떤 값이 남아 있습니까?
2. 계정마다 `cid` 는 몇 자리입니까? 개인 계정과 회사 계정을 `cid` 형식만으로 가를 수 있습니까?
3. `settings` 폴더의 ini 파일 이름이 `cid` 와 같습니까?
4. `ClientFirstSignInTimestamp` 와 `LastSignInTime` 을 UTC 로 바꿉니다. 같은 날 Windows 로그온 기록과 몇 분 차이가 납니까?
5. `SyncRootManager` 에서 `OneDrive!` 로 시작하는 키는 몇 개입니까? 사용자 SID 는 몇 명입니까?
6. 정책 키가 있습니까? 있다면 `ForcedLocalMassDeleteDetection` 이나 `DisablePersonalSync` 가 걸려 있습니까?

## 참고 문헌

1. Microsoft Learn, "Use OneDrive policies to control sync settings" (2026-09 갱신) — https://learn.microsoft.com/en-us/sharepoint/use-group-policy
2. Microsoft Learn, "Silently configure user accounts" — https://learn.microsoft.com/en-us/sharepoint/use-silent-account-configuration
3. Microsoft Learn, "Build a Cloud Sync Engine that Supports Placeholder Files" — https://learn.microsoft.com/en-us/windows/win32/cfapi/build-a-cloud-file-sync-engine
4. Beercow/OneDriveExplorer, README — https://github.com/Beercow/OneDriveExplorer
