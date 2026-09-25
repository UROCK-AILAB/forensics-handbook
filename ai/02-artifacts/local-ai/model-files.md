---
title: "로컬 모델 파일"
parent: "아티팩트 · 로컬 AI"
nav_order: 760
---

# 로컬 모델 파일 (GGUF·safetensors)

로컬 AI 도구가 돌리는 모델은 GGUF 나 safetensors 같은 형식의 큰 파일로 디스크에 남고, 파일 앞부분의 헤더와 앱이 따로 남긴 매니페스트·설치 기록·로그를 함께 읽으면 어떤 모델을 언제 어디서 받았는지 밝힐 수 있습니다.

앱별 모델 위치는 Windows 11 24H2 에서 Ollama 0.6.5, LM Studio 0.3.14, Msty 1.8.5, Jan 0.5.16, GPT4All 3.10.0 기준이고[6], 다른 판은 경로와 파일 이름이 다를 수 있습니다. 헥스·JSON·로그 예시는 모두 만든 예시입니다.

## 이 형식을 쓰는 아티팩트

모델 파일은 사용 기록이 아니라 모델 자체이지만, 조사에서는 그 PC 에 어떤 모델이 있었는지, 어디서 받았는지, 언제 받았는지를 알려 줍니다. GGUF 는 한 파일 안에 모델 이름·만든 사람·출처 URL·라이선스·채팅 틀 같은 메타데이터를 함께 넣는 형식이고, safetensors 는 텐서 목록을 JSON 헤더로 적고 자유 형식의 메타데이터 칸을 따로 둡니다. 파일 이름을 바꿔도 헤더의 값은 그대로 남아서, 이름을 바꿔 숨긴 모델도 헤더로 알아볼 수 있습니다. 사용자가 받아서 쓴 모델의 메타데이터는 사용 의도를 드러낼 수 있습니다[6, §6.1].

로컬 AI 도구는 모델을 저마다 정한 폴더에 두고, 두는 방식은 크게 둘로 나뉩니다. Ollama 와 Msty 는 파일을 내용의 SHA-256 digest 이름으로 두고 모델 이름은 매니페스트 폴더에 적는 digest 형이고, LM Studio·Jan·GPT4All 은 모델 이름이 드러나는 폴더나 파일 이름으로 GGUF 를 두는 이름형입니다[6, 부록 A][7].

| 앱(시험한 판) | 모델 파일 위치(Windows) | 저장 방식 | 모델 이름을 읽는 곳 | 받은 기록 |
|---|---|---|---|---|
| [Ollama](ollama.md) 0.6.5 | `%UserProfile%\.ollama\models\blobs\sha256-{digest}` | digest 형 | `%UserProfile%\.ollama\models\manifests\registry.ollama.ai\library\{모델}\{태그}` | `%LocalAppData%\Ollama\server.log` |
| [Msty](msty.md) 1.8.5 | `%AppData%\Msty\models\blobs\sha256-{digest}` | digest 형(Ollama 와 같은 짜임) | `%AppData%\Msty\models\manifests\registry.ollama.ai\library\{모델}\{태그}` | `%AppData%\Msty\logs\app.log` |
| [LM Studio](lm-studio.md) 0.3.14 | `%UserProfile%\.lmstudio\models\{제공자}\{저장소}\{파일}.gguf` | 이름형 | 폴더·파일 이름 | `%UserProfile%\.lmstudio\.internal\download-jobs-info.json` |
| [Jan](jan.md) 0.5.16 | `%AppData%\Jan\data\models\{허브}\{모델}\{크기}\model.gguf` | 이름형, 같은 폴더에 YAML | `model.yml`, `metadata.yml` | `%AppData%\Jan\data\logs\cortex.log` |
| [GPT4All](gpt4all.md) 3.10.0 | `%LocalAppData%\nomic.ai\GPT4ALL\{모델}.gguf` | 이름형, 파일 하나 | 파일 이름 | 설치 기록 없음 |

