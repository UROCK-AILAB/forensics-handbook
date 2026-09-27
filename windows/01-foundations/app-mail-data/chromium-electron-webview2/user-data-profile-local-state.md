---
title: "프로필 폴더와 계열 브라우저 구분"
parent: "크롬 계열 앱 공통 구조"
grand_parent: "기반 · 앱·메일 데이터 구조"
nav_order: 430
---

# 프로필 폴더와 계열 브라우저 구분 (User Data·Profile·Local State)

크롬 계열 브라우저는 사용자 데이터 폴더 (User Data Directory) 하나에 기록을 모으고, 그 아래 프로필 (Profile) 폴더마다 방문 기록·쿠키 같은 파일이 따로 쌓입니다.
`Local State` 파일에는 프로필 폴더 이름과 사용자가 붙인 이름을 잇는 정보가 들어 있습니다.
어느 브라우저의 폴더인지는 폴더 모양이 아니라 `Last Version`·`Last Browser` 파일과 `Local State` 의 키로 구분합니다.

## 이 구조를 쓰는 아티팩트

- Chrome·Edge 같은 크롬 계열 브라우저의 모든 기록이 이 구조 위에 있습니다. 파일별 해석은 [크롬 계열 브라우저](../../../02-artifacts/browsers/chrome-edge-whale/index.md) 에서 다룹니다.
- Electron 앱과 WebView2 앱도 비슷한 구조를 씁니다. 다만 프로필 폴더가 없거나 폴더 층이 다를 수 있습니다. 이 차이는 [Electron·WebView2 앱 데이터 위치](teams-discord-slack.md) 에서 다룹니다.

아래 폴더·파일 이름, JSON 키 이름, 파일 앞 몇 바이트는 Windows 11(빌드 26200)의 Chrome 153.0.8010.48 과 Edge 151.0.4129.101 기준입니다.
버전마다 다를 수 있으니 실제 기기에서 확인합니다.

## 구조

> 그림 자리: `User Data` 폴더 아래 `Local State`·`Last Version`·`Last Browser` 파일과 `Default`·`Profile 1` 폴더가 놓인 층. `Local State` 의 `profile.info_cache` 키가 각 프로필 폴더를 가리키는 화살표

### User Data 폴더의 기본 위치

| 브라우저 | Windows 기본 위치 | 근거 |
|---|---|---|
| Chrome | `%LOCALAPPDATA%\Google\Chrome\User Data` | [1] |
| Chrome Beta | `%LOCALAPPDATA%\Google\Chrome Beta\User Data` | [1] |
| Chrome Dev | `%LOCALAPPDATA%\Google\Chrome Dev\User Data` | [1] |
| Chrome Canary | `%LOCALAPPDATA%\Google\Chrome SxS\User Data` | [1] |
| Chromium | `%LOCALAPPDATA%\Chromium\User Data` | [1] |
| Edge | `%LOCALAPPDATA%\Microsoft\Edge\User Data` |  |

- Canary 의 폴더 이름에는 "Canary" 가 들어가지 않습니다. `Chrome SxS` 입니다.
- Brave·Whale·Opera 같은 다른 계열 브라우저의 기본 위치는 판마다 다를 수 있어 실제 기기에서 확인합니다.
- 실행 인수 `--user-data-dir` 로 이 위치를 바꿀 수 있습니다[1].
- User Data 폴더에는 두 가지가 함께 들어 있습니다. 하나는 방문 기록·즐겨찾기·쿠키 같은 프로필 데이터입니다. 다른 하나는 브라우저 설치 하나에 딸린 상태 값입니다[1].
- Windows 에서는 캐시 폴더도 프로필 폴더 안에 있습니다[1]. Chrome 153 에서는 `Default\Cache\Cache_Data` 입니다.

### User Data 바로 아래

