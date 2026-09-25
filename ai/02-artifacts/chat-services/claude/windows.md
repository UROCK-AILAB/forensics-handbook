---
title: "Claude Windows 앱"
parent: "Claude"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 160
---

# Windows 앱 (Windows)

Windows 의 Claude 데스크톱 앱은 사용자 데이터 폴더 하나에 크롬 계열 저장소, 앱 설정 JSON, Claude Code·Cowork 세션 파일을 함께 남깁니다. 일반 대화 원본은 계정 서버에 있지만, Cowork 에이전트 세션은 대화 기록과 계정 정보가 이 폴더에 남습니다.

> 확인 날짜: 2026-09. 공식 도움말과 MCP 문서(2026-09-25 열람), 공개 분석 도구 두 가지의 코드[6][7], 기기 관찰을 함께 썼습니다. 기기 관찰은 스토어에서 받은 앱의 패키지 폴더를 읽기 전용으로 열어 폴더·파일 이름과 키 이름만 본 것이고, 값은 가렸습니다(확인 범위: Windows 11, 2026-09). 앱이 자주 바뀌므로 경로와 키는 검체에서 다시 확인합니다.

## 무엇을 기록하나 · 왜 생기나

데스크톱 앱은 claude.ai 와 같은 계정으로 로그인해 쓰는 앱이라서, 일반 대화는 웹판처럼 서버에 저장됩니다. agentsview 코드 주석은 이 앱을 Electron 앱으로 설명하고, 사용자 데이터 폴더도 Electron 관례를 따른다고 적습니다[7]. 그래서 화면을 그리는 엔진이 캐시·쿠키·Local Storage·IndexedDB 를 만들고, 앱은 창 위치·처음 실행한 때·마지막 계정 ID 같은 값을 JSON 파일에 따로 적습니다.

대화 흔적이 기기에 직접 남는 곳은 두 폴더입니다. `claude-code-sessions` 에는 세션 정보 파일만 있고 대화 본문은 `.claude\projects` 에 있으며, Cowork(로컬 에이전트 모드) 세션은 `local-agent-mode-sessions` 에 세션 정보와 대화 기록이 함께 있습니다[6][7]. 로컬 MCP 서버를 연결하면 그 설정과 연결 로그도 남습니다[1].

## 위치와 버전별 차이

### 설치 방법에 따른 폴더

조직 배포용 MSIX 패키지는 x64 와 arm64 로 따로 있고[3], 개인 사용자는 다운로드 페이지에서 받은 파일로 설치합니다[2]. 지원 OS 는 Windows 10 이상입니다[2]. 조직 배포 안내는 사용자별 설치에 `Add-AppxPackage` 를, 기기 전체 제공에 `Add-AppxProvisionedPackage -Online` 을 쓰고, Intune·SCCM(MECM)·그룹 정책 소프트웨어 설치·DISM·PowerShell 을 배포 수단으로 듭니다[3].

사용자 데이터 폴더는 설치 방법에 따라 두 곳으로 나뉩니다. agentsview 코드는 MSIX 패키지 설치를 아래 첫째 경로로, MSIX 가 아니거나 예전 설치를 둘째 경로로 적습니다[7].

```
%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\
%APPDATA%\Claude\
```

