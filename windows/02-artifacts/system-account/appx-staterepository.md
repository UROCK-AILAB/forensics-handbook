---
title: "스토어 앱 설치 목록"
parent: "아티팩트 · 시스템·계정"
nav_order: 670
---

# 스토어 앱 설치 목록 (AppX·StateRepository)

> 이 페이지에서 "(확인 범위: 조사 PC)" 는 Windows 11 25H2(빌드 26200.9457), 한국 표준시(UTC+9) PC 한 대에서 직접 열어 본 사실을 뜻합니다. 다른 버전이나 다른 PC 에서는 따로 확인해야 합니다.

## 한 줄 요약

스토어 앱은 패키지 (package) 단위로 설치합니다. 패키지를 어느 사용자에게 언제 등록했는지는 `StateRepository-Machine.srd` 라는 SQLite DB 에 남습니다. 설치·업데이트·제거 과정은 AppXDeploymentServer 이벤트 로그에 남습니다. 이 로그는 금방 밀려날 수 있어서(조사 PC 에서는 8일치) DB 와 함께 봅니다.

## 무엇을 기록하나 · 왜 생기나

Windows 는 스토어 앱을 패키지로 설치하며, 패키지 형식의 이름은 MSIX 입니다. MSIX 는 예전 APPX 의 새 이름입니다. 패키지 하나에는 앱 (application) 이 0개에서 100개까지 들어가고, 프레임워크 패키지와 리소스 패키지에는 앱이 없습니다.

