---
title: "삼성 인터넷"
parent: "아티팩트 · 인터넷·브라우저"
nav_order: 870
---

# 삼성 인터넷 (Samsung Internet)

## 한 줄 요약

삼성 인터넷(패키지 com.sec.android.app.sbrowser)은 앱 데이터 폴더의 `app_sbrowser/Default/` 아래에 Chrome 과 이름이 같은 History, Cookies, Web Data 같은 파일을 남기고, 공개 도구 ALEAPP 는 이 파일들을 Chrome 과 같은 SQL 로 읽습니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

이 앱은 Google Play 한국어 페이지에 "삼성 브라우저" 라는 이름으로 올라 있고 개발자는 Samsung Electronics Co., Ltd. 이며, 영문 이름은 "Samsung Internet" 입니다 [4][5]. 이 핸드북에서는 "삼성 인터넷" 으로 부릅니다.

Chrome 계열이라는 단서는 사용자 에이전트 (User Agent) 문자열에 있습니다. 앱 이름과 버전 뒤에 `Chrome/버전` 부분이 붙는 모양이고, 이 Chrome/ 부분은 Chrome 기반 웹 브라우저에만 들어갑니다 [5]. 예시는 다음과 같습니다.

```
Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/117.0.0.0 Mobile Safari/537.36
```

삼성 인터넷 버전과 Chromium 버전을 맞춰 놓은 공식 표는 없습니다 [5].

사용자가 페이지를 열면 History 파일에 방문 주소와 방문 한 건 한 건, 검색어, 다운로드가 쌓이고, 사이트가 쿠키를 심으면 Cookies 파일에, 입력란에 값을 넣으면 Web Data 파일에 남습니다 [1][2]. 삼성 인터넷에는 비밀 모드, 스마트 추적 차단(사용자 활동을 추적하는 제3의 도메인을 가려내 쿠키 접근을 막는 기능), 유해 사이트 경고, 콘텐츠 차단 같은 개인정보 관련 기능이 있습니다 [4]. 비밀 모드에서 방문한 기록이 같은 History 에 남는지, 따로 저장되는지, 어느 폴더에 있는지는 실제 기기로 확인해야 합니다.

## 위치와 버전별 차이

경로는 모두 삼성 인터넷 앱 데이터 폴더(com.sec.android.app.sbrowser 패키지 폴더) 아래를 기준으로 적었고, 앱 데이터 폴더 자체는 [앱 데이터 폴더 구조 (/data/data·/data/user)](../../01-foundations/storage/app-data-layout.md) 페이지를 봅니다. 아래 표는 ALEAPP 가 `app_sbrowser` 경로 패턴으로 찾는 파일입니다. 삼성 인터넷 전용 모듈은 없고, Chrome 용 모듈들이 이 경로를 함께 찾습니다 [2][3].

| 위치 (`app_sbrowser/Default/` 아래) | ALEAPP 가 읽는 내용 |
|---|---|
| `History` | 방문 기록과 방문, 검색어, 다운로드(urls, visits, keyword_search_terms, downloads 표) [1] |
| `Cookies` | 쿠키 [2] |
| `Web Data` | 자동 완성 값, 결제·카드 정보 [2] |
| `Bookmarks` | 북마크(JSON 파일로 읽음) [2] |
| `Login Data` | 저장된 로그인 정보 [2] |
| `Top Sites` | 자주 가는 사이트 [2] |
| `Media History` | chromeMediaHistory 모듈이 읽는 파일 [2] |
| `DIPS` | chromeDIPS 모듈이 읽는 파일 [2] |
| `Network Action Predictor` | chromeNetworkActionPredictor 모듈이 읽는 파일 [2] |
| `Offline Pages/metadata/OfflinePages.db` | chromeOfflinePages 모듈이 읽는 파일 [2] |

ALEAPP Network Action Predictor 모듈의 시험 표본(2026-09-11 기준 Android 42개)에서는 34개에 이 파일이 있었고, 사본은 모두 `app_chrome/Default` 나 `app_sbrowser/Default` 아래에 있었습니다 [2]. 표본마다 행이 하나도 없는 파일도 많아서, Login Data 와 Top Sites 가 0행인 표본이 여러 개였습니다 [2].

