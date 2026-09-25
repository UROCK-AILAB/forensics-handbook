---
title: "MCP 서버와 도구 호출 기록"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 670
---

# MCP 서버와 도구 호출 기록 (MCP)

MCP(Model Context Protocol)는 AI 앱이 바깥의 도구 서버를 불러 쓰는 규약입니다. 디스크에는 어떤 서버를 붙였는지 적은 설정 파일과 호스트 앱이 받아 둔 서버 로그가 남고, 메모리에는 앱과 서버가 주고받은 JSON-RPC 메시지가 평문으로 남을 수 있습니다.

> 확인 날짜: 2026-09. 규약과 Claude 데스크톱 로그는 MCP 공식 디버깅 문서[3], Cursor 설정은 Cursor 문서[1][2], Codex CLI 설정은 openai/codex 저장소 @406dc92 의 설정 스키마[6], 메모리 흔적은 MCPRecon 논문[4]과 저자 도구 MCPRecon(마지막 커밋 2026-04-12)[5] 기준입니다. 논문은 Ubuntu 24.04 가상 머신에서 Codex CLI 와 VS Code + GitHub Copilot 을 시험했고, 공격 시연은 Cursor 2.4.27 로 했습니다[4]. "관찰" 이라고 적은 것은 Windows 11 PC 한 대에서 본 폴더·키 이름입니다(확인 범위: Windows 11, 2026-09). 앱은 자주 바뀌므로 지금 판과 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

MCP 에서 AI 앱(호스트)은 설정 파일에 적힌 서버를 띄우거나 접속하고, 그 서버가 내놓는 도구를 모델이 부를 수 있게 합니다. 모든 메시지는 JSON-RPC 2.0 형식이고, 한 세션은 보통 도구 목록을 묻는 `tools/list` 로 시작해 도구를 부르는 `tools/call` 과 그 응답으로 이어집니다[4]. 서버는 도구 말고도 리소스(resources)와 프롬프트 틀(prompts)을 내놓을 수 있습니다[4].

서버와 주고받는 방식(전송 방식)은 두 가지입니다. stdio 는 로컬 프로세스로 서버를 띄워 표준 입출력으로 대화하고, Streamable HTTP 는 원격 서버에 접속합니다[3]. Cursor 는 여기에 SSE 도 지원하지만[2], 논문은 SSE 를 MCP 문서가 폐기한 옛 전송 방식이라고 보고 시험에서 뺐습니다[4].

흔적이 남는 곳은 전송 방식에 따라 갈립니다. stdio 서버가 표준 오류(stderr)로 쓴 로그는 호스트 앱이 자동으로 받아 두고, 표준 출력(stdout)은 규약 통신에 쓰기 때문에 여기에 로그를 쓰면 안 됩니다[3]. Streamable HTTP 서버의 stderr 는 클라이언트가 받지 않아서 서버 쪽에서 따로 모으거나 OpenTelemetry 를 써야 합니다[3]. 원격 서버 안에서 도구가 실제로 무엇을 했는지는 그 서버를 운영하는 쪽에 남습니다. 다만 논문은 HTTP 방식에서도 도구 호출 인자와 응답(`result`·`error`·`isError`)을 메모리에서 되살렸습니다(Table 3)[4]. 요청과 응답이 PC 메모리에도 남을 수 있다는 뜻이고, 이 시험에서는 HTTP 서버도 같은 가상 머신 안에서 돌렸습니다[4]. 서버와 기기 중 어디에 무엇이 있는지 가르는 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

규약 안에도 로그 알림 `notifications/message` 가 있지만, 프로토콜 버전 `2026-07-28` 부터 폐기 예정으로 표시되었고 폐기 기간 동안은 남아 있습니다[3]. 로그 수준은 RFC 5424 의 8단계(debug 부터 emergency 까지)를 쓰고, 클라이언트가 요청의 `_meta` 에 `io.modelcontextprotocol/logLevel` 을 넣은 요청에만 서버가 이 알림을 보냅니다[3]. 그래서 규약 로그가 없다고 서버가 아무 일도 하지 않았다고 볼 수 없습니다. 요청마다 `_meta` 에 `io.modelcontextprotocol/protocolVersion` 과 `io.modelcontextprotocol/clientCapabilities` 가 꼭 들어가고, `io.modelcontextprotocol/clientInfo` 는 권장 항목입니다[3].

