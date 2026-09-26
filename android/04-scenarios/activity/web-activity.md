---
title: "웹 사용 행위 재구성"
parent: "시나리오 · 행위 재구성"
nav_order: 1600
---

# 웹 사용 행위 재구성 (Web Activity)

## 조사 질문

"그날 밤 어떤 사이트를 봤나", "이 주소는 직접 쳐서 들어갔나, 링크를 눌러 들어갔나", "이 파일은 어느 페이지에서 내려받았나", "무엇을 검색했나" 같은 질문에 답하는 흐름입니다. 브라우저 방문 기록을 중심에 두고 검색어, 다운로드, 공용 저장 공간의 파일, 앱 사용 기록을 차례로 겹쳐 한 사람이 웹에서 한 일을 시간 순서대로 정리하는 방법을 다룹니다.

기록은 "이 브라우저 프로필에 이 주소를 이 시각에 방문한 행이 있다", "이 주소에서 이 파일을 받은 행이 있다" 까지 알려 주지만, 페이지를 실제로 읽었는지, 그 방문이 이 기기에서 일어났는지 계정 동기화로 들어왔는지는 기록에 따라 알 수도 있고 모를 수도 있습니다. 사람을 가리는 문제는 [그 시각에 폰을 쓴 사람이 누구인가](user-attribution.md) 에서 이어 갑니다.

## 먼저 확인할 것

