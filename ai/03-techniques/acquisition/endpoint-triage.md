---
title: "기기에서 AI 흔적 모으기"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 770
---

# 기기에서 AI 흔적 모으기 (Endpoint Triage)

사용자 기기에서 AI 도구의 기록 폴더·설정 파일·앱 저장소를 빠르게 찾아 모으는 방법이며, 기록이 자동으로 지워지기 전에 폴더째 수집하고 인증 토큰이 섞인 수집물을 비밀 자료로 다룹니다.

> 확인 날짜: 2026-09. Claude Code 의 기록 위치와 자동 삭제는 공식 문서 "Data usage"(2026-09-25 열람)로 확인했습니다. 폴더·파일 이름과 설정 키 이름은 Windows 11(빌드 26200) 한 대의 사용자 폴더를 읽기 전용으로 열어 본 관찰이고, 앱은 실행하지 않았으며 값과 앱 버전은 읽지 않았습니다. 관찰 대상은 Claude Code·Cursor·Codex CLI·Gemini CLI·Ollama·Claude 데스크톱(스토어 앱)뿐이고, ChatGPT·Copilot·Gemini 의 데스크톱·모바일 앱은 관찰하지 않았습니다.

## 언제 쓰나

기기를 확보했거나 사건 대응 중에 기기에 접근할 수 있을 때, 디스크 전체를 분석하기 전에 AI 관련 흔적부터 골라 모으려고 씁니다. 개발 도구와 에이전트는 대화 전문과 도구 실행 기록을 기기에 평문으로 남기는 경우가 있어서 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md) 같은 조사에서 기기 수집이 핵심이 됩니다. 전체 조사 순서는 [조사 절차](investigation-process.md)를 따르고, 이 페이지는 그중 기기 수집 단계만 다룹니다.

## 절차

### 1. 켜져 있는 기기인지 먼저 봅니다

기기가 켜져 있으면 [조사 절차](investigation-process.md)의 휘발성 순서대로 메모리부터 수집합니다. 관찰한 PC 에서는 Claude 데스크톱 저장소의 `Network/Cookies` 와 `declarative_performance_observer.db` 를 열려고 했을 때 SQLite 오류(OperationalError)가 났습니다(확인 범위: Windows 11, 2026-09). 앱 실행 중 잠김 때문인지는 확인하지 못했지만, 켜진 기기에서는 이런 DB 파일을 그 자리에서 열지 말고 먼저 복사본을 만든 뒤 복사본을 여는 편이 안전합니다. 앱을 실행하면 설정과 캐시 파일이 바뀔 수 있으니, 조사하려고 AI 앱을 새로 실행하지 않습니다.

### 2. 도구별 폴더를 폴더째 수집합니다 (Windows)

Claude Code 는 세션 기록을 기본 30일 동안만 보관하고 지나면 지우므로, 기기를 확보하면 이 폴더부터 모읍니다. 폴더 안 파일 하나하나의 뜻은 각 도구 페이지에서 다루고, 여기서는 무엇을 챙길지만 적습니다. 아래 표의 폴더와 파일은 관찰한 PC 에서 확인한 것입니다(확인 범위: Windows 11, 2026-09).

