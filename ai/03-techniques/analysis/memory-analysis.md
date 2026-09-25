---
title: "메모리에서 AI 흔적 찾기"
parent: "기법 · 분석"
nav_order: 880
---

# 메모리에서 AI 흔적 찾기 (Memory Analysis)

AI 앱이 실행 중일 때 뜬 메모리 이미지에서 대화·도구 호출 메시지를 찾아 떼어 내고, 형식 검사와 요청·응답 짝짓기를 거쳐 증거로 쓸 만한 조각만 남기는 방법입니다.

논문은 Ubuntu 24.04 가상 머신에서 Codex CLI 와 VS Code + GitHub Copilot 을 시험했고, 공격 시연은 Cursor 2.4.27 로 했습니다[1]. Windows·macOS 나 새 판의 앱에서는 결과가 다를 수 있습니다.

## 언제 쓰나

디스크 기록이 없거나 믿기 어려울 때 씁니다. 에이전트의 도구 호출은 잠깐 떴다 사라지는 실행 환경에서 일어나서, 로그와 패킷 기록이 불완전하거나, 꺼져 있거나, 일부러 지워질 수 있습니다[1]. 설정을 고치고 흔적을 지우는 로컬 공격자(악성 코드, 악성 확장)가 있을 때도 메모리는 디스크와 따로 남는 증거원이 됩니다[1]. 원격 MCP 서버를 쓴 경우에도 HTTP 방식 호출의 인자와 결과를 메모리 이미지에서 되살릴 수 있습니다(Table 3)[1]. 설정에 따라 처음부터 디스크에 남지 않는 값도 있습니다. Codex CLI 는 로그인 정보 저장 방식을 `ephemeral` 로 두면 실행 중인 프로세스 메모리에만 둡니다([Codex CLI](../../02-artifacts/dev-agents/codex-cli.md) 참고).

디스크 분석에서 "되살릴 수 없음" 으로 나온 흔적을 다시 찾을 때도 씁니다. LangurTrace 연구는 로컬 LLM 앱의 흔적을 Windows 11 Pro 디스크에서 되살릴 수 있는지만 따졌고, 볼륨 섀도 사본과 라이브 메모리 분석은 평가하지 않았습니다(§6.2)[3]. 그래서 이 연구가 "되살릴 수 없음" 으로 적은 흔적도 일부는 되찾을 수 있습니다[3].

대화형 서비스에도 같은 생각을 적용할 수 있습니다. ISDFS 2025 발표 연구는 Windows PC 와 Android 폰에서 ChatGPT 를 사이버 범죄에 끌어들이는 상황을 꾸미고, 메모리·모바일·네트워크 포렌식을 함께 써서 세션 토큰, 대화 기록, 안전 장치를 피하도록 조작한 프롬프트를 뽑았습니다[4]. 웹 앱으로 쓴 ChatGPT 의 메모리를 분석한 사례 연구도 FSI:DI 2026 에 실렸습니다[5]. 대화 서비스별 디스크 흔적은 [ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md) 같은 서비스 쪽에 있습니다.

## 절차

아래 순서는 MCP 를 대상으로 한 논문의 알고리즘(Algorithm 1)과 검증 과정을 따릅니다[1]. MCP 가 아닌 앱에는 4단계의 기준 문자열과 6단계의 구조 검사를 그 앱의 형식에 맞게 바꿔 씁니다.