- **어떤 브라우저가 있나** — 기본 브라우저는 `dumpsys package` 의 Known Packages 아래 기본 브라우저 역할(Browser) 값(예: `com.android.chrome`)으로 봅니다. 기본 브라우저가 아닌 브라우저도 설치돼 있을 수 있으므로 [설치된 앱](../../02-artifacts/app-usage/packages/index.md) 에서 삼성 인터넷, Firefox, 네이버 앱 같은 브라우저 계열 패키지를 모두 뽑아 둡니다.
- **시간대** — 파일마다 시각 기준이 다르고 대부분 UTC 기준 값이라, 현지 시각으로 옮기려면 기기 시간대가 필요합니다([시각 값](../../01-foundations/value-decoding/time-values.md), [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md)).
- **사용자와 계정** — 브라우저가 계정에 로그인돼 동기화를 쓰고 있었다면 다른 기기의 방문이 섞일 수 있습니다. 로그인된 계정은 [계정](../../02-artifacts/system-account/accounts/index.md) 에서 확인합니다.
- **수집 범위** — 브라우저 프로필 파일은 앱 데이터 영역에 있어 adb 일반 권한으로는 보이지 않습니다. `History` 같은 SQLite 파일은 `-wal`·`-journal` 파일과 함께 확보해야 최근 기록을 놓치지 않습니다([SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | Chromium 계열 `History` 의 `urls`·`visits` 표 | 방문한 주소와 제목, 방문 시각, 방문 경로(링크·직접 입력 등), 머문 시간 | [크롬](../../02-artifacts/browsers/chrome/index.md), [삼성 인터넷](../../02-artifacts/browsers/samsung-internet.md) |
| 2 | `History` 의 `keyword_search_terms` 표 | 검색창에 넣은 검색어와 그 결과 주소 | [크롬](../../02-artifacts/browsers/chrome/index.md) |
| 3 | `History` 의 `downloads`·`downloads_url_chains` 표 | 내려받은 파일의 저장 위치, 시작한 탭 주소, 리다이렉트를 거친 실제 주소 | [크롬](../../02-artifacts/browsers/chrome/index.md) |
| 4 | Firefox 계열 `places.sqlite` | 방문 기록과 이 기기에서 한 방문인지 여부 | [그 밖의 브라우저](../../02-artifacts/browsers/other-browsers.md) |
| 5 | MediaStore 다운로드 행과 `/sdcard/Download` | 기기에 남은 파일과 받은 주소 | [미디어 저장소](../../02-artifacts/media/mediastore/index.md), [공용 저장 공간](../../01-foundations/storage/shared-storage.md) |
| 6 | 앱 안 웹뷰, 자동 완성, 쿠키 | 브라우저가 아닌 앱 안에서 연 페이지, 입력한 값, 로그인 흔적 | [크롬](../../02-artifacts/browsers/chrome/index.md), [네이버 앱](../../02-artifacts/browsers/naver.md) |
| 7 | usagestats 의 브라우저 화면 이벤트 | 그 시각에 브라우저 화면이 앞에 있었는지 | [어떤 앱을 언제 썼나](app-usage.md) |

브라우저 계열마다 파일 위치와 시각 기준이 달라 아래처럼 정리합니다.

| 브라우저 | 방문 기록 파일 | 시각 기준 | 비고 |
|---|---|---|---|
| Chrome | `app_chrome/Default/History` [1] | 1601-01-01 UTC 부터의 마이크로초 [1] | 기록 만료 기준은 90일입니다(`kExpireDaysThreshold`, 현행 Chromium) [4] |
| 삼성 인터넷 | `app_sbrowser/Default/History` [1] | Chrome 과 같습니다 [1] | ALEAPP 는 Chrome 과 같은 SQL 로 읽고, 이 행의 브라우저 이름을 "Browser" 로 적습니다 [1] |
| 앱 안 웹뷰 | 각 앱의 `app_webview/Default/History` [1] | Chrome 과 같습니다 [1] | ALEAPP 는 브라우저 이름 칸에 그 앱의 패키지 이름을 적습니다 [1] |
| Firefox 계열 | `files/places.sqlite` [7] | 유닉스 밀리초 [7] | 데스크톱 Firefox 의 마이크로초와 다릅니다 [7] |

## 분석 흐름

1. **방문 기록을 시간 순서로 폅니다.** Chromium 계열 `History` 에서 `visits` 표의 한 행이 방문 한 번이고, `visit_time`, `from_visit`(이전 방문), `transition`, `visit_duration`(마이크로초) 칸을 `urls` 표의 주소·제목과 이어 봅니다 [1]. `urls` 표에는 `visit_count`, `typed_count`, `last_visit_time` 같은 합계 칸도 있지만 [1], 사건 시각을 정할 때는 방문 한 번 한 번이 남은 `visits` 표를 씁니다.

2. **방문 경로를 풉니다.** `transition` 값의 낮은 1바이트(`transition & 0xff`)가 방문 유형이고, 주로 보는 값은 아래와 같습니다 [1]. 이 밖에 2 AUTO_BOOKMARK, 5 GENERATED, 9 KEYWORD 같은 값도 있으며 [1], 보고서에는 이름 그대로 옮깁니다.

   | 값 | 이름 | 뜻 |
   |---|---|---|
   | 0 | LINK | 링크를 눌러 들어감 |
   | 1 | TYPED | 주소창에 주소를 입력함 |
   | 7 | FORM_SUBMIT | 입력 양식을 제출함 |
   | 8 | RELOAD | 새로 고침 |

   `from_visit` 로 앞 방문을 따라가면 "검색 결과에서 링크를 눌러 이 페이지로 왔다" 같은 사슬을 이을 수 있습니다. 상위 비트 `0xC0000000` 은 클라이언트·서버 리다이렉트 두 비트를 묶은 마스크라서 [1], 리다이렉트로 거쳐 간 주소는 사용자가 직접 연 페이지와 나눠 적습니다.

3. **검색어를 붙입니다.** `keyword_search_terms` 표의 `term` 칸이 검색어이고 `url_id` 로 `urls` 표와 이어집니다 [1]. 검색어 행에는 시각이 따로 없어 이어진 주소의 방문 시각을 가져다 씁니다.

4. **다운로드를 잇습니다.** `downloads` 표에서 `target_path`(최종 저장 위치), `tab_url`(다운로드를 시작한 탭의 주소), `referrer`, `start_time`·`end_time`, `received_bytes`·`total_bytes`, `opened`(한 번이라도 열었으면 1) 칸을 읽습니다 [3]. `downloads_url_chains` 표의 `chain_index` 0 이 처음 요청한 주소이고 가장 큰 번호가 리다이렉트 뒤 최종 주소라서 [3], 사용자가 누른 링크와 실제로 파일이 온 서버를 나눠 볼 수 있습니다. 다운로드 행을 지우면 이 두 표의 같은 ID 행이 함께 지워집니다 [3].

5. **기기에 남은 파일과 맞춥니다.** `target_path` 의 파일이 아직 있는지 확인하고, MediaStore 의 `is_download`, `download_uri`, `referer_uri` 칸 [8] 과 `owner_package_name`(이 파일을 넣은 패키지) [9] 을 함께 봅니다. 브라우저 기록에는 없는데 `Download` 폴더에 파일이 있다면 다른 앱이 받은 파일일 수 있습니다.

6. **Firefox 계열이 있으면 따로 읽습니다.** `places.sqlite` 의 `moz_historyvisits` 표에는 `is_local` 칸이 있어, 이 기기에서 추가한 방문은 참, 동기화로 들어온 방문은 거짓입니다 [6]. `moz_places` 표도 방문 횟수와 마지막 방문 시각을 로컬과 원격으로 나눠 둡니다 [6]. Chromium 계열 `History` 에서 동기화로 들어온 방문을 가르는 칸은 공개 분석 자료가 없으므로, Chrome·삼성 인터넷 기록은 계정 동기화가 켜져 있었는지와 함께 해석합니다.

7. **앱 안에서 연 페이지를 봅니다.** 웹뷰를 쓰는 앱은 자기 패키지 아래 `app_webview/Default/` 에 `History`·`Cookies`·`Web Data` 를 남길 수 있습니다 [1]. `Web Data` 의 자동 완성 표에는 `date_created`·`date_last_used` 칸이 있고 값은 유닉스 초라서 [2], `History` 의 마이크로초와 단위가 다릅니다.

8. **앱 사용 기록으로 화면을 확인합니다.** 방문 시각 앞뒤로 브라우저 패키지의 `ACTIVITY_RESUMED`~`ACTIVITY_PAUSED` 구간이 있는지 봅니다. 방문 기록은 브라우저 안의 일이고 화면이 앞에 있었는지는 앱 사용 기록이 보여 주므로, 방문 시각에 브라우저 화면 구간이 없다면 그 방문이 어떻게 생겼는지 따로 따져 봅니다. 방법은 [어떤 앱을 언제 썼나](app-usage.md) 에 있고, 여러 기록을 한 축에 놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

> 그림 자리: 시간 축 위에 검색어 → LINK 방문 → 리다이렉트 → 다운로드 시작·끝 → Download 폴더 파일로 이어지는 사슬을 화살표로 그리고, 아래 줄에 브라우저 화면 구간을 겹친 그림

## 흔한 오판

**`urls.last_visit_time` 하나로 방문 시각을 적는 오판**이 흔합니다. 이 칸은 마지막 방문 하나만 보여 주므로 사건 시각의 방문은 `visits` 표에서 찾습니다 [1].

**방문을 모두 "사용자가 연 페이지" 로 세는 경우**도 있습니다. 리다이렉트와 새로 고침(RELOAD)도 방문 행으로 남으므로 `transition` 을 풀어 나눠 적습니다 [1].

**시각 단위를 섞는 실수**가 자주 나옵니다. Chromium `History` 는 1601년 기준 마이크로초, Chromium `Web Data` 자동 완성은 유닉스 초, Android Firefox 는 유닉스 밀리초입니다 [1][2][7].

**ALEAPP 결과의 "Browser" 를 Chrome 으로 읽는 경우**가 있습니다. 이 이름은 삼성 인터넷 경로에서 나온 행입니다 [1].

**기록이 없다고 "방문하지 않았다" 로 단정하는 것**도 조심합니다. Chromium 은 90일이 지난 기록을 지우기 시작하고 [4], 사용자가 방문 기록을 지웠을 수도 있습니다. Chrome 의 시크릿 탭 상태는 `cryptonito` 로 시작하는 파일에 암호화해 저장하므로 [5] 일반 방문 기록과 같은 방식으로 읽히지 않고, 이 핸드북은 그 파일을 푸는 방법을 다루지 않습니다. 삼성 인터넷 비밀 모드 기록이 어디에 남는지는 공개 자료가 없어 검체에서 확인합니다.

## 보고서 문장 예

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 피의자는 ○○ 사이트에 접속했다. | Chrome 방문 기록(`History` 의 `visits` 표)에 ○○일 ○○:○○(UTC ○○:○○) 주소 ○○ 방문 행이 있고, 방문 유형은 주소창 입력(TYPED)입니다. 이 브라우저는 ○○ 계정에 로그인돼 있어 다른 기기의 방문이 동기화됐을 가능성을 배제하지 못했습니다. |
| 피의자는 ○○를 검색한 뒤 파일을 받았다. | 같은 `History` 의 `keyword_search_terms` 표에 검색어 "○○" 행이 있고 이 행과 이어진 주소의 방문 시각은 ○○:○○ 이며, ○○:○○ `downloads` 표에 저장 위치 ○○, 시작한 탭 주소 ○○ 인 다운로드 행이 있으며, 이 파일은 확보 시점에 `/sdcard/Download` 에 남아 있었습니다. |
| 그날은 인터넷을 쓰지 않았다. | 확보한 브라우저 기록(Chrome, ○○)에서 ○○일 방문 행은 찾지 못했습니다. Chromium 은 90일이 지난 기록을 지우고, 시크릿 탭과 다른 브라우저의 기록은 이 확인에 들어 있지 않습니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [크롬](../../02-artifacts/browsers/chrome/index.md), [삼성 인터넷](../../02-artifacts/browsers/samsung-internet.md), [네이버 앱](../../02-artifacts/browsers/naver.md), [그 밖의 브라우저](../../02-artifacts/browsers/other-browsers.md), [미디어 저장소](../../02-artifacts/media/mediastore/index.md)
- 기반 구조: [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), [시각 값](../../01-foundations/value-decoding/time-values.md), [공용 저장 공간](../../01-foundations/storage/shared-storage.md)
- 이어지는 시나리오: [어떤 앱을 언제 썼나](app-usage.md), [자료를 밖으로 보냈나](../exfiltration/data-exfiltration/index.md), [지운 대화와 사진 찾기](deleted-content.md)
- 기법: [타임라인 작성](../../03-techniques/analysis/timeline/index.md), [콘텐츠 검색](../../03-techniques/analysis/content-search.md)

## 참고 문헌

1. ALEAPP scripts/artifacts/chrome.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chrome.py
2. ALEAPP scripts/artifacts/chromeAutofill.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chromeAutofill.py
3. Chromium components/history/core/browser/download_database.cc — https://raw.githubusercontent.com/chromium/chromium/main/components/history/core/browser/download_database.cc
4. GitHub 코드 검색 "kExpireDaysThreshold" (chromium/chromium) — 결과 줄: components/history/core/browser/history_backend.h `static constexpr int kExpireDaysThreshold = 90;` — https://github.com/search?q=repo%3Achromium%2Fchromium+kExpireDaysThreshold&type=code
5. Chromium TabStateFileManager.java — https://raw.githubusercontent.com/chromium/chromium/main/chrome/browser/tabpersistence/android/java/src/org/chromium/chrome/browser/tabpersistence/TabStateFileManager.java
6. Mozilla application-services, components/places/sql/create_shared_schema.sql (main) — https://raw.githubusercontent.com/mozilla/application-services/main/components/places/sql/create_shared_schema.sql
7. ALEAPP 저장소 scripts/artifacts (main, 커밋 c044fe5): firefox.py 등 — https://github.com/abrignoni/ALEAPP
8. AOSP MediaProvider — DatabaseHelper.java (main) — https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/DatabaseHelper.java
9. AOSP MediaProvider — apex/framework/java/android/provider/MediaStore.java (main) — https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/apex/framework/java/android/provider/MediaStore.java
