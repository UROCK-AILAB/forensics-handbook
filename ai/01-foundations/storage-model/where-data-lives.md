---
title: "AI 서비스의 데이터는 어디에 있나"
parent: "기반 · 저장 구조"
nav_order: 0
---

# AI 서비스의 데이터는 어디에 있나 (서버·기기·동기화)

> 확인 날짜: 2026-09-25. 공식 문서, 공개 분석 도구의 코드(agentsview, ALEAPP, iLEAPP), 논문을 바탕으로 썼습니다. 기기 관찰은 Windows 11 에서 AI 도구 폴더를 읽기 전용으로 열어 폴더·파일 이름과 키 이름만 본 결과이고, 이런 내용에는 "(확인 범위: Windows 11, 2026-09)" 를 붙였습니다. macOS·Linux·Android·iOS 는 문서·도구 코드·논문에 나온 내용만 씁니다.

## 한 줄 요약

AI 서비스의 대화 원본은 채팅 서비스라면 서버 계정에 있지만 모바일 앱과 데스크톱 앱은 기기에 사본을 두고, 코딩 도구와 로컬 AI 앱은 원본을 기기에 두기도 하므로, 조사는 서비스마다 원본과 사본이 어디에 있는지부터 가리는 순서로 진행합니다.

## 이 형식을 쓰는 아티팩트

AI 서비스를 쓰는 방식은 크게 네 가지이고, 방식마다 대화 원본이 있는 곳과 기기에 남는 것이 다릅니다.

| 쓰는 방식 | 예 | 대화 원본 | 기기에 남는 것 |
|---|---|---|---|
| 웹 브라우저로 쓰는 채팅 서비스 | [ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md), [Claude](../../02-artifacts/chat-services/claude/index.md), [Gemini](../../02-artifacts/chat-services/gemini/index.md) | 서버 계정 | 방문 기록, 캐시, 쿠키 같은 브라우저 저장소 |
| 모바일 앱 | 위와 같은 서비스, [Microsoft Copilot](../../02-artifacts/chat-services/copilot/index.md) | 서버 계정 | ChatGPT·Claude 는 앱 폴더의 SQLite·JSON 에 대화 사본 [8][9]. ChatGPT·Copilot 은 대화를 평문으로 저장하고 Gemini 는 대화를 클라우드에 둠 [10] |
| 터미널·편집기·데스크톱 앱에서 도는 개발 도구 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md), [Cursor](../../02-artifacts/dev-agents/cursor.md) | 기기의 세션 파일(클라우드 세션은 예외) | 세션 기록, 설정, 훅, 로그인 정보 [4][5][7] |
| 기기에서 모델을 돌리는 로컬 AI | [Ollama](../../02-artifacts/local-ai/ollama.md), [LM Studio](../../02-artifacts/local-ai/lm-studio.md), [Msty](../../02-artifacts/local-ai/msty.md) | 대화 화면 앱이 기기에 둠 | [모델 파일](../../02-artifacts/local-ai/model-files.md), 서버 로그, 명령 입력 이력, 앱의 대화 파일 [11] |

앞선 연구들도 AI 앱의 증거가 기기 저장소와 클라우드에 나뉘어 있다고 정리합니다. Panta 외(2026)는 ChatGPT 같은 AI 앱을 다룬 연구들(Dragonas 외 2024, Tyagi 외 2025, Kankanamge 외 2025)이 증거가 로컬 저장소와 클라우드 서비스에 흩어져 있음을 보였다고 요약했고, AI 시스템 전반의 포렌식 절차를 다룬 연구로 Cho 외(2025, Forensic Science International: Digital Investigation 52)를 꼽았습니다 [12].

## 구조

### 서버 쪽 — 계정에 남는 대화

Claude 개인용(Free·Pro·Max)은 대화를 지웠을 때의 처리와 보관 기간을 서버 저장소 기준으로 설명하고 [1], Gemini 앱은 "Keep Activity" 가 켜져 있을 때 대화를 계정의 "Gemini Apps Activity" 에 저장합니다 [2]. 기록 설정을 끈 상태에서도 서버에 잠시 남는 대화가 있습니다. 서비스별 보관 기간과 삭제 뒤 처리는 [대화 기록 보관 설정과 삭제](retention-deletion.md) 에, ChatGPT 의 서버 쪽 기록은 [ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md) 쪽에 모았습니다.

