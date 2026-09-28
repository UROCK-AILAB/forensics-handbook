---
title: "GPT4All"
parent: "아티팩트 · 로컬 AI"
nav_order: 730
---

# GPT4All

GPT4All 은 모델 내려받기와 대화 화면을 한 프로그램에 담은 통합형 로컬 AI 앱이고, Windows 에서는 모델 파일(`.gguf`)·원격 모델 설정(`.rmodel`)·대화 기록(`.chat`)이 모두 `%LocalAppData%\nomic.ai\GPT4ALL\` 한 폴더에 남습니다.

이 페이지는 Windows 11 Pro 24H2 의 GPT4All 3.10.0 기준이고[1], 새 판은 구조가 다를 수 있으니 분석 대상 앱의 판을 먼저 적습니다.

## 무엇을 기록하나 · 왜 생기나

로컬 LLM 환경은 백엔드 런타임, 클라이언트 화면, 통합형으로 나눌 수 있고, GPT4All 은 통합형입니다[1, §3.3, 표 1]. 통합형은 모델을 받아 돌리는 일과 대화 화면을 한 앱이 모두 맡아서, 백엔드 쪽 흔적(모델 파일)과 클라이언트 쪽 흔적(대화·설정·API 키)이 함께 생깁니다. 분류 전체의 틀은 [로컬 AI](index.md) 허브에서 다룹니다.

GPT4All 은 대화 하나를 자체 이진 형식의 `.chat` 파일 하나로 저장합니다(§4.6.4). 이 형식의 특징은 대화 중에 올린 파일의 내용이 `.chat` 안에 통째로 들어간다는 점입니다. 다른 로컬 LLM 앱은 대화 기록에 파일 경로·메타데이터만 적고 파일은 따로 두지만, GPT4All 은 `.chat` 하나에서 대화와 올린 파일을 함께 꺼낼 수 있습니다[1, §4.6.4, 그림 6]. 프롬프트·첨부·생성물을 나눠 보는 기준은 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)를 따릅니다.

클라우드 모델을 API 키로 연결해 쓰면 그 설정이 `.rmodel` 파일에 남습니다. API 키로 쓰는 클라우드 대화는 대개 서버가 대화 문맥을 보관하지 않고, 로컬 앱이 매번 다시 보냅니다[1, §3.4]. 그래서 원격 모델로 나눈 대화도 로컬의 `.chat` 이 주된 기록입니다. 서비스 쪽 저장의 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

## 위치와 버전별 차이

| 경로 | 담긴 것 | 형식 | 근거 |
|---|---|---|---|
| `%LocalAppData%\nomic.ai\GPT4ALL\{모델 이름}.gguf` | 내려받은 모델 | GGUF | 부록 A·B [1], 수집 타깃 [3] |
| `%LocalAppData%\nomic.ai\GPT4ALL\gpt4all-{ID}.rmodel` | 원격 모델 설정: API 키, 제공자 주소, 모델 이름 | JSON | 부록 A·B [1], 파서 [2] |
| `%LocalAppData%\nomic.ai\GPT4ALL\gpt4all-{ID}.chat` | 대화 설정, 대화 기록, 올린 파일 | 자체 이진 형식 | 부록 A·B [1], §4.6.4 |

`.chat` 파일 이름의 `{ID}` 는 샘플에서 UUID 였고, 파일 안 머리 부분에 같은 UUID 가 다시 들어 있습니다. LangurTrace 수집 타깃 [3] 은 `C:\Users\%user%\AppData\Local\nomic.ai\GPT4ALL\` 에서 `*.gguf`, `*.rmodel`, `*.chat` 세 가지만 모읍니다.

GPT4All 에 남는 아티팩트는 아래와 같습니다[1, 표 5]. ✩ 는 "있지만 지우면 대개 되살릴 수 없음", ⨯ 는 "없음", – 는 "기능 없음" 입니다.

| 항목 | GPT4All |
|---|---|
| 내려받은 모델 | ✩ |
| 모델 설치 기록 | ⨯ |
| 대화 설정 | ✩ |
| 대화 기록 | ✩ |
| 올린 파일 | ✩ |
| 생성 파일 | – |
| API 키 | ✩ |

LM Studio 의 `download-jobs-info.json`([LM Studio](lm-studio.md))이나 Ollama 의 서버 로그([Ollama](ollama.md))처럼 모델을 받은 기록을 따로 두는 파일이 GPT4All 에는 없습니다.

macOS·Linux 경로는 실제 기기로 확인해야 합니다. LangurTrace 시험은 Windows 에서만 했고, 다른 OS 에서도 아티팩트 종류는 비슷할 것이라는 추정만 있습니다[1, §4.1, §6.2].

## 구조

### `.rmodel`

원격 모델 하나의 설정을 담은 JSON 입니다. LangurTrace 파서 [2] 는 `apiKey`, `baseUrl`, `modelName` 세 키를 읽어 `remote_config.csv` 로 냅니다. 이 파일에서 증거로 쓰는 값은 API 키와 모델 제공자입니다[1, 부록 B]. 공개 샘플 [4] 에는 `.rmodel` 이 들어 있지 않으므로, 이 세 키 밖의 키는 실제 파일에서 읽어 봅니다.

### `.chat`

아래는 공개 샘플 세 파일[4]에서 본 모양입니다. 머리 부분과 대화 항목의 문자열은 모두 "4바이트 빅엔디언 바이트 길이 + UTF-16BE 글자" 짜임입니다.

| 위치 | 크기 | 샘플 값 |
|---|---|---|
| 0x00 | 4 | `F5 D5 53 CC` (세 파일 모두 같음) |
| 0x04 | 4 | 빅엔디언 정수 `0x0000000C`(12). 형식 판 번호로 보이는 값 |
| 0x08 | 8 | 빅엔디언 Unix 초. 세 파일 모두 2025-05-23 12:2x UTC |
| 0x10 | 가변 | 문자열: 파일 이름과 같은 UUID |
| 이어서 | 가변 | 문자열 세 개: 대화 이름으로 쓰이는 문구, `Chat A` 처럼 짧은 문자열, 모델 표시 이름 |
| 이어서 | 8 | 빅엔디언 정수. 샘플에서는 최상위 `Prompt: `·`Response: ` 항목 수와 같았음 |
| 이어서 | 가변 | 대화 항목들 |

대화 항목은 `Prompt: ` 또는 `Response: ` 라는 표지 문자열 뒤에 본문 문자열이 오는 짜임입니다. 본문 뒤에는 `FF FF FF FF` 와 0 바이트가 이어졌습니다. 추론 모델로 나눈 대화에는 `Think: ` 표지 뒤에 `<think>` 로 시작하는 생각 과정 글이 들어간 항목도 있었습니다. 이 항목은 답 항목 아래에 딸린 `Response: ` 표지 뒤에 붙었고, 이 딸린 표지는 본문 길이 자리가 `FF FF FF FF` 였습니다. 머리 부분의 항목 수에는 이 딸린 표지가 들어가지 않았습니다.

올린 파일은 그 질문 항목 뒤에 들어갑니다. 샘플에서는 `file:///` 로 시작하는 원래 경로가 UTF-8 로, 그 뒤에 파일 내용이 원래 바이트 그대로 들어 있었고, 둘 다 앞에 4바이트 빅엔디언 길이가 붙어 있었습니다. 경로가 사용자 PC 의 원래 위치(드라이브 문자 포함)를 가리키므로, 그 파일이 어디에 있었는지도 여기서 읽습니다.

