---
title: "Msty"
parent: "아티팩트 · 로컬 AI"
nav_order: 710
---

# Msty

Msty 는 모델을 받아 자기 컴퓨터에서 돌리는 기능과 대화 화면을 한 프로그램에 담은 통합형 로컬 AI 앱이고, `%AppData%\Msty` 폴더의 `msty.db` 하나에 대화·설정·API 키가, `logs\app.log` 에 모델 받기와 대화 시작, 첨부 전송이 줄마다 시각과 함께 남습니다.

이 페이지의 경로와 필드는 Msty 1.8.5 판 기준이고[1], 새 판은 저장 형식이 다릅니다[4]. 로그·DB 예시 값은 모두 만든 예시입니다.

## 무엇을 기록하나 · 왜 생기나

Msty 는 모델을 받아 띄우는 백엔드 런타임과 대화 화면인 클라이언트를 한 프로그램에 합친 통합형 앱이라서 두 쪽 흔적이 함께 생깁니다[1, §3.3, §4.6]. Msty 는 안에서 로컬 AI 서비스를 따로 띄우고(`app.log` 의 `Service is now running at: 127.0.0.1:10000`), 이 서비스가 쓰는 모델 폴더는 Ollama 와 같은 매니페스트·blob 짜임입니다[2]. 로컬 AI 앱을 백엔드·클라이언트·통합형으로 나누는 틀은 [로컬 AI](index.md)에서, 백엔드 쪽 흔적의 일반 모양은 [Ollama](ollama.md)에서 다룹니다.

Msty 에서 눈여겨볼 점은 세 가지입니다[1, §4.6.2]. 올린 파일은 `attachments` 폴더에 들어가고, 파일을 올린 메시지를 지워도 파일은 그대로 남습니다. 모델 설치 기록은 `app.log` 에 남아서, 지운 모델도 무엇을 받았는지 알 수 있습니다. `msty.db` 라는 SQLite 파일 하나에 대화 내용과 API 키를 포함한 설정이 모두 들어 있어서, 클라이언트 앱에서 기대하는 흔적 대부분을 이 파일 하나에서 얻습니다.

Msty 아티팩트는 다섯 가지입니다[1, 부록 B].

| 아티팩트 | 형식 | 담긴 것 |
|---|---|---|
| 주 기록(`app.log`) | 텍스트(줄마다 JSON) | 모델 설치, 모델 적재, 첨부 올림·지움 |
| 모델 매니페스트 | Docker V2 매니페스트 | 모델 층의 메타데이터 |
| 모델 층 | 이진 | 모델, 채팅 틀, 라이선스, 매개변수 |
| 대화(`msty.db`) | SQLite 3 | 설정, 대화 세션, API 키 |
| 올린 파일 | 원래 형식 | 올린 파일(지운 것 포함) |

클라우드 모델도 API 키를 넣어 Msty 안에서 쓸 수 있습니다. OpenAI 키를 등록해 `gpt-4o` 와 나눈 대화 같은 클라우드 모델 대화도 로컬 모델 대화와 같은 `msty.db` 표에 들어갑니다[2]. API 키로 쓰는 클라우드 대화는 대개 서버가 문맥을 보관하지 않고, 로컬 앱이 대화 기록을 저장해 두었다가 요청마다 함께 보냅니다[1, §3.4]. 그래서 이런 대화의 본문은 서비스 회사보다 이 기기의 `msty.db` 에서 먼저 찾습니다.

## 위치와 버전별 차이

