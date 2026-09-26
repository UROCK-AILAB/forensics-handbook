---
title: "LM Studio"
parent: "아티팩트 · 로컬 AI"
nav_order: 690
---

# LM Studio (LM Studio)

LM Studio 는 모델을 내려받아 자기 컴퓨터에서 대화하는 데스크톱 앱이고, Windows 에서는 `%UserProfile%\.lmstudio` 아래에 모델 설치 기록(`download-jobs-info.json`), 모델 파일, 대화 JSON, 올린 파일과 그 메타데이터가 남습니다.

이 페이지의 경로와 키는 Windows 11 24H2 의 LM Studio 0.3.14 기준입니다[3]. LM Studio 는 자주 바뀌어서 새 판에서는 경로와 키가 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

LM Studio 는 모델을 받아 돌리는 일과 대화 화면을 한 프로그램에서 함께 하는 통합형(integrated platform) 앱입니다[3 §3.3]. 그래서 Ollama 같은 백엔드 런타임이 남기는 모델 흔적과 Chatbox 같은 대화 화면 앱이 남기는 대화 흔적이 한 폴더에 같이 생깁니다. 로컬 AI 앱을 이렇게 나누는 틀은 [로컬 AI](index.md)에서 다룹니다.

LM Studio 는 모델 설치 기록, 대화, 올린 파일의 메타데이터를 대부분 JSON 으로 저장합니다[3 §4.6.1]. 이 가운데 모델 설치 기록은 모델 파일과 따로 `download-jobs-info.json` 에 쌓이기 때문에, 사용자가 모델을 지워도 받은 기록은 남습니다[3 §4.6.1]. 대화에 올린 파일은 원본과 메타데이터 JSON 이 `user-files` 폴더에 따로 저장됩니다[3 부록 A·B]. 프롬프트·첨부·생성물을 나눠 보는 기준은 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)를 따릅니다.

대화는 기기에 파일로 저장했다가 다시 열 수 있고, 폴더로 묶거나 복제할 수 있습니다. 복제하면 대화에 든 파일도 함께 복제합니다[1]. 모델은 대화 사이에 기억을 이어 가지 않고, 그 대화의 내용과 시스템 프롬프트만 압니다[1]. 모델이 답에 어떤 사실을 썼다면 그 사실은 그 대화 파일 안에서 찾으면 됩니다.

## 위치와 버전별 차이

