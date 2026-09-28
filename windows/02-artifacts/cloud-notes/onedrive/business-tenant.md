---
title: "회사용 OneDrive와 SharePoint 동기화"
parent: "원드라이브"
grand_parent: "아티팩트 · 클라우드·노트"
nav_order: 2210
---

# 회사용 OneDrive와 SharePoint 동기화 (Business Tenant)

회사·학교 계정으로 OneDrive 를 연결하면 레지스트리·`settings`·`logs` 에 `Business1`, `Business2` … 라는 이름으로 기록이 따로 쌓입니다. 이 기록에는 조직을 가리키는 테넌트 ID 와 SharePoint 주소가 남습니다. 관리자 정책의 값 이름에도 테넌트 ID 가 자주 들어갑니다. 그래서 어느 조직의 계정을 썼는지, 정책이 어느 조직을 대상으로 걸렸는지 구분할 수 있습니다.

> 이 페이지의 레지스트리·로그 값은 Windows 11 빌드 26200 과 OneDrive 26.168.0830.0006 기준입니다.

## 무엇을 기록하나 · 왜 생기나

Microsoft 365 를 쓰는 조직 하나를 테넌트 (Tenant) 라고 부르고, 조직마다 GUID 모양의 테넌트 ID 가 있습니다. 회사·학교 계정의 OneDrive 는 SharePoint 쪽 주소를 쓰며, 계정 키에는 `-my.sharepoint.com` 주소가 남습니다.

SharePoint 사이트와 Teams 의 문서 라이브러리도 PC 로 동기화할 수 있는데, 이 기능은 Microsoft 365 회사·학교 구독이나 SharePoint Server 2019 가 있어야 합니다. 관리자는 그룹 정책으로 어느 조직 계정을 허용할지, 동기화 폴더를 어디에 둘지, 어느 라이브러리를 자동으로 받을지 정할 수 있고, 이런 정책 값에 테넌트 ID 가 들어갑니다.

예전 회사용 동기화 앱은 `Groove.exe`, 새 동기화 앱은 `OneDrive.exe` 이며, 같은 계정이면 새 앱이 예전 앱의 동기화를 넘겨받으려 합니다.

자동 로그인 정책 `SilentAccountConfig` 를 켜면 Microsoft Entra ID 에 가입한 PC 에서 Windows 로그인 계정으로 OneDrive 를 자동 연결하지만, 다단계 인증이 필요한 사용자에게는 동작하지 않습니다. 자동 연결에 성공하면 남는 값은 [계정·설정 레지스트리](accounts-settings.md) 에서 다룹니다.

## 위치와 버전별 차이

| 기록 | 회사 계정의 자리 |
|---|---|
| 레지스트리 계정 키 | `HKCU\Software\Microsoft\OneDrive\Accounts\Business1`, `Business2` … |
| 설정·DB 폴더 | `%LOCALAPPDATA%\Microsoft\OneDrive\settings\Business<1-9>` |
| 로그 폴더 | `logs\Business1`, `logs\ListSync\Business1` |
| 회사 OneDrive 동기화 폴더 | 기본 이름이 `OneDrive - {organization name}` 입니다 |
| SharePoint·Teams 라이브러리 | 조직 이름으로 된 폴더 아래로 받습니다. 예: `%userprofile%\Contoso` |

옛 PC 에는 `Groove.exe` 로 동기화한 흔적이 있을 수 있습니다. 팀 사이트 라이브러리를 동기화했을 때의 레지스트리·DB 값(`LibraryType` 등)과 조직 이름 폴더 아래 하위 폴더의 이름 형식은 실제 기기에서 확인해야 합니다.

## 구조

### 계정 키에서 조직을 가리키는 값

`HKCU\Software\Microsoft\OneDrive\Accounts\Business1` 키의 값입니다. 개인·회사 계정에 모두 있는 값은 [계정·설정 레지스트리](accounts-settings.md) 에서 다룹니다.

