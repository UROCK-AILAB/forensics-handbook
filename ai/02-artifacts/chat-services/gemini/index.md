---
title: "Gemini"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 280
has_children: true
has_toc: false
---

# Gemini (Gemini)

## 한 줄 요약

Gemini 는 Google 의 대화형 AI 서비스이고, 웹·Android·iOS·Chrome 어디서 쓰든 대화는 Google 계정에 묶여 서버의 Gemini 앱 활동 (Gemini Apps Activity) 에 저장됩니다 [1].

## 왜 중요한가

Gemini 는 웹(gemini.google.com)과 Android·iOS 앱에서 쓰고, Chrome 브라우저 안에도 들어 있습니다(Gemini in Chrome) [1][2]. Android 와 iOS 에서 ChatGPT·Copilot 은 대화를 기기에 평문으로 저장하지만, Gemini 는 대화·브라우저 데이터·이미지를 모두 클라우드에 두고 이를 Google Takeout 으로 받을 수 있습니다 [9]. Android 15 기기(2026-04)에서 수집한 Gemini 앱 폴더에도 SQLite 데이터베이스는 하나도 없었고, 파일 13개가 모두 WebView 캐시와 컴파일된 OAT 파일이었습니다 [10]. 다만 같은 저장소의 README 는 저장 형식을 "Protocol Buffer encoded in SQLite" 라고 적어 자기 문서끼리 어긋나므로 보조 근거로만 봅니다 [10]. 그래서 대화 내용은 계정 데이터 내보내기와 서비스 회사에 대한 데이터 요청으로 확인하고, 기기에서는 언제 어떤 경로로 Gemini 를 썼는지 보여 주는 흔적을 찾습니다.

서버에 얼마나 남는지는 활동 저장 (Keep Activity) 설정에 달려 있습니다. 기본값은 켬이고 자동 삭제 기본값은 18개월이며, 사용자가 3개월·36개월·끄기(무기한)로 바꿀 수 있습니다 [1][3]. 활동 저장을 꺼도 대화는 계정과 함께 72시간 보관되지만 이 기록은 활동 목록에 보이지 않고, 임시 채팅 (Temporary Chats) 도 72시간 보관한 뒤 지웁니다 [1][3]. 사람 검토 (human review) 를 거친 대화는 최대 3년 보관하고, 사용자가 활동 기록을 지워도 이 사본은 지워지지 않습니다 [1]. 활동 목록에 없는 대화도 서버에는 남아 있을 수 있으니 이 점을 넣어 조사 범위를 정합니다. 보관 설정의 공통 개념은 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md) 에서 다룹니다.

Gemini 가 모으는 항목은 넓습니다. 프롬프트와 음성 입력, 올린 파일·사진·화면, Gemini Live 대화 녹취와 녹음, 맞춤 지시 (custom instructions), 생성 결과물, 연결된 앱의 데이터(검색·YouTube·Chrome 기록 등), 기기 정보(통화·메시지 기록, 연락처, 설치된 앱, 언어), 위치, 구독 정보가 들어 있습니다 [1]. 위치는 활동 기록에 저장하기 전에 3제곱킬로미터보다 넓고 사용자가 1,000명 이상인 구역으로 뭉개고, 정확한 위치는 기기 권한이 있을 때만 씁니다 [1]. 2025년 논문의 시험에서는 iOS 기기의 위치 설정을 꺼 둔 상태에서도 Gemini 와 ChatGPT 에서 반경 0.5마일(약 800m) 안의 위치 데이터를 얻을 수 있었습니다 [9]. Google Labs 의 실험 기능 Opal 에서 만든 Gems 는 Gemini 앱에 속하지 않고, Google Drive 의 "Opal" 폴더에 저장되며 활동 기록에 나오지 않습니다 [1].

