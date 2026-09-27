---
title: "Ollama"
parent: "아티팩트 · 로컬 AI"
nav_order: 680
---

# Ollama

Ollama 는 내려받은 언어 모델을 자기 컴퓨터에서 돌리는 백엔드 런타임이고, 대화 본문은 남기지 않지만 서버 로그에 모델을 받고 올리고 부른 시각이 줄마다 남고 `.ollama` 폴더에 모델 매니페스트와 레이어, CLI 입력 기록이 남습니다.

이 페이지의 경로와 로그 모양은 Ollama 0.6.5 기준이고[1], 뒤의 판은 로그 줄 모양과 파일이 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

Ollama 는 모델을 받아 디스크에 두고 로컬 서버를 띄운 다음, 명령줄이나 Chatbox 같은 클라이언트 앱이 보낸 API 요청을 받아 모델을 돌립니다. 모델도 백엔드 런타임도 대화나 문맥을 스스로 관리하지 않고, 클라이언트 앱이 대화를 들고 있다가 요청할 때마다 다시 보냅니다[1, §4.4]. 그래서 Ollama 쪽에는 대화 본문이 없고, 어떤 요청이 언제 왔는지를 적은 API 호출 기록이 핵심 증거가 됩니다. 대화 본문은 Ollama 에 붙어 쓴 클라이언트 앱의 저장소에서 찾습니다. 로컬 LLM 앱을 백엔드·클라이언트·통합형으로 나누는 틀은 [로컬 AI](index.md)에서 다룹니다.

로컬에서 돌릴 때 Ollama 회사는 프롬프트와 데이터를 보지 않고, 클라우드 모델을 쓸 때는 프롬프트와 답을 처리하지만 저장하거나 기록하지 않습니다[4]. 서비스 회사에 요청해 받을 대화 원본이 없다고 보고 기기에 남은 흔적을 중심에 둡니다. 서버와 기기 중 어디에 데이터가 남는지의 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

Ollama 아티팩트는 여섯 가지입니다[1, 표 3]. 이 가운데 서버 로그, 모델 매니페스트, 모델 레이어가 가장 중요하고, 앱 로그와 업그레이드 로그는 쓰임이 적으며, CLI 기록은 사용자가 명령줄로 모델을 쓴 경우에만 쓸모가 있습니다[1, §4.4].

| 아티팩트 | 형식 | 담긴 것 |
|---|---|---|
| 서버 로그 | 텍스트 | 모델 설치, API 호출 |
| 모델 매니페스트 | Docker 매니페스트 | 모델 레이어의 메타데이터 |
| 모델 레이어 | 이진 | 템플릿, 매개변수 |
| 앱 로그 | 텍스트 | 앱 사용 기록 |
| 업그레이드 로그 | 텍스트 | 소프트웨어 업데이트 기록 |
| CLI 기록 | 텍스트 | 명령줄로 친 사용자 입력 |

모델 레이어에는 템플릿과 매개변수 말고도 모델 본체와 라이선스가 있고, 매니페스트가 이 넷을 모두 적습니다[1, §4.4].

## 위치와 버전별 차이

### Windows

