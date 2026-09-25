---
title: "저장된 암호"
parent: "아티팩트 · 자격 증명·보안 설정"
nav_order: 1240
---

# 저장된 암호 (Google 비밀번호 관리자·Samsung Pass)

## 한 줄 요약

안드로이드에서 웹·앱 비밀번호는 브라우저, Google 비밀번호 관리자 (Google Password Manager), Samsung Pass 처럼 여러 곳에 저장될 수 있고, 이 가운데 구조를 소스로 확인할 수 있는 곳은 Chromium 계열 브라우저의 `Login Data` DB 와 어느 앱이 자동 완성을 맡는지 적어 두는 설정 키입니다 [2].

## 무엇을 기록하나 · 왜 생기나

Chromium 계열 브라우저는 사용자가 로그인 정보를 저장하면 사이트 주소, 아이디, 비밀번호 입력란 이름과 값, 만든 시각, 마지막으로 쓴 시각을 `logins` 표에 한 줄로 적습니다 [2]. 같은 DB 에는 유출·피싱·약한·재사용 비밀번호 표시를 담는 `insecure_credentials` 표와 로그인에 붙인 메모를 담는 `password_notes` 표도 있어서, 비밀번호 한 건을 두고 브라우저가 경고를 붙였는지, 사용자가 메모를 남겼는지까지 볼 수 있습니다 [2].

Android 쪽에는 이와 따로 자동 완성 서비스 (Autofill Service) 와 자격 증명 제공자 (Credential Provider) 를 고르는 설정이 있고, 관찰 기기에서는 이 설정이 settings secure 의 키로 남아 있었습니다. Google 비밀번호 관리자와 Samsung Pass 가 실제 비밀번호를 어느 파일에 어떤 모양으로 두는지는 이번 조사에서 확인하지 못했습니다. 그래서 이 페이지는 확인한 두 가지, 곧 브라우저 DB 구조와 설정 키를 중심으로 쓰고, 확인하지 못한 부분은 그렇다고 밝힙니다.

## 위치와 버전별 차이

Chromium 의 비밀번호 DB 는 파일이 두 가지이고, 프로필 저장소는 `Login Data`, 계정 저장소는 `Login Data For Account` 입니다 [2]. Android Chrome 에서 이 파일이 들어 있는 폴더는 확인하지 못했습니다. 같은 브라우저의 방문 기록 DB 는 ALEAPP 가 `*/app_chrome/Default/History*` 패턴으로 찾으니 [1] 그 프로필 폴더부터 살펴볼 만하지만, `Login Data` 가 같은 폴더에 있다고 확인한 것은 아닙니다. 앱 데이터 영역의 짜임새는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 페이지에서 다룹니다.

ALEAPP 의 chrome 모듈이 브라우저별로 찾는 폴더는 아래와 같고, 이 모듈은 History DB 만 읽고 `Login Data` 는 읽지 않습니다 [1].

```
app_chrome/Default     Chrome
app_sbrowser/Default   삼성 인터넷
app_opera              Opera
app_webview/Default    WebView
```

저장하는 쪽마다 확인한 범위가 다릅니다.

| 저장하는 쪽 | 확인한 것 | 확인하지 못한 것 |
|---|---|---|
| Chromium 계열 브라우저 | `Login Data`·`Login Data For Account` 파일 이름, 표와 칸 [2] | Android 에서의 전체 경로, `password_value` 가 암호화돼 있는지 |
| 삼성 인터넷 | ALEAPP 가 찾는 프로필 폴더 `app_sbrowser/Default` [1] | 저장 비밀번호 파일 |
| Google 비밀번호 관리자 | 없음 | 저장 파일 위치, Chrome 이 저장 비밀번호를 이쪽으로 옮기는지, 옮긴 뒤 `Login Data` 에 무엇이 남는지 |
| Samsung Pass | 관찰 기기 settings secure 에 `fingerprint_webpass` 키가 있음 | 패키지 이름, 저장 경로, DB 구조, 암호화 방식 |

