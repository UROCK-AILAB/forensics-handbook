---
title: "Gemini CLI"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 630
---

# Gemini CLI (Gemini CLI)

Gemini CLI 는 Google 의 명령줄 AI 에이전트이고, 대화할 때마다 프롬프트·답변·도구 실행·토큰 사용량을 프로젝트별 폴더 `~/.gemini/tmp/<project_hash>/chats/` 에 자동으로 저장하지만, 기본으로 30일이 지난 세션은 지우기 때문에 오래된 기록이 없는 것이 정상일 수 있습니다.

> 확인 날짜: 2026-09. 앱 버전은 확인하지 못했습니다. 세션 저장 방식은 공식 저장소의 세션 관리 문서[1] 기준입니다. 관찰한 PC 의 `~/.gemini` 에는 설정과 다른 도구의 폴더만 있고 `tmp/` 가 없어서, 세션 파일의 내부 구조는 직접 보지 못했습니다(확인 범위: Windows 11, 2026-09).

## 무엇을 기록하나 · 왜 생기나

Gemini CLI 는 대화하는 동안 세션을 자동으로 저장해서, 중간에 끊어도 그때까지의 내용이 남습니다[1]. 저장하는 내용은 프롬프트와 모델 답변, 모든 도구 실행의 입력과 출력, 토큰 사용량(입력·출력·캐시 등)이고, 모델의 생각·추론 요약도 있으면 함께 담습니다[1]. 도구 실행의 입력과 출력까지 담기 때문에, 에이전트가 어떤 명령을 돌리고 무엇을 돌려받았는지를 대화 흐름 안에서 볼 수 있습니다.

세션은 프로젝트별로 나뉩니다. 저장 폴더 이름의 `<project_hash>` 는 프로젝트 루트 폴더마다 다르고, 다른 폴더에서 실행하면 그 프로젝트의 기록으로 바뀝니다[1]. 사용자는 `gemini --resume`(마지막 세션, 번호나 ID 로 고를 수도 있음)이나 CLI 안의 `/resume` 으로 지난 세션을 이어 갈 수 있습니다[1].

기록은 영원히 남지 않습니다. 기본 보관 기간은 30일이고, `settings.json` 의 `sessionRetention` 으로 바꿀 수 있습니다[1]. 서버 쪽(Google 계정·API 쪽)에 무엇이 얼마나 남는지는 이번에 연 자료로 확인하지 못했고, 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다. 웹·앱으로 쓰는 Gemini 는 [Gemini](../chat-services/gemini/index.md)에서 따로 다룹니다.

## 위치와 버전별 차이

아래 표는 문서와 관찰로 확인한 위치만 담습니다. 프로젝트별 `.gemini/settings.json`, OS 별 시스템 설정 경로, 설정 우선순위는 설정 문서가 열리지 않아(404) 확인하지 못했습니다.

| 위치 | 담는 것 | 근거 |
|---|---|---|
| `~/.gemini/tmp/<project_hash>/chats/` | 프로젝트별 세션(대화) 기록 | 문서[1] |
| `~/.gemini/settings.json` | 사용자 설정(보관 기간, 훅 등) | 문서[1], 관찰 |
| `~/.gemini/antigravity/` | 어느 제품이 쓰는지 확인 못 함 | 관찰 |
| `~/.gemini/config/` | 어느 제품이 쓰는지 확인 못 함 | 관찰 |

로그인 정보 파일, `GEMINI.md`, 원격 측정(telemetry) 파일 출력, 체크포인트, MCP 서버 설정 키는 이번 자료에 없어서 쓰지 않습니다. MCP 전반은 [MCP 서버와 도구 호출 기록](mcp.md)에서 다룹니다.

관찰한 PC 의 `%USERPROFILE%\.gemini` 에는 파일이 26개 있었지만 대화 기록 폴더 `tmp/` 는 없었습니다. 같은 폴더 안에는 아래 두 폴더가 있었습니다(확인 범위: Windows 11, 2026-09).

```
antigravity/antigravity_state.pbtxt
antigravity/installation_id
antigravity/crashes/<파일>.log
antigravity/knowledge/knowledge.lock
antigravity/bin/webm_encoder.exe
antigravity/builtin/skills/<이름>/SKILL.md          (3개)
antigravity/builtin/skills/<이름>/docs/             hooks.md, json_configs.md, mcp_servers.md, plugins.md, rules.md, skills.md
antigravity/builtin/skills/<이름>/references/       app.md, cli.md, ide.md, sdk.md
config/config.json                                  키 userSettings.remoteControlHostname
config/hooks.json                                   최상위 <도구 이름> 아래 PreInvocation, PostInvocation, PostToolUse, Stop
config/mcp_config.json                              JSON 으로 읽히지 않음
config/projects/<파일>.json                         키 id, name, updatedAt
```