### Windows(Msty 1.8.5)

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%AppData%\Msty\msty.db` | 대화 세션, 메시지, API 키, 앱 설정, 기본 프롬프트 | 논문 부록 A, 샘플 |
| `%AppData%\Msty\logs\app.log` | 앱 시작·종료, 로컬 AI 서비스, 모델 받기·적재, 대화 시작, 첨부 전송 | 논문 부록 A, 샘플 |
| `%AppData%\Msty\attachments\{Unix 밀리초}-{원래 이름}` | 올린 파일 원본 | 논문 부록 A, 샘플 |
| `%AppData%\Msty\models\manifests\registry.ollama.ai\library\{모델}\{태그}` | 모델 매니페스트 | 논문 부록 A, 샘플 |
| `%AppData%\Msty\models\blobs\sha256-{digest}` | 모델 층(모델 본체 GGUF 포함) | 논문 부록 A, 샘플 |
| `%AppData%\Msty\msty-local.exe` | 로컬 AI 서비스 실행 파일 | 샘플 `app.log` 줄 |
| `%AppData%\Msty\msty-models-registry.json` | 앱이 받아 둔 모델 목록 정보 | 샘플 `app.log` 줄 |

매니페스트 경로의 마지막 자리(`{parameters}`)에는 `gemma3\1b`, `tinyllama\latest` 처럼 태그가 옵니다[1][2]. 마지막 두 줄은 `app.log` 의 `Skipping msty-local binary copy. File already exists at ...` 와 `Models registry updated and the latest info is at ...` 줄에 나오는 경로이고, LangurTrace 는 이 두 파일을 모으지 않습니다[2].

모델 폴더는 설정으로 정해집니다. `msty.db` 의 `app_settings` 표에서 키 `app.localAI.text` 의 값에 `modelsPath` 가 들어 있고, `app.log` 에도 로컬 AI 서비스를 띄울 때마다 `Serving models from: ...` 와 `modelsFolder: ...` 줄이 찍힙니다[2]. 이 값이 기본 경로와 다르면 그 경로를 따로 모읍니다. 모델 층의 짜임과 GGUF 헤더 읽기는 [로컬 모델 파일](model-files.md)에서 다룹니다.

### macOS·Linux

다른 운영체제에서도 아티팩트 종류와 쓰임은 대체로 같고, 형식과 위치는 다를 수 있습니다[1, §6.2]. macOS·Linux 는 실제 기기의 사용자 폴더에서 `msty.db` 와 `attachments` 폴더 이름으로 찾아 위치를 확인해야 합니다.

## 구조

### msty.db 의 표

`msty.db` 는 SQLite 3 파일이고, 머리글의 오프셋 0x12·0x13 두 바이트가 둘 다 `01` 인 롤백 저널 방식으로 쓰입니다[2]. 스키마에는 표가 스무 개 남짓 있고, 대화 조사에 쓰는 표는 아래와 같습니다. 이 가운데 핵심은 `api_keys`, `chat_sessions`, `chat_messages` 이고[1, 표 6], LangurTrace 는 `api_keys`, `chats`, `chat_messages`, `chat_sessions`, `custom_prompts` 다섯 표를 엑셀로 옮깁니다[2, `conversations_reporter.py`].

| 표 | 주요 열 | 담긴 것 |
|---|---|---|
| `chat_session_folders` | `id`, `title`, `sort_order`, `created_at` | 대화 폴더. 기본으로 `id` 가 `__ORPHANAGE__`, `title` 이 `Misc` 인 폴더 하나가 있음 |
| `chat_sessions` | `id`, `title`, `created_at`, `archived_at`, `folder_id`, `splits_order`, `is_vapor` | 왼쪽 목록에 보이는 대화 하나 |
| `chats` | `id`, `title`, `model_vendor`, `model_name`, `config`, `parent_chat_id`, `created_at`, `chat_session_id`, `extras`, `prompt_response_metrics` | 세션 안의 대화 창. 모델과 대화 설정 |
| `chat_messages` | `id`, `chat_id`, `text`, `role`, `model_name`, `attachments`, `config`, `parent_id`, `branch_parent_id`, `created_at`, `extras`, `prompt_response_metrics`, `reasoning_info` | 메시지 본문 하나 |
| `api_keys` | `id`, `name`, `key`, `provider`, `created_at`, `key_hint`, `models`, `extras`, `save_in_keychain` | 등록한 클라우드 서비스 키 |
| `app_settings` | `key`, `value` | 앱 설정. 모델 폴더, 로컬 서비스 주소, 기본 모델, 창 위치 |
| `custom_prompts` | `id`, `act`, `prompt`, `tags`, `type`, `is_custom`, `created_at` | 프롬프트 모음 |
| `search` | `extras`, `entity`, `content`, `entityId` | 메시지 본문 전문 검색 색인(FTS5 가상 표) |

이 밖에 `knowledge_stacks`, `workspaces`, `bookmarked_chat_messages`, `recent_messages`, `model_details`, `local_ai_stt_models` 표가 있고 샘플에서는 모두 비어 있습니다[2].

표끼리는 `chat_session_folders.id` ← `chat_sessions.folder_id`, `chat_sessions.id` ← `chats.chat_session_id`, `chats.id` ← `chat_messages.chat_id` 로 이어집니다. 논문 표 6 은 `chat_messages.chat_id` 를 "대화 세션 ID" 라고 적었지만[1, 표 6], 샘플 스키마의 외래 키와 LangurTrace 코드는 이 열을 `chats.id` 에 잇습니다[2]. 샘플에서는 세션 하나에 `chats` 행이 하나씩이라 두 값이 달라도 결과가 같지만, 세션 ID 로 메시지를 찾으면 한 행도 나오지 않습니다. `chats` 를 거쳐 잇는 것이 스키마 그대로입니다.

주요 열의 값은 아래와 같습니다[2].

- **`role`**: 사용자 메시지는 `user`, 모델 답은 `ai` 입니다.
- **`model_name`**: 로컬 모델은 `gemma3:1b` 처럼 Ollama 식 이름이고, 클라우드 모델은 `{api_keys.id}::gpt-4o` 처럼 키 행의 ID 앞에 붙습니다. 그래서 이 열로 어느 등록 키를 거쳐 보냈는지가 이어집니다.
- **`branch_parent_id`**: 바로 앞 메시지의 `id` 가 들어가서, 이 열을 따라가면 대화 순서가 나옵니다. 샘플에서 `parent_id` 는 모두 비어 있습니다.
- **`attachments`**: JSON 이고 `images`, `documents`, `youtube_links` 목록이 있습니다. 파일 하나에는 `size`, `type`(MIME), `path`(`attachments` 폴더 안의 사본 경로), `name`, `org_path`(올리기 전 원래 파일 경로), `org_name`, `folder` 가 들어갑니다. `org_path` 에는 사용자가 파일을 어디서 골랐는지가 드러납니다.
- **`config`**: 사용자 메시지에 그때의 모델 옵션(`maxTokens`, `temperature`, `topP` 등)이 JSON 으로 들어갑니다. `chats.config` 의 `modelOptions.systemPrompt` 에는 그 대화에 건 시스템 프롬프트가 들어갑니다.
- **`prompt_response_metrics`**: 모델 답 행에 JSON 으로 들어갑니다. `current` 에 이 답의 값이, `previous` 에 바로 앞 답의 값이 들어가고, 각각 옵션과 `model`, `time_to_first_token`, `prompt_eval_count`(입력 토큰), `eval_count`(출력 토큰)가 있습니다. 로컬 모델은 `created_at`(ISO 8601, `Z`)과 `total_duration`(나노초)도, 클라우드 모델은 `estimated_cost` 도 들어갑니다.
- **`extras`**: 메시지 행에는 `branch_active_at`(Unix 밀리초)이, `chats` 행에는 `is_temp_title` 과 첨부 목록이 들어갑니다.

아래는 이 열들을 모은 메시지 두 행입니다(만든 예시).

```text
id               01KKMTPSVCQ4R8T2W6Y0A3C5E7
chat_id          01KKMTMBE6H3J5K7M9N1P3Q5R7
text             이 영수증 금액을 표로 정리해 줘
role             user
model_name       01KKMT9W2DX4Z6B8C0E2G4J6K8::gpt-4o
attachments      {"images":[{"size":48210,"type":"image/png","path":"C:\\Users\\labuser01\\AppData\\Roaming\\Msty\\attachments\\1773446841905-receipt.png","name":"1773446841905-receipt.png","org_path":"C:\\Users\\labuser01\\Desktop\\receipt.png","org_name":"receipt.png","folder":"attachments"}],"documents":[],"youtube_links":[]}
created_at       2026-03-14 00:07:30

