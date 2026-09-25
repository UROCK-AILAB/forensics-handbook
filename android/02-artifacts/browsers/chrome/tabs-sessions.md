---
title: "탭과 세션"
parent: "크롬"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 840
---

# 탭과 세션 (Tabs·Sessions)

## 한 줄 요약

Chrome for Android 는 열린 탭을 다시 띄우려고 탭마다 상태 파일(TabState)을 앱 데이터의 탭 폴더에 저장하고, 이 파일에 탭의 현재 URL 과 탭을 연 앱, 마지막 탐색 시각 같은 값이 들어 있으며, 시크릿(incognito) 탭은 따로 암호화한 파일로 저장합니다 (현행 Chromium 기준) [1][2].

## 무엇을 기록하나 · 왜 생기나

앱을 다시 열었을 때 탭을 되살리려고 Chrome 은 탭 모델(TabModel)의 메타데이터와 탭별 상태를 탭 상태 폴더에 적어 둡니다 [2]. [방문 기록 (History)](history.md)이 지나간 방문을 쌓는 기록이라면, 탭 상태 파일은 저장한 시점에 열려 있던 탭의 모습을 보여 준다는 점이 다릅니다.

공개 도구 ALEAPP 의 Chrome 모듈 세 개(방문 기록, 쿠키, 자동 완성)에는 탭 상태 파일을 읽는 부분이 없어서 [3], 이 페이지의 구조는 Chromium 소스를 읽어 정리한 것입니다. 소스는 main 가지를 읽었고 특정 Chrome 버전의 태그가 아니라서, 설명은 모두 현행 Chromium 기준입니다.

## 위치와 버전별 차이

탭 상태 기본 폴더는 Chrome 이 `Context.getDir("tabs", MODE_PRIVATE)` 로 만듭니다(BASE_STATE_FOLDER = "tabs") [2]. getDir 로 만든 폴더는 디스크에서 이름 앞에 `app_` 이 붙는다고 보고 실제 폴더를 `app_tabs` 로 풀이하는데, 이 이름 규칙 문서를 직접 확인하지는 못했습니다. 같은 규칙으로 생기는 `app_chrome`, `app_webview` 가 ALEAPP 경로 패턴과 맞는다는 점만 확인했습니다 [3]. 앱 데이터 폴더 자체는 [앱 데이터 폴더 구조 (/data/data·/data/user)](../../../01-foundations/storage/app-data-layout.md), 패키지 이름은 [크롬 (Chrome for Android)](index.md) 허브를 봅니다.

기본 폴더 아래 하위 폴더 하나가 탭 모델 선택기(TabModelSelector) 하나의 상태를 담습니다 [2].

| 하위 폴더 | 쓰임 |
|---|---|
| `0` (TABBED_MODE_DIRECTORY) | 일반 탭 모드 |
| `custom_tabs` (CUSTOM_TABS_DIRECTORY) | 다른 앱이 Chrome 으로 띄운 맞춤 탭(Custom Tabs) |

파일 형식은 옛 형식(손으로 짠 직렬화)과 FlatBuffer 형식 두 가지가 있고, 옛 형식에서 FlatBuffer 로 옮기는 중에는 한 탭에 두 형식 파일이 함께 있을 수 있습니다. 소스에 "FlatBuffer 로 옮겼지만 옛 파일을 아직 지우지 않은" 상태가 따로 있습니다 [1]. 어느 Chrome 버전부터 FlatBuffer 를 쓰는지는 확인하지 못했습니다.

## 구조

### 파일 이름

| 파일 이름 | 뜻 |
|---|---|
| "tab" + 탭 번호 | 일반 탭 상태(SAVED_TAB_STATE_FILE_PREFIX) [1] |
| "cryptonito" + 탭 번호 | 시크릿 탭 상태, 암호화해 저장(CipherFactory, Cipher.ENCRYPT_MODE) [1] |
| 앞에 "flatbufferv1_" 이 붙은 이름 | 같은 탭의 FlatBuffer 형식 파일 [1] |
| "tab_state" + 고유 태그 | 탭 모델 메타데이터(TabMetadataFileManager.SAVED_METADATA_FILE_PREFIX) [4] |

예를 들면 `tab15`, `cryptonito15`, `flatbufferv1_tab15` 같은 모양이 됩니다(번호는 설명용). 메타데이터 파일에 붙는 고유 태그의 실제 값과 파일 안 구조는 확인하지 못했습니다.

복원할 때는 암호화하지 않은 파일을 먼저 찾고, 없으면 cryptonito 파일을 찾습니다. 탭을 닫아 지우면 deleteTabState 가 옛 형식과 FlatBuffer 형식 파일을 모두 지웁니다 [1].

