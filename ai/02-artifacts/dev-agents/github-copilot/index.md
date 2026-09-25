---
title: "GitHub Copilot"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 570
has_children: true
has_toc: false
---

# GitHub Copilot (VS Code·JetBrains)

GitHub Copilot 은 여러 IDE 안에서 도는 코딩 도우미이고, VS Code 에서는 작업 폴더마다 채팅 세션 파일과 세션 목록을 사용자 데이터 폴더에 남기며, IDE 마다 따로 로그를 남깁니다.

> 확인 날짜: 2026-09. GitHub·VS Code 공식 문서(2026-09-25 열람)와 VS Code 오픈소스 코드(`chatSessionStore.ts`, 그 파일의 마지막 커밋 2026-08-06)를 근거로 썼습니다. 이 묶음에는 기기 관찰 기록이 없어서 실물 파일로 확인한 내용은 없고, Copilot 확장·플러그인 버전도 확인하지 않았습니다.

## 왜 중요한가

Copilot 은 JetBrains IDE(IntelliJ IDEA, Android Studio, GoLand, PhpStorm, PyCharm, RubyMine, WebStorm, Rider), VS Code, Visual Studio, Xcode, Vim/Neovim 에서 돌아서, 개발자 PC 를 조사할 때 어느 IDE 를 썼는지부터 가려야 합니다. 이 가운데 기록이 가장 많이 확인된 곳은 VS Code 이고, 로컬 채팅 세션은 작업 폴더(워크스페이스) 단위로 묶여 사용자 데이터 폴더에 JSON·JSONL 파일로 남습니다. 세션 목록에는 작업 폴더와 마지막 메시지 시각이 들어가서 "어느 프로젝트에서 언제쯤 AI 와 대화했나" 를 좁히는 데 쓸 수 있습니다.

VS Code 는 로컬 세션 말고도 Claude·Codex 세션과 Copilot CLI·GitHub Copilot 앱·Claude Code 에서 들어온 외부 세션을 한 목록에 보여 줍니다. 클라우드 세션과 외부 세션은 목록에 외부 세션으로 표시되는데, 그 대화 원본이 PC 에 남는지 서버에만 있는지는 확인하지 못했습니다.

### PC 에 없고 서버에 있는 것

GitHub 가 프롬프트·응답을 서버에 얼마나 보관하는지, 학습에 쓰는지는 공식 자료를 열지 못해 확인하지 못했고, 조직 요금제의 감사 로그 항목도 확인하지 못했습니다. 서버 쪽 기록을 얻는 방법은 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 봅니다.

## 한눈에 보기

| 위치 | OS | 앱 버전 | 알려 주는 것 |
|---|---|---|---|
| VS Code `Code/User/settings.json`, 프로필별 `settings.json`, 작업 폴더의 `.vscode/settings.json` | Windows·macOS·Linux | 문서 기준(2026-09) | Copilot·채팅 설정, 원격 측정 범위 |
| VS Code 사용자 데이터 폴더 안 `chatSessions` 등의 `.json`·`.jsonl` | Windows·macOS | 소스 기준(2026-08). 1.109 전은 `.json`, 1.109 부터 `.jsonl` | 로컬 채팅 세션 기록 |
| VS Code 저장소 서비스의 키 `chat.ChatSessionStore.index` | Windows·macOS | 소스 기준(2026-08). 담기는 파일은 확인 못 함 | 세션 제목, 마지막 메시지 시각, 작업 폴더, 외부 세션 여부 |
| VS Code 출력 창, 확장 로그 폴더, `telemetry.log` | Windows·macOS | 문서 기준 | 오류·연결 문제, 원격 측정 |
| JetBrains `idea.log` | Windows·macOS | 문서 기준. 경로는 확인 못 함 | Copilot 오류, 사용자가 켠 진단·trace·인증서 기록 |
| `~/Library/Logs/GitHubCopilot/` | macOS | 문서 기준 | Xcode 용 Copilot 로그 |
| 사용자가 고른 자리의 내보낸 JSON | 모두 | 문서 기준 | `Chat: Export Chat...` 로 내보낸 프롬프트·응답 |

JetBrains 플러그인의 채팅 기록 저장 여부와 로그인 토큰 저장 방식(자격 증명 관리자·키체인 사용 여부)은 확인하지 못해서 표에 넣지 않았습니다.

## 읽는 순서

1. [Windows](windows.md) — 설정 파일 경로, 채팅 세션 폴더와 파일 형식, 세션 색인의 칸, 보관·삭제·내보내기
2. [macOS](macos.md) — macOS 경로, Xcode 용 Copilot 로그 폴더
3. [로그와 원격 측정](logs.md) — IDE 별 로그 여는 법, 사용자가 켜야 생기는 기록, VS Code 원격 측정 설정

## 함께 볼 페이지

- [Claude Code](../claude-code/index.md), [Cursor](../cursor.md), [Codex CLI](../codex-cli.md), [Gemini CLI](../gemini-cli.md) — 같은 기준으로 비교
- [MCP 서버와 도구 호출 기록](../mcp.md)
- [Microsoft Copilot](../../chat-services/copilot/index.md) — 이름이 비슷한 다른 서비스
- [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)
- [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)
- [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md)
- [기밀 자료를 AI에 넣었나](../../../04-scenarios/data-leak/confidential-input.md)
- [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)
