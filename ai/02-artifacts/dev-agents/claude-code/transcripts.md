---
title: "세션 기록 구조"
parent: "Claude Code"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 550
---

# 세션 기록 구조 (Transcripts)

Claude Code 는 세션마다 대화 전문과 도구 호출·결과를 JSON Lines 파일 하나에 평문으로 쌓고, 따로 입력 이력, 편집 전 파일 사본, 사용량 합계를 남깁니다.

> 확인 날짜: 2026-09. 파일 종류와 자동 삭제는 공식 문서(2026-09-25 열람)로, 키 이름은 기기 관찰로 확인했습니다. 기기 관찰은 각 기록 파일의 처음 300줄에서 키 이름과 값의 종류만 본 것이고 값은 가렸습니다(확인 범위: Windows 11, 2026-09). 기록 형식에는 공개 규격 문서가 없어서 버전마다 키가 바뀔 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

세션 기록 파일에는 사용자가 보낸 메시지, 모델의 답, 모델이 부른 도구와 그 입력, 도구가 돌려준 결과가 차례로 한 줄씩 들어가고, 훅이 받는 입력의 `transcript_path` 도 이 파일을 가리킵니다. 입력 이력은 위 화살표로 예전 프롬프트를 불러오거나 Ctrl+R 로 찾을 때 쓰고, 편집 전 파일 사본은 되돌리기(체크포인트)에 씁니다. 기록과 이력은 저장할 때 암호화하지 않고 OS 파일 권한으로만 보호합니다. 폴더 위치는 OS 마다 [Windows](windows.md), [macOS](macos.md) 페이지에 있습니다.

## 위치와 파일 종류

아래 경로는 모두 `~/.claude/` 기준입니다.

| 경로 | 담긴 것 | 자동 삭제 |
|---|---|---|
| `projects/<프로젝트>/<세션>.jsonl` | 대화 전문, 도구 호출과 결과 | 대상 |
| `projects/<프로젝트>/<세션>.orphaned-<시각>-<접미사>.jsonl` | 덮어쓰는 대신 떼어 둔 이전 기록 | 대상 |
| `projects/<프로젝트>/<세션>.jsonl.superseded-<시각>` | 기록의 이전 판 | 대상 |
| `projects/<프로젝트>/<세션>/subagents/` | 하위 에이전트 기록(부모와 함께 지움) | 대상 |
| `projects/<프로젝트>/<세션>/tool-results/` | 큰 도구 출력 | 대상 |
| `projects/<프로젝트>/memory/` | 프로젝트별 자동 메모리(`MEMORY.md` 와 주제별 .md) | 아님 |
| `history.jsonl` | 입력한 프롬프트, 시각, 프로젝트 경로 | 아님 |
| `paste-cache/<파일>.txt` | 큰 붙여넣기 내용 | 대상 |
| `file-history/<세션>/` | 편집 전 파일 사본 | 대상 |
| `stats-cache.json` | `/usage` 용 토큰·비용 합계 | 아님 |
| `debug/<세션 ID>.txt` | `--debug` 나 `/debug` 로 켠 디버그 로그 | 대상 |
| `feedback/drafts/` | 피드백 초안(최대 10개, 넘치면 가장 오래된 것부터 지움) | 대상 |
| `jobs/<이름>/state.json`, `timeline.jsonl` | 백그라운드 작업 상태와 경과 | 아님 |

관찰한 PC 에서는 하위 에이전트 기록이 `projects/` 아래 프로젝트 폴더, 세션 ID 폴더, `subagents/workflows/` 아래 이름 폴더를 거친 JSON Lines 파일로 있었고, `debug/` 에는 `latest` 가 있었습니다(확인 범위: Windows 11, 2026-09). 프로젝트 폴더 이름을 작업 경로에서 어떻게 바꿔 만드는지는 문서에서 확인하지 못해서, 폴더 이름으로 작업 경로를 되짚지 말고 기록 줄의 `cwd` 값을 봅니다.

## 구조

### 세션 기록 한 줄

