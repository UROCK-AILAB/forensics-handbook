---
title: "회사가 허용하지 않은 AI를 썼나"
parent: "시나리오 · 정보 유출"
nav_order: 930
---

# 회사가 허용하지 않은 AI를 썼나 (Shadow AI)

## 조사 질문

회사가 허용하지 않은 AI 서비스, 앱, 개발 도구, 로컬 모델을 썼는지 묻는 조사이고, 썼다면 언제부터 얼마나 자주, 개인 계정과 회사 계정 중 어느 쪽으로 썼는지까지 좁힙니다. 이런 사용을 흔히 섀도 AI (Shadow AI) 라고 부르고, 허가받지 않은 클라우드 서비스를 가리키는 섀도 IT (Shadow IT) 에서 나온 말입니다. 무엇을 입력했는지는 [기밀 자료를 AI에 넣었나](confidential-input.md) 에서 다루고, 이 페이지는 "무엇을 썼나" 와 "얼마나 썼나" 에 집중합니다.

## 먼저 확인할 것

- **허용 기준.** 회사가 허용한 AI 서비스와 계정 종류(회사 조직 계정만인지, 특정 도구만인지)를 정책 문서로 먼저 확인합니다. 기준이 없으면 "허용되지 않은 사용" 을 판단할 수 없습니다.
- **네트워크 로그의 종류와 필드.** 프록시, 방화벽, DNS, 보안 웹 게이트웨이 가운데 무엇이 있고 보존 기간이 얼마인지 확인합니다. 장비마다 남기는 필드가 달라서, 올린 데이터 양(Uploaded bytes)이 있는 로그인지에 따라 답할 수 있는 질문이 달라집니다.
- **사용자와 기기.** 어느 사용자 프로필인지, 회사 망 밖에서 쓴 기기인지 확인합니다. 회사 망을 거치지 않은 사용은 회사 프록시·방화벽 로그에 남지 않아서, 기기 흔적이나 기기에서 직접 모으는 기록(Defender for Endpoint 연동 등)으로만 볼 수 있습니다 [5].
- **시간대.** 네트워크 로그, 관리 도구 화면, 기기 설정 파일의 시각 필드마다 UTC 인지 현지 시각인지, 단위가 무엇인지 확인하고 맞춥니다. 이 페이지에서 다루는 기기 파일의 시각 값은 시간대와 단위를 설명한 공개 자료가 없어 실제 데이터로 확인해야 합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 프록시·DNS·방화벽 로그와 클라우드 앱 발견 보고서 | 어느 AI 도메인에 누가 언제 접속했는지, 올린 양 | [AI 서비스 도메인과 네트워크 기록](../../02-artifacts/network-enterprise/network-traces.md) |
| 2 | 데이터 보안 관리 도구의 AI 사이트 방문 기록 | 브라우저로 AI 사이트에 간 사용자와 시각, 차단·재정의 여부 | [보안 제품이 남기는 AI 사용 기록](../../02-artifacts/network-enterprise/dlp-casb.md) |
| 3 | 기기의 AI 도구 폴더 | 설치·설정된 적이 있는 도구 | [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) |
| 4 | 사용 통계·설정 파일 | 처음 쓴 날, 날짜별 사용량, 모델별 토큰 수 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md), [Claude](../../02-artifacts/chat-services/claude/index.md) |
| 5 | 계정·요금제 단서 | 개인 계정인지 회사 조직 계정인지 | [그 대화를 한 사람이 누구인가](../attribution/user-attribution.md) |
| 6 | 개발 도구의 훅 설정 | 프롬프트 제출 전후에 도는 명령(회사 감시 훅인지, 사용자가 넣은 것인지) | [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md) |
| 7 | 로컬 AI 폴더와 포트 | 인터넷 없이 쓴 AI | [Ollama](../../02-artifacts/local-ai/ollama.md), [로컬 모델 파일](../../02-artifacts/local-ai/model-files.md) |

