---
title: "에이전트가 자격 증명을 건드렸나"
parent: "시나리오 · AI 에이전트"
nav_order: 980
---

# 에이전트가 자격 증명을 건드렸나 (Agent Credentials)

이 페이지는 흔적을 찾고 해석하는 방법만 다루고, 저장된 비밀 값을 꺼내거나 보호를 푸는 방법은 다루지 않습니다.

## 조사 질문

AI 에이전트가 비밀번호·API 키·토큰 같은 자격 증명(credential)을 읽거나 출력했는지, 그리고 에이전트 도구 자신의 인증 정보가 어디에 어떤 방식으로 저장돼 있었는지를 밝히는 조사입니다. 질문은 두 갈래입니다. 하나는 에이전트가 사용자 프로젝트의 `.env` 파일이나 키 파일을 열어 본 경우이고, 다른 하나는 에이전트 도구나 로컬 LLM 앱에 넣어 둔 로그인 토큰·API 키가 새어 나갔는지 묻는 경우입니다.

두 갈래 모두 에이전트가 무엇을 실행했는지 먼저 알아야 합니다. 실행 기록을 찾고 읽는 절차는 [AI 에이전트가 무엇을 실행했나](agent-actions.md)를 따르고, 이 페이지는 자격 증명과 관련된 부분만 다룹니다. 인증 정보가 남는 곳의 일반 원리는 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

## 먼저 확인할 것

**증거 자체에 비밀 값이 들어 있습니다.** Claude Code 는 세션 기록과 프롬프트 기록을 암호화하지 않고 OS 파일 권한으로만 보호합니다. 도구가 `.env` 파일을 읽거나 명령이 자격 증명을 출력하면 그 값이 `projects/<project>/<session>.jsonl` 에 그대로 적힙니다[1]. 그래서 수집본을 다루는 사람과 보관 위치를 제한하고, 보고서에는 값을 가려서 씁니다.

**무엇을 모을지 먼저 정합니다.** 공개 도구마다 기준이 다릅니다.

- coding-agent-forensics 는 `auth.json`, `.credentials.json`, API 키가 든 설정 파일을 모으지 말라고 권합니다. 조사에 보탬이 되지 않고 들고 있는 비밀만 늘린다는 이유입니다[8].
- ccfx 는 `.credentials.json` 의 존재·크기·수정 시각만 기록하고 토큰 값은 읽지 않습니다. 다만 `-ac` 옵션으로 만드는 `claude-acquisition.zip` 은 폴더를 바이트 단위로 복사하므로 `.credentials.json` 의 OAuth 토큰이 평문으로 들어가고, `--redact-pii` 도 이 압축본에는 적용되지 않습니다[7].
- claude-forensics 는 `paste-cache/` 의 붙여넣은 내용이 100,000바이트(`_PASTE_INLINE_MAX_BYTES`) 이하면 결과 파일 `paste-cache.jsonl` 의 `content` 칸에 그대로 넣습니다[6]. 도구가 만든 결과물에도 비밀 값이 옮겨 갈 수 있습니다.

인증 파일은 값 대신 있는지·시각·권한만 적는 방식으로 충분한 경우가 많습니다. 통째로 복사해야 한다면 압축본을 암호화해 보관하고 그 사실을 기록합니다.

**OS 를 적어 둡니다.** 같은 도구라도 Windows·Linux 에서는 파일에, macOS 에서는 키체인(Keychain)에 인증 정보를 둘 수 있습니다[2].

**설정 폴더가 옮겨졌는지 봅니다.** Claude Code 는 `CLAUDE_CONFIG_DIR`, Codex 는 `CODEX_HOME` 환경 변수로 설정 폴더를 옮길 수 있고, 그러면 인증 파일도 그 폴더에 생깁니다[2][5].

**도구 버전과 날짜를 적습니다.** 인증 파일 이름과 저장 방식은 판마다 바뀔 수 있습니다. 아래 표는 2026년 9월 기준입니다.

