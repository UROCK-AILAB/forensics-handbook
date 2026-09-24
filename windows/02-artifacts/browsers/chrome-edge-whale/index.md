# 크롬 계열 브라우저 (Chrome·Edge·Whale 등)

## 한 줄 요약

크롬 계열 브라우저는 크로미움 (Chromium) 소스를 바탕으로 만든 브라우저입니다. Chrome, 크로미움 판 Edge, 네이버 Whale 이 여기에 듭니다. 이 브라우저들은 사용자마다 `User Data` 폴더를 두고, 그 아래에 같은 이름의 파일로 방문 기록·다운로드·쿠키·캐시·저장 비밀번호를 남깁니다.

## 왜 중요한가

- 웹에서 한 일은 대부분 브라우저 안에서 일어납니다. 방문한 주소, 내려받은 파일, 입력한 검색어가 프로필 폴더 하나에 모입니다.
- 계열 브라우저끼리는 `User Data` 폴더 위치만 다릅니다. 그 아래 파일 이름과 형식은 거의 같습니다. 그래서 Chrome 에서 익힌 읽는 법을 Edge·Whale 에도 그대로 씁니다.
- 파일 대부분은 SQLite·JSON·LevelDB 형식입니다. 브라우저를 띄우지 않고 공개 도구로 읽을 수 있습니다.
- `User Data` 폴더는 Windows 사용자 폴더 아래 있습니다. 그래서 어느 Windows 계정에서 남은 기록인지 알 수 있습니다.
- 한 계정 안에도 브라우저 프로필 (Profile) 이 여러 개일 수 있습니다. 프로필마다 폴더가 따로 있고, 기록도 따로 쌓입니다.
- 다운로드 기록에는 받은 주소와 저장 경로가 남습니다. 이 기록을 [다운로드 출처 표시 (Zone.Identifier)](../../filesystem/zone-identifier.md) 와 맞춰 보면 파일이 어디서 왔는지 좁힐 수 있습니다.

증명하지 못하는 것도 분명합니다.

- 기록은 Windows 계정과 브라우저 프로필 단위로 남습니다. 그 시각에 누가 키보드 앞에 있었는지는 남지 않습니다.
- 방문 기록은 페이지를 불러왔다는 기록입니다. 사용자가 그 페이지를 읽었는지, 거기서 무엇을 했는지는 방문 기록만으로 알 수 없습니다.
- 시크릿 모드 (Incognito, Edge 에서는 InPrivate) 창에서 연 페이지는 방문 기록 파일에 남지 않습니다. 이때 남는 흔적은 [시크릿 모드로 무엇을 했나](../../../04-scenarios/activity/private-browsing.md) 에서 다룹니다.
- 사용자는 브라우저 메뉴로 인터넷 사용 기록을 지울 수 있습니다. 그래서 기록이 없다는 것만으로 방문하지 않았다고 단정하지 않습니다. 지운 행은 SQLite 파일의 빈 공간에 남아 있을 수 있습니다.
- 즐겨찾기·저장 비밀번호처럼 동기화 (Sync) 하는 항목은 다른 기기에서 넣은 값일 수 있습니다. 이 PC 에서 입력했다고 바로 단정하지 않습니다.

## 한눈에 보기

> 그림 자리: `User Data` 폴더 아래의 `Local State` 와 프로필 폴더(`Default`·`Profile 1`…), 프로필 폴더 안의 주요 파일(History·Network\Cookies·Cache·Login Data·Sessions·Local Storage·IndexedDB·Web Data·Bookmarks·Extensions)을 나무 모양으로 보여 주는 그림

### 위치

아래는 기본 위치입니다. `%LOCALAPPDATA%` 는 보통 `C:\Users\<사용자>\AppData\Local` 입니다.