네트워크 쪽을 먼저 보는 이유는 조직 전체에서 대상 사용자와 기간을 좁힐 수 있기 때문이고, 기기 쪽은 좁힌 사용자의 도구·계정·사용량을 확인하는 데 씁니다.

## 네트워크와 관리 도구에서 찾기

**클라우드 앱 발견.** Microsoft Defender for Cloud Apps 의 클라우드 발견(Cloud discovery)은 트래픽 로그를 31,000개가 넘는 클라우드 앱 카탈로그와 대조하고 90개가 넘는 위험 요소로 점수를 매기며, 문서도 목적을 "Shadow IT" 로 설명합니다 [5]. 카탈로그에 없는 앱은 기본 설정으로 찾지 못하고, 발견 데이터는 하루 네 번 분석해 갱신합니다 [5]. 보고서는 방화벽·프록시 로그를 손으로 올리는 Snapshot 과, Defender for Endpoint 연동·로그 수집기(Syslog/FTP)·보안 웹 게이트웨이 연동으로 계속 받는 Continuous 두 가지입니다 [5]. 로그 원천마다 들어오는 필드가 달라서 Target App URL, Target App IP, Username, Origin IP, Total traffic, Uploaded bytes 가 모두 오는 장비(예: Zscaler)도 있고 URL, Username, Origin IP 만 오는 장비(예: Squid Native)도 있습니다 [5]. Uploaded bytes 가 있는 로그라면 AI 사이트로 올린 양을 추정할 수 있습니다. 생성형 AI 앱만 카테고리로 거를 수 있는지는 쓰고 있는 콘솔의 카테고리 목록에서 확인합니다.

**AI 사이트 목록과 대조.** Microsoft Purview 는 자기가 "생성형 AI 사이트" 로 보는 도메인 목록을 공개하고, 이 목록은 계속 늘어난다고 적혀 있습니다 [2]. 프록시·DNS 로그를 이 목록과 대조하면 도메인 기준으로 1차 선별을 할 수 있습니다. 목록 일부는 다음과 같습니다 [2].

```
*.chatgpt.com  *.openai.com  *.chat.com
*.claude.ai  *.anthropic.com
*.gemini.google.com  *.bard.google.com  *.notebooklm.cloud.google.com
*.copilot.microsoft.com  *.bing.com/chat
*.perplexity.ai  *.deepseek.com  *.grok.com  *.meta.ai  *.poe.com
*.character.ai  *.cursor.com  *.ollama.ai  *.qwen.ai  *.doubao.com
*.yiyan.baidu.com  *.huggingface.co/spaces/...(일부 경로)
```

목록에는 `*.chatgpt4online.org` 처럼 이름이 비슷한 제3자 사이트도 들어 있어서 [2], 공식 서비스와 이름을 흉내 낸 사이트를 나눠 적어야 합니다. 서비스별 도메인과 SNI 해석은 [AI 서비스 도메인과 네트워크 기록](../../02-artifacts/network-enterprise/network-traces.md) 에서 다룹니다.

**AI 사이트 방문 기록.** Purview 의 AI 용 데이터 보안 관리(DSPM for AI)에는 브라우저로 AI 사이트에 간 것을 탐지하는 기본 내부자 위험 정책 `DSPM for AI - Detect when users visit AI sites` 가 있고, 활동 탐색기에는 `AI website visit` 이벤트가 남습니다 [1]. 제3자 AI 사이트 방문을 찾으려면 Windows 사용자에게 Purview 브라우저 확장을 배포해야 하고, Chrome 에서 Endpoint DLP 를 쓸 때도 이 확장이 필요하며, Edge 는 Edge 구성 정책으로 연동을 켭니다 [1]. 확장이 배포되지 않은 브라우저의 방문은 이 기록에 없습니다. 기본 DLP 정책에는 `DSPM for AI - Block sensitive info from AI sites`(적응형 보호, 테스트 모드)와 `DSPM for AI - Block elevated risk users from submitting prompts to AI apps in Microsoft Edge` 등이 있고 [1], 차단 기록이나 재정의(override) 기록이 있으면 사용자가 경고를 보고도 진행했는지를 보여 주는 단서가 됩니다.

