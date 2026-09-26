---
title: "인스타그램"
parent: "아티팩트 · 메신저"
nav_order: 1000
---

# 인스타그램 (Instagram)

인스타그램 앱은 다이렉트 메시지(Direct Message)와 대화방 목록을 앱 데이터 폴더의 `direct.db` 에 남기고, 로그인 계정·연락처·앱 사용 구간은 따로 떨어진 파일에 남깁니다.

## 무엇을 기록하나 · 왜 생기나

인스타그램 앱(패키지 이름 `com.instagram.android`)은 주고받은 다이렉트 메시지를 기기 안 SQLite 데이터베이스에 한 건씩 저장하고, 메시지 한 건의 전체 내용을 JSON 문자열로 함께 넣어 둡니다[1]. 같은 DB 에는 대화방마다 참가자와 마지막 활동 시각이 있고 로그인한 계정의 ID 도 들어 있어서, 메시지를 보냈는지 받았는지를 이 둘을 비교해 구분합니다[1].

메시지 말고도 흔적이 세 군데 더 남습니다. 앱 설정 XML 에는 로그인 계정의 사용자 이름·ID·계정 종류가 JSON 으로 들어 있고, 계정별 메시징 DB 에는 앱이 받아 둔 연락처가, 앱 사용 시간 DB 에는 시작·끝 시각이 있는 구간이 쌓입니다[1].

## 위치와 버전별 차이

경로는 모두 앱 데이터 폴더 기준입니다. 앱 데이터 폴더가 어디에 어떻게 놓이는지는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 에서 다룹니다.

| 파일 | 경로 | 담긴 내용 |
|---|---|---|
| 대화 DB | `databases/direct.db` | 메시지(`messages`), 대화방(`threads`), 로그인 계정(`session`) |
| 계정 설정 | `shared_prefs/com.instagram.android_preferences.xml` | 계정 JSON(키 `current`, `user_access_map`) |
| 계정별 메시징 DB | `databases/ig_msys_database_<숫자>` | 연락처(`contacts`) |
| 앱 사용 시간 DB | `databases/time_in_app_<사용자 ID>.db` | 사용 구간(`intervals`). 파일 이름의 숫자가 사용자 ID |

이 폴더는 시스템이 다른 앱의 접근을 막는 앱 내부 저장소라서 일반 adb 권한으로는 바로 읽을 수 없고, Android 10(API 29) 이상에서는 이 위치가 암호화됩니다[2]. Android 12(API 31) 이상을 대상으로 하는 앱은 adb backup 을 실행해도 앱 데이터가 빠지는데[3], 인스타그램 앱이 여기에 해당하는지는 실제 기기의 앱 버전으로 확인합니다. 어떤 방식으로 파일을 확보하는지는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 를 봅니다.

`ig_msys_database_<숫자>` 는 확장자가 없지만 ALEAPP 시험 이미지에서는 암호 없는 일반 SQLite 파일이었습니다[1]. ALEAPP 이 이 모듈을 시험한 추출 이미지는 아래와 같습니다[1].

| Android | 시험 이미지의 기기 | 다이렉트 메시지 행 수(삼성 기기만) |
|---|---|---|
| 10 | 갤럭시 S10 | 0건 |
| 11, 12 | 픽셀 3 | |
| 13 | 갤럭시 S20, 기타 1대 | 갤럭시 S20: 11건 |
| 14 | 픽셀 7a, 갤럭시 A53, 기타 1대 | 갤럭시 A53: 0건 |
| 15 | 2대(하나는 POCO X7) | |
| 16, 17 | 픽셀 8 Pro | |

시험 이미지에는 인스타그램 앱 버전이 적혀 있지 않아서, 앱이 업데이트될 때 표나 열이 바뀌었는지는 알 수 없습니다. 삼성 One UI 에서 경로나 DB 구조가 다른지는 실제 기기로 확인해야 합니다.

## 구조

저장 형식 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 와 [설정 XML과 SharedPreferences](../../01-foundations/data-formats/shared-preferences.md) 페이지에서 다룹니다. 여기서는 표와 열의 뜻만 정리합니다.

### direct.db — messages 표

