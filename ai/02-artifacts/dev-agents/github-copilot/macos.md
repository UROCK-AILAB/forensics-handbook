---
title: "GitHub Copilot macOS"
parent: "GitHub Copilot"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 620
---

# macOS (macOS)

macOS 에서 GitHub Copilot 기록은 제품마다 다른 폴더에 남습니다. VS Code 채팅은 `~/Library/Application Support/Code/User` 아래, Copilot CLI 는 `~/.copilot` 아래, Visual Studio 추적 파일은 `~/Library/Caches/VSGitHubCopilotLogs/traces` 아래, Xcode 용 Copilot 로그는 `~/Library/Logs/GitHubCopilot` 아래에 있습니다.

> 이 쪽의 형식은 VS Code 1.132(JSONL 세션), Copilot CLI 1.0.76-0(세션 기록), Copilot CLI 1.0.83 macOS(arm64) 기준입니다[5]. 이보다 새 판에서는 경로나 칸이 다를 수 있으니 검체의 앱 버전부터 적어 둡니다.

## 무엇을 기록하나 · 왜 생기나

VS Code 는 채팅 세션을 저장하는 코드가 OS 와 상관없이 같아서, 세션 파일의 짜임과 세션 목록 키 `chat.ChatSessionStore.index` 는 macOS 에서도 같습니다. 세션 파일의 칸과 JSONL 조작 기록을 다시 적용하는 방법은 [Windows](windows.md)에서 다루고, 이 페이지는 macOS 경로와 macOS 에서 함께 쓰이는 다른 Copilot 제품을 다룹니다. 출력 창·`idea.log`·원격 측정 로그는 [로그와 원격 측정](logs.md)에 있습니다.

한 사용자 계정에 Copilot 이 여러 모양으로 들어올 수 있습니다. 편집기 안의 채팅(VS Code), 터미널에서 쓰는 Copilot CLI, Visual Studio 의 Copilot, Xcode 용 Copilot, JetBrains IDE 플러그인이 저마다 다른 폴더에 기록하므로, 한 곳만 보고 Copilot 을 쓰지 않았다고 판단하지 않습니다.

## 위치와 버전별 차이

아래 표의 `~` 는 사용자 홈 폴더(`/Users/사용자이름`)입니다.

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `~/Library/Application Support/Code/User/settings.json` | VS Code 사용자 설정(Copilot·채팅 설정 키 포함) | VS Code 문서 [1] |
| `~/Library/Application Support/Code/User/profiles/<profile ID>/settings.json` | 프로필별 설정 | VS Code 문서 [1] |
| 작업 폴더 루트의 `.vscode/settings.json` | 작업 폴더 설정 | VS Code 문서 [1] |
| `~/Library/Application Support/Code/User/workspaceStorage/<hash>/chatSessions/*.json`, `*.jsonl` | 폴더를 연 창의 채팅 세션 | agentsview [3][4] |
| `~/Library/Application Support/Code/User/workspaceStorage/<hash>/workspace.json` | 그 `<hash>` 폴더가 어느 프로젝트인지 | agentsview [4] |
| `~/Library/Application Support/Code/User/globalStorage/emptyWindowChatSessions/` | 폴더 없이 연 빈 창의 채팅 | agentsview [3], VS Code 소스 [2] |
| `~/Library/Application Support/Code/User/globalStorage/transferredChatSessions/` | 다른 작업 영역으로 넘긴 세션 | agentsview [3], VS Code 소스 [2] |
| `~/Library/Application Support/Code/User/workspaceStorage/no-workspace/chatSessions/*.json` | 예전 빈 창 세션 자리. VS Code 는 빈 창 세션을 여기서도 읽어 옴(agentsview 는 이 폴더를 읽지 않음) | VS Code 소스 [2] |
| `~/.copilot/session-state/<uuid>.jsonl` 또는 `~/.copilot/session-state/<uuid>/events.jsonl` | Copilot CLI 세션 이벤트 | GitHub 문서(agentsview 가 2026-07-19 확인) [5], agentsview [6] |
| `~/.copilot/session-state/<uuid>/workspace.yaml` | Copilot CLI 세션 이름(`name:` 줄) | agentsview [7] |
| `~/.copilot/session-store.db`, `session-store.db-wal` | 세션 파일에서 만든 SQLite 저장소 | GitHub 문서(agentsview 가 2026-07-19 확인) [5], agentsview [6] |
| `~/Library/Caches/VSGitHubCopilotLogs/traces/*_VSGitHubCopilot_traces.jsonl` | Visual Studio Copilot 추적 파일 | agentsview README [8] |
| `~/Library/Logs/GitHubCopilot/` | Xcode 용 Copilot 로그 폴더 | GitHub 문서 [9] |
| `~/Library/Logs/GitHubCopilot/github-copilot-for-xcode.log` | Xcode 용 Copilot 의 최근 로그 파일 | GitHub 문서 [9] |

