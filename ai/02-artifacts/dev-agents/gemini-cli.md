---
title: "Gemini CLI"
parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 660
---

# Gemini CLI

Gemini CLI 는 Google 의 명령줄 AI 에이전트이고, 대화할 때마다 프롬프트·답변·도구 실행·토큰 사용량을 프로젝트별 폴더 `~/.gemini/tmp/…/chats/` 에 한 줄씩 덧붙여 저장합니다. 기본 설정으로 30일이 지난 세션을 스스로 지우므로, 오래된 기록이 없는 것이 정상일 수 있습니다.

이 페이지의 파일 형식과 경로는 Gemini CLI 0.52.0-nightly.20260715 판 기준이고, 판에 따라 저장 방식이 바뀌었습니다(아래 "위치와 버전별 차이")[1][2][3][4].

## 무엇을 기록하나 · 왜 생기나

Gemini CLI 는 대화하는 동안 세션을 자동으로 저장해서, 중간에 끊어도 그때까지의 내용이 남습니다[1]. 저장하는 내용은 프롬프트와 모델 답변, 모든 도구 실행의 입력과 출력, 토큰 사용량(입력·출력·캐시 등), 그리고 있으면 모델의 생각·추론 요약입니다[1]. 도구 실행의 입력과 출력까지 담기 때문에, 에이전트가 어떤 명령을 돌리고 무엇을 돌려받았는지를 대화 흐름 안에서 볼 수 있습니다.

세션은 프로젝트별로 나뉩니다. 다른 프로젝트 폴더에서 실행하면 그 프로젝트의 기록으로 바뀌고[1], 사용자는 `gemini --resume`(`-r`, 번호나 세션 UUID 로 고를 수 있음)이나 CLI 안의 `/resume` 으로 지난 세션을 이어 갑니다[1]. `--list-sessions` 로 목록을 보고 `--delete-session` 이나 세션 브라우저의 `x` 키로 세션을 지울 수 있습니다[1].

기본 보관 기간은 30일이고 `settings.json` 에서 바꿀 수 있습니다[1]. 서버 쪽(Google 계정·API 쪽)에 남는 자료는 기기 기록과 따로 보고, 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md), 요청 절차는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)에 있습니다. 웹·앱으로 쓰는 Gemini 는 [Gemini](../chat-services/gemini/index.md)에서 따로 다룹니다.

## 위치와 버전별 차이

사용자 폴더 `~/.gemini`(Windows 는 `%USERPROFILE%\.gemini`)가 뿌리입니다. 홈 폴더를 얻지 못하면 시스템 임시 폴더 아래 `.gemini` 를 씁니다[3].

| 위치 | 담는 것 | 근거 |
|---|---|---|
| `~/.gemini/tmp/<프로젝트>/chats/session-*.jsonl` | 세션(대화) 기록. 옛 판은 `session-*.json` | [2][7] |
| `~/.gemini/tmp/<프로젝트>/chats/<부모 세션 ID>/<세션 ID>.jsonl` | 하위 에이전트 세션 | [2] |
| `~/.gemini/tmp/<프로젝트>/logs.json` | 사용자가 입력한 문장 기록 | [4] |
| `~/.gemini/tmp/<프로젝트>/checkpoint-<태그>.json` | `/resume save` 로 저장한 수동 체크포인트 | [1][4] |
| `~/.gemini/tmp/<프로젝트>/logs/session-<세션 ID>.jsonl` | 세션별 활동 로그 | [4] |
| `~/.gemini/tmp/<프로젝트>/tool-outputs/session-<세션 ID>/` | 세션별 도구 출력 | [4] |
| `~/.gemini/tmp/<프로젝트>/<세션 ID>/` | 세션별 계획(`plans`)·작업 추적(`tracker`)·작업(`tasks`) | [3][4] |
| `~/.gemini/tmp/<프로젝트>/.project_root` | 이 폴더가 가리키는 프로젝트 경로(평문) | [3] |
| `~/.gemini/projects.json` | 프로젝트 경로와 폴더 이름의 대응표 | [3] |
| `~/.gemini/history/<프로젝트>/` | 프로젝트별 기록 폴더(`.project_root` 가 함께 생김) | [3] |
| `~/.gemini/trustedFolders.json` | 신뢰한 폴더 목록 | [6][7] |
| `~/.gemini/settings.json` | 사용자 설정(보관 기간, 훅 등) | [1][3] |
| 프로젝트 폴더의 `.gemini/settings.json` | 프로젝트 설정 | [3] |
| `C:\ProgramData\gemini-cli\settings.json` | 시스템 설정(macOS `/Library/Application Support/GeminiCli/`, Linux `/etc/gemini-cli/`) | [3] |
| `~/.gemini/installation_id` | 설치 식별자 | [3] |
| `~/.gemini/oauth_creds.json`, `google_accounts.json`, `mcp-oauth-tokens.json`, `a2a-oauth-tokens.json` | 로그인·연결 정보 | [3] |

