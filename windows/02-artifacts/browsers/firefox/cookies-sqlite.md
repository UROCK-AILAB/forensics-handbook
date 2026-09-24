---
title: "쿠키 (cookies.sqlite)"
parent: "파이어폭스"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1720
---

# 쿠키 (cookies.sqlite)

## 한 줄 요약

파이어폭스는 웹사이트가 심은 쿠키를 프로필 본 폴더의 `cookies.sqlite` 파일에 SQLite 형식으로 저장하는데, 크롬 계열과 달리 값을 암호화하지 않아서 어느 도메인의 쿠키를 언제 만들고 언제 마지막으로 썼는지가 평문으로 남습니다.

## 무엇을 기록하나 · 왜 생기나

- 쿠키 (Cookie) 는 웹사이트가 브라우저에 맡겨 두는 이름과 값의 쌍입니다. 로그인 상태나 방문자 식별자가 주로 여기에 담깁니다.
사이트는 서버 응답의 `Set-Cookie` 헤더나 페이지 안의 스크립트로 쿠키를 심습니다. 파일에서는 한 행이 쿠키 하나이고, 행에는 도메인·이름·경로와 함께 시각 값 여러 개가 있습니다. 페이지 안에 끼워 넣은 광고·분석 스크립트도 제3자 쿠키 (Third-party Cookie) 를 남기므로, 사용자가 주소창에 연 사이트만 쿠키를 남기는 것은 아닙니다. 세션 쿠키 (Session Cookie) 는 파일에 쓰지 않으며, 소스 주석은 세션 쿠키가 아니고 방금 DB 에서 읽은 것이 아닐 때만 기록한다고 적었습니다.

## 위치와 버전별 차이

- 위치는 프로필 본 폴더의 `cookies.sqlite` 입니다. 프로필 폴더를 찾는 법은 [프로필 구조 (profiles.ini·prefs.js)](profiles-ini-prefs-js.md) 에서 다룹니다.
- 파일의 모양은 브라우저 버전을 따릅니다. 쿠키 코드는 스키마 버전을 mozStorage 의 `GetSchemaVersion`·`SetSchemaVersion` 으로 읽고 씁니다. 이 두 함수는 `PRAGMA user_version` 을 씁니다.
- 아래 스키마와 칸은 파이어폭스 소스의 개발 중인 최신 코드(main 가지, 2026-09-23)에서 확인한 것입니다. 이때 스키마 버전 상수는 17 입니다.

### 스키마 변경 이력

같은 칸이라도 파일 버전에 따라 뜻이나 단위가 다릅니다. 특히 `expiry` 는 버전에 따라 단위가 바뀌었습니다. 분석은 파일의 스키마 버전을 먼저 확인하는 데서 시작합니다.

| 버전 변화 | 바뀐 점 |
|---|---|
| 9 → 10 | `rawSameSite` 칸을 추가하고 `sameSite` 값을 옮겨 담았습니다 |
| 11 → 12 | `schemeMap` 칸을 추가했습니다 |
| 12 → 13 | `isPartitionedAttributeSet` 칸을 추가했습니다 |
| 13 → 14 | `rawSameSite` 에 따라 `sameSite` 값을 고쳤습니다 |
| 14 → 15 | `expiry` 를 초에서 밀리초로 바꿨습니다 |
| 15 → 16 | `updateTime` 칸을 추가하고, 기존 행에는 올린 때의 현재 시각을 채웠습니다 |

- 16 에서 17 로 올릴 때는 칸을 바꾸는 코드가 없고 버전 번호만 17 로 씁니다(main 가지 소스 기준). `rawSameSite` 가 언제 빠졌는지는 확인하지 못했습니다. 현재 `CREATE TABLE` 문에는 `rawSameSite` 가 없습니다.
- 각 스키마 버전이 어느 파이어폭스 출시판에 들어갔는지는 확인하지 못했습니다.

## 구조

저장 형식은 SQLite 입니다. 페이지와 레코드를 읽는 법은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

### 저널 방식

쿠키 DB 는 `PRAGMA journal_mode = WAL`, `synchronous = NORMAL` 로 쓰므로 최근 변경이 `cookies.sqlite-wal` 에 아직 합쳐지지 않은 채로 있을 수 있고, 본 파일만 열면 최근 쿠키를 놓칩니다. WAL·롤백 저널의 차이는 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

### `moz_cookies` 의 칸

버전 17 기준 칸은 아래와 같습니다.

