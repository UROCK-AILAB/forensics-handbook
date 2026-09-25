---
title: "Jan"
parent: "아티팩트 · 로컬 AI"
nav_order: 720
---

# Jan (Jan)

Jan 은 모델 내려받기와 대화 화면을 한 앱에 담은 통합형 로컬 LLM 앱이고, 0.5.16 판은 `%AppData%\Jan\data` 아래 스레드마다 `thread.json`·`messages.jsonl` 을 두고 모델 설정을 `cortex.db` 에 두며, 엔진 로그 `cortex.log` 에 대화 요청 본문과 모델 받기, API 키까지 평문으로 남깁니다.

이 쪽의 경로와 칸은 Jan 0.5.x 판 기준이고, 새 판은 저장 형식이 다릅니다[3].

## 무엇을 기록하나 · 왜 생기나

로컬 LLM 앱은 백엔드 런타임, 클라이언트 화면, 둘을 합친 통합형으로 나눌 수 있고, Jan 은 통합형입니다[1, §3.3, 표 1]. 그래서 Jan 에는 모델을 받고 돌린 흔적(백엔드 쪽)과 대화·설정·API 키(클라이언트 쪽)가 함께 남습니다. 이 틀과 앱별 비교는 [로컬 AI](index.md)에서 다룹니다.

Jan 0.5.x 는 Cortex 엔진 위에서 돌고, 이 엔진이 `cortex.log` 라는 로그를 씁니다. Jan 은 로그 수준과 범주를 거칠게 잡아 두어 로그가 매우 자세하고, 그래서 모델 설치, 대화 내용, 설정, API 키까지 이 파일에 들어갑니다[1, §4.6.3]. 이 로그에서 대화 요청의 시각·내용·모델, 클라우드 서비스 API 키 평문, 모델을 받은 로컬 경로와 원래 URL 을 읽을 수 있습니다[1, 그림 5].

Jan 은 로컬 모델뿐 아니라 OpenAI·Anthropic 같은 클라우드 모델도 API 키로 부를 수 있습니다. 샘플에서 `gpt-3.5-turbo` 로 나눈 대화도 로컬 모델 대화와 똑같이 스레드 폴더의 `messages.jsonl` 에 들어 있습니다[2]. API 키로 쓴 클라우드 대화는 서버가 대화 문맥을 대개 보관하지 않아 로컬 앱에만 남습니다[1, §3.4]. 프롬프트와 모델 답을 나눠 보는 기준은 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)를 따릅니다.

## 위치와 버전별 차이

### Windows, Jan 0.5.16

경로와 형식은 아래와 같습니다[1, 부록 A·B][2].

