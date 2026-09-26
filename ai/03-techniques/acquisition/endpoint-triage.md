---
title: "기기에서 AI 흔적 모으기"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 850
---

# 기기에서 AI 흔적 모으기 (Endpoint Triage)

사용자 기기에서 AI 도구의 기록 폴더·설정 파일·앱 저장소를 골라 모으는 방법입니다. 켜진 기기라면 메모리부터 뜨고, 기록이 자동으로 지워지기 전에 폴더째 모으며, SQLite 는 `-wal` 파일까지 함께 모으고, 인증 토큰이 섞인 수집물은 비밀 자료로 다룹니다.

아래 표의 폴더·파일 이름은 Windows 11(빌드 26200) 기준입니다.

## 언제 쓰나

기기를 확보했거나 사건 대응 중에 기기에 접근할 수 있을 때, 디스크 전체를 분석하기 전에 AI 관련 흔적부터 골라 모으려고 씁니다. 개발 도구와 에이전트는 대화 전문과 도구 실행 기록을 기기에 평문으로 남기는 경우가 많아서 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md) 같은 조사에서는 기기 수집이 핵심이 됩니다. 로컬 LLM 앱은 대화 본문이 기기에만 있는 경우가 많아 [로컬 AI](../../02-artifacts/local-ai/index.md) 조사도 기기 수집에서 시작합니다. 전체 조사 순서는 [조사 절차](investigation-process.md)를 따르고, 이 페이지는 그중 기기 수집 단계만 다룹니다.

## 절차

### 1. 켜진 기기면 메모리부터 뜹니다

기기가 켜져 있으면 [조사 절차](investigation-process.md)의 휘발성 순서대로 메모리를 먼저 수집합니다. Linux 가상 머신에서 돌린 Codex CLI 와 VS Code Copilot 의 메모리에서는 `tools/call` 요청의 인자와 실행 결과를 JSON-RPC 메시지로 찾을 수 있고, JSON-RPC `id` 로 요청과 응답을 짝지을 수 있습니다. 서버를 stdio 로 붙인 경우와 HTTP 로 붙인 경우 모두 되살아났습니다[4]. 공격을 재현한 시험에서는 악성 지시문이 든 서버 응답이 메모리에 없었고(수집 전에 덮어쓴 것으로 보입니다), 빼낸 내용을 실어 보낸 요청은 남아 있었습니다[4]. 그러니 한 번 뜬 메모리에 어떤 호출의 흔적이 없어도 그 호출이 없었다는 증거로 보지 않습니다[4]. 그래서 메모리는 가능한 한 빨리 뜹니다. LangurTrace 시험에서 "되살릴 수 없음" 으로 나온 항목은 디스크 수준 복구만 기준으로 한 것이라, 볼륨 섀도 복사본이나 라이브 메모리에서는 일부 되살릴 수 있습니다(§6.2)[3]. 메모리에서 무엇을 어떻게 찾는지는 [메모리에서 AI 흔적 찾기](../analysis/memory-analysis.md)에서 다룹니다.

조사하려고 AI 앱을 새로 실행하지 않습니다. 앱을 실행하면 설정·캐시·DB 파일이 바뀔 수 있습니다.

### 2. 도구별 폴더를 폴더째 모읍니다 (Windows)

파일을 골라 담지 말고 도구 폴더를 통째로 모읍니다. 폴더 안 파일 하나하나의 뜻은 각 도구 페이지에서 다루고, 아래 표는 어디를 모을지만 적습니다. `%USERPROFILE%` 아래 점(`.`)으로 시작하는 폴더는 macOS·Linux 의 `~/` 아래 같은 이름 폴더와 대응합니다.