로그인·연결 정보 파일은 위치만 기록하고 보고서에서는 값을 가립니다. 일반 원리는 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있고, MCP 서버 설정과 호출 기록은 [MCP 서버와 도구 호출 기록](mcp.md)에서 다룹니다.

**프로젝트 폴더 이름.** 판에 따라 `tmp/` 아래 폴더 이름을 만드는 방식이 다릅니다.

| 방식 | 폴더 이름 | 근거 |
|---|---|---|
| 옛 방식 | 프로젝트 절대 경로의 SHA-256 16진수 64자 | [3][7] |
| 새 방식(`acae712` 소스) | 프로젝트 폴더 이름을 소문자로 바꾸고 영문·숫자 밖의 글자를 `-` 로 바꾼 이름. 이어진 `-` 는 하나로 줄이고 앞뒤 `-` 는 뗌. 겹치면 `-1`, `-2` 를 붙임 | [3] |

새 방식은 처음 실행할 때 옛 해시 폴더(`tmp/`, `history/` 아래)를 새 이름 폴더로 복사하고, 옛 폴더는 지우지 않습니다[3]. 새 이름 폴더에 `.project_root` 말고 다른 파일이 이미 있으면 복사하지 않습니다[3]. 경로와 폴더 이름의 대응은 `projects.json` 에 `{"projects":{"경로":"이름"}}` 형식으로 적습니다[3]. Windows 에서는 이 파일의 경로를 소문자로 바꿔 적습니다[3]. 같은 날짜의 공식 문서는 여전히 `tmp/<project_hash>/chats/` 로 적고 있으므로[1], 문서와 소스가 다르다는 점을 알고 두 모양을 모두 찾습니다.

**세션 파일 형식.** 지금 판은 세션마다 JSON Lines 파일 하나(`.jsonl`)에 기록을 덧붙이고, 옛 판은 JSON 한 덩어리(`.json`)로 저장했습니다[2][7]. 옛 `.json` 세션을 `--resume` 으로 이어 쓰면 같은 이름 끝에 `l` 을 붙인 `.jsonl` 로 전체를 옮겨 적고 이어서 씁니다[2]. 이때 옛 `.json` 은 지우지 않아서[2], 같은 세션이 `.json` 과 `.jsonl` 두 파일로 남을 수 있습니다.

**신뢰 폴더 파일.** 출처끼리 형식이 다릅니다. gemini-cli 소스(`acae712`, 2026-07-17)는 `{"경로":"TRUST_FOLDER"}` 처럼 경로마다 `TRUST_FOLDER`·`TRUST_PARENT`·`DO_NOT_TRUST` 중 하나를 적습니다[6]. agentsview 분석기(2026-09 기준)는 `{"trustedFolders":[…]}` 배열 형식을 읽습니다[7]. 실제 파일을 열어 어느 형식인지 보고 읽습니다.

### 같은 폴더를 쓰는 다른 제품

