---
title: "DeepL"
parent: "아티팩트 · 번역 AI"
nav_order: 480
---

# DeepL

DeepL 은 DeepL SE 가 만든 번역·글 교정 서비스입니다. 무료와 Pro 는 서버 보관 방식이 다르고, 앱은 기술 정보를 서버로 보내며, 일부 데이터는 기기 안에만 남습니다[3]. 로컬 파일의 경로와 형식은 실제 기기에서 찾아야 합니다.

## 무엇을 기록하나 · 왜 생기나

DeepL 은 웹, Windows 앱, 모바일 앱으로 글과 문서를 번역하고, Windows 앱에는 문법·맞춤법 교정과 어조·문체 조정(DeepL Write 기능)도 들어 있습니다. 번역하려면 원문을 서버로 보내야 해서, 원문과 번역본이 서버에 얼마나 남는지가 먼저 문제가 됩니다. 이 부분은 요금제에 따라 다릅니다[3].

| 구분 | 내용 |
|---|---|
| 무료 서비스의 입력 글 | 신경망 학습·개선을 위해 "제한된 기간" 처리함. 구체적인 삭제 기간은 공개되지 않음 |
| Pro 서비스의 입력 글 | 번역·교정이 끝나면 글·문서와 번역본을 삭제하고, 번역 내용을 계속 보관하지 않음 |
| 처리 장소 | Pro 의 글, 무료 서비스의 문서 번역은 EEA 안의 DeepL 설비에서 처리 |
| 앱이 보내는 기술 정보 | 접속 날짜·시각, 앱 버전, 운영체제, 전송량, 전송 성공 알림, 줄인(익명화한) IP 주소, 전체 IP 주소, 오류가 나면 진단 정보 |
| 앱 전체 IP 주소 보관 | 무료는 최대 14일, Pro 는 계약 기간 동안 |
| 모바일 앱 사용량 | 기기 사이에 공유하지 않는 고유 사용자 ID 로 원문·목표 언어 설정, 번역·교정한 글자 수, 복사 버튼 사용 여부를 기록 |

정리하면 Pro 에서는 번역 원문이 서버에 계속 남지 않고, 무료에서는 제한된 기간 남습니다[3]. 모바일 앱에서는 요금제와 상관없이 언어 설정과 글자 수 같은 사용량 기록이 서버에 남고, 이 사용량 항목에 번역한 글은 들어 있지 않습니다. 서버 기록과 기기 기록을 나눠 보는 방법은 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md), 보관 기간이 조사에 주는 영향은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에서 다룹니다.

기기 쪽에 남는 데이터는 두 가지입니다[3]. 모바일 앱의 "저장한 번역(saved translations)" 기능은 글과 번역을 기기 안에 저장합니다. 용어집(glossary)은 로그인하지 않고 만들면 기기에만 저장하고 DeepL 로 보내지 않으며, 로그인한 상태로 만들면 DeepL 로 보내질 수 있고 계정에서 볼 수 있습니다. 로그인한 웹 사용자에게 번역 기록 기능이 있는지, 있다면 서버와 브라우저 중 어디에 두는지는 계정 화면과 브라우저 저장소를 함께 보고 확인합니다.

## 위치와 버전별 차이

| 판 | 알려진 내용 | 로컬 저장 위치 |
|---|---|---|
| Windows | 무료 설치 파일(exe)을 내려받아 설치. Pro Advanced·Ultimate·Team·Business·Enterprise·Write 구독자는 MSI 설치 파일로 조직 전체에 배포할 수 있음 | 공개 문서에 없음. 실제 기기에서 확인 |
| macOS | DeepL for Windows 안내 페이지에 Mac 용 앱(DeepL for Mac) 내려받기 링크가 있음 | 공개 문서에 없음. 실제 기기에서 확인 |
| Android | 앱 이름 "DeepL Translate", 개발사 DeepL SE, 패키지 이름 `com.deepl.mobiletranslator` | 공개 문서에 없음. 실제 기기에서 확인 |
| iOS | 처리방침의 모바일 앱 설명(저장한 번역·음성 입력)은 적용 기기를 따로 나누지 않음 | 공개 문서에 없음. 실제 기기에서 확인 |
| 웹(deepl.com) | 처리방침 10.1 절에 쿠키·localStorage 항목을 필수·성능·기능·마케팅으로 나눈 표가 있음 | 브라우저 저장소. 개별 키 이름은 공개 문서에 없음 |

