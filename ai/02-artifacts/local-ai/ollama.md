---
title: "Ollama"
parent: "아티팩트 · 로컬 AI"
nav_order: 650
---

# Ollama (Ollama)

Ollama 는 내려받은 언어 모델을 자기 컴퓨터에서 돌리는 도구이고, 모델·키·캐시는 사용자 홈 폴더의 `.ollama` 에 두며 Windows 에서는 앱·서버 로그를 `%LOCALAPPDATA%\Ollama` 에 따로 남깁니다.

> 확인 날짜: 2026-09. 위치와 설정은 공식 문서(2026-09-25 열람)를 근거로 썼고, `.ollama` 폴더 안의 파일 이름과 캐시 파일의 키 이름은 Windows 11 PC 한 대에서 읽은 것입니다. 그 PC 에 깔린 Ollama 버전은 확인하지 못해서 버전 번호는 적지 않습니다. macOS·Linux 는 기기를 보지 않았고 문서만 근거로 합니다.

## 무엇을 기록하나 · 왜 생기나

Ollama 는 모델을 받아 디스크에 두고 로컬 서버를 띄운 다음, 앱·명령줄·다른 프로그램이 보낸 요청을 받아 모델을 돌립니다. 공식 문서는 로컬에서 돌릴 때 Ollama 가 프롬프트와 데이터를 보지 않는다고 적고 있어서("Ollama runs locally. We don't see your prompts or data when you run locally."), 로컬 실행 대화는 서비스 회사에 요청해 받을 원본이 없고 기기에 남은 흔적이 조사의 중심이 됩니다. 서버가 어디에 있고 데이터가 어디에 남는지의 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

`.ollama` 폴더에는 Ollama 공개키(`id_ed25519.pub`)도 있고, 문서는 이 키를 모델을 Ollama 에 올리거나 비공개 모델을 받아 올 때 쓴다고 설명합니다. Ollama 는 클라우드 모델도 부를 수 있지만, 클라우드 모델로 나눈 대화를 서버에 얼마나 보관하는지는 이번에 문서로 확인하지 못했습니다.

디스크에 남는 것은 받은 모델 파일, 모델을 올리거나 비공개 모델을 받을 때 쓰는 키 쌍, 앱이 받아 둔 캐시, 앱·서버·업그레이드 로그입니다. 대화 내용이 어디에 어떤 형식으로 남는지는 문서로 확인하지 못했고, 관찰한 PC 의 `.ollama` 폴더에도 대화 파일로 볼 만한 것은 없었습니다 (확인 범위: Windows 11, 2026-09).

## 위치와 버전별 차이

### Windows

Windows 판은 관리자 권한 없이 홈 폴더 아래에 깔리고, 설치 프로그램을 `OllamaSetup.exe /DIR="..."` 처럼 실행하면 다른 폴더에 깔 수도 있습니다. 설치하지 않고 압축만 풀어 쓰는 명령줄 판(`ollama-windows-amd64.zip`, `ollama-windows-amd64-rocm.zip`, `ollama-windows-amd64-mlx.zip`)도 공식으로 내려받을 수 있습니다.

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%LOCALAPPDATA%\Programs\Ollama` | 실행 파일(설치할 때 PATH 에 추가) | 문서 |
| `%LOCALAPPDATA%\Ollama\app.log` | GUI 앱 로그 | 문서 |
| `%LOCALAPPDATA%\Ollama\server.log` | 서버 로그 | 문서 |
| `%LOCALAPPDATA%\Ollama\upgrade.log` | 업그레이드할 때의 출력 | 문서 |
| `%TEMP%` 아래 `ollama` 로 시작하는 폴더 | 임시 실행 파일 | 문서 |
| `%HOMEPATH%\.ollama` | 모델과 설정 | 문서 |
| `C:\Users\%username%\.ollama\models` | 받은 모델(기본 위치) | 문서 |
| `%USERPROFILE%\.ollama\id_ed25519.pub` | Ollama 공개키(모델 올리기·비공개 모델 받기에 씀) | 문서, 관찰 |
| `%USERPROFILE%\.ollama\id_ed25519` | 짝이 되는 개인키 | 관찰 |
| `%USERPROFILE%\.ollama\cache\` 아래 JSON 파일 | 추천 모델 목록으로 보이는 캐시 | 관찰 |

관찰한 PC 의 `.ollama` 폴더에는 파일이 캐시 JSON 하나, `id_ed25519`, `id_ed25519.pub` 세 개뿐이었고 `models` 아래에는 파일이 없었습니다 (확인 범위: Windows 11, 2026-09). 문서는 공개키만 언급하지만 같은 폴더에 개인키도 있었습니다. 관찰 범위가 `.ollama` 폴더뿐이어서 `%LOCALAPPDATA%\Ollama` 의 로그는 이 PC 에서 보지 않았습니다.

### macOS·Linux

| 항목 | macOS | Linux |
|---|---|---|
| 모델 기본 위치 | `~/.ollama/models` | `/usr/share/ollama/.ollama/models` |
| Ollama 공개키 | `~/.ollama/id_ed25519.pub` | `/usr/share/ollama/.ollama/id_ed25519.pub` |
| 환경 변수를 거는 곳 | `launchctl setenv` | `systemctl edit ollama.service` 로 연 설정의 `[Service]` 아래 `Environment="..."` 줄 |
| 로그 | 확인하지 못함 | 확인하지 못함 |

Linux 기본 위치가 사용자 홈이 아니라 `/usr/share/ollama` 아래라서, 사용자 홈 폴더만 수집하면 모델과 키가 빠집니다.

### 동작을 바꾸는 환경 변수

| 변수 | 하는 일 | 기본값 |
|---|---|---|
| `OLLAMA_MODELS` | 모델 저장 위치를 바꿈 | 위 표의 기본 위치 |
| `OLLAMA_HOST` | 서버가 붙는 주소와 포트 | `127.0.0.1` 의 `11434` 포트 |
| `OLLAMA_ORIGINS` | 교차 출처 요청을 더 허용할 출처 | `127.0.0.1`·`0.0.0.0` 에서 온 요청 허용 |
| `OLLAMA_KEEP_ALIVE` | 모델을 메모리에 남겨 두는 시간(API 의 `keep_alive` 로도 바꿈) | 5분 |

Windows 에서는 이 변수를 설정 앱의 사용자 계정 환경 변수로 겁니다. 디스크 이미지에서는 그 사용자의 레지스트리 하이브에 든 사용자 환경 변수를 읽어 값이 있는지 봅니다.

## 구조

관찰한 PC 의 `.ollama` 폴더 모양은 아래와 같고, 캐시 파일 이름은 가렸습니다 (확인 범위: Windows 11, 2026-09).

```
.ollama/
  cache/<파일>.json
  id_ed25519
  id_ed25519.pub
