---
title: "맥에서의 위치와 프로필"
parent: "크롬·엣지·웨일"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1230
---

# 맥에서의 위치와 프로필 (Profiles)

크롬·엣지 같은 Chromium 계열 브라우저는 `~/Library/Application Support` 아래의 브라우저별 사용자 데이터 폴더에 기록을 남기고, 그 안의 프로필 폴더마다 방문 기록·쿠키·확장이 따로 쌓여서 분석은 이 폴더를 찾고 프로필을 가르는 데서 시작합니다.

## 무엇을 기록하나 · 왜 생기나

사용자 데이터 폴더 (User Data Directory)는 브라우저 하나가 쓰는 데이터를 모두 담는 최상위 폴더이고, 프로필 (Profile)은 그 안의 하위 폴더입니다 [1]. 첫 프로필 폴더 이름은 보통 `Default` 이고, 프로필을 더 만들면 `Profile 1`, `Profile 2` 처럼 이어 붙습니다 [1]. 방문 기록·북마크·쿠키 같은 데이터는 프로필 폴더에 들어가서 [1] 같은 맥 계정 안에서도 프로필마다 기록이 따로 남습니다.

크롬·크로미움·엣지·브레이브·오페라는 같은 Chromium 구조를 쓰고, 브라우저마다 상위 폴더만 다릅니다 [3]. 그래서 아래의 프로필 구조는 브라우저가 달라도 그대로 쓸 수 있고, 브라우저마다 달라지는 것은 사용자 데이터 폴더 경로입니다.

## 위치와 버전별 차이

### 사용자 데이터 폴더

| 브라우저 | 사용자 데이터 폴더 | 출처 |
|---|---|---|
| Chrome | `~/Library/Application Support/Google/Chrome` | [1] |
| Chrome Beta | `~/Library/Application Support/Google/Chrome Beta` | [1] |
| Chrome Dev | `~/Library/Application Support/Google/Chrome Dev` | [1] |
| Chrome Canary | `~/Library/Application Support/Google/Chrome Canary` | [1] |
| Chromium | `~/Library/Application Support/Chromium` | [1] |
| Edge | `~/Library/Application Support/Microsoft Edge` | [3] |
| Edge Beta | `~/Library/Application Support/Microsoft Edge Beta` | [3] |
| Brave | `~/Library/Application Support/BraveSoftware/Brave-Browser` | [3] |
| Opera | `~/Library/Application Support/com.operasoftware.Opera` | [3] (확장 경로만 정의에 있음) |

크롬은 채널(Beta·Dev·Canary)마다 폴더가 따로 있어서, 한 사용자가 여러 채널을 썼다면 폴더도 여러 개 남습니다. Edge Dev·Canary, 비발디 (Vivaldi), 웨일 (Whale)의 맥 경로는 공개 자료에 나와 있지 않아 분석 대상에서 직접 찾습니다. 경로를 모르는 Chromium 계열 브라우저는 사용자 홈의 `~/Library/Application Support` 아래에서 `Local State` 파일이 있고 그 하위 폴더에 `History` 파일이 있는 폴더를 찾아 가려낼 수 있습니다.

이 경로와 파일 형식은 macOS 버전보다 브라우저 버전에 따라 달라집니다. 쿠키 파일 위치나 다운로드 표 구성이 그런 예이고, 그 내용은 각 하위 페이지에서 다룹니다.

### 기본 경로 밖의 프로필

브라우저를 `--user-data-dir` 명령줄 인자와 함께 실행하면 사용자 데이터 폴더를 다른 곳으로 바꿀 수 있고, 맥에서는 AppleScript로 이 인자를 붙여 브라우저를 여는 앱을 만들 수 있습니다 [1]. 기본 경로에 기록이 없거나 너무 적다면 다른 위치에 사용자 데이터 폴더가 있을 수 있어서, 볼륨 전체에서 `Local State` 와 `History` 파일 이름을 찾아봅니다.

### 캐시 폴더

맥에서는 캐시가 프로필과 다른 곳에 있습니다. 프로필이 `Library/Application Support` 아래에 있으면 캐시는 `Library/Caches` 아래의 같은 상대 경로에 만들어지고, 예를 들어 프로필 `~/Library/Application Support/Google/Chrome/Default` 의 캐시는 `~/Library/Caches/Google/Chrome/Default` 에 있습니다 [1].

