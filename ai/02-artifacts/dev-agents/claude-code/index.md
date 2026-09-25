---
title: "Claude Code"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 520
has_children: true
has_toc: false
---

# Claude Code (Claude Code)

Claude Code 는 터미널에서 도는 코딩 에이전트이고, 대화 전문과 도구 호출·결과, 입력 이력, 편집 전 파일 사본, 권한·훅 설정을 사용자 PC 의 `~/.claude/` 폴더에 평문으로 남깁니다.

> 확인 날짜: 2026-09. 공식 문서(2026-09-25 열람)와 Windows 기기 관찰을 함께 썼습니다. 기기 관찰은 이름과 키만 본 것이고 값은 가렸습니다(확인 범위: Windows 11, 2026-09). 관찰한 PC 의 설치 버전은 확인하지 않았고, macOS 는 문서만 근거로 썼습니다.

## 왜 중요한가

Claude Code 는 모델 호출만 네트워크로 보내고 파일 편집과 명령 실행은 사용자 PC 에서 합니다. 그래서 "AI 가 무엇을 실행했나", "어떤 파일을 모델에 보냈나", "누가 허용했나" 같은 질문의 답이 대부분 PC 안의 기록에 있습니다. 세션 기록은 저장할 때 암호화하지 않고 OS 파일 권한으로만 보호합니다. 사고 조사에서는 사용자 폴더와 함께 저장소 안의 `.claude/` 폴더도 보는데, 그 까닭은 [설정·권한·훅](settings-permissions.md)의 훅 절에 있습니다.

지원 OS 는 macOS 13.0 이상, Windows 10 1809 이상과 Windows Server 2019 이상, Ubuntu 20.04 이상, Debian 10 이상, Alpine 3.19 이상이고, 모든 OS 에서 사용자 데이터 폴더는 `~/.claude/`(Windows 는 `%USERPROFILE%\.claude`)입니다. 설치는 네이티브 설치기, Homebrew, WinGet, apt·dnf·apk, npm 으로 할 수 있고, VS Code 확장·JetBrains 플러그인·데스크톱 앱도 같은 폴더에 씁니다.

### PC 에 없고 서버에 있는 것

로컬 기록은 기본 30일 뒤 지워지지만 서버 쪽 보관은 계정 종류에 따라 다릅니다. 개인 요금제(Pro·Max 등)는 모델 개선 사용을 허용하면 5년, 거부하면 30일 보관하고, 상업 요금제(Team·Enterprise·API)는 기본 30일이며 데이터를 보관하지 않는 설정(ZDR)은 자격 확인 뒤 조직별로 켭니다. `/feedback`, `/bug`, `/share` 로 보낸 대화는 5년 보관하고, 세션 품질 설문 뒤 기록 공유에 동의하면 기록과 하위 에이전트 기록, 세션 로그 원본을 올려 6개월까지 보관합니다.

웹에서 돌리는 클라우드 세션은 Anthropic 의 가상 머신에서 돌아서 로컬 PC 에 세션 기록이 없을 수 있고, 이 경우 대화 원본은 서버에만 있습니다. 클라우드 세션이 로컬에 어떤 흔적을 남기는지는 확인하지 못했습니다. Remote Control 세션은 로컬에서 실행하지만 연결된 동안 기록 사본을 서버에도 둡니다. 서버 쪽 기록을 얻는 방법은 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)과 [Claude 기업용 감사 로그](../../network-enterprise/claude-enterprise.md)에 있습니다.

## 한눈에 보기

| 위치 | OS | 앱 버전 | 알려 주는 것 |
|---|---|---|---|
| `~/.claude/projects/` 아래 세션별 `.jsonl` | 모두 | 문서 기준(2026-09), 키는 관찰 | 대화 전문, 도구 호출과 입력·출력, 작업 폴더, 브랜치, 훅 실행 흔적 |
| `~/.claude/history.jsonl` | 모두 | 문서 기준, 키는 관찰 | 입력한 프롬프트, 시각, 프로젝트 경로(자동 삭제 안 함) |
| `~/.claude/file-history/` | 모두 | 문서 기준 | Claude 가 편집 도구로 바꾸기 전 파일 사본 |
| `~/.claude/stats-cache.json` | 모두 | 문서 기준, 키는 관찰 | 날짜·시간대별 사용량, 모델별 토큰·비용 합계(자동 삭제 안 함) |
| `~/.claude/settings.json`, 프로젝트의 `.claude/settings*.json` | 모두 | 문서 기준, 키는 관찰 | 권한 규칙, 훅, 플러그인 |
| `~/.claude.json` | 모두 | 문서 기준 | 로그인 세션, MCP 서버 설정, 프로젝트별 신뢰 결정 |
| `%USERPROFILE%\.claude\.credentials.json` | Windows | 문서 기준, 키는 관찰 | 구독 로그인 정보(평문) |
| 로그인 키체인 | macOS | 문서 기준 | 구독 로그인 정보(암호화) |
| `~/.claude/image-cache/` | 모두 | v2.1.274 이하 | 붙여 넣은 이미지(그 뒤 버전은 임시 폴더 아래 세션별 `images/`) |
| 관리 정책 파일·레지스트리·구성 프로파일 | OS 마다 다름 | 문서 기준 | 조직이 건 설정과 제한 |

## 읽는 순서

1. [Windows](windows.md) — 설치 위치, 평문 로그인 파일, 정책 레지스트리, 관찰한 폴더 모양
2. [macOS](macos.md) — 버전 폴더와 실행 링크, 키체인에 들어가는 로그인 정보, 구성 프로파일
3. [세션 기록 구조](transcripts.md) — 기록 줄의 키, 입력 이력, 편집 전 사본, 자동 삭제와 남는 것
4. [설정·권한·훅](settings-permissions.md) — 설정 우선순위, 권한 규칙과 모드, 훅, 관리 정책, 원격 측정

## 함께 볼 페이지

- [MCP 서버와 도구 호출 기록](../mcp.md)
- [Codex CLI](../codex-cli.md), [Gemini CLI](../gemini-cli.md), [Cursor](../cursor.md) — 같은 기준으로 비교
- [Claude](../../chat-services/claude/index.md) — 웹·데스크톱 앱
- [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)
- [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)
- [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)
- [에이전트가 자격 증명을 건드렸나](../../../04-scenarios/agents/agent-credentials.md)
- [프롬프트 인젝션 사고 분석](../../../03-techniques/analysis/prompt-injection.md)
