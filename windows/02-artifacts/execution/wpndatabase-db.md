---
title: "윈도 알림 기록"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 1100
---

# 윈도 알림 기록 (wpndatabase.db)

Windows 10 1607 이후 사용자에게 뜬 알림은 `%LOCALAPPDATA%\Microsoft\Windows\Notifications\wpndatabase.db` 에 SQLite 형식으로 남습니다. 알림 내용 (XML), 알림을 보낸 앱, 받은 시각, 지울 시각이 한 행에 들어 있습니다. 알림에는 메시지나 글의 일부가 들어 있을 수 있어, 원본이 지워진 뒤에도 내용을 되찾는 데 씁니다.

## 무엇을 기록하나 · 왜 생기나

앱이 띄운 알림 (notification) 은 이 DB 에 들어가고, `ExpiryTime` 열의 시각이 되면 지워집니다. 알림 한 건은 `Notification` 표의 한 행이며 실제 내용은 `Payload` 열에 있습니다. 알림을 보낼 수 있는 앱의 목록은 `NotificationHandler` 표에 있고 `PrimaryId` 열이 앱 이름을 보여 줍니다. 알림 종류에는 토스트 (toast), 타일 (tile), 배지 (badge) 가 있습니다.

알림에는 팝업 메시지나 앱의 글 일부가 들어 있을 수 있어서, 원본이 지워진 뒤에도 알림에서 내용을 되찾을 수 있습니다.

## 위치와 버전별 차이

### 위치

- 사용자마다 `%LOCALAPPDATA%\Microsoft\Windows\Notifications\wpndatabase.db` 가 있습니다.
- `%APPDATA%\Local\Microsoft\Windows\Notifications\wpndatabase.db` 로 적힌 경로도 `%LOCALAPPDATA%` 와 같은 폴더를 가리킵니다[1].
- 같은 폴더에 `wpndatabase.db-wal`, `wpndatabase.db-shm`, `WPNPRMRY.tmp`(0바이트), 빈 `wpnidm` 폴더가 함께 있을 수 있습니다.
- 프로필 폴더가 어느 계정의 것인지는 [사용자 프로필 목록](../system-account/profilelist.md) 으로 확인합니다.

### Windows 버전

| Windows | 달라지는 점 | 참고 |
|---|---|---|
| Windows 10 (10.0.10240.0) | 토스트 알림 API (`ToastNotification` 클래스) 의 지원 시작 빌드입니다 | [2] |
| Windows 10 1607 이전 | DB 형식이 SQLite 가 아니었습니다 | [1] |
| Windows 10 1607 이후 | SQLite 형식입니다 | [1] |
| Windows 10 1607 | API 에 `NotificationMirroring`·`RemoteId` 가 추가됩니다 | [2] |
| Windows 10 1703 | API 에 `Data`·`Priority` 가 추가됩니다 | [2] |
| Windows 10 1903 | API 에 `ExpiresOnReboot` 이 추가됩니다 | [2] |
| Windows 11 25H2 | 아래 "구조" 의 표와 열이 있습니다 | |