id               01KKMTPZAMV2W4X6Y8Z0A2B4C6
chat_id          01KKMTMBE6H3J5K7M9N1P3Q5R7
role             ai
branch_parent_id 01KKMTPSVCQ4R8T2W6Y0A3C5E7
created_at       2026-03-14 00:07:36
extras           {"branch_active_at":1773446856020}
```

### api_keys 표

`api_keys` 의 `provider`, `key`, `created_at` 은 클라우드 서비스, API 키, 등록 시각입니다[1, 표 6]. 다만 `key` 열은 평문 키가 아니고, `v10` 세 글자 뒤에 알아볼 수 없는 바이트가 이어지는 값입니다(열 형식은 text)[2]. `v10` 은 Chromium 이 운영체제 보호 키(Windows 에서는 DPAPI 로 감싼 키)로 암호화한 값 앞에 붙이는 표지와 같습니다[3]. 같은 행의 `save_in_keychain` 은 `1` 이고, `key_hint` 에는 `sk-...Q7xZ`(만든 예시)처럼 키의 앞 세 글자와 끝 네 글자만 평문으로 남습니다[2]. `models` 열에는 그 키로 쓸 수 있게 등록한 모델 목록이 JSON 으로 들어갑니다.

키 값은 보고서에 싣지 않고, "어느 서비스의 키가 언제 등록됐고 끝 네 글자가 무엇인지" 까지만 적습니다. 서버 쪽 대화 기록이나 사용 기록이 필요하면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 받습니다. API 키는 서비스 회사에 서버 쪽 자료를 요청할 때 넘기는 단서가 됩니다[1, §4.3]. 키가 남는 곳의 일반 원리는 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에서 다룹니다.

### custom_prompts 와 app_settings

LangurTrace 출력의 `custom_prompts` 시트에서 사용자가 정한 기본 프롬프트를 볼 수 있습니다[1, §5.2]. 샘플의 229행은 모두 `is_custom` 이 `0` 이고 `type` 이 `system`(180행), `user`(38행), `refinement`(11행)이며, `created_at` 이 앱이 처음 뜬 시각과 같습니다[2]. 같은 시각의 `app.log` 에는 `Adding 229 new default prompts` 줄이 있습니다. 앱이 넣은 기본 행이 대부분이므로, `is_custom` 과 `created_at` 으로 앱 설치 때 들어온 행과 나중에 생긴 행을 나눠 봅니다.

샘플 `app_settings` 에는 11개 키가 있습니다[2]. `app.localAI.text`(`modelsPath`, `status`, `port`, `host`), `app.localAI.defaultModelId`, `app.localAI.defaultVisionModelId`, `app.modelsInfoVersion`, `app.windowBounds` 가 조사에 쓰입니다.

### search 표와 지움 트리거

스키마에는 `chat_messages` 에 트리거가 세 개 걸려 있습니다[2]. 메시지를 넣으면 `search` 에 `entity='chat_messages'`, `entityId`(메시지 ID), `content`(본문), `extras`(`{"chatId":...}`)가 한 행 들어가고, 메시지 본문을 고치면 `search.content` 도 고쳐지고, 메시지를 지우면 같은 `entityId` 의 `search` 행도 지워집니다. 외래 키도 `chat_sessions` → `chats` → `chat_messages` 로 `ON DELETE cascade` 가 걸려 있어서, 세션을 지우면 딸린 대화와 메시지, 검색 행까지 함께 지워지게 짜여 있습니다. 그래서 `search` 표에는 지운 메시지의 사본이 따로 남지 않습니다. FTS5 내부 조각(`search_data`)에 지운 메시지의 낱말이 남는지는 실제 데이터로 확인해야 합니다.

### app.log

`app.log` 는 한 줄이 JSON 객체 하나입니다. 필드는 `level`, `time`(Unix 밀리초), `pid`, `hostname`(컴퓨터 이름), `msg` 이고, `level` 은 30·40·50 이 쓰입니다[2]. 40 은 `ollama_llama_server.exe is not running` 같은 경고, 50 은 `Failed fetching model ...` 같은 실패 줄입니다. 조사에 쓰이는 `msg` 는 아래와 같습니다[2].

| `msg` 모양 | 뜻 |
|---|---|
| `Running migrations...` / `Exiting app after flushing...` | 앱 시작 / 앱 종료 |
| `Service is now running at: 127.0.0.1:10000`, `Local AI Text Service started with pid: ...` | 로컬 AI 서비스를 띄움 |
| `Serving models from: ...`, `modelsFolder: ...`, `expose service on network: false` | 서비스 설정. 모델 폴더와 네트워크 공개 여부 |
| `Fetching model: {모델}:{태그}` | 모델 받기 시작 |
| `Failed fetching model {모델}:{태그}: AbortError: ...` | 받기 실패·중단 |
| `Fetched installed models: {모델 목록}` | 그 시각에 설치돼 있던 모델 목록 |
| `Loading model into memory {모델}` | 모델을 메모리에 올림 |
| `Using {모델} model from localai` / `Using {키 ID}::{모델} model from openai` | 대화에 쓴 모델과 출처 |
| `Local Chat conversation started with {모델} and options {...}` | 로컬 모델에 요청을 보냄 |
| `Local Chat conversation was aborted` | 답 생성을 멈춤 |
| `Using OpenAI-compatible API at https://api.openai.com/v1 with key sk-...{끝 네 글자}, options {...}` | 클라우드 API 로 요청을 보냄. 키는 힌트만 찍힘 |
| `Estimating cost for model {모델} with {입력} input tokens and {출력} output tokens` | 클라우드 답의 토큰 수 |
| `Encoding file to base64: ...\attachments\{파일}` | 첨부 파일을 모델에 보냄 |

