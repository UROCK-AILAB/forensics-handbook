---
title: "Gemini"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 280
has_children: true
has_toc: false
---

# Gemini (Gemini)

## 한 줄 요약

Gemini 는 Google 의 대화형 AI 서비스이고, 웹·Android·iOS·Chrome 어디서 쓰든 대화는 Google 계정에 묶여 서버의 활동 기록 (Gemini Apps Activity) 에 저장됩니다.

## 왜 중요한가

Gemini 는 웹(gemini.google.com)과 Android·iOS 앱에서 쓰고, Chrome 브라우저 안에도 들어 있습니다(Gemini in Chrome) [1][2]. 대화 원본은 서버에 있고 웹·앱을 쓴 기기에 대화 전문이 남는지는 공식 문서에 나와 있지 않습니다. 그래서 대화 내용은 서버 쪽 활동 기록과 계정 데이터 내보내기로 확인하고, 기기에서는 언제 어떤 경로로 Gemini 를 썼는지 보여 주는 흔적을 찾게 됩니다.

서버에 얼마나 남는지는 활동 저장 (Keep Activity) 설정에 달려 있습니다. 기본값은 켬이고 자동 삭제 기본값은 18개월이며, 사용자가 3개월·36개월·끄기(무기한)로 바꿀 수 있습니다 [1][3]. 활동 저장을 꺼도 대화는 계정과 함께 72시간 보관되지만 이 기록은 활동 목록에 보이지 않고, 임시 채팅 (Temporary Chats) 도 72시간 보관한 뒤 지웁니다 [1][3]. 사람 검토 (human review) 를 거친 대화는 최대 3년 보관하고, 사용자가 활동 기록을 지워도 이 사본은 지워지지 않습니다 [1]. 활동 목록에 없는 대화도 서버에는 남아 있을 수 있다는 점을 염두에 두고 조사 범위를 정합니다. 보관 설정의 공통 개념은 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md) 에서 다룹니다.

Google 개인정보 안내가 적은 수집 항목은 넓습니다. 프롬프트와 음성 입력, 올린 파일·사진·화면, Gemini Live 대화 녹취와 녹음, 맞춤 지시 (custom instructions), 생성 결과물, 연결된 앱의 데이터(검색·YouTube·Chrome 기록 등), 기기 정보(통화·메시지 기록, 연락처, 설치된 앱, 언어), 위치, 구독 정보가 들어 있습니다 [1]. 위치는 활동 기록에 저장하기 전에 3제곱킬로미터보다 넓고 사용자가 1,000명 이상인 구역으로 뭉개고, 정확한 위치는 기기 권한이 있을 때만 씁니다 [1]. Google Labs 의 실험 기능 Opal 에서 만든 Gems 는 Gemini Apps 에 속하지 않고, Google Drive 의 "Opal" 폴더에 저장되며 활동 기록에 나오지 않습니다 [1].

이름이 비슷한 Gemini CLI 는 다른 제품이라 [Gemini CLI](../../dev-agents/gemini-cli.md) 에서 따로 다루고, Gmail·문서 같은 업무 도구 안의 Gemini 는 [Google Workspace의 Gemini](../../office-integrations/workspace-gemini.md) 에서 다룹니다.

이 핸드북의 기기 관찰(Windows 11, 2026-09)에는 Gemini 웹·앱·Chrome 통합이 들어 있지 않습니다. 이 허브와 하위 페이지의 사실은 Google 도움말, 앱 스토어, Chromium 소스에서 가져왔고(확인 날짜 2026-09-25), 기기에 남는 흔적을 직접 관찰했다고 쓰지 않습니다.

## 한눈에 보기