1. **켜진 기기면 메모리부터 뜹니다.** 모으는 순서는 [조사 절차](../acquisition/investigation-process.md)의 휘발성 순서를 따르고, 조사하려고 AI 앱을 새로 실행하지 않습니다([기기에서 AI 흔적 모으기](../acquisition/endpoint-triage.md)). 클라이언트가 계속 메모리를 할당하면 앞서 주고받은 메시지 버퍼가 덮어써지므로[1], 사건 뒤 빨리 뜰수록 남는 것이 많습니다. 뜬 시각과 이미지 해시를 기록해 둡니다. MCP 는 메시지에 시각을 넣도록 정하지 않았으므로[1], 이 수집 시각이 메모리 흔적의 시간 기준이 됩니다.
2. **후보 프로세스를 고릅니다.** AI 앱 본체(편집기, 에이전트 실행기, 브라우저)와 그 자식 프로세스가 대상입니다. stdio 방식 MCP 서버는 클라이언트가 띄운 자식 프로세스이고, 논문 시험에서 Copilot 은 파이프, Codex 는 소켓으로 서버와 통신했습니다[1]. Volatility3 로 프로세스를 나열하고, 편집기나 에이전트의 PID 를 출발점으로 주면 찾을 범위가 줄어듭니다[1].
3. **프로세스 메모리 영역을 떼어 냅니다.** 힙과 익명 매핑, V8 힙, 매핑된 버퍼, 필요하면 스택까지 뽑습니다[1]. 떼어 낸 조각에는 PID, 영역 범위, 바이트 오프셋을 함께 적어 두어야 나중에 같은 자리를 다시 찾을 수 있습니다[1].
4. **기준 문자열을 찾습니다.** MCP 는 `"jsonrpc"`, `tools/list`, `tools/call` 을 씁니다[1][2]. 다른 AI 앱은 그 앱이 디스크에 남기는 JSON 키 이름을 기준 문자열로 삼습니다. MCP 메시지는 대부분 평문 UTF-8 JSON 입니다[1]. 다른 앱이 어느 인코딩으로 문자열을 두는지는 검체마다 다를 수 있으니 UTF-8 과 UTF-16LE 를 둘 다 찾습니다.
5. **JSON 을 떼어 냅니다.** 기준 문자열 바로 앞의 `{` 에서 시작해 중괄호 짝이 맞을 때까지 읽습니다. MCPRecon 은 기준 문자열 앞뒤 16KB(기본값) 안에서 이 짝을 찾습니다[2]. JSON 뒤에 이어지는 널 채움, 널로 끝나는 경계, 붙어 있는 바이너리 바이트가 메시지 끝을 가리는 단서입니다(Table A.6)[1].
6. **세 겹으로 거릅니다.** 먼저 JSON 으로 읽히는지 봅니다. 다음으로 JSON-RPC 2.0 구조인지 봅니다. `"jsonrpc":"2.0"` 이 있어야 하고, `method` 가 있으면 요청이나 알림, `result`·`error` 가 있으면 응답이며, `id` 는 문자열이나 정수여야 합니다[1][2]. 끝으로 MCP 메시지인지 봅니다. `method` 가 `tools/`·`resources/`·`prompts/`·`notifications/` 로 시작하거나 `result` 안에 `tools` 가 있으면 남깁니다[1][2].
7. **요청과 응답을 짝짓습니다.** `method` 가 있는 요청과 `result`·`error` 가 있는 응답의 `id` 가 같으면 한 쌍으로 봅니다[1]. `method` 가 있는데 `id` 가 없으면 응답을 기다리지 않는 알림입니다[2]. 짝지은 쌍에서 `tools/list` 응답으로 모델에게 보인 도구 목록을, `tools/call` 요청과 응답으로 인자와 결과를 뽑습니다[1].
8. **보고할 조각은 손으로 다시 봅니다.** Volatility3 로 클라이언트 프로세스의 메모리를 떼어 낸 뒤, `rg` 와 `xxd` 로 보고된 오프셋에 같은 JSON 이 있는지, 힙 버퍼 안에 자연스럽게 놓였는지 확인합니다[1].
9. **디스크·네트워크 기록과 맞춥니다.** 메모리에서 찾은 호출을 호스트 앱 로그, 대화 기록, 파일 변경 시각과 나란히 [AI 사용 타임라인](timeline.md)에 올립니다. MCP 설정 파일과 로그 위치는 [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md)에 있습니다.

8단계를 따라 해 보는 명령은 아래와 같습니다. 파일 이름, 오프셋, 바이트는 모두 만든 예시이고, 원본이 아니라 사본에서만 돌립니다.

```sh
# 만든 예시. 기준 문자열이 이미지 파일 안 몇 번째 바이트에 있는지 10진수로 뽑는다
rg -a -b -o '"jsonrpc":"2.0"' case-0001.vmem | head
# 뽑은 오프셋부터 256바이트를 헥스로 본다
xxd -s 27440064 -l 256 case-0001.vmem
```

