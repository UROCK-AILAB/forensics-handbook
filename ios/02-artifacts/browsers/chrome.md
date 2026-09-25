---
title: "크롬"
parent: "아티팩트 · 인터넷·브라우저"
nav_order: 770
---

# 크롬 (Chrome for iOS)

## 한 줄 요약

아이폰용 크롬은 방문 기록·내려받기·검색어를 데스크톱 크롬과 같은 크로미움 형식 SQLite 파일(`History` 등)에 적고, 이 파일은 앱 컨테이너의 `Application Support` 안에 있습니다.

## 무엇을 기록하나 · 왜 생기나

크롬은 사용자 데이터 폴더 (User Data Directory) 에 프로필 데이터를 모아 두고, 그 안에는 방문 기록·북마크·쿠키 같은 파일이 들어갑니다. 프로필은 사용자 데이터 폴더 아래 하위 폴더에 저장하고, 보통 이름이 `Default` 입니다 [2]. 크로미움 공식 문서에 따르면 iOS 에서는 이 폴더를 앱 샌드박스의 `Application Support` 안에 두고, 크롬은 `Library/Application Support/Google/Chrome`, 크로미움은 `Library/Application Support/Chromium` 을 씁니다 [2].

화면을 그리는 엔진에는 따로 정해진 규칙이 있습니다. App Store 심사 지침 2.5.6 은 웹을 탐색하는 앱이 알맞은 WebKit 프레임워크와 WebKit JavaScript 를 쓰도록 정하고 있고, EU·일본용 앱은 다른 브라우저 엔진을 쓰는 권한 (entitlement) 을 신청할 수 있습니다 [6]. 이 규칙은 엔진에 관한 것이고, 크롬의 기록 파일이 크로미움 형식으로 `Application Support` 에 있다는 것은 크로미움 문서와 MVT 가 알려 주는 별개의 사실입니다 [2][4]. 사파리 `History.db` 와는 파일도 표도 다르니 크롬 기록은 크롬 컨테이너를 따로 열어 봅니다. 사파리는 [사파리 (Safari)](safari/index.md) 에서 다룹니다.

## 위치와 버전별 차이

번들 ID (Bundle ID) 는 `com.google.chrome.ios` 이고, 기기 안의 방문 기록 파일 경로는 다음과 같습니다 [4].

```
private/var/mobile/Containers/Data/Application/*/Library/Application Support/Google/Chrome/Default/History
```

`*` 자리는 앱마다 붙는 컨테이너 UUID 입니다. 번들 ID 와 컨테이너의 관계는 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에서 설명합니다.

로컬 백업에서는 도메인이 `AppDomain-com.google.chrome.ios`, 상대 경로가 `Library/Application Support/Google/Chrome/Default/History` 입니다. MVT 는 이 파일을 백업 파일 ID `faf971ce92c3ac508c018dce1bef2a8b8e9838f1` 로 찾는데 [4], 이 값은 `AppDomain-com.google.chrome.ios-Library/Application Support/Google/Chrome/Default/History` 문자열의 SHA-1 과 같습니다(이 핸드북에서 직접 계산해 맞춰 봄). 백업 파일 ID 를 만드는 규칙은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에 있습니다.

iLEAPP 의 `chrome.py` 는 `History` 에서 방문 기록·방문·검색·내려받기·키워드 검색어를, `Web Data` 에서 자동 완성 항목과 프로필을 읽고, 그 밖에 다음 파일도 읽습니다 [1].

```
Bookmarks
Cookies
Login Data
Top Sites
Media History
Network Action Predictor
Offline Pages/metadata/OfflinePages.db
```

이 스크립트는 `*/Chrome/Default/History*` 같은 경로 패턴으로 파일을 찾고, 안드로이드·데스크톱과 함께 쓰는 공용 스크립트라서 `app_sbrowser`·`app_opera`·`Chromium` 경로도 같이 봅니다 [1]. 이 파일들이 아이폰 크롬 컨테이너에 모두 생기는지, 로컬 백업에 모두 들어가는지는 확인하지 못했습니다. MVT 가 백업 파일 ID 로 `History` 를 찾으니 `History` 는 백업에 들어간다고 볼 수 있지만 [4], 암호화하지 않은 백업에도 들어가는지는 확인하지 못했습니다.

