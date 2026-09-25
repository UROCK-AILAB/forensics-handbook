---
title: "사파리"
parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1140
has_children: true
has_toc: false
---

# 사파리 (Safari)

사파리는 방문 기록·다운로드·북마크·탭·쿠키·확장을 사용자 계정의 `~/Library/Safari/` 와 샌드박스 컨테이너 쪽 사파리 폴더에 나눠 남기고, 시각은 대부분 맥 절대 시각으로 적어서, 두 위치를 함께 모으고 시각 기준을 맞추면 이 계정의 웹 사용을 한 시간축에 놓을 수 있습니다.

## 왜 중요한가

사파리는 맥에 기본으로 들어 있는 브라우저라서, 다른 브라우저를 따로 설치하지 않은 계정이라면 웹 사용의 흔적은 대부분 사파리 파일에 있습니다. 파일마다 알려 주는 것이 달라서 방문 기록은 어느 주소를 언제 열었는지, 다운로드 목록은 무엇을 어디에 받았는지, 탭과 세션 파일은 무엇이 열려 있었고 언제 닫혔는지를 말해 주고, 한 파일이 비어 있으면 다른 파일로 빈자리를 메웁니다.

사용자 데이터 폴더는 두 곳입니다. 옛 위치 `~/Library/Safari/` 와 샌드박스 컨테이너 (Sandbox Container) 위치 `~/Library/Containers/com.apple.Safari/Data/Library/Safari` 가 있고, 뒤쪽은 Safari 15 이상에서 쓰는 경로입니다 [1]. 다만 Safari 15 부터 모든 파일이 컨테이너로 옮겨 갔다고 볼 공개 자료는 없고, ForensicArtifacts 정의는 `History.db` 와 `Downloads.plist` 를 `~/Library/Safari/` 에만 적습니다 [2]. 파일이 실제로 어느 쪽에 있는지는 파일마다 달라서, 수집할 때는 두 위치를 모두 가져옵니다.

사파리의 DB 와 plist 시각은 대부분 맥 절대 시각 (Mac Absolute Time), 곧 2001-01-01 00:00:00 UTC 부터 센 초입니다 [1][3]. 유닉스 시각과 기준이 달라서 다른 아티팩트와 나란히 놓기 전에 먼저 바꿔야 하고, 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에서 다룹니다.

## 한눈에 보기

| 기록 | 위치 | 버전 | 알려 주는 것 |
|---|---|---|---|
| 방문 기록 | `~/Library/Safari/History.db` [2], 프로필마다 컨테이너 쪽 사파리 폴더의 `Profiles/{UUID}/History.db` [1] | Mavericks 까지는 `History.plist` [1] | 어느 주소를 언제 방문했는지, 리디렉트 연결 |
| 다운로드 목록 | `~/Library/Safari/Downloads.plist` [2] | 버전별 차이 자료 없음 | 받은 주소, 저장 경로, 시작·끝 시각 |
| 북마크·읽기 목록·자주 방문 사이트 | 사파리 폴더의 `Bookmarks.plist`, `TopSites.plist` [1] | 버전별 차이 자료 없음 | 저장해 둔 주소, 읽기 목록에 넣은 때 |
| 탭과 세션 | `LastSession.plist`, `RecentlyClosedTabs.plist`, `BrowserState.db`, `SafariTabs.db`, `CloudTabs.db` 등 [1] | `SafariTabs.db` 는 Safari 17 프로필과 함께 쓰임 [1] | 열려 있던 탭, 닫은 탭과 창, 다른 기기의 iCloud 탭 |
| 캐시와 웹 데이터 | `~/Library/Caches/com.apple.Safari/Cache.db`, `~/Library/Cookies/Cookies.binarycookies` 와 각 컨테이너 쪽 경로 [2] | 버전별 차이 자료 없음 | 받아 둔 웹 자원, 쿠키 |
| 확장 | `Extensions`·`AppExtensions`·`WebExtensions` 폴더의 `Extensions.plist` [1][2] | Safari 14 에서 형식 바뀜 [1] | 설치한 확장과 켜짐 여부 |
| 설정 | `~/Library/Preferences/com.apple.safari.plist`, `~/Library/Containers/com.apple.Safari/Data/Library/Preferences/com.apple.Safari.plist` [1] | 키마다 쓰인 버전이 다름 [1] | 최근 검색, 다운로드 폴더, 홈페이지 |
| 그 밖의 DB | `~/Library/Safari/` 의 `AutoFillCorrections.db`, `CloudAutoFillCorrections.db`, `PerSitePreferences.db`, `Favicon Cache/favicons.db`, `Touch Icons Cache/TouchIconCacheSettings.db`, 각각 `-wal` 동반 [2] | 버전별 차이 자료 없음 | 수집 대상 파일. 표·칸 구성은 공개 자료 없음 |

버전 흐름은 아래와 같습니다 [1]. Apple 이 밝힌 연표가 아니라 분석 도구 mac_apt 가 버전마다 다르게 읽는 지점을 모은 것입니다.

