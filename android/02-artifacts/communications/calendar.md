---
title: "캘린더"
parent: "아티팩트 · 통화·문자·연락처"
nav_order: 620
---

# 캘린더 (calendar.db)

안드로이드 캘린더 제공자는 `calendar.db` 라는 SQLite 데이터베이스에 계정별 캘린더, 일정, 참석자, 알림 설정을 저장하고, 일정의 시작·종료 시각은 UTC 기준 유닉스 밀리초로 넣습니다. 서버와 동기화된 일정을 앱에서 지우면 행이 바로 없어지지 않고, `deleted` 열이 1 로 바뀐 채 동기화 어댑터가 서버에 반영할 때까지 남습니다. 약속 장소·시각·초대된 사람을 확인할 때 연락 기록과 함께 봅니다.

## 무엇을 기록하나 · 왜 생기나

캘린더 앱이나 동기화 어댑터(sync adapter)가 캘린더 제공자(Calendar Provider)에 일정을 넣으면 제공자가 이 데이터베이스에 씁니다. 한 사용자가 캘린더를 여러 개 둘 수 있고, 캘린더마다 구글 캘린더·Exchange 같은 다른 종류의 계정에 묶일 수 있습니다[3]. 동기화 어댑터는 기기의 캘린더 데이터를 서버와 맞추는 구성 요소이고, 캘린더·일정 표에는 동기화 어댑터만 쓰는 열이 따로 있습니다[3].

| 표 | 담는 것 |
|---|---|
| `Calendars` | 캘린더 하나의 이름·색·계정·동기화 정보[3] |
| `Events` | 일정 하나의 제목·장소·시작·종료 시각. 반복 일정도 한 행입니다[3] |
| `Instances` | 일정이 실제로 열리는 회차마다 한 행. 반복 일정은 회차 수만큼 행이 생깁니다[3] |
| `Attendees` | 일정에 초대된 참석자 한 명과 그 응답[3] |
| `Reminders` | 일정의 알림 설정 하나. 몇 분 전에 어떤 방법으로 알릴지[3] |
| `CalendarAlerts` | 이미 예약되었거나 울린 알림[4][5] |

AOSP 소스에는 이 밖에도 `EventsRawTimes`·`ExtendedProperties`·`CalendarMetaData`·`CalendarCache`·`Colors` 표가 정의되어 있습니다[5].

## 위치와 버전별 차이

데이터베이스 파일은 캘린더 제공자 패키지의 데이터 폴더 아래 `com.android.providers.calendar/databases/calendar.db` 에 있습니다[1][2]. ALEAPP 시험 데이터에는 Android 10(Galaxy S10)부터 Android 16(Pixel 8 Pro)까지 픽셀·삼성·포코 기기에서 뽑은 이 파일이 들어 있습니다[1]. 앱 데이터 폴더 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 를 봅니다.

| 항목 | 내용 | 근거 |
|---|---|---|
| 제공자 데이터베이스 | `com.android.providers.calendar/databases/calendar.db` | [1][2] |
| 데이터베이스 버전 | 601 (AOSP main). 기기마다 다를 수 있음 | [5] |
| `mutators` 열 | 데이터베이스 버전 600(KitKat, Android 4.4)에서 `Events`·`Calendars` 에 추가 | [5] |
| 구글 캘린더 앱 자체 저장소 | `com.google.android.calendar/databases/cal_v2a` | [1][2] |

구글 캘린더 앱은 제공자와 별도로 `cal_v2a` 라는 SQLite 데이터베이스를 따로 둡니다[1][2]. 이 파일의 `Events` 표는 일정 내용을 `Proto` 열에 프로토콜 버퍼로 넣고, 계정은 `Accounts` 표의 `PlatformAccountName` 과 이어 붙여야 나옵니다[1]. ALEAPP 는 이 프로토콜 버퍼에서 6번 필드를 제목, 7번을 설명, 3번을 일정 웹 링크, 19번을 iCal UID 로 읽고, 4번과 5번 필드를 만든 시각·고친 시각으로 읽습니다[1]. `Events` 표에는 `ToBeRemoved` 열도 있고, 오래된 앱 버전에는 `EventType` 열이 없습니다[1]. 프로토콜 버퍼 읽는 법은 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 에 있습니다.

