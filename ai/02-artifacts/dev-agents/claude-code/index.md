---
title: "Claude Code"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 550
has_children: true
has_toc: false
---

# Claude Code (Claude Code)

Claude Code 는 터미널에서 도는 코딩 에이전트이고, 대화 전문과 도구 호출·결과, 입력 이력, 편집 전 파일 사본, 권한·훅 설정을 사용자 PC 의 `~/.claude/` 폴더에 평문으로 남깁니다.


## 왜 중요한가

Claude Code 는 모델 호출만 네트워크로 보내고 파일 편집과 명령 실행은 사용자 PC 에서 합니다. 그래서 "AI 가 무엇을 실행했나", "어떤 파일을 모델에 보냈나", "누가 허용했나" 같은 질문의 답이 대부분 PC 안의 기록에 있습니다. 세션 기록은 저장할 때 암호화하지 않고 OS 파일 권한으로만 보호합니다[1]. 사고 조사에서는 사용자 폴더와 함께 저장소 안의 `.claude/` 폴더도 보는데, 그 까닭은 [설정·권한·훅](settings-permissions.md)의 훅 절에 있습니다.

기록 파일의 형식은 공개된 명세가 없고, 공식 문서에 없는 칸은 실제 기록과 시험 자료로만 알 수 있습니다[8]. 판이 바뀌면 칸이 달라질 수 있으므로 검체의 줄을 직접 열어 이 핸드북의 설명과 맞는지 확인합니다. 기록에는 서명이 없고 사용자가 고칠 수 있어서, 기록은 도구가 적은 내용의 증거일 뿐 사람이 한 행동의 증명은 아닙니다[9].

지원 OS 는 macOS 13.0 이상, Windows 10 1809 이상과 Windows Server 2019 이상, Ubuntu 20.04 이상, Debian 10 이상, Alpine 3.19 이상이고, 모든 OS 에서 사용자 데이터 폴더는 `~/.claude/`(Windows 는 `%USERPROFILE%\.claude`)입니다[2][3]. 설치는 네이티브 설치기, Homebrew, WinGet, apt·dnf·apk, npm 으로 할 수 있고, VS Code 확장·JetBrains 플러그인·데스크톱 앱도 같은 폴더에 씁니다. 다만 Claude 데스크톱 앱은 자기 데이터 폴더에 세션 메타와 Cowork 기록을 따로 두므로, 두 폴더를 모두 떠야 전체가 보입니다[6].

### PC 에 없고 서버에 있는 것

로컬 기록은 기본 30일 뒤 지워지지만 서버 쪽 보관은 계정 종류에 따라 다릅니다[1]. 개인 요금제(Pro·Max 등)는 모델 개선 사용을 허용하면 5년, 거부하면 30일 보관하고, 상업 요금제(Team·Enterprise·API)는 기본 30일이며 데이터를 보관하지 않는 설정(ZDR)은 자격 확인 뒤 조직별로 켭니다. `/feedback`, `/bug`, `/share` 로 보낸 대화는 5년 보관하고, 세션 품질 설문 뒤 기록 공유에 동의하면 기록과 하위 에이전트 기록, 세션 로그 원본을 올려 6개월까지 보관합니다.

웹에서 돌리는 클라우드 세션은 Anthropic 의 가상 머신에서 돌아서 로컬 PC 에 세션 기록이 없을 수 있고, 이 경우 대화 원본은 서버에만 있습니다[1]. 클라우드 세션이 로컬 PC 에 무엇을 남기는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. Remote Control 세션은 로컬에서 실행하지만 연결된 동안 기록 사본을 서버에도 둡니다[1]. 서버 쪽 기록을 얻는 방법은 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)과 [Claude 기업용 감사 로그](../../network-enterprise/claude-enterprise.md)에 있습니다.

## 한눈에 보기

### 사용자 폴더 `~/.claude/` 와 `~/.claude.json`