앱 본체는 `C:\Program Files\WindowsApps\<패키지 전체 이름>\` 폴더에 설치됩니다. 패키지는 사용자마다 따로 등록하므로 같은 패키지라도 사용자마다 등록 기록이 따로 남습니다. (확인 범위: 조사 PC)

StateRepository DB 에는 설치된 패키지, 패키지 안의 앱, 패키지를 등록한 사용자, 사용자별 등록 시각이 표로 남습니다. 레지스트리에는 모든 사용자용 목록과 사용자별 목록이 따로 남고, 설치·등록·제거 작업은 이벤트 로그에 작업마다 남습니다. (확인 범위: 조사 PC)

이 기록으로 아래 질문에 답합니다.

- 이 PC 에 어떤 스토어 앱이 있었나
- 그 앱을 어느 계정에 언제 등록했나
- 기본 탑재 앱인가, 나중에 들인 앱인가
- 지금은 없는 옛 버전이 있었나
- .msix 파일을 직접 받아 설치한 흔적이 있나

## 위치와 버전별 차이

| 위치 | 담긴 것 |
|---|---|
| `C:\ProgramData\Microsoft\Windows\AppRepository\StateRepository-Machine.srd` | 패키지·앱·사용자·등록 시각 (SQLite) |
| `C:\ProgramData\Microsoft\Windows\AppRepository\StateRepository-Deployment.srd` | 배포 관련 표 (SQLite) |
| 두 DB 옆의 `-wal`, `-shm` 파일 | DB 본체에 아직 반영하지 않은 최근 변경 |
| `AppRepository\<패키지 전체 이름>.xml` | 패키지마다 파일 하나 |
| `AppRepository\Packages\`, `AppRepository\Families\` | 하위 폴더 |
| `C:\Program Files\WindowsApps\<패키지 전체 이름>\` | 앱 본체 |
| `C:\Program Files\WindowsApps\Deleted\<패키지 전체 이름><GUID>\` | 지우는 이전 버전을 옮겨 두는 곳 |
| `%LOCALAPPDATA%\Packages\<패키지 계열 이름>\` | 사용자별 앱 데이터 |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Appx\AppxAllUserStore` | 모든 사용자용 패키지 목록 |
| `HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages\<패키지 전체 이름>` | 사용자별 패키지 목록 |
| `%SystemRoot%\System32\Winevt\Logs\` 의 AppX 관련 .evtx | 설치·등록·제거 작업 |

표의 위치는 모두 조사 PC 에서 확인했습니다. (확인 범위: 조사 PC)

- 두 .srd 파일은 첫 16바이트가 `SQLite format 3\0` 이라서, 확장자는 .srd 이지만 SQLite DB 입니다.
- 조사 PC 에서 `StateRepository-Machine.srd-wal` 은 103,032바이트로 비어 있지 않았습니다.
- 조사 PC 의 `AppRepository` 폴더에는 `<패키지 전체 이름>.xml` 파일이 393개 있었고, Package 표의 행 수도 393개였습니다.
- 이전 버전을 지울 때 `WindowsApps\Deleted\` 로 옮긴 뒤 지운다는 내용이 이벤트 471(삭제 실패 오류)에 남아 있었고, 이 폴더는 실제로 있었습니다.
- 사용자별 앱 데이터 폴더 아래에는 AC, AppData, LocalCache, LocalState, RoamingState, Settings, SystemAppData, TempState 가 있었습니다. 앱 데이터의 구조는 [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) 에서 다룹니다.
- 일부 앱 폴더에는 `SystemAppData\Helium\UserClasses.dat` 라는 앱 전용 레지스트리 하이브가 따로 있습니다. 조사 PC 의 hivelist 에는 이 하이브가 `\REGISTRY\WC\Silo<GUID>user_classes` 로 올라와 있었습니다.
- HKCU 쪽 키는 파일로는 `C:\Users\<사용자>\AppData\Local\Microsoft\Windows\UsrClass.dat` 에 있습니다. 조사 PC 의 `HKLM\SYSTEM\CurrentControlSet\Control\hivelist` 에서 `\REGISTRY\USER\<SID>_Classes` 가 이 파일을 가리켰습니다.

버전 차이는 이렇게 정리합니다.

- StateRepository 가 처음 생긴 Windows 버전은 이번에 연 자료로 확인하지 못했습니다.
- 이 페이지의 표·칸 이름은 조사 PC 한 대에서 본 것입니다. 다른 버전의 검체에서는 표 목록부터 확인합니다.

SQLite 파일과 WAL 의 구조는 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서, 하이브 파일은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 구조

### 패키지 이름 읽는 법

패키지 신원 (package identity) 은 다섯 부분입니다. 이름 (Name), 버전 (Version), 아키텍처 (Architecture), 리소스 ID (ResourceId), 게시자 (Publisher) 입니다.

패키지 전체 이름 (Package Full Name) 은 아래 형식입니다.

```
<Name>_<Version>_<Architecture>_<ResourceId>_<PublisherId>
Microsoft.Windows.Photos_2020.20090.1002.0_x64__8wekyb3d8bbwe
```

| 부분 | 예의 값 | 읽는 법 |
|---|---|---|
| Name | `Microsoft.Windows.Photos` | 패키지 이름입니다 |
| Version | `2020.20090.1002.0` | Major.Minor.Build.Revision 순서의 10진수입니다. 각 부분은 최대 65535 입니다 |
| Architecture | `x64` | neutral, x86, x64, arm, arm64, x86a64 가운데 하나입니다 |
| ResourceId | (비어 있음) | 비어 있으면 밑줄 두 개가 이어 붙습니다. 번들 (bundle) 의 ResourceId 는 항상 `~` 입니다 |
| PublisherId | `8wekyb3d8bbwe` | 게시자에서 만든 13자 문자열입니다 |

- 패키지 계열 이름 (Package Family Name) 은 `<Name>_<PublisherId>` 형식입니다. 예: `Microsoft.Windows.Photos_8wekyb3d8bbwe`
- 계열 이름에는 버전과 아키텍처가 없어서 앱을 업데이트해도 계열 이름은 그대로입니다. 앱 데이터와 보안 범위는 보통 계열 단위로 잡히므로 버전이 올라가도 설정이 이어집니다.
- PublisherId 는 서명 인증서의 주체 이름(Publisher)으로 만든 13자 고정 길이 문자열이고, Crockford Base32 로 적기 때문에 I·L·O·U 가 들어가지 않습니다.
- `8wekyb3d8bbwe` 는 Microsoft 의 PublisherId 입니다.
- 대소문자는 Publisher 에서만 구분합니다. 이름·ResourceId·PublisherId·전체 이름·계열 이름은 대소문자를 가리지 않습니다.
- 앱 식별자는 AUMID (ApplicationUserModelID) 입니다. 패키지 계열 이름과 매니페스트 Application 요소의 ID 로 만듭니다.

### StateRepository-Machine.srd 의 표

조사 PC 의 이 DB 에는 표 (table) 가 90개쯤 있었습니다. 분석에 먼저 쓰는 표는 아래와 같습니다. (확인 범위: 조사 PC)

| 표 | 주요 칸 (column) | 알려 주는 것 |
|---|---|---|
| Package | `_PackageID`, `PackageFamily`, `PackageFullName`, `ResourceId`, `Architecture`, `Version`(정수), `IsInbox`, `PackageType`, `DisplayName`, `PublisherDisplayName`, `Description`, `SignatureOrigin`, `PackageOrigin`, `OSMinVersion`, `OSMaxVersionTested` | 지금 설치된 패키지입니다. 설치 시각 칸은 없습니다 |
| PackageFamily | `Name`, `Publisher`, `PublisherId`, `PackageFamilyName`, `PackageSID`(BLOB), `RawPublisher` | 계열 이름과 게시자입니다. Package 표의 `PackageFamily` 칸이 이 표의 번호를 가리킵니다 |
| PackageUser | `Package`, `User`, `InstallTime`, `OSVersionWhenInstalled`, `WhenRestored`, `IsExplicitlyInstalled`, `DeploymentState` | 패키지를 등록한 사용자와 사용자별 설치 시각입니다 |
| User | `UserSid`(BLOB) | 사용자입니다. SID 는 이진 형식입니다 |
| PackageLocation | `Package`, `InstalledLocation`, `MutableLocation` | 설치 폴더입니다 |
| Application | `Package`, `ApplicationUserModelId`, `DisplayName`, `Executable`, `Entrypoint`, `PackageRelativeApplicationId` | 패키지 안의 앱과 실행 파일입니다 |
| PackageIdentity | `PackageFamily`, `PackageFullName` | 지금은 설치돼 있지 않은 옛 버전 이름까지 남습니다. 시각 칸은 없습니다 |
| DeploymentHistory | `PackageIdentity`, `User`, `HResult`, `WhenOccurred` | 배포 작업의 결과 코드와 시각입니다 |

그 밖에 PackageUserStatus, PackageMachineStatus, ProvisionedPackage, ProvisionedPackageDeleted, EndOfLifePackage, Bundle, BundlePackage, Dependency, ApplicationUser, AppExecutionAlias, Protocol, FileTypeAssociation, PrimaryTile, SecondaryTile 같은 표가 있었습니다.

조사 PC 에서 본 값은 이렇습니다. (확인 범위: 조사 PC)

- User 표는 5행이었습니다. S-1-0-0, S-1-5-18, S-1-5-19, 로컬 계정 2개(RID 1000·1001)입니다.
- PackageUser 에는 IsInbox=1(기본 탑재) 패키지가 129건, IsInbox=0 패키지가 362건 있었습니다.
- SYSTEM(S-1-5-18) 행은 IsExplicitlyInstalled=0·DeploymentState=1 인 경우가 많았습니다.
- 로그인 사용자 행은 IsExplicitlyInstalled=1·DeploymentState=2 인 경우가 많았습니다.
- DeploymentState, PackageOrigin, SignatureOrigin, PackageType, PackageUserStatus 의 Status 숫자가 무슨 뜻인지는 확인하지 못했습니다.
- PackageIdentity 527행 가운데 134행은 Package 표에 없는 이름이었습니다.
- 한 앱은 현재 버전 1개 말고도 옛 버전 전체 이름 20개가 PackageIdentity 에 남아 있었습니다.
- DeploymentHistory 30행은 모두 HResult 가 -2147009278(0x80073D02)이었습니다. 이 PC 에서는 실패 기록만 있었습니다.
- 0x80073D02 는 ERROR_PACKAGES_IN_USE 입니다. 패키지가 바꿀 리소스를 지금 쓰고 있어서 설치하지 못했다는 뜻입니다.
- 성공한 작업이 원래 이 표에 남지 않는지는 확인하지 못했습니다.
- DeploymentHistory 행의 시각은 2026-08-28 부터 09-10 사이였습니다. 같은 PC 의 AppXDeploymentServer 이벤트 로그는 09-15 부터 남아 있었습니다. 이벤트 로그에서 밀려난 기록이 이 표에는 남아 있었습니다.

### StateRepository-Deployment.srd 의 표

조사 PC 의 이 DB 에는 AppInstaller, AppInstallerUri, AppxManifest, AutoUpdatePackage, ContentGroup, ContentGroupFile, File, PackageAppInstaller, PackageSourceUri 표가 있었습니다. 칸 구성과 뜻은 이번에 보지 않았습니다. (확인 범위: 조사 PC)

### 레지스트리

`HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Appx\AppxAllUserStore` 아래에는 아래 하위 키가 있었습니다. (확인 범위: 조사 PC)

- Applications, Config, DeferredRemoval, Deleted, Deprovisioned, EndOfLife, InboxApplications, Staged, UpdatedApplications, Upgrade, UupProducts
- 사용자 SID 이름의 키들

하위 키에서 본 내용은 이렇습니다. (확인 범위: 조사 PC)

- `Applications\<패키지 전체 이름>` 키에는 `Path` 값이 있습니다. 값은 `C:\Program Files\WindowsApps\<전체 이름>\...\AppxManifest.xml` 이나 `AppxBundleManifest.xml` 경로입니다. 조사 PC 에서 126개였습니다.
- `Deprovisioned` 아래에는 패키지 계열 이름 키가 있었습니다. 예: `Microsoft.Copilot_8wekyb3d8bbwe`
- `Deprovisioned` 가 "새 사용자에게 자동으로 설치하지 않도록 뺀 앱" 을 뜻하는지는 확인하지 못했습니다.
- 사용자별 키 `HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages\<패키지 전체 이름>` 에는 `PackageRootFolder`, `DisplayName`, `PackageID`, `PackageSid`, `OSMinVersion`, `OSMaxVersionTested`, `CapabilityCount`, `SupportedUsers` 값이 있습니다. 조사 PC 에서 221개였습니다.

Microsoft 문서에는 아래 두 키가 나옵니다.

- `HKLM\Software\Microsoft\Windows\CurrentVersion\Appx\PackageRepositoryRoot` 는 패키지 저장소 위치를 담습니다. 이 키가 가리키는 폴더가 없거나 깨지면 0x80073CFE(ERROR_PACKAGE_REPOSITORY_CORRUPTED)가 납니다.
- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModel\StateChange\PackageList\<AUMID>\PackageStatus` 값이 바뀌면 앱이 흐리게 보이고 실행되지 않습니다.
- 이때 `Microsoft-Windows-TWinUI/Operational` 로그에 이벤트 5960 이 남습니다. 오류는 0x80073CFC 이고 메시지에 "package is in state: Modified" 가 들어갑니다.

