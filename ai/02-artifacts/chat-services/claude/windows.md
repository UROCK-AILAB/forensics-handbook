---
title: "Claude Windows 앱"
parent: "Claude"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 160
---

# Windows 앱 (Windows)

Windows 의 Claude 데스크톱 앱은 MSIX 패키지로 깔리고, 패키지 폴더 안에 크롬 계열 저장소와 앱이 직접 쓰는 JSON 설정 파일을 남깁니다. 대화 원본은 계정 서버에 있고, 기기에서는 설치·실행·설정·연결한 도구의 흔적을 주로 읽습니다.

> 확인 날짜: 2026-09. 공식 도움말과 MCP 문서(2026-09-25 열람), 기기 관찰을 함께 썼습니다. 기기 관찰은 스토어에서 받은 앱의 패키지 폴더를 읽기 전용으로 열어 폴더·파일 이름과 키 이름만 본 것이고 값은 가렸습니다(확인 범위: Windows 11, 2026-09). 관찰한 PC 의 앱 버전은 값이 가려져 확인하지 못했습니다.

## 무엇이 남나 · 왜 생기나

데스크톱 앱은 claude.ai 와 같은 계정으로 로그인해 쓰는 앱이라서, 대화는 웹판처럼 서버에 저장됩니다. 로컬 앱 폴더에 대화 본문이 남는지는 문서로 확인하지 못했고, 관찰에서도 값을 읽지 않았습니다. 대신 앱은 창 위치, 처음 실행한 때, 마지막으로 본 업데이트 버전, 마지막으로 쓴 계정 ID 같은 값을 JSON 파일에 적고, 화면을 그리는 크롬 계열 엔진이 캐시·쿠키·Local Storage·IndexedDB 를 따로 만듭니다. 로컬 MCP 서버를 연결하면 그 설정과 연결 로그도 남습니다[1].

## 설치와 배포

조직 배포용으로는 MSIX 패키지가 x64 와 arm64 로 따로 있고[3], 개인 사용자는 다운로드 페이지에서 받은 파일을 열어 설치한 뒤 시작 메뉴에서 실행합니다[2]. 다운로드 페이지의 설치 파일 형식은 이번에 확인하지 못했습니다. 지원 OS 는 Windows 10 이상입니다[2]. 조직 배포 안내는 사용자별로 깔 때 `Add-AppxPackage` 를, 기기 전체에 제공할 때 `Add-AppxProvisionedPackage -Online` 을 쓴다고 설명하고, Intune·SCCM(MECM)·그룹 정책 소프트웨어 설치·DISM·PowerShell 을 배포 수단으로 듭니다[3]. 두 방식이 기기에 남기는 흔적의 차이는 확인하지 못했습니다.

앱은 약 4시간마다 새 버전을 확인하고 스스로 업데이트하며, 관리 정책 `disableAutoUpdates` 로 끌 수 있습니다[3][4]. Cowork 기능을 쓰려면 Windows 기능 VirtualMachinePlatform 이 켜져 있어야 합니다[3]. 앱 메뉴의 Help > Troubleshooting > Show Logs 로 로그 폴더를 열 수 있고, 배포 안내에는 진단 파일 `supported-features-info.json` 도 나옵니다[3].