`calendar.db` 만 떼어 오지 말고 `-wal`·`-shm` 파일을 함께 수집합니다. ALEAPP 도 `calendar.db*` 형식으로 딸린 파일까지 찾습니다[1].

## 구조

아래 열 이름은 `CalendarContract` 에 정의된 실제 열 문자열입니다[4]. 기기마다 열이 더 있을 수 있으니 `PRAGMA table_info(Events)` 로 먼저 확인합니다.

| 표 | 주요 열 |
|---|---|
| `Calendars` | `_id`, `name`, `calendar_displayName`, `account_name`, `account_type`, `ownerAccount`, `visible`, `sync_events`, `_sync_id`, `dirty`, `mutators`, `deleted`, `cal_sync1`~`cal_sync10` |
| `Events` | `_id`, `calendar_id`, `title`, `description`, `eventLocation`, `dtstart`, `dtend`, `duration`, `eventTimezone`, `eventEndTimezone`, `allDay`, `rrule`, `rdate`, `lastDate`, `organizer`, `hasAlarm`, `eventStatus`, `selfAttendeeStatus`, `_sync_id`, `dirty`, `mutators`, `deleted`, `lastSynced`, `original_id`, `original_sync_id`, `uid2445` |
| `Attendees` | `_id`, `event_id`, `attendeeName`, `attendeeEmail`, `attendeeStatus`, `attendeeRelationship`, `attendeeType`, `attendeeIdentity`, `attendeeIdNamespace` |
| `Reminders` | `_id`, `event_id`, `minutes`, `method` |
| `CalendarAlerts` | `_id`, `event_id`, `begin`, `end`, `alarmTime`, `creationTime`, `receivedTime`, `notifyTime`, `state`, `minutes` |

`Events` 의 `_id` 는 `INTEGER PRIMARY KEY AUTOINCREMENT` 라서 지운 번호를 다시 쓰지 않습니다[5]. 그래서 번호가 비어 있으면 그 사이에 행이 지워졌다는 단서가 되고, `sqlite_sequence` 표에서 지금까지 쓴 가장 큰 번호를 확인할 수 있습니다. 다만 빈 번호가 모두 사용자가 지운 일정은 아닙니다. 아래 "수정과 삭제 표시" 에 적은 고치기 전 복사본도 `Events` 행 번호를 쓰고, 동기화가 끝나면 지워집니다[5][6]. `Attendees`·`Reminders`·`CalendarAlerts` 의 `event_id` 는 `Events` 의 `_id` 를 가리키고, `Events` 의 `calendar_id` 는 `Calendars` 의 `_id` 를 가리킵니다[3][4]. 숫자로 들어가는 열의 뜻은 아래와 같습니다[4].

| 열 | 값 |
|---|---|
| `attendeeStatus` | 0 없음, 1 수락, 2 거절, 3 초대됨, 4 미정 |
| `attendeeRelationship` | 0 없음, 1 참석자, 2 주최자, 3 공연자, 4 발표자 |
| `attendeeType` | 0 없음, 1 필수, 2 선택, 3 자원(회의실 등) |
| `eventStatus` | 0 미정, 1 확정, 2 취소 |
| `method` (알림) | 0 기본, 1 화면 알림, 2 이메일, 3 SMS, 4 알람 |
| `state` (울린 알림) | 0 예약됨, 1 울림, 2 닫음 |

`Reminders` 의 `minutes` 는 일정 시작 몇 분 전에 알릴지를 뜻합니다[3].

### 계정과 동기화

캘린더는 `account_name` 과 `account_type` 두 열을 함께 봐야 어느 계정의 것인지 알 수 있습니다[3]. `account_type` 은 그 행을 기기에 동기화한 계정의 종류입니다[4]. 기기 계정과 묶이지 않은 캘린더는 `account_type` 이 `LOCAL` 이고 동기화되지 않습니다[3][4]. `_sync_id` 는 동기화 서버가 붙인 고유 ID 이고, 한 번도 동기화되지 않은 행은 NULL 입니다[4].