설정 파일은 자격 증명이 새는 자리이기도 합니다. stdio 서버는 환경 변수를 일부만 물려받아서 설정의 `env` 키로 값을 넘기는데[3], 문서 예시처럼 API 키를 `env` 에 적으면 설정 파일 안에 평문으로 남습니다[3]. 토큰이 남는 곳 전반은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

## 위치와 버전별 차이

MCP 설정과 로그는 호스트 앱마다 따로 둡니다.

| 호스트 앱 | 설정 | 로그·기타 | 근거 |
|---|---|---|---|
| Claude 데스크톱 | `claude_desktop_config.json` 의 `mcpServers` | macOS `~/Library/Logs/Claude`, Windows `%APPDATA%\Claude\logs` 의 `mcp*.log` | 문서[3] |
| Claude 데스크톱(Windows 스토어 앱) | `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude` 아래 `claude_desktop_config.json`, `mcp-user-tool-toggles.json` | 패키지 안 `mcp-logs-<서버 이름>` 폴더의 JSON Lines | 경로[7], 파일 관찰 |
| Claude 데스크톱 Cowork 세션 | 세션 메타 파일 `local_*.json` 의 `remoteMcpServersConfig` | — | [8] |
| Cursor | 전역 `~/.cursor/mcp.json`, 프로젝트 `.cursor/mcp.json` | 출력(Output) 패널의 "MCP Logs" | 문서[2] |
| Codex CLI | `~/.codex/config.toml` 의 `[mcp_servers.<이름>]` | OAuth 토큰: 키링 또는 `CODEX_HOME/.credentials.json` | 스키마[6] |
| Claude Code | [Claude Code](claude-code/index.md) 페이지에서 다룸 | 대화 기록 안의 MCP 서버 상태 | 관찰 |
| Gemini CLI | 관찰한 `~/.gemini/config/mcp_config.json` | — | 관찰 |

Claude 데스크톱 로그에는 서버 연결 이벤트, 설정 문제, 실행 오류, 메시지 교환이 남습니다[3]. Windows 에서 Claude 데스크톱의 사용자 데이터 폴더는 스토어(MSIX) 설치면 `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude`, 스토어 밖 설치나 옛 설치면 `%APPDATA%\Claude` 입니다[7]. claude-forensics 는 Windows 검체에서 `\Users\이름\.claude` 와 `\Users\이름\AppData\Roaming\Claude\` 두 트리를 모두 떠야 한다고 적습니다[8]. 스토어 앱은 `logs` 폴더도 패키지 안으로 옮겨질 수 있어서, 두 위치를 모두 뒤져 `mcp*.log` 를 찾습니다. 관찰한 스토어 앱에서는 아래 경로에 MCP 흔적이 있었습니다(확인 범위: Windows 11, 2026-09).

```
%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\
  LocalCache\Local\claude-cli-nodejs\Cache\<이름>\mcp-logs-<서버 이름>\<파일>.jsonl
  LocalCache\Roaming\Claude\mcp-user-tool-toggles.json
  LocalCache\Roaming\Claude\claude_desktop_config.json
