---
title: "Codex CLI"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 650
---

# Codex CLI (Codex)

Codex CLI 는 OpenAI 가 만든 명령줄 코딩 에이전트입니다. 기기의 `CODEX_HOME`(기본 `~/.codex`) 아래에는 세션마다 대화 전체를 적는 rollout 파일, 입력 기록 `history.jsonl`, 상태 SQLite, 설정, 인증 파일이 남습니다. 조직이 OpenTelemetry 수집을 켰다면 도구 실행 결정과 결과가 PC 밖 수집 서버에도 남습니다.

> 근거와 날짜: 경로·줄 구조·키 이름은 생산자 소스 `openai/codex` 커밋 406dc92(2026-07-30)[2]와 그 커밋의 설정 스키마[3]에서 확인했습니다. agentsview 의 형식 문서(2026-09-11 수정)[4]는 Codex CLI 0.147.0 으로 rollout 을 다시 확인했다고 적습니다(2026-08-16). OpenTelemetry 이벤트와 `[history]` 설정은 공식 설정 문서[1]를 따릅니다. Codex 는 자주 바뀌므로 검체의 버전은 rollout 의 `session_meta.payload.cli_version` 으로 확인합니다.

## 무엇을 기록하나 · 왜 생기나

Codex 는 로컬 상태를 환경 변수 `CODEX_HOME` 이 가리키는 폴더에 두고, 변수가 없으면 `~/.codex` 를 씁니다[1]. Windows 에서는 `%USERPROFILE%\.codex` 입니다(확인 범위: Windows 11, 2026-09). 기록은 목적에 따라 네 갈래로 나뉩니다.

- **세션 기록(rollout).** 세션을 나중에 다시 열거나 살펴볼 수 있도록 세션 하나를 JSON Lines 파일 하나에 적습니다[2]. 사용자 입력, 모델 응답, 도구 호출과 결과, 턴마다의 모델·작업 폴더·승인 정책이 들어갑니다.
- **입력 기록 `history.jsonl`.** 모든 세션의 입력을 한 파일에 덧붙이는 전역 기록입니다[2]. 한 줄에 세션 ID, 시각, 입력한 글이 들어갑니다.
- **상태 SQLite.** rollout 에서 뽑은 세션 목록·제목·턴 정보와 로그를 SQLite 에 따로 모읍니다[2].
- **설정과 인증.** `config.toml` 에 기록·인증·MCP 서버·훅 설정이 들어가고[3], 로그인 정보는 기본으로 `auth.json` 에 남습니다[3].

조직이 구조화 로그를 모으려고 OpenTelemetry 내보내기를 켜면, Codex 는 대화 시작, API 요청, 도구 실행 승인·거부, 도구 실행 결과를 이벤트로 보냅니다[1]. 이 기록은 에이전트가 무엇을 하려 했고 사용자가 허락했는지를 보여 주므로, 회사 사건이라면 수집 서버가 있는지부터 묻습니다. OpenAI 계정 쪽 자료는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 받고, 서버와 기기의 경계는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에서 설명합니다.

## 위치와 버전별 차이

아래 경로는 모두 `CODEX_HOME` 기준입니다.

