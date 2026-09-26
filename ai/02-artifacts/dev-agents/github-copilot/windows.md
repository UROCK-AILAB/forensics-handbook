---
title: "GitHub Copilot Windows"
parent: "GitHub Copilot"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 610
---

# Windows (Windows)

Windows 에서 GitHub Copilot 대화는 쓰는 도구마다 다른 자리에 남습니다. VS Code 는 작업 폴더마다 세션 파일(`.json`·`.jsonl`)을 쓰고 세션 목록은 저장소 키에 따로 두며, Copilot CLI 는 사용자 폴더의 `.copilot` 아래에, Visual Studio 는 임시 폴더의 추적 파일과 솔루션 폴더의 `.vs` 아래에, JetBrains IDE 는 `%APPDATA%\github-copilot` 아래의 Nitrite 데이터베이스에 대화를 둡니다.

이 페이지의 경로와 필드 이름은 판이 바뀌면 달라질 수 있습니다. 도구별 판 차이는 아래 "위치와 버전별 차이" 에 있습니다.

## 무엇을 기록하나 · 왜 생기나

VS Code 는 Copilot 채팅 세션을 작업 폴더(워크스페이스) 단위로 묶고, Agents 창에서는 여러 작업 폴더의 세션을 한꺼번에 보여 줍니다 [1]. 세션 종류는 로컬 세션, worktree 를 쓰는 Copilot 세션, Claude 세션, Codex 세션, Agent Host 세션, 그리고 Copilot CLI·GitHub Copilot 앱·Claude Code 에서 들어온 외부 세션입니다 [1]. 로컬 채팅 세션은 VS Code 사용자 데이터 폴더 안에 파일로 남고, 클라우드 세션과 외부 세션은 목록에 "외부(`isExternal`)" 로 표시됩니다 [2]. 외부 세션의 원본은 그 세션을 만든 도구의 폴더에서 찾습니다. Copilot CLI 에서 온 세션이면 아래 Copilot CLI 절을, Claude Code 에서 온 세션이면 [Claude Code](../claude-code/index.md)를 봅니다.

세션 파일에는 사용자가 보낸 프롬프트, 모델 응답, 에이전트가 부른 도구와 터미널 명령, 턴마다 쓴 모델과 토큰 수가 들어갑니다 [4]. VS Code 는 세션을 저장할 때마다 세션 파일을 쓰고 이어서 세션 목록(색인)도 고쳐 씁니다 [2].

이 페이지는 Windows 경로와 파일 짜임을 다루고, macOS 경로는 [macOS](macos.md)에서, 출력 창·`idea.log`·원격 측정은 [로그와 원격 측정](logs.md)에서 다룹니다. 에이전트가 무엇을 실행했는지 묻는 조사 흐름은 [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)에 있습니다.

## 위치와 버전별 차이

### VS Code

