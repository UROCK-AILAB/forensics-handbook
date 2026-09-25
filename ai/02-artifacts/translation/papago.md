---
title: "파파고"
parent: "아티팩트 · 번역 AI"
nav_order: 440
---

# 파파고 (Papago)

파파고는 네이버가 만든 번역 서비스이고, 앱 스토어에 공개된 정보로는 수집 항목과 앱 식별자까지만 확인되며 번역 기록이 기기와 서버 중 어디에 얼마나 남는지는 공식 문서로 확인하지 못했습니다.

> 확인 날짜: 2026-09. 이 페이지는 Google Play 데이터 보안 항목과 App Store 페이지(2026-09-25 열람)만 근거로 썼습니다. 파파고 앱이 설치된 기기는 직접 관찰하지 않았고, 이 핸드북의 기기 관찰 대상에도 파파고는 들어 있지 않습니다. 네이버 개인정보 처리방침은 열리지 않아 참고하지 못했습니다.

## 무엇을 기록하나 · 왜 생기나

파파고는 텍스트·이미지·음성·오프라인·웹사이트·대화·문서 번역을 제공하고, 번역하려면 원문을 입력하거나 사진·음성·문서를 넘겨야 해서 입력한 내용이 앱과 서버를 거쳐 갑니다. 스토어에 공개된 항목을 보면 앱이 다루는 데이터의 종류는 짐작할 수 있지만, 번역 원문과 결과를 어디에 얼마 동안 보관하는지, 번역 기록이나 단어장이 네이버 계정에 동기화되는지는 확인하지 못했습니다. 그래서 조사할 때는 기기에서 앱 데이터 폴더와 브라우저 기록을 찾고, 서버 쪽 기록은 따로 요청해야 하는 대상으로 나눠 둡니다. 서버·기기·동기화를 나눠 보는 방법은 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

스토어의 개인정보 항목은 개발사가 스스로 신고한 내용이고, 실제 앱 동작을 검증한 결과가 아닙니다. 아래 표는 "개발사가 이렇게 밝혔다" 는 뜻으로 읽습니다.

| 출처 | 항목 | 개발사가 밝힌 내용 |
|---|---|---|
| Google Play 데이터 보안 | 수집 | 이름, 이메일 주소, 사용자 ID, 전화번호, 기타 개인정보, 사진, 앱 상호작용, 음성 또는 소리 녹음 파일, 기기 또는 기타 ID, 비정상 종료 로그, 파일 및 문서 |
| Google Play 데이터 보안 | 공유(분석 목적) | 앱 상호작용, 기기 또는 기타 ID, 비정상 종료 로그 |
| Google Play 데이터 보안 | 보안 | 전송 중 암호화, 데이터 삭제 요청 방법 제공 |
| App Store 개인정보 라벨 | 사용자를 추적하는 데 사용되는 데이터 | 식별자 |
| App Store 개인정보 라벨 | 사용자에게 연결된 데이터 | 연락처 정보, 사용자 콘텐츠, 식별자, 사용 데이터, 기타 데이터 |
| App Store 개인정보 라벨 | 사용자에게 연결되지 않은 데이터 | 위치, 사용자 콘텐츠, 진단 |

Google Play 수집 항목에 사진, 음성 녹음, 파일 및 문서가 들어 있고 App Store 라벨에도 사용자 콘텐츠가 있어서, 이미지·음성·문서 번역에 쓴 자료가 서버로 넘어갈 수 있다는 점은 개발사 신고로 알 수 있습니다. 넘어간 자료를 얼마나 보관하는지는 신고 항목에 없습니다. 프롬프트·첨부·결과를 나눠 보는 기준은 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)를 참고합니다.

## 위치와 버전별 차이

