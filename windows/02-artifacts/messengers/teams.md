---
title: "마이크로소프트 팀즈"
parent: "아티팩트 · 메신저"
nav_order: 2060
---

# 마이크로소프트 팀즈 (Teams)

> 위치: 아티팩트 사전 > 메신저

Teams 는 메시지·연락처·일정 같은 데이터를 IndexedDB 에 LevelDB 형식으로 저장합니다. 새 Teams 는 스토어 패키지 폴더 안에 브라우저와 같은 구성의 `EBWebView` 폴더를 둡니다. 대화용 IndexedDB 는 `Default` 가 아니라 `WV2Profile_tfw` 프로필에 있습니다. 앱 폴더의 `Logs` 에는 실행·업데이트 로그가 쌓입니다. 로그 줄 시각에는 `+09:00` 이 붙지만 실제 값은 UTC 입니다.

이 페이지의 폴더 구성과 로그 시각 설명은 새 Teams 26225.1806.5074.1452, 시간대 KST 기준입니다.

## 무엇을 기록하나 · 왜 생기나

Teams 는 브라우저와 같은 로컬 저장소에 데이터를 적어 둡니다.

Teams 는 데이터를 IndexedDB 에 LevelDB 형식으로 저장하고, 공개 파서 forensicsim 으로 여기서 메시지, 댓글, 게시물, 연락처, 일정, 반응 (reactions) 을 꺼낼 수 있습니다[1]. 새 Teams 폴더에는 WebView2 가 쓰는 `EBWebView` 폴더가 있고, 앱 자체도 로그, 설정 JSON, 원격 측정 (telemetry) DB 를 앱 폴더에 적습니다.

## 위치와 버전별 차이

### 클래식 Teams 와 새 Teams

판마다 Windows 캐시 위치가 다릅니다[2].

| 판 | Windows 캐시 위치 |
|---|---|
| 클래식 Teams | `%appdata%\Microsoft\Teams` |
| 새 Teams | `%userprofile%\appdata\local\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams` |

- 두 위치 모두 사용자 프로필 아래에 있습니다. 사용자마다 따로 봅니다.
- 새 Teams 의 앱 버전은 패키지 버전 폴더 이름(`MSTeams_<버전>_x64__8wekyb3d8bbwe`)에서 읽습니다. 설치 기록은 [스토어 앱 설치 목록](../system-account/appx-staterepository.md) 에서 확인합니다.
- `EBWebView` 폴더 구성과 WebView2 버전 파일(`Last Version`)은 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에서 다룹니다.

### 공개 파서가 시험한 버전

forensicsim 은 아래 두 환경에서 시험됐습니다[1].

| 앱 | 환경 |
|---|---|
| Microsoft Teams 1.4.00.11161 | Windows 10, 무료 업무 조직 |
| "Teams 2.0" 48/21062133356 | Windows 11, 개인 조직 |

"Teams 2.0" 은 2021년 Windows 11 개인용 Teams 로 보입니다. 2023년 이후의 새 Teams(MSTeams 패키지)와 같은 것인지는 공개 자료가 없습니다. 그래서 새 Teams 에 이 파서를 쓸 때는 결과를 따로 검증합니다.

## 구조

### 대화가 남는 곳: IndexedDB

IndexedDB 폴더 이름은 `IndexedDB\https_teams.microsoft.com_0.indexeddb.leveldb` 입니다. 큰 값은 옆의 `.blob` 폴더에 따로 둡니다[1].

새 Teams 에서는 아래 위치에 있습니다.

```
...\MSTeams\EBWebView\WV2Profile_tfw\IndexedDB\
    https_teams.microsoft.com_0.indexeddb.leveldb\      ← 파일 33개
    https_teams.microsoft.com_0.indexeddb.blob\
    https_<조직>-my.sharepoint.com_0.indexeddb.leveldb\
    https_<조직>-my.sharepoint.com_0.indexeddb.blob\
```

