---
title: "세션 기록 구조"
parent: "Claude Code"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 580
---

# 세션 기록 구조 (Transcripts)

Claude Code 는 세션마다 대화 전문과 도구 호출·결과를 JSON Lines 파일 하나에 평문으로 쌓고, 따로 입력 이력, 편집 전 파일 사본, 프로세스 상태, 셸 환경 사본, 사용량 합계를 남깁니다.

이 쪽의 키는 Claude Code 2.1.104~2.1.282 (Windows 11) 기준이고, 기록 형식에는 공개 규격 문서가 없어서 판마다 키가 바뀔 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

세션 기록 파일에는 사용자가 보낸 메시지, 모델의 답, 모델이 부른 도구와 그 입력, 도구가 돌려준 결과가 차례로 한 줄씩 들어가고, 훅이 받는 입력의 `transcript_path` 도 이 파일을 가리킵니다[1]. 입력 이력은 위 화살표로 예전 프롬프트를 불러오거나 Ctrl+R 로 찾을 때 쓰고, 편집 전 파일 사본은 되돌리기(체크포인트)에 씁니다[3][5]. 기록과 이력은 저장할 때 암호화하지 않고 OS 파일 권한으로만 보호합니다[2]. 폴더 위치는 OS 마다 [Windows](windows.md), [macOS](macos.md) 페이지에 있습니다.

## 위치와 버전별 차이

아래 경로는 모두 `~/.claude/` 기준입니다. "자동 삭제" 칸의 "목록에 없음" 은 청소 대상 목록[3]에 들지 않은 항목입니다.

| 경로 | 담긴 것 | 자동 삭제 | 근거 |
|---|---|---|---|
| `projects/<프로젝트>/<세션>.jsonl` | 대화 전문, 도구 호출과 결과 | 대상 | [3] |
| `projects/<프로젝트>/<세션>.orphaned-<시각>-<접미사>.jsonl` | 덮어쓰는 대신 떼어 둔 이전 기록 | 대상 | [3] |
| `projects/<프로젝트>/<세션>.jsonl.superseded-<시각>` | 기록의 이전 판 | 대상 | [3] |
| `projects/<프로젝트>/<세션>/subagents/agent-<ID>.jsonl` | 하위 에이전트 기록(부모와 함께 지움) | 대상 | [3][7] |
| `projects/<프로젝트>/<세션>/subagents/workflows/<워크플로 ID>/agent-<ID>.jsonl` | 워크플로 도구가 띄운 하위 에이전트 기록 | 대상 | [7] |
| 위 두 경로의 `agent-<ID>.meta.json` | 하위 에이전트 부가 정보 | 대상 | [7] |
| `projects/<프로젝트>/<세션>/tool-results/` | 큰 도구 출력 | 대상 | [3][7] |
| `projects/<프로젝트>/memory/` | 프로젝트별 자동 메모리(`MEMORY.md` 와 주제별 .md) | 아님 | [3] |
| `history.jsonl` | 입력한 프롬프트, 시각, 프로젝트 경로 | 아님 | [3][6][8] |
| `paste-cache/<해시>.txt` | 큰 붙여넣기 내용 | 대상 | [3][6] |
| `file-history/<세션>/<해시>@v<번호>` | 편집 전 파일 사본 | 대상 | [3][6] |
| `sessions/<PID>.json` | 실행 중이던 프로세스의 세션 ID, 작업 폴더, 상태 | 목록에 없음 | [6][8] |
| `shell-snapshots/snapshot-bash-<밀리초>-<임의 문자>.sh`(zsh 면 `snapshot-zsh-`) | Bash 도구가 쓴 셸 환경 사본 | 대상 | [3][6] |
| `.last-cleanup` | 마지막 자동 삭제 시각 | 목록에 없음 | [6] |
| `stats-cache.json` | `/usage` 용 토큰·비용 합계 | 아님 | [3] |
| `debug/<세션 ID>.txt` | `--debug` 나 `/debug` 로 켠 디버그 로그 | 대상 | [3] |
| `feedback/drafts/` | 피드백 초안(최대 10개, 넘치면 가장 오래된 것부터 지움) | 대상 | [3] |
| `jobs/<이름>/state.json`, `timeline.jsonl` | 백그라운드 작업 상태와 경과 | 아님 | [3] |
| `commands/*.md`, `plans/*.md`, `tasks/` | 사용자 명령, 계획 문서, 작업 목록 | `plans/`·`tasks/` 대상 | [3][8] |