사용자 설정 폴더는 `%APPDATA%\Code\User` 입니다 [3]. 그 아래 채팅 폴더의 이름은 VS Code 의 경로 변수(workspaceStorageHome, globalStorageHome)로 정해지고 [2], 이 변수가 가리키는 폴더는 `User` 아래의 `workspaceStorage`·`globalStorage` 입니다 [4].

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%APPDATA%\Code\User\settings.json` | 사용자 설정(Copilot·채팅 설정 키 포함) | [3] |
| `%APPDATA%\Code\User\profiles\<프로필 ID>\settings.json` | 프로필별 설정. 그 프로필에서 설정을 바꿨을 때만 생김 | [3] |
| 작업 폴더 루트의 `.vscode\settings.json` | 작업 폴더 설정. 여러 폴더 작업 영역이면 작업 영역 설정 파일 안에 들어감 | [3] |
| `%APPDATA%\Code\User\workspaceStorage\<해시>\chatSessions\<세션 ID>.json` 또는 `.jsonl` | 폴더를 연 창의 채팅 세션 | [2][4] |
| `%APPDATA%\Code\User\workspaceStorage\<해시>\workspace.json` | 이 해시 폴더가 어느 작업 폴더인지 알려 주는 파일 | [4] |
| `%APPDATA%\Code\User\globalStorage\emptyWindowChatSessions\` | 폴더 없이 연 빈 창의 채팅(기본 프로필) | [2][4] |
| `%APPDATA%\Code\User\workspaceStorage\no-workspace\chatSessions\` | 예전 빈 창 채팅 위치. 지금은 읽기만 함 | [2] |
| `%APPDATA%\Code\User\globalStorage\transferredChatSessions\` | 다른 작업 영역으로 넘기는 중인 세션 | [2][4] |

같은 세션 ID 로 `.json` 과 `.jsonl` 이 함께 있으면 `.jsonl` 을 기준으로 읽습니다 [4]. 두 형식은 VS Code 판에 따라 갈립니다. 1.109 전에는 JSON 한 파일로, 1.109 부터는 줄을 덧붙이는 기록으로 저장하고, JSONL 저장은 설정 `chat.useLogSessionStorage` 가 false 가 아니면 쓰므로 기본은 켜짐입니다 [2].

| VS Code 판 | 세션 파일 형식 | 조건 |
|---|---|---|
| 1.109 전 | 세션마다 JSON 스냅숏 한 파일(`.json`) | — |
| 1.109 부터 | 줄을 덧붙이는 조작 기록(`.jsonl`) | `chat.useLogSessionStorage` 가 false 가 아닐 때(기본 켜짐) |

VS Code 1.132 가 쓴 JSONL 파일도 같은 형식입니다 [7]. 작업 영역을 옮기면 VS Code 는 `.json`·`.jsonl` 파일을 새 저장 폴더로 복사하고, 원래 폴더의 파일은 지우지 않고 그대로 둡니다 [2]. 새 폴더에 같은 이름의 파일이 이미 있으면 그 파일은 건너뜁니다 [2]. 그래서 같은 세션 ID 의 파일이 두 해시 폴더에 함께 남을 수 있습니다.

### Copilot CLI · Visual Studio · JetBrains

| 도구 | 경로 | 담긴 것 | 근거 |
|---|---|---|---|
| Copilot CLI | `~/.copilot/session-state/<세션 ID>.jsonl` 또는 `~/.copilot/session-state/<세션 ID>/events.jsonl` | 세션 이벤트 기록. 폴더형이면 같은 폴더에 `workspace.yaml` 이 함께 있음 | [5][7] |
| Copilot CLI | `~/.copilot/session-store.db`(와 `-wal`) | 세션 파일에서 다시 만들 수 있는 SQLite 저장소. 모델 호출마다 토큰 사용 행도 들어감 | [5][7] |
| Visual Studio | `%LOCALAPPDATA%\Temp\VSGitHubCopilotLogs\traces\*_VSGitHubCopilot_traces.jsonl` | OpenTelemetry 추적(span) 기록. 대화 내용이 들어감 | [6][7] |
| Visual Studio 2026 | 솔루션 폴더의 `.vs\<이름>\copilot-chat\<이름>\sessions\<대화 ID>` | 확장자 없는 대화 파일 하나에 대화 하나 | [6] |
| JetBrains IDE | `%APPDATA%\github-copilot\` 아래의 `copilot-agent-sessions-nitrite.db` | 에이전트 세션과 턴을 담은 Nitrite 데이터베이스 | [9] |

Copilot CLI 경로는 `~/.copilot/` 모양으로 알려져 있어서 [7], Windows 기기에서는 사용자 폴더(`%USERPROFILE%`) 아래에서 `.copilot` 폴더를 찾습니다. 같은 세션 ID 로 두 모양이 다 있으면 폴더형(`events.jsonl`)을 기준으로 읽습니다 [5]. `tool.execution_*` 이벤트 해석은 Copilot CLI 1.0.76-0, `session-store.db` 해석은 1.0.83 기준입니다 [7]. 1.0.60 이 만드는 저장소(스키마 4판)에는 토큰 사용 표 `assistant_usage_events` 가 없습니다 [7].

Visual Studio 추적 파일은 형식을 설명한 공개 문서도 공개 소스도 없습니다 [7]. JetBrains 파일은 플러그인이 쓰는 Nitrite 4.2.x 와 판이 맞아야 열 수 있습니다 [9].

## 구조

### VS Code 세션 스냅숏

`.json` 파일, 그리고 `.jsonl` 을 처음부터 다시 적용해 얻은 최종 모양은 같은 짜임의 JSON 객체입니다 [4].

| 필드 | 뜻 |
|---|---|
| `version` | 형식 판 번호 |
| `sessionId` | 세션 ID. 비어 있으면 agentsview 는 파일 이름을 씀 |
| `creationDate` | 세션을 만든 시각(Unix 밀리초) |
| `lastMessageDate` | 마지막 메시지 시각(Unix 밀리초) |
| `customTitle` | 세션 제목 |
| `requests[]` | 턴 목록. 한 항목이 프롬프트 하나와 그 응답 |

`requests[]` 의 한 항목에는 아래 필드가 들어갑니다 [4].

| 필드 | 뜻 |
|---|---|
| `requestId` | 요청 ID |
| `message.text`, `message.parts` | 사용자가 보낸 프롬프트 |
| `response[]` | 응답 조각 목록(아래 표) |
| `agent.id`, `agent.name`, `agent.fullName`, `agent.extensionId` | 요청을 처리한 에이전트 |
| `modelId` | 고른 모델. `copilot/` 이 앞에 붙은 이름 |
| `timestamp` | 요청 시각(Unix 밀리초) |
| `result.timings.firstProgress`, `result.timings.totalElapsed` | 첫 응답까지 걸린 시간, 전체 걸린 시간 |
| `result.metadata.promptTokens`, `outputTokens` | 그 턴의 입력·출력 토큰 수 |
| `result.metadata.resolvedModel` | 실제로 응답한 모델 |
| `result.metadata.toolCallRounds` | 도구 호출 기록. `response[]` 의 도구 호출과 겹치고, agentsview 는 이 필드 대신 `response[]` 를 읽음 [7] |
| `followups` | 후속 질문 제안 |

`response[]` 조각은 `kind` 로 갈립니다. `kind` 가 없는 조각은 마크다운 응답 글이고 `value` 에 본문이 있습니다 [4].

| `kind` | 뜻 | 주요 필드 |
|---|---|---|
| (없음) | 응답 글 | `value` |
| `toolInvocationSerialized` | 도구 호출 한 번 | `toolId`, `toolCallId`, `invocationMessage`, `pastTenseMessage`, `toolSpecificData` |
| `prepareToolInvocation` | 도구 호출 준비. 실제 호출은 뒤에 따로 옴 | — |
| `inlineReference` | 응답에 끼운 파일 참조 | `inlineReference.fsPath`, `path`, `external` |
| `undoStop`, `codeblockUri`, `textEditGroup` | 편집·코드 블록 관련 조각 | — |

터미널 명령은 `toolSpecificData` 의 `command` 나 `commandLine.original` 에 들어가고, `command` 가 비어 있으면 `commandLine.original` 을 읽습니다 [4][7]. 끝난 도구 호출에는 `isConfirmed` 가 객체로 남을 수 있습니다 [7]. `toolId` 값은 `copilot_readFile`, `copilot_createFile`, `copilot_deleteFile`, `copilot_replaceString`, `copilot_applyPatch`, `copilot_runInTerminal`, `run_in_terminal`, `copilot_findTextInFiles`, `copilot_fetchWebPage`, `runSubagent` 처럼 도구마다 다르고, 이 이름들은 agentsview 가 분류표에 올린 것이라 전체 목록은 아닙니다 [4]. 도구 결과는 `resultDetails` 아래 `output` 에 들어갈 수 있는데, agentsview 는 다시 적용할 때 이 `output` 을 비우므로 도구 출력 원문이 필요하면 원본 줄을 직접 봅니다 [4].

해시 폴더의 `workspace.json` 에는 작업 폴더 주소가 `folder` 에, 여러 폴더 작업 영역이면 `workspace` 에 `file://` 주소로 들어갑니다 [4]. 아래는 만든 예시입니다.

