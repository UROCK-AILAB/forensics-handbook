---
title: "AnythingLLM"
parent: "아티팩트 · 로컬 AI"
nav_order: 740
---

# AnythingLLM (AnythingLLM)

AnythingLLM 데스크톱 앱은 대화·워크스페이스·이벤트 기록을 `%APPDATA%\anythingllm-desktop\storage\anythingllm.db` 한 SQLite 파일에 두고, 올린 문서에서 뽑은 본문은 같은 `storage` 폴더 아래 JSON 파일로 따로 둡니다.

이 쪽의 경로·표·칸은 Windows 10 에서 쓴 AnythingLLM 데스크톱 앱 자료 기준이고, 다른 판은 저장 구조가 다를 수 있습니다[1].

## 무엇을 기록하나 · 왜 생기나

AnythingLLM 은 대화를 워크스페이스(workspace) 단위로 묶고, 워크스페이스 안에서 다시 스레드(thread)로 나눕니다. 사용자가 질문을 보내면 앱은 질문과 답을 한 행으로 DB 에 적고, 답에는 쓴 모델·공급자·토큰 수와 참고한 문서 조각을 JSON 으로 함께 넣습니다[4]. 그래서 대화 본문뿐만 아니라 그 답이 어느 문서를 근거로 나왔는지까지 한 행에서 읽을 수 있습니다.

문서를 올리면 앱은 파일을 처리해 본문 글을 뽑고, 그 결과를 JSON 파일로 저장합니다. 이 JSON 의 `pageContent` 칸에는 올린 문서의 본문이 글 그대로 통째로 들어 있습니다[1][4]. 원래 파일을 지웠더라도 앱 저장소에 본문이 남는다는 뜻이라서, 기밀 자료를 넣었는지 묻는 조사([기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md))에서 먼저 볼 곳입니다. 프롬프트·첨부·생성물을 나눠 보는 기준은 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)를 따릅니다.

답을 낸 공급자와 모델은 답 JSON 의 `metrics` 에 남고, 샘플의 `metrics.provider` 칸은 `GenericOpenAiLLM` 이었습니다[4]. 공급자가 원격 서버라면 질문이 그 서버로도 나갔으므로, 어느 주소였는지는 설정에서 확인합니다. 로컬 런타임을 붙여 쓴 경우의 흔적은 [Ollama](ollama.md) 쪽에서 다룹니다. 서버 쪽에 남는 자료는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 받습니다.