**프로젝트 폴더 이름.** 작업 폴더 경로에서 ASCII 영문자·숫자·`-` 는 그대로 두고 나머지 글자는 모두 `-` 로 바꿔 만듭니다. 공백·`.`·`_`·`@`·경로 구분자도 모두 `-` 가 됩니다(2.1.233 기준)[7]. 예를 들어 `C:\dev\toy-shop` 은 `C--dev-toy-shop` 이 됩니다(만든 예시). 여러 글자가 모두 `-` 가 되므로 폴더 이름만으로는 원래 경로를 되돌릴 수 없습니다[6]. 작업 경로는 늘 기록 줄의 `cwd` 로 적습니다.

**Windows 에서 생기는 파일은 출처마다 다릅니다.** claude-forensics(v0.1.1)는 2026년 중반 Windows 판 Claude Code 가 `history.jsonl`, `shell-snapshots/`, `paste-cache/`, `file-history/` 를 쓰지 않는 것으로 보았지만[6], 2026년 9월 Windows 11 에서는 네 가지가 모두 생기고, 셸 환경 사본은 `snapshot-bash-` 로 시작해 13자리 숫자가 붙은 이름입니다. 판과 설치 환경(Git Bash 유무 등)에 따라 달라질 수 있어서, Windows 검체에서 이 폴더가 없어도 쓰지 않았다고 단정하지 않고 [Windows](windows.md) 페이지의 설치 방법별 차이와 함께 봅니다.

## 구조

### 세션 기록 한 줄

파일은 JSON Lines 형식이라 한 줄에 JSON 객체가 하나씩 들어갑니다. 키를 쓰임에 따라 묶으면 다음과 같습니다.