| 위치 | OS | 근거·시험한 판 | 알려 주는 것 |
|---|---|---|---|
| `~/.claude/projects/` 아래 세션별 `.jsonl` | 모두 | 문서[2], 키는 관찰, 도구[6][7][8] | 대화 전문, 도구 호출과 입력·출력, 작업 폴더, 브랜치, 훅 실행 흔적 |
| 세션 폴더 아래 `subagents/agent-<id>.jsonl` 과 `agent-<id>.meta.json` | 모두 | agentsview 관찰(2026-07)[8] | 하위 에이전트 대화와 사용량(이 사용량은 부모 세션 파일에 없음) |
| `~/.claude/history.jsonl` | 모두(아래 차이 참고) | 문서[2], 키는 관찰, 도구[6][7] | 입력한 프롬프트, 시각, 프로젝트 경로, 세션 ID(자동 삭제 안 함) |
| `~/.claude/file-history/<sessionId>/<hash>@v<N>` | 모두(아래 차이 참고) | 문서[2], 이름 규칙은 도구[6][7] | Claude 가 편집 도구로 바꾸기 전 파일 사본(원래 경로와 해시의 대응은 `.claude` 안에 없음[6]) |
| `~/.claude/paste-cache/<hash>.txt` | 모두(아래 차이 참고) | 도구[6] | 프롬프트에 붙여 넣은 내용 |
| `~/.claude/sessions/<pid>.json` | 모두 | 도구[6][7] | 프로세스별 PID, 세션 ID, 작업 폴더, 시작 시각, 상태, 버전, 진입 경로 |
| `~/.claude/shell-snapshots/snapshot-zsh-<ms>-<rand>.sh` | 모두(아래 차이 참고) | 도구[6] | Bash 도구가 쓴 셸 환경(alias, export, 함수, PATH), 파일 이름의 실행 시각(밀리초) |
| `~/.claude/.last-cleanup` | 모두 | 도구[6] | 마지막으로 오래된 세션 기록을 지운 시각 |
| `~/.claude/stats-cache.json` | 모두 | 문서[2], 키는 관찰 | 날짜·시간대별 사용량, 모델별 토큰·비용 합계(자동 삭제 안 함) |
| `~/.claude/backups/.claude.json.backup.*` | 모두 | 도구[6][7] | 계정 이메일, 조직 UUID, 구독 정보, 프로젝트별 비용 |
| `~/.claude/tasks/`, `~/.claude/plans/` | 모두 | 도구[7] | ccfx 는 세션 수·파일 수만 셈(내용은 검체로 확인) |
| `~/.claude/settings.json`, 프로젝트의 `.claude/settings*.json` | 모두 | 문서[2], 키는 관찰 | 권한 규칙, 훅, 플러그인 |
| `~/.claude.json` | 모두 | 문서[2] | 로그인 세션, MCP 서버 설정, 프로젝트별 신뢰 결정 |
| `%USERPROFILE%\.claude\.credentials.json` | Windows | 문서[4], 키는 관찰 | 구독 로그인 정보(평문) |
| 로그인 키체인 | macOS | 문서[4] | 구독 로그인 정보(암호화) |
| `~/.claude/image-cache/` | 모두 | 문서[2], v2.1.274 이하 | 붙여 넣은 이미지(그 뒤 버전은 임시 폴더 아래 세션별 `images/`) |
| 관리 정책 파일·레지스트리·구성 프로파일 | OS 마다 다름 | 문서[5] | 조직이 건 설정과 제한 |

`history.jsonl` 은 세션 기록이 지워진 뒤에도 몇 달 남습니다[6]. claude-forensics 는 `history.jsonl` 의 세션 ID 가운데 세션 기록 파일이 없는 것을 따로 모으고, `.last-cleanup` 시각과 함께 보여 줍니다. 이렇게 하면 기록이 지워진 세션도 프롬프트는 되살릴 수 있습니다. 자세한 짜임은 [세션 기록 구조](transcripts.md)에 있습니다.