`~/.gemini` 는 Gemini CLI 만 쓰는 폴더가 아닙니다. Google Antigravity(IDE)의 세션 폴더는 `~/.gemini/antigravity/`, Antigravity CLI 의 폴더는 `~/.gemini/antigravity-cli/` 입니다[8]. IDE 쪽에는 `conversations/<uuid>.db`(세션별 SQLite), `annotations/<uuid>.pbtxt`, `brain/<uuid>/`(평문 계획·작업 문서), `implicit/<uuid>.pb`(암호화)가 있습니다[8]. Antigravity CLI 는 새 판이 세션별 SQLite, 옛 판이 AES 로 암호화한 `.pb` 파일을 쓰고, `history.jsonl` 과 `brain/` 이 함께 있습니다[8]. Google 이 저장 형식을 공개하지 않아서, 이 구조는 역분석으로 알아낸 것입니다(2026-07-19, 2026-09-02 기준)[8]. Antigravity 폴더는 Gemini CLI 와 다른 제품의 흔적으로 나눠 봅니다.

`%USERPROFILE%\.gemini` 에 `tmp/` 없이 `antigravity/` 와 `config/` 만 있는 경우도 있습니다. `antigravity/` 안에는 `antigravity_state.pbtxt`, `installation_id`, `crashes/`, `knowledge/`, `bin/`, `builtin/skills/` 가 들어갑니다. `config/` 안에는 `config.json`, `hooks.json`, `mcp_config.json`, `projects/` 가 들어가고, 이 폴더를 어느 제품이 쓰는지 설명한 공개 문서는 없어서, 실제 기기에서 파일 시각과 함께 쓴 프로그램을 확인해야 합니다. 이처럼 `.gemini` 가 있어도 Gemini CLI 세션은 없을 수 있어서, 폴더가 있다는 사실만으로 Gemini CLI 를 썼다고 쓰지 않습니다.

## 구조

### 세션 파일 이름

새 세션 파일 이름은 `session-` 뒤에 만든 시각과 세션 ID 앞 8자를 붙입니다[2]. 시각은 `toISOString()` 값(UTC)을 분까지 자르고 `:` 를 `-` 로 바꾼 것입니다[2]. 하위 에이전트 세션은 부모 세션 ID 이름의 폴더 안에 `<세션 ID>.jsonl` 로 만듭니다[2].

```
만든 예시
chats/session-2026-08-14T01-37-5f0c2a9e.jsonl
chats/5f0c2a9e-1b2c-4d3e-8f90-a1b2c3d4e5f6/7c1d0e2f-3a4b-4c5d-9e6f-0a1b2c3d4e5f.jsonl
```

### 줄의 종류

`.jsonl` 파일은 한 줄에 JSON 객체 하나이고, 줄은 네 가지입니다[2].

| 줄 | 알아보는 법 | 뜻 |
|---|---|---|
| 첫 메타 줄 | `sessionId` 와 `projectHash` 가 있음 | 세션 시작 정보 |
| 메시지 줄 | `id` 가 있음 | 메시지 하나의 그 시점 전체 내용 |
| 갱신 줄 | `$set` 이 있음 | 메타 정보 바꾸기. `$set.messages` 가 있으면 메시지 목록 전체를 다시 적은 것 |
| 되감기 줄 | `$rewindTo` 가 있음 | 그 메시지 ID 부터 뒤를 대화에서 뺌 |

메타 줄의 키는 아래와 같습니다[2].

| 키 | 뜻 |
|---|---|
| `sessionId` | 세션 UUID |
| `projectHash` | 프로젝트 경로의 SHA-256 16진수. 새 방식 폴더 이름과 상관없이 해시로 적음 |
| `startTime`, `lastUpdated` | 시작·마지막 갱신 시각(ISO 8601 UTC) |
| `kind` | `main` 또는 `subagent` |
| `directories` | `/dir add` 로 더한 작업 폴더 |
| `summary` | 세션 요약(나중에 `$set` 으로 붙음) |
| `memoryScratchpad` | 작업 요약·도구 순서·건드린 경로(`touchedPaths`) 등(`$set` 으로 붙음) |

메시지 줄의 키는 아래와 같습니다[2].

