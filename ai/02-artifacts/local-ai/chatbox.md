---
title: "Chatbox"
parent: "아티팩트 · 로컬 AI"
nav_order: 700
---

# Chatbox (Chatbox)

Chatbox 는 Ollama·LM Studio 같은 로컬 백엔드나 클라우드 API 에 붙여 쓰는 대화 화면 앱이고, 대화 본문·시스템 프롬프트·메시지별 모델·API 키가 `%AppData%\xyz.chatboxapp.app\config.json` 과 그 백업 파일에, 올린 이미지와 만든 이미지가 `chatbox-blobs` 폴더에 남습니다.

논문은 Windows 11 Pro 24H2 에서 Chatbox 1.11.8 을 시험했습니다[1]. 1.12.0 부터 대화 저장 형식이, 1.16.1 부터 대화 저장 위치가 바뀌었으니 분석 대상 앱의 판을 먼저 적습니다.

## 무엇을 기록하나 · 왜 생기나

로컬 LLM 환경은 백엔드 런타임, 클라이언트 화면, 통합형으로 나뉘고, Chatbox 는 클라이언트 화면 앱입니다[1, §3.2, 표 1]. 모델도 백엔드도 대화 문맥을 스스로 들고 있지 않아서, 클라이언트 앱이 대화를 저장해 두었다가 요청할 때마다 다시 보냅니다[1, §4.4]. 그래서 로컬 LLM 환경에서 가장 중요한 증거는 클라이언트 화면 앱에서 나옵니다[1, §4.5]. 백엔드 쪽 흔적은 [Ollama](ollama.md)와 [LM Studio](lm-studio.md)에서, 분류 전체의 틀은 [로컬 AI](index.md)에서 다룹니다.

클라우드 모델을 API 키로 쓸 때도 대화 기록은 로컬 앱에 남습니다. API 호출은 대개 상태를 남기지 않아서, 로컬 앱이 대화 기록을 들고 있다가 호출할 때마다 함께 보내고 클라우드 쪽은 이 문맥을 대개 보관하지 않습니다[1, §3.4]. 같은 계정이라도 브라우저로 쓴 대화와 API 키로 쓴 대화는 따로 관리되므로, Chatbox 로 쓴 클라우드 대화는 서비스 회사 쪽보다 이 PC 에서 먼저 찾습니다. 서버와 기기 가운데 어디에 데이터가 남는지의 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

Chatbox 의 주요 아티팩트는 여섯 가지입니다[1, 표 4].

| 아티팩트 | 형식 | 담긴 것 |
|---|---|---|
| `config.json` | JSON | 대화 세션, API 키 |
| 올린 파일 | base64 로 바꾼 글자 | 사용자가 올린 파일 |
| 만든 파일 | base64 로 바꾼 글자 | 모델이 만든 파일 |
| 메인 로그 | 텍스트 | 백업·업데이트 기록 |
| API 캐시 | 크롬 캐시 | API 호출에 대한 응답 |
| 모델 목록 | LevelDB | 제공자별 모델 목록 |

이 가운데 가장 중요한 것은 `config.json` 이고, 그다음이 올린 파일과 만든 파일입니다[1, §4.5]. 만든 파일은 아동 성착취물 같은 불법 콘텐츠를 만들거나 퍼뜨린 사건에서 직접 증거가 될 수 있습니다[1, §4.3].

## 위치와 버전별 차이

### Windows 경로

