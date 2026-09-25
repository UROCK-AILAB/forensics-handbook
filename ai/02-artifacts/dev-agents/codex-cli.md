---
title: "Codex CLI"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 620
---

# Codex CLI (Codex)

Codex CLI 는 OpenAI 의 명령줄 코딩 에이전트이고, 기기에는 `CODEX_HOME`(기본 `~/.codex`) 폴더에 설정·인증 정보·입력 기록·로그가 남으며, 조직이 OpenTelemetry 수집을 켰다면 도구 실행 결정과 결과가 PC 밖 수집 서버에도 남습니다.

> 확인 날짜: 2026-09. 앱 버전은 확인하지 못했습니다. 폴더 구성과 설정 키는 공식 설정 문서[1] 기준이고, 관찰한 PC 의 `~/.codex` 에는 설정·스킬 파일만 있고 기록 파일이 없어서 기록 파일의 내부 구조는 직접 보지 못했습니다(확인 범위: Windows 11, 2026-09).

## 무엇을 기록하나 · 왜 생기나

Codex CLI 는 로컬 상태를 `CODEX_HOME` 이 가리키는 폴더에 두고, 이 환경 변수가 없으면 `~/.codex`(Windows 는 `%USERPROFILE%\.codex`)를 씁니다[1]. 문서에 따르면 그 안에 사용자 설정 `config.toml`, 파일 방식으로 저장한 인증 정보 `auth.json`, 입력 기록 `history.jsonl`, 로그와 캐시를 둡니다[1].

입력 기록은 기본으로 켜져 있어서 따로 끄지 않았다면 `CODEX_HOME` 아래(예: `~/.codex/history.jsonl`)에 남고, 설정 파일의 `[history]` 절에서 `persistence = "none"` 으로 끄거나 `max_bytes` 로 크기를 묶을 수 있습니다[1]. 크기를 넘으면 오래된 항목부터 버리고 파일을 다시 줄여 씁니다[1].

조직이 구조화 로그를 모으려고 OpenTelemetry 내보내기를 켜면, Codex 는 대화 시작, API 요청, 도구 실행 승인·거부, 도구 실행 결과를 이벤트로 보냅니다[1]. 기기 밖에 남는 이 기록은 에이전트가 무엇을 하려 했고 사용자가 허락했는지를 보여 주는 자료라서, 회사 사건이라면 수집 서버가 있는지부터 묻습니다.

서버 쪽(OpenAI 계정의 대화, API 요청 보관 기간)은 이번에 연 자료로 확인하지 못했습니다. 서버와 기기 중 어디에 무엇이 있는지 가르는 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

## 위치와 버전별 차이

Codex CLI 는 OS 가 달라도 사용자 홈 아래 같은 이름의 폴더를 씁니다[1]. 아래 표에서 "확인 못 함" 은 이번에 연 문서에 없다는 뜻입니다.

| 위치(`CODEX_HOME` 기준) | 담는 것 | 근거 |
|---|---|---|
| `config.toml` | 사용자 설정, `[history]` 절 | 문서[1] |
| `auth.json` | 파일 방식으로 저장한 인증 정보 | 문서[1] |
| `history.jsonl` | 입력 기록 | 문서[1] |
| 로그·캐시 | 문서는 "로그와 캐시가 여기 있다" 고만 적음, 파일 이름 확인 못 함 | 문서[1] |
| `hooks.json` | 훅 설정(공식 형식 확인 못 함) | 관찰 |
| `skills/` | 스킬 폴더 | 관찰 |
| 세션 전체 기록 파일 | 있는지, 어디 있는지 확인 못 함 | — |

인증 정보는 `auth.json` 대신 OS 키체인·키링에 둘 수 있고 `cli_auth_credentials_store` 설정으로 고르는데[1], 어느 쪽이 기본인지는 확인하지 못했습니다. 키체인에 두었다면 Windows 는 [자격 증명 관리자와 볼트](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/credentials/credential-manager-windows-vault.html), macOS 는 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html) 페이지대로 찾고, 토큰이 남는 곳 전반은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

관찰한 PC 의 `%USERPROFILE%\.codex` 에는 파일이 11개 있었고, `hooks.json` 하나와 `skills/<이름>/SKILL.md` 다섯 개, `skills/<이름>/<파일>.json` 다섯 개였습니다. `config.toml`·`auth.json`·`history.jsonl`·세션 폴더는 없었습니다(확인 범위: Windows 11, 2026-09).

## 구조

### 설정 `config.toml`

