---
title: "쿠키와 저장된 암호"
parent: "크롬·엣지·웨일"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1250
---

# 쿠키와 저장된 암호 (Cookies·Login Data)

Chromium 계열 브라우저는 프로필 폴더의 `Cookies` 와 `Login Data` SQLite 파일에 사이트별 쿠키와 저장한 로그인 정보를 남기고, 맥에서는 민감한 값을 키체인에 둔 비밀번호에서 만든 키로 암호화해서 어느 사이트의 기록인지와 값 자체를 나눠 해석해야 합니다.

이 페이지는 두 파일이 어떤 형식으로 저장되고 무엇을 뜻하는지까지만 다루고, 암호화된 값을 푸는 절차는 다루지 않습니다.

## 무엇을 기록하나 · 왜 생기나

쿠키 (Cookie)는 사이트가 브라우저에 맡겨 둔 작은 값이고, 브라우저는 이를 프로필의 `Cookies` DB에 사이트 호스트·이름·값·시각과 함께 한 행씩 둡니다 [1]. `Login Data` 는 사용자가 브라우저에 저장하기로 한 사이트 로그인 정보를 담는 DB이고, 같은 자리의 `Web Data` 도 함께 수집 대상입니다 [3]. 사이트에 로그인해 있거나 암호를 저장해 둔 흔적이 이 두 파일에 모여서, 어떤 사이트를 썼는지와 어느 계정으로 들어갔는지를 따질 때 방문 기록과 함께 봅니다.

## 위치와 버전별 차이

```
<프로필>/Cookies
<프로필>/Network/Cookies
<프로필>/Login Data
<프로필>/Network/Login Data     (크롬 정의에만 있음)
<프로필>/Web Data
```

새 버전 브라우저는 쿠키 DB를 프로필 안의 `Network` 폴더 아래에 두므로, 두 위치를 모두 수집합니다 [3]. 쿠키 DB가 `Network` 로 옮겨진 크롬 버전은 공개 문서에 나와 있지 않아서, 두 위치를 다 확인합니다. 크롬은 `Network/Login Data` 도 수집 대상이고 `Web Data` 도 같습니다 [3]. 프로필 폴더를 찾는 법은 [맥에서의 위치와 프로필 (Profiles)](profiles.md)에서 다룹니다.

아래 암호화 형식 설명은 크롬 v120 소스 기준입니다 [2].

## 구조

### cookies 표

옛 버전 `cookies` 표의 열은 아래와 같고, 시각 열은 모두 1601-01-01 UTC 기준 마이크로초입니다 [1].

| 열 | 비고 |
|---|---|
| `creation_utc` | 시각 열 |
| `host_key` | 쿠키가 속한 호스트 |
| `name`, `value`, `path` | 쿠키 이름·값·경로 |
| `expires_utc` | 시각 열, 만료 시각 |
| `secure`, `httponly` | 쿠키 속성 |
| `last_access_utc` | 시각 열, 마지막 접근 시각 |
| `has_expires`, `persistent`, `priority` | 쿠키 속성 |

현재 소스(2026-09 시점)의 `cookies` 표는 열이 더 많고 일부 이름도 바뀌었습니다 [4].

```
creation_utc, host_key, top_frame_site_key, name, value, encrypted_value,
path, expires_utc, is_secure, is_httponly, last_access_utc, has_expires,
is_persistent, priority, samesite, source_scheme, source_port,
last_update_utc, source_type, has_cross_site_ancestor
```

옛 버전의 `secure`·`httponly`·`persistent` 는 지금 `is_secure`·`is_httponly`·`is_persistent` 이고, 암호화된 값은 `encrypted_value` 열에 따로 들어갑니다 [4]. 암호화를 쓰면 `value` 열은 빈 문자열이 되고 `encrypted_value` 에만 값이 들어가서 [4], `value` 가 비어 있다고 쿠키 값이 없던 것은 아닙니다. 분석 대상 DB에서는 `.schema cookies` 로 실제 열을 먼저 확인하고, 위 목록에 없는 열은 그 버전의 소스로 뜻을 확인한 뒤에 씁니다.

### logins 표