논문 부록 A 와 LangurTrace KAPE 타깃[3], 공개 샘플[4]을 합친 표입니다. `config.json`, 백업 파일, `chatbox-blobs` 는 모두 Electron 이 앱마다 정하는 사용자 데이터 폴더(`userData`) 아래에 만들어집니다[5, `store-node.ts`].

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%AppData%\xyz.chatboxapp.app\config.json` | 설정, API 키, 대화(1.16.0 까지) | 논문, 타깃 |
| `%AppData%\xyz.chatboxapp.app\config-backup-{UTC 시각}.json` | `config.json` 의 자동 백업 | 타깃, 샘플, 소스 |
| `%AppData%\xyz.chatboxapp.app\chatbox-blobs\{type}input{filename}` | 올린 파일 | 논문 |
| `%AppData%\xyz.chatboxapp.app\chatbox-blobs\{type}{filename}` | 만든 파일 | 논문 |
| `%AppData%\xyz.chatboxapp.app\chatbox-blobs\parseFile-{UUID}` | 올린 문서에서 뽑은 글(1.11.8) | 소스, LangurTrace 코드 |
| `%AppData%\xyz.chatboxapp.app\logs\main.log` | 백업·업데이트 기록 | 논문, 타깃, 샘플 |
| `%AppData%\xyz.chatboxapp.app\Cache\Cache_Data` | 모델 목록 API 응답 | 논문 |
| `%AppData%\xyz.chatboxapp.app\Cache\CacheData\` | 같은 캐시(타깃이 적은 이름) | 타깃 |
| `%LocalAppData%\xyz.chatboxapp.app-updater\pending\` | 받아 둔 업데이트 설치 파일 | 샘플 `main.log` |

API 캐시 폴더 이름은 논문이 `Cache_Data`, KAPE 타깃이 `CacheData` 로 서로 다르게 적었습니다[1, 부록 A][3]. 타깃 경로가 실제 폴더와 다르면 캐시가 수집되지 않으므로, 분석 대상 기기에서 폴더 이름을 먼저 보고 수집 경로를 맞춥니다. 모델 목록 LevelDB 는 공개된 경로가 없고 KAPE 타깃도 모으지 않습니다[1, 부록 A][3]. 기기의 `xyz.chatboxapp.app` 폴더 아래에서 LevelDB 폴더를 찾아 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)의 방법으로 읽습니다.

공개된 시험은 Windows 만 다룹니다. 다른 운영체제에서는 형식과 저장 위치가 다를 수 있어도 아티팩트 종류는 크게 다르지 않으리라는 추정이 있습니다[1, §6.2]. macOS·Linux 에서는 Electron 사용자 데이터 폴더를 찾으면 같은 파일이 있는지 볼 수 있습니다. 사용자 데이터 폴더의 위치와 Electron 앱 공통 구조는 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)에서 다룹니다.

### 판에 따른 대화 저장 위치

데스크톱 판의 저장 방식은 아래처럼 바뀌었습니다[6, `docs/storage.md`]. 설정(`settings`, `configs`, `configVersion`)은 어느 판에서도 파일에 남고, 바뀐 것은 대화 세션입니다. 세션 데이터의 키는 `chat-sessions-list`, `session:*` 입니다.

| 앱 판 | `configVersion` | 데스크톱 판의 대화 세션 |
|---|---|---|
| 1.9.8~1.9.10 | 0~5 | 모두 파일(`config.json`) |
| 1.9.11 | 6~7 | 바뀜 없음(파일) |
| 1.12.0 | 7~8 | 파일. 세션 형식이 세션 목록(session-list) 방식으로 바뀜 |
| 1.13.1 | 9~10 | 제공자·세션 설정 구조 바뀜 |
| 1.16.1 | 11~12 | 대화 세션을 IndexedDB 로 옮기고 설정은 파일에 둠 |
| 1.19.0 | 13~14 | 이미지 생성 기록을 IndexedDB 의 독립 기록으로 옮김 |
| 1.21.0 | 14~15 | 세션 메타데이터를 목록 하나에서 세션별 기록으로 나눔 |

논문과 공개 샘플은 1.11.x 판이라 대화가 `config.json` 의 `chat-sessions` 키 하나에 모두 들어 있습니다. 공개 샘플의 `main.log` 에도 1.12.3 업데이트를 찾아 받아 둔 줄이 있어서, 수집 시점에 설치된 판은 그보다 앞섭니다[4]. 1.16.1 부터 대화는 Electron 앱의 IndexedDB 에 있으므로 `config.json` 만 모아서는 대화가 빠집니다. 분석 대상 앱의 판은 `config.json` 의 `configVersion` 과 `main.log` 의 업데이트 줄로 추정합니다.

### 백업 파일을 남기고 지우는 규칙

Chatbox 는 `config.json` 을 10분마다 같은 폴더에 `config-backup-{UTC ISO 시각}.json` 으로 복사합니다. 시각의 `:` 은 `_` 로 바꿔 파일 이름에 넣습니다(예: `config-backup-2025-05-23T11_36_10.169Z.json`)[5][6, `store-node.ts`]. 마지막 백업이 10분 안에 있으면 건너뛰고, `config.json` 이 없거나 JSON 으로 읽히지 않아도 건너뜁니다. PC 가 절전에 들어가면 타이머를 멈췄다가 깨어나면 다시 10분을 셉니다. 백업마다 오래된 백업을 정리하는데, 판에 따라 규칙이 다릅니다.

| 소스 시점 | 정리 규칙 | 로그 |
|---|---|---|
| 1.11.8(커밋 `97d32f92`, 2025-04-10) | 최근 50개만 남기고 나머지를 지움 | 지울 때마다 `store-node: clear backup: {파일 이름}` |
| main(커밋 `19de00fb`, 2026-06-10) | 오늘·어제 것은 한 시간에 마지막 하나, 그저께부터 30일 전까지는 하루에 마지막 하나를 남기고, 30일이 지난 것은 지움 | `Clearing N old backup(s)...` 한 줄 |

1.11.8 규칙대로면 앱을 켜 둔 시간으로 대략 8시간 20분(50 × 10분) 앞까지의 백업만 남습니다.

## 구조

### `config.json` 최상위

공개 샘플의 백업 두 파일은 최상위 키가 같습니다[4].

| 키 | 담긴 것 |
|---|---|
| `settings` | 제공자·모델, API 키, 서버 주소, 기본 프롬프트, 화면 설정 |
| `chat-sessions` | 대화 세션 목록(1.11.x) |
| `configs` | `uuid` 하나 |
| `configVersion` | 저장 형식 판(샘플 `7`) |
| `remoteConfig` | 샘플에서는 빈 객체 |
| `windowState` | 창 크기·위치 |

`settings` 에는 API 키, 등록한 로컬·클라우드 모델, 기본 프롬프트가 들어가고, `chat-sessions` 에는 세션마다 메타데이터, 시스템 프롬프트, 고른 모델, 대화 기록이 들어갑니다[1, §4.5, 그림 3].

### `settings` 의 연결 설정과 API 키

샘플 `settings` 에서 조사에 쓰는 키입니다[4]. 1.11.8 의 설정 형식에는 Chatbox 자체 서비스(Chatbox AI)의 라이선스 키 `licenseKey` 도 있습니다[5, `types.ts`].

| 무리 | 키 |
|---|---|
| 지금 고른 제공자·모델 | `aiProvider`, `model`, `claudeModel`, `geminiModel`, `ollamaModel`, `lmStudioModel`, `groqModel`, `deepseekModel`, `siliconCloudModel`, `perplexityModel`, `xAIModel` |
| 서버 주소 | `apiHost`(샘플 `https://api.openai.com`), `claudeApiHost`, `geminiAPIHost`, `ollamaHost`(샘플 `http://127.0.0.1:11434`), `lmStudioHost`(샘플 `http://127.0.0.1:1234/v1`), `azureEndpoint` |
| API 키 | `openaiKey`, `claudeApiKey`, `geminiAPIKey`, `groqAPIKey`, `deepseekAPIKey`, `siliconCloudKey`, `perplexityApiKey`, `xAIKey`, `azureApikey`, `extension.webSearch.tavilyApiKey` |
| 사용자가 더한 제공자 | `customProviders`(샘플에서는 빈 목록) |
| 프롬프트·생성 설정 | `defaultPrompt`(샘플 `You are a helpful assistant.`), `temperature`, `topP`, `dalleStyle`, `imageGenerateNum` |

