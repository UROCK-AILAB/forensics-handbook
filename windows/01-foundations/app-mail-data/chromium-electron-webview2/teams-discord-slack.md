---
title: "Electron·WebView2 앱 데이터 위치"
parent: "크롬 계열 앱 공통 구조"
grand_parent: "기반 · 앱·메일 데이터 구조"
nav_order: 440
---

# Electron·WebView2 앱 데이터 위치 (Teams·Discord·Slack 등)

> 위치: [크롬 계열 앱 공통 구조 (Chromium·Electron·WebView2)](index.md) > Electron·WebView2 앱 데이터 위치

## 한 줄 요약

Electron 앱과 WebView2 를 쓰는 앱은 Chromium 의 저장 방식을 그대로 써서 앱 폴더 안에 브라우저와 같은 모양의 폴더가 생깁니다. 위치는 앱이 정하므로 기본 위치를 알아 두고, 기본 위치를 벗어난 폴더는 `Local State`·`EBWebView` 이름으로 찾습니다.

## 이 구조를 쓰는 아티팩트

| 앱 | 방식 | 근거 | 자세히 |
|---|---|---|---|
| VS Code | Electron |  | 이 핸드북에 따로 페이지 없음 |
| 새 Teams | WebView2 (`EBWebView` 폴더) |  | [마이크로소프트 팀즈](../../../02-artifacts/messengers/teams.md) |
| 클래식 Teams | 실제 기기에서 확인 | 위치만 공개 문서[3] | [마이크로소프트 팀즈](../../../02-artifacts/messengers/teams.md) |
| 새 Outlook | WebView2 (`EBWebView` 폴더) |  | [새 Outlook](../../../02-artifacts/mail/new-outlook.md) |
| OneDrive | WebView2 (`EBWebView` 폴더) |  | [원드라이브](../../../02-artifacts/cloud-notes/onedrive/index.md) |
| 카카오톡 PC | 사용자별 폴더 안에 `EBWebView` 폴더 |  | [카카오톡 PC](../../../02-artifacts/messengers/kakaotalk-pc/index.md) |
| Discord | 폴더 두 개 |  | [디스코드](../../../02-artifacts/messengers/discord.md) |
| Slack | 실제 기기에서 확인 | — | [슬랙](../../../02-artifacts/messengers/slack.md) |

아래 폴더·파일 이름, JSON 키 이름, 파일 앞 몇 바이트는 Windows 11(빌드 26200) 기준입니다. 앱 버전마다 다를 수 있어 실제 기기에서 확인합니다.

안에 든 파일을 읽는 법은 브라우저와 같아서 프로필 폴더와 `Local State` 는 [프로필 폴더와 계열 브라우저 구분](user-data-profile-local-state.md) 에서, 캐시는 [캐시 형식](blockfile-simple-cache.md) 에서, 암호화는 [쿠키·비밀번호 암호화](dpapi-app-bound-encryption.md) 에서 다룹니다.

## 구조

> 그림 자리: 세 가지 폴더 층을 나란히 비교. 브라우저 `User Data` (`Local State` + `Default\…`), 프로필 폴더가 없는 Electron 앱 폴더 (`Local State` 와 `Cache`·`Network` 가 한 층), WebView2 사용자 데이터 폴더 (`EBWebView\Local State` + `EBWebView\Default\…`)

### Electron 앱

Electron 은 폴더 자리에 이름을 붙여 부릅니다. Windows 기본값은 아래와 같습니다[1].

| 이름 | Windows 기본값 | 두는 것 |
|---|---|---|
| `appData` | `%APPDATA%` | 사용자별 앱 데이터의 뿌리 |
| `userData` | `appData` 에 앱 이름을 붙인 폴더. 곧 `%APPDATA%\<앱 이름>` | 앱 데이터 |
| `sessionData` | `userData` 와 같음 | localStorage·쿠키·디스크 캐시·네트워크 상태·DevTools 파일·GPU 셰이더 같은 세션 데이터 |

앱 이름은 `package.json` 의 이름에서 오고, 보통 `productName` 을 `name` 보다 먼저 씁니다[1]. 그래서 폴더 이름이 실행 파일 이름이나 제품 이름과 다를 수 있습니다.