| 이름 | 종류 | 내용 |
|---|---|---|
| `Local State` | JSON 텍스트 파일 | 프로필 목록, 마지막으로 쓴 프로필, 암호화 키 |
| `Last Version` | 파일 | 마지막으로 실행한 브라우저의 버전 문자열 |
| `Last Browser` | 파일 | 브라우저 실행 파일 경로. UTF-16LE 로 적혀 있습니다 |
| `Default` | 폴더 | 첫 프로필. 프로필 폴더 이름은 보통 `Default` 입니다[1] |
| `Profile 1` 등 | 폴더 | 두 번째 이후 프로필 |
| `Guest Profile`·`System Profile` | 폴더 | Chrome 의 User Data 에 있습니다. 쓰임은 공개 자료에 나와 있지 않습니다 |

프로필 폴더 이름과 사용자가 붙인 표시 이름은 다르고, 표시 이름은 `Local State` 에 있으므로 보고서에는 두 이름을 함께 적습니다.

### Local State 의 프로필 정보

`Local State` 는 모든 프로필이 함께 쓰는 JSON 파일 하나이고, 아래 키 이름은 Chrome 153·Edge 151 의 파일에 적힌 이름입니다.
점(`.`)은 JSON 안에서 한 층 들어간다는 뜻입니다.

| 키 | 내용 |
|---|---|
| `profile.info_cache` | 프로필 폴더 이름(`Default`, `Profile 1`)을 키로 삼아 프로필마다 정보를 담습니다 |
| `profile.last_used` | 마지막으로 쓴 프로필의 폴더 이름입니다. Edge 151 의 `Local State` 에는 이 키가 없습니다 |
| `profile.last_active_profiles` | 목록입니다. 채우는 기준은 공개 자료에 나와 있지 않습니다 |
| `profile.profiles_order` | 목록입니다. 채우는 기준은 공개 자료에 나와 있지 않습니다 |
| `os_crypt.encrypted_key`, `os_crypt.app_bound_encrypted_key`, `os_crypt.audit_enabled` | 쿠키·비밀번호 암호화에 쓰는 키입니다. [쿠키·비밀번호 암호화](dpapi-app-bound-encryption.md) 에서 다룹니다 |

Chrome 의 `info_cache` 에서 프로필 하나에 딸린 필드는 아래와 같습니다.

`name`, `shortcut_name`, `user_name`, `gaia_id`, `gaia_name`, `gaia_given_name`, `hosted_domain`, `is_managed`, `is_ephemeral`, `avatar_icon`, `active_time`

- 필드마다 뜻을 설명한 공식 문서는 없습니다.
- `user_name` 과 `gaia_` 로 시작하는 필드는 이름으로 보면 브라우저에 로그인한 계정 정보로 보입니다. 이름에서 짐작한 뜻이므로 다른 기록과 대조합니다.
- `active_time` 은 소수점이 있는 숫자입니다. 1970-01-01 UTC 부터 센 초로 바꾸면 프로필을 쓴 날과 맞는 날짜(예: 2026-09-23 UTC)가 나오므로 Unix 초로 보입니다.

### 프로필 폴더 안 주요 파일

아래는 Chrome 153 의 `Default` 폴더에 있는 이름입니다.

| 자리 | 이름 |
|---|---|
| 프로필 바로 아래 파일 | `History`, `Login Data`, `Login Data For Account`, `Web Data`, `Preferences`, `Secure Preferences`, `Bookmarks`, `Favicons`, `Shortcuts`, `Top Sites` |
| 쿠키 | `Network\Cookies` |
| 캐시 | `Cache\Cache_Data`, `Code Cache\js`, `Code Cache\wasm`, `GPUCache` |
| 사이트 저장소·세션 | `Local Storage`, `Session Storage`, `IndexedDB`, `Service Worker`, `Sessions` |
| 확장 프로그램 | `Extensions` |
| 새 이름 | `Sessions_Encrypted`, `EncryptedBookmarks2` |

- `History` 파일의 첫 16바이트는 `SQLite format 3\0` 입니다. 읽는 법은 [SQLite 데이터베이스](../../database-log-formats/sqlite/index.md) 에서 다룹니다.
- 쿠키 DB 는 프로필 바로 아래가 아니라 `Network` 폴더 안에 있습니다. 옛 버전은 프로필 바로 아래 `Cookies` 에 두었습니다. 자리를 옮긴 버전은 공개 자료에 나와 있지 않으므로 두 자리를 모두 봅니다.
- 캐시도 옛 버전은 `Default\Cache` 바로 아래에 두었습니다. `Cache\Cache_Data` 로 옮긴 버전도 공개 자료에 나와 있지 않습니다. 캐시 파일의 형식은 [캐시 형식](blockfile-simple-cache.md) 에서 다룹니다.
- `Sessions_Encrypted` 와 `EncryptedBookmarks2` 는 뜻과 처음 생긴 버전이 공개 자료에 나와 있지 않습니다.

