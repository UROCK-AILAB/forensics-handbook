---
title: "Gemini Android 앱"
parent: "Gemini"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 300
---

# Android 앱 (Android)

Android 의 Gemini 는 따로 받은 Gemini 앱(패키지 `com.google.android.apps.bard`)으로 열어도 실제 실행은 Google 앱(`com.google.android.googlequicksearchbox`)이 맡고, 대화·이미지 원본은 서버에 있어서 기기에서는 대화 내용보다 "언제 어떤 길로 Gemini 를 불렀나" 를 보여 주는 흔적을 찾게 됩니다 [1][3][4].

앱 판에 따라 폴더 내용이 달라질 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

Gemini 앱을 받아도 Gemini 는 Google 앱이 실행하고(hosted by the Google app), 위치·마이크·카메라·알림 권한도 Google 앱 설정에서 관리합니다 [1]. 공개 코드에서도 같은 구조가 보입니다. 기본 어시스턴트를 바꿔 주는 앱 SwitchAI 는 Gemini 를 열 때 Gemini 앱의 `com.google.android.apps.bard.shellapp.BardEntryPointActivity` 를 부르고, 루트 권한 설정을 켜면 Google 앱 패키지 안의 액티비티를 곧바로 부릅니다 [4]. Gemini 앱 쪽 액티비티 이름에 "shellapp" 이 들어간 점도 Google 앱이 Gemini 를 실행하는 구조와 들어맞습니다.

ChatGPT 와 Copilot 이 대화를 기기에 평문으로 두는 것과 달리, Gemini 는 대화·브라우저 데이터·이미지를 모두 클라우드에 두고 Google Takeout 으로 받을 수 있습니다 [3]. 세 앱 모두 쓰는 플랫폼에 따라 대화를 되살릴 수 있지만, Gemini 대화를 기기와 Takeout 가운데 어디서 되살렸는지는 공개 자료에 없습니다 [3]. 그래서 대화 내용은 [계정 데이터 내보내기](export.md)나 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)으로 확인하고, 기기에서는 설치·설정·실행 흔적을 봅니다. 서버 보관 기간과 삭제 규칙은 [Gemini](index.md) 허브에 정리했습니다.

Google 앱을 기본 어시스턴트 앱으로 둔 휴대폰에서는 Gemini 를 모바일 어시스턴트로 고를 수 있고, 고르면 Google Assistant 대신 Gemini 가 답합니다 [2]. 휴대폰이 아닌 기기에서는 "Hey Google" 에 계속 Google Assistant 가 답합니다 [2]. 여는 길도 여럿이라 전원 버튼 길게 누르기, "Hey Google", 화면 아래 모서리에서 위로 쓸기, Gemini 앱을 직접 여는 방법이 있습니다 [2].

Gemini 가 모으는 항목 가운데 휴대폰과 관련된 것은 통화·메시지 기록, 연락처, 설치된 앱, 언어 같은 기기 정보입니다 [1]. 위치는 기기·IP·계정의 집·직장 주소로 대략 잡습니다 [1]. 이 항목들은 서버 쪽에 모이는 데이터라서 기기에 어떤 모양으로 남는지는 검체로 확인해야 합니다.

## 위치와 버전별 차이

| 항목 | 내용 | 근거 |
|---|---|---|
| Gemini 앱 패키지 | `com.google.android.apps.bard` | [4][5] |
| Gemini 앱 진입 액티비티 | `com.google.android.apps.bard.shellapp.BardEntryPointActivity` (보통 실행과 음성 입력 둘 다) | [4] |
| 실행 주체 | Google 앱 `com.google.android.googlequicksearchbox` | [1][4] |
| Google 앱 안에서 부르는 액티비티 | 보통 실행 `com.google.android.apps.search.assistant.surfaces.voice.robin.main.MainActivity`, 음성 입력 `com.google.android.apps.search.assistant.surfaces.voice.robin.ui.floaty.activity.FloatyActivity` | [4] |
| 권한 | Google 앱 설정에서 관리 | [1] |
| 필요 조건 | Gemini 를 쓸 수 있는 개인 계정 또는 회사·학교 계정 로그인, 지원 언어·국가의 기기 | [2] |
| 나이 제한 | Family Link 로 13세 미만(나라마다 나이 기준 다름) 사용을 끌 수 있음 | [2] |

