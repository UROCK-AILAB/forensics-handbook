---
title: "웹 사용 행위 재구성"
parent: "시나리오 · 행위 재구성"
nav_order: 2330
---

# 웹 사용 행위 재구성 (Web Activity)

## 조사 질문

이 맥에서 어떤 웹 사이트에 언제 들어갔고, 무엇을 검색했고, 무엇을 받았는지 묻습니다. 사용자가 주소를 직접 쳤는지, 링크나 리디렉션으로 넘어갔는지, 다른 기기에서 동기화돼 들어온 기록인지까지 가려야 "이 사람이 이 사이트를 봤다"에 가까운 문장을 쓸 수 있습니다.

브라우저마다 기록 파일과 시각 기준이 달라서, 브라우저를 하나씩 따로 읽은 뒤 한 타임라인에 합칩니다. 브라우저 밖에도 knowledgeC·격리 이벤트 DB·통합 로그의 DNS 기록처럼 웹 사용을 비추는 흔적이 있어서 브라우저 기록이 지워졌을 때 보강 자료로 씁니다. 브라우저 파일의 구조는 [사파리](../../02-artifacts/browsers/safari/index.md), [크롬·엣지·웨일](../../02-artifacts/browsers/chromium/index.md), [파이어폭스](../../02-artifacts/browsers/firefox.md) 페이지에서 다루고, 이 페이지는 조사 순서와 판단만 다룹니다.

## 먼저 확인할 것

OS 버전과 함께 설치된 브라우저와 버전을 확인합니다([설치한 앱과 영수증](../../02-artifacts/system-account/installed-apps-receipts.md)). 사파리는 17 이후 프로필마다 `Profiles/{UUID}/History.db` 를 따로 두고, 탭 정보를 `SafariTabs.db` 에 적습니다 [1]. 크롬 계열은 사용자 데이터 폴더 아래 프로필 폴더가 여럿일 수 있어서 프로필마다 따로 봅니다.

시간대는 [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md)에서 확인합니다. 시각 기준이 브라우저마다 달라서 사파리는 맥 절대 시각(2001-01-01 기준), 크롬 계열은 1601-01-01 UTC 기준 마이크로초, 파이어폭스는 1970 기준 마이크로초(PRTime)를 씁니다 [1][6][11]. 모두 한 기준으로 바꿔 적어 둡니다([맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md)).

수집 범위에서는 SQLite 본 파일과 함께 `-wal` 파일을 떴는지 확인합니다. ForensicArtifacts 정의는 브라우저 기록의 WAL 파일도 수집 대상으로 두고 있어서 [13], 본 파일만 뜨면 최근 기록이 빠질 수 있습니다([맥 증거 확보](../../03-techniques/process-acquisition/evidence-acquisition/index.md)).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 사파리 `~/Library/Safari/History.db`(+`-wal`) | 방문한 URL과 방문마다의 시각, 리디렉션 | [사파리](../../02-artifacts/browsers/safari/index.md) |
| 2 | 크롬 계열 `History` 의 `urls`·`visits`·`keyword_search_terms` 표 | 방문 URL, 방문 경로(`transition`), 검색어 | [크롬·엣지·웨일](../../02-artifacts/browsers/chromium/index.md) |
| 3 | 파이어폭스 `places.sqlite`(+`-wal`) | 방문 URL과 방문 종류 | [파이어폭스](../../02-artifacts/browsers/firefox.md) |
| 4 | 사파리 `Downloads.plist`, 크롬 `downloads` 표, 파이어폭스 `visit_type` 7 | 받은 파일 | [이 파일은 어디서 왔나](file-origin.md) |
| 5 | 사파리 탭·세션 파일 `LastSession.plist`·`RecentlyClosedTabs.plist`·`BrowserState.db`·`SafariTabs.db`·`CloudTabs.db` | 열어 둔 탭, 닫은 탭, 다른 기기의 아이클라우드 탭 | [사파리](../../02-artifacts/browsers/safari/index.md) |
| 6 | knowledgeC `/safari/history` 스트림 | `ZVALUESTRING` 칸의 URL | [KnowledgeC](../../02-artifacts/execution/knowledgec/index.md) |
| 7 | 격리 이벤트 DB와 파일의 격리 속성 | 받은 파일의 URL·referrer·받은 앱 | [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md) |
| 8 | 통합 로그 `mDNSResponder` 기록 | DNS 조회 | [통합 로그에서 찾을 것](../../02-artifacts/logs/unified-log-events/index.md) |