ALEAPP 는 표본 버전과 상관없이 한 가지 경로 패턴으로 찾습니다. ALEAPP 표본에 들어 있던 삼성 인터넷의 버전 코드(versionCode)는 다음과 같습니다.

| 표본의 Android 버전 | 삼성 인터넷 versionCode | 비고 |
|---|---|---|
| Android 13 | 1300067502 | s20fe 표본 [2] |
| Android 14 | 1260103502, 1290059502 | [1] |
| Android 15 | 1280509502 | [1] |
| Android 16 | 1300067502 | Pixel 8 Pro 표본(hc_pixel8pro_a16) [1] |

Android 16 표본이 Pixel 기기라서, 삼성 기기가 아닌 폰에서도 삼성 인터넷 파일이 나올 수 있다는 점을 알 수 있습니다 [1].

기본 브라우저가 무엇인지는 `dumpsys package` 출력의 "Known Packages" 아래 "Browser:" 항목에 나옵니다(Chrome 이 기본이면 com.android.chrome). 삼성 인터넷의 앱 데이터 폴더를 확보하는 방법은 [모바일 증거 확보 (Acquisition)](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 봅니다.

## 구조

History 는 Chrome 과 같은 표 이름을 쓰고 ALEAPP 도 같은 SQL 을 돌리기 때문에, urls·visits·keyword_search_terms·downloads 표의 열과 방문 경로 값은 [크롬 (Chrome for Android)](chrome/index.md) 페이지와 그 하위 페이지에서 한 번만 설명합니다. SQLite 파일 자체의 구조는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md) 페이지를 봅니다.

삼성 인터넷에서 따로 알아 둘 점은 두 가지입니다. 첫째로 ALEAPP 는 `app_sbrowser` 경로에서 나온 행의 브라우저 이름 열에 "Samsung Internet" 이 아니라 "Browser" 를 적어서, 보고서에서 "Browser" 로 표시된 행을 삼성 인터넷으로 읽어야 합니다 [1][2]. 둘째로 ALEAPP 의 탭 모듈(chromeSessionTabs.py, `Sessions/Tabs_<번호>`)과 동기화 세션 모듈(chromeSyncSessions.py, `Sync Data/LevelDB`)은 `app_chrome` 경로만 찾아서, 삼성 인터넷의 열린 탭은 도구 결과에 나오지 않습니다 [2]. 열린 탭이 어디에 남는지는 실제 기기에서 확인해야 합니다.

사용자 리뷰에는 "페이지 저장" 기능이 나옵니다. 저장한 페이지가 `Offline Pages` 폴더에 남는지, 삼성 계정으로 북마크나 탭을 동기화할 때 기기 안 어느 파일에 흔적이 남는지도 실제 기기에서 확인해야 합니다.

> 그림 자리: 삼성 인터넷 앱 데이터 폴더 아래 app_sbrowser/Default 의 파일들을 Chrome 의 app_chrome/Default 와 나란히 놓고, 같은 이름의 파일과 ALEAPP 가 붙이는 브라우저 이름("Browser"·"Chrome")을 함께 보여 주는 비교도

## 증거로서 의미

**증명하는 것.** `app_sbrowser/Default/History` 에 방문 행이 있으면 이 기기의 삼성 인터넷 프로필에 그 주소를 그 시각에 방문했다는 기록이 남아 있다는 뜻이고, 같은 기기의 Chrome 기록과는 폴더 이름으로 구분할 수 있습니다. downloads 표의 행은 삼성 인터넷이 그 주소에서 파일을 받는 작업을 기록했다는 뜻입니다 [1].

