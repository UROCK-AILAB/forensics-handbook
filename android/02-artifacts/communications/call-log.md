---
title: "통화 기록"
parent: "아티팩트 · 통화·문자·연락처"
nav_order: 550
---

# 통화 기록 (calllog.db)

## 한 줄 요약

`calllog.db` 는 전화 앱 화면의 "최근 기록" 뒤에 있는 SQLite 데이터베이스이고, 통화마다 상대 번호·시각·통화 길이·수신/발신 종류와 차단 이유까지 한 행에 적어 둡니다.

## 무엇을 기록하나 · 왜 생기나

전화가 오가면 안드로이드의 통화 기록 제공자가 `calls` 표에 행을 하나 추가합니다. 앱은 이 표를 `content://call_log/calls` 주소로 읽고, 읽으려면 `READ_CALL_LOG` 권한이 있어야 합니다[1]. 행에는 상대 번호와 통화 시각·길이뿐 아니라 통화 종류(수신·발신·부재중·거절·차단 등), 영상·Wi-Fi 통화 같은 부가 기능, 번호 공개 여부, 통화에 쓴 회선(SIM), 통화 당시 연락처에서 복사해 둔 이름이 함께 들어갑니다[3].

같은 데이터베이스에 `voicemail_status` 표도 있고[2], 음성 사서함 메시지 역시 `calls` 표에 종류 값 4 로 들어갑니다. 음성 사서함은 [통화 녹음과 음성 사서함](call-recording-voicemail.md) 에서 따로 다룹니다.

## 위치와 버전별 차이

AOSP 소스에서 이 데이터베이스를 만드는 코드는 `CallLogDatabaseHelper` 이고, 파일 이름은 `calllog.db` 입니다[2]. 같은 코드에 `calllog_shadow.db` 라는 이름도 따로 정의되어 있고, 이 "그림자(shadow)" 데이터베이스는 기기 보호 저장소(device protected storage)에 만듭니다[2]. 잠금을 풀기 전에도 열 수 있는 저장소라서 첫 잠금 해제 전에 들어온 통화를 담는 용도로 보입니다. 어떤 행이 언제 옮겨지는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 이 코드는 연락처 제공자(com.android.providers.contacts) 소스 안에 있어서 파일도 그 앱의 데이터 폴더에 있을 가능성이 높습니다. 실제 기기 경로와 삼성 기기가 같은 패키지를 쓰는지는 검체에서 확인합니다. 앱 데이터 폴더의 일반 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 를 봅니다.

| 항목 | 내용 | 근거 |
|---|---|---|
| 파일 이름 | `calllog.db`, 기기 보호 저장소에 `calllog_shadow.db` | AOSP main 가지[2] |
| 데이터베이스 버전 | 12 | AOSP main 가지. 기기마다 다를 수 있음[2] |
| 표 | `calls`, `voicemail_status` | [2] |
| 속성 키 | `call_log_last_synced`, `call_log_last_synced_for_shadow`, `migrated` | [2] |
| 옛 버전 | 헬퍼 코드에 `contacts2.db` 의 옛 표를 가리키는 상수(`LegacyConstants`)가 남아 있어, 예전에는 통화 기록이 [연락처](contacts.md) 데이터베이스 안에 있었던 것으로 보입니다. 옮겨진 Android 버전은 공개 자료가 없습니다 | [2] |
| 삼성 One UI | 같은 경로·패키지를 쓰는지, 칸이 더 있는지는 검체에서 확인 | — |

오래된 검체를 받았다면 `calllog.db` 가 없을 수도 있으니 `contacts2.db` 안에서도 통화 기록 표를 찾아봅니다.

## 구조

`calls` 표의 칸은 소스 상수 이름과 실제 칸 이름이 다른 것이 많습니다. 아래 표의 왼쪽이 실제 칸 이름이고[3], 도구가 상수 이름으로 보여 줄 때 맞춰 보는 데 씁니다.