아이폰 크롬의 캐시 폴더, 탭·세션 저장 파일, 컨테이너 안에 WebKit 데이터 폴더(`Library/WebKit/WebsiteData` 등)가 따로 생기는지도 확인하지 못했습니다. WebKit 을 쓰는 앱에 생길 수 있는 파일은 [네이버 앱](naver.md) 에 정리했습니다. 이 핸드북이 읽은 백업(확인 범위: iPhone 13 mini, iOS 27.0)에서는 다른 회사 앱 이름을 가려서 크롬 설치 여부를 알 수 없었고, 그래서 위 경로는 관찰로 확인한 값이 아닙니다.

iOS 버전별 차이는 확인한 자료가 없습니다. 엔진 쪽 차이는 지역에 따라 갈리는데, EU·일본에서 크롬이 실제로 다른 엔진(Blink)을 쓰는지는 확인하지 못했습니다.

## 구조

`History` 는 SQLite 파일이고 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 방식으로 읽습니다. iLEAPP·MVT 가 읽는 표와 칸은 다음과 같습니다.

| 파일 | 표 | 칸 |
|---|---|---|
| `History` | `urls` | `id`, `url`, `title`, `visit_count`, `typed_count`, `last_visit_time`, `hidden` [1] |
| `History` | `visits` | `id`, `url`(`urls.id` 를 가리킴), `visit_time`, `visit_duration`, `from_visit` [1][4] |
| `History` | `downloads` | `start_time` 등 [1] |
| `History` | `keyword_search_terms` | `url_id`, `term` [1] |
| `Cookies` | `cookies` | `last_access_utc` 등 [1] |
| `Login Data` | `logins` | `username_value`, `password_value`, `date_created` [1] |
| `Web Data` | `autofill` | `name`, `value`, `date_created`, `date_last_used`, `count` [1] |
| `Top Sites` | `top_sites` | `url`, `url_rank`, `title` [1] |

`urls` 는 주소마다 한 줄이고 `visits` 는 방문마다 한 줄이라서, 방문 시각을 주소와 함께 보려면 `visits.url` 과 `urls.id` 를 이어 붙입니다. MVT 는 `urls.id`, `urls.url`, `visits.id`, `visits.visit_time`, `visits.from_visit` 를 이렇게 이어 `visit_time` 순으로 뽑습니다 [4]. 검색어는 `keyword_search_terms.url_id` 를 `urls.id` 와 이어 붙여 어느 검색 결과 주소에서 나온 검색어인지 봅니다 [1].

`Login Data` 의 `password_value` 가 아이폰에서 암호화돼 있는지, 키가 어디 있는지는 확인하지 못했습니다. 저장된 암호 전반은 [저장된 암호](../credentials-security/saved-passwords.md) 를 봅니다.

## 증거로서 의미

**증명하는 것.** `visits` 줄은 그 크롬 프로필에 그 주소를 연 방문 기록이 남아 있다는 것을 보여 주고, `visit_time` 으로 그 시각을 알 수 있습니다. `keyword_search_terms` 는 검색어 문자열을, `downloads` 는 내려받기를 시작한 시각을 알려 줍니다. `Login Data` 의 `username_value` 와 `date_created` 로는 저장한 계정 이름과 저장한 시각을 봅니다.

**증명하지 못하는 것.** 방문 기록 한 줄만으로는 사람이 화면을 봤는지, 누가 폰을 들고 있었는지 알 수 없습니다. 구글 계정 동기화를 켜면 다른 기기에서 방문한 기록이 이 파일에 섞이는지, 섞인다면 구분하는 칸이 있는지는 확인하지 못했습니다. 그래서 "이 아이폰에서 방문했다" 고 쓰기 전에 아래 교차 검증 표의 기기 쪽 흔적과 맞춰 봐야 합니다. 시크릿 모드로 본 사이트는 이 파일에 남지 않습니다(아래 함정 참고).

