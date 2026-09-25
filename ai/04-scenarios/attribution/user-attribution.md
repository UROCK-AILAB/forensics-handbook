---
title: "그 대화를 한 사람이 누구인가"
parent: "시나리오 · 사용자와 출처"
nav_order: 900
---

# 그 대화를 한 사람이 누구인가 (User Attribution)

## 조사 질문

AI 서비스에 남은 대화 하나를 두고 "이 대화를 누가 했는가" 를 묻는 조사입니다. 기기에 남은 흔적으로는 보통 어느 기기의 어느 OS 계정에서, 어느 서비스 계정으로 대화가 오갔는지까지 좁힐 수 있고, 그 계정 앞에 실제로 누가 앉아 있었는지는 로그온 기록 같은 다른 흔적과 맞춰 봐야 정할 수 있습니다. 요즘은 AI 에이전트가 사람 대신 입력을 만들기도 해서, 사람이 친 입력과 자동으로 생긴 입력을 가르는 일도 이 질문에 들어갑니다.

이 글의 경로와 키 이름은 Claude Code 공식 문서(2026-09-25 확인)와 Windows 11 PC 한 대를 관찰한 결과(2026-09)에서 가져왔습니다. 관찰로 알아낸 내용에는 "(확인 범위: Windows 11, 2026-09)" 를 붙였고, 관찰할 때 앱 버전 번호는 적어 두지 않았습니다. AI 앱은 자주 바뀌므로 실제 사건에서는 기록 안에 남은 버전 값(`version`, `cliVersion` 등)부터 확인하고 이 글과 다르면 그 버전 기준으로 다시 봅니다.

## 먼저 확인할 것

**대화 원본이 어디에 있는가.** 서비스와 실행 방식에 따라 대화 원본이 기기에 있기도 하고 서버에만 있기도 합니다. 기기에 없는 대화를 기기에서 찾느라 시간을 쓰지 않도록, 조사를 시작할 때 아래 표로 먼저 가릅니다.

| 사용 환경 | 대화 원본 | 기기에 남는 것 |
|---|---|---|
| 웹 브라우저로 쓴 ChatGPT·Claude·Gemini 등 | 서비스 서버에만 있고, 계정의 데이터 내보내기나 사업자 요청으로 받습니다 | 브라우저 방문 기록·쿠키 같은 접속 흔적 |
| Claude Code(PC 에서 실행) | 사용자 PC 의 `~/.claude/projects/` 아래에 평문으로 저장하고, 프롬프트와 응답은 서버로도 보냅니다 | 대화 전문, 입력 기록, 수정 전 파일 사본 |
| Claude Code 클라우드 세션(웹) | Anthropic 가상 머신에서 돌아서 사용자 PC 에는 대화 파일이 생기지 않습니다 | 이 글에서 확인하지 못함 |
| Claude Code Remote Control 세션 | 실행은 PC 에서 하고, 연결되어 있는 동안 대화가 서버에도 저장됩니다 | 웹·모바일 앱에서 붙인 첨부는 `~/.claude/uploads/<session>/` |
| Claude 데스크톱(Windows 스토어 앱) | 일반 대화 원본이 기기에 있는지는 이 글에서 확인하지 못했고, 앱 안에서 시작한 Claude Code 세션 대화는 기기에 보관됩니다 | Electron 구조의 앱 폴더, 계정 UUID·기기 이름·세션 연결 정보 (확인 범위: Windows 11, 2026-09) |
| Gemini CLI·Codex CLI·Cursor·Ollama | 관찰한 폴더 목록에 대화 기록 파일이 없었습니다 (확인 범위: Windows 11, 2026-09) | 설정·설치 ID·훅 설정 |
| macOS·Linux, Android·iOS 앱 | 이 글에서 확인하지 못했습니다 | 각 OS 판 페이지 참고 |

**OS 계정과 권한.** Windows 에서 `~/.claude` 는 `%USERPROFILE%\.claude` 이고, Claude Code 문서는 대화 기록과 입력 기록을 저장할 때 암호화하지 않으며 "OS file permissions are the only protection." 이라고 적고 있습니다. 그래서 같은 PC 의 다른 계정이 이 파일을 읽거나 고칠 수 있었는지는 NTFS 권한과 프로필 경로로 따로 판단해야 합니다. 흔적이 어느 프로필 폴더 아래에 있는지는 "그 Windows 계정" 까지만 알려 주고, 그 계정을 여러 사람이 함께 썼는지는 로그온 기록과 맞춰 봅니다.