| 쓰는 곳 | 기록이 있는 곳 | OS·환경 | 앱 버전(2026-09 확인) | 알려 주는 것 |
|---|---|---|---|---|
| 웹 브라우저 | 서버 활동 기록. 브라우저 캐시·저장소에 대화가 남는지는 확인 못 함 | 브라우저 | 웹 서비스라 앱 버전 없음 | 서버에 남은 프롬프트와 대화, 공개 링크 목록, Gems 관리 페이지 [1][3] |
| Android 앱 | 서버 활동 기록. 앱을 받아도 Google 앱이 Gemini 를 실행 | Android | 패키지 이름·버전 확인 못 함 | 권한을 Google 앱 설정에서 관리하는 구조, 기본 어시스턴트로 골랐는지 [1][5] |
| iOS 앱 | 서버 활동 기록. 별도 앱 "Google Gemini" | iOS·iPadOS 17.4 이상 | 1.2026.3770306 | App Store 개인정보 라벨이 적은 수집 항목. 앱 안 저장 경로는 확인 못 함 [6] |
| Chrome 통합 | 서버 활동 기록, Chrome 설정 파일(Preferences·Local State)의 설정 키 | Windows·Mac·Chromebook Plus | 관리 정책은 Windows·macOS Chrome 137 부터 | 내부 이름 glic 으로 시작하는 설정 키, 기업 관리 정책 [2][7][8] |
| 계정 데이터 내보내기 | Google Takeout 보관 파일(.zip 또는 .tgz) | 계정 단위 | 해당 없음 | 활동 기록의 채팅·생성 미디어·올린 파일, Gems 데이터 [4] |

Chrome 설정 키 이름은 Chromium 소스(2026-09 main 브랜치)에서 확인했고, 실제 설정 파일에 어떤 값으로 남는지는 확인하지 못했습니다 [8].

## 읽는 순서

1. [웹 브라우저 (Web)](web.md) — 서버 활동 기록을 보는 곳, 공개 링크와 Gems 관리 페이지, 브라우저 쪽에서 확인하지 못한 부분을 정리합니다.
2. [Android 앱 (Android)](android.md) — Google 앱이 Gemini 를 실행하는 구조, 기본 어시스턴트 설정, 여는 방법과 권한을 다룹니다.
3. [iOS 앱 (iOS)](ios.md) — 별도 앱의 버전·요구 사항과 App Store 개인정보 라벨을 다룹니다.
4. [Chrome 통합 (Gemini in Chrome)](chrome.md) — 탭 내용을 공유하는 방식, glic 설정 키, 기업 관리 정책을 다룹니다.
5. [계정 데이터 내보내기 (Data Export)](export.md) — Google Takeout 에서 고르는 항목과 받는 방법, 내보내기에 빠질 수 있는 기록을 다룹니다.

## 함께 볼 페이지

- [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)
- [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)
- [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md)
- [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)
- [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)
- [브라우저에 들어간 AI (Edge Copilot·Chrome Gemini 등)](../../office-integrations/browser-builtin-ai.md)
- [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)
- [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)
- [windows] [크롬 계열 브라우저 (Chrome·Edge·Whale 등)](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)

## 참고 문헌

1. Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961 (2026-09-25 열람, 마지막 갱신 2026-09-24)
2. Use Gemini in Chrome - Computer - Google Chrome Help — https://support.google.com/chrome/answer/16283624
3. Manage & delete your activity in Gemini Apps - Computer - Gemini Apps Help — https://support.google.com/gemini/answer/13278892
4. Download your Gemini Apps data — https://support.google.com/gemini/answer/16920332?hl=en
5. Get started with the Gemini mobile app (Android) — https://support.google.com/gemini/answer/14554984?co=GENIE.Platform%3DAndroid&oco=0
6. Google Gemini — App Store — https://apps.apple.com/us/app/google-gemini/id6477489729
7. Chromium 정책 정의 GeminiSettings.yaml — https://raw.githubusercontent.com/chromium/chromium/main/components/policy/resources/templates/policy_definitions/GenerativeAI/GeminiSettings.yaml
8. Chromium glic_pref_names.h — https://raw.githubusercontent.com/chromium/chromium/main/chrome/browser/glic/glic_pref_names.h