| 묶음 | 키 |
|---|---|
| 줄마다 붙는 것 | `type`, `uuid`, `parentUuid`, `sessionId`, `timestamp`, `cwd`, `gitBranch`, `version`, `entrypoint`, `userType`, `isSidechain` |
| 메시지 | `message.role`, `message.content`(문자열 또는 목록), `message.model`, `message.id`, `message.stop_reason`, `requestId` |
| 메시지 내용 목록 안 | `type`, `text`, `thinking`, `signature`, `name`, `input`, `id`, `tool_use_id`, `content`, `is_error`, `caller` |
| 사용량 | `message.usage.input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `cache_creation.ephemeral_5m_input_tokens`, `cache_creation.ephemeral_1h_input_tokens`, `service_tier`, `inference_geo`, `speed`, `server_tool_use.web_search_requests`, `server_tool_use.web_fetch_requests`, `output_tokens_details.thinking_tokens`, `iterations[]` |
| 도구 결과 | `toolUseResult.stdout`, `stderr`, `interrupted`, `isImage`, `success`, `commandName`, `allowedTools`, `noOutputExpected`, `sourceToolAssistantUUID`, `sourceToolUseID` |
| 훅 실행 요약 | `hookCount`, `hookInfos[].command`, `hookInfos[].durationMs`, `hookErrors`, `hookAdditionalContext`, `preventedContinuation`, `stopReason`, `level` |
| 덧붙임 | `attachment.type`, `hookEvent`, `hookName`, `command`, `exitCode`, `stdout`, `stderr`, `durationMs`, `toolUseID`, `text` 등 |
| 되돌리기 스냅숏 | `snapshot.messageId`, `snapshot.timestamp`, `snapshot.trackedFileBackups`, `isSnapshotUpdate` |
| 그 밖 | `permissionMode`, `promptId`, `promptSource`, `sessionKind`, `effort`, `mode`, `aiTitle`, `lastPrompt`, `leafUuid`, `bridgeSessionId`, `ownerAccountUuid`, `ownerOrganizationUuid`, `attributionSkill`, `attributionPlugin`, `origin.kind`, `isMeta`, `subtype` |

`cache_creation` 아래 두 값은 더하면 `cache_creation_input_tokens` 와 같고(2.1.231 기준)[7], `iterations[]` 는 윗단 합계와 겹쳐서 더하면 두 번 세게 됩니다[6]. `sessionKind` 는 백그라운드·헤드리스 세션에만 `"bg"` 같은 값으로 붙고 대화형 세션에는 없습니다[7].

**줄 종류(`type`).** 기록마다 들어가는 값은 아래와 같습니다.

| 값 | 뜻 | 근거 |
|---|---|---|
| `user` | 사람이 친 프롬프트, 도구 결과, 편집기가 넣은 문맥 | [6][8] |
| `assistant` | 모델의 답과 도구 호출 | [6][8] |
| `system` | 시스템 줄 | [7] |
| `attachment` | 훅 실행 결과, 대기열에 쌓인 명령(`attachment.type` 이 `queued_command`) 등 | [7][8] |
| `ai-title`, `custom-title` | 자동으로 붙인 세션 제목, `/rename` 으로 바꾼 제목 | [7][8] |
| `permission-mode`, `mode` | 권한 모드가 바뀐 때와 그 값 | [7][8] |
| `queue-operation` | 대기열 조작 | [7] |
| `file-history-snapshot`, `file-history-delta` | 편집 전 사본의 목록과 추가분 | |

이 밖에 `last-prompt`, `bridge-session`, `agent-name`, `pr-link`, `frame-link`, `cost-state` 같은 값도 나옵니다. 뜻이 공개되지 않은 값은 이름만 적고 해석하지 않습니다.

`type` 이 `user` 라고 해서 모두 사람이 친 프롬프트는 아닙니다. 도구 결과도 `user` 줄의 `message.content` 안에 `tool_result` 블록으로 들어가서, 이 블록이 있는 줄과 `isSidechain` 이 참인 줄은 프롬프트에서 뺍니다[6]. VS Code 확장은 열린 파일과 선택 영역을 `ide_opened_file`, `ide_selection` 태그로 싼 `user` 줄로 넣고, 사람이 친 프롬프트 앞에 이 태그를 붙이기도 합니다[7]. 프롬프트가 어디서 왔는지는 `promptSource` 로 가립니다. 값으로는 `"typed"`, `"queued"`, `"system"`, `"sdk"`[7] 와 `"suggestion_accepted"` 가 나옵니다.

`entrypoint` 값으로는 `cli`, `sdk-cli`, `claude-desktop` 이, `permissionMode` 값으로는 `default`, `acceptEdits`, `plan`, `auto` 가 나옵니다. 권한 모드 각각의 뜻은 [설정·권한·훅](settings-permissions.md)에 있습니다.

`parentUuid` 는 앞선 줄의 `uuid` 를 가리켜 대화를 잇습니다. Windows 11 기록에서는 `parentUuid` 가 비어 있지 않은 줄의 98%(82,759줄 가운데 81,113줄)가 바로 앞의 `uuid` 있는 줄을 가리키고, 나머지는 더 앞 줄을 가리키거나 파일 안에 없는 값입니다. 그래서 대화 순서는 파일의 줄 순서가 아니라 `parentUuid` 를 따라 잇습니다.

아래는 키 이름과 `type`·도구 이름 값만 실제 형식을 따르고 나머지 값은 모두 새로 만든 예시입니다.

```json
{"type":"user","uuid":"11111111-2222-4333-8444-000000000001","parentUuid":null,"sessionId":"0f0f0f0f-aaaa-4bbb-8ccc-000000000123","timestamp":"2026-09-03T05:40:12.000Z","cwd":"C:\\dev\\toy-shop","gitBranch":"fix-cart-total","version":"2.x.x","isSidechain":false,"message":{"role":"user","content":"장바구니 합계 계산 버그를 찾아 줘"}}
{"type":"assistant","uuid":"11111111-2222-4333-8444-000000000002","parentUuid":"11111111-2222-4333-8444-000000000001","sessionId":"0f0f0f0f-aaaa-4bbb-8ccc-000000000123","timestamp":"2026-09-03T05:40:15.000Z","message":{"role":"assistant","model":"(모델 이름)","content":[{"type":"tool_use","id":"toolu_example01","name":"Read","input":{"file_path":"C:\\dev\\toy-shop\\src\\cart.js"}}]}}
```

명령 실행 도구의 이름은 `Bash` 이고 입력의 `command` 에 명령이 들어갑니다[6]. Windows 에서는 `PowerShell` 이라는 도구 이름도 같은 `command` 키로 나옵니다. 두 도구가 한 세션에 섞이는 까닭은 [Windows](windows.md) 페이지에 있습니다.

### 하위 에이전트 기록

하위 에이전트는 부모 세션 폴더의 `subagents/` 아래 `agent-<ID>.jsonl` 에 따로 기록하고, 워크플로 도구가 띄운 것은 `workflows/<워크플로 ID>/` 아래로 한 단계 더 들어가며, 옆에 `agent-<ID>.meta.json` 이 붙습니다[7]. 이 파일의 모든 줄은 `isSidechain` 이 참이고 `sessionId` 는 부모 세션의 값이라서[7], 세션 ID 로 모으면 부모와 하위 에이전트 기록이 함께 걸립니다. `.meta.json` 에는 `agentType`, `spawnDepth` 키가 있고, 워크플로 폴더에는 `journal.jsonl` 이 더 생깁니다. 줄에는 부모 기록과 같은 키 말고도 `agentId`, `attributionAgent`, `toolEndsTurn` 이 있습니다. 하위 에이전트가 쓴 토큰은 부모 기록에 들어가지 않아서, 세션 하나의 사용량을 셀 때 하위 에이전트 파일을 더해야 합니다[7].

### 입력 이력 history.jsonl

사용자가 입력한 프롬프트를 시각, 프로젝트 경로와 함께 한 줄씩 남깁니다. 키는 `display`, `project`, `sessionId`, `timestamp`, `pastedContents` 이고[6][8], `pastedContents` 아래 번호별 항목에는 `id`, `type` 과 함께 `content`(내용을 그대로 넣은 것) 또는 `contentHash` 가 들어갑니다. `sessionId` 가 없는 줄도 있습니다.

`contentHash` 가 붙은 붙여넣기는 내용이 `paste-cache/<해시>.txt` 로 빠집니다. 파일 이름에서 확장자를 뗀 부분이 `pastedContents` 안의 `contentHash` 값과 같아서, 둘을 맞춰 이을 수 있습니다[6]. `display` 가 `!` 로 시작하는 줄은 사용자가 셸 명령 모드로 직접 친 명령입니다[8].

```json
{"display":"장바구니 합계 계산 버그를 찾아 줘","pastedContents":{},"timestamp":1788414012000,"project":"C:\\dev\\toy-shop","sessionId":"0f0f0f0f-aaaa-4bbb-8ccc-000000000123"}
```

위 줄도 만든 예시입니다.

### 편집 전 파일 사본 file-history

사용자가 프롬프트를 보내 턴을 시작할 때마다 체크포인트를 만들고, Claude 가 파일 편집 도구로 바꾸기 전의 파일 사본을 `file-history/<세션>/` 에 둡니다[5]. 세션마다 최근 체크포인트 100개를 남기고, 오래된 체크포인트를 버려도 파일별 첫 사본은 남깁니다[5]. Bash 명령(`rm`, `mv`, `cp` 등)으로 바꾼 파일, 사용자가 직접 바꾼 파일, 다른 세션의 편집은 추적하지 않고, 하위 에이전트의 편집도 대부분 잡히지 않습니다[5].

사본 파일 이름은 `<해시>@v<번호>` 이고, 같은 파일의 판은 해시가 같고 번호만 다릅니다[6]. 사본이 원래 어느 파일이었는지는 출처마다 다르게 적습니다. claude-forensics(v0.1.1)는 해시와 원래 경로의 대응이 `.claude` 어디에도 없다고 보고 기록에서 뽑은 `files-touched.txt` 와 맞춰 보라고 하지만[6], 2.1.104~2.1.282 기록에서는 `type` 이 `file-history-snapshot` 인 줄의 `snapshot.trackedFileBackups` 가 파일 경로를 키로 삼고, 그 아래 `backupFileName`(사본 파일 이름), `version`, `backupTime`, `realParentDir` 을 둡니다. `backupFileName` 이 비어 있는(null) 항목도 있고, `file-history-delta` 줄에는 `backup`, `trackingPath`, `snapshotMessageId`, `messageId`, `timestamp` 키가 있습니다. 검체에서는 이 줄의 `backupFileName` 이 `file-history/<세션>/` 의 파일 이름과 맞는지 먼저 봅니다.

### 프로세스 상태 sessions

`sessions/<PID>.json` 은 Claude Code 프로세스 하나의 상태입니다. 키는 `pid`, `sessionId`, `cwd`, `startedAt`, `procStart`, `status`, `updatedAt`, `version`, `entrypoint`, `kind`, `name` 이고[6][8], `statusUpdatedAt`, `nameSince`, `nameSource`, `bridgeSessionId`, `pidDomain`, `peerProtocol`, `peerFeatures`, `messagingSocketPath` 도 들어갑니다. 이 파일의 마지막 수정 시각은 그 프로세스를 마지막으로 본 때로 볼 수 있습니다[6].

### 셸 환경 사본 shell-snapshots

Bash 도구가 명령을 돌린 셸의 alias, export, 함수, `PATH` 를 담은 스크립트입니다. 파일 이름의 숫자가 실행 시각(밀리초)이라서 claude-forensics 는 이 값을 시각으로 풀고, 안의 줄을 정규식으로 읽어 alias 가 `git`·`curl` 을 덮어썼는지, `PATH` 가 바뀌었는지, 토큰이 export 됐는지 봅니다[6]. 줄 이음이나 중첩된 heredoc 은 이 방식으로 제대로 읽히지 않습니다[6].

### 사용량 합계 stats-cache.json

`/usage` 가 보여 주는 토큰·비용 합계입니다. 키는 날짜별 활동(`dailyActivity[].date`, `messageCount`, `sessionCount`, `toolCallCount`), 날짜별 모델 토큰(`dailyModelTokens[].tokensByModel`), `firstSessionDate`, `lastComputedDate`, 시간대별 횟수(`hourCounts`), 가장 긴 세션(`longestSession.sessionId`, `duration`, `messageCount`, `timestamp`), 모델별 사용량(`modelUsage` 아래 `inputTokens`, `outputTokens`, `cacheCreationInputTokens`, `cacheReadInputTokens`, `costUSD`, `webSearchRequests` 등), `totalSessions`, `totalMessages` 입니다.

### 그 밖의 기록

피드백 초안에는 `draft_id`, `created_at`, `cli_version`, `os`, `model`, `cwd`, `source_session_id`, `transcript_ref.session_file`, `transcript_ref.project_dir_key`, `request_ids`, `status`, `title` 같은 키가 있어서, 초안이 어느 세션 기록을 가리키는지 알 수 있습니다. 백그라운드 작업의 `state.json` 에는 `sessionId`, `resumeSessionId`, `cwd`, `cliVersion`, `createdAt`, `updatedAt`, `state`, `intent`, `tokens` 가, `timeline.jsonl` 에는 `at`, `state`, `text`, `detail` 이 있습니다. 서드파티 모델 공급자를 쓸 때 만드는 피드백 묶음은 `~/.claude/feedback-bundles/` 에 알려진 키·토큰 패턴을 가린 기록 압축본으로 남습니다[3].

## 자동 삭제와 남는 것

`cleanupPeriodDays` 는 기본 30일이고 최소 1이며, 0 을 넣으면 설정 검증에서 걸립니다[3]. 기한이 지나면 세션 기록과 그 변형, `subagents/`, `tool-results/`, 세션별 `file-history/`, `debug/`, `plans/`, `shell-snapshots/`, `session-env/`, `paste-cache/`, `image-cache/`, `uploads/`, `tasks/`, `backups/`, `feedback/drafts/`, `usage-data/` 를 지웁니다[3]. `history.jsonl`, `stats-cache.json`, `jobs/`, `daemon/`, `agent-memory/`, 프로젝트별 자동 메모리는 지우지 않아서[3], 원본 기록이 사라진 뒤에도 언제 어떤 프로젝트에서 무엇을 입력했는지, 하루에 얼마나 썼는지는 따로 가늠할 수 있습니다. 세션 기록은 대략 30일 만에 지워지지만 `history.jsonl` 은 몇 달씩 남고, claude-forensics 는 `history.jsonl` 의 `sessionId` 가운데 기록 파일이 없는 프롬프트를 따로 뽑습니다[6]. `.last-cleanup` 의 시각과 이런 프롬프트의 날짜 범위를 함께 보면 청소 주기를 가늠할 수 있습니다[6].

데스크톱 앱이나 Cowork 에서 시작했거나 마지막으로 이어 간 세션 기록은 v2.1.248 부터 기본으로 기한 없이 남고 `desktopSessionCleanupPeriodDays` 로 기한을 둘 수 있으며, 그 전 판은 `cleanupPeriodDays` 에 따라 지웁니다[3]. 관리 정책이 `cleanupPeriodDays` 를 주면 이 기록도 그 기한 뒤 지웁니다. 설정 파일을 읽을 수 없거나 `--bare` 로 돌 때는 청소를 멈추고, 관리 정책이 `cleanupPeriodDays` 를 주면 그 값으로 돕니다[3].

사용자가 지우는 방법도 있습니다. `claude project purge` 는 그 프로젝트의 기록, 자동 메모리, 세션별 tasks·debug·file-history, `history.jsonl` 의 해당 줄, `~/.claude.json` 의 프로젝트 항목을 한꺼번에 지웁니다[3]. `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켜면 기록과 이력을 처음부터 쓰지 않아서[3], 기록이 비어 있는 까닭이 삭제가 아니라 설정일 수도 있습니다. 보관 설정과 삭제의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 세션 기록은 이 PC 의 이 사용자 폴더에서 돈 세션이 어떤 작업 폴더(`cwd`)와 브랜치(`gitBranch`)에서 어떤 프롬프트를 받았고, 모델이 어떤 도구를 어떤 입력으로 불렀으며, 도구가 무엇을 돌려줬는지 보여 줍니다. `history.jsonl` 은 기록 파일이 지워진 뒤에도 그 시각에 그 프로젝트에서 입력한 프롬프트를 보여 주고, `sessions/` 는 그 세션을 돌린 프로세스 번호와 상태를 보여 줍니다. 보고서에는 "이 세션 기록에 이 시각, 이 작업 폴더에서 이 명령을 실행한 도구 호출과 그 출력이 있다" 처럼 기록이 말하는 만큼만 씁니다.