| 칸 | 뜻 |
|---|---|
| `id` | 행 번호입니다 |
| `originAttributes` | 컨테이너·분할 정보입니다. 기본값은 빈 문자열입니다 |
| `name` | 쿠키 이름입니다 |
| `value` | 쿠키 값입니다. 평문입니다 |
| `host` | 쿠키가 속한 도메인입니다 |
| `path` | 쿠키를 보낼 경로입니다 |
| `expiry` | 만료 시각입니다 |
| `lastAccessed` | 마지막으로 쓴 시각입니다 |
| `creationTime` | 만든 시각입니다 |
| `isSecure` | HTTPS 로만 보내는지입니다 |
| `isHttpOnly` | 스크립트가 읽지 못하게 했는지입니다 |
| `inBrowserElement` | 안쪽 브라우저 요소용인지입니다 |
| `sameSite` | SameSite 속성입니다 |
| `schemeMap` | 쿠키를 심은 스킴 표시입니다 |
| `isPartitionedAttributeSet` | 분할 쿠키 속성이 붙었는지입니다 |
| `updateTime` | 갱신 시각입니다. 무엇이 바뀔 때 갱신되는지는 확인하지 못했습니다 |

- 고유 조건은 `name, host, path, originAttributes` 입니다. 이름·호스트·경로가 같아도 `originAttributes` 가 다르면 따로 저장됩니다.
- 크롬 계열과 달리 파이어폭스는 쿠키 값을 암호화하지 않아서 `value` 가 평문입니다.

## 증거로서 의미

### 증명하는 것

- 이 프로필의 브라우저가 그 도메인의 쿠키를 받아 저장한 적이 있습니다.
- `value` 가 평문이므로 로그인 식별자나 설정 값을 바로 읽을 수 있습니다.
- `creationTime` 무렵에 그 쿠키가 처음 생겼습니다.
- `lastAccessed` 는 브라우저가 그 쿠키를 마지막으로 쓴 시각입니다. 얼마나 자주 갱신하는지는 확인하지 못했으므로 대략의 시각으로 봅니다.
- 세션 쿠키가 아닌 행이 남아 있으면 만료 시각이 정해진 영구 쿠키입니다.

### 증명하지 못하는 것

- 사용자가 그 사이트를 직접 열었다는 것은 증명하지 못합니다. 제3자 쿠키와 백그라운드 요청도 행을 만듭니다.
- 쿠키 이름과 값만으로 서버가 그 값을 어떻게 쓰는지는 알 수 없습니다.
- 키보드 앞의 사람이 누구인지는 알 수 없습니다.
- 쿠키가 없다고 방문하지 않은 것은 아닙니다. 사용자가 지웠거나, 만료됐거나, 사생활 보호 창이었을 수 있습니다.

보고서에는 "그 사이트에 접속했다" 대신 "이 프로필의 쿠키 DB 에 그 도메인 쿠키가 있고, `value` 는 이 값이며, `creationTime` 은 X(UTC) 이다" 처럼 씁니다.

## 시각 해석

파이어폭스의 쿠키 시각은 단위가 칸마다 다릅니다. 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

| 칸 | 단위 | 주의할 점 |
|---|---|---|
| `creationTime` | 마이크로초 | 1970년 1월 1일 UTC 부터 셉니다 |
| `lastAccessed` | 마이크로초 | 1970년 1월 1일 UTC 부터 셉니다 |
| `expiry` | 밀리초 (스키마 15 이후). 그 전에는 초 | 파일의 스키마 버전을 먼저 확인합니다 |
| `updateTime` | 마이크로초 | 스키마 15 이하에서 올라온 행에는 스키마를 올린 때의 시각이 들어 있습니다 |

- `creationTime` 과 `lastAccessed` 는 마이크로초입니다. 소스가 정의하는 PRTime 은 1970년 1월 1일 기준 마이크로초입니다.
- `expiry` 는 스키마 15 부터 밀리초입니다. 스키마 14 이하의 파일에서는 초입니다. 같은 칸이 파일 버전에 따라 단위가 다르므로, 변환하기 전에 `PRAGMA user_version` 을 봅니다.
- 여러 기록을 한 시간 축에 놓을 때는 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 을 따릅니다.

## 함정과 한계

- **원본을 브라우저로 열지 않습니다.** 파이어폭스로 열면 쿠키가 추가·갱신·삭제될 수 있습니다. 해시를 기록한 사본으로 분석합니다.
- **`updateTime` 이 여러 행에서 같은 값이면 스키마를 올린 시각일 수 있습니다.** 15 에서 16 으로 올릴 때 기존 행 모두에 그때 시각을 채웠습니다. 이 값을 쿠키를 바꾼 시각으로 읽지 않습니다.
- **`-wal` 파일을 함께 봅니다.** 쿠키 DB 는 WAL 방식입니다. 최근 쿠키가 본 파일에 아직 없을 수 있습니다.
- **세션 쿠키는 파일에 없습니다.** 세션 쿠키는 파일에 쓰지 않으므로 세션 쿠키만 쓰던 사이트는 이 파일에 흔적이 없습니다.
- **`expiry` 단위를 스키마 버전으로 정합니다.** 스키마 버전을 보지 않고 `expiry` 를 초로 읽으면 밀리초 파일에서 엉뚱한 연도가 나옵니다.
- **지운 쿠키는 표에서 사라집니다.** 조각이 SQLite 빈 공간이나 WAL 에 남을 수 있습니다. 옛 쿠키를 찾으려면 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md), 섀도 복사본, WAL, 메모리도 봅니다.
- **도구가 스키마 버전을 모를 수 있습니다.** 옛 도구는 빠진 칸(`updateTime` 등)을 못 보여 주거나, `expiry` 단위를 틀리게 변환할 수 있습니다. 결과가 이상하면 `PRAGMA user_version` 부터 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

