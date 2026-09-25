---
title: "프롬프트 인젝션 사고 분석"
parent: "기법 · 분석"
nav_order: 900
---

# 프롬프트 인젝션 사고 분석 (Prompt Injection)

AI 에이전트가 읽은 웹 페이지·파일·도구 출력 속에 섞인 글을 지시처럼 따라 사용자가 시키지 않은 일을 했다는 의심이 있을 때, 에이전트가 무엇을 읽었고 그 뒤 무엇을 했으며 누가 그 동작을 허용했는지를 기록으로 이어 보는 분석 방법입니다.

이 페이지는 사고가 난 뒤 흔적을 해석하고 재발을 탐지하는 방법만 다루고, 지시를 숨겨 넣는 방법이나 문구는 쓰지 않습니다.

## 언제 쓰나

에이전트가 사용자가 요청하지 않은 명령을 실행했거나, 작업과 상관없는 파일을 읽었거나, 비밀 값이 밖으로 나간 흔적이 있을 때 씁니다. 저장소를 열자마자 모르는 명령이 돈 경우, 에이전트가 웹 페이지를 요약하다가 다른 사이트에 접속한 경우, 대화가 끝난 뒤에도 이상한 지시가 계속 따라붙는 경우가 여기에 들어갑니다. 위키백과는 2025년 10월 LayerX Security 가 ChatGPT Atlas 의 메모리에 넣은 지시가 세션과 기기를 넘어 남는 문제를 보고했다고 적고 있어, 대화 밖에 저장되는 메모리와 설정도 조사 대상에 넣습니다. 에이전트 동작 전반을 따라가는 흐름은 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)에 있고, 이 페이지는 "읽은 것" 과 "한 것" 을 잇는 부분에 집중합니다.

## 절차

### 1. 에이전트가 어디서 돌았는지 가립니다

에이전트가 도는 곳에 따라 기록이 있는 곳이 다릅니다. Claude Code, Codex CLI, Gemini CLI, Cursor 처럼 사용자 PC 에서 도는 에이전트는 대화와 도구 실행 기록이 기기에 남습니다. 사용자의 실제 브라우저를 조작하는 에이전트(Claude in Chrome 확장 등)는 사람이 한 방문과 에이전트가 한 방문이 같은 브라우저 프로필에 섞입니다. 웹에서 돌린 Claude Code 클라우드 세션처럼 서비스 쪽 가상 머신에서 도는 에이전트는 기록 원본이 서버에 있어서, 기기에서는 브라우저 방문 기록 같은 접속 흔적부터 확인하고 원본은 서비스 쪽에 요청합니다. 원격 MCP 서버(Streamable HTTP)의 로그도 PC 가 아니라 그 서버 쪽에 있습니다. 갈래별 흔적은 [브라우저를 조작하는 AI](../../02-artifacts/agentic-services/browser-agents.md)와 [ChatGPT 에이전트 모드](../../02-artifacts/agentic-services/chatgpt-agent.md)에 있습니다.

### 2. 문제의 동작을 기록에서 먼저 찾습니다

거꾸로 따라가려면 출발점이 있어야 해서, 문제가 된 명령이나 파일 접근을 도구 기록에서 먼저 찾아 고정합니다. Claude Code 는 `~/.claude/projects/<프로젝트>/<세션>.jsonl` 에 모든 메시지, 도구 호출, 도구 결과를 담습니다. 관찰한 기록에서는 도구 호출이 `message.content[]` 의 `name`·`input`·`id` 로, 결과가 `tool_use_id`·`content`·`is_error` 와 `toolUseResult.stdout`·`stderr`·`success` 로 남습니다. 큰 도구 출력은 `.../<세션>/tool-results/` 에, 하위 에이전트 대화는 `.../<세션>/subagents/` 에 따로 쌓여서 이 폴더들도 함께 봅니다. Cursor 는 조직이 훅으로 기록을 남겼다면 훅 입력의 `tool_name`·`tool_input`·`tool_output`·`command` 가 단서가 되고, Codex CLI 는 OpenTelemetry 수집을 켠 조직이라면 `codex.tool_result` 이벤트가 수집 서버에 있습니다. 기록 구조는 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md), [Cursor](../../02-artifacts/dev-agents/cursor.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md) 페이지에 있습니다.