```json
{ "folder": "file:///C:/work/demo-app" }
```

### VS Code 조작 기록(JSONL)

`.jsonl` 파일은 스냅숏이 아니라 세션을 바꾼 조작을 한 줄씩 적은 기록입니다. 줄마다 `kind`, `k`(바꿀 자리의 경로. 객체 키는 문자열, 배열 번호는 숫자), `v`(값), `i`(배열 자리) 필드가 있습니다 [4].

| `kind` | 뜻 |
|---|---|
| 0 | 처음 스냅숏. `v` 에 세션 전체가 들어감 |
| 1 | 경로 `k` 에 값 `v` 를 넣음 |
| 2 | 경로 `k` 의 배열에 `v` 의 항목을 붙임. `i` 가 있으면 그 자리부터 덮어씀 |
| 3 | 경로 `k` 의 값을 지움 |

그래서 최종 모양을 보려면 첫 줄부터 차례로 다시 적용해야 합니다. 나중에 바뀐 값의 이전 값은 앞 줄에 그대로 남으므로, 제목을 바꾸거나 응답을 고쳐 쓴 흔적도 줄 순서로 따라갈 수 있습니다. JSON 으로 읽히지 않는 줄은 건너뛰고 다음 줄로 넘어갑니다 [4]. 아래는 만든 예시입니다.

```
{"kind":0,"v":{"sessionId":"00000000-0000-4000-8000-000000000001","creationDate":1767225600000,"customTitle":"","requests":[]}}
{"kind":2,"k":["requests"],"v":[{"requestId":"req-demo-1","timestamp":1767225660000,"message":{"text":"demo question"},"response":[]}]}
{"kind":1,"k":["customTitle"],"v":"demo title"}
{"kind":2,"k":["requests",0,"response"],"v":[{"value":"demo answer"}]}
```

### VS Code 세션 목록(색인)

세션 목록은 폴더 안 파일이 아니라 VS Code 저장소 서비스의 키 `chat.ChatSessionStore.index` 에 들어갑니다 [2]. 폴더를 연 창이면 작업 영역 범위, 빈 창이면 애플리케이션 범위에 쓰고, 다른 작업 영역으로 넘긴 세션 목록은 프로필 범위의 키 `ChatSessionStore.transferIndex` 에 둡니다 [2]. VS Code 호환 편집기(Trae 등)의 저장소 값은 작업 영역별·전역 `state.vscdb` 의 `ItemTable` 키에 들어가므로 [7], 작업 영역 범위 색인은 같은 해시 폴더의 `state.vscdb` 에서 키 이름으로 찾습니다. `state.vscdb` 읽는 법은 [Cursor](../cursor.md)에, SQLite 자체는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html)에 있습니다.

색인은 `version` 과 `entries` 로 이뤄지고, `entries` 는 세션 ID 를 키로 삼아 항목을 담습니다 [2].

