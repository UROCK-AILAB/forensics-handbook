---
title: "쿠키와 자동 완성"
parent: "크롬"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 860
---

# 쿠키와 자동 완성 (Cookies·Autofill)

## 한 줄 요약

Chrome for Android 의 쿠키는 프로필 폴더의 `Cookies` SQLite 파일에, 입력란에 넣었던 값(자동 완성)과 주소 프로필은 `Web Data` SQLite 파일에 들어 있고, 두 파일은 시각 기준이 서로 달라서 쿠키는 1601년 기준 마이크로초, 자동 완성은 유닉스 초로 읽습니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

쿠키는 사이트가 브라우저에 맡겨 둔 값이라서, 어느 도메인이 언제 쿠키를 만들었고 언제 마지막으로 읽었는지를 보여 줍니다 [1]. 자동 완성은 사용자가 웹 양식의 입력란에 넣은 값을 Chrome 이 다음에 다시 제안하려고 입력란 이름과 함께 저장한 것이고, 같은 파일에 이름·전화번호·주소 같은 주소 프로필도 들어 있습니다 [2].

저장된 비밀번호(Login Data)와 결제 카드 정보를 포함한 저장된 암호 전반은 [저장된 암호 (Google 비밀번호 관리자·Samsung Pass)](../../credentials-security/saved-passwords.md) 페이지를 봅니다.

## 위치와 버전별 차이

| 파일 | 경로 | 비고 |
|---|---|---|
| Cookies | `app_chrome/Default/Cookies` | ALEAPP 는 이름이 정확히 `Cookies` 인 파일만 엽니다 [1] |
| Web Data | `app_chrome/Default/Web Data` | 파일 이름에 빈칸이 있습니다 [2] |

Android 에서도 데스크톱 Chrome 처럼 쿠키 파일이 `Default/Network/Cookies` 로 옮겨져 있을 수 있지만, ALEAPP 의 경로 패턴은 `Default/Cookies*` 만 찾습니다 [1]. 경로가 다른 기기라면 프로필 폴더 전체에서 `Cookies` 라는 이름을 찾아봅니다. 패키지 이름과 앱 데이터 폴더, WebView 를 쓰는 다른 앱이 같은 이름의 파일을 남기는 경우는 [크롬 (Chrome for Android)](index.md) 허브를 봅니다. WebView 가 만든 `Web Data` 에는 autofill 표가 아예 없을 수 있습니다 [2].

Web Data 의 표 구성은 Chrome 버전에 따라 옛 형식과 새 형식으로 나뉘고, ALEAPP 는 `PRAGMA table_info` 로 열이 있는지 보고 두 형식을 모두 읽습니다 [2].

| 구분 | 옛 형식 | 새 형식 |
|---|---|---|
| 자동 완성 입력값 | autofill 표에 date_created 열이 없고, autofill_dates 표(pair_id 로 연결)에 date_created 가 있음 | autofill 표에 name, value, date_created, date_last_used, count 열 |
| 주소 프로필 | autofill_profiles 표와 autofill_profile_names, autofill_profile_emails, autofill_profile_phones 표(guid 로 연결) | addresses 표(guid, date_modified, use_date, use_count)와 address_type_tokens 표(guid, type, value) |

## 구조

### cookies 표

ALEAPP 는 host_key, name, value, path, creation_utc, expires_utc, last_access_utc 열을 읽습니다 [1].

| 열 | 뜻 |
|---|---|
| host_key | 쿠키가 속한 도메인 |
| name, value | 쿠키 이름과 값 |
| path | 쿠키가 적용되는 경로 |
| creation_utc | 만든 시각 |
| expires_utc | 만료 시각 |
| last_access_utc | 마지막으로 읽은 시각 |

ALEAPP 는 value 열만 읽고 encrypted_value 열은 읽지 않습니다 [1]. 쿠키 값이 암호화되어 encrypted_value 에만 들어 있을 수 있으니, value 가 비어 있다고 쿠키 값이 없었다고 말하지 않습니다.

### autofill 표(새 형식)

| 열 | 뜻 |
|---|---|
| name | 입력란 이름 |
| value | 입력한 값 |
| date_created | 처음 저장한 시각 |
| date_last_used | 마지막으로 쓴 시각 |
| count | 쓴 횟수 |

