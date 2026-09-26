---
title: "설정·권한·훅"
parent: "Claude Code"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 590
---

# 설정·권한·훅 (Settings·Permissions·Hooks)

Claude Code 의 설정 파일에는 에이전트가 묻지 않고 실행해도 되는 명령(권한 규칙)과 특정 순간에 자동으로 도는 명령(훅)이 적혀 있어서, 사고 조사에서 "에이전트가 무엇을 할 수 있었나" 와 "사람 모르게 무엇이 돌았나" 를 가르는 근거가 됩니다. 같은 폴더의 `backups/` 에는 전역 상태 파일의 사본이 남아서 로그인한 계정과 프로젝트별 사용량까지 알려 줍니다.

Claude Code 판이 바뀌면 설정 키가 달라질 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

설정은 여러 파일에 나뉘어 있고, 위에 있는 것이 아래 것을 이깁니다[1]. 권한 규칙은 도구 호출마다 "묻기 / 허용 / 거부" 를 정하고[7], 훅은 도구를 부르기 전·후나 세션 시작·끝 같은 순간에 명령이나 HTTP 요청을 실행합니다[2]. 설치만으로는 설정 파일이 생기지 않습니다. `~/.claude/settings.json` 은 `/config` 에서 값을 바꿀 때, 프로젝트의 `.claude/settings.local.json` 은 "다시 묻지 않기" 로 허용하거나 팁 표시 같은 일부 `/config` 값을 바꿀 때 처음 생깁니다[4]. 사람이 손으로 만들 수도 있지만, 파일이 있다는 사실 자체가 누군가 설정을 바꾸거나 허용을 눌렀다는 흔적이 됩니다.

전역 상태 파일 `~/.claude.json` 은 이 우선순위와 따로 있고, 로그인 세션과 MCP 서버 설정, 프로젝트별 신뢰 결정을 담습니다[4]. Claude Code 는 이 파일을 쓰기 전에 사본을 `~/.claude/backups/` 에 남겨서[4], 사본에서 로그인 계정과 프로젝트별 비용·토큰 수를 읽을 수 있습니다[9].

## 위치와 버전별 차이

| 순위 | 파일 | 쓰는 사람·생기는 때 |
|---|---|---|
| 1 | 관리 정책 | 조직 관리자. 위치는 [Windows](windows.md), [macOS](macos.md) 페이지, Linux·WSL 은 `/etc/claude-code/`[5] |
| 2 | 명령줄 `--settings` | 실행할 때 넘긴 값(파일로 남지 않을 수 있음)[1] |
| 3 | `.claude/settings.local.json` | 프로젝트 안의 개인 설정. Claude Code 가 만들면 전역 git 제외 목록에 넣음[1][4] |
| 4 | `.claude/settings.json` | 프로젝트 공용 설정. 저장소에 커밋할 수 있음[1] |
| 5 | `~/.claude/settings.json` | 사용자 설정[1] |

우선순위와 따로 보는 파일은 다음과 같습니다.

| 경로 | 내용 | 근거 |
|---|---|---|
| `~/.claude.json` | 로그인 세션, MCP 서버 설정, 프로젝트별 신뢰 결정 | 문서[4] |
| `~/.claude/backups/.claude.json.backup.<시각>` | `~/.claude.json` 을 쓰기 전에 남긴 사본, 최근 5개 | 문서[4], ccfx 코드[9] |
| `~/.claude/backups/.claude.json.corrupted.<시각>` | `~/.claude.json` 이 깨졌을 때 옮겨 둔 사본 | 문서[4] |
| `~/.claude/remote-settings.json`, `~/.claude/policy-limits.json` | 서버 관리 설정의 캐시, 로그아웃할 때 지움 | 문서[5] |
| `~/.claude/.credentials.json` | 로그인 토큰. ccfx 는 있는지와 크기·수정 시각만 봄 | ccfx 문서[9] |

`backups/` 는 `cleanupPeriodDays` 청소 대상이라 오래된 사본은 남아 있지 않을 수 있고, 청소 목록 전체는 [세션 기록 구조](transcripts.md)에 있습니다. Windows 의 Claude Code 는 판에 따라 `history.jsonl`, `shell-snapshots/`, `paste-cache/`, `file-history/` 를 쓰지 않을 수 있습니다[10].