| 경로 | 형식 | 담긴 것 |
|---|---|---|
| `%AppData%\Jan\data\models\{허브}\...\*.gguf` | GGUF | 모델 파일 |
| `%AppData%\Jan\data\models\{허브}\...\*.yml` | YAML | 모델 메타데이터 |
| `%AppData%\Jan\data\cortex.db` | SQLite 3 | API 키, 모델 정보 |
| `%AppData%\Jan\data\threads\{스레드 ID}\thread.json` | JSON | 대화 이름, 고른 모델 |
| `%AppData%\Jan\data\threads\{스레드 ID}\messages.jsonl` | JSONL | 대화 기록, 쓴 모델, 시각 |
| `%AppData%\Jan\data\logs\cortex.log` | 텍스트 | 모델 설치 기록, 대화, API 키(지운 것 포함) |
| `%AppData%\Jan\Local Storage\leveldb\` | LevelDB | 대화 목록, 받은 모델(지운 것 일부 포함) |

모델 폴더의 짜임은 허브마다 다릅니다. Jan 자체 허브 모델은 `models\{허브}\{모델}\{크기}\model.gguf` 모양(`models\cortex.so\cogito-v1\3b\model.yml`)이고[1, 부록 A][2], Hugging Face 에서 받은 모델은 `models\huggingface.co\{작성자}\{저장소}\{파일 이름}.yml` 모양입니다[2]. 클라우드 모델 정의는 `models\remote\*.yml` 에 있습니다. 모델 폴더와 YAML 칸은 [로컬 모델 파일](model-files.md)에서 자세히 다룹니다.

KAPE 타깃은 `C:\Users\%user%\AppData\Roaming\Jan\` 아래만 모으고 로그는 `cortex*.log` 로 모두 모으지만, LangurTrace 파서(`src/apps/jan.py`)는 `cortex.log` 한 파일만 읽습니다[2].

### 다른 판과 다른 OS

- **새 판.** Jan 새 판은 저장 형식을 바꿨다는 보고가 있습니다[3]. 새 판의 경로·파일 형식은 공개된 분석 자료가 없어 검체로 확인해야 합니다. 먼저 `%AppData%\Jan` 과 그 아래 `data` 폴더가 있는지, `cortex.log`·`cortex.db` 가 있는지를 보고 판을 가립니다.
- **macOS·Linux.** LangurTrace 시험은 Windows 에서만 했고, 다른 OS 에서도 아티팩트 종류는 같을 것이라는 추정만 있습니다[1, §6.2]. 경로는 검체로 확인합니다.
- **판 확인.** `cortex.log` 는 엔진이 뜰 때마다 `cortex.cpp version: v1.0.12` 같은 줄을 남기므로, 이 줄로 기간별 엔진 판을 알 수 있습니다[2].

## 구조

### thread.json

스레드 폴더 이름과 `id` 가 같습니다. 샘플의 칸은 다음과 같습니다[2].

| 칸 | 뜻 |
|---|---|
| `id` | 스레드 ID(26자, 아래 "시각 해석" 참고) |
| `title`, `metadata.title` | 대화 이름 |
| `created_at` | 스레드를 만든 시각, Unix 초 |
| `metadata.updated_at` | 마지막으로 바뀐 시각, Unix 밀리초 |
| `metadata.lastMessage` | 마지막 메시지 본문 사본 |
| `assistants[].instructions` | 시스템 프롬프트(샘플은 빈 문자열) |
| `assistants[].model.id`, `model.engine` | 고른 모델 ID 와 엔진(`llama-cpp` 등) |
| `assistants[].model.parameters`, `model.settings` | `temperature`, `max_tokens`, `ctx_len`, `prompt_template` 같은 추론 설정 |
| `assistants[].tools[]` | 검색 보강(`retrieval`) 도구 설정과 켜짐 여부 |

### messages.jsonl

한 줄이 메시지 하나입니다. 아래는 샘플 줄의 모양을 따라 값을 바꾼 만든 예시입니다.

```json
{"completed_at":1767225606,"content":[{"text":{"annotations":[],"value":"예시 답변입니다."},"type":"text"}],"created_at":1767225606,"id":"01KDVDNFZ8Q4W2E7R9T1Y3V5X6","metadata":{"model":"Example-1B-Instruct","token_speed":120.5},"object":"thread.message","role":"assistant","status":"completed","thread_id":"01KDVDNA3VABCDEFGHJKMNPQRS"}
```

| 칸 | 뜻 |
|---|---|
| `id`, `thread_id` | 메시지 ID, 속한 스레드 ID |
| `role` | `user` 또는 `assistant` |
| `content[].text.value` | 본문(`content[].type` 이 `text` 일 때) |
| `created_at`, `completed_at` | Unix 초 |
| `metadata.model` | 답한 모델 이름(사용자 메시지는 `metadata` 가 비어 있음) |
| `metadata.token_speed` | 답을 만든 속도 |
| `status` | 샘플은 모두 `completed` |

샘플의 스레드 넷 가운데 메시지를 하나도 보내지 않은 `New Thread` 스레드에는 `messages.jsonl` 이 없고 `thread.json` 만 있습니다[2].

### cortex.db

SQLite 3 파일이고 샘플의 `schema_version` 은 3입니다. 읽는 법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html)를 따릅니다. 샘플 스키마는 다음과 같습니다[2].

| 표 | 칸 | 쓸모 |
|---|---|---|
| `engines` | `id`, `engine_name`, `type`, `api_key`, `url`, `version`, `variant`, `status`, `metadata`, `date_created`, `date_updated` | 클라우드 서비스별 API 키. 샘플에는 `anthropic`, `openai`, `groq` 등 10행이 있고 키는 `openai` 행에만 들어 있음 |
| `models` | `model_id`, `author_repo_id`, `branch_name`, `path_to_model_yaml`, `model_alias`, `model_format`, `model_source`, `status`, `engine`, `metadata` | 모델 목록. `status` 가 `downloaded` 인 행만 받은 모델이고, `downloadable` 은 허브 목록, `remote` 는 클라우드 모델 |
| `files` | `id`, `object`, `purpose`, `filename`, `created_at`, `bytes` | 샘플은 빈 표 |
| `hardware` | `uuid`, `type`, `hardware_id`, `software_id`, `activated`, `priority` | GPU 항목 |

샘플의 `models` 표는 115행이지만 `status` 가 `downloaded` 인 행은 `llama3.2-1b-instruct` 와 `cogito-v1:3b` 두 개뿐입니다. 로그의 `Adding model to db: {모델}` 줄도 허브 목록을 표에 채우는 기록이라 받기 기록이 아닙니다[2].

### cortex.log

줄 모양은 `YYYYMMDD HH:MM:SS.ffffff UTC {PID} {수준} [{태그}] {메시지} - {소스 파일}:{줄}` 이고, 태그가 없는 줄도 많습니다. 요청 본문처럼 여러 줄로 이어지는 메시지는 JSON 이 끝난 뒤 ` - server.cc:52` 같은 소스 표시가 따로 한 줄에 옵니다. 샘플에 나오는 줄 종류는 아래와 같습니다[2]. 표의 `{ }` 는 값이 들어가는 자리입니다.

| 사건 | 줄 모양(샘플) |
|---|---|
| 엔진 시작 | `Host: 127.0.0.1 Port: 39291`, `cortex.cpp version: v1.0.12 - main.cc:135` |
| 모델 받기 시작 | `Handle model input, model handle: {URL 또는 모델 이름} - models.cc:55`, `{폴더} successfully created! - file_manager_utils.cc:277`, `Task added to queue: {모델} - download_service.cc:492` |
| 파일 받기 끝 | `Transfer completed for URL: {URL} - download_service.cc:42` |
| 모델 적재 | `llama_model_loader: loaded meta data with ... from {GGUF 경로}`, `Model loaded successfully: {모델} - llama_engine.cc:421` |
| 클라우드 모델 적재 | `[LoadModelConfig] LoadModelConfig successfully: {모델}, {YAML 경로}`, `Model loaded successfully: {모델} - remote_engine.cc:473` |
| API 키 | `[LoadModel] header: Authorization: Bearer {키 평문} - remote_engine.cc:449` |
| 키 없음 | `api_key is empty - engine_service.cc:{줄}` |
| 대화 요청 | `[ChatCompletion] Start chat completion`, `[ChatCompletion] request body: {` 뒤에 JSON(`engine`, `model`, `messages[]`, 추론 설정) |
| 클라우드 호출 주소 | `[MakeStreamingChatCompletionRequest] full_url: https://api.openai.com/v1/chat/completions` |
| 답 조각 | `[operator ()] data: data: {...}`(로컬·클라우드 모두), `[StreamWriteCallback] data: {...}`(클라우드만). 조각마다 `created`(Unix 초)와 `delta.content` |
| 메시지 저장 | `CreateMessage for thread {스레드 ID} - message_fs_repository.cc:15` |
| 스레드 지우기 | `DeleteThread: {스레드 ID} - thread_fs_repository.cc:179` |
| 모델 지우기 | `Removed metadata for model {모델} - model_service.cc:973`, `Removed: {YAML 경로} - model_service.cc:718` |

요청 본문의 `messages[]` 에는 그때까지의 앞선 대화(사용자 말과 모델 답)가 함께 들어갑니다. 샘플에서는 로컬 모델과 클라우드 모델 모두 답이 조각 단위로 로그에 남았습니다. 로컬 모델 조각의 `model` 값은 `_` 이고, 클라우드 쪽 `StreamWriteCallback` 조각에는 서버가 돌려준 세부 모델 이름(예: `gpt-3.5-turbo-0125`)이 들어 있습니다[2].

### Local Storage(LevelDB)

앱 화면이 쓰는 저장소이고 원본(origin)은 `file://` 입니다. 샘플 파일에서 읽히는 키는 `threadList`, `threadStates`, `chatMessages`, `currentThreadMessages`, `downloadedModels`, `availableModels`, `last-used-model-id`, `activeAssistant` 입니다[2]. `.ldb` 파일의 블록은 압축되어 있을 수 있고, 샘플의 `000040.log` 에서 `llama3.2:1b` 는 UTF-16LE 로만 들어 있습니다[2]. 한 가지 문자열 검색만으로는 빠지는 값이 있으므로, [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html)와 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)의 방법으로 풀어 읽습니다.

