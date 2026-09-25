---
title: "MCP 서버와 도구 호출 기록"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 640
---

# MCP 서버와 도구 호출 기록 (MCP)

MCP(Model Context Protocol)는 AI 앱이 바깥의 도구 서버를 불러 쓰는 규약이고, 기기에는 어떤 서버를 붙였는지 적은 설정 파일과 호스트 앱이 받아 둔 서버 로그가 남지만, 원격 서버가 실제로 한 일은 그 서버 쪽에만 남을 수 있습니다.

> 확인 날짜: 2026-09. 앱 버전은 확인하지 못했습니다. 규약과 Claude 데스크톱 로그는 MCP 공식 디버깅 문서[3], Cursor 설정은 Cursor 문서[1][2] 기준입니다. 관찰은 Windows 11 PC 한 대의 폴더·키 이름뿐이고 값은 보지 않았습니다(확인 범위: Windows 11, 2026-09).

## 무엇을 기록하나 · 왜 생기나

MCP 에서 AI 앱(호스트)은 설정 파일에 적힌 서버를 띄우거나 접속해, 그 서버가 내놓는 도구를 모델이 부를 수 있게 합니다. 서버와 주고받는 방식(전송 방식)은 로컬 프로세스로 띄워 표준 입출력으로 대화하는 stdio 와 원격 서버에 접속하는 Streamable HTTP 가 있고[3], Cursor 는 여기에 SSE 도 지원합니다[2].

흔적이 남는 곳은 전송 방식에 따라 갈립니다. stdio 서버가 표준 오류(stderr)로 쓴 로그는 호스트 앱이 자동으로 받아 두고, 표준 출력(stdout)은 규약 통신에 쓰기 때문에 로그를 쓰면 안 됩니다[3]. 반대로 Streamable HTTP 서버의 stderr 는 클라이언트가 받지 않아서 서버 쪽에서 따로 모으거나 OpenTelemetry 를 써야 하고[3], 원격 MCP 서버가 도구를 실행한 기록은 PC 가 아니라 그 서버를 운영하는 쪽에 있습니다. 서버와 기기 중 어디에 무엇이 있는지 가르는 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

규약 안에도 로그 알림 `notifications/message` 가 있지만, 프로토콜 버전 `2026-07-28` 부터 폐기 예정으로 표시되었고 폐기 기간 동안은 남아 있습니다[3]. 로그 수준은 RFC 5424 의 8단계(debug 부터 emergency 까지)를 쓰고, 클라이언트가 요청의 `_meta` 에 `io.modelcontextprotocol/logLevel` 을 넣은 요청에만 서버가 이 알림을 보냅니다[3]. 그래서 규약 로그가 없다고 서버가 아무 일도 하지 않았다고 볼 수는 없습니다. 요청마다 `_meta` 에 `io.modelcontextprotocol/protocolVersion` 과 `io.modelcontextprotocol/clientCapabilities` 가 꼭 들어가고 `io.modelcontextprotocol/clientInfo` 는 권장 항목이라서[3], 로그에 요청 원문이 남으면 어느 클라이언트가 보낸 요청인지도 함께 남을 수 있습니다(문서에서 끌어낸 추론).

설정 파일은 자격 증명이 새는 자리이기도 합니다. stdio 서버는 환경 변수를 일부만 물려받아서 설정의 `env` 키로 값을 넘기는데[3], 문서 예시처럼 API 키를 `env` 에 적으면 설정 파일 안에 평문으로 남습니다[3]. 토큰이 남는 곳 전반은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

## 위치와 버전별 차이

MCP 설정과 로그는 호스트 앱마다 따로 둡니다. 아래 표는 문서와 관찰로 확인한 것만 담습니다.

| 호스트 앱 | 설정 | 로그 | 근거 |
|---|---|---|---|
| Claude 데스크톱 | `claude_desktop_config.json` 의 `mcpServers` | macOS `~/Library/Logs/Claude`, Windows `%APPDATA%\Claude\logs` 의 `mcp*.log` | 문서[3] |
| Claude 데스크톱(스토어 앱) | 패키지 안 `claude_desktop_config.json`, `mcp-user-tool-toggles.json` | 패키지 안 `mcp-logs-<서버 이름>` 폴더의 JSON Lines | 관찰 |
| Cursor | 전역 `~/.cursor/mcp.json`, 프로젝트 `.cursor/mcp.json` | 출력(Output) 패널의 "MCP Logs", 파일 위치 확인 못 함 | 문서[2] |
| Claude Code | [Claude Code](claude-code/index.md) 페이지에서 다룸 | 대화 기록 안의 MCP 서버 상태 | 관찰 |
| Codex CLI, Gemini CLI | 설정 키 확인 못 함 | 확인 못 함 | — |

