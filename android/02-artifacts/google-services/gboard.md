---
title: "지보드 입력 기록"
parent: "아티팩트 · 구글 입력·음성 비서"
nav_order: 1180
---

# 지보드 입력 기록 (Gboard)

## 한 줄 요약

구글 키보드 앱인 지보드(Gboard)는 앱 데이터 폴더의 SQLite 데이터베이스에 클립보드 항목과 키 입력 캐시, 입력 세션을 남기고, 여기서 사용자가 복사한 글과 입력칸에 친 글, 입력한 앱과 시각을 읽을 수 있습니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

지보드의 패키지 이름은 `com.google.android.inputmethod.latin` 이고, 흔적은 이 앱의 데이터 폴더 아래 `databases/` 와 `files/` 에 남습니다. 흔적은 클립보드(Clipboard), 키 입력 캐시(Keystroke Cache), 세션(Sessions) 세 갈래로 나뉘고, 공개 도구 ALEAPP 도 이 셋을 모듈 하나씩으로 따로 읽습니다 [1].

클립보드 데이터베이스에는 지보드 클립보드에 들어간 글과 HTML 글, 이미지를 가리키는 URI, 고정(Pinned) 여부가 시각과 함께 남습니다. 키 입력 캐시에는 입력한 글자와 맞춤법 실수, 고친 내용, 키보드가 띄운 추천 단어가 남고, 이미 지운 앱이나 사라진 메시지, 웹 입력칸에 쳤던 내용이 남아 있기도 합니다 [2]. 다만 비밀번호 입력칸은 기록하지 않고, 백스페이스(지우기)도 기록하지 않습니다 [2].

파일 이름에 training(학습)이 들어 있지만, 어떤 설정(개인 맞춤 학습 등)일 때 이 캐시가 생기는지, 시크릿 모드에서는 어떻게 동작하는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 삼성 기기에서 어떤 키보드가 기본으로 설정됐는지는 기기마다 설정 값으로 확인해야 하고, 삼성 자체 키보드의 흔적은 [삼성 키보드 입력 기록](../samsung/samsung-keyboard.md) 에서 다룹니다.

## 위치와 버전별 차이

아래 경로는 모두 앱 데이터 폴더 `/data/data/com.google.android.inputmethod.latin/` 기준입니다. 앱 데이터 폴더가 어떻게 짜여 있는지는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 를 봅니다.

| 파일(ALEAPP 경로 패턴) | 표 | 담긴 것 | ALEAPP 모듈 |
|---|---|---|---|
| `databases/gboard_clipboard.db*` | `clips` | 클립보드 항목 | Gboard - Clipboard |
| `files/clipboard_image/*` | (파일) | 클립보드에 들어간 이미지 | Gboard - Clipboard |
| `databases/trainingcache2.db`, `databases/trainingcache3.db` | `training_input_events_table` | 키 입력 이벤트 | Gboard - Keystroke Cache |
| `databases/trainingcachev2.db` | `input_action_table`, `session_table` | 키 입력 동작과 세션 | Gboard - Keystroke Cache |
| `databases/trainingcachev3.db` | `session` | 입력 세션 | Gboard - Sessions |

키 입력 캐시의 파일 이름은 지보드 판에 따라 달라집니다. 알려진 파일은 trainingcache2.db, trainingcache3.db, trainingcachev2.db, trainingcache4.db 이고, 그중 trainingcache4.db 에는 의미 있는 자료가 없었습니다 [2]. 아래는 기본 설정의 Pixel 3 로 시험한 판입니다 [2].

| 지보드 판 | Android | 비고 |
|---|---|---|
| 8.3.6.250752527 | 10 | |
| 8.8.10.277552084 | 10 | |
| 10.0.02.338070508 | 11 | trainingcache3.db 에 `s_table`, `tf_table` 도 있음 |
| Android 12 이후 판 | 12 이후 | 공개 자료 없음 |
| 삼성 One UI 기기 | — | 공개 자료 없음 |

어느 판이 어떤 파일 이름을 쓰는지는 정리된 자료가 없으니, 새 기기에서는 `databases/` 아래 `trainingcache` 로 시작하는 파일을 모두 열어 표 이름부터 확인합니다.

기기 쪽 설정에도 키보드와 관련된 키 이름이 보입니다. 아래 키 이름은 adb 일반 권한으로 읽을 수 있습니다.

