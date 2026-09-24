# 쿠키 (Cookies)

## 한 줄 요약

크롬 계열 브라우저는 웹사이트가 심은 쿠키를 프로필 폴더의 `Network\Cookies` 파일에 SQLite 형식으로 저장합니다. 쿠키 값은 암호화되어 있습니다. 하지만 어느 도메인의 쿠키를 언제 받았고, 언제 마지막으로 바꾸고 보냈는지는 평문으로 남습니다.

## 무엇을 기록하나 · 왜 생기나

- 쿠키 (Cookie) 는 웹사이트가 브라우저에 맡겨 두는 이름과 값의 쌍입니다. 로그인 상태, 사이트 설정, 방문자 추적 식별자가 주로 여기에 담깁니다.
- 사이트는 두 가지 방법으로 쿠키를 심습니다. 서버가 HTTP 응답의 `Set-Cookie` 헤더로 심거나, 페이지 안의 스크립트가 심습니다.
- 브라우저는 같은 사이트로 요청을 보낼 때 이 쿠키를 함께 보냅니다.
- 사용자가 주소창에 연 사이트만 쿠키를 남기는 것은 아닙니다. 페이지 안에 끼워 넣은 광고·분석 스크립트나 iframe 도 제3자 쿠키 (Third-party Cookie) 를 남깁니다.
- 파일에서는 한 행이 쿠키 하나입니다. 행에는 도메인·이름·경로와 함께 시각 값이 네 개 있습니다. 처음 만든 시각, 마지막으로 바꾼 시각, 마지막으로 쓴 시각, 만료 시각입니다.
- 브라우저는 바뀐 내용을 메모리에 모아 두었다가 한꺼번에 파일에 씁니다. 크로미엄 소스에서 이 주기는 30초입니다. 밀린 작업이 512개가 되면 주기를 기다리지 않고 바로 씁니다.
- 이름·도메인·경로가 같은 쿠키를 다시 심으면 브라우저는 옛 행을 지우고 새 행을 넣습니다.

## 위치와 버전별 차이

쿠키 파일의 모양은 윈도 버전이 아니라 브라우저 버전을 따릅니다.

### 파일 위치