Claude 데스크톱 로그에는 서버 연결 이벤트, 설정 문제, 실행 오류, 메시지 교환이 남습니다[3]. 관찰한 PC 에서는 스토어 앱으로 설치한 Claude 데스크톱의 패키지 폴더 안에서 MCP 흔적을 보았습니다. 스토어 앱 패키지는 `%LOCALAPPDATA%\Packages` 아래에 있고, 아래 경로는 그 안에서 관찰한 모양입니다(확인 범위: Windows 11, 2026-09).

```
%LOCALAPPDATA%\Packages\<Claude 패키지>\
  LocalCache\Local\claude-cli-nodejs\Cache\<이름>\mcp-logs-<서버 이름>\<파일>.jsonl
  LocalCache\Roaming\Claude\mcp-user-tool-toggles.json
  LocalCache\Roaming\Claude\claude_desktop_config.json
```

관찰 메모에는 `%APPDATA%\Claude\logs\mcp*.log` 가 없었고, 스토어 앱은 경로가 패키지 안으로 바뀔 수 있어서 스토어 앱의 `logs` 폴더 위치는 확인하지 못했습니다. 패키지 폴더 구조의 일반 원리는 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)와 [Claude](../chat-services/claude/index.md)에 있습니다.

## 구조

### 설정 파일

Claude 데스크톱과 Cursor 는 둘 다 최상위 `mcpServers` 아래 서버 이름별로 설정을 둡니다[2][3]. 로컬 서버는 띄울 명령과 인자, 환경 변수를 적고, 원격 서버는 주소와 인증 정보를 적습니다.

| 키 | 쓰는 곳 | 뜻 |
|---|---|---|
| `command`, `args`, `env` | Claude 데스크톱[3], Cursor 로컬 서버[2] | 띄울 명령, 인자, 넘길 환경 변수 |
| `envFile` | Cursor 로컬 서버[2] | 환경 변수 파일 |
| `url`, `headers` | Cursor 원격 서버[2] | 접속 주소, 요청 머리글 |
| `auth` | Cursor 원격 서버[2] | `CLIENT_ID`, `CLIENT_SECRET`, `scopes` |

Cursor 가 원격 서버에 OAuth 로 로그인할 때 쓰는 콜백 주소는 데스크톱이 `http://localhost:8787/callback`, 웹·에이전트가 `https://www.cursor.com/agents/mcp/oauth/callback` 이고[2], 받은 토큰을 기기 어디에 두는지는 확인하지 못했습니다. 아래는 문서 형식대로 새로 만든 예시이고, 관찰한 값이 아닙니다. `env` 값은 형식을 흉내 내지 않은 자리 표시입니다.

```json
{
  "mcpServers": {
    "notes": {
      "command": "npx",
      "args": ["-y", "example-notes-server", "C:\\Users\\alice\\notes"],
      "env": { "NOTES_TOKEN": "xxxx" }
    }
  }
}
```

`command` 와 `args` 에서 어떤 프로그램이 어떤 폴더를 대상으로 떴는지, `url` 에서 어느 원격 서버에 붙도록 설정했는지를 알 수 있어서, 도구가 건드릴 수 있었던 범위를 좁히는 출발점이 됩니다.

관찰한 스토어 앱의 `claude_desktop_config.json` 에는 `mcpServers` 키가 없었고 `preferences` 와 `coworkUserFilesPath` 만 있었습니다(확인 범위: Windows 11, 2026-09). 서버를 등록했을 때만 `mcpServers` 가 생긴다고 짐작할 수 있지만, 관찰에서 끌어낸 추론이고 문서로 확인하지는 않았습니다. 같은 폴더의 `mcp-user-tool-toggles.json` 은 `owners`(사전), 그 아래 목록, `v`(정수)로 되어 있어서 도구를 켜고 끈 상태로 보이지만 용도는 확인하지 못했습니다(확인 범위: Windows 11, 2026-09).