| 값 | 형식 | 내용 |
|---|---|---|
| `Business` | DWORD | 1. 회사 계정 키에만 있습니다 |
| `ConfiguredTenantId` | REG_SZ | 테넌트 ID (GUID) |
| `cid` | REG_SZ | 계정 ID. 회사 계정도 GUID 모양이지만 테넌트 ID 와는 다른 값입니다 |
| `DisplayName` | REG_SZ | 표시 이름 |
| `UserName` | REG_SZ | 사용자 이름. `UserEmail` 과 값이 다를 수 있습니다 |
| `PUID` | REG_SZ | 계정 식별 값 |
| `SPOResourceId` | REG_SZ | `https://<테넌트>-my.sharepoint.com/` 모양 |
| `TeamSiteSPOResourceId` | REG_SZ | `https://<테넌트>.sharepoint.com/` 모양 |
| `ServiceEndpointUri` | REG_SZ | `https://<테넌트>-my.sharepoint.com/personal/<사용자>/_api` 모양 |
| `EdpManaged` | DWORD | 뜻은 단정하지 않고 값만 옮깁니다 |
| `GrooveTakeoverAttemptedOperations`, `GrooveTakeoverSuccessfulOperations` | DWORD | 예전 동기화 앱(`Groove.exe`)의 동기화를 넘겨받은 흔적으로 보입니다 |

### 동기화 루트 등록의 회사 계정 값

- `HKCU\Software\SyncEngines\Providers\OneDrive\<범위 ID>` 의 `UrlNamespace` 는 `https://<테넌트>-my.sharepoint.com/personal/<사용자>/Documents/` 모양입니다. 회사 계정의 개인 문서 라이브러리입니다.
- `SyncRootManager` 의 `OneDrive!…` 키 가운데 회사 계정 키에만 `TenantName` 값이 있습니다.
- 두 키의 나머지 값과 이어 읽는 법은 [계정·설정 레지스트리](accounts-settings.md) 에 있습니다.

### 동기화 폴더 이름과 위치

**회사 OneDrive 폴더**

기본 이름은 `OneDrive - {organization name}` 입니다. 관리자는 정책으로 이 이름을 바꿀 수 있는데, 키는 `HKLM\SOFTWARE\Policies\Microsoft\OneDrive\CustomSyncRootFolderName` 이고 값 이름이 테넌트 ID, 데이터가 새 폴더 이름입니다. 이미 동기화 중인 사용자는 연결을 끊었다가 다시 연결해야 새 이름이 적용됩니다. 새 이름은 `OneDrive` 일 수 없고, 전체 경로(예: `C:\Users\{alias}\OneDrive - {organization name}`)는 120자를 넘을 수 없습니다.

기본 위치는 `HKCU\SOFTWARE\Policies\Microsoft\OneDrive\DefaultRootDir` 로 정하며, 값 이름이 테넌트 ID, 데이터가 경로입니다. 이 정책을 끄면 기본 위치는 `%userprofile%` 입니다. `HKCU\Software\Policies\Microsoft\OneDrive\DisableCustomRoot` 에 테넌트 ID 이름으로 1 을 넣으면 사용자가 위치를 바꾸지 못합니다.

**SharePoint·Teams 라이브러리**

| 사용자 동작 | 파일이 보이는 곳 |
|---|---|
| 라이브러리에서 "동기화" 버튼을 누름 | 조직 이름 폴더 아래. 예: `%userprofile%\Contoso` |
| "내 파일에 바로 가기 추가" | OneDrive 폴더 안. 사용자의 모든 기기에서 보입니다 |

- 동기화를 멈춰도 이미 내려받은 사본은 PC 에 남습니다.

### DB 에서 라이브러리 가르기

회사 계정의 [동기화 DB](syncenginedatabase-db.md) 에는 라이브러리를 구분할 열이 있습니다. 팀 사이트 라이브러리 행에 실제로 어떤 값이 들어가는지는 실제 데이터로 확인합니다.

| 표 | 열 | 쓰임 |
|---|---|---|
| `od_ScopeInfo_Records` | `siteID`, `webID`, `listID`, `webURL`, `tenantID`, `remotePath`, `libraryType` | 동기화 중인 SharePoint 라이브러리를 가릅니다 |
| `od_ClientFolder_Records` | `teamsChannelFolder`, `shortcutsFolder` | Teams 채널 폴더와 바로 가기 폴더 표시로 보입니다. 값의 뜻은 실제 데이터로 확인합니다 |
| `od_GraphMetadata_Records` | `createdBy`, `modifiedBy` | 만든 사람과 고친 사람을 적는 열로 보입니다. 실제 값은 실제 데이터로 확인합니다 |

### 조직에 관한 정책

모두 그룹 정책이 쓰는 레지스트리 값입니다. `1111-2222-3333-4444` 는 Microsoft 문서가 테넌트 ID 자리에 쓴 예시 값입니다.

