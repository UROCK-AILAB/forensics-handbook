---
title: "로그와 원격 측정"
parent: "GitHub Copilot"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 630
---

# 로그와 원격 측정 (Logs·Telemetry)

GitHub Copilot 은 IDE 마다 로그를 남기는 자리가 다르고, Visual Studio 의 Copilot 은 추적 파일 `*_VSGitHubCopilot_traces.jsonl` 에 프롬프트·응답·도구 호출까지 남기며, VS Code 자체의 원격 측정은 `telemetry.telemetryLevel` 설정에 따라 보내는 범위가 달라집니다.

> 로그 줄의 실제 모양은 Copilot 확장·플러그인 버전에 따라 다를 수 있으므로, 검체를 보고 버전과 함께 적어 둡니다.

## 무엇을 기록하나 · 왜 생기나

Copilot 로그는 연결 문제나 오류를 풀려고 남기는 기록입니다[1]. 로그 보는 법이 공개된 IDE 는 JetBrains IDE(IntelliJ IDEA, Android Studio, GoLand, PhpStorm, PyCharm, RubyMine, WebStorm, Rider), VS Code, Visual Studio, Xcode, Vim/Neovim 입니다[1]. 로그에 프롬프트·응답 본문이 들어가는지는 공개 자료에 없으므로, VS Code 의 대화 내용은 [Windows](windows.md)에서 다루는 세션 파일에서 찾습니다.

Visual Studio 는 사정이 다릅니다. Visual Studio Copilot 은 대화를 평소 공유 추적 파일 `*_VSGitHubCopilot_traces.jsonl` 에 담고, 이 파일은 OpenTelemetry 추적(span) 형식이라 span 을 읽어 대화를 다시 짜 맞출 수 있습니다[4]. 그래서 Visual Studio 에서는 이름이 "로그" 인 폴더가 대화 기록의 주된 자리가 됩니다. 이 형식을 설명한 Microsoft 쪽 공개 문서는 없습니다[4].

## 위치와 버전별 차이

### IDE 별 로그

| IDE | 여는 법 | 파일·경로 |
|---|---|---|
| VS Code | View → Output 에서 "GitHub Copilot" 채널 선택[1] | — |
| VS Code | 명령 팔레트 `Developer: Open Extension Logs Folder`[1] | 확장 로그 폴더. 공개 문서에 OS 별 경로가 없으므로 VS Code 사용자 데이터 폴더를 통째로 수집합니다 |
| VS Code | `Developer: Toggle Developer Tools` → Console 탭[1] | Electron 로그 |
| JetBrains | Help → Show Log in …(Rider 는 Diagnostic Tools 아래)[1] | `idea.log` |
| Visual Studio | View → Output 에서 "GitHub Copilot" 선택[1] | 추적 파일은 아래 표 |
| Xcode | Advanced → Open Copilot Log Folder[1] | 경로는 [macOS](macos.md) |
| Vim/Neovim | `:Copilot status` 로 상태 확인[1] | — |

VS Code 안에서는 "GitHub Copilot" 과 "GitHub Copilot Chat" 이 로그 설정 화면에 서로 다른 확장 이름으로 나옵니다[1].

### Visual Studio 추적 파일과 대화 파일