`.env` 를 읽었거나 비밀값을 출력한 세션이면 그 내용이 기록에 그대로 남고, 셸 환경 사본에는 export 한 토큰이 남을 수 있습니다[6]. 이런 값은 어느 파일 어느 줄에 남았는지만 적고 보고서에서는 가립니다.

**증명하지 못하는 것.** 도구 호출 줄이 있어도 그 결과로 파일이 지금 디스크에 어떤 상태인지는 알려 주지 않고, 사용자가 직접 바꾼 파일이나 Bash 로 바꾼 파일은 편집 전 사본도 없습니다. 기록은 그 계정으로 누가 입력했는지 알려 주지 않습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 모델이 보낸 답을 사용자가 실제로 읽었는지도 알 수 없습니다. `user` 줄이라도 도구 결과나 편집기가 넣은 문맥일 수 있어서, 사람이 친 프롬프트라고 쓰려면 `promptSource` 와 내용 블록 종류를 함께 봅니다.

## 시각 해석

| 어디 | 형식 | 근거 |
|---|---|---|
| 세션 기록 `timestamp`, `snapshot.timestamp` | 밀리초까지 적고 끝에 `Z` 가 붙은 ISO 8601 문자열(UTC) | [6][8] |
| `trackedFileBackups` 의 `backupTime`, `.last-cleanup` | 같은 ISO 8601 `Z` 문자열 | |
| `history.jsonl` 의 `timestamp` | 13자리 정수, 유닉스 밀리초 | [6][8] |
| `sessions/<PID>.json` 의 `startedAt`, `updatedAt`, `statusUpdatedAt` | 13자리 정수, 유닉스 밀리초 | [8] |
| `shell-snapshots` 파일 이름의 숫자 | 유닉스 밀리초 | [6] |