| 키 | 뜻 |
|---|---|
| `id`, `timestamp` | 메시지 ID, 만든 시각(ISO 8601 UTC) |
| `type` | `user`, `gemini`, `info`, `error`, `warning` |
| `content`, `displayContent` | 모델에 보낸 내용과 화면에 보인 내용 |
| `model` | 답한 모델 이름(`gemini` 메시지) |
| `tokens` | `input`, `output`, `cached`, `thoughts`, `tool`, `total` |
| `thoughts[]` | 생각 요약. `subject`, `description`, `timestamp` |
| `toolCalls[]` | `id`, `name`, `args`, `result`, `status`, `timestamp`, `agentId`, `displayName`, `description`, `resultDisplay`, `renderOutputAsMarkdown` |

도구 결과는 `toolCalls[].result[].functionResponse.response.output` 에서 읽습니다[7].

### 같은 메시지가 여러 줄에 남는 이유

기록 코드는 파일을 고쳐 쓰지 않고 줄을 덧붙이기만 합니다[2]. 토큰 수가 뒤늦게 오거나 도구 호출이 더해지면 같은 `id` 의 메시지를 통째로 한 줄 더 적습니다[2]. 그래서 한 파일에 같은 `id` 가 여러 번 나오고, Gemini CLI 와 agentsview 는 뒤에 나온 줄로 앞 줄을 바꿔 읽습니다[2][7]. 다만 agentsview 는 `$rewindTo` 줄을 처리하지 않아서, 되감아 뺀 메시지도 대화에 넣어 보여 줍니다[7]. 되감기(`$rewindTo`)로 뺀 메시지와, 가리기 등으로 내용이 바뀌어 `$set.messages` 로 다시 적기 전의 메시지도 앞쪽 줄에 그대로 남습니다[2]. 되감기 때문에 세션이 갈라질 수도 있고, coding-agent-forensics 는 되감은 턴을 지우지 않고 표시해 보여 줍니다[9].

### 사용자 입력 기록 `logs.json`

프로젝트 폴더의 `logs.json` 은 사용자 입력마다 `sessionId`, `messageId`(세션 안 순번), `timestamp`(ISO 8601 UTC), `type`(`user`), `message` 를 담은 항목의 배열입니다[4]. 세션을 지울 때는 세션 파일, `logs/`, `tool-outputs/`, 세션별 폴더를 지우고 `logs.json` 은 건드리지 않습니다[4].

### 설정 `settings.json`

보관 설정은 `general.sessionRetention` 아래에 있습니다[1][4].

| 키 | 뜻 |
|---|---|
| `general.sessionRetention.enabled` | 자동 정리 사용 여부, 기본 `true` |
| `general.sessionRetention.maxAge` | 보관 기간(`"24h"`, `"7d"`, `"4w"` 같은 형식), 기본 `"30d"` |
| `general.sessionRetention.maxCount` | 남길 세션 수, 기본 제한 없음 |
| `general.sessionRetention.minRetention` | 이 기간보다 새 세션은 지우지 않음, 기본 `"1d"` |
| `model.maxSessionTurns` | 세션 하나에서 주고받을 수 있는 횟수, 기본 `-1`(제한 없음) |

훅은 `hooks` 아래에 사건 이름별 배열로 적고, 각 항목에 `matcher` 와 `hooks` 목록(`type`, `command`, `name`, `timeout`)이 있습니다[5]. 사건 이름은 `SessionStart`, `SessionEnd`, `BeforeAgent`, `AfterAgent`, `BeforeModel`, `AfterModel`, `BeforeToolSelection`, `BeforeTool`, `AfterTool`, `PreCompress`, `Notification` 입니다[5]. 훅의 `command` 가 가리키는 스크립트는 도구 실행 전후에 따로 기록을 남길 수 있어서 열어 봅니다.

## 증거로서 의미