## 위치와 버전별 차이

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%APPDATA%\anythingllm-desktop\storage\anythingllm.db` | 대화·워크스페이스·스레드·이벤트·첨부 기록(SQLite) | 보고서[1], 샘플 DB[4] |
| `%APPDATA%\anythingllm-desktop\storage\documents\` | 문서 라이브러리에 올린 문서의 JSON(본문 포함) | 보고서[1], 파서[2] |
| `%APPDATA%\anythingllm-desktop\storage\direct-uploads\` | 대화 창에 바로 붙인 파일의 JSON | 샘플 DB `workspace_parsed_files.metadata` 의 `location` 값[4] |
| `%APPDATA%\anythingllm-desktop\storage\hotdir\` | 문서·첨부 JSON 의 `url` 값에 나오는 위치 | 샘플 JSON[4] |
| `%APPDATA%\anythingllm-desktop\storage\.env` | 환경 설정 | 보고서[1] |
| `%APPDATA%\anythingllm-desktop\GPUCache\`, `DawnWebGPUCache\`, `DawnGraphiteCache\` | `AnythingLLM.exe` 가 쓴 그래픽 캐시 | Procmon 화면[5] |

문서 JSON 과 첨부 JSON 의 파일 이름은 `원래 이름-UUID.json` 모양입니다(예: `notes.txt-` 뒤에 UUID)[4]. 파서는 `documents` 아래를 하위 폴더까지 뒤져 JSON 을 찾으므로[2], 그 아래 폴더 구조는 검체에서 직접 봅니다. `hotdir` 에 원래 파일이 그대로 남는지는 공개 자료에 없어서 검체로 확인해야 합니다.

`storage` 폴더 밖의 `GPUCache` 같은 폴더는 크롬 계열 앱 프로필에서 보이는 이름입니다. 크롬 계열 앱 프로필의 구조는 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)에서 다루고, `%APPDATA%\anythingllm-desktop\` 에 그 밖에 무엇이 생기는지는 검체에서 폴더 목록을 떠서 봅니다.

**판 번호.** 자료에 앱 판 번호가 없습니다. 샘플 DB 의 `_prisma_migrations` 표에는 적용한 스키마 변경이 40건 있고, 가장 늦은 `migration_name` 은 `20260406120000_init` 입니다[4]. 검체에서도 이 표의 목록과 설치 파일의 판 정보를 함께 적어 두면, 아래 표와 칸이 어느 무렵 스키마 기준인지 나중에 맞춰 볼 수 있습니다. Jan·Msty 처럼 저장 형식을 새로 바꾼 로컬 AI 앱도 있으니[6], 표 이름을 먼저 `sqlite_master` 로 읽고 시작합니다.

## 구조

### `anythingllm.db` 의 주요 표

샘플 DB 는 페이지 크기 4096 바이트, 롤백 저널 방식이고 표가 32개(`sqlite_sequence` 포함)입니다[4]. 조사에 바로 쓰는 표는 아래와 같습니다.

| 표 | 주요 칸 | 알려 주는 것 |
|---|---|---|
| `workspace_chats` | `id`, `workspaceId`, `prompt`, `response`, `include`, `user_id`, `createdAt`, `lastUpdatedAt`, `thread_id`, `feedbackScore`, `api_session_id` | 질문 한 번과 답 한 번 |
| `workspaces` | `id`, `name`, `slug`, `chatProvider`, `chatModel`, `chatMode`, `openAiPrompt`, `openAiTemp`, `openAiHistory`, `agentProvider`, `agentModel`, `createdAt` | 워크스페이스 이름과 설정. `openAiPrompt` 가 시스템 프롬프트 |
| `workspace_threads` | `id`, `name`, `slug`, `workspace_id`, `user_id`, `createdAt` | 스레드 이름과 만든 시각 |
| `workspace_parsed_files` | `id`, `filename`, `workspaceId`, `userId`, `threadId`, `metadata`, `tokenCountEstimate`, `createdAt` | 대화 창에 붙인 파일 |
| `event_logs` | `id`, `event`, `metadata`, `userId`, `occurredAt` | 앱 안에서 일어난 일의 기록 |
| `workspace_documents`, `document_vectors` | `docId`, `filename`, `docpath`, `workspaceId` / `docId`, `vectorId` | 문서와 워크스페이스, 문서와 벡터 ID 의 연결. 샘플에서는 문서 JSON 이 있는데도 비어 있었음 |
| `prompt_history` | `workspaceId`, `prompt`, `modifiedBy`, `modifiedAt` | 워크스페이스별 프롬프트와 바꾼 시각. 샘플에서는 비어 있어 쓰임은 검체로 확인 |
| `system_settings` | `label`, `value` | 앱 설정. 샘플에는 `telemetry_id`, `onboarding_complete` 두 행 |
| `embed_chats` | `prompt`, `response`, `session_id`, `connection_information`, `embed_id` | `embed_configs` 에 딸린 또 하나의 대화 표. 샘플에서는 비어 있음 |

샘플에서 행이 있던 표는 `workspace_chats`(6), `workspaces`(2), `workspace_threads`(4), `workspace_parsed_files`(7), `event_logs`(47), `system_settings`(2), `_prisma_migrations`(40) 뿐이었고(`sqlite_sequence` 제외), `users` 를 비롯한 나머지는 비어 있었습니다[4]. `user_id` 칸도 모두 비어 있었습니다.

### `workspace_chats.response` 의 JSON

`response` 칸은 글이 아니라 JSON 이고, 아래 키가 들어 있습니다[4].

- `text`: 모델이 낸 답 본문
- `sources[]`: 답에 쓴 문서 조각. 조각마다 `id`, `title`, `url`, `chunkSource`, `published`, `location`, `isDirectUpload`, `text` 등이 들어 있습니다.
- `type`, `attachments[]`
- `metrics`: `model`, `provider`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `outputTps`, `duration`, `timestamp`

Impl 파서는 이 JSON 에서 `text` 만 꺼내 CSV 에 옮기므로[2], 어떤 모델이 답했는지와 어떤 문서를 참고했는지는 원래 JSON 을 따로 읽어야 합니다.

### 스레드와 대화의 연결

`workspace_chats.thread_id` 가 `workspace_threads.id` 를 가리킵니다. 샘플에서 `thread_id` 가 빈 행은 스레드를 따로 만들지 않고 워크스페이스 기본 창에서 보낸 대화였고, 그때의 `sent_chat` 이벤트에도 스레드 이름이 없었습니다[4].

샘플의 스레드는 처음에 `Thread` 라는 이름으로 생기고, 첫 질문을 보낸 뒤 질문 앞 18자에 말줄임표(`…`, UTF-8 `E2 80 A6`)를 붙인 이름으로 바뀌었습니다. `event_logs` 의 `sent_chat` 기록을 차례로 보면 같은 스레드의 이름이 `Thread` 에서 새 이름으로 바뀌는 순간이 남아 있습니다[4]. 샘플처럼 스레드 이름이 첫 질문의 앞부분이면, 대화 행이 사라져도 스레드 이름으로 첫 질문의 일부를 알 수 있습니다.

### `event_logs`

`event` 칸은 사건 이름이고, `metadata` 칸은 JSON 입니다. 샘플에 나온 사건 이름은 아래 열 가지입니다[4].

| `event` | `metadata` 에 든 것 |
|---|---|
| `workspace_created` | `workspaceName` |
| `workspace_thread_created` | `workspaceName` |
| `sent_chat` | `workspaceName`, `thread`(스레드에서 보낸 경우), `chatModel` |
| `workspace_file_uploaded` | `filename`(JSON 파일 이름), `workspaceId` |
| `document_uploaded_to_chat` | `documentName`(원래 이름), `workspace`(slug), `thread` |
| `document_uploaded` | `documentName` |
| `update_llm_provider`, `update_embedding_engine`, `update_vector_db` | 샘플에서는 빈 `{}` |
| `workspace_vectors_reset` | `reason` |

`update_llm_provider` 는 공급자를 바꿨다는 사실만 남기고 무엇으로 바꿨는지는 적지 않습니다. 대화마다 실제로 쓴 공급자와 모델은 `response` 의 `metrics` 에서 읽습니다.

### 문서 JSON 과 첨부 JSON

`documents` 와 `direct-uploads` 아래 JSON 의 키는 아래와 같습니다[2][4].

| 키 | 담긴 것 |
|---|---|
| `id` | 문서 UUID. 파일 이름 뒤쪽과 같음 |
| `url` | `file://` 로 시작하는 `storage\hotdir\원래 이름` |
| `title` | 원래 파일 이름 |
| `docAuthor`, `description`, `docSource` | 작성자, 설명, 출처 설명. 샘플의 `docSource` 는 글 파일이 `a text file uploaded by the user.`, PDF 가 `pdf file uploaded by the user.` |
| `chunkSource` | `localfile://` 로 시작하는 원래 파일 위치 |
| `published` | 처리한 시각 문자열(아래 "시각 해석") |
| `wordCount`, `token_count_estimate` | 단어 수와 토큰 수 추정 |
| `pageContent` | 뽑은 본문 전체 |