아래는 첨부를 보내는 요청의 로그 줄입니다(만든 예시).

```text
{"level":30,"time":1773446850412,"pid":4120,"hostname":"LAB-PC01","msg":"Using 01KKMT9W2DX4Z6B8C0E2G4J6K8::gpt-4o model from openai"}
{"level":30,"time":1773446850415,"pid":4120,"hostname":"LAB-PC01","msg":"Encoding file to base64: C:\\Users\\labuser01\\AppData\\Roaming\\Msty\\attachments\\1773446841905-receipt.png"}
{"level":30,"time":1773446850419,"pid":4120,"hostname":"LAB-PC01","msg":"Using OpenAI-compatible API at https://api.openai.com/v1 with key sk-...Q7xZ, options {\"max_tokens\":4095,\"temperature\":1}, extra params {}"}
{"level":30,"time":1773446856010,"pid":4120,"hostname":"LAB-PC01","msg":"Estimating cost for model gpt-4o with 812 input tokens and 64 output tokens"}
```

이 로그에는 첨부를 올리고 지운 기록이 남습니다[1, 부록 B]. 공개 샘플에는 첨부를 보낼 때의 `Encoding file to base64:` 줄만 있고 지움 줄은 없어서, 지움 줄의 모양은 실제 로그에서 확인합니다[2].

