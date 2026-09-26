---
title: "개인 정보 보호 브라우징으로 무엇을 했나"
parent: "시나리오 · 행위 재구성"
nav_order: 2340
---

# 개인 정보 보호 브라우징으로 무엇을 했나 (Private Browsing)

## 조사 질문

사용자가 사파리의 개인 정보 보호 브라우징 (Private Browsing)이나 크롬의 시크릿 모드 (Incognito mode)로 무엇을 보고 무엇을 받았는지 묻습니다. 이 모드는 방문 기록을 남기지 않도록 만든 기능이라서, 이 페이지는 브라우저가 스스로 남기지 않는 기록을 찾는 방법보다 브라우저 밖에 남는 흔적을 어디서 어떻게 읽는지를 다룹니다. 우회하거나 되살리는 방법이 아니라 남는 흔적과 그 해석만 다룹니다.

## 먼저 확인할 것

먼저 macOS 버전과 사파리 버전, 설치된 브라우저 목록을 확인합니다. 아래 동작이 어느 사파리·macOS 버전부터인지는 공개 자료에 나와 있지 않아서 [1], 검체의 버전을 적어 두고 결과를 그 버전 범위 안에서만 말합니다. 버전은 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../02-artifacts/system-account/os-version-install-history.md)에서, 설치된 브라우저는 [설치한 앱과 영수증 (Applications·Receipts)](../../02-artifacts/system-account/installed-apps-receipts.md)에서 확인합니다.

다음으로 조사 대상 계정과 시간대를 정하고, 수집 범위에 메모리가 들어 있는지와 맥 밖의 네트워크 기록(회사 프록시·DNS 기록 등)을 받을 수 있는지 확인합니다. 방문한 웹사이트나 네트워크를 관리하는 조직(회사·인터넷 서비스 사업자)은 시크릿 모드 활동을 볼 수 있어서 [2], 맥 안의 기록이 비어 있을 때 맥 밖의 기록이 중요해집니다. 시간대는 [시간대와 시계 설정 (Time Zone·NTP)](../../02-artifacts/system-account/time-zone.md)에서 확인합니다.

## 무엇이 남지 않고 무엇이 남나

두 브라우저의 동작을 나란히 적으면 아래와 같습니다. "근거 없음" 은 공식 도움말에 설명이 없다는 뜻이고, 남는다는 뜻도 남지 않는다는 뜻도 아닙니다.

| 항목 | 사파리 개인 정보 보호 브라우징 [1] | 크롬 시크릿 모드 [2] |
|---|---|---|
| 방문한 페이지 | 저장하지 않음 | 세션이 끝나면 방문 기록을 남기지 않음 |
| 자동 완성 (AutoFill) 정보 | 저장하지 않음 | 근거 없음 |
| 최근 검색 | 스마트 검색 필드의 최근 검색에 넣지 않음 | 근거 없음 |
| 쿠키·웹사이트 데이터 | 바뀐 내용을 저장하지 않음 | 세션이 끝나면 사이트 데이터를 남기지 않음 |
| 내려받은 파일 | 다운로드 목록에는 넣지 않지만 파일은 컴퓨터에 남음 | 파일이 남음 |
| 북마크 | 근거 없음 | 저장한 북마크가 남음 |
| 다른 기기 | 열린 페이지를 iCloud 에 저장하지 않아 다른 Apple 기기의 탭 목록에 안 보이고, Handoff 로 넘어가지 않음 | 근거 없음 |
| 탭 사이 | 한 탭에서 시작한 브라우징이 다른 탭과 분리됨 | 근거 없음 |

사파리는 개인 정보 보호 브라우징에서 고급 추적·핑거프린팅 방지를 기본으로 켭니다 [1]. 크롬의 세션은 시크릿 창을 모두 닫을 때 끝나고, 위 표의 크롬 동작은 모두 세션이 끝난 뒤를 기준으로 합니다 [2]. 창이 아직 열려 있는 동안 기기에 무엇이 남는지는 이것으로 판단할 수 없습니다. 파이어폭스의 비공개 창은 이 페이지에서 다루지 않습니다.

