---
title: "통화 녹음과 음성 사서함"
parent: "아티팩트 · 통화·문자·연락처"
nav_order: 610
---

# 통화 녹음과 음성 사서함 (Call Recording·Voicemail)

기기 안에 저장된 음성 사서함은 통화 기록 표의 한 행과 확장자 없는 음성 파일 한 개로 남고, 통화 녹음은 제조사 기능이라서 삼성 기기에서는 녹음 설정 키와 공용 저장 공간의 `Recordings` 폴더부터 확인합니다.

## 무엇을 기록하나 · 왜 생기나

두 가지는 이름이 비슷해도 만드는 쪽이 다릅니다. 음성 사서함(Voicemail)은 AOSP 연락처 제공자가 관리해서, 메시지 한 건이 [통화 기록](call-log.md) 의 `calls` 표에 종류 값 4(음성 사서함) 행으로 들어가고 음성 파일은 제공자 데이터 폴더에 따로 저장됩니다[2][3]. 통화 녹음(Call Recording)은 AOSP 쪽 저장 규약이 공개 자료에 없고, 삼성 기기에는 전화 앱의 녹음 기능과 관련된 설정 키가 있습니다.

## 위치와 버전별 차이

| 대상 | 알려진 것 | 실제 기기에서 확인할 것 |
|---|---|---|
| 음성 사서함 기록 | `calllog.db` 의 `calls` 표, `type` = 4 인 행[1][2] | 삼성 기기에서 같은 표를 쓰는지 |
| 음성 사서함 상태 | 같은 데이터베이스의 `voicemail_status` 표[1] | 열 목록 |
| 음성 사서함 파일 | `voicemail-data` 라는 비공개 폴더에 확장자 없이 저장[2] | 실제 기기 경로, 음성 형식 |
| 통화 녹음 설정 | 삼성 녹음 관련 settings 키가 있음 | 각 키 값의 뜻 |
| 통화 녹음 파일 | `/sdcard` 최상위에 `Recordings` 폴더가 있음 | 하위 폴더, 파일 형식, 파일 이름 규칙 |

음성 사서함 파일을 만드는 코드는 `mContext.getDir(DATA_DIRECTORY, Context.MODE_PRIVATE)` 이고, `DATA_DIRECTORY` 값은 `"voicemail-data"` 입니다[2]. `getDir` 는 앱 데이터 폴더 안에 이름 앞에 `app_` 을 붙인 폴더를 만드는 함수라서, 파일은 연락처 제공자(com.android.providers.contacts) 데이터 폴더의 `app_voicemail-data` 폴더에 있을 가능성이 높습니다. 앱 데이터 폴더 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 에, `/sdcard` 구조는 [공용 저장 공간](../../01-foundations/storage/shared-storage.md) 에 있습니다.

한국 통신사의 음성 사서함이 기기 안에 파일로 내려오는지(비주얼 보이스메일·OMTP 방식인지)는 실제 기기에서 확인합니다. 음성 사서함 행이 하나도 없다면 기능을 쓰지 않았다기보다 통신사 서버에만 메시지가 있었을 가능성부터 따져 봅니다.

## 구조

### 음성 사서함 행

음성 사서함 쪽 코드는 `calls` 표에서 `Calls.TYPE = Calls.VOICEMAIL_TYPE` 조건으로 행을 골라 보여 줍니다[2]. 이 코드가 드러내는 열의 상수 이름은 아래와 같습니다[2].

```text
_ID, NUMBER, DATE, DURATION, NEW, IS_READ, TRANSCRIPTION,
TRANSCRIPTION_STATE, STATE, SOURCE_DATA, SOURCE_PACKAGE, HAS_CONTENT,
PHONE_ACCOUNT_COMPONENT_NAME, PHONE_ACCOUNT_ID, MIME_TYPE, DIRTY,
DELETED, LAST_MODIFIED, BACKED_UP, RESTORED, ARCHIVED,
IS_OMTP_VOICEMAIL, DISPLAY_NAME, SIZE
```

이 가운데 `number`·`date`·`duration`·`new`·`is_read`·`transcription`·`last_modified` 처럼 통화 기록과 같은 열은 실제 열 이름을 [통화 기록](call-log.md) 에서 확인할 수 있고, 나머지 음성 사서함 전용 열의 실제 문자열은 실제 기기에서 확인합니다. `SOURCE_PACKAGE` 는 이름으로 보면 메시지를 넣은 음성 사서함 앱을, `MIME_TYPE` 은 음성 파일 형식을 가리키는 열로 보이므로 실제 기기에서 `.schema calls` 로 실제 이름을 찾아 읽습니다.

