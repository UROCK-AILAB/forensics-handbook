---
title: "에이전트가 자격 증명을 건드렸나"
parent: "시나리오 · AI 에이전트"
nav_order: 890
---

# 에이전트가 자격 증명을 건드렸나 (Agent Credentials)

> 확인 범위: 공식 문서는 2026-09-25 에 열어 본 내용입니다. "(확인 범위: Windows 11, 2026-09)" 가 붙은 내용은 Windows 11 PC 한 대에서 폴더를 읽기 전용으로 열어 파일 이름과 키 이름만 확인한 것이고, 토큰 같은 값은 읽지 않았습니다. 이 페이지는 흔적을 찾고 해석하는 방법만 다루고, 저장된 비밀 값을 꺼내거나 보호를 푸는 방법은 다루지 않습니다.

## 조사 질문

AI 에이전트가 비밀번호·API 키·토큰 같은 자격 증명(credential)을 읽거나 출력했는지, 그리고 에이전트 도구 자신이 쓰는 인증 정보가 어디에 어떤 보호로 저장돼 있었는지를 밝히는 조사입니다. 두 갈래로 나뉘는데, 하나는 에이전트가 사용자 프로젝트의 `.env` 파일이나 키 파일을 열어 본 경우이고, 다른 하나는 에이전트 도구의 로그인 토큰이 유출됐는지 묻는 경우입니다. 두 갈래 모두 에이전트가 무엇을 실행했는지 먼저 알아야 해서, 실행 기록을 찾고 읽는 절차는 [AI 에이전트가 무엇을 실행했나](agent-actions.md)를 따르고 이 페이지는 자격 증명과 관련된 부분만 다룹니다.

## 먼저 확인할 것

- **증거 자체에 비밀 값이 있습니다.** Claude Code 문서는 세션 기록과 프롬프트 기록이 저장될 때 암호화되지 않고 OS 파일 권한만으로 보호된다고 밝히고, 도구가 `.env` 파일을 읽거나 명령이 자격 증명을 출력하면 그 값이 `projects/<project>/<session>.jsonl` 에 그대로 적힌다고 설명합니다. 수집본을 다루는 사람과 보관 위치를 제한하고, 보고서에는 값을 가려서 씁니다.
- **OS 마다 저장 방식이 다릅니다.** 같은 도구라도 Windows·Linux 에서는 파일에, macOS 에서는 키체인(Keychain)에 인증 정보를 둘 수 있어서 검체의 OS 를 먼저 적어 둡니다.
- **설정 폴더가 옮겨졌는지 봅니다.** Claude Code 는 `CLAUDE_CONFIG_DIR`, Codex 는 `CODEX_HOME` 환경 변수로 설정 폴더를 옮길 수 있고, 그러면 인증 파일도 그 폴더에 생깁니다.
- **도구 버전과 날짜를 적습니다.** 인증 파일 이름과 저장 방식은 판에 따라 바뀔 수 있고, 아래 내용은 2026-09 기준입니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | Claude Code 세션 기록과 하위 에이전트 기록 | 에이전트가 연 파일 경로와 명령, 그 출력에 섞인 값 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 2 | 큰 도구 출력 `.../<session>/tool-results/`, 붙여넣기 `~/.claude/paste-cache/`, 수정 전 사본 `~/.claude/file-history/<session>/` | 세션 기록 밖에 따로 저장된 출력·붙여넣은 내용·고치기 전 파일 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 3 | 권한 규칙 `.claude/settings.json`, `.claude/settings.local.json` 의 `permissions` | 자격 증명 파일 읽기를 막아 두었는지 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 4 | Claude Code 인증 파일 `.credentials.json` 과 macOS 키체인 항목 | 도구 자신의 로그인 정보가 있는 곳 | [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) |
| 5 | Codex `config.toml` 의 `cli_auth_credentials_store`, `[shell_environment_policy]`, 파일 방식일 때 `auth.json` | 인증 정보 저장 방식, 셸 명령에 넘긴 환경 변수 범위 | [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md) |
| 6 | Cursor `hooks.json` 과 훅 스크립트가 남긴 기록 | 파일 읽기·셸 실행을 훅으로 기록하거나 막았는지 | [Cursor](../../02-artifacts/dev-agents/cursor.md) |
| 7 | 셸 프로필과 설정의 `env` 블록 | 환경 변수로 넣은 토큰과 API 키 | [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) |
| 8 | 데스크톱 앱 쿠키 DB 와 계정 식별자 | 앱에 로그인한 계정과 세션 쿠키 | [Claude](../../02-artifacts/chat-services/claude/index.md) |