두 브라우저 모두 내려받은 파일은 남습니다 [1][2]. 방문 기록이 없어도 받은 파일에서 출발해 거꾸로 따라가는 것이 이 조사의 중심이 됩니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 내려받은 파일 자체 | 개인 정보 보호 창에서 받아도 파일은 남음 [1][2] | [이 파일은 어디서 왔나 (File Origin)](file-origin.md) |
| 2 | 파일의 확장 속성 `com.apple.quarantine`, `com.apple.metadata:kMDItemWhereFroms`, `com.apple.metadata:kMDItemDownloadedDate` | 다운로드 출처와 받은 시각의 후보 [3]. 개인 정보 보호 창에서 받은 파일에도 붙는지는 검체에서 확인 | [다운로드 출처 속성 (kMDItemWhereFroms)](../../02-artifacts/filesystem/where-froms.md) |
| 3 | 격리 이벤트 데이터베이스의 `LSQuarantineEvent` 표 | 다운로드 기록의 후보. 개인 정보 보호 창 다운로드가 기록되는지는 검체에서 확인 | [격리 속성과 다운로드 기록 (Quarantine)](../../02-artifacts/filesystem/quarantine/index.md) |
| 4 | 사파리 `RecentlyClosedTabs.plist` | 닫힌 창·탭 항목의 `IsPrivateWindow` 키 | [사파리 (Safari)](../../02-artifacts/browsers/safari/index.md) |
| 5 | KnowledgeC 의 `/safari/history` 스트림 | 개인 정보 보호 모드에서 기록되는지는 검체에서 확인 | [KnowledgeC (knowledgeC.db)](../../02-artifacts/execution/knowledgec/index.md) |
| 6 | 메모리·스왑 | 남는지는 공개 자료 없음. 라이브 확보 때만 볼 수 있음 | [메모리 분석 (Memory Forensics)](../../03-techniques/analysis/memory-forensics/index.md) |
| 7 | 맥 밖의 네트워크 기록 | 방문한 웹사이트와 네트워크 관리 조직이 활동을 볼 수 있을 수 있음 [2] | [웹 사용 행위 재구성 (Web Activity)](web-activity.md) |

`RecentlyClosedTabs.plist` 는 닫힌 창과 탭을 항목으로 담고, mac_apt 는 항목의 `IsPrivateWindow` 키를 읽어 개인 정보 보호 창을 따로 표시합니다. 이 키가 참인 항목은 개인 정보 보호 창이 열렸다가 닫혔다는 기록으로 보입니다. 다만 사파리 버전마다 이 파일에 개인 정보 보호 창이 남는지는 알려져 있지 않아서, 검체의 사파리 버전과 함께 적습니다. 파일 위치와 항목 구조는 [사파리 (Safari)](../../02-artifacts/browsers/safari/index.md)에 있습니다.

확장 속성과 격리 이벤트 데이터베이스, KnowledgeC 가 개인 정보 보호 창의 활동을 담는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 그래서 이 세 곳은 "있으면 쓰고, 없어도 결론을 내리지 않는" 후보로 다루고, 찾은 값이 개인 정보 보호 창에서 나왔는지는 다른 기록과 시각을 맞춰 따로 판단합니다.

## 분석 흐름

1. 검체의 macOS·사파리 버전과 설치된 브라우저를 적고, 조사 대상 계정과 시간대를 정합니다.
2. 일반 방문 기록에서 조사 구간을 먼저 읽습니다. 일반 창의 기록이 있는 구간과 비어 있는 구간을 나눠 두면 뒤 단계에서 찾은 흔적을 어느 구간에 놓을지 정하기 쉽습니다. 읽는 법은 [웹 사용 행위 재구성 (Web Activity)](web-activity.md)에 있습니다.
3. `RecentlyClosedTabs.plist` 에서 `IsPrivateWindow` 가 참인 항목을 찾아, 개인 정보 보호 창을 쓴 적이 있는지부터 확인합니다.
4. 다운로드 폴더와 사용자 폴더에서 조사 구간 안에 생긴 파일을 찾고, 다운로드 목록에 없는 파일을 따로 모읍니다. 개인 정보 보호 창에서 받은 파일은 다운로드 목록에 들어가지 않기 때문에 [1], 목록에 없는 파일이 후보가 됩니다. 파일이 생긴 시각은 [파일 시스템 이벤트 (FSEvents)](../../02-artifacts/filesystem/fsevents/index.md)로도 맞춰 봅니다.
5. 후보 파일마다 확장 속성과 격리 이벤트 데이터베이스를 읽어 출처 URL 과 받은 시각을 찾습니다. 값이 있으면 그대로 적고, 없으면 "속성이 없었다" 는 사실만 적습니다.
6. 메모리를 확보했다면 조사 구간의 URL·검색어 문자열을 찾되, 메모리에 남는지 자체가 알려져 있지 않아서 결과를 다른 기록으로 뒷받침할 때만 씁니다.
7. 맥 밖의 네트워크 기록을 받을 수 있다면 조사 구간의 접속 기록과 3~5단계의 결과를 한 타임라인에 올립니다. 타임라인은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)을 따릅니다.

