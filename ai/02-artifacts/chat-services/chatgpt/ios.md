---
title: "ChatGPT iOS 앱"
parent: "ChatGPT"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 120
---

# iOS 앱 (iOS)

iOS 용 ChatGPT 앱은 App Store 항목 `id6448311069` 로 배포하고 2026-09-25 기준 최신 버전은 1.2026.258 이지만, 앱 컨테이너 안에 무엇이 남는지와 백업에 들어가는지는 공개 자료로 확인하지 못했습니다.

> 확인 날짜: 2026-09-25. App Store 페이지를 바탕으로 썼습니다. OpenAI 공식 도움말은 열람하지 못했고, 이 핸드북은 iOS 기기에서 이 앱의 컨테이너를 관찰하지 못했습니다. 번들 ID, 컨테이너 안 파일 이름(Core Data·SQLite 이름, plist 키), 백업 포함 여부는 적지 않았습니다.

## 무엇이 남나 · 왜 생기나

App Store 페이지에서 확인할 수 있는 것은 배포 정보와 개인정보 라벨이고, 기기 안의 저장 구조는 알려 주지 않습니다. 대화 원본이 어디에 있는지는 [ChatGPT](index.md) 허브에서 정리했고, 이 페이지는 iOS 기기 쪽 길잡이와 App Store 정보를 읽는 법을 다룹니다.

## App Store 정보

| 항목 | 값(2026-09-25 확인) |
|---|---|
| App Store 항목 | `id6448311069` |
| 개발사 | OpenAI OpCo, LLC |
| 버전 | 1.2026.258(페이지에 "1일 전" 출시로 표시, 2026-09-24 무렵) |
| 요구 사양 | iOS 18.0 이상, iPadOS 18.0 이상, visionOS 2.0 이상 |
| 크기 | 238.2 MB |
| 분류·등급 | Productivity, 13+ |
| Mac App Store 항목 | 이 항목에는 없음(macOS 앱은 [macOS 앱](macos.md)에서 따로 다룸) |

버전 번호는 아래와 같은 모양으로 보이고, 가운데 자리에 연도가 들어갑니다. 끝자리가 무엇을 세는 번호인지는 확인하지 못했습니다.

```
1.<연도>.<일련번호>      예: 1.2026.258
```

같은 항목이 iPad 와 Vision Pro 도 지원해서, 한 계정의 흔적이 iPhone 말고 다른 Apple 기기에도 있을 수 있습니다. 조사할 기기에 깔린 앱의 버전을 먼저 적어 두면, 다른 버전에서 확인한 내용을 섞어 쓰는 실수를 줄일 수 있습니다.

### 개인정보 라벨

App Store 의 "Data Linked to You" 라벨에는 Health & Fitness, Location, Contact Info, User Content, Search History, Identifiers, Usage Data, Diagnostics 가 적혀 있습니다. 이 라벨도 개발사가 신고한 수집 항목이라서, [Android 앱](android.md)의 데이터 안전 항목과 마찬가지로 서버로 모으는 데이터의 종류로 읽고 기기에 남는 데이터 목록으로 읽지 않습니다. 서버에 모은 데이터는 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)이나 [계정 데이터 내보내기](export.md)로 확보합니다.

### 앱 안 결제 항목

App Store 에 적힌 앱 안 결제 항목의 이름은 ChatGPT Plus, ChatGPT Go, ChatGPT Pro 5x, ChatGPT Pro 20x, 그리고 100·500·1000 Credits 입니다(2026-09-25 확인). 기기나 Apple 계정의 구매 기록에 이 이름이 있으면 그 계정이 어떤 요금제를 쓰고 있었는지 가늠하는 단서가 될 수 있습니다.

## 위치와 보호 방식

iOS 앱은 데이터를 주로 자기 컨테이너에 두고, 파일은 기기의 [데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html) 등급에 따라 잠깁니다. ChatGPT 앱의 번들 ID 와 컨테이너 안 파일 이름은 확인하지 못해서, 수집한 자료에서 번들 ID 를 먼저 찾은 뒤 그 컨테이너를 엽니다. 로그인 정보처럼 비밀 값을 두는 곳의 일반 원리는 [키체인](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/keychain.html)에 있지만, ChatGPT 앱이 무엇을 키체인에 두는지는 확인하지 못했습니다.