### 도구별 인증 정보 위치

도구 자신의 인증 정보는 아래처럼 OS 와 설정에 따라 자리가 다릅니다.

| 도구 | Windows | macOS | Linux |
|---|---|---|---|
| Claude Code | `%USERPROFILE%\.claude\.credentials.json`, 사용자 프로필 폴더의 접근 권한을 그대로 물려받음 | 암호화된 macOS 키체인. 키체인에 쓰지 못하면(SSH 세션에서 잠겨 있을 때 등) `~/.claude/.credentials.json`(모드 `0600`) | `~/.claude/.credentials.json`, 모드 `0600` |
| Claude Code 의 Anthropic 프로필 | `%APPDATA%\Anthropic` 아래 `configs/`, 활성 프로필은 `active_config` | `~/.config/anthropic` | `~/.config/anthropic` |
| Codex CLI | `cli_auth_credentials_store` 가 `"file"` 이면 `CODEX_HOME/auth.json`, `"keyring"` 이면 OS 자격 증명 저장소, `"auto"` 는 OS 저장소를 쓰다가 못 쓰면 `auth.json`, `"ephemeral"` 은 실행 중 메모리에만 둠. OS 저장소의 항목 이름은 확인하지 못함 | 같음 | 같음 |
| Gemini CLI | 인증 정보 캐시 위치는 확인하지 못함 | 확인하지 못함 | 확인하지 못함 |
| Cursor | 자격 증명 저장 위치는 확인하지 못함 | 확인하지 못함 | 확인하지 못함 |

관찰한 PC 의 `.credentials.json` 에는 `claudeAiOauth` 아래 `accessToken`, `refreshToken`, `expiresAt`, `refreshTokenExpiresAt`, `scopes`, `subscriptionType`, `rateLimitTier` 키가 있었습니다. 같은 PC 의 `.codex` 폴더에는 `auth.json` 이 없었고, `.gemini` 폴더에서도 인증 정보 캐시로 보이는 파일은 보지 못했으며 `antigravity/installation_id` 만 있었습니다(확인 범위: Windows 11, 2026-09). `.credentials.json` 은 나이 기준 정리 대상이 아니라서 사용자가 지울 때까지 남습니다. 파일과 키체인의 보호 원리는 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html), [자격 증명 관리자와 볼트](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/credentials/credential-manager-windows-vault.html), [macOS 키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html)에서 다룹니다.

## 분석 흐름