Linux 에서는 VS Code 가 같은 폴더 짜임을 `~/.config/Code/User` 아래에 씁니다 [1][3]. Visual Studio 추적 파일은 Windows 에서 `%LOCALAPPDATA%\Temp\VSGitHubCopilotLogs\traces\`, Linux 에서 `~/.cache/VSGitHubCopilotLogs/traces/` 에 있습니다 [8].

판에 따라 달라지는 점은 아래와 같습니다.

| 대상 | 차이 | 근거 |
|---|---|---|
| VS Code 세션 파일 | 1.109 전에는 세션마다 JSON 한 파일, 1.109 부터는 줄을 덧붙이는 JSONL 로그. 설정 `chat.useLogSessionStorage` 가 `false` 이면 JSONL 을 쓰지 않음 | VS Code 소스 주석과 코드 [2] |
| VS Code 세션 목록 키 | 1.109 전 목록 항목에는 `timing` 칸이 없어서, VS Code 가 `lastMessageDate` 로 채워 넣음 | VS Code 소스 주석 [2] |
| VS Code 세션 파일 | 같은 세션 ID 로 `.json` 과 `.jsonl` 이 함께 있으면 agentsview 는 `.jsonl` 을 읽음 | agentsview [3] |
| Copilot CLI 세션 | 파일 하나(`<uuid>.jsonl`)로 쓰는 방식과 폴더(`<uuid>/events.jsonl`)로 쓰는 방식이 있고, 둘 다 있으면 agentsview 는 폴더 쪽을 읽음 | agentsview [6] |
| Copilot CLI 저장소 | 1.0.60 배포 패키지는 저장소 스키마 4판을 만들고, 이 판에는 사용량 표 `assistant_usage_events` 가 없음 | agentsview 형식 조사 [5] |

## 구조

### VS Code 채팅 세션

세션 파일의 칸(`sessionId`, `creationDate`, `lastMessageDate`, `customTitle`, `requests[]`)과 JSONL 조작 기록(`kind` 0~3)은 [Windows](windows.md)의 구조 절을 봅니다. macOS 에서 함께 볼 것은 `workspace.json` 입니다. 이 파일의 `folder` 칸(여러 폴더 작업 영역이면 `workspace` 칸)에 `file:///Users/...` 모양의 주소가 들어 있어서 [4], 이름만으로는 알 수 없는 `<hash>` 폴더를 프로젝트 폴더와 이을 수 있습니다.

아래는 폴더 짜임을 보여 주려고 만든 예시입니다.

```text
~/Library/Application Support/Code/User/
  workspaceStorage/
    3f9c0d2e7a1b4c5d6e7f8a9b0c1d2e3f/        (만든 예시 hash)
      workspace.json                          {"folder":"file:///Users/analyst01/work/demo-app"}
      chatSessions/
        0b6e1c2a-5d4f-4e3a-9c8b-7a6f5e4d3c2b.jsonl
  globalStorage/
    emptyWindowChatSessions/
    transferredChatSessions/
```

### Copilot CLI 이벤트

Copilot CLI 세션 파일은 한 줄에 이벤트 하나를 적는 JSONL 이고, 줄마다 `type`, `timestamp`, `data` 가 있습니다 [7]. 주요 이벤트 종류와 칸은 아래와 같습니다 [7].