| 열 | 뜻 |
|---|---|
| `timestamp` | 메시지 시각, 유닉스 마이크로초 |
| `thread_id` | 대화방 ID. `threads` 표와 잇는 값 |
| `message_type` | 메시지 종류. `video_call_event` 이면 영상 통화 이벤트 |
| `text` | 본문 |
| `message` | 메시지 한 건 전체를 담은 JSON |

본문·보낸 사람·항목 종류·미디어 정보는 `message` 열의 JSON 에 들어 있습니다[1]. JSON 안에는 보낸 사람 ID 인 `user_id`, 항목 ID 인 `item_id`, 종류를 뜻하는 `content_type` 이 있고, 미디어가 붙은 메시지면 `media` 안의 `image_versions2`·`video_versions` 에 `candidates` 목록과 그 안의 `url` 이 들어 있으며 `taken_at` 과 `user.username` 도 함께 있습니다[1]. JSON 안의 `thread_key`·`timestamp` 는 ALEAPP 이 시험한 모든 행에서 표의 `thread_id`·`timestamp` 열과 값이 같았습니다[1].

`message_type` 이 `video_call_event` 인 행은 JSON 의 `video_call_event` 아래에 `action`, `description`, `did_join`, `vc_id` 가 있습니다[1]. `description` 에는 "You started a video chat" 처럼 앱이 만든 문장이 들어가고, 통화를 시작할 때와 끝낼 때가 따로 기록되면 한 통화가 행 두 개로 남습니다[1].

### direct.db — threads 표와 session 표

`threads` 표에는 `thread_id`, `thread_info`, `last_activity_time` 열이 있습니다[1]. `thread_info` 는 JSON 이고 참가자 목록(`recipients` 또는 `users`), 대화에 초대한 사람(`inviter`), 대화방 제목(`thread_title`), `thread_v2_id` 가 들어 있습니다[1]. 참가자 한 명에는 `pk`·`pk_id`·`id` 가운데 하나와 `username`, `full_name` 이 있습니다[1]. `session` 표의 `user_id` 열이 이 기기에 로그인한 계정의 ID 입니다[1].

### 계정 설정 XML

`com.instagram.android_preferences.xml` 의 키 `current` 와 `user_access_map` 에 계정 JSON 이 들어 있습니다[1]. JSON 에는 `username`, `full_name`, ID(`id`·`instagram_pk`·`pk` 가운데 있는 것), `account_type`, `is_business`, `is_verified`, `follower_count`, `following_count`, `biography`, `external_url`, `profile_pic_url` 이 나올 수 있고, 같은 계정이 두 키에 서로 다른 상세도로 두 번 나오기도 합니다[1]. 팔로워 수 같은 값은 `user_access_map` 의 일부 항목에만 있었습니다[1].

### ig_msys_database — contacts 표

`contacts` 표의 열은 `id`, `name`, `first_name`, `last_name`, `username`, `phone_number`, `email_address`, `is_messenger_user`, `contact_type`, `blocked_by_viewer_status`, `blocked_since_timestamp_ms`, `work_company_name`, `work_job_title`, `profile_picture_url` 입니다[1]. 차단 여부와 차단한 시각도 이 표에 함께 남습니다.

### time_in_app — intervals 표

`intervals` 표의 열은 `start_walltime`, `end_walltime`, `start_event`, `end_event`, `seq_num` 입니다[1]. `start_event`·`end_event` 숫자의 뜻과 이 구간이 정확히 무엇을 재는지는 공개된 설명이 없고, DB·표 이름으로 짐작할 수 있을 뿐입니다[1].

## 증거로서 의미

**증명하는 것.** `messages` 표의 행은 그 시각에 그 대화방으로 오간 메시지를 앱이 기기에 저장했다는 기록입니다. 보낸 사람 `user_id` 가 `session` 표의 `user_id` 와 같으면 이 기기에 로그인한 계정이 보낸 메시지이고, 다르면 받은 메시지입니다[1]. 이 방향은 DB 에 저장된 값이 아니라 두 값을 비교해 계산한 결과라서, 보고서에는 계산 근거를 함께 적습니다. `threads` 표와 계정 설정 XML 은 이 기기에서 어느 계정으로 로그인했고 누구와 대화방을 열었는지를 보여 줍니다.