**Windows 에 어떤 폴더가 생기는지는 검체로 봅니다.** 2026년 중반 Windows 판 Claude Code 는 `history.jsonl`, `shell-snapshots/`, `paste-cache/`, `file-history/` 를 쓰지 않는 것으로 보인다는 분석이 있지만[6], 그 뒤 Windows 11 에서 `history.jsonl` 과 그 안의 `pastedContents` 항목이 남은 사례가 있습니다. 판에 따라 다르므로 검체에서 폴더가 실제로 있는지부터 적습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | Claude Code 세션 기록과 하위 에이전트 기록 | 에이전트가 연 파일 경로와 명령, 그 출력에 섞인 값 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 2 | 큰 도구 출력 `.../<session>/tool-results/`, 붙여넣기 `~/.claude/paste-cache/`, 수정 전 사본 `~/.claude/file-history/<session>/` | 세션 기록 밖에 따로 저장된 출력·붙여넣은 내용·고치기 전 파일 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 3 | `~/.claude/shell-snapshots/*.sh` | Bash 도구가 쓴 셸 환경. `export` 줄에 토큰이 남을 수 있음[6] | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 4 | 권한 규칙 `.claude/settings.json`, `.claude/settings.local.json` 의 `permissions` | 자격 증명 파일 읽기를 막아 두었는지 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 5 | Claude Code 인증 파일 `.credentials.json` 과 macOS 키체인 항목 | 도구 자신의 로그인 정보가 있는 곳 | [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) |
| 6 | `~/.claude/backups/.claude.json.backup.*` 의 `oauthAccount` | 로그인 계정의 이메일, 조직 UUID·이름·역할[7] | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 7 | Codex `config.toml` 의 `cli_auth_credentials_store`, `mcp_oauth_credentials_store`, `[shell_environment_policy]`, 모델 제공자·MCP 서버 설정, 그리고 `auth.json`·`.credentials.json` | 인증 정보 저장 방식, 셸 명령에 넘긴 환경 변수 범위, 설정 파일에 직접 적은 토큰 | [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md) |
| 8 | Cursor `hooks.json` 과 훅 스크립트가 남긴 기록 | 파일 읽기·셸 실행을 훅으로 기록하거나 막았는지 | [Cursor](../../02-artifacts/dev-agents/cursor.md) |
| 9 | 셸 프로필과 설정의 `env` 블록 | 환경 변수로 넣은 토큰과 API 키 | [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) |
| 10 | 데스크톱 앱 쿠키 DB, Cowork 세션 메타데이터 | 앱에 로그인한 계정과 세션 쿠키, 계정 이메일 | [Claude](../../02-artifacts/chat-services/claude/index.md) |
| 11 | 로컬 LLM 앱의 설정 파일·DB·로그 | 사용자가 앱에 넣은 클라우드 서비스 API 키 | 아래 "로컬 LLM 앱에 넣은 API 키" |

### 도구별 인증 정보 위치

| 도구 | Windows | macOS | Linux |
|---|---|---|---|
| Claude Code | `%USERPROFILE%\.claude\.credentials.json`. 사용자 프로필 폴더의 접근 권한을 그대로 물려받음[2] | 암호화된 macOS 키체인. 키체인에 쓰지 못하면(SSH 세션에서 잠겨 있을 때 등) `~/.claude/.credentials.json`(모드 `0600`)[2] | `~/.claude/.credentials.json`, 모드 `0600`[2] |
| Claude Code 의 Anthropic 프로필 | `%APPDATA%\Anthropic` 아래 `configs/`, 활성 프로필은 `active_config`[2] | `~/.config/anthropic`[2] | `~/.config/anthropic`[2] |
| Codex CLI 로그인 | `cli_auth_credentials_store` 로 정함. 기본값 `"file"` 이면 `CODEX_HOME/auth.json`, `"keyring"` 이면 OS 자격 증명 저장소(못 쓰면 실패), `"auto"` 는 OS 저장소를 쓰다가 못 쓰면 `CODEX_HOME` 의 파일, `"ephemeral"` 은 실행 중 메모리에만 둠[9][5] | 같음 | 같음 |
| Codex CLI 의 MCP OAuth 토큰 | `mcp_oauth_credentials_store` 로 정함. 기본값 `"auto"` 는 OS 저장소를 쓰다가 못 쓰면 `CODEX_HOME/.credentials.json`, `"file"` 은 이 파일, `"keyring"` 은 OS 저장소만 씀[9] | 같음 | 같음 |
| Cursor CLI | 세션별 `~/.cursor/chats/<workspace-hash>/<agent-id>/store.db` 에 `blobs`·`meta` 표가 있음. 이 저장소의 `blobEncryptionKey` 는 agentsview 분석기가 읽지 않음[10]. 계정 로그인 정보가 저장되는 곳은 공개된 분석 자료가 없어 검체로 확인해야 함 | 같음 | 같음 |
| Gemini CLI | 인증 정보 캐시 위치는 공개된 분석 자료가 없어 검체로 확인해야 함 | 같음 | 같음 |