- `...indexeddb.leveldb` 폴더에는 `CURRENT`, `MANIFEST-011437`, 번호가 붙은 `.ldb`·`.log` 파일 등이 있습니다(위 예에서 33개).
- `<조직>-my.sharepoint.com` 출처의 IndexedDB 도 있을 수 있습니다. 조직 OneDrive 의 출처입니다.
- `EBWebView\Default` 프로필에는 IndexedDB 가 없고 `Local Storage` 만 있습니다.
- 그래서 대화 데이터는 `Default` 가 아니라 `WV2Profile_tfw` 에서 찾습니다.
- `WV2Profile_tfw` 에는 `History`, `Login Data`, `Network`, `Cache`, `Local Storage\leveldb` 등 브라우저와 같은 구성이 있습니다. 이 파일들은 [크롬 계열 브라우저](../browsers/chrome-edge-whale/index.md) 와 같은 방법으로 읽습니다.

forensicsim 은 텍스트 로그 파일(`.log`)과 바이너리 표 파일(`.ldb`)을 모두 읽습니다. 기록 대부분은 `.ldb` 에 있습니다[1].

- LevelDB 의 파일 구성, 지운 기록이 남는 방식, 압축된 `.ldb` 를 푸는 법은 [LevelDB 저장소](../../01-foundations/database-log-formats/leveldb.md) 에서 다룹니다.
- IndexedDB 안 객체 저장소 이름과 메시지 레코드의 필드 이름은 새 Teams 기준으로 실제 데이터에서 확인해야 합니다.
- forensicsim 설명서에는 지운 기록을 되살리는 기능이 나와 있지 않습니다[1].

### 앱 폴더의 다른 파일

`...\LocalCache\Microsoft\MSTeams` 바로 아래에는 아래 항목이 있습니다.

| 항목 | 내용 |
|---|---|
| `EBWebView` | WebView2 데이터. 위 IndexedDB 가 여기 있습니다 |
| `Logs` | 앱 로그. 아래 "로그" 참고 |
| `app_settings.json` | 앱 설정과 실행 정보 |
| `tfw` | 원격 측정 SQLite DB |
| `UserAvatarIcons` | 이름으로 보면 사용자 사진 캐시입니다 |
| `cmd_settings.json`, `ecs_request_param.json`, `ecs_settings.dat64`, `previous_session_data.json`, `tma_request_param.json`, `uae.json`, `tmp` | 공개 자료 없음 |

`app_settings.json` 에는 아래 키가 있습니다.

| 키 | 알려 줄 수 있는 것 |
|---|---|
| `first_core_launch_time`, `first_app_launch_time`, `core_launch_count`, `app_launch_count` | 첫 실행 시각과 실행 횟수로 보입니다. 값이 모두 0 인 경우가 있습니다 |
| `install_source` | 설치 출처로 보입니다 |
| `active_users` | 항목마다 `id`·`cloudType`·`state` 가 있습니다. 로그인한 계정 목록으로 보입니다 |
| `active_clouds`, `most_recent_cloud` | 쓰는 클라우드. `most_recent_cloud` 값의 예: `"prod"` |
| `default_download_location`, `default_local_recording_location` | 받은 파일과 녹화 파일을 두는 폴더 |
| `web_client_version_used` | 웹 클라이언트 버전 |
| `main_window_bounds` | 창 위치와 크기 |

첫 실행 시각 필드가 0 으로 남는 경우가 있어, 이 필드만으로 첫 실행 시각을 잡지 않습니다. Teams 로 받은 파일은 `default_download_location` 이 가리키는 폴더에서 찾습니다.

`tfw` 폴더에는 이름이 base64 로 인코딩된 SQLite 파일들이 있습니다. `-wal`·`-shm` 짝도 있습니다. 이름을 풀면 `telemetry_offline_storage_EMEACOMMERCIAL` 같은 원격 측정 저장소입니다. 첫 16바이트는 `SQLite format 3` 과 0 바이트입니다.