> 그림 자리: 일반 창의 방문 기록이 비어 있는 구간 위에 받은 파일의 생성 시각·격리 속성 시각·네트워크 접속 기록을 겹쳐 놓은 타임라인

## 흔한 오판

방문 기록이 비어 있는 구간을 곧바로 개인 정보 보호 브라우징의 증거로 보는 경우가 많습니다. 방문 기록은 사용자가 직접 지우거나 다른 브라우저를 써도 비어 보일 수 있어서, 빈 구간은 "이 브라우저의 일반 기록에는 없다" 까지만 말하고, 지운 흔적은 [증거를 없애려 했나 (Anti-Forensics)](anti-forensics/index.md)에서 따로 봅니다.

`IsPrivateWindow` 가 참인 항목을 찾았다고 해서 그 창에서 무엇을 했는지까지 알 수 있다고 보지도 않습니다. 이 키는 닫힌 창이 개인 정보 보호 창이었다는 표시일 뿐이라서, 그 창의 활동은 받은 파일이나 맥 밖의 기록처럼 다른 흔적으로 따로 밝혀야 합니다.

받은 파일에 출처 속성이 있다고 해서 그 파일을 개인 정보 보호 창에서 받았다고 보는 것도 오판입니다. 파일과 속성만으로는 어느 창에서 받았는지 가릴 수 없고, 개인 정보 보호 창에서 받은 파일에 이 속성이 붙는지도 알려져 있지 않습니다. "다운로드 목록에는 없고 파일과 출처 속성은 있다" 처럼 관찰한 사실을 그대로 적습니다.

## 보고서 문장 예

- "사파리 `RecentlyClosedTabs.plist` 에 `IsPrivateWindow` 값이 참인 닫힌 창 항목이 N건 있습니다. 이 기록으로 개인 정보 보호 창을 연 적이 있다는 점은 확인되지만, 그 창에서 방문한 페이지는 이 파일에 나타나지 않습니다."
- "`~/Downloads` 의 파일 N개는 사파리 다운로드 목록에 없으나, 그중 N개에 `com.apple.metadata:kMDItemWhereFroms` 속성이 있어 출처 URL 을 확인했습니다. 이 기록만으로는 파일을 받은 창이 개인 정보 보호 창이었는지 판단할 수 없습니다."

## 함께 볼 페이지

- [웹 사용 행위 재구성 (Web Activity)](web-activity.md) — 일반 창의 방문 기록을 읽는 순서
- [이 파일은 어디서 왔나 (File Origin)](file-origin.md) — 받은 파일에서 출처를 거꾸로 따라갈 때
- [크롬·엣지·웨일 (Chromium 계열)](../../02-artifacts/browsers/chromium/index.md) — 크롬 프로필의 일반 기록
- [파이어폭스 (Firefox)](../../02-artifacts/browsers/firefox.md) — 파이어폭스를 함께 쓴 경우
- [앱별 네트워크 사용량 (netusage)](../../02-artifacts/network/netusage.md) — 조사 구간에 브라우저가 주고받은 양

## 참고 문헌

1. Apple 지원 — Safari 사용 설명서 "Browse privately in Safari on Mac" — https://support.apple.com/guide/safari/browse-privately-ibrw1069/mac
2. Google Chrome 도움말 — "Browse in Incognito mode" — https://support.google.com/chrome/answer/95464?hl=en&co=GENIE.Platform%3DDesktop
3. libyal libfsapfs — Apple File System (APFS) 형식 문서 — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