- 1607 이전 기기에서는 `%LOCALAPPDATA%\Microsoft\Windows\Notifications\` 폴더의 파일을 찾아 파일 헤더와 표 구조를 먼저 확인합니다.

## 구조

저장 형식은 SQLite 입니다. 페이지와 레코드, `-wal` 파일을 읽는 법은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

- 헤더의 오프셋 18·19 바이트가 모두 2 이면 WAL 모드입니다. Windows 11 25H2 의 파일은 WAL 모드였고 페이지 크기는 4096 이었습니다.

### 표

표와 열 이름은 Windows 11 25H2 의 스키마입니다.

| 표 | 열 |
|---|---|
| `Notification` | `Order`, `Id`, `HandlerId`, `ActivityId`, `Type`, `Payload`, `Tag`, `Group`, `ExpiryTime`, `ArrivalTime`, `DataVersion`, `PayloadType`, `BootId`, `ExpiresOnReboot` |
| `NotificationHandler` | `RecordId`, `PrimaryId`, `WNSId`, `HandlerType`, `WNFEventName`, `SystemDataPropertySet`, `CreatedTime`, `ModifiedTime`, `ParentId`, `ContainerSid` |
| `HandlerAssets` | `HandlerId`, `AssetKey`, `AssetValue` |
| `HandlerSettings` | `HandlerId`, `SettingKey`, `Value` |
| `Metadata` | `Key`, `Value` |
| `NotificationData` | `NotificationId`, `Key`, `Value` |
| `TimedNotification` | `TimerEventId`, `BBIWorkId`, `WnfStateName`, `HandlerId`, `NotificationType`, `Url` |
| `TransientTable` | `OfflineCacheCount`, `NotificationId`, `OfflineBundleId`, `ServerCacheRollover`, `CrossDeviceMatchId`, `SuppressPopup`, `IsMirroringDisabled`, `RecurrenceId`, `MessageId`, `Priority`, `CV` |
| `WNSPushChannel` | `ChannelId`, `HandlerId`, `Uri`, `ExpiryTime`, `CreatedTime`, `DeviceVersion` |

### `Notification` 의 주요 열

| 열 | 뜻 |
|---|---|
| `Order` | 기본 키입니다 |
| `Id` | 겹치지 않는 값입니다 (UNIQUE) |
| `HandlerId` | `NotificationHandler.RecordId` 를 가리킵니다 |
| `Type` | 알림 종류입니다. 한 예에서 `toast` 5건, `tile` 5건, `badge` 1건이 있었습니다 |
| `Payload` | 알림의 실제 내용입니다. BLOB 에 XML 문자열이 들어 있습니다 |
| `PayloadType` | `Xml` 입니다 |
| `ArrivalTime` | 알림을 받은 시각입니다. FILETIME 입니다 |
| `ExpiryTime` | 알림이 DB 에서 지워질 시각입니다. FILETIME 입니다 |
| `Tag`, `Group`, `ExpiresOnReboot` | API 의 같은 이름 속성과 이름이 같습니다 (아래 표) |

`ActivityId`, `DataVersion`, `BootId` 는 뜻을 단정할 수 없어 보고서에는 값만 옮깁니다.

### `NotificationHandler` 의 주요 열

| 열 | 뜻 |
|---|---|
| `RecordId` | 기본 키입니다. `Notification.HandlerId` 가 이 값을 가리킵니다 |
| `PrimaryId` | 앱 이름을 보여 줍니다. 스토어 앱은 `패키지 패밀리 이름!App` 모양, 데스크톱 앱은 실행 파일 경로나 짧은 이름입니다 |
| `HandlerType` | `app:desktop` 11개, `app:immersive` 222개, `app:system` 73개가 있었습니다 |
| `CreatedTime`, `ModifiedTime` | `YYYY-MM-DD HH:MM:SS` 모양 글자입니다. FILETIME 이 아닙니다 |

나머지 열은 뜻을 단정하지 않고 값만 옮깁니다.

### 나머지 표의 값

아래는 Windows 11 25H2 PC 한 대의 값입니다.

- `HandlerAssets` 의 키는 `DisplayName`, `IconUri`, `LaunchArgs` 였습니다.
- `HandlerSettings` 에는 앱마다 `s:toast`, `s:banner`, `s:audio`, `s:lock:toast`, `s:badge`, `s:tile`, `c:toast` 같은 설정 키가 있었습니다. 핸들러 306개에 키가 약 20개씩이었습니다. 키마다의 뜻은 시험 기기에서 앱의 알림 설정을 바꾸고 값이 어떻게 달라지는지 봐서 확인합니다.
- `Metadata` 값은 아래와 같았습니다.

| 키 | 값 |
|---|---|
| `toast:maxCount` | 20 |
| `tile:maxCount` | 5 |
| `badge:maxCount` | 1 |
| `toastCondensed:maxCount` | 80 |
| `raw:maxCount` | 5 |
| `CurrentNotificationId` | 3348 |

- `WNSPushChannel` 의 `ExpiryTime`·`CreatedTime` 도 FILETIME 이었습니다. 채널 6개 모두 만료가 생성 30일 뒤였습니다.
- `WNSPushChannel.Uri` 를 푸시 알림 서버 주소로 단정하지 않습니다.

### 알림 내용 (Payload)

토스트 알림의 XML 요소는 `toast`, `visual`, `binding`, `text`, `image`, `actions`, `action` 입니다. 아래는 이 요소 이름으로 만든 뼈대입니다. 특정 기기에서 나온 값이 아니고, 실제 속성은 더 많습니다.

```xml
<toast launch="(사이트 주소)">
  <visual>
    <binding>
      <text>(제목)</text>
      <text>(본문)</text>
      <image src="file:///(경로)"/>
    </binding>
  </visual>
  <actions>
    <action/>
  </actions>