## 위치

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%APPDATA%\Claude\claude_desktop_config.json` | 로컬 MCP 서버 설정(최상위 키 `mcpServers`) | 문서[1] |
| `%APPDATA%\Claude\logs\mcp.log` | MCP 연결과 실패 기록 | 문서[1] |
| `%APPDATA%\Claude\logs\mcp-server-<서버 이름>.log` | 그 서버가 표준 오류로 낸 출력 | 문서[1] |
| 패키지 폴더의 `LocalCache\Roaming\Claude\` | 크롬 계열 저장소와 앱 JSON 파일 | 관찰 |
| 패키지 폴더의 `LocalCache\Local\claude-cli-nodejs\Cache\` | MCP 로그로 보이는 JSON Lines 파일 | 관찰 |
| 패키지 폴더의 `AC\INetHistory\<이름>\container.dat` | 이름만 봄, 쓰임은 확인하지 못함 | 관찰 |
| `HKLM\SOFTWARE\Policies\Claude` | 기기 관리 정책 | 문서[4] |
| `HKCU\SOFTWARE\Policies\Claude` | 사용자 관리 정책 | 문서[4] |

관찰 메모는 패키지 폴더를 `%USERPROFILE%\Packages\<Claude 패키지>` 로 적었습니다(확인 범위: Windows 11, 2026-09). MSIX 앱 데이터는 보통 `%LOCALAPPDATA%\Packages` 아래에 있다고 알려져 있지만 이번에 연 Microsoft 문서에는 그 경로가 적혀 있지 않았고, 패키지 이름도 값이 가려져 모릅니다. 그래서 수집할 때는 경로를 짐작하지 말고 사용자 프로필에서 `LocalCache\Roaming\Claude` 폴더가 들어 있는 패키지 폴더를 찾아냅니다.

문서가 말하는 `%APPDATA%\Claude` 에 해당하는 폴더가 스토어 앱에서는 패키지 안 `LocalCache\Roaming\Claude` 로 보입니다(확인 범위: Windows 11, 2026-09). Microsoft 문서는 가상화된 패키지 앱이 Windows 10 1903 이후 `AppData` 의 Local·Roaming 아래에 새로 만드는 파일을 사용자·패키지별 전용 위치로 옮겨 쓰고, 파일을 열 때는 전용 위치를 먼저 찾고 없으면 실제 `AppData` 에서 연다고 설명합니다[5]. 이 앱이 가상화된 앱인지와 실제 `%APPDATA%\Claude` 에 파일이 생기는지는 확인하지 못해서, 두 곳을 모두 봅니다. 패키지 앱의 쓰기 위치가 옮겨지는 원리는 [Electron·웹뷰 앱의 저장 구조](../../../01-foundations/storage-model/electron-webview.md)를 봅니다. 관찰한 경로 목록에는 `logs` 폴더가 나오지 않았는데, 목록이 모든 경로를 담지 않아서 있다 없다를 가르지 않습니다.

## 구조

### 크롬 계열 저장소

`LocalCache\Roaming\Claude\` 아래에는 크롬 계열 브라우저 프로필과 같은 이름의 폴더와 파일이 있었습니다(확인 범위: Windows 11, 2026-09).

```
Cache\            Code Cache\        GPUCache\
DawnGraphiteCache\  DawnWebGPUCache\  Dictionaries\*.bdic
Crashpad\metadata   Crashpad\settings.dat
DIPS  DIPS-wal
File System\Origins\
IndexedDB\<이름>\   (CURRENT, LOCK, LOG, *.ldb, *.log)
Local Storage\leveldb\
Local State
InterestGroups
Network\Cookies  Network\Cookies-journal
Network\Network Persistent State  Network\TransportSecurity
Partitions\<이름>\...
ChromeNativeHost\chrome-native-host.exe
```

앱이 Electron 으로 만들어졌는지는 문서로 확인하지 못해서, "크롬 계열 저장소 모양이 보인다"까지만 씁니다. 폴더마다의 형식은 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)와 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html)에 있습니다. `ChromeNativeHost\chrome-native-host.exe` 는 이름으로 보아 브라우저 확장과 앱을 잇는 프로그램으로 보이지만 쓰임은 확인하지 못했습니다.

`Partitions` 아래에서는 `cowork-file-preview`, `launch-preview-static` 이라는 이름의 파티션을 보았습니다. `Partitions\cowork-file-preview\Network\Cookies` 는 SQLite 데이터베이스이고 표 `cookies` 와 `meta` 가 있었으며, `cookies` 의 칸은 크롬 계열 쿠키 DB 와 같았습니다(확인 범위: Windows 11, 2026-09).

```
cookies: creation_utc, host_key, top_frame_site_key, name, value,
         encrypted_value, path, expires_utc, is_secure, is_httponly,
         last_access_utc, has_expires, is_persistent, priority, samesite,
         source_scheme, source_port, last_update_utc, source_type,
         has_cross_site_ancestor