이 두 폴더를 Gemini CLI 가 쓰는지, 다른 Google 개발 도구가 쓰는지는 확인하지 못했습니다. 같은 `.gemini` 폴더를 다른 도구도 쓸 수 있어서, `.gemini` 가 있다는 사실만으로 Gemini CLI 를 썼다고 단정하지 않습니다.

## 구조

### 세션 폴더

세션 파일이 JSON 인지 JSON Lines 인지, 칸 이름이 무엇인지는 확인하지 못했습니다. 문서로 확인한 것은 저장 위치가 프로젝트별 폴더라는 점과 담는 내용(프롬프트, 답변, 도구 실행 입력·출력, 토큰 사용량)뿐입니다[1]. `<project_hash>` 를 어떤 값으로 만드는지도 문서에 없어서, 폴더 이름에서 프로젝트 경로를 거꾸로 알아낼 수 있다고 쓰지 않습니다. 어느 프로젝트의 세션인지는 파일 안에 작업 폴더가 적혀 있는지를 열어 보고 판단합니다.

### 설정 `settings.json` 의 보관 설정

보관을 다루는 키는 아래와 같고, 따로 정하지 않으면 30일 동안 보관합니다[1].

| 키 | 뜻 |
|---|---|
| `sessionRetention.enabled` | 자동 정리 사용 여부, 기본 `true` |
| `sessionRetention.maxAge` | 보관 기간(`"24h"`, `"7d"` 같은 형식), 기본 `"30d"` |
| `sessionRetention.maxCount` | 남길 세션 수 |
| `sessionRetention.minRetention` | 최소 보관 기간, 기본 `"1d"` |
| `model.maxSessionTurns` | 세션 하나의 길이(주고받은 횟수) 제한, 기본 `-1`(제한 없음) |

아래는 보관 기간을 줄인 설정을 새로 만든 예시이고, 관찰한 값이 아닙니다.

```json
{
  "sessionRetention": {
    "enabled": true,
    "maxAge": "7d",
    "maxCount": 20
  }
}
```

### 관찰한 훅 설정

관찰한 PC 의 `settings.json` 에는 `hooks.AfterAgent`, `hooks.AfterTool`, `hooks.BeforeAgent`, `hooks.BeforeTool` 이 있었고, 각 항목은 `hooks` 목록을 담은 배열이었습니다(확인 범위: Windows 11, 2026-09). 훅의 공식 형식은 이번 자료로 확인하지 못했습니다. 에이전트 동작 전후와 도구 실행 전후에 걸리는 이름이라서, 걸린 명령이 감사 기록을 남기는지 스크립트를 열어 확인할 곳입니다.

## 증거로서 의미

**증명하는 것.** `tmp/<project_hash>/chats/` 에 세션이 있으면 그 사용자 계정에서 그 프로젝트 폴더를 기준으로 Gemini CLI 와 대화한 기록이 있다는 뜻이고, 도구 실행의 입력과 출력이 함께 있으면 "이 세션에서 에이전트가 이 명령을 실행해 이 출력을 받은 기록이 있다" 고 쓸 수 있습니다. 토큰 사용량은 대화 규모를 가늠하는 근거가 됩니다. `settings.json` 의 `sessionRetention` 값은 기록이 얼마나 오래 남도록 설정되어 있었는지를 보여 줍니다.

**증명하지 못하는 것.** 세션이 없다고 사용하지 않았다고 말할 수 없는데, 기본 30일 정리나 사용자가 줄인 보관 설정으로 사라졌을 수 있기 때문입니다. `.gemini` 폴더나 그 안의 `antigravity/`·`config/` 는 다른 Google 도구의 흔적일 수 있어서 Gemini CLI 사용의 증거로 바로 쓰지 않습니다. 세션에 적힌 도구 실행이 실제로 파일을 바꿨는지는 파일 시스템과 git 이력으로 따로 확인하고, 입력한 사람이 누구인지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 좁힙니다.

## 시각 해석

세션 파일 안의 시각 칸과 그 기준(UTC 인지 현지 시각인지)은 확인하지 못했습니다. 세션은 대화하는 동안 자동으로 저장되어서[1], 파일 수정 시각은 대체로 그 세션의 마지막 저장 때를 가리키지만 `--resume` 으로 이어 쓰면 오래된 세션의 수정 시각도 새로 바뀔 수 있습니다. 기본 30일 정리가 있어서, 남아 있는 가장 오래된 세션의 시각은 "처음 쓴 때" 가 아니라 "정리 기준 안에서 남은 가장 오래된 때" 로 읽습니다. 여러 출처를 한 줄로 맞추는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