옛 형식에서는 처음 저장한 시각을 autofill_dates 표에서 pair_id 로 이어 찾습니다 [2].

### 주소 프로필

옛 형식의 autofill_profiles 표에는 date_modified, use_date, use_count, company_name, street_address, city, state, zipcode 같은 열이 있고, 이름과 이메일, 전화번호는 guid 로 이어진 곁 표에 있습니다 [2].

새 형식은 addresses 표 한 행이 프로필 하나이고, 이름이나 도시 같은 값은 address_type_tokens 표에 (guid, type, value) 한 줄씩 들어 있습니다. type 은 Chromium 의 FieldType 번호이고, ALEAPP 가 보고하는 번호는 아래 10개입니다 [2].

| type | 이름 |
|---|---|
| 3 | NAME_FIRST |
| 4 | NAME_MIDDLE |
| 5 | NAME_LAST |
| 9 | EMAIL_ADDRESS |
| 14 | PHONE_HOME_WHOLE_NUMBER |
| 33 | ADDRESS_HOME_CITY |
| 34 | ADDRESS_HOME_STATE |
| 35 | ADDRESS_HOME_ZIP |
| 60 | COMPANY_NAME |
| 77 | ADDRESS_HOME_STREET_ADDRESS |

ALEAPP 는 이 10개 말고 다른 번호(ADDRESS_HOME_COUNTRY, NAME_FULL 등)는 보고하지 않아서 [2], 도구 결과에 나라나 전체 이름이 없더라도 표에는 남아 있을 수 있습니다. local_addresses 라는 표도 있지만, ALEAPP 는 시험 이미지 두 개에서 이 표가 비어 있어 읽지 않습니다 [2].

## 증거로서 의미

| 기록 | 말할 수 있는 것 | 말할 수 없는 것 |
|---|---|---|
| 쿠키 host_key 와 creation_utc | 그 시각에 이 프로필의 Chrome 에 그 도메인의 쿠키가 만들어졌다 | 사용자가 그 사이트를 직접 열었다는 것(쿠키가 생긴 경위는 이 표에 없음) |
| last_access_utc | 그 시각에 Chrome 이 쿠키를 읽은 기록 | 사람이 그 순간 화면을 보고 있었다는 것 |
| autofill 의 name·value | 그 입력란 이름으로 그 값이 저장되었다 | 어느 사이트의 양식이었는지(표에 사이트 열이 없음) |
| date_last_used·count | 마지막으로 쓴 시각과 쓴 횟수 | 쓸 때마다의 시각 |
| 주소 프로필 | 이 프로필에 저장된 이름·연락처·주소 | 그 사람이 기기 사용자라는 것 |

자동 완성과 주소 프로필에는 개인 정보가 그대로 들어 있어서 보고서에 옮길 때는 사건에 필요한 항목만 적습니다. 계정 탈취나 다른 사람의 로그인 흔적을 따지는 사건은 [계정 탈취 흔적 (Account Takeover)](../../../04-scenarios/incident/account-takeover.md) 시나리오를 봅니다.

## 시각 해석

cookies 표의 creation_utc, expires_utc, last_access_utc 는 1601-01-01 부터의 마이크로초이고, ALEAPP 는 1,000,000 으로 나눈 뒤 1601-01-01 의 유닉스 초를 더해 바꾸며 0 이면 빈칸으로 둡니다 [1]. 계산 예시와 헥스 모양은 [방문 기록 (History)](history.md) 페이지에 있습니다.

Web Data 의 date_created, date_last_used(autofill 표)와 date_modified, use_date(주소 프로필)는 ALEAPP 가 유닉스 초로 읽습니다 [2]. 같은 Chrome 의 파일이라도 History·Cookies 와 기준이 달라서, 두 파일의 시각을 한 타임라인에 올릴 때는 열마다 기준을 따로 적어 두고 바꿉니다. 시각 형식은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

## 함정과 한계

원본 파일 옆에 `-journal` 파일이 있으면 읽기 전용으로 열 때 실패할 수 있고 ALEAPP 는 이런 파일을 건너뜁니다 [1][2]. 사본을 만드는 방법과 이유는 [방문 기록 (History)](history.md) 페이지의 함정 절에 있습니다.