```
~/Library/Caches/Google/Chrome/<프로필>/Cache
~/Library/Caches/Google/Chrome/<프로필>/Media Cache
~/Library/Caches/Google/Chrome/PnaclTranslationCache/
~/Library/Application Support/Google/Chrome/<프로필>/GPUCache/
~/Library/Application Support/Google/Chrome/<프로필>/Application Cache/Cache/
```

위 경로들은 오래된 브라우저 버전의 캐시 관련 폴더라서 최신 버전에는 없는 폴더도 있을 수 있고, 캐시 파일은 `index`, `data_#`, `f_######` 로 이루어진 Chrome 디스크 캐시 형식 (Chrome Disk Cache Format)입니다 [2]. 캐시는 프로필 폴더 아래의 `Cache` 와 `~/Library/Caches` 아래의 `Cache` 두 곳에 있을 수 있어서 [3], 한 곳에서만 찾으면 놓칠 수 있습니다. 두 곳을 다 봅니다.

## 구조

크롬 기본 경로를 예로 들면, 사용자 데이터 폴더 바로 아래에 `Local State` 가 있고 프로필 폴더 안에 브라우저 기록 파일들이 있습니다 [2][3].

```
~/Library/Application Support/Google/Chrome/
├── Local State
├── Default/
│   ├── History
│   ├── Archived History
│   ├── Visited Links
│   ├── Cookies            (새 버전은 Network/Cookies)
│   ├── Login Data
│   ├── Web Data
│   ├── Preferences
│   ├── Secure Preferences
│   └── Extensions/
└── Profile 1/
    └── (Default 와 같은 구성)
```

| 파일 | 담긴 것 | 자세한 설명 |
|---|---|---|
| `History`, `Archived History`, `Visited Links` | 방문·다운로드 기록 | [방문·다운로드 기록 (History)](history-downloads.md) |
| `Cookies`, `Login Data`, `Web Data` | 쿠키와 저장된 로그인 정보 | [쿠키와 저장된 암호 (Cookies·Login Data)](cookies-login-data.md) |
| `Extensions/` | 설치된 확장 파일 | [확장 (Extensions)](extensions.md) |
| `Preferences`, `Secure Preferences` | 프로필 설정(JSON) [2] | 이 페이지 |
| `Local State` | 사용자 데이터 폴더 전체의 설정 [2] | 이 페이지 |

`Preferences` 와 `Secure Preferences` 는 JSON 파일이라 텍스트로 열어 볼 수 있습니다 [2]. 다만 `Local State` 안에서 프로필 목록과 표시 이름·계정 정보를 담는 키, `Preferences` 안에서 로그인 계정과 동기화 상태를 담는 키는 정리된 공개 자료가 없습니다. 특정 키 이름을 근거로 보고서를 쓰기 전에는 분석 대상의 브라우저 버전에서 그 키가 실제로 무엇을 담는지 먼저 확인합니다. 저장 형식 자체는 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 이 macOS 계정의 홈 폴더에 어떤 Chromium 계열 브라우저의 사용자 데이터 폴더가 있고, 그 안에 어떤 프로필 폴더들이 있다는 점입니다. 프로필 폴더마다 기록이 따로 남아서 어느 프로필에서 생긴 기록인지 가를 수 있습니다.

**증명하지 못하는 것.** 폴더가 있다는 점만으로 그 브라우저를 언제, 얼마나 썼는지는 알 수 없고, 사용 시기는 프로필 안의 기록 시각으로 따로 확인합니다. 프로필 하나를 여러 사람이 썼는지, 프로필이 다른 기기와 동기화된 계정에 연결되어 있었는지도 폴더 구조만으로는 알 수 없습니다. `Profile 1` 같은 폴더 이름과 화면에 보이는 프로필 이름을 잇는 키를 실제 데이터로 확인하기 전에는, 폴더 이름만 보고 프로필 이름이나 계정을 적지 않습니다.

보고서에는 "이 사용자 홈 폴더에 크롬 사용자 데이터 폴더가 있고, 그 안에 `Default` 와 `Profile 1` 두 프로필이 있다" 처럼 폴더 구성만 적고, 사용 행위는 각 기록 페이지의 근거로 따로 씁니다.

## 함정과 한계