설정 파일을 고치면 실행 중인 세션이 바로 다시 읽고, 파일이 바뀔 때마다 `ConfigChange` 훅이 돕니다(MDM 이나 콘솔로 바꾼 관리 정책은 제외)[2]. 지금 어떤 관리 소스가 적용 중인지는 `/status` 의 `Setting sources` 줄에 나옵니다[5].

## 구조

### 사용자 설정 키

`~/.claude/settings.json` 에는 `permissions.allow`, `hooks` 아래 이벤트별 `matcher` 와 `hooks`, `enabledPlugins`, `extraKnownMarketplaces` 아래 이름별 `source.repo` 와 `source.source`, `autoMode.environment`, `autoUpdatesChannel`, `effortLevel`, `modelSettings` 아래 모델별 `effortLevel`, `theme` 같은 키가 들어갑니다. 훅 이벤트 키로는 `Notification`, `PermissionRequest`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `SessionEnd`, `Stop`, `StopFailure`, `SubagentStart`, `SubagentStop`, `TeammateIdle`, `UserPromptSubmit` 같은 것이 쓰입니다. `extraKnownMarketplaces` 의 `source.repo` 에는 저장소 이름이 들어 있어서, 외부 플러그인을 어디서 받아 왔는지 따라갈 때 출발점으로 씁니다.

아래는 키 이름만 실제와 같고 값은 새로 만든 예시입니다.

```json
{
  "permissions": {
    "allow": ["Bash(npm run lint)", "WebFetch(domain:docs.example.org)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(./secrets/**)"],
    "defaultMode": "default"
  },
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit", "hooks": [ { "type": "command", "command": "C:\\team-tools\\record-edit.cmd" } ] }
    ]
  },
  "cleanupPeriodDays": 30
}
```

### 권한

규칙은 `permissions.allow`, `ask`, `deny` 세 목록에 들어가고, deny → ask → allow 순서로 따져 먼저 맞은 것이 이깁니다[7]. 구체적인 allow 가 넓은 deny 를 이기지 못해서, deny 에 걸린 도구 호출이 기록에 성공으로 남아 있다면 그 시점의 설정이 지금과 달랐는지 먼저 의심합니다. 규칙은 `Bash(npm run build)`, `Bash(npm run *)`, `Read(./.env)`, `Edit(docs/**)`, `WebFetch(domain:example.com)` 같은 모양입니다[7]. 경로 앞의 `//` 는 파일 시스템 루트, `~/` 는 홈, `/` 하나는 그 규칙을 담은 설정 파일의 위치이고, 아무것도 없거나 `./` 이면 현재 폴더 기준입니다[7]. Windows 경로는 비교하기 전에 `C:\Users` 가 `/c/Users` 가 되는 식으로 바꿔 읽어서, Windows 에서 쓴 규칙도 이 모양으로 적혀 있을 수 있습니다[7].

"Yes, and don't ask again" 으로 영구 허용한 Bash 명령, WebFetch 도메인, WebSearch 는 `.claude/settings.local.json` 의 allow 규칙으로 남습니다[7]. Windows 에서 이 파일이 생기는 폴더는 [Windows](windows.md) 페이지에 있습니다. 파일 편집 허용은 세션이 끝나면 사라지고 파일에 남지 않아서[7], 편집을 허용한 흔적은 설정 파일이 아니라 [세션 기록](transcripts.md)에서 찾습니다.

권한 모드는 `default`(v2.1.200 부터 화면 이름 Manual, 별칭 `manual`), `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` 가 있고, 시작 모드는 `defaultMode` 키로 정합니다[7]. `bypassPermissions` 는 `.git`, `.claude` 같은 보호 경로에 쓸 때도 묻지 않습니다[7]. 조직은 `permissions.disableBypassPermissionsMode` 와 `permissions.disableAutoMode` 를 `"disable"` 로 두어 이 모드들을 막을 수 있습니다[7]. 세션 기록 줄에는 `permissionMode` 키가 있어서 그 시점의 모드를 볼 수 있지만, 값이 위 이름과 같은지는 검체에서 확인합니다. 데스크톱 앱에서 시작한 Cowork 세션은 메타데이터 파일에도 `permissionMode` 와 `remoteMcpServersConfig` 가 남고[10], 그 파일의 위치는 [Claude](../../chat-services/claude/index.md) 페이지에 있습니다.

### 훅

훅 이벤트는 다음과 같습니다[2].