### 음성 파일

제공자는 `File.createTempFile("voicemail", "", dataDirectory)` 로 파일을 만들어서[2], 파일 이름은 "voicemail" 뒤에 임의 숫자가 붙고 확장자가 없습니다. 파일의 절대 경로는 행의 `_DATA` 상수가 가리키는 열에 들어갑니다[2]. 그래서 폴더에서 파일을 먼저 찾기보다 행에서 경로를 읽어 파일과 짝을 짓는 편이 정확하고, 행이 없는 파일이나 파일이 없는 행이 있으면 따로 적어 둡니다.

## 증거로서 의미

**증명하는 것.** 음성 사서함 행은 해당 번호에서 온 음성 사서함 메시지를 기기가 받아 저장했다는 기록이고, 짝이 되는 파일이 남아 있으면 메시지 내용까지 들어 볼 수 있습니다. `new`·`is_read` 로 사용자가 확인했는지, `transcription` 으로 받아쓴 글이 있는지 봅니다. 녹음 설정 키가 있다는 것은 그 기기의 펌웨어에 통화 녹음 설정 자리가 있다는 흔적입니다.

**증명하지 못하는 것.** 녹음 설정 키가 있다는 것만으로 자동 녹음이 켜져 있었다거나 특정 통화를 녹음했다고 말할 수 없고, 키 값을 따로 읽어야 합니다. `Recordings` 폴더가 있다는 것도 표준 폴더가 만들어져 있다는 뜻일 뿐 녹음 파일이 있다는 뜻은 아닙니다. 녹음 파일이 있더라도 파일 이름에 상대 번호나 시각이 들어가는지 밝힌 공개 문서가 없으므로, 어느 통화의 녹음인지는 [통화 기록](call-log.md) 의 시각·통화 길이와 맞춰 본 뒤에 씁니다.

## 시각 해석

음성 사서함 행의 `date` 는 통화 기록과 같은 열이라서 유닉스 밀리초이고 UTC 기준입니다. 읽는 법은 [통화 기록](call-log.md) 의 시각 해석 절과 같습니다. 음성 파일과 녹음 파일의 만든 시각·바꾼 시각은 파일 시스템 시각이라서 [파일 시스템](../../01-foundations/storage/filesystems/index.md) 에 있는 규칙을 따르고, 파일을 복사하거나 백업에서 되살리면 바뀔 수 있습니다. 녹음 파일이 [미디어 저장소](../media/mediastore/index.md) 에 등록되어 시각이 따로 남는지는 실제 기기에서 확인합니다.

## 함정과 한계

제공자가 음성 사서함 행을 지울 때는 연결된 음성 파일을 `file.delete()` 로 먼저 지웁니다[2]. 행을 먼저 지우면 파일을 찾을 길이 없어지기 때문입니다[2]. 그러므로 지운 음성 사서함은 행과 파일이 함께 사라지고, 되살리려면 SQLite 쪽 흔적과 파일 시스템 쪽 흔적을 따로 찾아야 합니다. 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.

통화 녹음은 제조사와 One UI 판에 따라 다를 수 있습니다. 삼성 기기의 settings 에는 아래 녹음 관련 키가 있고, 공개된 설명이 없어 뜻은 이름으로 짐작만 할 수 있습니다.

