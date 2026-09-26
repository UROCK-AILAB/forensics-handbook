---
title: "Microsoft Copilot macOS 앱"
parent: "Microsoft Copilot"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 240
---

# macOS 앱 (macOS)

Microsoft 는 소비자용 Copilot 을 Mac 앱으로도 제공하고, 이 앱은 Mac App Store 에 번들 ID `com.microsoft.copilot-mac` 으로 올라와 있습니다. 기기 안의 저장 위치와 파일 형식은 공개된 분석 자료가 없어 검체로 확인해야 하므로, 이 페이지는 조사를 시작할 곳과 해석 기준을 적습니다.

## 공개 자료로 알 수 있는 것

Microsoft 는 소비자용 Copilot 을 웹(`copilot.microsoft.com`)과 Windows, Mac, iOS, Android 앱으로 제공합니다[1]. Mac App Store 의 "Microsoft Copilot" 은 번들 ID 가 `com.microsoft.copilot-mac` 이고, 2026-09-25 기준 판은 `25.7.440902001` 입니다[2]. 판은 그때의 값이라서, 검체에 설치된 판은 앱 번들의 `Info.plist` 에서 따로 읽습니다.

App Store 를 거치지 않는 독립 설치 패키지에도 "Microsoft Copilot" 이 있지만, 이쪽은 번들 ID 가 `com.microsoft.m365copilot` 이고 최소 macOS 14.0, 판 `1.2608 (0301)`(2026-08-03 갱신)이며 Microsoft 365 Copilot 릴리스 노트로 이어집니다[2]. 이름이 같아도 회사·학교 계정용 앱이므로 번들 ID 로 둘을 구별하고, 이 앱은 [Microsoft 365 Copilot](../../office-integrations/m365-copilot.md)에서 다룹니다.

| 항목 | 내용 |
|---|---|
| 배포 방식 | Mac App Store[2] |
| 번들 ID | `com.microsoft.copilot-mac`[2] |
| 목록에 적힌 판 | `25.7.440902001`(2026-09-25 목록 기준)[2] |
| 최소 macOS 판 | 공개 자료 없음. 검체의 `Info.plist` 에서 확인 |
| 사용자 데이터 폴더, 키체인 항목 이름 | 공개된 분석 자료가 없어 검체로 확인 |
| 대화가 기기에 사본으로 남는지 | 공식 문서에 언급 없음. 검체로 확인 |

대화 원본이 서버에만 있는지, 기기에도 남는지는 공식 문서가 말하지 않아서 어느 쪽으로도 단정하지 않습니다. 계정에 쌓인 활동 기록은 다른 기기와 마찬가지로 [계정 데이터 내보내기](export.md)로 받습니다.

## 조사할 때 볼 곳

검체에서 먼저 `/Applications` 아래 Copilot 앱 번들을 찾아 `Info.plist` 의 번들 ID 와 판을 기록하고, 사용자 라이브러리 폴더(`~/Library/Containers`, `~/Library/Application Support` 등)에서 번들 ID 가 들어간 폴더를 찾습니다. 찾은 파일은 형식에 따라 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/plist/index.html), [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/sqlite/index.html), [LevelDB와 IndexedDB](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/leveldb-indexeddb.html) 페이지를 따라 읽고, 앱이 웹뷰를 쓰면 [Electron·웹뷰 앱의 저장 구조](../../../01-foundations/storage-model/electron-webview.md)도 함께 봅니다. 로그인 정보는 키체인에 있을 수 있으니 검체에서 번들 ID 나 Microsoft 가 들어간 항목 이름을 찾되, 이 페이지는 값을 여는 방법을 다루지 않습니다. 키체인의 일반 구조는 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html) 페이지에 있습니다.

폴더가 언제 생기고 바뀌었는지는 [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/filesystem/fsevents/index.html)에서, 앱이 남긴 로그는 [통합 로그 형식](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/unified-log/index.html)에서 번들 ID 로 걸러 찾습니다. 화면 기록·마이크 같은 권한을 앱에 준 적이 있는지는 [개인 정보 보호 권한](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/credentials/tcc/index.html)에서 번들 ID 로 확인합니다. 이 기록들에 Copilot 앱이 무엇을 남기는지는 공개된 분석 자료가 없어서, 결과는 검체에서 본 사실로만 적습니다.

## 증거로서 의미

**증명하는 것.** 검체에서 번들 ID 가 `com.microsoft.copilot-mac` 인 앱 번들과 사용자 데이터 폴더를 찾으면 그 Mac 에 앱이 설치되어 있었다고 쓸 수 있고, 사용자 데이터 폴더가 무엇을 뜻하는지는 그 안의 파일을 확인한 만큼만 씁니다. 서버 쪽 대화는 내보낸 활동 기록으로 증명합니다.

**증명하지 못하는 것.** 앱이 설치되어 있다는 사실만으로 대화를 했다거나 무엇을 물었는지는 알 수 없습니다. 로그인한 계정과 그 앞에 앉은 사람은 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)를 따로 따져 봅니다.

## 함정과 한계

Mac 앱의 실제 파일 모양은 공개된 분석 자료가 없어 검체에서 확인합니다. 같은 계정을 웹이나 다른 기기에서 썼다면 대화가 그쪽에서 생겼을 수 있어서, [웹 브라우저](web.md)의 흔적과 [사파리](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/browsers/safari/index.html) 방문 기록도 함께 봅니다. 회사·학교 계정 대화는 소비자용 개인정보 안내가 아니라 조직의 보존 정책을 따르고, [Microsoft 365 Copilot](../../office-integrations/m365-copilot.md)에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 |
|---|---|
| [계정 데이터 내보내기](export.md) | 서버에 남은 프롬프트·응답 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱이 서비스와 통신한 시간대 |
| [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-mac/03-techniques/analysis/timeline/index.html) | 앱 폴더 변화와 다른 활동을 한 시간 축에 놓기 |

## 실습

시험용 Mac 과 개인 Microsoft 계정으로 직접 만든 검체에서 다음을 풀어 봅니다. Copilot 앱을 설치하고 대화한 뒤 사용자 라이브러리 아래에 번들 ID `com.microsoft.copilot-mac` 이름으로 새로 생긴 폴더는 무엇인가? 그 폴더 안에서 대화 내용이 평문으로 보이는 파일이 있는가, 아니면 계정 내보내기에서만 대화가 나오는가?

## 참고 문헌

1. Microsoft Privacy Statement (Microsoft Copilot 절), 2026-09 갱신 — https://www.microsoft.com/en-us/privacy/privacystatement
2. cocopuff2u, MOFA, `README.md`(Microsoft MacOS AppStore Packages, Microsoft Standalone Packages 목록, 2026-09-25 갱신) — https://github.com/cocopuff2u/MOFA