```
SessionStart, Setup, UserPromptSubmit, UserPromptExpansion, PreToolUse,
PermissionRequest, PermissionDenied, PostToolUse, PostToolUseFailure,
PostToolBatch, Notification, MessageDisplay, SubagentStart, SubagentStop,
TaskCreated, TaskCompleted, Stop, StopFailure, TeammateIdle,
InstructionsLoaded, ConfigChange, CwdChanged, DirectoryAdded, FileChanged,
WorktreeCreate, WorktreeRemove, PreCompact, PostCompact, PreModelSwitch,
PostModelSwitch, Elicitation, ElicitationResult, SessionEnd
```

훅은 `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, 관리 정책, 플러그인의 `hooks/hooks.json`, 스킬 머리말, 하위 에이전트 머리말에 둘 수 있고, 종류는 `command`, `http`, `mcp_tool`, `prompt`, `agent` 입니다[2]. 훅은 `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name` 을 입력으로 받고(하위 에이전트면 `agent_id`, `agent_type` 도), Claude Code 의 환경 변수를 물려받습니다[2]. `PreToolUse`, `UserPromptSubmit`, `Stop` 등에서 종료 코드 2 를 돌려주면 그 동작을 막고, 0 이면 통과시킵니다[2].

훅은 시작할 때 고정되지 않고, 설정 파일을 고치면 파일 감시로 바로 반영됩니다[2]. 프로젝트 설정의 훅은 작업 폴더 신뢰 대화상자를 통과한 뒤에 돌고, 신뢰 결정은 `~/.claude.json` 의 프로젝트별 상태에 남습니다[2][4]. `disableAllHooks: true` 로 훅을 끌 수 있지만 관리 정책의 훅은 밖에서 끌 수 없고, `allowManagedHooksOnly` 를 켜면 관리 정책의 훅만 돕니다[2]. HTTP 훅이 보낼 수 있는 주소는 `allowedHttpHookUrls` 로 제한합니다[2].

저장소에 커밋된 `.claude/settings.json` 의 훅은 그 저장소를 열고 신뢰한 사람의 PC 에서 명령을 실행합니다. 그래서 사고 조사에서는 사용자 폴더뿐만 아니라 사건과 관련된 저장소 안의 `.claude/` 폴더와 그 git 이력까지 확인 대상에 넣습니다. 훅이 실제로 돌았는지는 세션 기록의 `hookInfos[].command`, `attachment.hookEvent`, `attachment.exitCode` 같은 키에서 봅니다([세션 기록 구조](transcripts.md)).

### 관리 정책의 순서

관리 소스는 서버 관리 설정(claude.ai 관리 콘솔), MDM·HKLM·plist, 파일, HKCU 순서로 따집니다[5]. 기본으로는 정책 키가 있는 첫 소스만 쓰고, 가장 높은 소스에 `managedSourcesBehavior: "merge"` 를 두면 여러 소스를 합칩니다[5]. HKCU 는 사용자가 쓸 수 있는 위치라 관리자 소스로 치지 않습니다[5]. 서버 관리 설정은 시작할 때 받고 한 시간마다 다시 확인하고, MDM 과 HKCU 는 시작할 때 읽고 30분마다 바뀌었는지 확인합니다[5]. 관리 정책 파일은 `managed-settings.json`, `managed-settings.d/` 아래 JSON 파일들, `managed-mcp.json` 으로 나뉩니다[5].

### 인증 설정

인증은 클라우드 공급자 변수, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_API_KEY`, `apiKeyHelper`, `CLAUDE_CODE_OAUTH_TOKEN`, Anthropic 프로필, `/login` 구독 로그인 순서로 따지고, `ant auth login` 으로 만든 프로필은 이름을 지정하지 않으면 `/login` 보다 뒤로 갑니다[6]. 환경 변수로 인증했다면 로그인 파일이 없어도 쓸 수 있어서, 사용자·시스템 환경 변수와 셸 설정 파일도 함께 봅니다. `apiKeyHelper` 는 셸 스크립트를 실행해 키를 받아 오고 기본 5분마다 다시 실행하므로[6], 설정에 이 키가 있으면 가리키는 스크립트도 함께 확보합니다. `claude setup-token` 은 1년짜리 토큰을 화면에 출력만 하고 저장하지 않으며, `/logout` 은 로그인 정보를 지우고 처음 설정 상태로 되돌립니다[6]. 키와 토큰이 남는 곳과 보고서에서 가리는 방법은 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에, 에이전트가 자격 증명에 손댔는지 보는 흐름은 [에이전트가 자격 증명을 건드렸나](../../../04-scenarios/agents/agent-credentials.md)에 있습니다.

