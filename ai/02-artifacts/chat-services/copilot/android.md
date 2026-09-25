---
title: "Microsoft Copilot Android 앱"
parent: "Microsoft Copilot"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 250
---

# Android 앱 (Android)

Microsoft 는 소비자용 Copilot 을 Android 앱으로도 제공한다고 밝히지만, 패키지 이름과 앱 데이터 폴더 구조는 공식 문서에서 확인하지 못해서 이 페이지는 조사를 시작할 곳과 해석 기준만 적습니다.

> 확인 날짜: 2026-09. 근거는 Microsoft 개인정보 처리방침(2026년 9월 갱신) 한 줄입니다. Google Play 페이지는 짐작한 패키지 이름으로 열었지만 404 가 나와서 그 이름이 맞는지 알 수 없고, Android 기기는 직접 관찰하지 않았습니다. 앱 버전과 최소 Android 버전도 확인하지 못했습니다.

## 확인한 것과 확인하지 못한 것

개인정보 처리방침은 소비자용 Copilot 을 웹과 Windows, Mac, iOS, Android 앱으로 제공한다고 적습니다. Android 앱에 대해 공식 문서로 확인한 내용은 여기까지입니다.

| 항목 | 상태 |
|---|---|
| 패키지 이름 | 확인하지 못함 |
| 앱 데이터 폴더 아래 DB·설정 XML | 확인하지 못함 |
| Google Play 의 데이터 보안(Data safety) 항목 | 확인하지 못함 |
| 대화가 기기에 사본으로 남는지 | 확인하지 못함 |

대화 원본이 서버에만 있는지, 기기에도 남는지는 공식 문서가 말하지 않아서 어느 쪽으로도 단정하지 않습니다. 계정에 쌓인 활동 기록은 [계정 데이터 내보내기](export.md)로 받습니다.

## 조사할 때 볼 곳

패키지 이름을 확인하지 못했으니 이름을 짐작해 쓰지 않고, 검체의 설치 앱 목록에서 앱 이름으로 Copilot 을 찾은 다음 그 패키지 이름을 검체 기준으로 기록합니다. 앱 데이터가 어디에 어떤 짜임으로 놓이는지는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)를 따르고, 찾은 파일은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html), [설정 XML과 SharedPreferences](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/shared-preferences.html), [LevelDB와 IndexedDB](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/leveldb-indexeddb.html) 페이지를 따라 읽습니다.

앱 데이터 폴더는 보통 권한 없이 읽히지 않고, 저장 공간 암호화도 걸려 있습니다. 수집 범위가 어디까지 되는지는 [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html) 페이지를 참고하고, 이 페이지에서는 잠금 해제나 보안 우회 방법을 다루지 않습니다. 앱 데이터에 닿지 못하는 검체라면 계정 내보내기가 대화를 확보하는 주된 길입니다.

## 증거로서 의미

**증명하는 것.** 설치 앱 목록과 앱 데이터 폴더에서 Copilot 앱을 찾으면 그 기기에 앱이 설치되어 있었다고 쓸 수 있습니다. 서버 쪽 대화는 내보낸 활동 기록으로 증명합니다.

**증명하지 못하는 것.** 앱이 설치되어 있다는 사실만으로 대화를 했다거나 무엇을 물었는지는 알 수 없고, 기기 소유자와 대화한 사람이 같은지도 알 수 없습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)).

## 함정과 한계

이 페이지는 공식 문서 한 줄과 공통 원리만으로 썼고, 앱의 실제 파일 모양은 검체에서 확인해야 합니다. 인터넷에 도는 패키지 이름을 그대로 믿지 않고, 검체에 설치된 패키지로 확인합니다. 같은 계정을 브라우저에서 썼다면 [웹 브라우저](web.md) 흔적과 [크롬](https://urock-ailab.github.io/forensics-handbook-android/02-artifacts/browsers/chrome/index.html) 방문 기록도 함께 봅니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 |
|---|---|
| [계정 데이터 내보내기](export.md) | 서버에 남은 프롬프트·응답 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱이 서비스와 통신한 시간대 |
| [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-android/03-techniques/analysis/timeline/index.html) | 앱 설치·사용과 다른 활동을 한 시간 축에 놓기 |

## 실습

시험용 Android 기기와 개인 Microsoft 계정으로 직접 만든 검체에서 다음을 풀어 봅니다. 설치 앱 목록에서 Copilot 앱의 패키지 이름은 무엇으로 나오는가? 앱 데이터 폴더를 수집할 수 있었다면, 그 안에서 대화 내용이 보이는 파일이 있는가, 아니면 계정 내보내기에서만 대화가 나오는가?

## 참고 문헌

1. Microsoft Privacy Statement (Microsoft Copilot 절), 2026-09 갱신 — https://www.microsoft.com/en-us/privacy/privacystatement
