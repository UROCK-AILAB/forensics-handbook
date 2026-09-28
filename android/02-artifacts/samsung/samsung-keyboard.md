---
title: "삼성 키보드 입력 기록"
parent: "아티팩트 · 삼성 기기 전용"
nav_order: 1170
---

# 삼성 키보드 입력 기록 (Samsung Keyboard)

삼성 키보드는 클립보드에 들어간 글과 이미지를 `ClipItem.db` 의 `clip_table` 에 남기고, 화면 캡처를 클립보드에 넣으면 그 이미지를 JPEG 파일로 따로 저장해서, 사용자가 무엇을 언제 어느 앱과 관련해 복사했는지를 읽을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

지금 삼성 기기에 들어가는 삼성 키보드의 패키지 이름은 `com.samsung.android.honeyboard` 입니다. 삼성 키보드에는 클립보드 기능이 들어 있어서, 사용자가 복사한 글과 HTML, 이미지를 가리키는 URI 를 시각과 함께 데이터베이스에 쌓아 둡니다. 화면을 캡처해 클립보드에 넣은 "캡처 클립" 은 데이터베이스 밖에 이미지 파일로 저장됩니다.

공개 도구 ALEAPP 에는 이 흔적을 읽는 모듈(`samsung_honeyboard_clipboard.py`)이 있습니다. 이 모듈의 시험 표본은 Galaxy S20(Android 13), A53(Android 14), A15(Android 15) 입니다[1]. ALEAPP 는 데이터베이스의 WAL 파일까지 직접 읽어서 이미 지운 클립보드 항목도 되살립니다.

예전 삼성 키보드 패키지 `com.sec.android.inputmethod` 에는 사용자가 예측 단어 목록에서 지운 단어를 적어 두는 제외 목록이 있었습니다[2]. 이 목록은 사용자가 직접 한 행동의 기록이라서, 어떤 단어를 자주 쳤고 언제 지웠는지를 보여 준다는 해석이 있습니다[2]. 지금의 `honeyboard` 에도 이런 제외 목록이나 학습 단어 데이터베이스가 이어지는지는 실제 기기로 확인해야 합니다. 입력한 글 전체가 삼성 키보드에 남는다고 볼 근거는 없고, 이 점이 지보드와 다릅니다([지보드 입력 기록](../google-services/gboard.md)).

## 위치와 버전별 차이

| 패키지 | 경로 | 담긴 것 | 참고 |
|---|---|---|---|
| `com.samsung.android.honeyboard` | `*/com.samsung.android.honeyboard/databases/ClipItem.db` (함께 `ClipItem.db-wal`, `ClipItem.db-shm`) | 클립보드 기록 | [1] |
| `com.samsung.android.honeyboard` | `*/com.samsung.android.honeyboard/clipboard/*/clip` | 캡처 클립, 확장자 없는 JPEG | [1] |
| `com.sec.android.inputmethod` (예전) | `data/data/com.sec.android.inputmethod/databases/RemoveListManager` | 예측 단어 제외 목록 | [2] |
| `com.sec.android.inputmethod` (예전) | `data/data/com.sec.android.inputmethod/app_SwiftKey/user/blacklist` | SwiftKey 제외 목록, 한 줄에 한 단어인 텍스트 파일 | [2] |

앞의 두 줄은 ALEAPP 의 경로 패턴이라 앞부분이 `*` 로 되어 있습니다. 앱 데이터 폴더가 어떻게 짜여 있는지는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 를 봅니다. 예전 패키지의 두 경로가 어느 기종과 Android 판의 것인지는 알려져 있지 않습니다.

`clip_table` 에는 스키마가 두 가지 있고, 앱을 가리키는 열이 서로 다릅니다.

| 스키마 | 앱을 가리키는 열 | 값 |
|---|---|---|
| 새 스키마 | `caller_package_name` | 패키지 이름 문자열 |
| 옛 스키마 | `caller_app_uid` | 숫자 UID |

어느 One UI 판이나 키보드 판에서 스키마가 바뀌었는지는 알려져 있지 않아서, 기기마다 표 정의를 보고 구분합니다.

삼성 기기의 설정 값에는 키보드와 클립보드에 관련된 삼성 쪽 이름으로 보이는 아래 키가 있습니다. 키의 뜻은 시험 기기로 확인합니다. 기본 입력기를 가리키는 것으로 보이는 공통 키(`default_input_method` 등)는 [지보드 입력 기록](../google-services/gboard.md) 에 정리했습니다.