Windows 경로는 아래와 같습니다.

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%UserProfile%\.lmstudio\.internal\download-jobs-info.json` | 모델·실행 엔진 내려받기 작업 기록 | [3 부록 A], [4], [5] |
| `%UserProfile%\.lmstudio\models\{제공자}\{저장소}\{파일}.gguf` | 모델 파일(GGUF) | [3 부록 A], [5]의 `download.targetPath` |
| `%UserProfile%\.lmstudio\conversations\` | 대화 JSON | [1], [3 부록 A] |
| `%UserProfile%\.lmstudio\user-files\{파일}` | 올린 파일 원본 | [3 부록 A] |
| `%UserProfile%\.lmstudio\user-files\{파일}.metadata.json` | 올린 파일의 종류·크기·원래 이름·SHA-256 | [3 부록 A·B], [5] |
| `%AppData%\LM Studio\logs\main.log` | 업데이트·오류 로그 | [3 부록 A·B] |

대화 파일 이름은 논문 부록 A 가 `{ID}.json` 으로 적었지만, 공개 샘플에서는 `Conversations\{13자리 숫자}.conversation.json` 입니다[5]. 폴더 이름도 공식 문서와 논문은 소문자 `conversations`, 샘플과 LangurTrace KAPE 타깃은 `Conversations` 로 적었습니다. Windows 는 대소문자를 구분하지 않으므로 같은 폴더입니다.

메인 로그의 경로는 출처끼리 다릅니다. 논문(2025년 게재)은 `%AppData%\LM Studio\logs\main.log`(공백 있음)로 적었고, LangurTrace KAPE 타깃(저장소 2025-07-20 커밋)은 `C:\Users\%user%\Appdata\Roaming\LMStudio\logs\` 의 `*.log`(공백 없음)를 모읍니다[3 부록 A][4]. 공개 샘플에는 로그가 들어 있지 않고 LangurTrace 파서도 로그를 읽지 않으므로, 실제 기기에서는 `%AppData%` 아래 두 이름을 모두 찾아봅니다.

macOS·Linux 의 대화 폴더는 `~/.lmstudio/conversations/`, 모델 폴더는 `~/.lmstudio/models/` 입니다[1][2]. LangurTrace 시험은 Windows 에서만 했고, 다른 OS 는 경로가 달라도 아티팩트 종류는 같을 것이라는 추정만 있습니다[3 §6.2]. 그 밖의 macOS·Linux 경로는 실제 기기에서 확인해야 합니다.

앱 판은 설치 기록 안에서 찾을 수 있습니다. 공개 샘플의 `download-jobs-info.json` 에는 내려받기 요청 머리글 `User-Agent` 값 `LM Studio/0.3.14+5 (win32/x64)` 가 모델 작업마다 들어 있어서, 그 모델을 받을 때 쓴 앱 판과 플랫폼이 드러납니다[5]. 조사할 때는 이 값과 설치된 앱 판을 먼저 적고, 아래 구조가 그 판에 맞는지 확인하며 읽습니다.

모델이 기본 위치에 없으면 설치 기록의 `download.targetPath` 로 저장한 곳을 먼저 확인하고, 그래도 없으면 디스크 전체에서 `.gguf` 파일을 찾습니다. `lms import` 명령(실험 기능)으로 가져온 모델도 같은 모델 폴더에 들어갑니다[2]. 가져온 모델은 내려받기 작업이 아니므로 설치 기록에 남는지를 실제 기기에서 확인해야 합니다.

## 구조

### 모델 설치 기록

`download-jobs-info.json` 은 최상위 `jobs` 배열에 내려받기 작업을 하나씩 담습니다. 아래 키는 0.3.14 공개 샘플[5]과 LangurTrace 의 `model_setup_reporter.py`[4] 기준입니다.

| 키 | 담긴 값 |
|---|---|
| `jobIdentifier` | 작업 이름. `modelDownload:huggingface:…` 는 모델, `backendDownload:…` 는 실행 엔진 |
| `jobState.type` | 작업 상태. 샘플 값은 `completed`, `postActionFailed` |
| `jobState.completedTimestamp` | 작업이 끝난 시각(Unix ms) |
| `fullIndexedModelIdentifier` | `{제공자}/{저장소}/{파일}` 모양의 모델 이름 |
| `tasks[].request.url` | 파일을 받은 원본 URL |
| `tasks[].request.subpath` | 모델 폴더 아래 상대 경로 |
| `tasks[].request.sha256`, `tasks[].request.fileSizeBytes` | 받을 파일의 SHA-256 과 크기 |
| `tasks[].request.headers[]` | 요청 머리글. 샘플에서는 `User-Agent` 하나 |
| `tasks[].download.targetPath` | 기기에 저장한 전체 경로 |
| `tasks[].download.status`, `totalSizeBytes`, `downloadedSizeBytes`, `progress` | 내려받기 결과 |

이 파일에는 모델 이름, 내려받은 URL, SHA-256, 크기가 남습니다[3 부록 B]. 샘플의 모델 URL 은 `https://search.lmstudio.ai:443/v1/hf-proxy/{제공자}/{저장소}/resolve/main/{파일}?download=true` 모양이고, 실행 엔진은 `https://extensions.lmstudio.ai/` 에서 받았습니다[5]. 아래는 샘플의 짜임을 따라 만든 예시이고, 이름·해시·크기·시각은 모두 지어낸 값입니다.

```json
{
  "jobs": [
    {
      "jobIdentifier": "modelDownload:huggingface:example-org/demo-7B-GGUF:example-org/demo-7B-GGUF/demo-7B-Q4_K_M.gguf",
      "jobState": { "type": "completed", "completedTimestamp": 1767225600000 },
      "fullIndexedModelIdentifier": "example-org/demo-7B-GGUF/demo-7B-Q4_K_M.gguf",
      "tasks": [
        {
          "request": {
            "url": "https://search.lmstudio.ai:443/v1/hf-proxy/example-org/demo-7B-GGUF/resolve/main/demo-7B-Q4_K_M.gguf?download=true",
            "subpath": "example-org/demo-7B-GGUF/demo-7B-Q4_K_M.gguf",
            "sha256": "0a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f9",
            "fileSizeBytes": 4100000000,
            "headers": [{ "key": "User-Agent", "value": "LM Studio/0.3.14+5 (win32/x64)" }]
          },
          "download": {
            "targetPath": "C:\\Users\\labuser01\\.lmstudio\\models\\example-org\\demo-7B-GGUF\\demo-7B-Q4_K_M.gguf",
            "status": "completed",
            "totalSizeBytes": 4100000000
          }
        }
      ]
    }
  ]
}
```

