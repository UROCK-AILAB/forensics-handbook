---
title: "자동완성·폼 기록"
parent: "크롬 계열 브라우저"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1660
---

# 자동완성·폼 기록 (Web Data·Autofill)

## 한 줄 요약

크롬 계열 브라우저는 웹 폼에 입력해 제출한 값을 프로필 폴더의 `Web Data` 파일에 저장합니다. 이 파일은 SQLite 데이터베이스입니다. `autofill` 표에는 입력란 이름, 입력한 값, 처음 저장한 시각, 마지막으로 쓴 시각, 쓴 횟수가 남습니다. 사용자가 저장한 주소와 결제 카드도 같은 파일의 다른 표에 있습니다. 어느 사이트에서 입력했는지는 남지 않습니다.

## 무엇을 기록하나 · 왜 생기나

브라우저는 예전에 입력한 값을 다시 제안해서 입력을 줄여 줍니다. 이 기능은 두 갈래입니다.

| 기능 | 저장하는 것 | 주요 표 |
|---|---|---|
| 자동완성 (Autocomplete) | 입력란 하나의 이름과 값 한 쌍 | `autofill` |
| 자동 채우기 (Autofill) | 주소·카드처럼 여러 입력란을 한 번에 채우는 묶음 | 주소 표, `credit_cards` 등 |

Chromium 소스는 입력란 하나짜리를 Autocomplete, 묶음을 Autofill 로 부르는데, 자동완성 항목을 담는 표의 이름은 `autofill` 이라서 둘을 헷갈리기 쉽습니다.

Chromium 소스를 보면 자동완성 항목은 아래 조건에서만 생깁니다.

- 폼을 제출할 때 저장합니다. 입력만 하고 제출하지 않은 값은 남지 않습니다.
- 글자를 넣는 입력란만 저장합니다. 비밀번호 입력란과 숫자 입력란은 저장하지 않습니다.
- 페이지가 그 입력란의 자동완성을 막았으면(예: `autocomplete="off"`) 저장하지 않습니다.
- 비었거나 공백뿐인 값은 저장하지 않습니다.
- 값이 카드 번호, 국제 계좌 번호 (IBAN), 미국 사회보장번호 (SSN) 모양이면 저장하지 않습니다.
- 설정에서 자동완성을 끄면 저장하지 않습니다.
- 시크릿 창 (Incognito) 에서 제출한 폼은 저장하지 않습니다.

같은 이름과 값을 다시 제출하면 새 행이 생기지 않고, 기존 행의 `count` 가 1 늘며 `date_last_used` 가 그때 시각으로 바뀝니다. `date_created` 는 그대로입니다.

주소와 카드는 사용자가 브라우저에 저장한 정보입니다. 계정 쪽에 저장된 카드는 번호를 가린 사본으로 따로 남습니다.

## 위치와 버전별 차이

| 브라우저 | 파일 |
|---|---|
| Chrome | `%LOCALAPPDATA%\Google\Chrome\User Data\<프로필>\Web Data` |
| Edge | `%LOCALAPPDATA%\Microsoft\Edge\User Data\<프로필>\Web Data` |
| Whale | `%LOCALAPPDATA%\Naver\Naver Whale\User Data\<프로필>\Web Data` |

- `<프로필>` 자리에는 `Default`, `Profile 1` 같은 폴더 이름이 옵니다.
- 파일 이름에는 확장자가 없습니다. 이름 가운데에 빈칸이 있습니다.
- 같은 폴더에 이름 뒤에 `-journal` 이나 `-wal` 이 붙은 파일이 있으면 함께 꺼냅니다. 이유는 [WAL과 롤백 저널](../../../01-foundations/database-log-formats/sqlite/wal-journal-shm.md)에서 다룹니다.
- 명령줄 옵션 `--user-data-dir` 로 User Data 위치를 바꿀 수 있습니다.
- 프로필 폴더 고르기와 계열 브라우저 구분은 [프로필 폴더와 계열 브라우저 구분](../../../01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md)에서 다룹니다.

