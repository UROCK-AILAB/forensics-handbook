---
title: "동기화 DB"
parent: "원드라이브"
grand_parent: "아티팩트 · 클라우드·노트"
nav_order: 2190
---

# 동기화 DB (SyncEngineDatabase.db)

## 한 줄 요약

`SyncEngineDatabase.db` 는 OneDrive 동기화 엔진이 계정마다 두는 SQLite 파일입니다. 동기화하는 파일과 폴더가 한 행씩 들어 있고, 이름·크기·수정 시각·해시가 함께 남습니다. 이 DB 로 동기화 폴더의 파일 목록을 다시 만들고, 해시로 다른 곳에서 찾은 파일과 맞춰 봅니다.

> 아래 표·열 이름과 값은 Windows 11 빌드 26200, OneDrive 26.168.0830.0006 에 개인 계정 1개와 회사 계정 1개를 연결한 PC 기준입니다. 표와 열 이름은 앱 버전에 따라 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

동기화 엔진은 이 DB 에 동기화 범위 안의 파일과 폴더 목록을 적습니다. 파일 한 개가 `od_ClientFile_Records` 의 한 행이고 폴더 한 개가 `od_ClientFolder_Records` 의 한 행이며, 파일 행에는 이름, 크기, 로컬 수정 시각, 서버 쪽 수정 시각, 내용 해시가 있습니다. 이 밖에 파일을 내려받은 기록, 서비스와 주고받은 작업 기록 같은 활동 기록 성격의 표도 있습니다.

같은 폴더의 `SafeDelete.db` 에는 지운 파일에 관한 기록이 남습니다.

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 위치 | `%LOCALAPPDATA%\Microsoft\OneDrive\settings\<Personal 또는 BusinessN>\SyncEngineDatabase.db` |
| 옆 파일 | `SyncEngineDatabase.db-wal`, `SyncEngineDatabase.db-shm` |
| 형식 | 암호화하지 않은 SQLite 입니다. 파일이 `SQLite format 3` 으로 시작하고, `journal_mode` 는 `wal` 입니다 |
| 크기 | 예: 개인 계정 약 8.4MB(파일 9,925행·폴더 1,226행), 회사 계정 약 4.9MB(파일 4,551행·폴더 401행) |

옛 OneDrive 는 같은 정보를 `<UserCid>.dat` 와 `<UserCid>.dat.previous` 에 저장했고 새 버전은 SQLite 로 바꿨습니다. 어느 앱 버전에서 바뀌었는지는 알려져 있지 않으므로, 옛 PC 에서 `.db` 가 없으면 `.dat` 파일을 찾습니다.

계정마다 폴더가 따로 있어서 DB 도 계정마다 하나씩 있습니다. 계정 폴더와 레지스트리 계정 키의 관계는 [계정·설정 레지스트리](accounts-settings.md) 에서 다룹니다.

## 구조

SQLite 파일과 WAL 을 읽는 법은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다. 아래 표와 열의 설명은 따로 근거를 적은 것 말고는 이름에서 미루어 본 뜻입니다.

### 표 목록

개인 계정과 회사 계정 DB 의 표 목록은 같습니다.

| 표 | 내용 |
|---|---|
| `od_ClientFile_Records` | 파일 한 개당 한 행 |
| `od_ClientFolder_Records` | 폴더 한 개당 한 행 |
| `od_ScopeInfo_Records` | 동기화 범위. 라이브러리 단위 |
| `od_HydrationData` | 파일을 내려받은 기록으로 보이는 표 |
| `od_ServiceOperationHistory` | 서비스와 주고받은 작업 기록 |
| `od_GraphMetadata_Records`, `od_GraphMetadata_LastWrite` | 서비스 쪽 메타데이터 |
| `od_ArchiveData_Records` | 보관 관련 기록 |
| `od_SelectiveSync_Records`, `od_IgnoredItem_Records`, `od_ClientPolicy_Records` | 선택 동기화, 무시한 항목, 정책 |
| `od_ClientFilePostponedChange_Records`, `od_ClientFolderPostponedChange_Records`, `od_MigrateItemPostponedChange_Records` | 미뤄 둔 변경 |
| `od_CreateAddedFolderFailures`, `od_ThrottleHistory` | 폴더 생성 실패, 속도 제한 기록 |
| `odc_Convergence_ScopeInfo_Records`, `odc_convergence_items` | 공개된 설명 없음 |
| `__oddbm_schema` | 열이 `name`, `value` 두 개인 스키마 정보 표 |