샘플에서는 첨부나 생각 과정이 없는 대화에서도 두 번째 질문부터 문자열이 홀수 오프셋에서 시작하기도 했습니다. 그래서 2바이트 정렬을 가정하고 읽으면 뒤쪽 항목을 잘못 읽습니다.

위 필드 가운데 이름을 붙인 것(판 번호, 대화 이름, 항목 수)은 샘플 값으로 추정한 뜻입니다. 실제 데이터는 앱 화면의 대화 목록·모델 이름과 맞춰 한 번 더 확인합니다.

### 모델 파일

모델은 폴더 구분 없이 `GPT4ALL` 폴더 바로 아래 `{모델 이름}.gguf` 로 놓입니다(부록 A). GGUF 머리를 읽는 법과 해시로 출처를 찾는 법은 [로컬 모델 파일](model-files.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `.chat` 파일이 있으면 그 사용자 계정의 GPT4All 에 그 대화가 저장되어 있었고, 파일 안의 모델 표시 이름으로 어떤 모델과 대화했는지 쓸 수 있습니다. 올린 파일의 원래 경로와 내용이 `.chat` 에 들어 있으면, 그 경로의 파일을 이 앱의 대화에 넣은 기록이 있다고 쓸 수 있고, 원본 파일을 지웠어도 `.chat` 속 내용으로 무엇을 넣었는지 봅니다. 이 점은 [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) 같은 조사에서 쓸모가 큽니다. `.rmodel` 이 있으면 클라우드 모델을 API 키로 연결해 둔 적이 있다고 쓸 수 있습니다.

**증명하지 못하는 것.** `.chat` 은 계정 폴더에 남을 뿐이라서, 그 대화를 누가 쳤는지는 따로 밝혀야 합니다([그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)). 모델 파일이 있다고 그 모델로 대화했다는 뜻은 아니고, 모델 파일이 없다고 받은 적이 없다는 뜻도 아닙니다. 모델 설치 기록이 없어서, LangurTrace 시험에서 지운 모델은 앱 기록으로 되살아나지 않았습니다(0/5)[1, 표 5·8]. `.rmodel` 만으로는 그 원격 모델로 실제 대화했는지 알 수 없으므로, `.chat` 의 모델 표시 이름과 맞춰 봅니다.

**API 키.** `.rmodel` 의 `apiKey` 에는 키가 평문으로 남을 수 있어서, 보고서와 공유 사본에서는 가립니다. 이 키는 서비스 회사에 서버 쪽 자료를 요청하는 절차에 쓸 수 있습니다[1, §4.3]. 요청 절차는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md), 키가 남는 곳의 일반 원리는 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에서 다룹니다.