SwitchAI 의 액티비티 이름은 2026-03-29 판 코드 기준입니다 [4]. Google 앱 판이 바뀌면 이름도 바뀔 수 있어서, 검체의 앱 판에서 다시 확인합니다.

Gemini 앱 폴더는 `/data/data/com.google.android.apps.bard/` 입니다. LEAF 저장소의 기록에는 Android 15 기기에서 2026-04-20 에 뽑은 이 폴더에 SQLite 데이터베이스가 하나도 없었고, 파일 13개가 모두 웹뷰(WebView) 캐시와 미리 컴파일한 OAT 파일이었다고 적혀 있습니다 [5]. 같은 저장소의 README 는 Gemini 를 "SQLite 안에 Protocol Buffer 로 인코딩" 한다고 적어 두 문서가 서로 어긋납니다 [5]. 이 저장소는 학생 과제 수준이라 두 기록 모두 검체로 다시 확인하고, 어느 쪽이든 대화 전문이 앱 폴더에 있다는 근거로 쓰지 않습니다.

Google 앱 폴더 `/data/data/com.google.android.googlequicksearchbox/` 안에서 Gemini 대화가 어느 파일에 남는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 폴더 구조의 일반 원리는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html)에서, 이 폴더가 기기 암호화의 보호를 받는 방식은 [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/encryption/index.html)에서 다룹니다. 웹뷰 캐시를 읽는 법은 [Electron·웹뷰 앱의 저장 구조](../../../01-foundations/storage-model/electron-webview.md)에 있습니다.

## 구조

Gemini 전용 파일 구조는 공개된 자료가 없습니다. 대신 Google 앱 쪽에는 ALEAPP 이 읽는 파일이 두 종류 있고, 검색 위젯과 어시스턴트의 검색 세션, 최근 검색어를 담습니다 [6][7]. 두 분석기 모두 Gemini 를 언급하지 않아서, 이 파일에 Gemini 대화가 들어가는지는 검체에서 따로 확인합니다.

| 경로(Google 앱 폴더 안) | 형식 | ALEAPP 이 꺼내는 것 | 근거 |
|---|---|---|---|
| `app_session/*.binarypb` | protobuf | 세션 종류, 검색어, 음성 응답(mp3) | [6] |
| `files/recently/*`, `files/accounts/*/RecentsDataStore.pb` | protobuf | 최근 검색어, 연 페이지 주소·제목, 화면 캡처 번호 | [7] |
| `databases/accounts.notifications.db` | SQLite | `accounts` 표의 `account_name` (계정 이름) | [7] |

`app_session/*.binarypb` 는 protobuf 하나이고, `googleQuickSearchbox.py` 는 필드 번호로 값을 꺼냅니다 [6]. 필드 `3` 은 세션 종류 문자열이고, 필드 `132269847` 안의 `1` 안의 `2` 가 대표 검색어입니다. 같은 필드 `132269847` 안의 `2` 에는 조각이 여럿 들어 있고, 분석기는 조각마다 UTF-16 문자열 `com.google.android.apps.gsa.shared.search.Query` 를 찾아 그 뒤의 검색어를 읽습니다. 필드 `132269388` 안의 `1` 에는 음성 응답이 mp3 로 들어 있습니다 [6].

`RecentsDataStore.pb` 는 필드 `1` 이 되풀이되는 목록이고, 항목마다 `1` 번호, `4` 시각 1, `5` 검색어, `7` 페이지(`1` 주소, `2` 도메인, `3` 제목), `8` 검색(`1` 분류, `2` 검색 엔진), `9` 화면 캡처 번호, `17` 시각 2 가 있습니다 [7]. 화면 캡처는 "계정 이름-캡처 번호.jpg" 라는 이름의 파일과 짝을 짓습니다 [7]. SQLite 를 읽는 법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/data-formats/sqlite/index.html) 페이지를 봅니다.

## 증거로서 의미

**증명하는 것.** 기기에 Gemini 앱이나 Google 앱이 설치돼 있었고 어시스턴트 설정이 Gemini 로 되어 있었다면, 그 기기에서 Gemini 를 부를 수 있는 상태였다고 쓸 수 있습니다. Google 앱 권한 설정에 마이크나 위치 권한이 켜져 있었다면 그 권한이 허용된 상태였다고 쓸 수 있습니다. Google 앱의 세션 파일에 검색어나 음성 응답이 있으면 "이 시각 무렵 Google 앱에 이런 입력이 있었다" 까지는 쓸 수 있습니다.

