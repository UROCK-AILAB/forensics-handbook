---
title: "API 키와 토큰이 남는 곳"
parent: "기반 · 저장 구조"
nav_order: 30
---

# API 키와 토큰이 남는 곳 (API Keys·Tokens)

AI 도구와 앱은 로그인 토큰과 API 키를 평문 설정 파일, 앱 데이터베이스의 필드, OS 자격 증명 저장소, 로그와 대화 기록 가운데 한 곳 이상에 남깁니다. 어디에 두는지는 도구·판·설정마다 달라서, 파일이 없다는 사실만으로 로그인하지 않았다고 쓸 수 없습니다.

이 페이지의 예시 값은 모두 만든 예시입니다.

## 이 형식을 쓰는 아티팩트

키와 토큰이 남는 곳은 네 무리로 나뉩니다. 첫째는 터미널에서 도는 개발 도구([Claude Code](../../02-artifacts/dev-agents/claude-code/index.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md), [Cursor](../../02-artifacts/dev-agents/cursor.md))입니다. 둘째는 클라우드 모델을 API 키로 불러 쓰는 로컬 AI 앱([Chatbox](../../02-artifacts/local-ai/chatbox.md), [Msty](../../02-artifacts/local-ai/msty.md), [Jan](../../02-artifacts/local-ai/jan.md), [GPT4All](../../02-artifacts/local-ai/gpt4all.md), [AnythingLLM](../../02-artifacts/local-ai/anythingllm.md), [Ollama](../../02-artifacts/local-ai/ollama.md))입니다. 셋째는 채팅 서비스의 데스크톱·모바일 앱이고, 넷째는 [AI 에이전트 브라우저](../../02-artifacts/agentic-services/ai-browsers.md)입니다.

파일 구조는 각 페이지에서 자세히 다룹니다. 이 페이지는 키와 토큰이 남는 자리를 한곳에 모으고, 보고서에서 어떻게 다룰지 기준을 정합니다. 에이전트가 사용자의 `.env` 나 키 파일을 읽거나 출력했는지 따지는 흐름은 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md) 에 있습니다.

## 구조

### 남는 방식

| 방식 | 예 | 읽을 때 조심할 점 |
|---|---|---|
| 평문 설정 파일 | Claude Code `.credentials.json`[2], Codex `auth.json`[3], Chatbox `config.json`[8], GPT4All `.rmodel`[7][8] | 파일 권한 말고는 보호가 없어서 이미지 사본에서 바로 읽힙니다 |
| 앱 데이터베이스의 필드 | Msty `api_keys.key`, Jan `engines.api_key`[7], Character.AI `RKStorage`[9] | 필드 이름이 "key" 라도 값이 평문인지는 실제 데이터로 확인합니다 |
| OS 자격 증명 저장소 | macOS 키체인(Claude Code)[1], Codex 의 `keyring`·`auto` 설정[6] | 사용자 폴더의 파일 목록에는 보이지 않습니다 |
| 로그·대화 기록 속 사본 | Jan `cortex.log`[7], Claude Code 세션 기록[2] | 앱 설정에서 키를 지워도 사본이 남을 수 있습니다 |

### 개발 도구

| 도구 | 남는 곳 | 저장 방식을 정하는 것 | 근거 |
|---|---|---|---|
| Claude Code 로그인 | Windows·Linux `~/.claude/.credentials.json`. macOS 는 키체인이고, 키체인에 쓰지 못하면 `~/.claude/.credentials.json`(모드 0600) | `CLAUDE_CONFIG_DIR` 로 폴더를 옮기면 키체인 항목도 따로 생김 | [1][2] |
| Claude Code 계정 정보 | `~/.claude/backups/.claude.json.backup.*` 에 계정 이메일, 조직 UUID, 구독 정보 | 없음 | [10][11] |
| Codex CLI 로그인 | `CODEX_HOME/auth.json`(`CODEX_HOME` 기본값 `~/.codex`) 또는 OS 자격 증명 저장소 | `cli_auth_credentials_store`. 스키마 설명의 기본값은 `file` | [3][6] |
| Codex CLI 의 MCP OAuth 토큰 | OS 자격 증명 저장소. 쓸 수 없으면 `CODEX_HOME/.credentials.json` | `mcp_oauth_credentials_store`. 스키마 설명의 기본값은 `auto` | [6] |
| Codex CLI 설정에 직접 적은 값 | `config.toml` 의 모델 제공자 `experimental_bearer_token`·`http_headers`, MCP 서버 `env`·`http_headers` | 사용자가 직접 적음 | [6] |
| Ollama | `C:\Users\<username>\.ollama\id_ed25519.pub`, macOS `~/.ollama/id_ed25519.pub`, Linux `/usr/share/ollama/.ollama/id_ed25519.pub` | 없음 | [4] |

