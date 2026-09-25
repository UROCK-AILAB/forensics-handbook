---
title: "Gemini Android 앱"
parent: "Gemini"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 300
---

# Android 앱 (Android)

Android 의 Gemini 는 따로 받은 Gemini 앱으로 열어도 실제로는 Google 앱이 실행하는 구조라서, 기기 쪽 흔적은 Gemini 앱보다 Google 앱과 어시스턴트 설정 쪽을 먼저 봐야 하고 대화 원본은 서버의 활동 기록에 있습니다.

> 확인 날짜: 2026-09-25. Google 도움말(개인정보 안내, Android 시작 안내)과 ALEAPP 공개 목록을 바탕으로 썼습니다. Play 스토어 페이지는 열었지만 본문을 읽지 못해서 패키지 이름·앱 버전·데이터 안전 항목은 확인하지 못했고, 이 핸드북은 Android 기기에서 Gemini 흔적을 관찰하지 않았습니다. 앱 데이터 폴더 안의 파일 이름과 DB 이름은 적지 않았습니다.

## 무엇이 남나 · 왜 생기나

개인정보 안내는 Gemini 앱을 받아도 Gemini 를 Google 앱이 실행한다(hosted by the Google app)고 적었고, 위치·마이크·카메라·알림 권한도 Google 앱 설정에서 관리한다고 안내합니다. 그래서 권한을 준 기록이나 권한 설정을 찾을 때는 Gemini 앱이 아니라 Google 앱을 기준으로 봅니다. Google 앱의 패키지 폴더 안에 Gemini 대화가 어느 파일로 남는지는 확인하지 못했습니다.

Google 앱을 기본 어시스턴트 앱으로 둔 휴대폰에서는 Gemini 를 모바일 어시스턴트로 고를 수 있고, 고르면 Google Assistant 대신 Gemini 가 답합니다. 휴대폰이 아닌 기기에서는 "Hey Google" 에 계속 Google Assistant 가 답한다고 도움말은 구분해 적었습니다. 여는 방법도 여럿인데 전원 버튼 길게 누르기, "Hey Google", 화면 아래 모서리에서 위로 쓸기, Gemini 앱을 직접 여는 길이 있어서, 앱 실행 기록이 없다고 Gemini 를 부르지 않았다고 볼 수 없습니다.

개인정보 안내가 적은 수집 항목 가운데 휴대폰과 관련된 것은 통화·메시지 기록, 연락처, 설치된 앱, 언어 같은 기기 정보이고, 위치는 기기·IP·계정의 집·직장 주소로 대략 위치를 잡는다고 적었습니다. 이 항목들은 서버 쪽에 모이는 데이터이고 기기에 어떤 모양으로 남는지는 문서에 없습니다. 보관 기간과 삭제 규칙은 [Gemini](index.md) 허브에 정리했습니다.

## 위치와 버전별 차이

| 항목 | 내용 | 확인 상태 |
|---|---|---|
| Gemini 앱 패키지 | Play 스토어 주소의 `id=com.google.android.apps.bard` | 주소만 확인, 본문은 읽지 못함 |
| 실행 주체 | Google 앱 (`com.google.android.googlequicksearchbox`) | 도움말로 확인. 이 패키지 안의 Gemini 저장 경로·DB 는 확인하지 못함 |
| 권한 | Google 앱 설정에서 관리 | 도움말로 확인 |
| 필요 조건 | Gemini 를 쓸 수 있는 개인 계정 또는 회사·학교 계정 로그인, 지원 언어·국가의 기기 | 도움말로 확인. Android 버전·메모리 조건은 확인하지 못함 |
| 나이 제한 | Family Link 로 13세 미만(나라마다 나이 기준 다름) 사용을 끌 수 있음 | 도움말로 확인 |

패키지 폴더를 찾는 일반 방법은 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)를 따르고, 설정 파일은 [설정 XML과 SharedPreferences](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/shared-preferences.html), DB 는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html) 페이지의 읽는 법을 씁니다. 앱 데이터 폴더는 기기 암호화의 영향을 받아서 수집 전에 [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html)를 먼저 확인합니다.