claude-forensics 는 v0.1.1(2026-06-16) 문서에서 Windows 의 데스크톱 데이터 폴더를 `\Users\이름\AppData\Roaming\Claude\` 하나로만 적습니다[6]. agentsview 는 2026-09-25 판에서 스토어 패키지 경로를 함께 적습니다[7]. 두 자료가 적은 경로가 달라서 검체에서는 두 곳을 모두 보고, 사용자 프로필 전체에서 `claude_desktop_config.json` 과 `local-agent-mode-sessions` 를 이름으로 찾습니다.

Microsoft 문서는 가상화된 패키지 앱이 Windows 10 1903 이후 `AppData` 의 Local·Roaming 아래에 새로 만드는 파일을 사용자·패키지별 전용 위치로 옮겨 쓴다고 설명합니다[5]. 파일을 열 때는 전용 위치를 먼저 찾고, 없으면 실제 `AppData` 에서 엽니다[5]. 스토어판에서 `%APPDATA%\Claude` 대신 패키지 안 `LocalCache\Roaming\Claude` 에 파일이 생기는 까닭이 이것이고, 원리는 [Electron·웹뷰 앱의 저장 구조](../../../01-foundations/storage-model/electron-webview.md)에서 다룹니다.

### 경로 표

아래 표의 `Claude\` 는 위 두 사용자 데이터 폴더 중 검체에 있는 쪽입니다.

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `Claude\claude_desktop_config.json` | 로컬 MCP 서버 설정(최상위 키 `mcpServers`)과 앱 환경설정 | 문서[1], 도구[6], 관찰 |
| `Claude\logs\mcp.log` | MCP 연결과 실패 기록 | 문서[1] |
| `Claude\logs\mcp-server-서버이름.log` | 그 서버가 표준 오류로 낸 출력 | 문서[1] |
| `Claude\claude-code-sessions\` | 세션 정보 파일(대화 본문은 `.claude\projects` 에 있음) | 도구[6] |
| `Claude\local-agent-mode-sessions\` | Cowork 세션 정보, 대화 기록, `spaces.json` | 도구[6][7] |
| `Claude\config.json`, `buddy-tokens.json`, `cowork-enabled-cli-ops.json`, `ant-did` | 앱 설정·상태 파일 | 도구[6], 관찰 |
| `Claude\vm_bundles\` | 수 GB 크기의 폴더(수집 도구가 빼는 대상) | 도구[6] |
| `Claude\Cache\`, `Code Cache\` 등 | 크롬 계열 캐시와 저장소 | 도구[6], 관찰 |
| 패키지 폴더의 `LocalCache\Local\claude-cli-nodejs\Cache\` | `mcp-logs-` 로 시작하는 폴더의 JSON Lines 로그 | 관찰 |
| 패키지 폴더의 `AC\INetHistory\이름\container.dat` | 용도를 설명한 공개 자료 없음 | 관찰 |
| `HKLM\SOFTWARE\Policies\Claude` | 기기 관리 정책 | 문서[4] |
| `HKCU\SOFTWARE\Policies\Claude` | 사용자 관리 정책 | 문서[4] |

Claude Code 자체가 쓰는 `%USERPROFILE%\.claude` 폴더는 이 표와 따로 있습니다. claude-forensics 는 Claude Code 와 Cowork 의 상태가 두 폴더에 나뉘어 있어서 둘 다 떠야 전체를 볼 수 있다고 적습니다[6]. `.claude` 쪽은 [Claude Code — Windows](../../dev-agents/claude-code/windows.md)에서 다룹니다.

## 구조

### 세션 정보: claude-code-sessions

claude-forensics 는 이 폴더를 아래 모양으로 읽고, 여기 있는 파일을 Cowork 세션 정보(사이드카)라고 부릅니다[6]. 폴더 두 단계가 조직 UUID 와 계정 UUID 이고, 파일 하나가 세션 하나입니다.

```
claude-code-sessions\
  orgUuid\
    accountUuid\
      local_sessionId.json
```

파일 안의 키로 문서에 적힌 것은 `sessionId`, `cliSessionId`, `cwd`, `originCwd`, `createdAt`, `lastActivityAt`, `model`, `effort`, `isArchived`, `title`, `titleSource`, `permissionMode`, `remoteMcpServersConfig` 입니다[6]. 이 파일에는 대화 본문이 없고, claude-forensics 문서는 이 세션의 대화 기록이 CLI 세션처럼 `.claude\projects` 에 쓰인다고 적습니다[6]. 그래서 claude-forensics 는 `cliSessionId` 를 `.claude\projects` 아래 기록 파일 이름과 맞춰 본문을 찾습니다[6]. 기록 파일의 구조는 [세션 기록 구조](../../dev-agents/claude-code/transcripts.md)에서, 권한 모드는 [설정과 권한](../../dev-agents/claude-code/settings-permissions.md)에서 다룹니다.

### Cowork 세션: local-agent-mode-sessions

Cowork 세션은 세션 정보 파일과 같은 이름의 폴더가 짝을 이룹니다. 두 도구가 읽는 파일은 아래와 같습니다[6][7].

```
local-agent-mode-sessions\
  skills-plugin\                      세션 저장소 아님(두 도구 모두 건너뜀)
  orgUuid\
    accountUuid\                      agentsview 는 workspaceId 로 부름
      spaces.json
      local_sessionId.json            세션 정보
      local_sessionId\
        audit.jsonl                   claude-forensics 가 읽는 대화 기록
        .claude\projects\폴더\cliSessionId.jsonl                    agentsview 가 읽는 대화 기록
        .claude\projects\폴더\cliSessionId\subagents\...\agent-ID.jsonl  하위 에이전트 기록