| 도구 | 위치 | 챙길 것 | 자세히 |
|---|---|---|---|
| Claude Code | `%USERPROFILE%\.claude` | `projects\` 아래 세션 기록(`.jsonl`)과 하위 에이전트 기록, `history.jsonl`, `file-history\`, `paste-cache\`, `settings.json`, `stats-cache.json`, `jobs\`, `feedback\drafts\`, `debug\`, `plugins\`, `.credentials.json` | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| Claude 데스크톱(스토어 앱) | 스토어 앱 패키지 폴더 안 `LocalCache\Roaming\Claude\` | `Local Storage\leveldb`, `IndexedDB`, `Network\Cookies`, `Cache`, `Local State`, 설정 JSON(`claude_desktop_config.json`, `config.json`, `bridge-state.json`, `git-worktrees.json`, `mcp-user-tool-toggles.json` 등) | [Claude](../../02-artifacts/chat-services/claude/index.md) |
| Claude 데스크톱(스토어 앱) | 같은 패키지 폴더 안 `LocalCache\Local\claude-cli-nodejs\Cache\` | 이름이 `mcp-logs-` 로 시작하는 폴더의 `.jsonl` 로그 | [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md) |
| Cursor | `%USERPROFILE%\.cursor` | `hooks.json` | [Cursor](../../02-artifacts/dev-agents/cursor.md) |
| Codex CLI | `%USERPROFILE%\.codex` | `hooks.json`, `skills\` | [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md) |
| Gemini CLI | `%USERPROFILE%\.gemini` | `settings.json`, `config\`(`config.json`, `hooks.json`, `mcp_config.json`, `projects\`), `antigravity\` | [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md) |
| Ollama | `%USERPROFILE%\.ollama` | `id_ed25519`, `id_ed25519.pub`, `cache\` | [Ollama](../../02-artifacts/local-ai/ollama.md) |

스토어 앱 패키지 폴더의 정확한 상위 경로는 이번 관찰 메모만으로 확정하지 못해서 표에 적지 않았습니다. 패키지 폴더 안의 `LocalCache\Roaming\Claude\` 는 Chromium 계열 앱과 같은 모양이라서, 폴더 구조와 LevelDB·쿠키 DB 를 읽는 법은 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)와 Windows 판의 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)를 봅니다. 관찰한 쿠키 DB 에는 `cookies` 표가 있고 그 안에 `value` 칸과 `encrypted_value` 칸이 함께 있었습니다(확인 범위: Windows 11, 2026-09). 암호화한 값을 보호하는 방식은 Windows 판의 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html)에서 다룹니다.

같은 패키지 폴더의 `LocalCache\Local\` 아래에는 Android SDK·NuGet·npm·pip 캐시처럼 AI 와 상관없는 개발 도구 파일도 섞여 있었습니다(확인 범위: Windows 11, 2026-09). 폴더 안에 있다고 해서 모두 Claude 데스크톱이 만든 파일은 아니니, 패키지 폴더를 통째로 수집하되 분석할 때는 경로로 걸러 냅니다.

Cursor 는 사용자 폴더에 `hooks.json` 한 파일만 있었고, 앱 데이터 폴더는 이 PC 에 없었습니다. Codex CLI 와 Gemini CLI 폴더에서도 대화 기록 파일은 보이지 않았고, Ollama 폴더에서는 모델 파일과 대화 기록이 보이지 않았습니다(확인 범위: Windows 11, 2026-09). 이 PC 에서 보이지 않았다는 뜻일 뿐 이 도구들이 대화를 남기지 않는다는 뜻은 아니니, 설정에 따라 다른 곳에 저장하는지는 각 도구 페이지에서 확인합니다.

### 3. 훅 설정을 챙깁니다

관찰한 네 도구(Claude Code, Cursor, Codex CLI, Gemini CLI) 모두 설정에 `hooks` 항목이 있었고, Cursor 는 `beforeSubmitPrompt`·`beforeShellExecution`·`afterAgentResponse` 같은 이름 아래 `command`·`timeout` 을 적습니다(확인 범위: Windows 11, 2026-09). 훅은 에이전트가 움직이는 시점마다 외부 명령을 실행하는 설정이라서, 조사 대상자가 걸어 둔 훅이 무엇을 실행했는지 검토하려면 설정 파일이 반드시 필요합니다. Claude Code 는 훅이 실행한 명령을 세션 기록의 `hookInfos[].command` 와 `attachment.hookName` 같은 키로 남겼습니다(확인 범위: Windows 11, 2026-09). 훅이 사고에 쓰였는지 보는 방법은 [프롬프트 인젝션 사고 분석](../analysis/prompt-injection.md)과 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)에서 다룹니다.

### 4. 원격 측정과 피드백 설정을 확인합니다

Claude Code 는 `DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`, `DISABLE_FEEDBACK_COMMAND`, `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 환경 변수로 원격 측정과 피드백 전송을 끌 수 있고, 모든 환경 변수는 `settings.json` 에도 넣을 수 있습니다. 문서에 따르면 사용량 지표에는 코드·프롬프트·파일 경로가 들어가지 않고, 이 변수들은 모델에 보내는 대화 자체를 막지 않습니다. 그래서 설정 파일이나 시스템 환경 변수에서 이 값들이 켜져 있으면 피드백·세션 공유로 올린 대화 사본과 오류 보고가 서버에 없을 수 있다고만 보고, 대화가 서버에 남았는지는 계정 종류별 보관 기간으로 따로 판단합니다.

`/feedback`·`/bug`·`/share` 로 보낸 기록은 Anthropic 에 5년 보관되지만, Bedrock 같은 제3자 제공자를 쓰거나 Anthropic 자격 증명이 없으면 보내지 않고 `~/.claude/feedback-bundles/` 에 로컬 파일로 남습니다. 세션 품질 조사에서 사용자가 "Yes" 를 고르면 대화 기록과 하위 에이전트 기록, 원시 세션 로그를 올리고 최대 6개월 보관하며, 일부 환경에서는 이것도 같은 폴더에 로컬로 남습니다. 관찰한 PC 의 폴더 목록에는 `feedback-bundles` 가 보이지 않았지만 목록이 일부 경로를 생략한 것이라 없다고 단정하지 않았습니다(확인 범위: Windows 11, 2026-09). 수집할 때는 이 폴더가 있는지 직접 확인합니다.

### 5. 인증 정보는 비밀 자료로 다룹니다

관찰한 Claude Code 폴더의 `.credentials.json` 에는 `claudeAiOauth` 아래 `accessToken`·`refreshToken`·`expiresAt`·`refreshTokenExpiresAt`·`scopes`·`subscriptionType` 같은 키가 있었고, `daemon\control.key`·`daemon\pipe.key` 파일도 있었습니다. Ollama 폴더에는 `id_ed25519` 와 `id_ed25519.pub` 키 쌍이 있었습니다(확인 범위: Windows 11, 2026-09). 이런 파일이 든 수집물은 접근을 제한해 보관하고, 보고서에 값을 옮겨 적지 않으며, 토큰이나 키로 계정·서비스에 접속하지 않습니다. 토큰이 어떤 흔적을 남기는지는 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)과 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md)에서 다룹니다.

