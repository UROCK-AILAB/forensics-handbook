---
title: "네이버 앱"
parent: "아티팩트 · 인터넷·브라우저"
nav_order: 880
---

# 네이버 앱 (NAVER)

## 한 줄 요약

네이버 앱(패키지 com.nhn.android.search)은 검색과 뉴스, 쇼핑, 결제를 한데 묶은 앱이고, 공개 도구에 전용 파서가 없고 검색어와 방문 기록이 기기 안 어느 파일에 남는지도 아직 확인되지 않아서, 분석은 패키지 폴더를 직접 열어 보는 데서 시작합니다 [1][3].

## 무엇을 기록하나 · 왜 생기나

Google Play 한국어 상세 페이지를 보면 네이버 앱의 개발자는 NAVER Corp. 이고, 페이지에는 "안드로이드OS 9.0 이상의 환경에서 설치하는 것을 권장" 한다고 적혀 있습니다 [3]. 소개 글은 앱을 홈피드, 클립(숏폼), 콘텐츠(뉴스 등), 네이버플러스 스토어(쇼핑), 마이의 다섯 공간으로 나누어 설명하고, "마이" 에서는 인증, 결제도구, 결제·예약 주문 목록, 찜한 상품, 저장한 장소 같은 "내 활동내역" 을 모아 본다고 적습니다 [3]. 검색창에는 AI탭 버튼이 있어 렌즈(이미지 검색)와 음악검색을 쓰고, 음성검색과 내 주변 검색도 있으며, Wear OS 기기도 지원합니다 [3].

필수 접근 권한으로는 위치, 카메라, 파일 및 미디어, 마이크, 연락처, 전화, 신체활동, 알림(Android 13 이상)이 적혀 있습니다 [3]. 전화 권한은 네이버 인증서, 비밀번호 없이 로그인, 네이버페이에서 기기 전화번호를 확인하는 데 쓰고, 신체활동 권한은 만보기 걸음 수에 씁니다 [3]. Play 데이터 보안 항목에는 제3자와 공유할 수 있는 데이터로 "개인 정보, 금융 정보 외 5개", 수집할 수 있는 데이터로 "위치, 개인 정보 외 11개" 가 적혀 있습니다 [3].

이 기능 목록은 어떤 종류의 흔적을 찾아볼지 정하는 데 쓰고, 기기에 그 파일이 있다는 근거로 쓰지 않습니다. 개발사 소개 글에는 저장 경로나 DB 구조가 나오지 않아서, 검색어와 방문 기록이 SQLite 에 남는지 설정 XML 에 남는지, 표와 칸 이름이 무엇인지는 확인하지 못했습니다. 방문 기록을 남기지 않는 모드 같은 기능이 있는지와 그 흔적도 확인하지 못했습니다.

## 위치와 버전별 차이

지금까지 확인한 것과 확인하지 못한 것을 나누면 다음과 같습니다.

| 항목 | 상태 | 근거 |
|---|---|---|
| 패키지 이름 | com.nhn.android.search | Play 상세 페이지 주소의 id [3] |
| 공개 도구 전용 파서 | ALEAPP 에 없음 | ALEAPP 모듈 목록 [1] |
| 검색어·방문 기록 파일 | 확인 못 함 | — |
| WebView 방문 기록(`app_webview/Default/History`) | 있다면 ALEAPP 가 읽음, 실제로 남는지는 확인 못 함 | ALEAPP chrome.py [2] |
| 방문 기록을 남기지 않는 모드 | 확인 못 함 | — |
| 네이버 계정 서버 쪽 검색 기록 | 기기 밖 자료라 이번에 확인하지 않음 | — |

WebView 줄은 따로 설명이 필요합니다. ALEAPP 는 `app_webview/Default/History` 를 가진 모든 앱을 Chromium 파서로 읽고 브라우저 이름 칸에 그 앱의 패키지 이름을 적습니다 [2]. 네이버 앱 안에서 연 웹 페이지가 WebView 로 열려 이런 파일을 남긴다면 ALEAPP 결과에 com.nhn.android.search 라는 이름으로 나오겠지만, 실제로 그런지는 확인하지 못했습니다. WebView 파일의 구조와 읽는 법은 [크롬 (Chrome for Android)](chrome/index.md) 페이지에서 다룹니다.

