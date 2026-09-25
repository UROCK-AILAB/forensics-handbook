---
title: "Microsoft Copilot"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 210
has_children: true
has_toc: false
---

# Microsoft Copilot (Copilot)

소비자용 Microsoft Copilot 은 개인 Microsoft 계정으로 웹과 Windows·Mac·iOS·Android 앱에서 쓰는 대화형 AI 서비스이고, 대화 기록은 계정의 개인정보 대시보드에서 보고 내보내고 지울 수 있지만 기기에 어떤 사본이 남는지는 공식 문서에 없습니다.

> 확인 날짜: 2026-09-25. Microsoft 공식 문서(개인정보 처리방침, support.microsoft.com, learn.microsoft.com)만 근거로 썼습니다. 개인정보 처리방침의 마지막 갱신은 2026년 9월이고, 개인정보 제어 안내와 활동 기록 안내는 2026-08-18 앱 버전 갱신을 언급합니다. 이 묶음의 어느 페이지도 기기에서 Copilot 앱 폴더를 직접 관찰하지 않았고, 앱 버전 번호는 확인하지 못했습니다.

## 왜 중요한가

Copilot 은 새 Windows 11 PC 에 기본으로 깔려 있고 Copilot 키나 Windows 키 + C 로 바로 열리는 데다, Microsoft Edge 와 Xbox 같은 다른 Microsoft 제품 안에도 들어 있습니다. 사용자가 따로 설치하지 않아도 쓸 수 있는 서비스라서, 설치 기록이 없다고 사용하지 않았다고 보지 않습니다.

서비스는 프롬프트와 위치, 언어, 관련 설정을 써서 답을 만들고, 일부 시장에서는 대화 기록(저장한 메모리 포함)을 개인화에도 씁니다. 대화 데이터는 성능 감시, 오류 수정, 악용 방지, 서비스 제공과 개선에도 쓰지만, Copilot 앱에서 쓴 프롬프트·응답·파일 내용은 기반 모델 (foundation model) 학습에 쓰지 않는다고 밝힙니다. 조사에서는 계정 쪽 기록을 받는 길과 기기에서 사용 사실을 찾는 길을 함께 봅니다.

공식 문서는 대화 원본을 개인정보 대시보드에서 보고 내보내고 지울 수 있다는 데까지만 설명합니다. 대화가 기기에 사본으로 남는지는 문서에 없어서, 이 묶음은 "서버에만 있다" 고도 "기기에 남는다" 고도 단정하지 않습니다. 서버 보관 기간, 업로드한 파일의 보관 기간, 로그인하지 않고 썼을 때의 처리 방식도 공식 문서에서 찾지 못했습니다. 서버와 기기 가운데 어디에 무엇이 있는지의 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

이 묶음은 개인 Microsoft 계정으로 쓰는 소비자용 Copilot 만 다룹니다. 개인정보 안내 문서들도 개인 Microsoft 계정으로 로그인했을 때에만 적용된다고 밝힙니다. 회사·학교(Microsoft Entra) 계정은 소비자용 앱에 로그인할 수 없고 브라우저에서 `https://m365.cloud.microsoft/chat` 으로 넘어가는데, 이쪽은 기업 데이터 보호 (EDP) 약정이 붙는 별개 제품이라서 [Microsoft 365 Copilot](../../office-integrations/m365-copilot.md)과 [Microsoft Purview로 본 Copilot 기록](../../network-enterprise/purview-copilot.md)에서 다룹니다. 개발 도구인 [GitHub Copilot](../../dev-agents/github-copilot/index.md)도 이름만 같은 다른 제품입니다.

## 한눈에 보기