표 구성은 브라우저 버전보다 `Web Data` 의 스키마 버전 (Schema Version) 을 따릅니다. 스키마 버전은 `meta` 표의 `version` 행에 있습니다. 이 번호는 브라우저 버전과 따로 매깁니다. 먼저 이 값을 읽고 표 목록(`sqlite_master`)을 확인합니다.

아래는 Chromium 소스의 이전 (Migration) 코드에서 확인한 주소 표의 변화입니다.

| 스키마 버전 | 바뀐 점 |
|---|---|
| 107 | 계정 주소를 담는 `contact_info` 계열 표가 생깁니다 |
| 113 | 옛 `autofill_profiles` 계열 표의 주소를 새 표로 옮깁니다 |
| 114 | `autofill_profiles`·`autofill_profile_names`·`autofill_profile_emails`·`autofill_profile_phones`·`autofill_profile_addresses`·`autofill_profile_birthdates` 표를 지웁니다 |
| 121 | `server_addresses` 표를 지웁니다 |
| 134 | 기기 주소(`local_addresses`)와 계정 주소(`contact_info`)를 `addresses`·`address_type_tokens` 두 표로 합칩니다 |
| 145 | 주소 표에서 보조 사용 시각 열을 뺍니다 |

자동완성 표는 훨씬 오래전에 한 번 바뀌었습니다. 공개 도구 Hindsight 의 소스는 Chrome 35 이상에서 `autofill` 표의 `date_created`·`date_last_used` 를 바로 읽습니다. 그보다 옛 버전에서는 `autofill_dates` 표를 `pair_id` 로 이어 붙여 `date_created` 만 얻습니다.

## 구조

저장 형식은 보통의 SQLite 입니다. 페이지와 레코드 구조는 [파일·페이지 구조](../../../01-foundations/database-log-formats/sqlite/b-tree-record-format.md)에서 다룹니다. 여기서는 표와 열의 뜻만 봅니다.

### autofill 표 (자동완성)

| 열 | 형식 | 뜻 |
|---|---|---|
| `name` | VARCHAR | 입력란 이름입니다. 웹 페이지가 정한 이름이라 사이트마다 다릅니다(예: `email`, `q`) |
| `value` | VARCHAR | 제출한 값입니다. 평문입니다 |
| `value_lower` | VARCHAR | 값을 소문자로 바꾼 것입니다. 대소문자 없이 찾을 때 씁니다 |
| `date_created` | INTEGER, 기본값 0 | 이 이름·값 쌍을 처음 저장한 시각입니다 |
| `date_last_used` | INTEGER, 기본값 0 | 마지막으로 제출한 시각입니다 |
| `count` | INTEGER, 기본값 1 | 제출한 횟수입니다 |

기본 키는 (`name`, `value`) 이라서 같은 값이라도 입력란 이름이 다르면 다른 행입니다. 색인은 `name` 하나짜리와 (`name`, `value_lower`) 짜리가 있습니다. 사이트 주소, 페이지 제목, 사용자 이름을 담는 열은 없습니다. 사이트 안 검색창도 폼 입력란이라서 검색어가 `q` 같은 이름으로 남을 수 있습니다.

### 주소 표 (스키마 134 이후)

| 표 | 열 | 뜻 |
|---|---|---|
| `addresses` | `guid`, `use_count`, `use_date`, `date_modified`, `language_code`, `label`, `initial_creator_id`, `record_type` | 주소 하나의 정보입니다. 기기 주소인지 계정 주소인지는 `record_type` 이 가릅니다 |
| `address_type_tokens` | `guid`, `type`, `value`, `verification_status`, `observations` | 주소 하나를 이루는 칸들입니다. `guid` 로 `addresses` 와 잇습니다 |

`type` 은 칸의 종류를 숫자로 적은 것입니다. Chromium 소스는 이 번호를 서버와 맞출 때 말고는 바꾸지 말라고 적어 둡니다. 자주 보는 번호는 아래와 같습니다.