파일은 JSON Lines 형식이라 한 줄에 JSON 객체가 하나씩 들어갑니다. 관찰한 키를 쓰임에 따라 묶으면 다음과 같습니다(확인 범위: Windows 11, 2026-09).

| 묶음 | 키 |
|---|---|
| 줄마다 붙는 것 | `type`, `uuid`, `parentUuid`, `sessionId`, `timestamp`, `cwd`, `gitBranch`, `version`, `entrypoint`, `userType`, `isSidechain` |
| 메시지 | `message.role`, `message.content`(문자열 또는 목록), `message.model`, `message.id`, `message.stop_reason`, `requestId` |
| 메시지 내용 목록 안 | `type`, `text`, `thinking`, `signature`, `name`, `input`, `id`, `tool_use_id`, `content`, `is_error`, `caller` |
| 사용량 | `message.usage.input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `service_tier`, `inference_geo`, `speed`, `server_tool_use.web_search_requests`, `server_tool_use.web_fetch_requests`, `output_tokens_details.thinking_tokens` |
| 도구 결과 | `toolUseResult.stdout`, `stderr`, `interrupted`, `isImage`, `success`, `commandName`, `allowedTools`, `noOutputExpected`, `sourceToolAssistantUUID`, `sourceToolUseID` |
| 훅 실행 요약 | `hookCount`, `hookInfos[].command`, `hookInfos[].durationMs`, `hookErrors`, `hookAdditionalContext`, `preventedContinuation`, `stopReason`, `level` |
| 덧붙임 | `attachment.type`, `hookEvent`, `hookName`, `command`, `exitCode`, `stdout`, `stderr`, `durationMs`, `toolUseID`, `text` 등 |
| 되돌리기 스냅숏 | `snapshot.messageId`, `snapshot.timestamp`, `snapshot.trackedFileBackups`, `isSnapshotUpdate` |
| 그 밖 | `permissionMode`, `promptId`, `promptSource`, `effort`, `mode`, `aiTitle`, `lastPrompt`, `leafUuid`, `bridgeSessionId`, `ownerAccountUuid`, `ownerOrganizationUuid`, `attributionSkill`, `attributionPlugin`, `origin.kind`, `isMeta`, `subtype` |

관찰한 파일에서 `parentUuid` 는 한 줄만 null 이고 나머지 줄에서는 문자열이었습니다. 키 이름과 이 모양으로 보아 각 줄이 앞 줄의 `uuid` 를 가리켜 대화 순서를 잇는 것으로 보이지만, 값을 대조해 확인하지는 않았습니다. `type`, `entrypoint`, `permissionMode` 에 어떤 값이 들어가는지도 값을 가려서 알 수 없습니다. 권한 모드 이름은 문서에 나와 있고 [설정·권한·훅](settings-permissions.md)에서 다루지만, 기록의 `permissionMode` 값이 그 이름과 같은지는 검체에서 확인합니다.

하위 에이전트 기록에도 같은 키가 대부분 나오고, `agentId`, `attributionAgent`, `toolEndsTurn` 이 더 있었습니다.

아래는 키 이름만 관찰과 맞추고 값은 모두 새로 만든 예시입니다. `type` 값과 시각 문자열의 모양, 도구 이름도 만든 것입니다.

```json
{"type":"user","uuid":"11111111-2222-4333-8444-000000000001","parentUuid":null,"sessionId":"0f0f0f0f-aaaa-4bbb-8ccc-000000000123","timestamp":"2026-09-03T05:40:12.000Z","cwd":"C:\\dev\\toy-shop","gitBranch":"fix-cart-total","version":"2.x.x","isSidechain":false,"message":{"role":"user","content":"장바구니 합계 계산 버그를 찾아 줘"}}
{"type":"assistant","uuid":"11111111-2222-4333-8444-000000000002","parentUuid":"11111111-2222-4333-8444-000000000001","sessionId":"0f0f0f0f-aaaa-4bbb-8ccc-000000000123","timestamp":"2026-09-03T05:40:15.000Z","message":{"role":"assistant","model":"(모델 이름)","content":[{"type":"tool_use","id":"toolu_example01","name":"Read","input":{"file_path":"C:\\dev\\toy-shop\\src\\cart.js"}}]}}
```

### 입력 이력 history.jsonl

사용자가 입력한 프롬프트를 시각, 프로젝트 경로와 함께 한 줄씩 남깁니다. 관찰한 키는 `display`, `project`, `sessionId`, `timestamp`(정수), `pastedContents` 와 그 아래 번호별 `id`, `type`, `content`, `contentHash` 입니다(확인 범위: Windows 11, 2026-09). 관찰한 줄 가운데 일부에는 `sessionId` 가 없었습니다. 큰 붙여넣기 내용은 `paste-cache/` 의 텍스트 파일로 따로 빠지지만, `contentHash` 와 그 파일을 어떻게 잇는지는 확인하지 못했습니다.

```json
{"display":"장바구니 합계 계산 버그를 찾아 줘","pastedContents":{},"timestamp":1788414012000,"project":"C:\\dev\\toy-shop","sessionId":"0f0f0f0f-aaaa-4bbb-8ccc-000000000123"}
```

위 줄도 만든 예시입니다.

### 편집 전 파일 사본 file-history

사용자가 프롬프트를 보내 턴을 시작할 때마다 체크포인트를 만들고, Claude 가 파일 편집 도구로 바꾸기 전의 파일 사본을 `file-history/<세션>/` 에 둡니다. 세션마다 최근 체크포인트 100개를 남기고, 오래된 체크포인트를 버려도 파일별 첫 사본은 남깁니다. Bash 명령(`rm`, `mv`, `cp` 등)으로 바꾼 파일, 사용자가 직접 바꾼 파일, 다른 세션의 편집은 추적하지 않고, 하위 에이전트의 편집도 대부분 잡히지 않습니다.

### 사용량 합계 stats-cache.json

`/usage` 가 보여 주는 토큰·비용 합계입니다. 관찰한 키는 날짜별 활동(`dailyActivity[].date`, `messageCount`, `sessionCount`, `toolCallCount`), 날짜별 모델 토큰(`dailyModelTokens[].tokensByModel`), `firstSessionDate`, `lastComputedDate`, 시간대별 횟수(`hourCounts`), 가장 긴 세션(`longestSession.sessionId`, `duration`, `messageCount`, `timestamp`), 모델별 사용량(`modelUsage` 아래 `inputTokens`, `outputTokens`, `cacheCreationInputTokens`, `cacheReadInputTokens`, `costUSD`, `webSearchRequests` 등), `totalSessions`, `totalMessages` 입니다(확인 범위: Windows 11, 2026-09).

### 그 밖의 기록

피드백 초안에서는 `draft_id`, `created_at`, `cli_version`, `os`, `model`, `cwd`, `source_session_id`, `transcript_ref.session_file`, `transcript_ref.project_dir_key`, `request_ids`, `status`, `title` 같은 키를 보았고, 초안이 어느 세션 기록을 가리키는지 알려 줍니다. 백그라운드 작업의 `state.json` 에는 `sessionId`, `resumeSessionId`, `cwd`, `cliVersion`, `createdAt`, `updatedAt`, `state`, `intent`, `tokens` 가, `timeline.jsonl` 에는 `at`, `state`, `text`, `detail` 이 있었습니다(확인 범위: Windows 11, 2026-09). 서드파티 모델 공급자를 쓸 때 만드는 피드백 묶음은 `~/.claude/feedback-bundles/` 에 알려진 키·토큰 패턴을 가린 기록 압축본으로 남습니다.

## 자동 삭제와 남는 것

`cleanupPeriodDays` 는 기본 30일이고 최소 1이며, 0 을 넣으면 설정 검증에서 걸립니다. 기한이 지나면 세션 기록과 그 변형, `subagents/`, `tool-results/`, 세션별 `file-history/`, `debug/`, `plans/`, `shell-snapshots/`, `session-env/`, `paste-cache/`, `image-cache/`, `uploads/`, `tasks/`, `backups/`, `feedback/drafts/`, `usage-data/` 를 지웁니다. `history.jsonl`, `stats-cache.json`, `jobs/`, `daemon/`, `agent-memory/`, 프로젝트별 자동 메모리는 지우지 않아서, 원본 기록이 사라진 뒤에도 언제 어떤 프로젝트에서 무엇을 입력했는지, 하루에 얼마나 썼는지는 따로 가늠할 수 있습니다.

데스크톱 앱이나 Cowork 에서 시작했거나 마지막으로 이어 간 세션 기록은 v2.1.248 부터 기본으로 기한 없이 남고 `desktopSessionCleanupPeriodDays` 로 기한을 둘 수 있으며, 그 전 버전은 `cleanupPeriodDays` 에 따라 지웁니다. 관리 정책이 `cleanupPeriodDays` 를 주면 이 기록도 그 기한 뒤 지웁니다. 설정 파일을 읽지 못하거나 `--bare` 로 돌 때는 청소를 멈추고, 관리 정책이 `cleanupPeriodDays` 를 주면 그 값으로 돕니다.

사용자가 지우는 방법도 있습니다. `claude project purge` 는 그 프로젝트의 기록, 자동 메모리, 세션별 tasks·debug·file-history, `history.jsonl` 의 해당 줄, `~/.claude.json` 의 프로젝트 항목을 한꺼번에 지웁니다. `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켜면 기록과 이력을 처음부터 쓰지 않아서, 기록이 비어 있는 까닭이 삭제가 아니라 설정일 수도 있습니다. 보관 설정과 삭제의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 세션 기록은 이 PC 의 이 사용자 폴더에서 돈 세션이 어떤 작업 폴더(`cwd`)와 브랜치(`gitBranch`)에서 어떤 프롬프트를 받았고, 모델이 어떤 도구를 어떤 입력으로 불렀으며, 도구가 무엇을 돌려줬는지 보여 줍니다. `.env` 를 읽었거나 비밀값을 출력한 세션이면 그 내용도 기록에 그대로 남습니다. 보고서에는 "이 세션 기록에 이 시각, 이 작업 폴더에서 이 명령을 실행한 도구 호출과 그 출력이 있다" 처럼 기록이 말하는 만큼만 씁니다.

