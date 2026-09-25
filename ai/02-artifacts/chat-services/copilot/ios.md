---
title: "Microsoft Copilot iOS 앱"
parent: "Microsoft Copilot"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 260
---

# iOS 앱 (iOS)

Microsoft 는 소비자용 Copilot 을 iOS 앱으로도 제공한다고 밝히지만, 번들 ID 와 앱 컨테이너 구조, 백업에 들어가는지는 공식 문서에서 확인하지 못해서 이 페이지는 조사를 시작할 곳과 해석 기준만 적습니다.

> 확인 날짜: 2026-09. 근거는 Microsoft 개인정보 처리방침(2026년 9월 갱신) 한 줄이고, App Store 페이지는 열리지 않았습니다(404). iOS 기기는 직접 관찰하지 않았고, 앱 버전과 최소 iOS 버전, App Store 개인정보 라벨도 확인하지 못했습니다.

## 확인한 것과 확인하지 못한 것

개인정보 처리방침은 소비자용 Copilot 을 웹과 Windows, Mac, iOS, Android 앱으로 제공한다고 적습니다. iOS 앱에 대해 공식 문서로 확인한 내용은 여기까지입니다.

| 항목 | 상태 |
|---|---|
| App Store ID, 번들 ID | 확인하지 못함 |
| 앱 컨테이너 안의 DB·plist | 확인하지 못함 |
| 로컬 백업에 앱 데이터가 들어가는지 | 확인하지 못함 |
| 키체인 항목 이름 | 확인하지 못함 |
| 대화가 기기에 사본으로 남는지 | 확인하지 못함 |

대화 원본이 서버에만 있는지, 기기에도 남는지는 공식 문서가 말하지 않아서 어느 쪽으로도 단정하지 않습니다. 계정에 쌓인 활동 기록은 [계정 데이터 내보내기](export.md)로 받습니다.

## 조사할 때 볼 곳

번들 ID 를 모르니 짐작해 쓰지 않고, 검체의 설치 앱 목록이나 백업 안의 앱 목록에서 Copilot 을 찾아 번들 ID 를 검체 기준으로 기록합니다. 로컬 백업을 받는 방법과 그 안의 짜임은 [로컬 백업](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/backups/local-backup/index.html) 페이지를 따르고, 찾은 파일은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/sqlite/index.html)와 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/plist.html) 페이지를 따라 읽습니다. 앱 데이터가 백업에 빠져 있을 수 있어서, 백업에 앱 폴더가 없다고 앱을 쓰지 않았다고 보지 않습니다.

기기의 파일은 데이터 보호 등급에 따라 잠금 상태에서 읽히지 않을 수 있고, 로그인 정보는 키체인에 있을 수 있지만 항목 이름은 확인하지 못했습니다. 일반 원리는 [데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html)와 [키체인](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/keychain.html) 페이지에 있고, 이 페이지에서는 잠금 해제나 보안 우회 방법을 다루지 않습니다.

## 증거로서 의미

**증명하는 것.** 설치 앱 목록이나 백업에서 Copilot 앱을 찾으면 그 기기에 앱이 설치되어 있었다고 쓸 수 있습니다. 서버 쪽 대화는 내보낸 활동 기록으로 증명합니다.

**증명하지 못하는 것.** 앱이 설치되어 있다는 사실만으로 대화를 했다거나 무엇을 물었는지는 알 수 없고, 기기 소유자와 대화한 사람이 같은지도 알 수 없습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)).

## 함정과 한계

이 페이지는 공식 문서 한 줄과 공통 원리만으로 썼고, 앱의 실제 파일 모양은 검체에서 확인해야 합니다. 같은 계정을 브라우저에서 썼다면 [웹 브라우저](web.md) 흔적과 함께 [사파리](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/safari/index.html)나 [크롬](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/chrome.html) 방문 기록도 봅니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 |
|---|---|
| [계정 데이터 내보내기](export.md) | 서버에 남은 프롬프트·응답 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱이 서비스와 통신한 시간대 |
| [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-ios/03-techniques/analysis/timeline/index.html) | 앱 설치·사용과 다른 활동을 한 시간 축에 놓기 |

## 실습

시험용 iPhone 과 개인 Microsoft 계정으로 직접 만든 검체에서 다음을 풀어 봅니다. 로컬 백업의 앱 목록에서 Copilot 앱의 번들 ID 는 무엇으로 나오는가? 백업 안에 앱 폴더가 있다면 대화 내용이 보이는 파일이 있는가, 아니면 계정 내보내기에서만 대화가 나오는가?

## 참고 문헌

1. Microsoft Privacy Statement (Microsoft Copilot 절), 2026-09 갱신 — https://www.microsoft.com/en-us/privacy/privacystatement