앱은 `ready` 이벤트 전에 `sessionData` 경로를 바꿀 수 있고[1], 그러면 쿠키·캐시가 `userData` 가 아닌 곳에 생깁니다.

Chromium 이 만드는 폴더와 이름이 겹칠 수 있으므로, 앱 전용 파일은 `userData` 바로 아래가 아니라 하위 폴더에 두는 것이 Electron 의 권장 방식입니다[1]. 이 권고를 따르지 않은 앱은 `userData` 바로 아래에 Chromium 폴더와 앱 폴더가 섞이므로, 폴더마다 누가 만들었는지 구분해서 읽습니다.

#### 예: VS Code

VS Code 의 폴더는 `%APPDATA%\Code` 입니다.

`Default` 같은 프로필 폴더가 없고, `Cache`, `Code Cache`, `Local Storage`, `Session Storage`, `Network`, `Preferences`, `Service Worker` 와 `Local State` 가 `userData` 바로 아래에 있습니다. `Partitions` 폴더 아래에는 따로 나뉜 세션 데이터 폴더가 있습니다. 예: `vscode-browser`. `Network\Cookies` 와 `Cache\Cache_Data` 는 브라우저와 같은 구조입니다.

`Partitions` 아래 폴더도 프로필 폴더처럼 쿠키·캐시가 따로 쌓이는 자리로 보고 따로 읽습니다.

### WebView2 앱

WebView2 는 사용자 데이터 폴더 (User Data Folder, UDF) 에 쿠키·권한·캐시 같은 브라우저 데이터를 둡니다[2].