Takeout 보관 파일에서 Gemini 활동은 "My Activity" 폴더 아래 "Gemini Apps" 폴더에 들어갑니다. 공개 변환 도구들은 My Activity 형식을 JSON 으로 골랐을 때 경로를 `Takeout/My Activity/Gemini Apps/MyActivity.json` 으로 적었고 [12][13], 다른 도구는 `My Activity.json` 을 적고 `MyActivity.json` 은 예전 이름이라고 적었습니다 [11]. 파일 이름은 언어 설정에 따라 바뀌고, 폴더 이름까지 그리스어로 된 경로 예가 있습니다 [13]. 기록은 가지가 있는 대화가 아니라 활동을 하나씩 늘어놓은 목록이고 항목마다 따로 떨어져 있어서, 공개 도구는 30분 간격 같은 시간 기준으로 묶어 대화를 추정합니다 [13]. 답변이 보관 파일에 들어가는지는 도구끼리 다릅니다. 한 도구는 Takeout 이 답변을 내보내지 않는다고 적었고 [11], 다른 두 도구는 `safeHtmlItem` 필드를 답변으로 읽습니다 [12][13]. 그러니 실제 보관 파일에서 답변 필드가 있는지 먼저 봅니다. 파일 구조와 필드는 [계정 데이터 내보내기](export.md) 에서 다룹니다.

공개 분석 도구 가운데 ALEAPP·iLEAPP·RLEAPP 에는 Gemini 전용 분석기가 없습니다(2026-09-25 main 브랜치 기준) [14]. RLEAPP 의 `takeoutMyActivity.py`(2026-07-09 갱신)는 `*/My Activity/*/MyActivity.html` 을 서비스 폴더 이름별로 보고서에 붙이기만 하고, 내용을 행으로 풀지는 않습니다 [15]. 지금 판의 도구는 다를 수 있으니 쓰기 전에 저장소를 다시 봅니다.

이름이 비슷한 Gemini CLI 는 다른 제품이라 [Gemini CLI](../../dev-agents/gemini-cli.md) 에서 따로 다루고, Gmail·문서 같은 업무 도구 안의 Gemini 는 [Google Workspace의 Gemini](../../office-integrations/workspace-gemini.md) 에서 다룹니다.

## 한눈에 보기

| 쓰는 곳 | 기록이 있는 곳 | OS·환경 | 앱 버전 | 알려 주는 것 |
|---|---|---|---|---|
| 웹 브라우저 | 서버 활동 기록. 브라우저 쪽 흔적은 공개 분석 자료가 없어 실제 브라우저 프로필에서 확인 | 브라우저 | 웹 서비스라 앱 버전 없음 | 서버에 남은 프롬프트와 대화, 공개 링크 목록, Gems 관리 페이지 [1][3] |
| Android 앱 | 서버 활동 기록. 앱 패키지는 `com.google.android.apps.bard` 이고 [10], 앱을 받아도 Google 앱이 Gemini 를 실행 [5] | Android | 버전은 기기의 패키지 정보에서 확인 | 권한을 Google 앱 설정에서 관리하는 구조, 기본 어시스턴트로 골랐는지 [5]. Android 15(2026-04 수집본)의 앱 폴더에 SQLite DB 없음 [10] |
| iOS 앱 | 서버 활동 기록. 별도 앱 "Google Gemini" | iOS·iPadOS 17.4 이상 | 1.2026.3770306(2026-09 App Store) | App Store 개인정보 라벨이 적은 수집 항목 [6], 위치 설정을 끈 상태에서도 반경 0.5마일 안 위치 [9] |
| Chrome 통합 | 서버 활동 기록, Chrome 설정 파일(Preferences·Local State)의 설정 키 | Windows·Mac·Chromebook Plus | 관리 정책은 Windows·macOS Chrome 137 부터 | 내부 이름 glic 으로 시작하는 설정 키, 기업 관리 정책 [2][7][8] |
| 계정 데이터 내보내기 | Google Takeout 보관 파일(.zip 또는 .tgz). JSON 이면 `Takeout/My Activity/Gemini Apps/MyActivity.json` | 계정 단위 | 해당 없음 | 활동 기록의 채팅·생성 미디어·올린 파일, Gems 데이터 [4][12][13] |

