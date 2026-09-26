---
title: "GitHub Copilot"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 600
has_children: true
has_toc: false
---

# GitHub Copilot (VS Code·JetBrains)

GitHub Copilot 은 여러 IDE 와 터미널에서 도는 코딩 도우미이고, 어디서 썼느냐에 따라 대화가 VS Code 사용자 데이터 폴더, Copilot CLI 의 `~/.copilot` 폴더, Visual Studio 의 추적 파일처럼 서로 다른 곳에 남습니다.


## 왜 중요한가

Copilot 은 JetBrains IDE(IntelliJ IDEA, Android Studio, GoLand, PhpStorm, PyCharm, RubyMine, WebStorm, Rider), VS Code, Visual Studio, Xcode, Vim/Neovim 에서 돌고, 터미널용 Copilot CLI 도 따로 있습니다. 제품마다 저장 위치와 형식이 달라서, 개발자 PC 를 조사할 때는 어느 IDE 와 도구를 썼는지부터 가려내야 합니다.

VS Code 는 채팅 세션을 작업 폴더(워크스페이스)마다 `workspaceStorage` 아래 해시 폴더에 JSON·JSONL 파일로 남깁니다[1]. 같은 해시 폴더의 `workspace.json` 에 적힌 `folder` 또는 `workspace` 값으로 어느 프로젝트인지 알 수 있고, 세션 파일의 `creationDate`·`lastMessageDate` 는 Unix 밀리초라서 "어느 프로젝트에서 언제 AI 와 대화했나" 를 좁히는 데 쓸 수 있습니다[1]. 세션 색인에는 로컬 세션 말고도 백그라운드·클라우드 세션처럼 외부에서 불러온 세션이 `isExternal` 표시와 함께 들어갑니다[2]. 다른 에이전트 도구가 만든 세션이면 대화 원본은 그 도구 쪽 폴더에서 찾으면 됩니다. Claude Code 는 [Claude Code](../claude-code/index.md), Codex 는 [Codex CLI](../codex-cli.md) 쪽을 봅니다.

Copilot CLI 는 세션마다 이벤트를 JSONL 로 적습니다. `tool.execution_start` 와 `tool.execution_complete` 이벤트는 같은 `data.toolCallId` 를 달고 각각 RFC3339 형식의 `timestamp` 를 남겨서, 에이전트가 도구를 언제부터 언제까지 실행했는지 알 수 있습니다(Copilot CLI 1.0.76-0 기준)[1].

Visual Studio 의 Copilot 은 대화를 OpenTelemetry 형식의 추적 파일 `*_VSGitHubCopilot_traces.jsonl` 에 담습니다[1]. Visual Studio 2026 은 솔루션 폴더 아래 `.vs` 에도 대화 파일을 쓰므로[1], 솔루션 폴더도 수집 범위에 넣습니다. 공개된 생산자 쪽 형식 문서가 없어서, 필드 이름은 agentsview 가 읽는 것을 기준으로 삼고 실제 데이터로 확인합니다[1].

JetBrains IDE 는 Copilot 채팅을 Nitrite 데이터베이스에 저장합니다[1]. 이 데이터베이스는 공개 도구 copilot-jetbrains-exporter 로 JSONL 로 내보낸 뒤 읽을 수 있습니다[1]. 데이터베이스 파일 경로를 적은 공개 분석 자료는 없어서, 실제 기기에서 확인해야 합니다.

GitHub 서버에 남는 프롬프트·응답과 조직 요금제의 감사 기록은 PC 에서 얻을 수 없습니다. 서버 쪽 기록은 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)으로 얻습니다.

## 한눈에 보기

