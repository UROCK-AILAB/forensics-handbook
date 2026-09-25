---
title: "슬랙과 팀즈"
parent: "아티팩트 · 메신저"
nav_order: 1030
---

# 슬랙과 팀즈 (Slack·Teams)

슬랙 앱은 워크스페이스마다 SQLite 파일 하나에 메시지·채널·사용자·파일 기록을 남기고, 팀즈 앱은 `SkypeTeams.db` 한 파일에 메시지·사용자·통화·활동 기록을 남깁니다.

## 무엇을 기록하나 · 왜 생기나

두 앱 모두 업무용 메신저이고, 서버에서 받은 대화를 기기 안 SQLite 데이터베이스에 저장합니다. 슬랙 앱(패키지 이름 `com.Slack`)은 기기에 로그인한 워크스페이스마다 DB 파일을 따로 두고, 계정 목록은 별도의 계정 DB 에, 대화에 오간 이미지는 이미지 캐시에 남깁니다[1]. 팀즈 앱(패키지 이름 `com.microsoft.teams`)은 `SkypeTeams.db` 한 파일에 메시지, 대화방, 사용자, 통화 기록, 활동 피드, 파일 정보를 표로 나눠 저장합니다[2].

두 앱의 표 구조는 ALEAPP 슬랙·팀즈 모듈의 시험 이미지 하나씩에서 확인된 것입니다[1][2]. 팀즈 모듈은 2021-04-29 에 만든 뒤 고친 기록이 없어서 요즘 팀즈 앱에서는 구조가 다를 수 있습니다[2].

## 위치와 버전별 차이

경로는 모두 앱 데이터 폴더 기준이고, 앱 데이터 폴더의 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 에서 다룹니다.

| 앱 | 흔적 | 경로 |
|---|---|---|
| 슬랙 | 워크스페이스 DB | `databases/org_<팀 ID>` (워크스페이스마다 하나) |
| 슬랙 | 계정 DB | `databases/account_manager` |
| 슬랙 | 이미지 캐시 | `cache/slack_image_cache/<폴더>/<요청 URL 의 SHA-256>.0`(메타데이터), `.1`(본문) |
| 팀즈 | 메시지 DB | `databases/SkypeTeams.db` |

슬랙 워크스페이스 DB 는 파일 이름보다 `messages`·`conversation`·`users` 표가 모두 있는지로 알아봅니다[1]. 슬랙 이미지 캐시는 DiskLruCache 형식이라서 항목 하나가 `.0` 과 `.1` 두 파일로 짝을 이룹니다[1].

앱 데이터 폴더는 시스템이 다른 앱의 접근을 막는 앱 내부 저장소라서 일반 adb 권한으로는 바로 읽을 수 없고, Android 10(API 29) 이상에서는 이 위치가 암호화됩니다[3]. 확보 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 를 봅니다.

| 앱 | 시험 이미지 | 앱 버전 | 시험 이미지의 행 수 |
|---|---|---|---|
| 슬랙 | 픽셀 7a, Android 14 | 적혀 있지 않음 | 메시지 33, 대화 8, 사용자 5, 파일 4, 계정 1 |
| 팀즈 | 픽셀 7a, Android 14 | 버전코드 2024132725 | 메시지 32, 사용자 3, 통화 2, 활동 0, 파일 0 |

두 앱 모두 삼성 기기에서 시험한 기록이 없어서, 삼성 One UI 에서 경로나 구조가 다른지는 검체로 확인합니다[1][2]. 요즘 팀즈 앱은 `SkypeTeams.db` 를 쓰지 않을 수도 있으니, 검체에서 이 파일이 없으면 `databases` 폴더의 다른 파일을 먼저 살펴봅니다.

## 구조

SQLite 파일 구조 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

### 슬랙 — org 파일의 메시지 표

`messages` 표의 칸은 `ts`, `channel_id`, `user_id`, `subtype`, `message_json`, `thread_ts` 이고, 스레드 답글은 따로 `message_threads` 표에 `ts`, `channel_id`, `event_sub_type`, `message_blob`, `thread_ts` 칸으로 들어 있습니다[1]. 본문은 `message_json`(또는 `message_blob`) JSON 의 `text` 필드입니다[1]. 본문 안에서 사용자를 언급한 부분은 `<@U...>` 모양의 ID 로 남아 있어서 `users` 표에서 이름을 찾아 바꿔 읽습니다[1]. `subtype` 이 `CHANNEL_JOIN` 같은 행은 사용자가 입력한 글이 아니라 앱이 같은 표에 남긴 이벤트입니다[1].