### 패키지 폴더

`...\Packages\MSTeams_8wekyb3d8bbwe` 아래에는 아래 폴더가 있습니다.

`AC`, `AppData`, `LocalCache`, `LocalState`(비어 있음), `RoamingState`(비어 있음), `Settings`, `SystemAppData`, `TempState`

- `Settings` 에는 `settings.dat`, `settings.dat.LOG1`, `settings.dat.LOG2` 가 있습니다.
스토어 앱의 `settings.dat` 은 [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) 에서 다룹니다.

데이터는 `LocalState` 가 아니라 `LocalCache` 에 있으므로, `LocalState` 가 비었다고 데이터가 없다고 보지 않습니다.

### 로그

`Logs` 폴더에는 아래 모양의 파일이 쌓입니다(예: 파일 67개, 49MB).

| 파일 이름 모양 | 내용 |
|---|---|
| `MSTeams_<날짜>_<시각>.<번호>.log` | 앱 본체 로그 |
| `Launcher_*` | 실행기 로그 |
| `MSTeamsUpdate_*`, `MSTeamsBackgroundUpdate_*` | 업데이트 로그 |
| `MSTeamsBackgroundEcs_*`, `MSTeamsNM_SlimCore_*` | 공개 자료 없음 |
| `SkypeRT`, `skylib`, `mediastack`, `CS_logs`, `sc-tfw` 등 | 이름으로 보면 통화·미디어 쪽 로그입니다 |

로그 한 줄은 아래 모양입니다.

```
2026-09-20T23:33:05.907352+09:00 0x000026f4 <INFO> ...
```

앞에서부터 ISO 8601 시각, 스레드 ID, 등급, 내용입니다.

로그 파일은 이어서 돌아갑니다. 다음 파일은 이전 파일의 마지막 줄 시각에 시작합니다.

## 증거로서 의미

### 증명하는 것

- **앱을 쓴 계정.** 두 위치 모두 사용자 프로필 아래에 있습니다. 어느 Windows 계정의 Teams 인지 알 수 있습니다.
- **앱 안에 저장된 메시지·연락처·일정.** IndexedDB 에서 메시지, 댓글, 게시물, 연락처, 일정, 반응을 꺼낼 수 있습니다[1].
- **조직 OneDrive 사용.** `<조직>-my.sharepoint.com` 출처의 IndexedDB 는 조직 OneDrive 출처의 데이터가 이 앱 안에 저장됐다는 뜻입니다.
- **앱 실행과 업데이트 시간대.** 로그 파일 이름과 줄 시각이 실행·업데이트 시간대를 알려 줍니다.
- **받은 파일을 두는 폴더.** `default_download_location` 이 받은 파일을 찾을 폴더를 알려 줍니다.

### 증명하지 못하는 것

- **전체 대화.** IndexedDB 는 앱이 PC 에 저장한 만큼만 담습니다. 여기 없다고 대화가 없었다고 말할 수 없습니다.
- **메시지를 읽었는지.** 저장된 것은 앱이 받은 데이터입니다. 사용자가 화면에서 읽었다는 뜻은 아닙니다.
- **누가 입력했는지.** 계정까지만 알려 줍니다. 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- **첫 실행 시각.** `app_settings.json` 의 첫 실행 필드는 0 으로 남아 있을 수 있습니다.
- **원격 측정 DB 의 사용자 행위.** `tfw` 의 DB 는 원격 측정 저장소입니다. 대화 기록으로 보지 않습니다.

보고서에는 "피의자가 이 메시지를 읽었다" 가 아니라 이렇게 씁니다. "A 계정의 새 Teams `WV2Profile_tfw` 프로필 IndexedDB 에서 이 메시지 레코드를 꺼냈다. 레코드는 앱이 이 PC 에 저장한 데이터이다."

## 시각 해석