| `type` | 뜻 | `type` | 뜻 |
|---|---|---|---|
| 3 | 이름(first) | 33 | 시·군 |
| 5 | 성(last) | 34 | 도·주 |
| 7 | 전체 이름 | 35 | 우편번호 |
| 9 | 이메일 | 36 | 나라 |
| 14 | 전화번호 전체 | 60 | 회사 이름 |
| 30 | 주소 첫 줄 | 77 | 도로명 주소 전체 |

스키마 134 전에는 같은 모양의 표가 두 쌍 있습니다. 기기 주소는 `local_addresses`·`local_addresses_type_tokens`, 계정 주소는 `contact_info`·`contact_info_type_tokens` 입니다. 113 전에는 `autofill_profiles` 와 이름·이메일·전화·주소별 표에 나뉘어 있습니다.

### 결제 표

| 표 | 주요 열 | 뜻 |
|---|---|---|
| `credit_cards` | `guid`, `name_on_card`, `expiration_month`, `expiration_year`, `card_number_encrypted`, `date_modified`, `use_count`, `use_date`, `nickname` | 기기에 저장한 카드입니다. 카드 번호만 암호화해 BLOB 으로 둡니다 |
| `local_stored_cvc` | `guid`, `value_encrypted`, `last_updated_timestamp` | 카드 보안 코드(CVC)입니다. 암호화돼 있습니다 |
| `masked_credit_cards` | `id`, `network`, `name_on_card`, `last_four`, `exp_month`, `exp_year`, `bank_name`, `nickname` 등 | 계정 쪽 카드의 가린 사본입니다. 번호는 끝 네 자리만 있습니다 |
| `server_card_metadata` | `id`, `use_count`, `use_date` | 계정 쪽 카드의 사용 기록입니다 |
| `local_ibans`·`masked_ibans` | `value_encrypted` / `prefix`·`suffix` | 국제 계좌 번호입니다. 기기 쪽은 암호화하고, 계정 쪽은 앞뒤 일부만 둡니다 |

카드 번호와 CVC 는 운영체제 암호화 계층(OSCrypt)으로 암호화합니다. 복호에 무엇이 필요한지는 [쿠키·비밀번호 암호화](../../../01-foundations/app-mail-data/chromium-electron-webview2/dpapi-app-bound-encryption.md)에서 다룹니다. 카드에 적힌 이름과 유효기간은 평문입니다.

### 같은 파일의 다른 표

- `keywords` 표에는 검색 엔진 목록이 있습니다. `short_name`, `keyword`, `url`, `date_created`, `last_modified`, `last_visited`, `usage_count` 등이 있습니다. 사용자가 직접 넣은 검색 엔진이 여기 남습니다.
- `meta` 표에는 `version`(스키마 버전)과 `last_compatible_version` 이 있습니다.
- 표 목록은 스키마 버전마다 다릅니다. `sqlite_master` 로 확인합니다.

## 증거로서 의미

### 증명하는 것

- 이 프로필에서, 또는 동기화된 다른 기기에서 이름이 `name` 인 입력란에 `value` 를 제출한 적이 있습니다.
- `date_created` 무렵에 이 쌍을 처음 제출했습니다.
- `date_last_used` 무렵에 마지막으로 제출했습니다.
- `count` 만큼 제출했습니다. 단, 아래 "함정" 의 기간 삭제가 없었을 때입니다.
- 주소·카드 표의 항목은 이 프로필에 저장돼 있던 정보입니다. `use_count`·`use_date` 로 자동 채우기에 쓴 횟수와 마지막 시각을 알 수 있습니다.
- 카드 이름·유효기간·끝 네 자리처럼 평문인 열은 복호 없이 읽을 수 있습니다.

### 증명하지 못하는 것