크롬 사용자 데이터 폴더는 크롬이 `~/Library/Application Support/Google/Chrome`, 엣지가 `~/Library/Application Support/Microsoft Edge`, 브레이브가 `~/Library/Application Support/BraveSoftware/Brave-Browser` 이고 [5][13], 파이어폭스 기록은 `~/Library/Application Support/Firefox/Profiles/` 아래 프로필 폴더의 `places.sqlite` 입니다 [10]. 웨일의 맥 경로는 확인하지 못했습니다.

1~3번으로 방문 기록의 뼈대를 세우고, 4~5번으로 받은 파일과 탭 상태를 붙입니다. 6~8번은 브라우저 기록이 비었거나 지워졌을 때 보강하는 자료입니다. knowledgeC `/safari/history` 는 macOS 10.13 에서 관찰된 스트림이고 [9], mac_apt 가 해석하는 바이옴 스트림 `App.WebUsage`·`Safari.*` 가 macOS 에 실제로 있는지는 확인하지 못했습니다 [12]. 통합 로그의 DNS 기록은 서브시스템 `com.apple.mDNSResponder` 로 찾고, 비공개 데이터 설정이 꺼져 있으면 호스트 이름이 가려져 나옵니다 [14].

### 크롬 기록에서 검색어와 입력을 읽기

크롬 `urls` 표에는 `url`·`title`·`visit_count`·`typed_count`·`last_visit_time`·`hidden` 칸이 있습니다. `visit_count` 는 방문 횟수, `typed_count` 는 사용자가 URL 을 직접 친 횟수, `last_visit_time` 은 마지막 방문 시각, `hidden` 은 일부 조회에서 뺄 URL 을 표시합니다 [2]. `keyword_search_terms` 표는 검색 엔진 ID(`keyword_id`), `urls.id` 를 가리키는 `url_id`, 실제 검색어 `term`, 소문자로 바꾸고 공백을 정리한 `normalized_term` 을 담아서 [2], `keyword_search_terms.url_id = urls.id` 로 이으면 검색어와 검색 결과 페이지 방문이 한 줄로 묶입니다.

`visits` 표에는 방문마다 `visit_time`, 이전 방문 `from_visit`, 새 탭을 연 방문 `opener_visit`, 방문 경로 `transition`, 머문 시간 `visit_duration` 이 있습니다 [7]. `transition` 의 하위 8비트는 LINK 0, TYPED 1, AUTO_BOOKMARK 2, FORM_SUBMIT 7, RELOAD 8, KEYWORD 9 같은 핵심 종류이고, 그 위 비트에 FROM_ADDRESS_BAR(0x02000000), CLIENT_REDIRECT(0x40000000), SERVER_REDIRECT(0x80000000) 같은 한정자가 붙습니다 [8]. 방문 출처 값 이름에 SOURCE_SYNCED 가 있어서 다른 기기에서 동기화된 방문을 가릴 수 있지만, 숫자 값은 확인하지 못했습니다 [7].

### 사파리 기록을 읽기