기기에서 계정이 지워지면 제공자는 `LOCAL` 이 아니면서 기기에 없는 계정의 캘린더 행을 지우고, 트리거가 그 캘린더의 일정 행까지 지웁니다[5][6]. 그래서 계정을 뺀 기기에서는 그 계정의 일정이 표에 남지 않고, SQLite 의 빈 페이지나 WAL 에 조각만 남을 수 있습니다. 계정 추가·삭제 기록은 [계정](../system-account/accounts/index.md) 에서 봅니다.

### 수정과 삭제 표시

동기화 어댑터가 아닌 앱이 일정을 넣거나 고치거나 지우면 제공자가 `dirty` 를 1 로 바꾸고 `mutators` 열에 요청한 앱의 패키지 이름을 적습니다[6]. 일정 행 자체를 바꿀 때는 이 열을 그 앱 이름 하나로 새로 쓰고, 참석자·알림·확장 속성 행을 더할 때는 이미 적힌 이름 뒤에 쉼표로 이어 붙입니다(같은 이름이 있으면 더하지 않습니다)[6]. 동기화 어댑터가 서버와 맞춘 뒤 `dirty` 를 0 으로 되돌리면 `mutators` 도 비웁니다[6]. 그래서 `dirty` 가 1 인 행의 `mutators` 에는 마지막 동기화 뒤에 그 일정을 마지막으로 고친 앱과, 그 뒤 참석자·알림을 더한 앱이 남습니다. 그 사이에 일정을 고친 다른 앱은 남지 않을 수 있습니다.

일정을 지울 때는 행에 따라 처리가 다릅니다[3][6].

| 지우는 쪽과 대상 | 제공자가 하는 일 |
|---|---|
| 앱이 동기화된 일정(`_sync_id` 있음)을 지움 | `deleted`·`dirty` 를 1 로 바꾸고 `mutators` 를 지운 앱의 패키지 이름으로 새로 씁니다. `Instances`·`Reminders`·`CalendarAlerts`·`ExtendedProperties` 행은 바로 지우고, `Attendees` 행은 취소 통보를 위해 남깁니다 |
| 앱이 동기화 안 된 일정(`_sync_id` 없음)을 지움 | 일정 행을 바로 지우고, 트리거가 딸린 행을 모두 지웁니다 |
| 동기화 어댑터가 지움 | 일정 행을 바로 지우고, 트리거가 딸린 행을 모두 지웁니다 |

캘린더가 부분 수정(`canPartiallyUpdate`)을 허용하면, 동기화 뒤 사용자가 처음 고칠 때 제공자가 고치기 전 일정을 새 행으로 복사해 둡니다[5][6]. 이 복사본은 `dirty` 0, `lastSynced` 1 로 들어가고, 동기화 어댑터가 원래 행의 `dirty` 를 0 으로 되돌릴 때 지워집니다[5][6]. 동기화 전에 수집한 데이터에서는 이 행으로 고치기 전 제목·시각을 볼 수 있습니다.

## 증거로서 의미

**증명하는 것.** `Events` 행은 수집 시점에 그 계정의 캘린더에 해당 제목·장소·시각의 일정이 들어 있었다는 기록입니다. `Attendees` 로 누가 초대되었고 어떻게 응답했는지를, `organizer` 로 일정 주최자(소유자)의 이메일을 확인할 수 있습니다[3]. `deleted` 가 1 인 행은 마지막 동기화 뒤에 기기에서 지우라는 요청이 있었고 아직 서버에 반영되지 않았다는 뜻이고, 그 행의 `mutators` 에 지운 앱의 패키지 이름이 남습니다[6]. `CalendarAlerts` 의 `state` 와 `receivedTime`·`notifyTime` 은 알림이 실제로 울렸는지, 사용자가 닫았는지를 보여 줍니다[4].

**증명하지 못하는 것.** 일정이 있다고 그 약속에 실제로 갔다는 뜻은 아닙니다. 초대받은 일정은 다른 사람이 만든 일정이 동기화로 들어온 것일 수 있으므로 `organizer`·`ownerAccount`·`selfAttendeeStatus` 를 함께 봅니다. 제공자의 `Events` 표에는 일정을 처음 만든 시각 열이 없어서 언제 일정을 넣었는지는 이 표만으로 알 수 없습니다. 동기화가 끝나면 지운 일정의 행 자체가 사라지고 동기화 안 된 일정은 처음부터 바로 지워지므로, `deleted` 표시가 없다고 지운 일정이 없었다고 볼 수 없습니다[6].

