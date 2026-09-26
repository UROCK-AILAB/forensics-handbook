---
title: "윈도 타임라인"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1320
---

# 윈도 타임라인 (ActivitiesCache.db)

윈도 타임라인 (Windows Timeline) 의 활동 기록은 계정마다 SQLite 데이터베이스 `ActivitiesCache.db` 에 남습니다. 앱을 열거나 쓴 활동, 파일과 웹페이지를 연 활동, 클립보드 활동이 행 하나씩 들어갑니다. 다른 기기에서 동기화된 행이 섞일 수 있고, 시각 열은 Unix 초로 풀립니다.

## 무엇을 기록하나 · 왜 생기나

활동 기록 (activity history) 은 사용한 앱과 서비스, 연 파일, 둘러본 웹사이트처럼 기기에서 한 일을 기록하며 기기 안에 저장됩니다. 기기에 연결된 계정마다 따로 모으므로 로컬 계정, Microsoft 계정, 회사·학교 계정이 각각 따로입니다. 타임라인은 활동을 시간순으로 보여 주고, 하던 일을 다시 이어서 하게 해 주는 기능입니다[2].

### 활동 종류 (ActivityType)

행마다 `ActivityType` 값이 있습니다. 값의 뜻은 아래와 같습니다[1].

| 값 | 뜻 |
|---|---|
| 2 | 알림 (Notification) |
| 5 | 앱·파일·웹페이지 열기 |
| 6 | 앱을 쓰는 중이거나 앱에 포커스가 있음. 사용 시간 계산에 쓰입니다 |
| 10 | 클립보드 텍스트. 지속 시간은 43,200초 (12시간) 입니다 |
| 11, 12, 15 | Windows 시스템 작업 (자격 증명, Wi-Fi, 개인 설정, 언어, 접근성) |
| 16 | 복사·붙여넣기 |

값 0·1·3·4·7·13 도 설정 목록에 나옵니다 (아래 "구조" 참고). 3 은 모바일 기기 백업이나 Azure 인증으로 짐작되지만 확정되지 않았고, 0·1·4·7·8·9·13 은 뜻이 알려져 있지 않습니다[1].

### 기록을 켜고 지우는 설정

| Windows | 설정 위치 |
|---|---|
| 11 | 설정 > 개인 정보 및 보안 > 활동 기록. 설정 이름은 "Store my activity history on this device" 입니다 |
| 10 | 설정 > 개인 정보 > 활동 기록 |

- 같은 설정 화면에서 기기에 저장된 활동 기록을 지울 수 있습니다.
- 활동 기록을 Microsoft 로 보내는 옵션은 Windows 11 22H2·23H2 에서 2024-01-23 KB5034204 업데이트부터 없어졌습니다[2].
- 이 설정이 레지스트리의 어느 값에 남는지는 공개 자료에 나와 있지 않습니다.

## 위치와 버전별 차이

### 위치

```
%LOCALAPPDATA%\ConnectedDevicesPlatform\<계정 폴더>\ActivitiesCache.db
```

- `ConnectedDevicesPlatform` 폴더 아래에 계정마다 폴더가 하나씩 있습니다. 로컬 계정은 `L.<사용자>` 폴더, 그 밖의 계정은 AAD·MSA 이름 규칙의 폴더를 쓴다는 설명이 널리 쓰입니다. 이 규칙을 뒷받침하는 공개 문서가 드물므로 실제 이미지의 폴더를 모두 확인합니다.
- DB 옆에 `ActivitiesCache.db-wal` 과 `ActivitiesCache.db-shm` 이 함께 있습니다. 세 파일을 함께 수집하며, 이유는 "구조" 에서 설명합니다.
- 사용자 프로필 폴더 안이라 어느 Windows 사용자의 기록인지 가를 수 있습니다. 프로필 폴더와 계정의 짝은 [사용자 프로필 목록](../system-account/profilelist.md) 으로 확인합니다.

Windows 11 25H2 에서는 다음과 같은 모습이 나타날 수 있습니다.