표의 형식은 Windows 11(2026-09-25) 기준입니다. 정수는 밀리초로 풀고 문자열은 UTC 로 읽으면 됩니다[6][8]. 다른 판의 검체에서는 정수의 자릿수와 문자열의 끝 글자를 먼저 보고, 같은 프롬프트의 `history.jsonl` 시각과 세션 기록 시각을 맞춰 보면 형식을 한 번 더 가려낼 수 있습니다. 여러 도구의 시각을 한 기준으로 맞추는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

기록 파일의 생성 시각과 마지막 쓰기 시각은 대략 세션의 첫 활동과 마지막 활동을 가리킬 수 있지만, 세션을 이어 가거나 파일을 복사하면 달라질 수 있어서 기록 안의 시각을 우선합니다. 백그라운드로 넘긴 세션은 새 기록 파일에 이전 줄의 `timestamp` 를 그대로 다시 적으므로(아래 함정 참고), 파일이 생긴 시각보다 앞선 시각이 들어 있을 수 있습니다.

## 함정과 한계

기록 형식은 공개 규격이 없어서 키가 판마다 바뀔 수 있고, 그래서 분석 결과에는 기록 줄의 `version` 값을 함께 적습니다. `/compact` 나 Summarize 로 대화를 요약해도 원래 메시지는 기록 파일에 그대로 남아서, 파일이 화면에 보이던 대화보다 깁니다.