컨테이너에서 파일을 찾았다면 형식별 페이지를 따라 읽습니다. 데이터베이스는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/sqlite/index.html), 설정 파일은 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/plist.html)에서 다룹니다.

앱 데이터가 [로컬 백업](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/backups/local-backup/index.html)에 들어가는지는 확인하지 못했습니다. 백업에서 이 앱의 흔적을 찾지 못했다면 백업에서 빠진 것인지, 앱이 기기에 남기지 않은 것인지부터 가립니다.

## 증거로서 의미

**증명하는 것.** 기기에 앱이 설치돼 있었다면 그 기기에 ChatGPT 앱이 있었다고 쓸 수 있고, 설치된 버전을 알면 그 버전이 App Store 에 나온 시기와 견줄 수 있습니다. 구매 기록에 위 결제 항목이 있으면 그 계정으로 그 항목을 구매한 기록이 있다고 쓸 수 있습니다.

**증명하지 못하는 것.** App Store 정보와 개인정보 라벨은 이 사용자가 무엇을 입력했는지 알려 주지 않습니다. 컨테이너에 대화 사본이 있는지 확인하지 못해서, 대화를 찾지 못했다고 대화를 하지 않았다고 볼 수 없습니다. 기기를 쓴 사람이 누구인지는 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)에서처럼 다른 기록과 맞춥니다.

## 시각 해석

App Store 페이지의 출시 표시는 "1일 전" 처럼 상대 시각이라서, 날짜로 적을 때는 페이지를 연 날짜를 함께 적고 "무렵" 으로 씁니다. 컨테이너 안 파일의 시각은 앱이 동기화하거나 캐시를 새로 쓸 때도 바뀔 수 있어서 대화한 시각으로 바로 옮기지 않습니다. 기기의 여러 기록을 한 줄로 세우는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-ios/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

App Store 정보는 앱을 업데이트할 때마다 바뀌어서, 이 페이지의 버전·크기·요구 사양은 2026-09-25 의 값입니다. 조사할 때는 페이지를 다시 열어 날짜와 함께 기록합니다. 사파리나 크롬으로 쓴 ChatGPT 는 앱이 아니라 [웹 브라우저](web.md) 흔적으로 남고, 그쪽 기록은 [사파리](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/safari/index.html)와 [크롬 (Chrome for iOS)](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/chrome.html) 페이지에서 읽습니다.

## 직접 분석해 보기

앱 내부 형식을 확인하지 못해서 헥스 예시는 싣지 않았습니다. 컨테이너에서 파일을 찾으면 헥스로 앞부분을 열어 SQLite 나 plist 같은 알려진 형식의 머리 글자가 있는지 보고, 그다음 형식별 페이지에 적힌 공개 도구로 엽니다. 이 앱 데이터에 맞춘 공개 파서는 이번 조사에서 확인하지 못했습니다.

## 교차 검증

기기의 앱 흔적은 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)으로 본 접속 시간대, 그리고 [계정 데이터 내보내기](export.md)로 확보한 대화의 시각과 맞춥니다. 음성으로 대화했다면 [음성 대화 기능](../../generative-media/voice-mode.md)도 함께 봅니다.

## 실습

공개 검체 가운데 ChatGPT iOS 앱을 담은 것은 이번에 찾지 못했습니다. 시험용 기기에 앱을 깔고 시험용 계정으로 가짜 대화를 만든 뒤 다음을 풀어 봅니다.

1. 로컬 백업을 만들어 이 앱의 컨테이너가 백업에 들어가는지 확인합니다.
2. 들어간다면 대화 제목이나 본문이 평문으로 남는 파일이 있는지 확인합니다.
3. 앱에서 대화를 지운 뒤 다시 백업해 무엇이 바뀌는지 봅니다.

## 참고 문헌

- App Store, ChatGPT (OpenAI OpCo, LLC) — https://apps.apple.com/us/app/chatgpt/id6448311069