| 무엇 | 위치 | 근거 |
|---|---|---|
| 추적 파일 `*_VSGitHubCopilot_traces.jsonl` | Windows `%LOCALAPPDATA%\Temp\VSGitHubCopilotLogs\traces\` | agentsview README·형식 메모[4] |
| 같은 추적 파일 | macOS `~/Library/Caches/VSGitHubCopilotLogs/traces/` | agentsview README[4] |
| 같은 추적 파일 | Linux `~/.cache/VSGitHubCopilotLogs/traces/` | agentsview README[4] |
| 대화 파일(확장자 없음, 이름은 36자 UUID) | 솔루션 폴더의 `.vs\*\copilot-chat\*\sessions\` | agentsview `visualstudio_copilot_provider.go`, `visualstudio_copilot.go`[4] |

추적 파일은 추적 폴더에서 이름이 `.jsonl` 로 끝나고 `_VSGitHubCopilot_traces` 를 담은 파일입니다[4]. 파일 이름은 `20260615T234102_b45c44b2_VSGitHubCopilot_traces.jsonl` 처럼 날짜·시각 모양 글자로 시작합니다[4]. 이 앞부분이 파일을 만든 시각인지, UTC 인지는 공개 자료가 없으니 같은 파일 안의 span 시각과 견주어 검체에서 확인합니다.

Visual Studio 2026 은 솔루션 폴더의 `.vs/*/copilot-chat/*/sessions` 에도 대화 파일을 씁니다[4]. 대화 파일은 이름이 36자 UUID 모양(8-4-4-4-12 자리의 16진수)이고, 내용은 추적 파일과 같은 span 구조입니다[4]. 이 폴더는 사용자 프로필이 아닌 솔루션 폴더 안에 있어서, 사용자 폴더만 수집하면 빠집니다. 수집 범위는 [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md)를 봅니다. 이 배치가 어느 Visual Studio 판부터인지는 공개 자료가 없으므로, 보고서에는 검체의 Visual Studio 판을 함께 적습니다.

### 사용자가 켜야 생기는 기록

아래 기록은 평소에는 없고, 사용자가 일부러 켜거나 명령을 돌려야 생깁니다[1].

| IDE | 켜는 법 | 남는 것 |
|---|---|---|
| VS Code | `Developer: Set Log Level` → "GitHub Copilot Chat" 또는 "GitHub" → Trace | 자세한 로그. 끝나면 Info 로 되돌리게 되어 있음 |
| VS Code | `Developer: Chat Diagnostics` | 새 편집기 창에 진단 결과. "Reachability" 절 포함 |
| JetBrains | Help → Diagnostic Tools → Debug Log Settings 에 `#com.github.copilot:trace` 한 줄 추가 | `idea.log` 에 자세한 로그. 네트워크 문제 확인용 |
| JetBrains | Tools → GitHub Copilot → Log Diagnostics | `idea.log` 에 진단 결과. "Reachability" 절 포함 |
| JetBrains | Tools → GitHub Copilot → Log CA Certificates | 신뢰하는 CA 인증서를 PEM 형식으로 `idea.log` 에 남김 |
| Xcode | Advanced → Logging → Verbose Logging | 자세한 로그 |

`idea.log` 에 trace 줄이나 "Reachability" 절, PEM 인증서 덩어리가 있으면 그 무렵 누군가 Copilot 연결 문제를 풀려고 손댔다고 읽을 수 있습니다. 다만 이것은 사용자가 켜야 생긴다는 점에서 끌어낸 추론이므로, 보고서에는 추론이라고 밝혀 씁니다.

## 구조

### Visual Studio 추적 파일

한 줄에 OpenTelemetry JSON 봉투가 하나 들어 있고, 안쪽은 `resourceSpans[]` → `scopeSpans[]` → `spans[]` 차례로 이어집니다[4]. span 하나에는 `traceId`, `spanId`, `name`, `startTimeUnixNano`, `endTimeUnixNano`, `attributes[]` 가 있습니다[4]. `attributes[]` 의 항목은 `key` 와 `value` 로 나뉘고, `value` 안에 `stringValue`·`intValue`·`boolValue` 중 하나가 들어갑니다[4]. 속성을 읽기 쉽게 키-값 사전으로 펴 놓은 예시도 있지만, 원본 파일에서는 이 배열 모양으로 나옵니다[4].

span 은 `gen_ai.operation.name` 값에 따라 세 가지로 나뉩니다[4].

| span | `name` 모양 | 주요 속성 |
|---|---|---|
| 채팅 | `chat` 뒤에 모델 이름 | `gen_ai.conversation.id`, `gen_ai.request.model`·`gen_ai.response.model`, `gen_ai.input.messages`(프롬프트), `gen_ai.output.messages`(응답 글과 도구 호출 제안), `gen_ai.usage.input_tokens`·`gen_ai.usage.output_tokens`, `copilot_chat.client_id`, `copilot_chat.root_request_id`, `server.address` |
| 도구 실행 | `execute_tool` 뒤에 도구 이름 | `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.tool.call.arguments`(파일 경로·명령·패치), `gen_ai.tool.call.result`(결과), `gen_ai.tool.type` |
| 에이전트 호출 | `invoke_agent` 뒤에 에이전트 이름 | `gen_ai.agent.name`, `copilot_chat.mode`, `copilot_chat.turn_count`, `copilot_chat.entry_point`, `copilot_chat.initiator_type` |

`gen_ai.input.messages` 와 `gen_ai.output.messages` 는 JSON 을 문자열로 한 번 더 싼 값입니다[4]. 풀면 `role` 과 `parts[]` 가 나오고, `parts[]` 의 `type` 이 `text` 면 `content` 에 글이, `tool_call` 이면 `id`·`name`·`arguments` 가 들어 있습니다[4]. 대화는 `gen_ai.conversation.id` 로 묶습니다. 파일 하나에 여러 대화가 섞이고 대화 하나가 여러 추적 파일로 나뉠 수 있어서, 같은 폴더의 모든 추적 파일을 읽어 이 값으로 이어 붙입니다[4].