Jan 은 허브마다 짜임이 다릅니다. Jan 자체 허브 모델은 `models\cortex.so\{모델}\{크기}\` 아래 `model.yml`·`metadata.yml` 과 `model.gguf` 로 두고, Hugging Face 에서 받은 모델은 `models\huggingface.co\{작성자}\{저장소}\` 아래 GGUF 와 같은 이름의 `.yml` 로 둡니다[7]. `models\remote\*.yml` 은 `engine: openai` 같은 클라우드 모델 정의라서 모델 파일이 따로 없습니다. LM Studio 는 `models` 아래를 `publisher/model/model-file.gguf` 짜임으로 두고[4], 설치 기록의 `download.targetPath` 값(`...\.lmstudio\models\{제공자}\{저장소}\{파일}.gguf`)에도 이 경로가 남습니다[7].

Ollama 는 환경 변수 `OLLAMA_MODELS` 로, Msty 는 설정으로 모델 폴더를 옮길 수 있습니다. Ollama 는 `server.log` 첫머리의 `env="map[...]"` 에 `OLLAMA_MODELS` 값을 남기고, Msty 는 `app.log` 에 `Serving models from: ...` 와 `modelsFolder: ...` 줄을 남깁니다[7]. 기본 위치가 비어 있으면 이 줄에서 실제 모델 폴더를 먼저 찾습니다. 자세한 로그 형식은 [Ollama](ollama.md), [Msty](msty.md) 쪽에서 다룹니다.

그 밖에 파이썬 라이브러리로 받은 모델은 Hugging Face 캐시에 쌓이고, [로컬 이미지 생성 도구](image-gen-local.md)인 ComfyUI 는 `models/checkpoints` 에 safetensors 체크포인트를 둡니다[5].

### Hugging Face 캐시 위치

| 항목 | 값 |
|---|---|
| 기본 위치 | `~/.cache/huggingface/hub` |
| 위치를 바꾸는 방법 | 환경 변수 `HF_HOME`·`HF_HUB_CACHE`, 코드의 `cache_dir` 인자 |
| Xet 청크 캐시 | `~/.cache/huggingface/xet` 아래 환경마다 하나씩 생기는 식별자 폴더, 그 안의 `chunk_cache`·`shard_cache`·`staging` |
| 백업 제외 표시 | 캐시 폴더의 `CACHEDIR.TAG` 파일 |

`hf_xet` 1.2.0 부터는 `chunk_cache` 를 기본으로 쓰지 않습니다. 캐시 폴더에 `CACHEDIR.TAG` 를 만드는 것은 백업 도구에 이 폴더를 빼라고 알리는 표시라서, 백업본에는 모델 캐시가 빠져 있을 수 있습니다.

## 구조

### GGUF 헤더

GGUF 의 현재 판은 3 이고, 판 3 에서 빅엔디언 파일을 지원하기 시작했습니다. 기본은 리틀엔디언이고, 빅엔디언 파일은 메타데이터와 텐서 값이 모두 빅엔디언입니다.

| 순서 | 칸 | 크기 | 뜻 |
|---|---|---|---|
| 1 | magic | 4바이트 | `GGUF`(`47 47 55 46`) |
| 2 | version | uint32 | 형식 판(현재 3) |
| 3 | tensor_count | uint64 | 텐서 개수 |
| 4 | metadata_kv_count | uint64 | 메타데이터 키-값 개수 |
| 5 | 메타데이터 키-값 | 가변 | 아래 키들 |

반드시 있어야 하는 키는 `general.architecture`(예: `llama`)이고, 양자화한 텐서가 있으면 `general.quantization_version` 도 있어야 합니다. `general.alignment` 는 8의 배수이고 없으면 32 로 봅니다. 조사에서 자주 보는 키는 아래와 같습니다.

| 키 | 담긴 것 |
|---|---|
| `general.name` | 모델 이름 |
| `general.author` | 만든 사람 |
| `general.url` | 모델 페이지 URL |
| `general.source.url` | 원본 모델 URL |
| `general.description` | 설명 |
| `general.license` | 라이선스 |
| `general.file_type` | 파일 종류(양자화 방식 등) |
| `tokenizer.ggml.model` | 토크나이저 종류 |
| `tokenizer.chat_template` | 채팅 틀 |

명세가 권하는 파일 이름 규칙은 아래와 같고, 큰 모델은 여러 조각 파일로 나뉘어 조각 번호가 5자리로 0을 채워 붙습니다.

```
<BaseName><SizeLabel><FineTune><Version><Encoding><Type><Shard>.gguf
예(명세): Grok-100B-v1.0-Q4_0-00003-of-00009.gguf
```

이 규칙은 권장일 뿐이어서 실제 파일 이름이 따르지 않을 수 있고, 파일 이름보다 헤더 값을 먼저 믿습니다.

### safetensors

| 순서 | 칸 | 크기 | 뜻 |
|---|---|---|---|
| 1 | 헤더 크기 N | 8바이트 | 부호 없는 리틀엔디언 64비트 정수 |
| 2 | 헤더 | N바이트 | UTF-8 JSON, 반드시 `{` 로 시작 |
| 3 | 데이터 | 나머지 | 텐서 바이트 |

JSON 헤더의 각 항목은 텐서 이름을 키로 하고 `dtype`, `shape`, `data_offsets` 를 적습니다. `data_offsets` 의 두 값은 데이터 부분이 시작하는 곳을 0으로 센 시작과 끝이고, 끝 값은 마지막 바이트 다음 위치입니다. 특수 키 `__metadata__` 에는 문자열에서 문자열로 가는 자유 형식 정보를 넣을 수 있고, 무엇을 넣는지는 파일을 만든 도구마다 다릅니다. safetensors 형식에는 판 번호를 적는 칸이 따로 없습니다[2].

`.ckpt`·`.bin` 같은 pickle 형식은 불러올 때 임의의 코드가 실행될 수 있고, safetensors 는 JSON 으로 선언만 하는 형식이라 그렇지 않습니다. 의심스러운 모델 파일이 pickle 형식이라면 악성 코드를 실어 나를 수 있는 파일로 보고, 분석할 때는 라이브러리로 불러오지 않고 바이트로만 읽습니다. [AI로 악성 코드를 만들었나](../../04-scenarios/misuse/malware-development.md) 같은 조사에서 모델 파일이 나오면 이 점을 먼저 확인합니다.

### Ollama·Msty 의 매니페스트와 blob

매니페스트는 Docker 방식의 JSON 이고, 모델 본체·채팅 틀·라이선스·매개변수 파일을 각각 층(layer)으로 적습니다. 층마다 SHA-256 digest 와 크기가 있고, 실제 층 파일은 digest 와 같은 이름으로 `blobs` 폴더에 둡니다[6, §4.4]. 모델 이름과 태그는 파일 안이 아니라 매니페스트 경로의 폴더 이름(`library\{모델}\{태그}`)에 있습니다. 아래는 샘플[7]의 짜임을 따라 digest 를 지어낸 만든 예시입니다.

```json
{"schemaVersion":2,
 "mediaType":"application/vnd.docker.distribution.manifest.v2+json",
 "config":{"mediaType":"application/vnd.docker.container.image.v1+json",
           "digest":"sha256:1111...1111","size":480},
 "layers":[
  {"mediaType":"application/vnd.ollama.image.model","digest":"sha256:aaaa...aaaa","size":812345678},
  {"mediaType":"application/vnd.ollama.image.template","digest":"sha256:bbbb...bbbb","size":350},
  {"mediaType":"application/vnd.ollama.image.license","digest":"sha256:cccc...cccc","size":8400},
  {"mediaType":"application/vnd.ollama.image.params","digest":"sha256:dddd...dddd","size":80}]}
```

위 예시라면 모델 본체는 `blobs\sha256-aaaa...aaaa` 파일이고, digest 의 콜론을 하이픈으로 바꾼 이름입니다. 헤더를 읽을 대상은 `application/vnd.ollama.image.model` 층이고, Ollama `server.log` 는 이 파일을 적재할 때 `(version GGUF V3 (latest))` 라고 적어 GGUF 임을 보여 줍니다[7]. Msty 매니페스트에는 위 넷 말고 `application/vnd.ollama.image.system` 층이 더 있을 수 있습니다[7]. `config` 의 digest 도 `blobs` 에 파일로 남지만 `layers` 목록에는 없어서, LangurTrace 의 `model_manifest.csv` 에서는 모델 이름이 `-` 인 줄로 나옵니다.

### Jan 의 모델 YAML

Jan `model.yml` 은 주석으로 칸의 뜻을 적어 둡니다[7]. `id`·`model` 은 모델 식별자, `name` 은 주석이 `# metadata.general.name` 이라고 적은 이름, `files` 는 GGUF 경로(상대 또는 절대), `size` 는 바이트 크기이고, `engine`·`prompt_template`·`ctx_len`·`ngl` 같은 실행 값이 이어집니다. `metadata.yml` 에는 `version`, `name`, `default`(기본 크기, 예 `3b`), `author` 가 있습니다. YAML 의 `name` 은 GGUF 헤더의 `general.name` 과 글자가 다를 수 있습니다. 예를 들어 YAML 에는 하이픈을 넣은 이름이, `cortex.log` 에 찍힌 헤더 값에는 띄어쓴 이름이 들어가기도 합니다[7].

### Hugging Face 캐시 폴더

저장소마다 `models--조직--이름`, `datasets--조직--이름`, `spaces--조직--이름` 모양의 폴더를 만듭니다. 아래는 가짜 저장소 `sample-org/sample-model` 로 만든 예시이고, 해시 자리는 꺾쇠로 표시했습니다.

```
models--sample-org--sample-model/
  refs/main                          ← 브랜치 main 이 가리키는 커밋 해시
  blobs/<파일 해시>                   ← 실제 파일, 이름이 해시
  snapshots/<커밋 해시>/model.safetensors  ← blobs 를 가리키는 심볼릭 링크
  trees/<커밋 해시>.json              ← 그 커밋의 파일 목록(경로·크기·해시)
  .no_exist/<커밋 해시>/               ← Hub 에 없던 파일을 빈 파일로 기록
```

새 판을 받아도 옛 파일을 지우지 않아서, `snapshots` 아래 커밋 폴더가 여럿이면 그만큼 다른 판을 받은 적이 있다고 볼 수 있습니다. `hf_xet` 로 받은 Xet 파일은 캐시 맨 위 `blobs` 폴더에 한 번만 두고 저장소별 `blobs` 항목이 그 파일을 가리키는 링크가 되는 경우도 있어서, 저장소 폴더 안에서 실제 파일이 안 보이면 캐시 맨 위 `blobs` 를 함께 봅니다. Windows 에서 심볼릭 링크를 만들 수 없으면 `blobs` 를 쓰지 않고 `snapshots` 에 파일을 바로 두고, 개발자 모드이거나 관리자로 실행했으면 링크를 씁니다. `HF_HUB_DISABLE_SYMLINKS=1` 로 링크를 끌 수도 있습니다.

## 읽는 법

### 헥스로 헤더 읽기

**GGUF.** 아래는 명세를 따라 만든 예시이고 실제 파일에서 나온 값이 아닙니다.

```
00000000  47 47 55 46 03 00 00 00  23 01 00 00 00 00 00 00  GGUF....#.......
00000010  18 00 00 00 00 00 00 00                            ........
```

첫 4바이트 `47 47 55 46` 은 `GGUF` 이고, 다음 4바이트 `03 00 00 00` 은 리틀엔디언으로 판 3 입니다. 빅엔디언 파일이면 같은 자리가 `00 00 00 03` 으로 보입니다. 오프셋 0x08 의 8바이트 `23 01 00 00 00 00 00 00` 은 텐서 개수 0x123(291개), 오프셋 0x10 의 8바이트 `18 00 …` 은 메타데이터 키-값 개수 0x18(24개)이고, 오프셋 0x18 부터 메타데이터가 이어집니다. 글자 칸에서 `general.name` 이나 `general.source.url` 을 찾으면 그 뒤에 값이 글자로 보입니다. Ollama·Msty 는 `blobs` 의 모델 층 파일을 같은 방법으로 읽습니다.

**safetensors.** 역시 명세를 따라 만든 예시입니다. 헤더는 `{"__metadata__":{"note":"sample"},"w1":{"dtype":"F16","shape":[2,2],"data_offsets":[0,8]}}` 이고 길이는 90바이트입니다.

```
00000000  5A 00 00 00 00 00 00 00  7B 22 5F 5F 6D 65 74 61  Z.......{"__meta
00000010  64 61 74 61 5F 5F 22 3A  7B 22 6E 6F 74 65 22 3A  data__":{"note":
00000020  22 73 61 6D 70 6C 65 22  7D 2C 22 77 31 22 3A 7B  "sample"},"w1":{
```

첫 8바이트 `5A 00 00 00 00 00 00 00` 은 헤더 크기 90 이고, 오프셋 0x08 이 `7B`(`{`) 로 시작합니다. 데이터 부분은 8 + 90 = 98(0x62) 에서 시작하므로, 텐서 `w1` 은 파일 오프셋 0x62 부터 8바이트(F16 값 4개)입니다.

### 해시로 출처 대조하기

대조 방법은 두 가지입니다. Ollama 는 층마다 SHA-256 digest 와 크기가 있으니 이 값을 공개 모델 허브와 대조하고[6, §4.4], LM Studio 는 모델 파일을 지웠어도 설치 기록에 남은 이름과 해시로 같은 파일을 다른 곳에서 찾거나, 남은 요청 URL 로 같은 파일을 다시 받습니다[6, §4.6.1]. 절차는 아래와 같습니다.

1. 모델 파일마다 SHA-256 과 크기를 계산해 기록합니다. Ollama·Msty 는 계산한 값이 `blobs` 파일 이름의 digest 와 같은지 먼저 봅니다.
2. 앱 기록에 남은 해시와 맞춥니다. LM Studio 는 `download-jobs-info.json` 의 `jobs[].tasks[].request.sha256` 과 `request.fileSizeBytes`, Ollama·Msty 는 매니페스트의 `digest`·`size` 가 대조 값입니다.
3. 앱 기록에 남은 출처를 읽습니다. LM Studio 는 `request.url`, Jan 은 `cortex.log` 의 `Handle model input, model handle:` 줄과 GGUF 헤더의 `general.base_model.0.repo_url` 이 출처를 알려 줍니다.
4. 같은 해시를 공개 허브의 파일 해시와 맞춰 어느 저장소의 어느 파일인지 좁힙니다. 파일이 지워졌으면 2·3단계의 해시와 URL 만으로 같은 파일을 찾습니다.

LangurTrace 샘플[7]에서는 LM Studio 설치 기록 네 건 가운데 세 건의 `request.sha256` 이 모델 폴더 파일의 SHA-256(`models_index.csv`)과 같고, 나머지 한 건은 모델 폴더에 파일이 없습니다. 이렇게 기록에는 있고 파일이 없는 항목이 지운 모델의 후보입니다. LM Studio `request.url` 은 `https://search.lmstudio.ai:443/v1/hf-proxy/{저장소}/resolve/main/{파일}?download=true` 모양이어서, LM Studio 가 자체 주소를 거쳐 Hugging Face 저장소에서 받았다는 점과 저장소 이름이 함께 드러납니다[7].

### 앱 기록에서 받은 시각과 적재 시각 읽기

GGUF 와 safetensors 명세에는 시각 칸이 없지만, 모델을 받은 시각과 적재한 시각은 앱 기록에 따로 남습니다. 아래 줄 모양은 샘플[7]을 따라 값을 지어낸 만든 예시입니다.

| 앱 | 받은 기록 | 시각 형식 |
|---|---|---|
| Ollama | `server.log` 의 `source=download.go:177 msg="downloading {digest 앞 12자} in {조각 수} {조각 크기} part(s)"` 와 `POST "/api/pull"` 줄 | `time=` 은 현지 시각에 오프셋, `[GIN]` 줄은 오프셋 없는 현지 시각 |
| LM Studio | `download-jobs-info.json` 의 `jobs[].jobState.completedTimestamp` | Unix 밀리초 |
| Jan | `cortex.log` 의 `Handle model input, model handle: {URL 또는 모델 이름}`, `Task added to queue: {모델}`, `Transfer completed for URL: {URL}` | `YYYYMMDD HH:MM:SS.ffffff UTC` |
| Msty | `app.log` 한 줄 JSON 의 `"msg":"Fetching model: {모델}:{태그}"` | `time` 칸, Unix 밀리초 |

```
time=2025-06-01T10:15:02.123+09:00 level=INFO source=download.go:177 msg="downloading aaaaaaaaaaaa in 8 100 MB part(s)"
20250601 01:20:44.500000 UTC 1234 INFO  Task added to queue: sample-model:1b - download_service.cc:492
```

모델을 실제로 적재한 때는 Ollama `server.log` 와 Jan `cortex.log` 의 `llama_model_loader: loaded meta data with {키 개수} key-value pairs and {텐서 개수} tensors from {파일 경로}` 줄로 읽습니다. 이 줄 뒤에는 `general.name` 같은 GGUF 헤더 값이 로그에 그대로 찍혀서, 모델 파일이 지워져도 헤더 내용 일부를 로그로 되살릴 수 있습니다. 어느 대화에 어느 모델을 썼는지는 각 앱 쪽의 메시지별 모델 칸으로 확인합니다([Chatbox](chatbox.md), [Msty](msty.md), [Jan](jan.md), [LM Studio](lm-studio.md)).

파일 시스템 시각은 보조 근거입니다. 파일 생성 시각은 내려받거나 복사한 때에 가깝고, 모델을 쓴 때가 아닙니다. Hugging Face 캐시에서는 `hf cache ls` 가 저장소별 마지막 접근 시각과 수정 시각을 보여 주지만, 이 값도 파일 시스템 시각에서 나온 값으로 보고 볼륨의 마지막 접근 시각 기록 설정을 함께 확인합니다. `snapshots` 아래 커밋 폴더가 여럿이면 폴더 시각 순서로 판을 받은 순서를 가늠할 수 있습니다.

## 포렌식에서 중요한 점

### 지운 모델

모델 파일을 지워도 앱 기록은 대개 남습니다. LangurTrace 시험에서 앱 화면으로 모델을 지운 뒤 받은 기록을 되살린 비율은 아래와 같습니다[6, 표 8]. 디스크에 남은 파일만 잰 값이고, 볼륨 섀도 복사본·메모리·SQLite 카빙은 시험 범위 밖입니다[6, §6.2].

| 앱 | 지운 모델의 받은 기록을 되살린 비율 | 남는 곳 |
|---|---|---|
| Ollama | 100%(5/5) | `server.log` 의 다운로드 줄 |
| LM Studio | 100%(5/5) | `download-jobs-info.json` |
| Msty | 100%(5/5) | `app.log` 의 모델 설치 기록 |
| Jan | 100%(5/5) | `cortex.log` |
| GPT4All | 0%(0/5) | 되살릴 기록 없음 |

Ollama 는 삭제 요청도 `server.log` 에 `DELETE "/api/delete"` 줄로 남깁니다[7]. 다운로드 줄의 digest 는 앞 12자뿐이지만, 같은 모델을 받은 다른 매니페스트나 공개 허브의 digest 와 앞자리를 맞춰 어느 모델이었는지 좁힐 수 있습니다. GPT4All 은 모델 파일 말고 받은 기록이 없어서, 파일이 지워지면 [네트워크 기록](../network-enterprise/network-traces.md)이나 볼륨 수준 복구로 넘어갑니다.

### 끊긴 다운로드와 손상

Hugging Face 캐시에서 내려받다 끊긴 파일은 `.incomplete` 파일로 남고, `hf cache prune` 을 돌리면 이 파일과 어느 브랜치·태그도 가리키지 않는 옛 판이 함께 지워집니다. LM Studio 는 작업마다 `jobState.type` 과 `download.status` 에 상태를 적고, `download.status` 가 `completed` 인데 `jobState.type` 이 `postActionFailed` 인 작업(실행 엔진 작업 등)도 있습니다[7]. Msty `app.log` 에는 `Failed fetching model {모델}: AbortError: This operation was aborted` 처럼 받다가 멈춘 기록이 남습니다[7].

GGUF 파일이 `GGUF` 로 시작하지 않거나 판 값이 명세에 없는 값이면 손상이나 다른 형식을 의심합니다. safetensors 는 헤더 크기를 100MB 로 제한하고 텐서 오프셋이 서로 겹치지 않아야 하므로[2], 헤더 크기가 파일보다 크거나 헤더가 `{` 로 시작하지 않거나 오프셋이 겹치면 safetensors 가 아니거나 손상·조작된 파일로 봅니다.

### 증명하는 것과 증명하지 못하는 것

**증명하는 것.** 모델 파일이 있으면 그 모델이 그 디스크에 있었다고 쓸 수 있고, 헤더의 이름·URL·라이선스는 파일을 만든 쪽이 적어 넣은 값으로 인용할 수 있습니다. 앱의 설치 기록과 로그는 받은 시각과 출처 URL·해시를 알려 주고, 적재 로그는 그 모델을 불러온 시각을 알려 줍니다. Hugging Face 캐시의 폴더 이름과 `refs`·`snapshots`·`trees` 는 어느 저장소의 어느 커밋을 받았는지 알려 주고, `.incomplete` 파일은 내려받기를 시작했지만 끝내지 못한 흔적입니다.

**증명하지 못하는 것.** 모델 파일만으로는 그 모델을 돌렸다거나 무엇을 물었다고 쓸 수 없어서, 사용 여부는 적재 로그와 대화 기록으로 따로 밝힙니다. 헤더 값은 누구든 고쳐 쓸 수 있어서 `general.author` 나 `__metadata__` 의 값만으로 출처를 확정하지 않고, 해시를 공개 허브와 맞춘 결과를 함께 적습니다. 캐시가 비어 있어도 `HF_HOME`·`HF_HUB_CACHE`·`OLLAMA_MODELS` 로 다른 곳에 두었거나, `hf cache rm`·`hf cache prune` 이나 앱 화면에서 지웠을 수 있습니다.

## 함정

- **이름만 믿기.** 파일 이름과 폴더 이름은 사용자가 바꿀 수 있습니다. 헤더를 읽어 이름을 확인합니다.
- **헤더 이름도 비어 있거나 뜻이 없을 수 있음.** Ollama `server.log` 에 `msg="key not found" key=general.name` 줄이 찍히거나, Jan `cortex.log` 에 `general.name` 이 `Hf` 로 찍히는 모델이 있습니다[7]. 이럴 때는 `general.base_model.0.repo_url` 같은 다른 키와 해시로 모델을 가립니다.
- **조각 파일.** 여러 조각으로 나뉜 GGUF 는 조각 하나만 남아 있어도 모델 전체가 있었다고 보지 않고, 조각 번호와 전체 개수를 확인합니다.
- **digest 형 저장소의 파일 수.** Ollama·Msty 의 `blobs` 에는 모델 본체 말고도 채팅 틀·라이선스·매개변수·`config` 파일이 digest 이름으로 함께 있습니다. 크기와 매니페스트의 `mediaType` 으로 모델 본체를 고릅니다.
- **옮긴 모델 폴더.** LangurTrace 의 KAPE 타깃은 `C:\Users\%user%\...` 아래 기본 경로만 모읍니다. `OLLAMA_MODELS` 나 Msty 설정으로 옮긴 폴더, 다른 드라이브는 로그에서 경로를 읽고 따로 모읍니다.
- **캐시 명령의 부작용.** `hf cache ls` 나 `hf cache verify` 는 원본이 아니라 사본에서 돌립니다. `hf cache rm`·`hf cache prune` 은 지우는 명령이라 조사에서는 쓰지 않고, 사용자가 이 명령을 쓴 흔적이 있으면 캐시가 비어 있는 까닭으로 적습니다.
- **Windows 링크.** 링크를 쓰지 않은 Hugging Face 캐시에서는 `blobs` 가 비어 있어도 이상이 아닙니다.
- **시각의 시간대.** Ollama 로그는 현지 시각, Jan 로그는 UTC, LM Studio·Msty 는 Unix 밀리초라서 한 줄로 세우기 전에 기준을 맞춥니다. LangurTrace 는 LM Studio 의 Unix 밀리초를 분석 PC 의 현지 시각으로 바꿔 CSV 에 적고, Ollama 로그는 오프셋을 떼고 옮깁니다.

## 도구

모델 파일 하나는 SHA-256 을 떠서 기록합니다. Windows 에서는 PowerShell `Get-FileHash -Algorithm SHA256`, 리눅스에서는 `sha256sum` 으로 계산하면 됩니다. safetensors 헤더는 앞 8바이트로 길이를 읽은 뒤 그 길이만큼 잘라 `jq` 로 펼칩니다. Hugging Face 캐시 사본에서는 `hf cache ls` 로 저장소 목록과 시각을, `hf cache verify` 로 파일 해시가 맞는지를 확인합니다.

LangurTrace[7]는 KAPE 타깃과 모듈로 로컬 LLM 앱의 기록을 모으고 해석합니다. 모듈은 `LangurTrace.exe --src %sourceDirectory% --dst %destinationDirectory% --app ollama` 처럼 앱 이름을 넘겨 실행하고, 모델에 관해서는 아래 파일을 냅니다. LangurTrace 는 2025년 2~4월 배포판 앱으로 시험한 도구라서[6, 표 1], 지금 판의 앱에서는 경로나 키가 바뀌어 빠지는 항목이 있을 수 있습니다.

| 앱 | 출력 파일 | 칸 | 만드는 코드 |
|---|---|---|---|
| Ollama·Msty | `model_manifest.csv` | `model_name`, `parameter`, `layer_name`, `digest`, `size`, `path` | `src/reporter/ollama/manifest_reporter.py`, `layer_reporter.py` |
| LM Studio | `model_setup_history.csv` | Job ID, Model Name, Status, File Size (bytes), SHA256, Completed Time, URL, Saved Path | `src/reporter/lmstudio/model_setup_reporter.py` |
| LM Studio | `models_index.csv` | Provider, Model File, SHA256 | `src/reporter/lmstudio/model_reporter.py` |
| GPT4All | `model_index.csv` | `file_name`, `size`, `sha256` | `src/reporter/gpt4all/model_reporter.py` |
| Jan | `model_metadata.csv` | `file`, `version`, `name`, `parameter`, `author`, `model_id`, `model`, `path` | `src/reporter/jan/model_reporter.py` |

LM Studio 는 `models` 아래 모든 파일을, GPT4All 은 `*.gguf` 파일을 통째로 메모리로 읽어 SHA-256 을 계산하고(`src/parser/common_parser.py` 의 `parse_binary`), LM Studio 의 Provider 칸은 경로를 `\` 로 나눈 끝에서 세 번째 조각, 곧 `models\{제공자}\{저장소}\{파일}` 의 제공자 폴더 이름입니다. Ollama·Msty 는 파일을 해시하지 않고 `blobs` 파일 이름의 digest 를 그대로 옮깁니다. Jan 의 `model_metadata.csv` 는 YAML 을 줄 단위로 잘라 읽어서 `name` 칸에 주석이 붙어 나오기도 합니다.

## 함께 볼 페이지

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [Ollama](ollama.md), [LM Studio](lm-studio.md), [Msty](msty.md), [Jan](jan.md), [GPT4All](gpt4all.md), [로컬 이미지 생성 도구](image-gen-local.md) | 그 모델을 어느 도구가 두었고 썼는지, 앱별 로그·설치 기록의 전체 형식 |
| [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) | 모델을 내려받은 통신과 시각 |
| [보안 제품이 남기는 AI 사용 기록](../network-enterprise/dlp-casb.md) | 큰 모델 파일을 내려받은 기록이 보안 제품 로그에 있는지 |
| [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) | 옮긴 모델 폴더까지 빠짐없이 모으는 방법 |
| [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md) | 회사 PC 에서 로컬 모델이 나왔을 때의 조사 흐름 |
| [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) | 받은 시각·적재 시각·파일 시각을 다른 기록과 한 줄로 세우기 |

## 실습

LangurTrace 저장소의 `sample_dataset/collect` 에는 Windows 11 에서 모은 앱 폴더가, `sample_dataset/parse` 에는 LangurTrace 출력이 있습니다. GGUF 파일은 크기 때문에 빠졌지만[7], Ollama·Msty 매니페스트와 작은 층 파일, Jan YAML, LM Studio `download-jobs-info.json`, 각 앱 로그는 들어 있습니다.

1. Ollama 매니페스트에 적힌 모델은 몇 개이고, `server.log` 의 `download.go` 줄에 나오는 digest 앞자리 가운데 매니페스트에 없는 것은 무엇입니까? 그 digest 를 Msty 매니페스트에서 찾으면 어느 모델입니까?
2. LM Studio `download-jobs-info.json` 의 `request.sha256` 을 `parse` 의 `models_index.csv` 와 맞추면, 기록에는 있고 파일은 없는 모델은 무엇이고 받은 시각(`completedTimestamp`)은 UTC 로 언제입니까?
3. Jan `model.yml` 의 `name` 과 `cortex.log` 에 찍힌 `general.name` 을 모델마다 비교하면 무엇이 다릅니까?
4. 시험용 가상 머신에서 작은 공개 GGUF 를 받아 첫 24바이트에서 판·텐서 개수·메타데이터 개수를 손으로 읽고, 파일 이름을 `sample-renamed.gguf` 로 바꾼 뒤에도 헤더에서 원래 모델 이름을 찾을 수 있습니까?
5. safetensors 파일의 앞 8바이트로 헤더 길이를 계산하고, 그 길이만큼 잘라 낸 JSON 에 `__metadata__` 가 있습니까?
6. Hugging Face 캐시에서 같은 저장소의 다른 판을 받으면 `snapshots` 와 `refs/main` 은 어떻게 바뀝니까? Windows 일반 계정과 개발자 모드에서 `blobs` 의 모습은 어떻게 다릅니까?

## 참고 문헌

1. ggml, "GGUF", https://github.com/ggml-org/ggml/blob/master/docs/gguf.md (2026-09-25 열람)
2. Hugging Face, safetensors GitHub README, https://github.com/huggingface/safetensors (2026-09-25 열람)
3. Hugging Face, huggingface_hub "Understand caching / Manage cache", https://huggingface.co/docs/huggingface_hub/guides/manage-cache (2026-09-25 열람)
4. LM Studio Docs, "Import models", https://lmstudio.ai/docs/app/advanced/import-model (2026-09-25 열람)
5. ComfyUI, GitHub README, https://github.com/comfyanonymous/ComfyUI (2026-09-25 열람)
6. Sungjo Jeong, Sangjin Lee, Jungheum Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. https://doi.org/10.1016/j.fsidi.2025.301987
7. jeongramon, LangurTrace, https://github.com/jeongramon/LangurTrace — `README.md`, `dist/Targets/LLMApplications/*.tkape`, `dist/Modules/LLMApplications/Ollama.mkape`, `src/apps/{ollama,msty,lmstudio,jan,gpt4all}.py`, `src/parser/common_parser.py`, `src/reporter/ollama/manifest_reporter.py`, `src/reporter/ollama/layer_reporter.py`, `src/reporter/ollama/log_reporter.py`, `src/reporter/msty/reporter.py`, `src/reporter/lmstudio/model_reporter.py`, `src/reporter/lmstudio/model_setup_reporter.py`, `src/reporter/gpt4all/model_reporter.py`, `src/reporter/jan/model_reporter.py`, `sample_dataset/collect`, `sample_dataset/parse` (2026-09-25 열람)
