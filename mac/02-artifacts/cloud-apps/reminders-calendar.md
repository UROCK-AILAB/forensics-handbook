---
title: "미리 알림과 캘린더"
parent: "아티팩트 · 클라우드·애플 앱"
nav_order: 1570
---

# 미리 알림과 캘린더 (Reminders·Calendar)

미리 알림과 캘린더는 할 일과 일정을 SQLite DB에 남기고 항목마다 만든 시각·마지막 수정 시각·마감이나 시작 시각을 적어서, 사용자가 무엇을 언제 하려 했는지와 누구와 일정을 잡았는지를 읽을 수 있습니다.

아래 표 구조는 iOS 기준입니다 [2][3]. 맥에서는 표 이름과 열 이름을 실제 데이터에서 먼저 확인하고, 아래 구조는 찾아볼 후보로 씁니다. SQLite 파일 자체를 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

캘린더 DB에는 일정마다 제목, 시작·끝 시각과 시간대, 장소, 소속 캘린더, 주최자와 참석자, 화상 회의 주소, 설명, 만든 시각과 마지막 수정 시각이 남고, 캘린더를 누구와 공유했는지와 첨부 파일 이름도 따로 표에 남습니다 [3]. 미리 알림 DB에는 항목마다 제목, 메모, 만든 시각, 마지막 수정 시각, 마감 시각, 완료 시각과 완료 여부, 깃발 표시, 지우기 표시가 남습니다 [2].

두 앱 모두 계정으로 다른 기기와 동기화되기도 해서, DB에 있는 항목이 이 맥에서 만든 것인지는 DB만으로 판별하지 못합니다. 캘린더의 계정 이름은 `Store` 표에 남아서 [3], 항목이 어느 계정 소속인지는 확인할 수 있습니다.

## 위치와 버전별 차이

### 캘린더

캘린더 캐시 SQLite 파일은 아래 경로에 있습니다 [1].

```
~/Library/Calendars/Calendar Cache
```

| 항목 | 상태 |
|---|---|
| 최근 macOS에서 캘린더 DB가 `~/Library/Group Containers/group.com.apple.calendar/Calendar.sqlitedb` 로 옮겨졌는지와 그 버전 경계 | 실제 데이터로 확인 |
| `~/Library/Calendars/` 아래 계정별 `.caldav`·`.calendar` 폴더와 `.ics` 파일 구조 | 실제 데이터로 확인 |
| `Calendar Cache` 파일의 표·열 이름 | 실제 데이터로 확인 |

실제 데이터에서는 `~/Library/Calendars/` 와 그룹 컨테이너 아래를 모두 찾아보고, 찾은 파일의 표 목록으로 어느 형식인지 판별합니다.

### 미리 알림

iOS에서 미리 알림 DB는 `*/Container_v1/Stores/*.sqlite*` 패턴에 맞는 파일이고, iOS 17 이후 미리 알림은 앱 그룹 컨테이너에 저장됩니다 [2].

| 항목 | 상태 |
|---|---|
| 맥 경로 `~/Library/Group Containers/group.com.apple.reminders/Container_v1/Stores/Data-<UUID>.sqlite`(Catalina 10.15 이후 새 형식) | 실제 데이터로 확인 |
| 예전 미리 알림(macOS 10.14 이하)이 `~/Library/Calendars/` 의 캘린더 저장소를 같이 썼는지 | 실제 데이터로 확인 |

## 구조

아래 표는 모두 iOS 기준이고 [2][3], 맥에서 같은 이름으로 나오는지는 실제 데이터로 확인합니다.

### 캘린더 (iOS `Calendar.sqlitedb`)