- 어느 사이트에서 입력했는지. 표에 주소 열이 없습니다. [방문 기록](history.md)과 시각을 맞춰 추정할 뿐입니다.
- 누가 입력했는지. 프로필 폴더의 주인 계정만 알 수 있습니다.
- 처음과 마지막 사이에 언제 제출했는지. 중간 시각은 남지 않습니다.
- 이 PC 에서 입력했는지. 동기화로 다른 기기의 항목이 들어올 수 있습니다.
- 값이 없다는 것이 입력하지 않았다는 뜻인지. 시크릿 창, 저장 조건, 보존 기간 정리, 사용자 삭제로 빠질 수 있습니다.

보고서 문장 예(괄호 안은 자리 표시입니다):

> 사용자 (계정) 의 Chrome 프로필 `Default` 에 있는 `Web Data` 의 `autofill` 표에 입력란 이름 `email`, 값 (값) 인 행이 있습니다. 이 행의 처음 저장 시각은 (UTC 시각), 마지막 사용 시각은 (UTC 시각), 사용 횟수는 (횟수) 입니다. 이 기록만으로는 어느 사이트에서 입력했는지 알 수 없습니다. 같은 시각 무렵의 방문 기록은 (사이트) 입니다.

## 시각 해석

한 파일 안에서 표마다 시각 형식이 다릅니다.

| 표·열 | 저장 형식 | 무엇이 바뀔 때 바뀌나 |
|---|---|---|
| `autofill.date_created` | Unix 시각, 초, UTC | 이 쌍을 처음 저장할 때 |
| `autofill.date_last_used` | Unix 시각, 초, UTC | 같은 쌍을 다시 제출할 때 |
| `addresses.use_date`, `credit_cards.use_date` | Unix 시각, 초, UTC | 가장 최근에 쓴 때 |
| `addresses.date_modified`, `credit_cards.date_modified` | Unix 시각, 초, UTC | 내용을 마지막으로 고친 때 |
| `keywords.date_created`·`last_modified`·`last_visited` | WebKit 시각, 1601-01-01 부터 마이크로초, UTC | 열 이름대로의 사건 |

Chromium 은 자동완성·주소·카드 시각을 `ToTimeT()` 로 써서 1970년부터 센 초로 남기고, `keywords` 는 SQLite 도우미 `BindTime()` 으로 써서 1601년부터 센 마이크로초로 남깁니다. 둘 다 UTC 이며, 현지 시각으로 바꿀 때는 [시간대 설정](../../system-account/time-zone.md)을 봅니다.

값 0 은 시각이 없다는 뜻이고 열의 기본값도 0 입니다. 형식을 잘못 짐작하면 티가 나는데, Unix 초를 WebKit 마이크로초로 읽으면 1601년 1월 1일 새벽이 나옵니다.

바꾸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다.

## 함정과 한계

1. **기간을 정해 지우면 행이 남고 값이 바뀝니다.** 사용자가 "인터넷 사용 기록 삭제" 에서 기간을 골라 자동완성 데이터를 지우면 Chromium 은 행마다 따집니다.
   - `date_created` 와 `date_last_used` 가 모두 기간 안이면 행을 지웁니다.
   - 한쪽만 기간에 걸치면 행을 남기고 고칩니다.
   - 고친 행의 `date_created` 는 기간 끝 시각이 됩니다(원래 값이 기간 시작보다 앞이면 그대로).
   - 고친 행의 `date_last_used` 는 기간 시작 1초 앞이 됩니다(원래 값이 기간 끝 뒤면 그대로).
   - `count` 는 `1 + (count - 1) × (남은 기간 ÷ 원래 기간)` 으로 다시 계산합니다.
   - 그래서 고친 행의 시각과 횟수는 실제 사용 기록이 아닙니다. 여러 행의 시각이 같은 경계 값에 몰려 있으면 기간 삭제를 의심해 볼 수 있습니다(추론).
