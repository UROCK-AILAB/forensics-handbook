---
title: "AI 서비스의 데이터는 어디에 있나"
parent: "기반 · 저장 구조"
nav_order: 0
---

# AI 서비스의 데이터는 어디에 있나 (서버·기기·동기화)

> 확인 날짜: 2026-09. 공식 문서는 2026-09-25 에 열어 읽었습니다. 기기 관찰은 Windows 11(빌드 26200) 한 대에서 AI 도구 폴더를 읽기 전용으로 열어 폴더·파일 이름과 키 이름만 본 결과이고, 값과 앱 버전은 적어 두지 않았습니다. 관찰로 확인한 내용에는 "(확인 범위: Windows 11, 2026-09)" 를 붙였습니다. macOS·Linux·Android·iOS 는 기기에서 관찰하지 않았고 공식 문서에 나온 내용만 씁니다.

## 한 줄 요약

AI 서비스의 대화 원본은 웹·앱 채팅 서비스라면 서버 계정에 있고 코딩 도구라면 사용자 기기에 있는 경우가 있어서, 조사는 원본이 어느 쪽에 있는지부터 가리고 반대쪽에서는 캐시·설정·로그인 정보 같은 흔적을 찾는 순서로 진행합니다.

## 이 형식을 쓰는 아티팩트

AI 서비스를 쓰는 방식은 크게 세 가지이고, 방식마다 대화 원본이 있는 곳과 기기에 남는 것이 다릅니다.

| 쓰는 방식 | 예 | 대화 원본 | 기기에 남는 것 |
|---|---|---|---|
| 웹 브라우저·데스크톱 앱·모바일 앱으로 쓰는 채팅 서비스 | [ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md), [Claude](../../02-artifacts/chat-services/claude/index.md), [Gemini](../../02-artifacts/chat-services/gemini/index.md) | 서버 계정 | 브라우저·앱 캐시, 쿠키, 앱 설정 파일 |
| 터미널·편집기에서 도는 개발 도구 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md), [Cursor](../../02-artifacts/dev-agents/cursor.md) | 도구마다 다름. Claude Code 는 기기에 대화 전문을 남김 | 설정, 훅, 로그인 정보, 도구에 따라 대화 기록 |
| 기기에서 모델을 돌리는 로컬 AI | [Ollama](../../02-artifacts/local-ai/ollama.md) | 대화 기록 파일이 있는지 확인 못 함 | [모델 파일](../../02-artifacts/local-ai/model-files.md), 키 파일 |

대화 원본이 서버에만 있는 경우도 분명히 있습니다. 웹 브라우저로만 쓴 채팅 서비스는 원본이 서버 계정에 있고 기기에는 브라우저가 남긴 방문 기록·캐시·쿠키만 남으며, 캐시에 대화 내용이 어느 만큼 남는지는 이 쪽을 쓰면서 확인하지 못했습니다. 웹에서 실행하는 Claude Code(클라우드 세션)는 Anthropic 가상 머신에서 돌아서 사용자 PC 에 세션 기록이 없을 수 있다고 공식 문서가 적고 있습니다 [4].

## 구조

### 서버 쪽 — 계정에 남는 대화

Claude 개인용(Free·Pro·Max)은 대화를 지웠을 때의 처리와 보관 기간을 서버 저장소 기준으로 설명하고 [1], Gemini 앱은 "Keep Activity" 가 켜져 있을 때 대화를 계정의 "Gemini Apps Activity" 에 저장합니다 [2]. 기록 설정을 끈 상태에서도 서버에 잠시 남는 대화가 있고, 서비스별 보관 기간과 삭제 뒤 처리는 [대화 기록 보관 설정과 삭제](retention-deletion.md) 에 모았습니다. ChatGPT 는 이 쪽을 쓰면서 도움말 문서를 열지 못해 서버 저장 방식과 보관 기간을 확인하지 못했습니다.