### 3. 그 동작 앞에서 에이전트가 읽은 입력을 찾습니다

문제의 줄에서 `parentUuid` 를 따라 앞 줄로 거슬러 올라가며, 그 동작 직전에 들어온 도구 결과를 찾습니다. 웹 페이지를 가져온 결과, 파일을 읽은 결과, MCP 서버가 돌려준 결과, 명령 출력이 모두 후보이고, Claude Code 문서는 도구를 거친 파일 내용과 명령 출력, 붙여 넣은 글이 모두 디스크의 대화 기록에 쓰인다고 적습니다. 모델 응답 줄의 `message.usage.server_tool_use.web_fetch_requests`·`web_search_requests` 에는 웹 가져오기·검색 횟수가 남아서, 그 턴에 외부 웹 내용이 들어왔는지 가늠하는 데 씁니다.

지시가 섞였던 입력을 찾으면 보고서에는 그 입력의 위치(URL, 파일 경로, MCP 서버 이름), 에이전트가 읽은 시각, 기록에 남은 해당 부분의 해시를 적고, 원문은 증거 부록에 필요한 만큼만 옮깁니다. 웹 페이지는 지금 다시 열면 내용이 바뀌었을 수 있어서, 판단의 근거는 다시 받은 페이지가 아니라 대화 기록에 남은 도구 결과로 삼습니다.

### 4. 사용자가 시킨 일인지 가립니다

같은 동작이라도 사용자가 입력으로 시켰는지, 도구 결과에만 있던 요청을 에이전트가 따랐는지에 따라 사건의 성격이 달라집니다. 사용자가 직접 입력한 프롬프트는 `~/.claude/history.jsonl` 의 `display` 칸에 시각·프로젝트 경로와 함께 남아서, 문제의 동작 앞에 그런 요청이 있었는지 비교합니다. 세션 기록 줄에는 `promptSource`, `origin.kind`, `userType`, `entrypoint`, `isMeta` 키도 있습니다. 입력의 출처와 관련 있어 보이는 것은 키 이름에서 짐작한 것이라서, 값의 뜻은 같은 세션의 `history.jsonl` 입력과 줄마다 맞춰 보고 판단합니다.

다음으로 그 동작을 누가 허용했는지 봅니다. 세션 기록에는 줄마다 `permissionMode` 키가 있고, 문서가 밝힌 권한 모드는 `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` 입니다. 사용자가 "다시 묻지 않기" 로 영구 허용한 Bash 명령과 WebFetch 도메인은 `.claude/settings.local.json` 에 allow 규칙으로 저장되고, 사용자 설정의 `permissions.allow` 에도 허용 목록이 있습니다. Claude 데스크톱 스토어 앱의 `claude_desktop_config.json` 에는 계정별 `preferences.bypassPermissionsGateByAccount`·`bypassPermissionsOptInByAccount` 키가 있습니다. 조직이 Claude Code OpenTelemetry 를 켜 두었다면 `claude_code.tool_decision` 이벤트의 `source` 값(`config`, `hook`, `user_permanent`, `user_temporary`, `user_abort`, `user_reject`)으로 설정이 허용했는지 사람이 그 자리에서 허용했는지를 바로 가릅니다. Codex CLI 는 설정의 `sandbox_mode`·`approval_policy` 가 당시 허용 범위를 알려 주고, OpenTelemetry 를 켰다면 `codex.tool_decision` 이벤트가 승인·거부 결과를 남깁니다. 권한 설정의 우선순위와 파일 위치는 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) 페이지에 있습니다.

### 5. 계속 남는 지시와 설정을 찾습니다