Android 버전이나 앱 버전에 따라 파일 배치가 어떻게 달라지는지는 파일 자체를 확인하지 못해 정리할 수 없습니다. 루팅하지 않은 기기에서 adb 일반 권한으로 이 앱의 데이터 폴더를 읽을 수 있는지도 확인하지 못했고, 폴더를 확보하는 방법은 [모바일 증거 확보 (Acquisition)](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 봅니다.

관찰한 기기의 settings system 키 이름에는 `naver_sports_state` 와 `support_nowbar_naver_sports` 가 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 키 이름만 보였고 값은 가려져 있었으며, 이 키를 One UI 의 Now Bar 기능이 쓰는지 네이버 앱이 쓰는지, 값이 무엇을 뜻하는지는 확인하지 못했습니다. 네이버 앱이 이 기기에 깔려 있는지도 관찰 메모에서 패키지 이름이 가려져 확인하지 못했습니다. 설정 값 전반은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 페이지를 봅니다.

## 구조

확인한 파일 구조가 없어서 이 절은 찾는 순서만 적습니다.

1. 앱 데이터 폴더(com.nhn.android.search 패키지 폴더)를 확보하고, 폴더 배치는 [앱 데이터 폴더 구조 (/data/data·/data/user)](../../01-foundations/storage/app-data-layout.md) 페이지를 참고해 하위 폴더를 차례로 엽니다.
2. 파일마다 형식을 먼저 가립니다. SQLite 는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md), 설정 XML 은 [설정 XML과 SharedPreferences (XML·SharedPreferences)](../../01-foundations/data-formats/shared-preferences.md), 그 밖의 바이너리는 [프로토콜 버퍼 (Protocol Buffers)](../../01-foundations/data-formats/protobuf.md) 와 [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../01-foundations/data-formats/leveldb-indexeddb.md) 페이지를 봅니다.
3. `app_webview/Default/History` 가 있으면 Chrome 과 같은 방법으로 읽습니다.
4. 검색어나 주소가 들어 있는 표와 칸을 찾으면, 시험 기기에서 검색을 몇 번 해 보고 행이 늘어나는지 확인한 뒤에 그 칸의 뜻을 보고서에 씁니다.

앱 데이터를 처음 보는 앱에 이 순서를 적용하는 방법은 [앱 데이터 분석 (App Data Analysis)](../../03-techniques/analysis/app-data-analysis/index.md) 페이지에서 자세히 다룹니다.

## 증거로서 의미

**증명하는 것.** 네이버 앱 자체의 파일 구조를 모르는 지금은, 이 앱이 설치돼 있었다는 사실과 언제 화면에 떠 있었는지를 시스템 기록으로 확인하는 데까지가 안전합니다. WebView 방문 기록 파일이 있으면 그 파일에 적힌 주소를 그 시각에 네이버 앱 안에서 열었다는 기록으로 읽을 수 있습니다 [2].

**증명하지 못하는 것.** 방문 기록 파일을 찾지 못했다고 해서 네이버 앱으로 검색하지 않았다고 말할 수 없습니다. 검색 기록이 기기 밖 네이버 계정에 따로 남을 수 있지만 이번에 확인하지 않았고, 계정 쪽 자료는 [클라우드 데이터 (Google Takeout 등)](../../03-techniques/acquisition/cloud-data.md) 페이지의 방법으로 따로 확보해야 합니다. Chrome 이나 삼성 인터넷에서 네이버 웹사이트로 검색했다면 그 기록은 그 브라우저의 파일에서 찾습니다. Play 데이터 보안 항목의 "수집할 수 있는 데이터" 는 개발사가 스스로 밝힌 내용이고, 기기 안에 그 데이터가 파일로 남았다는 근거가 되지 않습니다.

## 시각 해석

네이버 앱 파일의 시각 형식은 확인하지 못했습니다. WebView 방문 기록 파일이라면 ALEAPP 가 Chromium 과 같이 1601-01-01 UTC 부터의 마이크로초로 읽습니다 [2]. 그 밖의 파일에서 시각으로 보이는 정수를 만나면 자릿수로 초·밀리초·마이크로초를 짐작하고, 시험 기기에서 알고 있는 시각의 동작을 한 번 해 본 뒤 값과 맞춰 봅니다. 형식별 변환은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

## 함정과 한계

