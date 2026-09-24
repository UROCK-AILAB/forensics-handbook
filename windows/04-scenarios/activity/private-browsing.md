# 시크릿 모드로 무엇을 했나 (Private Browsing)

시크릿 모드 (Incognito) 나 InPrivate 창에서 한 일을 묻는 조사를 다룹니다. 이런 창에서 연 페이지는 브라우저의 방문 기록 파일에 남지 않습니다. 그래서 브라우저 프로필 안보다 바깥에서 흔적을 찾는 일이 많습니다. 이 페이지는 브라우저가 지우는 것과 남기는 것을 먼저 나누고, 남는 흔적을 어떤 순서로 보는지 정리합니다.

브라우저마다의 파일 구조는 [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) 와 [파이어폭스](../../02-artifacts/browsers/firefox/index.md) 에 있습니다. 일반 창의 방문 기록 분석은 [웹 사용 행위 재구성](web-activity.md) 에서 다룹니다.

## 조사 질문

- 시크릿 창에서 어느 사이트에 들어갔습니까?
- 시크릿 창에서 무엇을 내려받거나 저장했습니까?
- 시크릿 창을 언제 썼습니까?
- 방문 기록이 비어 있는 까닭이 시크릿 창입니까, 기록 삭제입니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 버전과 빌드를 먼저 적어 둡니다. |
| 시간대 | 브라우저 기록과 파일 시스템 기록을 한 줄로 세우려면 시간대가 필요합니다. [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽습니다. Bias 값을 부호 있는 수로 읽는 법은 [이 파일을 누가 언제 열었나](file-access.md) 의 "먼저 확인할 것" 에 있습니다. |
| 사용자와 프로필 | 브라우저 데이터는 사용자 프로필마다, 브라우저 프로필마다 따로 있습니다. [사용자 프로필 목록](../../02-artifacts/system-account/profilelist.md) 으로 SID 와 프로필 폴더를 짝지어 둡니다. |
| 설치된 브라우저 | 브라우저마다 지우는 범위가 다릅니다. [설치 프로그램](../../02-artifacts/system-account/uninstall.md) 에서 설치된 브라우저를 확인합니다. |
| PC 가 켜져 있는지 | 시크릿 창이 아직 열려 있으면 세션 데이터가 아직 지워지지 않았습니다. 끄기 전에 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 과 [메모리 분석](../../03-techniques/analysis/memory-forensics/index.md) 을 봅니다. |
| 수집 범위 | 브라우저 프로필 폴더, 사용자의 다운로드 폴더, $MFT, 사용자 하이브, SRUDB.dat 를 함께 확보합니다. |

## 브라우저가 지우는 것과 남기는 것

Chrome 과 Edge 도움말에 적힌 내용을 나란히 놓았습니다.

| 항목 | Chrome 시크릿 모드 [1] | Edge InPrivate [2] |
|---|---|---|
| 방문 기록 | 세션이 끝나면 남기지 않음 | 창을 모두 닫으면 지움 |
| 쿠키·사이트 데이터 | 세션 동안 임시로 두고, 끝나면 남기지 않음 | 창을 모두 닫으면 지움 |
| 캐시한 이미지와 파일 | 도움말에 따로 없음 | 창을 모두 닫으면 지움 |
| 다운로드 기록(브라우저의 목록) | 도움말에 따로 없음 | 창을 모두 닫으면 지움 |
| 비밀번호·자동 채우기 양식 데이터 | 도움말에 따로 없음 | 창을 모두 닫으면 지움 |
| 사이트 권한·호스팅된 앱 데이터 | 도움말에 따로 없음 | 창을 모두 닫으면 지움 |
| 내려받은 파일 | 사용자가 지울 때까지 기기에 남음 | 남김 |
| 북마크·즐겨찾기 | 남음. 북마크와 읽기 목록 항목은 일반 브라우징 쪽으로 넘어감 | 즐겨찾기를 남김 |

**세션이 끝나는 때.**

Chrome 은 시크릿 창을 모두 닫아야 세션이 끝나고, 세션이 끝나야 데이터를 지웁니다[1]. 시크릿 창을 여러 개 열어도 세션은 하나로 이어집니다[1]. Edge 도 InPrivate 창을 모두 닫을 때 위 항목을 지웁니다[2]. 그래서 창이 하나라도 열린 채로 PC 를 확보했다면 세션 데이터가 아직 지워지지 않은 상태입니다.

**Edge 에서 더 볼 것.**

InPrivate 창을 연 프로필의 즐겨찾기·비밀번호·양식 채우기 데이터는 InPrivate 창에서도 쓸 수 있습니다[2]. InPrivate 새 탭의 검색창과 Bing.com 에서 검색하면 자동으로 "InPrivate search with Microsoft Bing" 을 쓰며, Bing 이 기본 검색 엔진이면 주소창 검색도 마찬가지입니다[2]. 이 검색이 PC 나 계정에 무엇을 남기는지는 도움말에 적혀 있지 않습니다.

**PC 밖에서 보이는 것.**

방문한 웹사이트는 시크릿 창의 활동을 볼 수도 있고[1], 네트워크를 관리하는 학교·회사·인터넷 서비스 제공자도 활동을 볼 수도 있습니다[1][2]. 조직의 네트워크에서 쓴 PC 라면 네트워크 관리 쪽의 기록을 따로 요청할 수 있습니다.

**Firefox.** Mozilla 도움말 본문을 이번에 열지 못했습니다. Firefox 사생활 보호 모드 (Private Browsing) 가 지우는 것과 남기는 것은 이 페이지에서 확인하지 못했습니다. [파이어폭스](../../02-artifacts/browsers/firefox/index.md) 에서 확인합니다.

**캐시와 쿠키가 어디에 있는가.** [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) 의 쿠키·캐시 페이지는 시크릿 창이 쿠키와 HTTP 캐시를 메모리에만 둔다고 적었습니다. 캐시 쪽은 Chromium 소스를 근거로 들었고, 이 페이지에서 연 도움말로는 다시 확인하지 않았습니다. 켜진 PC 라면 이 점 때문에 메모리 확보가 먼저입니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 근거 | 링크 |
|---|---|---|---|---|
| 1 | 켜진 PC 의 메모리 | 열린 시크릿 세션의 데이터 | 세션이 끝나야 지움[1][2] | [메모리 분석](../../03-techniques/analysis/memory-forensics/index.md) · [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) |
| 2 | 일반 프로필의 방문 기록 | 조사 시간대가 비어 있는지 | 시크릿 창은 남기지 않음[1][2] | [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) |
| 3 | 북마크·즐겨찾기 | 시크릿 창에서 저장한 항목 | 남음[1][2] | [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) |
| 4 | 내려받은 파일 | 시크릿 창에서 받은 파일 자체와 파일 시스템 시각 | 남음[1][2] | [마스터 파일 테이블](../../02-artifacts/filesystem/mft.md) · [이 파일은 어디서 왔나](file-origin.md) |
| 5 | 내려받은 파일의 출처 표시 | 파일을 받아 온 곳의 단서 | 후보 | [다운로드 출처 표시](../../02-artifacts/filesystem/zone-identifier.md) |
| 6 | 브라우저 실행 흔적 | 브라우저를 실행한 시각 | 후보 | [프리페치](../../02-artifacts/execution/prefetch/index.md) · [UserAssist](../../02-artifacts/execution/userassist.md) |
| 7 | 바로가기·점프리스트 | 시크릿 창을 여는 실행 인자 | 후보 | [바로가기 파일](../../02-artifacts/file-folder-usage/lnk.md) · [점프리스트](../../02-artifacts/file-folder-usage/jump-lists.md) |
| 8 | SRUM | 앱별 네트워크 사용량. 어느 사이트인지는 없음 | 후보 | [SRUM](../../02-artifacts/execution/system-resource-usage-monitor/index.md) |
| 9 | 페이지 파일·최대 절전 파일 | 디스크에 남은 URL 조각 | 후보 | [메모리 분석](../../03-techniques/analysis/memory-forensics/index.md) · [파일 내용 검색](../../03-techniques/analysis/content-search/index.md) |
| 10 | 조직의 네트워크 기록 | PC 밖에서 본 접속 | [1][2] | — |

"후보" 로 적은 기록은 이번에 연 자료로 확인하지 못했습니다. 시크릿 창을 썼을 때 실제로 무엇이 남는지는 링크한 페이지에서 확인합니다. 검체에서 직접 확인하기 전에는 보고서에 단정해서 쓰지 않습니다.

## 분석 흐름

1. Windows 버전·시간대·사용자를 정리합니다. 설치된 브라우저와 브라우저 프로필 목록을 만듭니다.
2. PC 가 켜져 있으면 시크릿·InPrivate 창이 열려 있는지 확인합니다. 열려 있으면 끄기 전에 메모리를 확보합니다.
3. 일반 프로필의 방문 기록에서 조사 시간대를 봅니다. 그 시간대가 비어 있는지 적어 둡니다.
4. 빈 시간대가 있으면 까닭을 나눕니다. 시크릿 창, 기록 삭제, 다른 브라우저, 다른 프로필, PC 를 쓰지 않은 시간이 모두 후보입니다. 기록 삭제의 흔적은 [웹 사용 행위 재구성](web-activity.md) 에서 봅니다.
5. 북마크·즐겨찾기에서 조사 대상과 관계있는 항목을 찾습니다. Chrome 에서는 시크릿 창에서 저장한 북마크도 일반 쪽에 있습니다[1].
6. 다운로드 폴더와 사용자 폴더에서 조사 시간대에 생긴 파일을 $MFT 로 찾습니다.
7. 찾은 파일이 브라우저의 다운로드 목록에 있는지 봅니다. Edge 에서 목록에 없는 파일은 InPrivate 창에서 받았을 가능성이 있습니다[2]. 목록을 지웠거나 다른 프로그램이 저장했을 가능성도 함께 적습니다.
8. 그 파일의 출처 표시를 확인합니다. 있으면 [다운로드 출처 표시](../../02-artifacts/filesystem/zone-identifier.md) 를 따라 읽습니다.
9. 프리페치·UserAssist 로 그 시간대에 브라우저를 실행했는지 봅니다. 바로가기·점프리스트에 시크릿 창을 여는 인자가 있는지도 봅니다.
10. SRUM 에서 그 시간대 브라우저의 네트워크 사용량을 봅니다. 이 값으로는 어느 사이트인지 알 수 없습니다.
11. 메모리·페이지 파일·최대 절전 파일에서 사이트 주소를 문자열로 찾습니다.
12. 모든 시각을 UTC 로 맞춰 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다.

## 흔한 오판

1. **방문 기록이 비어 있으니 시크릿 창을 썼다고 봅니다.** 기록 삭제, 다른 브라우저, 다른 프로필로도 같은 빈자리가 생깁니다. 빈자리만으로 시크릿 창 사용을 단정하지 않습니다.
2. **시크릿 창은 아무것도 남기지 않는다고 봅니다.** 내려받은 파일과 북마크·즐겨찾기는 남습니다[1][2]. 방문한 사이트[1]와 네트워크 관리자[1][2]도 활동을 볼 수 있을지 모릅니다.
3. **다운로드 목록에 없으니 내려받지 않았다고 봅니다.** Edge 는 InPrivate 창을 닫을 때 다운로드 기록을 지우고 파일은 남깁니다[2]. 파일 시스템에서 파일을 직접 찾습니다.
4. **북마크가 일반 프로필에 있으니 일반 창에서 저장했다고 봅니다.** Chrome 시크릿 창에서 저장한 북마크는 일반 브라우징 쪽으로 넘어갑니다[1].
5. **브라우저 실행 흔적을 시크릿 창 사용의 증거로 씁니다.** 실행 흔적으로는 그 브라우저를 실행했다는 것까지만 말합니다.
6. **Firefox 도 Chrome·Edge 와 같다고 봅니다.** 이 페이지에서는 Firefox 의 동작을 확인하지 못했습니다. [파이어폭스](../../02-artifacts/browsers/firefox/index.md) 에서 따로 확인합니다.
7. **PC 를 먼저 끄고 디스크 이미지를 만듭니다.** 시크릿 창이 열려 있었다면 창을 닫거나 PC 를 끄는 순간 세션 데이터가 사라질 수 있습니다[1][2].

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 ○○ 에 시크릿 모드로 ○○ 사이트에 접속했습니다."
- 쓸 문장: "사용자 ○○ 프로필의 Edge 방문 기록에는 ○○(UTC)부터 ○○(UTC)까지 항목이 없습니다. 같은 시간대에 `○○\Downloads\○○.zip` 파일이 생겼는데, 이 파일은 Edge 의 다운로드 목록에 없습니다. Microsoft 도움말은 InPrivate 창을 모두 닫으면 다운로드 기록을 지우고 내려받은 파일은 남긴다고 적었습니다. 이 기록은 InPrivate 창에서 파일을 내려받았을 가능성과 맞습니다. 다운로드 목록을 지웠거나 다른 프로그램이 파일을 저장했을 가능성은 배제하지 못했습니다."

## 함께 볼 페이지

- [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) — 방문 기록·쿠키·캐시·북마크 파일의 구조입니다.
- [파이어폭스](../../02-artifacts/browsers/firefox/index.md) — Firefox 사생활 보호 모드의 동작은 여기서 확인합니다.
- [웹 사용 행위 재구성](web-activity.md) — 일반 창의 기록과 기록 삭제의 흔적입니다.
- [이 파일은 어디서 왔나](file-origin.md) · [다운로드 출처 표시](../../02-artifacts/filesystem/zone-identifier.md) — 시크릿 창에서 내려받은 파일을 따라갑니다.
- [메모리 분석](../../03-techniques/analysis/memory-forensics/index.md) · [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) — 켜진 PC 에서 세션 데이터를 확보합니다.
- [SRUM](../../02-artifacts/execution/system-resource-usage-monitor/index.md) — 앱별 네트워크 사용량입니다.
- [증거를 없애려 했나](anti-forensics/index.md) — 기록을 일부러 지운 경우입니다.

## 참고 문헌

1. Google Chrome 도움말, "Browse in Incognito mode" (날짜 표시 없음) — https://support.google.com/chrome/answer/9845881?hl=en
2. Microsoft 지원, "Browse InPrivate in Microsoft Edge" (날짜 표시 없음) — https://support.microsoft.com/en-us/microsoft-edge/browse-inprivate-in-microsoft-edge-cd2c9a48-0bc4-b98e-5e46-ac40c84e27e2