</toast>
```

- `image` 의 `src` 는 `file:` 주소였습니다.
- 브라우저가 띄운 웹 알림은 `toast` 의 `launch` 속성에 사이트 주소가 들어 있었습니다.

### 알림 API 와 DB 열

`ToastNotification` 속성[2]과 이름이 같거나 비슷한 DB 열입니다. 이름이 비슷하다고 속성 값이 그 열에 그대로 들어간다고 단정하지 않습니다.

| API 속성 | 뜻 | 이름이 같거나 비슷한 DB 열 |
|---|---|---|
| `ExpirationTime` | 이 시각 뒤에는 알림을 보여 주지 않습니다 | `Notification.ExpiryTime` |
| `ExpiresOnReboot` | 재부팅 뒤 알림 센터에 남는지 정합니다 | `Notification.ExpiresOnReboot` |
| `Group` | 알림 그룹 식별자입니다 | `Notification.Group` |
| `Tag` | 그룹 안에서 이 알림의 고유 식별자입니다 | `Notification.Tag` |
| `SuppressPopup` | 화면에 팝업을 띄울지 정합니다 | `TransientTable.SuppressPopup` |
| `Priority` | 우선순위입니다 | `TransientTable.Priority` |
| `NotificationMirroring` | 다른 기기로 복제를 허용할지 정합니다 | `TransientTable.IsMirroringDisabled` |
| `RemoteId` | 다른 기기의 알림과 짝짓는 ID 입니다 | — |
| `Data` | 알림 상태에 대한 추가 정보입니다 | — |

- 알림이 만료되거나 사용자가 닫아 화면에서 사라지면 `Dismissed` 이벤트가 일어납니다.

## 증거로서 의미

### 증명하는 것

- `Notification` 의 한 행은 이 사용자에게 `PrimaryId` 의 앱이 `ArrivalTime` 에 알림을 보낸 기록입니다.
- `Payload` 는 그 알림에 보인 글과 그림 경로입니다.
- 웹 알림이면 `launch` 속성으로 알림을 보낸 사이트를 알 수 있습니다.
- `NotificationHandler` 는 이 사용자 환경에서 알림 핸들러로 등록된 앱 목록입니다.

### 증명하지 못하는 것

- 사용자가 알림을 보았는지, 눌렀는지는 알 수 없습니다.
- 알림을 닫으면 DB 에서 바로 지워지는지는 시험 기기에서 재현해 확인합니다. 행이 없다고 알림을 받지 않은 것은 아닙니다.
- 지난 알림은 대부분 남지 않습니다. 한 예에서 `Notification` 표에는 11행만 있었는데 `CurrentNotificationId` 는 3348 이었습니다.
- 알림은 원본 메시지의 일부일 수 있습니다. 원본 전체를 알려 주지 않습니다.
- 핸들러로 등록된 앱을 사용자가 실행했다고 단정할 수 없습니다.

보고서에는 "그 메시지를 받아 읽었다" 대신 "사용자 X 의 `wpndatabase.db` 에 앱 Y 의 토스트 알림이 있다. 받은 시각은 A(UTC) 이고, 내용에 '...' 가 적혀 있다" 처럼 씁니다.

## 시각 해석

| 열 | 형식 | 비고 |
|---|---|---|
| `Notification.ArrivalTime` | FILETIME | 받은 시각입니다. UTC 로 풀면 `-wal` 파일의 수정 시각 (UTC) 과 몇 분 차이로 맞아 UTC 로 보입니다 |
| `Notification.ExpiryTime` | FILETIME | DB 에서 지워질 시각입니다. 타일과 배지는 0 이었습니다 |
| `NotificationHandler.CreatedTime`, `ModifiedTime` | `YYYY-MM-DD HH:MM:SS` 글자 | 시간대는 같은 기기의 다른 기록과 시각을 맞춰 확인합니다 |
| `WNSPushChannel.ExpiryTime`, `CreatedTime` | FILETIME | 만료가 생성 30일 뒤였습니다 |

- 변환식은 `(값 ÷ 10000000) − 11644473600 = 유닉스 시간` 입니다[1].
- 한 예에서 토스트 5건은 모두 `ExpiryTime − ArrivalTime` 이 정확히 72시간 (3일) 이었습니다. 3일을 기본값으로 단정하지 않습니다.
- FILETIME 의 뜻과 다른 형식은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.
- 알림 시각을 다른 기록과 한 시간 축에 놓는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 을 따릅니다.

## 함정과 한계

- **세 파일을 함께 수집합니다.** `-wal` 파일은 DB 파일보다 늦게 바뀔 수 있고, 사본을 뜨는 몇 분 사이에 70KB 에서 1.5MB 로 커진 예도 있습니다. 최근 알림은 `-wal` 에만 있을 수 있습니다. `wpndatabase.db`, `-wal`, `-shm` 을 함께 뜹니다.
- **원본을 열지 않습니다.** SQLite 도구로 열면 `-wal` 의 내용이 DB 파일로 옮겨질 수 있습니다. 해시를 기록한 사본으로 작업합니다. [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 를 참고합니다.
- **행이 적은 것이 정상일 수 있습니다.** 알림은 만료되면 지워집니다. 과거 알림은 섀도 복사본 속 옛 파일에서 찾습니다. [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 을 참고합니다.
- **지운 행.** 빈 페이지 (freelist) 가 있을 수 있습니다(한 예에서 202페이지 가운데 5페이지). 지운 행을 되살릴 수 있는지는 실제 데이터로 확인합니다. 찾는 법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.
- **시각 형식이 표마다 다릅니다.** `NotificationHandler` 의 시각은 글자이고 시간대를 모릅니다. FILETIME 열과 같은 방법으로 풀지 않습니다.
- **`Payload` 는 BLOB 입니다.** 뷰어가 헥스로만 보여 줄 수 있습니다. 글자로 바꿔 읽습니다. 글자가 깨지면 문자 인코딩을 헥스로 확인합니다.
- **API 이름과 DB 열을 섞어 쓰지 않습니다.** 이름이 같아도 뜻이 같다는 근거는 없습니다. 보고서에는 DB 열 이름을 씁니다.
- **개인정보가 평문으로 나옵니다.** 메시지 일부, 사이트 주소, 파일 경로가 들어 있을 수 있습니다. 보고서에는 필요한 만큼만 옮깁니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 FILETIME 규칙과 변환식[1]으로 만든 예시입니다. 특정 기기에서 나온 값이 아닙니다.

```
ArrivalTime = 133549686000000000
133549686000000000 ÷ 10,000,000 − 11644473600 = 1710495000 → 2024-03-15 09:30:00 UTC

