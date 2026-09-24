# 파이어폭스 (Firefox)

## 한 줄 요약

파이어폭스는 모질라 (Mozilla) 가 만드는 브라우저입니다. 크롬 계열과는 다른 코드로 만들어 파일 이름·형식·시각 기준이 다릅니다. 사용자마다 프로필 (Profile) 폴더를 두고, 그 안에 방문 기록·쿠키·캐시·저장 비밀번호·세션·양식 기록·추가 기능 목록을 파일별로 남깁니다.

## 왜 중요한가

- 한 PC 에 브라우저가 여럿이면 기록도 브라우저마다 따로 쌓입니다. 크롬 계열만 보고 끝내면 파이어폭스로 한 일을 놓칩니다.
- 크롬 계열에서 익힌 읽는 법을 그대로 쓰면 틀립니다. 파일 이름과 표 이름이 다르고, 시각을 세는 기준일도 다릅니다.
- 기록 대부분은 SQLite·JSON 파일입니다. 브라우저를 띄우지 않고 공개 도구로 읽을 수 있습니다.
- 프로필 폴더는 Windows 사용자 폴더 아래 있습니다. 그래서 어느 Windows 계정의 기록인지 알 수 있습니다.
- 한 계정 안에도 파이어폭스 프로필이 여러 개일 수 있습니다. 프로필마다 기록이 따로 쌓입니다.
- 지운 흔적을 따로 담는 표도 있습니다. 즐겨찾기의 `moz_bookmarks_deleted`, 양식 기록의 `moz_deleted_formhistory` 가 그 예입니다. 다만 이 표에 어떤 조건에서 행이 들어가는지는 이번 조사에서 확인하지 못했습니다. 표가 비어 있다고 지운 항목이 없다고 보지 않습니다.

증명하지 못하는 것도 분명합니다.

- 기록은 Windows 계정과 파이어폭스 프로필 단위로 남습니다. 그 시각에 누가 키보드 앞에 있었는지는 남지 않습니다.
- 방문 기록은 페이지를 불러왔다는 기록입니다. 사용자가 그 페이지를 읽었는지, 거기서 무엇을 했는지는 방문 기록만으로 알 수 없습니다.
- 사용자는 기록을 지울 수 있습니다. 기록이 없다는 것만으로 방문하지 않았다고 단정하지 않습니다.
- 사생활 보호 창 (Private Browsing) 에서 한 일이 각 파일에 어떻게 남는지는 이번 조사에서 소스로 확인하지 못했습니다. [시크릿 모드로 무엇을 했나](/04-scenarios/activity/private-browsing.md) 를 참고합니다.

## 한눈에 보기

> 그림 자리: `profiles.ini` 에서 프로필 본 폴더와 로컬 폴더로 이어지고, 각 폴더 아래 주요 파일(`places.sqlite`·`cookies.sqlite`·`logins.json`·`key4.db`·세션 파일·`formhistory.sqlite`·`extensions.json`·`storage`·`cache2`)이 달린 나무 그림. 파일마다 어느 폴더에 있는지는 검체에서 확인한 뒤 그린다

### 위치

| 폴더 | Windows 기본 위치 | 담는 것 |
|---|---|---|
| 프로필 본 폴더 (root) | `%APPDATA%\Mozilla\Firefox\Profiles` | 오래 남길 데이터 |
| 프로필 로컬 폴더 (local) | `%LOCALAPPDATA%\Mozilla\Firefox\Profiles` | 지워도 되는 캐시 |

- 프로필 하나는 폴더 한두 개로 이루어집니다. 두 개일 때 본 폴더에는 오래 남길 데이터가 있고, 로컬 폴더에는 캐시가 있습니다.
- 어느 프로필이 있고 어느 것이 기본인지는 `profiles.ini` 가 알려 줍니다. 자세한 내용은 [프로필 구조 (profiles.ini·prefs.js)](/02-artifacts/browsers/firefox/profiles-ini-prefs-js.md) 에서 다룹니다.
- 수집할 때는 본 폴더와 로컬 폴더를 모두 뜹니다. SQLite 파일은 같은 이름의 `-wal` 파일도 함께 뜹니다.
- 원본 프로필로 파이어폭스를 켜지 않습니다. 켜는 순간 세션·쿠키·양식 기록 파일이 바뀔 수 있습니다.

### Windows 버전에 따라 달라지는 점

아래 경로 예는 Forensics Wiki 에서 확인한 것입니다.