| 판 | 확인한 식별 정보 | 로컬 저장 위치 |
|---|---|---|
| Android | 앱 이름 "네이버 파파고 - AI 통번역", 개발자 NAVER Corp., 패키지 이름 `com.naver.labs.translator` | 확인하지 못함 |
| iOS·iPadOS | 같은 앱 이름, iOS 17.0 이상 필요. 스토어 페이지 버전 기록 맨 위에 1.12.3(9월 17일, 연도 표시 없음)이 보였고, 2026-09 현재 최신 버전인지는 확인하지 못함 | 확인하지 못함 |
| macOS | 별도 Mac 앱은 확인하지 못함. App Store 페이지에 macOS 13.0 이상, Apple M1 칩 이상 Mac 에서 iOS 앱을 실행할 수 있다고 표시됨 | 확인하지 못함 |
| Windows | 전용 데스크톱 앱이 있는지 확인하지 못함 | 해당 없음(확인하지 못함) |
| 웹 | 브라우저로 쓰는 판 | 브라우저 기록·저장소 |

Android 에서는 패키지 이름이 앱 데이터 폴더를 찾는 열쇠이고, 앱 데이터 폴더의 일반 구조는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)에서 다룹니다. 파파고 폴더 안에 어떤 파일과 DB 가 있는지는 확인하지 못해서 이 페이지에 적지 않습니다. iOS 에서는 앱 컨테이너 안의 파일이 [데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html) 등급에 따라 잠기고, 컨테이너 안의 구체적인 파일은 역시 확인하지 못했습니다.

웹 판을 썼다면 방문 기록과 저장소는 브라우저 쪽에 남습니다. 읽는 법은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html), [사파리(macOS)](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/browsers/safari/index.html), [크롬(Android)](https://urock-ailab.github.io/forensics-handbook-android/02-artifacts/browsers/chrome/index.html), [사파리(iOS)](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/safari/index.html) 페이지를 따릅니다. 파파고 웹 페이지가 브라우저 저장소에 어떤 키를 쓰는지는 확인하지 못했습니다.

## 구조

파파고 앱의 로컬 파일 형식, DB 표 이름, 칸 이름은 공식 문서로도, 기기 관찰로도 확인하지 못했습니다. 모바일 앱은 흔히 SQLite 나 설정 XML·plist 에 데이터를 두지만, 파파고가 그렇게 하는지는 기기를 직접 열어 봐야 알 수 있습니다. 기기를 열어 보면 아래 순서로 정리합니다.

1. 앱 데이터 폴더 안의 파일 목록과 크기, 시각을 먼저 기록합니다.
2. 파일 앞머리의 서명으로 형식을 가립니다. SQLite 는 [SQLite 데이터베이스(Android)](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html), 설정 XML 은 [설정 XML과 SharedPreferences](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/shared-preferences.html), iOS plist 는 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/plist.html) 페이지로 넘어갑니다.
3. 번역 원문·결과로 보이는 칸, 즐겨찾기·단어장으로 보이는 칸, 계정 식별자로 보이는 칸을 나눠 적고, 테스트 기기에서 번역을 한 번 해 본 뒤 어느 칸이 바뀌는지 비교해 뜻을 확인합니다.

## 증거로서 의미

**증명하는 것.** Android 에서 `com.naver.labs.translator` 패키지가 설치되어 있었다는 기록이나 iOS 앱 목록의 파파고 항목은 기기에 이 앱이 있었다는 사실을 보여 줍니다. 앱 데이터 폴더에서 번역 원문과 결과가 나온다면, 그 기기에서 그 내용을 파파고로 번역한 기록이 있다고 쓸 수 있습니다. 개발사 신고에 따르면 식별자·연락처 정보·사용자 콘텐츠·사용 데이터를 사용자와 연결해 다루므로, 서버 쪽 기록을 받을 수 있다면 계정과 사용을 잇는 자료가 됩니다.

**증명하지 못하는 것.** 스토어 라벨은 수집하는 데이터의 종류만 말하고, 특정 번역을 서버에 얼마 동안 두었는지는 말하지 않습니다. 기기에 번역 기록이 없다고 해서 번역하지 않았다고 단정할 수 없는데, 앱이 기록을 남기는지부터 확인하지 못했기 때문입니다. 앱이 설치되어 있었다는 사실만으로 특정 문서를 번역했다고 쓸 수도 없습니다. 기기를 여러 사람이 썼다면 누가 입력했는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 좁힙니다.

## 시각 해석

