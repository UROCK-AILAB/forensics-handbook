---
title: "Cursor"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 610
---

# Cursor (Cursor)

Cursor 는 AI 채팅과 에이전트가 들어간 VS Code 계열 편집기이고, 기기에는 작업 공간마다 대화 기록을 담은 SQLite 파일과 사용자 폴더 `~/.cursor` 의 훅·MCP 설정이 남지만, 서버에 무엇이 얼마나 남는지는 공개 자료로 확인하지 못했습니다.

> 확인 날짜: 2026-09. 앱 버전은 확인하지 못했습니다. 대화 기록 구조는 2025-06 에 보관 처리된 제3자 도구의 기준이고, 관찰한 PC 에는 Cursor 앱 데이터 폴더가 없어서 대화 기록 파일을 직접 보지 못했습니다. 관찰로 확인한 것은 `~/.cursor/hooks.json` 의 키 모양뿐입니다(확인 범위: Windows 11, 2026-09).

## 무엇을 기록하나 · 왜 생기나

사용자가 편집기 안에서 AI 에게 질문하거나 에이전트에게 작업을 맡기면, Cursor 는 그 대화를 작업 공간(workspace) 하나당 하나씩 두는 `state.vscdb` 라는 SQLite 파일에 저장합니다[4]. 이 내용은 대화 기록을 내보내는 제3자 도구가 읽는 방식에서 알려진 것이고, 그 도구 저장소는 2025-06-17 에 보관 처리되어 지금 버전의 Cursor 가 같은 구조를 쓰는지는 알 수 없습니다[4]. 도구 코드에는 작업 공간별 폴더 말고 전역 저장소(globalStorage) 쪽 경로도 나와서, 대화가 작업 공간 파일에만 있는지 전역 파일에도 있는지는 검체에서 두 곳을 모두 열어 확인합니다.

사용자 폴더의 `~/.cursor` 에는 에이전트 동작 전후에 사용자 스크립트를 돌리는 훅(hook) 설정 `hooks.json` 과 MCP 서버 설정이 들어갑니다[1][2]. 훅은 셸 명령 실행, 파일 읽기와 편집, MCP 도구 호출, 프롬프트 제출 같은 순간에 걸 수 있어서, 조직이 감사 목적으로 훅을 걸어 두었다면 그 스크립트가 남긴 기록이 대화 기록과 별도의 증거가 됩니다.

서버 쪽은 사정이 다릅니다. 보안 페이지에 따르면 개인 정보 보호 모드(Privacy Mode)를 켜면 데이터를 학습에 쓰지 않고, 모델 제공사와 기술·계약상 통제를 둡니다[3]. 다만 이 모드에서 서버에 무엇이 남는지, 얼마나 보관하는지, 코드베이스 색인(임베딩)을 서버에 두는지는 그 페이지에 없고 세부는 trust.cursor.com 을 가리킵니다[3]. 계정은 Settings 대시보드에서 언제든 지울 수 있지만 지운 뒤의 보관 기간은 적혀 있지 않습니다[3]. 대화 원본이 서버에도 있는지, 기기에만 있는지는 확인하지 못했고, 클라우드에서 돌아가는 에이전트(백그라운드 에이전트)의 기록이 어디에 남는지도 확인하지 못했습니다. 서버와 기기 중 어디에 무엇이 있는지 가르는 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

## 위치와 버전별 차이

아래 표는 문서와 관찰로 확인한 위치만 담습니다. `state.vscdb` 가 OS 마다 어느 경로에 있는지는 이번에 연 자료에 없어서 비워 둡니다.

| 위치 | OS | 담는 것 | 근거 |
|---|---|---|---|
| `~/.cursor/hooks.json` | 모두 | 사용자 범위 훅 설정 | 문서[1], 관찰(Windows) |
| `<프로젝트 루트>/.cursor/hooks.json` | 모두 | 프로젝트 범위 훅 설정 | 문서[1] |
| `C:\ProgramData\Cursor\hooks.json` | Windows | 기업(시스템 전체) 범위 훅 설정 | 문서[1] |
| `/Library/Application Support/Cursor/hooks.json` | macOS | 기업 범위 훅 설정 | 문서[1] |
| `/etc/cursor/hooks.json` | Linux·WSL | 기업 범위 훅 설정 | 문서[1] |
| `mcp.json`(전역·프로젝트) | 모두 | MCP 서버 설정 | 문서[2], [MCP 서버와 도구 호출 기록](mcp.md)에서 다룸 |
| `state.vscdb` | 확인 못 함 | 작업 공간별 대화 기록 | 제3자 도구[4] |

