---
title: "미리 알림과 캘린더"
parent: "아티팩트 · 메일·클라우드·애플 앱"
nav_order: 1010
---

# 미리 알림과 캘린더 (Reminders·Calendar)

## 한 줄 요약

캘린더 일정은 `HomeDomain` 의 `Library/Calendar/Calendar.sqlitedb` 에, 미리 알림은 앱 그룹 `group.com.apple.reminders` 의 `Container_v#/Stores/` 아래 SQLite DB 에 따로 남고, 두 DB 모두 시각을 Mac 절대 시각(2001-01-01 기준 초)으로 읽습니다.

## 무엇을 기록하나 · 왜 생기나

캘린더 DB 에는 사용자가 만든 일정뿐 아니라 초대받은 일정, 구독한 캘린더, 생일 일정, 일정의 장소·참석자·첨부까지 들어가고, 공개 도구 iLEAPP 는 이 DB 에서 `calendarEvents`, `calendarBirthdays`, `calendarList` 세 보고서를 만듭니다 [1]. 관찰한 DB 에는 일정 표 말고도 변경 기록 표(`CalendarItemChanges`, `CalendarChanges` 등 이름이 `Changes` 로 끝나는 표)와 공유 캘린더 변경으로 보이는 `ResourceChange` 표가 있어서, 수집 시점의 상태에 더해 바뀐 흔적도 찾아볼 수 있습니다(확인 범위: iPhone 13 mini, iOS 27.0).

미리 알림 DB 에는 할 일의 제목·메모·마감일·완료 여부·완료 시각과 목록, 공유 목록 정보가 들어 있습니다 [2]. iLEAPP 는 iOS 13.3.1 부터 18.0 까지 이 DB 를 시험했고, iOS 버전에 따라 경로와 표가 달라진다고 적었습니다 [2].

두 앱은 iCloud 보호 방식도 다릅니다. 캘린더는 CalDAV 표준 기반이라 고급 데이터 보호를 켜도 종단 간 암호화 대상이 아니고, 미리 알림은 고급 데이터 보호를 켜면 종단 간 암호화됩니다 [3]. 계정 쪽 자료 확보는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에서 다룹니다.

## 위치와 버전별 차이

| 무엇 | 위치 | 확인 정도 |
|---|---|---|
| 캘린더 DB | `HomeDomain :: Library/Calendar/Calendar.sqlitedb` | [1] 경로 패턴 `*/Calendar.sqlitedb*`, 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |
| 캘린더 알림 보조 DB | `HomeDomain :: Library/Calendar/Extras.db` | 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |
| 캘린더 앱 설정 | `HomeDomain :: Library/Preferences/com.apple.mobilecal.plist` | 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |
| 미리 알림 DB | `AppDomainGroup-group.com.apple.reminders :: Container_v#/Stores/Data-<UUID>.sqlite`, `Data-local.sqlite` (`#` 은 가린 숫자) | [2], 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |
| 미리 알림 앱 그룹 설정 | `AppDomainGroup-group.com.apple.reminders :: Library/Preferences/group.com.apple.reminders.plist` | 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |
| 미리 알림 데몬 설정 | `HomeDomain :: Library/Preferences/com.apple.remindd.plist` | 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |

미리 알림은 iOS 버전에 따라 위치와 표가 달라집니다.

| iOS | 미리 알림 DB 위치 | 읽는 표 | 근거 |
|---|---|---|---|
| 13·14·15 | `*/Container_v1/Stores/*.sqlite*` | `ZREMCDOBJECT` 를 `Z_PRIMARYKEY` 로 개체 종류를 가려 읽음. 미리 알림 개체 번호(`Z_ENT`)가 13·14·15 에서 23, 24, 28 로 바뀜 | [2] |
| 16 | `*/Container_v1/Stores/*.sqlite*` | `ZREMCDREMINDER` | [2] |
| 17 이상 | 미리 알림 앱 그룹 컨테이너 | `ZREMCDREMINDER` | [2] |
| 27.0 | `AppDomainGroup-group.com.apple.reminders :: Container_v#/Stores/` | `ZREMCDREMINDER`·`ZREMCDOBJECT` 등이 함께 있음 | 확인 범위: iPhone 13 mini, iOS 27.0 |

iLEAPP 는 iOS 16 이상이면 `ZREMCDREMINDER` 를, 그 전 버전이면 `ZREMCDOBJECT` 를 읽고, iOS 17 부터는 DB 가 `Library/Reminders/Container_v1` 이 아니라 앱 그룹 컨테이너에 있다고 적었습니다 [2]. 관찰한 iOS 27.0 DB 에는 두 표가 함께 있었으므로, 검체에서는 버전과 상관없이 두 표가 모두 있는지 먼저 봅니다. 미리 알림이 캘린더 DB 에서 떨어져 나온 iOS 버전(iOS 13 으로 알려짐)은 이번 자료로 확인하지 못했습니다.