| 위치 | 담는 것 | 근거 |
|---|---|---|
| `sessions/YYYY/MM/DD/rollout-YYYY-MM-DDThh-mm-ss-세션ID.jsonl` | 세션 하나의 전체 기록. 날짜 폴더와 파일 이름의 시각은 현지 시각 | [2] |
| `sessions/…`, `archived_sessions/` 의 `rollout-….jsonl.zst` | 수정 뒤 7일이 지난 rollout 을 zstd 로 압축한 파일 | [2] |
| `archived_sessions/rollout-….jsonl` | 보관 처리한 세션. 날짜 폴더 없이 한 폴더에 둠 | [2][4] |
| `session_index.jsonl` | 옛 판의 세션 목록·제목. agentsview 는 지금 판이 쓰지 않는다고 적음 | [4] |
| `history.jsonl` | 전역 입력 기록 | [2][3] |
| `state_5.sqlite` | 세션(thread) 목록·제목·작업 폴더·git 정보 | [2] |
| `thread_history_1.sqlite` | 턴과 항목(item) 사본 | [2][4] |
| `logs_2.sqlite` | 로그 줄 | [2] |
| `goals_1.sqlite`, `memories_1.sqlite` | 목표·메모리 기능용 DB | [2] |
| `log/` | 로그 폴더(`log_dir` 기본값) | [3] |
| `config.toml` | 사용자 설정 | [1][3] |
| `auth.json` | CLI 로그인 정보(`cli_auth_credentials_store = "file"`, 기본값) | [3] |
| `.credentials.json` | MCP 서버 OAuth 정보(키링을 쓸 수 없을 때) | [3] |
| `.tmp/rollout-compression.lock` | 마지막 rollout 압축 작업의 프로세스 번호와 시작 시각 | [2] |

SQLite 파일은 `CODEX_HOME` 이 아니라 `sqlite_home` 설정이 가리키는 폴더에 생깁니다. `sqlite_home` 의 기본값은 환경 변수 `CODEX_SQLITE_HOME` 이고, 그것도 없으면 `CODEX_HOME` 입니다[3]. 파일 이름의 숫자(`state_5`, `logs_2`)는 406dc92 기준이라 판이 바뀌면 달라질 수 있어서, 검체에서는 `*.sqlite` 로 모두 찾습니다. agentsview 문서(2026-09-11 수정)는 지금 판이 세션 제목을 `thread_history_*.sqlite` 에 두고, 2026-08-13 에 실제 `~/.codex` 에서 `session_index.jsonl` 이 없고 `thread_history_1.sqlite` 가 있는 것을 확인해 인덱스 파일이 없는 것이 정상이라고 적었습니다[4]. 406dc92 의 테이블 정의에서는 `title` 칸이 `state_5.sqlite` 의 `threads` 테이블에 있습니다[2].

로그인 정보는 `cli_auth_credentials_store` 로 저장 방식을 고릅니다. `file`(기본)은 `auth.json`, `keyring` 은 OS 키링, `auto` 는 키링을 먼저 쓰고 안 되면 파일, `ephemeral` 은 실행 중인 프로세스 메모리에만 둡니다[3]. MCP 서버의 OAuth 정보는 `mcp_oauth_credentials_store` 가 따로 정하고, 기본값 `auto` 는 키링을 먼저 쓰고 쓸 수 없으면 `.credentials.json` 에 둡니다[3]. 키링에 두었다면 Windows 는 [자격 증명 관리자와 볼트](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/credentials/credential-manager-windows-vault.html), macOS 는 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html)에서 찾습니다. 토큰이 남는 곳 전반은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

관찰한 PC 의 `%USERPROFILE%\.codex` 에는 파일이 11개 있었습니다. `hooks.json` 하나, `skills/<이름>/SKILL.md` 다섯 개, `skills/<이름>/<파일>.json` 다섯 개이고, `config.toml`·`auth.json`·`history.jsonl`·`sessions/` 는 없었습니다(확인 범위: Windows 11, 2026-09). Codex 를 실행하지 않아도 다른 도구가 이 폴더에 스킬·훅 파일을 둘 수 있으므로, 폴더가 있다는 사실만으로 Codex 를 썼다고 보지 않습니다.

## 구조

### rollout 파일

한 줄이 JSON 객체 하나이고, 모든 줄에 `timestamp` 가 있습니다. `ordinal` 은 있을 때만 적고, 나머지는 `type` 과 `payload` 두 칸입니다[2]. `timestamp` 는 줄을 쓴 순간의 UTC 시각을 `2026-09-01T03:04:05.678Z` 모양(밀리초까지, 끝에 `Z`)으로 적습니다[2].