Windows 에서 Ollama 가 쓰는 경로는 아래와 같습니다[1, 부록 A][5][6].

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%LocalAppData%\Ollama\server.log` | 서버 로그(지금 쓰는 파일) | 논문, 문서 |
| `%LocalAppData%\Ollama\server-1.log`, `server-2.log` … | 앞선 서버 로그 | 문서("server-#.log"), 샘플 |
| `%LocalAppData%\Ollama\app.log`, `app-1.log` … | 앱 로그 | 논문, 문서, 샘플 |
| `%LocalAppData%\Ollama\upgrade.log` | 업그레이드 로그 | 논문, 문서 |
| `%UserProfile%\.ollama\models\manifests\registry.ollama.ai\library\{모델 이름}\{parameters}` | 모델 매니페스트 | 논문, 샘플 |
| `%UserProfile%\.ollama\models\blobs\sha256-{digest}` | 모델 레이어 | 논문, 샘플 |
| `%UserProfile%\.ollama\history` | CLI 입력 기록 | 논문 |
| `%UserProfile%\.ollama\id_ed25519.pub` | Ollama 공개키 | 문서 |
| `%UserProfile%\.ollama\id_ed25519` | 짝이 되는 개인키 | – |
| `%UserProfile%\.ollama\cache\` 아래 JSON 파일 | 앱 캐시 | – |
| `%LocalAppData%\Programs\Ollama` | 실행 파일(설치할 때 PATH 에 추가) | 문서, 샘플 |
| `%TEMP%` 아래 `ollama` 로 시작하는 폴더 | 임시 파일 | 문서 |

매니페스트 경로의 마지막 자리(`{parameters}`)에는 `llama3.2\latest` 처럼 태그 이름(`latest`)이 오고, LangurTrace 출력은 이 값을 `parameter` 열에 넣습니다[1, 부록 A][2].

앱 로그에는 `%LocalAppData%\Ollama\config.json` 을 썼다는 줄(`msg="wrote store: …\\config.json"`)과, 업데이트 설치 파일을 `%LocalAppData%\Ollama\updates\` 아래 폴더에 받았다는 줄도 남습니다[2]. `config.json` 의 내용은 실제 기기에서 열어 확인합니다.

Windows 판은 관리자 권한 없이 사용자 폴더 아래에 깔리고, 설치 프로그램을 `OllamaSetup.exe /DIR="d:\some\location"` 처럼 실행하면 다른 폴더에 깔립니다[5]. 설치하지 않고 압축만 풀어 쓰는 명령줄 판(`ollama-windows-amd64.zip`, `ollama-windows-amd64-rocm.zip`, `ollama-windows-amd64-mlx.zip`)도 공식으로 받을 수 있습니다[5].

`.ollama` 폴더에는 공개키 `id_ed25519.pub` 와 함께 짝이 되는 개인키 `id_ed25519`, 캐시 JSON 이 생깁니다(Windows 11 기준). `models` 아래가 비어 있거나 `history` 파일이 없을 수도 있습니다.

### macOS·Linux

macOS·Linux 의 위치는 아래와 같습니다[4][6]. 다른 운영체제에서도 아티팩트 종류는 Windows 와 같을 것으로 보입니다[1, §4.1].

| 항목 | macOS | Linux |
|---|---|---|
| 모델 기본 위치 | `~/.ollama/models` | `/usr/share/ollama/.ollama/models` |
| Ollama 공개키 | `~/.ollama/id_ed25519.pub` | `/usr/share/ollama/.ollama/id_ed25519.pub` |
| 서버 로그 | `~/.ollama/logs/server.log` | systemd 저널(`journalctl -u ollama` 로 읽음) |

Linux 기본 위치는 사용자 홈이 아니라 `/usr/share/ollama` 아래라서, 사용자 홈만 수집하면 모델과 키가 빠집니다. Linux 서버 로그는 파일이 아니라 저널에 들어가므로 저널을 함께 수집합니다. 컨테이너로 돌렸다면 로그는 `docker logs` 로 보는 컨테이너 출력에 있고, 터미널에서 `ollama serve` 로 직접 띄웠다면 그 터미널에만 찍힙니다[6].

### 동작을 바꾸는 환경 변수

| 변수 | 하는 일 | 기본값[4] | 공개 샘플(0.6.5) 로그에 찍힌 값[2] |
|---|---|---|---|
| `OLLAMA_MODELS` | 모델 저장 위치를 바꿈 | 위 표의 기본 위치 | `C:\\Users\\…\\.ollama\\models` |
| `OLLAMA_HOST` | 서버가 붙는 주소와 포트 | `127.0.0.1` 의 `11434` 포트 | `http://127.0.0.1:11434` |
| `OLLAMA_ORIGINS` | 교차 출처 요청을 허용할 출처 | `127.0.0.1`·`0.0.0.0` 에서 온 요청 허용 | `http://localhost`, `https://localhost`, `http(s)://127.0.0.1`, `http(s)://0.0.0.0` 과 각 `:*`, `app://*`, `file://*`, `tauri://*`, `vscode-webview://*`, `vscode-file://*` |
| `OLLAMA_KEEP_ALIVE` | 모델을 메모리에 남겨 두는 시간 | 5분 | `5m0s` |
| `OLLAMA_NOHISTORY` | (이름만 로그에 나옴) | – | `false` |

Windows 에서는 이 변수를 설정 앱의 "Edit environment variables for your account" 에서 겁니다[5]. 값을 확인하는 가장 직접적인 곳은 로그입니다. 서버가 뜰 때마다 `server.log` 첫 줄에, 앱이 뜰 때마다 `app.log` 에 그때 쓴 환경 변수 전체가 `env="map[…]"` 으로 찍히기 때문입니다(구조 절 참고). 디스크 이미지에서 사용자 레지스트리 하이브의 사용자 환경 변수를 읽는 것은 로그가 없거나 지워졌을 때의 보조 수단입니다.