```
settings secure : sip_keyboard_type_mouse_id_list, sip_voice_input_use_side_key,
                  clipboard_show_access_notifications,
                  ltw_clipboard_sync_state, samsungflow_clipboard_sync_state
settings system : sip_key_feedback_sound, sip_key_feedback_vibration
settings global : navigation_bar_button_to_hide_keyboard
```

## 구조

저장 형식 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 를 봅니다. 아래는 ALEAPP 가 읽는 열만 정리한 것입니다.

### ClipItem.db 의 clip_table

| 열 | 뜻 |
|---|---|
| `id` | 행 번호 |
| `time_stamp` | 유닉스 밀리초 시각 |
| `type` | 항목 종류. 값마다의 뜻은 시험 기기에서 종류가 다른 항목을 복사해 보고 확인 |
| `text` | 클립보드 글 |
| `caller_package_name` 또는 `caller_app_uid` | 앱을 가리키는 열(위 스키마 표) |
| `user_id` | 사용자 번호. 열이 없으면 ALEAPP 는 0 으로 봄 |
| `html` | HTML 형식 글(열이 있을 때) |
| `uri` | 이미지 등을 가리키는 URI(열이 있을 때) |

`user_id` 가 0 이면 주 사용자이고, 150 이면 삼성 보안 폴더(Secure Folder)입니다. 보안 폴더가 어떤 구조인지는 [보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md) 에서 다룹니다.

옛 스키마의 `caller_app_uid` 는 숫자라서, `/data/system/packages.xml` 에서 같은 UID 를 찾아 패키지 이름으로 바꿉니다. Android 12 이후에는 `packages.xml` 이 바이너리 형식(ABX)일 수 있어서, 먼저 글자로 풀어야 합니다([설치된 앱](../app-usage/packages/index.md), [안드로이드 바이너리 XML](../../01-foundations/data-formats/abx.md), [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md)).

### WAL 에서 지운 항목 되살리기

ALEAPP 는 `ClipItem.db-wal` 의 WAL 프레임에 든 B-tree 페이지를 직접 읽어, 본 데이터베이스에서 이미 지운 클립보드 항목을 되살립니다. 같은 데이터베이스 페이지가 여러 프레임에 있으면 마지막 프레임만 읽어서 중간 상태가 겹쳐 나오지 않게 합니다. 그래서 한 페이지 안에서 마지막 프레임 전에만 있던 항목은 이 방식으로 나오지 않을 수 있습니다. WAL 이 어떻게 짜여 있는지는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서, 지운 행을 찾는 일반 방법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

### 캡처 클립 파일

캡처 클립은 `clipboard/` 아래 폴더마다 `clip` 이라는 확장자 없는 JPEG 로 들어 있고, 그 부모 폴더의 이름이 복사한 시각(유닉스 밀리초)입니다. JPEG 안의 EXIF `DateTimeOriginal` 과 `SubSecTimeOriginal` 에는 캡처한 시각이 들어 있습니다.

JPEG 끝 표지(`FF D9`) 뒤에는 삼성 전용 SEFT 꼬리가 붙습니다. 그 안의 `Captured_App_Info` 는 Base64 로 인코딩한 JSON 이고, JSON 의 `"comp"` 키가 캡처할 때 화면에 떠 있던 앱 구성요소를 가리킵니다. 값에서 슬래시 앞부분이 패키지 이름입니다.

### 예전 패키지의 제외 목록

`RemoveListManager` 데이터베이스의 `RemovedList` 표에는 `removed_word`(지운 단어)와 `time_word_added` 열이 있습니다. `time_word_added` 는 사람이 읽는 글자 형식으로 적혀 있습니다. SwiftKey 제외 목록 `blacklist` 는 한 줄에 한 단어씩 적은 텍스트 파일입니다.

## 증거로서 의미

### 증명하는 것

`clip_table` 의 한 행은 기록된 시각에 이 글이나 HTML, URI 가 삼성 키보드 클립보드에 들어가 있었다는 기록이고, `user_id` 로 주 사용자 쪽인지 보안 폴더 쪽인지를 구분할 수 있습니다. WAL 에서 되살린 항목은 사용자가 지우기 전까지 그런 항목이 클립보드에 있었다는 것을 보여 줍니다.