```

같은 PC 에서 `%APPDATA%\Claude\logs\mcp*.log` 는 보이지 않았습니다(확인 범위: Windows 11, 2026-09). 패키지 폴더 구조의 일반 원리는 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)와 [Claude](../chat-services/claude/index.md)에 있습니다.

## 구조

### 설정 파일

Claude 데스크톱과 Cursor 는 둘 다 최상위 `mcpServers` 아래 서버 이름별로 설정을 둡니다[2][3]. Codex CLI 는 TOML 인 `config.toml` 의 `mcp_servers` 표 아래 서버 이름별로 둡니다[6]. 로컬 서버는 띄울 명령과 인자, 환경 변수를 적고, 원격 서버는 주소와 인증 정보를 적습니다.

| 키 | 쓰는 곳 | 뜻 |
|---|---|---|
| `command`, `args`, `env` | Claude 데스크톱[3], Cursor 로컬 서버[2], Codex[6] | 띄울 명령, 인자, 넘길 환경 변수 |
| `envFile` | Cursor 로컬 서버[2] | 환경 변수 파일 |
| `env_vars`, `cwd` | Codex[6] | 물려줄 환경 변수 이름, 작업 폴더 |
| `url`, `headers` | Cursor 원격 서버[2] | 접속 주소, 요청 머리글 |
| `url`, `http_headers`, `env_http_headers`, `bearer_token_env_var` | Codex[6] | 접속 주소, 머리글, 환경 변수에서 읽을 머리글·베어러 토큰 |
| `auth` | Cursor 원격 서버[2] | `CLIENT_ID`, `CLIENT_SECRET`, `scopes` |
| `auth`, `oauth.client_id`, `scopes`, `oauth_resource` | Codex[6] | 인증 방식(`oauth`·`chatgpt`)과 OAuth 설정 |
| `enabled`, `enabled_tools`, `disabled_tools` | Codex[6] | 서버를 켤지, 허용·차단할 도구 목록 |
| `default_tools_approval_mode`, `tools.<도구>.approval_mode` | Codex[6] | 도구 승인 방식(`auto`·`prompt`·`writes`·`approve`) |

Codex 는 MCP OAuth 토큰을 `mcp_oauth_credentials_store` 설정에 따라 둡니다. 기본값 `auto` 는 OS 키링을 쓰고, 키링을 쓸 수 없으면 `CODEX_HOME/.credentials.json` 파일에 둡니다[6]. 이 파일은 같은 사용자로 도는 다른 프로그램도 읽을 수 있다고 스키마에 적혀 있습니다[6]. Cursor 가 원격 서버에 OAuth 로 로그인할 때 쓰는 콜백 주소는 데스크톱이 `http://localhost:8787/callback`, 웹·에이전트가 `https://www.cursor.com/agents/mcp/oauth/callback` 입니다[2]. 토큰이 들어 있는 파일은 보고서에서 값을 가리고, 서비스 쪽 사용 기록은 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 받습니다.

아래는 문서 형식대로 만든 예시이고, 관찰한 값이 아닙니다. `env` 값은 형식을 흉내 내지 않은 자리 표시입니다.

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

`command` 와 `args` 에서는 어떤 프로그램이 어떤 폴더를 대상으로 떴는지, `url` 에서는 어느 원격 서버에 붙도록 설정했는지 알 수 있습니다. 도구가 건드릴 수 있었던 범위를 여기서부터 좁힙니다.

관찰한 스토어 앱의 `claude_desktop_config.json` 에는 `mcpServers` 키가 없었고 `preferences` 와 `coworkUserFilesPath` 만 있었습니다. 같은 폴더의 `mcp-user-tool-toggles.json` 은 `owners`(사전)와 그 아래 목록, `v`(정수)로 되어 있었습니다(확인 범위: Windows 11, 2026-09). 두 파일의 칸 뜻을 설명한 공개 문서가 없어서, 검체에서는 서버를 붙인 뒤와 뗀 뒤의 파일을 시험 기기에서 비교해 해석합니다.

### 호스트 앱이 받은 서버 로그

스토어 앱 패키지의 `mcp-logs-<서버 이름>` 폴더에 있던 JSON Lines 파일은 한 줄의 키가 `cwd`, `debug`, `sessionId`, `timestamp` 였습니다(확인 범위: Windows 11, 2026-09). 폴더 이름에 서버 이름이 들어가서 어느 서버의 로그인지 폴더만 보고 나눌 수 있습니다. `sessionId` 가 어느 세션 기록과 이어지는지는 공개 문서가 없어서, 같은 값이 대화 기록이나 세션 메타 파일에 있는지 검체에서 찾아 맞춥니다.

### 대화 기록·세션 메타·훅에 남는 MCP 흔적

Claude Code 대화 기록 줄에서 `attachment.failedMcpServers`, `attachment.pendingMcpServers` 키를 보았습니다(확인 범위: Windows 11, 2026-09). 대화 기록 구조는 [Claude Code](claude-code/index.md)에서 다룹니다. Claude 데스크톱 Cowork 세션 메타 파일(`local_*.json`)에는 `remoteMcpServersConfig` 칸이 있습니다[8]. 도구 문서에는 칸 이름만 있어서, 그 세션에 붙인 원격 MCP 서버 설정이 어떤 모양으로 들어가는지는 검체에서 열어 봅니다.

Cursor 는 `beforeMCPExecution`, `afterMCPExecution` 훅으로 MCP 호출 전후에 사용자 스크립트를 돌릴 수 있습니다[1]. 조직이 감사 로그를 남겼는지 여기서 확인합니다. 관찰한 PC 의 `~/.cursor/hooks.json` 에도 `beforeMCPExecution` 훅이 있었습니다(확인 범위: Windows 11, 2026-09). 훅 파일 형식은 [Cursor](cursor.md)에 있습니다.