2. **오래된 항목은 저절로 지워집니다.** 마지막 사용이 14×31일(약 14개월)보다 오래된 자동완성 항목을 Chromium 이 지웁니다. 이 정리는 브라우저 주 버전이 올라간 뒤 한 번 돕니다. 마지막으로 정리한 주 버전은 프로필 설정(Preferences)에 적어 둡니다.
3. **동기화 항목이 섞입니다.** 동기화 (Sync) 를 켜면 다른 기기의 자동완성 항목이 이 표에 들어옵니다. 양쪽에 같은 항목이 있으면 `date_created` 는 더 이른 값, `date_last_used` 는 더 늦은 값을 씁니다. 그래서 두 시각 모두 다른 기기의 사용일 수 있습니다.
4. **지운 행은 되살리기 어렵습니다.** Chromium 은 SQLite 를 빌드할 때 `SQLITE_SECURE_DELETE` 를 넣습니다. 그래서 `secure_delete` 가 기본으로 켜집니다. 이 설정은 지운 내용을 0 으로 덮어씁니다. 파일 안의 빈 공간을 뒤지는 방법([파일 안에 남은 지운 레코드](../../../01-foundations/database-log-formats/sqlite/freelist-freeblock.md))은 이 파일에서 거의 소득이 없습니다. 남은 저널 파일, [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md), 비할당 영역의 옛 사본을 찾습니다. Edge·Whale 이 같은 빌드 설정을 쓰는지는 이 글에서 확인하지 않았습니다.
5. **시크릿 창 사용은 여기 없습니다.** Chromium 소스는 시크릿 창에서 제출한 폼을 저장하지 않습니다. 시크릿 창 조사는 [시크릿 모드로 무엇을 했나](../../../04-scenarios/activity/private-browsing.md)를 봅니다.
6. **값이 없어도 입력했을 수 있습니다.** 비밀번호 입력란, 자동완성을 막은 입력란, 카드 번호 모양의 값은 처음부터 저장하지 않습니다. 비밀번호는 [저장 비밀번호 (Login Data)](login-data.md)에 따로 남을 수 있습니다.
7. **입력란 이름은 사이트가 정합니다.** `name` 이 `email` 이라고 이메일 입력란이라는 보장은 없습니다. 이름만 보고 값의 종류를 단정하지 않습니다.
8. **쓰는 중인 파일입니다.** 브라우저가 켜져 있으면 최근 변경이 저널에만 있을 수 있습니다. 원본을 도구로 열면 파일이 바뀔 수 있습니다. 항상 사본을 만들어 엽니다.

**안티포렌식.** 설정 화면에서 자동완성 데이터를 지우면 행이 사라지고, 기간을 정하면 위 1번처럼 값이 바뀝니다. 주소·카드를 지우면 그 행이 빠집니다. 동기화를 켰다면 다른 기기나 계정 쪽에 같은 항목이 남아 있을 수 있습니다. `Web Data` 파일을 통째로 지우면 [$MFT](../../filesystem/mft.md)와 [$UsnJrnl](../../filesystem/usnjrnl.md)에 삭제 흔적이 남습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 레코드 형식 명세로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. `sqlite_master` 의 `autofill` 표 정의에 `WITHOUT ROWID` 가 없으면 보통의 rowid 표입니다. 아래는 그 경우의 표 잎 페이지 셀 하나입니다.

```
셀 시작 기준
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00      33 0C 07 17 2B 2B 04 04 01 65 6D 61 69 6C 6B 69
10      6D 40 65 78 61 6D 70 6C 65 2E 63 6F 6D 6B 69 6D
20      40 65 78 61 6D 70 6C 65 2E 63 6F 6D 65 F4 23 55
30      65 FA 39 C0 03
```