TOML 형식이고, 기록을 다루는 `[history]` 절에 `persistence` 와 `max_bytes` 가 들어갑니다[1]. OpenTelemetry 내보내기 설정의 `log_user_prompt` 는 기본 `false` 라서 프롬프트 내용은 가려진 채 나가고, 켜야만 내용이 남습니다[1]. 아래는 기록을 끈 설정을 새로 만든 예시입니다.

```toml
# 만든 예시
[history]
persistence = "none"
```

MCP 서버 설정이 이 파일의 어느 절에 들어가는지는 확인하지 못했고, MCP 전반은 [MCP 서버와 도구 호출 기록](mcp.md)에서 다룹니다.

### 입력 기록 `history.jsonl`

이름으로 보아 한 줄에 JSON 한 개씩 적는 JSON Lines 파일이지만, 한 줄에 어떤 키가 있는지는 확인하지 못했습니다. 검체에서는 키 이름을 짐작하지 말고 줄마다 키 목록을 뽑아 모양부터 확인합니다(아래 "직접 분석해 보기").

### 구조화 로그 이벤트(OpenTelemetry)

내보내기 방식은 `otlp-http`, `otlp-grpc` 이고, 이벤트를 모았다가 비동기로 보내며 종료할 때 남은 것을 비웁니다[1].

| 이벤트 | 담는 것[1] |
|---|---|
| `codex.conversation_starts` | 모델, 샌드박스 설정 |
| `codex.api_request` | 시도, 상태, 걸린 시간, 오류 |
| `codex.tool_decision` | 도구 실행 승인·거부 결과 |
| `codex.tool_result` | 실행 시간, 성공 여부 |
| `codex.sse_event`, `codex.websocket_event` | 스트리밍 응답 이벤트 |

### 관찰한 훅·스킬 파일

관찰한 PC 의 `hooks.json` 은 `hooks.` 아래 이벤트별 목록이었고, 목록 항목의 키는 `matcher`(문자열)와 `hooks`(목록)였습니다. 이벤트는 PermissionRequest, PostToolUse, PreToolUse, Stop, UserPromptSubmit 이었습니다. `skills/<이름>/<파일>.json` 의 키는 `files`(사전), `files.SKILL.md`(문자열), `version`(정수)이었고 이 파일의 용도는 확인하지 못했습니다(모두 확인 범위: Windows 11, 2026-09). 훅 설정의 공식 형식은 이번에 연 문서에 없었습니다.

## 증거로서 의미

**증명하는 것.** `history.jsonl` 에 줄이 있으면 그 사용자 계정의 `CODEX_HOME` 에서 Codex 에 무엇을 입력한 기록이 있다는 뜻입니다. `config.toml` 은 기록을 껐는지, 크기를 묶었는지, 인증을 어디에 두게 했는지를 보여 주고, `hooks.json` 은 어떤 동작에 사용자 스크립트를 걸었는지를 보여 줍니다. 수집 서버에 `codex.tool_decision` 이 있으면 "이 시각에 이 도구 실행을 승인(또는 거부)한 기록이 있다" 고 쓸 수 있습니다.

**증명하지 못하는 것.** 관찰한 PC 처럼 `~/.codex` 에 설정과 스킬만 있고 기록이 없으면, 다른 도구가 폴더를 만들었을 수도, 기록을 껐을 수도, 지웠을 수도 있고 이 흔적만으로는 어느 쪽인지 가릴 수 없습니다. `config.toml` 에 `persistence = "none"` 이 있으면 끈 사실은 보이지만 언제 껐는지는 파일 시각으로만 짐작합니다. 수집 서버의 이벤트는 기본 설정에서 프롬프트 내용이 가려져서, 무엇을 시켰는지는 기기 쪽 기록이나 다른 자료로 채워야 합니다. 입력한 사람이 누구인지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 좁힙니다.

## 시각 해석

`history.jsonl` 에 시각 칸이 있는지, 있다면 UTC 인지와 단위가 무엇인지는 확인하지 못했습니다. 칸이 없으면 파일 수정 시각이 마지막으로 줄을 덧붙인 때를 가리키고, `max_bytes` 로 오래된 줄을 버렸다면 파일 안의 가장 오래된 줄이 실제 첫 사용보다 늦을 수 있습니다. `config.toml`·`hooks.json` 의 수정 시각은 설정을 마지막으로 고친 때입니다. OpenTelemetry 이벤트의 시각 기준은 이번 문서로 확인하지 못해서, 수집 서버 설정을 함께 받아 시간대를 확인합니다. 여러 출처를 맞추는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