### attachments 폴더

올린 파일은 `{Unix 밀리초}-{원래 이름}` 이름의 사본으로 `attachments` 폴더에 들어갑니다[1, §4.6.2][2]. 샘플에서는 이름 앞의 시각이 그 파일을 단 메시지의 `created_at` 보다 3~4초 앞서고, 메시지의 `attachments.name` 과 `app.log` 의 `Encoding file to base64:` 줄에 같은 이름이 나옵니다[2]. 파일 이름·메시지 열·로그 줄 세 곳이 같은 이름으로 이어지는 셈입니다. 첨부와 생성물을 나눠 보는 원리는 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것**

- `chat_messages` 에 남은 행이 있으면, 그 시각에 이 프로그램에서 그 글이 사용자 입력(`user`)이나 모델 답(`ai`)으로 저장됐다는 것
- 메시지별 `model_name` 으로 어느 모델에 물었는지, 클라우드 모델이면 어느 등록 키를 거쳤는지
- `attachments` 폴더의 사본과 메시지의 `org_path` 로, 어떤 파일을 어느 경로에서 골라 모델에 넘겼는지. 메시지를 지워도 사본은 남습니다[1, 표 8]
- `app.log` 의 `Fetching model:` 과 `Fetched installed models:` 줄로, 모델 파일이 지워진 뒤에도 어떤 모델을 받았고 언제 설치돼 있었는지[1, §5.3]
- `api_keys` 행과 로그의 키 힌트로, 어느 클라우드 서비스 키를 언제 등록해 썼는지

**증명하지 못하는 것**

- 그 대화를 누가 쳤는지. `hostname` 은 컴퓨터 이름일 뿐이고, 사람은 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 좁힙니다.
- 모델 답을 사용자가 읽었거나 밖으로 옮겼는지
- 첨부 사본이 있다는 것만으로 그 파일을 모델에 보냈는지. 보낸 시각은 `Encoding file to base64:` 줄과 메시지 행으로 따로 확인합니다.
- 클라우드 서비스가 서버에 무엇을 남겼는지. 기기 기록은 요청을 보냈다는 것까지만 말합니다.
- 지워진 대화가 없었다는 것. LangurTrace 시험에서 UI 로 지운 대화는 되살아나지 않았습니다(0/50)[1, 표 8].

## 시각 해석

| 값 | 형식 | 기준 | 생기는 때 |
|---|---|---|---|
| `chat_sessions.created_at`, `chats.created_at` | `YYYY-MM-DD HH:MM:SS` 글자 | UTC | 새 대화 창을 연 뒤, 첫 메시지보다 0~95초 앞 |
| `chat_messages.created_at` | `YYYY-MM-DD HH:MM:SS` 글자 | UTC | 사용자 행은 보낸 때, `ai` 행은 답을 다 받은 때 |
| `api_keys.created_at` | 같은 글자 | UTC | 키를 등록한 때 |
| `id` 열 앞 10자 | Crockford Base32 로 적은 Unix 밀리초(ULID 모양) | UTC | 행 ID 를 만든 때 |
| `extras.branch_active_at` | Unix 밀리초 | UTC | 행을 저장한 무렵. 샘플에서는 ID 시각과 0.1초 안쪽으로 붙음 |
| `prompt_response_metrics.created_at` | ISO 8601, `Z` | UTC | 로컬 모델의 답 생성이 끝난 때 |
| `app.log` 의 `time` | Unix 밀리초 | UTC | 줄을 쓴 때 |
| 첨부 파일 이름 앞자리 | Unix 밀리초 | UTC | 사본 이름을 정한 때. 샘플에서는 그 메시지 `created_at` 보다 3~4초 앞 |

`created_at` 에는 시간대 표시가 없지만, 샘플에서 첨부를 단 메시지의 `created_at` 과 `app.log` 의 같은 첨부 `Encoding file to base64:` 줄의 `time` 이 초 단위까지 같아서 UTC 로 확인됩니다[2]. 모델 답 행의 `created_at` 은 답을 다 받은 때에 가깝습니다. 샘플에서 사용자 메시지와 `Local Chat conversation started` 줄은 같은 초에 찍혔고, 답 행은 그보다 36초 뒤였으며, 그 답의 `total_duration` 이 35.4초였습니다[2].

