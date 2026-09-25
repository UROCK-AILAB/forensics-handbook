---
title: "AI로 피싱·사기 문구를 만들었나"
parent: "시나리오 · 악용"
nav_order: 850
---

# AI로 피싱·사기 문구를 만들었나 (Phishing)

확인 날짜는 2026-09이고, 기기에서 직접 본 내용은 Windows 11 한 대에 한정됩니다. AI 앱은 자주 바뀌어서 아래 경로와 키 이름은 이 날짜를 기준으로 읽어야 합니다. 관찰 메모에는 앱 버전 값을 적지 않아서 이 쪽도 버전을 적지 않습니다.

## 조사 질문

피싱 메일·사기 문자·가짜 안내문을 용의자가 AI 서비스로 만들었는지 묻는 조사입니다. 질문은 두 방향으로 나뉩니다. 용의자 쪽에서는 그 문구를 만든 AI 대화 기록이 기기나 계정에 남았는지를 보고, 피해 쪽에서는 받은 메일과 첨부에 AI 를 쓴 흔적이 보이는지를 봅니다.

MITRE ATT&CK 는 공격자가 생성형 AI 도구를 손에 넣어 쓰는 행위를 T1588.007 인공지능 (Artificial Intelligence)으로 분류합니다. 상위 기법은 T1588 능력 확보 (Obtain Capabilities)이고 전술은 자원 개발 (Resource Development, TA0042), 플랫폼은 PRE 입니다. 설명에는 여러 언어로 피싱 문구를 자동으로 만들고, 악성 스크립트를 난독화하고, 사기·사칭용 합성 미디어를 만드는 쓰임이 적혀 있습니다. 이 항목은 2024-03-11 에 생겼고 2026-05-12 에 고친 1.1 판이 최신입니다.

ATT&CK 는 이 행위가 조직의 방어 범위 밖에서 일어나서 예방 통제로 쉽게 막을 수 없고, 대상 조직이 볼 수 없는 곳에서 일어나 탐지도 어렵다고 적었습니다. 그래서 탐지는 생성형 AI 를 쓴 결과로 나타나는 피싱 (Phishing)과 정보 수집용 피싱 (Phishing for Information)에 맞추라고 권합니다. 이 핸드북은 이를 바탕으로 증거를 세 갈래로 나눕니다. 용의자 기기의 AI 앱·도구 기록, 수사 요청으로만 받을 수 있는 서비스 회사 서버 기록, 메일·첨부 같은 결과물에 남은 특징입니다.

위협 보고서에 나온 사례는 이 조사가 무엇을 찾아야 하는지 보여 줍니다. Google 위협 인텔리전스 그룹(GTIG)은 2025-11-06 보고서에서 이란 정부와 연계된 APT42 가 싱크탱크 직원을 사칭하는 피싱 자료를 만들고 전문 용어를 번역하는 데 Gemini 를 썼다고 밝혔습니다. 같은 보고서에는 북한 UNC1069 가 스페인어 사회공학 미끼 문구와 업무 핑계 문구, 자격 증명을 노린 가짜 소프트웨어 업데이트 안내문을 만든 사례가 있고, Google 은 두 행위자의 계정을 막았습니다. 보고서는 2025년 지하 시장에 광고된 주요 AI 도구가 거의 모두 피싱 지원 기능을 내세웠다고도 적었습니다. ATT&CK 의 절차 예에는 ShinyHunters(G1057)가 음성 피싱에 Bland AI 를 쓴 사례와 Contagious Interview(G1052)가 캠페인용 이미지·콘텐츠를 AI 로 만든 사례가 올라 있습니다. Anthropic 은 2025-08-27 보고서에서 북한 원격 근무자가 AI 로 기술 면접을 통과하고 업무를 이어 간 위장 취업 사례를 밝혔고, 같은 보고서 목록에 연애 사기 사례도 있지만 이 핸드북은 그 세부를 확인하지 못했습니다.

## 먼저 확인할 것