`CODEX_HOME` 을 다른 폴더로 바꿔 쓰면 홈 아래 `~/.codex` 에는 아무것도 없을 수 있어서, 사용자 환경 변수와 셸 설정 파일에서 이 변수를 먼저 찾습니다. 세션 전체 기록 파일 경로는 이번에 연 문서에 없어서 이 페이지에 적지 않았고, 검체에 `CODEX_HOME` 아래 다른 기록 폴더가 있으면 버전과 함께 기록한 뒤 직접 열어 봅니다.

`max_bytes` 로 줄이 잘리는 동작은 설정에 따른 정상 동작이라서 앞부분이 없다고 조작으로 보면 안 됩니다. 반대로 `persistence = "none"` 은 사용자가 스스로 켤 수 있는 설정이라 기록이 없는 이유가 될 수 있지만, 사건 전후로 설정을 바꿨는지는 파일 시각과 백업을 함께 봐야 합니다. 보관·삭제 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 설정 파일에서 기록을 끈 흔적은 절 이름과 키 문자열 바이트로 찾고, JSON Lines 는 줄 끝 `0A` 로 줄을 나눕니다. 아래는 문자 인코딩대로 만든 예시이고, 검체에서 뜬 바이트가 아닙니다.

```
만든 예시(인코딩 명세로 만든 바이트)
"[history]"             5B 68 69 73 74 6F 72 79 5D
"persistence = \"none\""  70 65 72 73 69 73 74 65 6E 63 65 20 3D 20 22 6E 6F 6E 65 22
줄 끝(LF)                0A
```

지운 `history.jsonl` 을 할당되지 않은 영역에서 찾을 때는 `7B 22`(`{"`)로 시작해 `0A` 로 끝나는 덩어리를 후보로 삼고, 각 덩어리가 온전한 JSON 인지 다시 확인합니다.

**공개 도구로 한 번.** 수집한 사본에서 jq 와 ripgrep 으로 키 모양과 설정을 봅니다. 경로는 만든 예시이고, 원본이 아니라 사본에서만 돌립니다.

```sh
# 만든 예시 경로
CX=/cases/case-0001/copy/alice/.codex
# 줄마다 키 목록을 뽑아 모양별로 세기(값은 출력하지 않음)
jq -c 'keys' "$CX/history.jsonl" | sort | uniq -c
# 기록·인증 관련 설정 찾기
rg -n '^\[history\]|persistence|max_bytes|cli_auth_credentials_store|log_user_prompt' "$CX/config.toml"
# 훅 이벤트 이름만 보기
jq '.hooks | keys' "$CX/hooks.json"
```

`auth.json` 은 열어 보더라도 값을 보고서에 옮기지 않고, 파일이 있었다는 사실과 수정 시각만 적습니다.

## 교차 검증

에이전트가 실행한 명령과 고친 파일은 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)의 흐름으로 셸 기록·git 이력과 맞춰 보고, 인증 정보를 건드린 정황은 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md)에서 다룹니다. 같은 PC 에 [Claude Code](claude-code/index.md)나 [Gemini CLI](gemini-cli.md)가 함께 있으면 훅·스킬 파일이 어느 도구 것인지 먼저 나눕니다. 서비스 접속은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)과, 서버 쪽 대화는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)과 이어 봅니다. 웹 ChatGPT 쪽 흔적은 [ChatGPT](../chat-services/chatgpt/index.md)에 있습니다.

## 실습

공개 검체에 Codex CLI 흔적이 들어 있는지는 확인하지 못했습니다. 시험용 가상 머신과 시험 계정으로 풀어 봅니다.

1. 기본 설정으로 몇 번 입력한 뒤 `~/.codex` 에 생긴 파일을 모두 적고, `history.jsonl` 의 키 모양을 뽑아 봅니다.
2. `persistence = "none"` 으로 바꾼 뒤 다시 입력해 무엇이 더 이상 생기지 않는지 확인합니다.
3. `max_bytes` 를 작게 잡고 입력을 늘려, 오래된 줄이 버려진 뒤 파일 시각과 첫 줄이 어떻게 달라지는지 봅니다.
4. `CODEX_HOME` 을 다른 폴더로 바꿔 쓰고, 기본 폴더만 수집했을 때 무엇을 놓치는지 적어 봅니다.

## 참고 문헌

1. OpenAI Codex — Advanced configuration — https://learn.chatgpt.com/docs/config-file/config-advanced