| 필드 | 뜻 |
|---|---|
| `sessionId` | 세션 ID. 세션 파일 이름과 맞춰 볼 수 있음 |
| `title` | 세션 제목. 없으면 "New Chat" 이 들어가고, 이 글자는 VS Code 표시 언어에 맞춰 번역된 문자열일 수 있음 |
| `lastMessageDate` | 마지막 메시지 시각. 세션의 같은 값을 옮겨 적음 |
| `timing.created`, `timing.lastRequestStarted`, `timing.lastRequestEnded` | 세션을 만든 시각, 마지막 요청을 시작·끝낸 시각 |
| `stats`, `lastResponseState` | 통계, 마지막 응답 상태 |
| `initialLocation` | 세션을 처음 연 자리 |
| `hasPendingEdits` | 적용하지 않은 편집이 남았는지 |
| `workingDirectory` | 작업 폴더 |
| `isEmpty` | 빈 세션인지 |
| `isExternal` | 클라우드·외부 세션인지 |
| `permissionLevel` | 권한 수준 |
| `inputState` | 외부 세션에서 보내지 않은 입력(텍스트, 모드, 고른 모델 등). 첨부는 비움 |

1.109 전의 색인에는 `timing` 이 없어서, VS Code 는 옛 항목을 읽을 때 `lastMessageDate` 로 `timing` 을 채웁니다 [2]. 아래는 필드 이름만 소스에서 가져오고 값은 새로 지어낸 예시입니다.

```json
{ "version": 1, "entries": { "00000000-0000-4000-8000-000000000001": { "sessionId": "00000000-0000-4000-8000-000000000001", "title": "New Chat", "lastMessageDate": 1767225660000, "isEmpty": false, "isExternal": false } } }
```

로컬 세션은 색인에 400개까지 두고, 넘치면 `lastMessageDate` 가 오래된 것부터 색인에서 뺍니다 [2]. 이때 색인 항목만 지우고 세션 파일은 그대로 둡니다 [2]. 외부 세션은 이 계산에서 빠집니다.

### VS Code 설정 키

Copilot 과 채팅 세션 관련 설정은 위 `settings.json` 들에 남습니다. 관련 키는 `github.copilot.chat.summarizeAgentConversationHistory.enabled`, `chat.viewSessions.enabled`, `chat.viewSessions.orientation`, `chat.agentSessions.showExternal`, `chat.agentSessions.autoMarkAsDoneMergedSessionsAfterDays`, `chat.agentSessions.autoDeleteArchivedMergedSessionsAfterDays`, `sessions.showApplicationBadge`, `chat.agentsControl.enabled` 입니다 [1]. 병합된 세션을 자동으로 정리하려면 자동 정리 설정 두 개를 모두 켜야 하고 기본은 꺼짐이며, 권장 값은 15일입니다 [1]. 아래는 만든 예시입니다.

```json
{
  "chat.useLogSessionStorage": true,
  "chat.agentSessions.autoMarkAsDoneMergedSessionsAfterDays": 15,
  "chat.agentSessions.autoDeleteArchivedMergedSessionsAfterDays": 15
}
```

### Copilot CLI 이벤트 기록

Copilot CLI 세션 파일은 한 줄에 이벤트 하나를 적는 JSONL 이고, 줄마다 `type`, `timestamp`(RFC3339 문자열), `data` 가 있습니다 [5]. 세션 파일에서 `session-store.db` 를 다시 만드는 동작은 GitHub 문서에 있지만, 이벤트와 데이터베이스의 짜임은 공개되지 않았습니다 [7]. 아래 표는 agentsview 가 읽는 필드입니다 [5].

| `type` | 주요 필드(`data` 아래) | 뜻 |
|---|---|---|
| `session.start` | `sessionId`, `context.cwd`, `context.branch` | 세션 시작, 작업 폴더와 git 브랜치 |
| `user.message` | `content`, `source` | 사용자 프롬프트. `source` 가 `skill-` 로 시작하면 스킬이 넣은 글 |
| `assistant.message` | `content`, `reasoningText`, `toolRequests[]`(`name`, `arguments`, `toolCallId`), `model`, `outputTokens` | 모델 응답과 도구 호출 요청 |
| `tool.execution_start` | `toolCallId` | 도구 실행 시작 |
| `tool.execution_complete` | `toolCallId`, `result`, `success` | 도구 실행 끝, 결과, 성공 여부 |
| `assistant.reasoning` | — | 추론 기록이 있었음 |
| `session.model_change` | `newModel` | 모델을 바꿈 |
| `session.shutdown` | `modelMetrics`(모델별 `usage.inputTokens`, `cacheReadTokens`, `cacheWriteTokens`, `outputTokens`, `reasoningTokens`), `totalNanoAiu` | 세션 끝의 모델별 토큰 합계 |

`tool.execution_start` 와 `tool.execution_complete` 는 같은 `toolCallId` 를 달고 각자 `timestamp` 를 따로 적으므로, 두 줄로 도구가 실행된 구간을 잴 수 있습니다 [7]. 폴더형 세션의 `workspace.yaml` 에는 `name:` 줄에 세션 이름이 들어가고, 이 이름은 모델이 지었거나 사용자가 붙인 제목입니다 [5].