서버에 있는 원본은 사용자가 스스로 내려받는 [계정 데이터 내보내기](data-export-formats.md) 로 얻거나, 서비스 회사에 [데이터를 요청](../../03-techniques/acquisition/legal-requests.md) 해서 얻습니다. 기기만 확보한 조사라면 서버 원본은 손에 없다는 점을 처음부터 보고서에 적어 둡니다.

서버 쪽 자료가 기기에서 지운 뒤에도 남는 예가 있습니다. Ray-Ban Meta 안경과 Meta AI 앱을 실험한 Panta 외(2026)는 삭제, 페어링 해제, 공장 초기화 뒤에도 일부 식별자와 흔적이 남았고, 클라우드 내보내기에는 기기 쪽을 보완하는 대화 증거가 남아 있었다고 적었습니다 [12]. 자세한 내용은 [Meta AI 앱과 AI 안경](../../02-artifacts/chat-services/meta-ai-glasses.md) 에서 다룹니다.

### 모바일 앱 — 기기에 남는 대화 사본

원본이 서버에 있는 서비스라도 모바일 앱은 대화 사본을 앱 폴더에 두는 경우가 많습니다. Tyagi·Gong·Karabiyik(2025)은 Android·iOS 의 ChatGPT·Copilot·Gemini 앱을 비교해, ChatGPT 와 Copilot 은 대화를 브라우저 데이터와 함께 기기에 평문으로 저장하고 Gemini 는 대화·브라우저 데이터·이미지를 클라우드에 두어 Google Takeout 으로 받을 수 있다고 초록에 적었습니다 [10]. 공개 분석기도 ChatGPT·Claude 앱의 SQLite 와 JSON 을 복호화 단계 없이 바로 엽니다 [8][9].

| 앱 | OS | 대화가 남는 파일(앱 폴더 기준) | 형식 | 분석기가 시험한 범위 | 근거 |
|---|---|---|---|---|---|
| ChatGPT | Android | `com.openai.chatgpt/databases/` 아래 `*_conversations.db` | SQLite | 앱 1.2024.177 까지, Android 15 시험 이미지(vc 2525902) | [8] |
| ChatGPT | iOS | `Library/Application Support/conversations-*/` 아래 `*.json` | 대화마다 JSON 파일 하나 | 앱 1.2024.178 까지, 시험 이미지 1.2024.219·1.2024.233(iOS 17) | [9] |
| Claude | Android | `com.anthropic.claude/databases/` 아래 `acc_*_claude_cache.db` | SQLite, 칸 안에 JSON | Android 13·17 시험 이미지, 앱 버전 기록 없음 | [8] |
| Claude | iOS | `Library/Application Support/ClaudeCache/` 아래 `cache_*.sqlite` | SQLite | iOS 18.7.8·26.5.2 시험 이미지 | [9] |
| Gemini | Android·iOS | 기기 쪽 공개 분석기 없음 | 대화는 클라우드, Takeout 으로 받음 | ALEAPP·iLEAPP 에 전용 분석기 없음(2026-09-25) | [10] |
| Copilot | Android·iOS | 기기 쪽 공개 분석기 없음 | 평문 대화와 브라우저 데이터 | ALEAPP·iLEAPP 에 전용 분석기 없음(2026-09-25) | [10] |

Android 의 경로는 앱 데이터 폴더(`/data/data/` 아래 패키지 이름 폴더) 기준이고, iOS 의 경로는 `Containers/Data/Application/` 아래 UUID 이름의 앱 폴더 기준입니다. 앱 폴더의 공통 구조와 보호 방식은 [앱 데이터 폴더 구조 (Android)](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html) 와 [데이터 보호 (iOS)](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html) 를 봅니다.

분석기가 시험한 판은 2024~2026 년의 몇 판뿐이라서 지금 판의 파일 구성과 다를 수 있습니다. 검체에서는 앱 판을 먼저 적고, 표의 파일이 그 자리에 있는지 확인합니다. Claude 앱의 파일은 이름대로 캐시라서 계정의 대화 전체가 들어 있다고 단정하지 않고 계정 내보내기와 견줘 봅니다. Copilot 은 기기에 대화가 남는지를 두고 출처끼리 다르게 적었으므로 [Copilot](../../02-artifacts/chat-services/copilot/index.md) 쪽의 대조를 봅니다. 표·칸·시각 형식은 [ChatGPT Android](../../02-artifacts/chat-services/chatgpt/android.md), [ChatGPT iOS](../../02-artifacts/chat-services/chatgpt/ios.md), [Claude Android](../../02-artifacts/chat-services/claude/android.md), [Claude iOS](../../02-artifacts/chat-services/claude/ios.md) 쪽에서 다룹니다.