## 시각 해석

`dtstart`·`dtend` 는 UTC 기준 유닉스 밀리초이고[3][4], 반복 일정의 마지막 날짜 `lastDate` 도 같은 단위입니다[4]. `Instances` 의 `begin`·`end` 도 UTC 밀리초이고, `startDay`·`endDay` 는 캘린더 시간대 기준의 율리우스 일(Julian day), `startMinute`·`endMinute` 는 그 시간대 자정부터 센 분입니다[3]. `CalendarAlerts` 의 `alarmTime`·`creationTime`·`receivedTime`·`notifyTime` 도 모두 UTC 밀리초입니다[4][5]. `eventTimezone` 에는 그 일정에 지정된 시간대 이름이 들어갑니다[3]. 일정이 어느 시간대 기준으로 잡혔는지는 이 값으로 보고, 사용자 화면에 보였을 시각은 기기 시간대로 바꿔 봅니다.

예를 들어 `dtstart` 가 1740902400000 이면 2025-03-02 08:00:00 UTC 이고, `eventTimezone` 이 `Asia/Seoul` 이면 현지 시각 17:00 입니다(만든 예시). 종일 일정(`allDay` 1)은 `eventTimezone` 이 `UTC` 이고 시각이 자정에 맞춰져야 합니다[4]. 그래서 `dtstart` 가 1740873600000(2025-03-02 00:00 UTC)인 종일 일정은 "3월 2일 하루" 로 읽어야 하고, 한국 시각으로 바꿔 "3월 2일 오전 9시" 로 쓰면 틀립니다(만든 예시).

일정 시각은 사용자가 약속으로 정한 시각이지 기기가 무언가를 한 시각이 아닙니다. 반면 `CalendarAlerts` 의 `creationTime`·`receivedTime`·`notifyTime` 은 기기가 그 일을 한 시각이라, 기기 시계가 틀려 있었다면 그만큼 어긋납니다[4]. 변환 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을, 기기 시간대는 [시간대와 시각 설정](../system-account/time-zone.md) 을 봅니다.

## 함정과 한계

ALEAPP 는 `Calendars` 의 `cal_sync8` 열을 캘린더를 만든 시각으로 읽어 밀리초로 바꿉니다[1]. AOSP 에서 `cal_sync8` 은 동기화 어댑터용 일반 열로만 정의되어 있어서[4], 이 해석은 특정 동기화 어댑터(구글 계정 등)에 한정될 가능성이 있습니다. 보고서에 쓰기 전에 다른 기록과 맞춰 봅니다.

제공자 `calendar.db` 와 구글 캘린더 앱의 `cal_v2a` 는 따로 저장되므로[1], 한쪽에 없는 일정이 다른 쪽에 있을 수 있습니다. ALEAPP 시험 데이터에서도 같은 기기의 두 파일 행 수가 다릅니다(Poco X7 Android 15 에서 제공자 62행, 앱 190행)[1]. 두 파일을 모두 수집하고 제목·시작 시각으로 같은 일정을 맞춰 본 뒤, 제공자의 `uid2445` 와 앱의 iCal UID 가 같은 값인지 확인합니다.

`Instances` 표는 앱이 조회한 기간 앞뒤로 제공자가 반복 일정을 펼쳐 채우는 표이고, 시간대가 바뀌면 행을 모두 지우고 다시 만듭니다[6]. 그래서 반복 일정의 모든 회차가 들어 있다고 볼 수 없고, 반복 일정은 `Events` 의 `rrule`·`rdate`·`duration` 을 기준으로 해석합니다[3]. 지워진 행 복구 원리는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에, 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래 바이트는 SQLite 레코드 형식 명세와 AOSP 의 `Reminders` 표 정의로 만든 예시이고, 실제 기기에서 가져온 값이 아닙니다. 첫 열 `_id` 는 `INTEGER PRIMARY KEY` 라서 rowid 와 같고 레코드 본문에는 NULL 로 들어갑니다[5].