ALEAPP 모듈 가운데 이름에 "naver" 가 들어간 것은 LINE(jp.naver.line.android)을 읽는 line.py 뿐이라서 [1], 그 결과를 네이버 앱 기록으로 읽으면 안 됩니다. LINE 은 [라인 (LINE)](../messengers/line.md) 페이지에서 다룹니다. 같은 회사의 웹 브라우저인 웨일은 패키지가 다른 별도 앱이고 [그 밖의 브라우저 (웨일·파이어폭스)](other-browsers.md) 페이지에서 다룹니다.

settings system 의 `naver_sports_state` 같은 키 이름은 네이버 앱이 깔려 있다는 근거로 쓰지 않습니다. 앞에서 적었듯이 이 키를 쓰는 주체가 확인되지 않았습니다.

WebView 파일은 ALEAPP 결과에 패키지 이름으로 섞여 나오기 때문에, com.nhn.android.search 행이 보이면 경로에 `app_webview` 가 들어 있는지 확인하고 Chrome 행과 섞지 않습니다 [2].

## 직접 분석해 보기

**헥스로 한 번.** 구조를 확인한 파일이 없어서 이 페이지에는 헥스 예시를 만들지 않았습니다. 패키지 폴더에서 파일을 찾으면 첫 몇 바이트로 형식부터 가리고, 형식별 헥스 읽는 법은 위 "구조" 절에 걸어 둔 기반 구조 페이지를 따릅니다. WebView 방문 기록 파일의 시각 값 헥스 예시는 [삼성 인터넷 (Samsung Internet)](samsung-internet.md) 과 Chrome 페이지에 있습니다.

**공개 도구로 한 번.** ALEAPP 를 돌린 뒤 Chrome 계열 보고서에서 브라우저 이름이 com.nhn.android.search 인 행이 있는지 봅니다. 행이 있으면 경로 칸에서 `app_webview/Default/History` 를 확인하고, 없으면 도구가 이 앱을 읽지 않은 것이지 기록이 없다는 뜻은 아니라서 위 "구조" 절의 순서대로 직접 봅니다.

## 교차 검증

- [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) — 관찰 기기의 `dumpsys usagestats` 이벤트 줄에는 time=, type=, package=, class= 칸이 있었고, ACTIVITY_RESUMED·ACTIVITY_PAUSED 같은 화면 전환 이벤트와 shortcutId= 칸이 붙은 SHORTCUT_INVOCATION 이벤트가 보였습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). package= 가 com.nhn.android.search 인 줄로 앱이 화면에 떠 있던 시간대를 잡습니다.
- [설치된 앱 (packages.xml)](../app-usage/packages/index.md) — 설치·업데이트 시각과 버전을 확인합니다.
- [알림 기록 (Notification History)](../app-usage/notification-history.md) — 앱이 보낸 알림 제목과 시각을 봅니다.
- [네이버 지도 (NAVER Map)](../location/naver-map.md), [네이버 MYBOX (MYBOX)](../mail-cloud/mybox.md), [네이버 밴드 (BAND)](../korean-apps/band.md) — 같은 회사의 다른 앱을 쓴 기록이 있으면 시간대를 함께 맞춰 봅니다.
- [웹 사용 행위 재구성 (Web Activity)](../../04-scenarios/activity/web-activity.md), [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)

## 실습

공개 검체나 직접 만든 시험 기기 가운데 네이버 앱이 깔린 이미지를 골라 아래 질문을 풀어 봅니다.

1. com.nhn.android.search 패키지 폴더 아래에 SQLite 파일은 몇 개이고, 그 가운데 주소나 검색어로 보이는 문자열이 들어 있는 표는 어느 것입니까?
2. `app_webview/Default/History` 가 있습니까? 있다면 ALEAPP 보고서에서 그 행들은 어떤 브라우저 이름으로 나옵니까?
3. 시험 기기에서 네이버 앱으로 알고 있는 시각에 검색을 세 번 한 뒤 다시 확보했을 때, 행이 늘어난 파일과 칸은 어느 것이고 그 칸의 값은 어떤 시각 형식입니까?
4. usagestats 에서 네이버 앱이 화면에 떠 있던 시간대와 3번에서 찾은 시각이 겹칩니까?

## 참고 문헌

1. ALEAPP `scripts/artifacts` 폴더 목록(GitHub API) — https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
2. ALEAPP `scripts/artifacts/chrome.py` (main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chrome.py
3. Google Play, "네이버 - NAVER" 상세 페이지(한국어) — https://play.google.com/store/apps/details?id=com.nhn.android.search&hl=ko