용의자가 어떤 경로로 AI 를 썼는지에 따라 대화 원본이 있는 곳이 달라집니다. ChatGPT·Gemini·Claude 같은 웹 서비스를 브라우저로 썼다면 대화 원본은 서비스 회사 서버에만 있고, 기기에는 브라우저 기록·캐시·쿠키 정도만 남습니다. 서버 기록은 서비스 회사에 수사 요청을 보내야 받을 수 있고, 서비스별 서버 보관 기간과 제공 절차는 이 쪽에서 확인하지 못했습니다. 데스크톱 앱이나 개발 도구를 썼다면 기기에 기록이 더 남을 수 있고, Ollama 같은 로컬 AI 를 썼다면 서버 기록이 아예 없습니다.

수집을 시작하기 전에 OS 판과 시간대, 조사할 사용자 계정, 수집 범위(기기 이미지만인지, 계정 내보내기나 서버 기록 요청까지인지)를 정해 둡니다. 시간대는 AI 대화 시각과 메일 발송 시각을 맞춰 볼 때 필요합니다.

OS 마다 앱 데이터를 보호하는 방식이 다르고, 이 쪽에서 직접 본 것은 Windows 11 뿐입니다. 다른 OS 에서는 아래 공통 원리 쪽을 먼저 읽고 앱 폴더를 찾습니다.

| OS | 이 쪽에서 확인한 범위 | 공통 원리 |
|---|---|---|
| Windows | 사용자 폴더의 AI 도구 폴더와 Claude 데스크톱(스토어 앱) 폴더를 봤습니다 (확인 범위: Windows 11, 2026-09) | [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html), [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html) |
| macOS | 확인하지 못했습니다 | [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html), [LevelDB와 IndexedDB](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/leveldb-indexeddb.html) |
| Android | 확인하지 못했습니다 | [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html), [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html) |
| iOS | 확인하지 못했습니다 | [데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html), [iOS 키체인](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/keychain.html) |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 피해 쪽이 받은 메일·첨부 | 보낸 계정, 받는 사람 구성, 첨부 형식, AI 가 만든 코드로 의심되는 표시 | [AI가 만든 글·이미지 판별의 한계](../../03-techniques/analysis/detection-limits.md) |
| 2 | 용의자 브라우저 기록·캐시·쿠키 | AI 웹 서비스에 접속한 시각과 계정 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html), [AI 서비스 도메인과 네트워크 기록](../../02-artifacts/network-enterprise/network-traces.md) |
| 3 | AI 데스크톱 앱 폴더 | 앱을 쓴 흔적, 쿠키 DB | [Claude](../../02-artifacts/chat-services/claude/index.md), [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md) |
| 4 | AI 개발 도구 기록 | 입력한 프롬프트와 그 시각 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 5 | 메일 클라이언트 보낸편지함, 첨부 파일의 작성 시각 | AI 대화 뒤에 실제로 보냈는지 | [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) |
| 6 | 서비스 회사 서버 기록 | 대화 원본, 계정 차단 기록 | [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) |

### 피해 쪽 결과물에 남는 특징

Microsoft 위협 인텔리전스는 2025-09-24 블로그에서 SVG 첨부 안의 페이로드를 AI 가 만든 코드로 난독화한 피싱 캠페인을 탐지했다고 밝혔습니다. 미국 조직을 노린 캠페인이었고, 공격자는 탈취한 소규모 기업 메일 계정에서 받는 사람을 자기 자신으로 두고 실제 대상은 숨은 참조(BCC)에 넣어 보냈습니다. 첨부 이름은 "23mb – PDF- 6 pages.svg" 처럼 PDF 로 보이게 지었지만 확장자는 `.svg` 였고, SVG 는 텍스트 형식이라 안에 스크립트를 넣을 수 있습니다.

Microsoft 는 이 코드에서 LLM 이 만든 코드로 볼 만한 표시 다섯 가지를 들었습니다.

| 표시 | 보고서의 예 |
|---|---|
| 영어 설명 단어에 무작위 16진수를 붙인 지나치게 긴 이름 | `processBusinessMetricsf43e08` |
| 필요 이상으로 잘게 나눈 모듈 구조 | — |
| 격식을 차린 일반적인 주석 | "Advanced business intelligence data processor" |
| 틀에 박힌 방식의 난독화 | — |
| 문서를 흉내 낸 듯한 CDATA·XML 선언 | — |