### 개발 도구 — 기기에 원본을 두는 도구

Claude Code 는 모든 OS 에서 `~/.claude/` 를 사용자 데이터 폴더로 쓰고(Windows 는 `%USERPROFILE%\.claude`), `CLAUDE_CONFIG_DIR` 환경 변수로 이 폴더를 옮길 수 있습니다 [5]. 세션 기록(대화 전문)은 `~/.claude/projects/` 아래 프로젝트 폴더에 세션마다 `.jsonl` 파일로 평문으로 남고 [4][5], VS Code 확장·JetBrains 플러그인·데스크톱 앱도 같은 `~/.claude/` 에 씁니다 [6]. 웹에서 실행하는 Claude Code(클라우드 세션)는 Anthropic 가상 머신에서 돌아서 사용자 PC 에 세션 기록이 없을 수 있습니다 [4]. Windows 11 의 `%USERPROFILE%\.claude` 에서는 `.credentials.json`, `settings.json`, `stats-cache.json`, `history.jsonl`, `file-history/`, `paste-cache/`, `projects/`, `jobs/`, `feedback/drafts/` 가 보였습니다(확인 범위: Windows 11, 2026-09).

다른 개발 도구도 세션 기록을 사용자 폴더 아래에 둡니다. 공개 분석 도구 agentsview(README 2026-09-11, v0.44.0)가 세션을 찾는 기본 위치는 아래와 같습니다 [7]. 같은 표의 오른쪽 칸은 Windows 11 에서 폴더를 열어 본 모습이고, 세션 파일이 없는 PC 도 있으므로 폴더가 있다는 것만으로 대화를 했다고 쓰지 않습니다.

| 도구 | 세션 기록 기본 위치 [7] | Windows 11 에서 본 것(확인 범위: Windows 11, 2026-09) | 자세한 쪽 |
|---|---|---|---|
| Codex CLI | `~/.codex/sessions/`, 보관된 세션은 `~/.codex/archived_sessions/` | `%USERPROFILE%\.codex` 에 `hooks.json`, `skills/` 아래 `SKILL.md` 와 JSON 파일 | [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md) |
| Gemini CLI | `~/.gemini/tmp/` 아래 프로젝트 폴더의 `chats/session-*.json`·`.jsonl` | `%USERPROFILE%\.gemini` 에 `settings.json`, `config/`(`config.json`, `hooks.json`, `mcp_config.json`, `projects/`), `antigravity/`(`antigravity_state.pbtxt`, `installation_id`, `crashes/`) | [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md) |
| Cursor | `~/.cursor/projects/` | `%USERPROFILE%\.cursor` 에 `hooks.json` 한 개 | [Cursor](../../02-artifacts/dev-agents/cursor.md) |

기록 구조는 도구별 쪽에서, 보관 기간은 [대화 기록 보관 설정과 삭제](retention-deletion.md) 에서, 로그인 정보는 [API 키와 토큰이 남는 곳](api-keys-tokens.md) 에서 다룹니다.

### 로컬 AI — 대화를 쥐는 쪽은 화면 앱

로컬 AI 는 모델을 돌리는 백엔드와 대화 화면을 보여 주는 앱으로 나뉩니다. LangurTrace 논문(Jeong·Lee·Park, 2025)은 모델과 백엔드는 대화나 문맥을 스스로 관리하지 않고, 화면 앱이 대화를 쥐고 있다가 매번 백엔드로 다시 보낸다고 설명합니다 [11]. 그래서 Ollama 같은 백엔드에서는 대화 본문보다 API 호출이 적힌 서버 로그와 모델 파일이 중요하고, 대화 본문은 LM Studio(`%UserProfile%/.lmstudio/conversations/`)나 Msty(`%AppData%/Msty/msty.db`) 같은 화면 앱 쪽에서 찾습니다 [11].