보고서에는 "이 사이트에 접속했다" 보다 "크롬 방문 기록에 이 시각에 이 주소를 연 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

크롬 시각은 1601-01-01 부터 센 마이크로초이고, `last_visit_time`, `visit_time`, `start_time`, `last_access_utc`, `date_created`(`logins`) 가 이 기준을 씁니다 [1]. iLEAPP 는 다음 식으로 바꿉니다 [1].

```sql
datetime(visit_time/1000000 + strftime('%s','1601-01-01'), 'unixepoch')
```

`strftime('%s','1601-01-01')` 은 -11644473600 이라서, 초로 바꾼 값에서 11644473600 을 빼면 유닉스 시각이 됩니다. 이 식은 `localtime` 을 붙이지 않았으니 결과를 UTC 로 읽고, 현지 시각이 필요하면 [시간대와 시각 설정](../system-account/time-zone.md) 으로 시간대를 확인한 뒤 따로 더합니다. MVT 도 `visit_time` 을 크롬 시각 변환 함수로 바꿉니다 [4].

같은 크롬 파일 안에도 기준이 다른 칸이 있습니다. `Web Data` 의 `autofill.date_created`, `autofill.date_last_used` 는 유닉스 초라서 `datetime(x,'unixepoch')` 로 바로 바꿉니다 [1]. `visit_duration` 은 시각이 아니라 마이크로초 단위 길이이고, iLEAPP 는 1000000 으로 나눠 시:분:초로 보여 줍니다 [1].

사파리 `History.db` 는 기준이 다른 시각 값을 씁니다. 여러 기준을 한곳에서 비교하려면 [시각 값](../../01-foundations/value-decoding/time-values.md) 을 봅니다.

## 함정과 한계

시크릿 (Incognito) 모드 세션이 끝나면 크롬은 사이트 데이터와 방문한 사이트 기록을 남기지 않습니다. 다만 시크릿 중에 저장한 북마크와 내려받은 파일은 시크릿을 나가도 남습니다 [5]. 그래서 방문 기록에 없는 사이트의 북마크나 내려받은 파일이 있으면 시크릿 사용을 의심해 볼 수 있지만, 시크릿을 썼다는 흔적(설정 키 등)이 기기에 남는지는 확인하지 못했습니다. 크롬에는 시크릿 탭 잠금 설정도 있어서, 켜 두면 크롬을 떠날 때 시크릿 탭을 잠그고 다시 볼 때 Face ID·Touch ID·암호 같은 기기 인증을 요구합니다 [5].

iLEAPP 코드 주석에는 자동 완성 프로필에 대해 "iOS 시험 자료가 모두 비어 있다" 는 말이 있습니다 [1]. 아이폰 크롬에서 `Web Data` 가 얼마나 채워지는지는 불확실하니, 빈 표를 "사용자가 지웠다" 로 읽지 않습니다.

공용 스크립트가 여러 브라우저 경로를 함께 찾기 때문에, 도구 결과에서 어느 앱 컨테이너의 파일인지 경로로 한 번 더 확인합니다 [1].

회사가 관리하는 기기에서는 크롬이 MDM 관리 앱 설정으로 정책을 받습니다. 크롬은 `ChromePolicy` 키를 먼저 읽고, 이 키가 없을 때만 `EncodedChromePolicy` 를 읽습니다 [3]. 이 문서는 버전 35 부터 지원한다는 옛 문구와 "크롬 48 에서 정책 지원을 없앨 예정" 이라는 문구가 함께 있는 오래된 문서라서, 현재 관리 방식을 판단할 근거로 쓰지는 않습니다 [3]. 관리 설정이 들어간 경로는 [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) 쪽에서 확인합니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 명세로 만든 예시이고 실제 검체에서 뽑은 값이 아닙니다. `History` 파일 맨 앞 16바이트는 SQLite 머리글이라서 다음처럼 보입니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