**증명하지 못하는 것.** 도구 호출 줄이 있어도 그 결과로 파일이 지금 디스크에 어떤 상태인지는 알려 주지 않고, 사용자가 직접 바꾼 파일이나 Bash 로 바꾼 파일은 편집 전 사본도 없습니다. 기록은 그 계정으로 누가 입력했는지 알려 주지 않습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 모델이 보낸 답을 사용자가 실제로 읽었는지도 알 수 없습니다.

## 시각 해석

세션 기록의 `timestamp` 와 `snapshot.timestamp` 는 문자열이고, `history.jsonl` 의 `timestamp` 는 정수입니다(확인 범위: Windows 11, 2026-09). 값을 가려서 문자열에 시간대 표기가 붙는지, 정수가 초인지 밀리초인지는 확인하지 못했고, 검체에서 자릿수와 끝 글자를 먼저 봅니다. 같은 프롬프트가 세션 기록과 `history.jsonl` 에 모두 있으면 두 시각을 맞춰 보는 방법으로 형식을 가려낼 수 있습니다. 기록 파일의 생성 시각과 마지막 쓰기 시각은 대략 세션의 첫 활동과 마지막 활동을 가리킬 수 있지만, 세션을 이어 가거나 파일을 복사하면 달라질 수 있어서 기록 안의 시각을 우선합니다.