캡처 클립은 캡처한 시각과 클립보드에 넣은 시각을 따로 남기고, `"comp"` 값으로 캡처할 때 화면에 떠 있던 앱까지 알려 줍니다. 예전 패키지의 제외 목록은 사용자가 그 단어를 예측 목록에서 직접 지웠다는 기록이고, 그 단어를 자주 쳤다는 흔적으로 보는 해석도 있습니다[2].

### 증명하지 못하는 것

클립보드에 들어갔다는 기록만으로는 그 글을 어디에 붙여 넣었는지, 보냈는지 알 수 없어서 메신저나 메일 쪽 기록과 맞춰 봐야 합니다. ALEAPP 는 `caller_package_name` 을 앱을 가리키는 열로 읽지만, 그 앱이 복사한 앱인지 붙여 넣은 앱인지는 이 열만으로 단정할 수 없습니다. 누가 폰을 들고 복사했는지도 알 수 없습니다([그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)).

사용자가 친 글 전체가 남는다는 근거는 없어서, 삼성 키보드에서 입력 내용을 찾지 못했다고 입력이 없었다고 말할 수 없습니다. 클립보드 기록이 없다고 해서 복사하지 않았다고 말할 수도 없습니다. 항목을 얼마나 오래 두는지, 다른 키보드를 쓴 기간이 있었는지를 따로 확인해야 하기 때문입니다.

보고서에는 "이 글을 보냈다" 가 아니라 "이 시각에 삼성 키보드 클립보드에 이 글이 기록되어 있고, 앱 열 값은 이 패키지다" 처럼 씁니다.

## 시각 해석

| 위치 | 값 | 뜻 |
|---|---|---|
| `clip_table.time_stamp` | 유닉스 밀리초 | 클립보드 항목의 시각. ALEAPP 는 UTC 로 바꿈 |
| 캡처 클립의 부모 폴더 이름 | 유닉스 밀리초 | 클립보드에 복사한 시각 |
| 캡처 클립 EXIF `DateTimeOriginal` + `SubSecTimeOriginal` | 날짜·시각 글자 | 캡처한 시각 |
| `RemovedList.time_word_added` | 사람이 읽는 글자 | 제외 목록에 들어간 시각으로 보임 |

캡처 클립에서는 폴더 이름(복사한 때)과 EXIF 시각(캡처한 때)이 서로 다른 사건이라서, 두 값을 나란히 적으면 캡처하고 얼마 뒤에 복사했는지를 알 수 있습니다. EXIF 시각이 어느 시간대로 적히는지는 [카메라 사진과 메타데이터](../media/dcim-exif.md) 를 보고 기기 시간대와 함께 판단합니다([시간대와 시각 설정](../system-account/time-zone.md)).

`time_word_added` 는 실제 시각과 4시간 차이가 나서 UTC 로 보인다는 시험 결과가 있습니다[2]. 한 사람의 시험 결과이므로, 실제 기기에서는 시각을 알고 있는 항목 하나로 먼저 확인합니다. 유닉스 밀리초를 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

## 함정과 한계

스키마가 두 가지라서, 한쪽 열 이름으로 짠 쿼리는 다른 스키마에서 오류가 납니다. 먼저 표 정의를 보고 `caller_package_name` 과 `caller_app_uid` 중 어느 열이 있는지 확인합니다. 옛 스키마의 UID 를 패키지 이름으로 바꿀 때는 같은 기기의 `packages.xml` 을 써야 합니다.

`ClipItem.db-wal` 을 빠뜨리면 지운 항목을 되살릴 수 없고, 최근 항목이 빠질 수도 있습니다. 세 파일을 함께 복사하고, SQLite 도구로 열 때는 원본이 아닌 사본으로 엽니다. `user_id` 150 인 행은 보안 폴더 쪽 기록이라서, 주 사용자만 보고 끝내면 놓칩니다.

캡처 클립은 확장자가 없어서 확장자로 이미지를 찾는 검색에 걸리지 않습니다. 파일 머리의 JPEG 표지로 찾습니다. ALEAPP 표본은 Android 13~15 라서 Android 16 이후 판에서는 구조가 다를 수 있어 실제 기기로 확인합니다. adb 일반 권한으로는 앱 데이터 폴더를 읽을 수 없습니다. 예전 패키지의 제외 목록은 2019년 자료 하나[2]에만 나오는 내용이라서, 지금 기기에서는 없을 수 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 JPEG 끝 표지와 Base64 규칙으로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다. SEFT 꼬리의 세부 구조는 이 예시에서 생략했습니다.

