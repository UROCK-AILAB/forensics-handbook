---
title: "Electron·웹뷰 앱의 저장 구조"
parent: "기반 · 저장 구조"
nav_order: 10
---

# Electron·웹뷰 앱의 저장 구조 (Electron·WebView2·WKWebView)

> 확인 날짜: 2026-09. Electron·WebView2 공식 문서는 2026-09-25 에 열어 읽었고, WebView2 문서의 갱신 날짜는 2026-09-02 입니다. 기기 관찰은 Windows 11(빌드 26200) 한 대에서 Claude 데스크톱(스토어 앱) 폴더를 읽기 전용으로 열어 폴더·파일 이름, JSON 키 이름, 데이터베이스 표·칸 이름만 본 결과이고 값과 앱 버전은 적어 두지 않았습니다. 관찰로 확인한 내용에는 "(확인 범위: Windows 11, 2026-09)" 를 붙였습니다.

## 한 줄 요약

Electron 앱과 WebView2 를 쓰는 앱은 웹 페이지를 앱 창 안에 띄우는 방식이라서 크롬 계열 브라우저와 같은 저장소(쿠키 DB, Local Storage, IndexedDB, 캐시)를 앱 전용 폴더에 따로 만들고, 앱이 직접 쓰는 설정은 그 옆에 JSON 파일로 둡니다.

## 이 형식을 쓰는 아티팩트

AI 채팅 서비스의 데스크톱 앱 가운데 이 쪽에서 폴더를 직접 본 것은 Claude 데스크톱(스토어 앱)이고, 폴더 구성이 Electron 앱의 사용자 데이터 폴더와 같은 모양이었습니다(확인 범위: Windows 11, 2026-09). 다른 AI 데스크톱 앱이 Electron·WebView2·WKWebView 가운데 무엇으로 만들어졌는지는 이 쪽을 쓰면서 확인하지 못했고, [ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md), [Microsoft Copilot](../../02-artifacts/chat-services/copilot/index.md) 같은 서비스별 쪽에서 앱마다 확인합니다.

크롬 계열 저장소 하나하나의 파일 형식은 다른 판에서 이미 다룹니다. 폴더 공통 구조는 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html), LevelDB 는 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html), SQLite 는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html) 를 봅니다. 이 쪽은 AI 앱 폴더에서 무엇을 먼저 찾고 어떻게 나눠 읽는지에 집중합니다.

## 구조

### Electron 의 경로 이름

Electron 은 앱이 쓰는 폴더를 이름으로 나눠 부르고, 앱은 `app.getPath` 로 그 위치를 받습니다 [1]. 기준이 되는 `appData` 는 OS 마다 기본 위치가 다르고, 앱 설정 파일을 두는 `userData` 는 기본적으로 `appData` 아래에 앱 이름을 붙인 폴더입니다 [1].

| 이름 | 무엇을 두나 | Windows | macOS | Linux |
|---|---|---|---|---|
| `appData` | 사용자별 앱 데이터의 기준 폴더 | `%APPDATA%` | `~/Library/Application Support` | `$XDG_CONFIG_HOME` 또는 `~/.config` |
| `userData` | 앱 설정 파일 | `appData` 아래 앱 이름 폴더 | 같음 | 같음 |
| `sessionData` | 세션이 만드는 데이터: localStorage, 쿠키, 디스크 캐시, 내려받은 사전, 네트워크 상태, 개발자 도구 파일, 컴파일된 GPU 셰이더 | 기본은 `userData` | 같음 | 같음 |
| `logs` | 앱 로그 폴더 | `userData` 안(앱이 `setAppLogsPath()` 를 경로 없이 부른 경우) | `~/Library/Logs/<앱 이름>`(같은 조건) | `userData` 안(같은 조건) |
| `crashDumps`, `temp` | 충돌 덤프, 임시 파일 | 확인 못 함 | 확인 못 함 | 확인 못 함 |