`session-store.db` 의 `assistant_usage_events` 표에는 모델 호출마다 한 행이 들어갑니다 [5][7].

| 열 | 뜻 |
|---|---|
| `id` | 행 번호 |
| `session_id` | 세션 ID. 세션 파일 이름과 맞춰 봄 |
| `model` | 모델 이름 |
| `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`, `reasoning_tokens` | 토큰 수 |
| `created_at` | 기록 시각(ISO 문자열) |

SQLite 쓰기 잠금 때문에 한 행 쓰기가 실패하면 그 행은 다시 쓰이지 않습니다 [7]. 그래서 이 표의 마지막 행 시각을 세션 기록이 모두 들어왔다는 증거로 쓰지 않습니다.

### Visual Studio 추적 파일

추적 파일은 OpenTelemetry 형식의 JSONL 이고, 한 줄이 `resourceSpans[]` → `scopeSpans[]` → `spans[]` 로 이어지는 묶음이라 한 줄에 span 이 여러 개 들어갈 수 있습니다 [6][7]. span 한 개에는 `traceId`, `spanId`, `name`, `startTimeUnixNano`, `endTimeUnixNano`, `attributes[]` 가 있고, `attributes` 항목은 `key` 와 `value`(`stringValue`, `intValue`, `boolValue`)로 이뤄집니다 [6]. 주요 속성 키는 아래와 같습니다 [6].

| 속성 키 | 뜻 |
|---|---|
| `gen_ai.conversation.id` | 대화 ID. 이 값으로 span 을 대화별로 묶음 |
| `gen_ai.operation.name` | 작업 종류. `chat` 이면 모델 호출 |
| `gen_ai.request.model`, `gen_ai.response.model` | 요청한 모델, 응답한 모델 |
| `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` | 토큰 수 |
| `gen_ai.input.messages`, `gen_ai.output.messages` | 모델에 보낸 메시지, 모델이 돌려준 메시지 |
| `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result` | 도구 이름, 호출 ID, 인자, 결과 |
| `copilot_chat.mode`, `copilot_chat.turn_count`, `copilot_chat.root_request_id`, `copilot_chat.client_id` | 채팅 모드, 턴 수, 첫 요청 ID, 클라이언트 ID |

span 이름이 `invoke_agent` 로 시작하면 에이전트 실행 한 번입니다 [6]. 파일 하나에 여러 대화의 span 이 섞이고, 파일이 돌려쓰기로 나뉘면 한 대화가 여러 파일에 걸칩니다 [6]. 그래서 한 대화를 모두 보려면 같은 폴더의 다른 추적 파일에서도 그 대화의 span 을 모읍니다 [6]. 이 파일에는 프롬프트, 도구 인자, 명령 출력, 비밀 값까지 들어갈 수 있습니다 [6].