| 시각 | 무엇이 바뀔 때 | UTC·현지 |
|---|---|---|
| 로그 줄 시각 | 로그 줄을 쓸 때 | `+09:00` 이 붙지만 실제 값은 UTC 입니다 |
| 로그 파일 이름의 날짜·시각 | 새 로그 파일을 만들 때 | 현지 시각(KST)입니다 |
| `app_settings.json` 의 실행 시각 필드 | 공개 자료 없음 | 0 으로 남은 경우가 있습니다 |
| IndexedDB 레코드 안의 시각 | 공개 자료 없음 | LevelDB 자체의 기록에는 시각 필드가 없습니다. [LevelDB 저장소](../../01-foundations/database-log-formats/leveldb.md) 참고 |
| 파일 시스템 시각 | 파일을 다시 쓸 때 | UTC. [마스터 파일 테이블](../filesystem/mft.md) 참고 |

### 로그 줄 시각은 UTC 입니다

예를 들어 마지막 줄 시각이 `11:43:36.818898+09:00` 인 로그 파일의 수정 시각은 20:43:36 KST, 곧 UTC 로 11:43:36 입니다. 줄 시각의 숫자는 UTC 인데 `+09:00` 표시만 붙은 것이며, MSTeams 로그와 Launcher 로그가 모두 이렇게 적힙니다.

파일 이름은 현지 시각입니다. 첫 줄이 `2026-09-20T23:33:05+09:00` 인 파일의 이름은 `MSTeams_2026-09-21_08-33-05.00.log` 입니다. 23:33:05 UTC 는 다음 날 08:33:05 KST 입니다.

판과 시간대마다 다를 수 있습니다. 줄 시각을 표시대로 현지 시각으로 읽으면 KST PC 에서 9시간이 틀립니다. 증거 PC 에서도 마지막 줄 시각과 파일 수정 시각을 맞춰 본 뒤 씁니다. 증거 PC 의 시간대는 [시간대 설정](../system-account/time-zone.md) 에서 확인합니다.

## 함정과 한계

- **`Default` 프로필만 봅니다.** 대화용 IndexedDB 는 `WV2Profile_tfw` 에 있습니다. `EBWebView` 아래 프로필 폴더를 모두 봅니다.
- **로그 줄 시각의 `+09:00` 을 믿습니다.** 실제 값은 UTC 입니다. 파일 수정 시각과 맞춰 봅니다.
- **`LocalState` 만 봅니다.** 새 Teams 의 데이터는 `LocalCache` 아래에 있습니다.
- **원본 LevelDB 를 라이브러리로 엽니다.** 여는 과정에서 옛 값이 정리될 수 있습니다. 늘 사본에서 작업합니다. 이유는 [LevelDB 저장소](../../01-foundations/database-log-formats/leveldb.md) 에서 다룹니다.
- **캐시 지우기와 재설정.** 새 Teams 는 앱 재설정으로 데이터를 지울 수 있습니다. 캐시를 지우면 진단 로그도 함께 지워집니다[2]. 자세한 규칙은 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에서 다룹니다. 폴더와 로그가 함께 비어 있으면 지운 흔적인지 따져 보고, 옛 시점은 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 찾습니다.
- **공개 파서를 그대로 씁니다.** forensicsim 이 시험한 버전은 새 Teams 와 다를 수 있습니다.
- **원격 측정 DB 를 대화 DB 로 봅니다.** `tfw` 의 SQLite 는 원격 측정 저장소입니다.
- **SharePoint 출처를 Teams 대화로 봅니다.** `<조직>-my.sharepoint.com` 출처는 조직 OneDrive 쪽 데이터입니다. [원드라이브](../cloud-notes/onedrive/index.md) 와 함께 해석합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 base64 규칙과 SQLite 명세로 만든 예시입니다. 실제 데이터에서 나온 파일 이름이 아닙니다.

