---
title: "Microsoft Copilot"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 210
has_children: true
has_toc: false
---

# Microsoft Copilot (Copilot)

소비자용 Microsoft Copilot 은 개인 Microsoft 계정으로 웹과 Windows·Mac·iOS·Android 앱에서 쓰는 대화형 AI 서비스이고, 대화 원본은 계정의 개인정보 대시보드에서 보고 내보내고 지울 수 있습니다.

## 왜 중요한가

Copilot 은 새 Windows 11 PC 에 기본으로 깔려 있고, Copilot 키나 Windows 키 + C 로 바로 열립니다 [7]. Microsoft Edge 와 Xbox 같은 다른 Microsoft 제품 안에도 들어 있습니다 [1]. 사용자가 따로 설치하지 않아도 쓸 수 있는 서비스라서, 설치 기록이 없다고 해서 사용하지 않았다고 보면 안 됩니다.

서비스는 프롬프트와 위치, 언어, 관련 설정을 써서 답을 만들고, 일부 시장에서는 대화 기록(저장한 메모리 포함)을 개인화에도 씁니다. 대화 데이터는 성능 감시, 오류 수정, 악용 방지, 서비스 제공과 개선에도 쓰지만, Copilot 앱에서 쓴 프롬프트·응답·파일 내용은 기반 모델 (foundation model) 학습에 쓰지 않는다고 밝힙니다 [1][2][3]. 조사에서는 계정 쪽 기록을 받는 길과 기기에서 사용 사실을 찾는 길을 함께 봅니다.

기기에 대화 사본이 남는지는 공식 문서에 나오지 않고, 공개 연구끼리도 결과가 다릅니다. Tyagi·Gong·Karabiyik(2025)은 Copilot 이 Android 와 iOS 모두에서 대화를 브라우저 데이터와 함께 평문으로 저장한다고 초록에 적었고, Android 기기에서 사용자 프롬프트, 브라우저 데이터, 위치 정보를 복구했다고 밝혔습니다 [10]. 초록에는 시험한 앱 판이 나오지 않습니다. 반대로 LEAF 저장소의 스키마 문서는 2026-04-20 에 Android 15 기기에서 뽑은 `com.microsoft.copilot` 폴더에 대화 저장이 없고, 그 폴더의 `be6e4c19699f4fdf9f8c0ec9f9b398ef.db` 는 `StorageRecord` 표(`blob` 칸)에 Microsoft 원격 측정 이벤트를 쌓는 대기열이라고 적었습니다 [11]. 같은 저장소의 README 는 이 앱을 "SQLite 안의 암호화한 JSON" 이라고 적어 문서끼리 어긋나므로, 보조 자료로만 봅니다. 앱 판에 따라 저장 방식이 바뀌었을 수 있으니, 검체에서 앱 판을 먼저 확인하고 폴더를 직접 열어 봅니다. 서버와 기기 가운데 어디에 무엇이 있는지의 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

회사에서 Microsoft Purview 를 쓰면 개인용 Copilot 대화도 회사 쪽에 남을 수 있습니다. Purview 보존 정책의 "Other AI apps" 위치에 "Microsoft Copilot (consumer version)" 이 들어 있고, 조직에 내용을 수집하는 정책(collection policy)이 있어야 프롬프트와 응답이 보존 대상이 됩니다 [9]. 자세한 내용은 [Microsoft Purview로 본 Copilot 기록](../../network-enterprise/purview-copilot.md)에서 다룹니다.

이 묶음은 개인 Microsoft 계정으로 쓰는 소비자용 Copilot 만 다룹니다. 개인정보 안내 문서들도 개인 Microsoft 계정으로 로그인했을 때에만 적용된다고 밝힙니다 [2][3]. 회사·학교(Microsoft Entra) 계정으로 소비자용 앱에 로그인하려 하면 기본 브라우저에서 `https://m365.cloud.microsoft/chat` 이 열립니다 [6]. 이쪽은 기업 데이터 보호 (EDP) 약정이 붙는 별개 제품이라서 [Microsoft 365 Copilot](../../office-integrations/m365-copilot.md)에서 다룹니다. 개발 도구인 [GitHub Copilot](../../dev-agents/github-copilot/index.md)도 이름만 같은 다른 제품입니다.

## 한눈에 보기