| 위치 | OS | 앱 버전 | 알려 주는 것 |
|---|---|---|---|
| VS Code `Code/User/settings.json`, 프로필별 `settings.json`, 작업 폴더의 `.vscode/settings.json` | Windows·macOS·Linux | 문서 기준(2026-09) | Copilot·채팅 설정, 원격 측정 범위 |
| `Code/User/workspaceStorage/<hash>/chatSessions/*.json`, `*.jsonl` | Windows·macOS·Linux | 소스 기준[2]. 1.109 전은 `.json`, 1.109 부터 `.jsonl`. agentsview 는 1.132 로 2026-08-12 시험[1] | 작업 폴더별 로컬 채팅 세션. 같은 UUID 로 두 형식이 함께 있으면 agentsview 는 `.jsonl` 을 기준으로 읽음 |
| `Code/User/workspaceStorage/<hash>/workspace.json` | Windows·macOS·Linux | 소스 기준[1] | 해시 폴더가 가리키는 프로젝트(`folder` 또는 `workspace`) |
| `Code/User/globalStorage/emptyWindowChatSessions/`, `transferredChatSessions/` | Windows·macOS·Linux | 소스 기준[1] | 폴더를 열지 않은 창의 채팅, 다른 작업 폴더로 넘긴 세션 |
| VS Code 저장소 서비스의 키 `chat.ChatSessionStore.index` | Windows·macOS·Linux | 소스 기준(2026-08)[2] | 세션 제목, 마지막 메시지 시각, 작업 폴더, 외부 세션 여부 |
| VS Code 출력 창, 확장 로그 폴더, `telemetry.log` | Windows·macOS·Linux | 문서 기준 | 오류·연결 문제, 원격 측정 |
| `~/.copilot/session-state/<uuid>.jsonl` 또는 `<uuid>/events.jsonl`, 같은 폴더의 `workspace.yaml` | Windows·macOS·Linux | Copilot CLI 1.0.76-0 으로 2026-07-28 시험[1] | Copilot CLI 세션 이벤트(메시지, 모델, 도구 실행 시작·끝), 세션 이름 |
| `~/.copilot/session-store.db`(`-wal` 포함) | Windows·macOS·Linux | Copilot CLI 1.0.83 으로 2026-09-10 시험[1] | 세션 파일에서 다시 만드는 SQLite 저장소, `assistant_usage_events` 표의 모델 호출별 사용량 |
| Windows `%LOCALAPPDATA%\Temp\VSGitHubCopilotLogs\traces\`, macOS `~/Library/Caches/VSGitHubCopilotLogs/traces/`, Linux `~/.cache/VSGitHubCopilotLogs/traces/` 의 `*_VSGitHubCopilot_traces.jsonl` | Windows·macOS·Linux | 공개 형식 문서 없음[1] | Visual Studio Copilot 대화, `gen_ai.conversation.id`, `gen_ai.usage.input_tokens`·`output_tokens` |
| 솔루션 폴더의 `.vs\*\copilot-chat\*\sessions\` 안 확장자 없는 파일 | Windows | Visual Studio 2026[1] | Visual Studio 대화 파일 |
| JetBrains `idea.log` | Windows·macOS·Linux | 문서 기준 | Copilot 오류, 사용자가 켠 진단·trace·인증서 기록 |
| JetBrains Nitrite 데이터베이스 | Windows·macOS·Linux | 경로는 실제 기기에서 확인[1] | JetBrains Copilot 채팅 |
| `~/Library/Logs/GitHubCopilot/` | macOS | 문서 기준 | Xcode 용 Copilot 로그 |
| 사용자가 고른 자리의 내보낸 JSON | 모두 | 문서 기준 | `Chat: Export Chat...` 로 내보낸 프롬프트·응답 |

`Code/User` 는 Windows 에서 `%APPDATA%\Code\User`, macOS 에서 `~/Library/Application Support/Code/User`, Linux 에서 `~/.config/Code/User` 입니다[1]. VS Code 의 `.jsonl` 세션 파일은 처음 모양 위에 바뀐 내용을 한 줄씩 덧붙인 조작 기록이라서, 앞 줄부터 차례로 적용해야 최종 대화가 나오고 나중에 바뀐 값의 이전 값이 앞 줄에 남습니다[1]. `~/.copilot/session-store.db` 는 세션 파일에서 다시 만들 수 있는 저장소이고, 그 안의 가장 늦은 시각이 세션 파일 전체를 다 담았다는 뜻은 아닙니다[1].

## 읽는 순서

1. [Windows](windows.md) — Windows 경로, VS Code 채팅 세션 폴더와 파일 형식, 세션 파일의 키와 JSONL 조작 기록 읽는 법, 세션 색인, 보관·삭제·내보내기
2. [macOS](macos.md) — macOS 경로, Xcode 용 Copilot 로그 폴더
3. [로그와 원격 측정](logs.md) — IDE 별 로그 여는 법, 사용자가 켜야 생기는 기록, VS Code 원격 측정 설정, Visual Studio 추적 파일

## 함께 볼 페이지

- [Claude Code](../claude-code/index.md), [Cursor](../cursor.md), [Codex CLI](../codex-cli.md), [Gemini CLI](../gemini-cli.md) — 같은 기준으로 비교
- [MCP 서버와 도구 호출 기록](../mcp.md) — VS Code 와 Copilot 을 MCP 클라이언트로 쓴 메모리 분석 연구
- [Microsoft Copilot](../../chat-services/copilot/index.md) — 이름이 비슷한 다른 서비스
- [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)
- [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)
- [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md) — 사용자 폴더 밖의 `.vs` 폴더까지 수집 범위에 넣기
- [기밀 자료를 AI에 넣었나](../../../04-scenarios/data-leak/confidential-input.md)
- [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)

## 참고 문헌

1. kenn-io/agentsview. https://github.com/kenn-io/agentsview — `README.md`(Supported Agents 표, JetBrains Copilot via exporter), `docs/internal/session-format-sources.md`(2026-09-11), `internal/parser/vscode_copilot.go`, `internal/parser/vscode_copilot_provider.go`, `internal/parser/copilot.go`, `internal/parser/copilot_provider.go`, `internal/parser/visualstudio_copilot_provider.go`
2. microsoft/vscode. https://github.com/microsoft/vscode — `src/vs/workbench/contrib/chat/common/model/chatSessionStore.ts`