```
만든 예시(값은 지어낸 것)
01a2b3c0: 7b22 6a73 6f6e 7270 6322 3a22 322e 3022  {"jsonrpc":"2.0"
...
01a2b440: 2c22 6964 223a 377d 0000 0000 0000 0000  ,"id":7}........
```

첫 줄은 `{"jsonrpc":"2.0"` 의 UTF-8 바이트이고, 마지막 줄의 `7D` 뒤에 널 바이트가 이어지면 그 자리를 메시지 끝으로 봅니다.

## 도구

**Volatility3.** 메모리 이미지에서 프로세스를 나열하고 후보 프로세스의 메모리 매핑을 뽑는 데 씁니다[1]. MCPRecon 의 `--vol3` 옵션은 `--client` 를 함께 줄 때 Volatility3 의 `linux.pslist` 를 대신 돌려 줍니다[2].

**MCPRecon.** 파이썬 표준 라이브러리만 쓰는 도구이고, 명령줄 도구 `mcprecon.py` 와 Tkinter 화면 도구 `mcprecon_gui.py` 로 나뉩니다[2]. 출력 칸과 필터 옵션은 [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md)에 있고, 결과를 읽을 때 알아야 할 동작은 아래와 같습니다(`tool/mcprecon.py` 기준)[2].

| 동작 | 코드가 하는 일 | 결과를 읽을 때 |
|---|---|---|
| 이미지 읽기 | 메모리 이미지 파일을 통째로 읽어 들인다 | 분석 PC 에 이미지 크기만큼의 메모리가 필요하다 |
| `offset` | 떼어 낸 JSON 이 이미지 파일 안에서 시작하는 위치. 코드 첫머리 설명에 적힌 `vma` 칸은 실제 출력에 없다 | 어느 프로세스의 메모리인지는 이 칸만으로 알 수 없다 |
| 기준 문자열 | `--keywords` 로 준 문자열을 바이트 그대로 찾고, `jsonrpc` 는 늘 더한다 | UTF-16LE 로 남은 문자열은 찾지 않는다 |
| `session` | 오프셋 거리가 512KB 보다 멀어지면 번호를 바꾼다 | MCP 세션이 아니라 이미지 안에서 가까이 놓인 조각의 묶음이다 |
| `confidence` | 세션마다 JSON 성공 비율, JSON-RPC 통과 비율, MCP 판정 비율, 요청·응답 짝 비율, 오프셋이 모인 정도를 0.2 씩 더한다 | 같은 세션의 줄은 모두 같은 값이다. 조각 하나의 신뢰도가 아니다 |
| `mcp` | `method` 가 MCP 메서드로 시작하거나 `result` 에 `tools` 가 있을 때만 참 | `tools/call` 에 대한 응답 줄은 `false` 로 나오는 것이 보통이고, `--mcp-only` 를 주면 `id` 가 같은 짝으로 남는다 |
| `--client` | 프로세스 목록에서 이름에 정해진 글자가 든 첫 프로세스의 PID 를 고른다. `codex` 는 `code`, `code helper`, `codex`, `cursor` 를 찾는다 | 기록에 꼬리표만 붙는다. 그 PID 의 메모리 범위로 좁히는 것은 `--vma-file` 을 `--regions-file` 과 함께 줄 때뿐이다 |
| `--vol3` | `--client` 를 줄 때만 `linux.pslist` 를 돌린다 | Windows 이미지는 따로 뽑은 프로세스 목록을 `--ps-file` 로 준다. Volatility3 JSON 출력이면 `PID`·`ImageFileName` 칸을 읽는다 |

아래는 `tools/call` 요청과 그 응답이 짝지어 나온 출력 두 줄입니다. 칸 순서는 코드가 쓰는 순서를 따랐고, 값은 모두 만든 예시입니다.

```json
{"offset": 27440064, "type": "request", "id": 7, "method": "tools/call", "tool": "get_current_weather", "valid": true, "mcp": true, "json": {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "get_current_weather", "arguments": {"city_name": "Exampleville", "country": "XX"}}}, "tag": null, "session": 0, "confidence": 0.84}
{"offset": 27441088, "type": "response", "id": 7, "method": null, "tool": null, "valid": true, "mcp": false, "json": {"jsonrpc": "2.0", "id": 7, "result": {"content": [{"type": "text", "text": "sunny"}], "isError": false}}, "tag": null, "session": 0, "confidence": 0.84}
```