## 증거로서 의미

**증명하는 것**

- 어느 모델을 언제 받았는지. `cortex.log` 의 받기 줄에는 시각, 모델 이름, 받은 URL, 저장한 폴더가 남고, LangurTrace 시험에서 지운 모델 5개의 받기 기록이 모두 나왔습니다[1, §5.3, 표 8].
- 어떤 대화를 언제 어느 모델로 나눴는지. `messages.jsonl` 과 `cortex.log` 요청 본문이 서로 받쳐 줍니다. LangurTrace 시험에서 앱 화면으로 지운 대화 50건이 모두 `cortex.log` 에서 나왔습니다[1, §5.3, 표 8].
- 클라우드 서비스 API 키를 등록해 썼는지. `cortex.db` 의 `engines.api_key` 와 `cortex.log` 의 `Authorization` 줄에 남습니다[1, §4.6.3, 부록 B].
- 스레드와 모델을 지운 사실과 그 시각. 샘플의 `DeleteThread`, `Removed` 줄이 그 예입니다[2].

**증명하지 못하는 것**

- 사람이 직접 친 글인지. 요청 본문에는 앱이 만든 요청도 섞입니다. 샘플에는 첫 메시지를 받은 뒤 앱이 보낸 `Summarize in a 10-word Title. Give the title only. Here is the message: ...` 요청이 있는데, 대화 이름을 짓는 요청입니다[2].
- 누가 앱을 썼는지. 기록은 Windows 사용자 프로필 단위입니다.
- 올린 파일이나 생성 파일. Jan 에는 파일을 올리거나 생성하는 기능이 없습니다[1, 표 5·8]. 샘플의 `cortex.db` `files` 표도 비어 있습니다[2].
- 클라우드 서버 쪽 기록. 서버에 남은 자료는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 절차로 확인합니다. API 키는 서비스 회사에 서버 쪽 자료를 요청할 때 단서로 쓸 수 있습니다[1, §4.3].