## 함정과 한계

기록 형식은 공개 규격이 없어서 키가 버전마다 바뀔 수 있고, 그래서 분석 결과에는 기록 줄의 `version` 값을 함께 적습니다. `/compact` 나 Summarize 로 대화를 요약해도 원래 메시지는 기록 파일에 그대로 남아서, 파일이 화면에 보이던 대화보다 깁니다.

한 세션의 기록이 파일 하나에만 있지도 않습니다. `.orphaned-` 나 `.superseded-` 가 붙은 파일도 같은 세션의 기록이라 세션 ID 에 `.jsonl` 을 붙인 이름으로만 찾으면 빠뜨리기 쉽고, 큰 도구 출력은 `tool-results/` 로, 큰 붙여넣기는 `paste-cache/` 로 빠져서 기록 줄만 보면 내용이 잘려 보일 수 있습니다.

기록이 없는 까닭도 30일 청소, `claude project purge`, `CLAUDE_CODE_SKIP_PROMPT_HISTORY`, 클라우드 세션처럼 여러 가지입니다. 삭제인지 설정인지 가르려면 `history.jsonl` 과 `stats-cache.json` 이 남아 있는지부터 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 JSON Lines 명세와 위의 만든 예시 줄로 만든 바이트이고, 실제 파일에서 뜬 것이 아닙니다. 줄마다 `7B`(`{`)로 시작하고 JSON Lines 규칙대로 `0A`(줄바꿈)로 끝납니다. 실제 파일의 키 순서와 줄 끝 바이트는 검체에서 확인합니다.