| 실제 칸 | 소스 상수 | 뜻 |
|---|---|---|
| `number` | NUMBER | 상대 번호(TEXT) |
| `presentation` | NUMBER_PRESENTATION | 번호 공개 여부 |
| `post_dial_digits` | POST_DIAL_DIGITS | 연결 뒤에 누른 숫자 |
| `via_number` | VIA_NUMBER | 수신 전화가 들어온 보조 회선 번호 |
| `date` | DATE | 통화 시각. 유닉스 밀리초 |
| `duration` | DURATION | 통화 길이. 초 |
| `data_usage` | DATA_USAGE | 통화에 쓴 데이터양. 바이트 |
| `type` | TYPE | 통화 종류 |
| `features` | FEATURES | 부가 기능 비트 |
| `subscription_component_name` | PHONE_ACCOUNT_COMPONENT_NAME | 전화 계정을 제공한 구성 요소 |
| `subscription_id` | PHONE_ACCOUNT_ID | 전화 계정 ID(TEXT) |
| `phone_account_address` | PHONE_ACCOUNT_ADDRESS | 전화 계정 주소 |
| `new` | NEW | 사용자가 확인했는지 |
| `is_read` | IS_READ | 읽음 여부 |
| `name` | CACHED_NAME | 통화 당시 연락처에서 복사한 이름 |
| `numbertype`, `numberlabel` | CACHED_NUMBER_TYPE, CACHED_NUMBER_LABEL | 복사해 둔 번호 종류·이름표 |
| `lookup_uri`, `normalized_number`, `formatted_number` | CACHED_LOOKUP_URI 등 | 복사해 둔 연락처 조회 정보 |
| `countryiso`, `geocoded_location` | COUNTRY_ISO, GEOCODED_LOCATION | 국가 코드, 번호로 추정한 지역 |
| `voicemail_uri`, `transcription` | VOICEMAIL_URI, TRANSCRIPTION | 음성 사서함 연결, 받아쓴 글 |
| `last_modified` | LAST_MODIFIED | 행을 넣거나 바꾸거나 삭제 표시한 마지막 시각. 유닉스 밀리초 |
| `block_reason`, `call_screening_app_name` | BLOCK_REASON, CALL_SCREENING_APP_NAME | 차단 이유, 통화 선별 앱 이름 |
| `missed_reason` | MISSED_REASON | 부재중 이유 |
| `priority`, `subject`, `location` | PRIORITY, SUBJECT, LOCATION | 통화 작성기(call composer)로 보낸 우선순위·제목·위치 |
| `is_business_call`, `asserted_display_name` | IS_BUSINESS_CALL, ASSERTED_DISPLAY_NAME | 업무 전화 여부, 발신 측이 내세운 표시 이름 |

소스의 CREATE TABLE 문에는 이 밖에도 `PHONE_ACCOUNT_HIDDEN`, `SUB_ID`, `ADD_FOR_ALL_USERS`, `CALL_SCREENING_COMPONENT_NAME`, `COMPOSER_PHOTO_URI`, `IS_PHONE_ACCOUNT_MIGRATION_PENDING` 같은 상수가 있고, 음성 사서함용 칸들이 뒤에 붙습니다[2]. 칸마다 추가된 API 수준은 자료마다 다르게 나옵니다.

숫자 칸의 값은 다음과 같이 읽습니다[3].

| 칸 | 값 |
|---|---|
| `type` | 1 수신, 2 발신, 3 부재중, 4 음성 사서함, 5 거절, 6 차단, 7 다른 기기에서 받음 |
| `features` (비트를 더한 값) | 1 영상 통화, 2 다른 기기에서 가져옴, 4 HD, 8 Wi-Fi 통화, 16 보조 다이얼링, 32 RTT, 64 VoLTE |
| `presentation` | 1 허용, 2 발신자 제한, 3 알 수 없음, 4 공중전화, 5 사용할 수 없음 |
| `block_reason` | 0 차단 안 됨, 1 통화 선별 서비스, 2 음성 사서함으로 바로 보냄, 3 차단 번호, 4 알 수 없는 번호, 5 발신자 제한 번호, 6 공중전화, 7 연락처에 없는 번호 |

예를 들어 `features` 가 72 이면 8(Wi-Fi 통화)과 64(VoLTE)를 더한 값입니다.