| 앱 종류 | 기본 UDF 위치[2] |
|---|---|
| Win32·.NET (WPF·WinForms) | 실행 파일 경로 뒤에 `.WebView2` 를 붙인 폴더. 예: `D:\WebView2App\WebView2.exe` 를 실행하면 `D:\WebView2App\WebView2.exe.WebView2\` |
| ClickOnce | 실행 파일이 있는 폴더 또는 그 하위 |
| WinUI 2 (UWP)·패키지된 WinUI 3 | 패키지 폴더의 `ApplicationData\LocalFolder` |

설치 폴더(`Program Files` 등)에는 쓰기 권한이 없어 기본 위치가 실패하므로, Win32·.NET 앱은 대부분 `userDataFolder` 인수로 위치를 직접 정하도록 권장합니다[2]. 그래서 실제 앱은 기본 위치가 아닌 곳을 쓰는 경우가 많습니다.

UDF 를 만든 뒤 브라우저 데이터는 UDF 안의 하위 폴더에 쌓이고[2], 이 하위 폴더 이름은 보통 `EBWebView` 입니다. `EBWebView` 안은 브라우저 User Data 와 같은 구성입니다. `Local State`, `Last Version`, 그리고 `Default\` 아래 `History`, `Login Data`, `Network\Cookies`, `Cache\Cache_Data`, `Code Cache`, `Local Storage` 등이 있습니다.

UDF 하나에는 프로필을 여러 개 둘 수 있고 프로필마다 전용 폴더가 생깁니다[2]. 다만 UDF 하나는 한 번에 WebView2 세션 하나만 쓰며, 같은 UDF 를 쓰는 컨트롤은 앱이 달라도 세션을 함께 씁니다[2].

- 패키지 앱 폴더의 구조는 [UWP 앱 데이터 구조](../packages-settings-dat.md) 에서 다룹니다.

#### 앱별 EBWebView 위치

| 앱 | 위치 |
|---|---|
| 새 Outlook | `%LOCALAPPDATA%\Microsoft\Olk\EBWebView` |
| OneDrive | `%LOCALAPPDATA%\Microsoft\OneDrive\EBWebView` |
| 여러 스토어 앱 | `%LOCALAPPDATA%\Packages\<패키지 이름>\LocalState\EBWebView` |
| 새 Teams | `%LOCALAPPDATA%\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams\EBWebView` |
| 카카오톡 PC | `%LOCALAPPDATA%\Kakao\KakaoTalk\users\<사용자별 폴더>\wv\EBWebView` |
| Edge 안의 OneAuth | `%LOCALAPPDATA%\Microsoft\Edge\User Data\OneAuth\WebView2\EBWebView` |

#### 앱마다 다른 Chromium 버전

`EBWebView` 의 `Last Version` 값은 앱마다 다릅니다. 아래는 한 PC 에 함께 있던 값의 예입니다.

| 앱 | `Last Version` |
|---|---|
| 새 Outlook | `151.0.4129.86` |
| 새 Teams | `153.0.4234.48` |
| OneDrive | `149.0.4022.96` |

같은 PC 안에서도 폴더마다 Chromium 버전이 다를 수 있으므로, 파일 구조를 판단할 때는 그 폴더의 `Last Version` 을 기준으로 삼고 같은 PC 의 Edge 브라우저 버전으로 짐작하지 않습니다.

### Teams

| 판 | Windows 캐시 위치[3] |
|---|---|
| 클래식 Teams | `%appdata%\Microsoft\Teams` |
| 새 Teams | `%userprofile%\appdata\local\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams` |

새 Teams 의 `EBWebView\Local State` 에는 `Default` 와 `WV2Profile_tfw` 두 프로필이 있고, `EBWebView` 아래에도 `WV2Profile_tfw` 폴더가 있습니다. "tfw" 의 뜻을 설명한 공개 자료는 없습니다. 두 프로필 폴더를 모두 읽습니다. `EBWebView` 폴더가 있으므로 새 Teams 는 WebView2 기반으로 보입니다.

- 대화 기록 같은 Teams 고유 해석은 [마이크로소프트 팀즈](../../../02-artifacts/messengers/teams.md) 에서 다룹니다.

### Discord·Slack

- Discord 는 `%APPDATA%\discord` 와 `%LOCALAPPDATA%\Discord` 두 폴더가 있습니다. 두 폴더를 모두 봅니다.
- Slack 은 설치형과 스토어 판의 경로가 다를 수 있어 실제 기기에서 확인합니다.
- 두 앱의 해석은 [디스코드](../../../02-artifacts/messengers/discord.md) 와 [슬랙](../../../02-artifacts/messengers/slack.md) 에서 다룹니다.
- 경로를 모를 때는 아래 "읽는 법" 처럼 `Local State` 와 `EBWebView` 이름으로 찾습니다.

## 읽는 법

1. **이름으로 후보를 모읍니다.** 사용자 프로필마다 `Local State` 파일과 `EBWebView` 폴더를 모두 찾습니다. `%APPDATA%`, `%LOCALAPPDATA%`, `%LOCALAPPDATA%\Packages` 아래를 먼저 보고 디스크 전체로 넓힙니다. 이미지에서는 [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md) 목록에서 이름으로 찾습니다.
2. **경로로 앱을 구분합니다.** `%APPDATA%\<앱 이름>`, 패키지 폴더 이름, 실행 파일 경로 + `.WebView2` 같은 모양을 봅니다. 폴더 이름이 제품 이름과 다를 수 있으니 [설치 프로그램](../../../02-artifacts/system-account/uninstall.md) 과 [스토어 앱 설치 목록](../../../02-artifacts/system-account/appx-staterepository.md) 에서 설치 경로를 맞춰 봅니다.
3. **층을 확인합니다.** `Default` 같은 프로필 폴더가 있는지 봅니다. VS Code 같은 Electron 앱처럼 없을 수도 있습니다. 그때는 `Local State` 가 있는 폴더를 프로필 폴더처럼 읽습니다.
4. **버전을 적습니다.** `Last Version` 파일이 있으면 그 값을 적습니다. 파일 구조는 이 버전에 맞춰 판단합니다.
5. **추가 세션 폴더를 찾습니다.** `Partitions` 아래 폴더와 WebView2 의 추가 프로필 폴더(예: 새 Teams 의 `WV2Profile_tfw`)도 같은 방법으로 읽습니다.
6. **파일을 읽습니다.** 방문 기록·쿠키·저장소·캐시는 [크롬 계열 브라우저](../../../02-artifacts/browsers/chrome-edge-whale/index.md) 와 같은 방법으로 읽습니다. 결과에는 브라우저가 아니라 앱 이름과 폴더 경로를 붙입니다.

## 포렌식에서 중요한 점

### 앱을 지워도 남는 폴더

UDF 삭제 규칙은 아래와 같습니다[2].

| 경우 | UDF 는 어떻게 되나 |
|---|---|
| Win32·.NET·WinUI 2·WinUI 3 앱 | 자동으로 지우지 않습니다. MSIX 로 설치한 앱을 지워도 자동으로 정리하지 않습니다 |
| Microsoft Store 패키지 앱을 제거 | Windows 가 UDF 를 자동으로 지웁니다 |
| ClickOnce 앱 | 세션이 끝나면 UDF 를 자동으로 지웁니다 |
| 앱이 UDF 위치를 바꿈 | 이전 UDF 를 자동으로 정리하지 않습니다 |

그래서 앱을 지운 뒤에도 UDF 가 남을 수 있습니다. 설치 목록에 없는 앱의 `EBWebView` 가 보이면 지운 앱의 흔적인지 확인합니다. MSIX 와 스토어 패키지 앱의 규칙이 서로 달라 보이므로 실제로 남았는지는 폴더를 직접 보고 판단합니다.

### 여러 앱이 함께 쓰는 UDF

같은 UDF 를 쓰는 컨트롤은 앱이 달라도 세션을 함께 쓰므로[2], 한 UDF 안의 쿠키·기록이 폴더 경로가 가리키는 앱에서만 나왔다고 단정하지 않습니다.

### 캐시를 지운 경우

새 Teams 는 설정 > 앱 > 설치된 앱 > 고급 옵션 > 재설정 으로도 앱 데이터를 지울 수 있습니다[3]. Teams 캐시를 지우면 원인 조사에 쓰는 진단 로그도 함께 지워지므로[3], 캐시와 로그가 함께 없으면 사용자가 캐시를 지웠을 가능성도 따져 봅니다.

- 지운 파일은 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 방법으로 찾습니다.

### 지운 기록과 손상

앱 폴더 안의 파일 형식은 브라우저와 같아서 지운 레코드와 비정상 종료 흔적도 같은 방법으로 봅니다. DB 파일은 [SQLite 데이터베이스](../../database-log-formats/sqlite/index.md), 캐시는 [캐시 형식](blockfile-simple-cache.md) 을 봅니다.

## 함정

- **앱 안의 폴더를 브라우저 프로필로 착각합니다.** Edge 의 User Data 안에도 `OneAuth\WebView2\EBWebView` 가 있을 수 있습니다. 이 폴더는 Edge 브라우저 프로필이 아닙니다.
- **`Default` 가 없어서 빈 폴더로 봅니다.** VS Code 같은 Electron 앱은 `userData` 바로 아래에 `Cache`·`Network` 가 있습니다. `Default` 를 찾는 도구는 이 폴더를 건너뛸 수 있습니다.
- **기본 위치만 봅니다.** Electron 은 `sessionData`, WebView2 는 `userDataFolder` 로 위치를 바꿀 수 있습니다.
- **WebView2 버전을 Edge 버전으로 짐작합니다.** 앱마다 `Last Version` 이 다릅니다.
- **폴더 하나만 수집합니다.** Discord 는 폴더가 두 개 있습니다. 새 Teams 는 프로필 폴더가 두 개 있습니다.
- **폴더 이름으로 앱을 단정합니다.** Electron 앱 폴더 이름은 `package.json` 에서 옵니다. 설치 기록과 맞춰 봅니다.

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| 파일 목록 도구, MFT 목록 도구 | `Local State`·`EBWebView` 이름으로 후보 폴더를 모읍니다 |
| 텍스트 편집기, JSON 조회 도구(jq 등) | `Local State` 의 프로필 목록과 암호화 키 유무를 봅니다 |
| 크롬 계열 브라우저용 공개 분석 도구 | 앱 폴더를 브라우저 프로필 폴더처럼 지정해 읽습니다. `Default` 가 없는 폴더를 읽는지 먼저 확인합니다 |

## 참고 문헌

- Electron docs, *app* (`app.getPath`) — https://www.electronjs.org/docs/latest/api/app
- Microsoft Learn, *Manage user data folders* (WebView2, ms.date 2026-06-26) — https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/user-data-folder
- Microsoft Learn, *Clear the Teams client cache* (ms.date 2026-09-14) — https://learn.microsoft.com/en-us/troubleshoot/microsoftteams/teams-administration/clear-teams-cache
