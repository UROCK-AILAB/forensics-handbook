---
title: "Claude macOS 앱"
parent: "Claude"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 170
---

# macOS 앱 (macOS)

macOS 의 Claude 데스크톱 앱은 `~/Library/Application Support/Claude/` 에 데이터를 두고, 이 폴더에는 MCP 설정뿐만 아니라 Cowork 세션의 메타데이터와 에이전트 대화 기록까지 남습니다. 일반 채팅 대화의 원본은 계정 서버에 있습니다.

Anthropic 은 Cowork 의 디스크 형식을 공개하지 않았습니다. 아래 폴더 구조는 공개 분석 도구의 구현 기준이라 앱 판에 따라 바뀔 수 있습니다[6].

## 무엇이 남나 · 왜 생기나

데스크톱 앱은 claude.ai 와 같은 계정으로 로그인해 쓰는 앱이라서 일반 채팅은 서버에 저장됩니다. 앱은 macOS 11(Big Sur) 이상에서 돌고, 다운로드 페이지에서 받은 파일을 열어 설치한 뒤 응용 프로그램(Applications) 폴더에서 실행하며, 업데이트는 앱 안에서 합니다[1].

앱은 Electron 앱이라서 사용자 데이터 폴더가 macOS 의 Electron 기본 위치인 `~/Library/Application Support/Claude` 에 생깁니다[6]. 로컬 MCP 서버를 연결하면 이 폴더에 설정 파일이, `~/Library/Logs/Claude` 에 연결 로그가 남습니다[2]. Cowork(로컬 에이전트 모드, local agent mode)로 일을 시키면 세션마다 메타데이터 JSON 과 대화 기록 JSON Lines 파일이 `local-agent-mode-sessions/` 아래에 쌓이고, `claude-code-sessions/` 아래에는 본문이 `~/.claude/projects/` 의 Claude Code 기록 파일에 있는 세션의 메타데이터만 남습니다[5]. 두 폴더 모두 계정 식별값을 폴더 이름으로 쓰고, Cowork 메타데이터에는 계정 이메일도 들어 있어서 사용자를 가릴 때도 씁니다[5].

## 위치와 버전별 차이

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `/Applications/` 아래의 앱 번들 | 설치한 앱 | 문서[1] |
| `~/Library/Application Support/Claude/claude_desktop_config.json` | 로컬 MCP 서버 설정 | 문서[2] |
| `~/Library/Logs/Claude/mcp.log` | MCP 연결과 실패 기록 | 문서[2] |
| `~/Library/Logs/Claude/mcp-server-서버이름.log` | 그 서버가 표준 오류로 낸 출력 | 문서[2] |
| `~/Library/Application Support/Claude/local-agent-mode-sessions/` | Cowork 세션 메타데이터와 대화 기록 | 도구[5][6] |
| `~/Library/Application Support/Claude/claude-code-sessions/` | 세션 메타데이터(본문은 `~/.claude/projects/`) | 도구[5] |
| `~/Library/Application Support/Claude/` 의 `cowork-enabled-cli-ops.json`, `config.json`, `buddy-tokens.json`, `ant-did` | 앱 설정·상태 파일 | 도구[5] |
| `~/Library/Application Support/Claude/vm_bundles/` | 큰 캐시 폴더(12GB 에 이르기도 함) | 도구[5] |
| 환경설정 도메인 `com.anthropic.claudefordesktop` | MDM 으로 내려받는 관리 설정 | 문서[3] |

claude-forensics 는 `-W` 옵션을 주면 macOS 에서 `~/Library/Application Support/Claude` 를 자동으로 찾아 읽고, 다른 OS 에서는 이 옵션을 거부하고 `-w` 로 경로를 직접 받습니다[5]. Windows 에서 같은 폴더는 설치 방식에 따라 `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude` 나 `%APPDATA%\Claude` 이고, Linux 에서는 `~/.config/Claude` 입니다[6]. Windows 쪽 폴더 모양과 앱 JSON 파일의 키는 [Windows 앱](windows.md)에서 다룹니다.