| 정책 | 키와 값 | 뜻 |
|---|---|---|
| 특정 조직만 허용 | `HKLM\SOFTWARE\Policies\Microsoft\OneDrive\AllowTenantList` 에 값 이름 `1111-2222-3333-4444` | 허용하지 않은 조직 계정을 추가하면 오류가 납니다. 이미 추가된 계정은 동기화가 멈춥니다. `BlockTenantList` 보다 우선합니다 |
| 특정 조직 차단 | `HKLM\SOFTWARE\Policies\Microsoft\OneDrive\BlockTenantList` 에 값 이름 `1111-2222-3333-4444` | 그 조직 계정을 막습니다 |
| 다른 조직 공유 동기화 차단 | `HKLM\SOFTWARE\Policies\Microsoft\OneDrive` `BlockExternalSync` = 1 | 다른 조직이 공유한 라이브러리·폴더를 동기화(B2B Sync)하지 못하게 합니다 |
| 팀 사이트 라이브러리 자동 동기화 | `HKCU\Software\Policies\Microsoft\OneDrive\TenantAutoMount` `"LibraryName"="LibraryID"` | 지정한 라이브러리를 자동으로 동기화합니다 |
| 자동 로그인 | `HKLM\SOFTWARE\Policies\Microsoft\OneDrive` `SilentAccountConfig` = 1 | Windows 로그인 계정으로 OneDrive 를 자동 연결합니다 |
| 알려진 폴더 자동 이동 | `HKLM\SOFTWARE\Policies\Microsoft\OneDrive` `KFMSilentOptIn` = `"<테넌트 ID>"` | 폴더를 그 조직의 OneDrive 로 옮깁니다. 폴더 선택은 `KFMSilentOptInDesktop`·`KFMSilentOptInDocuments`·`KFMSilentOptInPictures`(1), 알림은 `KFMSilentOptInWithNotification` 입니다 |
| 알려진 폴더 이동 금지 | `HKLM\SOFTWARE\Policies\Microsoft\OneDrive` `KFMBlockOptIn` = 1 | 알려진 폴더를 OneDrive 로 옮기지 못하게 합니다("Manage backup" 비활성). 값이 2 이면 이미 옮긴 폴더를 PC 로 되돌리고 나서 막습니다 |
| 알려진 폴더 되돌리기 금지 | `HKLM\SOFTWARE\Policies\Microsoft\OneDrive` `KFMBlockOptOut` = 1 | 문서·사진·바탕 화면을 OneDrive 에 묶어 두고 "Stop protecting" 을 막습니다 |
| 자동 내려받기 크기 한도 | `HKLM\SOFTWARE\Policies\Microsoft\OneDrive\DiskSpaceCheckThresholdMB` 에 테넌트 ID 이름의 DWORD | 조직별로 자동 내려받기 크기 한도를 정합니다 |

`TenantAutoMount` 의 라이브러리 ID 는 `tenantId=xxx&siteId=xxx&webId=xxx&listId=xxx&webUrl=httpsxxx&version=1` 모양이고, SharePoint 에서 복사한 문자열은 `%2D`·`%7B`·`%7D`·`%3A`·`%2F`·`%2E` 를 풀어서 넣어야 합니다. 이 정책으로 받은 라이브러리는 다음 로그인 때 온라인 전용 파일로 동기화되며, 사용자는 이 라이브러리의 동기화를 멈출 수 없습니다.

다른 조직의 OneDrive 로 이미 옮긴 알려진 폴더를 새 조직으로 옮기면 새 빈 폴더가 생깁니다. 사용자에게는 빈 바탕 화면이 보입니다. 이런 PC 에서는 옛 조직 쪽 폴더도 함께 찾습니다.

### 로그

- 회사 계정 로그는 `logs\Business1` 에 따로 쌓입니다. 형식과 읽는 법은 [로그 (ODL·ODLGZ)](odl-odlgz.md) 에서 다룹니다.
- 목록 동기화 (ListSync) 로그인 `Nucleus-….odlgz` 는 `logs\ListSync\Business1` 에 있습니다.
- `logs\Common` 의 `FileCoAuth-….odl` 은 이름으로 보면 오피스 파일 공동 작성 (co-authoring) 쪽 로그로 보입니다.

## 증거로서 의미

### 증명하는 것

