---
title: "AI 에이전트 브라우저"
parent: "아티팩트 · 에이전트형 서비스"
nav_order: 430
---

# AI 에이전트 브라우저 (Comet·Fellou 등)

AI 에이전트 브라우저 (AI agent browser) 는 AI 에이전트를 브라우저 안에 넣어 사용자 대신 검색하고 페이지를 조작하는 브라우저이고, 제품마다 대화 본문을 기기에 캐시하는지 서버에만 두는지가 달라서 어디까지 기기에서 복구되는지가 먼저 갈립니다.

이 쪽의 경로와 칸 이름은 AABF v1.1.260618 기준이고, 브라우저 판이 바뀌면 경로가 달라질 수 있습니다[1].

## 무엇을 기록하나 · 왜 생기나

AABF 는 여섯 브라우저를 다룹니다. Perplexity Comet, Fellou, Microsoft Edge(Copilot), BrowserOS, Sigma Browser, Genspark Browser 입니다[1]. 도구는 흔적을 계정(Account), 프롬프트(Prompt), 작업 흐름(Workflow), 결과(Output) 네 갈래로 나누고, 서버 접속에 쓰는 인증(Authentication) 흔적을 따로 셉니다. 작업 흐름은 에이전트가 세운 계획, 검색어, 부른 도구와 그 입력·출력 같은 중간 단계를 말합니다.

도구는 각 브라우저를 서비스 형태로도 나눕니다. 대화 본문을 기기에 남기는 쪽(local-centric)은 Comet 과 BrowserOS, 계정·토큰만 기기에 남기고 본문은 서버에 두는 쪽(cloud-centric)은 Fellou, Edge, Genspark, 둘이 섞인 쪽(hybrid)은 Sigma 입니다[1]. 이 구분이 조사 방향을 정합니다. 기기 쪽이면 프로필 폴더를 떠서 캐시를 읽고, 서버 쪽이면 기기에서는 누가 언제 썼는지까지만 잡고 본문은 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 받습니다.

이 브라우저들은 대부분 Chromium 을 바탕으로 만들었고 Fellou 만 Electron 입니다[1]. 그래서 방문 기록·쿠키 같은 일반 흔적은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)(Windows 판)와 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md) 방식대로 읽고, 이 쪽은 에이전트 기능이 더하는 흔적만 다룹니다. 일반 브라우저에 확장으로 붙는 에이전트(Claude in Chrome 등)는 [브라우저를 조작하는 AI](browser-agents.md)에 있습니다.

## 위치와 버전별 차이

아래 경로에서 `%LOCALAPPDATA%` 는 `...\AppData\Local`, `%APPDATA%` 는 `...\AppData\Roaming` 이고, `{profile}` 은 `Default`, `Profile 1` 같은 프로필 폴더 자리입니다. 모두 AABF `aabf/signatures.py` 에서 옮겼습니다[1].

| 브라우저 | 바탕 | 서비스 형태 | 사용자 데이터 폴더 |
|---|---|---|---|
| Comet (Perplexity AI) | Chromium | 기기 중심 | `%LOCALAPPDATA%\Perplexity\Comet\UserData` |
| Fellou (ASI X) | Electron | 서버 중심 | `%APPDATA%\Fellou` |
| Microsoft Edge (Copilot) | Chromium | 서버 중심 | `%LOCALAPPDATA%\Microsoft\Edge\User Data` |
| BrowserOS | Chromium | 기기 중심 | `%LOCALAPPDATA%\BrowserOS\BrowserOS\User Data` |
| Sigma Browser | Chromium | 섞임 | `%LOCALAPPDATA%\Chromium\UserData` |
| Genspark Browser (MainFunc) | Chromium | 서버 중심 | `%LOCALAPPDATA%\GensparkSoftware\Genspark-Browser\UserData` |

출처끼리 다른 경로가 하나 있습니다. BrowserOS 는 AABF 주석에 따르면 논문 표에는 `UserData`, `BrowserOS\UserData` 로 적혀 있었고, AABF 가 실제 설치본과 맞춰 `BrowserOS\BrowserOS\User Data` 로 고쳤습니다(2026-06 코드 기준)[1]. 검체에서는 두 모양을 모두 찾아봅니다.

### Comet