1. `tfw` 폴더의 파일 이름을 base64 로 풉니다. 예를 들어 이름이 아래와 같다면

   ```
   dGVsZW1ldHJ5X29mZmxpbmVfc3RvcmFnZV9FTUVBQ09NTUVSQ0lBTA==
   ```

   풀면 `telemetry_offline_storage_EMEACOMMERCIAL` 입니다. 실제 이름에는 끝 `=` 나 확장자가 다를 수 있습니다.

2. 같은 파일의 첫 16바이트를 봅니다.

   ```
   오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
   0x00   53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
   ```

   이 머리이면 평문 SQLite 입니다. 사본을 SQLite 도구로 엽니다.

3. 로그 시각을 확인합니다. 최신 `MSTeams_*.log` 의 마지막 줄 시각과 그 파일의 수정 시각(UTC)을 나란히 적습니다. 숫자가 같으면 줄 시각은 표시와 달리 UTC 입니다.

4. IndexedDB 의 `.log` 파일에서 문자열을 찾습니다. `.log` 는 압축하지 않아 문자열이 보입니다. `.ldb` 는 압축돼 있어 풀어야 합니다. 자세한 구조는 [LevelDB 저장소](../../01-foundations/database-log-formats/leveldb.md) 에서 다룹니다.

### 공개 도구로 한 번

공개 도구의 예로 forensicsim 이 있습니다. Teams 의 IndexedDB 를 읽어 메시지·연락처·일정 등을 꺼냅니다[1].

- 도구에 `WV2Profile_tfw` 아래 폴더를 넣었는지 확인합니다.
- 시험한 버전과 증거 PC 의 버전이 다르면 결과 몇 건을 `.log` 문자열 검색으로 맞춰 봅니다.
- 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 점 |
|---|---|
| [스토어 앱 설치 목록](../system-account/appx-staterepository.md) | 새 Teams 의 설치 시각과 버전을 봅니다 |
| [SRUM](../execution/system-resource-usage-monitor/index.md) | Teams 가 네트워크를 쓴 시간대를 로그 시각과 맞춰 봅니다 |
| [윈도 알림 기록](../execution/wpndatabase-db.md) | Teams 알림이 남았는지 봅니다 |
| [원드라이브](../cloud-notes/onedrive/index.md) | SharePoint 출처 데이터와 조직 OneDrive 동기화 기록을 맞춰 봅니다 |
| [스카이프](skype.md) | Skype 에서 옮겨 온 대화가 있는지 봅니다 |
| [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) | `EBWebView` 의 쿠키·캐시·방문 기록을 읽는 법을 봅니다 |

여러 출처의 시각을 시간순으로 합치는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다. 조사 전체 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다.

## 실습

Windows 11 가상 머신에 새 Teams 를 설치해 직접 시험하고, 시험 전에 Teams 버전과 가상 머신의 시간대를 적어 둡니다.

1. `EBWebView` 아래 프로필 폴더는 몇 개입니까? `teams.microsoft.com` 출처의 IndexedDB 는 어느 프로필에 있습니까?
2. 메시지 하나를 보낸 직후 IndexedDB 폴더의 `.log` 에서 그 문장이 검색됩니까?
3. 최신 로그의 마지막 줄 시각과 파일 수정 시각을 비교합니다. 줄 시각은 UTC 입니까, 현지 시각입니까? 시간대를 바꿔 다시 시험합니다.
4. `app_settings.json` 의 `first_app_launch_time` 과 `app_launch_count` 는 몇 번 실행한 뒤 0 이 아닌 값이 됩니까?
5. 앱 재설정 뒤 `LocalCache` 아래에 무엇이 남습니까?

## 참고 문헌

- lxndrblz, forensicsim — README — https://github.com/lxndrblz/forensicsim
- Microsoft Learn, "Clear the Teams client cache" — https://learn.microsoft.com/en-us/troubleshoot/microsoftteams/teams-administration/clear-teams-cache