한 세션의 기록이 파일 하나에만 있지도 않습니다. `.orphaned-` 나 `.superseded-` 가 붙은 파일도 같은 세션의 기록이라 세션 ID 에 `.jsonl` 을 붙인 이름으로만 찾으면 빠뜨리기 쉽고, 큰 도구 출력은 `tool-results/` 로, 큰 붙여넣기는 `paste-cache/` 로 빠져서 기록 줄만 보면 내용이 잘려 보일 수 있습니다.

**같은 줄이 두 번 나오는 경우**가 두 가지 있습니다. 첫째, 세션을 백그라운드로 넘기면(Ctrl+B, `/background` 등) `claude --resume <기록> --fork-session` 이 돌면서 새 기록 파일에 이전 대화 줄을 `uuid`, `parentUuid`, `timestamp`, `requestId`, `message.id`, 사용량까지 똑같이 다시 적습니다(2.1.226 기준)[7]. 바뀌는 것은 `sessionId` 이고, 백그라운드 실행이 띄운 경우에는 줄마다 `sessionKind:"bg"` 가 더 붙습니다[7]. 새 파일에는 원본을 가리키는 칸이 없어서, 줄 수를 세거나 타임라인을 만들 때 `uuid` 로 겹치는 줄을 걸러야 합니다. 둘째, 응답을 스트리밍하는 동안 같은 `message.id`·`requestId` 로 `assistant` 줄이 여러 개 남고 뒤로 갈수록 `output_tokens` 가 커집니다(2.1.220 기준)[7]. 토큰은 같은 짝 가운데 가장 큰 값 하나만 셉니다.