Codex 의 OS 자격 증명 저장소 안 항목 이름은 공개된 자료가 없어 검체의 자격 증명 관리자나 키체인에서 확인합니다. `.credentials.json` 은 같은 사용자로 실행되는 다른 프로그램도 읽을 수 있고, 키링에 둔 MCP 토큰은 사용자가 OS 수준에서 따로 허용하지 않는 한 Codex 만 읽습니다[9].

Claude Code `.credentials.json` 의 `claudeAiOauth` 아래에는 `accessToken`, `refreshToken`, `expiresAt`, `refreshTokenExpiresAt`, `scopes`, `subscriptionType`, `rateLimitTier` 키가 있습니다(Windows 11 기준). Codex 는 기본값이 `"file"` 이므로 `.codex` 폴더에 `auth.json` 이 없으면 로그인하지 않았거나, 설정으로 저장 방식을 바꿨거나, 파일을 지운 경우를 차례로 따집니다. `.credentials.json` 은 나이 기준 정리 대상이 아니라서 사용자가 지울 때까지 남습니다[1]. 파일과 키체인의 보호 원리는 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/protection/data-protection-api/index.html), [자격 증명 관리자와 볼트](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/credentials/credential-manager-windows-vault.html), [macOS 키체인](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/protection/keychain/index.html)에서 다룹니다.

### Codex 설정 파일에 직접 남는 인증 정보

Codex 는 `auth.json` 말고도 `config.toml` 의 여러 항목으로 인증 정보를 받습니다. 아래 항목은 Codex 설정 스키마에 정해져 있습니다[9].

| 항목 | 값이 있는 곳 |
|---|---|
| 모델 제공자의 `experimental_bearer_token` | `config.toml` 안에 토큰이 그대로 적힘. 보안상 `env_key` 쓰기를 권장함 |
| 모델 제공자의 `env_key`, `env_http_headers` | 설정에는 환경 변수 이름만 있고 값은 그 환경 변수에 있음 |
| 모델 제공자의 `http_headers` | 설정 안에 헤더 값이 그대로 적힘 |
| 모델 제공자의 `auth`(`command`, `args`, `cwd`) | 토큰을 돌려주는 명령. 결과는 기본 300000ms(`refresh_interval_ms`) 동안 재사용 |
| 모델 제공자의 `requires_openai_auth = true` | 로그인 방식과 토큰·키를 `auth.json` 에 둠 |
| MCP 서버의 `env`, `http_headers` | 설정 안에 값이 그대로 적힐 수 있음 |
| MCP 서버의 `bearer_token_env_var`, `env_http_headers` | 설정에는 환경 변수 이름만 있음 |

이름만 적힌 항목은 그 이름을 셸 프로필과 시스템 환경 변수에서 다시 찾아야 값의 출처가 드러납니다.

### 로컬 LLM 앱에 넣은 API 키

로컬 LLM 앱은 사용자가 넣은 클라우드 서비스 API 키를 앱 폴더에 보관합니다. 이런 키는 그 자체로 증거 가치가 크지는 않지만, 서비스 회사에 서버 쪽 자료를 요청할 때 쓸 수 있습니다[11]. API 키로 쓴 대화는 로컬 앱이 대화 기록을 들고 있다가 호출마다 다시 보내므로, 클라우드 쪽에는 대개 대화 맥락이 남지 않습니다[11]. 아래 위치는 LangurTrace 시험(Windows 11 Pro 24H2)에 쓴 앱 판 기준이고, 지금 판은 저장 방식이 다를 수 있습니다[11].