**증명하지 못하는 것.** `video_call_event` 행은 영상 통화 이벤트일 뿐 통화 기록이 아니라서[1], 통화가 실제로 이어졌는지나 얼마나 길었는지를 이 행 하나로 말할 수 없습니다. `contacts` 표의 행은 앱이 로컬 연락처 저장소에 넣어 둔 항목일 뿐이고, 행이 있다고 해서 소유자가 그 계정과 연락했거나 팔로우했거나 아는 사이라는 뜻은 아닙니다[1]. `intervals` 표의 구간은 무엇을 재는지 출처가 없어서 "이 시간 동안 앱을 썼다" 는 문장의 근거로 쓰기 어렵고, 앱 사용 시간은 [앱 사용 기록](../app-usage/usagestats/index.md) 과 함께 봐야 합니다.

`direct.db` 에 메시지가 0건이어도 메시지가 없었다고 볼 수는 없습니다. ALEAPP 시험 이미지 가운데 일부는 `direct.db` 에 메시지가 0건이었습니다[1]. 미디어 메시지도 마찬가지라서 시험 이미지에는 본문 없이 미디어 URL 만 있었고 다이렉트 메시지 미디어의 캐시 사본은 어느 이미지에도 없었지만, 캐시 사본이 없다고 해서 미디어가 없었다고 할 수는 없습니다[1].

보고서에는 "이 계정이 이 사진을 보냈다" 보다 "이 시각에 이 대화방에 이 URL 을 가리키는 미디어 메시지 행이 있고, 보낸 사람 ID 가 로그인 계정 ID 와 같다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

| 값 | 위치 | 단위 |
|---|---|---|
| `timestamp` | `messages` 표, 메시지 JSON | 유닉스 마이크로초(10^-6 초) |
| `last_activity_time` | `threads` 표 | 유닉스 마이크로초 |
| `taken_at` | 메시지 JSON 의 `media` | 유닉스 초 |
| `blocked_since_timestamp_ms` | `contacts` 표 | 유닉스 밀리초(열 이름과 ALEAPP 변환 기준) |
| `start_walltime`, `end_walltime` | `intervals` 표 | 유닉스 초 |

같은 DB 안에서도 마이크로초·밀리초·초가 섞여 있어서, 값마다 단위를 따로 맞춰 바꿉니다[1]. 유닉스 시각은 1970-01-01 UTC 기준이라 현지 시각으로 옮길 때는 기기의 [시간대와 시각 설정](../system-account/time-zone.md) 을 함께 확인합니다. 단위 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

`last_activity_time` 이 어떤 동작에서 바뀌는지는 공식 설명이 없고, 열 이름으로 짐작할 수 있을 뿐입니다. `taken_at` 은 미디어 쪽 시각이라 메시지를 보낸 시각과 같은 값이 아닐 수 있으니, 두 값을 섞어 쓰지 않습니다.

## 함정과 한계

WAL 파일을 빼고 DB 만 열면 행이 빠집니다. ALEAPP 은 DB 를 읽을 때 `-wal`·`-shm`·`-journal` 짝 파일을 함께 가져오고, 한 시험 이미지에서는 연락처 5건이 WAL 에만 있었습니다[1]. 확보할 때 짝 파일을 모두 함께 복사하고, 원본이 아니라 사본을 엽니다.

로그인한 계정은 대화방 참가자 목록에 들어 있지 않습니다[1]. 참가자 목록만 보고 "이 대화방에는 상대 한 명만 있었다" 고 읽으면 로그인 계정을 빠뜨리게 됩니다.

계정 설정 XML 에서 같은 계정이 두 번 나오면 한 계정을 두 개로 세지 않도록 ID 로 묶습니다. 팔로워 수 같은 필드가 비어 있으면 값이 0 이라는 뜻이 아니라 파일에 그 값이 없다는 뜻입니다[1].

앱을 지우면 앱 전용 저장소의 파일도 함께 지워져서[2] 앱을 지운 기기에는 이 페이지의 DB 가 남지 않습니다. 이때는 [설치된 앱](../app-usage/packages/index.md) 과 [앱 사용 기록](../app-usage/usagestats/index.md) 처럼 시스템 쪽에 남는 흔적으로 앱이 있었는지를 확인합니다.

표·열 이름은 앱 버전이 적혀 있지 않은 ALEAPP 시험 이미지 기준입니다[1]. 다른 앱 버전의 데이터에서는 열이 다를 수 있으니 먼저 표 구조를 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

