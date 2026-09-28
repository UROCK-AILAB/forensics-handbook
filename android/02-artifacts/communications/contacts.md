---
title: "연락처"
parent: "아티팩트 · 통화·문자·연락처"
nav_order: 600
---

# 연락처 (contacts2.db)

`contacts2.db` 는 안드로이드 연락처 제공자가 쓰는 SQLite 데이터베이스이고, 계정별 원본 연락처와 그 안의 전화번호·이메일 같은 값, 여러 계정의 같은 사람을 하나로 묶은 결과, 그리고 지운 연락처의 ID 와 삭제 시각을 따로 적어 둡니다.

## 무엇을 기록하나 · 왜 생기나

연락처 앱이나 동기화 계정(구글·삼성 계정 등)이 연락처를 추가하면 연락처 제공자가 이 데이터베이스에 씁니다. 한 사람이라도 계정마다 원본 행이 따로 생기고, 제공자가 이 원본들을 묶어 화면에 보이는 연락처 하나로 만듭니다. 그래서 연락처 하나를 제대로 읽으려면 세 층을 차례로 따라가야 합니다.

| 층 | 소스 상수 | 담는 것 |
|---|---|---|
| 합쳐진 연락처 | `Tables.CONTACTS` | 화면에 보이는 연락처 하나 |
| 원본 연락처 | `Tables.RAW_CONTACTS` | 계정마다 따로 있는 원본 |
| 값 | `Tables.DATA` | 이름·전화번호·이메일 같은 실제 값 한 줄씩 |

통화 기록도 예전에는 이 데이터베이스 안에 있었지만 지금은 따로 떨어져 있습니다. 자세한 내용은 [통화 기록](call-log.md) 에 있습니다.

## 위치와 버전별 차이

AOSP 소스의 `ContactsDatabaseHelper` 가 이 데이터베이스를 만들고, 파일 이름은 `contacts2.db`, main 가지의 데이터베이스 버전은 1701 입니다[1]. 파일은 연락처 제공자(com.android.providers.contacts)의 데이터 폴더에 있을 것으로 보입니다. 실제 기기 경로와 프로필("내 정보")용 데이터베이스가 따로 있는지, 삼성 One UI 가 같은 제공자·경로를 쓰는지는 실제 기기에서 확인합니다. 앱 데이터 폴더 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 를 봅니다.

| 항목 | 내용 | 근거 |
|---|---|---|
| 파일 이름 | `contacts2.db` | AOSP main[1] |
| 데이터베이스 버전 | 1701 | AOSP main. 기기마다 다를 수 있음[1] |
| WAL | 시스템 설정으로 WAL(선행 기록 로그) 사용을 조절하는 코드가 있음 | [1] |
| 삭제 기록 표 | `deleted_contacts` | [2] |
| 삼성 One UI | 같은 경로인지, 휴지통 기능이 어디에 저장하는지 실제 기기에서 확인 | — |

WAL 을 쓸 수 있으므로 `contacts2.db` 만 떼어 오지 말고 `-wal`·`-shm` 파일을 함께 수집합니다. 최근 변경이 아직 본 파일에 합쳐지지 않고 WAL 에만 있을 수 있기 때문입니다.

## 구조

소스의 `Tables` 상수에 정의된 표는 아래와 같습니다[1]. 이 목록은 상수 이름을 소문자로 옮긴 것이고, 소스에 실제 표 이름 문자열까지 나오는 것은 `contacts`·`raw_contacts`·`data`·`mimetypes`·`deleted_contacts`·`data_usage_stat` 입니다[1]. 소스에는 `view_contacts`·`view_raw_contacts`·`view_data` 같은 뷰도 따로 있으니, 분석할 때는 먼저 `.tables` 로 실제 이름을 확인하고 뷰가 아닌 표를 읽습니다.