대화 기록이 어디에 있는지는 두 도구의 설명이 다릅니다. 2026-06 의 claude-forensics 는 Cowork 대화 기록을 세션 폴더 안의 `audit.jsonl` 에서 읽고, `cliSessionId` 가 가리키는 기록은 `~/.claude/projects/` 에서 찾습니다[5]. 2026-09 의 agentsview 는 세션 폴더 안의 `.claude/projects/` 에서 `cliSessionId` 이름의 기록 파일을 찾고, `audit.jsonl` 은 읽지 않습니다[6]. 앱 판에 따라 한쪽만 있거나 둘 다 있을 수 있으므로 검체에서 두 위치를 모두 봅니다.

## 구조

### Cowork 세션: `local-agent-mode-sessions/`

두 도구가 읽는 폴더 모양은 다음과 같습니다(`sid` 는 세션 UUID)[5][6]. claude-forensics 는 `org`·`account` 두 단계를 `orgUuid`·`accountUuid` 라고 부르고[5], agentsview 코드 주석은 `orgId`·`workspaceId` 라고 부릅니다[6].

```
local-agent-mode-sessions/
├── skills-plugin/                         세션 저장소가 아님(두 도구 모두 건너뜀)
└── org/account/
    ├── spaces.json                        이 계정의 공간(space) 목록
    ├── local_sid.json                     세션 메타데이터
    └── local_sid/                         세션 작업 폴더
        ├── audit.jsonl                    에이전트 대화 기록 [5]
        └── .claude/projects/인코딩된폴더/
            ├── cliSessionId.jsonl         Claude Code 형식 대화 기록 [6]
            └── cliSessionId/subagents/**/agent-id.jsonl   하위 에이전트 기록 [6]
```

세션 작업 폴더(`local_sid/`) 아래에는 `.claude/outputs` 같은 큰 하위 폴더가 있고, 메타데이터 파일 옆에는 `cowork-clientdata-cache.json`·`cowork_settings.json` 같은 캐시 파일이 함께 있습니다[6]. 그래서 agentsview 는 `local_` 로 시작하고 `.json` 으로 끝나며 이름이 세션 ID 형식에 맞는 파일만 메타데이터로 봅니다. 인코딩된 폴더 이름은 판마다 달라서, 호스트에서 돈 세션은 `-outputs` 로 끝나는 이름이고 가상 머신에서 돈 세션은 `/sessions/이름` 을 바꾼 이름입니다[6]. 이름을 되짚어 만들지 말고 `cliSessionId.jsonl` 파일을 찾아 들어갑니다.

세션 메타데이터 `local_sid.json` 에서 두 도구가 읽는 키는 다음과 같습니다.

| 키 | 담긴 것 | 근거 |
|---|---|---|
| `sessionId`, `cliSessionId` | 세션 ID, 대화 기록 파일 이름이 되는 ID | [5][6] |
| `title` | 세션 제목 | [5][6] |
| `initialMessage` | 첫 요청 | [5] |
| `accountName`, `emailAddress` | 계정 표시 이름과 이메일 | [5] |
| `cwd` | 에이전트의 작업 폴더(가상 머신 안 경로일 수 있음) | [5] |
| `userSelectedFolders` | 사용자가 붙인 로컬 폴더 | [5][6] |
| `egressAllowedDomains`, `webFetchAllowedUrls` | 에이전트가 접속하도록 허락한 도메인·주소 | [5] |
| `spaceId` | 이 세션이 속한 공간 | [5] |
| `model`, `isArchived`, `memoryEnabled` | 설정한 모델, 보관 여부, 메모리 사용 여부 | [5] |
| `processName`, `vmProcessName` | 프로세스 이름 | [5] |
| `systemPrompt` | 시스템 프롬프트(40KB 넘는 경우가 있음) | [5] |
| `createdAt`, `lastActivityAt` | 만든 때, 마지막 활동 때 | [5][6] |

`spaces.json` 은 `spaces` 배열에 공간마다 `id`, `name`, `folders[].path`, `projects[].uuid`, `instructions`, `origin` 을 담고, 세션 메타데이터의 `spaceId` 로 이어집니다[5].