**rg 와 xxd.** 도구가 보고한 조각을 손으로 확인할 때 씁니다[1]. UTF-16LE 문자열은 GNU `strings -el` 로 뽑아 같은 키 이름을 찾을 수 있습니다.

## 함정과 한계

메모리에 없다고 해서 그 호출이 없었던 것은 아닙니다. Codex 와 Copilot 을 한 가상 머신에서 함께 돌리고 메모리를 한 번만 뜬 시험에서는 일부 단계의 흔적이 되살아나지 않았습니다(Table 4)[1]. Codex 는 HTTP 날씨 서버와 Context7 에서 첫 번째 호출이 빠졌고, Copilot 은 세 구성 모두에서 도구 목록 조회가, stdio 날씨 서버에서는 두 번째 호출까지 빠졌습니다[1]. 클라이언트가 계속 메모리를 할당하면 버퍼가 덮어써지고, 여러 앱이 함께 돌면 메모리가 더 자주 바뀌고 조각나며, 짧게 쓰고 버리는 버퍼는 일부만 남아 검사를 통과하지 못하기 때문입니다[1]. 클라이언트를 하나씩 돌린 여섯 구성에서는 세 단계가 모두 되살아났습니다(Table 3)[1].

증거가 한쪽만 남을 수 있습니다. 논문의 공격 시연에서 악성 서버가 응답에 지시문을 끼워 넣었는데, 지시문이 든 응답은 손으로 찾아봐도 메모리 어디에도 없었고(덮어써진 것으로 보입니다), 작업 폴더의 파일 내용을 `country` 인자에 실어 내보낸 요청만 되살아났습니다(§8.3)[1]. 지시가 어디서 왔는지는 메모리만으로 밝히지 못할 수 있으니 서버 설정과 대화 기록을 함께 봅니다. 시연 내용과 인젝션 분석 방법은 [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md)과 [프롬프트 인젝션 사고 분석](prompt-injection.md)에 있습니다.

논문의 시험 범위는 좁습니다. 운영체제는 Linux 하나였고, 클라이언트는 Codex CLI 와 VS Code + Copilot 두 가지였으며, 다른 클라이언트·운영체제·MCP 메서드는 시험 범위에 들지 않았습니다(§7.3)[1]. HTTP 방식 시험에서도 서버는 같은 가상 머신 안에서 네트워크 서비스로 돌았고, 메모리 이미지는 그 가상 머신 전체를 뜬 것입니다(§6.5)[1]. 실제 원격 서버를 쓴 사건에서는 서버 프로세스의 메모리가 조사 대상 기기에 없으므로, 클라이언트 쪽에 무엇이 남는지 검체로 확인합니다. 서버 안에서 일어난 일은 [서비스 회사에 대한 데이터 요청](../acquisition/legal-requests.md) 같은 법적 절차로 얻습니다.

이 방법은 메시지가 평문 JSON 으로 메모리에 놓인다는 전제에 기댑니다. 앞으로 MCP 구현이 메모리 안의 메시지를 암호화하거나 알아보기 어려운 형태로 두거나 버퍼를 곧바로 지우면 되살리기 어려워집니다[1]. 커널이나 메모리 수집 도구가 오염되었으면 메모리 증거 자체를 믿을 수 없습니다[1]. 메모리에는 MCP 와 상관없는 JSON 조각도 많아서, 문자열 검색만으로는 조각이 맞는 메시지인지, 어느 요청의 응답인지 가를 수 없습니다[1].

메모리에는 비밀 값도 평문으로 남습니다. 세션 토큰은 메모리 등에서 뽑을 수 있습니다[4]. 토큰과 API 키는 어디에 남았는지까지만 적고 보고서에서는 값을 가립니다. 남는 곳 전반은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

## 결과를 어떻게 해석하나

