---
title: "프롬프트·첨부·생성물 구분하기"
parent: "기반 · 기본 개념"
nav_order: 50
---

# 프롬프트·첨부·생성물 구분하기 (Prompt·Attachment·Output)

> 확인 날짜: 2026-09. 기기 관찰은 Windows 11 한 대에서 AI 도구 폴더를 읽기 전용으로 열어 폴더·파일 이름과 키 이름만 본 결과이고, 값과 앱 버전은 적어 두지 않았습니다. 관찰로 확인한 내용에는 "(확인 범위: Windows 11, 2026-09)" 를 붙였습니다.

## 한 줄 요약

AI 대화 기록은 사용자가 입력한 프롬프트 (Prompt), 프롬프트와 함께 넣은 첨부 (Attachment), 모델이 만든 생성물 (Output) 로 나뉘고, 셋은 기록 안에서 서로 다른 칸에 들어가서 어느 칸에서 나온 글인지에 따라 "사용자가 넣었다" 와 "모델이 만들었다" 가 갈립니다.

## 이 형식을 쓰는 아티팩트

대화형 서비스, 개발 도구, 로컬 AI 모두 프롬프트·첨부·생성물을 주고받지만 원본이 어디에 남는지는 서비스마다 다릅니다. 서버·기기·동기화의 전체 그림은 [AI 서비스의 데이터는 어디에 있나](../storage-model/where-data-lives.md) 에서 다루고, 이 쪽은 기록 안에서 세 가지를 가르는 법에 집중합니다.

공식 문서로 확인한 예는 Claude Code 입니다. Claude Code 는 모든 사용자 프롬프트와 모델 출력을 네트워크로 LLM 에 보내고 이때 TLS 1.2 이상으로 암호화합니다. 그래서 대화는 서버를 거치지만, 클라이언트는 세션을 이어 가려고 세션 대화 기록을 `~/.claude/projects/` 아래에 평문으로 저장하기도 합니다. 로컬 기록의 기본 보관 기간은 30일이고 `cleanupPeriodDays` 로 바꾸며, Claude 데스크톱·Cowork 에서 시작했거나 마지막으로 이어 간 세션은 기본적으로 이 30일 제한을 받지 않습니다. Remote Control 세션은 실행은 기기에서 하지만 연결된 동안 기기 간 동기화를 위해 대화 기록을 Anthropic 서버에도 저장합니다 [1]. 서버 쪽 보관 기간은 [대화 기록 보관 설정과 삭제](../storage-model/retention-deletion.md) 에 정리합니다.

웹 서비스(ChatGPT·Claude 웹·Gemini 등)는 대화 원본이 서버에만 있는지, 계정 내보내기 파일에서 프롬프트·첨부·생성 이미지가 어떤 파일로 나뉘는지를 이 쪽을 쓰면서 공식 문서로 확인하지 못했습니다. 내보내기 파일 구조는 [계정 데이터 내보내기 형식](../storage-model/data-export-formats.md) 과 서비스별 쪽을 봅니다.

이 PC 에서 AI 도구 폴더를 열어 본 결과는 아래와 같습니다(확인 범위: Windows 11, 2026-09). 대화 기록 파일이 없었다는 말은 이 PC 에 없었다는 뜻일 뿐이고, 도구가 기록을 남기지 않는다는 뜻은 아닙니다.