대화 창에 붙인 파일은 `workspace_parsed_files.metadata` 에도 같은 키가 들어가는데, 여기에는 `pageContent` 가 없고 대신 `location`(`direct-uploads` 안 JSON 경로)과 `isDirectUpload` 가 있습니다[4]. 본문은 `location` 이 가리키는 JSON 과, 답의 `sources[].text` 조각에서 찾습니다.

`chunkSource` 에는 사용자가 파일을 고른 원래 위치가 들어갑니다. 샘플에서는 사용자 `Downloads` 폴더 아래 경로였습니다[4]. 이 값에는 사용자 계정 이름이 들어 있으니 보고서에 옮길 때 필요한 만큼만 씁니다.

### 비밀 값이 들 수 있는 곳

`api_keys.secret`, `browser_extension_api_keys.key`, `desktop_mobile_devices.token`, `temporary_auth_tokens.token`, `password_reset_tokens.token`, `users.password`, `recovery_codes.code_hash` 칸은 이름 그대로 키·토큰·비밀번호를 담는 칸이고, 샘플에서는 모두 비어 있었습니다[4]. `.env` 도 설정 파일이라 원격 공급자 키 같은 값이 들어 있는지 검체에서 확인합니다. 값이 있으면 있다는 사실과 위치만 적고 보고서에서는 가립니다. 공통 원칙은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** `workspace_chats` 행이 있으면 그 시각에 그 워크스페이스에서 이 질문을 보내고 이 답을 받은 기록이 그 계정의 앱 저장소에 있다고 쓸 수 있습니다. 답 JSON 의 `metrics` 로 어느 공급자·모델이 답했는지, `sources` 로 어느 문서를 참고했는지 말할 수 있습니다. 문서·첨부 JSON 이 있으면 그 이름의 파일을 앱에 넣었고, 앱이 그 본문을 이만큼 읽어 저장했다고 쓸 수 있습니다. `chunkSource` 는 그 파일을 어느 폴더에서 골랐는지 알려 줍니다. `event_logs` 는 워크스페이스·스레드를 만들고, 파일을 올리고, 설정을 바꾼 차례를 알려 줍니다.