`id` 는 26자이고 앞 10자를 풀면 Unix 밀리초가 나옵니다. 샘플의 메시지·API 키 행은 이 값이 `created_at` 과 같은 초였지만, `chat_sessions`·`chats` 행은 ID 시각이 `created_at` 보다 5초에서 1분 39초 앞섰습니다[2]. 새 대화 창을 연 때와 처음 저장한 때가 다를 수 있으므로, 세션 시작 시각을 적을 때는 두 값을 함께 봅니다. `created_at` 은 초 단위까지만 있어서, 같은 초 안의 순서는 ID 시각이나 `branch_parent_id` 로 정합니다.

여러 기록을 시간순으로 합치는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **지운 대화.** LangurTrace 시험에서 UI 로 지운 대화는 0%(0/50), 지운 첨부는 100%(50/50), 지운 모델 받기 기록은 100%(5/5) 되살아났습니다[1, 표 8]. 이 비율은 LangurTrace 로 디스크에서 되살린 결과만 잰 것이고, 볼륨 섀도 복사본·메모리 분석·여유 공간(slack) 분석·SQLite 해제 페이지·WAL 카빙은 시험 범위 밖입니다[1, §6.2]. 방법 일반은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)에서 다룹니다.
- **지운 뒤 되살릴 수 있는 것.** Msty 아티팩트별로 지운 뒤 되살릴 수 있는지는 아래와 같습니다[1, 표 5]. ★ 는 지워도 되살릴 수 있는 것, ✩ 는 있지만 지우면 대개 되살리지 못하는 것, – 는 기능이 없는 것입니다.

  | 내려받은 모델 | 모델 설치 기록 | 대화 설정 | 대화 기록 | 올린 파일 | 생성 파일 | API 키 |
  |---|---|---|---|---|---|---|
  | ★ | ✩ | ★ | ✩ | ★ | – | ✩ |