관찰 기기의 `dumpsys package` 출력에서 Known Packages 목록의 `Browser:` 항목에는 com.android.chrome 이 있었습니다. 이 항목으로 시스템이 브라우저 역할에 어느 패키지를 두었는지 알 수 있지만, 사용자가 다른 브라우저에 비밀번호를 저장했을 가능성까지 지워 주지는 않습니다.

Android 버전이나 One UI 버전에 따라 저장 위치가 어떻게 바뀌었는지는 확인하지 못했습니다.

### 자동 완성·자격 증명 설정 키

관찰 기기에서 자동 완성과 자격 증명에 관련된 이름의 키는 아래와 같았습니다. 값은 관찰 메모에서 가려져 있어 키 이름만 확인했습니다.

| 설정 영역 | 키 |
|---|---|
| secure | `autofill_service`, `autofill_field_classification`, `autofill_service_search_uri`, `autofill_user_data_max_category_count` |
| secure | `credential_service`, `credential_service_primary`, `save_previous_credential_description_show_count` |
| secure | `fingerprint_webpass`, `fingerprint_used_samsungaccount` |
| global | `autofill_compat_mode_allowed_packages`, `autofill_logging_level` |
| system | `show_password` |

`autofill_service` 값이 "패키지/서비스 클래스" 모양이라는 설명과 `credential_service` 가 자격 증명 제공자 목록이라는 설명은 문서로 확인하지 못했고, `fingerprint_webpass`·`fingerprint_used_samsungaccount` 는 이름으로 보아 지문과 웹 로그인·삼성 계정에 관련돼 보이지만 뜻은 모릅니다. `show_password` 는 비밀번호를 입력할 때 글자를 보여 줄지 정하는 설정으로 보이고, 저장된 비밀번호와는 다른 것으로 봐야 합니다. 설정 키를 읽는 법과 저장 파일은 [설정 값](../system-account/settings.md) 페이지에서 다룹니다.

## 구조

`Login Data` 의 `logins` 표에 있는 칸을 묶으면 아래와 같습니다(현행 Chromium main 기준) [2]. SQLite 파일 형식 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에서 다룹니다.

| 묶음 | 칸 |
|---|---|
| 식별 | `id` |
| 사이트 | `origin_url`, `action_url`, `signon_realm`, `scheme`, `federation_url` |
| 입력란과 값 | `username_element`, `username_value`, `password_element`, `password_value`, `submit_element`, `form_data`, `possible_username_pairs` |
| 표시 | `display_name`, `icon_url` |
| 시각 | `date_created`, `date_last_used`, `date_password_modified`, `date_last_filled`, `date_received` |
| 사용·상태 | `times_used`, `blacklisted_by_user`, `password_type`, `skip_zero_click`, `generation_upload_status`, `moving_blocked_for`, `keychain_identifier`, `actor_login_approved` |
| 공유 | `sender_email`, `sender_name`, `sender_profile_image_url`, `sharing_notification_displayed` |

칸 이름은 소스로 확인했지만 칸마다 뜻을 소스 주석으로 확인하지는 않았습니다. `blacklisted_by_user` 는 "이 사이트는 저장하지 않음" 을 고른 항목으로 알려져 있으나 확인하지 못했고, 공유 묶음은 다른 사람에게서 받은 비밀번호로 보이지만 이름에서 짐작한 것입니다. 보고서에 칸의 뜻을 적을 때는 이 점을 밝힙니다.

같은 DB 의 다른 표는 아래와 같습니다 [2].

| 표 | 담긴 것 |
|---|---|
| `insecure_credentials` | 유출·피싱·약한·재사용 비밀번호 표시. `parent_id` 로 `logins` 에 이어짐 |
| `password_notes` | 로그인 한 건에 붙인 메모 |
| `sync_entities_metadata`, `sync_model_metadata` | 동기화 상태 정보 |

## 증거로서 의미

**증명하는 것**