```text
07                    페이로드 길이 7바이트
07                    rowid = 7 (_id)
05                    레코드 헤더 길이 5바이트
00                    열1 _id: 직렬 형식 0 (NULL, 값은 rowid)
01                    열2 event_id: 직렬 형식 1 (1바이트 정수)
01                    열3 minutes: 직렬 형식 1 (1바이트 정수)
09                    열4 method: 직렬 형식 9 (정수 1, 본문 없음)
2A                    event_id = 42
0F                    minutes = 15
                      → 일정 42번, 15분 전, 화면 알림(1)
```

**공개 도구로 한 번.** SQLite 명령줄 도구(sqlite3)로 사본을 열어 열 이름부터 확인하고, 일정과 캘린더 계정을 이어 붙여 읽습니다. ALEAPP 도 같은 방식으로 `Events` 와 `Calendars` 를 이어 붙입니다[1].

```sql
PRAGMA table_info(Events);
SELECT e._id, c.account_name, c.account_type, e.title, e.eventLocation,
       datetime(e.dtstart/1000, 'unixepoch') AS start_utc,
       datetime(e.dtend/1000, 'unixepoch')   AS end_utc,
       e.eventTimezone, e.allDay, e.organizer,
       e._sync_id, e.dirty, e.deleted, e.mutators, e.lastSynced
FROM Events e LEFT JOIN Calendars c ON c._id = e.calendar_id
ORDER BY e.dtstart;

SELECT event_id, attendeeName, attendeeEmail, attendeeStatus, attendeeRelationship
FROM Attendees ORDER BY event_id;
```

지운 표시만 남은 일정은 `WHERE e.deleted = 1` 로, 동기화 전에 고친 일정은 `WHERE e.dirty = 1` 로 골라냅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [계정](../system-account/accounts/index.md) | 캘린더의 `account_name`·`account_type` 이 기기에 등록된 계정인지, 계정을 언제 추가·삭제했는지 |
| [연락처](contacts.md) | 참석자 이메일과 연락처에 저장된 이름 |
| [통화 기록](call-log.md) · [문자](messages/index.md) | 일정 앞뒤로 참석자와 주고받은 연락 |
| [알림 기록](../app-usage/notification-history.md) | 캘린더 알림이 실제로 화면에 떴는지 |
| [구글 위치 기록과 타임라인](../location/google-timeline.md) | 일정 장소에 실제로 있었는지 |

연락 관계를 정리하는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 에 있습니다.

## 실습

NIST CFReDS 같은 곳에서 구할 수 있는 공개 안드로이드 증거물 이미지로 아래 질문을 풀어 봅니다.

1. `.tables` 결과를 위 표 목록과 비교하고, `PRAGMA table_info(Events)` 로 `mutators`·`lastSynced` 열이 있는지 확인합니다.
2. `Calendars` 의 `account_type` 별로 캘린더 수를 세고, `LOCAL` 캘린더가 있는지 봅니다.
3. `deleted` 가 1 이거나 `dirty` 가 1 인 일정을 뽑고, `mutators` 에 어떤 패키지가 적혔는지 봅니다.
4. 종일 일정 하나를 골라 `dtstart` 가 UTC 자정인지 확인하고, 날짜로만 읽습니다.
5. 구글 캘린더 앱의 `cal_v2a` 가 있으면 두 파일의 일정 수와 제목을 비교합니다.

## 참고 문헌

1. ALEAPP, scripts/artifacts/googleCalendar.py (main) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/googleCalendar.py
2. Mattia Epifani, "A first look at Android 14 forensics", 2024-01-18 — https://blog.digital-forensics.it/2024/01/a-first-look-at-android-14-forensics.html
3. Android Developers, Calendar provider overview — https://developer.android.com/identity/providers/calendar-provider
4. CalendarContract.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/provider/CalendarContract.java
5. CalendarDatabaseHelper.java — AOSP CalendarProvider (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_packages_providers_calendarprovider/main/src/com/android/providers/calendar/CalendarDatabaseHelper.java
6. CalendarProvider2.java — AOSP CalendarProvider (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_packages_providers_calendarprovider/main/src/com/android/providers/calendar/CalendarProvider2.java