Visual Studio 2026 의 `.vs\...\sessions\` 파일은 이름이 36자 UUID 이고 확장자가 없으며, 파일 하나가 대화 하나입니다 [6]. 이 파일도 추적 파일과 같은 span 형식입니다 [6]. 이 파일은 사용자 폴더가 아니라 솔루션 폴더에 생기므로, 사용자 폴더만 살펴보면 놓치고 저장소에 커밋돼 원격으로 올라갈 수도 있습니다 [8].

### JetBrains Nitrite 데이터베이스

JetBrains IDE 의 Copilot 은 에이전트 세션을 Nitrite(MVStore 기반 Java 내장 데이터베이스) 파일 `copilot-agent-sessions-nitrite.db` 에 둡니다 [7][9]. 이 파일은 `%APPDATA%\github-copilot\` 아래 하위 폴더까지 뒤져 찾고, 대화는 아래 두 컬렉션에 들어 있습니다 [9].

| 컬렉션 | 필드 |
|---|---|
| `com.github.copilot.agent.session.persistence.nitrite.entity.NtAgentSession` | `id`, `name.value`(제목), `user`, `createdAt`, `modifiedAt`, `turns`(턴을 세션 안에 넣어 둔 경우) |
| `com.github.copilot.agent.session.persistence.nitrite.entity.NtAgentTurn` | `sessionId`, `createdAt`, `deletedAt`, `request.stringContent`, `request.contents`, `request.chatMode`, `response.stringContent`, `response.contents`, `response.modelInformation.modelName` |

exporter 는 `deletedAt` 이 있는 턴을 내보내지 않습니다 [9]. 거꾸로 말하면 지운 턴이 이 표시만 달고 데이터베이스 안에 남아 있을 수 있으므로, 원본 파일을 직접 볼 때는 `deletedAt` 이 있는 턴을 따로 봅니다. `user` 필드는 사용자를 가리키는 값이므로 보고서에서는 가려서 씁니다.

### 보관·삭제·내보내기(VS Code)

세션은 보관(archive)과 영구 삭제로 나뉩니다. 보관은 세션을 지우지 않지만, worktree 세션이면 커밋하지 않은 변경을 세션 브랜치에 커밋한 뒤 worktree 폴더를 지웁니다 [1]. 삭제는 되돌릴 수 없고, 커밋하지 않은 채 worktree 에만 있던 파일은 잃을 수 있습니다 [1]. 세션 삭제 함수(`deleteSession`)는 그 세션의 `.json` 과 `.jsonl` 파일을 둘 다 지운 뒤 색인 항목을 지웁니다 [2]. 모든 세션을 지우는 함수는 info 수준 로그 `ChatSessionStore: Clearing N chat sessions` 를 남깁니다 [2].

`transferredChatSessions` 의 파일은 받는 쪽 작업 영역이 읽으면 지워지고, 받는 쪽이 확인할 때 넘긴 지 5분이 지났으면 읽지 않고 지워집니다 [2]. 그래서 이 폴더에 남은 파일은 받는 쪽이 아직 열어 보지 않은 세션입니다.

`Chat: Export Chat...` 명령을 쓰면 세션의 프롬프트와 응답 전부를 JSON 파일로 내보내고, 그 파일은 사용자가 고른 자리에 생깁니다 [1]. 내보낸 파일의 일반적인 해석은 [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md)을 봅니다.

로그인 토큰이 흔히 남는 자리와 보고서에서 가리는 법은 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에, 자격 증명 관리자의 구조는 [자격 증명 관리자와 볼트](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/credentials/credential-manager-windows-vault.html)에 있습니다.

## 증거로서 의미

**증명하는 것.** VS Code 세션 파일이 있으면 그 해시 폴더의 작업 폴더에서 채팅 세션이 열렸고 기록이 저장됐다는 뜻이고, `workspace.json` 으로 작업 폴더를, `requests[]` 의 `message.text` 와 `timestamp` 로 무엇을 언제 물었는지를 읽을 수 있습니다. 에이전트가 부른 도구와 터미널 명령은 `toolInvocationSerialized` 조각에, Copilot CLI 는 `tool.execution_start`·`tool.execution_complete` 줄에, Visual Studio 는 `gen_ai.tool.*` 속성에 남습니다. `.jsonl` 파일은 VS Code 1.109 이후 판이 썼다는 단서가 되고, 앞 줄에 남은 이전 값으로 제목·응답이 어떻게 바뀌었는지도 따라갈 수 있습니다. 턴마다 적힌 모델 이름과 토큰 수로 그 턴에 어느 모델이 응답했는지도 좁힐 수 있습니다.

**증명하지 못하는 것.** 세션 파일은 어느 Windows 계정 폴더에 기록이 남았는지를 알려 줄 뿐 키보드 앞에 누가 있었는지는 알려 주지 않고, 이 판단은 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)에서 다룹니다. 모델이 제안한 편집을 사용자가 받아들였는지, 제안한 코드가 저장소에 들어갔는지는 세션 파일만으로 확인되지 않고 git 기록과 파일 시각으로 따로 봐야 합니다. 도구 호출 기록은 에이전트가 그 도구를 불렀다는 기록이지, 명령이 시스템에 어떤 결과를 남겼는지까지 보여 주지는 않습니다. 클라우드 세션의 대화 원본은 PC 가 아니라 서버 쪽 자료라서 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)으로 확인합니다.

보고서에는 "이 작업 폴더에서 이 시각에 이런 프롬프트를 보낸 기록과, 에이전트가 이 명령을 실행하도록 요청한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

| 기록 | 필드 | 형식 | 바뀌는 때 |
|---|---|---|---|
| VS Code 세션 | `creationDate` | Unix 밀리초(UTC) | 세션을 만들 때 |
| VS Code 세션 | `requests[].timestamp` | Unix 밀리초(UTC) | 요청을 보낼 때 |
| VS Code 세션 | `lastMessageDate` | Unix 밀리초(UTC) | 마지막 메시지 때 |
| VS Code 색인 | `lastMessageDate`, `timing.*` | 세션 값을 옮겨 적음 | 세션을 저장할 때 |
| Copilot CLI | `timestamp` | RFC3339 문자열. 시간대 표시가 값 안에 있음 | 이벤트마다 |
| Copilot CLI 저장소 | `created_at` | ISO 문자열 | 모델 호출마다 |
| Visual Studio | `startTimeUnixNano`, `endTimeUnixNano` | Unix 나노초 문자열(UTC) | span 이 시작·끝날 때 |
| JetBrains | `createdAt`, `modifiedAt` | 숫자. exporter 는 턴 시각을 밀리초로 다룸 | 세션·턴을 만들고 바꿀 때 |

VS Code 세션 파일의 세 필드는 Unix 밀리초이고 [4], 색인의 `lastMessageDate` 는 세션 모델의 같은 값을 옮겨 적은 것이라 [2] 단위가 같습니다. `.jsonl` 은 줄을 덧붙일 때마다 파일 수정 시각이 바뀌어 마지막 대화 무렵과 가깝게 움직이지만, 작업 영역을 옮길 때 VS Code 가 파일을 새 폴더로 복사하므로 [2] 새 폴더에 생긴 사본의 파일 시각은 원래 대화 시각과 어긋날 수 있습니다. 그래서 대화 시각은 파일 시스템 시각이 아니라 파일 안의 `timestamp` 로 정하고, 파일 시각은 맞춰 보는 데만 씁니다. 여러 출처를 시간순으로 합치는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)과 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)에 있습니다.

## 함정과 한계

- 색인은 로컬 세션을 400개까지만 두고, 넘친 세션은 색인에서만 빠지고 파일은 남습니다 [2]. 색인에 없는 세션 파일이 곧 지운 세션이라는 뜻이 아니므로, 색인 항목 개수와 `chatSessions` 폴더의 파일 개수를 따로 세어 비교합니다.
- 제목이 "New Chat"(또는 표시 언어로 번역된 같은 문구)이면 제목이 비어 있던 세션입니다 [2]. 제목으로 대화 내용을 짐작하지 않습니다.
- 한 PC 에 `.json` 과 `.jsonl` 이 섞여 있을 수 있습니다. 1.109 전에 쓴 세션이 남아 있거나 `chat.useLogSessionStorage` 를 꺼 둔 경우이고, 어느 쪽인지는 설정 파일로 구분합니다. 같은 ID 로 둘 다 있으면 `.jsonl` 을 기준으로 봅니다.
- `.jsonl` 의 한 줄만 떼어 읽으면 최종 상태가 아닙니다. 반드시 첫 줄부터 다시 적용하고, 마지막 줄이 덜 쓰여 JSON 으로 읽히지 않으면 그 줄은 따로 적어 둡니다.
- `result.metadata.toolCallRounds` 와 `response[]` 에 같은 도구 호출이 두 번 나오므로 [7], 호출 횟수를 셀 때는 한쪽만 셉니다.
- Copilot CLI 의 `session-store.db` 를 복사할 때는 `-wal` 파일을 함께 떠야 합니다. SQLite WAL 을 쓰는 저장소는 본 파일만 떠서는 최근 기록이 빠질 수 있습니다 [8].
- Visual Studio 추적 파일은 Windows `Temp` 폴더 아래에 있어서 임시 파일 정리로 사라질 수 있으니 먼저 수집합니다. 파일 하나에 여러 대화가 섞이므로, 보고서에 붙일 때는 해당 `gen_ai.conversation.id` 의 span 만 골라 냅니다 [6].
- Visual Studio 2026 의 `.vs` 폴더는 솔루션 폴더에 있어서 사용자 폴더만 떠 오면 빠지고 [8], JetBrains 의 `%APPDATA%\github-copilot` 도 `Code\User` 와 따로 떠야 합니다.
- JetBrains Nitrite 파일은 IDE 가 쓰는 중에는 잠겨 있을 수 있으니, 사본을 떠서 읽기 전용으로 엽니다 [9].

## 직접 분석해 보기

세션 파일은 평문 JSON·JSONL 이라서 헥스 편집기로 열면 형식부터 가를 수 있습니다. `.json` 스냅숏은 `{`(바이트 `7B`)로 시작해 파일 끝까지 객체 하나이고, `.jsonl` 은 `{"kind":` 로 시작하는 줄이 줄바꿈(바이트 `0A`)으로 이어집니다. 아래는 위 조작 기록 예시의 세 번째 줄을 바이트로 적은 것으로, 명세로 만든 예시이고 실제 세션 파일의 바이트가 아닙니다.

```
7B 22 6B 69 6E 64 22 3A 31 2C 22 6B 22 3A 5B 22    {"kind":1,"k":["
63 75 73 74 6F 6D 54 69 74 6C 65 22 5D 2C 22 76    customTitle"],"v
22 3A 22 64 65 6D 6F 20 74 69 74 6C 65 22 7D 0A    ":"demo title"}.
```

공개 도구로는 agentsview 가 VS Code·Copilot CLI·Visual Studio 기록을 모두 읽습니다 [4][5][6]. 도구 없이 확인하려면 PowerShell 로 파일을 찾고, 짧은 스크립트로 조작 기록을 다시 적용합니다. 아래 명령과 스크립트는 만든 예시이고, 원본이 아니라 떠 온 사본에서 돌립니다.

```powershell
# 만든 예시: 사용자 폴더 사본을 E:\case01\Users\analyst01 에 떠 왔다고 가정
$u = 'E:\case01\Users\analyst01'
Get-ChildItem "$u\AppData\Roaming\Code\User" -Recurse -Include *.json,*.jsonl |
  Where-Object { $_.DirectoryName -match 'ChatSessions$' } |
  Select-Object FullName, Length, LastWriteTimeUtc
Get-ChildItem "$u\.copilot\session-state" -Recurse -Include *.jsonl, workspace.yaml
Get-ChildItem "$u\AppData\Local\Temp\VSGitHubCopilotLogs\traces" -Filter *_VSGitHubCopilot_traces.jsonl
Get-ChildItem "$u\AppData\Roaming\github-copilot" -Recurse -Filter copilot-agent-sessions-nitrite.db
```

```python
# 만든 예시: VS Code 조작 기록(.jsonl)을 첫 줄부터 다시 적용해 최종 JSON 을 출력
import json, sys
state = None
for line in open(sys.argv[1], encoding="utf-8"):
    try:
        op = json.loads(line)
    except ValueError:
        continue                      # 덜 쓰인 줄은 건너뜀
    if op.get("kind") == 0:
        state = op["v"]
        continue
    keys = op.get("k") or []
    if state is None or not keys:
        continue
    parent = state
    for key in keys[:-1]:
        parent = parent[key]
    last = keys[-1]
    if op["kind"] == 1:
        parent[last] = op["v"]
    elif op["kind"] == 2:
        arr, i = parent[last], op.get("i")
        if i is None:
            arr.extend(op["v"])
        else:
            arr[i:i + len(op["v"])] = op["v"]
    elif op["kind"] == 3:
        del parent[last]
print(json.dumps(state, ensure_ascii=False, indent=1))
```

위 조작 기록 예시를 이 스크립트에 넣으면 `customTitle` 이 `demo title` 이고 `requests[0].response` 에 `demo answer` 가 든 최종 JSON 이 나옵니다. 그다음 `requests[]` 를 돌며 `timestamp`, `message.text`, `toolInvocationSerialized` 조각의 `toolId` 와 `commandLine.original` 을 뽑아 표로 만들면 됩니다.

## 교차 검증

- 작업 폴더 설정 `.vscode\settings.json`, 해시 폴더의 `workspace.json`, 색인의 `workingDirectory` 를 맞춰 봅니다.
- 에이전트가 만들거나 고친 파일은 `toolInvocationSerialized` 조각의 파일 경로와 그 파일의 파일 시스템 시각, git 기록을 맞춰 봅니다.
- VS Code 출력 창과 trace 로그의 세션 관련 문장은 [로그와 원격 측정](logs.md)에서 봅니다.
- Copilot 에 MCP 서버를 붙여 썼다면 [MCP 서버와 도구 호출 기록](../mcp.md)을 함께 봅니다.
- 네트워크 쪽 흔적은 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)으로 확인합니다.
- 외부 세션이 Claude Code 에서 왔다면 [Claude Code](../claude-code/index.md)의 기록과 맞춰 봅니다.

## 실습

직접 만든 시험 환경(가짜 사용자 `analyst01`, 가짜 작업 폴더 `C:\work\demo-app`)에서 풀어 봅니다.

1. 작업 폴더를 열고 채팅을 두 번, 빈 창에서 한 번 했을 때 `chatSessions` 와 `emptyWindowChatSessions` 에 파일이 몇 개 생기는가? 해시 폴더의 `workspace.json` 은 어느 폴더를 가리키는가?
2. 세션 제목을 바꾼 뒤 `.jsonl` 에 어떤 `kind` 의 줄이 붙는가? 이전 제목은 어느 줄에 남는가?
3. 에이전트 모드에서 터미널 명령을 한 번 실행하게 한 뒤, 명령 줄이 `response[]` 의 어느 필드에 남는가?
4. 세션 하나를 보관하고 다른 하나를 삭제한 뒤 폴더의 파일 개수와 `state.vscdb` 의 색인 항목은 어떻게 달라지는가?
5. `chat.useLogSessionStorage` 를 false 로 바꾸고 새 세션을 열면 파일 확장자가 바뀌는가?

## 참고 문헌

1. Manage agent sessions in VS Code(2026-09-16 갱신) — https://code.visualstudio.com/docs/copilot/chat/chat-sessions
2. microsoft/vscode 소스 `chatSessionStore.ts`(main, 마지막 커밋 2026-08-06) — https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/common/model/chatSessionStore.ts
3. User and workspace settings — Visual Studio Code(2026-09-16 갱신) — https://code.visualstudio.com/docs/configure/settings
4. kenn-io/agentsview `internal/parser/vscode_copilot.go`, `internal/parser/vscode_copilot_provider.go`(main, 2026-09-25 열람) — https://github.com/kenn-io/agentsview/tree/main/internal/parser
5. kenn-io/agentsview `internal/parser/copilot.go`, `internal/parser/copilot_provider.go`, `internal/parser/discovery.go`(main, 2026-09-25 열람) — https://github.com/kenn-io/agentsview/tree/main/internal/parser
6. kenn-io/agentsview `internal/parser/visualstudio_copilot.go`(마지막 커밋 2026-09-19), `internal/parser/visualstudio_copilot_provider.go`(main, 2026-09-25 열람) — https://github.com/kenn-io/agentsview/tree/main/internal/parser
7. kenn-io/agentsview `README.md`, `docs/internal/session-format-sources.md`(last_edited 2026-09-11) — https://github.com/kenn-io/agentsview/blob/main/docs/internal/session-format-sources.md
8. Shorton88/coding-agent-forensics `README.md` — https://github.com/Shorton88/coding-agent-forensics
9. MCBoarder289/copilot-jetbrains-exporter `README.md`, `app/src/main/java/io/github/copilotjetbrains/NitriteReader.java`, `PlatformDefaults.java`(마지막 push 2026-03-09) — https://github.com/MCBoarder289/copilot-jetbrains-exporter