## 시각 해석

샘플 `.chat` 에는 시각 값이 머리 부분 0x08 의 8바이트 하나뿐이었고, 메시지마다 붙은 시각은 없었습니다. 값은 Unix 초라서 UTC 기준이고, 현지 시각으로 옮길 때는 분석 대상 기기의 시간대를 따로 적습니다. 이 값이 대화를 만든 시각인지 마지막으로 저장한 시각인지 밝힌 문서는 없습니다. 시험 기기에서 새 대화를 만든 뒤 시간을 두고 이어서 대화해 이 값이 바뀌는지로 확인합니다.

메시지 하나하나의 시각은 `.chat` 에서 나오지 않으므로, 대화가 이어진 시간대는 `.chat` 의 파일 시스템 시각과 다른 기록을 맞춰 추정합니다. 원격 모델로 대화했다면 네트워크 기록([AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md))에서 요청 시각을 찾습니다. 시각을 한 줄로 맞추는 법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **지운 뒤 복구.** LangurTrace 시험에서 앱 화면으로 지운 대화는 0/50, 지운 모델은 0/5 가 되살아났습니다[1, 표 8]. 이 값은 디스크에 남은 파일만 본 결과이고, 볼륨 섀도 복사본과 메모리는 시험 범위에 들지 않았습니다[1, §6.2]. 지운 `.chat` 을 더 찾으려면 섀도 복사본과 할당되지 않은 영역을 봅니다. 샘플 머리 4바이트 `F5 D5 53 CC` 로 검색하는 방법을 쓸 수 있고, 이렇게 되살린 결과는 시험 기기에서 지운 `.chat` 으로 먼저 재현해 보고 씁니다. 일반 절차는 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)에서 다룹니다.
- **LangurTrace 대화 출력.** 논문은 지우지 않은 GPT4All 아티팩트를 모두 파싱했다고 적었습니다(§5.3, 2025-11 공개). 그런데 저장소 코드 [2](커밋 `0416e72`, 2025-07-20)는 본문 길이를 4바이트 길이의 마지막 1바이트로만 읽고, 0 바이트를 지운 뒤 UTF-8 로 풉니다. 그래서 255바이트를 넘는 답은 잘리고, 한글처럼 ASCII 밖의 글자는 제대로 나오지 않습니다. 저장소의 샘플 출력 [4] 에서도 긴 답이 수십 글자에서 끊기고, 본문 없이 첨부만 단 질문 칸에는 첨부 경로·내용과 뒤따르는 답이 섞여 나옵니다. 첨부 내용도 길이를 1바이트로만 읽어 255바이트를 넘으면 잘립니다. 코드는 `Think: ` 를 따로 찾지 않지만, 샘플 출력에서는 생각 과정 글 일부가 `Think: ` 로 시작하는 답 칸으로 섞여 나옵니다. 출력 HTML 은 질문을 모두 먼저 싣고 답을 그 뒤에 싣습니다. 보고서에 쓸 본문은 원본 `.chat` 에서 직접 읽어 확인합니다.
- **수집 위치 고정.** LangurTrace 타깃 [3] 은 `C:\Users\%user%\...` 한 곳만 모읍니다. 다른 드라이브나 다른 폴더에 둔 모델은 모으지 않으므로, 디스크 전체에서 `.gguf` 를 찾습니다.
- **모델 해시.** LangurTrace 는 `.gguf` 파일 전체의 SHA-256 을 `model_index.csv`(`file_name`, `size`, `sha256`)로 냅니다 [2]. 파일이 크므로 수집 사본에서 계산하고, 해시 대조 절차는 [로컬 모델 파일](model-files.md)을 따릅니다.

## 직접 분석해 보기

**헥스로.** `.chat` 사본을 헥스 보기로 열어 머리 부분을 읽습니다. 아래는 샘플 구조를 따라 만든 예시이고, 값은 모두 지어낸 것입니다.

```
00000000: f5 d5 53 cc 00 00 00 0c 00 00 00 00 6a 0f 1e 40
00000010: 00 00 00 48 00 33 00 66 00 32 00 61 00 39 00 63
00000020: 00 31 00 30 00 2d 00 35 00 62 00 37 00 65 00 2d
```