- 계정 폴더로 16자리 16진수 이름의 폴더와 `AAD.<GUID>` 이름의 폴더가 함께 있습니다.
- `L.` 로 시작하는 폴더가 없을 수도 있습니다.
- 16자리 16진수 이름의 폴더가 어느 계정 종류인지는 공개 자료에 나와 있지 않습니다.
- 계정 폴더마다 `ActivitiesCache.db`, `-wal`, `-shm` 세 파일이 있습니다.
- `ConnectedDevicesPlatform` 바로 아래에는 `<폴더 이름>.cdp`, `<폴더 이름>.cdpresource`, `CDPGlobalSettings.cdp`, `Connected Devices Platform certificates.sst` 파일이 있습니다.

GUID 표기는 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에서 다룹니다.

### Windows 버전에 따라 달라지는 점

| Windows | 내용 | 참고 문헌 |
|---|---|---|
| 10 1803 (빌드 17134) · 1809 (17763) · 1903 이후 | 타임라인을 지원합니다 | [1] |
| 11 22H2 · 23H2 | 2024-01-23 KB5034204 부터 Microsoft 로 보내는 옵션이 없어졌습니다 | [2] |
| 11 25H2 | DB 를 만들고 계속 갱신합니다. `user_version` 은 30 입니다 | — |

- Windows 11 에서 타임라인 화면이 없어졌다는 설명이 널리 쓰이지만, Microsoft 문서[2]에는 그런 설명이 없습니다.
- 화면이 없어도 DB 는 남고 계속 기록됩니다. Windows 11 25H2 에서 16진수 이름 폴더의 `-wal` 크기가 몇 분 사이에 4,152 바이트에서 935,272 바이트로 늘어난 예가 있습니다.
- 분석 대상의 버전은 [시스템 기본 정보](../system-account/os-version-computer-name-install-date-shutdown-t.md) 로 먼저 확인합니다.

## 구조

### 파일 형식

Windows 11 25H2 기준 형식은 다음과 같습니다.

- 평범한 SQLite 파일입니다. 첫 16바이트가 `SQLite format 3` 과 `00` 입니다.
- [윈도 검색 색인 DB](windows-search/index.md) 처럼 헤더가 암호화돼 있지 않습니다.
- `journal_mode` 는 `wal` 입니다. 그래서 최근 기록이 `-wal` 파일에만 있을 수 있습니다.

WAL 파일을 읽는 방법과 지운 행이 남는 자리는 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

### 표

Windows 11 25H2 의 DB 에는 다음 표가 있습니다.

| 표 | 열 또는 내용 |
|---|---|
| `Activity` | 활동 행. 아래 표에 열을 적었습니다 |
| `ActivityOperation` | `Activity` 와 비슷한 열에 `OperationOrder`, `OperationType`, `CreatedTime`, `OperationExpirationTime`, `CorrelationVector`, `UploadAllowedByPolicy`, `PatchFields`, `ThrottleReleaseTime`, `PublishProcessStatus` 가 더 있습니다 |
| `Activity_PackageId` | `ActivityId`, `Platform`, `PackageName`, `ExpirationTime` |
| `SmartLookup` | `Activity` 와 거의 같은 열에 `IsInUploadQueue` 가 더 있습니다 |
| `Metadata` | DB 설정. 키는 `CurrentEtag`, `CurrentSettings`, `DatabaseActivityPolicies`, `DatabaseInstanceId`, `DatabaseInstanceIdUpdateTime`, `DatabaseNotificationSubscriptionInfo`, `PendingFirstDEKUpload` 입니다 |
| `AppSettings`, `Asset`, `DataEncryptionKeys`, `ManualSequence` | 열의 뜻은 공개 자료에 나와 있지 않습니다 |

분석에서 주로 다루는 표는 `Activity` ("Activities" 로 적기도 합니다), `Activity_PackageID`, `ActivityOperation` 입니다[1].

### Activity 표의 열

Windows 11 25H2 에서 `Activity` 표의 열은 다음과 같습니다.

