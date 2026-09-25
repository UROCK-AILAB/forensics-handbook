---
title: "Claude Code Windows"
parent: "Claude Code"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 530
---

# Windows (Windows)

Windows 에서 Claude Code 는 사용자 프로필 아래 `.claude` 폴더와 `.claude.json` 파일에 기록·설정·로그인 정보를 평문으로 남기고, 조직이 거는 관리 정책은 `C:\Program Files\ClaudeCode` 폴더나 정책 레지스트리 키에서 읽습니다.

> 확인 날짜: 2026-09. 공식 문서(2026-09-25 열람)와 기기 관찰을 함께 썼습니다. 기기 관찰은 폴더·파일 이름과 키 이름만 본 것이고 값은 가렸습니다(확인 범위: Windows 11, 2026-09). 관찰한 PC 에 깔린 Claude Code 버전은 확인하지 않았고, 본문의 v2.1.x 같은 번호는 문서 문장을 그대로 옮긴 것입니다.

## 무엇이 남나 · 왜 생기나

Claude Code 는 터미널에서 도는 코딩 에이전트입니다. 모델 호출은 네트워크로 보내지만 파일 편집과 명령 실행은 사용자 PC 에서 하고, 대화 전문과 입력한 프롬프트 목록, 편집 전 파일 사본, 권한 규칙도 PC 의 사용자 폴더에 남습니다. 이 페이지는 Windows 에서 달라지는 설치 위치, 로그인 정보 보호 방식, 관리 정책 위치를 다루고, 기록 파일의 짜임은 [세션 기록 구조](transcripts.md)에서, 설정 파일의 뜻은 [설정·권한·훅](settings-permissions.md)에서 다룹니다.

