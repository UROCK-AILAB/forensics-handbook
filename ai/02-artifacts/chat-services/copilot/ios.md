---
title: "Microsoft Copilot iOS 앱"
parent: "Microsoft Copilot"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 260
---

# iOS 앱 (iOS)

Microsoft Copilot iOS 앱은 대화를 기기에 평문으로 남긴다는 연구가 있고, 설치 앱 목록에서 번들 ID 를 읽어 앱 데이터 폴더를 찾아가며 분석합니다.

## 무엇을 기록하나 · 왜 생기나

Microsoft 는 소비자용 Copilot 을 웹과 Windows, Mac, iOS, Android 앱으로 제공합니다 [1]. 앱의 App Store 주소는 `https://apps.apple.com/us/app/microsoft-copilot/id6472538445` 이고, 같은 앱의 Android 패키지는 `com.microsoft.copilot` 입니다 [3].

ChatGPT·Gemini·Copilot 모바일 앱을 Android 와 iOS 에서 분석한 2025년 논문에서, ChatGPT 와 Copilot 은 두 OS 모두에서 대화 데이터를 브라우저 데이터와 함께 평문으로 저장했습니다 [2]. 그래서 iOS 기기의 앱 데이터에 닿을 수 있으면 대화 내용이 기기에서 나올 수 있습니다.

같은 초록 안에서도 OS 나 앱이 다른 결과는 섞어 쓰지 않습니다. Copilot 에서 사용자 프롬프트·브라우저 데이터·위치 데이터를 복구한 것은 Android 기기의 결과입니다 [2]. 위치 설정을 끈 iOS 기기에서 반경 약 0.5마일로 위치가 드러난 앱은 Gemini 와 ChatGPT 이고, Copilot 은 여기에 들지 않습니다 [2]. Android 쪽 내용은 [Android 앱](android.md) 페이지에서 다룹니다.

## 위치와 버전별 차이

iOS 앱의 데이터 폴더는 `.../mobile/Containers/Data/Application/` 아래 UUID 이름 폴더입니다. iLEAPP 의 ChatGPT·Claude 분석기도 이 모양의 경로로 앱 파일을 찾습니다 [5]. UUID 는 기기마다 달라서, 먼저 번들 ID 를 알아낸 다음 그 번들 ID 가 쓰는 폴더를 찾아갑니다.

Copilot iOS 앱의 번들 ID 는 공개 자료에 나오지 않으니 검체에서 읽습니다. 아래 위치가 번들 ID 와 폴더를 이어 줍니다.

| 위치 | 담긴 것 | 근거 |
|---|---|---|
| `*/mobile/Library/FrontBoard/applicationState.db` | 앱마다 번들 ID, 앱 번들 경로(`bundlePath`), 데이터 폴더 경로(`sandboxPath`) | iLEAPP `applicationStateDB.py` [4] |
| `*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist` | 앱 그룹 폴더의 주인 번들 ID(`MCMMetadataIdentifier` 키) | iLEAPP `appGrouplisting.py` [6] |
| `*/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist` | 앱 확장 폴더의 주인 번들 ID(같은 키) | iLEAPP `appGrouplisting.py` [6] |

iLEAPP 의 두 분석기를 시험한 범위는 iOS 12.4 부터 iOS 18.7.8 까지입니다 [4][6]. 그보다 새 iOS 판에서는 모양이 다를 수 있습니다. 2025년 논문의 초록에는 시험한 Copilot 앱 판과 iOS 판이 나오지 않으니, 판을 인용하려면 논문 본문을 봅니다 [2].

로컬 백업에 이 앱의 데이터가 들어가는지, 로그인 정보가 키체인에 어떤 이름으로 남는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 백업을 받는 방법과 그 안의 짜임은 [로컬 백업](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/backups/local-backup/index.html) 페이지를 따릅니다. 잠금 상태에서 파일이 읽히는지는 [데이터 보호](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/data-protection/index.html), 키체인 구조는 [키체인](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/keychain.html) 페이지에 있습니다. 이 페이지는 잠금 해제나 보안 우회 방법을 다루지 않습니다.