팀 범위 훅(Enterprise)은 웹 대시보드에서 설정해 자동으로 동기화하는데[1], 이 설정이 기기에 파일로 남는지는 확인하지 못했습니다.

관찰한 PC 의 `%USERPROFILE%\.cursor` 에는 파일이 `hooks.json` 하나뿐이었고 Cursor 앱 데이터 폴더는 없었습니다(확인 범위: Windows 11, 2026-09). 앱을 쓰지 않은 PC 에서도 다른 도구가 `~/.cursor/hooks.json` 을 만들 수 있다는 뜻으로 읽을 수 있어서, 이 파일 하나만 보고 "Cursor 를 설치했다" 고 쓰면 안 됩니다. 이 해석은 관찰에서 끌어낸 추론이고 문서로 확인한 사실은 아닙니다.

앱 데이터 폴더의 전체 구조도 확인하지 못했습니다. 수집한 폴더가 Electron 앱 모양이면 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)와 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)를 따라 읽고, 앱 버전을 먼저 적어 둡니다.

## 구조

### 대화 기록 `state.vscdb`

`state.vscdb` 는 SQLite 데이터베이스라서 형식 자체는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html) 페이지대로 읽습니다. 제3자 도구가 읽는 표와 키는 아래와 같고, 2025년 중반까지의 도구 기준입니다[4].

| 표 | 도구가 읽는 키 |
|---|---|
| `ItemTable` | `aiService.prompts`, `workbench.panel.aichat.view.aichat.chatdata` |
| `cursorDiskKV` | `composerData` |

키 이름으로 보아 `aiService.prompts` 는 사용자가 넣은 프롬프트, `aichat` 이 붙은 키는 채팅 패널, `composerData` 는 에이전트 쪽 대화로 짐작할 수 있지만 이 대응은 문서로 확인하지 않았습니다. 값이 JSON 인지, 대화 한 건이 어떤 구조인지, 시각 칸이 있는지도 확인하지 못했습니다.

### 훅 설정 `hooks.json`

`hooks.json` 은 JSON 파일이고 최상위에 숫자 `version`(필수, 값 1)이 있습니다[1]. 이벤트 이름 아래에 스크립트 목록을 두고, 스크립트마다 아래 키를 씁니다[1].

| 키 | 뜻 |
|---|---|
| `command` | 돌릴 명령(필수) |
| `type` | `"command"` 또는 `"prompt"`, 기본 command |
| `timeout` | 제한 시간(초) |
| `loop_limit` | 기본 5 |
| `failClosed` | 기본 false |
| `matcher` | 정규식 |

훅을 걸 수 있는 이벤트는 문서에 아래처럼 나옵니다[1].

| 갈래 | 이벤트 |
|---|---|
| 에이전트 | sessionStart, sessionEnd, preToolUse, postToolUse, postToolUseFailure, subagentStart, subagentStop, beforeShellExecution, afterShellExecution, beforeMCPExecution, afterMCPExecution, beforeReadFile, afterFileEdit, beforeSubmitPrompt, preCompact, stop, afterAgentResponse, afterAgentThought |
| Tab(자동 완성) | beforeTabFileRead, afterTabFileEdit |
| 앱 수명 | workspaceOpen |

모든 훅은 입력으로 `conversation_id`, `generation_id`, `model`, `model_id`, `model_params`, `hook_event_name`, `cursor_version`, `workspace_roots`, `user_email`, `transcript_path` 를 받고, workspaceOpen 같은 앱 수명 훅에는 대화 칸이 없습니다[1]. 훅 입력에 `transcript_path` 가 있다는 점에서 Cursor 가 대화 기록 파일 경로를 따로 둔다는 것을 알 수 있지만, 그 파일의 위치와 형식은 확인하지 못했습니다. 감사용 훅 스크립트가 이 입력을 그대로 파일에 적었다면, 그 기록에서 대화 ID·모델·Cursor 버전·계정 이메일·작업 폴더를 함께 얻을 수 있습니다.