한 번 읽힌 입력은 그 세션에서 끝나지만, 설정 파일이나 메모리에 들어간 내용은 다음 세션에도 다시 읽힙니다. 확인할 곳은 아래와 같고, 각 파일의 변경 시각을 사건 시각과 나란히 [AI 사용 타임라인](timeline.md)에 올립니다.

| 위치 | 확인할 것 |
|---|---|
| 저장소 안 `.claude/settings.json`, `.claude/settings.local.json` | 훅(`hooks.*`)과 허용 규칙. 저장소에 커밋된 훅은 그 저장소를 연 사람의 PC 에서 명령을 실행하고, 프로젝트 훅은 작업 폴더 신뢰 대화상자를 통과한 뒤에 돕니다 |
| 저장소 안 `.cursor/hooks.json`, `.cursor/mcp.json` | 프로젝트 범위 훅과 MCP 서버 등록 |
| `~/.claude/settings.json`, `~/.cursor/hooks.json`, Gemini CLI `settings.json` 의 `hooks.*` | 사용자 범위 훅 |
| `~/.claude.json`(MCP 서버 설정), `claude_desktop_config.json` 의 `mcpServers`, `~/.cursor/mcp.json` | 등록된 MCP 서버와 실행 명령·인자·환경 변수 |
| `~/.claude/projects/<프로젝트>/memory/` | 프로젝트별 자동 메모. 날짜 기준 자동 삭제에서 빠집니다 |
| 서비스 계정의 메모리 기능 | 서버에 있으니 계정 내보내기나 사업자 요청으로 확인 |

Claude Code 훅은 시작 때 고정되지 않고 설정 파일을 고치면 바로 반영되어서, 지금 보이는 훅 설정이 사고 당시와 같다고 보면 안 됩니다. 세션 기록의 `hookInfos[].command`, `attachment.hookEvent`, `attachment.hookName`, `attachment.exitCode` 키에는 실제로 돈 훅이 남으니, 설정 파일보다 이 기록을 먼저 봅니다. Cursor 확장이 `vscode.cursor.mcp.registerServer()` 로 등록한 MCP 서버는 설정 파일에 남지 않아서, `mcp.json` 에 없다고 그 서버를 쓰지 않았다고 단정하지 않습니다. MCP 설정의 구조는 [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md)에 있습니다.

### 6. 밖으로 나간 것을 확인합니다