| `type` | 담는 것 | 근거 |
|---|---|---|
| `session_meta` | 세션 머리. `id`, `timestamp`, `cwd`, `originator`, `cli_version`, `source`, `model_provider`, 있으면 `forked_from_id`·`parent_thread_id`·`agent_path`, 그리고 `git`(브랜치 등) | [2][4] |
| `turn_context` | 턴마다의 `turn_id`, `cwd`, `model`, `effort`, `approval_policy`, `sandbox_policy`, 있으면 `current_date`·`timezone` | [2][4] |
| `response_item` | 모델과 주고받은 항목. 아래 표 | [2][4] |
| `event_msg` | 진행 이벤트. `task_started`, `task_complete`, `turn_aborted`, `agent_message`, `token_count` 등 | [4] |
| `compacted` | 긴 대화를 줄인 요약 | [2] |
| `inter_agent_communication`, `inter_agent_communication_metadata`, `world_state` | 그 밖의 항목. 내용은 검체에서 확인 | [2] |

`response_item` 의 `payload.type` 은 다음과 같습니다[4].

| `payload.type` | 담는 것 |
|---|---|
| `message` | `role`(`user`·`assistant`)과 `content` 배열. 사용자 글은 `input_text`, 모델 글은 `output_text` 블록 |
| `function_call` | 도구 호출. `name`(`exec_command`, `shell`, `apply_patch`, `spawn_agent` 등), `call_id`, `arguments`(JSON 문자열) |
| `custom_tool_call` | 도구 호출. `apply_patch` 본문을 `input` 에 그대로 둠 |
| `function_call_output`, `custom_tool_call_output` | 같은 `call_id` 의 결과 |

`apply_patch` 호출에는 `file_path` 칸이 없습니다. 고친 파일은 패치 본문의 `*** Add File:`, `*** Update File:`, `*** Delete File:`, `*** Move to:` 줄에 적힌 경로로 알아냅니다[4]. `event_msg` 의 `token_count` 에는 누적 사용량과 마지막 턴 사용량(`info.last_token_usage`)이 함께 있습니다[4].

`session_meta.payload.originator` 가 `codex_exec` 이면 대화형 화면이 아니라 `codex exec` 로 돌린 비대화형 세션입니다[4]. 하위 에이전트 세션은 `source.subagent` 와 `parent_thread_id` 로 부모를 가리키고, 갈라져 나온(fork) 세션은 `forked_from_id` 로 원래 세션을 가리킵니다[2][4].

아래는 한 세션의 앞부분을 줄인 만든 예시입니다. ID·경로·시각은 모두 지어낸 값입니다.

```json
{"timestamp":"2026-09-01T03:04:05.678Z","type":"session_meta","payload":{"id":"0199aaaa-bbbb-7ccc-8ddd-eeeeffff0001","timestamp":"2026-09-01T03:04:05.600Z","cwd":"/home/user1/project-x","originator":"codex_cli_rs","cli_version":"0.0.0-example","source":"cli","model_provider":"openai"}}
{"timestamp":"2026-09-01T03:04:06.012Z","type":"turn_context","payload":{"turn_id":"turn-example-1","cwd":"/home/user1/project-x","model":"example-model","timezone":"Asia/Seoul"}}
{"timestamp":"2026-09-01T03:04:06.020Z","type":"response_item","payload":{"type":"message","role":"user","content":[{"type":"input_text","text":"테스트를 돌려 줘"}]}}
{"timestamp":"2026-09-01T03:04:09.441Z","type":"response_item","payload":{"type":"function_call","name":"exec_command","call_id":"call_example_1","arguments":"{\"cmd\":\"npm test\"}"}}
```

### `history.jsonl`

한 줄의 모양은 `{"session_id":"…","ts":…,"text":"…"}` 입니다[2]. `ts` 는 Unix 초(UTC 기준)이고, `session_id` 는 rollout 의 세션 ID 와 같은 값이라 두 파일을 이어 볼 수 있습니다. 줄 하나를 한 번에 쓰고 덧붙이며, 쓰는 동안 파일에 잠금을 겁니다. Unix 에서는 권한 0600 으로 만듭니다[2].