관찰한 백업의 관련 도메인은 캘린더 쪽이 `AppDomain-com.apple.mobilecal`(항목 4개)과 `AppDomainPlugin-com.apple.mobilecal.CalendarIntentsExtension`·`CalendarWidgetExtension`·`FacetimeExtension`, `AppDomainPlugin-com.apple.eventkit.CalendarDiagnosticExtension` 등이고, 미리 알림 쪽이 `AppDomain-com.apple.reminders`(7개), `AppDomainGroup-group.com.apple.reminders`(24개), `AppDomainPlugin-com.apple.reminders.` 로 시작하는 확장 5개 등이었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

## 구조

### 캘린더 DB (Calendar.sqlitedb)

관찰한 DB 의 표 가운데 분석에 쓸 만한 것은 아래와 같습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
CalendarItem, Calendar, Store, Location, Participant, Identity, Alarm, AlarmCache,
Attachment, AttachmentFile, Recurrence, ExceptionDate, OccurrenceCache, Conference,
Notification, ResourceChange, Sharee, SuggestedEventInfo, Error,
CalendarItemChanges, CalendarChanges, AlarmChanges, ParticipantChanges, RecurrenceChanges ...,
ClientCursor, ClientSequence
```

일정 한 건은 `CalendarItem` 한 행이고, 주요 칸은 아래와 같습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
CalendarItem (일부)
summary, description, start_date, start_tz, end_date, end_tz, all_day,
calendar_id, organizer_id, status, url, creation_date, last_modified,
UUID, unique_identifier, external_id, entity_type, priority, due_date, completion_date,
has_attendees, has_attachment, has_recurrences, hidden, app_link,
created_by_id, modified_by_id, travel_time
```

iLEAPP 는 `CalendarItem` 을 중심으로 `Location`(`title`, `address`, `latitude`, `longitude`), `Calendar`(`title`, `color`, `store_id`, `self_identity_email`, `owner_identity_email`, `sharing_status`, `notes`), `Store`(`name`), `Participant`(`email`, `identity_id`, `entity_type`, `status`), `Identity`(`display_name`, `address`), `Attachment`·`AttachmentFile`(`filename`, `file_size`), `Sharee`(`owner_id`, `access_level`, `identity_id`)를 이어 읽습니다 [1]. 즉 일정 → 캘린더 → 저장소(계정) 순서로 올라가면 그 일정이 어느 계정의 어느 캘린더에 있었는지 알 수 있고, 참석자·공유 대상은 `Identity` 로 이름과 주소를 붙입니다.

iLEAPP 는 `CalendarItem` 에 `conference_url_detected` 칸이 있으면 그 칸을, 없으면 `conference_url` 칸을 읽습니다 [1]. 관찰한 `CalendarItem` 에는 두 칸이 모두 없었고, 따로 `Conference` 표(`url` 칸 포함)가 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0). 화상 회의 주소를 찾을 때는 버전에 따라 두 곳을 모두 봅니다.

`CalendarItem` 에 `due_date`, `completion_date`, `priority` 칸이 있는 점은 옛 iOS 에서 미리 알림을 이 DB 에 함께 저장하던 흔적으로 보이지만 확인하지 못했습니다(확인 범위: iPhone 13 mini, iOS 27.0).

그 밖에 관찰한 표와 칸은 아래와 같습니다(확인 범위: iPhone 13 mini, iOS 27.0). `ResourceChange` 는 공유 캘린더의 변경 알림 기록으로, `SuggestedEventInfo` 는 메일·메시지에서 찾아낸 일정 제안과 관련 있는 표로 보이지만 둘 다 확인하지 못했습니다.

```
ResourceChange: change_type, timestamp, changed_properties, create_count, update_count,
                delete_count, deleted_summary, deleted_start_date, calendar_id, calendar_item_id
SuggestedEventInfo: opaque_key, unique_key, changed_fields, timestamp, extraction_group_identifier
Calendar (일부): published_URL, subcal_url, last_sync_start, last_sync_end, refresh_date
Store (일부): name, type, creator_bundle_id, last_sync_start, last_sync_end, owner_name
Location (일부): title, address, latitude, longitude, mapkit_handle, radius
```