모델 파일을 지웠더라도 여기 남은 이름과 해시로 같은 파일을 다른 곳에서 찾을 수 있고, 남은 URL 로 사용자가 받은 것과 같은 파일을 다시 받을 수 있습니다[3 §4.6.1]. 해시로 모델을 대조하는 방법은 [로컬 모델 파일](model-files.md)에서 다룹니다.

### 대화 JSON

대화 파일은 들여쓰기한 평문 JSON 입니다. 샘플에서는 파일 이름의 13자리 숫자와 파일 안 `createdAt` 이 둘 다 대화를 만든 시각(Unix ms)이고, 두 값의 차이는 0~3 ms 였습니다[5]. 이 파일은 손으로 고치거나 그 구조에 기대지 말라는 안내가 있습니다[1]. 판마다 구조가 바뀔 수 있으므로 아래 키는 0.3.14 샘플[5]과 LangurTrace 의 `conversations_reporter.py`[4] 기준으로만 읽습니다.

| 키 | 담긴 값 |
|---|---|
| `name` | 대화 제목 |
| `createdAt` | 대화를 만든 시각(Unix ms) |
| `pinned`, `preset`, `systemPrompt` | 고정 여부, 프리셋, 시스템 프롬프트 |
| `lastUsedModel.identifier`, `lastUsedModel.indexedModelIdentifier` | 마지막에 쓴 모델 |
| `tokenCount`, `userFilesSizeBytes` | 대화 토큰 수, 올린 파일 크기 |
| `plugins`, `pluginConfigs` | 켠 플러그인. 샘플 값 `lmstudio/rag-v1` |
| `usePerChatPredictionConfig`, `perChatPredictionConfig` | 대화별 생성 설정 |
| `clientInput`, `clientInputFiles` | 입력 칸에 남은 글과 파일 |
| `notes`, `looseFiles` | 샘플에서는 빈 배열 |
| `messages[]` | 메시지 목록 |

메시지 하나는 `versions[]` 배열과 `currentlySelected` 번호로 이루어집니다. `currentlySelected` 는 `versions[]` 가운데 화면에 보이는 판의 번호입니다. 샘플의 메시지는 모두 판이 하나였으므로, 답을 다시 만든 대화라면 `versions[]` 에 다른 판이 남아 있는지 직접 봅니다.

사용자 메시지는 `type` 이 `singleStep` 이고 `role` 이 `user` 입니다. `content[]` 의 필드는 `type` 이 `text` 면 `text` 에 본문이 들고, `file` 이면 `fileIdentifier`, `fileType`, `sizeBytes` 가 듭니다. 같은 메시지의 `preprocessed.content[]` 에는 모델에 실제로 넘긴 글이 들어갑니다. 샘플에서 PDF 를 올린 메시지는 `preprocessed` 안에 "The following citations were found in the files provided by the user:" 로 시작하는 문서 발췌가 들어 있었습니다[5]. 샘플의 사용자 메시지에는 따로 시각 필드가 없었습니다.

모델의 답은 `type` 이 `multiStep` 이고 `role` 이 `assistant` 이며, `senderInfo.senderName` 에 모델 이름이 들고 본문은 `steps[]` 에 나뉘어 들어갑니다. 샘플에 나온 단계 종류는 아래 넷입니다[5].

| `steps[].type` | 담긴 값 |
|---|---|
| `contentBlock` | 답 본문 `content[].text`, 답한 모델 `genInfo.identifier`·`genInfo.indexedModelIdentifier`, 생성 통계 `genInfo.stats`(초당 토큰 수, 입력·출력 토큰 수, 멈춘 이유), 적재·생성 설정 `genInfo.loadModelConfig`·`genInfo.predictionConfig` |
| `debugInfoBlock` | `debugInfo` 글. 샘플에는 `Original User Prompt: …`, 문서 검색 결과, 대화 이름을 붙인 방식이 남음 |
| `status` | `statusState` 의 진행 상태 글 |
| `citationBlock` | 답에 인용한 문서 조각 `citedText` |