| 앱(시험한 판) | 위치 | 키가 든 곳 | 자세히 |
|---|---|---|---|
| Chatbox 1.11.8 | `%APPDATA%\xyz.chatboxapp.app\config.json`, 같은 폴더의 `config-backup-*.json` | `settings` 의 `openaiKey`, `azureApikey`, `claudeApiKey`, `geminiAPIKey`, `groqAPIKey`, `deepseekAPIKey`, `siliconCloudKey`, `perplexityApiKey`, `xAIKey`[12] | [Chatbox](../../02-artifacts/local-ai/chatbox.md) |
| Msty 1.8.5 | `%APPDATA%\Msty\msty.db` | `api_keys` 표의 `provider`, `key`, `created_at`[11] | [Msty](../../02-artifacts/local-ai/msty.md) |
| Jan 0.5.16 | `%APPDATA%\Jan\data\cortex.db`, `%APPDATA%\Jan\data\logs\cortex.log` | `engines` 표[12], 그리고 로그에 평문으로 남은 API 키. 로그에는 지운 키도 남음[11] | [Jan](../../02-artifacts/local-ai/jan.md) |
| GPT4All 3.10.0 | `%LOCALAPPDATA%\nomic.ai\GPT4ALL\*.rmodel` | 원격 모델 설정 JSON 의 `apiKey`[12] | [GPT4All](../../02-artifacts/local-ai/gpt4all.md) |

Chatbox 의 `settings` 에는 `userAvatarKey`, `defaultAssistantAvatarKey` 처럼 이름에 Key 가 들어가지만 API 키가 아닌 항목도 있습니다. LangurTrace 의 Chatbox 분석기는 이름에 `key` 가 들어간 항목을 모두 "API Key" 로 뽑으므로[12], 결과를 옮길 때 항목 이름을 하나씩 봅니다. `config-backup-*.json` 에는 지난 시점의 키가 남아 있을 수 있어서 `config.json` 과 함께 봅니다.

## 분석 흐름

1. **실행 기록에서 자격 증명 파일을 건드린 호출을 찾습니다.** 세션 기록의 도구 호출 `input` 에서 `.env`, `.credentials.json`, `auth.json`, 키 파일 이름 같은 경로와, 환경 변수를 출력하는 명령을 찾습니다. 그다음 짝이 되는 결과 항목의 `content` 와 `toolUseResult.stdout`·`stderr` 에 실제로 값이 찍혔는지 봅니다(키 이름은 Windows 11 기준). 하위 에이전트 기록과 `tool-results/` 도 같이 찾아야 빠뜨리지 않습니다. 검색 결과를 보고서에 옮길 때는 값을 가립니다.

2. **기록 밖에 남은 사본을 찾습니다.** 사용자가 비밀 값을 붙여넣었다면 `paste-cache/<hash>.txt` 에 남을 수 있고, 파일 이름은 Claude Code 가 붙인 내용 해시입니다[6]. `history.jsonl` 의 `pastedContents` 항목에는 붙여넣은 내용이나 그 해시(`contentHash`)가 들어가서 어느 프롬프트에서 붙여넣었는지 이을 수 있습니다. 에이전트가 `.env` 같은 파일을 고쳤다면 `file-history/<session>/<hash>@v<N>` 에 고치기 전 판이 남을 수 있습니다[6]. `shell-snapshots/` 의 `snapshot-zsh-<ms>-<rand>.sh`(bash 면 `snapshot-bash-`)는 Bash 도구가 쓴 셸 환경이고, 파일 이름의 밀리초가 Claude Code 를 실행한 시각입니다[6]. 이 파일의 `export` 줄에 토큰이 남을 수 있어서 claude-forensics 는 이 줄을 `exports` 칸으로 뽑습니다[6]. 디버그를 켰던 세션이면 `~/.claude/debug/` 의 세션별 로그도 봅니다.

3. **당시 막아 둔 장치가 있었는지 봅니다.** Claude Code 는 권한 규칙으로 자격 증명 파일 읽기를 막을 수 있고, 규칙은 `.claude/settings.json`·`.claude/settings.local.json` 의 `permissions` 에 적습니다[1]. Codex 는 `[shell_environment_policy]` 로 셸 명령에 넘길 환경 변수를 정합니다. `ignore_default_excludes` 의 기본값이 `true` 라서, 따로 설정하지 않으면 이름에 `KEY`·`SECRET`·`TOKEN` 이 든 환경 변수도 그대로 넘어가고, `false` 로 두었을 때만 이런 변수를 먼저 걸러 냅니다[3]. `inherit` 는 `"all"`(부모 프로세스 환경 전부), `"core"`(플랫폼 기본 변수), `"none"`(물려받지 않음) 중 하나이고, 제외·포함 규칙은 예전 형식 `exclude`·`include_only` 나 새 형식 `filters` 로 적습니다[9]. 이 값들이 결과를 바꾸므로 설정 파일의 이 절을 그대로 옮겨 적습니다. Cursor 는 `beforeReadFile`·`beforeShellExecution` 훅이 파일 경로와 명령을 받습니다[4]. 이런 훅을 걸어 두었다면 그 스크립트가 남긴 기록이 가장 직접적인 증거가 됩니다.