**증명하는 것.** `tmp/` 아래 `chats/` 에 세션이 있으면 그 사용자 계정에서 그 프로젝트를 대상으로 Gemini CLI 와 대화한 기록이 있다는 뜻입니다. `toolCalls[]` 에 `args` 와 `result` 가 있으면 "이 세션에서 에이전트가 이 인자로 이 도구를 실행하고 이 출력을 받은 기록이 있다" 고 쓸 수 있습니다. `projectHash` 와 `.project_root`, `projects.json` 은 세션이 어느 프로젝트 경로에서 일어났는지를 알려 줍니다[2][3]. 되감기 줄 앞에 남은 메시지는 사용자가 되돌린 요청과 답변을 보여 줍니다[2]. `general.sessionRetention` 값은 기록이 얼마나 오래 남도록 설정되어 있었는지를 보여 줍니다.

**증명하지 못하는 것.** 세션이 없다고 쓰지 않았다고 말할 수 없습니다. 기본 30일 정리, 사용자가 줄인 보관 설정, `--delete-session` 으로 지웠을 수 있고, 대화 내용 없이 시작만 한 세션은 스스로 지우기도 합니다[2]. 디스크가 가득 차면 기록을 멈추고 대화는 계속합니다[2]. 세션에 적힌 도구 실행이 실제로 파일을 바꿨는지는 파일 시스템과 git 이력으로 따로 확인하고, 입력한 사람이 누구인지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 좁힙니다. `~/.gemini` 폴더나 그 안의 `antigravity/` 는 다른 Google 도구의 흔적일 수 있습니다[8].

## 시각 해석

세션 파일 안의 시각(`startTime`, `lastUpdated`, `timestamp`, `thoughts[].timestamp`, `toolCalls[].timestamp`)은 모두 `new Date().toISOString()` 으로 만든 UTC 값이고 끝에 `Z` 가 붙습니다[2]. 파일 이름의 시각도 UTC 이고 분까지만 있으며, 세션을 처음 만든 때를 가리킵니다[2]. 메시지를 적을 때마다 `$set` 줄로 `lastUpdated` 를 새로 적으므로, 메타 줄의 `lastUpdated` 가 아니라 파일에서 가장 늦은 `lastUpdated` 가 마지막 활동 시각입니다[2][7].

`--resume` 으로 이어 쓰면 같은 파일에 줄이 붙어서 파일 수정 시각과 `lastUpdated` 가 새로 바뀌고, 파일 이름의 시각은 그대로입니다[2]. 옛 `.json` 을 이어 쓴 경우 새 `.jsonl` 의 파일 만든 시각은 이어 쓴 때이지만 안의 `startTime` 은 원래 세션 시작 시각입니다[2]. 자동 정리는 각 세션의 `lastUpdated` 를 기준으로 오래된 세션을 지웁니다[4]. 그래서 남은 가장 오래된 세션은 "처음 쓴 때" 가 아니라 "정리 기준 안에서 남은 가장 오래된 때" 로 읽습니다. 여러 출처를 한 줄로 맞추는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

- 기본 30일 정리는 정상 동작이라서 오래된 세션이 없다고 조작으로 볼 이유는 없습니다[1]. 다만 사건 무렵에 `maxAge` 나 `maxCount` 를 줄였다면 기록을 일부러 줄였을 수 있으니, `settings.json` 의 수정 시각과 백업·볼륨 섀도 사본의 이전 판을 함께 봅니다. 기록이 스스로 지워지므로 조사 중인 기기는 되도록 빨리, 필요하면 정해진 간격으로 수집합니다[9]. 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.
- 줄 수를 그대로 세면 같은 메시지를 여러 번 세게 됩니다. `id` 로 묶어 마지막 줄만 쓰고, 되감기 앞 줄은 따로 표시합니다.
- 토큰 수를 메시지마다 더하면 부풀 수 있습니다. 일부 기록은 누적값이거나 나눠 받은 값이라서, 입력·캐시 토큰은 앞 메시지와의 차이로 다시 셉니다[7].
- 하위 에이전트 세션은 `chats/` 바로 아래가 아니라 부모 세션 ID 폴더 안에 있습니다[2]. agentsview 는 `chats/session-*` 만 찾으므로[7], 도구 결과만 보면 하위 에이전트 대화가 빠집니다.
- 폴더 이름이 해시인지 이름인지는 판에 따라 다르고, 새 방식으로 바꿀 때 옛 해시 폴더를 복사만 하므로 같은 세션이 두 폴더에 함께 있을 수 있습니다[3]. `tmp/` 아래 폴더를 모두 수집하고 세션 ID 로 중복을 가려냅니다.
- 정리로 지운 세션 파일은 할당되지 않은 영역에 조각으로 남을 수 있습니다. JSON Lines 라서 줄 단위로 되살릴 수 있고, 일반 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 지금 판의 세션 파일은 `JSON.stringify` 로 쓴 메타 줄로 시작하므로 첫 바이트가 `{"sessionId"` 입니다[2]. 옛 `.json` 은 파일 전체가 JSON 객체 하나입니다[7]. 아래는 문자 인코딩대로 만든 예시이고, 실제 데이터에서 뜬 바이트가 아닙니다.