## 구조

### 폴더 모양

공개 샘플[2]의 모양을 따라 이름만 바꾼 만든 예시입니다.

```
.ollama/
  history
  models/
    manifests/registry.ollama.ai/library/<모델 이름>/<parameters>
    blobs/sha256-<digest 64자리>
AppData/Local/Ollama/
  server.log  server-1.log  server-2.log
  app.log     app-1.log     app-2.log
  upgrade.log
```

로그 번호가 클수록 오래된 파일입니다. 공개 샘플에서는 `server-2.log` 는 19:11, `server-1.log` 는 19:17, `server.log` 는 20:22 에 서버가 뜨면서 시작했고, 같은 시각에 `app` 로그도 새 파일로 바뀌었습니다(샘플 기준, 2025-05-23 현지 시각)[2].

### 모델 매니페스트와 레이어

매니페스트는 Docker 방식의 매니페스트 파일이고, 모델 본체·템플릿·라이선스·매개변수 레이어를 SHA-256 digest 와 크기로 적습니다[1, §4.4]. 모델 이름은 파일 안이 아니라 경로에 있고, `library\{모델 이름}\{parameters}` 의 마지막 파일이 매니페스트 자체입니다. 레이어 파일은 digest 를 이름으로 삼아서 `blobs\sha256-{digest}` 로 저장되고, 매니페스트의 `sha256:` 뒤 값과 파일 이름의 `sha256-` 뒤 값이 같습니다[1, §4.4][2]. 매니페스트의 필드는 아래와 같습니다[2].

| 필드 | 샘플 값 |
|---|---|
| `schemaVersion` | `2` |
| `mediaType` | `application/vnd.docker.distribution.manifest.v2+json` |
| `config.mediaType` | `application/vnd.docker.container.image.v1+json` |
| `config.digest`, `config.size` | 설정 레이어의 digest 와 크기 |
| `layers[].mediaType` | 아래 넷 가운데 하나 |
| `layers[].digest` | `sha256:` 과 64자리 16진수 |
| `layers[].size` | 바이트 수 |

| `layers[].mediaType` | 레이어 |
|---|---|
| `application/vnd.ollama.image.model` | 모델 본체(GGUF) |
| `application/vnd.ollama.image.template` | 프롬프트 템플릿 |
| `application/vnd.ollama.image.license` | 라이선스(샘플에서는 두 개) |
| `application/vnd.ollama.image.params` | 매개변수 |

LangurTrace 는 이 네 이름으로 레이어를 나눕니다[2, `manifest_reporter.py`]. `config` 레이어는 JSON 이고 `model_format`(`gguf`), `model_family`, `model_families`, `model_type`, `file_type`, `architecture`, `os`, `rootfs.diff_ids` 필드가 있으며, `params` 레이어도 JSON 입니다(`stop` 필드)[2]. 모델 본체 레이어가 GGUF 라는 점은 서버 로그의 `(version GGUF V3 (latest))` 로도 드러납니다[2]. 모델 본체를 바이트로 읽는 법은 [로컬 모델 파일](model-files.md)에서 다룹니다.