```text
contacts, raw_contacts, data, mimetypes, packages, phone_lookup,
name_lookup, groups, aggregation_exceptions, stream_items,
stream_item_photos, photo_files, deleted_contacts, search_index,
presence, aggregated_presence, status_updates, accounts, settings,
visible_contacts, default_directory, directories, pre_authorized_uris,
data_usage_stat
```

아래 열 이름도 소스 상수 이름이라 실제 열 문자열과 다를 수 있으니 `.schema` 로 확인합니다[1].

| 표 | 열(상수 이름) |
|---|---|
| 원본 연락처 | `_ID`, `ACCOUNT_ID`, `SOURCE_ID`, `BACKUP_ID`, `VERSION`, `DIRTY`, `DELETED`, `CONTACT_ID`, `DISPLAY_NAME_PRIMARY`, `DISPLAY_NAME_ALTERNATIVE`, `DISPLAY_NAME_SOURCE`, `SYNC1`~`SYNC4`, `STARRED`, `PINNED`, `CUSTOM_RINGTONE`, `SEND_TO_VOICEMAIL`, `LR_TIMES_CONTACTED`, `LR_LAST_TIME_CONTACTED` |
| 값 | `_ID`, `RAW_CONTACT_ID`, `MIMETYPE_ID`, `DATA1`~`DATA15`, `IS_PRIMARY`, `IS_SUPER_PRIMARY`, `SYNC1`~`SYNC4`, `PACKAGE_ID` |
| 합쳐진 연락처 | `_ID`, `NAME_RAW_CONTACT_ID`, `LOOKUP_KEY`, `CONTACT_LAST_UPDATED_TIMESTAMP`, `STARRED`, `PINNED`, `PHOTO_FILE_ID` |

값 표는 한 줄에 값 하나를 담고 `DATA1`~`DATA15` 라는 이름 없는 열을 씁니다. 그 줄이 전화번호인지 이메일인지는 `MIMETYPE_ID` 를 `mimetypes` 표와 이어 붙여야 알 수 있어서[1], 값 표만 보면 숫자와 글자가 뒤섞여 보입니다. mimetype 문자열은 이름이 `vnd.android.cursor.item/name`, 전화번호가 `vnd.android.cursor.item/phone_v2`, 이메일이 `vnd.android.cursor.item/email_v2` 로 정해져 있지만[3], ID 번호는 기기마다 다르므로 실제 기기에서 `mimetypes` 표를 직접 열어 짝을 확인합니다.

원본 연락처 표에는 `DELETED` 열이 있습니다. 동기화 계정의 연락처는 지워도 행이 바로 없어지지 않고 이 열에 표시만 된 채 서버와 맞출 때까지 남을 수 있다는 뜻으로 읽을 수 있습니다. 실제로 언제 행을 지우는지는 실제 기기에서 확인합니다. `LR_TIMES_CONTACTED`·`LR_LAST_TIME_CONTACTED` 는 연락 횟수와 마지막 연락 시각으로 보이고, 소스에는 옛 열을 `0 AS` 로 채워 돌려주는 코드가 있습니다[1].

### 지운 연락처 기록

`deleted_contacts` 표는 열이 두 개뿐입니다[2].

```sql
CREATE TABLE deleted_contacts (
  CONTACT_ID INTEGER PRIMARY KEY,
  CONTACT_DELETED_TIMESTAMP INTEGER NOT NULL default 0
)
```

위 문장은 소스의 상수 형태로 옮긴 것이고, 상수가 가리키는 실제 열 이름은 `contact_id`·`contact_deleted_timestamp` 입니다[3]. 제공자는 연락처를 지울 때 현재 시각을 밀리초로 넣고, `deleteOldLogs()` 가 `ContactsContract.DeletedContacts.DAYS_KEPT_MILLISECONDS` 보다 오래된 행을 지웁니다[2]. 이 값은 AOSP 에서 30일이고[3], 제조사 기기에서는 다를 수 있습니다.

## 증거로서 의미