### `backups/` 사본에 남는 계정·사용량

ccfx 는 `backups/` 에서 이름이 `.claude.json.backup.` 으로 시작하는 파일을 모아 이름순으로 정렬하고, 가장 마지막 파일 하나만 JSON 으로 읽습니다[9]. 그 파일에서 읽는 키는 두 묶음입니다.

| 위치 | 키 | ccfx 가 쓰는 곳 |
|---|---|---|
| `oauthAccount` | `accountUuid`, `emailAddress`, `organizationUuid`, `organizationName`, `organizationType`, `organizationRole`, `organizationRateLimitTier`, `userRateLimitTier` | 보고서의 사용자 신원 절. 등급은 `userRateLimitTier` 가 비어 있으면 `organizationRateLimitTier` 를 씀 |
| `projects` 아래 프로젝트 경로별 | `lastCost`, `lastTotalInputTokens`, `lastTotalOutputTokens`, `lastTotalCacheCreationInputTokens`, `lastTotalCacheReadInputTokens` | 프로젝트별 비용(달러)과 토큰 수 |

ccfx 코드는 `projects` 항목의 `lastSessionFirstPrompt`, `lastSessionModified` 키도 정의하지만 보고서에 쓰지 않습니다[9]. `lastSessionFirstPrompt` 에는 키 이름으로 보아 마지막 세션의 첫 입력이 들어갈 수 있으므로, 검체에서 값이 있는지 직접 확인합니다. `backups/` 의 OAuth 계정 묶음은 신원을 드러냅니다[10].

아래는 키 이름만 실제와 같고 값은 모두 새로 만든 예시입니다.

```json
{
  "oauthAccount": {
    "accountUuid": "00000000-1111-2222-3333-444444444444",
    "emailAddress": "user01@example.org",
    "organizationUuid": "55555555-6666-7777-8888-999999999999",
    "organizationName": "Example Org",
    "organizationType": "example_type",
    "organizationRole": "member"
  },
  "projects": {
    "/home/user01/repo01": {
      "lastCost": 1.25,
      "lastTotalInputTokens": 1200,
      "lastTotalOutputTokens": 3400
    }
  }
}
```

사본은 `~/.claude.json` 을 쓰기 전에 남긴 것이라[4], 같은 키가 지금의 `~/.claude.json` 에도 있을 수 있습니다. 사본이 여러 개면 계정이나 조직이 사본 사이에서 바뀌었는지, 프로젝트 목록이 언제 늘었는지를 비교할 수 있습니다. 이메일과 계정·조직 UUID 는 개인 정보라서 보고서에서는 가립니다. ccfx 의 `--redact-pii` 가 이메일과 UUID 를 가립니다[9].

### 원격 측정

조직은 `CLAUDE_CODE_ENABLE_TELEMETRY=1` 과 `OTEL_*` 환경 변수로 OpenTelemetry 수집기에 이벤트를 모을 수 있습니다[8]. 이벤트는 `claude_code.user_prompt`, `assistant_response`, `tool_result`, `tool_decision`, `api_request`, `api_error` 이고, 공통 속성으로 `session.id`, `organization.id`, `user.account_uuid`, `user.email`, `terminal.type`, `app.entrypoint` 가 붙습니다[8]. `claude_code.tool_decision` 의 `source` 값은 `config`, `hook`, `user_permanent`, `user_temporary`, `user_abort`, `user_reject` 라서[8], 도구 호출을 설정이 허용했는지 사람이 눌러 허용했는지 가를 수 있습니다.

프롬프트, 응답, 도구 인자, 도구 출력은 기본으로 가려지고 `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_ASSISTANT_RESPONSES`, `OTEL_LOG_TOOL_DETAILS`, `OTEL_LOG_TOOL_CONTENT` 로 켜야 남습니다[8]. 사용량 지표에는 코드·프롬프트·파일 경로가 들어가지 않습니다[8]. 반대로 `DISABLE_TELEMETRY=1`, `DISABLE_ERROR_REPORTING=1`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 을 켜면 원격 측정과 오류 보고, 필수가 아닌 통신이 꺼집니다[3]. WebFetch 는 가져오기 전에 호스트 이름만 `api.anthropic.com` 에 보내 차단 목록을 확인하고, `skipWebFetchPreflight` 로 끕니다[3]. 네트워크 쪽 흔적은 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)과 함께 봅니다.