```
만든 예시(명세로 만든 바이트)
00000000  7B 22 74 79 70 65 22 3A 22 75 73 65 72 22 2C 22  {"type":"user","
```

**공개 도구로 한 번.** 사본에서 jq 로 읽습니다. `type` 값을 먼저 세어 보고, 그 결과에 맞춰 도구 호출 줄을 뽑습니다. 아래 파일 이름과 `"assistant"`, `"tool_use"` 값은 만든 예시에 맞춘 것이라 검체의 실제 값으로 바꿉니다.

```sh
# 만든 예시 파일 이름
F=0f0f0f0f-aaaa-4bbb-8ccc-000000000123.jsonl
jq -r '.type' "$F" | sort | uniq -c
jq -r '[.timestamp, .type, (.permissionMode // "")] | @tsv' "$F"
jq -c 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | {name, input}' "$F"
jq -c 'select(.hookInfos) | .hookInfos[] | {command, durationMs}' "$F"
```

## 교차 검증

기록의 도구 호출 시각은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 파일 시스템 시각, 셸 이력과 함께 올리고, 기록에 남은 권한 모드와 훅 흔적은 [설정·권한·훅](settings-permissions.md)의 설정 파일과 맞춰 봅니다. MCP 도구 호출은 [MCP 서버와 도구 호출 기록](../mcp.md)과, 도구 출력에 외부 문서가 섞였다면 [프롬프트 인젝션 사고 분석](../../../03-techniques/analysis/prompt-injection.md)과 이어 봅니다. 에이전트가 한 일을 순서대로 정리하는 흐름은 [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)에 있고, 지운 기록을 되살리는 방법은 [대화 내용 되살리기](../../../03-techniques/analysis/content-recovery.md)에 있습니다.

## 실습

공개 검체에 Claude Code 흔적이 들어 있는지는 확인하지 못했습니다. 시험용 가상 머신에서 가짜 저장소를 만들고 세션을 돌려 풀어 봅니다.

1. 파일 하나를 편집 도구로 고치고, 다른 파일은 Bash 로 지우게 한 뒤 `file-history/` 에 무엇이 남는지 비교합니다.
2. `/compact` 를 한 번 한 세션에서 요약 전 메시지가 기록 파일에 남아 있는지 확인합니다.
3. `cleanupPeriodDays` 를 1로 두고 이틀 뒤 `history.jsonl` 과 `stats-cache.json` 에 남은 것으로 지워진 세션의 날짜와 프로젝트를 되짚어 봅니다.
4. 같은 프롬프트의 `history.jsonl` 시각과 세션 기록 시각을 맞춰 보고, 정수 시각의 단위를 가려냅니다.

## 참고 문헌

1. Hooks reference — https://code.claude.com/docs/en/hooks
2. Data usage — https://code.claude.com/docs/en/data-usage
3. .claude 폴더 파일·폴더 참조(claude-directory) — https://code.claude.com/docs/en/claude-directory
4. Configure permissions — https://code.claude.com/docs/en/permissions
5. Checkpointing — https://code.claude.com/docs/en/checkpointing