**증명하는 것.** 원본 연락처와 값 표는 수집 시점에 어떤 계정으로 어떤 이름·번호가 저장되어 있었는지를 보여 줍니다. `deleted_contacts` 의 행은 그 ID 의 연락처를 해당 시각에 지웠다는 기록이고, 표가 보관 기간(AOSP 기준 30일) 안의 행만 남기므로 최근에 연락처를 지웠는지를 판단하는 근거가 됩니다. 반대로 행이 없다고 해서 30일보다 전에 지운 연락처가 없었다고 할 수는 없습니다.

**증명하지 못하는 것.** `deleted_contacts` 에는 연락처 ID 와 삭제 시각만 있고 이름이나 번호는 없습니다[2]. 지운 연락처가 누구였는지는 [통화 기록](call-log.md) 의 `name` 열처럼 다른 곳에 복사된 값이나 SQLite 복구 결과로 따로 찾아야 합니다. 연락처에 저장되어 있다는 사실이 그 사람과 연락했다는 뜻도 아니고, 계정 동기화로 다른 기기에서 넘어온 연락처일 수도 있으므로 원본 연락처의 계정 열을 함께 봅니다. 삭제 기록으로는 누가 지웠는지나 사용자가 직접 지웠는지, 동기화로 지워졌는지를 구분할 수 없습니다.

## 시각 해석

`deleted_contacts` 의 삭제 시각은 제공자가 `Clock.getInstance().currentTimeMillis()` 로 넣는 유닉스 밀리초라서[2] UTC 기준 값입니다. 기기 시계를 기준으로 하므로 기기 시각이 틀려 있었다면 그만큼 어긋납니다. 합쳐진 연락처의 `CONTACT_LAST_UPDATED_TIMESTAMP` 는 여러 단위로 풀어 보고 같은 기기의 다른 기록과 시각이 맞는 단위를 찾은 뒤에 씁니다. 변환 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을 봅니다.

## 함정과 한계

지운 연락처의 이름과 번호는 `deleted_contacts` 에 남지 않으므로, 원본 행까지 이미 지워졌다면 남은 조각은 SQLite 의 빈 페이지나 WAL 에서 찾아야 합니다. 원리는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에, 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.

삼성 기기에는 이름에 휴지통(trash bin)이 들어간 연락처 설정 키가 있어 삼성 연락처 앱의 휴지통 기능과 관련이 있어 보입니다. 그 기능이 지운 연락처를 어디에 얼마 동안 두는지는 실제 기기에서 확인합니다. 삼성 기기의 settings 목록에는 아래와 같은 연락처 관련 키가 있습니다.

| 영역 | 키 |
|---|---|
| global | `contact_setting_display_order`, `contact_setting_show_frequently_contacted`, `contact_setting_sort_order`, `contact_setting_trash_bin_on`, `favorite_contacts_view_as_list_tip`, `only_contact_with_phone`, `lock_screen_emergency_contacts_access`, `zen_selected_exception_contacts_allowed` |
| system | `contact_default_account`, `contacts_rad_value` |

`contact_setting_trash_bin_on` 이 그 키이고, 켜짐·꺼짐 값의 뜻은 단정하지 않습니다. 설정 값 읽는 법은 [설정 값](../system-account/settings.md) 에 있습니다.

`dumpsys user` 출력에는 사용자 프로필마다 `mUseParentsContacts` 필드가 있고, 이름으로 보면 부모 사용자와 연락처를 함께 쓰는지를 나타내는 것으로 보입니다. 보안 폴더나 작업 프로필이 있는 기기는 연락처가 프로필마다 따로 있을 수 있으니 [보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md) 과 [사용자와 프로필](../system-account/users-profiles.md) 을 함께 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래 바이트는 SQLite 레코드 형식 명세로 만든 예시이고, 실제 기기에서 가져온 값이 아닙니다. `deleted_contacts` 의 첫 열은 `INTEGER PRIMARY KEY` 라서 rowid 와 같은 값이 되고, 레코드 본문에는 NULL(직렬 형식 0)로 들어갑니다. 그래서 테이블 잎 셀 하나는 아래처럼 짧습니다.