| 영역 | 녹음 관련 키 |
|---|---|
| system | `record_call_storage_setting_value`, `record_calls_automatically_on_off`, `record_calls_automatically_type`, `record_calls_notification_on_off`, `recording_calls_repeat_notification`, `simultaneous_recording_calls`, `automatic_rejection_of_recording_calls`, `add_info_com_sec_android_app_voicenote#record` (# 자리에 숫자가 들어감) |
| global | `call_recording_support`, `call_recording_auto_record_support`, `call_recording_config_version`, `call_recording_disclaimer`, `call_recording_ui_type` |

이름으로 짐작하면 자동 녹음 켜짐·꺼짐, 자동 녹음 대상, 저장 위치를 정하는 키입니다. `add_info_com_sec_android_app_voicenote` 라는 이름으로 보면 삼성 음성 녹음 앱(com.sec.android.app.voicenote)이 관련될 가능성이 있습니다. 설정 값 읽는 법은 [설정 값](../system-account/settings.md) 에 있습니다.

통화 중 AI 기능과 관련 있어 보이는 키도 있습니다.

| 영역 | 키 |
|---|---|
| global | `screen_call`, `screen_call_voice`, `translate_during_calls`, `do_not_show_call_transcript_badge`, `do_not_show_on_device_voicemail_badge` |
| system | `call_transcript`, `call_transcript_language`, `on_device_voicemail_send_to_voicemail_on_off` |

`call_transcript` 나 `on_device_voicemail_…` 같은 이름은 통화 내용을 글로 받아 적거나 기기 안에서 음성 사서함을 받는 기능을 떠올리게 하지만, 그 결과가 어디에 어떤 형식으로 남는지 설명한 공개 문서는 없습니다. 이런 기능을 켠 기기라면 통화 기록의 `transcription` 열 말고도 전화 앱 자기 데이터 폴더를 따로 살펴봅니다.

일반 앱이 통화 음성을 녹음하지 못하게 막는 제한이 Android 버전에 따라 있을 수 있으므로, 제3자 녹음 앱의 파일이 있다면 그 앱이 실제로 상대 목소리까지 녹음했는지는 파일을 들어 보고 판단합니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래 바이트는 SQLite 레코드 형식 명세로 만든 예시이고, 실제 기기에서 가져온 값이 아닙니다. 음성 사서함 행의 `type` 값 4 는 SQLite 가 1바이트 정수(직렬 형식 1)로 저장하므로, 레코드 머리의 해당 자리에 `01`, 본문의 해당 자리에 `04` 가 보이면 음성 사서함 행입니다.

```text
레코드 머리: ... 01 ...      type 칸 직렬 형식 1 (1바이트 정수)
레코드 본문: ... 04 ...      type = 4 (음성 사서함)
```

음성 파일은 확장자가 없으므로 헥스 편집기로 앞부분을 열어 어떤 음성 형식의 머리인지 확인하고, 행의 `MIME_TYPE` 열 값과 맞는지 봅니다.

**공개 도구로 한 번.** SQLite 명령줄 도구(sqlite3)로 `calllog.db` 사본을 열어 음성 사서함 행만 뽑습니다. 음성 사서함 전용 열은 `.schema calls` 결과를 보고 덧붙입니다.

```sql
SELECT number,
       datetime(date/1000, 'unixepoch') AS date_utc,
       duration, new, is_read, voicemail_uri, transcription
FROM calls
WHERE type = 4
ORDER BY date;
```

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [통화 기록](call-log.md) | 녹음 파일 시각과 통화 시각·길이 |
| [배터리 사용 기록](../app-usage/batterystats.md) | 오디오 사용 구간 |
| [미디어 저장소](../media/mediastore/index.md) | 녹음 파일이 등록되었는지 |
| [공용 저장 공간](../../01-foundations/storage/shared-storage.md) | `Recordings` 폴더 아래 파일 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 녹음 앱·전화 앱이 화면에 올라온 시각 |
| [구글 백업](../mail-cloud/google-backup.md), [삼성 클라우드와 원드라이브](../mail-cloud/samsung-cloud-onedrive.md) | 기기에서 지운 녹음이 백업에 남았는지 |

`dumpsys batterystats` 이력에는 오디오를 쓰기 시작하고 멈춘 구간을 보여 주는 `+audio`·`-audio` 표시가 남습니다. 이 표시만으로는 통화 녹음인지 알 수 없으므로, 통화 기록의 시각과 겹치는지를 보는 보조 자료로만 씁니다. 연락 관계를 정리하는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 에 있습니다.

## 실습

NIST CFReDS 같은 곳에서 구할 수 있는 공개 안드로이드 증거물 이미지로 아래 질문을 풀어 봅니다.

1. `calls` 표에서 `type` 이 4 인 행을 찾고, 음성 파일 경로 열과 실제 파일이 짝을 이루는지 봅니다.
2. 짝이 없는 음성 파일이나 파일이 없는 행이 있다면 어느 쪽이 먼저 사라졌는지 설명해 봅니다.
3. `/sdcard/Recordings` 아래에 파일이 있다면 파일 시각을 통화 기록의 `date`·`duration` 과 맞춰 어느 통화의 녹음인지 좁혀 봅니다.
4. settings 에서 녹음 관련 키의 값을 읽고, 값이 바뀌면 무엇이 달라지는지 시험 기기로 확인할 계획을 세웁니다.

## 참고 문헌

1. CallLogDatabaseHelper.java — AOSP ContactsProvider (main). https://raw.githubusercontent.com/aosp-mirror/platform_packages_providers_contactsprovider/main/src/com/android/providers/contacts/CallLogDatabaseHelper.java
2. VoicemailContentTable.java — AOSP ContactsProvider (main). https://raw.githubusercontent.com/aosp-mirror/platform_packages_providers_contactsprovider/main/src/com/android/providers/contacts/VoicemailContentTable.java
3. CallLog.java — AOSP frameworks/base (main). https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/provider/CallLog.java