0x04 의 `00 00 00 0c` 는 12, 0x08 의 `00 00 00 00 6a 0f 1e 40` 은 Unix 초 1779375680 이라서 2026-05-21 15:01:20 UTC 입니다. 0x10 의 `00 00 00 48` 은 뒤따르는 UTF-16BE 문자열이 72바이트(36글자)라는 뜻이고, 그 문자열이 UUID `3f2a9c10-...` 입니다(만든 예시). 대화 항목은 UTF-16BE `Prompt: `(`00 50 00 72 00 6f ...`)와 `Response: ` 를 찾아 그 뒤 4바이트 길이만큼 읽습니다. 첨부는 ASCII `file:///` 를 찾고, 그 앞 4바이트가 경로 길이, 경로 뒤 4바이트가 내용 길이입니다.

**공개 도구로.** 수집은 LangurTrace 의 KAPE 타깃 `GPT4All.tkape`, 파싱은 모듈 `GPT4All.mkape` 로 합니다 [3]. 모듈이 실행하는 명령은 아래와 같고, 결과로 `remote_config.csv`, `model_index.csv`, `conversations\{파일 이름}.html` 과 첨부를 풀어 둔 `{파일 이름}_files\` 가 나옵니다 [2].

```
LangurTrace.exe --src %sourceDirectory% --dst %destinationDirectory% --app gpt4all
```

HTML 은 위 함정 때문에 원본과 한 번씩 맞춰 봅니다. 앞의 헥스 방식대로 길이 4바이트를 빅엔디언으로 읽는 짧은 스크립트를 따로 두면 비교하기 쉽습니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [로컬 모델 파일](model-files.md) | `.gguf` 의 메타데이터와 해시로 모델 출처 찾기 |
| [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) | `.rmodel` 의 키를 다루는 기준 |
| [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) | 원격 모델 요청과 모델 내려받기 통신 |
| [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) | 앱 설치·실행 흔적과 수집 범위 |
| [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) | `.chat` 머리 시각과 파일 시각을 다른 기록과 맞추기 |
| [LM Studio](lm-studio.md), [Msty](msty.md), [Jan](jan.md) | 같은 통합형 앱. 모델 설치 기록이 남는 앱과 비교 |
| [Ollama](ollama.md), [Chatbox](chatbox.md) | 같은 PC 의 다른 로컬 AI 도구 |

## 실습

LangurTrace 저장소 [4] 의 `sample_dataset/collect/C/Users/USER/AppData/Local/nomic.ai/GPT4ALL/` 에 `.chat` 세 개가 있고, `sample_dataset/parse/LLM application artifacts/gpt4all/` 에 LangurTrace 출력이 있습니다. 모델 파일(GGUF)은 크기 때문에 빠져 있고(저장소 README), `.rmodel` 도 없습니다.

1. 세 `.chat` 의 0x08 시각을 UTC 와 한국 시각으로 옮기고, 세 대화를 만든 순서를 적어 봅니다.
2. 각 대화에 쓴 모델 표시 이름을 머리 부분에서 읽고, `parse` 의 `model_index.csv` 에 있는 모델 파일 이름과 짝지어 봅니다.
3. 첨부가 든 `.chat` 에서 원래 경로와 내용 길이를 읽고, `parse` 의 `_files` 폴더에 풀린 파일과 크기·내용이 같은지 봅니다.
4. 가장 긴 `Response: ` 항목의 길이 값을 읽고, `parse` 의 HTML 에 나온 글자 수와 비교해 봅니다.
5. 추론 모델로 나눈 대화에서 `Think: ` 항목을 찾아, HTML 에 그 내용이 나오는지 봅니다.

## 참고 문헌

1. Jeong, S., Lee, S., Park, J., "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. https://doi.org/10.1016/j.fsidi.2025.301987 (§3.3, §3.4, §4.1, §4.3, §4.6.4, §5.3, §6.2, 표 1·5·8, 부록 A·B)
2. LangurTrace 파서 코드, https://github.com/jeongramon/LangurTrace — `src/apps/gpt4all.py`, `src/reporter/gpt4all/conversation_reporter.py`, `src/reporter/gpt4all/configuration_reporter.py`, `src/reporter/gpt4all/model_reporter.py` (커밋 `0416e72`, 2025-07-20)
3. LangurTrace KAPE 타깃·모듈, https://github.com/jeongramon/LangurTrace — `dist/Targets/LLMApplications/GPT4All.tkape`, `dist/Modules/LLMApplications/GPT4All.mkape`
4. LangurTrace 공개 샘플, https://github.com/jeongramon/LangurTrace — `sample_dataset/collect/C/Users/USER/AppData/Local/nomic.ai/GPT4ALL/`, `sample_dataset/parse/LLM application artifacts/gpt4all/`, `README.md`