```
만든 예시(인코딩 명세로 만든 바이트)
{"sessionId"   UTF-8  7B 22 73 65 73 73 69 6F 6E 49 64 22
"$rewindTo"    UTF-8  22 24 72 65 77 69 6E 64 54 6F 22
줄 끝                  0A
```

`$rewindTo` 바이트를 찾으면 되감기가 일어난 곳을 바로 짚을 수 있고, 할당되지 않은 영역에서 `{"sessionId"` 를 찾으면 지운 세션의 첫 줄을 찾을 수 있습니다.

**공개 도구로 한 번.** 수집한 사본에서 세션 목록, 되감기, 도구 호출을 봅니다. 경로는 만든 예시이고, 원본이 아니라 사본에서만 돌립니다.

```sh
# 만든 예시 경로
GM=/cases/case-0001/copy/alice/.gemini
# 프로젝트 폴더와 그 폴더가 가리키는 경로
for d in "$GM"/tmp/*/; do printf '%s  ' "$d"; cat "$d/.project_root" 2>/dev/null; echo; done
# 세션 파일(하위 에이전트 포함)과 수정 시각
find "$GM/tmp" -path '*/chats/*' -name '*.json*' -type f -printf '%TY-%Tm-%Td %TH:%TM  %p\n' | sort
# 한 세션의 되감기 줄
jq -c 'select(has("$rewindTo"))' session.jsonl
# 메시지 id 별 마지막 줄만 남겨 도구 호출 보기
jq -sc 'map(select(has("id"))) | group_by(.id) | map(last) | sort_by(.timestamp) | .[]
        | select(.toolCalls) | {timestamp, tools: [.toolCalls[] | {name, args, status}]}' session.jsonl
# 보관 설정과 훅 사건 이름
jq '{retention: .general.sessionRetention, maxSessionTurns: .model.maxSessionTurns, hooks: (.hooks // {} | keys)}' "$GM/settings.json"
```

폴더 이름이 64자 해시이고 `.project_root` 가 없으면, 후보 경로를 SHA-256 으로 계산해 폴더 이름이나 메타 줄의 `projectHash` 와 맞춰 봅니다[2][3]. 아래 경로는 만든 예시이고, Windows 는 대소문자가 다르면 값이 달라지므로 원래 표기와 소문자 표기를 모두 계산합니다.

```sh
printf '%s' 'C:\Users\alice\src\sample-app' | sha256sum
```

agentsview 는 Gemini CLI 의 `.json`·`.jsonl` 세션을 모두 읽고 `projects.json`·`trustedFolders.json` 으로 폴더 이름을 프로젝트에 이어 줍니다(2026-09 저장소 기준)[7]. coding-agent-forensics 는 브라우저에서 파일을 읽어 되감은 턴을 표시합니다[9]. 두 도구 모두 지금 판과 다를 수 있으니 결과를 원본 줄과 맞춰 봅니다.

## 교차 검증