크롬 계열 브라우저는 모두 `User Data\<프로필>\` 아래에 같은 이름으로 쿠키 파일을 둡니다. 프로필 폴더 이름(`Default`, `Profile 1` 등)과 브라우저별 차이는 [프로필 폴더와 계열 브라우저 구분](/01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md) 에서 다룹니다.

| 브라우저 | 기본 User Data 위치 |
|---|---|
| Chrome | `%LOCALAPPDATA%\Google\Chrome\User Data` |
| Edge | `%LOCALAPPDATA%\Microsoft\Edge\User Data` |
| Whale | `%LOCALAPPDATA%\Naver\Naver Whale\User Data` |

| 쿠키 파일 경로 | 쓰는 버전 |
|---|---|
| `<프로필>\Cookies` | 네트워크 기능을 샌드박스 (Sandbox) 에 넣기 전 버전 |
| `<프로필>\Network\Cookies` | 현재 버전 |

크로미엄은 네트워크 기능을 샌드박스 안에서 돌리면서 쿠키 파일을 `Network` 폴더로 옮겼습니다. 옮기는 순서는 다음과 같습니다(크로미엄 `network_sandbox.cc` 기준).

1. `Cookies` 와 `Cookies-journal` 을 `Network` 폴더로 복사합니다.
2. 복사가 모두 끝나면 `Network` 폴더에 `NetworkDataMigrated` 파일을 만듭니다. 이 파일에는 내용이 없습니다.
3. 프로필 폴더 바로 아래에 있던 옛 파일을 지웁니다.

이 순서 때문에 분석에서 볼 점이 셋 있습니다.

- `NetworkDataMigrated` 가 있으면 옮기기가 끝난 프로필입니다. 이 파일의 생성 시각으로 옮긴 때를 짐작할 수 있습니다.
- `Network\Cookies` 의 파일 생성 시각은 옮긴 때입니다. 프로필을 처음 만든 때가 아닙니다.
- 옛 `Cookies` 는 지운 파일로 남을 수 있습니다. 옮기기 전 상태를 볼 수 있는 곳입니다.

Electron·WebView2 로 만든 앱도 크로미엄의 쿠키 형식을 그대로 씁니다. 앱별 위치는 [Electron·WebView2 앱 데이터 위치](/01-foundations/app-mail-data/chromium-electron-webview2/teams-discord-slack.md) 에 있습니다.

### DB 스키마 버전

`meta` 표의 `version` 값으로 스키마를 구분합니다. 아래 날짜는 크로미엄 소스 주석에 적힌 반영 날짜입니다. 실제 배포 버전에는 몇 주 뒤에 들어갑니다. 2026년 9월 main 브랜치 기준 최신 버전은 24입니다.

| version | 반영 날짜 | 바뀐 점 |
|---|---|---|
| 7 | 2013-12-16 | `encrypted_value` 열을 추가했습니다 |
| 10 | 2018-02-13 | 참·거짓 열 이름에 `is_` 를 붙였습니다(`secure` → `is_secure` 등) |
| 11 | 2019-04-17 | `firstpartyonly` 열을 `samesite` 로 바꿨습니다 |
| 12 | 2019-11-20 | `source_scheme` 열을 추가했습니다 |
| 13 | 2020-10-28 | `source_port` 열을 추가했습니다 |
| 14 | 2021-02-23 | 윈도에서 암호화한 값을 모두 새 키로 다시 썼습니다 |
| 15 | 2021-07-01 | `top_frame_site_key` 열을 추가했습니다 |
| 18 | 2022-04-19 | `last_update_utc` 열을 추가했습니다 |
| 19 | 2023-09-22 | 저장된 만료 시각을 400일 이내로 잘랐습니다 |
| 22 | 2024-03-22 | `source_type` 열을 추가했습니다 |
| 23 | 2024-04-10 | `has_cross_site_ancestor` 값을 채웠습니다 |
| 24 | 2024-08-15 | 암호화하기 전에 값 앞에 도메인의 SHA-256 해시를 붙였습니다 |

### 값 암호화 방식

`encrypted_value` 의 첫 바이트를 보면 어느 방식인지 알 수 있습니다. 키가 어디 있고 어떻게 푸는지는 [쿠키·비밀번호 암호화](/01-foundations/app-mail-data/chromium-electron-webview2/dpapi-app-bound-encryption.md) 에서 다룹니다.

| 첫머리 | 방식 | 키 |
|---|---|---|
| `01 00 00 00 D0 8C 9D DF …` | 옛 방식입니다. 값 전체가 사용자 DPAPI 블롭입니다 | 사용자 [DPAPI 마스터키](/01-foundations/protection/data-protection-api/master-key-protect-sid.md) |
| `v10` (`76 31 30`) | AES-256-GCM 입니다 | `Local State` 의 `os_crypt.encrypted_key`. `DPAPI` 다섯 글자 뒤에 사용자 DPAPI 블롭이 있습니다 |
| `v20` (`76 32 30`) | 앱 바인딩 암호화 (App-Bound Encryption) 입니다. Chrome 127 부터 쿠키에 씁니다 | `Local State` 의 `os_crypt.app_bound_encrypted_key`. `APPB` 네 글자로 시작합니다. SYSTEM 권한 서비스를 거쳐야 풀립니다 |

- 옛 방식 블롭의 구조는 [DPAPI 블롭 구조](/01-foundations/protection/data-protection-api/dpapi-blob.md) 에 있습니다.
- DB 버전 14 에서 윈도판은 모든 값을 새 방식으로 다시 암호화했습니다.
- Edge·Whale 이 `v20` 을 쓰는지는 브라우저와 버전마다 다릅니다. 행마다 첫 3바이트를 직접 확인합니다.

## 구조

저장 형식은 SQLite 입니다. 페이지와 레코드를 읽는 법은 [SQLite 데이터베이스](/01-foundations/database-log-formats/sqlite/index.md) 와 [파일·페이지 구조](/01-foundations/database-log-formats/sqlite/b-tree-record-format.md) 에서 다룹니다.

### 파일

| 파일 | 설명 |
|---|---|
| `Cookies` | SQLite 주 파일입니다 |
| `Cookies-journal` | 롤백 저널입니다. 크로미엄은 저널을 TRUNCATE 방식으로 씁니다. 커밋이 끝나면 길이가 0 이 됩니다 |

크로미엄의 SQLite 연결은 따로 켜야만 WAL 을 씁니다. 쿠키 DB 는 이 설정을 켜지 않습니다(2026년 9월 소스 기준). 그래서 `Cookies-wal` 파일은 생기지 않습니다. 저널 방식의 차이는 [WAL과 롤백 저널](/01-foundations/database-log-formats/sqlite/wal-journal-shm.md) 에서 다룹니다.

### 표

`meta` 표에는 `version` 과 `last_compatible_version` 이 있습니다. 쿠키는 `cookies` 표에 있습니다. 아래는 DB 버전 24 의 열입니다.

| 열 | 뜻 | 분석에서 보는 점 |
|---|---|---|
| `creation_utc` | 쿠키를 만든 시각 | 아래 "시각 해석" 절에서 다룹니다 |
| `host_key` | 쿠키가 속한 도메인 | 점(`.`)으로 시작하면 하위 도메인에도 보내는 도메인 쿠키입니다. 점이 없으면 그 호스트에만 보냅니다 |
| `top_frame_site_key` | 분할 쿠키 (Partitioned Cookie) 를 만든 최상위 사이트 | 비어 있으면 분할 쿠키가 아닙니다. 값이 있으면 어느 사이트 안에서 끼워 넣은 페이지가 심었는지 알려 줍니다 |
| `name` | 쿠키 이름 | |
| `value` | 평문 값 | 암호화를 쓰면 빈 문자열입니다 |
| `encrypted_value` | 암호화한 값 | 첫 3바이트로 방식을 구분합니다 |
| `path` | 쿠키를 보낼 경로 | |
| `expires_utc` | 만료 시각 | 세션 쿠키는 0 입니다 |
| `is_secure` | HTTPS 로만 보내는지 | |
| `is_httponly` | 스크립트가 읽지 못하게 했는지 | |
| `last_access_utc` | 마지막으로 쓴 시각 | 사용자 동작과 같지 않습니다 |
| `has_expires`, `is_persistent` | 영구 쿠키인지 | 두 열에 같은 값을 씁니다. 0 이면 세션 쿠키 (Session Cookie) 입니다 |
| `priority` | 공간이 모자랄 때 지우는 순서 | 0 낮음, 1 보통, 2 높음 |
| `samesite` | SameSite 속성 | -1 지정 안 함, 0 None, 1 Lax, 2 Strict |
| `source_scheme` | 쿠키를 심은 곳의 스킴 | 0 모름, 1 보안 아님(http), 2 보안(https) |
| `source_port` | 쿠키를 심은 곳의 포트 | -1 은 모름입니다 |
| `last_update_utc` | 마지막으로 심거나 바꾼 시각 | 0 이면 기록이 없습니다 |
| `source_type` | 마지막으로 심은 주체 | 0 모름, 1 HTTP 응답, 2 스크립트, 3 기타 |
| `has_cross_site_ancestor` | 분할 쿠키 키의 일부 | 상위 프레임에 다른 사이트가 끼어 있었는지 표시합니다 |

고유 색인 `cookies_unique_index` 는 `host_key, top_frame_site_key, has_cross_site_ancestor, name, path, source_scheme, source_port` 로 행을 구분합니다. 이 조합이 같은 쿠키는 한 행만 남습니다.

### encrypted_value 안의 모양

아래는 크로미엄 소스로 만든 예시입니다. 특정 검체에서 나온 값이 아닙니다.

```
76 31 30                                     "v10" 접두사 (v20 이면 76 32 30)
xx xx xx xx xx xx xx xx xx xx xx xx          논스 (Nonce) 12바이트
.. .. .. .. ..                               암호문 (평문과 길이가 같음)
tt tt tt tt tt tt tt tt tt tt tt tt tt tt tt tt   인증 태그 16바이트
```

DB 버전 24 이상에서는 평문 앞 32바이트가 `host_key` 의 SHA-256 해시입니다. 실제 쿠키 값은 그 뒤에 이어집니다. 크로미엄은 풀고 나서 이 해시가 `host_key` 와 맞는지 확인합니다. 맞지 않으면 그 행을 불러오지 않습니다.

## 증거로서 의미

### 증명하는 것

- 이 프로필의 브라우저가 그 도메인의 쿠키를 받아 저장한 적이 있습니다.
- `last_update_utc` 시각에 그 쿠키를 마지막으로 심었거나 바꿨습니다.
- `last_access_utc` 시각 무렵에 브라우저가 그 쿠키를 요청에 실었거나 스크립트에 넘겼습니다.
- `source_type` 이 1 이면 서버 응답이 심었고, 2 이면 페이지 스크립트가 심었습니다.
- `top_frame_site_key` 에 값이 있으면 그 최상위 사이트를 보는 중에 쿠키가 생겼습니다.
- `is_persistent` 가 0 인 행이 남아 있으면 그 쿠키가 생긴 뒤 어떤 조건의 재시작이 없었다는 뜻입니다. 크로미엄은 두 조건이 모두 맞으면 시작할 때 세션 쿠키를 모두 지웁니다. 하나는 시작 설정이 "이어서 열기" 가 아닌 것이고, 다른 하나는 직전 종료가 비정상 종료가 아닌 것입니다.

### 증명하지 못하는 것

- 사용자가 그 사이트를 직접 열었다는 것은 증명하지 못합니다. 제3자 쿠키와 백그라운드 요청도 행을 만듭니다.
- 사용자가 그 사이트에 로그인했다는 것은 쿠키 이름만으로 증명하지 못합니다. 값을 풀어도 서버가 그 값을 어떻게 쓰는지는 따로 확인해야 합니다.
- 페이지를 무엇을 보았는지, 얼마나 머물렀는지는 알 수 없습니다.
- 키보드 앞의 사람이 누구인지는 알 수 없습니다.
- 쿠키가 없다고 방문하지 않은 것은 아닙니다. 사용자가 지웠거나, 만료됐거나, 시크릿 창 (Incognito) 이었거나, 사이트 쿠키를 막는 설정이었을 수 있습니다.

보고서에는 "A 사이트에 접속했다" 대신 "이 프로필의 쿠키 DB 에 A 도메인 쿠키가 있고, 마지막으로 바뀐 시각은 X(UTC) 이다" 처럼 씁니다.

## 시각 해석

모든 시각 열은 1601년 1월 1일 00:00 UTC 부터 센 마이크로초입니다. 현지 시각이 아닙니다. 0 은 값이 없다는 뜻입니다. 변환은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

> 그림 자리: 쿠키 하나를 심고, 같은 값으로 다시 심고, 다른 값으로 바꾸고, 요청에 실어 보낼 때 네 시각 열이 각각 어떻게 움직이는지 보여 주는 시간 축 그림

| 열 | 언제 바뀌나 | 주의할 점 |
|---|---|---|
| `creation_utc` | 쿠키를 새로 심을 때입니다. 같은 값으로 다시 심으면 옛 시각을 물려받습니다. 값이 바뀌면 새 시각이 됩니다 | "처음 방문한 때" 가 아니라 "지금 값이 처음 생긴 때" 에 가깝습니다 |
| `last_update_utc` | 쿠키를 심거나 다시 심을 때마다 바뀝니다 | DB 버전 18 전에 만든 행은 0 입니다 |
| `last_access_utc` | 쿠키를 만들 때 `creation_utc` 와 같은 값으로 채웁니다. 그 뒤 요청에 실어 보내거나 스크립트가 읽을 때 바뀝니다. 직전 기록에서 60초가 지나야 새로 씁니다 | 다른 탭이나 백그라운드 요청도 이 값을 바꿉니다. `creation_utc` 와 같으면 만든 뒤 60초가 지나서 쓴 기록은 없습니다 |
| `expires_utc` | 사이트가 정합니다 | 크로미엄은 만료 시각을 만든 때로부터 400일 뒤까지로 자릅니다. 세션 쿠키는 0 입니다 |

- 브라우저는 바뀐 내용을 최대 30초 모았다가 씁니다. 브라우저를 강제로 끄면 마지막 몇십 초의 변경이 파일에 없을 수 있습니다.
- `last_access_utc` 는 60초 단위로만 갱신되므로 마지막 사용 시각보다 최대 1분 가까이 이를 수 있습니다.
- 사이트가 늘 같은 수명(`Max-Age`)을 주는 쿠키라면 `expires_utc` 에서 그 수명을 빼서 마지막으로 심은 시각을 짐작할 수 있습니다. `last_update_utc` 가 없는 옛 DB 에서 쓸 만한 추정입니다. 보고서에는 추정이라고 밝힙니다.
- 여러 기록을 한 시간 축에 놓을 때는 [시간대·시계 오차 보정](/03-techniques/analysis/timeline/time-normalization.md) 을 따릅니다.

## 함정과 한계

- **원본 프로필을 브라우저로 열지 않습니다.** 브라우저는 시작할 때 세션 쿠키를 지웁니다. 만료된 쿠키도 불러온 뒤 정리합니다. 스키마 버전이 브라우저가 지원하지 않을 만큼 옛것이면 파일을 지우고 새로 만들 수 있습니다. 항상 해시를 기록한 사본을 SQLite 도구로 엽니다.
- **실행 중에는 복사가 막힐 수 있습니다.** 윈도판 크로미엄은 쿠키 DB 를 단독 잠금으로 여는 것이 기본값입니다. 라이브 수집에서는 섀도 복사본이나 원시 디스크 읽기를 씁니다. [라이브 응답](/03-techniques/process-acquisition/live-response/index.md) 을 참고합니다.
- **브라우저를 닫는 것도 증거를 바꿉니다.** "종료 시 쿠키 삭제" 로 정한 사이트의 쿠키는 브라우저를 닫을 때 지워집니다.
- **지운 쿠키는 DB 안에서 되살리기 어렵습니다.** 크로미엄은 SQLite 의 `secure_delete` 를 기본으로 켭니다. 지운 행 자리는 0 으로 덮입니다. 그래서 [프리리스트·프리블록](/01-foundations/database-log-formats/sqlite/freelist-freeblock.md) 에서 옛 행을 찾을 가능성이 낮습니다.
- **DB 밖에는 남을 수 있습니다.** 커밋 전 원래 페이지는 `Cookies-journal` 에 먼저 적힙니다. 이 저널은 커밋 뒤 길이만 0 으로 줄어듭니다. 그래서 전에 쓰던 클러스터가 [비할당 영역](/03-techniques/analysis/data-recovery/unallocated-slack-space.md) 에 남을 수 있습니다. 옮기기 전 옛 `Cookies`, [섀도 복사본](/03-techniques/analysis/volume-shadow-copy-analysis.md), 메모리도 봅니다. SSD 에서는 [TRIM](/03-techniques/analysis/data-recovery/ssd-trim.md) 때문에 이런 흔적이 빨리 사라집니다.
- **값을 못 풀어도 할 수 있는 일이 많습니다.** 도메인·이름·경로·시각은 평문입니다. 값 길이도 계산할 수 있습니다. DB 버전 24 이상의 `v10`·`v20` 행은 `encrypted_value` 길이에서 63(접두사 3 + 논스 12 + 해시 32 + 태그 16)을 빼면 값의 바이트 수입니다. 버전 24 전이면 31을 뺍니다.
- **복호 도구가 해시를 떼는지 확인합니다.** DB 버전 24 이상에서 앞 32바이트를 떼지 않으면 값 앞에 깨진 글자가 붙어 나옵니다.
- **`v20` 은 사용자 비밀번호만으로 풀리지 않습니다.** 사용자 DPAPI 에 더해 SYSTEM 쪽 재료가 필요합니다. [시스템 DPAPI 키](/01-foundations/protection/data-protection-api/dpapi-system.md) 와 [오프라인 복호 재료와 절차](/01-foundations/protection/data-protection-api/nt.md) 를 참고합니다.
- **평문 `value` 가 있는 행을 눈여겨봅니다.** 윈도판 크롬 계열 브라우저는 암호화를 쓰면 `value` 를 비워 둡니다. `value` 와 `encrypted_value` 가 둘 다 찬 행은 현재 크로미엄이 불러오지 않고 버립니다. 이런 행은 옛 버전이나 다른 프로그램이 쓴 것일 수 있습니다.
- **시크릿 창의 쿠키는 파일에 없습니다.** 시크릿 창은 쿠키를 메모리에만 둡니다. [시크릿 모드로 무엇을 했나](/04-scenarios/activity/private-browsing.md) 를 참고합니다.
- **프로필마다 쿠키 파일이 따로 있습니다.** `Default` 만 보고 끝내지 않습니다.
- **도구가 스키마 버전을 모를 수 있습니다.** 옛 도구는 `secure`·`httponly` 같은 옛 열 이름을 찾다가 실패합니다. 새 열(`last_update_utc`, `source_type`)을 빼고 보여 주는 도구도 있습니다. 결과가 이상하면 `meta` 표의 버전부터 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

**시각 값.** SQLite 레코드는 정수를 빅엔디언으로 저장합니다. 아래는 2024-01-01 00:00:00 UTC 를 명세대로 만든 예시입니다. 크기가 커서 8바이트 정수(serial type 6)로 들어갑니다.

```
00 2F 6C 6D 58 A7 60 00    = 13348540800000000
13348540800000000 ÷ 1,000,000 = 13348540800 초 (1601-01-01 부터)
13348540800 − 11644473600   = 1704067200 (1970-01-01 부터 센 초)
→ 2024-01-01 00:00:00 UTC
```

11644473600 은 1601년 1월 1일과 1970년 1월 1일 사이의 초 수입니다.

**값의 첫머리.** `encrypted_value` 칸의 첫 3바이트가 `76 31 30` 이면 `v10`, `76 32 30` 이면 `v20` 입니다. 접두사 없이 `01 00 00 00 D0 8C 9D DF` 로 시작하면 옛 DPAPI 블롭입니다.

**풀린 값의 해시.** 도메인이 `.example.com` 이면 DB 버전 24 이상에서 풀린 평문의 앞 32바이트는 아래와 같아야 합니다. 이 값은 문자열 `.example.com` 의 SHA-256 을 계산한 것입니다.

```
14 96 29 5B 2B E8 C8 8D 72 9A 34 16 3E 68 85 B0
47 08 33 C3 4E 8B 5B 53 C3 70 A9 F5 DB B7 70 09
```

앞 32바이트가 행의 `host_key` 해시와 같으면 키와 풀이 방법이 맞은 것입니다. 다르면 키가 틀렸거나, 다른 행의 값을 옮겨 붙인 것입니다.

### 공개 도구로 한 번

`Cookies` 와 `Cookies-journal` 을 함께 사본으로 뜬 뒤, SQLite 명령줄 도구를 읽기 전용으로 열어 아래처럼 조회합니다.

```sql
SELECT value AS schema_version FROM meta WHERE key = 'version';