보고서에는 "2025-04-16 16:25(UTC)에 Jan 엔진이 `llama3.2-1b-instruct` 모델로 이 문장을 담은 대화 요청을 처리한 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

| 기록 | 형식 | 시간대 |
|---|---|---|
| `cortex.log` 줄 머리 | `YYYYMMDD HH:MM:SS.ffffff` 뒤에 `UTC` | UTC. 샘플 줄 6,879개 모두 마이크로초 뒤 세 자리가 `000` 이라 실제로는 밀리초 단위 |
| `thread.json` `created_at` | Unix 초 | UTC 기준 |
| `thread.json` `metadata.updated_at` | Unix 밀리초 | UTC 기준 |
| `messages.jsonl` `created_at`, `completed_at` | Unix 초 | UTC 기준 |
| 답 조각의 `created` | Unix 초 | UTC 기준 |
| `cortex.db` `engines.date_created`, `date_updated` | `YYYY-MM-DD HH:MM:SS` 텍스트, 스키마 기본값 `CURRENT_TIMESTAMP` | 샘플 값이 클라우드 모델 YAML 의 `created: 1739975265`(2025-02-19 14:27:45 UTC)와 같음 |

샘플에서 `messages.jsonl` 의 사용자 메시지 `created_at` 1744820618 은 2025-04-16 16:23:38 UTC 이고, `cortex.log` 의 같은 대화 요청 줄도 `20250416 16:23:38.444000 UTC` 입니다[2]. 두 기록은 시간대를 바꾸지 않고 그대로 맞춰 보면 됩니다.