`Login Data` 의 `logins` 표는 열 이름과 시각 기준을 분석 대상 DB의 `.schema logins` 로 확인한 것만 씁니다.

### 맥에서 값을 암호화하는 형식

맥의 Chromium 계열 브라우저에서 암호화된 값은 앞에 접두어 `v10` 이 붙고, 접두어가 없는 값은 평문으로 다룹니다 [2]. 암호화 키는 사용자 키체인에 저장된 비밀번호에서 PBKDF2로 만든 128비트 키이고, 암호 방식은 AES-128-CBC입니다 [2]. 키체인에서 비밀번호를 얻지 못하면 암호화를 쓸 수 없는 상태(키 없음)로 처리합니다 [2].

키체인에서 이 비밀번호를 담은 항목의 이름과 계정 이름은 분석 대상 키체인에서 확인합니다. 키체인 파일의 구조와 항목 읽는 법은 [키체인 (Keychain)](../../../01-foundations/protection/keychain/index.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 이 프로필의 쿠키 DB에 이 호스트의 이 이름으로 된 쿠키가 이 시각에 만들어졌고 이 시각에 마지막으로 쓰였다는 기록이 있다는 점입니다 [1]. `Login Data` 에 행이 있으면 이 프로필에 그 사이트의 로그인 정보를 저장한 기록이 있다는 뜻입니다.

**증명하지 못하는 것.** 쿠키가 있다는 사실만으로 사용자가 그 사이트 페이지를 직접 열었다고 단정하지 않고, [방문·다운로드 기록 (History)](history-downloads.md)의 방문과 맞춰 봅니다. 암호화된 값은 사용자 키체인의 비밀번호 없이는 읽을 수 없고 [2], 값을 읽지 못하면 쿠키가 어느 계정의 세션인지, 저장된 암호가 무엇인지도 알 수 없습니다.

쿠키 DB에서 암호화된 값은 `encrypted_value` 열에만 들어가고 `host_key`·`name`·시각 열은 평문 그대로 들어가서 [4], 키 없이도 어느 사이트의 쿠키가 언제 생겼는지는 읽을 수 있습니다. `logins` 표는 실제 DB에서 열마다 `v10` 접두어가 있는지 직접 보고 평문인 열만 근거로 씁니다.

보고서에는 "이 프로필의 쿠키 DB에 이 호스트의 쿠키가 이 시각(UTC)에 만들어진 기록이 있다", "이 프로필의 `Login Data` 에 이 사이트의 로그인 정보가 저장된 기록이 있다" 처럼 쓰고, 값의 내용은 읽을 수 있었던 경우에만 적습니다.

## 시각 해석

`creation_utc`, `expires_utc`, `last_access_utc` 는 방문 기록과 같은 1601-01-01 UTC 기준 마이크로초라서 [1], 바꾸는 법은 [방문·다운로드 기록 (History)](history-downloads.md)의 시각 해석을 그대로 씁니다. `creation_utc` 는 쿠키가 처음 생긴 때, `last_access_utc` 는 그 쿠키를 마지막으로 쓴 때로 읽고, `expires_utc` 는 앞으로의 시각일 수 있어서 사용자 행위 시각으로 타임라인에 넣지 않습니다. 모두 UTC라서 현지 시각은 [시간대와 시계 설정 (Time Zone·NTP)](../../system-account/time-zone.md)을 보고 바꿉니다.

## 함정과 한계

- **쿠키 파일 두 곳.** `Cookies` 와 `Network/Cookies` 가 둘 다 있을 수 있습니다 [3]. 한쪽만 보면 옛 기록이나 새 기록을 놓칩니다.
- **평문과 암호문이 섞임.** 접두어 `v10` 이 없는 값은 평문으로 다룹니다 [2]. 같은 DB 안에서 평문 값과 암호화된 값이 함께 보여도 이상한 일로 단정하지 말고, 행마다 접두어를 확인합니다.
- **키체인과 한 묶음.** 값을 읽을 수 있는지는 사용자 키체인에 달려 있어서 [2], 증거를 확보할 때 브라우저 프로필과 사용자 키체인을 함께 보존합니다. 확보 절차는 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)에서 다룹니다.
- **다루지 않은 열.** `logins` 표의 열과 `cookies` 표 새 열의 값 뜻은 이 페이지에서 다루지 않습니다. 도구가 열 이름을 붙여 보여 주면 분석 대상 DB의 `.schema` 와 맞춰 봅니다.
- **지운 쿠키와 로그인 정보.** 지운 행은 SQLite 파일의 빈 공간을 살펴야 하고, 그 방법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

