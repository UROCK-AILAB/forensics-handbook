---
title: "Claude Code Windows"
parent: "Claude Code"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 560
---

# Windows

Windows 에서 Claude Code 는 사용자 프로필 아래 `.claude` 폴더와 `.claude.json` 파일에 기록·설정·로그인 정보를 평문으로 남기고, 조직이 거는 관리 정책은 `C:\Program Files\ClaudeCode` 폴더나 정책 레지스트리 키에서 읽습니다. 데스크톱 앱에서 Claude Code 나 Cowork 를 썼다면 앱 데이터 폴더에도 세션 정보가 남아서, 두 곳을 함께 수집합니다.


## 무엇을 기록하나 · 왜 생기나

Claude Code 는 터미널에서 도는 코딩 에이전트입니다. 모델 호출은 네트워크로 보내지만 파일 편집과 명령 실행은 사용자 PC 에서 하고, 대화 전문과 입력한 프롬프트 목록, 편집 전 파일 사본, 권한 규칙도 PC 의 사용자 폴더에 남습니다. 이 페이지는 Windows 에서 달라지는 설치 위치, 로그인 정보 보호 방식, 관리 정책 위치, 데스크톱 앱 폴더까지 넣은 수집 범위를 다룹니다. 기록 파일의 짜임은 [세션 기록 구조](transcripts.md)에서, 설정 파일의 뜻은 [설정·권한·훅](settings-permissions.md)에서 다룹니다.

## 위치와 버전별 차이