4. **막는 장치가 실제로 작동했는지 확인합니다.** 규칙이나 훅이 설정돼 있어도 그 시각에 적용됐는지는 따로 봅니다. Claude Code 세션 기록에서는 훅 항목의 `exitCode`·`hookErrors`·`preventedContinuation` 으로 결과를 봅니다. Cursor 훅은 종료 코드 2 일 때만 막고, 0 과 2 가 아닌 코드는 기본으로 통과시킵니다[4].

5. **도구 자신의 인증 정보 상태를 적습니다.** 위 표의 위치에서 인증 파일이 있는지, 파일 시각이 언제인지, 접근 권한이 어떤지를 기록합니다. Claude Code 는 인증 수단의 우선순위가 클라우드 설정(`CLAUDE_CODE_USE_BEDROCK`·`_VERTEX`·`_FOUNDRY`) → `ANTHROPIC_AUTH_TOKEN` → `ANTHROPIC_API_KEY` → `apiKeyHelper` → `CLAUDE_CODE_OAUTH_TOKEN` → Anthropic 프로필·페더레이션 → `/login` 구독 OAuth 순이라서[2], 파일만 보지 말고 환경 변수와 설정의 `env` 블록도 봅니다. `claude setup-token` 은 1년짜리 토큰을 화면에 출력만 하고 저장하지 않으며, 사용자가 직접 `CLAUDE_CODE_OAUTH_TOKEN` 으로 넣어 씁니다[2]. 그래서 이 토큰은 셸 프로필이나 설정의 `env` 블록에서 찾습니다. `apiKeyHelper` 는 API 키를 돌려주는 셸 스크립트이고 기본 5분마다 다시 실행되므로(`CLAUDE_CODE_API_KEY_HELPER_TTL_MS`)[2], 스크립트 파일과 그 스크립트가 키를 가져오는 곳을 함께 봅니다. `--debug` 로 실행한 세션이면 `~/.claude/debug/<session-id>.txt` 에 `Using Anthropic profile auth` 줄이 남아 프로필 인증을 썼는지 알려 줍니다[2]. Codex 는 위 "Codex 설정 파일에 직접 남는 인증 정보" 표의 항목을 모두 봅니다.

6. **계정 흔적을 모읍니다.** `~/.claude/backups/.claude.json.backup.*` 의 `oauthAccount` 에는 `accountUuid`, `emailAddress`, `organizationUuid`, `organizationName`, `organizationType`, `organizationRole` 이 들어 있습니다[7]. Claude 데스크톱 앱 폴더의 Cowork 세션 메타데이터 `local-agent-mode-sessions/<orgUuid>/<accountUuid>/local_<sid>.json` 에는 `emailAddress`·`accountName` 이 있습니다[6]. Windows 스토어판 Claude 데스크톱 앱에는 `LocalCache/Roaming/Claude/Network/Cookies` 쿠키 DB 가 있고, 따로 있는 `Partitions/cowork-file-preview/Network/Cookies` 의 `cookies` 표에는 `host_key`, `name`, `value`, `encrypted_value`, `creation_utc`, `expires_utc`, `last_access_utc` 같은 칸이 있어 Chromium 쿠키 구조와 같습니다. 계정 식별자는 `config.json` 의 `lastKnownAccountUuid`, `cowork-enabled-cli-ops.json` 의 `ownerAccountId` 에 있습니다. 쿠키 DB 읽는 법은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html)와 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)를 봅니다. 이 흔적은 어느 계정의 인증 정보가 그 기기에 있었는지 알려 주고, 누가 키보드 앞에 있었는지는 [그 대화를 한 사람이 누구인가](../attribution/user-attribution.md)의 방법으로 따로 좁힙니다.

7. **로컬 LLM 앱의 키를 확인합니다.** 에이전트 도구 말고도 검체에 로컬 LLM 앱이 있으면 위 "로컬 LLM 앱에 넣은 API 키" 표의 위치를 봅니다. 어느 서비스의 키가 언제 등록됐는지(Msty `api_keys.created_at` 등)를 적고, 키 값은 가립니다. 이 키로 서버 쪽 자료를 받으려면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 절차를 밟습니다.