`sessionData` 는 따로 정하지 않으면 `userData` 를 가리키고, 문서는 브라우저 저장소를 쓰지 않는 앱이라면 `sessionData` 를 다른 곳으로 옮기라고 권합니다 [1]. 그래서 쿠키·캐시 같은 크롬 계열 저장소는 보통 `userData` 폴더 안에서 찾지만, 앱이 위치를 바꿨을 수 있어서 기본 위치에 없으면 다른 곳도 찾아봅니다. 문서는 또 일부 환경이 `userData` 폴더를 클라우드에 백업한다며 이 폴더에 큰 파일을 쓰지 말라고 적고 있습니다 [1].

### AI 앱 폴더에서 본 크롬 계열 항목

Claude 데스크톱 데이터 폴더(스토어 앱은 패키지 폴더 아래 `LocalCache\Roaming\Claude\`)에서 본 항목을 크롬 계열 저장소와 앱 자체 파일로 나누면 아래와 같습니다(확인 범위: Windows 11, 2026-09). "담기는 것" 칸은 Electron 문서의 `sessionData` 설명 [1] 과 폴더 이름으로 맞춘 것이고, 파일 내용은 읽지 않았습니다.

| 항목 | 모양 | 담기는 것 |
|---|---|---|
| `Network\Cookies`, `Cookies-journal` | SQLite | 쿠키 |
| `Network\Network Persistent State`, `TransportSecurity`, `NetworkDataMigrated` | 파일 | 네트워크 상태 |
| `Local Storage\leveldb\` | LevelDB(`.ldb`, `.log`, `CURRENT`, `LOCK`, `LOG`, `LOG.old`) | localStorage |
| `IndexedDB\` 아래 이름별 폴더 | LevelDB(`.ldb`, `.log`, `CURRENT`, `LOCK`, `LOG`) | IndexedDB |
| `File System\Origins\` | LevelDB(`CURRENT`, `LOCK`, `LOG`, `LOG.old`, `.log`) | 파일 시스템 API 데이터 |
| `Cache\` | `index`, `journal.baj`, `snapshot.baf` 와 캐시 파일 | 디스크 캐시 |
| `Code Cache\` | `index-dir\the-real-index` 와 캐시 파일 | 스크립트 코드 캐시 |
| `GPUCache\`, `DawnGraphiteCache\`, `DawnWebGPUCache\` | 캐시 파일 | GPU 관련 캐시 |
| `Dictionaries\` | `.bdic` 파일 | 내려받은 맞춤법 사전 |
| `Crashpad\` | `metadata`, `settings.dat` | 충돌 보고 설정 |
| `Local State`, `DIPS`, `DIPS-wal`, `InterestGroups` | 파일 | 크롬 계열 공통 파일(각 형식은 다른 판 참고) |
| `Partitions\` 아래 이름별 폴더 | 위 항목을 파티션마다 따로 | 앱이 나눈 세션별 저장소 |

`Partitions\` 아래에는 `cowork-file-preview`, `launch-preview-static` 같은 이름의 폴더가 있었고, 폴더마다 `Network\Cookies` 가 따로 있었습니다(확인 범위: Windows 11, 2026-09). 앱이 세션(파티션)을 나누면 쿠키 DB 도 파티션마다 따로 생겨서, 쿠키를 찾을 때는 기본 `Network\Cookies` 한 곳만 보지 말고 `Partitions\` 아래를 모두 봅니다.

### 쿠키 DB 의 표와 칸

파티션 쪽 쿠키 DB 를 열어 보니 `cookies` 표와 `meta` 표가 있었습니다(확인 범위: Windows 11, 2026-09). `cookies` 표의 칸은 `creation_utc`, `host_key`, `top_frame_site_key`, `name`, `value`, `encrypted_value`, `path`, `expires_utc`, `is_secure`, `is_httponly`, `last_access_utc`, `has_expires`, `is_persistent`, `priority`, `samesite`, `source_scheme`, `source_port`, `last_update_utc`, `source_type`, `has_cross_site_ancestor` 이고, `meta` 표의 칸은 `key`, `value` 입니다. 값이 평문 `value` 와 암호화된 `encrypted_value` 두 칸으로 나뉘는 구성과 시각 칸의 해석은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html) 쪽을 따릅니다. 로그인 세션의 흔적으로서 쿠키가 무엇을 뜻하는지는 [API 키와 토큰이 남는 곳](api-keys-tokens.md) 에서 다룹니다.

### 앱 자체 JSON 파일

같은 폴더에는 크롬 계열 저장소와 별개로 앱이 직접 쓰는 JSON 파일이 있었습니다. 이름은 `claude_desktop_config.json`, `config.json`, `window-state.json`, `bridge-state.json`, `buddy-tokens.json`, `plan-usage-history.json`, `git-worktrees.json`, `mcp-user-tool-toggles.json`, `extensions-blocklist.json`, `cowork-enabled-cli-ops.json`, `ant-device-registry.json` 입니다(확인 범위: Windows 11, 2026-09). 파일 이름과 키 구성은 앱 버전마다 바뀔 수 있어서 검체의 앱 버전과 함께 적습니다.

조사에 먼저 쓰이는 키는 아래와 같습니다(확인 범위: Windows 11, 2026-09). 키의 뜻을 설명한 공식 문서는 찾지 못했고 "짐작" 칸은 이름으로 짐작한 것입니다.

| 파일 | 키 | 값 종류 | 짐작 |
|---|---|---|---|
| `config.json` | `first_launch_at` | 정수 | 처음 실행한 시점 |
| `config.json` | `version_first_launch.version`, `version_first_launch.at` | 문자열, 정수 | 처음 실행한 앱 버전과 그 시점 |
| `config.json` | `updaterLastSeenVersion` | 문자열 | 업데이트 기능이 마지막으로 본 버전 |
| `config.json` | `lastKnownAccountUuid` | 문자열 | 마지막으로 로그인한 계정 식별자 |
| `config.json` | `locale`, `userThemeMode` | 문자열 | 언어, 화면 테마 |
| `window-state.json` | `x`, `y`, `width`, `height`, `isMaximized`, `isFullScreen`, `displayBounds` | 정수, 참거짓 | 창 위치와 크기, 화면 범위 |

`first_launch_at` 같은 정수 시각 칸이 초 단위인지 밀리초 단위인지는 값을 읽지 않아 확인하지 못했습니다. 검체에서는 값의 자릿수를 보고 단위를 가린 뒤 다른 기록과 맞춰 봅니다.

### Electron safeStorage — 문자열 암호화

Electron 에는 앱이 문자열을 OS 의 보호 기능으로 암호화해 저장하는 `safeStorage` 가 있고, OS 마다 쓰는 보호 기능과 막아 주는 범위가 다릅니다 [2].

| OS | 쓰는 보호 기능 | 막아 주는 범위 |
|---|---|---|
| Windows | DPAPI | 같은 로그온 자격 증명의 사용자만 풀 수 있고, 다른 사용자로부터는 막지만 같은 사용자 공간의 다른 앱으로부터는 막지 못함 |
| macOS | 키체인에 암호 키 보관 | 다른 사용자와 같은 사용자 공간의 다른 앱으로부터 막음 |
| Linux | kwallet(4·5·6) 또는 gnome-libsecret | 비밀 저장소가 없으면 코드에 박힌 평문 암호로 암호화 |

Linux 에서 앱이 어느 저장소를 골랐는지는 `getSelectedStorageBackend()` 가 `basic_text`, `gnome_libsecret`, `kwallet`, `kwallet5`, `kwallet6`, `unknown` 가운데 하나로 알려 줍니다 [2]. 어떤 AI 앱이 `safeStorage` 를 쓰는지, `Local State` 안에 어떤 키가 있는지는 이 쪽을 쓰면서 확인하지 못했습니다. 보호 기능 자체의 구조는 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html) 와 [키체인 (macOS)](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html) 를 봅니다.

### WebView2 사용자 데이터 폴더

WebView2 는 Windows 앱 안에 웹 페이지를 띄우는 부품이고, 쿠키·권한·캐시된 자원 같은 브라우저 데이터를 사용자 데이터 폴더 (User Data Folder, UDF) 에 둡니다 [3]. 브라우저 데이터는 UDF 의 하위 폴더에 들어가는데 [3], 하위 폴더 이름은 문서에 없어서 확인하지 못했습니다. 한 UDF 안에 프로필을 여러 개 둘 수 있고 프로필마다 전용 폴더가 생깁니다 [3].

UDF 의 기본 위치는 앱을 만든 방식에 따라 다릅니다 [3].

| 앱 종류 | 기본 UDF 위치 |
|---|---|
| Win32, .NET(WPF·WinForms) | 실행 파일 옆 `<실행 파일 이름>.exe.WebView2\` (문서 예: `D:\WebView2App\WebView2.exe.WebView2\`) |
| WinUI 2(UWP), WinUI 3(패키지 앱) | 패키지 폴더의 `ApplicationData\LocalFolder` 아래 |

문서 예제는 사용자가 정한 위치로 `%LOCALAPPDATA%\<앱이름>\WebView2` 를 쓰지만 [3], 실제 위치는 앱마다 달라서 앱별로 확인합니다. 앱이 지울 수 있는 데이터 종류(`CoreWebView2BrowsingDataKinds`)는 `LocalStorage`, `IndexedDb`, `CacheStorage`, `FileSystems`, `WebSql`(Edge 에서 제거됨), `Cookies`, `DiskCache`, `DownloadHistory`, `BrowsingHistory`, `GeneralAutofill`, `PasswordAutosave`, `Settings` 로 나뉘어 있어서 [3], UDF 에서 찾을 데이터도 이 종류를 기준으로 가늠합니다.

UDF 를 언제 지우는지도 앱 종류마다 다릅니다 [3]. Win32·.NET·WinUI 2·WinUI 3 앱은 UDF 를 자동으로 지우지 않고, ClickOnce 앱은 자동으로 지우며, 스토어 앱은 앱을 지울 때 Windows 가 UDF 를 지웁니다. 그래서 스토어 앱·ClickOnce 앱이 아닌 WebView2 앱은 앱을 지운 뒤에도 UDF 가 남을 수 있고, 앱이 UDF 위치를 바꾼 경우에도 이전 UDF 는 자동으로 지워지지 않습니다 [3].

### WKWebView (macOS·iOS)

macOS·iOS 앱이 쓰는 WKWebView 의 저장 위치와 데이터 저장소 구조는 이 쪽을 쓰면서 Apple 문서를 열지 않아 확인하지 못했습니다. macOS 의 LevelDB·IndexedDB 형식은 [LevelDB와 IndexedDB (macOS)](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/leveldb-indexeddb.html) 를 봅니다.

## 읽는 법

1. 앱의 데이터 폴더를 찾습니다. Electron 앱은 `appData` 아래 앱 이름 폴더에서 시작하고, 스토어 앱은 패키지 폴더 아래 `LocalCache\Roaming\` 을 보고, WebView2 앱은 실행 파일 옆 `.exe.WebView2` 폴더와 `%LOCALAPPDATA%` 아래를 봅니다.
2. 앱을 끈 상태에서 폴더째 복사하거나, 앱이 켜져 있다면 쓰기 잠금이 걸린 파일이 있다는 점을 기록해 둡니다.
3. 복사본을 크롬 계열 저장소(쿠키 DB·Local Storage·IndexedDB·캐시)와 앱 자체 JSON 파일로 나눕니다. 크롬 계열 저장소는 다른 판의 방법으로 읽고, JSON 파일은 키 이름과 값 종류부터 목록으로 뜹니다.
4. `config.json` 같은 파일의 설치·업데이트 관련 키와 계정 식별자 키를 먼저 읽고, 쿠키 DB 의 `host_key` 와 시각 칸으로 어느 서비스 주소에 로그인 세션이 있었는지 봅니다.
5. `Partitions\` 아래 파티션마다 같은 작업을 되풀이합니다.

## 포렌식에서 중요한 점

**쓰는 중인 파일은 잠겨 있습니다.** 이 PC 에서 기본 `Network\Cookies` 와 `declarative_performance_observer.db` 는 앱이 쓰고 있어서 SQLite 로 열리지 않았습니다(`OperationalError`, 확인 범위: Windows 11, 2026-09). 원본을 직접 열지 말고 복사본을 만들어 열며, `-journal`·`-wal` 파일도 함께 복사해 두어야 마지막 변경분을 잃지 않습니다.

**LevelDB 는 지운 값이 한동안 남습니다.** Local Storage·IndexedDB 는 LevelDB 라서 지운 레코드가 `.log`·`.ldb` 에 남아 있을 수 있고, 읽는 법은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html) 를 따릅니다. 그 안에 AI 대화 내용이 들어 있는지는 이 쪽을 쓰면서 확인하지 못했고, 되살리는 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md) 에서 다룹니다.

**앱을 지워도 데이터가 남을 수 있습니다.** 위 WebView2 UDF 삭제 규칙대로 스토어 앱·ClickOnce 앱이 아니면 UDF 가 남고, Electron 문서가 `userData` 를 클라우드에 백업하는 환경을 언급하고 있어서 [1] 백업 사본이 있는지도 확인합니다. Electron 스토어 앱의 `LocalCache` 가 앱 삭제 때 함께 지워지는지는 확인하지 못했습니다.

## 함정

**같은 UDF 는 여러 앱이 함께 쓸 수 있습니다.** 같은 UDF 를 쓰는 WebView2 컨트롤은 앱이 달라도 같은 로그온 세션 안에서 세션을 공유한다고 문서가 적고 있어서 [3], UDF 의 쿠키 하나를 특정 앱의 흔적이라고 단정하지 않습니다.

**Windows 의 safeStorage 는 사용자 단위 보호입니다.** 같은 사용자 공간의 다른 앱은 풀 수 있다고 문서가 적고 있어서 [2], 암호화돼 있다는 사실만으로 그 사용자 계정 안의 다른 프로그램이 읽지 못했다고 쓰지 않습니다.

**하위 폴더 이름을 문서로 단정하지 않습니다.** WebView2 UDF 의 하위 폴더 이름과 Electron `crashDumps` 의 OS 별 기본 위치는 문서에 없었고, `logs` 도 앱이 `setAppLogsPath()` 를 부른 경우의 위치만 문서에 있습니다 [1]. 검체에서 본 이름을 그대로 적고, 다른 앱에도 같다고 쓰지 않습니다.

**앱 폴더의 크롬 계열 파일은 브라우저 기록이 아닙니다.** 이름과 형식이 크롬과 같아도 그 앱 창 안에서 생긴 데이터이고, 같은 서비스를 브라우저로 쓴 흔적은 브라우저 프로필 폴더에 따로 남습니다.

## 도구

쿠키 DB 는 DB Browser for SQLite 같은 공개 도구로 복사본을 열어 읽고, LevelDB 는 다른 판 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html) 에 소개한 공개 도구로 읽습니다. JSON 파일은 `jq` 같은 공개 도구로 키 목록을 뽑을 수 있습니다.

## 참고 문헌

1. Electron — app (app.getPath) — https://www.electronjs.org/docs/latest/api/app
2. Electron — safeStorage — https://www.electronjs.org/docs/latest/api/safe-storage
3. Microsoft Learn — Manage user data folders (WebView2) — https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/user-data-folder