### 계열 브라우저를 구분하는 단서

Chrome 과 Edge 는 폴더 구성이 거의 같아서 폴더 이름만 보고 구분하지 않고, 아래 파일과 키를 함께 봅니다.

| 단서 | Chrome 153 | Edge 151 |
|---|---|---|
| `Last Version` 값 | `153.0.8010.48` | `151.0.4129.101` |
| `Last Browser` 값 | `C:\Program Files\Google\Chrome\Application\` 아래 실행 파일 경로 | Edge 실행 파일 경로 |
| `Local State` 최상위 키 | Edge 전용 키 없음 | `edge`, `edge_ci`, `dual_engine`, `smartscreen` 처럼 `edge` 로 시작하거나 Edge 에만 있는 키 |
| `info_cache` 필드 | 위 목록 | `edge_account_cid`, `edge_account_type`, `edge_account_tenant_id` 같은 `edge_account_*` 필드가 더 있음 |
| `os_crypt` 키 | `encrypted_key`, `app_bound_encrypted_key`, `audit_enabled` | 여기에 `aster_app_bound_encrypted_key` 가 하나 더 있음. 뜻은 공개 자료에 나와 있지 않습니다 |
| `profile.last_used` | 있음 | 없음 |

- Brave·Whale·Opera 에서는 이 단서가 다를 수 있어 실제 기기에서 확인합니다.

## 읽는 법

1. **User Data 폴더를 찾습니다.** 사용자 프로필마다 위 기본 위치를 봅니다.
2. **기본 위치 밖도 찾습니다.** 디스크 전체에서 `Local State` 라는 이름의 파일을 찾습니다. 이 파일이 있는 폴더가 크롬 계열 데이터 폴더 후보입니다. `--user-data-dir` 로 옮긴 폴더와 Electron·WebView2 앱 폴더가 함께 나옵니다. 실행 인수가 남았을 수 있는 [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md) 도 봅니다.
3. **계열을 구분합니다.** `Last Version`, `Last Browser`, `Local State` 최상위 키를 위 표와 맞춰 봅니다.
4. **프로필 폴더와 표시 이름을 짝짓습니다.** 사본의 `Local State` 를 JSON 으로 엽니다. `profile.info_cache` 아래 키가 폴더 이름입니다. 그 안의 필드에서 표시 이름과 계정 정보를 읽습니다.
5. **실제 폴더 목록과 비교합니다.** `info_cache` 에 없는 폴더가 있거나 그 반대면 이유를 따로 확인합니다.
6. **프로필마다 따로 분석합니다.** 방문 기록·쿠키·캐시는 프로필 폴더마다 따로 있습니다. 결과에는 프로필 폴더 이름을 붙입니다.

### 헥스로 한 번 따라가기

`Last Browser` 는 UTF-16LE 로 적힌 경로입니다.
아래는 `C:\P` 네 글자를 UTF-16LE 규칙대로 바꾼 예시이며, 실제 파일에서 옮긴 바이트가 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07
00000000  43 00 3A 00 5C 00 50 00   C.:.\.P.
```