### 옛 형식 TabState 안의 순서

저장 코드(saveState)가 쓰는 순서는 아래와 같습니다 [1].

| 순서 | 값 | 비고 |
|---|---|---|
| (암호화 파일만) | KEY_CHECKER | long 값 0 |
| 1 | timestampMillis | long |
| 2 | WebContents 상태 바이트 길이 + 그 바이트 | int 와 바이트 묶음. 탐색 기록 등이 들어 있습니다 |
| 3 | parentId | int |
| 4 | openerAppId | 문자열. 탭을 연 앱의 ID, 없으면 소스에서 NULL_STR 로 정한 값 |
| 5 | WebContents 상태 버전 | int |
| 6 | 옛 sync ID 자리, 옛 SHOULD_PRESERVE 자리 | long(-1), boolean(false) |
| 7 | themeColor | int |
| 8 | tabLaunchTypeAtCreation | int. 탭이 어떻게 만들어졌는지 |
| 9 | rootId | int |
| 10 | userAgent | int |
| 11 | lastNavigationCommittedTimestampMillis | long. 마지막으로 탐색이 확정된 시각 |
| 12 | 탭 그룹 ID | long 두 개, 둘 다 0 이면 그룹 없음 |
| 13 | tabHasSensitiveContent | boolean |
| 14 | isPinned | boolean |
| 15 | url | 문자열. 탭의 현재 URL |

읽는 코드는 뒤쪽 칸이 없어 파일 끝(EOFException)을 만나면 기본값으로 넘어가서 [1], 오래된 Chrome 이 쓴 파일에는 뒤쪽 칸이 아예 없을 수 있습니다. tabLaunchTypeAtCreation 의 숫자별 뜻은 확인하지 못했습니다.

## 증거로서 의미

| 기록 | 말할 수 있는 것 | 말할 수 없는 것 |
|---|---|---|
| "tab" 파일의 url | 파일을 저장한 시점에 그 URL 이 일반 탭에 열려 있었다 | 사용자가 그 탭을 마지막으로 본 시각 |
| openerAppId | 이 탭을 연 앱으로 적힌 ID | 사용자가 그 앱에서 링크를 눌렀다는 단정 |
| `custom_tabs` 아래 파일 | 다른 앱이 맞춤 탭으로 띄운 탭의 상태 | 어느 앱이 띄웠는지(openerAppId 등으로 따로 확인) |
| "cryptonito" 파일 | Chrome 이 시크릿 탭 상태를 암호화해 저장한 적이 있다 | 시크릿 탭에서 무엇을 봤는지 |
| isPinned, 탭 그룹 ID | 탭이 고정되었거나 그룹에 들어 있었다 | 누가 그렇게 설정했는지 |

openerAppId 는 링크를 눌러 Chrome 이 열린 경로를 따질 때 단서가 되고, 문자로 받은 링크를 따라간 사건이라면 [스미싱 흔적 (Smishing)](../../../04-scenarios/incident/smishing.md) 페이지와 함께 봅니다. 앱 ID 가 가리키는 앱이 기기에 있었는지는 [설치된 앱 (packages.xml)](../../app-usage/packages/index.md)에서 확인합니다.

## 시각 해석

탭 상태 파일의 시각 칸(timestampMillis, lastNavigationCommittedTimestampMillis)은 이름이 …Millis 인 long 값이지만, 기준 에포크가 유닉스 시각인지는 이번에 읽은 소스만으로는 확인하지 못했습니다 [1]. 두 칸을 유닉스 밀리초로 풀어 본 뒤에는 같은 URL 의 [방문 기록 (History)](history.md) visit_time 과 맞는지 대 보고, 맞을 때만 보고서에 시각으로 씁니다. 방문 기록의 시각은 1601년 기준 마이크로초라서 단위와 기준이 다르다는 점에 주의합니다. 시각 형식을 바꾸는 법은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

## 함정과 한계

시크릿 탭 상태는 cryptonito 파일에 암호화되어 있고, 소스 로그에 "Encryption key has changed, cannot restore incognito TabState" 가 있어 키가 바뀌면 Chrome 자신도 복원하지 못합니다 [1]. 키를 어디에 두는지, 앱을 끈 뒤에도 파일이 남는지는 확인하지 못했습니다. 이 페이지는 이 파일을 푸는 방법을 다루지 않고, 파일이 있다는 사실과 이름, 개수까지만 기록합니다.