| 위치 (`UserData\{profile}\` 아래) | 담긴 것 |
|---|---|
| `Local Storage\leveldb` | 키 `pplx-next-auth-session`(이메일·이름·사용자명·UUID·만료 시각이 평문), `comet-sidecar-threads-by-id`(대화 URL 과 갱신 시각), `pplx-top-sites-cache`(방문 사이트) |
| `IndexedDB\https_www.perplexity.ai_0.indexeddb.leveldb` | 서버 응답 캐시. 대화 목록, 프롬프트, 작업 흐름, 답변 |
| `Network\Cookies` | 세션 쿠키 `__Secure-next-auth.session-token`(JWE) |
| `Local State` (프로필 폴더가 아니라 `UserData` 바로 아래) | 쿠키를 푸는 키 `os_crypt.encrypted_key`(DPAPI 로 감쌈) |

Local Storage 에는 로그인하지 않아도 남는 흔적도 있습니다. AABF 는 `pplx-top-sites-cache`(방문한 사이트의 주소·제목·방문 횟수), 이름이 `web_url` 이나 `first_page_visit_url` 로 끝나는 키(이동한 주소), `cometOnboardingStep`(첫 설정 단계), `locationMetadata`(위치 권한 상태와 갱신 시각)를 이런 흔적으로 따로 읽습니다[1].

### Fellou

| 위치 (`%APPDATA%\Fellou\` 아래) | 담긴 것 |
|---|---|
| `FellouUserData\` 의 `user.json`, `currentUser.json`, `metaInfo.json`, `metadata.json` | 사용자 ID, 프로필 ID, 만든 시각, 마지막 로그인, 지금 쓰는 사용자 |
| `FellouUserData\{folder16}\profiles\{profile}\sqliteDatabase.db` | 앱 상태 표 `key_value_store`·`redux_store`, 방문 기록 표 `history`, 사이트 권한 표 `permission` |
| `Partitions\shared-process\Local Storage\leveldb` | 계정 정보(이름·이메일·전화번호·만든 시각)와 로그인 토큰 |
| `Partitions\profile-{profile}\Local Storage\leveldb` | `fellou.id_token` 과 관련 토큰 |

`{folder16}` 은 AABF 가 이 자리의 폴더를 부르는 이름이고, 실제 이름은 검체에서 봅니다. AABF 는 에이전트의 작업 흐름 본문이 `sqliteDatabase.db` 에 없고 서버에만 있다고 적습니다[1].

### Microsoft Edge (Copilot)

| 위치 (`User Data\{profile}\` 아래) | 담긴 것 |
|---|---|
| `Local Storage\leveldb` (출처 `https://copilot.microsoft.com`) | MSAL 캐시. 키 `msal.2.account.keys`, `msal.2\|...` 로 시작하는 계정·토큰 항목, `token.keys` |
| `Local State` (프로필 폴더가 아니라 `User Data` 바로 아래) | `os_crypt.encrypted_key` |

토큰 본문(`data`)은 DPAPI 로 암호화돼 있고, 키 이름에서 테넌트·클라이언트 ID 와 범위(scope)를, `lastUpdatedAt` 에서 세션 시각을 읽습니다[1]. Edge 는 Windows 에 기본으로 깔려 있어서 폴더가 있다는 것만으로는 Copilot 을 썼다는 근거가 되지 않고, `msal.2.*` 키가 있는지를 봐야 합니다. Edge 의 Copilot 옆 패널과 정책 설정은 [브라우저에 들어간 AI](../office-integrations/browser-builtin-ai.md)에 있습니다.

### BrowserOS

BrowserOS 는 에이전트가 고정 ID `bflpfmnmnokmjhmgnolecpppdbdophmk` 인 내장 확장이고, 따로 로그인하는 기능이 없어 계정 흔적은 없습니다[1].

| 위치 | 담긴 것 |
|---|---|
| `User Data\{profile}\Local Extension Settings\bflpfmnmnokmjhmgnolecpppdbdophmk` | 대화 UUID, `lastMessagedAt`, 프롬프트, 도구 호출 입력·출력, 답변 |
| `User Data\{profile}\IndexedDB\chrome-extension_bflpfmnmnokmjhmgnolecpppdbdophmk_0.indexeddb.leveldb` | 확장의 IndexedDB 저장소 |
| `User Data\.browseros\browseros-server.log`, `browseros-server.log.old` | 로컬 제어 서버 로그. 시작, 도구 로딩, 대화별 conversationId 와 모델, 요청부터 끝까지의 처리 흐름(시각 포함) |
| `User Data\.browseros\browseros.db` (`-wal`, `-shm` 포함) | 로컬 제어 서버의 에이전트 상태 DB |
| `%LOCALAPPDATA%\Temp\gemini-client-error-*.json` | 모델 호출이 실패했을 때 남는 대화 맥락과 함수 호출 순서 |
| `User Data\{profile}\Network\Cookies`, `Login Data` | 세션 쿠키 `__Secure-better-auth.session_token`, Google 로그인 세션, 기기 식별자 |

BrowserOS 는 에이전트를 움직이는 로컬 제어 서버를 루프백(127.0.0.1)에 띄웁니다[1]. 이 통신은 기기 밖으로 나가지 않으므로 프록시 기록에는 남지 않습니다.

### Sigma Browser

Sigma 도 에이전트가 고정 ID `amabiocpfnlgbceffljgkcjeacejflga` 인 내장 확장입니다[1].

| 위치 (`Chromium\UserData\{profile}\` 아래) | 담긴 것 |
|---|---|
| `Local Storage\leveldb` 키 `search-storage` (출처 `https://app.sigmabrowser.com`) | 계정(`state.user`), 토큰, 작업 기록 `state.userHistory[]`, 답변 요약 |
| `Local Extension Settings\amabiocpfnlgbceffljgkcjeacejflga` | `userId`, `socketAuth`(세션 ID·토큰), 입력 칸에 친 글, `lastVisitedPath`, `activeTarget_` 로 시작하는 키 |
| `Network\Cookies` | 인증 토큰 |

에이전트가 단계별로 생각한 과정은 기기에 남지 않고 서버에만 있습니다[1].

### Genspark Browser

| 위치 (`UserData\{profile}\` 아래) | 담긴 것 |
|---|---|
| `Network\Cookies` | `session_id`(인증 토큰), `ai_user`(사용자 ID 와 처음 발급 시각), `ai_session`(세션 시각) |
| `Login Data` | 계정 이메일 |
| `IndexedDB\https_*.indexeddb.leveldb` | 다시 발급받는 데 쓰는 인증 토큰 |

대화 본문은 모두 서버에 있습니다[1].

## 구조

저장 형식 자체는 기반 구조 쪽에 있습니다. Local Storage·IndexedDB·확장 저장소는 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html), `Cookies`·`Login Data`·`sqliteDatabase.db` 는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html)(둘 다 Windows 판) 방식으로 읽습니다. 아래는 AABF 파서가 읽는 값의 짜임입니다.

### Comet 의 IndexedDB 캐시

Comet 캐시는 `keyval` 저장소에 있고, 키는 `["pplx-query-cache-버전", 캐시 종류, 대화 slug 나 UUID, ...]` 모양의 배열입니다(`aabf/parsing/services/comet.py`)[1]. 두 번째 칸이 캐시 종류이고 AABF 는 네 가지를 읽습니다.

| 캐시 종류 | 담긴 것 | 주요 칸 |
|---|---|---|
| `all_results` | 대화 본문 전체. 단계 항목의 목록 | `backend_uuid`, `thread_url_slug`, `context_uuid`, `query_str`(프롬프트), `thread_title`, `display_model`, `mode`, `author_id`, `author_username`, `entry_created_datetime`, `blocks[]`, `featured_images`, `attachments` |
| `/rest/thread/list_recent` | 최근 대화 목록. 제목이 곧 프롬프트 | `uuid`, `slug`, `title`, `task_description`, `query_str`, `status`, `last_query_datetime`, `answer_preview` |
| `/rest/thread/list_ask_threads` | 대화 목록(`pages[]` 아래) | 위와 같음, 그리고 `source` |
| `thread_metadata` | 제목과 시각 | `title`, `thread_status`, `created_at`, `updated_at` |

`blocks[]` 안에서 `markdown_block.answer` 가 답변이고, `plan_block.goals[].description` 이 에이전트가 세운 계획입니다. `workflow_block.steps[]` 는 단계마다 `title`, `status`, `items[]` 를 담고, 항목 `type` 이 `WORKFLOW_ITEM_QUERIES` 면 검색어(`payload.queries_payload.queries`), `WORKFLOW_ITEM_SOURCES` 면 참고한 주소(`payload.sources_payload.sources[].url`)입니다.

`source` 칸은 대화가 어디서 시작됐는지 알려 줍니다. AABF 는 값이 `entropy` 면 에이전트 대화로, `default`(일반 Perplexity 검색)와 `youtube`(위젯)는 에이전트 대화가 아닌 것으로 봅니다[1]. 캐시 항목에는 `expiry_time` 이 붙어 있고 AABF 는 이 값이 약 30일이라 오래된 대화는 캐시에서 빠질 수 있다고 적습니다.

### BrowserOS 의 확장 저장소

확장 저장소(`chrome.storage.local`)의 `conversations` 키에 대화 목록이 JSON 으로 들어 있습니다(`aabf/parsing/services/browseros.py`)[1]. 대화마다 `id`, `lastMessagedAt`, `messages[]` 가 있고, 메시지마다 `id`, `role`, `parts[]` 가 있습니다. `role` 이 `user` 면 프롬프트, `assistant` 면 답변입니다. `parts[]` 에서 `type` 이 `text` 인 조각은 글이고, `tool-` 로 시작하는 조각은 도구 호출 하나이며 `input`, `output`, `state`, `toolCallId` 칸이 있습니다. 도구 이름은 `type` 에서 `tool-` 를 뗀 나머지입니다.

같은 저장소에는 대화가 없어도 남는 설정이 있습니다. `scheduledJobRuns`(예약 작업의 `id`, `name`, `status`, `nextRunAt`, `lastRunAt`, `prompt` 또는 `goal`), `llm-providers`(`modelId`, `type`, `baseUrl`, `contextWindow`, `createdAt`), `mcpServers`(`name`, `url`), `sessionInfo` 입니다. 예약 작업의 프롬프트는 사용자가 무엇을 시키려 했는지 보여 주고, `baseUrl` 은 어느 모델 서버 주소를 설정했는지 보여 줍니다. MCP 설정 읽는 법은 [MCP 서버와 도구 호출 기록](../dev-agents/mcp.md)에 있습니다.

### Sigma 의 `search-storage`

`search-storage` 값은 JSON 이고 `state` 아래에 칸이 모여 있습니다(`aabf/parsing/services/sigma.py`)[1].

| 칸 | 담긴 것 |
|---|---|
| `state.user` | `user_id`, `email`, `username`, `created_at`, `last_login_at`, `subscription` |
| `state.access_token`, `refresh_token`, `session_id`, `is_log_in` | 인증 정보 |
| `state.userHistory[]` | `id` 또는 `api_thread_id`, `query`(프롬프트), `hash`, `created_at`, `updated_at`, `session_id`, `thread_name`, `thread_type`, `summary`(답변 요약) |
| `state.userPrompts[]` | 판에 따라 프롬프트를 여기에 두기도 함. 항목이 객체일 수도 문자열일 수도 있음 |

확장 저장소 쪽 `inputSearchPage:` 와 `inputMainPage` 로 시작하는 키에는 AABF 설명으로 사용자가 입력 칸에 친 원래 글이 들어갑니다[1]. 이 값을 `userHistory` 의 `query` 와 맞춰 보면 입력 칸에 남은 글이 실제로 보낸 프롬프트와 같은지 볼 수 있습니다.

### Fellou 의 Local Storage 와 SQLite

Local Storage 에서 AABF 가 읽는 키는 여섯 가지입니다(`aabf/parsing/services/fellou.py`)[1]. `fellou.userInfo`(`id`, `email`, `phone_number`, `createdAt`, `authing_user_id`, `isAdmin`), `_authing_user`(`id`, `username`, `email`, `phone`), 토큰 `fellou.id_token`·`fellou.access_token`·`_authing_token`, 이용량 `userPoint`(`availablePoint`, `usedPoint`, `monthlyPoint`)입니다. `fellou.id_token` 은 Authing 이 발급한 JWT 이고, AABF 는 유효 기간이 발급 뒤 약 10년이라고 적습니다.

`sqliteDatabase.db` 의 `key_value_store` 표에서는 키 `fellou.tabRestore` 가 중요합니다. 값은 JSON 이고 `records[]` 마다 되살릴 탭의 `url`, `title`, `id` 가 있어서, 에이전트가 만든 보고서·작업 화면의 주소와 제목(작업 주제)이 남습니다. 주소가 `agent.fellou.ai/report/`, `/container/`, `/task/`, `/chat/`, `/session/` 뒤에 UUID 가 붙는 모양이면 AABF 는 그 UUID 를 에이전트 세션 ID 로 읽습니다. `history` 표에서는 `url`, `title`, `lastVisitTime` 또는 `visitTime`, `visitCount` 를, `permission` 표에서는 `url`, `domain`, `permission`, `visitTime` 을 읽습니다. AABF 목록은 이 방문 기록에 AI 방문인지 사람 방문인지 가리는 표시가 있다고 적는데, 파서 코드에는 그 칸 이름이 나오지 않으므로 검체의 `history` 표 칸을 직접 보고 확인합니다.

### Genspark 쿠키 값

AABF 주석에 따르면 `session_id` 값은 `UUID:16진수 토큰`, `ai_user` 는 `ID|ISO 시각`, `ai_session` 은 `ID|시각|시각` 모양입니다(`aabf/parsing/services/genspark.py`)[1]. `ai_user` 의 시각은 처음 발급된 때라서 이 계정을 이 브라우저에서 처음 쓴 시점의 단서가 됩니다.

## 증거로서 의미

**증명하는 것.** 사용자 데이터 폴더는 그 브라우저가 설치돼 실행된 흔적입니다. BrowserOS·Sigma 의 고정 확장 ID 저장소는 AABF 설명으로 에이전트를 쓴 뒤에야 생기므로, 에이전트를 한 번 이상 썼다는 흔적이 됩니다. AABF 는 이 저장소를 브라우저를 가려낼 때 보조 표시로 씁니다[1]. 계정 키(`pplx-next-auth-session`, `fellou.userInfo`, `search-storage` 의 `state.user`)는 이 프로필에 로그인한 계정을 알려 주고, Comet `all_results` 의 `author_id`·`author_username` 은 대화마다 어느 계정이 썼는지를 잇습니다. 기기 중심인 Comet·BrowserOS 에서는 프롬프트와 답변, 에이전트가 거친 단계까지 기기에서 읽을 수 있습니다.

**증명하지 못하는 것.** 계정이 남아 있다고 해서 그 시각에 키보드 앞에 있던 사람이 계정 주인이라는 뜻은 아니고, 이 문제는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)에서 다룹니다. 서버 중심인 Fellou·Edge·Genspark 는 기기에 본문이 없어서, 기기만으로는 무엇을 시켰는지 말할 수 없습니다. Comet 캐시는 약 30일 뒤 밀려나므로 캐시에 없다고 해서 그 대화가 없었다는 뜻도 아닙니다. 에이전트가 페이지를 열고 눌렀다는 기록이 있어도, 그 결과 외부 사이트에서 실제로 무엇이 바뀌었는지는 그 사이트 쪽 기록으로 확인해야 합니다.

보고서에는 "Comet 프로필의 캐시에 이 계정 이름으로 이런 프롬프트와 에이전트 단계가 남아 있고 캐시 항목 시각은 이렇다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

한 브라우저 안에서도 시각 형식이 섞여 있습니다. AABF `aabf/analysis/timestamps.py` 는 네 형식을 구분합니다[1].

| 형식 | 예로 든 칸 |
|---|---|
| ISO-8601 문자열 | Comet `entry_created_datetime`, Sigma `created_at` |
| 유닉스 밀리초 | BrowserOS `lastMessagedAt`, Comet Local Storage `updatedAt` |
| 유닉스 초 | Comet `perplexity_last_event_timestamp` |
| 1601-01-01 부터 마이크로초(WebKit) | SQLite 의 `creation_utc` 같은 칸 |

AABF 는 숫자의 크기로 형식을 고릅니다. 10^15 이상이면 WebKit 마이크로초, 10^11 이상이면 밀리초, 그보다 작으면 초로 봅니다. 시간대 표시가 없는 문자열은 UTC 로 가정하는데, 도구가 정한 가정이라 검체에서 다른 기록과 맞춰 봐야 합니다. Fellou `fellou.tabRestore` 의 탭 `id` 는 `1700000000000-0` 처럼(만든 예시) 앞부분이 유닉스 밀리초이고, AABF 는 이 앞부분을 탭 시각으로 읽습니다.

시각이 무엇을 뜻하는지도 칸마다 다릅니다. BrowserOS `lastMessagedAt` 은 대화의 마지막 메시지 시각이라서, AABF 는 한 대화의 모든 메시지에 이 값 하나를 붙입니다. 메시지마다 언제 보냈는지는 이 값으로 알 수 없고, 로컬 제어 서버 로그(`browseros-server.log`)의 시각과 맞춰 봐야 합니다. `pplx-next-auth-session` 의 시각은 세션 만료 시각이지 로그인 시각이 아닙니다. 여러 기록을 한 줄로 늘어놓는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

- **폴더 이름이 겹치는 경우.** Sigma 폴더는 `%LOCALAPPDATA%\Chromium\UserData` 라서 이름만으로 Sigma 라고 단정하지 않고, 확장 ID `amabiocpfnlgbceffljgkcjeacejflga` 폴더나 `search-storage` 키가 있는지 함께 봅니다. Edge 폴더는 거의 모든 Windows 에 있으므로 `msal.2.*` 키로 Copilot 사용을 따로 확인합니다.
- **Comet 의 에이전트 대화와 일반 검색이 섞임.** 같은 캐시에 일반 Perplexity 검색이 함께 들어 있습니다. `source` 칸이 있으면 `entropy` 만 에이전트 대화이고, 칸이 없는 캐시(`list_recent` 만 있는 경우)는 AABF 가 모두 에이전트 대화로 둡니다[1]. 이 경우 일반 검색이 섞였을 수 있다는 점을 보고서에 적습니다.
- **같은 대화가 여러 번 나옴.** Comet 은 같은 대화 본문을 캐시 판(`pplx-query-cache-버전`)마다 따로 두므로 AABF 는 중복을 걷어 냅니다[1]. 손으로 셀 때도 대화 ID 로 묶어서 셉니다.
- **IndexedDB 의 `.blob` 폴더.** IndexedDB 는 큰 값을 `이름.indexeddb.leveldb` 옆의 `이름.indexeddb.blob` 폴더에 따로 둡니다. AABF 는 이 폴더를 함께 수집하지 않으면 대화 본문처럼 큰 값을 가리키는 레코드가 조용히 빠진다고 적습니다(`aabf/collection/local.py`)[1]. 수집할 때 두 폴더를 함께 뜹니다.
- **Genspark 쿠키가 평문인지.** AABF 안에서도 적힌 내용이 다릅니다. `signatures.py` 의 설명은 `session_id`·`ai_user`·`ai_session` 이 평문이라고 적고, 같은 파일의 항목 표시와 `genspark.py` 주석은 보통 `encrypted_value` 칸에 DPAPI·AES-GCM 으로 암호화돼 있다고 적습니다(둘 다 2026-06 코드)[1]. 검체의 `cookies` 표에서 `value` 와 `encrypted_value` 중 어느 칸이 차 있는지 봅니다.
- **암호화된 쿠키.** Chromium 쿠키의 `v10` 형식은 `Local State` 의 키와 같은 사용자의 DPAPI 로 풀리지만, AABF README 는 App-Bound(`v20`) 쿠키 암호화를 다루지 않는다고 적습니다[1]. DPAPI 구조는 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html)(Windows 판)에 있습니다.
- **토큰은 가립니다.** `pplx-next-auth-session`, `fellou.id_token`, `search-storage` 의 `access_token`·`refresh_token`, 쿠키의 세션 값은 모두 계정 접근에 쓰이는 값입니다. `fellou.id_token` 은 JWT 라서 가운데 조각을 base64url 로 풀면 사용자 ID·이름·이메일이 보이지만 서명된 것이지 암호화된 것은 아닙니다[1]. 보고서에는 토큰이 어느 파일의 어느 키에 있었는지만 쓰고 값은 가립니다. 토큰이 남는 곳의 일반론은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md), 서버 쪽 대화는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 안내합니다.
- **도구의 범위.** AABF 는 디스크 흔적만 다루고 메모리는 다루지 않습니다[1]. 실행 중인 브라우저의 프로필을 읽거나 DPAPI 값을 풀려면 관리자 권한이 필요하다고 README 가 적습니다. 실행 중인 브라우저가 `Cookies` 를 잡고 있으면 그 파일만 복사에 실패하고, AABF 는 나머지 파일은 계속 복사합니다(`aabf/collection/local.py`)[1].

## 직접 분석해 보기

**헥스로.** 저장소 폴더의 `.log`·`.ldb` 파일에서 키 이름을 바이트로 찾아 위치를 잡아 봅니다. 예를 들어 `fellou.id_token` 은 ASCII 로 아래와 같습니다(명세로 만든 예시).

```
66 65 6C 6C 6F 75 2E 69 64 5F 74 6F 6B 65 6E   fellou.id_token
```

같은 방식으로 `pplx-next-auth-session`, `search-storage`, `conversations` 를 찾습니다. 바이트로 찾아지지 않아도 없는 것으로 보지 않고, LevelDB 를 읽는 도구로 한 번 더 읽습니다. 읽는 법은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html)(Windows 판)에 있습니다.

**공개 도구로.** AABF[1] 는 Python 3.10 이상에서 돌고 `ccl_chromium_reader` 로 LevelDB·IndexedDB 를 읽습니다. 떠 온 이미지 파일(`.E01` 등), 마운트한 드라이브, 사용자 `AppData` 폴더를 대상으로 줄 수 있습니다.

```powershell
aabf identify "E:\cases\disk0.E01"          # 어떤 브라우저가 있는지 확인만
aabf collect  "E:\cases\disk0.E01" -O evidence   # 기기 흔적 수집
```

`aabf collect` 는 원래 경로 모양을 살려 파일을 복사하고, 파일마다 SHA-256 을 `manifest.json` 에 적습니다(README, `aabf/collection/local.py`)[1]. 결과를 읽을 때는 도구가 판정한 "에이전트 대화" 가 위 함정 절의 규칙(`source` 칸, 중복 제거)을 거친 것이라는 점을 기억하고, 중요한 레코드는 원래 LevelDB 에서 한 번 더 확인합니다. 서버에만 있는 대화는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 받습니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 같은 프로필의 방문 기록·다운로드 | 에이전트가 연 사이트와 받은 파일(사람 방문과 섞임) | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html) |
| 프록시·DNS 기록 | `perplexity.ai`, `agent.fellou.ai`, `app.sigmabrowser.com`, `copilot.microsoft.com` 접속 시간대 | [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) |
| Perplexity 계정 | Comet 이 아닌 웹·앱에서 한 같은 계정의 대화 | [Perplexity](../chat-services/perplexity.md) |
| BrowserOS 제어 서버 로그 | 대화별 시작·끝 시각과 모델 | 이 쪽 BrowserOS 절 |
| 서버 쪽 대화 기록 | 서버 중심 브라우저의 프롬프트·작업 흐름 원본 | [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) |

에이전트가 한 일 전체를 짜 맞추는 절차는 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md), 에이전트가 로그인 정보를 건드렸는지는 [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md)에 있습니다.

## 실습

조사용 계정과 가상 머신(Windows 11)으로 시험 환경을 만들어 아래 질문을 풀어 봅니다.

1. Comet 에서 에이전트에게 작업 하나를 시키고 일반 검색도 한 번 한 뒤, IndexedDB 캐시에서 두 대화의 `source` 값을 비교합니다.
2. BrowserOS 에서 도구를 두 번 이상 부르는 작업을 시킨 뒤, `conversations` 의 `tool-` 조각 순서와 `browseros-server.log` 의 기록 순서를 맞춰 봅니다.
3. Sigma 입력 칸에 글을 치고 보내지 않은 채 브라우저를 닫은 뒤, `inputMainPage` 키와 `userHistory` 에 무엇이 남는지 봅니다.
4. Fellou 에서 에이전트 작업을 하나 한 뒤 `fellou.tabRestore` 의 탭 `id` 앞부분 시각과 `history` 표의 방문 시각을 비교합니다.
5. Genspark `cookies` 표에서 `session_id` 가 `value` 칸에 있는지 `encrypted_value` 칸에 있는지 확인하고, 설치한 판 번호와 함께 적습니다.

## 참고 문헌

1. seturi, AI-Agent-Browser-Forensics (AABF) v1.1.260618, MIT — https://github.com/seturi/AI-Agent-Browser-Forensics. 읽은 파일: `README.md`, `pyproject.toml`, `aabf/__init__.py`, `aabf/models.py`, `aabf/paths.py`, `aabf/signatures.py`, `aabf/identification/identify.py`, `aabf/collection/local.py`, `aabf/cli.py`, `aabf/analysis/timestamps.py`, `aabf/parsing/services/comet.py`, `fellou.py`, `edge.py`, `browseros.py`, `sigma.py`, `genspark.py` (2026-09-25 열람). `aabf/__init__.py` 는 논문 "I Know What You Prompted Last Session: Forensic Analysis of AI Agent Browsers" 의 틀을 구현한다고 적지만, 저자와 게재 정보는 저장소에 없습니다.
