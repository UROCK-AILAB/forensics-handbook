---
title: "API 키와 토큰이 남는 곳"
parent: "기반 · 저장 구조"
nav_order: 30
---

# API 키와 토큰이 남는 곳 (API Keys·Tokens)

> 확인 날짜: 2026-09. 공식 문서는 2026-09-25 에 열어 읽었습니다. 기기 관찰은 Windows 11(빌드 26200) 한 대에서 AI 도구 폴더를 읽기 전용으로 열어 파일 이름과 키 이름만 본 결과이고, 토큰·키 값은 읽지 않았으며 앱 버전은 적어 두지 않았습니다. 관찰로 확인한 내용에는 "(확인 범위: Windows 11, 2026-09)" 를 붙였습니다. 이 쪽의 예시 값은 모두 새로 만든 가짜 값이고 실제 키·토큰의 형식을 따르지 않습니다.

## 한 줄 요약

AI 개발 도구와 데스크톱 앱은 로그인 정보를 평문 파일, OS 자격 증명 저장소(키체인·자격 증명 관리자), 브라우저 방식의 쿠키 DB, 환경 변수 가운데 한 곳 이상에 두고, 어디에 두는지는 도구와 OS 와 설정마다 달라서 파일이 없다는 사실만으로 로그인하지 않았다고 쓸 수 없습니다.

## 이 형식을 쓰는 아티팩트

터미널에서 도는 개발 도구([Claude Code](../../02-artifacts/dev-agents/claude-code/index.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md)), 로컬 AI([Ollama](../../02-artifacts/local-ai/ollama.md)), 채팅 서비스의 데스크톱 앱이 대상입니다. 에이전트가 자격 증명 파일을 읽거나 옮긴 사고를 조사하는 흐름은 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md) 에서 다루고, 이 쪽은 조사자가 어디를 봐야 하는지를 정리합니다.

## 구조

### 한눈에 보기

| 도구 | Windows | macOS | Linux | 보호 | 근거 |
|---|---|---|---|---|---|
| Claude Code | `%USERPROFILE%\.claude\.credentials.json` | 키체인. 쓰기가 막히면 `~/.claude/.credentials.json`(모드 0600) | `~/.claude/.credentials.json` | 파일은 따로 암호화하지 않고 파일 권한만 따름 | [1][2] |
| Codex CLI | 설정에 따라 `~/.codex/auth.json` 또는 OS 자격 증명 저장소 | 같음 | 같음 | `auth.json` 은 평문 파일 | [3] |
| Gemini CLI | 확인 못 함 | 확인 못 함 | 확인 못 함 | 확인 못 함 | 문서를 열지 못함 |
| Ollama | `C:\Users\<username>\.ollama\id_ed25519.pub` | `~/.ollama/id_ed25519.pub` | `/usr/share/ollama/.ollama/id_ed25519.pub` | 확인 못 함 | [4] |
| 데스크톱 채팅 앱(Electron) | 앱 데이터 폴더의 쿠키 DB | 확인 못 함 | 확인 못 함 | `value`·`encrypted_value` 두 칸 | 관찰 |

### Claude Code

Claude Code 는 Windows·Linux 에서 로그인 정보를 `~/.claude/.credentials.json` 에 두고, 이 파일은 따로 암호화하지 않고 사용자 프로필 폴더의 접근 권한을 따릅니다 [1][2]. macOS 에서는 키체인에 저장하고, SSH 세션처럼 키체인 쓰기가 막히면 `~/.claude/.credentials.json` 에 파일 모드 0600 으로 대신 씁니다 [1]. `CLAUDE_CONFIG_DIR` 로 데이터 폴더를 옮기면 키체인 항목도 그 폴더에 묶여 따로 생깁니다 [1]. 키체인 항목의 서비스 이름은 확인하지 못했습니다.

이 PC 의 `.credentials.json` 은 최상위 키 `claudeAiOauth` 아래에 `accessToken`(문자열), `refreshToken`(문자열), `expiresAt`(정수), `refreshTokenExpiresAt`(정수), `scopes`(목록), `subscriptionType`(문자열), `rateLimitTier`(문자열)로 짜여 있었습니다(확인 범위: Windows 11, 2026-09). 아래는 짜임만 보이려고 만든 예시이고, 값은 모두 가짜입니다.

```json
{
  "claudeAiOauth": {
    "accessToken": "(가림-예시)",
    "refreshToken": "(가림-예시)",
    "expiresAt": 0,
    "refreshTokenExpiresAt": 0,
    "scopes": ["(예시 범위)"],
    "subscriptionType": "(예시)",
    "rateLimitTier": "(예시)"
  }
}
```