| 도구 | 위치 | 이 PC 에서 본 것 | 대화 기록 파일 |
|---|---|---|---|
| [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) | `%USERPROFILE%\.claude` | 파일 10085개, 프롬프트 기록·세션 기록 | 있음 |
| [Claude](../../02-artifacts/chat-services/claude/index.md) 데스크톱(스토어 앱) | 앱 패키지 폴더 아래 `LocalCache\Roaming\Claude\` | `IndexedDB`, `Local Storage\leveldb`, `Cache`, `Code Cache`, `Network\Cookies` 같은 Electron 형 폴더 | 열어 보지 않아 확인 못 함 |
| [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md) | `%USERPROFILE%\.codex` | `hooks.json`, `skills/` | 없음 |
| [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md) | `%USERPROFILE%\.gemini` | 설정·훅 파일, `antigravity/` 폴더 | 없음 |
| [Cursor](../../02-artifacts/dev-agents/cursor.md) | `%USERPROFILE%\.cursor` | `hooks.json` 1개, 앱 데이터 폴더는 없음 | 없음 |
| [Ollama](../../02-artifacts/local-ai/ollama.md) | `%USERPROFILE%\.ollama` | 모델 추천 목록 캐시, `id_ed25519` 키 쌍 | 없음 |

Electron 형 폴더의 공통 구조는 [Electron·웹뷰 앱의 저장 구조](../storage-model/electron-webview.md) 와 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html) 에서 다룹니다. macOS·Android·iOS 의 저장 위치는 이 쪽에서 관찰하지 않았으므로 서비스별 쪽을 봅니다.

## 구조

### 세 가지와 기록 칸 (Claude Code)

Claude Code 로컬 기록에서는 프롬프트 기록 파일 `history.jsonl` 과 세션 기록 `projects/<이름>/<파일>.jsonl` 두 곳이 중심이고, 둘 다 한 줄에 JSON 하나가 들어가는 JSONL 입니다. 아래 표는 키 이름을 세 가지로 나눈 것이며 키 이름은 관찰로 확인했고 각 칸의 뜻은 공식 설명이 없어 이름으로 짐작한 것입니다(확인 범위: Windows 11, 2026-09).

| 구분 | 파일 | 키 | 담기는 것 |
|---|---|---|---|
| 프롬프트 | `history.jsonl` | `display`(문자열), `project`(문자열), `sessionId`(문자열), `timestamp`(정수) | 입력한 프롬프트와 프로젝트·세션·시각 |
| 첨부(붙여넣기) | `history.jsonl` | `pastedContents.#` 아래 `id`(정수), `type`, `content`, `contentHash` | 프롬프트에 붙여 넣은 내용, 또는 그 해시만 |
| 프롬프트·생성물 | 세션 기록 | `message.role`, `message.content[].type` | 누가 쓴 줄인지, 내용 조각의 종류 |
| 생성물(글) | 세션 기록 | `message.content[].text`, `message.content[].thinking`(+`signature`) | 답 글, 사고 과정 글 |
| 생성물(도구 호출) | 세션 기록 | `message.content[].name`, `input`, `id` | 모델이 부른 도구와 넘긴 값 |
| 도구 결과 | 세션 기록 | `message.content[].tool_use_id`, `content`, `is_error` | 도구를 실행해 돌아온 값 |
| 도구 결과 | 세션 기록 | `toolUseResult` 아래 `stdout`, `stderr`, `interrupted`, `isImage`, `success`, `commandName` | 명령 실행 결과 |
| 생성물의 부가 정보 | 세션 기록 | `message.model`, `message.id`, `requestId`, `message.stop_reason`, `message.usage.*` | 모델 이름, 요청 번호, 끝난 이유, 토큰 수 |

`message.usage` 아래에는 `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `service_tier`, `inference_geo` 같은 칸이 있습니다(확인 범위: Windows 11, 2026-09). 세션 기록의 줄마다 공통으로 `type`, `uuid`, `parentUuid`, `sessionId`, `timestamp`(문자열), `cwd`, `gitBranch`, `version`, `entrypoint`, `userType`, `isSidechain` 이 붙고, `uuid` 와 `parentUuid` 는 이름으로 보아 줄끼리 앞뒤를 잇는 칸입니다. `version` 칸은 이름으로 보아 그 줄을 남긴 클라이언트 버전이라서 앱 버전을 따로 적어 두지 않은 이 관찰에서도 검체마다 버전을 읽어 볼 수 있습니다.

아래는 세션 기록 한 줄의 짜임을 보이려고 만든 예시이고, 값은 모두 비웠습니다.

```json
{"type": "…", "uuid": "…", "parentUuid": "…", "sessionId": "…", "timestamp": "…",
 "cwd": "…", "version": "…",
 "message": {"role": "…", "model": "…", "content": [{"type": "…", "text": "…"}]}}