| 어디서 | 위치·식별 정보 | 앱 판 | 알려 주는 것 |
|---|---|---|---|
| 웹 | `copilot.microsoft.com` | 해당 없음(웹 서비스) | 브라우저 방문 기록으로 본 접속 사실 |
| Windows | Microsoft Store 앱, AppLocker 규칙의 패키지 이름 `MICROSOFT.COPILOT` [6] | 공식 문서에 판 번호가 없어 검체의 패키지 정보로 확인 | 설치 흔적, 관리 정책, Copilot 키 설정 |
| macOS | 번들 ID `com.microsoft.copilot-mac` [14] | Mac App Store 판 `25.7.440902001`(MOFA 목록, 2026-09-25 갱신) [14] | 앱 폴더 위치는 검체에서 확인 |
| Android | 패키지 `com.microsoft.copilot` [12][13], 실행 액티비티 `com.microsoft.copilotn.MainActivity` [13] | 공개 자료에 판 번호가 없어 검체에서 확인 | 연구에 따라 평문 대화·프롬프트·위치(2025) [10] 또는 원격 측정 대기열만(2026-04) [11] |
| iOS | App Store ID `id6472538445` [12], 번들 ID 는 공개 자료가 없어 검체에서 확인 | 공개 자료에 판 번호가 없어 검체에서 확인 | 평문 대화와 브라우저 데이터(2025) [10] |
| 계정 | 개인정보 대시보드(`account.microsoft.com/privacy`), CSV 내보내기 [4][5] | 해당 없음 | 서버에 남은 프롬프트와 응답 |

Android 패키지 이름(`copilot`)과 실행 액티비티의 접두어(`copilotn`)가 다르므로, 로그나 실행 기록을 찾을 때는 두 문자열을 모두 검색합니다 [13]. LEAPP 계열 도구(ALEAPP·iLEAPP·RLEAPP)에는 Copilot 전용 분석기가 없어서(2026-09-25 저장소 목록 기준) [16], 앱 폴더는 SQLite·캐시 파일을 직접 열어 봅니다.

계정 내보내기 CSV 는 첫 줄이 `Conversation,Time,Author,Message` 이고, `Author` 값은 `Human` 과 `AI` 입니다. `Time` 칸에는 시간대 표시가 없고, 대화 ID 와 메시지 ID 도 없습니다. 이 형식은 2026년 7월에 받은 실제 내보내기를 기준으로 한 공개 파서에서 확인한 것입니다 [15]. 줄 순서, BOM, 시각 해석은 [계정 데이터 내보내기](export.md)에서 다룹니다.

앱 폴더를 직접 볼 때 필요한 공통 원리는 OS 별 핸드북을 따릅니다. Windows 는 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)와 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html), macOS 는 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html), Android 는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html), iOS 는 [데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html)를 봅니다.

### 이름이 같은 회사용 앱 가리기

Microsoft 는 회사용 앱에도 "Microsoft Copilot app" 이라는 이름을 씁니다. 관리 문서는 예전 Microsoft 365 app 이 지금의 Microsoft Copilot app 이라고 적고 [6], Copilot 키 정책 설명은 이 앱의 AUMID 를 `Microsoft.MicrosoftOfficeHub_8wekyb3d8bbwe!Microsoft.MicrosoftOfficeHub` 로 듭니다 [8]. 앱 목록에 보이는 이름만으로는 소비자용인지 회사용인지 가릴 수 없으므로, 아래 식별자로 가립니다.

| 제품 | Windows | macOS | iOS |
|---|---|---|---|
| 소비자용 Microsoft Copilot | 패키지 `Microsoft.Copilot` [6] | `com.microsoft.copilot-mac` [14] | App Store `id6472538445` [12] |
| 회사용 Microsoft Copilot app(옛 Microsoft 365 app) | 패키지 `Microsoft.MicrosoftOfficeHub` [8] | `com.microsoft.m365copilot` [14] | `com.microsoft.officemobile` [14] |

MOFA 목록은 macOS 의 `com.microsoft.m365copilot` 과 iOS 의 `com.microsoft.officemobile` 도 "Microsoft Copilot" 이라는 이름으로 적습니다 [14]. macOS 항목에는 Microsoft 365 Copilot 릴리스 노트 링크가 붙어 있지만, iOS 항목에는 이름과 판 번호만 있으므로 검체의 앱 정보로 어느 쪽 앱인지 한 번 더 확인합니다 [14]. Copilot 키가 어느 앱을 여는지는 정책과 설정에 따라 달라지므로, 키 설정은 [Windows 앱](windows.md) 쪽에서 확인합니다.

## 읽는 순서

