---
title: "방문 기록"
parent: "크롬"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 830
---

# 방문 기록 (History)

## 한 줄 요약

Chrome for Android 의 방문 기록은 프로필 폴더의 `History` SQLite 파일에 URL 별 요약(urls 표)과 방문 한 건씩의 기록(visits 표), 주소창 검색어(keyword_search_terms 표)로 나뉘어 들어 있고, 시각은 1601-01-01 UTC 부터 센 마이크로초로 적습니다 [1].

## 무엇을 기록하나 · 왜 생기나

Chrome 은 페이지를 열 때마다 방문 한 건을 visits 표에 적고, 같은 URL 의 누적 정보(제목, 방문 횟수, 마지막 방문 시각)는 urls 표 한 행에 모읍니다 [1]. 방문마다 "어떻게 들어왔는지"를 적는 전환 값(transition)과 바로 앞 방문을 가리키는 번호(from_visit)가 붙어서, 사용자가 주소창에 직접 입력했는지, 링크를 눌렀는지, 리다이렉트로 넘어갔는지를 가려 볼 수 있습니다 [1].

같은 `History` 파일에는 다운로드 표도 들어 있지만, 다운로드는 [다운로드 (Downloads)](downloads.md) 페이지에서 따로 다룹니다. 열려 있던 탭은 이 파일이 아니라 탭 상태 파일에 남고, [탭과 세션 (Tabs·Sessions)](tabs-sessions.md) 페이지에 정리했습니다.

## 위치와 버전별 차이

파일은 Chrome 앱 데이터 폴더 아래 `app_chrome/Default/History` 입니다 [1]. 패키지 이름과 앱 데이터 폴더, 같은 폴더 구조를 쓰는 다른 Chromium 계열 앱과 WebView 를 가려내는 법은 [크롬 (Chrome for Android)](index.md) 허브에 모았습니다. 공개 도구 ALEAPP 는 이름이 정확히 `History` 인 파일만 열고 `History-journal` 같은 곁 파일은 건너뜁니다 [1].

| 구분 | 내용 |
|---|---|
| ALEAPP 가 이 파서로 시험한 표본 | Android 10(galaxys10), Android 14(삼성 기기에 Chrome 과 삼성 인터넷), Android 16(Pixel 8 Pro) 등 [1] |
| 표본의 방문 행 수 | Android 10 표본 291행, Android 14 표본 58행, Android 16 표본 39행 [1] |
| 삼성 인터넷 | 같은 Chromium 계열의 방문 기록 파일을 따로 남깁니다. 경로는 [크롬 (Chrome for Android)](index.md) 허브, 내용은 [삼성 인터넷 (Samsung Internet)](../samsung-internet.md) 페이지를 봅니다 |

표본의 행 수는 기기와 사용 기간에 따라 크게 달라지는 예일 뿐이고, 기준치로 쓰지 않습니다.

## 구조

### urls 표

URL 한 개에 한 행이고, ALEAPP 는 아래 칸을 읽습니다 [1].

| 칸 | 뜻 |
|---|---|
| id | URL 번호. visits.url 과 keyword_search_terms.url_id 가 이 값을 가리킵니다 |
| url, title | 주소와 페이지 제목 |
| visit_count | 방문 횟수 |
| typed_count | 주소창에 직접 입력해 들어간 횟수를 세는 칸으로 보입니다 |
| last_visit_time | 마지막 방문 시각(1601-01-01 UTC 부터의 마이크로초) |
| hidden | 0 이면 목록에 보이는 기록, 1 이면 숨긴 기록 |

### visits 표

방문 한 번에 한 행입니다 [1].

| 칸 | 뜻 |
|---|---|
| visit_time | 방문 시각(1601-01-01 UTC 부터의 마이크로초) |
| url | urls.id 를 가리킵니다 |
| from_visit | 바로 앞 방문의 visits.id. 이 값을 따라가면 "어디서 왔는지"를 이을 수 있습니다 |
| transition | 어떻게 들어왔는지를 적은 값(아래 표) |
| visit_duration | 머문 시간(마이크로초). ALEAPP 는 1,000,000 으로 나눠 시:분:초로 보이고 0 이면 빈칸으로 둡니다 |

transition 은 낮은 1바이트(`transition & 0xff`)가 핵심 유형이고, 높은 비트들은 덧붙는 한정자(qualifier)입니다 [1].