서버에 있는 원본은 사용자가 스스로 내려받는 [계정 데이터 내보내기](data-export-formats.md) 로 얻거나, 서비스 회사에 [데이터를 요청](../../03-techniques/acquisition/legal-requests.md) 해서 얻습니다. 기기만 확보한 조사라면 서버 원본은 손에 없다는 점을 처음부터 보고서에 적어 둡니다.

### 기기 쪽 — 기기에 원본을 두는 도구

Claude Code 는 모든 OS 에서 `~/.claude/` 를 사용자 데이터 폴더로 쓰고(Windows 는 `%USERPROFILE%\.claude`), `CLAUDE_CONFIG_DIR` 환경 변수로 이 폴더를 옮길 수 있습니다 [5]. 세션 기록(대화 전문)은 `~/.claude/projects/<프로젝트>/<세션>.jsonl` 에 평문으로 남고 [4][5], VS Code 확장·JetBrains 플러그인·데스크톱 앱도 같은 `~/.claude/` 에 씁니다 [6]. 이 PC 의 `%USERPROFILE%\.claude` 에서는 `.credentials.json`, `settings.json`, `stats-cache.json`, `history.jsonl`, `file-history/`, `paste-cache/`, `projects/`, `jobs/`, `feedback/drafts/` 를 보았습니다(확인 범위: Windows 11, 2026-09). 기록 구조는 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) 쪽에서, 보관 기간은 [대화 기록 보관 설정과 삭제](retention-deletion.md) 에서, 로그인 정보는 [API 키와 토큰이 남는 곳](api-keys-tokens.md) 에서 다룹니다.

다른 개발 도구는 이 PC 에서 설정 파일만 보였고 대화 기록 파일은 보이지 않았습니다(확인 범위: Windows 11, 2026-09). 대화 기록 파일이 없었다는 말은 이 PC 에 없었다는 뜻이고, 도구가 기록을 남기지 않는다는 뜻은 아닙니다. Codex CLI 가 세션 기록을 어디에 두는지는 이번에 연 문서에 없어서 확인하지 못했습니다.

| 도구 | 이 PC 의 위치 | 이 PC 에서 본 것 |
|---|---|---|
| Codex CLI | `%USERPROFILE%\.codex` | `hooks.json`, `skills/` 아래 `SKILL.md` 와 JSON 파일 |
| Gemini CLI | `%USERPROFILE%\.gemini` | `settings.json`, `config/`(`config.json`, `hooks.json`, `mcp_config.json`, `projects/`), `antigravity/`(`antigravity_state.pbtxt`, `installation_id`, `crashes/` 아래 로그) |
| Cursor | `%USERPROFILE%\.cursor` | `hooks.json` 한 개. Cursor 앱 데이터 폴더는 없었음 |
| Ollama | `%USERPROFILE%\.ollama` | `cache/` 아래 JSON 한 개, `id_ed25519`, `id_ed25519.pub`. `models` 폴더는 없었음 |

Ollama 는 로컬 모델을 돌릴 때 프롬프트나 데이터를 보지 않는다고 적고 있고, 클라우드 모델을 쓸 때는 요청을 처리하되 저장·기록·학습에 쓰지 않는다고 적고 있습니다 [3]. 모델 파일은 OS 마다 기본 위치가 정해져 있고 `OLLAMA_MODELS` 환경 변수로 바꿉니다 [3]. 이 PC 에 `models` 폴더가 없었던 까닭이 모델을 받지 않아서인지, 모델 폴더를 다른 곳으로 옮겨서인지는 폴더만 보고 알 수 없습니다. Ollama 의 로그 경로와 대화 입력 기록 파일이 있는지는 확인하지 못했습니다.

### OS 별 위치

공식 문서로 확인한 위치와 관찰한 위치를 OS 별로 모으면 아래와 같습니다. 칸이 "확인 못 함" 인 곳은 문서도 관찰도 없는 곳입니다.