**증명하지 못하는 것.** 샘플처럼 사용자 표가 비어 있으면 `user_id` 로 사람을 가릴 수 없어서, 그 대화를 누가 쳤는지는 계정·로그온 기록으로 따로 밝힙니다([그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)). 문서 JSON 은 앱이 파일을 처리했다는 기록이지, 그 파일 내용을 모델에 보냈다는 기록이 아닙니다. 모델에 실제로 간 조각은 답의 `sources` 에서 봅니다. 원격 공급자를 쓴 경우 질문이 서버로 나갔다는 점은 `metrics.provider` 로 말할 수 있지만, 서버가 그 내용을 얼마나 보관했는지는 이 기록으로 알 수 없습니다.

## 시각 해석

| 값 | 형식 | 기준 |
|---|---|---|
| `createdAt`, `lastUpdatedAt`, `occurredAt` 등 DB 의 날짜 칸 | 정수 Unix 밀리초 | UTC |
| `response` 의 `metrics.timestamp` | ISO 8601 문자열, 끝에 `Z` | UTC |
| 문서·첨부 JSON 의 `published` | `DD/MM/YYYY, HH:MM:SS` 모양 문자열, 오프셋 없음 | 기기 현지 시각 |

DB 의 날짜 칸은 `DATETIME` 으로 선언됐지만 샘플에서는 SQLite 저장 형식이 정수였고, 값은 Unix 밀리초였습니다[4]. 샘플에서 대화 한 행의 `createdAt` 과 그 답의 `metrics.timestamp` 는 앞뒤로 10초 안쪽에 붙어 있어서, `createdAt` 이 UTC 라는 점을 이 둘로 맞춰 볼 수 있습니다[4]. 같은 대화의 `sent_chat` 이벤트 시각도 몇 초 안쪽에 있지만 앞서기도 하고 뒤서기도 해서, 질문 순서는 `createdAt` 으로 정합니다.

샘플의 `published` 에서 1시간을 빼면 같은 첨부의 `workspace_parsed_files.createdAt` 과 같은 초이거나 몇 초 앞선 시각이 됩니다[4]. 그래서 샘플 기기의 시간대는 UTC+1 로 읽힙니다. 샘플에서는 날짜가 일/월/년 순서였지만 `05/05` 처럼 일과 월이 같은 날은 순서를 가릴 수 없으니, 같은 문서의 DB 밀리초 값과 맞춰 순서와 시간대를 정합니다.