| 브라우저 | 기본 `User Data` 폴더 |
|---|---|
| Chrome | `%LOCALAPPDATA%\Google\Chrome\User Data` |
| Chrome Beta · Dev · Canary | `%LOCALAPPDATA%\Google\Chrome Beta\User Data` · `Chrome Dev\User Data` · `Chrome SxS\User Data` |
| Chromium | `%LOCALAPPDATA%\Chromium\User Data` |
| Edge (크로미움 판) | `%LOCALAPPDATA%\Microsoft\Edge\User Data` |
| Whale | `%LOCALAPPDATA%\Naver\Naver Whale\User Data` |

| 항목 | 내용 |
|---|---|
| 프로필 폴더 | `User Data` 아래 `Default` 가 첫 프로필입니다. 프로필을 더 만들면 `Profile 1`, `Profile 2` 같은 폴더가 생깁니다. |
| `Local State` | `User Data` 바로 아래 있는 JSON 파일입니다. 모든 프로필이 이 파일 하나를 함께 씁니다. 프로필 목록과 쿠키·비밀번호를 푸는 키가 여기 있습니다. |
| 캐시 | Windows 에서는 캐시도 프로필 폴더 안에 있습니다. |
| 위치를 바꾼 경우 | 실행 인자 `--user-data-dir` 로 다른 폴더를 쓸 수 있습니다. Chrome·Edge 는 `UserDataDir` 정책으로도 바꿀 수 있습니다. 기본 위치가 비어 있으면 바로가기의 실행 인자와 정책 값을 확인합니다. |
| 사용자 정보 | 폴더 경로에 Windows 사용자 이름이 드러납니다. 브라우저에 로그인한 계정은 `Local State` 의 프로필 정보에 남을 수 있습니다. |

Brave·Opera·Vivaldi 같은 다른 계열 브라우저는 폴더 위치와 구성이 조금씩 다릅니다. 어느 브라우저의 폴더인지 가리는 법은 [프로필 폴더와 계열 브라우저 구분](../../../01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md) 에서 다룹니다.

### Windows 버전에 따라 달라지는 점

