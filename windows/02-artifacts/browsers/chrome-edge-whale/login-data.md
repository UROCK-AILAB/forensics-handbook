---
title: "저장 비밀번호 (Login Data)"
parent: "크롬 계열 브라우저"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1630
---

# 저장 비밀번호 (Login Data)

> 상위 허브: [크롬 계열 브라우저 (Chrome·Edge·Whale 등)](index.md)

## 한 줄 요약

크롬 계열 브라우저는 저장한 비밀번호를 프로필 폴더의 `Login Data` 파일에 둡니다. 이 파일은 SQLite 데이터베이스이고, 암호화하는 칸은 비밀번호 값 하나뿐이며 사이트 주소·아이디·저장 시각·사용 횟수는 평문입니다. 그래서 비밀번호를 풀지 못해도 "이 프로필에 어느 사이트의 어느 아이디가 언제 저장됐나" 는 읽을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

브라우저의 비밀번호 관리자 (Password Manager) 가 이 파일을 씁니다. 한 행이 생기는 경우는 다음과 같습니다.

- 로그인 폼을 제출한 뒤 저장 제안에서 "저장" 을 고르면 `logins` 표에 행이 하나 생깁니다.
- 저장 제안에서 "저장 안 함" 을 고르면 그 사이트가 차단 목록에 들어가는데, 이것도 `logins` 표의 한 행이며 `blacklisted_by_user` 가 1 입니다.
- 설정 화면에서 직접 추가하거나, 파일에서 가져오거나, 다른 사용자에게서 공유받아도 행이 생깁니다.
- 동기화 (Sync) 를 켠 계정이면 다른 기기에서 저장한 항목도 이 파일에 들어옵니다.

`logins` 말고도 표가 몇 개 더 있습니다.

- `stats` 표에는 저장 제안 창을 닫은 횟수가 사이트·아이디별로 쌓입니다.
- `insecure_credentials` 표에는 비밀번호 점검 결과(유출·약함 등)가 들어갑니다. `logins` 의 `id` 를 가리킵니다.
- `password_notes` 표에는 비밀번호마다 붙인 메모가 들어갑니다.

암호화 방식과 키를 푸는 절차는 [쿠키·비밀번호 암호화 (DPAPI·App-Bound Encryption)](../../../01-foundations/app-mail-data/chromium-electron-webview2/dpapi-app-bound-encryption.md)에서 다루고, 이 페이지는 `Login Data` 에만 해당하는 내용을 다룹니다.

## 위치와 버전별 차이

### 파일

| 파일 | 뜻 |
|---|---|
| `<User Data>\<프로필>\Login Data` | 프로필 저장소입니다 |
| `<User Data>\<프로필>\Login Data For Account` | 계정 저장소 (Account Store) 입니다. Chromium 소스는 이 파일을 프로필 저장소와 따로 엽니다 |
| `Login Data-journal`, `Login Data For Account-journal` | 각 파일의 롤백 저널입니다 |
| `<User Data>\Local State` | 비밀번호 값을 푸는 키가 들어 있는 JSON 파일입니다 |

- `<User Data>` 는 Chrome 이 `%LOCALAPPDATA%\Google\Chrome\User Data`, Edge 가 `%LOCALAPPDATA%\Microsoft\Edge\User Data` 입니다. 다른 계열 브라우저의 경로와 `<프로필>` 폴더 이름(`Default`, `Profile 1` …)은 [프로필 폴더와 계열 브라우저 구분](../../../01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md)에 있습니다.
- 파일 네 개의 이름은 Chromium 소스(`password_manager_constants.cc`)에 그대로 적혀 있습니다.
- 아래 PC 에서는 두 브라우저 모두 `Login Data For Account` 파일이 있었지만 행은 0개였습니다. `-wal` 파일은 없었습니다 (확인 범위: Windows 11 25H2, Chrome 153·Edge 151, PC 한 대). 이 글에서 "관찰" 이라고 쓴 것은 모두 이 PC 에서 본 것입니다.

### Windows 버전보다 브라우저 버전이 중요합니다

이 파일의 모양은 Windows 버전이 아니라 브라우저 버전에 따라 바뀌며, 가장 큰 차이는 `password_value` 칸의 암호화 방식입니다. 칸의 앞 몇 바이트를 보면 구분됩니다.