모양을 보여 주려고 만든 예시입니다. digest 는 지어낸 값을 줄였습니다.

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
  "config": {"mediaType": "application/vnd.docker.container.image.v1+json",
             "digest": "sha256:0b1c…", "size": 488},
  "layers": [
    {"mediaType": "application/vnd.ollama.image.model",
     "digest": "sha256:5e7a…", "size": 1321082688},
    {"mediaType": "application/vnd.ollama.image.template",
     "digest": "sha256:c4d2…", "size": 1392},
    {"mediaType": "application/vnd.ollama.image.params",
     "digest": "sha256:8f06…", "size": 110}
  ]
}
```

### 서버 로그의 줄 종류

`server.log` 에는 모양이 다른 줄이 섞여 있습니다. 아래는 0.6.5 샘플 줄의 모양을 따라 값을 바꾼 만든 예시입니다[2].

```
2026/03/14 09:05:11 routes.go:1231: INFO server config env="map[… OLLAMA_HOST:http://127.0.0.1:11434 … OLLAMA_KEEP_ALIVE:5m0s … OLLAMA_MODELS:C:\\Users\\labuser01\\.ollama\\models OLLAMA_NOHISTORY:false …]"
time=2026-03-14T09:05:11.402+09:00 level=INFO source=images.go:458 msg="total blobs: 0"
time=2026-03-14T09:05:11.403+09:00 level=INFO source=routes.go:1298 msg="Listening on 127.0.0.1:11434 (version 0.6.5)"
[GIN] 2026/03/14 - 09:07:30 | 404 |      1.2031ms |       127.0.0.1 | POST     "/api/show"
time=2026-03-14T09:07:31.118+09:00 level=INFO source=download.go:177 msg="downloading 5e7a90c3d1f2 in 13 100 MB part(s)"
[GIN] 2026/03/14 - 09:07:52 | 200 |   21.4410921s |       127.0.0.1 | POST     "/api/pull"
time=2026-03-14T09:07:52.640+09:00 level=INFO source=server.go:405 msg="starting llama server" cmd="…ollama.exe runner --model C:\\Users\\labuser01\\.ollama\\models\\blobs\\sha256-5e7a… --port 50123"
llama_model_loader: loaded meta data with 30 key-value pairs and 255 tensors from C:\Users\labuser01\.ollama\models\blobs\sha256-5e7a… (version GGUF V3 (latest))
llama_model_loader: - kv   2:                               general.name str              = Sample Model 1B
[GIN] 2026/03/14 - 09:08:10 | 200 |    6.0213301s |       127.0.0.1 | POST     "/v1/chat/completions"
[GIN] 2026/03/14 - 09:09:02 | 200 |     48.1102ms |       127.0.0.1 | DELETE   "/api/delete"
```

| 줄 | 알아볼 표지 | 담긴 것 |
|---|---|---|
| 설정 | `routes.go:1231: INFO server config env="map[…]"`(첫 줄) | 서버가 뜰 때 쓴 환경 변수 전체 |
| 판 | `msg="Listening on 127.0.0.1:11434 (version …)"` | 서버 주소와 Ollama 판 |
| 레이어 수 | `msg="total blobs: N"`, `msg="total unused blobs removed: N"` | 서버가 뜰 때 있던 레이어 수 |
| API 호출 | `[GIN] YYYY/MM/DD - HH:MM:SS \| 상태 \| 걸린 시간 \| 호출 IP \| 메서드 "경로"` | 요청 종류, 성공 여부, 걸린 시간, 호출한 IP |
| 받기 | `source=download.go:177 msg="downloading {digest 앞 12자} in {조각 수} {조각 크기} part(s)"` | 받은 레이어의 digest 앞부분과 크기 |
| 올리기 | `msg="starting llama server" cmd="… --model {레이어 경로} …"` | 실행한 모델 본체 레이어 경로 |
| 올리기(llama.cpp) | `llama_model_loader: loaded meta data … from {레이어 경로} (version GGUF V3 (latest))`, `general.name str = …` | 레이어 경로와 GGUF 안의 모델 이름 |

API 호출 줄에는 API 종류, 시각, 성공 여부, 걸린 시간, 호출 IP(대개 127.0.0.1)가 들어가고, 핵심 호출은 모델 목록·받기·실행·삭제·대화 요청입니다[1, §4.4]. 로그에 나오는 경로와 그 뜻은 아래와 같습니다[2][7][8].

| 경로 | 뜻 |
|---|---|
| `POST "/api/pull"` | 모델 받기 |
| `GET "/api/tags"` | 로컬 모델 목록 |
| `POST "/api/show"` | 모델 정보 보기 |
| `POST "/api/generate"` | 프롬프트 하나에 대한 답 만들기 |
| `DELETE "/api/delete"` | 모델과 그 데이터 지우기 |
| `GET "/api/version"` | 판 조회 |
| `GET "/v1/models"` | OpenAI 호환 모델 목록 |
| `POST "/v1/chat/completions"` | OpenAI 호환 대화 요청 |

받기 줄의 digest 앞 12자는 레이어 파일 이름의 `sha256-` 뒤 앞 12자와 같습니다. 조각 수와 조각 크기를 곱하면 매니페스트의 `size` 와 대략 맞습니다[2]. 받기 줄과 `/api/pull`·`/api/delete` 줄에는 모델 이름이 없습니다. 이름은 매니페스트 경로, 올리기 줄의 `general.name`, 클라이언트 앱 기록에서 찾아 digest 와 이어 붙입니다.

### 앱 로그

`app.log` 는 모든 줄이 `time=…` 모양입니다. 여기에는 `msg="ollama app started"`, `msg="app config" env="map[…]"`, `msg="started ollama server with pid N"`, 서버 로그 위치, 업데이트 확인(`msg="New update available at …"`), 서버가 멈췄다 다시 뜬 기록(`msg="server crash 1 - exit code … - respawning"`)이 남습니다[2].

### CLI 기록

`history` 는 명령줄로 친 입력을 시각 순서대로 쌓고 모델의 답은 넣지 않습니다[1, §4.4]. `/help`, `/bye` 같은 CLI 명령도 입력과 함께 한 줄씩 들어가고, 추출한 결과에는 시각 필드가 없습니다[3]. LangurTrace 공개 샘플의 `history` 는 0바이트이지만 같은 샘플의 서버 로그에는 대화 요청 줄이 남아 있습니다[2]. 그래서 `history` 가 비었다고 대화가 없었다고 보지 않습니다.

### 캐시 JSON

`.ollama\cache\` JSON 의 키 이름과 값 종류는 아래와 같습니다. 이 파일을 어느 기능이 쓰는지는 실제 기기에서 앱 동작과 맞춰 확인해야 합니다.

| 키 | 값 종류 |
|---|---|
| `recommendations` | 목록 |
| `recommendations[].model` | 문자열 |
| `recommendations[].description` | 문자열 |
| `recommendations[].context_length` | 정수 |
| `recommendations[].max_output_tokens` | 정수 |
| `recommendations[].required_plan` | 문자열 |
| `recommendations[].thinking.default` | 문자열 |
| `recommendations[].thinking.values` | 목록 |

## 증거로서 의미

**증명하는 것.** `server.log` 의 받기 줄과 `/api/pull` 줄은 그 시각에 그 digest 의 레이어를 받은 기록이고, LangurTrace 시험에서 UI 로 지운 모델 5개 모두 이 로그로 무엇을 받았는지 되살아났습니다(5/5)[1, 표 8, §5.3]. 올리기 줄은 그 모델 본체 레이어가 그 시각에 메모리에 올라갔다는 기록이고, `[GIN]` 줄은 어떤 종류의 요청이 언제 어느 IP 에서 와서 얼마 걸렸는지를 보여 줍니다. 매니페스트와 레이어가 있으면 그 모델이 그 디스크에 있었다고 쓸 수 있고, digest 로 공개 모델 허브와 맞춰 볼 수 있습니다[1, §4.4]. `history` 에 남은 줄은 명령줄로 그 입력을 친 기록입니다. `id_ed25519` 와 `id_ed25519.pub` 가 있으면 그 계정에 Ollama 키 쌍이 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 서버 로그에는 대화 본문이 없어서, `/v1/chat/completions` 줄로 대화 요청이 있었다는 것까지만 쓰고 무슨 말을 했는지는 클라이언트 앱에서 찾습니다. 요청 수와 메시지 수도 1:1 이 아니어서, 샘플에서는 Chatbox 의 첫 사용자 메시지 하나에 대화 요청 줄이 두 개 찍혔습니다[2]. `/api/delete` 줄에는 무엇을 지웠는지가 없어서, 매니페스트가 사라진 모델과 시각을 맞춰 보고 "이 시각에 삭제 요청이 있었고 그 뒤 이 모델의 매니페스트가 없다" 까지만 씁니다. 호출 IP 가 127.0.0.1 이면 같은 PC 안의 프로그램이 부른 것이지만, 어느 프로그램이었는지는 줄에 없습니다. 캐시 JSON 의 모델 이름은 사용자가 받았거나 쓴 모델이라는 근거가 되지 않고, 키 쌍이 있다는 사실만으로 모델을 올렸거나 클라우드 모델을 썼다고 단정하지 않습니다. `models` 폴더가 비어 있어도 `OLLAMA_MODELS` 로 다른 곳에 모델을 두었을 수 있으니 로그의 환경 변수 맵을 먼저 봅니다.

## 시각 해석

서버 로그에는 시각 표기가 세 가지 섞여 있습니다. 아래 예시 값은 +09:00 PC 의 샘플 값입니다[2].

| 줄 | 시각 표기 | 시간대 |
|---|---|---|
| `time=…` 로 시작하는 줄 | `2025-05-23T20:24:41.663+09:00` 모양, 밀리초까지 | 현지 시각에 UTC 오프셋이 붙음 |
| `[GIN]` 줄 | `2025/05/23 - 20:25:00`, 초까지 | 오프셋 없는 현지 시각 |
| 첫 줄 설정 | `2025/05/23 20:22:22`, 초까지 | 오프셋 없는 현지 시각 |

같은 사건의 `[GIN]` 줄과 `time=` 줄 시각이 맞으므로[2], 오프셋 없는 줄도 같은 현지 시각으로 읽으면 됩니다. 다른 PC 의 시간대는 `time=` 줄의 오프셋에서 읽고, `llama_model_loader:` 줄처럼 시각이 없는 줄은 앞뒤 줄 시각으로 자리를 잡습니다.

`[GIN]` 시각은 요청이 끝난 때에 가깝습니다. Chatbox 가 저장한 답 메시지의 `timestamp`(Unix 밀리초, UTC)를 현지 시각으로 바꾸면 같은 대화 요청의 `[GIN]` 시각과 1초 안팎으로 맞고, `[GIN]` 시각에서 걸린 시간을 빼면 사용자 메시지 시각 근처가 됩니다[2]. 그래서 요청이 시작된 때는 `[GIN]` 시각에서 걸린 시간을 빼서 추정합니다.

모델은 기본 5분 동안 메모리에 남습니다[4]. 로그의 올리기 줄이 모델이 올라간 때를 직접 보여 주므로, 메모리에 모델이 있었는지로 요청 시각을 짐작하지 않고 로그 줄로 씁니다. 캐시 JSON 에는 시각 필드가 없어서 파일 시스템 시각만 남고, 이 시각은 앱이 그 파일을 마지막으로 쓴 때입니다. `history` 는 줄마다 시각이 붙는지 실제 파일을 열어 확인하고, 시각이 없으면 파일 수정 시각을 마지막 입력 무렵으로만 봅니다.

## 함정과 한계

- **LangurTrace 출력의 시각.** `server_log.csv` 는 `time=` 줄의 오프셋을 버리고 시각만 옮기고, 정규식이 `+HH:MM` 오프셋만 받도록 짜여 있어서 `-05:00` 처럼 음수 오프셋이 붙은 줄은 받기 행이 빠집니다[2, `log_reporter.py`]. API 호출 행의 시각은 `2025/05/23 - 19:26:12`, 받기 행은 `2025-05-23 - 20:24:41.663` 으로 모양도 다릅니다[2].
- **LangurTrace 출력의 모델 올리기 행.** 올리기 행의 시각은 바로 앞의 `status="llm server loading model"` 줄에서 가져옵니다. 샘플에서는 러너를 띄우기 전에 한 번 더 찍히는 `llama_model_loader:` 줄들이 그 앞 모델의 시각을 받아, 2분 넘게 앞선 시각으로 기록된 행이 있습니다[2]. `general.name` 은 띄어쓰기 없는 이름만 잡아서 `Llama 3.2 3B Instruct` 같은 이름은 빠지고, `--ollama-engine` 으로 올린 모델은 `llama_model_loader:` 줄이 찍히지 않아 올리기 행이 아예 없습니다[2]. 올리기 시각과 이름은 CSV 의 `Original Line` 열과 원본 로그의 `starting llama server` 줄로 다시 맞춥니다.
- **도구가 다 읽지 않는 파일.** LangurTrace KAPE 타깃은 `%LocalAppData%\Ollama\` 의 `*.log` 전부와 매니페스트, 레이어, `history` 를 모으지만, 파서는 `server*.log`, 매니페스트, 레이어 이름만 읽습니다[2, `Ollama.tkape`, `ollama.py`]. `app.log`·`upgrade.log`·`history` 는 직접 엽니다. API 호출 행의 `Content` 열에는 경로만 들어가고 상태·걸린 시간·IP·메서드는 `Original Line` 에만 있습니다.
- **모델 위치.** 수집 경로가 `C:\Users\%user%\…` 로 고정이라 `OLLAMA_MODELS` 로 옮긴 모델은 모으지 않습니다[2]. `OLLAMA_MODELS` 를 바꾼 경우 제거 프로그램은 받은 모델을 지우지 않으므로[5], Ollama 를 지운 뒤에도 다른 드라이브에 모델이 남아 있을 수 있습니다.
- **로그가 돌아감.** 서버와 앱이 뜰 때마다 새 로그가 시작되고 앞선 파일은 `-1`, `-2` 로 밀립니다. 샘플에는 `-2` 까지 있었으니[2], 실제 기기에서 몇 개까지 남는지 보고 오래된 받기 기록이 이미 밀려났을 수 있다는 점을 보고서에 적습니다.
- **설치하지 않은 실행.** 압축 파일 판을 풀어 쓰면 설치 기록 없이 실행 흔적만 남을 수 있고, `/DIR` 로 다른 곳에 깐 경우도 기본 경로에 실행 파일이 없습니다. `starting llama server` 줄에는 실행 파일 경로가 통째로 찍히므로 이 경로도 봅니다[2]. [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)의 실행 흔적을 함께 봅니다.
- **외부에 열린 서버.** `OLLAMA_HOST` 를 `0.0.0.0:11434` 처럼 바꾸면 다른 기기에서도 서버를 부를 수 있습니다[4]. 이때는 `[GIN]` 줄의 호출 IP 필드를 먼저 보고, 127.0.0.1 이 아닌 줄은 그 PC 사용자의 요청이라고 바로 보지 않습니다. 설정 줄의 `OLLAMA_HOST` 값으로 그 시기에 서버가 밖에 열려 있었는지도 확인합니다.
- **개인키.** `id_ed25519` 의 내용은 보고서나 공유 자료에 싣지 않고, 파일이 있었다는 사실과 파일 시각만 적습니다. 키와 토큰을 다루는 기준은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)을 따릅니다.
- **판 차이.** 이 페이지의 로그 줄 모양과 소스 위치(`routes.go:1231`, `download.go:177`)는 0.6.5 기준이라 판이 바뀌면 달라질 수 있습니다. 0.6.5 뒤 판의 데스크톱 앱이 대화를 따로 저장하는지는 실제 기기에서 확인해야 합니다. 분석 대상의 판은 `Listening on … (version …)` 줄에서 읽습니다.

## 직접 분석해 보기

**원본 파일로.** 먼저 로그 사본에서 줄 종류별로 뽑습니다. 파일 이름은 사본 위치에 맞춥니다.

```
grep -h "source=download.go" server*.log
grep -h "^\[GIN\]" server*.log
grep -h "starting llama server\|general.name\|Listening on" server*.log
grep -h "server config env=" server*.log
```

받기 줄의 digest 앞 12자를 `blobs` 폴더의 파일 이름, 매니페스트의 `layers[].digest` 와 차례로 맞춰 보면, 남은 모델과 지워진 모델이 나뉩니다. LangurTrace 샘플에서는 받기 줄에 모델 본체 크기의 레이어가 세 번 나오지만 매니페스트는 `llama3.2\latest` 하나만 남아 있습니다[2]. 모델 본체 레이어가 남아 있으면 헥스 보기로 첫 4바이트가 `47 47 55 46`(글자로 `GGUF`)인지 보고, 맞으면 [로컬 모델 파일](model-files.md)의 GGUF 헤더 읽는 법을 따릅니다. 매니페스트·`config`·`params` 레이어는 글자 파일이라 JSON 으로 읽으면 됩니다.

**공개 도구로.** LangurTrace 는 KAPE 타깃(`Ollama.tkape`)과 모듈(`Ollama.mkape`)로 배포되고, 모듈은 `LangurTrace.exe --src %sourceDirectory% --dst %destinationDirectory% --app ollama` 를 실행합니다[2]. 결과는 `server_log.csv`(열: `Type`, `Timestamp`, `Content`, 파일, `Original Line`; `Type` 은 `API Call`, `Model Download`, `Model Load: …`)와 `model_manifest.csv`(열: `model_name`, `parameter`, `layer_name`, `digest`, `size`, `path`)입니다[2]. 매니페스트에 없는 레이어 파일은 `model_name` 이 `-` 인 행으로 붙습니다[2, `layer_reporter.py`]. 함정 절의 시각·이름 문제가 있으니 CSV 는 원본 줄과 맞춰 씁니다.

라이브 시스템이라면 `11434` 포트에서 듣는 프로세스가 있는지, `OLLAMA_HOST` 에 다른 주소가 걸려 있는지를 수집 기록에 남깁니다.

## 교차 검증

Ollama 로그만으로는 대화 내용과 부른 프로그램을 알 수 없어서, 클라이언트 앱 기록과 시각을 맞춥니다. Chatbox 설정 파일에는 `settings.ollamaHost` 가 `http://127.0.0.1:11434` 로 들어 있고, 메시지마다 `aiProvider` 가 `ollama`, `model` 이 `Ollama (llama3.2:latest)` 같은 값으로 남습니다[2]. 이 메시지 시각과 `/v1/chat/completions` 줄 시각이 맞고, 메시지의 모델이 바뀐 때에 맞춰 다른 모델의 `starting llama server` 줄이 찍혀 있어서, 받기 줄의 digest 가 어느 모델 이름인지도 이 대조로 잇게 됩니다[2].

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [로컬 AI](index.md) | Ollama 를 백엔드로 쓰는 클라이언트 앱과 대화 본문이 남는 곳 |
| [로컬 모델 파일](model-files.md) | 모델 본체 레이어의 GGUF 헤더와 이름 |
| [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) | 실행 파일이 실제로 돌았는지, 설치 없이 쓴 흔적 |
| [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) | 모델 받기와 클라우드 모델 호출로 오간 통신 |
| [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) | 로그·메시지·파일 시각을 한 줄로 세우기 |
| [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md) | 로컬 AI 사용을 묻는 조사 흐름 |