```

### 세 가지 밖의 칸

세션 기록에는 `attachment` 키가 있고 그 아래에 `type`, `hookEvent`, `hookName`, `stdout`, `stderr`, `exitCode`, `text`, `reminderType` 같은 칸이 붙습니다. 이름으로 보아 사용자가 올린 첨부 파일이 아니라 도구가 대화에 끼워 넣는 부가 정보(훅 실행 결과·알림 등)이고, 공식 설명은 확인하지 못했습니다(확인 범위: Windows 11, 2026-09).

세션 기록에는 `snapshot.trackedFileBackups`, `snapshot.messageId`, `snapshot.timestamp` 키도 있고, 같은 폴더 아래 `file-history/<이름>/<파일>` 이 827개 있었습니다. 생성물이 바꾼 파일의 이전 상태를 담은 사본으로 보이지만 공식 설명은 확인하지 못했습니다. 서브에이전트 기록은 `projects/<이름>/<ID>/subagents/workflows/<이름>/<파일>.jsonl` 에 따로 쌓이고 `agentId`, `attributionAgent` 키가 더 붙습니다(확인 범위: Windows 11, 2026-09).

`stats-cache.json` 에는 날짜별 `messageCount`·`sessionCount`·`toolCallCount` 와 모델별 토큰 수만 있고 내용은 없습니다(확인 범위: Windows 11, 2026-09). 공식 문서도 사용량 지표에는 코드·프롬프트·파일 경로가 들어가지 않는다고 밝힙니다 [1].

## 읽는 법

1. 원본 폴더를 복사해 두고 사본으로 작업합니다. JSONL 은 한 줄이 독립된 JSON 이라서 파일 전체가 아니라 줄 단위로 읽습니다.
2. `history.jsonl` 로 프롬프트를 시간순으로 늘어놓습니다. `pastedContents` 가 비어 있지 않은 줄은 붙여넣기가 있었던 프롬프트이고, 여기에 `content` 가 있으면 붙여 넣은 내용이 이 파일에 함께 남은 것입니다. 관찰한 파일의 처음 300줄에서 붙여넣기 5건 가운데 `content` 가 있는 것은 1건, `contentHash` 만 있는 것은 4건이었습니다(확인 범위: Windows 11, 2026-09).
3. `contentHash` 만 있는 붙여넣기는 본문이 이 파일에 없습니다. 같은 폴더에 `paste-cache/<파일>.txt` 가 7개 있었지만 둘이 이어지는지는 확인하지 못했으므로, 이름만 보고 짝을 짓지 말고 내용과 해시를 직접 대조합니다.
4. 세션 기록에서는 `message.role` 과 `message.content[].type` 으로 사용자 줄과 모델 줄을 가릅니다. 모델 줄에는 `message.model`, `requestId`, `message.usage` 가 함께 붙어서 사용자 줄과 구별하기 쉽습니다.
5. 도구 호출의 `id` 와 도구 결과의 `tool_use_id` 는 이름이 짝을 이루므로 둘을 이어 "모델이 무엇을 부르고 무엇을 돌려받았는지" 를 한 묶음으로 봅니다. 에이전트가 실행한 명령을 따라가는 법은 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md) 에서 다룹니다.
6. `attachment` 키의 줄은 사용자 첨부 목록에서 뺍니다.

아래는 줄마다 시각과 역할만 뽑아 보는 공개 도구 jq 로 만든 예시입니다. 파일 이름은 가짜 값입니다.

```bash
jq -c 'select(.message.role != null) | {timestamp, role: .message.role, model: .message.model}' demo-session.jsonl
```

## 포렌식에서 중요한 점

로컬 세션 기록은 기본 30일이 지나면 정리되고 `cleanupPeriodDays` 로 이 기간을 바꿀 수 있어서 [1], 오래된 세션이 없을 때는 사용하지 않은 것인지 보관 기간이 지나 정리된 것인지를 먼저 가립니다. 관찰한 `settings.json` 에는 `cleanupPeriodDays` 키가 없었습니다(확인 범위: Windows 11, 2026-09). 세션 기록이 없어도 `stats-cache.json` 의 날짜별 메시지·세션 수는 남아 있을 수 있어 사용한 날을 가늠하는 데 쓰지만, 내용은 되살리지 못합니다. 지운 대화를 캐시나 스냅숏에서 되살리는 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md) 에서 다룹니다.

프롬프트와 첨부의 사본이 기기 밖으로 나가는 길도 있습니다. `/feedback`·`/bug`·`/share` 로 보낸 기록은 대화 내용과 코드를 포함해 Anthropic 으로 가서 5년 보관됩니다. Amazon Bedrock·Google Cloud Agent Platform 같은 외부 제공자를 쓰거나 Anthropic 자격 증명이 없으면 이 기록을 보내지 않고 `~/.claude/feedback-bundles/` 에 로컬 압축 파일로 쓰며, 이때 알려진 API 키·토큰 모양은 가린 뒤 씁니다. Claude 가 초안을 쓴 피드백은 사용자가 보내기로 하기 전까지 기기에 쌓여 있습니다. 세션 설문 뒤 기록을 봐도 되는지 묻는 질문에 Yes 를 고르면 대화 기록과 서브에이전트 기록, 디스크의 원본 세션 로그 파일을 올리고 최대 6개월 보관하며, 알려진 API 키·토큰 모양만 가리고 소스 코드와 파일 내용은 그대로 올립니다. Bedrock·Google Cloud Agent Platform·Microsoft Foundry 에서는 같은 내용을 올리지 않고 `~/.claude/feedback-bundles/` 에 씁니다 [1]. 이 PC 의 `feedback/drafts/<파일>.json` 에는 `draft_id`, `created_at`, `cli_version`, `model`, `status`, `request_ids`, `source_session_id`, `transcript_ref.session_file` 같은 키가 있었고(확인 범위: Windows 11, 2026-09), 공식 문서의 피드백 초안과 같은 것으로 보이지만 대응 관계는 짐작입니다. `source_session_id` 와 `transcript_ref.session_file` 은 이름으로 보아 초안이 가리키는 세션이라서 세션 기록과 대조할 만합니다.

프롬프트를 제출하는 시점에 외부 명령을 돌리는 훅 설정도 흔적으로 남습니다. Claude Code 와 Codex CLI 의 `hooks.UserPromptSubmit`, Cursor 의 `hooks.beforeSubmitPrompt`, Gemini CLI 의 `hooks.BeforeAgent` 가 이 PC 설정 파일에 있었습니다(확인 범위: Windows 11, 2026-09). 훅이 프롬프트 내용을 받는지는 확인하지 못했으므로, 훅에 걸린 명령이 무엇이고 어디에 무엇을 쓰는지를 따로 확인합니다. 도구 호출이 외부 서버로 이어지는 경우는 [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md) 을 봅니다.

## 함정

- **`attachment` 키는 첨부가 아닙니다.** 이름이 같다고 사용자가 올린 파일로 보고서에 적으면 도구가 끼워 넣은 훅 결과나 알림을 사용자 행위로 잘못 쓰게 됩니다.
- **도구 결과 속 글은 사용자가 쓴 글이 아닙니다.** 도구가 기기에서 읽어 온 파일 내용이나 명령 출력이 도구 결과에 들어가서, 그 안에 기밀 문구가 있다는 사실만으로 "사용자가 붙여 넣었다" 고 쓸 수 없습니다. 기밀 자료 입력을 가리는 흐름은 [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) 에서 다룹니다.
- **사고 과정 글과 답 글을 섞지 않습니다.** `thinking` 과 `text` 는 다른 칸이라서 "모델이 답한 내용" 을 인용할 때 어느 칸에서 가져왔는지 밝힙니다.
- **시각 형식이 파일마다 다릅니다.** `history.jsonl` 의 `timestamp` 는 정수이고 세션 기록의 `timestamp` 는 문자열이며(확인 범위: Windows 11, 2026-09), 어느 시간대 기준인지는 공식 설명을 확인하지 못했습니다. 파일 시스템 시각이나 다른 기록과 맞춰 본 뒤에 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) 에 올립니다.
- **이름으로 짐작한 연결을 사실로 쓰지 않습니다.** `paste-cache` 와 `contentHash`, `file-history` 와 편집 전 파일처럼 이름이 그럴듯한 연결도 내용으로 대조하기 전에는 추정으로 적습니다.

## 도구

JSONL 은 텍스트라서 텍스트 편집기와 jq 같은 공개 명령줄 도구로 읽고, 줄 수가 많으면 스크립트로 `message.role` 별로 나눠 표로 만듭니다. 데스크톱 앱의 IndexedDB·Local Storage 는 LevelDB 형식이라서 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html) 쪽의 도구와 읽는 법을 따릅니다. 기기에서 이런 폴더를 모으는 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) 에서 다룹니다.

## 참고 문헌

1. Claude Code Docs — Data usage — https://code.claude.com/docs/en/data-usage