| 버전 | 바뀐 점 | 자세히 |
|---|---|---|
| OS X Mavericks 까지 | 방문 기록이 `History.plist` | [방문 기록](history.md) |
| OS X Yosemite 부터 | 방문 기록이 `History.db` | [방문 기록](history.md) |
| Safari 14 | 확장 plist 형식 변경 | [확장](extensions.md) |
| Safari 15 | 컨테이너 경로 사용 | 이 페이지 위 |
| Safari 17 | 프로필(여러 프로필) 도입, 프로필마다 방문 기록 | [방문 기록](history.md), [탭과 세션](tabs-sessions.md) |

### 설정 파일에서 읽는 키

설정 파일은 하위 페이지 어디에도 따로 속하지 않아서 이 페이지에 모아 둡니다. 설정 파일에는 아래 키가 있고 [1], 뜻 칸의 설명 가운데 출처에 없는 것은 키 이름으로 짐작한 것입니다.

| 키 | 쓰인 버전 | 뜻 |
|---|---|---|
| `RecentSearchStrings` | Mavericks | 최근 검색어 |
| `RecentWebSearches` | Yosemite 이후 | 최근 검색. 안에 `SearchString`, `Date` |
| `FrequentlyVisitedSitesCache` | El Capitan 이후 | 자주 방문한 사이트. 안에 `URL`, `Title` |
| `DownloadsPath` | 표시 없음 | 받은 파일을 저장할 기본 폴더([다운로드](downloads.md)) |
| `HomePage` | 표시 없음 | 홈페이지 주소(이름으로 본 뜻) |
| `LastExtensionSelectedInPreferences` | 표시 없음 | 설정 창에서 마지막으로 고른 확장([확장](extensions.md)) |
| `NSNavLastRootDirectory` | 표시 없음 | 이름으로 보면 파일 열기·저장 창이 마지막으로 연 폴더 |
| `SuccessfulLaunchTimestamp` | 표시 없음 | 이름으로 보면 사파리가 마지막으로 정상 실행된 시각 |

어느 키가 두 설정 파일 가운데 어느 쪽에 남는지는 공개 자료가 없어서 두 파일을 모두 읽습니다. plist 를 읽는 법은 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

## 읽는 순서

1. [방문 기록 (History.db)](history.md) — `history_items`·`history_visits` 두 표를 잇는 법, 리디렉트 연결, 기록 지우기가 무엇을 지우는지, iCloud 로 묶인 기기와의 관계를 다룹니다.
2. [다운로드 (Downloads.plist)](downloads.md) — `DownloadHistory` 항목의 키와 두 시각, 목록과 받은 파일이 따로 움직이는 점을 다룹니다.
3. [북마크와 읽기 목록 (Bookmarks·Reading List)](bookmarks.md) — `Bookmarks.plist` 의 폴더·항목 구조, 읽기 목록에 넣은 시각, 자주 방문 사이트 목록, 북마크의 iCloud 보호 수준을 다룹니다.
4. [탭과 세션 (Tabs·Sessions)](tabs-sessions.md) — 마지막 세션, 최근 닫은 탭, 탭별 뒤로/앞으로 목록, Safari 17 프로필 목록을 찾는 법, 다른 기기의 iCloud 탭, 탭 스냅샷을 다룹니다.
5. [캐시와 웹 데이터 (Cache·WebKit)](cache-webkit.md) — 캐시 DB 위치, `Cookies.binarycookies` 를 헥스로 읽는 법, 웹 아이콘과 사이트별 설정 파일을 다룹니다.
6. [확장 (Safari Extensions)](extensions.md) — 옛 `.safariextz` 목록과 Safari 14 이후 앱 확장·웹 확장 목록, 확장을 담은 앱과 함께 보는 법을 다룹니다.
7. [개인 정보 보호 브라우징 (Private Browsing)](private-browsing.md) — Apple 이 밝힌 "저장하지 않는 것" 과 그래도 남는 실마리를 다룹니다.

## 함께 볼 페이지

- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) — `History.db` 등 DB 파일과 `-wal` 을 읽는 법
- [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md) — 다운로드·북마크·세션·설정 파일의 형식
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) — 맥 절대 시각 바꾸기
- [크롬·엣지·웨일 (Chromium 계열)](../chromium/index.md), [파이어폭스 (Firefox)](../firefox.md) — 같은 계정에서 다른 브라우저를 썼을 때
- [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md) — 받은 파일 쪽에 남는 출처
- [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md) — 사파리 기록을 다른 흔적과 묶어 따지는 순서
- [개인 정보 보호 브라우징으로 무엇을 했나 (Private Browsing)](../../../04-scenarios/activity/private-browsing.md) — 기록이 비어 있을 때 따지는 순서

## 참고 문헌

1. mac_apt Safari 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/safari.py
2. ForensicArtifacts 정의 파일 webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
3. plaso Safari History.db SQLite 플러그인 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/sqlite_plugins/safari.py