## 증거로서 의미

**증명하는 것.** 설정 파일은 수집한 시점에 어떤 명령이 허용·거부 목록에 있었고 어떤 훅이 걸려 있었는지 보여 줍니다. `settings.local.json` 의 allow 규칙은 누군가 그 명령을 "다시 묻지 않기" 로 허용했거나 손으로 적어 넣은 흔적이고, 저장소에 커밋된 훅은 git 이력으로 언제 누가 넣었는지까지 따라갈 수 있습니다. `backups/` 사본의 `oauthAccount` 는 사본을 남긴 때에 이 사용자 프로필의 Claude Code 가 어느 계정·조직으로 로그인해 있었는지 보여 주고, `projects` 는 그 계정으로 Claude Code 를 쓴 작업 폴더와 마지막 세션의 비용·토큰 수를 보여 줍니다.

**증명하지 못하는 것.** 설정 파일은 지금 상태만 담아서 사건 당시에도 같았다고 말해 주지 않고, 규칙을 누가 눌러 허용했는지도 알려 주지 않습니다. 훅이 걸려 있었다는 사실이 훅이 돌았다는 뜻은 아니어서, 실행 여부는 세션 기록이나 원격 측정에서 따로 확인합니다. 명령줄 `--settings` 로 넘긴 값과 환경 변수는 파일에 남지 않을 수 있습니다. 로그인 계정이 남았다고 해서 그 계정 주인이 키보드 앞에 있었다는 뜻은 아니고, 누가 입력했는지는 로그인 기록·세션 시각 같은 다른 흔적과 맞춰 봅니다. `lastCost` 같은 값은 마지막 세션 기준이라 그 프로젝트에서 쓴 전체 사용량이 아닙니다.

## 시각 해석

사용자 설정 파일의 키에는 시각 값이 없습니다. 설정이 언제 바뀌었는지는 파일 시스템의 마지막 쓰기 시각, `backups/` 의 파일 이름에 붙은 시각, 저장소의 git 커밋 시각, 세션 기록의 `permissionMode` 가 바뀐 줄의 시각으로 가늠합니다. 설정 파일은 고칠 때마다 통째로 다시 쓰일 수 있어서, 마지막 쓰기 시각은 마지막 변경만 알려 줍니다.

`backups/` 사본 이름에 붙은 시각과 `projects` 아래 `lastSessionModified` 값의 형식·시간대는 공개된 명세가 없어서 검체에서 확인해야 합니다. ccfx 코드는 `lastSessionModified` 를 형식을 정하지 않은 JSON 값(`json.RawMessage`)으로 받기만 합니다[9]. 사본 이름의 시각을 파일 시스템의 생성·수정 시각과 나란히 놓으면 어떤 형식인지 가늠할 수 있습니다.

## 함정과 한계

우선순위가 높은 파일 하나가 아래 파일의 규칙을 덮기 때문에, 한 파일만 보고 "허용돼 있었다" 고 쓰지 않습니다. HKCU 정책 값은 사용자가 직접 쓸 수 있는 위치라서 조직 정책의 근거로 삼지 않습니다.

훅은 플러그인과 스킬·하위 에이전트 머리말에도 있을 수 있어서, 설정 파일 네 곳만 보면 빠뜨립니다. `/hooks` 메뉴는 훅과 그 출처(User, Project, Local, Plugin, Session)를 읽기 전용으로 보여 주지만[2], 살아 있는 시스템에서 앱을 켜야 볼 수 있습니다.

ccfx 는 이름순으로 가장 마지막 사본 하나만 읽어서[9], 그보다 앞선 사본에 다른 계정이 남아 있어도 보고서에는 나오지 않습니다. 사본은 모두 따로 열어 봅니다. ccfx 의 `-ac` 옵션이 만드는 수집 압축 파일에는 `.credentials.json` 이 평문 그대로 들어가고 `--redact-pii` 도 적용되지 않으므로[9], 그 파일은 토큰이 든 증거물로 다룹니다.

## 직접 분석해 보기

설정 파일과 `backups/` 사본은 평문 JSON 이라 헥스로 볼 때의 요령은 [Windows](windows.md) 페이지 예시와 같습니다. 여기서는 사본을 jq 로 읽습니다. 아래 경로는 만든 예시입니다.