`Id`, `AppId`, `PackageIdHash`, `AppActivityId`, `ActivityType`, `ActivityStatus`, `ParentActivityId`, `Tag`, `Group`, `MatchId`, `LastModifiedTime`, `ExpirationTime`, `Payload`, `Priority`, `IsLocalOnly`, `PlatformDeviceId`, `DdsDeviceId`, `CreatedInCloud`, `StartTime`, `EndTime`, `LastModifiedOnClient`, `GroupAppActivityId`, `ClipboardPayload`, `EnterpriseId`, `OriginalPayload`, `UserActionState`, `IsRead`, `OriginalLastModifiedOnClient`, `GroupItems`, `LocalExpirationTime`, `ETag`

분석에 자주 쓰는 열은 다음과 같습니다.

| 열 | 형태 | 알려진 내용 |
|---|---|---|
| `Id` | GUID | 행 식별자 |
| `AppId` | `[{"application":…, "platform":…}]` 모양의 JSON 배열 문자열 | 활동과 연결된 앱 |
| `ActivityType` | 정수 | 활동 종류. 위 표를 봅니다 |
| `Payload` | BLOB | JSON 으로 알려져 있습니다[1]. 전체를 조회하려면 SQLite JSON1 확장이 필요합니다 |
| `ClipboardPayload` | BLOB | Base64 로 인코딩한 텍스트 |
| `PlatformDeviceId` | — | 활동이 나온 기기. 이 값을 HKCU 의 DeviceCache 항목과 맞춰 기기를 찾습니다. 같은 기기의 값도 시간이 지나면 바뀝니다[1] |
| `StartTime`, `EndTime`, `LastModifiedTime`, `ExpirationTime`, `CreatedInCloud`, `LastModifiedOnClient` | `StartTime`·`LastModifiedTime` 은 INTEGER | Unix 초로 풀립니다. 열마다의 정확한 뜻은 아래 "시각 해석" 을 봅니다 |

- DeviceCache 의 전체 키 경로는 공개 자료에 나와 있지 않습니다. 흔히 `HKCU\Software\Microsoft\Windows\CurrentVersion\TaskFlow\DeviceCache` 로 설명하는 키가 Windows 11 25H2 에는 없을 수 있습니다.
- `Metadata` 의 `CurrentSettings` 값은 `{"ActivityTypes":[0,1,3,4,7,11,12,13,15,16],"Environment":"prod"}` 와 같은 모양입니다. `AAD.<GUID>` 폴더 DB 에서는 `ActivityTypes` 가 `[0,1,3,4,7,13,16]` 인 예가 있습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 계정 폴더의 DB 에 이 활동 행이 있습니다 | 그 행이 이 PC 에서 생겼는지. 다른 기기에서 동기화된 행일 수 있습니다 |
| 유형 5 행이 있으면, 활동 기록에 앱·파일·웹페이지를 연 활동이 올라갔습니다 | 파일 내용을 읽거나 고쳤는지 |
| 유형 6 행이 있으면, 활동 기록에 그 앱을 쓰던 활동이 올라갔습니다 | 그 계정 앞에 실제로 누가 앉아 있었는지 |
| `PlatformDeviceId` 로 행이 어느 기기에서 왔는지 가를 실마리. 같은 기기의 값도 시간이 지나면 바뀔 수 있습니다 | 시각 열 하나하나의 정확한 뜻 |
| 유형 10 행에 `ClipboardPayload` 가 있으면 그 클립보드 텍스트 | 행이 없으니 활동도 없었다는 것 |
| | 암호화된 `Payload` 의 내용 |

- 행이 없는 이유는 여러 가지입니다. 설정을 껐을 수 있고, 기록을 지웠을 수 있고, DB 가 그 유형을 모으지 않았을 수 있습니다.
- 다른 기기의 행을 이 PC 의 행과 섞어 읽지 않고, 기기를 먼저 가른 뒤에 해석합니다. 사람을 가려내는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

### 보고서 문장

아래 앱 이름과 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 프로필의 ActivitiesCache.db `Activity` 표에 ActivityType 5 인 행이 있습니다. `AppId` 의 application 값은 메모장을 가리키는 문자열이고, `StartTime` 을 Unix 초로 풀면 2025-04-02 06:15:30 UTC 입니다. 이 행의 `PlatformDeviceId` 는 같은 DB 의 다른 행 대부분과 같습니다."
- 쓰면 안 되는 문장: "사용자 A 가 2025-04-02 15:15 에 이 PC 에서 메모장으로 문서를 열었습니다."