LangurTrace 가 Ollama 0.6.5 로 실험해 적은 Windows 위치는 서버 로그 `%LocalAppData%/Ollama/server.log`, 앱 로그 `app.log`, 업그레이드 로그 `upgrade.log`, 명령 입력 이력 `%UserProfile%/.ollama/history`, 모델 매니페스트와 레이어 `%UserProfile%/.ollama/models/` 입니다 [11]. 명령 입력 이력에는 명령줄로 보낸 요청이 시각 순서대로 남지만 모델의 답은 남지 않습니다 [11]. Ollama 는 로컬 모델을 돌릴 때 프롬프트나 데이터를 보지 않고, 클라우드 모델을 쓸 때는 요청을 처리하되 저장·기록·학습에 쓰지 않는다고 적고 있습니다 [3]. 모델 파일 위치는 `OLLAMA_MODELS` 환경 변수로 바꿀 수 있습니다 [3]. Windows 11 의 `%USERPROFILE%\.ollama` 에서는 `cache/` 아래 JSON 한 개, `id_ed25519`, `id_ed25519.pub` 가 보였고 `models` 폴더는 없었습니다(확인 범위: Windows 11, 2026-09). 로그와 이력 파일의 형식은 [Ollama](../../02-artifacts/local-ai/ollama.md) 쪽에서 다룹니다.

### OS 별 위치

공식 문서, 분석 도구 코드, 논문, 관찰로 알 수 있는 위치를 OS 별로 모으면 아래와 같습니다.