ExpiryTime  = 133552278000000000 → 2024-03-18 09:30:00 UTC
ExpiryTime − ArrivalTime = 2,592,000,000,000 (100나노초 단위) = 259,200초 = 72시간
```

- SQLite 레코드 안에서 이 정수를 찾는 법은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

DB 파일 헤더에서 WAL 모드를 확인합니다.

```
오프셋 0x12 (18)  02
오프셋 0x13 (19)  02    → 두 바이트가 모두 2 이면 WAL 모드
```

### 공개 도구로 한 번

세 파일을 같은 폴더에 사본으로 뜬 뒤, 사본을 SQLite 명령줄 도구로 엽니다. `Order`·`Group`·`Key` 는 SQL 키워드와 겹치므로 큰따옴표로 감쌉니다.

```sql
SELECT n."Order", n.Type, h.PrimaryId,
       datetime(n.ArrivalTime / 10000000 - 11644473600, 'unixepoch') AS arrival_utc,
       CASE WHEN n.ExpiryTime = 0 THEN NULL
            ELSE datetime(n.ExpiryTime / 10000000 - 11644473600, 'unixepoch')
       END AS expiry_utc,
       n.Tag, n."Group",
       CAST(n.Payload AS TEXT) AS payload_xml
FROM Notification n
LEFT JOIN NotificationHandler h ON h.RecordId = n.HandlerId
ORDER BY n.ArrivalTime;
```

알림 핸들러 목록과 표시 이름을 뽑습니다.

```sql
SELECT h.RecordId, h.PrimaryId, h.HandlerType,
       h.CreatedTime, h.ModifiedTime,
       a.AssetValue AS display_name