```sh
# 만든 예시: 사본을 푼 폴더
CASE=/mnt/case01/Users/examiner01
jq '.permissions' "$CASE/.claude/settings.json"
jq -r '.hooks | to_entries[] | .key as $e | .value[] | .hooks[] | [$e, .type, (.command // .url // "")] | @tsv' "$CASE/.claude/settings.json"
# backups 사본마다 계정·조직과 프로젝트 목록 뽑기
for f in "$CASE"/.claude/backups/.claude.json.backup.*; do
  jq -r --arg f "$(basename "$f")" '[$f, .oauthAccount.emailAddress, .oauthAccount.organizationUuid, ((.projects // {}) | keys | length)] | @tsv' "$f"
done
# 저장소 안의 .claude 폴더를 모두 찾기
find /mnt/case01 -type d -name .claude 2>/dev/null
```

공개 도구로는 ccfx 가 `--path` 로 받은 `.claude` 폴더를 읽어, 가장 마지막 사본의 계정 정보를 보고서의 사용자 신원 절에 넣습니다[9]. 예: `ccfx --path /mnt/case01/Users/examiner01/.claude --format json --redact-pii --output ./ccfx-out`. ccfx 는 `commands/` 의 사용자 명령 `.md` 파일 수와 `plans/` 의 계획 `.md` 파일 수도 셉니다[9].

## 교차 검증

설정의 허용 규칙과 훅은 [세션 기록 구조](transcripts.md)의 도구 호출, 훅 실행 흔적과 맞춰 보고, 저장소 쪽 `.claude/` 는 git 이력과 함께 봅니다. `backups/` 사본의 계정은 [Claude](../../chat-services/claude/index.md) 데스크톱 앱 폴더의 계정 식별값과, 조직 쪽 기록은 [Claude 기업용 감사 로그](../../network-enterprise/claude-enterprise.md)와 맞춰 봅니다. MCP 서버 설정은 [MCP 서버와 도구 호출 기록](../mcp.md)과, 외부 문서가 훅이나 설정 변경을 부추긴 흔적은 [프롬프트 인젝션 사고 분석](../../../03-techniques/analysis/prompt-injection.md)과 이어 봅니다. 조직이 허용하지 않은 도구 사용인지는 [회사가 허용하지 않은 AI를 썼나](../../../04-scenarios/data-leak/shadow-ai.md)의 흐름을 따릅니다. 계정의 서버 쪽 기록은 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)으로 받습니다.

## 실습

시험용 가상 머신에 Claude Code 를 깔고 풀어 봅니다.

1. 설치 직후와 "다시 묻지 않기" 를 한 번 누른 뒤의 `.claude` 폴더를 비교해, 새로 생긴 파일과 규칙 모양을 적습니다.
2. 사용자 설정에 `allow`, 프로젝트 설정에 같은 명령의 `deny` 를 두고 세션 기록에 무엇이 남는지 봅니다.
3. 가짜 저장소의 `.claude/settings.json` 에 파일에 한 줄 적기만 하는 `PostToolUse` 훅을 넣고, 신뢰 대화상자 전후로 훅이 도는지와 세션 기록의 훅 흔적을 비교합니다.
4. 두 계정으로 번갈아 로그인한 뒤 `backups/` 사본마다 `oauthAccount.emailAddress` 를 뽑아, 사본 이름의 시각과 로그인 순서가 맞는지 봅니다.
5. 새 폴더에서 세션을 하나 연 뒤 사본의 `projects` 에 그 경로가 언제 나타나는지, `lastSessionModified` 가 어떤 형식인지 적습니다.

## 참고 문헌

1. Settings files and precedence — https://code.claude.com/docs/en/settings
2. Hooks reference — https://code.claude.com/docs/en/hooks
3. Data usage — https://code.claude.com/docs/en/data-usage
4. .claude 폴더 파일·폴더 참조(claude-directory) — https://code.claude.com/docs/en/claude-directory
5. Deploy managed settings — https://code.claude.com/docs/en/managed-settings
6. Authentication — https://code.claude.com/docs/en/authentication
7. Configure permissions — https://code.claude.com/docs/en/permissions
8. Monitoring (OpenTelemetry) — https://code.claude.com/docs/en/monitoring-usage
9. fkasasagi, ccfx(마지막 커밋 2026-08-18) — https://github.com/fkasasagi/ccfx (`README.en.md`, `collector/backups.go`, `collector/misc.go`)
10. forensicdave, claude-forensics v0.1.1(마지막 커밋 2026-06-16) — https://github.com/forensicdave/claude-forensics (`README.md`, `docs/claude_forensics.md`)