## 시각 해석

| 열 | 형식 | 알려진 것 |
|---|---|---|
| `StartTime` | Unix 초, INTEGER | 이름은 시작 시각이지만, 정확한 뜻은 공개 자료에 나와 있지 않습니다 |
| `EndTime` | Unix 초 | Windows 11 25H2 에서 모든 행이 0 인 예가 있습니다 |
| `LastModifiedTime` · `LastModifiedOnClient` | Unix 초. `LastModifiedTime` 은 INTEGER | 정확한 뜻은 공개 자료에 나와 있지 않습니다 |
| `ExpirationTime` | Unix 초 | 정확한 뜻은 공개 자료에 나와 있지 않습니다 |
| `CreatedInCloud` | Unix 초 | 정확한 뜻은 공개 자료에 나와 있지 않습니다. 값이 있는 행은 동기화를 거친 행일 수 있습니다 |

- Unix 초는 1970-01-01 00:00:00 UTC 부터 센 초입니다. 그래서 풀어낸 값은 UTC 입니다. 계산은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서, 현지 시각 변환은 [시간대 설정](../system-account/time-zone.md) 에서 다룹니다.
- Windows 11 25H2 에서 `StartTime` 과 `LastModifiedTime` 은 INTEGER 로 저장되고, Unix 초로 풀면 맞는 날짜가 나옵니다.
- 로컬 DB 의 보존 기간은 공개 자료에 나와 있지 않습니다. 흔히 말하는 30일은 클라우드에 올라간 활동 기록이 마지막 동기화 뒤 30일 안에 자동으로 지워진다는 뜻입니다[2]. 로컬 DB 의 보존 기간이 아닙니다.
- `ExpirationTime` − `LastModifiedTime` 이 2,555~3,650일 (약 7~10년) 인 경우가 있습니다.
- 보존 기간을 가정해 "이 날짜 전 기록은 없다" 고 쓰지 않습니다. 실제 행의 날짜 범위를 적습니다.

## 함정과 한계

1. **동기화된 행을 이 PC 의 행으로 읽습니다.** Windows 11 25H2 DB 의 예입니다.
   - `StartTime` 범위가 2023-03-28 ~ 2026-09-23 입니다.
   - 사용자 폴더는 2026-06-26 에 만들어졌는데 그보다 오래된 행이 있습니다.
   - 711행 가운데 702행에 `CreatedInCloud` 값이 있습니다.
   - `PlatformDeviceId` 가 활동 종류마다 5~7가지입니다.

   이런 DB 에는 다른 기기에서 동기화돼 들어온 행이 섞여 있습니다. 행을 `PlatformDeviceId` 로 먼저 나눕니다.
2. **`-wal` 을 빼고 수집합니다.** 최근 기록이 `-wal` 에만 있을 수 있습니다. `ActivitiesCache.db`, `-wal`, `-shm` 세 파일을 함께 가져옵니다.
3. **원본 DB 를 바로 엽니다.** 사본을 만든 뒤 사본을 엽니다. SQLite 도구가 WAL 을 합치면 파일이 바뀝니다. 자세한 내용은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.
4. **Windows 11 에서도 파일 열기 행을 기대합니다.** Windows 11 25H2 의 16진수 이름 폴더 DB 예입니다.
   - `Activity` 711행, `ActivityOperation` 0행, `Activity_PackageId` 1,422행, `DataEncryptionKeys` 82행입니다.
   - `ActivityType` 은 11 (604행), 12 (21행), 15 (86행) 뿐입니다. 유형 5·6 행은 없습니다.
   - `AppId` 의 application 값은 설정·자격 증명 동기화처럼 보이는 이름입니다. "11·12·15 = 시스템 작업" 설명과 맞습니다.
   - `AAD.<GUID>` 폴더 DB 는 `Activity` 와 `ActivityOperation` 이 모두 0행입니다.

   두 DB 의 `CurrentSettings` 에 있는 `ActivityTypes` 목록에도 5 와 6 이 없습니다. 이 목록과 유형 5·6 행이 없는 것이 관계있는지는 알려져 있지 않습니다.
