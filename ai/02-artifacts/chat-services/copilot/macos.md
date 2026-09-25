---
title: "Microsoft Copilot macOS 앱"
parent: "Microsoft Copilot"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 240
---

# macOS 앱 (macOS)

Microsoft 는 소비자용 Copilot 을 Mac 앱으로도 제공한다고 밝히지만, 배포 방식과 번들 ID, 기기 안의 저장 위치는 공식 문서에서 확인하지 못해서 이 페이지는 조사를 시작할 곳과 해석 기준만 적습니다.

> 확인 날짜: 2026-09. 근거는 Microsoft 개인정보 처리방침(2026년 9월 갱신) 한 줄이고, Mac App Store 페이지는 열리지 않았습니다(404). macOS 기기는 직접 관찰하지 않았고, 앱 버전과 최소 macOS 버전도 확인하지 못했습니다.

## 확인한 것과 확인하지 못한 것

개인정보 처리방침은 소비자용 Copilot 을 웹(`copilot.microsoft.com`)과 Windows, Mac, iOS, Android 앱으로 제공한다고 적습니다. Mac 앱에 대해 공식 문서로 확인한 내용은 여기까지이고, 나머지는 아래 표처럼 비어 있습니다.

| 항목 | 상태 |
|---|---|
| 배포 방식(Mac App Store 인지 아닌지) | 확인하지 못함 |
| 번들 ID, 최소 macOS 버전 | 확인하지 못함 |
| `~/Library/Containers`, `~/Library/Application Support` 아래 폴더 | 확인하지 못함 |
| 키체인 항목 이름 | 확인하지 못함 |
| 대화가 기기에 사본으로 남는지 | 확인하지 못함 |

대화 원본이 서버에만 있는지, 기기에도 남는지는 공식 문서가 말하지 않아서 어느 쪽으로도 단정하지 않습니다. 계정에 쌓인 활동 기록은 다른 기기와 마찬가지로 [계정 데이터 내보내기](export.md)로 받습니다.

## 조사할 때 볼 곳

앱 이름이나 번들 ID 를 모르는 상태라서, 검체에서 먼저 설치된 앱 목록과 사용자 라이브러리 폴더를 훑어 Copilot 관련 폴더를 찾고 그 이름을 기록합니다. 찾은 파일은 형식에 따라 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/plist/index.html), [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/sqlite/index.html), [LevelDB와 IndexedDB](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/leveldb-indexeddb.html) 페이지를 따라 읽고, 앱이 웹뷰를 쓴다면 [Electron·웹뷰 앱의 저장 구조](../../../01-foundations/storage-model/electron-webview.md)도 함께 봅니다. 로그인 정보가 키체인에 있을 수 있지만 항목 이름은 확인하지 못했고, 값을 여는 방법은 다루지 않습니다. 키체인의 일반 구조는 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html) 페이지에 있습니다.

폴더가 언제 생기고 바뀌었는지는 [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/filesystem/fsevents/index.html)에서, 앱이 남긴 로그는 [통합 로그 형식](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/unified-log/index.html)에서 찾아봅니다. 화면 기록·마이크 같은 권한을 앱에 준 적이 있는지는 [개인 정보 보호 권한](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/credentials/tcc/index.html)에서 확인합니다. 이 가운데 Copilot 앱이 실제로 무엇을 남기는지는 확인하지 못해서, 찾은 결과는 검체에서 본 사실로만 적습니다.

## 증거로서 의미

**증명하는 것.** 검체에서 Copilot 앱 번들과 사용자 데이터 폴더를 찾으면 그 Mac 에 앱이 설치되어 있었다고 쓸 수 있고, 사용자 데이터 폴더가 무엇을 뜻하는지는 그 안의 파일을 확인한 만큼만 씁니다. 서버 쪽 대화는 내보낸 활동 기록으로 증명합니다.

**증명하지 못하는 것.** 앱이 설치되어 있다는 사실만으로 대화를 했다거나 무엇을 물었는지는 알 수 없습니다. 로그인한 계정과 그 앞에 앉은 사람은 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)를 따로 따져 봅니다.

## 함정과 한계

이 페이지는 공식 문서 한 줄과 공통 원리만으로 썼고, Mac 앱의 실제 파일 모양은 검체에서 확인해야 합니다. 같은 계정을 웹이나 다른 기기에서 썼다면 대화가 그쪽에서 생겼을 수 있어서, [웹 브라우저](web.md)의 흔적과 [사파리](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/browsers/safari/index.html) 방문 기록도 함께 봅니다. 회사·학교 계정 대화는 소비자용 개인정보 안내가 아니라 조직의 보존 정책을 따르고, [Microsoft 365 Copilot](../../office-integrations/m365-copilot.md)에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 |
|---|---|
| [계정 데이터 내보내기](export.md) | 서버에 남은 프롬프트·응답 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱이 서비스와 통신한 시간대 |
| [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-mac/03-techniques/analysis/timeline/index.html) | 앱 폴더 변화와 다른 활동을 한 시간 축에 놓기 |

## 실습

시험용 Mac 과 개인 Microsoft 계정으로 직접 만든 검체에서 다음을 풀어 봅니다. Copilot 앱을 설치하고 대화한 뒤 사용자 라이브러리 아래에 새로 생긴 폴더는 무엇인가? 그 폴더 안에서 대화 내용이 평문으로 보이는 파일이 있는가, 아니면 계정 내보내기에서만 대화가 나오는가?

## 참고 문헌

1. Microsoft Privacy Statement (Microsoft Copilot 절), 2026-09 갱신 — https://www.microsoft.com/en-us/privacy/privacystatement