## 구조

앱 데이터 폴더 안에서 대화가 어떤 파일에 어떤 짜임으로 들어 있는지는 공개된 분석 자료가 없습니다. iLEAPP 에는 Copilot 분석기가 없고, 2026-09-25 기준 저장소의 AI 대화 앱 분석기는 `chatgpt.py` 와 `iOSclaude.py` 두 개입니다 [5].

그래서 폴더 안의 파일을 하나씩 형식부터 가립니다. SQLite 파일은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/data-formats/sqlite/index.html), plist 는 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/data-formats/plist.html) 페이지를 따라 읽습니다. 대화가 브라우저 데이터와 함께 저장된다는 연구가 있으니 앱 안의 웹뷰 저장소도 살펴봅니다 [2]. 웹뷰 저장소의 일반 구조는 [Electron·웹뷰 앱의 저장 구조](../../../01-foundations/storage-model/electron-webview.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** `applicationState.db` 나 앱 그룹 메타데이터에서 Copilot 번들 ID 를 찾으면 그 기기에 앱이 설치된 적이 있다고 쓸 수 있습니다. 앱 데이터 폴더에서 평문 대화가 나오면, 그 계정의 대화 가운데 기기에 남은 부분을 보여 줍니다. 서버 쪽 대화는 [계정 데이터 내보내기](export.md)로 확인합니다.

**증명하지 못하는 것.** 앱이 설치되어 있다는 사실만으로 대화를 했다거나 무엇을 물었는지는 알 수 없습니다. 앱 판에 따라 기기에 두는 데이터가 다를 수 있어서, 기기에 대화가 없다고 대화가 없었다고 할 수도 없습니다. 기기 소유자와 대화한 사람이 같은지도 이 기록만으로는 알 수 없습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)).

## 시각 해석

Copilot 앱 파일 안의 시각 칸과 형식은 공개 자료에 없습니다. 검체에서 칸을 찾으면 값의 모양(유닉스 초·밀리초, Mac 절대 시각 등)과 시간대를 따로 확인합니다.

앱을 쓴 시점을 보조로 볼 때는 `applicationState.db` 의 화면 스냅숏 시각을 쓸 수 있습니다. iOS 18 과 iOS 26 추출본에서 `creationDate` 는 해당 스냅숏 파일의 UTC 수정 시각과 같습니다 [4]. `lastUsedDate` 는 드물게 채워지고, `creationDate` 보다 한참 뒤에 바뀔 수 있습니다 [4]. 두 값 모두 그 시각에 앱이 화면 앞에 있었다거나 사용자가 화면을 봤다는 증명은 아닙니다 [4].

## 함정과 한계

- `applicationState.db` 에 번들 ID 가 없다고 앱을 설치한 적이 없다고 보지 않습니다. 이 DB 에서 번들 ID 를 읽을 수 없는 앱은 iLEAPP 표에서 빠지고, 설치·삭제 이력은 Mobile Installation 로그에 남을 수 있습니다 [4].
- 앱 그룹 목록에는 기기에 더는 없는 앱의 항목이 남아 있을 수 있습니다 [6]. 이 항목 하나로 "지금 설치되어 있다" 고 쓰지 않습니다.
- 위 논문은 2025년 시점의 결과입니다 [2]. 앱이 바뀌면 기기에 두는 데이터도 바뀔 수 있으니 검체의 앱 판을 함께 적습니다.
- 초록의 iOS 위치 데이터 결과는 Copilot 이 아니라 Gemini·ChatGPT 의 것입니다 [2].
- 같은 계정을 브라우저에서도 썼다면 대화가 앱이 아니라 [웹 브라우저](web.md)에서 이뤄졌을 수 있습니다. [사파리](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/safari/index.html)나 [크롬](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/chrome.html) 방문 기록도 봅니다.
- 앱 데이터에 로그인 토큰이 남아 있으면 보고서에서 가립니다. 토큰이 남는 곳의 일반론은 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에 있고, 서버 쪽 자료는 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)으로 받습니다.