```
settings secure : default_input_method, enabled_input_methods,
                  input_methods_subtype_history, selected_input_method_subtype,
                  selected_spell_checker, selected_spell_checker_subtype,
                  default_voice_input_method, default_device_input_method,
                  show_ime_with_hard_keyboard
settings global : touch_keyboard, keyboard_dex
settings system : keyboard_vibration_enabled, sip_speak_keyboard_input_aloud
```

키 이름으로 보아 secure 쪽 키들은 기본 입력기와 켜 둔 입력기를 가리키는 것으로 보입니다. 값의 형식과 global·system 쪽 키의 뜻은 검체에서 확인합니다. 설정 값 전체는 [설정 값](../system-account/settings.md) 에서 다룹니다.

## 구조

저장 형식 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 와 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 페이지를 봅니다. 아래는 ALEAPP 가 읽는 칸만 정리한 것입니다 [1].

### 클립보드 — gboard_clipboard.db 의 clips 표

| 칸 | 뜻 |
|---|---|
| `timestamp` | 유닉스 밀리초 시각 |
| `text` | 클립보드 글 |
| `html_text` | HTML 형식 글 |
| `uri` | 이미지 등을 가리키는 URI |
| `item_type` | 0 이면 빈칸, 1 이면 'Pinned'(고정한 항목), 그 밖의 값은 숫자 그대로 |
| `entity_type` | 0 이면 빈칸, 1 이면 'Link', 그 밖의 값은 숫자 그대로 |
| `_id` | 행 번호 |

ALEAPP 는 `uri` 칸에서 마지막 '/' 뒤의 이름만 떼어 내 `files/clipboard_image/` 아래 이미지 파일과 잇습니다 [1]. 이 이미지 파일의 형식과 이름 규칙은 공개 자료가 없어 검체에서 확인합니다.

```sql
replace(uri, rtrim(uri, replace(uri, '/', '')), '')
```

### 키 입력 캐시 — trainingcache2.db, trainingcache3.db

`training_input_events_table` 한 행에는 입력 당시 앞에 떠 있던 앱과 입력이 들어간 칸의 이름, 시각, 키 입력이 든 `_payload` 가 함께 들어 있습니다. 앱 칸에는 Gmail 같은 앱이 들어갑니다 [2].

| 칸 | 뜻 |
|---|---|
| `_id` | 행 번호 |
| `_payload` | 키 입력이 든 프로토콜 버퍼 BLOB |
| `f2` | 앱 |
| `f4` | 입력칸 이름 |
| `f5` | 입력칸 ID |
| `f9` | 유닉스 밀리초 시각 |

ALEAPP 는 `_payload` 를 프로토콜 버퍼로 풀어 필드 '7' 안의 필드 '2' 에서 글자 항목들을 꺼내고, 각 항목의 필드 '1' 을 UTF-8 로 풀어 이어 붙입니다. 백스페이스를 기록하지 않아서 이렇게 글자를 다시 이어 붙여야 하고, 지운 부분은 글 끝에 붙어 나옵니다 [2].

10.0.02.338070508 판의 trainingcache3.db 에는 이 밖에 `s_table` 과 `tf_table` 이 더 있습니다. `tf_table` 은 키를 하나씩 담는데 `f1` 이 세션 ID, `f3` 이 키 데이터, `f4` 가 키 순서이고, ALEAPP 는 두 표를 읽지 않습니다.

### 키 입력 캐시 — trainingcachev2.db

이 파일에는 `input_action_table` 과 `session_table` 이 있고, ALEAPP 는 `_payload`, `_timestamp`(유닉스 밀리초), `_session_id`, `_id` 칸을 읽습니다. 두 표는 세션 ID 로 묶습니다 [1].

```sql
input_action_table i LEFT JOIN session_table s ON s._session_id = i._session_id
```

### 세션 — trainingcachev3.db 의 session 표

칸은 `_session_id`, `_timestamp_`, `package_name` 입니다. `_session_id` 값 자체가 유닉스 밀리초 시각이라서 ALEAPP 는 이 칸도 시각으로 바꿔 보여 주고, `_timestamp_` 도 유닉스 밀리초입니다. `package_name` 은 입력이 이뤄진 앱입니다.

## 증거로서 의미

### 증명하는 것