`logins` 에 줄이 있으면 이 브라우저 프로필에 해당 사이트의 로그인 정보가 저장돼 있다는 뜻이고, `username_value` 로 어떤 아이디였는지, `date_created`·`date_last_used` 로 언제 저장하고 언제 마지막으로 썼는지, `times_used` 로 몇 번 썼는지 기록된 값을 읽을 수 있습니다. `insecure_credentials` 에 이어진 줄이 있으면 브라우저가 그 비밀번호에 유출·피싱·약함·재사용 가운데 하나의 표시를 붙였다는 기록이 됩니다. 계정 탈취가 의심되는 사건이라면 이 표시와 그 시점이 [계정 탈취 흔적 (Account Takeover)](../../04-scenarios/incident/account-takeover.md) 분석의 단서가 됩니다.

**증명하지 못하는 것**

저장된 줄은 그 기기에서 사람이 직접 입력했다는 증거가 아닙니다. 계정 저장소 파일(`Login Data For Account`)과 동기화 표가 따로 있으니, 같은 계정의 다른 기기에서 넘어온 항목일 수 있는지 먼저 따져 봅니다. 마지막 사용 시각은 브라우저가 그 값을 채우거나 쓴 기록이지 로그인에 성공했다는 기록이 아니고, 저장된 비밀번호가 지금도 맞는지도 알려 주지 않습니다. 브라우저 DB 에 흔적이 없어도 Google 비밀번호 관리자나 Samsung Pass 에 저장돼 있을 수 있어서, 한 곳이 비었다고 "저장된 비밀번호가 없다" 고 쓰면 안 됩니다.

`dumpsys account` 의 Accounts History 에 `action_clear_password` 줄이 보일 수 있지만, 이 줄은 AccountManager 계정 기록이고 브라우저나 비밀번호 관리자의 저장 암호와는 다른 것입니다. 이 기록은 [계정 (Accounts)](../system-account/accounts/index.md) 페이지에서 다룹니다.

## 시각 해석

`logins` 의 시각 칸은 Chromium 의 base::Time 값이고, 1601-01-01 부터 센 마이크로초입니다 [2]. 1601-01-01 과 1970-01-01 사이는 11644473600 초라서, 1,000,000 으로 나눈 뒤 이 값을 빼면 유닉스 초가 됩니다. 이 값이 UTC 기준인지와 Chrome 시각 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지를 따르고, 현지 시각으로 옮길 때는 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 에서 기기 시간대를 먼저 확인합니다.

시각 칸이 다섯 개라서 무엇이 바뀔 때 어느 칸이 바뀌는지 구분해야 하지만, 칸 이름 말고 갱신 조건은 소스로 확인하지 못했습니다. 이름으로 보면 `date_created` 는 저장한 때, `date_password_modified` 는 비밀번호를 바꾼 때, `date_last_used`·`date_last_filled` 는 쓰거나 채운 때로 보이니, 보고서에는 "이 칸의 값이 이 시각이다" 까지만 씁니다. 값이 0 이면 그 사건이 기록되지 않았다는 뜻으로 보고 날짜로 바꾸지 않습니다.

`dumpsys account` 의 timestamp 칸 형식은 관찰 메모에서 가려져 있어 확인하지 못했습니다.

## 함정과 한계

첫째, Android 에서 `password_value` 가 평문인지 암호화돼 있는지 확인하지 못했습니다. 이 핸드북은 비밀번호를 풀어내는 방법을 다루지 않고, 저장돼 있다는 사실과 시각·사이트·아이디 같은 주변 기록을 해석하는 데 그칩니다.

둘째, Chrome 이 저장 비밀번호를 Google Play 서비스 쪽으로 옮겼는지에 따라 `Login Data` 에 남는 내용이 달라질 수 있지만, 이 부분은 확인하지 못했습니다. 최신 기기에서 `logins` 가 비어 있거나 적다면 그 차이 자체를 기록해 둡니다.

셋째, Samsung Pass 는 저장 위치와 구조를 전혀 확인하지 못했습니다. 설정 키가 있다는 사실만으로 Samsung Pass 를 썼다고 말할 수 없고, 관찰 기기에서는 키 이름만 봤습니다.