| `type` | 주요 칸 | 알려 주는 것 |
|---|---|---|
| `session.start` | `data.sessionId`, `data.context.cwd`, `data.context.branch` | 세션 ID, CLI 를 실행한 폴더, git 브랜치 |
| `user.message` | `data.content`, `data.source` | 사용자가 넣은 글. `source` 가 `skill-` 로 시작하면 사용자 입력이 아니라 스킬이 넣은 글 |
| `assistant.message` | `data.content`, `data.reasoningText`, `data.toolRequests[]`(`name`, `arguments`, `toolCallId`), `data.model`, `data.outputTokens` | 응답, 추론 글, 요청한 도구와 인자, 모델, 출력 토큰 수 |
| `tool.execution_start` | `data.toolCallId` | 도구 실행 시작 |
| `tool.execution_complete` | `data.toolCallId`, `data.result`, `data.success` | 도구 실행 결과와 성공 여부 |
| `session.model_change` | `data.newModel` | 세션 도중 모델을 바꿈 |
| `session.shutdown` | `data.modelMetrics`(모델별 `usage` 의 `inputTokens`, `outputTokens`, `cacheReadTokens`, `cacheWriteTokens`, `reasoningTokens`), `data.totalNanoAiu` | 세션 종료와 모델별 사용량 합계 |

`assistant.reasoning` 줄도 있지만 agentsview 는 이 줄의 칸을 읽지 않습니다 [7]. `tool.execution_start` 와 `tool.execution_complete` 는 같은 `toolCallId` 를 쓰고 저마다 RFC3339 `timestamp` 가 있어서, 도구 하나가 언제 시작해 언제 끝났는지 짝을 지어 볼 수 있습니다 [5]. `session-store.db` 는 세션 파일에서 다시 만드는 저장소이고, GitHub 는 이 표 구조를 공개하지 않았습니다 [5]. 1.0.83 macOS 배포 패키지는 모델을 한 번 부를 때마다 이 저장소에 사용량 한 줄을 쓰고 ISO 형식 시각을 붙입니다 [5].

### Visual Studio 추적 파일

추적 파일은 OpenTelemetry span 을 한 줄에 하나씩 적은 JSONL 입니다 [5]. 대화는 span 속성 `gen_ai.conversation.id` 로 나뉘고, 토큰 수는 `gen_ai.usage.input_tokens` 와 `gen_ai.usage.output_tokens` 에 있습니다 [5][10]. Visual Studio Copilot 은 대화를 이 공용 추적 파일 안에 저장합니다 [10]. Microsoft 는 이 파일 형식을 공개하지 않았습니다 [5].

### Xcode 용 Copilot 로그

Xcode 용 Copilot 앱에서 Advanced → Open Copilot Log Folder 를 누르면 로그 폴더가 열리고, Advanced → Logging → Verbose Logging 스위치를 켜면 더 자세한 로그를 남깁니다 [9]. 로그 줄의 형식과 프롬프트·응답 본문이 들어가는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다.

### JetBrains IDE

macOS 의 JetBrains IDE 에서는 Help → Show Log in Finder 로 `idea.log` 를 엽니다 [9]. JetBrains IDE 는 Copilot 채팅을 Nitrite 데이터베이스에 저장하고, 이 데이터베이스는 `copilot-jetbrains-exporter` 로 JSONL 을 뽑아서 읽을 수 있습니다 [8]. 그 데이터베이스 파일의 경로는 공개된 분석 자료가 없어 검체로 확인해야 합니다. `idea.log` 에 남는 Copilot 관련 줄은 [로그와 원격 측정](logs.md)에서 다룹니다.

## 증거로서 의미

VS Code 세션 파일과 설정 파일이 증명하는 것과 증명하지 못하는 것은 [Windows](windows.md)와 같습니다.

**증명하는 것.** `~/.copilot/session-state` 의 세션 파일은 그 계정에서 Copilot CLI 로 대화한 기록입니다. `session.start` 의 `context.cwd` 는 CLI 를 실행한 폴더이고, `tool.execution_*` 짝은 에이전트가 도구를 부른 시각과 결과입니다 [7]. `workspace.json` 은 VS Code 채팅 세션이 어느 프로젝트 폴더에서 열렸는지 알려 줍니다 [4]. Xcode 용 Copilot 로그 파일이 있으면 그 계정에서 Xcode 용 Copilot 을 실행한 적이 있다고 읽을 수 있습니다.

**증명하지 못하는 것.** 도구 호출 기록은 에이전트가 명령을 요청하고 결과를 받았다는 기록이지, 사용자가 그 명령을 직접 입력했다는 기록이 아닙니다. 추적 파일과 `session-store.db` 의 토큰 수는 사용량일 뿐이라서 무엇을 보냈는지는 알려 주지 않습니다. Xcode 로그 파일만으로는 어떤 코드를 제안받았는지, 제안을 받아들였는지를 알 수 없습니다. 에이전트가 한 일을 순서대로 세우는 방법은 [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)에 있습니다.

