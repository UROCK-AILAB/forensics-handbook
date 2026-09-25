---
title: "에이닷"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 370
---

# 에이닷 (A.)

에이닷은 SK텔레콤의 AI 에이전트 서비스로, 대화뿐만 아니라 통화 녹음 요약·일정 관리·먼저 보내는 알림까지 다루지만, 녹음과 요약이 폰에 남는지 서버에 올라가는지는 2026-09 현재 공개 자료로 확인하지 못했습니다.

> 확인 날짜: 2026-09. 서비스 연혁과 기능은 위키백과(2차 자료, 2026-09-25 열람)로만 확인했고, 개인정보 처리방침은 열어 보지 못했습니다. 이 PC 의 기기 관찰에는 에이닷이 없어서 관찰로 확인한 경로·파일 이름이 없고, 앱 버전과 Android 앱 패키지 이름, iOS 앱 폴더도 확인하지 못했습니다.

## 무엇을 기록하나 · 왜 생기나

에이닷은 2022-05-16 에 Android 베타로 나와 2023-09-26 에 정식으로 문을 열었고, 지금은 Android·iOS·PC·웹으로 제공합니다[1]. 위키백과는 서비스 유형을 "AI 에이전트 서비스" 로 적고, 한국어 GPT 를 바탕으로 초거대 언어 모델 (LLM) 과 ChatGPT 를 함께 섞어 운영한다고 설명합니다[1]. 위키백과 문서에는 이름을 바꾼 이력이 없습니다[1].

기능은 대화형 AI 에 그치지 않습니다. 통화 녹음 내용을 분석해 상대방과 나눈 대화를 자동으로 정리하는 통화 녹음·요약, 날씨·뉴스·교통·환율 같은 실시간 정보, 일정 관리, 사용자에게 먼저 말을 거는 개인화 알림이 있습니다[1]. 그래서 조사에서는 사용자가 에이닷에 입력한 글뿐만 아니라 통화 상대와 나눈 말의 요약, 일정, 알림 문구까지 흔적이 될 수 있고, 이 가운데 무엇이 기기에 남는지를 먼저 가려야 합니다. 서버와 기기의 몫을 가르는 기준은 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

## 위치와 버전별 차이

아래 표는 확인한 위치가 아니라 수집 범위를 정할 때 빠뜨리지 말아야 할 곳입니다.

| 쓰는 형태 | 확인한 로컬 위치 | 수집할 곳 |
|---|---|---|
| Android 앱 | 확인 못 함(패키지 이름도 확인 못 함) | 앱 데이터 폴더, 녹음 파일이 있을 만한 공용 저장 공간, 알림 기록 |
| iOS 앱 | 확인 못 함 | 백업·전체 추출본의 앱 컨테이너 |
| PC | 확인 못 함 | 설치 프로그램 목록과 사용자 폴더의 앱 데이터 |
| 웹 | 확인 못 함 | 쓰던 브라우저의 방문 기록·캐시·사이트 저장소 |

통화 녹음·요약이 쟁점이면 폰부터 수집하지만, 녹음 파일과 요약문이 실제로 어디에 저장되는지는 확인하지 못했습니다. Android 는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)와 [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html)를, iOS 는 [데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html)와 [로컬 백업](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/backups/local-backup/index.html)을 먼저 읽고, 어떤 추출 방식으로 어디까지 얻을 수 있는지 가늠합니다. PC 앱이 Electron 이나 웹뷰로 만든 것으로 보이면 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)를 봅니다. 기기별 수집 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)에 있습니다.

폰 앱은 업데이트가 잦아서, 추출할 때 앱 버전과 추출 날짜를 꼭 함께 적습니다.

## 구조

로컬 저장 구조(파일 이름, 데이터베이스 표, 설정 키, 녹음 파일 형식)는 확인한 자료가 없어서 쓰지 않습니다. 검체에서 앱 폴더를 찾았다면 파일 형식을 첫 바이트로 가린 뒤 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html)나 [설정 XML과 SharedPreferences](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/shared-preferences.html) 같은 형식 페이지로 읽고, 표나 키의 이름만 보고 뜻을 짐작해 보고서에 쓰지 않습니다.

## 증거로서 의미

**증명하는 것.** 폰에 녹음 요약문이 남아 있다면 그 요약이 한때 그 기기에 내려와 있었다는 기록이고, 앱 설치 기록과 네트워크 기록은 그 기기가 그 시간대에 서비스를 쓸 수 있었거나 서비스와 통신했다는 기록입니다. 보고서에는 "이 기기의 에이닷 앱 자료에 이 통화 상대와 관련된 요약문이 있다" 처럼 기록이 말하는 만큼만 씁니다.