## 증거로서 의미

**증명하는 것.** 기기에 Gemini 앱이나 Google 앱이 설치돼 있었고 어시스턴트 설정이 Gemini 로 되어 있었다면, 그 기기에서 Gemini 를 부를 수 있는 상태였다고 쓸 수 있습니다. Google 앱 권한 설정에 마이크나 위치 권한이 켜져 있었다면 그 권한이 허용된 상태였다고 쓸 수 있습니다.

**증명하지 못하는 것.** 설치와 설정만으로는 실제로 대화했는지, 무엇을 물었는지 알 수 없고 대화 내용은 서버 활동 기록에서 확인해야 합니다. Google 앱은 Gemini 말고도 검색 등 여러 기능을 맡아서, Google 앱 실행 기록을 곧바로 Gemini 사용으로 읽지 않습니다.

## 시각 해석

기기 쪽에서 Gemini 대화 시각을 담은 파일은 확인하지 못했습니다. 설치 시각과 앱 실행 시각은 Android 의 일반 기록을 따르고 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-android/03-techniques/analysis/timeline/index.html)에서 다룹니다. 메시지 단위 시각은 서버 활동 기록에 있어서 [계정 데이터 내보내기](export.md)로 받아 맞춰 봅니다.

## 함정과 한계

Gemini 앱을 지운 뒤에도 Google 앱은 남아 있을 수 있고, Gemini 를 부르는 길은 앱 아이콘 말고도 전원 버튼·"Hey Google"·화면 모서리 쓸기가 있습니다. 앱 목록에 Gemini 앱이 없다는 사실만으로 사용하지 않았다고 쓰지 않습니다. 앱을 관리하거나 지우는 방법을 다룬 도움말 "Manage or delete the Gemini app on your Android device" 가 따로 있지만 이번 조사에서 본문을 열지 않았습니다.

공개 도구 ALEAPP 의 분석기 목록에서 Gemini·Bard·Google 앱 전용 분석기를 찾지 못했지만, 목록 화면이 잘려 보여 지원하지 않는다고 단정할 수 없습니다. 공개 도구 지원 여부는 확인하지 못한 상태로 두고, 쓰기 전에 도구의 최신 목록을 직접 확인합니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 계정 데이터 내보내기 | 대화 내용과 메시지 시각 | [계정 데이터 내보내기](export.md) |
| 크롬 방문 기록 | 앱 대신 웹 판을 쓴 흔적 | [웹 브라우저](web.md) |
| 음성 대화 기능 | "Hey Google"·Gemini Live 같은 음성 사용 | [음성 대화 기능](../../generative-media/voice-mode.md) |
| 서비스 회사 자료 | 서버에 남은 대화 원본 | [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md) |

## 실습

Gemini 흔적을 담은 공개 Android 검체는 이번 조사에서 확인하지 못했습니다. 시험용 기기와 계정으로 아래 질문을 풀어 봅니다.

1. Gemini 앱을 설치하고 한 번 대화한 뒤 Gemini 앱 패키지 폴더와 Google 앱 패키지 폴더 중 어느 쪽 파일의 수정 시각이 바뀝니까?
2. 어시스턴트를 Gemini 로 바꾸기 전과 후에 달라지는 설정 파일이 있습니까?
3. Gemini 앱을 지운 뒤에도 Google 앱 쪽에 남는 흔적이 있습니까?

## 참고 문헌

1. Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961 (2026-09-25 열람)
2. Get started with the Gemini mobile app (Android) — https://support.google.com/gemini/answer/14554984?co=GENIE.Platform%3DAndroid&oco=0 (2026-09-25 열람)
3. ALEAPP scripts/artifacts 목록 (GitHub) — https://github.com/abrignoni/ALEAPP/tree/main/scripts/artifacts (2026-09-25 열람)
4. Google Gemini — Google Play (본문 읽기 실패) — https://play.google.com/store/apps/details?id=com.google.android.apps.bard&hl=en_US
