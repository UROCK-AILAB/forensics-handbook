---
title: "크롬"
parent: "아티팩트 · 인터넷·브라우저"
nav_order: 820
has_children: true
has_toc: false
---

# 크롬 (Chrome for Android)

## 한 줄 요약

Chrome for Android(패키지 com.android.chrome)는 앱 데이터 폴더의 `app_chrome/Default/` 아래 SQLite 파일에 방문 기록과 다운로드, 쿠키, 자동 완성을 남기고, 열린 탭은 따로 탭 상태 파일에 저장합니다 [1][2][3][4].

## 왜 중요한가

관찰한 기기에서는 `dumpsys package` 출력의 "Known Packages" 아래 "Browser:" 항목에 com.android.chrome 이 나와 기본 브라우저 역할을 Chrome 이 맡고 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 웹에서 무엇을 찾고, 어디에 들어가고, 무엇을 받았는지를 묻는 사건이면 기본 브라우저가 무엇인지 먼저 확인하고, Chrome 이라면 이 앱의 파일부터 봅니다.

한 앱 안에서도 파일마다 시각 기준이 다르다는 점을 먼저 알아 두어야 합니다. History 와 Cookies 는 1601-01-01 UTC 부터의 마이크로초이고 [1][2], Web Data 의 자동 완성 시각은 ALEAPP 가 유닉스 초로 읽으며 [3], 탭 상태 파일의 시각 칸은 이름이 …Millis 인 long 값이지만 기준 에포크를 확인하지 못했습니다 [4]. 각 페이지의 "시각 해석" 절에서 칸마다 따로 다룹니다.

같은 폴더 이름을 다른 앱도 씁니다. Brave, Edge, Opera 같은 Chromium 계열 앱도 `app_chrome` 이라는 이름을 쓰기 때문에 폴더 구조만으로는 어느 브라우저인지 알 수 없고, 경로 안의 패키지 폴더 이름으로 가려야 합니다 [1]. WebView 를 쓰는 다른 앱도 자기 패키지 아래 `app_webview/Default/` 에 History, Cookies, Web Data 를 남기고, ALEAPP 는 이것도 같은 파서로 읽어 브라우저 이름 칸에 그 앱의 패키지 이름을 적습니다 [1][2][3]. 도구 결과에 Chrome 이 아닌 이름이 섞여 나오면 이 두 경우인지 먼저 봅니다.

## 한눈에 보기

경로는 모두 Chrome 앱 데이터 폴더(com.android.chrome 패키지 폴더) 아래를 기준으로 적었습니다. 앱 데이터 폴더 자체는 [앱 데이터 폴더 구조 (/data/data·/data/user)](../../../01-foundations/storage/app-data-layout.md) 페이지를 봅니다.

| 위치 | 형식 | 알려 주는 것 | Android 버전 |
|---|---|---|---|
| `app_chrome/Default/History` | SQLite | 방문 기록(urls, visits), 검색어(keyword_search_terms) [1] | ALEAPP 표본 Android 10~16 [1] |
| `app_chrome/Default/History` | SQLite | 다운로드(downloads, downloads_url_chains, downloads_slices) [1][5] | 같은 파일, 오래된 DB 에는 일부 칸이 없음 [1] |
| 탭 상태 폴더(`tabs` 로 만든 폴더) | Chrome 전용 파일 | 저장 시점에 열려 있던 탭의 URL, 탭을 연 앱, 시크릿 탭 파일 [4] | 현행 Chromium 소스 기준 |
| `app_chrome/Default/Cookies` | SQLite | 도메인별 쿠키와 만든·읽은 시각 [2] | 경로 이동 여부는 확인 못 함 |
| `app_chrome/Default/Web Data` | SQLite | 입력란에 넣은 값, 주소 프로필 [3] | 옛 형식과 새 형식이 있음 [3] |

같은 Chromium 계열인 삼성 인터넷(com.sec.android.app.sbrowser)은 `app_sbrowser/Default/History` 를 남기고 ALEAPP 가 Chrome 과 같은 SQL 로 읽습니다 [1]. 삼성 기기에서는 Chrome 과 삼성 인터넷이 함께 깔려 있는 경우가 있어서(ALEAPP 의 Android 14 삼성 표본이 그런 예입니다 [1]) 두 앱을 따로 봅니다. 관찰 기기에 삼성 인터넷이 깔려 있는지는 관찰 메모에서 가려져 있어 확인하지 못했습니다.

루팅하지 않은 기기에서 일반 adb 권한으로 이 폴더를 읽을 수 있는지는 확인하지 못했습니다. 앱 데이터 폴더를 확보하는 방법은 [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 봅니다. 저장된 비밀번호(Login Data)와 Top Sites, Shortcuts, Bookmarks 같은 다른 파일의 Android 경로와 표 이름도 이번에 확인하지 않았고, 저장된 암호는 [저장된 암호 (Google 비밀번호 관리자·Samsung Pass)](../../credentials-security/saved-passwords.md) 페이지에서 다룹니다.

> 그림 자리: Chrome 앱 데이터 폴더 아래 app_chrome/Default 의 세 SQLite 파일과 탭 상태 폴더, 각 파일에서 이어지는 하위 페이지를 한 장에 그린 구조도

## 읽는 순서

1. [방문 기록 (History)](history.md) — urls·visits·검색어 표, 방문 경로를 알려 주는 transition 값, 1601년 기준 마이크로초를 바꾸는 계산과 헥스 예시, 기록 만료 기준, 저널 파일이 있을 때 읽는 법을 다룹니다.
2. [탭과 세션 (Tabs·Sessions)](tabs-sessions.md) — 탭 상태 폴더와 파일 이름 규칙, 옛 형식 TabState 안의 값 순서, 탭을 연 앱의 ID, 암호화된 시크릿 탭 파일을 다룹니다.
3. [다운로드 (Downloads)](downloads.md) — downloads 표의 칸과 상태·위험 판정·중단 사유 값, 실제 파일 주소를 남기는 URL 사슬 표, 저장된 SHA-256 으로 파일을 대조하는 법을 다룹니다.
4. [쿠키와 자동 완성 (Cookies·Autofill)](cookies-autofill.md) — cookies 표, 자동 완성 입력값과 주소 프로필의 옛·새 형식, 유닉스 초를 쓰는 Web Data 시각을 다룹니다.

## 함께 볼 페이지

- [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md)
- [삼성 인터넷 (Samsung Internet)](../samsung-internet.md), [그 밖의 브라우저 (웨일·파이어폭스)](../other-browsers.md), [네이버 앱 (NAVER)](../naver.md)
- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md), [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../../01-foundations/value-decoding/time-values.md)
- [패키지 이름과 UID (Package Name·UID)](../../../01-foundations/value-decoding/package-uid.md)
- [앱 사용 기록 (usagestats)](../../app-usage/usagestats/index.md)
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. ALEAPP `scripts/artifacts/chrome.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chrome.py
2. ALEAPP `scripts/artifacts/chromeCookies.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chromeCookies.py
3. ALEAPP `scripts/artifacts/chromeAutofill.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chromeAutofill.py
4. Chromium `TabStateFileManager.java` — https://raw.githubusercontent.com/chromium/chromium/main/chrome/browser/tabpersistence/android/java/src/org/chromium/chrome/browser/tabpersistence/TabStateFileManager.java
5. Chromium `components/history/core/browser/download_database.cc` — https://raw.githubusercontent.com/chromium/chromium/main/components/history/core/browser/download_database.cc