API 키는 평문 문자열로 들어갑니다. 샘플에서는 `openaiKey` 에만 값이 있고 나머지 키는 빈 문자열이었습니다[4]. 이런 API 키는 그 자체로는 증거 가치가 크지 않아도, 서비스 회사에 서버 쪽 자료를 요청할 때 넘길 수 있습니다[1, §4.3]. 키 값은 보고서와 공유 자료에서 가리고, 어느 키 이름에 값이 있었는지와 파일 시각만 적습니다. 서비스 회사에 자료를 요청하는 절차는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)을, 키와 토큰을 다루는 기준은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)을 따릅니다.

`ollamaHost`, `lmStudioHost` 는 기본값으로도 들어가므로 값이 있다고 그 백엔드를 썼다고 보지 않습니다. 실제로 쓴 백엔드는 메시지별 `aiProvider`·`model` 로 봅니다.

### 대화 세션(`chat-sessions[]`)

| 키 | 담긴 것 | 근거 |
|---|---|---|
| `id` | 세션 UUID | 샘플 |
| `name` | 세션 이름 | 샘플 |
| `threadName` | 지금 주제 이름. 샘플에서 `name` 과 다른 세션이 있음 | 샘플 |
| `type` | `chat` 또는 `picture`(이미지 만들기 세션). 없으면 옛 판의 `chat` | 샘플, 소스 |
| `settings` | 세션마다 따로 고른 모델(샘플 `{"ollamaModel": "gemma3:1b"}`, `{"model": "gpt-3.5-turbo"}`) | 샘플 |
| `messages` | 지금 주제의 메시지 | 샘플 |
| `threads[]` | 앞선 주제 목록(`id`, `name`, `messages`, `createdAt`) | 소스 |
| `messageForksHash` | 다시 만든 답 같은 분기 메시지(`lists[].messages`, `createdAt`) | 샘플, 소스 |

