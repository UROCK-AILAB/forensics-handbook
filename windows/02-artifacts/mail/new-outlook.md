---
title: "새 Outlook"
parent: "아티팩트 · 메일"
nav_order: 1940
---

# 새 Outlook (New Outlook)

새 Outlook (Outlook for Windows) 은 Windows 메일·일정·사람 앱을 대신하는 Microsoft 의 메일 앱입니다. 스토어 앱 패키지로 깔리고, 본체 실행 파일 이름은 `olk.exe` 입니다. PC 에 남는 주된 흔적은 `%LOCALAPPDATA%\Microsoft\Olk` 폴더의 WebView2 프로필과 로그 파일입니다. 로그에는 앱을 켜고 끈 시각, 연결된 계정, 실행 인자가 UTC 시각과 함께 남습니다. 메일 본문을 PC 어디에 어떤 형식으로 두는지는 공개 문서에 나와 있지 않아 실제 데이터로 확인해야 합니다.

## 내용별 근거

| 내용 | 근거 |
|---|---|
| 메일·일정·사람 앱을 대신하는 앱이라는 점, 옮겨 오는 방법 | Microsoft 지원 문서[1] |
| 패키지 이름, 실행 파일, 폴더 구성, 로그 형식 | Windows 11 25H2, 새 Outlook 1.2026.707.300 기준 |
| 로그의 `Time` 필드가 UTC 라는 점 | 로그 마지막 행 시각과 파일 수정 시각의 비교(아래 "시각 해석") |
| 메일 본문·첨부를 PC 에 두는 곳과 형식 | 공개 자료 없음. 실제 데이터로 확인 |
| 오프라인 설정을 켰을 때 메일·첨부를 두는 곳 | 공개 자료 없음. 실제 데이터로 확인 |
| Gmail 같은 다른 회사 계정을 Microsoft 클라우드를 거쳐 동기화한다는 점 | 흔히 알려진 내용. 공식 자료 없음 |
| 클래식 Outlook 의 전환 토글이 남기는 레지스트리 값 | 흔히 알려진 내용. 공식 자료가 없어 이름을 적지 않음 |
| 로그를 몇 개, 며칠치 남기는지 | 공개 자료 없음 |
| 프리패치 파일이 생기는지 | 실제 기기에서 확인 |

## 무엇을 기록하나 · 왜 생기나

### 사용자가 새 Outlook 으로 오는 길

새 Outlook 은 Windows 메일·일정·사람 앱을 대신하는 앱입니다[1]. 새 Outlook 으로 오는 길은 세 가지입니다.

- Microsoft Store 에서 받습니다[1].
- 메일·일정 앱 안의 대화 상자에서 "Open Outlook" 을 누릅니다[1].
- 클래식 Outlook 화면 위 구석의 "Try the new Outlook" 토글을 켭니다[1].

Windows 10 에서도 2025년 1월 선택 업데이트부터 새 기능을 쓸 수 있고, 2월부터 더 넓게 배포됩니다[1]. 다만 여기서 말하는 새 기능이 무엇인지는 밝혀져 있지 않습니다.

그래서 새 Outlook 흔적이 있는 PC 에는 옛 메일 앱이나 클래식 Outlook 의 흔적이 함께 있을 수 있습니다. 옛 메일 앱은 [Windows 메일 앱](hxstore.md) 에서, 클래식 Outlook 은 [아웃룩](outlook/index.md) 에서 다룹니다. 새 Outlook 에 캐시 모드가 없다는 점과 PST 를 다루는 범위도 [아웃룩](outlook/index.md) 허브에 있습니다.

### PC 에 남는 것

앱을 쓰면 `%LOCALAPPDATA%\Microsoft\Olk` 폴더에 WebView2 사용자 데이터 폴더와 로그가 쌓입니다. 로그는 한 줄마다 시각이 붙고, 앱 시작·종료, 계정 조회, 실행 인자가 행으로 남습니다. 스토어 앱이라 `%LOCALAPPDATA%\Packages` 아래에도 패키지 데이터 폴더가 생깁니다.

