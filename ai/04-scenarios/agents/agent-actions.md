---
title: "AI 에이전트가 무엇을 실행했나"
parent: "시나리오 · AI 에이전트"
nav_order: 880
---

# AI 에이전트가 무엇을 실행했나 (Agent Actions)

> 확인 범위: 공식 문서는 2026-09-25 에 열어 본 내용입니다. "(확인 범위: Windows 11, 2026-09)" 가 붙은 내용은 Windows 11 PC 한 대에서 폴더를 읽기 전용으로 열어 파일 이름과 키 이름만 확인한 것이고, 값은 시각 값의 자릿수와 모양 말고는 읽지 않았습니다. AI 개발 도구는 판이 자주 바뀌어서 검체의 도구 버전을 먼저 확인하고 이 페이지와 맞춰 봅니다.

## 조사 질문

AI 에이전트(AI agent)가 사용자 컴퓨터에서 어떤 명령을 실행하고 어떤 파일을 읽거나 고쳤는지, 그 일을 사람이 시켰거나 승인했는지를 밝히는 조사입니다. 사고 대응에서는 "에이전트가 이 폴더를 지웠나", "이 명령은 사람이 쳤나 에이전트가 만들었나", "그때 자동 승인이 켜져 있었나" 같은 물음으로 나옵니다.

이 페이지는 사용자 컴퓨터에서 도는 개발 도구 에이전트(Claude Code·Codex CLI·Gemini CLI·Cursor)와 데스크톱 앱의 에이전트 기능을 다룹니다. 웹 브라우저 안이나 서비스 회사 서버에서 도는 에이전트는 [ChatGPT 에이전트 모드](../../02-artifacts/agentic-services/chatgpt-agent.md)와 [브라우저를 조작하는 AI](../../02-artifacts/agentic-services/browser-agents.md)에서 다룹니다. Android·iOS 앱에서 에이전트가 실행한 기록은 이 페이지를 쓸 때 확인한 자료가 없어서 다루지 않습니다.

## 먼저 확인할 것

- **OS 와 사용자 계정**: 여기서 다루는 도구는 모두 사용자 홈 폴더 아래에 기록을 둡니다. macOS·Linux 에서는 `~/.claude`, `~/.codex`, `~/.gemini`, `~/.cursor` 이고, Windows 에서는 같은 이름의 폴더가 `%USERPROFILE%` 아래에 생깁니다(확인 범위: Windows 11, 2026-09). 기록은 계정마다 따로 쌓이고, PC 에 있는 사용자 폴더를 모두 확인합니다. Codex 는 `CODEX_HOME` 환경 변수로 폴더를 옮길 수 있어서, 기본 위치 `~/.codex` 에 없으면 환경 변수 설정부터 찾습니다.
- **도구 버전**: Claude Code 세션 기록은 줄마다 `version` 키를 적고(확인 범위: Windows 11, 2026-09), Cursor 훅이 받는 입력에는 `cursor_version` 이 들어갑니다. 같은 도구라도 판에 따라 저장 위치가 바뀝니다. 예를 들어 Claude Code 는 v2.1.274 까지 첨부 이미지를 `~/.claude/image-cache/<session>/` 에 두었고, 그 뒤 판은 `~/.claude` 밖의 임시 폴더 아래 세션별 `images/` 에 둡니다.
- **시각 형식과 시간대**: Claude Code 의 `history.jsonl` 은 `timestamp` 를 13자리 정수(유닉스 밀리초)로 적고, 세션 기록은 끝에 `Z` 가 붙은 ISO 8601 문자열(UTC)로 적습니다(확인 범위: Windows 11, 2026-09). 다른 판이나 다른 도구의 기록이면 정수는 자릿수로 초인지 밀리초인지 가리고, 문자열은 끝에 시간대 표시가 붙었는지 확인한 뒤 한 기준으로 맞춥니다. 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.
- **수집 범위**: 세션 기록 옆에 하위 에이전트 기록과 큰 도구 출력이 따로 있어서 도구 폴더를 통째로 모읍니다. Windows 스토어판 Claude 데스크톱 앱은 `%LOCALAPPDATA%\Packages\<Claude 패키지>\LocalCache` 에 데이터를 둡니다(확인 범위: Windows 11, 2026-09). 수집 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다. 세션 기록에는 명령 출력과 파일 내용이 그대로 들어가서 비밀 값이 섞여 있을 수 있고, 다루는 방법은 [에이전트가 자격 증명을 건드렸나](agent-credentials.md)에 있습니다.
- **보관 기간 설정**: 기록이 없을 때 이유를 가리려면 당시 보관 설정을 알아야 합니다. Claude Code 는 `cleanupPeriodDays`(기본 30일), Claude 데스크톱 앱은 `desktopSessionCleanupPeriodDays`, Gemini CLI 는 `settings.json` 의 `sessionRetention`(기본 30일), Codex 는 `[history]` 절의 `persistence`·`max_bytes` 로 정합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | Claude Code 프롬프트 기록 `~/.claude/history.jsonl` | 사용자가 입력한 프롬프트마다 시각과 프로젝트 경로. 나이 기준으로 지우지 않아 사용자가 지울 때까지 남음 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 2 | Claude Code 세션 기록 `~/.claude/projects/<project>/<session>.jsonl` | 모든 메시지와 도구 호출, 도구 결과, 작업 폴더·브랜치·권한 모드 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 3 | 하위 에이전트 기록 `.../<session>/subagents/`, 큰 출력 `.../<session>/tool-results/` | 하위 에이전트가 따로 실행한 도구, 세션 기록에 다 담지 않은 출력 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 4 | 수정 전 사본 `~/.claude/file-history/<session>/` | Claude Code 가 고친 파일의 수정 전 내용(최근 체크포인트 100개분) | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 5 | 설정 `settings.json` 의 `permissions`·`hooks` | 당시 허용 규칙과 도구 실행 앞뒤에 걸린 훅 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 6 | Codex `~/.codex/history.jsonl`, `config.toml` | 기록과 당시 허용 범위(`sandbox_mode`, `approval_policy`) | [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md) |
| 7 | Gemini CLI `~/.gemini/tmp/<project_hash>/chats/` | 프롬프트·응답과 모든 도구 실행의 입력과 출력 | [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md) |
| 8 | Cursor `hooks.json`(사용자·프로젝트·기업) | 에이전트 동작을 기록하거나 막도록 훅을 걸었는지 | [Cursor](../../02-artifacts/dev-agents/cursor.md) |
| 9 | 데스크톱 앱 MCP 로그와 `claude_desktop_config.json` | MCP 서버 쪽 기록, 신뢰 폴더와 권한 확인 생략 동의 | [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md), [Claude](../../02-artifacts/chat-services/claude/index.md) |
| 10 | 사용 통계 `~/.claude/stats-cache.json` | 날짜별 도구 호출 수·메시지 수·세션 수. 명령 내용은 없음 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |

Claude Code 의 경로와 보관 규칙은 공식 문서를 따랐고, 키 이름은 Windows 11 PC 에서 확인했습니다(확인 범위: Windows 11, 2026-09). Codex 의 세션별 기록 폴더와 로그 파일 이름, Gemini CLI 세션 파일의 형식, Cursor 앱의 대화 DB 위치는 이 페이지를 쓸 때 확인하지 못했습니다.

## 분석 흐름

1. **도구와 기간을 좁힙니다.** 사용자 폴더마다 도구 폴더가 있는지 보고, 있으면 도구 버전과 보관 설정을 적어 둡니다. 관찰한 PC 에서는 `.claude` 에 파일이 1만 개 넘게 있었지만 `.codex` 에는 `hooks.json` 과 스킬 파일만, `.gemini` 에는 설정 파일만 있고 세션 폴더(`tmp/`)가 없었으며, `.cursor` 에는 `hooks.json` 하나만 있고 Cursor 앱 데이터 폴더가 없었습니다(확인 범위: Windows 11, 2026-09). 폴더가 있다는 사실과 실행 기록이 남아 있다는 사실은 따로 확인합니다.
2. **조사 기간의 세션을 고릅니다.** Claude Code 는 `history.jsonl` 의 `timestamp`·`project`·`sessionId` 로 기간 안의 세션을 찾고(확인 범위: Windows 11, 2026-09), 같은 이름의 세션 파일을 `projects/` 아래에서 엽니다. 이름이 `<session>.orphaned-<timestamp>-<suffix>.jsonl` 이나 `<session>.jsonl.superseded-<timestamp>` 인 파일도 같은 세션의 기록이라 함께 봅니다.
3. **도구 호출과 결과를 짝짓습니다.** 세션 기록의 `message.content[]` 에서 `name`·`input`·`id` 가 도구 호출을 나타내고, 같은 값을 `tool_use_id` 로 가리키는 항목의 `content`·`is_error` 가 결과입니다. 셸 명령이면 `toolUseResult` 의 `stdout`·`stderr`·`interrupted`·`success` 도 봅니다(확인 범위: Windows 11, 2026-09). 호출만 있고 짝이 되는 결과가 없으면 "실행 요청이 기록됐다" 까지만 씁니다.
4. **누가 시켰는지 따라갑니다.** `parentUuid` 를 거슬러 올라가 그 호출 직전의 사용자 메시지를 찾고, `history.jsonl` 에 같은 프롬프트가 있는지 대조합니다. 승인 여부는 줄마다 적힌 `permissionMode` 와 설정의 `permissions.allow` 목록으로 판단하고, 데스크톱 앱이면 `claude_desktop_config.json` 의 `preferences.localAgentModeTrustedFolders`, 계정별 `bypassPermissionsGateByAccount`·`bypassPermissionsOptInByAccount` 값도 봅니다(확인 범위: Windows 11, 2026-09). Codex 는 `config.toml` 의 `sandbox_mode`(예: `"workspace-write"`, `"danger-full-access"`)와 `approval_policy`(예: `"on-request"`, `"never"`)가 같은 역할을 합니다.
5. **하위 에이전트와 백그라운드 작업을 더합니다.** 관찰한 PC 에서 하위 에이전트 기록은 `projects/<이름>/<ID>/subagents/workflows/<이름>/` 아래에 따로 있었고 `agentId`·`attributionAgent` 키가 붙어 있었습니다. 백그라운드 작업은 `jobs/<이름>/state.json`(`cwd`, `intent`, `state`, `createdAt`, `updatedAt`, `sessionId`)과 `timeline.jsonl`(`at`, `state`, `detail`, `text`)에 상태가 남았습니다(확인 범위: Windows 11, 2026-09). 메인 세션 기록만 보면 이쪽 실행을 빠뜨립니다.
6. **훅 기록을 확인합니다.** 훅(hook)은 도구 실행 앞뒤에 사용자가 건 명령이고, 설정 파일에는 어떤 이벤트에 걸었는지만 남습니다. 실제로 돌았는지는 Claude Code 세션 기록의 `attachment.hookEvent`·`hookName`·`command`·`exitCode`·`stdout`·`stderr`·`durationMs`, 그리고 `hookErrors`·`preventedContinuation` 으로 봅니다(확인 범위: Windows 11, 2026-09). Cursor 훅은 종료 코드 2 일 때 막고 0 이면 성공이며 그 밖의 코드는 기본으로 통과시켜서, 훅이 오류로 끝났다면 동작이 막히지 않았을 수 있습니다. Codex 는 관리자 설정 `requirements.toml` 에 `allow_managed_hooks_only = true` 가 있으면 사용자·프로젝트·세션 훅을 무시하고 관리자 훅만 돌립니다.
7. **파일 변화와 맞춰 봅니다.** `file-history/<session>/` 의 수정 전 사본과 세션 기록의 `snapshot.trackedFileBackups` 로 어떤 파일이 바뀌었는지 보고, 대상 파일의 파일 시스템 시각이나 저장소 커밋 기록과 대조합니다. 어느 폴더와 브랜치에서 일했는지는 세션 기록의 `cwd`·`gitBranch` 로 알 수 있습니다(확인 범위: Windows 11, 2026-09).
8. **다른 도구도 같은 방식으로 봅니다.** Gemini CLI 는 세션에 "모든 도구 실행의 입력과 출력" 을 남기고, `<project_hash>` 가 프로젝트 루트 폴더에서 나온 값이라 폴더 단위로 묶입니다. Codex 는 OpenTelemetry 를 켠 환경이면 `codex.tool_decision`(승인·거부)과 `codex.tool_result`(실행 결과) 이벤트가 수집 서버에 남고, 사용자 프롬프트는 `log_user_prompt = true` 일 때만 내용이 들어갑니다. Cursor 는 훅이 받는 `command`·`cwd`·`file_path`·`tool_name`·`tool_input`·`tool_output` 을 훅 스크립트가 파일로 적어 두었는지 찾습니다. 훅 실행과 오류는 앱 화면(Hooks 탭과 출력 채널)에서 보이지만 파일로 남는지는 확인하지 못했습니다.
9. **기록이 없으면 이유를 가립니다.** 보관 기간이 지났거나, `claude project purge` 로 지웠거나(`projects/` 기록, 세션별 `tasks/`·`debug/`·`file-history/`, `history.jsonl` 의 해당 줄, `~/.claude.json` 의 프로젝트 항목이 함께 지워짐), `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켜서 처음부터 쓰지 않았을 수 있습니다. Gemini CLI 는 `--delete-session` 으로, Codex 는 `persistence = "none"` 으로 기록이 없을 수 있습니다. 세션 기록이 없어도 그날 도구 호출이 있었는지는 `stats-cache.json` 의 `dailyActivity[].toolCallCount` 로 알 수 있습니다(확인 범위: Windows 11, 2026-09).
10. **타임라인에 합칩니다.** 세션 기록의 시각을 파일 시스템·이벤트 로그·네트워크 기록과 한 줄로 세웁니다. 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)과 [Windows 판 타임라인 작성](https://urock-ailab.github.io/forensics-handbook-windows/03-techniques/analysis/timeline/index.html)을 봅니다.

## 흔한 오판

**도구 호출 기록을 실행 완료로 읽는 경우**가 가장 흔합니다. 호출 항목은 모델이 그 도구를 쓰겠다고 요청했다는 기록이고, 실행 결과는 짝이 되는 결과 항목과 `is_error`·`interrupted` 값으로 따로 확인합니다. 결과가 성공이어도 명령이 대상 파일에 무엇을 했는지는 파일 쪽 기록으로 확인합니다.

**명령을 사람이 입력했다고 보는 경우**도 있습니다. `history.jsonl` 과 사용자 메시지에는 사람이 입력한 프롬프트가 남고, 도구 호출의 `input` 에는 모델이 만든 명령이 남습니다. 둘을 섞으면 사용자가 "정리해 줘" 라고만 말한 일을 사용자가 삭제 명령을 쳤다고 쓰게 됩니다. 반대로 사람이 승인했는지는 권한 모드와 허용 규칙을 봐야 알 수 있어서, 모델이 만든 명령이라는 사실만으로 사용자 책임이 없다고 쓰지도 않습니다.

**하위 에이전트 기록을 빠뜨리는 경우**가 있습니다. 하위 에이전트와 백그라운드 작업은 메인 세션 파일 밖에 기록되어서, 메인 파일만 보면 실행 수가 적게 잡힙니다.

**훅 설정을 훅 실행으로 읽는 경우**도 있습니다. 설정 파일은 걸어 둔 훅만 보여 주고, 실제로 돌았는지와 결과는 세션 기록의 훅 항목에 있습니다.

**기록이 없으면 실행도 없었다고 보는 경우**는 위 9단계의 여러 이유 때문에 틀릴 수 있습니다. 특히 `history.jsonl` 은 나이 기준으로 지우지 않아서, 프롬프트 기록은 있는데 세션 기록만 없다면 보관 기간 정리나 삭제를 먼저 의심합니다.

**서버에 원본이 있을 것이라고 가정하는 경우**도 조심합니다. CLI 로 돌린 로컬 세션의 대화 원본이 서비스 회사 서버에 따로 남는지는 이 페이지를 쓸 때 확인하지 못했습니다. 서버 쪽 자료가 필요하면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)과 기업용 감사 로그([Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md))로 따로 확인합니다.

## 보고서 문장 예

아래는 만든 예시이고, 사용자 이름·폴더 이름·시각·건수는 모두 가짜 값입니다.

> 사용자 계정 `demo-user` 의 Claude Code 세션 기록 가운데 2026-08-14 01:02~01:37(UTC) 구간의 파일 1개에 도구 호출 12건과 각 호출에 짝이 되는 결과 항목 12건이 있습니다. 그중 1건의 입력에는 `C:\work\sample-shop\build` 폴더를 지우는 명령이 적혀 있고, 결과 항목에는 오류 표시가 없습니다. 이 호출 직전 사용자 메시지는 빌드 폴더 정리를 요청하는 내용이며, 같은 줄의 권한 모드 값과 설정 파일의 허용 목록은 부록에 적었습니다. 폴더가 실제로 지워진 시각은 세션 기록만으로는 확정할 수 없어 파일 시스템 기록으로 따로 확인했습니다.

> 같은 기간 `demo-user` 의 `stats-cache.json` 에는 2026-08-15 날짜에 도구 호출 수가 기록되어 있지만 그날의 세션 기록 파일은 없습니다. 기록으로는 그날 도구 호출이 있었다는 사실까지만 확인되고, 어떤 명령을 실행했는지는 확인되지 않습니다.

보고서 전체 틀은 [AI 관련 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)를 따릅니다.

## 함께 볼 페이지

- [에이전트가 자격 증명을 건드렸나](agent-credentials.md) — 세션 기록에 섞인 비밀 값과 도구 자체의 인증 정보
- [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md), [Cursor](../../02-artifacts/dev-agents/cursor.md) — 도구별 저장 구조
- [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md) — 외부 도구 서버 쪽 기록
- [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md) — 에이전트가 사용자 뜻과 다른 일을 한 경우
- [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md) — 기록이 없을 때의 해석
- [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html) — 데스크톱 앱 폴더 구조(Windows 판)

## 참고 문헌

1. Explore the .claude directory (Claude Code 문서) — https://code.claude.com/docs/en/claude-directory
2. docs/config.md (openai/codex GitHub) — https://github.com/openai/codex/blob/main/docs/config.md
3. Advanced configuration (Codex 문서) — https://learn.chatgpt.com/docs/config-file/config-advanced
4. Session management (google-gemini/gemini-cli GitHub 문서) — https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/session-management.md
5. Hooks (Cursor 문서) — https://cursor.com/docs/agent/hooks