1. `33` 은 레코드 길이입니다. 51바이트입니다.
2. `0C` 는 rowid 12 입니다.
3. `07` 은 레코드 머리 길이입니다. 이 바이트를 포함해 7바이트입니다.
4. `17` 은 첫 열(`name`)의 형식 번호 23 입니다. 13 이상 홀수는 문자열이고, 길이는 (23 − 13) ÷ 2 = 5바이트입니다.
5. `2B 2B` 는 둘째·셋째 열(`value`, `value_lower`)입니다. 형식 번호 43 이므로 각각 15바이트 문자열입니다.
6. `04 04` 는 넷째·다섯째 열(`date_created`, `date_last_used`)입니다. 4바이트 부호 있는 정수입니다.
7. `01` 은 여섯째 열(`count`)입니다. 1바이트 정수입니다.
8. 오프셋 0x09 부터 5바이트는 `email` 입니다.
9. 오프셋 0x0E 와 0x1D 부터 15바이트씩은 `kim@example.com` 입니다. 이 예시는 대문자가 없어서 두 값이 같습니다.
10. 오프셋 0x2C 의 `65 F4 23 55` 는 빅 엔디언 1710498645 입니다. Unix 초이므로 2024-03-15 10:30:45 UTC 입니다.
11. 오프셋 0x30 의 `65 FA 39 C0` 은 1710897600 입니다. 2024-03-20 01:20:00 UTC 입니다.
12. 오프셋 0x34 의 `03` 은 `count` 3 입니다.

SQLite 정수는 빅 엔디언입니다. 윈도 레지스트리 값처럼 리틀 엔디언으로 읽으면 엉뚱한 수가 나옵니다. 정수 칸의 크기는 값에 따라 1·2·3·4·6·8바이트로 바뀝니다. 값이 0 이나 1 이면 형식 번호 8·9 로 적고 본문 바이트가 없을 수도 있습니다. 그래서 항상 머리부터 읽습니다.

### 공개 도구로 한 번

1. 이미지에서 `Web Data` 와 같은 이름의 `-journal`·`-wal` 파일을 함께 꺼냅니다. 해시를 적고 사본에서 작업합니다.
2. SQLite 뷰어(예: DB Browser for SQLite)나 `sqlite3` 명령줄 도구로 사본을 엽니다.
3. 스키마 버전과 표 목록을 먼저 봅니다.

   ```sql
   SELECT key, value FROM meta;
   SELECT name FROM sqlite_master WHERE type = 'table';
   ```

4. 자동완성 항목을 UTC 시각으로 뽑습니다.

   ```sql
   SELECT name, value, count,
          datetime(date_created, 'unixepoch')   AS created_utc,
          datetime(date_last_used, 'unixepoch') AS last_used_utc
   FROM autofill
   ORDER BY date_last_used DESC;
   ```

5. 스키마 134 이후라면 주소를 칸별로 뽑습니다.

   ```sql
   SELECT a.guid, a.use_count,
          datetime(a.use_date, 'unixepoch') AS use_utc,
          t.type, t.value
   FROM addresses a JOIN address_type_tokens t ON a.guid = t.guid
   ORDER BY a.guid, t.type;
   ```

6. `keywords` 는 WebKit 시각이라 식이 다릅니다.

   ```sql
   SELECT short_name, keyword, url,
          datetime(date_created / 1000000 - 11644473600, 'unixepoch') AS created_utc
   FROM keywords;
   ```