### 메모리에 남는 JSON-RPC 메시지

논문은 MCP 메시지가 클라이언트 프로세스의 힙에 평문 UTF-8 JSON 으로 남는다는 것을 보였습니다[4]. stdio 방식에서 Copilot 은 파이프, Codex 는 소켓으로 서버와 통신했고, HTTP 방식에서는 HTTP 클라이언트 라이브러리와 스트리밍 파서의 버퍼가 더 생긴다고 논문은 적습니다[4]. 논문이 되살린 흔적은 아래와 같습니다(Table 5, Table A.6)[4].

| 무리 | 메모리에 남은 모양 | 알려 주는 것 |
|---|---|---|
| 봉투 | `"jsonrpc":"2.0"`, `"id":4` | MCP 메시지라는 표시, 요청·응답 짝 |
| 메서드 | `"method":"tools/list"`, `"method":"tools/call"`, `"method":"notifications/initialized"` | 도구 목록 조회, 호출, 세션 시작 |
| 도구 목록 | `result.tools[]` 의 `name`, `description`, `inputSchema`, `required` | 모델에게 보인 도구와 입력 형식 |
| 호출 인자 | `"arguments":{...}` | 호출할 때 넘긴 값 |
| 결과 | `result.content[{"type":"text","text":...}]`, `isError`, `error` | 도구 출력, 성공·실패 |
| 기타 | `"result":{"resources":[]}`, `"result":{"resourceTemplates":[]}`, `"_meta":{"progressToken":4}` | 리소스 유무, 호출 묶음·순서 단서 |
| 경계 단서 | JSON 뒤의 널 채움, 붙어 있는 바이너리 | 메시지 끝 찾기 |
| 클라이언트 지시문 | 메모리 안의 긴 지시·정책 문장 | 클라이언트에 내장된 지시 |