5. **`Payload` 를 모두 JSON 으로 읽습니다.** Windows 11 25H2 에서 `Payload` 는 BLOB 열에 Base64 ASCII 텍스트로 들어 있을 수 있습니다.
   - 유형 15 는 Base64 를 풀면 DER 로 된 CMS EnvelopedData (OID 1.2.840.113549.1.7.3) 입니다.
   - 유형 11·12 는 Base64 를 풀면 `43 42 01 00` 으로 시작하는 이진 데이터입니다.

   이 유형들은 JSON 이 아니고 암호화된 것으로 보입니다. `DataEncryptionKeys` 표와의 관계는 알려져 있지 않습니다.
6. **클립보드 열에 값이 있으면 내용도 있다고 봅니다.** `ClipboardPayload` 에 값이 든 137행이 모두 `[]` 인 예가 있습니다.
7. **계정 폴더 이름을 규칙대로만 찾습니다.** `L.` 폴더가 없을 수도 있습니다. `ConnectedDevicesPlatform` 아래 폴더를 모두 열어 봅니다.

### 지우기와 조작

- **설정에서 지웁니다.** 사용자는 설정 화면에서 기기에 저장된 활동 기록을 지울 수 있습니다. 지운 행은 DB 안의 빈 공간이나 `-wal` 에 남을 수 있습니다. 찾는 방법은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.
- **설정을 끕니다.** 수집할 때 "Store my activity history on this device" 설정 상태를 함께 적어 둡니다. 설정이 꺼져 있으면 행이 없는 것을 사용하지 않은 것으로 읽지 않습니다.
- **DB 파일을 지웁니다.** 파일을 지운 흔적은 [마스터 파일 테이블](../filesystem/mft.md) 과 [USN 변경 저널](../filesystem/usnjrnl.md) 에서 봅니다. 지우기 전 DB 는 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 파일 헤더 문자열로 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00
```

1. 0x00~0x0E 를 ASCII 로 읽으면 `SQLite format 3` 입니다.
2. 0x0F 의 `00` 이 문자열 끝입니다.
3. 이 16바이트가 보이면 평범한 SQLite 파일입니다. 보이지 않으면 암호화나 손상을 의심합니다.
4. 같은 폴더에 `-wal` 파일이 있는지, 크기가 얼마인지 적어 둡니다.

`Payload` 를 볼 때는 BLOB 의 앞 바이트를 먼저 봅니다. 아래는 Windows 11 25H2 에서 나타나는 앞부분 모양만 옮긴 예시입니다. 뒤 바이트는 줄였습니다.

```
Base64 를 푼 뒤 (유형 11·12)
오프셋  00 01 02 03 04 05 06 07
0x00    43 42 01 00 .. .. .. ..
```

5. BLOB 이 영문자·숫자·`+`·`/`·`=` 로만 된 ASCII 라면 Base64 로 보고 풉니다.
6. 푼 결과가 JSON 텍스트인지, 위처럼 이진 데이터인지 확인합니다.
7. 이진 데이터라면 암호화된 것으로 보고, 내용을 짐작해 보고서에 쓰지 않습니다.

### 공개 도구로 한 번

SQLite 명령줄 도구 `sqlite3` 로 사본을 열어 봅니다. `json_extract` 는 JSON1 확장이 들어 있는 빌드에서만 됩니다.

```sql
-- 활동 종류별 행 수
SELECT ActivityType, COUNT(*) FROM Activity GROUP BY ActivityType;

-- 기기별 행 수. 동기화된 행을 가를 때 씁니다
SELECT PlatformDeviceId, COUNT(*) FROM Activity GROUP BY PlatformDeviceId;

-- 시각을 UTC 로 풀어 보기
SELECT Id,
       ActivityType,
       json_extract(AppId, '$[0].application') AS app,
       datetime(StartTime, 'unixepoch')        AS start_utc,
       datetime(LastModifiedTime, 'unixepoch') AS modified_utc,
       PlatformDeviceId