`[history]` 의 `persistence` 는 `save-all`(기본)과 `none` 두 값이고, `none` 이면 이 파일에 아무것도 쓰지 않습니다[2][3]. `max_bytes` 를 정하면 파일이 그 크기를 넘을 때 가장 오래된 줄부터 버려 `max_bytes` 의 80% 까지 줄입니다. 이때 파일 길이를 0 으로 잘랐다가 남길 줄을 처음부터 다시 씁니다[2]. 생산자 소스에서 이 파일에 줄을 덧붙이는 곳은 대화형 화면(TUI)의 입력 경로이고, `codex exec` 와 app-server 코드에는 그 호출이 없습니다[4].

### 상태 SQLite

406dc92 의 테이블 정의[2]에서 조사에 쓰는 칸은 다음과 같습니다. 칸은 판마다 추가되므로 검체에서는 `.schema` 로 먼저 확인합니다.

| 파일 · 테이블 | 칸 |
|---|---|
| `state_5.sqlite` · `threads` | `id`, `rollout_path`, `created_at`, `updated_at`, `source`, `model_provider`, `cwd`, `title`, `sandbox_policy`, `approval_mode`, `tokens_used`, `archived`, `archived_at`, `git_sha`, `git_branch`, `git_origin_url`, 뒤에 더한 `first_user_message`, `cli_version`, `created_at_ms`, `updated_at_ms`, `recency_at` 등 |
| `thread_history_1.sqlite` · `thread_turns` | `thread_id`, `turn_id`, `status`, `started_at`, `completed_at`, `duration_ms` |
| `thread_history_1.sqlite` · `thread_items` | `thread_id`, `turn_id`, `item_id`, `created_at_ms`, `item_json` |
| `logs_2.sqlite` · `logs` | `ts`, `ts_nanos`, `level`, `target`, `message`, `thread_id`, `process_uuid` |

`threads.rollout_path` 는 세션 파일의 경로를 적으므로, rollout 파일을 지웠어도 DB 에 경로와 제목이 남아 있을 수 있습니다. `thread_items.item_json` 은 대화 항목을 JSON 으로 담습니다. SQLite 를 읽는 일반 방법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html) 페이지에 있습니다.

### `config.toml`

TOML 형식이고, 조사에 쓰는 키는 다음과 같습니다[1][3].

| 키 | 뜻 |
|---|---|
| `[history]` `persistence`, `max_bytes` | 입력 기록을 남길지, 크기 상한 |
| `cli_auth_credentials_store`, `mcp_oauth_credentials_store` | 인증 정보를 둘 곳 |
| `sqlite_home`, `log_dir` | SQLite·로그 폴더를 옮겼는지 |
| `[mcp_servers.이름]` | MCP 서버. `command`, `args`, `env`, `env_vars`, `cwd`, `url`, `http_headers`, `env_http_headers`, `bearer_token_env_var`, `oauth`, `scopes`, `enabled_tools`, `disabled_tools`, `default_tools_approval_mode` 등 |
| `[hooks]` | 훅. 이벤트 이름 아래 `matcher` 와 `hooks` 목록 |
| `[otel]` | `exporter`(`none`, `statsig`, `otlp-http`, `otlp-grpc`), `log_user_prompt`, `environment` |

`[otel]` 의 `log_user_prompt` 는 기본이 `false` 라서 프롬프트 내용은 가려진 채 나가고, 켜야만 내용이 남습니다[1]. `[mcp_servers]` 의 `env` 나 `http_headers` 에 비밀 값이 그대로 적혀 있을 수 있으니 보고서에는 키 이름만 옮깁니다. MCP 전반은 [MCP 서버와 도구 호출 기록](mcp.md)에서 다룹니다.