관찰한 PC 의 `hooks.json` 은 `version`(정수)과 `hooks.` 아래 이벤트별 목록으로 되어 있었고, 목록 항목의 키는 `command`(문자열)와 `timeout`(정수)이었습니다. 걸려 있던 이벤트는 afterAgentResponse, beforeMCPExecution, beforeShellExecution, beforeSubmitPrompt, postToolUse, postToolUseFailure, preToolUse, stop 이었고, 문서 형식과 맞았습니다(확인 범위: Windows 11, 2026-09). 아래는 문서 형식대로 새로 만든 예시이고, 관찰한 값이 아닙니다.

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

훅 실행 결과는 Customize 의 Hooks 탭과 "Hooks" 출력 채널에서 볼 수 있는데[1], 이 결과가 파일로 남는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것.** `state.vscdb` 에 프롬프트나 대화가 남아 있으면 그 작업 공간에서 그 내용이 Cursor 를 거쳐 오간 기록이 있다는 뜻입니다. 파일이 작업 공간마다 따로 있어서 어느 프로젝트에서 AI 를 썼는지 좁히는 단서가 되고, 그래서 파일이 놓인 폴더를 함께 기록합니다. `hooks.json` 이 있으면 그 범위(사용자·프로젝트·기업)에 누군가 훅을 설정했다는 뜻이고, 어떤 이벤트에 어떤 명령을 걸었는지가 남습니다. 감사용 훅이 남긴 기록이 있으면 "이 시각에 에이전트가 이 셸 명령을 실행하려 했다" 처럼 에이전트 동작을 대화 기록과 별개로 보여 줍니다.

**증명하지 못하는 것.** `~/.cursor/hooks.json` 하나만으로는 Cursor 를 설치하거나 썼다고 말할 수 없습니다(위의 관찰 참고). 대화 기록이 기기에 없다고 대화가 없었다고 말할 수도 없는데, 서버에 무엇이 남는지와 클라우드 에이전트 기록의 위치를 확인하지 못했기 때문입니다. 프롬프트 기록은 요청을 보여 줄 뿐이라서, 에이전트가 실제로 파일을 고치거나 명령을 실행했는지는 git 이력·파일 시스템 기록·훅 기록으로 따로 확인합니다. 편집기를 연 사람이 누구인지도 기록이 알려 주지 않아서 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 좁힙니다.

## 시각 해석

`state.vscdb` 안에 대화별 시각 칸이 있는지 확인하지 못해서, 지금 기댈 수 있는 시각은 파일 시스템의 시각입니다. 파일 수정 시각은 앱이 그 파일에 마지막으로 쓴 때라서 대화 한 건의 시각이 아니라 그 작업 공간의 마지막 쓰기를 가리키고, 편집기 상태를 저장할 때도 바뀔 수 있습니다. `hooks.json` 의 수정 시각은 훅 설정을 마지막으로 고친 때입니다. 문서에 나온 훅 입력 칸에는 시각이 없어서, 감사 기록에 찍힌 시각은 훅 스크립트가 직접 넣은 값이고 UTC 인지 현지 시각인지는 그 스크립트를 열어 확인합니다. 여러 출처의 시각을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

대화 기록 구조의 근거가 보관 처리된 제3자 도구 하나뿐이라서, 검체의 `state.vscdb` 에 위 키가 없으면 "대화가 없다" 가 아니라 "구조가 바뀌었을 수 있다" 로 먼저 봅니다. 표 전체의 키 목록을 뽑아 보고 앱 버전과 함께 기록합니다.

훅 설정은 여러 범위에 흩어집니다. 사용자·프로젝트·기업 파일을 모두 모으지 않으면 걸려 있던 훅을 빠뜨리고, 팀 범위 훅은 웹 대시보드에서 오기 때문에 기기 파일만으로는 다 보지 못할 수 있습니다. MCP 서버는 확장 프로그램이 설정 파일을 거치지 않고 등록할 수도 있는데, 이 내용은 [MCP 서버와 도구 호출 기록](mcp.md)에 있습니다.