### 이벤트 로그

Microsoft 는 배포 문제를 볼 때 `Microsoft-Windows-AppxPackaging/Operational` 과 `Microsoft-Windows-AppXDeploymentServer/Operational` 로그를 보라고 안내합니다. 이 가운데 AppXDeployment-Server 쪽을 먼저 보라고 합니다. PowerShell 의 `Get-AppxLog` 는 가장 최근 배포 작업의 로그를 보여 줍니다.

조사 PC 에는 아래 로그가 있었습니다. 모두 `%SystemRoot%\System32\Winevt\Logs\` 아래 .evtx 파일입니다. (확인 범위: 조사 PC)

- AppxPackaging/Operational
- AppXDeploymentServer/Operational, AppXDeploymentServer/Restricted
- AppXDeployment/Operational, AppXDeployment-Server/Operational
- AppReadiness/Admin, AppReadiness/Operational
- StateRepository/Operational
- Store/Operational

AppXDeploymentServer/Operational 에서 본 이벤트는 아래와 같습니다. (확인 범위: 조사 PC)

| ID | 메시지 | 알려 주는 것 |
|---|---|---|
| 603 | Started deployment <작업> operation on a package with main parameter <이름> | 작업을 시작했습니다 |
| 400 | Deployment <작업> operation with target volume C: on Package <전체 이름> from: (<원본 파일>) finished successfully. | 작업이 성공했습니다. Add·Stage 작업은 괄호 안에 원본 .msix 파일 이름이 경로 없이 들어갑니다 |
| 401 | Deployment <작업> operation ... failed with error 0x… | 작업이 실패했습니다 |
| 404 | AppX Deployment operation failed for package with error 0x… | 작업이 실패했습니다 |
| 607 | Deployment Remove operation on package <전체 이름> has been de-queued and is running for user SID <SID>. | 제거 작업과 대상 사용자입니다 |
| 821 | During-logon registration of package <전체 이름> for user <SID> finished with result | 로그온할 때 패키지를 등록했습니다 |
| 854 | (처리할 URI `...\AppxManifest.xml` 추가) | 처리할 매니페스트 경로입니다 |
| 855 | ... <옛 전체 이름> is updating to <새 전체 이름> | 업데이트 전 버전과 뒤 버전입니다 |
| 10002 | (Resiliency File 생성) | 제거 작업 때 `AppRepository` 에 `<GUID>_S-1-5-18_<n>.rslc` 파일을 만들었습니다 |
| 939~942 | (AppX 서비스 상태 전환) | Appxsvc 가 시작·실행·정지 사이를 오갔습니다 |

- 작업 이름으로는 Add, Register, RegisterByPackageFamilyName, RegisterByPackageFullName, Stage, DeStage, Remove, ProvisionPackageOperation, DeprovisionPackageOperation, OnDemandRegisterOperation, PreRegisterPackage 등이 보였습니다.
- 이벤트 로그는 사용자 SID 를 문자열로 적습니다. 예: `S-1-5-21-…-1001`, `S-1-5-18`
- 조사 PC 에서 AppXDeploymentServer/Operational 의 최대 크기는 5,242,880바이트였습니다.
- 가장 오래된 이벤트는 8일 전(2026-09-15)이었습니다.

이벤트 로그 파일의 구조는 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다.

### 자주 보이는 오류 코드

Microsoft 문서가 밝힌 코드입니다. 이벤트 401·404 의 오류 코드와 DeploymentHistory 의 HResult 를 읽을 때 씁니다.

| 코드 | 이름 | 뜻 |
|---|---|---|
| 0x80073CF0 | ERROR_INSTALL_OPEN_PACKAGE_FAILED | 패키지를 열지 못했습니다. 서명이 없을 때 등입니다. 자세한 내용은 AppxPackagingOM 로그에 남습니다 |
| 0x80073CF1 | ERROR_INSTALL_PACKAGE_NOT_FOUND | 그 사용자에게 설치되지 않은 패키지를 지우려 했습니다 |
| 0x80073CF3 | ERROR_INSTALL_RESOLVE_DEPENDENCY_FAILED | 업데이트·의존 패키지·충돌 검사에 실패했습니다. 의존 패키지를 찾지 못했거나 설치된 패키지와 충돌할 때 등입니다 |
| 0x80073CF9 | ERROR_INSTALL_FAILED | 설치에 실패했습니다 |
| 0x80073CFA | ERROR_REMOVE_FAILED | 제거에 실패했습니다 |
| 0x80073CFB | ERROR_PACKAGE_ALREADY_EXISTS | 같은 패키지가 이미 설치돼 있어 다시 설치하지 못했습니다. 이름이 같아도 내용이 비트 단위로 다르면 이 오류가 납니다 |
| 0x80073CFF | ERROR_INSTALL_POLICY_FAILURE | 개발자 라이선스나 사이드로드를 허용한 시스템이어야 설치할 수 있습니다 |
| 0x80073D01 | ERROR_DEPLOYMENT_BLOCKED_BY_POLICY | 정책이 배포를 막았습니다 |
| 0x80073D02 | ERROR_PACKAGES_IN_USE | 패키지가 바꿀 리소스를 지금 쓰고 있어서 설치하지 못했습니다 |
| 0x80073D06 | ERROR_INSTALL_PACKAGE_DOWNGRADE | 더 높은 버전이 이미 설치돼 있어서 설치하지 못했습니다 |

## 증거로서 의미

### 증명하는 것

- Package 표에 행이 있으면 수집 시점에 그 패키지가 이 PC 에 설치돼 있었습니다.
- PackageUser 행은 그 패키지를 어느 사용자 SID 에 등록했는지 알려 줍니다.
- PackageUser 의 InstallTime 은 그 사용자에게 패키지를 등록한 시각에 가깝습니다. (확인 범위: 조사 PC)
- IsInbox 값으로 기본 탑재 앱과 나중에 들인 앱을 나눕니다. (확인 범위: 조사 PC)
- PackageIdentity 에만 있는 이름은 그 버전 이름이 이 PC 의 저장소에 한 번은 기록됐다는 뜻입니다.
- 이벤트 400 의 Add·Stage 기록은 설치에 쓴 원본 .msix 파일 이름을 알려 줍니다. (확인 범위: 조사 PC)
- 이벤트 607·821 은 제거·등록 대상 사용자 SID 를 알려 줍니다. (확인 범위: 조사 PC)

### 증명하지 못하는 것

- 앱을 실행했는지는 알 수 없습니다. 등록은 실행이 아닙니다. 실행 흔적은 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 에서 다룹니다.
- 사용자가 스스로 설치했는지 단정하지 못합니다. IsExplicitlyInstalled·DeploymentState 숫자의 뜻을 확인하지 못했습니다.
- 앱을 어디서 받았는지 단정하지 못합니다. PackageOrigin·SignatureOrigin 숫자의 뜻을 확인하지 못했습니다.
- InstallTime 은 내려받은 시각이 아닙니다. 조사 PC 에서는 Add 완료 시각과 31분 차이가 났습니다.
- 제거한 시각은 이번에 본 표에서 찾지 못했습니다. PackageIdentity 에는 시각 칸이 없습니다. 이벤트 로그가 남아 있을 때만 이벤트 607 로 제거 작업의 시각을 봅니다.
- 앱을 완전히 제거하면 Package·PackageUser 행이 곧바로 지워지는지는 확인하지 못했습니다.
- 그 시각에 누가 PC 앞에 있었는지는 알 수 없습니다. 사람을 좁히는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

보고서에는 "StateRepository-Machine.srd 의 PackageUser 표에 따르면 이 패키지는 SID <SID> 계정에 등록돼 있고, 등록 시각 값(InstallTime)은 <UTC 시각> 이다" 처럼 씁니다. "이 시각에 앱을 내려받았다" 로 쓰지 않습니다.

## 시각 해석

| 시각 | 형식·기준 | 무엇과 가까운가 (확인 범위: 조사 PC) |
|---|---|---|
| PackageUser.InstallTime | FILETIME 정수, UTC | 그 사용자에게 등록을 마친 시각 |
| DeploymentHistory.WhenOccurred | FILETIME 정수, UTC | 배포 결과가 난 시각 |
| `AppRepository\<전체 이름>.xml` 의 수정 시각 | 파일 시스템 시각 | Add 작업을 마친 시각 |
| 이벤트 로그 TimeCreated | UTC | 작업마다 시작·완료 시각 |

- FILETIME 은 1601-01-01 UTC 부터 센 100나노초 단위의 수입니다.
- SQLite 에서는 `datetime(값/10000000-11644473600,'unixepoch')` 로 UTC 날짜를 얻습니다.
- 변환 원리는 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

조사 PC 에서 한 앱의 시각을 맞춰 보면 이렇습니다. (확인 범위: 조사 PC)

| 기록 | 시각 (UTC) |
|---|---|
| `AppRepository\<전체 이름>.xml` 수정 시각 | 01:15 |
| 이벤트 400, Add 완료 | 01:16:11 |
| PackageUser.InstallTime | 01:47:24 |
| 이벤트 400, Register 완료 | 01:47:25 |

InstallTime 은 Register 완료와 1초 차이였고 Add 완료와는 31분 차이였습니다. 그래서 InstallTime 은 내려받은 시각이 아니라 그 사용자에게 등록한 시각으로 읽습니다.

기본 탑재 앱의 시각은 OS 설치 시각과 다릅니다. (확인 범위: 조사 PC)

기본 탑재 앱의 가장 이른 InstallTime 은 2026-06-26 02:15:10 UTC 였고, 같은 PC 의 OS 설치 시각(`InstallDate`)은 2026-06-26 18:07:41 UTC 였습니다. 기본 탑재 앱의 InstallTime 이 OS 설치 시각보다 16시간 일렀습니다.


- 그러므로 기본 탑재 앱의 InstallTime 을 OS 설치 시각으로 쓰지 않습니다. OS 설치 시각은 [시스템 기본 정보](os-version-computer-name-install-date-shutdown-t.md) 에서 다룹니다.

## 함정과 한계

1. **-wal·-shm 파일을 같이 떠야 합니다.** 조사 PC 에서 `-wal` 파일은 비어 있지 않았으므로 .srd 파일만 뜨면 최근 변경이 빠집니다.
2. **서비스가 돌아가도 복사는 됐습니다.** 조사 PC 에서는 켜진 상태에서도 .srd 파일을 복사할 수 있었습니다. (확인 범위: 조사 PC)
3. **설치 시각은 Package 표가 아니라 PackageUser 표에 있습니다.** 같은 패키지에 SYSTEM 행과 사용자 행이 따로 있습니다. 어느 SID 의 행인지 늘 같이 적습니다.
4. **숫자 칸의 뜻은 확인하지 못했습니다.** DeploymentState, PackageOrigin, SignatureOrigin, PackageType, PackageUserStatus 의 Status 는 값만 적고 뜻을 단정하지 않습니다.
5. **기본 탑재 앱의 InstallTime 은 OS 설치 시각이 아닙니다.** 조사 PC 에서는 16시간 어긋났습니다.
6. **이벤트 로그는 금방 밀려납니다.** 조사 PC 에서는 8일치만 남아 있었습니다. DeploymentHistory 에는 그보다 오래된 기록이 남아 있었습니다.
7. **DeploymentHistory 에 성공 기록이 없을 수 있습니다.** 조사 PC 에서는 실패 기록만 있었습니다. 행이 없다고 설치 작업이 없었던 것은 아닙니다.
8. **HResult 는 음수로 보입니다.** 32비트 오류 코드를 부호 있는 정수로 담기 때문입니다. 16진수로 바꿔 오류 이름을 찾습니다.
9. **이름을 찾을 때 대소문자를 가리지 않습니다.** 패키지 이름은 대소문자를 구분하지 않습니다. 도구 검색에서 대소문자 구분을 끕니다.
10. **옛 버전 이름에는 시각이 없습니다.** PackageIdentity 에 남은 이름만으로 그 버전을 언제 썼는지 말할 수 없습니다.
11. **Deprovisioned 키의 뜻은 확인하지 못했습니다.** 키 이름만 보고 "사용자가 앱을 뺐다" 고 쓰지 않습니다.
12. **흐리게 보이는 앱은 PackageStatus 값을 봅니다.** 이 값이 바뀌면 앱이 실행되지 않습니다. TWinUI/Operational 이벤트 5960 과 함께 봅니다.
13. **스토어 앱 업데이트 실패는 Windows Update 이벤트에도 섞여 남습니다.** 조사 PC 에서는 System 로그의 Windows Update 클라이언트 이벤트 20 에 남았습니다. 제목은 스토어 상품 ID 로 시작했습니다. 예: `9NMPJ99VJBWV-Microsoft.YourPhone`, 오류 0x80073D02. 이 이벤트는 [윈도 업데이트 기록](windows-update-cbs-log.md) 에서 다룹니다.
14. **다른 Windows 버전은 따로 확인합니다.** 이 페이지의 표·칸은 조사 PC 한 대에서 본 것입니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 값은 명세로 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다.

**파일 첫 16바이트.** SQLite 파일은 아래 16바이트로 시작합니다. 조사 PC 의 두 .srd 파일도 이렇게 시작했습니다.

```
53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

