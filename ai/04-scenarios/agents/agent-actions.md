---
title: "AI 에이전트가 무엇을 실행했나"
parent: "시나리오 · AI 에이전트"
nav_order: 970
---

# AI 에이전트가 무엇을 실행했나 (Agent Actions)

AI 개발 도구는 판이 자주 바뀌므로 분석 대상 기기의 도구 버전을 먼저 보고 이 페이지와 맞춰 봅니다.

## 조사 질문

AI 에이전트(AI agent)가 사용자 컴퓨터에서 어떤 명령을 실행하고 어떤 파일을 읽거나 고쳤는지, 그 일을 사람이 시켰거나 승인했는지를 밝히는 조사입니다. 사고 대응에서는 "에이전트가 이 폴더를 지웠나", "이 명령은 사람이 쳤나 에이전트가 만들었나", "그때 자동 승인이 켜져 있었나" 같은 물음으로 나옵니다.

이 페이지는 사용자 컴퓨터에서 도는 개발 도구 에이전트(Claude Code·Codex CLI·Gemini CLI·Cursor·GitHub Copilot)와 Claude 데스크톱 앱의 에이전트 기능을 다룹니다. 웹 브라우저 안이나 서비스 회사 서버에서 도는 에이전트는 [ChatGPT 에이전트 모드](../../02-artifacts/agentic-services/chatgpt-agent.md)와 [브라우저를 조작하는 AI](../../02-artifacts/agentic-services/browser-agents.md)에서 다룹니다. 도구마다 파일 구조를 자세히 설명하지 않고, 조사 순서와 판단 기준만 적습니다. 구조는 표의 "자세히" 링크를 따라갑니다.

## 먼저 확인할 것