1. **실행 기록에서 자격 증명 파일을 건드린 호출을 찾습니다.** 세션 기록의 도구 호출 `input` 에서 `.env`, `.credentials.json`, `auth.json`, 키 파일 이름 같은 경로와, 환경 변수를 출력하는 명령을 찾습니다. 그다음 짝이 되는 결과 항목의 `content` 와 `toolUseResult.stdout`·`stderr` 에 실제로 값이 찍혔는지 봅니다(키 이름은 확인 범위: Windows 11, 2026-09). 하위 에이전트 기록과 `tool-results/` 도 같이 찾아야 빠뜨리지 않습니다. 검색 결과를 보고서에 옮길 때는 값을 가립니다.
2. **기록 밖에 남은 사본을 찾습니다.** 사용자가 비밀 값을 붙여넣었다면 `paste-cache/` 에, 에이전트가 `.env` 같은 파일을 고쳤다면 `file-history/<session>/` 에 고치기 전 내용이 남을 수 있습니다. `history.jsonl` 의 `pastedContents` 항목에는 붙여넣은 내용이나 그 해시(`contentHash`)가 들어갑니다(확인 범위: Windows 11, 2026-09). 디버그를 켰던 세션이면 `~/.claude/debug/` 의 세션별 로그도 봅니다.
3. **당시 막아 둔 장치가 있었는지 봅니다.** Claude Code 문서는 권한 규칙으로 자격 증명 파일 읽기를 막으라고 권하고, 규칙은 `.claude/settings.json`·`.claude/settings.local.json` 의 `permissions` 에 적습니다. Codex 는 `[shell_environment_policy]` 로 셸 명령에 넘길 환경 변수를 정합니다. `ignore_default_excludes` 는 기본값이 `true` 라서 따로 설정하지 않으면 이름에 `KEY`·`SECRET`·`TOKEN` 이 든 환경 변수도 그대로 넘어가고, `false` 로 두었을 때만 이런 변수를 먼저 걸러 냅니다. `inherit`(`"core"`, `"none"`)와 제외·포함 규칙도 결과를 바꾸므로 설정 파일의 이 절을 그대로 옮겨 적습니다. Cursor 는 `beforeReadFile`·`beforeShellExecution` 훅이 파일 경로와 명령을 받아서, 이런 훅을 걸어 두었다면 그 스크립트가 남긴 기록이 가장 직접적인 증거가 됩니다.
4. **막는 장치가 실제로 작동했는지 확인합니다.** 규칙이나 훅이 설정돼 있어도 그 시각에 적용됐는지는 따로 봅니다. Claude Code 세션 기록에서는 훅 항목의 `exitCode`·`hookErrors`·`preventedContinuation` 으로 결과를 보고(확인 범위: Windows 11, 2026-09), Cursor 훅은 종료 코드 2 일 때만 막고 0 과 2 가 아닌 코드는 기본으로 통과시킨다는 점을 함께 적습니다.
5. **도구 자신의 인증 정보 상태를 적습니다.** 위 표의 위치에서 인증 파일이 있는지, 파일 시각이 언제인지, 접근 권한이 어떤지를 기록합니다. Claude Code 는 인증 수단의 우선순위가 클라우드 설정(`CLAUDE_CODE_USE_BEDROCK`·`_VERTEX`·`_FOUNDRY`) → `ANTHROPIC_AUTH_TOKEN` → `ANTHROPIC_API_KEY` → `apiKeyHelper` → `CLAUDE_CODE_OAUTH_TOKEN` → Anthropic 프로필·페더레이션 → `/login` 구독 OAuth 순이라서, 파일만 보지 말고 환경 변수와 설정의 `env` 블록도 봅니다. `claude setup-token` 은 1년짜리 토큰을 화면에 출력만 하고 저장하지 않으며 사용자가 직접 `CLAUDE_CODE_OAUTH_TOKEN` 으로 넣어 쓰기 때문에, 이 토큰은 셸 프로필이나 설정의 `env` 블록에서 찾습니다. `apiKeyHelper` 는 API 키를 돌려주는 셸 스크립트이고 기본 5분마다 다시 실행되어서(`CLAUDE_CODE_API_KEY_HELPER_TTL_MS`), 스크립트 파일과 그 스크립트가 키를 가져오는 곳을 함께 봅니다. `--debug` 로 실행한 세션이면 `~/.claude/debug/<session-id>.txt` 에 `Using Anthropic profile auth` 줄이 남아 프로필 인증을 썼는지 알려 줍니다.
6. **데스크톱 앱의 계정 흔적을 봅니다.** 관찰한 PC 의 Windows 스토어판 Claude 데스크톱 앱에는 `LocalCache/Roaming/Claude/Network/Cookies` 쿠키 DB 가 있었지만 열지 못했고, 따로 있는 `Partitions/cowork-file-preview/Network/Cookies` 의 `cookies` 표에 `host_key`, `name`, `value`, `encrypted_value`, `creation_utc`, `expires_utc`, `last_access_utc` 같은 칸이 있어 Chromium 쿠키 구조와 같았습니다. 계정 식별자는 `config.json` 의 `lastKnownAccountUuid`, `cowork-enabled-cli-ops.json` 의 `ownerAccountId` 에 있었습니다(확인 범위: Windows 11, 2026-09). 쿠키 DB 읽는 법은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)와 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)를 봅니다.
7. **값이 밖으로 나갔는지는 따로 확인합니다.** 자격 증명을 읽은 호출 뒤에 네트워크를 쓰는 명령이나 MCP 도구 호출이 이어졌는지 세션 기록에서 보고, [AI 서비스 도메인과 네트워크 기록](../../02-artifacts/network-enterprise/network-traces.md)과 [보안 제품이 남기는 AI 사용 기록](../../02-artifacts/network-enterprise/dlp-casb.md)으로 교차 확인합니다. 서비스 쪽 로그인·토큰 사용 기록은 [Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md)나 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 확인합니다.

## 흔한 오판

**인증 파일이 있다는 사실을 유출로 읽는 경우**가 있습니다. `.credentials.json` 이나 `auth.json` 은 도구가 정상적으로 로그인하면 생기는 파일이고, 유출을 말하려면 그 파일을 읽은 호출이나 복사한 흔적, 다른 곳에서 토큰을 쓴 서비스 쪽 기록이 있어야 합니다.