**증명하지 못하는 것.** 설치와 설정만으로는 실제로 대화했는지, 무엇을 물었는지 알 수 없고 대화 내용은 서버 기록에서 확인해야 합니다 [3]. Google 앱은 Gemini 말고도 검색 등 여러 기능을 맡아서, Google 앱 실행 기록이나 세션 파일을 곧바로 Gemini 사용으로 읽지 않습니다. Gemini 앱 폴더에 대화가 없다는 사실도 대화가 없었다는 뜻이 아니고, 원래 서버에 두는 구조라서 그렇습니다 [3][5].

## 시각 해석

Gemini 대화의 메시지 단위 시각은 서버 기록에 있어서 [계정 데이터 내보내기](export.md)로 받아 맞춰 봅니다 [3]. 설치 시각과 앱 실행 시각은 Android 의 일반 기록을 따르고 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/android/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에서 다룹니다.

Google 앱 쪽 파일의 시각은 파일마다 뜻이 다릅니다. `app_session/*.binarypb` 에는 ALEAPP 이 읽는 시각 필드가 없고, 분석기는 파일 수정 시각을 UTC 로 바꿔 "File Timestamp" 칸에 넣습니다 [6]. 그래서 이 값은 파일을 마지막으로 쓴 시각이고, 복사하면서 수정 시각이 바뀌면 틀어집니다. `RecentsDataStore.pb` 의 필드 `4` 는 1970년부터 센 밀리초로, ALEAPP 이 UTC 로 바꿔 "Timestamp" 칸에 넣습니다 [7]. 필드 `17` 은 이름만 "timestamp2" 로 붙어 있고 분석기가 뜻을 적지 않았습니다 [7].

## 함정과 한계

Gemini 앱을 지운 뒤에도 Google 앱은 남아 있을 수 있고, Gemini 를 부르는 길은 앱 아이콘 말고도 전원 버튼·"Hey Google"·화면 모서리 쓸기가 있습니다 [2]. 앱 목록에 Gemini 앱이 없다는 사실만으로 사용하지 않았다고 쓰지 않습니다.

공개 분석 도구 가운데 Gemini 전용 분석기는 없습니다. ALEAPP 의 main 브랜치(2026-09-24 커밋) 전체 목록에는 AI 대화 분석기로 `chatgpt.py`, `chatgpt2.py`, `claude.py`, DeepSeek 분석기 3개, `Grok.py`, AIChatbotNova 분석기 4개가 있지만 Gemini·Bard 분석기는 없습니다 [8]. Google 앱 분석기 두 개는 있지만 검색·어시스턴트 세션을 읽는 용도이고 Gemini 를 따로 다루지 않습니다 [6][7]. 도구 목록은 자주 바뀌므로 분석 전에 최신 목록을 다시 봅니다.

ALEAPP 의 Google 앱 분석기가 시험한 판도 오래됐습니다. `googleQuickSearchbox.py` 는 Android 13·14 의 Google 앱 버전 코드 301246250·301381725 에서 각각 2행·1행을 읽었다고 적었습니다 [6]. `googleQuickSearchboxRecent.py` 는 Android 10·13·14 이미지 7개에서 모두 0행이었다고 적었습니다 [7]. 지금 Google 앱 판에서는 파일 이름이나 필드 번호가 다를 수 있습니다.

LEAF 기록은 기기 하나, 날짜 하루의 관찰이고 README 와 서로 어긋납니다 [5]. 앱 폴더에 데이터베이스가 없다는 기록은 참고로만 쓰고, 검체의 폴더 목록을 직접 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** `app_session/*.binarypb` 를 헥스 편집기로 열면 protobuf 필드 머리가 보입니다. 필드 번호를 왼쪽으로 3비트 밀고 형식 번호(길이가 붙은 값은 2)를 더한 값을 varint 로 적은 것이 필드 머리라서, 필드 `3` 은 `1A`, 필드 `132269847` 은 `BA F1 C8 F8 03`, 필드 `132269388` 은 `E2 D4 C8 F8 03` 으로 시작합니다. 아래는 필드 머리 계산으로 만든 예시이고 실제 검체 값이 아닙니다.