지시를 따른 결과가 외부 전송이나 비밀 값 노출이라면 나간 경로를 찾습니다. 로컬 stdio 방식 MCP 서버가 stderr 로 쓴 로그는 호스트 앱이 받아 두고, Claude Desktop 은 이 로그를 macOS `~/Library/Logs/Claude`, Windows `%APPDATA%\Claude\logs` 의 `mcp*.log` 에 남기며 서버 연결, 실행 오류, 주고받은 메시지를 담는다고 MCP 문서가 적습니다. Windows 스토어 앱은 앱 폴더가 `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude` 에 있어서[agentsview], `logs` 폴더를 이 아래에서도 찾아봅니다. 같은 패키지 폴더의 `LocalCache\Local\claude-cli-nodejs\Cache\` 아래 `mcp-logs-<서버 이름>` 폴더에도 JSONL 로그(줄 키 `cwd`·`debug`·`sessionId`·`timestamp`)가 생깁니다. 세션 기록의 `attachment.failedMcpServers`·`pendingMcpServers` 키는 이름으로 보아 MCP 서버 연결 실패·대기를 담는 것으로 짐작되니, 값은 위 로그와 맞춰 보고 판단합니다.

디스크 로그가 없으면 메모리가 남은 경로입니다. Satter 외(DFRWS USA 2026)는 Cursor 2.4.27 을 클라이언트로 두고, 날씨 도구 `get_current_weather` 를 네 번째 부를 때 응답에 키를 하나 더 붙여 지시문을 넣는 로컬 MCP 서버로 시험했습니다[논문 §8]. Composer 1 과 Gemini 3 Flash 는 지시를 따라 작업 공간의 `mcp.json` 내용을 날씨 도구를 다시 부르는 호출의 `country` 인자에 실어 보냈고, GPT 5.2 Low 와 Sonnet 4.5 는 거부했지만 거부 사실을 접힌 Thinking 안에만 적었습니다. 사용자 화면에는 "Listed test Read mcp.json" 한 줄과 다시 부른 도구 호출만 보였습니다. 논문의 MCPRecon 은 메모리에서 빠져나간 내용이 든 요청(메모리 오프셋, 도구 이름, 인자)을 되살렸지만, 지시문이 든 응답은 이미 덮어써져 되살리지 못했습니다. 그래서 도구 인자에 작업과 상관없는 파일 내용이 들어 있으면 그 자체를 유출의 근거로 삼고, 지시문이 든 응답이 메모리에 없다고 주입이 없었다고 보지 않습니다. 시험은 Ubuntu 24.04 가상 머신에서 했고, MCP 메시지에는 시각 칸이 없어서 순서는 `id` 와 메모리 위치로 짐작할 뿐입니다. 논문 안에서도 모델 이름(초록은 "Composer 1 and Gemini 3 Flash", 기여 목록은 "Gemini 3 Flash and Cursor 1")과 다시 부른 도구 이름(`get_weather_forecast`·`get_current_weather`)이 서로 다르게 적혀 있습니다. 메모리 수집과 분석은 [메모리에서 AI 흔적 찾기](memory-analysis.md)와 [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md)에 있습니다.

브라우저를 조작하는 에이전트라면 사용자 브라우저 프로필의 방문 기록과 다운로드를 봅니다. Claude Code 를 Chrome 과 연결하면 에이전트가 연 탭을 세션에 묶인 탭 그룹으로 모으고, 확장과의 중계에 `bridge.claudeusercontent.com` 을 쓰며, GIF 녹화나 스크린샷 파일을 남길 수 있어서 에이전트가 본 화면을 되짚는 자료가 됩니다. 네트워크 쪽은 Sysmon 이벤트 ID 22(DNS 질의)와 3(연결, 기본으로 꺼짐)이 프로세스별로 시각을 UTC 로 남깁니다([AI 서비스 도메인과 네트워크 기록](../../02-artifacts/network-enterprise/network-traces.md)).

비밀 값은 대화 기록 자체에도 남습니다. Claude Code 문서는 도구가 `.env` 파일을 읽거나 명령이 자격 증명을 출력하면 그 값이 대화 기록에 그대로 쓰인다고 적어서, 기록에서 노출된 값의 종류를 확인하고 해당 키를 폐기·교체할 대상으로 넘깁니다. 이 판단은 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md)에서 이어 갑니다.

### 7. 조직 서버 기록을 요청합니다

Microsoft 365 Copilot 같은 조직용 서비스는 사용자 PC 가 아니라 테넌트 쪽에 기록이 있습니다. Purview 감사 기록의 `AccessedResources` 에는 Copilot 이 읽은 파일·메일·메시지와 함께 `XPIADetected` 칸이 있고, `Messages` 에는 `JailbreakDetected` 칸이 있습니다. 두 칸은 서비스가 내린 판정 표시라서 그대로 결론으로 쓰지 않고, 에이전트가 읽은 자원 목록과 나란히 놓고 봅니다. 감사 기록에는 프롬프트·응답 본문이 없고 메시지 ID 만 있어서, 본문은 보존 정책이 켜져 있을 때 eDiscovery 로 찾습니다. 자세한 내용은 [Microsoft Purview로 본 Copilot 기록](../../02-artifacts/network-enterprise/purview-copilot.md)에 있습니다.

### 8. 재발을 탐지할 기록을 겁니다

조사가 끝나면 같은 일이 다시 일어났을 때 남을 기록을 정합니다. Cursor 훅은 `beforeReadFile`, `beforeShellExecution`, `beforeMCPExecution`, `afterAgentResponse` 같은 이벤트에서 파일 경로와 명령, 도구 입력을 받아 기록하거나 막을 수 있고, 종료 코드 2 는 차단, 0 은 성공이며 그 밖의 값은 기본으로 통과(fail open)입니다. Claude Code 훅도 `PreToolUse`, `UserPromptSubmit` 등에서 종료 코드 2 로 동작을 막고, 관리 정책의 `allowManagedHooksOnly` 로 관리 훅만 허용할 수 있습니다. OpenTelemetry 로 도구 결정과 결과를 조직 수집기로 보내면 PC 의 기록이 지워져도 사본이 남는데, 프롬프트·응답·도구 인자는 기본으로 가려지니 조직 정책에 맞춰 켤 항목을 정합니다.

악성 코드 쪽 지표도 함께 봅니다. Google 위협 인텔리전스 그룹(GTIG)은 2025년 11월 보고서에서 기기에 깔린 AI CLI 도구에 프롬프트를 넣어 비밀 값을 더 찾는 자격 증명 탈취 코드(QUIETVAULT)와, LLM 기반 보안 분석을 피하려는 문구를 코드 안에 넣은 리버스 셸(FRUITSHELL)을 보고했습니다. 보고서 내용을 바탕으로 이 핸드북이 짐작한 탐지 지표는 표본 안의 자연어 프롬프트 문자열, AI API 로 나가는 연결, 평소와 다른 부모 프로세스가 AI CLI 를 실행하는 행위입니다. 보안 분석에 LLM 을 쓰는 조직이라면 분석 대상 파일 안의 문구가 분석 결과를 흔들 수 있다는 점도 탐지 설계에 넣습니다.

## 도구

JSONL 기록은 `jq` 로 필요한 줄만 골라 읽습니다. 아래는 관찰로 확인한 키 이름만 써서 도구 호출과 결과를 시각 순으로 뽑는 예시이고, 결과에는 비밀 값이 섞일 수 있어 증거와 같은 수준으로 다룹니다.

```bash
jq -c 'select(.message.content | type == "array") | {timestamp, uuid, parentUuid, permissionMode, calls: [.message.content[] | select(.name != null) | {name, id}], results: [.message.content[] | select(.tool_use_id != null) | {tool_use_id, is_error}]}' session.jsonl
```

설정 파일(JSON·TOML)은 편집기로 읽되 수정 시각을 먼저 적어 두고, 저장소 안 설정은 git 기록으로 언제 누가 넣었는지 확인합니다. 네트워크와 프로세스 기록은 조직이 쓰는 EDR·Sysmon 수집 도구로 봅니다.

## 함정과 한계

대화 기록은 무결성 보호가 없습니다. Claude Code 문서는 대화 기록과 입력 기록을 저장할 때 암호화하지 않고 OS 파일 권한이 유일한 보호라고 적어서, 같은 계정의 프로그램이나 사람이 고칠 수 있습니다. 조직 수집기나 서버 쪽 기록이 있으면 대조해 두고, 없으면 그 한계를 보고서에 적습니다.

기록이 없는 까닭이 여럿입니다. `cleanupPeriodDays` 가 지난 세션은 지워지고, `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켜면 처음부터 기록하지 않으며, 클라우드 세션이나 서버에서 도는 에이전트는 기기에 기록이 없습니다. `~/.codex` 처럼 설정과 스킬 파일만 있고 기록이 없는 폴더도 있어서, 폴더가 있다고 그 도구로 사고가 났다고 보지 않습니다.