CLI 의 WebSearch 도구는 검색 호출 자체를 기록에 적지 않고, 도구 결과 줄의 `toolUseResult`(`query`, `results`, `durationSeconds`, `searchCount`)만 남깁니다[7]. 그래서 이 도구로 검색하면 `server_tool_use.web_search_requests` 는 0 으로 남습니다.

저장소 안 `.claude/worktrees/<이름>` 워크트리에서 돈 세션은 워크트리를 지운 뒤에도 그 경로가 `cwd` 에 남습니다[7]. 폴더가 없다고 기록을 의심하지 않고, 원래 저장소 경로로 되짚습니다.

JSON 으로 읽히지 않는 줄은 기록 도중 프로세스가 멈췄거나 누가 손으로 고친 흔적일 수 있어서, 건너뛰지 말고 줄 번호와 함께 따로 적어 둡니다[6].

기록이 없는 까닭도 30일 청소, `claude project purge`, `CLAUDE_CODE_SKIP_PROMPT_HISTORY`, 클라우드 세션처럼 여러 가지입니다. 삭제인지 설정인지 가르려면 `history.jsonl`, `stats-cache.json`, `.last-cleanup` 이 남아 있는지부터 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 JSON Lines 명세와 위의 만든 예시 줄로 만든 바이트이고, 실제 파일에서 뜬 것이 아닙니다. 줄마다 `7B`(`{`)로 시작하고 JSON Lines 규칙대로 `0A`(줄바꿈)로 끝납니다. 실제 파일의 키 순서와 줄 끝 바이트는 검체에서 확인합니다.

```
만든 예시(명세로 만든 바이트)
00000000  7B 22 74 79 70 65 22 3A 22 75 73 65 72 22 2C 22  {"type":"user","
```

**공개 도구로 한 번.** 사본에서 jq 로 읽습니다. `"assistant"`, `"tool_use"`, `"Bash"`, `"Read"` 같은 값은 실제 형식을 따른 것이고, 파일 이름만 만든 예시입니다.

```sh
# 만든 예시 파일 이름
F=0f0f0f0f-aaaa-4bbb-8ccc-000000000123.jsonl
jq -r '.type' "$F" | sort | uniq -c
jq -r '[.timestamp, .type, (.promptSource // ""), (.permissionMode // "")] | @tsv' "$F"
jq -c 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | {name, input}' "$F"
jq -c 'select(.hookInfos) | .hookInfos[] | {command, durationMs}' "$F"
jq -c 'select(.type=="file-history-snapshot") | .snapshot.trackedFileBackups | to_entries[] | {path: .key, backup: .value.backupFileName}' "$F"
```