| 앞부분 | 방식 | 키가 있는 곳 | 근거 |
|---|---|---|---|
| `01 00 00 00 D0 8C 9D DF …` | 값을 DPAPI 로 바로 감쌉니다 | 사용자 DPAPI 마스터키 | Chrome 79 소스 |
| `v10` (`76 31 30`) | AES-256-GCM. 키를 DPAPI 로 감싸 둡니다 | `Local State` 의 `os_crypt.encrypted_key` | Chrome 80 부터 소스 |
| `v20` (`76 32 30`) | AES-256-GCM. 키를 App-Bound 암호화로 감싸 둡니다 | `Local State` 의 `os_crypt.app_bound_encrypted_key` | 현재 Chromium 소스 |

- 첫 줄의 바이트는 DPAPI 블롭 머리입니다. 블롭 구조는 [DPAPI 블롭 구조](../../../01-foundations/protection/data-protection-api/dpapi-blob.md)에서 봅니다.
- Chrome 80 은 `v10` 으로 시작하지 않는 값을 옛 DPAPI 방식으로 풉니다. 그래서 오래 쓴 프로필에는 옛 방식 값이 남아 있을 수 있습니다.
- Google 은 Chrome 127 에서 App-Bound 암호화를 쿠키부터 적용했습니다. 비밀번호와 결제 정보에는 뒤에 넓히겠다고 밝혔습니다. 비밀번호에 `v20` 이 붙기 시작한 버전은 이 글에서 확인하지 못했습니다.
- 관찰한 PC 에서는 Chrome·Edge 모두 저장 비밀번호가 전부 `v20` 이었습니다. `Local State` 에는 `encrypted_key`(`DPAPI` 로 시작)와 `app_bound_encrypted_key`(`APPB` 로 시작)가 함께 있었습니다.

새 브라우저라도 `v20` 을 쓰지 않는 경우가 있습니다. Chromium 소스는 아래 조건이면 App-Bound 암호화를 켜지 않고 `v10` 으로 저장합니다.

- 브라우저를 시스템 전체가 아니라 사용자 한 명에게만 설치했습니다.
- 명령줄이나 정책으로 `User Data` 위치를 바꿨습니다.
- 정책 `ApplicationBoundEncryptionEnabled` 로 껐습니다.
- Windows 로밍 프로필을 씁니다. `HKLM\SOFTWARE\FSLogix` 키가 있어도 로밍 환경으로 봅니다.

그래서 접두사가 `v10` 인지 `v20` 인지는 설치 방식과 회사 정책을 짐작하는 단서도 됩니다.

### 스키마 버전

`meta` 표의 `version` 이 스키마 버전입니다. 현재 Chromium 소스는 43 이고 `last_compatible_version` 은 40 이며, 관찰한 Chrome 153·Edge 151 도 같은 값이었습니다. 열이 추가된 주요 버전은 다음과 같습니다.

| 스키마 버전 | 바뀐 점 |
|---|---|
| 20 | `id` 열이 생겼습니다. 26 부터 AUTOINCREMENT 입니다 |
| 25 | `date_last_used` 가 생겼습니다. 28 에서 옛 `preferred` 열이 빠졌습니다 |
| 29 | `insecure_credentials` 표가 생겼습니다 (옛 `compromised_credentials` 를 옮김) |
| 30 | `date_password_modified` 가 생겼습니다 |
| 33 | `password_notes` 표가 생겼습니다 |
| 37 | 공유받은 비밀번호용 `sender_email`·`sender_name`·`date_received` 가 생겼습니다 |
| 42 | `date_last_filled` 가 생겼습니다 |

옛 검체를 열 때는 먼저 `version` 을 보고 어떤 열이 있어야 하는지 확인합니다.

## 구조

파일은 평범한 SQLite 데이터베이스입니다. 페이지 크기는 2048바이트입니다 (Chromium 소스, 관찰도 같음). 페이지·레코드를 읽는 법은 [파일·페이지 구조 (B-tree·Record Format)](../../../01-foundations/database-log-formats/sqlite/b-tree-record-format.md)에서 다룹니다.

### logins 표의 주요 열

현재 소스 기준으로 열이 32개 있습니다. 분석에 쓰는 열만 추렸습니다.

