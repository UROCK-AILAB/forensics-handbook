---
title: "인터넷 익스플로러·옛 엣지"
parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1790
has_children: true
has_toc: false
---

# 인터넷 익스플로러·옛 엣지 (IE·EdgeHTML)

## 한 줄 요약

인터넷 익스플로러 (Internet Explorer, IE) 는 Windows 의 구성 요소인 브라우저입니다. 옛 엣지 (Microsoft Edge Legacy) 는 EdgeHTML 엔진을 쓰던 예전 Edge 입니다. IE 4~9 는 방문 기록·캐시·쿠키·내려받기 기록을 `index.dat` 파일에 둡니다. IE 10 이후와 옛 엣지는 같은 기록을 ESE 데이터베이스인 `WebCacheV*.dat` 에 둡니다. 주소창 입력 주소·저장 비밀번호·즐겨찾기는 레지스트리와 사용자 폴더에 따로 남습니다.

## 왜 중요한가

- IE 는 Windows 의 구성 요소라서 설치된 Windows 의 지원 정책을 따릅니다.
- Windows 11 25H2 에도 IE 의 기록 자리가 남아 있습니다. 이 판에서 `HKLM\SOFTWARE\Microsoft\Internet Explorer` 의 `svcVersion` 값은 `11.1882.26100.0` 입니다.
- Windows 11 25H2 에도 WebCache 폴더, `INetCache`·`INetCookies` 폴더, `TypedURLs` 키, `IntelliForms` 키, `%USERPROFILE%\Favorites` 폴더가 모두 있고, 옛 엣지 패키지 폴더는 없습니다.
- IE 10 이후에는 방문 기록·캐시·쿠키·내려받기 기록이 사용자마다 파일 하나에 모이고, 그 파일 하나로 웹 사용의 큰 줄기를 볼 수 있습니다.
- IE 4~9 를 쓰던 옛 시스템에서는 `index.dat` 가 주된 기록입니다. 그래서 분석 대상의 IE 버전부터 확인합니다.
- 엣지 안의 IE 모드는 최소 2029년까지 지원합니다. IE 모드가 어느 파일에 기록을 남기는지는 실제 데이터로 확인해야 합니다.

증명하지 못하는 것도 있습니다.