**InstallTime 정수를 날짜로 바꾸기.** SQLite 도구가 보여 주는 InstallTime 값이 `133485408000000000` 이라고 해 봅니다.

1. 10,000,000 으로 나누면 13,348,540,800 입니다. 1601-01-01 부터 센 초입니다.
2. 11,644,473,600 을 빼면 1,704,067,200 입니다. 1970-01-01 부터 센 초입니다.
3. 날짜로 바꾸면 2024-01-01 00:00:00 UTC 입니다.

SQLite 가 정수를 파일에 어떻게 적는지는 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

**HResult 음수를 오류 코드로 바꾸기.** DeploymentHistory 의 HResult 가 `-2147009278` 이라고 해 봅니다.

1. 음수이므로 2^32(4,294,967,296)을 더합니다.
2. 결과는 2,147,958,018 입니다.
3. 16진수로 바꾸면 `0x80073D02` 입니다.
4. 위 오류 코드 표에서 ERROR_PACKAGES_IN_USE 를 찾습니다.

### 공개 도구로 한 번

1. `AppRepository` 폴더에서 두 .srd 파일과 각각의 `-wal`, `-shm` 파일을 같은 폴더로 사본을 뜹니다. 파일 이름은 바꾸지 않습니다.
2. sqlite3 명령줄 도구나 DB Browser for SQLite 같은 공개 SQLite 도구로 사본을 엽니다. WAL 을 다룰 때 주의할 점은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.
3. 사용자별 등록 시각을 뽑습니다.