Windows 앱에서는 다른 프로그램에서 글을 고르고 Ctrl+C 를 두 번 누르면 바로 번역하고, Ctrl+Shift+C 를 두 번 누르면 자기가 쓴 글을 번역하면서 언어를 고를 수 있습니다. 이 방식이면 원문이 이메일 창이나 문서 편집기 같은 다른 프로그램에서 왔을 수 있어서, 번역한 글의 출처는 DeepL 기록만 보지 말고 그 시간대에 열려 있던 문서와 함께 봅니다.

MSI 로 조직에 배포한 경우에는 앱 설치가 사용자 한 사람의 선택이 아니라 관리자의 배포일 수 있습니다. 회사가 허용하지 않은 번역기를 썼는지 묻는 사건이라면 설치 방식부터 구분하고, 판단 순서는 [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md)를 따릅니다.

Android 에서는 패키지 이름으로 앱 데이터 폴더를 찾고, 폴더의 일반 구조는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html)에서 다룹니다. 저장한 번역과 로그인하지 않고 만든 용어집은 기기 안에 남지만[3], 이 폴더나 iOS 앱 컨테이너의 어느 파일에 들어가는지는 아래 구조 절의 순서로 실제 기기에서 찾습니다.

## 구조

Windows·macOS·Android·iOS 어느 판이든 로컬 파일 형식, DB 표 이름, 열 이름은 공개 문서에 없습니다. Windows 앱을 어떤 틀로 만들었는지도 공개 문서에 없어서, [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)에 맞는 폴더가 나오는지는 기기에서 직접 봐야 합니다. 폴더를 찾으면 아래 순서로 정리합니다.

1. 앱 데이터 폴더의 파일 목록과 크기, 시각을 먼저 기록합니다.
2. 파일 앞머리의 서명으로 형식을 판별하고, SQLite·LevelDB·설정 XML·plist 같은 형식별 페이지로 넘어갑니다.
3. 테스트 기기에서 번역 하나를 "저장한 번역" 에 넣고 용어집 항목 하나를 만든 뒤, 어느 파일이 바뀌는지 비교해 원문·번역·용어집이 들어 있는 곳을 확인합니다.

웹 판의 흔적은 브라우저 쪽에서 봅니다. 저장소 형식은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html), 브라우저별 위치는 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html) 페이지를 따릅니다.

## 증거로서 의미

**증명하는 것.** Windows 의 설치 기록이나 Android 의 `com.deepl.mobiletranslator` 패키지는 기기에 DeepL 앱이 있었다는 사실을 보여 줍니다. 모바일 기기에서 저장한 번역이나 로그인하지 않고 만든 용어집이 나온다면, 그 기기에서 만든 기록으로 볼 수 있습니다[3]. 서버 쪽에서는 앱의 전체 IP 주소(무료는 최대 14일)를 보관하고, 모바일 앱의 언어 설정과 글자 수를 고유 사용자 ID 로 기록합니다[3]. 서비스 회사 자료를 받는다면 "이 사용자 ID 가 이 기간에 이 언어 쌍으로 이만큼 번역했다" 는 수준의 사실까지는 말할 수 있지만, 이 ID 는 기기 사이에 공유하지 않아서 한 사람이 쓴 여러 기기를 이 ID 하나로 묶을 수는 없습니다.

**증명하지 못하는 것.** 서버의 사용량 기록에는 글자 수만 남고 번역한 글의 내용은 남지 않습니다. Pro 에서는 번역 원문을 계속 보관하지 않기 때문에, 서버에서 원문을 받을 수 있다고 기대하기 어렵습니다. 무료 서비스의 "제한된 기간" 은 기간이 정해져 있지 않아서, 특정 날짜의 글이 아직 남아 있는지 처리방침만으로는 알 수 없습니다. 로그인한 상태의 용어집은 서버로 보내질 수 있으므로, 기기에 용어집이 없다고 해서 만든 적이 없다고 단정하지 않습니다.

## 시각 해석