설정 스키마의 훅 이벤트는 `PermissionRequest`, `PostCompact`, `PostToolUse`, `PreCompact`, `PreToolUse`, `SessionEnd`, `SessionStart`, `Stop`, `SubagentStart`, `SubagentStop`, `UserPromptSubmit` 입니다[3]. 이벤트마다 `matcher` 와 `hooks` 목록을 두고, 목록 항목은 `type`(`command`, `prompt`, `agent`)과 `command`, `commandWindows`, `timeout`, `async` 등을 담습니다[3]. 이 스키마는 `config.toml` 안에 적는 훅을 설명합니다. 관찰한 PC 의 `hooks.json` 도 이벤트 아래 `matcher`(문자열)와 `hooks`(목록)를 두는 같은 모양이었고, 이벤트는 PermissionRequest, PostToolUse, PreToolUse, Stop, UserPromptSubmit 이었습니다(확인 범위: Windows 11, 2026-09). `skills/<이름>/<파일>.json` 의 키는 `files`, `files.SKILL.md`, `version` 이었고, 이 파일의 용도는 공개 자료에 설명이 없어 검체에서 만든 도구를 먼저 가립니다.

### 구조화 로그 이벤트(OpenTelemetry)

내보내기 방식은 `otlp-http` 와 `otlp-grpc` 이고, 이벤트를 모았다가 비동기로 보내며 종료할 때 남은 것을 비웁니다[1][3].

| 이벤트 | 담는 것[1] |
|---|---|
| `codex.conversation_starts` | 모델, 추론 설정, 샌드박스·승인 정책 |
| `codex.api_request` | 시도, 상태·성공 여부, 걸린 시간, 오류 |
| `codex.sse_event` | 스트림 이벤트 종류, 성공 여부, 걸린 시간, 끝날 때의 토큰 수 |
| `codex.websocket_request`, `codex.websocket_event` | 요청 시간, 메시지마다 종류·성공 여부·오류 |
| `codex.user_prompt` | 프롬프트 길이. 내용은 켜기 전까지 가림 |
| `codex.tool_decision` | 도구 실행 승인·거부 결과 |
| `codex.tool_result` | 실행 시간, 성공 여부, 출력 일부 |

## 증거로서 의미

**증명하는 것.** rollout 파일은 그 계정의 `CODEX_HOME` 에서 이 세션이 열렸고, 어느 폴더(`cwd`)에서 어떤 모델로 무엇을 입력했고, 에이전트가 어떤 명령을 실행하고 어떤 파일에 패치를 적용하려 했는지를 순서대로 보여 줍니다. `function_call_output` 이 있으면 그 호출에 결과가 돌아온 기록이 있다는 뜻입니다. `originator` 로 대화형과 `codex exec` 를, `parent_thread_id`·`forked_from_id` 로 하위 에이전트와 갈라진 세션을 가릅니다. `history.jsonl` 은 세션 파일이 지워진 뒤에도 "이 시각에 이 세션 ID 로 이런 글을 입력한 기록이 있다" 고 말해 줍니다. `config.toml` 은 기록을 껐는지, 인증을 어디에 두게 했는지, 어떤 MCP 서버와 훅을 걸었는지를 보여 줍니다. 수집 서버에 `codex.tool_decision` 이 있으면 "이 시각에 이 도구 실행을 승인(또는 거부)한 기록이 있다" 고 쓸 수 있습니다.

**증명하지 못하는 것.** rollout 의 `function_call` 은 에이전트가 실행을 요청한 기록이라서, 명령이 실제로 파일을 바꿨는지는 파일 시스템·git 이력과 맞춰 봐야 합니다. 입력한 사람이 누구인지는 계정만으로 정해지지 않으므로 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 좁힙니다. `history.jsonl` 이 비어 있어도 Codex 를 쓰지 않았다고 할 수 없습니다. `persistence = "none"` 이거나, `codex exec` 로만 썼거나, `max_bytes` 로 앞부분이 잘렸을 수 있습니다. 수집 서버의 이벤트는 기본 설정에서 프롬프트 내용이 가려지므로, 무엇을 시켰는지는 기기 쪽 기록으로 채웁니다.

## 시각 해석