```
.. .. FF D9                       JPEG 끝 표지(EOI). 여기부터 SEFT 꼬리
.. .. .. ..                       (SEFT 구조, 생략)
43 61 70 74 75 72 65 64 5F 41 70 70 5F 49 6E 66 6F
                                  "Captured_App_Info"
65 79 4A 6A 62 32 31 77 ...       "eyJjb21w..." Base64 글
```

뒤따르는 Base64 글이 아래와 같다고 합시다.

```
eyJjb21wIjoiY29tLmV4YW1wbGUubWVtby8uTWFpbkFjdGl2aXR5In0=
```

이 글을 Base64 로 풀면 41바이트 JSON 이 나옵니다.

```
{"comp":"com.example.memo/.MainActivity"}
```

슬래시 앞 `com.example.memo` 가 캡처할 때 화면에 떠 있던 앱의 패키지 이름입니다. 실제 파일에서는 `FF D9` 를 찾은 뒤 그 뒤에서 `Captured_App_Info` 글자를 찾고, 이어지는 Base64 글을 풀어 봅니다.

### 공개 도구로 한 번

1. 앱 데이터 폴더에서 `databases/ClipItem.db` 와 딸린 `-wal`, `-shm` 파일, `clipboard/` 폴더를 함께 복사합니다.
2. SQLite 도구로 사본을 열어 `clip_table` 의 표 정의를 보고, 앱을 가리키는 열이 어느 쪽인지 확인합니다.
3. 새 스키마라면 아래처럼 읽습니다.

```sql
SELECT id, datetime(time_stamp/1000, 'unixepoch') AS ts_utc, type, text,
       caller_package_name, user_id
FROM clip_table ORDER BY time_stamp;
```

4. ALEAPP 로 같은 폴더를 처리해, 3단계 결과와 행 수·시각을 맞춰 봅니다. ALEAPP 쪽에만 있는 행은 WAL 에서 되살린 항목일 수 있습니다.
5. 캡처 클립 몇 개를 골라 폴더 이름의 시각, EXIF 시각, `"comp"` 값을 ALEAPP 결과와 비교합니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [설정 값](../system-account/settings.md) | 그 기기의 기본 입력기가 삼성 키보드였는지 |
| [지보드 입력 기록](../google-services/gboard.md) | 다른 키보드를 쓴 기간과 그 기간의 입력 흔적 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 클립보드 시각에 앞에 떠 있던 앱 |
| [스크린샷과 화면 녹화](../media/screenshots.md) | 캡처 클립과 같은 시각의 스크린샷 파일 |
| [카카오톡](../messengers/kakaotalk/index.md) 등 메신저 | 복사한 글이 보낸 메시지로 남았는지 |

복사한 글이 밖으로 나갔는지 묻는 조사 흐름은 [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 를, 여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 을 봅니다.

## 실습

공개된 시험 이미지 가운데 Android 13 이후 삼성 기기 이미지를 골라 아래 질문을 풀어 봅니다.

1. `ClipItem.db` 의 `clip_table` 은 새 스키마입니까, 옛 스키마입니까? 옛 스키마라면 `caller_app_uid` 값을 `packages.xml` 로 패키지 이름으로 바꿔 봅니다.
2. `user_id` 가 150 인 행이 있습니까? 있다면 몇 개이고, 가장 이른 시각은 UTC 로 언제입니까?
3. SQLite 도구로 본 행 수와 ALEAPP 결과의 행 수가 다르다면, 차이 나는 항목은 WAL 에서 되살린 것입니까?
4. 캡처 클립 하나를 골라 폴더 이름의 시각과 EXIF 시각의 차이를 구하고, `"comp"` 값의 패키지를 적습니다.

## 참고 문헌

1. ALEAPP, scripts/artifacts/samsung_honeyboard_clipboard.py (GitHub main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/samsung_honeyboard_clipboard.py
2. Alexis Brignoni, "Android - Predictive text exclusions in Samsung devices" (2019-06) — https://abrignoni.blogspot.com/2019/06/android-predictive-text-exclusions-in.html