- `Accounts\BusinessN` 키와 `Business` = 1 이 있으면, 이 Windows 사용자 프로필에서 회사·학교 계정을 연결한 적이 있습니다.
- `ConfiguredTenantId`, `SPOResourceId`, `ServiceEndpointUri` 로 어느 조직의 계정인지 가릴 수 있습니다.
- `SyncRootManager` 의 `TenantName` 으로 조직 이름을 볼 수 있습니다.
- 정책 키의 값 이름에 테넌트 ID 가 있으면, 그 조직 계정이 관리 대상이었던 것으로 보입니다.
- `od_ScopeInfo_Records` 의 `siteID`·`webURL` 로 동기화하던 SharePoint 라이브러리를 가릴 수 있습니다.
- `AllowTenantList`·`BlockExternalSync` 가 있으면 관리자가 다른 조직 계정이나 다른 조직이 공유한 폴더의 동기화를 막는 정책을 건 적이 있습니다.

### 증명하지 못하는 것

- 회사 계정을 연결했다는 것만으로 업무 목적이었는지 개인 목적이었는지는 알 수 없습니다.
- 라이브러리 폴더에 파일이 있다고 지금도 동기화 중이라는 뜻은 아닙니다. 동기화를 멈춰도 사본은 남습니다.
- `TenantAutoMount` 로 받은 라이브러리의 파일은 온라인 전용일 수 있습니다. 목록에 있다고 내용이 PC 에 있었다는 뜻은 아닙니다.
- 누가 파일을 만들고 고쳤는지는 `createdBy`·`modifiedBy` 열의 실제 값을 확인하기 전에는 단정하지 않습니다.
- 정책 값이 있다고 지금도 그 정책이 걸려 있다는 뜻은 아닙니다. 이유는 [계정·설정 레지스트리](accounts-settings.md) 의 정책 절에 있습니다.

보고서에는 "회사 자료를 동기화했다" 대신 이렇게 씁니다. "사용자 A 의 `Accounts\Business1` 에 테넌트 ID X 가 있고, 동기화 DB 의 `od_ScopeInfo_Records` 에 `webURL` 이 Y 인 라이브러리 행이 있다."

## 시각 해석

회사 계정 키와 DB 의 시각 형식은 개인 계정과 같습니다. [계정·설정 레지스트리](accounts-settings.md) 와 [동기화 DB](syncenginedatabase-db.md) 의 "시각 해석" 을 따릅니다.

## 함정과 한계

- **GUID 두 개를 섞지 않습니다.** `cid` 와 `ConfiguredTenantId` 는 둘 다 GUID 모양이지만 다른 값입니다. 설정 ini 파일 이름은 `cid` 쪽입니다.
- **`UserName` 과 `UserEmail` 이 다를 수 있습니다.** 보고서에는 어느 값을 썼는지 밝힙니다.
- **라이브러리 폴더는 OneDrive 폴더 밖에 있을 수 있습니다.** "동기화" 버튼으로 받은 라이브러리는 조직 이름 폴더 아래로 갑니다. OneDrive 폴더만 뒤지면 놓칩니다.
- **OneDrive 폴더 안의 파일이 사용자 것만은 아닙니다.** "내 파일에 바로 가기 추가" 로 넣은 공유 라이브러리도 OneDrive 폴더 안에 보입니다.
- **문서의 예시 값을 실제 값으로 읽지 않습니다.** `1111-2222-3333-4444` 와 `Contoso` 는 Microsoft 문서의 예시입니다.
- **팀 사이트 라이브러리의 `LibraryType` 등은 실제 데이터에서 직접 봅니다.**
- **알려진 폴더를 다른 조직으로 옮긴 PC 는 바탕 화면이 비어 보일 수 있습니다.** 옛 조직 폴더를 함께 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

`TenantAutoMount` 라이브러리 ID 처럼 퍼센트 인코딩 (percent-encoding) 된 문자열은 `%` 뒤 두 글자를 16진 바이트로 읽어 풉니다. 아래는 규칙으로 만든 예시입니다. 특정 조직의 값이 아닙니다.

```
%2D → 0x2D → -
%7B → 0x7B → {
%7D → 0x7D → }
%3A → 0x3A → :
%2F → 0x2F → /
%2E → 0x2E → .

1111%2D2222%2D3333%2D4444                    → 1111-2222-3333-4444
https%3A%2F%2F<테넌트>%2Esharepoint%2Ecom%2F  → https://<테넌트>.sharepoint.com/
```

푼 `tenantId` 를 계정 키의 `ConfiguredTenantId` 와 맞춰 봅니다. 같으면 자동 동기화 대상 라이브러리가 사용자가 연결한 조직의 것입니다.

### 공개 도구로 한 번