파일 말고도 인증 정보가 들어오는 길이 여럿 있고, Claude Code 는 클라우드 공급자 변수, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_API_KEY`, `apiKeyHelper`, `CLAUDE_CODE_OAUTH_TOKEN`, Anthropic 프로필, `/login` 구독 로그인 순서로 먼저 있는 것을 씁니다 [1]. `apiKeyHelper` 는 셸 스크립트를 실행해 키를 받고 기본 5분마다 다시 실행하며 [1], `claude setup-token` 은 1년짜리 토큰을 화면에 출력만 하고 저장하지 않습니다 [1]. `/logout` 은 로그인 정보를 지우고 처음 설정 상태로 되돌립니다 [1].

같은 폴더의 `daemon\` 아래에는 `control.key`, `pipe.key` 파일이 있었습니다(확인 범위: Windows 11, 2026-09). 용도를 설명한 문서를 찾지 못했고, 이름만으로 계정 자격 증명이라고 쓰지 않습니다.

### Codex CLI

Codex CLI 는 로그인 정보를 `~/.codex/auth.json` 평문 파일이나 OS 자격 증명 저장소에 두고, 어느 쪽에 둘지는 설정 `cli_auth_credentials_store` 로 정합니다 [3].

| 값 | 저장하는 곳 |
|---|---|
| `file` | `CODEX_HOME` 아래 `auth.json`(`CODEX_HOME` 기본값은 `~/.codex`) |
| `keyring` | OS 자격 증명 저장소. 저장소가 없으면 실패 |
| `auto` | 저장소를 먼저 쓰고, 안 되면 `auth.json` |
| `ephemeral` | 현재 프로세스 메모리에만 |

이 설정의 기본값은 확인하지 못했습니다. 문서는 `auth.json` 에 접근 토큰이 들어 있으니 비밀번호처럼 다루라고 적고 있습니다 [3]. API 키로 로그인할 때는 `OPENAI_API_KEY` 값을 `codex login --with-api-key` 에 넘기고, `codex logout` 은 저장된 로그인 정보를 지웁니다 [3]. Windows 에서 `keyring` 을 쓸 때 자격 증명 관리자에 남는 항목 이름은 확인하지 못했고, 자격 증명 관리자 자체는 [자격 증명 관리자와 볼트](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/credentials/credential-manager-windows-vault.html) 를 봅니다.

이 PC 의 `%USERPROFILE%\.codex` 에는 `auth.json` 이 없었습니다(확인 범위: Windows 11, 2026-09). 로그인하지 않았는지, `keyring` 에 저장했는지, `CODEX_HOME` 을 다른 곳으로 정했는지, `ephemeral` 로 썼는지는 이 사실만으로 가릴 수 없습니다.

### Gemini CLI

Gemini CLI 의 인증 방식과 자격 증명 파일 이름은 인증 문서를 열지 못해 확인하지 못했습니다. 이 PC 의 `%USERPROFILE%\.gemini` 에서는 `settings.json`(`hooks` 키만 있었음), `config\` 아래 설정 파일, `antigravity\` 폴더를 보았고 인증 정보로 보이는 파일은 보지 못했습니다(확인 범위: Windows 11, 2026-09).

### Ollama

Ollama 는 사용자 폴더의 `.ollama` 아래에 공개 키 `id_ed25519.pub` 를 두고, 이 키로 모델 올리기(push), 비공개 모델 받기, Ollama Cloud 접근을 합니다 [4]. 로그인은 설정 앱이나 `ollama signin` 으로 합니다 [4]. 이 PC 의 `.ollama` 폴더에는 같은 이름의 개인 키 `id_ed25519` 도 있었습니다(확인 범위: Windows 11, 2026-09).

### 데스크톱 채팅 앱의 로그인 세션

Electron 으로 만든 채팅 앱의 로그인 세션은 앱 데이터 폴더의 쿠키 DB `Network\Cookies` 와 파티션별 쿠키 DB 의 `cookies` 표에 남고, 값 칸은 평문 `value` 와 암호화된 `encrypted_value` 두 칸입니다(확인 범위: Windows 11, 2026-09). 쿠키 DB 의 위치와 칸 목록은 [Electron·웹뷰 앱의 저장 구조](electron-webview.md) 에 있습니다. Windows 에서 쿠키를 암호화하는 방식과 `Local State` 의 키 구조는 이 쪽을 쓰면서 확인하지 못했고, [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html) 와 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html) 를 봅니다. 앱이 Electron `safeStorage` 로 문자열을 암호화했다면 Windows 에서는 같은 사용자 공간의 다른 앱이 풀 수 있습니다 [5].

비밀값은 아니지만 계정을 가리키는 식별자도 앱 설정 파일에 남습니다. Claude 데스크톱에서는 `config.json` 의 `lastKnownAccountUuid`, `cowork-enabled-cli-ops.json` 의 `ownerAccountId`, `plan-usage-history.json` 의 `samples[].org` 가 계정·조직 식별자로 보이는 칸이었습니다(확인 범위: Windows 11, 2026-09). 이 식별자로 사용자를 가리는 법은 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md) 에서 다룹니다.

### 환경 변수와 대화 기록 속 비밀값

도구가 읽는 환경 변수에도 키가 들어갈 수 있습니다. Codex CLI 는 `OPENAI_API_KEY` 를 [3], Claude Code 는 `ANTHROPIC_API_KEY`·`ANTHROPIC_AUTH_TOKEN`·`CLAUDE_CODE_OAUTH_TOKEN` 을 [1] 읽습니다. `GEMINI_API_KEY`·`GOOGLE_API_KEY` 는 확인하지 못했습니다. 셸 기록이나 `.env` 파일에 키가 남는 일반 경로는 이번에 연 문서에 없었습니다.

대화 기록에 비밀값이 섞여 들어가는 길도 있습니다. Claude Code 문서는 세션 중에 `.env` 를 읽었거나 비밀값을 출력했다면 그 내용이 세션 기록에 그대로 남는다고 적고 있습니다 [2]. 그래서 세션 기록 파일도 자격 증명을 담은 파일로 다룹니다.

## 읽는 법

1. 위 표의 위치마다 파일이 있는지, 파일 시스템 시각이 언제인지를 먼저 목록으로 뜹니다. 값은 열어 보지 않은 채로도 있음·없음과 시각만으로 알 수 있는 것이 많습니다.
2. 파일을 열어야 하면 사본에서 열고, 보고서와 작업 메모에는 키 이름과 값 종류, 만료 시각 같은 칸만 옮기고 토큰 값은 옮기지 않습니다.
3. `expiresAt`·`refreshTokenExpiresAt` 같은 정수 시각 칸은 초 단위인지 밀리초 단위인지 문서로 확인하지 못했습니다. 자릿수로 단위를 가리고 파일 수정 시각과 맞춰 봅니다.
4. 파일이 없으면 OS 자격 증명 저장소(Windows 자격 증명 관리자, macOS 키체인), 환경 변수, 다른 설정 폴더(`CLAUDE_CONFIG_DIR`, `CODEX_HOME`)를 차례로 봅니다.

## 포렌식에서 중요한 점

**토큰은 조사자가 쓰는 열쇠가 아닙니다.** 수집한 토큰으로 서비스에 접속하면 권한 범위를 벗어난 접근이 될 수 있어서, 서버 쪽 기록이 필요하면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 을 따릅니다. 수집한 파일은 비밀번호와 같은 수준으로 보관하고 공유 범위를 좁힙니다.

**토큰이 있다는 사실이 증명하는 범위는 좁습니다.** 로그인 정보 파일은 그 사용자 계정에서 누군가 로그인했다는 것과 파일이 마지막으로 바뀐 시점을 알려 주지만, 그 토큰으로 언제 무엇을 했는지는 알려 주지 않습니다. 사용 시점은 세션 기록과 [네트워크 기록](../../02-artifacts/network-enterprise/network-traces.md) 으로 따로 확인합니다.

**로그아웃하면 파일이 사라집니다.** Claude Code 의 `/logout` 과 Codex CLI 의 `codex logout` 은 저장된 로그인 정보를 지웁니다 [1][3]. 파일이 없다면 로그아웃했을 가능성도 함께 적습니다.

## 함정

**화면에만 나온 토큰도 있습니다.** `claude setup-token` 은 토큰을 출력만 하고 저장하지 않아서 [1], 이 토큰은 도구 폴더가 아니라 사용자가 옮겨 적은 곳(환경 변수, 스크립트, 설정 파일)에 있을 수 있습니다.

**이름이 "key" 인 파일이 모두 계정 열쇠는 아닙니다.** Claude Code 의 `daemon\control.key`·`pipe.key` 처럼 용도를 확인하지 못한 파일은 이름만으로 자격 증명이라고 쓰지 않습니다.

**암호화된 칸이 보호를 뜻하지는 않습니다.** `safeStorage` 로 암호화한 값은 Windows 에서 사용자 단위로 보호되어서 [5], 같은 사용자 계정으로 실행한 다른 프로그램이 읽지 못했다는 근거가 되지 않습니다. 쿠키의 `encrypted_value` 를 어떤 방식으로 암호화하는지는 이 쪽에서 확인하지 못했으므로, 보호 범위도 같다고 단정하지 않습니다.

## 도구

파일 목록과 시각은 OS 기본 명령이나 공개 타임라인 도구로 뜨고, JSON 파일은 `jq` 로 키 목록만 뽑으면 값을 화면에 띄우지 않고 짜임을 볼 수 있습니다. Windows 자격 증명 관리자는 살아 있는 시스템에서 그 사용자로 로그온한 상태라면 `cmdkey /list` 로 항목 이름을 볼 수 있고, 자세한 구조는 [자격 증명 관리자와 볼트](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/credentials/credential-manager-windows-vault.html) 를, macOS 는 [키체인 (macOS)](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html) 을, iOS 는 [키체인 (iOS)](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/keychain.html) 을 봅니다.

## 참고 문헌

1. Claude Code Docs — Authentication — https://code.claude.com/docs/en/authentication
2. Claude Code Docs — .claude 폴더 참조 (claude-directory) — https://code.claude.com/docs/en/claude-directory
3. OpenAI Codex — Authentication — https://learn.chatgpt.com/docs/auth
4. Ollama — FAQ — https://docs.ollama.com/faq
5. Electron — safeStorage — https://www.electronjs.org/docs/latest/api/safe-storage