```sql
SELECT p.PackageFullName,
       p.IsInbox,
       pu.User,
       pu.IsExplicitlyInstalled,
       datetime(pu.InstallTime/10000000-11644473600,'unixepoch') AS install_utc
FROM PackageUser AS pu
JOIN Package AS p ON p._PackageID = pu.Package
ORDER BY pu.InstallTime;
```

4. `pu.User` 값으로 User 표의 행을 찾아 `UserSid` 를 읽습니다. 이진 SID 를 문자열로 바꾸는 방법은 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에서 다룹니다. SID 와 계정 이름은 [사용자 프로필 목록](profilelist.md) 으로 잇습니다.
5. 지금은 설치돼 있지 않은 옛 버전 이름을 뽑습니다.

```sql
SELECT PackageFullName
FROM PackageIdentity
WHERE PackageFullName NOT IN (SELECT PackageFullName FROM Package);
```

6. 배포 결과 기록을 16진 오류 코드로 뽑습니다.

```sql
SELECT PackageIdentity,
       User,
       printf('0x%08X', HResult & 0xFFFFFFFF) AS hresult,
       datetime(WhenOccurred/10000000-11644473600,'unixepoch') AS when_utc
FROM DeploymentHistory
ORDER BY WhenOccurred;
```

7. 이벤트 뷰어나 공개 EVTX 파서로 AppXDeploymentServer/Operational 을 엽니다. 이벤트 603·400·401·607·821·855 를 골라 봅니다. 라이브 시스템에서는 `Get-AppxLog` 로 가장 최근 배포 작업을 봅니다.
8. 한 패키지를 골라 3번의 등록 시각과 이벤트 400 Register 완료 시각을 맞춰 봅니다.
9. 레지스트리 뷰어로 SOFTWARE 하이브의 `AppxAllUserStore` 와 사용자 UsrClass.dat 의 `Repository\Packages` 를 엽니다. DB 의 패키지 목록과 비교합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 설치 프로그램 | 스토어 앱이 아닌 일반 설치 프로그램 목록을 나란히 봅니다 | [설치 프로그램](uninstall.md) |
| AmCache | InventoryApplication 에서 `Source` 가 `AppxPackage` 인 항목을 StateRepository 목록과 맞춰 봅니다 | [AmCache](../execution/amcache-hve/index.md) |
| UWP 앱 데이터 | `%LOCALAPPDATA%\Packages` 안의 앱 설정과 데이터를 봅니다 | [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) |
| 사용자 프로필 목록 | PackageUser 의 SID 를 계정 이름과 프로필 폴더로 잇습니다 | [사용자 프로필 목록](profilelist.md) |
| 사용자 계정 | RID 1000·1001 같은 로컬 계정을 확인합니다 | [사용자 계정](sam.md) |
| 시스템 기본 정보 | OS 설치 시각을 기본 탑재 앱 시각과 나눠 봅니다 | [시스템 기본 정보](os-version-computer-name-install-date-shutdown-t.md) |
| 윈도 업데이트 기록 | 스토어 앱 업데이트 실패가 Windows Update 이벤트 20 에도 남았는지 봅니다 | [윈도 업데이트 기록](windows-update-cbs-log.md) |
| 실행 흔적 | 등록한 앱을 실제로 실행했는지 봅니다 | [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) |
| 섀도 복사본 | 이전 시점의 .srd 에 지금은 없는 패키지가 있는지 봅니다 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