## 실습

공개 시험 데이터는 LangurTrace 저장소의 `sample_dataset` 입니다[2]. `collect/C/Users/USER/AppData/Local/Ollama/` 에 서버·앱 로그 여섯 개가, `collect/C/Users/USER/.ollama/` 에 매니페스트 하나와 작은 레이어 다섯 개, 빈 `history` 가 있고, `parse/LLM application artifacts/ollama/` 에 LangurTrace 출력이 있습니다. 모델 본체 GGUF 는 크기 때문에 빠져 있습니다.

1. `server-2.log`, `server-1.log`, `server.log` 가 시작한 시각과 그때의 Ollama 판은 무엇입니까?
2. 받기 줄에 나온 모델 본체 레이어는 몇 개이고, 그 가운데 매니페스트가 남은 것은 무엇입니까? `/api/delete` 줄의 시각과 함께 적어 봅니다.
3. `server_log.csv` 의 `Model Load` 행 시각을 원본 로그의 `starting llama server` 줄과 비교하면 어느 행이 어긋납니까?
4. 같은 샘플의 Chatbox 설정 파일에서 `aiProvider` 가 `ollama` 인 메시지 시각을 현지 시각으로 바꾸고, `/v1/chat/completions` 줄과 짝지어 봅니다. 짝이 없는 요청 줄은 몇 개입니까?
5. 시험용 가상 머신에 Ollama 를 깔고 가짜 사용자 `labuser01` 로 명령줄 대화를 해 본 뒤, `OLLAMA_NOHISTORY` 를 `true` 로 두었을 때와 두지 않았을 때 `history` 가 어떻게 다른지 봅니다.