| 핵심 유형(낮은 1바이트) | 이름 |
|---|---|
| 0 | LINK |
| 1 | TYPED |
| 2 | AUTO_BOOKMARK |
| 3 | AUTO_SUBFRAME |
| 4 | MANUAL_SUBFRAME |
| 5 | GENERATED |
| 6 | START_PAGE |
| 7 | FORM_SUBMIT |
| 8 | RELOAD |
| 9 | KEYWORD |
| 10 | KEYWORD_GENERATED |

| 한정자 비트 | 이름 |
|---|---|
| 0x00800000 | BLOCKED |
| 0x01000000 | FORWARD_BACK |
| 0x02000000 | FROM_ADDRESS_BAR |
| 0x04000000 | HOME_PAGE |
| 0x08000000 | FROM_API |
| 0x10000000 | CHAIN_START |
| 0x20000000 | CHAIN_END |
| 0x40000000 | CLIENT_REDIRECT |
| 0x80000000 | SERVER_REDIRECT |

0xC0000000 은 CLIENT_REDIRECT 와 SERVER_REDIRECT 두 비트를 한꺼번에 보는 마스크(IS_REDIRECT_MASK)이고 따로 된 한정자가 아닙니다 [1].

### 검색어

keyword_search_terms 표에는 url_id(urls.id 를 가리킴)와 term 칸이 있고, ALEAPP 는 urls 와 이어 붙여 검색어와 URL, last_visit_time 을 함께 보여 줍니다 [1]. ALEAPP 의 "Search Terms" 결과는 이 표와 다르게, urls.url 에 `search?q=` 가 들어간 행에서 `q=` 뒤의 값을 잘라 URL 디코딩한 것이라서 [1], 두 결과는 출처가 다르다는 점을 알고 씁니다.

## 증거로서 의미

| 기록 | 말할 수 있는 것 | 말할 수 없는 것 |
|---|---|---|
| visits 한 행 | 그 시각에 이 프로필의 Chrome 이 그 URL 을 불러온 기록이 있다 | 사용자가 화면을 보았는지, 누가 기기를 쥐고 있었는지 |
| transition 이 TYPED, FROM_ADDRESS_BAR 한정자 | 주소창 입력으로 들어간 방문으로 기록되었다 | 사람이 한 글자씩 쳤는지, 자동 완성을 골랐는지 |
| transition 에 리다이렉트 비트 | 앞 페이지에서 넘어간 방문이다 | 사용자가 그 페이지를 고른 것 |
| urls 의 visit_count·last_visit_time | 남아 있는 기록 기준의 누적 방문과 마지막 방문 | 전체 기간의 방문 횟수(오래된 기록은 만료되거나 지워질 수 있음) |
| keyword_search_terms 의 term | 그 검색어가 URL 과 함께 기록되었다 | 검색 결과에서 무엇을 열었는지(visits 로 따로 확인) |
| 기록이 없음 | — | 그 사이트에 가지 않았다는 것 |

보고서에는 "이 시각에 이 URL 방문 기록이 있다" 처럼 표가 말하는 만큼만 씁니다. 방문자를 특정하는 문제는 [그 시각에 폰을 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 시나리오를 봅니다.

## 시각 해석

visit_time 과 last_visit_time 은 1601-01-01 00:00:00 UTC 부터 센 마이크로초이고 [1], 1,000,000 으로 나눈 뒤 1601-01-01 과 1970-01-01 사이의 초(11,644,473,600)를 빼면 유닉스 초가 됩니다. 값 자체가 UTC 기준이라 현지 시각으로 보이려면 기기의 시간대를 따로 확인하고, 시간대 기록은 [시간대와 시각 설정](../../system-account/time-zone.md) 페이지에 있습니다. 여러 시각 형식을 바꾸는 법은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지에 모았습니다.

visits 에는 방문마다 시각이 남고 urls 에는 마지막 방문 시각 하나만 남아서, 같은 URL 을 여러 번 방문한 경우 앞선 방문 시각은 visits 에서만 볼 수 있습니다 [1].

## 함정과 한계

Chromium 의 기록 만료 기준(kExpireDaysThreshold)은 90일이고, HistoryBackend 가 이 일수를 기준으로 오래된 기록을 지우기 시작합니다 [2]. Android 판에 같은 90일이 적용되는지, 다른 기기에서 동기화된 방문이 이 파일에 들어오는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 따라서 오래전 방문이 없다는 사실만으로 사용자가 지웠다고 판단하지 않습니다.

원본 `History` 옆에 `-journal` 파일이 있으면 읽기 전용으로 열 때 실패할 수 있는데, SQLite 가 저널을 되감으려면 파일에 써야 하기 때문입니다. ALEAPP 는 이런 파일을 건너뛰고 기록을 남깁니다 [1]. 원본은 건드리지 말고 사본을 만들어 곁 파일과 함께 열고, 저널과 지운 행의 흔적은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)와 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md) 페이지를 봅니다. ALEAPP 는 Magisk 미러 경로(`.magisk` … `mirror`)에 있는 사본은 중복이라 건너뜁니다 [1].