| Windows 버전 | `User Data` 폴더가 있는 곳 | 브라우저 지원 |
|---|---|---|
| XP | `C:\Documents and Settings\<사용자>\Local Settings\Application Data\` 아래 | 옛 판 Chrome 만 돌아갑니다. |
| Vista | `C:\Users\<사용자>\AppData\Local\` 아래 | 옛 판 Chrome 만 돌아갑니다. |
| 7 · 8 · 8.1 | Vista 와 같음 | Chrome 과 Edge 모두 109 판이 마지막 지원 판입니다. Chrome 109 는 2023년 1월 10일에 나왔습니다. |
| 10 · 11 | Vista 와 같음 | 최신 판이 돌아갑니다. |

Windows 버전보다 브라우저 판에 따른 차이가 더 큽니다. 아래 표는 옛 판과 요즘 판의 차이입니다. 바뀐 판 번호는 각 하위 페이지에서 다룹니다.

| 항목 | 옛 판 | 요즘 판 |
|---|---|---|
| 쿠키 파일 | 프로필 폴더 바로 아래 `Cookies` | `Network\Cookies` |
| 캐시 폴더 | `Cache` 바로 아래 캐시 파일 | `Cache\Cache_Data` 아래 캐시 파일 |
| 세션 파일 | 프로필 폴더 바로 아래 `Current Session`·`Last Session`·`Current Tabs`·`Last Tabs` | `Sessions` 폴더 아래 `Session_<숫자>`·`Tabs_<숫자>` |
| 쿠키·비밀번호 암호화 | 값마다 DPAPI 로 암호화 | `Local State` 에 든 키로 값을 암호화하고, 그 키를 DPAPI 로 보호합니다. Chrome 127 부터는 쿠키에 앱 바운드 암호화 (App-Bound Encryption) 를 더합니다. |

브라우저를 업데이트하면 옛 자리의 파일이 남아 있기도 합니다. 그래서 옛 자리와 새 자리를 둘 다 봅니다. 암호화 구조는 [쿠키·비밀번호 암호화 (DPAPI·App-Bound Encryption)](../../../01-foundations/app-mail-data/chromium-electron-webview2/dpapi-app-bound-encryption.md) 에서 다룹니다.

### 알려 주는 것

| 알 수 있는 것 | 어디에 남나 (프로필 폴더 기준) | 형식 | 자세히 |
|---|---|---|---|
| 방문한 주소·방문 시각·방문 횟수 | `History` | SQLite | [방문·다운로드 기록](history.md) |
| 내려받은 파일·받은 주소·저장 경로 | `History` | SQLite | [방문·다운로드 기록](history.md) |
| 사이트별 쿠키와 그 시각 | `Network\Cookies` (옛 판은 `Cookies`) | SQLite, 값은 암호화 | [쿠키](cookies.md) |
| 받아 둔 페이지·이미지 사본 | `Cache\Cache_Data` (옛 판은 `Cache`) | 캐시 전용 형식 | [캐시](cache.md) |
| 사이트별로 저장한 아이디·비밀번호 | `Login Data` | SQLite, 비밀번호는 암호화 | [저장 비밀번호](login-data.md) |
| 닫을 때 열려 있던 탭·창 | `Sessions\` (옛 판은 `Current Session` 등) | SNSS | [세션·탭 복원](sessions.md) |
| 사이트가 브라우저에 저장한 값 | `Local Storage\leveldb\`, `IndexedDB\` | LevelDB | [웹 저장소](local-storage-indexeddb.md) |
| 입력란에 넣은 값·주소·카드 정보 | `Web Data` | SQLite | [자동완성·폼 기록](web-data-autofill.md) |
| 즐겨찾기와 추가한 시각 | `Bookmarks` | JSON | [즐겨찾기](bookmarks.md) |
| 설치한 확장 프로그램 | `Extensions\`, `Preferences`·`Secure Preferences` | 폴더·JSON | [확장 프로그램](extensions.md) |
| 프로필 목록·암호화 키 | `User Data\Local State` | JSON | [프로필 폴더와 계열 브라우저 구분](../../../01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md) |

시각 형식도 먼저 알아 둡니다. SQLite 파일 안의 시각 칸은 대부분 1601년 1월 1일 0시 (UTC) 부터 센 마이크로초입니다. 이 형식을 WebKit 시각 (WebKit Time) 이라고 부릅니다. Windows FILETIME 과 기준일은 같지만 단위가 다릅니다. FILETIME 은 100나노초 단위입니다. 다른 형식을 쓰는 칸도 있으므로 하위 페이지에서 칸마다 밝힙니다. 바꾸는 법은 [시각 값 형식 (FILETIME·Unix·WebKit·DOS·OLE)](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

## 읽는 순서

1. [방문·다운로드 기록 (History)](history.md) — 방문한 주소, 방문 시각, 내려받은 파일을 담은 SQLite DB 를 읽습니다. 방문이 어떻게 이어졌는지와 입력한 검색어도 다룹니다.
2. [쿠키 (Cookies)](cookies.md) — 사이트별 쿠키의 만든 시각, 마지막 접근 시각, 만료 시각을 읽습니다. 값은 암호화돼 있어서 풀려면 따로 재료가 필요합니다.
3. [캐시 (Cache)](cache.md) — 브라우저가 받아 둔 페이지 조각과 이미지를 꺼냅니다. 방문 기록을 지운 뒤에도 캐시에 흔적이 남는 경우를 다룹니다.
4. [저장 비밀번호 (Login Data)](login-data.md) — 사이트별로 저장한 아이디와 암호화된 비밀번호를 읽습니다. 저장한 시각과 마지막으로 쓴 시각도 함께 봅니다.
5. [세션·탭 복원 (Sessions)](sessions.md) — 브라우저를 닫을 때 열려 있던 탭과 창을 읽습니다. 탭마다 남은 뒤로 가기 목록도 다룹니다.
6. [웹 저장소 (Local Storage·IndexedDB)](local-storage-indexeddb.md) — 사이트가 브라우저에 저장한 값을 LevelDB 에서 꺼냅니다. 웹메일이나 웹 메신저의 흔적이 여기 남기도 합니다.
7. [자동완성·폼 기록 (Web Data·Autofill)](web-data-autofill.md) — 입력란에 넣은 값과 저장한 주소·카드 정보를 읽습니다. 입력한 횟수와 시각도 함께 봅니다.
8. [즐겨찾기 (Bookmarks)](bookmarks.md) — JSON 파일에서 즐겨찾기와 추가한 시각을 읽습니다. 백업 파일과 비교해 지운 즐겨찾기를 찾는 법도 다룹니다.
9. [확장 프로그램 (Extensions)](extensions.md) — 설치한 확장 프로그램, 요청한 권한, 설치 시각을 읽습니다. 의심스러운 확장을 가려내는 법도 다룹니다.

## 함께 볼 페이지

- [크롬 계열 앱 공통 구조 (Chromium·Electron·WebView2)](../../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) — 브라우저 밖에서 같은 구조를 쓰는 앱까지 묶어 설명합니다.
- [Electron·WebView2 앱 데이터 위치 (Teams·Discord·Slack 등)](../../../01-foundations/app-mail-data/chromium-electron-webview2/teams-discord-slack.md) — 메신저·협업 앱 안에 숨은 크롬 계열 프로필을 찾습니다.
- [캐시 형식 (Blockfile·Simple Cache)](../../../01-foundations/app-mail-data/chromium-electron-webview2/blockfile-simple-cache.md) — 캐시 파일의 저장 형식입니다.
- [DPAPI 구조 (Data Protection API)](../../../01-foundations/protection/data-protection-api/index.md) — 쿠키·비밀번호를 풀 때 필요한 Windows 보호 구조입니다.
- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/database-log-formats/sqlite/index.md) · [WAL과 롤백 저널](../../../01-foundations/database-log-formats/sqlite/wal-journal-shm.md) · [파일 안에 남은 지운 레코드 (Freelist·Freeblock)](../../../01-foundations/database-log-formats/sqlite/freelist-freeblock.md) — History·Cookies·Login Data·Web Data 의 저장 형식과 지운 행 복구입니다.
- [LevelDB 저장소 (LevelDB)](../../../01-foundations/database-log-formats/leveldb.md) — Local Storage·IndexedDB 의 저장 형식입니다.
- [파이어폭스 (Firefox)](../firefox/index.md) · [인터넷 익스플로러·옛 엣지 (IE·EdgeHTML)](../ie-edgehtml/index.md) — 구조가 다른 브라우저입니다. 옛 EdgeHTML 엣지는 이름만 같고 기록 방식이 전혀 다릅니다.
- [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md) — 여러 브라우저 기록을 한 타임라인으로 묶는 순서입니다.
- [웹메일·웹하드로 올렸나 (Web Upload)](../../../04-scenarios/exfiltration/data-exfiltration/web-upload.md) — 브라우저로 파일을 밖에 올린 흔적을 찾는 순서입니다.
- [섀도 복사본 활용 (Volume Shadow Copy Analysis)](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 기록을 지우기 전의 프로필 파일을 꺼냅니다.

## 참고 문헌

- The Chromium Projects, "User Data Directory" (docs/user_data_dir.md) — https://chromium.googlesource.com/chromium/src/+/HEAD/docs/user_data_dir.md
- Microsoft Learn, "Create Microsoft Edge user data directory variables" — https://learn.microsoft.com/en-us/deployedge/edge-learnmore-create-user-directory-vars
- Microsoft Learn, "Microsoft Edge Supported Operating Systems" — https://learn.microsoft.com/en-us/deployedge/microsoft-edge-supported-operating-systems
- Google Chrome Enterprise 도움말, Chrome 브라우저 시스템 요구 사항 — https://support.google.com/chrome/a/answer/7100626
- Google Security Blog, "Improving the security of Chrome cookies on Windows" (2024) — https://security.googleblog.com/2024/07/improving-security-of-chrome-cookies-on.html
- Forensics Wiki, "Google Chrome" — https://forensics.wiki/google_chrome/