FROM NotificationHandler h
LEFT JOIN HandlerAssets a
       ON a.HandlerId = h.RecordId AND a.AssetKey = 'DisplayName'
ORDER BY h.ModifiedTime;

SELECT "Key", Value FROM Metadata;
```

- DB Browser for SQLite 같은 범용 뷰어로도 같은 표를 볼 수 있습니다. 알림 전용 공개 도구의 결과는 위 조회 결과와 한 번 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 크롬 계열 브라우저 | 웹 알림을 보낸 사이트의 방문 기록 | [크롬 계열 브라우저](../browsers/chrome-edge-whale/index.md) |
| 스토어 앱 설치 목록 | `PrimaryId` 의 패키지 패밀리 이름으로 앱 확인 | [스토어 앱 설치 목록](../system-account/appx-staterepository.md) |
| 윈도 타임라인 | 같은 알림이 있는지 | [윈도 타임라인](../file-folder-usage/activitiescache-db.md) |
| 메신저·메일 앱 | 알림 내용과 원본 메시지 | [카카오톡 PC](../messengers/kakaotalk-pc/index.md), [마이크로소프트 팀즈](../messengers/teams.md) |
| 섀도 복사본 | 만료로 지워진 옛 알림 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

연락 내용을 엮는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에 있습니다.

## 실습

Windows 10 1607 이후 공개 데이터 세트(NIST CFReDS 등)에서 사용자의 `Notifications` 폴더를 통째로 꺼내 풀어 봅니다.

1. `wpndatabase.db` 옆에 `-wal`·`-shm` 파일이 있습니까? 각 파일의 크기와 수정 시각은 무엇입니까?
2. `Notification` 표에 행이 몇 개 있습니까? `Metadata` 의 `CurrentNotificationId` 와 비교하면 몇 건이 남지 않았습니까?
3. 토스트 알림 하나를 골라 `ArrivalTime` 을 UTC 로 풉니다. `ExpiryTime − ArrivalTime` 은 얼마입니까?
4. 웹 알림이 있습니까? `launch` 속성의 사이트 주소가 브라우저 방문 기록에도 있습니까?
5. `NotificationHandler` 에서 `HandlerType` 별로 앱 수를 셉니다. 데스크톱 앱 가운데 설치 프로그램 목록에 없는 것이 있습니까?

## 참고 문헌

1. inc0x0, *Windows 10 Notification Database* (2018-10-09 — 파일 위치, SQLite 형식과 1607 이전 차이, `Notification`·`NotificationHandler` 연결, `Payload`, `ArrivalTime`·`ExpiryTime` 과 변환식, 조사 가치). https://inc0x0.com/2018/10/windows-10-notification-database/
2. Microsoft Learn, *ToastNotification Class (Windows.UI.Notifications)* (지원 버전, 속성의 뜻과 추가된 버전, `Dismissed` 이벤트). https://learn.microsoft.com/en-us/uwp/api/windows.ui.notifications.toastnotification