```

claude-forensics(v0.1.1, 2026-06-16)는 `audit.jsonl` 을 에이전트 세션의 전체 대화 기록으로 읽습니다[6]. agentsview(2026-09-25)는 세션 폴더 안 `.claude\projects` 에서 `cliSessionId.jsonl` 을 찾아 읽고, 이 파일이 Claude Code 기록과 같은 형식이라고 적습니다[7]. 두 도구가 서로 다른 파일을 대화 기록으로 삼으므로 검체에서는 둘 다 찾습니다. agentsview 는 `.claude\projects` 아래 폴더 이름이 버전마다 달라서(`-…-outputs` 로 끝나거나 가상 머신 안 경로 `/sessions/…` 를 바꾼 모양) 폴더 이름을 되짚지 않고 파일 이름으로 찾는다고 적습니다[7]. 같은 폴더에 있는 `cowork-clientdata-cache.json`, `cowork_settings.json` 은 세션 정보 파일이 아닙니다[7].

agentsview 의 Cowork 형식 메모는 2026-07-19 에 Anthropic 문서를 봤을 때 Cowork 의 디스크 형식이 공개돼 있지 않았고, 위 구조는 구현에서 알아낸 것이라고 적습니다[7]. 앱이 바뀌면 달라질 수 있습니다.

**세션 정보 파일(`local_sessionId.json`).** claude-forensics 가 읽는 키와 뜻은 다음과 같습니다[6].

| 키 | 담긴 것 |
|---|---|
| `sessionId`, `cliSessionId` | Cowork 세션 ID, `.claude` 기록과 잇는 ID |
| `emailAddress`, `accountName` | 계정 이메일과 표시 이름 |
| `title`, `initialMessage` | 세션 제목과 첫 요청 |
| `spaceId` | 이 세션이 속한 스페이스 |
| `model`, `isArchived`, `memoryEnabled` | 설정한 모델, 보관 여부, 메모리 사용 여부 |
| `userSelectedFolders` | 사용자가 에이전트에 붙인 폴더 |
| `egressAllowedDomains`, `webFetchAllowedUrls` | 에이전트가 접속을 허락받은 도메인과 URL |
| `processName`, `vmProcessName` | 프로세스 이름 |
| `systemPrompt` | 시스템 프롬프트(40KB 넘게 클 수 있음) |
| `cwd` | 에이전트의 작업 폴더(가상 머신 안 경로) |
| `createdAt`, `lastActivityAt` | 만든 시각, 마지막 활동 시각 |

아래는 위 키 이름으로 새로 만든 예시이고, 값은 모두 지어낸 것입니다.

```json
{
  "sessionId": "local_11111111-2222-4333-8444-555555555555",
  "cliSessionId": "66666666-7777-4888-9999-aaaaaaaaaaaa",
  "emailAddress": "user@example.com",
  "title": "분기 보고서 정리",
  "spaceId": "space-example-01",
  "userSelectedFolders": ["C:\\Users\\example\\Documents\\reports"],
  "egressAllowedDomains": ["example.com"],
  "cwd": "/sessions/example-session",
  "createdAt": 1767225600000,
  "lastActivityAt": 1767229200000
}
```

**대화 기록(`audit.jsonl`).** 한 줄이 이벤트 하나이고, claude-forensics 코드 주석은 CLI 기록에 없는 `type` 으로 `system`, `result`, `rate_limit_event` 가 더 있다고 적습니다[6]. 이 도구가 실제로 읽는 줄은 `type` 이 `system`, `user`, `assistant`, `result` 인 줄입니다[6]. 시각은 `_audit_timestamp` 에 있습니다. `system` 줄에서 작업 폴더(`cwd`)와 모델을, `assistant` 줄의 `message.usage` 에서 토큰 수를, `result` 줄에서 앱이 적은 비용(`total_cost_usd`)과 턴 수(`num_turns`)를 읽습니다[6]. 메시지 형식은 Claude Code 기록과 같아서, 사용자 요청과 도구 호출을 읽는 법은 [세션 기록 구조](../../dev-agents/claude-code/transcripts.md)를 따르면 됩니다.

**스페이스 목록(`spaces.json`).** 계정 폴더마다 하나 있고, 최상위 `spaces` 배열의 항목마다 `id`, `name`, `folders[].path`, `projects[].uuid`, `instructions`, `origin` 이 있습니다[6]. 세션 정보의 `spaceId` 를 여기 `id` 와 맞추면 세션이 어느 스페이스에서 어떤 폴더와 지시문으로 돌았는지 알 수 있습니다.

### 앱 설정 JSON

사용자 데이터 폴더에는 앱이 직접 쓰는 JSON 파일이 있고, 키 이름은 다음과 같았습니다(확인 범위: Windows 11, 2026-09). claude-forensics 는 이 가운데 `config.json`, `claude_desktop_config.json`, `buddy-tokens.json`, `cowork-enabled-cli-ops.json` 과 `ant-did` 를 수집 대상으로 둡니다[6]. 키의 뜻을 설명한 공개 자료가 없어서, 아래 셋째 칸은 키 이름이 가리키는 것만 적었고 검체의 값으로 확인해야 합니다.

| 파일 | 키(일부) | 키 이름이 가리키는 것 |
|---|---|---|
| `config.json` | `first_launch_at`, `version_first_launch.at`, `version_first_launch.version`, `updaterLastSeenVersion`, `updaterBannerStagedAt.version`, `updaterBannerStagedAt.stagedAt`, `lastKnownAccountUuid`, `locale`, `userThemeMode`, `planUsageLastTrayOpenAt`, `terminalCliPowerShellPath`, `windowSizeWasSignedIn`, `quickWindowPosition.monitor.*` | 처음 실행한 때와 그때 버전, 업데이트 버전, 마지막 계정 ID, 모니터 정보 |
| `claude_desktop_config.json` | `mcpServers`, `coworkUserFilesPath`, `preferences.localAgentModeTrustedFolders`, `preferences.remoteToolsDeviceName`, `preferences.coworkWebSearchEnabled`, `preferences.coworkBrowserToolsEnabled`, `preferences.coworkPreferredBrowser`, `preferences.coworkScheduledTasksEnabled`, `preferences.ccdScheduledTasksEnabled`, `preferences.ccRemoteControlDefaultEnabled`, `preferences.ccAutoArchiveInactiveDays`, `preferences.bypassPermissionsGateByAccount`, `preferences.keepAwakeEnabled`, `preferences.sidebarMode`, `preferences.epitaxyPrefs.*` | MCP 서버, Cowork 작업 폴더, 신뢰한 폴더, 켜 둔 에이전트 기능 |
| `bridge-state.json` | `enabled`, `environmentId`, `localSessionId`, `remoteSessionId`, `processedMessageUuids`, `pendingProcessedAcks`, `userConsented` | 공개 설명 없음 |
| `plan-usage-history.json` | `version`, `samples[].org`, `samples[].t`, `samples[].u.fh`, `samples[].u.sd` | 공개 설명 없음 |
| `buddy-tokens.json` | `tokens-today.date`, `tokens-today.tokens` | 날짜와 토큰 수 |
| `window-state.json` | `x`, `y`, `width`, `height`, `isMaximized`, `isFullScreen`, `displayBounds.*` | 창 크기와 위치 |
| `git-worktrees.json` | `schemaVersion`, `worktrees`, `untrackedDirGc.cwds`, `untrackedDirGc.roots`, `untrackedDirGc.sightings` | 앱이 다룬 코드 작업 폴더 |
| `mcp-user-tool-toggles.json` | `v`, `owners.*` | 공개 설명 없음 |
| `extensions-blocklist.json` | `[].url`, `[].lastUpdated`, `[].entries[].id`, `.reason`, `.hash`, `.certificateFingerprint`, `.is_internal_dxt` | 확장 차단 목록 |
| `cowork-enabled-cli-ops.json` | `ownerAccountId` | 계정 ID |
| `ant-device-registry.json` | 키 이름 가림, 값은 문자열 | 공개 설명 없음 |

관찰한 PC 의 `claude_desktop_config.json` 에는 `mcpServers` 키가 없었습니다. 이 파일에는 앱 환경설정이 함께 들어 있어서, 키가 없으면 이 파일로 로컬 MCP 서버를 설정하지 않았다는 뜻으로만 읽습니다. MCP 설정과 로그의 해석은 [MCP 서버와 도구 호출 기록](../../dev-agents/mcp.md)에서 다룹니다.

### 크롬 계열 저장소

스토어판의 `LocalCache\Roaming\Claude\` 아래에는 크롬 계열 브라우저 프로필과 같은 이름의 폴더와 파일이 있었습니다(확인 범위: Windows 11, 2026-09).

```
Cache\            Code Cache\        GPUCache\
DawnGraphiteCache\  DawnWebGPUCache\  Dictionaries\*.bdic
Crashpad\metadata   Crashpad\settings.dat
DIPS  DIPS-wal
File System\Origins\
IndexedDB\이름\   (CURRENT, LOCK, LOG, *.ldb, *.log)
Local Storage\leveldb\
Local State
InterestGroups
Network\Cookies  Network\Cookies-journal
Network\Network Persistent State  Network\TransportSecurity
Partitions\이름\...
ChromeNativeHost\chrome-native-host.exe
```

폴더마다의 형식은 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)와 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html)에 있습니다. `Partitions` 아래에는 `cowork-file-preview`, `launch-preview-static` 파티션이 있었고, `Partitions\cowork-file-preview\Network\Cookies` 는 표 `cookies` 와 `meta` 가 있는 SQLite 데이터베이스였습니다(확인 범위: Windows 11, 2026-09). `cookies` 의 칸은 크롬 계열 쿠키 DB 와 같았습니다.

```
cookies: creation_utc, host_key, top_frame_site_key, name, value,
         encrypted_value, path, expires_utc, is_secure, is_httponly,
         last_access_utc, has_expires, is_persistent, priority, samesite,
         source_scheme, source_port, last_update_utc, source_type,
         has_cross_site_ancestor