단계마다 `stepIdentifier` 가 있고, 샘플에서는 Unix ms 13자리 뒤에 `-` 와 소수가 붙은 모양이었습니다[5]. 소수 부분의 뜻은 공개 자료에 설명이 없습니다.

### 올린 파일

올린 파일은 `user-files` 에 `fileIdentifier` 이름으로 저장되고, 같은 이름 뒤에 `.metadata.json` 을 붙인 메타데이터 파일이 옆에 생깁니다[3 부록 A][5]. 메타데이터의 키는 `type`(MIME 종류), `sizeBytes`, `originalName`(사용자가 올린 원래 파일 이름), `fileIdentifier`, `preview.data`, `sha256Hex` 입니다[5]. 샘플의 `fileIdentifier` 는 `{13자리 숫자} - {숫자}.{확장자}` 모양이었고, 앞자리 숫자는 Unix ms 로 풀리는 값이었습니다. 대화 JSON 의 `content[].fileIdentifier` 가 이 이름과 같아서, 어느 대화에 어느 파일을 올렸는지 이을 수 있습니다. 공개 샘플에는 메타데이터 JSON 만 있고 원본 파일은 들어 있지 않습니다.

## 증거로서 의미

**증명하는 것.** 설치 기록은 그 사용자 계정의 LM Studio 가 어떤 모델을 어느 URL 에서 받았고 언제 받기를 마쳤는지, 받은 파일의 SHA-256 과 크기가 얼마인지를 보여 줍니다. LangurTrace 시험에서 UI 로 지운 모델 5개의 내려받기 기록은 모두 되살아났습니다[3 표 8]. 대화 JSON 이 있으면 그 대화의 제목, 만든 시각, 메시지 본문, 답한 모델, 시스템 프롬프트가 그 계정의 LM Studio 에 저장되어 있었다고 쓸 수 있습니다. 올린 파일의 메타데이터에는 원래 파일 이름과 SHA-256 이 있어서, 다른 곳에서 찾은 문서와 같은 파일인지 해시로 대조할 수 있습니다. 문서 검색 플러그인을 쓴 대화라면 `preprocessed` 와 `citationBlock` 에 올린 문서의 어느 부분이 모델에 들어갔는지가 남습니다.

**증명하지 못하는 것.** 대화 파일은 계정 폴더에 남을 뿐이라서, 그 대화를 누가 키보드로 쳤는지는 따로 밝혀야 합니다([그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)). 대화나 올린 파일이 없다고 없었다고 보지 않습니다. LangurTrace 시험에서 UI 로 지운 대화 50개와 올린 파일 50개는 디스크에서 하나도 되살아나지 않았습니다[3 표 8]. 다만 이 실험은 디스크 수준 복구만 쟀고 볼륨 섀도 복사본과 메모리 분석은 시험하지 않았으므로[3 §6.2], 그쪽은 따로 찾아봅니다([대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)). 모델 파일이나 설치 기록이 있다고 그 모델로 대화했다는 뜻도 아니어서, 어떤 모델로 답을 받았는지는 대화 JSON 의 `genInfo.identifier` 로 봅니다. 기기 안의 파일만으로는 대화가 기기 밖으로 나갔는지 판단할 수 없으므로 네트워크 기록을 함께 봅니다.

## 시각 해석

공개 샘플의 LM Studio 파일 안에 든 시각은 모두 Unix 시각(1970-01-01 UTC 부터 흐른 밀리초)이라 시간대 정보가 없고, 풀면 UTC 입니다.

| 값 | 위치 | 뜻 |
|---|---|---|
| `createdAt` | 대화 JSON | 대화를 만든 시각 |
| 파일 이름 앞 13자리 | `{숫자}.conversation.json` | 샘플에서 `createdAt` 과 0~3 ms 차이 |
| `stepIdentifier` 앞 13자리 | 답의 각 단계 | 샘플에서 단계 차례대로 같거나 커지는 값 |
| `jobState.completedTimestamp` | 설치 기록 | 내려받기 작업이 끝난 시각 |
| `fileIdentifier` 앞 13자리 | 올린 파일 이름 | 샘플에서 그 파일을 쓴 답의 단계보다 11초쯤 앞선 값 |

샘플의 사용자 메시지에는 시각 필드가 없으므로, 질문을 보낸 때는 바로 뒤 답의 `stepIdentifier` 로 좁힙니다. `fileIdentifier` 앞자리를 올린 시각으로 쓰려면 시험 기기에서 파일을 올린 때와 맞춰 본 뒤에 씁니다.