### od_ClientFile_Records

| 열 | 내용 |
|---|---|
| `resourceID`, `parentResourceID` | 이 파일의 ID 와 부모 폴더 ID |
| `eTag` | 서버 쪽 버전 표시 |
| `fileName` | 파일 이름. 폴더 경로는 들어 있지 않습니다 |
| `volumeID`, `itemIndex` | 로컬 볼륨과 항목 번호 |
| `size`, `serverSize` | 로컬 크기, 서버 쪽 크기 |
| `lastChange` | 로컬 파일의 수정 시각. Unix 초(UTC)입니다 |
| `serverLastChange` | 서버 쪽 수정 시각으로 보입니다. 값은 Unix 초 범위입니다 |
| `diskCreationTime`, `diskLastAccessTime` | 값은 Unix 초 범위입니다. 뜻은 아래 "시각 해석" 에서 다룹니다 |
| `fileStatus`, `lastKnownPinState` | 파일 상태 값. 뜻은 공개된 설명이 없습니다 |
| `locallyDeleted`, `serverDeleted` | 로컬·서버 쪽 삭제 표시로 보입니다 |
| `sharedItem` | 공유 항목 표시 |
| `localHashDigest`, `localHashAlgorithm` | 로컬 내용 해시(BLOB)와 해시 종류 번호 |
| `serverHashDigest`, `serverHashAlgorithm` | 서버 쪽 해시(BLOB)와 해시 종류 번호 |
| `mediaDateTaken`, `mediaWidth`, `mediaHeight`, `mediaDuration` | 사진·영상 정보 |
| `spoPermissions`, `checkedOutState`, `irmEnabled`, `irmEncrypted` 등 `irm*`, `local…CLP…`·`server…CLP…` | 권한·보호 관련 열. 민감도 레이블 쪽으로 보이지만 공개된 설명은 없습니다 |

값의 예는 이렇습니다.

- `fileStatus` 는 2 와 8 두 값, `lastKnownPinState` 는 NULL 과 0 만 들어 있습니다. 각 값이 자리표시자를 뜻하는지 등은 공개된 설명이 없습니다.
- 개인 계정 DB 에서 `locallyDeleted` 와 `serverDeleted` 는 모두 NULL 입니다.
- 해시가 비어 있는 행이 개인·회사 계정에 각각 9행 있습니다.

**해시.** `localHashAlgorithm` 은 5 이고, `localHashDigest` 는 20바이트입니다. 내용이 PC 에 있는 파일 60개로 해시를 계산해 맞추면 결과는 이렇습니다.

| 비교 | 개인 계정 | 회사 계정 |
|---|---|---|
| QuickXorHash 와 같음 | 60/60 | 59/60 |
| SHA-1 과 같음 | 0/60 | 0/60 |

따라서 5 는 QuickXorHash 이고, DB 는 해시를 원시 바이트로 저장합니다.

Microsoft Graph 에서 `quickXorHash` 는 회사·학교용과 개인용 OneDrive 모두에 반드시 있는 유일한 해시입니다. Graph 는 `quickXorHash` 를 base64 문자열로 주고, `sha1Hash`·`crc32Hash` 는 16진 문자열로 줍니다. 따라서 DB 의 `localHashDigest` 를 base64 로 바꾸면 Graph 나 웹에서 받은 `quickXorHash` 와 맞춰 볼 수 있습니다.

### od_ClientFolder_Records

열은 `resourceID`, `parentResourceID`, `parentScopeID`, `eTag`, `folderName`, `volumeID`, `itemIndex`, `folderStatus`, `locallyDeleted`, `serverDeleted`, `sharedItem`, `teamsChannelFolder`, `shortcutsFolder`, `folderColor` 등입니다.

파일의 전체 경로는 어느 열에도 통째로 들어 있지 않습니다. 파일 행의 `parentResourceID` 로 폴더 행의 `resourceID` 를 찾고, 그 폴더의 `parentResourceID` 로 다시 위 폴더를 찾으며 맨 위까지 올라가 `folderName` 을 이어 붙입니다.