1. 사용자 `NTUSER.DAT` 와 `SOFTWARE` 하이브를 사본으로 뜹니다.
2. `Software\Microsoft\OneDrive\Accounts\Business*` 키에서 `ConfiguredTenantId`, `SPOResourceId`, `ServiceEndpointUri` 를 모읍니다.
3. `SOFTWARE` 하이브의 `SyncRootManager` 에서 `TenantName` 이 있는 `OneDrive!…` 키를 찾습니다.
4. 두 하이브의 `Policies\Microsoft\OneDrive` 아래에서 테넌트 ID 가 들어간 값 이름을 모읍니다.
5. `settings\Business1\SyncEngineDatabase.db` 사본을 `-wal`·`-shm` 과 함께 SQLite 명령줄 도구로 엽니다.

```sql
SELECT scopeID, scopeType, libraryType, tenantID,
       siteID, webID, listID, webURL, remotePath, lastKnownFolderPath
FROM od_ScopeInfo_Records;
```

`tenantID` 가 계정 키의 `ConfiguredTenantId` 와 다른 행이 있으면, 다른 조직이 공유한 라이브러리인지 따져 봅니다. 공개 도구 OneDriveExplorer 도 `settings\Business<1-9>` 폴더의 DB 를 읽습니다[5]. 도구 결과는 위 조회 결과와 한 번 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 계정·설정 레지스트리 | 개인·회사 계정에 모두 있는 값과 자동 연결 성공 표시를 봅니다 | [계정·설정 레지스트리](accounts-settings.md) |
| 동기화 DB | 라이브러리별 파일 목록과 해시를 봅니다 | [동기화 DB](syncenginedatabase-db.md) |
| 로그 | 회사 계정 로그와 목록 동기화 로그를 봅니다 | [로그 (ODL·ODLGZ)](odl-odlgz.md) |
| 마이크로소프트 팀즈 | Teams 채널 라이브러리를 쓴 흔적을 봅니다 | [마이크로소프트 팀즈](../../messengers/teams.md) |
| 오피스 사용 흔적 | 조직 라이브러리 경로의 문서를 연 기록을 봅니다 | [오피스 사용 흔적](../../file-folder-usage/microsoft-office/index.md) |
| 바로가기 파일 | `%userprofile%\<조직 이름>` 아래 파일을 연 기록을 봅니다 | [바로가기 파일](../../file-folder-usage/lnk.md) |
| 사용자 프로필 목록 | `SyncRootManager` 키의 SID 가 누구인지 봅니다 | [사용자 프로필 목록](../../system-account/profilelist.md) |

회사 자료를 개인 계정이나 다른 조직으로 옮겼는지 살피는 흐름은 [자료를 밖으로 빼돌렸나](../../../04-scenarios/exfiltration/data-exfiltration/index.md) 에 있습니다.

## 실습

회사 계정으로 OneDrive 를 쓴 공개 시험 데이터(NIST CFReDS 등)가 있으면 아래 질문을 풀어 봅니다.

1. `Accounts` 아래에 `Business` 로 시작하는 키가 몇 개입니까? 각 키의 `ConfiguredTenantId` 는 서로 같습니까?
2. `cid` 와 `ConfiguredTenantId` 는 어떻게 다릅니까? `settings\Business1` 의 ini 파일 이름은 어느 쪽과 같습니까?
3. `SPOResourceId` 와 `TeamSiteSPOResourceId` 의 주소에서 테넌트 이름 부분은 무엇입니까?
4. `%userprofile%` 바로 아래에 조직 이름으로 된 폴더가 있습니까? 그 폴더 아래 파일은 동기화 DB 의 어느 범위 행과 이어집니까?
5. `od_ScopeInfo_Records` 에서 `tenantID` 가 계정 키와 다른 행이 있습니까?
6. 정책 키에 테넌트 ID 가 들어간 값이 있습니까? 있다면 어느 정책입니까?

## 참고 문헌

1. Microsoft Learn, "Use OneDrive policies to control sync settings" (2026-09 갱신) — https://learn.microsoft.com/en-us/sharepoint/use-group-policy
2. Microsoft Learn, "Silently configure user accounts" — https://learn.microsoft.com/en-us/sharepoint/use-silent-account-configuration
3. Microsoft Learn, "Redirect and move Windows known folders to OneDrive" — https://learn.microsoft.com/en-us/sharepoint/redirect-known-folders
4. Microsoft Support, "Sync SharePoint and Teams files with your computer" — https://support.microsoft.com/en-us/office/sync-sharepoint-and-teams-files-with-your-computer-6de9ede8-5b6e-4503-80b2-6190f3354a88
5. Beercow/OneDriveExplorer, README — https://github.com/Beercow/OneDriveExplorer