- 폴더와 키가 있다는 것만으로 사용자가 IE 를 썼다고 단정하지 않습니다. Windows 11 25H2 에도 폴더와 키가 모두 있습니다.
- IE 와 옛 엣지는 같은 `WebCacheV01.dat` 를 씁니다. 그래서 이 파일의 기록을 IE 사용 흔적이라고 바로 단정하지 않습니다.
- 기록은 Windows 계정 단위로 남을 뿐, 그 시각에 누가 키보드 앞에 있었는지는 남지 않습니다. 사람을 좁히는 법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- 기록이 없다고 방문하지 않은 것은 아니며, 사용자가 지웠을 수 있습니다. 이전 시점의 파일은 [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 꺼내 비교합니다.

## 한눈에 보기

> 그림 자리: IE 4~9 의 기록 종류별 `index.dat` 폴더들과, IE 10 이후·옛 엣지가 함께 쓰는 `WebCacheV01.dat` 하나를 나란히 놓고, 레지스트리(TypedURLs·IntelliForms)와 즐겨찾기 폴더를 옆에 붙여 보여 주는 그림

### 버전마다 기록을 두는 곳

| 브라우저 | 방문 기록·캐시·쿠키·내려받기 기록 | 형식 |
|---|---|---|
| IE 4~9 | 기록 종류별 폴더(`History.IE5`·`Content.IE5`·`Cookies`·`IEDownloadHistory` 등)의 `index.dat` | `index.dat` 전용 형식 |
| IE 10·11 | `%LOCALAPPDATA%\Microsoft\Windows\WebCache\WebCacheV*.dat` (사용자마다 하나) | ESE |
| 옛 엣지 | 같은 `WebCacheV01.dat` 안의 서로 다른 컨테이너 | ESE |

- 파일 이름은 `WebCacheV01.dat` 와 `WebCacheV24.dat` 두 가지가 있습니다[2].
- 옛 엣지는 전용 폴더 `C:\Users\<사용자>\AppData\Local\Packages\Microsoft.MicrosoftEdge_8wekyb3d8bbwe\` 도 씁니다. 공개 수집 정의 `Edge.tkape` 는 이 폴더 아래를 모두 모읍니다[6].

### 지원 종료 시점

IE·옛 엣지의 지원 종료 시점입니다[5]. 분석 대상의 Windows 판과 날짜를 보고, 그 시점에 IE·옛 엣지를 쓸 수 있었는지 판단할 때 씁니다.

| 대상 | 내용 |
|---|---|
| IE 11 | 마지막 주 버전입니다 |
| Windows 10 반기 채널 (SAC)·Windows 10 IoT 의 IE 11 데스크톱 앱 | 2022-06-15 에 지원이 끝났습니다 |
| 일부 Windows 10 버전의 IE 11 데스크톱 앱 | "영구히 사용 불가" 로 바뀌었습니다 |
| Windows 10 LTSB 2015·2016, LTSC 2019·2021, Windows 8.1, Windows 7 ESU, Windows Server 2012~2022 | IE 11 지원 대상입니다 |
| 엣지 안의 IE 모드 | 최소 2029년까지 지원합니다 |
| 옛 엣지 데스크톱 앱 | 2021-03-09 에 지원이 끝났습니다 |

- 이 지원 목록에 Windows 11 은 없습니다[5].
- "영구히 사용 불가" 조치가 적용된 날짜와 옛 엣지가 새 엣지로 바뀐 시점은 분석 대상의 업데이트 기록에서 확인합니다.

### 알려 주는 것

| 알 수 있는 것 | 어디에 남나 | 쓰는 버전 | 자세히 |
|---|---|---|---|
| 방문 기록·캐시 목록·쿠키·내려받기 기록 | `WebCacheV*.dat` | IE 10 이후, 옛 엣지 | [웹캐시 DB](webcachev01-dat.md) |
| 같은 기록의 옛 형식 | 기록 종류별 폴더의 `index.dat` | IE 4~9 | [옛 기록 파일](index-dat.md) |
| 주소창에 입력한 주소와 입력 시각 | NTUSER.DAT 의 `Software\Microsoft\Internet Explorer\TypedURLs`·`TypedURLsTime` | 시각 키는 Windows 8 에서 소개됐습니다 | [주소창 입력 주소](typedurls-typedurlstime.md) |
| 사이트별로 저장한 아이디·비밀번호 | NTUSER.DAT 의 `Software\Microsoft\Internet Explorer\IntelliForms\Storage2` | IE 7~9 | [저장 비밀번호](intelliforms.md) |
| 받아 둔 웹 자원 파일·쿠키 폴더 | `%LOCALAPPDATA%\Microsoft\Windows\INetCache\IE` (IE 10 이후), `…\Temporary Internet Files\Content.IE5` (IE 4~9), `INetCookies` | IE 4 이후 | [쿠키·캐시 폴더](inetcookies-inetcache.md) |
| 즐겨찾기 | `%USERPROFILE%\Favorites` 의 `.url` 파일, 옛 엣지는 `spartan.edb` | IE, 옛 엣지 | [즐겨찾기](favorites-url.md) |

하위 페이지에 없는 자리도 하나 있습니다. Vista 이후 IE 는 탭 복구용 폴더 `C:\Users\<사용자>\AppData\Local\Microsoft\Internet Explorer\Recovery` 를 씁니다[2]. 수집할 때는 이 폴더도 함께 모읍니다.

## 읽는 순서

1. [웹캐시 DB (WebCacheV01.dat)](webcachev01-dat.md) — IE 10 이후와 옛 엣지의 방문 기록·캐시·쿠키·내려받기 기록을 ESE 데이터베이스에서 읽습니다. 잠긴 파일의 사본을 뜨는 법과 비정상 종료 상태를 다루는 법도 봅니다.
2. [옛 기록 파일 (index.dat)](index-dat.md) — IE 4~9 의 기록 파일을 머리글과 레코드 단위로 읽습니다. 파일 종류마다 두 시각의 뜻이 어떻게 다른지 봅니다.
3. [주소창 입력 주소 (TypedURLs·TypedURLsTime)](typedurls-typedurlstime.md) — 사용자 하이브에서 주소창에 입력한 주소와 입력 시각을 짝지어 읽습니다.
4. [저장 비밀번호 (IntelliForms)](intelliforms.md) — IE 7~9 가 저장한 아이디·비밀번호를 사이트 주소와 DPAPI 로 푸는 흐름을 봅니다. HTTP 기본 인증 비밀번호가 들어가는 곳도 다룹니다.
5. [쿠키·캐시 폴더 (INetCookies·INetCache)](inetcookies-inetcache.md) — 캐시 파일과 쿠키 폴더를 찾고, 어느 파일이 어느 주소에서 왔는지 기록 파일로 잇습니다.
6. [즐겨찾기 (Favorites .url)](favorites-url.md) — 즐겨찾기 폴더의 `.url` 파일을 글자로 읽고, 시각은 파일 시스템에서 가져옵니다. 옛 엣지의 즐겨찾기 자리도 봅니다.

## 함께 볼 페이지

- [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) — `WebCacheV*.dat` 와 `spartan.edb` 의 저장 형식입니다.
- [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) — `TypedURLs`·`IntelliForms` 가 들어 있는 NTUSER.DAT 의 구조입니다.
- [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) — 저장 비밀번호를 풀 때 필요한 Windows 보호 구조입니다.
- [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) — WebCache 와 `index.dat` 의 시각 값을 바꾸는 법입니다.
- [UWP 앱 데이터 구조](../../../01-foundations/app-mail-data/packages-settings-dat.md) — 옛 엣지 패키지 폴더의 짜임입니다.
- [자격 증명 관리자와 볼트](../../credentials/credential-manager-windows-vault.md) — HTTP 기본 인증 비밀번호가 들어가는 `Credentials` 폴더를 다룹니다.
- [크롬 계열 브라우저](../chrome-edge-whale/index.md) — 지금의 Edge 는 크롬 계열입니다. 옛 엣지와 이름만 같고 기록 방식이 다릅니다.
- [파이어폭스](../firefox/index.md) — 구조가 다른 또 하나의 브라우저입니다.
- [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) — 여러 브라우저의 기록을 한 타임라인으로 묶는 순서입니다.

## 참고 문헌

1. ForensicArtifacts, *artifacts/data/webbrowser.yaml* (IE 4~9 와 IE 10 이후의 기록·캐시 파일 경로). https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
2. Forensics Wiki, *Internet Explorer* (WebCache 파일 이름과 ESE 형식, `TypedURLs` 키, 탭 복구 폴더). https://forensics.wiki/internet_explorer
3. SecurityXploded, IE 비밀번호 저장·복호 방식 설명 글 (IE 7~9 의 `IntelliForms\Storage2`). https://securityxploded.com/iepasswordsecrets.php
4. RegRipper 3.0, *plugins/typedurlstime.pl* (`TypedURLsTime` 키와 Windows 8 에서의 소개). https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/typedurlstime.pl
5. Microsoft Learn, *Lifecycle FAQ - Internet Explorer and Microsoft Edge* (IE·옛 엣지 지원 종료 시점, IE 모드 지원 기간). https://learn.microsoft.com/en-us/lifecycle/faq/internet-explorer-microsoft-edge
6. EricZimmerman/KapeFiles, *Targets/Browsers/Edge.tkape* (옛 엣지 패키지 폴더). https://raw.githubusercontent.com/EricZimmerman/KapeFiles/master/Targets/Browsers/Edge.tkape
7. Forensafe 블로그, 옛 엣지(EdgeHTML) 아티팩트 설명 글 (옛 엣지의 WebCacheV01.dat 컨테이너와 `spartan.edb`). https://www.forensafe.com/blogs/microsoftedge.html