**증명하지 못하는 것.** 기록은 기기에서 누가 폰을 들고 있었는지 알려 주지 않습니다. 비밀 모드 기록이 어디에 남는지 알려진 자료가 없어서, History 에 없다는 사실만으로 그 시간에 삼성 인터넷을 쓰지 않았다고 말할 수 없습니다. 삼성 계정 동기화가 어떤 흔적을 남기는지도 알려지지 않아서, 방문 행이 이 기기에서 직접 연 것인지 다른 기기에서 넘어온 것인지도 이 파일만으로는 단정하지 않습니다. 보고서에는 "이 시각에 삼성 인터넷 방문 기록에 이 주소가 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

History 의 시각 열(last_visit_time, visit_time, start_time 등)은 Chromium 과 같이 1601-01-01 UTC 부터 흐른 마이크로초로 읽고, ALEAPP 도 `app_chrome` 과 `app_sbrowser` 에 같은 변환을 씁니다 [1]. 값은 UTC 라서 보고서에 현지 시각으로 옮길 때는 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 페이지를 참고해 기기 시간대를 따로 확인합니다. 열마다 언제 바뀌는지는 Chrome 페이지에서 다루고, 시각 형식 전반은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

## 함정과 한계

도구 결과의 브라우저 이름부터 조심합니다. 삼성 인터넷 행은 "Browser" 로 나오고 [1], Chrome·Brave·Edge·Opera 로 따로 이름을 붙이는 경우를 빼면 `app_chrome` 을 쓰는 Chromium 파생 브라우저는 경로 안의 패키지 폴더 이름이 그대로 이름 열에 들어가며, WebView 를 쓰는 앱도 `app_webview/Default/History` 를 남기면 그 앱의 패키지 이름으로 나옵니다 [1]. 이름 열만 보지 말고 경로 열에서 패키지 폴더를 확인합니다.

History 를 읽을 때 저널 파일도 함께 봅니다. ALEAPP 는 이름이 정확히 "History" 인 파일만 열고 `-journal` 같은 파일은 건너뛰는데, 비어 있지 않은 롤백 저널이 남은 History 는 읽기 전용으로 열면 실패할 수 있습니다(SQLite 가 저널을 되감으려면 파일에 써야 하기 때문입니다) [1]. ALEAPP 는 이런 파일을 건너뛰고 기록만 남기므로, 도구 결과에 삼성 인터넷 행이 없으면 로그에서 건너뛴 파일이 있는지 먼저 봅니다. Magisk 미러 경로(`.magisk…mirror`)의 사본은 중복이라 ALEAPP 가 건너뜁니다 [1].

빈 파일도 흔합니다. 표본 여러 개에서 Login Data 와 Top Sites 가 0행이었기 때문에 [2], 행이 없다는 사실만으로 누군가 지웠다고 보지 않습니다. 비밀 모드 기록, 열린 탭, 저장한 페이지, 삼성 계정 동기화 흔적의 위치는 실제 기기에서 직접 찾아야 합니다.

## 직접 분석해 보기

**헥스로 한 번.** 시각 열의 값은 Chrome 과 같은 방법으로 바꿉니다. 아래는 명세로 만든 예시이고 실제 기기에서 가져온 값이 아닙니다. visit_time 열에 정수 13353724800000000 이 들어 있다고 하면 16진수로는 `0x2F71245721E000` 이고, 이를 1,000,000 으로 나눈 초에서 1601-01-01 과 1970-01-01 사이의 초(11,644,473,600)를 빼면 유닉스 초 1709251200 이 되어 2024-03-01 00:00:00 UTC 로 읽힙니다. 이 계산을 단계별로 따라가는 헥스 예시는 [크롬 (Chrome for Android)](chrome/index.md) 의 방문 기록 하위 페이지에 있습니다.

**공개 도구로 한 번.** 먼저 파일 경로에 `com.sec.android.app.sbrowser` 와 `app_sbrowser` 가 함께 들어 있는지 확인하고, 사본을 만든 뒤 sqlite3 로 표 목록과 행 수를 봅니다.

```
sqlite3 History ".tables"
sqlite3 History "SELECT count(*) FROM urls; SELECT count(*) FROM visits; SELECT count(*) FROM keyword_search_terms; SELECT count(*) FROM downloads;"
```