Chrome 설정 키 이름은 Chromium 소스(2026-09 main 브랜치)에 정의돼 있습니다 [8]. 키에 어떤 값이 들어가는지는 실제 Preferences·Local State 파일을 열어 확인합니다.

## 읽는 순서

1. [웹 브라우저 (Web)](web.md) — 서버 활동 기록을 보는 곳, 공개 링크와 Gems 관리 페이지를 다룹니다.
2. [Android 앱 (Android)](android.md) — Google 앱이 Gemini 를 실행하는 구조, 기본 어시스턴트 설정, 여는 방법과 권한, 앱 폴더에 남는 파일을 다룹니다.
3. [iOS 앱 (iOS)](ios.md) — 별도 앱의 버전·요구 사항, App Store 개인정보 라벨, 위치 데이터를 다룹니다.
4. [Chrome 통합 (Gemini in Chrome)](chrome.md) — 탭 내용을 공유하는 방식, glic 설정 키, 기업 관리 정책을 다룹니다.
5. [계정 데이터 내보내기 (Data Export)](export.md) — Google Takeout 에서 고르는 항목과 받는 방법, 보관 파일의 경로와 필드, 내보내기에 빠질 수 있는 기록을 다룹니다.

## 함께 볼 페이지

- [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)
- [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)
- [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md)
- [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)
- [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)
- [브라우저에 들어간 AI (Edge Copilot·Chrome Gemini 등)](../../office-integrations/browser-builtin-ai.md)
- [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)
- [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)
- [windows] [크롬 계열 브라우저 (Chrome·Edge·Whale 등)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html)
- [android] [앱 데이터 폴더 구조 (/data/data·/data/user)](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html)

## 참고 문헌

1. Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961 (2026-09-25 열람, 마지막 갱신 2026-09-24)
2. Use Gemini in Chrome - Computer - Google Chrome Help — https://support.google.com/chrome/answer/16283624
3. Manage & delete your activity in Gemini Apps - Computer - Gemini Apps Help — https://support.google.com/gemini/answer/13278892
4. Download your Gemini Apps data — https://support.google.com/gemini/answer/16920332?hl=en
5. Get started with the Gemini mobile app (Android) — https://support.google.com/gemini/answer/14554984?co=GENIE.Platform%3DAndroid&oco=0
6. Google Gemini — App Store — https://apps.apple.com/us/app/google-gemini/id6477489729
7. Chromium 정책 정의 GeminiSettings.yaml — https://raw.githubusercontent.com/chromium/chromium/main/components/policy/resources/templates/policy_definitions/GenerativeAI/GeminiSettings.yaml
8. Chromium glic_pref_names.h — https://raw.githubusercontent.com/chromium/chromium/main/chrome/browser/glic/glic_pref_names.h
9. Sonali Tyagi, Yufeng Gong, Umit Karabiyik, "Forensic analysis and privacy implications of LLM mobile apps: A case study of ChatGPT, Copilot, and Gemini", Forensic Science International: Digital Investigation, 54 (2025), 301974. https://doi.org/10.1016/j.fsidi.2025.301974 (초록)
10. LEAF-Digital-Forensics, `docs/parser-schemas.md`(2026-04-20 수집, Android 15)와 `leaf/README.md`(보조 자료) — https://github.com/MarcosAOSperoni/LEAF-Digital-Forensics
11. remnic, `packages/import-gemini/src/parser.ts` — https://github.com/joshuaswarren/remnic
12. gemini-to-obsidian, `README.md`·`gemini-to-obsidian.py` — https://github.com/Coryrichter94/gemini-to-obsidian
13. AI-Conversation-Toolkit, `docs/gemini-extractor.md` — https://github.com/silver-gr/AI-Conversation-Toolkit
14. ALEAPP·iLEAPP·RLEAPP 저장소 파일 목록(2026-09-25 main) — https://github.com/abrignoni/ALEAPP, https://github.com/abrignoni/iLEAPP, https://github.com/abrignoni/RLEAPP
15. RLEAPP, `scripts/artifacts/takeoutMyActivity.py`(2025-07-23 작성, 2026-07-09 갱신) — https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/takeoutMyActivity.py