## 참고 문헌

1. Jeong, S., Lee, S., Park, J., "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. https://doi.org/10.1016/j.fsidi.2025.301987 (§4.1, §4.4, §5.3, 표 3, 표 8, 부록 A)
2. jeongramon/LangurTrace, https://github.com/jeongramon/LangurTrace — `src/apps/ollama.py`, `src/reporter/ollama/log_reporter.py`, `src/reporter/ollama/manifest_reporter.py`, `src/reporter/ollama/layer_reporter.py`, `dist/Targets/LLMApplications/Ollama.tkape`, `dist/Modules/LLMApplications/Ollama.mkape`, `sample_dataset/collect/C/Users/USER/AppData/Local/Ollama/`, `sample_dataset/collect/C/Users/USER/.ollama/`, `sample_dataset/collect/C/Users/USER/AppData/Roaming/xyz.chatboxapp.app/config-backup-2025-05-23T11_36_10.169Z.json`, `sample_dataset/parse/LLM application artifacts/ollama/`
3. k0w4lzk1/LangurTrace-Implementation, https://github.com/k0w4lzk1/LangurTrace-Implementation — `Ourimplementation/correlation/kape/ollama_extracted_prompts.csv`
4. Ollama, "FAQ", https://docs.ollama.com/faq (2026-09-25 열람)
5. Ollama, "Windows", https://docs.ollama.com/windows (2026-09-25 열람)
6. Ollama, "Troubleshooting", https://docs.ollama.com/troubleshooting (2026-09-25 열람)
7. Ollama, "API", https://github.com/ollama/ollama/blob/main/docs/api.md (2026-09-25 열람)
8. Ollama, "OpenAI compatibility", https://docs.ollama.com/api/openai-compatibility (2026-09-25 열람)