| 도구 | 모을 위치 | 특히 챙길 것 | 출처 | 자세히 |
|---|---|---|---|---|
| Claude Code | `%USERPROFILE%\.claude\` | `projects\` 세션 기록(`.jsonl`)과 하위 에이전트 기록, `history.jsonl`, `sessions\`, `backups\`, `file-history\`, `paste-cache\`, `shell-snapshots\`, `settings.json`, `.last-cleanup` | [5][6] | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| Claude 데스크톱·Cowork (스토어 앱) | `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\` | `local-agent-mode-sessions\`, `claude-code-sessions\`, `Local Storage\leveldb`, `IndexedDB`, `Network\Cookies`, 설정 JSON(`claude_desktop_config.json` 등) | [5][7] | [Claude](../../02-artifacts/chat-services/claude/index.md) |
| Claude 데스크톱·Cowork (설치형) | `%APPDATA%\Claude\` | 위와 같음 | [5][7] | 위와 같음 |
| Claude 데스크톱 MCP 로그 | 스토어 앱 패키지 폴더의 `LocalCache\Local\claude-cli-nodejs\Cache\` | 이름이 `mcp-logs-` 로 시작하는 폴더의 `.jsonl` | | [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md) |
| Cursor 편집기 | `%APPDATA%\Cursor\User\globalStorage\` | `state.vscdb` 와 `-wal`·`-shm` | [7] | [Cursor](../../02-artifacts/dev-agents/cursor.md) |
| Cursor CLI 등 | `%USERPROFILE%\.cursor\` | `projects\` 아래 `agent-transcripts\`, `chats\` 아래 `store.db` 와 `store.db-wal`, `ai-tracking\ai-code-tracking.db`, `hooks.json` | [7] | 위와 같음 |
| Codex CLI | `%USERPROFILE%\.codex\` | `sessions\`, `history.jsonl`, `hooks.json`, `skills\` | [7] | [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md) |
| Gemini CLI | `%USERPROFILE%\.gemini\` | `tmp\` 아래 프로젝트별 `chats\`, `settings.json`, `projects.json`, `antigravity\` | [7] | [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md) |
| GitHub Copilot CLI | `%USERPROFILE%\.copilot\` | `session-state\`, `session-store.db` 와 `session-store.db-wal` | [7] | [GitHub Copilot](../../02-artifacts/dev-agents/github-copilot/index.md) |
| Visual Studio Copilot | `%LOCALAPPDATA%\Temp\VSGitHubCopilotLogs\traces\`, 솔루션 폴더의 `.vs\` | 추적 파일 | [7][8] | 위와 같음 |
| Ollama | `%USERPROFILE%\.ollama\`, `%LOCALAPPDATA%\Ollama\` | `history`, `models\manifests\`, `models\blobs\`, `*.log`, `id_ed25519`·`id_ed25519.pub` | [3][9] | [Ollama](../../02-artifacts/local-ai/ollama.md) |
| 그 밖의 로컬 LLM 앱 | 아래 "도구" 의 LangurTrace 타깃 표 | | [9] | [로컬 AI](../../02-artifacts/local-ai/index.md) |
| Recall (Copilot+ PC) | `C:\Users\*\AppData\Local\CoreAIPlatform.00\UKP\` | 폴더 전체(재귀) | [10] | [Recall](../../02-artifacts/windows-ai/recall.md) |

Windows 에서 Claude Code 가 어떤 하위 폴더를 쓰는지는 출처끼리 다릅니다. claude-forensics 문서는 2026년 중반의 Windows Claude Code 가 `history.jsonl`, `shell-snapshots/`, `paste-cache/`, `file-history/` 를 쓰지 않는 것으로 보인다고 했지만[5], 2026-09 무렵 Windows 11(빌드 26200)의 Claude Code 폴더에는 `history.jsonl`·`paste-cache\`·`file-history\` 가 있습니다. 판과 설정에 따라 다를 수 있으니 폴더를 통째로 모은 뒤 무엇이 있는지 목록으로 남깁니다.

사용자 폴더만 살펴보면 놓치는 곳이 있습니다. Aider 는 작업 중인 저장소 안에 기록을 쓰고, Visual Studio 의 Copilot 은 솔루션 폴더의 `.vs\` 에 쓰므로[8], 조사 대상자의 작업 폴더도 함께 봅니다. Ollama 모델을 `OLLAMA_MODELS` 환경 변수로 다른 곳에 옮겼다면 그 위치도 따로 모읍니다. 스토어 앱 패키지 폴더의 `LocalCache\Local\` 아래에는 Android SDK·NuGet·npm·pip 캐시처럼 AI 와 상관없는 개발 도구 파일도 섞여 있을 수 있으니, 패키지 폴더는 통째로 모으되 분석할 때 경로로 걸러 냅니다.

Claude 데스크톱 폴더는 Chromium 계열 앱과 같은 모양이라서, LevelDB·쿠키 DB 를 읽는 법은 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)와 Windows 판의 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)를 봅니다. 쿠키 DB 의 `cookies` 표에는 `value` 열과 `encrypted_value` 열이 함께 있고, 암호화한 값을 보호하는 방식은 Windows 판의 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/protection/data-protection-api/index.html)에서 다룹니다.

### 3. SQLite 는 `-wal`·`-shm` 파일과 함께 모읍니다

SQLite DB 가 미리 쓰기 로그(Write-Ahead Log, WAL) 방식이면 최근에 쓴 행은 체크포인트로 본 파일에 옮겨지기 전까지 옆의 `-wal` 파일에 있습니다. coding-agent-forensics 가 다루는 에이전트 11종 가운데 SQLite 를 쓰는 4종은 모두 WAL 을 씁니다. 막 기록한 Hermes Agent DB 는 본 파일이 4 KB 인데 대화 111 KB 가 WAL 에 남아 있어서, `state.db` 만 모으면 아무것도 되살리지 못합니다[8]. 2026-09-07 에 Windows 에서 뜬 Cursor CLI `store.db` 도 4096바이트 머리만 있고 스키마와 행은 `store.db-wal` 에 있었습니다[7]. GitHub Copilot CLI 의 `session-store.db` 도 `-wal` 과 함께 읽어야 합니다[7].

그래서 `.db`·`.sqlite`·`.vscdb` 파일을 모을 때는 같은 이름의 `-wal`·`-shm` 파일을 한 번에 복사하고, 분석은 원본이 아닌 복사본으로 합니다. 수집 도구의 파일 거르개가 본 파일 이름만 지정하면 WAL 이 빠집니다. 예를 들어 LangurTrace 의 Msty 타깃은 `FileMask: 'msty.db'`, Jan 타깃은 `FileMask: 'cortex.db'` 로 지정해 옆의 `-wal`·`-shm` 파일을 모으지 않으므로 [9], 실제 기기에 이 파일이 있으면 따로 모읍니다. WAL 의 구조와 지운 행을 찾는 법은 Windows 판의 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html)에서 다룹니다.

### 4. 훅 설정을 챙깁니다

Claude Code, Cursor, Codex CLI, Gemini CLI 는 모두 설정에 `hooks` 항목이 있고, Cursor 는 `beforeSubmitPrompt`·`beforeShellExecution`·`afterAgentResponse` 같은 이름 아래 `command`·`timeout` 을 적습니다. 훅은 에이전트가 움직이는 시점마다 외부 명령을 실행하는 설정이라서, 조사 대상자가 걸어 둔 훅이 무엇을 실행했는지 보려면 설정 파일이 꼭 필요합니다. Claude Code 는 훅이 실행한 명령을 세션 기록의 `hookInfos[].command` 와 `attachment.hookName` 같은 키로 남깁니다. ccfx [6] 도 `settings.json`·`settings.local.json` 에서 권한 규칙과 훅 정의를 뽑습니다. 훅이 사고에 쓰였는지 보는 방법은 [프롬프트 인젝션 사고 분석](../analysis/prompt-injection.md)에서 다룹니다.

### 5. 자동 삭제와 전송 설정을 확인합니다

Claude Code 는 세션 기록을 기본 30일 동안만 보관하고, `cleanupPeriodDays` 로 이 기간을 바꿀 수 있습니다 [1]. 세션 기록(`projects\` 아래 `.jsonl`)이 지워진 뒤에도 입력 이력 `history.jsonl` 은 몇 달 더 남고, 마지막 정리 시각은 `.last-cleanup` 에 남습니다[5]. 그래서 세션 기록이 없는 입력 이력 줄은 지워진 세션의 유일한 흔적일 수 있습니다. Gemini CLI 도 개수와 기간 기준으로 자기 기록을 지우므로[8], 두 도구는 기기를 확보하는 대로 먼저 모읍니다.

Claude Code 는 `DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`, `DISABLE_FEEDBACK_COMMAND`, `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 환경 변수로 원격 측정과 피드백 전송을 끌 수 있고, 모든 환경 변수는 `settings.json` 에도 넣을 수 있습니다 [1]. 사용량 지표에는 코드·프롬프트·파일 경로가 들어가지 않고, 이 변수들은 모델에 보내는 대화 자체를 막지 않습니다[1]. 그래서 이 값들이 켜져 있으면 피드백으로 올린 대화 사본과 오류 보고가 서버에 없을 수 있다고만 보고, 대화가 서버에 남았는지는 계정 종류별 보관 기간으로 따로 판단합니다.