7. 브라우저 기록 전용 도구(예: Hindsight)로 같은 프로필을 한 번 더 돌립니다. 몇 행을 골라 SQL 결과와 시각을 맞춰 봅니다. 도구가 시각 형식을 어떻게 읽는지 확인하는 과정입니다. [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [방문·다운로드 기록 (History)](history.md) | `date_created`·`date_last_used` 무렵에 방문한 페이지. 어느 사이트의 폼인지 추정합니다 |
| [저장 비밀번호 (Login Data)](login-data.md) | 같은 아이디·이메일 값. 로그인 폼이었는지 확인합니다 |
| [쿠키 (Cookies)](cookies.md) | 그 시각 무렵에 쿠키를 받은 사이트 |
| [세션·탭 복원 (Sessions)](sessions.md) | 마지막 세션에 열려 있던 페이지 |
| [양식 기록 (formhistory.sqlite)](../firefox/formhistory-sqlite.md) | 같은 사용자가 Firefox 에서 넣은 값 |
| [저장 비밀번호 (IntelliForms)](../ie-edgehtml/intelliforms.md) | 옛 IE·Edge 에서 넣은 값 |
| [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 예전 `Web Data` 와 비교해 사라진 행과 바뀐 횟수 |

웹 사용 전체 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md), 올리기·보내기 조사는 [웹메일·웹하드로 올렸나](../../../04-scenarios/exfiltration/data-exfiltration/web-upload.md)에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 검체에서 크롬 계열 브라우저를 쓴 윈도 이미지를 하나 고릅니다. 가상 머신에서 직접 폼을 제출하며 파일을 비교해도 됩니다.

1. `meta` 표의 `version` 은 얼마입니까? 주소는 어느 표에 있습니까?
2. `autofill` 표에서 `count` 가 가장 큰 행 다섯 개를 고릅니다. 각 행의 두 시각을 UTC 와 현지 시각으로 바꿔 봅니다.
3. 그중 한 행의 `date_last_used` 앞뒤 1분 안의 방문 기록을 찾습니다. 어느 사이트의 폼으로 볼 수 있습니까? 그렇게 볼 근거는 무엇입니까?
4. 가상 머신에서 같은 값을 세 번 제출합니다. `count` 와 두 시각은 어떻게 바뀝니까?
5. 기간을 "지난 1시간" 으로 골라 자동완성 데이터를 지웁니다. 그 전부터 있던 행의 시각과 `count` 는 어떻게 바뀝니까?
6. 시크릿 창에서 폼을 제출한 뒤 `Web Data` 를 다시 봅니다. 새 행이 생깁니까?

## 참고 문헌

- Chromium 소스, `autocomplete_table.cc`(자동완성 표 정의·갱신·기간 삭제) · `autocomplete_sync_bridge.cc`(동기화 병합) — https://raw.githubusercontent.com/chromium/chromium/main/components/autofill/core/browser/webdata/autocomplete/autocomplete_table.cc , https://raw.githubusercontent.com/chromium/chromium/main/components/autofill/core/browser/webdata/autocomplete/autocomplete_sync_bridge.cc
- Chromium 소스, `autocomplete_history_manager.cc`(저장 조건·보존 정리) · `browser_autofill_manager.cc`(시크릿 창) · `autofill_constants.h`(보존 기간) — https://raw.githubusercontent.com/chromium/chromium/main/components/autofill/core/browser/single_field_fillers/autocomplete/autocomplete_history_manager.cc , https://raw.githubusercontent.com/chromium/chromium/main/components/autofill/core/browser/foundations/browser_autofill_manager.cc , https://raw.githubusercontent.com/chromium/chromium/main/components/autofill/core/common/autofill_constants.h
- Chromium 소스, `address_autofill_table.cc` · `payments_autofill_table.cc` · `field_types.h` · `usage_history_information.h`(주소·결제 표와 칸 번호) — https://raw.githubusercontent.com/chromium/chromium/main/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc , https://raw.githubusercontent.com/chromium/chromium/main/components/autofill/core/browser/webdata/payments/payments_autofill_table.cc , https://raw.githubusercontent.com/chromium/chromium/main/components/autofill/core/browser/field_types.h , https://raw.githubusercontent.com/chromium/chromium/main/components/autofill/core/browser/data_model/usage_history_information.h
- Chromium 소스, `keyword_table.cc` · `sql/statement.cc` · `third_party/sqlite/sqlite_common_configuration_flags.gni`(keywords 시각 형식·SQLite 빌드 설정) — https://raw.githubusercontent.com/chromium/chromium/main/components/search_engines/keyword_table.cc , https://raw.githubusercontent.com/chromium/chromium/main/sql/statement.cc , https://raw.githubusercontent.com/chromium/chromium/main/third_party/sqlite/sqlite_common_configuration_flags.gni
- Chromium 문서, "User Data Directory" — https://chromium.googlesource.com/chromium/src/+/HEAD/docs/user_data_dir.md
- Ryan Benson, Hindsight 소스 `pyhindsight/browsers/chrome.py` — https://raw.githubusercontent.com/obsidianforensics/hindsight/master/pyhindsight/browsers/chrome.py