`visit_time` 이 2026-01-01 00:00:00 UTC 라면 값은 (1767225600 + 11644473600) × 1000000 = 13411699200000000 이고, 6바이트로는 모자라니 SQLite 레코드 안에 8바이트 빅엔디언 정수로 들어갑니다.

```
00 2F A5 DE 8E A6 80 00
```

거꾸로 이 8바이트를 정수로 읽어 1000000 으로 나누고 11644473600 을 빼면 유닉스 시각 1767225600 이 나옵니다. 레코드 안에서 정수를 찾는 방법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에 있습니다.

**공개 도구로 한 번.** 파일을 복사한 뒤 사본에서 SQLite 셸로 다음처럼 뽑으면 MVT 가 뽑는 칸과 같은 모양이 나옵니다.

```sql
SELECT urls.id, urls.url, urls.title, visits.id, visits.from_visit,
       datetime(visits.visit_time/1000000 + strftime('%s','1601-01-01'), 'unixepoch') AS visit_utc,
       visits.visit_duration/1000000.0 AS duration_sec
FROM visits JOIN urls ON visits.url = urls.id
ORDER BY visits.visit_time;
```

iLEAPP 를 로컬 백업 폴더에 돌리면 `chrome.py` 가 같은 파일들을 찾아 표로 보여 주고 [1], MVT 는 백업이나 파일 시스템 추출본에서 `History` 를 찾아 방문 기록을 뽑습니다 [4]. 두 도구의 결과 줄 수와 시각이 셸로 직접 뽑은 결과와 같은지 맞춰 봅니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [KnowledgeC](../app-usage/knowledgec/index.md), [바이옴](../app-usage/biome/index.md) | 방문 시각에 크롬이 앞에 떠 있었는지 |
| [화면 사용 시간](../app-usage/screen-time.md) | 그날 크롬 사용 시간 |
| [앱별 데이터 사용량](../network/data-usage.md) | 크롬이 그 무렵 통신했는지 |
| [설치된 앱](../app-usage/installed-apps.md) | 크롬 컨테이너 UUID 와 설치 여부 |
| [사파리](safari/index.md), [네이버 앱](naver.md) | 같은 주소를 다른 브라우저로도 열었는지 |

여러 브라우저를 한 흐름으로 묶는 절차는 [웹 사용 행위 재구성](../../04-scenarios/activity/web-activity.md) 과 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등) 가운데 아이폰 크롬 데이터가 들어 있는 것을 골라 다음을 풀어 봅니다.

1. 로컬 백업의 `Manifest.db` 에서 `AppDomain-com.google.chrome.ios` 도메인 파일을 모두 찾고, 위에 적은 크롬 파일 가운데 어느 것이 들어 있는지 적어 봅니다.
2. `History` 에서 가장 이른 방문과 가장 늦은 방문의 시각을 UTC 로 구하고, 검체 설명의 시간대로 바꿔 봅니다.
3. `keyword_search_terms` 의 검색어마다 이어지는 `urls` 줄을 찾아 검색 시각을 붙여 봅니다.
4. 같은 시간대의 KnowledgeC 나 바이옴 기록에 크롬이 앞에 떠 있었던 흔적이 있는지 맞춰 봅니다.

## 참고 문헌

1. iLEAPP, `scripts/artifacts/chrome.py` (abrignoni/iLEAPP, main) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/chrome.py
2. Chromium Docs, User Data Directory — https://chromium.googlesource.com/chromium/src/+/HEAD/docs/user_data_dir.md
3. The Chromium Projects, iOS MDM Policy Format — https://www.chromium.org/administrators/ios-mdm-policy-format/
4. MVT, `src/mvt/ios/modules/mixed/chrome_history.py` (mvt-project/mvt, main) — https://raw.githubusercontent.com/mvt-project/mvt/main/src/mvt/ios/modules/mixed/chrome_history.py
5. Google Chrome 도움말, Browse in Incognito mode (iPhone & iPad) — https://support.google.com/chrome/answer/95464?hl=en&co=GENIE.Platform%3DiOS
6. Apple Developer, App Review Guidelines (2.5.6) — https://developer.apple.com/app-store/review/guidelines/