1. [웹 브라우저 (Web)](web.md) — `copilot.microsoft.com` 방문 기록과 브라우저 저장소에서 볼 수 있는 것과 없는 것
2. [Windows 앱 (Windows)](windows.md) — `Microsoft.Copilot` 패키지, Copilot 키와 관리 정책, 이름이 헷갈리는 제품 가리기
3. [macOS 앱 (macOS)](macos.md) — `com.microsoft.copilot-mac` 앱과 검체에서 확인할 곳
4. [Android 앱 (Android)](android.md) — `com.microsoft.copilot` 폴더, 논문과 공개 관찰이 서로 다른 점
5. [iOS 앱 (iOS)](ios.md) — App Store 앱과 검체에서 확인할 곳
6. [계정 데이터 내보내기 (Data Export)](export.md) — 개인정보 대시보드의 활동 기록, CSV 형식, 삭제

기기 흔적만으로는 대화 내용을 알 수 없는 경우가 있어서, 어느 기기에서 썼는지 먼저 가린 뒤 계정 데이터 내보내기로 넘어가면 됩니다. 계정 데이터를 사용자 협조 없이 받아야 하면 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 봅니다.

## 함께 볼 페이지

- [브라우저에 들어간 AI](../../office-integrations/browser-builtin-ai.md) — Edge 안의 Copilot
- [Recall](../../windows-ai/recall.md) — Recall 을 켠 PC 에서 Copilot 창이 찍힌 스냅숏
- [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) — 기기 기록을 지웠을 때 남는 접속 흔적
- [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md) — 서비스별 내보내기 형식 비교
- [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md) — 보관과 삭제의 일반 원리
- [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md) — 계정 기록과 실제 사용자 가리기

## 참고 문헌

1. Microsoft Privacy Statement (Microsoft Copilot 절), 2026-09 갱신 — https://www.microsoft.com/en-us/privacy/privacystatement
2. Microsoft Copilot for individuals: your privacy controls and choices — https://support.microsoft.com/privacy/microsoft-copilot/privacy-controls
3. Microsoft Copilot for individuals: your data, privacy, and responsible AI — https://support.microsoft.com/privacy/microsoft-copilot/overview
4. Manage your Copilot activity history in the privacy dashboard — https://support.microsoft.com/privacy/manage-your-copilot-activity-history-in-the-privacy-dashboard
5. Microsoft Copilot for individuals: your activity history — https://support.microsoft.com/privacy/microsoft-copilot/activity-history
6. Updated Windows and Microsoft Copilot Chat experience (Microsoft Learn, 2026-08-18 갱신) — https://learn.microsoft.com/en-us/windows/client-management/manage-windows-copilot
7. Getting started with Copilot on Windows (2026-08-17) — https://support.microsoft.com/topic/1159c61f-86c3-4755-bf83-7fbff7e0982d
8. WindowsAI Policy CSP (Microsoft Learn, 2026-09-10), SetCopilotHardwareKey 절 — https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-windowsai
9. Learn about retention for Copilot & AI apps (Microsoft Learn) — https://learn.microsoft.com/en-us/purview/retention-policies-copilot
10. Sonali Tyagi, Yufeng Gong, Umit Karabiyik, "Forensic analysis and privacy implications of LLM mobile apps: A case study of ChatGPT, Copilot, and Gemini", Forensic Science International: Digital Investigation, 54 (2025), 301974. https://doi.org/10.1016/j.fsidi.2025.301974 (초록)
11. LEAF-Digital-Forensics, `docs/parser-schemas.md`, `leaf/README.md`(보조 자료) — https://github.com/MarcosAOSperoni/LEAF-Digital-Forensics
12. plausible/analytics, `priv/ua_inspector/client.mobile_apps.yml`(Microsoft Copilot 항목의 Play·App Store 주소) — https://github.com/plausible/analytics/blob/master/priv/ua_inspector/client.mobile_apps.yml
13. WSTxda/SwitchAI, `app/src/main/java/com/wstxda/switchai/assistant/CopilotAssistant.kt` — https://github.com/WSTxda/SwitchAI
14. cocopuff2u/MOFA, `README.md`(macOS·iOS App Store 목록, 2026-09-25 갱신) — https://github.com/cocopuff2u/MOFA
15. vladsadovsky/llm-aggregator.ts, `electron/services/import/archive/parsers/copilotCsv.ts` — https://github.com/vladsadovsky/llm-aggregator.ts
16. abrignoni/ALEAPP·iLEAPP·RLEAPP, `scripts/artifacts/` — https://github.com/abrignoni/ALEAPP, https://github.com/abrignoni/iLEAPP, https://github.com/abrignoni/RLEAPP