> 그림 자리: 파일 행 하나에서 `parentResourceID` → 폴더 행 `resourceID` 를 따라 맨 위 폴더까지 올라가며 경로를 이어 붙이는 과정을 화살표로 보여 주는 그림

### od_ScopeInfo_Records

동기화 범위, 즉 라이브러리 하나가 한 행입니다. 열은 `scopeID`, `scopeType`, `libraryType`, `cid`, `siteID`, `webID`, `listID`, `webURL`, `tenantID`, `remotePath`, `lastKnownFolderPath`, `selectiveSyncEnabled`, `syncTokenData` 등입니다.

두 계정 DB 모두 `scopeType` 3, `libraryType` 2 인 행이 있고, 개인 계정 DB 에만 `scopeType` 7, `libraryType` 3 인 행이 하나 더 있습니다. 이 행이 무엇을 가리키는지는 공개된 설명이 없습니다. SharePoint 라이브러리를 구분하는 데 이 표를 쓰는 법은 [회사용 OneDrive와 SharePoint 동기화](business-tenant.md) 에서 다룹니다.

### 활동 기록 성격의 표

| 표 | 열 | 값 |
|---|---|---|
| `od_HydrationData` | `resourceID`, `firstHydrationTime`, `lastHydrationTime`, `hydrationCount`, `lastHydrationType` | 시각은 Unix 초입니다. `lastHydrationType` 은 `Active` 만 들어 있습니다. 개인 75행, 회사 95행 |
| `od_ServiceOperationHistory` | `id`, `timestamp`, `scopeId`, `operationName`, `resultCode`, `sizeInBytes`, `scenarioName` | `timestamp` 는 Unix 초입니다. 개인 2,523행, 회사 1,479행. 가장 이른 값과 늦은 값이 약 29일 차이입니다 |
| `od_GraphMetadata_Records` | `resourceID`, `graphMetadataJSON`, `spoCompositeID`, `createdBy`, `modifiedBy`, `filePolicies`, `fileExtension`, `lastWriteCount` | 내용은 실제 데이터로 확인합니다 |
| `od_ArchiveData_Records` | `resourceID`, `fileName`, `lastReportedAccessTime`, `lastReportingTime` | 회사 계정 676행, 개인 계정 0행 |

- `od_HydrationData` 는 자리표시자 파일을 언제 처음, 언제 마지막으로 내려받았는지 보여 주는 표로 보입니다. 공식 설명은 없고, 열 이름과 값에서 미루어 본 뜻입니다.
- `od_ServiceOperationHistory` 의 `operationName` 에는 `GetQuotaInfo`, `GetClientPolicy`, `NotificationReceived`, `EnumChanges`, `SyncVerification`, `CreateSubscription`, `DeleteSubscription`, `DownloadBlock`, `InlineUploadBatch`, `UploadBatch`, `GetCanonicalFolderInfo` 같은 값이 들어갑니다.
- 이 표의 보관 기간은 공개된 자료가 없으므로 실제 데이터에서 가장 이른 시각과 늦은 시각으로 확인합니다. 약 한 달 치만 남은 예가 있습니다.

### 같은 폴더의 SafeDelete.db

`SafeDelete.db` 도 암호화하지 않은 SQLite 입니다.

| 표 | 열 |
|---|---|
| `filter_delete_info` | `fileId`, `volumeId`, `notificationTime`, `path`, `process` |
| `deletes_last_touched_by_sync_engine` | `resourceId`, `notificationTime`, `isKFMOptOut` |
| `items_moved_to_recycle_bin` | `fileId`, `volumeId`, `itemName`, `resourceId`, `parentResourceId`, `reparentStatus`, `notificationTime` 등 |
| `unvalidated_deletes_displayed_in_ux`, `placeholder_deletes_info`, `redundant_placeholder_deletes` | 공개된 설명 없음 |

`notificationTime` 은 Unix 초입니다. 회사 계정의 `filter_delete_info` 8행의 `process` 열에 서로 다른 프로그램 4개가 적힌 예가 있어, "어떤 프로그램이 어떤 경로를 지웠는지" 가 남을 수 있습니다. 어떤 조건에서 이 표에 행을 쓰는지는 공개된 설명이 없습니다.

## 증거로서 의미

### 증명하는 것

