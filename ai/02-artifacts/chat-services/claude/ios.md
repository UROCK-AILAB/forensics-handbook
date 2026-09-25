---
title: "Claude iOS 앱"
parent: "Claude"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 190
---

# iOS 앱 (iOS)

iPhone·iPad 의 Claude 앱은 App Store 에서 받는 앱이고 대화 원본은 계정 서버에 있습니다. 앱 컨테이너 안에 무엇이 남는지는 확인하지 못해서, 이 페이지는 앱을 알아보는 기준과 App Store 의 개인정보 표기를 정리합니다.

> 확인 날짜: 2026-09. App Store 페이지와 공식 도움말(2026-09-25 열람)만 근거로 썼습니다. iPhone·iPad 기기는 직접 관찰하지 않았습니다.

## 무엇이 남나 · 왜 생기나

App Store 의 앱 이름은 "Claude by Anthropic", 판매자는 Anthropic PBC 이고, 2026-09-25 에 본 버전은 1.260923.20, 크기는 169.2 MB 였습니다[1]. iOS 18.0 이상과 iPadOS 18.0 이상에서 돌아갑니다[1]. 앱은 claude.ai 와 같은 계정으로 로그인해 쓰고 대화는 서버에 저장되며, 지운 대화의 서버 쪽 처리는 [Claude](index.md) 허브에 정리해 두었습니다.

기기에는 앱 컨테이너가 생기지만 번들 ID 와 컨테이너 안의 파일·데이터베이스 이름, 대화 본문을 기기에 두는지는 확인하지 못했습니다. iOS 앱에서는 계정 데이터를 내보낼 수 없고, 내보내기는 웹이나 데스크톱 앱에서만 됩니다[2]. 대화 내용이 필요하면 [계정 데이터 내보내기](export.md)를 웹이나 PC 에서 받거나 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 검토합니다.

## 버전

| 확인 날짜 | 버전 | 크기 | 지원 OS | 근거 |
|---|---|---|---|---|
| 2026-09-25 | 1.260923.20 | 169.2 MB | iOS 18.0 이상, iPadOS 18.0 이상 | [1] |

App Store 페이지의 버전·크기·지원 OS 는 확인한 날의 최신 버전 기준이라서, 검체 기기에 깔린 버전은 기기 쪽 자료에서 따로 확인하고 이 표와 비교합니다.

## 위치와 읽는 법

앱 컨테이너 안의 경로를 확인하지 못해서 이 페이지에는 경로를 적지 않습니다. 앱 데이터를 얻는 길과 읽는 법은 공통 페이지를 따릅니다. 기기 잠금과 파일별 보호 등급 때문에 무엇을 언제 읽을 수 있는지는 [데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html)에서, 로컬 백업에 앱 데이터가 들어가는지 확인하는 방법은 [로컬 백업](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/backups/local-backup/index.html)에서 다룹니다. 컨테이너에서 데이터베이스나 설정 파일을 찾으면 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/sqlite/index.html)와 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/plist.html)의 방법으로 읽고, 로그인 정보를 키체인에 두는지는 확인하지 못했지만 키체인의 구조는 [키체인](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/keychain.html)에 있습니다.

## App Store 의 개인정보 표기

App Store 페이지의 App Privacy 는 "사용자에게 연결된 데이터"를 쓰는 목적별로 다음처럼 적고 있습니다[1].

| 목적 | 표기한 데이터 |
|---|---|
| 광고·마케팅 | 대략적 위치, 연락처 정보, 식별자, 사용 데이터 |
| 분석 | 위치, 사용자 콘텐츠, 식별자, 사용 데이터, 진단 |
| 앱 기능 | 위치, 연락처 정보, 사용자 콘텐츠, 식별자, 사용 데이터, 진단 |