작업 공간을 지우거나 앱을 지우면 `state.vscdb` 도 함께 사라질 수 있고, 지운 SQLite 레코드를 되살리는 일반 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)에 있습니다. 서버 쪽 보관 기간은 공개 자료에 없어서 다른 서비스의 규칙으로 메우지 말고, 사건 당시의 약관과 trust.cursor.com 자료를 따로 확보합니다. 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 파일이 SQLite 인지는 첫 16바이트로 확인하고, 키 이름은 문자열 바이트로 찾습니다. 아래는 SQLite 명세와 문자 인코딩대로 만든 예시이고, 검체에서 뜬 바이트가 아닙니다.

```
만든 예시(명세로 만든 바이트)
파일 머리 "SQLite format 3\0"  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00
"composerData"  UTF-8           63 6F 6D 70 6F 73 65 72 44 61 74 61
"cursorDiskKV"  UTF-8           63 75 72 73 6F 72 44 69 73 6B 4B 56
```

할당되지 않은 영역이나 지운 페이지에서 키 문자열이 보이면 그 근처가 대화 레코드였을 수 있으니, 그 바이트 범위를 따로 떼어 SQLite 레코드 형식으로 풀어 봅니다.

**공개 도구로 한 번.** 수집한 사본에서 sqlite3 명령줄 도구로 표와 키 목록부터 봅니다. 경로는 만든 예시이고, 원본이 아니라 사본에서만 돌립니다.

```sh
# 만든 예시 경로
DB=/cases/case-0001/copy/workspace-a1b2/state.vscdb
sqlite3 "$DB" ".tables"
sqlite3 "$DB" "SELECT key, length(value) FROM ItemTable WHERE key LIKE 'aiService.%' OR key LIKE 'workbench.panel.aichat%';"
sqlite3 "$DB" "SELECT key, length(value) FROM cursorDiskKV WHERE key LIKE 'composerData%';"

# 훅 설정의 이벤트와 명령만 뽑기
jq '.hooks | to_entries[] | {event: .key, commands: [.value[].command]}' /cases/case-0001/copy/alice/.cursor/hooks.json
```

값을 열어 볼 때는 먼저 길이와 첫 글자로 형식을 가늠하고, 제3자 도구(cursor-chat-export 등)는 2025년 중반 구조를 기준으로 만들었다는 점을 보고서에 적습니다.

## 교차 검증

에이전트가 실제로 한 일은 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)의 흐름으로 git 이력·셸 기록과 맞춰 보고, 외부 문서가 에이전트를 부추긴 정황이 있으면 [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md)으로 이어 갑니다. VS Code 에서 쓰는 [GitHub Copilot](github-copilot/index.md)이나 역시 훅을 쓰는 [Claude Code](claude-code/index.md)가 같은 PC 에 함께 있으면 흔적이 섞이지 않게 도구별로 나눕니다. 서비스 접속 시각은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)과, 회사가 허용한 도구인지는 [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md)와 함께 봅니다. 수집 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다.

## 실습

공개 검체에 Cursor 흔적이 들어 있는지는 확인하지 못했습니다. 시험용 가상 머신과 시험 계정으로 풀어 봅니다.

1. 작업 공간 두 개를 열어 각각 채팅과 에이전트를 한 번씩 쓴 뒤, `state.vscdb` 가 몇 개 생겼고 어느 폴더에 있는지 적어 봅니다.
2. `ItemTable`, `cursorDiskKV` 의 키 목록을 뽑아 제3자 도구가 읽는 키가 지금 버전에도 있는지 비교합니다.
3. `beforeShellExecution` 훅에 입력을 파일로 적는 스크립트를 걸고, 에이전트에게 명령을 시킨 뒤 훅 기록과 대화 기록의 시각을 맞춰 봅니다.
4. 앱 버전을 적고, 한 달 뒤 같은 실습을 되풀이해 달라진 점을 비교합니다.

## 참고 문헌

1. Cursor Docs — Hooks — https://cursor.com/docs/agent/hooks
2. Cursor Docs — Model Context Protocol (MCP) — https://cursor.com/docs/context/mcp
3. Cursor — Security — https://cursor.com/security
4. somogyijanos/cursor-chat-export (GitHub, 2025-06-17 보관 처리) — https://github.com/somogyijanos/cursor-chat-export