**수집 범위를 바꾸는 설정.** 환경 변수 `CLAUDE_CONFIG_DIR` 가 있으면 모든 `~/.claude` 경로가 그 폴더로 옮겨 가므로, 기본 위치가 비어 있으면 이 변수부터 확인합니다. `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 가 있으면 대화·입력 기록을 쓰지 않아서, 기록이 비어 있다는 사실만으로 사용하지 않았다고 말할 수 없습니다. 대화 전문은 기본 30일이 지나면 지우고 `cleanupPeriodDays` 로 기간을 바꿀 수 있는데, `history.jsonl` 과 `.credentials.json`, `stats-cache.json` 은 날짜로 지우지 않고 사용자가 지울 때까지 남습니다. 보관 기간과 서버 쪽 보관 규칙은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에서 다룹니다.

**시간대.** `history.jsonl` 의 `timestamp` 는 정수이지만, 단위와 기준 시간대는 공식 문서로 확인하지 못했습니다. 다른 기록의 시각과 맞출 때는 파일 시스템 시각이나 시각을 아는 다른 사건 하나와 먼저 대조해 기준을 정합니다.

## 볼 아티팩트와 순서

위에서부터 차례로 보면 "어느 OS 계정 → 어느 서비스 계정 → 어느 작업 폴더·시간대 → 사람인가 자동인가" 순서로 좁혀 갑니다.

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 흔적이 있는 프로필 폴더와 파일 권한 | 어느 Windows 계정 아래에 남았는가 | [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) |
| 2 | Claude Code `.credentials.json` 의 `claudeAiOauth.subscriptionType`, `rateLimitTier` 키 (확인 범위: Windows 11, 2026-09) | 로그인한 계정의 요금제 종류 | [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) |
| 3 | Claude Code `history.jsonl` | 입력한 프롬프트, 시각, 프로젝트 경로, 세션 ID | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 4 | Claude Code `projects/<project>/<session>.jsonl` | 서비스 계정·조직 식별자, 작업 폴더, git 브랜치, 실행 경로, 버전 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 5 | 하위 에이전트 기록(`subagents/` 아래) | 자동 에이전트가 만든 줄인지 가르는 단서 | [AI 에이전트가 무엇을 실행했나](../agents/agent-actions.md) |
| 6 | Claude Code `stats-cache.json` | 날짜별 메시지 수, 시간별 사용 분포 | [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) |
| 7 | Claude Code `feedback/drafts/`, `jobs/` | 작업 폴더, OS, CLI 버전, 만든 시각 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 8 | Claude 데스크톱 `config.json`, `claude_desktop_config.json`, `bridge-state.json` | 마지막 계정 UUID, 기기 이름, 로컬 세션과 서버 세션의 연결 | [Claude](../../02-artifacts/chat-services/claude/index.md) |
| 9 | Claude Code `remote-settings.json`, `policy-limits.json` | 조직 서버가 관리하는 설정 캐시 | [Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md) |
| 10 | 서비스 계정의 데이터 내보내기, 사업자 보유 기록 | 서버에만 있는 대화 원본, 로그인 IP·기기 기록 | [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md), [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) |
| 11 | 다른 AI 도구 폴더(`.gemini`, `.codex`, `.cursor`, `.ollama`) | 설치·설정 흔적, 조직이 걸어 둔 훅 | 아래 "함께 볼 페이지" |

## 분석 흐름

1. **프로필과 계정을 묶습니다.** 흔적이 있는 `%USERPROFILE%` 이 어느 Windows 계정인지 정하고, 그 계정의 로그온 기록과 기기를 함께 쓴 사람이 있었는지를 따로 적어 둡니다. 이 단계의 결론은 "이 Windows 계정" 에서 멈춥니다.

2. **서비스 계정을 찾습니다.** Claude Code 대화 기록에는 `ownerAccountUuid`, `ownerOrganizationUuid`, `userType` 키가 있고, Claude 데스크톱 `config.json` 에는 `lastKnownAccountUuid`, `cowork-enabled-cli-ops.json` 에는 `ownerAccountId`, `plan-usage-history.json` 에는 `samples[].org` 키가 있습니다 (확인 범위: Windows 11, 2026-09). 앱마다 적힌 계정·조직 값이 서로 같은지 맞춰 보면, 한 PC 에서 서비스 계정 여러 개를 오갔는지 알 수 있습니다. `claude_desktop_config.json` 은 계정별 설정을 `preferences.*ByAccount.` 아래에 계정마다 따로 둡니다 (확인 범위: Windows 11, 2026-09). 앱마다 계정 값을 같은 형식으로 적는지는 확인하지 못했으므로, 값이 다르게 생겼다고 바로 다른 계정이라고 보지 않습니다.

3. **대화를 작업 장소와 시간에 묶습니다.** `history.jsonl` 한 줄에는 `display`, `pastedContents`, `project`, `sessionId`, `timestamp` 키가 있습니다 (확인 범위: Windows 11, 2026-09). 아래는 이 키 이름으로 새로 만든 예시이고, 값은 모두 가짜입니다.

   ```json
   {"display":"결제 모듈 테스트 코드 정리해 줘","pastedContents":{},"project":"C:\\Users\\sample-user\\work\\demo-shop","sessionId":"11111111-2222-4333-8444-555555555555","timestamp":1767225600000}
   ```

   같은 `sessionId` 로 `projects/` 아래 대화 전문을 찾으면 `cwd`, `gitBranch`, `entrypoint`, `version`, `timestamp` 로 어느 폴더·브랜치에서 어떤 방식으로 실행했는지 이어 볼 수 있습니다 (확인 범위: Windows 11, 2026-09). `stats-cache.json` 의 `hourCounts` 와 `dailyActivity[]` 는 평소 어느 시간대에 썼는지를 보여 주므로, 문제의 대화 시각이 그 사람의 평소 사용 시간대와 맞는지 가늠하는 데 씁니다.

4. **사람의 입력과 자동 입력을 가릅니다.** 대화 기록에는 `promptSource`, `origin.kind`, `permissionMode`, `bridgeSessionId` 키가 있고, 하위 에이전트 기록에는 `agentId`, `attributionAgent`, `isSidechain` 키가 있습니다 (확인 범위: Windows 11, 2026-09). 이 키들은 사람이 친 입력과 에이전트가 만든 입력을 가르는 단서가 되지만, 값마다 무슨 뜻인지는 공식 문서로 확인하지 못했습니다. 그래서 보고서에는 키의 값을 그대로 옮기고 해석은 같은 도구로 재현해 본 결과가 있을 때만 붙입니다. `jobs/<이름>/state.json`(`createdAt`, `updatedAt`, `state`)과 `timeline.jsonl` 은 백그라운드 작업이 있었는지 보여 주고, `settings.json` 의 `hooks.UserPromptSubmit`·`hooks.SessionEnd` 같은 훅 설정은 입력이나 세션 종료 때 따로 실행되는 명령이 있었는지 보여 줍니다 (확인 범위: Windows 11, 2026-09).

5. **원격으로 이어진 세션을 확인합니다.** Claude 데스크톱의 `bridge-state.json` 에는 `localSessionId`, `remoteSessionId`, `environmentId` 키가 있고, `claude_desktop_config.json` 에는 `preferences.remoteToolsDeviceName` 키가 있습니다 (확인 범위: Windows 11, 2026-09). 다른 기기에서 이 PC 의 세션을 이어 썼을 가능성이 있으면 이 값들로 로컬 세션과 서버 세션을 짝지어 보고, 그 뒤는 서버 기록으로 넘깁니다. 각 키의 정확한 뜻은 확인하지 못했습니다.

6. **서버 기록으로 넘어갑니다.** 기기에 대화가 없거나 로그인 IP·기기 목록이 필요하면 계정 데이터 내보내기나 사업자 요청으로 받습니다. 내보내기 파일 구성과 사업자가 주는 로그인 기록의 형식은 이 글에서 확인하지 못했습니다. `.credentials.json` 에는 로그인 토큰이 평문으로 들어 있으므로, 사본은 원본과 같은 수준으로 보관하고 토큰 값은 보고서에 옮기지 않습니다.

## 흔한 오판

**프로필 폴더를 곧 사람으로 읽는 경우.** 흔적이 한 계정의 프로필 아래에 있다는 사실은 그 Windows 계정을 가리킬 뿐이고, 공용 계정이나 계정을 빌려 쓴 경우에는 사람이 달라집니다. 로그온 기록, 잠금 해제 기록 같은 다른 흔적과 맞추기 전에는 이름을 적지 않습니다.

**기록이 없으니 쓰지 않았다고 보는 경우.** 기록을 끄는 환경 변수, 기간이 지나 지운 대화, 클라우드 세션처럼 PC 에 대화 파일이 생기지 않는 방식이 모두 "빈 폴더" 로 보입니다. `history.jsonl` 과 `stats-cache.json` 처럼 날짜로 지우지 않는 파일이 남아 있는지 함께 봅니다.

**에이전트가 만든 줄을 사람의 입력으로 읽는 경우.** 하위 에이전트 기록이나 자동 작업이 남긴 줄도 같은 계정·같은 세션 아래에 쌓입니다. `isSidechain`·`agentId` 같은 키가 있는 줄과 사람이 친 줄을 섞어 세지 않습니다.

**파일이 평문이라 누구도 손대지 않았다고 보는 경우.** 대화 기록은 암호화하지 않은 평문이라 같은 권한이 있는 사람은 누구나 고칠 수 있습니다. 사업자가 보관한 기록이나 내보내기 파일을 받을 수 있으면 로컬 파일과 내용을 맞춰 보고 나중에 고쳤는지 가립니다. 서버 쪽 보관 기간은 요금제와 설정에 따라 다르고, 내보내기에 Claude Code 세션이 들어가는지는 이 글에서 확인하지 못했습니다.

## 보고서 문장 예

아래 문장은 형식을 보여 주려고 만든 예시이고, 이름과 값은 모두 가짜입니다.

> 사용자 계정 `sample-user` 의 프로필 폴더 아래 Claude Code 입력 기록(`history.jsonl`)에 프로젝트 경로 `C:\Users\sample-user\work\demo-shop` 으로 입력한 프롬프트 12건이 있고, 이 가운데 3건은 조사 대상 문구를 포함한다. 같은 세션의 대화 기록에 적힌 계정 식별자는 데스크톱 앱 설정의 마지막 로그인 계정 식별자와 같다. 이 기록은 해당 Windows 계정과 해당 서비스 계정에서 입력이 있었음을 보여 주며, 그 시각에 이 계정을 사용한 사람은 로그온 기록으로 따로 확인해야 한다.

> 조사 대상 대화는 기기에서 발견되지 않았다. 이 PC 의 설정에서 대화 기록을 끄는 환경 변수는 확인되지 않았고, 대화 전문 보관 기간은 기본값(30일)이었다. 대화 원본은 서비스 서버에 있을 수 있어 계정 데이터 내보내기를 요청하였다.

## 함께 볼 페이지

- [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md) — 서버·기기·동기화 구분
- [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md) — 데스크톱 앱 폴더 구조
- [크롬 계열 앱 공통 구조 (Windows 판)](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html) — `Local Storage`·`IndexedDB`·`Network/Cookies` 읽는 법
- [DPAPI 구조 (Windows 판)](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html) — 쿠키 등 보호된 값의 원리
- [키체인 (macOS 판)](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html), [데이터 보호 (iOS 판)](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html), [저장 공간 암호화 (Android 판)](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html) — 다른 OS 의 보호 방식
- [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Cursor](../../02-artifacts/dev-agents/cursor.md), [Ollama](../../02-artifacts/local-ai/ollama.md) — 다른 AI 도구의 흔적
- [회사가 허용하지 않은 AI를 썼나](../data-leak/shadow-ai.md) — 사용 사실 자체를 묻는 조사
- [이 글·이미지는 AI가 만들었나](ai-generated.md) — 결과물 쪽에서 출처를 묻는 조사
- [AI 관련 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) — 보고서 문장의 수위

## 참고 문헌

- Anthropic, Claude Code Docs — Data usage. https://code.claude.com/docs/en/data-usage (2026-09-25 확인)
- Anthropic, Claude Code Docs — Explore the .claude directory (application data). https://code.claude.com/docs/en/claude-directory (2026-09-25 확인)