## 직접 분석해 보기

**번들 ID 와 폴더 찾기.** iLEAPP 을 파일 시스템 추출본에 돌리면 Installed Apps 분류의 "Application State" 표에 `Bundle ID`, `Bundle Path`, `Sandbox Path` 칸이 나옵니다 [4]. 아래는 표 모양만 보여 주려고 만든 예시이고, 번들 ID 와 UUID 는 지어낸 값입니다.

```text
Bundle ID        | Bundle Path | Sandbox Path
com.example.app  | (생략)      | .../mobile/Containers/Data/Application/2222BBBB-.../
```

앱 이름으로 Copilot 행을 찾고, `Sandbox Path` 의 UUID 폴더를 분석 대상으로 잡습니다.

**평문 대화 찾기.** 시험 기기에서 알아보기 쉬운 문장으로 대화한 뒤 추출합니다. 그 문장으로 데이터 폴더를 검색하면 대화가 담긴 파일을 좁힐 수 있습니다. 찾은 파일은 헥스 편집기로 첫 바이트부터 봅니다. `53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00`("SQLite format 3") 으로 시작하면 SQLite 파일이고, `62 70 6C 69 73 74 30 30`("bplist00") 으로 시작하면 이진 plist 입니다. 형식을 가린 뒤에는 각 형식 페이지의 방법대로 표와 칸을 읽습니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 |
|---|---|
| [계정 데이터 내보내기](export.md) | 서버에 남은 프롬프트·응답 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱이 서비스와 통신한 시간대. Copilot 앱 요청의 사용자 에이전트는 `CopilotSapphire/` 뒤에 판 번호가 붙은 모양입니다 [3] |
| [사파리](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/safari/index.html) | 같은 서비스를 브라우저로 쓴 기록 |
| [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/analysis/timeline/index.html) | 앱 설치·사용과 다른 활동을 한 시간 축에 놓기 |

## 실습

Copilot 이 들어 있는 공개 iOS 검체는 알려진 것이 없습니다. 시험용 iPhone 과 시험용 Microsoft 계정으로 검체를 만들어 풀어 봅니다.

1. `applicationState.db` 에서 Copilot 앱의 번들 ID 와 데이터 폴더 경로는 무엇으로 나오는가?
2. 대화에 쓴 문장이 데이터 폴더의 어느 파일에 평문으로 남는가? 그 파일은 SQLite 인가, plist 인가, 웹뷰 저장소인가?
3. 앱에서 대화를 지운 뒤 다시 추출하면 그 문장이 남는가? 계정 내보내기에는 남는가?
4. 로컬 백업만 받았을 때 2번의 파일이 백업 안에 들어 있는가?

## 참고 문헌

1. Microsoft Privacy Statement (Microsoft Copilot 절), 2026-09 갱신 — https://www.microsoft.com/en-us/privacy/privacystatement
2. Sonali Tyagi, Yufeng Gong, Umit Karabiyik, "Forensic analysis and privacy implications of LLM mobile apps: A case study of ChatGPT, Copilot, and Gemini", Forensic Science International: Digital Investigation, 54 (2025), 301974. https://doi.org/10.1016/j.fsidi.2025.301974 (초록)
3. plausible/analytics, `priv/ua_inspector/client.mobile_apps.yml` (Microsoft Copilot 항목) — https://github.com/plausible/analytics/blob/master/priv/ua_inspector/client.mobile_apps.yml
4. iLEAPP, `scripts/artifacts/applicationStateDB.py` (작성 Alexis Brignoni·mxkrt, 2026-08-25 갱신) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/applicationStateDB.py
5. iLEAPP, `scripts/artifacts/chatgpt.py`, `scripts/artifacts/iOSclaude.py` — https://github.com/abrignoni/iLEAPP/tree/main/scripts/artifacts
6. iLEAPP, `scripts/artifacts/appGrouplisting.py` (작성 Alexis Brignoni, 2026-07-31 갱신) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/appGrouplisting.py