스레드 ID 와 메시지 ID 는 26자 ULID 모양이고, 앞 10자가 밀리초 시각입니다. 샘플 스레드 `01JRZPM67W51V8N4CVD6RK77H0` 의 앞 10자를 Crockford base32 로 풀면 1744820639996 이 나오고, 이 값은 같은 스레드의 `created_at` 1744820639 와 초 단위까지 같습니다[2]. 그래서 파일이 지워지고 로그의 `DeleteThread: {스레드 ID}` 줄만 남아도 그 스레드를 만든 때를 ID 로 알 수 있습니다.

`engines` 표의 두 시각은 키를 넣은 때가 아닙니다. 샘플에서는 10행 모두 `date_created` 가 2025-02-19 14:27:45, `date_updated` 가 2025-04-16 14:01:39 로 같고, `date_updated` 는 엔진이 v1.0.12 로 다시 뜬 직후(`cortex.log` 14:01:38)와 겹칩니다[2]. 키를 처음 쓴 때는 `cortex.log` 의 첫 `Authorization` 줄로 잡습니다.

## 함정과 한계

- **판이 바뀌면 이 페이지가 맞지 않을 수 있음.** Jan 새 판은 저장 형식을 바꿨다는 보고가 있습니다[3]. 검체의 판부터 확인합니다.
- **`thread.json` 의 모델은 메시지마다 쓴 모델이 아님.** 샘플 스레드 `hello, gpt` 는 `assistants[].model.id` 가 `llama3.2-1b-instruct` 이지만 그 안의 답은 모두 `metadata.model` 이 `gpt-3.5-turbo` 입니다[2]. 메시지마다 `metadata.model` 을 봅니다.
- **`models` 표는 받은 모델 목록이 아님.** `status` 로 걸러야 합니다. 지운 모델은 표에서 빠지므로 `cortex.log` 받기 줄과 Local Storage 의 `downloadedModels` 를 함께 봅니다. 샘플에서 지운 `gemma2:2b`, `llama3.2:1b` 는 표에 없지만 Local Storage 파일에 이름이 남아 있습니다[2].
- **로그의 모델 이름.** `general.name` 이 `Hf` 처럼 뜻 없는 값으로 찍힌 모델이 있습니다. 이럴 때는 `general.base_model.0.repo_url` 줄을 봅니다[2]. 자세한 방법은 [로컬 모델 파일](model-files.md)에 있습니다.
- **API 키와 대화가 로그에 평문으로 남음.** 보고서와 도구 출력에서 키 값을 가립니다. 키가 남는 곳과 다루는 원칙은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)을 따릅니다. LangurTrace 의 `model_configuration.xlsx` 는 `engines` 표를 `api_key` 칸까지 그대로 옮기고, `verbose_log_parsed.xlsx` 의 `Configurations` 시트에도 `Authorization` 줄이 들어갑니다[2].
- **LangurTrace 로그 출력의 모양.** `log_reporter.py` 는 `[태그]` 와 ` - 소스` 가 한 줄에 모두 있어야 새 항목으로 읽고, 나머지 줄은 앞 항목에 이어 붙입니다[2]. 그래서 샘플의 `ChatLogs` 시트에서는 대화 요청이 `GetEngineByModelId` 태그 항목의 메시지 칸에 붙어 나오고, 태그가 없는 받기 줄·`DeleteThread` 줄·`Removed` 줄은 따로 한 행이 되지 않습니다. 지운 흔적은 원본 `cortex.log` 를 직접 검색해 확인합니다.
- **LangurTrace 의 다른 출력.** `conversation_reporter.py` 는 `messages.jsonl` 만 읽고 `thread.json` 은 건너뛰며, 시각을 분석 PC 의 현지 시각으로 바꿔 첫 메시지의 분 단위 시각을 HTML 파일 이름으로 씁니다[2]. 샘플 출력 `2025-04-17_01-23.html` 은 1744820618 을 UTC+9 로 바꾼 이름입니다. 같은 분에 시작한 스레드가 둘이면 파일 이름이 겹칩니다. `model_reporter.py` 는 YAML 줄을 `:` 로 나눈 둘째 조각만 씁니다. 그래서 샘플 `model_metadata.csv` 에는 `cogito-v1:3b` 가 ` cogito-v1` 로 잘려 있고, Hugging Face 모델 행에는 값 뒤의 YAML 주석(`# metadata.general.name` 등)이 붙은 채로 들어 있습니다[2].
- **디스크 복구만 잰 수치.** 표 8 은 앱 화면으로 지운 뒤 디스크에 남은 것만 쟀고, 볼륨 섀도 복사본, 메모리, SQLite 여유 공간 복구는 시험하지 않았습니다[1, §6.2].