```text
09                    페이로드 길이 9바이트
2A                    rowid = 42 (지운 연락처 ID)
03                    레코드 머리 길이 3바이트
00                    칸1 직렬 형식 0 (NULL, 값은 rowid)
05                    칸2 직렬 형식 5 (6바이트 정수)
01 95 55 45 4D 40     0x019555454D40 = 1740892360000 밀리초
                      = 2025-03-02 05:12:40 UTC
```

**공개 도구로 한 번.** SQLite 명령줄 도구(sqlite3)로 사본을 열어 표 이름과 열 이름부터 확인한 뒤 읽습니다. 열 이름이 다르면 `.schema` 결과에 맞춰 바꿉니다.

```sql
.tables
.schema deleted_contacts
SELECT rowid,
       datetime(contact_deleted_timestamp/1000, 'unixepoch') AS deleted_utc
FROM deleted_contacts
ORDER BY contact_deleted_timestamp;
```

값 표를 사람이 읽을 수 있게 보려면 값 표의 mimetype ID 를 `mimetypes` 표와 이어 붙이고, 원본 연락처 ID 로 원본 연락처 표와 이어 붙입니다. 열 이름은 `.schema data` 와 `.schema mimetypes` 결과를 보고 정합니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [통화 기록](call-log.md) | 통화 당시 복사된 이름과 지금 연락처, 지운 연락처 |
| [문자](messages/index.md) | 같은 번호와 주고받은 문자 |
| [계정](../system-account/accounts/index.md) | 연락처를 동기화한 계정과 계정 추가·삭제 시각 |
| [카카오톡](../messengers/kakaotalk/index.md) | 메신저 친구 목록과 전화번호 |
| [dumpsys 출력](../logs/dumpsys.md) | 알림마다 적힌 연락처 연관도 |

`dumpsys notification` 출력에는 알림마다 `mContactAffinity` 필드가 있습니다. 이름으로 보면 알림을 보낸 상대가 연락처와 얼마나 가까운지를 나타내는 값으로 보이지만, 계산 방법을 알 수 없는 값이라 보고서에는 값만 옮기고 가까운 정도를 단정하지 않습니다. 연락 관계를 정리하는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 에, 증거를 지우려 했는지 보는 흐름은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에 있습니다.

## 실습

NIST CFReDS 같은 곳에서 구할 수 있는 공개 안드로이드 증거물 이미지로 아래 질문을 풀어 봅니다.

1. `.tables` 결과를 위 표 목록과 비교해 이름이 다르거나 없는 표를 찾습니다.
2. `mimetypes` 표를 열어 전화번호와 이메일에 해당하는 ID 를 찾고, 값 표에서 전화번호만 뽑습니다.
3. `deleted_contacts` 의 삭제 시각을 한국 시각으로 바꾸고, 가장 오래된 행이 수집 시점보다 30일 넘게 앞서는지 봐서 보관 기간이 AOSP 와 같은지 확인합니다.
4. 원본 연락처 표에서 `DELETED` 에 해당하는 열이 켜진 행이 있는지, 있다면 어떤 계정의 행인지 봅니다.

## 참고 문헌

1. ContactsDatabaseHelper.java — AOSP ContactsProvider (main). https://raw.githubusercontent.com/aosp-mirror/platform_packages_providers_contactsprovider/main/src/com/android/providers/contacts/ContactsDatabaseHelper.java
2. DeletedContactsTableUtil.java — AOSP ContactsProvider (main). https://raw.githubusercontent.com/aosp-mirror/platform_packages_providers_contactsprovider/main/src/com/android/providers/contacts/database/DeletedContactsTableUtil.java
3. ContactsContract.java — AOSP frameworks/base (main). https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/provider/ContactsContract.java