그런데 실제 차단은 이 표시가 아니라 기존 신호로 이뤄졌습니다. 자기 앞으로 보내고 BCC 를 쓴 발송 방식, PDF 로 꾸민 SVG, 이미 알려진 피싱 도메인으로 넘어가는 동작, 난독화 자체, 세션 추적과 브라우저 지문 수집이 그 신호입니다. Microsoft 는 AI 가 만든 코드가 더 복잡할 수는 있어도 사람이 만든 공격과 같은 행위·기반 시설의 틀 안에서 움직인다고 결론을 냈고, Safe Links, 0시간 자동 제거(Zero-Hour Auto Purge, ZAP), 피싱에 강한 인증, SmartScreen, 조건부 액세스의 인증 강도 설정을 권했습니다. 다섯 표시는 의심할 근거일 뿐 AI 가 만들었다는 증명이 아니고, 문장만 보고 AI 작성 여부를 가리는 도구의 신뢰도는 이 쪽에서 확인하지 못했습니다.

### 용의자 기기에 남는 것

웹 서비스로 문구를 만들었다면 기기에서 찾을 수 있는 것은 접속 흔적까지입니다. 서비스별로 계정 데이터를 내보내는 형식과 서버 보관 설정은 [ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md), [Gemini](../../02-artifacts/chat-services/gemini/index.md), [Claude](../../02-artifacts/chat-services/claude/index.md) 쪽에 있습니다.