- **OS 와 사용자 계정**: 여기서 다루는 CLI 도구는 모두 사용자 홈 폴더 아래에 기록을 둡니다. macOS·Linux 에서는 `~/.claude`, `~/.codex`, `~/.gemini`, `~/.cursor`, `~/.copilot` 이고, Windows 에서는 같은 이름의 폴더가 `%USERPROFILE%` 아래에 생깁니다. Codex 는 `CODEX_HOME` 환경 변수로 폴더를 옮길 수 있어서, 기본 위치에 없으면 환경 변수 설정부터 찾습니다. Claude 데스크톱 앱은 이와 별도로 macOS 의 `~/Library/Application Support/Claude/`, Windows 의 `%APPDATA%\Claude\` 에 데이터를 두고[6], 스토어판은 `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude` 에 둡니다[7]. Windows 기기에서는 `.claude` 와 데스크톱 앱 폴더를 둘 다 뜹니다[6].
- **도구 버전**: Claude Code 세션 기록은 줄마다 `version` 키를 적고, Cursor 훅이 받는 입력에는 `cursor_version` 이 들어갑니다[5]. 같은 도구라도 판에 따라 저장 위치가 바뀝니다. 예를 들어 Claude Code 는 v2.1.274 까지 첨부 이미지를 `~/.claude/image-cache/<session>/` 에 두었고, 그 뒤 판은 `~/.claude` 밖의 임시 폴더 아래 세션별 `images/` 에 둡니다[1].
- **Windows 에서 생기는 파일**: 출처끼리 다릅니다. claude-forensics(v0.1.1, 2026-06)는 2026년 중반 Windows 의 Claude Code 가 `history.jsonl`, `shell-snapshots/`, `paste-cache/`, `file-history/` 를 쓰지 않는 것으로 보인다고 했지만[6], 2026-09 Windows 11 관찰에서는 `history.jsonl` 이 있었습니다. 판에 따라 다를 수 있으므로 실제 기기에서 네 가지가 있는지 먼저 확인합니다.
- **시각 형식과 시간대**: 도구마다 다르고, 같은 도구 안에서도 파일마다 다릅니다.

  | 도구 | 값 | 형식 |
  |---|---|---|
  | Claude Code | `history.jsonl` 의 `timestamp` | 정수[10]. 13자리 유닉스 밀리초 |
  | Claude Code | 세션 기록의 `timestamp` | 끝에 `Z` 가 붙은 ISO 8601 문자열, UTC |
  | Codex CLI | `history.jsonl` 의 `ts` | 유닉스 초[7] |
  | Codex CLI | 세션 폴더 `YYYY/MM/DD` 와 파일 이름의 시각 | 그 PC 의 현지 시각(`OffsetDateTime::now_local()`)[8] |
  | Gemini CLI | 메시지 `timestamp`, 파일 이름의 시각 | UTC ISO 8601(`toISOString()`), 파일 이름은 분까지[9] |
  | Cursor 편집기 | `composerData` 의 `createdAt`·`lastUpdatedAt` / 한 턴(bubble)의 `createdAt` | 유닉스 밀리초 / ISO 8601 문자열[7] |

  Codex 는 파일 이름과 폴더가 현지 시각이라서, 분석 PC 의 시간대로 풀면 날짜가 하루 어긋날 수 있습니다. Codex CLI 기록에는 기록한 곳의 시간대가 남습니다[11]. 여러 도구를 한 기준으로 맞추는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.
- **수집 범위**: 세션 기록 옆에 하위 에이전트 기록과 큰 도구 출력이 따로 있어서 도구 폴더를 통째로 모읍니다. SQLite 저장소(Cursor 의 `state.vscdb`·`store.db`, Copilot CLI 의 `session-store.db`)는 `-wal` 파일을 함께 떠야 하고[7][11], Visual Studio 의 Copilot 은 사용자 폴더가 아니라 솔루션 폴더의 `.vs\` 에 기록합니다[11]. 수집 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다. 세션 기록에는 명령 출력과 파일 내용이 그대로 들어가서 비밀 값이 섞여 있을 수 있고, 다루는 방법은 [에이전트가 자격 증명을 건드렸나](agent-credentials.md)에 있습니다.
- **보관 기간 설정**: 기록이 없을 때 이유를 판별하려면 당시 보관 설정을 알아야 합니다. Claude Code 는 `cleanupPeriodDays`(기본 30일), Claude 데스크톱 앱은 `desktopSessionCleanupPeriodDays` 로 정하고[1], 마지막으로 정리한 시각은 `~/.claude/.last-cleanup` 에 남습니다[6]. Gemini CLI 는 `settings.json` 의 `sessionRetention`(기본 30일)[4], Codex 는 `[history]` 절의 `persistence`·`max_bytes` 로 정합니다[2]. 설정 전체는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 볼 아티팩트와 순서

사고가 난 도구부터 봅니다. Claude Code 는 기록 종류가 많아서 따로 적었습니다.

| 순서 | Claude Code 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | 프롬프트 기록 `~/.claude/history.jsonl` | 사용자가 입력한 프롬프트마다 시각과 프로젝트 경로. 나이 기준으로 지우지 않아 사용자가 지울 때까지 남음[1]. `display` 가 `!` 로 시작하면 사용자가 직접 친 셸 명령[10] | [세션 기록](../../02-artifacts/dev-agents/claude-code/transcripts.md) |
| 2 | 세션 기록 `~/.claude/projects/<project>/<session>.jsonl` | 모든 메시지와 도구 호출, 도구 결과, 작업 폴더·브랜치·권한 모드 | [세션 기록](../../02-artifacts/dev-agents/claude-code/transcripts.md) |
| 3 | 하위 에이전트 기록 `.../<session>/subagents/agent-<id>.jsonl`(옆에 `agent-<id>.meta.json`), 큰 출력 `.../<session>/tool-results/` | 하위 에이전트가 따로 실행한 도구, 세션 기록에 다 담지 않은 출력[7] | [세션 기록](../../02-artifacts/dev-agents/claude-code/transcripts.md) |
| 4 | 수정 전 사본 `~/.claude/file-history/<session>/<hash>@v<N>` | Claude Code 가 고친 파일의 판마다 남긴 사본(최근 체크포인트 100개분)[1][6] | [세션 기록](../../02-artifacts/dev-agents/claude-code/transcripts.md) |
| 5 | 프로세스 기록 `~/.claude/sessions/<pid>.json` | 실행 중이던 프로세스의 `pid`·`sessionId`·`cwd`·`startedAt`·`status`·`updatedAt`·`version`·`entrypoint`[6] | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 6 | 셸 환경 `~/.claude/shell-snapshots/snapshot-zsh-<ms>-<rand>.sh`(또는 `snapshot-bash-…`) | Bash 도구가 쓴 alias·export·함수·`PATH`. 파일 이름에 실행 시각(밀리초)[6] | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 7 | 설정 `settings.json` 의 `permissions`·`hooks` | 당시 허용 규칙과 도구 실행 앞뒤에 걸린 훅 | [설정과 권한](../../02-artifacts/dev-agents/claude-code/settings-permissions.md) |
| 8 | 데스크톱 앱의 `claude_desktop_config.json` 과 MCP 로그 | 신뢰 폴더와 권한 확인 생략 동의, MCP 서버 쪽 기록 | [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md), [Claude](../../02-artifacts/chat-services/claude/index.md) |
| 9 | 데스크톱 앱 세션 `claude-code-sessions/<org>/<account>/local_<id>.json`, 에이전트 세션 `local-agent-mode-sessions/<org>/<account>/local_<id>/audit.jsonl` | 세션 메타(`cliSessionId`·`cwd`·`permissionMode`·`remoteMcpServersConfig`)와 에이전트 세션의 전체 기록[6] | [Windows 의 Claude Code](../../02-artifacts/dev-agents/claude-code/windows.md) |
| 10 | 사용 통계 `~/.claude/stats-cache.json` | 날짜별 도구 호출 수·메시지 수·세션 수. 명령 내용은 없음 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |

다른 도구는 아래 위치에서 도구 호출을 읽습니다.

| 도구 | 실행 기록 위치 | 도구 호출을 읽는 곳 | 자세히 |
|---|---|---|---|
| Codex CLI | `$CODEX_HOME/sessions/YYYY/MM/DD/rollout-YYYY-MM-DDThh-mm-ss-<uuid>.jsonl`, 보관한 세션은 `archived_sessions/`[8]. 프롬프트는 `history.jsonl`(`session_id`, `ts`, `text`)[7] | `response_item` 가운데 `function_call`·`custom_tool_call` 의 `name`·`call_id`·인자와, 같은 `call_id` 의 `function_call_output`. `apply_patch` 는 파일 경로 필드가 없고 본문의 `*** Add File:`·`*** Update File:`·`*** Delete File:`·`*** Move to:` 줄이 파일을 가리킴[7] | [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md) |
| Gemini CLI | `~/.gemini/tmp/<project>/chats/session-<YYYY-MM-DDTHH-MM>-<sessionId 앞 8자>.jsonl`, 하위 에이전트는 `chats/<parentSessionId>/<sessionId>.jsonl`[9] | `type` 이 `gemini` 인 메시지의 `toolCalls[]`. 되감기는 `$rewindTo` 줄로 남음[9] | [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md) |
| Cursor 편집기 | `…/Cursor/User/globalStorage/state.vscdb` 의 `cursorDiskKV` 표[7] | `bubbleId:<composerId>:<bubbleUuid>` 값의 `toolFormerData`(`name`, `rawArgs`, `result`)[7] | [Cursor](../../02-artifacts/dev-agents/cursor.md) |
| Cursor CLI | `~/.cursor/projects/<project>/agent-transcripts/`[7] | 대화 파일. 하위 에이전트는 `<parent>/subagents/<id>` 아래[7] | [Cursor](../../02-artifacts/dev-agents/cursor.md) |
| VS Code 의 Copilot | `…/Code/User/workspaceStorage/<hash>/chatSessions/*.json`·`*.jsonl`[7] | `response[]` 의 `toolId`·`toolCallId`, 터미널 명령은 `toolSpecificData.commandLine.original`[7] | [GitHub Copilot](../../02-artifacts/dev-agents/github-copilot/index.md) |
| Copilot CLI | `~/.copilot/session-state/<uuid>.jsonl` 또는 `<uuid>/events.jsonl`[7] | `tool.execution_start`·`tool.execution_complete` 이벤트의 `data.toolCallId`[7] | [GitHub Copilot](../../02-artifacts/dev-agents/github-copilot/index.md) |

Cursor 편집기 DB 의 키는 공개 문서가 없고, 표의 키는 macOS 판 DB(`composerData` 의 `_v` 가 16) 기준입니다[7]. 다른 판에서는 실제 데이터로 확인합니다.

## 분석 흐름

1. **도구와 기간을 좁힙니다.** 사용자 폴더마다 도구 폴더가 있는지 보고, 있으면 도구 버전과 보관 설정을 적어 둡니다. 도구 폴더가 있어도 실행 기록은 없을 수 있습니다. `.codex` 에 `hooks.json` 과 스킬 파일만 있거나, `.gemini` 에 설정 파일만 있고 세션 폴더(`tmp/`)가 없거나, `.cursor` 에 `hooks.json` 하나만 있는 경우가 그렇습니다. 그래서 폴더가 있다는 사실과 실행 기록이 남아 있다는 사실은 따로 확인합니다.
2. **조사 기간의 세션을 고릅니다.** Claude Code 는 `history.jsonl` 의 `timestamp`·`project`·`sessionId` 로 기간 안의 세션을 찾고[10], 같은 이름의 세션 파일을 `projects/` 아래에서 엽니다. 프로젝트 폴더 이름은 작업 폴더 경로에서 영문자·숫자·`-` 말고 모든 글자를 `-` 로 바꾼 것이라 원래 경로로 정확히 되돌릴 수 없고[6][7], 실제 작업 폴더는 줄 안의 `cwd` 로 확인합니다[6]. `sessions/<pid>.json` 에 같은 `sessionId` 가 있으면 그 세션을 띄운 프로세스와 시작 시각도 알 수 있습니다[6].
3. **도구 호출과 결과를 짝짓습니다.** 세션 기록에서 `type` 이 `assistant` 인 줄의 `message.content[]` 가운데 `type` 이 `tool_use` 인 블록이 도구 호출이고, `name`·`input`·`id` 가 들어갑니다. 결과는 `type` 이 `user` 인 줄 안의 `tool_result` 블록이며, 같은 값을 `tool_use_id` 로 가리키고 `content`·`is_error` 를 적습니다[6][10]. 셸 명령이면 `toolUseResult` 의 `stdout`·`stderr`·`interrupted`·`success` 도 봅니다. 호출만 있고 짝이 되는 결과가 없으면 "실행 요청이 기록됐다" 까지만 씁니다. Bash 명령과 읽거나 고친 파일 목록은 아래처럼 뽑을 수 있습니다[6].

   ```sh
   # Bash 도구에 넘긴 명령
   jq -rc 'select(.type=="assistant") | .message.content[]?
           | select(.type=="tool_use" and .name=="Bash") | .input.command' *.jsonl
   # Read·Write·Edit 도구가 다룬 파일
   jq -rc 'select(.type=="assistant") | .message.content[]?
           | select(.type=="tool_use" and (.name=="Read" or .name=="Write" or .name=="Edit"))
           | .input.file_path' *.jsonl | sort -u
   ```

   다른 도구는 위 표의 필드로 같은 일을 합니다. Codex 는 `call_id` 로, Copilot CLI 는 `toolCallId` 로 호출과 결과를 잇고, Cursor 편집기는 한 턴 안의 `toolFormerData` 에 입력과 결과를 함께 둡니다[7].
4. **누가 시켰는지 따라갑니다.** `parentUuid` 를 거슬러 올라가 그 호출 직전의 사용자 메시지를 찾고, `history.jsonl` 에 같은 프롬프트가 있는지 대조합니다. `type` 이 `user` 인 줄이 모두 사람의 입력은 아닙니다. 도구 결과(`tool_result`)도 이 줄에 들어가고[6], VS Code 확장은 `ide_opened_file`·`ide_selection` 태그로 싼 편집기 정보를 user 줄로 씁니다[7]. 사용자 턴마다 `promptSource`(`"typed"`, `"queued"`, `"system"`, `"sdk"`)가, 백그라운드 세션에는 `sessionKind:"bg"` 가 붙고, 이 키들은 공개 문서가 없습니다[7]. Codex 는 `session_meta.payload.originator` 가 `codex_exec` 이면 사람이 대화하지 않는 `codex exec` 실행입니다[7].
5. **승인이 있었는지 봅니다.** Claude Code 는 줄마다 적힌 `permissionMode` 와 설정의 `permissions.allow` 목록으로 판단하고, 데스크톱 앱이면 `claude_desktop_config.json` 의 `preferences.localAgentModeTrustedFolders`, 계정별 `bypassPermissionsGateByAccount`·`bypassPermissionsOptInByAccount` 값도 봅니다. 데스크톱 앱 세션 메타에도 `permissionMode` 가 남습니다[6]. Codex 는 `config.toml` 의 `sandbox_mode`(예: `"workspace-write"`, `"danger-full-access"`)와 `approval_policy`(예: `"on-request"`, `"never"`)가 같은 역할을 합니다[2]. 설정 파일은 조사 시점의 값이라서, 사고 당시 값과 같은지는 파일 수정 시각과 백업으로 따로 확인합니다.
6. **하위 에이전트와 백그라운드 작업을 더합니다.** 하위 에이전트 기록은 `projects/<project>/<부모 세션 ID>/subagents/agent-<id>.jsonl` 에 따로 있고, 워크플로 도구가 띄운 것은 `workflows/<워크플로 ID>/` 아래로 한 단계 더 들어갑니다. 모든 줄에 `isSidechain: true` 와 부모 세션의 `sessionId` 가 붙습니다[7]. `agentId`·`attributionAgent` 키도 있고, 백그라운드 작업은 `jobs/<이름>/state.json`(`cwd`, `intent`, `state`, `createdAt`, `updatedAt`, `sessionId`)과 `timeline.jsonl`(`at`, `state`, `detail`, `text`)에 상태가 남습니다. Codex 하위 에이전트는 `session_meta` 의 `source.subagent` 와 `parent_thread_id` 로 부모를 가리킵니다[7]. 메인 세션 기록만 보면 이쪽 실행을 빠뜨립니다.
7. **이어받은 기록의 중복을 걸러냅니다.** Claude Code 는 세션을 백그라운드로 돌리면 `claude --resume <transcript> --fork-session` 을 띄우고, 새 기록 파일에 이전 대화 줄을 `uuid`·`timestamp`·`requestId`·usage 까지 똑같이 다시 적습니다. `sessionId` 는 새 값으로 바뀌고, 백그라운드 실행기가 띄운 경우에는 줄마다 `sessionKind:"bg"` 가 붙습니다. 원본 세션을 가리키는 필드는 없습니다(Claude Code 2.1.226 기준)[7]. Codex 의 fork 와 하위 에이전트 rollout 도 부모 대화 줄을 다시 적은 채로 시작할 수 있고, fork 는 `forked_from_id` 로 원본을 가리킵니다[7]. 두 파일의 도구 호출을 그대로 더하면 같은 명령을 두 번 세게 됩니다. 같은 `uuid` 나 `call_id` 는 한 번만 셉니다.
8. **훅 기록을 확인합니다.** 훅(hook)은 도구 실행 앞뒤에 사용자가 건 명령이고, 설정 파일에는 어떤 이벤트에 걸었는지만 남습니다. 실제로 돌았는지는 Claude Code 세션 기록의 `attachment.hookEvent`·`hookName`·`command`·`exitCode`·`stdout`·`stderr`·`durationMs`, 그리고 `hookErrors`·`preventedContinuation` 으로 봅니다. Cursor 훅은 종료 코드 2 일 때 막고 0 이면 성공이며 그 밖의 코드는 기본으로 통과시켜서, 훅이 오류로 끝났다면 동작이 막히지 않았을 수 있습니다[5]. Codex 는 관리자 설정 `requirements.toml` 에 `allow_managed_hooks_only = true` 가 있으면 사용자·프로젝트·세션 훅을 무시하고 관리자 훅만 돌립니다[3]. Cursor 훅이 받는 `command`·`cwd`·`file_path`·`tool_name`·`tool_input`·`tool_output` 은 훅 스크립트가 따로 파일로 적어 두었을 때만 남으므로, 훅 스크립트의 출력 경로를 찾아봅니다[5].
9. **파일 변화와 맞춰 봅니다.** `file-history/<session>/` 의 사본은 파일마다 `<hash>@v<N>` 이름으로 판이 쌓입니다. 해시와 원래 경로의 대응은 `.claude` 에 따로 저장되지 않는다는 해석이 있어서[6], 3단계의 Read·Write·Edit 파일 목록으로 거슬러 올라가 찾습니다. 세션 기록에는 `snapshot.trackedFileBackups` 키도 있는데, 이 값이 원래 경로와 사본 파일을 잇는지는 실제 데이터에서 값을 보고 확인한 뒤 씁니다. Codex 는 `apply_patch` 본문의 파일 표시 줄로 바뀐 파일을 알 수 있습니다[7]. 어느 폴더와 브랜치에서 일했는지는 Claude Code 세션 기록의 `cwd`·`gitBranch`와 Codex `session_meta` 의 `cwd`·`git.branch`[7]로 알 수 있고, 마지막으로 대상 파일의 파일 시스템 시각이나 저장소 커밋 기록과 대조합니다.
10. **셸 환경을 확인합니다.** 명령이 뜻과 다르게 동작했다면 `shell-snapshots/` 의 alias 가 `git`·`curl` 같은 명령을 덮어쓰지 않았는지 봅니다[6]. 이 파일에는 export 한 환경 변수가 들어가서 토큰이 섞일 수 있습니다. 보고서에서는 값을 가리고, 다루는 방법은 [에이전트가 자격 증명을 건드렸나](agent-credentials.md)를 따릅니다.
11. **다른 기록원도 봅니다.** Codex 는 OpenTelemetry 를 켠 환경이면 `codex.tool_decision`(승인·거부)과 `codex.tool_result`(실행 결과) 이벤트가 수집 서버에 남고, 사용자 프롬프트는 `log_user_prompt = true` 일 때만 내용이 들어갑니다[3]. 디스크 기록이 없고 메모리 이미지가 있으면 MCP 요청·응답을 메모리에서 되살릴 수 있습니다. MCPRecon 논문의 시험(Ubuntu 24.04 가상 머신, stdio·HTTP 두 방식)에서는 Codex CLI 와 VS Code Copilot 의 프로세스 메모리에서 `tools/call` 인자와 도구 결과가 되살아났습니다[12]. 방법은 [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md)과 [메모리에서 AI 흔적 찾기](../../03-techniques/analysis/memory-analysis.md)를 봅니다.
12. **기록이 없으면 이유를 확인합니다.** 보관 기간이 지났거나, `claude project purge` 로 지웠거나(`projects/` 기록, 세션별 `tasks/`·`debug/`·`file-history/`, `history.jsonl` 의 해당 줄, `~/.claude.json` 의 프로젝트 항목이 함께 지워짐), `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켜서 처음부터 쓰지 않았을 수 있습니다[1]. Gemini CLI 는 `--delete-session` 으로[4], Codex 는 `persistence = "none"` 이면 프롬프트 기록(`history.jsonl`)을 쓰지 않습니다[2]. `history.jsonl` 의 `sessionId` 가운데 세션 기록 파일이 없는 것을 모으고 `.last-cleanup` 시각과 맞춰 보면 정리로 사라졌는지 가릴 수 있습니다[6]. 세션 기록은 약 30일 주기로 정리되고 `history.jsonl` 은 몇 달 남습니다[6]. 세션 기록이 없어도 그날 도구 호출이 있었는지는 `stats-cache.json` 의 `dailyActivity[].toolCallCount` 로 알 수 있습니다.
13. **타임라인에 합칩니다.** 세션 기록의 시각을 파일 시스템·이벤트 로그·네트워크 기록과 시간순으로 합칩니다. 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)과 [Windows 판 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)을 봅니다.

## 흔한 오판

**도구 호출 기록을 실행 완료로 읽는 경우**가 가장 흔합니다. 호출 항목은 모델이 그 도구를 쓰겠다고 요청했다는 기록이고, 실행 결과는 짝이 되는 결과 항목과 `is_error`·`interrupted` 값으로 따로 확인합니다. 결과가 성공이어도 명령이 대상 파일에 무엇을 했는지는 파일 쪽 기록으로 확인합니다.

**명령을 사람이 입력했다고 보는 경우**도 있습니다. `history.jsonl` 과 사용자 메시지에는 사람이 입력한 프롬프트가 남고, 도구 호출의 `input` 에는 모델이 만든 명령이 남습니다. 둘을 섞으면 사용자가 "정리해 줘" 라고만 말한 일을 사용자가 삭제 명령을 쳤다고 쓰게 됩니다. 반대로 `history.jsonl` 에서 `!` 로 시작하는 줄은 사용자가 직접 친 셸 명령이라서 에이전트 탓으로 돌리면 안 됩니다[10]. 사람이 승인했는지는 권한 모드와 허용 규칙을 봐야 알 수 있어서, 모델이 만든 명령이라는 사실만으로 사용자 책임이 없다고 쓰지도 않습니다.

**user 줄을 모두 사람의 입력으로 세는 경우**도 있습니다. 도구 결과와 편집기가 넣은 정보도 `type` 이 `user` 인 줄로 남아서, 줄 수를 세면 사람의 입력이 부풀려집니다[6][7].

**이어받은 기록을 따로 세는 경우**가 있습니다. 백그라운드로 돌린 Claude Code 세션과 Codex 의 fork 는 앞 대화를 새 파일에 다시 적어서, 파일마다 도구 호출을 더하면 같은 명령이 두 번 나옵니다[7]. Gemini CLI 는 되감은 턴도 파일에 남기므로[11], 사용자가 되돌린 대화를 최종 대화로 읽지 않습니다.

**하위 에이전트 기록을 빠뜨리는 경우**가 있습니다. 하위 에이전트와 백그라운드 작업은 메인 세션 파일 밖에 기록되어서, 메인 파일만 보면 실행 수가 적게 잡힙니다.

**훅 설정을 훅 실행으로 읽는 경우**도 있습니다. 설정 파일은 걸어 둔 훅만 보여 주고, 실제로 돌았는지와 결과는 세션 기록의 훅 항목에 있습니다.

**세션 기록을 조작할 수 없는 기록으로 보는 경우**도 조심합니다. 세션 기록은 서명이 없고 사용자가 고칠 수 있는 파일이라서, 도구가 기록한 내용의 증거이지 사람이 한 일의 증명은 아닙니다[11]. 중간에 JSON 이 깨진 줄은 기록 도중 멈췄거나 누가 손으로 고친 흔적일 수 있습니다[6].

**기록이 없으면 실행도 없었다고 보는 경우**는 위 12단계의 여러 이유 때문에 틀릴 수 있습니다. 특히 `history.jsonl` 은 나이 기준으로 지우지 않아서, 프롬프트 기록은 있는데 세션 기록만 없다면 보관 기간 정리나 삭제를 먼저 의심합니다. 메모리에서 MCP 흔적이 나오지 않은 것도 호출이 없었다는 뜻이 아닙니다[12].

**서버에 원본이 있을 것이라고 가정하는 경우**도 조심합니다. 로컬 세션 기록은 PC 에 있는 파일이 원본이고, 서버 쪽 자료가 필요하면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)과 기업용 감사 로그([Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md))로 따로 확인합니다.

## 보고서 문장 예

아래는 만든 예시이고, 사용자 이름·폴더 이름·시각·건수는 모두 가짜 값입니다.

> 사용자 계정 `demo-user` 의 Claude Code 세션 기록 가운데 2026-08-14 01:02~01:37(UTC) 구간의 파일 1개에 도구 호출 12건과 각 호출에 짝이 되는 결과 항목 12건이 있습니다. 그중 1건의 입력에는 `C:\work\sample-shop\build` 폴더를 지우는 명령이 적혀 있고, 결과 항목에는 오류 표시가 없습니다. 이 호출 직전 사용자 메시지는 빌드 폴더 정리를 요청하는 내용이며, 같은 줄의 권한 모드 값과 설정 파일의 허용 목록은 부록에 적었습니다. 폴더가 실제로 지워진 시각은 세션 기록만으로는 확정할 수 없어 파일 시스템 기록으로 따로 확인했습니다.

> 같은 기간 `demo-user` 의 `stats-cache.json` 에는 2026-08-15 날짜에 도구 호출 수가 기록되어 있지만 그날의 세션 기록 파일은 없습니다. 기록으로는 그날 도구 호출이 있었다는 사실까지만 확인되고, 어떤 명령을 실행했는지는 확인되지 않습니다.

> 세션 기록 파일 2개에 같은 `uuid` 의 도구 호출 줄 8건이 똑같이 들어 있어, 이를 한 번씩만 세어 도구 호출을 모두 20건으로 적었습니다.

보고서 전체 틀은 [AI 관련 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)를 따릅니다.

## 함께 볼 페이지

- [에이전트가 자격 증명을 건드렸나](agent-credentials.md) — 세션 기록과 셸 환경에 섞인 비밀 값, 도구 자체의 인증 정보
- [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md), [Cursor](../../02-artifacts/dev-agents/cursor.md), [GitHub Copilot](../../02-artifacts/dev-agents/github-copilot/index.md) — 도구별 저장 구조
- [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md) — 외부 도구 서버 쪽 기록과 메모리 흔적
- [OpenAI API 플랫폼 기록](../../02-artifacts/network-enterprise/openai-api-platform.md) — Agents SDK 트레이스와 API 호출 로깅으로 보는 서버 쪽 실행 흐름
- [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md) — 에이전트가 사용자 뜻과 다른 일을 한 경우
- [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md) — 기록이 없을 때의 해석
- [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html) — 데스크톱 앱 폴더 구조(Windows 판)

## 참고 문헌

1. Explore the .claude directory (Claude Code 문서) — https://code.claude.com/docs/en/claude-directory
2. docs/config.md (openai/codex GitHub) — https://github.com/openai/codex/blob/main/docs/config.md
3. Advanced configuration (Codex 문서) — https://learn.chatgpt.com/docs/config-file/config-advanced
4. Session management (google-gemini/gemini-cli GitHub 문서) — https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/session-management.md
5. Hooks (Cursor 문서) — https://cursor.com/docs/agent/hooks
6. forensicdave/claude-forensics v0.1.1(2026-06) — https://github.com/forensicdave/claude-forensics , `README.md`, `docs/claude_forensics.md`, `claude-forensics.sh`, `claude_forensics.py`
7. kenn-io/agentsview — https://github.com/kenn-io/agentsview , `docs/internal/session-format-sources.md`(2026-09-11 수정), `internal/parser/codex.go`, `cursor_ide.go`, `cursor_provider.go`, `vscode_copilot.go`, `copilot.go`, `cowork_paths.go`, `discovery.go`
8. openai/codex `codex-rs/rollout/src/recorder.rs` (커밋 406dc92) — https://github.com/openai/codex/blob/406dc9239492aff6d295cca5eebe2a548548d42f/codex-rs/rollout/src/recorder.rs
9. google-gemini/gemini-cli `packages/core/src/services/chatRecordingService.ts` (커밋 acae712) — https://github.com/google-gemini/gemini-cli/blob/acae7124bdd849e554eaa5e090199a0cf08cd782/packages/core/src/services/chatRecordingService.ts
10. fkasasagi/ccfx — https://github.com/fkasasagi/ccfx , `README.en.md`, `collector/history.go`, `collector/transcripts.go`
11. Shorton88/coding-agent-forensics `README.md` — https://github.com/Shorton88/coding-agent-forensics
12. Satter, A., Salmon, M., Muhanna, L., Spinosa, T. T., Gharaibeh, T., Baggili, I., "With or Without Logs: Memory Forensic Reconstruction of Model Context Protocol (MCP) Activity in Agentic LLM Systems", DFRWS USA 2026 — https://dfrws.org/presentation/with-or-without-logs-reconstructing-model-context-protocol-activity-from-volatile-memory/ , 도구 https://github.com/BiTLab-BaggiliTruthLab/MCPRecon