### 호스트 앱이 받은 서버 로그

스토어 앱 패키지의 `mcp-logs-<서버 이름>` 폴더에 있던 JSON Lines 파일은 한 줄의 키가 `cwd`, `debug`, `sessionId`, `timestamp` 였습니다(확인 범위: Windows 11, 2026-09). 폴더 이름에 서버 이름이 들어가서 어느 서버의 로그인지 폴더만 보고 나눌 수 있고, `sessionId` 는 칸 이름으로 보아 호스트 앱 쪽 세션과 이어 볼 단서로 짐작되지만 문서로 확인하지는 않았습니다. `debug` 칸에 무엇이 적히는지는 값을 보지 않아서 확인하지 못했습니다.

### 대화 기록과 훅에 남는 MCP 흔적

Claude Code 대화 기록 줄에서 `attachment.failedMcpServers`, `attachment.pendingMcpServers` 키를 보았고(확인 범위: Windows 11, 2026-09), MCP 서버 연결이 실패하거나 대기 중이었던 사실이 대화 기록에 함께 남는다는 뜻입니다. 대화 기록 구조는 [Claude Code](claude-code/index.md)에서 다룹니다.

Cursor 는 `beforeMCPExecution`, `afterMCPExecution` 훅으로 MCP 호출 전후에 사용자 스크립트를 돌릴 수 있어서[1], 조직이 감사 로그를 남겼는지 확인할 곳이 됩니다. 관찰한 PC 의 `~/.cursor/hooks.json` 에도 `beforeMCPExecution` 훅이 있었습니다(확인 범위: Windows 11, 2026-09). 훅 파일 형식은 [Cursor](cursor.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 설정 파일에 서버가 있으면 그 호스트 앱에 그 서버를 붙이도록 설정한 기록이 있다는 뜻이고, `command`·`args`·`url` 이 서버의 정체와 대상 폴더·주소를 알려 줍니다. 호스트 앱이 받은 로그에 연결·오류·메시지 교환이 있으면 "이 시각에 이 서버가 떠서 호스트와 통신한 기록이 있다" 고 쓸 수 있습니다. Cursor 는 기본으로 MCP 도구를 쓰기 전에 승인을 묻는데[2], 감사 훅이나 대화 기록에 승인 흔적이 있으면 사람이 허락했는지를 판단하는 근거가 됩니다.

**증명하지 못하는 것.** 설정에 없다고 MCP 서버를 쓰지 않았다고 말할 수 없는데, Cursor 확장 프로그램이 `vscode.cursor.mcp.registerServer()` 로 서버를 등록하면 설정 파일에 남지 않기 때문입니다[2]. Cursor 는 Run Mode 설정에 따라 허용 목록에 있는 도구를 묻지 않고 바로 실행해서[2], 승인 흔적이 없다고 도구가 실행되지 않았다고 볼 수도 없습니다. 원격 서버가 도구 호출을 받아 실제로 무엇을 했는지는 기기 로그로 알 수 없고 서버 운영 쪽 자료가 필요합니다. 설정 파일에 적힌 API 키는 그 키가 있었다는 사실만 보여 줄 뿐, 누가 그 키를 썼는지는 서비스 쪽 기록으로 확인합니다.

## 시각 해석

관찰한 JSON Lines 로그에 `timestamp` 칸이 있었지만, 값을 보지 않아서 형식과 시간대는 확인하지 못했습니다. 검체에서는 몇 줄을 열어 끝에 `Z` 나 `+09:00` 같은 시간대 표시가 있는지 먼저 봅니다. `mcp*.log` 의 시각 형식도 확인하지 못했습니다. 설정 파일에는 시각 칸이 없어서, 서버를 언제 등록했는지는 파일 수정 시각이나 백업·볼륨 섀도 사본의 이전 판을 비교해 좁힙니다. 여러 출처를 한 줄로 맞추는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

MCP 설정은 호스트 앱마다, 그리고 전역·프로젝트 범위마다 흩어집니다. 한 앱의 설정만 보고 "MCP 를 쓰지 않았다" 고 쓰기 쉬워서, 설치된 AI 도구 목록부터 만들고 도구별로 전역 설정과 저장소 안의 프로젝트 설정을 모두 모읍니다. 관찰한 `~/.gemini/config/mcp_config.json` 처럼 JSON 으로 읽히지 않는 파일도 있었는데(확인 범위: Windows 11, 2026-09), 빈 파일인지 다른 형식인지는 확인하지 못해서 바이트를 직접 열어 판단합니다.

호스트 앱이 받아 두는 것은 stdio 서버의 stderr 이고[3], 서버가 스스로 다른 파일에 로그를 쓰는지는 서버마다 달라서 일반 규칙으로 말할 수 없습니다. 설정 파일을 사건 뒤에 고치거나 지우면 등록 흔적이 사라져서, 호스트 앱 로그와 대화 기록의 서버 이름을 설정과 맞춰 빈틈을 찾습니다.

## 직접 분석해 보기

**헥스로 한 번.** 설정 파일이나 할당되지 않은 영역에서 MCP 설정 조각을 찾을 때는 키 문자열 바이트를 씁니다. 아래는 문자 인코딩대로 만든 예시이고, 검체에서 뜬 바이트가 아닙니다.

```
만든 예시(인코딩 명세로 만든 바이트)
"mcpServers"  UTF-8     6D 63 70 53 65 72 76 65 72 73
"mcpServers"  UTF-16LE  6D 00 63 00 70 00 53 00 65 00 72 00 76 00 65 00 72 00 73 00
```

**공개 도구로 한 번.** 수집한 사본에서 jq 로 서버 목록과 넘긴 환경 변수 이름만 뽑고, 값은 출력하지 않습니다. 경로는 만든 예시이고, 원본이 아니라 사본에서만 돌립니다.

```sh
# 만든 예시 경로
CASE=/cases/case-0001/copy/alice
# 서버 이름, 명령, 인자, 원격 주소, 환경 변수 이름(값 제외)
jq '.mcpServers | to_entries[] | {name: .key, command: .value.command, args: .value.args, url: .value.url, env_names: (.value.env // {} | keys)}' "$CASE/.cursor/mcp.json"
# 사본 전체에서 MCP 설정·로그 후보 찾기
rg -l -g '*.json' '"mcpServers"' "$CASE"
find "$CASE" -type d -name 'mcp-logs-*'
```

찾은 로그 폴더는 서버별로 줄 수와 첫·마지막 `timestamp` 를 뽑아 표로 만들고, 설정에 없는 서버 이름이 로그에 있으면 따로 표시합니다.

## 교차 검증

도구 호출이 실제로 무엇을 바꿨는지는 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)의 흐름으로 파일 시스템·git 이력과 맞춰 보고, 설정의 `env` 나 원격 서버 인증 정보가 쟁점이면 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md)로 이어 갑니다. 도구가 가져온 외부 문서가 모델을 조종한 정황은 [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md)에서 다룹니다. 원격 서버와의 통신은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)으로 확인하고, 도구별 흔적은 [Cursor](cursor.md), [Codex CLI](codex-cli.md), [Gemini CLI](gemini-cli.md), [Claude Code](claude-code/index.md) 페이지에서 봅니다.

## 실습

공개 검체에 MCP 흔적이 들어 있는지는 확인하지 못했습니다. 시험용 가상 머신과 시험 계정으로 풀어 봅니다.

1. 로컬 stdio 서버 하나를 설정 파일로 등록하고 도구를 한 번 부른 뒤, 호스트 앱 로그에 연결·호출이 어떻게 남는지 적어 봅니다.
2. 같은 서버를 설정 파일에서 지운 뒤, 로그와 대화 기록에서 그 서버의 흔적이 얼마나 남는지 확인합니다.
3. 원격 서버에 접속하는 설정을 만들고, 기기에 남는 것과 서버 쪽에만 남는 것을 나눠 표로 만듭니다.
4. Cursor 에 `beforeMCPExecution` 훅을 걸어 입력을 파일로 적고, 그 기록과 호스트 앱 로그의 시각을 맞춰 봅니다.

## 참고 문헌

1. Cursor Docs — Hooks — https://cursor.com/docs/agent/hooks
2. Cursor Docs — Model Context Protocol (MCP) — https://cursor.com/docs/context/mcp
3. Model Context Protocol — Debugging — https://modelcontextprotocol.io/docs/tools/debugging