**클라우드 사업자를 거친 사용.** Claude Code 를 Bedrock, Google Agent Platform, Microsoft Foundry, Claude Platform on AWS 로 쓰면 사용 지표, 오류 보고, `/feedback` 이 기본으로 꺼집니다 [3]. 이때 모델 요청은 Anthropic 도메인이 아니라 클라우드 사업자 도메인으로 가므로, AI 회사 도메인만 찾으면 이 사용을 놓칩니다. 다만 WebFetch 도구는 공급자와 상관없이 가져올 URL 의 호스트 이름만 `api.anthropic.com` 에 보내 Anthropic 의 차단 목록과 대조합니다 [3]. Claude Code 의 사용 지표는 Anthropic 과 제3자 로깅 인프라로, 오류 보고는 제3자 오류 추적 서비스로 가고, 지표에는 코드·프롬프트·파일 경로가 들어가지 않습니다 [3]. 오류 보고는 Pro·Max 구독으로 로그인해 Claude API 에 바로 연결한 v2.1.198 이후 판에서만 기본으로 켜지므로 [3], 오류 보고 전송이 없다는 것만으로는 사용 여부를 판별하지 못합니다. `DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 값이 켜진 환경에서는 이 전송이 줄어들어 네트워크 쪽 흔적도 적습니다 [3]. 텔레메트리를 받는 호스트 이름은 공개 문서에 없어 실제 네트워크 기록에서 확인해야 합니다.

## 기기에서 찾기

**설치 흔적 폴더(Windows).** 아래 폴더가 있으면 그 도구가 설치됐거나 설정된 적이 있다고 말할 수 있습니다. 폴더가 있다는 사실만으로 "썼다" 까지는 말하지 않습니다.

| 폴더 | 도구 | 관찰한 내용 |
|---|---|---|
| `%USERPROFILE%\.claude` | Claude Code | 세션 기록, 입력 이력, 사용 통계, 자격 증명 파일 |
| `%USERPROFILE%\.cursor` | Cursor | `hooks.json` 하나뿐이었고 Cursor 앱 데이터 폴더는 없었음 |
| `%USERPROFILE%\.codex` | Codex CLI | `hooks.json`, 스킬 폴더 |
| `%USERPROFILE%\.gemini` | Gemini CLI | `antigravity\installation_id`, `antigravity\crashes\파일.log`, `config\projects\파일.json`(`id`, `name`, `updatedAt`) |
| `%USERPROFILE%\.ollama` | Ollama | `id_ed25519`, `id_ed25519.pub`, `cache\파일.json`(`recommendations[].model` 등) |
| `%LOCALAPPDATA%\Packages\` 아래 Claude 패키지 폴더 | Claude 데스크톱(스토어 앱) | `LocalCache\Roaming\Claude\` 아래 `Local Storage\leveldb`, `IndexedDB`, `Network\Cookies`, `Cache`, `Code Cache`, `Local State` |

`.cursor` 처럼 설정 파일 하나만 있는 폴더는 앱을 깔아 쓴 흔적이라기보다 훅이나 설정만 둔 흔적일 수 있으므로, 앱 데이터 폴더가 따로 있는지 함께 봅니다. 스토어 앱 폴더의 Electron 저장소 원리는 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md) 와 다른 판의 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html) 를 봅니다.

**사용 시기와 규모.** Claude Code 의 `stats-cache.json` 에는 날짜별 사용량과 모델별 토큰 수가 모여 있습니다.

| 키 | 알려 주는 것 |
|---|---|
| `firstSessionDate` | 처음 세션을 연 날 |
| `dailyActivity[].date / messageCount / sessionCount / toolCallCount` | 날짜별 메시지·세션·도구 호출 수 |
| `dailyModelTokens[].date`, `dailyModelTokens[].tokensByModel` | 날짜별·모델별 토큰 수 |
| `hourCounts` | 시간대별 사용 횟수 |
| `longestSession.*` | 가장 길었던 세션의 길이·메시지 수·시각 |
| `modelUsage.모델.inputTokens / outputTokens` | 모델별 입력·출력 토큰 합계 |
| `totalMessages`, `totalSessions` | 전체 메시지·세션 수 |

아래는 키 모양을 보여 주려고 만든 예시이고 값은 모두 가짜입니다. 실제 날짜 표기 형식은 실제 파일에서 확인합니다.

```json
{"firstSessionDate":"2026-01-05","dailyActivity":[{"date":"2026-03-02","messageCount":42,"sessionCount":3,"toolCallCount":17}],"totalMessages":1200,"totalSessions":85}
```

이 파일은 합계만 담고 내용은 담지 않아서 "허용되지 않은 도구를 이 기간에 이만큼 썼다" 를 밝히는 데 쓰고, 무엇을 넣었는지는 세션 기록으로 넘깁니다. `hourCounts` 의 시간이 UTC 인지 현지 시각인지는 공개된 설명이 없으므로 근무 시간 밖 사용을 주장할 때는 세션 기록의 `timestamp` 로 다시 맞춥니다.

**계정 종류 단서.** 회사 조직 계정인지 개인 계정인지는 다음 키로 좁힙니다.

| 파일 | 키 | 알려 주는 것 |
|---|---|---|
| `.claude\.credentials.json` | `claudeAiOauth.subscriptionType`, `claudeAiOauth.rateLimitTier`, `claudeAiOauth.scopes`, `claudeAiOauth.expiresAt` | 키 이름으로 보면 로그인한 계정의 요금제 종류와 권한 범위(값의 뜻은 공개 설명이 없어 회사 계약 요금제와 대조해 확인) |
| Claude 데스크톱 `config.json` | `lastKnownAccountUuid`, `first_launch_at`, `version_first_launch.at / version`, `updaterLastSeenVersion` | 마지막 계정 ID, 처음 실행한 시각과 그때의 버전 |
| Claude 데스크톱 `plan-usage-history.json` | `samples[].org`, `samples[].t` | 사용량을 기록한 조직과 시각 |
| Claude 데스크톱 `buddy-tokens.json` | `tokens-today.date`, `tokens-today.tokens` | 그날 쓴 토큰 수 |
| Claude 데스크톱 `claude_desktop_config.json` | `preferences.localAgentModeTrustedFolders`, `coworkUserFilesPath`, `preferences.coworkWebSearchEnabled` | 에이전트가 다룰 수 있게 허용한 폴더, 웹 검색 사용 설정 |

`.credentials.json` 에는 `accessToken` 과 `refreshToken` 필드도 있어서 증거로 옮길 때는 비밀번호처럼 다룹니다. 토큰 취급은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) 에 있고, 계정 ID 를 실제 사람과 잇는 방법은 [그 대화를 한 사람이 누구인가](../attribution/user-attribution.md) 에 있습니다. `first_launch_at` 같은 정수 시각은 단위가 공개돼 있지 않아, 파일 수정 시각과 맞춰 보고 초인지 밀리초인지 정합니다.

**개발 도구의 훅 설정.** 개발 도구는 프롬프트를 보내기 전이나 도구를 실행하기 전후에 정해 둔 명령을 돌리는 훅을 설정 파일에 둡니다. 관찰한 이벤트 이름은 다음과 같습니다.

| 도구 | 파일 | 훅 이벤트 |
|---|---|---|
| Cursor | `hooks.json` | `beforeSubmitPrompt`, `beforeShellExecution`, `beforeMCPExecution`, `afterAgentResponse`, `preToolUse`, `postToolUse`, `stop`(각각 `command`, `timeout`) |
| Codex CLI | `hooks.json` | `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PermissionRequest`, `Stop` |
| Gemini CLI | `settings.json` | `BeforeAgent`, `AfterAgent`, `BeforeTool`, `AfterTool` |
| Claude Code | `settings.json` | `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `SessionEnd`, `SubagentStart` 등 |