그다음 ALEAPP 를 돌려 Chrome 계열 보고서에서 브라우저 이름이 "Browser" 인 행을 모으고, 행 수가 위에서 센 숫자와 맞는지 대조합니다. 숫자가 다르면 건너뛴 저널 파일이 있는지 확인합니다. 도구 결과를 원본과 맞춰 보는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지를 봅니다.

## 교차 검증

- [크롬 (Chrome for Android)](chrome/index.md) — 같은 기기에 Chrome 과 삼성 인터넷이 함께 있으면 두 기록을 나눠 보고, 기본 브라우저가 무엇인지는 [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) 의 `dumpsys package` "Known Packages" 에서 확인합니다.
- [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) — `dumpsys usagestats` 이벤트 줄에는 time=, type=, package=, class= 필드가 있고 ACTIVITY_RESUMED·ACTIVITY_PAUSED·ACTIVITY_STOPPED 같은 종류가 나옵니다. package= 가 com.sec.android.app.sbrowser 인 줄의 시각이 방문 시각 앞뒤에 있는지 맞춰 봅니다.
- [공용 저장 공간 (Shared Storage·/sdcard)](../../01-foundations/storage/shared-storage.md) — downloads 표에 적힌 파일이 /sdcard 의 Download 폴더에 실제로 있는지 봅니다. Download 폴더는 여러 앱이 함께 쓰므로, 폴더에 파일이 있다는 것만으로 어느 브라우저가 받았는지는 알 수 없습니다.
- [설치된 앱 (packages.xml)](../app-usage/packages/index.md) — 삼성 인터넷의 설치·업데이트 시각과 버전을 확인합니다.
- [저장된 암호 (Google 비밀번호 관리자·Samsung Pass)](../credentials-security/saved-passwords.md) — Login Data 를 볼 때 함께 봅니다.
- [웹 사용 행위 재구성 (Web Activity)](../../04-scenarios/activity/web-activity.md), [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)

## 실습

공개된 증거물 이미지나 직접 만든 시험 기기 가운데 삼성 인터넷이 깔린 이미지를 골라 아래 질문을 풀어 봅니다.

1. 이미지 안에서 `app_sbrowser/Default/History` 를 찾고, 경로의 패키지 폴더가 com.sec.android.app.sbrowser 인지 확인합니다. 같은 이미지에 `app_chrome/Default/History` 도 있다면 두 파일의 가장 이른 방문 시각과 가장 늦은 방문 시각은 각각 언제입니까?
2. ALEAPP 보고서에서 브라우저 이름이 "Browser" 인 행의 수와 sqlite3 로 센 visits 표의 행 수가 맞습니까? 맞지 않는다면 로그에 건너뛴 파일이 있습니까?
3. downloads 표의 파일 가운데 공용 저장 공간에 실제로 남아 있는 파일은 몇 개이고, 남아 있지 않은 파일은 어떤 상태 값으로 기록돼 있습니까?
4. usagestats 에서 삼성 인터넷이 화면에 떠 있던 시간대와 History 방문 시각이 겹칩니까?

## 참고 문헌

1. ALEAPP `scripts/artifacts/chrome.py` (main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chrome.py
2. ALEAPP 저장소 `scripts/artifacts` (main, 커밋 c044fe5, 2026-09-24). chromeAutofill.py, chromeBookmarks.py, chromeCookies.py, chromeCreditCards.py, chromeDIPS.py, chromeLoginData.py, chromeMediaHistory.py, chromeNetworkActionPredictor.py, chromeOfflinePages.py, chromePaymentsCustomerData.py, chromeSessionTabs.py, chromeSyncSessions.py, chromeTopSites.py — https://github.com/abrignoni/ALEAPP
3. ALEAPP `scripts/artifacts` 폴더 목록(GitHub API) — https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
4. Google Play, "삼성 브라우저" 상세 페이지(한국어) — https://play.google.com/store/apps/details?id=com.sec.android.app.sbrowser&hl=ko
5. Samsung Developer, "Samsung Internet User Agent Information" — https://developer.samsung.com/internet/user-agent-string-format.html