세션에 적힌 도구 실행은 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)의 흐름으로 셸 기록·git 이력과 맞춰 보고, 외부 문서가 에이전트 동작을 부추긴 정황이 있으면 [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md)으로 이어 갑니다. 같은 PC 에 [Codex CLI](codex-cli.md)나 [Claude Code](claude-code/index.md)가 있으면 훅 설정과 스크립트가 어느 도구 것인지 먼저 나눕니다. 자격 증명 파일을 건드린 도구 호출이 있으면 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md)로 이어 갑니다. 서비스 접속은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)과, 회사가 허용한 도구인지는 [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md)와 함께 봅니다. 수집 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다.

## 실습

Gemini CLI 흔적이 든 공개 시험 이미지가 없으므로, 시험용 가상 머신과 시험 계정으로 풀어 봅니다.

1. 서로 다른 프로젝트 폴더 두 곳에서 대화한 뒤 `tmp/` 아래 폴더 이름이 해시인지 이름인지, `projects.json` 과 `.project_root` 에 무엇이 적혔는지 봅니다.
2. 파일을 읽는 요청을 한 번 넣고, 같은 `id` 의 메시지 줄이 몇 번 적히는지와 `toolCalls[].result` 모양을 확인합니다.
3. 대화를 되감은 뒤 `$rewindTo` 줄 앞에 되돌린 메시지가 남았는지 확인합니다.
4. `general.sessionRetention.maxAge` 를 `"24h"` 로 줄이고 이틀 뒤 다시 실행해, 사라진 파일과 남은 `logs.json` 항목을 비교합니다.
5. `--resume` 으로 지난 세션을 이어 쓴 뒤 파일 이름의 시각, 파일 수정 시각, 마지막 `lastUpdated` 를 비교합니다.

## 참고 문헌

1. google-gemini/gemini-cli — `docs/cli/session-management.md` (커밋 acae7124bdd849e554eaa5e090199a0cf08cd782) — https://github.com/google-gemini/gemini-cli/blob/acae7124bdd849e554eaa5e090199a0cf08cd782/docs/cli/session-management.md
2. google-gemini/gemini-cli — `packages/core/src/services/chatRecordingService.ts`, `packages/core/src/services/chatRecordingTypes.ts`, `packages/core/src/utils/thoughtUtils.ts` (커밋 acae712) — https://github.com/google-gemini/gemini-cli/tree/acae7124bdd849e554eaa5e090199a0cf08cd782/packages/core/src
3. google-gemini/gemini-cli — `packages/core/src/config/storage.ts`, `packages/core/src/config/storageMigration.ts`, `packages/core/src/config/projectRegistry.ts`, `packages/core/src/utils/paths.ts` (커밋 acae712) — https://github.com/google-gemini/gemini-cli/tree/acae7124bdd849e554eaa5e090199a0cf08cd782/packages/core/src
4. google-gemini/gemini-cli — `packages/core/src/utils/sessionOperations.ts`, `packages/core/src/core/logger.ts`, `packages/cli/src/utils/sessionCleanup.ts` (커밋 acae712) — https://github.com/google-gemini/gemini-cli/tree/acae7124bdd849e554eaa5e090199a0cf08cd782/packages
5. google-gemini/gemini-cli — `docs/hooks/index.md` (커밋 acae712) — https://github.com/google-gemini/gemini-cli/blob/acae7124bdd849e554eaa5e090199a0cf08cd782/docs/hooks/index.md
6. google-gemini/gemini-cli — `packages/core/src/utils/trust.ts` (커밋 acae712) — https://github.com/google-gemini/gemini-cli/blob/acae7124bdd849e554eaa5e090199a0cf08cd782/packages/core/src/utils/trust.ts
7. kenn-io/agentsview — `internal/parser/gemini.go`, `internal/parser/gemini_provider.go`, `internal/parser/discovery.go`, `docs/internal/session-format-sources.md`(2026-09-11) — https://github.com/kenn-io/agentsview
8. kenn-io/agentsview — `README.md`(Supported Agents 표, Antigravity CLI 절), `internal/parser/antigravity.go`, `internal/parser/antigravity_crypto.go`, `docs/internal/session-format-sources.md` — https://github.com/kenn-io/agentsview
9. Shorton88/coding-agent-forensics — `README.md` — https://github.com/Shorton88/coding-agent-forensics
