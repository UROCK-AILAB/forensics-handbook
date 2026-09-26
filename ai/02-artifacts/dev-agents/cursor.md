---
title: "Cursor"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 640
---

# Cursor (Cursor)

Cursor 는 AI 채팅과 에이전트가 들어간 VS Code 계열 편집기입니다. 편집기 대화는 앱 데이터 폴더의 전역 `state.vscdb` 에 있는 `cursorDiskKV` 표에 남고, 예전 채팅 패널 대화는 작업 공간별 `state.vscdb` 에 남으며, 사용자 폴더 `~/.cursor` 에는 에이전트 대화 사본과 세션 저장소, 훅·MCP 설정이 남습니다.

> 기준: 2026-09. 출처마다 기준으로 삼은 Cursor 판과 날짜가 다릅니다(아래 "출처별 기준" 표). 지금 쓰는 판은 구조가 다를 수 있으니 분석 대상의 앱 버전과 `_v` 값을 먼저 적습니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 편집기 안에서 AI 에게 묻거나 에이전트(Composer)에게 작업을 맡기면, Cursor 는 대화 한 건을 전역 `state.vscdb` 의 `cursorDiskKV` 표에 `composerData:` 키로 저장하고, 그 대화의 발화 하나하나를 `bubbleId:` 키로 따로 저장합니다[5][6][7]. VS Code 계열이라 작업 공간(workspace)마다 `state.vscdb` 가 하나씩 더 있고, 이 파일에는 그 작업 공간에 속한 대화 목록과 예전 채팅 패널의 대화가 들어갑니다[4][7]. 예전 채팅 패널을 내보내는 도구 cursor-chat-export 는 2024-08-30 에 마지막으로 고친 뒤 보관 처리되었고, 작업 공간 파일의 채팅 패널 키 하나만 읽습니다[4]. 그래서 이 도구로 뽑은 결과에는 전역 파일의 에이전트 대화가 들어 있지 않습니다.

사용자 폴더의 `~/.cursor` 에는 에이전트 대화를 글로 옮긴 사본(`projects` 아래 `agent-transcripts`), 에이전트 세션 저장소(`chats` 아래 `store.db`), 코드 변경이 AI 몫인지 사람 몫인지 구분하는 기록(`ai-tracking`)이 쌓입니다[5][7][8]. 같은 폴더에는 에이전트 동작 전후에 사용자 스크립트를 돌리는 훅(hook) 설정 `hooks.json` 과 MCP 서버 설정도 들어갑니다[1][2]. 훅은 셸 명령 실행, 파일 읽기와 편집, MCP 도구 호출, 프롬프트 제출 같은 순간에 걸 수 있어서, 조직이 감사 목적으로 훅을 걸어 두었다면 그 스크립트가 남긴 기록이 대화 기록과 별개의 증거가 됩니다.

서버 쪽은 공개 문서로 알 수 있는 것이 적습니다. 개인 정보 보호 모드(Privacy Mode)를 켜면 데이터를 학습에 쓰지 않고, 모델 제공사와는 기술·계약상 통제를 둡니다[3]. 이 모드에서 서버에 무엇을 얼마나 오래 두는지, 코드베이스 색인(임베딩)을 서버에 두는지는 보안 페이지에 나와 있지 않고, 세부는 trust.cursor.com 에 있습니다[3]. 계정은 Settings 대시보드에서 언제든 지울 수 있지만, 지운 뒤의 보관 기간은 적혀 있지 않습니다[3]. 서버에 남은 자료는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 구하고, 서버와 기기 중 어디에 무엇이 있는지 구분하는 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

## 위치와 버전별 차이

### 앱 데이터 폴더

아래 표의 `Cursor/` 는 OS 마다 이 폴더를 가리킵니다[4][5][6].

| OS | `Cursor/` 가 가리키는 폴더 |
|---|---|
| Windows | `%APPDATA%\Cursor\` (`C:\Users\%user%\AppData\Roaming\Cursor\`) |
| macOS | `~/Library/Application Support/Cursor/` |
| Linux | `~/.config/Cursor/` |

| 경로 | 담는 것 | 근거 |
|---|---|---|
| `Cursor/User/globalStorage/state.vscdb` 와 `-wal`, `-shm`, `.backup` | 전역 SQLite, 편집기 대화(`cursorDiskKV`) | [5][6][7] |
| `Cursor/User/globalStorage/storage.json` | 창 상태, 최근 연 작업 공간과 파일 | [7] |
| `Cursor/User/workspaceStorage/<hash>/state.vscdb` | 작업 공간별 SQLite(`ItemTable`), 그 작업 공간의 대화 목록과 예전 채팅 패널 | [4][7] |
| `Cursor/User/workspaceStorage/<hash>/workspace.json` | 해시 이름 폴더를 실제 작업 폴더 경로에 잇는 파일 | [7] |
| `Cursor/User/History/` | 편집한 파일의 로컬 기록 사본, 에이전트가 고친 것 포함 | [7] |
| `Cursor/Backups/` | 저장하지 않은 편집 내용 | [7] |
| `Cursor/User/settings.json` | 사용자 설정 | [7] |
| `Cursor/logs/` | 실행마다 `yyyyMMddTHHmmss` 이름의 폴더, `main.log`·`renderer.log`, 확장 호스트 로그(`anysphere.cursor-agent-exec`, `anysphere.cursor-mcp`), `cursor.hooks.*.log`, `cursor.requestTraces.log` | [7] |
| `Cursor/machineid` | 원격 측정(telemetry)에 함께 보내는 기기 식별자 | [7] |

### 사용자 폴더 `~/.cursor`

Windows 에서는 `%USERPROFILE%\.cursor\` 입니다[7].

| 경로 | 담는 것 | 근거 |
|---|---|---|
| `~/.cursor/projects/<project>/agent-transcripts/` | 에이전트 대화 사본(예전 텍스트 `.txt`, 새 JSONL `.jsonl`) | [5][7] |
| `~/.cursor/projects/<project>/terminals/` | 에이전트가 돌린 명령의 터미널 출력 | [7] |
| `~/.cursor/projects/<project>/mcps/` | 프로젝트별 MCP 서버 상태 | [7] |
| `~/.cursor/chats/<workspace-hash>/<agent-id>/store.db` 와 `-wal` | 에이전트 세션 저장소 | [5][8] |
| `~/.cursor/ai-tracking/ai-code-tracking.db` | 코드 변경을 AI 와 사람 가운데 누가 썼는지 구분하는 SQLite | [5][7][8] |
| `~/.cursor/mcp.json`, 프로젝트의 `.cursor/mcp.json` | MCP 서버 설정 | [2][7] |
| `~/.cursor/hooks.json`, `~/.cursor/hooks/` | 사용자 범위 훅 설정과 그 스크립트 | [1][7] |
| `~/.cursor/agents/` | 사용자가 정의한 에이전트 | [7] |
| `~/.cursor/argv.json`, `~/.cursor/extensions/extensions.json` | 실행 인자, 설치한 확장 프로그램과 버전 | [7] |

### 훅 설정 범위

| 위치 | OS | 범위 | 근거 |
|---|---|---|---|
| `~/.cursor/hooks.json` | 모두 | 사용자 | [1] |
| `<프로젝트 루트>/.cursor/hooks.json` | 모두 | 프로젝트 | [1] |
| `C:\ProgramData\Cursor\hooks.json` | Windows | 기업(시스템 전체) | [1][7] |
| `/Library/Application Support/Cursor/hooks.json` | macOS | 기업 | [1] |
| `/etc/cursor/hooks.json` | Linux·WSL | 기업 | [1] |

팀 범위 훅(Enterprise)은 웹 대시보드에서 설정해 자동으로 동기화하므로[1], 기기 파일만으로는 걸려 있던 훅을 다 보지 못할 수 있습니다.

### 출처별 기준

| 출처 | 기준 판·날짜 | 다루는 범위 |
|---|---|---|
| cursor-chat-export[4] | 마지막 커밋 2024-08-30, 보관 처리 | 작업 공간 DB 의 예전 채팅 패널 키 |
| cursor2md[6] | 2026-08-17 | 전역 DB 의 `composerData` 옛 구조와 새 구조, Windows 기본 경로 |
| agentsview[5] | 설명서 2026-09-11 | 전역 DB(macOS 기기, `composerData` `_v: 16`, bubble `_v: 3`), 대화 사본(macOS, 2026-09-04), `store.db`(Windows, 2026-09-07) |
| KapeFiles Cursor 수집 대상[7] | 2026-09-18 | Windows 수집 경로 전체(Windows Server 2025 에 새로 설치한 Cursor 기준) |
| la-roca 설명서[8] | 2026-09-21 | `chats` 저장소, 전역·작업 공간 DB, `ai-tracking` |
| MCPRecon 논문[9] | Cursor 2.4.27 | 공격 시나리오에서 사용자 화면에 보인 것 |

에이전트 대화가 어디에 "주로" 남는지는 출처끼리 다릅니다. agentsview 설명서(2026-09-11)는 편집기(GUI)가 `agent-transcripts` 를 쓰지 않고 전역 `state.vscdb` 가 편집기 대화의 유일한 저장소이며, `agent-transcripts` 와 `chats/.../store.db` 는 Cursor CLI(Cursor Agent)가 쓴다고 적었습니다[5]. KapeFiles 수집 대상(2026-09-18)은 에이전트 대화가 전역 `state.vscdb` 에 있고, 전체 대화를 `agent-transcripts` 아래 JSONL 로도 쓴다고 적었습니다[7]. la-roca 설명서(2026-09-21)는 지금의 에이전트 대화가 `chats` 아래 세션마다 `store.db` 하나씩 있고 옆에 `meta.json` 이 있으며, 이 저장소로는 데스크톱과 CLI 를 구분할 수 없다고 적었고, 전역 `state.vscdb` 는 예전(legacy) 저장소로 부릅니다[8]. 실제 기기에서는 세 곳을 모두 모으고, 같은 대화 ID 가 여러 곳에 있는지 맞춰 봅니다.

`%USERPROFILE%\.cursor\hooks.json` 하나만 있고 `%APPDATA%\Cursor` 폴더는 없는 PC 도 있습니다. 그래서 `~/.cursor` 의 파일 하나만 보고 Cursor 를 설치했다고 쓰지 않고, 앱 데이터 폴더와 설치 흔적을 함께 봅니다. 앱 데이터 폴더는 Electron 앱 모양이라서 위 표에 없는 폴더는 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)와 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)를 따라 읽습니다.

## 구조

`state.vscdb`, `store.db`, `ai-code-tracking.db` 는 모두 SQLite 라서 형식 자체는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html) 페이지대로 읽습니다.

### 전역 `state.vscdb` 의 `cursorDiskKV`

`cursorDiskKV` 는 키 하나에 JSON 값 하나를 두는 표입니다[5][7].

| 키 | 담는 것 | 근거 |
|---|---|---|
| `composerData:<composerId>` | 대화 한 건 | [5][6][7] |
| `bubbleId:<composerId>:<bubbleId>` | 그 대화의 발화 한 개 | [5][6][7] |
| `checkpointId:*`, `messageRequestContext:*` | 이름만 알려짐, 값 구조는 실제 데이터로 확인 | [7] |

`composerData` 값의 필드는 아래와 같습니다.

| 필드 | 뜻 | 근거 |
|---|---|---|
| `_v` | 문서 형식의 판, macOS 기기에서 16 | [5] |
| `name` | 대화 제목 | [5][6] |
| `createdAt`, `lastUpdatedAt` | 대화 시작과 마지막 갱신, epoch 밀리초 | [5][6] |
| `fullConversationHeadersOnly[]` | 발화 순서, 항목마다 `bubbleId` 와 `type`(1 사용자, 2 어시스턴트) | [5][6] |
| `conversationMap` | 발화를 문서 안에 두는 필드, 보고된 대화에서는 모두 `{}` | [5] |
| `workspaceIdentifier.uri.fsPath` | 작업 폴더 경로 | [5] |
| `trackedGitRepos[].repoPath`, `trackedGitRepos[].branches[].branchName` | git 저장소 경로와 브랜치 | [5] |
| `context.mentions.fileSelections` | 대화에 붙인 파일 | [6] |
| `conversation[]` (옛 구조) | 발화를 문서 안에 직접 둠, 항목마다 `type`, `text`, `context.selections`, `codeBlocks`, `timingInfo.clientEndTime` | [6] |

`fullConversationHeadersOnly` 가 있으면 새 구조이고, 문서 맨 위에 `conversation` 배열이 있으면 옛 구조입니다[6]. 같은 전역 파일 안에 두 구조가 섞여 있을 수 있으니 대화마다 어느 쪽인지 봅니다.

`bubbleId` 값의 필드는 아래와 같습니다.

| 필드 | 뜻 | 근거 |
|---|---|---|
| `_v` | 문서 형식의 판, macOS 기기에서 3 | [5] |
| `type` | 1 사용자, 2 어시스턴트 | [5] |
| `text` | 발화 본문 | [5][6] |
| `createdAt` | 발화 시각, ISO-8601 문자열 | [5] |
| `context` | 발화에 붙인 선택 영역 등 | [6] |
| `toolFormerData` | 어시스턴트 발화 안의 도구 호출: `toolCallId`, `name`, `rawArgs`, `params`, `result` | [5] |

Claude Code 처럼 도구 호출과 결과를 별도 블록으로 두지 않고, 호출한 발화 안에 호출과 결과를 함께 둡니다[5]. `rawArgs` 와 `params` 는 JSON 을 문자열로 넣은 값이고, `result` 는 문자열인 경우와 객체인 경우(`todo_write` 도구 사례)가 둘 다 있습니다[5]. 토큰 필드는 출처끼리 다릅니다. agentsview 설명서(2026-09-11)는 `composerData` 와 bubble 에 토큰·비용 필드가 없었다고 적었고[5], la-roca 설명서(2026-09-21)는 bubble 에 적힌 모델과 토큰 수를 읽는다고 적었습니다[8].

### 작업 공간 `state.vscdb` 의 `ItemTable`

| 키 | 담는 것 | 근거 |
|---|---|---|
| `composer.composerData` | 그 작업 공간에 속한 대화 목록 | [7] |
| `aiService.prompts` | 이름만 알려짐, 값 구조는 실제 데이터로 확인 | [7] |
| `workbench.panel.aichat.view.aichat.chatdata` | 예전 채팅 패널 대화 | [4][7] |

예전 채팅 패널 값은 JSON 이고, `tabs[]` 아래 탭마다 `timestamp` 와 `bubbles[]` 가 있습니다[4]. bubble 의 `type` 은 `user` 와 `ai` 이고, 사용자 글은 `delegate.a`, `text`, `initText`(JSON 문자열) 필드에 들어가고, 선택 영역은 `selections[].text`, 붙인 그림은 `image.path`, AI 쪽은 `modelType` 과 `rawText` 에 있습니다[4]. 작업 공간 DB 의 프롬프트·생성 배열은 전역 DB 의 대화와 겹칩니다[8]. 작업 공간 DB 는 대화를 작업 폴더에 묶는 근거가 되고, 해시 이름 폴더가 어느 작업 폴더인지는 같은 폴더의 `workspace.json` 에 나와 있습니다[7].

### 에이전트 대화 사본 `agent-transcripts`

파일은 세 가지로 놓입니다[5].

- 평평한 배치: `agent-transcripts/<id>.ext`
- 폴더 배치: `agent-transcripts/<id>/<id>.ext`
- 하위 에이전트: `agent-transcripts/<parent>/subagents/<id>.ext`

확장자는 예전 텍스트면 `.txt`, 새 형식이면 `.jsonl` 입니다[5]. 사용자 메시지는 맨 앞에 분 단위 시각 꼬리표가 붙고 이어서 질문이 `<user_query>` 태그 안에 들어갑니다[5]. 꼬리표 모양은 `<timestamp>Weekday, Mon D, YYYY, H:MM AM|PM (UTC±H[:MM])</timestamp>` 입니다[5]. 파일은 `{"type":"turn_ended","status":...}` 레코드로 끝납니다(macOS 기준)[5].

하위 에이전트를 부른 세션에는 `Subagent` 도구 호출이 남고, 입력 필드는 `description`, `prompt`, `subagent_type`, `run_in_background` 입니다[5]. 도구 호출 블록의 `"id"` 는 모두 `null` 이고 `tool_result` 블록은 없어서, 부모 세션과의 연결은 폴더 위치로만 알 수 있습니다[5]. JSONL 에 도구 출력이 빠진다는 사용자 보고도 있습니다[5]. 도구 결과가 필요하면 전역 DB 의 `toolFormerData` 와 `terminals/` 폴더를 함께 봅니다.

### 에이전트 세션 저장소 `store.db`

`store.db` 에는 `blobs`(`id`, `data`)와 `meta`(`key`, `value`) 두 표가 있습니다[5]. `meta` 의 키 `0` 값은 UTF-8 JSON 을 16진수 글자로 적은 문자열이고, 풀면 `agentId` 와 `latestRootBlobId` 가 나옵니다[5]. `blobs` 의 값은 protobuf 이고, 루트 blob 의 8번 필드(turn 목록)에 추론(reasoning) 글과 epoch 밀리초 시각이 있습니다[5]. 공개된 `.proto` 가 없어서 필드 번호는 그 판(Windows, 2026-09-07)에만 맞는 값으로 봐야 합니다[5]. 마지막 루트뿐 아니라 저장소의 모든 목록 노드를 따라가면, 대화 압축(compaction) 뒤에도 남아 있는 앞 기록을 함께 읽을 수 있습니다[8].

이 저장소에는 `blobEncryptionKey` 가 있고, agentsview 는 암호화된 blob 을 읽지 않습니다[5]. 이 값은 보고서에서 가립니다.

### 코드 기여 기록 `ai-code-tracking.db`

코드 변경을 AI 와 사람 가운데 누가 썼는지 구분하는 SQLite 이고[7], 대화가 아니라 코드 기여를 적은 행이 들어 있습니다[8]. 표와 열 이름을 설명한 공개 분석 자료는 없어서, 실제 파일에서 `.schema` 로 확인합니다.

### 훅 설정 `hooks.json`

`hooks.json` 은 JSON 파일이고 최상위에 숫자 `version`(필수, 값 1)이 있습니다[1]. `hooks` 아래 이벤트 이름마다 스크립트 목록을 두고, 스크립트마다 아래 키를 씁니다[1].

| 키 | 뜻 |
|---|---|
| `command` | 돌릴 명령(필수) |
| `type` | `"command"` 또는 `"prompt"`, 기본 command |
| `timeout` | 제한 시간(초) |
| `loop_limit` | 기본 5 |
| `failClosed` | 기본 false |
| `matcher` | 정규식 |

훅을 걸 수 있는 이벤트는 아래와 같습니다[1].

| 분류 | 이벤트 |
|---|---|
| 에이전트 | sessionStart, sessionEnd, preToolUse, postToolUse, postToolUseFailure, subagentStart, subagentStop, beforeShellExecution, afterShellExecution, beforeMCPExecution, afterMCPExecution, beforeReadFile, afterFileEdit, beforeSubmitPrompt, preCompact, stop, afterAgentResponse, afterAgentThought |
| Tab(자동 완성) | beforeTabFileRead, afterTabFileEdit |
| 앱 수명 | workspaceOpen |

모든 훅은 입력으로 `conversation_id`, `generation_id`, `model`, `model_id`, `model_params`, `hook_event_name`, `cursor_version`, `workspace_roots`, `user_email`, `transcript_path` 를 받고, workspaceOpen 같은 앱 수명 훅에는 대화 필드가 없습니다[1]. 감사용 훅 스크립트가 이 입력을 그대로 파일에 적었다면, 그 기록에서 대화 ID·모델·Cursor 버전·계정 이메일·작업 폴더를 함께 얻습니다. `transcript_path` 가 가리키는 파일이 위의 `agent-transcripts` 파일과 같은지는 출처마다 설명이 달라서, 실제 훅 기록에 적힌 경로로 확인합니다.

아래는 문서 형식대로 만든 예시입니다.

```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      { "command": "./hooks/audit.sh", "timeout": 10 }
    ]
  }
}
```

훅 실행 결과는 Customize 의 Hooks 탭과 "Hooks" 출력 채널에서 볼 수 있고[1], `Cursor/logs/` 아래 `cursor.hooks.*.log` 에도 남습니다[7].

## 증거로서 의미

**증명하는 것.** 전역 DB 에 `composerData` 와 그 bubble 이 있으면 그 대화가 Cursor 를 거쳐 오간 기록이 있다는 뜻이고, `fullConversationHeadersOnly` 로 발화 순서를 되살릴 수 있습니다. `workspaceIdentifier.uri.fsPath` 와 `trackedGitRepos` 는 대화가 어느 작업 폴더와 어느 git 브랜치에서 이뤄졌는지 알려 주고, 작업 공간 DB 와 `workspace.json` 이 이를 한 번 더 받쳐 줍니다. `toolFormerData` 는 에이전트가 어떤 도구를 어떤 인자로 불렀고 어떤 결과를 받았다고 앱이 적었는지 보여 줍니다. `ai-code-tracking.db` 는 코드 변경이 AI 몫으로 기록되었는지, `terminals/` 는 에이전트가 돌린 명령이 어떤 출력을 냈는지 보여 줍니다[7]. `hooks.json` 이 있으면 그 범위(사용자·프로젝트·기업)에 누군가 훅을 설정했다는 뜻이고, 감사용 훅이 남긴 기록이 있으면 "이 시각에 에이전트가 이 셸 명령을 실행하려 했다" 처럼 에이전트 동작을 대화 기록과 따로 보여 줍니다.

**증명하지 못하는 것.** 도구 호출 기록은 앱이 적은 내용일 뿐이라서, 파일이 실제로 바뀌었는지나 명령이 실제로 실행되었는지는 git 이력·`User/History/`·파일 시스템 기록으로 따로 확인합니다. 기록이 있다고 사용자가 그 동작을 알아챘다고 볼 수도 없습니다. MCP 서버 응답에 숨긴 지시로 에이전트가 작업 공간 데이터를 빼낸 실험(Cursor 2.4.27)에서, 사용자 화면에 보인 것은 "Listed test Read mcp.json" 한 줄과 조금 달라진 도구 호출뿐이었고, 나머지는 사용자가 접힌 생각(Thinking) 블록과 입출력 블록을 펼쳐야 보였습니다[9]. 대화 기록이 기기에 없다고 대화가 없었다고 말할 수도 없는데, 판 올림 뒤 행이 사라진 보고와 서버 쪽 자료가 따로 있기 때문입니다(함정 참고). `~/.cursor/hooks.json` 하나만으로는 Cursor 를 설치하거나 썼다고 말할 수 없습니다. 편집기를 연 사람이 누구인지도 기록으로는 알 수 없어서 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 좁힙니다.

## 시각 해석

| 값 | 형식 | 가리키는 때 | 근거 |
|---|---|---|---|
| `composerData.createdAt` | epoch 밀리초(UTC 기준) | 대화 시작 | [5][6] |
| `composerData.lastUpdatedAt` | epoch 밀리초(UTC 기준) | 대화 마지막 갱신 | [5][6] |
| bubble `createdAt` | ISO-8601 문자열 | 발화 하나 | [5] |
| 옛 구조 `conversation[].timingInfo.clientEndTime` | 숫자 | cursor2md 가 마지막 항목 값을 대화 끝으로 씀 | [6] |
| 예전 채팅 패널 탭의 `timestamp` | 숫자 | cursor-chat-export 가 가장 큰 값을 가장 최근 탭으로 씀 | [4] |
| 대화 사본의 `<timestamp>` 꼬리표 | 현지 시각 글자와 UTC 차이, 분 단위 | 사용자 메시지 | [5] |
| `store.db` turn 의 시각 | epoch 밀리초 | 발화, 필드 번호는 그 판 기준 | [5] |

`lastUpdatedAt` 이 bubble 의 시각보다 뒤처지는 경우가 있어서, 둘 가운데 늦은 쪽을 대화 끝으로 잡습니다[5]. 한 레코드 안에서도 `composerData` 는 밀리초 숫자이고 bubble 은 ISO-8601 문자열이라, 두 값을 시간순으로 합칠 때는 둘 다 UTC 로 바꾼 뒤 비교합니다. 옛 구조 숫자와 탭 `timestamp` 는 단위를 적은 자료가 없어서 자릿수로 초·밀리초를 구분합니다.

대화 사본의 꼬리표는 분 단위라서 초는 알 수 없고, 어시스턴트가 답을 마친 시각은 파일에 없습니다[5]. agentsview 는 꼬리표가 없는 사본이면 파일 수정 시각을 세션의 시작과 끝으로 씁니다[5]. 파일 시스템 시각은 앱이 그 파일에 마지막으로 쓴 때이고, 전역 `state.vscdb` 는 모든 대화를 한 파일에 담으므로 그 수정 시각이 특정 대화의 시각을 뜻하지 않습니다. 문서에 나온 훅 입력 필드에는 시각이 없어서, 감사 기록의 시각은 훅 스크립트가 직접 넣은 값이고 UTC 인지 현지 시각인지는 그 스크립트를 열어 확인합니다. 여러 출처의 시각을 시간순으로 합치는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

예전 도구로 뽑은 결과를 전부로 보지 않습니다. cursor-chat-export 는 작업 공간 DB 의 채팅 패널 키 하나만 읽으므로[4], 이 도구 결과에 대화가 없어도 전역 DB 의 `cursorDiskKV` 에는 에이전트 대화가 있을 수 있습니다.

판 올림으로 행이 사라질 수 있습니다. Cursor 3.16.29 업데이트 뒤 일부 사용자의 `cursorDiskKV` 행이 줄거나 사라졌다는 보고가 있고, 그래서 agentsview 는 `fullConversationHeadersOnly` 가 가리키는 bubble 행이 없어도 대화 전체를 버리지 않고 빈자리로 둡니다[5]. 다른 보고(2026-09-08)에서는 `cursorDiskKV` 2,189행 가운데 64행의 값이 SQL NULL 이었고(`composerData` 2행, `bubbleId` 62행), 원인은 밝혀지지 않았습니다[5]. 빈 값이나 빠진 행은 "대화가 없었다" 가 아니라 "기록이 비었다" 로 적습니다.

SQLite 는 WAL 과 함께 모읍니다. KapeFiles 수집 대상은 `state.vscdb*` 로 `-wal`, `-shm`, `.backup` 파일까지 모으고[7], `store.db` 는 본 파일이 4,096바이트 머리뿐이고 표와 행이 모두 `store.db-wal` 에 있을 수 있습니다[5]. 원본을 sqlite3 로 바로 열면 WAL 이 본 파일로 합쳐질 수 있으므로 사본에서만 엽니다. 전역 `state.vscdb` 는 86MB(macOS 기기)에서 500MB 넘게까지 커질 수 있어서[5], 수집 시간을 넉넉히 잡습니다.

형식이 판마다 바뀝니다. 새 구조와 옛 구조가 한 파일에 섞일 수 있고[6], `_v` 값과 필드 번호는 "출처별 기준" 표의 판 기준입니다[5]. 실제 데이터에서 위 키가 없으면 "대화가 없다" 가 아니라 "구조가 바뀌었을 수 있다" 로 먼저 보고, 표 전체의 키 목록을 뽑아 앱 버전과 함께 기록합니다.

훅 설정은 여러 범위에 흩어집니다. 사용자·프로젝트·기업 파일을 모두 모으지 않으면 걸려 있던 훅을 빠뜨리고, 팀 범위 훅은 웹 대시보드에서 옵니다[1]. MCP 서버는 확장 프로그램이 설정 파일을 거치지 않고 등록할 수도 있는데, 이 내용은 [MCP 서버와 도구 호출 기록](mcp.md)에 있습니다. `mcp.json` 의 인증 정보와 `store.db` 의 `blobEncryptionKey` 는 어디에 있는지만 적고 보고서에서 값을 가립니다. 이런 값이 남는 곳 전반은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

agentsview 는 `composerData` 행이 없어진 대화를 Cursor 안에서 지운 대화로 처리합니다[5]. 지운 SQLite 레코드를 되살리는 일반 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)에 있고, `.backup` 파일과 WAL 에 앞 상태가 남았는지도 비교합니다. 서버 쪽 보관 기간은 공개 문서에 없어서 다른 서비스의 규칙으로 메우지 않고, 사건 당시의 약관과 trust.cursor.com 자료를 따로 확보합니다. 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 파일이 SQLite 인지는 첫 16바이트로 확인하고, 키 이름과 필드 이름은 문자열 바이트로 찾습니다. JSON 값 안의 시각은 숫자를 글자로 적은 것이라 ASCII 숫자 바이트로 보입니다. `store.db` 의 `meta` 값은 16진수 글자 문자열이라서, 바이트로 보면 `7b22` 가 `37 62 32 32` 로 한 번 더 감싸여 있습니다. 아래는 SQLite 명세와 문자 인코딩대로 만든 예시이고, 실제 데이터에서 뜬 바이트가 아닙니다.

```
만든 예시(명세로 만든 바이트)
파일 머리 "SQLite format 3\0"   53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00
"composerData:"  UTF-8           63 6F 6D 70 6F 73 65 72 44 61 74 61 3A
"bubbleId:"      UTF-8           62 75 62 62 6C 65 49 64 3A
"createdAt":1767225600000        ... 3A 31 37 36 37 32 32 35 36 30 30 30 30 30
  1767225600000 ms = 2026-01-01T00:00:00Z
meta 값 "7b226167656e744964223a"  → 풀면 {"agentId":
```

할당되지 않은 영역이나 지운 페이지에서 `composerData:` 나 `bubbleId:` 문자열이 보이면 그 근처가 대화 레코드였을 수 있으니, 그 바이트 범위를 따로 떼어 SQLite 레코드 형식으로 풀어 봅니다.

**공개 도구로 한 번.** 수집한 사본에서 sqlite3 명령줄 도구와 jq 로 봅니다. 경로와 ID 는 만든 예시이고, WAL 파일을 같은 폴더에 함께 둔 사본에서만 돌립니다.

```sh
# 만든 예시 경로
C=/cases/case-0001/copy
G=$C/Cursor/User/globalStorage/state.vscdb
W=$C/Cursor/User/workspaceStorage/0a1b2c3d4e5f/state.vscdb

# 전역 DB: 키 종류별 행 수와 빈 값 수
sqlite3 "$G" <<'SQL'
SELECT substr(key, 1, instr(key, ':') - 1) AS kind, count(*),
       sum(value IS NULL OR length(value) = 0) AS empty
FROM cursorDiskKV GROUP BY kind;
SQL

# 대화 목록: ID, 형식 판, 제목, 시작·마지막 갱신(UTC), 작업 폴더
sqlite3 "$G" <<'SQL'
SELECT substr(key, 14),
       json_extract(CAST(value AS TEXT), '$._v'),
       json_extract(CAST(value AS TEXT), '$.name'),
       datetime(json_extract(CAST(value AS TEXT), '$.createdAt') / 1000, 'unixepoch'),
       datetime(json_extract(CAST(value AS TEXT), '$.lastUpdatedAt') / 1000, 'unixepoch'),
       json_extract(CAST(value AS TEXT), '$.workspaceIdentifier.uri.fsPath')
FROM cursorDiskKV WHERE key LIKE 'composerData:%' AND length(value) > 0;
SQL

# 대화 하나의 발화 순서와 각 발화(만든 예시 ID)
sqlite3 "$G" <<'SQL'
SELECT h.key AS n,
       json_extract(h.value, '$.type') AS type,
       json_extract(CAST(b.value AS TEXT), '$.createdAt'),
       json_extract(CAST(b.value AS TEXT), '$.toolFormerData.name'),
       substr(json_extract(CAST(b.value AS TEXT), '$.text'), 1, 80)
FROM cursorDiskKV c,
     json_each(CAST(c.value AS TEXT), '$.fullConversationHeadersOnly') h
LEFT JOIN cursorDiskKV b
  ON b.key = 'bubbleId:' || substr(c.key, 14) || ':' || json_extract(h.value, '$.bubbleId')
WHERE c.key = 'composerData:11111111-2222-3333-4444-555555555555'
ORDER BY h.key;
SQL

# 작업 공간 DB: 대화 관련 키가 있는지와 값 길이
sqlite3 "$W" "SELECT key, length(value) FROM ItemTable WHERE key IN ('composer.composerData','aiService.prompts','workbench.panel.aichat.view.aichat.chatdata');"
cat "$(dirname "$W")/workspace.json"

# 세션 저장소: meta 키 0 의 칸 이름만 보기(값은 보고서에서 가림)
S=$C/.cursor/chats/9f8e7d6c/1a2b3c4d/store.db
sqlite3 "$S" "SELECT value FROM meta WHERE key = '0';" | xxd -r -p | jq 'keys'

# 코드 기여 기록의 표 구조
sqlite3 "$C/.cursor/ai-tracking/ai-code-tracking.db" ".schema"

# 대화 사본: 사용자 메시지 시각 꼬리표와 끝 레코드
grep -o '<timestamp>[^<]*</timestamp>' "$C"/.cursor/projects/*/agent-transcripts/*/*.jsonl | head
grep -c '"turn_ended"' "$C"/.cursor/projects/*/agent-transcripts/*/*.jsonl

# 훅 설정의 이벤트와 명령만 뽑기
jq '.hooks | to_entries[] | {event: .key, commands: [.value[].command]}' "$C/.cursor/hooks.json"
```

`LEFT JOIN` 으로 붙였으므로 bubble 행이 사라진 발화는 빈칸으로 나옵니다. 정리된 결과가 필요하면 agentsview 가 전역 DB 와 대화 사본을 함께 읽고[5], cursor2md 가 전역 DB 의 옛·새 구조를 마크다운으로 내보냅니다[6]. 두 도구 모두 위 "출처별 기준" 표의 판과 날짜를 기준으로 만들었으므로, 보고서에는 도구 이름과 그 기준을 함께 적습니다. Windows 에서 수집 경로를 빠뜨리지 않으려면 KapeFiles 의 Cursor 수집 대상[7]을 목록으로 씁니다.

## 교차 검증

에이전트가 실제로 한 일은 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)의 흐름으로 git 이력·셸 기록과 맞춰 보고, 앱 안에서는 `User/History/` 의 파일 사본과 `projects/*/terminals/` 의 명령 출력을 대화의 `toolFormerData` 와 맞춰 봅니다. 외부 문서나 MCP 응답이 에이전트를 부추긴 정황이 있으면 [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md)과 [MCP 서버와 도구 호출 기록](mcp.md)으로 이어 가고, 디스크에 흔적이 없으면 [메모리에서 AI 흔적 찾기](../../03-techniques/analysis/memory-analysis.md)를 봅니다. VS Code 에서 쓰는 [GitHub Copilot](github-copilot/index.md)이나 역시 훅을 쓰는 [Claude Code](claude-code/index.md)가 같은 PC 에 함께 있으면 흔적이 섞이지 않게 도구별로 나눕니다. 서비스 접속 시각은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)과, 회사가 허용한 도구인지는 [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md)와 함께 봅니다. 수집 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다.

## 실습

시험용 가상 머신과 시험 계정으로 시험 데이터를 만들어 풉니다.

1. 작업 공간 두 개를 열어 각각 에이전트에게 한 번씩 일을 시킨 뒤, 전역 `state.vscdb` 에 `composerData:` 행이 몇 개 생겼고 각 행의 `workspaceIdentifier.uri.fsPath` 가 어느 폴더인지 적어 봅니다.
2. 같은 대화가 `~/.cursor/projects/*/agent-transcripts/` 와 `~/.cursor/chats/*/*/store.db` 에도 생겼는지 확인하고, 세 곳의 ID 를 맞춰 봅니다. 출처끼리 다른 설명 가운데 지금 판이 어느 쪽인지 적습니다.
3. 대화 하나에서 `composerData.lastUpdatedAt` 과 마지막 bubble 의 `createdAt` 을 UTC 로 바꿔 비교합니다.
4. `beforeShellExecution` 훅에 입력을 파일로 적는 스크립트를 걸고, 에이전트에게 명령을 시킨 뒤 훅 기록, `toolFormerData`, `terminals/` 출력, `logs/` 의 `cursor.hooks.*.log` 시각을 맞춰 봅니다.
5. 앱 버전과 `_v` 값을 적고, 판을 올린 뒤 같은 실습을 되풀이해 달라진 키와 필드를 비교합니다.

## 참고 문헌

1. Cursor Docs — Hooks — https://cursor.com/docs/agent/hooks
2. Cursor Docs — Model Context Protocol (MCP) — https://cursor.com/docs/context/mcp
3. Cursor — Security — https://cursor.com/security
4. somogyijanos/cursor-chat-export (마지막 커밋 2024-08-30, 보관 처리) — https://github.com/somogyijanos/cursor-chat-export — `config.yml`, `src/vscdb.py`, `src/export.py`, `chat.py`
5. kenn-io/agentsview — https://github.com/kenn-io/agentsview — `docs/internal/session-format-sources.md`(2026-09-11), `internal/parser/cursor_ide.go`, `internal/parser/cursor.go`, `internal/parser/cursor_paths.go`, `internal/parser/cursor_provider.go`, `internal/parser/cursor_store.go`, `README.md`
6. changlehu/cursor-chat-export-to-markdown (2026-08-17) — https://github.com/changlehu/cursor-chat-export-to-markdown — `cursor2md.py`
7. EricZimmerman/KapeFiles (2026-09-18) — https://github.com/EricZimmerman/KapeFiles — `Targets/Apps/Cursor.tkape`
8. thellmwhisperer/la-roca (2026-09-21) — https://github.com/thellmwhisperer/la-roca — `docs/ingest.md`
9. Satter, A., Salmon, M., Muhanna, L., Spinosa, T. T., Gharaibeh, T., Baggili, I. — With or Without Logs: Memory Forensic Reconstruction of Model Context Protocol (MCP) Activity in Agentic LLM Systems — 저자 원고, 도구 저장소 https://github.com/BiTLab-BaggiliTruthLab/MCPRecon