쿠키 시각은 정수입니다. SQLite 레코드는 정수를 빅엔디언으로 저장합니다. 아래는 2024-01-01 00:00:00 UTC 를 명세대로 만든 예시입니다. 특정 검체에서 나온 값이 아닙니다.

```
creationTime (마이크로초):
00 06 0D D7 10 21 20 00    = 1704067200000000
1704067200000000 ÷ 1,000,000 = 1704067200 초 → 2024-01-01 00:00:00 UTC

expiry (스키마 15 이후, 밀리초):
00 00 01 8C C2 51 F4 00    = 1704067200000
1704067200000 ÷ 1,000 = 1704067200 초 → 2024-01-01 00:00:00 UTC
```

- 같은 시각이라도 마이크로초 칸과 밀리초 칸은 저장된 바이트가 다릅니다.

### 공개 도구로 한 번

`cookies.sqlite` 와 `cookies.sqlite-wal` 을 함께 사본으로 뜬 뒤, SQLite 명령줄 도구를 읽기 전용으로 열어 아래처럼 조회합니다.

```sql
PRAGMA user_version;

SELECT host, name, path, value,
       datetime(creationTime / 1000000, 'unixepoch') AS created_utc,
       datetime(lastAccessed / 1000000, 'unixepoch') AS accessed_utc,
       datetime(expiry / 1000, 'unixepoch')          AS expires_utc,
       isSecure, isHttpOnly, sameSite
FROM moz_cookies
ORDER BY creationTime;
```

- 위 `expires_utc` 는 스키마 15 이후(밀리초) 기준입니다. 스키마 14 이하면 `expiry` 를 그대로 초로 읽습니다.
- DB Browser for SQLite 같은 범용 뷰어로 같은 표를 볼 수 있습니다. 도구가 단위를 어떻게 변환했는지 위 조회 결과와 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 방문·다운로드·즐겨찾기 | 쿠키 생성 시각 무렵에 그 도메인이나 끼워 넣은 페이지를 연 기록이 있는지 봅니다 | [places.sqlite](places-sqlite.md) |
| 캐시 | 같은 도메인의 응답을 받은 시각을 봅니다 | [캐시 (cache2)](cache2.md) |
| 웹 저장소 | 같은 사이트가 로컬 저장소에도 흔적을 남겼는지 봅니다 | [웹 저장소 (storage 폴더)](storage.md) |
| 저장 비밀번호 | 같은 사이트에 로그인 정보를 저장했는지 봅니다 | [저장 비밀번호 (logins.json·key4.db)](logins-json-key4-db.md) |
| 다른 브라우저 쿠키 | 같은 사이트를 다른 브라우저로 썼는지 봅니다 | [크롬 계열 쿠키](../chrome-edge-whale/cookies.md) |

웹 사용 전체를 재구성하는 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) 에 있습니다.

## 실습

파이어폭스를 쓴 공개 검체(NIST CFReDS 등)에서 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. `PRAGMA user_version` 은 몇입니까? 그 버전에서 `expiry` 는 초입니까 밀리초입니까?
2. `value` 가 평문인 로그인성 쿠키를 골라, 그 도메인의 방문 기록 첫 방문 시각과 `creationTime` 을 비교해 봅니다.
3. `host` 가 점(`.`)으로 시작하는 도메인 쿠키와 그렇지 않은 호스트 쿠키를 각각 셉니다.
4. 방문 기록에 없는 도메인의 쿠키를 모읍니다. 어떤 종류의 서비스가 많습니까?

## 참고 문헌

1. Mozilla, *CookiePersistentStorage.cpp* (파이어폭스 소스, main 가지 — 스키마 버전, 칸, 저널 방식, 시각 단위, 세션 쿠키 처리). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/netwerk/cookie/CookiePersistentStorage.cpp
2. Mozilla, *nsINavHistoryService.idl* (파이어폭스 소스, main 가지 — PRTime 정의). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/components/places/nsINavHistoryService.idl
3. Mozilla, *mozStorageConnection.cpp* (파이어폭스 소스, main 가지 — 스키마 버전과 `PRAGMA user_version`). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/storage/mozStorageConnection.cpp