편집 되돌리기 사본은 일부만 잡습니다. Claude Code 체크포인트는 Claude 의 편집 도구로 바꾼 파일만 추적하고, Bash 명령으로 지우거나 옮긴 파일과 대부분의 하위 에이전트 편집은 잡지 않아서, 사본이 없는 변경은 명령 기록과 파일 시스템 흔적으로 따로 확인합니다.

모델이 왜 그렇게 했는지는 기록이 직접 말해 주지 않습니다. 세션 기록에 `message.content[].thinking` 칸이 있지만 모델이 만든 글이라서 원인의 증명으로 쓰지 않고, "이 입력을 읽은 다음 이 동작이 있었다" 는 순서와 권한 기록으로 판단합니다.

## 결과를 어떻게 해석하나

기록으로는 입력과 동작의 순서, 그리고 그 동작을 허용한 설정이나 사람을 알 수 있습니다. 에이전트가 어떤 입력을 읽은 직후 문제의 동작을 했고, 사용자 입력 기록에는 그런 요청이 없으며, 권한 기록이 사람의 그 자리 승인 없이 설정으로 허용되었음을 보이면 "도구 결과에 들어온 내용을 따른 것으로 보인다" 고 쓸 수 있습니다. 그 입력을 누가 왜 넣었는지는 입력이 있던 곳(웹 사이트, 저장소, MCP 서버)의 기록으로 따로 밝혀야 하고, 에이전트 쪽 기록만으로는 증명하지 못합니다.