- 영문자와 기호 하나가 2바이트입니다. 둘째 바이트는 `00` 입니다.
- 그래서 문자열을 1바이트씩 읽는 도구에서는 글자 사이에 점이 끼어 보입니다.
- 파일 첫머리에 다른 바이트가 붙을 수도 있으니 첫 몇 바이트를 직접 봅니다.
- 인코딩 규칙은 [문자 인코딩](../../value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.

`Local State` 의 뼈대는 아래와 같습니다.
Chrome 153·Edge 151 의 키 이름으로 만든 예시이고, `<…>` 는 값 자리를 표시한 것이지 실제 값이 아닙니다.

```json
{
  "profile": {
    "info_cache": {
      "Default":   { "name": "<표시 이름>", "active_time": <소수점 있는 숫자> },
      "Profile 1": { "name": "<표시 이름>", "active_time": <소수점 있는 숫자> }
    },
    "last_used": "<프로필 폴더 이름>",
    "profiles_order": [ "<…>" ]
  },
  "os_crypt": {
    "encrypted_key": "<base64 문자열>",
    "app_bound_encrypted_key": "<base64 문자열>"
  }
}
```

## 포렌식에서 중요한 점

### 기본 위치가 비어 있을 때

`--user-data-dir` 로 위치를 바꿀 수 있으므로 기본 위치에 폴더가 없다고 브라우저를 쓰지 않았다고 단정하지 않습니다. 사용자 프로필마다, 그리고 기본 위치 밖까지 `Local State` 를 찾은 뒤에 판단합니다.

### 버전과 파일 구조

`Last Version` 은 마지막으로 실행한 버전입니다. 폴더 안 파일 가운데 일부는 업데이트 전에 쓴 것일 수 있어서, 옛 자리의 쿠키·캐시 파일이 남아 있으면 옛 버전 구조로 읽습니다. 업데이트한 뒤에도 옛 자리의 파일이 남을 수 있으므로 옛 자리와 새 자리를 둘 다 봅니다.

### 시각

- `active_time` 은 Unix 초로 보입니다. 공식 문서에 설명이 없으므로 다른 시각 기록과 대조합니다.
- 이 값이 어떤 동작 때 바뀌는지도 공개 자료에 없으므로 보고서에는 "이 프로필에 이 시각 값이 적혀 있다" 까지만 씁니다.
- 변환은 [시각 값 형식](../../value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

### 지운 프로필과 옛 상태

- `Local State` 는 모든 프로필이 함께 쓰는 파일 하나입니다. 옛 시점의 프로필 목록을 보려면 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 속 `Local State` 와 비교합니다.
- 지운 프로필 폴더는 파일 시스템 수준에서 찾습니다. [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 를 봅니다.

## 함정

- **폴더 이름을 프로필 이름으로 적습니다.** `Profile 1` 은 폴더 이름입니다. 사용자가 붙인 이름은 `Local State` 에 따로 있습니다.
- **Canary 를 놓칩니다.** Canary 폴더 이름은 `Chrome SxS` 입니다.
- **`last_used` 만으로 마지막 프로필을 찾습니다.** Edge 151 의 `Local State` 에는 이 키가 없습니다.
- **`Guest Profile`·`System Profile` 을 사용자 프로필과 같이 셉니다.** 두 폴더의 쓰임은 공개 자료에 나와 있지 않습니다. 안의 파일을 보고 따로 판단합니다.
- **폴더 모양으로 브라우저를 구분합니다.** Chrome 과 Edge 는 폴더 구성이 거의 같습니다. Electron·WebView2 앱 폴더에도 `Local State` 가 있습니다. 앱 안에 든 폴더를 브라우저 프로필로 착각하지 않습니다. [Electron·WebView2 앱 데이터 위치](teams-discord-slack.md) 를 봅니다.
- **쿠키 파일을 한 자리에서만 찾습니다.** 요즘 버전은 `Network\Cookies`, 옛 버전은 프로필 바로 아래 `Cookies` 입니다.
- **원본 폴더를 브라우저로 엽니다.** `Last Version` 은 마지막으로 실행한 버전을 적는 파일입니다. 다른 버전의 브라우저로 열면 이런 값이 바뀔 수 있습니다. 사본을 만들고 파일 단위로 읽습니다.

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| 텍스트 편집기, JSON 조회 도구(jq 등) | `Local State` 의 키와 값을 읽습니다 |
| 헥스 편집기 | `Last Browser` 의 UTF-16LE 문자열과 파일 첫머리를 봅니다 |
| SQLite 조회 도구(DB Browser for SQLite 등) | `History` 같은 프로필 파일을 엽니다 |

도구가 프로필을 하나만 보여 주면 폴더 목록과 비교합니다.
결과가 도구마다 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 참고 문헌

- Chromium docs, *User Data Directory* — https://chromium.googlesource.com/chromium/src/+/HEAD/docs/user_data_dir.md
