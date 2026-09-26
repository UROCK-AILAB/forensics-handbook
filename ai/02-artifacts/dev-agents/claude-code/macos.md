---
title: "Claude Code macOS"
parent: "Claude Code"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 570
---

# macOS

macOS 에서 Claude Code 는 기록과 설정을 다른 OS 와 같은 `~/.claude/` 와 `~/.claude.json` 에 두지만, 로그인 정보는 키체인에 넣고 키체인에 쓰지 못할 때만 파일로 남깁니다.

본문의 v2.1.x 같은 번호는 공식 문서에 적힌 버전이고, 앱이 자주 바뀌므로 검체의 파일 모양은 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

macOS 에서도 대화 전문, 입력한 프롬프트 목록, 편집 전 파일 사본은 홈 폴더의 `~/.claude/` 에 남고, VS Code 확장·JetBrains 플러그인·데스크톱 앱도 이 폴더에 씁니다[6]. 짜임은 [세션 기록 구조](transcripts.md)와 [설정·권한·훅](settings-permissions.md)에서 다룹니다. 이 페이지는 macOS 에서 달라지는 부분만 다룹니다. 설치 방식에 따라 옛 버전이 디스크에 남는 방식, 키체인에 들어가는 로그인 정보, 관리 정책 위치, 그리고 Claude 데스크톱 앱에서 돌린 Code 세션이 `~/Library/Application Support/Claude/` 에 남기는 메타데이터입니다.

## 위치와 버전별 차이

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `~/.local/bin/claude` | 네이티브 설치의 실행 링크(심볼릭 링크) | 문서[6] |
| `~/.local/share/claude/versions/` | 네이티브 설치로 받은 실행 파일(버전 번호가 파일 이름) | 문서[6] |
| `~/.claude/` | 사용자 데이터 폴더(기록·설정·캐시) | 문서[2] |
| `~/.claude.json` | 로그인 세션, MCP 서버 설정, 프로젝트별 상태, `/config` 전역 값 | 문서[2] |
| 로그인 키체인 | 구독 계정 로그인 정보 | 문서[4] |
| `~/.claude/.credentials.json` | 키체인에 쓰지 못했을 때의 로그인 정보(파일 모드 0600) | 문서[4] |
| `~/.config/anthropic` | Anthropic 프로필 설정(ant CLI, 워크로드 ID 연동) | 문서[4] |
| `/Library/Application Support/ClaudeCode/managed-settings.json`, `managed-settings.d/`, `managed-mcp.json` | 관리 정책 파일 | 문서[3] |
| 관리 환경설정 도메인 `com.anthropic.claudecode` | MDM 구성 프로파일로 내려온 정책 | 문서[3] |
| `~/Library/Application Support/Claude/claude-code-sessions/` | 데스크톱 앱에서 돌린 Code 세션의 메타데이터 | 도구[7] |
| `~/Library/Application Support/Claude/local-agent-mode-sessions/` | Cowork 세션 메타데이터와 대화 기록 | 도구[7][8] |

`CLAUDE_CONFIG_DIR` 환경 변수로 데이터 폴더를 옮길 수 있고, 이렇게 옮기면 키체인 항목도 그 폴더에 묶여 따로 생깁니다[4]. 한 사용자 계정에 키체인 항목이 여럿 보이면 데이터 폴더도 여럿일 수 있어서, 셸 설정 파일에서 이 변수를 찾아봅니다.

### 설치 방법별 차이

| 설치 방법 | 옛 버전이 남는 곳 | 업데이트 |
|---|---|---|
| 네이티브 설치기(`install.sh`) | `~/.local/share/claude/versions/` | 스스로 업데이트 |
| Homebrew `claude-code`(stable 채널), `claude-code@latest`(latest 채널) | Homebrew 폴더, `brew cleanup` 전까지 | 기본으로 하지 않음. `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE=1` 이면 백그라운드에서 올림 |
| npm(`@anthropic-ai/claude-code`) | npm 전역 폴더. 옛 버전이 남는지는 문서에 설명이 없어 검체에서 확인 | npm 전역 폴더에 쓸 수 있으면 스스로 업데이트 |