## 위치와 버전별 차이

| 흔적 | 위치 | 알려 주는 것 |
|---|---|---|
| 앱 패키지 | `C:\Program Files\WindowsApps\Microsoft.OutlookForWindows_<버전>_x64__8wekyb3d8bbwe` | 깔린 판, 실행 파일 이름 |
| 주 데이터 폴더 | `%LOCALAPPDATA%\Microsoft\Olk` | WebView2 프로필, 로그, 창 설정 |
| 패키지 데이터 폴더 | `%LOCALAPPDATA%\Packages\Microsoft.OutlookForWindows_8wekyb3d8bbwe` | 패키지 설정, 배포 정보 |

패키지 이름은 `Microsoft.OutlookForWindows_8wekyb3d8bbwe` 입니다. `Olk` 폴더는 클래식 Outlook 의 첨부 임시 폴더(OLK)와 이름만 비슷한 다른 폴더이며, 첨부 임시 폴더는 [아웃룩](outlook/index.md) 허브에서 다룹니다. Windows 10 에서 같은 위치를 쓰는지는 실제 기기에서 확인합니다. 앱 판에 따라 폴더 구성과 로그 형식이 바뀔 수 있습니다.

## 구조

### 앱 패키지

패키지의 `AppxManifest.xml` 에는 실행 파일이 네 개 적혀 있습니다.

- 본체는 `olk.exe` 입니다.
- 그 밖에 `olkFullTrustExecutor.exe`·`olkPushNotificationBackgroundTask.exe`·`olkexthost.exe` 가 있습니다.

실행 흔적(프리패치·프로세스 목록)은 `olk.exe` 이름으로 찾습니다. 클래식 Outlook 의 실행 파일 이름으로 찾으면 놓칩니다.

### `Olk` 폴더