`threads` 와 `messageForksHash` 는 1.11.8 의 세션 형식에 있는 키입니다[5, `types.ts`]. 사용자가 새 주제를 시작하거나 답을 다시 만들면 앞선 메시지가 여기로 옮겨지므로, `messages` 만 보면 대화 일부가 빠집니다. 샘플에서는 `messageForksHash` 가 있는 세션마다 빈 객체였습니다[4].

### 메시지(`messages[]`)

| 키 | 담긴 것 |
|---|---|
| `id` | 메시지 UUID |
| `role` | `system`, `user`, `assistant` |
| `contentParts[]` | `type` 이 `text` 면 `text` 필드에 본문, `image` 면 `storageKey` 필드에 blob 키 |
| `timestamp` | Unix 밀리초 |
| `aiProvider` | 답한 제공자(샘플 `ollama`, `openai`) |
| `model` | 답한 모델(샘플 `Ollama (llama3.2:latest)`, `OpenAI API (gpt-4o)`, `OpenAI API (DALL-E-3)`) |
| `style` | 이미지 스타일(샘플 `vivid`) |
| `wordCount`, `tokenCount` | 이 메시지의 단어 수와 토큰 수 |
| `tokensUsed` | 이 답을 만드는 데 쓴 토큰 수 |
| `firstTokenLatency` | 요청부터 첫 글자가 올 때까지 걸린 밀리초 |
| `generating`, `status`, `toolCalls` | 생성 중 여부, 파일 보내기·웹 페이지 읽기 상태, 도구 호출 |
| `files[]` | 올린 문서(`id`, `name`, `fileType`, `storageKey`, `chatboxAIFileUUID`) |
| `links[]` | 넣은 웹 주소(`id`, `url`, `title`, `storageKey`) |

`files[]` 와 `links[]` 는 1.11.8 소스의 메시지 형식에만 있고 공개 샘플에는 나오지 않습니다[5]. 샘플의 `chat` 세션은 하나를 빼고 첫 메시지가 `role` 이 `system` 인 시스템 프롬프트였고, 그 본문이 `settings.defaultPrompt` 와 같았습니다. `picture` 세션의 첫 `system` 메시지는 앱이 넣는 이미지 생성 안내문이었습니다[4]. 답마다 그때 쓴 모델이 함께 기록됩니다[1, §4.5].

모양을 보여 주려고 만든 예시입니다. ID·시각·본문은 지어낸 값입니다.

```json
{
  "id": "0b7c1e52-3f4a-4c1d-9a6e-2d8f5b1c7e90",
  "name": "Sample Session",
  "threadName": "Sample Session",
  "type": "chat",
  "settings": {"ollamaModel": "sample-model:1b"},
  "messageForksHash": {},
  "messages": [
    {"id": "5a1d…", "role": "system",
     "contentParts": [{"type": "text", "text": "You are a helpful assistant."}],
     "timestamp": 1773446700000},
    {"id": "8e2f…", "role": "user",
     "contentParts": [{"type": "text", "text": "예시 질문입니다."},
                      {"type": "image", "storageKey": "picture:input-box:1c9e…"}],
     "timestamp": 1773446712345, "wordCount": 2, "tokenCount": 9},
    {"id": "c47a…", "role": "assistant",
     "contentParts": [{"type": "text", "text": "예시 답입니다."}],
     "timestamp": 1773446718901, "aiProvider": "ollama",
     "model": "Ollama (sample-model:1b)", "tokensUsed": 42,
     "firstTokenLatency": 310, "generating": false}
  ]
}
```

### `chatbox-blobs` 의 이름과 내용

blob 파일 이름은 메시지의 `storageKey` 에서 파일 이름에 못 쓰는 글자(`:`)를 뺀 값입니다[5][6, `store-node.ts`]. 그래서 blob 이름으로 어느 세션·메시지의 파일인지 거꾸로 찾을 수 있습니다.

| 종류 | `storageKey` | blob 파일 이름 | 내용(샘플) |
|---|---|---|---|
| 올린 이미지 | `picture:input-box:{UUID}` | `pictureinput-box{UUID}` | `data:image/png;base64,` 로 시작하는 Data URL |
| 만든 이미지 | `picture:{세션 ID}:{메시지 ID}:{UUID}` | `picture{세션 ID}{메시지 ID}{UUID}` | 머리말 없는 base64 |
| 올린 문서 | `parseFile-{UUID}` | 같음 | 문서에서 뽑은 글(1.11.8 소스) |

만든 이미지는 한 번에 여러 장이 나오면 세션 ID 와 메시지 ID 가 같고 마지막 UUID 만 다릅니다. 샘플의 `picture` 세션에는 `OpenAI API (DALL-E-3)` 답 하나에 blob 세 개가 달려 있고, 이는 `settings.imageGenerateNum` 값 `3` 과 맞습니다[4].