8. **값이 밖으로 나갔는지는 따로 확인합니다.** 자격 증명을 읽은 호출 뒤에 네트워크를 쓰는 명령이나 MCP 도구 호출이 이어졌는지 세션 기록에서 보고, [AI 서비스 도메인과 네트워크 기록](../../02-artifacts/network-enterprise/network-traces.md)과 [보안 제품이 남기는 AI 사용 기록](../../02-artifacts/network-enterprise/dlp-casb.md)으로 교차 확인합니다. MCP 호출 기록은 [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md)에서 다룹니다. 서비스 쪽 로그인·토큰 사용 기록은 [Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md)나 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 확인합니다.

## 흔한 오판

**인증 파일이 있다는 사실을 유출로 읽는 경우**가 있습니다. `.credentials.json` 이나 `auth.json` 은 도구에 정상적으로 로그인하면 생기는 파일입니다. 유출을 말하려면 그 파일을 읽은 호출이나 복사한 흔적, 다른 곳에서 토큰을 쓴 서비스 쪽 기록이 있어야 합니다.

**macOS 에 파일이 없으면 인증 정보가 없다고 보는 경우**도 틀립니다. Claude Code 는 macOS 에서 키체인을 씁니다. 오히려 `~/.claude/.credentials.json` 이 macOS 에 있으면 키체인 쓰기가 거부된 상황이었을 수 있습니다[2]. Codex 도 설정에 따라 OS 저장소를 쓰므로 `auth.json` 이 없다는 것만으로 로그인하지 않았다고 쓰지 않습니다.

**Codex 의 두 `.credentials.json` 을 헷갈리는 경우**가 있습니다. Codex 의 `CODEX_HOME/.credentials.json` 은 MCP 서버 OAuth 토큰을 담는 파일이고[9], Claude Code 의 `~/.claude/.credentials.json` 과 이름만 같습니다. 어느 폴더의 파일인지 경로째 적습니다.

**세션 기록에 값이 있으면 외부로 보냈다고 쓰는 경우**도 조심합니다. 기록은 에이전트가 그 값을 읽었거나 출력했다는 사실까지 보여 줍니다. 값이 어디까지 전달됐는지는 네트워크 기록이나 서비스 쪽 기록으로 따로 확인해야 합니다.

**Codex 의 환경 변수 제외 규칙을 파일 보호로 읽는 경우**가 있습니다. 이 규칙은 셸 명령에 넘기는 환경 변수만 거르고, 에이전트가 디스크의 `.env` 파일을 여는 일과는 관계가 없습니다. 게다가 기본 설정에서는 이름에 `KEY`·`SECRET`·`TOKEN` 이 든 변수도 걸러지지 않습니다[3]. 그래서 설정 파일에 `ignore_default_excludes = false` 가 없으면 이런 변수가 셸 명령에 넘어갔을 수 있다고 봅니다.

**Ollama 폴더의 키 쌍을 사용자 SSH 키로 보는 경우**도 있습니다. `%USERPROFILE%\.ollama` 에는 `id_ed25519`·`id_ed25519.pub` 가 있을 수 있습니다. 이름이 SSH 키와 같아도 Ollama 폴더 안의 파일이라 사용자 SSH 키라고 단정하지 않습니다. 자세한 내용은 [Ollama](../../02-artifacts/local-ai/ollama.md)를 봅니다.

**분석 도구의 "API Key" 출력을 모두 키로 세는 경우**도 있습니다. 앞에서 적은 대로 Chatbox 설정의 아바타 항목처럼 이름에만 Key 가 들어간 값이 섞여 나옵니다.

**로그아웃 뒤 흔적이 없다고 보는 경우**도 조심합니다. Claude Code 의 서버 관리 설정 캐시 `~/.claude/remote-settings.json` 은 로그아웃할 때 지워지지만, 세션 기록에 이미 적힌 값은 보관 기간 동안 그대로 남습니다[1]. Jan 처럼 로그에 키를 평문으로 적는 앱은 앱에서 키를 지워도 로그에 남습니다[11]. 보관과 삭제 규칙은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 보고서 문장 예

아래는 만든 예시이고, 사용자 이름·폴더 이름·시각은 모두 가짜 값입니다. 비밀 값 자체는 예시로도 적지 않습니다.