- **API 키 열.** `key` 열은 `v10` 으로 시작하는 암호화 값이라, 이 열을 평문 API 키로 읽으면 틀립니다[1, 표 6][2][3]. 보고서에는 `provider`, `created_at`, `key_hint` 만 씁니다.
- **수집 범위.** LangurTrace KAPE 타깃은 `C:\Users\%user%\Appdata\Roaming\Msty\` 아래 기본 경로만 모으고, DB 는 파일 마스크가 `msty.db` 하나라 같은 폴더의 `msty.db-journal` 이나 `msty.db-wal` 은 모으지 않습니다[2, `Msty.tkape`]. 로그는 타깃이 `app*.log`, 파서는 `*.log` 를 받습니다. 켜진 앱의 DB 는 저널 파일까지 함께 복사하고, 옮긴 모델 폴더는 `app_settings` 와 로그에서 경로를 읽어 따로 모읍니다. 수집 절차 일반은 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)에서 다룹니다.
- **LangurTrace 의 로그 분류.** `main_history.csv` 는 `msg` 에 소문자 `model` 이 들어 있으면 `Model setup`, `file` 이나 `attachment` 가 들어 있으면 `Attachment` 로 적고(`settings` 가 함께 있으면 버림) 나머지 줄은 버립니다[2, `log_reporter.py`]. 그래서 `No knowledge stacks attached to this model` 이 `Model setup` 으로, `Models info file not found ...` 가 `Attachment` 로 들어가고, `Local Chat conversation started ...` 와 `Using OpenAI-compatible API ...` 줄, 앱 시작·종료 줄은 빠집니다. 샘플 `app.log` 214줄 가운데 97줄만 CSV 에 들어갔습니다[2]. 대화 요청 시각은 원본 `app.log` 에서 읽습니다.
- **LangurTrace 출력의 시각.** `main_history.csv` 의 `time` 은 `time` 값을 분석 PC 의 현지 시각으로 바꾼 것이라, 한국 시간대 PC 에서 만든 샘플 출력은 원본보다 9시간 뒤로 보입니다[2]. 대화 HTML 과 `msty_db.xlsx` 는 DB 의 `created_at` 을 그대로 옮겨서 UTC 입니다. 한 보고서에 두 기준이 섞이지 않게 맞춥니다.
- **LangurTrace 가 읽지 않는 것.** 엑셀에는 다섯 표만 들어가서 `app_settings`, `chat_session_folders`, `search` 는 직접 엽니다. 대화 HTML 은 첨부 가운데 `images` 만 그림으로 붙이고 `documents` 는 넣지 않습니다. `msty.db` 가 여러 개 모여도 첫 파일만 읽습니다[2, `conversations_reporter.py`].
- **대화 제목.** 세션 제목은 사용자가 친 글이 아니라 모델 답이나 제목 생성 결과의 앞부분일 수 있고, `extras.is_temp_title` 이 `true` 인 `chats` 행도 있습니다[2]. 제목을 사용자 입력으로 인용하지 않습니다.
- **로그 줄 수와 메시지 수.** `Local Chat conversation started` 줄은 로컬 모델에 보낸 사용자 메시지마다 한 번씩 찍히고, 답이 끝난 직후에 옵션이 다른 줄(`temperature` 0.5, `num_predict` 1200)이 한 번 더 찍히기도 합니다[2]. 줄 수를 메시지 수로 세지 않고 메시지 행과 시각으로 짝지어 봅니다.
- **멈춘 답.** `Local Chat conversation was aborted` 줄과 `branch_active_at` 이 같은 밀리초인 `ai` 행이 DB 에 남고, 이 행의 `prompt_response_metrics` 에는 `current` 없이 `previous` 만 들어갑니다[2]. 답을 중간에 멈춰도 그때까지 받은 답이 저장될 수 있습니다.
- **판 차이.** 이 페이지의 경로·표·로그 문장은 1.8.5 기준입니다. 2026-05 에 Msty 가 저장 형식을 새로 짰다는 기록이 있습니다[4]. 다른 판은 폴더 구성과 `sqlite_master` 의 스키마부터 확인합니다.

## 직접 분석해 보기

**헥스로.** `msty.db` 사본을 헥스 보기로 열어 첫 16바이트가 `53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00`(글자로 `SQLite format 3` 과 NUL)인지 봅니다. 오프셋 0x10 의 두 바이트가 페이지 크기이고, 0x12·0x13 이 `01 01` 이면 롤백 저널, `02 02` 면 WAL 방식입니다. 아래는 페이지 크기 4096 에 롤백 저널 방식인 머리글입니다(명세로 만든 예시).

```text
00000000: 5351 4c69 7465 2066 6f72 6d61 7420 3300  SQLite format 3.
00000010: 1000 0101 0040 2020 0000 0003 0000 0010  .....@  ........
```

WAL 방식이면 `msty.db-wal` 을 함께 두고 엽니다. 머리글과 페이지 읽는 법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html)에서 다룹니다. 표를 열 때는 사본을 읽기 전용으로 열고, 아래처럼 세션·대화·메시지를 이어 시각 순서로 봅니다.

```sql
SELECT s.title AS session_title, c.model_name AS chat_model,
       m.created_at, m.role, m.model_name, m.text, m.attachments