키 입력 캐시의 한 행은 기록된 시각에 그 앱의 그 입력칸에 지보드로 이런 글자가 입력된 기록이 있다는 뜻입니다. 이미 지운 앱이나 사라진 메시지의 입력 내용이 남아 있을 수 있어서, 앱 쪽 기록이 없어진 뒤에도 입력 흔적을 찾는 길이 되기도 합니다. 클립보드 표의 한 행은 그 시각에 이 글이나 링크, 이미지가 지보드 클립보드에 들어갔고, `item_type` 이 1 이면 사용자가 고정해 둔 항목이라는 기록입니다. 세션 표는 어느 앱에서 지보드 입력 세션이 열렸는지를 시각과 함께 보여 줍니다.

### 증명하지 못하는 것

입력한 글이 실제로 보내지거나 저장됐는지는 이 기록만으로 알 수 없어서, 메신저나 메일 앱 쪽 기록과 맞춰 봐야 합니다. 누가 폰을 들고 입력했는지도 알 수 없습니다([그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)). 비밀번호 입력칸은 기록하지 않고 캐시는 주기적으로 지워지며 크기 제한도 있는 것으로 보여서, 캐시에 없다고 해서 입력이 없었다고 말할 수는 없습니다. ALEAPP 가 읽는 클립보드 칸에는 복사한 앱이 없어서, 어느 앱에서 복사했는지도 이 표만으로는 알 수 없습니다.

보고서에는 "이 메시지를 보냈다" 가 아니라 "이 시각에 이 앱의 이 입력칸에서 지보드 캐시에 이런 글자가 기록되어 있다" 처럼 씁니다.

## 시각 해석

| 파일·표 | 칸 | 값 | ALEAPP 변환 |
|---|---|---|---|
| gboard_clipboard.db `clips` | `timestamp` | 유닉스 밀리초 | `datetime(timestamp/1000,'unixepoch')` |
| trainingcache2·3.db `training_input_events_table` | `f9` | 유닉스 밀리초 | `datetime(f9/1000, "unixepoch")` |
| trainingcachev2.db | `_timestamp` | 유닉스 밀리초 | — |
| trainingcachev3.db `session` | `_session_id`, `_timestamp_` | 유닉스 밀리초 | `datetime(_session_id / 1000, 'unixepoch')` |

ALEAPP 의 `unixepoch` 변환 결과는 UTC 라서, 현지 시각으로 옮길 때는 기기 시간대를 따로 확인합니다([시간대와 시각 설정](../system-account/time-zone.md)). 유닉스 밀리초를 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

클립보드 시각이 복사한 때인지 고정한 때인지, 세션 표의 두 시각이 세션 시작과 마지막 기록 중 무엇을 뜻하는지는 공개 자료가 없습니다. 그래서 이 시각들은 "이 시각 값이 기록되어 있다" 까지만 쓰고, 다른 기록으로 뒷받침합니다.

## 함정과 한계

키 입력 캐시의 파일 이름과 표 구조가 판마다 달라서, 한 판에서 확인한 쿼리를 다른 판에 그대로 쓰면 빈 결과가 나올 수 있습니다. Android 12 이후 판과 삼성 기기에서의 모양은 공개 자료가 없어 검체로 확인해야 합니다.

ALEAPP 는 `_payload` 에서 필드 '7'·'2'·'1' 만 풀고 나머지 필드는 보여 주지 않습니다. 백스페이스가 기록되지 않아 지운 글자가 끝에 붙어 나와서, 복원한 글은 사용자가 최종으로 남긴 글과 다를 수 있습니다.

캐시는 주기적으로 지워지고 크기 제한도 있는 것으로 보이지만, 주기와 크기, 고정하지 않은 클립보드 항목을 두는 기간은 알려져 있지 않습니다. 사용자가 클립보드를 비우거나 앱 데이터를 지운 뒤 사라진 행은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 방법으로 따로 찾아봅니다. ALEAPP 경로 패턴은 파일 이름 뒤에 `*` 가 붙어 있어 같은 이름으로 시작하는 파일을 모두 잡으니, 수집할 때 딸린 파일까지 함께 가져옵니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 프로토콜 버퍼 인코딩 규칙으로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. `_payload` 안에서 필드 '7' 아래 필드 '2' 항목 두 개가 "안" 과 "녕" 을 담는 모양을 보여 줍니다. 필드 태그 바이트는 필드 번호를 왼쪽으로 3비트 밀고 형식 번호 2(길이가 붙는 형식)를 더한 값입니다.