메모리에서 나온 MCP 흔적은 두 가지로 나눠 읽습니다[1]. `tools/list` 응답과 도구 스키마는 능력 증거라서 그때 모델에게 어떤 도구가 보였는지를 알려 줍니다. `tools/call` 요청과 짝지은 응답은 행동 증거라서 어떤 도구를 어떤 인자로 불렀고 무엇을 돌려받았는지를 알려 줍니다. 응답의 `result` 와 `error`, `isError` 로 성공과 실패를 가릅니다[1].

믿을 만한 조각은 요청의 `method`, `id`, 도구 이름, 인자, 같은 `id` 의 응답, `inputSchema` 가 서로 맞습니다[1]. 인자는 그 도구의 입력 스키마에 맞아야 하고, 응답은 요청과 같은 `id` 에 구조도 맞아야 합니다[1]. 칸끼리 어긋나거나, 짝이 없거나, 인자가 스키마와 다른 조각은 혼자서 누가 무엇을 했다는 근거로 쓰지 않습니다[1]. MCPRecon 의 `confidence` 는 세션 전체의 점수라서 조각 하나의 신뢰도로 옮겨 적지 않습니다[2].

시각은 메모리를 뜬 시각까지만 말할 수 있습니다. 메모리에 있었다는 것은 그 메시지가 수집 시각보다 앞서 오갔다는 뜻이고, 몇 시에 오갔는지는 디스크 쪽 기록에서 가져옵니다. 순서는 `id` 와 메모리 위치로 추정할 뿐이며, JSON-RPC 규격이 `id` 를 차례대로 매기라고 정하지 않았으므로 `id` 순서를 시간 순서로 단정하지 않습니다[1].

메모리 흔적은 클라이언트가 그 요청을 보냈다는 것까지 보여 줍니다. 사용자가 그 호출을 시켰는지, 승인했는지는 대화 기록과 승인 기록에서 따로 확인합니다. 논문의 공격 시연에서 사용자 화면에 드러난 것은 "Listed test Read mcp.json" 한 줄과 조금 바뀐 `get_weather_forecast` 호출뿐이었고, 나머지는 접힌 생각 블록과 입력·응답 칸을 펼쳐야 보였습니다(§8.2)[1]. 에이전트가 한 일 전체를 따라가는 흐름은 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)에 있습니다.

보고서에는 기록이 말하는 만큼만 씁니다. 아래 문장의 시각, 오프셋, 값은 모두 만든 예시입니다.

> 2026-01-01 03:00 UTC 에 수집한 메모리 이미지의 파일 오프셋 27440064 에 도구 `get_current_weather` 를 부른 `tools/call` 요청(`id` 7)이 있고, 같은 `id` 의 응답이 오프셋 27441088 에 있다. 요청의 인자 `country` 에는 작업 폴더의 설정 파일 내용으로 보이는 문자열이 들어 있다. 이 요청이 오간 시각은 메모리만으로 정할 수 없고, 수집 시각보다 앞선다.

## 참고 문헌

1. A. Satter, M. Salmon, L. Muhanna, T. T. Spinosa, T. Gharaibeh, I. Baggili, "With or Without Logs: Memory Forensic Reconstruction of Model Context Protocol (MCP) Activity in Agentic LLM Systems". 코드와 실험 자료: https://github.com/BiTLab-BaggiliTruthLab/MCPRecon (§4, Algorithm 1, §5.2, §6.4~6.8, §7.2~7.3, §8, Table 3·4·5·A.6)
2. BiTLab-BaggiliTruthLab/MCPRecon — https://github.com/BiTLab-BaggiliTruthLab/MCPRecon — `README.md`, `tool/mcprecon.py` (마지막 커밋 2026-04-12)
3. S. Jeong, S. Lee, J. Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. https://doi.org/10.1016/j.fsidi.2025.301987 (§6.2)
4. "Forensic Investigations in the Age of AI: Identifying and Analyzing Artifacts from AI-Assisted Crimes", 2025 13th International Symposium on Digital Forensics and Security (ISDFS), IEEE, 2025. https://doi.org/10.1109/isdfs65363.2025.11012109 (초록)
5. "Forensic analysis from generative AI web application memory: A ChatGPT case study", Forensic Science International: Digital Investigation, 2026. https://doi.org/10.1016/j.fsidi.2026.302175