시험은 Ubuntu 24.04(커널 6.14) 가상 머신(VMware, 메모리 8GB)에서 했고, 날씨 서버(stdio·HTTP)와 Context7(stdio)을 붙여 도구 목록 조회 한 번과 호출 두 번을 한 뒤 메모리를 떴습니다[4]. 클라이언트 하나씩 돌린 여섯 구성에서는 세 단계가 모두 되살아났습니다(Table 3)[4]. Codex 와 Copilot 을 한 VM 에서 함께 돌리고 메모리를 한 번만 뜬 경우에는 일부 단계가 빠졌습니다(Table 4)[4]. 이 절은 요약이고, 메모리 수집과 분석 절차는 [메모리에서 AI 흔적 찾기](../../03-techniques/analysis/memory-analysis.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 설정 파일에 서버가 있으면 그 호스트 앱에 그 서버를 붙이도록 설정한 기록이 있다는 뜻입니다. `command`·`args`·`url` 로 서버의 정체와 대상 폴더·주소를 알 수 있고, Codex 의 `enabled_tools`·`default_tools_approval_mode` 로 어떤 도구를 승인 없이 쓰도록 했는지도 알 수 있습니다[6]. 호스트 앱이 받은 로그에 연결·오류·메시지 교환이 있으면 "이 시각에 이 서버가 떠서 호스트와 통신한 기록이 있다" 고 쓸 수 있습니다. 메모리에서 `tools/call` 요청과 같은 `id` 의 응답을 짝지었으면 "이 도구를 이 인자로 불렀고 이런 결과를 받은 기록이 메모리에 있다" 고 쓸 수 있습니다[4]. Cursor 는 기본으로 MCP 도구를 쓰기 전에 승인을 묻고[2], 감사 훅이나 대화 기록에 승인 흔적이 있으면 사람이 허락했는지 판단할 수 있습니다.

**증명하지 못하는 것.** 설정에 없다고 MCP 서버를 쓰지 않았다고 말할 수 없습니다. Cursor 확장 프로그램이 `vscode.cursor.mcp.registerServer()` 로 서버를 등록하면 설정 파일에 남지 않기 때문입니다[2]. Cursor 는 Run Mode 설정에 따라 허용 목록에 있는 도구를 묻지 않고 바로 실행하므로[2], 승인 흔적이 없다고 도구가 실행되지 않았다고 볼 수도 없습니다. 메모리에 흔적이 없어도 호출이 없었다는 뜻이 아니고, 버퍼를 덮어써서 사라졌을 수 있습니다[4]. 원격 서버가 호출을 받아 서버 안에서 무엇을 했는지는 기기 쪽 자료로 알 수 없고 서버 운영 쪽 자료가 필요합니다. 설정 파일에 적힌 API 키는 그 키가 있었다는 사실만 보여 주고, 누가 그 키를 썼는지는 서비스 쪽 기록으로 확인합니다.

## 시각 해석

MCP 는 메시지에 시각을 넣으라고 정하지 않습니다[4]. 메모리에서 되살린 메시지는 `id` 와 메모리 위치로 순서를 추정할 뿐이고, JSON-RPC 규격이 `id` 를 차례대로 매기라고 정하지 않아서 `id` 순서를 시간 순서로 단정할 수 없습니다[4]. 메모리 흔적의 시각은 메모리를 뜬 시각과, 같은 호출을 적은 디스크 쪽 기록(호스트 앱 로그, 대화 기록)에서 가져옵니다.

관찰한 JSON Lines 로그에는 `timestamp` 칸이 있었습니다(확인 범위: Windows 11, 2026-09). 형식과 시간대를 설명한 공개 문서가 없어서, 검체에서 몇 줄을 열어 끝에 `Z` 나 `+09:00` 같은 시간대 표시가 있는지 먼저 봅니다. `mcp*.log` 도 같은 방법으로 확인합니다. 설정 파일에는 시각 칸이 없어서, 서버를 언제 등록했는지는 파일 수정 시각이나 백업·볼륨 섀도 사본의 이전 판을 비교해 좁힙니다. 여러 출처를 한 줄로 맞추는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

MCP 설정은 호스트 앱마다, 그리고 전역·프로젝트 범위마다 흩어집니다. 한 앱의 설정만 보고 "MCP 를 쓰지 않았다" 고 쓰기 쉬우므로, 설치된 AI 도구 목록부터 만들고 도구별로 전역 설정과 저장소 안의 프로젝트 설정을 모두 모읍니다. 관찰한 `~/.gemini/config/mcp_config.json` 은 JSON 으로 읽히지 않았습니다(확인 범위: Windows 11, 2026-09). 이런 파일은 바이트를 직접 열어 빈 파일인지 다른 형식인지 판단합니다.

호스트 앱이 받아 두는 것은 stdio 서버의 stderr 이고[3], 서버가 스스로 다른 파일에 로그를 쓰는지는 서버마다 다릅니다. 설정 파일을 사건 뒤에 고치거나 지우면 등록 흔적이 사라지므로, 호스트 앱 로그·대화 기록·세션 메타의 서버 이름을 설정과 맞춰 빈틈을 찾습니다. 논문도 설정을 바꾸고 흔적을 지우는 로컬 공격자를 위협 모델에 넣고, 이때 메모리가 디스크와 별개인 증거원이 된다고 봅니다[4].

메모리 흔적에는 한계가 따로 있습니다. 논문의 시험은 Linux 에서만 했고, Windows·macOS 클라이언트에서 같은 결과가 나오는지는 검체로 확인해야 합니다[4]. 앞으로 MCP 구현이 메시지를 평문으로 메모리에 두지 않으면 되살리기 어려워집니다[4]. 메모리에는 MCP 와 상관없는 JSON 조각도 많습니다. 증거로 쓰려면 method, `id`, 도구 이름, 인자, 응답, `inputSchema` 가 서로 맞아야 하고, 인자가 도구의 `inputSchema` 와 어긋나거나 짝이 없는 조각은 혼자서 근거로 쓰지 않습니다[4].

논문의 공격 시연(Cursor 2.4.27)에서는 악성 날씨 서버가 `get_current_weather` 도구의 네 번째 응답에 지시문을 끼워 넣었습니다[4]. 지시문은 작업 폴더에서 `mcp.json` 을 찾아 그 내용을 다음 도구 호출의 인자에 실으라는 것이었습니다[4]. Composer 1 과 Gemini 3 Flash 는 지시를 따랐고, GPT 5.2 Low 와 Sonnet 4.5 는 거부했습니다[4]. 추가로 부른 도구를 논문 8.2절은 `get_weather_forecast`, 8.3절은 `get_current_weather` 로 다르게 적고, 8.3절은 사용자 데이터가 `country` 인자에 실려 나갔다고 적습니다[4]. 사용자 화면에 드러난 것은 "Listed test Read mcp.json" 한 줄과 조금 바뀐 도구 호출뿐이었고, 나머지는 접힌 생각(Thinking) 블록과 입력·응답 블록을 펼쳐야 보였습니다[4]. MCPRecon 은 빼낸 내용이 든 요청은 되살렸지만, 지시문이 든 응답은 이미 덮어써져 메모리에 없었습니다[4]. 논문 안에서도 공격이 먹힌 모델을 초록은 "Composer 1 and Gemini 3 Flash", 기여 목록은 "Gemini 3 Flash and Cursor 1" 로 다르게 적습니다[4]. 인젝션 사고 전반은 [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md)에서 다룹니다.

## 직접 분석해 보기

**헥스로 한 번.** 설정 파일, 할당되지 않은 영역, 메모리 덤프에서 MCP 조각을 찾을 때는 키 문자열 바이트를 씁니다. 아래는 문자 인코딩대로 만든 예시이고, 검체에서 뜬 바이트가 아닙니다.

```
만든 예시(인코딩 명세로 만든 바이트)
"mcpServers"       UTF-8     6D 63 70 53 65 72 76 65 72 73
"mcpServers"       UTF-16LE  6D 00 63 00 70 00 53 00 65 00 72 00 76 00 65 00 72 00 73 00
"jsonrpc":"2.0"    UTF-8     22 6A 73 6F 6E 72 70 63 22 3A 22 32 2E 30 22
```

메모리에서 `"jsonrpc":"2.0"` 을 찾으면 앞뒤로 중괄호 짝을 맞춰 JSON 하나를 떼어 냅니다. 뒤에 이어지는 널 바이트(`00`)는 메시지 끝을 찾는 단서가 됩니다[4]. 아래는 논문의 칸 모양대로 만든 예시 요청이고, 값은 모두 지어낸 것입니다.

```json
{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"get_current_weather","arguments":{"city_name":"Exampleville","country":"XX"}}}
```

**공개 도구로 한 번.** 수집한 사본에서 jq 로 서버 목록과 넘긴 환경 변수 이름만 뽑고, 값은 출력하지 않습니다. 경로는 만든 예시이고, 원본이 아니라 사본에서만 돌립니다.

```sh
# 만든 예시 경로
CASE=/cases/case-0001/copy/alice
# 서버 이름, 명령, 인자, 원격 주소, 환경 변수 이름(값 제외)
jq '.mcpServers | to_entries[] | {name: .key, command: .value.command, args: .value.args, url: .value.url, env_names: (.value.env // {} | keys)}' "$CASE/.cursor/mcp.json"
# 사본 전체에서 MCP 설정·로그 후보 찾기
rg -l -g '*.json' '"mcpServers"' "$CASE"
rg -l -g '*.toml' '^\[mcp_servers\.' "$CASE"
find "$CASE" -type d -name 'mcp-logs-*'
```

찾은 로그 폴더는 서버별로 줄 수와 첫·마지막 `timestamp` 를 뽑아 표로 만들고, 설정에 없는 서버 이름이 로그에 있으면 따로 표시합니다.

메모리 이미지는 MCPRecon 으로 봅니다[5]. 파이썬 표준 라이브러리만 쓰고, 기준 문자열(`jsonrpc`, `tools/list`, `tools/call`) 둘레에서 JSON 을 떼어 내 JSON 형식 → JSON-RPC 구조 → MCP 메서드(`tools/`·`resources/`·`prompts/`·`notifications/`) 순서로 거른 뒤, `id` 로 요청과 응답을 짝짓습니다[4][5].

```sh
# 만든 예시 파일 이름. 메모리 이미지 사본에서만 돌린다
python3 mcprecon.py case-0001.vmem --keywords jsonrpc tools/list tools/call --mcp-only > case-0001-mcp.jsonl
```

출력은 한 줄에 JSON 하나이고, 칸은 `offset`, `session`, `type`(request·response·notification·unknown), `id`, `method`, `tool`, `confidence`, `mcp`, `json` 입니다. `--emit-raw` 를 주면 원문 `raw` 가 붙습니다[5]. `--tools-only` 는 `tools/call` 요청과 짝지은 응답만 남기고, `--client {codex,cursor,copilot,auto,other}` 와 `--vol3`(Volatility3 `linux.pslist` 자동 실행)으로 프로세스별로 나눌 수 있습니다[5]. JSON 짝이 안 맞으면 `--window`(기본 16KB)를 늘립니다[5]. 도구 README 가 밝힌 시험 환경은 Linux 의 Python 3.10 입니다[5]. 보고서에는 `offset` 을 함께 적고, `xxd` 로 그 위치에 같은 JSON 이 있는지 한 번 더 확인합니다[4].

## 교차 검증

도구 호출이 실제로 무엇을 바꿨는지는 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)의 흐름으로 파일 시스템·git 이력과 맞춰 봅니다. 설정의 `env`, 원격 서버 인증 정보, Codex 의 `.credentials.json` 이 쟁점이면 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md)로 이어 갑니다. 원격 서버와의 통신은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)으로 확인하고, 메모리 흔적은 [메모리에서 AI 흔적 찾기](../../03-techniques/analysis/memory-analysis.md)의 절차로 수집합니다. 도구별 흔적은 [Cursor](cursor.md), [Codex CLI](codex-cli.md), [Gemini CLI](gemini-cli.md), [GitHub Copilot](github-copilot/index.md), [Claude Code](claude-code/index.md) 페이지에서 봅니다.