프롬프트 제출 전에 도는 훅이 있으면 `command` 에 적힌 경로를 따라가 회사가 넣은 감시 훅인지 사용자가 넣은 것인지 구분하고, 훅이 따로 남긴 로그가 있는지도 찾습니다. 훅이 로그를 남기는지는 훅 명령마다 다르므로 `command` 가 가리키는 스크립트를 읽어 확인합니다. 각 도구의 설정 파일은 [Cursor](../../02-artifacts/dev-agents/cursor.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md) 페이지에서 다룹니다.

**로컬 AI.** Ollama 서버는 기본으로 `127.0.0.1:11434` 에서 듣고 `OLLAMA_HOST` 로 주소를 바꿉니다 [4]. 라이브 조사에서 이 포트가 열려 있으면 로컬 AI 를 쓰고 있다는 단서가 되지만, 주소를 바꾼 환경도 있으므로 `OLLAMA_HOST` 값도 함께 봅니다. 모델 위치는 Windows `C:\Users\%username%\.ollama\models`, macOS `~/.ollama/models`, Linux `/usr/share/ollama/.ollama/models` 입니다 [4]. 로컬 AI 는 회사 망에 AI 도메인 접속을 남기지 않을 수 있어서 네트워크 쪽 선별로는 보이지 않을 수 있고, 그럴 때는 기기 폴더와 모델 위치로 찾습니다. 모델 파일 형식은 [로컬 모델 파일](../../02-artifacts/local-ai/model-files.md) 을 봅니다.