## 직접 분석해 보기

**헥스와 손으로 한 번.** `cortex.db` 는 첫 16바이트가 `53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00`(글자로 `SQLite format 3` 과 NUL)인지 헥스 보기로 확인한 뒤 SQLite 도구로 엽니다. 켜진 앱에서 복사했다면 같은 폴더의 `-wal`, `-shm` 파일도 함께 옮깁니다. 스레드 ID 의 시각은 손으로 풀 수 있습니다. 아래는 만든 예시입니다.

```text
스레드 ID(만든 예시): 01KDVDNA3VABCDEFGHJKMNPQRS
앞 10자: 0 1 K D V D N A 3 V
Crockford base32 값: 0 1 19 13 27 13 21 10 3 27
32진수로 계산: 1767225600123 ms = 2026-01-01 00:00:00.123 UTC
```

Crockford base32 는 `0123456789ABCDEFGHJKMNPQRSTVWXYZ` 순서로 값을 매기고 I, L, O, U 를 쓰지 않습니다. 이렇게 푼 값이 `thread.json` 의 `created_at` 과 초 단위까지 같은지 봅니다.

**로그를 직접 한 번.** `cortex.log` 를 텍스트 편집기나 `grep` 으로 열어 아래 순서로 찾습니다.

1. `cortex.cpp version` 과 `Host:` 줄로 엔진을 띄운 때와 판을 나열합니다.
2. `model handle`, `Task added to queue`, `Transfer completed for URL`, `Removed` 로 모델을 받고 지운 흐름을 세웁니다.
3. `request body` 뒤 JSON 의 `model` 과 `messages[]` 를 읽고, 같은 시각의 `messages.jsonl` 줄과 맞춥니다. `messages.jsonl` 에 없는 요청은 지운 대화이거나 앱이 보낸 이름 짓기 요청입니다.
4. `DeleteThread` 줄의 스레드 ID 를 `threads` 폴더와 대조해, 폴더가 없는 ID 는 앞 10자를 풀어 만든 시각을 구합니다.