명세로 만든 예시로, 암호화된 값을 담은 열(쿠키 DB에서는 `encrypted_value`)을 헥스로 열면 첫 세 바이트가 아래처럼 보입니다.

```
76 31 30 xx xx xx xx xx ...
v  1  0  (암호문)
```

`76 31 30` 은 글자 `v10` 이고, 이 접두어가 있으면 암호화된 값, 없으면 평문으로 다룹니다 [2]. 뒤의 바이트는 예시라서 `xx` 로 적었습니다. SQLite 레코드 안에서 열 값을 찾아가는 방법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

### SQL로 한 번

원본을 건드리지 않도록 사본을 `sqlite3` 같은 공개 도구로 엽니다. 먼저 열을 확인하고, 확인한 열로 호스트별 쿠키와 시각을 뽑습니다.

```sql
.schema cookies

SELECT host_key, name,
       datetime(creation_utc / 1000000 - 11644473600, 'unixepoch') AS created_utc,
       datetime(last_access_utc / 1000000 - 11644473600, 'unixepoch') AS last_access_utc,
       length(value) AS plain_len,
       substr(encrypted_value, 1, 3) = CAST('v10' AS BLOB) AS enc_has_v10
FROM cookies
ORDER BY creation_utc;
```

`plain_len` 은 평문 `value` 열의 길이이고, `enc_has_v10` 은 `encrypted_value` 열이 `v10` 접두어로 시작하는지 보는 용도입니다. 오래된 DB에 `encrypted_value` 열이 없으면 그 줄을 뺍니다. `Login Data` 도 `.schema logins` 로 열을 확인한 뒤 같은 방식으로 읽습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [방문·다운로드 기록 (History)](history-downloads.md) | 쿠키의 호스트와 생성·접근 시각을 방문 기록과 맞춰 봅니다 |
| [키체인 (Keychain)](../../../01-foundations/protection/keychain/index.md) | 값을 암호화한 키의 바탕이 되는 비밀번호가 사용자 키체인에 있습니다 |
| [저장된 암호 (Passwords·iCloud Keychain)](../../credentials/saved-passwords.md) | 브라우저 밖에 저장된 같은 사이트의 로그인 정보를 봅니다 |
| [정보 탈취 악성 코드 (Infostealer)](../../../04-scenarios/incident/infostealer.md) | 브라우저 쿠키·로그인 파일이 사고 조사 대상이 될 때 볼 순서를 정리합니다 |
| [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md) | 쿠키와 방문 기록을 묶어 웹 사용을 다시 짭니다 |

## 실습

공개 데이터셋(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 프로필마다 `Cookies` 와 `Network/Cookies` 중 어느 파일이 있는지 확인해 보세요.
2. `.schema cookies` 로 열 목록을 뽑아 이 페이지의 표와 무엇이 다른지 적어 보세요.
3. 쿠키 값 가운데 `v10` 접두어가 있는 행과 없는 행의 수를 세어 보세요.
4. 쿠키 수가 가장 많은 호스트 다섯 개를 골라, 같은 호스트의 방문이 `History` 에 있는지 찾아보세요.

## 참고 문헌

1. Forensics Wiki, "Google Chrome" — https://forensics.wiki/google_chrome/
2. Chromium 소스(v120.0.6099.109), components/os_crypt/sync/os_crypt_mac.mm — https://chromium.googlesource.com/chromium/src/+/refs/tags/120.0.6099.109/components/os_crypt/sync/os_crypt_mac.mm
3. ForensicArtifacts, webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
4. Chromium 소스, net/extras/sqlite/sqlite_persistent_cookie_store.cc — https://chromium.googlesource.com/chromium/src/+/HEAD/net/extras/sqlite/sqlite_persistent_cookie_store.cc