여러 기록의 시각을 한 줄로 세우는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

## 실습

Windows 공개 검체(NIST CFReDS 등)에서 `AppRepository` 폴더와 AppX 이벤트 로그를 꺼내 아래 질문을 풀어 봅니다.

1. 검체에 `StateRepository-Machine.srd` 가 있습니까? `-wal` 파일도 함께 있습니까?
2. Package 표의 행 수와 `AppRepository` 폴더의 `.xml` 파일 수가 같습니까?
3. IsInbox=0 패키지 가운데 로컬 사용자 SID 에 등록된 패키지는 무엇입니까?
4. 그 패키지의 InstallTime 을 직접 날짜로 바꿔 봅니다. 도구가 보여 주는 값과 같습니까?
5. 같은 패키지의 이벤트 400 Register 완료 시각과 InstallTime 은 몇 초 차이 납니까? Add 완료와는 얼마나 차이 납니까?
6. PackageIdentity 에만 남은 옛 버전 이름은 몇 개입니까?
7. DeploymentHistory 의 HResult 를 16진수로 바꾸면 어떤 오류입니까?
8. AppXDeploymentServer/Operational 의 가장 오래된 이벤트와 DeploymentHistory 의 가장 오래된 행 가운데 어느 쪽이 더 오래됐습니까?

## 참고 문헌

1. Microsoft Learn, *Troubleshooting packaging, deployment, and query of Windows apps* (배포 이벤트 로그와 `Get-AppxLog`, 오류 코드, `PackageRepositoryRoot`, `PackageStatus` 와 이벤트 5960). https://learn.microsoft.com/en-us/windows/win32/appxpkg/troubleshooting
2. Microsoft Learn, *An overview of Package Identity in Windows apps* (패키지 신원 다섯 부분, 전체 이름·계열 이름 형식, PublisherId, 대소문자 규칙, MSIX 와 APPX, AUMID). https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/package-identity-overview