올린 파일과 만든 파일의 인코딩은 출처끼리 다릅니다. 논문(2025)은 올린 파일이 base64 이고 만든 파일이 Data URL 이라고 적었습니다[1, §4.5]. LangurTrace 코드(2025-07)는 반대로 `pictureinput` 로 시작하는 blob 을 Data URL 로 풀어 `uploaded` 에 두고, 그 밖의 `picture` blob 은 머리말 없는 base64 로 풀어 `generated` 에 둡니다[2, `files_reporter.py`]. 공개 샘플의 blob 여섯 개는 코드 쪽 설명대로 풀립니다[4]. 실제 데이터에서는 blob 첫 글자가 `data:` 인지 보고 판단합니다.

올린 문서는 원본이 아니라 뽑은 글만 남습니다. 1.11.8 에서는 제공자가 Chatbox AI 가 아니면 문서에서 글을 뽑아 정해진 토큰 수(첨부 전체 4만 토큰을 첨부 수로 나눈 값)만큼 자른 뒤 `parseFile-{UUID}` blob 으로 저장하고, 메시지 `files[]` 에는 이름·파일 종류·blob 키만 적습니다[5, `sessionActions.ts`, `desktop_platform.ts`]. 제공자가 Chatbox 자체 서비스(Chatbox AI)일 때는 파일을 그 서버에 올리고 `files[].chatboxAIFileUUID` 에 서버 쪽 식별자만 남깁니다[5, `sessionActions.ts`]. 올린 파일과 만든 파일은 대화 기록에 파일 이름과 MIME 종류로만 적힙니다[1, §4.5].

### `main.log`

줄 모양은 `[YYYY-MM-DD HH:MM:SS.mmm] [수준]  메시지` 입니다. 샘플에 나온 줄은 아래와 같습니다[4].

| 줄 | 담긴 것 |
|---|---|
| `store-node: init store, config path: {경로}` | 앱이 뜬 때와 `config.json` 위치 |
| `store-node: skip backup because config.json does not exist.` | 백업할 `config.json` 이 없어 건너뜀 |
| `store-node: backup config to: {경로}`, `store-node: auto backup: {경로}` | 백업 파일을 만든 때와 이름 |
| `Checking for update`, `Found version {판} (url: …)`, `Downloading update from …`, `Update has already been downloaded to {경로}` | 업데이트 확인과 받은 설치 파일 |
| `tray: created` | 알림 영역 아이콘을 만듦 |

샘플 `main.log` 에는 백업을 만든 줄이 일곱 번 있지만 수집본에 남은 백업 파일은 두 개이고 `config.json` 은 없습니다[4]. 로그의 백업 이름 목록은 폴더에 없는 백업 파일을 찾아 되살릴 때 대상 목록이 됩니다.

## 증거로서 의미

**증명하는 것.** `config.json` 이나 백업의 메시지는 그 시각에 그 세션에서 그 본문이 오갔고, 답을 어느 제공자의 어느 모델이 했는지를 보여 줍니다(§4.5). 세션의 `system` 메시지와 `settings.defaultPrompt` 로 사용자가 정한 시스템 프롬프트를 보이고, `settings` 의 API 키 필드로 어느 클라우드 서비스의 키를 등록했는지 보입니다. 만든 이미지 blob 은 모델이 만든 결과물의 사본이고, 올린 이미지 blob 은 사용자가 대화에 넣은 이미지 원본입니다. 논문 실험에서 UI 로 지운 올린 파일 50개와 만든 파일 50개는 모두 blob 으로 되살아났습니다(표 8, 50/50)[1, §5.3]. 백업 여러 개를 비교하면 어느 세션이 두 백업 사이에 없어졌는지 보입니다. 공개 샘플에서는 11:36:10Z 백업에 있던 세션 하나가 11:46:10Z 백업에 없고, 그사이 `picture` 세션 하나가 새로 생겼으며 이름이 `Untitled` 이던 세션 하나에는 새 이름이 붙었습니다[4].