| 항목 | 내용 |
|---|---|
| `EBWebView\` | WebView2 사용자 데이터 폴더입니다. `Default\` 아래에 `History`, `Network`(쿠키), `Local Storage\leveldb`, `Session Storage`, `Cache`, `Code Cache`, `Login Data`, `Web Data`, `Favicons`, `Top Sites`, `Preferences` 등이 있습니다 |
| `logs\` | `olk_*.log` 파일이 쌓입니다. 3개만 남은 PC 도 있습니다 |
| `UserSettings.json` | 창 위치(`rcNormal`·`rcWork`·`dpi`·`showCmd`), `Flights`, `PinSettings`, `UpdateSettings`, `BootAfterUpdateTime` 같은 필드가 있습니다 |
| `updated.txt`, `xpdApi.log`, `Feedback\` | 함께 있습니다 |

- `EBWebView\Default\` 에 `IndexedDB` 폴더와 `Service Worker` 폴더가 없을 수 있습니다.
- WebView2 프로필 파일을 읽는 법은 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에서 다룹니다.

### 패키지 데이터 폴더

| 항목 | 내용 |
|---|---|
| `AC\INetCache`, `AC\INetCookies\ESE`, `AC\INetHistory`, `AC\Temp` | 캐시·쿠키·기록·임시 파일 이름의 하위 폴더가 있습니다 |
| `LocalCache\sentinel.json` | 배포 링(ring), 패키지 이름, 버전, 해시 필드가 있습니다 |
| `LocalState\` | 비어 있을 수 있습니다 |
| `Settings\settings.dat` (+ `.LOG1`·`.LOG2`) | 패키지 설정 파일입니다 |
| `RoamingState`, `SystemAppData\Helium`, `TempState` | 있습니다 |

`settings.dat` 의 형식과 읽는 법은 [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) 에서 다룹니다.

### 로그 파일 (`logs\olk_*.log`)

- 파일 이름 규칙은 `olk_YYYYMMDD_HHMMSSmmm.log` 입니다. 예를 들면 `olk_20260101_093000123.log` 모양입니다(설명을 위해 만든 이름).
- 탭으로 필드를 나눈 글자 파일이고, 첫 줄이 머리글입니다.
- 머리글의 필드는 `Index`, `Time`, `Metadata`, `Thread`, `Message` 와 `Param0 Type`·`Param0 Value` 부터 `Param9 Type`·`Param9 Value` 까지입니다. 모두 25개입니다.

아래 글자가 든 행을 볼 만합니다.

| 행의 글자 | 함께 남는 값 | 알려 주는 것 |
|---|---|---|
| `Application starting` | `sessionId`, `deviceId` | 앱이 시작한 시각 |
| `Application exiting` | | 앱이 끝난 시각 |
| `FindAccountResult` | `accountIdW`, `accountFound`, `totalAccounts` | 계정 조회 결과 |
| `Command-line`, `Application started with the following command line` | 실행 인자 | 앱이 열린 방법. `mailto:` 링크로 열렸으면 받는 사람 주소가 그대로 남습니다 |
| `Sending verb result response` | 값 안의 계정 메일 주소 | 앱에 연결된 계정 |

실행 인자에는 `olk.exe` 의 전체 경로가 남아서, 경로의 패키지 폴더 이름으로 그때의 앱 판을 알 수 있습니다. 판이 바뀌면 경로의 판 번호도 바뀝니다(예: 1.2025.1104.200 → 1.2026.707.300). 로그가 3개(2026-07-21 두 개, 2026-08-19 한 개)만 남은 PC 도 있으므로, 몇 개, 며칠치를 남기는지는 실제 기기에서 확인합니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 로그에 `Application starting` 행이 있으면 이 프로필에서 새 Outlook 이 실행된 적이 있습니다 | 그 사이에 사용자가 메일을 읽거나 보냈다는 것 |
| `Application starting`·`Application exiting` 행은 앱이 켜지고 꺼진 시각을 알려 줍니다 | 앱 창 앞에 사람이 있었다는 것 |
| `accountFound` 가 true 이면 계정이 연결된 적이 있습니다 | 그 계정의 메일이 PC 에 남아 있다는 것. 계정이 연결됐는데도 `IndexedDB` 폴더가 없을 수 있습니다 |
| 실행 인자에 `mailto:` 주소가 있으면, 그 주소가 든 링크로 앱이 열렸습니다 | 그 주소로 메일을 실제로 보냈다는 것 |
| 로그 속 메일 주소는 이 앱에 그 계정이 있었다는 근거입니다 | 그 계정을 쓴 사람이 누구인지 |
| 패키지 폴더 이름은 깔린 판을 알려 줍니다 | PC 에서 메일을 찾지 못했을 때, 메일을 쓰지 않았다는 것. 메일을 두는 곳이 알려져 있지 않습니다 |

### 보고서 문장

아래 시각과 주소는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`%LOCALAPPDATA%\Microsoft\Olk\logs` 의 로그 파일에 2026-03-05 01:12:40 UTC 의 `Application starting` 행이 있습니다. 같은 파일의 실행 인자 행에 `mailto:partner@example.com` 이 있습니다."
- 쓰면 안 되는 문장: "사용자는 3월 5일 새 Outlook 으로 partner@example.com 에 메일을 보냈습니다."

앞 문장으로는 앱이 그 주소가 든 링크로 열린 사실까지만 알 수 있습니다. 메일을 보냈다고 쓰려면 서버 쪽 기록이나 받는 쪽 사본이 따로 필요합니다.

## 시각 해석

- 로그의 `Time` 필드는 UTC 입니다. 예를 들어 시간대가 UTC+9 인 PC 에서 마지막 행 `Application exiting` 의 `Time` 값이 2026-08-19 02:01:05.382 이면, 같은 파일의 수정 시각은 2026-08-19 11:01:05.38(+09:00) 으로 두 값은 9시간 차이가 납니다.
- 파일 이름의 시각도 UTC 이며, 첫 행의 시각과 거의 같습니다.
- 다른 분석 대상에서는 같은 방법으로 한 번 맞춰 봅니다. 마지막 행의 시각과 파일 수정 시각을 비교하고, 차이가 그 PC 의 시간대와 같은지 봅니다([시간대 설정](../system-account/time-zone.md)).
- `EBWebView` 안 파일의 시각 값은 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 와 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 읽는 법을 봅니다.

## 함정과 한계

1. **클래식 Outlook 위치만 봅니다.** 새 Outlook 흔적은 클래식 Outlook 과 다른 곳에 있습니다. 클래식 Outlook 폴더가 없다고 메일 앱을 쓰지 않았다고 보지 않습니다.
2. **`Olk` 폴더를 첨부 임시 폴더로 봅니다.** 이름만 비슷합니다. 경로를 끝까지 읽습니다.
3. **`EBWebView` 의 기록을 사용자의 웹 사용으로 봅니다.** 이 폴더는 앱 안의 웹 화면이 쓰는 프로필입니다. 브라우저 기록과 나눠 적습니다([크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md)).
4. **계정이 연결됐으니 메일이 PC 에 있다고 봅니다.** `accountFound` 가 true 인데도 `IndexedDB` 폴더가 없는 경우가 있습니다. 메일 본문을 두는 곳과, 오프라인 설정을 켰을 때 두는 곳은 실제 데이터로 확인합니다.
5. **다른 회사 계정의 메일은 그 회사 서버에만 있다고 봅니다.** 새 Outlook 이 Gmail·Yahoo·iCloud·IMAP 계정을 Microsoft 클라우드를 거쳐 동기화한다고 흔히 알려져 있습니다. 그렇다면 메일 사본이 Microsoft 서버에도 생깁니다. 서버 쪽 자료를 어디에 요청할지 정할 때 따로 확인합니다.
6. **로그 시각을 현지 시각으로 읽습니다.** `Time` 필드와 파일 이름의 시각은 UTC 입니다.
7. **로그가 오래 남는다고 봅니다.** 두 날짜의 로그 3개만 남은 PC 도 있습니다. 보관 기간이 알려져 있지 않으므로, 로그가 없는 날에 앱을 쓰지 않았다고 보지 않습니다. 지워진 로그 파일은 [USN 변경 저널](../filesystem/usnjrnl.md) 에서 찾습니다.
8. **전환 토글의 레지스트리 값으로 새 Outlook 사용을 단정합니다.** 이 값은 흔히 알려져 있을 뿐, 이름과 뜻을 밝힌 공식 자료가 없습니다. 새 Outlook 을 쓴 PC 에도 `HKCU\Software\Microsoft\Office\16.0\Outlook\Preferences` 키가 없을 수 있습니다. 로그와 패키지 흔적으로 판단합니다.
9. **로그 형식이 늘 같다고 봅니다.** 판에 따라 바뀔 수 있습니다. 머리글 줄을 먼저 읽고 필드를 맞춥니다.

## 직접 분석해 보기

### 원시 바이트로 한 번

로그는 탭으로 필드를 나눈 글자 파일입니다. 헥스 편집기로 열면 필드 구분과 찾을 낱말이 바이트로 보입니다. 아래 바이트는 글자를 인코딩 규칙으로 계산한 값입니다. 특정 기기에서 뽑은 값이 아닙니다.

| 찾을 글자 | UTF-8 | UTF-16LE |
|---|---|---|
| 탭 | `09` | `09 00` |
| `mailto:` | `6D 61 69 6C 74 6F 3A` | `6D 00 61 00 69 00 6C 00 74 00 6F 00 3A 00` |
| `FindAccountResult` | `46 69 6E 64 41 63 63 6F 75 6E 74 52 65 73 75 6C 74` | 각 바이트 뒤에 `00` |

1. `logs` 폴더의 파일을 사본으로 뜹니다.
2. 파일의 첫 바이트로 인코딩을 정합니다. 읽는 법은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.
3. 첫 줄에서 탭 바이트로 나뉜 필드 이름을 셉니다. 새 Outlook 1.2026.707.300 에서는 25개입니다. 필드 수가 다르면 판이 다른 로그입니다.
4. `mailto:` 바이트를 찾아 실행 인자 행을 봅니다. 그 행의 `Time` 필드를 UTC 로 읽습니다.
5. `FindAccountResult` 바이트를 찾아 계정 조회 결과를 봅니다.
6. 지워진 로그의 조각은 미할당 영역에서 같은 바이트로 찾아볼 수 있습니다([삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)).

### 공개 도구로 한 번

- 로그는 표 계산 프로그램이나 명령줄 도구에서 탭으로 열을 나눠 봅니다. 첫 줄을 머리글로 씁니다.
- `EBWebView` 안의 파일은 크롬 계열 브라우저 기록을 읽는 공개 도구로 엽니다. 도구가 브라우저가 아닌 프로필 폴더를 받는지 먼저 확인합니다.
- `UserSettings.json`·`sentinel.json` 은 JSON 을 보여 주는 편집기로 엽니다.
- `settings.dat` 는 [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) 의 방법으로 엽니다.

> 그림 자리: `Olk` 폴더와 패키지 데이터 폴더의 구성, 파일마다 알려 주는 것(앱 판·시작과 종료 시각·계정·웹 화면 기록)을 한 장에 놓은 그림

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [스토어 앱 설치 목록](../system-account/appx-staterepository.md) | 새 Outlook 패키지가 언제 깔렸고 판이 무엇인지 |
| [프리패치](../execution/prefetch/index.md) · [BAM·DAM](../execution/background-activity-moderator.md) | `olk.exe` 실행 흔적이 로그의 시작 시각과 맞는지 |
| [SRUM](../execution/system-resource-usage-monitor/index.md) | 로그의 시작·종료 시각 사이에 이 앱이 네트워크를 쓴 양 |
| [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) | `EBWebView` 의 웹 화면 기록과 쿠키 |
| [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) | 패키지 `settings.dat` 의 설정 값 |
| [윈도 알림 기록](../execution/wpndatabase-db.md) | 새 메일 알림이 남았는지 |
| [아웃룩](outlook/index.md) | 같은 사용자가 클래식 Outlook 이나 PST 를 함께 썼는지 |
| [Windows 메일 앱](hxstore.md) | 옛 메일 앱에서 옮겨 왔는지 |
| [USN 변경 저널](../filesystem/usnjrnl.md) | 로그 파일이 생기고 지워진 때 |

메일로 누구와 연락했는지 정리하는 순서는 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다.

## 실습

**직접 만든 가상 머신** 에서 해 봅니다. 공개 문서에 나와 있지 않은 부분을 직접 확인하는 실습입니다.

1. 새 Outlook 을 깔고 계정 하나를 더합니다. `Olk` 폴더와 패키지 데이터 폴더에 무엇이 새로 생깁니까?
2. 제목에 고유한 낱말을 넣은 메일을 받습니다. 디스크 전체에서 그 낱말을 찾아보십시오. 어느 파일에서 나옵니까?
3. 오프라인 설정을 켜고 2번을 다시 해 보십시오. `IndexedDB` 폴더가 생깁니까?
4. 앱을 여러 번 켜고 끕니다. `logs` 폴더의 파일은 몇 개까지 늘어납니까? 오래된 파일은 언제 지워집니까?
5. 웹페이지의 `mailto:` 링크를 눌러 앱을 엽니다. 로그의 실행 인자 행에 무엇이 남습니까?
6. 클래식 Outlook 에서 "Try the new Outlook" 토글을 켭니다. 레지스트리의 어느 값이 바뀝니까?

**공개 시험 데이터(NIST CFReDS 등)** 가운데 Windows 11 이미지에서도 해 봅니다.

1. `Microsoft.OutlookForWindows` 패키지 폴더가 있습니까? 판은 무엇입니까?
2. `logs` 폴더가 있다면 `Application starting` 행은 몇 개입니까? 시각을 UTC 로 읽으면 다른 사용 흔적과 맞습니까?
3. `FindAccountResult` 행의 `totalAccounts` 값은 무엇입니까?

## 참고 문헌

1. Microsoft 지원, "Outlook for Windows: The Future of Mail, Calendar and People on Windows 11" — https://support.microsoft.com/en-us/office/outlook-for-windows-the-future-of-mail-calendar-and-people-on-windows-11-715fc27c-e0f4-4652-9174-47faa751b199