### VS Code 세션 저장 로그 문장

VS Code 는 채팅 세션 저장 중 오류가 나면 원격 측정 이벤트 `chatSessionStoreError` 를 보냅니다[2]. 세션 저장과 관련해 로그에 남는 문장은 아래와 같습니다[2].

| 수준 | 문장 | 뜻 |
|---|---|---|
| trace | `ChatSessionStore: Trimmed N old chat sessions from index` | 로컬 세션이 400개를 넘어 오래된 세션이 색인에서 빠졌다 |
| info | `ChatSessionStore: Read chat session <ID> from previous location` | 예전 빈 창 위치 같은 옛 폴더의 세션을 읽었다 |
| info | `ChatSessionStore: Copied N chat session files from ... to ... (originals preserved at old location)` | 작업 영역이 바뀌어 세션 파일을 새 자리로 복사했고, 원본은 옛 자리에 남겨 두었다 |
| info | `ChatSessionStore: Clearing N chat sessions` | 세션을 한꺼번에 지웠다 |

trace 수준 문장은 기본 설정의 로그에서는 보이지 않을 수 있습니다. 세션 색인과 폴더 구조는 [Windows](windows.md)에 있습니다.

### VS Code 원격 측정 설정

VS Code 는 충돌 보고, 오류 원격 측정, 사용 데이터 세 가지를 모으고, 설정 키 `telemetry.telemetryLevel` 로 보내는 범위를 정합니다[3].

| 값 | 보내는 것 |
|---|---|
| `all` | 충돌·오류·사용 데이터 |
| `error` | 충돌·오류 |
| `crash` | 충돌만 |
| `off` | 보내지 않음 |

로컬에서도 확인할 수 있습니다[3]. `Developer: Show Telemetry` 는 추적을 켜고 Telemetry 출력 채널을 열며, `Developer: Open Log...` 로 로컬 `telemetry.log` 파일을 열 수 있고, `Developer: Reload Window` 로 추적을 끕니다. `code --telemetry` 를 돌리면 VS Code 가 보낼 수 있는 원격 측정 이벤트 목록을 JSON 으로 뽑습니다.

확장은 `telemetry.telemetryLevel` 을 따르지 않고 자체 원격 측정을 할 수 있어서, 확장마다 따로 확인해야 합니다[3]. Copilot Chat 은 OpenTelemetry 로 추적·지표·이벤트를 내보낼 수 있습니다[3]. 그래서 `settings.json` 에 `off` 가 들어 있어도 Copilot 이 아무것도 보내지 않았다고 결론 내리지 않습니다. 아래는 만든 예시입니다.

```json
{
  "telemetry.telemetryLevel": "error"
}
```

GitHub 가 서버에 보관하는 프롬프트·사용 기록과 조직 요금제의 감사 로그는 PC 에서 볼 수 없으니, [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)과 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)를 봅니다.

## 증거로서 의미

**증명하는 것.** Copilot 로그가 있으면 그 IDE 에 Copilot 확장이나 플러그인이 설치돼 돌았다는 흔적이 됩니다. Visual Studio 추적 파일에 채팅 span 이 있으면, 그 시각에 그 대화 ID 로 어떤 프롬프트가 모델에 갔고 어떤 응답이 돌아왔는지, 입력·출력 토큰이 얼마였는지를 말할 수 있습니다[4]. 도구 실행 span 은 어떤 파일 경로·명령·패치를 인자로 도구가 실행됐고 어떤 결과를 돌려받았는지를 보여 줍니다[4]. `copilot_chat.mode` 와 `copilot_chat.initiator_type` 에는 에이전트 모드였는지, 요청을 누가 시작한 것으로 기록됐는지가 들어 있습니다[4]. 원격 측정 설정 값은 그 계정의 VS Code 가 어느 범위까지 보내도록 설정돼 있었는지를 알려 줍니다[3].

**증명하지 못하는 것.** VS Code·JetBrains 로그에 프롬프트나 응답 본문이 들어간다는 공개 문서는 없으므로, 그 로그만으로 어떤 프롬프트를 보냈는지나 제안을 받아들였는지를 말하지 않습니다. Visual Studio 의 도구 실행 span 도 도구가 돌았다는 기록일 뿐이라서, 그 변경이 지금 파일에 남아 있는지는 파일 자체와 버전 관리 기록으로 따로 확인합니다. 원격 측정 설정이 확장의 자체 원격 측정까지 막았다고 볼 수는 없습니다[3]. 추적 파일에는 자판 앞에 앉은 사람이 누구였는지가 없으므로, 계정·로그인 흔적과 함께 봅니다.