**macOS 에 파일이 없으면 인증 정보가 없다고 보는 경우**도 틀립니다. Claude Code 는 macOS 에서 키체인을 쓰고, 오히려 `~/.claude/.credentials.json` 이 macOS 에 있으면 키체인 쓰기가 거부된 상황이었을 수 있습니다.

**세션 기록에 값이 있으면 외부로 보냈다고 쓰는 경우**도 조심합니다. 기록은 에이전트가 그 값을 읽었거나 출력했다는 사실까지 보여 주고, 값이 어디까지 전달됐는지는 네트워크 기록이나 서비스 쪽 기록으로 따로 확인해야 합니다.

**Codex 의 환경 변수 제외 규칙을 파일 보호로 읽는 경우**가 있습니다. 이 규칙은 셸 명령에 넘기는 환경 변수만 거르고, 에이전트가 디스크의 `.env` 파일을 여는 일과는 관계가 없습니다. 게다가 기본 설정에서는 이름에 `KEY`·`SECRET`·`TOKEN` 이 든 변수도 걸러지지 않아서, 설정 파일에 `ignore_default_excludes = false` 가 없으면 이런 변수가 셸 명령에 넘어갔을 수 있다고 봅니다.

**Ollama 폴더의 키 쌍을 사용자 SSH 키로 보는 경우**도 있습니다. 관찰한 PC 의 `%USERPROFILE%\.ollama` 에는 `id_ed25519`·`id_ed25519.pub` 가 있었고(확인 범위: Windows 11, 2026-09), 이름이 SSH 키와 같아도 Ollama 폴더 안의 파일이라 사용자 SSH 키라고 단정하지 않습니다. 자세한 내용은 [Ollama](../../02-artifacts/local-ai/ollama.md)를 봅니다. 같은 PC 의 `~/.claude/daemon/control.key`·`pipe.key` 도 이름에 key 가 들어가지만 용도는 확인하지 못했습니다.

**로그아웃 뒤 흔적이 없다고 보는 경우**도 조심합니다. Claude Code 의 서버 관리 설정 캐시 `~/.claude/remote-settings.json` 은 로그아웃할 때 지워지지만, 세션 기록에 이미 적힌 값은 보관 기간 동안 그대로 남습니다. 보관과 삭제 규칙은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 보고서 문장 예

아래는 만든 예시이고, 사용자 이름·폴더 이름·시각은 모두 가짜 값입니다. 비밀 값 자체는 예시로도 적지 않습니다.

> 사용자 계정 `demo-user` 의 Claude Code 세션 기록에서 2026-08-20 05:11(UTC)에 `C:\work\sample-api\.env` 파일을 읽는 도구 호출 1건과 그 결과 항목이 확인됩니다. 결과 항목에는 이름이 `SAMPLE_DB_PASSWORD` 인 설정 줄과 값이 들어 있으며, 값은 이 보고서에서 가렸습니다. 같은 세션에서 이 호출 뒤에 네트워크를 쓰는 명령은 기록되어 있지 않습니다. 세션 기록만으로는 이 값이 다른 곳으로 전달됐는지 판단할 수 없어 네트워크 기록을 따로 검토했습니다.

> 같은 계정의 `%USERPROFILE%\.claude\.credentials.json` 은 수집 시점에 있었고, 설정 파일의 권한 규칙에는 `.env` 파일 읽기를 막는 항목이 없었습니다. 인증 파일을 읽거나 복사한 도구 호출은 조사 기간의 세션 기록에서 찾지 못했습니다.

## 함께 볼 페이지

- [AI 에이전트가 무엇을 실행했나](agent-actions.md) — 실행 기록을 찾고 읽는 절차
- [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) — AI 서비스 인증 정보의 일반 위치
- [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md), [Cursor](../../02-artifacts/dev-agents/cursor.md) — 도구별 저장 구조
- [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md) — 외부 내용에 이끌려 에이전트가 비밀 파일을 연 경우
- [기밀 자료를 AI에 넣었나](../data-leak/confidential-input.md) — 사람이 직접 비밀 값을 붙여넣은 경우
- [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html), [macOS 키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html) — OS 보호 원리

## 참고 문헌

1. Explore the .claude directory (Claude Code 문서) — https://code.claude.com/docs/en/claude-directory
2. Authentication (Claude Code 문서) — https://code.claude.com/docs/en/authentication
3. Advanced configuration (Codex 문서) — https://learn.chatgpt.com/docs/config-file/config-advanced
4. Hooks (Cursor 문서) — https://cursor.com/docs/agent/hooks
5. Authentication (Codex 문서) — https://learn.chatgpt.com/docs/auth