FROM chat_messages m
JOIN chats c ON c.id = m.chat_id
JOIN chat_sessions s ON s.id = c.chat_session_id
ORDER BY m.created_at, m.id;
```

첨부 파일 이름 `1773446841905-receipt.png`(만든 예시)의 앞 13자리는 Unix 밀리초라서 2026-03-14 00:07:21.905 UTC 가 되고, 메시지 ID `01KKMTPSVCQ4R8T2W6Y0A3C5E7` 의 앞 10자 `01KKMTPSVC` 를 Crockford Base32 로 풀면 1773446850412, 곧 00:07:30.412 UTC 가 됩니다. 이 두 값과 `app.log` 의 `time` 을 나란히 두면 파일을 붙인 때, 메시지를 저장한 때, 파일을 보낸 때가 순서대로 섭니다.

**공개 도구로.** LangurTrace 는 KAPE 타깃(`Msty.tkape`)과 모듈(`Msty.mkape`)로 배포되고, 모듈은 `LangurTrace.exe --src %sourceDirectory% --dst %destinationDirectory% --app msty` 를 실행합니다[2]. 결과는 아래와 같습니다[2].

| 출력 | 내용 |
|---|---|
| `main_history.csv` | 열 `file`, `log type`(`Model setup`·`Attachment`), `time`, `msg` |
| `model_manifest.csv` | 열 `model_name`, `parameter`, `layer_name`, `digest`, `size`, `path`. Ollama 와 같은 코드로 만듦 |
| `msty_db.xlsx` | 시트 `api_keys`, `chats`, `chat_messages`, `chat_sessions`, `custom_prompts` |
| `conversations\{created_at}_{제목 앞 40자}.html` | `chats` 행마다 대화 한 페이지 |
| `uploaded_files\` | `attachments` 폴더의 사본 |

`msty_db.xlsx` 의 `api_keys` 시트에는 `key` 열이 그대로 들어가므로 보고서에 붙이기 전에 가립니다. 함정 절의 로그 분류와 시각 기준을 알고 CSV 를 원본 줄과 맞춰 씁니다.

## 교차 검증

`msty.db` 의 메시지와 `app.log` 는 서로 맞춰 볼 곳이 많습니다. `Estimating cost for model gpt-4o with 15 input tokens and 365 output tokens` 같은 줄의 두 숫자는 같은 답 행의 `prompt_response_metrics.current` 에 든 `prompt_eval_count`(15), `eval_count`(365)와 같습니다[2]. 로그의 `Fetched installed models:` 목록이 바뀐 시각과 `Fetching model:` 줄로 모델을 받은 때를 잡고, 그 뒤 메시지의 `model_name` 이 새 모델로 바뀌는지 봅니다.

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [로컬 AI](index.md) | 통합형 앱의 위치와 다른 로컬 AI 앱 목록 |
| [로컬 모델 파일](model-files.md) | `models` 폴더의 매니페스트·층과 모델 본체 GGUF 헤더, 해시 대조 |
| [Ollama](ollama.md) | 같은 매니페스트 짜임을 쓰는 백엔드의 로그와 비교 |
| [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) | `api_keys` 행을 보고서에 다루는 법 |
| [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/protection/data-protection-api/index.html) | `v10` 표지가 붙은 값을 보호하는 Windows 구조 |
| [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) | 클라우드 모델 호출(`api.openai.com`)과 모델 받기 통신 |
| [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) | 첨부의 `org_path` 와 사본으로 넣은 자료를 밝히는 흐름 |
| [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md) | 로컬 AI 앱 사용을 묻는 조사 흐름 |

## 실습

공개 시험 데이터는 LangurTrace 저장소의 `sample_dataset` 입니다[2]. `collect/C/Users/USER/AppData/Roaming/Msty/` 에 `msty.db`, `logs/app.log`, 첨부 두 개, 매니페스트 세 개와 작은 층 파일들이, `parse/LLM application artifacts/msty/` 에 LangurTrace 출력이 있습니다. 모델 본체 GGUF 는 크기 때문에 빠져 있습니다.

1. `chat_sessions` 세 행의 `created_at` 과 `id` 앞 10자를 푼 시각을 나란히 적으면, 어느 세션의 차이가 가장 큽니까? 그 사이 `app.log` 에는 어떤 줄이 있습니까?
2. 클라우드 모델로 보낸 메시지는 몇 개이고, 그 메시지의 `model_name` 앞부분은 `api_keys` 의 어느 행과 이어집니까? 키 힌트는 로그의 어느 줄에도 나옵니까?
3. 첨부 두 파일의 이름 앞 13자리, 메시지의 `created_at`, `Encoding file to base64:` 줄의 `time` 을 UTC 로 나란히 적어 봅니다. `bus.jpg` 를 보낸 요청에는 어떤 첨부가 함께 실려 갔습니까?
4. `main_history.csv` 의 행 수와 원본 `app.log` 의 줄 수를 비교하고, 빠진 줄 가운데 대화 요청을 나타내는 줄을 찾아 봅니다.
5. `tinydolphin`·`tinyllama` 를 받기 시작한 시각, 실패 줄, 설치 목록에 처음 나온 시각을 로그에서 차례로 적어 봅니다.

## 참고 문헌

1. Jeong, S., Lee, S., Park, J., "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. https://doi.org/10.1016/j.fsidi.2025.301987 (§3.3, §3.4, §4.3, §4.6.2, §5.2, §5.3, §6.2, 표 1, 표 5, 표 6, 표 8, 부록 A, 부록 B)
2. jeongramon/LangurTrace, https://github.com/jeongramon/LangurTrace — `README.md`, `src/apps/msty.py`, `src/reporter/msty/reporter.py`, `src/reporter/msty/log_reporter.py`, `src/reporter/msty/conversations_reporter.py`, `src/reporter/msty/files_reporter.py`, `dist/Targets/LLMApplications/Msty.tkape`, `dist/Modules/LLMApplications/Msty.mkape`, `sample_dataset/collect/C/Users/USER/AppData/Roaming/Msty/`, `sample_dataset/parse/LLM application artifacts/msty/` (2026-09-25 열람)
3. Chromium, https://chromium.googlesource.com/chromium/src/+/main/components/os_crypt/async/browser/dpapi_key_provider.cc — `kKeyTag` 와 그 주석 "Data prefix for data encrypted with DPAPI"
4. k0w4lzk1/LangurTrace-Implementation, https://github.com/k0w4lzk1/LangurTrace-Implementation — `GAPS.md`(2026-05-08 커밋, 2026-09-25 열람)