네이티브 설치에서 `~/.local/bin/claude` 는 `versions/` 안의 한 버전을 가리키는 심볼릭 링크입니다[6]. 업데이트는 백그라운드에서 받고 다음 실행부터 적용되므로, 링크가 가리키는 곳은 마지막으로 쓴 버전이 아니라 다음 실행에 쓸 버전일 수 있습니다. 사용자가 링크를 자기 스크립트나 다른 링크로 바꾸면 Claude Code 는 어느 버전이 필요한지 가릴 수 없어 설치한 모든 버전을 디스크에 남기고, v2.1.207 전에는 업데이트할 때마다 바꾼 링크를 다시 덮어썼습니다[6]. 링크를 바꾸지 않은 보통 설치에서 몇 개의 버전이 남는지는 판마다 다를 수 있어 `versions/` 목록으로 확인합니다. Homebrew 로 깐 경우에는 `brew cleanup` 을 돌리기 전까지 옛 버전이 남아서, Homebrew 폴더의 버전 목록으로 어떤 버전을 거쳐 왔는지 가늠해 볼 수 있습니다. npm 패키지도 `@anthropic-ai/claude-code-darwin-arm64` 같은 플랫폼별 패키지로 같은 실행 파일을 받아 연결합니다[6]. 실행 파일은 "Anthropic PBC" 가 서명하고 Apple 공증을 받았습니다[6].

### 버전에 따라 달라지는 곳

| 항목 | 차이 |
|---|---|
| 붙여 넣은 이미지·첨부 이미지 | v2.1.274 이하는 `~/.claude/image-cache/` 아래 세션별 폴더, 그 뒤는 `CLAUDE_CODE_TMPDIR` 이 정하는 임시 폴더 아래 세션별 `images/`[2] |
| 권한 거부 규칙 | v2.1.268 부터 `/etc` 가 `/private/etc` 로 풀리는 것처럼 심볼릭 링크 폴더를 거쳐 적은 거부·묻기 규칙을 실제 위치에도 적용(macOS·Linux)[5] |

새 판에서 이미지가 실제로 놓이는 곳은 검체의 `CLAUDE_CODE_TMPDIR` 값과 임시 폴더를 보고 확인합니다. 이미지가 `image-cache` 에 없다고 첨부가 없었다고 보지 않고, 먼저 설치 버전을 확인합니다.

## 구조

### 프로젝트 폴더 이름

기록 파일은 `~/.claude/projects/` 아래, 작업 경로를 바꿔 만든 이름의 폴더에 들어갑니다. 이름은 작업 경로의 ASCII 영문자·숫자·`-` 는 그대로 두고 나머지 글자는 모두 `-` 로 바꿔 만듭니다(Claude Code 2.1.233 기준)[8]. macOS 경로는 `/` 로 시작해서 폴더 이름이 `-` 로 시작합니다. 만든 예시로 작업 경로가 `/Users/examiner01/work/app` 이면 폴더 이름은 `-Users-examiner01-work-app` 이 되고, 세션 파일은 `/Users/examiner01/.claude/projects/-Users-examiner01-work-app/` 아래에 생깁니다.

이 바꾸기는 되돌릴 수 없습니다. claude-forensics 는 앞의 `-` 를 `/` 로 돌리고 나머지 `-` 도 `/` 로 바꿔 경로를 되짚는데, 원래 경로에 `-` 가 있으면 틀어지므로 기록 줄의 `cwd` 값을 먼저 씁니다[7]. 보고서에는 폴더 이름이 아니라 `cwd` 값을 적습니다.

### 로그인 정보

로그인 정보는 암호화된 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html)에 들어갑니다[4]. SSH 세션처럼 키체인이 잠겨 쓰기를 거부하면 `~/.claude/.credentials.json` 에 파일 모드 0600 으로 대신 저장하고[4], 이 파일은 [Windows](windows.md)의 같은 이름 파일처럼 평문 JSON 입니다. 원격 접속으로만 쓰던 Mac 에서 이 파일이 나온다면 키체인 쓰기 실패와 관련이 있을 수 있지만, 파일 하나로 접속 방식을 단정하지는 않습니다.

키체인 항목의 서비스 이름은 공개된 분석 자료에 없어서, 검체의 키체인 항목 목록에서 Claude Code 항목을 찾아 이름과 생성·수정 시각을 기록합니다. 항목 값은 보고서에서 가리고, 토큰이 남는 다른 곳은 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에 모아 두었습니다. 계정 쪽 기록이 필요하면 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)으로 받습니다.

### 관리 정책

관리 정책은 `/Library/Application Support/ClaudeCode/` 아래 파일이나 MDM 구성 프로파일로 내려옵니다[3]. 구성 프로파일은 관리 환경설정 도메인 `com.anthropic.claudecode` 를 쓰고, 그 안의 최상위 키는 `managed-settings.json` 과 같습니다[3]. 관리 환경설정을 읽는 법은 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/plist/index.html) 페이지를 참고합니다. 여러 소스 사이의 순서는 [설정·권한·훅](settings-permissions.md)에서 다룹니다.