**공개 도구로 한 번.** LangurTrace 는 KAPE 타깃 `Jan.tkape` 로 모으고 모듈 `Jan.mkape` 로 `LangurTrace.exe --src %sourceDirectory% --dst %destinationDirectory% --app jan` 을 돌립니다[2]. 출력은 `model_metadata.csv`(모델 YAML), `model_configuration.xlsx`(`cortex.db` 의 `engines`·`models` 표), `conversations\*.html`(스레드별 대화), `verbose_log_parsed.xlsx`(시트 `ChatLogs`·`Configurations`)입니다[1, §5.2][2]. Local Storage 는 모으기만 하고 파싱하지 않습니다[1, §5.1]. 도구 출력은 위 "함정과 한계" 의 모양을 알고 읽고, 지운 흔적은 원본 로그로 다시 확인합니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| `messages.jsonl` ↔ `cortex.log` 요청 본문 | 시각(둘 다 UTC)과 본문. 로그에만 있는 요청은 지운 대화 후보 |
| `thread.json` ↔ `cortex.log` `CreateMessage`·`DeleteThread` | 스레드 ID 와 시각 |
| `cortex.db` `models`(`status`) ↔ 모델 폴더 ↔ `cortex.log` 받기 줄 | 남은 모델과 지운 모델 |
| `engines.api_key` ↔ `cortex.log` `Authorization` 줄 ↔ `api.openai.com` 같은 호출 주소 | 어느 서비스를 키로 썼는지. 네트워크 쪽은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) |
| 모델 YAML ↔ GGUF 헤더 ↔ 로그의 `llama_model_loader` 줄 | 모델 이름과 출처 URL. [로컬 모델 파일](model-files.md) |

여러 앱의 기록을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 실습

공개 검체는 LangurTrace 저장소의 `sample_dataset` 입니다. `sample_dataset/collect/C/Users/USER/AppData/Roaming/Jan/` 에 모은 원본이, `sample_dataset/parse/LLM application artifacts/jan/` 에 LangurTrace 출력이 있습니다[2]. GGUF 모델 파일은 크기 때문에 빠져 있습니다.

1. `threads` 폴더의 스레드는 넷입니다. `cortex.log` 의 `DeleteThread` 줄에 나오는 스레드 ID 는 무엇이고, 그 스레드를 만든 시각은 ID 로 풀면 언제입니까?
2. 지운 스레드에서 사용자가 보낸 문장은 `cortex.log` 의 어느 요청 본문에 남아 있습니까? 그 가운데 앱이 보낸 이름 짓기 요청은 무엇입니까?
3. `cortex.db` `models` 표에서 `status` 가 `downloaded` 인 모델과, `cortex.log` 에서 받았다가 지운 모델을 나눠 적어 보십시오.
4. 스레드 `hello, gpt` 의 `thread.json` 모델과 `messages.jsonl` 의 `metadata.model` 은 어떻게 다릅니까?
5. LangurTrace 의 `conversations` 폴더 HTML 파일 이름의 시각은 `messages.jsonl` 의 `created_at` 과 몇 시간 차이가 납니까? 왜 그렇습니까?
6. API 키가 남은 곳을 모두 찾되, 답에는 키 값을 가리고 위치만 적으십시오.

## 참고 문헌

1. Jeong, S., Lee, S., Park, J., "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. https://doi.org/10.1016/j.fsidi.2025.301987 (§3.3, §3.4, §4.1, §4.3, §4.6.3, §5.1–5.3, §6.2, 표 1, 표 5, 표 8, 그림 5, 부록 A·B)
2. jeongramon/LangurTrace, https://github.com/jeongramon/LangurTrace — `src/apps/jan.py`, `src/reporter/jan/reporter.py`, `src/reporter/jan/configuration_reporter.py`, `src/reporter/jan/conversation_reporter.py`, `src/reporter/jan/log_reporter.py`, `src/reporter/jan/model_reporter.py`, `dist/Targets/LLMApplications/Jan.tkape`, `dist/Modules/LLMApplications/Jan.mkape`, `sample_dataset/collect/C/Users/USER/AppData/Roaming/Jan/`, `sample_dataset/parse/LLM application artifacts/jan/`
3. k0w4lzk1/LangurTrace-Implementation, https://github.com/k0w4lzk1/LangurTrace-Implementation — `GAPS.md`(G1, 2026-05-08 커밋). LangurTrace 원저자와 다른 사람이 올린 저장소입니다.