## 시각 해석

| 기록 | 시각 칸 | 형식 | 근거 |
|---|---|---|---|
| VS Code 세션 파일 | `creationDate`, `lastMessageDate`, `requests[].timestamp` | Unix 밀리초(UTC 기준) | agentsview [4] |
| Copilot CLI 이벤트 | 줄마다 `timestamp` | RFC3339 문자열(시간대 표시 포함) | agentsview [5][7] |
| Copilot CLI 저장소 사용량 | 줄마다 시각 | ISO 형식 | agentsview 형식 조사 [5] |
| Visual Studio 추적 파일 | span 의 `startTimeUnixNano`, `endTimeUnixNano` | Unix 나노초를 적은 문자열 | agentsview [11] |

세션 목록 키의 `lastMessageDate` 를 읽을 때 조심할 점은 [Windows](windows.md)의 시각 해석 절과 같습니다. macOS 에서는 파일 시스템 시각에 더해 파일 시스템 이벤트 기록으로 세션 파일이 언제 생기고 바뀌었는지 맞춰 볼 수 있습니다. 구조는 [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/fsevents/index.html)에, 여러 기록을 한 줄로 세우는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

- **제품마다 폴더가 다릅니다.** VS Code, Copilot CLI, Visual Studio, Xcode, JetBrains 기록은 서로 다른 폴더에 있어서, 한쪽이 비어 있다고 다른 쪽도 없다고 보지 않습니다.
- **VS Code JSONL 세션은 마지막 줄만 보면 안 됩니다.** 조작 기록이라서 처음부터 다시 적용해야 최종 모양이 나오고, 나중에 바뀐 값의 이전 값은 앞 줄에 남습니다 [4]. 다시 적용하는 방법은 [Windows](windows.md)에 있습니다.
- **`session-store.db` 는 WAL 과 함께 뜹니다.** `session-store.db-wal` 을 빼고 복사하면 최근 기록이 빠질 수 있습니다. 저장소에서 가장 늦은 사용량 줄의 시각이 세션 전체가 기록됐다는 뜻은 아닙니다 [5]. WAL 을 읽는 법은 [SQLite](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/data-formats/sqlite/index.html)에 있습니다.
- **Visual Studio 추적 파일은 캐시 폴더에 있습니다.** `~/Library/Caches` 아래라서 수집할 때 파일이 남아 있는지부터 확인합니다.
- **로그인 정보는 따로 봅니다.** Copilot 로그인 토큰이 키체인에 들어가는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 키체인 구조는 [키체인](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/protection/keychain/index.html)에, 토큰이 흔히 남는 자리와 보고서에서 가리는 법은 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다. VS Code 세션 파일과 Copilot CLI 세션 파일은 복호화 단계 없이 JSON 으로 읽힙니다 [4][7].
- **MCP 도구 호출.** Copilot 에 붙인 MCP 서버의 기록은 [MCP 서버와 도구 호출 기록](../mcp.md)에서 다룹니다.

## 직접 분석해 보기

**텍스트로 한 번.** JSONL 은 한 줄이 JSON 하나라서 텍스트 뷰어로 바로 읽힙니다. 아래 세 줄은 형식을 보여 주려고 만든 예시입니다.

```text
{"kind":1,"k":["customTitle"],"v":"로그인 오류 고치기"}
{"type":"tool.execution_start","timestamp":"2026-09-01T02:14:07.512Z","data":{"toolCallId":"call_demo_0001"}}
{"type":"tool.execution_complete","timestamp":"2026-09-01T02:14:09.030Z","data":{"toolCallId":"call_demo_0001","success":true}}
```

첫 줄은 VS Code 세션 파일의 조작 한 줄이고, `kind` 1 은 경로 `k` 에 값 `v` 를 넣는다는 뜻입니다. 둘째·셋째 줄은 Copilot CLI 의 도구 실행 시작과 끝이고, `toolCallId` 가 같은 두 줄의 `timestamp` 차이가 도구 실행 시간입니다.