### 데스크톱 앱에서 돌린 Code 세션

Claude 데스크톱 앱에서 돌린 Code 세션은 본문이 `~/.claude/projects/` 에, 메타데이터가 `~/Library/Application Support/Claude/claude-code-sessions/` 아래 조직 ID 폴더와 계정 ID 폴더를 거친 `local_세션ID.json` 에 따로 남습니다[7]. 메타데이터의 `cliSessionId` 값으로 `~/.claude/projects/` 의 기록 파일을 찾아 이어야 제목·모델·보관 여부·계정과 대화 본문이 한 세션으로 묶입니다[7]. 같은 폴더의 `local-agent-mode-sessions/` 에는 Cowork 세션이 남습니다[7][8]. 두 폴더의 짜임과 키는 [Claude macOS 앱](../../chat-services/claude/macos.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 버전 파일과 실행 링크가 있으면 그 사용자 계정에 Claude Code 를 설치한 흔적이 있다고 쓸 수 있습니다. `versions/` 목록은 디스크에 남은 버전만 보여 주고, 거쳐 온 버전 전부라고 보지는 않습니다. 관리 정책 파일이나 구성 프로파일이 있으면 그 Mac 에 정책이 놓여 있었다고 쓸 수 있습니다. `claude-code-sessions/` 에 메타데이터가 있으면 그 계정 폴더 이름의 계정으로 데스크톱 앱에서 Code 세션을 연 기록이 있다고 쓸 수 있습니다[7].

**증명하지 못하는 것.** 키체인 항목과 데이터 폴더는 그 계정으로 누가 작업했는지 알려 주지 않습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 클라우드에서 돈 세션은 이 Mac 에 기록이 없을 수 있고, 로컬 기록은 기본 30일 뒤 지워집니다([세션 기록 구조](transcripts.md)). 메타데이터만 있고 `cliSessionId` 에 맞는 기록 파일이 없으면 세션이 있었다는 것까지만 쓰고, 대화 내용은 쓰지 않습니다.

## 시각 해석

기록 안의 시각은 [세션 기록 구조](transcripts.md)를 따릅니다. 폴더가 언제 생기고 바뀌었는지는 [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/filesystem/fsevents/index.html)에서 `~/.claude/`, `~/.local/share/claude/versions/`, `~/Library/Application Support/Claude/` 경로를 찾아 맞춰 봅니다. `versions/` 에 새 파일이 생긴 시각은 업데이트 시각을 가늠하는 데 쓸 수 있지만, 스스로 업데이트하는 설치에서는 사용자가 그 시각에 앱을 켰다는 뜻까지는 아닙니다.

`~/.claude/.last-cleanup` 은 마지막 자동 삭제 시각이라서, 남은 기록의 날짜 범위와 함께 봅니다[7]. 이 파일이 없거나 오래됐는데 남은 기록의 날짜 범위가 넓으면, 그 Mac 에 보통보다 오래된 기록이 남아 있다는 신호입니다[7].

## 함정과 한계

- **`CLAUDE_CONFIG_DIR` 로 옮긴 데이터 폴더.** `~/.claude/` 에 없고 키체인 항목도 따로 있습니다[4].
- **없다는 사실.** Homebrew 설치는 `brew cleanup` 을 돌리면 옛 버전이 사라지고, `/logout` 은 로그인 정보를 지웁니다[4]. 옛 버전이나 로그인 정보가 없다는 사실만으로 쓰지 않았다고 보지 않습니다.
- **두 폴더를 모두 떠야 합니다.** `~/.claude/` 만 뜨면 데스크톱 앱 세션의 제목·계정이 빠지고, `~/Library/Application Support/Claude/` 만 뜨면 데스크톱 앱에서 돌린 Code 세션의 대화 본문이 빠집니다[7].
- **`-W` 는 실행하는 사람의 홈을 읽습니다.** claude-forensics 의 `-W` 는 macOS 에서 `$HOME/Library/Application Support/Claude` 를 자동으로 쓰고, 다른 OS 에서는 거부합니다[7]. 압수한 Mac 의 사본을 볼 때 `-W` 를 쓰면 분석가 자신의 폴더를 읽게 되므로 `-w 사본경로` 로 직접 줍니다.

## 직접 분석해 보기

**헥스로 한 번.** 파일로 남은 `.credentials.json` 은 평문 JSON 이라서 [Windows](windows.md) 페이지의 헥스 예시와 같은 방법으로 읽습니다. 첫 바이트가 `7B`(`{`)이면 암호화하지 않은 파일입니다.

**공개 도구로 한 번.** 살아 있는 Mac 에서는 기본 명령으로 서명과 설치 버전을 읽기만 합니다. 아래 사용자 이름과 폴더는 만든 예시입니다.

```sh
# 만든 예시: 사용자 examiner01
codesign --verify --verbose /Users/examiner01/.local/bin/claude
readlink /Users/examiner01/.local/bin/claude
ls -la /Users/examiner01/.local/share/claude/versions/
ls -la "/Library/Application Support/ClaudeCode/"
ls -la /Users/examiner01/.claude/projects/
```

뜬 사본은 claude-forensics 로 한 번에 정리합니다[7]. 이 도구는 `.claude` 트리를 `cp -Rp` 로 시각과 권한을 살려 복사하고 쓰기 권한을 없앤 뒤 그 사본만 읽으며, 데스크톱 앱 폴더에서는 `claude-code-sessions/`, `local-agent-mode-sessions/` 폴더와 `cowork-enabled-cli-ops.json`, `claude_desktop_config.json`, `config.json`, `buddy-tokens.json`, `ant-did` 파일만 복사합니다[7]. 사본과 결과 파일 전부의 SHA-256 을 `MANIFEST.sha256` 에 남깁니다[7].

```sh
# 만든 예시: 압수한 Mac 에서 뜬 사본
./claude-forensics.sh -w /cases/c01/copy/Claude /cases/c01/copy/.claude /cases/c01/out
```

## 교차 검증

폴더 시각은 [FSEvents](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/filesystem/fsevents/index.html)와, 기록 시각은 [macOS 타임라인](https://urock-ailab.github.io/forensics-handbook-mac/03-techniques/analysis/timeline/index.html)과 맞춰 봅니다. 데스크톱 앱 세션은 [Claude macOS 앱](../../chat-services/claude/macos.md)의 메타데이터와 이어 봅니다. 모델 호출이 나간 시간대는 [네트워크 기록](../../network-enterprise/network-traces.md)으로, 에이전트가 실행한 명령과 바꾼 파일은 [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)로 이어 봅니다.

## 실습

Claude Code 흔적이 든 공개 검체가 없으면 시험용 Mac 이나 가상 머신에 직접 깔아 만든 검체로 풀어 봅니다.

1. 네이티브 설치로 두 번 업데이트한 뒤 `versions/` 에는 무엇이 남고, 실행 링크는 어디를 가리킵니까?
2. SSH 로 접속해 로그인했을 때와 화면 앞에서 로그인했을 때 `.credentials.json` 이 생기는지 비교해 봅니다.
3. `CLAUDE_CONFIG_DIR` 을 지정해 로그인하면 키체인 항목은 몇 개가 됩니까?
4. 이름에 `-` 와 공백이 든 폴더에서 세션을 열고, `projects/` 아래 폴더 이름과 기록 줄의 `cwd` 값을 비교해 봅니다.
5. 데스크톱 앱에서 Code 세션을 하나 열고, `claude-code-sessions/` 의 `cliSessionId` 와 `~/.claude/projects/` 의 파일 이름이 맞는지 봅니다.
6. FSEvents 에서 `~/.claude/projects/` 아래 파일이 처음 생긴 시각과 기록 첫 줄의 시각은 얼마나 차이 납니까?

## 참고 문헌

1. Settings files and precedence — https://code.claude.com/docs/en/settings
2. .claude 폴더 파일·폴더 참조(claude-directory) — https://code.claude.com/docs/en/claude-directory
3. Deploy managed settings — https://code.claude.com/docs/en/managed-settings
4. Authentication — https://code.claude.com/docs/en/authentication
5. Configure permissions — https://code.claude.com/docs/en/permissions
6. Advanced setup — https://code.claude.com/docs/en/setup
7. forensicdave, claude-forensics v0.1.1 — https://github.com/forensicdave/claude-forensics (`README.md`, `claude-forensics.sh`, `claude_forensics.py` 의 `decode_project_dir`·`process_cowork`·`process_agent_sessions`)
8. kenn-io, agentsview — https://github.com/kenn-io/agentsview (`internal/parser/cowork_paths.go`, `docs/internal/session-format-sources.md`)