서버는 앱 접속 날짜·시각을 기록하지만[3], 그 기준이 UTC 인지 현지 시각인지는 공개되지 않았습니다. 서비스 회사 자료를 받으면 자료에 적힌 시간대 표기를 먼저 확인합니다. 기기 쪽에서 앱이 저장한 번역에 시각을 남기는지는 공개 문서에 없어서, 실제 기기에서 확인하기 전까지는 파일 시스템 시각만 쓰고 그 시각을 번역 한 건의 시각으로 옮겨 쓰지 않습니다. 여러 기록을 한 줄로 엮는 법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- 무료와 Pro 는 서버 보관 방식이 다릅니다. 계정의 요금제를 확인하지 않고 "서버에 원문이 남는다" 거나 "남지 않는다" 고 쓰지 않습니다.
- 앱 IP 주소는 무료에서 최대 14일만 보관하므로, 서버 자료 요청이 늦어지면 IP 주소는 받지 못할 수 있습니다. 요청 절차는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)을 참고합니다.
- Google Play 데이터 보안[1]에는 이메일 주소(선택, 앱 기능·사기 방지·보안·계정 관리 목적) 수집과 음성 또는 소리 녹음의 공유(앱 기능 목적)가 신고되어 있습니다. 개발사가 스스로 신고한 내용이고 실제 동작을 검증한 결과가 아닙니다.
- 모바일 음성 입력은 기기에 설치된 음성 서비스를 쓰고, 음성이 Apple·Google·Samsung 같은 기기 제공사로 넘어갈 수 있습니다[3]. 음성 입력의 흔적은 DeepL 앱이 아니라 기기의 음성 서비스 쪽에 남을 수 있습니다. 음성 기능 일반은 [음성 대화 기능](../generative-media/voice-mode.md)에서 다룹니다.
- 처리방침은 고쳐질 수 있어서, 사건 당시에 같은 내용이 적용되었는지는 그 시기의 처리방침 판으로 따로 확인해야 합니다.

## 직접 분석해 보기

**헥스로 한 번.** 앱 데이터 폴더에서 이름만으로 형식을 알 수 없는 파일이 나오면 앞 16바이트를 봅니다. 아래는 SQLite 명세로 만든 예시이고, DeepL 파일에서 나온 값이 아닙니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

이 서명이 보이면 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html) 페이지를 따라 헤더를 읽습니다. 서명이 없는 파일은 LevelDB 로그나 설정 파일일 수 있어서 형식별 페이지와 차례로 대조합니다.

**공개 도구로 한 번.** 형식을 판별한 뒤에는 DB Browser for SQLite 같은 공개 SQLite 뷰어로 표와 열을 살펴보고, 모바일 이미지 전체는 ALEAPP·iLEAPP 같은 공개 분석 도구로 설치 앱 목록을 뽑을 수 있습니다. DeepL 전용 분석기가 있는지는 쓰는 도구 판의 분석기 목록에서 확인합니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 브라우저 기록 | deepl.com 방문, 웹 판 사용 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html) |
| 네트워크 기록 | 번역 서버와 통신한 시간대 | [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) |
| 보안 제품 기록 | 번역 서비스로 보낸 내용이나 차단 이벤트 | [보안 제품이 남기는 AI 사용 기록](../network-enterprise/dlp-casb.md) |
| 서비스 회사 자료 | 모바일 앱 사용자 ID 별 언어 설정·글자 수, 앱 IP 주소 | [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) |
| 다른 번역 앱 | 같은 문서를 다른 번역기로 넘겼는지 | [파파고](papago.md) |

기밀 문서를 번역기에 넣었는지 묻는 사건이라면 [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) 시나리오의 순서를 따르고, 기기에서 흔적을 모으는 범위는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)를 참고합니다.

## 실습

아래 질문은 직접 만든 테스트 기기로 풀어 봅니다.

1. Windows 테스트 기기에 DeepL 을 깔고, 메모장에 적은 가짜 문장 "sample-project-alpha 납품 일정" 을 Ctrl+C 두 번으로 번역한 뒤 앱 데이터 폴더에서 바뀐 파일을 찾아봅니다.
2. 모바일 테스트 기기에서 로그인하지 않고 용어집 항목 하나를 만들고, 그 항목이 앱 데이터 폴더의 어느 파일에 들어가는지 찾아봅니다.
3. 같은 기기에서 번역 하나를 "저장한 번역" 에 넣었다가 지운 뒤, 지운 항목이 파일 안이나 SQLite 빈 공간에 남는지 확인합니다.

## 참고 문헌

1. Google Play — DeepL Translate 데이터 보안. https://play.google.com/store/apps/datasafety?id=com.deepl.mobiletranslator&hl=en
2. DeepL — DeepL for Windows 안내 페이지. https://www.deepl.com/en/windows-app
3. DeepL — Privacy Policy. https://www.deepl.com/en/privacy