| 어디서 | 위치·식별 정보 | 앱 버전 | 알려 주는 것 |
|---|---|---|---|
| 웹 | `copilot.microsoft.com` | 해당 없음(웹 서비스) | 브라우저 방문 기록으로 본 접속 사실 |
| Windows | 스토어 앱, 패키지 이름 `Microsoft.Copilot` | 확인하지 못함 | 설치 흔적, 관리 정책 |
| macOS | 앱이 있다는 사실만 공식 문서로 확인 | 확인하지 못함 | 저장 위치를 확인하지 못함 |
| Android | 앱이 있다는 사실만 공식 문서로 확인 | 확인하지 못함 | 패키지 이름을 확인하지 못함 |
| iOS | 앱이 있다는 사실만 공식 문서로 확인 | 확인하지 못함 | 번들 ID 를 확인하지 못함 |
| 계정 | 개인정보 대시보드(`account.microsoft.com/privacy`), CSV 내보내기 | 해당 없음 | 서버에 남은 프롬프트와 응답 |

앱의 로컬 저장 위치, 파일 형식, DB 표 이름은 어느 OS 에서도 공식 문서에 없고 기기에서도 보지 못했습니다. 앱 폴더를 직접 볼 때 필요한 공통 원리는 OS 별 페이지를 따릅니다. Windows 는 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)와 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html), macOS 는 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html), Android 는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html), iOS 는 [데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html)를 봅니다.

## 읽는 순서

1. [웹 브라우저 (Web)](web.md) — `copilot.microsoft.com` 방문 기록과 브라우저 저장소에서 볼 수 있는 것과 없는 것
2. [Windows 앱 (Windows)](windows.md) — `Microsoft.Copilot` 패키지, Copilot 키와 관리 정책, 이름이 헷갈리는 제품 가리기
3. [macOS 앱 (macOS)](macos.md) — 공식 문서로 확인한 범위와 검체에서 확인할 것
4. [Android 앱 (Android)](android.md) — 공식 문서로 확인한 범위와 패키지 이름을 모를 때 조사할 곳
5. [iOS 앱 (iOS)](ios.md) — 공식 문서로 확인한 범위와 검체에서 확인할 것
6. [계정 데이터 내보내기 (Data Export)](export.md) — 개인정보 대시보드의 두 갈래 활동 기록과 CSV 내보내기, 삭제

기기 흔적만으로는 대화 내용을 알 수 없는 경우가 많아서, 어느 기기에서 썼는지 가린 뒤 계정 데이터 내보내기로 넘어가는 순서가 자연스럽습니다.

## 함께 볼 페이지

- [브라우저에 들어간 AI](../../office-integrations/browser-builtin-ai.md) — Edge 안의 Copilot
- [Recall](../../windows-ai/recall.md) — Recall 을 켠 PC 에서 Copilot 창이 찍힌 스냅숏
- [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) — 기기 기록을 지웠을 때 남는 접속 흔적
- [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md) — 보관과 삭제의 일반 원리
- [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md) — 계정 기록과 실제 사용자 가리기

## 참고 문헌

1. Microsoft Privacy Statement (Microsoft Copilot 절), 2026-09 갱신 — https://www.microsoft.com/en-us/privacy/privacystatement
2. Microsoft Copilot for individuals: your privacy controls and choices — https://support.microsoft.com/privacy/microsoft-copilot/privacy-controls
3. Microsoft Copilot for individuals: your data, privacy, and responsible AI — https://support.microsoft.com/privacy/microsoft-copilot/overview
4. Manage your Copilot activity history in the privacy dashboard — https://support.microsoft.com/privacy/manage-your-copilot-activity-history-in-the-privacy-dashboard
5. Microsoft Copilot for individuals: your activity history — https://support.microsoft.com/privacy/microsoft-copilot/activity-history
6. Updated Windows and Microsoft Copilot Chat experience (Microsoft Learn, 2026-08-18 갱신) — https://learn.microsoft.com/en-us/windows/client-management/manage-windows-copilot
7. Getting started with Copilot on Windows — https://support.microsoft.com/topic/1159c61f-86c3-4755-bf83-7fbff7e0982d