사파리 `History.db` 는 URL 하나에 한 행인 `history_items` 와 방문마다 한 행인 `history_visits` 로 나뉘고, `history_visits.history_item = history_items.id` 로 잇습니다. 리디렉션은 `redirect_source`·`redirect_destination` 칸으로 따라갑니다 [3]. `history_tombstones` 표(`start_time`, `end_time`, `url`, `generation`)도 있지만 기록 지우기의 흔적인지와 시각 기준은 확인하지 못했습니다 [3]. 설정 plist 의 `RecentWebSearches` 에는 최근 검색어(`SearchString`)와 시각(`Date`)이 남습니다(요세미티 이후) [1].

## 분석 흐름

1. 사용자와 브라우저 프로필 목록을 정리하고, 프로필마다 기록 DB와 `-wal` 파일을 확보합니다.
2. 브라우저마다 방문 기록을 뽑아 시각을 한 기준으로 바꿉니다.
3. 방문마다 사용자가 직접 한 행위인지 가립니다. 크롬은 `typed_count` 와 `transition` 의 TYPED(1)·KEYWORD(9), 파이어폭스는 TRANSITION_TYPED(2)가 직접 입력에 가깝고, 크롬 리디렉션 한정자와 파이어폭스 5·6 은 리디렉션이라 사용자 행위로 세지 않습니다 [2][8][11].
4. 검색어를 뽑습니다. 크롬은 `keyword_search_terms`, 사파리는 `RecentWebSearches` 를 보고, 검색 결과 페이지 방문과 이어 봅니다.
5. 동기화된 기록을 걸러 냅니다. 크롬 SOURCE_SYNCED, 사파리 아이클라우드 탭(`CloudTabs.db`), 바이옴 `remote/` 폴더 기록은 이 맥에서 직접 한 일이 아닐 수 있습니다 [1][7][12].
6. 다운로드 기록과 격리 이벤트 DB를 붙여 방문 뒤 무엇을 받았는지 봅니다(자세한 방법은 [이 파일은 어디서 왔나](file-origin.md)).
7. 브라우저 기록에 빈 구간이 있으면 knowledgeC, 통합 로그 DNS 기록, 탭·세션 파일로 채울 수 있는지 봅니다.
8. 모든 결과를 [타임라인](../../03-techniques/analysis/timeline/index.md)에 올리고, 같은 시간대의 [어떤 앱을 언제 썼나](app-usage.md) 결과와 맞춰 브라우저가 실제로 앞에 있었는지 확인합니다.

3~8단계의 순서는 공개 자료의 절차가 아니라 필자가 정리한 방법입니다.

## 흔한 오판

- **방문 기록 한 줄을 "사용자가 이 사이트를 찾아 들어갔다"로 쓰는 경우.** 리디렉션과 자동 로드도 방문으로 남습니다. `transition`·방문 종류와 `typed_count` 를 확인한 만큼만 씁니다 [2][8][11].
- **동기화된 방문을 이 맥의 사용으로 세는 경우.** 크롬 동기화 방문, 사파리 아이클라우드 기록은 다른 기기에서 한 일일 수 있습니다 [7]. 사파리 방문 기록·탭 그룹·아이클라우드 탭은 표준 데이터 보호에서도 아이클라우드 종단간 암호화 대상입니다 [16].
- **기록이 비어 있으면 웹을 쓰지 않았다고 보는 경우.** 사파리 "기록 지우기"는 방문 기록·뒤로/앞으로 목록·자주 방문·최근 검색·다운로드 목록을 지우고 아이클라우드로 묶인 다른 기기 기록까지 지우지만 받은 파일은 남깁니다 [15]. 개인 정보 보호 브라우징은 [개인 정보 보호 브라우징으로 무엇을 했나](private-browsing.md)에서 따로 봅니다.
- **`-wal` 파일 없이 결론을 내는 경우.** 최근 기록이 WAL 에만 있을 수 있습니다 [13].
- **시각 기준을 섞는 경우.** 세 브라우저의 기원 시각이 2001년·1601년·1970년으로 모두 달라서, 한 기준으로 바꾸기 전에는 값을 서로 비교할 수 없습니다.
- **쿠키나 저장된 암호 값을 읽어 사용 사실을 세우려는 경우.** 크롬의 이 값들은 키체인 없이 읽을 수 없고 [4], 이 핸드북은 복호 절차를 다루지 않습니다.