DB 의 밀리초 값을 사람이 읽는 시각으로 바꾸는 법은 1000 으로 나눈 Unix 초로 보는 것입니다. 예를 들어 만든 예시 값 `1767225600000` 은 2026-01-01 00:00:00 UTC 입니다. 다른 기록과 한 줄로 늘어놓는 법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **기록이 지워진 흔적.** 샘플에서 `event_logs` 의 `workspace_file_uploaded` 는 10건인데 `workspace_parsed_files` 에 남은 행은 7건이고, `sqlite_sequence` 의 그 표 값은 10이었습니다[4]. 행이 빠진 자리의 파일 이름은 이벤트 `metadata` 의 `filename` 에 남아 있습니다. 한 표만 보면 사라진 첨부를 놓칩니다.
- **삭제 뒤 복구.** 대화나 문서를 UI 에서 지운 뒤 무엇이 남는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. SQLite 에서 지운 행을 찾는 일반 방법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html)와 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)를 봅니다.
- **켜진 앱의 DB.** 앱이 켜져 있으면 잠금을 피하려고 DB 를 `-wal`, `-shm` 과 함께 복사한 뒤 엽니다[1][2]. 샘플 DB 는 롤백 저널 방식이라 `-wal` 이 없을 수 있지만, 있으면 반드시 함께 떠야 마지막 대화가 빠지지 않습니다.
- **파서가 읽지 않는 것.** Impl 파서는 `workspace_chats`, `workspaces`, `event_logs` 세 표와 `documents` 아래 JSON 만 읽습니다[2]. `workspace_threads`(스레드 이름), `workspace_parsed_files`, `direct-uploads` 아래 JSON, 답 JSON 의 `metrics`·`sources` 는 결과 CSV 에 들어가지 않습니다. `documents` 폴더가 없으면 `storage` 전체에서 `pageContent` 나 `chunkSource` 가 든 JSON 을 모읍니다.
- **시간대 가정.** 같은 저장소의 `correlation.py` 는 시각 칸 전체가 밀리초로 읽히지 않고 시간대 표시도 없으면 `Asia/Kolkata` 시각으로 보고 UTC 로 바꿉니다[4]. 샘플의 `published` 는 UTC+1 이었으므로 이 가정을 그대로 쓰면 시각이 어긋납니다.
- **수집 범위.** KAPE 타깃은 `C:\Users\%user%\AppData\Roaming\anythingllm-desktop\storage\` 만 재귀로 모읍니다[3]. 같은 프로필 폴더의 캐시 폴더나 다른 드라이브에 둔 저장소는 모으지 않습니다.
- **KAPE 모듈.** 모듈은 `main.py --app anythingllm` 을 부르는데[3], 저장소 트리에는 이 `main.py` 도, 보고서가 적은 `src/reporter/anythingllm/` 도 없습니다[1]. 실제로 돌릴 수 있는 것은 독립 파서 `final_anythingllm_parser.py` 입니다.

## 직접 분석해 보기

### 헥스로 한 번

먼저 DB 파일 머리 32바이트를 봅니다. 아래는 SQLite 명세에 맞춰 만든 예시이고, 샘플 DB 의 머리도 앞 20바이트가 이와 같았습니다[4].

```
00000000: 5351 4c69 7465 2066 6f72 6d61 7420 3300  SQLite format 3.
00000010: 1000 0101 0040 2020 0000 0001 0000 0010  .....@  ........
```

오프셋 16~17 의 `10 00` 은 페이지 크기 4096 이고, 오프셋 18~19 의 `01 01` 은 롤백 저널 방식이라는 뜻입니다. WAL 방식이면 이 두 바이트가 `02 02` 이고, 그때는 `-wal` 파일을 꼭 함께 봅니다. 머리 구조는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html) 쪽에서 자세히 다룹니다.

스레드 이름은 레코드 안에 UTF-8 로 들어 있습니다. 아래는 첫 질문이 `draft a summary of the report` 였다고 가정해 만든 예시로, 앞 18자 뒤에 말줄임표 `E2 80 A6` 이 붙습니다.

```
64 72 61 66 74 20 61 20 73 75 6d 6d 61 72 79 20 6f 66 e2 80 a6   draft a summary of…
```

지운 행을 카빙할 때 `E2 80 A6` 로 끝나는 짧은 글을 찾으면 스레드 이름 후보를 모을 수 있습니다.

### 공개 도구로 한 번

사본을 만든 뒤 SQLite 셸이나 DB 브라우저로 엽니다. 스레드 이름과 공급자까지 한 번에 보려면 아래처럼 묻습니다.

```sql
SELECT c.id, w.name AS workspace, t.name AS thread, c.prompt,
       json_extract(c.response, '$.metrics.provider') AS provider,
       json_extract(c.response, '$.metrics.model')    AS model,
       datetime(c.createdAt / 1000, 'unixepoch')      AS created_utc