**증명하지 못하는 것.** 요약문은 AI 가 통화를 정리한 글이라서 실제로 오간 말과 같다고 볼 수 없고, 요약에 빠지거나 잘못 옮긴 부분이 있을 수 있습니다. 원래 녹음과 대조하기 전에는 요약문의 문장을 통화 당사자가 한 말로 인용하지 않습니다. 기기에서 녹음이나 요약을 찾지 못해도 서버에 없다고 할 수 없고, 그 계정을 누가 썼는지도 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 좁힙니다.

## 시각 해석

통화 녹음 요약에는 통화 시각, 녹음 파일이 생긴 시각, 요약을 만든 시각이 따로 있을 수 있고, 세 시각이 같다고 가정하지 않습니다. 어느 시각이 어디에 적히는지는 확인하지 못해서, 검체에서 통화 기록의 시각과 맞춰 보며 가려냅니다. 기기 쪽 시각의 기준(UTC 인지 현지 시각인지)은 형식마다 다르고, 여러 출처를 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)과 [Android 타임라인 작성](https://urock-ailab.github.io/forensics-handbook-android/03-techniques/analysis/timeline/index.html)에 있습니다.

## 함정과 한계

녹음·요약의 서버 보관 기간, 삭제 뒤 파기 시점, 내보내기 기능은 확인하지 못했습니다. 사건 당시의 개인정보 처리방침을 따로 확보해 확인하고, 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에서 봅니다. 국내 통신사에 자료를 요청하는 절차는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)을 따릅니다.

먼저 말을 거는 알림은 사용자가 요청하지 않아도 생깁니다. 알림 기록에 에이닷 문구가 있다는 사실만으로 사용자가 그 시각에 에이닷을 썼다고 쓰면 안 되고, 앱을 연 기록이나 사용자가 입력한 기록과 구분합니다. 통화 녹음에는 통화 상대의 목소리와 개인정보가 들어 있어서, 수집·열람 범위를 영장이나 동의 범위 안으로 제한합니다.

## 직접 분석해 보기

**헥스로 한 번.** 앱 이름 문자열로 알림 기록이나 할당되지 않은 영역을 먼저 훑습니다. 아래는 문자 인코딩 명세대로 만든 예시이고, 검체에서 뜬 바이트가 아닙니다.

```
만든 예시(인코딩 명세로 만든 바이트)
"에이닷"  UTF-8     EC 97 90 EC 9D B4 EB 8B B7
"에이닷"  UTF-16LE  D0 C5 74 C7 F7 B2
```

**공개 도구로 한 번.** 폰 추출본의 사본 폴더에서 ripgrep 으로 이름이 들어간 파일을 추리고, 찾은 파일은 형식에 맞는 도구로 다시 엽니다. 경로는 만든 예시입니다.

```sh
# 만든 예시 경로
CASE=/cases/case-0004/copy/phone-dave
rg -a -l "에이닷" "$CASE"
```

알림에 남은 문구로 대화 조각을 되살리는 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)에 있습니다.

## 교차 검증

녹음 요약은 폰의 통화 기록과 시각·상대를 맞춰 보고, 음성 기능의 일반적인 흔적은 [음성 대화 기능](../generative-media/voice-mode.md)과 [AI 회의록 앱](../generative-media/meeting-notes.md)에서 비교합니다. 네트워크 쪽은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)을, 서버 쪽 원본은 [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md)을 봅니다.

## 실습

공개 검체에 에이닷 흔적이 들어 있는지는 확인하지 못했습니다. 시험용 폰과 시험 계정, 서로 동의한 시험 통화로 풀어 봅니다.

1. 시험 통화를 녹음·요약한 뒤 폰 추출본에서 녹음 파일과 요약문이 남는지, 남는다면 어느 폴더인지 찾아봅니다.
2. 통화 시각, 녹음 파일 시각, 요약 시각을 한 표에 적고 차이를 비교합니다.
3. 먼저 말을 거는 알림이 온 날의 알림 기록과 앱 사용 기록을 나란히 놓고, 사용자가 앱을 연 시각을 가려 봅니다.

## 참고 문헌

1. 에이닷 — 위키백과(한국어, 2차 자료) — https://ko.wikipedia.org/wiki/에이닷
