---
title: "Gemini iOS 앱"
parent: "Gemini"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 310
---

# iOS 앱 (iOS)

iOS 에는 App Store 에 "Google Gemini" 라는 별도 앱이 있고 대화 원본은 계정의 서버 활동 기록에 있어서, 기기에서는 앱 설치 사실과 앱 컨테이너 안의 흔적을 찾게 되지만 그 안의 파일 구조는 공개 자료로 확인되지 않았습니다.

> 확인 날짜: 2026-09-25. Google 도움말(개인정보 안내), App Store 페이지, iLEAPP 공개 목록을 바탕으로 썼습니다. 이 핸드북은 iOS 기기에서 Gemini 흔적을 관찰하지 않았습니다. 번들 ID, 앱 컨테이너 안의 저장 경로와 DB 이름은 확인하지 못해서 적지 않았습니다.

## 무엇이 남나 · 왜 생기나

Android 에서는 Google 앱이 Gemini 를 실행하지만([Android 앱](android.md)), iOS 에는 Gemini 를 쓰는 별도 앱이 있습니다. 대화는 활동 저장 (Keep Activity) 설정에 따라 계정 쪽 Gemini 앱 활동에 저장되고, 보관 기간과 삭제 규칙은 [Gemini](index.md) 허브에 정리했습니다. 앱이 기기에 대화 사본이나 캐시를 남기는지는 공식 문서에 없습니다.

App Store 의 개인정보 라벨은 앱이 무엇을 모아 사용자와 연결하는지 판매자가 스스로 밝힌 목록이고, 기기 안에 무엇이 남는지와는 다른 이야기입니다. 그래도 어떤 종류의 데이터를 찾아볼지 정하는 데는 쓸 수 있습니다. 확인 시점 라벨이 "나와 연결된 데이터" 로 적은 항목은 구매, 정확한·대략 위치, 연락처 정보, 사용자 콘텐츠(사진·영상·음성·이메일), 검색·방문 기록, 식별자, 사용 데이터, 민감 정보, 진단이고, 용도는 개발자의 광고·마케팅, 분석, 개인화, 앱 기능, 기타입니다.

## 위치와 버전별 차이

| 항목 | 내용 | 확인 상태 |
|---|---|---|
| App Store 이름 | Google Gemini (판매자 Google LLC) | App Store 페이지로 확인 |
| App Store ID | 6477489729 | App Store 페이지로 확인 |
| 확인 시점 버전 | 1.2026.3770306 (2026-09-25 기준 하루 전 출시) | App Store 페이지로 확인 |
| 요구 사항 | iOS 17.4 이상, iPadOS 17.4 이상 | App Store 페이지로 확인 |
| 크기 | 364.3 MB | App Store 페이지로 확인 |
| 번들 ID, 컨테이너 안 경로·DB | — | 확인하지 못함 |
| 위젯·Siri·Live Activities 연동 | — | 확인하지 못함 |

앱은 자주 새 버전이 나와서 위 버전은 확인한 날의 값일 뿐이고, 분석할 기기의 설치 버전은 따로 확인합니다. App Store ID 는 앱 스토어 안의 번호이고 기기의 앱 컨테이너를 찾는 번들 ID 와 다릅니다.

앱 컨테이너 안의 파일은 기기 잠금 상태에 따라 보호 등급이 달라서 [데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html)를 먼저 확인하고, 로그인 정보가 들어가는 곳은 [키체인](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/keychain.html) 페이지에서 다룹니다. 컨테이너에서 설정 파일이나 DB 를 찾았다면 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/plist.html)과 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/sqlite/index.html)의 읽는 법을 씁니다. 로컬 백업으로 수집할 때는 [로컬 백업](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/backups/local-backup/index.html)을 보는데, Gemini 앱 데이터가 백업에 들어가는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것.** 기기에 Google Gemini 앱이 설치돼 있었다면 그 기기에서 Gemini 를 쓸 수 있는 상태였다고 쓸 수 있습니다. 위치·마이크·사진 같은 권한 허용 기록이 있으면 그 권한을 허용한 상태였다고 쓸 수 있습니다.

**증명하지 못하는 것.** 설치 사실만으로는 대화했는지, 무엇을 물었는지 알 수 없고 대화 내용은 서버 활동 기록에서 확인해야 합니다. 개인정보 라벨에 적힌 항목이 기기에 남아 있다고 볼 수도 없는데, 라벨은 서버로 모으는 데이터의 종류를 밝힌 것이기 때문입니다.

## 시각 해석

기기 쪽에서 Gemini 대화 시각을 담은 파일은 확인하지 못했습니다. 설치·실행 시각은 iOS 의 일반 기록을 따르고 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-ios/03-techniques/analysis/timeline/index.html)에서 다룹니다. 메시지 단위 시각은 서버 활동 기록에 있어서 [계정 데이터 내보내기](export.md)로 받아 맞춰 봅니다.

## 함정과 한계

iOS 에서도 Gemini 를 앱이 아니라 사파리나 크롬으로 열 수 있어서, 앱이 없다고 쓰지 않았다고 볼 수 없습니다. 이 경우 흔적은 [웹 브라우저](web.md)에서 다룬 브라우저 기록 쪽에 남습니다.

공개 도구 iLEAPP 의 분석기 목록에서 Gemini·Google 앱·AI 대화 전용 분석기를 찾지 못했지만, 목록 화면이 잘려 보여 지원하지 않는다고 단정할 수 없습니다. 쓰기 전에 도구의 최신 목록을 직접 확인합니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 계정 데이터 내보내기 | 대화 내용과 메시지 시각 | [계정 데이터 내보내기](export.md) |
| 사파리·크롬 방문 기록 | 앱 대신 웹 판을 쓴 흔적 | [웹 브라우저](web.md) |
| 음성 대화 기능 | Gemini Live 같은 음성 사용 | [음성 대화 기능](../../generative-media/voice-mode.md) |
| 서비스 회사 자료 | 서버에 남은 대화 원본 | [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md) |

## 실습

Gemini 흔적을 담은 공개 iOS 검체는 이번 조사에서 확인하지 못했습니다. 시험용 기기와 계정으로 아래 질문을 풀어 봅니다.

1. 앱을 설치하고 한 번 대화한 뒤 로컬 백업을 만들면, 백업 목록에 Gemini 앱의 파일이 들어갑니까?
2. 활동 저장을 끈 상태와 켠 상태에서 앱 컨테이너 안의 파일 수정 시각이 다르게 바뀝니까?
3. 기기 쪽 흔적으로 알아낸 사용 시각이 계정 데이터 내보내기의 시각과 맞습니까?

## 참고 문헌

1. Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961 (2026-09-25 열람)
2. Get started with the Gemini mobile app — https://support.google.com/gemini/answer/14554984?co=GENIE.Platform%3DAndroid&oco=0 (2026-09-25 열람)
3. Google Gemini — App Store — https://apps.apple.com/us/app/google-gemini/id6477489729 (2026-09-25 열람)
4. iLEAPP scripts/artifacts 목록 (GitHub) — https://github.com/abrignoni/iLEAPP/tree/main/scripts/artifacts (2026-09-25 열람)