`/feedback`·`/bug`·`/share` 로 보낸 기록은 Anthropic 에 5년 보관되지만, Bedrock 같은 제3자 제공자를 쓰거나 Anthropic 자격 증명이 없으면 보내지 않고 `~/.claude/feedback-bundles/` 에 로컬 파일로 남습니다 [1]. 세션 품질 조사에서 사용자가 "Yes" 를 고르면 대화 기록과 하위 에이전트 기록, 원시 세션 로그를 올리고 최대 6개월 보관하며, 일부 환경에서는 이것도 같은 폴더에 로컬로 남습니다 [1]. 수집할 때 이 폴더가 있는지 직접 봅니다.

### 6. 인증 정보는 비밀 자료로 다룹니다

Claude Code 폴더의 `.credentials.json` 에는 `claudeAiOauth` 아래 `accessToken`·`refreshToken`·`expiresAt`·`refreshTokenExpiresAt`·`scopes`·`subscriptionType` 같은 키가 있고, `daemon\control.key`·`daemon\pipe.key` 파일도 있습니다. Ollama 폴더에는 `id_ed25519` 와 `id_ed25519.pub` 키 쌍이 있습니다. `backups\.claude.json.backup.*` 에는 계정 이메일과 조직 정보가 들어 있으므로[5][6], 이 파일도 개인 정보로 다룹니다.