FROM workspace_chats c
LEFT JOIN workspaces w        ON c.workspaceId = w.id
LEFT JOIN workspace_threads t ON c.thread_id  = t.id
ORDER BY c.createdAt;
```

Impl 파서는 `storage` 폴더 사본을 받아 CSV 네 개를 냅니다[2].

```
python final_anythingllm_parser.py --src 수집본\anythingllm-desktop\storage --dst out
```

결과는 `anythingllm_chats.csv`, `anythingllm_workspaces.csv`, `anythingllm_event_logs.csv`, `anythingllm_document_contents.csv` 이고, DB 에서 온 시각은 밀리초 값 그대로, 문서 CSV 의 시각은 `published` 문자열 그대로 옮깁니다[1][2]. 위 "함정과 한계" 에 적은 대로 스레드 이름·첨부 표·`metrics` 는 따로 읽습니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [Ollama](ollama.md) | 로컬 런타임을 붙여 썼을 때 모델 적재·요청 기록 |
| [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md) | `anythingllm-desktop` 프로필 폴더의 캐시 |
| [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) | `AnythingLLM.exe` 를 실행한 흔적. 같은 저장소의 상관 분석은 SRUM 과 `$MFT` 기록을 질문 시각 앞뒤 600초 안에서 맞췄습니다[4] |
| [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) | 원격 공급자로 나간 요청 |
| [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) | DB 밀리초 값과 파일 시스템 시각 맞추기 |
| [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) | 문서 JSON 의 `pageContent`·`chunkSource` 로 넣은 자료 밝히기 |

## 실습

k0w4lzk1/LangurTrace-Implementation 저장소의 `Ourimplementation/correlation/` 폴더에 샘플 `anythingllm.db` 와 문서 JSON 세 개, 파서 결과 CSV 가 있습니다[4]. 사본을 내려받아 아래 질문을 풀어 봅니다.

1. `workspace_chats` 여섯 행을 `workspace_threads` 와 이으면, 스레드마다 대화가 몇 개이고 스레드 없이 보낸 대화는 어느 것입니까?
2. 각 대화의 `createdAt` 과 `response` 의 `metrics.timestamp` 는 몇 밀리초 차이 나고, 어느 쪽이 앞섭니까?
3. `event_logs` 의 `workspace_file_uploaded` 기록과 `workspace_parsed_files` 행을 맞춰 보면, 표에서 빠진 첨부 JSON 이름은 무엇입니까?
4. 문서 JSON 의 `published` 와 `event_logs` 의 `document_uploaded` 시각을 맞추면 기기 시간대는 UTC 에서 몇 시간 떨어져 있습니까?
5. 같은 폴더의 `anythingllm_chats.csv` 에는 어떤 칸이 빠져 있고, 그 값은 DB 어디에서 찾습니까?

## 참고 문헌

1. k0w4lzk1/LangurTrace-Implementation, "AnythingLLM Integration & Custom Parser Report", https://github.com/k0w4lzk1/LangurTrace-Implementation — `Ourimplementation/anything llm parser and kape files/AnythingLLM_LangurTrace_Extension_Report.md`
2. 같은 저장소, `Ourimplementation/anything llm parser and kape files/final_anythingllm_parser.py`
3. 같은 저장소, `Ourimplementation/anything llm parser and kape files/AnythingLLM.tkape`, `AnythingLLM.mkape`
4. 같은 저장소, `Ourimplementation/correlation/` 의 `anythingllm.db`, 문서 JSON 세 개, `anythingllm_chats.csv`, `anythingllm_document_contents.csv`, `correlation.py`, `report.md`
5. 같은 저장소, `Ourimplementation/anythingllm procmon vm setup/` 의 Procmon 화면(`image.png`)
6. 같은 저장소, `README.md`, `GAPS.md`
