---
title: "크롬 계열 앱 공통 구조"
parent: "기반 · 앱·메일 데이터 구조"
nav_order: 420
has_children: true
has_toc: false
---

# 크롬 계열 앱 공통 구조 (Chromium·Electron·WebView2)

## 한 줄 요약

Chrome·Edge 같은 브라우저, Electron 앱, WebView2 를 쓰는 앱은 모두 Chromium 의 저장 방식을 씁니다.
그래서 폴더 안 모양이 거의 같고 `Local State`, 프로필 폴더, `Cache`, `Network\Cookies` 가 공통으로 보입니다. 이 구조를 한 번 익히면 브라우저와 메신저·메일·클라우드 앱의 기록을 같은 방법으로 읽습니다.

## 왜 중요한가

웹 기록은 브라우저 폴더에만 있지 않습니다. 새 Outlook·새 Teams·OneDrive·카카오톡 PC 폴더 안에서도 Chromium 폴더(`EBWebView`)를 봤고 (관찰), 앱 안에서 연 웹 화면의 쿠키·저장소·캐시가 이 폴더에 쌓입니다.

위치는 앱이 정합니다. 브라우저는 실행 인수로, Electron·WebView2 앱은 앱 코드로 위치를 바꿀 수 있어서 기본 경로만 보면 놓칩니다. 관찰한 범위에서는 위치가 Windows 버전보다 앱 종류와 앱 버전에 따라 달라지는 것으로 보였지만, PC 한 대에서 본 것이라 단정하지 않습니다.

같은 PC 안에서도 폴더마다 형식이 달라서 HTTP 캐시와 `Code Cache` 는 저장 형식이 달랐습니다 (관찰). 쿠키·비밀번호를 푸는 키 구성도 브라우저와 앱이 달랐으므로 (관찰) 복호에 필요한 것도 폴더마다 다릅니다.

앱을 지워도 데이터 폴더가 남을 수 있으니, 설치 기록에 없는 앱의 흔적을 여기서 찾습니다.

이 묶음에서 "관찰" 이라고 적은 내용은 Windows 11(빌드 26200) PC 한 대에서 폴더·파일 이름, JSON 키 이름, 파일 앞 몇 바이트만 보고 적은 것입니다.

## 한눈에 보기

### 어디에 있나

| 종류 | Windows 기본 위치 | Windows 버전 | 알려 주는 것 |
|---|---|---|---|
| Chrome | `%LOCALAPPDATA%\Google\Chrome\User Data` | 문서에 버전 구분 없음 | 프로필별 방문 기록·쿠키·저장 비밀번호·캐시 |
| Chromium | `%LOCALAPPDATA%\Chromium\User Data` | 문서에 버전 구분 없음 | 위와 같음 |
| Edge | `%LOCALAPPDATA%\Microsoft\Edge\User Data` | 관찰: Windows 11 | 위와 같음. Edge 계정 정보가 더 있음 |
| Electron 앱 | `%APPDATA%\<앱 이름>` (기본값) | 문서에 버전 구분 없음 | 앱 안 웹 화면의 쿠키·저장소·캐시 |
| WebView2 앱 (설치형 Win32·.NET) | 실행 파일 경로 + `.WebView2` (기본값). 앱이 다른 곳을 정하는 경우가 많음 | 문서에 버전 구분 없음 | 위와 같음 |
| WebView2 앱 (패키지 앱) | 패키지 폴더의 `ApplicationData\LocalFolder` | 문서에 버전 구분 없음 | 위와 같음 |
| 새 Teams | `%userprofile%\appdata\local\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams` | 문서에 버전 구분 없음 | 앱 캐시와 WebView2 데이터 |

다른 계열 브라우저와 다른 앱의 위치, 관찰한 `EBWebView` 위치는 하위 페이지에 정리했습니다. `%APPDATA%`·`%LOCALAPPDATA%` 는 사용자마다 따로 있으므로 사용자 프로필마다 봅니다.

### 폴더 안 공통 요소