meta:    key, value
```

기본 `Network\Cookies` 와 `declarative_performance_observer.db`, `launch-preview-static` 파티션의 같은 파일들은 열리지 않았습니다(OperationalError, 확인 범위: Windows 11, 2026-09). 앱이 실행 중이라 잠겨 있었던 것으로 보이지만 원인은 따로 확인하지 않았습니다. 쿠키 값이 `encrypted_value` 칸에 보호돼 들어가는 원리는 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html)와 크롬 계열 페이지에서 다루고, 이 앱이 같은 방식을 쓰는지는 확인하지 못했습니다.

### 앱 JSON 파일

같은 폴더에는 앱이 직접 쓰는 JSON 파일이 있었고, 키 이름은 다음과 같았습니다(확인 범위: Windows 11, 2026-09). 뜻은 키 이름으로 짐작한 것이고 문서로 확인하지 않았습니다.

| 파일 | 키(일부) | 조사에 쓸 곳 |
|---|---|---|
| `config.json` | `first_launch_at`, `version_first_launch.at`, `version_first_launch.version`, `updaterLastSeenVersion`, `updaterBannerStagedAt.version`, `updaterBannerStagedAt.stagedAt`, `lastKnownAccountUuid`, `locale`, `userThemeMode`, `planUsageLastTrayOpenAt`, `terminalCliPowerShellPath`, `windowSizeWasSignedIn`, `quickWindowPosition.monitor.*` | 처음 실행한 때와 그때 버전, 마지막으로 본 버전, 마지막 계정 ID, 연결된 모니터 정보 |
| `claude_desktop_config.json` | `coworkUserFilesPath`, `preferences.localAgentModeTrustedFolders`, `preferences.remoteToolsDeviceName`, `preferences.coworkWebSearchEnabled`, `preferences.coworkBrowserToolsEnabled`, `preferences.coworkPreferredBrowser`, `preferences.coworkScheduledTasksEnabled`, `preferences.ccdScheduledTasksEnabled`, `preferences.ccRemoteControlDefaultEnabled`, `preferences.ccAutoArchiveInactiveDays`, `preferences.bypassPermissionsGateByAccount`, `preferences.keepAwakeEnabled`, `preferences.sidebarMode`, `preferences.epitaxyPrefs.*` | Cowork 작업 폴더, 신뢰한 폴더 목록, 켜 둔 에이전트 기능, 고정·별표 목록 |
| `bridge-state.json` | `enabled`, `environmentId`, `localSessionId`, `remoteSessionId`, `processedMessageUuids`, `pendingProcessedAcks`, `userConsented` (최상위 키 이름은 가림) | 원격 세션 연결 상태로 보임 |
| `plan-usage-history.json` | `version`, `samples[].org`, `samples[].t`, `samples[].u.fh`, `samples[].u.sd` | 요금제 사용량 표본으로 보임(칸 뜻은 확인하지 못함) |
| `buddy-tokens.json` | `tokens-today.date`, `tokens-today.tokens` | 날짜별 토큰 수로 보임 |
| `window-state.json` | `x`, `y`, `width`, `height`, `isMaximized`, `isFullScreen`, `displayBounds.*` | 창 크기와 위치 |
| `git-worktrees.json` | `schemaVersion`, `worktrees`, `untrackedDirGc.cwds`, `untrackedDirGc.roots`, `untrackedDirGc.sightings` | 앱이 다룬 코드 작업 폴더 |
| `mcp-user-tool-toggles.json` | `v`, `owners.*` | MCP 도구를 켜고 끈 기록으로 보임 |
| `extensions-blocklist.json` | `[].url`, `[].lastUpdated`, `[].entries[].id`, `.reason`, `.hash`, `.certificateFingerprint`, `.is_internal_dxt` | 확장 차단 목록 |
| `cowork-enabled-cli-ops.json` | `ownerAccountId` | 계정 ID |
| `ant-device-registry.json` | 키 이름 가림, 값은 문자열 | 확인하지 못함 |

관찰한 PC 의 `claude_desktop_config.json` 에는 `mcpServers` 키가 보이지 않았습니다. 문서가 MCP 설정 파일로 설명하는 파일과 이름이 같지만 앱 환경설정이 함께 들어 있어서, `mcpServers` 키가 없다는 사실은 이 PC 에서 로컬 MCP 서버를 이 파일로 설정하지 않았다는 뜻으로만 읽습니다. MCP 설정과 로그의 해석은 [MCP 서버와 도구 호출 기록](../../dev-agents/mcp.md)에서 다룹니다.

아래는 키 이름만 따서 새로 만든 `config.json` 예시이고, 값은 모두 지어낸 것입니다.

```json
{
  "first_launch_at": 1767225600000,
  "version_first_launch": { "at": 1767225600000, "version": "0.0.0-example" },
  "updaterLastSeenVersion": "0.0.0-example",
  "lastKnownAccountUuid": "00000000-0000-4000-8000-000000000000",
  "locale": "ko-KR"
}
```

### 패키지 안의 다른 폴더

`LocalCache\Local\claude-cli-nodejs\Cache\<이름>\` 아래에는 `mcp-logs-scheduled-tasks`, `mcp-logs-computer-use` 처럼 `mcp-logs-` 로 시작하는 폴더와 JSON Lines 파일이 있었고, 한 줄의 키는 `cwd`, `debug`, `sessionId`, `timestamp` 였습니다(확인 범위: Windows 11, 2026-09). 데스크톱 앱에서 시작한 Claude Code 세션의 기록은 `%USERPROFILE%\.claude` 쪽에 남아서 [Claude Code](../../dev-agents/claude-code/index.md)에서 다룹니다.

같은 `LocalCache\Local` 에는 Android SDK, NuGet, npm-cache, pip cache, GitHub CLI 의 device-id 같은 다른 개발 도구의 캐시 폴더도 있었습니다(확인 범위: Windows 11, 2026-09). 앱 안에서 돌린 도구가 쓴 파일이 패키지 안으로 옮겨진 것으로 보이지만 원인은 확인하지 못했습니다. 이런 폴더가 보여도 사용자가 그 도구를 따로 설치했다고 바로 쓰지 않고, 앱 밖의 설치 흔적과 비교합니다.

## 관리 정책

조직은 `HKLM\SOFTWARE\Policies\Claude`(기기)나 `HKCU\SOFTWARE\Policies\Claude`(사용자)에 정책을 넣고, 둘 다 있으면 기기 쪽이 우선합니다[4]. 문서에 나오는 정책 키 예는 다음과 같습니다[4].

```
disableAutoUpdates                 autoUpdaterEnforcementHours
isDesktopExtensionEnabled          isDesktopExtensionDirectoryEnabled
isClaudeCodeForDesktopEnabled      isLocalDevMcpEnabled
secureVmFeaturesEnabled (Cowork)   allowedWorkspaceFolders
forceLoginOrgUUID                  effortLevel
```

정책 키가 있으면 그 기기나 사용자에게 관리 정책이 놓여 있었다고 쓸 수 있습니다. 조직 계정의 관리자 쪽 기록은 [Claude 기업용 감사 로그](../../network-enterprise/claude-enterprise.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 패키지 폴더와 `LocalCache\Roaming\Claude` 가 있으면 이 Windows 계정에 앱이 설치됐고 한 번 이상 실행된 흔적이 있다고 쓸 수 있습니다. `config.json` 의 `lastKnownAccountUuid` 는 앱이 마지막으로 알던 계정 ID 를, `claude_desktop_config.json` 의 신뢰 폴더와 Cowork 경로는 사용자가 앱에 허락한 폴더를 알려 줍니다. `mcpServers` 설정과 MCP 로그가 있으면 로컬 MCP 서버를 연결했거나 연결하려 한 기록이 있다고 쓸 수 있습니다.

**증명하지 못하는 것.** 기기의 파일만으로는 대화 본문을 확인할 수 없고, 앱을 누가 조작했는지도 알 수 없습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 계정 ID 는 마지막 계정 하나만 가리켜서 그 전에 쓴 계정이 없었다는 근거가 되지 않습니다. 대화 내용이 필요하면 [계정 데이터 내보내기](export.md)를 씁니다.

## 시각 해석

`first_launch_at`, `version_first_launch.at`, `updaterBannerStagedAt.stagedAt`, `planUsageLastTrayOpenAt`, `samples[].t` 는 정수 시각이지만, 값을 보지 않아 단위(초·밀리초)와 기준을 확인하지 못했습니다. 자릿수로 단위를 판단하고, 파일 시스템 시각과 비교해 맞는지 봅니다. `version_first_launch` 는 이름으로 보아 처음 실행한 때의 버전과 시각이라서, 설치 시각을 가늠하는 데 파일 시스템 시각보다 먼저 봅니다. 앱은 약 4시간마다 새 버전을 확인해 스스로 적용해서[3], 앱 파일의 파일 시스템 시각을 처음 설치한 때로 보지 않습니다.

쿠키 DB 의 `creation_utc`, `last_access_utc`, `expires_utc` 는 크롬 계열 쿠키 시각과 같은 칸 이름이라서 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)의 시각 해석을 따릅니다. MCP 로그 줄의 `timestamp` 는 문자열이고, 시간대 표시가 붙어 있는지는 값을 보고 판단합니다. 정책 레지스트리 키는 키의 마지막 쓰기 시각으로 정책이 언제 바뀌었는지 가늠합니다. 여러 시각을 한 줄로 맞추는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

앱이 실행 중이면 쿠키 DB 같은 파일이 잠겨 열리지 않습니다. 앱을 닫은 뒤에 사본을 뜨거나 디스크 이미지에서 꺼내고, `-journal`·`-wal` 파일도 함께 가져옵니다. 수집 순서는 [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다.

관찰한 스토어판과 다운로드 페이지에서 받은 설치판이 같은 폴더 구조를 쓰는지는 확인하지 못했습니다. Microsoft 문서에 따르면 패키지 앱을 제거하면 전용 위치로 옮겨 쓴 `AppData` 파일도 함께 지워지므로[5], 앱을 지운 뒤에는 패키지 폴더가 남지 않을 수 있습니다. 패키지 폴더가 없다고 앱을 쓰지 않았다고 단정하지 말고, `%APPDATA%\Claude` 와 사용자 프로필 전체에서 `claude_desktop_config.json` 을 찾아봅니다. 반대로 패키지 안에 다른 개발 도구의 캐시가 섞여 있어서, 폴더 크기나 파일 수만 보고 앱을 많이 썼다고 판단하지 않습니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 JSON 명세와 위의 만든 예시로 짠 바이트이고, 실제 파일에서 뜬 것이 아닙니다. 실제 파일의 키 순서는 다를 수 있습니다. 첫 바이트가 `7B`(`{`)이고 따옴표(`22`) 뒤에 키 이름의 ASCII 가 이어지면 암호화하지 않은 평문 JSON 입니다.

```
만든 예시(명세로 만든 바이트)
00000000  7B 22 66 69 72 73 74 5F 6C 61 75 6E 63 68 5F 61  {"first_launch_a
00000010  74 22 3A 31 37 36 37 32 32 35 36 30 30 30 30 30  t":1767225600000
```

**공개 도구로 한 번.** 사본으로 뜬 JSON 파일은 jq 같은 JSON 도구로 키 목록을 뽑고(`jq 'paths | map(tostring) | join(".")' config.json`), 쿠키 DB 사본은 SQLite 도구로 `cookies` 표의 `host_key` 와 시각 칸을 봅니다. 크롬 계열 폴더는 크롬 계열 브라우저 프로필을 읽는 공개 도구로 열 수 있는지 사본에서 시험해 봅니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [웹 브라우저](web.md) | 같은 PC 에서 브라우저로도 썼는지 |
| [Claude Code](../../dev-agents/claude-code/index.md) | 데스크톱 앱에서 시작한 코딩 세션 기록 |
| [MCP 서버와 도구 호출 기록](../../dev-agents/mcp.md) | 연결한 로컬 도구와 호출 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱이 접속한 시각 |
| [계정 데이터 내보내기](export.md) | 대화 본문과 시각 |

## 실습

직접 만든 시험용 Windows 가상 머신이나 공개 검체(NIST CFReDS 등)에 데스크톱 앱이 있다면 다음을 풀어 봅니다.

1. 패키지 폴더는 어디에 있고, `LocalCache\Roaming\Claude` 아래에 어떤 크롬 계열 폴더가 있는가?
2. `config.json` 의 `version_first_launch` 와 `updaterLastSeenVersion` 을 비교하면 처음 실행한 뒤 업데이트가 있었는가?
3. `claude_desktop_config.json` 에 `mcpServers` 키가 있다면, 그 서버 이름과 같은 이름의 MCP 로그가 있는가?

## 참고 문헌

1. Connect to local MCP servers (Model Context Protocol 문서) — https://modelcontextprotocol.io/docs/develop/connect-local-servers
2. Install Claude Desktop (Claude Help Center) — https://support.claude.com/en/articles/10065433-installing-claude-desktop
3. Deploy Claude Desktop for Windows (Claude Help Center) — https://support.claude.com/en/articles/12622703-deploy-claude-desktop-for-windows
4. Enterprise configuration for Claude Desktop (Claude Help Center) — https://support.claude.com/en/articles/12622667-enterprise-configuration-for-claude-desktop
5. Understanding how packaged desktop apps run on Windows (Microsoft Learn) — https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes
