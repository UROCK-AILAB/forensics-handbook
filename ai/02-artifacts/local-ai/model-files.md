---
title: "로컬 모델 파일"
parent: "아티팩트 · 로컬 AI"
nav_order: 680
---

# 로컬 모델 파일 (GGUF·safetensors)

로컬 AI 도구가 돌리는 모델은 GGUF 나 safetensors 같은 형식의 큰 파일로 디스크에 남고, 두 형식 모두 파일 앞부분의 헤더만 읽어도 모델 이름·구조·출처 정보를 확인할 수 있습니다.

> 확인 날짜: 2026-09. 형식은 GGUF 명세(ggml 저장소 `docs/gguf.md`)와 safetensors 저장소 README, 모델 파일이 흔히 놓이는 Hugging Face 캐시는 huggingface_hub 문서를 근거로 썼습니다(모두 2026-09-25 열람). 기기에서 모델 파일을 직접 관찰하지는 않았습니다. 이 페이지의 헥스 예시는 모두 명세를 따라 만든 예시입니다.

## 무엇을 기록하나 · 왜 생기나

모델 파일은 사용 기록이 아니라 모델 자체이지만, 조사에서는 세 가지를 알려 줍니다. 그 PC 에 어떤 모델이 있었는지, 그 모델을 어디서 받았는지, 언제 받았는지입니다. GGUF 는 한 파일 안에 모델 이름·만든 사람·출처 URL·라이선스·채팅 틀 같은 메타데이터를 함께 넣는 형식이고, safetensors 는 텐서 목록을 JSON 헤더로 적고 자유 형식의 메타데이터 칸을 따로 둡니다. 파일 이름을 바꿔도 헤더의 값은 그대로 남아서, 이름을 바꿔 숨긴 모델도 헤더로 알아볼 수 있습니다.

로컬 AI 도구는 모델을 저마다 정한 폴더에 둡니다. [LM Studio](lm-studio.md)는 `~/.lmstudio/models/` 아래 `만든 곳/모델/` 폴더에 GGUF 를 두고, [로컬 이미지 생성 도구](image-gen-local.md)인 ComfyUI 는 `models/checkpoints` 에 safetensors 체크포인트를 둡니다. [Ollama](ollama.md)의 모델 폴더 위치는 그 페이지에서 다룹니다. 파이썬 라이브러리로 받은 모델은 Hugging Face 캐시에 쌓이고, 이 캐시에는 내려받은 판과 시점을 따라갈 단서가 남습니다.

## 위치와 버전별 차이

### Hugging Face 캐시

| 항목 | 값 |
|---|---|
| 기본 위치 | `~/.cache/huggingface/hub` |
| 위치를 바꾸는 방법 | 환경 변수 `HF_HOME`·`HF_HUB_CACHE`, 코드의 `cache_dir` 인자 |
| Xet 청크 캐시 | `~/.cache/huggingface/xet` 아래 환경마다 하나씩 생기는 식별자 폴더, 그 안의 `chunk_cache`·`shard_cache`·`staging` |
| 백업 제외 표시 | 캐시 폴더의 `CACHEDIR.TAG` 파일 |

`hf_xet` 1.2.0 부터는 `chunk_cache` 를 기본으로 쓰지 않습니다. 캐시 폴더에 `CACHEDIR.TAG` 를 만드는 것은 백업 도구에 이 폴더를 빼라고 알리는 표시라서, 백업본에는 모델 캐시가 빠져 있을 수 있습니다. 기기에서 Hugging Face 캐시를 직접 관찰하지는 않았습니다.

### 형식의 판

GGUF 의 현재 판은 3 이고, 판 3 에서 빅엔디언 파일을 지원하기 시작했습니다. 기본은 리틀엔디언이고, 빅엔디언 파일은 메타데이터와 텐서 값이 모두 빅엔디언입니다. safetensors README 에는 판 번호를 따로 적는 칸이 없습니다.

## 구조

### GGUF 헤더

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

JSON 헤더의 각 항목은 텐서 이름을 키로 하고 `dtype`, `shape`, `data_offsets` 를 적습니다. `data_offsets` 의 두 값은 데이터 부분이 시작하는 곳을 0으로 센 시작과 끝이고, 끝 값은 마지막 바이트 다음 위치입니다. 특수 키 `__metadata__` 에는 문자열에서 문자열로 가는 자유 형식 정보를 넣을 수 있고, 무엇을 넣는지는 파일을 만든 도구마다 다릅니다. 명세는 헤더 크기를 100MB 로 제한하고 텐서 오프셋이 서로 겹치지 않는지 검사하라고 적고 있어서, 이 조건을 어긴 파일은 손상이나 조작을 의심해 봅니다.

`.ckpt`·`.bin` 같은 pickle 형식은 불러올 때 임의의 코드가 실행될 수 있고, safetensors 는 JSON 으로 선언만 하는 형식이라 그렇지 않습니다. 의심스러운 모델 파일이 pickle 형식이라면 악성 코드를 실어 나를 수 있는 파일로 보고, 분석할 때는 라이브러리로 불러오지 않고 바이트로만 읽습니다. [AI로 악성 코드를 만들었나](../../04-scenarios/misuse/malware-development.md) 같은 조사에서 모델 파일이 나오면 이 점을 먼저 확인합니다.

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

새 판을 받아도 옛 파일을 지우지 않아서, `snapshots` 아래 커밋 폴더가 여럿이면 그만큼 다른 판을 받은 적이 있다고 볼 수 있습니다. 내려받다 끊긴 파일은 `.incomplete` 파일로 남고, `hf cache prune` 을 돌리면 이 파일과 어느 브랜치·태그도 가리키지 않는 옛 판이 함께 지워집니다. `hf_xet` 로 받은 Xet 파일은 캐시 맨 위 `blobs` 폴더에 한 번만 두고 저장소별 `blobs` 항목이 그 파일을 가리키는 링크가 되는 경우도 있어서, 저장소 폴더 안에서 실제 파일이 안 보이면 캐시 맨 위 `blobs` 를 함께 봅니다. Windows 에서 심볼릭 링크를 만들 수 없으면 `blobs` 를 쓰지 않고 `snapshots` 에 파일을 바로 두고, 개발자 모드이거나 관리자로 실행했으면 링크를 씁니다. `HF_HUB_DISABLE_SYMLINKS=1` 로 링크를 끌 수도 있습니다.

## 증거로서 의미

**증명하는 것.** 모델 파일이 있으면 그 모델이 그 디스크에 있었다고 쓸 수 있고, 헤더의 이름·URL·라이선스는 파일을 만든 쪽이 적어 넣은 값으로 인용할 수 있습니다. Hugging Face 캐시의 폴더 이름과 `refs`·`snapshots`·`trees` 는 어느 저장소의 어느 커밋을 받았는지 알려 주고, `.incomplete` 파일은 내려받기를 시작했지만 끝내지 못한 흔적입니다.

**증명하지 못하는 것.** 모델 파일은 그 모델을 돌렸다거나 무엇을 물었다는 기록이 아니어서, 사용 여부는 도구의 대화·로그와 실행 흔적으로 따로 밝힙니다. 헤더 값은 누구든 고쳐 쓸 수 있어서 `general.author` 나 `__metadata__` 의 값만으로 출처를 확정하지 않습니다. 캐시가 비어 있어도 `HF_HOME`·`HF_HUB_CACHE` 로 다른 곳에 두었거나, `hf cache rm`·`hf cache prune` 으로 지웠을 수 있습니다.

## 시각 해석

GGUF 와 safetensors 명세에는 시각을 담는 칸이 없어서, 모델 파일의 시각은 파일 시스템 시각에 기댑니다. 파일 생성 시각은 내려받거나 복사한 때에 가깝고, 모델을 쓴 때가 아닙니다. Hugging Face 캐시에서는 `hf cache ls` 가 저장소별 마지막 접근 시각과 수정 시각을 보여 주지만, 이 값도 파일 시스템 시각에서 나온 값으로 보고 볼륨의 마지막 접근 시각 기록 설정을 함께 확인합니다. `snapshots` 아래 커밋 폴더가 여럿이면 폴더 시각 순서로 판을 받은 순서를 가늠할 수 있습니다.

## 함정과 한계

- **이름만 믿기.** 파일 이름과 폴더 이름은 사용자가 바꿀 수 있습니다. 헤더를 읽어 이름을 확인합니다.
- **조각 파일.** 여러 조각으로 나뉜 GGUF 는 조각 하나만 남아 있어도 모델 전체가 있었다고 보지 않고, 조각 번호와 전체 개수를 확인합니다.
- **캐시 명령의 부작용.** `hf cache ls` 나 `hf cache verify` 는 원본이 아니라 사본에서 돌립니다. `hf cache rm`·`hf cache prune` 은 지우는 명령이라 조사에서는 쓰지 않고, 사용자가 이 명령을 쓴 흔적이 있으면 캐시가 비어 있는 까닭으로 적습니다.
- **Windows 링크.** 링크를 쓰지 않은 캐시에서는 `blobs` 가 비어 있어도 이상이 아닙니다.
- **해시 대조.** 모델 파일의 SHA-256 을 공개 저장소의 해시와 맞춰 출처를 좁힐 수 있다는 원리는 캐시가 해시 이름으로 파일을 두는 방식에서 나오지만, 대조 절차를 적은 문서는 이번에 확인하지 못했습니다.

## 직접 분석해 보기

**헥스로 — GGUF.** 아래는 명세를 따라 만든 예시이고 실제 파일에서 나온 값이 아닙니다.

```
00000000  47 47 55 46 03 00 00 00  23 01 00 00 00 00 00 00  GGUF....#.......
00000010  18 00 00 00 00 00 00 00                            ........
```

첫 4바이트 `47 47 55 46` 은 `GGUF` 이고, 다음 4바이트 `03 00 00 00` 은 리틀엔디언으로 판 3 입니다. 빅엔디언 파일이면 같은 자리가 `00 00 00 03` 으로 보입니다. 오프셋 0x08 의 8바이트 `23 01 00 00 00 00 00 00` 은 텐서 개수 0x123(291개), 오프셋 0x10 의 8바이트 `18 00 …` 은 메타데이터 키-값 개수 0x18(24개)이고, 오프셋 0x18 부터 메타데이터가 이어집니다. 글자 칸에서 `general.name` 이나 `general.source.url` 을 찾으면 그 뒤에 값이 글자로 보입니다.

**헥스로 — safetensors.** 역시 명세를 따라 만든 예시입니다. 헤더는 `{"__metadata__":{"note":"sample"},"w1":{"dtype":"F16","shape":[2,2],"data_offsets":[0,8]}}` 이고 길이는 90바이트입니다.

```
00000000  5A 00 00 00 00 00 00 00  7B 22 5F 5F 6D 65 74 61  Z.......{"__meta
00000010  64 61 74 61 5F 5F 22 3A  7B 22 6E 6F 74 65 22 3A  data__":{"note":
00000020  22 73 61 6D 70 6C 65 22  7D 2C 22 77 31 22 3A 7B  "sample"},"w1":{
```

첫 8바이트 `5A 00 00 00 00 00 00 00` 은 헤더 크기 90 이고, 오프셋 0x08 이 `7B`(`{`) 로 시작합니다. 데이터 부분은 8 + 90 = 98(0x62) 에서 시작하므로, 텐서 `w1` 은 파일 오프셋 0x62 부터 8바이트(F16 값 4개)입니다. 헤더 크기가 파일보다 크거나 헤더가 `{` 로 시작하지 않으면 safetensors 가 아니거나 손상된 파일입니다.

**공개 도구로.** Hugging Face 캐시 사본에서 `hf cache ls` 로 저장소 목록과 시각을, `hf cache verify` 로 파일 해시가 맞는지를 확인합니다. 모델 파일 하나는 SHA-256 을 떠서 기록해 두고, safetensors 헤더는 앞 8바이트로 길이를 읽은 뒤 그 길이만큼 잘라 `jq` 로 펼칩니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [Ollama](ollama.md), [LM Studio](lm-studio.md), [로컬 이미지 생성 도구](image-gen-local.md) | 그 모델을 어느 도구가 두었고 썼는지 |
| [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) | 모델을 내려받은 통신과 시각 |
| [보안 제품이 남기는 AI 사용 기록](../network-enterprise/dlp-casb.md) | 큰 모델 파일을 내려받은 기록이 보안 제품 로그에 있는지 |
| [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md) | 회사 PC 에서 로컬 모델이 나왔을 때의 조사 흐름 |
| [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) | 모델 파일 시각을 다른 기록과 한 줄로 세우기 |

## 실습

공개 검체 가운데 로컬 모델 파일이 든 것은 확인하지 못했습니다. 시험용 가상 머신에서 작은 공개 모델을 받아 아래 질문을 풀어 봅니다.

1. GGUF 파일 하나의 첫 24바이트에서 판, 텐서 개수, 메타데이터 개수를 손으로 읽어 보고, 공개 도구가 보여 주는 값과 맞습니까?
2. GGUF 파일 이름을 `sample-renamed.gguf` 로 바꾼 뒤에도 헤더에서 원래 모델 이름을 찾을 수 있습니까?
3. safetensors 파일의 앞 8바이트로 헤더 길이를 계산하고, 그 길이만큼 잘라 낸 JSON 에 `__metadata__` 가 있습니까?
4. Hugging Face 캐시에서 같은 저장소의 다른 판을 받으면 `snapshots` 와 `refs/main` 은 어떻게 바뀝니까? Windows 일반 계정과 개발자 모드에서 `blobs` 의 모습은 어떻게 다릅니까?

## 참고 문헌

1. ggml, "GGUF", https://github.com/ggml-org/ggml/blob/master/docs/gguf.md (2026-09-25 열람)
2. Hugging Face, safetensors GitHub README, https://github.com/huggingface/safetensors (2026-09-25 열람)
3. Hugging Face, huggingface_hub "Understand caching / Manage cache", https://huggingface.co/docs/huggingface_hub/guides/manage-cache (2026-09-25 열람)
4. LM Studio Docs, "Import models", https://lmstudio.ai/docs/app/advanced/import-model (2026-09-25 열람)
5. ComfyUI, GitHub README, https://github.com/comfyanonymous/ComfyUI (2026-09-25 열람)