meta:    key, value
```

크롬 계열 쿠키 값이 `encrypted_value` 칸에 보호돼 들어가는 원리는 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html)와 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)에서 다룹니다. 쿠키와 로그인 정보는 보고서에서 가립니다([API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)).

### 패키지 안의 다른 폴더

스토어판 패키지의 `LocalCache\Local\claude-cli-nodejs\Cache\이름\` 아래에는 `mcp-logs-scheduled-tasks`, `mcp-logs-computer-use` 처럼 `mcp-logs-` 로 시작하는 폴더와 JSON Lines 파일이 있었고, 한 줄의 키는 `cwd`, `debug`, `sessionId`, `timestamp` 였습니다(확인 범위: Windows 11, 2026-09). 이 로그는 [Claude Code — Windows](../../dev-agents/claude-code/windows.md)와 [MCP 서버와 도구 호출 기록](../../dev-agents/mcp.md)에서 다룹니다.

같은 `LocalCache\Local` 에는 Android SDK, NuGet, npm-cache, pip cache, GitHub CLI 의 device-id 같은 다른 개발 도구의 캐시 폴더도 있었습니다(확인 범위: Windows 11, 2026-09). 이런 폴더가 보여도 사용자가 그 도구를 따로 설치했다고 바로 쓰지 않고, 앱 밖의 설치 흔적과 비교합니다.

### 관리 정책

조직은 `HKLM\SOFTWARE\Policies\Claude`(기기)나 `HKCU\SOFTWARE\Policies\Claude`(사용자)에 정책을 넣고, 둘 다 있으면 기기 쪽이 우선합니다[4]. 문서에 나오는 정책 키 예는 다음과 같습니다[4].

```
disableAutoUpdates                 autoUpdaterEnforcementHours
isDesktopExtensionEnabled          isDesktopExtensionDirectoryEnabled
isClaudeCodeForDesktopEnabled      isLocalDevMcpEnabled
secureVmFeaturesEnabled (Cowork)   allowedWorkspaceFolders
forceLoginOrgUUID                  effortLevel
```

앱은 약 4시간마다 새 버전을 확인해 스스로 업데이트하고, `disableAutoUpdates` 로 이를 끌 수 있습니다[3][4]. Cowork 를 쓰려면 Windows 기능 VirtualMachinePlatform 이 켜져 있어야 합니다[3]. 앱 메뉴의 `Help > Troubleshooting > Show Logs` 로 로그 폴더를 열 수 있고, 배포 안내에는 진단 파일 `supported-features-info.json` 도 나옵니다[3]. 조직 계정의 관리자 쪽 기록은 [Claude 기업용 감사 로그](../../network-enterprise/claude-enterprise.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 사용자 데이터 폴더가 있으면 이 Windows 계정에 앱이 설치돼 한 번 이상 실행된 흔적이 있다고 쓸 수 있습니다. `local-agent-mode-sessions` 의 세션 정보 파일과 대화 기록이 있으면 그 세션에서 오간 요청·응답·도구 호출과, 에이전트에 붙인 폴더·허락한 도메인을 기록이 말하는 만큼 쓸 수 있습니다([AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)). 세션 정보의 `emailAddress`, `accountName` 과 폴더 이름의 조직·계정 UUID 는 그 세션이 어느 계정으로 돌았는지 알려 줍니다[6]. `claude-code-sessions` 의 파일은 `cliSessionId` 로 `.claude` 의 기록과 이어지고, 그 세션의 제목·보관 여부·소유 조직과 계정을 알려 줍니다[6]. `mcpServers` 설정과 MCP 로그가 있으면 로컬 MCP 서버를 연결했거나 연결하려 한 기록이 있다고 쓸 수 있습니다.

**증명하지 못하는 것.** 계정 이메일은 로그인한 계정을 가리킬 뿐, 그때 키보드 앞에 누가 있었는지는 알려 주지 않습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). `config.json` 의 `lastKnownAccountUuid` 는 마지막 계정 하나만 가리켜서, 그 전에 다른 계정을 쓰지 않았다는 근거가 되지 않습니다. `result` 줄의 `total_cost_usd` 는 앱이 적은 값이고, claude-forensics 는 청구 기록의 기준이 Anthropic Console 이라고 적습니다[6]. 일반 대화(Cowork·Claude Code 가 아닌 대화)의 본문은 이 폴더로 확인할 수 없어서 [계정 데이터 내보내기](export.md)를 씁니다.

## 시각 해석

agentsview 는 Cowork 세션 정보의 `createdAt`, `lastActivityAt` 을 1970-01-01 UTC 기준 밀리초로 읽습니다[7]. claude-forensics 는 `audit.jsonl` 의 `_audit_timestamp` 가 밀리초 정수이면 UTC 로 바꾸고, 문자열이면 그대로 쓰며, 문자열은 `Z` 로 끝나는 UTC 형식이라고 적습니다[6]. `claude-code-sessions` 의 `createdAt`, `lastActivityAt` 은 단위를 적은 자료가 없어서, 13자리 정수면 밀리초로 보고 파일 시스템 시각과 맞는지 확인합니다.

agentsview 는 제목을 바꾸면 세션 정보 파일만 바뀐다고 적습니다[7]. 그래서 세션 정보 파일의 수정 시각이 대화 기록 파일보다 늦으면, 마지막 대화 뒤에 제목 변경 같은 정보 수정이 있었을 수 있습니다. 대화가 오간 시각은 기록 줄의 시각으로 씁니다.

`config.json` 의 `first_launch_at`, `version_first_launch.at`, `updaterBannerStagedAt.stagedAt`, `planUsageLastTrayOpenAt` 과 `plan-usage-history.json` 의 `samples[].t` 는 단위를 적은 공개 자료가 없어서 자릿수로 판단합니다. 앱은 약 4시간마다 스스로 업데이트하므로[3], 앱 파일의 파일 시스템 시각을 처음 설치한 때로 보지 않고 `version_first_launch` 를 먼저 봅니다. 쿠키 DB 의 `creation_utc`, `last_access_utc`, `expires_utc` 는 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)의 시각 해석을 따르고, 정책 레지스트리 키는 키의 마지막 쓰기 시각으로 정책이 바뀐 때를 가늠합니다. 여러 시각을 한 줄로 맞추는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

`vm_bundles\` 는 크기가 수 GB 에 이르고, claude-forensics 문서는 12GB 로 적습니다[6]. 이 도구는 `vm_bundles\`, `Cache\`, `Code Cache\` 를 수집에서 빼고 세션 폴더 둘과 설정 파일 다섯 개만 뜹니다[6]. 선별 수집을 하더라도 원본 디스크 이미지는 따로 남겨 두고, 수집 순서는 [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다.

앱이 실행 중이면 쿠키 DB 같은 파일이 잠겨 열리지 않을 수 있습니다. 앱을 닫은 뒤 사본을 뜨거나 디스크 이미지에서 꺼내고, `-journal`·`-wal` 파일도 함께 가져옵니다.

Microsoft 문서에 따르면 패키지 앱을 지우면 전용 위치로 옮겨 쓴 `AppData` 파일도 함께 지워집니다[5]. 그래서 스토어판을 지운 뒤에는 패키지 폴더가 남지 않을 수 있고, 패키지 폴더가 없다고 앱을 쓰지 않았다고 단정하지 않습니다. `.claude` 폴더, 네트워크 기록, 계정 데이터 내보내기를 함께 봅니다.

claude-forensics 는 JSON 으로 읽히지 않는 줄을 건너뛰되 로그에 남기며, 이런 줄은 쓰는 도중에 멈췄거나 누가 손으로 고친 흔적이라고 적습니다[6]. 그런 줄이 있으면 따로 세어 보고서에 적습니다. 패키지 안에 다른 개발 도구의 캐시가 섞여 있어서, 폴더 크기나 파일 수만 보고 앱을 많이 썼다고 판단하지 않습니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 위의 `config.json` 키 이름으로 만든 예시 바이트이고, 실제 파일에서 뜬 것이 아닙니다. 첫 바이트가 `7B`(`{`)이고 따옴표(`22`) 뒤에 키 이름의 ASCII 가 이어지면 암호화하지 않은 평문 JSON 입니다. `local_sessionId.json` 과 `audit.jsonl` 도 같은 방법으로 평문인지 먼저 봅니다.

```
만든 예시(명세로 만든 바이트)
00000000  7B 22 66 69 72 73 74 5F 6C 61 75 6E 63 68 5F 61  {"first_launch_a
00000010  74 22 3A 31 37 36 37 32 32 35 36 30 30 30 30 30  t":1767225600000
```

**공개 도구로 한 번.** claude-forensics 는 macOS·Linux 에서 돌고, Windows 에서 떠 온 `.claude` 와 데스크톱 데이터 폴더를 함께 받습니다[6]. `-w` 에는 `claude-code-sessions` 와 `local-agent-mode-sessions` 가 들어 있는 폴더의 사본을 줍니다. 스토어판이면 `LocalCache\Roaming\Claude` 사본이 그 폴더입니다.

```sh
./claude-forensics.sh \
    -w /path/to/copy/of/Claude \
    /path/to/copy/of/.claude \
    output-dir
```

결과에는 `cowork-sessions.jsonl`(claude-code-sessions)과 `cowork-agent-sessions.jsonl`(local-agent-mode-sessions)이 따로 나오고, 결과 파일마다 SHA-256 을 적은 `MANIFEST.sha256` 도 만들어집니다[6]. README 는 이 목록이 읽기 전용 사본까지 담는다고 적지만, `claude-forensics.sh` 코드와 `docs/claude-forensics.md` 는 묶음(tgz)에 들어가는 결과 파일만 담고 사본은 빼는 것으로 되어 있습니다[6]. 그래서 사본의 해시는 따로 계산해 둡니다. claude-forensics 문서는 이 도구가 시험한 앱 버전을 적지 않았고, 도구 판은 v0.1.1(2026-06-16)입니다. agentsview 는 사용자 홈 아래 기본 경로를 읽는 세션 뷰어라서, 증거 사본은 분석용 가상 머신에서 엽니다. 설정 JSON 은 jq 로 키 목록을 뽑고(`jq 'paths | map(tostring) | join(".")' config.json`), 쿠키 DB 사본은 SQLite 도구로 `cookies` 표의 `host_key` 와 시각 칸을 봅니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [Claude Code — Windows](../../dev-agents/claude-code/windows.md) | `cliSessionId` 로 이어지는 `.claude` 쪽 기록 |
| [세션 기록 구조](../../dev-agents/claude-code/transcripts.md) | 대화 기록 한 줄의 구조와 도구 호출 |
| [MCP 서버와 도구 호출 기록](../../dev-agents/mcp.md) | 연결한 로컬 도구와 호출 |
| [웹 브라우저](web.md) | 같은 PC 에서 브라우저로도 썼는지 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱이 접속한 시각 |
| [계정 데이터 내보내기](export.md) | 일반 대화 본문과 시각 |
| [macOS 앱](macos.md) | 같은 계정을 macOS 에서도 썼는지 |

## 실습

직접 만든 시험용 Windows 가상 머신이나 공개 검체(NIST CFReDS 등)에 데스크톱 앱이 있다면 다음을 풀어 봅니다.

1. 사용자 데이터 폴더는 `%APPDATA%\Claude` 와 패키지 안 `LocalCache\Roaming\Claude` 중 어디에 있는가?
2. `local-agent-mode-sessions` 의 세션 정보 파일에서 `cliSessionId` 를 뽑으면, 같은 이름의 기록 파일이 세션 폴더 안과 `.claude\projects` 중 어디에 있는가? `audit.jsonl` 도 있는가?
3. 세션 정보의 `spaceId` 를 `spaces.json` 과 맞추면 그 세션은 어느 스페이스에서, 어떤 폴더를 붙여 돌았는가?
4. `config.json` 의 `version_first_launch` 와 `updaterLastSeenVersion` 을 비교하면 처음 실행한 뒤 업데이트가 있었는가?

## 참고 문헌

1. Connect to local MCP servers (Model Context Protocol 문서) — https://modelcontextprotocol.io/docs/develop/connect-local-servers
2. Install Claude Desktop (Claude Help Center) — https://support.claude.com/en/articles/10065433-installing-claude-desktop
3. Deploy Claude Desktop for Windows (Claude Help Center) — https://support.claude.com/en/articles/12622703-deploy-claude-desktop-for-windows
4. Enterprise configuration for Claude Desktop (Claude Help Center) — https://support.claude.com/en/articles/12622667-enterprise-configuration-for-claude-desktop
5. Understanding how packaged desktop apps run on Windows (Microsoft Learn) — https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes
6. forensicdave/claude-forensics v0.1.1 (마지막 커밋 2026-06-16) — https://github.com/forensicdave/claude-forensics — `README.md`, `docs/claude_forensics.md`, `docs/claude-forensics.md`, `claude_forensics.py`(`process_cowork`, `summarise_audit`, `process_agent_sessions`), `claude-forensics.sh`(phase 0)
7. kenn-io/agentsview (2026-09-25 판) — https://github.com/kenn-io/agentsview — `internal/parser/cowork_paths.go`, `internal/parser/cowork.go`, `internal/parser/cowork_provider.go`, `docs/internal/session-format-sources.md`