`direct.db` 와 짝 파일의 사본을 헥스 편집기로 엽니다. 일반 SQLite 파일은 첫 16바이트가 아래처럼 시작합니다. 아래는 SQLite 형식 명세로 만든 예시이고 특정 기기에서 나온 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

그다음 문자열 `"thread_key"` 나 `"item_id"` 로 DB 파일과 `-wal` 파일을 검색합니다. `message` 열은 JSON 문자열이라 헥스 화면에서도 글자로 보이고, 검색에 걸린 위치 앞뒤로 메시지 한 건의 JSON 이 이어집니다. 이 방식으로 표에서 지워졌지만 빈 공간에 남아 있는 행이 보일 수도 있는데, 이렇게 찾은 조각을 어떻게 다루는지는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

### 공개 도구로 한 번

공개 도구 ALEAPP 의 인스타그램 모듈은 이 페이지의 네 파일을 읽어 메시지·대화방·계정·연락처·사용 구간을 표로 내놓습니다[1]. 도구 결과는 sqlite3 같은 SQLite 셸로 같은 값을 직접 뽑아 맞춰 봅니다. 아래 쿼리는 메시지 시각을 UTC 로 바꾸고 방향을 계산하는 예입니다. JSON 안 `user_id` 의 위치는 실제 DB 에서 `message` 열 값을 먼저 확인한 뒤 경로를 맞추고, `session` 표에 행이 여럿이면 메시지가 겹쳐 나오니 먼저 행 수를 확인합니다.

```sql
SELECT
  datetime(m.timestamp / 1000000, 'unixepoch') AS utc_time,
  m.thread_id,
  m.message_type,
  m.text,
  json_extract(m.message, '$.user_id') AS sender_id,
  CASE WHEN json_extract(m.message, '$.user_id') = s.user_id
       THEN 'Outgoing' ELSE 'Incoming' END AS direction
FROM messages m, session s
ORDER BY m.timestamp;
```

도구와 직접 쿼리의 결과가 다르면 어느 쪽이 맞는지 가려내는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 확인할 것 |
|---|---|
| [앱 사용 기록](../app-usage/usagestats/index.md) | 메시지 시각 앞뒤로 인스타그램 앱이 화면에 올라온 기록이 있는지 |
| [알림 기록](../app-usage/notification-history.md) | 받은 메시지 시각에 인스타그램 알림이 있었는지 |
| [디지털 웰빙](../app-usage/digital-wellbeing.md) | `intervals` 구간과 앱 사용 시간이 겹치는지 |
| [설치된 앱](../app-usage/packages/index.md) | 앱 설치·업데이트 시각과 DB 기록이 시작된 시점 |
| [계정](../system-account/accounts/index.md) | 기기 계정 목록과 설정 XML 의 로그인 계정 |
| [미디어 저장소](../media/mediastore/index.md) | 대화에 오간 사진이 공용 저장 공간에 저장됐는지 |

여러 앱의 대화를 시간순으로 합쳐 보는 방법은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 와 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 시험 이미지(NIST CFReDS 등) 가운데 인스타그램 앱 데이터가 든 Android 이미지를 골라 아래 질문을 풀어 봅니다.

1. `session` 표의 `user_id` 와 계정 설정 XML 의 계정 ID 가 같은 계정을 가리키는지 확인합니다.
2. 대화방마다 보낸 메시지와 받은 메시지는 각각 몇 건이고, 계산 근거는 무엇인지 적습니다.
3. `video_call_event` 행을 모아 같은 `vc_id` 로 묶이는 행이 몇 개인지 세고, 이 행들로 말할 수 있는 것과 없는 것을 나눠 적습니다.
4. `-wal` 파일을 뺀 사본과 함께 연 사본에서 행 수가 달라지는지 비교합니다.
5. `taken_at` 과 메시지 `timestamp` 가 다른 미디어 메시지를 찾고, 보고서에 어느 시각을 어떻게 적을지 정합니다.

## 참고 문헌

1. ALEAPP, `instagram.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/instagram.py
2. Android Developers, "Access app-specific files" — https://developer.android.com/training/data-storage/app-specific
3. Android Developers, "Behavior changes: Apps targeting Android 12" — https://developer.android.com/about/versions/12/behavior-changes-12