| 열 | 형식 | 뜻 |
|---|---|---|
| `id` | 정수 | 행 번호. AUTOINCREMENT 라서 지운 번호를 다시 쓰지 않습니다 |
| `origin_url` | 문자열 | 로그인 폼이 있던 페이지 주소 (경로까지, 쿼리는 뺌) |
| `action_url` | 문자열 | 폼을 보낸 주소 |
| `signon_realm` | 문자열 | 찾을 때 쓰는 기준 값. 웹은 `https://example.com/` 꼴입니다. 안드로이드 앱 항목은 `android://<인증서 해시>@<패키지 이름>` 꼴입니다 |
| `username_element`, `password_element` | 문자열 | 폼 안 입력칸의 이름 |
| `username_value` | 문자열 | 아이디. **평문입니다** |
| `password_value` | BLOB | 암호화한 비밀번호 |
| `blacklisted_by_user` | 정수 | 1 이면 "저장 안 함" 을 고른 사이트 |
| `scheme` | 정수 | 0 HTML 폼, 1 HTTP Basic, 2 HTTP Digest, 3 기타, 4 아이디만 |
| `password_type` | 정수 | 어떻게 들어왔나 (아래 표) |
| `times_used` | 정수 | 이 아이디·비밀번호로 HTML 폼 로그인을 한 횟수 |
| `date_created` 외 시각 열 | 정수 | 아래 "시각 해석" 참고 |
| `sender_email`, `sender_name` | 문자열 | 공유로 받은 경우 보낸 사람 |

`origin_url`·`username_element`·`username_value`·`password_element`·`signon_realm` 다섯 칸을 묶은 값은 겹칠 수 없습니다 (UNIQUE 제약).

`password_type` 값은 Chromium 의 `PasswordForm::Type` 입니다. 새 값은 뒤에 붙습니다. 그래서 옛 버전에는 뒤쪽 값이 없습니다.

| 값 | 뜻 |
|---|---|
| 0 | 폼을 제출하고 저장했습니다 |
| 1 | 브라우저가 만들어 준 비밀번호입니다 |
| 2 | 사이트가 자격 증명 관리 API (Credential Management API) 로 저장했습니다 |
| 3 | 설정 화면에서 직접 추가했습니다 |
| 4 | 파일에서 가져왔습니다 |
| 5 | 다른 사용자에게서 공유받았습니다 |
| 6 | 자격 증명 교환 (Credential Exchange) 방식으로 가져왔습니다 |
| 7 | 비밀번호 변경 폼을 제출하고 저장했습니다 |

### 암호문 길이로 비밀번호 길이 알기

`v10`·`v20` 값의 모양은 "접두사 3바이트 + 논스 12바이트 + 암호문 + 인증 태그 16바이트" 입니다 (Chromium 소스). GCM 방식은 암호문 길이가 평문 길이와 같고 브라우저는 비밀번호를 UTF-8 로 바꿔서 암호화하므로, `password_value` 길이에서 31 을 빼면 복호화 없이 비밀번호의 UTF-8 바이트 수를 알 수 있습니다. 관찰한 PC 의 `v20` 값 2,000여 개에서 이 계산이 0 이하로 나온 행은 없었습니다.

옛 DPAPI 방식 값은 블롭 안에 여러 칸이 더 있어서 이 계산을 쓰지 않습니다.

### 다른 표

| 표 | 주요 열 | 뜻 |
|---|---|---|
| `stats` | `origin_domain`, `username_value`, `dismissal_count`, `update_time` | 저장 제안 창을 닫은 횟수와 고친 때 |
| `insecure_credentials` | `parent_id`, `insecurity_type`, `create_time`, `is_muted` | 점검에서 문제로 잡힌 항목 |
| `password_notes` | `parent_id`, `key`, `value`, `date_created` | 메모. `value` 는 비밀번호와 같은 방식으로 암호화합니다 (스키마 40 부터) |
| `sync_entities_metadata`, `sync_model_metadata` | | 동기화 상태 |
| `meta` | `key`, `value` | 스키마 버전 |
| `sqlite_sequence` | `name`, `seq` | `logins` 에서 지금까지 쓴 가장 큰 `id` |

관찰한 Edge 파일에는 Chromium 에 없는 표가 두 개 더 있었습니다.

- `logins_edge_extended`: `id`, `source`, `strength_alert_status`, `password_nickname`
- `breached`: `url`, `username`, `status`, `last_checked_time`, `hashed_password` 등