### 경로 표

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%USERPROFILE%\.local\bin\claude.exe` | 네이티브 설치기로 깐 실행 파일 | 문서[7] |
| `%USERPROFILE%\.local\share\claude` | 설치한 버전 파일 | 문서[7] |
| `%USERPROFILE%\.claude\` | 사용자 데이터 폴더(기록·설정·캐시) | 문서[3], 도구[8], 관찰 |
| `%USERPROFILE%\.claude.json` | 로그인 세션, MCP 서버 설정, 프로젝트별 상태(작업 폴더 신뢰 결정 등), `/config` 전역 값 | 문서[1] |
| `%USERPROFILE%\.claude\.credentials.json` | 구독 계정 로그인 정보 | 문서[5], 관찰 |
| `%APPDATA%\Anthropic` | Anthropic 프로필 설정(ant CLI, 워크로드 ID 연동) | 문서[1] |
| `C:\Program Files\ClaudeCode\managed-settings.json`, `managed-settings.d\`, `managed-mcp.json` | 관리 정책 파일 | 문서[4] |
| `HKLM\SOFTWARE\Policies\ClaudeCode` 의 값 `Settings` | 관리 정책(REG_SZ 또는 REG_EXPAND_SZ 로 넣은 JSON 문자열) | 문서[4] |
| `HKCU\SOFTWARE\Policies\ClaudeCode` 의 값 `Settings` | 사용자가 쓸 수 있는 대체 정책 위치 | 문서[4] |
| 세션을 시작한 폴더의 `.claude\settings.local.json` | "다시 묻지 않기"로 허용한 규칙 | 문서[6] |
| 데스크톱 앱 데이터 폴더(아래 절) | 앱에서 쓴 Claude Code·Cowork 세션 정보 | 도구[8][9] |

데이터 폴더는 `CLAUDE_CONFIG_DIR` 환경 변수로 옮길 수 있습니다. 표의 `.claude` 폴더가 없거나 비어 있으면 미사용으로 판단하기 전에 사용자·시스템 환경 변수에 이 값이 있는지 먼저 봅니다.

"다시 묻지 않기" 규칙 줄은 Windows 에서 달라지는 부분입니다. 이 규칙은 v2.1.211 부터 저장소 루트의 `.claude\settings.local.json` 에 남지만, Windows 에서는 저장소 루트를 쓰지 않고 세션을 시작한 폴더의 `.claude` 쪽 파일에 남습니다[6]. v2.1.211 전에는 OS 와 상관없이 시작 폴더에 남겼습니다. 저장소의 하위 폴더에서 시작한 세션이었다면 루트의 `.claude` 만 열어서는 규칙을 놓칠 수 있어서, 저장소 안의 `.claude` 폴더를 모두 찾아봅니다.

### 설치 방법별 차이

| 설치 방법 | 흔적이 남는 곳 | 업데이트 |
|---|---|---|
| 네이티브 설치기(`install.ps1`, `install.cmd`) | `%USERPROFILE%\.local\bin\claude.exe`, `%USERPROFILE%\.local\share\claude` | 백그라운드에서 스스로 업데이트 |
| WinGet(`Anthropic.ClaudeCode`) | 문서에 실행 파일 위치가 없어 검체로 확인 | 스스로 업데이트하지 않음(`CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE=1` 이면 대신 실행) |
| npm(`@anthropic-ai/claude-code`) | 문서에 실행 파일 위치가 없어 검체로 확인 | 문서에 설명이 없어 검체로 확인 |
| WSL 안에 설치 | WSL 배포판 리눅스 홈의 `~/.claude` | 리눅스 설치와 같음 |

WinGet·npm 설치는 문서에 실행 파일 위치가 없어서, 검체에서는 패키지 관리자의 설치 목록과 디스크 전체에서 이름이 `claude` 로 시작하는 실행 파일을 찾습니다. 네이티브 설치에는 관리자 권한이 필요 없어서, 관리자 권한이 없는 계정에서도 설치 흔적이 나올 수 있습니다[7]. 업데이트 채널은 설정 키 `autoUpdatesChannel` 로 고르고 값은 `"latest"`(기본)와 `"stable"` 입니다[7]. WSL 에 깐 경우에는 Windows 사용자 폴더가 아니라 배포판 안의 리눅스 홈에 기록이 쌓여서, 배포판을 따로 수집합니다.

명령을 실행하는 도구도 환경에 따라 다릅니다. Git for Windows 가 깔려 있으면 Git Bash 를 Bash 도구로 쓰고, 없으면 PowerShell 도구를 씁니다[7]. Git 이 있어도 claude.ai·Console 계정에서는 PowerShell 도구가 기본으로 함께 켜져 있어서, 한 세션 기록에 두 도구의 호출이 섞일 수 있습니다. Git Bash 경로는 `CLAUDE_CODE_GIT_BASH_PATH` 로 지정합니다. 네이티브 Windows 에서는 샌드박스를 지원하지 않고 WSL 2 에서는 지원합니다. 기록에서 어떤 도구로 명령을 실행했는지 읽을 때 이 차이를 함께 봅니다.

### Windows 에서 생기는 하위 폴더

`%USERPROFILE%\.claude` 아래에서 볼 수 있는 항목은 다음과 같습니다. 항목마다의 뜻은 [세션 기록 구조](transcripts.md)와 [설정·권한·훅](settings-permissions.md)에 있습니다.

```
.credentials.json
settings.json
stats-cache.json
history.jsonl
backups\
cache\
daemon\control.key
daemon\pipe.key
debug\latest
feedback\drafts\
file-history\
jobs\pins.json
jobs\<이름>\state.json
jobs\<이름>\timeline.jsonl
paste-cache\<파일>.txt
plugins\
projects\
```

Windows 판이 이 가운데 무엇을 쓰는지는 자료마다 다릅니다. claude-forensics v0.1.1(2026-06-16) 문서는 2026년 중반의 Windows 판 Claude Code 가 `history.jsonl`, `shell-snapshots/`, `paste-cache/`, `file-history/` 를 쓰지 않는 것으로 보인다고 했고, `projects/` 의 세션 기록, Cowork 세션 정보, `audit.jsonl` 을 포함한 Cowork 에이전트 기록은 그대로 뽑힌다고 했습니다[8]. 2026년 9월 Windows 기기에서는 이 네 가지 가운데 `history.jsonl`, `paste-cache\`, `file-history\` 가 있었고 `shell-snapshots\` 는 없었습니다. 시점이 달라서 어느 한쪽을 기준으로 삼지 않고, 검체마다 이 네 항목이 있는지부터 봅니다.

`plans\`, `session-env\`, `sessions\`, `tasks\`, `todos\` 폴더[3]는 없을 수도 있습니다. 그 기능을 쓰지 않았을 수도 있고 자동 정리가 지웠을 수도 있어서, 폴더가 없다는 사실만으로 판이나 사용 여부를 가르지 않습니다. `daemon\` 의 두 파일은 쓰임을 설명한 공개 자료가 없어서 검체로 확인해야 합니다.

### 데스크톱 앱 폴더와 수집 범위

Claude 데스크톱 앱에서 Claude Code 나 Cowork(로컬 에이전트 모드)를 쓰면 앱 데이터 폴더에도 세션 정보가 남습니다. Windows 검체에서는 `\Users\이름\.claude` 와 `\Users\이름\AppData\Roaming\Claude\` 두 폴더를 모두 떠야 전체를 볼 수 있습니다[8]. 스토어(MSIX) 설치의 앱 폴더는 `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude` 이고, 스토어가 아닌 설치나 예전 설치의 앱 폴더는 `%APPDATA%\Claude` 입니다[9]. claude-forensics 는 `AppData\Roaming\Claude` 한 곳만 다루므로, 검체에서는 두 곳을 모두 봅니다[8].

앱 폴더 아래에서 Claude Code 와 이어지는 항목은 다음과 같습니다.

| 앱 폴더 아래 경로 | 담긴 것 | 근거 |
|---|---|---|
| `claude-code-sessions\<orgUuid>\<accountUuid>\local_<sessionId>.json` | 앱 쪽 세션 정보(제목, 소유 조직·계정, 모델, 보관 여부, `cliSessionId`). claude-forensics 문서는 "Cowork 세션 메타데이터" 라고 부릅니다 | 도구[8] |
| `local-agent-mode-sessions\<orgUuid>\<accountUuid>\local_<sessionId>.json` | Cowork 에이전트 세션 정보(제목, 시스템 프롬프트, 허용 목록, 소유자) | 도구[8] |
| `local-agent-mode-sessions\<orgUuid>\<accountUuid>\local_<sessionId>\audit.jsonl` | Cowork 에이전트 대화 기록 전체와 실행 비용 | 도구[8] |
| `local-agent-mode-sessions\…\local_<sessionId>\.claude\projects\…\<cliSessionId>.jsonl` | Claude Code 형식으로 적은 Cowork 기록 | 도구[9] |
| `local-agent-mode-sessions\<orgUuid>\<accountUuid>\spaces.json` | Cowork 공간 이름과 폴더 | 도구[8] |
| `cowork-enabled-cli-ops.json`, `claude_desktop_config.json`, `config.json`, `buddy-tokens.json`, `ant-did` | claude-forensics 가 함께 떠 오는 설정 파일 | 도구[8] |

`claude-code-sessions` 의 `cliSessionId` 값은 `.claude\projects` 아래 기록 파일 이름과 같아서, 이 값으로 앱 쪽 제목·계정 정보와 `.claude` 쪽 대화 기록을 잇습니다[8]. Cowork 의 Claude Code 형식 기록은 사용자 `.claude` 가 아니라 앱 폴더의 세션 폴더 안에 있어서, `.claude` 만 떠 오면 빠집니다[9].

claude-forensics 는 앱 폴더 전체가 아니라 `claude-code-sessions`, `local-agent-mode-sessions` 와 위 설정 파일만 복사합니다. 약 12GB 인 `vm_bundles\` 와 `Cache\`, `Code Cache\` 같은 캐시는 뺍니다[8]. 선별 수집이라면 이 목록을 최소 범위로 삼으면 되고, 각 파일의 키와 시각, 크롬 계열 저장소까지 넣은 앱 폴더 전체 구조는 [Claude — Windows 앱](../../chat-services/claude/windows.md)에서 다룹니다.

스토어판 패키지 폴더의 `LocalCache\Local\claude-cli-nodejs\Cache\` 아래에는 `mcp-logs-` 로 시작하는 폴더가 생기고, 그 안의 JSON Lines 파일 한 줄에는 `cwd`, `debug`, `sessionId`, `timestamp` 키가 있습니다. MCP 기록을 읽는 법은 [MCP 서버와 도구 호출 기록](../mcp.md)에서 다룹니다.

## 구조

### 기록 폴더 이름

`projects\` 아래 폴더 이름은 작업 폴더 경로에서 ASCII 영문자·숫자·`-` 만 남기고 나머지 글자를 모두 `-` 로 바꾼 값입니다(Claude Code 2.1.233 기준)[9]. Windows 경로는 드라이브 문자 뒤의 `:\` 가 `--` 로 바뀝니다. 한글 같은 ASCII 밖 글자도 `-` 로 바뀌어서 폴더 이름만으로는 원래 경로를 알아볼 수 없습니다.

```
만든 예시
작업 폴더   C:\Work\my_app
기록 폴더   %USERPROFILE%\.claude\projects\C--Work-my-app\
```

이름을 되돌리면 원래 있던 `-` 와 바뀐 `-` 를 가를 수 없으므로, 폴더 이름보다 기록 줄의 `cwd` 값을 먼저 씁니다[8]. 기록 줄의 짜임은 [세션 기록 구조](transcripts.md)에서 다룹니다.

### 로그인 정보 파일

`.credentials.json` 은 사용자 프로필 폴더의 접근 권한을 그대로 물려받아 기본으로 그 사용자 계정만 읽을 수 있고, 파일 자체는 따로 암호화하지 않습니다[5]. [DPAPI](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html)나 [자격 증명 관리자](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/credentials/credential-manager-windows-vault.html)를 거치지 않는 평문 JSON 이라서, 이미지 사본에서도 바로 읽힙니다. macOS 는 같은 정보를 키체인에 넣어서 [macOS](macos.md) 페이지와 비교해 봅니다.

파일의 최상위 키 `claudeAiOauth` 아래에는 다음 키가 있습니다.

```
claudeAiOauth
  accessToken
  refreshToken
  expiresAt              (정수)
  refreshTokenExpiresAt  (정수)
  scopes                 (목록)
  subscriptionType
  rateLimitTier