파파고 앱이 번역 기록에 시각을 남기는지, 남긴다면 UTC 인지 현지 시각인지는 확인하지 못했습니다. 앱 데이터 폴더에서 시각 값을 찾으면 테스트 기기에서 번역한 시각과 비교해 기준을 정하고, 그 전에는 파일 시스템 시각(파일을 만들거나 고친 시각)만 씁니다. 파일 시각은 파일 전체가 마지막으로 바뀐 때를 말할 뿐이라, 특정 번역 한 건의 시각으로 옮겨 쓰지 않습니다. 다른 기록과 한 줄로 엮는 법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- 스토어 페이지의 버전 번호(1.12.3)는 페이지를 가져온 시점의 표시이고, 조사 대상 기기의 버전은 기기의 설치 기록에서 따로 확인합니다.
- 오프라인 번역 기능이 있어서, 번역할 때마다 서버와 통신했다고 가정하면 안 됩니다. 네트워크 기록이 없다고 해서 번역하지 않았다고 단정하지 않습니다.
- 웹 판 사용은 앱 폴더에 남지 않고 브라우저 쪽에 남습니다. 앱 폴더만 보고 사용 여부를 판단하지 않습니다.
- 앱을 지우면 앱 데이터 폴더도 함께 지워지는 것이 보통이지만, 파파고의 계정 동기화 여부를 확인하지 못해서 서버 쪽에 기록이 남는지는 알 수 없습니다. 보관과 삭제의 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)를 참고합니다.

## 직접 분석해 보기

**헥스로 한 번.** 앱 데이터 폴더에서 이름만으로 형식을 알 수 없는 파일이 나오면 앞 16바이트를 봅니다. 아래는 SQLite 명세로 만든 예시이고, 파파고 파일에서 나온 값이 아닙니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

이 16바이트가 보이면 SQLite 파일이고, 이어지는 헤더 해석은 SQLite 페이지를 따릅니다. 파일 이름이나 확장자가 없어도 서명으로 형식을 가릴 수 있어서, 목록을 만들 때 서명을 함께 적어 둡니다.

**공개 도구로 한 번.** 형식을 가린 뒤에는 DB Browser for SQLite 같은 공개 SQLite 뷰어로 표와 칸을 훑고, 모바일 이미지 전체는 ALEAPP·iLEAPP 같은 공개 분석 도구로 설치 앱 목록과 사용 기록을 뽑을 수 있습니다. 이 도구들이 파파고 전용 해석기를 두고 있는지는 확인하지 못했고, 해석기가 없으면 원본 파일을 직접 여는 방법으로 돌아갑니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 브라우저 기록 | 웹 판 파파고 방문 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html) |
| 네트워크 기록 | 번역 서버와 통신한 시간대 | [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) |
| 보안 제품 기록 | 번역 서비스로 보낸 내용이나 차단 이벤트 | [보안 제품이 남기는 AI 사용 기록](../network-enterprise/dlp-casb.md) |
| 서비스 회사 자료 | 계정·기기와 연결된 서버 기록 | [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) |
| 다른 번역 앱 | 같은 문서를 다른 번역기로 넘겼는지 | [DeepL](deepl.md) |

기밀 문서를 번역기에 넣었는지 묻는 사건이라면 [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) 시나리오의 순서를 따릅니다.

## 실습

파파고가 들어 있는 공개 검체는 확인하지 못했습니다. 직접 만든 테스트 기기로 아래 질문을 풀어 봅니다.

1. 테스트 기기에 파파고를 깔고 가짜 문장 "sample-project-alpha 회의 일정" 을 번역한 뒤, 앱 데이터 폴더에서 어느 파일이 바뀌었는지 찾아봅니다.
2. 번역 기록을 앱 안에서 지운 뒤 같은 파일을 다시 열어, 지운 기록이 파일 안이나 SQLite 빈 공간에 남는지 확인합니다.
3. 비행기 모드에서 오프라인 번역을 해 보고, 네트워크 기록 없이 앱 폴더에만 흔적이 남는지 비교합니다.

## 참고 문헌

1. Google Play — 네이버 파파고 - AI 통번역 데이터 보안. https://play.google.com/store/apps/datasafety?id=com.naver.labs.translator&hl=ko
2. App Store(한국) — 네이버 파파고 - AI 통번역. https://apps.apple.com/kr/app/id1147874819