hidden 이 1 인 행은 ALEAPP 가 "Yes" 로 표시하니 [1], 도구 화면에서 숨긴 기록을 빼고 세지 않았는지 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. 2025-01-01 00:00:00 UTC 를 Chrome 시각으로 바꾸면 (1,735,689,600 + 11,644,473,600) × 1,000,000 = 13,380,163,200,000,000 이고, 16진수로 `0x2F89300292A000` 입니다. SQLite 레코드 안에서는 이 값이 8바이트 큰 쪽 먼저(big-endian) 정수로 들어가서 아래처럼 보입니다.

```
00 2F 89 30 02 92 A0 00    visit_time = 13380163200000000
                           ÷ 1,000,000 = 13380163200 초
                           − 11644473600 = 1735689600 (유닉스 초)
                           = 2025-01-01 00:00:00 UTC
```

transition 도 같은 방법으로 풉니다. 예를 들어 값이 `0x32000001`(10진수 838860801)이면 낮은 1바이트가 1 이라 TYPED 이고, 높은 비트는 FROM_ADDRESS_BAR(0x02000000), CHAIN_START(0x10000000), CHAIN_END(0x20000000)가 켜진 것입니다. 이 값도 명세로 만든 예시입니다. SQLite 레코드 헤더를 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) 페이지를 봅니다.

### 공개 도구로 한 번

사본을 sqlite3 명령줄이나 DB Browser for SQLite 로 열어 아래처럼 방문과 URL, 앞 방문을 한 번에 봅니다. 결과는 ALEAPP 의 Web Visits 결과와 나란히 놓고 행 수와 시각이 맞는지 확인합니다.

```sql
SELECT v.id,
       datetime(v.visit_time/1000000 - 11644473600, 'unixepoch') AS visit_utc,
       u.url, u.title,
       v.transition & 0xff AS core_type,
       printf('0x%08X', v.transition) AS transition_hex,
       v.from_visit,
       v.visit_duration/1000000.0 AS duration_sec
FROM visits v JOIN urls u ON u.id = v.url
ORDER BY v.visit_time;
```

## 교차 검증

같은 URL 이 열린 탭으로 남아 있는지는 [탭과 세션 (Tabs·Sessions)](tabs-sessions.md), 방문 직후 파일을 받았는지는 [다운로드 (Downloads)](downloads.md), 그 사이트의 쿠키와 입력값은 [쿠키와 자동 완성 (Cookies·Autofill)](cookies-autofill.md) 페이지에서 확인합니다. Chrome 이 그 시각에 실제로 화면에 나와 있었는지는 [앱 사용 기록 (usagestats)](../../app-usage/usagestats/index.md)으로 맞춰 보고, 전체 흐름은 [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md)과 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) 페이지를 봅니다. 문자로 받은 링크를 눌렀는지 따지는 사건이라면 [스미싱 흔적 (Smishing)](../../../04-scenarios/incident/smishing.md)을 함께 봅니다.

## 실습

Chrome 이 깔린 공개 Android 검체(NIST CFReDS 등에서 고른 것)로 아래 질문을 풀어 봅니다.

1. visits 에서 transition 의 낮은 1바이트가 1(TYPED)인 방문을 모두 뽑고, 그 가운데 FROM_ADDRESS_BAR 비트가 켜진 것이 몇 건인지 셉니다.
2. from_visit 를 따라가 리다이렉트 비트가 켜진 방문이 어느 방문에서 이어졌는지 사슬로 그려 봅니다.
3. urls.visit_count 와 visits 에 남은 그 URL 의 행 수가 다른 경우를 찾고, 차이가 왜 생길 수 있는지 적어 봅니다.
4. keyword_search_terms 의 검색어와 ALEAPP "Search Terms" 결과를 비교해 한쪽에만 있는 항목을 찾아봅니다.

## 참고 문헌

1. ALEAPP `scripts/artifacts/chrome.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chrome.py
2. GitHub 코드 검색 "kExpireDaysThreshold" (chromium/chromium), `components/history/core/browser/history_backend.h` 결과 줄 — https://github.com/search?q=repo%3Achromium%2Fchromium+kExpireDaysThreshold&type=code