기본 30일 정리는 정상 동작이라서 오래된 세션이 없다고 조작으로 볼 이유는 없습니다[1]. 다만 `maxAge` 나 `maxCount` 를 사건 무렵에 줄였다면 의도적으로 기록을 줄였을 가능성을 따져 볼 수 있고, 그때는 `settings.json` 의 수정 시각과 백업·볼륨 섀도 사본의 이전 판을 함께 봅니다. 보관 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

세션이 프로젝트별로 흩어져서 `tmp/` 아래 폴더를 모두 수집해야 하고, 한 폴더만 보고 "기록이 적다" 고 쓰면 안 됩니다. 정리로 지운 세션 파일은 할당되지 않은 영역에 조각으로 남을 수 있고, 되살리는 일반 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)에 있습니다. 이번 조사에서 확인하지 못한 항목(파일 형식, 로그인 정보 파일, 설정 우선순위)은 다른 도구의 규칙으로 메우지 말고 검체와 그 버전의 문서로 확인합니다.

## 직접 분석해 보기

**헥스로 한 번.** 파일 형식을 모를 때는 첫 바이트부터 봅니다. 첫 바이트가 `7B`(`{`)이고 줄마다 `{` 로 시작해 `0A` 로 끝나면 JSON Lines, 파일 전체가 `{` 하나로 열려 `}` 로 닫히면 JSON 한 덩어리로 봅니다. 보관 설정은 키 문자열 바이트로 찾습니다. 아래는 문자 인코딩대로 만든 예시이고, 검체에서 뜬 바이트가 아닙니다.

```
만든 예시(인코딩 명세로 만든 바이트)
"sessionRetention"  UTF-8  73 65 73 73 69 6F 6E 52 65 74 65 6E 74 69 6F 6E
"maxAge"            UTF-8  6D 61 78 41 67 65
```

**공개 도구로 한 번.** 수집한 사본에서 프로젝트별 세션 수와 보관 설정을 봅니다. 경로는 만든 예시이고, 원본이 아니라 사본에서만 돌립니다.

```sh
# 만든 예시 경로
GM=/cases/case-0001/copy/alice/.gemini
# 프로젝트 폴더별 세션 파일 수와 수정 시각
find "$GM/tmp" -path '*/chats/*' -type f -printf '%TY-%Tm-%Td %TH:%TM  %p\n' | sort
# 보관 설정과 훅 이벤트
jq '{sessionRetention, maxSessionTurns: .model.maxSessionTurns, hooks: (.hooks // {} | keys)}' "$GM/settings.json"
# 세션 파일에서 특정 문자열 찾기
rg -l "sample-app" "$GM/tmp"
```

세션 파일을 처음 열 때는 형식을 짐작하지 말고 `head -c 300` 으로 앞부분을 본 뒤 jq 로 키 목록을 뽑습니다.

## 교차 검증

세션에 적힌 도구 실행은 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)의 흐름으로 셸 기록·git 이력과 맞춰 보고, 외부 문서가 에이전트 동작을 부추긴 정황이 있으면 [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md)으로 이어 갑니다. 같은 PC 에 [Codex CLI](codex-cli.md)나 [Claude Code](claude-code/index.md)가 있으면 훅 파일이 어느 도구 것인지 먼저 나눕니다. 서비스 접속은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)과, 회사에서 허용한 도구인지는 [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md)와 함께 봅니다. 수집 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다.

## 실습

공개 검체에 Gemini CLI 흔적이 들어 있는지는 확인하지 못했습니다. 시험용 가상 머신과 시험 계정으로 풀어 봅니다.

1. 서로 다른 프로젝트 폴더 두 곳에서 대화한 뒤 `tmp/` 아래 폴더가 몇 개 생겼는지, 세션 파일의 형식과 키가 무엇인지 적어 봅니다.
2. 도구를 쓰는 요청을 한 번 넣고, 세션 파일에 도구 입력과 출력이 어떤 모양으로 남는지 확인합니다.
3. `maxAge` 를 `"24h"` 로 줄이고 하루 뒤 다시 실행해, 어느 시점에 오래된 세션이 사라지는지 봅니다.
4. `--resume` 으로 지난 세션을 이어 쓴 뒤 그 파일의 수정 시각이 어떻게 바뀌는지 기록합니다.

## 참고 문헌

1. google-gemini/gemini-cli — docs/cli/session-management.md — https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/cli/session-management.md