claude-forensics 의 수집 스크립트는 프로젝트 폴더의 모든 기록에서 Claude 가 실행한 명령(`bash-commands.txt`)과 읽고 쓴 파일(`files-touched.txt`)을 아래처럼 뽑고, `history.jsonl` 가운데 기록 파일이 없는 프롬프트를 `orphan-prompts.jsonl` 로 따로 모읍니다[6]. 이 필터는 `Bash` 도구만 보므로, Windows 검체에서는 `.name=="PowerShell"` 도 함께 넣습니다.

```sh
find projects -name '*.jsonl' -exec cat {} + \
  | jq -rc 'select(.type=="assistant") | .message.content[]?
            | select(.type=="tool_use" and .name=="Bash") | .input.command'
find projects -name '*.jsonl' -exec cat {} + \
  | jq -rc 'select(.type=="assistant") | .message.content[]?
            | select(.type=="tool_use" and (.name=="Read" or .name=="Write" or .name=="Edit"))
            | .input.file_path' | sort -u
```

공개 도구마다 시험한 판과 날짜가 다르고 지금 판과 다를 수 있습니다. claude-forensics 는 v0.1.1(README 의 Windows 설명은 "2026년 중반 기준")[6], agentsview 는 Claude Code 2.1.233 까지 시험한 기록을 남겼고 형식 문서는 2026-09-11 판[7], ccfx 는 2026-08-18 커밋[8]을 기준으로 적었습니다.

## 교차 검증

기록의 도구 호출 시각은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 파일 시스템 시각, 셸 이력과 함께 올리고, 기록에 남은 권한 모드와 훅 흔적은 [설정·권한·훅](settings-permissions.md)의 설정 파일과 맞춰 봅니다. MCP 도구 호출은 [MCP 서버와 도구 호출 기록](../mcp.md)과, 도구 출력에 외부 문서가 섞였다면 [프롬프트 인젝션 사고 분석](../../../03-techniques/analysis/prompt-injection.md)과 이어 봅니다. 에이전트가 한 일을 순서대로 정리하는 흐름은 [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)에 있고, 지운 기록을 되살리는 방법은 [대화 내용 되살리기](../../../03-techniques/analysis/content-recovery.md)에 있습니다.

## 실습

시험용 가상 머신에 Claude Code 를 깔고 가짜 저장소에서 세션을 돌려 풀어 봅니다.

1. 파일 하나를 편집 도구로 고치고, 다른 파일은 Bash 로 지우게 한 뒤 `file-history/` 에 무엇이 남는지, `file-history-snapshot` 줄의 `backupFileName` 이 그 파일 이름과 맞는지 비교합니다.
2. `/compact` 를 한 번 한 세션에서 요약 전 메시지가 기록 파일에 남아 있는지 확인합니다.
3. 세션을 백그라운드로 넘긴 뒤 새로 생긴 기록 파일과 원래 파일에서 `uuid` 가 겹치는 줄을 세어 봅니다.
4. `cleanupPeriodDays` 를 1로 두고 이틀 뒤 `history.jsonl`, `stats-cache.json`, `.last-cleanup` 에 남은 것으로 지워진 세션의 날짜와 프로젝트를 되짚어 봅니다.
5. 큰 텍스트를 붙여넣은 뒤 `history.jsonl` 의 `contentHash` 와 `paste-cache/` 파일 이름을 맞춰 봅니다.

## 참고 문헌

1. Hooks reference — https://code.claude.com/docs/en/hooks
2. Data usage — https://code.claude.com/docs/en/data-usage
3. .claude 폴더 파일·폴더 참조(claude-directory) — https://code.claude.com/docs/en/claude-directory
4. Configure permissions — https://code.claude.com/docs/en/permissions
5. Checkpointing — https://code.claude.com/docs/en/checkpointing
6. claude-forensics (v0.1.1) — https://github.com/forensicdave/claude-forensics , `README.md`, `docs/claude_forensics.md`, `claude_forensics.py`, `claude_report.py`, `claude-forensics.sh`
7. agentsview — https://github.com/kenn-io/agentsview , `docs/internal/session-format-sources.md`(2026-09-11 판, Claude Code 절), `internal/parser/claude_provider.go`
8. ccfx (2026-08-18 커밋) — https://github.com/fkasasagi/ccfx , `collector/history.go`, `collector/sessions.go`, `collector/transcripts.go`, `collector/misc.go`, `collector/filehistory.go`