## 증거로서 의미

**증명하는 것.** 기록 한 행은 이 기기의 통화 기록 제공자가 해당 시각에 해당 번호와 해당 종류의 통화를 적었다는 뜻입니다. `type` 과 `block_reason` 을 함께 보면 부재중인지, 사용자가 거절했는지, 차단 목록이나 통화 선별 앱 때문에 막혔는지를 나눠 볼 수 있고, `subscription_id` 와 `via_number` 로 어느 회선을 썼는지 좁힐 수 있습니다.

**증명하지 못하는 것.** 기록은 통화가 오갔다는 사실만 말하고, 누가 폰을 들고 있었는지나 무슨 말을 했는지는 말하지 않습니다. `name` 칸은 통화 당시 연락처에서 복사해 둔 값이라서, 지금 연락처에 없는 이름이 남아 있을 수 있지만 그 이름이 상대의 실제 신원이라는 뜻은 아닙니다. 복사해 둔 이름을 나중에 언제 다시 고쳐 쓰는지는 공개된 분석 자료가 없습니다. 기록이 없다고 해서 통화가 없었다고 할 수도 없습니다. 사용자가 지웠거나 보관 한도에 밀려 지워졌을 수 있기 때문입니다. 메신저 앱으로 한 음성 통화가 이 표에 남는지도 앱마다 검체에서 확인합니다.

## 시각 해석

`date` 는 유닉스 시작 시점부터 센 밀리초라서 시간대와 상관없는 UTC 기준 값이고, `duration` 은 초 단위입니다[3]. `date` 가 통화를 건(울린) 시각인지 연결된 시각인지는 공개 문서에 밝혀져 있지 않으므로, `date` 에 `duration` 을 더한 값을 통화가 끝난 시각으로 보고서에 쓰려면 먼저 시험 기기로 확인합니다. `last_modified` 는 행을 넣거나 바꾸거나 삭제 표시를 한 마지막 시각이고, 단위는 유닉스 밀리초입니다[3]. 그래서 `date` 보다 한참 뒤의 `last_modified` 가 있으면 통화가 끝난 뒤에 그 행을 누군가 고쳤다는 단서가 되지만, 어느 칸을 바꿨는지는 이 값만으로 알 수 없습니다. 시각 값 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을 봅니다.

## 함정과 한계

AOSP 기본값은 전화 계정(PhoneAccountHandle)마다 최근 500건까지만 남기는 것이라서(`DEFAULT_MAX_CALL_LOG_SIZE = 500`)[3], 통화가 잦은 사용자라면 오래된 기록이 밀려 지워집니다. main 가지 소스에는 기능 플래그가 켜져 있으면 SIM 통화의 한도를 기기 설정값(`config_maximumCallLogEntriesPerSim`)으로 바꾸는 코드도 있어서[3], 제조사나 기기마다 한도가 다를 수 있으니 삼성 기기의 값은 검체에서 확인합니다. 계정마다 따로 세므로 SIM 이 둘인 기기는 전체 행이 500건보다 많을 수 있습니다.

통화 기록을 넣는 코드는 상대 번호가 연락처에 있으면 그 연락처의 사용 통계를 갱신하고, 발신 통화가 기준 길이(`MIN_DURATION_FOR_NORMALIZED_NUMBER_UPDATE_MS`) 이상 이어졌는데 연락처 쪽 정규화 번호가 비어 있으면 그 번호도 채웁니다[3]. 이렇게 통화 기록과 [연락처](contacts.md) 의 값이 서로 영향을 주고받습니다. 두 데이터베이스 가운데 한쪽 값만 보고 "연락처에 저장된 사람과 통화했다" 고 쓰지 않습니다.

사용자가 기록을 지우면 행은 표에서 사라지지만, SQLite 파일 안의 빈 페이지나 WAL 파일에 흔적이 남을 수 있습니다. 원리는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서, 복구 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다. 그래서 수집할 때는 `-wal`·`-shm` 파일도 함께 가져옵니다.

설정에도 아래와 같이 통화와 관련된 키가 여럿 있습니다. 공개된 설명이 없어 키 이름만으로 뜻을 단정하지 않습니다.