보고서 문장은 다음처럼 씁니다(만든 예시).

- 좋은 예: "2026-09-12 07:41:10(UTC)에 세션 `9c1e5a20-...` 의 기록에 `https://docs.example.org/setup` 을 가져온 도구 결과가 있고, 같은 턴의 다음 도구 호출(07:41:18)에서 `C:\work\demo-app\.env` 를 읽는 명령이 실행되었습니다. `history.jsonl` 의 같은 세션 입력에는 이 파일을 읽으라는 요청이 없고, 해당 줄의 `permissionMode` 값과 프로젝트의 `.claude/settings.local.json` 허용 규칙은 부록에 적었습니다."
- 피할 예: "공격자가 프롬프트 인젝션으로 AI 를 조종해 비밀번호를 훔쳤다."

보고서 전체의 틀은 [AI 관련 포렌식 보고서](../reporting/forensic-report.md)를 따릅니다.

## 참고 문헌

- Claude Code Docs — Explore the .claude directory. https://code.claude.com/docs/en/claude-directory
- Claude Code Docs — Hooks reference. https://code.claude.com/docs/en/hooks
- Claude Code Docs — Configure permissions. https://code.claude.com/docs/en/permissions
- Claude Code Docs — Settings files and precedence. https://code.claude.com/docs/en/settings
- Claude Code Docs — Monitoring (OpenTelemetry). https://code.claude.com/docs/en/monitoring-usage
- Claude Code Docs — Checkpointing. https://code.claude.com/docs/en/checkpointing
- Claude Code Docs — Use Claude Code with Chrome. https://code.claude.com/docs/en/chrome
- OpenAI Codex — Advanced configuration. https://learn.chatgpt.com/docs/config-file/config-advanced
- Cursor Docs — Hooks. https://cursor.com/docs/agent/hooks
- Cursor Docs — Model Context Protocol (MCP). https://cursor.com/docs/context/mcp
- Model Context Protocol — Debugging. https://modelcontextprotocol.io/docs/tools/debugging
- Microsoft Learn — Audit logs for Copilot and AI applications. https://learn.microsoft.com/en-us/purview/audit-copilot
- Microsoft Learn — Sysmon. https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
- Google Cloud Blog (GTIG), "GTIG AI Threat Tracker: Advances in Threat Actor Usage of AI Tools" (2025-11-06). https://cloud.google.com/blog/topics/threat-intelligence/threat-actor-usage-of-ai-tools
- Wikipedia — ChatGPT Atlas. https://en.wikipedia.org/wiki/ChatGPT_Atlas
- [논문] A. Satter, M. Salmon, L. Muhanna, T. T. Spinosa, T. Gharaibeh, I. Baggili, "With or Without Logs: Memory Forensic Reconstruction of Model Context Protocol (MCP) Activity in Agentic LLM Systems", DFRWS USA 2026. (§6.4, §7.3, §8) https://dfrws.org/presentation/with-or-without-logs-reconstructing-model-context-protocol-activity-from-volatile-memory/ — 도구: https://github.com/BiTLab-BaggiliTruthLab/MCPRecon
- [agentsview] kenn-io/agentsview — `internal/parser/cowork_paths.go`. https://github.com/kenn-io/agentsview