### 6. 해시를 계산하고 기록합니다

수집이 끝나면 수집본의 해시를 계산하고 [조사 절차](investigation-process.md)의 보관 연속성 항목대로 기록합니다. Claude Code 세션 기록에 `version` 키가 있었으니(확인 범위: Windows 11, 2026-09), 수집 당시 도구 버전을 이 값으로 적어 둘 수 있는지 분석 단계에서 확인합니다. 아래는 수집 목록을 적는 모양을 보여 주려고 새로 만든 예시이고, 사용자 이름과 파일 이름은 지어낸 것입니다.

```text
C:\Users\demo-user\.claude\  -> case42_claude_code.zip  SHA-256 (계산 값)
C:\Users\demo-user\.cursor\hooks.json  -> case42_cursor_hooks.json  SHA-256 (계산 값)
Claude 데스크톱 패키지 폴더  -> case42_claude_desktop.zip  SHA-256 (계산 값)
```

## 다른 OS

**macOS·Linux.** Claude Code 는 세션 기록을 `~/.claude/projects/` 아래에 두고, 자동 삭제 규칙은 Windows 와 같습니다. macOS 용 Claude 데스크톱 앱의 저장 위치는 이번에 확인하지 못했고, 앱 설정 파일과 키 보관 방식의 공통 원리는 macOS 판의 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/plist/index.html)과 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html)을 봅니다.

**Android·iOS.** AI 앱이 기기의 어디에 무엇을 저장하는지는 이번에 확인하지 못했습니다. 앱 데이터 폴더와 저장소 암호화의 공통 원리는 Android 판의 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)와 [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html), iOS 판의 [데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html)와 [로컬 백업](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/backups/local-backup/index.html)에서 다룹니다. 모바일에서만 쓴 계정이라면 [계정 데이터 내보내기로 수집](export-collection.md)이나 [서비스 회사에 대한 데이터 요청](legal-requests.md)을 함께 검토합니다.

## 도구

폴더를 모을 때는 시각 정보를 보존하는 수집 도구나 디스크 이미지 도구를 쓰고, RFC 3227 이 경고한 대로 모든 파일의 접근 시각을 바꾸는 복사 명령은 피합니다. 세션 기록 같은 JSON Lines 파일은 `jq` 로 키를 골라 볼 수 있고, 쿠키 같은 SQLite 파일은 복사본을 `sqlite3` 이나 DB Browser for SQLite 로 엽니다. SQLite 와 LevelDB 를 읽는 법은 Windows 판의 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html)와 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html)에 있습니다.

## 함정과 한계

Claude Code 세션 기록은 기본 30일이 지나면 지워지고 `cleanupPeriodDays` 로 이 기간을 바꿀 수 있어서, 기록이 짧게 남아 있다면 설정 파일에서 이 값을 확인합니다. Claude 데스크톱이나 Cowork 에서 시작했거나 마지막으로 이어 간 세션은 기본적으로 이 제한을 받지 않아서, 같은 기기 안에서도 세션마다 남은 기간이 다를 수 있습니다. Anthropic 이 관리하는 가상 머신에서 돈 클라우드 세션은 처음부터 기기에 원본이 없습니다.

설정 파일은 수집한 시점의 설정을 보여 줄 뿐이고, 사건이 일어난 때에도 같은 설정이었는지는 따로 확인해야 합니다. 관찰 내용은 한 PC 에서 파일 이름과 키 이름만 본 것이라, 다른 버전이나 다른 설정의 기기에서는 파일 구성이 다를 수 있습니다.

## 결과를 어떻게 해석하나

세션 기록과 입력 이력은 그 기기의 그 사용자 폴더에서 해당 도구가 이런 대화와 도구 실행을 기록했다는 사실을 보여 주지만, 누가 키보드 앞에 있었는지까지 정하지는 못합니다. `stats-cache.json` 처럼 일별 메시지 수·세션 수·도구 호출 수를 모아 둔 파일(확인 범위: Windows 11, 2026-09)은 사용량의 흐름을 보여 주지만 개별 대화 내용을 대신하지 못합니다. 기기에 기록이 없을 때는 자동 삭제, 클라우드 세션, 다른 기기 사용 가운데 어느 경우인지 계정 내보내기나 회사 자료와 맞춰 봅니다. 모은 기록을 시간 순으로 엮는 방법은 [AI 사용 타임라인](../analysis/timeline.md)에, 지워진 대화를 되살리는 방법은 [대화 내용 되살리기](../analysis/content-recovery.md)에 있습니다.

## 참고 문헌

- Claude Code 문서, "Data usage". https://code.claude.com/docs/en/data-usage (2026-09-25 열람)
- D. Brezinski, T. Killalea, "RFC 3227 — Guidelines for Evidence Collection and Archiving (BCP 55)", 2002-02. https://www.rfc-editor.org/rfc/rfc3227