- **프로필 하나만 보기.** `Default` 만 보면 다른 프로필의 기록을 놓칩니다. 사용자 데이터 폴더 아래의 하위 폴더를 모두 확인합니다.
- **채널과 브라우저 여러 개.** Chrome과 Chrome Beta·Canary, Edge, Brave는 폴더가 모두 따로라서 한 사용자에게 사용자 데이터 폴더가 여러 개 있을 수 있습니다.
- **바꾼 사용자 데이터 폴더.** `--user-data-dir` 로 실행하면 기본 경로 밖에 기록이 쌓입니다 [1]. 파일 이름으로 볼륨 전체를 찾아봅니다.
- **캐시 위치.** 맥에서는 캐시가 `~/Library/Caches` 쪽에 따로 있어서 [1], 사용자 데이터 폴더만 수집하면 캐시가 빠집니다.
- **공개되지 않은 경로.** Edge Dev·Canary, 비발디, 웨일의 맥 경로는 공개 자료가 없습니다. 분석 대상에서 찾은 경로는 찾은 대로 기록하고, 공개 자료로 확인되는 경로와 구분해 적습니다.

## 직접 분석해 보기

### 파일 이름으로 한 번

증거물 볼륨을 읽기 전용으로 붙인 뒤, 사용자 데이터 폴더와 프로필 폴더를 파일 이름으로 찾습니다. `Local State` 가 있는 폴더가 사용자 데이터 폴더이고, `History` 가 있는 폴더가 프로필 폴더입니다.

```sh
find "/Volumes/<검체>/Users" -name "Local State" 2>/dev/null
find "/Volumes/<검체>/Users" -name "History" -path "*Application Support*" 2>/dev/null
```

기본 경로 밖의 사용자 데이터 폴더까지 찾으려면 `-path` 조건을 빼고 볼륨 전체를 봅니다. `Preferences` 는 JSON이라서 `python3 -m json.tool Preferences` 처럼 들여쓰기를 맞춰 읽으면 키 구조를 따라가기 쉽습니다. 원본이 아닌 사본으로 작업합니다.

### 공개 도구로 한 번

ForensicArtifacts 정의에는 브라우저별 경로가 모여 있어서 [3], 이 정의를 읽는 공개 수집 도구를 쓰면 여러 브라우저의 프로필 파일을 한 번에 모을 수 있습니다. 도구 결과에 나온 프로필 폴더 목록을 위의 `find` 결과와 맞춰 보면, 정의에 없는 브라우저나 바뀐 경로 때문에 빠진 폴더를 찾을 수 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [사용자 계정 (Local Accounts)](../../system-account/user-accounts/index.md) | 사용자 데이터 폴더가 있는 홈 폴더가 어느 계정의 것인지 확인합니다 |
| [설치한 앱과 영수증 (Applications·Receipts)](../../system-account/installed-apps-receipts.md) | 사용자 데이터 폴더가 있는 브라우저가 설치되어 있었는지 봅니다 |
| [KnowledgeC (knowledgeC.db)](../../execution/knowledgec/index.md), [바이옴 (Biome)](../../execution/biome/index.md) | 브라우저 앱을 실제로 쓴 시기를 맞춰 봅니다 |
| [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) | 프로필 폴더가 만들어지거나 지워진 흔적을 찾습니다 |
| [타임 머신 (Time Machine)](../../filesystem/time-machine/index.md) | 백업에 남은 예전 프로필 폴더와 지금 폴더를 비교합니다 |

## 실습

공개 시험 자료(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 이미지에 있는 사용자마다 Chromium 계열 사용자 데이터 폴더가 몇 개 있는지 세어 보세요.
2. 각 사용자 데이터 폴더 안의 프로필 폴더 이름을 모두 적고, 프로필마다 `History` 파일이 있는지 확인해 보세요.
3. 크롬 프로필 하나를 골라 `~/Library/Caches` 쪽에 짝이 되는 캐시 폴더가 있는지 찾아보세요.
4. 기본 경로 밖에 `Local State` 파일이 있는지 볼륨 전체에서 찾아보세요.

## 참고 문헌

1. Chromium Docs, "User Data Directory" — https://chromium.googlesource.com/chromium/src/+/HEAD/docs/user_data_dir.md
2. Forensics Wiki, "Google Chrome" — https://forensics.wiki/google_chrome/
3. ForensicArtifacts, webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