`audit.jsonl` 은 한 줄에 사건 하나를 적는 JSON Lines 파일이고, 메시지 형식은 Claude Code 기록과 같습니다[5]. 줄의 `type` 은 `user`·`assistant` 외에 `system`(작업 폴더 `cwd` 와 `model`), `result`(런타임이 계산한 `total_cost_usd` 와 `num_turns`), `rate_limit_event` 가 있고, claude-forensics 는 줄마다 `_audit_timestamp` 를 시각으로 읽습니다[5]. `assistant` 줄의 `message.usage` 에는 토큰 수와 `service_tier` 가 들어 있습니다[5]. 세션 폴더 안의 `cliSessionId.jsonl` 은 Claude Code 기록 형식 그대로라서 [Claude Code](../../dev-agents/claude-code/index.md)의 세션 기록 구조를 따라 읽으면 됩니다[6].

### 세션 메타데이터: `claude-code-sessions/`

`claude-code-sessions/org/account/local_sessionId.json` 은 메타데이터만 담고(claude-forensics 는 이것을 Cowork 세션 메타데이터라고 부릅니다), 대화 본문은 `~/.claude/projects/` 의 Claude Code 기록 파일에 있습니다[5]. 둘은 `cliSessionId` 값과 기록 파일 이름으로 이어집니다. 파일에 드는 키는 `sessionId`, `cliSessionId`, `cwd`, `originCwd`, `createdAt`, `lastActivityAt`, `model`, `effort`, `isArchived`, `title`, `titleSource`, `permissionMode`, `remoteMcpServersConfig` 입니다[5]. 데스크톱 앱에서 시작한 세션 기록을 언제 지우는지는 Claude Code 의 [세션 기록 구조](../../dev-agents/claude-code/transcripts.md)에서 다룹니다.

### 관리 설정과 로그인 정보

조직은 Jamf Pro·Kandji·Intune 같은 MDM 의 구성 프로필로 환경설정 도메인 `com.anthropic.claudefordesktop` 에 관리 설정을 내려보내고, 쓸 수 있는 키는 Windows 정책과 같은 목록입니다[3]. 키 목록은 [Windows 앱](windows.md)의 관리 정책 절에 있습니다. 구성 프로필이 기기에 남기는 plist 파일의 경로는 공개 문서에 나오지 않아 검체로 확인해야 하고, 찾은 plist 는 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/data-formats/plist/index.html)의 방법으로 읽습니다.

앱이 로그인 정보를 키체인에 두는지와 항목 이름은 공개된 분석 자료가 없어 검체의 키체인에서 확인해야 합니다. 키체인의 구조와 보호 방식은 [키체인](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/protection/keychain/index.html)에서 다룹니다. `buddy-tokens.json` 처럼 이름에 토큰이 들어간 파일에서 인증 값이 보이면 보고서에서 가립니다.

## 증거로서 의미

**증명하는 것.** 응용 프로그램 폴더에 앱이 있고 `~/Library/Application Support/Claude/` 가 있으면 이 macOS 사용자 계정에 앱을 설치하고 실행한 흔적이 있다고 쓸 수 있습니다. `local-agent-mode-sessions/` 에 세션이 있으면 그 계정으로 Cowork 세션을 만든 기록이 있다고 쓸 수 있고, 대화 기록에서 요청한 내용, 에이전트가 부른 도구, 쓴 토큰을 읽을 수 있습니다[5]. 메타데이터의 `userSelectedFolders`·`egressAllowedDomains`·`webFetchAllowedUrls` 는 에이전트에 허락한 폴더와 접속 범위를 알려 줍니다[5]. MCP 설정과 `~/Library/Logs/Claude` 의 로그가 있으면 로컬 MCP 서버를 연결했거나 연결하려 한 기록이 있다고 쓸 수 있고, 관리 설정이 있으면 기기에 조직 정책이 놓여 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 메타데이터의 `emailAddress` 는 앱에 로그인한 계정을 알려 줄 뿐이고, 그때 키보드 앞에 누가 있었는지는 알려 주지 않습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). `egressAllowedDomains` 는 허락한 범위이고 실제로 접속한 기록이 아니라서 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)과 맞춰 봅니다. `result` 줄의 `total_cost_usd` 는 런타임이 계산한 값이고 청구 금액이 아니며, 청구 근거는 Anthropic 콘솔입니다[5]. 일반 채팅 대화가 기기에 남는지는 공개된 분석 자료가 없어서, 대화 내용이 필요하면 [계정 데이터 내보내기](export.md)를 씁니다.

## 시각 해석