**다른 OS.** 이 페이지가 macOS·Linux 에 대해 다루는 것은 위 Ollama 모델 위치뿐입니다. macOS 의 AI 앱 저장 위치와 Android·iOS 앱의 흔적은 각 서비스 페이지를 보고, 앱 설치·실행 흔적의 일반 원리는 다른 판의 [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/fsevents/index.html), [Android 앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html) 를 봅니다.

## 분석 흐름

1. 회사가 허용한 AI 목록과 계정 종류를 정책 문서로 확정하고, 조사 기간을 정합니다.
2. 프록시·DNS 로그를 AI 사이트 목록과 대조해 도메인 기준으로 1차 선별하고, 클라우드 앱 발견 보고서가 있으면 사용자·기간·올린 양을 뽑습니다. 이름을 흉내 낸 사이트는 따로 분류합니다.
3. 데이터 보안 관리 도구에서 `AI website visit` 과 차단·재정의 기록을 보고, 브라우저 확장이 배포된 브라우저였는지 확인합니다.
4. 좁힌 사용자의 기기에서 AI 도구 폴더를 모으고, 설치 흔적만 있는 도구와 사용 기록이 있는 도구를 나눕니다. 수집 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) 를 따릅니다.
5. 사용 통계로 처음 쓴 날과 기간별 사용량을 정리하고, 계정·요금제 단서로 개인 계정 사용인지 회사 조직 계정 사용인지 확인합니다.
6. 훅 설정과 클라우드 사업자 경유 여부, 로컬 AI 사용 여부를 확인해 네트워크 쪽 선별에서 빠진 사용을 채웁니다.
7. 네트워크 접속 시각과 기기 기록을 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) 으로 묶고, 입력 내용까지 봐야 하면 [기밀 자료를 AI에 넣었나](confidential-input.md) 로 넘어갑니다.

## 흔한 오판

**"AI 도구 폴더가 있으니 썼다."** 폴더는 설치나 설정이 있었다는 것까지만 보여 줍니다. `.cursor` 에 훅 설정 파일 하나만 있고 앱 데이터 폴더가 없던 경우처럼, 폴더가 있어도 사용 기록이 없을 수 있습니다.