LangurTrace 는 이 값을 `datetime.fromtimestamp` 로 바꾸므로, 출력의 시각은 분석 PC 의 현지 시각이고 시간대 표시가 없습니다[4]. 공개 샘플의 출력(`model_setup_history.csv`, `conversations` 폴더의 HTML 파일 이름)은 원래 값을 UTC 로 푼 시각보다 9시간 늦게 적혀 있습니다[5]. 보고서에 옮길 때는 원래 Unix ms 값에서 다시 풀어 UTC 로 적습니다. 파일 시스템 시각이 언제 바뀌는지는 공개 자료에 설명이 없어 시험 기기로 확인해야 합니다. 다른 기록과 시각을 맞추는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **판마다 바뀌는 구조.** 대화 구조는 판마다 바뀔 수 있으므로, 0.3.14 에서 만든 파서를 다른 판 데이터에 그대로 돌리지 않습니다. 값이 비어 나오면 내용이 없는 것인지 키 이름이 바뀐 것인지 원본 JSON 으로 구분합니다.
- **LangurTrace 보고서가 빼는 것.** 대화 HTML 은 `versions[currentlySelected]` 한 판만, 답은 `contentBlock` 의 글만 옮깁니다[4]. 다시 만든 답의 다른 판, `preprocessed` 의 문서 발췌, `debugInfoBlock`·`citationBlock` 은 원본 JSON 에서 직접 봅니다.
- **설치 기록을 옮기는 범위.** LangurTrace 는 `jobIdentifier` 가 `modelDownload` 로 시작하는 작업만, 그것도 `tasks[]` 의 첫 항목만 CSV 로 옮깁니다[4]. 실행 엔진 작업과 둘째 항목부터의 파일은 원본에서 봅니다.
- **로그는 따로 찾기.** LangurTrace 파서는 `main.log` 를 읽지 않고, KAPE 타깃의 로그 경로는 논문과 다릅니다(위 "위치와 버전별 차이").
- **고정된 수집 경로.** KAPE 타깃은 `C:\Users\%user%\.lmstudio\` 아래 네 곳과 `C:\Users\%user%\Appdata\Roaming\LMStudio\logs\` 처럼 정해진 경로만 모읍니다[4]. 다른 드라이브로 옮긴 모델은 모으지 않습니다.
- **공개 샘플의 빈 곳.** 샘플에는 GGUF, 올린 파일 원본, 로그가 빠져 있습니다[5]. 그래서 `models_index.csv` 의 해시는 샘플 원본만으로 다시 계산할 수 없습니다.

## 직접 분석해 보기

**헥스로.** 대화 파일을 헥스 보기로 열면 0.3.14 샘플에서는 아래처럼 `{`, 줄바꿈, 빈칸 두 개, `"name": "` 로 시작했습니다. 제목 부분은 만든 예시입니다.

```
00000000: 7B 0A 20 20 22 6E 61 6D 65 22 3A 20 22 44 65 6D  {.  "name": "Dem
00000010: 6F 20 63 68 61 74 22 2C 0A                       o chat",.
```

글자로 읽히지 않는 바이트만 이어지면 그 판이 다른 저장 방식을 쓴다고 보고 따로 확인합니다. 모델 파일의 머리를 읽는 법은 [로컬 모델 파일](model-files.md)을 봅니다.

**공개 도구로.** 사본에서 `jq` 로 설치 기록과 대화를 펼칩니다. 첫 줄은 모델 작업마다 끝난 시각(UTC), 모델 이름, SHA-256 을 뽑고, 둘째 줄은 대화 제목과 만든 시각, 셋째 줄은 답한 모델을 뽑습니다. 파일 이름은 만든 예시입니다.

```
jq -r '.jobs[] | select(.jobIdentifier|startswith("modelDownload")) | [(.jobState.completedTimestamp/1000|todate), .fullIndexedModelIdentifier, .tasks[0].request.sha256] | @tsv' download-jobs-info.json
jq -r '[.name, (.createdAt/1000|todate)] | @tsv' Conversations/1767225600000.conversation.json
jq -r '.messages[].versions[] | .steps[]? | select(.type=="contentBlock") | .genInfo.identifier' Conversations/1767225600000.conversation.json
```

LangurTrace[4]는 KAPE 타깃·모듈로 쓰거나 `LangurTrace.exe --src 수집폴더 --dst 결과폴더 --app lmstudio` 로 돌립니다. 결과로 `model_setup_history.csv`(작업 ID·모델 이름·상태·크기·SHA256·끝난 시각·URL·저장 경로), `models_index.csv`(제공자·모델 파일·SHA256), `uploaded_files.csv`(원래 이름·파일 ID·크기·SHA256), `uploaded_files` 폴더, `conversations` 폴더의 대화별 HTML 이 나옵니다. `models_index.csv` 의 SHA256 은 도구가 모델 파일을 읽어 새로 계산한 값입니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [로컬 모델 파일](model-files.md) | GGUF 머리, 설치 기록 해시와 모델 파일 해시 대조 |
| [Chatbox](chatbox.md) | 다른 대화 앱이 LM Studio 를 백엔드로 쓴 경우. 공개 샘플의 Chatbox 설정에는 `settings.lmStudioHost` 값 `http://127.0.0.1:1234/v1` 이 있음[5] |
| [Ollama](ollama.md) | 같은 PC 의 다른 로컬 AI 도구 |
| [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) | `search.lmstudio.ai`, `extensions.lmstudio.ai` 로 오간 통신과 설치 기록 시각 맞추기 |
| [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) | `.lmstudio` 폴더와 `%AppData%` 로그 수집 |
| [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) | Unix ms 값을 다른 기록과 한 줄에 놓기 |
| [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) | 올린 파일 메타데이터와 대화 속 문서 발췌로 보는 조사 흐름 |

## 실습

LangurTrace 저장소[4]의 `sample_dataset` 이 공개 시험 데이터입니다. `collect/C/Users/USER/.lmstudio/` 에는 설치 기록, 대화 4개, 올린 파일 메타데이터 1개가 있고, `parse/LLM application artifacts/lmstudio/` 에는 LangurTrace 출력이 있습니다[5].

1. 설치 기록에서 모델 작업은 몇 개이고, 각각 UTC 로 언제 끝났습니까? `User-Agent` 로 본 앱 판은 무엇입니까?
2. `model_setup_history.csv` 와 `models_index.csv` 를 비교해, 설치 기록에는 있는데 모델 파일 목록에는 없는 모델을 찾아보십시오. 이 차이로 보고서에 어디까지 쓸 수 있습니까?
3. PDF 를 올린 대화는 어느 파일이고, 문서 발췌는 JSON 의 어느 키에 남았습니까? LangurTrace HTML 에는 그 발췌가 보입니까?
4. 각 대화 파일 이름의 숫자와 `createdAt` 을 UTC 로 풀어 비교하고, LangurTrace 출력의 시각과는 몇 시간 차이가 나는지 확인해 보십시오.
5. 시험용 가상 머신에 LM Studio 를 깔고 가짜 사용자 `labuser01` 로 대화를 만든 뒤, 대화를 복제하면 새 파일의 이름과 `createdAt` 이 어떻게 되는지, 대화를 지우면 `user-files` 에 무엇이 남는지 확인해 보십시오.

## 참고 문헌

1. LM Studio Docs, "Manage chats", https://lmstudio.ai/docs/app/basics/chat (2026-09-25 열람)
2. LM Studio Docs, "Import models", https://lmstudio.ai/docs/app/advanced/import-model (2026-09-25 열람)
3. Sungjo Jeong, Sangjin Lee, Jungheum Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. DOI: 10.1016/j.fsidi.2025.301987
4. LangurTrace, https://github.com/jeongramon/LangurTrace — `src/main.py`, `src/apps/lmstudio.py`, `src/reporter/lmstudio/model_setup_reporter.py`, `src/reporter/lmstudio/conversations_reporter.py`, `src/reporter/lmstudio/files_metadata_reporter.py`, `src/reporter/lmstudio/files_reporter.py`, `src/reporter/lmstudio/model_reporter.py`, `dist/Targets/LLMApplications/LMStudio.tkape`
5. LangurTrace 공개 샘플, https://github.com/jeongramon/LangurTrace — `sample_dataset/collect/C/Users/USER/.lmstudio/`, `sample_dataset/parse/LLM application artifacts/lmstudio/`, `sample_dataset/collect/C/Users/USER/AppData/Roaming/xyz.chatboxapp.app/config-backup-2025-05-23T11_46_10.171Z.json`