## 위치

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%USERPROFILE%\.local\bin\claude.exe` | 네이티브 설치기로 깐 실행 파일 | 문서 |
| `%USERPROFILE%\.local\share\claude` | 설치한 버전 파일 | 문서 |
| `%USERPROFILE%\.claude\` | 사용자 데이터 폴더(기록·설정·캐시) | 문서, 관찰 |
| `%USERPROFILE%\.claude.json` | 로그인 세션, MCP 서버 설정, 프로젝트별 상태(작업 폴더 신뢰 결정 등), `/config` 전역 값 | 문서 |
| `%USERPROFILE%\.claude\.credentials.json` | 구독 계정 로그인 정보 | 문서, 관찰 |
| `%APPDATA%\Anthropic` | Anthropic 프로필 설정(ant CLI, 워크로드 ID 연동) | 문서 |
| `C:\Program Files\ClaudeCode\managed-settings.json`, `managed-settings.d\`, `managed-mcp.json` | 관리 정책 파일 | 문서 |
| `HKLM\SOFTWARE\Policies\ClaudeCode` 의 값 `Settings` | 관리 정책(REG_SZ 또는 REG_EXPAND_SZ 로 넣은 JSON 문자열) | 문서 |
| `HKCU\SOFTWARE\Policies\ClaudeCode` 의 값 `Settings` | 사용자가 쓸 수 있는 대체 정책 위치 | 문서 |
| 세션을 시작한 폴더의 `.claude\settings.local.json` | "다시 묻지 않기"로 허용한 규칙 | 문서 |

데이터 폴더는 `CLAUDE_CONFIG_DIR` 환경 변수로 옮길 수 있습니다. 표의 `.claude` 폴더가 없거나 비어 있으면 미사용으로 판단하기 전에 사용자·시스템 환경 변수에 이 값이 있는지 먼저 봅니다.

마지막 줄은 Windows 에서 달라지는 부분입니다. 문서는 "다시 묻지 않기"로 허용한 규칙이 v2.1.211 부터 저장소 루트의 `.claude\settings.local.json` 에 남는다고 설명하면서, Windows 에서는 저장소 루트를 쓰지 않고 세션을 시작한 폴더의 `.claude` 쪽 파일에 남긴다고 따로 적습니다. v2.1.211 전에는 OS 와 상관없이 시작 폴더에 남겼습니다. 저장소의 하위 폴더에서 시작한 세션이었다면 루트의 `.claude` 만 열어서는 규칙을 놓칠 수 있어서, 저장소 안의 `.claude` 폴더를 모두 찾아봅니다.

### 관찰한 폴더 모양

관찰한 PC 의 `%USERPROFILE%\.claude` 아래에서는 다음 항목을 보았습니다(확인 범위: Windows 11, 2026-09). 항목마다의 뜻은 [세션 기록 구조](transcripts.md)와 [설정·권한·훅](settings-permissions.md)에 있습니다.

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

`daemon\` 의 두 파일은 이름만 보았고 쓰임은 확인하지 않았습니다. 문서가 설명하는 `plans\`, `shell-snapshots\`, `session-env\`, `sessions\`, `tasks\`, `todos\` 같은 폴더는 이 PC 에서 보지 못했습니다. 그 기능을 쓰지 않았을 수도 있고 자동 삭제가 지웠을 수도 있어서, 폴더가 없다는 사실만으로 버전이나 사용 여부를 가르지 않습니다.

## 설치 방법별 차이

| 설치 방법 | 흔적이 남는 곳 | 업데이트 |
|---|---|---|
| 네이티브 설치기(`install.ps1`, `install.cmd`) | `%USERPROFILE%\.local\bin\claude.exe`, `%USERPROFILE%\.local\share\claude` | 백그라운드에서 스스로 업데이트 |
| WinGet(`Anthropic.ClaudeCode`) | 실행 파일 위치는 확인하지 못함 | 스스로 업데이트하지 않음(`CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE=1` 이면 대신 실행) |
| npm(`@anthropic-ai/claude-code`) | 확인하지 못함 | 확인하지 못함 |
| WSL 안에 설치 | WSL 리눅스 쪽 홈의 `~/.claude` | 리눅스 설치와 같음 |

네이티브 설치에는 관리자 권한이 필요 없어서, 관리자 권한이 없는 계정에서도 설치 흔적이 나올 수 있습니다. 업데이트 채널은 설정 키 `autoUpdatesChannel` 로 고르고 값은 `"latest"`(기본)와 `"stable"` 입니다. WSL 에 깐 경우에는 Windows 사용자 폴더가 아니라 WSL 배포판의 리눅스 홈에 기록이 쌓이지만, 배포판 파일 안의 실제 경로는 확인하지 못했습니다.

명령을 실행하는 도구도 환경에 따라 다릅니다. Git for Windows 가 깔려 있으면 Git Bash 를 Bash 도구로 쓰고, 없으면 PowerShell 도구를 씁니다. Git 이 있어도 claude.ai·Console 계정에서는 PowerShell 도구가 기본으로 함께 켜져 있어서, 한 세션 기록에 두 도구의 호출이 섞일 수 있습니다. Git Bash 경로는 `CLAUDE_CODE_GIT_BASH_PATH` 로 지정합니다. 네이티브 Windows 에서는 샌드박스를 지원하지 않고 WSL 2 에서는 지원합니다. 기록에서 어떤 도구로 명령을 실행했는지 읽을 때 이 차이를 함께 봅니다.

## 로그인 정보 보호

`.credentials.json` 은 사용자 프로필 폴더의 접근 권한을 그대로 물려받아 기본으로 그 사용자 계정만 읽을 수 있고, 파일 자체는 따로 암호화하지 않습니다. [DPAPI](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html)나 [자격 증명 관리자](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/credentials/credential-manager-windows-vault.html)를 거치지 않는 평문 JSON 이라서, 이미지 사본에서도 바로 읽힙니다. macOS 는 같은 정보를 키체인에 넣어서 [macOS](macos.md) 페이지와 비교해 봅니다.

관찰한 파일에서는 최상위 키 `claudeAiOauth` 아래에 다음 키가 있었습니다(확인 범위: Windows 11, 2026-09).

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

키 이름으로 보아 `subscriptionType` 과 `rateLimitTier` 는 구독 종류와 사용량 등급을 담는 것으로 보이지만, 값은 확인하지 않았습니다. 토큰 값은 비밀이라 보고서와 작업 사본에 옮기지 않고, 파일과 키가 있었다는 사실과 만료 시각만 적습니다. 토큰이 남는 다른 곳은 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에 모아 두었습니다. 인증 방법이 여럿이라 이 파일 하나로 인증 방식을 단정하지 않고, [설정·권한·훅](settings-permissions.md)의 인증 절과 함께 봅니다.

## 관리 정책

조직은 `C:\Program Files\ClaudeCode\` 아래 파일이나 `HKLM\SOFTWARE\Policies\ClaudeCode` 의 `Settings` 값으로 정책을 겁니다. 예전 경로인 `C:\ProgramData\ClaudeCode\managed-settings.json` 은 지금 판에서 읽지 않아서, 그 자리에 파일이 있어도 정책이 적용됐다는 근거가 되지 않습니다. `HKCU\SOFTWARE\Policies\ClaudeCode` 의 값은 다른 관리 소스가 정책 키를 하나도 주지 않을 때만 쓰고, 사용자가 직접 쓸 수 있는 위치라서 조직 정책이 있었다는 증거로 보기 어렵습니다. 여러 소스 사이의 순서와 합치는 방식은 [설정·권한·훅](settings-permissions.md)에서 다룹니다.

## 스토어판 데스크톱 앱과 겹치는 부분

VS Code 확장, JetBrains 플러그인, 데스크톱 앱도 `~/.claude/` 에 씁니다. 그래서 `.claude` 폴더의 기록만으로는 터미널에서 썼는지 다른 앱에서 썼는지 가르기 어렵고, 기록 줄의 `entrypoint` 키를 함께 봅니다([세션 기록 구조](transcripts.md)).

스토어에서 받은 Claude 데스크톱 앱의 패키지 폴더 안에서는 `LocalCache\Local\claude-cli-nodejs\Cache\` 아래 JSON Lines 파일을 보았고, `mcp-logs-` 로 시작하는 폴더에 MCP 서버별 로그가 있었습니다(확인 범위: Windows 11, 2026-09). 한 줄의 키는 `cwd`, `debug`, `sessionId`, `timestamp` 였습니다. 스토어 앱이 아닌 일반 설치에서 `%LOCALAPPDATA%\claude-cli-nodejs` 가 생기는지는 확인하지 못했습니다. 데스크톱 앱 자체는 [Claude](../../chat-services/claude/index.md)에서, MCP 기록은 [MCP 서버와 도구 호출 기록](../mcp.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 실행 파일과 `.claude` 폴더가 있으면 이 Windows 계정에서 Claude Code 를 설치했거나 실행한 흔적이 있다고 쓸 수 있습니다. `.credentials.json` 이 있으면 이 프로필에 구독 계정 로그인 정보가 저장돼 있었다고 쓸 수 있고, 정책 파일이나 HKLM 값이 있으면 그 기기에 관리 정책이 놓여 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 폴더와 로그인 파일은 그 계정으로 누가 키보드 앞에 앉아 있었는지 알려 주지 않습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 클라우드에서 돈 세션은 PC 에 기록이 없을 수 있고 로컬 기록도 기본 30일 뒤 지워져서, 흔적이 없다고 사용하지 않았다고 볼 수는 없습니다.

## 시각 해석

네이티브 설치는 백그라운드에서 스스로 업데이트하기 때문에, 실행 파일이나 버전 파일의 파일 시스템 시각을 처음 설치한 때로 단정하지 않습니다. `.credentials.json` 의 `expiresAt`, `refreshTokenExpiresAt` 는 정수 시각이지만 단위(초·밀리초)는 값을 보지 않아 확인하지 못했고, 자릿수를 보고 판단합니다. 대화 시각은 기록 파일 안의 값이 더 정확하며 [세션 기록 구조](transcripts.md)의 시각 절을 따릅니다. 관찰한 PC 의 `.claude` 폴더 바로 아래에는 이름을 가린 JSON 파일 하나에 `version_from`, `version_to`, `outcome`, `status`, `error_code`, `path`, `timestamp` 키가 있었습니다(확인 범위: Windows 11, 2026-09). 문서에는 `claude doctor` 가 가장 최근 업데이트 시도의 결과를 보여 준다고만 나와 있고, 이 파일이 그 기록인지는 확인하지 못했습니다. 키 이름으로 보아 업데이트 결과를 적는 파일로 보여 업데이트 시각을 가늠하는 데 참고할 수 있습니다. 정책 레지스트리 키는 키의 마지막 쓰기 시각으로 정책이 언제 바뀌었는지 가늠해 볼 수 있습니다.

## 함정과 한계

표의 경로가 비어 있어도 쓰지 않았다고 단정하기 전에 몇 가지를 먼저 봅니다. `CLAUDE_CONFIG_DIR` 로 데이터 폴더를 옮겼을 수 있고, WSL 안에 깔았다면 Windows 쪽 사용자 폴더가 아니라 배포판 안의 리눅스 홈에 기록이 있습니다. `/logout` 은 로그인 정보를 지우므로 `.credentials.json` 이 없다고 로그인한 적이 없다고 보지 않습니다. 반대로 `C:\ProgramData\ClaudeCode` 에 정책 파일이 있어도 지금 판은 그 파일을 읽지 않으므로 정책이 적용됐다는 근거로 쓰지 않습니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 JSON 명세와 관찰한 최상위 키 이름으로 만든 예시 바이트이고, 실제 파일에서 뜬 것이 아닙니다. 파일 첫 바이트가 `7B`(`{`)이고, 공백·줄바꿈을 건너뛴 뒤 `claudeAiOauth` 의 ASCII 가 이어지면 암호화하지 않은 평문 JSON 입니다.

```
만든 예시(명세로 만든 바이트)
00000000  7B 22 63 6C 61 75 64 65 41 69 4F 61 75 74 68 22  {"claudeAiOauth"
```

**공개 도구로 한 번.** 살아 있는 PC 에서는 PowerShell 로 서명과 폴더, 정책 값을 읽기만 합니다. 서명자가 "Anthropic, PBC" 로 나오는지 봅니다. 이미지 사본이라면 NTUSER.DAT 와 SOFTWARE 하이브를 Registry Explorer 같은 공개 도구로 열어 같은 키를 봅니다. 아래 사용자 이름은 만든 예시입니다.

```powershell
# 만든 예시: 사용자 examiner01
Get-AuthenticodeSignature "C:\Users\examiner01\.local\bin\claude.exe"
Get-ChildItem -Force "C:\Users\examiner01\.claude" | Select-Object Name, Length, LastWriteTimeUtc
reg query "HKLM\SOFTWARE\Policies\ClaudeCode" /v Settings
reg query "HKCU\SOFTWARE\Policies\ClaudeCode" /v Settings
```

## 교차 검증

`.claude` 폴더의 파일 시각과 기록 시각을 [Windows 타임라인](https://urock-ailab.github.io/forensics-handbook-windows/03-techniques/analysis/timeline/index.html)에 함께 올리고, 같은 시간대의 [네트워크 기록](../../network-enterprise/network-traces.md)에 모델 호출 흔적이 있는지 봅니다. 에이전트가 실행한 명령과 바꾼 파일은 [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)의 순서로 따라가고, 수집 범위는 [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다.

## 실습

공개 검체에 Claude Code 흔적이 들어 있는지는 확인하지 못했습니다. 시험용 가상 머신에 직접 깔고 짧은 세션을 몇 번 돌린 뒤 이미지를 떠서 풀어 봅니다.

1. 실행 파일의 서명자와 파일 시각, `.claude` 폴더의 생성 시각은 서로 어떤 순서입니까?
2. `CLAUDE_CONFIG_DIR` 을 다른 폴더로 지정하고 세션을 돌리면 어느 폴더에 무엇이 생깁니까?
3. 하위 폴더에서 세션을 시작하고 "다시 묻지 않기"로 명령을 허용하면 `settings.local.json` 은 어느 폴더에 생깁니까?
4. HKCU 에만 정책 값을 넣었을 때와 HKLM 에도 넣었을 때 `/status` 의 `Setting sources` 줄은 어떻게 다릅니까?

## 참고 문헌

1. Settings files and precedence — https://code.claude.com/docs/en/settings
2. Data usage — https://code.claude.com/docs/en/data-usage
3. .claude 폴더 파일·폴더 참조(claude-directory) — https://code.claude.com/docs/en/claude-directory
4. Deploy managed settings — https://code.claude.com/docs/en/managed-settings
5. Authentication — https://code.claude.com/docs/en/authentication
6. Configure permissions — https://code.claude.com/docs/en/permissions
7. Advanced setup — https://code.claude.com/docs/en/setup