`session-store.db` 는 WAL 과 함께 사본을 만들어 macOS 에 들어 있는 `sqlite3` 로 엽니다. 표 구조가 공개되지 않았으므로 `.tables` 와 `.schema` 로 표 이름과 칸부터 확인합니다.

```sh
mkdir -p /tmp/case
cp ~/.copilot/session-store.db ~/.copilot/session-store.db-wal /tmp/case/
sqlite3 /tmp/case/session-store.db ".tables"
```

**공개 도구로 한 번.** agentsview [3] 는 VS Code 채팅, Copilot CLI, Visual Studio 추적 파일을 읽어 세션 목록으로 보여 줍니다. 원본 폴더가 아니라 떠 온 사본을 가리키게 설정하고, 도구 결과는 원본 줄 몇 개를 골라 위처럼 직접 맞춰 봅니다.

## 교차 검증

- VS Code 세션의 `workspace.json` 프로젝트 폴더와 Copilot CLI 의 `context.cwd` 가 같은 폴더를 가리키는지 봅니다.
- `tool.execution_*` 기록에 파일을 고친 도구가 있으면 그 파일의 수정 시각과 [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/fsevents/index.html)를 맞춰 봅니다.
- 조직 계정이면 서버 쪽 사용 기록을 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md) 절차로 받아 기기 기록과 비교합니다.
- 같은 시간대에 다른 코딩 에이전트([Claude Code](../claude-code/index.md), [Codex CLI](../codex-cli.md), [Cursor](../cursor.md))를 썼는지 함께 봅니다.

## 실습

시험용 macOS 계정(가짜 사용자 `analyst01`, 가짜 작업 폴더 `~/work/demo-app`)을 만들어 풀어 봅니다.

1. VS Code 에서 폴더를 열고 채팅을 한 뒤, `workspaceStorage` 아래 어느 hash 폴더에 `chatSessions` 가 생기는가? 그 폴더의 `workspace.json` 은 무엇을 가리키는가?
2. 폴더를 열지 않은 빈 창에서 채팅하면 세션 파일은 어디에 생기는가?
3. Copilot CLI 에게 파일을 하나 만들게 한 뒤 `events.jsonl` 에서 그 도구 호출의 시작·끝 시각을 찾으면, 새 파일의 생성 시각과 맞는가?
4. Xcode 용 Copilot 에서 Verbose Logging 을 켜기 전과 뒤에 `github-copilot-for-xcode.log` 의 크기와 줄 모양은 어떻게 달라지는가?

## 참고 문헌

1. User and workspace settings — Visual Studio Code(2026-09-16 갱신, 2026-09-25 열람) — https://code.visualstudio.com/docs/configure/settings
2. microsoft/vscode, `src/vs/workbench/contrib/chat/common/model/chatSessionStore.ts`(main, 마지막 커밋 2026-08-06) — https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/common/model/chatSessionStore.ts
3. kenn-io/agentsview, `internal/parser/vscode_copilot_provider.go`(2026-09-25 기준) — https://github.com/kenn-io/agentsview
4. kenn-io/agentsview, `internal/parser/vscode_copilot.go`(2026-09-25 기준) — https://github.com/kenn-io/agentsview
5. kenn-io/agentsview, `docs/internal/session-format-sources.md`(2026-09-11 갱신) — https://github.com/kenn-io/agentsview
6. kenn-io/agentsview, `internal/parser/copilot_provider.go`(2026-09-25 기준) — https://github.com/kenn-io/agentsview
7. kenn-io/agentsview, `internal/parser/copilot.go`(2026-09-25 기준) — https://github.com/kenn-io/agentsview
8. kenn-io/agentsview, `README.md` 의 Supported Agents 표와 "JetBrains Copilot via exporter" 절(2026-09-25 기준) — https://github.com/kenn-io/agentsview
9. Viewing logs for GitHub Copilot in your environment — GitHub Docs(2026-09-25 열람) — https://docs.github.com/en/copilot/troubleshooting-github-copilot/viewing-logs-for-github-copilot-in-your-environment
10. kenn-io/agentsview, `internal/parser/visualstudio_copilot_provider.go`(2026-09-25 기준) — https://github.com/kenn-io/agentsview
11. kenn-io/agentsview, `internal/parser/visualstudio_copilot.go`(2026-09-25 기준) — https://github.com/kenn-io/agentsview