**"네트워크 로그에 AI 도메인이 없으니 쓰지 않았다."** 클라우드 앱 발견은 카탈로그에 없는 앱을 기본으로 찾지 못하고 [5], 클라우드 사업자를 거친 사용은 모델 요청이 클라우드 사업자 주소로 가고 사용 지표도 기본으로 꺼지며 [3], 로컬 AI 와 회사 망 밖 사용은 회사 네트워크에 남지 않을 수 있습니다.

**"AI 사이트 목록에 있는 도메인에 접속했으니 그 회사 서비스를 썼다."** 목록에는 이름이 비슷한 제3자 사이트도 있습니다 [2]. 공식 서비스인지 도메인을 하나씩 확인합니다.

**"방문 기록이 없으니 브라우저로 쓰지 않았다."** 제3자 AI 사이트 방문은 Purview 브라우저 확장이 배포된 경우에만 잡히고, Chrome 도 이 확장이 있어야 합니다 [1].

**"텔레메트리 전송이 없으니 도구를 쓰지 않았다."** 텔레메트리를 끄는 설정이 켜진 환경에서는 전송이 줄어듭니다 [3]. 전송이 없는 것과 사용하지 않은 것은 다른 이야기입니다.

## 보고서 문장 예

보고서에는 기록으로 확인되는 만큼만 씁니다. 아래 예시의 날짜·계정·수치는 만든 값입니다.

| 피할 문장 | 쓸 문장 |
|---|---|
| 사용자가 허가 없이 AI 를 상습적으로 썼다. | 2026-01-05 부터 2026-03-31 까지 프록시 로그에 user-b 계정의 AI 사이트 목록 도메인 접속이 58일에 걸쳐 있다. 이 로그에는 올린 데이터 양 필드가 없다. |
| 사용자가 개인 계정으로 회사 코드를 AI 에 넣었다. | 조사 대상 기기의 개발 도구 자격 증명 파일에 적힌 요금제 종류는 회사가 계약한 조직 요금제와 다르다. 이 파일은 로그인한 계정의 종류를 보여 줄 뿐 입력 내용을 담지 않는다. |
| 사용자가 로컬 AI 를 썼다. | 조사 대상 기기의 사용자 폴더에 Ollama 폴더와 모델 폴더가 있다. 이 흔적은 설치와 모델 내려받기를 보여 주고, 대화 내용이나 사용 시각은 이 흔적만으로 알 수 없다. |

보고서 전체 틀은 [AI 관련 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 를 봅니다.

## 함께 볼 페이지

- [기밀 자료를 AI에 넣었나](confidential-input.md) — 무엇을 입력했는지 찾는 조사
- [그 대화를 한 사람이 누구인가](../attribution/user-attribution.md) — 계정과 실제 사용자를 잇는 방법
- [에이전트가 자격 증명을 건드렸나](../agents/agent-credentials.md) — 개발 도구에 남은 토큰과 권한
- [브라우저에 들어간 AI](../../02-artifacts/office-integrations/browser-builtin-ai.md) — 따로 설치하지 않아도 쓰게 되는 AI 기능
- [그 밖의 서비스](../../02-artifacts/chat-services/other-services.md)
- [조사 절차](../../03-techniques/acquisition/investigation-process.md)

## 참고 문헌

1. Considerations for deploying Microsoft Purview Data Security Posture Management (DSPM) for AI | Microsoft Learn — https://learn.microsoft.com/en-us/purview/dspm-for-ai-considerations
2. Supported AI sites by Microsoft Purview for data security and compliance protections | Microsoft Learn — https://learn.microsoft.com/en-us/purview/ai-microsoft-purview-supported-sites
3. Data usage | Claude Code Docs — https://code.claude.com/docs/en/data-usage
4. FAQ | Ollama — https://docs.ollama.com/faq
5. Cloud app discovery overview - Microsoft Defender for Cloud Apps | Microsoft Learn — https://learn.microsoft.com/en-us/defender-cloud-apps/set-up-cloud-discovery