## 실습

MCPRecon README 는 시험용 메모리 스냅숏(`*.vmem`, `sample.vmem`)을 저장소에 함께 둔다고 적고, Google Drive 내려받기 주소도 안내합니다[5]. 저장소 파일 목록에 스냅숏이 없으면 이 주소에서 받습니다. 이 스냅숏으로 1~2번을 풀고, 나머지는 시험용 가상 머신과 시험 계정으로 풀어 봅니다.

1. 시험용 스냅숏에서 `tools/list` 응답을 찾아, 모델에게 보인 도구 이름과 `required` 칸을 표로 만듭니다.
2. 같은 스냅숏에서 `tools/call` 요청과 같은 `id` 의 응답을 짝짓고, 짝이 없는 조각이 몇 개인지 셉니다.
3. 로컬 stdio 서버 하나를 설정 파일로 등록하고 도구를 한 번 부른 뒤, 호스트 앱 로그에 연결·호출이 어떻게 남는지 적습니다. 그 뒤 설정에서 서버를 지우고, 로그와 대화 기록에 그 서버의 흔적이 얼마나 남는지 확인합니다.
4. 원격 서버에 접속하는 설정을 만들고 도구를 부른 뒤 메모리를 뜹니다. 기기 디스크, 기기 메모리, 서버 쪽에 각각 무엇이 남는지 나눠 표로 만듭니다.
5. Cursor 에 `beforeMCPExecution` 훅을 걸어 입력을 파일로 적고, 그 기록과 호스트 앱 로그의 시각을 맞춰 봅니다.