FROM Activity
ORDER BY StartTime;

-- DB 설정 (CurrentSettings 등)
SELECT * FROM Metadata;
```

kacos2000 의 WindowsTimeline 저장소에는 이 DB 의 표와 활동 종류를 정리한 자료가 있습니다[1]. 다른 SQLite 도구나 타임라인 도구를 써도 됩니다. 도구를 쓸 때는 다음을 확인합니다.

- `-wal` 까지 반영해서 읽는지 확인합니다.
- 시각을 UTC 로 보여 주는지, 분석 PC 의 현지 시각으로 바꿔 보여 주는지 확인합니다.
- 다른 기기의 행을 구분해 보여 주는지 확인합니다.
- `Payload` 를 JSON 으로만 풀려다 암호화된 행을 빼 버리지 않는지 확인합니다.
- 행 몇 개는 `sqlite3` 로 직접 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [바로가기 파일](lnk.md) · [점프리스트](jump-lists.md) · [최근 문서](recentdocs.md) | 유형 5 행의 파일을 연 흔적이 이 PC 에도 있는지 |
| [UserAssist](../execution/userassist.md) · [프리페치](../execution/prefetch/index.md) · [BAM·DAM](../execution/background-activity-moderator.md) | 유형 5·6 행의 앱이 이 PC 에서 실행됐는지 |
| [SRUM](../execution/system-resource-usage-monitor/index.md) | 앱 사용 시간. 유형 6 행과 비교합니다 |
| [윈도 알림 기록](../execution/wpndatabase-db.md) | 유형 2 알림 행과 같은 알림이 있는지 |
| [크롬 계열 브라우저](../browsers/chrome-edge-whale/index.md) | 웹페이지를 연 활동과 방문 기록 |
| [사용자 프로필 목록](../system-account/profilelist.md) · [사용자 계정](../system-account/sam.md) | 계정 폴더가 어느 사용자의 것인지 |
| [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 옛 DB. 지금 DB 와 비교하면 지운 행이 드러납니다 |

여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다. 파일을 연 기록을 합쳐 읽는 순서는 [이 파일을 누가 언제 열었나](../../04-scenarios/activity/file-access.md) 에서, 프로그램 실행을 좇는 순서는 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 실습 이미지 가운데 Windows 10 1803 이후 이미지를 골라 다음을 풀어 봅니다.

1. `ConnectedDevicesPlatform` 아래에 계정 폴더가 몇 개 있습니까? 폴더 이름은 어떤 규칙을 따릅니까?
2. 각 폴더에 `-wal` 파일이 있습니까? 사본을 만들 때 세 파일을 모두 가져왔습니까?
3. `Activity` 표를 `ActivityType` 별로 세어 봅니다. 유형 5 와 6 행이 있습니까?
4. `PlatformDeviceId` 는 몇 가지입니까? 가장 많은 값이 이 PC 라고 볼 근거를 다른 기록에서 찾아봅니다.
5. 유형 5 행 하나를 골라 `StartTime` 을 UTC 로 풀어 봅니다. 같은 파일의 바로가기 파일이나 점프리스트 시각과 얼마나 떨어져 있습니까?
6. `Metadata` 의 `CurrentSettings` 를 읽어 봅니다. `ActivityTypes` 목록과 실제 행의 유형이 맞습니까?

실험용 가상 머신이 있으면 활동 기록 설정을 켠 채 파일을 열고 앱을 써 봅니다. 앞뒤로 세 파일을 떠서 어느 표에 어떤 행이 늘었는지 비교합니다. 결과에는 실험한 Windows 버전과 설정 상태를 함께 적습니다.

## 참고 문헌

- kacos2000, WindowsTimeline (GitHub README) — https://github.com/kacos2000/WindowsTimeline
- Microsoft Support, "Windows activity history and your privacy" — https://support.microsoft.com/en-us/windows/windows-activity-history-and-your-privacy-2b279964-44ec-8c2f-e0c2-6779b07d2cbd