| 영역 | 키 |
|---|---|
| secure | `backup_enabled:com.android.calllogbackup` |
| global | `dialer_show_blocked_calls_in_recents`, `spam_call_enable`, `spam_call_mute_first_ring`, `show_contacts_numbers_in_calls`, `caller_information`, `multi_sim_voice_call`, `multi_sim_voice_call_slot`, `last_call_forward_action` |
| system | `dialer_app_active`, `block_unwanted_call`, `block_unwanted_call_type`, `call_screening`, `voicecall_type`, `prefered_voice_call` |

`backup_enabled:com.android.calllogbackup` 키가 있다는 것은 com.android.calllogbackup 라는 통화 기록 백업 패키지가 이 기기에 있다는 흔적입니다. 기기에서 기록을 지웠더라도 백업 쪽에 남았을 가능성이 있으니 [구글 백업](../mail-cloud/google-backup.md) 도 함께 봅니다. 설정 값을 읽는 법은 [설정 값](../system-account/settings.md) 에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래 바이트는 SQLite 레코드 형식 명세로 만든 예시이고, 실제 검체에서 가져온 값이 아닙니다. 레코드 머리에서 `date` 칸의 직렬 형식(serial type)이 5 이면 값은 6바이트 빅 엔디언 정수입니다.

```text
직렬 형식 5 (6바이트 정수) 본문:  01 95 4F 1C 27 40
16진수 0x01954F1C2740 = 1740789000000 (밀리초)
= 2025-03-01 00:30:00 UTC = 2025-03-01 09:30:00 한국 시각
```

같은 레코드에서 `type` 칸이 직렬 형식 1(1바이트 정수)이고 본문 바이트가 `03` 이면 부재중 통화입니다.

**공개 도구로 한 번.** SQLite 명령줄 도구(sqlite3)로 사본을 열고, 먼저 `.schema calls` 로 이 기기의 칸 목록이 위 표와 같은지 확인한 다음 읽습니다.

```sql
SELECT number,
       datetime(date/1000, 'unixepoch') AS date_utc,
       duration, type, features, presentation,
       block_reason, subscription_id, name
FROM calls
ORDER BY date;
```

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [연락처](contacts.md) | `name` 에 남은 이름과 지금 연락처, 지운 연락처 기록 |
| [문자](messages/index.md) | 같은 번호와 앞뒤로 주고받은 문자 |
| [통화 녹음과 음성 사서함](call-recording-voicemail.md) | 같은 시각의 녹음 파일, `type` 4 행 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 전화 앱이 화면에 올라온 시각 |
| [알림 기록](../app-usage/notification-history.md) | 부재중 전화 알림 |
| [카카오톡](../messengers/kakaotalk/index.md) 같은 메신저 | 통화 기록에 없는 메신저 음성 통화 |

여러 기록을 한 줄로 합치는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에, 연락 관계를 재구성하는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 에 있습니다.

## 실습

NIST CFReDS 같은 곳에서 구할 수 있는 공개 안드로이드 검체로 아래 질문을 풀어 봅니다.

1. `calls` 표의 칸 목록을 위 표와 비교해 없는 칸과 더 있는 칸을 찾습니다.
2. `type` 이 6 인 행을 모두 찾고, `block_reason` 값으로 어떤 이유로 막혔는지 나눕니다.
3. 가장 이른 `date` 와 가장 늦은 `date` 를 한국 시각으로 바꾸고, 전화 계정별 행 수가 500 에 가까운지 봅니다.
4. `name` 에 이름이 있지만 지금 연락처에서 찾을 수 없는 번호가 있는지 봅니다.

## 참고 문헌

1. CallLog.Calls — Android Developers API reference. https://developer.android.com/reference/android/provider/CallLog.Calls
2. CallLogDatabaseHelper.java — AOSP ContactsProvider (main). https://raw.githubusercontent.com/aosp-mirror/platform_packages_providers_contactsprovider/main/src/com/android/providers/contacts/CallLogDatabaseHelper.java
3. CallLog.java — AOSP frameworks/base (main). https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/provider/CallLog.java