`Extras.db` 에는 `ZALARM`(`ZALARMID`, `ZENTITYID`, `ZFIRETIME`, `ZACKNOWLEDGEDDATE`, `ZENTITYDATE`, `ZENTITYURI` 등)과 `ZSETTING`(`ZKEY`, `ZVALUE`) 표가 있었고, 캘린더 앱 설정에는 `LastViewedDate`(float), `LastViewedOccurrenceDate`(datetime), `LastViewedOccurrenceUID`(str), `LastSuspendTime`(float), `defaultCalendarID`(str), `defaultCalendarChangedTimestamp`(int), `LastViewType`(int), `LastReminderMigrationCleanupVersion`(int) 같은 키가 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

### 미리 알림 DB (Data-*.sqlite)

관찰한 미리 알림 DB 는 `Data-<UUID>.sqlite` 와 `Data-local.sqlite` 두 개였습니다(확인 범위: iPhone 13 mini, iOS 27.0). 앞쪽은 계정(iCloud 등)별 DB, 뒤쪽은 기기 로컬 계정 DB 로 보이지만 확인하지 못했습니다. 두 DB 모두 `ZREMCDREMINDER`, `ZREMCDBASELIST`, `ZREMCDOBJECT`, `ZREMCDBASESECTION`, `ZREMCDSAVEDATTACHMENT`, `ZREMCDHASHTAGLABEL`, `ZREMCDTEMPLATE`, `ZREMCKSHAREDENTITYSYNCACTIVITY`, `ZREMCKCLOUDSTATE`, `ACHANGE`, `ATRANSACTION` 같은 표를 담고 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
ZREMCDREMINDER (일부)
ZTITLE, ZNOTES, ZCREATIONDATE, ZLASTMODIFIEDDATE, ZDUEDATE, ZSTARTDATE, ZCOMPLETIONDATE,
ZCOMPLETED, ZFLAGGED, ZPRIORITY, ZMARKEDFORDELETION, ZLIST, ZPARENTREMINDER,
ZTIMEZONE, ZCONTACTHANDLES, ZCKIDENTIFIER, ZICSURL