```
3A 0E                     필드 7, 길이 14
   12 05                  필드 2, 길이 5   (첫 글자 항목)
      0A 03 EC 95 88      필드 1, 길이 3, UTF-8 "안"
   12 05                  필드 2, 길이 5   (둘째 글자 항목)
      0A 03 EB 85 95      필드 1, 길이 3, UTF-8 "녕"
```

필드 '1' 의 값을 차례로 이어 붙이면 "안녕" 이 됩니다. 실제 `_payload` 에는 이 밖의 필드도 섞여 있을 수 있어서, `3A` 로 시작하는 필드 '7' 을 먼저 찾고 그 안을 차례로 풉니다. 프로토콜 버퍼를 읽는 자세한 방법은 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 에 있습니다.

### 공개 도구로 한 번

1. 앱 데이터 폴더 `databases/` 와 `files/clipboard_image/` 를 딸린 파일까지 함께 복사합니다.
2. SQLite 도구로 각 파일을 열어 표 목록을 보고, 위 표와 같은 이름이 있는지 확인합니다.
3. 클립보드는 아래처럼 시각을 바꿔 읽습니다.

```sql
SELECT datetime(timestamp/1000,'unixepoch') AS ts_utc, text, html_text, uri,
       item_type, entity_type, _id
FROM clips ORDER BY timestamp;
```

4. ALEAPP 로 같은 폴더를 처리하면 클립보드 결과는 Timestamp, Text, HTML Text, URI, Image, Item Type, Entity Type, ID 칸으로, 키 입력 캐시 결과는 Source, Event Timestamp, ID, Text, App, Input Name, Input ID 칸으로, 세션 결과는 시각으로 바꾼 `_session_id`, `_timestamp_`, Session ID, Application 칸으로 나옵니다.
5. 2단계에서 직접 읽은 값과 ALEAPP 결과를 몇 행 골라 맞춰 봅니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [설정 값](../system-account/settings.md) | 그 기기에서 지보드가 기본 입력기로 켜져 있었는지 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 키 입력 캐시의 시각에 그 앱이 앞에 떠 있었는지(ACTIVITY_RESUMED 등). 키보드 앱 자체가 여기에 찍히는 모양은 검체에서 확인 |
| [카카오톡](../messengers/kakaotalk/index.md) 등 메신저 | 입력한 글이 실제 보낸 메시지로 남았는지 |
| [크롬](../browsers/chrome/index.md) | 웹 입력칸에 친 글과 같은 시각의 방문·검색 기록 |
| [삼성 키보드 입력 기록](../samsung/samsung-keyboard.md) | 삼성 기기에서 다른 키보드를 쓴 기간 |

여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 을, 복원한 글로 낱말을 찾는 방법은 [콘텐츠 검색](../../03-techniques/analysis/content-search.md) 을 봅니다.

## 실습

공개 검체 가운데 지보드가 깔린 Android 이미지를 골라 아래 질문을 풀어 봅니다.

1. `databases/` 아래 `trainingcache` 로 시작하는 파일은 무엇무엇이고, 각 파일에는 어떤 표가 있습니까?
2. `training_input_events_table` 의 `f2` 칸에 나오는 앱은 몇 개이고, 가장 이른 `f9` 시각과 가장 늦은 시각은 UTC 로 언제입니까?
3. `_payload` 하나를 골라 헥스로 필드 '7'·'2'·'1' 을 따라가 풀고, ALEAPP 의 Text 칸과 같은지 확인합니다.
4. `clips` 표에서 `item_type` 이 1 인 항목은 몇 개이고, `uri` 가 있는 항목은 `files/clipboard_image/` 의 어느 파일과 이어집니까?
5. 세션 표의 `package_name` 과 키 입력 캐시의 앱 목록이 서로 맞습니까?

## 참고 문헌

1. ALEAPP, scripts/artifacts/gboard.py (GitHub main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/gboard.py
2. Yogesh Khatri, "Gboard has some interesting data..", Swift Forensics, 2021-01-09 — https://www.swiftforensics.com/2021/01/gboard-has-some-interesting-data.html
