---
title: "크롬·엣지·웨일"
parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1220
has_children: true
has_toc: false
---

# 크롬·엣지·웨일 (Chromium 계열)

크롬·엣지·브레이브·오페라처럼 Chromium을 바탕으로 한 브라우저는 맥에서도 같은 폴더 구조와 같은 SQLite 파일에 기록을 남겨서, 사용자 데이터 폴더 경로만 브라우저별로 알면 방문·다운로드·쿠키·확장을 한 방법으로 읽을 수 있습니다.

## 왜 중요한가

맥에 기본으로 들어 있는 브라우저는 사파리지만, 사용자가 크롬이나 엣지를 따로 설치해 쓰면 웹 사용 기록은 이 브라우저들의 폴더에 쌓여서 사파리만 보면 놓칩니다. 크롬·크로미움·엣지·브레이브·오페라는 브라우저마다 상위 폴더만 다르고 그 아래 구성은 같아서 [1], 한 브라우저에서 익힌 분석 방법을 다른 브라우저에 그대로 쓸 수 있습니다.

기록은 사용자 데이터 폴더 (User Data Directory) 안의 프로필 (Profile) 폴더마다 따로 쌓입니다 [2]. 프로필 폴더 하나에 방문 기록(`History`), 쿠키(`Cookies`), 저장된 로그인 정보(`Login Data`), 설정(`Preferences`), 확장(`Extensions/`)이 함께 들어 있고 [1][3], 한 맥 계정 안에 브라우저와 프로필이 여러 개 있으면 그만큼 기록 묶음도 여러 개입니다.

시각 값은 대부분 1601-01-01 UTC 기준 마이크로초라서 [3] 맥 절대 시각이나 유닉스 시각과 기준이 다르고, 다른 아티팩트와 한 시간축에 놓으려면 먼저 기준을 맞춥니다. 바꾸는 법은 [방문·다운로드 기록 (History)](history-downloads.md)에서 다룹니다.

## 한눈에 보기

| 기록 | 위치 | macOS·브라우저 버전 | 알려 주는 것 |
|---|---|---|---|
| 사용자 데이터 폴더와 프로필 | `~/Library/Application Support` 아래 브라우저별 폴더, 그 안의 `Default`, `Profile 1` … [2] | 브라우저·채널마다 폴더가 다름 | 어떤 브라우저와 프로필을 썼는지 |
| 방문·다운로드 기록 | `<프로필>/History` [1][3] | 다운로드 표 구성은 브라우저 버전에 따라 바뀜 [3] | 방문한 URL과 방문 방식, 받은 파일과 거친 URL |
| 쿠키·저장된 로그인 정보 | `<프로필>/Cookies` 또는 `Network/Cookies`, `<프로필>/Login Data` [1] | 새 브라우저 버전은 쿠키를 `Network` 아래에 둠 [1] | 어떤 사이트의 쿠키가 언제 생겼는지, 로그인 정보를 저장했는지 |
| 확장 | `<프로필>/Extensions/`, `Preferences`·`Secure Preferences` [1][3] | 브라우저 버전에 따른 차이는 실제 데이터로 확인 | 어떤 확장이 어떤 경로로 설치됐는지 |

위 표의 `<프로필>` 은 사용자 데이터 폴더 안의 프로필 폴더를 뜻합니다. 이 경로와 형식은 macOS 버전보다 브라우저 버전에 따라 달라집니다. 웨일 (Whale)처럼 맥 경로를 분석 대상에서 직접 찾아야 하는 브라우저는 [맥에서의 위치와 프로필 (Profiles)](profiles.md)에 찾는 법을 적었습니다.

## 읽는 순서

1. [맥에서의 위치와 프로필 (Profiles)](profiles.md) — 브라우저별 사용자 데이터 폴더, 프로필 폴더 구성, `~/Library/Caches` 쪽 캐시 위치, 기본 경로 밖의 프로필을 찾는 법을 다룹니다.
2. [방문·다운로드 기록 (History)](history-downloads.md) — `urls`·`visits`·`downloads` 표와 transition 값 풀이, 1601 기준 시각을 바꾸는 SQL을 다룹니다.
3. [쿠키와 저장된 암호 (Cookies·Login Data)](cookies-login-data.md) — 쿠키 DB의 열과 두 저장 위치, 맥에서 값에 붙는 `v10` 암호화 형식과 키체인과의 관계를 다룹니다.
4. [확장 (Extensions)](extensions.md) — 확장 폴더와 설치 위치 값, 외부 확장 설정 파일, 사고 대응 때 먼저 볼 값을 다룹니다.

## 함께 볼 페이지

- [사파리 (Safari)](../safari/index.md), [파이어폭스 (Firefox)](../firefox.md) — 같은 사용자의 다른 브라우저 기록
- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) — `History`·`Cookies`·`Login Data` 의 저장 형식
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) — 시각 기준끼리의 관계
- [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md) — 브라우저로 받은 파일에 남는 다른 기록
- [키체인 (Keychain)](../../../01-foundations/protection/keychain/index.md) — 쿠키·암호 값 암호화에 쓰는 비밀번호가 있는 곳
- [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md)
- [개인 정보 보호 브라우징으로 무엇을 했나 (Private Browsing)](../../../04-scenarios/activity/private-browsing.md)
- [정보 탈취 악성 코드 (Infostealer)](../../../04-scenarios/incident/infostealer.md)

## 참고 문헌

1. ForensicArtifacts, webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
2. Chromium Docs, "User Data Directory" — https://chromium.googlesource.com/chromium/src/+/HEAD/docs/user_data_dir.md
3. Forensics Wiki, "Google Chrome" — https://forensics.wiki/google_chrome/