ZREMCDBASELIST (일부)
ZNAME, ZCOLOR, ZSHAREDOWNERNAME, ZSHAREDOWNERADDRESS, ZSHARINGSTATUS,
ZLASTUSERACCESSDATE, ZMARKEDFORDELETION
```

칸 이름으로 보아 `ZREMCDREMINDER.ZLIST` 는 `ZREMCDBASELIST` 의 목록 행을, `ZPARENTREMINDER` 는 상위 할 일을 가리키고, 검체에서 몇 행을 앱 화면과 맞춰 확인한 뒤 이어 읽습니다. 두 DB 의 칸 목록은 조금 달라서, 예를 들어 `ZTITLEDOCUMENT`·`ZUSERACTIVITY` 칸은 `Data-local.sqlite` 쪽에만 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

`ZREMCDOBJECT` 에는 `ZLATITUDE`, `ZLONGITUDE`, `ZPROXIMITY`, `ZALARM`, `ZTRIGGER`, `ZASSIGNEE`, `ZORIGINATOR` 칸이 있고, 위치 기반 알림과 담당자 지정에 관련 있어 보이지만 확인하지 못했습니다. 공유 목록 활동으로 보이는 `ZREMCKSHAREDENTITYSYNCACTIVITY` 에는 `ZACTIVITYTYPERAWVALUE`, `ZACTIVITYDATE`, `ZAUTHORUSERRECORDIDSTRING`, `ZSHAREDENTITYNAME` 칸이 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

앱 그룹 설정 `group.com.apple.reminders.plist` 에는 `firstTimeAppForegroundingDate`(datetime), `lastAppForegroundingDates`(list), `activitySessionBeginTime`(datetime), `activitySessionId`(str), `lastSeenWelcomeScreenVersion`(int)이, `com.apple.remindd.plist` 에는 `CloudKitAccountStatus`, `lastExtraneousAlarmsCollectorExecutionDate`(datetime), `analyticsActivityLastExecutionDate`(datetime), `spotlightIndexVersion`(str) 같은 키가 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0). `firstTimeAppForegroundingDate` 와 `lastAppForegroundingDates` 는 이름으로 보아 미리 알림 앱을 처음·최근에 앞으로 띄운 시각이지만, 동작은 확인하지 못했습니다.

## 증거로서 의미

### 증명하는 것

`CalendarItem` 행은 수집 시점에 그 제목·시각·장소의 일정이 어느 캘린더에 있었는지 보여 주고, 참석자와 주최자는 `Participant`·`Identity` 로 이름과 주소를 붙일 수 있습니다 [1]. 미리 알림 행은 할 일의 제목·메모·마감일과 함께 완료 여부(`ZCOMPLETED`)와 완료 시각(`ZCOMPLETIONDATE`)을 보여 줍니다 [2]. 공유 캘린더와 공유 목록은 `Sharee`, `ZSHAREDOWNERNAME` 같은 칸으로 누구와 나눴는지를 보여 줍니다.

### 증명하지 못하는 것

일정이 캘린더에 있다고 그 일정에 실제로 갔다고 말할 수 없고, 장소 칸은 입력한 장소일 뿐 그 시각의 위치가 아닙니다. 구독 캘린더나 초대로 들어온 일정은 사용자가 직접 만들지 않았을 수 있어서, `Store`·`Calendar` 로 출처를 먼저 가립니다. 완료 표시는 누군가 완료로 바꿨다는 기록이고, 그 일을 했다는 증명은 아닙니다. 공유 목록의 미리 알림은 다른 참여자가 만들었을 수 있습니다.

보고서에는 "그날 그 장소에서 만났다" 대신 "수집 시점에 이 캘린더에 이 제목·장소·시각의 일정이 있고, 만든 시각 칸 값은 이렇다" 처럼 씁니다. 실제 위치는 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md) 의 흔적과 맞춰 봅니다.

## 시각 해석

캘린더의 시각 칸은 Mac 절대 시각(2001-01-01 UTC 기준 초)이고, iLEAPP 는 `datetime('2001-01-01', 칸 || ' seconds')` 로 바꿉니다 [1]. 미리 알림도 같은 기준이며, iLEAPP 는 값에 978307200 을 더해 Unix 시각으로 만든 뒤 UTC 로 바꿉니다 [2]. 두 방식은 같은 결과를 냅니다.

캘린더에는 `start_tz`·`end_tz`, 미리 알림에는 `ZTIMEZONE` 칸이 따로 있습니다(확인 범위: iPhone 13 mini, iOS 27.0). 저장된 값은 UTC 기준으로 바꾸고, 사용자가 본 현지 시각은 이 시간대 칸으로 다시 계산해서 둘을 함께 적습니다. 종일 일정(`all_day`)이 어느 시간대 기준으로 저장되는지는 확인하지 못해서, UTC 로 바꾼 날짜가 화면과 하루 어긋나 보이면 `start_tz` 를 함께 보고 판단합니다. 시간대 해석은 [시간대와 시각 설정](../system-account/time-zone.md) 과 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

`creation_date`·`last_modified`(캘린더), `ZCREATIONDATE`·`ZLASTMODIFIEDDATE`(미리 알림)는 이름으로 보아 항목을 만들고 고친 시각이지만, 동기화로 다른 기기에서 받은 항목이 이 기기에 들어온 시각인지 원래 만든 시각인지는 확인하지 못했습니다. `com.apple.mobilecal.plist` 의 `LastViewedDate`·`LastSuspendTime` 은 float 로, `defaultCalendarChangedTimestamp` 는 int 로 저장되어 있었고, 기준 시점은 확인하지 못했습니다(확인 범위: iPhone 13 mini, iOS 27.0).

## 함정과 한계

iLEAPP 설명과 관찰한 구조가 어긋난 곳(`conference_url` 칸과 `Conference` 표)이 있어서, 도구 결과에 화상 회의 주소가 비어 있다고 없었다고 쓰면 안 됩니다. 버전이 바뀌면 칸이 옮겨 갈 수 있어서 도구 결과는 [도구 검증](../../03-techniques/reporting/tool-validation.md) 방식으로 원본 DB 와 대조합니다.

iOS 13~15 의 미리 알림은 `ZREMCDOBJECT` 한 표에 여러 종류의 개체가 섞여 있고, 미리 알림을 가리키는 `Z_ENT` 번호가 버전마다 달랐습니다 [2]. 번호를 외워 쓰지 말고 검체의 `Z_PRIMARYKEY` 표에서 `Z_NAME` 으로 번호를 찾습니다.

지운 일정과 할 일은 `ZMARKEDFORDELETION` 칸이나 캘린더의 `*Changes` 표, `ResourceChange` 의 `deleted_summary`·`deleted_start_date` 칸에 흔적이 남을 수 있어 보이지만, 언제까지 남는지는 확인하지 못했습니다. 행이 이미 없어진 경우에는 `-wal` 파일과 빈 페이지를 함께 보고, 방법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

SQLite 는 실수(REAL) 값을 레코드 안에 8바이트 빅엔디언 IEEE 754 배정밀도로 저장합니다. 시각 칸이 실수로 저장되었다고 가정하면, Mac 절대 시각 800000000 초는 아래처럼 보입니다. 아래는 명세로 만든 예시이고 검체에서 나온 값이 아닙니다.

```
41 C7 D7 84 00 00 00 00        = 800000000.0
800000000 + 978307200 = 1778307200 (Unix 초) = 2026-05-09 06:13:20 UTC
```

검체에서 칸 값이 정수로 저장되어 있으면 레코드 머리의 형식 번호가 달라지고 바이트 길이도 달라집니다. 레코드 머리와 형식 번호를 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에 있습니다.

### 공개 도구로 한 번

1. 로컬 백업의 `Manifest.db` 에서 두 앱의 DB 를 찾아 곁가지 파일과 함께 복사합니다.

   ```sql
   SELECT fileID, domain, relativePath FROM Files
   WHERE (domain = 'HomeDomain' AND relativePath LIKE 'Library/Calendar/%')
      OR (domain = 'AppDomainGroup-group.com.apple.reminders' AND relativePath LIKE 'Container_v%/Stores/%');
   ```

2. 캘린더 일정을 캘린더·계정 이름과 함께 읽습니다.

   ```sql
   SELECT datetime('2001-01-01', ci.start_date || ' seconds') AS start_utc,
          ci.start_tz, ci.summary, l.title AS place, c.title AS calendar, s.name AS store
   FROM CalendarItem ci
   LEFT JOIN Location l ON l.ROWID = ci.location_id
   LEFT JOIN Calendar c ON c.ROWID = ci.calendar_id
   LEFT JOIN Store s ON s.ROWID = c.store_id
   ORDER BY ci.start_date;
   ```

3. 미리 알림을 목록 이름과 함께 읽습니다.

   ```sql
   SELECT r.ZTITLE, l.ZNAME AS list,
          datetime(r.ZCREATIONDATE + 978307200, 'unixepoch') AS created_utc,
          datetime(r.ZDUEDATE + 978307200, 'unixepoch') AS due_utc,
          r.ZCOMPLETED,
          datetime(r.ZCOMPLETIONDATE + 978307200, 'unixepoch') AS completed_utc
   FROM ZREMCDREMINDER r
   LEFT JOIN ZREMCDBASELIST l ON l.Z_PK = r.ZLIST;
   ```

4. 같은 파일을 iLEAPP 에 넣어 `calendarEvents` 보고서와 미리 알림 보고서를 만들고, 2·3번 결과와 행 수와 시각이 같은지 견줍니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [애플 계정](../system-account/apple-account.md) | 캘린더·미리 알림을 동기화한 계정(CalDAV 계정 포함) |
| [메일 앱](apple-mail.md) | 일정 초대가 온 메일 |
| [알림 기록](../app-usage/notifications.md) | 일정·할 일 알림이 뜬 시각 |
| [연락처](../communications/contacts.md) | 참석자·공유 대상의 연락처 |
| [중요 위치](../location/significant-locations.md) | 일정 시각에 실제로 머문 곳 |
| [KnowledgeC](../app-usage/knowledgec/index.md)·[바이옴](../app-usage/biome/index.md) | 두 앱을 앞에 띄워 쓴 시각 |
| [시리](../input-assistant/siri.md) | 음성으로 만든 일정·할 일 |

사건 전후의 행동 순서를 세우는 데는 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 이 시각들을 다른 기록과 함께 한 줄로 늘어놓는 방법을 봅니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 캘린더와 미리 알림을 쓴 iOS 검체가 있는지 먼저 확인하고, 있으면 아래 질문을 풀어 봅니다.

1. 검체의 iOS 버전을 확인하고, 미리 알림 DB 가 `Container_v1/Stores/` 와 앱 그룹 컨테이너 가운데 어디에 있는지 봅니다.
2. `Z_PRIMARYKEY` 에서 미리 알림 개체의 `Z_ENT` 번호를 찾아 [2] 가 적은 번호(23, 24, 28)와 같은지 견줍니다.
3. `CalendarItem` 에서 `Store` 이름별로 일정 수를 세고, 사용자가 직접 만든 캘린더와 구독·생일 캘린더를 나눕니다.
4. 일정 하나의 `start_date` 를 UTC 와 `start_tz` 현지 시각 두 가지로 적습니다.
5. 완료된 미리 알림 가운데 `ZCOMPLETIONDATE` 가 `ZDUEDATE` 보다 늦은 것을 찾아 목록을 만듭니다.

## 참고 문헌

1. iLEAPP, `scripts/artifacts/calendarAll.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/calendarAll.py
2. iLEAPP, `scripts/artifacts/reminders.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/reminders.py
3. Apple 지원 102651, "iCloud data security overview" — https://support.apple.com/en-us/102651