- 동기화 엔진이 알고 있던 파일과 폴더의 이름, 크기, 위치를 보여 줍니다.
- `lastChange` 는 로컬 파일의 수정 시각입니다. 파일 60개를 실제 파일과 대 보면 60/60 맞습니다.
- `localHashDigest` 로 다른 곳에서 찾은 파일이 같은 내용인지 맞춰 볼 수 있습니다. Graph 나 웹에서 받은 `quickXorHash` 와도 맞춰 볼 수 있습니다.
- `od_ServiceOperationHistory` 는 언제 어떤 종류의 작업을 서비스와 주고받았는지, 크기가 얼마였는지 보여 줍니다.
- `SafeDelete.db` 의 `filter_delete_info` 에 행이 있으면 그 경로를 지운 프로그램 이름이 남아 있습니다.

### 증명하지 못하는 것

- 사용자가 파일을 열었거나 읽었다는 것은 이 DB 로 알 수 없습니다.
- 파일 행이 있다고 그 파일 내용이 PC 에 있었다는 뜻은 아닙니다. 파일 주문형에서는 자리표시자만 있을 수 있습니다. 내용이 있었는지는 파일 시스템에서 따로 확인합니다.
- 누가 파일을 올렸는지는 이 DB 만으로 알 수 없습니다. `od_GraphMetadata_Records` 의 `createdBy`·`modifiedBy` 에 무엇이 들어가는지는 실제 데이터로 확인합니다.
- `od_HydrationData` 가 사용자의 직접 열기인지 다른 프로그램의 읽기인지는 알 수 없습니다. 표의 뜻 자체도 짐작입니다.
- 행이 없다고 동기화하지 않았다는 뜻은 아닙니다. 지운 파일의 행이 언제까지 남는지는 공개된 자료가 없습니다.
- `od_ServiceOperationHistory` 에 없는 기간을 "활동이 없었다" 로 읽지 않습니다. 약 한 달 치만 남은 예가 있습니다.

보고서에는 "이 파일을 클라우드에 올렸다" 대신 이렇게 씁니다. "사용자 A 의 회사 계정 동기화 DB 에 파일 X 행이 있다. `lastChange` 는 Y(UTC)이고, QuickXorHash 는 Z 이다."

## 시각 해석

DB 의 시각 열은 모두 Unix 초입니다. 1970-01-01 00:00 UTC 부터 센 초이므로 변환하면 UTC 입니다. 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

| 열 | 언제의 시각인가 | 근거 |
|---|---|---|
| `lastChange` | 로컬 파일의 수정 시각 | 내용이 PC 에 있는 파일 60개를 실제 파일과 대 보면 두 계정 모두 60/60 같습니다 |
| `diskCreationTime` | 공개된 설명 없음 | 실제 파일의 만든 시각과 개인 10/60, 회사 21/60 만 같습니다 |
| `serverLastChange`, `diskLastAccessTime`, `mediaDateTaken` | 이름에서 미루어 본 뜻만 있습니다 | Unix 초 범위의 값입니다 |
| `od_HydrationData` 의 시각 | 처음·마지막 내려받기로 보입니다 | Unix 초입니다 |
| `od_ServiceOperationHistory.timestamp` | 작업 시각 | Unix 초입니다 |
| `SafeDelete.db` 의 `notificationTime` | 삭제 알림 시각으로 보입니다 | Unix 초입니다 |

`lastChange` 에 315500400 이 든 행이 있습니다. 이 값은 1980-01-01 00:00 (UTC+9), 곧 1979-12-31 15:00 UTC 이고 날짜가 비어 있던 파일로 보이므로, 이런 값을 실제 수정 시각으로 읽지 않습니다. `diskCreationTime` 도 실제 파일과 맞은 비율이 낮았으므로 파일을 만든 시각으로 보고서에 쓰지 않습니다.

## 함정과 한계