**증명하지 못하는 것.** 지운 대화는 백업에 들어간 것만 되살아납니다. 논문 실험에서 지운 대화 50개 가운데 29개(58%)만 되살아났고, 백업이 규칙적으로 만들어지지 않는 탓이라는 해석이 있습니다[1, 표 8, §5.3]. 두 백업 사이 10분 안에 만들고 지운 대화는 어느 백업에도 없습니다. 올린 문서는 뽑은 글만 남아서 원본 파일의 내용·형식·해시를 이것으로 증명하지 못하고, 파일 이름은 `files[].name` 에서만 읽습니다. blob 이름에는 시각이 없어서, 어느 메시지에도 이어지지 않는 blob 은 대화 안에서 언제 쓰였는지 알 수 없습니다. 공개 샘플의 올린 이미지 blob 세 개 가운데 두 개는 남은 백업 어느 메시지도 가리키지 않습니다[4]. API 키가 있다는 사실만으로 그 키로 대화했다고 쓰지 않고, 메시지의 `aiProvider` 가 그 제공자인 답이 있을 때 그 서비스를 쓴 기록이 있다고 씁니다. 로컬 모델 답이라도 모델 파일이 이 PC 에 있었는지는 백엔드 쪽 기록([Ollama](ollama.md), [로컬 모델 파일](model-files.md))으로 따로 확인합니다.

## 시각 해석

| 값 | 표기 | 시간대 | 바뀌는 때 |
|---|---|---|---|
| 메시지 `timestamp` | Unix 밀리초 | UTC | 메시지를 만들 때 |
| `threads[].createdAt`, `messageForksHash.*.createdAt` | 숫자(소스 형식) | 실제 데이터에서 확인 | 주제·분기를 만들 때 |
| 백업 파일 이름 | `2025-05-23T11_36_10.169Z` | UTC(끝의 `Z`) | 백업할 때 |
| `main.log` 줄 | `[2025-05-23 20:36:10.200]` | 오프셋 없는 현지 시각 | 줄을 쓸 때 |
| blob 파일 | 이름에 시각 없음 | 파일 시스템 시각만 | blob 을 쓸 때 |

샘플에서는 같은 백업의 파일 이름 `11_36_10.169Z` 와 로그 줄 `20:36:10.200` 이 9시간 차이라서, 수집한 PC 가 UTC+9 였다고 읽을 수 있습니다[4]. 로그에는 오프셋이 없으므로 이렇게 백업 이름과 로그 줄을 맞춰 그 PC 의 시간대를 확인합니다. 샘플 답 메시지의 `timestamp` 를 현지 시각으로 바꾸면 Ollama 서버 로그의 대화 요청 줄과 1초 안팎으로 맞습니다([Ollama](ollama.md)의 시각 해석 참고). LangurTrace 는 `timestamp` 를 분석 PC 의 현지 시각으로 바꾸고 오프셋을 적지 않으므로[2, `config_reporter.py`], 출력 시각을 옮겨 쓸 때는 분석 PC 의 시간대를 함께 적습니다.

## 함정과 한계

- **판 차이.** 1.12.0 에서 세션 형식이 세션 목록 방식으로 바뀌었고(세션 키는 `chat-sessions-list`, `session:*`), 1.16.1 부터 세션이 IndexedDB 로 옮겨졌습니다[6, `docs/storage.md`]. LangurTrace 는 `chat-sessions` 키만 읽으므로[2, `config_reporter.py`] 1.12.0 뒤 판에서는 대화를 뽑지 못할 수 있습니다. 백업은 `config.json` 만 복사하므로[6, `store-node.ts`], 1.16.1 뒤 판에서 백업으로 지운 대화를 되살리는 방법이 통하는지는 실제 데이터로 확인해야 합니다.
- **LangurTrace 가 읽지 않는 필드.** 대화 보고서는 세션의 `messages` 만 읽고 `threads[]` 와 `messageForksHash` 는 읽지 않습니다[2]. 올린 문서는 `files[].mimeType` 으로 이미지인지 구분하는데 1.11.8 소스의 필드 이름은 `fileType` 입니다[2][5]. HTML 의 문서 링크는 `.txt` 가 빠진 이름을 가리키므로 `uploaded` 폴더에서 `parseFile-…txt` 를 직접 찾습니다.
- **LangurTrace 의 API 키 표.** `configuration.csv` 는 `settings` 최상위 키 이름에 `key` 가 들어가고 값이 있으면 모두 `API Key` 행으로 냅니다[2]. 그래서 `userAvatarKey`, `defaultAssistantAvatarKey` 처럼 아바타 이미지 키를 담는 필드도 값이 있으면 API 키로 나오고, `extension.webSearch.tavilyApiKey` 처럼 한 단계 안에 든 키는 빠집니다. 이 표의 키 값은 가리지 않은 평문이므로 공유하기 전에 가립니다.
- **HTML 이 덮어써짐.** 대화 HTML 이름은 첫 메시지의 현지 시각과 `threadName`(없으면 세션 ID)으로 만들어서, 여러 백업에 같은 세션이 있으면 같은 이름으로 여러 번 쓰고 마지막에 읽은 파일의 내용만 남습니다[2]. 백업마다 달라진 메시지는 원본 JSON 을 비교해서 봅니다.
- **캐시와 모델 목록.** KAPE 타깃은 API 캐시를 모으지만 보고서에는 넣지 않고, 모델 목록 LevelDB 는 모으지도 않습니다[1, §5.3][3]. 논문 시험에서 API 캐시에는 모델 목록 호출 응답만 나왔고 모든 요청이 저장되지도 않았습니다. LevelDB 에는 지운 항목의 잔재가 남을 때가 있습니다[1, §4.5]. 이 두 곳은 직접 엽니다.
- **복구 범위.** 논문의 복구율은 디스크에 남은 파일을 LangurTrace 로 읽은 결과이고, 볼륨 섀도 복사본과 메모리는 시험 범위에 들지 않았습니다[1, §6.2]. 백업이 정리 규칙에 따라 지워졌다면 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)의 방법으로 지워진 백업 파일을 찾습니다.
- **Chatbox 자체 서비스.** 제공자가 Chatbox AI 면 올린 파일이 Chatbox 서버에 있고 PC 에는 서버 쪽 식별자만 남습니다[5]. 서버 쪽 자료는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 구합니다.