| 값 | 기준 | 바뀌는 때 |
|---|---|---|
| rollout 날짜 폴더와 파일 이름 | 그 PC 의 현지 시각 | 세션을 만들 때 한 번 |
| rollout 줄의 `timestamp` | UTC, 밀리초 | 줄을 쓸 때마다 |
| `turn_context.timezone`, `current_date` | 턴을 시작할 때의 시간대와 날짜(있을 때만) | 턴마다 |
| `history.jsonl` 의 `ts` | Unix 초(UTC) | 입력할 때마다 |
| `threads.created_at`·`updated_at` (뒤에 `_ms` 가 붙은 칸) | Unix 초 (`_ms` 는 밀리초) | 세션을 만들 때 / 갱신할 때 |
| `.jsonl.zst` 의 수정 시각 | 압축 전 원본의 수정 시각을 옮겨 적음 | 압축할 때 |

폴더와 파일 이름은 현지 시각이고 줄 안의 `timestamp` 는 UTC 라서, 한국 시간대(UTC+9) PC 에서 오전 9시 전에 연 세션은 폴더 날짜가 첫 줄의 UTC 날짜보다 하루 뒤입니다[2]. 폴더 날짜로 사건일을 정하지 말고 줄의 `timestamp` 로 정한 뒤, `turn_context.timezone` 과 운영체제 시간대 설정으로 현지 시각을 붙입니다. coding-agent-forensics 도 Codex CLI 기록에 시작한 곳의 시간대가 남는다고 적습니다[5]. `thread_items.created_at_ms` 와 `thread_turns.started_at` 같은 DB 시각은 rollout 에서 옮긴 값이므로 rollout 과 어긋나면 rollout 을 먼저 봅니다. 여러 출처를 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

- **폴더를 옮겨 쓴 경우.** `CODEX_HOME`, `CODEX_SQLITE_HOME`, `sqlite_home`, `log_dir` 를 바꾸면 `~/.codex` 에는 일부만 있거나 아무것도 없을 수 있습니다[3]. 사용자 환경 변수와 셸 설정 파일에서 이 이름들을 먼저 찾습니다.
- **압축된 rollout.** 406dc92 의 압축 작업은 수정한 지 7일이 지난 rollout 을 같은 폴더에 `.jsonl.zst` 로 압축하고, 원래 `.jsonl` 은 지웁니다[2]. 다른 세션이 가리키는 rollout 은 압축하지 않습니다. 압축 파일에서는 문자열 검색이 걸리지 않으므로 사본에서 풀어서 검색합니다. 지운 원래 파일은 할당되지 않은 영역에 남아 있을 수 있습니다.
- **이어받은 기록의 중복.** 갈라진 세션과 하위 에이전트의 rollout 은 부모 대화를 다시 적은 줄로 시작할 수 있고, 그 안에는 부모의 `token_count` 도 들어 있습니다[4]. 부모 파일과 겹치는 턴(`turn_context.turn_id` 가 같은 턴)을 빼지 않으면 입력 횟수와 사용량을 두 번 셉니다.
- **입력 기록 끄기와 세션 기록은 별개.** `[history] persistence = "none"` 은 `history.jsonl` 만 막습니다[3]. rollout 은 그대로 생기므로 `history.jsonl` 이 없다는 사실로 기록 전체가 꺼졌다고 보지 않습니다.
- **잘린 입력 기록.** `max_bytes` 로 앞부분이 버려지는 것은 설정에 따른 정상 동작이라서, 첫 줄이 늦다고 조작으로 보면 안 됩니다. `persistence` 를 사건 전후로 바꿨는지는 `config.toml` 의 수정 시각과 백업으로 봅니다. 보관·삭제 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.
- **읽을 수 없는 항목.** 다중 에이전트 도구의 `encrypted_content` 에는 평문 대신 `gAAAAA` 로 시작하는 암호화된 값이 들어 있을 수 있습니다[4]. agentsview 는 이 값을 풀지 않고 표시에서 뺍니다[4]. 보고서에는 "내용 암호화" 라고 적습니다.
- **같은 모양의 다른 도구.** TRAE CLI 2.0 도 Codex 와 같은 모양의 rollout 을 쓰고 `originator` 에 `codex-tui` 를 적는다고 agentsview 가 적었습니다[4]. 형식만 보고 Codex 라고 단정하지 말고 폴더 위치와 설치 흔적으로 도구를 가립니다.
- **로그인 정보.** `auth.json` 과 `.credentials.json` 은 토큰을 담으므로, 파일이 있었다는 사실과 수정 시각만 보고서에 적고 값은 가립니다.