### 슬랙 — 대화·사용자·파일 표

`conversation` 표에는 `conversation_id`, `name_or_user`, `type`, `is_member`, `is_open`, `is_starred`, `latest`, `lastRead` 같은 칸이 있습니다[1]. 시험 이미지에서 `type` 값은 `PUBLIC` 과 `DM` 이었습니다[1]. `is_member` 는 DM·그룹 DM 에서 NULL 이라서, DM 행에서는 이 칸이 비어 있는 상태가 정상입니다[1]. `lastRead` 는 읽은 시각이 아니라 마지막으로 읽은 메시지의 `ts` 값입니다[1].

`users` 표에는 `id`, `name` 과 `profile_real_name`, `profile_email`, `profile_phone`, `profile_title` 처럼 `profile_` 로 시작하는 칸이 있습니다[1]. `files` 표의 칸은 `id`, `file_blob`(서버 파일 기록 JSON), `user`, `channels`, `title`, `deleted` 입니다[1]. 파일 기록 안의 `url_private`, `thumb_720` 같은 URL 을 SHA-256 으로 바꾸면 이미지 캐시의 파일 이름과 맞춰 볼 수 있고, 시험 이미지에서는 3개가 원본 URL 로, 1개는 썸네일 URL 로만 맞았습니다[1].

### 슬랙 — account_manager 의 accounts 표

`accounts` 표의 칸은 `last_accessed`, `email`, `user_id`, `team_id`, `team_domain`, `enterprise_id`, `environment_variant`, `secondary_auth_enabled`, `is_logged_out`, `created_ts`, `team_json` 이고, `team_json` 에 팀 이름 같은 정보가 들어 있습니다[1]. 같은 표의 `token_encrypted`·`token_encrypted_ext1` 칸에는 세션 인증 값이 들어 있어서 ALEAPP 도 일부러 보고서에 넣지 않습니다[1]. 이 두 칸의 값은 보고서에 옮기지 않습니다.

### 팀즈 — SkypeTeams.db

| 표 | 칸 | 내용 |
|---|---|---|
| `Message` | `arrivalTime`, `userDisplayName`, `content`, `deleteTime`, `conversationId`, `messageId` | 메시지 |
| `Conversation` | `conversationId`, `displayName` | 대화방. `displayName` 이 대화 주제 이름 |
| `User` | `lastSyncTime`, `givenName`, `surname`, `displayName`, `email`, `secondaryEmail`, `alternativeEmail`, `telephoneNumber`, `homeNumber`, `accountEnabled`, `type`, `userType`, `isSkypeTeamsUser`, `isPrivateChatEnabled`, `mri` | 사용자 |
| `MessagePropertyAttribute` | `propertyId`, `attributeValue` | `propertyId` 가 `CallLog` 인 행이 통화 기록 |
| `ActivityFeed` | `activityTimestamp`, `sourceUserImDisplayName`, `messagePreview`, `activityType`, `activitySubtype`, `isRead` | 활동 피드 |
| `FileInfo` | `lastModifiedTime`, `fileName`, `type`, `objectUrl`, `isFolder`, `lastModifiedBy` | 파일 정보 |

`Message` 표는 `conversationId` 로 `Conversation` 표와 잇습니다[2]. 통화 기록은 `CallLog` 행의 `attributeValue` 에 JSON 으로 들어 있고, 그 안에 `connectTimeMillis`, `endTimeMillis`, `callState`, `callType`, `originatorDisplayName`, `callDirection`, `target`, `sessionType` 이 있습니다[2]. `target` 을 `User` 표의 `mri` 와 이으면 통화 상대의 이름을 찾을 수 있습니다[2].

## 증거로서 의미

**증명하는 것.** 슬랙의 `messages` 행은 그 워크스페이스·채널에 그 시각의 메시지가 기기에 저장돼 있었다는 기록이고, `accounts` 표는 이 기기에 어느 워크스페이스와 이메일로 로그인했는지와 로그아웃 상태(`is_logged_out`)를 보여 줍니다[1]. 팀즈의 `Message` 행은 그 대화방에 도착한 메시지를, `CallLog` 행은 통화 방향·상태·연결 시각·끝 시각을 담은 통화 기록을 보여 줍니다[2].