- **`-wal`·`-shm` 을 함께 뜹니다.** WAL 방식이므로 아직 본 DB 로 옮기지 않은 변경이 `-wal` 에 있을 수 있습니다. 주 파일만 뜨면 최근 변경을 놓칩니다.
- **원본을 SQLite 로 바로 열지 않습니다.** 해시를 기록한 사본에서 작업합니다. 이유는 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.
- **실행 중인 PC 에서 파일 해시를 맞춰 볼 때 조심합니다.** 자리표시자 (placeholder) 파일을 읽으면 내려받기 (hydration) 가 일어납니다. 로컬에 내용이 있는 파일만 읽고, 자리표시자는 건너뜁니다. 자리표시자의 구조는 [클라우드 동기화 공통 구조](../cloud-files-api-syncrootmanager.md) 에서 다룹니다.
- **해시를 16진 문자열과 base64 로 혼동하지 않습니다.** DB 는 원시 바이트, Graph 는 base64 입니다. 20바이트 해시를 base64 로 바꾸면 28글자가 됩니다.
- **해시가 없는 행이 있습니다.** 계정마다 9행이 비어 있는 예가 있습니다.
- **코드 값의 뜻을 짐작으로 채우지 않습니다.** `fileStatus`, `lastKnownPinState`, `scopeType`, `libraryType`, `irm*` 열의 값은 공개된 설명이 없습니다.
- **표와 열 이름은 앱 버전을 따릅니다.** 옛 PC 는 `.dat` 형식일 수 있습니다. 새 버전에서 표나 열이 늘거나 바뀔 수 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

**정수 시각 값.** 아래는 SQLite 명세로 만든 예시입니다. 특정 파일에서 나온 값이 아닙니다. SQLite 레코드는 정수를 빅엔디언 (big-endian) 으로 저장합니다. 1704067200 은 4바이트 정수에 들어가므로 SQLite 는 이 값을 형식 값(serial type) 4 로 적습니다.

```
레코드 안의 바이트: 65 92 00 80
정수로 읽기:        0x65920080 = 1704067200
Unix 초로 읽기:     2024-01-01 00:00:00 UTC
```

레코드 머리와 형식 값을 읽는 법은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

**해시 열.** `localHashDigest` 는 20바이트 BLOB 입니다. 아래는 자리만 표시한 예시입니다.

```
hh hh hh hh hh hh hh hh hh hh hh hh hh hh hh hh hh hh hh hh   (20바이트)
→ hex() 결과: 40글자
→ base64 결과: 28글자, 끝이 "=" 하나
```

base64 로 바꾼 값이 Graph 의 `quickXorHash` 와 같은 모양입니다.

### 공개 도구로 한 번

`SyncEngineDatabase.db` 를 `-wal`·`-shm` 과 함께 사본으로 뜬 뒤, SQLite 명령줄 도구로 사본을 엽니다.

```sql
-- 표 목록
SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name;

-- 파일마다 전체 경로를 만들고 시각·해시를 붙인다
WITH RECURSIVE up(fileId, parentId, path, depth) AS (
  SELECT resourceID, parentResourceID, fileName, 0
  FROM od_ClientFile_Records
  UNION ALL
  SELECT up.fileId, d.parentResourceID, d.folderName || '\' || up.path, up.depth + 1
  FROM up JOIN od_ClientFolder_Records d ON d.resourceID = up.parentId
  WHERE up.depth < 64
)
SELECT f.resourceID,
       u.path,
       f.size,
       datetime(f.lastChange, 'unixepoch')       AS last_change_utc,
       datetime(f.serverLastChange, 'unixepoch') AS server_last_change_utc,
       f.fileStatus,
       f.localHashAlgorithm,
       hex(f.localHashDigest)                    AS local_hash_hex
FROM up u
JOIN od_ClientFile_Records f ON f.resourceID = u.fileId
WHERE NOT EXISTS (SELECT 1 FROM od_ClientFolder_Records d WHERE d.resourceID = u.parentId)
ORDER BY u.path;

-- 서비스와 주고받은 작업
SELECT datetime(timestamp, 'unixepoch') AS utc, operationName, resultCode, sizeInBytes, scenarioName
FROM od_ServiceOperationHistory
ORDER BY timestamp;

-- 내려받기 기록 (파일 이름을 붙여 본다)
SELECT h.resourceID, f.fileName,
       datetime(h.firstHydrationTime, 'unixepoch') AS first_utc,
       datetime(h.lastHydrationTime, 'unixepoch')  AS last_utc,
       h.hydrationCount, h.lastHydrationType
FROM od_HydrationData h
LEFT JOIN od_ClientFile_Records f ON f.resourceID = h.resourceID
ORDER BY h.lastHydrationTime;
```