`meta` 에도 `edge_breached_table_version`, `logins_edge_extended_table_version` 키가 더 있었습니다. 이 칸들의 뜻은 공개 문서로 확인하지 못했습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 프로필에 이 사이트·아이디 조합이 저장돼 있었습니다 | 이 PC 에서 저장했는지. 동기화로 다른 기기의 항목이 들어옵니다 |
| 저장된 시각(`date_created`)이 있습니다 | 키보드 앞에 누가 있었는지 |
| 이 자격 증명으로 폼 로그인을 한 횟수와 마지막 때가 적혀 있습니다 | 서버가 로그인을 받아들였는지. "성공한 제출" 은 브라우저의 판단입니다 |
| "저장 안 함" 행은 그 사이트의 로그인 화면에서 저장 제안을 받은 적이 있다는 뜻입니다 | 그 사이트에서 무엇을 했는지. 방문 기록은 [History](history.md)에서 봅니다 |
| 어떤 길로 들어온 항목인지(`password_type`), 공유라면 누가 보냈는지 | 저장된 비밀번호가 지금도 맞는지 |
| 안드로이드 앱 항목이 있으면 같은 계정을 휴대폰에서도 썼다는 단서입니다 | 지운 항목이 없었다는 것 |

### 보고서 문장

아래 사이트·아이디·값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 의 Chrome `Default` 프로필 `Login Data` 에 `signon_realm` 이 `https://mail.example.com/` 이고 아이디가 `kim01` 인 행이 있습니다. 이 행의 `date_created` 는 2025-03-14 01:23:45 UTC 이고 `password_type` 은 0(폼 제출 저장)입니다. `times_used` 는 12 입니다."
- 쓰면 안 되는 문장: "사용자 A 는 2025-03-14 10:23 에 이 PC 에서 메일 계정에 로그인했습니다."

## 시각 해석

시각 열은 모두 **1601-01-01 00:00 UTC 부터 센 마이크로초** 입니다. 흔히 WebKit 시각 (WebKit/Chrome Time) 이라고 부릅니다. Chromium 의 SQLite 계층이 이 형식으로 저장합니다. 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다. 현지 시각으로 바꿀 때는 [시간대 설정](../../system-account/time-zone.md)을 씁니다.

| 열 | 바뀌는 때 (Chromium 소스 주석) | 동기화로 옮겨 가나 |
|---|---|---|
| `date_created` | 브라우저가 이 항목을 저장한 때 | 옮겨 갑니다 |
| `date_last_used` | 이 항목으로 폼 제출이 성공한 마지막 때. 처음 값은 `date_created` 입니다 | 옮겨 갑니다 |
| `date_last_filled` | 사이트에 이 항목을 채워 넣은 마지막 때. 제출 성공과 상관없습니다 | 동기화 명세에서 찾지 못했습니다 |
| `date_password_modified` | 비밀번호 값을 마지막으로 바꾼 때. 옛 항목은 비어 있을 수 있습니다 | 옮겨 갑니다 |
| `date_received` | 공유로 받은 때 | |
| `stats.update_time` | 닫은 횟수 행을 고친 때 | |
| `insecure_credentials.create_time` | 점검 결과 행을 만든 때 | |

- 값이 0 이면 "비어 있음" 입니다. 1601-01-01 로 바꾸지 않습니다.
- `date_password_modified` 가 비어 있으면 `date_last_used` 나 `date_created` 로 대신 보라고 소스 주석에 적혀 있습니다.
- 동기화 명세에는 "Chrome 이 아닌 사용처(예: Google Play 서비스)는 `date_last_used` 를 고치지 않을 수 있다" 고 적혀 있습니다. 휴대폰에서 쓴 기록은 여기에 안 남을 수 있습니다.

관찰한 PC 의 값은 소스 주석과 달랐습니다. 열이 있다고 값이 채워진다고 보면 안 됩니다.

- Chrome·Edge 모두 `date_last_filled` 가 모든 행에서 0 이었습니다.
- Chrome 은 `date_last_used` 가 0 인 행이 대부분이었습니다. 이 행들은 대부분 `password_type` 4(가져옴)였습니다.
- `date_last_used` 가 `date_created` 보다 앞선 행이 Chrome 18개, Edge 1개 있었습니다.
- Edge 는 `date_password_modified` 가 거의 모든 행에서 0 이었습니다.

## 함정과 한계

1. **복호화를 못 해서 분석을 멈춥니다.** 사이트·아이디·시각·횟수는 평문입니다. 비밀번호 길이도 암호문 길이로 압니다.
2. **`date_created` 를 이 PC 에서 저장한 시각으로 씁니다.** 동기화로 들어온 행은 처음 저장한 기기의 값을 그대로 가져옵니다. 가져오기(`password_type` 4)로 들어온 행도 이 PC 에서 폼을 쓴 기록이 아닙니다. 같은 `date_created` 근처에 행이 한꺼번에 많으면 가져오기나 동기화를 먼저 의심합니다.
3. **`times_used` 를 로그인 횟수로 단정합니다.** 브라우저가 폼 제출로 판단한 횟수입니다. 동기화로 다른 기기의 횟수가 합쳐져 옵니다.
4. **"저장 안 함" 행을 저장된 계정으로 셉니다.** 관찰한 차단 행은 `username_value` 와 `password_value` 가 비어 있었습니다. 동기화 명세도 차단 항목은 아이디·비밀번호가 비어 있다고 적습니다.
5. **`Login Data` 하나만 봅니다.** 프로필마다 파일이 따로 있습니다. `Login Data For Account` 도 따로 봅니다. 한 PC 에 계열 브라우저가 여럿이면 각각 봅니다.
6. **`v20` 을 `v10` 처럼 풀려고 합니다.** 키가 다른 곳에 있고 감싼 방식도 다릅니다. 오프라인에서는 사용자 DPAPI 말고 [시스템 DPAPI 키](../../../01-foundations/protection/data-protection-api/dpapi-system.md)도 필요합니다. 절차는 [쿠키·비밀번호 암호화](../../../01-foundations/app-mail-data/chromium-electron-webview2/dpapi-app-bound-encryption.md)를 따릅니다.
7. **`Local State` 를 빼고 수집합니다.** `Login Data` 만 가져오면 `v10`·`v20` 값을 풀 키가 없습니다. 사용자 폴더의 DPAPI 마스터키도 함께 가져옵니다 ([마스터키 파일](../../../01-foundations/protection/data-protection-api/master-key-protect-sid.md)).
8. **원본 파일을 바로 엽니다.** 사본을 만들어 엽니다. 저널 파일도 함께 복사합니다. 이유는 [WAL과 롤백 저널](../../../01-foundations/database-log-formats/sqlite/wal-journal-shm.md)에서 다룹니다. 켜져 있는 PC 에서는 브라우저가 파일을 잡고 있을 수 있습니다.
9. **브라우저 밖 비밀번호 관리자를 놓칩니다.** 비밀번호 관리 확장 프로그램을 쓰면 이 파일에 안 남습니다. [확장 프로그램](extensions.md)을 함께 봅니다.

### 지우기와 조작

- 사용자가 항목을 지우면 `logins` 행이 삭제됩니다.
- 기간을 정해 지우는 기능은 `date_created` 가 그 기간에 드는 행을 지웁니다 (소스의 `RemoveLoginsCreatedBetween`). 그래서 남은 행의 `date_created` 에 빈 구간이 생깁니다.
- Chromium 은 SQLite 를 `secure_delete` 가 켜진 상태로 빌드하며 지운 내용을 0 으로 덮으므로, 파일 안 빈 공간에서 옛 행을 되살리기 어렵습니다. Chromium 코드를 그대로 쓰는 계열 브라우저라면 같다고 보지만, 브라우저마다 검체에서 확인합니다. 빈 공간 복구 방법은 [파일 안에 남은 지운 레코드](../../../01-foundations/database-log-formats/sqlite/freelist-freeblock.md)에 있습니다.
- Chromium 은 롤백 저널을 TRUNCATE 방식으로 씁니다. 거래가 끝나면 저널 크기를 0 으로 줄이므로 저널에 있던 옛 페이지는 파일시스템의 빈 공간에만 남을 수 있습니다 ([비할당 영역과 슬랙](../../../03-techniques/analysis/data-recovery/unallocated-slack-space.md)).
- `id` 는 다시 쓰지 않습니다. 중간에 빈 번호가 있으면 지운 행이 있었다는 단서입니다. `sqlite_sequence` 의 `seq` 가 `logins` 의 가장 큰 `id` 보다 크면 마지막 쪽 행이 지워진 것입니다.
- 옛 판 파일은 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)에서 찾습니다. 동기화를 켠 계정이면 다른 기기에도 남아 있을 수 있습니다.

### 이 파일을 노린 흔적

정보 탈취 악성코드는 흔히 이 파일과 `Local State` 를 노리고, Google 이 App-Bound 암호화를 만든 까닭도 여기에 있습니다. 이 경우 `Login Data` 자체보다 둘레의 흔적을 봅니다.

- 다른 폴더에 `Login Data` 라는 이름의 파일이 생겼다가 지워진 기록을 [$UsnJrnl](../../filesystem/usnjrnl.md)에서 찾습니다.
- 브라우저가 아닌 프로그램이 실행된 흔적과 탐지 기록을 봅니다. 흐름은 [자격 증명을 빼냈나](../../../04-scenarios/incident/credential-theft-lateral-movement/credential-dumping.md)를 따릅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 Chromium 소스와 SQLite 명세로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

**`password_value` 칸 (v10, 비밀번호 8바이트일 때, 모두 39바이트)**

```
76 31 30                                          "v10"  (v20 이면 76 32 30)
5A 1C 7E 90 33 C4 08 61 F2 AB 0D 47               논스 12바이트 (예시 값)
?? ?? ?? ?? ?? ?? ?? ??                           암호문 8바이트 = 평문 UTF-8 길이
?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??   GCM 인증 태그 16바이트
```

- 앞 세 바이트가 `76 31 30` 이면 `v10` 입니다.
- 앞 네 바이트가 `01 00 00 00` 이고 그 뒤가 `D0 8C 9D DF 01 15 D1 11 …` 이면 옛 DPAPI 블롭입니다.
- 39 − 31 = 8 이므로 비밀번호는 UTF-8 로 8바이트입니다.

**`date_created` 칸**

SQLite 는 이 크기의 정수를 레코드 안에 8바이트 빅엔디언으로 적습니다 (직렬 유형 6). 2025-03-14 01:23:45 UTC 를 저장하면 이렇게 됩니다.

```
00 2F 8E D9 92 A9 0A 40      = 13,386,389,025,000,000 (마이크로초, 1601 기준)
```

1. 1,000,000 으로 나눕니다. 13,386,389,025 초가 나옵니다.
2. 1601년과 1970년 사이의 초 11,644,473,600 을 뺍니다. 1,741,915,425 가 나옵니다.
3. 이 유닉스 시각이 2025-03-14 01:23:45 UTC 입니다.

> 그림 자리: `password_value` 앞 3바이트로 방식을 가르고, 방식마다 키가 `Local State` 의 어느 값에 있고 그 값을 무엇이 감싸는지 보여 주는 흐름도

### 공개 도구로 한 번

사본을 SQLite 명령줄 도구 (sqlite3) 로 열고 아래 질의를 돌립니다. 시각은 UTC 로 나옵니다. 0 인 시각은 비워 둡니다.

```sql
SELECT id, signon_realm, origin_url, username_value,
       blacklisted_by_user, password_type, times_used,
       datetime(date_created/1000000 - 11644473600, 'unixepoch') AS created_utc,
       CASE date_last_used WHEN 0 THEN NULL
         ELSE datetime(date_last_used/1000000 - 11644473600, 'unixepoch') END AS last_used_utc,
       CASE date_password_modified WHEN 0 THEN NULL
         ELSE datetime(date_password_modified/1000000 - 11644473600, 'unixepoch') END AS pw_modified_utc,
       CAST(substr(password_value, 1, 3) AS TEXT) AS enc_prefix,
       CASE WHEN CAST(substr(password_value, 1, 3) AS TEXT) IN ('v10', 'v20')
         THEN length(password_value) - 31 END AS pw_utf8_len
FROM logins
ORDER BY date_created;

SELECT seq FROM sqlite_sequence WHERE name = 'logins';
SELECT key, value FROM meta;
```

- 결과를 읽고 나서 `meta` 의 `version` 으로 열 구성을 다시 확인합니다.
- 브라우저 기록을 한꺼번에 읽는 공개 도구 Hindsight 도 저장 비밀번호 항목을 읽습니다. 도구 결과는 위 질의 결과와 행 수·시각을 맞춰 봅니다.

## 교차 검증

| 함께 볼 것 | 맞춰 볼 점 |
|---|---|
| [방문·다운로드 기록 (History)](history.md) | `date_created`·`date_last_used` 무렵에 같은 사이트 방문이 있는지. 없으면 동기화나 가져오기를 의심합니다 |
| [쿠키 (Cookies)](cookies.md) | 같은 사이트의 로그인 쿠키가 만들어진 때 |
| [자동완성·폼 기록 (Web Data·Autofill)](web-data-autofill.md) | 아이디 입력칸에 친 값과 그 시각 |
| [프로필 폴더와 계열 브라우저 구분](../../../01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md) | 이 프로필에 로그인한 계정과 동기화 여부 |
| [마스터키 파일](../../../01-foundations/protection/data-protection-api/master-key-protect-sid.md), [오프라인 복호 재료와 절차](../../../01-foundations/protection/data-protection-api/nt.md) | 복호화에 필요한 재료가 수집됐는지 |
| [자격 증명 관리자와 볼트](../../credentials/credential-manager-windows-vault.md) | 브라우저 밖에 저장된 같은 사이트 자격 증명 |
| [파이어폭스 저장 비밀번호](../firefox/logins-json-key4-db.md), [IE 저장 비밀번호](../ie-edgehtml/intelliforms.md) | 다른 브라우저에 같은 계정이 있는지. 가져오기의 출처일 수 있습니다 |

전체 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md)과 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md)에서 다룹니다.

## 실습

크롬 계열 브라우저가 들어 있는 공개 검체(NIST CFReDS 등)로 아래 질문을 풀어 봅니다.

1. 사용자 폴더마다 프로필이 몇 개이고, 각 프로필에 `Login Data` 와 `Login Data For Account` 가 있습니까?
2. `meta` 의 `version` 은 몇이고, 그 버전에 있어야 할 열이 모두 있습니까?
3. `password_value` 앞부분은 옛 DPAPI·`v10`·`v20` 가운데 무엇입니까? 섞여 있다면 가장 늦게 저장된 옛 방식 행은 언제입니까?
4. 가장 먼저 저장된 행의 `date_created` 를 UTC 와 검체의 현지 시각으로 각각 적어 봅니다.
5. `blacklisted_by_user` 가 1 인 사이트를 History 의 방문 기록과 맞춰 봅니다.
6. `sqlite_sequence` 의 값과 `logins` 의 가장 큰 `id` 를 비교합니다. 지운 행이 있었다고 말할 수 있습니까?
7. `date_created` 가 몇 초 안에 몰린 행 묶음이 있습니까? 그 묶음의 `password_type` 은 무엇입니까?

## 참고 문헌

1. Chromium 소스 — 비밀번호 저장소. 스키마·버전 변화·삭제 문([login_database.cc](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/password_manager/core/browser/password_store/login_database.cc)), 열의 뜻과 `Type`·`Scheme` 값([password_form.h](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/password_manager/core/browser/password_form.h)), 파일 이름([password_manager_constants.cc](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/password_manager/core/browser/password_manager_constants.cc)), `stats` 표([interactions_stats.h](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/password_manager/core/browser/password_store/interactions_stats.h)).
2. Chromium 소스 — 동기화 명세. [password_specifics.proto](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/sync/protocol/password_specifics.proto).
3. Chromium 소스 — 암호화. Chrome 79·80 의 [os_crypt_win.cc (80)](https://chromium.googlesource.com/chromium/src/+/refs/tags/80.0.3987.87/components/os_crypt/os_crypt_win.cc), `v20` 접두사와 키 이름([app_bound_encryption_provider_win.h](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/chrome/browser/os_crypt/app_bound_encryption_provider_win.h)), App-Bound 를 켜는 조건([app_bound_encryption_win.cc](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/chrome/browser/os_crypt/app_bound_encryption_win.cc)).
4. Chromium 소스 — SQLite 계층. 시각 저장 형식과 저널 방식, `secure_delete`([sql/database.cc](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/sql/database.cc), [sql/statement.cc](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/sql/statement.cc)).
5. Will Harris, "Improving the security of Chrome cookies on Windows", Google Online Security Blog, 2024-07-30. <https://security.googleblog.com/2024/07/improving-security-of-chrome-cookies-on.html>
6. Obsidian Forensics, Hindsight. <https://github.com/obsidianforensics/hindsight>