| 대상 | Windows | macOS | Linux | 근거 |
|---|---|---|---|---|
| Claude Code 데이터 폴더 | `%USERPROFILE%\.claude` | `~/.claude` | `~/.claude` | [5] |
| Claude Code 세션 기록 | `%USERPROFILE%\.claude\projects\` | `~/.claude/projects/` | `~/.claude/projects/` | [4][5] |
| Ollama 모델 | `C:\Users\%username%\.ollama\models` | `~/.ollama/models` | `/usr/share/ollama/.ollama/models` | [3] |
| Claude 데스크톱(스토어 앱) | 앱 패키지 폴더 아래 `LocalCache\Roaming\Claude\` (확인 범위: Windows 11, 2026-09) | 확인 못 함 | 해당 없음 | 관찰 |

Electron 으로 만든 데스크톱 앱의 기본 데이터 폴더는 OS 마다 정해져 있고 [Electron·웹뷰 앱의 저장 구조](electron-webview.md) 에서 다룹니다. Android·iOS 앱의 기기 쪽 저장 위치는 이 쪽을 쓰면서 확인하지 못했고, 앱 폴더와 보호 방식의 공통 원리는 [앱 데이터 폴더 구조 (Android)](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html) 와 [데이터 보호 (iOS)](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html) 를 봅니다.

### Windows 스토어(MSIX) 앱의 위치

Claude 데스크톱을 스토어 앱으로 설치한 PC 에서는 앱 데이터가 앱 패키지 폴더 아래 `LocalCache\Roaming\Claude\` 에 있었습니다(확인 범위: Windows 11, 2026-09). 같은 패키지 폴더의 `LocalCache\Local\` 아래에는 `claude-cli-nodejs\Cache\` 아래 JSONL 파일(키: `cwd`, `debug`, `sessionId`, `timestamp`)과 함께 npm·pip·NuGet 캐시, `GitHub CLI\device-id` 같은 개발 도구 폴더가 있었습니다(확인 범위: Windows 11, 2026-09). 앱 안에서 실행한 도구들이 쓴 파일이 패키지 폴더로 모인 것으로 보이지만, 패키지 앱의 파일 쓰기 방향을 바꾸는 규칙 자체는 확인하지 못했습니다. 그래서 스토어 앱을 쓴 PC 에서는 `%APPDATA%`·`%LOCALAPPDATA%` 만 보지 말고 패키지 폴더 아래 `LocalCache` 도 함께 봅니다.

### 동기화 — 여러 기기에 같은 대화가 보이는 까닭

같은 계정의 대화가 웹·데스크톱·모바일에 똑같이 보이는 것은 대화가 서버 계정에 있고 각 기기가 그 기록을 불러와 보여 주기 때문이라는 일반 설명이 통하지만, 서비스별 동기화 방식은 이 쪽을 쓰면서 공식 문서로 확인하지 못했습니다. 공식 문서로 확인한 예는 Claude Code 의 Remote Control 세션으로, 실행은 사용자 기기에서 하고 연결된 동안에는 대화 기록 사본을 서버에도 저장합니다 [4].

Claude 데스크톱 데이터 폴더의 `bridge-state.json` 에는 `enabled`, `environmentId`, `localSessionId`, `remoteSessionId`, `processedMessageUuids`, `pendingProcessedAcks`, `userConsented` 키가 있었습니다(확인 범위: Windows 11, 2026-09). 키 이름으로 보아 기기의 세션과 서버의 세션을 잇는 기록으로 보이지만 용도를 설명한 공식 문서는 찾지 못했습니다.

## 읽는 법

1. 기기에서 어떤 방식으로 AI 서비스를 썼는지 먼저 확인합니다. 설치된 앱, 브라우저 방문 기록, 사용자 폴더 아래 `.claude`·`.codex`·`.gemini`·`.cursor`·`.ollama` 같은 도구 폴더, 스토어 앱 패키지 폴더를 봅니다. 모으는 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) 를 따릅니다.
2. 원본이 서버에 있는 서비스라면 계정 내보내기 파일이나 서비스 회사 회신이 있는지 확인하고, 없다면 기기에서 찾은 것은 흔적일 뿐 원본이 아니라고 적어 둡니다.
3. 원본이 기기에 있는 도구라면 폴더째 복사한 사본에서 분석합니다. 앱이 쓰고 있는 데이터베이스는 잠겨서 열리지 않을 수 있습니다(자세한 내용은 [Electron·웹뷰 앱의 저장 구조](electron-webview.md)).
4. 서버 쪽 기록과 기기 쪽 흔적의 시각을 한 표에 놓고 맞춰 봅니다. 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다.

## 포렌식에서 중요한 점

서버에서 지운 대화와 기기에서 지운 파일은 따로 봐야 합니다. 서버 쪽은 서비스 회사의 보관 정책에 따라 사라지는 시점이 정해지고, 기기 쪽은 도구의 자동 정리 설정과 사용자의 삭제에 따라 사라집니다. 서버에서 대화를 지운 뒤에도 기기 캐시에 내용이 남는지는 이 쪽을 쓰면서 확인하지 못했고, 캐시에서 내용을 되살리는 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md) 에서 다룹니다.

로컬에 원본을 두는 도구는 자동 정리로 세션 기록이 사라져도 입력 이력이나 사용량 통계 같은 다른 파일이 남을 수 있고, 무엇이 지워지고 무엇이 남는지는 [대화 기록 보관 설정과 삭제](retention-deletion.md) 에 정리했습니다.

## 함정

**폴더가 없거나 비어 있다고 쓰지 않았다고 볼 수 없습니다.** Claude Code 는 `CLAUDE_CONFIG_DIR` 로 [5], Ollama 는 `OLLAMA_MODELS` 로 [3] 저장 위치를 옮길 수 있고, 웹에서 돈 클라우드 세션은 사용자 PC 에 기록을 남기지 않을 수 있습니다 [4]. 기본 위치에 없다면 환경 변수와 다른 위치를 먼저 확인합니다.

**스토어 앱의 패키지 폴더 위치를 한 가지로 단정하지 않습니다.** 보통의 패키지 폴더는 `%LOCALAPPDATA%\Packages` 아래에 있는데, 이 PC 의 관찰 기록에는 `%USERPROFILE%\Packages` 아래로 적혀 있었고 이 차이는 확인하지 못했습니다. 보고서에는 "앱 패키지 폴더 아래 `LocalCache\Roaming\Claude`" 처럼 확인한 만큼만 씁니다.

**계정에 대화가 보인다고 그 기기에서 대화했다고 쓸 수 없습니다.** 동기화된 서비스는 어느 기기에서든 같은 대화 목록을 보여 주고, 입력한 기기와 사람을 가리는 일은 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md) 의 방법을 따릅니다.

**앱 버전에 따라 폴더 구성이 바뀝니다.** 이 쪽의 관찰은 2026-09 한 시점의 모습이고 앱 버전은 적어 두지 않았습니다. 검체를 볼 때는 그 검체의 앱 버전을 따로 확인해 함께 적습니다.

## 도구

폴더 구성은 파일 탐색기나 `dir /s`, `ls -laR` 같은 기본 명령으로 먼저 목록을 뜨고, 목록을 사본과 함께 보관합니다. JSON·JSONL 파일은 `jq` 같은 공개 도구로 읽을 수 있고, SQLite 파일은 DB Browser for SQLite 같은 공개 도구로 엽니다. 크롬 계열 저장소(LevelDB·IndexedDB·쿠키 DB)를 읽는 법은 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html) 와 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html) 를 봅니다.

## 참고 문헌

1. Claude Privacy Center — How long do you store my data? — https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data
2. Gemini Apps Help — Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961?hl=en
3. Ollama — FAQ — https://docs.ollama.com/faq
4. Claude Code Docs — Data usage — https://code.claude.com/docs/en/data-usage
5. Claude Code Docs — .claude 폴더 참조 (claude-directory) — https://code.claude.com/docs/en/claude-directory
6. Claude Code Docs — Advanced setup — https://code.claude.com/docs/en/setup