| Windows 판 | 본 폴더 경로 예 | 로컬 폴더 경로 예 |
|---|---|---|
| XP | `C:\Documents and Settings\%USERNAME%\Application Data\Mozilla\Firefox\Profiles\` | `C:\Documents and Settings\%USERNAME%\Local Settings\Application Data\Mozilla\Firefox\Profiles\` |
| Vista·7 | `C:\Users\%USERNAME%\AppData\Roaming\Mozilla\Firefox\Profiles\` | `C:\Users\%USERNAME%\AppData\Local\Mozilla\Firefox\Profiles\` |

- 그 뒤 Windows 판에서도 기본 위치는 `%APPDATA%`·`%LOCALAPPDATA%` 아래입니다.

Windows 판보다 파이어폭스 판에 따른 차이가 더 큽니다.

| 파이어폭스 판 | 바뀐 점 | 자세히 |
|---|---|---|
| 21 | 다운로드 기록이 `downloads.sqlite` 에서 `places.sqlite` 로 옮겨 갔습니다 | [places.sqlite](/02-artifacts/browsers/firefox/places-sqlite.md) |
| 32 | 디스크 캐시가 `Cache` 에서 `cache2` 로 바뀌었습니다 | [캐시 (cache2)](/02-artifacts/browsers/firefox/cache2.md) |
| 32 | 로그인 파일이 `signons.sqlite` 에서 `logins.json` 으로 바뀌었습니다 | [저장 비밀번호](/02-artifacts/browsers/firefox/logins-json-key4-db.md) |
| 58.0.2 | 키 파일이 `key3.db` 에서 `key4.db` 로 바뀌었습니다 | [저장 비밀번호](/02-artifacts/browsers/firefox/logins-json-key4-db.md) |
| 75.0·144.0 | `key4.db` 와 `logins.json` 의 암호 방식이 바뀌었습니다 | [저장 비밀번호](/02-artifacts/browsers/firefox/logins-json-key4-db.md) |
| 확인 못 함 | 쿠키 스키마 15 부터 만료 시각이 초에서 밀리초로 바뀌었습니다 | [쿠키 (cookies.sqlite)](/02-artifacts/browsers/firefox/cookies-sqlite.md) |
| 확인 못 함 | 세션 파일이 압축하지 않은 `.js`·`.bak` 에서 LZ4 압축 파일로 바뀌었습니다 | [세션 복원](/02-artifacts/browsers/firefox/sessionstore-jsonlz4.md) |

### 알려 주는 것

| 알 수 있는 것 | 파일 | 형식 | 자세히 |
|---|---|---|---|
| 프로필 목록과 기본 프로필 | `profiles.ini` | 텍스트 | [프로필 구조](/02-artifacts/browsers/firefox/profiles-ini-prefs-js.md) |
| 방문한 주소·방문 시각·방문 유형, 즐겨찾기, 다운로드 | `places.sqlite` | SQLite | [방문·다운로드·즐겨찾기](/02-artifacts/browsers/firefox/places-sqlite.md) |
| 사이트별 쿠키와 그 시각 | `cookies.sqlite` | SQLite | [쿠키](/02-artifacts/browsers/firefox/cookies-sqlite.md) |
| 받아 둔 웹 자원 | `cache2\` (로컬 폴더) | 캐시 전용 형식 | [캐시](/02-artifacts/browsers/firefox/cache2.md) |
| 사이트별로 저장한 로그인 | `logins.json`·`key4.db` | JSON·SQLite | [저장 비밀번호](/02-artifacts/browsers/firefox/logins-json-key4-db.md) |
| 열려 있던 창과 탭 | `sessionstore.jsonlz4`, `sessionstore-backups\` | LZ4 로 압축한 JSON | [세션 복원](/02-artifacts/browsers/firefox/sessionstore-jsonlz4.md) |
| 사이트가 브라우저에 넣어 둔 값 | `storage\` | 확인하지 못함 | [웹 저장소](/02-artifacts/browsers/firefox/storage.md) |
| 입력란에 친 값 | `formhistory.sqlite` | SQLite | [양식 기록](/02-artifacts/browsers/firefox/formhistory-sqlite.md) |
| 설치한 추가 기능 | `extensions.json` | JSON | [확장 프로그램](/02-artifacts/browsers/firefox/extensions-json.md) |

시각 형식도 먼저 알아 둡니다. 파이어폭스의 SQLite 파일 속 시각은 대부분 1970년 1월 1일 0시 (UTC) 부터 센 마이크로초입니다. 파이어폭스 소스는 이 단위를 PRTime 이라고 부릅니다. 예외도 있습니다. 쿠키의 만료 시각은 스키마 15 부터 밀리초이고, `extensions.json` 의 날짜도 밀리초입니다. 크롬 계열과 기준일이 다르므로 두 브라우저의 시각을 같은 식으로 바꾸지 않습니다. 바꾸는 법은 [시각 값 형식 (FILETIME·Unix·WebKit·DOS·OLE)](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

## 읽는 순서

1. [프로필 구조 (profiles.ini·prefs.js)](/02-artifacts/browsers/firefox/profiles-ini-prefs-js.md) — `profiles.ini` 로 프로필 폴더를 찾고, 본 폴더와 로컬 폴더를 가립니다. 모든 분석이 여기서 시작합니다.
2. [방문·다운로드·즐겨찾기 (places.sqlite)](/02-artifacts/browsers/firefox/places-sqlite.md) — 방문한 주소, 방문 시각, 방문 유형을 읽습니다. 즐겨찾기와 다운로드 기록도 같은 파일에서 다룹니다.
3. [쿠키 (cookies.sqlite)](/02-artifacts/browsers/firefox/cookies-sqlite.md) — 사이트별 쿠키의 만든 시각, 마지막으로 쓴 시각, 만료 시각을 읽습니다. 스키마 버전에 따라 만료 시각의 단위가 다릅니다.
4. [캐시 (cache2)](/02-artifacts/browsers/firefox/cache2.md) — 받아 둔 웹 자원과 항목 메타데이터를 읽습니다. 캐시는 로컬 폴더에 있습니다.
5. [저장 비밀번호 (logins.json·key4.db)](/02-artifacts/browsers/firefox/logins-json-key4-db.md) — 사이트별 저장 로그인과 그 값을 푸는 키를 읽습니다. 파이어폭스 판에 따라 파일과 암호 방식이 다릅니다.
6. [세션 복원 (sessionstore.jsonlz4)](/02-artifacts/browsers/firefox/sessionstore-jsonlz4.md) — 열려 있던 창과 탭을 여러 판의 세션 파일에서 꺼냅니다. 파일마다 쓰는 때가 다른 점을 다룹니다.
7. [웹 저장소 (storage 폴더)](/02-artifacts/browsers/firefox/storage.md) — 사이트가 브라우저에 넣어 둔 값을 찾습니다. 구조를 검체에서 직접 확인하는 순서를 다룹니다.
8. [양식 기록 (formhistory.sqlite)](/02-artifacts/browsers/firefox/formhistory-sqlite.md) — 입력란에 친 값, 쓴 횟수, 처음·마지막으로 쓴 시각을 읽습니다. 지운 항목의 흔적도 다룹니다.
9. [확장 프로그램 (extensions.json)](/02-artifacts/browsers/firefox/extensions-json.md) — 설치한 추가 기능, 켜짐·꺼짐 상태, 설치 시각을 읽습니다. 파이어폭스 밖에서 설치한 확장을 가리는 법도 다룹니다.

## 함께 볼 페이지

- [SQLite 데이터베이스](/01-foundations/database-log-formats/sqlite/index.md) — `places.sqlite`·`cookies.sqlite`·`formhistory.sqlite`·`key4.db` 의 저장 형식과 지운 행 복구입니다.
- [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) — 마이크로초·밀리초 시각을 UTC 로 바꾸는 법입니다.
- [크롬 계열 브라우저](/02-artifacts/browsers/chrome-edge-whale/index.md) · [인터넷 익스플로러·옛 엣지](/02-artifacts/browsers/ie-edgehtml/index.md) — 구조가 다른 브라우저입니다.
- [사용자 프로필 목록](/02-artifacts/system-account/profilelist.md) — 파이어폭스 프로필이 어느 Windows 계정에 속하는지 봅니다.
- [웹 사용 행위 재구성](/04-scenarios/activity/web-activity.md) — 여러 브라우저 기록을 한 타임라인으로 묶는 순서입니다.
- [시크릿 모드로 무엇을 했나](/04-scenarios/activity/private-browsing.md) — 사생활 보호 창을 쓴 흔적을 찾는 순서입니다.
- [섀도 복사본 활용](/03-techniques/analysis/volume-shadow-copy-analysis.md) · [삭제 데이터 복구](/03-techniques/analysis/data-recovery/index.md) — 기록을 지우기 전의 프로필 파일을 꺼냅니다.

## 참고 문헌

1. Mozilla, *Profile Management — Firefox Source Docs* (프로필 본 폴더·로컬 폴더와 기본 위치, profiles.ini). https://firefox-source-docs.mozilla.org/toolkit/profile/index.html
2. *Mozilla Firefox — Forensics Wiki* (Windows 판별 경로 예, 다운로드 기록 이동, cache2 도입, 시각 단위). https://forensics.wiki/mozilla_firefox/
3. Mozilla, *nsPlacesTables.h* (파이어폭스 소스, main 가지 — `moz_bookmarks_deleted` 표). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/components/places/nsPlacesTables.h
4. Mozilla, *nsINavHistoryService.idl* (파이어폭스 소스, main 가지 — PRTime 정의). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/components/places/nsINavHistoryService.idl
5. Mozilla, *CookiePersistentStorage.cpp* (파이어폭스 소스, main 가지 — 쿠키 만료 시각 단위 변경). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/netwerk/cookie/CookiePersistentStorage.cpp
6. lclevy, *firepwd — README* (판별 로그인·키 파일과 암호 방식). https://github.com/lclevy/firepwd
7. Mozilla, *SessionFile.sys.mjs* (파이어폭스 소스, main 가지 — 세션 파일과 압축). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/browser/components/sessionstore/SessionFile.sys.mjs
8. Mozilla, *FormHistory.sys.mjs* (파이어폭스 소스, main 가지 — `moz_deleted_formhistory` 표). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/components/satchel/FormHistory.sys.mjs
9. Mozilla, *XPIDatabase.sys.mjs* (파이어폭스 소스, main 가지 — `extensions.json` 날짜 단위). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/mozapps/extensions/internal/XPIDatabase.sys.mjs