| 표 | 열 | 뜻 |
|---|---|---|
| `CalendarItem` | `summary`, `description` | 일정 제목과 설명 |
| | `start_date`, `end_date`, `start_tz` | 시작·끝 시각과 시작 시간대 |
| | `creation_date`, `last_modified` | 만든 시각과 마지막 수정 시각 |
| | `location_id`, `calendar_id`, `organizer_id` | 장소·캘린더·주최자로 이어지는 번호 |
| | `has_attendees`, `conference_url`(또는 `conference_url_detected`) | 참석자 여부와 화상 회의 주소 |
| | `ROWID`, `calendar_scale` | 행 번호, 그 밖의 열 |
| `Calendar` | `title`, `color`, `store_id`, `sharing_status`, `notes` | 캘린더 이름과 공유 상태 |
| `Store` | `name` | 계정 이름 |
| `Location` | `title`, `address`, `latitude`, `longitude` | 장소 이름·주소·좌표 |
| `Participant` | `owner_id`, `identity_id`, `email`, `status`, `entity_type` | 참석자와 응답 상태 |
| `Identity` | `display_name`, `address` | 사람 이름과 주소 |
| `Attachment`, `AttachmentFile` | `filename`, `file_size` | 첨부 파일 이름과 크기 |
| `Sharee` | `owner_id`, `identity_id`, `access_level` | 캘린더를 공유받은 사람과 권한 |

### 미리 알림 (iOS)

iOS 16 이후 형식은 `ZREMCDREMINDER` 표에 항목이 모이고, 열은 `ZTITLE`, `ZNOTES`, `ZCREATIONDATE`, `ZLASTMODIFIEDDATE`, `ZDUEDATE`, `ZCOMPLETIONDATE`, `ZCOMPLETED`, `ZFLAGGED`, `ZMARKEDFORDELETION` 입니다 [2]. 예전 형식은 `ZREMCDOBJECT` 한 표에 여러 종류가 섞여 있어서 종류 번호를 `Z_PRIMARYKEY` 표로 찾아야 하고, 이 번호는 iOS 13~15 사이에 23, 24, 28로 바뀝니다 [2]. 번호를 고정값으로 쓰지 말고 분석 대상마다 `Z_PRIMARYKEY` 에서 다시 찾습니다.

## 증거로서 의미

**증명하는 것.** 캘린더 DB에 일정 행이 있으면 그 제목과 시작·끝 시각을 담은 일정이 이 사용자의 캘린더에 있었다는 기록이고, 참석자·주최자 표는 그 일정에 누가 이름을 올렸는지 알려 줍니다 [3]. `Sharee` 표에 행이 있으면 캘린더를 다른 사람과 공유한 기록이고, 화상 회의 주소 열은 어느 회의에 들어갈 주소가 일정에 붙어 있었는지 알려 줍니다 [3]. 미리 알림에서는 완료 여부와 완료 시각이 할 일을 끝냈다고 표시한 기록이고, `ZMARKEDFORDELETION` 이 켜진 행은 지우기로 표시된 항목이라서 사용자가 지운 할 일을 되살리는 단서가 됩니다 [2].

**증명하지 못하는 것.** 일정이 있다는 사실만으로 그 모임이 실제로 열렸는지, 참석자가 실제로 왔는지는 알 수 없습니다. 동기화로 다른 기기에서 넘어온 항목일 수 있어서, 이 맥에서 입력했다고 쓰지 않습니다. 지우기로 표시된 행이 없다고 해서 지운 항목이 없다고 말하지 못합니다.

보고서에는 "이 사용자의 캘린더 DB에 이 제목의 일정이 이 시각으로 잡혀 있고, 참석자 목록에 이 이메일 주소가 있다" 처럼 기록이 보여 주는 만큼만 씁니다.

## 시각 해석

iOS 기준으로 두 DB의 시각 열은 맥 절대 시각(2001-01-01 기준 초)이고, 아래 두 식으로 바꿀 수 있습니다 [2][3]. 맥 데이터에서도 같은 기준인지는 값의 크기로 먼저 확인합니다.

```
datetime('2001-01-01', CalendarItem.start_date || ' seconds')
DATETIME(ZDUEDATE + 978307200, 'UNIXEPOCH')
```

첫 식은 2001-01-01에 초를 더하고, 둘째 식은 978307200초를 더해 유닉스 시각으로 바꾸는 방식이라 결과는 같습니다. 캘린더 일정은 `start_tz` 에 시작 시간대가 따로 남아서 [3], 보고서에는 바꾼 UTC 값과 일정의 시간대를 함께 적습니다. 시각 값의 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다.

시각 열마다 뜻이 다르다는 점도 챙깁니다. `start_date` 와 `ZDUEDATE` 는 사용자가 정한 일정·마감 시각이라 미래일 수 있고, 행동이 일어난 시각을 보여 주는 열은 `creation_date`, `last_modified`, `ZCREATIONDATE`, `ZLASTMODIFIEDDATE`, `ZCOMPLETIONDATE` 입니다 [2][3].