| 요소 | 알려 주는 것 | 자세히 |
|---|---|---|
| `Local State` | 프로필 목록, 계정 정보로 보이는 칸, 암호화 키 | [프로필 폴더와 계열 브라우저 구분](user-data-profile-local-state.md) |
| 프로필 폴더 (`Default`, `Profile 1` …) | 프로필마다 따로 쌓인 기록 | [프로필 폴더와 계열 브라우저 구분](user-data-profile-local-state.md) |
| `Last Version`·`Last Browser` | 마지막으로 실행한 버전과 실행 파일. 어느 브라우저·앱의 폴더인지 가리는 단서 | [프로필 폴더와 계열 브라우저 구분](user-data-profile-local-state.md) |
| `EBWebView` 폴더 | WebView2 앱이 쓰는 Chromium 데이터 | [Electron·WebView2 앱 데이터 위치](teams-discord-slack.md) |
| `Cache\Cache_Data` | HTTP 캐시. 블록 파일 방식 (관찰) | [캐시 형식](blockfile-simple-cache.md) |
| `Code Cache\js`·`Code Cache\wasm` | 스크립트 캐시. Simple Cache (관찰) | [캐시 형식](blockfile-simple-cache.md) |
| 쿠키·비밀번호 DB 의 암호문 | 암호화한 쿠키·비밀번호 값. 앞 3바이트 `v10`·`v20` 으로 방식을 가림 | [쿠키·비밀번호 암호화](dpapi-app-bound-encryption.md) |

> 그림 자리: 브라우저 `User Data`, Electron 앱 폴더, WebView2 앱의 `EBWebView` 를 나란히 놓고 공통 요소(`Local State`·프로필 폴더·`Cache`·`Network\Cookies`)를 같은 색으로 칠한 비교 그림

## 읽는 순서

1. [프로필 폴더와 계열 브라우저 구분 (User Data·Profile·Local State)](user-data-profile-local-state.md) — 브라우저별 User Data 위치와 프로필 폴더 구성을 다룹니다. `Local State` 로 폴더 이름과 표시 이름을 짝짓고, Chrome 과 Edge 를 가리는 단서를 정리합니다.
2. [Electron·WebView2 앱 데이터 위치 (Teams·Discord·Slack 등)](teams-discord-slack.md) — Electron 과 WebView2 가 데이터 폴더를 어디에 만드는지 다룹니다. 관찰한 앱별 위치와, 앱을 지운 뒤에도 폴더가 남는 경우를 정리합니다.
3. [캐시 형식 (Blockfile·Simple Cache)](blockfile-simple-cache.md) — 두 캐시 형식의 파일 구성과 오프셋을 헥스로 따라갑니다. 비정상 종료와 지운 항목이 어떻게 남는지도 다룹니다.
4. [쿠키·비밀번호 암호화 (DPAPI·App-Bound Encryption)](dpapi-app-bound-encryption.md) — `Local State` 의 두 키와 `v10`·`v20` 암호문을 가리는 법을 다룹니다. 디스크 이미지만으로 무엇을 풀 수 있는지도 나눕니다.

## 함께 볼 페이지

- [크롬 계열 브라우저](../../../02-artifacts/browsers/chrome-edge-whale/index.md) — 방문 기록·쿠키·캐시 같은 파일을 아티팩트로 해석합니다.
- [SQLite 데이터베이스](../../database-log-formats/sqlite/index.md) — 프로필 폴더의 `History` 같은 DB 파일을 읽는 법입니다.
- [DPAPI 구조](../../protection/data-protection-api/index.md) — `Local State` 의 키를 보호하는 DPAPI 마스터 키와 블롭을 다룹니다.
- [UWP 앱 데이터 구조](../packages-settings-dat.md) — 패키지 앱의 `Packages` 폴더 구조를 다룹니다.
- [시각 값 형식](../../value-decoding/filetime-unix-webkit-dos-ole.md) — 캐시와 DB 에 든 시각 값을 바꿉니다.
- [마이크로소프트 팀즈](../../../02-artifacts/messengers/teams.md), [새 Outlook](../../../02-artifacts/mail/new-outlook.md), [원드라이브](../../../02-artifacts/cloud-notes/onedrive/index.md), [카카오톡 PC](../../../02-artifacts/messengers/kakaotalk-pc/index.md), [디스코드](../../../02-artifacts/messengers/discord.md), [슬랙](../../../02-artifacts/messengers/slack.md) — 이 구조를 쓰거나 쓸 수 있는 앱의 아티팩트 페이지입니다.
- [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) — 브라우저와 앱의 기록을 묶어 웹 사용 흐름을 다시 짭니다.

## 참고 문헌

- Chromium docs, *User Data Directory* — https://chromium.googlesource.com/chromium/src/+/HEAD/docs/user_data_dir.md
- Electron docs, *app* (`app.getPath`) — https://www.electronjs.org/docs/latest/api/app
- Microsoft Learn, *Manage user data folders* (WebView2, ms.date 2026-06-26) — https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/user-data-folder
- Microsoft Learn, *Clear the Teams client cache* (ms.date 2026-09-14) — https://learn.microsoft.com/en-us/troubleshoot/microsoftteams/teams-administration/clear-teams-cache