**증명하지 못하는 것.** 슬랙의 `users` 표에는 앱이 받아 둔 멤버만 있어서 워크스페이스 전체 멤버가 아닐 수 있고, 표에 없다고 해서 그 사람이 워크스페이스에 없었다고 할 수 없습니다[1]. `subtype` 이 `CHANNEL_JOIN` 같은 이벤트 행은 사용자가 쓴 글이 아니라서 "이 사람이 채널에 글을 올렸다" 는 근거가 되지 않습니다[1]. 이미지 캐시에 사본이 없어도 그 파일이 기기에 없었다는 증거는 아닙니다[1]. 팀즈의 `deleteTime` 에 값이 있으면 삭제된 메시지의 흔적으로 볼 수 있지만, 이 해석은 칸 이름에 기댄 것이고 공식 출처가 없습니다[2]. 누가 언제 지웠는지도 이 칸만으로는 말할 수 없습니다.

보고서에는 "이 사람이 이 파일을 공유했다" 보다 "이 워크스페이스 DB 의 `files` 표에 이 파일 기록이 있고, `user` 칸의 ID 는 이 사용자다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

| 앱 | 값 | 형식 |
|---|---|---|
| 슬랙 | `ts`, `thread_ts`, `lastRead` | 유닉스 초에 소수점 아래가 붙은 값, 텍스트로 저장(모양: `0000000000.000000`) |
| 슬랙 | `last_accessed`, `created_ts` | 단위는 검체에서 확인 |
| 팀즈 | `arrivalTime`, `deleteTime` | 유닉스 밀리초 |
| 팀즈 | `lastSyncTime`(`User`), `activityTimestamp`(`ActivityFeed`) | 유닉스 밀리초 |
| 팀즈 | `connectTimeMillis`, `endTimeMillis`(`CallLog` JSON) | 유닉스 밀리초 |
| 팀즈 | `lastModifiedTime`(`FileInfo`) | ISO 형태 문자열, T 구분자 |

슬랙의 `ts` 는 텍스트로 저장돼 있어서 정렬하거나 바꿀 때 숫자로 먼저 바꿉니다[1]. `lastRead` 는 벽시계 시각이 아니라 마지막으로 읽은 메시지의 `ts` 라서, 그 메시지를 읽은 때가 아니라 읽은 위치를 가리킵니다[1]. 슬랙 `accounts` 표의 두 시각은 단위를 설명한 공개 자료가 없으니, 검체에서 자릿수를 보고 판단합니다[1].

유닉스 시각은 1970-01-01 UTC 기준이라서, 현지 시각으로 옮길 때는 기기의 [시간대와 시각 설정](../system-account/time-zone.md) 을 함께 봅니다. 팀즈 `FileInfo` 의 문자열은 시간대 표시가 있는지 검체에서 확인합니다. 시각 값 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

슬랙은 워크스페이스마다 DB 파일이 따로라서, 한 파일만 보면 다른 워크스페이스의 대화를 놓칩니다[1]. 파일 이름의 팀 ID 와 `accounts` 표의 `team_id` 를 맞춰 어느 파일이 어느 워크스페이스인지 먼저 정리합니다. 스레드 답글은 `messages` 가 아니라 `message_threads` 표에 있어서, 한 표만 보면 답글이 빠집니다[1].

슬랙 `conversation` 표의 `is_member` 가 비어 있는 행을 "소속 정보 누락" 으로 읽지 않습니다. DM·그룹 DM 에서는 원래 NULL 입니다[1].

팀즈의 표 구조는 2021년에 만든 ALEAPP 모듈과 앱 버전코드 2024132725 시험 이미지 하나 기준이라, 다른 앱 버전의 검체에서는 표나 칸이 다를 수 있습니다[2]. 그 시험 이미지에서 활동 피드와 파일 정보는 0행이어서, 두 표에 실제로 어떤 값이 들어가는지는 검체에서 확인합니다[2].

DB 를 읽을 때는 `-wal`·`-shm`·`-journal` 짝 파일도 함께 있어야 하니, 확보할 때 짝 파일을 모두 복사하고 사본을 엽니다. 앱을 지우면 앱 전용 저장소의 파일도 지워져서[3] 이 페이지의 흔적이 남지 않습니다. 이때는 [설치된 앱](../app-usage/packages/index.md) 과 [앱 사용 기록](../app-usage/usagestats/index.md) 으로 앱이 있었는지를 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