## 직접 분석해 보기

**헥스로 한 번.** rollout 의 모든 줄은 `{"timestamp":"` 로 시작하고 `0A` 로 끝나므로, 지운 rollout 을 할당되지 않은 영역에서 찾을 때 이 바이트열을 기준으로 삼습니다. `history.jsonl` 줄은 `{"session_id":"` 로 시작합니다. 아래 바이트는 문자 인코딩대로 옮긴 만든 예시이고, 검체에서 뜬 값이 아닙니다.

```
만든 예시(인코딩으로 옮긴 바이트)
{"timestamp":"      7B 22 74 69 6D 65 73 74 61 6D 70 22 3A 22
"type":"session_meta"  22 74 79 70 65 22 3A 22 73 65 73 73 69 6F 6E 5F 6D 65 74 61 22
{"session_id":"     7B 22 73 65 73 73 69 6F 6E 5F 69 64 22 3A 22
줄 끝(LF)            0A
```

찾은 덩어리가 온전한 JSON 인지 한 줄씩 다시 확인하고, `session_meta` 줄이 있으면 그 `id` 로 원래 파일 이름과 `threads.rollout_path` 를 찾아 맞춥니다.

**공개 도구로 한 번.** 수집한 사본에서 jq·sqlite3·zstd 로 봅니다. 경로는 만든 예시이고, 원본이 아니라 사본에서만 돌립니다.

```sh
# 만든 예시 경로
CX=/cases/case-0001/copy/user1/.codex
# 세션 파일 목록(압축본 포함)
find "$CX/sessions" "$CX/archived_sessions" -name 'rollout-*.jsonl*'
# 압축본은 사본 폴더에 풀어서 본다
zstd -d -o /cases/case-0001/work/r1.jsonl "$CX/sessions/2026/09/01/rollout-2026-09-01T12-04-05-example.jsonl.zst"
# 줄 종류별 개수
jq -r '.type + "/" + (.payload.type // "")' /cases/case-0001/work/r1.jsonl | sort | uniq -c
# 실행 요청한 명령만 시각과 함께
jq -r 'select(.type=="response_item" and .payload.type=="function_call") | [.timestamp, .payload.name, .payload.arguments] | @tsv' /cases/case-0001/work/r1.jsonl
# 입력 기록을 사람이 읽는 UTC 시각으로
jq -r '[(.ts|todate), .session_id, .text] | @tsv' "$CX/history.jsonl"
# 세션 목록
sqlite3 "$CX/state_5.sqlite" "SELECT id, datetime(created_at,'unixepoch'), cwd, title, archived, rollout_path FROM threads;"
```

agentsview[4]는 Codex rollout 을 읽어 세션·도구 호출·사용량으로 정리하고, coding-agent-forensics[5]는 브라우저에서 세션 파일을 열어 타임라인과 파일 변경을 보여 줍니다. 두 도구 모두 판이 바뀌면 읽지 못하는 칸이 생길 수 있으므로 결과를 위의 jq 출력과 맞춰 봅니다.

## 교차 검증

에이전트가 실행한 명령과 고친 파일은 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)의 흐름으로 셸 기록·git 이력과 맞추고, rollout 의 `git` 과 `threads.git_sha` 를 커밋 이력과 비교합니다. 인증 파일이나 비밀 값을 건드린 정황은 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md)에서 다룹니다.