## 함정과 한계

- **iOS 구조를 맥에 그대로 쓰는 위험.** 위 표 구조는 iOS 기준입니다 [2][3]. 맥 데이터에서 표가 없거나 열 이름이 다르면 그대로 적고, 추측으로 메우지 않습니다.
- **정한 시각과 한 시각.** 일정 시작·마감 시각은 행동 시각이 아닙니다. 타임라인에 넣을 때 열의 뜻을 함께 적습니다.
- **바뀌는 종류 번호.** 예전 미리 알림 형식의 종류 번호는 버전마다 달라서 [2], 한 기기에서 쓴 쿼리를 다른 기기에 그대로 쓰지 않습니다.
- **실제 데이터로 확인할 맥 경로.** 캘린더 DB의 그룹 컨테이너 이동과 미리 알림의 맥 경로는 실제 데이터로 확인해야 합니다. 수집 때 `~/Library/Calendars/` 만 가져오면 빠지는 파일이 있을 수 있습니다.
- **첨부의 격리 속성.** 캘린더 일정 첨부를 내려받은 파일에 남는 격리 종류는 [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

찾은 DB 파일 사본을 헥스 편집기로 열어 첫 바이트가 SQLite 머리말인지 확인하고, 페이지 크기와 WAL 파일 여부를 적습니다. 머리말을 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

### 공개 도구로 한 번

사본을 만든 뒤 `sqlite3` 으로 표 목록을 먼저 보고, 위 구조 표의 표가 있을 때만 쿼리를 돌립니다.

```
sqlite3 Calendar.sqlitedb ".tables"
sqlite3 Calendar.sqlitedb "SELECT ROWID, summary,
  datetime('2001-01-01', start_date || ' seconds') AS start_utc, start_tz,
  datetime('2001-01-01', creation_date || ' seconds') AS created_utc
  FROM CalendarItem;"
sqlite3 reminders.sqlite "SELECT ZTITLE,
  DATETIME(ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS created_utc,
  DATETIME(ZCOMPLETIONDATE + 978307200, 'UNIXEPOCH') AS completed_utc,
  ZCOMPLETED, ZMARKEDFORDELETION FROM ZREMCDREMINDER;"
```

파일 이름은 실제 데이터에서 찾은 이름으로 바꿉니다. iLEAPP의 `reminders.py` [2]와 `calendarAll.py` [3]는 iOS 추출본을 읽는 도구라서, 맥 데이터에는 쿼리를 참고하는 용도로만 씁니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [아이클라우드 계정 (iCloud Account)](icloud-account.md) | 캘린더·미리 알림이 묶인 계정 |
| [연락처 (Contacts)](contacts.md) | 참석자 이메일 주소와 연락처 항목 |
| [애플 메일 (Apple Mail)](../mail/apple-mail/index.md) | 일정 초대 메일과 응답 |
| [줌 (Zoom)](../messengers/zoom.md) | 일정의 화상 회의 주소와 실제 회의 참여 |
| [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) | 일정 첨부를 내려받은 기록 |
| [개인 정보 보호 권한 (TCC)](../credentials/tcc/index.md) | 다른 앱이 캘린더·미리 알림에 접근을 승인받았는지 |
| [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) | 일정을 연락 관계 재구성에 쓰는 흐름 |

## 실습

공개 데이터셋(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. `~/Library/Calendars/Calendar Cache` 가 있는지 찾고, 있으면 표 목록을 적어 보세요.
2. 그룹 컨테이너 아래에서 캘린더와 미리 알림 DB로 보이는 SQLite 파일을 찾고, iOS 구조 표의 표 이름과 겹치는 것이 있는지 비교해 보세요.
3. 일정 하나를 골라 만든 시각, 시작 시각, 시작 시간대를 뽑고 각 시각이 무엇을 뜻하는지 나눠 적어 보세요.
4. 지우기로 표시된 미리 알림 행이 있으면 제목과 마지막 수정 시각을 뽑아 보세요.

## 참고 문헌

1. ForensicArtifacts, macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. iLEAPP, scripts/artifacts/reminders.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/reminders.py
3. iLEAPP, scripts/artifacts/calendarAll.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/calendarAll.py