```text
1A 05 76 6F 69 63 65                          필드 3, 길이 5, "voice" (만든 예시)
BA F1 C8 F8 03 09 0A 07 12 05 68 65 6C 6C 6F  필드 132269847 > 1 > 2, "hello" (만든 예시)
```

`BA F1 C8 F8 03` 을 찾으면 대표 검색어 자리로 곧바로 갈 수 있고, `E2 D4 C8 F8 03` 과 길이 값, 안쪽 필드 `1` 의 머리 `0A` 와 길이 값 뒤에 mp3 머리(`ID3` 또는 `FF FB` 같은 프레임 동기 바이트)가 이어지면 음성 응답이 들어 있다는 뜻입니다.

**공개 도구로 한 번.** ALEAPP 에 추출 이미지를 넣으면 "Google Now & QuickSearch" 분류 아래 "Google Quick Search Queries" 와 "Google Quick Search Recent" 두 보고서가 나옵니다 [6][7]. Gemini 앱 폴더와 Google 앱 폴더는 전용 분석기가 없어서, 폴더 목록과 파일 수정 시각을 직접 뽑아 봅니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 계정 데이터 내보내기 | 대화 내용과 메시지 시각 | [계정 데이터 내보내기](export.md) |
| 서비스 회사 자료 | 서버에 남은 대화 원본 | [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md) |
| 크롬 방문 기록 | 앱 대신 웹 판을 쓴 흔적 | [웹 브라우저](web.md), [크롬](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/browsers/chrome/index.html) |
| 음성 대화 기능 | "Hey Google"·Gemini Live 같은 음성 사용 | [음성 대화 기능](../../generative-media/voice-mode.md) |
| 웹뷰 캐시 | 앱 폴더에 남은 캐시 조각 | [대화 내용 되살리기](../../../03-techniques/analysis/content-recovery.md) |

## 실습

Gemini 흔적을 담은 공개 Android 검체는 알려진 것이 없어서, 시험용 기기와 계정으로 아래 질문을 풀어 봅니다.

1. Gemini 앱을 설치하고 한 번 대화한 뒤 Gemini 앱 폴더와 Google 앱 폴더 가운데 어느 쪽 파일의 수정 시각이 바뀝니까?
2. 어시스턴트를 Gemini 로 바꾸기 전과 후에 달라지는 설정 파일이 있습니까?
3. 전원 버튼으로 Gemini 를 부른 뒤 Google 앱의 `app_session` 폴더에 새 `.binarypb` 파일이 생깁니까? 생긴다면 필드 `3` 의 세션 종류 값은 무엇입니까?
4. Gemini 앱을 지운 뒤에도 Google 앱 쪽에 남는 흔적이 있습니까?

## 참고 문헌

1. Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961 (2026-09-25 열람)
2. Get started with the Gemini mobile app (Android) — https://support.google.com/gemini/answer/14554984?co=GENIE.Platform%3DAndroid&oco=0 (2026-09-25 열람)
3. Sonali Tyagi, Yufeng Gong, Umit Karabiyik, "Forensic analysis and privacy implications of LLM mobile apps: A case study of ChatGPT, Copilot, and Gemini", Forensic Science International: Digital Investigation, 54 (2025), 301974. https://doi.org/10.1016/j.fsidi.2025.301974 (초록)
4. WSTxda/SwitchAI — https://github.com/WSTxda/SwitchAI , `app/src/main/java/com/wstxda/switchai/assistant/GeminiAssistant.kt` (2026-03-29 갱신, 2026-09-25 열람)
5. MarcosAOSperoni/LEAF-Digital-Forensics — https://github.com/MarcosAOSperoni/LEAF-Digital-Forensics , `docs/parser-schemas.md`, `leaf/README.md` (2026-09-25 열람)
6. abrignoni/ALEAPP — https://github.com/abrignoni/ALEAPP , `scripts/artifacts/googleQuickSearchbox.py` (2026-09-25 열람)
7. abrignoni/ALEAPP — https://github.com/abrignoni/ALEAPP , `scripts/artifacts/googleQuickSearchboxRecent.py` (분석기 표기 갱신일 2026-08-01, 2026-09-25 열람)
8. abrignoni/ALEAPP — https://github.com/abrignoni/ALEAPP , `scripts/artifacts/` 전체 목록 (main 브랜치, 2026-09-25 열람)