Claude 데스크톱(스토어 앱)은 `%USERPROFILE%\Packages\` 아래 Claude 패키지 폴더의 `LocalCache\Roaming\Claude\` 에 `IndexedDB`, `Local Storage\leveldb`, `Cache`, `Network\Cookies` 같은 Electron 형 폴더를 둡니다 (확인 범위: Windows 11, 2026-09). 파티션 쿠키 DB `Partitions\cowork-file-preview\Network\Cookies` 에는 `cookies` 표(칸 `creation_utc`, `host_key`, `name`, `value`, `encrypted_value`, `path`, `expires_utc`, `last_access_utc`, `last_update_utc` 등)와 `meta` 표(`key`, `value`)가 있어 Chromium 쿠키 DB 와 모양이 같습니다 (확인 범위: Windows 11, 2026-09). 기본 `Network\Cookies` 는 앱이 잠그고 있어 열지 못했고, 대화 내용이 이 폴더에 로컬로 남는지도 열어 보지 않아 확인하지 못했습니다.

Claude Code 로 문구를 만들었다면 `%USERPROFILE%\.claude\history.jsonl` 의 `display` 칸과 세션 파일 `projects\` 아래 `.jsonl` 의 `message.content[].text` 칸에 입력과 응답이 남는 모양입니다 (확인 범위: Windows 11, 2026-09). 실제 값은 보지 않았습니다. 시각은 `history.jsonl` 의 `timestamp` 가 정수, 세션 파일의 `timestamp` 가 문자열로 들어 있고, 두 칸이 에포크 밀리초인지 ISO 8601 인지는 값을 보지 않아 확인하지 못했습니다. 키 전체의 뜻과 보관 기간은 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) 쪽에 있습니다.

같은 PC 에서 Codex CLI(`%USERPROFILE%\.codex`), Gemini CLI(`%USERPROFILE%\.gemini`), Ollama(`%USERPROFILE%\.ollama`) 폴더에는 대화 기록 파일이 없었습니다 (확인 범위: Windows 11, 2026-09). 이 PC 에서 그랬다는 뜻이지 이 도구들이 기록을 전혀 남기지 않는다는 뜻은 아니고, 도구별 내용은 [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md), [Ollama](../../02-artifacts/local-ai/ollama.md) 쪽에서 봅니다.

음성 피싱에 쓰는 음성 합성 서비스가 기기에 남기는 흔적은 확인하지 못했습니다.

## 분석 흐름

1. 피해 쪽 메일을 원본 그대로 확보하고 헤더·발송 계정·받는 사람 구성·첨부 형식을 기록합니다. AI 흔적보다 먼저 기존 피싱 신호를 정리합니다.
2. 첨부 안의 스크립트에서 AI 생성 코드로 의심되는 표시를 찾되, 찾은 표시는 "의심 근거" 로만 적습니다.
3. 용의자 기기에서 브라우저 기록·쿠키로 AI 웹 서비스에 접속한 시각과 계정을 찾습니다.
4. AI 데스크톱 앱·개발 도구·로컬 AI 폴더를 확인하고, 대화 기록이 로컬에 있으면 피싱 문구와 같거나 비슷한 입력·응답을 찾습니다.
5. AI 대화 시각, 첨부 파일 작성 시각, 메일 발송 시각을 한 타임라인에 놓고 순서를 봅니다. 시각 칸마다 UTC 인지 현지 시각인지 먼저 정합니다.
6. 기기에 대화 원본이 없고 웹 서비스 사용만 확인되면 서비스 회사에 서버 기록을 요청합니다.

## 흔한 오판

긴 16진수 붙은 이름이나 격식 있는 주석이 보인다고 AI 가 만들었다고 판정하는 일이 가장 흔합니다. Microsoft 사례에서도 그런 표시는 의심 근거였고 차단은 기존 신호로 이뤄졌습니다.

용의자 기기에 AI 대화 기록이 없다고 AI 를 쓰지 않았다고 결론 내리는 것도 잘못입니다. 웹 서비스로 썼다면 대화 원본은 처음부터 서버에만 있습니다.

AI 서비스 접속 기록과 피싱 메일 발송이 같은 날이라는 사실만으로 그 대화에서 문구를 만들었다고 쓰지 않습니다. 대화 내용이나 서버 기록으로 문구가 이어져야 합니다.

## 보고서 문장 예

아래 문장은 형식을 보여 주려고 만든 예시이고, 시각과 이름은 가짜입니다.

> 용의자 계정 "sample_user" 의 브라우저 기록에 2026-03-02 09:14(UTC+9)부터 09:52 사이 생성형 AI 웹 서비스 접속 기록이 있습니다. 같은 날 10:05(UTC+9)에 보낸 문제의 메일이 보낸편지함에 있습니다. 대화 원본은 기기에 없어 문구를 AI 로 만들었는지는 이 자료로 판단할 수 없습니다.

> 첨부 스크립트에서 설명형 영어 단어와 16진수를 붙인 함수 이름, 일반적인 주석이 확인됩니다. 이 특징은 AI 생성 코드에서 보고된 적이 있지만 AI 가 만들었다는 증명은 아닙니다.

## 함께 볼 페이지

- [AI로 악성 코드를 만들었나](malware-development.md)
- [딥페이크·합성 이미지를 만들었나](deepfake.md)
- [이 글·이미지는 AI가 만들었나](../attribution/ai-generated.md)
- [그 대화를 한 사람이 누구인가](../attribution/user-attribution.md)
- [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)
- [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)
- [AI 관련 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)

## 참고 문헌

1. Microsoft Security Blog, "AI vs. AI: Detecting an AI-obfuscated phishing campaign" (2025-09-24) — https://www.microsoft.com/en-us/security/blog/2025/09/24/ai-vs-ai-detecting-an-ai-obfuscated-phishing-campaign/
2. Google Cloud Blog(GTIG), "GTIG AI Threat Tracker: Advances in Threat Actor Usage of AI Tools" (2025-11-06) — https://cloud.google.com/blog/topics/threat-intelligence/threat-actor-usage-of-ai-tools
3. Anthropic, "Detecting and countering misuse of AI: August 2025" (2025-08-27) — https://www.anthropic.com/news/detecting-countering-misuse-aug-2025
4. MITRE ATT&CK, T1588.007 Obtain Capabilities: Artificial Intelligence (v1.1, 수정 2026-05-12) — https://attack.mitre.org/techniques/T1588/007/