세션 메타데이터의 `createdAt`·`lastActivityAt` 은 유닉스 epoch 밀리초 정수입니다[6]. 이 칸과 `_audit_timestamp` 는 밀리초 정수나 ISO 8601 문자열로 올 수 있고, `audit.jsonl` 의 시각은 끝에 `Z` 가 붙은 UTC 문자열입니다[5]. agentsview 는 대화 기록에 시각이 하나도 없는 세션(만들고 돌리지 않은 세션)만 `createdAt`·`lastActivityAt` 으로 시작·끝 시각을 채웁니다[6].

세션 제목을 바꾸면 메타데이터 파일만 바뀌어서, agentsview 는 메타데이터 파일과 대화 기록 파일의 수정 시각 가운데 늦은 쪽을 세션의 수정 시각으로 씁니다[6]. 메타데이터 파일의 수정 시각이 늦다고 그때 대화가 있었다고 보지 않습니다.

업데이트는 앱 안에서 이뤄지고[1] 그때 앱 번들의 파일 시스템 시각이 바뀔 수 있어서, 번들 시각을 처음 설치한 때로 보지 않습니다. 처음 받은 때는 [격리 속성과 다운로드 기록](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/quarantine/index.html)에서, 폴더가 생기고 지워진 순서는 [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/fsevents/index.html)에서 찾습니다. 여러 시각을 한 줄로 맞추는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)을 봅니다. MCP 로그 줄의 시각 형식은 공개 문서에 없어서 값을 보고 판단합니다.

## 함정과 한계

- **두 폴더를 모두 떠야 합니다.** `claude-code-sessions/` 의 세션은 메타데이터가 `~/Library/Application Support/Claude/` 에, 본문이 `~/.claude/projects/` 에 있어서 한쪽만 뜨면 제목·계정과 대화가 끊깁니다[5]. `~/.claude` 쪽은 [Claude Code](../../dev-agents/claude-code/index.md)에서 다룹니다.
- **큰 폴더는 따로 판단합니다.** claude-forensics 는 `vm_bundles/`·`Cache/`·`Code Cache/` 를 수사 가치가 없다고 보고 복사하지 않습니다[5]. 도구의 수집 목록을 그대로 쓰면 이 폴더들이 빠지므로, 사건에 필요하면 따로 뜹니다.
- **`skills-plugin/` 은 세션이 아닙니다.** `local-agent-mode-sessions/` 바로 아래에 있지만 플러그인 지원 데이터입니다[5][6].
- **도구마다 읽는 기록이 다릅니다.** 위치 절에서 본 것처럼 `audit.jsonl` 과 세션 폴더 안 `.claude/projects/` 가운데 도구가 한쪽만 읽을 수 있어서, 도구 결과에 세션이 비어 있으면 원본 폴더를 직접 봅니다.
- **App Store 판과 헷갈리지 않습니다.** App Store 의 Claude 앱은 iPhone·iPad 호환만 표기돼 있고 Mac 호환 표기는 없습니다(2026-09 기준)[4]. Mac 의 Claude 흔적은 이 페이지의 데스크톱 앱에서 나온 것인지 [웹 브라우저](web.md)에서 나온 것인지부터 가립니다.
- **앱을 지워도 라이브러리가 남을 수 있습니다.** 응용 프로그램 폴더에 앱이 없어도 사용자 라이브러리의 폴더와 로그를 따로 봅니다.

## 직접 분석해 보기

헥스로 볼 만한 이진 구조는 없고 모두 JSON 과 JSON Lines 라서 텍스트로 읽습니다. 아래는 위 키 목록으로 만든 예시이고 값은 모두 지어낸 것입니다.

```json
{"sessionId":"local_11111111-2222-3333-4444-555555555555",
 "cliSessionId":"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
 "title":"예시 보고서 정리","emailAddress":"user@example.com",
 "cwd":"/sessions/example-name","spaceId":"space-0001",
 "userSelectedFolders":["/Users/example/Documents/sample"],
 "egressAllowedDomains":["example.org"],
 "createdAt":1757000000000,"lastActivityAt":1757000600000}
```

`createdAt` 1757000000000 을 1000 으로 나누면 1757000000 초이고, UTC 로 2025-09-04 15:33:20 입니다.

셸 도구로는 다음 순서로 봅니다.