**Claude Code.** Windows·Linux 의 `.credentials.json` 은 따로 암호화하지 않고 사용자 프로필 폴더의 접근 권한을 따릅니다[1][2]. 이 파일은 최상위 키 `claudeAiOauth` 아래에 `accessToken`, `refreshToken`, `expiresAt`, `refreshTokenExpiresAt`, `scopes`, `subscriptionType`, `rateLimitTier` 를 담습니다. 파일 짜임과 헥스 예시는 [Claude Code — Windows](../../02-artifacts/dev-agents/claude-code/windows.md) 에 있습니다. 키체인 항목의 서비스 이름은 공개 문서에 없어서 실제 기기의 키체인 목록에서 확인해야 합니다.

Claude Code 는 파일 말고도 인증 정보를 받는 길이 여럿이고, 클라우드 공급자 변수, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_API_KEY`, `apiKeyHelper`, `CLAUDE_CODE_OAUTH_TOKEN`, Anthropic 프로필, `/login` 구독 로그인 순서로 먼저 있는 것을 씁니다[1]. `apiKeyHelper` 는 셸 스크립트를 실행해 키를 받고 기본 5분마다 다시 실행합니다[1]. 설정에 이 키가 있으면 스크립트 파일도 함께 확보합니다.

**Codex CLI.** 로그인 정보를 둘 곳은 `cli_auth_credentials_store` 로 정합니다[3][6].

| 값 | 저장하는 곳 |
|---|---|
| `file` | `CODEX_HOME/auth.json`. 스키마 설명이 기본값으로 적은 값 |
| `keyring` | OS 자격 증명 저장소. 저장소를 쓸 수 없으면 실패 |
| `auto` | 저장소를 쓸 수 있으면 저장소, 아니면 `CODEX_HOME` 의 파일 |
| `ephemeral` | 실행 중인 프로세스 메모리에만 |

MCP 서버의 OAuth 토큰은 `mcp_oauth_credentials_store` 가 따로 정하고, 값은 `auto`, `file`, `keyring` 세 가지입니다[6]. `.credentials.json` 은 같은 사용자로 실행되는 다른 프로그램도 읽을 수 있고, 저장소에 둔 토큰은 사용자가 OS 에서 따로 허용하지 않는 한 Codex 만 읽습니다[6]. `auto` 에서는 MCP 클라이언트가 한 저장소에서 토큰을 읽으면, 그 클라이언트가 실행되는 동안 같은 저장소를 계속 씁니다[6]. `auth.json` 에는 접근 토큰이 들어 있어서 비밀번호처럼 다룹니다[3].

`config.toml` 에는 값이 그대로 적히는 필드와 환경 변수 이름만 적히는 필드가 섞여 있습니다. 모델 제공자의 `experimental_bearer_token` 은 토큰 값을 그대로 담아서, 보안상 이 필드보다 `env_key` 를 쓰는 편이 낫습니다[6]. `env_key`, `env_http_headers`, MCP 서버의 `bearer_token_env_var` 에는 환경 변수 이름만 들어갑니다[6]. 필드 목록 전체는 [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md) 와 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md) 에 있습니다.

`%USERPROFILE%\.codex` 에 `auth.json` 이 없을 때, 로그인하지 않았는지, 저장 방식을 `keyring`·`ephemeral` 로 바꿨는지, `CODEX_HOME` 을 옮겼는지, 로그아웃했는지는 이 사실만으로 판별할 수 없습니다.

**Gemini CLI.** 인증 정보를 두는 파일 이름은 실제 기기에서 확인해야 합니다. `%USERPROFILE%\.gemini` 에는 `settings.json`(`hooks` 키만 있는 경우가 있음), `config\` 아래 설정 파일, `antigravity\` 폴더가 있고, 이 가운데 인증 정보로 보이는 파일은 없습니다. `~/.gemini/antigravity/` 는 Gemini CLI 가 아닌 Google Antigravity 의 폴더입니다[13].

**Cursor.** Cursor CLI 대화 저장소 `store.db`(`blobs`·`meta` 표)에는 `blobEncryptionKey` 가 들어 있고, agentsview 의 읽기 도구는 이 값을 쓰지 않습니다[13]. 계정 토큰은 아니지만 이름대로 암호화 키이므로 다른 키와 같이 가립니다. 저장소 위치는 [Cursor](../../02-artifacts/dev-agents/cursor.md) 에 있습니다.

**Ollama.** 공개 키 `id_ed25519.pub` 로 모델 올리기(push), 비공개 모델 받기, Ollama Cloud 접근을 하고, 로그인은 설정 앱이나 `ollama signin` 으로 합니다[4]. `.ollama` 폴더에는 같은 이름의 개인 키 `id_ed25519` 도 있습니다.

### 로컬 AI 앱

아래 위치는 Windows 11 Pro 24H2(26100.3775)의 Chatbox 1.11.8, Msty 1.8.5, Jan 0.5.16, GPT4All 3.10.0 기준이고[7], 지금 판과 다를 수 있습니다.

| 앱 | 남는 곳 | 필드 | 값의 모양 | 자세히 |
|---|---|---|---|---|
| Chatbox | `%AppData%\xyz.chatboxapp.app\config.json` 과 같은 폴더의 `config-backup-*.json` | `settings` 의 `openaiKey`, `azureApikey`, `claudeApiKey`, `geminiAPIKey`, `groqAPIKey`, `deepseekAPIKey`, `siliconCloudKey`, `perplexityApiKey`, `xAIKey` | 평문[8] | [Chatbox](../../02-artifacts/local-ai/chatbox.md) |
| Msty | `%AppData%\Msty\msty.db` | `api_keys` 의 `key`, `key_hint`, `provider`, `created_at`, `save_in_keychain` | 아래 설명 | [Msty](../../02-artifacts/local-ai/msty.md) |
| Jan | `%AppData%\Jan\data\cortex.db`, `%AppData%\Jan\data\logs\cortex.log` | `engines.api_key`, 로그의 `[LoadModel] header: Authorization: Bearer` 줄 | 평문[7][8] | [Jan](../../02-artifacts/local-ai/jan.md) |
| GPT4All | `%LocalAppData%\nomic.ai\GPT4ALL\gpt4all-{ID}.rmodel` | JSON 의 `apiKey`, `baseUrl`, `modelName` | 논문 부록 B 가 "API Key" 로 적음[7][8] | [GPT4All](../../02-artifacts/local-ai/gpt4all.md) |

Msty 는 출처끼리 다릅니다. 논문 표 6 은 `api_keys.key` 를 "클라우드 LLM 에 접근하는 API 키" 로 적었습니다[7]. LangurTrace 저장소의 샘플 `msty.db`(2025-05-23 수집)에서는 `key` 값이 `v10` 으로 시작하고 평문 키가 아니었으며, `key_hint` 에만 키의 앞뒤 몇 글자가 평문으로 남아 있었습니다[8]. 실제 데이터에서는 값이 평문인지부터 봅니다.

API 키로 부른 클라우드 대화는 대개 상태를 남기지 않아서, 로컬 앱이 대화 기록을 쥐고 매번 다시 보냅니다[7, §3.4]. 그래서 이런 대화는 대개 클라우드 쪽에 대화 문맥이 남지 않고 로컬 앱의 기록이 주된 증거가 됩니다. 다만 API 종류에 따라 서버가 키에 묶인 제한된 기록을 남기는 예외도 있습니다[7, §3.4]. 키 자체의 증거 가치는 크지 않지만, 서비스 회사에 서버 쪽 자료를 공식 절차로 요청할 때 넘길 수 있습니다[7, §4.3].

AnythingLLM 의 키·토큰 필드는 [AnythingLLM](../../02-artifacts/local-ai/anythingllm.md) 에 정리돼 있습니다.

### 채팅 앱과 브라우저

**Electron 데스크톱 앱.** 로그인 세션은 앱 데이터 폴더의 쿠키 DB `Network\Cookies` 와 파티션별 쿠키 DB 의 `cookies` 표에 남고, 값은 평문 `value` 와 암호화된 `encrypted_value` 두 열로 나뉩니다. 쿠키 DB 위치와 열 목록은 [Electron·웹뷰 앱의 저장 구조](electron-webview.md) 에, Windows 에서 `encrypted_value` 를 보호하는 원리는 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html) 와 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/protection/data-protection-api/index.html) 에 있습니다. 앱이 Electron `safeStorage` 로 문자열을 암호화했다면, Windows 에서는 같은 사용자 공간의 다른 앱도 풀 수 있습니다[5].

비밀값은 아니지만 계정을 가리키는 식별자도 설정 파일에 남습니다. Claude 데스크톱에서는 `config.json` 의 `lastKnownAccountUuid`, `cowork-enabled-cli-ops.json` 의 `ownerAccountId`, `plan-usage-history.json` 의 `samples[].org` 가 계정·조직 식별자로 보이는 필드입니다. 이런 식별자로 사용자를 가려내는 법은 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md) 에서 다룹니다.

**모바일 컴패니언 앱.** 루팅한 Android 12(API 31) 에뮬레이터에서 앱 여섯 개를 시험한 결과[9], Character.AI 는 기기에 대화를 두지 않고 인증 토큰만 `RKStorage` 에 남겨서 이 앱에서는 인증 토큰이 중요한 증거가 됩니다[9]. Kindroid 는 `PersistedInstallation.json` 에 Firebase 토큰과 갱신 토큰을 남깁니다[9]. 파일 위치가 논문 표와 도구 코드에서 다르므로 [AI 컴패니언 앱](../../02-artifacts/chat-services/companion-apps.md) 을 봅니다. [Copilot — Android](../../02-artifacts/chat-services/copilot/android.md) 처럼 앱 설정 파일 안 JSON 에 토큰이 들어가는 경우도 있습니다.

**AI 에이전트 브라우저.** 로그인 흔적은 Comet 의 Local Storage 키 `pplx-next-auth-session` 과 쿠키 `__Secure-next-auth.session-token`, Fellou 의 `fellou.id_token`, Edge Copilot 의 MSAL 캐시 `msal.2.*` 와 `token.keys`, Genspark 쿠키의 `session_id` 에 남습니다[14]. 위치와 구조는 [AI 에이전트 브라우저](../../02-artifacts/agentic-services/ai-browsers.md) 에 있습니다.

### 환경 변수와 기록 속 사본

도구가 읽는 환경 변수에도 키가 들어갑니다. Codex CLI 는 `OPENAI_API_KEY` 를 `codex login --with-api-key` 에 넘겨 로그인하고[3], Claude Code 는 `ANTHROPIC_API_KEY`·`ANTHROPIC_AUTH_TOKEN`·`CLAUDE_CODE_OAUTH_TOKEN` 을 읽습니다[1]. 환경 변수로 인증했다면 로그인 파일이 없어도 도구를 쓸 수 있어서, 사용자·시스템 환경 변수와 셸 설정 파일을 함께 봅니다.

기록 파일에 비밀값이 섞여 들어가는 길도 있습니다. Claude Code 가 세션 중에 `.env` 를 읽었거나 비밀값을 출력했다면 그 내용이 세션 기록에 그대로 남습니다[2]. `shell-snapshots/*.sh` 에서는 export 한 토큰이 나올 수 있고, `paste-cache` 에는 가장 민감한 내용이 담기는 경우가 많습니다[10]. Jan 의 `cortex.log` 에는 등록한 API 키가 평문으로 남습니다[7, §4.6.3]. 그래서 세션 기록·로그 파일도 자격 증명을 담은 파일로 다룹니다.

## 읽는 법

1. 위 위치마다 파일이 있는지와 파일 시스템 시각을 먼저 목록으로 뜹니다. 값을 열지 않고도 있음·없음과 시각만으로 알 수 있는 것이 많습니다.
2. 파일을 열어야 하면 사본에서 엽니다. 보고서와 작업 메모에는 파일 위치, 키 이름, 값이 있었는지, 만료 시각 같은 정보만 옮기고 토큰 값은 옮기지 않습니다. Msty `key_hint` 처럼 앱이 일부러 남긴 앞뒤 몇 글자는 키를 구별하는 데 쓸 수 있습니다.
3. 시각 필드의 기준을 확인합니다. Claude Code `expiresAt`·`refreshTokenExpiresAt` 는 단위가 문서에 없어서 자릿수로 초·밀리초를 구분하고 파일 수정 시각과 맞춰 봅니다. Msty `api_keys.created_at` 은 스키마 기본값이 SQLite `CURRENT_TIMESTAMP` 라서 UTC 입니다[8]. Jan `engines` 표의 `date_created`·`date_updated` 도 스키마 기본값이 `CURRENT_TIMESTAMP` 입니다[8]. 이 열을 키를 넣은 시각으로 쓰기 전에 [Jan](../../02-artifacts/local-ai/jan.md) 의 시각 절을 봅니다.
4. 파일이 없으면 OS 자격 증명 저장소(Windows 자격 증명 관리자, macOS 키체인), 환경 변수, 옮긴 설정 폴더(`CLAUDE_CONFIG_DIR`, `CODEX_HOME`), 로그 파일을 차례로 봅니다. Codex 는 `config.toml` 의 `cli_auth_credentials_store`·`mcp_oauth_credentials_store` 값으로 어디를 볼지 정합니다.

## 포렌식에서 중요한 점

**토큰은 조사자가 쓰는 열쇠가 아닙니다.** 수집한 토큰으로 서비스에 접속하면 권한 범위를 벗어난 접근이 될 수 있습니다. 서버 쪽 기록이 필요하면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 을 따릅니다. 기기에 남은 토큰으로 서버의 대화를 받아 온 연구에서도, 서비스 회사의 협조나 적법한 서버 로그 접근으로 더 많은 증거를 얻을 수 있다고 봅니다[9]. 수집한 파일은 비밀번호와 같은 수준으로 보관하고 공유 범위를 좁힙니다.

**토큰이 있다는 사실이 증명하는 범위는 좁습니다.** 로그인 정보 파일은 그 사용자 계정에 누군가 로그인한 정보가 저장돼 있었다는 것과 파일이 마지막으로 바뀐 시점을 알려 줍니다. 그 토큰으로 언제 무엇을 했는지는 알려 주지 않습니다. 사용 시점은 세션 기록과 [네트워크 기록](../../02-artifacts/network-enterprise/network-traces.md) 으로 따로 확인합니다. API 키도 마찬가지라서, 키가 등록돼 있다는 사실만으로 그 키로 대화했다고 쓰지 않습니다.

**지운 뒤에 남는 정도가 앱마다 다릅니다.** Claude Code 의 `/logout` 과 Codex CLI 의 `codex logout` 은 저장된 로그인 정보를 지웁니다[1][3]. Character.AI 는 계정을 지우자 기기에 있던 인증 토큰과 로그인 정보가 모두 사라졌습니다[9]. 로컬 AI 앱에서 등록한 API 키를 지운 뒤 되살린 결과는 아래와 같습니다(표 5)[7].

| 앱 | 결과 |
|---|---|
| Jan | 지워도 되살아남. `cortex.log` 에 지운 키까지 남음(부록 B) |
| Msty | 있지만 지우면 대개 되살아나지 않음 |
| GPT4All | 있지만 지우면 대개 되살아나지 않음 |
| LM Studio | 클라우드 키 기능 없음 |

이 결과는 디스크 수준 복구만 잰 것이고, 볼륨 섀도 복사본과 메모리는 시험하지 않았습니다[7, §6.2]. Chatbox 는 `config.json` 의 백업 사본을 주기적으로 만들고 지우는데, 이 사본으로 지운 뒤에도 최근 자료를 되살릴 수 있습니다[7, §4.5]. 설정에서 키를 지웠어도 백업 사본에 예전 설정이 남아 있을 수 있으니 함께 봅니다.

## 함정

**화면에만 나온 토큰도 있습니다.** `claude setup-token` 은 1년짜리 토큰을 출력만 하고 저장하지 않습니다[1]. 이 토큰은 도구 폴더가 아니라 사용자가 옮겨 적은 곳(환경 변수, 스크립트, 설정 파일)에 있을 수 있습니다.

**이름에 "key" 가 들어가도 계정 열쇠가 아닐 수 있습니다.** Claude Code 폴더 `daemon\` 아래에는 `control.key`, `pipe.key` 가 있습니다. 공개 문서에 용도 설명이 없어서, 이름만으로 계정 자격 증명이라고 쓰지 않습니다. 도구도 같은 실수를 합니다. LangurTrace 의 Chatbox 보고 코드는 `settings` 의 키 이름에 `key` 가 들어가고 값이 있으면 모두 API 키 행으로 내보내는데[8], 샘플 `settings` 에는 아바타 이미지를 가리키는 `userAvatarKey`, `defaultAssistantAvatarKey` 도 있습니다[8].

**분석 도구의 출력에 키가 평문으로 들어갑니다.** LangurTrace 는 Chatbox 키를 `configuration.csv` 에, GPT4All 키를 `remote_config.csv` 에, Jan 의 `engines` 표를 `api_key` 열까지 엑셀로 옮깁니다[8]. ccfx 는 `.credentials.json` 의 존재·크기·수정 시각만 적지만, `-ac` 옵션으로 만드는 수집 압축본에는 OAuth 토큰이 평문으로 들어갑니다[11]. coding-agent-forensics 는 `auth.json`, `.credentials.json`, API 키가 든 설정 파일을 모으지 말라고 권합니다[12]. 도구 출력도 원본과 같은 수준으로 보관하고, 보고서에 붙이기 전에 값을 가립니다.

**암호화된 필드가 보호를 뜻하지는 않습니다.** `safeStorage` 로 암호화한 값은 Windows 에서 사용자 단위로 보호되므로[5], 같은 사용자 계정으로 실행한 다른 프로그램은 읽을 수 없었다는 근거가 되지 않습니다. Codex 의 `.credentials.json` 도 같은 사용자로 실행되는 다른 프로그램이 읽을 수 있습니다[6].

## 도구

파일 목록과 시각은 OS 기본 명령이나 공개 타임라인 도구로 뜹니다. JSON 파일은 `jq 'keys'` 처럼 키 이름만 뽑으면 값을 화면에 띄우지 않고 짜임을 볼 수 있고, SQLite 는 스키마와 `count(*)`, 값이 비었는지만 조회하면 됩니다. Windows 자격 증명 관리자는 그 사용자로 로그온한 실행 중인 시스템에서 `cmdkey /list` 로 항목 이름을 볼 수 있습니다. 구조는 [자격 증명 관리자와 볼트](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/credentials/credential-manager-windows-vault.html), [키체인 (macOS)](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/protection/keychain/index.html), [키체인 (iOS)](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/keychain.html) 에서 다룹니다.

LangurTrace 는 Chatbox·Msty·Jan·GPT4All 의 키를 표로 뽑고[8], ccfx 는 Claude Code 로그인 파일이 있는지만 기록합니다[11]. 두 도구 모두 위 "함정" 에 적은 대로 출력의 키 값을 다뤄야 합니다.

## 참고 문헌

1. Claude Code Docs — Authentication — https://code.claude.com/docs/en/authentication
2. Claude Code Docs — .claude 폴더 참조 (claude-directory) — https://code.claude.com/docs/en/claude-directory
3. OpenAI Codex — Authentication — https://learn.chatgpt.com/docs/auth
4. Ollama — FAQ — https://docs.ollama.com/faq
5. Electron — safeStorage — https://www.electronjs.org/docs/latest/api/safe-storage
6. openai/codex — `codex-rs/core/config.schema.json`(커밋 406dc92) — https://github.com/openai/codex — `AuthCredentialsStoreMode`, `OAuthCredentialsStoreMode`, `cli_auth_credentials_store`, `mcp_oauth_credentials_store`, `ModelProviderInfo`, `RawMcpServerConfig`
7. S. Jeong, S. Lee, J. Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation 54 (2025) 301987. https://doi.org/10.1016/j.fsidi.2025.301987
8. jeongramon/LangurTrace(커밋 3ed4648, 2025-07-30) — https://github.com/jeongramon/LangurTrace — `src/reporter/chatbox/config_reporter.py`, `src/reporter/gpt4all/configuration_reporter.py`, `src/reporter/jan/configuration_reporter.py`, `sample_dataset/collect/C/Users/USER/AppData/Roaming/xyz.chatboxapp.app/config-backup-2025-05-23T11_36_10.169Z.json`, `sample_dataset/collect/C/Users/USER/AppData/Roaming/Msty/msty.db`, `sample_dataset/collect/C/Users/USER/AppData/Roaming/Jan/data/cortex.db`
9. K. J. Comeaux, T. T. Spinosa, A. Ghosn, I. Baggili, "Ex Machina: A forensic evaluation of AI companion applications and their evidentiary value", Forensic Science International: Digital Investigation 56 (2026) 302050. https://doi.org/10.1016/j.fsidi.2026.302050
10. forensicdave/claude-forensics(v0.1.1) — https://github.com/forensicdave/claude-forensics — `README.md`, `docs/claude_forensics.md`
11. fkasasagi/ccfx — https://github.com/fkasasagi/ccfx — `README.en.md`
12. Shorton88/coding-agent-forensics — https://github.com/Shorton88/coding-agent-forensics — `README.md`
13. kenn-io/agentsview — https://github.com/kenn-io/agentsview — `README.md`, `docs/internal/session-format-sources.md`(2026-09-11 수정)
14. seturi/AI-Agent-Browser-Forensics — https://github.com/seturi/AI-Agent-Browser-Forensics — `aabf/signatures.py`