보고서 문장은 "피의자가 Copilot 에게 코드를 고치게 했다" 가 아니라 "2026-06-12 19:46:40(UTC) 에 대화 ID 3f2a9c1e-… 의 채팅 span 에 이런 프롬프트가 기록돼 있다" 처럼 기록이 말하는 만큼만 씁니다(시각과 ID 는 아래 만든 예시의 값).

## 시각 해석

Visual Studio span 의 `startTimeUnixNano`·`endTimeUnixNano` 는 1970-01-01 UTC 부터 센 나노초를 10진 문자열로 적은 값입니다[4]. 시작과 끝이 따로 있으므로 요청 하나에 걸린 시간도 알 수 있습니다. 추적 파일 이름 앞부분의 날짜·시각 모양 글자가 무엇을 뜻하는지는 공개 자료가 없으니, 같은 파일 안의 span 시각과 비교해 검체에서 확인합니다. 대화 하나가 여러 파일에 나뉠 수 있으므로, 대화 시각은 파일 수정 시각이 아닌 span 시각으로 잡습니다[4].

VS Code 로그 줄의 시각 형식과 시간대는 공개 문서에 없으니, 같은 검체의 다른 시각(세션 파일의 `creationDate`·`lastMessageDate` 밀리초 값, [Windows](windows.md) 참고)과 맞춰 봅니다.

## 함정과 한계

- Visual Studio 추적 파일은 사용자 임시 폴더(`%LOCALAPPDATA%\Temp`) 아래에 있어서 임시 파일 정리에 쓸려 나갈 수 있으니, 다른 것보다 먼저 떠 옵니다.
- 같은 프롬프트가 여러 채팅 span 에 거듭 나오고, 같은 도구 호출 ID 가 채팅 span 과 도구 실행 span 에 겹쳐 나옵니다[4]. span 수를 질문 수나 명령 수로 세지 않습니다.
- `gen_ai.tool.call.arguments` 와 `gen_ai.tool.call.result` 에는 파일 경로, 명령, 패치, 파일 내용이 그대로 들어갈 수 있습니다[4]. 소스 코드나 비밀 값이 섞일 수 있으니 보고서에 옮길 때 가립니다. 토큰·키가 남는 자리는 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)을 봅니다.
- 추적 폴더에서 파일 하나만 떼어 보면 대화가 중간에 끊겨 보입니다. 폴더를 통째로 수집하고, 대화 ID 로 모든 파일을 훑습니다[4].
- JSON 문자열 안의 한글은 UTF-8 글자 그대로일 수도 있고 `\uXXXX` 로 적혔을 수도 있으니, 키워드 검색은 두 모양 다 해 봅니다.
- VS Code 의 출력 창과 명령 팔레트는 VS Code 를 실행해야 쓸 수 있어서, 디스크 이미지에서는 확장 로그 폴더를 파일로 찾아야 합니다. 그 경로는 공개 문서에 없으니 VS Code 사용자 데이터 폴더를 통째로 떠 옵니다.
- trace 수준은 문제를 푼 뒤 Info 로 되돌리게 되어 있어서[1], 수집 시점의 설정이 Info 여도 과거에 trace 로 남긴 로그가 있을 수 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 추적 파일 형식[4]에 맞춰 만든 예시 줄이고, 값은 모두 지어낸 것입니다.

```json
{"resourceSpans":[{"scopeSpans":[{"spans":[{"traceId":"0af7651916cd43dd8448eb211c80319c","spanId":"b7ad6b7169203331","name":"chat model-x","startTimeUnixNano":"1781293600000000000","endTimeUnixNano":"1781293604000000000","attributes":[{"key":"gen_ai.conversation.id","value":{"stringValue":"3f2a9c1e-5b7d-4e8a-9c21-0d4b6e8f1a23"}},{"key":"gen_ai.operation.name","value":{"stringValue":"chat"}},{"key":"gen_ai.input.messages","value":{"stringValue":"[{\"role\":\"user\",\"parts\":[{\"type\":\"text\",\"content\":\"explain this function\"}]}]"}},{"key":"gen_ai.usage.input_tokens","value":{"intValue":"1200"}}]}]}]}]}
```

헥스 편집기로 열면 이 줄의 첫머리가 이렇게 보입니다(만든 예시).

```text
00000000  7B 22 72 65 73 6F 75 72  63 65 53 70 61 6E 73 22  {"resourceSpans"
```