```

캐시 JSON 에서 읽은 키 이름과 값 종류는 다음과 같습니다 (확인 범위: Windows 11, 2026-09).

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

모양을 보여 주려고 만든 예시입니다. 모델 이름과 값은 모두 지어낸 것이고 관찰한 파일의 값이 아닙니다.

```json
{
  "recommendations": [
    {
      "model": "sample-model:7b",
      "description": "만든 예시 설명",
      "context_length": 8192,
      "max_output_tokens": 4096,
      "required_plan": "free",
      "thinking": { "default": "off", "values": ["off", "on"] }
    }
  ]
}
```

키 이름으로 보아 이 파일은 앱이 보여 주는 추천 모델 목록을 받아 둔 캐시로 보이지만, 이를 밝힌 문서는 찾지 못했습니다. `models` 폴더 안의 짜임과 모델 파일 형식도 이번에 문서로 확인하지 못했고, 관찰한 PC 에는 모델 파일이 없었습니다. 모델 파일을 바이트로 읽는 법은 [로컬 모델 파일](model-files.md)에서 다룹니다. 세 로그 파일의 줄 형식도 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것.** `%LOCALAPPDATA%\Programs\Ollama` 나 `.ollama` 폴더가 있으면 그 사용자 계정에 Ollama 를 깔았거나 실행한 흔적이 있다고 쓸 수 있습니다. 모델 폴더에 파일이 있으면 그 모델이 그 디스크에 있었다고 쓸 수 있고, `id_ed25519` 와 `id_ed25519.pub` 가 있으면 그 계정에 Ollama 키 쌍이 만들어진 적이 있다고 쓸 수 있습니다. `server.log` 와 `app.log` 에 남은 줄은 로그가 적은 범위만큼 서버와 앱이 동작한 기록이 됩니다.

**증명하지 못하는 것.** 대화 내용이 어디에 남는지 확인하지 못했으므로 `.ollama` 폴더에 대화 파일이 없다고 대화가 없었다고 쓰지 않습니다. 캐시의 `recommendations` 는 추천 목록으로 보이는 값이라서, 거기 적힌 모델을 사용자가 받았거나 썼다는 근거가 되지 않습니다. 키 쌍을 언제 만드는지 문서로 확인하지 못해서, 키가 있다는 사실만으로 모델을 올렸거나 비공개 모델·클라우드 모델을 썼다고 단정하지 않습니다. `models` 폴더가 비어 있어도 `OLLAMA_MODELS` 로 다른 곳에 모델을 두었을 수 있습니다.

## 시각 해석

캐시 JSON 의 키 가운데 시각 값은 보이지 않았습니다 (확인 범위: Windows 11, 2026-09). 그래서 시각은 파일 시스템 시각에 기대게 됩니다. 캐시 파일의 수정 시각은 앱이 캐시를 마지막으로 새로 쓴 때로 보고, 사용자가 무엇을 한 때와 바로 잇지 않습니다. 키 파일의 생성 시각은 키를 만든 때에 가깝다고 볼 수 있지만 어떤 조건에서 만드는지는 확인하지 못했습니다. 로그 줄의 시각 표기와 시간대(UTC 인지 현지 시각인지)도 확인하지 못했으므로, 같은 때에 남은 운영체제 기록과 맞춰 보고 차이를 적습니다.

모델은 기본 5분 동안 메모리에 남았다가 내려갑니다. 라이브 시스템에서 메모리를 뜰 때 모델이 올라가 있었다면 최근 몇 분 안에 요청이 있었을 수 있지만, `OLLAMA_KEEP_ALIVE` 값을 먼저 확인하고 해석합니다.

## 함정과 한계

- **모델 위치.** `OLLAMA_MODELS` 로 옮긴 모델 폴더는 제거 프로그램이 지우지 않습니다. Ollama 를 지운 뒤에도 다른 드라이브에 모델이 남아 있을 수 있어서, 사용자 환경 변수 값과 큰 파일이 모인 폴더를 함께 찾습니다.
- **설치하지 않은 실행.** 압축 파일 판을 풀어 쓰면 설치 기록 없이 실행 흔적만 남을 수 있습니다. 설치 프로그램 목록에 없다고 쓰지 않았다고 보지 않고, [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)의 실행 흔적을 함께 봅니다. `/DIR` 로 다른 곳에 깐 경우도 같습니다.
- **외부에 열린 서버.** `OLLAMA_HOST` 를 `0.0.0.0:11434` 처럼 바꾸면 다른 기기에서도 서버에 접속할 수 있습니다. 사고 조사에서 이 값이 걸려 있었다면 서버 로그에 남은 요청을 그 PC 사용자의 요청이라고 바로 보지 않고, 네트워크 기록으로 요청이 어디서 왔는지 따로 확인합니다.
- **개인키.** `id_ed25519` 의 내용은 보고서나 공유 자료에 싣지 않고, 파일이 있었다는 사실과 파일 시각만 적습니다. 키와 토큰을 다루는 기준은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)을 따릅니다.
- **대화 저장.** 데스크톱 앱이 채팅 기록을 어디에 어떤 형식으로 두는지는 확인하지 못했습니다. SQLite 같은 특정 형식이라고 단정하지 않습니다.

## 직접 분석해 보기

**헥스로.** `.ollama` 의 캐시와 공개키는 글자 파일이라 헥스로 볼 것이 적습니다. 모델 폴더에서 파일이 나오면 헥스 보기로 첫 바이트를 봅니다. Ollama 모델 파일의 형식은 이번에 문서로 확인하지 못했으므로, 첫 4바이트가 `47 47 55 46`(글자로 `GGUF`) 인지 직접 확인하고 맞으면 [로컬 모델 파일](model-files.md)의 GGUF 헤더 읽는 법을 따릅니다.

**공개 도구로.** 캐시 JSON 은 사본을 떠서 `jq` 같은 공개 도구로 읽습니다. 파일 이름은 만든 예시입니다.

```
jq '.recommendations[].model' .ollama/cache/sample-cache.json
```

라이브 시스템이라면 `11434` 포트에서 듣고 있는 프로세스가 있는지, `OLLAMA_HOST` 에 다른 주소가 걸려 있는지를 수집 기록에 남깁니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) | 실행 파일이 실제로 돌았는지, 설치 없이 쓴 흔적 |
| [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) | 모델 내려받기와 클라우드 모델 호출로 오간 통신 |
| [로컬 모델 파일](model-files.md) | 디스크에 있는 모델의 이름·출처 URL·라이선스 |
| [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) | 로그·파일 시각을 다른 기록과 한 줄로 세우기 |
| [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md) | 로컬 AI 사용을 묻는 조사 흐름 |

## 실습

공개 검체 가운데 Ollama 가 든 것은 확인하지 못했습니다. 시험용 가상 머신에 직접 깔고 가짜 사용자 `labuser01` 로 모델 하나를 받아 본 다음, 아래 질문을 풀어 봅니다.

1. 설치 직후와 첫 실행 뒤에 `.ollama` 폴더에 생기는 파일은 무엇이고, 키 쌍은 어느 시점에 생깁니까?
2. `OLLAMA_MODELS` 를 다른 드라이브로 바꾸고 모델을 받은 뒤 제거하면, 어떤 파일이 남습니까?
3. `server.log` 한 줄의 시각을 운영체제 이벤트 시각과 비교하면 시간대가 맞습니까?
4. 압축 파일 판만 풀어 실행했을 때, 설치 프로그램 목록과 실행 흔적에는 각각 무엇이 남습니까?

## 참고 문헌

1. Ollama, "FAQ", https://docs.ollama.com/faq (2026-09-25 열람)
2. Ollama, "Windows", https://docs.ollama.com/windows (2026-09-25 열람)