넷째, 공개 도구가 이 DB 를 다 읽어 준다고 기대하지 않습니다. ALEAPP 의 chrome 모듈은 `Login Data` 를 읽지 않고 [1], 다른 모듈이 읽는지는 확인하지 못했습니다.

다섯째, 사용자가 브라우저에서 저장 비밀번호를 지우면 `logins` 줄이 사라지지만, SQLite 는 지운 레코드가 빈 페이지나 WAL 파일에 남을 수 있습니다. 복구 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) 페이지에 있습니다.

## 직접 분석해 보기

### SQL 로 한 번

`Login Data` 사본을 SQLite 도구로 열고, 비밀번호 값은 빼고 사이트·아이디·시각만 읽습니다. 아래 질의는 위 구조 표로 만든 예시입니다.

```sql
SELECT l.id,
       l.origin_url,
       l.username_value,
       datetime(l.date_created   / 1000000 - 11644473600, 'unixepoch') AS created_utc,
       datetime(l.date_last_used / 1000000 - 11644473600, 'unixepoch') AS last_used_utc,
       l.times_used,
       l.blacklisted_by_user,
       (SELECT COUNT(*) FROM insecure_credentials i WHERE i.parent_id = l.id) AS insecure_marks
FROM logins l
ORDER BY l.date_created;
```

`Login Data For Account` 가 함께 있으면 같은 질의를 한 번 더 돌려 두 파일의 사이트 목록을 맞춰 봅니다. 원본이 아니라 사본을 열고, 같은 폴더의 `-wal`·`-journal` 파일도 함께 복사합니다. 헥스로 페이지를 따라가는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에서 설명합니다.

### 설정 키 한 번

adb 일반 셸 권한으로도 설정 키 목록을 읽을 수 있고, 관찰 기기의 키 이름도 이렇게 얻었습니다.

```
adb shell settings list secure
adb shell settings list global
adb shell settings list system
```

출력에서 위 표의 키를 찾아 값을 기록하되, 값의 형식은 이 페이지에서 확인하지 못했으니 보고서에는 읽은 값을 그대로 옮깁니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [크롬 (Chrome for Android)](../browsers/chrome/index.md) | `logins` 의 사이트를 방문 기록에서 같은 시간대에 찾을 수 있는지 |
| [삼성 인터넷 (Samsung Internet)](../browsers/samsung-internet.md) | 기본 브라우저가 아닌 쪽에도 로그인 흔적이 있는지 |
| [계정 (Accounts)](../system-account/accounts/index.md) | 동기화 계정이 언제 추가됐는지, `Login Data For Account` 와 시기가 맞는지 |
| [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) | 자동 완성·자격 증명 제공자로 어느 앱이 지정돼 있는지 |
| [설치된 앱 (packages.xml)](../app-usage/packages/index.md) | 설정 키가 가리키는 앱이 실제로 설치돼 있는지, 언제 설치됐는지 |

웹 사용 흐름 전체는 [웹 사용 행위 재구성 (Web Activity)](../../04-scenarios/activity/web-activity.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 검체에 Chrome 앱 데이터가 들어 있으면 아래 질문을 풀어 봅니다.

1. Chrome 프로필 폴더에 `Login Data` 와 `Login Data For Account` 가운데 어느 파일이 있고, 각각 `logins` 가 몇 줄입니까?
2. `date_created` 가 가장 이른 줄과 가장 늦은 줄은 어느 사이트이고, UTC 로 언제입니까?
3. `insecure_credentials` 에 이어진 줄이 있다면 어느 로그인에 붙어 있습니까?
4. 같은 사이트를 History DB 에서 찾으면 `date_last_used` 와 가까운 시각에 방문 기록이 있습니까?
5. 검체에 설정 파일이 있으면 `autofill_service` 값이 가리키는 앱은 무엇입니까?

## 참고 문헌

1. ALEAPP — scripts/artifacts/chrome.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chrome.py
2. Chromium — components/password_manager/core/browser/password_store/login_database.cc — https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/password_manager/core/browser/password_store/login_database.cc