디스크에 기록이 없어도 Codex 가 실행 중일 때 뜬 메모리에서는 MCP 요청·응답을 되살릴 수 있습니다. Satter 등의 연구는 Ubuntu 24.04 가상 머신에서 Codex CLI 와 MCP 서버를 돌린 뒤 메모리 이미지에서 `tools/list`·`tools/call` JSON-RPC 메시지를 되살렸고, stdio 방식 MCP 서버와의 통신은 소켓을 거쳤다고 적었습니다[6]. 여러 클라이언트를 함께 돌린 경우에는 일부 요청의 흔적이 메모리 이미지에 없었고, 연구진은 메모리에 없다는 것이 실행하지 않았다는 증거는 아니라고 적었습니다[6]. 방법은 [메모리에서 AI 흔적 찾기](../../03-techniques/analysis/memory-analysis.md)와 [MCP 서버와 도구 호출 기록](mcp.md)에 있습니다.

같은 PC 에 [Claude Code](claude-code/index.md)나 [Gemini CLI](gemini-cli.md)가 함께 있으면 훅·스킬 파일이 어느 도구 것인지 먼저 나눕니다. 서비스 접속은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)과, 웹 ChatGPT 쪽 흔적은 [ChatGPT](../chat-services/chatgpt/index.md)와 이어 봅니다.

## 실습

시험용 가상 머신과 시험 계정으로 검체를 만들어 풉니다.

1. 기본 설정으로 대화형 세션을 두 번 연 뒤 `~/.codex` 에 생긴 파일을 모두 적고, rollout 의 줄 종류와 `history.jsonl` 의 줄을 세션 ID 로 이어 봅니다.
2. 같은 요청을 `codex exec` 로 한 번 실행하고, rollout 의 `originator` 와 `history.jsonl` 에 줄이 생겼는지 비교합니다.
3. 시간대를 UTC+9 로 두고 오전 9시 전에 세션을 열어, 폴더 날짜와 첫 줄 `timestamp` 의 날짜가 어떻게 다른지 적습니다.
4. `persistence = "none"` 으로 바꾼 뒤 다시 입력해, 무엇이 더 이상 생기지 않고 무엇은 계속 생기는지 확인합니다.
5. 운영체제 시계를 8일 뒤로 옮겨 Codex 를 다시 실행한 뒤, `.jsonl.zst` 가 생겼는지와 그 수정 시각이 원본과 같은지 봅니다.

## 참고 문헌

1. OpenAI Codex — Advanced configuration — https://learn.chatgpt.com/docs/config-file/config-advanced
2. openai/codex, 커밋 406dc9239492aff6d295cca5eebe2a548548d42f(2026-07-30) — https://github.com/openai/codex — `codex-rs/rollout/src/recorder.rs`, `codex-rs/rollout/src/compression.rs`, `codex-rs/rollout/src/lib.rs`, `codex-rs/message-history/src/lib.rs`, `codex-rs/protocol/src/protocol.rs`, `codex-rs/state/src/sqlite.rs`, `codex-rs/state/src/runtime/threads.rs`, `codex-rs/state/migrations/0001_threads.sql`·`0005_threads_cli_version.sql`·`0007_threads_first_user_message.sql`·`0025_thread_timestamps_millis.sql`·`0039_threads_recency_at.sql`, `codex-rs/state/logs_migrations/0001_logs.sql`, `codex-rs/state/thread_history_migrations/0001_thread_history.sql`
3. openai/codex, 같은 커밋 — `codex-rs/core/config.schema.json`
4. kenn-io/agentsview — https://github.com/kenn-io/agentsview — `docs/internal/session-format-sources.md`(2026-09-11 수정), `internal/parser/codex.go`, `internal/parser/codex_provider.go`, `internal/parser/codex_metadata.go`
5. Shorton88/coding-agent-forensics — https://github.com/Shorton88/coding-agent-forensics — `README.md`
6. Satter, A., Salmon, M., Muhanna, L., Spinosa, T. T., Gharaibeh, T., Baggili, I., "With or Without Logs: Memory Forensic Reconstruction of Model Context Protocol (MCP) Activity in Agentic LLM Systems", DFRWS USA 2026 — https://dfrws.org/presentation/with-or-without-logs-reconstructing-model-context-protocol-activity-from-volatile-memory/ — 도구: https://github.com/BiTLab-BaggiliTruthLab/MCPRecon