```

토큰 값은 비밀이라 보고서와 작업 사본에 옮기지 않고, 파일과 키가 있었다는 사실과 만료 시각만 적습니다. 토큰이 남는 다른 곳은 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에 모아 두었습니다. 인증 방법이 여럿이라 이 파일 하나로 인증 방식을 단정하지 않고, [설정·권한·훅](settings-permissions.md)의 인증 절과 함께 봅니다.

### 관리 정책

조직은 `C:\Program Files\ClaudeCode\` 아래 파일이나 `HKLM\SOFTWARE\Policies\ClaudeCode` 의 `Settings` 값으로 정책을 겁니다[4]. 예전 경로인 `C:\ProgramData\ClaudeCode\managed-settings.json` 은 지금 판에서 읽지 않아서, 그 자리에 파일이 있어도 정책이 적용됐다는 근거가 되지 않습니다. `HKCU\SOFTWARE\Policies\ClaudeCode` 의 값은 다른 관리 소스가 정책 키를 하나도 주지 않을 때만 쓰고, 사용자가 직접 쓸 수 있는 위치라서 조직 정책이 있었다는 증거로 보기 어렵습니다. 여러 소스 사이의 순서와 합치는 방식은 [설정·권한·훅](settings-permissions.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 실행 파일과 `.claude` 폴더가 있으면 이 Windows 계정에서 Claude Code 를 설치했거나 실행한 흔적이 있다고 쓸 수 있습니다. `.credentials.json` 이 있으면 이 프로필에 구독 계정 로그인 정보가 저장돼 있었다고 쓸 수 있고, 정책 파일이나 HKLM 값이 있으면 그 기기에 관리 정책이 놓여 있었다고 쓸 수 있습니다. 앱 폴더의 `claude-code-sessions` 파일이 `cliSessionId` 로 `.claude` 의 기록과 이어지면, 그 세션을 데스크톱 앱에서 열었고 어느 조직·계정 폴더 아래에 기록됐는지까지 쓸 수 있습니다[8].

**증명하지 못하는 것.** 폴더와 로그인 파일은 그 계정으로 누가 키보드 앞에 앉아 있었는지 알려 주지 않습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 클라우드에서 돈 세션은 PC 에 기록이 없을 수 있고 로컬 기록도 기본 30일 뒤 지워져서[2], 흔적이 없다고 사용하지 않았다고 볼 수는 없습니다.

## 시각 해석

네이티브 설치는 백그라운드에서 스스로 업데이트하기 때문에, 실행 파일이나 버전 파일의 파일 시스템 시각을 처음 설치한 때로 단정하지 않습니다. `.credentials.json` 의 `expiresAt`, `refreshTokenExpiresAt` 는 정수 시각이고 단위를 적은 공개 자료가 없어서, 13자리면 1970-01-01 UTC 기준 밀리초, 10자리면 초로 보고 파일 시각과 맞는지 확인합니다. 대화 시각은 기록 파일 안의 값이 더 정확하며 [세션 기록 구조](transcripts.md)의 시각 절을 따릅니다. 앱 폴더 쪽 세션 정보의 `createdAt`, `lastActivityAt` 해석은 [Claude — Windows 앱](../../chat-services/claude/windows.md)의 시각 절을 따릅니다.

`.claude` 폴더 바로 아래에 `version_from`, `version_to`, `outcome`, `status`, `error_code`, `path`, `timestamp` 키가 든 JSON 파일이 있을 수 있습니다. 이 파일을 설명한 공개 자료가 없어서, 판이 바뀐 시각의 근거로 쓰려면 시험 기기에서 업데이트 전후로 파일을 비교해 뜻을 먼저 확인합니다. 정책 레지스트리 키는 키의 마지막 쓰기 시각으로 정책이 언제 바뀌었는지 가늠해 볼 수 있습니다.

## 함정과 한계

표의 경로가 비어 있어도 쓰지 않았다고 단정하기 전에 몇 가지를 먼저 봅니다. `CLAUDE_CONFIG_DIR` 로 데이터 폴더를 옮겼을 수 있고, WSL 안에 깔았다면 Windows 쪽 사용자 폴더가 아니라 배포판 안의 리눅스 홈에 기록이 있습니다. 데스크톱 앱에서 쓴 Cowork 기록은 앱 폴더 안에만 있어서, `.claude` 만 수집하면 통째로 빠집니다. `history.jsonl` 같은 항목이 없는 것은 판에 따른 차이일 수 있다는 점도 위 출처 비교를 따라 함께 적습니다.

`/logout` 은 로그인 정보를 지우므로 `.credentials.json` 이 없다고 로그인한 적이 없다고 보지 않습니다[5]. 반대로 `C:\ProgramData\ClaudeCode` 에 정책 파일이 있어도 지금 판은 그 파일을 읽지 않으므로 정책이 적용됐다는 근거로 쓰지 않습니다. 기록 파일은 평문이고 사용자가 고칠 수 있어서, 깨진 줄이나 앞뒤가 맞지 않는 줄은 기록 도중 멈춘 흔적이거나 손으로 고친 흔적일 수 있습니다[8].

## 직접 분석해 보기

**헥스로 한 번.** 아래는 JSON 명세와 최상위 키 이름으로 만든 예시 바이트이고, 실제 파일에서 뜬 것이 아닙니다. 파일 첫 바이트가 `7B`(`{`)이고, 공백·줄바꿈을 건너뛴 뒤 `claudeAiOauth` 의 ASCII 가 이어지면 암호화하지 않은 평문 JSON 입니다.

```
만든 예시(명세로 만든 바이트)
00000000  7B 22 63 6C 61 75 64 65 41 69 4F 61 75 74 68 22  {"claudeAiOauth"
```

**공개 도구로 한 번.** 살아 있는 PC 에서는 PowerShell 로 서명과 폴더, 정책 값, 앱 폴더 위치를 읽기만 합니다. 서명자가 "Anthropic, PBC" 로 나오는지 봅니다. 이미지 사본이라면 NTUSER.DAT 와 SOFTWARE 하이브를 Registry Explorer 같은 공개 도구로 열어 같은 키를 봅니다. 아래 사용자 이름은 만든 예시입니다.

```powershell
# 만든 예시: 사용자 examiner01
Get-AuthenticodeSignature "C:\Users\examiner01\.local\bin\claude.exe"
Get-ChildItem -Force "C:\Users\examiner01\.claude" | Select-Object Name, Length, LastWriteTimeUtc
reg query "HKLM\SOFTWARE\Policies\ClaudeCode" /v Settings
reg query "HKCU\SOFTWARE\Policies\ClaudeCode" /v Settings
Test-Path "C:\Users\examiner01\AppData\Roaming\Claude"
Test-Path "C:\Users\examiner01\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude"
```

떠 온 사본은 claude-forensics 로 읽을 수 있습니다. 이 도구는 macOS·Linux 에서 돌고, Windows 에서 떠 온 `.claude` 와 앱 폴더 사본을 함께 받습니다[8]. Windows 사본은 앱 폴더 위치를 스스로 찾지 못해서 `-w` 로 직접 알려 줍니다. 스토어판이면 `LocalCache\Roaming\Claude` 사본을 줍니다.

```sh
# 만든 예시 경로
./claude-forensics.sh \
    -w /mnt/evidence/examiner01/AppData/Roaming/Claude \
    /mnt/evidence/examiner01/.claude \
    ./out
```

결과에는 `.claude` 쪽 세션과 프롬프트, `claude-code-sessions` 를 정리한 `cowork-sessions.jsonl`, `audit.jsonl` 을 정리한 `cowork-agent-sessions.jsonl` 이 따로 나오고, 모든 결과 파일의 SHA-256 목록도 함께 만들어집니다[8]. claude-forensics 문서는 시험한 Claude Code 판을 적지 않았고 도구 판은 v0.1.1(2026-06-16)이라서, 지금 판의 검체에서는 경고 줄(`WARNING no X under …`)로 빠진 항목을 먼저 봅니다.

## 교차 검증

`.claude` 폴더의 파일 시각과 기록 시각을 [Windows 타임라인](https://urock-ailab.github.io/forensics-handbook-windows/03-techniques/analysis/timeline/index.html)에 함께 올리고, 같은 시간대의 [네트워크 기록](../../network-enterprise/network-traces.md)에 모델 호출 흔적이 있는지 봅니다. 데스크톱 앱에서 연 세션은 [Claude — Windows 앱](../../chat-services/claude/windows.md)의 세션 정보와 `cliSessionId` 로 맞춰 봅니다. 에이전트가 실행한 명령과 바꾼 파일은 [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)의 순서로 따라가고, 수집 범위는 [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다.

## 실습

시험용 가상 머신에 Claude Code 와 데스크톱 앱을 직접 깔고 짧은 세션을 몇 번 돌린 뒤 이미지를 떠서 풀어 봅니다.

1. 실행 파일의 서명자와 파일 시각, `.claude` 폴더의 생성 시각은 서로 어떤 순서입니까?
2. `CLAUDE_CONFIG_DIR` 을 다른 폴더로 지정하고 세션을 돌리면 어느 폴더에 무엇이 생깁니까?
3. 하위 폴더에서 세션을 시작하고 "다시 묻지 않기"로 명령을 허용하면 `settings.local.json` 은 어느 폴더에 생깁니까?
4. HKCU 에만 정책 값을 넣었을 때와 HKLM 에도 넣었을 때 `/status` 의 `Setting sources` 줄은 어떻게 다릅니까?
5. 그 판에서 `history.jsonl`, `shell-snapshots\`, `paste-cache\`, `file-history\` 가운데 어느 것이 생깁니까?
6. 데스크톱 앱에서 Claude Code 세션을 열면 `claude-code-sessions` 의 `cliSessionId` 와 같은 이름의 기록 파일이 `.claude\projects` 에 생깁니까?

## 참고 문헌

1. Settings files and precedence — https://code.claude.com/docs/en/settings
2. Data usage — https://code.claude.com/docs/en/data-usage
3. .claude 폴더 파일·폴더 참조(claude-directory) — https://code.claude.com/docs/en/claude-directory
4. Deploy managed settings — https://code.claude.com/docs/en/managed-settings
5. Authentication — https://code.claude.com/docs/en/authentication
6. Configure permissions — https://code.claude.com/docs/en/permissions
7. Advanced setup — https://code.claude.com/docs/en/setup
8. forensicdave, claude-forensics v0.1.1(마지막 커밋 2026-06-16) — https://github.com/forensicdave/claude-forensics , `README.md`, `docs/claude_forensics.md`, `docs/claude-forensics.md`, `claude-forensics.sh`, `claude_forensics.py`
9. kenn-io, agentsview(2026-09-25 판) — https://github.com/kenn-io/agentsview , `internal/parser/cowork_paths.go`, `internal/parser/cowork.go`, `docs/internal/session-format-sources.md`(last_edited 2026-09-11)