SELECT host_key, name, path,
       datetime(nullif(creation_utc, 0)   / 1000000 - 11644473600, 'unixepoch') AS created_utc,
       datetime(nullif(last_update_utc, 0) / 1000000 - 11644473600, 'unixepoch') AS updated_utc,
       datetime(nullif(last_access_utc, 0) / 1000000 - 11644473600, 'unixepoch') AS accessed_utc,
       datetime(nullif(expires_utc, 0)    / 1000000 - 11644473600, 'unixepoch') AS expires_utc,
       is_persistent, source_type, top_frame_site_key,
       CAST(substr(encrypted_value, 1, 3) AS TEXT) AS enc_tag,
       length(encrypted_value) AS enc_len
FROM cookies
ORDER BY creation_utc;
```

- `nullif` 는 0 을 빈 값으로 바꿉니다. 0 을 그대로 변환하면 1601년이 나와 오해를 부릅니다.
- `enc_tag` 로 행마다 암호화 방식을 셉니다.
- DB Browser for SQLite 같은 범용 뷰어로 같은 표를 볼 수 있습니다. Hindsight 같은 크로미엄 전용 공개 도구는 시각 변환과 `Network` 폴더 확인을 대신 해 줍니다. 도구 결과는 위 조회 결과와 한 번 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 방문 기록 | 쿠키 생성 시각 무렵에 그 도메인이나 끼워 넣은 페이지를 연 기록이 있는지 봅니다 | [방문·다운로드 기록](/02-artifacts/browsers/chrome-edge-whale/history.md) |
| 캐시 | 같은 도메인의 응답을 받은 시각을 봅니다 | [캐시](/02-artifacts/browsers/chrome-edge-whale/cache.md) |
| 웹 저장소 | 같은 사이트가 로컬 저장소에도 흔적을 남겼는지 봅니다 | [웹 저장소](/02-artifacts/browsers/chrome-edge-whale/local-storage-indexeddb.md) |
| 저장 비밀번호 | 같은 사이트에 로그인 정보를 저장했는지 봅니다 | [저장 비밀번호](/02-artifacts/browsers/chrome-edge-whale/login-data.md) |
| 세션·탭 복원 | 세션 쿠키가 남은 이유(세션 복원 설정)와 열린 탭을 봅니다 | [세션·탭 복원](/02-artifacts/browsers/chrome-edge-whale/sessions.md) |
| 확장 프로그램 | 확장 프로그램이 요청을 보내 쿠키를 만들었을 가능성을 봅니다 | [확장 프로그램](/02-artifacts/browsers/chrome-edge-whale/extensions.md) |
| $MFT·$UsnJrnl | `Cookies`·`NetworkDataMigrated` 의 생성 시각과 옛 `Cookies` 삭제 기록을 봅니다 | [$MFT](/02-artifacts/filesystem/mft.md), [$UsnJrnl](/02-artifacts/filesystem/usnjrnl.md) |
| SRUM 네트워크 사용량 | 그 시간대에 브라우저가 실제로 통신했는지 봅니다 | [네트워크 사용량](/02-artifacts/execution/system-resource-usage-monitor/network-data-usage.md) |
| 응용 프로그램 이벤트 로그 | 앱 바인딩 검증에 실패한 기록이 Application 로그에 남는지 봅니다. 다른 프로그램이 쿠키를 풀려고 한 흔적일 수 있습니다. 이벤트 원본과 ID 는 판마다 검체에서 확인합니다 | [자격 증명을 빼냈나](/04-scenarios/incident/credential-theft-lateral-movement/credential-dumping.md) |
| 다른 브라우저 쿠키 | 같은 사이트를 다른 브라우저로 썼는지 봅니다 | [파이어폭스 쿠키](/02-artifacts/browsers/firefox/cookies-sqlite.md), [IE 쿠키·캐시 폴더](/02-artifacts/browsers/ie-edgehtml/inetcookies-inetcache.md) |

웹 사용 전체를 재구성하는 흐름은 [웹 사용 행위 재구성](/04-scenarios/activity/web-activity.md) 에 있습니다.

## 실습

크롬이나 엣지를 쓴 공개 검체(NIST CFReDS 등)에서 사용자 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. 프로필 폴더 바로 아래의 `Cookies` 와 `Network\Cookies` 가운데 어느 것이 있습니까? `NetworkDataMigrated` 가 있다면 생성 시각은 언제입니까?
2. `meta` 표의 `version` 은 몇입니까? 그 버전에 있어야 할 열이 실제로 다 있습니까?
3. `encrypted_value` 첫 3바이트로 행을 나누면 `v10`·`v20`·옛 DPAPI 블롭이 각각 몇 행입니까?
4. `is_persistent` 가 0 인 행이 있습니까? 있다면 그 행의 `creation_utc` 와 방문 기록의 마지막 방문 시각을 비교해 봅니다.
5. 한 도메인을 골라 쿠키의 `creation_utc` 와 방문 기록의 첫 방문 시각이 몇 초 차이 나는지 봅니다. 방문 기록에 없는 제3자 도메인은 어느 페이지를 연 시각과 겹칩니까?
6. `source_type` 이 2(스크립트)인 쿠키의 도메인을 모읍니다. 어떤 종류의 서비스가 많습니까?

## 참고 문헌

1. Chromium, *net/extras/sqlite/sqlite_persistent_cookie_store.cc* (쿠키 DB 스키마, 버전 기록, 기록 주기, 해시 접두사). https://chromium.googlesource.com/chromium/src/+/refs/heads/main/net/extras/sqlite/sqlite_persistent_cookie_store.cc
2. Chromium, *net/cookies/cookie_monster.cc* (마지막 사용 시각 60초 기준, 생성 시각 물려받기, 만료 쿠키 정리). https://chromium.googlesource.com/chromium/src/+/refs/heads/main/net/cookies/cookie_monster.cc
3. Chromium, *chrome/browser/profiles/profile_impl.cc* (세션 쿠키 보존과 복원 조건). https://chromium.googlesource.com/chromium/src/+/refs/heads/main/chrome/browser/profiles/profile_impl.cc
4. Chromium, *content/browser/network_sandbox.cc* (`Network` 폴더로 옮기는 절차와 `NetworkDataMigrated`). https://chromium.googlesource.com/chromium/src/+/refs/heads/main/content/browser/network_sandbox.cc
5. Chromium, *sql/database.cc* (`secure_delete` 기본값, TRUNCATE 저널 방식). https://chromium.googlesource.com/chromium/src/+/refs/heads/main/sql/database.cc
6. Will Harris, *Improving the security of Chrome cookies on Windows*, Google Security Blog (2024-07-30). https://security.googleblog.com/2024/07/improving-security-of-chrome-cookies-on.html