1. `~/Library/Application Support/Claude/` 의 `local-agent-mode-sessions/`·`claude-code-sessions/`·설정 JSON 과 `~/Library/Logs/Claude`, `~/.claude` 를 사본으로 뜹니다.
2. 세션 메타데이터를 한 줄씩 뽑습니다. `jq -c '{sessionId, cliSessionId, title, emailAddress, createdAt, lastActivityAt}' local-agent-mode-sessions/*/*/local_*.json`
3. 대화 기록에서 도구 호출과 비용 줄을 뽑습니다. `jq -c 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | .name' audit.jsonl`, `jq -c 'select(.type=="result") | {total_cost_usd, num_turns}' audit.jsonl`
4. `cliSessionId` 로 세션 폴더 안 `.claude/projects/` 와 `~/.claude/projects/` 에서 같은 이름의 기록 파일을 찾습니다.
5. 관리 설정 plist 를 찾았다면 `plutil -p` 로 키를 읽습니다.

공개 도구로는 claude-forensics 가 두 폴더를 읽기 전용 사본으로 뜬 뒤 `cowork-sessions.jsonl`(claude-code-sessions 메타데이터)과 `cowork-agent-sessions.jsonl`(Cowork 대화 기록과 공간 정보)을 만들고, 모든 결과 파일의 SHA-256 목록을 남깁니다[5]. 명령 예는 `./claude-forensics.sh -W ~/.claude 결과폴더` 이고, 다른 기기에서 뜬 사본은 `-w 사본경로` 로 줍니다[5]. agentsview 는 `local-agent-mode-sessions/` 를 읽어 Cowork 세션을 `cowork:` 접두어가 붙은 ID 로 보여 줍니다[6].

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [Claude Code](../../dev-agents/claude-code/index.md) | `cliSessionId` 로 이어지는 대화 기록 본문 |
| [격리 속성과 다운로드 기록](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/quarantine/index.html) | 설치 파일을 받은 때와 받은 곳 |
| [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/fsevents/index.html) | 세션 폴더가 생기고 지워진 순서 |
| [통합 로그 형식](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/data-formats/unified-log/index.html) | 앱 실행과 관련된 시스템 기록 |
| [MCP 서버와 도구 호출 기록](../../dev-agents/mcp.md) | 연결한 로컬 도구 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱과 에이전트가 실제로 접속한 시각 |
| [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md) | 에이전트 기록으로 행위를 되짚는 순서 |
| [계정 데이터 내보내기](export.md) | 일반 채팅 대화 본문과 시각 |

## 실습

직접 만든 시험용 macOS 가상 머신이나 공개 검체(NIST CFReDS 등)의 Mac 이미지로 다음을 풀어 봅니다.

1. `local-agent-mode-sessions/` 아래 세션 폴더에 `audit.jsonl` 과 `.claude/projects/` 가운데 무엇이 있는가? 둘 다 있다면 같은 대화를 담고 있는가?
2. `local_sid.json` 의 `createdAt`·`lastActivityAt` 과 대화 기록 첫 줄·마지막 줄의 시각은 얼마나 떨어져 있는가?
3. `claude-code-sessions/` 의 `cliSessionId` 가운데 `~/.claude/projects/` 에 기록 파일이 없는 것은 몇 개인가?
4. `~/Library/Logs/Claude` 에 `mcp-server-` 로 시작하는 로그가 있다면, 그 서버가 `claude_desktop_config.json` 에도 남아 있는가?

## 참고 문헌

1. Install Claude Desktop (Claude Help Center) — https://support.claude.com/en/articles/10065433-installing-claude-desktop
2. Connect to local MCP servers (Model Context Protocol 문서) — https://modelcontextprotocol.io/docs/develop/connect-local-servers
3. Enterprise configuration for Claude Desktop (Claude Help Center) — https://support.claude.com/en/articles/12622667-enterprise-configuration-for-claude-desktop
4. Claude by Anthropic — App Store — https://apps.apple.com/us/app/claude-by-anthropic/id6473753684
5. forensicdave, claude-forensics v0.1.1 — https://github.com/forensicdave/claude-forensics (`README.md`, `claude-forensics.sh`, `claude_forensics.py` 의 `process_cowork`·`process_agent_sessions`·`summarise_audit`, `docs/claude_forensics.md`)
6. kenn-io, agentsview — https://github.com/kenn-io/agentsview (`internal/parser/cowork.go`, `internal/parser/cowork_paths.go`, `docs/internal/session-format-sources.md`)