추적에 쓰는 데이터 항목은 표기에 없었습니다[1]. 이 표기는 서비스가 어떤 종류의 데이터를 다루는지 알려 주지만, 기기 안 어느 파일에 무엇이 남는지는 알려 주지 않습니다. 서비스 회사에 자료를 요청할 때 어떤 항목이 있을 수 있는지 가늠하는 데 씁니다. 같은 기준의 Android 표기는 [Android 앱](android.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 기기의 설치 앱 목록이나 백업에 이 앱이 있으면 그 기기에 앱이 설치된 적이 있다고 쓸 수 있습니다.

**증명하지 못하는 것.** 앱 컨테이너의 내용을 확인하지 못해서, 앱이 있다는 사실만으로 어떤 대화를 했는지나 언제 마지막으로 썼는지는 말할 수 없습니다. 앱이 없어도 사파리나 다른 브라우저로 claude.ai 를 썼을 수 있어서 [웹 브라우저](web.md), [사파리](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/safari/index.html), [크롬 (Chrome for iOS)](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/chrome.html)도 봅니다. 누가 기기를 쥐고 있었는지는 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)의 방법으로 좁힙니다.

## 시각 해석

앱 컨테이너 안의 시각 칸은 확인하지 못했습니다. 설치 시각과 기기 쪽 시각은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-ios/03-techniques/analysis/timeline/index.html)의 방법으로 읽고, 대화마다의 시각은 계정 데이터 내보내기 자료에서 얻습니다. 기기 시각과 서버 자료의 시각을 맞추는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

App Store 에는 비슷한 이름의 다른 앱이 있을 수 있어서, 앱 이름만으로 가리지 말고 판매자와 번들 ID 를 함께 확인합니다. 번들 ID 는 이 핸드북에서 확인하지 못했으니 검체 기기에서 얻은 값을 보고서에 그대로 적습니다. 로컬 백업이나 논리 수집으로 앱 데이터가 나오지 않았다고 앱에 흔적이 없다고 쓰지 않고, 어떤 수집 방식으로 무엇을 얻었는지를 함께 적습니다. App Store 호환 표기는 iPhone·iPad 뿐이어서[1], Mac 의 Claude 흔적은 [macOS 앱](macos.md)에서 봅니다.

## 직접 분석해 보기

앱 컨테이너의 파일을 확인하지 못해서 헥스 예시는 싣지 않습니다. 앱 데이터를 얻었다면 다음 순서로 봅니다.

1. 설치 앱 목록에서 판매자가 Anthropic PBC 인 Claude 앱을 찾고 번들 ID 와 버전을 적습니다.
2. 그 번들 ID 에 해당하는 앱 컨테이너의 하위 폴더 목록을 적습니다.
3. 파일 첫 바이트로 형식을 가리고, SQLite 는 표 이름부터, plist 는 키 이름부터 적습니다.
4. 찾은 내용은 확인한 앱 버전·날짜와 함께 기록하고, 이 페이지의 버전 표와 비교합니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [웹 브라우저](web.md) | 휴대폰 브라우저로 쓴 흔적 |
| [계정 데이터 내보내기](export.md) | 대화 본문과 시각 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 회사 네트워크에서 접속한 기록 |
| [Android 앱](android.md) | 같은 사람이 다른 휴대폰에서 쓴 경우 |

## 실습

직접 만든 시험용 기기의 로컬 백업이나 공개 검체(NIST CFReDS 등)의 iOS 이미지로 다음을 풀어 봅니다.

1. 설치 앱 목록에 판매자가 Anthropic PBC 인 앱이 있는가, 있다면 번들 ID 와 버전은 무엇인가?
2. 로컬 백업에 그 앱의 컨테이너 파일이 들어 있는가, 들어 있다면 어떤 파일 형식이 보이는가?
3. 사파리 방문 기록의 claude.ai 방문과 앱 설치 시각 가운데 어느 쪽이 먼저인가?

## 참고 문헌

1. Claude by Anthropic — App Store — https://apps.apple.com/us/app/claude-by-anthropic/id6473753684
2. How can I export my Claude data? (Claude Help Center) — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data