`org_` 파일이나 `SkypeTeams.db` 사본을 헥스 편집기로 열면 첫 16바이트가 SQLite 머리 문자열로 시작합니다. 아래는 SQLite 형식 명세로 만든 예시이고 특정 검체에서 나온 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

슬랙 파일에서는 문자열 `CHANNEL_JOIN` 이나 `"text"` 를, 팀즈 파일에서는 `connectTimeMillis` 를 DB 와 `-wal` 파일에서 검색합니다. 두 앱 모두 본문과 통화 기록이 JSON 문자열이라 헥스 화면에서도 글자로 보이고, 표에서 지워졌지만 빈 공간에 남은 조각이 보이면 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 따라 다룹니다.

슬랙 이미지 캐시는 파일 이름이 요청 URL 의 SHA-256 이라서[1], `files` 표에서 꺼낸 URL 을 그대로 해시해 캐시 폴더에서 같은 이름을 찾습니다. 아래는 해시를 구하는 명령의 모양이고, URL 은 검체에서 꺼낸 값으로 바꿉니다.

```sh
printf '%s' '<url_private 값>' | sha256sum
```

### 공개 도구로 한 번

공개 도구 ALEAPP 의 슬랙 모듈은 워크스페이스 DB 와 계정 DB, 이미지 캐시를, 팀즈 모듈은 `SkypeTeams.db` 를 읽어 보고서로 내놓습니다[1][2]. 도구 결과는 SQLite 셸로 직접 뽑은 값과 맞춰 봅니다.

```sql
-- 슬랙: 메시지 시각을 UTC 로
SELECT datetime(CAST(ts AS REAL), 'unixepoch') AS utc_time,
       channel_id, user_id, subtype,
       json_extract(message_json, '$.text') AS text
FROM messages
ORDER BY CAST(ts AS REAL);

-- 팀즈: 메시지와 대화방 이름
SELECT datetime(m.arrivalTime / 1000, 'unixepoch') AS utc_time,
       c.displayName, m.userDisplayName, m.content, m.deleteTime
FROM Message m JOIN Conversation c ON m.conversationId = c.conversationId
ORDER BY m.arrivalTime;

-- 팀즈: 통화 기록 JSON
SELECT attributeValue FROM MessagePropertyAttribute WHERE propertyId = 'CallLog';
```

도구 결과와 직접 확인한 값이 다를 때 가려내는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 확인할 것 |
|---|---|
| [앱 사용 기록](../app-usage/usagestats/index.md) | 메시지·통화 시각 앞뒤로 앱이 화면에 올라온 기록이 있는지 |
| [알림 기록](../app-usage/notification-history.md) | 받은 메시지 시각에 앱 알림이 있었는지 |
| [계정](../system-account/accounts/index.md) | 기기 계정 목록과 슬랙 `accounts` 표의 이메일 |
| [보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md) | 업무용 앱이 작업 프로필 안에 설치됐는지 |
| [통화 기록](../communications/call-log.md) | 팀즈 통화 시각과 기기 통화 기록이 겹치는지 |

여러 앱의 대화를 한 흐름으로 세우는 방법은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 와 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등) 가운데 슬랙이나 팀즈 앱 데이터가 든 Android 이미지를 골라 아래 질문을 풀어 봅니다.

1. 슬랙 `org_` 파일이 몇 개이고, 각각 `accounts` 표의 어느 워크스페이스와 이어지는지 정리합니다.
2. 슬랙 `messages` 표를 `subtype` 값별로 세고, 값마다 사람이 쓴 글인지 앱이 남긴 이벤트인지 `message_json` 을 열어 확인합니다.
3. 슬랙 `conversation` 표의 `lastRead` 값과 같은 `ts` 를 가진 메시지를 찾아, 그 메시지로 말할 수 있는 것을 적습니다.
4. 팀즈 `CallLog` JSON 에서 `connectTimeMillis` 와 `endTimeMillis` 로 통화 길이를 구하고, `target` 을 `User.mri` 와 이어 상대를 찾습니다.
5. 팀즈 `Message` 표에서 `deleteTime` 에 값이 있는 행을 찾고, 보고서에 이 값을 어떤 근거와 한계와 함께 적을지 정합니다.

## 참고 문헌

1. ALEAPP, `slack.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/slack.py
2. ALEAPP, `teams.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/teams.py
3. Android Developers, "Access app-specific files" — https://developer.android.com/training/data-storage/app-specific