## 직접 분석해 보기

**원본 파일로.** `config.json` 과 모든 `config-backup-*.json` 사본을 모은 뒤, 파일마다 세션 ID·이름·메시지 수를 뽑아 나란히 놓습니다. 아래는 Python 표준 라이브러리만 쓴 예입니다.

```python
import json, glob, datetime
for fn in sorted(glob.glob("config*.json")):
    d = json.load(open(fn, encoding="utf-8"))
    print("==", fn, "configVersion", d.get("configVersion"))
    for s in d.get("chat-sessions", []):
        print(s["id"], s.get("type"), s.get("name"), len(s.get("messages", [])),
              len(s.get("threads", [])), len(s.get("messageForksHash", {})))
        for m in s.get("messages", []):
            t = datetime.datetime.fromtimestamp(m["timestamp"] / 1000, datetime.timezone.utc)
            print("  ", t.isoformat(), m["role"], m.get("model", ""))
```

한 백업에만 있는 세션 ID 가 지운 세션의 후보입니다. blob 은 헥스로 첫 바이트를 봅니다. 공개 샘플에서 올린 이미지 blob 은 `64 61 74 61 3A`(글자로 `data:`)로, 만든 이미지 blob 은 `69 56 42 4F 52 77`(글자로 `iVBORw`, PNG 머리를 base64 로 바꾼 모양)로 시작합니다[4]. Data URL 은 쉼표 뒤를, 머리말 없는 blob 은 전체를 base64 로 풀면 되고, 풀어 낸 파일이 `89 50 4E 47`(PNG)로 시작하는지 확인합니다. 샘플의 만든 이미지를 풀면 PNG 안에 C2PA 매니페스트가 있고, 그 안에 `c2pa.created` 동작, `softwareAgent` 이름 `DALL·E`, `digitalSourceType` `trainedAlgorithmicMedia`, 클레임 생성기 `OpenAI-API` 가 들어 있습니다[4]. 읽는 법은 [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md)에서 다룹니다.