| 대상 | Windows | macOS | Linux | 근거 |
|---|---|---|---|---|
| Claude Code 데이터 폴더 | `%USERPROFILE%\.claude` | `~/.claude` | `~/.claude` | [5] |
| Claude Code 세션 기록 | `%USERPROFILE%\.claude\projects\` | `~/.claude/projects/` | `~/.claude/projects/` | [4][5] |
| Claude 데스크톱 데이터 폴더 | 스토어 판 `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude`, 그 밖의 설치 `%APPDATA%\Claude` | `~/Library/Application Support/Claude` | `~/.config/Claude` | [7] |
| Ollama 모델 | `C:\Users\%username%\.ollama\models` | `~/.ollama/models` | `/usr/share/ollama/.ollama/models` | [3] |
| Ollama 서버 로그 | `%LocalAppData%/Ollama/server.log` | 공개 자료 없음 | 공개 자료 없음 | [11] |

Electron 으로 만든 데스크톱 앱의 기본 데이터 폴더는 [Electron·웹뷰 앱의 저장 구조](electron-webview.md) 에서, Claude 데스크톱 폴더의 내용은 [Claude](../../02-artifacts/chat-services/claude/index.md) 쪽에서 다룹니다. 표에서 "공개 자료 없음" 인 칸은 검체에서 기본 위치와 설정을 보고 확인합니다.

### Windows 스토어(MSIX) 앱의 위치

Claude 데스크톱은 설치 방식에 따라 데이터 폴더가 다릅니다. agentsview 코드는 MSIX 패키지로 설치한 경우 `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude` 를, MSIX 가 아니거나 예전 방식으로 설치한 경우 `%APPDATA%\Claude` 를 데이터 폴더로 적습니다 [7]. 두 곳 모두 아래에 Cowork 세션 폴더 `local-agent-mode-sessions` 가 있습니다 [7].

스토어 판을 쓴 Windows 11 에서는 같은 패키지 폴더의 `LocalCache\Local\` 아래에도 파일이 있었습니다. `claude-cli-nodejs\Cache\` 아래 JSONL 파일(키: `cwd`, `debug`, `sessionId`, `timestamp`)과 npm·pip·NuGet 캐시, `GitHub CLI\device-id` 같은 개발 도구 폴더가 보였습니다(확인 범위: Windows 11, 2026-09). 그러니 스토어 판을 쓴 PC 에서는 `%APPDATA%`·`%LOCALAPPDATA%` 바로 아래만 보지 말고 패키지 폴더의 `LocalCache` 아래도 함께 봅니다.

### 동기화 — 여러 기기에 같은 대화가 보이는 까닭

같은 계정의 대화가 웹·데스크톱·모바일에 똑같이 보이면 대화 목록의 원본은 서버 계정에 있다고 보고, 기기마다 남은 사본은 따로 수집합니다. Claude Code 의 Remote Control 세션은 실행을 사용자 기기에서 하고, 연결된 동안에는 대화 기록 사본을 서버에도 저장합니다 [4]. 이런 세션은 기기의 세션 기록과 서버 사본이 함께 있습니다.

Claude 데스크톱 데이터 폴더의 `bridge-state.json` 에는 `enabled`, `environmentId`, `localSessionId`, `remoteSessionId`, `processedMessageUuids`, `pendingProcessedAcks`, `userConsented` 키가 있었습니다(확인 범위: Windows 11, 2026-09). 이 파일의 용도를 설명한 공개 문서가 없으므로, 검체에서는 `localSessionId` 와 `remoteSessionId` 값을 세션 기록의 세션 ID 와 대조해 두 세션이 이어졌는지 확인합니다.

## 읽는 법

1. 기기에서 어떤 방식으로 AI 서비스를 썼는지 먼저 확인합니다. 설치된 앱, 브라우저 방문 기록, 사용자 폴더 아래 `.claude`·`.codex`·`.gemini`·`.cursor`·`.ollama` 같은 도구 폴더, 스토어 앱 패키지 폴더, 휴대전화의 앱 폴더를 봅니다. 모으는 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) 를 따릅니다.
2. 서비스마다 원본이 서버에 있는지 기기에 있는지 가립니다. 원본이 서버에 있다면 계정 내보내기 파일이나 서비스 회사 회신이 있는지 확인하고, 없다면 기기에서 찾은 대화는 사본이라고 적어 둡니다.
3. 원본이나 사본이 기기에 있다면 폴더째 복사한 사본에서 분석합니다. 앱이 쓰고 있는 데이터베이스는 잠겨서 열리지 않을 수 있고, SQLite 는 `-wal`·`-shm` 파일을 함께 가져와야 합니다(자세한 내용은 [Electron·웹뷰 앱의 저장 구조](electron-webview.md) 와 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html)).
4. 서버 쪽 기록과 기기 쪽 기록의 시각을 한 표에 놓고 맞춰 봅니다. 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다.

## 포렌식에서 중요한 점

서버에서 지운 대화와 기기에서 지운 파일은 따로 봅니다. 서버 쪽은 서비스 회사의 보관 정책에 따라 사라지는 시점이 정해지고, 기기 쪽은 앱의 캐시 정리, 도구의 자동 정리 설정, 사용자의 삭제에 따라 사라집니다. 한쪽에서 지운 대화가 다른 쪽에 남을 수 있으므로 서버 내보내기와 기기 사본을 둘 다 봅니다. 기기 캐시와 데이터베이스에서 지운 내용을 되살리는 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md) 에서 다룹니다.

기기에 원본을 두는 도구는 자동 정리로 세션 기록이 사라져도 입력 이력이나 사용량 통계 같은 다른 파일이 남을 수 있습니다. 로컬 AI 는 모델을 지운 뒤에도 Ollama 서버 로그의 다운로드 기록에 모델 정보가 남아 어떤 모델을 설치했었는지 알 수 있습니다 [11]. 무엇이 지워지고 무엇이 남는지는 [대화 기록 보관 설정과 삭제](retention-deletion.md) 에 정리했습니다.

## 함정

**폴더가 없거나 비어 있다고 쓰지 않았다고 볼 수 없습니다.** Claude Code 는 `CLAUDE_CONFIG_DIR` 로 [5], Ollama 는 `OLLAMA_MODELS` 로 [3] 저장 위치를 옮길 수 있고, 웹에서 돈 클라우드 세션은 사용자 PC 에 기록을 남기지 않을 수 있습니다 [4]. 기본 위치에 없다면 환경 변수와 다른 위치를 먼저 확인합니다.

**Windows 데스크톱 앱의 폴더를 한 곳으로 단정하지 않습니다.** Claude 데스크톱은 스토어 판이면 `%LOCALAPPDATA%\Packages` 아래 패키지 폴더에, 그 밖의 설치면 `%APPDATA%\Claude` 에 데이터를 둡니다 [7]. 한 PC 에 두 폴더가 모두 있을 수 있으니 둘 다 확인합니다.

**모바일 앱에 대화가 없다고 서비스를 안 썼다고 쓰지 않습니다.** Gemini 앱은 대화를 클라우드에 두므로 [10] 기기에서는 설치와 사용 흔적만 찾고 대화는 Takeout 이나 서비스 회사 회신으로 확인합니다. ChatGPT·Claude 앱도 분석기가 시험한 판과 지금 판이 다를 수 있습니다 [8][9].

**계정에 대화가 보인다고 그 기기에서 대화했다고 쓸 수 없습니다.** 동기화된 서비스는 어느 기기에서든 같은 대화 목록을 보여 주고, 기기의 사본도 다른 기기에서 한 대화를 받아 온 것일 수 있습니다. 입력한 기기와 사람을 가리는 일은 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md) 의 방법을 따릅니다.

**앱 버전에 따라 폴더 구성이 바뀝니다.** 이 쪽의 Windows 관찰은 2026-09 한 시점의 모습입니다. 검체를 볼 때는 그 검체의 앱 버전을 따로 확인해 함께 적습니다.

## 도구

폴더 구성은 파일 탐색기나 `dir /s`, `ls -laR` 같은 기본 명령으로 먼저 목록을 뜨고, 목록을 사본과 함께 보관합니다. JSON·JSONL 파일은 `jq` 같은 공개 도구로 읽고, SQLite 파일은 DB Browser for SQLite 같은 공개 도구로 엽니다. 개발 도구의 세션 파일은 agentsview 가 여러 도구의 기본 위치를 찾아 읽고 [7], 휴대전화 추출본의 ChatGPT·Claude 앱 데이터는 ALEAPP·iLEAPP 의 분석기가 읽으며 [8][9], 로컬 AI 앱의 흔적은 LangurTrace 가 모아 분석합니다 [11]. 크롬 계열 저장소(LevelDB·IndexedDB·쿠키 DB)를 읽는 법은 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html) 와 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html) 를 봅니다.

## 참고 문헌

1. Claude Privacy Center — How long do you store my data? — https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data
2. Gemini Apps Help — Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961?hl=en
3. Ollama — FAQ — https://docs.ollama.com/faq
4. Claude Code Docs — Data usage — https://code.claude.com/docs/en/data-usage
5. Claude Code Docs — .claude 폴더 참조 (claude-directory) — https://code.claude.com/docs/en/claude-directory
6. Claude Code Docs — Advanced setup — https://code.claude.com/docs/en/setup
7. kenn-io/agentsview — `README.md`(2026-09-11, v0.44.0, Supported Agents 표), `internal/parser/cowork_paths.go`, `internal/parser/gemini_provider.go`, `internal/parser/codex.go` — https://github.com/kenn-io/agentsview (2026-09-25 열람)
8. ALEAPP — `scripts/artifacts/chatgpt.py`(Evangelos Dragonas, 2026-08-01 갱신), `scripts/artifacts/chatgpt2.py`(Alexis Brignoni, 2026-07-10 갱신), `scripts/artifacts/claude.py`(Brandon Baye, 2026-08-09 갱신) — https://github.com/abrignoni/ALEAPP (2026-09-25 열람)
9. iLEAPP — `scripts/artifacts/chatgpt.py`(Evangelos Dragonas, 2026-08-21 갱신), `scripts/artifacts/iOSclaude.py`(Brandon Baye, 2026-08-09 갱신) — https://github.com/abrignoni/iLEAPP (2026-09-25 열람)
10. Sonali Tyagi, Yufeng Gong, Umit Karabiyik, "Forensic analysis and privacy implications of LLM mobile apps: A case study of ChatGPT, Copilot, and Gemini", Forensic Science International: Digital Investigation, 54 (2025), 301974. https://doi.org/10.1016/j.fsidi.2025.301974 (초록)
11. Sungjo Jeong, Sangjin Lee, Jungheum Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987 (DFRWS APAC 2025). https://doi.org/10.1016/j.fsidi.2025.301987
12. Shishir Panta, Ruba Alsmadi, Ibrahim Baggili, "Seeing the Evidence: A Forensic Framework for Analyzing Ray-Ban Meta AI Smart Glasses", Forensic Science International: Digital Investigation (2026), DFRWS USA 2026 — https://dfrws.org/presentation/seeing-the-evidence-a-forensic-framework-for-analyzing-ray-ban-meta-ai-smart-glasses/