Windows 에서 어떤 폴더가 생기는지는 출처마다 다릅니다. claude-forensics(v0.1.1, 2026-06)는 2026년 중반의 Windows 판 Claude Code 가 `history.jsonl`, `shell-snapshots/`, `paste-cache/`, `file-history/` 를 쓰지 않는 것으로 보았지만[6], 2026년 9월 Windows 11 에서는 `history.jsonl`, `file-history\`, `paste-cache\` 가 생기고 `shell-snapshots\` 는 생기지 않았습니다([Windows](windows.md) 참고). 판과 사용한 기능에 따라 다르므로, 폴더가 없다는 사실만으로 그 기능을 쓰지 않았다고 판단하지 않고 검체로 확인합니다.

`.credentials.json` 과 `backups/` 의 계정 정보는 보고서에서 가려야 합니다. 로그인 정보가 남는 곳 전체는 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

### Claude 데스크톱 앱 폴더

Claude 데스크톱 앱의 데이터 폴더에는 Cowork 세션 메타와 Cowork 에이전트 세션 기록이 남습니다[6][8]. 데이터 폴더 위치는 다음과 같습니다.

| OS | 데이터 폴더 | 근거 |
|---|---|---|
| macOS | `~/Library/Application Support/Claude/` | [6][8] |
| Windows(스토어판이 아닌 설치) | `%APPDATA%\Claude\` | [6][8] |
| Windows(MSIX 패키지 설치) | `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\` | [8] |
| Linux | `~/.config/Claude/` | [8] |

그 안에서 볼 곳은 아래와 같습니다. 표의 경로는 모두 데이터 폴더 기준입니다.

| 위치 | 근거 | 알려 주는 것 |
|---|---|---|
| `claude-code-sessions/<orgUuid>/<accountUuid>/local_<sessionId>.json` | [6] | Cowork 세션 메타 파일로, 제목, 모델, 작업 폴더, 보관 여부, 권한 모드, 원격 MCP 설정이 들어 있습니다. 소유 조직·계정 UUID 는 상위 폴더 이름에 있고, `cliSessionId` 로 `~/.claude/projects/` 의 세션 기록과 이어집니다 |
| `local-agent-mode-sessions/<orgUuid>/<accountUuid>/local_<sessionId>.json` | [6][8] | Cowork 에이전트 세션의 제목, 첫 메시지, 소유 계정의 이메일과 이름, 허용한 폴더·도메인 |
| `local-agent-mode-sessions/…/local_<sessionId>/audit.jsonl` | [6] | Cowork 에이전트 대화 전문과, 에이전트 런타임이 적은 비용·턴 수 |
| `local-agent-mode-sessions/…/local_<sessionId>/.claude/projects/…/<cliSessionId>.jsonl` | [8] | Claude Code 와 같은 형식의 세션 기록, 그 옆 `subagents/` 의 하위 에이전트 기록 |
| `local-agent-mode-sessions/<orgUuid>/<accountUuid>/spaces.json` | [6] | Cowork 스페이스 ID 와 이름·폴더·지시문 |
| `cowork-enabled-cli-ops.json`, `claude_desktop_config.json`, `config.json`, `buddy-tokens.json`, `ant-did` | [6] | claude-forensics 가 수집 사본에 넣는 설정 파일입니다. 각 파일의 용도는 공개 자료에 설명이 없어 검체로 확인해야 합니다 |
| `vm_bundles/`, `Cache/`, `Code Cache/` | [6] | 큰 캐시 폴더라서 claude-forensics 는 수집 사본에서 뺍니다(`vm_bundles/` 는 12GB 정도) |

데스크톱 앱 자체의 대화 기록과 저장 구조는 [Claude](../../chat-services/claude/index.md)에서 다룹니다.

## 읽는 순서

1. [Windows](windows.md) — 설치 위치, 평문 로그인 파일, 정책 레지스트리, 관찰한 폴더 모양, 스토어판 데스크톱 앱과 겹치는 부분
2. [macOS](macos.md) — 버전 폴더와 실행 링크, 키체인에 들어가는 로그인 정보, 구성 프로파일
3. [세션 기록 구조](transcripts.md) — 기록 줄의 키, 입력 이력, 편집 전 사본, 자동 삭제와 남는 것
4. [설정·권한·훅](settings-permissions.md) — 설정 우선순위, 권한 규칙과 모드, 훅, 관리 정책, 원격 측정

## 공개 분석 도구

도구마다 시험한 Claude Code 판이 다르고, 지금 판과 기록 모양이 다를 수 있습니다.

- **claude-forensics**(forensicdave, v0.1.1, 2026-06-16)[6]: `.claude` 폴더를 읽기 전용 사본으로 뜨고, 세션·프롬프트·프로세스·셸 스냅숏·붙여 넣은 내용·편집 사본을 JSONL 로 뽑은 뒤 결과 파일의 SHA-256 목록을 만듭니다. jq 가 있으면 Claude 가 실행한 Bash 명령, 읽고 쓴 파일, 세션 기록이 지워진 프롬프트 목록도 만듭니다. 도구는 macOS·Linux 에서 돌고, Windows 에서 뜬 사본은 `-w` 옵션으로 데스크톱 데이터 폴더를 함께 지정해 읽습니다.
- **ccfx**(fkasasagi, v0.7.2, 2026-08-05)[7]: Go 로 만든 실행 파일 하나이고 Linux·macOS·Windows 에서 돕니다. `history.jsonl` 에서 `!` 로 시작하는 입력을 사용자가 직접 친 셸 명령으로 따로 표시하고, 프롬프트 인젝션 의심 세션을 고르는 절이 있습니다. `.credentials.json` 은 있는지와 크기·수정 시각만 기록하지만, `-ac` 옵션으로 만든 수집 압축본에는 로그인 정보가 평문 그대로 들어갑니다.
- **agentsview**(kenn-io)[8]: 여러 코딩 에이전트의 기록을 함께 읽는 도구입니다. 형식 근거 문서(2026-09-11 수정)에 Claude Code 2.1.220~2.1.233(2026-07~08)으로 시험한 관찰을 적어 두었고, 하위 에이전트 파일, 백그라운드 전환 때 생기는 중복 기록, 프로젝트 폴더 이름 규칙이 여기서 나옵니다. 자세한 내용은 [세션 기록 구조](transcripts.md)에 있습니다.
- **coding-agent-forensics**(Shorton88, v1.0.0, 2026-08-29)[9]: 브라우저에서 여는 HTML 파일 하나로 된 뷰어이고, Claude Code 의 하위 에이전트(sidechain) 기록을 살려서 보여 줍니다. 수집 때 `.credentials.json` 같은 로그인 파일은 조사에 보탬이 안 되니 모으지 말라고 권합니다.

## 함께 볼 페이지

- [MCP 서버와 도구 호출 기록](../mcp.md)
- [Codex CLI](../codex-cli.md), [Gemini CLI](../gemini-cli.md), [Cursor](../cursor.md) — 같은 기준으로 비교
- [Claude](../../chat-services/claude/index.md) — 웹·데스크톱 앱
- [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)
- [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)
- [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md)
- [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)
- [에이전트가 자격 증명을 건드렸나](../../../04-scenarios/agents/agent-credentials.md)
- [프롬프트 인젝션 사고 분석](../../../03-techniques/analysis/prompt-injection.md)

## 참고 문헌

1. Anthropic, Data usage — https://code.claude.com/docs/en/data-usage (2026-09-25 열람)
2. Anthropic, .claude 폴더 파일·폴더 참조(claude-directory) — https://code.claude.com/docs/en/claude-directory (2026-09-25 열람)
3. Anthropic, Advanced setup — https://code.claude.com/docs/en/setup (2026-09-25 열람)
4. Anthropic, Authentication — https://code.claude.com/docs/en/authentication (2026-09-25 열람)
5. Anthropic, Deploy managed settings — https://code.claude.com/docs/en/managed-settings (2026-09-25 열람)
6. forensicdave, claude-forensics v0.1.1 — https://github.com/forensicdave/claude-forensics , `README.md`, `docs/claude_forensics.md`, `docs/claude-forensics.md`, `claude_forensics.py`, `claude-forensics.sh`
7. fkasasagi, ccfx — https://github.com/fkasasagi/ccfx , `README.en.md`
8. kenn-io, agentsview — https://github.com/kenn-io/agentsview , `README.md`, `docs/internal/session-format-sources.md`, `internal/parser/cowork.go`, `internal/parser/cowork_paths.go`
9. Shorton88, coding-agent-forensics — https://github.com/Shorton88/coding-agent-forensics , `README.md`