**공개 도구로.** LangurTrace 는 KAPE 타깃(`Chatbox.tkape`)과 모듈(`Chatbox.mkape`)로 배포되고, 모듈은 `LangurTrace.exe --src %sourceDirectory% --dst %destinationDirectory% --app chatbox` 를 실행합니다[3]. 타깃은 `C:\Users\%user%\AppData\Roaming\xyz.chatboxapp.app\` 의 `*.json`, `chatbox-blobs\`, `logs\*.log`, `Cache\CacheData\` 를 모읍니다. 결과는 아래와 같습니다[2][4].

| 출력 | 내용 |
|---|---|
| `report/configuration.csv` | 열 `Type`, `Key`, `Value`. `Type` 은 `API Key` 또는 `Default Prompt` |
| `report/conversation/{첫 메시지 현지 시각}_{threadName 또는 세션 ID}.html` | 세션별 대화. 메시지마다 시각과 모델을 붙임 |
| `uploaded/` | 올린 이미지(`pictureinput…` 에 확장자 붙임)와 문서 글(`parseFile-….txt`) |
| `generated/` | 만든 이미지(`picture….png` 등) |

`*.json` 을 모두 읽으므로 백업에만 남은 세션도 HTML 로 나옵니다. 공개 샘플 출력에는 최신 백업에 없는 세션의 HTML 도 들어 있습니다[4]. 앞의 함정 절 때문에 HTML 은 원본 JSON 과 맞춰 씁니다.

## 교차 검증

로컬 모델로 답한 메시지는 백엔드 로그와 시각을 맞추면 요청이 실제로 그 PC 의 백엔드로 갔는지 확인됩니다. 공개 샘플에서는 `aiProvider` 가 `ollama` 인 답 메시지 시각이 Ollama `server.log` 의 `/v1/chat/completions` 줄과 맞습니다([Ollama](ollama.md)의 교차 검증 참고).

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [Ollama](ollama.md), [LM Studio](lm-studio.md) | 로컬 모델 답의 요청 시각, 올린 모델 |
| [로컬 모델 파일](model-files.md) | 메시지의 모델 이름에 해당하는 모델 파일 |
| [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md) | 만든 이미지 안의 C2PA 매니페스트 |
| [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md) | 메시지·blob 을 입력과 결과로 나누기 |
| [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) | 키를 다루고 보고하는 기준 |
| [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) | 클라우드 API 로 나간 통신 |
| [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) | 메시지·백업·로그 시각을 한 줄로 세우기 |
| [딥페이크·합성 이미지를 만들었나](../../04-scenarios/misuse/deepfake.md) | 만든 이미지가 쟁점인 조사 흐름 |

## 실습

공개 시험 데이터는 LangurTrace 저장소의 `sample_dataset` 입니다[4]. `collect/C/Users/USER/AppData/Roaming/xyz.chatboxapp.app/` 에 백업 두 개, `chatbox-blobs` 의 blob 여섯 개, `logs/main.log` 가 있고, `parse/LLM application artifacts/chatbox/` 에 LangurTrace 출력이 있습니다.

1. 두 백업의 파일 이름을 현지 시각으로 바꾸고, `main.log` 에서 같은 백업을 만든 줄을 찾아 수집 PC 의 시간대를 구합니다.
2. 두 백업을 비교해 없어진 세션과 새로 생긴 세션을 찾고, 없어진 세션이 지워진 시간 범위를 적어 봅니다.
3. `main.log` 에 이름이 나온 백업 가운데 수집본에 없는 것은 몇 개입니까?
4. blob 여섯 개를 올린 것과 만든 것으로 나누고, 각 blob 을 가리키는 메시지를 찾습니다. 어느 메시지도 가리키지 않는 blob 은 무엇입니까?
5. 세션마다 답한 모델을 뽑고, 로컬 모델 답과 클라우드 모델 답의 `firstTokenLatency` 를 비교해 봅니다.
6. 시험용 가상 머신에 Chatbox 1.16.1 뒤 판을 깔고 가짜 사용자 `labuser01` 로 대화한 뒤, `config.json` 에 대화가 남는지와 백업 파일에 무엇이 들어가는지 봅니다.

## 참고 문헌

1. Jeong, S., Lee, S., Park, J., "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. https://doi.org/10.1016/j.fsidi.2025.301987 (§3.2, §3.4, §4.1, §4.3, §4.4, §4.5, §5.3, §6.2, 표 1·4·8, 부록 A)
2. LangurTrace 파서 코드, https://github.com/jeongramon/LangurTrace — `src/apps/chatbox.py`, `src/reporter/chatbox/reporter.py`, `src/reporter/chatbox/config_reporter.py`, `src/reporter/chatbox/files_reporter.py` (커밋 `0416e72`, 2025-07-20)
3. LangurTrace KAPE 타깃·모듈, https://github.com/jeongramon/LangurTrace — `dist/Targets/LLMApplications/Chatbox.tkape`, `dist/Modules/LLMApplications/Chatbox.mkape`
4. LangurTrace 공개 샘플, https://github.com/jeongramon/LangurTrace — `sample_dataset/collect/C/Users/USER/AppData/Roaming/xyz.chatboxapp.app/`(`config-backup-2025-05-23T11_36_10.169Z.json`, `config-backup-2025-05-23T11_46_10.171Z.json`, `chatbox-blobs/`, `logs/main.log`), `sample_dataset/parse/LLM application artifacts/chatbox/`
5. Chatbox 소스(1.11.8 시점), https://github.com/chatboxai/chatbox — 커밋 `97d32f92`(2025-04-10, "copy files from pro repo at release 1.11.8")의 `src/main/store-node.ts`, `src/main/main.ts`, `src/shared/types.ts`, `src/renderer/storage/StoreStorage.ts`, `src/renderer/stores/sessionActions.ts`, `src/renderer/platform/desktop_platform.ts`, `src/renderer/components/InputBox.tsx`
6. Chatbox 소스(main 브랜치), https://github.com/chatboxai/chatbox — `src/main/store-node.ts`(커밋 `19de00fb`, 2026-06-10), `docs/storage.md`(문서 안 최종 수정 2026-08-28) (2026-09-25 열람)