데스크톱 Chrome 의 Sessions 폴더(`Session_*`, `Tabs_*` 파일)가 Android 에도 있는지, 최근에 닫은 탭과 동기화된 다른 기기의 탭이 어느 파일에 남는지는 확인하지 못했습니다. 탭을 닫으면 해당 탭 파일을 지우는 코드가 있어서 [1], 탭 폴더에 파일이 없다는 것만으로 그 URL 을 열지 않았다고 말하지 않습니다. 지운 파일의 흔적은 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md) 페이지를 봅니다.

한 탭에 옛 형식과 FlatBuffer 형식 파일이 함께 있으면 두 파일의 내용이 다를 수 있으니, 두 파일을 따로 읽고 어느 쪽이 나중에 쓰였는지 파일 시스템 시각으로 확인합니다. 파일 시스템 시각은 [파일 시스템 (ext4·F2FS)](../../../01-foundations/storage/filesystems/index.md) 페이지를 봅니다.

## 직접 분석해 보기

전용 공개 파서가 없어서 헥스 편집기로 직접 보는 방법이 기본입니다. 옛 형식의 암호화하지 않은 "tab" 파일이라면 앞에서부터 timestampMillis, WebContents 상태 길이와 바이트, parentId 순서로 값이 이어지고, 파일 끝 가까이에서 탭의 현재 URL 문자열을 찾을 수 있습니다 [1]. 저장 코드는 Java 의 DataOutputStream 으로 값을 쓰기 때문에 int 는 4바이트, long 은 8바이트를 큰 쪽 먼저(big-endian) 적고, 문자열(writeUTF)은 뒤따르는 바이트 수를 2바이트로 먼저 적은 뒤 수정 UTF-8 로 적습니다 [1][5]. 이 규칙대로 읽더라도 알려진 URL 이 열린 시험용 기기에서 만든 파일로 먼저 한 번 맞춰 보고 검체에 적용합니다. 이렇게 시험 기기로 도구와 방법을 확인하는 절차는 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md) 페이지를 봅니다.

FlatBuffer 형식 파일("flatbufferv1_" 로 시작)의 스키마는 이번에 확인하지 못했습니다. 파일 안에서 URL 문자열을 검색해 찾는 데까지만 하고, 칸의 뜻은 스키마를 확인한 뒤에 씁니다. 문자열 검색은 [콘텐츠 검색 (Content Search)](../../../03-techniques/analysis/content-search.md) 페이지를 봅니다.

## 교차 검증

탭 파일의 URL 은 [방문 기록 (History)](history.md)의 urls·visits 와 맞춰 보고, 탭에서 받은 파일은 [다운로드 (Downloads)](downloads.md)의 tab_url 과 대 봅니다. 앱 전환 시각은 [앱 사용 기록 (usagestats)](../../app-usage/usagestats/index.md), 탭 화면 그림은 [최근 앱 화면 (Recents·Snapshots)](../../app-usage/recents-snapshots.md)에서 따로 확인합니다.

## 실습

Chrome 이 깔린 공개 Android 검체로 아래 질문을 풀어 봅니다.

1. 탭 상태 폴더 아래 `0` 과 `custom_tabs` 에 파일이 각각 몇 개 있는지 세고, "tab", "cryptonito", "flatbufferv1_" 으로 나눠 표로 만듭니다.
2. "tab" 파일마다 URL 문자열을 찾아 방문 기록의 urls 표에 같은 URL 이 있는지 확인합니다.
3. 같은 탭 번호로 옛 형식과 FlatBuffer 형식 파일이 함께 있는 경우를 찾고, 두 파일의 URL 이 같은지 비교합니다.

## 참고 문헌

1. Chromium `TabStateFileManager.java` — https://raw.githubusercontent.com/chromium/chromium/main/chrome/browser/tabpersistence/android/java/src/org/chromium/chrome/browser/tabpersistence/TabStateFileManager.java
2. Chromium `TabStateDirectory.java` — https://raw.githubusercontent.com/chromium/chromium/main/chrome/browser/tabpersistence/android/java/src/org/chromium/chrome/browser/tabpersistence/TabStateDirectory.java
3. ALEAPP `scripts/artifacts/chrome.py`, `chromeCookies.py`, `chromeAutofill.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chrome.py , https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chromeCookies.py , https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chromeAutofill.py
4. GitHub 코드 검색 "SAVED_METADATA_FILE_PREFIX" (chromium/chromium), `TabMetadataFileManager.java` 결과 줄 — https://github.com/search?q=repo%3Achromium%2Fchromium+SAVED_METADATA_FILE_PREFIX&type=code
5. Java SE 8 API `java.io.DataOutputStream` — https://docs.oracle.com/javase/8/docs/api/java/io/DataOutputStream.html