## 참고 문헌

1. Cursor Docs — Hooks — https://cursor.com/docs/agent/hooks
2. Cursor Docs — Model Context Protocol (MCP) — https://cursor.com/docs/context/mcp
3. Model Context Protocol — Debugging — https://modelcontextprotocol.io/docs/tools/debugging
4. A. Satter, M. Salmon, L. Muhanna, T. T. Spinosa, T. Gharaibeh, I. Baggili, "With or Without Logs: Memory Forensic Reconstruction of Model Context Protocol (MCP) Activity in Agentic LLM Systems", 논문 원고, Louisiana State University BiT Lab, 2026. 도구와 시험 자료는 [5].
5. BiTLab-BaggiliTruthLab/MCPRecon — https://github.com/BiTLab-BaggiliTruthLab/MCPRecon — `README.md`, `tool/mcprecon.py`, 파일 목록(마지막 커밋 2026-04-12)
6. openai/codex @406dc92 — https://github.com/openai/codex — `codex-rs/core/config.schema.json` (`mcp_servers`, `RawMcpServerConfig`, `mcp_oauth_credentials_store`, `OAuthCredentialsStoreMode`)
7. kenn-io/agentsview — https://github.com/kenn-io/agentsview — `internal/parser/cowork_paths.go`
8. forensicdave/claude-forensics v0.1.1 (2026-06-16) — https://github.com/forensicdave/claude-forensics — `README.md`, `docs/claude_forensics.md`