> 사용자 계정 `demo-user` 의 Claude Code 세션 기록에서 2026-08-20 05:11(UTC)에 `C:\work\sample-api\.env` 파일을 읽는 도구 호출 1건과 그 결과 항목이 확인됩니다. 결과 항목에는 이름이 `SAMPLE_DB_PASSWORD` 인 설정 줄과 값이 들어 있으며, 값은 이 보고서에서 가렸습니다. 같은 세션에서 이 호출 뒤에 네트워크를 쓰는 명령은 기록되어 있지 않습니다. 세션 기록만으로는 이 값이 다른 곳으로 전달됐는지 판단할 수 없어 네트워크 기록을 따로 검토했습니다.

> 같은 계정의 `%USERPROFILE%\.claude\.credentials.json` 은 수집 시점에 있었고, 파일 내용은 수집하지 않고 존재와 수정 시각만 기록했습니다. 설정 파일의 권한 규칙에는 `.env` 파일 읽기를 막는 항목이 없었습니다. 조사 기간의 세션 기록에는 인증 파일을 읽거나 복사한 도구 호출이 기록되어 있지 않습니다.

> 같은 기기의 `%APPDATA%\Msty\msty.db` 에는 `api_keys` 표에 클라우드 서비스 키 1건이 2026-08-18 에 등록된 것으로 기록되어 있습니다. 키 값은 이 보고서에서 가렸습니다.

## 함께 볼 페이지

- [AI 에이전트가 무엇을 실행했나](agent-actions.md) — 실행 기록을 찾고 읽는 절차
- [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) — AI 서비스 인증 정보의 일반 위치
- [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md), [Cursor](../../02-artifacts/dev-agents/cursor.md), [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md) — 도구별 저장 구조
- [Chatbox](../../02-artifacts/local-ai/chatbox.md), [Msty](../../02-artifacts/local-ai/msty.md), [Jan](../../02-artifacts/local-ai/jan.md), [GPT4All](../../02-artifacts/local-ai/gpt4all.md) — 로컬 LLM 앱의 저장 구조
- [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) — 수집 범위를 정하는 법
- [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md) — 외부 내용에 이끌려 에이전트가 비밀 파일을 연 경우
- [기밀 자료를 AI에 넣었나](../data-leak/confidential-input.md) — 사람이 직접 비밀 값을 붙여넣은 경우
- [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/protection/data-protection-api/index.html), [macOS 키체인](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/protection/keychain/index.html) — OS 보호 원리

## 참고 문헌

1. Explore the .claude directory (Claude Code 문서) — https://code.claude.com/docs/en/claude-directory
2. Authentication (Claude Code 문서) — https://code.claude.com/docs/en/authentication
3. Advanced configuration (Codex 문서) — https://learn.chatgpt.com/docs/config-file/config-advanced
4. Hooks (Cursor 문서) — https://cursor.com/docs/agent/hooks
5. Authentication (Codex 문서) — https://learn.chatgpt.com/docs/auth
6. forensicdave/claude-forensics (v0.1.1, 마지막 커밋 2026-06-16) — https://github.com/forensicdave/claude-forensics , `README.md`, `docs/claude_forensics.md`, `claude_forensics.py`
7. fkasasagi/ccfx (2026-08-18 커밋 기준) — https://github.com/fkasasagi/ccfx , `README.en.md`, `collector/backups.go`
8. Shorton88/coding-agent-forensics (2026-08-29 커밋 기준) — https://github.com/Shorton88/coding-agent-forensics , `README.md`
9. openai/codex (커밋 406dc92) — https://github.com/openai/codex , `codex-rs/core/config.schema.json`
10. kenn-io/agentsview — https://github.com/kenn-io/agentsview , `docs/internal/session-format-sources.md`(last_edited 2026-09-11), `internal/parser/cursor_store.go`
11. Sungjo Jeong, Sangjin Lee, Jungheum Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987, https://doi.org/10.1016/j.fsidi.2025.301987
12. jeongramon/LangurTrace (2025-07-30 커밋 기준) — https://github.com/jeongramon/LangurTrace , `src/apps/*.py`, `src/reporter/chatbox/config_reporter.py`, `src/reporter/jan/configuration_reporter.py`, `src/reporter/gpt4all/configuration_reporter.py`, `sample_dataset/collect/C/Users/USER/AppData/Roaming/xyz.chatboxapp.app/`