## 보고서 문장 예

> 사용자 ○○의 크롬 기본 프로필 `History` 에 ○○○○년 ○월 ○일 ○시 ○분(UTC로 바꾼 시각) "https://○○" 방문 기록이 있고, 이 방문의 `transition` 핵심 값은 TYPED(1)이며 동기화 방문 표시는 없습니다. 같은 프로필의 `keyword_search_terms` 에는 ○시 ○분에 검색어 "○○" 로 검색 결과 페이지를 연 기록이 있습니다. 이 기록들로 이 프로필에서 주소를 직접 입력한 방문과 검색이 있었다는 점은 확인할 수 있지만, 그 시각에 맥 앞에 있던 사람이 누구인지는 정할 수 없습니다.

## 함께 볼 페이지

- [사파리 (Safari)](../../02-artifacts/browsers/safari/index.md) — 사파리 기록 파일의 구조
- [크롬·엣지·웨일 (Chromium 계열)](../../02-artifacts/browsers/chromium/index.md) — 크롬 계열 기록 파일의 구조
- [파이어폭스 (Firefox)](../../02-artifacts/browsers/firefox.md) — `places.sqlite` 구조
- [개인 정보 보호 브라우징으로 무엇을 했나 (Private Browsing)](private-browsing.md) — 기록이 남지 않는 창을 쓴 경우
- [이 파일은 어디서 왔나 (File Origin)](file-origin.md) — 받은 파일의 출처
- [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md) — WAL 과 지운 행

## 참고 문헌

1. mac_apt Safari 플러그인 safari.py (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/safari.py
2. Chromium 소스 components/history/core/browser/url_database.cc — https://chromium.googlesource.com/chromium/src/+/HEAD/components/history/core/browser/url_database.cc
3. plaso Safari History.db SQLite 플러그인 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/sqlite_plugins/safari.py
4. Chromium 소스(v120.0.6099.109) components/os_crypt/sync/os_crypt_mac.mm — https://chromium.googlesource.com/chromium/src/+/refs/tags/120.0.6099.109/components/os_crypt/sync/os_crypt_mac.mm
5. Chromium Docs — User Data Directory — https://chromium.googlesource.com/chromium/src/+/HEAD/docs/user_data_dir.md
6. Forensics Wiki — Google Chrome — https://forensics.wiki/google_chrome/
7. Chromium 소스 components/history/core/browser/visit_database.cc — https://chromium.googlesource.com/chromium/src/+/HEAD/components/history/core/browser/visit_database.cc
8. Chromium 소스 ui/base/page_transition_types.h — https://chromium.googlesource.com/chromium/src/+/HEAD/ui/base/page_transition_types.h
9. Sarah Edwards, "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (mac4n6.com, 2018-08-05) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
10. Forensics Wiki — Mozilla Firefox — https://forensics.wiki/mozilla_firefox/
11. Mozilla 소스 toolkit/components/places/nsINavHistoryService.idl — https://searchfox.org/mozilla-central/source/toolkit/components/places/nsINavHistoryService.idl
12. mac_apt (Yogesh Khatri), plugins/biome.py — https://github.com/ydkhatri/mac_apt/blob/master/plugins/biome.py , iLEAPP — https://github.com/abrignoni/iLEAPP
13. ForensicArtifacts — webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
14. Mandiant (Alexander Holcomb), "Reviewing macOS Unified Logs" (2022-08-31) — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
15. Apple Support, "Clear your browsing history in Safari on Mac" — https://support.apple.com/guide/safari/clear-your-browsing-history-sfri47acf5d6/mac
16. Apple Support, "iCloud data security overview" (102651) — https://support.apple.com/en-us/102651