인증 파일을 모을지는 도구마다 원칙이 다릅니다. coding-agent-forensics [8] 는 `auth.json`·`.credentials.json`·API 키가 든 설정 파일은 조사에 보탬이 없고 쥐고 있는 비밀만 늘리니 모으지 말라고 합니다. ccfx [6] 는 `.credentials.json` 의 값은 읽지 않고 있는지·크기·수정 시각만 적지만, `-ac` 로 만든 수집 압축본에는 이 파일이 평문으로 들어가고 `--redact-pii` 도 적용되지 않는다고 경고합니다. 수집 범위는 영장이나 동의 범위에 맞춰 정하고, 인증 파일이 든 수집물은 접근을 제한해 보관하며, 보고서에는 값을 옮겨 적지 않습니다. 토큰이 남는 곳은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)과 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md)에서 다루고, 서버 쪽 기록은 [서비스 회사에 대한 데이터 요청](legal-requests.md)으로 받습니다.

### 7. 해시를 계산하고 기록합니다

수집이 끝나면 수집본의 해시를 계산하고 [조사 절차](investigation-process.md)의 보관 연속성 항목대로 기록합니다. claude-forensics [5] 는 스냅숏과 결과 파일 전체의 SHA-256 을 `MANIFEST.sha256` 에 적고 `sha256sum -c` 로 대조하게 합니다. Claude Code 세션 기록과 `sessions\` 파일에 `version` 키가 있으므로[6] 수집 당시 도구 판을 이 값으로 함께 적어 둡니다. 아래는 수집 목록을 적는 모양을 보여 주려고 만든 예시이고, 사용자 이름과 파일 이름은 지어낸 것입니다.

```text
C:\Users\demo-user\.claude\  -> case42_claude_code.zip  SHA-256 (계산 값)
C:\Users\demo-user\.cursor\  -> case42_cursor.zip  SHA-256 (계산 값)
Claude 데스크톱 패키지 폴더  -> case42_claude_desktop.zip  SHA-256 (계산 값)
```

### 다른 OS

**macOS·Linux.** Claude Code 는 `~/.claude/` 를 쓰고 자동 삭제 규칙은 Windows 와 같습니다 [1]. macOS 의 Claude 데스크톱·Cowork 폴더는 `~/Library/Application Support/Claude/` 이고[5], 다른 도구의 macOS·Linux 경로는 agentsview 문서의 표에 있습니다[7]. 설정 파일과 키 보관 방식의 공통 원리는 macOS 판의 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/data-formats/plist/index.html)과 [키체인](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/protection/keychain/index.html)을 봅니다. LangurTrace [3] 는 Windows 만 시험했습니다.

**Android·iOS.** 모바일 AI 앱의 저장 위치는 각 서비스 페이지에서 다룹니다. 앱 데이터 폴더를 얻을 수 있는지는 추출 방식에 따라 달라서, Android 판의 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html)와 [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/encryption/index.html), iOS 판의 [데이터 보호](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/data-protection/index.html)와 [로컬 백업](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/backups/local-backup/index.html)을 보고 수집 범위를 정합니다. 모바일에서만 쓴 계정이라면 [계정 데이터 내보내기로 수집](export-collection.md)이나 [서비스 회사에 대한 데이터 요청](legal-requests.md)을 함께 검토합니다.

## 도구

폴더를 모을 때는 시각 정보를 보존하는 수집 도구나 디스크 이미지 도구를 쓰고, 모든 파일의 접근 시각을 바꾸는 복사 명령은 피합니다[2]. 아래 도구는 AI 흔적을 모으거나 모은 폴더를 읽는 공개 도구입니다.

| 도구 | 대상 | 하는 일 | 시험 판·날짜 |
|---|---|---|---|
| KAPE 타깃 `WindowsCopilotRecall.tkape` [10] | Recall | `C:\Users\*\AppData\Local\CoreAIPlatform.00\UKP\` 를 재귀로 복사 | 타깃 Version 1.0 |
| LangurTrace [3][9] | Ollama·Chatbox·LM Studio·Msty·Jan·GPT4All | KAPE 타깃으로 모으고, 모듈(`LangurTrace.exe`)로 HTML·CSV·XLSX 보고서를 만듦 | 논문은 Windows 11 Pro 24H2(26100.3775)에서 Ollama 0.6.5, Chatbox 1.11.8, LM Studio 0.3.14, Msty 1.8.5, Jan 0.5.16, GPT4All 3.10.0 을 시험(2025) |
| claude-forensics [5] | Claude Code·Claude 데스크톱·Cowork | 모은 폴더를 읽기 전용 스냅숏으로 복사한 뒤 세션·입력·붙여 넣기·파일 이력을 JSONL·보고서로 뽑고 `MANIFEST.sha256` 을 만듦. macOS·Linux 에서 실행하며 Windows 에서 가져온 폴더도 읽음 | v0.1.1(마지막 커밋 2026-06-16) |
| ccfx [6] | Claude Code | `.claude` 를 바꾸지 않고 읽어 세션·도구 사용·계정 정보를 CSV·JSON·Markdown·HTML 로 냄. Windows 에서도 실행. `-ac` 로 파일 시각을 보존한 압축본 `claude-acquisition.zip` 을 만듦(Windows 에서 `-ac` 는 심볼릭 링크를 보존하려고 관리자 권한이나 개발자 모드 필요) | 저장소 마지막 push 2026-08-18 |
| coding-agent-forensics [8] | Claude Code·Codex·Copilot·Cursor·Gemini 등 11종 | 인터넷 없이 여는 HTML 한 파일에 기록을 끌어 넣어 타임라인·파일 변경·위험 규칙을 보여 줌. 앱 안의 수집 안내에 Windows·macOS·Linux 에이전트별 저장 경로와 Velociraptor 수집 절차가 들어 있음 | 저장소 마지막 push 2026-08-29 |

LangurTrace 타깃이 모으는 위치는 아래와 같습니다 [9]. 경로는 모두 `C:\Users\%user%\` 아래로 고정이라, 다른 드라이브나 환경 변수로 옮긴 위치는 모으지 않습니다.

| 타깃 | 모으는 위치(`C:\Users\%user%\` 아래) |
|---|---|
| Ollama | `AppData\Local\Ollama\*.log`, `.ollama\models\manifests\registry.ollama.ai\library\`(재귀), `.ollama\models\blobs\`, `.ollama\history` |
| Chatbox | `AppData\Roaming\xyz.chatboxapp.app\` 의 `*.json`, `chatbox-blobs\`, `logs\*.log`, `Cache\CacheData\` |
| LM Studio | `.lmstudio\.internal\download-jobs-info.json`, `.lmstudio\models\`(재귀), `.lmstudio\Conversations`, `.lmstudio\user-files\`, `AppData\Roaming\LMStudio\logs\*.log` |
| Msty | `AppData\Roaming\Msty\` 의 `logs\app*.log`, `models\manifests\registry.ollama.ai\library\`(재귀), `models\blobs\`, `msty.db`, `attachments\` |
| Jan | `AppData\Roaming\Jan\data\` 의 `models`(재귀), `cortex.db`, `threads`(재귀), `logs\cortex*.log`, `AppData\Roaming\Jan\Local Storage\leveldb\` |
| GPT4All | `AppData\Local\nomic.ai\GPT4ALL\` 의 `*.gguf`, `*.rmodel`, `*.chat` |

타깃 경로와 논문 부록 A 의 경로는 두 곳에서 다릅니다. LM Studio 로그는 논문이 `%AppData%/LM Studio/logs/main.log`(공백 있음), 타깃이 `AppData\Roaming\LMStudio\logs\`(공백 없음)로 적었고, Chatbox API 캐시는 논문이 `Cache/Cache_Data`, 타깃이 `Cache\CacheData\` 로 적었습니다 [3][9]. 실제 기기에서 두 경로를 모두 찾아봅니다. 논문을 낸 뒤 Jan 과 Msty 는 저장 형식을 바꿨다는 지적이 있으므로 [11], 지금 판에서는 타깃이 모은 폴더가 비어 있지 않은지 확인합니다.

세션 기록 같은 JSON Lines 파일은 `jq` 로 키를 골라 볼 수 있고, SQLite 파일은 복사본을 `sqlite3` 이나 DB Browser for SQLite 로 엽니다. LevelDB 를 읽는 법은 Windows 판의 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)에 있습니다.

## 함정과 한계

Claude 데스크톱이나 Cowork 에서 시작했거나 마지막으로 이어 간 세션은 기본적으로 30일 삭제 규칙을 받지 않아서, 같은 기기 안에서도 세션마다 남은 기간이 다를 수 있습니다 [1]. Anthropic 이 관리하는 가상 머신에서 돈 클라우드 세션은 처음부터 기기에 원본이 없습니다 [1].

수집 도구의 경로 목록은 도구를 만든 때의 앱 판을 기준으로 합니다. LangurTrace 타깃은 2025년 판 앱을 기준으로 하고, claude-forensics 는 없는 하위 폴더를 경고만 남기고 건너뜁니다 [5]. 도구가 아무것도 내놓지 않으면 앱이 기록을 남기지 않은 것인지 도구가 경로를 모르는 것인지부터 확인합니다. 폴더째 모아 두면 나중에 다른 도구로 다시 읽을 수 있습니다.

설정 파일은 수집한 시점의 설정을 보여 줄 뿐이고, 사건이 일어난 때에도 같은 설정이었는지는 따로 확인해야 합니다. 파일 구성은 앱 판과 설정에 따라 다를 수 있으므로 실제 기기에서 확인합니다.

## 결과를 어떻게 해석하나

세션 기록과 입력 이력은 그 기기의 그 사용자 폴더에서 해당 도구가 이런 대화와 도구 실행을 기록했다는 사실을 보여 주지만, 누가 키보드 앞에 있었는지까지 정하지는 못합니다. 이 기록은 서명이 없고 사용자가 고칠 수 있는 파일이라서[8], 대상자가 관리하던 PC 의 앱 로그처럼 다룹니다. `stats-cache.json` 처럼 일별 메시지 수·세션 수·도구 호출 수를 모아 둔 파일은 사용량의 흐름을 보여 주지만 개별 대화 내용을 대신하지 못합니다.

기기에 기록이 없을 때는 자동 삭제, 클라우드 세션, 다른 기기 사용, 수집 도구가 경로를 놓친 경우 가운데 어느 쪽인지 `.last-cleanup`, 계정 내보내기, 회사 자료와 맞춰 봅니다. 메모리에서 찾은 흔적이 디스크 기록과 맞지 않으면 그 차이 자체를 보고서에 적습니다. 모은 기록을 시간 순으로 엮는 방법은 [AI 사용 타임라인](../analysis/timeline.md)에, 지워진 대화를 되살리는 방법은 [대화 내용 되살리기](../analysis/content-recovery.md)에 있습니다.

## 참고 문헌

1. Claude Code 문서, "Data usage". https://code.claude.com/docs/en/data-usage (2026-09-25 열람)
2. D. Brezinski, T. Killalea, "RFC 3227 — Guidelines for Evidence Collection and Archiving (BCP 55)", 2002-02. https://www.rfc-editor.org/rfc/rfc3227
3. S. Jeong, S. Lee, J. Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation 54 (2025) 301987. https://doi.org/10.1016/j.fsidi.2025.301987
4. A. Sattar, M. Salmon, L. Muhanna, T. T. Spinosa, T. Gharaibeh, I. Baggili, "With or Without Logs: Memory Forensic Reconstruction of Model Context Protocol (MCP) Activity in Agentic LLM Systems". 도구: BiTLab-BaggiliTruthLab/MCPRecon, `tool/mcprecon.py`. https://github.com/BiTLab-BaggiliTruthLab/MCPRecon
5. forensicdave/claude-forensics, `README.md`. https://github.com/forensicdave/claude-forensics
6. fkasasagi/ccfx, `README.en.md`. https://github.com/fkasasagi/ccfx
7. kenn-io/agentsview, `README.md`(last_edited 2026-09-11), `docs/internal/session-format-sources.md`, `internal/parser/cowork_paths.go`, `internal/parser/cursor_ide.go`, `internal/parser/copilot_provider.go`. https://github.com/kenn-io/agentsview
8. Shorton88/coding-agent-forensics, `README.md`. https://github.com/Shorton88/coding-agent-forensics
9. jeongramon/LangurTrace, `dist/Targets/LLMApplications/*.tkape`. https://github.com/jeongramon/LangurTrace
10. EricZimmerman/KapeFiles, `Targets/Windows/WindowsCopilotRecall.tkape`. https://github.com/EricZimmerman/KapeFiles
11. k0w4lzk1/LangurTrace-Implementation, `GAPS.md`. https://github.com/k0w4lzk1/LangurTrace-Implementation