expires_utc 는 만료 시각이라 사용자가 언제 무엇을 했는지 보여 주는 열이 아닙니다. autofill 표에는 사이트 열이 없어서 값이 어느 사이트에서 입력되었는지는 이 표만으로 알 수 없고, 같은 시각 근처의 [방문 기록 (History)](history.md)에서 양식 제출(transition 7, FORM_SUBMIT) 방문을 찾아 맞춰 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다. autofill 의 date_created 가 2025-01-01 00:00:00 UTC 라면 유닉스 초 1,735,689,600 이고 16진수로 `0x67748580` 이라서, SQLite 레코드 안에서는 4바이트 정수로 아래처럼 보입니다.

```
67 74 85 80    date_created = 1735689600 (유닉스 초) = 2025-01-01 00:00:00 UTC
```

같은 시각이 Cookies 의 creation_utc 라면 1601년 기준 마이크로초라서 8바이트 `00 2F 89 30 02 92 A0 00` 으로 보입니다. 바이트 길이와 크기가 이만큼 달라서, 헥스에서 시각 값을 찾을 때 기준을 먼저 정해 두면 헷갈리지 않습니다. 레코드 헤더를 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) 페이지를 봅니다.

### 공개 도구로 한 번

사본을 sqlite3 명령줄이나 DB Browser for SQLite 로 열어 쿠키와 자동 완성을 따로 봅니다. 결과는 ALEAPP 의 쿠키, 자동 완성 결과와 나란히 놓고 맞춰 봅니다.

```sql
-- Cookies 파일
SELECT host_key, name, path,
       datetime(creation_utc/1000000 - 11644473600, 'unixepoch')    AS created_utc,
       datetime(last_access_utc/1000000 - 11644473600, 'unixepoch') AS last_access_utc
FROM cookies ORDER BY creation_utc;

-- Web Data 파일(새 형식)
SELECT name, value, count,
       datetime(date_created, 'unixepoch')   AS created_utc,
       datetime(date_last_used, 'unixepoch') AS last_used_utc
FROM autofill ORDER BY date_last_used;

-- Web Data 파일(새 형식 주소 프로필)
SELECT a.guid, t.type, t.value,
       datetime(a.use_date, 'unixepoch') AS use_utc, a.use_count
FROM addresses a JOIN address_type_tokens t ON t.guid = a.guid;
```

옛 형식 DB 에서는 autofill 표에 date_created 열이 없어서 첫 번째 Web Data 질의가 오류를 내니, `PRAGMA table_info(autofill);` 로 열을 먼저 확인합니다.

## 교차 검증

쿠키의 도메인과 시각은 [방문 기록 (History)](history.md)의 같은 도메인 방문과 맞춰 보고, 자동 완성 값은 같은 시각 근처의 양식 제출 방문과 대 봅니다. 주소 프로필의 이름·전화번호가 기기의 [연락처 (contacts2.db)](../../communications/contacts.md)나 [계정 (Accounts)](../../system-account/accounts/index.md)과 겹치는지도 확인합니다. 키보드가 따로 남긴 입력 기록은 [지보드 입력 기록 (Gboard)](../../google-services/gboard.md), [삼성 키보드 입력 기록 (Samsung Keyboard)](../../samsung/samsung-keyboard.md) 페이지를 봅니다.

## 실습

Chrome 이 깔린 공개 Android 실습 이미지로 아래 질문을 풀어 봅니다.

1. cookies 표에서 creation_utc 가 가장 이른 도메인 다섯 개를 뽑고, 같은 도메인의 첫 방문 시각과 비교합니다.
2. Web Data 가 옛 형식인지 새 형식인지 `PRAGMA table_info` 로 판별합니다.
3. address_type_tokens 에서 ALEAPP 가 보고하지 않는 type 번호가 있는지 찾아봅니다.
4. autofill 의 date_last_used 와 가장 가까운 FORM_SUBMIT 방문을 찾아, 값이 어느 사이트에서 입력되었을지 근거와 함께 적어 봅니다.

## 참고 문헌

1. ALEAPP `scripts/artifacts/chromeCookies.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chromeCookies.py
2. ALEAPP `scripts/artifacts/chromeAutofill.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chromeAutofill.py