`startTimeUnixNano` 의 `1781293600000000000` 을 10^9 로 나누면 1781293600 초이고, 이는 2026-06-12 19:46:40 UTC(한국 시각 2026-06-13 04:46:40)입니다. 끝 시각 `1781293604000000000` 과는 4초 차이입니다. 대화 ID 는 헥스 편집기에서 `"gen_ai.conversation.id"` 를 글자로 검색하면 바로 뒤의 `"stringValue":"` 다음에 있습니다[4].

### 공개 도구로 한 번

jq 로 span 을 한 줄씩 펼치면 속성을 사전 모양으로 볼 수 있습니다. 사본에서만 돌립니다.

```sh
jq -c '.resourceSpans[].scopeSpans[].spans[]
  | {name, start: .startTimeUnixNano, end: .endTimeUnixNano,
     attrs: (.attributes | map({(.key): (.value.stringValue // .value.intValue // .value.boolValue)}) | add)}' \
  20260615T234102_b45c44b2_VSGitHubCopilot_traces.jsonl
```

대화 하나만 보려면 `select(.attrs["gen_ai.conversation.id"] == "3f2a9c1e-5b7d-4e8a-9c21-0d4b6e8f1a23")` 를 이어 붙이고, 폴더의 모든 추적 파일에 같은 명령을 돌립니다. `gen_ai.input.messages` 는 문자열이라서 `fromjson` 으로 한 번 더 풀어야 `parts[].content` 가 보입니다. agentsview 는 이 추적 폴더와 `.vs` 아래 대화 파일을 읽어 대화 목록으로 보여 주는 공개 도구이므로, 그 결과를 위 수작업 결과와 대조합니다[4].

## 교차 검증

- VS Code 세션 파일과 색인 → [Windows](windows.md), [macOS](macos.md)
- Copilot 을 MCP 클라이언트로 쓴 경우의 도구 호출 기록 → [MCP 서버와 도구 호출 기록](../mcp.md)
- `server.address` 에 나오는 서버로 간 연결 → [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)
- 기업 보안 제품 기록 → [보안 제품이 남기는 AI 사용 기록](../../network-enterprise/dlp-casb.md)
- 도구 실행 span 에 나온 파일 경로와 패치 → 해당 파일과 저장소의 커밋 기록

## 실습

Copilot 로그가 든 공개 검체가 없으므로, 직접 만든 시험 환경(가짜 사용자 `analyst01`)에서 풀어 봅니다.

1. Visual Studio 에서 Copilot 에게 질문 두 개를 하고 에이전트 모드로 파일 하나를 고치게 한 뒤, 추적 폴더의 파일 수와 대화 ID 개수는 각각 몇 개인가? 채팅·도구 실행·에이전트 호출 span 은 각각 몇 개인가?
2. 같은 솔루션 폴더의 `.vs` 아래에 `copilot-chat` 폴더가 생겼는가? 생겼다면 대화 파일 이름이 추적 파일의 `gen_ai.conversation.id` 와 같은가?
3. 추적 파일 이름 앞부분의 날짜·시각과 첫 span 의 `startTimeUnixNano` 는 몇 시간 차이 나는가? 시험 PC 의 시간대와 견주면 파일 이름은 UTC 인가, 현지 시각인가?
4. VS Code 에서 로그 수준을 Trace 로 바꾸기 전과 뒤에 확장 로그 폴더의 파일은 어떻게 달라지는가?
5. JetBrains 에서 Log CA Certificates 를 한 번 돌린 뒤 `idea.log` 에서 PEM 덩어리를 찾을 수 있는가?

## 참고 문헌

1. GitHub Docs, "Viewing logs for GitHub Copilot in your environment". https://docs.github.com/en/copilot/troubleshooting-github-copilot/viewing-logs-for-github-copilot-in-your-environment
2. microsoft/vscode. https://github.com/microsoft/vscode — `src/vs/workbench/contrib/chat/common/model/chatSessionStore.ts`(main)
3. Visual Studio Code Docs, "Telemetry"(2026-09-16 갱신). https://code.visualstudio.com/docs/configure/telemetry
4. kenn-io/agentsview. https://github.com/kenn-io/agentsview — `README.md`(Supported Agents 표), `docs/internal/visual-studio-copilot-traces.md`, `docs/internal/session-format-sources.md`(2026-09-11), `internal/parser/visualstudio_copilot.go`(마지막 커밋 2026-09-19), `internal/parser/visualstudio_copilot_provider.go`, `internal/parser/discovery.go`