- 경로 조회는 부모 폴더를 더 찾을 수 없는 행만 남깁니다. 그래서 맨 위 폴더부터 이어 붙인 경로가 나옵니다.
- `hex()` 결과는 다른 도구로 base64 로 바꿔 Graph 값과 비교합니다.
- `SafeDelete.db` 는 따로 엽니다. `SELECT datetime(notificationTime, 'unixepoch'), path, process FROM filter_delete_info;` 로 지운 경로와 프로그램을 봅니다.

공개 도구 OneDriveExplorer 는 settings 폴더의 DB 로 폴더 구조를 다시 만듭니다. `$Recycle.Bin` 으로 지운 항목을 찾고, ODL 로그를 항목과 엮어 보여 줍니다. 도구가 보여 주는 경로와 시각은 위 조회 결과와 한 번 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 계정·설정 레지스트리 | DB 가 어느 계정 것인지, 동기화 폴더가 어디인지 봅니다 | [계정·설정 레지스트리](accounts-settings.md) |
| 로그 | DB 의 시각 무렵에 앱이 올리기·내려받기를 했는지 봅니다 | [로그 (ODL·ODLGZ)](odl-odlgz.md) |
| 마스터 파일 테이블 | `lastChange` 와 실제 파일의 수정 시각을 맞춰 봅니다 | [마스터 파일 테이블](../../filesystem/mft.md) |
| USN 변경 저널 | 동기화 폴더 안에서 파일이 생기고 지워진 순서를 봅니다 | [USN 변경 저널](../../filesystem/usnjrnl.md) |
| 휴지통 | 동기화 폴더에서 지운 파일이 휴지통에 있는지 봅니다 | [휴지통](../../file-folder-usage/recycle-bin.md) |
| 해시 대조 | QuickXorHash 로 다른 곳에서 찾은 파일과 맞춰 봅니다 | [해시셋 대조와 유사 해시](../../../03-techniques/analysis/hash-set-fuzzy-hash.md) |
| 자리표시자 구조 | 온라인 전용 파일과 내려받은 파일을 구분합니다 | [클라우드 동기화 공통 구조](../cloud-files-api-syncrootmanager.md) |

자료 유출을 의심하는 사건에서 이 DB 를 쓰는 흐름은 [자료를 밖으로 빼돌렸나](../../../04-scenarios/exfiltration/data-exfiltration/index.md) 에 있습니다.

## 실습

OneDrive 를 쓴 공개 시험 데이터(NIST CFReDS 등)에서 사용자의 `settings` 폴더를 통째로 꺼내 아래 질문을 풀어 봅니다.

1. 계정 폴더마다 `SyncEngineDatabase.db` 가 있습니까? `-wal` 파일의 크기는 얼마입니까?
2. `__oddbm_schema` 표에는 어떤 이름과 값이 있습니까? 이 페이지의 표 목록과 다른 표가 있습니까?
3. 경로 조회로 파일 전체 경로를 만든 뒤, 내용이 PC 에 있는 파일과 자리표시자로만 있는 파일을 나눕니다. 각각 몇 개입니까?
4. 디스크에 있는 파일 몇 개를 골라 `lastChange` 와 파일 시스템의 수정 시각을 비교합니다. 몇 개가 같습니까?
5. `localHashAlgorithm` 값은 무엇입니까? 파일 하나로 QuickXorHash 를 계산해 `localHashDigest` 와 맞춰 봅니다.
6. `od_ServiceOperationHistory` 의 가장 이른 시각과 가장 늦은 시각은 며칠 차이입니까? `UploadBatch` 가 몰린 시간대가 있습니까?
7. `SafeDelete.db` 의 `filter_delete_info` 에 행이 있습니까? `process` 열에 어떤 프로그램이 있습니까?

## 참고 문헌

1. Beercow/OneDriveExplorer, README — https://github.com/Beercow/OneDriveExplorer
2. Microsoft Learn, "hashes resource type" (Microsoft Graph v1.0) — https://learn.microsoft.com/en-us/graph/api/resources/hashes
3. Microsoft Learn, "Build a Cloud Sync Engine that Supports Placeholder Files" — https://learn.microsoft.com/en-us/windows/win32/cfapi/build-a-cloud-file-sync-engine
